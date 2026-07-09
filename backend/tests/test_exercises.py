"""
Integration tests for the /api/v1/courses/{course_id}/lessons/{lesson_id}/exercises endpoints.

Full path pattern: /api/v1/courses/{course_id}/lessons/{lesson_id}/exercises/...

Covers:
- GET exercises is public (no auth required)
- Unknown lesson_id returns an empty list (not 404)
- Single-exercise lookup returns 404 for unknown IDs
- submit and my-submissions require authentication
- Course progress requires authentication
"""

import pytest
from httpx import AsyncClient

# Placeholder IDs that don't exist in the test DB
COURSE_ID = 99999
LESSON_ID = 99999
EXERCISE_ID = 99999

BASE = f"/api/v1/courses/{COURSE_ID}/lessons"


# ── GET exercises list ────────────────────────────────────────────────────────

async def test_get_exercises_no_auth_returns_200(async_client: AsyncClient):
    """GET exercises is publicly accessible — no auth header needed."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200


async def test_get_exercises_unknown_lesson_returns_empty_list(async_client: AsyncClient):
    """GET exercises for a non-existent lesson returns 200 with an empty list."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_exercises_response_is_list(async_client: AsyncClient):
    """GET exercises always returns a JSON array."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── GET single exercise ───────────────────────────────────────────────────────

async def test_get_single_exercise_not_found_returns_404(async_client: AsyncClient):
    """GET a specific exercise that doesn't exist returns 404."""
    resp = await async_client.get(f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}")
    assert resp.status_code == 404


# ── POST submit exercise ──────────────────────────────────────────────────────

async def test_submit_exercise_requires_auth_returns_401(async_client: AsyncClient):
    """POST to /submit without a token returns 401."""
    resp = await async_client.post(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/submit",
        json={"student_answer": "my answer"},
    )
    assert resp.status_code == 401


async def test_submit_exercise_unknown_exercise_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """POST to /submit for a non-existent exercise returns 404."""
    resp = await async_client.post(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/submit",
        json={"student_answer": "my answer"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── GET my-submissions ────────────────────────────────────────────────────────

async def test_get_my_submissions_requires_auth_returns_401(async_client: AsyncClient):
    """GET my-submissions without a token returns 401."""
    resp = await async_client.get(
        f"{BASE}/{LESSON_ID}/exercises/{EXERCISE_ID}/my-submissions"
    )
    assert resp.status_code == 401


# ── GET course progress ───────────────────────────────────────────────────────

async def test_get_course_progress_requires_auth_returns_401(async_client: AsyncClient):
    """GET exercises/progress without a token returns 401."""
    resp = await async_client.get(
        f"{BASE}/{LESSON_ID}/exercises/progress"
    )
    assert resp.status_code == 401
