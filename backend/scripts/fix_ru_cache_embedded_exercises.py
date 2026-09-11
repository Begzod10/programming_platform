"""Fix a duplication bug introduced by fix_orphaned_exercises.py's RU-cache
step, discovered auditing lesson 544: some lessons' cached RU sections_json
still held OLD fully-embedded exercise objects (full title/description/
options inline, no "id" key — the pre-id-stub authoring style, apparently
from before this lesson range's exercises were rewritten to the current
stub+hydrate pattern on 2026-08-20). The live column was ALREADY
consistently id-stub-only everywhere (verified: 0 lessons with embedded
entries live, platform-wide) — but audit_lesson_exercises.py's
"referenced ids" computation only recognized `{"id": N}` entries, so it
never saw those embedded ones as representing 6830-6835 etc., and
fix_orphaned_exercises.py's RU-mirror step APPENDED fresh id-stubs for them
on top of the pre-existing embedded copies instead of replacing — result:
13 total exercise entries in the RU cache where only 7 should exist
(6 old-embedded + 7 id-stub, one of the 7 legitimately new — the
matching-exercise rollout's own addition).

Fix: for every lesson whose cached RU sections_json exercise section has
ANY non-id (embedded) entry, replace that section's whole "exercises" list
with fresh {"id": N} stubs mirroring the LIVE column's list exactly (same
ids, same order) — matching the pattern every lesson already uses live.
Hydration fills in translated content per-id from each exercise's own
translation_cache rows afterward, same as every stub already relies on.
"""
from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402


async def main():
    async with AsyncSessionLocal() as db:
        ru_rows = (
            await db.execute(
                select(TranslationCache).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                )
            )
        ).scalars().all()

        lessons = (
            await db.execute(select(Lesson).where(Lesson.id.in_([r.entity_id for r in ru_rows])))
        ).scalars().all()
        lesson_by_id = {l.id: l for l in lessons}

        fixed = 0
        for row in ru_rows:
            lesson = lesson_by_id.get(row.entity_id)
            if lesson is None or not lesson.sections_json:
                continue
            try:
                live_sections = json.loads(lesson.sections_json)
            except Exception:
                continue
            live_ex_sections = [s for s in live_sections if s.get("type") == "exercise"]
            if len(live_ex_sections) != 1:
                continue
            live_ids = [e.get("id") for e in live_ex_sections[0].get("exercises", []) if e.get("id") is not None]

            try:
                ru_sections = json.loads(row.translated_text)
            except Exception:
                continue
            ru_ex_sections = [s for s in ru_sections if s.get("type") == "exercise"]
            if len(ru_ex_sections) != 1:
                continue
            ru_sec = ru_ex_sections[0]
            has_embedded = any("id" not in e for e in ru_sec.get("exercises", []))
            if not has_embedded:
                continue

            ru_sec["exercises"] = [{"id": i} for i in live_ids]
            row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
            row.source_text_hash = _hash_source(lesson.sections_json)
            fixed += 1
            print(f"lesson {lesson.id}: replaced RU cache's exercise list with id-stubs {live_ids} (was mixed embedded+stub)")

        await db.commit()
        print(f"\nDONE. {fixed} lessons' RU cache exercise sections normalized to id-stubs.")


if __name__ == "__main__":
    asyncio.run(main())
