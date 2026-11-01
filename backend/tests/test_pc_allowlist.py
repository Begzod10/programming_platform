import uuid
from contextlib import asynccontextmanager

import pytest
from sqlalchemy import delete, update
from starlette.testclient import TestClient

from app.db.database import AsyncSessionLocal
from app.main import app
from app.models.group import Group
from app.models.pc_control import PcAllowlist, PcDevice
from app.models.user import Student, UserRole
from app.services import pc_allowlist_service as svc

PW = "securepass123"
DEFAULTS = ["code.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe",
            "python.exe", "node.exe", "chrome.exe", "msedge.exe"]
URL = "/api/v1/teacher/pc/allowlist"


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
def reset_global(client):
    async def _reset():
        async with AsyncSessionLocal() as db:
            await db.execute(delete(PcAllowlist).where(PcAllowlist.group_id.is_(None)))
            await db.commit()
    client.portal.call(_reset)
    yield
    client.portal.call(_reset)


def _register(c, role=None):
    uid = _uid()
    r = c.post("/api/v1/auth/register", json={
        "username": f"pcal_{uid}", "email": f"pcal_{uid}@example.com", "password": PW})
    assert r.status_code == 201, r.text
    user_id = r.json()["user"]["id"]
    if role is not None:
        async def _flip():
            async with AsyncSessionLocal() as db:
                await db.execute(update(Student).where(Student.id == user_id).values(role=role))
                await db.commit()
        c.portal.call(_flip)
    r = c.post("/api/v1/auth/login", json={"username": f"pcal_{uid}", "password": PW})
    assert r.status_code == 200, r.text
    return user_id, f"pcal_{uid}", r.json()["access_token"]


@pytest.fixture
def teacher(client):
    tid, _, token = _register(client, UserRole.teacher)
    return tid, {"Authorization": f"Bearer {token}"}


def _group(client, teacher_id):
    async def _mk():
        async with AsyncSessionLocal() as db:
            g = Group(name=f"g_{_uid()}", teacher_id=teacher_id)
            db.add(g)
            await db.commit()
            await db.refresh(g)
            return g.id
    return client.portal.call(_mk)


def _exes(entries):
    return [e["exe"] for e in entries]


def test_defaults_when_no_row(client, teacher):
    _, h = teacher
    r = client.get(URL, headers=h)
    assert r.status_code == 200, r.text
    assert _exes(r.json()["entries"]) == DEFAULTS
    assert _exes(r.json()["effective"]) == DEFAULTS


def test_put_global_round_trips_and_lowercases(client, teacher):
    _, h = teacher
    r = client.put(URL, headers=h, json={"entries": [
        {"exe": "Code.EXE", "publisher": "Microsoft"}, {"exe": "foo.exe"}]})
    assert r.status_code == 200, r.text
    got = client.get(URL, headers=h).json()["entries"]
    assert got == [{"exe": "code.exe", "publisher": "Microsoft"}, {"exe": "foo.exe", "publisher": None}]
    # second PUT updates the same single global row
    client.put(URL, headers=h, json={"entries": [{"exe": "bar.exe"}]})

    async def _count():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select, func
            return (await db.execute(select(func.count()).select_from(PcAllowlist)
                                     .where(PcAllowlist.group_id.is_(None)))).scalar()
    assert client.portal.call(_count) == 1


def test_group_list_merges_with_global_without_duplicates(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    client.put(URL, headers=h, json={"entries": [{"exe": "a.exe"}, {"exe": "b.exe"}]})
    r = client.put(f"{URL}?group_id={gid}", headers=h, json={"entries": [{"exe": "B.exe"}, {"exe": "c.exe"}]})
    assert r.status_code == 200, r.text
    body = client.get(f"{URL}?group_id={gid}", headers=h).json()
    assert _exes(body["entries"]) == ["b.exe", "c.exe"]
    assert _exes(body["effective"]) == ["a.exe", "b.exe", "c.exe"]

    async def _eff():
        async with AsyncSessionLocal() as db:
            return await svc.effective_allowlist(db, gid)
    assert _exes(client.portal.call(_eff)) == ["a.exe", "b.exe", "c.exe"]


@pytest.mark.parametrize("entries", [[], [{"exe": "C:\\x\\a.exe"}], [{"exe": "notanexe"}],
                                     [{"exe": "a/b.exe"}], [{"exe": ""}]])
def test_invalid_lists_422_and_previous_kept(client, teacher, entries):
    _, h = teacher
    assert client.put(URL, headers=h, json={"entries": [{"exe": "keep.exe"}]}).status_code == 200
    r = client.put(URL, headers=h, json={"entries": entries})
    assert r.status_code == 422, r.text
    assert _exes(client.get(URL, headers=h).json()["entries"]) == ["keep.exe"]


def test_non_teacher_403(client):
    _, _, token = _register(client)
    h = {"Authorization": f"Bearer {token}"}
    assert client.get(URL, headers=h).status_code == 403
    assert client.put(URL, headers=h, json={"entries": [{"exe": "a.exe"}]}).status_code == 403


def test_validate_entries_unit():
    assert svc.validate_entries([{"exe": " Foo.EXE "}]) == [{"exe": "foo.exe", "publisher": None}]
    with pytest.raises(ValueError):
        svc.validate_entries([])
    with pytest.raises(ValueError):
        svc.validate_entries([{"exe": "a\\b.exe"}])


def test_put_pushes_new_allowlist_to_connected_device(client, teacher):
    _, h = teacher
    uid = _uid()
    r = client.post("/api/v1/auth/register", json={
        "username": f"pcalst_{uid}", "email": f"pcalst_{uid}@example.com", "password": PW})
    assert r.status_code == 201
    r = client.post("/api/v1/pc/login", json={
        "username": f"pcalst_{uid}", "password": PW,
        "hostname": "lab-al", "machine_key": f"mk-al-{uid}"})
    assert r.status_code == 200, r.text
    token = r.json()["token"]
    with client.websocket_connect(f"/api/v1/pc/ws?token={token}") as ws:
        first = ws.receive_json()
        assert _exes(first["allowlist"]) == DEFAULTS
        r = client.put(URL, headers=h, json={"entries": [{"exe": "pushed.exe", "publisher": "P"}]})
        assert r.status_code == 200, r.text
        frame = ws.receive_json()
        assert frame["type"] == "state"
        assert frame["allowlist"] == [{"exe": "pushed.exe", "publisher": "P"}]


def test_foreign_group_allowlist_403_and_unknown_group_404(client, teacher):
    _, h = teacher
    other_tid = _register(client, UserRole.teacher)[0]
    foreign = _group(client, other_tid)
    assert client.get(f"{URL}?group_id={foreign}", headers=h).status_code == 403
    assert client.put(f"{URL}?group_id={foreign}", headers=h,
                      json={"entries": [{"exe": "a.exe"}]}).status_code == 403
    assert client.get(f"{URL}?group_id=99999999", headers=h).status_code == 404
    assert client.put(f"{URL}?group_id=99999999", headers=h,
                      json={"entries": [{"exe": "a.exe"}]}).status_code == 404
    # the global allowlist is a platform-wide setting: any teacher may edit it
    assert client.put(URL, headers=h, json={"entries": [{"exe": "a.exe"}]}).status_code == 200
