"""Tests for job_retry_stuck_project_reviews (app/scheduler.py) — the
safety net behind the project-4926 incident (see
_run_ai_review_and_persist_failure's docstring in projects.py for the
full story). Defense-in-depth alongside that timeout fix: this sweep
catches a project stuck at status="Submitted", reviewed_at=None with no
instructor_feedback at all, regardless of *why* it never got a review
attempt persisted, and retries it every 15 minutes.

Deliberately narrow — must NOT touch:
  - a project still genuinely in flight (submitted recently)
  - a project that already failed with a real, persisted reason
  - a project that's already been reviewed

Note: tests share one SQLite DB for the whole run (see conftest.py), so a
prior test's stuck project can still be sitting there when a later test's
sweep runs. Assertions below check membership in the retried-id set for
*this test's own* project(s) rather than an absolute call count, so they
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


async def _make_project(db_session, student_id: int, **overrides):
    from app.models.project import Project

    defaults = dict(
        student_id=student_id,
        title="Loyiha",
        description="",
        difficulty_level="Easy",
        status="Submitted",
        project_files="/uploads/projects/sweep-test.zip",
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=30),
    )
    defaults.update(overrides)
    project = Project(**defaults)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


async def _run_sweep_and_collect_retried_ids(results_by_id: dict | None = None) -> set:
    """Runs the sweep with _run_ai_review_and_persist_failure mocked, and
    returns the set of project ids it was called with. `results_by_id` can
    map a project id to an exception instance to raise for that one id,
    to exercise the one-failure-doesn't-block-the-rest guarantee."""
    from app import scheduler as scheduler_module

    seen_ids = set()

    async def _fake_retry(db, project):
        seen_ids.add(project.id)
        if results_by_id and project.id in results_by_id:
            raise results_by_id[project.id]
        return {"success": True}

    with patch(
        "app.api.v1.endpoints.projects._run_ai_review_and_persist_failure",
        new=_fake_retry,
    ):
        await scheduler_module.job_retry_stuck_project_reviews()

    return seen_ids


async def test_sweep_retries_a_genuinely_stuck_project(async_client, db_session):
    student_id = await _make_student(async_client, "stuck")
    project = await _make_project(db_session, student_id)

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert project.id in retried_ids


async def test_sweep_ignores_recently_submitted_project(async_client, db_session):
    """A project submitted 2 minutes ago is still well within how long a
    real synchronous AI review takes — must not be touched yet."""
    student_id = await _make_student(async_client, "recent")
    project = await _make_project(
        db_session, student_id,
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert project.id not in retried_ids


async def test_sweep_ignores_project_with_persisted_failure_reason(async_client, db_session):
    """A project that already failed for a real, known reason (persisted
    instructor_feedback) is working as intended — not the "zero trace"
    incident this sweep guards against. Leave it for the teacher/student to
    act on, don't keep retrying it forever."""
    student_id = await _make_student(async_client, "knownfail")
    project = await _make_project(
        db_session, student_id,
        instructor_feedback="AI baholash vaqtincha ishlamayapti.",
    )

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert project.id not in retried_ids


async def test_sweep_ignores_already_reviewed_project(async_client, db_session):
    student_id = await _make_student(async_client, "reviewed")
    project = await _make_project(
        db_session, student_id,
        status="Approved",
        reviewed_at=datetime.now(timezone.utc) - timedelta(minutes=30),
    )

    retried_ids = await _run_sweep_and_collect_retried_ids()

    assert project.id not in retried_ids


async def test_sweep_one_failure_does_not_block_the_rest(async_client, db_session):
    """Same isolation guarantee _run_ai_review_and_persist_failure gives one
    request, one level up: one project's retry blowing up must not stop the
    sweep from processing the others."""
    student_a = await _make_student(async_client, "sweepA")
    student_b = await _make_student(async_client, "sweepB")
    project_a = await _make_project(db_session, student_a)
    project_b = await _make_project(db_session, student_b)

    retried_ids = await _run_sweep_and_collect_retried_ids(
        results_by_id={project_a.id: RuntimeError("boom")}
    )

    assert project_a.id in retried_ids
    assert project_b.id in retried_ids
