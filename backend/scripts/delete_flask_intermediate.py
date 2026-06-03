"""Delete the "Python Flask — O'rta daraja" course and everything under it.

Use this when the seed needs to be re-run from scratch (e.g. after fixing
broken Mermaid diagrams). Cascades through lessons, exercises, and
sections via SQLAlchemy relationships.

Usage:
    cd backend
    python scripts/delete_flask_intermediate.py
    # add --dry-run to preview without deleting

Safe to re-run: if the course doesn't exist, prints a notice and exits 0.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, delete  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


COURSE_TITLE = "Python Flask — O'rta daraja"


async def delete_course(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(
                select(Course).where(Course.title == COURSE_TITLE)
            )
        ).scalar_one_or_none()

        if course is None:
            print(f"Course '{COURSE_TITLE}' not found — nothing to delete.")
            return

        # Count what we're about to wipe so the operator can sanity-check.
        lesson_ids = (
            await db.execute(
                select(Lesson.id).where(Lesson.course_id == course.id)
            )
        ).scalars().all()

        exercise_count = 0
        if lesson_ids:
            exercise_count = len(
                (
                    await db.execute(
                        select(Exercise.id)
                        .where(Exercise.lesson_id.in_(lesson_ids))
                    )
                ).scalars().all()
            )

        print(f"Found course id={course.id}  title='{course.title}'")
        print(f"  → {len(lesson_ids)} lessons, {exercise_count} exercises")

        if dry_run:
            print("\nDRY RUN — nothing deleted.")
            return

        # Delete in reverse-dependency order so we don't rely on DB cascades
        # being configured (some installs may not have ON DELETE CASCADE set).
        if lesson_ids:
            await db.execute(
                delete(Exercise).where(Exercise.lesson_id.in_(lesson_ids))
            )
            await db.execute(
                delete(Lesson).where(Lesson.course_id == course.id)
            )
        await db.execute(delete(Course).where(Course.id == course.id))
        await db.commit()

        print(f"Deleted course id={course.id} and all dependents.")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(delete_course(dry_run=dry))
