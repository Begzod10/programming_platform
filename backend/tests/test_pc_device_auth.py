import hashlib
import uuid

from sqlalchemy import select, update

from app.db.database import AsyncSessionLocal
from app.models.pc_control import PcDevice, PcSession
from app.models.user import Student, UserRole
from app.services.pc_lock_service import compute_state

PW = "securepass123"


def _uid() -> str:
    return uuid.uuid4().hex[:10]


async def _register(client, role=None):
    uid = _uid()
    resp = await client.post("/api/v1/auth/register", json={
        "username": f"pc_{uid}", "email": f"pc_{uid}@example.com", "password": PW})
    assert resp.status_code == 201
    body = resp.json()
    if role is not None:
        async with AsyncSessionLocal() as db:
            await db.execute(update(Student).where(Student.id == body["user"]["id"]).values(role=role))
            await db.commit()
    return f"pc_{uid}", body


async def _pc_login(client, username, machine_key, hostname="lab-1", password=PW):
    return await client.post("/api/v1/pc/login", json={
        "username": username, "password": password,
        "hostname": hostname, "machine_key": machine_key})


async def test_login_returns_token_and_locked_state(async_client):
    username, _ = await _register(async_client)
    resp = await _pc_login(async_client, username, f"mk-{_uid()}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["token"]
    assert body["state"]["student"]["id"]
    assert body["state"]["locked"] in (True, False)
    assert body["state"]["reason"] != "no_student"


async def test_bad_password_rejected(async_client):
    username, _ = await _register(async_client)
    resp = await _pc_login(async_client, username, f"mk-{_uid()}", password="wrong-password")
    assert resp.status_code in (400, 401)


async def test_teacher_login_refused_403(async_client):
    username, _ = await _register(async_client, role=UserRole.teacher)
    resp = await _pc_login(async_client, username, f"mk-{_uid()}")
    assert resp.status_code == 403


async def test_second_login_closes_previous_session_and_reuses_device(async_client):
    username, _ = await _register(async_client)
    mk = f"mk-{_uid()}"
    key_hash = hashlib.sha256(mk.encode("utf-8")).hexdigest()
    r1 = await _pc_login(async_client, username, mk, hostname="old-name")
    r2 = await _pc_login(async_client, username, mk, hostname="new-name")
    assert r1.status_code == r2.status_code == 200
    async with AsyncSessionLocal() as db:
        devices = (await db.execute(select(PcDevice).where(PcDevice.machine_key_hash == key_hash))).scalars().all()
        assert len(devices) == 1
        assert devices[0].hostname == "new-name"
        sessions = (await db.execute(select(PcSession).where(PcSession.device_id == devices[0].id))).scalars().all()
        assert len(sessions) == 2
        assert len([s for s in sessions if s.signed_out_at is None]) == 1
    # the first token is now dead (its session is closed)
    old = await async_client.get("/api/v1/pc/state", headers={"Authorization": f"Bearer {r1.json()['token']}"})
    assert old.status_code == 401
    new = await async_client.get("/api/v1/pc/state", headers={"Authorization": f"Bearer {r2.json()['token']}"})
    assert new.status_code == 200


async def test_pc_token_rejected_on_student_api(async_client):
    username, _ = await _register(async_client)
    tok = (await _pc_login(async_client, username, f"mk-{_uid()}")).json()["token"]
    resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 401
    t = await async_client.get("/api/v1/teacher/statistics", headers={"Authorization": f"Bearer {tok}"})
    assert t.status_code in (401, 403)


async def test_student_token_rejected_on_pc_state(async_client):
    _, body = await _register(async_client)
    resp = await async_client.get(
        "/api/v1/pc/state", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert resp.status_code == 401


async def test_state_requires_token(async_client):
    assert (await async_client.get("/api/v1/pc/state")).status_code == 401


async def test_logout_closes_session(async_client):
    username, _ = await _register(async_client)
    tok = (await _pc_login(async_client, username, f"mk-{_uid()}")).json()["token"]
    h = {"Authorization": f"Bearer {tok}"}
    assert (await async_client.post("/api/v1/pc/logout", headers=h)).status_code == 200
    assert (await async_client.get("/api/v1/pc/state", headers=h)).status_code == 401


async def test_compute_state_with_open_session(async_client):
    username, body = await _register(async_client)
    tok = (await _pc_login(async_client, username, f"mk-{_uid()}")).json()["token"]
    async with AsyncSessionLocal() as db:
        sess = (await db.execute(
            select(PcSession).where(PcSession.student_id == body["user"]["id"],
                                    PcSession.signed_out_at.is_(None)))).scalars().first()
        device = await db.get(PcDevice, sess.device_id)
        st = await compute_state(db, device)
    assert st["student"]["id"] == body["user"]["id"]
    assert st["reason"] != "no_student"
    for k in ("remaining", "completed", "required"):
        assert isinstance(st[k], int)
