import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from starlette import status
from app.dependencies import get_db, get_current_student, get_current_teacher, get_current_student_optional, \
    get_current_instructor
from app.services import lesson_service, achievement_service
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonRead
from app.models.user import Student
from app.models.submission import Submission
from app.models.project import Project
from app.models.lesson import LessonCompletion, Lesson
from app.models.course import Course

from .lesson_helpers import (
    PROJECT_PASS_THRESHOLD,
    _inject_file_previews,
    _hydrate_exercise_sections,
    _calc_lesson_progress,
    _calc_course_progress,
    _ensure_enrolled,
    _add_points,
    _subtract_points,
    _try_auto_ai_review,
    _check_completion_gate,
    translate_project_feedback,
)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons", response_model=List[LessonRead])
async def get_lessons(
        course_id: int,
        lang: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    if current_student:
        await _ensure_enrolled(db, current_student.id, course_id)
    lessons = await lesson_service.get_lessons_by_course(db, course_id)

    completed_ids: set = set()
    if current_student and lessons:
        lesson_ids = [l.id for l in lessons]
        comp_res = await db.execute(
            select(LessonCompletion.lesson_id).where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id.in_(lesson_ids)
            )
        )
        completed_ids = {row[0] for row in comp_res.all()}

    result = []
    for lesson in lessons:
        lesson_data = LessonRead.model_validate(lesson)
        is_comp = lesson.id in completed_ids
        lesson_data.is_completed = is_comp
        lesson_data.completed = is_comp

        if current_student:
            pct = await _calc_lesson_progress(db, lesson, current_student.id)
            lesson_data.progress_percentage = pct
        else:
            lesson_data.progress_percentage = 0

        result.append(lesson_data)

    if lang and lang != "uz":
        from app.services import translation_store as ts
        for lesson, dto in zip(lessons, result):
            for field_name in ("title", "chapter", "text_content", "task_title",
                               "task_description", "task_requirements", "task_technologies"):
                tr = ts.get("lesson", lesson.id, lang, field_name)
                if tr is not None:
                    setattr(dto, field_name, tr)
            tr_sections = ts.get("lesson", lesson.id, lang, "sections_json")
            if tr_sections:
                dto.sections_json = tr_sections

    await _inject_file_previews(db, [l.id for l in lessons], result)
    await _hydrate_exercise_sections(db, result, lang=lang)
    return result


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson(
        course_id: int,
        lesson_id: int,
        lang: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        current_student: Optional[Student] = Depends(get_current_student_optional)
):
    if current_student:
        await _ensure_enrolled(db, current_student.id, course_id)
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    if current_student:
        prev_res = await db.execute(
            select(Lesson).where(
                Lesson.course_id == course_id,
                Lesson.is_active == True,
                Lesson.order < lesson.order,
            ).order_by(Lesson.order.desc()).limit(1)
        )
        prev_lesson = prev_res.scalar_one_or_none()
        if prev_lesson and prev_lesson.has_project:
            pass_check = await db.execute(
                select(Project)
                .join(Submission, Submission.project_id == Project.id)
                .where(
                    Submission.lesson_id == prev_lesson.id,
                    Submission.student_id == current_student.id,
                    Project.points_earned >= PROJECT_PASS_THRESHOLD,
                    Project.status == "Approved",
                )
            )
            if not pass_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Oldingi darsning loyihasini muvaffaqiyatli topshiring",
                )

    res = LessonRead.model_validate(lesson)

    if lang and lang != "uz":
        from app.services import translation_store as ts
        for field_name in ("title", "chapter", "text_content", "task_title",
                           "task_description", "task_requirements", "task_technologies"):
            tr = ts.get("lesson", lesson.id, lang, field_name)
            if tr is not None:
                setattr(res, field_name, tr)
        tr_sections = ts.get("lesson", lesson.id, lang, "sections_json")
        if tr_sections:
            res.sections_json = tr_sections

    if current_student:
        comp_res = await db.execute(
            select(LessonCompletion).where(
                LessonCompletion.student_id == current_student.id,
                LessonCompletion.lesson_id == lesson_id
            )
        )
        is_comp = comp_res.scalar_one_or_none() is not None
        res.is_completed = is_comp
        res.completed = is_comp
        res.progress_percentage = await _calc_lesson_progress(db, lesson, current_student.id)

    await _inject_file_previews(db, [lesson_id], [res])
    await _hydrate_exercise_sections(db, [res], lang=lang)
    return res


@router.post("/courses/{course_id}/lessons", response_model=LessonRead, status_code=201)
async def create_lesson(
        course_id: int,
        data: LessonCreate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
    return await lesson_service.create_lesson(db, course_id, data)


@router.put("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def update_lesson(
        course_id: int,
        lesson_id: int,
        data: LessonUpdate,
        current_teacher: Student = Depends(get_current_teacher),
        db: AsyncSession = Depends(get_db)
):
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
    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await lesson_service.delete_lesson(db, lesson_id)
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  LESSON COMPLETION
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    existing = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    already = existing.scalar_one_or_none()
    if already is not None:
        progress = await _calc_course_progress(db, lesson.course_id, current_student.id)
        cert = await achievement_service.award_certificate(db, current_student.id, lesson.course_id)
        return {
            "message": "Dars allaqachon tugatilgan",
            "course_id": lesson.course_id,
            "already_completed": True,
            **progress,
            "certificate_issued": cert is not None,
            "certificate_id": cert.id if cert else None,
        }

    await _check_completion_gate(db, lesson, current_student.id)

    result = await lesson_service.complete_lesson(db, lesson_id, current_student.id)
    course_id = result.get("course_id")

    cert = await achievement_service.award_certificate(db, current_student.id, course_id)
    progress = await _calc_course_progress(db, course_id, current_student.id)

    try:
        from app.services.streak_service import bump_streak
        await bump_streak(db, current_student.id)
        await db.commit()
    except Exception:
        await db.rollback()

    try:
        await achievement_service.check_and_award_achievements(db, current_student.id)
    except Exception:
        pass

    return {
        **result,
        **progress,
        "certificate_issued": cert is not None,
        "certificate_id": cert.id if cert else None,
    }


@router.get("/lessons/{lesson_id}/my-exercise-submissions")
async def get_my_exercise_submissions(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Latest submission per exercise for this lesson."""
    from app.models.exercise import Exercise, ExerciseSubmission

    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    ex_id_rows = (
        await db.execute(
            select(Exercise.id).where(Exercise.lesson_id == lesson_id)
        )
    ).all()
    ex_ids = [r[0] for r in ex_id_rows]
    if not ex_ids:
        return []

    rows = (
        await db.execute(
            select(ExerciseSubmission)
            .where(
                ExerciseSubmission.student_id == current_student.id,
                ExerciseSubmission.exercise_id.in_(ex_ids),
            )
            .order_by(ExerciseSubmission.submitted_at.desc())
        )
    ).scalars().all()

    latest_by_ex: dict[int, ExerciseSubmission] = {}
    for s in rows:
        if s.exercise_id not in latest_by_ex:
            latest_by_ex[s.exercise_id] = s

    return [
        {
            "exercise_id": s.exercise_id,
            "student_answer": s.student_answer,
            "is_correct": s.is_correct,
            "score": s.score,
            "ai_feedback": s.ai_feedback,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
        }
        for s in latest_by_ex.values()
    ]


@router.get("/lessons/{lesson_id}/is-completed")
async def is_lesson_completed(
        lesson_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    lesson_res = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_res.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, lesson.course_id)

    comp_res = await db.execute(
        select(LessonCompletion).where(
            LessonCompletion.student_id == current_student.id,
            LessonCompletion.lesson_id == lesson_id
        )
    )
    completion = comp_res.scalar_one_or_none()
    progress = await _calc_course_progress(db, lesson.course_id, current_student.id)

    return {
        "lesson_id": lesson_id,
        "is_completed": completion is not None,
        "completed_at": completion.completed_at if completion else None,
        "course_id": lesson.course_id,
        **progress,
    }


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
        course_id: int,
        current_student: Optional[Student] = Depends(get_current_student_optional),
        db: AsyncSession = Depends(get_db)
):
    if not current_student:
        return {
            "course_id": course_id,
            "total_lessons": 0,
            "completed_lessons": 0,
            "progress_percentage": 0,
            "progress": 0,
            "percentage": 0,
        }

    progress = await _calc_course_progress(db, course_id, current_student.id)
    return {"course_id": course_id, **progress}


# ─────────────────────────────────────────────────────────────────────────────
#  VIDEO WATCH
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/courses/{course_id}/lessons/{lesson_id}/sections/{section_id}/watch")
async def mark_video_watched(
        course_id: int,
        lesson_id: int,
        section_id: str,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    from app.models.video_watch import VideoWatch

    lesson = await lesson_service.get_lesson_by_id(db, lesson_id)
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _ensure_enrolled(db, current_student.id, course_id)

    existing = await db.execute(
        select(VideoWatch).where(
            VideoWatch.student_id == current_student.id,
            VideoWatch.lesson_id == lesson_id,
            VideoWatch.section_id == section_id
        )
    )
    if not existing.scalar_one_or_none():
        db.add(VideoWatch(
            student_id=current_student.id,
            lesson_id=lesson_id,
            section_id=section_id
        ))
        await db.commit()

    progress_pct = await _calc_lesson_progress(db, lesson, current_student.id)
    course_progress = await _calc_course_progress(db, course_id, current_student.id)

    return {
        "watched": True,
        "lesson_progress": progress_pct,
        **course_progress
    }


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
    lock_res = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id).with_for_update()
    )
    lesson = lock_res.scalar_one_or_none()
    if not lesson or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    await _ensure_enrolled(db, current_student.id, course_id)

    existing_res = await db.execute(
        select(Submission).where(
            Submission.lesson_id == lesson_id,
            Submission.student_id == current_student.id
        )
    )
    existing_sub = existing_res.scalar_one_or_none()

    if existing_sub is not None:
        proj_res = await db.execute(
            select(Project).where(Project.id == existing_sub.project_id)
        )
        existing_project = proj_res.scalar_one_or_none()
        proj_status = existing_project.status if existing_project else existing_sub.status
        prev_points = existing_project.points_earned if existing_project else 0
        can_resubmit = (
            existing_project is not None and proj_status == "Rejected"
        )
        if not can_resubmit:
            if proj_status == "Submitted":
                raise HTTPException(
                    status_code=400,
                    detail="Loyihangiz hali tekshirilmoqda — natijani kuting"
                )
            raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

        if prev_points > 0 and proj_status == "Approved":
            await _subtract_points(db, current_student.id, prev_points)

        existing_project.status = "Submitted"
        existing_project.points_earned = 0
        existing_project.grade = None
        existing_project.instructor_feedback = None
        existing_project.reviewed_at = None
        existing_project.submitted_at = datetime.utcnow()
        existing_project.github_url = data.github_url
        existing_project.live_demo_url = data.live_demo_url
        existing_project.description = (
                data.description or lesson.task_description or "Dars loyihasi"
        )

        existing_sub.status = "Submitted"
        existing_sub.points_earned = 0
        existing_sub.grade = None
        existing_sub.instructor_feedback = None
        existing_sub.reviewed_at = None
        existing_sub.github_url = data.github_url
        existing_sub.live_demo_url = data.live_demo_url
        existing_sub.description = data.description

        await db.commit()

        await _try_auto_ai_review(db, existing_project)

        student_res = await db.execute(
            select(Student).where(Student.id == current_student.id)
        )
        student = student_res.scalar_one_or_none()
        progress = await _calc_course_progress(db, course_id, current_student.id)

        return {
            "message": "Loyiha qayta topshirildi — o'qituvchi tekshirishini kuting",
            "submission_id": existing_sub.id,
            "project_id": existing_project.id,
            "resubmitted": True,
            **progress,
            "points_earned": 0,
            "total_points": student.total_points if student else 0,
            "certificate_issued": False,
            "certificate_id": None,
        }

    new_project = Project(
        student_id=current_student.id,
        title=lesson.task_title or lesson.title,
        description=data.description or lesson.task_description or "Dars loyihasi",
        github_url=data.github_url,
        live_demo_url=data.live_demo_url,
        difficulty_level="Easy",
        status="Submitted",
        submitted_at=datetime.utcnow(),
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

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Bu dars allaqachon topshirilgan")

    await _try_auto_ai_review(db, new_project)

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
        "certificate_id": cert.id if cert else None,
    }


@router.get("/courses/{course_id}/lessons/{lesson_id}/submission")
async def get_lesson_submission(
        course_id: int,
        lesson_id: int,
        lang: Optional[str] = None,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
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
        return {"submitted": False, "pass_threshold": PROJECT_PASS_THRESHOLD}

    proj_res = await db.execute(
        select(Project).where(Project.id == submission.project_id)
    )
    project = proj_res.scalar_one_or_none()

    proj_status = project.status if project else submission.status

    # Draft means the project was never actually submitted (e.g. /submit call failed).
    # Treat it the same as no submission so the student can submit again.
    if proj_status == "Draft":
        return {"submitted": False, "pass_threshold": PROJECT_PASS_THRESHOLD}
    points_earned = project.points_earned if project else 0
    grade = project.grade if project else None
    feedback = project.instructor_feedback if project else None
    import json as _json

    def _parse_json_list(val):
        if not val:
            return []
        if isinstance(val, list):
            return val
        try:
            return _json.loads(val)
        except Exception:
            return []

    ai_bugs = _parse_json_list(project.ai_bugs if project else None)
    ai_improvements = _parse_json_list(project.ai_improvements if project else None)
    ai_strengths = _parse_json_list(project.ai_strengths if project else None)

    # The grader writes Uzbek regardless of who's reading, so translate the
    # verdict to match the rest of the page.
    if project is not None:
        feedback, ai_strengths, ai_improvements, ai_bugs = (
            await translate_project_feedback(
                db,
                project_id=project.id,
                lang=lang,
                feedback=feedback,
                strengths=ai_strengths,
                improvements=ai_improvements,
                bugs=ai_bugs,
            )
        )

    reviewed = proj_status in ("Approved", "Rejected")
    passed = (
        points_earned >= PROJECT_PASS_THRESHOLD
        and proj_status not in ("Rejected", "Draft")
    )
    can_resubmit = reviewed and not passed

    return {
        "submitted": True,
        "submission_id": submission.id,
        "project_id": submission.project_id,
        "status": proj_status,
        "github_url": submission.github_url,
        "live_demo_url": submission.live_demo_url,
        "description": submission.description,
        "points_earned": points_earned,
        "grade": grade,
        "instructor_feedback": feedback,
        "ai_bugs": ai_bugs,
        "ai_improvements": ai_improvements,
        "ai_strengths": ai_strengths,
        "reviewed": reviewed,
        "passed": passed,
        "can_resubmit": can_resubmit,
        "pass_threshold": PROJECT_PASS_THRESHOLD,
    }


# ── Sample project ────────────────────────────────────────────────────────────

@router.get("/lessons/{lesson_id}/sample")
async def get_lesson_sample(
        lesson_id: int,
        db: AsyncSession = Depends(get_db),
):
    from app.models.lesson_sample import LessonSample
    from app.schemas.lesson_sample import LessonSampleRead
    result = await db.execute(select(LessonSample).where(LessonSample.lesson_id == lesson_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample topilmadi")
    return LessonSampleRead.model_validate(sample)


# ─────────────────────────────────────────────────────────────────────────────
#  Include sub-routers
# ─────────────────────────────────────────────────────────────────────────────

from .lesson_files import router as _files_router
from .lesson_vocabulary import router as _vocab_router

router.include_router(_files_router)
router.include_router(_vocab_router)
