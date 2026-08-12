"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=4 (L5)."""
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

LESSON_ID = 794

TITLE_RU = "5-Test Coverage + бинарный поиск"

TEXT_RU = """\
<h2>Этап 5: Test Coverage + бинарный поиск — ложь процента coverage</h2>

<pre class="mermaid">
flowchart LR
    FUNC["find_rank_by_points() - функция бинарного поиска"] --> TESTS["Тестируется только случай 'элемент есть, в середине списка'"]
    TESTS --> COV["pytest-cov: 95%+ coverage - почти все СТРОКИ выполнены"]
    COV --> BLIND["Но: пустой список и список из одного элемента НИКОГДА не тестировались"]
    BLIND --> BUG["В production при вызове /rank для рейтинга с одним элементом - неверный результат"]
</pre>

<p>В курсе Python: Algoritmlar va Ma'lumotlar Tuzilmasi вы уже изучили бинарный поиск, а в курсе Python: Testlash — Test Coverage (<code>pytest-cov</code>). На этом уроке вы объедините их: напишете функцию <code>find_rank_by_points()</code>, отвечающую на вопрос "какое у меня место в рейтинге?" со скоростью <strong>O(log n)</strong>. Но на этот раз вы познакомитесь с одним из самых опасных заблуждений: <strong>высокий процент coverage тоже не гарантирует корректность.</strong></p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — бинарный поиск: нахождение рейтинга со скоростью O(log n)</h4>
<pre><code># app/ranking.py
def find_rank_by_points(sorted_points_desc, target_points):
    \"\"\"sorted_points_desc - список баллов, отсортированный по убыванию.
    Находит, где target_points ВПЕРВЫЕ встречается в этом списке
    (rank = этот индекс + 1).\"\"\"
    low, high = 0, len(sorted_points_desc) - 1
    while low <= high:                              # ❗ <= ВАЖНО - увидите ниже
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            # Сдвигаемся влево, находим ПЕРВЫЙ совпадающий индекс
            while mid > 0 and sorted_points_desc[mid - 1] == target_points:
                mid -= 1
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None   # не найдено</code></pre>

<h4>БЛОК 2 — pytest-cov: что измеряет отчёт coverage?</h4>
<pre><code># Terminal:
pytest --cov=app --cov-report=term-missing

# Результат (пример):
# app/ranking.py    24 stmts   1 miss   96%
#
# ❗ 96% означает ТОЛЬКО "23 из 24 строк выполнились хотя бы ОДИН
# раз". Это НИЧЕГО не говорит о том, "с какими ЗНАЧЕНИЯМИ они
# тестировались"!</code></pre>

<h4>БЛОК 3 — тесты, ЯВНО проверяющие граничные случаи</h4>
<pre><code># tests/test_ranking.py
def test_find_rank_empty_list():
    assert find_rank_by_points([], 100) is None

def test_find_rank_single_element_found():
    assert find_rank_by_points([100], 100) == 1

def test_find_rank_single_element_not_found():
    assert find_rank_by_points([100], 50) is None

def test_find_rank_target_not_in_list():
    assert find_rank_by_points([300, 200, 100], 250) is None</code></pre>

<h3>🐛 Намеренная ошибка — высокий coverage, но граничные случаи не протестированы</h3>
<pre><code># В find_rank_by_points() есть ТОНКАЯ ошибка off-by-one:
def find_rank_by_points(sorted_points_desc, target_points):
    low, high = 0, len(sorted_points_desc) - 1
    while low < high:                                # ❌ < вместо <=  !
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None

# tests/test_ranking.py - тестируется ТОЛЬКО "happy path":
def test_find_rank_middle_of_large_list():
    scores = [500, 400, 300, 200, 100]
    assert find_rank_by_points(scores, 300) == 3   # ✅ ЭТОТ тест проходит

# $ pytest --cov=app --cov-report=term-missing
# app/ranking.py   12 stmts   0 miss   100%   ✅✅✅
#
# 100% COVERAGE! Но:
find_rank_by_points([100], 100)   # ❌ возвращает None - ОШИБКА! (должно быть 1)
# Потому что при low=0, high=0 условие `while low < high` СРАЗУ становится
# False - цикл НИКОГДА не выполняется, хотя 100 точно есть в списке!</code></pre>

<p><strong>Результат:</strong> 100% coverage — это не значит "ошибок нет", это значит лишь <strong>"каждая строка выполнилась хотя бы один раз"</strong>. Ошибка <code>while low < high</code> выше <strong>никогда</strong> не проявляется при тестировании с большими списками — потому что в большом списке цикл всё равно выполняется несколько раз, и инструмент coverage отмечает эту строку как "выполненную". Ошибка проявляется только в <strong>граничном случае</strong> — списке из одного элемента — потому что именно в этом случае <code>low == high</code> сразу же выполняется. Если никто не протестировал <strong>именно этот</strong> граничный случай, ошибка остаётся <strong>скрытой</strong>, даже при coverage 100%.</p>

<h3>Теперь объясним</h3>

<h4>1. Что на самом деле измеряет процент coverage?</h4>
<p>Coverage измеряет, что строки (или ветви) кода были выполнены хотя бы <strong>один раз</strong> во время тестирования. Он <strong>ничего</strong> не знает о том, с <strong>какими значениями</strong> они выполнялись, и был ли результат <strong>правильным</strong>.</p>

<h4>2. Почему бинарный поиск особенно склонен к граничным ошибкам?</h4>
<p>В бинарном поиске работа с границами <code>low</code>, <code>high</code>, <code>mid</code> — разница всего <strong>в одну единицу</strong>, например между <code>&lt;</code> и <code>&lt;=</code>, <code>-1</code> и <code>+1</code>, может изменить весь результат (off-by-one ошибки). Эти ошибки проявляются именно в <strong>граничных</strong> случаях (пустой список, один элемент, первый/последний элемент) — в "обычных" случаях в середине они остаются скрытыми.</p>

<h4>3. Почему ошибка выше не заметна на большом списке, но заметна на маленьком?</h4>
<p>Ошибка <code>while low &lt; high</code> создаёт проблему только на <strong>одном</strong> шаге, где <code>low == high</code>. В большом списке цикл до этого момента работает <strong>правильно много</strong> раз, и результат часто (но не всегда) случайно оказывается верным. В списке из одного элемента же <code>low</code> и <code>high</code> равны <strong>с самого начала</strong> — ошибка проявляется <strong>немедленно</strong>.</p>

<h4>4. На что нужно обратить особое внимание при написании тестов?</h4>
<p>Для любого алгоритма, особенно <strong>чувствительных к границам</strong> алгоритмов вроде поиска/сортировки: нужно <strong>явно</strong> тестировать пустой вход, вход из одного элемента, и случаи, когда искомое значение находится <strong>в самом начале/конце</strong> списка — без этого, каким бы высоким ни был процент coverage, уверенность остаётся ложной.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>На 3-м уроке вы увидели, что "зелёный тест" может быть ложным (flaky-тесты). На этом уроке вы увидели, что <strong>"высокий coverage" тоже</strong> может давать ложную уверенность. Оба — разные проявления одного и того же общего урока: <strong>метрики (зелёная галочка, процент) — это не сама корректность, а лишь её приблизительный, иногда обманчивый индикатор.</strong></p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Процент coverage измеряет лишь выполнение строк, а не корректность результата</li>
<li>✅ Бинарный поиск особенно склонен к off-by-one ошибкам из-за чувствительности к граничным условиям (<code>&lt;</code>/<code>&lt;=</code>)</li>
<li>✅ Такие ошибки обычно проявляются только в граничных случаях (пустой список, один элемент)</li>
<li>✅ Несмотря на высокий coverage, если граничные случаи не протестированы, ошибка может оставаться скрытой</li>
<li>✅ "Зелёный тест" (3-й урок) и "высокий coverage" (этот урок) - оба являются метриками, а не самой корректностью</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 5: Test Coverage + бинарный поиск
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/ranking.py - правильный бинарный поиск (с <=)
# ─────────────────────────────────────────────────────────────────────

def find_rank_by_points(sorted_points_desc, target_points):
    low, high = 0, len(sorted_points_desc) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            while mid > 0 and sorted_points_desc[mid - 1] == target_points:
                mid -= 1
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_ranking.py - ЯВНОЕ тестирование граничных случаев
# ─────────────────────────────────────────────────────────────────────

def test_find_rank_empty_list():
    assert find_rank_by_points([], 100) is None


def test_find_rank_single_element_found():
    assert find_rank_by_points([100], 100) == 1


def test_find_rank_single_element_not_found():
    assert find_rank_by_points([100], 50) is None


def test_find_rank_target_not_in_list():
    assert find_rank_by_points([300, 200, 100], 250) is None


def test_find_rank_middle_of_large_list():
    scores = [500, 400, 300, 200, 100]
    assert find_rank_by_points(scores, 300) == 3


# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - off-by-one, тестирован только happy path (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def find_rank_by_points(sorted_points_desc, target_points):
#     low, high = 0, len(sorted_points_desc) - 1
#     while low < high:                    # < вместо <= !
#         ...
#     return None
#
# При тестировании только большим списком - 100% coverage, но
# find_rank_by_points([100], 100) НЕВЕРНО возвращает None.
"""

EX = {
    4574: {
        "title": "Что на самом деле измеряет процент coverage?",
        "description": "Что на самом деле означает показатель '95% coverage', отображаемый pytest-cov?",
        "hint": "Coverage отвечает на вопрос ВЫПОЛНЕНА ли строка, а не ПРАВИЛЬНА ли она.",
        "explanation": "Coverage измеряет лишь то, что строки кода (или ветви) выполнились хотя бы один раз во время теста - он ничего не знает о том, с какими значениями они выполнялись или был ли результат верным.",
    },
    4575: {
        "title": "Почему бинарный поиск особенно склонен к off-by-one ошибкам?",
        "description": "Почему алгоритм бинарного поиска более склонен к off-by-one (ошибка на единицу) ошибкам, чем другие алгоритмы?",
        "hint": "Подумайте о разнице между while low < high и while low <= high.",
        "explanation": "В бинарном поиске работа с границами low/high/mid - разница всего в одну единицу, например между < и <=, может изменить весь результат (off-by-one ошибки), и эти ошибки проявляются именно в граничных случаях.",
    },
    4576: {
        "title": "Расположите, как ошибка остаётся скрытой при 100% coverage",
        "description": "Расположите процесс того, как find_rank_by_points(), написанная с ошибкой while low < high, скрывает ошибку при 100% coverage.",
        "hint": "",
        "explanation": "",
    },
    4577: {
        "title": "Сложность эффективности бинарного поиска",
        "description": "Какова сложность Big O нахождения элемента в отсортированном списке через бинарный поиск? (ответьте в нотации Big O, например: O(x))",
        "hint": "На каждом шаге область поиска сокращается вдвое.",
        "expected_answer": "O(log n)",
    },
    4578: {
        "title": "Почему граничные случаи нужно тестировать отдельно?",
        "description": (
            "Даже при высоком проценте coverage, почему граничные "
            "случаи вроде пустого списка или списка из одного элемента "
            "нужно тестировать ОТДЕЛЬНО, ЯВНО? Объясните своими словами."
        ),
        "hint": "Coverage измеряет, что строка выполнена, или то, с каким значением она выполнена?",
        "expected_answer": "Процент coverage показывает лишь то, что строки кода выполнились хотя бы один раз, но не показывает, с КАКИМИ значениями они выполнялись. Ошибки вроде off-by-one обычно проявляются только при ОПРЕДЕЛЁННЫХ, граничных входных значениях (например пустой список, или список из одного элемента, где low и high равны) - при больших или 'обычных' средних случаях цикл всё равно выполняется правильно несколько раз, заставляя инструмент coverage отметить строку как 'выполненную', хотя результат в граничном случае неверен. Поэтому полагаться только на процент coverage недостаточно - граничные случаи должны проверяться явными, отдельными тестами.",
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
        TASK_TITLE_RU = "RankVault — Test Coverage + бинарный поиск (find_rank_by_points)"
        TASK_DESCRIPTION_RU = (
            "Напишите функцию find_rank_by_points(), работающую со "
            "скоростью O(log n) через бинарный поиск, и используйте её в "
            "эндпоинте GET /rank/<user_id>. Получите отчёт coverage через "
            "pytest-cov — но обратите внимание НЕ ТОЛЬКО на процент, а на "
            "явное тестирование граничных случаев."
        )
        TASK_REQUIREMENTS_RU = (
            "• app/ranking.py: find_rank_by_points() написана с правильными граничными условиями (low <= high)\n"
            "• GET /rank/<user_id> — использует find_rank_by_points() (НЕ линейный поиск)\n"
            "• tests/test_ranking.py: отдельные тесты для пустого списка, списка из одного элемента (найден и не найден), и элемента в середине\n"
            "• pytest --cov=app --cov-report=term-missing показывает 90%+ coverage\n"
            "• README.md: объяснены ограничения coverage (что он не измеряет), обновлён чеклист статуса"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, pytest-cov, алгоритмы"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
