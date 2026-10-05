"""Builds each student's knowledge/skill snapshot for the team-project AI
planner — see app/schemas/team_project.py::SkillProfile for the shape and
why this is a separate signal from Student.current_level.

Everything here is batched per group (one query per table, grouped in
Python afterward) rather than per-student, so building N profiles costs a
constant handful of queries instead of N times that.

`exercise_accuracy_by_topic` merges two different groupings into one flat
dict: course category name (e.g. "Web Asoslari") and exercise type (e.g.
"multiple_choice"). The spec text ("group ExerciseSubmission by the parent
Course.category name and by Exercise.exercise_type") reads as two axes, not
one composite key — the worked example in the spec ("Strong on
multiple_choice (91%)") only shows the exercise_type axis, so this treats
both as independent topic keys landing in the same dict. On the rare
collision between a category name and an exercise_type string, the
exercise_type entry wins (computed second) — noted here since it's a
judgment call, not a discovered convention.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.category import Category
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.group import student_groups
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.models.student_achievement import CourseCertificate
from app.models.user import Student
from app.schemas.team_project import (
    SkillProfile, SkillProfileCompletedCourse, SkillProfilePastProject,
)
from app.utils.constants import GRADE_MULTIPLIERS

MIN_ATTEMPTS_FOR_ACCURACY = 5
# What a student is studying NOW matters more than what they did months ago:
# someone who finished Django long ago and is now on JavaScript should get
# JavaScript work. Anything done inside this window counts as "current focus".
RECENT_WINDOW = timedelta(days=30)
MAX_PAST_PROJECTS = 5
PAST_PROJECT_TEXT_LIMIT = 300


async def build_group_skill_profiles(db: AsyncSession, group_id: int) -> List[SkillProfile]:
    students = (await db.execute(
        select(Student)
        .join(student_groups, student_groups.c.student_id == Student.id)
        .where(student_groups.c.group_id == group_id)
    )).scalars().all()
    if not students:
        return []
    return await _build_profiles(db, students)


async def build_profiles_for_student_ids(db: AsyncSession, student_ids: List[int]) -> List[SkillProfile]:
    """Same as build_group_skill_profiles, but for an explicit id list —
    the team-projects create flow no longer assumes "the roster" is one
    Group's full membership (a teacher can hand-pick students across
    several of their groups), so team formation needs a profile builder
    that isn't tied to a single group_id."""
    if not student_ids:
        return []
    students = (await db.execute(
        select(Student).where(Student.id.in_(student_ids))
    )).scalars().all()
    if not students:
        return []
    return await _build_profiles(db, students)


async def build_skill_profile(db: AsyncSession, student_id: int) -> Optional[SkillProfile]:
    student = (await db.execute(
        select(Student).where(Student.id == student_id)
    )).scalar_one_or_none()
    if student is None:
        return None
    profiles = await _build_profiles(db, [student])
    return profiles[0] if profiles else None


async def _build_profiles(db: AsyncSession, students: List[Student]) -> List[SkillProfile]:
    student_ids = [s.id for s in students]

    (
        certified_courses_by_student,
        lesson_completions_by_student,
        accuracy_by_student,
        projects_by_student,
    ) = await _fetch_group_signals(db, student_ids)

    profiles = []
    for student in students:
        certified = certified_courses_by_student.get(student.id, {})
        lesson_rows = lesson_completions_by_student.get(student.id, [])
        accuracy = accuracy_by_student.get(student.id, {})
        projects = projects_by_student.get(student.id, [])

        completed_lessons_by_course: Dict[int, int] = {}
        code_languages: set = set()
        recent_since = datetime.now(timezone.utc) - RECENT_WINDOW
        recent_lessons_by_title: Dict[str, int] = {}
        recent_languages: set = set()
        for course_id, code_language, completed_at, course_title in lesson_rows:
            completed_lessons_by_course[course_id] = completed_lessons_by_course.get(course_id, 0) + 1
            if code_language:
                code_languages.add(code_language.strip().lower())
            if _is_recent(completed_at, recent_since):
                recent_lessons_by_title[course_title] = recent_lessons_by_title.get(course_title, 0) + 1
                if code_language:
                    recent_languages.add(code_language.strip().lower())

        completed_courses = await _resolve_completed_courses(
            db, certified, completed_lessons_by_course,
        )

        past_projects = [
            SkillProfilePastProject(
                title=p.title,
                technologies_used=(
                    [t.strip().lower() for t in p.technologies_used.split(",") if t.strip()]
                    if p.technologies_used else []
                ),
                grade=p.grade,
                ai_strengths=(p.ai_strengths or "")[:PAST_PROJECT_TEXT_LIMIT] or None,
                ai_improvements=(p.ai_improvements or "")[:PAST_PROJECT_TEXT_LIMIT] or None,
            )
            for p in sorted(
                [p for p in projects if p.reviewed_at is not None],
                key=lambda p: p.reviewed_at, reverse=True,
            )[:MAX_PAST_PROJECTS]
        ]

        technologies_seen = sorted({
            t.strip().lower()
            for p in projects if p.technologies_used
            for t in p.technologies_used.split(",") if t.strip()
        } | code_languages)

        recent_technologies = sorted(recent_languages | {
            t.strip().lower()
            for p in projects
            if p.technologies_used and _is_recent(p.submitted_at or p.reviewed_at, recent_since)
            for t in p.technologies_used.split(",") if t.strip()
        })

        summary = _build_summary(
            student, completed_courses, completed_lessons_by_course,
            accuracy, past_projects, technologies_seen,
            recent_courses=recent_lessons_by_title,
            recent_technologies=recent_technologies,
        )

        profiles.append(SkillProfile(
            student_id=student.id,
            full_name=student.full_name or student.username,
            current_level=student.current_level,
            lifetime_points=student.lifetime_points,
            completed_courses=completed_courses,
            completed_lessons_by_course=completed_lessons_by_course,
            exercise_accuracy_by_topic=accuracy,
            past_projects=past_projects,
            technologies_seen=technologies_seen,
            streak=student.current_streak,
            last_activity_date=student.last_activity_date,
            summary=summary,
        ))
    return profiles


async def _fetch_group_signals(db: AsyncSession, student_ids: List[int]):
    """One query per signal for the whole group of student_ids."""

    # 1. Explicit certificates.
    cert_rows = (await db.execute(
        select(CourseCertificate.student_id, CourseCertificate.course_id)
        .where(CourseCertificate.student_id.in_(student_ids))
    )).all()
    certified_courses_by_student: Dict[int, set] = {}
    for sid, course_id in cert_rows:
        certified_courses_by_student.setdefault(sid, set()).add(course_id)

    # 2. Lesson completions, joined for course_id + code_language (used for
    #    both completed_lessons_by_course and technologies_seen).
    completion_rows = (await db.execute(
        select(LessonCompletion.student_id, Lesson.course_id, Lesson.code_language,
               LessonCompletion.completed_at, Course.title)
        .select_from(LessonCompletion)
        .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
        .join(Course, Course.id == Lesson.course_id)
        .where(LessonCompletion.student_id.in_(student_ids))
    )).all()
    lesson_completions_by_student: Dict[int, list] = {}
    for sid, course_id, code_language, completed_at, course_title in completion_rows:
        lesson_completions_by_student.setdefault(sid, []).append(
            (course_id, code_language, completed_at, course_title))

    # 3a. Exercise accuracy grouped by course category name.
    correct_expr = func.sum(case((ExerciseSubmission.is_correct == True, 1), else_=0))
    by_category = (await db.execute(
        select(
            ExerciseSubmission.student_id, Category.name,
            func.count(ExerciseSubmission.id), correct_expr,
        )
        .select_from(ExerciseSubmission)
        .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
        .join(Lesson, Lesson.id == Exercise.lesson_id)
        .join(Course, Course.id == Lesson.course_id)
        .outerjoin(Category, Category.id == Course.category_id)
        .where(ExerciseSubmission.student_id.in_(student_ids))
        .group_by(ExerciseSubmission.student_id, Category.name)
    )).all()

    # 3b. Exercise accuracy grouped by exercise_type.
    by_type = (await db.execute(
        select(
            ExerciseSubmission.student_id, Exercise.exercise_type,
            func.count(ExerciseSubmission.id), correct_expr,
        )
        .select_from(ExerciseSubmission)
        .join(Exercise, Exercise.id == ExerciseSubmission.exercise_id)
        .where(ExerciseSubmission.student_id.in_(student_ids))
        .group_by(ExerciseSubmission.student_id, Exercise.exercise_type)
    )).all()

    accuracy_by_student: Dict[int, Dict[str, float]] = {}
    for sid, topic, attempts, correct in [*by_category, *by_type]:
        if not topic or attempts < MIN_ATTEMPTS_FOR_ACCURACY:
            continue
        accuracy_by_student.setdefault(sid, {})[topic] = round((correct or 0) / attempts, 3)

    # 4. All projects (reviewed or not — technologies_seen wants every
    #    project; past_projects filters to reviewed_at is not None itself).
    project_rows = (await db.execute(
        select(Project).where(Project.student_id.in_(student_ids))
    )).scalars().all()
    projects_by_student: Dict[int, list] = {}
    for p in project_rows:
        projects_by_student.setdefault(p.student_id, []).append(p)

    return (
        certified_courses_by_student, lesson_completions_by_student,
        accuracy_by_student, projects_by_student,
    )


async def _resolve_completed_courses(
    db: AsyncSession,
    certified_course_ids: set,
    completed_lessons_by_course: Dict[int, int],
) -> List[SkillProfileCompletedCourse]:
    """A course counts as completed if either a CourseCertificate exists for
    it, or LessonCompletion coverage is 100% (mirrors
    achievement_service.py::check_course_completion's own is_active-only
    lesson count — a certificate should normally already exist by the time
    coverage hits 100%, but this is a coverage fallback in case one wasn't
    issued for some reason, matching the "verify the actual data, don't
    trust one mechanism" approach the rest of this codebase uses)."""
    candidate_course_ids = set(certified_course_ids) | set(completed_lessons_by_course.keys())
    if not candidate_course_ids:
        return []

    total_lessons_by_course = dict((await db.execute(
        select(Lesson.course_id, func.count(Lesson.id))
        .where(Lesson.course_id.in_(candidate_course_ids), Lesson.is_active == True)
        .group_by(Lesson.course_id)
    )).all())

    completed_ids = set(certified_course_ids)
    for course_id, completed_count in completed_lessons_by_course.items():
        total = total_lessons_by_course.get(course_id, 0)
        if total > 0 and completed_count >= total:
            completed_ids.add(course_id)
    if not completed_ids:
        return []

    course_rows = (await db.execute(
        select(Course.id, Course.title, Category.name)
        .outerjoin(Category, Category.id == Course.category_id)
        .where(Course.id.in_(completed_ids))
    )).all()
    return [
        SkillProfileCompletedCourse(course_id=cid, title=title, category=category_name)
        for cid, title, category_name in course_rows
    ]


def _is_recent(moment: Optional[datetime], since: datetime) -> bool:
    if moment is None:
        return False
    if moment.tzinfo is None:  # SQLite hands back naive datetimes
        moment = moment.replace(tzinfo=timezone.utc)
    return moment >= since


def _average_grade(projects: List[SkillProfilePastProject]) -> Optional[str]:
    graded = [GRADE_MULTIPLIERS[p.grade] for p in projects if p.grade in GRADE_MULTIPLIERS]
    if not graded:
        return None
    avg = sum(graded) / len(graded)
    # Nearest letter by multiplier distance — same scale award_points-style
    # code elsewhere in this codebase already uses (app/utils/constants.py).
    return min(GRADE_MULTIPLIERS, key=lambda g: abs(GRADE_MULTIPLIERS[g] - avg))


def _build_summary(
    student: Student,
    completed_courses: List[SkillProfileCompletedCourse],
    completed_lessons_by_course: Dict[int, int],
    accuracy: Dict[str, float],
    past_projects: List[SkillProfilePastProject],
    technologies_seen: List[str],
    recent_courses: Optional[Dict[str, int]] = None,
    recent_technologies: Optional[List[str]] = None,
) -> str:
    """Deterministic (no AI) 2-3 sentence summary — this is what actually
    goes into the team-project planner's prompt in Phase 3."""
    parts = [f"{student.current_level.value}."]

    if completed_courses:
        course_bits = []
        for c in completed_courses[:3]:
            n = completed_lessons_by_course.get(c.course_id, 0)
            course_bits.append(f"{c.title} ({n}/{n} lessons)" if n else c.title)
        extra = f" and {len(completed_courses) - 3} more" if len(completed_courses) > 3 else ""
        parts.append(f"Completed {', '.join(course_bits)}{extra}.")

    if accuracy:
        ranked = sorted(accuracy.items(), key=lambda kv: kv[1], reverse=True)
        strong = ranked[0]
        weak = ranked[-1]
        if strong[0] != weak[0]:
            parts.append(
                f"Strong on {strong[0]} ({strong[1]:.0%}), weaker on {weak[0]} ({weak[1]:.0%})."
            )
        else:
            parts.append(f"Accuracy on {strong[0]}: {strong[1]:.0%}.")

    if past_projects:
        avg_grade = _average_grade(past_projects)
        grade_bit = f", avg grade {avg_grade}" if avg_grade else ""
        parts.append(f"{len(past_projects)} past project{'s' if len(past_projects) != 1 else ''}{grade_bit}.")

    if recent_courses:
        studying = ", ".join(
            f"{title} ({n} lesson{'s' if n != 1 else ''})"
            for title, n in sorted(recent_courses.items(), key=lambda kv: -kv[1])[:3]
        )
        parts.append(f"CURRENT FOCUS (last 30 days): {studying}.")

    if technologies_seen:
        recent = [t for t in (recent_technologies or []) if t in technologies_seen]
        earlier = [t for t in technologies_seen if t not in recent]
        if recent and earlier:
            parts.append(
                f"Current technologies: {', '.join(recent)}. "
                f"Earlier (not recently practiced): {', '.join(earlier)}."
            )
        else:
            parts.append(f"Technologies: {', '.join(technologies_seen)}.")

    return " ".join(parts)
