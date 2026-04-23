import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.base_class import Base
from app.db.session import get_db
from app.config import settings


def make_engine():
    return create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    engine = make_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield


@pytest_asyncio.fixture(scope="session")
async def async_client(setup_db):
    engine = make_engine()
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def registered_student(async_client, setup_db):
    data = {
        "username": "teststudent",
        "email": "test@example.com",
        "full_name": "Test Student",
        "password": "TestPass123!"
    }
    response = await async_client.post("/api/v1/auth/register", json=data)
    print("\nREGISTER:", response.status_code, response.json())
    return data


@pytest_asyncio.fixture(scope="session")
async def auth_token(async_client, registered_student):
    response = await async_client.post("/api/v1/auth/login", json={
        "username": registered_student["username"],
        "password": registered_student["password"]
    })
    print("\nLOGIN:", response.status_code, response.json())
    data = response.json()
    if "access_token" not in data:
        raise Exception(f"Login muvaffaqiyatsiz! Javob: {data}")
    return data["access_token"]


@pytest_asyncio.fixture(scope="session")
async def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
