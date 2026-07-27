"""
Regression tests for the points/balls reversal bugs found in this audit:

1. `RankingService.revoke_earned_points` must reverse BOTH `total_points`
   (spendable) and `lifetime_points` (career total / leaderboard), unlike
   `subtract_points_from_student` which is intentionally spend-only (store
   purchases). Before this fix, `ai_review_service.py` used the spend-only
   method to reverse a previously-Approved project's score on re-review,
   which permanently inflated `lifetime_points`/the leaderboard on every
   re-review cycle.

2. `ProjectService.create_project`'s lesson-scoped resubmit path must only
   reverse points if the replaced project was actually Approved (i.e. its
   points were actually credited to the wallet). Before this fix, it
   unconditionally subtracted `points_earned` from `total_points` even for
   Rejected projects, wrongly draining the student's spendable balance for
   points they never received.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.ranking import Ranking
from app.services.ranking_service import RankingService
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate


@pytest_asyncio.fixture
async def student_id(async_client: AsyncClient) -> int:
    """Register a fresh student and return their id."""
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"ptsuser_{uid}",
            "email": f"ptsuser_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    return reg.json()["user"]["id"]


# ── Bug 1: revoke_earned_points must reverse both wallets ────────────────────


async def test_revoke_earned_points_reverses_both_wallets(db_session, student_id):
    """add_points_to_student(+90) then revoke_earned_points(90) must leave
    total_points AND lifetime_points back at their starting values, with
    Ranking.total_points mirroring lifetime_points."""
    service = RankingService(db_session)

    student = await service.add_points_to_student(student_id, 90)
    assert student.total_points == 90
    assert student.lifetime_points == 90

    student = await service.revoke_earned_points(student_id, 90)
    assert student.total_points == 0
    assert student.lifetime_points == 0

    result = await db_session.execute(
        Ranking.__table__.select().where(Ranking.student_id == student_id)
    )
    ranking = result.mappings().one()
    assert ranking["total_points"] == 0


async def test_revoke_earned_points_matches_re_review_scenario(db_session, student_id):
    """Simulates ai_review_service's re-review branch: old score (80) is
    revoked, then a new score (60, below the 75 pass threshold so it is
    NOT re-added) is recorded. lifetime_points must drop back to 0, not
    stay inflated at 80."""
    service = RankingService(db_session)

    # First review: Approved with 80 points.
    await service.add_points_to_student(student_id, 80)

    # Re-review: old 80 must be fully reversed (both wallets). New score is
    # 60, which is below the pass threshold, so nothing is re-added — this
    # mirrors ai_review_service.py's `if new_points > 0 and new_points >= 75`
    # gate not firing.
    student = await service.revoke_earned_points(student_id, 80)

    assert student.total_points == 0
    assert student.lifetime_points == 0, (
        "lifetime_points leaked stale points from the reversed review — "
        "this is exactly the bug this fix addresses"
    )


async def test_subtract_points_from_student_is_still_spend_only(db_session, student_id):
    """Guard rail: subtract_points_from_student must remain spend-only
    (only total_points moves) so store purchases never touch the
    leaderboard. This is intentionally different from revoke_earned_points."""
    service = RankingService(db_session)

    await service.add_points_to_student(student_id, 50)
    student = await service.subtract_points_from_student(student_id, 20)

    assert student.total_points == 30
    assert student.lifetime_points == 50, (
        "subtract_points_from_student must never touch lifetime_points"
    )


# ── Bug 2: resubmitting a Rejected project must not drain total_points ──────


@pytest_asyncio.fixture
async def lesson_id(db_session, student_id) -> int:
    course = Course(
        title="Test Course",
        description="Test",
        instructor_id=student_id,
        difficulty_level="Easy",
        duration_weeks=1,
        max_points=100,
    )
    db_session.add(course)
    await db_session.flush()

    lesson = Lesson(course_id=course.id, title="Test Lesson", points_reward=50)
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)
    return lesson.id


async def test_resubmit_after_rejection_does_not_drain_wallet(
    db_session, student_id, lesson_id
):
    """A project that was AI-scored 40 (Rejected, points never credited to
    the wallet) is then resubmitted for the same lesson. The resubmit path
    must NOT subtract the 40 points from total_points, because they were
    never added in the first place."""
    service = ProjectService(db_session)

    # First submission, ends up Rejected with a nonzero AI score (points
    # stored on the project row for display, but never credited — mirrors
    # ai_review_service.py only calling add_points_to_student when
    # new_points >= 75).
    first = await service.create_project(
        student_id=student_id,
        data=ProjectCreate(
            title="Attempt 1",
            description="First attempt at the project",
            github_url="https://github.com/example/repo1",
            lesson_id=lesson_id,
        ),
    )
    first.status = "Rejected"
    first.points_earned = 40
    await db_session.commit()

    # Give the student some unrelated spendable balance so we can prove it
    # survives the resubmit untouched.
    ranking_service = RankingService(db_session)
    student = await ranking_service.add_points_to_student(student_id, 100)
    assert student.total_points == 100

    # Resubmit for the same lesson — this deletes+replaces the Rejected
    # project and, before the fix, unconditionally subtracted old_points
    # (40) from total_points even though it was never credited.
    await service.create_project(
        student_id=student_id,
        data=ProjectCreate(
            title="Attempt 2",
            description="Second attempt at the project",
            github_url="https://github.com/example/repo2",
            lesson_id=lesson_id,
        ),
    )

    await db_session.refresh(student)
    assert student.total_points == 100, (
        "resubmitting a Rejected project wrongly drained points that were "
        "never credited to the wallet — this is exactly the bug this fix "
        "addresses"
    )
