"""One-off: write hand-authored RU translations for lesson_samples
(title/description) produced by translation subagents, into
translation_cache under entity_type='lesson_sample'. Matches the
write_ru_translations.py convention — provider='manual', no AI call.

Reads the merged batch output files (lsbatch_{1,2,3}_ru.json), each an
array of {"id": <lesson_sample.id>, "title_ru": str, "description_ru": str|null},
cross-referenced against the source batch files (lsbatch_{1,2,3}.json) for
the original Uzbek text (needed to compute source_hash).
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
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402

LANG = "ru"
SCRATCH = Path("/tmp/claude-1000/-home-rimefara/8737316e-ed9e-4fd7-845d-e235ba0ed8c2/scratchpad/batches")


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
        for i in (1, 2, 3):
            src = json.load(open(SCRATCH / f"lsbatch_{i}.json", encoding="utf-8"))
            ru = json.load(open(SCRATCH / f"lsbatch_{i}_ru.json", encoding="utf-8"))
            src_by_id = {r["id"]: r for r in src}
            ru_by_id = {r["id"]: r for r in ru}

            for sid, srow in src_by_id.items():
                rrow = ru_by_id.get(sid)
                if not rrow:
                    missing.append(sid)
                    continue
                title_ru = (rrow.get("title_ru") or "").strip()
                if title_ru:
                    await _write(db, "lesson_sample", sid, "title", srow["title"], title_ru)
                    written += 1
                desc_src = srow.get("description")
                desc_ru = (rrow.get("description_ru") or "").strip() if rrow.get("description_ru") else ""
                if desc_src and desc_src.strip() and desc_ru:
                    await _write(db, "lesson_sample", sid, "description", desc_src, desc_ru)
                    written += 1
        await db.commit()

    print(f"wrote {written} translation_cache rows; missing ids: {missing}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
