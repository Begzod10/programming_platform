"""A gennis/turon student's own name/phone edits are written to the source first
(management), username/email cannot be edited, and a failure changes nothing."""
import json
import uuid

import httpx
import pytest
from sqlalchemy import select

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import Student
from app.services import profile_sync
from app.services.profile_sync import clean_full_name, clean_phone, split_full_name
from fastapi import HTTPException


# ── pure helpers ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("993154318", "993154318"), ("+998 99 315 43 18", "993154318"), ("998993154318", "993154318"),
])
def test_clean_phone(raw, expected):
    assert clean_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "12345", "9931543189", "abc", None])
def test_bad_phone_is_a_400(raw):
    with pytest.raises(HTTPException) as e:
        clean_phone(raw)
    assert e.value.status_code == 400


def test_clean_full_name():
    assert clean_full_name("  Ali   Vali ") == "Ali Vali"
    for bad in ("", "  ", None, "x" * 256):
        with pytest.raises(HTTPException):
            clean_full_name(bad)


@pytest.mark.parametrize("full,surname,expected", [
    ("Afruzbek Abdujjaborov", "Abdujjaborov", ("Afruzbek", "Abdujjaborov")),
    ("Muhammad Ali Saparov", "Saparov", ("Muhammad Ali", "Saparov")),
    ("Muhammad Ali Saparov", None, ("Muhammad Ali", "Saparov")),
    ("Yangi Familiya", "Eski", ("Yangi", "Familiya")),
    ("Faqatism", "Eski", ("Faqatism", "Eski")),
    ("Abdujjaborov", "Abdujjaborov", ("Abdujjaborov", "Abdujjaborov")),
])
def test_split_full_name(full, surname, expected):
    assert split_full_name(full, surname) == expected


# ── the profile endpoint ─────────────────────────────────────────────────────

class Remote:
    """Stands in for management-v2's PUT /student-profile."""
    def __init__(self, status=200):
        self.status, self.calls = status, []

    def install(self, monkeypatch):
        def handler(request: httpx.Request):
            self.calls.append((str(request.url), dict(request.headers), json.loads(request.content)))
            return httpx.Response(self.status, json={"ok": self.status == 200})
        real = httpx.AsyncClient
        monkeypatch.setattr(profile_sync.httpx, "AsyncClient",
                            lambda **kw: real(transport=httpx.MockTransport(handler), **kw))


async def _student(async_client, **overrides):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"ps_{uid}", "email": f"ps_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    sid = reg.json()["user"]["id"]
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        for k, v in overrides.items():
            setattr(s, k, v)
        await db.commit()
    return sid, {"Authorization": f"Bearer {reg.json()['access_token']}"}


async def _row(sid):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(Student).where(Student.id == sid))).scalar_one()


@pytest.fixture()
def secret(monkeypatch):
    monkeypatch.setattr(settings, "STUDENT_PLATFORM_SERVICE_SECRET", "s3cret")


async def test_a_gennis_student_edit_is_written_to_the_source_then_saved(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810001, full_name="Ali Valiyev", surname="Valiyev", phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"full_name": "Alisher Valiyev", "phone": "+998 91 234 56 78"}, headers=h)
    assert r.status_code == 200, r.text
    (url, headers, body), = remote.calls
    assert url.endswith("/student-profile") and headers["x-student-platform-secret"] == "s3cret"
    assert body == {"source": "gennis", "id": 810001, "name": "Alisher", "surname": "Valiyev", "phone": "912345678"}
    row = await _row(sid)
    assert (row.full_name, row.surname, row.phone) == ("Alisher Valiyev", "Valiyev", "912345678")


async def test_a_turon_student_is_written_with_the_turon_id(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, turon_id=820001, full_name="Sarvar Ruzmatov", surname="Ruzmatov", phone="935455952")
    r = await async_client.put("/api/v1/student/me", json={"phone": "935000000"}, headers=h)
    assert r.status_code == 200, r.text
    assert remote.calls[0][2] == {"source": "turon", "id": 820001, "phone": "935000000"}


async def test_nothing_is_sent_when_nothing_changed(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810002, full_name="Ali Valiyev", surname="Valiyev", phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"full_name": "Ali  Valiyev", "phone": "90 000 00 00", "bio": "hi"}, headers=h)
    assert r.status_code == 200
    assert remote.calls == []
    assert (await _row(sid)).bio == "hi"


async def test_a_refused_write_changes_nothing_here(async_client, monkeypatch, secret):
    Remote(status=500).install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810003, full_name="Ali Valiyev", surname="Valiyev", phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"full_name": "Boshqa Ism", "phone": "911111111"}, headers=h)
    assert r.status_code == 502
    row = await _row(sid)
    assert (row.full_name, row.phone) == ("Ali Valiyev", "900000000")


async def test_an_unreachable_source_changes_nothing_here(async_client, monkeypatch, secret):
    def boom(**kw):
        raise httpx.ConnectError("down")
    class Down:
        def __init__(self, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def put(self, *a, **kw): raise httpx.ConnectError("down")
    monkeypatch.setattr(profile_sync.httpx, "AsyncClient", Down)
    sid, h = await _student(async_client, gennis_id=810004, full_name="Ali Valiyev", surname="Valiyev", phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"phone": "911111111"}, headers=h)
    assert r.status_code == 502
    assert (await _row(sid)).phone == "900000000"


async def test_an_invalid_phone_never_reaches_the_source(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810005, phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"phone": "12345"}, headers=h)
    assert r.status_code == 400
    assert remote.calls == []


async def test_username_and_email_of_a_linked_student_cannot_be_changed(async_client, monkeypatch, secret):
    Remote().install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810006)
    before = await _row(sid)
    r = await async_client.put("/api/v1/student/me", json={"username": "hacked_name", "email": "x@evil.uz"}, headers=h)
    assert r.status_code == 200
    after = await _row(sid)
    assert (after.username, after.email) == (before.username, before.email)


async def test_a_local_only_student_edits_freely_and_nothing_is_sent(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client)
    r = await async_client.put("/api/v1/student/me", json={"full_name": "Mahalliy Odam", "phone": "12345"}, headers=h)
    assert r.status_code == 200
    assert remote.calls == []
    assert (await _row(sid)).phone == "12345"


async def test_without_a_configured_secret_the_edit_is_saved_locally_only(async_client, monkeypatch):
    monkeypatch.setattr(settings, "STUDENT_PLATFORM_SERVICE_SECRET", "")
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810007, phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"phone": "911111111"}, headers=h)
    assert r.status_code == 200
    assert remote.calls == []
    assert (await _row(sid)).phone == "911111111"
