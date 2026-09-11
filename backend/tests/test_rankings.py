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

import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient
from sqlalchemy import select

from app.models.ranking import Ranking
from app.models.user import Student, UserRole
from app.services.ranking_service import RankingService


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


# ── calculate_and_update_rankings() — SQL window-function rewrite ───────────


async def test_calculate_and_update_rankings_ranks_are_dense_and_ordered(
    async_client: AsyncClient, db_session
):
    """After calculate_and_update_rankings() runs, global_rank must be a
    dense (no-gap) sequence 1..N strictly matching descending total_points
    order, for at least 5 students with distinct point totals.

    Regression test for the rewrite from a Python-side load-everything-and-
    sort loop to a SQL `ROW_NUMBER() OVER (...)` window (one UPDATE per
    period instead of one per row).
    """
    service = RankingService(db_session)

    # Distinct, deliberately-unsorted point totals so awarding order != rank
    # order — this would catch a rewrite that accidentally ranked by
    # insertion order instead of by points.
    point_totals = [30, 90, 10, 70, 50]
    student_ids = []

    for points in point_totals:
        uid = uuid.uuid4().hex[:8]
        reg = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"rankuser_{uid}",
                "email": f"rankuser_{uid}@example.com",
                "password": "securepass123",
            },
        )
        assert reg.status_code == 201, f"Register failed: {reg.text}"
        student_id = reg.json()["user"]["id"]
        student_ids.append(student_id)
        await service.add_points_to_student(student_id, points)

    # add_points_to_student already calls calculate_and_update_rankings
    # internally, but call it again explicitly so this test exercises (and
    # asserts against) the rewritten method directly and deterministically,
    # independent of that internal call.
    await service.calculate_and_update_rankings()

    # Look at every active student's Ranking row, not just our 5 — other
    # test files in this session-scoped DB may also have awarded points to
    # their own students, and dense-ness is a property of the whole ranked
    # population, not a subset. This also makes the assertion robust to
    # test execution order.
    result = await db_session.execute(
        select(Ranking.student_id, Ranking.total_points, Ranking.global_rank)
        .join(Student, Student.id == Ranking.student_id)
        .where(Student.is_active == True, Student.role == UserRole.student)
    )
    all_rows = {r.student_id: (r.total_points, r.global_rank) for r in result.all()}

    # Every one of the 5 students got a Ranking row and a rank.
    assert set(student_ids) <= set(all_rows.keys())

    all_ranks = [rank for _pts, rank in all_rows.values()]
    n = len(all_ranks)
    assert sorted(all_ranks) == list(range(1, n + 1)), (
        "global_rank across all active-student rankings must be a dense "
        "(gap-free), unique 1..N sequence"
    )

    # Restrict to our 5 students: sorted by points descending, their ranks
    # must be strictly increasing (highest points -> lowest rank number) —
    # this would catch a rewrite that ranked by insertion order or ignored
    # points entirely.
    my_rows = {sid: all_rows[sid] for sid in student_ids}
    by_points_desc = sorted(my_rows.items(), key=lambda kv: kv[1][0], reverse=True)
    ranks_in_points_order = [rank for _sid, (_pts, rank) in by_points_desc]

    assert ranks_in_points_order == sorted(ranks_in_points_order), (
        "global_rank must increase monotonically as total_points decreases"
    )
    assert len(set(ranks_in_points_order)) == 5, (
        "global_rank must be unique per student (no ties collapsed)"
    )

    # And the points themselves came back exactly as awarded.
    assert [pts for _sid, (pts, _rank) in by_points_desc] == sorted(
        point_totals, reverse=True
    )
