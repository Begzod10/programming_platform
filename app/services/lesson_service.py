from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import Optional, List
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


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
    lesson = Lesson(**data.dict(), course_id=course_id)
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    # exercises ni ham yuklaymiz
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson.id)
        .options(selectinload(Lesson.exercises))
    )
    return result.scalar_one()


async def update_lesson(db: AsyncSession, lesson_id: int, data: LessonUpdate) -> Optional[Lesson]:
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
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
