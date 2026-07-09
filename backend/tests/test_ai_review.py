"""
Integration tests for the /api/v1/ai/{project_id}/ai-review endpoint.

Covers:
- Auth required (401 without token)
- Non-existent project returns 404
- Project owned by a different student returns 403
- Successful review with mocked AI service returns 200
- Non-integer project_id returns 422 (FastAPI path-param validation)
- Mock is called rather than the real AI service

The actual AI call (analyze_project_with_grok via run_ai_review_for_project)
is always mocked so tests are fast and offline.
"""

import uuid

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

BASE = "/api/v1/ai"


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def student_with_project(async_client: AsyncClient, db_session):
    """Register a student and insert a project in the DB for that student.

    Returns (auth_headers, project_id).
    """
    from app.models.project import Project

    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"aiuser_{uid}",
            "email": f"aiuser_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, f"Student register failed: {reg.text}"
    user_data = reg.json()
    user_id = user_data["user"]["id"]
    token = user_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project = Project(
        student_id=user_id,
        title="My Test Project",
        description="Integration test project",
        difficulty_level="Easy",
        github_url="https://github.com/example/repo",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return headers, project.id


# ── Auth guard ────────────────────────────────────────────────────────────────

async def test_ai_review_requires_auth_returns_401(async_client: AsyncClient):
    """POST without a token returns 401 before any project lookup."""
    resp = await async_client.post(f"{BASE}/1/ai-review")
    assert resp.status_code == 401


# ── Not found ─────────────────────────────────────────────────────────────────

async def test_ai_review_nonexistent_project_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """POST for a project ID that doesn't exist returns 404."""
    resp = await async_client.post(f"{BASE}/99999999/ai-review", headers=auth_headers)
    assert resp.status_code == 404


# ── Ownership guard ───────────────────────────────────────────────────────────

async def test_ai_review_wrong_owner_returns_403(
    async_client: AsyncClient, student_with_project, auth_headers: dict
):
    """POST by a different student on another student's project returns 403.

    student_with_project owns the project; auth_headers is a separate student.
    """
    _, project_id = student_with_project
    resp = await async_client.post(
        f"{BASE}/{project_id}/ai-review",
        headers=auth_headers,  # different student
    )
    assert resp.status_code == 403


# ── Validation ────────────────────────────────────────────────────────────────

async def test_ai_review_non_integer_project_id_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """A non-integer path param (e.g. 'abc') fails FastAPI validation → 422."""
    resp = await async_client.post(f"{BASE}/abc/ai-review", headers=auth_headers)
    assert resp.status_code == 422


# ── Mocked success ────────────────────────────────────────────────────────────

async def test_ai_review_mocked_returns_200_with_message(
    async_client: AsyncClient, student_with_project
):
    """POST by the project owner with a mocked AI service returns 200.

    run_ai_review_for_project is patched so no real HTTP call is made.
    """
    headers, project_id = student_with_project

    mock_result = {
        "score": 88,
        "strengths": "Clean code and good naming",
        "improvements": "Add error handling",
        "bugs": "",
        "grade": "B+",
    }

    with patch(
        "app.api.v1.endpoints.ai_review.run_ai_review_for_project",
        new=AsyncMock(return_value=mock_result),
    ):
        resp = await async_client.post(
            f"{BASE}/{project_id}/ai-review",
            headers=headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "AI baholash yakunlandi!"
    assert data["score"] == 88
    assert data["grade"] == "B+"


async def test_ai_review_mock_prevents_real_http(
    async_client: AsyncClient, student_with_project
):
    """Verify that the mock is invoked (not the real AI) by asserting call count."""
    headers, project_id = student_with_project

    mock_fn = AsyncMock(return_value={"score": 70, "strengths": "ok", "improvements": "", "bugs": "", "grade": "C"})

    with patch(
        "app.api.v1.endpoints.ai_review.run_ai_review_for_project",
        new=mock_fn,
    ):
        resp = await async_client.post(
            f"{BASE}/{project_id}/ai-review",
            headers=headers,
        )

    assert resp.status_code == 200
    # Confirm the mock was called exactly once (the real network was never hit)
    mock_fn.assert_called_once()
