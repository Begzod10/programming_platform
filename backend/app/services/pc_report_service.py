"""Teacher progress report for PC Guard: per student per Tashkent day, quota
status plus lab-PC minutes (locked vs unlocked) and top apps."""
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_quota import StudentDailyProgress
from app.models.group import student_groups
from app.models.pc_control import PcSession, PcUsageEvent
from app.models.user import Student
from app.services.daily_quota_service import TZ

TOP_APPS = 5


def _utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _day_start(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=TZ)


async def build_report(db: AsyncSession, date_from: date, date_to: date,
                       group_id: Optional[int]) -> list[dict]:
    start = _day_start(date_from)
    end = _day_start(date_to + timedelta(days=1))
    start_utc, end_utc = start.astimezone(timezone.utc), end.astimezone(timezone.utc)

    allowed: Optional[set[int]] = None
    if group_id is not None:
        allowed = set((await db.execute(
            select(student_groups.c.student_id).where(student_groups.c.group_id == group_id)
        )).scalars().all())
        if not allowed:
            return []

    # 1. sessions in range -> (student, day) keys
    q = select(PcSession.student_id, PcSession.signed_in_at).where(
        PcSession.signed_in_at >= start_utc, PcSession.signed_in_at < end_utc)
    if allowed is not None:
        q = q.where(PcSession.student_id.in_(allowed))
    keys: set[tuple[int, date]] = set()
    for sid, signed_in in (await db.execute(q)).all():
        keys.add((sid, _utc(signed_in).astimezone(TZ).date()))

    # 2. daily progress rows in range
    q = select(StudentDailyProgress).where(
        StudentDailyProgress.quota_date >= date_from, StudentDailyProgress.quota_date <= date_to)
    if allowed is not None:
        q = q.where(StudentDailyProgress.student_id.in_(allowed))
    progress = {(p.student_id, p.quota_date): p for p in (await db.execute(q)).scalars().all()}
    keys.update(progress.keys())

    # 3. usage events overlapping the range, split across Tashkent days
    q = (select(PcSession.student_id, PcUsageEvent.app_name, PcUsageEvent.started_at,
                PcUsageEvent.ended_at, PcUsageEvent.was_locked)
         .join(PcSession, PcSession.id == PcUsageEvent.session_id)
         .where(PcUsageEvent.ended_at.is_not(None),
                PcUsageEvent.started_at < end_utc, PcUsageEvent.ended_at > start_utc))
    if allowed is not None:
        q = q.where(PcSession.student_id.in_(allowed))
    locked_s: dict = defaultdict(float)
    unlocked_s: dict = defaultdict(float)
    app_s: dict = defaultdict(lambda: defaultdict(float))
    for sid, app_name, s, e, was_locked in (await db.execute(q)).all():
        s_loc, e_loc = _utc(s).astimezone(TZ), _utc(e).astimezone(TZ)
        day = max(s_loc.date(), date_from)
        while day <= date_to:
            d0, d1 = _day_start(day), _day_start(day + timedelta(days=1))
            if d0 >= e_loc:
                break
            secs = (min(e_loc, d1) - max(s_loc, d0)).total_seconds()
            if secs > 0:
                (locked_s if was_locked else unlocked_s)[(sid, day)] += secs
                app_s[(sid, day)][app_name] += secs
                keys.add((sid, day))
            day += timedelta(days=1)

    if not keys:
        return []
    names = dict((await db.execute(
        select(Student.id, Student.full_name).where(Student.id.in_({k[0] for k in keys}))
    )).all())

    rows = []
    for sid, day in sorted(keys, key=lambda k: (k[1], k[0])):
        p = progress.get((sid, day))
        apps = sorted(app_s.get((sid, day), {}).items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_APPS]
        rows.append({
            "student_id": sid,
            "full_name": names.get(sid),
            "date": day.isoformat(),
            "quota_met": bool(p.unlocked) if p else False,
            "unlocked_at": _utc(p.unlocked_at).isoformat() if p and p.unlocked_at else None,
            "minutes_locked": round(locked_s.get((sid, day), 0.0) / 60, 1),
            "minutes_unlocked": round(unlocked_s.get((sid, day), 0.0) / 60, 1),
            "top_apps": [{"app": a, "minutes": round(sec / 60, 1)} for a, sec in apps],
        })
    return rows
