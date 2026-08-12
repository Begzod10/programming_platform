"""Russian translation for Python: Ilg'or Mavzular, lesson order=10 (R2, CAPSTONE)."""
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

LESSON_ID = 730

TITLE_RU = "Review 2 (CAPSTONE): Итоговое повторение продвинутых тем"

TEXT_RU = """\
<h2>Review 2 (CAPSTONE) — Исполнитель задач: async, GIL и magic methods вместе</h2>

<pre class="mermaid">
flowchart TB
    TASK["@dataclass Vazifa (приоритет, __lt__)"] --> QUEUE["очередь, отсортированная по приоритету"]
    QUEUE --> IOTASK["I/O-bound задачи -> asyncio.gather (одновременно)"]
    QUEUE --> CPUTASK["CPU-bound задачи -> multiprocessing (уроки 7,8)"]
    DECORATOR["@vaqt_olchagich"] --> IOTASK
</pre>

<p>Объединив всё, что изучили в 9 уроках &mdash; декоратор, генератор, контекстный менеджер, functools, comprehensions, type hints, asyncio, дизайн с учётом GIL, magic methods &mdash; построим небольшую <strong>систему исполнения задач</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — Vazifa через @dataclass и сортировка по приоритету</h4>
<pre><code>from dataclasses import dataclass, field

@dataclass
class Vazifa:
    nomi: str
    ustuvorlik: int          # ❗ меньшее число - более высокий приоритет
    cpu_bound: bool = False   # ❗ если True, это CPU-bound задача (урок 8)

    def __lt__(self, boshqa):     # ❗ урок 9: нужен для sort()
        return self.ustuvorlik < boshqa.ustuvorlik

vazifalar = [
    Vazifa("Email yuborish", ustuvorlik=2),
    Vazifa("Hisobot generatsiya qilish", ustuvorlik=1, cpu_bound=True),
    Vazifa("Fayl yuklab olish", ustuvorlik=3),
]
vazifalar.sort()   # ❗ сортируется по приоритету через __lt__</code></pre>

<h4>БЛОК 2 — выполнение I/O-bound задач через asyncio</h4>
<pre><code>import asyncio
import time
from functools import wraps

def vaqt_olchagich(func):                    # ❗ урок 1: декоратор
    @wraps(func)
    async def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = await func(*args, **kwargs)
        print(f"{args[0].nomi}: {time.time() - boshlanish:.2f}s")
        return natija
    return wrapper

@vaqt_olchagich
async def io_vazifani_bajarish(vazifa: Vazifa) -> str:    # ❗ урок 6: type hints
    await asyncio.sleep(1)                                  # ❗ урок 7: симулирует ожидание I/O
    return f"{vazifa.nomi} bajarildi"

async def main():
    io_vazifalar = [v for v in vazifalar if not v.cpu_bound]   # ❗ урок 5: list comprehension
    natijalar = await asyncio.gather(*(io_vazifani_bajarish(v) for v in io_vazifalar))
    print(natijalar)

asyncio.run(main())</code></pre>

<h4>БЛОК 3 — правильное разделение CPU-bound задач (решение с учётом GIL)</h4>
<pre><code># Вспомните урок 8: из-за GIL asyncio/threading НЕ ПОМОГАЮТ для CPU-bound задач.
# Поэтому CPU-bound задачи нужно выполнять ОТДЕЛЬНО, через multiprocessing:

from multiprocessing import Process

def cpu_vazifani_bajarish(vazifa: Vazifa) -> None:
    print(f"{vazifa.nomi} - CPU-bound, alohida protsessda bajarilmoqda...")
    # ... код, требующий много вычислений ...

cpu_vazifalar = [v for v in vazifalar if v.cpu_bound]
protsesslar = [Process(target=cpu_vazifani_bajarish, args=(v,)) for v in cpu_vazifalar]
# for p in protsesslar: p.start(); p.join()</code></pre>

<h3>🐛 Намеренная ошибка — прямой вызов CPU-bound кода ВНУТРИ async-функции</h3>
<pre><code>async def vazifani_bajarish(vazifa: Vazifa):
    if vazifa.cpu_bound:
        # ❌ ОШИБКА: CPU-bound (блокирующий) код прямо внутри корутины!
        natija = 0
        for i in range(50_000_000):
            natija += i
        return natija
    await asyncio.sleep(1)
    return "bajarildi"

async def main():
    await asyncio.gather(
        vazifani_bajarish(Vazifa("Email", 2)),
        vazifani_bajarish(Vazifa("Hisobot", 1, cpu_bound=True)),   # ❗ это "замораживает" ВЕСЬ event loop!
    )
# Результат: даже задача "Email" ЖДЁТ завершения Hisobot - хотя они
# должны выполняться "одновременно"! asyncio работает в одном потоке.</code></pre>

<p><strong>Результат:</strong> <code>asyncio</code> работает в <strong>одном</strong> потоке (thread) и переключается между задачами только в точках <code>await</code> (урок 7). Если внутри корутины прямо написан <strong>блокирующий</strong> (долгий, без <code>await</code>) CPU-bound код, он <strong>занимает</strong> весь event loop, не доходя до точки <code>await</code> — никакая другая корутина (даже просто ожидающая <code>asyncio.sleep(1)</code>) в это время не работает. Это напрямую связано с темой GIL из урока 8: CPU-bound работу нужно не помещать внутрь <code>asyncio</code>, а выносить в <strong>отдельный процесс</strong> (<code>multiprocessing</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему для Vazifa вместе используются @dataclass и __lt__?</h4>
<p><code>@dataclass</code> автоматически даёт <code>__init__</code>/<code>__repr__</code>/<code>__eq__</code>, но <strong>не даёт</strong> <code>__lt__</code> (эта логика сравнения специфична для проекта и не создаётся автоматически). Поэтому, если нужна сортировка, <code>__lt__</code> нужно добавить <strong>вручную</strong> — это продолжение принципа из урока 9.</p>

<h4>2. Почему I/O-bound и CPU-bound задачи используются ОТДЕЛЬНО?</h4>
<p>Как мы видели в уроке 8, из-за GIL <code>asyncio</code> (и <code>threading</code>) не ускоряют CPU-bound работу. Поэтому задачи нужно <strong>разделять</strong> по типу: I/O-bound задачи выполняются через <code>asyncio.gather()</code> (одновременно, эффективно), CPU-bound задачи &mdash; через <code>multiprocessing</code> (в настоящих параллельных процессах).</p>

<h4>3. Почему написание CPU-bound кода внутри корутины — ошибка?</h4>
<p><code>asyncio</code> основан на кооперативности (cooperative) — корутина сообщает "переключитесь на другую задачу" только в точке <code>await</code>. Если внутри корутины есть долгий обычный Python-код без <code>await</code> (например большой цикл <code>for</code>), он никогда не "уступает" — это блокирует весь event loop, и главное преимущество <code>asyncio</code> (управление многими задачами одновременно) теряется.</p>

<h4>4. Почему декоратор @vaqt_olchagich работает с async-функцией?</h4>
<p>В отличие от простого декоратора из урока 1, здесь <code>wrapper</code> тоже объявлен как <code>async def</code> и внутри использует <code>await func(...)</code> &mdash; потому что wrapper, "оборачивающий" <code>async</code>-функцию, тоже должен быть корутиной и вызывать исходную корутину через <code>await</code>.</p>

<h4>5. Какие концепции из 9 уроков объединяет этот проект?</h4>
<p>Декоратор (урок 1), list comprehension (урок 5), type hints (урок 6), asyncio/await/gather (урок 7), решение с учётом GIL о I/O vs CPU-bound (урок 8), <code>@dataclass</code> и <code>__lt__</code> (урок 9) &mdash; всё это работает вместе для принятия одного реального архитектурного решения (направление задач в правильный механизм исполнения).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>@dataclass</code> + написанный вручную <code>__lt__</code> — делает класс данных сортируемым</li>
<li>✅ I/O-bound задачи должны выполняться через <code>asyncio.gather()</code>, CPU-bound — через <code>multiprocessing</code></li>
<li>✅ Блокирующий (долгий, без <code>await</code>) код внутри корутины "замораживает" весь event loop</li>
<li>✅ Async-декораторы тоже должны использовать <code>async def</code> и <code>await</code></li>
<li>✅ Все основные концепции 9 уроков объединяются в реальных архитектурных решениях</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# REVIEW 2 (CAPSTONE): Исполнитель задач
# ════════════════════════════════════════════════════════════════════

import asyncio
import time
from dataclasses import dataclass
from functools import wraps


@dataclass
class Vazifa:
    nomi: str
    ustuvorlik: int
    cpu_bound: bool = False

    def __lt__(self, boshqa):
        return self.ustuvorlik < boshqa.ustuvorlik


def vaqt_olchagich(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = await func(*args, **kwargs)
        print(f"{args[0].nomi}: {time.time() - boshlanish:.2f}s")
        return natija
    return wrapper


@vaqt_olchagich
async def io_vazifani_bajarish(vazifa: Vazifa) -> str:
    await asyncio.sleep(1)
    return f"{vazifa.nomi} bajarildi"


async def main():
    vazifalar = [
        Vazifa("Email yuborish", ustuvorlik=2),
        Vazifa("Hisobot generatsiya qilish", ustuvorlik=1, cpu_bound=True),
        Vazifa("Fayl yuklab olish", ustuvorlik=3),
    ]
    vazifalar.sort()

    io_vazifalar = [v for v in vazifalar if not v.cpu_bound]
    natijalar = await asyncio.gather(*(io_vazifani_bajarish(v) for v in io_vazifalar))
    print(natijalar)


asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# Разделение CPU-bound задач через multiprocessing (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# from multiprocessing import Process
#
# def cpu_vazifani_bajarish(vazifa: Vazifa) -> None:
#     print(f"{vazifa.nomi} - CPU-bound, alohida protsessda bajarilmoqda...")
#
# cpu_vazifalar = [v for v in vazifalar if v.cpu_bound]
# protsesslar = [Process(target=cpu_vazifani_bajarish, args=(v,)) for v in cpu_vazifalar]
# for p in protsesslar: p.start(); p.join()

# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка - вызов CPU-bound кода внутри корутины (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# async def vazifani_bajarish_xato(vazifa):
#     if vazifa.cpu_bound:
#         natija = 0
#         for i in range(50_000_000):   # ❌ блокирующий, CPU-bound код без await!
#             natija += i
#         return natija
#     await asyncio.sleep(1)
#     return "bajarildi"
"""

EX = {
    4254: {
        "title": "Почему в @dataclass __lt__ нужно писать вручную?",
        "description": "@dataclass автоматически даёт __init__/__repr__/__eq__, но почему __lt__ нужно писать вручную?",
        "hint": "Как @dataclass узнает, по какому полю сортировать?",
        "explanation": "@dataclass автоматически создаёт __init__/__repr__/__eq__, но не даёт __lt__, потому что логика сравнения (по какому полю или логике) специфична для проекта — это должен указать разработчик вручную.",
    },
    4255: {
        "title": "Почему I/O-bound и CPU-bound задачи используются отдельно?",
        "description": "В системе исполнения задач почему I/O-bound задачи выполняются через asyncio, а CPU-bound — отдельно через multiprocessing?",
        "hint": "Вспомните урок 8.",
        "explanation": "Из-за GIL asyncio/threading не ускоряют CPU-bound работу (урок 8), поэтому I/O-bound задачи выполняются через asyncio.gather(), а CPU-bound задачи — отдельно через multiprocessing.",
    },
    4256: {
        "title": "Расположите процесс работы исполнителя задач",
        "description": "Расположите процесс подготовки и запуска списка задач в функции main().",
        "hint": "",
        "explanation": "",
    },
    4257: {
        "title": "Правильный модуль для CPU-bound задач",
        "description": "Какой модуль нужно использовать для получения настоящего параллелизма в CPU-bound задачах из-за GIL? (напишите название)",
        "hint": "",
        "expected_answer": "multiprocessing",
    },
    4258: {
        "title": "Почему CPU-bound код внутри корутины блокирует весь event loop?",
        "description": (
            "Если внутри корутины vazifani_bajarish_xato() для задачи с "
            "cpu_bound=True выполняется цикл 50 миллионов раз (без "
            "await), почему в это время не работают ДРУГИЕ корутины "
            "(даже просто ожидающие asyncio.sleep(1))? Объясните своими "
            "словами."
        ),
        "hint": "asyncio переключается между корутинами в любой момент, или только в точках await?",
        "expected_answer": "asyncio работает в одном потоке (thread) кооперативным образом — переключение между корутинами происходит ТОЛЬКО в точках await, то есть когда корутина сама подаёт сигнал \"я сейчас жду, пусть работает другая задача\". Если внутри корутины есть долгий обычный Python-код без await (например цикл 50 миллионов раз), этот код никогда не \"уступает\" — пока он не завершится, единственный поток полностью занят. В результате все остальные корутины (даже те, что просто выполняют простое ожидание вроде asyncio.sleep(1)) вообще не запускаются, пока этот блокирующий код не завершится — это сводит на нет главное преимущество asyncio (управление многими задачами одновременно).",
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
