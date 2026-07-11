"""Shared utilities for the lessons endpoints.

No HTTP routes live here — only helpers imported by the split modules.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.config import settings
from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.models.lesson_file import LessonFile
from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student, UserRole

LESSONS_FILES_DIR = Path(settings.UPLOAD_DIR) / "lesson_files"
LESSONS_FILES_DIR.mkdir(parents=True, exist_ok=True)
LESSON_PREVIEWS_DIR = Path(settings.UPLOAD_DIR) / "lesson_previews"
LESSON_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CODE_EXTENSIONS = {
    ".html", ".css", ".js", ".py", ".ts", ".jsx", ".tsx",
    ".json", ".xml", ".php", ".java", ".cpp", ".c", ".sql"
}

PROJECT_PASS_THRESHOLD = 75


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
    """Hard-lock: only enrolled students, the course instructor, or any teacher may proceed."""
    stmt = select(Student).options(selectinload(Student.enrolled_courses)).where(Student.id == student_id)
    res = await db.execute(stmt)
    student = res.scalar_one()

    # Teachers can view any course's content (they review and manage lessons)
    if student.role == UserRole.teacher:
        return

    course_res = await db.execute(select(Course).where(Course.id == course_id))
    course = course_res.scalar_one_or_none()
    if course and course.instructor_id == student_id:
        return

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
        from app.services.ai_review_service import run_ai_review_for_project
        await run_ai_review_for_project(db, project, raise_on_error=False)
    except Exception:
        pass


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
