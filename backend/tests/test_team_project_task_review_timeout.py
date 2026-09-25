"""Tests for review_task_submission's timeout guard
(app/services/team_project_task_review.py).

Regression test for the same incident class already fixed twice elsewhere
in this codebase (projects 4638/4926, see lesson_helpers.py's
_AUTO_REVIEW_TIMEOUT_S and projects.py's _run_ai_review_and_persist_failure)
but never applied to team-project task review: an unbounded AI call can be
cancelled by an edge/proxy timeout via asyncio.CancelledError, a
BaseException that skips straight past `except Exception`, leaving a task
silently stuck at status="submitted" forever. review_task_submission now
wraps its call_chain() call in asyncio.wait_for(), so a hang can only ever
surface as an ordinary asyncio.TimeoutError.
"""
import asyncio
import uuid

import pytest_asyncio
from unittest.mock import AsyncMock, patch

from app.models.group import Group
from app.models.team_project import TeamProject, TeamProjectTeam, TeamProjectTask, TaskStatus
from app.services.team_project_task_review import review_task_submission


@pytest_asyncio.fixture
async def submitted_task(async_client, db_session):
    """A TeamProjectTask sitting at status=submitted with a GitHub URL —
    the minimum review_task_submission needs (it operates on the ORM
    object directly via task_id, no HTTP layer involved)."""
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"taskreview_{uid}",
            "email": f"taskreview_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]

    group = Group(name=f"TR Group {uid}", teacher_id=student_id)
    db_session.add(group)
    await db_session.flush()

    team_project = TeamProject(group_id=group.id, team_size=2, deadline_days=14)
    db_session.add(team_project)
    await db_session.flush()

    team = TeamProjectTeam(team_project_id=team_project.id, name="Team 1")
    db_session.add(team)
    await db_session.flush()

    task = TeamProjectTask(
        team_id=team.id, assigned_student_id=student_id, order=0,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.submitted, submission_url="https://github.com/acme/repo",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


_FAKE_SNAPSHOT = {"exists": True, "content_text": "print('hello')"}


async def test_task_review_timeout_returns_failure_without_crashing(db_session, submitted_task):
    from app.services import team_project_task_review as module

    task = submitted_task

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)  # far longer than the patched timeout below
        return ("raw", {}, "mock", 1)  # pragma: no cover — never reached

    with patch.object(module, "_TASK_REVIEW_TIMEOUT_S", 0.05), \
         patch.object(module, "fetch_github_snapshot", new=AsyncMock(return_value=_FAKE_SNAPSHOT)), \
         patch.object(module, "call_chain", new=_hangs_forever):
        result = await review_task_submission(db_session, task.id)

    assert result["success"] is False
    assert "timed out" in result["reason"]

    await db_session.refresh(task)
    assert task.status == TaskStatus.submitted  # untouched, not silently rejected
    assert task.reviewed_at is None
    assert task.ai_score is None


async def test_task_review_timeout_leaves_session_usable_afterward(db_session, submitted_task):
    """The timeout path does no writes of its own — verify the session
    (and a plain read on the same task) still works fine afterward."""
    from app.services import team_project_task_review as module
    from sqlalchemy import select

    task = submitted_task

    async def _hangs_forever(*args, **kwargs):
        await asyncio.sleep(10)

    with patch.object(module, "_TASK_REVIEW_TIMEOUT_S", 0.05), \
         patch.object(module, "fetch_github_snapshot", new=AsyncMock(return_value=_FAKE_SNAPSHOT)), \
         patch.object(module, "call_chain", new=_hangs_forever):
        await review_task_submission(db_session, task.id)

    row = (
        await db_session.execute(select(TeamProjectTask).where(TeamProjectTask.id == task.id))
    ).scalar_one()
    assert row.status == TaskStatus.submitted


async def test_task_review_success_within_timeout_unaffected(db_session, submitted_task):
    """A fast, successful review still behaves exactly as before — the
    wait_for wrapper must not change anything on the happy path."""
    from app.services import team_project_task_review as module

    task = submitted_task
    parsed = {
        "score": 85, "approved": True,
        "criteria_results": [], "contract_violations": [],
        "feedback": "Yaxshi", "feedback_ru": "Хорошо",
    }
    mock = AsyncMock(return_value=("raw", parsed, "mock-provider", 1))

    with patch.object(module, "_TASK_REVIEW_TIMEOUT_S", 5), \
         patch.object(module, "fetch_github_snapshot", new=AsyncMock(return_value=_FAKE_SNAPSHOT)), \
         patch.object(module, "call_chain", new=mock):
        result = await review_task_submission(db_session, task.id)

    mock.assert_awaited_once()
    assert result["success"] is True
    assert result["score"] == 85
    await db_session.refresh(task)
    assert task.status == TaskStatus.approved
    assert task.reviewed_at is not None
