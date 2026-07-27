"""Write RU translations for every exercise in a spec module (title,
description, hint, options/drag_items — auto-deriving correct_order_ru by
index-mapping, never hand-typed) from each exercise dict's _ru fields.

Usage:
    cd backend
    python scripts/translate_exercises_ru.py course_specs/my_course.py

Requires exercises to already exist (run create_exercises.py first). Run
check_ru_coverage.py <course_id> after this to confirm full coverage.
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
from course_builder.translations import translate_exercises_from_spec  # noqa: E402


async def main(spec_path: str) -> int:
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

        total_exercises = 0
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
            rows = (
                await db.execute(
                    select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.order)
                )
            ).scalars().all()
            if len(rows) != len(exercise_specs):
                print(f"  lesson order={lesson_spec['order']}: {len(rows)} exercise row(s) in DB "
                      f"but {len(exercise_specs)} in spec — run create_exercises.py first, skipping")
                continue
            count = await translate_exercises_from_spec(db, list(rows), exercise_specs)
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5}: "
                  f"{count}/{len(rows)} exercise(s) translated")
            total_exercises += count

        await db.commit()
        print(f"\nTranslated {total_exercises} exercise(s) across the course (id={course.id}).")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(sys.argv[1])))
