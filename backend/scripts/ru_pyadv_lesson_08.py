"""Russian translation for Python: Ilg'or Mavzular, lesson order=8 (L8)."""
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

LESSON_ID = 726

TITLE_RU = "8-Threading vs Multiprocessing (GIL)"

TEXT_RU = """\
<h2>Threading vs Multiprocessing — что такое GIL и когда что использовать</h2>

<pre class="mermaid">
flowchart LR
    GIL["GIL - одновременно только 1 поток выполняет Python bytecode"] --> CPU["CPU-bound: threading НЕ ПОМОГАЕТ"]
    GIL --> IO["I/O-bound: threading ПОМОГАЕТ (GIL освобождается во время ожидания)"]
    MP["multiprocessing - У КАЖДОГО процесса свой GIL"] --> CPUFAST["CPU-bound: настоящий параллелизм"]
</pre>

<p>В уроке 7 мы рассмотрели <code>asyncio</code>. Теперь разберём самую запутанную тему Python — <strong>GIL (Global Interpreter Lock)</strong> — и как он влияет на <code>threading</code> и <code>multiprocessing</code>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — что такое GIL?</h4>
<pre><code># GIL (Global Interpreter Lock) - "замок" в CPython, обеспечивающий, что
# в один момент времени ТОЛЬКО ОДИН поток выполняет Python bytecode

# Это означает: код, кажущийся "параллельным" при работе с threading,
# на самом деле на уровне процессора НЕ является настоящим параллелизмом -
# потоки работают по очереди, очень быстро переключаясь между собой</code></pre>

<h4>БЛОК 2 — threading: НЕТ пользы для CPU-bound работы</h4>
<pre><code>import threading
import time

def hisoblash():
    natija = 0
    for i in range(50_000_000):     # ❗ CPU-bound - только вычисления, без ожидания
        natija += i

boshlanish = time.time()
t1 = threading.Thread(target=hisoblash)
t2 = threading.Thread(target=hisoblash)
t1.start(); t2.start()
t1.join(); t2.join()
print(f"2 thread bilan: {time.time() - boshlanish:.2f}s")
# ❗ Результат НЕ БЫСТРЕЕ, чем с одним потоком - из-за GIL!</code></pre>

<h4>БЛОК 3 — multiprocessing: настоящее ускорение для CPU-bound работы</h4>
<pre><code>from multiprocessing import Process
import time

def hisoblash():
    natija = 0
    for i in range(50_000_000):
        natija += i

if __name__ == "__main__":
    boshlanish = time.time()
    p1 = Process(target=hisoblash)      # ❗ Process - создаёт отдельный процесс со своим GIL
    p2 = Process(target=hisoblash)
    p1.start(); p2.start()
    p1.join(); p2.join()
    print(f"2 protsess bilan: {time.time() - boshlanish:.2f}s")
    # ✅ На этот раз НАСТОЯЩЕЕ ускорение - у каждого процесса свой независимый GIL!</code></pre>

<h3>🐛 Намеренная ошибка — выбор threading для CPU-bound задачи</h3>
<pre><code># Обработка изображений (требует много вычислений) - CPU-bound задача
import threading

def rasmni_qayta_ishlash(rasm):
    # ... много вычислений CPU (обработка пикселей) ...
    pass

threadlar = [threading.Thread(target=rasmni_qayta_ishlash, args=(r,)) for r in rasmlar]
# ❌ Это НЕ ПОМОГАЕТ! Из-за GIL, в один момент реально работает только один поток
# Код "выглядит параллельным", но скорость почти такая же, как с одним потоком</code></pre>

<p><strong>Результат:</strong> обработка изображений &mdash; <strong>CPU-bound</strong> задача (много вычислений, мало ожидания). Из-за GIL, даже если создано несколько потоков через <code>threading</code>, они <strong>не могут</strong> одновременно выполнять Python bytecode &mdash; настоящего параллелизма на уровне процессора <strong>нет</strong>. Правильное решение &mdash; <code>multiprocessing</code>, так как каждый процесс имеет свой независимый GIL и реально работает параллельно на разных ядрах процессора.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое GIL?</h4>
<p><strong>GIL (Global Interpreter Lock)</strong> &mdash; внутренний механизм CPython, обеспечивающий, что в один момент времени <strong>только один</strong> поток выполняет Python bytecode. Это сделано для упрощения управления памятью, но в результате Python threading не даёт настоящего параллелизма для CPU-bound работы.</p>

<h4>2. Почему threading работает для I/O-bound, но не для CPU-bound?</h4>
<p>Во время ожидания I/O (например ожидания сетевого ответа) поток <strong>освобождает</strong> GIL &mdash; в это время может работать другой поток. Но при CPU-bound вычислениях поток <strong>постоянно</strong> занимает GIL, почти не оставляя возможности другому потоку &mdash; поэтому ни <code>asyncio</code> из урока 7, ни <code>threading</code> не ускоряют CPU-bound работу.</p>

<h4>3. Почему multiprocessing даёт настоящее ускорение?</h4>
<p><code>multiprocessing</code> создаёт для каждой задачи <strong>отдельный процесс Python</strong>, и у каждого процесса <strong>свой GIL</strong>. Поэтому процессы реально работают <strong>параллельно</strong> на разных ядрах процессора &mdash; это даёт настоящее ускорение для CPU-bound задач.</p>

<h4>4. Когда что использовать (краткое правило)?</h4>
<p><strong>I/O-bound</strong> (сеть, файл, база — много ожидания): <code>asyncio</code> (урок 7) или <code>threading</code>. <strong>CPU-bound</strong> (много вычислений, обработка изображений/видео, сложные алгоритмы): <code>multiprocessing</code>. Выбор неверного инструмента — код "работает", но не даёт ожидаемого ускорения.</p>

<h4>5. Почему threading не помогает в CPU-bound задаче?</h4>
<p>GIL даёт право выполнять Python-код только одному потоку в момент времени. В CPU-bound задаче потоки почти <strong>никогда</strong> не переходят в ожидание (не освобождают GIL), поэтому они работают по очереди, последовательно — создание нескольких потоков добавляет дополнительные накладные расходы (overhead), но не даёт настоящей скорости.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ GIL обеспечивает, что в один момент только один поток выполняет Python bytecode</li>
<li>✅ threading полезен для I/O-bound работы (GIL освобождается во время ожидания)</li>
<li>✅ threading не помогает в CPU-bound работе (GIL постоянно занят)</li>
<li>✅ multiprocessing даёт каждому процессу отдельный GIL — настоящий параллелизм для CPU-bound</li>
<li>✅ Правило: I/O-bound → asyncio/threading, CPU-bound → multiprocessing</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 8: Threading vs Multiprocessing (GIL)
# ════════════════════════════════════════════════════════════════════

import threading
import time
from multiprocessing import Process

# ─────────────────────────────────────────────────────────────────────
# 1) threading - нет пользы для CPU-bound работы
# ─────────────────────────────────────────────────────────────────────


def hisoblash():
    natija = 0
    for i in range(50_000_000):
        natija += i


def threading_sinov():
    boshlanish = time.time()
    t1 = threading.Thread(target=hisoblash)
    t2 = threading.Thread(target=hisoblash)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"2 thread bilan: {time.time() - boshlanish:.2f}s")

# ─────────────────────────────────────────────────────────────────────
# 2) multiprocessing - настоящая скорость для CPU-bound работы
# ─────────────────────────────────────────────────────────────────────


def multiprocessing_sinov():
    boshlanish = time.time()
    p1 = Process(target=hisoblash)
    p2 = Process(target=hisoblash)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"2 protsess bilan: {time.time() - boshlanish:.2f}s")


if __name__ == "__main__":
    threading_sinov()
    multiprocessing_sinov()

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - threading для CPU-bound задачи (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def rasmni_qayta_ishlash(rasm):
#     pass  # много вычислений CPU
#
# threadlar = [threading.Thread(target=rasmni_qayta_ishlash, args=(r,)) for r in rasmlar]
# ❌ Из-за GIL это не помогает!
"""

EX = {
    4234: {
        "title": "Что такое GIL?",
        "description": "Что обеспечивает GIL (Global Interpreter Lock)?",
        "hint": "Это внутренний \"замок\" CPython.",
        "explanation": "GIL — внутренний механизм CPython, обеспечивающий, что в один момент времени только один поток выполняет Python bytecode.",
    },
    4235: {
        "title": "Когда полезен threading?",
        "description": "Для каких задач полезен модуль threading?",
        "hint": "Во время ожидания GIL освобождается.",
        "explanation": "threading полезен для I/O-bound задач (сеть, файл — много ожидания), потому что во время ожидания поток освобождает GIL, и может работать другой поток.",
    },
    4236: {
        "title": "Расположите причину скорости multiprocessing в CPU-bound задаче",
        "description": "Расположите, почему выполнение CPU-bound вычислений через два Process реально быстрее.",
        "hint": "",
        "explanation": "",
    },
    4237: {
        "title": "Модуль, подходящий для CPU-bound задачи",
        "description": "Какой модуль используется для получения настоящего параллелизма в CPU-bound (требующих много вычислений) задачах? (напишите название)",
        "hint": "",
        "expected_answer": "multiprocessing",
    },
    4238: {
        "title": "Почему threading не помогает в CPU-bound задаче?",
        "description": (
            "Если функция hisoblash() (требующая много CPU, без "
            "ожидания) выполняется через 2 threading.Thread, почему "
            "это не намного быстрее, чем выполнение одним потоком? "
            "Объясните своими словами."
        ),
        "hint": "Есть ли в функции hisoblash() какая-то точка ожидания, \"освобождающая\" GIL?",
        "expected_answer": "GIL даёт право выполнять Python bytecode только одному потоку в момент времени. В функции hisoblash() нет никакого ожидания (I/O) — она состоит только из вычислений, занимающих процессор, поэтому поток никогда не получает возможности \"освободить\" GIL. В результате, даже если созданы два потока, они выполняются не одновременно, а по очереди через GIL — это добавляет дополнительные накладные расходы на создание потоков (overhead), но не даёт настоящей скорости.",
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
