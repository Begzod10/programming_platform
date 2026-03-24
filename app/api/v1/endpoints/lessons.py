from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.dependencies import get_db, get_current_student, get_current_teacher
from app.services import lesson_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project

router = APIRouter()


@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(course_id: int, db: AsyncSession = Depends(get_db)):
    """Kurs darslarini olish (hamma ko'rishi mumkin)"""
    return await lesson_service.get_lessons_by_course(db, course_id)


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(course_id: int, lesson_id: int, db: AsyncSession = Depends(get_db)):
    """Darsni olish (hamma ko'rishi mumkin)"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return lesson


@router.post("/courses/{course_id}/lessons", response_model=LessonRead, status_code=201)
async def create_lesson(
        course_id: int,
        data: LessonCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Yangi dars yaratish (faqat teacher)"""
    return await lesson_service.create_lesson(db, course_id, data)


@router.put("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def update_lesson(
        course_id: int,
        lesson_id: int,
        data: LessonUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Darsni yangilash (faqat teacher)"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return await lesson_service.update_lesson(db, lesson_id, data)


@router.delete("/courses/{course_id}/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
        course_id: int,
        lesson_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Darsni o'chirish (faqat teacher)"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await lesson_service.delete_lesson(db, lesson_id)
    return None


# ============ SUBMISSION ENDPOINTS ============

class LessonSubmitRequest(BaseModel):
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    description: Optional[str] = None


@router.post("/courses/{course_id}/lessons/{lesson_id}/submit", status_code=201)
async def submit_lesson_project(
        course_id: int,
        lesson_id: int,
        data: LessonSubmitRequest,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dars loyihasini topshirish"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    # Allaqachon topshirilganmi?
    existing_result = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

    # Project yaratish
    new_project = Project(
        student_id=current_student.id,
        title=lesson.task_title or lesson.title,
        description=data.description or lesson.task_description or "Dars loyihasi",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
        difficulty_level="Easy",
        status="Submitted",
    )
    db.add(new_project)
    await db.flush()

    # Submission yaratish
    submission = Submission(
        lesson_id=lesson_id,
        student_id=current_student.id,
        project_id=new_project.id,
        status="Submitted",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
        description=data.description,
    )
    db.add(submission)
    await db.commit()

    return {
        "message": "Loyiha muvaffaqiyatli topshirildi",
        "submission_id": submission.id,
        "project_id": new_project.id
    }


@router.get("/courses/{course_id}/lessons/{lesson_id}/submission")
async def get_lesson_submission(
        course_id: int,
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dars submission statusini olish"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    result = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        return {"submitted": False}

    return {
        "submitted": True,
        "submission_id": submission.id,
        "project_id": submission.project_id,
        "status": submission.status,
        "github_url": submission.github_url,
        "live_demo_url": submission.live_demo_url,
        "description": submission.description,
    }