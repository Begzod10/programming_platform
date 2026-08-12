"""Russian translation for Python: Testlash, lesson order=2 (L3)."""
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

LESSON_ID = 638

TITLE_RU = "3-Тестирование Flask-приложения"

TEXT_RU = """\
<h2>Тестирование Flask-приложения — test_client и тестовая база данных</h2>

<pre class="mermaid">
flowchart LR
    TC["app.test_client()"] -->|отправляет запрос| R["Flask route"]
    R --> RESP["ответ: status_code + JSON"]
    RESP --> A["проверяется через assert"]
    TESTDB[("Тестовая DB — отдельная!")] --> R
</pre>

<p>В уроках 1-2 мы тестировали простые функции. Теперь протестируем целое Flask-приложение, то есть процесс HTTP запрос-ответ. Flask предоставляет для этого специальный инструмент: <strong>test_client</strong> — "поддельный клиент", позволяющий отправлять запросы без реального запуска сервера.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первый запрос через test_client</h4>
<pre><code># app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def bosh_sahifa():
    return jsonify({"xabar": "Salom!"})</code></pre>

<pre><code># test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    return app.test_client()  # ❗ реальный сервер не запускается!

def test_bosh_sahifa(client):
    javob = client.get('/')
    assert javob.status_code == 200
    assert javob.get_json() == {"xabar": "Salom!"}</code></pre>

<h4>БЛОК 2 — POST-запрос и проверка статус-кодов</h4>
<pre><code>@app.route('/users', methods=['POST'])
def user_yaratish():
    data = request.get_json()
    if not data.get('ism'):
        return jsonify({"xato": "ism majburiy"}), 400
    return jsonify({"id": 1, "ism": data['ism']}), 201</code></pre>

<pre><code>def test_user_yaratish_togri(client):
    javob = client.post('/users', json={"ism": "Olim"})
    assert javob.status_code == 201
    assert javob.get_json()["ism"] == "Olim"

def test_user_yaratish_xato(client):
    javob = client.post('/users', json={})  # нет имени
    assert javob.status_code == 400</code></pre>

<h4>БЛОК 3 — fixture тестовой базы данных</h4>
<pre><code># conftest.py
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # ❗ временная БД в памяти
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # создаются чистые таблицы для теста
            yield client
            db.drop_all()  # после теста всё очищается</code></pre>

<h3>🐛 Намеренная ошибка — тесты против production базы данных</h3>
<pre><code># ❌ conftest.py — TESTING не настроен, используется РЕАЛЬНЫЙ DATABASE_URL!
import pytest
from app import app, db

@pytest.fixture
def client():
    # app.config['SQLALCHEMY_DATABASE_URI'] всё ещё РЕАЛЬНЫЙ адрес БД из .env!
    with app.test_client() as client:
        yield client

def test_user_ochirish(client):
    client.delete('/users/1')  # ❗ Это удалит РЕАЛЬНОГО пользователя!</code></pre>

<p><strong>Результат:</strong> если в fixture теста не изменить <code>SQLALCHEMY_DATABASE_URI</code> на конкретную тестовую базу (например <code>sqlite:///:memory:</code>), приложение <strong>всё ещё подключается к production (реальной)</strong> базе данных. Тесты обычно добавляют, изменяют и удаляют данные — это может полностью повредить или уничтожить данные реальных пользователей! Это одна из самых опасных, катастрофических ошибок тестирования.</p>

<h3>Теперь объясним</h3>

<h4>1. Что делает test_client()?</h4>
<p><code>app.test_client()</code> — специальный объект, позволяющий отправлять запросы напрямую (в памяти) в Flask-приложение, без запуска сервера на реальном порту. Это значительно ускоряет тесты — проблем вроде сети или занятости порта вообще не возникает.</p>

<h4>2. javob.status_code и javob.get_json()</h4>
<p>Каждый запрос через <code>test_client</code> (<code>client.get()</code>, <code>client.post()</code> и т.д.) возвращает объект ответа. <code>status_code</code> — HTTP-статус (200, 201, 400...), <code>get_json()</code> превращает тело ответа в Python-объект (dict/list).</p>

<h4>3. Почему для тестов нужна ОТДЕЛЬНАЯ база данных?</h4>
<p>Тесты запускаются часто и обычно связаны с созданием/удалением данных. Если они подключены к production DB, реальные данные оказываются под угрозой при каждом запуске теста. Поэтому для тестов используется <strong>отдельная, временная</strong> база (например SQLite в памяти).</p>

<h4>4. Что такое sqlite:///:memory:?</h4>
<p>Это временная база SQLite, которая живёт <strong>в памяти</strong>, а не на диске. После завершения теста она автоматически исчезает — не остаётся никаких файлов или внешних зависимостей, и каждый запуск теста начинается с "чистого" состояния.</p>

<h4>5. db.create_all() / db.drop_all() — зачем внутри fixture?</h4>
<p><code>db.create_all()</code> создаёт таблицы перед началом теста, <code>db.drop_all()</code> очищает всё после завершения. Это помещается внутрь fixture через <code>yield</code>, обеспечивая, что каждый тест работает в <strong>чистой, независимой от других тестов</strong> среде.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>app.test_client()</code> позволяет отправлять запросы в Flask-приложение без реального сервера</li>
<li>✅ <code>javob.status_code</code> и <code>javob.get_json()</code> — основные инструменты проверки HTTP-ответа</li>
<li>✅ Тесты никогда не должны подключаться к production базе данных — используется отдельная тестовая DB</li>
<li>✅ <code>sqlite:///:memory:</code> — временная база в памяти, начинающая каждый раз с чистого состояния</li>
<li>✅ <code>db.create_all()</code>/<code>db.drop_all()</code> внутри fixture обеспечивают независимую, изолированную среду для каждого теста</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 3: Тестирование Flask-приложения
# ════════════════════════════════════════════════════════════════════

import pytest
from flask import Flask, jsonify, request

# ─── app.py (упрощённо) ───
app = Flask(__name__)
users = []

@app.route('/')
def bosh_sahifa():
    return jsonify({"xabar": "Salom!"})


@app.route('/users', methods=['POST'])
def user_yaratish():
    data = request.get_json()
    if not data.get('ism'):
        return jsonify({"xato": "ism majburiy"}), 400
    yangi_user = {"id": len(users) + 1, "ism": data['ism']}
    users.append(yangi_user)
    return jsonify(yangi_user), 201


# ─────────────────────────────────────────────────────────────────────
# conftest.py — ОТДЕЛЬНАЯ конфигурация для тестов
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # тестовая БД в памяти
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────────────────────────────
# test_app.py
# ─────────────────────────────────────────────────────────────────────

def test_bosh_sahifa(client):
    javob = client.get('/')
    assert javob.status_code == 200
    assert javob.get_json() == {"xabar": "Salom!"}


def test_user_yaratish_togri(client):
    javob = client.post('/users', json={"ism": "Olim"})
    assert javob.status_code == 201
    assert javob.get_json()["ism"] == "Olim"


def test_user_yaratish_xato(client):
    javob = client.post('/users', json={})
    assert javob.status_code == 400


# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка — TESTING/тестовая DB не настроены (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client_xato():
#     # ❌ SQLALCHEMY_DATABASE_URI не изменён — всё ещё РЕАЛЬНАЯ DB из .env!
#     with app.test_client() as client:
#         yield client
#
# def test_user_ochirish_xato(client_xato):
#     client_xato.delete('/users/1')  # ❌ Может удалить РЕАЛЬНОГО пользователя!
"""

EX = {
    3767: {
        "title": "Зачем нужен test_client()?",
        "description": "Для чего в основном используется app.test_client() во Flask?",
        "hint": "Это \"поддельный клиент\", предназначенный для тестов.",
        "explanation": "app.test_client() позволяет отправлять запросы напрямую в Flask-приложение без запуска сервера на реальном порту, что ускоряет тесты.",
    },
    3768: {
        "title": "Что возвращает javob.get_json()?",
        "description": "Что делает get_json() у объекта ответа, полученного от запроса test_client?",
        "hint": "Этот метод подготавливает JSON-ответ для использования в Python.",
        "explanation": "get_json() превращает JSON-текст тела ответа в Python-объект dict или list, чтобы его можно было проверить обычным Python-кодом.",
    },
    3769: {
        "title": "Расположите fixture теста Flask в правильном порядке",
        "description": "Упорядочите шаги подготовки изолированной тестовой среды Flask.",
        "hint": "Сначала конфигурация, затем подготовка базы, затем работа теста, затем очистка.",
    },
    3770: {
        "title": "Почему для теста обязательна отдельная база данных?",
        "description": (
            "Если в fixture теста SQLALCHEMY_DATABASE_URI всё ещё указывает "
            "на production-базу (не изменён на тестовую), почему это "
            "считается серьёзной опасностью? Как этого можно избежать? "
            "Объясните своими словами."
        ),
        "expected_answer": "Тесты обычно выполняют операции создания, изменения и удаления данных. Если они подключены к реальной (production) базе данных, при каждом запуске теста данные реальных пользователей могут быть изменены или полностью удалены — это может нанести непоправимый ущерб. Чтобы этого избежать, тесты всегда должны работать с отдельной, временной базой данных (например sqlite:///:memory:), и это должно быть явно задано через SQLALCHEMY_DATABASE_URI в fixture теста.",
        "hint": "Тесты создают/удаляют данные — что произойдёт, если это происходит в реальной базе?",
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
