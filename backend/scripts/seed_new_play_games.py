"""Add the new /play modules ("So'z va grafik", "Yangi o'yinlar") — safe to re-run: only missing rows are added.

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


HANG_WORDS = [("🐱", "mushuk", "кошка"), ("🍎", "olma", "яблоко"), ("🐟", "baliq", "рыба"), ("🌳", "daraxt", "дерево"),
              ("🚗", "mashina", "машина"), ("🐘", "fil", "слон"), ("🍌", "banan", "банан"), ("🌙", "oy", "луна"),
              ("🦁", "sher", "лев"), ("📖", "kitob", "книга")]


def rounds(kind, title, title_ru, instr, instr_ru, emoji, atype, **extra):
    c = {"mode": "rounds", "kind": kind, "character": {"emoji": emoji, "label": title}, **extra}
    return (title, title_ru, atype, instr, instr_ru, c)


def mode(m, title, title_ru, instr, instr_ru, emoji, atype, **extra):
    c = {"mode": m, "character": {"emoji": emoji, "label": title}, **extra}
    return (title, title_ru, atype, instr, instr_ru, c)


T = EarlyActivityType
MODULE2_TITLE = "Yangi o'yinlar"
ACTIVITIES2 = [
    rounds("clock", "Soat (oson)", "Часы (легко)", "Soat nechchi?", "Сколько времени?", "🕒", T.count, level="easy", rounds_count=6),
    rounds("clock", "Soat (qiyin)", "Часы (сложно)", "Soat nechchi?", "Сколько времени?", "🕒", T.count, level="hard", rounds_count=8),
    rounds("mult", "Ko'paytirish (oson)", "Умножение (легко)", "Ko'paytir!", "Умножь!", "✖️", T.count, max=5, rounds_count=8),
    rounds("mult", "Ko'paytirish (qiyin)", "Умножение (сложно)", "Ko'paytir!", "Умножь!", "✖️", T.count, max=9, rounds_count=10),
    rounds("shape", "Shakl va rang", "Фигуры и цвета", "To'g'ri shaklni bos!", "Нажми на нужную фигуру!", "🔷", T.match, rounds_count=8),
    rounds("listen", "Harfni eshit", "Услышь букву", "Eshit va harfni top!", "Послушай и найди букву!", "🔊", T.match, set="letters", rounds_count=8),
    rounds("listen", "Sonni eshit", "Услышь число", "Eshit va sonni top!", "Послушай и найди число!", "🔊", T.match, set="numbers", rounds_count=8),
    rounds("money", "Necha so'm?", "Сколько сумов?", "Pullarni sanab, javobni top!", "Посчитай деньги!", "💰", T.count, max=2000, rounds_count=6),
    mode("bubbles", "Pufakchalar (sonlar)", "Пузыри (числа)", "To'g'ri pufakchani yorib chiq!", "Лопни нужные пузыри!", "🫧", T.match, kind="numbers", max=10, rounds_count=6),
    mode("bubbles", "Pufakchalar (harflar)", "Пузыри (буквы)", "To'g'ri pufakchani yorib chiq!", "Лопни нужные пузыри!", "🫧", T.match, kind="letters", rounds_count=6),
    mode("bubbles", "Pufakchalar (qo'shish)", "Пузыри (сложение)", "Yig'indisi mos pufakchani yorib chiq!", "Лопни пузыри с нужной суммой!", "🫧", T.count, kind="sums", max=12, rounds_count=6),
    mode("hangman", "Osilgan odam", "Виселица", "Harflarni taxmin qilib so'zni top!", "Угадай слово по буквам!", "🔤", T.sequence, rounds_count=4, words=[{"emoji": e, "uz": u, "ru": r} for e, u, r in HANG_WORDS]),
    mode("merge", "2048 (oson)", "2048 (легко)", "Bir xil sonlarni birlashtir!", "Соединяй одинаковые числа!", "🔢", T.count, goal=64),
    mode("merge", "2048 (qiyin)", "2048 (сложно)", "Bir xil sonlarni birlashtir!", "Соединяй одинаковые числа!", "🔢", T.count, goal=128),
    mode("sudoku", "Sudoku 4×4 (oson)", "Судоку 4×4 (легко)", "Har qator, ustun va katakda 1–4 bo'lsin!", "В каждой строке, столбце и квадрате цифры 1–4!", "🧮", T.sequence, blanks=5),
    mode("sudoku", "Sudoku 4×4 (qiyin)", "Судоку 4×4 (сложно)", "Har qator, ustun va katakda 1–4 bo'lsin!", "В каждой строке, столбце и квадрате цифры 1–4!", "🧮", T.sequence, blanks=9),
    mode("puzzle", "Rasm jumboq", "Пазл-картинка", "Ikki bo'lakni bosib almashtir, rasmni tikla!", "Меняй куски местами и собери картинку!", "🧩", T.sequence),
]

MODULES = [
    (MODULE_TITLE, "Слова и графики", "Harflardan so'z tuz va grafikni o'qi", "Собери слово из букв и прочитай график", "🔤", 5, 9, ACTIVITIES),
    (MODULE2_TITLE, "Новые игры", "Soat, ko'paytirish, pufakchalar, sudoku va boshqalar", "Часы, умножение, пузыри, судоку и другое", "🎮", 5, 12, ACTIVITIES2),
]


async def main():
    async with AsyncSessionLocal() as db:
        for title, title_ru, desc, desc_ru, icon, age_min, age_max, acts in MODULES:
            module = (await db.execute(select(EarlyModule).where(EarlyModule.title == title))).scalar_one_or_none()
            if module is None:
                instructor_id = (await db.execute(select(EarlyModule.instructor_id).order_by(EarlyModule.id).limit(1))).scalar_one()
                next_order = (await db.execute(select(func.coalesce(func.max(EarlyModule.display_order), 0) + 1))).scalar_one()
                module = EarlyModule(
                    title=title, title_ru=title_ru, description=desc, description_ru=desc_ru,
                    subject=EarlySubject.logic, age_min=age_min, age_max=age_max, icon_emoji=icon, color_accent="#6C5CE7",
                    instructor_id=instructor_id, source_lang="uz", display_order=next_order,
                    is_active=True, is_published=True,
                )
                db.add(module)
                await db.flush()
                print("module created:", title, module.id)
            existing = set((await db.execute(select(EarlyActivity.title).where(EarlyActivity.module_id == module.id))).scalars())
            added = 0
            for i, (a_title, a_ru, atype, instr, instr_ru, content) in enumerate(acts, 1):
                if a_title in existing:
                    continue
                db.add(EarlyActivity(
                    module_id=module.id, title=a_title, title_ru=a_ru, order=i, activity_type=atype,
                    instruction_text=instr, instruction_text_ru=instr_ru,
                    content_json=json.dumps(content, ensure_ascii=False),
                    estimated_seconds=90, max_stars=3, source_lang="uz", is_active=True, is_published=True,
                ))
                added += 1
            print(f"  {title}: activities added: {added}")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
