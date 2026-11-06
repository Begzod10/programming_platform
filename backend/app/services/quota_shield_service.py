"""Quota shield: spend one stored shield to save a missed day (no penalty, no debt, streak kept).

Called from daily_quota_service.process_eod_for_student. The stock is the `quantity` of the student's
inventory row for the `quota_shield` store item; at most one shield is spent per calendar week
(Monday-Sunday of the quota day). The caller owns the transaction.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_quota import QuotaShieldUse
from app.models.store import StoreItem, StudentInventoryItem
from app.models.user import Student
from app.services.wallet_service import QUOTA_SHIELD_SLUG


def week_bounds(day: date) -> tuple[date, date]:
    """The Monday and the Sunday of the calendar week `day` falls in."""
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


async def try_use_shield(db: AsyncSession, student_id: int, day: date, *,
                         lessons_missed: int, penalty_saved: int, streak_length: int) -> bool:
    """Spend one shield for `day` if the student has one and has not used one this calendar week.

    True: the stock went down by one and a QuotaShieldUse row was added (flushed, not committed).
    False: nothing changed."""
    # Same lock order as a purchase (Student, then the inventory row) so the two can never deadlock.
    await db.execute(select(Student.id).where(Student.id == student_id).with_for_update())
    row = (await db.execute(
        select(StudentInventoryItem)
        .join(StoreItem, StoreItem.id == StudentInventoryItem.store_item_id)
        .where(StudentInventoryItem.student_id == student_id, StoreItem.slug == QUOTA_SHIELD_SLUG)
        .with_for_update(of=StudentInventoryItem)
    )).scalar_one_or_none()
    if row is None or row.quantity < 1:
        return False

    monday, sunday = week_bounds(day)
    used_this_week = (await db.execute(
        select(QuotaShieldUse.id).where(
            QuotaShieldUse.student_id == student_id,
            QuotaShieldUse.quota_date >= monday, QuotaShieldUse.quota_date <= sunday,
        ).limit(1)
    )).first()
    if used_this_week is not None:
        return False

    row.quantity -= 1
    db.add(QuotaShieldUse(student_id=student_id, quota_date=day, lessons_missed=lessons_missed,
                          penalty_saved=penalty_saved, streak_length=streak_length))
    await db.flush()
    return True
