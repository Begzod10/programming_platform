"""
Regression tests for project like dedup (Task 2.6).

Before this fix, `ProjectService.like_project` did a bare
`likes_count += 1` with no per-student dedup — only self-likes were
blocked, so the same other student could like a project unlimited times
and inflate `likes_count` arbitrarily. `ProjectLike` (unique on
(student_id, project_id)) is the real dedup mechanism now; `likes_count`
is recomputed from it on every like/unlike rather than incremented in
place.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select

from app.models.project import ProjectLike


@pytest_asyncio.fixture
async def make_student(async_client: AsyncClient):
    """Factory fixture: register+login a fresh student, return (id, headers)."""

    async def _make():
        uid = uuid.uuid4().hex[:8]
        username = f"likeuser_{uid}"
        email = f"likeuser_{uid}@example.com"
        password = "securepass123"

        reg = await async_client.post(
            "/api/v1/auth/register",
            json={"username": username, "email": email, "password": password},
        )
        assert reg.status_code == 201, f"Register failed: {reg.text}"
        student_id = reg.json()["user"]["id"]

        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        return student_id, headers

    return _make


async def _create_project(async_client: AsyncClient, headers: dict) -> int:
    resp = await async_client.post(
        "/api/v1/project/",
        json={
            "title": "Test loyiha",
            "description": "Test tavsif",
            "github_url": "https://github.com/example/repo",
            "difficulty_level": "Easy",
        },
        headers=headers,
    )
    assert resp.status_code == 201, f"Project create failed: {resp.text}"
    return resp.json()["id"]


# ── Basic like flow ───────────────────────────────────────────────────────


async def test_like_creates_row_and_bumps_count(async_client, make_student, db_session):
    owner_id, owner_headers = await make_student()
    liker_id, liker_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    resp = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["likes_count"] == 1

    rows = (
        await db_session.execute(
            select(ProjectLike).where(
                ProjectLike.project_id == project_id,
                ProjectLike.student_id == liker_id,
            )
        )
    ).scalars().all()
    assert len(rows) == 1


async def test_same_student_liking_twice_does_not_double_count(
    async_client, make_student, db_session
):
    owner_id, owner_headers = await make_student()
    liker_id, liker_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    first = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert first.status_code == 200
    assert first.json()["likes_count"] == 1

    # Repeat like from the SAME student — must not 500, must not create a
    # second row, must not bump likes_count again.
    second = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert second.status_code == 200, second.text
    assert second.json()["likes_count"] == 1

    third = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert third.status_code == 200
    assert third.json()["likes_count"] == 1

    rows = (
        await db_session.execute(
            select(ProjectLike).where(
                ProjectLike.project_id == project_id,
                ProjectLike.student_id == liker_id,
            )
        )
    ).scalars().all()
    assert len(rows) == 1


async def test_two_different_students_both_count(async_client, make_student):
    owner_id, owner_headers = await make_student()
    liker1_id, liker1_headers = await make_student()
    liker2_id, liker2_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    resp1 = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker1_headers
    )
    assert resp1.status_code == 200
    assert resp1.json()["likes_count"] == 1

    resp2 = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker2_headers
    )
    assert resp2.status_code == 200
    assert resp2.json()["likes_count"] == 2


async def test_self_like_still_blocked(async_client, make_student):
    owner_id, owner_headers = await make_student()
    project_id = await _create_project(async_client, owner_headers)

    resp = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=owner_headers
    )
    assert resp.status_code == 400
    assert "O'z loyihangizga" in resp.json()["error"]["message"]


# ── Unlike flow ────────────────────────────────────────────────────────────


async def test_unlike_removes_row_and_decrements_count(
    async_client, make_student, db_session
):
    owner_id, owner_headers = await make_student()
    liker_id, liker_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    like_resp = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert like_resp.json()["likes_count"] == 1

    unlike_resp = await async_client.request(
        "DELETE", f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert unlike_resp.status_code == 200, unlike_resp.text
    assert unlike_resp.json()["likes_count"] == 0

    rows = (
        await db_session.execute(
            select(ProjectLike).where(
                ProjectLike.project_id == project_id,
                ProjectLike.student_id == liker_id,
            )
        )
    ).scalars().all()
    assert len(rows) == 0


async def test_unliking_never_liked_project_is_a_clean_noop(async_client, make_student):
    owner_id, owner_headers = await make_student()
    liker_id, liker_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    resp = await async_client.request(
        "DELETE", f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["likes_count"] == 0


async def test_unlike_then_relike_works(async_client, make_student):
    owner_id, owner_headers = await make_student()
    liker_id, liker_headers = await make_student()

    project_id = await _create_project(async_client, owner_headers)

    await async_client.post(f"/api/v1/project/{project_id}/like", headers=liker_headers)
    await async_client.request(
        "DELETE", f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    resp = await async_client.post(
        f"/api/v1/project/{project_id}/like", headers=liker_headers
    )
    assert resp.status_code == 200
    assert resp.json()["likes_count"] == 1
