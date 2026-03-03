from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.user import Student
from app.schemas.user import UserUpdate
from typing import Optional, List


async def get_student_by_id(db: AsyncSession, student_id: int) -> Optional[Student]:
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalars().first()


async def get_all_students(db: AsyncSession, skip: int = 0, limit: int = 10, search: str = None) -> List[Student]:
    query = select(Student)
    if search:
        query = query.where(
            or_(
                Student.username.ilike(f"%{search}%"),
                Student.full_name.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%")
            )
        )
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_student(db: AsyncSession, student_id: int, data: UserUpdate) -> Student:
    student = await get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student topilmadi")
    for key, value in data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(student, key, value)
    await db.commit()
    await db.refresh(student)
    return student


async def delete_student(db: AsyncSession, student_id: int) -> dict:
    student = await get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student topilmadi")
    await db.delete(student)
    await db.commit()
    return {"message": "Student o'chirildi"}
