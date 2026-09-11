"""Fix a real bug hit while verifying the matching-exercise pilot:

lessons.py's GET /courses/{c}/lessons endpoint, when lang != 'uz', replaces
dto.sections_json WHOLESALE with the cached lesson-level RU translation
(translation_cache entity_type='lesson', field_name='sections_json') BEFORE
_hydrate_exercise_sections runs. That cached blob was written by
translate_lesson() back when the course was originally authored/translated
— long before attach_matching_to_sections.py appended a new exercise stub
to the LIVE `lessons.sections_json` column. Result: any Russian-language
student never sees a newly-added exercise at all (confirmed: UZ list has 9
exercises for lesson 224, RU list has 8 — the new matching exercise is
silently absent), even though the underlying Exercise row and its own
translation_cache entries are fully present and correct.

Fix: mirror the exact same stub-append performed on the live column into
the cached RU sections_json blob, for each of the 14 pilot lessons. The
stub carries no translatable text itself (hydration fills content in later
from the per-exercise translation_cache rows already written by
add_matching_pilot.py), so no re-translation is needed — only structural
sync.
"""
from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

NEW_EXERCISE_BY_LESSON = {
    218: 7438, 219: 7439, 220: 7440, 221: 7441, 222: 7442, 223: 7443,
    224: 7444, 225: 7445, 226: 7446, 227: 7447, 228: 7448, 229: 7449,
    230: 7450, 231: 7451,
}


async def main():
    async with AsyncSessionLocal() as db:
        lessons = (
            await db.execute(select(Lesson).where(Lesson.id.in_(NEW_EXERCISE_BY_LESSON.keys())))
        ).scalars().all()
        lesson_by_id = {l.id: l for l in lessons}

        rows = (
            await db.execute(
                select(TranslationCache).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.entity_id.in_(NEW_EXERCISE_BY_LESSON.keys()),
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                )
            )
        ).scalars().all()
        assert len(rows) == 14, f"expected 14 cached RU sections_json rows, found {len(rows)}"

        for row in rows:
            lesson_id = row.entity_id
            ex_id = NEW_EXERCISE_BY_LESSON[lesson_id]
            ru_sections = json.loads(row.translated_text)
            ex_sections = [s for s in ru_sections if s.get("type") == "exercise"]
            assert len(ex_sections) == 1, f"lesson {lesson_id}: expected 1 exercise section in RU cache"
            sec = ex_sections[0]
            existing_ids = {e.get("id") for e in sec.get("exercises", [])}
            if ex_id in existing_ids:
                print(f"lesson {lesson_id}: RU cache already has {ex_id}, skipping")
                continue
            sec.setdefault("exercises", []).append({"id": ex_id})

            # keep the cached hash pinned to the CURRENT live raw column, so
            # a future currency check (if one is ever added) stays honest
            live_lesson = lesson_by_id[lesson_id]
            from app.services.translation_service import _hash_source
            row.source_text_hash = _hash_source(live_lesson.sections_json)
            row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
            print(f"lesson {lesson_id}: appended stub {ex_id} to cached RU sections_json "
                  f"(section now has {len(sec['exercises'])} exercises)")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
