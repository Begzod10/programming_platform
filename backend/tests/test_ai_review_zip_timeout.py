"""Tests for _run_ai_review_and_persist_failure's timeout guard
(app/api/v1/endpoints/projects.py — the ZIP-upload AI review path).

Regression test for a real production incident (project 4926, 2026-09-11):
a ZIP upload's AI review had no wall-clock bound, so a hung/cancelled call
(asyncio.CancelledError, a BaseException — not an Exception) skipped
straight past the existing `except Exception` fallback-write and left the
project stuck at status="Submitted", reviewed_at=None, with literally zero
trace anywhere — no instructor_feedback, no error log, no completed
access-log line — for 6 days until a student reported it.

_try_auto_ai_review (lesson_helpers.py) already got this exact fix earlier
(project 4638's incident) — this endpoint never did. Mirrors that file's
test structure: patch _AUTO_REVIEW_TIMEOUT_S down to a few milliseconds so
the timeout path is actually exercised without a real multi-second wait.
"""

import asyncio
import uuid

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
async def zip_project(async_client, db_session):
    """A persisted Project row with project_files set (a ZIP upload), owned
    by a fresh student — the minimum _run_ai_review_and_persist_failure
    needs (it operates on the ORM object directly, no HTTP layer involved)."""
    from app.models.project import Project

    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"ziptimeout_{uid}",
            "email": f"ziptimeout_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]

    project = Project(
        student_id=student_id,
        title="Loyiha",
        description="",
        difficulty_level="Easy",
        status="Submitted",
        project_files="/uploads/projects/regression-test.zip",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


async def test_zip_review_timeout_writes_fallback_feedback(db_session, zip_project):
    from app.api.v1.endpoints import projects as projects_module
    from app.api.v1.endpoints import lesson_helpers

    project = zip_project

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)  # far longer than the patched timeout below
        return {"success": True}  # pragma: no cover — never reached

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 0.05), \
         patch.object(projects_module, "run_ai_review_for_project", new=_hangs_forever):
        result = await projects_module._run_ai_review_and_persist_failure(db_session, project)

    assert result["success"] is False

    # The defensive rollback inside the timeout branch expires every object
    # on the session — re-sync `project` before reading its attributes, or a
    # plain synchronous attribute access tries to lazy-load outside a
    # greenlet and raises MissingGreenlet.
    await db_session.refresh(project)

    assert project.instructor_feedback is not None
    assert "vaqtincha" in project.instructor_feedback
    # Status untouched — a timed-out review must still leave the project
    # sitting at "Submitted" for the teacher, not silently mark it done.
    assert project.status == "Submitted"
    assert project.reviewed_at is None


async def test_zip_review_timeout_leaves_session_usable_afterward(db_session, zip_project):
    """The timeout path rolls back before writing its fallback — verify that
    write (and the session generally) actually succeeds afterward."""
    from app.api.v1.endpoints import projects as projects_module
    from app.api.v1.endpoints import lesson_helpers
    from app.models.project import Project
    from sqlalchemy import select

    project = zip_project

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 0.05), \
         patch.object(projects_module, "run_ai_review_for_project", new=_hangs_forever):
        await projects_module._run_ai_review_and_persist_failure(db_session, project)

    row = (
        await db_session.execute(select(Project).where(Project.id == project.id))
    ).scalar_one()
    assert row.instructor_feedback is not None
    assert "vaqtincha" in row.instructor_feedback


async def test_zip_review_success_within_timeout_unaffected(db_session, zip_project):
    """A fast, successful review still behaves exactly as before — the
    wait_for wrapper must not change anything on the happy path."""
    from app.api.v1.endpoints import projects as projects_module
    from app.api.v1.endpoints import lesson_helpers

    project = zip_project
    mock = AsyncMock(return_value={"success": True})

    with patch.object(lesson_helpers, "_AUTO_REVIEW_TIMEOUT_S", 5), \
         patch.object(projects_module, "run_ai_review_for_project", new=mock):
        result = await projects_module._run_ai_review_and_persist_failure(db_session, project)

    mock.assert_awaited_once()
    assert result["success"] is True
    # success=True takes the early-return path — no fallback feedback written.
    assert project.instructor_feedback is None


async def test_zip_review_unhandled_exception_still_persists_feedback(db_session, zip_project):
    """A plain (non-timeout) exception must also leave the session usable
    afterward — the generic except branch now refreshes the object the same
    way the timeout branch does, closing a gap where the very next
    `project.reviewed_at is None` read could raise MissingGreenlet on an
    expired attribute post-rollback."""
    from app.api.v1.endpoints import projects as projects_module

    project = zip_project

    async def _blows_up(*args, **kwargs):
        raise RuntimeError("boom")

    with patch.object(projects_module, "run_ai_review_for_project", new=_blows_up):
        result = await projects_module._run_ai_review_and_persist_failure(db_session, project)

    assert result["success"] is False
    await db_session.refresh(project)
    assert project.instructor_feedback is not None
    assert "vaqtincha" in project.instructor_feedback
