"""Platform-wide generalization of fix_ru_sections_cache.py (which fixed
this same bug for the 14-lesson course-30 pilot only).

Bug: GET /courses/{c}/lessons/{l}, when lang != 'uz', replaces
dto.sections_json WHOLESALE with the cached lesson-level RU translation
(translation_cache entity_type='lesson', field_name='sections_json',
written back when the course was originally authored/translated) BEFORE
_hydrate_exercise_sections runs. bulk_add_matching_exercises.py appended a
new exercise stub to the LIVE lessons.sections_json column for every
lesson, but never touched this separate cached blob — so any lesson that
already had a cached RU sections_json translation now silently hides its
new matching exercise from Russian-language students (Uzbek is unaffected:
lang == 'uz' never takes this cached-override branch).

Fix: for every lesson that has BOTH (a) a newly-created matching Exercise
and (b) an existing cached RU sections_json translation row, append the
same {"id": <exercise_id>} stub into the cached blob's exercise section —
mirroring exactly what was already done to the live column. No new
translation work needed: the stub carries no text itself, hydration fills
it in later from the exercise's own translation_cache rows.
"""
from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402


async def main():
    async with AsyncSessionLocal() as db:
        # Every lesson's new matching exercise id (all of them, platform-wide).
        rows = (
            await db.execute(select(Exercise.lesson_id, Exercise.id).where(Exercise.exercise_type == "matching"))
        ).all()
        new_ex_by_lesson = {lesson_id: ex_id for lesson_id, ex_id in rows}
        print(f"{len(new_ex_by_lesson)} lessons have a matching exercise")

        cache_rows = (
            await db.execute(
                select(TranslationCache).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                    TranslationCache.entity_id.in_(new_ex_by_lesson.keys()),
                )
            )
        ).scalars().all()
        print(f"{len(cache_rows)} of those have a cached RU sections_json translation to fix")

        lessons = (
            await db.execute(select(Lesson).where(Lesson.id.in_([r.entity_id for r in cache_rows])))
        ).scalars().all()
        lesson_by_id = {l.id: l for l in lessons}

        fixed = 0
        already_ok = 0
        skipped_no_ex_section = 0

        for row in cache_rows:
            lesson_id = row.entity_id
            ex_id = new_ex_by_lesson[lesson_id]
            ru_sections = json.loads(row.translated_text)
            ex_sections = [s for s in ru_sections if s.get("type") == "exercise"]
            if len(ex_sections) != 1:
                # Same as lesson 604 on the live column: no exercise section
                # in the cached blob either (project-only capstone lesson) —
                # nothing to append here, the frontend's live-fetch fallback
                # (see bulk_add_matching_exercises.py's lesson-604 handling)
                # covers it regardless of language.
                skipped_no_ex_section += 1
                continue
            sec = ex_sections[0]
            existing_ids = {e.get("id") for e in sec.get("exercises", [])}
            if ex_id in existing_ids:
                already_ok += 1
                continue
            sec.setdefault("exercises", []).append({"id": ex_id})

            live_lesson = lesson_by_id[lesson_id]
            row.source_text_hash = _hash_source(live_lesson.sections_json)
            row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
            fixed += 1

        await db.commit()
        print(f"\nDONE. fixed={fixed} already_ok={already_ok} skipped_no_ex_section={skipped_no_ex_section}")


if __name__ == "__main__":
    asyncio.run(main())
