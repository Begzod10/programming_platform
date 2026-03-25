from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.course import Course
from app.models.user import Student
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_courses(
            self,
            skip: int = 0,
            limit: int = 100,
            search: Optional[str] = None,
            difficulty_level: Optional[str] = None,
            is_active: Optional[bool] = None,
            instructor_id: Optional[int] = None
    ) -> List[Course]:
        """Barcha kurslar (filter bilan)"""
        query = select(Course).options(
            selectinload(Course.lessons),
            selectinload(Course.students)
        )

        if search:
            query = query.where(or_(
                Course.title.ilike(f"%{search}%"),
                Course.description.ilike(f"%{search}%")
            ))

        if difficulty_level:
            query = query.where(Course.difficulty_level == difficulty_level)

        if is_active is not None:
            query = query.where(Course.is_active == is_active)

        if instructor_id:
            query = query.where(Course.instructor_id == instructor_id)

        query = query.order_by(Course.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """ID bo'yicha kurs"""
        query = (
            select(Course)
            .options(selectinload(Course.students), selectinload(Course.lessons))
            .where(Course.id == course_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_course(self, course_data: CourseCreate, instructor_id: int) -> Course:
        """Yangi kurs yaratish"""
        data = course_data.model_dump()
        data["instructor_id"] = instructor_id

        new_course = Course(**data)
        self.db.add(new_course)
        await self.db.commit()
        await self.db.refresh(new_course)

        return new_course

    async def update_course(
            self,
            course_id: int,
            course_data: CourseUpdate,
            instructor_id: int
    ) -> Optional[Course]:
        """Kursni yangilash"""
        course = await self.get_course_by_id(course_id)

        if not course:
            return None

        if course.instructor_id != instructor_id:
            raise HTTPException(status_code=403, detail="Faqat o'z kursingizni tahrirlashingiz mumkin")

        for key, value in course_data.model_dump(exclude_unset=True).items():
            setattr(course, key, value)

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def delete_course(self, course_id: int, instructor_id: int) -> bool:
        """Kursni o'chirish"""
        course = await self.get_course_by_id(course_id)

        if not course:
            return False

        if course.instructor_id != instructor_id:
            raise HTTPException(status_code=403, detail="Faqat o'z kursingizni o'chirishingiz mumkin")

        await self.db.delete(course)
        await self.db.commit()

        return True

    async def enroll_student(self, course_id: int, student_id: int) -> bool:
        """Studentni kursga yozish"""
        course = await self.get_course_by_id(course_id)

        if not course or not course.is_active:
            raise HTTPException(status_code=404, detail="Kurs topilmadi yoki faol emas")

        student_result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.enrolled_courses))
            .where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            raise HTTPException(status_code=404, detail="Student topilmadi")

        if course in student.enrolled_courses:
            raise HTTPException(status_code=400, detail="Allaqachon yozilgansiz")

        student.enrolled_courses.append(course)
        await self.db.commit()

        return True

    async def unenroll_student(self, course_id: int, student_id: int) -> bool:
        """Studentni kursdan chiqarish"""
        course = await self.get_course_by_id(course_id)

        if not course:
            raise HTTPException(status_code=404, detail="Kurs topilmadi")

        student_result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.enrolled_courses))
            .where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            raise HTTPException(status_code=404, detail="Student topilmadi")

        if course not in student.enrolled_courses:
            raise HTTPException(status_code=400, detail="Bu kursga yozilmagansiz")

        student.enrolled_courses.remove(course)
        await self.db.commit()

        return True

    async def get_course_count(self) -> int:
        """Umumiy kurslar soni"""
        result = await self.db.execute(select(func.count(Course.id)))
        return result.scalar()