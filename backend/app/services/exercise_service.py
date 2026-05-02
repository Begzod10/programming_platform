from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from typing import List, Optional
import httpx
import json
import re

from app.models.exercise import Exercise, ExerciseSubmission
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseSubmitRequest
from app.config import settings


async def get_exercises_by_lesson(db: AsyncSession, lesson_id: int) -> List[Exercise]:
    result = await db.execute(
        select(Exercise)
        .where(Exercise.lesson_id == lesson_id, Exercise.is_active == True)
        .order_by(Exercise.order)
    )
    return result.scalars().all()


async def get_exercise_by_id(db: AsyncSession, exercise_id: int) -> Optional[Exercise]:
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    return result.scalar_one_or_none()


async def create_exercise(db: AsyncSession, lesson_id: int, data: ExerciseCreate) -> Exercise:
    exercise = Exercise(**data.dict(), lesson_id=lesson_id)
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def update_exercise(db: AsyncSession, exercise_id: int, data: ExerciseUpdate) -> Optional[Exercise]:
    exercise = await get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(exercise, key, value)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def delete_exercise(db: AsyncSession, exercise_id: int) -> bool:
    exercise = await get_exercise_by_id(db, exercise_id)
    if not exercise:
        return False
    await db.delete(exercise)
    await db.commit()
    return True


async def get_ai_explanation(
        question: str,
        correct_answer: str,
        student_answer: str,
        explanation: Optional[str] = None
) -> str:
    prompt = f"""Sen dasturlash o'qituvchisisiz. O'quvchi savolga xato javob berdi.

Savol: {question}
{"Qo'shimcha tushuntirish: " + explanation if explanation else ""}

Faqat xatoning SABABINI tushuntir (2-3 jumla, o'zbek tilida).
TO'G'RI JAVOBNI AYTMA, O'QUVCHI JAVOBINI HAM AYTMA.
Faqat nima uchun xato bo'lishi mumkinligini va qanday o'ylash kerakligini ayt.
O'quvchi o'zi topishi kerak."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                settings.GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROK_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return f"Noto'g'ri. To'g'ri javob: {correct_answer}"


def check_answer_locally(exercise: Exercise, student_answer: str) -> dict:
    """AI siz oddiy tekshiruv"""
    exercise_type = exercise.exercise_type

    if exercise_type == "fill_in_blank":
        correct = [a.strip().lower() for a in (exercise.correct_answers or "").split(",")]
        answers = [a.strip().lower() for a in student_answer.split(",")]
        is_correct = sorted(correct) == sorted(answers)
        return {
            "is_correct": is_correct,
            "partial_score": 1.0 if is_correct else 0.0,
            "needs_ai_explanation": not is_correct,
            "correct_answer": exercise.correct_answers,
            "feedback": "To'g'ri!" if is_correct else None
        }

    elif exercise_type == "drag_and_drop":
        try:
            correct_order = json.loads(exercise.correct_order or "[]")
            student_order = json.loads(student_answer)
            is_correct = correct_order == student_order
            return {
                "is_correct": is_correct,
                "partial_score": 1.0 if is_correct else 0.0,
                "needs_ai_explanation": not is_correct,
                "correct_answer": exercise.correct_order,
                "feedback": "To'g'ri tartib!" if is_correct else None
            }
        except Exception:
            return {
                "is_correct": False,
                "partial_score": 0,
                "needs_ai_explanation": False,
                "feedback": "Javob formati noto'g'ri"
            }

    elif exercise_type == "multiple_choice":
        correct = set(a.strip() for a in (exercise.correct_answers or "").split(","))
        student = set(a.strip() for a in student_answer.split(","))
        is_correct = correct == student
        return {
            "is_correct": is_correct,
            "partial_score": 1.0 if is_correct else 0.0,
            "needs_ai_explanation": not is_correct,
            "correct_answer": exercise.correct_answers,
            "feedback": "To'g'ri!" if is_correct else None
        }

    else:
        # text_input — Grok AI tekshiradi
        return None


async def check_answer_with_grok(
        question: str,
        expected_answer: Optional[str],
        student_answer: str,
        hint: Optional[str] = None,
        explanation: Optional[str] = None
) -> dict:
    prompt = f"""Sen dasturlash o'qituvchisisiz. Student savolga erkin javob berdi. Javobni baholab ber.

Savol: {question}
{"Kutilgan javob: " + expected_answer if expected_answer else ""}
{"Yordam: " + hint if hint else ""}
{"Tushuntirish: " + explanation if explanation else ""}
Student javobi: {student_answer}

Faqat JSON formatda javob ber, boshqa hech narsa yozma:
{{
  "is_correct": true yoki false,
  "partial_score": 0.0 dan 1.0 gacha (qisman togri bolsa),
  "feedback": "Uzbek tilida tushuntirish. Xato bolsa nima notogri va qanday togrash kerakligini ayt."
}}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.GROK_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROK_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"is_correct": False, "partial_score": 0.5, "feedback": text}
    except Exception as e:
        return {
            "is_correct": False,
            "partial_score": 0,
            "feedback": f"AI xato: {str(e)}"
        }


async def submit_exercise(
        db: AsyncSession,
        exercise_id: int,
        student_id: int,
        data: ExerciseSubmitRequest
) -> ExerciseSubmission:
    from app.services.ranking_service import RankingService

    exercise = await get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")

    # ✅ Avval to'g'ri javob berganmi tekshirish
    prev_correct = await db.execute(
        select(ExerciseSubmission).where(
            ExerciseSubmission.exercise_id == exercise_id,
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.is_correct == True
        )
    )
    already_solved = prev_correct.first() is not None

    # Tekshiruv
    result = check_answer_locally(exercise, data.student_answer)

    if result is None:
        result = await check_answer_with_grok(
            question=exercise.description,
            expected_answer=exercise.expected_answer,
            student_answer=data.student_answer,
            hint=exercise.hint,
            explanation=exercise.explanation
        )
    elif not result.get("is_correct") and result.get("needs_ai_explanation"):
        ai_feedback = await get_ai_explanation(
            question=exercise.description,
            correct_answer=result.get("correct_answer", ""),
            student_answer=data.student_answer,
            explanation=exercise.explanation
        )
        result["feedback"] = ai_feedback

    is_correct = result.get("is_correct", False)
    partial = result.get("partial_score", 0)

    # ✅ Ball faqat 1-marta to'g'ri javob berganda beriladi
    if is_correct and not already_solved:
        score = exercise.points
        ranking_service = RankingService(db)
        await ranking_service.add_points_to_student(student_id, score)
    else:
        score = 0  # Qayta yechsa ball yo'q

    # ✅ already_solved bo'lsa maxsus xabar
    if already_solved and is_correct:
        result["feedback"] = "✅ Barakalla! Bu mashqni avval ham to'g'ri yechgansiz. Ball bir marta beriladi."
    elif already_solved and not is_correct:
        result["feedback"] = result.get("feedback", "") + "\n\n💡 Qayta urinib ko'ring!"

    submission = ExerciseSubmission(
        exercise_id=exercise_id,
        student_id=student_id,
        student_answer=data.student_answer,
        is_correct=is_correct,
        score=score,
        ai_feedback=result.get("feedback", "")
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def get_my_submissions(db: AsyncSession, student_id: int, exercise_id: int) -> List[ExerciseSubmission]:
    result = await db.execute(
        select(ExerciseSubmission)
        .where(
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.exercise_id == exercise_id
        )
        .order_by(ExerciseSubmission.submitted_at.desc())
    )
    return result.scalars().all()
