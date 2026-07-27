"""Set (UPDATE) the task_* fields on every lesson in a spec module that
defines a "task" — these are NOT a separate table, just columns on the
Lesson row itself, so this is an update pass, not a create step. Must run
after create_lessons.py (the lesson row must already exist) and after
create_exercises.py (rebuilds sections_json's project section alongside
the existing exercise section, so exercises should already be there).

Usage:
    cd backend
    python scripts/set_submission_tasks.py course_specs/my_course.py
    # add --dry-run to preview without writing
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
from course_builder.db_helpers import apply_submission_task  # noqa: E402


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

        updated = 0
        for lesson_spec in lessons_spec:
            task_spec = lesson_spec.get("task")
            if not task_spec:
                continue
            lesson = (
                await db.execute(
                    select(Lesson).where(Lesson.course_id == course.id, Lesson.order == lesson_spec["order"])
                )
            ).scalar_one_or_none()
            if not lesson:
                print(f"  lesson order={lesson_spec['order']}: not found — run create_lessons.py first, skipping")
                continue
            did_set = await apply_submission_task(db, lesson, task_spec)
            if did_set:
                print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5}: "
                      f"task {task_spec.get('task_title')!r}")
                updated += 1

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would set task fields on {updated} lesson(s).")
        else:
            await db.commit()
            print(f"\nSet task fields on {updated} lesson(s) for course id={course.id}.")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
