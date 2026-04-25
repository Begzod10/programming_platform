from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import Optional, List

from app.models.lesson import Lesson, LessonCompletion
from app.models.user import Student
from app.schemas.lesson import LessonCreate, LessonUpdate
from sqlalchemy.orm import selectinload



async def get_lessons_by_course(db: AsyncSession, course_id: int) -> List[Lesson]:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id, Lesson.is_active == True)
        .order_by(Lesson.order)
        .options(selectinload(Lesson.exercises))
    )
    return result.scalars().all()


async def get_lesson_by_id(db: AsyncSession, lesson_id: int) -> Optional[Lesson]:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(selectinload(Lesson.exercises))
    )
    return result.scalar_one_or_none()


async def create_lesson(db: AsyncSession, course_id: int, data: LessonCreate) -> Lesson:
    new_lesson = Lesson(**data.dict(), course_id=course_id)
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)

    # Mashqlarni (exercises) ham yuklab qaytarish uchun qaytadan select qilamiz
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == new_lesson.id)
        .options(selectinload(Lesson.exercises))
    )
    return result.scalar_one()


async def update_lesson(db: AsyncSession, lesson_id: int, data: LessonUpdate) -> Optional[Lesson]:
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(lesson, key, value)
    await db.commit()

    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(selectinload(Lesson.exercises))
    )
    return result.scalar_one()


async def delete_lesson(db: AsyncSession, lesson_id: int) -> bool:
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        return False
    await db.delete(lesson)
    await db.commit()
    return True


async def complete_lesson(db: AsyncSession, lesson_id: int, student_id: int) -> dict:
    """Darsni tugatish va ball berish"""

    # Dars mavjudligini tekshirish
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    # Allaqachon tugatilganmi?
    existing = await db.execute(
        select(LessonCompletion).where(
            and_(
                LessonCompletion.student_id == student_id,
                LessonCompletion.lesson_id == lesson_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dars allaqachon tugatilgan")

    # LessonCompletion yaratish
    completion = LessonCompletion(student_id=student_id, lesson_id=lesson_id)
    db.add(completion)

    # Studentga ball qo'shish (Ranking ham yangilanadi)
    points_earned = 0
    if student_id and hasattr(lesson, "points_reward") and lesson.points_reward:
        from app.services.ranking_service import RankingService
        ranking_service = RankingService(db)
        await ranking_service.add_points_to_student(student_id, lesson.points_reward)
        points_earned = lesson.points_reward

    # Kurs progressini hisoblash
    total_result = await db.execute(
        select(Lesson).where(
            Lesson.course_id == lesson.course_id,
            Lesson.is_active == True
        )
    )
    total_lessons = total_result.scalars().all()

    completed_result = await db.execute(
        select(LessonCompletion).where(
            and_(
                LessonCompletion.student_id == student_id,
                LessonCompletion.lesson_id.in_([l.id for l in total_lessons])
            )
        )
    )
    completed_count = len(completed_result.scalars().all())
    total_count = len(total_lessons)
    progress = int((completed_count / total_count) * 100) if total_count > 0 else 0

    # Student total points olish
    student_res = await db.execute(select(Student).where(Student.id == student_id))
    student = student_res.scalar_one_or_none()

    await db.commit()  # Barcha o'zgarishlarni saqlaymiz

    return {
        "message": "Dars tugatildi",
        "total_lessons": total_count,
        "completed_lessons": completed_count,
        "progress_percentage": progress,
        "points_earned": points_earned,
        "total_points": student.total_points if student else 0,
        "course_id": lesson.course_id
    }
