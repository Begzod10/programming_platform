"""classroom_v2 -> student_platform progress pull (request #47, 2026-09-14).

classroom reads a student's "Web dasturlash" progress from here,
server-to-server, keyed by (source, ext_id) — the same identity pair its
own login/SSO handoff already carries (see student_platform's own
/auth/sso and app/services/sso_service.py::resolve_sso_login). This is the
separate, later pull classroom makes to render the subject card; no
browser session or JWT is involved, so auth here is a shared secret
(X-Classroom-Key), the same pattern team_game_session_reports.py uses for
the parent bot's /summary-public.

Query logic mirrors two existing endpoints that already compute this same
data, just keyed differently:
  * students.py::get_my_course_stats — per-course lesson/exercise stats,
    keyed off the current JWT session's student.
  * parent.py::_build_child_progress — certificates/projects/achievements,
    keyed off a Gennis parent id via an eager-loaded Student.
Neither can be reused directly (wrong key, wrong auth), so the query
shapes are duplicated here rather than the functions themselves.
"""
import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select, func, case, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import get_db
from app.models.user import Student
from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.student_achievement import StudentAchievement
from app.models.dictionary import UserDictionary

router = APIRouter()


def _require_classroom_secret(x_classroom_key: Optional[str]) -> None:
    """Same shape as team_game_session_reports.py's _require_internal_secret
    — 503 when the integration isn't configured at all, 401 for a wrong key.
    Deliberately its own CLASSROOM_INTEGRATION_SECRET, not PARENT_BOT_SECRET
    or SSO_SHARED_SECRET (request #47 asked for it kept separate)."""
    expected = settings.CLASSROOM_INTEGRATION_SECRET
    if not expected:
        raise HTTPException(status_code=503, detail="Classroom integration not configured")
    if not x_classroom_key or not hmac.compare_digest(x_classroom_key, expected):
        raise HTTPException(status_code=401, detail="Invalid classroom key")


async def _load_student_by_source(db: AsyncSession, source: str, ext_id: int) -> Optional[Student]:
    # gennis and turon id spaces are independent and overlap (request #47
    # §4) — the caller must always pass both, never just a bare id.
    if source == "gennis":
        column = Student.gennis_id
    elif source == "turon":
        column = Student.turon_id
    else:
        raise HTTPException(status_code=400, detail="source must be 'gennis' or 'turon'")

    stmt = (
        select(Student)
        .where(column == ext_id)
        .options(
            selectinload(Student.certificates),
            selectinload(Student.projects),
            selectinload(Student.student_achievements).selectinload(StudentAchievement.achievement),
        )
    )
    row = await db.execute(stmt)
    return row.scalar_one_or_none()


@router.get("/progress")
async def get_classroom_progress(
    source: str = Query(..., description="'gennis' or 'turon'"),
    ext_id: int = Query(..., description="gennis_id or turon_id, matching `source`"),
    x_classroom_key: Optional[str] = Header(default=None, alias="X-Classroom-Key"),
    db: AsyncSession = Depends(get_db),
):
    _require_classroom_secret(x_classroom_key)

    student = await _load_student_by_source(db, source, ext_id)
    if student is None:
        return {"found": False, "source": source, "ext_id": ext_id}

    sid = student.id

    # ── Enrolled courses + category/prerequisite metadata ──────────────────
    # Goes through the student_courses association table directly, same as
    # students.py's course-stats — Student has no enrolled-courses-by-id
    # relationship convenient for a WHERE clause, and this is one query
    # either way.
    course_id_rows = (await db.execute(
        sa_text("SELECT course_id FROM student_courses WHERE student_id = :sid"),
        {"sid": sid},
    )).all()
    course_ids = [r[0] for r in course_id_rows]

    courses_by_id: dict[int, Course] = {}
    if course_ids:
        rows = (await db.execute(
            select(Course)
            .where(Course.id.in_(course_ids))
            .options(selectinload(Course.category))
        )).scalars().all()
        courses_by_id = {c.id: c for c in rows}

    # ── Per-course lesson completion ────────────────────────────────────────
    lessons_by_course: dict[int, dict] = {}
    if course_ids:
        total_q = await db.execute(
            select(Lesson.course_id, func.count(Lesson.id))
            .where(Lesson.course_id.in_(course_ids))
            .group_by(Lesson.course_id)
        )
        for cid, cnt in total_q.all():
            lessons_by_course[cid] = {"total": cnt, "done": 0}

        done_q = await db.execute(
            select(Lesson.course_id, func.count(LessonCompletion.id))
            .join(LessonCompletion, Lesson.id == LessonCompletion.lesson_id)
            .where(LessonCompletion.student_id == sid, Lesson.course_id.in_(course_ids))
            .group_by(Lesson.course_id)
        )
        for cid, cnt in done_q.all():
            if cid in lessons_by_course:
                lessons_by_course[cid]["done"] = cnt

    # ── Per-course exercise stats (correct answers, once per exercise) ─────
    exercises_by_course: dict[int, dict] = {}
    if course_ids:
        ex_q = await db.execute(
            select(
                Lesson.course_id,
                func.count(func.distinct(Exercise.id)),
                func.count(func.distinct(case(
                    (ExerciseSubmission.is_correct == True, Exercise.id)  # noqa: E712
                ))),
            )
            .select_from(Lesson)
            .join(Exercise, Exercise.lesson_id == Lesson.id)
            .outerjoin(
                ExerciseSubmission,
                (ExerciseSubmission.exercise_id == Exercise.id)
                & (ExerciseSubmission.student_id == sid),
            )
            .where(Lesson.course_id.in_(course_ids))
            .group_by(Lesson.course_id)
        )
        for cid, total, correct in ex_q.all():
            exercises_by_course[cid] = {"total": total or 0, "correct": correct or 0}

    courses_out = []
    for cid in course_ids:
        c = courses_by_id.get(cid)
        if c is None:
            continue
        les = lessons_by_course.get(cid, {"total": 0, "done": 0})
        ex = exercises_by_course.get(cid, {"total": 0, "correct": 0})
        courses_out.append({
            "id": c.id,
            "title": c.title,
            "category": c.category.name if c.category else None,
            "display_order": c.display_order,
            "prerequisite_course_id": c.prerequisite_course_id,
            "lessons_total": les["total"],
            "lessons_done": les["done"],
            "exercises_total": ex["total"],
            "exercises_correct": ex["correct"],
            "progress_pct": round((les["done"] / les["total"] * 100) if les["total"] > 0 else 0),
            "enrolled": True,
        })
    courses_out.sort(key=lambda c: (c["display_order"] or 0, c["title"]))

    # ── Overall exercise/project totals (mirrors students.py's course-stats) ──
    ov_ex = (await db.execute(
        select(
            func.count(func.distinct(Exercise.id)),
            func.count(func.distinct(case(
                (ExerciseSubmission.is_correct == True, Exercise.id)  # noqa: E712
            ))),
        )
        .select_from(ExerciseSubmission)
        .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
        .where(ExerciseSubmission.student_id == sid)
    )).one()
    ex_total, ex_correct = ov_ex[0] or 0, ov_ex[1] or 0

    # ── Projects (student's own portfolio pieces — Project, not Submission) ──
    projects_out = [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "grade": p.grade,
            "points_earned": p.points_earned,
            "github_url": p.github_url,
            "submitted_at": p.submitted_at.isoformat() if p.submitted_at else None,
        }
        for p in student.projects
    ]
    projects_approved = sum(1 for p in student.projects if p.status in ("Approved", "Reviewed"))
    projects_submitted = sum(1 for p in student.projects if p.status == "Submitted")
    graded = [p for p in student.projects if p.grade and p.grade.isdigit()]
    avg_grade = round(sum(int(p.grade) for p in graded) / len(graded), 1) if graded else None

    achievements_out = [
        {
            "title": sa.achievement.name,
            "icon": sa.achievement.icon,
            "category": sa.achievement.category,
            "earned_at": sa.earned_at.isoformat() if sa.earned_at else None,
        }
        for sa in student.student_achievements
        if sa.achievement
    ]

    vocab_count = (await db.execute(
        select(func.count(UserDictionary.id)).where(UserDictionary.student_id == sid)
    )).scalar_one()

    return {
        "found": True,
        "source": source,
        "ext_id": ext_id,
        "student_id": sid,
        "username": student.username,
        "full_name": student.full_name,
        "level": student.current_level.value if student.current_level else "Beginner",

        "profile": {
            "total_points": student.total_points,
            "lifetime_points": student.lifetime_points,
            "global_rank": student.global_rank,
            "current_streak": student.current_streak,
            "longest_streak": student.longest_streak,
            "current_level": student.current_level.value if student.current_level else "Beginner",
        },

        "overall": {
            "exercises_total": ex_total,
            "exercises_correct": ex_correct,
            "exercises_pct": round((ex_correct / ex_total * 100) if ex_total > 0 else 0),
            "projects_total": len(student.projects),
            "projects_approved": projects_approved,
            "projects_submitted": projects_submitted,
            "avg_grade": avg_grade,
            "points": student.total_points,
        },

        "courses": courses_out,
        "projects": projects_out,
        "certificates_count": len(student.certificates),
        "achievements": achievements_out,
        "vocabulary_count": vocab_count,
    }
