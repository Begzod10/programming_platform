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


# ── Manual point adjustments: audit ledger + recalc-round-trip ───────────────


import uuid  # noqa: E402
import pytest_asyncio  # noqa: E402
from sqlalchemy import select  # noqa: E402


@pytest_asyncio.fixture
async def teacher_and_student(async_client: AsyncClient, db_session):
    """Register a teacher (upgraded from student) and a plain student.

    Returns (teacher_headers, student_id).
    """
    from app.models.user import Student, UserRole

    uid = uuid.uuid4().hex[:8]

    # Register teacher via API then upgrade role directly in DB (register only
    # creates students).
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"teach_{uid}",
            "email": f"teach_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg.status_code == 201, reg.text
    t_data = reg.json()
    t_id = t_data["user"]["id"]
    t_headers = {"Authorization": f"Bearer {t_data['access_token']}"}

    async with db_session.begin_nested():
        teacher = (await db_session.execute(
            select(Student).where(Student.id == t_id)
        )).scalar_one()
        teacher.role = UserRole.teacher
    await db_session.commit()

    # Register a plain student to receive adjustments.
    reg2 = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": f"stud_{uid}",
            "email": f"stud_{uid}@example.com",
            "password": "securepass123",
        },
    )
    assert reg2.status_code == 201, reg2.text
    s_id = reg2.json()["user"]["id"]

    return t_headers, s_id


async def test_add_points_writes_point_adjustment(
    async_client: AsyncClient, teacher_and_student, db_session,
):
    """POST /rankings/add-points inserts a PointAdjustment row with the reason."""
    from app.models.point_adjustment import PointAdjustment

    headers, student_id = teacher_and_student
    resp = await async_client.post(
        "/api/v1/rankings/add-points",
        headers=headers,
        json={"student_id": student_id, "points": 42, "reason": "manual bonus"},
    )
    assert resp.status_code == 200, resp.text

    rows = (await db_session.execute(
        select(PointAdjustment).where(PointAdjustment.student_id == student_id)
    )).scalars().all()
    assert len(rows) == 1
    row = rows[0]
    assert row.delta == 42
    assert row.reason == "manual bonus"
    assert row.actor_id is not None


async def test_subtract_points_writes_negative_delta(
    async_client: AsyncClient, teacher_and_student, db_session,
):
    from app.models.point_adjustment import PointAdjustment

    headers, student_id = teacher_and_student
    # Prime the student with 100 points via add-points, then subtract 20.
    await async_client.post(
        "/api/v1/rankings/add-points",
        headers=headers,
        json={"student_id": student_id, "points": 100, "reason": "seed"},
    )
    resp = await async_client.post(
        "/api/v1/rankings/subtract-points",
        headers=headers,
        json={"student_id": student_id, "points": 20, "reason": "penalty"},
    )
    assert resp.status_code == 200, resp.text

    rows = (await db_session.execute(
        select(PointAdjustment)
        .where(PointAdjustment.student_id == student_id)
        .order_by(PointAdjustment.id.asc())
    )).scalars().all()
    assert [r.delta for r in rows] == [100, -20]
    assert rows[1].reason == "penalty"


async def test_add_points_requires_reason(
    async_client: AsyncClient, teacher_and_student,
):
    """Request without `reason` is rejected by pydantic (422)."""
    headers, student_id = teacher_and_student
    resp = await async_client.post(
        "/api/v1/rankings/add-points",
        headers=headers,
        json={"student_id": student_id, "points": 5},
    )
    assert resp.status_code == 422


async def test_recalc_reconciles_manual_adjustments_to_zero_drift(
    async_client: AsyncClient, teacher_and_student, db_session,
):
    """After manual adjustments, the recalc identity SUM must match total_points.

    Fresh test DB → the only points term touched is the manual ledger, so the
    identity trivially holds and drift should be 0 for that student.
    """
    from scripts.recalc_points import _compute_for_student
    from app.models.user import Student

    headers, student_id = teacher_and_student
    # Two adds, one subtract: net +30.
    for pts, reason in [(50, "a"), (10, "b"), (0, "")]:
        pass
    await async_client.post(
        "/api/v1/rankings/add-points",
        headers=headers,
        json={"student_id": student_id, "points": 50, "reason": "a"},
    )
    await async_client.post(
        "/api/v1/rankings/add-points",
        headers=headers,
        json={"student_id": student_id, "points": 10, "reason": "b"},
    )
    await async_client.post(
        "/api/v1/rankings/subtract-points",
        headers=headers,
        json={"student_id": student_id, "points": 30, "reason": "c"},
    )

    st = (await db_session.execute(
        select(Student).where(Student.id == student_id)
    )).scalar_one()
    await db_session.refresh(st)

    row = await _compute_for_student(db_session, st)
    assert row["manual_pts"] == 30
    assert row["expected"] == 30
    # student.total_points should also be 30 after those three calls (net).
    assert row["current"] == 30
    assert row["delta"] == 0
