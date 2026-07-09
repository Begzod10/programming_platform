"""Practice session CRUD and AI judge for typed answers."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_student
from app.models.dictionary import PracticeSession
from app.models.user import Student

router = APIRouter()

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
    s.progress = None
    await db.commit()
    return _session_dict(s)


class ProgressUpdate(BaseModel):
    progress: Any


@router.get("/session/active")
async def get_active_session(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
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


class JudgeAnswerRequest(BaseModel):
    user_input: str = Field(..., max_length=200)
    target: str = Field(..., max_length=200)
    definition: Optional[str] = Field(None, max_length=400)


@router.post("/judge-answer")
async def judge_typed_answer(
    body: JudgeAnswerRequest,
    current_user: Student = Depends(get_current_student),
):
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
