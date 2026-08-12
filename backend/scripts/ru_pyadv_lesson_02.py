"""Russian translation for Python: Ilg'or Mavzular, lesson order=1 (L2)."""
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

LESSON_ID = 712

TITLE_RU = "2-Генераторы и итераторы"

TEXT_RU = """\
<h2>Генераторы и итераторы — производство элементов "по одному", экономя память</h2>

<pre class="mermaid">
flowchart LR
    LIST["[1,2,3,...1000000] - всё в ПАМЯТИ"] --> MEM["Много памяти"]
    GEN["generator: yield 1, yield 2, ..."] --> LAZY["Каждый вычисляется ТОЛЬКО ПО ЗАПРОСУ"]
    LAZY --> MEM2["Мало памяти"]
</pre>

<p>Иногда нужно производить последовательность больших объёмов данных <strong>по одному элементу</strong>, не загружая всё сразу в память. <strong>Генератор</strong> &mdash; специальный тип функции, позволяющий создавать такую "ленивую" (lazy) последовательность с помощью ключевого слова <code>yield</code>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — простая функция-генератор</h4>
<pre><code>def sonlar_generatori(n):
    for i in range(n):
        yield i              # ❗ не 'return', а 'yield' - "отдаёт" значение и ПРИОСТАНАВЛИВАЕТСЯ

gen = sonlar_generatori(3)    # ❗ функция ЕЩЁ НЕ запускается - создаётся объект-генератор
print(next(gen))              # 0 - выполняется до этого места, затем останавливается
print(next(gen))              # 1 - продолжает с оставшегося места
print(next(gen))              # 2
# print(next(gen))            # ❌ StopIteration - больше элементов нет

for son in sonlar_generatori(3):   # ❗ цикл for сам автоматически перехватывает StopIteration
    print(son)                      # 0, 1, 2</code></pre>

<h4>БЛОК 2 — generator expression</h4>
<pre><code># List comprehension - ВСЁ создаётся сразу в памяти
kvadratlar_royxat = [x**2 for x in range(1000000)]   # ❗ большой массив - много памяти

# Generator expression - вместо квадратных скобок используются (), элементы вычисляются "лениво"
kvadratlar_gen = (x**2 for x in range(1000000))      # ❗ почти не расходует память!

print(sum(kvadratlar_gen))    # ✅ генератор можно использовать напрямую с sum()</code></pre>

<h4>БЛОК 3 — протокол итератора (__iter__ / __next__)</h4>
<pre><code># Генератор - "удобная" форма итератора. Итератор можно создать и вручную:
class Sanagich:
    def __init__(self, chegara):
        self.hozirgi = 0
        self.chegara = chegara

    def __iter__(self):            # ❗ говорит, что сам объект "поддерживает итерацию"
        return self

    def __next__(self):            # ❗ каждый раз возвращает следующее значение
        if self.hozirgi >= self.chegara:
            raise StopIteration     # ❗ при завершении ОБЯЗАТЕЛЬНО нужно вызвать эту ошибку
        qiymat = self.hozirgi
        self.hozirgi += 1
        return qiymat

for son in Sanagich(3):
    print(son)   # 0, 1, 2</code></pre>

<h3>🐛 Намеренная ошибка — попытка использовать генератор второй раз</h3>
<pre><code>gen = (x for x in range(3))
print(list(gen))   # [0, 1, 2] - генератор "израсходован"

print(list(gen))   # ❌ [] - ПУСТО! Генератор проходится только ОДИН РАЗ</code></pre>

<p><strong>Результат:</strong> генератор &mdash; это <strong>одноразовая</strong> последовательность. Каждый вызов <code>next()</code> (или полный проход через <code>for</code>/<code>list()</code>) <strong>изменяет</strong> внутреннее состояние генератора &mdash; он не возвращается к началу заново. В отличие от списка (list), если нужно пройти генератор второй раз, его нужно <strong>создать заново</strong>.</p>

<h3>Теперь объясним</h3>

<h4>1. Разница между yield и return</h4>
<p><code>return</code> <strong>полностью завершает</strong> функцию. <code>yield</code> же <strong>сохраняет состояние и приостанавливает</strong> функцию &mdash; при следующем вызове <code>next()</code> функция продолжается именно с того места, где остановилась. Поэтому в функции-генераторе может быть несколько <code>yield</code>.</p>

<h4>2. Почему генератор экономит память?</h4>
<p>List comprehension сразу вычисляет <strong>все</strong> элементы и помещает их в память. Генератор же вычисляет элементы <strong>только по запросу</strong> (по одному) и никогда не хранит полный список в памяти &mdash; это важно при работе с большими или бесконечными последовательностями.</p>

<h4>3. Как записывается generator expression?</h4>
<p>List comprehension использует квадратные скобки <code>[...]</code>, generator expression же использует обычные скобки <code>(...)</code>. Синтаксис почти одинаковый, но результат совершенно разный: один — полный список, другой — "ленивый" объект-генератор.</p>

<h4>4. Что такое протокол итератора (<code>__iter__</code>/<code>__next__</code>)?</h4>
<p>Чтобы цикл <code>for</code> в Python работал, объект должен соответствовать <strong>протоколу итератора</strong>: <code>__iter__()</code> возвращает сам объект, <code>__next__()</code> отдаёт следующее значение и при завершении вызывает <code>StopIteration</code>. Функции-генераторы реализуют этот протокол <strong>автоматически</strong> — функция с <code>yield</code> за кулисами создаёт объект с <code>__iter__</code>/<code>__next__</code>.</p>

<h4>5. Почему генератор нельзя использовать второй раз?</h4>
<p>Генератор хранит в своём внутреннем состоянии, "где он остановился". После однократного полного прохода его внутреннее состояние остаётся "завершённым" &mdash; возможности "перезапустить с начала" <strong>нет</strong>. Для повторного использования нужно <strong>заново вызвать</strong> функцию-генератор (или generator expression), что создаст новый объект-генератор.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>yield</code> приостанавливает функцию, сохраняя состояние; <code>return</code> же полностью её завершает</li>
<li>✅ Генератор экономит память, производя элементы "лениво" (lazy)</li>
<li>✅ Generator expression — записывается через <code>(...)</code>, экономящая память версия list comprehension</li>
<li>✅ Протокол итератора — <code>__iter__</code> + <code>__next__</code> + <code>StopIteration</code></li>
<li>✅ Генератор одноразовый — для повторного использования нужно создать заново</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 2: Генераторы и итераторы
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Простая функция-генератор
# ─────────────────────────────────────────────────────────────────────

def sonlar_generatori(n):
    for i in range(n):
        yield i


gen = sonlar_generatori(3)
print(next(gen))
print(next(gen))
print(next(gen))

for son in sonlar_generatori(3):
    print(son)

# ─────────────────────────────────────────────────────────────────────
# 2) Generator expression
# ─────────────────────────────────────────────────────────────────────

kvadratlar_royxat = [x**2 for x in range(1000000)]
kvadratlar_gen = (x**2 for x in range(1000000))

print(sum(kvadratlar_gen))

# ─────────────────────────────────────────────────────────────────────
# 3) Протокол итератора
# ─────────────────────────────────────────────────────────────────────


class Sanagich:
    def __init__(self, chegara):
        self.hozirgi = 0
        self.chegara = chegara

    def __iter__(self):
        return self

    def __next__(self):
        if self.hozirgi >= self.chegara:
            raise StopIteration
        qiymat = self.hozirgi
        self.hozirgi += 1
        return qiymat


for son in Sanagich(3):
    print(son)

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - использование генератора второй раз (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# gen_xato = (x for x in range(3))
# print(list(gen_xato))   # [0, 1, 2]
# print(list(gen_xato))   # ❌ [] - ПУСТО!
"""

EX = {
    4166: {
        "title": "Разница между yield и return",
        "description": "Чем ключевое слово yield в основном отличается от return?",
        "hint": "В функции-генераторе может быть несколько yield.",
        "explanation": "return полностью завершает функцию, yield же приостанавливает её, сохраняя состояние, и продолжается с того же места при следующем вызове next().",
    },
    4167: {
        "title": "Почему генератор экономит память?",
        "description": "Почему генератор, в отличие от list comprehension, экономит память?",
        "hint": "Это называется \"ленивым\" (lazy) вычислением.",
        "explanation": "Генератор вычисляет элементы только по запросу (по одному) и никогда не хранит полный список в памяти, list comprehension же сразу помещает все элементы в память.",
    },
    4168: {
        "title": "Расположите процесс итерации через Sanagich",
        "description": "Расположите процесс работы цикла for son in Sanagich(3).",
        "hint": "",
        "explanation": "",
    },
    4169: {
        "title": "Запись generator expression",
        "description": "List comprehension использует квадратные скобки. А какие скобки использует generator expression? (напишите символ, например: ())",
        "hint": "",
        "expected_answer": "()",
    },
    4170: {
        "title": "Почему генератор нельзя использовать второй раз?",
        "description": (
            "После создания gen = (x for x in range(3)) и однократного "
            "вызова list(gen), почему повторный вызов list(gen) "
            "возвращает пустой список []? Объясните своими словами."
        ),
        "hint": "Генератор хранит \"где он остановился\", или каждый раз начинает \"с начала\"?",
        "expected_answer": "Генератор хранит в себе внутреннее состояние \"где он остановился\", а не хранит все элементы в одном месте, как список (list). При вызове list(gen) генератор через __next__() отдаёт все элементы по одному, доходя до конца (StopIteration), и остаётся в состоянии \"завершён\". Возможности \"вернуть генератор к началу\" нет, поэтому повторный его вызов больше не даёт никаких новых элементов и возвращает пустой список. Для повторного использования нужно заново создать generator expression.",
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
