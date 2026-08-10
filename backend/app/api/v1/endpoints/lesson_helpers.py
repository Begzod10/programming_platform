"""Shared utilities for the lessons endpoints.

No HTTP routes live here — only helpers imported by the split modules.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

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
from app.services.translation_service import DEFAULT_SOURCE_LANG, translate_fields

logger = logging.getLogger(__name__)

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


# Fields the frontend's ExerciseCard actually renders. Deliberately excludes
# correct_answers / expected_answer / correct_order / explanation — those are
# grading secrets and must never reach the browser before submission.
_EXERCISE_RENDER_FIELDS = (
    "title", "description", "exercise_type", "options", "drag_items",
    "is_multiple_select", "hint", "difficulty_level", "points", "order",
)


_EXERCISE_TRANSLATABLE_FIELDS = ("title", "description", "hint", "drag_items", "options")


async def _hydrate_exercise_sections(db: AsyncSession, lessons_data: list, lang: str | None = None) -> None:
    """Fill in bare ``{"id": N}`` exercise stubs inside sections_json with the
    full exercise payload the frontend needs to render the card.

    Content-authoring scripts (see scripts/enrich_course_lessons.py) write
    only an id into each exercise section entry, on the assumption that the
    frontend fetches the full row per id. It never did — ExerciseCard reads
    ex.description / ex.exercise_type / ex.options straight off the object
    handed to it — so any lesson touched by those scripts rendered an empty
    exercise card (no question text, no options, just the submit button).
    Hydrating here fixes every affected lesson centrally instead of
    rewriting sections_json row by row.

    `lang`: when set to a non-Uzbek language, each of the 5 translatable
    fields (_EXERCISE_TRANSLATABLE_FIELDS) is looked up in translation_store
    first, falling back to the raw (Uzbek) column if no translation exists.
    Without this, a stub exercise was ALWAYS hydrated straight from the
    live Exercise row regardless of the requested lang — the in-lesson
    exercise view (the actual student-facing rendering path; the
    entity_type='exercise' translation this mirrors has no other reader,
    since GET .../exercises is never called by any frontend code) silently
    showed Uzbek text to Russian students for every exercise stored as a
    stub, no matter how complete translation_cache was for that exercise.
    """
    from app.models.exercise import Exercise
    from app.services import translation_store as ts

    parsed_by_lesson: dict[int, list] = {}
    needed_ids: set[int] = set()
    for dto in lessons_data:
        if not dto.sections_json:
            continue
        try:
            sections = json.loads(dto.sections_json)
        except Exception:
            continue
        has_stub = False
        for sec in sections:
            if sec.get("type") != "exercise":
                continue
            for ex in sec.get("exercises", []) or []:
                if "description" not in ex and ex.get("id"):
                    has_stub = True
                    needed_ids.add(ex["id"])
        if has_stub:
            parsed_by_lesson[dto.id] = sections

    if not needed_ids:
        return

    rows = (await db.execute(
        select(Exercise).where(Exercise.id.in_(needed_ids))
    )).scalars().all()
    by_id = {row.id: row for row in rows}
    translate = bool(lang) and lang != "uz"

    for dto in lessons_data:
        sections = parsed_by_lesson.get(dto.id)
        if sections is None:
            continue
        for sec in sections:
            if sec.get("type") != "exercise":
                continue
            hydrated = []
            for ex in sec.get("exercises", []) or []:
                row = by_id.get(ex.get("id")) if "description" not in ex else None
                if row is not None:
                    payload = {f: getattr(row, f) for f in _EXERCISE_RENDER_FIELDS}
                    if translate:
                        for field in _EXERCISE_TRANSLATABLE_FIELDS:
                            tr = ts.get("exercise", row.id, lang, field)
                            if tr:
                                payload[field] = tr
                    hydrated.append({"id": row.id, **payload})
                else:
                    hydrated.append(ex)
            sec["exercises"] = hydrated
        dto.sections_json = json.dumps(sections, ensure_ascii=False)


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
        # A project only counts as "done" once it has passed review — a
        # merely-submitted (pending/rejected/low-score) project must not
        # push progress to 100%, since that's what the course lesson-list
        # page uses to decide whether the next lesson is unlocked. Mirrors
        # the same Approved + points_earned >= PROJECT_PASS_THRESHOLD check
        # used in _check_completion_gate below.
        sub_res = await db.execute(
            select(Project.status, Project.points_earned)
            .join(Submission, Submission.project_id == Project.id)
            .where(
                Submission.lesson_id == lesson.id,
                Submission.student_id == student_id,
            )
        )
        has_passing = any(
            (p_st or "") == "Approved" and (pts or 0) >= PROJECT_PASS_THRESHOLD
            for (p_st, pts) in sub_res.all()
        )
        if has_passing:
            done += total_projects

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
    response can never break the student's submission flow. Records why
    the review didn't happen and lets the project sit at
    status="Submitted" for the teacher to review manually.

    Accepts ZIP uploads as well as GitHub URLs: run_ai_review_for_project
    grades either source. Requiring github_url here used to drop every
    ZIP-based lesson submission out of the grader with nothing written
    anywhere, so those projects sat unreviewed and un-diagnosable.
    """
    if project is None:
        return
    if not project.github_url and not project.project_files:
        # Nothing to grade yet — the ZIP upload endpoint re-triggers the
        # review once a file lands, so this is an expected no-op.
        return

    try:
        from app.services.ai_review_service import run_ai_review_for_project
        result = await run_ai_review_for_project(db, project, raise_on_error=False)
    except Exception as e:
        logger.warning("[ai-auto] project=%s unhandled error: %s", project.id, e)
        result = {
            "success": False,
            "reason": "AI baholash vaqtincha ishlamayapti. "
                      "O'qituvchi loyihangizni tez orada baholaydi.",
        }

    # Leave a trace of the failure on the row. Without this a skipped
    # review is indistinguishable from one that never ran, and neither the
    # student nor the teacher has any way to know a retry would fix it.
    if not result.get("success") and project.reviewed_at is None:
        reason = result.get("reason", "AI tekshirish muvaffaqiyatsiz")
        logger.info("[ai-auto] project=%s not graded: %s", project.id, reason)
        project.instructor_feedback = reason
        await db.commit()
        await db.refresh(project)


async def translate_project_feedback(
        db: AsyncSession,
        *,
        project_id: int,
        lang: Optional[str],
        feedback: Optional[str],
        strengths: list,
        improvements: list,
        bugs: list,
) -> tuple[Optional[str], list, list, list]:
    """Serve AI review feedback in the student's chosen language.

    The grader always writes Uzbek, so a student reading the platform in
    Russian saw Russian chrome and a Russian task description wrapped
    around an Uzbek verdict. Rather than re-grading, we translate on read
    through the same cache the lesson/course text uses — that keeps the
    stored grade authoritative and fixes the whole back catalogue, not
    just newly graded work.

    The three AI fields are JSON arrays of bare strings, which
    translate_json_blob cannot walk (it only descends into dict keys), so
    each item is cached as its own field: `ai_strengths.0`, `.1`, …
    Falls back to the Uzbek source on any failure — an untranslated
    verdict beats no verdict.
    """
    if not lang or lang == DEFAULT_SOURCE_LANG:
        return feedback, strengths, improvements, bugs

    lists = {
        "ai_strengths": strengths,
        "ai_improvements": improvements,
        "ai_bugs": bugs,
    }

    fields: dict[str, Optional[str]] = {"instructor_feedback": feedback}
    for name, values in lists.items():
        for i, item in enumerate(values):
            if isinstance(item, str):
                fields[f"{name}.{i}"] = item

    try:
        out = await translate_fields(
            db,
            entity_type="project",
            entity_id=project_id,
            target_lang=lang,
            fields=fields,
            source_lang=DEFAULT_SOURCE_LANG,
        )
    except Exception:
        logger.exception(
            "translate_project_feedback: failed for project=%s lang=%s",
            project_id, lang,
        )
        return feedback, strengths, improvements, bugs

    def _rebuild(name: str, values: list) -> list:
        return [
            out.get(f"{name}.{i}", item) if isinstance(item, str) else item
            for i, item in enumerate(values)
        ]

    return (
        out.get("instructor_feedback", feedback),
        _rebuild("ai_strengths", strengths),
        _rebuild("ai_improvements", improvements),
        _rebuild("ai_bugs", bugs),
    )


async def _check_completion_gate(
        db: AsyncSession,
        lesson: Lesson,
        student_id: int,
) -> None:
    """Raise 400 if the student hasn't met the requirements to complete this lesson.

    Gate rules:
      - Lesson has a project: an Approved Project with points_earned >=
        PROJECT_PASS_THRESHOLD must exist for this lesson. A Draft, Submitted,
        or Rejected project does NOT unlock the next lesson.
      - Lesson has no project: every exercise in the lesson must have at least
        one correct ExerciseSubmission by this student.
    """
    from app.models.exercise import Exercise, ExerciseSubmission

    if lesson.has_project:
        sub_res = await db.execute(
            select(Project.status, Project.points_earned)
            .join(Submission, Submission.project_id == Project.id)
            .where(
                Submission.lesson_id == lesson.id,
                Submission.student_id == student_id,
            )
        )
        rows = sub_res.all()
        if not rows:
            raise HTTPException(
                status_code=400,
                detail="Avval shu darsning loyihasini topshiring",
            )
        has_pending = any(
            (p_st or "") == "Submitted" for (p_st, _pts) in rows
        )
        has_passing = any(
            (p_st or "") == "Approved"
            and (pts or 0) >= PROJECT_PASS_THRESHOLD
            for (p_st, pts) in rows
        )
        if has_passing:
            return
        if has_pending:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Loyiha hali tekshirilmoqda. Natijani kuting — "
                    "keyingi dars faqat tasdiqlangandan so'ng ochiladi."
                ),
            )
        raise HTTPException(
            status_code=400,
            detail=(
                "Loyiha kamida 75 ball to'plamagan. Qayta topshiring, "
                "so'ng keyingi dars ochiladi."
            ),
        )

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
