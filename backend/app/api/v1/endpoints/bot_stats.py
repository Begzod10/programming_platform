from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, case
from app.dependencies import get_db
from app.models.user import Student
from app.models.lesson import LessonCompletion, Lesson
from app.models.exercise import ExerciseSubmission, Exercise
from app.models.submission import Submission
from app.models.course import Course, student_courses
from app.models.ranking import Ranking

router = APIRouter()


@router.get("/search-student")
async def search_student(q: str, db: AsyncSession = Depends(get_db)):
    if len(q.strip()) < 2:
        return []
    results = await db.execute(
        select(Student).where(
            (Student.full_name.ilike(f"%{q}%")) |
            (Student.username.ilike(f"%{q}%"))
        ).limit(10)
    )
    students = results.scalars().all()
    return [
        {"id": s.id, "name": s.full_name or s.username or f"Student #{s.id}"}
        for s in students
    ]


@router.get("/student-stats/{student_id}")
async def get_student_stats(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Enrolled courses — only published
    enrolled_q = await db.execute(
        select(Course).join(
            student_courses,
            Course.id == student_courses.c.course_id
        ).where(
            student_courses.c.student_id == student_id,
            Course.is_published == True,
        )
    )
    courses = enrolled_q.scalars().all()
    course_ids = [c.id for c in courses]

    # Lessons per course
    lessons_by_course: dict = {}
    if course_ids:
        total_q = await db.execute(
            select(Lesson.course_id, func.count(Lesson.id))
            .where(Lesson.course_id.in_(course_ids))
            .group_by(Lesson.course_id)
        )
        for cid, cnt in total_q.all():
            lessons_by_course[cid] = {"total": cnt, "completed": 0}

        done_q = await db.execute(
            select(Lesson.course_id, func.count(LessonCompletion.id))
            .join(LessonCompletion, Lesson.id == LessonCompletion.lesson_id)
            .where(
                LessonCompletion.student_id == student_id,
                Lesson.course_id.in_(course_ids)
            )
            .group_by(Lesson.course_id)
        )
        for cid, cnt in done_q.all():
            if cid in lessons_by_course:
                lessons_by_course[cid]["completed"] = cnt

    # Exercise stats per course (ExerciseSubmission → Exercise → Lesson)
    exercises_by_course: dict = {}
    if course_ids:
        ex_q = await db.execute(
            select(
                Lesson.course_id,
                func.count(ExerciseSubmission.id),
                func.sum(case((ExerciseSubmission.is_correct == True, 1), else_=0))
            )
            .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
            .join(Lesson, Lesson.id == Exercise.lesson_id)
            .where(
                ExerciseSubmission.student_id == student_id,
                Lesson.course_id.in_(course_ids)
            )
            .group_by(Lesson.course_id)
        )
        for cid, total, correct in ex_q.all():
            exercises_by_course[cid] = {"total": total, "correct": int(correct or 0)}

    # Project submissions per course
    projects_by_course: dict = {}
    if course_ids:
        sub_q = await db.execute(
            select(Lesson.course_id, Submission.status, Submission.grade,
                   Submission.points_earned, Lesson.title)
            .join(Submission, Submission.lesson_id == Lesson.id)
            .where(
                Submission.student_id == student_id,
                Lesson.course_id.in_(course_ids)
            )
            .order_by(Lesson.course_id)
        )
        for cid, status, grade, pts, lesson_title in sub_q.all():
            projects_by_course.setdefault(cid, []).append({
                "lesson": lesson_title,
                "status": status,
                "grade": grade,
                "points": pts,
            })

    # Ranking
    ranking_q = await db.execute(
        select(Ranking).where(Ranking.student_id == student_id)
    )
    ranking = ranking_q.scalar_one_or_none()

    courses_data = []
    for c in courses:
        cid = c.id
        lesson_info = lessons_by_course.get(cid, {"total": 0, "completed": 0})
        courses_data.append({
            "id": cid,
            "title": c.title,
            "lessons_total": lesson_info["total"],
            "lessons_completed": lesson_info["completed"],
            "exercises": exercises_by_course.get(cid, {"total": 0, "correct": 0}),
            "projects": projects_by_course.get(cid, []),
        })

    return {
        "student_id": student_id,
        "name": student.full_name or student.username or "",
        "total_points": ranking.total_points if ranking else 0,
        "global_rank": ranking.global_rank if ranking else 0,
        "weekly_points": ranking.weekly_points if ranking else 0,
        "courses": courses_data,
    }
