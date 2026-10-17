"""Course 28 lesson 198, exercise 1047 (ordering "Yuklangan rasm faylini xavfsiz saqlash"): the key was ONE strict
sequence, so a student who put os.makedirs second, or imghdr after secure_filename, was marked wrong although
both orders are valid code (and the AI feedback then invented a reason). The exercise now stores the real
dependencies as order_constraints (positions in correct_order) and has a hint and an explanation.
UZ in place, RU in translation_cache (the constraints are language-neutral).

    python scripts/fix_exercise_1047_order.py           # dry-run
    python scripts/fix_exercise_1047_order.py --apply
"""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import _write  # noqa: E402

EXERCISE_ID = 1047
# positions in correct_order: 0 validate, 1 imghdr, 2 secure_filename, 3 uuid, 4 makedirs, 5 save, 6 db, 7 redirect
CONSTRAINTS = [
    [0, 1], [0, 2], [0, 3], [0, 4], [0, 5],   # the form is validated first
    [1, 3], [2, 3],                           # the unique name is built from a checked file / cleaned name
    [3, 5], [4, 5],                           # name and folder are ready before writing
    [5, 6], [6, 7],                           # saved on disk, then in the database, then redirect
]
HINT = ("Avval hamma tekshiruv (forma, tur, nom), keyin yangi nom va papka tayyorlanadi, "
        "faqat shundan keyin diskka yoziladi, bazaga saqlanadi va redirect qilinadi.")
EXPLANATION = (
    "Tartib bog'liqliklardan chiqadi: form.validate_on_submit() eng birinchi, chunki noto'g'ri so'rov bilan ishlashning ma'nosi yo'q. "
    "imghdr.what (ichki tur) va secure_filename (nom) bir-biriga bog'liq emas, ikkalasi ham uuid4 bilan yangi nom yaratishdan oldin kelishi kerak. "
    "os.makedirs(..., exist_ok=True) faqat file.save() dan oldin bajarilishi shart, undan oldin istalgan joyda bo'lishi mumkin. "
    "Fayl diskka yozilgach, bazaga nomi saqlanadi (User.avatar = new_name), oxirida redirect + flash bilan profilga qaytariladi."
)
HINT_RU = ("Сначала все проверки (форма, тип, имя), затем готовятся новое имя и папка, "
           "и только после этого файл пишется на диск, имя сохраняется в базе и делается redirect.")
EXPLANATION_RU = (
    "Порядок следует из зависимостей: form.validate_on_submit() идёт первым, потому что работать с неверным запросом бессмысленно. "
    "imghdr.what (внутренний тип) и secure_filename (имя) не зависят друг от друга, но оба должны быть до создания нового имени через uuid4. "
    "os.makedirs(..., exist_ok=True) обязательно должен быть до file.save(), а до этого может стоять где угодно. "
    "После записи файла на диск имя сохраняется в базе (User.avatar = new_name), в конце — redirect + flash на профиль."
)


async def main(apply: bool):
    async with AsyncSessionLocal() as db:
        ex = (await db.execute(select(Exercise).where(Exercise.id == EXERCISE_ID))).scalar_one()
        print(ex.title, "| hozir correct_answers:", ex.correct_answers, "| hint:", repr(ex.hint), "| explanation:", repr(ex.explanation))
        print("yangi order_constraints:", CONSTRAINTS, "\nyangi hint:", HINT, "\nyangi explanation:", EXPLANATION)
        if not apply:
            print("\nDRY-RUN: hech narsa yozilmadi."); return
        ex.correct_answers = json.dumps({"order_constraints": CONSTRAINTS})
        ex.hint, ex.explanation = HINT, EXPLANATION
        await db.flush()
        await _write(db, "exercise", EXERCISE_ID, "hint", HINT, HINT_RU)
        await _write(db, "exercise", EXERCISE_ID, "explanation", EXPLANATION, EXPLANATION_RU)
        await db.commit()
        print("\nyozildi. Servisni qayta ishga tushiring.")


if __name__ == "__main__":
    asyncio.run(main("--apply" in sys.argv))
