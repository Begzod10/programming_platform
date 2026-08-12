"""Run the full course-building pipeline for one spec module, in the
correct order, in a single process. Equivalent to running create_course.py,
create_lessons.py, create_exercises.py, translate_lessons_ru.py,
translate_exercises_ru.py, create_samples.py, set_submission_tasks.py, then
check_exercise_integrity.py + check_ru_coverage.py + check_course_images.py
— but each of those remains independently runnable if you only need to
redo one piece (e.g. re-translate after editing spec content).

Usage:
    cd backend
    python scripts/build_course.py course_specs/my_course.py
    # add --dry-run to create/translate nothing, just validate the spec shape

Does NOT publish the course — is_published stays whatever COURSE says
(default False). A human should review before flipping it.
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
from course_builder.db_helpers import (  # noqa: E402
    get_or_create_course, get_or_create_lesson, sync_lesson_exercises,
    sync_lesson_sample, apply_submission_task,
)
from course_builder.translations import (  # noqa: E402
    translate_course_from_spec, translate_lesson_from_spec, translate_exercises_from_spec,
)
from check_exercise_integrity import check_course as check_exercises  # noqa: E402
from check_ru_coverage import check_course as check_ru  # noqa: E402
from check_diagram_coverage import diagram_coverage  # noqa: E402


async def main(spec_path: str, dry_run: bool) -> int:
    module = load_spec(spec_path)
    course_spec = require(module, "COURSE")
    lessons_spec = require(module, "LESSONS")

    async with AsyncSessionLocal() as db:
        course, created = await get_or_create_course(db, course_spec)
        course_ru_count = await translate_course_from_spec(db, course, course_spec)
        print(f"{'Created' if created else 'Reusing'} course id={course.id} {course.title!r} "
              f"(RU fields: {course_ru_count})")

        for lesson_spec in lessons_spec:
            lesson, l_created = await get_or_create_lesson(db, course.id, lesson_spec)
            tag = "created" if l_created else "exists"
            print(f"  lesson order={lesson_spec['order']:>2} id={lesson.id:>5} [{tag}] {lesson.title!r}")

            exercise_specs = lesson_spec.get("exercises") or []
            if exercise_specs:
                rows = await sync_lesson_exercises(db, lesson, exercise_specs)
                print(f"    exercises: {len(rows)}")
                ru_count = await translate_exercises_from_spec(db, rows, exercise_specs)
                print(f"    exercises translated: {ru_count}")

            # Must run BEFORE translate_lesson_from_spec — that function reads
            # lesson.task_title/task_description off the ORM object to build
            # section_translations, so the task fields have to already be set.
            task_spec = lesson_spec.get("task")
            if task_spec:
                await apply_submission_task(db, lesson, task_spec)
                print(f"    task: {task_spec.get('task_title')!r}")

            lesson_ru_count = await translate_lesson_from_spec(db, lesson, lesson_spec)
            print(f"    lesson RU strings: {lesson_ru_count}")

            sample_spec = lesson_spec.get("sample")
            if sample_spec:
                await sync_lesson_sample(db, lesson.id, sample_spec)
                print(f"    sample: {sample_spec['title']!r}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
            await engine.dispose()
            return 0

        await db.commit()
        print(f"\nCommitted. Running verification checks for course id={course.id}...")

    async with AsyncSessionLocal() as db:
        integrity_problems = await check_exercises(db, course.id)
        ru_problems = await check_ru(db, course.id)

    ok = True
    if integrity_problems:
        ok = False
        print(f"\n=== check_exercise_integrity: {len(integrity_problems)} problem(s) ===")
        for p in integrity_problems:
            print(p)
    else:
        print("check_exercise_integrity: OK")

    if ru_problems:
        ok = False
        print(f"\n=== check_ru_coverage: {len(ru_problems)} problem(s) ===")
        for p in ru_problems:
            print(p)
    else:
        print("check_ru_coverage: OK")

    async with AsyncSessionLocal() as db:
        print(f"\n{await diagram_coverage(db, course.id)}")
        print("(informational only — see course_builder/__init__.py 'Diagrams (Mermaid)')")

    print(f"\nDon't forget: python scripts/check_course_images.py {course.id}")
    print(f"Course is_published={course.is_published} — flip explicitly when reviewed.")

    await engine.dispose()
    return 0 if ok else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
