"""
Integration tests for the /api/v1/game-sessions endpoints.

Covers:
- Public list access (no auth)
- Auth requirements (401 without token, 403 for wrong role)
- Creating sessions as a teacher
- Validation errors (422) for bad input
- Retrieving and deleting sessions
- Non-existent session returns 404
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import update

BASE = "/api/v1/game-sessions"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _session_payload(**overrides) -> dict:
    """Return a minimal valid GameSessionCreate payload."""
    defaults = {
        "title": "Integration Test Session",
        "game_type": "team",
        "team_count": 2,
    }
    return {**defaults, **overrides}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def teacher_headers(async_client: AsyncClient, db_session) -> dict:
    """Register a fresh user and promote them to the teacher role.

    The /register endpoint always creates students, so we update the role
    directly in the DB after registration and re-log in to get a valid token.
    """
    from app.models.user import Student, UserRole

    uid = uuid.uuid4().hex[:8]
    username = f"teacher_{uid}"
    email = f"teacher_{uid}@example.com"
    password = "teacherpass123"

    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201, f"Teacher register failed: {reg.text}"
    user_id = reg.json()["user"]["id"]

    # Elevate role to teacher in the shared SQLite DB
    await db_session.execute(
        update(Student).where(Student.id == user_id).values(role=UserRole.teacher)
    )
    await db_session.commit()

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login.status_code == 200, f"Teacher login failed: {login.text}"
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── List sessions ─────────────────────────────────────────────────────────────

async def test_list_sessions_public_returns_200(async_client: AsyncClient):
    """GET /game-sessions is publicly accessible and returns a JSON list."""
    resp = await async_client.get(BASE)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_list_sessions_with_auth_returns_200(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /game-sessions with student token also returns 200 (optional auth)."""
    resp = await async_client.get(BASE, headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── Create session ────────────────────────────────────────────────────────────

async def test_create_session_without_auth_returns_401(async_client: AsyncClient):
    """POST /game-sessions requires authentication."""
    resp = await async_client.post(BASE, json=_session_payload())
    assert resp.status_code == 401


async def test_create_session_student_role_returns_403(
    async_client: AsyncClient, auth_headers: dict
):
    """POST /game-sessions with a student token returns 403 (teacher role required)."""
    resp = await async_client.post(BASE, json=_session_payload(), headers=auth_headers)
    assert resp.status_code == 403


async def test_create_session_as_teacher_returns_201(
    async_client: AsyncClient, teacher_headers: dict
):
    """Teacher successfully creates a session — returns 201 with session data."""
    resp = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Integration Test Session"
    assert data["status"] == "pending"
    assert data["game_type"] == "team"
    assert "id" in data
    assert "teams" in data


async def test_created_session_teams_match_team_count(
    async_client: AsyncClient, teacher_headers: dict
):
    """The number of teams created equals the requested team_count."""
    resp = await async_client.post(
        BASE,
        json=_session_payload(title="Team Count Test", team_count=3),
        headers=teacher_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["team_count"] == 3
    assert len(data["teams"]) == 3


# ── Validation errors ─────────────────────────────────────────────────────────

async def test_create_session_title_too_short_returns_422(
    async_client: AsyncClient, teacher_headers: dict
):
    """title with 1 character violates min_length=2 → 422."""
    resp = await async_client.post(
        BASE,
        json=_session_payload(title="X"),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_create_session_team_count_below_minimum_returns_422(
    async_client: AsyncClient, teacher_headers: dict
):
    """team_count=1 violates ge=2 constraint → 422."""
    resp = await async_client.post(
        BASE,
        json=_session_payload(team_count=1),
        headers=teacher_headers,
    )
    assert resp.status_code == 422


async def test_create_session_missing_game_type_returns_422(
    async_client: AsyncClient, teacher_headers: dict
):
    """Omitting the required game_type field returns 422."""
    resp = await async_client.post(
        BASE,
        json={"title": "No Type", "team_count": 2},
        headers=teacher_headers,
    )
    assert resp.status_code == 422


# ── Get single session ────────────────────────────────────────────────────────

async def test_get_nonexistent_session_returns_404(async_client: AsyncClient):
    """GET /game-sessions/99999 returns 404 for an unknown session."""
    resp = await async_client.get(f"{BASE}/99999")
    assert resp.status_code == 404


async def test_get_session_by_id_after_create(
    async_client: AsyncClient, teacher_headers: dict
):
    """Create a session, then retrieve it by ID."""
    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.get(f"{BASE}/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert data["title"] == "Integration Test Session"


# ── Delete session ────────────────────────────────────────────────────────────

async def test_delete_session_student_role_returns_403(
    async_client: AsyncClient, auth_headers: dict, teacher_headers: dict
):
    """A student cannot delete a teacher's session — returns 403."""
    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.delete(f"{BASE}/{session_id}", headers=auth_headers)
    assert resp.status_code == 403


async def test_delete_session_as_creator_returns_204(
    async_client: AsyncClient, teacher_headers: dict
):
    """Teacher can delete their own session — returns 204 No Content."""
    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.delete(f"{BASE}/{session_id}", headers=teacher_headers)
    assert resp.status_code == 204

    # Confirm it is gone
    check = await async_client.get(f"{BASE}/{session_id}")
    assert check.status_code == 404
