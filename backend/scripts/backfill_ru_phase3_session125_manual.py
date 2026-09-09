"""Phase 3 (priority slice): hand-translated RU backfill for GameQuestion
quiz rows in session 125 ("Blue 5-6", real class from today). No translation
API used — every string below composed by hand.

Idempotent: only updates rows still missing question_text_ru or options_ru;
safe to re-run. ORM-only via AsyncSessionLocal, no DDL, no app.main import.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select, or_  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.team_game import GameQuestion  # noqa: E402

QUESTION_MAP: dict[str, str] = {
    "<b>...</b> tegi nima qiladi?": "Что делает тег <b>...</b>?",
    "<br> tegining yopuvchisi bormi?": "Есть ли у тега <br> закрывающий тег?",
    "<button>...</button> nima uchun?": "Для чего нужен тег <button>...</button>?",
    "<h1>...</h1> nima uchun ishlatiladi?": "Для чего используется <h1>...</h1>?",
    "<img> tegining vazifasi nima?": "Какова функция тега <img>?",
    "<li> nima?": "Что такое тег <li>?",
    "<p>...</p> nima uchun ishlatiladi?": "Для чего используется <p>...</p>?",
    "<ul> tegi nima uchun?": "Для чего нужен тег <ul>?",
    "Eng katta sarlavha qaysi teg?": "Какой тег обозначает самый большой заголовок?",
    "HTML nima?": "Что такое HTML?",
    "Ko'p teglar necha qismdan iborat bo'ladi?": "Из скольких частей состоит большинство тегов?",
    "Rang berish uchun tegga nima qo'shamiz?": "Что мы добавляем к тегу, чтобы задать цвет?",
    "Tugmaga rang berish uchun nima ishlatamiz?": "Что мы используем, чтобы задать цвет кнопке?",
    "Yakuniy sahifada nechta asosiy qism bor (sarlavha, rasm, ro'yxat, tugma)?":
        "Сколько основных частей на итоговой странице (заголовок, изображение, список, кнопка)?",
    "background-color nima?": "Что такое background-color?",
    "href atributi nima uchun?": "Для чего нужен атрибут href?",
    "src atributi nimani ko'rsatadi?": "Что указывает атрибут src?",
    'style="color: red" nima qiladi?': 'Что делает style="color: red"?',
    'width="200" nima qiladi?': 'Что делает width="200"?',
}

OPTION_MAP: dict[str, str] = {
    "2": "2",
    "3": "3",
    "4": "4",
    "6": "6",
    "<b>": "<b>",
    "<h1>": "<h1>",
    "<h6>": "<h6>",
    "<p>": "<p>",
    "Bitta (faqat ochuvchi)": "Одна (только открывающий)",
    "Bitta band": "Один пункт",
    "Bosiladigan tugma yaratish": "Создание кликабельной кнопки",
    "Brauzerga sahifada nima ko'rsatishni aytadigan til": "Язык, который указывает браузеру, что показывать на странице",
    "Chegara rangi": "Цвет границы",
    "Eng katta sarlavha": "Самый большой заголовок",
    "Faqat h1 da kerak": "Нужен только в h1",
    "Fonni qizil qiladi": "Делает фон красным",
    "Ha, </br> kerak": "Да, нужен </br>",
    "Havola": "Ссылка",
    "Havola qayerga o'tishini ko'rsatish uchun": "Чтобы указать, куда ведёт ссылка",
    "Havola yaratish": "Создание ссылки",
    "Hech qanday qism yo'q": "Частей нет",
    "Ikkita yopuvchi kerak": "Нужны два закрывающих тега",
    "Ikkita: ochuvchi va yopuvchi": "Две: открывающий и закрывающий",
    "Matn rangi": "Цвет текста",
    "Matn rangini qizil qiladi": "Делает цвет текста красным",
    "Matn yozish": "Написание текста",
    "Matnni o'chiradi": "Удаляет текст",
    "Matnni qalin qiladi": "Делает текст жирным",
    "Matnni qalin qilish uchun": "Чтобы сделать текст жирным",
    "O'yin": "Игра",
    "Oddiy matn (paragraf)": "Обычный текст (параграф)",
    "Orqa fon rangi": "Цвет фона",
    "Ovoz dasturi": "Программа для звука",
    "Rang berish uchun": "Для задания цвета",
    "Rasm": "Изображение",
    "Rasm chegarasini": "Границу изображения",
    "Rasm dasturi": "Программа для рисования",
    "Rasm manzilini (qaysi rasm)": "Адрес изображения (какое изображение)",
    "Rasm nomini (alt matn)": "Название изображения (alt текст)",
    "Rasm o'lchami": "Размер изображения",
    "Rasm qo'yadi": "Вставляет изображение",
    "Rasm qo'yish": "Вставка изображения",
    "Rasm qo'yish uchun": "Чтобы вставить изображение",
    "Rasm rangini": "Цвет изображения",
    "Rasmni 200 marta ko'paytiradi": "Увеличивает изображение в 200 раз",
    "Rasmni 200 piksel kenglikda ko'rsatadi": "Показывает изображение шириной 200 пикселей",
    "Rasmni aylantiradi": "Поворачивает изображение",
    "Rasmni o'chiradi": "Удаляет изображение",
    "Ro'yxat": "Список",
    "Ro'yxat konteyneri": "Контейнер списка",
    "Ro'yxat yasash": "Создание списка",
    "Ro'yxatning har bir bandi": "Каждый пункт списка",
    "Sarlavha": "Заголовок",
    "Sarlavha yaratish": "Создание заголовка",
    "Tugma": "Кнопка",
    "Tugma yaratadi": "Создаёт кнопку",
    "Tugma yaratish": "Создание кнопки",
    "Uchta": "Три",
    "Yangi qatorga o'tadi": "Переходит на новую строку",
    "Yo'q, yopuvchi tegi yo'q": "Нет, закрывающего тега не существует",
    "alt": "alt",
    "class": "class",
    "href": "href",
    "src": "src",
    "style": "style",
    'style="background-color: ..."': 'style="background-color: ..."',
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GameQuestion).where(
                GameQuestion.question_kind == "quiz",
                GameQuestion.session_id == 125,
                or_(GameQuestion.question_text_ru.is_(None), GameQuestion.question_text_ru == "", GameQuestion.options_ru.is_(None)),
            ).order_by(GameQuestion.id)
        )
        rows = result.scalars().all()
        print(f"Phase3/session125: {len(rows)} rows need RU")

        written = 0
        missing_keys = []
        for row in rows:
            q_ru = QUESTION_MAP.get(row.question_text)
            opts_ru = []
            ok = q_ru is not None
            for o in row.options:
                tr = OPTION_MAP.get(o)
                if tr is None:
                    ok = False
                    missing_keys.append(o)
                opts_ru.append(tr)
            if not ok:
                print(f"  SKIP id={row.id}: missing mapping for {row.question_text!r}")
                continue
            row.question_text_ru = q_ru
            row.options_ru = opts_ru
            written += 1
        await db.commit()
        print(f"Phase3/session125 wrote {written}/{len(rows)} rows.")
        if missing_keys:
            print("Missing option keys:", set(missing_keys))


if __name__ == "__main__":
    asyncio.run(main())
