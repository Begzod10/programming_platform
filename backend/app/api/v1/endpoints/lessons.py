import json
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from starlette import status
from app.models.lesson_file import LessonFile
from app.dependencies import get_db, get_current_student, get_current_teacher, get_current_student_optional, \
    get_current_instructor
from app.services import lesson_service, achievement_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course
from app.services.course_service import CourseService
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from app.config import settings

router = APIRouter()
LESSONS_FILES_DIR = Path(settings.UPLOAD_DIR) / "lesson_files"
LESSONS_FILES_DIR.mkdir(parents=True, exist_ok=True)

# Ruxsat etilgan kod fayl turlari
ALLOWED_CODE_EXTENSIONS = {
    ".html", ".css", ".js", ".py", ".ts", ".jsx", ".tsx",
    ".json", ".xml", ".php", ".java", ".cpp", ".c", ".sql"
}


# ─────────────────────────────────────────────────────────────────────────────
#  YORDAMCHI FUNKSIYALAR
# ─────────────────────────────────────────────────────────────────────────────

async def _calc_lesson_progress(
        db: AsyncSession,
        lesson: Lesson,
        student_id: int
) -> int:
    """
    Lesson foizi = (ko'rilgan video + bajarilgan exercise + topshirilgan project)
                   / (jami video + exercise + project) × 100
    """
    from app.models.video_watch import VideoWatch
    from app.models.exercise import ExerciseSubmission

    sections = []
    if lesson.sections_json:
        try:
            sections = json.loads(lesson.sections_json)
        except Exception:
            pass

    total_videos = sum(1 for s in sections if s.get("type") == "video" and s.get("videoUrl"))
    total_exercises = sum(1 for s in sections if s.get("type") == "exercise")
    total_projects = sum(1 for s in sections if s.get("type") == "project")
    total = total_videos + total_exercises + total_projects

    if total == 0:
        comp = await db.execute(
            select(LessonCompletion).where(
                LessonCompletion.student_id == student_id,
                LessonCompletion.lesson_id == lesson.id
            )
        )
        return 100 if comp.scalar_one_or_none() else 0

    done = 0

    # Ko'rilgan videolar
    if total_videos > 0:
        video_section_ids = [
            s["id"] for s in sections
            if s.get("type") == "video" and s.get("videoUrl")
        ]
        watched_res = await db.execute(
            select(func.count(VideoWatch.id)).where(
                VideoWatch.student_id == student_id,
                VideoWatch.lesson_id == lesson.id,
                VideoWatch.section_id.in_(video_section_ids)
            )
        )
        done += watched_res.scalar() or 0

    # Bajarilgan exercise sectionlar
    if total_exercises > 0:
        for sec in sections:
            if sec.get("type") != "exercise":
                continue
            ex_list = sec.get("exercises", [])
            if not ex_list:
                done += 1
                continue
            ex_ids = [e["id"] for e in ex_list if e.get("id")]
            if not ex_ids:
                done += 1
                continue
            sub_res = await db.execute(
                select(func.count(ExerciseSubmission.id)).where(
                    ExerciseSubmission.student_id == student_id,
                    ExerciseSubmission.exercise_id.in_(ex_ids)
                )
            )
            submitted = sub_res.scalar() or 0
            if submitted >= len(ex_ids):
                done += 1

    # Topshirilgan projectlar
    if total_projects > 0:
        sub_res = await db.execute(
            select(func.count(Submission.id)).where(
                Submission.student_id == student_id,
                Submission.lesson_id == lesson.id
            )
        )
        proj_done = sub_res.scalar() or 0
        done += min(proj_done, total_projects)

    return int(min(done, total) / total * 100)


async def _calc_course_progress(
        db: AsyncSession,
        course_id: int,
        student_id: int
) -> dict:
    """
    Kurs foizi = barcha lesson foizlarining o'rtachasi
    """
    lessons_res = await db.execute(
        select(Lesson).where(
            Lesson.course_id == course_id,
            Lesson.is_active == True
        )
    )
    lessons = lessons_res.scalars().all()
    total = len(lessons)

    if total == 0:
        return {
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percentage": 0,
            "progress": 0,
            "percentage": 0,
        }

    lesson_progresses = []
    for lesson in lessons:
        pct = await _calc_lesson_progress(db, lesson, student_id)
        lesson_progresses.append(pct)

    completed = sum(1 for p in lesson_progresses if p == 100)
    avg_pct = int(sum(lesson_progresses) / total)

    return {
        "total_lessons": total,
        "completed_lessons": completed,
        "progress_percentage": avg_pct,
        "progress": avg_pct,
        "percentage": avg_pct,
    }


async def _ensure_enrolled(db: AsyncSession, student_id: int, course_id: int):
    """Hard-lock: only enrolled students or the course instructor may proceed."""
    course_res = await db.execute(select(Course).where(Course.id == course_id))
    course = course_res.scalar_one_or_none()
    if course and course.instructor_id == student_id:
        return

    stmt = select(Student).options(selectinload(Student.enrolled_courses)).where(Student.id == student_id)
    res = await db.execute(stmt)
    student = res.scalar_one()
    if not any(c.id == course_id for c in student.enrolled_courses):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kursga kirish ruxsati yo'q. O'qituvchi sizni qo'shishi kerak.",
        )


async def _add_points(db: AsyncSession, student_id: int, points: int) -> int:
    if not points or points <= 0:
        return 0
    from app.services.ranking_service import RankingService
    service = RankingService(db)
    student = await service.add_points_to_student(student_id, points)
    return student.total_points if student else 0


async def _subtract_points(db: AsyncSession, student_id: int, points: int) -> int:
    if not points or points <= 0:
        return 0
    from app.services.ranking_service import RankingService
    service = RankingService(db)
    student = await service.subtract_points_from_student(student_id, points)
    return student.total_points if student else 0


# Minimum project score (0-100) to unlock the next lesson WHEN the teacher
# hasn't explicitly approved yet (status="Under Review"). Matches the B-grade
# bucket in the AI prompt ("Yaxshi: asosiy funksional ishlaydi"). A teacher's
# Approve verdict always passes, regardless of score — their judgement is the
# gate. Earlier value (90) was effectively requiring an A and silently
# blocking students whose work was good enough for the lesson.
PROJECT_PASS_THRESHOLD = 75


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    if current_student:
        await _ensure_enrolled(db, current_student.id, course_id)
    lessons = await lesson_service.get_lessons_by_course(db, course_id)

    completed_ids: set = set()
    if current_student and lessons:
        lesson_ids = [l.id for l in lessons]
        comp_res = await db.execute(
            select(LessonCompletion.lesson_id).where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id.in_(lesson_ids)
            )
        )
        completed_ids = {row[0] for row in comp_res.all()}

    result = []
    for lesson in lessons:
        lesson_data = LessonRead.model_validate(lesson)
        is_comp = lesson.id in completed_ids
        lesson_data.is_completed = is_comp
        lesson_data.completed = is_comp

        if current_student:
            pct = await _calc_lesson_progress(db, lesson, current_student.id)
            lesson_data.progress_percentage = pct
        else:
            lesson_data.progress_percentage = 0

        result.append(lesson_data)

    return result


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(
        course_id: int,
        lesson_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    if current_student:
        await _ensure_enrolled(db, current_student.id, course_id)
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    res = LessonRead.model_validate(lesson)

    if current_student:
        comp_res = await db.execute(
            select(LessonCompletion).where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id == lesson_id
            )
        )
        is_comp = comp_res.scalar_one_or_none() is not None
        res.is_completed = is_comp
        res.completed = is_comp
        res.progress_percentage = await _calc_lesson_progress(db, lesson, current_student.id)

    return res


@router.post("/courses/{course_id}/lessons", response_model=LessonRead, status_code=201)
async def create_lesson(
        course_id: int,
        data: LessonCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    return await lesson_service.create_lesson(db, course_id, data)


@router.put("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def update_lesson(
        course_id: int,
        lesson_id: int,
        data: LessonUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return await lesson_service.update_lesson(db, lesson_id, data)


@router.delete("/courses/{course_id}/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
        course_id: int,
        lesson_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await lesson_service.delete_lesson(db, lesson_id)
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON COMPLETION
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_lookup = await db.execute(select(Lesson.course_id).where(Lesson.id == lesson_id))
    course_id_row = lesson_lookup.scalar_one_or_none()
    if course_id_row is None:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, course_id_row)

    result = await lesson_service.complete_lesson(db, lesson_id, current_student.id)
    course_id = result.get("course_id")

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)
    progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        **result,
        **progress,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None,
    }


@router.get("/lessons/{lesson_id}/my-exercise-submissions")
async def get_my_exercise_submissions(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Latest submission per exercise for this lesson.

    One row per exercise the student has attempted in this lesson — the most
    recent submission only. Used by the lesson page to hydrate ExerciseCard
    state after a refresh: render the saved answer + score + checkmark, but
    let the student still resubmit if they want.
    """
    from app.models.exercise import Exercise, ExerciseSubmission

    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    ex_id_rows = (
        await db.execute(
            select(Exercise.id).where(Exercise.lesson_id == lesson_id)
        )
    ).all()
    ex_ids = [r[0] for r in ex_id_rows]
    if not ex_ids:
        return []

    # Latest submission per exercise. Cheaper than DISTINCT ON for the small
    # per-lesson volume — pull all rows, dedupe in Python keeping the newest.
    rows = (
        await db.execute(
            select(ExerciseSubmission)
            .where(
                ExerciseSubmission.student_id == current_student.id,
                ExerciseSubmission.exercise_id.in_(ex_ids),
            )
            .order_by(ExerciseSubmission.submitted_at.desc())
        )
    ).scalars().all()

    latest_by_ex: dict[int, ExerciseSubmission] = {}
    for s in rows:
        if s.exercise_id not in latest_by_ex:
            latest_by_ex[s.exercise_id] = s

    return [
        {
            "exercise_id": s.exercise_id,
            "student_answer": s.student_answer,
            "is_correct": s.is_correct,
            "score": s.score,
            "ai_feedback": s.ai_feedback,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
        }
        for s in latest_by_ex.values()
    ]


@router.get("/lessons/{lesson_id}/is-completed")
async def is_lesson_completed(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    comp_res = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    completion = comp_res.scalar_one_or_none()
    progress = await _calc_course_progress(db, lesson.course_id, current_student.id)

    return {
        "lesson_id": lesson_id,
        "is_completed": completion is not None,
        "completed_at": completion.completed_at if completion else None,
        "course_id": lesson.course_id,
        **progress,
    }


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
        course_id: int,
        current_student: Optional[Student] = Depends(get_current_student_optional),
        db: AsyncSession = Depends(get_db)
):
    if not current_student:
        return {
            "course_id": course_id,
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percentage": 0,
            "progress": 0,
            "percentage": 0,
        }

    progress = await _calc_course_progress(db, course_id, current_student.id)
    return {"course_id": course_id, **progress}


# ─────────────────────────────────────────────────────────────────────────────
#  VIDEO WATCH
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/courses/{course_id}/lessons/{lesson_id}/sections/{section_id}/watch")
async def mark_video_watched(
        course_id: int,
        lesson_id: int,
        section_id: str,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    from app.models.video_watch import VideoWatch

    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, course_id)

    existing = await db.execute(
        select(VideoWatch).where(
            VideoWatch.student_id == current_student.id,
            VideoWatch.lesson_id == lesson_id,
            VideoWatch.section_id == section_id
        )
    )
    if not existing.scalar_one_or_none():
        db.add(VideoWatch(
            student_id=current_student.id,
            lesson_id=lesson_id,
            section_id=section_id
        ))
        await db.commit()

    progress_pct = await _calc_lesson_progress(db, lesson, current_student.id)
    course_progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        "watched": True,
        "lesson_progress": progress_pct,
        **course_progress
    }


class LessonSubmitRequest(BaseModel):
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    description: Optional[str] = None


@router.post("/courses/{course_id}/lessons/{lesson_id}/submit", status_code=201)
async def submit_lesson_project(
        course_id: int,
        lesson_id: int,
        data: LessonSubmitRequest,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    # Row-level lock on the lesson serializes concurrent submits from the
    # same student (double-click / network retry). The second request blocks
    # until the first commits, then re-reads the existing-submission check
    # below and exits cleanly with 400 instead of inserting a duplicate.
    lock_res = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id).with_for_update()
    )
    lesson = lock_res.scalar_one_or_none()
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    await _ensure_enrolled(db, current_student.id, course_id)

    existing_res = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    existing_sub = existing_res.scalar_one_or_none()

    # Re-submission path: an existing submission may be replaced ONLY if the
    # teacher explicitly Rejected it. An Approved project is locked regardless
    # of score — the teacher's verdict is the gate. Pending submissions stay
    # locked too, so the student waits instead of spamming uploads.
    if existing_sub is not None:
        proj_res = await db.execute(
            select(Project).where(Project.id == existing_sub.project_id)
        )
        existing_project = proj_res.scalar_one_or_none()
        proj_status = existing_project.status if existing_project else existing_sub.status
        prev_points = existing_project.points_earned if existing_project else 0
        can_resubmit = (
            existing_project is not None and proj_status == "Rejected"
        )
        if not can_resubmit:
            if proj_status == "Submitted":
                raise HTTPException(
                    status_code=400,
                    detail="Loyihangiz hali tekshirilmoqda — natijani kuting"
                )
            raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

        # Reverse any points awarded by the previous review so re-review
        # doesn't double-count when the teacher scores the new attempt.
        if prev_points > 0:
            await _subtract_points(db, current_student.id, prev_points)

        existing_project.status = "Submitted"
        existing_project.points_earned = 0
        existing_project.grade = None
        existing_project.instructor_feedback = None
        existing_project.reviewed_at = None
        existing_project.github_url = data.github_url
        existing_project.live_demo_url = data.live_demo_url
        existing_project.description = (
                data.description or lesson.task_description or "Dars loyihasi"
        )

        existing_sub.status = "Submitted"
        existing_sub.points_earned = 0
        existing_sub.grade = None
        existing_sub.instructor_feedback = None
        existing_sub.reviewed_at = None
        existing_sub.github_url = data.github_url
        existing_sub.live_demo_url = data.live_demo_url
        existing_sub.description = data.description

        await db.commit()

        student_res = await db.execute(
            select(Student).where(Student.id == current_student.id)
        )
        student = student_res.scalar_one_or_none()
        progress = await _calc_course_progress(db, course_id, current_student.id)

        return {
            "message": "Loyiha qayta topshirildi — o'qituvchi tekshirishini kuting",
            "submission_id": existing_sub.id,
            "project_id": existing_project.id,
            "resubmitted": True,
            **progress,
            "points_earned": 0,
            "total_points": student.total_points if student else 0,
            "certificate_issued": False,
            "certificate_id": None,
        }

    new_project = Project(
        student_id=current_student.id,
        title=lesson.task_title or lesson.title,
        description=data.description or lesson.task_description or "Dars loyihasi",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
        difficulty_level="Easy",
        status="Submitted",
    )
    db.add(new_project)
    await db.flush()

    submission = Submission(
        lesson_id=lesson_id,
        student_id=current_student.id,
        project_id=new_project.id,
        status="Submitted",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
        description=data.description,
    )
    db.add(submission)

    points_earned = 0
    comp_check = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    if not comp_check.scalar_one_or_none():
        completion = LessonCompletion(
            student_id=current_student.id,
            lesson_id=lesson_id
        )
        db.add(completion)
        points_reward = getattr(lesson, "points_reward", 0) or 0
        if points_reward > 0:
            await _add_points(db, current_student.id, points_reward)
            points_earned = points_reward

    try:
        await db.commit()
    except IntegrityError:
        # Defense-in-depth: if the partial unique index is in place and we
        # still raced past the existing-check (e.g. cross-process without
        # the row lock holding), turn the DB error into a clean 400.
        await db.rollback()
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)

    student_res = await db.execute(select(Student).where(Student.id == current_student.id))
    student = student_res.scalar_one_or_none()

    progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        "message": "Loyiha topshirildi va dars tugatildi!",
        "submission_id": submission.id,
        "project_id": new_project.id,
        **progress,
        "points_earned": points_earned,
        "total_points": student.total_points if student else 0,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None,
    }


@router.get("/courses/{course_id}/lessons/{lesson_id}/submission")
async def get_lesson_submission(
        course_id: int,
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    result = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        return {"submitted": False, "pass_threshold": PROJECT_PASS_THRESHOLD}

    # The teacher's review writes to the Project row, not the Submission row,
    # so we join through to get the authoritative score and feedback.
    proj_res = await db.execute(
        select(Project).where(Project.id == submission.project_id)
    )
    project = proj_res.scalar_one_or_none()

    proj_status = project.status if project else submission.status
    points_earned = project.points_earned if project else 0
    grade = project.grade if project else None
    feedback = project.instructor_feedback if project else None
    reviewed = proj_status in ("Approved", "Rejected")
    # Two paths to "passed":
    #   1. Teacher approved — their verdict is the gate, score is informational.
    #   2. AI graded only (Under Review / Submitted) but score is high enough
    #      that we don't need to wait for a teacher to release the lesson.
    # Rejected always fails regardless of score.
    passed = (
        proj_status == "Approved"
        or (proj_status not in ("Rejected", "Draft")
            and points_earned >= PROJECT_PASS_THRESHOLD)
    )
    can_resubmit = reviewed and not passed

    return {
        "submitted": True,
        "submission_id": submission.id,
        "project_id": submission.project_id,
        "status": proj_status,
        "github_url": submission.github_url,
        "live_demo_url": submission.live_demo_url,
        "description": submission.description,
        "points_earned": points_earned,
        "grade": grade,
        "instructor_feedback": feedback,
        "reviewed": reviewed,
        "passed": passed,
        "can_resubmit": can_resubmit,
        "pass_threshold": PROJECT_PASS_THRESHOLD,
    }


@router.post("/{lesson_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_lesson_file(
        lesson_id: int,
        file: UploadFile = File(...),
        label: str = Form(default=""),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """O'qituvchi darsga kod fayl yuklaydi — kodi o'qilib qaytariladi"""

    # Kengaytmani tekshirish
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_CODE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Faqat kod fayllari qabul qilinadi: {', '.join(ALLOWED_CODE_EXTENSIONS)}"
        )

    # Faylni o'qish
    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Fayl bo'sh!")

    if len(contents) > 1 * 1024 * 1024:  # 1MB limit
        raise HTTPException(status_code=400, detail="Fayl 1MB dan katta!")

    # Kodni decode qilish
    try:
        code_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Fayl UTF-8 formatida emas!")

    # Darsni tekshirish
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi!")

    # Faylni serverga saqlash
    filename = f"{uuid.uuid4()}{ext}"
    filepath = LESSONS_FILES_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    # Bazaga saqlash
    lesson_file = LessonFile(
        lesson_id=lesson_id,
        original_name=file.filename,
        saved_name=filename,
        file_url=f"/uploads/lesson_files/{filename}",
        extension=ext,
        label=label,
        code_content=code_text,
        file_size=len(contents)
    )
    db.add(lesson_file)
    await db.commit()
    await db.refresh(lesson_file)

    return {
        "id": lesson_file.id,
        "lesson_id": lesson_id,
        "original_name": file.filename,
        "file_url": lesson_file.file_url,
        "extension": ext,
        "label": label,
        "code_content": code_text,
        "file_size": len(contents),
        "created_at": lesson_file.created_at
    }


# ============================================================
# 2. DARSNING BARCHA FAYLLARINI OLISH
# ============================================================

@router.get("/{lesson_id}/files")
async def get_lesson_files(
        lesson_id: int,
        current_user: Optional[Student] = Depends(get_current_student_optional),
        db: AsyncSession = Depends(get_db)
):
    # 1. LessonFile jadvalidan
    result = await db.execute(
        select(LessonFile)
        .where(LessonFile.lesson_id == lesson_id)
        .order_by(LessonFile.created_at)
    )
    db_files = result.scalars().all()

    files = [
        {
            "id": f.id,
            "lesson_id": f.lesson_id,
            "original_name": f.original_name,
            "file_url": f.file_url,
            "extension": f.extension,
            "label": f.label,
            "code_content": f.code_content,
            "file_size": f.file_size,
            "created_at": f.created_at
        }
        for f in db_files
    ]

    # 2. sections_json ichidagi projectFiles dan ham olish
    if not files:
        lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = lesson_res.scalar_one_or_none()
        if lesson and lesson.sections_json:
            try:
                sections = json.loads(lesson.sections_json)
                for section in sections:
                    for pf in section.get("projectFiles", []):
                        files.append({
                            "id": pf.get("_localId"),
                            "lesson_id": lesson_id,
                            "original_name": pf.get("filename") or pf.get("name"),
                            "file_url": None,
                            "extension": "." + pf.get("filename", "").split(".")[-1],
                            "label": pf.get("label", ""),
                            "code_content": pf.get("content") or pf.get("code"),
                            "file_size": pf.get("size"),
                            "created_at": None
                        })
            except Exception:
                pass

    return files



@router.get("/{lesson_id}/files/{file_id}")
async def get_lesson_file(
        lesson_id: int,
        file_id: int,
        current_user: Student = Depends(get_current_instructor),  # ← o'zgartirildi
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")
    return {
        "id": lesson_file.id,
        "original_name": lesson_file.original_name,
        "file_url": lesson_file.file_url,
        "extension": lesson_file.extension,
        "label": lesson_file.label,
        "code_content": lesson_file.code_content,
        "file_size": lesson_file.file_size,
        "created_at": lesson_file.created_at
    }


# ============================================================
# 4. FAYLNI YANGILASH (kodni o'zgartirish)
# ============================================================

@router.put("/{lesson_id}/files/{file_id}")  # PATCH o'rniga PUT
async def update_lesson_file(
        lesson_id: int,
        file_id: int,
        label: str = Body(default=None, embed=True),
        code_content: str = Body(default=None, embed=True),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Fayl label yoki kodni yangilash"""

    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    if label is not None:
        lesson_file.label = label

    if code_content is not None:
        lesson_file.code_content = code_content
        # Diskdagi faylni ham yangilash
        filepath = LESSONS_FILES_DIR / lesson_file.saved_name
        if filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code_content)

    await db.commit()
    await db.refresh(lesson_file)

    return {
        "id": lesson_file.id,
        "label": lesson_file.label,
        "code_content": lesson_file.code_content,
        "message": "Fayl yangilandi!"
    }


# ============================================================
# 5. FAYLNI O'CHIRISH
# ============================================================

@router.delete("/{lesson_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_file(
        lesson_id: int,
        file_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Faylni o'chirish"""

    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    # Diskdan o'chirish
    filepath = LESSONS_FILES_DIR / lesson_file.saved_name
    if filepath.exists():
        filepath.unlink()

    await db.delete(lesson_file)
    await db.commit()
    return None


@router.get("/{lesson_id}/files/{file_id}/download")
async def download_lesson_file(
        lesson_id: int,
        file_id: int,
        current_user: Student = Depends(get_current_instructor),  # ← o'zgartirildi
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(
            LessonFile.id == file_id,
            LessonFile.lesson_id == lesson_id
        )
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    filepath = LESSONS_FILES_DIR / lesson_file.saved_name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fayl serverda topilmadi!")

    return FileResponse(
        path=str(filepath),
        filename=lesson_file.original_name,
        media_type="application/octet-stream"
    )
