from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_teacher
from app.models.lesson_question import LessonQuestion
from app.models.lesson import Lesson
from app.models.user import Student

router = APIRouter()


class LessonQuestionCreate(BaseModel):
    question_text:  str       = Field(..., min_length=1)
    options:        List[str] = Field(..., min_length=2, max_length=4)
    correct_option: int       = Field(..., ge=0, le=3)
    time_limit:     int       = Field(30, ge=5, le=120)
    points:         int       = Field(6, ge=0, le=10)
    order_index:    int       = Field(0, ge=0)


class LessonQuestionRead(BaseModel):
    id:             int
    lesson_id:      int
    question_text:  str
    options:        List[str]
    correct_option: int
    time_limit:     int
    points:         int
    order_index:    int

    class Config:
        from_attributes = True


async def _require_lesson_owner(db: AsyncSession, lesson_id: int, teacher_id: int) -> Lesson:
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


# ── List questions for a lesson ───────────────────────────────────────────────
@router.get("/lessons/{lesson_id}/questions", response_model=List[LessonQuestionRead])
async def list_lesson_questions(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _require_lesson_owner(db, lesson_id, teacher.id)
    rows = (await db.execute(
        select(LessonQuestion)
        .where(LessonQuestion.lesson_id == lesson_id)
        .order_by(LessonQuestion.order_index, LessonQuestion.id)
    )).scalars().all()
    return rows


# ── Create question for a lesson ──────────────────────────────────────────────
@router.post("/lessons/{lesson_id}/questions", response_model=LessonQuestionRead, status_code=status.HTTP_201_CREATED)
async def create_lesson_question(
    lesson_id: int,
    body: LessonQuestionCreate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _require_lesson_owner(db, lesson_id, teacher.id)

    # Auto order_index if not provided
    count = (await db.execute(
        sa_text("SELECT COUNT(*) FROM lesson_questions WHERE lesson_id = :lid"),
        {"lid": lesson_id}
    )).scalar() or 0
    order = body.order_index if body.order_index else int(count)

    q = LessonQuestion(
        lesson_id=lesson_id,
        question_text=body.question_text,
        options=body.options,
        correct_option=body.correct_option,
        time_limit=body.time_limit,
        points=body.points,
        order_index=order,
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


# ── Update a lesson question ───────────────────────────────────────────────────
@router.put("/lessons/{lesson_id}/questions/{question_id}", response_model=LessonQuestionRead)
async def update_lesson_question(
    lesson_id: int,
    question_id: int,
    body: LessonQuestionCreate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _require_lesson_owner(db, lesson_id, teacher.id)
    q = (await db.execute(
        select(LessonQuestion).where(LessonQuestion.id == question_id, LessonQuestion.lesson_id == lesson_id)
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    q.question_text  = body.question_text
    q.options        = body.options
    q.correct_option = body.correct_option
    q.time_limit     = body.time_limit
    q.points         = body.points
    q.order_index    = body.order_index
    await db.commit()
    await db.refresh(q)
    return q


# ── Delete a lesson question ───────────────────────────────────────────────────
@router.delete("/lessons/{lesson_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_question(
    lesson_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _require_lesson_owner(db, lesson_id, teacher.id)
    q = (await db.execute(
        select(LessonQuestion).where(LessonQuestion.id == question_id, LessonQuestion.lesson_id == lesson_id)
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(q)
    await db.commit()


# ── List lessons for a course (used by game import UI) ────────────────────────
@router.get("/lessons-with-questions")
async def list_all_lessons_with_questions(
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    rows = (await db.execute(
        sa_text("""
            SELECT l.id, l.title, l.order, COUNT(lq.id) AS question_count,
                   COUNT(lq.id) FILTER (WHERE lq.question_kind = 'bug_hunt') AS bug_count,
                   c.id AS course_id, c.title AS course_title
            FROM lessons l
            LEFT JOIN lesson_questions lq ON lq.lesson_id = l.id
            JOIN courses c ON c.id = l.course_id
            GROUP BY l.id, l.title, l.order, c.id, c.title
            HAVING COUNT(lq.id) > 0
            ORDER BY c.title, l.order, l.id
        """)
    )).all()
    return [
        {"id": r[0], "title": r[1], "order": r[2], "question_count": r[3],
         "bug_count": r[4], "course_id": r[5], "course_title": r[6]}
        for r in rows
    ]


@router.get("/courses/{course_id}/lessons-with-questions")
async def list_lessons_with_question_counts(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    rows = (await db.execute(
        sa_text("""
            SELECT l.id, l.title, l.order, COUNT(lq.id) AS question_count
            FROM lessons l
            LEFT JOIN lesson_questions lq ON lq.lesson_id = l.id
            WHERE l.course_id = :cid
            GROUP BY l.id, l.title, l.order
            ORDER BY l.order, l.id
        """),
        {"cid": course_id}
    )).all()
    return [
        {"id": r[0], "title": r[1], "order": r[2], "question_count": r[3]}
        for r in rows
    ]
