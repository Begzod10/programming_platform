from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db
from app.services import lesson_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead

router = APIRouter()


@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(course_id: int, db: AsyncSession = Depends(get_db)):
    return await lesson_service.get_lessons_by_course(db, course_id)


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(course_id: int, lesson_id: int, db: AsyncSession = Depends(get_db)):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return lesson


@router.post("/courses/{course_id}/lessons", response_model=LessonRead)
async def create_lesson(course_id: int, data: LessonCreate, db: AsyncSession = Depends(get_db)):
    return await lesson_service.create_lesson(db, course_id, data)


@router.put("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def update_lesson(course_id: int, lesson_id: int, data: LessonUpdate, db: AsyncSession = Depends(get_db)):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return await lesson_service.update_lesson(db, lesson_id, data)


@router.delete("/courses/{course_id}/lessons/{lesson_id}")
async def delete_lesson(course_id: int, lesson_id: int, db: AsyncSession = Depends(get_db)):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await lesson_service.delete_lesson(db, lesson_id)
    return {"message": "Dars o'chirildi"}