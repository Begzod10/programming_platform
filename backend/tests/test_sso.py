"""Tests for POST /api/v1/auth/sso — the classroom SSO handoff.

See docs/CLASSROOM_SSO_FOR_STUDENT_PLATFORM.md for the full contract these
tests check against. Every test gets a working SSO_SHARED_SECRET via the
autouse sso_secret fixture below; the "not configured" case explicitly
monkeypatches it back to empty.
"""
import time
import uuid

import pytest
from jose import jwt
from sqlalchemy import select

from app.config import settings
from app.models.user import Student, UserRole

ALGORITHM = "HS256"
TEST_SECRET = "test-sso-shared-secret-for-pytest-only"


def _claims(**overrides) -> dict:
    now = int(time.time())
    base = {
        "iss": "classroom",
        "aud": "student_platform",
        "sub": "gennis:999001",
        "source": "gennis",
        "ext_id": 999001,
        "username": "sso_test_student",
        "name": "Anora",
        "surname": "Qodirova",
        "role": "student",
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + 90,
    }
    base.update(overrides)
    return base


def _token(secret: str = TEST_SECRET, **overrides) -> str:
    return jwt.encode(_claims(**overrides), secret, algorithm=ALGORITHM)


@pytest.fixture(autouse=True)
def sso_secret(monkeypatch):
    monkeypatch.setattr(settings, "SSO_SHARED_SECRET", TEST_SECRET)
    yield


async def test_new_student_creates_account_and_fills_source_id(async_client, db_session):
    ext_id = 900001
    token = _token(ext_id=ext_id, sub=f"gennis:{ext_id}")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["role"] == "student"
    assert body["access_token"]

    result = await db_session.execute(select(Student).where(Student.gennis_id == ext_id))
    user = result.scalar_one()
    assert user.username == f"gennis_{ext_id}"


async def test_second_sso_login_reuses_same_account(async_client):
    ext_id = 900002
    resp1 = await async_client.post(
        "/api/v1/auth/sso", json={"token": _token(ext_id=ext_id, sub=f"gennis:{ext_id}")}
    )
    assert resp1.status_code == 200
    user_id_1 = resp1.json()["user"]["id"]

    resp2 = await async_client.post(
        "/api/v1/auth/sso", json={"token": _token(ext_id=ext_id, sub=f"gennis:{ext_id}")}
    )
    assert resp2.status_code == 200
    assert resp2.json()["user"]["id"] == user_id_1


async def test_password_account_then_sso_links_to_same_account(async_client, db_session):
    """A person who registered/logged in locally before ever touching SSO
    must land on their existing row, not a fresh duplicate — see the doc's
    checklist item on this exact scenario."""
    ext_id = 900003
    username = f"gennis_{ext_id}"
    existing = Student(
        username=username,
        email=f"{username}@gennis.uz",
        hashed_password="x",
        role=UserRole.student,
        is_active=True,
    )
    db_session.add(existing)
    await db_session.commit()
    await db_session.refresh(existing)

    token = _token(ext_id=ext_id, sub=f"gennis:{ext_id}", username=username)
    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 200
    assert resp.json()["user"]["id"] == existing.id

    await db_session.refresh(existing)
    assert existing.gennis_id == ext_id


async def test_gennis_and_turon_same_numeric_id_are_different_accounts(async_client):
    shared_id = 55555
    gennis_resp = await async_client.post(
        "/api/v1/auth/sso",
        json={"token": _token(ext_id=shared_id, source="gennis", sub=f"gennis:{shared_id}")},
    )
    turon_resp = await async_client.post(
        "/api/v1/auth/sso",
        json={"token": _token(ext_id=shared_id, source="turon", sub=f"turon:{shared_id}")},
    )

    assert gennis_resp.status_code == 200
    assert turon_resp.status_code == 200
    assert gennis_resp.json()["user"]["id"] != turon_resp.json()["user"]["id"]


async def test_expired_token_is_rejected(async_client):
    now = int(time.time())
    token = _token(ext_id=900004, sub="gennis:900004", iat=now - 200, exp=now - 110)

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_token_cannot_be_reused(async_client):
    token = _token(ext_id=900005, sub="gennis:900005")

    first = await async_client.post("/api/v1/auth/sso", json={"token": token})
    second = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert first.status_code == 200
    assert second.status_code == 401


async def test_wrong_audience_is_rejected(async_client):
    token = _token(ext_id=900006, sub="gennis:900006", aud="some-other-service")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_wrong_issuer_is_rejected(async_client):
    token = _token(ext_id=900007, sub="gennis:900007", iss="not-classroom")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_unknown_source_is_rejected(async_client):
    token = _token(ext_id=900008, sub="unknown:900008", source="unknown")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_missing_jti_is_rejected(async_client):
    token = _token(ext_id=900008, sub="gennis:900008", jti="")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_non_integer_ext_id_is_rejected(async_client):
    token = _token(ext_id="not-a-number", sub="gennis:x")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_wrong_shared_secret_is_rejected(async_client):
    token = _token(secret="a-completely-different-secret", ext_id=900009, sub="gennis:900009")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 401


async def test_disabled_secret_returns_503(async_client, monkeypatch):
    monkeypatch.setattr(settings, "SSO_SHARED_SECRET", "")
    token = _token(ext_id=900010, sub="gennis:900010")

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 503


async def test_short_token_rejected_with_422(async_client):
    resp = await async_client.post("/api/v1/auth/sso", json={"token": "short"})

    assert resp.status_code == 422


async def test_missing_token_field_rejected_with_422(async_client):
    resp = await async_client.post("/api/v1/auth/sso", json={})

    assert resp.status_code == 422


async def test_inactive_account_is_forbidden(async_client, db_session):
    ext_id = 900011
    inactive = Student(
        username=f"gennis_{ext_id}",
        email=f"gennis_{ext_id}@gennis.uz",
        hashed_password="x",
        role=UserRole.student,
        is_active=False,
        gennis_id=ext_id,
    )
    db_session.add(inactive)
    await db_session.commit()

    token = _token(ext_id=ext_id, sub=f"gennis:{ext_id}")
    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 403


async def test_teacher_role_creates_teacher_account(async_client, db_session):
    ext_id = 900012
    token = _token(
        ext_id=ext_id, sub=f"gennis:{ext_id}", role="teacher", username="teacher_uname"
    )

    resp = await async_client.post("/api/v1/auth/sso", json={"token": token})

    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "teacher"

    result = await db_session.execute(select(Student).where(Student.gennis_id == ext_id))
    user = result.scalar_one()
    # Teachers keep the token's own username (not the source_id convention
    # students get) — see the doc's "Yangi hisob maydonlari" table.
    assert user.username == "teacher_uname"
