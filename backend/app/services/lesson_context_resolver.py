"""Resolve the lesson + course a project belongs to.

A project is linked to a lesson through `submissions`
(submissions.project_id → submissions.lesson_id) — there is no direct
project.lesson_id column. Standalone projects (no submission row)
resolve to None and the AI grader falls back to a generic persona.

Single source of truth so the regrade endpoint, the upload endpoint,
and the main AI review pipeline all build the same context dict.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.submission import Submission


async def load_lesson_context_for_project(
    db: AsyncSession, *, project_id: int
) -> Optional[dict]:
    """Return the lesson_context dict consumed by
    `analyze_project_with_grok`, or None if the project isn't tied to
    any lesson (standalone submission / data drift)."""
    sub_row = (await db.execute(
        select(Submission.lesson_id)
        .where(Submission.project_id == project_id)
        .where(Submission.lesson_id.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    )).first()
    if not sub_row or sub_row[0] is None:
        return None
    lesson_id = sub_row[0]

    lesson = (await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )).scalar_one_or_none()
    if lesson is None:
        return None

    course = (await db.execute(
        select(Course).where(Course.id == lesson.course_id)
    )).scalar_one_or_none()

    return {
        "course_title": course.title if course else None,
        "course_difficulty": course.difficulty_level if course else None,
        "lesson_title": lesson.title,
        "lesson_order": lesson.order,
        "lesson_code_language": lesson.code_language,
        "task_title": lesson.task_title,
        "task_description": lesson.task_description,
        "task_requirements": lesson.task_requirements,
        "task_technologies": lesson.task_technologies,
    }
