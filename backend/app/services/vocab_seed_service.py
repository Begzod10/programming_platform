"""Put a finished lesson's vocabulary into the student's own dictionary, so nobody has to add words by hand.

One dictionary row per (word, language): 'uz' carries the Uzbek definition, 'ru' the Russian one (skipped when the
lesson word has no Russian definition). The dictionary list is filtered by language, so a student only meets the
rows of the language they study in. A word the student already has in that language is left exactly as it is.

Best-effort by contract: this is called right after a LessonCompletion has been committed and must never break or
undo finishing the lesson — every failure is logged and reported as 0.
See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.4.
"""
from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dictionary import UserDictionary
from app.models.lesson import LessonVocabulary
from app.models.user import Student

logger = logging.getLogger(__name__)

DICT_WORD_LIMIT = 80      # user_dictionary.word is String(80); lesson_vocabulary.word allows 120


def _new_rows(student_id: int, lesson_id: int, vocab: list, existing: set) -> list[UserDictionary]:
    """Dictionary rows to insert. `existing` holds the (lowercased word, lang) pairs the student already has."""
    seen, rows = set(existing), []
    for v in vocab:
        word = (v.word or "").strip()[:DICT_WORD_LIMIT].strip()
        if not word:
            continue
        for lang, definition in (("uz", v.definition), ("ru", v.definition_ru)):
            definition = (definition or "").strip()
            key = (word.lower(), lang)
            if not definition or key in seen:
                continue
            seen.add(key)
            rows.append(UserDictionary(student_id=student_id, word=word, context=definition,
                                       lesson_id=lesson_id, lang=lang))
    return rows


async def seed_lesson_words(db: AsyncSession, student_id: int, lesson_id: int) -> int:
    """Add the lesson's words to the student's dictionary; returns how many rows were added. Never raises.

    Call it only after the caller's own work is committed: on success it commits, on failure it rolls back.
    """
    try:
        student = await db.get(Student, student_id)
        if student is None or student.is_demo:
            return 0
        vocab = list((await db.execute(
            select(LessonVocabulary).where(LessonVocabulary.lesson_id == lesson_id)
            .order_by(LessonVocabulary.order, LessonVocabulary.id))).scalars().all())
        if not vocab:
            return 0
        existing = {(w, lang) for w, lang in (await db.execute(
            select(func.lower(UserDictionary.word), UserDictionary.lang)
            .where(UserDictionary.student_id == student_id))).all()}
        rows = _new_rows(student_id, lesson_id, vocab, existing)
        if not rows:
            return 0
        async with db.begin_nested():
            db.add_all(rows)
        await db.commit()
        return len(rows)
    except Exception:  # noqa: BLE001 — seeding is purely additive; the lesson is already finished
        logger.exception("[vocab-seed] failed for student=%s lesson=%s", student_id, lesson_id)
        try:
            await db.rollback()
        except Exception:  # noqa: BLE001
            pass
        return 0
