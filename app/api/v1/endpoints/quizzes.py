from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student
from app.services import quiz_service
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizRead, QuizReadWithQuestions,
    QuestionCreate, QuestionRead, QuizSubmit, QuizResultRead
)
from app.models.user import Student

router = APIRouter()


@router.get("/", response_model=List[QuizRead])
async def get_quizzes(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Barcha testlar"""
    return await quiz_service.get_all_quizzes(db, skip, limit)


@router.get("/my-results", response_model=List[QuizResultRead])
async def my_results(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening test natijalarim"""
    return await quiz_service.get_my_results(db, current_student.id)


@router.get("/{quiz_id}", response_model=QuizReadWithQuestions)
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    """Bitta testni savollar bilan olish"""
    quiz = await quiz_service.get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    return quiz


@router.post("/", response_model=QuizRead)
async def create_quiz(data: QuizCreate, db: AsyncSession = Depends(get_db)):
    """Yangi test yaratish"""
    return await quiz_service.create_quiz(db, data)


@router.put("/{quiz_id}", response_model=QuizRead)
async def update_quiz(quiz_id: int, data: QuizUpdate, db: AsyncSession = Depends(get_db)):
    """Testni yangilash"""
    return await quiz_service.update_quiz(db, quiz_id, data)


@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    """Testni o'chirish"""
    result = await quiz_service.delete_quiz(db, quiz_id)
    if not result:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    return {"message": "Test o'chirildi"}


@router.post("/{quiz_id}/questions", response_model=QuestionRead)
async def add_question(
        quiz_id: int,
        data: QuestionCreate,
        db: AsyncSession = Depends(get_db)
):
    """Testga savol qo'shish"""
    return await quiz_service.add_question(db, quiz_id, data)


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    """Savolni o'chirish"""
    result = await quiz_service.delete_question(db, question_id)
    if not result:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    return {"message": "Savol o'chirildi"}


@router.post("/{quiz_id}/submit", response_model=QuizResultRead)
async def submit_quiz(
        quiz_id: int,
        data: QuizSubmit,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Testni topshirish"""
    return await quiz_service.submit_quiz(db, quiz_id, current_student.id, data)
