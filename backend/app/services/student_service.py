from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import Student
from app.models.ranking import Ranking
from app.models.project import Project  # ✅ Project modelini import qiling
from app.models.course import Course
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.group import Group
from app.models.lesson import Lesson, LessonCompletion
from app.schemas.user import UserUpdate


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_students_by_teacher(
            self,
            teacher_id: int,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
    ) -> List[dict]:
        query = (
            select(Student)
            .options(
                selectinload(Student.groups),
                selectinload(Student.enrolled_courses),
            )
            .join(Student.groups)
            .where(Group.teacher_id == teacher_id)
            .distinct()
        )
        
        if search:
            query = query.where(
                or_(
                    Student.username.ilike(f"%{search}%"),
                    Student.full_name.ilike(f"%{search}%"),
                    Student.email.ilike(f"%{search}%"),
                    Student.phone.ilike(f"%{search}%"),
                    Student.surname.ilike(f"%{search}%"),
                )
            )
            
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Student.id.desc()))
        students = result.scalars().all()
        return [await self.build_teacher_progress_dto(student) for student in students]

    async def get_teacher_students_progress(
            self,
            teacher_id: int,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
    ) -> dict:
        query = (
            select(Student)
            .options(
                selectinload(Student.groups),
                selectinload(Student.enrolled_courses),
            )
            .join(Student.groups)
            .where(Group.teacher_id == teacher_id)
            .distinct()
        )

        if search:
            query = query.where(
                or_(
                    Student.username.ilike(f"%{search}%"),
                    Student.full_name.ilike(f"%{search}%"),
                    Student.email.ilike(f"%{search}%"),
                    Student.phone.ilike(f"%{search}%"),
                    Student.surname.ilike(f"%{search}%"),
                )
            )

        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0
        result = await self.db.execute(
            query.order_by(Student.id.desc()).offset(skip).limit(limit)
        )
        students = result.scalars().all()

        return {
            "total": total,
            "items": [await self.build_teacher_progress_dto(student) for student in students],
        }

    async def get_teacher_student_progress(
            self,
            teacher_id: int,
            student_id: int,
    ) -> dict:
        result = await self.db.execute(
            select(Student)
            .options(
                selectinload(Student.groups),
                selectinload(Student.enrolled_courses),
            )
            .join(Student.groups)
            .where(Student.id == student_id, Group.teacher_id == teacher_id)
            .limit(1)
        )
        student = result.scalars().first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student topilmadi yoki sizning guruhingizda emas",
            )

        return await self.build_teacher_progress_dto(student, include_detail=True)

    async def build_teacher_progress_dto(
            self,
            student: Student,
            include_detail: bool = False,
    ) -> dict:
        courses = await self._get_student_courses_for_progress(student)
        course_items = [
            await self._build_course_progress_dto(course, student.id)
            for course in courses
        ]

        average_progress = 0
        if course_items:
            average_progress = round(
                sum(item["progress_percentage"] for item in course_items) / len(course_items)
            )

        groups = list(student.groups or [])
        data = {
            "student_id": student.id,
            "username": student.username,
            "email": student.email,
            "full_name": student.full_name,
            "phone": student.phone,
            "avatar_url": student.avatar_url,
            "balance": student.balance or 0,
            "current_level": (
                student.current_level.value
                if hasattr(student.current_level, "value")
                else str(student.current_level)
            ),
            "total_points": student.total_points or 0,
            "global_rank": student.global_rank,
            "group_ids": [group.id for group in groups],
            "group_names": [group.name for group in groups if group.name],
            "course_ids": [course.id for course in courses],
            "course_titles": [course.title for course in courses],
            "courses_count": len(course_items),
            "average_progress": average_progress,
            "courses": course_items,
        }

        if include_detail:
            data.update({
                "enrollment_date": student.enrollment_date,
                "created_at": student.created_at,
                "is_active": student.is_active,
            })

        return data

    async def _get_student_courses_for_progress(self, student: Student) -> List[Course]:
        courses_by_id = {
            course.id: course
            for course in (student.enrolled_courses or [])
        }

        completed_courses_result = await self.db.execute(
            select(Course)
            .join(Lesson, Lesson.course_id == Course.id)
            .join(LessonCompletion, LessonCompletion.lesson_id == Lesson.id)
            .where(
                LessonCompletion.student_id == student.id,
                Lesson.is_active == True,
            )
            .distinct()
        )

        for course in completed_courses_result.scalars().all():
            courses_by_id[course.id] = course

        return sorted(courses_by_id.values(), key=lambda course: course.id, reverse=True)

    async def _build_course_progress_dto(self, course: Course, student_id: int) -> dict:
        total_lessons = await self.db.scalar(
            select(func.count(Lesson.id)).where(
                Lesson.course_id == course.id,
                Lesson.is_active == True,
            )
        ) or 0

        completed_lessons = await self.db.scalar(
            select(func.count(LessonCompletion.id))
            .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
            .where(
                Lesson.course_id == course.id,
                Lesson.is_active == True,
                LessonCompletion.student_id == student_id,
            )
        ) or 0

        earned_points = await self.db.scalar(
            select(func.coalesce(func.sum(ExerciseSubmission.score), 0))
            .join(Exercise, ExerciseSubmission.exercise_id == Exercise.id)
            .join(Lesson, Exercise.lesson_id == Lesson.id)
            .where(
                Lesson.course_id == course.id,
                ExerciseSubmission.student_id == student_id,
            )
        ) or 0

        progress_percentage = 0
        if total_lessons:
            progress_percentage = int(min(completed_lessons, total_lessons) / total_lessons * 100)

        return {
            "course_id": course.id,
            "course_title": course.title,
            "difficulty_level": course.difficulty_level,
            "progress_percentage": progress_percentage,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "earned_points": int(earned_points),
            "max_points": course.max_points,
            "is_completed": total_lessons > 0 and completed_lessons >= total_lessons,
        }

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
        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Student.id.desc()))
        # Scalars natijasini listga o'girib qaytarish PEP 8 uchun yaxshi
        return list(result.scalars().all())

    async def get_student_by_id(self, student_id: int) -> Student:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student (ID: {student_id}) topilmadi"
            )
        return student

    async def update_student(self, student_id: int, data: UserUpdate) -> Student:
        student = await self.get_student_by_id(student_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete_student(self, student_id: int) -> bool:
        """Studentni o'chirish (Ranking va Projectlar bilan birga)"""

        # 1. Avval studentga bog'liq rankingni o'chiramiz
        await self.db.execute(
            delete(Ranking).where(Ranking.student_id == student_id)
        )

        # 2. Studentga bog'liq loyihalarni (Project) o'chiramiz
        # (Bu qator IntegrityError: NotNullViolationError ni tuzatadi)
        await self.db.execute(
            delete(Project).where(Project.student_id == student_id)
        )

        # 3. Studentni qidirib topamiz
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            return False

        # 4. Studentning o'zini o'chiramiz
        await self.db.delete(student)
        await self.db.commit()
        return True

    async def deactivate_student(self, student_id: int) -> Student:
        student = await self.get_student_by_id(student_id)
        student.is_active = False
        await self.db.commit()
        await self.db.refresh(student)
        return student
