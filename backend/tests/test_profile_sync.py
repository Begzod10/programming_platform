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
from app.services.profile_sync import clean_phone
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


# ── the profile endpoint ─────────────────────────────────────────────────────

class Remote:
    """Stands in for management-v2's PUT /student-profile."""
    def __init__(self, status=200, writes=True):
        self.status, self.calls, self.writes = status, [], writes

    def install(self, monkeypatch):
        def handler(request: httpx.Request):
            self.calls.append((str(request.url), dict(request.headers), json.loads(request.content)))
            body = json.loads(request.content)
            written = [k for k in ("name", "surname", "phone", "password") if k in body] if self.writes else []
            return httpx.Response(self.status, json={"ok": self.status == 200, "written": written})
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


async def test_a_gennis_students_phone_is_written_to_the_source_then_saved(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810001, full_name="Ali Valiyev", surname="Valiyev", phone="900000000")
    r = await async_client.put("/api/v1/student/me", json={"phone": "+998 91 234 56 78"}, headers=h)
    assert r.status_code == 200, r.text
    (url, headers, body), = remote.calls
    assert url.endswith("/student-profile") and headers["x-student-platform-secret"] == "s3cret"
    assert body == {"source": "gennis", "id": 810001, "phone": "912345678"}
    assert (await _row(sid)).phone == "912345678"


async def test_name_and_photo_of_a_linked_student_cannot_be_edited(async_client, monkeypatch, secret):
    """They come from turon-v2 / gennis-v2; every login restores them."""
    remote = Remote(); remote.install(monkeypatch)
    sid, h = await _student(async_client, gennis_id=810008, full_name="Ali Valiyev", surname="Valiyev",
                            avatar_url="https://admin.tisedu.uz/static/profile_photos/a.jpg")
    r = await async_client.put("/api/v1/student/me", json={
        "full_name": "Boshqa Ism", "avatar_url": "/uploads/avatars/mine.jpg", "bio": "salom"}, headers=h)
    assert r.status_code == 200, r.text
    row = await _row(sid)
    assert (row.full_name, row.surname) == ("Ali Valiyev", "Valiyev")
    assert row.avatar_url == "https://admin.tisedu.uz/static/profile_photos/a.jpg"
    assert row.bio == "salom"              # the rest stays editable
    assert remote.calls == []              # and nothing about the name reaches the source


async def test_a_linked_student_cannot_upload_or_delete_a_photo(async_client):
    sid, h = await _student(async_client, turon_id=820002, avatar_url="https://admin.tisedu.uz/static/profile_photos/a.jpg")
    up = await async_client.patch("/api/v1/student/me/avatar", files={"file": ("a.png", b"\x89PNG\r\n", "image/png")}, headers=h)
    assert up.status_code == 403
    assert (await async_client.delete("/api/v1/student/me/avatar", headers=h)).status_code == 403
    assert (await _row(sid)).avatar_url == "https://admin.tisedu.uz/static/profile_photos/a.jpg"


async def test_the_profile_tells_the_client_when_name_and_photo_are_read_only(async_client):
    _, linked = await _student(async_client, gennis_id=810009)
    _, local = await _student(async_client)
    assert (await async_client.get("/api/v1/student/me", headers=linked)).json()["identity_managed"] is True
    assert (await async_client.get("/api/v1/student/me", headers=local)).json()["identity_managed"] is False


async def test_a_local_only_student_still_edits_their_own_name(async_client):
    sid, h = await _student(async_client)
    r = await async_client.put("/api/v1/student/me", json={"full_name": "Yangi Ism"}, headers=h)
    assert r.status_code == 200
    assert (await _row(sid)).full_name == "Yangi Ism"


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
    r = await async_client.put("/api/v1/student/me", json={"phone": "911111111"}, headers=h)
    assert r.status_code == 502
    assert (await _row(sid)).phone == "900000000"


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


# ── password ─────────────────────────────────────────────────────────────────

def _fake_login(monkeypatch, ok):
    from app.services.gennis_service import GennisService

    async def login(username, password):
        return {"user": {"id": 1}} if ok(password) else None
    monkeypatch.setattr(GennisService, "login", staticmethod(login))


async def test_a_linked_students_password_is_checked_and_written_at_the_source(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    _fake_login(monkeypatch, lambda p: p == "oldpass123")
    sid, h = await _student(async_client, gennis_id=810010)
    before = (await _row(sid)).hashed_password
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "oldpass123", "new_password": "newpass456"}, headers=h)
    assert r.status_code == 200, r.text
    (url, headers, body), = remote.calls
    assert body == {"source": "gennis", "id": 810010, "password": "newpass456"}
    assert (await _row(sid)).hashed_password == before        # the local copy is only a placeholder


async def test_a_wrong_current_password_sends_nothing(async_client, monkeypatch, secret):
    remote = Remote(); remote.install(monkeypatch)
    _fake_login(monkeypatch, lambda p: p == "oldpass123")
    _, h = await _student(async_client, turon_id=820010)
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "nope12345", "new_password": "newpass456"}, headers=h)
    assert r.status_code == 400 and remote.calls == []


async def test_a_refused_password_write_is_an_error_not_a_silent_success(async_client, monkeypatch, secret):
    Remote(status=500).install(monkeypatch)
    _fake_login(monkeypatch, lambda p: True)
    _, h = await _student(async_client, gennis_id=810011)
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "oldpass123", "new_password": "newpass456"}, headers=h)
    assert r.status_code == 502


async def test_without_the_service_secret_a_linked_password_change_fails_loudly(async_client, monkeypatch):
    monkeypatch.setattr(settings, "STUDENT_PLATFORM_SERVICE_SECRET", "")
    _fake_login(monkeypatch, lambda p: True)
    _, h = await _student(async_client, gennis_id=810012)
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "oldpass123", "new_password": "newpass456"}, headers=h)
    assert r.status_code == 502


async def test_a_local_student_still_changes_the_local_password(async_client):
    _, h = await _student(async_client)
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "securepass123", "new_password": "another789"}, headers=h)
    assert r.status_code == 200


async def test_an_old_management_that_ignores_the_password_is_not_reported_as_success(async_client, monkeypatch, secret):
    Remote(writes=False).install(monkeypatch)
    _fake_login(monkeypatch, lambda p: True)
    _, h = await _student(async_client, gennis_id=810013)
    r = await async_client.put("/api/v1/student/me/password",
                               json={"current_password": "oldpass123", "new_password": "newpass456"}, headers=h)
    assert r.status_code == 502
