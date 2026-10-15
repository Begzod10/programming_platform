"""Regression tests for the team-project audit fixes: AI review output is
validated/enforced (not trusted), and submit_task can't re-open approved work
or touch a finalized team."""
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.models.group import Group
from app.models.team_project import (
    TaskStatus, TeamProject, TeamProjectTask, TeamProjectTeam, TeamStatus,
)
from app.services import team_project_task_review as module
from app.services.team_project_task_review import (
    _as_bool, _coerce_score, review_task_submission,
)
from app.utils.datetime_utils import utcnow


@pytest_asyncio.fixture
async def submitted(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"audit_{uid}", "email": f"audit_{uid}@example.com",
              "password": "securepass123"},
    )
    assert reg.status_code == 201, reg.text
    body = reg.json()
    student_id = body["user"]["id"]
    headers = {"Authorization": f"Bearer {body['access_token']}"}

    group = Group(name=f"Audit {uid}", teacher_id=student_id)
    db_session.add(group)
    await db_session.flush()
    tp = TeamProject(group_id=group.id, team_size=2, deadline_days=14)
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=tp.id, name="Team 1", status=TeamStatus.working)
    db_session.add(team)
    await db_session.flush()
    task = TeamProjectTask(
        team_id=team.id, assigned_student_id=student_id, order=0,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json='["a", "b"]', depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.submitted, submission_url="https://github.com/acme/repo",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    await db_session.refresh(team)
    return task, team, headers


# ── review output is validated, not trusted ──────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    (85, 85), ("85/100", 85), ("85.5", 85), (85.9, 85), (150, 100), (-5, 0),
    (None, None), ("abc", None), (True, None), ([], None),
])
def test_coerce_score(raw, expected):
    assert _coerce_score(raw) == expected


def test_string_false_is_not_true():
    assert _as_bool("false") is False
    assert _as_bool("true") is True
    assert _as_bool(True) is True
    assert _as_bool(None) is False


async def _run_review(db_session, task, parsed, snapshot):
    with patch.object(module, "fetch_github_snapshot", new=AsyncMock(return_value=snapshot)), \
         patch.object(module, "call_chain", new=AsyncMock(return_value=("raw", parsed, "mock", 1))):
        result = await review_task_submission(db_session, task.id)
    await db_session.refresh(task)
    return result


_READABLE = {"exists": True, "content_text": "print('hi')"}


async def test_non_numeric_score_fails_cleanly_instead_of_raising(db_session, submitted):
    task, _, _ = submitted
    result = await _run_review(db_session, task, {"score": "n/a", "approved": True}, _READABLE)
    assert result["success"] is False
    assert task.status == TaskStatus.submitted


async def test_unreadable_code_cannot_be_approved_or_score_high(db_session, submitted):
    task, _, _ = submitted
    parsed = {"score": 95, "approved": True, "criteria_results": [], "contract_violations": []}
    result = await _run_review(db_session, task, parsed, {"exists": False, "content_text": ""})
    assert result["success"] is True
    assert result["score"] == 30
    assert result["approved"] is False
    assert task.status == TaskStatus.changes_requested


async def test_unmet_criterion_blocks_approval_despite_high_score(db_session, submitted):
    task, _, _ = submitted
    parsed = {
        "score": 90, "approved": True,
        "criteria_results": [{"criterion": "a", "met": True}, {"criterion": "b", "met": False}],
        "contract_violations": [],
    }
    result = await _run_review(db_session, task, parsed, _READABLE)
    assert result["approved"] is False
    assert task.status == TaskStatus.changes_requested


async def test_contract_violation_blocks_approval(db_session, submitted):
    task, _, _ = submitted
    parsed = {"score": 90, "approved": True, "criteria_results": [],
              "contract_violations": ["missing POST /api/login"]}
    result = await _run_review(db_session, task, parsed, _READABLE)
    assert result["approved"] is False


async def test_clean_high_score_still_approves(db_session, submitted):
    task, _, _ = submitted
    parsed = {"score": 90, "approved": True,
              "criteria_results": [{"criterion": "a", "met": True}], "contract_violations": []}
    result = await _run_review(db_session, task, parsed, _READABLE)
    assert result["approved"] is True
    assert task.status == TaskStatus.approved


async def test_malformed_feedback_fields_are_normalized(db_session, submitted):
    import json
    task, _, _ = submitted
    parsed = {"score": 70, "approved": False, "criteria_results": "oops",
              "contract_violations": {"x": 1}, "feedback": ["list"], "feedback_ru": None}
    await _run_review(db_session, task, parsed, _READABLE)
    stored = json.loads(task.ai_feedback_json)
    assert stored["criteria_results"] == []
    assert stored["contract_violations"] == []
    assert stored["feedback"] == "" and stored["feedback_ru"] == ""


async def test_student_code_is_wrapped_in_student_input_tag(db_session, submitted):
    task, _, _ = submitted
    mock = AsyncMock(return_value=("raw", {"score": 50, "approved": False}, "mock", 1))
    with patch.object(module, "fetch_github_snapshot", new=AsyncMock(return_value=_READABLE)), \
         patch.object(module, "call_chain", new=mock):
        await review_task_submission(db_session, task.id)
    prompt = mock.await_args.args[0]
    assert "<student_input>" in prompt and "</student_input>" in prompt


# ── submit_task guards ───────────────────────────────────────────────────────

async def _submit(async_client, headers, team, task, url="https://github.com/acme/repo"):
    with patch("app.api.v1.endpoints.team_project.review_task_submission",
               new=AsyncMock(return_value={"success": False, "reason": "mock"})):
        return await async_client.post(
            f"/api/v1/team-projects/teams/{team.id}/tasks/{task.id}/submit",
            headers=headers, json={"submission_url": url},
        )


async def test_cannot_resubmit_an_approved_task(async_client, db_session, submitted):
    task, team, headers = submitted
    task.status = TaskStatus.approved
    await db_session.commit()
    resp = await _submit(async_client, headers, team, task)
    assert resp.status_code == 400, resp.text


async def test_cannot_submit_on_a_finalized_team(async_client, db_session, submitted):
    task, team, headers = submitted
    team.status = TeamStatus.reviewed
    await db_session.commit()
    resp = await _submit(async_client, headers, team, task)
    assert resp.status_code == 400, resp.text


async def test_non_github_url_is_rejected_at_submit(async_client, submitted):
    task, team, headers = submitted
    resp = await _submit(async_client, headers, team, task, url="https://example.com/x")
    assert resp.status_code == 400, resp.text


async def test_resubmission_clears_previous_review_state(async_client, db_session, submitted):
    task, team, headers = submitted
    task.status = TaskStatus.changes_requested
    task.reviewed_at = utcnow() - timedelta(hours=1)
    task.ai_score = 40
    task.ai_feedback_json = '{"feedback": "old"}'
    await db_session.commit()

    resp = await _submit(async_client, headers, team, task)
    assert resp.status_code == 200, resp.text

    await db_session.refresh(task)
    assert task.status == TaskStatus.submitted
    assert task.reviewed_at is None and task.ai_score is None and task.ai_feedback_json is None
