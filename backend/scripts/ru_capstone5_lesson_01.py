"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=0 (L1)."""
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

LESSON_ID = 786

TITLE_RU = "1-Планирование и скелет репозитория"

TEXT_RU = """\
<h2>RankVault — проект, построенный на тестировании и алгоритмах, в 7 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> API["2-Flask API + TDD"]
    API --> DB["3-PostgreSQL + фикстуры"]
    DB --> RANK["4-Алгоритм рейтинга"]
    RANK --> COV["5-Coverage + бинарный поиск"]
    COV --> CACHE["6-HashMap + мокирование"]
    CACHE --> DEPLOY["7-Деплой (завершение CAPSTONE)"]
</pre>

<p>В этом курсе вы объедините всё, что изучали <strong>по отдельности</strong> в курсах Python: Testlash и Python: Algoritmlar va Ma'lumotlar Tuzilmasi, в <strong>одном реальном проекте</strong>: <strong>RankVault</strong> — система рейтинга/очков для соревнований (leaderboard). Каждый урок — очередной этап этого одного проекта.</p>

<p>Но этот capstone отличается от предыдущих четырёх одной вещью: на этот раз "намеренная ошибка" находится <strong>не в самом коде</strong> — она скрыта в <strong>ложной уверенности</strong>, которую дают тесты или непроверенные состояния алгоритма. Зелёный тест, высокий процент coverage, "успешный" CI — всё это может ложно подтверждать реальную корректность. Каждый этап показывает эту идею в новом месте.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — скелет репозитория и политика TDD</h4>
<pre><code># Структура репозитория для RankVault
rankvault/
  app/
    __init__.py
    models.py
    routes.py
  tests/
    conftest.py        # ❗ дополняется на 3-м уроке - отдельная тестовая БД
    test_scores.py
  requirements.txt
  README.md
  .gitignore

# Политика TDD, которая пишется в README.md:
# "Каждая новая функция НАЧИНАЕТСЯ с теста (RED),
#  затем пишется простейший код, чтобы тест прошёл (GREEN),
#  затем код очищается (REFACTOR)."</code></pre>

<h4>БЛОК 2 — схема БД: users и scores</h4>
<pre><code># Основные таблицы для RankVault (на уровне ER-диаграммы):
#
# users   (id, username, created_at)
# scores  (id, user_id -> users.id, points, submitted_at)
#
# Связь: один user -> много scores (1 ко многим)
# - "рейтинг" - сортировка всех пользователей по САМОМУ ВЫСОКОМУ (или общему) баллу</code></pre>

<h4>БЛОК 3 — pytest + pytest-cov + подготовка МЕСТА для отдельной тестовой БД</h4>
<pre><code># requirements.txt
# flask
# psycopg2-binary
# pytest
# pytest-cov

# tests/conftest.py - ПОКА скелет, дополняется на 3-м уроке
import pytest

@pytest.fixture
def client():
    # ❗ Сюда на 3-м уроке добавится конфигурация приложения,
    # подключающаяся к ОТДЕЛЬНОЙ тестовой базе - пока placeholder.
    raise NotImplementedError("Дополняется на 3-м уроке")</code></pre>

<h3>🐛 Намеренная сложность: откладывать настройку тестовой инфраструктуры "на потом"</h3>
<p>В TaskFlow (Capstone 1) попытка писать код без схемы БД создавала проблему. Здесь похожая, но касающаяся <strong>тестовой инфраструктуры</strong> ошибка: многие разработчики планируют настроить отдельную тестовую базу в <code>conftest.py</code> (например через <code>TEST_DATABASE_URL</code>) <strong>не в начале проекта</strong>, а "позже, когда тестов станет больше":</p>
<pre><code># Решив "пока обойдусь production-базой, отделю позже", оставляют
# tests/conftest.py пустым или подключают напрямую к основному DATABASE_URL:
@pytest.fixture
def client():
    app.config['DATABASE_URL'] = os.environ['DATABASE_URL']  # ❗ PRODUCTION база!
    return app.test_client()</code></pre>
<p><strong>Результат:</strong> пока (проект маленький, тестов мало) это выглядит <strong>безобидно</strong>. Но когда на 3-м уроке количество тестов вырастет, это решение приведёт к <strong>flaky (нестабильным) тестам</strong> — тесты будут влиять на данные друг друга, и результат будет меняться в зависимости от порядка запуска. Правильный подход: планировать тестовую инфраструктуру (отдельная БД, откат транзакций) <strong>с самого начала проекта</strong>, пока проблема ещё не проявилась.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему "намеренные ошибки" в этом capstone отличаются от других?</h4>
<p>В предыдущих четырёх capstone-проектах ошибка всегда была <strong>в самом коде</strong> (например неверный SQL, cast без проверки). Здесь же ошибка чаще <strong>в самих тестах или в алгоритме</strong> — код выглядит "рабочим", тесты "зелёные", но на самом деле какой-то важный случай <strong>никогда не был протестирован</strong> или протестирован неправильно.</p>

<h4>2. Почему политику TDD нужно записать в README с самого начала проекта?</h4>
<p>TDD (сначала тест, потом код) — это <strong>привычка</strong>, а привычки, если их не закрепить строго в начале проекта, по мере роста проекта отбрасываются под предлогом "экономии времени". Запись в README служит <strong>напоминающим</strong> документом об этом правиле в командном (или даже сольном) проекте.</p>

<h4>3. Почему отдельную тестовую базу (<code>TEST_DATABASE_URL</code>) нужно планировать с самого начала?</h4>
<p>Если тесты работают в <strong>той же</strong> базе данных, что и production (или development), данные, записанные/удалённые одним тестом, могут <strong>повлиять</strong> на другой тест. Это — корень проблемы "flaky test", которую вы увидите на 3-м уроке. Заранее спланировать это - значит избежать большой переделки позже.</p>

<h4>4. Почему выбрана именно "система рейтинга/очков" (leaderboard)?</h4>
<p>Вычисление рейтинга — внешне простая задача (отсортировать пользователей по баллам), но внутри скрывает <strong>множество нюансов</strong>: как обрабатываются равные баллы, как обрабатывается пустой список, как обеспечивается скорость при большом объёме данных. Это — <strong>богатый</strong> материал для алгоритмов (сортировка, поиск, хеширование) и тестирования (охват граничных случаев).</p>

<h4>5. Какова общая идея этих 7 этапов?</h4>
<p>Каждый этап по-своему показывает, что "зелёная галочка" (✅ тест прошёл, ✅ высокий coverage, ✅ CI успешен) <strong>не гарантирует</strong> автоматически реальную корректность. В конце capstone вы научитесь не только тестировать, но и <strong>не доверять слепо самим тестам</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Ошибки в этом capstone скрыты не в коде, а часто в тестах или непроверенных случаях</li>
<li>✅ Запись политики TDD в README напоминает о ней по мере роста проекта</li>
<li>✅ Отдельная тестовая база должна планироваться с самого начала проекта - это предотвращает будущие flaky-тесты</li>
<li>✅ Система рейтинга/очков - богатый материал, полный нюансов для алгоритмов и тестирования</li>
<li>✅ В этом курсе "зелёная галочка" (тест прошёл, высокий coverage, успешный CI) не всегда означает реальную корректность</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 1: Планирование и скелет репозитория
# ════════════════════════════════════════════════════════════════════

# Этот урок посвящён скорее ПЛАНИРОВАНИЮ, чем написанию кода.
# Ниже - схема БД и скелет тестов для RankVault:

# ─────────────────────────────────────────────────────────────────────
# schema.sql (пока не настоящая миграция - будет на 3-м уроке)
# ─────────────────────────────────────────────────────────────────────

# CREATE TABLE users (
#   id SERIAL PRIMARY KEY,
#   username VARCHAR(50) UNIQUE NOT NULL,
#   created_at TIMESTAMP DEFAULT NOW()
# );
#
# CREATE TABLE scores (
#   id SERIAL PRIMARY KEY,
#   user_id INTEGER REFERENCES users(id),
#   points INTEGER NOT NULL,
#   submitted_at TIMESTAMP DEFAULT NOW()
# );

# ─────────────────────────────────────────────────────────────────────
# tests/conftest.py - скелет, дополняется на 3-м уроке
# ─────────────────────────────────────────────────────────────────────

import pytest


@pytest.fixture
def client():
    # На 3-м уроке: сюда добавится конфигурация, подключающаяся
    # к ОТДЕЛЬНОЙ тестовой базе (через TEST_DATABASE_URL).
    raise NotImplementedError("Дополняется на 3-м уроке")


# ─────────────────────────────────────────────────────────────────────
# Намеренная сложность - fixture, подключённая к production (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client():
#     app.config['DATABASE_URL'] = os.environ['DATABASE_URL']  # PRODUCTION!
#     return app.test_client()
# Пока выглядит безобидно, но когда тестов станет больше - будет flaky.
"""

EX = {
    4534: {
        "title": "Где скрыты ошибки в этом capstone?",
        "description": "Где обычно скрыты 'намеренные ошибки' в capstone-проекте RankVault?",
        "hint": "Этот capstone посвящён тестированию и алгоритмам.",
        "explanation": "В этом capstone ошибка чаще скрыта в самих тестах или в непроверенных состояниях алгоритма - код выглядит работающим, тесты кажутся зелёными, но важный случай никогда не был правильно протестирован.",
    },
    4535: {
        "title": "Почему нужна отдельная тестовая база?",
        "description": "Почему проблематично запускать тесты в той же базе, что используется в production/development?",
        "hint": "Могут ли тесты влиять на данные друг друга?",
        "explanation": "Если тесты работают в одной базе, данные одного теста могут повлиять на другой тест - это делает тесты 'flaky', то есть результат меняется в зависимости от порядка запуска.",
    },
    4536: {
        "title": "Расположите процесс планирования RankVault",
        "description": "Расположите правильный процесс планирования этапа 1 для RankVault.",
        "hint": "",
        "explanation": "",
    },
    4537: {
        "title": "Три этапа цикла TDD",
        "description": "Напишите три этапа цикла TDD (Test Driven Development) подряд, через запятую (например: X, Y, Z).",
        "hint": "Сначала неудачный тест, затем код, который его проходит, затем очистка.",
        "expected_answer": "RED, GREEN, REFACTOR",
    },
    4538: {
        "title": "Почему опасно откладывать настройку тестовой инфраструктуры?",
        "description": (
            "Если разработчик откладывает настройку отдельной тестовой "
            "базы, решив 'проект пока маленький, сделаю позже', к какой "
            "проблеме это может привести в дальнейшем? Объясните своими "
            "словами."
        ),
        "hint": "Почему это решение кажется безобидным, когда проект маленький?",
        "expected_answer": "Когда проект маленький и тестов мало, использование production/development базы кажется безобидным. Но по мере роста числа тестов, разные тесты, читая/записывая одни и те же данные в одной базе, начинают влиять друг на друга - в результате тесты могут давать разный результат в зависимости от ПОРЯДКА запуска (flaky-тесты). Исправление этой ситуации после того, как проект уже разросся, требует намного больше времени и переделки, чем построение отдельной тестовой базы и механизма отката транзакций с самого начала.",
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
        TASK_TITLE_RU = "RankVault — скелет репозитория и документ политики TDD"
        TASK_DESCRIPTION_RU = (
            "Создайте репозиторий на GitHub для проекта RankVault (с "
            "папками app/ и tests/), напишите полный README.md (с "
            "политикой TDD и схемой таблиц users/scores), и создайте "
            "скелет tests/conftest.py с установленными pytest + pytest-cov."
        )
        TASK_REQUIREMENTS_RU = (
            "• На GitHub создан публичный репозиторий с названием 'rankvault'\n"
            "• Есть папки app/ и tests/\n"
            "• README.md: описание проекта, политика TDD (RED-GREEN-REFACTOR), технологии, чеклист статуса\n"
            "• В README.md описаны таблицы users и scores и связь между ними\n"
            "• requirements.txt: добавлены flask, psycopg2-binary, pytest, pytest-cov\n"
            "• Есть скелет tests/conftest.py (пока с NotImplementedError)\n"
            "• Есть файл .gitignore (исключены venv, __pycache__, .env)"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, pytest-cov, PostgreSQL, Git, GitHub"
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
