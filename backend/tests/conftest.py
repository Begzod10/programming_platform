"""
Pytest configuration for the student_platform backend test suite.

Boot order (critical):
  1. os.environ overrides are set at the very top of this module.
  2. Only AFTER that do we import any app module, so pydantic_settings
     picks up the SQLite DATABASE_URL instead of the production PostgreSQL URL
     from .env, and SECRET_KEY is guaranteed to satisfy the min_length=16
     constraint without touching the real .env file.
  3. Tables are created once per session using asyncio.run() (sync fixture)
     to avoid pytest-asyncio event-loop scope conflicts with session fixtures.
  4. GennisService.login is mocked for every test so no outgoing network
     calls block the test run (the default timeout is 10 s).
"""

import asyncio
import os
import uuid

# ── 1. Override env vars BEFORE any app import ───────────────────────────────
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-characters-xxx"

# ── 2. App imports (engine/session already use SQLite from the env var) ───────
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport

# Importing app.db.base registers ALL mapped classes on Base.metadata, which
# is required for create_all to create every table.
from app.db import base as _all_models  # noqa: F401
from app.db.base_class import Base
from app.db.database import engine as _app_engine, AsyncSessionLocal
from app.main import app


# ── 3. Create tables once per session (sync, avoids loop-scope issues) ────────

async def _create_all_tables() -> None:
    async with _app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _dispose_engine() -> None:
    await _app_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create the SQLite test schema before any test runs."""
    asyncio.run(_create_all_tables())
    yield
    asyncio.run(_dispose_engine())


# ── 4. Mock GennisService so every test is fast (no 10-second network wait) ───

@pytest_asyncio.fixture(autouse=True)
async def mock_gennis_login():
    """Patch GennisService.login to return None for all tests.

    This makes the login flow fall through to local authentication immediately
    instead of trying to reach https://admin.gennis.uz for 10 seconds.
    """
    with patch(
        "app.services.gennis_service.GennisService.login",
        new=AsyncMock(return_value=None),
    ):
        yield


# ── 5. Per-test fixtures ───────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def db_session():
    """Raw async session for direct ORM inserts in test setup code."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    """httpx AsyncClient pointing at the ASGI app.

    ASGITransport does NOT trigger the ASGI lifespan, so init_db() (which
    contains PostgreSQL-specific SQL) is never called.  Tables are already
    in place from the session-scoped create_tables fixture.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient) -> dict:
    """Register a fresh student per test, log in, return Bearer headers."""
    uid = uuid.uuid4().hex[:8]
    username = f"testuser_{uid}"
    email = f"test_{uid}@example.com"
    password = "testpassword123"

    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
