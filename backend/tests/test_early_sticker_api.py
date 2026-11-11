"""Sticker endpoints: new_stickers on completion, the album, "seen"."""
import pytest
import pytest_asyncio
from sqlalchemy import func, select

from app.models.early_learning import EarlyStickerAward
from app.models.user import UserRole
from tests._early_helpers import add_completion, make_module, make_student, make_teacher

pytestmark = pytest.mark.asyncio
BASE = "/api/v1/early-learning"


@pytest.fixture(autouse=True)
def _games_unlocked():
    """These tests exercise stickers, not the daily-quota gate."""
    from app.main import app
    from app.dependencies import require_games_unlocked
    app.dependency_overrides[require_games_unlocked] = lambda: None
    yield
    app.dependency_overrides.pop(require_games_unlocked, None)


@pytest_asyncio.fixture
async def teacher(async_client, db_session):
    return await make_teacher(async_client, db_session)


async def _complete(async_client, headers, activity_id, stars=3):
    res = await async_client.post(f"{BASE}/activities/{activity_id}/complete", json={"stars": stars}, headers=headers)
    assert res.status_code == 200, res.text
    return res.json()


def _by_key(album):
    return {s["key"]: s for s in album["stickers"]}


async def test_complete_returns_new_stickers(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=5)
    for a in acts[:3]:
        body = await _complete(async_client, headers, a.id)
        assert "star:10" not in [s["key"] for s in body["new_stickers"]]
    body = await _complete(async_client, headers, acts[3].id)
    star = next(s for s in body["new_stickers"] if s["key"] == "star:10")
    assert star == {"key": "star:10", "emoji": "🐱", "name": "Mushuk", "name_ru": "Кошка",
                    "kind": "star", "rarity": "common"}
    assert body["stars_earned"] == 3 and body["activity_id"] == acts[3].id
    again = await _complete(async_client, headers, acts[3].id)
    assert again["new_stickers"] == []


async def test_third_game_of_the_day_gives_daily_sticker(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=5)
    first = await _complete(async_client, headers, acts[0].id, stars=1)
    second = await _complete(async_client, headers, acts[1].id, stars=1)
    assert first["new_stickers"] == [] and second["new_stickers"] == []
    third = await _complete(async_client, headers, acts[2].id, stars=1)
    assert [s["key"] for s in third["new_stickers"]] == ["daily:01"]


async def test_complete_survives_sticker_failure(async_client, db_session, teacher, monkeypatch):
    from app.api.v1.endpoints import early_learning as endpoints

    async def boom(*args, **kwargs):
        raise RuntimeError("sticker service down")

    monkeypatch.setattr(endpoints, "sync_awards", boom)
    _, headers = await make_student(async_client, db_session)
    module, acts = await make_module(db_session, teacher, n_activities=1)
    body = await _complete(async_client, headers, acts[0].id, stars=2)
    assert body["new_stickers"] == [] and body["stars_earned"] == 2
    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    assert detail["earned_stars"] == 2


async def test_album_backfills_existing_player(async_client, db_session, teacher):
    student_id, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await add_completion(db_session, student_id, a.id)   # earned before stickers existed
    res = await async_client.get(f"{BASE}/stickers", headers=headers)
    assert res.status_code == 200, res.text
    album = res.json()
    assert _by_key(album)["star:10"]["owned"] is True
    assert _by_key(album)["star:10"]["is_new"] is True
    assert album["owned_count"] >= 2                          # star:10 + the finished module
    assert album["next_star"] == {"at": 20, "have": 12}


async def test_awards_stay_new_until_seen(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await _complete(async_client, headers, a.id)
    album = (await async_client.get(f"{BASE}/stickers", headers=headers)).json()
    assert _by_key(album)["star:10"]["is_new"] is True
    seen = await async_client.post(f"{BASE}/stickers/seen", headers=headers)
    assert seen.status_code == 200 and seen.json()["marked"] >= 1
    album = (await async_client.get(f"{BASE}/stickers", headers=headers)).json()
    assert not [s for s in album["stickers"] if s["is_new"]]
    assert (await async_client.post(f"{BASE}/stickers/seen", headers=headers)).json() == {"marked": 0}


async def test_album_lang(async_client, db_session):
    _, headers = await make_student(async_client, db_session)
    ru = (await async_client.get(f"{BASE}/stickers?lang=ru", headers=headers)).json()
    assert _by_key(ru)["star:10"]["hint"] == "Собери 10 звёзд"
    uz = (await async_client.get(f"{BASE}/stickers", headers=headers)).json()
    assert _by_key(uz)["star:10"]["hint"] == "10 yulduz yig'"
    assert (await async_client.get(f"{BASE}/stickers?lang=xx", headers=headers)).status_code == 422


async def test_teacher_gets_album_but_no_awards(async_client, db_session, teacher):
    viewer_id, headers = await make_student(async_client, db_session, role=UserRole.teacher)
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        assert (await _complete(async_client, headers, a.id))["new_stickers"] == []
    res = await async_client.get(f"{BASE}/stickers", headers=headers)
    assert res.status_code == 200 and res.json()["owned_count"] == 0
    rows = (await db_session.execute(
        select(func.count()).select_from(EarlyStickerAward).where(EarlyStickerAward.student_id == viewer_id)
    )).scalar_one()
    assert rows == 0


async def test_stickers_require_auth(async_client):
    assert (await async_client.get(f"{BASE}/stickers")).status_code in (401, 403)
    assert (await async_client.post(f"{BASE}/stickers/seen")).status_code in (401, 403)
