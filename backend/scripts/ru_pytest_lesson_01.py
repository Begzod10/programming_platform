"""Russian translation for Python: Testlash, lesson order=0 (L1)."""
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

LESSON_ID = 634

TITLE_RU = "1-Знакомство с pytest"

TEXT_RU = """\
<h2>Знакомство с pytest — первый тест за 5 минут</h2>

<pre class="mermaid">
flowchart LR
    F["файл test_*.py"] --> D["pytest — находит тесты (discovery)"]
    D --> R["Каждая функция test_ запускается"]
    R -->|assert верен| P["✅ PASSED"]
    R -->|assert неверен| X["❌ FAILED"]
</pre>

<p>До сих пор вы проверяли код вручную: запускали программу и сравнивали результат глазами. Это медленно и легко ошибиться. <strong>pytest</strong> — самый популярный фреймворк тестирования в Python: он автоматически, за несколько секунд, проверяет, правильно ли работает ваш код.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка pytest и первый тест</h4>
<pre><code># Терминал:
pip install pytest</code></pre>

<pre><code># kalkulyator.py
def qoshish(a, b):
    return a + b</code></pre>

<pre><code># test_kalkulyator.py
from kalkulyator import qoshish

def test_qoshish():
    assert qoshish(2, 3) == 5</code></pre>

<pre><code># Терминал:
pytest
# ================ 1 passed in 0.01s ================</code></pre>

<h4>БЛОК 2 — несколько assert и неудачный тест</h4>
<pre><code>def test_qoshish_manfiy_sonlar():
    assert qoshish(-2, -3) == -5

def test_qoshish_nol_bilan():
    assert qoshish(5, 0) == 5

def test_qoshish_xato_kutilgan():
    assert qoshish(2, 2) == 5  # ❗ намеренная ошибка — ожидается 5 вместо 4</code></pre>

<pre><code># Терминал:
pytest
# ================ 2 passed, 1 failed in 0.02s ================
# FAILED test_kalkulyator.py::test_qoshish_xato_kutilgan
# assert 4 == 5</code></pre>

<p>pytest точно показывает, какой тест провалился: какой именно тест, на какой строке, и какие именно значения не совпали (<code>4 == 5</code>). Это помогает быстро найти проблему.</p>

<h4>БЛОК 3 — запуск нескольких тестовых файлов</h4>
<pre><code># Структура проекта:
# loyiha/
#   kalkulyator.py
#   test_kalkulyator.py
#   validatsiya.py
#   test_validatsiya.py

# Терминал — запуск всех тестов:
pytest

# Запуск только одного файла:
pytest test_kalkulyator.py

# Запуск только одной функции:
pytest test_kalkulyator.py::test_qoshish</code></pre>

<h3>🐛 Намеренная ошибка — забыть префикс test_ в имени функции</h3>
<pre><code># test_kalkulyator.py
from kalkulyator import qoshish

def qoshishni_tekshir():  # ❌ не начинается с 'test_'!
    assert qoshish(2, 2) == 5  # здесь НАМЕРЕННАЯ ошибка — но она никогда не запустится!</code></pre>

<pre><code># Терминал:
pytest
# ================ no tests ran in 0.01s ================</code></pre>

<p><strong>Результат:</strong> если имя функции не начинается с <code>test_</code>, pytest <strong>вообще не добавляет её</strong> в список тестов — никакой ошибки или предупреждения не появится, он просто скажет "no tests ran". Это очень опасно: разработчик может подумать, что "всё зелёное (passed)", хотя на самом деле функция <strong>никогда не была проверена</strong>. Это одна из самых распространённых, но незаметных ошибок в написании тестов.</p>

<h3>Теперь объясним</h3>

<h4>1. Как pytest "находит" тесты (discovery)?</h4>
<p>pytest сканирует текущую папку и подпапки, ища файлы/функции по следующим правилам: имя файла должно начинаться с <code>test_*.py</code> или заканчиваться на <code>*_test.py</code>, имя функции должно начинаться с <code>test_</code>. Всё, что не соответствует этому правилу, <strong>полностью игнорируется</strong>.</p>

<h4>2. assert — сердце теста</h4>
<p><code>assert условие</code> — если <code>условие</code> равно <code>False</code>, тест помечается как <strong>FAILED</strong>, и pytest точно показывает, какие значения не совпали. Если <code>условие</code> равно <code>True</code>, ничего не происходит — тест <strong>PASSED</strong>.</p>

<h4>3. Почему нужно проверять код через тесты, а не вручную?</h4>
<p>Ручная проверка — разовая и забывается. Тестовая функция же сохраняется навсегда: если позже вы измените код, достаточно снова запустить <code>pytest</code>, чтобы за секунды узнать, ничего ли не сломалось.</p>

<h4>4. Где располагается тестовый файл?</h4>
<p>Обычно тестовый файл располагается в той же папке, что и проверяемый модуль, или в отдельной папке <code>tests/</code>. Главное — соблюдать правило именования.</p>

<h4>5. Что означает вывод pytest?</h4>
<pre><code>================ 2 passed, 1 failed in 0.02s ================</code></pre>
<p><code>passed</code> — количество успешно пройденных тестов, <code>failed</code> — количество неудачных. Под каждым <code>FAILED</code> показывается, какой <code>assert</code> не сработал и что ожидалось, а что было получено.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ pytest — фреймворк, автоматически проверяющий правильность кода</li>
<li>✅ Тестовый файл должен называться <code>test_*.py</code>, функция — начинаться с <code>test_</code>, иначе pytest её не найдёт</li>
<li>✅ <code>assert условие</code> — если условие ложно, тест становится FAILED, показываются точные значения</li>
<li>✅ Команда <code>pytest</code> запускает все тесты, <code>pytest файл.py::функция</code> — один тест</li>
<li>✅ Забыть префикс <code>test_</code> — самая опасная, незаметная ошибка: тест "пропадает" без какого-либо предупреждения</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 1: Знакомство с pytest
# ════════════════════════════════════════════════════════════════════

# ─── kalkulyator.py ───
def qoshish(a, b):
    return a + b


def ayirish(a, b):
    return a - b


# ─── test_kalkulyator.py ───
# from kalkulyator import qoshish, ayirish

def test_qoshish():
    assert qoshish(2, 3) == 5


def test_qoshish_manfiy_sonlar():
    assert qoshish(-2, -3) == -5


def test_qoshish_nol_bilan():
    assert qoshish(5, 0) == 5


def test_ayirish():
    assert ayirish(10, 4) == 6


# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка — функция без префикса 'test_' (в комментарии, pytest не найдёт)
# ─────────────────────────────────────────────────────────────────────

# def qoshishni_tekshir():  # ❌ не запустится pytest'ом, так как не начинается с 'test_'
#     assert qoshish(2, 2) == 5  # эта строка НИКОГДА не выполнится!


# Терминал:
#   pip install pytest
#   pytest                              # все тесты
#   pytest test_kalkulyator.py          # один файл
#   pytest test_kalkulyator.py::test_qoshish  # один тест
"""

EX = {
    3751: {
        "title": "Как pytest находит тестовую функцию?",
        "description": "Какие функции pytest считает \"тестами\" и запускает автоматически?",
        "hint": "Обратите внимание на правило именования — pytest строго его требует.",
        "explanation": "pytest автоматически считает тестами только функции в файлах test_*.py, имя которых начинается с 'test_'. Функции с другим именем полностью игнорируются.",
    },
    3752: {
        "title": "Что произойдёт, если assert равен False?",
        "description": "Если результат условия assert внутри тестовой функции равен False, что сделает pytest?",
        "hint": "assert — основной механизм, определяющий успех/неудачу теста.",
        "explanation": "Если условие assert ложно, pytest помечает этот тест как FAILED и точно показывает в консоли, какие значения (например 4 == 5) не совпали.",
    },
    3753: {
        "title": "Расположите порядок запуска теста",
        "description": "Упорядочите шаги написания и запуска первого теста с pytest в новом проекте.",
        "hint": "Сначала устанавливается библиотека, затем пишутся файл и функция, затем запускается.",
    },
    3754: {
        "title": "Какая проблема возникает при забытом префиксе test_?",
        "description": (
            "Если имя тестовой функции написано не с 'test_', а иначе "
            "(например 'qoshishni_tekshir'), что произойдёт при запуске "
            "pytest, и почему это особенно опасно? Объясните своими "
            "словами."
        ),
        "expected_answer": "pytest вообще не распознает эту функцию как тест и не добавит её в список тестов — в результате она никогда не запустится. Это особенно опасно, потому что pytest не выдаёт никакой ошибки или предупреждения, а просто показывает \"no tests ran\" или \"всё passed\" по остальным тестам. Разработчик уверен, что код правильно проверен, хотя на самом деле важная функция никогда не тестировалась — это тихий, незаметный вид ошибки.",
        "hint": "pytest не выдаёт ошибку — он просто \"не видит\" эту функцию.",
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
