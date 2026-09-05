"""Tests for GET /early-learning/leaderboard — a student's own classmates
(share a teacher-owned Group or Flow), ranked by total stars across every
published early-learning activity. See app/services/teacher_students.py's
classmate_ids_subquery for the Group+Flow scoping this builds on.
"""
import json
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import insert, update

from app.models.early_learning import EarlyActivity, EarlyActivityCompletion, EarlyActivityType, EarlyModule, EarlySubject
from app.models.group import Group, student_groups
from app.models.user import Student, UserRole


def _select_content(character: str) -> dict:
    return {
        "mode": "select",
        "character": {"emoji": "🧪", "label": character},
        "correct_items": [{"id": "c0", "label": "correct", "icon": "BookOpen"}],
        "distractor_items": [{"id": "d0", "label": "distractor", "icon": "Keyboard"}],
    }


async def _register_student(async_client: AsyncClient, prefix: str) -> tuple[int, dict]:
    uid = uuid.uuid4().hex[:8]
    username = f"{prefix}_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "TestPass123!"},
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]
    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "TestPass123!"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return student_id, headers


@pytest_asyncio.fixture
async def instructor_id(async_client: AsyncClient, db_session) -> int:
    student_id, _ = await _register_student(async_client, "el_lb_teacher")
    await db_session.execute(update(Student).where(Student.id == student_id).values(role=UserRole.teacher))
    await db_session.commit()
    return student_id


@pytest_asyncio.fixture
async def published_activity(db_session, instructor_id) -> int:
    module = EarlyModule(
        title=f"test-lb-module-{uuid.uuid4().hex[:8]}",
        subject=EarlySubject.logic, display_order=0,
        instructor_id=instructor_id, is_published=True, is_active=True,
    )
    db_session.add(module)
    await db_session.flush()
    activity = EarlyActivity(
        module_id=module.id, title=f"test-lb-activity-{uuid.uuid4().hex[:8]}",
        activity_type=EarlyActivityType.match, content_json=json.dumps(_select_content("Test")),
        max_stars=3, is_published=True, is_active=True,
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity.id


async def _join_group(db_session, student_id: int, group_id: int) -> None:
    await db_session.execute(insert(student_groups).values(student_id=student_id, group_id=group_id))
    await db_session.commit()


@pytest.mark.asyncio
async def test_leaderboard_reports_no_class_for_unassigned_student(
    async_client: AsyncClient, auth_headers: dict
):
    # Act: a freshly-registered student belongs to no Group/Flow at all
    response = await async_client.get("/api/v1/early-learning/leaderboard", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["has_class"] is False
    assert len(body["entries"]) == 1
    assert body["entries"][0]["is_me"] is True
    assert body["entries"][0]["total_stars"] == 0


@pytest.mark.asyncio
async def test_leaderboard_ranks_classmates_by_total_stars(
    async_client: AsyncClient, db_session, instructor_id, published_activity
):
    # Arrange: a real class — a Group owned by instructor_id, two students in it
    group = Group(name="test-lb-group", teacher_id=instructor_id)
    db_session.add(group)
    # commit (not just flush) — async_client's HTTP calls below use a
    # separate session/connection to the same SQLite file; leaving this
    # transaction open causes "database is locked" once they try to write.
    await db_session.commit()

    high_id, high_headers = await _register_student(async_client, "el_lb_high")
    low_id, low_headers = await _register_student(async_client, "el_lb_low")
    await _join_group(db_session, high_id, group.id)
    await _join_group(db_session, low_id, group.id)

    await async_client.post(
        f"/api/v1/early-learning/activities/{published_activity}/complete",
        json={"stars": 3}, headers=high_headers,
    )
    await async_client.post(
        f"/api/v1/early-learning/activities/{published_activity}/complete",
        json={"stars": 1}, headers=low_headers,
    )

    # Act: the low scorer checks the leaderboard
    response = await async_client.get("/api/v1/early-learning/leaderboard", headers=low_headers)

    # Assert
    body = response.json()
    assert body["has_class"] is True
    by_id = {e["student_id"]: e for e in body["entries"]}
    assert high_id in by_id and low_id in by_id
    assert by_id[high_id]["total_stars"] == 3
    assert by_id[low_id]["total_stars"] == 1
    assert by_id[high_id]["rank"] < by_id[low_id]["rank"]
    assert by_id[low_id]["is_me"] is True
    assert by_id[high_id]["is_me"] is False


@pytest.mark.asyncio
async def test_leaderboard_excludes_students_outside_the_class(
    async_client: AsyncClient, db_session, instructor_id, published_activity
):
    # Arrange: student in the class vs. a random student with no shared teacher
    group = Group(name="test-lb-group-2", teacher_id=instructor_id)
    db_session.add(group)
    await db_session.commit()

    in_class_id, in_class_headers = await _register_student(async_client, "el_lb_inclass")
    await _join_group(db_session, in_class_id, group.id)

    outsider_id, outsider_headers = await _register_student(async_client, "el_lb_outsider")
    await async_client.post(
        f"/api/v1/early-learning/activities/{published_activity}/complete",
        json={"stars": 3}, headers=outsider_headers,
    )

    # Act
    response = await async_client.get("/api/v1/early-learning/leaderboard", headers=in_class_headers)

    # Assert: the outsider's high score never shows up
    body = response.json()
    ids = {e["student_id"] for e in body["entries"]}
    assert outsider_id not in ids
    assert in_class_id in ids
