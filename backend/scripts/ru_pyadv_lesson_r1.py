"""Russian translation for Python: Ilg'or Mavzular, lesson order=6 (R1)."""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

LESSON_ID = 722

TITLE_RU = "Review 1: Декораторы, генераторы, контекстные менеджеры, functools, Type Hints"

TEXT_RU = """\
<h2>Review 1 — Повторение уроков 1-6: система поиска библиотеки</h2>

<p>Объединив всё из уроков 1-6, построим небольшую систему поиска библиотеки: декоратор, генератор, контекстный менеджер, functools и type hints — всё вместе.</p>

<h3>Цель проекта</h3>
<ul>
<li>Кеширование функции поиска через <code>@lru_cache</code> (урок 4)</li>
<li>"Производство" доступных книг по одной через <strong>генератор</strong> (урок 2)</li>
<li>Безопасное открытие/закрытие "файла" библиотеки через <strong>контекстный менеджер</strong> (урок 3)</li>
<li>Возврат результата поиска через <strong>list comprehension</strong> и type hint <code>Optional</code> (уроки 5, 6)</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — контекстный менеджер библиотеки</h4>
<p>Создайте класс <code>Kutubxona</code> с методами <code>__enter__</code>/<code>__exit__</code> &mdash; <code>__enter__</code> выводит "Kutubxona ochildi" и возвращает список книг, <code>__exit__</code> выводит "Kutubxona yopildi" (как в уроке 3).</p>

<h4>Задание 2 — генератор книг</h4>
<p>Напишите функцию-генератор, которая через <code>yield</code> отдаёт по одной только книги со значением <code>mavjud=True</code> из списка книг (как в уроке 2).</p>

<h4>Задание 3 — кеширование поиска</h4>
<p>Украсьте функцию поиска по заголовку декоратором <code>@lru_cache</code>, укажите тип результата как <code>Optional[str]</code> (как в уроках 4, 6).</p>

<h4>Задание 4 — фильтрация через list comprehension</h4>
<p>Получите из списка книг только уникальных (без повторов) авторов через <code>set comprehension</code> (как в уроке 5).</p>

<h3>🐛 Намеренная сложность: применение @lru_cache к генератору</h3>
<p>Если вы примените <code>@lru_cache</code> к функции-генератору, вы можете попасть в следующую ловушку:</p>
<pre><code>@lru_cache(maxsize=None)
def mavjud_kitoblar(kitoblar_royxati):     # ❗ функция-генератор + lru_cache
    for kitob in kitoblar_royxati:
        if kitob.mavjud:
            yield kitob.sarlavha

# Первый вызов - работает правильно:
for sarlavha in mavjud_kitoblar(kitoblar):
    print(sarlavha)

# Второй вызов (С ТЕМИ ЖЕ аргументами) - даёт ПУСТОЙ результат!
for sarlavha in mavjud_kitoblar(kitoblar):
    print(sarlavha)   # ❌ ничего не выводится!</code></pre>
<p><strong>Результат:</strong> при применении <code>lru_cache</code> к функции-генератору, он кеширует <strong>сам объект-генератор</strong>, а <strong>не его значения</strong>. Первый цикл <code>for</code> <strong>полностью "расходует"</strong> генератор (вспомните урок 2 — генератор одноразовый). При повторном вызове <code>lru_cache</code> возвращает тот же самый (уже "израсходованный") объект-генератор, поэтому второй цикл <code>for</code> даёт пустой результат. <strong>Решение:</strong> не применяйте <code>lru_cache</code> к функциям-генераторам &mdash; вместо этого кешируйте результат, превратив его в <code>list()</code>, или используйте отдельный механизм кеширования.</p>

<h3>Начальный код</h3>
<pre><code>from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])   # ❗ namedtuple - хешируемый (нужен для lru_cache)

class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        # Задание 1: выведите "Kutubxona ochildi", верните self.kitoblar
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # Задание 1: выведите "Kutubxona yopildi"
        pass

def mavjud_kitoblar_generatori(kitoblar):
    # Задание 2: отдайте через yield только заголовки книг с mavjud=True
    pass

@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar, sarlavha) -> Optional[str]:
    # Задание 3: найдите соответствующую книгу, если не найдено - верните None
    pass</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])

class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        print("Kutubxona ochildi")
        return self.kitoblar

    def __exit__(self, exc_type, exc_value, traceback):
        print("Kutubxona yopildi")
        return False

def mavjud_kitoblar_generatori(kitoblar):
    for kitob in kitoblar:
        if kitob.mavjud:
            yield kitob.sarlavha

@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar: tuple, sarlavha: str) -> Optional[str]:
    for kitob in kitoblar:
        if kitob.sarlavha == sarlavha:
            return kitob.sarlavha
    return None

kitoblar = (
    Kitob("Python asoslari", "Ali", True),
    Kitob("Django darslari", "Vali", False),
    Kitob("Algoritmlar", "Ali", True),
)

with Kutubxona(kitoblar) as royxat:
    for sarlavha in mavjud_kitoblar_generatori(royxat):
        print(sarlavha)

noyob_mualliflar = {kitob.muallif for kitob in kitoblar}
print(noyob_mualliflar)   # {'Ali', 'Vali'}</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Всё из уроков 1-6 вместе: декоратор, генератор, контекстный менеджер, functools, comprehensions, type hints</li>
<li>✅ Контекстный менеджер используется для безопасного открытия/закрытия ресурсов ("подключения" библиотеки)</li>
<li>✅ Применение <code>lru_cache</code> к функции-генератору опасно — он кеширует только объект-генератор, не значения</li>
<li>✅ Set comprehension удобен для быстрого получения уникальных значений</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# REVIEW 1: Система поиска библиотеки (уроки 1-6)
# ════════════════════════════════════════════════════════════════════

from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])


class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        print("Kutubxona ochildi")
        return self.kitoblar

    def __exit__(self, exc_type, exc_value, traceback):
        print("Kutubxona yopildi")
        return False


def mavjud_kitoblar_generatori(kitoblar):
    for kitob in kitoblar:
        if kitob.mavjud:
            yield kitob.sarlavha


@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar: tuple, sarlavha: str) -> Optional[str]:
    for kitob in kitoblar:
        if kitob.sarlavha == sarlavha:
            return kitob.sarlavha
    return None


kitoblar = (
    Kitob("Python asoslari", "Ali", True),
    Kitob("Django darslari", "Vali", False),
    Kitob("Algoritmlar", "Ali", True),
)

with Kutubxona(kitoblar) as royxat:
    for sarlavha in mavjud_kitoblar_generatori(royxat):
        print(sarlavha)

noyob_mualliflar = {kitob.muallif for kitob in kitoblar}
print(noyob_mualliflar)

# ─────────────────────────────────────────────────────────────────────
# Намеренная сложность - применение lru_cache к генератору (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @lru_cache(maxsize=None)
# def mavjud_kitoblar_xato(kitoblar_royxati):
#     for kitob in kitoblar_royxati:
#         if kitob.mavjud:
#             yield kitob.sarlavha
# # Второй вызов даёт ПУСТОЙ результат - генератор "израсходован"!
"""

EX = {
    4215: {
        "title": "Роль контекстного менеджера Kutubxona",
        "description": "При работе блока with Kutubxona(kitoblar) as royxat:, что делает __enter__?",
        "hint": "__enter__ вызывается в начале 'with'.",
        "explanation": "Метод __enter__ выводит \"Kutubxona ochildi\" и возвращает список self.kitoblar, это значение передаётся переменной royxat.",
    },
    4216: {
        "title": "Проблема применения lru_cache к генератору",
        "description": "Когда @lru_cache применён к функции-генератору, почему второй одинаковый вызов даёт пустой результат?",
        "hint": "Вспомните урок 2: генератор одноразовый.",
        "explanation": "lru_cache кеширует сам объект-генератор, а не значения. После первого полного прохода генератор \"расходуется\", и lru_cache возвращает тот же самый израсходованный объект.",
    },
    4217: {
        "title": "Расположите процесс работы проекта библиотеки",
        "description": "Расположите полный процесс, происходящий при использовании mavjud_kitoblar_generatori(royxat) внутри блока with Kutubxona(kitoblar) as royxat.",
        "hint": "",
        "explanation": "",
    },
    4218: {
        "title": "Почему не рекомендуется применять lru_cache к генератору и что делать?",
        "description": (
            "Объединив уроки 1-6, объясните, почему применение "
            "@lru_cache к функциям-генераторам опасно, и что нужно "
            "сделать для решения этой проблемы? Объясните своими "
            "словами."
        ),
        "hint": "Что на самом деле кеширует lru_cache — ЗНАЧЕНИЯ функции, или ОБЪЕКТ-РЕЗУЛЬТАТ вызова функции?",
        "expected_answer": "lru_cache кеширует РЕЗУЛЬТАТ вызова функции. Когда вызывается функция-генератор, её \"результатом\" на самом деле является сам объект-генератор (пока ещё ни одно значение не вычислено) — значения вычисляются по одному только при прохождении генератора (например через цикл for). lru_cache кеширует именно этот объект-генератор. После первого полного прохода генератора он \"расходуется\" (вспомните урок 2, генератор одноразовый). При повторном вызове с теми же аргументами lru_cache возвращает тот же (уже израсходованный) объект-генератор, поэтому второй проход даёт пустой результат. Решение: не применять lru_cache к функциям-генераторам — вместо этого кешировать результат, превратив его в list(), или применить совершенно другой способ кеширования.",
    },
}


async def _run():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        ex_rows = (
            await db.execute(select(Exercise).where(Exercise.id.in_(EX.keys())))
        ).scalars().all()

        section_map = {"Текст": "Текст", "Код": "Код", "Упражнения": "Упражнения"}
        section_map[lesson.text_content] = TEXT_RU
        section_map[lesson.code_content] = CODE_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={"title": TITLE_RU, "text_content": TEXT_RU},
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
