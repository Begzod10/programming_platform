"""Daily-quota / games-lock read endpoints.

Live updates arrive over the notifications WebSocket ({type:'quota'} frames);
these are the initial paint + a poll fallback, same pattern as the bell.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_student
from app.models.user import Student
from app.models.daily_quota import PenaltyLog, StreakTracker, StreakBonusLog
from app.services import daily_quota_service

router = APIRouter()


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
