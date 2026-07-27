"""Create Exercise rows for every lesson in a spec module and rebuild each
lesson's sections_json exercise section from them.

Usage:
    cd backend
    python scripts/create_exercises.py course_specs/my_course.py
    # add --dry-run to preview without writing

Requires lessons to already exist (run create_lessons.py first). Run
check_exercise_integrity.py <course_id> right after this, before
translating — no point translating a broken answer key.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

from course_builder.spec_loader import load_spec, require  # noqa: E402
from course_builder.db_helpers import sync_lesson_exercises  # noqa: E402


async def main(spec_path: str, dry_run: bool) -> int:
    module = load_spec(spec_path)
    course_spec = require(module, "COURSE")
    lessons_spec = require(module, "LESSONS")

    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(select(Course).where(Course.title == course_spec["title"]))
        ).scalar_one_or_none()
        if not course:
            print(f"course {course_spec['title']!r} does not exist yet — run create_course.py first")
            return 1

        total_created = 0
        for lesson_spec in lessons_spec:
            exercise_specs = lesson_spec.get("exercises") or []
            if not exercise_specs:
                continue
            lesson = (
                await db.execute(
                    select(Lesson).where(Lesson.course_id == course.id, Lesson.order == lesson_spec["order"])
                )
            ).scalar_one_or_none()
            if not lesson:
                print(f"  lesson order={lesson_spec['order']}: not found — run create_lessons.py first, skipping")
                continue

            already_had = bool((
                await db.execute(select(Exercise.id).where(Exercise.lesson_id == lesson.id))
            ).first())
            rows = await sync_lesson_exercises(db, lesson, exercise_specs)
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5}: "
                  f"{len(rows)} exercise(s){' (already existed)' if already_had else ''}")
            total_created += len(rows)

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would have {total_created} exercise row(s) across the course.")
        else:
            await db.commit()
            print(f"\n{total_created} exercise row(s) present across the course "
                  f"(id={course.id}). Run check_exercise_integrity.py {course.id} next.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
