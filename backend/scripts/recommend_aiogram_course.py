"""One-off: tell students who already know Python about the aiogram (Telegram bot) course.

Audience: Python-area ratio >= MIN_PYTHON_RATIO and no progress in the aiogram area.
Students who already got this notification are skipped, so the script is safe to re-run.

    python scripts/recommend_aiogram_course.py            # dry-run: counts and the text
    python scripts/recommend_aiogram_course.py --apply    # create the notifications
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.user import Student  # noqa: E402
from app.services.notification_service import _emit  # noqa: E402
from app.services.team_project_skills import build_skill_levels  # noqa: E402

NOTE_TYPE = "course_recommendation"
MIN_PYTHON_RATIO = 0.3
COURSE_TITLE = "Telegram Bot aiogram"
TITLE = "Yangi kurs: Telegram bot yozing 🤖"
BODY = ("Python'ni bilasiz — endi o'zingizning Telegram botingizni yozing. "
        "«Telegram Bot aiogram» kursida buyruqlar, tugmalar va FSM bilan ishlaydigan bot qurasiz.")
EXTRA = "Telegram Bot aiogram"


async def main(apply: bool) -> None:
    async with AsyncSessionLocal() as db:
        course_id = (await db.execute(
            select(Course.id).where(Course.title == COURSE_TITLE, Course.is_published == True)  # noqa: E712
        )).scalar_one_or_none()
        if course_id is None:
            print(f"published course {COURSE_TITLE!r} not found"); return
        ids = (await db.execute(select(Student.id))).scalars().all()
        levels = await build_skill_levels(db, ids)
        already = set((await db.execute(
            select(Notification.student_id).where(Notification.type == NOTE_TYPE, Notification.extra == EXTRA)
        )).scalars().all())
        audience = [s for s, v in levels.items()
                    if v["python"].ratio >= MIN_PYTHON_RATIO and v["aiogram"].ratio == 0 and s not in already]
        print(f"students={len(ids)} python>={MIN_PYTHON_RATIO}&aiogram=0 -> {len(audience)} "
              f"(already notified: {len(already)}); course id={course_id}")
        if not apply:
            print("DRY-RUN. Text:", TITLE, "|", BODY); return
        for s in audience:
            await _emit(db, s, type=NOTE_TYPE, tone="ok", title=TITLE, body=BODY, extra=EXTRA,
                        icon="🤖", link=f"/student/courses/{course_id}")
        await db.commit()
        print("sent", len(audience))


asyncio.run(main("--apply" in sys.argv))
