"""Tests for the orphaned-submission escape hatch.

Bug: create_project() immediately marks a lesson-linked, github_url
project "Submitted" on creation, relying on a separate POST
.../submit call to set submitted_at and trigger AI review. If that
second call never reaches the server, the project is stuck forever at
status="Submitted" with submitted_at=NULL, and the old guard blocked the
student from ever resubmitting. is_orphaned_submission() (project_service.py)
now distinguishes "genuinely pending review" from "half-finished submit
that never completed", and both the resubmit guard and
GET .../submission's `stuck` field use it.
"""
import uuid
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, update

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.project import Project
from app.models.user import Student, UserRole


@pytest_asyncio.fixture
async def instructor_id(async_client: AsyncClient, db_session) -> int:
    uid = uuid.uuid4().hex[:8]
    username = f"proj_teacher_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "teacherpass123"},
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["user"]["id"]
    await db_session.execute(update(Student).where(Student.id == user_id).values(role=UserRole.teacher))
    await db_session.commit()
    return user_id


@pytest_asyncio.fixture
async def lesson_id(db_session, instructor_id) -> int:
    course = Course(
        title="Test Course", description="—", instructor_id=instructor_id,
        difficulty_level="Beginner", duration_weeks=1, max_points=100,
    )
    db_session.add(course)
    await db_session.flush()
    lesson = Lesson(course_id=course.id, title="Test Lesson", order=1)
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)
    return lesson.id


def _submit_payload(lesson_id: int, github_url: str = "https://github.com/example/repo") -> dict:
    return {
        "title": "Amaliy mashq",
        "description": "Test project submission",
        "github_url": github_url,
        "lesson_id": lesson_id,
        "difficulty_level": "Easy",
    }


@pytest.mark.asyncio
async def test_resubmit_blocked_while_genuinely_pending(
    async_client: AsyncClient, auth_headers: dict, lesson_id: int
):
    # Arrange: a fresh submission, created just now
    first = await async_client.post("/api/v1/project/", json=_submit_payload(lesson_id), headers=auth_headers)
    assert first.status_code == 201, first.text

    # Act: try to submit again immediately
    response = await async_client.post("/api/v1/project/", json=_submit_payload(lesson_id), headers=auth_headers)

    # Assert: genuinely recent — still blocked. Errors go through this
    # app's global HTTPException handler (app/core/exceptions.py), which
    # wraps `detail` as `error.message`, not a bare `detail` key.
    assert response.status_code == 400
    assert "tekshirilmoqda" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_resubmit_allowed_once_orphaned(
    async_client: AsyncClient, auth_headers: dict, db_session, lesson_id: int
):
    # Arrange: a submission stuck exactly like the reported bug —
    # status=Submitted, submitted_at never set (the /submit call "never
    # arrived"), old enough to be past the grace period.
    first = await async_client.post("/api/v1/project/", json=_submit_payload(lesson_id), headers=auth_headers)
    assert first.status_code == 201, first.text
    project_id = first.json()["id"]

    stale = datetime.utcnow() - timedelta(minutes=5)
    await db_session.execute(
        update(Project).where(Project.id == project_id).values(created_at=stale, updated_at=stale)
    )
    await db_session.commit()

    # Act
    response = await async_client.post("/api/v1/project/", json=_submit_payload(lesson_id), headers=auth_headers)

    # Assert: orphaned, not genuinely pending — a fresh submission is
    # allowed (not asserting the new id differs from the old one: SQLite
    # reuses freed rowids after a DELETE when a table has no explicit
    # AUTOINCREMENT, unlike Postgres's SERIAL/IDENTITY in production, so
    # that isn't a safe signal here). A genuinely fresh row is what
    # matters — check its created_at moved off the artificially-aged
    # timestamp instead.
    assert response.status_code == 201, response.text
    new_project = (
        await db_session.execute(select(Project).where(Project.id == response.json()["id"]))
    ).scalar_one()
    assert new_project.created_at > stale + timedelta(minutes=1)


@pytest.mark.asyncio
async def test_submission_status_reports_stuck(
    async_client: AsyncClient, auth_headers: dict, db_session, lesson_id: int
):
    # Arrange
    first = await async_client.post("/api/v1/project/", json=_submit_payload(lesson_id), headers=auth_headers)
    assert first.status_code == 201, first.text
    project_id = first.json()["id"]

    stale = datetime.utcnow() - timedelta(minutes=5)
    await db_session.execute(
        update(Project).where(Project.id == project_id).values(created_at=stale, updated_at=stale)
    )
    await db_session.commit()

    course_id = (
        await db_session.execute(select(Lesson.course_id).where(Lesson.id == lesson_id))
    ).scalar_one()

    # Act
    response = await async_client.get(
        f"/api/v1/courses/{course_id}/lessons/{lesson_id}/submission",
        headers=auth_headers,
    )

    # Assert
    body = response.json()
    assert body["submitted"] is True
    assert body["stuck"] is True
