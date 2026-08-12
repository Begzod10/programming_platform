"""Russian translation for Python: Ilg'or Mavzular, lesson order=4 (L5)."""
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

LESSON_ID = 718

TITLE_RU = "5-Comprehensions глубже"

TEXT_RU = """\
<h2>Comprehensions глубже — удобное создание данных в одну строку</h2>

<pre class="mermaid">
flowchart LR
    NESTED["двухуровневый for"] --> FLAT["nested comprehension - в одну строку"]
    WALRUS[":= walrus-оператор"] --> REUSE["использование вычисленного значения БЕЗ повторного вычисления"]
</pre>

<p>Основы list/dict/set comprehension вы изучили в предыдущих курсах. Теперь их <strong>более глубокие</strong> возможности: вложенные (nested) comprehension и добавленный в Python 3.8 <strong>walrus-оператор</strong> (<code>:=</code>).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — вложенный (nested) list comprehension</h4>
<pre><code># "Уплощение" (flatten) матрицы обычным циклом:
matritsa = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
tekis = []
for qator in matritsa:
    for son in qator:
        tekis.append(son)

# То же самое - через nested comprehension, в одну строку:
tekis_comp = [son for qator in matritsa for son in qator]   # ❗ внешний цикл ПЕРВЫЙ, внутренний ВТОРОЙ
print(tekis_comp)   # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Можно добавить и фильтрацию по условию
juft_sonlar = [son for qator in matritsa for son in qator if son % 2 == 0]
print(juft_sonlar)   # [2, 4, 6, 8]</code></pre>

<h4>БЛОК 2 — dict и set comprehension</h4>
<pre><code>sonlar = [1, 2, 3, 4, 5]

# Dict comprehension - {ключ: значение for ...}
kvadratlar_lugat = {son: son**2 for son in sonlar}
print(kvadratlar_lugat)   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Set comprehension - автоматически удаляет повторяющиеся значения
takrorlanuvchi = [1, 2, 2, 3, 3, 3]
noyob_kvadratlar = {son**2 for son in takrorlanuvchi}
print(noyob_kvadratlar)   # {1, 4, 9} - без повторов</code></pre>

<h4>БЛОК 3 — walrus-оператор (:=): вычислить, сохранить, использовать</h4>
<pre><code># БЕЗ := - функция вызывается ДВАЖДЫ (неэффективно)
natijalar = [uzun_hisoblash(x) for x in range(10) if uzun_hisoblash(x) > 5]

# С := - функция вызывается только ОДИН раз, результат сохраняется и переиспользуется
natijalar = [natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5]
# ❗ (natija := uzun_hisoblash(x)) - вычисляет И сохраняет в natija ОДНОВРЕМЕННО</code></pre>

<h3>🐛 Намеренная ошибка — перепутан порядок циклов в nested comprehension</h3>
<pre><code>matritsa = [[1, 2, 3], [4, 5, 6]]

# ❌ НЕВЕРНЫЙ порядок - написано, будто "внутренний" и "внешний" цикл поменяны местами
xato_natija = [son for son in qator for qator in matritsa]
# ❌ NameError: name 'qator' is not defined
# (потому что переменная 'qator' объявляется ТОЛЬКО во втором 'for',
#  но первый 'for' пытается обратиться к ней раньше)</code></pre>

<p><strong>Результат:</strong> в nested comprehension циклы выполняются <strong>слева направо, в порядке написания</strong> — точно как во вложенных обычных циклах <code>for</code>: <strong>первый</strong> <code>for</code> — <strong>внешний</strong> цикл, <strong>второй</strong> <code>for</code> — <strong>внутренний</strong> цикл. Если порядок написан неверно (например внутренняя переменная используется до объявления во внешнем цикле), Python выдаёт <code>NameError</code>, так как ещё "не знает" эту переменную.</p>

<h3>Теперь объясним</h3>

<h4>1. Каков порядок циклов в nested comprehension?</h4>
<p>Правило простое: порядок <code>for</code> в nested comprehension такой же, как если бы вы "выписали" их в виде обычных вложенных циклов <code>for</code>. <strong>Первый</strong> написанный <code>for</code> — <strong>самый внешний</strong> цикл.</p>

<h4>2. Когда используются dict и set comprehension?</h4>
<p>Dict comprehension (<code>{k: v for ...}</code>) — для быстрого создания пар ключ-значение. Set comprehension (<code>{x for ...}</code>) используется вместо list comprehension, когда нужны <strong>уникальные</strong> (без повторов) элементы в результате.</p>

<h4>3. Зачем нужен walrus-оператор (<code>:=</code>)?</h4>
<p><code>:=</code> позволяет <strong>сохранить</strong> результат в переменную <strong>одновременно с вычислением</strong> выражения. Это особенно полезно в условиях comprehension, чтобы не выполнять одно и то же "дорогое" вычисление (например вызов функции) <strong>дважды</strong>, а сделать это <strong>один раз</strong>.</p>

<h4>4. Как := повышает эффективность?</h4>
<p>Без <code>:=</code>, если условие и результат зависят от одного и того же "дорогого" вычисления (например <code>uzun_hisoblash(x)</code>), это вычисление выполняется <strong>дважды</strong> (один раз для условия, один раз для результата). С <code>:=</code> оно вычисляется <strong>один раз</strong>, и результат переиспользуется для обоих.</p>

<h4>5. Почему при неверном порядке возникает NameError?</h4>
<p>Python "разворачивает" nested comprehension <strong>слева направо</strong>, в порядке написания. Если в первом <code>for</code> используется переменная из второго <code>for</code> (например <code>qator</code>), но <code>qator</code> ещё <strong>не объявлена</strong> (так как она в следующем <code>for</code>), Python не может <strong>найти</strong> это имя и выдаёт <code>NameError</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Порядок <code>for</code> в nested comprehension — как в обычных вложенных циклах, первый — внешний</li>
<li>✅ Dict comprehension (<code>{k: v for ...}</code>) и set comprehension (<code>{x for ...}</code>) — для разных целей</li>
<li>✅ Walrus-оператор (<code>:=</code>) — вычисляет и сохраняет одновременно</li>
<li>✅ <code>:=</code> позволяет выполнить одно и то же "дорогое" вычисление один раз, а не дважды</li>
<li>✅ Неверный порядок в nested comprehension приводит к <code>NameError</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 5: Comprehensions глубже
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Вложенный (nested) list comprehension
# ─────────────────────────────────────────────────────────────────────

matritsa = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

tekis = []
for qator in matritsa:
    for son in qator:
        tekis.append(son)

tekis_comp = [son for qator in matritsa for son in qator]
print(tekis_comp)

juft_sonlar = [son for qator in matritsa for son in qator if son % 2 == 0]
print(juft_sonlar)

# ─────────────────────────────────────────────────────────────────────
# 2) Dict и set comprehension
# ─────────────────────────────────────────────────────────────────────

sonlar = [1, 2, 3, 4, 5]

kvadratlar_lugat = {son: son**2 for son in sonlar}
print(kvadratlar_lugat)

takrorlanuvchi = [1, 2, 2, 3, 3, 3]
noyob_kvadratlar = {son**2 for son in takrorlanuvchi}
print(noyob_kvadratlar)

# ─────────────────────────────────────────────────────────────────────
# 3) Walrus-оператор (в комментарии - uzun_hisoblash не определена)
# ─────────────────────────────────────────────────────────────────────

# natijalar = [uzun_hisoblash(x) for x in range(10) if uzun_hisoblash(x) > 5]
# natijalar = [natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5]

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - перепутан порядок циклов (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# xato_natija = [son for son in qator for qator in matritsa]
# ❌ NameError: name 'qator' is not defined
"""

EX = {
    4196: {
        "title": "Порядок циклов в nested comprehension",
        "description": "В записи [son for qator in matritsa for son in qator], какой for считается внешним циклом?",
        "hint": "Это похоже на обычные вложенные циклы for.",
        "explanation": "В nested comprehension первый написанный for считается самым внешним циклом, точно как в обычных вложенных циклах for.",
    },
    4197: {
        "title": "Когда используется set comprehension?",
        "description": "Чем set comprehension вроде {son**2 for son in takrorlanuvchi} отличается от list comprehension?",
        "hint": "Какое свойство есть у множества (set), созданного через {}?",
        "explanation": "Set comprehension даёт в результате уникальные (без повторов) элементы, так как тип set (множество) не хранит повторяющиеся значения.",
    },
    4198: {
        "title": "Расположите процесс работы с walrus-оператором",
        "description": "Расположите процесс работы [natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5].",
        "hint": "",
        "explanation": "",
    },
    4199: {
        "title": "Символ walrus-оператора",
        "description": "Каким символом записывается добавленный в Python 3.8 оператор, позволяющий сохранить значение в переменную одновременно с вычислением? (напишите символ)",
        "hint": "",
        "expected_answer": ":=",
    },
    4200: {
        "title": "Почему при неверном порядке возникает NameError?",
        "description": (
            "Если написать [son for son in qator for qator in "
            "matritsa] (с перепутанным порядком), почему возникает "
            "ошибка \"NameError: name 'qator' is not defined\"? "
            "Объясните своими словами."
        ),
        "hint": "В каком порядке \"разворачивается\" nested comprehension — в порядке написания?",
        "expected_answer": "Python \"разворачивает\" nested comprehension слева направо, в порядке написания, точно как обычные вложенные циклы for. В этой записи первый for (for son in qator) считается самым внешним циклом и обращается к переменной qator, но переменная qator на самом деле объявляется только в СЛЕДУЮЩЕМ, втором for (for qator in matritsa). Когда запускается первый цикл, Python ещё \"не знает\" имя qator (оно ещё не определено), поэтому выдаёт ошибку NameError.",
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
