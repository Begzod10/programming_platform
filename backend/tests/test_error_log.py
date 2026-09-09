"""Tests for the app-error-log feature: app/core/exceptions.py's
_persist_error_log (the only writer) and the teacher/error-log endpoints
(the only reader) — see app/models/error_log.py for the design rationale.

_persist_error_log is exercised directly against a lightweight fake
Request (rather than by forcing a real unhandled 500 through a live route,
which would mean adding a test-only broken endpoint to the production
router) — it only reads `.method`, `.url.path` and `.headers.get`, all of
which the fake provides.
"""
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, update

from app.core.exceptions import _persist_error_log
from app.models.error_log import AppErrorLog
from app.models.user import Student, UserRole


class _FakeURL:
    def __init__(self, path: str):
        self.path = path


class _FakeRequest:
    """Minimal stand-in for fastapi.Request — see module docstring."""

    def __init__(self, method: str, path: str, token: str | None = None):
        self.method = method
        self.url = _FakeURL(path)
        self._headers = {"authorization": f"Bearer {token}"} if token else {}

    @property
    def headers(self):
        return self._headers


async def _register_with_username(
    async_client: AsyncClient, db_session, username: str, role: UserRole = UserRole.student
) -> tuple[int, dict]:
    """Register `username` exactly (not a random suffix), optionally flip
    to teacher, log in. Mirrors test_early_learning.py's `_register` but
    takes the literal username since _ALLOWED_USERNAMES matches on it."""
    password = "testpassword123"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["user"]["id"]
    if role != UserRole.student:
        await db_session.execute(update(Student).where(Student.id == user_id).values(role=role))
        await db_session.commit()
    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return user_id, {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_persist_error_log_writes_a_row_with_actor_identity(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    username = f"crashuser_{uid}"
    user_id, headers = await _register_with_username(async_client, db_session, username)
    token = headers["Authorization"].removeprefix("Bearer ")

    request = _FakeRequest("GET", "/api/v1/does-not-matter", token=token)
    await _persist_error_log(request, ValueError("boom"), "Traceback (most recent call last):\nValueError: boom")

    row = (
        await db_session.execute(
            select(AppErrorLog).where(AppErrorLog.actor_id == user_id)
        )
    ).scalar_one()
    assert row.method == "GET"
    assert row.path == "/api/v1/does-not-matter"
    assert row.error_type == "ValueError"
    assert row.message == "boom"
    assert "ValueError: boom" in row.traceback
    assert row.actor_username == username
    assert row.actor_role == "student"


@pytest.mark.asyncio
async def test_persist_error_log_handles_anonymous_request(async_client, db_session):
    request = _FakeRequest("POST", "/api/v1/play/whatever")
    await _persist_error_log(request, RuntimeError("no token"), "tb")

    row = (
        await db_session.execute(
            select(AppErrorLog).where(AppErrorLog.path == "/api/v1/play/whatever")
        )
    ).scalar_one()
    assert row.actor_id is None
    assert row.actor_username is None
    assert row.actor_role is None


@pytest.mark.asyncio
async def test_allowlisted_teacher_can_list_and_delete(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    # A fresh unique username per test run, but still matching the
    # allowlist prefix pattern is NOT what we want here — the allowlist is
    # an exact-match set, so this test registers the literal
    # "rimefara_teach" account. Guard against test-order collisions with a
    # cleanup at the end rather than randomizing the username away.
    username = "rimefara_teach"
    existing = (
        await db_session.execute(select(Student).where(Student.username == username))
    ).scalar_one_or_none()
    if existing is not None:
        pytest.skip("rimefara_teach already exists in this test DB run — avoiding a collision")

    _, headers = await _register_with_username(async_client, db_session, username, role=UserRole.teacher)

    request = _FakeRequest("GET", f"/api/v1/probe-{uid}")
    await _persist_error_log(request, KeyError("missing"), "tb-for-probe")

    resp = await async_client.get("/api/v1/teacher/error-log", headers=headers)
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    assert any(i["path"] == f"/api/v1/probe-{uid}" for i in items)
    entry_id = next(i["id"] for i in items if i["path"] == f"/api/v1/probe-{uid}")

    del_resp = await async_client.delete(f"/api/v1/teacher/error-log/{entry_id}", headers=headers)
    assert del_resp.status_code == 200, del_resp.text

    remaining = (
        await db_session.execute(select(AppErrorLog).where(AppErrorLog.id == entry_id))
    ).scalar_one_or_none()
    assert remaining is None


@pytest.mark.asyncio
async def test_non_allowlisted_teacher_gets_403(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    username = f"regular_teacher_{uid}"
    _, headers = await _register_with_username(async_client, db_session, username, role=UserRole.teacher)

    resp = await async_client.get("/api/v1/teacher/error-log", headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_student_gets_403(async_client, db_session):
    uid = uuid.uuid4().hex[:8]
    username = f"regular_student_{uid}"
    _, headers = await _register_with_username(async_client, db_session, username)

    resp = await async_client.get("/api/v1/teacher/error-log", headers=headers)
    assert resp.status_code == 403
