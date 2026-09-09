"""Tests for _try_auto_ai_review's timeout guard (lesson_helpers.py).

Regression test for a real production incident (project 4638, 2026-09-09):
a submission's auto-triggered AI review had no wall-clock bound, so a slow
provider chain could run past both Cloudflare's and nginx's own proxy
timeouts. The edge proxy dropping the connection either orphaned the
coroutine or got it cancelled via asyncio.CancelledError — a BaseException,
not an Exception, so it skipped straight past the existing `except
Exception` fallback-write and left the project silently stuck at
status="Submitted" forever with zero trace anywhere (no instructor_feedback,
no error-log entry, no completed access-log line).

_try_auto_ai_review now wraps the whole call in asyncio.wait_for(), so a
slow AI call can only ever surface as an ordinary asyncio.TimeoutError.
These tests monkeypatch _AUTO_REVIEW_TIMEOUT_S down to a few milliseconds
so the timeout path is actually exercised without a real multi-second wait.
"""

import asyncio
import uuid

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
async def project_with_github_url(async_client, db_session):
    """A persisted Project row with a github_url, owned by a fresh student —
    the minimum _try_auto_ai_review needs (it operates on the ORM object
    directly, no HTTP layer involved)."""
    from app.models.project import Project

    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"aitimeout_{uid}",
            "email": f"aitimeout_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]

    project = Project(
        student_id=student_id,
        title="Timeout Test Project",
        description="Regression test for the stuck-forever auto-review bug",
        difficulty_level="Easy",
        status="Submitted",
        github_url="https://github.com/example/repo",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.mark.asyncio
async def test_auto_review_timeout_writes_fallback_feedback(
    db_session, project_with_github_url
):
    from app.api.v1.endpoints import lesson_helpers

    project = project_with_github_url

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)  # far longer than the patched timeout below
        return {"success": True}  # pragma: no cover — never reached

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 0.05), \
         patch("app.services.ai_review_service.run_ai_review_for_project", new=_hangs_forever):
        await lesson_helpers._try_auto_ai_review(db_session, project)

    # The defensive rollback inside the timeout branch expires every object
    # on the session (standard SQLAlchemy behavior) — re-sync `project`
    # inside an async context before reading its attributes, or a plain
    # synchronous attribute access tries to lazy-load outside a greenlet
    # and raises MissingGreenlet.
    await db_session.refresh(project)

    assert project.instructor_feedback is not None
    assert "vaqtincha" in project.instructor_feedback
    # Status untouched — a timed-out review must still leave the project
    # sitting at "Submitted" for the teacher, not silently mark it done.
    assert project.status == "Submitted"
    assert project.reviewed_at is None


@pytest.mark.asyncio
async def test_auto_review_timeout_leaves_session_usable_afterward(
    db_session, project_with_github_url
):
    """The timeout path rolls back before writing its fallback — verify that
    write (and the session generally) actually succeeds afterward, i.e. the
    rollback didn't leave the session broken for the request's remaining
    work (award_certificate, the response-building queries, ...)."""
    from app.api.v1.endpoints import lesson_helpers
    from app.models.project import Project
    from sqlalchemy import select

    project = project_with_github_url

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 0.05), \
         patch("app.services.ai_review_service.run_ai_review_for_project", new=_hangs_forever):
        await lesson_helpers._try_auto_ai_review(db_session, project)

    # A completely ordinary read on the same session, post-rollback — would
    # raise if the session were left in a broken/pending-rollback state.
    row = (
        await db_session.execute(select(Project).where(Project.id == project.id))
    ).scalar_one()
    assert row.instructor_feedback is not None
    assert "vaqtincha" in row.instructor_feedback


@pytest.mark.asyncio
async def test_auto_review_success_within_timeout_unaffected(
    db_session, project_with_github_url
):
    """A fast, successful review still behaves exactly as before — the
    wait_for wrapper must not change anything on the happy path."""
    from app.api.v1.endpoints import lesson_helpers

    project = project_with_github_url
    mock = AsyncMock(return_value={"success": True})

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 5), \
         patch("app.services.ai_review_service.run_ai_review_for_project", new=mock):
        await lesson_helpers._try_auto_ai_review(db_session, project)

    mock.assert_awaited_once()
    # success=True takes the early-return path — no fallback feedback written.
    assert project.instructor_feedback is None
