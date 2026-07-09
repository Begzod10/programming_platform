from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.dependencies import get_db, get_current_instructor
from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.schemas.teacher_progress import (
    TeacherStudentProgress,
    TeacherStudentProgressDetail,
    TeacherStudentProgressList,
    TeacherStudentRankingList,
)
from app.models.user import Student
from app.models.group import Group
from app.models.student_achievement import StudentAchievement
from app.services.student_service import StudentService

router = APIRouter()


VALID_PERIODS = ("day", "week", "month", "all")


@router.get("/rankings", response_model=TeacherStudentRankingList)
async def get_students_rankings(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        period: str = Query(
            "all",
            description="day | week | month | all — which Ranking bucket to read",
        ),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    if period not in VALID_PERIODS:
        period = "all"
    service = StudentService(db)
    return await service.get_teacher_students_ranking(
        current_teacher.id,
        skip=skip,
        limit=limit,
        search=search,
        period=period,
    )


async def _student_is_in_teachers_group(
    db: AsyncSession, student_id: int, teacher_id: int
) -> bool:
    """Return True iff `student_id` belongs to a group owned by `teacher_id`."""
    res = await db.execute(
        select(Student)
        .join(Student.groups)
        .where(Student.id == student_id, Group.teacher_id == teacher_id)
        .limit(1)
    )
    return res.scalars().first() is not None


@router.get("/", response_model=List[TeacherStudentProgress])
async def get_all_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_students_by_teacher(current_teacher.id, skip, limit, search)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_student(
        data: UserCreate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    from app.services.auth_service import register_new_student
    result = await register_new_student(db, data)
    return result["user"]


@router.get("/progress", response_model=TeacherStudentProgressList)
async def get_students_progress(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_teacher_students_progress(
        current_teacher.id,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.get("/{student_id}/progress", response_model=TeacherStudentProgressDetail)
async def get_student_progress(
        student_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    service = StudentService(db)
    return await service.get_teacher_student_progress(current_teacher.id, student_id)


@router.delete("/{student_id}")
async def teacher_delete_student(
    student_id: int,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Delete a student — only allowed if the student is in a group the
    requesting teacher owns. Without this check any teacher can delete
    any student account on the platform.
    """
    if not await _student_is_in_teachers_group(db, student_id, current_teacher.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu studentni o'chirish huquqi yo'q (sizning guruhingizda emas)",
        )
    service = StudentService(db)
    return await service.delete_student(student_id)


# ── Achievement overview schemas ───────────────────────────────────────────

class AchievementBrief(BaseModel):
    id: int
    name: str
    icon: Optional[str] = "🏆"
    category: Optional[str] = None
    points_reward: int = 0
    earned_at: datetime


class StudentAchievementOverview(BaseModel):
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int = 0
    achievement_count: int = 0
    achievements: List[AchievementBrief] = []


# ── Endpoint ───────────────────────────────────────────────────────────────

@router.get("/achievements/overview", response_model=List[StudentAchievementOverview])
async def get_students_achievements_overview(
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """All students with the achievements they have earned.

    Returns every student (sorted by achievement count desc) with a flat
    list of their badges — name, icon, category, points, and date earned.
    """
    from app.models.group import Group, student_groups
    teacher_student_ids_sq = (
        select(student_groups.c.student_id)
        .join(Group, Group.id == student_groups.c.group_id)
        .where(Group.teacher_id == current_teacher.id)
        .scalar_subquery()
    )
    students_res = await db.execute(
        select(Student)
        .where(Student.id.in_(teacher_student_ids_sq))
        .order_by(Student.full_name)
    )
    students = students_res.scalars().all()

    student_ids = [s.id for s in students]
    if not student_ids:
        return []

    sa_res = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id.in_(student_ids))
        .options(selectinload(StudentAchievement.achievement))
        .order_by(StudentAchievement.earned_at.desc())
    )
    all_sa = sa_res.scalars().all()

    # Group by student
    by_student: dict[int, list] = {s.id: [] for s in students}
    for sa in all_sa:
        if sa.achievement is None:
            continue
        by_student[sa.student_id].append(AchievementBrief(
            id=sa.achievement_id,
            name=sa.achievement.name,
            icon=sa.achievement.icon or "🏆",
            category=sa.achievement.category,
            points_reward=sa.achievement.points_reward or 0,
            earned_at=sa.earned_at,
        ))

    result = [
        StudentAchievementOverview(
            student_id=s.id,
            username=s.username,
            full_name=s.full_name,
            avatar_url=s.avatar_url,
            total_points=s.total_points or 0,
            achievement_count=len(by_student[s.id]),
            achievements=by_student[s.id],
        )
        for s in students
    ]

    result.sort(key=lambda x: x.achievement_count, reverse=True)
    return result
