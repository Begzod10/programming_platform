"""Daily-quota / games-lock read endpoints.

Live updates arrive over the notifications WebSocket ({type:'quota'} frames);
these are the initial paint + a poll fallback, same pattern as the bell.
"""
from datetime import date as _date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_student, get_current_teacher
from app.models.user import Student
from app.models.daily_quota import PenaltyLog, StreakTracker, StreakBonusLog
from app.services import daily_quota_service

router = APIRouter()


def _cfg_dict(cfg) -> dict:
    return {
        "enabled": cfg.enabled,
        "enforce_from": cfg.enforce_from.isoformat() if cfg.enforce_from else None,
        "base_lessons": cfg.base_lessons,
        "penalty_per_lesson": cfg.penalty_per_lesson,
        "unlock_mode": cfg.unlock_mode,
        "yield_rate": daily_quota_service.YIELD_RATE,
    }


class QuotaConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    enforce_from: Optional[_date] = None
    clear_enforce_from: Optional[bool] = None   # set enforce_from to NULL (enforce immediately)
    base_lessons: Optional[int] = None
    penalty_per_lesson: Optional[int] = None
    unlock_mode: Optional[str] = None


@router.get("/config")
async def get_quota_config(
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    """Teacher-only: current daily-quota settings (the on/off toggle lives here)."""
    cfg = await daily_quota_service.get_config(db)
    await db.commit()
    return _cfg_dict(cfg)


@router.put("/config")
async def update_quota_config(
    body: QuotaConfigUpdate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    """Teacher-only: flip the feature on/off, set the enforcement start date, or
    tune the thresholds — all without a redeploy."""
    cfg = await daily_quota_service.get_config(db)
    if body.enabled is not None:
        cfg.enabled = body.enabled
    if body.clear_enforce_from:
        cfg.enforce_from = None
    elif body.enforce_from is not None:
        cfg.enforce_from = body.enforce_from
    if body.base_lessons is not None:
        cfg.base_lessons = max(1, body.base_lessons)
    if body.penalty_per_lesson is not None:
        cfg.penalty_per_lesson = max(0, body.penalty_per_lesson)
    if body.unlock_mode in ("base", "full"):
        cfg.unlock_mode = body.unlock_mode
    cfg.updated_by = teacher.id
    await db.commit()
    return _cfg_dict(cfg)


@router.get("/status")
async def quota_status(
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Today's quota progress + lock state, plus a streak summary."""
    status_ = await daily_quota_service.get_today(db, current_student.id)
    st = (await db.execute(
        select(StreakTracker).where(StreakTracker.student_id == current_student.id)
    )).scalar_one_or_none()
    streak = {
        "length": st.length if st else 0,
        "best_length": st.best_length if st else 0,
        "active": bool(st.active) if st else False,
        "yield_rate": daily_quota_service.YIELD_RATE,
    }
    return {**status_.as_dict(), "streak": streak}


@router.get("/penalties")
async def quota_penalties(
    limit: int = Query(30, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    rows = (await db.execute(
        select(PenaltyLog)
        .where(PenaltyLog.student_id == current_student.id)
        .order_by(PenaltyLog.created_at.desc())
        .limit(limit)
    )).scalars().all()
    return {"items": [
        {
            "quota_date": r.quota_date.isoformat(),
            "lessons_missed": r.lessons_missed,
            "points_deducted": r.points_deducted,
            "points_after": r.points_after,
            "reason": r.reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows
    ]}


@router.get("/streak")
async def quota_streak(
    limit: int = Query(30, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    st = (await db.execute(
        select(StreakTracker).where(StreakTracker.student_id == current_student.id)
    )).scalar_one_or_none()
    bonuses = (await db.execute(
        select(StreakBonusLog)
        .where(StreakBonusLog.student_id == current_student.id)
        .order_by(StreakBonusLog.created_at.desc())
        .limit(limit)
    )).scalars().all()
    return {
        "length": st.length if st else 0,
        "best_length": st.best_length if st else 0,
        "started_on": st.started_on.isoformat() if st and st.started_on else None,
        "active": bool(st.active) if st else False,
        "yield_rate": daily_quota_service.YIELD_RATE,
        "bonus_history": [
            {
                "quota_date": b.quota_date.isoformat(),
                "streak_length": b.streak_length,
                "base_points": b.base_points,
                "bonus_points": b.bonus_points,
            } for b in bonuses
        ],
    }
