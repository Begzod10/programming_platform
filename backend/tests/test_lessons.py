"""
Integration tests for course and lesson endpoints.

Verifies:
- Courses list is publicly accessible.
- Unknown course returns 404.
- Lessons list uses optional auth: open without auth, 403 when auth'd but not enrolled.
- Lesson completion endpoint requires auth.
- Lesson completion returns 404 for a non-existent lesson.
- is-completed requires auth.
- Course progress returns zero totals for unauthenticated callers.
"""

import pytest
from httpx import AsyncClient


# ── Courses ───────────────────────────────────────────────────────────────────


async def test_get_courses_returns_200_without_auth(async_client: AsyncClient):
    """GET /api/v1/courses/ is public and returns a list."""
    resp = await async_client.get("/api/v1/courses/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_courses_accepts_pagination_params(async_client: AsyncClient):
    """GET /api/v1/courses/?skip=0&limit=5 returns 200 with a list."""
    resp = await async_client.get("/api/v1/courses/?skip=0&limit=5")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_courses_with_category_filter_returns_200(async_client: AsyncClient):
    """GET /api/v1/courses/?category_id=99999 returns 200 with empty list (no match)."""
    resp = await async_client.get("/api/v1/courses/?category_id=99999")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_course_unknown_id_returns_404(async_client: AsyncClient):
    """GET /api/v1/courses/{id} returns 404 for a non-existent course."""
    resp = await async_client.get("/api/v1/courses/99999")
    assert resp.status_code == 404


async def test_get_course_detail_has_expected_structure(async_client: AsyncClient):
    """GET /api/v1/courses/ response items are dicts (schema sanity check)."""
    resp = await async_client.get("/api/v1/courses/")
    assert resp.status_code == 200
    # With an empty DB the list is empty; either way the response must be a list.
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert isinstance(item, dict)


# ── Lessons ───────────────────────────────────────────────────────────────────


async def test_get_lessons_without_auth_returns_200(async_client: AsyncClient):
    """GET /api/v1/courses/{id}/lessons uses optional auth.

    Without a token the enrollment gate is skipped and the endpoint returns
    200 with an empty list for an unknown course.
    """
    resp = await async_client.get("/api/v1/courses/99999/lessons")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_lessons_authenticated_not_enrolled_returns_403(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /api/v1/courses/{id}/lessons with auth but not enrolled returns 403."""
    resp = await async_client.get("/api/v1/courses/99999/lessons", headers=auth_headers)
    assert resp.status_code == 403


async def test_complete_lesson_requires_auth_returns_401(async_client: AsyncClient):
    """POST /api/v1/lessons/{id}/complete without a token returns 401."""
    resp = await async_client.post("/api/v1/lessons/99999/complete")
    assert resp.status_code == 401


async def test_complete_lesson_with_auth_unknown_lesson_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """POST /api/v1/lessons/{id}/complete with valid auth but unknown lesson returns 404."""
    resp = await async_client.post("/api/v1/lessons/99999/complete", headers=auth_headers)
    assert resp.status_code == 404


async def test_is_lesson_completed_requires_auth(async_client: AsyncClient):
    """GET /api/v1/lessons/{id}/is-completed returns 401 without auth."""
    resp = await async_client.get("/api/v1/lessons/99999/is-completed")
    assert resp.status_code == 401


async def test_course_progress_without_auth_returns_zero(async_client: AsyncClient):
    """GET /api/v1/courses/{id}/progress returns zeroed-out progress for unauthenticated callers."""
    resp = await async_client.get("/api/v1/courses/99999/progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["progress_percentage"] == 0
    assert data["completed_lessons"] == 0
