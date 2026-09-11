"""Tests for skill_profile_service.py — the team-project AI planner's input
signal, deliberately separate from Student.current_level (see the module
docstring in skill_profile_service.py for why).

Builds one group of 3 students at different levels/activity profiles and
asserts on the accuracy math, completed-course resolution (both via
CourseCertificate and via LessonCompletion coverage), past-project
selection/truncation, technologies_seen dedup, and the deterministic
summary text — plus a query-count guard against N+1, mirroring the existing
pattern in test_lesson_progress_batching.py.
"""
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import event

from app.db.database import engine as _engine
from app.models.category import Category
from app.models.course import Course
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.group import Group, student_groups
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.models.student_achievement import CourseCertificate
from app.models.user import Student, StudentLevel
from app.services.skill_profile_service import (
    build_skill_profile, build_group_skill_profiles, MIN_ATTEMPTS_FOR_ACCURACY,
)


async def _register_student(async_client, prefix: str) -> int:
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"{prefix}_{uid}",
            "email": f"{prefix}_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    return reg.json()["user"]["id"]


async def _make_course(db_session, category_id=None, **overrides) -> Course:
    course = Course(
        title=overrides.get("title", "Web Asoslari"),
        description="test course",
        instructor_id=overrides["instructor_id"],
        difficulty_level="Beginner",
        duration_weeks=4,
        max_points=100,
        category_id=category_id,
    )
    db_session.add(course)
    await db_session.flush()
    return course


async def _make_lesson(db_session, course_id: int, title: str, code_language=None) -> Lesson:
    lesson = Lesson(course_id=course_id, title=title, code_language=code_language)
    db_session.add(lesson)
    await db_session.flush()
    return lesson


async def _complete_lesson(db_session, student_id: int, lesson_id: int) -> None:
    db_session.add(LessonCompletion(student_id=student_id, lesson_id=lesson_id))
    await db_session.flush()


async def _make_exercise(db_session, lesson_id: int, exercise_type: str) -> Exercise:
    ex = Exercise(
        lesson_id=lesson_id, title="ex", description="desc", exercise_type=exercise_type,
    )
    db_session.add(ex)
    await db_session.flush()
    return ex


async def _submit(db_session, exercise_id: int, student_id: int, is_correct: bool) -> None:
    db_session.add(ExerciseSubmission(
        exercise_id=exercise_id, student_id=student_id,
        student_answer="x", is_correct=is_correct,
    ))
    await db_session.flush()


@pytest_asyncio.fixture
async def three_students(async_client, db_session):
    """Beginner (low activity), Intermediate (mixed accuracy + 1 completed
    course via coverage, no explicit certificate), Advanced (certified
    course + past projects + varied tech)."""
    from sqlalchemy import select

    beginner_id = await _register_student(async_client, "beginner")
    intermediate_id = await _register_student(async_client, "intermediate")
    advanced_id = await _register_student(async_client, "advanced")

    # ORM attribute assignment (not a bulk `update()` statement) — Student's
    # @validates('lifetime_points') hook, which keeps current_level in sync,
    # only fires on the former.
    for sid, points in ((beginner_id, 50), (intermediate_id, 1500), (advanced_id, 6000)):
        student = (await db_session.execute(
            select(Student).where(Student.id == sid)
        )).scalar_one()
        student.lifetime_points = points
    await db_session.commit()

    return {"beginner": beginner_id, "intermediate": intermediate_id, "advanced": advanced_id}


@pytest_asyncio.fixture
async def category(db_session) -> Category:
    cat = Category(name=f"Web Asoslari {uuid.uuid4().hex[:6]}", slug=f"web-{uuid.uuid4().hex[:6]}")
    db_session.add(cat)
    await db_session.flush()
    await db_session.commit()
    return cat


async def test_student_levels_reflect_lifetime_points(three_students, db_session):
    """Sanity check on the fixture itself — StudentLevel is derived from
    lifetime_points via Student's own validator, confirming the 3 students
    really do land at 3 different levels before testing the profile
    built from them."""
    from sqlalchemy import select
    rows = (await db_session.execute(
        select(Student.id, Student.current_level).where(
            Student.id.in_(three_students.values())
        )
    )).all()
    levels = {sid: lvl for sid, lvl in rows}
    assert levels[three_students["beginner"]] == StudentLevel.Beginner
    assert levels[three_students["intermediate"]] == StudentLevel.Intermediate
    assert levels[three_students["advanced"]] == StudentLevel.Advanced


async def test_exercise_accuracy_math_and_min_attempts_threshold(
    three_students, db_session, category,
):
    student_id = three_students["intermediate"]
    course = await _make_course(db_session, category_id=category.id, instructor_id=three_students["advanced"])
    lesson = await _make_lesson(db_session, course.id, "L1")

    # multiple_choice: 10 attempts, 9 correct -> 90% (>= min attempts)
    mc = await _make_exercise(db_session, lesson.id, "multiple_choice")
    for i in range(10):
        await _submit(db_session, mc.id, student_id, is_correct=(i != 9))

    # drag_and_drop: only 3 attempts -> excluded, below MIN_ATTEMPTS_FOR_ACCURACY
    dd = await _make_exercise(db_session, lesson.id, "drag_and_drop")
    for i in range(3):
        await _submit(db_session, dd.id, student_id, is_correct=True)
    await db_session.commit()

    assert MIN_ATTEMPTS_FOR_ACCURACY == 5  # guards the fixture's own assumption above

    profile = await build_skill_profile(db_session, student_id)
    assert profile.exercise_accuracy_by_topic.get("multiple_choice") == pytest.approx(0.9)
    assert "drag_and_drop" not in profile.exercise_accuracy_by_topic


async def test_completed_courses_via_certificate_and_via_coverage(
    three_students, db_session, category,
):
    teacher_id = three_students["advanced"]

    # Course A: explicit CourseCertificate, no lesson completions recorded
    # (simulates a legacy/edge-case row — coverage alone wouldn't catch it).
    course_a = await _make_course(db_session, category_id=category.id, instructor_id=teacher_id, title="Course A")
    db_session.add(CourseCertificate(student_id=three_students["advanced"], course_id=course_a.id))

    # Course B: no certificate, but 100% LessonCompletion coverage.
    course_b = await _make_course(db_session, category_id=category.id, instructor_id=teacher_id, title="Course B")
    l1 = await _make_lesson(db_session, course_b.id, "B-L1", code_language="python")
    l2 = await _make_lesson(db_session, course_b.id, "B-L2", code_language="python")
    await db_session.flush()
    await _complete_lesson(db_session, three_students["intermediate"], l1.id)
    await _complete_lesson(db_session, three_students["intermediate"], l2.id)

    # Course C: partial coverage (1 of 2 lessons) — must NOT count as completed.
    course_c = await _make_course(db_session, category_id=category.id, instructor_id=teacher_id, title="Course C")
    c1 = await _make_lesson(db_session, course_c.id, "C-L1")
    c2 = await _make_lesson(db_session, course_c.id, "C-L2")
    await db_session.flush()
    await _complete_lesson(db_session, three_students["intermediate"], c1.id)
    await db_session.commit()

    advanced_profile = await build_skill_profile(db_session, three_students["advanced"])
    assert {c.course_id for c in advanced_profile.completed_courses} == {course_a.id}
    assert advanced_profile.completed_courses[0].category is not None

    intermediate_profile = await build_skill_profile(db_session, three_students["intermediate"])
    completed_ids = {c.course_id for c in intermediate_profile.completed_courses}
    assert course_b.id in completed_ids
    assert course_c.id not in completed_ids
    assert intermediate_profile.completed_lessons_by_course[course_b.id] == 2


async def test_past_projects_limited_sorted_and_truncated(three_students, db_session):
    from app.utils.datetime_utils import utcnow
    student_id = three_students["advanced"]
    long_text = "x" * 400

    for i in range(7):
        db_session.add(Project(
            student_id=student_id,
            title=f"Project {i}",
            description="d",
            difficulty_level="Medium",
            technologies_used="React,Node",
            grade="B",
            ai_strengths=long_text,
            ai_improvements=long_text,
            reviewed_at=utcnow(),
        ))
    # An unreviewed project must be excluded from past_projects entirely.
    db_session.add(Project(
        student_id=student_id, title="Unreviewed", description="d",
        difficulty_level="Medium", technologies_used="Vue",
    ))
    await db_session.commit()

    profile = await build_skill_profile(db_session, student_id)
    assert len(profile.past_projects) == 5
    assert all(p.title != "Unreviewed" for p in profile.past_projects)
    assert all(len(p.ai_strengths) <= 300 for p in profile.past_projects)
    # technologies_seen counts every project regardless of review status —
    # covered explicitly in test_technologies_seen_includes_unreviewed_projects_*.
    assert "vue" in profile.technologies_seen


async def test_technologies_seen_includes_unreviewed_projects_and_lesson_code_language(
    three_students, db_session, category,
):
    student_id = three_students["advanced"]
    db_session.add(Project(
        student_id=student_id, title="Unreviewed", description="d",
        difficulty_level="Medium", technologies_used="Vue,TypeScript",
    ))
    course = await _make_course(db_session, category_id=category.id, instructor_id=student_id)
    lesson = await _make_lesson(db_session, course.id, "L1", code_language="Python")
    await db_session.flush()
    await _complete_lesson(db_session, student_id, lesson.id)
    await db_session.commit()

    profile = await build_skill_profile(db_session, student_id)
    # technologies_seen is Project.technologies_used (ALL projects, reviewed
    # or not) union Lesson.code_language across completed lessons — deduped
    # lowercase.
    assert {"vue", "typescript", "python"} <= set(profile.technologies_seen)
    assert profile.technologies_seen == sorted(profile.technologies_seen)


async def test_summary_mentions_level_courses_accuracy_projects_and_tech(
    three_students, db_session, category,
):
    student_id = three_students["advanced"]
    teacher_id = student_id
    course = await _make_course(db_session, category_id=category.id, instructor_id=teacher_id, title="JS Fundamentals")
    lesson = await _make_lesson(db_session, course.id, "L1")
    await db_session.flush()
    await _complete_lesson(db_session, student_id, lesson.id)
    db_session.add(CourseCertificate(student_id=student_id, course_id=course.id))

    mc = await _make_exercise(db_session, lesson.id, "multiple_choice")
    for i in range(10):
        await _submit(db_session, mc.id, student_id, is_correct=(i < 9))  # 90%
    dd = await _make_exercise(db_session, lesson.id, "drag_and_drop")
    for i in range(10):
        await _submit(db_session, dd.id, student_id, is_correct=(i < 6))  # 60%

    from app.utils.datetime_utils import utcnow
    db_session.add(Project(
        student_id=student_id, title="P1", description="d",
        difficulty_level="Medium", technologies_used="html,css",
        grade="B", reviewed_at=utcnow(),
    ))
    await db_session.commit()

    profile = await build_skill_profile(db_session, student_id)
    assert profile.summary.startswith("Advanced.")
    assert "JS Fundamentals" in profile.summary
    assert "multiple_choice (90%)" in profile.summary
    assert "drag_and_drop (60%)" in profile.summary
    assert "1 past project" in profile.summary
    assert "avg grade B" in profile.summary
    assert "css, html" in profile.summary  # technologies_seen is sorted


async def test_build_group_skill_profiles_returns_one_profile_per_member(
    three_students, db_session,
):
    teacher_id = three_students["advanced"]
    group = Group(name="Test Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in three_students.values():
        await db_session.execute(
            student_groups.insert().values(student_id=sid, group_id=group.id)
        )
    await db_session.commit()

    profiles = await build_group_skill_profiles(db_session, group.id)
    assert {p.student_id for p in profiles} == set(three_students.values())
    by_id = {p.student_id: p for p in profiles}
    assert by_id[three_students["beginner"]].current_level == StudentLevel.Beginner
    assert by_id[three_students["advanced"]].current_level == StudentLevel.Advanced


async def test_group_profiles_batched_not_per_student(three_students, db_session):
    """Query-count guard: building profiles for a 3-student group must not
    scale linearly with group size — mirrors
    test_lesson_progress_batching.py's approach for the same class of bug.
    """
    teacher_id = three_students["advanced"]
    group = Group(name="Batch Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in three_students.values():
        await db_session.execute(
            student_groups.insert().values(student_id=sid, group_id=group.id)
        )
    await db_session.commit()

    queries = []

    def _count(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(_engine.sync_engine, "before_cursor_execute", _count)
    try:
        await build_group_skill_profiles(db_session, group.id)
    finally:
        event.remove(_engine.sync_engine, "before_cursor_execute", _count)

    # Fixed handful of batched queries (students, certs, completions,
    # accuracy x2, projects, completed-course resolution x2) — nowhere near
    # "one round-trip per student per signal", which is the actual bug this
    # guards against. 20 is a generous ceiling, not a tight budget.
    assert len(queries) < 20, f"expected O(1) batched queries, got {len(queries)}"


# ── HTTP endpoint ────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def teacher_headers(async_client) -> dict:
    from sqlalchemy import update
    uid = uuid.uuid4().hex[:8]
    username, password = f"skillteacher_{uid}", "teacherpass123"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert reg.status_code == 201
    user_id = reg.json()["user"]["id"]
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as s:
        await s.execute(update(Student).where(Student.id == user_id).values(role="teacher"))
        await s.commit()
    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": password},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}, user_id


async def test_skill_profile_endpoint_requires_teacher_ownership(
    async_client, teacher_headers, three_students, db_session,
):
    headers, teacher_id = teacher_headers
    student_id = three_students["advanced"]

    # Not yet reachable by this teacher (no group/flow link) -> 404, not 403
    # (avoids leaking whether the student id exists at all).
    resp = await async_client.get(
        f"/api/v1/teacher/students/{student_id}/skill-profile", headers=headers,
    )
    assert resp.status_code == 404

    group = Group(name="Owned Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(
        student_groups.insert().values(student_id=student_id, group_id=group.id)
    )
    await db_session.commit()

    resp = await async_client.get(
        f"/api/v1/teacher/students/{student_id}/skill-profile", headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == student_id
    assert data["current_level"] == "Advanced"
    assert "summary" in data and isinstance(data["summary"], str)


async def test_skill_profile_endpoint_requires_auth(async_client, three_students):
    resp = await async_client.get(
        f"/api/v1/teacher/students/{three_students['advanced']}/skill-profile",
    )
    assert resp.status_code == 401
