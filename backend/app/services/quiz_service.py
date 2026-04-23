from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import List, Optional

from app.models.quiz import Quiz, Question, StudentQuizResult
from app.schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate, QuizSubmit


async def get_all_quizzes(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Quiz]:
    result = await db.execute(
        select(Quiz).where(Quiz.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    result = await db.execute(
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    return result.scalar_one_or_none()


async def create_quiz(db: AsyncSession, data: QuizCreate) -> Quiz:
    quiz = Quiz(**data.dict())
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    return quiz


async def update_quiz(db: AsyncSession, quiz_id: int, data: QuizUpdate) -> Optional[Quiz]:
    quiz = await get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(quiz, key, value)
    await db.commit()
    await db.refresh(quiz)
    return quiz


async def delete_quiz(db: AsyncSession, quiz_id: int) -> bool:
    quiz = await get_quiz_by_id(db, quiz_id)
    if not quiz:
        return False
    await db.delete(quiz)
    await db.commit()
    return True


async def add_question(db: AsyncSession, quiz_id: int, data: QuestionCreate) -> Question:
    quiz = await get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    if data.correct_answer not in ["A", "B", "C", "D"]:
        raise HTTPException(status_code=400, detail="Javob A, B, C yoki D bo'lishi kerak")
    question = Question(**data.dict(), quiz_id=quiz_id)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        return False
    await db.delete(question)
    await db.commit()
    return True


async def submit_quiz(db: AsyncSession, quiz_id: int, student_id: int, data: QuizSubmit) -> StudentQuizResult:
    quiz = await get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Test topilmadi")

    # Javoblarni tekshirish
    questions = {q.id: q for q in quiz.questions}
    correct = 0
    total = len(quiz.questions)

    for answer in data.answers:
        q = questions.get(answer.question_id)
        if q and q.correct_answer == answer.answer.upper():
            correct += 1

    score = int((correct / total) * 100) if total > 0 else 0
    passed = score >= quiz.passing_score

    result_obj = StudentQuizResult(
        student_id=student_id,
        quiz_id=quiz_id,
        score=score,
        correct_answers=correct,
        total_questions=total,
        passed=passed,
        time_spent_seconds=data.time_spent_seconds
    )
    db.add(result_obj)
    await db.commit()
    await db.refresh(result_obj)
    return result_obj


async def get_my_results(db: AsyncSession, student_id: int) -> List[StudentQuizResult]:
    result = await db.execute(
        select(StudentQuizResult).where(StudentQuizResult.student_id == student_id)
    )
    return result.scalars().all()