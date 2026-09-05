"""Tests for the early-learning module/activity endpoints (GET /modules,
GET /modules/{id}, POST /activities/{id}/complete).

Content is inserted directly via db_session (matching the test suite's
db_session-fixture convention, e.g. test_bug_hunt.py) rather than routed
through backend/scripts/_seed_early_learning.py, so these tests don't depend
on that script's content.
"""
import json
import uuid
from datetime import date

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


async def _register(async_client: AsyncClient, db_session, prefix: str, role: UserRole = UserRole.student):
    """Register a fresh account, optionally flip its role, log in. Returns
    (student_id, headers) — generalizes the instructor_id fixture's
    register-then-flip-role pattern with a role param, for the
    teacher-exemption test."""
    uid = uuid.uuid4().hex[:8]
    username = f"{prefix}_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "TestPass123!"},
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]
    if role != UserRole.student:
        await db_session.execute(update(Student).where(Student.id == student_id).values(role=role))
        await db_session.commit()
    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "TestPass123!"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return student_id, headers


async def _set_birth_date(db_session, student_id: int, birth_date) -> None:
    await db_session.execute(update(Student).where(Student.id == student_id).values(birth_date=birth_date))
    await db_session.commit()


async def _make_module(
    db_session, instructor_id: int, published: bool, activity_published: bool = True,
    age_min: int = 4, age_max: int = 6,
):
    uid = uuid.uuid4().hex[:8]
    module = EarlyModule(
        title=f"test-module-{uid}",
        subject=EarlySubject.logic,
        display_order=0,
        instructor_id=instructor_id,
        is_published=published,
        is_active=True,
        age_min=age_min,
        age_max=age_max,
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


# ── Age gating ──────────────────────────────────────────────────────────────
# Most accounts have no birth_date at all (see gennis_service.py) — gating
# must only ever exclude a CONFIRMED mismatch, never require proof of
# eligibility, or it would lock out nearly everyone including real 5-8 year
# olds. See early_learning.py's _is_age_eligible.

def _years_ago(n: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - n)
    except ValueError:  # Feb 29 on a non-leap target year
        return today.replace(year=today.year - n, day=28)


@pytest.mark.asyncio
async def test_module_hidden_from_confirmed_too_old_student(
    async_client: AsyncClient, db_session, instructor_id
):
    # Arrange: age_min=5, age_max=8, grace=2 → eligible up to 10; 16 is well outside it
    module, _ = await _make_module(db_session, instructor_id, published=True, age_min=5, age_max=8)
    student_id, headers = await _register(async_client, db_session, "el_age_old")
    await _set_birth_date(db_session, student_id, _years_ago(16))

    # Act
    list_response = await async_client.get("/api/v1/early-learning/modules", headers=headers)
    detail_response = await async_client.get(f"/api/v1/early-learning/modules/{module.id}", headers=headers)

    # Assert: invisible in the list, and 404 (not a special error) on direct access —
    # same treatment as an unpublished module, so age is never leaked to the client.
    assert module.id not in [m["id"] for m in list_response.json()]
    assert detail_response.status_code == 404


@pytest.mark.asyncio
async def test_module_visible_to_student_in_range(async_client: AsyncClient, db_session, instructor_id):
    # Arrange
    module, _ = await _make_module(db_session, instructor_id, published=True, age_min=5, age_max=8)
    student_id, headers = await _register(async_client, db_session, "el_age_ok")
    await _set_birth_date(db_session, student_id, _years_ago(6))

    # Act
    response = await async_client.get("/api/v1/early-learning/modules", headers=headers)

    # Assert
    assert module.id in [m["id"] for m in response.json()]


@pytest.mark.asyncio
async def test_module_visible_when_birth_date_unknown(async_client: AsyncClient, db_session, instructor_id):
    # Arrange: no _set_birth_date call — birth_date stays NULL, the common case today
    module, _ = await _make_module(db_session, instructor_id, published=True, age_min=5, age_max=8)
    student_id, headers = await _register(async_client, db_session, "el_age_unknown")

    # Act
    response = await async_client.get("/api/v1/early-learning/modules", headers=headers)

    # Assert: unknown age never excludes — only a confirmed mismatch does
    assert module.id in [m["id"] for m in response.json()]


@pytest.mark.asyncio
async def test_teacher_sees_module_regardless_of_age(async_client: AsyncClient, db_session, instructor_id):
    """A teacher previewing this feature (see EarlyLearning.js's
    /teacher/early-learning route) must never be excluded by age — the
    point of gating is scoping it to young kids among *students*, not
    hiding it from staff who are supposed to be able to check it."""
    module, _ = await _make_module(db_session, instructor_id, published=True, age_min=5, age_max=8)
    teacher_id, headers = await _register(async_client, db_session, "el_age_teacher", role=UserRole.teacher)
    await _set_birth_date(db_session, teacher_id, _years_ago(30))

    response = await async_client.get("/api/v1/early-learning/modules", headers=headers)

    assert module.id in [m["id"] for m in response.json()]


@pytest.mark.asyncio
async def test_complete_404s_for_confirmed_too_old_student(
    async_client: AsyncClient, db_session, instructor_id
):
    # Arrange
    _, activity = await _make_module(db_session, instructor_id, published=True, age_min=5, age_max=8)
    student_id, headers = await _register(async_client, db_session, "el_age_old_complete")
    await _set_birth_date(db_session, student_id, _years_ago(20))

    # Act
    response = await async_client.post(
        f"/api/v1/early-learning/activities/{activity.id}/complete",
        json={"stars": 3},
        headers=headers,
    )

    # Assert
    assert response.status_code == 404
