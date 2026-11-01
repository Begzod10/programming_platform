import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.db.database import AsyncSessionLocal
from app.main import app
from app.models.daily_quota import StudentDailyProgress
from app.models.pc_control import PcDevice, PcSession
from app.services import daily_quota_service, pc_push_service

PW = "securepass123"


def _uid() -> str:
    return uuid.uuid4().hex[:10]


def _signin(c: TestClient):
    uid = _uid()
    r = c.post("/api/v1/auth/register", json={
        "username": f"pcws_{uid}", "email": f"pcws_{uid}@example.com", "password": PW})
    assert r.status_code == 201, r.text
    student_id = r.json()["user"]["id"]
    r = c.post("/api/v1/pc/login", json={
        "username": f"pcws_{uid}", "password": PW,
        "hostname": "lab-ws", "machine_key": f"mk-ws-{uid}"})
    assert r.status_code == 200, r.text
    return student_id, r.json()["token"]


@pytest.fixture
def client():
    from app.core.rate_limit import _counters
    _counters.clear()
    # The app lifespan runs Postgres-only DDL; skip it (tables come from conftest).
    @asynccontextmanager
    async def _no_lifespan(_app):
        yield
    original = app.router.lifespan_context
    app.router.lifespan_context = _no_lifespan
    try:
        with TestClient(app) as c:  # `with` keeps one portal/event loop for ws + helper calls
            yield c
    finally:
        app.router.lifespan_context = original


def test_first_frame_is_state(client):
    _, token = _signin(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        frame = ws.receive_json()
        assert frame["type"] == "state"
        assert "locked" in frame


def test_bad_token_closes_4001(client):
    with pytest.raises(WebSocketDisconnect) as ei:
        with client.websocket_connect("/api/v1/pc/ws?token=garbage") as ws:
            ws.receive_json()
    assert ei.value.code == 4001


def test_missing_token_closes_4001(client):
    with pytest.raises(WebSocketDisconnect) as ei:
        with client.websocket_connect("/api/v1/pc/ws") as ws:
            ws.receive_json()
    assert ei.value.code == 4001


def test_heartbeat_updates_device_and_pongs(client):
    _, token = _signin(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        ws.receive_json()
        ws.send_json({"type": "bogus-garbage"})
        ws.send_text("not json at all")
        ws.send_json({"type": "hb", "app": "notepad.exe"})
        assert ws.receive_json() == {"type": "pong"}

    async def _read():
        async with AsyncSessionLocal() as db:
            return (await db.execute(
                select(PcDevice).where(PcDevice.hostname == "lab-ws").order_by(PcDevice.id.desc())
            )).scalars().first()
    dev = client.portal.call(_read)
    assert dev.last_app == "notepad.exe"
    assert isinstance(dev.last_seen_at, datetime)


@pytest.fixture
def quota_enforced(client):
    """Deterministic quota config: enabled, no rest days, base quota >= 1. Restored afterwards."""
    async def _set(values):
        async with AsyncSessionLocal() as db:
            cfg = await daily_quota_service.get_config(db)
            old = {k: getattr(cfg, k) for k in values}
            for k, v in values.items():
                setattr(cfg, k, v)
            await db.commit()
            return old
    old = client.portal.call(_set, {"enabled": True, "rest_days": "", "base_lessons": 2, "enforce_from": None})
    yield
    client.portal.call(_set, old)


def test_unlock_pushes_state_to_signed_in_device(client, quota_enforced):
    student_id, token = _signin(client)

    async def _unlock_and_push():
        async with AsyncSessionLocal() as db:
            row = (await db.execute(select(StudentDailyProgress).where(
                StudentDailyProgress.student_id == student_id))).scalars().first()
            row.required = 0
            row.base_required = 0
            await db.commit()
            await daily_quota_service._emit_unlocked(db, student_id)

    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        first = ws.receive_json()
        assert first["type"] == "state"
        assert first["locked"] is True
        client.portal.call(_unlock_and_push)
        frame = ws.receive_json()
        assert frame["type"] == "state"
        assert frame["locked"] is False


def test_heartbeat_delivers_state_change_that_was_never_pushed(client, quota_enforced):
    student_id, token = _signin(client)

    async def _meet_quota_silently():  # no _emit_unlocked: only the heartbeat can notice
        async with AsyncSessionLocal() as db:
            row = (await db.execute(select(StudentDailyProgress).where(
                StudentDailyProgress.student_id == student_id))).scalars().first()
            row.required = 0
            row.base_required = 0
            await db.commit()

    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        assert ws.receive_json()["locked"] is True
        client.portal.call(_meet_quota_silently)
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}
        frame = ws.receive_json()
        assert frame["type"] == "state" and frame["locked"] is False
        # unchanged since the last frame sent on this socket: only a pong
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}


def test_heartbeat_delivers_state_after_platform_hosts_change(client, monkeypatch):
    """A changed PC_PLATFORM_HOSTS must reach a connected agent on the next heartbeat."""
    from app.config import settings
    monkeypatch.setattr(settings, "PC_PLATFORM_HOSTS", "old.example.uz")  # restored by monkeypatch
    _, token = _signin(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        first = ws.receive_json()
        assert first["type"] == "state"
        assert first["browser_hosts"] == ["old.example.uz"]

        monkeypatch.setattr(settings, "PC_PLATFORM_HOSTS", "new.example.uz,lms.example.uz")
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}
        frame = ws.receive_json()
        assert frame["type"] == "state"
        assert frame["browser_hosts"] == ["new.example.uz", "lms.example.uz"]

        # unchanged afterwards: only a pong
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}
        ws.send_json({"type": "hb", "app": None})
        assert ws.receive_json() == {"type": "pong"}


def test_heartbeat_unchanged_state_sends_only_pong(client):
    _, token = _signin(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        ws.receive_json()
        for _ in range(2):
            ws.send_json({"type": "hb", "app": "x.exe"})
            assert ws.receive_json() == {"type": "pong"}


def _last_seen(client, machine_key_prefix_host="lab-ws"):
    async def _read():
        async with AsyncSessionLocal() as db:
            return (await db.execute(
                select(PcDevice).where(PcDevice.hostname == machine_key_prefix_host)
                .order_by(PcDevice.id.desc()))).scalars().first().last_seen_at
    return client.portal.call(_read)


def test_heartbeat_after_logout_closes_4001_and_does_not_write(client):
    _, token = _signin(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        ws.receive_json()
        r = client.post("/api/v1/pc/logout", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        before = _last_seen(client)
        with pytest.raises(WebSocketDisconnect) as ei:
            ws.send_json({"type": "hb", "app": "stale.exe"})
            ws.receive_json()
        assert ei.value.code == 4001
    assert _last_seen(client) == before


def test_heartbeat_rechecks_session_even_without_forced_close(client):
    # Session closed behind the socket's back (no logout endpoint, so no close_all).
    _, token = _signin(client)

    async def _close_sessions():
        async with AsyncSessionLocal() as db:
            for sess in (await db.execute(select(PcSession).where(PcSession.signed_out_at.is_(None)))).scalars():
                sess.signed_out_at = datetime.now(timezone.utc)
            await db.commit()
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        ws.receive_json()
        client.portal.call(_close_sessions)
        with pytest.raises(WebSocketDisconnect) as ei:
            ws.send_json({"type": "hb", "app": "x.exe"})
            ws.receive_json()
        assert ei.value.code == 4001


def test_second_login_closes_first_socket_without_new_students_state(client):
    uid = _uid()
    for n in ("a", "b"):
        r = client.post("/api/v1/auth/register", json={
            "username": f"pcws{n}_{uid}", "email": f"pcws{n}_{uid}@example.com", "password": PW})
        assert r.status_code == 201

    def login(n):
        r = client.post("/api/v1/pc/login", json={
            "username": f"pcws{n}_{uid}", "password": PW,
            "hostname": "lab-ws", "machine_key": f"mk-ws-{uid}"})
        assert r.status_code == 200
        return r.json()["token"]

    token_a = login("a")
    with client.websocket_connect(f"/api/v1/pc/ws?token={token_a}") as ws:
        assert ws.receive_json()["type"] == "state"
        login("b")
        with pytest.raises(WebSocketDisconnect) as ei:
            ws.send_json({"type": "hb", "app": None})
            ws.receive_json()  # must be a close, never B's state frame
        assert ei.value.code == 4001


def test_push_for_student_without_session_is_noop(client):
    async def _go():
        async with AsyncSessionLocal() as db:
            await pc_push_service.push_state_for_student(db, 987654321)
            await pc_push_service.push_state_to_device(db, 987654321)
            await daily_quota_service._emit_unlocked(db, 987654321)
    client.portal.call(_go)


def test_pc_token_rejected_on_student_notifications_ws(client):
    _, token = _signin(client)
    with pytest.raises(WebSocketDisconnect) as ei:
        with client.websocket_connect(f"/api/v1/notifications/ws?token={token}") as ws:
            ws.receive_json()
    assert ei.value.code == 4001
