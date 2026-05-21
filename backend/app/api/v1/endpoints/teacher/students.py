from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, get_current_instructor
from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.models.user import Student
from app.models.group import Group
from app.services.student_service import StudentService

router = APIRouter()


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


@router.get("/", response_model=List[UserRead])
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
