"""
translation_service — on-demand lesson/course/exercise translation.

Endpoints don't talk to Groq directly; they ask this module for the field
they want in the target language. Cache hit → instant. Cache miss → AI
call, save row, return.

Entry points:
    await translate_fields(db, entity_type, entity_id, lang, fields_dict,
                           source_lang)
        → dict of translated strings (same keys as input)

    await translate_json_blob(db, entity_type, entity_id, lang,
                              source_text, source_lang,
                              field_name="sections_json")
        → translated JSON-as-string, suitable to feed back into the FE

Both functions short-circuit when source_lang == lang.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.translation_cache import TranslationCache
from app.services.grok_service import translate_text_with_ai

logger = logging.getLogger(__name__)

SUPPORTED_LANGS = ("uz", "ru")
DEFAULT_SOURCE_LANG = "uz"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _hash_source(text: str) -> str:
    """SHA-256 of the source string — lets a read path drop stale rows."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _should_skip(text: Optional[str]) -> bool:
    """True if there's nothing to translate (empty, whitespace, or single
    short token like a number or URL)."""
    if text is None:
        return True
    s = text.strip()
    if not s:
        return True
    # URLs / image paths — no human language to translate
    if s.startswith(("http://", "https://", "/")) and " " not in s:
        return True
    return False


async def _read_cached(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    lang: str,
    field_name: str,
    source_hash: str,
) -> Optional[str]:
    row = (
        await db.execute(
            select(TranslationCache).where(
                TranslationCache.entity_type == entity_type,
                TranslationCache.entity_id == entity_id,
                TranslationCache.lang == lang,
                TranslationCache.field_name == field_name,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    # Source changed since this row was cached — caller falls back to a
    # fresh translation. The stale row will be overwritten on commit.
    if row.source_text_hash != source_hash:
        return None
    return row.translated_text


async def _write_cached(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    lang: str,
    field_name: str,
    source_hash: str,
    translated_text: str,
) -> None:
    existing = (
        await db.execute(
            select(TranslationCache).where(
                TranslationCache.entity_type == entity_type,
                TranslationCache.entity_id == entity_id,
                TranslationCache.lang == lang,
                TranslationCache.field_name == field_name,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        existing.source_text_hash = source_hash
        existing.translated_text = translated_text
    else:
        db.add(TranslationCache(
            entity_type=entity_type,
            entity_id=entity_id,
            lang=lang,
            field_name=field_name,
            source_text_hash=source_hash,
            translated_text=translated_text,
            provider="groq",
        ))


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

async def translate_fields(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: int,
    target_lang: str,
    fields: dict[str, Optional[str]],
    source_lang: str,
) -> dict[str, Optional[str]]:
    """Bulk-translate a dict of fields for one entity.

    Returns a dict with the same keys as `fields`. Values are either the
    translation or, when translation fails or is unnecessary, the source
    string itself. Cache misses are issued in parallel — for a lesson with
    title + text_content + 4 task_* fields, that's one round-trip not six.
    """
    if target_lang == source_lang:
        return fields
    if target_lang not in SUPPORTED_LANGS or source_lang not in SUPPORTED_LANGS:
        return fields

    out: dict[str, Optional[str]] = {}
    misses: list[tuple[str, str, str]] = []  # (field_name, source, source_hash)

    for field_name, source in fields.items():
        if _should_skip(source):
            out[field_name] = source
            continue
        source_hash = _hash_source(source)
        cached = await _read_cached(
            db, entity_type, entity_id, target_lang, field_name, source_hash,
        )
        if cached is not None:
            out[field_name] = cached
        else:
            misses.append((field_name, source, source_hash))
            # Tentatively echo the source so callers always have a string —
            # we overwrite below if the AI call succeeds.
            out[field_name] = source

    if not misses:
        return out

    # Fire all misses in parallel — AI calls are I/O-bound so this is a
    # straight throughput win.
    async def _one(field_name: str, source: str) -> Optional[str]:
        try:
            return await translate_text_with_ai(
                source, source_lang=source_lang, target_lang=target_lang,
            )
        except Exception:
            logger.exception(
                "translate_fields: AI call failed for %s/%s/%s field=%s",
                entity_type, entity_id, target_lang, field_name,
            )
            return None

    results = await asyncio.gather(
        *[_one(name, src) for name, src, _ in misses],
        return_exceptions=False,
    )

    wrote_any = False
    for (field_name, source, source_hash), translated in zip(misses, results):
        if not translated:
            continue
        out[field_name] = translated
        await _write_cached(
            db, entity_type, entity_id, target_lang, field_name,
            source_hash, translated,
        )
        wrote_any = True

    if wrote_any:
        try:
            await db.commit()
        except Exception:
            # Don't let a cache-write failure surface as a 500. The
            # translation is already in `out`; next read will retry.
            await db.rollback()
            logger.exception(
                "translate_fields: cache commit failed for %s/%s/%s",
                entity_type, entity_id, target_lang,
            )

    return out


async def translate_json_blob(
    db: AsyncSession,
    *,
    entity_type: str,
    entity_id: int,
    target_lang: str,
    source_text: Optional[str],
    source_lang: str,
    field_name: str = "sections_json",
) -> Optional[str]:
    """Translate a JSON string (e.g. lesson.sections_json) wholesale.

    The model is told to preserve structure and only translate known
    natural-language keys. If the AI returns something that's not valid
    JSON the source is returned unchanged — better that than a parse error
    on the FE.
    """
    if _should_skip(source_text):
        return source_text
    if target_lang == source_lang:
        return source_text
    if target_lang not in SUPPORTED_LANGS or source_lang not in SUPPORTED_LANGS:
        return source_text

    source_hash = _hash_source(source_text or "")
    cached = await _read_cached(
        db, entity_type, entity_id, target_lang, field_name, source_hash,
    )
    if cached is not None:
        return cached

    try:
        translated = await translate_text_with_ai(
            source_text or "", source_lang=source_lang,
            target_lang=target_lang, is_json=True,
        )
    except Exception:
        logger.exception(
            "translate_json_blob: AI call failed for %s/%s/%s",
            entity_type, entity_id, target_lang,
        )
        return source_text

    if not translated:
        return source_text

    # Sanity-check it's still valid JSON — if not, fall back to source.
    import json
    try:
        json.loads(translated)
    except Exception:
        logger.warning(
            "translate_json_blob: AI returned non-JSON for %s/%s/%s",
            entity_type, entity_id, target_lang,
        )
        return source_text

    await _write_cached(
        db, entity_type, entity_id, target_lang, field_name,
        source_hash, translated,
    )
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception(
            "translate_json_blob: cache commit failed for %s/%s/%s",
            entity_type, entity_id, target_lang,
        )
    return translated
