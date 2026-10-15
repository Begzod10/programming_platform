"""Teacher-applied penalties.

A teacher picks a student, a reason, and an amount, and docks that many points
from the student's *profile* total (career/leaderboard + spendable wallet),
floored at 0 — a standalone disciplinary action, unrelated to any project. Every
penalty is logged (TeacherPenalty) and the student is notified with full detail.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_instructor
from app.models.user import Student, UserRole
from app.models.teacher_penalty import TeacherPenalty, PENALTY_TYPES
from app.services.ranking_service import RankingService
from app.services.teacher_students import teacher_student_ids_subquery
from app.services import notification_service

router = APIRouter()


# ── Schemas ─────────────────────────────────────────────────────────────────

class PenaltyStudent(BaseModel):
    student_id: int
    full_name: Optional[str] = None
    username: str
    avatar_url: Optional[str] = None
    rating_points: int = 0      # lifetime_points — what the leaderboard shows
    spendable_points: int = 0   # total_points — the store wallet


class ApplyPenaltyRequest(BaseModel):
    student_id: int
    # Uncapped (teacher may fine any amount), but at least 1 point.
    amount: int = Field(..., ge=1, description="Jarima balli (musbat son)")
    penalty_type: str = "other"
    comment: Optional[str] = Field(None, max_length=1000)

    @field_validator("penalty_type", mode="before")
    @classmethod
    def _valid_type(cls, v):
        return v if v in PENALTY_TYPES else "other"


class PenaltyRead(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    amount: int
    penalty_type: str
    comment: Optional[str] = None
    points_before: int
    points_after: int
    created_at: datetime


class ApplyPenaltyResponse(BaseModel):
    penalty: PenaltyRead
    rating_points: int  # student's new leaderboard total after the dock


# ── Helpers ─────────────────────────────────────────────────────────────────

async def _student_in_scope(db: AsyncSession, student_id: int, teacher_id: int) -> bool:
    """True iff the student is reachable by this teacher (group or flow)."""
    res = await db.execute(
        select(Student.id).where(
            Student.id == student_id,
            Student.id.in_(select(teacher_student_ids_subquery(teacher_id).c.student_id)),
        ).limit(1)
    )
    return res.scalars().first() is not None


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/students", response_model=List[PenaltyStudent])
async def list_penalty_students(
    search: Optional[str] = Query(None),
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Students this teacher can penalise, with their current rating balance —
    powers the picker on the Penalties page."""
    scope = select(teacher_student_ids_subquery(current_teacher.id).c.student_id).scalar_subquery()
    q = (
        select(Student)
        .where(
            Student.id.in_(scope),
            Student.role == UserRole.student,
            Student.is_demo.is_(False),
        )
        .order_by(Student.full_name, Student.username)
    )
    if search:
        like = f"%{search.strip()}%"
        q = q.where(func.coalesce(Student.full_name, "").ilike(like) | Student.username.ilike(like))
    rows = (await db.execute(q)).scalars().all()
    return [
        PenaltyStudent(
            student_id=s.id,
            full_name=s.full_name,
            username=s.username,
            avatar_url=s.avatar_url,
            rating_points=s.lifetime_points or 0,
            spendable_points=s.total_points or 0,
        )
        for s in rows
    ]


@router.get("", response_model=List[PenaltyRead])
@router.get("/", response_model=List[PenaltyRead])
async def list_penalties(
    student_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Penalty history for this teacher's students (optionally one student)."""
    scope = select(teacher_student_ids_subquery(current_teacher.id).c.student_id).scalar_subquery()
    q = (
        select(TeacherPenalty)
        .where(TeacherPenalty.student_id.in_(scope))
        .order_by(TeacherPenalty.created_at.desc())
        .limit(limit)
    )
    if student_id is not None:
        q = q.where(TeacherPenalty.student_id == student_id)
    penalties = (await db.execute(q)).scalars().all()
    if not penalties:
        return []

    # Resolve names in one shot.
    ids = {p.student_id for p in penalties} | {p.teacher_id for p in penalties if p.teacher_id}
    name_rows = (await db.execute(
        select(Student.id, Student.full_name, Student.username).where(Student.id.in_(ids))
    )).all()
    names = {r[0]: (r[1] or r[2]) for r in name_rows}

    return [
        PenaltyRead(
            id=p.id,
            student_id=p.student_id,
            student_name=names.get(p.student_id),
            teacher_id=p.teacher_id,
            teacher_name=names.get(p.teacher_id) if p.teacher_id else None,
            amount=p.amount,
            penalty_type=p.penalty_type,
            comment=p.comment,
            points_before=p.points_before,
            points_after=p.points_after,
            created_at=p.created_at,
        )
        for p in penalties
    ]


@router.post("", response_model=ApplyPenaltyResponse)
@router.post("/", response_model=ApplyPenaltyResponse)
async def apply_penalty(
    data: ApplyPenaltyRequest,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Dock `amount` points from the student's profile total (rating + wallet),
    floored at 0. Logs the penalty and notifies the student with full detail."""
    res = await db.execute(select(Student).where(Student.id == data.student_id))
    student = res.scalar_one_or_none()
    if not student or student.role != UserRole.student:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    if student.is_demo:
        raise HTTPException(status_code=400, detail="Demo akkauntni jarima qilib bo'lmaydi")
    if not await _student_in_scope(db, data.student_id, current_teacher.id):
        raise HTTPException(status_code=403, detail="Bu student sizning guruhingizda emas")

    points_before = student.lifetime_points or 0
    # revoke_earned_points reduces BOTH wallets (spendable + career/leaderboard),
    # floored at 0 — exactly the "rating points" the student sees, dropped.
    await RankingService(db).revoke_earned_points(data.student_id, data.amount)
    await db.refresh(student)
    points_after = student.lifetime_points or 0

    penalty = TeacherPenalty(
        student_id=data.student_id,
        teacher_id=current_teacher.id,
        amount=data.amount,
        penalty_type=data.penalty_type,
        comment=(data.comment or None),
        points_before=points_before,
        points_after=points_after,
    )
    db.add(penalty)
    await db.commit()
    await db.refresh(penalty)

    # Full-detail notification (never raises into us).
    await notification_service.notify_teacher_penalty(
        db, data.student_id,
        amount=data.amount, penalty_type=data.penalty_type,
        comment=data.comment, points_after=points_after,
    )

    return ApplyPenaltyResponse(
        penalty=PenaltyRead(
            id=penalty.id,
            student_id=penalty.student_id,
            student_name=(student.full_name or student.username),
            teacher_id=penalty.teacher_id,
            teacher_name=(current_teacher.full_name or current_teacher.username),
            amount=penalty.amount,
            penalty_type=penalty.penalty_type,
            comment=penalty.comment,
            points_before=penalty.points_before,
            points_after=penalty.points_after,
            created_at=penalty.created_at,
        ),
        rating_points=points_after,
    )
