from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from fastapi import HTTPException, status

from app.models.user import Student
from app.schemas.user import UserUpdate


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_students(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
    ) -> List[Student]:
        query = select(Student)

        if search:
            query = query.where(
                or_(
                    Student.username.ilike(f"%{search}%"),
                    Student.full_name.ilike(f"%{search}%"),
                    Student.email.ilike(f"%{search}%"),
                )
            )

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_student_by_id(self, student_id: int) -> Student:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with id {student_id} not found",
            )
        return student

    async def get_student_by_email(self, email: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.email == email)
        )
        return result.scalar_one_or_none()

    async def get_student_by_username(self, username: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.username == username)
        )
        return result.scalar_one_or_none()

    async def update_student(self, student_id: int, data: UserUpdate) -> Student:
        student = await self.get_student_by_id(student_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete_student(self, student_id: int) -> dict:
        student = await self.get_student_by_id(student_id)
        await self.db.delete(student)
        await self.db.commit()
        return {"message": f"Student {student_id} deleted successfully"}

    async def update_avatar(self, student_id: int, avatar_url: str) -> Student:
        student = await self.get_student_by_id(student_id)
        student.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def get_student_stats(self, student_id: int) -> dict:
        student = await self.get_student_by_id(student_id)
        return {
            "id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "current_level": student.current_level,
            "total_points": student.total_points,
            "global_rank": student.global_rank,
            "is_active": student.is_active,
            "is_verified": student.is_verified,
            "enrollment_date": student.enrollment_date,
        }

    async def deactivate_student(self, student_id: int) -> Student:
        student = await self.get_student_by_id(student_id)
        student.is_active = False
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def activate_student(self, student_id: int) -> Student:
        student = await self.get_student_by_id(student_id)
        student.is_active = True
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def get_total_count(self, search: Optional[str] = None) -> int:
        query = select(func.count()).select_from(Student)

        if search:
            query = query.where(
                or_(
                    Student.username.ilike(f"%{search}%"),
                    Student.full_name.ilike(f"%{search}%"),
                    Student.email.ilike(f"%{search}%"),
                )
            )

        result = await self.db.execute(query)
        return result.scalar_one()

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

