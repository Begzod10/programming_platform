"""Russian translation for Python: Testlash, lesson order=1 (L2)."""
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

LESSON_ID = 636

TITLE_RU = "2-Fixture и Mock"

TEXT_RU = """\
<h2>Fixture и Mock — подготовка и подмена в тестах</h2>

<pre class="mermaid">
flowchart LR
    FX["@pytest.fixture"] -->|даёт готовые данные| T["тестовая функция"]
    MOCK["mock/patch"] -->|заменяет реальный вызов| T
    T --> R["Быстрый, надёжный тест без внешних зависимостей"]
</pre>

<p>В уроке 1 мы тестировали простые функции. Но в реальных проектах тесты часто требуют одинаковой "подготовки" (например, тестовых данных) или зависят от внешних вещей (API, время, файловая система). <strong>Fixture</strong> — чтобы не повторять подготовку, <strong>mock</strong> — чтобы "подделать" внешнюю зависимость.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первый fixture</h4>
<pre><code>import pytest

@pytest.fixture
def foydalanuvchi():
    return {"ism": "Olim", "yosh": 22}

def test_foydalanuvchi_ismi(foydalanuvchi):  # ❗ имя fixture как параметр
    assert foydalanuvchi["ism"] == "Olim"

def test_foydalanuvchi_yoshi(foydalanuvchi):  # ❗ оба теста получают нового пользователя
    assert foydalanuvchi["yosh"] == 22</code></pre>

<p>pytest видит параметр с именем <code>foydalanuvchi</code> и автоматически вызывает fixture-функцию с таким же именем, передавая её результат в тест. Каждый тест получает <strong>свою собственную копию</strong>.</p>

<h4>БЛОК 2 — разделение fixture через conftest.py</h4>
<pre><code># conftest.py — общие fixture для ВСЕХ тестовых файлов в этой папке
import pytest

@pytest.fixture
def db_ulanish():
    print("DB ulanish ochildi")
    yield "fake_connection"  # ❗ часть до yield — setup
    print("DB ulanish yopildi")  # ❗ часть после yield — teardown</code></pre>

<pre><code># test_users.py — fixture из conftest.py доступен автоматически
def test_foydalanuvchi_saqlash(db_ulanish):
    assert db_ulanish == "fake_connection"</code></pre>

<h4>БЛОК 3 — замена внешнего вызова через mock</h4>
<pre><code># ob_havo.py
import requests

def hozirgi_harorat(shahar):
    javob = requests.get(f"https://api.masalan.uz/weather?city={shahar}")
    return javob.json()["harorat"]</code></pre>

<pre><code># test_ob_havo.py
from unittest.mock import patch
from ob_havo import hozirgi_harorat

@patch("ob_havo.requests.get")  # ❗ патчится место, где ИСПОЛЬЗУЕТСЯ в модуле ob_havo
def test_hozirgi_harorat(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    natija = hozirgi_harorat("Toshkent")
    assert natija == 25
    # ❗ Реального запроса в интернет вообще не было!</code></pre>

<h3>🐛 Намеренная ошибка — patch в неправильном месте</h3>
<pre><code># ❌ Патч самой библиотеки requests — НЕ РАБОТАЕТ как ожидается
@patch("requests.get")  # ❌ неверный адрес!
def test_hozirgi_harorat_xato(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    natija = hozirgi_harorat("Toshkent")
    # ❗ Этот тест иногда работает, а иногда отправляет реальный запрос в интернет —
    # потому что внутри ob_havo.py "requests" уже импортирован,
    # и его копия там НЕ была подменена!</code></pre>

<p><strong>Результат:</strong> <code>@patch("requests.get")</code> заменяет <strong>саму</strong> библиотеку <code>requests</code> на глобальном уровне, но файл <code>ob_havo.py</code> уже выполнил <code>import requests</code> и создал свою собственную ссылку (reference). Патч изменяет не <code>ob_havo.requests.get</code>, а другое место, поэтому функция <code>hozirgi_harorat()</code> всё ещё может пытаться вызвать <strong>реальный</strong> <code>requests.get</code>. Правило: <strong>патчится то место, ГДЕ используется</strong> объект, а не там, где он объявлен.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен fixture?</h4>
<p>Многие тесты требуют одинакового "начального состояния" (например, тестового пользователя, подключения к DB). Fixture позволяет описать эту подготовку в одном месте и "внедрить" её в любую тестовую функцию как параметр — код не дублируется.</p>

<h4>2. yield — объединение setup и teardown в одном fixture</h4>
<p>Код до <code>yield</code> — это <strong>setup</strong> (подготовка), код после <code>yield</code> — это <strong>teardown</strong> (очистка). После завершения теста pytest автоматически выполняет часть после <code>yield</code> — для корректного закрытия ресурсов.</p>

<h4>3. Почему conftest.py отдельный?</h4>
<p>Fixture из <code>conftest.py</code> становятся доступны <strong>без импорта</strong> во всех тестовых файлах той же папки (и её подпапок). Это стандартный способ разделения fixture по всему проекту.</p>

<h4>4. Что такое mock и зачем он нужен?</h4>
<p>Mock — это подстановка "поддельной" версии вместо реальной функции/объекта. Это делает тесты <strong>быстрыми</strong> (не обращаются в интернет), <strong>надёжными</strong> (тест проходит, даже если сеть не работает) и <strong>предсказуемыми</strong> (всегда одинаковый результат).</p>

<h4>5. Правильный выбор места для patch</h4>
<p>Самая частая ошибка — указать в <code>@patch</code> "исходный" адрес библиотеки. Правильный подход: патчить нужно там, <strong>где патчимый объект вызывается</strong>, указывая имя именно того модуля (<code>@patch("ob_havo.requests.get")</code>, а не <code>@patch("requests.get")</code>).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>@pytest.fixture</code> создаёт переиспользуемую подготовку для тестов</li>
<li>✅ <code>conftest.py</code> автоматически делится fixture по всей папке</li>
<li>✅ <code>yield</code> позволяет описать setup и teardown в одном месте</li>
<li>✅ <code>@patch</code> заменяет внешние вызовы (API, DB) поддельной версией</li>
<li>✅ Патч ставится <strong>там, где объект используется</strong>, а не там, где объявлен — это самая частая ошибка mock</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 2: Fixture и Mock
# ════════════════════════════════════════════════════════════════════

import pytest
from unittest.mock import patch

# ─────────────────────────────────────────────────────────────────────
# 1) Простой fixture
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def foydalanuvchi():
    return {"ism": "Olim", "yosh": 22}


def test_foydalanuvchi_ismi(foydalanuvchi):
    assert foydalanuvchi["ism"] == "Olim"


def test_foydalanuvchi_yoshi(foydalanuvchi):
    assert foydalanuvchi["yosh"] == 22


# ─────────────────────────────────────────────────────────────────────
# 2) setup/teardown через yield
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def db_ulanish():
    print("DB ulanish ochildi")
    yield "fake_connection"
    print("DB ulanish yopildi")


def test_foydalanuvchi_saqlash(db_ulanish):
    assert db_ulanish == "fake_connection"


# ─────────────────────────────────────────────────────────────────────
# 3) parametrize — запуск одного теста с несколькими значениями
# ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("son,kutilgan", [
    (2, 4),
    (3, 9),
    (5, 25),
])
def test_kvadrat(son, kutilgan):
    assert son ** 2 == kutilgan


# ─────────────────────────────────────────────────────────────────────
# 4) Замена внешнего вызова через mock — ПРАВИЛЬНЫЙ способ
# ─────────────────────────────────────────────────────────────────────

# ob_havo.py:
# import requests
# def hozirgi_harorat(shahar):
#     javob = requests.get(f"https://api.masalan.uz/weather?city={shahar}")
#     return javob.json()["harorat"]

@patch("ob_havo.requests.get")  # ✅ место использования в модуле ob_havo
def test_hozirgi_harorat(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    # natija = hozirgi_harorat("Toshkent")
    # assert natija == 25


# ─────────────────────────────────────────────────────────────────────
# 5) Намеренная ошибка — patch в неверном месте (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @patch("requests.get")  # ❌ неверно — у ob_havo.py своя копия
# def test_hozirgi_harorat_xato(mock_get):
#     mock_get.return_value.json.return_value = {"harorat": 25}
#     # Иногда может отправить реальный запрос в интернет!
"""

EX = {
    3759: {
        "title": "Для чего используется fixture?",
        "description": "Для чего в основном используется @pytest.fixture в pytest?",
        "hint": "Fixture — способ описать в одном месте подготовку, нужную нескольким тестам.",
        "explanation": "Fixture позволяет описать общую подготовку для тестов (например тестовые данные, подключение к DB) в одном месте и передавать её в любую тестовую функцию как параметр.",
    },
    3760: {
        "title": "Какую роль играет код после yield в fixture?",
        "description": "Для чего обычно используется код, написанный ПОСЛЕ строки yield внутри fixture?",
        "hint": "До yield — подготовка, после — очистка.",
        "explanation": "Код до yield считается setup, код после — teardown. После завершения теста pytest автоматически выполняет часть после yield.",
    },
    3761: {
        "title": "Расположите поток применения mock в правильном порядке",
        "description": "Упорядочите процесс тестирования вызова requests.get() через mock.",
        "hint": "Сначала устанавливается patch, затем настраивается ответ mock, затем вызывается и проверяется функция.",
    },
    3762: {
        "title": "Почему @patch(\"requests.get\") может не сработать как ожидается?",
        "description": (
            "Файл ob_havo.py делает 'import requests' и вызывает "
            "requests.get(). Если тест патчит @patch(\"requests.get\") (саму "
            "библиотеку), почему это иногда не срабатывает и уходит "
            "реальный запрос в интернет? Каково правильное решение? "
            "Объясните своими словами."
        ),
        "expected_answer": "Когда файл ob_havo.py делает 'import requests', в пространстве имён модуля ob_havo создаётся ссылка на сам модуль requests. @patch(\"requests.get\") заменяет только ГЛОБАЛЬНУЮ копию библиотеки requests, но ob_havo.py вызывает requests.get через свою собственную внутреннюю ссылку — эта ссылка может остаться неподменённой. Правильное решение — патчить там, ГДЕ используется патчимый объект, указывая имя именно этого модуля: @patch(\"ob_havo.requests.get\"), а не @patch(\"requests.get\").",
        "hint": "После импорта, через имя какого модуля функция выполняет вызов?",
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
