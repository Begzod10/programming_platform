import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, case, or_
from app.config import settings
from app.dependencies import get_db
from app.models.user import Student
from app.models.lesson import LessonCompletion, Lesson
from app.models.exercise import ExerciseSubmission, Exercise
from app.models.submission import Submission
from app.models.course import Course, student_courses
from app.models.ranking import Ranking

router = APIRouter()

_TASHKENT = ZoneInfo("Asia/Tashkent")


def _day_start_utc(now: Optional[datetime] = None) -> datetime:
    """Today's 00:00 Asia/Tashkent as an aware UTC datetime ("today" for the group report)."""
    local = (now or datetime.now(timezone.utc)).astimezone(_TASHKENT)
    return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def _week_start_utc(now: Optional[datetime] = None) -> datetime:
    """Monday 00:00 Asia/Tashkent of the current week, as an aware UTC datetime — the same moment the weekly
    points reset (scheduler `job_reset_weekly`), so lessons/exercises cover exactly the points' week."""
    local = (now or datetime.now(timezone.utc)).astimezone(_TASHKENT)
    monday = (local - timedelta(days=local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return monday.astimezone(timezone.utc)


# request #47 §5 (2026-09-14): these two endpoints had NO auth at all —
# anyone who could reach the host could read any student's name or full
# stats. Same shared-secret pattern as team_game_session_reports.py's
# _require_internal_secret / this module's own PARENT_BOT_SECRET (the
# actual consumer of these two — the Telegram parent bot's search flow).
def _require_bot_secret(x_internal_secret: Optional[str]) -> None:
    expected = settings.PARENT_BOT_SECRET
    if not expected:
        raise HTTPException(status_code=503, detail="Bot integration not configured")
    if not x_internal_secret or not hmac.compare_digest(x_internal_secret, expected):
        raise HTTPException(status_code=401, detail="Invalid internal secret")


@router.get("/search-student")
async def search_student(
        q: str,
        db: AsyncSession = Depends(get_db),
        x_internal_secret: Optional[str] = Header(default=None, alias="X-Internal-Secret"),
):
    _require_bot_secret(x_internal_secret)
    from sqlalchemy import and_
    q = q.strip()
    if len(q) < 2:
        return []

    words = [w for w in q.split() if len(w) >= 2]
    reversed_q = " ".join(reversed(words)) if len(words) > 1 else q

    # Build conditions: exact phrase, reversed phrase, username, each word
    conditions = [
        Student.full_name.ilike(f"%{q}%"),
        Student.full_name.ilike(f"%{reversed_q}%"),
        Student.username.ilike(f"%{q}%"),
    ]
    # Multi-word: match if ALL words appear (any order, correct spelling)
    if len(words) > 1:
        conditions.append(and_(*[Student.full_name.ilike(f"%{w}%") for w in words]))
    # Fallback: also match any single word >= 5 chars — catches spelling variants
    # e.g. "Karimov Shohruz" will still find "Shoxruz Karimov" via "Karimov"
    for w in words:
        if len(w) >= 5:
            conditions.append(Student.full_name.ilike(f"%{w}%"))

    results = await db.execute(
        select(Student).where(or_(*conditions)).limit(10)
    )
    # Deduplicate (a student might match multiple conditions)
    seen, students = set(), []
    for s in results.scalars().all():
        if s.id not in seen:
            seen.add(s.id)
            students.append(s)
    return [
        {"id": s.id, "name": s.full_name or s.username or f"Student #{s.id}"}
        for s in students
    ]


@router.get("/student-stats/{student_id}")
async def get_student_stats(
        student_id: int,
        db: AsyncSession = Depends(get_db),
        x_internal_secret: Optional[str] = Header(default=None, alias="X-Internal-Secret"),
):
    _require_bot_secret(x_internal_secret)
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

    # This week's activity (all courses, published or not — it is the student's effort that counts).
    week_start = _week_start_utc()
    weekly_lessons = (await db.execute(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.student_id == student_id, LessonCompletion.completed_at >= week_start)
    )).scalar() or 0
    ex_row = (await db.execute(
        select(func.count(ExerciseSubmission.id),
               func.sum(case((ExerciseSubmission.is_correct == True, 1), else_=0)))
        .where(ExerciseSubmission.student_id == student_id, ExerciseSubmission.submitted_at >= week_start)
    )).one()
    weekly_exercises = {"total": int(ex_row[0] or 0), "correct": int(ex_row[1] or 0)}

    # Today's activity for the group report. Exercise points are what was ACTUALLY awarded (score is 0 on a
    # repeat solve); project points are those graded today, whenever the project was submitted.
    day_start = _day_start_utc()
    dx = (await db.execute(
        select(func.count(ExerciseSubmission.id),
               func.sum(case((ExerciseSubmission.is_correct == True, 1), else_=0)),
               func.sum(func.coalesce(ExerciseSubmission.score, 0)))
        .where(ExerciseSubmission.student_id == student_id, ExerciseSubmission.submitted_at >= day_start)
    )).one()
    daily_exercises = {"total": int(dx[0] or 0), "correct": int(dx[1] or 0), "points": int(dx[2] or 0)}
    submitted_today = (await db.execute(
        select(func.count(Submission.id)).where(
            Submission.student_id == student_id, Submission.submitted_at >= day_start)
    )).scalar() or 0
    graded_points = (await db.execute(
        select(func.sum(Submission.points_earned)).where(
            Submission.student_id == student_id, Submission.points_earned > 0,
            Submission.updated_at >= day_start)
    )).scalar() or 0
    daily_projects = {"submitted": int(submitted_today), "points": int(graded_points)}

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
        # weekly_points only receives the day's points at the nightly rollover; weekly_rank is ordered by
        # weekly + daily, so the two must be reported together or the number and the place disagree.
        "weekly_points": (ranking.weekly_points + ranking.daily_points) if ranking else 0,
        "weekly_rank": ranking.weekly_rank if ranking else 0,
        "weekly_lessons": weekly_lessons,
        "weekly_exercises": weekly_exercises,
        "daily_exercises": daily_exercises,
        "daily_projects": daily_projects,
        "courses": courses_data,
    }
