"""One-off: write hand-authored RU translations for the 34 lessons whose
text_content was never translated (courses 67/68/69/70), produced by
translation subagents as plain text files. Writes into translation_cache
under entity_type='lesson', field_name='text_content' — same convention as
write_ru_translations.py (provider='manual', no AI call).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402

LANG = "ru"
SCRATCH = Path("/tmp/claude-1000/-home-rimefara/8737316e-ed9e-4fd7-845d-e235ba0ed8c2/scratchpad/text_content")

LESSON_IDS = list(range(541, 575))  # 541..574 inclusive


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
    written = 0
    missing = []
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(Lesson).where(Lesson.id.in_(LESSON_IDS)))).scalars().all()
        by_id = {l.id: l for l in rows}

        for lid in LESSON_IDS:
            ru_path = SCRATCH / f"lesson_{lid}_ru.txt"
            if not ru_path.exists():
                missing.append(lid)
                continue
            translated = ru_path.read_text(encoding="utf-8").strip()
            if not translated:
                missing.append(lid)
                continue
            lesson = by_id[lid]
            if not lesson.text_content or not lesson.text_content.strip():
                continue
            await _write(db, "lesson", lid, "text_content", lesson.text_content, translated)
            written += 1
        await db.commit()

    print(f"wrote {written} translation_cache rows; missing/empty ids: {missing}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
