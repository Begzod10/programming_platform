import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from typing import List, Optional

from app.models.quiz import Quiz, Question, StudentQuizResult
from app.models.user import Student
from app.schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate, QuizSubmit
from app.services.ranking_service import RankingService

_GRADE_PREFIX_RE = re.compile(r"^\s*(\d{1,2})")


def student_grades(student: Student) -> set[int]:
    """Sinf raqamini guruh nomidan chiqarib olish (masalan "5-green" -> 5).

    Bazada alohida "sinf" maydoni yo'q — turon/gennis guruh nomlari doim
    "<raqam>-<rang>" shaklida keladi, shu naqshni ishlatamiz. Bir student bir
    nechta guruhda bo'lishi mumkin (masalan yil almashinuvida), shuning
    uchun to'plam qaytaramiz — har qandayi mos kelsa yetarli.
    """
    grades: set[int] = set()
    for g in getattr(student, "groups", None) or []:
        m = _GRADE_PREFIX_RE.match(g.name or "")
        if m:
            grades.add(int(m.group(1)))
    return grades


def _quiz_visible_to_grades(quiz: Quiz, grades: set[int]) -> bool:
    """grade_min/grade_max ikkalasi ham NULL bo'lsa cheklovsiz (hamma ko'radi).
    Aks holda talabaning aniqlangan sinflaridan kamida bittasi oraliqqa
    tushishi kerak. Talabaning sinfi umuman aniqlanmasa (grades bo'sh —
    gennis yoki guruhsiz), cheklangan testlar undan yashiriladi, cheklovsiz
    testlar esa ko'rinaveradi."""
    if quiz.grade_min is None and quiz.grade_max is None:
        return True
    if not grades:
        return False
    lo = quiz.grade_min if quiz.grade_min is not None else 0
    hi = quiz.grade_max if quiz.grade_max is not None else 999
    return any(lo <= g <= hi for g in grades)


async def get_all_quizzes(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        student: Optional[Student] = None,
) -> List[Quiz]:
    result = await db.execute(
        select(Quiz).where(Quiz.is_active == True).order_by(Quiz.id)
    )
    quizzes = result.scalars().all()

    if student is not None:
        grades = student_grades(student)
        quizzes = [q for q in quizzes if _quiz_visible_to_grades(q, grades)]

    return quizzes[skip: skip + limit]


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

    # Ball faqat BIRINCHI marta o'tganda beriladi — aks holda talaba bir xil
    # testni qayta-qayta topshirib ball "fermalashi" mumkin edi.
    if passed and quiz.points_reward:
        prior = await db.execute(
            select(StudentQuizResult.id).where(
                StudentQuizResult.student_id == student_id,
                StudentQuizResult.quiz_id == quiz_id,
                StudentQuizResult.passed == True,
            ).limit(1)
        )
        if prior.scalars().first() is None:
            await RankingService(db).add_points_to_student(student_id, quiz.points_reward)

    await db.commit()
    await db.refresh(result_obj)
    return result_obj


async def get_my_results(db: AsyncSession, student_id: int) -> List[StudentQuizResult]:
    result = await db.execute(
        select(StudentQuizResult).where(StudentQuizResult.student_id == student_id)
    )
    return result.scalars().all()