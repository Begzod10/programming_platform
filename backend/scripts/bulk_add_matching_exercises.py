"""Platform-wide rollout of the `matching` exercise (see the course-30
pilot: scripts/add_matching_pilot.py + scripts/attach_matching_to_sections.py,
which this generalizes and merges into one script) to every remaining lesson
outside course_id=30.

Reads /home/student_platform/backend/scripts/all_matching_content.json —
{lesson_id: {topic, topic_ru, terms, terms_ru, defs, defs_ru}, ...}, one
entry per lesson, authored from each lesson's own theory/task content — and
for every lesson_id present:
  1. creates one new `Exercise` row (exercise_type="matching", additive —
     never touches any existing exercise), matching the pilot's exact shape
     (title/description/hint template, drag_items=terms, options=defs,
     difficulty_level="Medium", points=4, order = current max+1)
  2. writes its RU translation via the translation_cache (write_ru_translations
     .translate_exercises' underlying `_write` helper) so RU-locale students
     see a translated version
  3. appends a stub {"id": <new_exercise_id>} into the lesson's sections_json
     exercise section's `exercises` array — REQUIRED, not optional: see
     attach_matching_to_sections.py's docstring — StudentCourses.js's
     apiToLesson() renders straight from sections_json when it has an
     exercise section, so a bare exercises-table row is otherwise invisible
     to students no matter what.

Idempotent per lesson: skips any lesson_id that already has an
exercise_type="matching" row (so a partial/interrupted run can be re-run
safely). Commits in batches of BATCH_SIZE lessons so a mid-run failure
doesn't lose all prior work and so progress is visible.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select, func  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from scripts.write_ru_translations import _write  # noqa: E402

CONTENT_FILE = Path("/home/student_platform/backend/scripts/all_matching_content.json")
BATCH_SIZE = 40


async def main():
    content = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    lesson_ids = [int(k) for k in content.keys()]
    print(f"loaded {len(lesson_ids)} lesson entries from {CONTENT_FILE}")

    created = 0
    skipped_existing = 0
    errors = []

    async with AsyncSessionLocal() as db:
        # Lessons + their existing matching exercises, to make re-runs idempotent.
        lessons = (
            await db.execute(select(Lesson).where(Lesson.id.in_(lesson_ids)))
        ).scalars().all()
        lessons_by_id = {l.id: l for l in lessons}
        missing_lessons = set(lesson_ids) - set(lessons_by_id.keys())
        if missing_lessons:
            print(f"WARNING: {len(missing_lessons)} lesson_ids in content file not found in DB: "
                  f"{sorted(missing_lessons)[:20]}{'...' if len(missing_lessons) > 20 else ''}")

        existing_matching = (
            await db.execute(
                select(Exercise.lesson_id).where(
                    Exercise.lesson_id.in_(lesson_ids), Exercise.exercise_type == "matching"
                )
            )
        ).scalars().all()
        already_done = set(existing_matching)

        batch_count = 0
        for lesson_id in lesson_ids:
            if lesson_id not in lessons_by_id:
                continue
            if lesson_id in already_done:
                skipped_existing += 1
                continue

            lesson = lessons_by_id[lesson_id]
            c = content[str(lesson_id)]

            try:
                if not lesson.sections_json:
                    raise RuntimeError("lesson has no sections_json")
                sections = json.loads(lesson.sections_json)
                ex_sections = [s for s in sections if s.get("type") == "exercise"]
                if len(ex_sections) != 1:
                    raise RuntimeError(f"expected exactly 1 exercise section, found {len(ex_sections)}")
                sec = ex_sections[0]

                max_order = (
                    await db.execute(
                        select(func.max(Exercise.order)).where(Exercise.lesson_id == lesson_id)
                    )
                ).scalar()
                next_order = (max_order or 0) + 1

                title = f"\U0001f517 Juftlikni top: {c['topic']}"
                description = "Chap tarafdagi atamalarni o'ng tarafdagi ta'riflari bilan moslashtiring."
                hint = "Har bir so'zni dars matnida qanday ishlatilganini eslang."

                ex = Exercise(
                    lesson_id=lesson_id,
                    title=title,
                    description=description,
                    exercise_type="matching",
                    drag_items=json.dumps(c["terms"], ensure_ascii=False),
                    options=json.dumps(c["defs"], ensure_ascii=False),
                    hint=hint,
                    difficulty_level="Medium",
                    points=4,
                    order=next_order,
                )
                db.add(ex)
                await db.flush()

                title_ru = f"\U0001f517 Найди пару: {c['topic_ru']}"
                description_ru = "Сопоставьте термины слева с их определениями справа."
                hint_ru = "Вспомните, как каждое слово использовалось в тексте урока."
                drag_items_ru = json.dumps(c["terms_ru"], ensure_ascii=False)
                options_ru = json.dumps(c["defs_ru"], ensure_ascii=False)

                await _write(db, "exercise", ex.id, "title", title, title_ru)
                await _write(db, "exercise", ex.id, "description", description, description_ru)
                await _write(db, "exercise", ex.id, "hint", hint, hint_ru)
                await _write(db, "exercise", ex.id, "drag_items", ex.drag_items, drag_items_ru)
                await _write(db, "exercise", ex.id, "options", ex.options, options_ru)

                existing_ids = {e.get("id") for e in sec.get("exercises", [])}
                if ex.id not in existing_ids:
                    sec.setdefault("exercises", []).append({"id": ex.id})
                    lesson.sections_json = json.dumps(sections, ensure_ascii=False)

                created += 1
                batch_count += 1
            except Exception as e:  # noqa: BLE001
                errors.append((lesson_id, str(e)))
                continue

            if batch_count >= BATCH_SIZE:
                await db.commit()
                print(f"...committed batch, {created} created so far")
                batch_count = 0

        await db.commit()

    print(f"\nDONE. created={created} skipped_existing={skipped_existing} errors={len(errors)}")
    if errors:
        print("ERRORS:")
        for lid, msg in errors:
            print(f"  lesson {lid}: {msg}")


if __name__ == "__main__":
    asyncio.run(main())
