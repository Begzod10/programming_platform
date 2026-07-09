"""
Auth endpoint integration tests.

Covers registration, login, /me reads, and logout against the real SQLite DB.
Each test creates its own user with a UUID-suffixed username/email so tests
are fully independent and can run in any order.
"""

import uuid
import pytest
from httpx import AsyncClient


def _unique() -> str:
    return uuid.uuid4().hex[:8]


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


# ── Logout ────────────────────────────────────────────────────────────────────

async def test_logout_returns_200(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert "message" in resp.json()
