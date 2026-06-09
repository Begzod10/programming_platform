"""Bulk-assign every course to a category based on its difficulty_level.

Run once after creating the Category model. Idempotent — re-running won't
change anything that's already in the right bucket and won't duplicate
category rows (lookup is case-insensitive by name).

Default mapping:
    Beginner     → "Beginner"
    Intermediate → "Intermediate"
    Advanced     → "Advanced"
    Expert       → "Advanced"   (no separate Expert bucket by default)

To customize: edit MAPPING below before running.

Usage:
    cd backend
    venv/bin/python scripts/assign_default_categories.py
    # add --dry-run to preview without writing
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.category import Category  # noqa: E402
from app.models.course import Course  # noqa: E402
from app.services.course_service import resolve_category  # noqa: E402


MAPPING: dict[str, str] = {
    "Beginner":     "Beginner",
    "Intermediate": "Intermediate",
    "Advanced":     "Advanced",
    "Expert":       "Advanced",
}


async def run(dry_run: bool) -> None:
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        courses = (await db.execute(select(Course))).scalars().all()
        if not courses:
            print("No courses found — nothing to do.")
            return

        # Resolve every target category up-front so the loop only does updates.
        # resolve_category is idempotent — existing rows are reused, new ones
        # are inserted, slug collisions get a numeric suffix.
        name_to_id: dict[str, int] = {}
        for cat_name in set(MAPPING.values()):
            cat_id = await resolve_category(
                db,
                category_id=None,
                category_name=cat_name,
                created_by_id=None,
            )
            name_to_id[cat_name] = cat_id
            print(f"  category «{cat_name}» → id={cat_id}")

        assigned = 0
        skipped = 0
        unmapped = 0
        for course in courses:
            target_name = MAPPING.get(course.difficulty_level or "")
            if target_name is None:
                unmapped += 1
                print(
                    f"  ↷ #{course.id:<3} {course.title!r:<45} "
                    f"difficulty={course.difficulty_level!r} — no mapping, skipped"
                )
                continue

            target_id = name_to_id[target_name]
            if course.category_id == target_id:
                skipped += 1
                continue

            old = course.category_id
            course.category_id = target_id
            assigned += 1
            print(
                f"  ✓ #{course.id:<3} {course.title!r:<45} "
                f"category {old!r:>6} → {target_id} ({target_name})"
            )

        if dry_run:
            print(f"\nDRY-RUN: would assign {assigned}, leave {skipped}, "
                  f"skip {unmapped}. No commit.")
            await db.rollback()
        else:
            await db.commit()
            print(f"\nDone — assigned {assigned}, unchanged {skipped}, "
                  f"unmapped {unmapped}.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(run(dry_run=dry))
