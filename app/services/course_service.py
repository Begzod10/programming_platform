from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.course import Course
from app.models.user import Student
from app.schemas.course import CourseCreate, CourseUpdate, CourseRead
from app.models.lesson import Lesson, LessonCompletion


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
        """Yangi kurs yaratish va unga mos achievement (sertifikat) qo'shish"""
        data = course_data.model_dump()
        data["instructor_id"] = instructor_id

        new_course = Course(**data)
        self.db.add(new_course)
        await self.db.flush()  # ID olish uchun flash qilamiz, lekin commit emas hali
        await self.db.refresh(new_course)

        # 🎖 Avtomatik achievement (badge/certificate) yaratish
        from app.services import achievement_service
        await achievement_service.create_achievement(
            self.db,
            name=f"{new_course.title}",
            description=f"Tabriklaymiz! Siz '{new_course.title}' kursini muvaffaqiyatli yakunladingiz va sertifikatga ega bo'ldingiz.",
            badge_image_url="/static/default_badge.png", # Standart rasm
            points_reward=100,
            criteria_type="course_completion",
            criteria_value=1,
            course_id=new_course.id
        )

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

        update_data = course_data.model_dump(exclude_unset=True)
        old_title = course.title
        new_title = update_data.get("title")

        for key, value in update_data.items():
            setattr(course, key, value)

        # 🔄 Agar kurs nomi o'zgarsa, unga tegishli achievement nomini ham o'zgartiramiz
        if new_title and new_title != old_title:
            from app.models.achievement import Achievement
            from sqlalchemy import update as sqlalchemy_update
            await self.db.execute(
                sqlalchemy_update(Achievement)
                .where(Achievement.course_id == course.id)
                .values(name=f"{new_title}")
            )

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

    @staticmethod
    async def calc_progress(db: AsyncSession, course_id: int, student_id: int) -> int:
        total = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == course_id, Lesson.is_active == True))
        total_count = total.scalar() or 0
        if total_count == 0: return 0

        completed = await db.execute(
            select(func.count(LessonCompletion.id))
            .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
            .where(Lesson.course_id == course_id, LessonCompletion.student_id == student_id)
        )
        return int((completed.scalar() or 0) / total_count * 100)

    @staticmethod
    async def build_dto(db: AsyncSession, course: Course, student_id: Optional[int] = None):
        # 1. Asosiy ma'lumotlarni yig'amiz
        data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "difficulty_level": course.difficulty_level,
            "duration_weeks": course.duration_weeks,
            "max_points": course.max_points,
            "image_url": course.image_url,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "instructor_name": None,
            "progress_percentage": 0,
            "lessons_count": 0,
            "students_count": 0
        }

        # Instructor nomini xavfsiz olish
        try:
            if course.instructor:
                data["instructor_name"] = course.instructor.full_name or course.instructor.username
        except:
            pass

        # 2. Jami faol darslar soni
        total_stmt = select(func.count(Lesson.id)).where(
            Lesson.course_id == course.id,
            Lesson.is_active == True
        )
        total_res = await db.execute(total_stmt)
        total_count = total_res.scalar() or 0
        data["lessons_count"] = total_count

        # 3. Talabalar soni
        from app.models.course import student_courses
        st_count_stmt = select(func.count()).select_from(student_courses).where(
            student_courses.c.course_id == course.id
        )
        st_count_res = await db.execute(st_count_stmt)
        data["students_count"] = st_count_res.scalar() or 0

        if student_id and total_count > 0:
            comp_stmt = (
                select(func.count(LessonCompletion.id))
                .join(Lesson, LessonCompletion.lesson_id == Lesson.id)  # ✅ aniq join sharti
                .where(
                    Lesson.course_id == course.id,
                    Lesson.is_active == True,  # ✅ faqat faol darslar
                    LessonCompletion.student_id == student_id
                )
            )
            comp_res = await db.execute(comp_stmt)
            comp_count = comp_res.scalar() or 0

            data["progress_percentage"] = int((comp_count / total_count) * 100)
        else:
            data["progress_percentage"] = 0

        return data