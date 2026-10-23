import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import insert, update
from starlette.testclient import TestClient

from app.db.database import AsyncSessionLocal
from app.main import app
from app.models.daily_quota import StudentDailyProgress
from app.models.group import Group, student_groups
from app.models.pc_control import PcDevice, PcSession, PcUsageEvent
from app.models.user import Student, UserRole
from app.services.daily_quota_service import TZ

PW = "securepass123"
T = "/api/v1/teacher/pc"
D1 = date(2020, 3, 2)  # fixed historical week, far from other tests' data


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


def _register(c, role=None):
    uid = _uid()
    r = c.post("/api/v1/auth/register", json={
        "username": f"pcr_{uid}", "email": f"pcr_{uid}@example.com", "password": PW})
    assert r.status_code == 201, r.text
    user_id = r.json()["user"]["id"]
    if role is not None:
        async def _flip():
            async with AsyncSessionLocal() as db:
                await db.execute(update(Student).where(Student.id == user_id).values(role=role))
                await db.commit()
        c.portal.call(_flip)
    r = c.post("/api/v1/auth/login", json={"username": f"pcr_{uid}", "password": PW})
    assert r.status_code == 200, r.text
    return user_id, r.json()["access_token"]


@pytest.fixture
def teacher(client):
    tid, token = _register(client, UserRole.teacher)
    return tid, {"Authorization": f"Bearer {token}"}


def _at(day, hh, mm=0):
    # UTC: SQLite drops the offset of aware datetimes, so store UTC wall time.
    return datetime(day.year, day.month, day.day, hh, mm, tzinfo=TZ).astimezone(timezone.utc)


def _mk_student_session(client, events=(), group_id=None, signed_in=None):
    """Create student + device + session (+ events [(start, end, app, locked)]). Returns student_id."""
    sid, _ = _register(client)

    async def _go():
        async with AsyncSessionLocal() as db:
            dev = PcDevice(hostname=f"h-{_uid()}", machine_key_hash=_uid() + _uid())
            db.add(dev)
            await db.flush()
            first = events[0][0] if events else signed_in or _at(D1, 9)
            s = PcSession(device_id=dev.id, student_id=sid, signed_in_at=signed_in or first)
            db.add(s)
            await db.flush()
            for start, end, app_name, locked in events:
                db.add(PcUsageEvent(session_id=s.id, app_name=app_name, started_at=start,
                                    ended_at=end, was_locked=locked))
            if group_id is not None:
                await db.execute(insert(student_groups).values(student_id=sid, group_id=group_id))
            await db.commit()
    client.portal.call(_go)
    return sid


def _group(client, teacher_id):
    async def _mk():
        async with AsyncSessionLocal() as db:
            g = Group(name=f"g_{_uid()}", teacher_id=teacher_id)
            db.add(g)
            await db.commit()
            await db.refresh(g)
            return g.id
    return client.portal.call(_mk)


def _report(client, headers, frm, to, group_id=None):
    params = {"from": frm.isoformat(), "to": to.isoformat()}
    if group_id is not None:
        params["group_id"] = group_id
    return client.get(f"{T}/report", headers=headers, params=params)


def test_minutes_split_and_top_apps(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    sid = _mk_student_session(client, group_id=gid, events=[
        (_at(D1, 9, 0), _at(D1, 9, 10), "code.exe", True),
        (_at(D1, 10, 0), _at(D1, 10, 20), "chrome.exe", False),
    ])
    r = _report(client, h, D1, D1, gid)
    assert r.status_code == 200, r.text
    rows = [x for x in r.json() if x["student_id"] == sid]
    assert len(rows) == 1
    row = rows[0]
    assert row["date"] == D1.isoformat()
    assert row["minutes_locked"] == 10
    assert row["minutes_unlocked"] == 20
    assert row["quota_met"] is False and row["unlocked_at"] is None
    assert row["top_apps"] == [{"app": "chrome.exe", "minutes": 20}, {"app": "code.exe", "minutes": 10}]


def test_midnight_crossing_event_is_split(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    sid = _mk_student_session(client, group_id=gid, events=[
        (_at(D1, 23, 50), _at(D1 + timedelta(days=1), 0, 20), "code.exe", False)])
    r = _report(client, h, D1, D1 + timedelta(days=1), gid)
    assert r.status_code == 200, r.text
    by_date = {x["date"]: x for x in r.json() if x["student_id"] == sid}
    assert by_date[D1.isoformat()]["minutes_unlocked"] == 10
    assert by_date[(D1 + timedelta(days=1)).isoformat()]["minutes_unlocked"] == 20


def test_quota_from_progress_row_and_progress_only_student(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    sid, _ = _register(client)
    unlocked_at = _at(D1, 11, 0)

    async def _go():
        async with AsyncSessionLocal() as db:
            await db.execute(insert(student_groups).values(student_id=sid, group_id=gid))
            db.add(StudentDailyProgress(student_id=sid, quota_date=D1, unlocked=True,
                                        unlocked_at=unlocked_at))
            await db.commit()
    client.portal.call(_go)
    rows = [x for x in _report(client, h, D1, D1, gid).json() if x["student_id"] == sid]
    assert len(rows) == 1
    assert rows[0]["quota_met"] is True
    assert rows[0]["unlocked_at"] is not None
    assert rows[0]["minutes_locked"] == 0 and rows[0]["top_apps"] == []


def test_group_filter_excludes_other_groups(client, teacher):
    tid, h = teacher
    g1, g2 = _group(client, tid), _group(client, tid)
    ev = [(_at(D1, 9), _at(D1, 9, 5), "a.exe", False)]
    s1 = _mk_student_session(client, events=ev, group_id=g1)
    s2 = _mk_student_session(client, events=ev, group_id=g2)
    ids = {x["student_id"] for x in _report(client, h, D1, D1, g1).json()}
    assert s1 in ids and s2 not in ids


def test_top_apps_limited_to_five(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    evs = [(_at(D1, 9, i * 8), _at(D1, 9, i * 8 + i + 1), f"app{i}.exe", False) for i in range(7)]
    sid = _mk_student_session(client, group_id=gid, events=evs)
    row = next(x for x in _report(client, h, D1, D1, gid).json() if x["student_id"] == sid)
    assert [a["app"] for a in row["top_apps"]] == [f"app{i}.exe" for i in (6, 5, 4, 3, 2)]


def test_empty_range_returns_empty_list(client, teacher):
    tid, h = teacher
    gid = _group(client, tid)
    r = _report(client, h, D1, D1, gid)
    assert r.status_code == 200 and r.json() == []


def test_range_validation(client, teacher):
    _, h = teacher
    assert _report(client, h, D1, D1 - timedelta(days=1)).status_code == 422
    assert _report(client, h, D1, D1 + timedelta(days=31)).status_code == 422  # 32 days inclusive
    assert _report(client, h, D1, D1 + timedelta(days=30)).status_code == 200  # 31 days inclusive


def test_report_is_teacher_only(client):
    _, token = _register(client)
    r = _report(client, {"Authorization": f"Bearer {token}"}, D1, D1)
    assert r.status_code == 403
    assert _report(client, {}, D1, D1).status_code in (401, 403)


def test_device_token_rejected(client):
    uname_id = _uid()
    r = client.post("/api/v1/auth/register", json={
        "username": f"pcr_{uname_id}", "email": f"pcr_{uname_id}@example.com", "password": PW})
    assert r.status_code == 201
    r = client.post("/api/v1/pc/login", json={
        "username": f"pcr_{uname_id}", "password": PW, "hostname": f"lab-{uname_id}",
        "machine_key": f"mk-{uname_id}"})
    assert r.status_code == 200, r.text
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    assert _report(client, h, D1, D1).status_code in (401, 403)
