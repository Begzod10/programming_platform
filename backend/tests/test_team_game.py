"""
Integration tests for the /api/v1/game-sessions endpoints.

Covers:
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

async def test_list_sessions_requires_auth(async_client: AsyncClient):
    """GET /game-sessions with no token is rejected — this endpoint used to
    leak every session's full roster (names/usernames/avatars) with zero
    authentication; auth is now mandatory."""
    resp = await async_client.get(BASE)
    assert resp.status_code == 401


async def test_list_sessions_with_auth_returns_200(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /game-sessions with a valid student token returns 200."""
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

async def test_get_session_requires_auth(async_client: AsyncClient):
    """GET /game-sessions/{id} with no token is rejected."""
    resp = await async_client.get(f"{BASE}/99999")
    assert resp.status_code == 401


async def test_get_nonexistent_session_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /game-sessions/99999 returns 404 for an unknown session."""
    resp = await async_client.get(f"{BASE}/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_session_by_id_after_create(
    async_client: AsyncClient, teacher_headers: dict
):
    """Create a session, then retrieve it by ID as the owning teacher."""
    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.get(f"{BASE}/{session_id}", headers=teacher_headers)
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
    check = await async_client.get(f"{BASE}/{session_id}", headers=teacher_headers)
    assert check.status_code == 404


# ── Course-less session visibility (teacher's own students only) ───────────────
#
# A course-less game used to be "open to everyone" regardless of who made it —
# a student with no relationship at all to the creating teacher still saw
# (and could be auto-assigned into) that teacher's games. See
# app/services/teacher_students.py::student_teacher_ids_subquery.

async def _register_and_login(async_client: AsyncClient, prefix: str) -> tuple[int, dict]:
    uid = uuid.uuid4().hex[:8]
    username = f"{prefix}_{uid}"
    password = "testpassword123"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    user_id = reg.json()["user"]["id"]

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200, f"Login failed: {login.text}"
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return user_id, headers


async def test_courseless_session_hidden_from_unrelated_student(
    async_client: AsyncClient, teacher_headers: dict, auth_headers: dict
):
    """A student with no Group/Flow tie to the creating teacher must not see
    that teacher's course-less session in their list."""
    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.get(BASE, headers=auth_headers)
    assert resp.status_code == 200
    assert session_id not in {s["id"] for s in resp.json()}


async def test_courseless_session_visible_to_teachers_own_student(
    async_client: AsyncClient, teacher_headers: dict, db_session,
):
    """A student who IS in one of the creating teacher's own groups sees the
    course-less session — the fix must not hide it from its real audience."""
    from app.models.group import Group, student_groups
    from sqlalchemy import insert

    teacher_id = (await async_client.get("/api/v1/auth/me", headers=teacher_headers)).json()["id"]
    student_id, student_headers = await _register_and_login(async_client, "myclassstudent")

    group = Group(name=f"test-group-{uuid.uuid4().hex[:8]}", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(
        insert(student_groups).values(student_id=student_id, group_id=group.id)
    )
    await db_session.commit()

    create = await async_client.post(BASE, json=_session_payload(), headers=teacher_headers)
    assert create.status_code == 201
    session_id = create.json()["id"]

    resp = await async_client.get(BASE, headers=student_headers)
    assert resp.status_code == 200
    assert session_id in {s["id"] for s in resp.json()}
