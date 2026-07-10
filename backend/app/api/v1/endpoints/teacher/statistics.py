from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.dependencies import get_db, get_current_instructor
from app.models.user import Student, UserRole, StudentLevel
from app.models.group import Group, student_groups
from app.models.project import Project
from app.models.submission import Submission

router = APIRouter()


def _teacher_students_subq(teacher_id: int):
    """Subquery: IDs of students that belong to any group owned by teacher_id."""
    return (
        select(student_groups.c.student_id)
        .join(Group, Group.id == student_groups.c.group_id)
        .where(Group.teacher_id == teacher_id)
        .scalar_subquery()
    )


@router.get("/statistics")
async def get_teacher_statistics(
        db: AsyncSession = Depends(get_db),
        current_teacher: Student = Depends(get_current_instructor)
):
    teacher_id = current_teacher.id
    student_ids_sq = _teacher_students_subq(teacher_id)

    now = datetime.now(timezone.utc)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = this_month_start
    two_months_ago_start = (last_month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Students in teacher's groups only
    total_students = await db.scalar(
        select(func.count()).select_from(Student).where(
            Student.role == UserRole.student,
            Student.id.in_(student_ids_sq),
        )
    )

    # Groups owned by this teacher
    active_groups = await db.scalar(
        select(func.count()).select_from(Group).where(Group.teacher_id == teacher_id)
    )

    # Average points — teacher's students only
    avg_points = await db.scalar(
        select(func.avg(Student.total_points)).where(
            Student.role == UserRole.student,
            Student.id.in_(student_ids_sq),
        )
    )

    # Advanced students — teacher's students only
    advanced_count = await db.scalar(
        select(func.count()).select_from(Student).where(
            Student.role == UserRole.student,
            Student.total_points >= 5000,
            Student.id.in_(student_ids_sq),
        )
    )

    # Checked / pending works — projects from teacher's students only
    checked_works = await db.scalar(
        select(func.count()).select_from(Project).where(
            Project.status.in_(["Reviewed", "Approved"]),
            Project.student_id.in_(student_ids_sq),
        )
    )

    pending_works = await db.scalar(
        select(func.count()).select_from(Project).where(
            Project.status == "Submitted",
            Project.student_id.in_(student_ids_sq),
        )
    )

    this_month_checked = await db.scalar(
        select(func.count()).select_from(Project).where(
            Project.status.in_(["Reviewed", "Approved"]),
            Project.updated_at >= this_month_start,
            Project.student_id.in_(student_ids_sq),
        )
    )

    last_month_checked = await db.scalar(
        select(func.count()).select_from(Project).where(
            Project.status.in_(["Reviewed", "Approved"]),
            Project.updated_at >= last_month_start,
            Project.updated_at < last_month_end,
            Project.student_id.in_(student_ids_sq),
        )
    )

    two_months_ago_checked = await db.scalar(
        select(func.count()).select_from(Project).where(
            Project.status.in_(["Reviewed", "Approved"]),
            Project.updated_at >= two_months_ago_start,
            Project.updated_at < last_month_start,
            Project.student_id.in_(student_ids_sq),
        )
    )

    def calc_growth(current, previous):
        c = current or 0
        p = previous or 0
        if p < 3:
            return "N/A"
        growth = round(((c - p) / p) * 100)
        growth = max(-999, min(999, growth))
        return f"+{growth}%" if growth >= 0 else f"{growth}%"

    this_month_growth = calc_growth(this_month_checked, last_month_checked)
    last_month_growth = calc_growth(last_month_checked, two_months_ago_checked)

    avg_growth_val = round(((this_month_checked or 0) + (last_month_checked or 0)) / 2)
    prev_avg_val   = round(((last_month_checked or 0) + (two_months_ago_checked or 0)) / 2)
    average_growth = calc_growth(avg_growth_val, prev_avg_val)

    # Weekly activity (last 7 days) — teacher's students only
    weekly_activity = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = await db.scalar(
            select(func.count()).select_from(Project).where(
                Project.reviewed_at >= day_start,
                Project.reviewed_at < day_end,
                Project.student_id.in_(student_ids_sq),
            )
        )
        weekly_activity.append({
            "day": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][day.weekday()],
            "value": count or 0
        })

    # Level breakdown — teacher's students only
    beginner_count = await db.scalar(
        select(func.count()).select_from(Student).where(
            Student.role == UserRole.student,
            Student.current_level == StudentLevel.Beginner,
            Student.id.in_(student_ids_sq),
        )
    )
    intermediate_count = await db.scalar(
        select(func.count()).select_from(Student).where(
            Student.role == UserRole.student,
            Student.current_level == StudentLevel.Intermediate,
            Student.id.in_(student_ids_sq),
        )
    )

    # Top 5 students — teacher's students only
    top_students_rows = (await db.execute(
        select(Student.id, Student.full_name, Student.username, Student.total_points, Student.current_level)
        .where(
            Student.role == UserRole.student,
            Student.is_active == True,
            Student.id.in_(student_ids_sq),
        )
        .order_by(Student.total_points.desc())
        .limit(5)
    )).all()

    top_students = [
        {
            "id": r.id,
            "name": r.full_name or r.username or f"Student #{r.id}",
            "points": r.total_points,
            "level": r.current_level.value if r.current_level else "Beginner",
        }
        for r in top_students_rows
    ]

    # Grade distribution — teacher's students only
    grade_rows = (await db.execute(
        select(Project.grade, func.count().label("cnt"))
        .where(
            Project.grade.isnot(None),
            Project.student_id.in_(student_ids_sq),
        )
        .group_by(Project.grade)
        .order_by(Project.grade)
    )).all()
    grade_distribution = [{"grade": r.grade, "count": r.cnt} for r in grade_rows]

    return {
        "total_students": total_students or 0,
        "active_groups": active_groups or 0,
        "average_points": round(float(avg_points or 0), 1),
        "advanced_students": advanced_count or 0,
        "checked_works": checked_works or 0,
        "pending_works": pending_works or 0,
        "dynamics": [
            {"label": "Этот месяц", "value": this_month_growth},
            {"label": "Прошлый месяц", "value": last_month_growth},
            {"label": "Средний рост", "value": average_growth},
        ],
        "weekly_activity": weekly_activity,
        "level_breakdown": {
            "beginner": beginner_count or 0,
            "intermediate": intermediate_count or 0,
            "advanced": advanced_count or 0,
        },
        "top_students": top_students,
        "grade_distribution": grade_distribution,
    }


@router.get("/projects")
async def get_teacher_projects(
        status: Optional[str] = Query(None, description="Filter by status: Submitted, Approved, Rejected, Under Review"),
        skip: int = Query(0, ge=0),
        limit: int = Query(200, ge=1, le=500),
        db: AsyncSession = Depends(get_db),
        current_teacher: Student = Depends(get_current_instructor),
):
    """All projects from the current teacher's own students, optionally filtered by status."""
    student_ids_sq = _teacher_students_subq(current_teacher.id)

    q = (
        select(Project)
        .options(selectinload(Project.student))
        .where(Project.student_id.in_(student_ids_sq))
    )
    if status:
        q = q.where(Project.status == status)

    q = q.order_by(Project.submitted_at.desc().nullslast(), Project.created_at.desc())
    q = q.offset(skip).limit(limit)

    rows = (await db.execute(q)).scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "points_earned": p.points_earned,
            "grade": p.grade,
            "github_url": p.github_url,
            "live_demo_url": p.live_demo_url,
            "description": p.description,
            "difficulty_level": p.difficulty_level,
            "instructor_feedback": p.instructor_feedback,
            "submitted_at": p.submitted_at.isoformat() if p.submitted_at else None,
            "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
            "project_files": p.project_files,
            "ai_strengths": p.ai_strengths,
            "ai_improvements": p.ai_improvements,
            "ai_bugs": p.ai_bugs,
            "student": {
                "id": p.student.id,
                "username": p.student.username,
                "full_name": p.student.full_name,
                "email": p.student.email,
                "avatar_url": p.student.avatar_url,
            } if p.student else None,
        }
        for p in rows
    ]
