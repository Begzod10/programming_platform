"""Create the namuna (LessonSample) row for every lesson in a spec module
that defines one.

Usage:
    cd backend
    python scripts/create_samples.py course_specs/my_course.py
    # add --dry-run to preview without writing

Requires lessons to already exist (run create_lessons.py first).
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

from course_builder.spec_loader import load_spec, require  # noqa: E402
from course_builder.db_helpers import sync_lesson_sample  # noqa: E402


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

        created = 0
        for lesson_spec in lessons_spec:
            sample_spec = lesson_spec.get("sample")
            if not sample_spec:
                continue
            lesson = (
                await db.execute(
                    select(Lesson).where(Lesson.course_id == course.id, Lesson.order == lesson_spec["order"])
                )
            ).scalar_one_or_none()
            if not lesson:
                print(f"  lesson order={lesson_spec['order']}: not found — run create_lessons.py first, skipping")
                continue
            sample = await sync_lesson_sample(db, lesson.id, sample_spec)
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5}: sample {sample.title!r}")
            created += 1

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would have {created} sample(s) present across the course.")
        else:
            await db.commit()
            print(f"\n{created} sample(s) present across the course (id={course.id}).")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
