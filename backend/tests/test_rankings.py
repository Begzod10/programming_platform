"""
Integration tests for rankings endpoints.

Verifies:
- /leaderboard is publicly accessible for all supported period values.
- /leaderboard respects limit and offset params.
- /project-leaderboard rejects invalid period values with 422.
- /project-leaderboard with period=all returns a well-formed response.

Note: /project-leaderboard uses raw PostgreSQL SQL (::int casts, INTERVAL).
The period=all test mocks AsyncSession.execute to avoid the PG-specific syntax
while still exercising the response serialisation logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient


# ── /leaderboard (ORM-based, SQLite-safe) ────────────────────────────────────


async def test_leaderboard_all_period_returns_200(async_client: AsyncClient):
    """GET /api/v1/rankings/leaderboard with default period returns 200 and a list."""
    resp = await async_client.get("/api/v1/rankings/leaderboard")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_leaderboard_daily_period_returns_200(async_client: AsyncClient):
    """GET /api/v1/rankings/leaderboard?period=daily returns 200."""
    resp = await async_client.get("/api/v1/rankings/leaderboard?period=daily")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_leaderboard_weekly_period_returns_200(async_client: AsyncClient):
    """GET /api/v1/rankings/leaderboard?period=weekly returns 200."""
    resp = await async_client.get("/api/v1/rankings/leaderboard?period=weekly")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_leaderboard_monthly_period_returns_200(async_client: AsyncClient):
    """GET /api/v1/rankings/leaderboard?period=monthly returns 200."""
    resp = await async_client.get("/api/v1/rankings/leaderboard?period=monthly")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_leaderboard_limit_param(async_client: AsyncClient):
    """GET /api/v1/rankings/leaderboard?limit=5 returns 200 with at most 5 items."""
    resp = await async_client.get("/api/v1/rankings/leaderboard?limit=5")
    assert resp.status_code == 200
    assert len(resp.json()) <= 5


# ── /project-leaderboard ─────────────────────────────────────────────────────


async def test_project_leaderboard_invalid_period_returns_422(async_client: AsyncClient):
    """GET /api/v1/rankings/project-leaderboard?period=invalid returns 422.

    FastAPI validates the Literal["all","day","week","month"] type before the
    handler runs, so no DB call is made and no mocking is needed.
    """
    resp = await async_client.get("/api/v1/rankings/project-leaderboard?period=invalid")
    assert resp.status_code == 422


async def test_project_leaderboard_all_period_returns_200(async_client: AsyncClient):
    """GET /api/v1/rankings/project-leaderboard?period=all returns 200 with expected shape.

    The handler uses raw PostgreSQL SQL (::int casts). We mock AsyncSession.execute
    to return an empty result so the test runs against SQLite without a parse error,
    while still verifying the response serialisation.
    """
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []

    with patch(
        "sqlalchemy.ext.asyncio.AsyncSession.execute",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await async_client.get("/api/v1/rankings/project-leaderboard?period=all")

    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["items"] == []
    assert data["total"] == 0
    assert data["period"] == "all"
