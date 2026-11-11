"""Shared setup helpers for the early-learning sticker tests."""
import json
import uuid
from datetime import date

from httpx import AsyncClient
from sqlalchemy import update

from app.models.early_learning import (
    EarlyActivity, EarlyActivityCompletion, EarlyActivityDailyStars,
    EarlyActivityType, EarlyModule, EarlySubject,
)
from app.models.user import Student, UserRole

PASSWORD = "TestPass123!"


async def _register(async_client: AsyncClient, db_session, prefix: str, role: UserRole):
    username = f"{prefix}_{uuid.uuid4().hex[:8]}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": PASSWORD},
    )
    assert reg.status_code == 201, reg.text
    student_id = reg.json()["user"]["id"]
    if role != UserRole.student:
        await db_session.execute(update(Student).where(Student.id == student_id).values(role=role))
        await db_session.commit()
    login = await async_client.post("/api/v1/auth/login", json={"username": username, "password": PASSWORD})
    return student_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


async def make_teacher(async_client: AsyncClient, db_session) -> int:
    teacher_id, _ = await _register(async_client, db_session, "stk_teacher", UserRole.teacher)
    return teacher_id


async def make_student(async_client: AsyncClient, db_session, role: UserRole = UserRole.student):
    return await _register(async_client, db_session, "stk_kid", role)


async def make_module(db_session, instructor_id: int, n_activities: int = 3, published: bool = True,
                      title_ru: str | None = None, icon_emoji: str | None = None,
                      modes: list[str] | None = None):
    uid = uuid.uuid4().hex[:8]
    module = EarlyModule(
        title=f"stk-module-{uid}", title_ru=title_ru, icon_emoji=icon_emoji,
        subject=EarlySubject.logic, display_order=0, instructor_id=instructor_id,
        is_published=published, is_active=True, age_min=4, age_max=12,
    )
    db_session.add(module)
    await db_session.flush()
    activities = []
    for i in range(n_activities):
        activity = EarlyActivity(
            module_id=module.id, title=f"stk-activity-{uid}-{i}", order=i,
            activity_type=EarlyActivityType.match,
            content_json=json.dumps({"mode": modes[i] if modes else "select",
                                     "correct_items": [], "distractor_items": []}),
            max_stars=3, is_published=True, is_active=True,
        )
        db_session.add(activity)
        activities.append(activity)
    await db_session.commit()
    await db_session.refresh(module)
    for a in activities:
        await db_session.refresh(a)
    return module, activities


async def add_completion(db_session, student_id: int, activity_id: int, stars: int = 3) -> None:
    db_session.add(EarlyActivityCompletion(
        student_id=student_id, activity_id=activity_id, stars_earned=stars, attempts=1,
    ))
    await db_session.commit()


async def add_daily(db_session, student_id: int, activity_id: int, day: date, stars: int = 3,
                    attempts: int = 1) -> None:
    db_session.add(EarlyActivityDailyStars(
        student_id=student_id, activity_id=activity_id, activity_date=day,
        stars_earned=stars, attempts=attempts,
    ))
    await db_session.commit()
