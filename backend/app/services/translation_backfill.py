"""Course title/description RU-translation backfill.

Extracted out of app/main.py's `lifespan()` — it used to run this loop
(translating every active course's title/description not yet in
translation_cache) synchronously BEFORE the server started accepting any
requests, which meant an OpenAI outage, a missing OPENAI_API_KEY, or just
a slow API response delayed the entire app's startup — a course-translation
backfill should never be able to block the whole platform from booting.

Now scheduled via app.scheduler (once shortly after startup, then daily) —
see start_scheduler(). translation_store.load(db) (the actual request-time
cache) stays in lifespan(): that one is a local-DB-only read, fast, and the
app genuinely needs it warm before serving translated content.
"""
from __future__ import annotations

import hashlib
import logging

from sqlalchemy import text as sa_text

from app.db.database import AsyncSessionLocal
from app.services import translation_store as ts
from app.services.grok_service import translate_text_with_ai

logger = logging.getLogger(__name__)


async def backfill_course_translations() -> None:
    """Translate every active course's title/description into RU if not
    already cached. Best-effort per course/field — one failure (rate limit,
    missing key, malformed response) must never abort the rest of the
    batch, matching the original lifespan block's swallow-and-continue
    behavior."""
    try:
        async with AsyncSessionLocal() as db:
            rows = (await db.execute(sa_text(
                "SELECT id, title, description FROM courses WHERE is_active=true"
            ))).all()
            upsert_sql = sa_text("""
                INSERT INTO translation_cache
                  (entity_type, entity_id, lang, field_name, source_text_hash,
                   translated_text, provider, created_at, updated_at)
                VALUES (:et, :eid, 'ru', :fn, :h, :tr, 'openai', NOW(), NOW())
                ON CONFLICT (entity_type, entity_id, lang, field_name) DO UPDATE
                  SET translated_text=EXCLUDED.translated_text, updated_at=NOW()
            """)
            translated_count = 0
            for course_id, title, description in rows:
                for field_name, src in (("title", title), ("description", description)):
                    if not src or not src.strip():
                        continue
                    if ts.get("course", course_id, "ru", field_name):
                        continue  # already in store
                    try:
                        tr = await translate_text_with_ai(src, source_lang="uz", target_lang="ru")
                        if tr and tr.strip():
                            h = hashlib.sha256(src.strip().encode()).hexdigest()
                            await db.execute(upsert_sql, {
                                "et": "course", "eid": course_id, "fn": field_name,
                                "h": h, "tr": tr,
                            })
                            ts.put("course", course_id, "ru", field_name, tr)
                            translated_count += 1
                    except Exception as e:  # noqa: BLE001 — one bad course/field must not abort the batch
                        logger.warning("Course %s field '%s' RU translation failed: %s", course_id, field_name, e)
            await db.commit()
            if translated_count:
                logger.info("Course translation backfill: %d field(s) newly translated", translated_count)
    except Exception as e:  # noqa: BLE001 — a scheduled job failing must not crash the scheduler
        logger.warning("Course translation backfill failed (non-fatal): %s", e)
