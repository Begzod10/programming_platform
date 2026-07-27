"""Word selection, serialization, result submission, and due-counts."""
from __future__ import annotations

import random
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_student
from app.models.course import Course
from app.models.dictionary import UserDictionary
from app.models.lesson import Lesson
from app.models.user import Student
from app.services import srs

router = APIRouter()


def _apply_scope(stmt, *, category_id=None, course_id=None, lesson_id=None):
    if lesson_id is not None:
        return stmt.where(UserDictionary.lesson_id == lesson_id)
    if course_id is not None:
        return stmt.join(Lesson, Lesson.id == UserDictionary.lesson_id).where(Lesson.course_id == course_id)
    if category_id is not None:
        return stmt.join(Lesson, Lesson.id == UserDictionary.lesson_id).join(
            Course, Course.id == Lesson.course_id
        ).where(Course.category_id == category_id)
    return stmt


def _mask_word_in_text(text: str, word: str) -> str:
    """Blank out standalone occurrences of `word`'s tokens inside `text`.

    Recall-style surfaces (Quiz+ round 2 "Yozish" pass, Spelling, Listening,
    and the MCQ "pick the meaning" options) show a word's definition and ask
    the student to reproduce the word itself. The AI explanation prompt
    often restates the term as its own subject (e.g. "JavaScript — bu
    veb-sahifalarga dinamiklik qo'shadigan dasturlash tili."), which hands
    the answer straight back to the student instead of testing recall.
    Mask it out of the copies used for those surfaces.

    Cloze mode needs the *raw* context (it blanks the word out of a real
    usage sentence on purpose) — callers must keep using `word.context`
    there, never this masked copy.
    """
    if not text:
        return text
    tokens = [t for t in re.split(r"[^\w']+", word or "") if len(t) >= 2]
    out = text
    for tok in tokens:
        pattern = re.compile(rf"(?<![\w']){re.escape(tok)}(?![\w'])", re.IGNORECASE)
        out = pattern.sub(lambda m: "•" * max(len(m.group(0)), 3), out)
    return out


def _serialize(word: UserDictionary, pool: list[UserDictionary]) -> dict:
    distractors = [w for w in pool if w.id != word.id]
    word_sample = random.sample(distractors, min(3, len(distractors)))
    options = [word.word] + [d.word for d in word_sample]
    random.shuffle(options)

    ctx_pool = [w for w in distractors if (w.context or "").strip()]
    ctx_sample = random.sample(ctx_pool, min(3, len(ctx_pool)))
    # Mask each option's own target word out of its own context text so the
    # "pick the meaning" MCQ pass can't be solved by literally spotting the
    # word inside the option (see _mask_word_in_text).
    context_options = [_mask_word_in_text(word.context or "", word.word)] + [
        _mask_word_in_text(d.context or "", d.word) for d in ctx_sample
    ]
    random.shuffle(context_options)

    return {
        "id": word.id,
        "word": word.word,
        "context": word.context or "",
        "context_masked": _mask_word_in_text(word.context or "", word.word),
        "lesson_id": word.lesson_id,
        "options": options,
        "context_options": context_options,
        "interval_days": word.interval_days,
        "lapses": word.lapses,
        "ease_factor": word.ease_factor,
        "review_count": word.review_count,
        "next_review_at": (word.next_review_at.isoformat() if word.next_review_at else None),
    }


@router.get("/words")
async def get_practice_words(
    count: int = Query(default=10, ge=1, le=200),
    due_only: bool = Query(default=False),
    weak_only: bool = Query(default=False),
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    ids: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    Word = UserDictionary

    if ids:
        try:
            id_list = [int(x) for x in ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(400, "Invalid ids list")
        if not id_list:
            return []
        rows = (
            await db.execute(
                select(Word).where(Word.id.in_(id_list), Word.student_id == current_user.id)
            )
        ).scalars().all()
        by_id = {w.id: w for w in rows}
        ordered = [by_id[i] for i in id_list if i in by_id]
        pool = list(ordered)
        if len(pool) < 4:
            extra = (
                await db.execute(
                    select(Word).where(
                        Word.student_id == current_user.id,
                        Word.id.notin_([w.id for w in pool]),
                    ).limit(20)
                )
            ).scalars().all()
            pool += extra
        return [_serialize(w, pool) for w in ordered]

    now = datetime.utcnow()
    base = select(Word).where(Word.student_id == current_user.id)
    base = _apply_scope(base, category_id=category_id, course_id=course_id, lesson_id=lesson_id)

    if due_only:
        base = base.where(or_(Word.next_review_at.is_(None), Word.next_review_at <= now))
    if weak_only:
        base = base.where(srs.weak_condition(Word))

    if due_only or weak_only:
        ordered = (
            await db.execute(
                base.order_by(Word.ease_factor.asc(), Word.interval_days.asc(), Word.created_at.asc())
            )
        ).scalars().all()
        if len(ordered) < 2:
            raise HTTPException(400, "Mashq uchun yetarlicha so'z yo'q (kamida 2 ta kerak).")
        selected = ordered[:count]
        pool = list({w.id: w for w in ordered}.values())
        if len(pool) < 4:
            extra = (
                await db.execute(
                    select(Word).where(
                        Word.student_id == current_user.id,
                        Word.id.notin_([w.id for w in pool]),
                    ).limit(20)
                )
            ).scalars().all()
            pool += extra
        return [_serialize(w, pool) for w in selected]

    all_words = (
        await db.execute(base.order_by(*srs.pool_priority_order(Word, now)))
    ).scalars().all()
    if len(all_words) < 2:
        raise HTTPException(400, "Mashq uchun yetarlicha so'z yo'q (kamida 2 ta kerak).")
    selected = all_words[:count]
    return [_serialize(w, all_words) for w in selected]


class ResultRequest(BaseModel):
    word_id: int
    was_correct: bool
    grade: Optional[int] = Field(default=None, ge=0, le=2)


@router.post("/result")
async def submit_result(
    payload: ResultRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    word = (
        await db.execute(
            select(UserDictionary).where(
                UserDictionary.id == payload.word_id,
                UserDictionary.student_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not word:
        raise HTTPException(404, "So'z topilmadi")

    sched = srs.apply_result(word, grade=payload.grade, was_correct=payload.was_correct)
    await db.commit()
    return {
        "ok": True,
        "interval_days": word.interval_days,
        "next_review_at": word.next_review_at.isoformat(),
        "ease_factor": word.ease_factor,
        "reps": word.reps,
        "lapses": word.lapses,
        "is_leech": sched["is_leech"],
    }


@router.get("/due-counts")
async def get_due_counts(
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    now = datetime.utcnow()

    def _scoped(stmt):
        return _apply_scope(
            stmt.where(UserDictionary.student_id == current_user.id),
            category_id=category_id,
            course_id=course_id,
            lesson_id=lesson_id,
        )

    due = (
        await db.execute(
            _scoped(select(func.count(UserDictionary.id))).where(
                or_(UserDictionary.next_review_at.is_(None), UserDictionary.next_review_at <= now)
            )
        )
    ).scalar() or 0

    fragile = (
        await db.execute(
            _scoped(select(func.count(UserDictionary.id))).where(srs.is_fragile(UserDictionary))
        )
    ).scalar() or 0

    total = (
        await db.execute(_scoped(select(func.count(UserDictionary.id))))
    ).scalar() or 0

    return {"due": due, "fragile": fragile, "total": total}
