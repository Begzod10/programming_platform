"""Mashq (practice) endpoints — SM-2 SRS drill over the student's saved
dictionary words.

Ported from life_tracker/backend/app/routers/practice.py and adapted to
student_platform's async stack + simpler dictionary schema (one word +
context, no folders/modules).

Modes supported (the field is opaque to the backend — the frontend owns
the per-mode UX):
    flashcard | quiz | spelling | listening | cloze
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_student
from app.models.dictionary import PracticeSession, UserDictionary
from app.models.user import Student
from app.services import srs


router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Word serialisation — includes MCQ distractors so quiz mode is one round-trip
# ─────────────────────────────────────────────────────────────────────────────

def _serialize(word: UserDictionary, pool: list[UserDictionary]) -> dict:
    distractors = [w for w in pool if w.id != word.id]
    sample = random.sample(distractors, min(3, len(distractors)))
    options = [word.word] + [d.word for d in sample]
    random.shuffle(options)
    return {
        "id": word.id,
        "word": word.word,
        "context": word.context or "",
        "lesson_id": word.lesson_id,
        "options": options,
        # SRS state — surfaced so the UI can label cards
        # ("never reviewed", "fragile", etc.) in the queue preview.
        "interval_days": word.interval_days,
        "lapses": word.lapses,
        "ease_factor": word.ease_factor,
        "review_count": word.review_count,
        "next_review_at": (
            word.next_review_at.isoformat() if word.next_review_at else None
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Word selection
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/words")
async def get_practice_words(
    count: int = Query(default=10, ge=1, le=200),
    due_only: bool = Query(default=False),
    weak_only: bool = Query(default=False),
    ids: Optional[str] = Query(
        default=None,
        description=(
            "Comma-separated word IDs. Used by Resume to rehydrate a paused "
            "drill without re-selecting from the SRS pool. Returns the words "
            "in the order they were passed."
        ),
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    Word = UserDictionary

    # Resume path — caller already knows which words it wants.
    if ids:
        try:
            id_list = [int(x) for x in ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(400, "Invalid ids list")
        if not id_list:
            return []
        rows = (
            await db.execute(
                select(Word).where(
                    Word.id.in_(id_list),
                    Word.student_id == current_user.id,
                )
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

    if due_only:
        base = base.where(
            or_(Word.next_review_at.is_(None), Word.next_review_at <= now)
        )
    if weak_only:
        base = base.where(srs.weak_condition(Word))

    if due_only or weak_only:
        # Narrowed pool: hardest first.
        ordered = (
            await db.execute(
                base.order_by(
                    Word.ease_factor.asc(),
                    Word.interval_days.asc(),
                    Word.created_at.asc(),
                )
            )
        ).scalars().all()
        if len(ordered) < 2:
            raise HTTPException(
                400,
                "Mashq uchun yetarlicha so'z yo'q (kamida 2 ta kerak).",
            )
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

    # Default pool: coverage-aware priority sorted DB-side.
    all_words = (
        await db.execute(base.order_by(*srs.pool_priority_order(Word, now)))
    ).scalars().all()
    if len(all_words) < 2:
        raise HTTPException(
            400,
            "Mashq uchun yetarlicha so'z yo'q (kamida 2 ta kerak).",
        )
    selected = all_words[:count]
    return [_serialize(w, all_words) for w in selected]


# ─────────────────────────────────────────────────────────────────────────────
# Result submission with SM-2 scheduling
# ─────────────────────────────────────────────────────────────────────────────

class ResultRequest(BaseModel):
    word_id: int
    was_correct: bool
    grade: Optional[int] = Field(
        default=None,
        ge=0,
        le=2,
        description=(
            "3-level grade: 0 = wrong/forgot, 1 = hard (close), "
            "2 = good (exact/correct). When provided, supersedes was_correct. "
            "Typed-answer modes (spelling, listening, cloze) send this so "
            "'close' answers get a smaller interval bump instead of full credit."
        ),
    )


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

    sched = srs.apply_result(
        word, grade=payload.grade, was_correct=payload.was_correct
    )
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


# ─────────────────────────────────────────────────────────────────────────────
# Due-counts helper for UI badges
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/due-counts")
async def get_due_counts(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    now = datetime.utcnow()
    from sqlalchemy import func as sql_func

    due = (
        await db.execute(
            select(sql_func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id,
                or_(
                    UserDictionary.next_review_at.is_(None),
                    UserDictionary.next_review_at <= now,
                ),
            )
        )
    ).scalar() or 0

    fragile = (
        await db.execute(
            select(sql_func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id,
                srs.is_fragile(UserDictionary),
            )
        )
    ).scalar() or 0

    total = (
        await db.execute(
            select(sql_func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id
            )
        )
    ).scalar() or 0

    return {"due": due, "fragile": fragile, "total": total}


# ─────────────────────────────────────────────────────────────────────────────
# Session bookkeeping — supports resume across page reloads
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_MODES = {"flashcard", "quiz", "spelling", "listening", "cloze"}


def _session_dict(s: PracticeSession) -> dict:
    return {
        "id": s.id,
        "mode": s.mode,
        "total_words": s.total_words,
        "correct": s.correct,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        "progress": s.progress,
    }


class CreateSessionRequest(BaseModel):
    mode: str


@router.post("/session")
async def create_session(
    payload: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    if payload.mode not in ALLOWED_MODES:
        raise HTTPException(400, f"Noma'lum rejim: {payload.mode}")
    s = PracticeSession(student_id=current_user.id, mode=payload.mode)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return _session_dict(s)


class CompleteSessionRequest(BaseModel):
    total_words: int = Field(..., ge=0)
    correct: int = Field(..., ge=0)


@router.put("/session/{session_id}/complete")
async def complete_session(
    session_id: int,
    payload: CompleteSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    s = (
        await db.execute(
            select(PracticeSession).where(
                PracticeSession.id == session_id,
                PracticeSession.student_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Sessiya topilmadi")

    s.total_words = payload.total_words
    s.correct = payload.correct
    s.completed_at = datetime.utcnow()
    # A completed session can't be resumed — drop the snapshot so
    # /session/active never picks it back up if a stale progress write
    # races the complete request.
    s.progress = None
    await db.commit()
    return _session_dict(s)


class ProgressUpdate(BaseModel):
    progress: Any  # Opaque snapshot — frontend owns the shape.


@router.get("/session/active")
async def get_active_session(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Most recent uncompleted session with a progress snapshot, or null.
    A session with no snapshot yet (just created, no chunk finished) is
    intentionally not returned — nothing useful to resume from."""
    s = (
        await db.execute(
            select(PracticeSession)
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.is_(None),
                PracticeSession.progress.isnot(None),
            )
            .order_by(PracticeSession.started_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return _session_dict(s) if s else None


@router.put("/session/{session_id}/progress")
async def update_session_progress(
    session_id: int,
    payload: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    s = (
        await db.execute(
            select(PracticeSession).where(
                PracticeSession.id == session_id,
                PracticeSession.student_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Sessiya topilmadi")
    if s.completed_at is not None:
        # Stale progress write racing the complete request. Drop it
        # silently — a completed session can't be resumed.
        return {"ok": True, "ignored": True}
    s.progress = payload.progress
    await db.commit()
    return {"ok": True}


@router.delete("/session/{session_id}", status_code=204)
async def discard_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Discard an uncompleted session. Refuse on completed sessions so
    history stays append-only."""
    s = (
        await db.execute(
            select(PracticeSession).where(
                PracticeSession.id == session_id,
                PracticeSession.student_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Sessiya topilmadi")
    if s.completed_at is not None:
        raise HTTPException(400, "Tugagan sessiyani o'chirib bo'lmaydi")
    await db.delete(s)
    await db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# AI judge for typed answers — synonyms / paraphrases / missing function words
# ─────────────────────────────────────────────────────────────────────────────

class JudgeAnswerRequest(BaseModel):
    user_input: str = Field(..., max_length=200)
    target: str = Field(..., max_length=200)
    definition: Optional[str] = Field(None, max_length=400)


@router.post("/judge-answer")
async def judge_typed_answer(
    body: JudgeAnswerRequest,
    current_user: Student = Depends(get_current_student),
):
    """Last-resort judge for typed answers when the local Levenshtein matcher
    rejects them. Designed for cases like target="qo'shimcha funksiya" and
    typed="qo'shimcha funksiyalar" — essentially correct but rejected by edit
    distance because of the suffix.

    Returns {"ok": bool, "verdict": "yes"|"close"|"no", "reason": str}. Falls
    back to {"ok": false, ...} when no AI provider is configured or the call
    fails — the caller then keeps its local rejection.
    """
    from app.services.grok_service import _ask_ai
    from app.config import settings

    user_input = body.user_input.strip()
    target = body.target.strip()
    if not user_input or not target:
        raise HTTPException(400, "user_input va target majburiy")

    has_provider = any([
        getattr(settings, "GROK_API_KEY", None),
        getattr(settings, "GEMINI_API_KEY", None),
        getattr(settings, "OPENAI_API_KEY", None),
    ])
    if not has_provider:
        return {"ok": False, "verdict": "no", "reason": "AI sozlanmagan"}

    definition = (body.definition or "").strip()[:400]
    prompt = (
        "Sen lug'at javoblarini baholaysiz. O'quvchi maqsadli so'z yoki "
        "iborani yozishi kerak edi. Quyidagi javobni baholang — sinonimlarni, "
        "uzun so'zlardagi 1 ta belgi xatosini va ko'p so'zli iboralarda "
        "yo'qotilgan yordamchi so'zlarni (artikllar, predloglar) qabul qiling. "
        "Ma'noni o'zgartiruvchi yoki noto'g'ri so'z tanlangan javoblarni rad eting.\n\n"
        f"Maqsad: {target}\n"
        f"Ta'rif / izoh: {definition or '(yo''q)'}\n"
        f"O'quvchi yozdi: {user_input}\n\n"
        "Faqat BIR so'z qaytaring (katta harf bilan): YES (asosan to'g'ri), "
        "CLOSE (ma'nosi yaqin, qisman to'g'ri), yoki NO."
    )

    try:
        raw = await _ask_ai(prompt)
    except Exception as e:
        return {"ok": False, "verdict": "no", "reason": f"ai_error: {type(e).__name__}"}

    if not raw:
        return {"ok": False, "verdict": "no", "reason": "AI bo'sh javob qaytardi"}

    token = raw.strip().upper().split()[:1]
    verdict = token[0] if token else "NO"
    if verdict not in ("YES", "CLOSE", "NO"):
        verdict = "NO"

    return {
        "ok": verdict in ("YES", "CLOSE"),
        "verdict": verdict.lower(),
        "reason": raw[:200],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Retention buckets + leeches — surfacing struggle words
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/buckets")
async def get_retention_buckets(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Counts by retention bucket. Frontend uses these for a stacked bar
    so the student sees how many cards are fragile vs mastered at a glance."""
    from sqlalchemy import func as sql_func

    label = srs.bucket_expr(UserDictionary).label("bucket")
    rows = (
        await db.execute(
            select(label, sql_func.count().label("n"))
            .where(UserDictionary.student_id == current_user.id)
            .group_by(label)
        )
    ).all()
    out = {"fragile": 0, "learning": 0, "solid": 0, "mastered": 0}
    for bucket, n in rows:
        out[bucket] = n
    return out


@router.get("/leeches")
async def get_leeches(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Cards forgotten LEECH_LAPSES+ times. Surface so the student can
    pause, rewrite the entry, or study them deliberately."""
    rows = (
        await db.execute(
            select(UserDictionary)
            .where(
                UserDictionary.student_id == current_user.id,
                UserDictionary.lapses >= srs.LEECH_LAPSES,
            )
            .order_by(UserDictionary.lapses.desc(), UserDictionary.ease_factor.asc())
            .limit(limit)
        )
    ).scalars().all()
    return [
        {
            "id": w.id,
            "word": w.word,
            "context": w.context,
            "lapses": w.lapses,
            "ease_factor": w.ease_factor,
            "interval_days": w.interval_days,
        }
        for w in rows
    ]


@router.get("/history")
async def get_history(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    rows = (
        await db.execute(
            select(PracticeSession)
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
            )
            .order_by(PracticeSession.started_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [_session_dict(s) for s in rows]
