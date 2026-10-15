"""Course 28 lesson 191, exercise 7712 (matching "Flask-Migrate va Alembic"): the hint said nothing
("remember how each word was used") and there was no explanation. A student who mixed up init / migrate /
upgrade got only the generic AI paragraph. UZ in place, RU in translation_cache.

    python scripts/fix_exercise_7712_hint.py           # dry-run
    python scripts/fix_exercise_7712_hint.py --apply
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import _write  # noqa: E402

EXERCISE_ID = 7712
HINT = ("Tartibni eslang: avval migratsiyalar papkasi tayyorlanadi, keyin o'zgarish FAYLI yoziladi, "
        "oxirida u bazaga qo'llanadi. Bu buyruqlardan faqat bittasi bazaga tegadi.")
EXPLANATION = (
    "flask db init — bir marta migrations/ papkasini yaratadi. "
    "flask db migrate — modellardagi o'zgarishni topib, migrations/versions ichida yangi migratsiya FAYLINI yaratadi, "
    "lekin bazaga tegmaydi. flask db upgrade — shu faylni bazaga qo'llaydi (jadval yoki ustun haqiqatan o'zgaradi). "
    "downgrade — bazani bir qadam orqaga qaytaradi. migrations/versions — barcha migratsiya fayllari saqlanadigan joy."
)
HINT_RU = ("Вспомните порядок: сначала готовится папка миграций, затем пишется ФАЙЛ изменения, "
           "в конце он применяется к базе. Из этих команд к базе обращается только одна.")
EXPLANATION_RU = (
    "flask db init — один раз создаёт папку migrations/. "
    "flask db migrate — находит изменения в моделях и создаёт в migrations/versions новый ФАЙЛ миграции, "
    "но к базе не обращается. flask db upgrade — применяет этот файл к базе (таблица или столбец реально меняются). "
    "downgrade — откатывает базу на один шаг назад. migrations/versions — место, где хранятся все файлы миграций."
)


async def main(apply: bool):
    async with AsyncSessionLocal() as db:
        ex = (await db.execute(select(Exercise).where(Exercise.id == EXERCISE_ID))).scalar_one()
        print(f"{ex.title}\n--- hint (hozir): {ex.hint}\n--- hint (yangi): {HINT}\n--- explanation (hozir): {ex.explanation}\n--- explanation (yangi): {EXPLANATION}")
        if not apply:
            print("\nDRY-RUN: hech narsa yozilmadi."); return
        ex.hint, ex.explanation = HINT, EXPLANATION
        await db.flush()
        await _write(db, "exercise", EXERCISE_ID, "hint", HINT, HINT_RU)
        await _write(db, "exercise", EXERCISE_ID, "explanation", EXPLANATION, EXPLANATION_RU)
        await db.commit()
        print("\nyozildi. Servisni qayta ishga tushiring.")


if __name__ == "__main__":
    asyncio.run(main("--apply" in sys.argv))
