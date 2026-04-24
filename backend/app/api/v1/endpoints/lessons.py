from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_student, get_current_teacher, get_current_student_optional
from app.services import lesson_service, achievement_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course

router = APIRouter()


# ============ LESSON ENDPOINTS ============

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
        "progress_percentage": min(percentage, 100),
        "progress": min(percentage, 100),  # Alias
        "percentage": min(percentage, 100)  # Alias
    }


async def _ensure_enrolled(db: AsyncSession, student_id: int, course_id: int):
    """Talabani kursga a'zoligini tekshiradi va bo'lmasa a'zo qiladi"""
    stmt = select(Student).options(selectinload(Student.enrolled_courses)).where(Student.id == student_id)
    res = await db.execute(stmt)
    student = res.scalar_one()

    if not any(c.id == course_id for c in student.enrolled_courses):
        course_stmt = select(Course).where(Course.id == course_id)
        course_res = await db.execute(course_stmt)
        course = course_res.scalar_one_or_none()
        if course:
            student.enrolled_courses.append(course)
            await db.flush()


async def _add_points(db: AsyncSession, student_id: int, points: int) -> int:
    """Studentga ball qo'shish (Ranking orqali)"""
    if not points or points <= 0:
        return 0
    from app.services.ranking_service import RankingService
    service = RankingService(db)
    student = await service.add_points_to_student(student_id, points)
    if student:
        return student.total_points
    return 0


# ============================================================
# LESSON CRUD ENDPOINTS
# ============================================================

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    """Kurs darslarini olish."""
    if current_student:
        allowed = await achievement_service.check_course_prerequisite(db, current_student.id, course_id)
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="Bu kursga kirish uchun avval oldingi kursni tugatishingiz kerak."
            )

    lessons = await lesson_service.get_lessons_by_course(db, course_id)

    completed_ids = set()
    if current_student:
        completed_lessons = await db.execute(
            select(LessonCompletion.lesson_id)
            .where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id.in_([l.id for l in lessons])
            )
        )
        completed_ids = {r[0] for r in completed_lessons.all()}

    result = []
    for l in lessons:
        lesson_data = LessonRead.model_validate(l)
        is_comp = l.id in completed_ids
        lesson_data.is_completed = is_comp
        lesson_data.completed = is_comp  # Alias
        result.append(lesson_data)

    return result


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(
        course_id: int,
        lesson_id: int,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    """Darsni olish"""
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
        is_comp = existing.scalar_one_or_none() is not None
        res.is_completed = is_comp
        res.completed = is_comp  # Alias

    return res


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


# ============================================================
# LESSON COMPLETION ENDPOINTS
# ============================================================

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Darsni tugatish — ball qo'shiladi, kurs tugasa sertifikat beriladi"""
    result = await lesson_service.complete_lesson(db, lesson_id, current_student.id)
    course_id = result.get("course_id")

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)

    return {
        **result,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None
    }


@router.get("/lessons/{lesson_id}/is-completed")
async def is_lesson_completed(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dars tugatilganmi? + kurs progressini ham qaytaradi"""
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    result = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    completion = result.scalar_one_or_none()
    progress = await _calc_course_progress(db, lesson.course_id, current_student.id)

    return {
        "lesson_id": lesson_id,
        "is_completed": completion is not None,
        "completed_at": completion.completed_at if completion else None,
        "course_id": lesson.course_id,
        **progress
    }


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
        course_id: int,
        current_student: Optional[Student] = Depends(get_current_student_optional),
        db: AsyncSession = Depends(get_db)
):
    """Kurs progressini qaytaradi"""
    if not current_student:
        return {
            "course_id": course_id,
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percentage": 0,
            "progress": 0,
            "percentage": 0
        }
    progress = await _calc_course_progress(db, course_id, current_student.id)
    return {"course_id": course_id, **progress}


# ============================================================
# SUBMISSION ENDPOINTS
# ============================================================

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
    """Dars loyihasini topshirish — ball avtomatik qo'shiladi, kurs tugasa sertifikat beriladi"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    existing_result = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

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

    points_earned = 0
    completion_check = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    if not completion_check.scalar_one_or_none():
        completion = LessonCompletion(
            student_id=current_student.id,
            lesson_id=lesson_id
        )
        db.add(completion)

        points_reward = getattr(lesson, "points_reward", 0) or 0
        if points_reward > 0:
            await _add_points(db, current_student.id, points_reward)
            points_earned = points_reward

    await db.commit()

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)

    student_res = await db.execute(select(Student).where(Student.id == current_student.id))
    student = student_res.scalar_one_or_none()

    progress = await _calc_course_progress(db, course_id, current_student.id)
    return {
        "message": "Loyiha topshirildi va dars tugatildi!",
        "submission_id": submission.id,
        "project_id": new_project.id,
        **progress,
        "points_earned": points_earned,
        "total_points": student.total_points if student else 0,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None
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
