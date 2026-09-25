"""
Tests for the 10-minute cooldown between a student's project submissions
(services/submission_cooldown.py) and its enforcement on the endpoints.
"""

import uuid
from datetime import timedelta

import pytest_asyncio
from httpx import AsyncClient

from app.models.project import Project
from app.services.submission_cooldown import seconds_until_can_submit
from app.utils.datetime_utils import utcnow


@pytest_asyncio.fixture
async def student(async_client: AsyncClient):
    """Fresh student per test so earlier tests' projects don't start a timer."""
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"cool_{uid}", "email": f"cool_{uid}@example.com",
              "password": "securepass123"},
    )
    assert reg.status_code == 201, reg.text
    body = reg.json()
    return body["user"]["id"], {"Authorization": f"Bearer {body['access_token']}"}


async def _submitted(db, student_id, ago: timedelta) -> Project:
    p = Project(student_id=student_id, title="Loyiha", description="desc",
                difficulty_level="Easy", status="Submitted",
                submitted_at=utcnow() - ago)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


# ── seconds_until_can_submit ──────────────────────────────────────────────────

async def test_no_previous_submission_means_no_wait(db_session, student):
    sid, _ = student
    assert await seconds_until_can_submit(db_session, sid) == 0


async def test_draft_projects_do_not_start_the_timer(db_session, student):
    sid, _ = student
    db_session.add(Project(student_id=sid, title="Draft", description="d",
                           difficulty_level="Easy", status="Draft"))
    await db_session.commit()
    assert await seconds_until_can_submit(db_session, sid) == 0


async def test_recent_submission_blocks_for_rest_of_10_minutes(db_session, student):
    sid, _ = student
    await _submitted(db_session, sid, timedelta(minutes=3))
    wait = await seconds_until_can_submit(db_session, sid)
    assert 7 * 60 - 5 <= wait <= 7 * 60 + 1


async def test_submission_older_than_10_minutes_does_not_block(db_session, student):
    sid, _ = student
    await _submitted(db_session, sid, timedelta(minutes=10, seconds=5))
    assert await seconds_until_can_submit(db_session, sid) == 0


async def test_project_can_be_excluded_from_its_own_cooldown(db_session, student):
    sid, _ = student
    p = await _submitted(db_session, sid, timedelta(minutes=1))
    assert await seconds_until_can_submit(db_session, sid) > 0
    assert await seconds_until_can_submit(db_session, sid, exclude_project_id=p.id) == 0


# ── Endpoints ─────────────────────────────────────────────────────────────────

NEW_PROJECT = {
    "title": "Ikkinchi loyiha",
    "description": "Cooldown testi uchun yetarlicha uzun tavsif matni",
    "github_url": "https://github.com/test/project",
    "technologies_used": ["HTML"],
    "difficulty_level": "Easy",
}


async def test_create_project_during_cooldown_returns_429(async_client, db_session, student):
    sid, headers = student
    await _submitted(db_session, sid, timedelta(minutes=2))
    resp = await async_client.post("/api/v1/project/", headers=headers, json=NEW_PROJECT)
    assert resp.status_code == 429, resp.text
    body = resp.json()
    message = body.get("error", {}).get("message") or body.get("detail")
    assert "daqiqa" in message


async def test_create_project_after_cooldown_is_allowed(async_client, db_session, student):
    sid, headers = student
    await _submitted(db_session, sid, timedelta(minutes=11))
    resp = await async_client.post("/api/v1/project/", headers=headers, json=NEW_PROJECT)
    assert resp.status_code == 201, resp.text


async def test_other_students_are_not_affected(async_client, db_session, student):
    sid, _ = student
    await _submitted(db_session, sid, timedelta(minutes=1))
    uid = uuid.uuid4().hex[:8]
    other = (await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"cool2_{uid}", "email": f"cool2_{uid}@example.com",
              "password": "securepass123"},
    )).json()
    resp = await async_client.post(
        "/api/v1/project/", json=NEW_PROJECT,
        headers={"Authorization": f"Bearer {other['access_token']}"})
    assert resp.status_code == 201, resp.text
