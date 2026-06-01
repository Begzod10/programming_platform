import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_student, get_current_teacher, get_current_student_optional
from app.services import lesson_service, achievement_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course
from app.services.course_service import CourseService

router = APIRouter()


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
    stmt = select(Student).options(selectinload(Student.enrolled_courses)).where(Student.id == student_id)
    res = await db.execute(stmt)
    student = res.scalar_one()
    if not any(c.id == course_id for c in student.enrolled_courses):
        course_res = await db.execute(select(Course).where(Course.id == course_id))
        course = course_res.scalar_one_or_none()
        if course:
            student.enrolled_courses.append(course)
            await db.flush()


async def _add_points(db: AsyncSession, student_id: int, points: int) -> int:
    if not points or points <= 0:
        return 0
    from app.services.ranking_service import RankingService
    service = RankingService(db)
    student = await service.add_points_to_student(student_id, points)
    return student.total_points if student else 0


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
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
    if existing_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

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
        return {"submitted": False}

    return {
        "submitted": True,
        "submission_id": submission.id,
        "project_id": submission.project_id,
        "status": submission.status,
        "github_url": submission.github_url,
        "live_demo_url": submission.live_demo_url,
        "description": submission.description,
    }
