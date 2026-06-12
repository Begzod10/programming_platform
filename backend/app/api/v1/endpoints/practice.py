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
from datetime import datetime, timedelta, date
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select, update, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_student
from app.models.course import Course
from app.models.dictionary import PracticeSession, UserDictionary
from app.models.lesson import Lesson
from app.models.user import Student
from app.services import srs


router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Scope helpers — narrow word queries by category/course/lesson.
# Mirrors life_tracker's folder/module scope using student_platform's
# category → course → lesson hierarchy.
# ─────────────────────────────────────────────────────────────────────────────

def _apply_scope(stmt, *, category_id=None, course_id=None, lesson_id=None):
    """Layer scope filters onto a UserDictionary select. The narrowest
    provided filter wins — lesson > course > category — but they compose,
    so passing both course and lesson is fine (lesson must belong to it)."""
    if lesson_id is not None:
        return stmt.where(UserDictionary.lesson_id == lesson_id)
    if course_id is not None:
        return stmt.join(
            Lesson, Lesson.id == UserDictionary.lesson_id
        ).where(Lesson.course_id == course_id)
    if category_id is not None:
        return stmt.join(
            Lesson, Lesson.id == UserDictionary.lesson_id
        ).join(
            Course, Course.id == Lesson.course_id
        ).where(Course.category_id == category_id)
    return stmt


# ─────────────────────────────────────────────────────────────────────────────
# Word serialisation — includes MCQ distractors so quiz mode is one round-trip
# ─────────────────────────────────────────────────────────────────────────────

def _serialize(word: UserDictionary, pool: list[UserDictionary]) -> dict:
    distractors = [w for w in pool if w.id != word.id]
    # Word-side distractors (old direction: context → pick the word).
    word_sample = random.sample(distractors, min(3, len(distractors)))
    options = [word.word] + [d.word for d in word_sample]
    random.shuffle(options)

    # Context-side distractors (new direction: word → pick its meaning).
    # Filter to entries that actually have a context, otherwise the choice
    # is meaningless. If we can't gather 3 real distractors we fall back
    # to whatever we have; the FE can still render fewer choices.
    ctx_pool = [w for w in distractors if (w.context or "").strip()]
    ctx_sample = random.sample(ctx_pool, min(3, len(ctx_pool)))
    context_options = [word.context or ""] + [d.context for d in ctx_sample]
    random.shuffle(context_options)

    return {
        "id": word.id,
        "word": word.word,
        "context": word.context or "",
        "lesson_id": word.lesson_id,
        "options": options,
        "context_options": context_options,
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
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
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
    base = _apply_scope(
        base,
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    )

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
                or_(
                    UserDictionary.next_review_at.is_(None),
                    UserDictionary.next_review_at <= now,
                ),
            )
        )
    ).scalar() or 0

    fragile = (
        await db.execute(
            _scoped(select(func.count(UserDictionary.id))).where(
                srs.is_fragile(UserDictionary),
            )
        )
    ).scalar() or 0

    total = (
        await db.execute(
            _scoped(select(func.count(UserDictionary.id)))
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
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Counts by retention bucket. Frontend uses these for a stacked bar
    so the student sees how many cards are fragile vs mastered at a glance."""
    label = srs.bucket_expr(UserDictionary).label("bucket")
    stmt = _apply_scope(
        select(label, func.count().label("n"))
        .where(UserDictionary.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    ).group_by(label)
    rows = (await db.execute(stmt)).all()
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


# ─────────────────────────────────────────────────────────────────────────────
# Statistika — aggregate dashboard for the Statistika sub-tab
# ─────────────────────────────────────────────────────────────────────────────

def _compute_streaks(dates: List[date], today: date) -> tuple[int, int]:
    """Walk distinct completion dates to compute (current_streak, longest_streak).

    Current streak counts back from today; the user gets credit for yesterday
    if they haven't practised yet today (otherwise the streak would die at
    midnight before they had a chance to drill). Longest is the max run
    anywhere in history.
    """
    if not dates:
        return 0, 0
    days = sorted(set(dates), reverse=True)

    # Current streak: today, or yesterday-as-grace
    current = 0
    if days[0] == today:
        expected = today
    elif days[0] == today - timedelta(days=1):
        expected = today - timedelta(days=1)
    else:
        current = 0
        expected = None

    if expected is not None:
        for d in days:
            if d == expected:
                current += 1
                expected = expected - timedelta(days=1)
            else:
                break

    # Longest streak: scan ascending, count consecutive
    asc = sorted(set(dates))
    longest = 1
    run = 1
    for i in range(1, len(asc)):
        if asc[i] - asc[i - 1] == timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    return current, longest


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Aggregate practice statistics for the Statistika tab.

    Returns:
      - streak:           current + longest daily streak
      - last_7_days:      one entry per day for the past week
      - mode_breakdown:   sessions/words/accuracy per mode
      - totals:           sessions, words drilled, mastered, mastery %
    """
    now = datetime.utcnow()
    today = now.date()
    seven_ago_dt = datetime(today.year, today.month, today.day) - timedelta(days=6)

    # ── Distinct completed-session dates (for streak) ────────────────────
    date_rows = (
        await db.execute(
            select(cast(PracticeSession.completed_at, Date).label("d"))
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
            )
            .group_by("d")
        )
    ).all()
    dates = [r[0] for r in date_rows if r[0] is not None]
    current_streak, longest_streak = _compute_streaks(dates, today)

    # ── Last 7 days activity (per-day counts) ────────────────────────────
    seven_rows = (
        await db.execute(
            select(
                cast(PracticeSession.completed_at, Date).label("d"),
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
                PracticeSession.completed_at >= seven_ago_dt,
            )
            .group_by("d")
        )
    ).all()
    by_date = {r.d: r for r in seven_rows}
    last_7_days = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        row = by_date.get(d)
        words = int(row.words) if row else 0
        correct = int(row.correct) if row else 0
        last_7_days.append({
            "date": d.isoformat(),
            "sessions": int(row.sessions) if row else 0,
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })

    # ── Per-mode breakdown over all-time completed sessions ──────────────
    mode_rows = (
        await db.execute(
            select(
                PracticeSession.mode,
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
            )
            .group_by(PracticeSession.mode)
        )
    ).all()
    mode_breakdown = []
    for r in mode_rows:
        words = int(r.words)
        correct = int(r.correct)
        mode_breakdown.append({
            "mode": r.mode,
            "sessions": int(r.sessions),
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })
    # Sort by sessions desc so the most-used mode reads first
    mode_breakdown.sort(key=lambda x: x["sessions"], reverse=True)

    # ── Totals ───────────────────────────────────────────────────────────
    total_words = (
        await db.execute(
            select(func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id
            )
        )
    ).scalar() or 0

    # "Mastered" matches the bucket_expr: interval > SOLID_MAX_INT and not fragile
    mastered = (
        await db.execute(
            select(func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id,
                UserDictionary.interval_days > srs.SOLID_MAX_INT,
                ~srs.is_fragile(UserDictionary),
            )
        )
    ).scalar() or 0

    total_sessions = sum(r["sessions"] for r in mode_breakdown)
    total_drilled = sum(r["words"] for r in mode_breakdown)
    total_correct = sum(r["correct"] for r in mode_breakdown)
    overall_acc = round((total_correct / total_drilled) * 100) if total_drilled else 0

    return {
        "streak": {
            "current": current_streak,
            "longest": longest_streak,
            "today_practised": today in by_date,
        },
        "last_7_days": last_7_days,
        "mode_breakdown": mode_breakdown,
        "totals": {
            "words": total_words,
            "mastered": mastered,
            "mastery_pct": round((mastered / total_words) * 100) if total_words else 0,
            "sessions": total_sessions,
            "drilled": total_drilled,
            "accuracy": overall_acc,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Sessions overview — drill-results history with by-date / by-month / averages
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/sessions-overview")
async def get_sessions_overview(
    days: int = Query(default=30, ge=7, le=180),
    months: int = Query(default=6, ge=3, le=24),
    recent_limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Aggregated history of completed practice sessions.

    Powers the Tarix sub-tab — gives the student a calendar-style view of
    their drilling activity: per-day buckets for the last `days`, per-month
    buckets for the last `months`, averages, and the recent N sessions.
    """
    now = datetime.utcnow()
    today = now.date()
    day_window_start = datetime(today.year, today.month, today.day) - timedelta(days=days - 1)

    # First month of the rolling month window — anchor at the 1st of
    # (today.month - (months - 1)).
    anchor_month = today.month - (months - 1)
    anchor_year = today.year
    while anchor_month <= 0:
        anchor_month += 12
        anchor_year -= 1
    month_window_start = datetime(anchor_year, anchor_month, 1)

    base_filter = [
        PracticeSession.student_id == current_user.id,
        PracticeSession.completed_at.isnot(None),
    ]

    # ── By-date (last `days` days) ───────────────────────────────────────
    day_rows = (
        await db.execute(
            select(
                cast(PracticeSession.completed_at, Date).label("d"),
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(*base_filter, PracticeSession.completed_at >= day_window_start)
            .group_by("d")
        )
    ).all()
    by_day_map = {r.d: r for r in day_rows}
    by_date = []
    for i in range(days):
        d = today - timedelta(days=days - 1 - i)
        row = by_day_map.get(d)
        words = int(row.words) if row else 0
        correct = int(row.correct) if row else 0
        by_date.append({
            "date": d.isoformat(),
            "sessions": int(row.sessions) if row else 0,
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })

    # ── By-month (last `months` months) ──────────────────────────────────
    # Walk all completed sessions inside the window in Python — month
    # boundary math via SQL is awkward across dialects and the volume per
    # student stays small.
    month_session_rows = (
        await db.execute(
            select(
                PracticeSession.completed_at,
                PracticeSession.total_words,
                PracticeSession.correct,
            )
            .where(*base_filter, PracticeSession.completed_at >= month_window_start)
        )
    ).all()

    # Pre-seed every month in the window so empty months still render
    by_month_map: dict[str, dict] = {}
    cur_y, cur_m = anchor_year, anchor_month
    while True:
        key = f"{cur_y:04d}-{cur_m:02d}"
        by_month_map[key] = {
            "month": key, "sessions": 0, "words": 0, "correct": 0,
            "active_days": set(),
        }
        if cur_y == today.year and cur_m == today.month:
            break
        cur_m += 1
        if cur_m > 12:
            cur_m = 1
            cur_y += 1

    for row in month_session_rows:
        ts: datetime = row.completed_at
        key = f"{ts.year:04d}-{ts.month:02d}"
        if key not in by_month_map:
            continue
        bucket = by_month_map[key]
        bucket["sessions"] += 1
        bucket["words"] += int(row.total_words or 0)
        bucket["correct"] += int(row.correct or 0)
        bucket["active_days"].add(ts.date())

    by_month = []
    for key in sorted(by_month_map.keys()):
        b = by_month_map[key]
        words = b["words"]
        correct = b["correct"]
        by_month.append({
            "month": key,
            "sessions": b["sessions"],
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
            "active_days": len(b["active_days"]),
        })

    # ── Lifetime totals + averages (over completed sessions) ─────────────
    totals_row = (
        await db.execute(
            select(
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
                func.min(PracticeSession.started_at).label("first"),
            )
            .where(*base_filter)
        )
    ).first()

    sessions_total = int(totals_row.sessions or 0)
    words_total = int(totals_row.words or 0)
    correct_total = int(totals_row.correct or 0)
    first_seen: Optional[datetime] = totals_row.first

    # Sum of (completed_at - started_at) in seconds for sessions that have
    # both endpoints. Falls back to 0 when nothing matches.
    duration_rows = (
        await db.execute(
            select(PracticeSession.started_at, PracticeSession.completed_at)
            .where(
                *base_filter,
                PracticeSession.started_at.isnot(None),
            )
        )
    ).all()
    total_seconds = 0
    duration_samples = 0
    for r in duration_rows:
        if r.started_at and r.completed_at and r.completed_at > r.started_at:
            delta = (r.completed_at - r.started_at).total_seconds()
            # Clamp absurd values (e.g. tabs left open) so the average
            # stays representative of a real drill.
            if 5 <= delta <= 3600:
                total_seconds += delta
                duration_samples += 1

    avg_session_minutes = round(total_seconds / duration_samples / 60, 1) if duration_samples else 0
    avg_session_words = round(words_total / sessions_total, 1) if sessions_total else 0
    avg_session_accuracy = round((correct_total / words_total) * 100) if words_total else 0

    # Distinct active days (lifetime)
    active_days_lifetime = (
        await db.execute(
            select(func.count(func.distinct(cast(PracticeSession.completed_at, Date))))
            .where(*base_filter)
        )
    ).scalar() or 0

    # Distinct active days within the day window
    active_days_window = sum(1 for d in by_date if d["sessions"] > 0)

    # Sessions per week — anchor on the first completed session.
    if first_seen:
        weeks_active = max(1.0, (now - first_seen).total_seconds() / (7 * 86400))
        sessions_per_week = round(sessions_total / weeks_active, 1)
    else:
        sessions_per_week = 0

    # ── Recent N sessions ────────────────────────────────────────────────
    recent_rows = (
        await db.execute(
            select(PracticeSession)
            .where(*base_filter)
            .order_by(PracticeSession.started_at.desc())
            .limit(recent_limit)
        )
    ).scalars().all()
    recent_sessions = []
    for s in recent_rows:
        duration_s = None
        if s.started_at and s.completed_at and s.completed_at > s.started_at:
            duration_s = int((s.completed_at - s.started_at).total_seconds())
        accuracy = (
            round((s.correct / s.total_words) * 100)
            if s.total_words else 0
        )
        recent_sessions.append({
            "id": s.id,
            "mode": s.mode,
            "total_words": s.total_words,
            "correct": s.correct,
            "accuracy": accuracy,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "duration_seconds": duration_s,
        })

    return {
        "window": {
            "days": days,
            "months": months,
            "from_date": by_date[0]["date"] if by_date else None,
            "to_date": by_date[-1]["date"] if by_date else None,
        },
        "totals": {
            "sessions": sessions_total,
            "words": words_total,
            "correct": correct_total,
            "accuracy": avg_session_accuracy,
            "active_days": int(active_days_lifetime),
            "minutes": round(total_seconds / 60) if total_seconds else 0,
        },
        "averages": {
            "per_session_words": avg_session_words,
            "per_session_accuracy": avg_session_accuracy,
            "per_session_minutes": avg_session_minutes,
            "sessions_per_week": sessions_per_week,
            "active_days_in_window": active_days_window,
        },
        "by_date": by_date,
        "by_month": by_month,
        "recent": recent_sessions,
    }


@router.get("/needs-review")
async def get_needs_review(
    limit: int = Query(default=10, ge=1, le=50),
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Top-N words the student should study next.

    Priority ladder (best signal first):
      1. Never reviewed (review_count = 0)
      2. Reviewed but with accuracy < 70% (struggling)
      3. Long-time-no-see (next_review_at past, or null)

    Within each tier, oldest first. Returned shape mirrors what the
    Statistika panel renders directly.
    """
    Word = UserDictionary
    now = datetime.utcnow()

    # Pull a generous pool then rank in Python — the priority ladder mixes
    # boolean and computed-ratio comparisons that SQL would over-complicate.
    pool_stmt = _apply_scope(
        select(Word).where(Word.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    )
    pool = (await db.execute(pool_stmt)).scalars().all()

    def tier(w):
        if (w.review_count or 0) == 0:
            return 0
        if w.review_count > 0:
            acc = (w.correct_count or 0) / w.review_count
            if acc < 0.7:
                return 1
        return 2

    def sort_key(w):
        rc = w.review_count or 0
        acc = (w.correct_count or 0) / rc if rc > 0 else 0.0
        created = w.created_at or datetime(1970, 1, 1)
        return (tier(w), acc, created)

    ranked = sorted(pool, key=sort_key)
    selected = ranked[:limit]

    out = []
    for w in selected:
        rc = w.review_count or 0
        acc = round((w.correct_count or 0) / rc * 100) if rc > 0 else None
        out.append({
            "id": w.id,
            "word": w.word,
            "context": w.context,
            "lesson_id": w.lesson_id,
            "review_count": rc,
            "accuracy": acc,
            "lapses": w.lapses or 0,
            "interval_days": w.interval_days or 0,
            "next_review_at": w.next_review_at.isoformat() if w.next_review_at else None,
        })

    # Also surface how many words match the "needs review" predicate so the
    # UI can show "N more" beside the list without a second round-trip.
    needs_total = sum(
        1 for w in pool
        if (w.review_count or 0) == 0
        or ((w.review_count or 0) > 0
            and (w.correct_count or 0) / (w.review_count or 1) < 0.7)
    )

    return {"items": out, "total": needs_total}


@router.get("/breakdown")
async def get_breakdown(
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    """Distribution by difficulty (derived from the parent course's
    `difficulty_level`) and by AI-extracted part_of_speech.

    Mirrors life_tracker's by_difficulty / by_part_of_speech blocks. The
    difficulty comes from the course tier rather than a per-word column —
    in this codebase words inherit difficulty from the lesson they were
    captured in, so words from a "Beginner" course bucket as Beginner.
    Words with no lesson_id (manually added, no source) bucket as
    "noma'lum".
    """
    Word = UserDictionary

    base = _apply_scope(
        select(
            Word.id,
            Word.part_of_speech,
            Course.difficulty_level,
        )
        .outerjoin(Lesson, Lesson.id == Word.lesson_id)
        .outerjoin(Course, Course.id == Lesson.course_id)
        .where(Word.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    )

    rows = (await db.execute(base)).all()

    by_difficulty: dict[str, int] = {}
    by_pos: dict[str, int] = {}
    for _wid, pos, diff in rows:
        diff_key = diff or "noma'lum"
        pos_key = (pos or "noma'lum").lower()
        by_difficulty[diff_key] = by_difficulty.get(diff_key, 0) + 1
        by_pos[pos_key] = by_pos.get(pos_key, 0) + 1

    # Sort PoS descending so the dominant grammatical category reads first.
    # Difficulty keeps a curriculum-friendly order: Beginner → Expert,
    # unknown at the end.
    diff_order = ["Beginner", "Intermediate", "Advanced", "Expert"]
    by_difficulty_sorted = {
        **{k: by_difficulty[k] for k in diff_order if k in by_difficulty},
        **{k: v for k, v in by_difficulty.items() if k not in diff_order},
    }
    by_pos_sorted = dict(sorted(by_pos.items(), key=lambda x: -x[1]))

    return {
        "total": len(rows),
        "by_difficulty": by_difficulty_sorted,
        "by_part_of_speech": by_pos_sorted,
    }
