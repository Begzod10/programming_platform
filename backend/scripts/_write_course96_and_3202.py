"""One-off: write hand-authored RU translations for course 96's 21
exercises (options/drag_items+correct_order) and fix exercise 3202's
correct_answers gap. Uses the same write path as write_ru_translations.py
(translation_cache, provider='manual') — no AI call involved.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402

LANG = "ru"


async def _write(db, entity_type, entity_id, field_name, source_text, translated_text):
    source_hash = _hash_source(source_text or "")
    existing = (
        await db.execute(select(TranslationCache).where(
            TranslationCache.entity_type == entity_type,
            TranslationCache.entity_id == entity_id,
            TranslationCache.lang == LANG,
            TranslationCache.field_name == field_name,
        ))
    ).scalar_one_or_none()
    if existing is not None:
        existing.source_text_hash = source_hash
        existing.translated_text = translated_text
    else:
        db.add(TranslationCache(
            entity_type=entity_type, entity_id=entity_id, lang=LANG,
            field_name=field_name, source_text_hash=source_hash,
            translated_text=translated_text, provider="manual",
        ))


async def main():
    with open(
        "/tmp/claude-1000/-home-rimefara/8737316e-ed9e-4fd7-845d-e235ba0ed8c2/scratchpad/course96_ru.json",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    ex_ids = [int(k) for k in data.keys()] + [3202]
    written = 0
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(Exercise).where(Exercise.id.in_(ex_ids)))).scalars().all()
        by_id = {e.id: e for e in rows}

        for id_str, fields in data.items():
            ex_id = int(id_str)
            ex = by_id[ex_id]
            if "options" in fields:
                source = ex.options
                translated = json.dumps(fields["options"], ensure_ascii=False)
                await _write(db, "exercise", ex_id, "options", source, translated)
                written += 1
            if "drag_items" in fields:
                source_items = ex.drag_items
                translated_items = json.dumps(fields["drag_items"], ensure_ascii=False)
                await _write(db, "exercise", ex_id, "drag_items", source_items, translated_items)
                written += 1
                # This course stores correct_order == drag_items verbatim
                # (verified against the DB before writing this script) —
                # so the same translated list is the correct translation
                # for correct_order too, not a re-typed guess.
                source_order = ex.correct_order
                if source_order and json.loads(source_order) == json.loads(source_items):
                    await _write(db, "exercise", ex_id, "correct_order", source_order, translated_items)
                    written += 1
                else:
                    print(f"WARNING: exercise {ex_id} correct_order != drag_items, skipped auto-map")

        # Exercise 3202 correct_answers fix
        ex3202 = by_id[3202]
        assert ex3202.correct_answers == "butun,ro'yxat", ex3202.correct_answers
        await _write(db, "exercise", 3202, "correct_answers", ex3202.correct_answers, "целиком,список")
        written += 1

        await db.commit()

    print(f"wrote {written} translation_cache rows")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
