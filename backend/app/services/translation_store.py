"""In-memory translation store.

Loaded once at startup from translation_cache. All route handlers look up
translations here — zero DB round-trips per request.

Usage:
    from app.services import translation_store as ts

    tr = ts.get("lesson", lesson_id, "ru", "title")   # str | None
    if tr:
        dto.title = tr
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# (entity_type, entity_id, lang, field_name) -> translated_text
_store: dict[tuple[str, int, str, str], str] = {}


async def load(db: AsyncSession) -> None:
    rows = (await db.execute(text(
        "SELECT entity_type, entity_id, lang, field_name, translated_text FROM translation_cache"
    ))).all()
    _store.clear()
    for entity_type, entity_id, lang, field_name, translated_text in rows:
        if translated_text:
            _store[(entity_type, entity_id, lang, field_name)] = translated_text
    logger.info("Translation store: %d entries loaded", len(_store))


def get(entity_type: str, entity_id: int, lang: str, field_name: str) -> Optional[str]:
    return _store.get((entity_type, entity_id, lang, field_name))


def put(entity_type: str, entity_id: int, lang: str, field_name: str, value: str) -> None:
    """Add a single entry (used when translating courses at startup)."""
    if value:
        _store[(entity_type, entity_id, lang, field_name)] = value
