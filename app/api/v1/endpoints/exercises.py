from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student
from app.services import exercise_service
from app.schemas.exercise import (
    ExerciseCreate, ExerciseUpdate, ExerciseRead,
    ExerciseSubmitRequest, ExerciseSubmissionRead
)
from app.models.user import Student

router = APIRouter()


# prefix: /courses/{course_id}/lessons
# to'liq URL: /courses/{course_id}/lessons/{lesson_id}/exercises

@router.get("/{lesson_id}/exercises", response_model=List[ExerciseRead])
async def get_exercises(lesson_id: int, db: AsyncSession = Depends(get_db)):
    """Dars mashqlari — GET /courses/{course_id}/lessons/{lesson_id}/exercises"""
    return await exercise_service.get_exercises_by_lesson(db, lesson_id)


@router.post("/{lesson_id}/exercises", response_model=ExerciseRead)
async def create_exercise(
        lesson_id: int,
        data: ExerciseCreate,
        db: AsyncSession = Depends(get_db)
):
    """Yangi mashq qo'shish — POST /courses/{course_id}/lessons/{lesson_id}/exercises"""
    return await exercise_service.create_exercise(db, lesson_id, data)


@router.get("/{lesson_id}/exercises/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(lesson_id: int, exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Bitta mashq — GET /courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}"""
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return exercise


@router.put("/{lesson_id}/exercises/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
        lesson_id: int,
        exercise_id: int,
        data: ExerciseUpdate,
        db: AsyncSession = Depends(get_db)
):
    """Mashqni yangilash — PUT /courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}"""
    return await exercise_service.update_exercise(db, exercise_id, data)


@router.delete("/{lesson_id}/exercises/{exercise_id}")
async def delete_exercise(lesson_id: int, exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Mashqni o'chirish — DELETE /courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}"""
    result = await exercise_service.delete_exercise(db, exercise_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return {"message": "Mashq o'chirildi"}


@router.post("/{lesson_id}/exercises/{exercise_id}/submit", response_model=ExerciseSubmissionRead)
async def submit_exercise(
        lesson_id: int,
        exercise_id: int,
        data: ExerciseSubmitRequest,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mashqqa javob berish — POST /courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}/submit"""
    return await exercise_service.submit_exercise(db, exercise_id, current_student.id, data)


@router.get("/{lesson_id}/exercises/{exercise_id}/my-submissions", response_model=List[ExerciseSubmissionRead])
async def my_submissions(
        lesson_id: int,
        exercise_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening javoblarim — GET /courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}/my-submissions"""
    return await exercise_service.get_my_submissions(db, current_student.id, exercise_id)


@router.get("/{lesson_id}/exercises/progress")
async def get_course_progress(
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Student = Depends(get_current_student)
):
    """Course progress foizi"""
    from sqlalchemy import func
    from app.models.lesson import Lesson
    from app.models.exercise import Exercise, ExerciseSubmission

    # Coursedagi jami exerciselar
    total = await db.execute(
        select(func.count(Exercise.id))
        .join(Lesson, Lesson.id == Exercise.lesson_id)
        .where(Lesson.course_id == course_id, Exercise.is_active == True)
    )
    total_count = total.scalar() or 0

    # Bajarilgan exerciselar
    completed = await db.execute(
        select(func.count(ExerciseSubmission.exercise_id.distinct()))
        .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
        .join(Lesson, Lesson.id == Exercise.lesson_id)
        .where(
            Lesson.course_id == course_id,
            ExerciseSubmission.student_id == current_student.id,
            ExerciseSubmission.is_correct == True
        )
    )
    completed_count = completed.scalar() or 0

    progress = round((completed_count / total_count * 100), 1) if total_count > 0 else 0

    return {
        "course_id": course_id,
        "total_exercises": total_count,
        "completed_exercises": completed_count,
        "progress_percent": progress
    }
