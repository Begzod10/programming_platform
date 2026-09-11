"""
Auth endpoint integration tests.

Covers registration, login, /me reads, and logout against the real SQLite DB.
Each test creates its own user with a UUID-suffixed username/email so tests
are fully independent and can run in any order.
"""

import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.models.user import Student, UserRole


def _unique() -> str:
    return uuid.uuid4().hex[:8]


def _birth_date_for_age(age: int) -> date:
    """A birth_date that makes the age-from-birth_date arithmetic
    (early_learning.py's _age_from_birth_date and schemas/user.py's
    _early_learning_eligible use the same formula) resolve to exactly
    `age` today, regardless of what day this test runs on. Pinning the
    month/day to January 1st means "has the birthday happened yet this
    year" is always true, so the result is just today.year - birth_year —
    no boundary case to dodge."""
    return date(date.today().year - age, 1, 1)


# ── Registration ──────────────────────────────────────────────────────────────

async def test_register_returns_201_and_access_token(async_client: AsyncClient):
    uid = _unique()
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_{uid}",
            "email": f"user_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert "user" in body
    assert body["user"]["username"] == f"user_{uid}"


async def test_register_returns_user_with_student_role(async_client: AsyncClient):
    uid = _unique()
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"roletest_{uid}",
            "email": f"roletest_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["user"]["role"] == "student"


async def test_register_duplicate_email_returns_400(async_client: AsyncClient):
    uid = _unique()
    payload = {
        "username": f"firstuser_{uid}",
        "email": f"shared_{uid}@example.com",
        "password": "securepass123",
    }
    first = await async_client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await async_client.post(
        "/api/v1/auth/register",
        json={**payload, "username": f"seconduser_{uid}"},
    )
    assert second.status_code == 400
    # Custom exception handler wraps errors as {"success": false, "error": {"message": ...}}
    body = second.json()
    assert body.get("success") is False
    assert "email" in body["error"]["message"].lower()


async def test_register_duplicate_username_returns_400(async_client: AsyncClient):
    uid = _unique()
    shared_username = f"sharedname_{uid}"
    first = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": shared_username,
            "email": f"first_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert first.status_code == 201

    second = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": shared_username,
            "email": f"second_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert second.status_code == 400
    body = second.json()
    assert body.get("success") is False
    assert "username" in body["error"]["message"].lower()


async def test_register_short_password_returns_422(async_client: AsyncClient):
    uid = _unique()
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_{uid}",
            "email": f"user_{uid}@example.com",
            "password": "short",  # < 8 characters
        },
    )
    assert resp.status_code == 422


async def test_register_short_username_returns_422(async_client: AsyncClient):
    uid = _unique()
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "ab",  # < 3 characters
            "email": f"user_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_valid_credentials_returns_200_and_token(async_client: AsyncClient):
    uid = _unique()
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"logintest_{uid}",
            "email": f"logintest_{uid}@example.com",
            "password": "mypassword99",
        },
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": f"logintest_{uid}", "password": "mypassword99"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(async_client: AsyncClient):
    uid = _unique()
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"wrongpw_{uid}",
            "email": f"wrongpw_{uid}@example.com",
            "password": "correctpassword123",
        },
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": f"wrongpw_{uid}", "password": "WRONGPASSWORD"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user_returns_401(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "nobody_xyz_12345678", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_login_by_email_returns_200(async_client: AsyncClient):
    uid = _unique()
    email = f"emaillogin_{uid}@example.com"
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"emaillogin_{uid}",
            "email": email,
            "password": "mypassword99",
        },
    )
    # Login using email in the username field (the app supports this)
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": email, "password": "mypassword99"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


# ── Synced (gennis/turon) student login — real username, not synthetic ────────
# See gennis_service.py's GennisService docstring / reference_student_platform_
# synced_usernames.md: this used to always mint a `{source}_{ext_id}`
# placeholder for a synced STUDENT (teachers already got their real typed
# username). Fixed to match teachers: use the credential the person actually
# authenticated with, since the `stmt` lookup in auth_service.login already
# guarantees no existing row owns it by the time a new Student is created.

def _mgmt_login_payload(ext_id: int, name: str, surname: str, source: str = "turon") -> dict:
    """Shape of a successful management-v2 shim /login response for a
    student with no groups/flows (keeps sync_student_data a no-op so these
    tests only exercise username resolution, not roster sync)."""
    return {
        "access_token": "tok",
        "source": source,
        "user": {
            "id": ext_id,
            "name": name,
            "surname": surname,
            "role": "student",
            "phone": [],
            "student": {"group": [], "flow": [], "combined_debt": 0},
        },
    }


async def test_synced_student_gets_real_typed_username_not_synthetic(
    async_client: AsyncClient, db_session, monkeypatch
):
    from unittest.mock import AsyncMock
    from sqlalchemy import select
    from app.services.gennis_service import GennisService

    ext_id = 900001
    typed_username = "real_turon_login_name"
    monkeypatch.setattr(
        GennisService, "login",
        AsyncMock(return_value=_mgmt_login_payload(ext_id, "Sync", "Student")),
    )

    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": typed_username, "password": "whatever"},
    )
    assert resp.status_code == 200

    db_session.expire_all()  # request committed through its own session
    student = (
        await db_session.execute(select(Student).where(Student.turon_id == ext_id))
    ).scalar_one()
    assert student.username == typed_username
    assert student.username != f"turon_{ext_id}"


async def test_synced_student_username_upgrades_from_synthetic_on_relogin(
    async_client: AsyncClient, db_session, monkeypatch
):
    """An account synced before this fix (or before management-v2 could
    resolve a username for it) still carries its old `turon_<id>` username —
    the next successful login converges it onto the real one, same as a
    teacher's already did."""
    from unittest.mock import AsyncMock
    from sqlalchemy import select
    from app.core.security import get_password_hash
    from app.services.gennis_service import GennisService

    ext_id = 900002
    legacy_username = f"turon_{ext_id}"
    pre_existing = Student(
        username=legacy_username,
        email=f"{legacy_username}@turon.uz",
        full_name="Old Synthetic",
        hashed_password=get_password_hash("irrelevant"),
        role=UserRole.student,
        turon_id=ext_id,
    )
    db_session.add(pre_existing)
    await db_session.commit()

    real_username = "upgraded_real_name"
    monkeypatch.setattr(
        GennisService, "login",
        AsyncMock(return_value=_mgmt_login_payload(ext_id, "Sync", "Student")),
    )

    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": real_username, "password": "whatever"},
    )
    assert resp.status_code == 200

    # The login endpoint commits through its OWN dependency-injected session
    # (app.dependencies.get_db), not db_session — expire_all() before
    # re-querying so this doesn't just hand back db_session's stale
    # identity-mapped copy of pre_existing from before the request.
    db_session.expire_all()
    student = (
        await db_session.execute(select(Student).where(Student.turon_id == ext_id))
    ).scalar_one()
    assert student.username == real_username
    assert student.id == pre_existing.id  # same account, not a duplicate


# ── /me ───────────────────────────────────────────────────────────────────────

async def test_get_me_with_valid_token_returns_user_data(
    async_client: AsyncClient, auth_headers: dict
):
    resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert "username" in body
    assert "email" in body
    assert body["role"] == "student"


async def test_get_me_without_token_returns_401(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


# ── early_learning_eligible ─────────────────────────────────────────────────
# Drives whether the "Kichkinalar uchun" sidebar link shows at all — see
# schemas/user.py's _early_learning_eligible. A blanket age<11 cutoff,
# distinct from early_learning.py's own per-module _is_age_eligible.

async def test_early_learning_eligible_defaults_true_with_no_birth_date(
    async_client: AsyncClient, auth_headers: dict
):
    # Most accounts have no synced birth_date at all — unknown must stay
    # permissive, or the link would vanish for the majority of students who
    # simply haven't had this field synced yet, not because they're 11+.
    resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["early_learning_eligible"] is True


async def test_early_learning_eligible_true_under_11(
    async_client: AsyncClient, db_session, auth_headers: dict
):
    me = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me.json()["id"]
    await db_session.execute(
        update(Student).where(Student.id == user_id).values(birth_date=_birth_date_for_age(8))
    )
    await db_session.commit()

    resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["early_learning_eligible"] is True


async def test_early_learning_eligible_false_at_11_and_over(
    async_client: AsyncClient, db_session, auth_headers: dict
):
    me = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me.json()["id"]
    await db_session.execute(
        update(Student).where(Student.id == user_id).values(birth_date=_birth_date_for_age(11))
    )
    await db_session.commit()

    resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["early_learning_eligible"] is False


# ── Logout ────────────────────────────────────────────────────────────────────

async def test_logout_returns_200(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert "message" in resp.json()
