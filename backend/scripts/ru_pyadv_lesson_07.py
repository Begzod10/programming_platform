"""Russian translation for Python: Ilg'or Mavzular, lesson order=7 (L7)."""
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

LESSON_ID = 724

TITLE_RU = "7-Основы asyncio"

TEXT_RU = """\
<h2>Основы asyncio — выполнение другой работы во время ожидания</h2>

<pre class="mermaid">
flowchart LR
    MAIN["asyncio.run(main())"] --> T1["vazifa1() - ожидает сетевой запрос..."]
    MAIN --> T2["vazifa2() - ожидает сетевой запрос..."]
    T1 -->|во время ожидания| T2
    T2 -->|во время ожидания| T1
    T1 --> DONE["оба завершаются почти ОДНОВРЕМЕННО"]
</pre>

<p>Многие функции (сетевой запрос, чтение файла, запрос к базе данных) связаны с <strong>ожиданием</strong> — программа ждёт ответа, ничего не делая. <code>asyncio</code> позволяет во время этого "ожидания" выполнять <strong>другие задачи</strong>, в рамках одного потока (thread).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первая async-функция (корутина)</h4>
<pre><code>import asyncio

async def salomlash(ism):              # ❗ 'async def' - это функция-корутина
    print(f"{ism} - boshlandi")
    await asyncio.sleep(1)              # ❗ 'await' - ожидание, но с возможностью переключения на ДРУГИЕ задачи
    print(f"{ism} - tugadi")

asyncio.run(salomlash("Olim"))          # ❗ asyncio.run() - запускает event loop</code></pre>

<h4>БЛОК 2 — asyncio.gather: выполнение нескольких задач ОДНОВРЕМЕННО</h4>
<pre><code>import time

async def main():
    boshlanish = time.time()

    # Последовательное выполнение - занимает 3 секунды (1+1+1)
    # await salomlash("Olim")
    # await salomlash("Vali")
    # await salomlash("Ali")

    # С gather - ВСЕ начинаются ОДНОВРЕМЕННО - всего 1 секунда!
    await asyncio.gather(
        salomlash("Olim"),
        salomlash("Vali"),
        salomlash("Ali"),
    )

    print(f"Jami vaqt: {time.time() - boshlanish:.2f} soniya")

asyncio.run(main())   # "Jami vaqt: 1.00 soniya" (не 3.00!)</code></pre>

<h4>БЛОК 3 — разница между корутиной (asyncio) и потоком (thread)</h4>
<pre><code># asyncio - в рамках ОДНОГО потока (thread), переключается на другую задачу во время "ожидания"
# Это очень эффективно для I/O-bound задач: сетевые запросы, операции с файлами/базой
# (потому что в это время процессор "простаивает", и это время можно отдать другой задаче)

# threading - НАСТОЯЩИЕ несколько потоков, параллельно на уровне процессора (но в Python из-за GIL
# для CPU-bound задач настоящего параллелизма нет - подробно рассмотрим в уроке 8)

# Краткое правило:
# Много ожидания I/O (сеть, файл)  -> asyncio
# Много вычислений CPU             -> multiprocessing (урок 8)</code></pre>

<h3>🐛 Намеренная ошибка — забыли await, вызвали корутину напрямую</h3>
<pre><code>async def salomlash(ism):
    await asyncio.sleep(1)
    return f"Salom, {ism}!"

async def main():
    natija = salomlash("Olim")   # ❗ НЕТ 'await'!
    print(natija)                  # ❌ "<coroutine object salomlash at 0x...>"
    # Корутина НИКОГДА не запустилась - создан лишь "план"!

asyncio.run(main())</code></pre>

<p><strong>Результат:</strong> вызов функции, объявленной через <code>async def</code>, <strong>не запускает её сразу</strong> &mdash; он лишь создаёт <strong>объект-корутину</strong> ("план, который нужно выполнить"). Чтобы действительно <strong>выполнить</strong> этот план, его обязательно нужно передать в <code>await</code> или в event loop через <code>asyncio.run()</code>/<code>asyncio.gather()</code>. Без <code>await</code> корутина никогда не выполняется, и через print выводится лишь текст "coroutine object".</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое async/await?</h4>
<p><code>async def</code> объявляет функцию как <strong>корутину</strong> (функцию, которую можно "ожидать"). <code>await</code> внутри корутины отмечает точку "ожидания" другой корутины (или чего-то ожидаемого) — в этой точке Python может переключиться на другие задачи.</p>

<h4>2. Зачем нужен asyncio.gather()?</h4>
<p><code>await</code> нескольких корутин <strong>последовательно</strong> выполняет их одну за другой, по очереди (общее время — сумма всех). <code>asyncio.gather()</code> запускает их <strong>одновременно</strong>, не складывая их времена "ожидания", выполняя почти параллельно.</p>

<h4>3. Когда полезен asyncio (I/O-bound)?</h4>
<p><code>asyncio</code> особенно полезен для <strong>I/O-bound</strong> задач — когда программа тратит большую часть времени не на работу процессора, а на <strong>ожидание внешнего ответа</strong> (сеть, файл, база данных). Во время ожидания процессор "простаивает", и <code>asyncio</code> использует это время для выполнения другой задачи.</p>

<h4>4. Разница между asyncio и threading</h4>
<p><code>asyncio</code> работает в рамках <strong>одного</strong> потока, переключаясь между задачами только в точках "ожидания". <code>threading</code> же создаёт <strong>несколько</strong> настоящих потоков. Но в Python из-за GIL (Global Interpreter Lock) threading не даёт настоящего параллелизма для CPU-bound (много вычислений) задач — подробно это рассмотрим в уроке 8.</p>

<h4>5. Почему корутина не работает без await?</h4>
<p>Вызов функции <code>async def</code> создаёт только <strong>объект-корутину</strong> — это сам "план, который нужно выполнить", ещё <strong>не выполненный</strong>. Чтобы <strong>действительно запустить</strong> этот план, его обязательно нужно передать в <code>await</code> (или в <code>asyncio.run()</code>/<code>gather()</code>) — это равносильно тому, чтобы сказать Python: "теперь выполни этот план".</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>async def</code> создаёт функцию-корутину, <code>await</code> отмечает точку ожидания</li>
<li>✅ <code>asyncio.run()</code> запускает event loop и выполняет корутину</li>
<li>✅ <code>asyncio.gather()</code> выполняет несколько корутин одновременно (параллельно)</li>
<li>✅ asyncio подходит для I/O-bound (много ожидания) задач, multiprocessing — для CPU-bound задач</li>
<li>✅ Корутина, вызванная без await, никогда не выполняется, создаётся лишь объект</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 7: Основы asyncio
# ════════════════════════════════════════════════════════════════════

import asyncio
import time

# ─────────────────────────────────────────────────────────────────────
# 1) Первая async-функция (корутина)
# ─────────────────────────────────────────────────────────────────────


async def salomlash(ism):
    print(f"{ism} - boshlandi")
    await asyncio.sleep(1)
    print(f"{ism} - tugadi")


asyncio.run(salomlash("Olim"))

# ─────────────────────────────────────────────────────────────────────
# 2) asyncio.gather - выполнение нескольких задач одновременно
# ─────────────────────────────────────────────────────────────────────


async def main():
    boshlanish = time.time()

    await asyncio.gather(
        salomlash("Olim"),
        salomlash("Vali"),
        salomlash("Ali"),
    )

    print(f"Jami vaqt: {time.time() - boshlanish:.2f} soniya")


asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - забыли await (в комментарии)
# ─────────────────────────────────────────────────────────────────────


async def salomlash2(ism):
    await asyncio.sleep(1)
    return f"Salom, {ism}!"


# async def main_xato():
#     natija = salomlash2("Olim")   # НЕТ await!
#     print(natija)                  # ❌ "<coroutine object salomlash2 at 0x...>"
#
# asyncio.run(main_xato())
"""

EX = {
    4224: {
        "title": "Для чего используется async/await?",
        "description": "Для каких ситуаций в основном используется async/await?",
        "hint": "Сетевой запрос или чтение файла - программа часто просто ждёт.",
        "explanation": "async/await используется в задачах, связанных с ожиданием (I/O) — сетевой запрос, чтение файла — позволяя во время ожидания выполнять другие задачи.",
    },
    4225: {
        "title": "Что делает asyncio.gather()?",
        "description": "Что делает asyncio.gather(vazifa1(), vazifa2(), vazifa3())?",
        "hint": "Это быстрее, чем последовательный await.",
        "explanation": "asyncio.gather() запускает все переданные корутины одновременно, выполняя их почти параллельно, не складывая их время \"ожидания\".",
    },
    4226: {
        "title": "Расположите процесс работы с asyncio.gather",
        "description": "Расположите процесс работы await asyncio.gather(salomlash('Olim'), salomlash('Vali')).",
        "hint": "",
        "explanation": "",
    },
    4227: {
        "title": "Функция, запускающая event loop",
        "description": "Напишите функцию, используемую в asyncio для запуска самой внешней корутины (например: asyncio.___(main())).",
        "hint": "",
        "expected_answer": "run",
    },
    4228: {
        "title": "Почему корутина не работает без await?",
        "description": (
            "Если написать natija = salomlash2(\"Olim\") (без await), а "
            "затем вызвать print(natija), почему сама функция не "
            "выполняется, а выводится только текст \"<coroutine "
            "object ...>\"? Объясните своими словами."
        ),
        "hint": "Вызов async-функции СРАЗУ ЗАПУСКАЕТ её, или только создаёт \"план\"?",
        "expected_answer": "Вызов функции, объявленной через async def, не запускает её сразу — он лишь создаёт объект-корутину, представляющий \"план, который нужно выполнить\", при этом ни один код ещё не выполнен. Чтобы действительно выполнить этот план, его обязательно нужно передать в await или в event loop через asyncio.run()/gather(). Так как await не написан, Python никогда не запускает корутину, поэтому при вызове print(natija) выводится не результат функции, а сам ещё не выполненный объект-корутина (\"<coroutine object ...>\").",
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
