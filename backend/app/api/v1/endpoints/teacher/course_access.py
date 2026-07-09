"""Teacher endpoints for assigning / unassigning student access to courses.

Hard-lock policy: students only see lessons of courses they're enrolled in.
This module lets the course instructor grant or revoke that enrollment, in bulk
or per-student, optionally scoped to one of their own groups.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_instructor
from app.models.course import Course, student_courses
from app.models.group import Group, student_groups
from app.models.user import Student, UserRole

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Schemas (kept local — only used by this module)
# ─────────────────────────────────────────────────────────────────────────────

class GroupBrief(BaseModel):
    id: int
    name: str


class StudentAccess(BaseModel):
    """One student in the teacher's roster, with current course-access state."""
    id: int
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    is_enrolled: bool
    groups: List[GroupBrief] = Field(default_factory=list)


class StudentsAccessResponse(BaseModel):
    course_id: int
    total: int
    enrolled_count: int
    items: List[StudentAccess]


class AssignRequest(BaseModel):
    """Bulk assign or unassign by individual student ids or whole groups."""
    student_ids: List[int] = Field(default_factory=list, max_length=1000)
    group_ids: List[int] = Field(default_factory=list, max_length=200)


class AssignResponse(BaseModel):
    added: int
    skipped: int


class UnassignResponse(BaseModel):
    removed: int


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _get_course(db: AsyncSession, course_id: int) -> Course:
    """Fetch course by id — any teacher may manage student enrollment."""
    res = await db.execute(select(Course).where(Course.id == course_id))
    course = res.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Kurs topilmadi")
    return course


async def _teacher_group_ids(db: AsyncSession, teacher_id: int) -> List[int]:
    res = await db.execute(select(Group.id).where(Group.teacher_id == teacher_id))
    return [row[0] for row in res.all()]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{course_id}/students", response_model=StudentsAccessResponse)
async def list_course_students(
    course_id: int,
    group_id: Optional[int] = Query(None, description="Restrict to one group"),
    only_enrolled: bool = Query(False, description="Return only currently enrolled"),
    search: Optional[str] = Query(None, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """List students the teacher can manage for this course.

    Scope: students enrolled in any group taught by the current teacher, plus
    students already enrolled in the course (so a teacher can revoke access
    even for someone who left the group). Each item carries `is_enrolled` so
    the UI can render a checkbox list with the current state pre-filled.
    """
    course = await _get_course(db, course_id)
    teacher_group_ids = await _teacher_group_ids(db, current_teacher.id)

    if group_id is not None and group_id not in teacher_group_ids:
        raise HTTPException(403, "Bu guruh sizniki emas")

    # All students enrolled in this course (used only for is_enrolled flags).
    enrolled_q = (
        select(Student.id)
        .join(student_courses, student_courses.c.student_id == Student.id)
        .where(student_courses.c.course_id == course.id)
    )
    enrolled_ids = {row[0] for row in (await db.execute(enrolled_q)).all()}

    # Roster pool — strictly the current teacher's own students.
    # We never merge in global enrolled_ids because that would leak the other
    # teacher's students (who may be enrolled in the same shared course).
    roster_q = (
        select(Student.id)
        .join(student_groups, student_groups.c.student_id == Student.id)
        .where(Student.role == UserRole.student)
    )
    if group_id is not None:
        roster_q = roster_q.where(student_groups.c.group_id == group_id)
    elif teacher_group_ids:
        roster_q = roster_q.where(student_groups.c.group_id.in_(teacher_group_ids))
    else:
        roster_q = roster_q.where(False)  # teacher has no groups → empty pool

    roster_ids = {row[0] for row in (await db.execute(roster_q)).all()}
    pool_ids = roster_ids  # only show this teacher's own students

    if only_enrolled:
        pool_ids = pool_ids & enrolled_ids
    # enrolled_count: how many of THIS teacher's students are enrolled
    teacher_enrolled_count = len(enrolled_ids & roster_ids)
    if not pool_ids:
        return StudentsAccessResponse(
            course_id=course.id, total=0, enrolled_count=teacher_enrolled_count, items=[]
        )

    stmt = (
        select(Student)
        .options(selectinload(Student.groups))
        .where(Student.id.in_(pool_ids))
        .order_by(Student.full_name.asc().nullslast(), Student.id.asc())
    )
    if search:
        like = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            func.lower(func.coalesce(Student.full_name, "")).like(like)
            | func.lower(func.coalesce(Student.username, "")).like(like)
            | func.lower(func.coalesce(Student.email, "")).like(like)
        )

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
    rows = (await db.execute(stmt.offset(skip).limit(limit))).scalars().all()

    items = [
        StudentAccess(
            id=s.id,
            full_name=s.full_name,
            username=s.username,
            email=s.email,
            is_enrolled=s.id in enrolled_ids,
            groups=[
                GroupBrief(id=g.id, name=g.name)
                for g in s.groups
                if g.teacher_id == current_teacher.id
            ],
        )
        for s in rows
    ]

    return StudentsAccessResponse(
        course_id=course.id,
        total=total,
        enrolled_count=teacher_enrolled_count,
        items=items,
    )


@router.post(
    "/{course_id}/students",
    response_model=AssignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_students(
    course_id: int,
    payload: AssignRequest,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Grant access to a set of students and/or whole groups."""
    course = await _get_course(db, course_id)
    teacher_group_ids = set(await _teacher_group_ids(db, current_teacher.id))

    bad_groups = [g for g in payload.group_ids if g not in teacher_group_ids]
    if bad_groups:
        raise HTTPException(403, f"Sizning guruhingiz emas: {bad_groups}")

    target_ids: set[int] = set(payload.student_ids)
    if payload.group_ids:
        gres = await db.execute(
            select(student_groups.c.student_id).where(
                student_groups.c.group_id.in_(payload.group_ids)
            )
        )
        target_ids.update(row[0] for row in gres.all())

    if not target_ids:
        return AssignResponse(added=0, skipped=0)

    # Filter to students that actually exist and have student role.
    real_q = await db.execute(
        select(Student.id).where(
            Student.id.in_(target_ids),
            Student.role == UserRole.student,
        )
    )
    real_ids = {row[0] for row in real_q.all()}

    # Skip the ones already enrolled.
    already_q = await db.execute(
        select(student_courses.c.student_id).where(
            student_courses.c.course_id == course.id,
            student_courses.c.student_id.in_(real_ids),
        )
    )
    already = {row[0] for row in already_q.all()}
    to_add = real_ids - already

    if to_add:
        await db.execute(
            student_courses.insert(),
            [{"student_id": sid, "course_id": course.id} for sid in to_add],
        )
        await db.commit()

    return AssignResponse(added=len(to_add), skipped=len(target_ids) - len(to_add))


@router.delete(
    "/{course_id}/students/{student_id}",
    response_model=UnassignResponse,
)
async def unassign_student(
    course_id: int,
    student_id: int,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a single student's access."""
    course = await _get_course(db, course_id)

    res = await db.execute(
        student_courses.delete().where(
            and_(
                student_courses.c.course_id == course.id,
                student_courses.c.student_id == student_id,
            )
        )
    )
    await db.commit()
    return UnassignResponse(removed=res.rowcount or 0)
