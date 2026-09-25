"""Add the "So'z va grafik" module (word-build + bar-chart games) to /play.

Uses the app's own DB settings (.env), so no password to type. Idempotent.

    cd /home/student_platform/backend      # or wherever backend/ lives
    python scripts/seed_new_play_games.py
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select

from app.db import base as _base  # noqa: F401
from app.db.database import AsyncSessionLocal
from app.models.early_learning import EarlyActivity, EarlyActivityType, EarlyModule, EarlySubject

MODULE_TITLE = "So'z va grafik"

EASY_WORDS = [("🐱", "mushuk", "кошка"), ("🍎", "olma", "яблоко"), ("🍞", "non", "хлеб"), ("🐟", "baliq", "рыба"),
              ("🏠", "uy", "дом"), ("🌸", "gul", "цветок"), ("🐶", "it", "пёс"), ("☀️", "quyosh", "солнце")]
HARD_WORDS = [("🚀", "raketa", "ракета"), ("🐢", "toshbaqa", "черепаха"), ("🌈", "kamalak", "радуга"),
              ("🍓", "qulupnay", "клубника"), ("🚲", "velosiped", "велосипед"), ("🦋", "kapalak", "бабочка"),
              ("🏫", "maktab", "школа"), ("🍉", "tarvuz", "арбуз")]


def words(rows):
    return [{"emoji": e, "uz": u, "ru": r} for e, u, r in rows]


def wb(rounds, rows):
    return {"mode": "wordbuild", "character": {"emoji": "🔤", "label": "So'z tuz"},
            "rounds_count": rounds, "words": words(rows)}


def chart(rounds, hard):
    return {"mode": "chart", "character": {"emoji": "📊", "label": "Grafik"}, "rounds_count": rounds, "hard": hard}


ACTIVITIES = [
    ("So'z tuz (oson)", "Составь слово (легко)", EarlyActivityType.sequence,
     "Harflarni to'g'ri tartibda bos!", "Нажимай буквы по порядку!", wb(5, EASY_WORDS)),
    ("So'z tuz (qiyin)", "Составь слово (сложно)", EarlyActivityType.sequence,
     "Harflarni to'g'ri tartibda bos!", "Нажимай буквы по порядку!", wb(6, HARD_WORDS)),
    ("Grafik o'qi (oson)", "Читай график (легко)", EarlyActivityType.count,
     "Grafikka qarab javob ber!", "Посмотри на график и ответь!", chart(6, False)),
    ("Grafik o'qi (qiyin)", "Читай график (сложно)", EarlyActivityType.count,
     "Grafikka qarab javob ber!", "Посмотри на график и ответь!", chart(8, True)),
]


async def main():
    async with AsyncSessionLocal() as db:
        module = (await db.execute(select(EarlyModule).where(EarlyModule.title == MODULE_TITLE))).scalar_one_or_none()
        if module is None:
            instructor_id = (await db.execute(select(EarlyModule.instructor_id).order_by(EarlyModule.id).limit(1))).scalar_one()
            next_order = (await db.execute(select(func.coalesce(func.max(EarlyModule.display_order), 0) + 1))).scalar_one()
            module = EarlyModule(
                title=MODULE_TITLE, title_ru="Слова и графики",
                description="Harflardan so'z tuz va grafikni o'qi", description_ru="Собери слово из букв и прочитай график",
                subject=EarlySubject.logic, age_min=5, age_max=9, icon_emoji="🔤", color_accent="#6C5CE7",
                instructor_id=instructor_id, source_lang="uz", display_order=next_order,
                is_active=True, is_published=True,
            )
            db.add(module)
            await db.flush()
            print("module created:", module.id)
        existing = set((await db.execute(select(EarlyActivity.title).where(EarlyActivity.module_id == module.id))).scalars())
        added = 0
        for i, (title, title_ru, atype, instr, instr_ru, content) in enumerate(ACTIVITIES, 1):
            if title in existing:
                continue
            db.add(EarlyActivity(
                module_id=module.id, title=title, title_ru=title_ru, order=i, activity_type=atype,
                instruction_text=instr, instruction_text_ru=instr_ru,
                content_json=json.dumps(content, ensure_ascii=False),
                estimated_seconds=90, max_stars=3, source_lang="uz", is_active=True, is_published=True,
            ))
            added += 1
        await db.commit()
        print(f"activities added: {added}")


if __name__ == "__main__":
    asyncio.run(main())
