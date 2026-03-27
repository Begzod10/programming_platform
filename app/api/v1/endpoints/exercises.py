from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/lessons/{lesson_id}/exercises", response_model=List[ExerciseRead])
async def get_exercises(lesson_id: int, db: AsyncSession = Depends(get_db)):
    """Dars mashqlari"""
    return await exercise_service.get_exercises_by_lesson(db, lesson_id)


@router.get("/exercises/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Bitta mashq"""
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return exercise


@router.post("/lessons/{lesson_id}/exercises", response_model=ExerciseRead)
async def create_exercise(
        lesson_id: int,
        data: ExerciseCreate,
        db: AsyncSession = Depends(get_db)
):
    """Yangi mashq qo'shish (teacher)

    exercise_type:
    - fill_in_blank: description da ___ bilan bo'sh joy, correct_answers da javoblar vergul bilan
    - drag_and_drop: drag_items JSON array, correct_order JSON array
    - multiple_choice: options JSON array, correct_answers da to'g'ri variant(lar), is_multiple_select
    - text_input: expected_answer (AI tekshiradi)
    """
    return await exercise_service.create_exercise(db, lesson_id, data)


@router.put("/exercises/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
        exercise_id: int,
        data: ExerciseUpdate,
        db: AsyncSession = Depends(get_db)
):
    """Mashqni yangilash"""
    return await exercise_service.update_exercise(db, exercise_id, data)


@router.delete("/exercises/{exercise_id}")
async def delete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Mashqni o'chirish"""
    result = await exercise_service.delete_exercise(db, exercise_id)
    if not result:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return {"message": "Mashq o'chirildi"}


@router.post("/exercises/{exercise_id}/submit", response_model=ExerciseSubmissionRead)
async def submit_exercise(
        exercise_id: int,
        data: ExerciseSubmitRequest,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mashqqa javob berish

    fill_in_blank: "javob1,javob2"
    drag_and_drop: '["item2","item1","item3"]'
    multiple_choice: "A" yoki "A,C"
    text_input: oddiy matn (AI tekshiradi)
    """
    return await exercise_service.submit_exercise(db, exercise_id, current_student.id, data)


@router.get("/exercises/{exercise_id}/my-submissions", response_model=List[ExerciseSubmissionRead])
async def my_submissions(
        exercise_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening javoblarim tarixi"""
    return await exercise_service.get_my_submissions(db, current_student.id, exercise_id)
