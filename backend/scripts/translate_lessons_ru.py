"""Write RU translations for every lesson's own content (title,
text_content, the fixed section labels, and the code/text/video strings
inside sections_json) from a spec module's per-lesson _ru fields.

Does NOT translate exercises — see translate_exercises_ru.py for that.
Exercises are stored in sections_json as bare {"id": N} stubs (see
course_builder/db_helpers.py::build_sections_json), not full embeds, so
they contribute zero translatable strings here; the actual student-facing
translation for them happens at request time in
app/api/v1/endpoints/lesson_helpers.py::_hydrate_exercise_sections, which
looks up entity_type='exercise' translation_cache rows directly.

MUST run AFTER set_submission_tasks.py if the lesson has a "task" —
translate_lesson_from_spec() reads lesson.task_title/task_description off
the ORM row to build its section_translations map (the project section
inside sections_json embeds those same strings a second time), so running
this first means the task fields are still None/stale and get silently
skipped.

Usage:
    cd backend
    python scripts/translate_lessons_ru.py course_specs/my_course.py

Requires lessons to already exist. Run check_ru_coverage.py <course_id>
after this AND translate_exercises_ru.py to confirm full coverage.
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
from course_builder.translations import translate_lesson_from_spec  # noqa: E402


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

        total_strings = 0
        for lesson_spec in lessons_spec:
            lesson = (
                await db.execute(
                    select(Lesson).where(Lesson.course_id == course.id, Lesson.order == lesson_spec["order"])
                )
            ).scalar_one_or_none()
            if not lesson:
                print(f"  lesson order={lesson_spec['order']}: not found — run create_lessons.py first, skipping")
                continue
            count = await translate_lesson_from_spec(db, lesson, lesson_spec)
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5}: "
                  f"{count} string(s) written{' (no RU content in spec)' if count == 0 else ''}")
            total_strings += count

        await db.commit()
        print(f"\nWrote {total_strings} RU string(s) across the course (id={course.id}).")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(sys.argv[1])))
