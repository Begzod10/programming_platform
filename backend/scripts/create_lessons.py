"""Create (or find, idempotently) every Lesson row for a spec module's
COURSE + LESSONS. Does NOT create exercises, samples, or task fields —
see create_exercises.py / create_samples.py / set_submission_tasks.py.

Usage:
    cd backend
    python scripts/create_lessons.py course_specs/my_course.py
    # add --dry-run to preview without writing

Requires the course to already exist (run create_course.py first).
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

from course_builder.spec_loader import load_spec, require  # noqa: E402
from course_builder.db_helpers import get_or_create_lesson  # noqa: E402


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

        created_count = 0
        for lesson_spec in lessons_spec:
            lesson, created = await get_or_create_lesson(db, course.id, lesson_spec)
            marker = "created" if created else "exists"
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5} "
                  f"[{marker}] {lesson_spec['title']!r}")
            if created:
                created_count += 1

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would create {created_count}/{len(lessons_spec)} new lesson(s).")
        else:
            await db.commit()
            print(f"\nCreated {created_count}/{len(lessons_spec)} new lesson(s) "
                  f"for course id={course.id}.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
