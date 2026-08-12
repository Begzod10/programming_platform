"""Russian translation for Python: Testlash, lesson order=5 (L6, CAPSTONE)."""
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

LESSON_ID = 644

TITLE_RU = "6-CAPSTONE: Полностью протестированный Flask API"

TEXT_RU = """\
<h2>🚀 CAPSTONE: Полностью протестированный Flask API</h2>

<p>Это — финальный проект курса. Всё, что изучено в уроках 1-5 — основы pytest, fixture, mock, Flask test_client, TDD и coverage — объединяется в одном реальном проекте: полный набор тестов для <strong>REST API задач (Tasks)</strong>.</p>

<h3>Цель проекта</h3>
<ul>
<li><code>GET /tasks</code>, <code>POST /tasks</code>, <code>PUT /tasks/:id</code>, <code>DELETE /tasks/:id</code> — тесты для полного CRUD</li>
<li>Для каждого endpoint тестируются <strong>как успешные, так и ошибочные</strong> случаи</li>
<li>Изолированный fixture для теста (каждый тест начинается с <strong>чистого</strong> состояния)</li>
<li>Вызов внешнего уведомления (notification) заменяется через <code>mock</code></li>
<li>Новая функция (например "показать только невыполненные задачи") добавляется по TDD</li>
<li>Coverage проверяется через <code>pytest-cov</code></li>
</ul>

<h3>Скелет для начала</h3>
<pre><code># app.py
from flask import Flask, jsonify, request

app = Flask(__name__)
vazifalar = []

@app.route('/tasks', methods=['GET'])
def royxat():
    return jsonify(vazifalar)

@app.route('/tasks', methods=['POST'])
def yaratish():
    # Задание: валидация + добавление новой задачи
    pass

@app.route('/tasks/&lt;int:task_id&gt;', methods=['PUT'])
def yangilash(task_id):
    # Задание: переключение статуса "выполнено"
    pass

@app.route('/tasks/&lt;int:task_id&gt;', methods=['DELETE'])
def ochirish(task_id):
    # Задание: удаление задачи из списка
    pass</code></pre>

<pre><code># conftest.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        # Задание: очистите список задач после каждого теста!</code></pre>

<h3>🐛 Намеренная сложность: "утечка" состояния между тестами (test isolation)</h3>
<pre><code># ❌ conftest.py — очистки НЕТ!
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # ❌ список задач НЕ ОЧИЩАЕТСЯ между тестами!

# test_tasks.py
def test_royxat_bosh(client):
    javob = client.get('/tasks')
    assert javob.get_json() == []  # ❗ Если этот тест запустить ОДИН — PASSED

def test_vazifa_yaratish(client):
    client.post('/tasks', json={"matn": "Non olish"})
    javob = client.get('/tasks')
    assert len(javob.get_json()) == 1</code></pre>

<p><strong>Результат:</strong> если <code>test_royxat_bosh</code> запустить отдельно — он <strong>пройдёт</strong> (потому что список ещё пуст). Но если запустить его <strong>после</strong> <code>test_vazifa_yaratish</code> — он будет <strong>FAILED</strong>! Потому что задача, добавленная предыдущим тестом, осталась в глобальном списке <code>vazifalar</code>. Это классический пример нарушения <strong>test isolation</strong> (независимости тестов): тесты становятся <strong>зависимыми</strong> друг от друга, их результат начинает зависеть от <strong>порядка запуска</strong>. Именно эту проблему решал <code>db.drop_all()</code>, который мы видели в уроке 3 — очистка состояния после каждого теста <strong>обязательна</strong>.</p>

<h3>Задания</h3>

<h4>Задание 1 — полный CRUD + тесты</h4>
<p>Дополните скелет выше, напишите тесты, проверяющие успешные и ошибочные случаи для каждого endpoint.</p>

<h4>Задание 2 — изоляция тестов</h4>
<p>Добавьте в fixture <code>client</code> в conftest.py код, очищающий список <code>vazifalar</code> после каждого теста (после <code>yield</code>).</p>

<h4>Задание 3 — уведомление через mock</h4>
<p>Добавьте функцию, отправляющую уведомление во внешний сервис (например Telegram-бот) при создании задачи, замените её в тесте через <code>@patch</code> — без реального обращения в сеть.</p>

<h4>Задание 4 — новая функция через TDD</h4>
<p><code>GET /tasks?bajarilmagan=true</code> — фильтр, возвращающий только невыполненные задачи. Сначала напишите тест (RED), затем код (GREEN).</p>

<h4>Задание 5 — проверка coverage</h4>
<p>Запустите <code>pytest --cov=app --cov-report=term-missing</code>, найдите непротестированные строки и напишите для них тесты.</p>

<h3>📌 После этого проекта вы знаете</h3>
<ul>
<li>✅ Уроки 1-5 все вместе: fixture, mock, тестирование Flask, TDD, coverage</li>
<li>✅ Test isolation (независимость) — каждый тест должен работать независимо от других, в чистом состоянии</li>
<li>✅ "Утечка" состояния между тестами — опасная ошибка, делающая результат зависимым от порядка запуска</li>
<li>✅ Полностью протестированный небольшой проект — пример реального навыка для портфолио</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# CAPSTONE: Полностью протестированный Flask API — начальный скелет
# ════════════════════════════════════════════════════════════════════

import pytest
from flask import Flask, jsonify, request
from unittest.mock import patch

app = Flask(__name__)
vazifalar = []


def bildirishnoma_yuborish(matn):
    # В реальном проекте здесь вызывается Telegram/email API
    print(f"Bildirishnoma: {matn}")


@app.route('/tasks', methods=['GET'])
def royxat():
    bajarilmagan = request.args.get('bajarilmagan')
    if bajarilmagan == 'true':
        return jsonify([v for v in vazifalar if not v['bajarildi']])
    return jsonify(vazifalar)


@app.route('/tasks', methods=['POST'])
def yaratish():
    data = request.get_json()
    if not data.get('matn'):
        return jsonify({"xato": "'matn' majburiy"}), 400
    yangi = {"id": len(vazifalar) + 1, "matn": data['matn'], "bajarildi": False}
    vazifalar.append(yangi)
    bildirishnoma_yuborish(f"Yangi vazifa: {yangi['matn']}")
    return jsonify(yangi), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def yangilash(task_id):
    for v in vazifalar:
        if v['id'] == task_id:
            v['bajarildi'] = not v['bajarildi']
            return jsonify(v)
    return jsonify({"xato": "Topilmadi"}), 404


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def ochirish(task_id):
    global vazifalar
    oldingi_uzunlik = len(vazifalar)
    vazifalar = [v for v in vazifalar if v['id'] != task_id]
    if len(vazifalar) == oldingi_uzunlik:
        return jsonify({"xato": "Topilmadi"}), 404
    return '', 204


# ─────────────────────────────────────────────────────────────────────
# conftest.py — с ПРАВИЛЬНОЙ изоляцией
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    vazifalar.clear()  # ✅ очистка после каждого теста


# ─────────────────────────────────────────────────────────────────────
# test_tasks.py — полный набор тестов
# ─────────────────────────────────────────────────────────────────────

def test_royxat_bosh(client):
    javob = client.get('/tasks')
    assert javob.get_json() == []


def test_vazifa_yaratish(client):
    javob = client.post('/tasks', json={"matn": "Non olish"})
    assert javob.status_code == 201
    assert javob.get_json()["matn"] == "Non olish"


def test_vazifa_yaratish_xato(client):
    javob = client.post('/tasks', json={})
    assert javob.status_code == 400


@patch('app.bildirishnoma_yuborish')
def test_vazifa_yaratishda_bildirishnoma(mock_bildirish, client):
    client.post('/tasks', json={"matn": "Sut sotib olish"})
    mock_bildirish.assert_called_once()  # ✅ проверяется без реального обращения в сеть


def test_bajarilmagan_filtri(client):
    client.post('/tasks', json={"matn": "1-vazifa"})
    client.post('/tasks', json={"matn": "2-vazifa"})
    client.put('/tasks/1')  # отметить первую как выполненную
    javob = client.get('/tasks?bajarilmagan=true')
    natijalar = javob.get_json()
    assert len(natijalar) == 1
    assert natijalar[0]['matn'] == "2-vazifa"


# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка — fixture без изоляции (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client_xato():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#     # ❌ НЕТ vazifalar.clear() — следующий тест увидит данные предыдущего!
"""

EX = {
    3791: {
        "title": "Почему важна test isolation?",
        "description": "Почему важна \"test isolation\" (независимость) между тестами?",
        "hint": "Один тест не должен \"влиять\" на другой.",
        "explanation": "Test isolation гарантирует, что результат каждого теста не зависит от того, запускались ли другие тесты и в каком порядке.",
    },
    3792: {
        "title": "Что произойдёт, если глобальный список не очищается между тестами?",
        "description": "Если fixture теста не очищает глобальный список задач после каждого теста, к чему это может привести?",
        "hint": "Данные, добавленные в одном тесте, могут \"перейти\" в следующий.",
        "explanation": "Если состояние не очищается, данные, созданные в одном тесте, влияют на следующий — тесты становятся зависимыми, а результат начинает зависеть от порядка их запуска.",
    },
    3793: {
        "title": "Расположите поток написания теста для capstone-проекта в правильном порядке",
        "description": "Упорядочите процесс добавления новой функции фильтра методом TDD.",
        "hint": "Цикл TDD: сначала тест, потом код, затем проверка.",
    },
    3794: {
        "title": "Почему test_royxat_bosh проходит один, но проваливается после другого?",
        "description": (
            "Если fixture client в conftest.py не очищает список задач "
            "между тестами, почему тест test_royxat_bosh проходит при "
            "самостоятельном запуске, но не проходит при запуске после "
            "test_vazifa_yaratish? Какую проблему это показывает? "
            "Объясните своими словами."
        ),
        "expected_answer": "vazifalar — глобальный (на уровне модуля) список, и если fixture не очищает его после каждого теста, данные, добавленные в одном тесте, сохраняются в памяти и \"переходят\" в следующий тест. При самостоятельном запуске test_royxat_bosh список ещё пуст, поэтому assert javob == [] проходит верно. Но при запуске после test_vazifa_yaratish задача, добавленная в том тесте, остаётся в списке, поэтому список уже не пуст, и assert не срабатывает. Это показывает проблему скрытой зависимости тестов друг от друга (отсутствие test isolation): результат тестов начинает зависеть от порядка их запуска, что делает тесты ненадёжными и непредсказуемыми.",
        "hint": "Что произойдёт, если глобальная переменная \"не очищается\" между тестами?",
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
