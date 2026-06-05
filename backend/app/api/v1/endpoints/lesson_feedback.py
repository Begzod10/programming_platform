"""Lesson-level rating + comment endpoints.

Students rate a lesson 1-5 stars and optionally drop a comment.
Teachers (course owners) see per-lesson aggregates + recent comments
so they can spot lessons that need rework.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_student, get_current_teacher
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.lesson_feedback import LessonFeedback
from app.models.user import Student
from app.schemas.lesson_feedback import (
    CourseFeedbackOverview,
    LessonFeedbackComment,
    LessonFeedbackIn,
    LessonFeedbackOut,
    LessonFeedbackSummary,
)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
#  STUDENT — submit & read own feedback
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/lessons/{lesson_id}/feedback",
    response_model=LessonFeedbackOut,
    status_code=status.HTTP_200_OK,
)
async def submit_lesson_feedback(
    lesson_id: int,
    payload: LessonFeedbackIn,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> LessonFeedbackOut:
    """Upsert the student's feedback for a lesson.

    Re-submitting overwrites the previous rating/comment so a student can
    revise their score after revisiting a lesson.
    """
    lesson = (
        await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    ).scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")

    existing = (
        await db.execute(
            select(LessonFeedback).where(
                LessonFeedback.lesson_id == lesson_id,
                LessonFeedback.student_id == current_student.id,
            )
        )
    ).scalar_one_or_none()

    comment = (payload.comment or "").strip() or None

    if existing is None:
        existing = LessonFeedback(
            student_id=current_student.id,
            lesson_id=lesson_id,
            rating=payload.rating,
            comment=comment,
        )
        db.add(existing)
    else:
        existing.rating = payload.rating
        existing.comment = comment

    await db.commit()
    await db.refresh(existing)
    return LessonFeedbackOut.model_validate(existing)


@router.get(
    "/lessons/{lesson_id}/feedback/my",
    response_model=Optional[LessonFeedbackOut],
)
async def get_my_lesson_feedback(
    lesson_id: int,
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Optional[LessonFeedbackOut]:
    """Prefill the feedback widget with whatever the student last submitted."""
    row = (
        await db.execute(
            select(LessonFeedback).where(
                LessonFeedback.lesson_id == lesson_id,
                LessonFeedback.student_id == current_student.id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        return None
    return LessonFeedbackOut.model_validate(row)


# ─────────────────────────────────────────────────────────────────────────────
#  TEACHER — per-course aggregate + per-lesson comments
# ─────────────────────────────────────────────────────────────────────────────

async def _require_course_owner(
    db: AsyncSession, course_id: int, teacher: Student
) -> Course:
    course = (
        await db.execute(select(Course).where(Course.id == course_id))
    ).scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    if course.instructor_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kursning instruktori emassiz",
        )
    return course


@router.get(
    "/teacher/courses/{course_id}/lesson-feedback",
    response_model=CourseFeedbackOverview,
)
async def teacher_course_feedback_overview(
    course_id: int,
    current_teacher: Student = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
) -> CourseFeedbackOverview:
    """One row per lesson: avg rating, count, breakdown by star."""
    course = await _require_course_owner(db, course_id, current_teacher)

    lessons = (
        await db.execute(
            select(Lesson)
            .where(Lesson.course_id == course_id)
            .order_by(Lesson.order)
        )
    ).scalars().all()
    lesson_ids = [l.id for l in lessons]

    if lesson_ids:
        breakdown_rows = (
            await db.execute(
                select(
                    LessonFeedback.lesson_id,
                    LessonFeedback.rating,
                    func.count(LessonFeedback.id).label("c"),
                )
                .where(LessonFeedback.lesson_id.in_(lesson_ids))
                .group_by(LessonFeedback.lesson_id, LessonFeedback.rating)
            )
        ).all()
    else:
        breakdown_rows = []

    per_lesson: dict[int, dict] = {
        lid: {"count": 0, "total": 0, "breakdown": {str(i): 0 for i in range(1, 6)}}
        for lid in lesson_ids
    }
    for lesson_id, rating, c in breakdown_rows:
        bucket = per_lesson[lesson_id]
        bucket["count"] += c
        bucket["total"] += rating * c
        bucket["breakdown"][str(rating)] = c

    summaries: List[LessonFeedbackSummary] = []
    total_responses = 0
    weighted_sum = 0
    for lesson in lessons:
        b = per_lesson[lesson.id]
        avg = round(b["total"] / b["count"], 2) if b["count"] else None
        total_responses += b["count"]
        weighted_sum += b["total"]
        summaries.append(
            LessonFeedbackSummary(
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                lesson_order=lesson.order,
                response_count=b["count"],
                average_rating=avg,
                rating_breakdown=b["breakdown"],
            )
        )

    course_avg = round(weighted_sum / total_responses, 2) if total_responses else None
    return CourseFeedbackOverview(
        course_id=course.id,
        course_title=course.title,
        total_responses=total_responses,
        average_rating=course_avg,
        lessons=summaries,
    )


@router.get(
    "/teacher/lessons/{lesson_id}/feedback",
    response_model=List[LessonFeedbackComment],
)
async def teacher_lesson_feedback_comments(
    lesson_id: int,
    limit: int = 50,
    current_teacher: Student = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
) -> List[LessonFeedbackComment]:
    """Most recent comments for a single lesson — for the drill-down view."""
    lesson = (
        await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    ).scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    await _require_course_owner(db, lesson.course_id, current_teacher)

    limit = max(1, min(limit, 200))
    rows = (
        await db.execute(
            select(LessonFeedback, Student.full_name)
            .join(Student, Student.id == LessonFeedback.student_id)
            .where(LessonFeedback.lesson_id == lesson_id)
            .order_by(LessonFeedback.updated_at.desc())
            .limit(limit)
        )
    ).all()

    out: List[LessonFeedbackComment] = []
    for fb, student_name in rows:
        out.append(
            LessonFeedbackComment(
                id=fb.id,
                rating=fb.rating,
                comment=fb.comment,
                created_at=fb.created_at,
                updated_at=fb.updated_at,
                student_id=fb.student_id,
                student_name=student_name,
            )
        )
    return out
