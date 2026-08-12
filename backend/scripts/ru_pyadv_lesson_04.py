"""Russian translation for Python: Ilg'or Mavzular, lesson order=3 (L4)."""
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

LESSON_ID = 716

TITLE_RU = "4-functools глубже"

TEXT_RU = """\
<h2>functools глубже — готовые инструменты для функционального программирования</h2>

<pre class="mermaid">
flowchart LR
    CACHE["@lru_cache"] --> FAST["Возвращает из кеша, не пересчитывая"]
    PARTIAL["partial(func, x)"] --> FIXED["Новая функция с ЗАРАНЕЕ заданными аргументами"]
    REDUCE["reduce(func, список)"] --> ACC["'Сворачивает' список в одно значение"]
</pre>

<p>Модуль <code>functools</code> &mdash; набор готовых инструментов, облегчающих работу с функциями. В уроке 1 мы научились писать декораторы сами; теперь посмотрим на <strong>готовые, оптимизированные</strong> декораторы и функции Python.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — @lru_cache: кеширование результатов</h4>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=None)              # ❗ сохраняет вычисленные результаты в памяти
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(30)   # ❗ первый вызов - медленный (рекурсия вычисляет много раз)
fibonacci(30)   # ❗ второй вызов - МГНОВЕННО (берётся из кеша, не пересчитывается)

print(fibonacci.cache_info())   # CacheInfo(hits=1, misses=31, maxsize=None, currsize=31)</code></pre>

<h4>БЛОК 2 — partial: создание функции с частично заданными аргументами</h4>
<pre><code>from functools import partial

def daraja(asos, korsatkich):
    return asos ** korsatkich

kvadrat = partial(daraja, korsatkich=2)     # ❗ новая функция, где korsatkich ВСЕГДА равен 2
kub = partial(daraja, korsatkich=3)          # ❗ новая функция, где korsatkich ВСЕГДА равен 3

print(kvadrat(5))    # daraja(5, korsatkich=2) - 25
print(kub(5))         # daraja(5, korsatkich=3) - 125</code></pre>

<h4>БЛОК 3 — reduce: "сворачивание" списка в одно значение</h4>
<pre><code>from functools import reduce

sonlar = [1, 2, 3, 4, 5]

# reduce(функция, список) - применяет функцию последовательно, "накапливая" результат
kopaytma = reduce(lambda x, y: x * y, sonlar)   # ❗ (((1*2)*3)*4)*5 = 120
print(kopaytma)   # 120

# похоже на sum() - но работает с любой операцией
maksimum = reduce(lambda x, y: x if x > y else y, sonlar)
print(maksimum)   # 5</code></pre>

<h3>🐛 Намеренная ошибка — использование lru_cache с изменяемым (mutable) аргументом</h3>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=None)
def royxatni_qayta_ishlash(royxat):     # ❗ список (list) - mutable, не хешируется!
    return sum(royxat)

royxatni_qayta_ishlash([1, 2, 3])
# ❌ TypeError: unhashable type: 'list'
# (lru_cache использует аргументы как "ключ", они ОБЯЗАНЫ быть хешируемыми)</code></pre>

<p><strong>Результат:</strong> <code>lru_cache</code> сохраняет каждую <strong>комбинацию аргументов</strong> как "ключ", связывая с ней результат. Для этого аргументы должны быть <strong>хешируемыми</strong> (immutable) &mdash; изменяемые (mutable) типы вроде <code>list</code> не хешируются, поэтому возникает <code>TypeError</code>. Решение: использовать вместо <code>list</code> immutable-тип, например <code>tuple</code> (<code>tuple(royxat)</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Когда полезен lru_cache?</h4>
<p><code>lru_cache</code> очень полезен для "дорогих" (требующих много времени) функций, вызываемых <strong>повторно</strong> с одинаковыми аргументами &mdash; например рекурсивной <code>fibonacci</code>. Он вычисляет результат один раз, а при следующих одинаковых вызовах мгновенно возвращает его из кеша.</p>

<h4>2. Зачем нужен partial?</h4>
<p><code>partial</code> создаёт из существующей функции новую функцию с <strong>заранее заданными некоторыми аргументами</strong>. Это используется для "адаптации" функции (например, создание специальной функции <code>kvadrat</code> из общей функции <code>daraja</code>) без повторного написания полной функции.</p>

<h4>3. Как работает reduce?</h4>
<p><code>reduce(функция, список)</code> применяет функцию к первым двум элементам списка, затем применяет результат к следующему элементу, и так далее &mdash; в итоге весь список "сворачивается" в <strong>одно</strong> значение. Функции вроде <code>sum()</code>, <code>max()</code> фактически являются частными случаями <code>reduce</code>.</p>

<h4>4. Почему аргументы lru_cache должны быть хешируемыми?</h4>
<p><code>lru_cache</code> внутренне хранит результаты в виде <strong>словаря</strong> (dictionary), где комбинация аргументов выполняет роль "ключа". В Python ключ словаря обязан быть <strong>хешируемым</strong> (обычно immutable) &mdash; изменяемые типы вроде <code>list</code> не могут быть ключом.</p>

<h4>5. Когда functools лучше, чем написание собственного декоратора?</h4>
<p>В уроке 1 мы научились писать декоратор сами — это важно для <strong>понимания</strong>. Но в реальных проектах готовые инструменты из <code>functools</code> (например <code>lru_cache</code>) <strong>оптимизированы</strong>, проверены и учитывают многие граничные случаи (например потокобезопасность) — поэтому, когда они доступны, рекомендуется использовать их вместо переписывания вручную.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>@lru_cache</code> — кеширует результаты функции, предотвращая повторные вычисления</li>
<li>✅ <code>partial(func, arg=значение)</code> — создаёт новую функцию с заранее заданными некоторыми аргументами</li>
<li>✅ <code>reduce(func, список)</code> — применяет функцию последовательно, "сворачивая" список в одно значение</li>
<li>✅ Аргументы <code>lru_cache</code> должны быть хешируемыми (immutable)</li>
<li>✅ Готовые инструменты <code>functools</code> часто превосходят ручные версии в реальных проектах</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 4: functools глубже
# ════════════════════════════════════════════════════════════════════

from functools import lru_cache, partial, reduce

# ─────────────────────────────────────────────────────────────────────
# 1) @lru_cache - кеширование результатов
# ─────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


fibonacci(30)
fibonacci(30)
print(fibonacci.cache_info())

# ─────────────────────────────────────────────────────────────────────
# 2) partial - функция с частично заданными аргументами
# ─────────────────────────────────────────────────────────────────────


def daraja(asos, korsatkich):
    return asos ** korsatkich


kvadrat = partial(daraja, korsatkich=2)
kub = partial(daraja, korsatkich=3)

print(kvadrat(5))
print(kub(5))

# ─────────────────────────────────────────────────────────────────────
# 3) reduce - сворачивание списка в одно значение
# ─────────────────────────────────────────────────────────────────────

sonlar = [1, 2, 3, 4, 5]

kopaytma = reduce(lambda x, y: x * y, sonlar)
print(kopaytma)

maksimum = reduce(lambda x, y: x if x > y else y, sonlar)
print(maksimum)

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - lru_cache с mutable-аргументом (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @lru_cache(maxsize=None)
# def royxatni_qayta_ishlash(royxat):
#     return sum(royxat)
#
# royxatni_qayta_ishlash([1, 2, 3])
# ❌ TypeError: unhashable type: 'list'
"""

EX = {
    4186: {
        "title": "Когда полезен lru_cache?",
        "description": "Для каких функций в основном полезен декоратор @lru_cache?",
        "hint": "Рекурсивная fibonacci - классический пример.",
        "explanation": "lru_cache полезен для \"дорогих\" функций, вызываемых повторно с одинаковыми аргументами — результат вычисляется один раз, а при следующих вызовах берётся из кеша.",
    },
    4187: {
        "title": "Что делает partial?",
        "description": "Что делает partial(daraja, korsatkich=2)?",
        "hint": "Это создаёт из существующей функции \"адаптированную\" новую функцию.",
        "explanation": "partial создаёт из существующей функции новую функцию, где некоторые аргументы (в данном случае korsatkich=2) заданы заранее.",
    },
    4188: {
        "title": "Расположите процесс вычисления reduce(lambda x,y: x*y, [1,2,3,4,5])",
        "description": "Расположите шаги, которыми функция reduce сворачивает список [1,2,3,4,5] через умножение в одно значение.",
        "hint": "",
        "explanation": "",
    },
    4189: {
        "title": "Метод для просмотра статистики lru_cache",
        "description": "Напишите метод, показывающий статистику кеша (hits, misses) функции, украшенной lru_cache.",
        "hint": "Вызывается в форме имя_функции.___().",
        "expected_answer": "cache_info",
    },
    4190: {
        "title": "Почему lru_cache с mutable-аргументом даёт TypeError?",
        "description": (
            "Если в функцию, украшенную @lru_cache, передать список "
            "как аргумент (например royxatni_qayta_ishlash([1,2,3])), "
            "почему возникает ошибка \"TypeError: unhashable type: "
            "'list'\"? Объясните своими словами."
        ),
        "hint": "Как lru_cache хранит аргументы — как обычный список, или как ключ словаря?",
        "expected_answer": "lru_cache внутренне хранит вычисленные результаты в виде словаря (dictionary), где комбинация переданных функции аргументов выполняет роль \"ключа\". В Python в качестве ключа словаря можно использовать только хешируемые (обычно immutable) значения. Тип list же является изменяемым (mutable) и нехешируемым типом, поэтому при попытке использовать его как ключ Python выдаёт ошибку \"unhashable type: 'list'\". Решение — использовать вместо list immutable-тип, например tuple(royxat).",
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
