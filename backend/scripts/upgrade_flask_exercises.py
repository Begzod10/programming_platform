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


async def upgrade(dry_run: bool = False) -> None:
    total_added = 0
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
            if not lesson:
                print(f"  ⚠ lesson order={ldata['order']} '{ldata['title']}' missing — skip")
                continue

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
                print(f"  L{ldata['order']+1:>2} {lesson.title:<32}  "
                      f"existing={existing_count} target={target_count}  (skip)")
                continue

            # Append the tail
            tail = ldata["exercises"][existing_count:]
            new_rows: list[Exercise] = []
            for i, ex in enumerate(tail):
                row = Exercise(
                    lesson_id=lesson.id,
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
                    order=existing_count + i,
                    is_active=True,
                )
                db.add(row)
                new_rows.append(row)
            await db.flush()  # need ids for sections_json

            # Rebuild sections_json with ALL exercises (existing tail incoming too).
            all_rows = existing + new_rows
            lesson.sections_json = build_sections_json(ldata, all_rows)
            total_added += len(new_rows)
            print(f"  L{ldata['order']+1:>2} {lesson.title:<32}  "
                  f"existing={existing_count} → {len(all_rows)} (+{len(new_rows)} new)")

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would have added {total_added} exercises. Rolled back.")
        else:
            await db.commit()
            print(f"\nUpgrade complete: {total_added} new exercises added.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(upgrade(dry_run="--dry-run" in sys.argv))
