"""Game levels for early-learning activities.

Level 1 is the original game and keeps living in EarlyActivityCompletion /
EarlyActivityDailyStars. Levels 2 and 3 live in the EarlyActivityLevel*
tables. A level opens once the level below it has UNLOCK_STARS stars.
"""
from datetime import date
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.early_learning import (
    EarlyActivityCompletion, EarlyActivityLevelCompletion, EarlyActivityLevelDailyStars,
)

LEVELS = (1, 2, 3)
UNLOCK_STARS = 2

# Game types whose levels 2-3 really are harder (frontend levelContent.js
# changes their content or, for trace, their scoring). Every other type
# keeps level 1 only: replaying the same game must not earn extra stars.
# Keep in step with LEVELED_MODES in frontend levelContent.js.
LEVELED_MODES = frozenset({
    "select", "maze", "count", "compare", "bubbles", "arithmetic", "rounds", "keyboard",
    "hangman", "simon", "merge", "sudoku", "chart", "trace", "pattern", "cause_effect",
})


def levels_for(mode) -> int:
    """How many levels a game of this mode has (3, or 1). No mode = select."""
    mode = mode or "select"
    return len(LEVELS) if isinstance(mode, str) and mode in LEVELED_MODES else 1


async def best_stars_at(db: AsyncSession, student_id: int, activity_id: int, level: int) -> int:
    """Best stars the student has at `level` of the activity (0 if never played)."""
    if level == 1:
        stmt = select(EarlyActivityCompletion.stars_earned).where(
            EarlyActivityCompletion.student_id == student_id,
            EarlyActivityCompletion.activity_id == activity_id,
        )
    else:
        stmt = select(EarlyActivityLevelCompletion.stars_earned).where(
            EarlyActivityLevelCompletion.student_id == student_id,
            EarlyActivityLevelCompletion.activity_id == activity_id,
            EarlyActivityLevelCompletion.level == level,
        )
    return (await db.execute(stmt)).scalar_one_or_none() or 0


async def level_rows(
    db: AsyncSession, student_id: int, activity_ids: List[int]
) -> Dict[int, Dict[int, EarlyActivityLevelCompletion]]:
    """Level 2/3 best-attempt rows: {activity_id: {level: row}}."""
    if not activity_ids:
        return {}
    rows = (
        await db.execute(
            select(EarlyActivityLevelCompletion).where(
                EarlyActivityLevelCompletion.student_id == student_id,
                EarlyActivityLevelCompletion.activity_id.in_(activity_ids),
            )
        )
    ).scalars().all()
    out: Dict[int, Dict[int, EarlyActivityLevelCompletion]] = {}
    for row in rows:
        out.setdefault(row.activity_id, {})[row.level] = row
    return out


async def level_daily(
    db: AsyncSession, student_id: int, activity_ids: List[int], day: date
) -> Dict[int, Dict[int, EarlyActivityLevelDailyStars]]:
    """Level 2/3 rows for one day: {activity_id: {level: row}}."""
    if not activity_ids:
        return {}
    rows = (
        await db.execute(
            select(EarlyActivityLevelDailyStars).where(
                EarlyActivityLevelDailyStars.student_id == student_id,
                EarlyActivityLevelDailyStars.activity_id.in_(activity_ids),
                EarlyActivityLevelDailyStars.activity_date == day,
            )
        )
    ).scalars().all()
    out: Dict[int, Dict[int, EarlyActivityLevelDailyStars]] = {}
    for row in rows:
        out.setdefault(row.activity_id, {})[row.level] = row
    return out


def levels_payload(level_one, higher: Dict[int, object] | None, unlock_all: bool, count: int = 3) -> List[dict]:
    """The EarlyLevelOut dicts (`count` of them: 3, or 1 for a game that
    cannot get harder) for one activity. `level_one` is the
    EarlyActivityCompletion row (or None), `higher` the {level: row} map."""
    higher = higher or {}
    out = []
    prev_best = None
    for level in LEVELS[:count]:
        row = level_one if level == 1 else higher.get(level)
        best = row.stars_earned if row else 0
        out.append({
            "level": level,
            "best_stars": best,
            "attempts": row.attempts if row else 0,
            "unlocked": level == 1 or unlock_all or (prev_best or 0) >= UNLOCK_STARS,
        })
        prev_best = best
    return out
