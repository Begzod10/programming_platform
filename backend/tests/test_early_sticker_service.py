"""Award rules and album shape (app/services/early_sticker_service.py)."""
from datetime import date, datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy import func, select, update

from app.models.early_learning import EarlyActivity, EarlyModule, EarlyStickerAward
from app.services import early_sticker_service as svc
from tests._early_helpers import add_completion, add_daily, make_module, make_student, make_teacher

D = date(2026, 11, 11)
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def teacher(async_client, db_session):
    return await make_teacher(async_client, db_session)


@pytest_asyncio.fixture
async def kid(async_client, db_session):
    student_id, _ = await make_student(async_client, db_session)
    return student_id


async def _award_count(db_session, student_id):
    return (await db_session.execute(
        select(func.count()).select_from(EarlyStickerAward).where(EarlyStickerAward.student_id == student_id)
    )).scalar_one()


def _by_key(album):
    return {s["key"]: s for s in album["stickers"]}


async def test_star_thresholds(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=5)
    for a in acts[:3]:
        await add_completion(db_session, kid, a.id)          # 9 stars
    new = await svc.sync_awards(db_session, kid, D)
    assert not [k for k in new if k.startswith("star:")]
    await add_completion(db_session, kid, acts[3].id)        # 12 stars
    assert "star:10" in await svc.sync_awards(db_session, kid, D)


async def test_several_thresholds_at_once(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=8)
    for a in acts:
        await add_completion(db_session, kid, a.id)          # 24 stars
    new = await svc.sync_awards(db_session, kid, D)
    assert {"star:10", "star:20"} <= set(new)
    assert "star:30" not in new


async def test_sync_is_idempotent(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await add_completion(db_session, kid, a.id)
    assert await svc.sync_awards(db_session, kid, D)
    count = await _award_count(db_session, kid)
    assert await svc.sync_awards(db_session, kid, D) == []
    assert await _award_count(db_session, kid) == count


async def test_daily_needs_three_distinct(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=5)
    await add_daily(db_session, kid, acts[0].id, D, attempts=3)   # one game replayed 3 times
    assert not [k for k in await svc.sync_awards(db_session, kid, D) if k.startswith("daily:")]
    await add_daily(db_session, kid, acts[1].id, D)
    assert not [k for k in await svc.sync_awards(db_session, kid, D) if k.startswith("daily:")]
    await add_daily(db_session, kid, acts[2].id, D)
    assert "daily:01" in await svc.sync_awards(db_session, kid, D)


async def test_one_daily_per_day_then_next(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=5)
    for a in acts[:3]:
        await add_daily(db_session, kid, a.id, D)
    assert "daily:01" in await svc.sync_awards(db_session, kid, D)
    await add_daily(db_session, kid, acts[3].id, D)
    assert not [k for k in await svc.sync_awards(db_session, kid, D) if k.startswith("daily:")]
    nxt = D + timedelta(days=1)
    for a in acts[:3]:
        await add_daily(db_session, kid, a.id, nxt)
    assert "daily:02" in await svc.sync_awards(db_session, kid, nxt)


async def _play_day(db_session, kid, acts, day):
    for a in acts[:3]:
        await add_daily(db_session, kid, a.id, day)


async def test_streak(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=3)
    for back in (2, 1, 0):
        await _play_day(db_session, kid, acts, D - timedelta(days=back))
    assert await svc.current_streak(db_session, kid, D) == 3
    assert "streak:3" in await svc.sync_awards(db_session, kid, D)


async def test_streak_alive_from_yesterday(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=3)
    for back in (2, 1):
        await _play_day(db_session, kid, acts, D - timedelta(days=back))
    await add_daily(db_session, kid, acts[0].id, D)
    assert await svc.current_streak(db_session, kid, D) == 2


async def test_streak_broken(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=3)
    for back in (3, 2):
        await _play_day(db_session, kid, acts, D - timedelta(days=back))
    assert await svc.current_streak(db_session, kid, D) == 0


async def test_module_badge(db_session, teacher, kid):
    module, acts = await make_module(db_session, teacher, n_activities=3)
    key = f"module:{module.id}"
    for a in acts[:2]:
        await add_completion(db_session, kid, a.id, stars=1)
    assert key not in await svc.sync_awards(db_session, kid, D)
    await add_completion(db_session, kid, acts[2].id, stars=1)
    assert key in await svc.sync_awards(db_session, kid, D)


async def test_empty_module_gives_no_badge(db_session, teacher, kid):
    module, acts = await make_module(db_session, teacher, n_activities=1)
    await db_session.execute(update(EarlyActivity).where(EarlyActivity.id == acts[0].id).values(is_published=False))
    await db_session.commit()
    assert f"module:{module.id}" not in await svc.sync_awards(db_session, kid, D)
    album = await svc.album(db_session, kid, "uz", D)
    assert f"module:{module.id}" not in _by_key(album)


async def test_owned_sticker_survives_star_drop(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await add_completion(db_session, kid, a.id)          # 12 stars
    assert "star:10" in await svc.sync_awards(db_session, kid, D)
    await db_session.execute(update(EarlyActivity).where(EarlyActivity.id == acts[0].id).values(is_published=False))
    await db_session.commit()                                 # 9 stars now
    assert await svc.sync_awards(db_session, kid, D) == []
    album = await svc.album(db_session, kid, "uz", D)
    assert _by_key(album)["star:10"]["owned"] is True
    assert album["next_star"] == {"at": 20, "have": 9}


async def test_daily_pool_exhausted(db_session, teacher, kid, monkeypatch):
    monkeypatch.setattr(svc, "DAILY_STICKERS", svc.DAILY_STICKERS[:1])
    db_session.add(EarlyStickerAward(student_id=kid, sticker_key="daily:01", daily_date=D - timedelta(days=5)))
    await db_session.commit()
    _, acts = await make_module(db_session, teacher, n_activities=4)
    await _play_day(db_session, kid, acts, D)
    assert await svc.sync_awards(db_session, kid, D) == []
    album = await svc.album(db_session, kid, "uz", D)
    assert album["today"] == {"played": 3, "needed": 3, "earned": True}


async def test_album_shape_and_hints(db_session, teacher, kid):
    module, _ = await make_module(db_session, teacher, n_activities=1, title_ru="Модуль")
    live = (await db_session.execute(
        select(func.count(func.distinct(EarlyModule.id)))
        .join(EarlyActivity, EarlyActivity.module_id == EarlyModule.id)
        .where(EarlyModule.is_published.is_(True), EarlyModule.is_active.is_(True),
               EarlyActivity.is_published.is_(True), EarlyActivity.is_active.is_(True))
    )).scalar_one()
    album = await svc.album(db_session, kid, "uz", D)
    assert album["owned_count"] == 0
    assert album["total"] == 81 + live
    assert album["streak"] == 0
    assert album["today"] == {"played": 0, "needed": 3, "earned": False}
    assert album["next_star"] == {"at": 10, "have": 0}
    first = album["stickers"][0]
    assert first["key"] == "star:10" and first["owned"] is False and first["is_new"] is False
    assert first["hint"] == "10 yulduz yig'"
    stickers = _by_key(album)
    assert stickers["daily:01"]["hint"] == "Bir kunda 3 ta o'yin o'yna"
    assert stickers["streak:7"]["hint"] == "7 kun ketma-ket o'yna"
    assert stickers[f"module:{module.id}"]["hint"] == f"«{module.title}»ni tugat"
    assert stickers[f"module:{module.id}"]["rarity"] == "rare"
    kinds = [s["kind"] for s in album["stickers"]]
    assert kinds == sorted(kinds, key=["star", "daily", "streak", "module"].index)

    ru = _by_key(await svc.album(db_session, kid, "ru", D))
    assert ru["star:10"]["hint"] == "Собери 10 звёзд"
    assert ru["star:10"]["name"] == "Кошка"
    assert ru["daily:01"]["hint"] == "Сыграй 3 игры за день"
    assert ru["streak:7"]["hint"] == "Играй 7 дней подряд"
    assert ru[f"module:{module.id}"]["hint"] == "Пройди «Модуль»"
    assert ru[f"module:{module.id}"]["name"] == "Модуль"


async def test_album_marks_new_until_seen(db_session, teacher, kid):
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await add_completion(db_session, kid, a.id)
    await svc.sync_awards(db_session, kid, D)
    sticker = _by_key(await svc.album(db_session, kid, "uz", D))["star:10"]
    assert sticker["owned"] is True and sticker["is_new"] is True and sticker["hint"] is None
    await db_session.execute(
        update(EarlyStickerAward).where(EarlyStickerAward.student_id == kid)
        .values(seen_at=datetime.now(timezone.utc))
    )
    await db_session.commit()
    assert _by_key(await svc.album(db_session, kid, "uz", D))["star:10"]["is_new"] is False


async def test_sticker_payload(db_session, teacher):
    module, _ = await make_module(db_session, teacher, n_activities=1, title_ru="Модуль", icon_emoji="🎨")
    bare, _ = await make_module(db_session, teacher, n_activities=1)
    out = await svc.sticker_payload(db_session, ["star:50", f"module:{module.id}", f"module:{bare.id}", "nope:1"])
    assert out[0] == {"key": "star:50", "emoji": "🦁", "name": "Sher", "name_ru": "Лев", "kind": "star", "rarity": "rare"}
    assert out[1] == {"key": f"module:{module.id}", "emoji": "🎨", "name": module.title, "name_ru": "Модуль",
                      "kind": "module", "rarity": "rare"}
    assert out[2]["emoji"] == "🏅" and out[2]["name_ru"] == bare.title
    assert len(out) == 3


async def test_duplicate_insert_is_swallowed(db_session, kid):
    """What a concurrent request racing this one looks like: the unique
    constraint fires, the award is reported as not-new, the session survives."""
    assert await svc._insert(db_session, kid, "star:10") is True
    assert await svc._insert(db_session, kid, "star:10") is False
    assert await svc._insert(db_session, kid, "daily:01", daily_date=D) is True
    assert await svc._insert(db_session, kid, "daily:02", daily_date=D) is False
    await db_session.commit()
    assert await _award_count(db_session, kid) == 2


async def test_module_filter_hides_badge(db_session, teacher, kid):
    """A module the student may not open (age gate) must not show up as an
    uncollectable badge, nor be awarded."""
    module, acts = await make_module(db_session, teacher, n_activities=1)
    await add_completion(db_session, kid, acts[0].id)
    key = f"module:{module.id}"
    hide = lambda m: m.id != module.id
    assert key not in await svc.sync_awards(db_session, kid, D, module_ok=hide)
    hidden = await svc.album(db_session, kid, "uz", D, module_ok=hide)
    shown = await svc.album(db_session, kid, "uz", D)
    assert key not in _by_key(hidden) and key in _by_key(shown)
    assert hidden["total"] == shown["total"] - 1


async def test_sync_with_stale_owned_snapshot(db_session, teacher, kid, monkeypatch):
    """The shape of a real race: this request read "owns nothing" while a
    parallel one already inserted the rows."""
    _, acts = await make_module(db_session, teacher, n_activities=4)
    for a in acts:
        await add_completion(db_session, kid, a.id)
        await add_daily(db_session, kid, a.id, D)
    first = await svc.sync_awards(db_session, kid, D)
    assert "star:10" in first and "daily:01" in first
    count = await _award_count(db_session, kid)

    async def stale(db, student_id):
        return {}

    real_owned = svc._owned
    monkeypatch.setattr(svc, "_owned", stale)
    assert await svc.sync_awards(db_session, kid, D) == []
    monkeypatch.setattr(svc, "_owned", real_owned)
    assert await _award_count(db_session, kid) == count
    assert _by_key(await svc.album(db_session, kid, "uz", D))["star:10"]["owned"] is True


async def test_russian_streak_hint_grammar(db_session, kid):
    ru = _by_key(await svc.album(db_session, kid, "ru", D))
    assert ru["streak:3"]["hint"] == "Играй 3 дня подряд"
    assert ru["streak:14"]["hint"] == "Играй 14 дней подряд"
