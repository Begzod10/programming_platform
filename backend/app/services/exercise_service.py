from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
import json
import logging

import re

from app.models.exercise import Exercise, ExerciseSubmission
from app.models.lesson import Lesson, LessonCompletion
from app.models.course import Course
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseSubmitRequest
from app.services.grok_service import ProviderError, call_chain, parse_ai_json

logger = logging.getLogger(__name__)


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


async def reorder_exercises(
        db: AsyncSession,
        lesson_id: int,
        exercise_id_1: int,
        exercise_id_2: int
) -> bool:
    """
    Ikkita mashqning `order` qiymatini almashtiradi.
    Ikkalasi ham lesson_id ga tegishli bo'lishi shart.
    """
    ex1 = await get_exercise_by_id(db, exercise_id_1)
    ex2 = await get_exercise_by_id(db, exercise_id_2)

    # Topilmasa yoki boshqa darsga tegishli bo'lsa — False
    if not ex1 or not ex2:
        return False
    if ex1.lesson_id != lesson_id or ex2.lesson_id != lesson_id:
        return False

    # Order qiymatlarini almashtiramiz
    ex1.order, ex2.order = ex2.order, ex1.order

    await db.commit()
    return True


# ──────────────────────────────────────────────────────
#  AI va submit logikasi (o'zgarishsiz qoldirildi)
# ──────────────────────────────────────────────────────

async def get_ai_explanation(
        question: str,
        correct_answer: str,
        student_answer: str,
        explanation: Optional[str] = None,
        course_title: str = "",
        lesson_title: str = "",
) -> str:
    scope = ""
    if course_title:
        scope = f"Kurs: {course_title}"
        if lesson_title:
            scope += f" — Dars: {lesson_title}"
        scope += "\n"
    prompt = f"""Sen dasturlash o'qituvchisisiz. O'quvchi savolga xato javob berdi.

{scope}Savol: {question}
{"Qo'shimcha tushuntirish: " + explanation if explanation else ""}

MUHIM: Javobni faqat shu kurs doirasida baholagil. Masalan, HTML/CSS kursida "class" so'zi HTML attribut sifatida tushuntirilishi kerak, OOP yoki JavaScript classi emas.

Faqat xatoning SABABINI tushuntir (2-3 jumla, o'zbek tilida).
TO'G'RI JAVOBNI AYTMA, O'QUVCHI JAVOBINI HAM AYTMA.
Faqat nima uchun xato bo'lishi mumkinligini va qanday o'ylash kerakligini ayt.
O'quvchi o'zi topishi kerak."""
    try:
        text, _parsed, provider, attempts = await call_chain(
            prompt, max_tokens=300, validator=None,
        )
        if attempts:
            logger.info("[exercise-ai] explanation via %s after %d fallthrough(s): %s",
                        provider, len(attempts), "; ".join(attempts))
        return text.strip()
    except ProviderError as e:
        logger.warning("[exercise-ai] get_ai_explanation failed: %s", e)
        return f"Noto'g'ri. To'g'ri javob: {correct_answer}"


def check_answer_locally(exercise: Exercise, student_answer: str) -> dict:
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

            # Normalize each item: drag chips render without leading-whitespace
            # (indentation looks weird in a pill UI), so the student-submitted
            # values often differ from the stored `correct_order` only by
            # whitespace. Strict == would then mark a correct sequence as
            # wrong (e.g. "    yigindi = yigindi + i;" vs
            # "yigindi = yigindi + i;"). Compare on normalized strings.
            def _norm(item: object) -> str:
                if not isinstance(item, str):
                    return ""
                # Strip outer whitespace and collapse internal whitespace runs
                # so cosmetic differences (tabs vs spaces, double-space typos)
                # also don't cause false negatives.
                return " ".join(item.split())

            correct_norm = [_norm(x) for x in correct_order]
            student_norm = [_norm(x) for x in student_order]
            is_correct = correct_norm == student_norm

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
        # Build options list so we can map letters (A,B,C…) → option texts.
        # Teachers may store correct_answers as full text ("Backtick `...`")
        # while the frontend submits the letter ("C"). Normalize both sides.
        try:
            options_list = json.loads(exercise.options or "[]")
        except (json.JSONDecodeError, TypeError):
            options_list = [o.strip() for o in (exercise.options or "").split(",") if o.strip()]

        def _to_text(val: str) -> str:
            """If val is a single letter A-Z, return the corresponding option text."""
            v = val.strip()
            if len(v) == 1 and v.isalpha():
                idx = ord(v.upper()) - 65
                if 0 <= idx < len(options_list):
                    return str(options_list[idx]).strip().lower()
            return v.lower()

        correct = {_to_text(a) for a in (exercise.correct_answers or "").split(",") if a.strip()}
        student = {_to_text(a) for a in student_answer.split(",") if a.strip()}
        is_correct = correct == student
        return {
            "is_correct": is_correct,
            "partial_score": 1.0 if is_correct else 0.0,
            "needs_ai_explanation": not is_correct,
            "correct_answer": exercise.correct_answers,
            "feedback": "To'g'ri!" if is_correct else None
        }

    else:
        return None


async def check_answer_with_grok(
        question: str,
        expected_answer: Optional[str],
        student_answer: str,
        hint: Optional[str] = None,
        explanation: Optional[str] = None,
        course_title: str = "",
        lesson_title: str = "",
        lesson_excerpt: str = "",
) -> dict:
    scope = ""
    if course_title:
        scope = f"Kurs: {course_title}"
        if lesson_title:
            scope += f" — Dars: {lesson_title}"
        scope += "\n"
    excerpt_block = f"Dars matni (qisqa): {lesson_excerpt}\n" if lesson_excerpt else ""
    prompt = f"""Sen dasturlash o'qituvchisisiz. Student savolga erkin javob berdi. Javobni baholab ber.

{scope}{excerpt_block}
MUHIM: Javobni faqat yuqoridagi kurs va dars doirasida baholagil.
Masalan, HTML/CSS kursida "class" so'zi HTML atributi sifatida tushuntirilishi kerak — OOP yoki JavaScript class emas.

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
        _text, parsed, provider, attempts = await call_chain(
            prompt, max_tokens=500, validator=parse_ai_json,
        )
        if attempts:
            logger.info("[exercise-ai] grade via %s after %d fallthrough(s): %s",
                        provider, len(attempts), "; ".join(attempts))
        return parsed
    except ProviderError as e:
        logger.warning("[exercise-ai] check_answer_with_grok failed: %s", e)
        return {
            "is_correct": False,
            "partial_score": 0,
            "feedback": "AI xizmati hozir javob bera olmadi. Birozdan keyin qayta urinib ko'ring.",
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

    # Fetch lesson + course for AI grading context
    lesson_row = (await db.execute(
        select(Lesson, Course.title.label("course_title"))
        .outerjoin(Course, Course.id == Lesson.course_id)
        .where(Lesson.id == exercise.lesson_id)
    )).first()
    lesson_obj = lesson_row[0] if lesson_row else None
    course_title = lesson_row[1] if lesson_row else ""
    lesson_title = lesson_obj.title if lesson_obj else ""

    # Strip HTML/mermaid from lesson text for the AI excerpt
    raw_text = (lesson_obj.text_content or "") if lesson_obj else ""
    clean = re.sub(r"<pre[\s\S]*?</pre>", " ", raw_text, flags=re.IGNORECASE)
    clean = re.sub(r"```[\s\S]*?```", " ", clean)
    clean = re.sub(r"<[^>]+>", " ", clean)
    lesson_excerpt = re.sub(r"\s+", " ", clean).strip()[:400]

    prev_correct = await db.execute(
        select(ExerciseSubmission).where(
            ExerciseSubmission.exercise_id == exercise_id,
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.is_correct == True
        )
    )
    already_solved = prev_correct.first() is not None

    result = check_answer_locally(exercise, data.student_answer)

    if result is None:
        result = await check_answer_with_grok(
            question=exercise.description,
            expected_answer=exercise.expected_answer,
            student_answer=data.student_answer,
            hint=exercise.hint,
            explanation=exercise.explanation,
            course_title=course_title,
            lesson_title=lesson_title,
            lesson_excerpt=lesson_excerpt,
        )
    elif not result.get("is_correct") and result.get("needs_ai_explanation"):
        ai_feedback = await get_ai_explanation(
            question=exercise.description,
            correct_answer=result.get("correct_answer", ""),
            student_answer=data.student_answer,
            explanation=exercise.explanation,
            course_title=course_title,
            lesson_title=lesson_title,
        )
        result["feedback"] = ai_feedback

    is_correct = result.get("is_correct", False)
    partial = result.get("partial_score", 0)

    if is_correct and not already_solved:
        score = exercise.points
        ranking_service = RankingService(db)
        await ranking_service.add_points_to_student(student_id, score)
    else:
        score = 0

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
        ai_feedback=result.get("feedback", ""),
        time_spent_ms=data.time_spent_ms,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    if is_correct:
        await _maybe_auto_complete_lesson(db, exercise.lesson_id, student_id)
        # Streak only counts correct work — a wrong submission shouldn't
        # protect the flame. Failures must be local to the streak system
        # so they can't break the user-facing submission flow.
        try:
            from app.services.streak_service import bump_streak
            await bump_streak(db, student_id)
            await db.commit()
        except Exception:
            await db.rollback()

    return submission


async def _maybe_auto_complete_lesson(
        db: AsyncSession,
        lesson_id: int,
        student_id: int,
) -> None:
    """Insert LessonCompletion if a project-less lesson is fully solved.

    Triggered after a correct ExerciseSubmission. For lessons that have a
    project (task_title or project_id set), completion is driven by the
    project-submit flow instead — this is a no-op there.
    """
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if lesson is None or lesson.has_project:
        return

    existing = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == student_id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return

    ex_ids_rows = await db.execute(
        select(Exercise.id).where(Exercise.lesson_id == lesson_id)
    )
    ex_ids = [r[0] for r in ex_ids_rows.all()]
    if not ex_ids:
        return

    correct_rows = await db.execute(
        select(ExerciseSubmission.exercise_id)
        .where(
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.exercise_id.in_(ex_ids),
            ExerciseSubmission.is_correct == True,
        )
        .distinct()
    )
    correct_ids = {r[0] for r in correct_rows.all()}
    if len(correct_ids) < len(ex_ids):
        return

    db.add(LessonCompletion(student_id=student_id, lesson_id=lesson_id))
    if lesson.points_reward and lesson.points_reward > 0:
        from app.services.ranking_service import RankingService
        await RankingService(db).add_points_to_student(student_id, lesson.points_reward)
    try:
        await db.commit()
    except IntegrityError:
        # Concurrent request inserted the completion first — fine, rollback the
        # extra points award via the unique constraint hit.
        await db.rollback()


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