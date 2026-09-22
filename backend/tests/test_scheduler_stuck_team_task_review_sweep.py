"""Tests for job_retry_stuck_team_task_reviews (app/scheduler.py) — the
same defense-in-depth sweep pattern as job_retry_stuck_project_reviews
(see that function's docstring in scheduler.py for the full incident
writeup), applied to team-project task submissions instead of regular
projects. Catches a task stuck at status="submitted", reviewed_at=None
regardless of *why* it never got a review attempt persisted, and retries
it every 15 minutes.

Deliberately narrow — must NOT touch:
  - a task still genuinely in flight (submitted recently)
  - a task that's already been reviewed

Note: tests share one SQLite DB for the whole run (see conftest.py), so a
prior test's stuck task can still be sitting there when a later test's
sweep runs. Assertions below check membership in the retried-id set for
*this test's own* task(s) rather than an absolute call count, so they
stay correct regardless of what earlier tests left behind.
"""
import uuid
from datetime import datetime, timedelta, timezone

from unittest.mock import patch


async def _make_student(async_client, prefix: str) -> int:
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"{prefix}_{uid}",
            "email": f"{prefix}_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, reg.text
    return reg.json()["user"]["id"]


async def _make_task(db_session, student_id: int, **overrides):
    from app.models.group import Group
    from app.models.team_project import TeamProject, TeamProjectTeam, TeamProjectTask, TaskStatus

    uid = uuid.uuid4().hex[:8]
    group = Group(name=f"Sweep Group {uid}", teacher_id=student_id)
    db_session.add(group)
    await db_session.flush()

    team_project = TeamProject(group_id=group.id, team_size=2, deadline_days=14)
    db_session.add(team_project)
    await db_session.flush()

    team = TeamProjectTeam(team_project_id=team_project.id, name="Team 1")
    db_session.add(team)
    await db_session.flush()

    defaults = dict(
        team_id=team.id, assigned_student_id=student_id, order=0,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.submitted, submission_url="https://github.com/acme/repo",
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=30),
    )
    defaults.update(overrides)
    task = TeamProjectTask(**defaults)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


async def _run_sweep_and_collect_retried_ids(results_by_id: dict | None = None) -> set:
    """Runs the sweep with review_task_submission mocked, and returns the
    set of task ids it was called with. `results_by_id` can map a task id
    to an exception instance to raise for that one id, to exercise the
    one-failure-doesn't-block-the-rest guarantee."""
    from app import scheduler as scheduler_module

    seen_ids = set()

    async def _fake_retry(db, task_id):
        seen_ids.add(task_id)
        if results_by_id and task_id in results_by_id:
            raise results_by_id[task_id]
        return {"success": True}

    with patch(
        "app.services.team_project_task_review.review_task_submission",
        new=_fake_retry,
    ):
        await scheduler_module.job_retry_stuck_team_task_reviews()

    return seen_ids


async def test_sweep_retries_a_genuinely_stuck_task(async_client, db_session):
    student_id = await _make_student(async_client, "stucktask")
    task = await _make_task(db_session, student_id)

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert task.id in retried_ids


async def test_sweep_ignores_recently_submitted_task(async_client, db_session):
    """A task submitted 2 minutes ago is still well within how long a real
    synchronous AI review takes — must not be touched yet."""
    student_id = await _make_student(async_client, "recenttask")
    task = await _make_task(
        db_session, student_id,
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert task.id not in retried_ids


async def test_sweep_ignores_already_reviewed_task(async_client, db_session):
    from app.models.team_project import TaskStatus

    student_id = await _make_student(async_client, "reviewedtask")
    task = await _make_task(
        db_session, student_id,
        status=TaskStatus.approved,
        reviewed_at=datetime.now(timezone.utc) - timedelta(minutes=30),
    )

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert task.id not in retried_ids


async def test_sweep_one_failure_does_not_block_the_rest(async_client, db_session):
    """Same isolation guarantee review_task_submission's own timeout guard
    gives one call, one level up: one task's retry blowing up must not
    stop the sweep from processing the others."""
    student_a = await _make_student(async_client, "sweeptaskA")
    student_b = await _make_student(async_client, "sweeptaskB")
    task_a = await _make_task(db_session, student_a)
    task_b = await _make_task(db_session, student_b)

    retried_ids = await _run_sweep_and_collect_retried_ids(
        results_by_id={task_a.id: RuntimeError("boom")}
    )

    assert task_a.id in retried_ids
    assert task_b.id in retried_ids
