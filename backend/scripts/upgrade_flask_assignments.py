"""Non-destructive upgrade: attach per-lesson assignments (task_*) to the
existing Python Flask course.

Reads LESSON_TASKS from seed_flask_course.py and applies the five task fields
(task_title, task_description, task_requirements, task_technologies,
task_deadline_days) to the matching lesson on the live DB, keyed by lesson
`order`.

Safety rules:
  - Only updates a field when it is currently NULL/empty on the DB row.
    Teacher edits in the admin UI are never overwritten.
  - Idempotent: a second run does nothing if all fields are already populated.

Usage:
    cd backend
    python scripts/upgrade_flask_assignments.py            # apply
    python scripts/upgrade_flask_assignments.py --dry-run  # preview only
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

from scripts.seed_flask_course import COURSE, LESSON_TASKS  # noqa: E402


_FIELDS = (
    ("task_title", "title"),
    ("task_description", "description"),
    ("task_requirements", "requirements"),
    ("task_technologies", "technologies"),
    ("task_deadline_days", "deadline_days"),
)


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


async def upgrade(dry_run: bool = False) -> None:
    updated_lessons = 0
    updated_fields_total = 0

    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if not course:
            print(f"Course '{COURSE['title']}' not found. "
                  "Run scripts/seed_flask_course.py first.")
            return

        print(f"Course: id={course.id}  title='{course.title}'")

        lessons = (
            await db.execute(
                select(Lesson)
                .where(Lesson.course_id == course.id)
                .order_by(Lesson.order)
            )
        ).scalars().all()
        print(f"Found {len(lessons)} lessons in DB.")

        for lesson in lessons:
            task = LESSON_TASKS.get(lesson.order)
            if not task:
                print(f"  order={lesson.order:>2}  no LESSON_TASKS entry — skip")
                continue

            changes: list[str] = []
            for col_attr, task_key in _FIELDS:
                current = getattr(lesson, col_attr)
                desired = task.get(task_key)
                if desired is None:
                    continue
                if _is_empty(current):
                    setattr(lesson, col_attr, desired)
                    changes.append(col_attr)

            if changes:
                updated_lessons += 1
                updated_fields_total += len(changes)
                print(f"  order={lesson.order:>2}  id={lesson.id:>3}  "
                      f"+{len(changes)} field(s): {', '.join(changes)}  "
                      f"  ({task['title']})")
            else:
                print(f"  order={lesson.order:>2}  id={lesson.id:>3}  "
                      f"already populated — skip")

        if dry_run:
            await db.rollback()
            print(f"\nDRY RUN — would update {updated_lessons} lesson(s), "
                  f"{updated_fields_total} field(s). Nothing written.")
        else:
            await db.commit()
            print(f"\nUpdated {updated_lessons} lesson(s), "
                  f"{updated_fields_total} field(s) total.")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(upgrade(dry_run=dry))
