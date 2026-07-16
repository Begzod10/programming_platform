"""Single source of truth for LessonCompletion + lesson.points_reward flow.

Three call sites (AI review, teacher review, exercise auto-complete) all mutate
LessonCompletion + apply the lesson's points_reward when a student passes.
Previously each site had its own hand-rolled insert/skip logic and NONE unwound
the completion when a project was demoted (Approved -> Rejected on re-review),
so lesson-reward points accumulated permanently even for now-failing lessons.

`reconcile_lesson_completion` collapses those paths into one idempotent
operation:
  - passing=True  and no completion -> insert row + add points_reward
  - passing=True  and completion    -> no-op (never double-award)
  - passing=False and completion    -> delete row + subtract points_reward
  - passing=False and no completion -> no-op

The DB-level UniqueConstraint on (student_id, lesson_id) is the ultimate
safety net; this helper additionally catches IntegrityError from a racing
insert so callers never see a 500.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson, LessonCompletion

if TYPE_CHECKING:
    from app.services.ranking_service import RankingService


async def reconcile_lesson_completion(
    db: AsyncSession,
    *,
    student_id: int,
    lesson_id: int,
    passing: bool,
    ranking_service: "RankingService",
) -> None:
    """Bring (student, lesson) completion + reward state in line with `passing`.

    Idempotent — safe to call from any status transition path. The caller is
    responsible for the outer commit; this helper only flushes.
    """
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if lesson is None:
        # Lesson was deleted (e.g. course cleanup). Nothing to reconcile.
        return

    points_reward = int(lesson.points_reward or 0)

    existing_res = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == student_id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    existing = existing_res.scalar_one_or_none()

    if passing:
        if existing is not None:
            # Already credited — never double-award.
            return
        db.add(LessonCompletion(student_id=student_id, lesson_id=lesson_id))
        try:
            await db.flush()
        except IntegrityError:
            # Concurrent request inserted the row first. That request also
            # awarded the points_reward, so we must NOT award again.
            await db.rollback()
            return
        if points_reward > 0:
            await ranking_service.add_points_to_student(student_id, points_reward)
        return

    # Not passing.
    if existing is None:
        return
    await db.delete(existing)
    await db.flush()
    if points_reward > 0:
        await ranking_service.subtract_points_from_student(student_id, points_reward)
