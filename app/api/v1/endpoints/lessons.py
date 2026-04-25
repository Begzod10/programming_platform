from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from app.models.lesson import Lesson
from app.dependencies import get_db, get_current_student, get_current_teacher, get_current_student_optional
from app.services import lesson_service, achievement_service, exercise_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseRead, ExerciseSubmitRequest, \
    ExerciseSubmissionRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course

router = APIRouter()


# ============ YORDAMCHI FUNKSIYALAR ============

async def _calc_course_progress(db: AsyncSession, course_id: int, student_id: int) -> dict:
    total_query = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.course_id == course_id,
            Lesson.is_active == True
        )
    )
    total = total_query.scalar() or 0
    if total == 0:
        return {"total_lessons": 0, "completed_lessons": 0, "progress_percentage": 0}

    completed_query = await db.execute(
        select(func.count(LessonCompletion.id))
        .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
        .where(
            Lesson.course_id == course_id,
            LessonCompletion.student_id == student_id
        )
    )
    completed = completed_query.scalar() or 0
    percentage = int((completed / total) * 100)
    return {
        "total_lessons": total,
        "completed_lessons": completed,
        "progress_percentage": min(percentage, 100)
    }


async def _add_points(db: AsyncSession, student_id: int, points: int) -> int:
    if not points or points <= 0:
        return 0
    from app.services.ranking_service import RankingService
    service = RankingService(db)
    student = await service.add_points_to_student(student_id, points)
    return student.total_points if student else 0


# ============ LESSON ENDPOINTS ============

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dars ro'yxati — teacher hammasini, student faqat published larni ko'radi"""
    from app.models.user import UserRole

    is_teacher = current_student.role == UserRole.teacher

    from sqlalchemy.orm import selectinload

    query = select(Lesson).where(
        Lesson.course_id == course_id,
        Lesson.is_active == True
    ).order_by(Lesson.order).options(selectinload(Lesson.exercises))

    if not is_teacher:
        query = query.where(Lesson.is_published == True)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(
        course_id: int,
        lesson_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    res = LessonRead.model_validate(lesson)
    if current_student:
        existing = await db.execute(
            select(LessonCompletion).where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id == lesson_id
            )
        )
        res.is_completed = existing.scalar_one_or_none() is not None

    return res


@router.post("/courses/{course_id}/lessons", response_model=LessonRead, status_code=201)
async def create_lesson(
        course_id: int,
        data: LessonCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    return await lesson_service.create_lesson(db, course_id, data)


# ... (update va delete endpointlari o'zgarmadi, shuning uchun davom etamiz)

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Darsni tugatish — ball qo'shiladi va sertifikat tekshiriladi"""
    result = await lesson_service.complete_lesson(db, lesson_id, current_student.id)
    course_id = result.get("course_id")
    cert = await achievement_service.award_certificate(db, current_student.id, course_id)

    return {
        **result,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None
    }


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
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    # Avval topshirilganini tekshirish
    existing_result = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

    # Yangi proyekt yaratish
    new_project = Project(
        student_id=current_student.id,
        title=lesson.task_title or lesson.title,
        description=data.description or "Dars loyihasi",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
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

    # Darsni tugatish va ball berish
    points_earned = 0
    completion_check = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    if not completion_check.scalar_one_or_none():
        db.add(LessonCompletion(student_id=current_student.id, lesson_id=lesson_id))
        points_reward = getattr(lesson, "points_reward", 0) or 0
        if points_reward > 0:
            await _add_points(db, current_student.id, points_reward)
            points_earned = points_reward

    await db.commit()

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)
    progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        "message": "Loyiha topshirildi!",
        "submission_id": submission.id,
        "points_earned": points_earned,
        "progress": progress,
        "certificate_issued": cert is not None
    }


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
