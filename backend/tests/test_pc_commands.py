import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, func, select, update
from starlette.testclient import TestClient

from app.db.database import AsyncSessionLocal
from app.main import app
from app.models.group import Group
from app.models.pc_control import PcCommand, PcDevice, PcSession, PcUsageEvent
from app.models.user import Student, UserRole
from app.services import daily_quota_service

PW = "securepass123"
T = "/api/v1/teacher/pc"


def _uid() -> str:
    return uuid.uuid4().hex[:10]


@pytest.fixture
def client():
    from app.core.rate_limit import _counters
    _counters.clear()

    @asynccontextmanager
    async def _no_lifespan(_app):
        yield
    original = app.router.lifespan_context
    app.router.lifespan_context = _no_lifespan
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.router.lifespan_context = original


@pytest.fixture(autouse=True)
def clean_all_commands(client):
    # An `all`-scope lock left behind would poison other PC tests.
    async def _reset():
        async with AsyncSessionLocal() as db:
            await db.execute(delete(PcCommand).where(PcCommand.scope_type == "all"))
            await db.commit()
    client.portal.call(_reset)
    yield
    client.portal.call(_reset)


@pytest.fixture
def quota_enforced(client):
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


def _register(c, role=None):
    uid = _uid()
    r = c.post("/api/v1/auth/register", json={
        "username": f"pcc_{uid}", "email": f"pcc_{uid}@example.com", "password": PW})
    assert r.status_code == 201, r.text
    user_id = r.json()["user"]["id"]
    if role is not None:
        async def _flip():
            async with AsyncSessionLocal() as db:
                await db.execute(update(Student).where(Student.id == user_id).values(role=role))
                await db.commit()
        c.portal.call(_flip)
    r = c.post("/api/v1/auth/login", json={"username": f"pcc_{uid}", "password": PW})
    assert r.status_code == 200, r.text
    return user_id, f"pcc_{uid}", r.json()["access_token"]


@pytest.fixture
def teacher(client):
    tid, _, token = _register(client, UserRole.teacher)
    return tid, {"Authorization": f"Bearer {token}"}


def _device_login(c):
    """Fresh student + fresh device. Returns (student_id, device_id, token, headers)."""
    sid, uname, _ = _register(c)
    uid = _uid()
    r = c.post("/api/v1/pc/login", json={
        "username": uname, "password": PW, "hostname": f"lab-cmd-{uid}", "machine_key": f"mk-cmd-{uid}"})
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    h = {"Authorization": f"Bearer {token}"}

    async def _dev():
        async with AsyncSessionLocal() as db:
            return (await db.execute(select(PcSession.device_id).where(
                PcSession.student_id == sid))).scalars().first()
    return sid, c.portal.call(_dev), token, h


def _group(client, teacher_id):
    async def _mk():
        async with AsyncSessionLocal() as db:
            g = Group(name=f"g_{_uid()}", teacher_id=teacher_id)
            db.add(g)
            await db.commit()
            await db.refresh(g)
            return g.id
    return client.portal.call(_mk)


def _set_group(client, device_id, group_id):
    async def _go():
        async with AsyncSessionLocal() as db:
            await db.execute(update(PcDevice).where(PcDevice.id == device_id).values(group_id=group_id))
            await db.commit()
    client.portal.call(_go)


def _ev(start, minutes=5, app_name="code.exe", locked=False):
    return {"app_name": app_name, "started_at": start.isoformat(),
            "ended_at": (start + timedelta(minutes=minutes)).isoformat(), "was_locked": locked}


def _count_events(client, session_id_of_student):
    async def _c():
        async with AsyncSessionLocal() as db:
            return (await db.execute(select(func.count()).select_from(PcUsageEvent).join(
                PcSession, PcSession.id == PcUsageEvent.session_id).where(
                PcSession.student_id == session_id_of_student))).scalar()
    return client.portal.call(_c)


# ---------- usage ----------

def test_valid_usage_batch_stored(client):
    sid, _, _, h = _device_login(client)
    now = datetime.now(timezone.utc)
    r = client.post("/api/v1/pc/usage", headers=h, json={"events": [
        _ev(now - timedelta(minutes=30)), _ev(now - timedelta(minutes=20), locked=True, app_name="chrome.exe")]})
    assert r.status_code == 200, r.text
    assert _count_events(client, sid) == 2


@pytest.mark.parametrize("bad", ["reversed", "equal", "13h", "empty_app", "long_app"])
def test_invalid_event_rejects_whole_batch(client, bad):
    sid, _, _, h = _device_login(client)
    now = datetime.now(timezone.utc)
    good = _ev(now - timedelta(hours=1))
    if bad == "reversed":
        evil = {"app_name": "x.exe", "started_at": now.isoformat(),
                "ended_at": (now - timedelta(minutes=1)).isoformat(), "was_locked": False}
    elif bad == "equal":
        evil = {"app_name": "x.exe", "started_at": now.isoformat(), "ended_at": now.isoformat(), "was_locked": False}
    elif bad == "13h":
        evil = _ev(now - timedelta(hours=14), minutes=13 * 60)
    elif bad == "empty_app":
        evil = _ev(now - timedelta(hours=2), app_name="")
    else:
        evil = _ev(now - timedelta(hours=2), app_name="a" * 256)
    r = client.post("/api/v1/pc/usage", headers=h, json={"events": [good, evil]})
    assert r.status_code == 422, r.text
    assert _count_events(client, sid) == 0


def test_exactly_12h_event_accepted(client):
    sid, _, _, h = _device_login(client)
    now = datetime.now(timezone.utc)
    r = client.post("/api/v1/pc/usage", headers=h, json={"events": [_ev(now - timedelta(hours=13), minutes=720)]})
    assert r.status_code == 200, r.text


def test_501_events_422_and_500_ok(client):
    sid, _, _, h = _device_login(client)
    now = datetime.now(timezone.utc) - timedelta(hours=2)
    r = client.post("/api/v1/pc/usage", headers=h, json={"events": [_ev(now)] * 501})
    assert r.status_code == 422
    assert _count_events(client, sid) == 0
    r = client.post("/api/v1/pc/usage", headers=h, json={"events": [_ev(now)] * 500})
    assert r.status_code == 200, r.text
    assert _count_events(client, sid) == 500


def test_usage_requires_device_token(client):
    assert client.post("/api/v1/pc/usage", json={"events": []}).status_code == 401


# ---------- devices list ----------

def _find(devices, device_id):
    return next(d for d in devices if d["id"] == device_id)


def test_devices_online_after_heartbeat_and_offline_when_stale(client, teacher, quota_enforced):
    _, th = teacher
    sid, did, token, h = _device_login(client)
    assert client.get("/api/v1/pc/state", headers=h).status_code == 200  # heartbeat-ish
    d = _find(client.get(f"{T}/devices", headers=th).json(), did)
    assert d["online"] is True
    assert d["student"]["id"] == sid
    assert d["locked"] is True and d["reason"] == "quota_pending"
    assert set(d) == {"id", "hostname", "group_id", "online", "student", "locked",
                      "reason", "last_app", "last_seen_at"}

    async def _stale():
        async with AsyncSessionLocal() as db:
            await db.execute(update(PcDevice).where(PcDevice.id == did).values(
                last_seen_at=datetime.now(timezone.utc) - timedelta(minutes=5)))
            await db.commit()
    client.portal.call(_stale)
    d = _find(client.get(f"{T}/devices", headers=th).json(), did)
    assert d["online"] is False


def test_device_with_no_session_shows_no_student(client, teacher):
    _, th = teacher
    _, did, _, h = _device_login(client)
    client.post("/api/v1/pc/logout", headers=h)
    d = _find(client.get(f"{T}/devices", headers=th).json(), did)
    assert d["student"] is None and d["locked"] is True and d["reason"] == "no_student"


# ---------- patch ----------

def test_patch_device_group(client, teacher):
    tid, th = teacher
    _, did, _, _ = _device_login(client)
    gid = _group(client, tid)
    r = client.patch(f"{T}/devices/{did}", headers=th, json={"group_id": gid})
    assert r.status_code == 200, r.text
    assert _find(client.get(f"{T}/devices", headers=th).json(), did)["group_id"] == gid
    assert client.patch(f"{T}/devices/{did}", headers=th, json={"group_id": None}).status_code == 200
    assert _find(client.get(f"{T}/devices", headers=th).json(), did)["group_id"] is None
    assert client.patch(f"{T}/devices/{did}", headers=th, json={"group_id": 99999999}).status_code == 404
    assert client.patch(f"{T}/devices/99999999", headers=th, json={"group_id": None}).status_code == 404


def test_patch_device_pushes_state(client, teacher):
    tid, th = teacher
    _, did, token, _ = _device_login(client)
    gid = _group(client, tid)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        assert ws.receive_json()["type"] == "state"
        assert client.patch(f"{T}/devices/{did}", headers=th, json={"group_id": gid}).status_code == 200
        assert ws.receive_json()["type"] == "state"


# ---------- commands ----------

def _state(client, h):
    return client.get("/api/v1/pc/state", headers=h).json()


def test_lock_all_then_clear(client, teacher, quota_enforced):
    _, th = teacher
    _, _, _, h1 = _device_login(client)
    _, _, _, h2 = _device_login(client)
    assert _state(client, h1)["reason"] == "quota_pending"
    r = client.post(f"{T}/commands", headers=th, json={"scope_type": "all", "scope_id": None, "type": "lock"})
    assert r.status_code == 200, r.text
    for h in (h1, h2):
        s = _state(client, h)
        assert s["locked"] is True and s["reason"] == "teacher_lock"
    r = client.post(f"{T}/commands", headers=th, json={"scope_type": "all", "scope_id": None, "type": "clear"})
    assert r.status_code == 200, r.text
    for h in (h1, h2):
        assert _state(client, h)["reason"] == "quota_pending"


def test_unlock_device_overrides_all_lock(client, teacher, quota_enforced):
    _, th = teacher
    _, did, _, h = _device_login(client)
    client.post(f"{T}/commands", headers=th, json={"scope_type": "all", "type": "lock"})
    r = client.post(f"{T}/commands", headers=th, json={"scope_type": "device", "scope_id": did, "type": "unlock"})
    assert r.status_code == 200, r.text
    s = _state(client, h)
    assert s["locked"] is False and s["reason"] == "teacher_unlock"


def test_newer_all_lock_beats_older_device_unlock_via_api(client, teacher, quota_enforced):
    _, th = teacher
    _, did, _, h = _device_login(client)
    client.post(f"{T}/commands", headers=th, json={"scope_type": "device", "scope_id": did, "type": "unlock"})
    assert _state(client, h)["reason"] == "teacher_unlock"
    client.post(f"{T}/commands", headers=th, json={"scope_type": "all", "type": "lock"})
    s = _state(client, h)
    assert s["locked"] is True and s["reason"] == "teacher_lock"


def test_device_unlock_does_not_carry_over_to_next_student(client, teacher, quota_enforced):
    _, th = teacher
    uid = _uid()
    mk = f"mk-carry-{uid}"

    def login():
        sid, uname, _ = _register(client)
        r = client.post("/api/v1/pc/login", json={
            "username": uname, "password": PW, "hostname": f"lab-{uid}", "machine_key": mk})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}, r.json()["state"]

    h_a, _ = login()
    did = client.get(f"{T}/devices", headers=th).json()
    did = next(d["id"] for d in did if d["hostname"] == f"lab-{uid}")
    r = client.post(f"{T}/commands", headers=th, json={"scope_type": "device", "scope_id": did, "type": "unlock"})
    assert r.status_code == 200, r.text
    assert _state(client, h_a)["reason"] == "teacher_unlock"

    async def _backdate():  # make the ordering independent of timestamp resolution
        async with AsyncSessionLocal() as db:
            await db.execute(update(PcCommand).where(PcCommand.id == r.json()["id"]).values(
                created_at=datetime.now(timezone.utc) - timedelta(hours=1)))
            await db.execute(update(PcSession).where(PcSession.device_id == did).values(
                signed_in_at=datetime.now(timezone.utc) - timedelta(hours=2)))
            await db.commit()
    client.portal.call(_backdate)
    h_b, state_b = login()
    assert state_b["reason"] == "quota_pending"
    assert _state(client, h_b)["locked"] is True


def test_all_lock_before_sign_in_applies_to_new_session(client, teacher, quota_enforced):
    _, th = teacher
    client.post(f"{T}/commands", headers=th, json={"scope_type": "all", "type": "lock"})
    _, _, _, h = _device_login(client)
    assert _state(client, h)["reason"] == "teacher_lock"


def test_group_command_does_not_reach_other_group(client, teacher, quota_enforced):
    tid, th = teacher
    g1, g2 = _group(client, tid), _group(client, tid)
    _, d1, t1, h1 = _device_login(client)
    _, d2, t2, h2 = _device_login(client)
    _set_group(client, d1, g1)
    _set_group(client, d2, g2)
    with client.websocket_connect(f"/api/v1/pc/ws?token={t1}") as ws1, \
            client.websocket_connect(f"/api/v1/pc/ws?token={t2}") as ws2:
        ws1.receive_json()
        ws2.receive_json()
        r = client.post(f"{T}/commands", headers=th, json={"scope_type": "group", "scope_id": g1, "type": "lock"})
        assert r.status_code == 200, r.text
        frame = ws1.receive_json()
        assert frame["type"] == "state" and frame["reason"] == "teacher_lock"
        # other group's socket got nothing: the next frame it sees is the pong for our heartbeat
        ws2.send_json({"type": "hb", "app": None})
        assert ws2.receive_json() == {"type": "pong"}
    assert _state(client, h1)["reason"] == "teacher_lock"
    assert _state(client, h2)["reason"] == "quota_pending"


def test_message_frame_reaches_device_socket(client, teacher):
    _, th = teacher
    _, did, token, _ = _device_login(client)
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        ws.receive_json()
        r = client.post(f"{T}/commands", headers=th, json={
            "scope_type": "device", "scope_id": did, "type": "message", "payload": {"text": "Salom"}})
        assert r.status_code == 200, r.text
        assert ws.receive_json() == {"type": "message", "text": "Salom"}
        r = client.post(f"{T}/commands", headers=th, json={
            "scope_type": "all", "type": "message", "payload": {"text": "Hammaga"}})
        assert r.status_code == 200, r.text
        assert ws.receive_json() == {"type": "message", "text": "Hammaga"}


def test_message_does_not_affect_lock_state(client, teacher, quota_enforced):
    _, th = teacher
    _, did, _, h = _device_login(client)
    client.post(f"{T}/commands", headers=th, json={
        "scope_type": "device", "scope_id": did, "type": "message", "payload": {"text": "hi"}})
    assert _state(client, h)["reason"] == "quota_pending"


@pytest.mark.parametrize("payload", [{"text": "x" * 501}, {"text": ""}, {"text": "   "}, {}, None])
def test_bad_message_422(client, teacher, payload):
    _, th = teacher
    _, did, _, _ = _device_login(client)
    r = client.post(f"{T}/commands", headers=th, json={
        "scope_type": "device", "scope_id": did, "type": "message", "payload": payload})
    assert r.status_code == 422, r.text


def test_message_500_chars_ok(client, teacher):
    _, th = teacher
    _, did, _, _ = _device_login(client)
    r = client.post(f"{T}/commands", headers=th, json={
        "scope_type": "device", "scope_id": did, "type": "message", "payload": {"text": "x" * 500}})
    assert r.status_code == 200, r.text


@pytest.mark.parametrize("body,code", [
    ({"scope_type": "all", "type": "explode"}, 422),
    ({"scope_type": "planet", "type": "lock"}, 422),
    ({"scope_type": "all", "scope_id": 3, "type": "lock"}, 422),
    ({"scope_type": "device", "type": "lock"}, 422),
    ({"scope_type": "device", "scope_id": 99999999, "type": "lock"}, 404),
    ({"scope_type": "group", "scope_id": 99999999, "type": "lock"}, 404),
])
def test_invalid_commands(client, teacher, body, code):
    _, th = teacher
    assert client.post(f"{T}/commands", headers=th, json=body).status_code == code


def test_command_stores_created_by(client, teacher):
    tid, th = teacher
    _, did, _, _ = _device_login(client)
    r = client.post(f"{T}/commands", headers=th, json={"scope_type": "device", "scope_id": did, "type": "lock"})
    cid = r.json()["id"]

    async def _get():
        async with AsyncSessionLocal() as db:
            return await db.get(PcCommand, cid)
    assert client.portal.call(_get).created_by == tid


# ---------- auth ----------

def test_non_teacher_403_everywhere(client):
    _, _, token = _register(client)
    h = {"Authorization": f"Bearer {token}"}
    assert client.get(f"{T}/devices", headers=h).status_code == 403
    assert client.patch(f"{T}/devices/1", headers=h, json={"group_id": None}).status_code == 403
    assert client.post(f"{T}/commands", headers=h, json={"scope_type": "all", "type": "lock"}).status_code == 403


def test_device_token_rejected_on_teacher_endpoints(client):
    _, _, _, h = _device_login(client)
    assert client.get(f"{T}/devices", headers=h).status_code in (401, 403)
    assert client.patch(f"{T}/devices/1", headers=h, json={"group_id": None}).status_code in (401, 403)
    assert client.post(f"{T}/commands", headers=h, json={"scope_type": "all", "type": "lock"}).status_code in (401, 403)
