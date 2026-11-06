"""The quota shield at end of day: no penalty, no debt, streak kept; once per calendar week; never wasted."""
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import select, func

from app.db.database import AsyncSessionLocal
from app.models.daily_quota import (
    PenaltyLog, QuotaConfig, QuotaShieldUse, StreakTracker, StudentDailyProgress,
)
from app.models.notification import Notification
from app.models.store import StoreItem, StoreItemKind, StudentInventoryItem, AcquiredVia
from app.models.user import Student
from app.services import daily_quota_service as dq
from app.services import notification_service
from app.services.ranking_service import RankingService

MON = date(2026, 11, 2)          # weekday 0, not a rest day
TUE = MON + timedelta(days=1)
SUN = date(2026, 11, 8)          # rest day (Mon=0..Sun=6, rest_days "5,6")
NEXT_MON = date(2026, 11, 9)     # a different calendar week


@pytest.fixture(autouse=True)
def lessons(monkeypatch):
    """`completed` per call is set by the test; plenty of lessons are always available to miss."""
    state = {"completed": 0}

    async def completed(db, student_id, day):
        return state["completed"]

    async def available(db, student_id):
        return 99
    monkeypatch.setattr(dq, "count_completed_on", completed)
    monkeypatch.setattr(dq, "uncompleted_available", available)
    return state


async def _shield_item(db):
    item = (await db.execute(select(StoreItem).where(StoreItem.slug == "quota_shield"))).scalar_one_or_none()
    if item is None:
        item = StoreItem(slug="quota_shield", kind=StoreItemKind.boost, title="Norma himoyasi",
                         title_ru="Защита нормы", price_coins=500, is_active=True,
                         asset_ref={"effect": "quota_shield", "max_owned": 2})
        db.add(item)
        await db.flush()
    return item


async def _student(*, shields=1, streak=5, streak_last=None):
    """A student with `shields` in stock and (if streak) an active quota streak that last qualified `streak_last`."""
    async with AsyncSessionLocal() as db:
        uid = uuid.uuid4().hex[:8]
        s = Student(username=f"qe_{uid}", email=f"qe_{uid}@example.com", hashed_password="x",
                    lifetime_points=1000, total_points=1000)
        db.add(s)
        await db.flush()
        if shields is not None:
            item = await _shield_item(db)
            db.add(StudentInventoryItem(student_id=s.id, store_item_id=item.id, kind=StoreItemKind.boost,
                                        quantity=shields, is_equipped=False, acquired_via=AcquiredVia.purchase))
        if streak:
            db.add(StreakTracker(student_id=s.id, active=True, length=streak, best_length=streak,
                                 started_on=MON - timedelta(days=streak), last_qualified_date=streak_last,
                                 base_points_snapshot=1000))
        await db.commit()
        return s.id


async def _eod(sid, day):
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        result = await dq.process_eod_for_student(db, RankingService(db), student, day)
        await db.commit()
        return result


async def _state(sid, day=None):
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        qty = (await db.execute(select(StudentInventoryItem.quantity).where(
            StudentInventoryItem.student_id == sid))).scalar_one_or_none()
        tracker = (await db.execute(select(StreakTracker).where(StreakTracker.student_id == sid))).scalar_one_or_none()
        penalties = (await db.execute(select(func.count(PenaltyLog.id)).where(PenaltyLog.student_id == sid))).scalar()
        uses = (await db.execute(select(func.count(QuotaShieldUse.id)).where(QuotaShieldUse.student_id == sid))).scalar()
        row = None
        if day:
            row = (await db.execute(select(StudentDailyProgress).where(
                StudentDailyProgress.student_id == sid, StudentDailyProgress.quota_date == day))).scalar_one_or_none()
        return {"points": s.lifetime_points, "qty": qty, "tracker": tracker, "penalties": penalties, "uses": uses, "row": row}


async def test_a_missed_day_with_a_shield_keeps_points_debt_and_streak(lessons):
    sid = await _student(shields=1, streak=5, streak_last=MON - timedelta(days=1))
    result = await _eod(sid, MON)
    st = await _state(sid, MON)
    assert result == {"lessons_missed": 2, "penalty_saved": 200, "streak_length": 5}
    assert st["points"] == 1000 and st["penalties"] == 0
    assert st["row"].penalty_points == 0 and st["row"].carried_out == 0 and st["row"].processed
    assert st["tracker"].active and st["tracker"].length == 5 and st["tracker"].last_qualified_date == MON
    assert st["qty"] == 0 and st["uses"] == 1


async def test_the_streak_carries_on_the_next_day(lessons):
    sid = await _student(shields=1, streak=5, streak_last=MON - timedelta(days=1))
    await _eod(sid, MON)
    lessons["completed"] = 2
    await _eod(sid, TUE)
    st = await _state(sid)
    assert st["tracker"].active and st["tracker"].length == 6


async def test_without_a_shield_nothing_changes(lessons):
    sid = await _student(shields=None, streak=5, streak_last=MON - timedelta(days=1))
    result = await _eod(sid, MON)
    st = await _state(sid, MON)
    assert result is None
    assert st["points"] == 800 and st["penalties"] == 1
    assert st["row"].carried_out == 2
    assert not st["tracker"].active and st["tracker"].length == 0


async def test_only_one_shield_per_calendar_week(lessons):
    sid = await _student(shields=2, streak=5, streak_last=MON - timedelta(days=1))
    assert await _eod(sid, MON) is not None
    assert await _eod(sid, TUE) is None                      # same week: penalised, shield stays
    st = await _state(sid)
    assert st["points"] == 800 and st["qty"] == 1 and st["uses"] == 1
    assert await _eod(sid, NEXT_MON) is not None             # next week it works again
    assert (await _state(sid))["qty"] == 0


async def test_a_rest_day_does_not_spend_a_shield(lessons):
    sid = await _student(shields=1, streak=5, streak_last=SUN - timedelta(days=1))
    assert await _eod(sid, SUN) is None
    assert (await _state(sid))["qty"] == 1


async def test_a_fully_met_day_does_not_spend_a_shield(lessons):
    lessons["completed"] = 2
    sid = await _student(shields=1, streak=5, streak_last=MON - timedelta(days=1))
    assert await _eod(sid, MON) is None
    st = await _state(sid)
    assert st["qty"] == 1 and st["tracker"].length == 6


async def test_grace_period_saves_an_active_streak_but_never_a_streak_that_does_not_exist(lessons):
    async with AsyncSessionLocal() as db:
        cfg = await dq.get_config(db)
        old = cfg.enforce_from
        cfg.enforce_from = date(2030, 1, 1)                  # penalties not enforced yet
        await db.commit()
    try:
        with_streak = await _student(shields=1, streak=5, streak_last=MON - timedelta(days=1))
        no_streak = await _student(shields=1, streak=0)
        assert await _eod(with_streak, MON) is not None
        assert (await _state(with_streak))["tracker"].length == 5
        assert await _eod(no_streak, MON) is None
        assert (await _state(no_streak))["qty"] == 1
    finally:
        async with AsyncSessionLocal() as db:
            cfg = await dq.get_config(db)
            cfg.enforce_from = old
            await db.commit()


async def test_a_penalty_with_no_streak_tracker_is_still_prevented(lessons):
    sid = await _student(shields=1, streak=0)
    result = await _eod(sid, MON)
    st = await _state(sid, MON)
    assert result == {"lessons_missed": 2, "penalty_saved": 200, "streak_length": 0}
    assert st["points"] == 1000 and st["tracker"] is None and st["qty"] == 0


async def test_processing_the_same_day_twice_spends_one_shield(lessons):
    sid = await _student(shields=2, streak=5, streak_last=MON - timedelta(days=1))
    assert await _eod(sid, MON) is not None
    assert await _eod(sid, MON) is None
    st = await _state(sid)
    assert st["qty"] == 1 and st["uses"] == 1


async def test_notify_quota_shield_used_creates_the_notification():
    sid = await _student(shields=None, streak=0)
    async with AsyncSessionLocal() as db:
        await notification_service.notify_quota_shield_used(db, sid, penalty_saved=200, streak_length=5)
    async with AsyncSessionLocal() as db:
        n = (await db.execute(select(Notification).where(
            Notification.student_id == sid, Notification.type == "quota_shield_used"))).scalar_one()
    assert n.tone == "ok" and n.icon == "🛡️" and n.link == "/student/daily-rules"
