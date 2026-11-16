"""Game levels for early-learning activities.

Level 1 is the original game and keeps living in EarlyActivityCompletion /
EarlyActivityDailyStars. Levels 2 and 3 live in the EarlyActivityLevel*
tables. A level opens once the level below it has UNLOCK_STARS stars.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.early_learning import EarlyActivityCompletion, EarlyActivityLevelCompletion

LEVELS = (1, 2, 3)
UNLOCK_STARS = 2


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
