"""Russian translation for Python: Ilg'or Mavzular, lesson order=0 (L1)."""
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

LESSON_ID = 710

TITLE_RU = "1-Декораторы"

TEXT_RU = """\
<h2>Декораторы — "оборачивание" функции для добавления нового поведения</h2>

<pre class="mermaid">
flowchart LR
    ORIG["original_funksiya"] --> DEC["@декоратор"]
    DEC --> WRAP["wrapper(*args, **kwargs)"]
    WRAP -->|доп. код до| ORIG
    ORIG -->|результат| WRAP
    WRAP -->|доп. код после| RESULT["итоговый результат"]
</pre>

<p>Иногда нужно добавить функции дополнительное поведение (например, измерение времени выполнения, запись лога), <strong>не изменяя саму функцию</strong>. <strong>Декоратор</strong> &mdash; механизм Python, позволяющий "обернуть" функцию другой функцией, добавив вокруг неё дополнительный код.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — простой декоратор</h4>
<pre><code>def vaqt_olchagich(func):                    # ❗ декоратор — принимает функцию как аргумент
    def wrapper(*args, **kwargs):             # ❗ внутренняя функция — "оборачивает" исходную
        import time
        boshlanish = time.time()
        natija = func(*args, **kwargs)        # ❗ исходная функция вызывается здесь
        tugash = time.time()
        print(f"{func.__name__} {tugash - boshlanish:.4f} soniyada bajarildi")
        return natija
    return wrapper                             # ❗ возвращается функция wrapper

@vaqt_olchagich                                # ❗ синтаксис '@' - равносильно hisoblash = vaqt_olchagich(hisoblash)
def hisoblash(n):
    return sum(range(n))

hisoblash(1000000)   # выводит "hisoblash 0.0123 soniyada bajarildi"</code></pre>

<h4>БЛОК 2 — @wraps: сохранение метаданных</h4>
<pre><code>from functools import wraps

def vaqt_olchagich(func):
    @wraps(func)                                # ❗ сохраняет __name__, __doc__ и другие данные func
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))

print(hisoblash.__name__)   # "hisoblash" (✅ с @wraps)
print(hisoblash.__doc__)    # "n gacha bo'lgan sonlar yig'indisini hisoblaydi." (✅)</code></pre>

<h4>БЛОК 3 — декоратор с параметром (фабрика декораторов)</h4>
<pre><code>def takrorlash(necha_marta):                  # ❗ внешняя функция - принимает параметр
    def dekorator(func):                       # ❗ настоящий декоратор - здесь
        @wraps(func)
        def wrapper(*args, **kwargs):
            natija = None
            for _ in range(necha_marta):
                natija = func(*args, **kwargs)
            return natija
        return wrapper
    return dekorator                            # ❗ возвращается сам декоратор

@takrorlash(3)                                  # ❗ takrorlash(3) - создаёт декоратор, затем применяет его
def salomlash():
    print("Salom!")

salomlash()   # "Salom!" выводится 3 раза</code></pre>

<h3>🐛 Намеренная ошибка — забыли @wraps</h3>
<pre><code>def vaqt_olchagich(func):
    def wrapper(*args, **kwargs):    # ❗ НЕТ @wraps!
        return func(*args, **kwargs)
    return wrapper

@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))

print(hisoblash.__name__)   # ❌ "wrapper" (НЕ ожидаемое "hisoblash"!)
print(hisoblash.__doc__)    # ❌ None (исходный docstring ИСЧЕЗ!)</code></pre>

<p><strong>Результат:</strong> декоратор <strong>заменяет</strong> исходную функцию новой функцией по имени <code>wrapper</code>. Без <code>@wraps</code> метаданные вроде <code>hisoblash.__name__</code> и <code>hisoblash.__doc__</code> принадлежат не исходной функции <code>hisoblash</code>, а <code>wrapper</code> &mdash; это создаёт <strong>путаницу</strong> для отладки, генераторов документации и интроспекции (например <code>help()</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен декоратор?</h4>
<p>Декоратор позволяет добавить функции общее поведение (запись лога, измерение времени, кеширование, проверку прав), <strong>не изменяя её собственный код</strong>. Это используется для применения одинакового "дополнительного поведения" ко многим функциям без дублирования кода (DRY).</p>

<h4>2. Зачем в wrapper нужны *args, **kwargs?</h4>
<p>Декоратор должен уметь оборачивать функцию с <strong>любой</strong> сигнатурой — функция может принимать 0, 1 или 10 аргументов. <code>*args, **kwargs</code> позволяют wrapper передать <strong>любые пришедшие аргументы</strong> исходной функции без изменений.</p>

<h4>3. Почему важен @wraps?</h4>
<p>В Python функция тоже объект, и у неё есть метаданные вроде <code>__name__</code>, <code>__doc__</code>. При применении декоратора имя функции фактически заменяется на <code>wrapper</code>. <code>functools.wraps(func)</code> <strong>копирует</strong> эти метаданные от исходной функции в <code>wrapper</code>, чтобы внешний код (например отладчик, IDE) по-прежнему правильно "узнавал" функцию по имени.</p>

<h4>4. Как работает декоратор с параметром?</h4>
<p>При записи <code>@takrorlash(3)</code> сначала вызывается <code>takrorlash(3)</code> &mdash; это возвращает <strong>настоящий декоратор</strong> (функцию <code>dekorator</code>), и именно этот возвращённый декоратор затем применяется к <code>salomlash</code>. Поэтому декораторы с параметрами имеют трёхуровневую структуру (внешняя функция → декоратор → wrapper).</p>

<h4>5. Когда вызывается декоратор?</h4>
<p>Декоратор (строка <code>@декоратор</code>) выполняется один раз сразу <strong>при объявлении</strong> функции (заменяя функцию на <code>wrapper</code>). Код внутри <code>wrapper</code> же выполняется <strong>при каждом вызове</strong> функции.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Декоратор — механизм добавления функции дополнительного поведения без изменения её кода</li>
<li>✅ <code>*args, **kwargs</code> — необходимы, чтобы wrapper мог обернуть функцию с любой сигнатурой</li>
<li>✅ <code>@functools.wraps(func)</code> — сохраняет метаданные вроде <code>__name__</code>/<code>__doc__</code></li>
<li>✅ Декоратор с параметром — трёхуровневая структура: внешняя функция → декоратор → wrapper</li>
<li>✅ Декоратор выполняется один раз при объявлении, wrapper — при каждом вызове</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 1: Декораторы
# ════════════════════════════════════════════════════════════════════

from functools import wraps
import time


# ─────────────────────────────────────────────────────────────────────
# 1) Простой декоратор
# ─────────────────────────────────────────────────────────────────────

def vaqt_olchagich(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = func(*args, **kwargs)
        tugash = time.time()
        print(f"{func.__name__} {tugash - boshlanish:.4f} soniyada bajarildi")
        return natija
    return wrapper


@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))


hisoblash(1000000)
print(hisoblash.__name__)
print(hisoblash.__doc__)

# ─────────────────────────────────────────────────────────────────────
# 2) Декоратор с параметром
# ─────────────────────────────────────────────────────────────────────

def takrorlash(necha_marta):
    def dekorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            natija = None
            for _ in range(necha_marta):
                natija = func(*args, **kwargs)
            return natija
        return wrapper
    return dekorator


@takrorlash(3)
def salomlash():
    print("Salom!")


salomlash()

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - забыли @wraps (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def vaqt_olchagich_xato(func):
#     def wrapper(*args, **kwargs):    # НЕТ @wraps!
#         return func(*args, **kwargs)
#     return wrapper
#
# @vaqt_olchagich_xato
# def hisoblash_xato(n):
#     \"\"\"n gacha bo'lgan sonlar yig'indisini hisoblaydi.\"\"\"
#     return sum(range(n))
#
# print(hisoblash_xato.__name__)   # ❌ "wrapper", НЕ "hisoblash_xato"!
"""

EX = {
    4156: {
        "title": "Для чего используются декораторы?",
        "description": "Для чего в основном используются декораторы?",
        "hint": "Например, когда нужно добавить измерение времени или логирование во множество функций.",
        "explanation": "Декоратор позволяет добавить функции общее дополнительное поведение (лог, измерение времени, кеширование), не изменяя её собственный код.",
    },
    4157: {
        "title": "Зачем в wrapper нужны *args, **kwargs?",
        "description": "Зачем в записи wrapper(*args, **kwargs) используются *args, **kwargs?",
        "hint": "Декоратор может применяться к разным функциям — их сигнатуры разные.",
        "explanation": "*args, **kwargs позволяют wrapper передать любые пришедшие аргументы исходной функции без изменений, поэтому декоратор может применяться к функции с любой сигнатурой.",
    },
    4158: {
        "title": "Расположите процесс работы @takrorlash(3)",
        "description": "Расположите процесс, происходящий при применении декоратора @takrorlash(3) к функции salomlash().",
        "hint": "",
        "explanation": "",
    },
    4159: {
        "title": "Декоратор, сохраняющий метаданные",
        "description": "Какой декоратор (из functools) используется внутри декоратора для сохранения метаданных исходной функции, таких как __name__ и __doc__? (напишите название)",
        "hint": "Используется в форме functools.___(func).",
        "expected_answer": "wraps",
    },
    4160: {
        "title": "Почему без @wraps __name__ выводится неверно?",
        "description": (
            "В декораторе без @wraps, почему hisoblash.__name__ "
            "выводится не как \"hisoblash\", а как \"wrapper\"? "
            "Объясните своими словами."
        ),
        "hint": "После применения @декоратора, на какую функцию на самом деле указывает переменная hisoblash?",
        "expected_answer": "После применения @декоратора переменная с именем hisoblash на самом деле указывает уже не на исходную функцию hisoblash, а на функцию wrapper, созданную внутри декоратора. В Python каждая функция — объект со своим метаданным __name__ — и у функции wrapper значение __name__ по умолчанию равно \"wrapper\", так как она именно так названа. Если не использовать @functools.wraps(func), никто не заменяет __name__ у wrapper на __name__ исходной func, поэтому при обращении извне к hisoblash.__name__ выводится \"wrapper\", а не ожидаемое \"hisoblash\".",
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
