import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import pytest
from sqlalchemy import select
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.db.database import AsyncSessionLocal
from app.main import app
from app.models.daily_quota import StudentDailyProgress
from app.models.pc_control import PcDevice
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


def test_unlock_pushes_state_to_signed_in_device(client):
    student_id, token = _signin(client)

    async def _unlock_and_push():
        async with AsyncSessionLocal() as db:
            await daily_quota_service.get_today(db, student_id)  # creates today's row
            row = (await db.execute(select(StudentDailyProgress).where(
                StudentDailyProgress.student_id == student_id))).scalars().first()
            row.required = 0
            row.base_required = 0
            await db.commit()
            await daily_quota_service._emit_unlocked(db, student_id)

    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        first = ws.receive_json()
        assert first["type"] == "state"
        if first["locked"] is False:
            pytest.skip("quota disabled or rest day: device is never locked")
        client.portal.call(_unlock_and_push)
        frame = ws.receive_json()
        assert frame["type"] == "state"
        assert frame["locked"] is False


def test_push_for_student_without_session_is_noop(client):
    async def _go():
        async with AsyncSessionLocal() as db:
            await pc_push_service.push_state_for_student(db, 987654321)
            await pc_push_service.push_state_to_device(db, 987654321)
            await daily_quota_service._emit_unlocked(db, 987654321)
    client.portal.call(_go)
