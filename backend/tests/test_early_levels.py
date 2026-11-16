"""Game levels: levels 2-3 of each early-learning activity (own stars, locked
until the previous level has 2+ stars)."""
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.early_learning import EarlyActivityCompletion, EarlyActivityLevelCompletion
from app.models.user import UserRole
from tests._early_helpers import add_completion, make_module, make_student, make_teacher

pytestmark = pytest.mark.asyncio
BASE = "/api/v1/early-learning"


@pytest.fixture(autouse=True)
def _games_unlocked():
    """These tests exercise levels, not the daily-quota gate."""
    from app.main import app
    from app.dependencies import require_games_unlocked
    app.dependency_overrides[require_games_unlocked] = lambda: None
    yield
    app.dependency_overrides.pop(require_games_unlocked, None)


@pytest_asyncio.fixture
async def teacher(async_client, db_session):
    return await make_teacher(async_client, db_session)


async def _post(async_client, headers, activity_id, stars, level=None):
    body = {"stars": stars}
    if level is not None:
        body["level"] = level
    return await async_client.post(f"{BASE}/activities/{activity_id}/complete", json=body, headers=headers)


# ---- Task 1: completing a level -------------------------------------------

async def test_level_two_locked_until_two_stars(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    a = acts[0]
    res = await _post(async_client, headers, a.id, 3, level=2)
    assert res.status_code == 409 and res.json()["error"]["message"] == "level_locked"
    assert (await _post(async_client, headers, a.id, 1)).status_code == 200
    res = await _post(async_client, headers, a.id, 3, level=2)
    assert res.status_code == 409 and res.json()["error"]["message"] == "level_locked"
    assert (await _post(async_client, headers, a.id, 2)).status_code == 200
    res = await _post(async_client, headers, a.id, 3, level=2)
    assert res.status_code == 200, res.text
    assert res.json()["level"] == 2 and res.json()["stars_earned"] == 3


async def test_level_three_needs_level_two(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    a = acts[0]
    await add_completion(db_session, student_id, a.id, stars=3)
    res = await _post(async_client, headers, a.id, 3, level=3)
    assert res.status_code == 409 and res.json()["error"]["message"] == "level_locked"
    assert (await _post(async_client, headers, a.id, 2, level=2)).status_code == 200
    res = await _post(async_client, headers, a.id, 1, level=3)
    assert res.status_code == 200 and res.json()["level"] == 3


async def test_level_upsert_keeps_best(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    a = acts[0]
    await add_completion(db_session, student_id, a.id, stars=2)
    assert (await _post(async_client, headers, a.id, 3, level=2)).status_code == 200
    res = await _post(async_client, headers, a.id, 1, level=2)
    assert res.status_code == 200
    assert res.json()["stars_earned"] == 3 and res.json()["attempts"] == 2
    l1 = (await db_session.execute(select(EarlyActivityCompletion).where(
        EarlyActivityCompletion.student_id == student_id,
        EarlyActivityCompletion.activity_id == a.id,
    ))).scalar_one()
    await db_session.refresh(l1)
    assert l1.stars_earned == 2 and l1.attempts == 1
    rows = (await db_session.execute(select(EarlyActivityLevelCompletion).where(
        EarlyActivityLevelCompletion.student_id == student_id,
    ))).scalars().all()
    assert [(r.level, r.stars_earned, r.attempts) for r in rows] == [(2, 3, 2)]


async def test_teacher_skips_lock(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session, role=UserRole.teacher)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    res = await _post(async_client, headers, acts[0].id, 2, level=3)
    assert res.status_code == 200, res.text
    assert res.json()["level"] == 3 and res.json()["stars_earned"] == 2


async def test_level_one_unchanged(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    res = await _post(async_client, headers, acts[0].id, 2)
    assert res.status_code == 200
    body = res.json()
    assert body["level"] == 1 and body["stars_earned"] == 2 and body["attempts"] == 1
    assert body["activity_id"] == acts[0].id
    again = await _post(async_client, headers, acts[0].id, 3, level=1)
    assert again.json()["stars_earned"] == 3 and again.json()["attempts"] == 2


async def test_level_out_of_range_rejected(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    assert (await _post(async_client, headers, acts[0].id, 2, level=4)).status_code == 422
    assert (await _post(async_client, headers, acts[0].id, 2, level=0)).status_code == 422
