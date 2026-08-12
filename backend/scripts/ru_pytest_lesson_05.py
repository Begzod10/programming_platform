"""Russian translation for Python: Testlash, lesson order=4 (L5)."""
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

LESSON_ID = 642

TITLE_RU = "5-Test Coverage"

TEXT_RU = """\
<h2>Test Coverage — какая часть кода протестирована?</h2>

<pre class="mermaid">
flowchart LR
    CODE["Исходный код"] --> COV["запускается pytest-cov"]
    TESTS["Тесты"] --> COV
    COV --> REPORT["Отчёт покрытия: % и строки"]
    REPORT -->|низкий %| GAP["Находятся непротестированные строки"]
</pre>

<p>Мы написали тесты, но как узнать — <strong>какая часть</strong> кода реально протестирована, а какая ещё нет? <strong>Test coverage</strong> (покрытие тестами) — метрика, отвечающая именно на этот вопрос: сколько процентов кода выполняется при запуске тестов.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка pytest-cov и первый отчёт</h4>
<pre><code># Терминал:
pip install pytest-cov</code></pre>

<pre><code># baholash.py
def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    else:
        return "F"</code></pre>

<pre><code># test_baholash.py
from baholash import harfli_baho

def test_harfli_baho_a():
    assert harfli_baho(95) == "A"</code></pre>

<pre><code># Терминал:
pytest --cov=baholash

# Name           Stmts   Miss  Cover
# ----------------------------------
# baholash.py        5      2    60%</code></pre>

<h4>БЛОК 2 — просмотр непротестированных строк</h4>
<pre><code># Терминал — показывает, какие именно строки были пропущены:
pytest --cov=baholash --cov-report=term-missing

# Name           Stmts   Miss  Cover   Missing
# ------------------------------------------------
# baholash.py        5      2    60%   5, 7</code></pre>

<p>Столбец <code>Missing</code> показывает номера строк, которые тесты ни разу не выполнили. Здесь строки 5 и 7 (ветки <code>elif</code> и <code>else</code>) ни разу не сработали — потому что тест был только с 95 баллами.</p>

<h4>БЛОК 3 — доведение coverage до 100%</h4>
<pre><code># Добавляются тесты для недостающих случаев:
def test_harfli_baho_b():
    assert harfli_baho(82) == "B"

def test_harfli_baho_f():
    assert harfli_baho(40) == "F"</code></pre>

<pre><code># Терминал:
pytest --cov=baholash --cov-report=term-missing

# Name           Stmts   Miss  Cover   Missing
# ------------------------------------------------
# baholash.py        5      0   100%</code></pre>

<h3>🐛 Намеренная ошибка — достичь 100% coverage только ради цифры</h3>
<pre><code># ❌ Строка выполняется, но НИЧЕГО не проверяется!
def test_harfli_baho_qamrov_uchun():
    harfli_baho(82)  # ❗ функция вызвана — строка считается "выполненной"
    # ❌ Но НЕТ assert! Результат вообще не проверяется.</code></pre>

<p><strong>Результат:</strong> отчёт coverage покажет 100% — потому что строка <code>harfli_baho(82)</code> действительно <strong>выполнилась</strong>. Но этот тест вообще не проверяет, <strong>правильный</strong> или <strong>неправильный</strong> результат — нет <code>assert</code>! Даже если в функции есть ошибка (например неверная граница), этот тест всё равно останется "passed". <strong>Coverage измеряет, какие строки выполнились, а не правильность поведения.</strong> 100% coverage не означает, что код без ошибок.</p>

<h3>Теперь объясним</h3>

<h4>1. Что измеряет coverage?</h4>
<p>Coverage показывает в процентах, какие строки (или ветки) исходного кода <strong>выполнились</strong> при запуске тестов. Это показатель того, насколько код "прогнан через тесты", но не гарантия качества.</p>

<h4>2. Какой процент coverage считается "хорошим"?</h4>
<p>100% coverage выглядит идеально, но не всегда практическая цель. Многие команды останавливаются на уровне 80-90% и уделяют особое внимание <strong>важным, критичным</strong> частям (например оплате, аутентификации). Важна не сама цифра, а то, <strong>какие именно строки</strong> остались непротестированными.</p>

<h4>3. Зачем полезен --cov-report=term-missing?</h4>
<p>Обычный <code>--cov</code> показывает только общий процент. <code>term-missing</code> показывает <strong>точные номера строк</strong>, которые ни разу не выполнились — это точно указывает, какие тесты нужно добавить.</p>

<h4>4. Почему 100% coverage не означает отсутствие ошибок в коде?</h4>
<p>Coverage проверяет только то, что строка <strong>выполнилась</strong>, а не правильность <strong>результата</strong>. Тест без <code>assert</code> или с неверным <code>assert</code> может увеличить число покрытых строк, но никогда не найдёт реальные ошибки.</p>

<h4>5. Как правильно использовать coverage?</h4>
<p>Используйте отчёт coverage, чтобы найти, <strong>какой код вообще не протестирован</strong>, а затем напишите для этих частей <strong>содержательные</strong> тесты (с точным assert). Превращение самой цифры coverage в цель может привести к некачественным тестам.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>pytest-cov</code> измеряет, сколько процентов кода выполнили тесты</li>
<li>✅ <code>--cov-report=term-missing</code> показывает точные непротестированные строки</li>
<li>✅ Высокий процент coverage — хороший знак, но не должен быть единственной целью</li>
<li>✅ Coverage измеряет выполнение строк, а не правильность результата</li>
<li>✅ Тест без assert "ложно" повышает coverage, но не находит реальных ошибок</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 5: Test Coverage
# ════════════════════════════════════════════════════════════════════

# ─── baholash.py ───
def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    else:
        return "F"


# ─── test_baholash.py — полный (охватывающий все ветки) ───
def test_harfli_baho_a():
    assert harfli_baho(95) == "A"


def test_harfli_baho_b():
    assert harfli_baho(82) == "B"


def test_harfli_baho_f():
    assert harfli_baho(40) == "F"


# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка — вызов ради coverage, без проверки (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def test_harfli_baho_qamrov_uchun():
#     harfli_baho(82)  # ❌ строка считается "выполненной", но нет assert!
#     # Результат вообще не проверяется — ошибка в функции останется незамеченной.


# Терминал:
#   pip install pytest-cov
#   pytest --cov=baholash                        # общий процент
#   pytest --cov=baholash --cov-report=term-missing  # какие строки не хватает
"""

EX = {
    3783: {
        "title": "Что измеряет test coverage?",
        "description": "Что в основном показывает test coverage (покрытие тестами)?",
        "hint": "Это про то, насколько код \"выполнялся\", а не про качество.",
        "explanation": "Test coverage показывает в процентах, какие строки (или ветки) исходного кода выполнились при запуске тестов.",
    },
    3784: {
        "title": "Зачем полезен --cov-report=term-missing?",
        "description": "Какую дополнительную информацию даёт флаг pytest --cov-report=term-missing?",
        "hint": "Что может означать слово \"Missing\"?",
        "explanation": "--cov-report=term-missing, помимо обычного процента, показывает точные номера строк, которые тесты ни разу не выполнили.",
    },
    3785: {
        "title": "Расположите процесс улучшения coverage в правильном порядке",
        "description": "Упорядочите процесс повышения низкого процента coverage.",
        "hint": "Сначала получаем отчёт, затем находим пробелы, затем добавляем тест.",
    },
    3786: {
        "title": "Почему 100% coverage не гарантирует отсутствие ошибок в коде?",
        "description": (
            "Если тестовая функция вызывает harfli_baho(82), но не пишет "
            "никакого assert, и эта строка считается \"выполненной\", доводя "
            "coverage до 100% — почему это вводит в заблуждение? Что "
            "coverage на самом деле проверяет, а что нет? Объясните своими "
            "словами."
        ),
        "expected_answer": "Coverage измеряет только то, какие строки кода выполнились при запуске тестов — это не проверяет, правильный или неправильный результат этих строк. Если тестовая функция вызывает harfli_baho(82), но не сравнивает результат через assert, строка считается \"выполненной\" и coverage растёт, но даже если функция вернёт неверный результат (например \"C\" вместо \"A\"), тест всё равно останется \"passed\". Поэтому высокий процент coverage — не гарантия правильной работы кода, а лишь показатель того, сколько кода было \"прогнано\".",
        "hint": "Coverage считает \"выполненные строки\" — это то же самое, что \"правильный результат\"?",
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
