"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=2 (L3)."""
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

LESSON_ID = 790

TITLE_RU = "3-PostgreSQL CRUD + фикстуры"

TEXT_RU = """\
<h2>Этап 3: PostgreSQL CRUD + фикстуры — flaky (нестабильные) тесты</h2>

<pre class="mermaid">
flowchart LR
    T1["test_get_scores_empty запускается - 0 записей в базе"] --> DB[("Одна общая тестовая база")]
    T2["test_post_score запускается потом - добавляет 1 запись"] --> DB
    DB --> T3["test_get_scores_empty запускается ПОВТОРНО - ТЕПЕРЬ проваливается!"]
</pre>

<p>На 1-м уроке мы оставили <code>tests/conftest.py</code> с пометкой "дополним позже" — и вот этот момент настал. В курсе Python: Testlash вы уже изучили <code>@pytest.fixture</code>, <code>conftest.py</code> и <code>app.test_client()</code>. На этом уроке вы применяете их к RankVault — и увидите <strong>вживую</strong> ту самую опасность, о которой предупреждали на 1-м уроке: даже при наличии отдельной тестовой базы, если данные между тестами не <strong>очищаются</strong>, тесты всё равно влияют друг на друга.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — дополнение conftest.py: отдельная тестовая база</h4>
<pre><code># tests/conftest.py
import pytest
from app import create_app, db as _db

@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])   # ❗ ОТДЕЛЬНАЯ база!
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()</code></pre>

<h4>БЛОК 2 — ЧИСТОЕ состояние для КАЖДОГО теста: fixture автоочистки</h4>
<pre><code># tests/conftest.py - продолжение
@pytest.fixture(autouse=True)
def clean_tables(app):
    yield   # ❗ сначала запускается тест
    with app.app_context():
        _db.session.query(Score).delete()   # ❗ очищается ПОСЛЕ каждого теста
        _db.session.query(User).delete()
        _db.session.commit()</code></pre>

<h4>БЛОК 3 — полный тест для GET /scores, опираясь на чистое состояние</h4>
<pre><code># tests/test_scores.py
def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.status_code == 200
    assert response.get_json() == []   # ❗ ожидается пустая база

def test_get_scores_after_post(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    response = client.get('/scores')
    assert len(response.get_json()) == 1</code></pre>

<h3>🐛 Намеренная ошибка — отдельная база ЕСТЬ, но очистки НЕТ</h3>
<pre><code># conftest.py - подключена к ОТДЕЛЬНОЙ тестовой базе (правильно!), но
# fixture `clean_tables` НЕ НАПИСАН - данные остаются между тестами:
@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()   # ❗ Это работает ТОЛЬКО в конце ВСЕЙ сессии тестов!

@pytest.fixture
def client(app):
    return app.test_client()
# ❌ Между тестами ничего НЕ ОЧИЩАЕТСЯ!

# tests/test_scores.py - два теста, написанные ПОДРЯД:
def test_post_score(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    # эта запись ОСТАЁТСЯ в базе

def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.get_json() == []   # ❌ Если test_post_score запустился
    # РАНЬШЕ, в базе УЖЕ есть 1 запись - этот тест ПРОВАЛИТСЯ!

# Но если pytest запустит их в ОБРАТНОМ порядке (например из-за другого
# расположения в файле, или при отключённом -p no:randomly),
# оба могут выглядеть "зелёными"!</code></pre>

<p><strong>Результат:</strong> подключение к отдельной тестовой базе (<code>TEST_DATABASE_URL</code>) — это <strong>необходимо</strong>, но <strong>недостаточно</strong>. Если данные между тестами не очищаются, данные, записанные одним тестом, "просачиваются" в <strong>следующий</strong> тест. Такие тесты называются <strong>flaky</strong> (нестабильными) — они могут давать разный результат в зависимости от <strong>порядка</strong> запуска. Тестовый набор, "зелёный" сегодня, завтра, при запуске в другом порядке, может стать "красным" <strong>без единого изменения кода</strong> — это сбивает разработчиков с толку: возникает вопрос "что изменилось?", хотя на самом деле ничего не изменилось, просто порядок тестов был другим.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему отдельной тестовой базы (<code>TEST_DATABASE_URL</code>) недостаточно?</h4>
<p>Отдельная база лишь отделяет тесты <strong>от production</strong> — это важно, но не гарантирует изоляцию тестов <strong>друг от друга</strong>. Если все тесты <strong>делят</strong> одну тестовую базу и никто её не очищает, тесты всё равно влияют друг на друга — только теперь страдает не production, а <strong>другие тесты</strong>.</p>

<h4>2. Что делает fixture <code>clean_tables</code> с <code>autouse=True</code>?</h4>
<p><code>autouse=True</code> означает, что этот fixture автоматически применяется к <strong>каждому</strong> тесту, вызывать его отдельно не нужно. Код после <code>yield</code> выполняется <strong>после</strong> каждого теста — здесь, очищая таблицы, он гарантирует, что следующий тест всегда начинается с <strong>чистого</strong> состояния.</p>

<h4>3. Почему flaky-тесты особенно опасны?</h4>
<p>Обычный, стабильно проваливающийся тест сразу привлекает внимание и исправляется. Flaky-тест же проваливается <strong>время от времени</strong>, поэтому разработчики часто <strong>игнорируют</strong> его, считая "случайной ошибкой", или просто перезапускают в надежде, что "пройдёт" — а это может скрыть настоящие, серьёзные проблемы на фоне "случайных ошибок".</p>

<h4>4. Почему эта проблема иногда видна, а иногда нет?</h4>
<p>Порядок тестов <strong>не детерминирован</strong> — pytest по умолчанию запускает файлы в алфавитном порядке, но плагин (например <code>pytest-randomly</code>) или выборочный запуск тестов может <strong>изменить</strong> порядок. Поэтому ошибка проявляется только при <strong>определённом</strong> порядке — это ещё больше усложняет её обнаружение.</p>

<h4>5. Как это связано с "намеренной сложностью" на 1-м уроке?</h4>
<p>На 1-м уроке мы увидели <strong>теоретически</strong>, что откладывание тестовой инфраструктуры опасно. На этом уроке вы увидели это <strong>вживую</strong>: даже при правильно настроенной отдельной базе, если нет механизма <strong>очистки</strong>, опасность всё равно проявляется — это показывает, что тестовая инфраструктура — это не <strong>разовая настройка</strong>, а постоянная практика, о которой нужно помнить <strong>при написании каждого нового теста</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Отдельная тестовая база необходима, но недостаточна - данные между тестами тоже должны очищаться</li>
<li>✅ Fixture с <code>autouse=True</code> используется для автоматической очистки после каждого теста</li>
<li>✅ Flaky-тесты дают разный результат в зависимости от порядка - это делает их особенно опасными и трудными для обнаружения</li>
<li>✅ Порядок тестов не детерминирован - плагин или выборочный запуск может его изменить</li>
<li>✅ Тестовая инфраструктура - не разовая настройка, а постоянная практика</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 3: PostgreSQL CRUD + фикстуры
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) tests/conftest.py - отдельная тестовая база + автоочистка
# ─────────────────────────────────────────────────────────────────────

import os
import pytest
from app import create_app, db as _db
from app.models import Score, User


@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_tables(app):
    yield
    with app.app_context():
        _db.session.query(Score).delete()
        _db.session.query(User).delete()
        _db.session.commit()


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_scores.py - GET /scores, опираясь на чистое состояние
# ─────────────────────────────────────────────────────────────────────

def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_scores_after_post(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    response = client.get('/scores')
    assert len(response.get_json()) == 1


# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - conftest.py без очистки (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def app():
#     app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
#     with app.app_context():
#         _db.create_all()
#         yield app
#         _db.drop_all()   # только в конце ВСЕЙ сессии!
# # fixture clean_tables ВООБЩЕ ОТСУТСТВУЕТ - данные остаются между
# # тестами, результат меняется в зависимости от ПОРЯДКА запуска (flaky).
"""

EX = {
    4554: {
        "title": "Почему отдельной тестовой базы недостаточно?",
        "description": "Почему подключение к отдельной тестовой базе через TEST_DATABASE_URL НЕДОСТАТОЧНО для предотвращения flaky-тестов?",
        "hint": "От ЧЕГО отделяет отдельная база, и что ВСЁ ЕЩЁ является общим?",
        "explanation": "Отдельная тестовая база отделяет тесты от production-данных, но если все тесты делят одну и ту же тестовую базу и никто её не очищает, тесты всё равно влияют друг на друга (теперь уже на другие тесты).",
    },
    4555: {
        "title": "Что делает fixture с autouse=True?",
        "description": "Какова задача fixture clean_tables, помеченного как @pytest.fixture(autouse=True)?",
        "hint": "Слово 'autouse' означает 'применяется автоматически'.",
        "explanation": "Fixture с autouse=True автоматически применяется к каждому тесту (вызывать отдельно не нужно). Код после yield выполняется после каждого теста - здесь, очищая таблицы, он гарантирует, что следующий тест начинается с чистого состояния.",
    },
    4556: {
        "title": "Расположите процесс возникновения flaky-теста",
        "description": "Расположите процесс возникновения flaky-поведения между двумя тестами при отсутствии fixture очистки.",
        "hint": "",
        "explanation": "",
    },
    4557: {
        "title": "Название тестов с разным результатом в зависимости от порядка",
        "description": "Как называются тесты, которые иногда проходят, а иногда проваливаются в зависимости от порядка запуска? (ответьте английским термином)",
        "hint": "Это слово использовано и в заголовке урока.",
        "expected_answer": "flaky",
    },
    4558: {
        "title": "Почему flaky-тесты опаснее обычных проваливающихся тестов?",
        "description": (
            "По сравнению с тестом, который стабильно проваливается, "
            "почему flaky-тест (проваливающийся время от времени) "
            "представляет большую опасность? Объясните своими словами."
        ),
        "hint": "Стабильная ошибка сразу привлекает внимание. Как относятся к ошибке, которая появляется время от времени?",
        "expected_answer": "Стабильно проваливающийся тест сразу заметен и обязательно исправляется. Flaky-тест же проваливается лишь ВРЕМЯ ОТ ВРЕМЕНИ, поэтому разработчики часто не воспринимают его всерьёз, считая 'случайной ошибкой' или 'проблемой сети/окружения', и просто перезапускают его в надежде, что он 'пройдёт'. Это формирует в команде привычку игнорировать flaky-тесты - и именно из-за этой привычки НАСТОЯЩИЕ, серьёзные ошибки тоже могут быть списаны на 'ещё один flaky-тест' и оставлены без внимания.",
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
        TASK_TITLE_RU = "RankVault — PostgreSQL CRUD + фикстуры (без flaky-тестов)"
        TASK_DESCRIPTION_RU = (
            "Продолжая POST /scores со 2-го этапа, напишите эндпоинты GET "
            "/scores, GET /scores/:id и DELETE /scores/:id. Дополните "
            "tests/conftest.py отдельной базой через TEST_DATABASE_URL И "
            "fixture'ом clean_tables с autouse=True — тесты должны "
            "стабильно проходить независимо от порядка запуска."
        )
        TASK_REQUIREMENTS_RU = (
            "• tests/conftest.py: подключение к отдельной тестовой базе через TEST_DATABASE_URL\n"
            "• Fixture clean_tables с autouse=True — очищает таблицы после каждого теста\n"
            "• Написаны эндпоинты GET /scores, GET /scores/:id, DELETE /scores/:id\n"
            "• Повторный запуск pytest (несколько раз подряд) даёт стабильный результат\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, PostgreSQL, SQLAlchemy"
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
