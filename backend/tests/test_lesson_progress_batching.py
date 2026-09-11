"""
Regression tests for Task 2.3 — the N+1 query bug in `_calc_course_progress`
(backend/app/api/v1/endpoints/lesson_helpers.py).

Before the fix, `_calc_course_progress` called `_calc_lesson_progress` once
per lesson, and that function issued up to 3 of its own DB queries
(VideoWatch, ExerciseSubmission, Submission+Project) — ~60 round-trips for a
20-lesson course on every lesson list/detail/submit request.

These tests verify:
1. The batched implementation produces byte-for-byte identical progress
   values to the ORIGINAL per-lesson-loop implementation for a 5-lesson
   course mixing exercise-gated and project-gated lessons (some complete,
   some partial, some untouched). The expected numbers below were hand
   derived from `_calc_lesson_progress`'s pre-refactor logic and confirmed
   by running this exact test against the pre-refactor code (see the class
   docstring below) before the batching change was made.
2. The batched implementation issues a small, constant number of queries
   regardless of how many lessons the course has (O(1)), not one that grows
   with lesson count (O(N)) — the actual point of the fix.
"""
import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import event

from app.db.database import engine as _engine
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.project import Project
from app.models.submission import Submission
from app.models.video_watch import VideoWatch
from app.api.v1.endpoints.lesson_helpers import _calc_course_progress


@pytest_asyncio.fixture
async def student_id(async_client) -> int:
    """Register a fresh student and return their id."""
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"produser_{uid}",
            "email": f"produser_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    return reg.json()["user"]["id"]


async def _make_exercise(db_session, lesson_id: int, title: str) -> Exercise:
    ex = Exercise(
        lesson_id=lesson_id,
        title=title,
        description="desc",
        exercise_type="text_input",
    )
    db_session.add(ex)
    await db_session.flush()
    return ex


@pytest_asyncio.fixture
async def five_lesson_course(db_session, student_id) -> int:
    """A 5-lesson course mixing exercise-gated and project-gated lessons,
    some complete, some partial, some untouched.

    Hand-derivation (matching `_calc_lesson_progress`'s pre-refactor logic
    exactly, section by section):

      L1 — one exercise section, 2 exercises, BOTH submitted.
           total=1 (1 exercise section), done=1 (section fully submitted)
           -> 100%

      L2 — one watched video section + one exercise section where only 1
           of 2 exercises is submitted.
           total=2 (1 video + 1 exercise section), done=1 (video watched;
           exercise section NOT fully submitted so it contributes 0)
           -> int(1/2*100) = 50%

      L3 — one exercise section, 1 exercise, NOT submitted.
           total=1, done=0 -> 0%

      L4 — one project section; Submission -> Project with
           status="Approved", points_earned=80 (>= PROJECT_PASS_THRESHOLD=75).
           total=1 (1 project section), done=1 (has_passing=True)
           -> 100%

      L5 — one project section; Submission -> Project with
           status="Submitted" (pending review), points_earned=0.
           total=1, done=0 (not Approved) -> 0%

      course avg = (100 + 50 + 0 + 100 + 0) / 5 = 50
      completed_lessons (pct == 100) = 2 (L1, L4)
    """
    course = Course(
        title="Progress Batching Test Course",
        description="test",
        instructor_id=student_id,
        # Must be one of CourseBase.validate_difficulty's allowed values —
        # GET /api/v1/courses/ (hit by other test files sharing this
        # session-scoped SQLite DB) serializes every course row through
        # that validator, so an invalid value here would fail unrelated
        # tests elsewhere in the suite, not just this file's own tests.
        difficulty_level="Beginner",
        duration_weeks=1,
        max_points=100,
    )
    db_session.add(course)
    await db_session.flush()

    # ── L1: exercise-gated, fully complete ──────────────────────────────
    l1 = Lesson(course_id=course.id, title="L1", order=1, points_reward=10)
    db_session.add(l1)
    await db_session.flush()
    e1 = await _make_exercise(db_session, l1.id, "E1")
    e2 = await _make_exercise(db_session, l1.id, "E2")
    l1.sections_json = json.dumps([
        {"type": "exercise", "exercises": [{"id": e1.id}, {"id": e2.id}]},
    ])
    db_session.add_all([
        ExerciseSubmission(exercise_id=e1.id, student_id=student_id,
                            student_answer='"a"', is_correct=True),
        ExerciseSubmission(exercise_id=e2.id, student_id=student_id,
                            student_answer='"b"', is_correct=True),
    ])

    # ── L2: mixed, partial (video done, exercise section not done) ─────
    l2 = Lesson(course_id=course.id, title="L2", order=2, points_reward=10)
    db_session.add(l2)
    await db_session.flush()
    e3 = await _make_exercise(db_session, l2.id, "E3")
    e4 = await _make_exercise(db_session, l2.id, "E4")
    l2.sections_json = json.dumps([
        {"type": "video", "id": "vsec1", "videoUrl": "http://x/vid.mp4"},
        {"type": "exercise", "exercises": [{"id": e3.id}, {"id": e4.id}]},
    ])
    db_session.add(VideoWatch(student_id=student_id, lesson_id=l2.id, section_id="vsec1"))
    db_session.add(ExerciseSubmission(exercise_id=e3.id, student_id=student_id,
                                       student_answer='"a"', is_correct=True))
    # e4 intentionally left unsubmitted.

    # ── L3: exercise-gated, untouched ───────────────────────────────────
    l3 = Lesson(course_id=course.id, title="L3", order=3, points_reward=10)
    db_session.add(l3)
    await db_session.flush()
    e5 = await _make_exercise(db_session, l3.id, "E5")
    l3.sections_json = json.dumps([
        {"type": "exercise", "exercises": [{"id": e5.id}]},
    ])

    # ── L4: project-gated, complete (Approved, passing score) ──────────
    l4 = Lesson(
        course_id=course.id, title="L4", order=4, points_reward=10,
        task_title="Build something",
        sections_json=json.dumps([{"type": "project"}]),
    )
    db_session.add(l4)
    await db_session.flush()
    p4 = Project(student_id=student_id, title="P4", description="d",
                  difficulty_level="Easy", status="Approved", points_earned=80)
    db_session.add(p4)
    await db_session.flush()
    db_session.add(Submission(project_id=p4.id, student_id=student_id,
                               lesson_id=l4.id, status="Approved"))

    # ── L5: project-gated, submitted but not yet passing ────────────────
    l5 = Lesson(
        course_id=course.id, title="L5", order=5, points_reward=10,
        task_title="Build something else",
        sections_json=json.dumps([{"type": "project"}]),
    )
    db_session.add(l5)
    await db_session.flush()
    p5 = Project(student_id=student_id, title="P5", description="d",
                  difficulty_level="Easy", status="Submitted", points_earned=0)
    db_session.add(p5)
    await db_session.flush()
    db_session.add(Submission(project_id=p5.id, student_id=student_id,
                               lesson_id=l5.id, status="Submitted"))

    await db_session.commit()
    return course.id


async def test_batched_course_progress_matches_hand_derived_values(
    db_session, student_id, five_lesson_course
):
    """See `five_lesson_course`'s docstring for the full hand-derivation."""
    progress = await _calc_course_progress(db_session, five_lesson_course, student_id)

    assert progress["total_lessons"] == 5
    assert progress["completed_lessons"] == 2
    assert progress["progress_percentage"] == 50
    assert progress["progress"] == 50
    assert progress["percentage"] == 50


@pytest_asyncio.fixture
async def many_lesson_course(db_session, student_id) -> int:
    """A 20-lesson course (matching the exact scale cited in the bug
    report) where every lesson has one exercise section with one
    exercise, half submitted / half not. Used purely to demonstrate query
    count no longer scales with lesson count.
    """
    course = Course(
        title="Many Lessons Query Count Course",
        description="test",
        instructor_id=student_id,
        difficulty_level="Beginner",
        duration_weeks=1,
        max_points=100,
    )
    db_session.add(course)
    await db_session.flush()

    lesson_count = 20
    for i in range(lesson_count):
        lesson = Lesson(course_id=course.id, title=f"L{i}", order=i, points_reward=10)
        db_session.add(lesson)
        await db_session.flush()
        ex = await _make_exercise(db_session, lesson.id, f"E{i}")
        lesson.sections_json = json.dumps([
            {"type": "exercise", "exercises": [{"id": ex.id}]},
        ])
        if i % 2 == 0:
            db_session.add(ExerciseSubmission(
                exercise_id=ex.id, student_id=student_id,
                student_answer='"a"', is_correct=True,
            ))

    await db_session.commit()
    return course.id


async def test_batched_course_progress_query_count_is_constant_not_linear(
    db_session, student_id, many_lesson_course
):
    """The actual point of the fix: for a 20-lesson course, the total
    number of queries `_calc_course_progress` issues must be a small O(1)
    constant, not one that scales with the lesson count (O(N) — the old
    per-lesson-loop implementation issued at least 1 query per lesson here,
    i.e. >= 20, before even counting the video/project branches).
    """
    queries: list[str] = []

    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    event.listen(_engine.sync_engine, "before_cursor_execute", _before_cursor_execute)
    try:
        progress = await _calc_course_progress(db_session, many_lesson_course, student_id)
    finally:
        event.remove(_engine.sync_engine, "before_cursor_execute", _before_cursor_execute)

    assert progress["total_lessons"] == 20

    assert len(queries) <= 6, (
        f"_calc_course_progress issued {len(queries)} queries for a "
        f"20-lesson course — expected a small O(1) constant (<= 6), not "
        f"one that scales with lesson count:\n" + "\n".join(queries)
    )
