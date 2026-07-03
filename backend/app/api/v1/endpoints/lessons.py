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
from app.models.lesson import LessonCompletion, Lesson, LessonVocabulary
from app.models.dictionary import UserDictionary
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
LESSON_PREVIEWS_DIR = Path(settings.UPLOAD_DIR) / "lesson_previews"
LESSON_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


async def _inject_file_previews(db: AsyncSession, lesson_ids: list[int], lessons_data: list) -> None:
    """Inject previewImageUrl into file sections in sections_json for the given lessons."""
    if not lesson_ids:
        return
    files_res = await db.execute(
        select(LessonFile.lesson_id, LessonFile.original_name, LessonFile.preview_image_url)
        .where(
            LessonFile.lesson_id.in_(lesson_ids),
            LessonFile.preview_image_url.isnot(None),
        )
    )
    preview_map: dict[int, dict[str, str]] = {}
    for row in files_res.all():
        preview_map.setdefault(row.lesson_id, {})[row.original_name] = row.preview_image_url

    for lesson_dto in lessons_data:
        lesson_previews = preview_map.get(lesson_dto.id)
        if not lesson_previews or not lesson_dto.sections_json:
            continue
        try:
            sections = json.loads(lesson_dto.sections_json)
            changed = False
            for sec in sections:
                if sec.get("type") == "file" and sec.get("fileName") in lesson_previews:
                    sec["previewImageUrl"] = lesson_previews[sec["fileName"]]
                    changed = True
            if changed:
                lesson_dto.sections_json = json.dumps(sections, ensure_ascii=False)
        except Exception:
            pass

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
                select(func.count(func.distinct(ExerciseSubmission.exercise_id))).where(
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


async def _try_auto_ai_review(db: AsyncSession, project: Project) -> None:
    """Best-effort AI grading after a lesson project is submitted.

    Wrapped here so a missing key, an HTTP timeout, or a malformed AI
    response can never break the student's submission flow. Logs the
    failure and lets the project sit at status="Submitted" for the
    teacher to review manually.
    """
    if project is None or not project.github_url:
        return
    try:
        # Lazy import — keeps the cold-start cost out of lessons module
        # load and avoids circular import via the projects router.
        from app.services.ai_review_service import run_ai_review_for_project
        await run_ai_review_for_project(db, project, raise_on_error=False)
    except Exception:
        # Service returns a {"success": False} dict on its known failure
        # modes; an uncaught exception here means something truly unexpected
        # (e.g. network library blew up). Swallow and let the teacher
        # review path keep working.
        pass


# Minimum project score (0-100) to unlock the next lesson WHEN the teacher
# hasn't explicitly approved yet (status="Under Review"). Matches the B-grade
# bucket in the AI prompt ("Yaxshi: asosiy funksional ishlaydi"). A teacher's
# Approve verdict always passes, regardless of score — their judgement is the
# gate. Earlier value (90) was effectively requiring an A and silently
# blocking students whose work was good enough for the lesson.
PROJECT_PASS_THRESHOLD = 75


# ─────────────────────────────────────────────────────────────────────────────
#  STUDENT LESSON FILE DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────
# Matches the URL the FE has always been calling. The earlier file-download
# endpoint (further down, /{lesson_id}/files/{file_id}/download) is
# instructor-only and keyed on file_id; the FE only has file_name from the
# lesson sections payload, so it needs this name-keyed counterpart with
# get_current_student auth + enrolment check.

@router.get("/courses/{course_id}/lessons/{lesson_id}/download")
async def download_lesson_file_for_student(
        course_id: int,
        lesson_id: int,
        file_name: str,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    # Validate the lesson belongs to the course before checking enrolment so
    # cross-course downloads can't sneak through a forged course_id.
    lesson_res = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = lesson_res.scalar_one_or_none()
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    await _ensure_enrolled(db, current_student.id, course_id)

    # Lookup is keyed on the original filename the student sees in the
    # lesson section. Multiple uploads with the same display name pick the
    # newest by created_at, mirroring how the FE renders them.
    file_row = (
        await db.execute(
            select(LessonFile)
            .where(
                LessonFile.lesson_id == lesson_id,
                LessonFile.original_name == file_name,
            )
            .order_by(LessonFile.created_at.desc())
        )
    ).scalars().first()
    if not file_row:
        raise HTTPException(status_code=404, detail="Fayl topilmadi")

    # saved_name is server-issued (UUID-based), so this resolve can't
    # escape LESSONS_FILES_DIR via a crafted file_name query string.
    filepath = LESSONS_FILES_DIR / file_row.saved_name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fayl serverda topilmadi")

    return FileResponse(
        path=str(filepath),
        filename=file_row.original_name,
        media_type="application/octet-stream",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        lang: Optional[str] = None,
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

    if lang and lang != "uz":
        from app.services import translation_store as ts
        for lesson, dto in zip(lessons, result):
            for field_name in ("title", "chapter", "text_content", "task_title",
                               "task_description", "task_requirements", "task_technologies"):
                tr = ts.get("lesson", lesson.id, lang, field_name)
                if tr is not None:
                    setattr(dto, field_name, tr)
            tr_sections = ts.get("lesson", lesson.id, lang, "sections_json")
            if tr_sections:
                dto.sections_json = tr_sections

    await _inject_file_previews(db, [l.id for l in lessons], result)
    return result


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(
        course_id: int,
        lesson_id: int,
        lang: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    if current_student:
        await _ensure_enrolled(db, current_student.id, course_id)
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    # Prerequisite gate: if the previous lesson (by order) has a project,
    # the student must have a passing submission (score ≥ threshold) before
    # they can access this lesson.
    if current_student:
        prev_res = await db.execute(
            select(Lesson).where(
                Lesson.course_id == course_id,
                Lesson.is_active == True,
                Lesson.order < lesson.order,
            ).order_by(Lesson.order.desc()).limit(1)
        )
        prev_lesson = prev_res.scalar_one_or_none()
        if prev_lesson and prev_lesson.has_project:
            pass_check = await db.execute(
                select(Project)
                .join(Submission, Submission.project_id == Project.id)
                .where(
                    Submission.lesson_id == prev_lesson.id,
                    Submission.student_id == current_student.id,
                    Project.points_earned >= PROJECT_PASS_THRESHOLD,
                    Project.status == "Approved",
                )
            )
            if not pass_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Oldingi darsning loyihasini muvaffaqiyatli topshiring",
                )

    res = LessonRead.model_validate(lesson)

    # Translate natural-language fields lazily when the student requests
    # a different language than the lesson was authored in. The service
    # short-circuits when source == target and caches everything else.
    # Wrapped in try/except so the page never 500s if the translation_cache
    # table is missing (migration not yet run) or the AI is down.
    if lang and lang != "uz":
        from app.services import translation_store as ts
        for field_name in ("title", "chapter", "text_content", "task_title",
                           "task_description", "task_requirements", "task_technologies"):
            tr = ts.get("lesson", lesson.id, lang, field_name)
            if tr is not None:
                setattr(res, field_name, tr)
        tr_sections = ts.get("lesson", lesson.id, lang, "sections_json")
        if tr_sections:
            res.sections_json = tr_sections

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

    await _inject_file_previews(db, [lesson_id], [res])
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

async def _check_completion_gate(
        db: AsyncSession,
        lesson: Lesson,
        student_id: int,
) -> None:
    """Raise 400 if the student hasn't met the requirements to complete this lesson.

    Gate rules:
      - Lesson has a project: a non-Draft Submission must exist for this lesson.
      - Lesson has no project: every exercise in the lesson must have at least
        one correct ExerciseSubmission by this student.
    """
    from app.models.exercise import Exercise, ExerciseSubmission

    if lesson.has_project:
        # Authoritative status lives on Project (the teacher reviews the
        # Project row, not the Submission). Submission.status stays "Draft"
        # forever in the current write-path, so we must look through the join.
        sub_res = await db.execute(
            select(Submission.status, Project.status)
            .outerjoin(Project, Project.id == Submission.project_id)
            .where(
                Submission.lesson_id == lesson.id,
                Submission.student_id == student_id,
            )
        )
        statuses = [(p_st or s_st) for (s_st, p_st) in sub_res.all()]
        if not any(st and st not in ("Draft",) for st in statuses):
            raise HTTPException(
                status_code=400,
                detail="Avval shu darsning loyihasini topshiring",
            )
        return

    ex_ids_rows = await db.execute(
        select(Exercise.id).where(Exercise.lesson_id == lesson.id)
    )
    ex_ids = [r[0] for r in ex_ids_rows.all()]
    if not ex_ids:
        # Project-less, exercise-less lesson — nothing to gate on. The teacher
        # might mark it complete from another path; we don't block here.
        return

    correct_rows = await db.execute(
        select(ExerciseSubmission.exercise_id)
        .where(
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.exercise_id.in_(ex_ids),
            ExerciseSubmission.is_correct == True,
        )
        .distinct()
    )
    correct_ids = {r[0] for r in correct_rows.all()}
    missing = len(ex_ids) - len(correct_ids)
    if missing > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Hali {missing} ta mashq to'g'ri yechilmagan",
        )


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    # Idempotent: if already complete, return success without re-awarding points.
    existing = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    already = existing.scalar_one_or_none()
    if already is not None:
        progress = await _calc_course_progress(db, lesson.course_id, current_student.id)
        cert = await achievement_service.award_certificate(db, current_student.id, lesson.course_id)
        return {
            "message": "Dars allaqachon tugatilgan",
            "course_id": lesson.course_id,
            "already_completed": True,
            **progress,
            "certificate_issued": cert is not None,
            "certificate_id": cert.id if cert else None,
        }

    await _check_completion_gate(db, lesson, current_student.id)

    result = await lesson_service.complete_lesson(db, lesson_id, current_student.id)
    course_id = result.get("course_id")

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)
    progress = await _calc_course_progress(db, course_id, current_student.id)

    try:
        from app.services.streak_service import bump_streak
        await bump_streak(db, current_student.id)
        await db.commit()
    except Exception:
        await db.rollback()

    # Check lesson_count / course_count / points_threshold achievements
    try:
        await achievement_service.check_and_award_achievements(db, current_student.id)
    except Exception:
        pass

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

        # Reverse points only if they were actually awarded (Approved project).
        # Rejected projects store points_earned from the AI score but never
        # add those to the student, so subtracting them would deduct phantom points.
        if prev_points > 0 and proj_status == "Approved":
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

        # Re-run AI on resubmission too so a fresh attempt gets graded
        # without waiting on a teacher. The service handles the previous
        # points reversal internally.
        await _try_auto_ai_review(db, existing_project)

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
    # LessonCompletion is intentionally NOT created here on submission.
    # It is created only when the project is approved (score ≥ threshold)
    # in ai_review_service and the teacher review endpoint, so that the
    # next lesson stays locked until the student actually passes.

    try:
        await db.commit()
    except IntegrityError:
        # Defense-in-depth: if the partial unique index is in place and we
        # still raced past the existing-check (e.g. cross-process without
        # the row lock holding), turn the DB error into a clean 400.
        await db.rollback()
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

    # Auto-trigger AI review so GitHub-URL submissions don't wait for a
    # teacher just to get a first grade. raise_on_error=False keeps any AI
    # failure from breaking the submission: project stays at "Submitted"
    # / "На проверке" and the teacher can review manually.
    await _try_auto_ai_review(db, new_project)

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
    import json as _json

    def _parse_json_list(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        try:
            return _json.loads(val)
        except Exception:
            return []

    ai_bugs = _parse_json_list(project.ai_bugs if project else None)
    ai_improvements = _parse_json_list(project.ai_improvements if project else None)
    ai_strengths = _parse_json_list(project.ai_strengths if project else None)
    reviewed = proj_status in ("Approved", "Rejected")
    # Pass = score clears the threshold AND status isn't an explicit fail/draft.
    # The teacher's "Approved" action alone is NOT a pass signal — the review
    # endpoint marks every reviewed project Approved regardless of score, so
    # we trust the points they entered as the real verdict (matches what the
    # student sees in the "X/100" badge).
    passed = (
        points_earned >= PROJECT_PASS_THRESHOLD
        and proj_status not in ("Rejected", "Draft")
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
        "ai_bugs": ai_bugs,
        "ai_improvements": ai_improvements,
        "ai_strengths": ai_strengths,
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
            "preview_image_url": f.preview_image_url,
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
        "preview_image_url": lesson_file.preview_image_url,
        "created_at": lesson_file.created_at
    }


# ============================================================
# 3b. PREVIEW RASM YUKLASH
# ============================================================

@router.post("/{lesson_id}/files/{file_id}/preview", status_code=status.HTTP_200_OK)
async def upload_lesson_file_preview(
        lesson_id: int,
        file_id: int,
        image: UploadFile = File(...),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Teacher uploads a preview screenshot for a lesson file."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if image.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Faqat rasm fayllari (JPEG, PNG, WebP, GIF)")

    result = await db.execute(
        select(LessonFile).where(LessonFile.id == file_id, LessonFile.lesson_id == lesson_id)
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    contents = await image.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Rasm 5MB dan katta bo'lmasin")

    # Delete old preview if exists
    if lesson_file.preview_image_url:
        old_name = Path(lesson_file.preview_image_url).name
        old_path = LESSON_PREVIEWS_DIR / old_name
        if old_path.exists():
            old_path.unlink()

    ext = Path(image.filename).suffix.lower() if image.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = LESSON_PREVIEWS_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    lesson_file.preview_image_url = f"/uploads/lesson_previews/{filename}"
    await db.commit()
    await db.refresh(lesson_file)

    return {"preview_image_url": lesson_file.preview_image_url}


@router.delete("/{lesson_id}/files/{file_id}/preview", status_code=status.HTTP_200_OK)
async def delete_lesson_file_preview(
        lesson_id: int,
        file_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LessonFile).where(LessonFile.id == file_id, LessonFile.lesson_id == lesson_id)
    )
    lesson_file = result.scalar_one_or_none()
    if not lesson_file:
        raise HTTPException(status_code=404, detail="Fayl topilmadi!")

    if lesson_file.preview_image_url:
        old_path = LESSON_PREVIEWS_DIR / Path(lesson_file.preview_image_url).name
        if old_path.exists():
            old_path.unlink()
        lesson_file.preview_image_url = None
        await db.commit()

    return {"ok": True}


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


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON VOCABULARY  (teacher manages, students check preparation)
# ─────────────────────────────────────────────────────────────────────────────

class VocabIn(BaseModel):
    word: str
    definition: str
    order: int = 0

class VocabOut(BaseModel):
    id: int
    word: str
    definition: str
    order: int
    class Config:
        from_attributes = True


@router.get("/courses/{course_id}/lessons/{lesson_id}/vocabulary", response_model=List[VocabOut])
async def get_lesson_vocabulary(
        lesson_id: int,
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student),
):
    rows = (await db.execute(
        select(LessonVocabulary)
        .where(LessonVocabulary.lesson_id == lesson_id)
        .order_by(LessonVocabulary.order, LessonVocabulary.id)
    )).scalars().all()
    return rows


@router.post("/courses/{course_id}/lessons/{lesson_id}/vocabulary", response_model=VocabOut)
async def add_vocab_word(
        lesson_id: int,
        course_id: int,
        data: VocabIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    word = data.word.strip()
    definition = data.definition.strip()
    if not word or not definition:
        raise HTTPException(status_code=422, detail="So'z va ta'rif bo'sh bo'lishi mumkin emas")
    vocab = LessonVocabulary(lesson_id=lesson_id, word=word, definition=definition, order=data.order)
    db.add(vocab)
    await db.commit()
    await db.refresh(vocab)
    return vocab


@router.put("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}", response_model=VocabOut)
async def update_vocab_word(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        data: VocabIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    vocab = (await db.execute(
        select(LessonVocabulary).where(
            LessonVocabulary.id == vocab_id,
            LessonVocabulary.lesson_id == lesson_id,
        )
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")
    vocab.word = data.word.strip()
    vocab.definition = data.definition.strip()
    vocab.order = data.order
    await db.commit()
    await db.refresh(vocab)
    return vocab


@router.delete("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}")
async def delete_vocab_word(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    vocab = (await db.execute(
        select(LessonVocabulary).where(
            LessonVocabulary.id == vocab_id,
            LessonVocabulary.lesson_id == lesson_id,
        )
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")
    await db.delete(vocab)
    await db.commit()
    return {"ok": True}


@router.post("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}/add-to-dict")
async def add_vocab_to_dict(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student),
):
    """Student marks a vocab word as unknown — add it to their personal dictionary."""
    vocab = (await db.execute(
        select(LessonVocabulary).where(LessonVocabulary.id == vocab_id)
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")

    existing = (await db.execute(
        select(UserDictionary).where(
            UserDictionary.student_id == current_user.id,
            func.lower(UserDictionary.word) == vocab.word.lower(),
        )
    )).scalar_one_or_none()
    if existing:
        return {"ok": True, "already_exists": True}

    db.add(UserDictionary(
        student_id=current_user.id,
        word=vocab.word,
        context=vocab.definition,
        lesson_id=lesson_id,
    ))
    await db.commit()
    return {"ok": True, "already_exists": False}


# ── Sample project ────────────────────────────────────────────────────────────

@router.get("/lessons/{lesson_id}/sample")
async def get_lesson_sample(
        lesson_id: int,
        db: AsyncSession = Depends(get_db),
):
    from app.models.lesson_sample import LessonSample
    from app.schemas.lesson_sample import LessonSampleRead
    result = await db.execute(select(LessonSample).where(LessonSample.lesson_id == lesson_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample topilmadi")
    return LessonSampleRead.model_validate(sample)
