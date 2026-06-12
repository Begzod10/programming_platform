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


# Keys whose values are natural-language strings the student reads.
# Anything outside this set stays untouched — id/type/url/code/etc.
# This list is derived from a census of every string key actually used
# in production sections_json blobs; if you add a new field on the
# teacher editor that holds prose, add it here too.
_TRANSLATABLE_KEYS = {
    # Lesson body / sections
    "html", "label", "text", "content", "title", "description",
    # Exercise prompt + author guidance
    "question", "prompt", "hint", "explanation",
    # Author's reference answer (shown to students after grading)
    "expected_answer",
    # Generic UI fields a future editor might add
    "answer", "correctAnswer", "feedback", "placeholder",
}

# Keys whose values are NEVER translated even if they happen to look
# like text. These are identifiers, code, taxonomy tags, or grading
# data the student is supposed to match verbatim.
_NEVER_TRANSLATE_KEYS = {
    # Identifiers and structural tags
    "type", "id", "url", "videoUrl", "imgUrl", "image", "src",
    # Code + programming language tag
    "code", "codeLanguage", "lang",
    # Files
    "fileName", "fileSize",
    # Styling
    "icon", "color", "bg", "fontFamily",
    # Exercise grading data (must match exactly)
    "correct_answers", "correct_order", "exercise_type", "difficulty_level",
    # Choice arrays stored as JSON strings; translating them would
    # break the matching logic on the frontend
    "options", "drag_items",
}


def _collect_translatable_strings(node, out: list[tuple[list, str]], path: list = None) -> None:
    """Walk a parsed JSON tree, collecting every string value under a
    translatable key. `out` accumulates (path, source_string) pairs so we
    can write the translation back to the exact spot it came from."""
    if path is None:
        path = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k in _NEVER_TRANSLATE_KEYS:
                continue
            child_path = path + [k]
            if k in _TRANSLATABLE_KEYS and isinstance(v, str) and v.strip():
                out.append((child_path, v))
            else:
                _collect_translatable_strings(v, out, child_path)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _collect_translatable_strings(item, out, path + [i])


def _set_at_path(tree, path: list, value) -> None:
    node = tree
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = value


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
    """Translate the natural-language strings inside a JSON document.

    The old version asked the model to round-trip the whole JSON, which
    was fragile — gpt-4.1 frequently emitted commentary, dropped keys,
    or escaped quotes incorrectly, and the json.loads() guard then made
    us throw the translation away and return source. Result: lesson
    bodies appeared untranslated and the cache was never written, so
    every render paid the AI cost again.

    The new approach:
      1. Parse the source as JSON locally.
      2. Walk the tree, collecting every string under a translatable key.
      3. Send just those strings (no structure) to translate_fields-style
         batched calls — small, fast, and the parser never gets involved.
      4. Stitch the translations back into the tree at their exact path.
      5. Re-serialize. Output is GUARANTEED to be valid JSON because we
         never let the model touch the structure.
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

    import json
    try:
        tree = json.loads(source_text or "null")
    except Exception:
        # Source isn't valid JSON — can't safely modify it.
        logger.warning(
            "translate_json_blob: source not valid JSON for %s/%s",
            entity_type, entity_id,
        )
        return source_text

    pairs: list[tuple[list, str]] = []
    _collect_translatable_strings(tree, pairs)
    if not pairs:
        # Nothing to translate — write the source as the "translation" so
        # we don't keep re-checking on every request.
        await _write_cached(
            db, entity_type, entity_id, target_lang, field_name,
            source_hash, source_text or "",
        )
        try: await db.commit()
        except Exception: await db.rollback()
        return source_text

    async def _translate_one(s: str) -> Optional[str]:
        try:
            from app.services.grok_service import translate_text_with_ai
            return await translate_text_with_ai(
                s, source_lang=source_lang, target_lang=target_lang,
            )
        except Exception:
            logger.exception(
                "translate_json_blob: per-string AI call failed for %s/%s",
                entity_type, entity_id,
            )
            return None

    results = await asyncio.gather(
        *[_translate_one(src) for _, src in pairs],
        return_exceptions=False,
    )

    # Apply translations back into the parsed tree at their original path.
    # Any string we couldn't translate stays in source language — partial
    # translation beats none.
    for (path, src), translated in zip(pairs, results):
        if translated and translated.strip() and translated.strip() != src.strip():
            _set_at_path(tree, path, translated)

    out = json.dumps(tree, ensure_ascii=False)

    await _write_cached(
        db, entity_type, entity_id, target_lang, field_name,
        source_hash, out,
    )
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception(
            "translate_json_blob: cache commit failed for %s/%s/%s",
            entity_type, entity_id, target_lang,
        )
    return out
