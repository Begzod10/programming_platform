"""Phase 4 batch A: hand-translated RU sibling rows for 10 small lessons
(3 quiz rows each) that currently have no ru-detected LessonQuestion quiz
row. No translation API used — every string below composed by hand.

For each source uz row we INSERT a new LessonQuestion row: same lesson_id,
same order_index, same time_limit/points/correct_option, question_kind
='quiz', question_text/options set to the RU translation. question_text_ru
is intentionally left NULL on the new row (only meaningful for bug_hunt).

Idempotent / resumable: before inserting for a lesson, re-checks (via the
same Cyrillic-detection rule as _detect_lang in team_game_questions.py)
whether that lesson already has ANY ru-detected quiz row — skips if so,
so a partial re-run never creates a second ru sibling.

ORM-only via AsyncSessionLocal; no DDL; no app.main import.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson_question import LessonQuestion  # noqa: E402

LESSON_IDS = [984, 1020, 1327, 1328, 1329, 1330, 1331, 1336, 1337, 1338]


def _detect_lang(text: str) -> str:
    return "ru" if any("Ѐ" <= c <= "ӿ" for c in text) else "uz"


# source row id -> (question_text_ru, options_ru)
ROW_TRANSLATIONS: dict[int, tuple[str, list[str]]] = {
    # lesson 984 — GitHub Actions CI/CD
    2934: ("Какой триггер должен быть у переиспользуемого (reusable) workflow, который может вызываться другими workflow?",
           ["workflow_dispatch", "workflow_call", "workflow_run", "on: reusable"]),
    2935: ("В нескольких workflow повторяется только связка checkout + настройка Python + установка зависимостей (не целый job). "
           "Какой инструмент лучше всего подходит для переиспользования этого?",
           ["Reusable workflow", "Composite action", "Matrix strategy", "Concurrency group"]),
    2936: ("Всегда ли использование secrets: inherit является самым безопасным решением?",
           ["Да, потому что все секреты шифруются",
            "Нет, потому что автоматическая передача всех секретов может нарушать принцип наименьших привилегий",
            "Да, потому что автоматически выбираются только нужные секреты",
            "Нет, потому что это работает только в composite action"]),
    # lesson 1020 — code review practices
    2967: ("Какие два элемента ОБЯЗАТЕЛЬНО должны быть в конкретном (actionable) комментарии?",
           ["Имя автора и дата коммита", "ЧТО является проблемой и ПОЧЕМУ это проблема",
            "Только готовое предложение по коду", "Уровень опыта ревьюера"]),
    2968: ("Что означает комментарий, начинающийся с префикса 'nit:'?",
           ["Это очень важно и обязательно блокирует PR", "Это предупреждение о проблеме безопасности",
            "Это метка, обозначающая необязательную, неблокирующую рекомендацию",
            "Это метка, обозначающая формат сообщения коммита"]),
    2969: ("Согласно уроку, КОГДА ревьюеру следует использовать вариант 'Request changes'?",
           ["Только когда есть замечание по читаемости кода",
            "Только когда есть реальная, блокирующая проблема с корректностью, безопасностью или тестами",
            "Каждый раз, даже если есть только комментарии nit:", "Только когда автор неопытен"]),
    # lesson 1327 — Python turtle graphics
    3757: ("Что делает команда t.right(90)?",
           ["Идёт вперёд", "Поворачивает направо на 90 градусов", "Поднимает перо", "Меняет цвет"]),
    3758: ("Что происходит, если черепашка движется после t.penup()?",
           ["Рисует линию", "Двигается, не рисуя линию", "Возвращается назад", "Останавливается"]),
    3759: ("На сколько градусов нужно поворачивать на каждом шаге, чтобы нарисовать квадрат?",
           ["45", "60", "90", "120"]),
    # lesson 1328
    3761: ('Что делает t.pencolor("red")?',
           ["Делает фон красным", "Делает цвет линии (пера) красным", "Закрашивает внутреннюю часть фигуры", "Удаляет черепашку"]),
    3762: ("Между какими двумя командами нужно рисовать, чтобы закрасить фигуру внутри?",
           ["t.forward() и t.right()", "t.begin_fill() и t.end_fill()", "t.penup() и t.pendown()", "import и turtle.done()"]),
    3763: ('Что изменяет turtle.bgcolor("lightblue")?',
           ["Цвет линии", "Цвет фона всего окна", "Цвет черепашки", "Цвет текста"]),
    # lesson 1329
    3765: ("Что делает for i in range(4):?",
           ["Выполняется 1 раз", "Повторяется 4 раза", "Повторяется бесконечно", "Никогда не выполняется"]),
    3766: ("На сколько градусов должен быть каждый поворот, чтобы нарисовать пятиугольник (5 сторон)?",
           ["60", "72", "90", "120"]),
    3767: ("Как записываются команды внутри цикла for?",
           ["Сдвинутыми влево", "Со сдвигом внутрь (с отступом/пробелами)", "Заглавными буквами", "В скобках"]),
    # lesson 1330
    3769: ("С помощью какого слова создаётся функция?", ["func", "def", "function", "make"]),
    3770: ("Что такое 'size' в def kvadrat(size):?",
           ["Имя функции", "Параметр — значение, передаваемое в функцию", "Название цвета", "Ошибка"]),
    3771: ("Если вызвать kvadrat(50), что подставляется вместо size внутри функции?",
           ["0", "50", "100", "Ничего"]),
    # lesson 1331
    3773: ("Что возвращает random.randint(1, 6)?",
           ["Всегда 1", "Случайное целое число от 1 до 6", "Случайный элемент из списка", "Всегда 6"]),
    3774: ("Что делает random.choice(ranglar)?",
           ["Удаляет цвета", "Выбирает случайный элемент из списка", "Создаёт новый цвет", "Сортирует цвета"]),
    3775: ("Что нужно сделать перед тем, как использовать модуль random?",
           ["Ничего", "Написать import random", "Переустановить PyCharm", "Подключиться к интернету"]),
    # lesson 1336 — HTML basics (reuses phase-3 batch-A vocabulary)
    3782: ("Какой тег обозначает самый большой заголовок?", ["<h6>", "<h1>", "<p>", "<b>"]),
    3783: ("Что делает тег <b>...</b>?",
           ["Делает текст жирным", "Удаляет текст", "Переходит на новую строку", "Вставляет изображение"]),
    3784: ("Есть ли у тега <br> закрывающий тег?",
           ["Да, нужен </br>", "Нет, закрывающего тега не существует", "Нужны два закрывающих тега", "Нужен только в h1"]),
    # lesson 1337 — CSS basics
    3786: ('Что делает style="color: red"?',
           ["Делает фон красным", "Делает цвет текста красным", "Удаляет изображение", "Создаёт кнопку"]),
    3787: ("Что такое background-color?",
           ["Цвет текста", "Цвет фона", "Цвет границы", "Размер изображения"]),
    3788: ("Что мы добавляем к тегу, чтобы задать цвет?", ["class", "style", "src", "href"]),
    # lesson 1338 — <img> basics
    3790: ("Какова функция тега <img>?",
           ["Написание текста", "Вставка изображения", "Создание списка", "Создание кнопки"]),
    3791: ("Что указывает атрибут src?",
           ["Название изображения (alt текст)", "Адрес изображения (какое изображение)", "Цвет изображения", "Границу изображения"]),
    3792: ('Что делает width="200"?',
           ["Увеличивает изображение в 200 раз", "Показывает изображение шириной 200 пикселей", "Удаляет изображение", "Поворачивает изображение"]),
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        inserted = 0
        for lesson_id in LESSON_IDS:
            result = await db.execute(
                select(LessonQuestion).where(
                    LessonQuestion.lesson_id == lesson_id,
                    LessonQuestion.question_kind == "quiz",
                )
            )
            lesson_qs = result.scalars().all()
            if any(_detect_lang(q.question_text) == "ru" for q in lesson_qs):
                print(f"lesson {lesson_id}: already has a ru sibling row, skipping")
                continue

            uz_rows = [q for q in lesson_qs if _detect_lang(q.question_text) == "uz"]
            for row in sorted(uz_rows, key=lambda r: (r.order_index, r.id)):
                tr = ROW_TRANSLATIONS.get(row.id)
                if tr is None:
                    print(f"  SKIP lesson {lesson_id} row {row.id}: no translation prepared")
                    continue
                q_ru, opts_ru = tr
                if len(opts_ru) != len(row.options):
                    print(f"  SKIP lesson {lesson_id} row {row.id}: option count mismatch")
                    continue
                new_row = LessonQuestion(
                    lesson_id=row.lesson_id,
                    question_text=q_ru,
                    options=opts_ru,
                    correct_option=row.correct_option,
                    time_limit=row.time_limit,
                    points=row.points,
                    order_index=row.order_index,
                    question_kind="quiz",
                )
                db.add(new_row)
                inserted += 1
            print(f"lesson {lesson_id}: inserted {len(uz_rows)} ru sibling rows")

        await db.commit()
        print(f"Phase4 batch A: inserted {inserted} new LessonQuestion rows across {len(LESSON_IDS)} lessons")


if __name__ == "__main__":
    asyncio.run(main())
