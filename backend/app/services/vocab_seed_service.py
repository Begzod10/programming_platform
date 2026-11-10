"""Put a finished lesson's vocabulary into the student's own dictionary, so nobody has to add words by hand.

ONE dictionary row per word, in the student's language: a Russian-language student gets lang='ru' rows carrying the
Russian definition (the Uzbek one where the lesson word has no Russian), everyone else lang='uz' rows. Never a second
row for a word the student already has in either language — two rows of one word are two separate review cards with
their own schedule, which makes a word come back in the other language right after it was learnt.

The language is the one the student last used the site in (students.ui_lang, remembered from their own requests);
failing that, the language most of their own dictionary is in; failing that, Uzbek.

Seeded rows are marked `seeded` so they do not count as words the student saved themselves (achievements).

Best-effort by contract: seed_lesson_words is called right after a LessonCompletion has been committed and must never
break or undo finishing the lesson. It works in a session of its own, so nothing it does — including a failure — can
touch the caller's session or the objects loaded in it.
See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.4.
"""
from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.models.dictionary import UserDictionary
from app.models.lesson import LessonVocabulary
from app.models.user import Student

logger = logging.getLogger(__name__)

DICT_WORD_LIMIT = 80      # user_dictionary.word is String(80); lesson_vocabulary.word allows 120
LANGS = ("uz", "ru")


def normalize_lang(value) -> str | None:
    """'uz' / 'ru', or None for anything else."""
    value = (value or "").strip().lower() if isinstance(value, str) else ""
    return value if value in LANGS else None


async def resolve_lang(db: AsyncSession, student: Student) -> str:
    """The language this student's seeded words should be in."""
    known = normalize_lang(student.ui_lang)
    if known:
        return known
    counts = dict((await db.execute(
        select(UserDictionary.lang, func.count(UserDictionary.id))
        .where(UserDictionary.student_id == student.id, UserDictionary.seeded.is_not(True))
        .group_by(UserDictionary.lang))).all())
    return "ru" if counts.get("ru", 0) > counts.get("uz", 0) else "uz"


def _new_rows(student_id: int, lesson_id: int, vocab: list, existing: set, lang: str) -> list[UserDictionary]:
    """Dictionary rows to insert. `existing` holds the lowercased words the student already has (any language)."""
    seen, rows = set(existing), []
    for v in vocab:
        word = (v.word or "").strip()[:DICT_WORD_LIMIT].strip()
        uz, ru = (v.definition or "").strip(), (v.definition_ru or "").strip()
        definition = ru if (lang == "ru" and ru) else uz
        if not word or not definition or word.lower() in seen:
            continue
        seen.add(word.lower())
        rows.append(UserDictionary(student_id=student_id, word=word, context=definition, lesson_id=lesson_id,
                                   lang=lang, seeded=True))
    return rows


async def plan_rows(db: AsyncSession, student_id: int, lesson_id: int) -> list[UserDictionary]:
    """The dictionary rows seeding would add right now (nothing is written). Demo students get none."""
    student = await db.get(Student, student_id)
    if student is None or student.is_demo:
        return []
    vocab = list((await db.execute(
        select(LessonVocabulary).where(LessonVocabulary.lesson_id == lesson_id)
        .order_by(LessonVocabulary.order, LessonVocabulary.id))).scalars().all())
    if not vocab:
        return []
    existing = set((await db.execute(
        select(func.lower(UserDictionary.word)).where(UserDictionary.student_id == student_id))).scalars().all())
    return _new_rows(student_id, lesson_id, vocab, existing, await resolve_lang(db, student))


async def seed_lesson_words_strict(student_id: int, lesson_id: int) -> int:
    """Add the lesson's words to the student's dictionary in a session of its own; returns the rows added.
    Raises on failure — for the backfill script, which has to count failures."""
    async with AsyncSessionLocal() as db:
        rows = await plan_rows(db, student_id, lesson_id)
        if rows:
            db.add_all(rows)
            await db.commit()
        return len(rows)


async def seed_lesson_words(student_id: int, lesson_id: int) -> int:
    """seed_lesson_words_strict that never raises: a failure is logged and reported as 0."""
    try:
        return await seed_lesson_words_strict(student_id, lesson_id)
    except Exception:  # noqa: BLE001 — seeding is purely additive; the lesson is already finished
        logger.exception("[vocab-seed] failed for student=%s lesson=%s", student_id, lesson_id)
        return 0
