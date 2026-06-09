import re
import unicodedata
from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.category import Category
from app.models.course import Course
from app.models.user import Student
from app.schemas.course import CourseCreate, CourseUpdate
from app.models.lesson import Lesson, LessonCompletion


def _slugify(value: str) -> str:
    """Plain ASCII slug — collapses non-alphanumerics into single dashes."""
    norm = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    norm = re.sub(r"[^a-zA-Z0-9]+", "-", norm).strip("-").lower()
    return norm or "kat"


async def resolve_category(
    db: AsyncSession,
    *,
    category_id: Optional[int],
    category_name: Optional[str],
    created_by_id: Optional[int] = None,
) -> Optional[int]:
    """Return a category id, creating one by name if needed.

    Priority: explicit category_id wins. Otherwise the name is matched
    case-insensitively; if no match, a new row is inserted (auto-create).
    Returns None if neither input is provided — uncategorized is allowed.
    """
    if category_id is not None:
        res = await db.execute(select(Category.id).where(Category.id == category_id))
        if res.scalar_one_or_none() is None:
            raise HTTPException(404, "Kategoriya topilmadi")
        return category_id

    if not category_name:
        return None
    name = category_name.strip()
    if not name:
        return None

    res = await db.execute(
        select(Category).where(func.lower(Category.name) == name.lower())
    )
    existing = res.scalar_one_or_none()
    if existing:
        return existing.id

    base_slug = _slugify(name)
    slug = base_slug
    suffix = 2
    # Slug collisions are rare but possible (e.g. two names that ASCII to
    # the same value). Append a counter rather than mutating the name.
    while True:
        clash = await db.execute(select(Category.id).where(Category.slug == slug))
        if clash.scalar_one_or_none() is None:
            break
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    new_cat = Category(name=name, slug=slug, created_by_id=created_by_id)
    db.add(new_cat)
    await db.flush()
    return new_cat.id


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

        query = query.order_by(Course.display_order.asc(), Course.id.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """ID bo'yicha kurs"""
        query = (
            select(Course)
            .options(
                selectinload(Course.students),
                selectinload(Course.lessons),
                selectinload(Course.category),
            )
            .where(Course.id == course_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def validate_course_integrity(self, course: Course):
        """Kurs butunligini tekshirish"""
        pass

    async def create_course(self, course_data: CourseCreate, instructor_id: int) -> Course:
        """Yangi kurs yaratish va unga mos achievement (sertifikat) qo'shish"""
        data = course_data.model_dump()
        data["instructor_id"] = instructor_id

        if data.get("max_points", 0) <= 0:
            raise HTTPException(
                status_code=400,
                detail="Kursning maksimal balli 0 dan katta bo'lishi kerak"
            )

        category_name = data.pop("category_name", None)
        category_id = data.pop("category_id", None)
        data["category_id"] = await resolve_category(
            self.db,
            category_id=category_id,
            category_name=category_name,
            created_by_id=instructor_id,
        )

        new_course = Course(**data)
        self.db.add(new_course)
        await self.db.flush()
        await self.db.refresh(new_course)

        from app.services import achievement_service
        await achievement_service.create_achievement(
            self.db,
            name=f"{new_course.title}",
            description=(
                f"Tabriklaymiz! Siz '{new_course.title}' kursini "
                f"muvaffaqiyatli yakunladingiz va sertifikatga ega bo'ldingiz."
            ),
            badge_image_url="/static/default_badge.png",
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
            raise HTTPException(
                status_code=403,
                detail="Faqat o'z kursingizni tahrirlashingiz mumkin"
            )

        update_data = course_data.model_dump(exclude_unset=True)
        old_title = course.title
        new_title = update_data.get("title")

        # Category fields are resolved together: explicit id beats name,
        # and a non-empty name auto-creates if missing. Empty name + no id
        # clears the assignment so the course becomes uncategorized.
        if "category_id" in update_data or "category_name" in update_data:
            cat_id = update_data.pop("category_id", None)
            cat_name = update_data.pop("category_name", None)
            update_data["category_id"] = await resolve_category(
                self.db,
                category_id=cat_id,
                category_name=cat_name,
                created_by_id=instructor_id,
            )

        for key, value in update_data.items():
            setattr(course, key, value)

        await self.validate_course_integrity(course)

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
            raise HTTPException(
                status_code=403,
                detail="Faqat o'z kursingizni o'chirishingiz mumkin"
            )
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

    # ─────────────────────────────────────────────────────────────────────────
    #  KURS PROGRESS HISOBLASH
    #
    #  Qoida (oddiy va to'g'ri):
    #    course_progress = tugatilgan_lesson_soni / jami_faol_lesson_soni × 100
    #
    #  Misol — 2 ta lesson:
    #    0 tugatilgan → 0/2 × 100 = 0%
    #    1 tugatilgan → 1/2 × 100 = 50%
    #    2 tugatilgan → 2/2 × 100 = 100%
    #
    #  Misol — 4 ta lesson:
    #    1 tugatilgan → 1/4 × 100 = 25%
    #    3 tugatilgan → 3/4 × 100 = 75%
    #
    #  ESLATMA: exercises (mashqlar) progress ga QO'SHILMAYDI.
    #  Exercises alohida endpoint orqali ko'rsatiladi.
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def calc_progress(db: AsyncSession, course_id: int, student_id: int) -> int:
        """
        Kurs progressini hisoblash va int (0-100) qaytarish.
        Faqat faol (is_active=True) lessonlar hisobga olinadi.
        """
        # Jami faol lessonlar
        total_res = await db.execute(
            select(func.count(Lesson.id)).where(
                Lesson.course_id == course_id,
                Lesson.is_active == True
            )
        )
        total = total_res.scalar() or 0
        if total == 0:
            return 0

        # Tugatilgan lessonlar (LessonCompletion jadvalidan)
        completed_res = await db.execute(
            select(func.count(LessonCompletion.id))
            .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
            .where(
                Lesson.course_id == course_id,
                Lesson.is_active == True,
                LessonCompletion.student_id == student_id
            )
        )
        completed = completed_res.scalar() or 0

        # min() — completed hech qachon total dan oshmaydi (xavfsizlik uchun)
        return int(min(completed, total) / total * 100)

    @staticmethod
    async def build_dto(db: AsyncSession, course: Course, student_id: Optional[int] = None):
        """
        Kurs DTO (Data Transfer Object) ni quramiz.

        progress_percentage:
          - student_id berilgan → calc_progress() — faqat lesson completions
          - student_id yo'q (teacher/anonymous) → 0
        """
        data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor_id": course.instructor_id,
            "difficulty_level": course.difficulty_level,
            "duration_weeks": course.duration_weeks,
            "max_points": course.max_points,
            "image_url": course.image_url,
            "thumbnail_url": getattr(course, "thumbnail_url", None),
            "video_intro_url": getattr(course, "video_intro_url", None),
            "syllabus_url": getattr(course, "syllabus_url", None),
            "prerequisite_course_id": getattr(course, "prerequisite_course_id", None),
            "is_active": course.is_active,
            "is_published": course.is_published,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "instructor_name": None,
            "progress_percentage": 0,
            "lessons_count": 0,
            "students_count": 0,
            "is_enrolled": False,
            "category_id": getattr(course, "category_id", None),
            "category_name": None,
        }
        try:
            if course.category:
                data["category_name"] = course.category.name
        except Exception:
            pass

        # Instructor nomi (xavfsiz)
        try:
            if course.instructor:
                data["instructor_name"] = (
                        course.instructor.full_name or course.instructor.username
                )
        except Exception:
            pass

        # Jami faol lessonlar soni
        total_res = await db.execute(
            select(func.count(Lesson.id)).where(
                Lesson.course_id == course.id,
                Lesson.is_active == True
            )
        )
        total_lessons = total_res.scalar() or 0
        data["lessons_count"] = total_lessons

        # Talabalar soni
        from app.models.course import student_courses as sc_table
        st_res = await db.execute(
            select(func.count()).select_from(sc_table).where(
                sc_table.c.course_id == course.id
            )
        )
        data["students_count"] = st_res.scalar() or 0

        # Kurs progressi — FAQAT lesson completions asosida
        if student_id and total_lessons > 0:
            data["progress_percentage"] = await CourseService.calc_progress(
                db, course.id, student_id
            )

        # Hard-lock: instructor and enrolled students get is_enrolled=True.
        if student_id:
            if course.instructor_id == student_id:
                data["is_enrolled"] = True
            else:
                enrolled_res = await db.execute(
                    select(sc_table.c.course_id).where(
                        sc_table.c.course_id == course.id,
                        sc_table.c.student_id == student_id,
                    )
                )
                data["is_enrolled"] = enrolled_res.first() is not None

        return data
