"""
Integration tests for the /api/v1/courses/{course_id}/lessons/{lesson_id}/exercises endpoints.

Full path pattern: /api/v1/courses/{course_id}/lessons/{lesson_id}/exercises/...

Covers:
- GET exercises is public (no auth required)
- Unknown lesson_id returns an empty list (not 404)
- Single-exercise lookup returns 404 for unknown IDs
- submit and my-submissions require authentication
- Course progress requires authentication
"""

import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select

# Placeholder IDs that don't exist in the test DB
COURSE_ID = 99999
LESSON_ID = 99999
EXERCISE_ID = 99999

BASE = f"/api/v1/courses/{COURSE_ID}/lessons"


# ── GET exercises list ────────────────────────────────────────────────────────

async def test_get_exercises_no_auth_returns_200(async_client: AsyncClient):
    """GET exercises is publicly accessible — no auth header needed."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200


async def test_get_exercises_unknown_lesson_returns_empty_list(async_client: AsyncClient):
    """GET exercises for a non-existent lesson returns 200 with an empty list."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_exercises_response_is_list(async_client: AsyncClient):
    """GET exercises always returns a JSON array."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── GET single exercise ───────────────────────────────────────────────────────

async def test_get_single_exercise_not_found_returns_404(async_client: AsyncClient):
    """GET a specific exercise that doesn't exist returns 404."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}")
    assert resp.status_code == 404


# ── POST submit exercise ──────────────────────────────────────────────────────

async def test_submit_exercise_requires_auth_returns_401(async_client: AsyncClient):
    """POST to /submit without a token returns 401."""
    resp = await async_client.post(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/submit",
        json={"student_answer": "my answer"},
    )
    assert resp.status_code == 401


async def test_submit_exercise_unknown_exercise_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """POST to /submit for a non-existent exercise returns 404."""
    resp = await async_client.post(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/submit",
        json={"student_answer": "my answer"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── GET my-submissions ────────────────────────────────────────────────────────

async def test_get_my_submissions_requires_auth_returns_401(async_client: AsyncClient):
    """GET my-submissions without a token returns 401."""
    resp = await async_client.get(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/my-submissions"
    )
    assert resp.status_code == 401


# ── GET course progress ───────────────────────────────────────────────────────

async def test_get_course_progress_requires_auth_returns_401(async_client: AsyncClient):
    """GET exercises/progress without a token returns 401."""
    resp = await async_client.get(
        f"{BASE}/{LESSON_ID}/exercises/progress"
    )
    assert resp.status_code == 401


# ── Idempotency: concurrent scoring inserts must award points exactly once ────


@pytest_asyncio.fixture
async def scoring_exercise_setup(db_session):
    """Insert a Student + Course + Lesson + fill-in-blank Exercise.

    Returns (student_id, exercise_id, exercise_points).
    """
    from app.models.course import Course
    from app.models.exercise import Exercise
    from app.models.lesson import Lesson
    from app.models.user import Student, UserRole

    uid = uuid.uuid4().hex[:8]

    teacher = Student(
        username=f"teach_{uid}",
        email=f"teach_{uid}@example.com",
        hashed_password="x",
        role=UserRole.teacher,
    )
    student = Student(
        username=f"stud_{uid}",
        email=f"stud_{uid}@example.com",
        hashed_password="x",
        role=UserRole.student,
        total_points=0,
    )
    db_session.add_all([teacher, student])
    await db_session.commit()
    await db_session.refresh(teacher)
    await db_session.refresh(student)

    course = Course(
        title=f"Course {uid}",
        description="test",
        instructor_id=teacher.id,
        difficulty_level="Beginner",
        duration_weeks=1,
        max_points=100,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    lesson = Lesson(course_id=course.id, title="L1", points_reward=0)
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    exercise = Exercise(
        lesson_id=lesson.id,
        title="Fill it",
        description="1+1 = ___",
        exercise_type="fill_in_blank",
        correct_answers="2",
        points=17,
    )
    db_session.add(exercise)
    await db_session.commit()
    await db_session.refresh(exercise)

    return student.id, exercise.id, exercise.points


async def test_concurrent_correct_submissions_award_points_once(scoring_exercise_setup):
    """Two racing correct submissions must yield exactly one scoring row.

    The partial unique index on exercise_submissions (student_id, exercise_id)
    WHERE score > 0 is the invariant. Regardless of which submission wins the
    race, student.total_points must move by exactly exercise.points, not 2x.
    """
    from app.db.database import AsyncSessionLocal
    from app.models.exercise import ExerciseSubmission
    from app.models.user import Student
    from app.schemas.exercise import ExerciseSubmitRequest
    from app.services.exercise_service import submit_exercise

    student_id, exercise_id, points = scoring_exercise_setup

    async def _one_submit():
        # Each concurrent task uses its own session, matching real request flow.
        async with AsyncSessionLocal() as db:
            return await submit_exercise(
                db, exercise_id, student_id,
                ExerciseSubmitRequest(student_answer="2", time_spent_ms=100),
            )

    results = await asyncio.gather(
        _one_submit(), _one_submit(), return_exceptions=True,
    )
    # Neither call is allowed to 500 out — the IntegrityError must be caught.
    for r in results:
        assert not isinstance(r, Exception), f"submit raised: {r!r}"

    async with AsyncSessionLocal() as db:
        # Exactly one scoring row.
        scoring_rows = (await db.execute(
            select(ExerciseSubmission).where(
                ExerciseSubmission.student_id == student_id,
                ExerciseSubmission.exercise_id == exercise_id,
                ExerciseSubmission.score > 0,
            )
        )).scalars().all()
        assert len(scoring_rows) == 1, (
            f"expected exactly 1 scoring row, got {len(scoring_rows)}"
        )
        assert scoring_rows[0].score == points

        # Total points bumped by exactly `points`, never doubled.
        st = (await db.execute(
            select(Student).where(Student.id == student_id)
        )).scalar_one()
        assert st.total_points == points, (
            f"total_points={st.total_points}, expected {points}"
        )


async def test_repeat_correct_submission_after_scoring_stays_at_one_award(
    scoring_exercise_setup,
):
    """A second correct submission (sequential) must not add points a second time."""
    from app.db.database import AsyncSessionLocal
    from app.models.exercise import ExerciseSubmission
    from app.models.user import Student
    from app.schemas.exercise import ExerciseSubmitRequest
    from app.services.exercise_service import submit_exercise

    student_id, exercise_id, points = scoring_exercise_setup

    async with AsyncSessionLocal() as db:
        await submit_exercise(
            db, exercise_id, student_id,
            ExerciseSubmitRequest(student_answer="2", time_spent_ms=100),
        )
    async with AsyncSessionLocal() as db:
        await submit_exercise(
            db, exercise_id, student_id,
            ExerciseSubmitRequest(student_answer="2", time_spent_ms=100),
        )

    async with AsyncSessionLocal() as db:
        scoring_rows = (await db.execute(
            select(ExerciseSubmission).where(
                ExerciseSubmission.student_id == student_id,
                ExerciseSubmission.exercise_id == exercise_id,
                ExerciseSubmission.score > 0,
            )
        )).scalars().all()
        assert len(scoring_rows) == 1
        st = (await db.execute(
            select(Student).where(Student.id == student_id)
        )).scalar_one()
        assert st.total_points == points
