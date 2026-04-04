from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, status, Request  # ← Request qo'shildi
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from app.dependencies import get_db, get_current_student, get_current_teacher
from app.services import lesson_service, exercise_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseRead, ExerciseSubmitRequest, \
    ExerciseSubmissionRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course

router = APIRouter()


# ============ LESSON ENDPOINTS ============

async def _calc_course_progress(db: AsyncSession, course_id: int, student_id: int) -> dict:
    total_query = await db.execute(
        select(func.count(Lesson.id)).where(Lesson.course_id == course_id, Lesson.is_active == True)
    )
    total = total_query.scalar() or 0
    if total == 0:
        return {"total_lessons": 0, "completed_lessons": 0, "progress_percentage": 0}

    completed_query = await db.execute(
        select(func.count(LessonCompletion.id))
        .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
        .where(Lesson.course_id == course_id, LessonCompletion.student_id == student_id)
    )
    completed = completed_query.scalar() or 0
    percentage = int((completed / total) * 100)
    return {
        "total_lessons": total,
        "completed_lessons": completed,
        "progress_percentage": min(percentage, 100)
    }


async def _ensure_enrolled(db: AsyncSession, student_id: int, course_id: int):
    """Talabani kursga a'zoligini tekshiradi va bo'lmasa a'zo qiladi"""
    # Student va uning kurslarini yuklash
    stmt = select(Student).options(selectinload(Student.enrolled_courses)).where(Student.id == student_id)
    res = await db.execute(stmt)
    student = res.scalar_one()

    if not any(c.id == course_id for c in student.enrolled_courses):
        course_stmt = select(Course).where(Course.id == course_id)
        course_res = await db.execute(course_stmt)
        course = course_res.scalar_one_or_none()
        if course:
            student.enrolled_courses.append(course)
            await db.flush()  # Transactionni davom ettirish uchun


@router.get("/courses/{course_id}/lessons")
async def get_lessons(
        course_id: int,
        request: Request,  # ✅ qo'shildi
        db: AsyncSession = Depends(get_db)
):
    from app.api.v1.endpoints.courses import _get_id_from_auth
    student_id = await _get_id_from_auth(request)
    lessons = await lesson_service.get_lessons_by_course(db, course_id)
    # student_id = await _get_id_from_auth(request)

    result = []
    for lesson in lessons:
        lesson_dict = {
            "id": lesson.id,
            "course_id": lesson.course_id,
            "title": lesson.title,
            "order": lesson.order,
            "task_title": lesson.task_title,
            "task_description": lesson.task_description,
            "task_requirements": lesson.task_requirements,
            "task_technologies": lesson.task_technologies,
            "task_deadline_days": lesson.task_deadline_days,
            "text_content": lesson.text_content,
            "code_content": lesson.code_content,
            "code_language": lesson.code_language,
            "video_url": lesson.video_url,
            "image_url": lesson.image_url,
            "file_url": lesson.file_url,
            "project_id": lesson.project_id,
            "is_active": lesson.is_active,
            "created_at": lesson.created_at,
            "updated_at": lesson.updated_at,
            "exercises": lesson.exercises if hasattr(lesson, 'exercises') else [],
            "is_completed": False
        }
        if student_id:
            comp = await db.execute(
                select(LessonCompletion).where(
                    LessonCompletion.student_id == student_id,
                    LessonCompletion.lesson_id == lesson.id
                )
            )
            lesson_dict["is_completed"] = comp.scalar_one_or_none() is not None
        result.append(lesson_dict)

    return result


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(course_id: int, lesson_id: int, db: AsyncSession = Depends(get_db)):
    """Darsni olish"""
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


# ============ EXERCISE ENDPOINTS (lesson ichida) ============

@router.get("/courses/{course_id}/lessons/{lesson_id}/exercises", response_model=List[ExerciseRead])
async def get_exercises(
        course_id: int,
        lesson_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Dars mashqlarini olish"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return await exercise_service.get_exercises_by_lesson(db, lesson_id)


@router.get("/courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
        course_id: int,
        lesson_id: int,
        exercise_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Bitta mashqni olish"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise or exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return exercise


@router.post("/courses/{course_id}/lessons/{lesson_id}/exercises", response_model=ExerciseRead, status_code=201)
async def create_exercise(
        course_id: int,
        lesson_id: int,
        data: ExerciseCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Darsga mashq qo'shish (faqat teacher)

    exercise_type:
    - fill_in_blank: description da ___ bilan bo'sh joy, correct_answers: "javob1,javob2"
    - drag_and_drop: drag_items: '["item1","item2"]', correct_order: '["item2","item1"]'
    - multiple_choice: options: '["A variant","B variant"]', correct_answers: "A" yoki "A,C"
    - text_input: expected_answer (AI tekshiradi)
    """
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    return await exercise_service.create_exercise(db, lesson_id, data)


@router.put("/courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
        course_id: int,
        lesson_id: int,
        exercise_id: int,
        data: ExerciseUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Mashqni yangilash (faqat teacher)"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise or exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return await exercise_service.update_exercise(db, exercise_id, data)


@router.delete("/courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}", status_code=204)
async def delete_exercise(
        course_id: int,
        lesson_id: int,
        exercise_id: int,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    """Mashqni o'chirish (faqat teacher)"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise or exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    await exercise_service.delete_exercise(db, exercise_id)
    return None


@router.post("/courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}/submit",
             response_model=ExerciseSubmissionRead, status_code=201)
async def submit_exercise(
        course_id: int,
        lesson_id: int,
        exercise_id: int,
        data: ExerciseSubmitRequest,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mashqqa javob berish (student)

    fill_in_blank: "javob1,javob2"
    drag_and_drop: '["item2","item1","item3"]'
    multiple_choice: "A" yoki "A,C"
    text_input: oddiy matn (AI tekshiradi)
    """
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise or exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return await exercise_service.submit_exercise(db, exercise_id, current_student.id, data)


@router.get("/courses/{course_id}/lessons/{lesson_id}/exercises/{exercise_id}/my-submissions",
            response_model=List[ExerciseSubmissionRead])
async def my_exercise_submissions(
        course_id: int,
        lesson_id: int,
        exercise_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening mashq javoblarim tarixi"""
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise or exercise.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Mashq topilmadi")
    return await exercise_service.get_my_submissions(db, current_student.id, exercise_id)


# ============ SUBMISSION ENDPOINTS ============

# ============================================================
# PROGRESS ENDPOINTS
# ============================================================

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(404, "Dars topilmadi")

    # 1. Kursga avtomatik a'zo qilish (Muhim!)
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    # 2. Tugatishni yozish
    existing = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    if not existing.scalar_one_or_none():
        completion = LessonCompletion(student_id=current_student.id, lesson_id=lesson_id)
        db.add(completion)

    await db.commit()
    progress = await _calc_course_progress(db, lesson.course_id, current_student.id)
    return {"message": "Dars tugatildi", **progress}


@router.get("/lessons/{lesson_id}/is-completed")
async def is_lesson_completed(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """
    Dars tugatilganmi? + kurs progressini ham qaytaradi.
    Frontend sahifa ochilganda shu endpointni chaqirsin.
    """
    # Lesson mavjudligini tekshirish
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    # Tugatilganmi?
    result = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    completion = result.scalar_one_or_none()

    # Kurs progressini hisoblash
    progress = await _calc_course_progress(db, lesson.course_id, current_student.id)

    return {
        "lesson_id": lesson_id,
        "is_completed": completion is not None,
        "completed_at": completion.completed_at if completion else None,
        # Progress ma'lumotlari — frontend shu yerdan olsin
        "course_id": lesson.course_id,
        **progress
        # Javob misoli:
        # {
        #   "lesson_id": 5,
        #   "is_completed": true,
        #   "completed_at": "2024-01-15T10:30:00",
        #   "course_id": 2,
        #   "total_lessons": 10,
        #   "completed_lessons": 7,
        #   "progress_percentage": 70
        # }
    }


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
        course_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """
    Kurs progressini qaytaradi.
    Frontend kurs sahifasi ochilganda shu endpointni chaqirsin.
    """
    progress = await _calc_course_progress(db, course_id, current_student.id)
    return {
        "course_id": course_id,
        **progress
        # Javob misoli:
        # {
        #   "course_id": 2,
        #   "total_lessons": 10,
        #   "completed_lessons": 10,
        #   "progress_percentage": 100
        # }
    }


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
    """Dars loyihasini topshirish va avtomatik tugatilgan deb belgilash"""
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

    # 3. LessonCompletion ham yozamiz (progress uchun)
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

    await db.commit()

    # Progress hisoblash
    progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        "message": "Loyiha topshirildi va dars tugatildi!",
        "submission_id": submission.id,
        "project_id": new_project.id,
        **progress
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
