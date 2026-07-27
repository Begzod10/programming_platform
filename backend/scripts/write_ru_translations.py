"""Write hand-authored Russian translations directly into translation_cache.

Used instead of bulk_translate.py (which calls OpenAI) when translations are
authored by hand. Matches the exact schema/hash convention the read path
(app/services/translation_store.py) expects, so there's no difference at
request time between this and an AI-generated cache row.

Each call site provides a dict of {field_name: {source_hash_input: translated}}
— see translate_lesson()/translate_exercise() below for the shape.

REQUIRED WORKFLOW when creating or enhancing ANY course — do not skip
translate_exercises():

  A platform-wide audit found 1,371 exercises across 21 courses where
  translate_lesson() had been called (lesson content was RU) but
  translate_exercises() had NOT been called for that lesson's exercises —
  students saw fully-Uzbek exercises under Russian UI chrome. This happened
  silently because nothing checked for the gap until a student hit it.

  For every lesson you seed or enhance:
    1. Call translate_lesson(db, lesson_id, ...) for the lesson's own fields.
    2. ALSO call translate_exercises(db, {exercise_id: {field: translated, ...}, ...})
       for every exercise attached to that lesson — title, description,
       hint (if non-empty), options (if the exercise has options),
       drag_items + correct_order (if drag_and_drop; correct_order must be
       built by index-mapping the ORIGINAL correct_order into the
       ORIGINAL drag_items, then reading the translated item at that same
       index — never re-typed by hand, or a RU student who drags the
       objectively correct order can be marked wrong).
    3. fill_in_blank/text_input correct_answers: translate it ONLY if the
       answer is genuine natural language (not a code/SQL/API token) — see
       exercise_service.py::check_answer_locally, which looks up a
       translation_store "correct_answers" entry before falling back to
       the raw column.
    4. After writing, run `python scripts/check_ru_coverage.py <course_id>`
       — it fails loudly and lists exactly what's missing. Treat a
       non-clean report as a bug, not a "TODO for later".

  DO NOT write to Exercise.title_ru / description_ru / hint_ru /
  explanation_ru / expected_answer_ru — those columns exist on the model
  but are NEVER read by any serving code (see the warning comment on the
  Exercise model). Only translation_cache rows (written via _write() below)
  are actually served to students.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import (  # noqa: E402
    _hash_source, _collect_translatable_strings, _set_at_path,
)

LANG = "ru"


async def _write(db, entity_type: str, entity_id: int, field_name: str,
                  source_text: str, translated_text: str) -> None:
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


async def translate_lesson(db, lesson_id: int, flat_fields: dict[str, str],
                            section_translations: dict[str, str]) -> None:
    """flat_fields: {field_name: translated_text} for title/text_content/etc.
    section_translations: {source_string: translated_string} covering every
    string _collect_translatable_strings finds in this lesson's sections_json.
    """
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

    for field_name, translated in flat_fields.items():
        source = getattr(lesson, field_name)
        if source and source.strip():
            await _write(db, "lesson", lesson_id, field_name, source, translated)

    if lesson.sections_json:
        tree = json.loads(lesson.sections_json)
        collected: list = []
        _collect_translatable_strings(tree, collected)
        missing = [s for _, s in collected if s not in section_translations]
        if missing:
            raise ValueError(
                f"lesson {lesson_id}: {len(missing)} strings have no translation "
                f"provided (first: {missing[0][:80]!r})"
            )
        translated_tree = json.loads(lesson.sections_json)
        for path, source in collected:
            _set_at_path(translated_tree, path, section_translations[source])
        translated_json = json.dumps(translated_tree, ensure_ascii=False)
        await _write(db, "lesson", lesson_id, "sections_json",
                     lesson.sections_json, translated_json)


async def translate_exercises(db, translations: dict[int, dict[str, str]]) -> None:
    """translations: {exercise_id: {field_name: translated_text}}"""
    ex_rows = (
        await db.execute(select(Exercise).where(Exercise.id.in_(translations.keys())))
    ).scalars().all()
    by_id = {e.id: e for e in ex_rows}
    for ex_id, fields in translations.items():
        ex = by_id[ex_id]
        for field_name, translated in fields.items():
            source = getattr(ex, field_name)
            if source and source.strip():
                await _write(db, "exercise", ex_id, field_name, source, translated)


async def run(fn) -> None:
    async with AsyncSessionLocal() as db:
        await fn(db)
        await db.commit()
