"""Russian translation for Python: Ilg'or Mavzular, lesson order=2 (L3)."""
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

LESSON_ID = 714

TITLE_RU = "3-Контекстные менеджеры"

TEXT_RU = """\
<h2>Контекстные менеджеры — безопасное открытие и закрытие ресурсов</h2>

<pre class="mermaid">
flowchart LR
    WITH["with ochish(...) as f:"] --> ENTER["вызывается __enter__()"]
    ENTER --> BLOCK["выполняется код блока"]
    BLOCK --> EXIT["__exit__() вызывается ВСЕГДА"]
    BLOCK -->|даже при ошибке| EXIT
</pre>

<p>После использования <strong>ресурсов</strong> вроде открытия файла, подключения к базе данных, блокировки (lock), их <strong>обязательно нужно закрыть</strong> — даже если произошла ошибка. <strong>Контекстный менеджер</strong> (оператор <code>with</code>) автоматизирует этот процесс.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — with при работе с файлом</h4>
<pre><code># Без with - нужно закрывать вручную, и при ошибке файл может не закрыться
f = open("malumot.txt", "w")
f.write("Salom")
f.close()          # ❗ если write() выдаст ошибку, close() НИКОГДА не вызовется!

# С with - закрывается АВТОМАТИЧЕСКИ, даже при ошибке
with open("malumot.txt", "w") as f:    # ❗ вызывается __enter__(), возвращается f
    f.write("Salom")                    # ❗ даже если здесь произойдёт ошибка...
# ❗ после завершения блока (или даже при ошибке) __exit__() вызывается АВТОМАТИЧЕСКИ - файл закрывается</code></pre>

<h4>БЛОК 2 — создание собственного контекстного менеджера через класс</h4>
<pre><code>class BazaUlanishi:
    def __enter__(self):                          # ❗ вызывается при начале 'with'
        print("Ulanish ochildi")
        return self                                # ❗ передаётся переменной после 'as'

    def __exit__(self, exc_type, exc_value, traceback):  # ❗ вызывается при завершении блока 'with' (даже при ошибке)
        print("Ulanish yopildi")
        return False                                # ❗ False - не "проглатывать" ошибку, передать её выше

with BazaUlanishi() as baza:
    print("Baza bilan ishlash...")
# Результат: "Ulanish ochildi" -> "Baza bilan ishlash..." -> "Ulanish yopildi"</code></pre>

<h4>БЛОК 3 — contextlib.contextmanager: более короткая запись</h4>
<pre><code>from contextlib import contextmanager

@contextmanager                       # ❗ превращает функцию-генератор в контекстный менеджер
def baza_ulanishi():
    print("Ulanish ochildi")
    yield "baza-obyekti"               # ❗ часть до yield - роль __enter__, после yield - роль __exit__
    print("Ulanish yopildi")

with baza_ulanishi() as baza:
    print(f"Ishlatilmoqda: {baza}")
# Результат тот же, что и при написании через класс, но короче</code></pre>

<h3>🐛 Намеренная ошибка — написан только __enter__, без __exit__</h3>
<pre><code>class YomonManager:
    def __enter__(self):
        print("Ochildi")
        return self
    # МЕТОДА __exit__ НЕТ!

with YomonManager() as m:
    print("Ishlatilmoqda")

# ❌ Ошибка: AttributeError: __exit__
# (оператор 'with' требует ОБА метода, одного __enter__ недостаточно!)</code></pre>

<p><strong>Результат:</strong> для работы оператора <code>with</code> у объекта <strong>обязательно</strong> должны быть <strong>оба</strong> метода &mdash; <code>__enter__</code> И <code>__exit__</code>. Если написан только <code>__enter__</code>, а <code>__exit__</code> забыт, Python при выходе из блока <code>with</code> пытается вызвать <code>__exit__</code> и, не найдя его, выдаёт <code>AttributeError</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен контекстный менеджер?</h4>
<p>После использования ресурсов (файл, сетевое соединение, lock) их <strong>обязательно</strong> нужно закрыть/очистить &mdash; даже если внутри произошла ошибка. Оператор <code>with</code> <strong>автоматически</strong> обеспечивает эту логику "всегда закрывать", избавляя разработчика от необходимости вручную писать <code>try/finally</code>.</p>

<h4>2. Когда вызываются __enter__ и __exit__?</h4>
<p><code>__enter__()</code> вызывается <strong>при начале</strong> блока <code>with</code>, его возвращаемое значение передаётся переменной после <code>as</code>. <code>__exit__()</code> вызывается <strong>при завершении</strong> блока <code>with</code>, <strong>даже если внутри произошла ошибка (exception)</strong> &mdash; это гарантировано.</p>

<h4>3. Зачем нужны 3 аргумента у __exit__?</h4>
<p><code>__exit__(self, exc_type, exc_value, traceback)</code> &mdash; если в блоке <code>with</code> произошла ошибка, эти аргументы дают информацию о ней (тип ошибки, значение, traceback). Если ошибки не было, все они равны <code>None</code>. Если <code>__exit__</code> возвращает <code>True</code>, ошибка "проглатывается" (подавляется), если <code>False</code> (или ничего не возвращает), ошибка передаётся выше.</p>

<h4>4. Что делает декоратор @contextmanager?</h4>
<p><code>contextlib.contextmanager</code> превращает обычную функцию-генератор в контекстный менеджер <strong>без написания полного класса</strong>: код до <code>yield</code> выполняет роль <code>__enter__</code>, код после <code>yield</code> — роль <code>__exit__</code>. Это намного более короткая запись для небольших контекстных менеджеров.</p>

<h4>5. Почему без __exit__ возникает AttributeError?</h4>
<p>Оператор <code>with</code> определён в Python как <strong>протокол</strong> &mdash; он требует наличия у объекта <strong>обоих</strong> методов (<code>__enter__</code> И <code>__exit__</code>). При завершении блока Python <strong>автоматически</strong> пытается вызвать <code>__exit__</code>; если этого метода нет, по обычному правилу Python возникает <code>AttributeError</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Оператор <code>with</code> автоматизирует открытие/закрытие ресурсов, даже при ошибке</li>
<li>✅ <code>__enter__</code> вызывается в начале блока, <code>__exit__</code> — при его завершении (даже при ошибке)</li>
<li>✅ Аргументы <code>__exit__</code> дают информацию об ошибке; возврат <code>True</code> подавляет ошибку</li>
<li>✅ <code>@contextlib.contextmanager</code> — создаёт более короткий контекстный менеджер через генератор</li>
<li>✅ Для <code>with</code> обязательно должны быть и <code>__enter__</code>, и <code>__exit__</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 3: Контекстные менеджеры
# ════════════════════════════════════════════════════════════════════

from contextlib import contextmanager

# ─────────────────────────────────────────────────────────────────────
# 1) with при работе с файлом (в комментарии - для примера)
# ─────────────────────────────────────────────────────────────────────

# with open("malumot.txt", "w") as f:
#     f.write("Salom")

# ─────────────────────────────────────────────────────────────────────
# 2) Создание собственного контекстного менеджера через класс
# ─────────────────────────────────────────────────────────────────────


class BazaUlanishi:
    def __enter__(self):
        print("Ulanish ochildi")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Ulanish yopildi")
        return False


with BazaUlanishi() as baza:
    print("Baza bilan ishlash...")

# ─────────────────────────────────────────────────────────────────────
# 3) Более короткая запись через contextlib.contextmanager
# ─────────────────────────────────────────────────────────────────────


@contextmanager
def baza_ulanishi():
    print("Ulanish ochildi")
    yield "baza-obyekti"
    print("Ulanish yopildi")


with baza_ulanishi() as baza:
    print(f"Ishlatilmoqda: {baza}")

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - класс без __exit__ (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class YomonManager:
#     def __enter__(self):
#         print("Ochildi")
#         return self
#     # МЕТОДА __exit__ НЕТ!
#
# with YomonManager() as m:
#     print("Ishlatilmoqda")
# ❌ AttributeError: __exit__
"""

EX = {
    4176: {
        "title": "Для чего используется оператор with?",
        "description": "Для чего в основном используется оператор with?",
        "hint": "Это избавляет от необходимости писать try/finally.",
        "explanation": "Оператор with автоматически обеспечивает обязательное закрытие/очистку ресурсов после использования, даже если внутри произошла ошибка.",
    },
    4177: {
        "title": "Когда вызывается __exit__?",
        "description": "Когда вызывается метод __exit__?",
        "hint": "Это гарантированный механизм очистки.",
        "explanation": "__exit__ вызывается при завершении блока with — это гарантировано, даже если внутри блока произошла ошибка (exception).",
    },
    4178: {
        "title": "Расположите процесс работы with BazaUlanishi() as baza:",
        "description": "Расположите процесс работы блока with BazaUlanishi() as baza.",
        "hint": "",
        "explanation": "",
    },
    4179: {
        "title": "Декоратор для создания контекстного менеджера через генератор",
        "description": "Напишите название декоратора из модуля contextlib, превращающего обычную функцию-генератор в контекстный менеджер.",
        "hint": "Используется в форме @contextlib.___.",
        "expected_answer": "contextmanager",
    },
    4180: {
        "title": "Почему без __exit__ возникает AttributeError?",
        "description": (
            "В классе YomonManager написан только __enter__, __exit__ "
            "нет. Почему при завершении блока with YomonManager() as m "
            "выдаётся ошибка AttributeError? Объясните своими словами."
        ),
        "hint": "Какие именно методы требует оператор with от объекта?",
        "expected_answer": "Оператор with определён в Python как чёткий протокол — для его работы у объекта обязательно должны существовать оба метода, и __enter__, и __exit__. При завершении блока with (или при возникновении ошибки) Python автоматически пытается вызвать метод __exit__ этого объекта, потому что именно через этот метод выполняется \"очистка\" ресурса. Так как в классе YomonManager метод __exit__ вообще не написан, Python не может найти этот метод и по обычному правилу Python выдаёт ошибку AttributeError.",
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
