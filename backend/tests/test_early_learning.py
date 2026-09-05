"""Tests for the early-learning module/activity endpoints (GET /modules,
GET /modules/{id}, POST /activities/{id}/complete).

Content is inserted directly via db_session (matching the test suite's
db_session-fixture convention, e.g. test_bug_hunt.py) rather than routed
through backend/scripts/_seed_early_learning.py, so these tests don't depend
on that script's content.
"""
import json
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import update

from app.models.early_learning import (
    EarlyActivity,
    EarlyActivityType,
    EarlyModule,
    EarlySubject,
)
from app.models.user import Student, UserRole


def _select_content(character: str, n_correct: int = 2, n_distractor: int = 1) -> dict:
    return {
        "mode": "select",
        "character": {"emoji": "🧪", "label": character},
        "correct_items": [
            {"id": f"c{i}", "label": f"correct {i}", "icon": "BookOpen"} for i in range(n_correct)
        ],
        "distractor_items": [
            {"id": f"d{i}", "label": f"distractor {i}", "icon": "Keyboard"} for i in range(n_distractor)
        ],
    }


@pytest_asyncio.fixture
async def instructor_id(async_client: AsyncClient, db_session) -> int:
    """A Student flipped to role=teacher, for EarlyModule.instructor_id's FK
    — mirrors test_bug_hunt.py's teacher_headers fixture, minus the login
    step since only the id is needed here."""
    uid = uuid.uuid4().hex[:8]
    username = f"early_teacher_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "teacherpass123"},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["user"]["id"]
    await db_session.execute(update(Student).where(Student.id == user_id).values(role=UserRole.teacher))
    await db_session.commit()
    return user_id


async def _make_module(db_session, instructor_id: int, published: bool, activity_published: bool = True):
    uid = uuid.uuid4().hex[:8]
    module = EarlyModule(
        title=f"test-module-{uid}",
        subject=EarlySubject.logic,
        display_order=0,
        instructor_id=instructor_id,
        is_published=published,
        is_active=True,
    )
    db_session.add(module)
    await db_session.flush()
    activity = EarlyActivity(
        module_id=module.id,
        title=f"test-activity-{uid}",
        activity_type=EarlyActivityType.match,
        content_json=json.dumps(_select_content("Test")),
        max_stars=3,
        is_published=activity_published,
        is_active=True,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(module)
    await db_session.refresh(activity)
    return module, activity


@pytest_asyncio.fixture
async def published_module(db_session, instructor_id):
    module, activity = await _make_module(db_session, instructor_id, published=True)
    return module, activity


@pytest_asyncio.fixture
async def unpublished_module(db_session, instructor_id):
    module, activity = await _make_module(db_session, instructor_id, published=False)
    return module, activity


@pytest.mark.asyncio
async def test_list_modules_excludes_unpublished(
    async_client: AsyncClient, auth_headers: dict, published_module, unpublished_module
):
    # Arrange: one published + one unpublished module already seeded by fixtures
    pub_module, _ = published_module
    unpub_module, _ = unpublished_module

    # Act
    response = await async_client.get("/api/v1/early-learning/modules", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    ids = [m["id"] for m in response.json()]
    assert pub_module.id in ids
    assert unpub_module.id not in ids


@pytest.mark.asyncio
async def test_get_module_404s_when_unpublished(
    async_client: AsyncClient, auth_headers: dict, unpublished_module
):
    # Arrange
    module, _ = unpublished_module

    # Act
    response = await async_client.get(f"/api/v1/early-learning/modules/{module.id}", headers=auth_headers)

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_module_404s_when_missing(async_client: AsyncClient, auth_headers: dict):
    # Act
    response = await async_client.get("/api/v1/early-learning/modules/999999999", headers=auth_headers)

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_module_detail_defaults_to_zero_progress(
    async_client: AsyncClient, auth_headers: dict, published_module
):
    # Arrange
    module, activity = published_module

    # Act
    response = await async_client.get(f"/api/v1/early-learning/modules/{module.id}", headers=auth_headers)

    # Assert
    body = response.json()
    activity_out = next(a for a in body["activities"] if a["id"] == activity.id)
    assert activity_out["best_stars"] == 0
    assert activity_out["attempts"] == 0
    assert activity_out["content"]["mode"] == "select"


@pytest.mark.asyncio
async def test_complete_activity_creates_completion(
    async_client: AsyncClient, auth_headers: dict, published_module
):
    # Arrange
    _, activity = published_module

    # Act
    response = await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 2},
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["stars_earned"] == 2
    assert body["attempts"] == 1


@pytest.mark.asyncio
async def test_complete_activity_upserts_without_regressing_stars(
    async_client: AsyncClient, auth_headers: dict, published_module
):
    # Arrange
    _, activity = published_module
    await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 3},
        headers=auth_headers,
    )

    # Act: a worse second attempt
    response = await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 1},
        headers=auth_headers,
    )

    # Assert: attempts increments, but stars_earned keeps the best score
    body = response.json()
    assert body["attempts"] == 2
    assert body["stars_earned"] == 3


@pytest.mark.asyncio
async def test_complete_activity_404s_when_unpublished(
    async_client: AsyncClient, auth_headers: dict, unpublished_module
):
    # Arrange
    _, activity = unpublished_module

    # Act
    response = await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 1},
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_completions_are_isolated_per_student(
    async_client: AsyncClient, auth_headers: dict, published_module
):
    # Arrange: one student completes the activity
    module, activity = published_module
    await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 3},
        headers=auth_headers,
    )
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"early_student_{uid}", "email": f"early_student_{uid}@example.com", "password": "testpassword123"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"username": f"early_student_{uid}", "password": "testpassword123"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Act: a second student who never played reads the same module
    response = await async_client.get(f"/api/v1/early-learning/modules/{module.id}", headers=other_headers)

    # Assert: their own progress is independent (still zero)
    body = response.json()
    activity_out = next(a for a in body["activities"] if a["id"] == activity.id)
    assert activity_out["best_stars"] == 0
    assert activity_out["attempts"] == 0
