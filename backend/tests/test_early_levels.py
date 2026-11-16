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


# ---- Task 2: reading levels back ------------------------------------------

async def _add_level(db_session, student_id, activity_id, level, stars, day=None):
    from app.models.early_learning import EarlyActivityLevelDailyStars
    db_session.add(EarlyActivityLevelCompletion(
        student_id=student_id, activity_id=activity_id, level=level, stars_earned=stars, attempts=1,
    ))
    if day is not None:
        db_session.add(EarlyActivityLevelDailyStars(
            student_id=student_id, activity_id=activity_id, level=level, activity_date=day,
            stars_earned=stars, attempts=1,
        ))
    await db_session.commit()


def _levels(activity):
    return [(lv["level"], lv["best_stars"], lv["attempts"], lv["unlocked"]) for lv in activity["levels"]]


async def test_activity_levels_in_detail(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    module, acts = await make_module(db_session, teacher, n_activities=1)
    await add_completion(db_session, student_id, acts[0].id, stars=2)
    await _add_level(db_session, student_id, acts[0].id, 2, 1)
    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    act = detail["activities"][0]
    assert _levels(act) == [(1, 2, 1, True), (2, 1, 1, True), (3, 0, 0, False)]
    assert act["best_stars"] == 2 and act["attempts"] == 1


async def test_teacher_sees_all_unlocked(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session, role=UserRole.teacher)
    module, _ = await make_module(db_session, teacher, n_activities=1)
    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    assert [lv["unlocked"] for lv in detail["activities"][0]["levels"]] == [True, True, True]


async def test_public_detail_levels_locked(async_client, db_session, teacher):
    module, _ = await make_module(db_session, teacher, n_activities=1)
    detail = (await async_client.get(f"{BASE}/public/modules/{module.id}")).json()
    assert _levels(detail["activities"][0]) == [(1, 0, 0, True), (2, 0, 0, False), (3, 0, 0, False)]
    assert detail["max_level_plays"] == 3 and detail["level_plays"] == 0 and detail["max_stars"] == 9


async def test_list_counts_levels(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    module, acts = await make_module(db_session, teacher, n_activities=2)
    await _post(async_client, headers, acts[0].id, 3)
    await _post(async_client, headers, acts[1].id, 2)
    assert (await _post(async_client, headers, acts[0].id, 1, level=2)).status_code == 200
    items = (await async_client.get(f"{BASE}/modules", headers=headers)).json()
    item = next(i for i in items if i["id"] == module.id)
    assert item["max_stars"] == 18
    assert item["earned_stars"] == 6
    assert item["earned_stars_today"] == 6
    assert item["level_plays"] == 3 and item["max_level_plays"] == 6
    assert item["completed_count"] == 2
    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    assert detail["earned_stars"] == 6 and detail["level_plays"] == 3
    assert detail["activities"][0]["today_stars"] == 4


async def test_total_stars_and_leaderboards_include_levels(async_client, db_session, teacher):
    from app.services.early_sticker_service import total_stars
    student_id, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=1)
    await _post(async_client, headers, acts[0].id, 3)
    await _post(async_client, headers, acts[0].id, 2, level=2)
    await _post(async_client, headers, acts[0].id, 1, level=3)
    assert await total_stars(db_session, student_id) == 6
    for period in ("all_time", "today"):
        board = (await async_client.get(f"{BASE}/leaderboard?period={period}", headers=headers)).json()
        me = next(e for e in board["entries"] if e["is_me"])
        assert me["total_stars"] == 6, period


async def test_plays_on_counts_activity_once(async_client, db_session, teacher):
    from app.api.v1.endpoints.early_learning import _today
    from app.services.early_sticker_service import current_streak, plays_on
    student_id, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=3)
    await _post(async_client, headers, acts[0].id, 3)
    await _post(async_client, headers, acts[0].id, 3, level=2)
    assert await plays_on(db_session, student_id, _today()) == 1
    # A level-2-only play still counts as one play of that activity that day.
    await add_completion(db_session, student_id, acts[1].id, stars=3)
    await _add_level(db_session, student_id, acts[1].id, 2, 3, day=_today())
    assert await plays_on(db_session, student_id, _today()) == 2
    await _post(async_client, headers, acts[2].id, 1)
    assert await plays_on(db_session, student_id, _today()) == 3
    assert await current_streak(db_session, student_id, _today()) == 1


# ---- games that cannot get harder keep one level ---------------------------

def test_levels_for_modes():
    from app.services.early_levels import levels_for
    assert levels_for("maze") == 3 and levels_for("select") == 3 and levels_for(None) == 3
    assert levels_for("trace") == 3 and levels_for("pattern") == 3
    for mode in ("sort", "sequence", "build", "pairs", "typing", "wordbuild", "puzzle"):
        assert levels_for(mode) == 1
    assert levels_for("unknown-mode") == 1


async def test_one_level_game_has_one_level_everywhere(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    module, (sort_a, maze_a) = await make_module(db_session, teacher, n_activities=2, modes=["sort", "maze"])
    await add_completion(db_session, student_id, sort_a.id, stars=3)

    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    by_id = {a["id"]: a for a in detail["activities"]}
    assert [l["level"] for l in by_id[sort_a.id]["levels"]] == [1]
    assert len(by_id[maze_a.id]["levels"]) == 3

    listed = next(m for m in (await async_client.get(f"{BASE}/modules", headers=headers)).json() if m["id"] == module.id)
    assert listed["max_stars"] == 3 * 1 + 3 * 3
    assert listed["max_level_plays"] == 1 + 3
    assert listed["level_plays"] == 1

    public = (await async_client.get(f"{BASE}/public/modules/{module.id}")).json()
    assert len({a["id"]: a for a in public["activities"]}[sort_a.id]["levels"]) == 1


async def test_one_level_game_rejects_level_two_even_for_teacher(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    _, (sort_a,) = await make_module(db_session, teacher, n_activities=1, modes=["sort"])
    await add_completion(db_session, student_id, sort_a.id, stars=3)
    res = await _post(async_client, headers, sort_a.id, 3, level=2)
    assert res.status_code == 409 and res.json()["error"]["message"] == "level_locked"
    _, t_headers = await make_student(async_client, db_session, role=UserRole.teacher)
    res = await _post(async_client, t_headers, sort_a.id, 3, level=3)
    assert res.status_code == 409
