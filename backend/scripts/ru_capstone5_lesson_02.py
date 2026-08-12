"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=1 (L2)."""
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

LESSON_ID = 788

TITLE_RU = "2-Flask API + основы TDD"

TEXT_RU = """\
<h2>Этап 2: Flask API + основы TDD — RED-GREEN-REFACTOR и ошибка "подделки"</h2>

<pre class="mermaid">
flowchart LR
    RED["RED: пишется неудачный тест"] --> GREEN{"GREEN: как заставить тест пройти?"}
    GREEN -->|"Реальная, общая логика"| REAL["Работает для любого ввода"]
    GREEN -->|"Просто зашить ожидаемое значение"| FAKE["'Подделка' - работает ТОЛЬКО для этого одного случая"]
    FAKE --> HIDDEN["С одним тестом эта подделка остаётся незамеченной"]
</pre>

<p>В курсе Python: Testlash вы уже изучили основы pytest и цикл TDD (Red-Green-Refactor). На этом уроке вы применяете их к первому реальному эндпоинту RankVault — <code>POST /scores</code>. Но здесь раскрывается самое непонятое место TDD: рекомендация писать на этапе GREEN "простейший код, который проходит тест", если понята неправильно, может превратиться в ошибку <strong>"подделки" (faking it)</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — RED: сначала пишется неудачный тест</h4>
<pre><code># tests/test_scores.py
def test_post_score_returns_created_score(client):
    response = client.post('/scores', json={'user_id': 1, 'points': 100})
    assert response.status_code == 201
    assert response.get_json()['points'] == 100

# На этом этапе эндпоинта /scores вообще не существует - тест обязательно
# ПРОВАЛИТСЯ (404 или ошибка). Это - RED. ВАЖНО увидеть, что тест
# ДЕЙСТВИТЕЛЬНО провалился - иначе он может вообще ничего не проверять.</code></pre>

<h4>БЛОК 2 — GREEN: РЕАЛЬНЫЙ, общий код, который проходит тест</h4>
<pre><code># app/routes.py
from flask import request, jsonify
from app import app, db
from app.models import Score

@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    score = Score(user_id=data['user_id'], points=data['points'])
    db.session.add(score)
    db.session.commit()
    return jsonify({'id': score.id, 'points': score.points}), 201</code></pre>

<h4>БЛОК 3 — Triangulation: подтверждение общности ВТОРЫМ тестом</h4>
<pre><code># tests/test_scores.py - добавляется ВТОРОЙ тест с другими значениями
def test_post_score_with_different_values(client):
    response = client.post('/scores', json={'user_id': 2, 'points': 250})
    assert response.status_code == 201
    assert response.get_json()['points'] == 250

# Если код - РЕАЛЬНАЯ логика, этот тест ТОЖЕ пройдёт автоматически -
# потому что функция работает для любого ввода. Это - "triangulation":
# через несколько разных тестовых случаев код "принуждается" к
# ОБЩЕМУ решению, а не только к одному случаю.</code></pre>

<h3>🐛 Намеренная ошибка — "подделка" (faking it): зашить только ожидаемое значение</h3>
<pre><code># Решив "пройду тест простейшим способом", вместо РЕАЛЬНОЙ логики -
# просто зашить точные значения, которые ожидает тест:
@app.route('/scores', methods=['POST'])
def create_score():
    return jsonify({'id': 1, 'points': 100}), 201   # ❌ ЗАШИТО!
    # Никакой записи в БД, request.get_json() вообще не читается!

# С единственным тестом из БЛОКА 1 этот код ПОЛНОСТЬЮ проходит "зелёным":
# ✅ test_post_score_returns_created_score PASSED
#
# Но этот эндпоинт на самом деле НИЧЕГО не делает - он всегда
# возвращает ОДИН И ТОТ ЖЕ ответ { "id": 1, "points": 100 } для
# любого запроса. Данные никогда не сохраняются в базе!</code></pre>

<p><strong>Результат:</strong> "подделка" (faking it) — ошибка, возникающая из-за <strong>неправильного</strong> понимания этапа GREEN в TDD: "простейший код" не означает "зашить значение, которое ожидает тест" — это означает "простейшее <strong>общее</strong> решение, работающее для любого корректного ввода". Если в проекте всего <strong>один</strong> тестовый случай, разница между этими двумя <strong>не видна</strong> — оба делают тест "зелёным". Разница проявляется только когда добавляется <strong>второй тест с другими</strong> значениями: зашитый код на втором тесте обязательно <strong>провалится</strong>, потому что он "запомнил" только один случай.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему на этапе RED важно увидеть, что тест ДЕЙСТВИТЕЛЬНО провалился?</h4>
<p>Если тест сразу после написания выдаёт "зелёный" результат (например из-за опечатки тест вообще ничего не проверяет), это означает, что <strong>сам</strong> тест ненадёжен. Увидеть этап RED — способ убедиться, что тест <strong>действительно</strong> проверяет нужное.</p>

<h4>2. В чём разница между "простейшим кодом" и "подделкой"?</h4>
<p>"Простейший код" — логика, проходящая тест, но <strong>реальная, общая</strong> (например сохранение входных данных в базу). "Подделка" — прохождение теста через <strong>зашивание</strong> точных ожидаемых значений, без какой-либо общей логики. Оба выглядят "простыми", но реально <strong>работает только один</strong> из них.</p>

<h4>3. Почему одного теста недостаточно — что такое "triangulation"?</h4>
<p>С одним тестовым случаем "подделка" и настоящее решение <strong>неотличимы</strong>. Когда добавляется второй тест с <strong>другими</strong> значениями, зашитая "подделка" обязательно ломается — это <strong>заставляет</strong> разработчика написать <strong>общее</strong> решение. Эта техника называется <strong>triangulation</strong>.</p>

<h4>4. Всегда ли этап REFACTOR разоблачает подделку?</h4>
<p><strong>Нет</strong> — если в проекте всё ещё только один тест, на этапе REFACTOR это тоже может остаться незамеченным, потому что код всё равно "зелёный". Подделка обнаруживается только когда добавляется <strong>новый, другой</strong> тестовый случай.</p>

<h4>5. К чему это приводит в реальном проекте?</h4>
<p>Если другой разработчик (или вы сами на следующем уроке) поверит, что эндпоинт <code>/scores</code> <strong>действительно</strong> сохраняет данные, и начнёт строить на нём что-то (например расчёт рейтинга — на 4-м уроке), но на самом деле в базу ничего не записывается, это приведёт к непонятным ошибкам вида "данные потерялись" на <strong>более поздних</strong> этапах — а настоящий источник ошибки (изначально зашитый, нерабочий эндпоинт) останется скрытым <strong>гораздо раньше</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ На этапе RED важно увидеть, что тест действительно провалился - это подтверждает надёжность самого теста</li>
<li>✅ "Простейший код" - это общая, реальная логика, а не "зашитое значение"</li>
<li>✅ Один тестовый случай не может отличить "подделку" от настоящего решения</li>
<li>✅ Triangulation - принуждение кода к общему решению через несколько разных тестовых случаев</li>
<li>✅ Зашитая "подделка" разоблачается только при добавлении нового теста - до этого момента она остаётся опасной, скрытой</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 2: Flask API + основы TDD
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) tests/test_scores.py - RED, затем 2-й тест для triangulation
# ─────────────────────────────────────────────────────────────────────

def test_post_score_returns_created_score(client):
    response = client.post('/scores', json={'user_id': 1, 'points': 100})
    assert response.status_code == 201
    assert response.get_json()['points'] == 100


def test_post_score_with_different_values(client):
    response = client.post('/scores', json={'user_id': 2, 'points': 250})
    assert response.status_code == 201
    assert response.get_json()['points'] == 250


# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - GREEN: реальный, общий код
# ─────────────────────────────────────────────────────────────────────

from flask import request, jsonify
from app import app, db
from app.models import Score


@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    score = Score(user_id=data['user_id'], points=data['points'])
    db.session.add(score)
    db.session.commit()
    return jsonify({'id': score.id, 'points': score.points}), 201


# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - "подделка" (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @app.route('/scores', methods=['POST'])
# def create_score():
#     return jsonify({'id': 1, 'points': 100}), 201   # зашито!
#     # request.get_json() вообще не читается, в БД ничего не пишется.
#
# С единственным тестом это проходит "зелёным" - но с добавлением
# второго теста с другими значениями обязательно провалится.
"""

EX = {
    4544: {
        "title": "Почему на этапе RED тест должен ДЕЙСТВИТЕЛЬНО провалиться?",
        "description": "Почему важно увидеть, что написанный на этапе RED тест ДЕЙСТВИТЕЛЬНО провалился, а не просто выполнился?",
        "hint": "Если тест сразу после написания оказывается зелёным, что это может означать?",
        "explanation": "Увидеть этап RED - способ убедиться, что тест действительно проверяет нужное. Если тест сразу после написания зелёный, возможно, он вообще ничего правильно не проверяет.",
    },
    4545: {
        "title": "Разница между 'простейшим кодом' и 'подделкой'",
        "description": "В чём основная разница между рекомендуемым на этапе GREEN 'простейшим кодом' и 'подделкой' (faking it)?",
        "hint": "Оба выглядят 'простыми', но только один реально работает.",
        "explanation": "'Простейший код' - это общая, реальная логика, проходящая тест. 'Подделка' же - прохождение теста через зашивание точных ожидаемых значений, без какой-либо общей логики.",
    },
    4546: {
        "title": "Расположите цикл TDD (с triangulation)",
        "description": "Расположите процесс построения эндпоинта POST /scores через TDD с использованием triangulation.",
        "hint": "",
        "explanation": "",
    },
    4547: {
        "title": "Способ принуждения кода к общему решению через несколько тестовых случаев",
        "description": "Напишите название техники в TDD, принуждающей код от 'подделки' к общему решению через несколько разных тестовых случаев.",
        "hint": "Это слово происходит от геометрического термина 'триангуляция'.",
        "expected_answer": "triangulation",
    },
    4548: {
        "title": "Почему ошибка 'подделки' опасна в реальном проекте?",
        "description": (
            "Если эндпоинт /scores на самом деле ничего не сохраняет в "
            "базу, а только возвращает зашитое значение, и другой "
            "разработчик начинает строить на этом эндпоинте (например "
            "функцию расчёта рейтинга), к чему это может привести? "
            "Объясните своими словами."
        ),
        "hint": "Если эндпоинт на самом деле не сохраняет данные, на что опираются последующие функции?",
        "expected_answer": "Если эндпоинт /scores написан через 'подделку', он не сохраняет никаких данных в базу - а лишь возвращает одно и то же зашитое значение. Если другой разработчик (или сам разработчик на следующем уроке) поверит, что этот эндпоинт ДЕЙСТВИТЕЛЬНО сохраняет данные, и начнёт строить на нём такие функции, как расчёт рейтинга, на более поздних этапах появятся непонятные ошибки вида 'данные потерялись', 'рейтинг рассчитывается неверно' - а настоящий источник этих ошибок (изначально зашитый, нерабочий эндпоинт) останется скрытым намного раньше, и его будет сложно найти.",
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
        TASK_TITLE_RU = "RankVault — Flask API + основы TDD (POST /scores)"
        TASK_DESCRIPTION_RU = (
            "Используя цикл TDD (RED-GREEN-REFACTOR), напишите эндпоинт "
            "POST /scores. Напишите тесты минимум с ДВУМЯ разными "
            "значениями (triangulation) — код должен принимать не только "
            "один случай, а ЛЮБОЙ корректный ввод, и сохранять его в базу."
        )
        TASK_REQUIREMENTS_RU = (
            "• tests/test_scores.py: минимум 2 теста с разными значениями (triangulation)\n"
            "• POST /scores — написан с реальной, общей логикой (НЕ зашитое значение)\n"
            "• Подтверждено, что каждый POST-запрос действительно добавляет запись в таблицу Score\n"
            "• В истории git-коммитов видны этапы RED (неудачный тест) и GREEN (пройденный тест)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, TDD"
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
