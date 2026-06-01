"""Non-destructive upgrade: append missing exercises to existing Python Flask course.

Use when LESSONS in seed_flask_course.py has more exercises than what's
currently in the DB for the same course (e.g. after we added 2 extra
exercises to lessons 3, 7, 8, 9, 10).

Idempotent: only inserts exercises beyond the current count, then rebuilds
sections_json for any lesson that gained new exercises. Running again does
nothing.

Usage:
    cd backend
    python scripts/upgrade_flask_exercises.py            # apply
    python scripts/upgrade_flask_exercises.py --dry-run  # preview
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: F401,E402
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

# Reuse the canonical lesson definitions + helpers from the seed script.
from scripts.seed_flask_course import (  # noqa: E402
    COURSE, LESSONS, _jdump, build_sections_json,
)


def _build_exercise_row(lesson_id: int, ex: dict, order_idx: int) -> Exercise:
    return Exercise(
        lesson_id=lesson_id,
        title=ex["title"],
        description=ex.get("description", ex["title"]),
        exercise_type=ex["exercise_type"],
        options=_jdump(ex.get("options")),
        correct_answers=_jdump(ex.get("correct_answers")),
        drag_items=_jdump(ex.get("drag_items")),
        correct_order=_jdump(ex.get("correct_order")),
        is_multiple_select=bool(ex.get("is_multiple_select", False)),
        expected_answer=ex.get("expected_answer", ""),
        hint=ex.get("hint", ""),
        explanation=ex.get("explanation", ""),
        difficulty_level=ex["difficulty_level"],
        points=ex["points"],
        order=order_idx,
        is_active=True,
    )


async def upgrade(dry_run: bool = False) -> None:
    new_lessons = 0
    new_exercises = 0
    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if not course:
            print(f"Course '{COURSE['title']}' not found — run seed_flask_course.py first.")
            return
        print(f"Found course id={course.id}  title='{course.title}'")

        for ldata in LESSONS:
            lesson = (
                await db.execute(
                    select(Lesson).where(
                        Lesson.course_id == course.id,
                        Lesson.order == ldata["order"],
                    )
                )
            ).scalar_one_or_none()

            # Case 1: lesson missing entirely → create it + all its exercises
            if not lesson:
                lesson = Lesson(
                    course_id=course.id,
                    title=ldata["title"],
                    order=ldata["order"],
                    points_reward=10,
                    text_content=ldata["text"],
                    code_content=ldata["code"],
                    code_language=ldata["lang"],
                    video_url=ldata["video"],
                    sections_json=None,
                    is_active=True,
                    is_published=True,
                )
                db.add(lesson)
                await db.flush()

                ex_rows = [
                    _build_exercise_row(lesson.id, ex, i)
                    for i, ex in enumerate(ldata["exercises"])
                ]
                for r in ex_rows:
                    db.add(r)
                await db.flush()
                lesson.sections_json = build_sections_json(ldata, ex_rows)
                new_lessons += 1
                new_exercises += len(ex_rows)
                print(f"  L{ldata['order']+1:>2} {ldata['title']:<40}  NEW LESSON ({len(ex_rows)} ex)")
                continue

            # Case 2: lesson exists → check if its exercises are up to date
            existing = (
                await db.execute(
                    select(Exercise)
                    .where(Exercise.lesson_id == lesson.id)
                    .order_by(Exercise.order, Exercise.id)
                )
            ).scalars().all()
            existing_count = len(existing)
            target_count = len(ldata["exercises"])

            if existing_count >= target_count:
                print(f"  L{ldata['order']+1:>2} {lesson.title:<40}  "
                      f"existing={existing_count} target={target_count}  (skip)")
                continue

            # Append missing tail exercises
            tail = ldata["exercises"][existing_count:]
            new_rows = [
                _build_exercise_row(lesson.id, ex, existing_count + i)
                for i, ex in enumerate(tail)
            ]
            for r in new_rows:
                db.add(r)
            await db.flush()
            all_rows = existing + new_rows
            lesson.sections_json = build_sections_json(ldata, all_rows)
            new_exercises += len(new_rows)
            print(f"  L{ldata['order']+1:>2} {lesson.title:<40}  "
                  f"existing={existing_count} → {len(all_rows)} (+{len(new_rows)} new)")

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would add {new_lessons} lessons + {new_exercises} exercises. Rolled back.")
        else:
            await db.commit()
            print(f"\nUpgrade complete: +{new_lessons} lessons, +{new_exercises} exercises.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(upgrade(dry_run="--dry-run" in sys.argv))
