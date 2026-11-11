"""Sticker awards for the kids' games: who is entitled to what, and the
album the frontend renders.

Everything is derived from the two existing completion tables — nothing
here changes how stars are recorded. `today` is always passed in by the
caller (the endpoints use their own UTC `_today()`), which keeps the day
boundary in one place and the rules testable.

  star    total stars >= threshold                       (never revoked)
  daily   DAILY_PLAYS_NEEDED distinct activities today → the first daily
          sticker the student does not own; one per day
  streak  consecutive "play days" (same DAILY_PLAYS_NEEDED rule)
  module  every visible activity of a live module completed
"""
from datetime import date, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.early_learning import (
    EarlyActivity, EarlyActivityCompletion, EarlyActivityDailyStars,
    EarlyModule, EarlyStickerAward,
)
from app.services.early_sticker_catalog import (
    CATALOG, DAILY_PLAYS_NEEDED, DAILY_STICKERS, STAR_STICKERS, STREAK_STICKERS,
)

MODULE_FALLBACK_EMOJI = "🏅"

_HINTS = {
    "star": ("{n} yulduz yig'", "Собери {n} звёзд"),
    "daily": ("Bir kunda {n} ta o'yin o'yna", "Сыграй {n} игры за день"),
    "streak": ("{n} kun ketma-ket o'yna", "Играй {n} дней подряд"),
    "module": ("«{n}»ni tugat", "Пройди «{n}»"),
}


def _hint(kind: str, n, lang: str) -> str:
    uz, ru = _HINTS[kind]
    return (ru if lang == "ru" else uz).format(n=n)


def _threshold(key: str) -> int:
    return int(key.split(":", 1)[1])


def _visible(module: EarlyModule) -> List[EarlyActivity]:
    return [a for a in module.activities if a.is_active and a.is_published]


async def _live_modules(db: AsyncSession) -> List[EarlyModule]:
    """Published, active modules that have at least one visible activity."""
    modules = (
        await db.execute(
            select(EarlyModule)
            .where(EarlyModule.is_published.is_(True), EarlyModule.is_active.is_(True))
            .options(selectinload(EarlyModule.activities))
            .order_by(EarlyModule.display_order, EarlyModule.id)
            .execution_options(populate_existing=True)
        )
    ).scalars().all()
    return [m for m in modules if _visible(m)]


async def _owned(db: AsyncSession, student_id: int) -> Dict[str, EarlyStickerAward]:
    rows = (
        await db.execute(
            select(EarlyStickerAward)
            .where(EarlyStickerAward.student_id == student_id)
            .execution_options(populate_existing=True)
        )
    ).scalars().all()
    return {row.sticker_key: row for row in rows}


async def total_stars(db: AsyncSession, student_id: int) -> int:
    total = (
        await db.execute(
            select(func.coalesce(func.sum(EarlyActivityCompletion.stars_earned), 0))
            .join(EarlyActivity, EarlyActivity.id == EarlyActivityCompletion.activity_id)
            .join(EarlyModule, EarlyModule.id == EarlyActivity.module_id)
            .where(
                EarlyActivityCompletion.student_id == student_id,
                EarlyActivity.is_published.is_(True), EarlyActivity.is_active.is_(True),
                EarlyModule.is_published.is_(True), EarlyModule.is_active.is_(True),
            )
        )
    ).scalar_one()
    return int(total or 0)


async def plays_on(db: AsyncSession, student_id: int, day: date) -> int:
    """Distinct activities played that day (one daily row per activity)."""
    return (
        await db.execute(
            select(func.count()).select_from(EarlyActivityDailyStars).where(
                EarlyActivityDailyStars.student_id == student_id,
                EarlyActivityDailyStars.activity_date == day,
            )
        )
    ).scalar_one()


async def current_streak(db: AsyncSession, student_id: int, today: date) -> int:
    """Consecutive play days ending today — or yesterday, when today is not
    a play day yet (the streak is still alive until the day is over)."""
    days = set(
        (
            await db.execute(
                select(EarlyActivityDailyStars.activity_date)
                .where(
                    EarlyActivityDailyStars.student_id == student_id,
                    EarlyActivityDailyStars.activity_date <= today,
                )
                .group_by(EarlyActivityDailyStars.activity_date)
                .having(func.count() >= DAILY_PLAYS_NEEDED)
            )
        ).scalars().all()
    )
    day = today if today in days else today - timedelta(days=1)
    streak = 0
    while day in days:
        streak += 1
        day -= timedelta(days=1)
    return streak


async def _finished_module_keys(db: AsyncSession, student_id: int, modules: List[EarlyModule]) -> List[str]:
    done = set(
        (
            await db.execute(
                select(EarlyActivityCompletion.activity_id)
                .where(EarlyActivityCompletion.student_id == student_id)
            )
        ).scalars().all()
    )
    return [f"module:{m.id}" for m in modules if all(a.id in done for a in _visible(m))]


async def _insert(db: AsyncSession, student_id: int, key: str, daily_date: Optional[date] = None) -> bool:
    """Insert one award in its own savepoint; a concurrent request that got
    there first trips a unique constraint, which just means "already owned"."""
    try:
        async with db.begin_nested():
            db.add(EarlyStickerAward(student_id=student_id, sticker_key=key, daily_date=daily_date))
        return True
    except IntegrityError:
        return False


async def sync_awards(db: AsyncSession, student_id: int, today: date) -> List[str]:
    """Grant every sticker the student is entitled to but does not own yet.
    Returns the newly granted keys. Commits."""
    owned = await _owned(db, student_id)
    stars = await total_stars(db, student_id)
    streak = await current_streak(db, student_id, today)
    modules = await _live_modules(db)

    wanted = [s.key for s in STAR_STICKERS if _threshold(s.key) <= stars]
    wanted += [s.key for s in STREAK_STICKERS if _threshold(s.key) <= streak]
    wanted += await _finished_module_keys(db, student_id, modules)

    new: List[str] = []
    for key in wanted:
        if key not in owned and await _insert(db, student_id, key):
            new.append(key)

    has_daily_today = any(a.daily_date == today for a in owned.values())
    if not has_daily_today and await plays_on(db, student_id, today) >= DAILY_PLAYS_NEEDED:
        nxt = next((s for s in DAILY_STICKERS if s.key not in owned), None)
        if nxt is not None and await _insert(db, student_id, nxt.key, daily_date=today):
            new.append(nxt.key)

    await db.commit()
    return new


def _module_fields(module: EarlyModule) -> dict:
    return {
        "key": f"module:{module.id}",
        "emoji": module.icon_emoji or MODULE_FALLBACK_EMOJI,
        "name": module.title,
        "name_ru": module.title_ru or module.title,
        "kind": "module",
        "rarity": "rare",
    }


def _catalog_fields(key: str) -> dict:
    s = CATALOG[key]
    return {"key": s.key, "emoji": s.emoji, "name": s.name, "name_ru": s.name_ru,
            "kind": s.kind, "rarity": s.rarity}


async def sticker_payload(db: AsyncSession, keys: List[str]) -> List[dict]:
    """{key, emoji, name, name_ru, kind, rarity} per key; unknown keys are skipped."""
    module_ids = [int(k.split(":", 1)[1]) for k in keys if k.startswith("module:") and k[7:].isdigit()]
    modules = {}
    if module_ids:
        rows = (await db.execute(select(EarlyModule).where(EarlyModule.id.in_(module_ids)))).scalars().all()
        modules = {f"module:{m.id}": m for m in rows}
    out = []
    for key in keys:
        if key in CATALOG:
            out.append(_catalog_fields(key))
        elif key in modules:
            out.append(_module_fields(modules[key]))
    return out


async def album(db: AsyncSession, student_id: int, lang: str, today: date) -> dict:
    owned = await _owned(db, student_id)
    modules = await _live_modules(db)
    stars = await total_stars(db, student_id)
    played = await plays_on(db, student_id, today)

    def entry(fields: dict, hint: str) -> dict:
        award = owned.get(fields["key"])
        return {
            "key": fields["key"],
            "emoji": fields["emoji"],
            "name": fields["name_ru"] if lang == "ru" else fields["name"],
            "kind": fields["kind"],
            "rarity": fields["rarity"],
            "owned": award is not None,
            "is_new": award is not None and award.seen_at is None,
            "hint": None if award is not None else hint,
        }

    stickers = [entry(_catalog_fields(s.key), _hint("star", _threshold(s.key), lang)) for s in STAR_STICKERS]
    stickers += [entry(_catalog_fields(s.key), _hint("daily", DAILY_PLAYS_NEEDED, lang)) for s in DAILY_STICKERS]
    stickers += [entry(_catalog_fields(s.key), _hint("streak", _threshold(s.key), lang)) for s in STREAK_STICKERS]
    for m in modules:
        fields = _module_fields(m)
        stickers.append(entry(fields, _hint("module", fields["name_ru"] if lang == "ru" else fields["name"], lang)))

    next_star = next((s for s in STAR_STICKERS if s.key not in owned), None)
    has_daily_today = any(a.daily_date == today for a in owned.values())
    all_daily_owned = all(s.key in owned for s in DAILY_STICKERS)
    return {
        "owned_count": sum(1 for s in stickers if s["owned"]),
        "total": len(stickers),
        "streak": await current_streak(db, student_id, today),
        "today": {
            "played": played,
            "needed": DAILY_PLAYS_NEEDED,
            "earned": has_daily_today or (all_daily_owned and played >= DAILY_PLAYS_NEEDED),
        },
        "next_star": {"at": _threshold(next_star.key), "have": stars} if next_star else None,
        "stickers": stickers,
    }
