"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=6 (L7)."""
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

LESSON_ID = 770

TITLE_RU = "7-Финальная полировка и деплой (завершение CAPSTONE)"

TEXT_RU = """\
<h2>Этап 7 (завершение CAPSTONE): деплой и ошибка относительного пути</h2>

<pre class="mermaid">
flowchart TB
    FLASK["Flask (API + frontend, В ОДНОМ месте)"] -->|"Web Service"| RENDER["Render/Railway"]
    BOT["bot/bot.py"] -->|"Background Worker!"| RENDER2["Render/Railway worker"]
    FLASK -. "один и тот же DATABASE_URL" .-> DB[("PostgreSQL")]
    BOT -. "один и тот же DATABASE_URL" .-> DB
</pre>

<p>MoneyLog отличается от двух других capstone-проектов &mdash; на этапе 1 вы выбрали не хостить frontend отдельно (Flask сам его обслуживает). Поэтому здесь всего <strong>две</strong> единицы деплоя: Flask (API + frontend, ОДИН "Web Service") и бот (отдельный "Background Worker"). Но именно это решение "один Flask отдаёт всё" может привести к новому, специфичному для production типу ошибки: <strong>ошибке относительного пути (relative path)</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — правильная раздача статики через абсолютный путь</h4>
<pre><code># app.py
import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # ❗ вычисляется ОТСЮДА, где реально находится app.py
FRONTEND_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)</code></pre>

<h4>БЛОК 2 — деплой с двумя типами сервисов</h4>
<pre><code># На платформах вроде Render/Railway:
#
# moneylog-web  -> "Web Service" (Flask: API + frontend, ОДИН процесс, слушает $PORT)
# moneylog-bot  -> "Background Worker" (bot/bot.py: работает постоянно, polling)
#
# ОБА должны подключаться к одному и тому же DATABASE_URL (принцип с 5-го урока)</code></pre>

<h4>БЛОК 3 — финальный README и чеклист проверки</h4>
<pre><code># README.md
# MoneyLog

## Живые ссылки
- Web + API: https://moneylog.onrender.com
- Telegram bot: @MoneyLogBot

## Статус
- [x] Все 7 этапов завершены ✅

## Чеклист проверки (после деплоя)
- [ ] Главная страница (index.html) и style.css/app.js загружаются ПРАВИЛЬНО (не 404)
- [ ] Регистрация/вход работают
- [ ] Добавление расхода на сайте работает
- [ ] Добавление расхода через Telegram-бот текстом работает
- [ ] В конце месяца приходит предупреждение о бюджете</code></pre>

<h3>🐛 Намеренная ошибка — простой относительный путь для статической папки</h3>
<pre><code># app.py
FRONTEND_DIR = "static"          # ❌ вычисляется относительно текущей рабочей папки (cwd)!

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

# Локально работает, потому что вы всегда запускаете
#   cd moneylog/backend && python app.py
# именно из папки, где находится app.py - поэтому cwd и место
# расположения app.py СЛУЧАЙНО совпадают.
#
# На production-сервере же gunicorn/systemd часто запускается из
# СОВСЕМ ДРУГОЙ "рабочей директории" (например, из корня репозитория):
#   WorkingDirectory=/srv/moneylog
#   ExecStart=gunicorn backend.app:app
#
# Теперь cwd = /srv/moneylog, а папка "static" на самом деле
# находится в /srv/moneylog/backend/static!</code></pre>

<p><strong>Результат:</strong> строка <code>"static"</code> внутри <code>send_from_directory("static", ...)</code> &mdash; это <strong>относительный путь</strong>, который вычисляется не относительно расположения <code>app.py</code>, а относительно того, <strong>из какой папки был запущен процесс (working directory)</strong>. При локальной разработке вы обычно запускаете команду прямо из самого проекта, поэтому эти два места <strong>случайно</strong> совпадают, и ошибка остаётся незамеченной. На production-сервере же процесс деплоя (gunicorn, systemd, Docker) часто запускается из <strong>совсем другой</strong> папки &mdash; в результате <code>"static"</code> указывает не туда, и все CSS/JS файлы получают <code>404 Not Found</code>, хотя JSON-эндпоинты вроде <code>/api/...</code> продолжают работать как обычно (они не зависят от файловой системы). Правильное решение &mdash; всегда вычислять путь <strong>абсолютно</strong>, на основе <code>os.path.dirname(os.path.abspath(__file__))</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему в MoneyLog всего ДВЕ единицы деплоя (в React-capstone'ах было три)?</h4>
<p>Из-за архитектурного решения, принятого на этапе 1: поскольку vanilla JS не требует шага сборки, Flask может отдавать его <strong>сам</strong> как статические файлы. Поэтому API и frontend объединяются в <strong>одном</strong> процессе ("Web Service") &mdash; отдельным остаётся только бот ("Background Worker").</p>

<h4>2. В чём разница между относительным (relative) и абсолютным (absolute) путём?</h4>
<p>Относительный путь (например <code>"static"</code>) вычисляется относительно <strong>текущей рабочей папки</strong> процесса (working directory, cwd) &mdash; а она <strong>может меняться</strong> в зависимости от того, как запущена программа. Абсолютный путь (построенный через <code>os.path.dirname(os.path.abspath(__file__))</code>) всегда вычисляется от реального расположения файла <code>app.py</code> &mdash; и <strong>не меняется</strong>, независимо от того, откуда программа запущена.</p>

<h4>3. Почему эта ошибка совершенно не заметна локально?</h4>
<p>Потому что во время разработки вы почти всегда запускаете команду вроде <code>cd moneylog/backend && python app.py</code> прямо из самого проекта &mdash; поэтому cwd и реальное расположение файла <strong>случайно</strong> совпадают. Ошибка проявляется только в production, когда процесс деплоя выбирает другую рабочую директорию.</p>

<h4>4. Почему при этом ломается только frontend, а API продолжает работать?</h4>
<p>Эндпоинты вроде <code>/api/expenses</code> работают с базой данных и не зависят от относительного пути в файловой системе. Только вызов <code>send_from_directory()</code> читает статический файл из файловой системы &mdash; поэтому именно эта, и только эта, часть возвращает 404 из-за неверного пути.</p>

<h4>5. Почему бот и Flask всё равно нуждаются в ОДНОМ И ТОМ ЖЕ <code>DATABASE_URL</code> (снова)?</h4>
<p>Принцип, заложенный ещё на 5-м уроке, действует и на этапе деплоя: оба должны работать с <strong>одними и теми же</strong> пользователями и расходами в одной production-базе данных, иначе расход, добавленный на сайте, не будет виден в боте (и наоборот).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ В Vanilla JS + Flask frontend и API можно деплоить как единый "Web Service"</li>
<li>✅ Бот всё равно должен деплоиться отдельно, как "Background Worker"</li>
<li>✅ Относительный путь (например <code>"static"</code>) зависит от рабочей папки процесса, абсолютный &mdash; нет</li>
<li>✅ <code>os.path.dirname(os.path.abspath(__file__))</code> &mdash; способ всегда строить абсолютные пути к статике/шаблонам</li>
<li>✅ Неверный относительный путь обычно не заметен локально и проявляется только как 404 при production-деплое</li>
</ul>

<h3>🎉 Поздравляем!</h3>
<p>Вы построили MoneyLog с нуля &mdash; с пустого репозитория на этапе 1, через схему базы данных, Flask API, vanilla JS frontend, аутентификацию, быстрое добавление расходов через Telegram-бота, автоматическое ежемесячное предупреждение о бюджете, и, наконец, до <strong>правильного, состоящего из двух частей production-деплоя</strong>. Это был опыт объединения знаний, полученных отдельно на курсах Flask и Telegram Bot, вместе с vanilla JavaScript без шага сборки, в <strong>одном реальном проекте</strong>.</p>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 7 (ЗАВЕРШЕНИЕ CAPSTONE): Деплой и ошибка относительного пути
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app.py - правильная раздача статики через абсолютный путь
# ─────────────────────────────────────────────────────────────────────

import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ─────────────────────────────────────────────────────────────────────
# 2) Типы сервисов и переменные окружения (в комментарии - концепция деплоя, не код)
# ─────────────────────────────────────────────────────────────────────

# moneylog-web  -> "Web Service" (Flask: API + frontend, один процесс)
# moneylog-bot  -> "Background Worker" (bot/bot.py: работает постоянно)
#
# .env (одинаковый в ОБОИХ):
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - простой относительный путь (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# FRONTEND_DIR = "static"          # ❌ относительно текущей рабочей папки (cwd)!
#
# @app.route("/")
# def index():
#     return send_from_directory(FRONTEND_DIR, "index.html")
#
# Локально работает (cwd == папка app.py), а на production gunicorn/
# systemd может запускаться из другой рабочей директории - 404!
"""

EX = {
    4454: {
        "title": "Сколько единиц деплоя в MoneyLog?",
        "description": "Из-за архитектурного решения, принятого на этапе 1, сколько отдельных единиц деплоя (сервисов) имеет MoneyLog в production?",
        "hint": "Vanilla JS не требует шага сборки - поэтому Flask может отдавать его сам.",
        "explanation": "Поскольку на этапе 1 было решено, что Flask сам отдаёт frontend как статические файлы, API и frontend объединяются в ОДНОМ \"Web Service\"; отдельным остаётся только бот, как \"Background Worker\" - итого две единицы деплоя.",
    },
    4455: {
        "title": "Разница между относительным и абсолютным путём",
        "description": "Относительно чего вычисляется относительный путь вроде send_from_directory(\"static\", ...)?",
        "hint": "cwd - это ОТКУДА запущена программа, а не ГДЕ она расположена.",
        "explanation": "Относительный путь вычисляется относительно текущей рабочей папки процесса (cwd) - а она может меняться в зависимости от того, как и откуда запущена программа, поэтому это ненадёжно.",
    },
    4456: {
        "title": "Расположите процесс деплоя MoneyLog",
        "description": "Расположите общий процесс деплоя MoneyLog в production.",
        "hint": "",
        "explanation": "",
    },
    4457: {
        "title": "Способ построения абсолютного пути из относительного",
        "description": "Какая комбинация функций используется для того, чтобы всегда правильно вычислять путь к статической/шаблонной папке независимо от расположения app.py? (напишите название, например: os.path.xxx(os.path.xxx(__file__)))",
        "hint": "Две функции os.path используются последовательно, одна внутри другой.",
        "expected_answer": "os.path.dirname(os.path.abspath(__file__))",
    },
    4458: {
        "title": "Почему ошибка относительного пути не заметна локально и проявляется только в production?",
        "description": (
            "Относительный путь вроде FRONTEND_DIR = \"static\" обычно "
            "работает без проблем при локальной разработке, но приводит "
            "к ошибке 404 при деплое на production-сервер. Почему "
            "возникает эта разница? Объясните своими словами."
        ),
        "hint": "Откуда ВЫ запускаете программу локально? Кто и откуда запускает её на production-сервере?",
        "expected_answer": "При локальной разработке разработчик почти всегда запускает команду 'python app.py' или 'flask run' именно из той папки, где находится файл app.py - поэтому текущая рабочая папка процесса (cwd) и реальное расположение app.py СЛУЧАЙНО совпадают, и относительный путь вроде 'static' работает правильно. На production-сервере же средство деплоя (gunicorn, systemd, Docker) часто запускается из совсем другой рабочей директории (например, из корня репозитория) - теперь cwd и расположение app.py уже НЕ совпадают, поэтому 'static' указывает не туда, и все файлы CSS/JS возвращают ошибку 404.",
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
        TASK_TITLE_RU = "MoneyLog — завершение CAPSTONE: полностью задеплоенный проект"
        TASK_DESCRIPTION_RU = (
            "Задеплойте MoneyLog на реальный хостинг: Flask (API + "
            "frontend, единый Web Service) и Telegram-бот (Background "
            "Worker). Убедитесь, что оба подключены к ОДНОЙ И ТОЙ ЖЕ "
            "production-базе данных, и что пути к статическим файлам "
            "абсолютные. Обновите README.md с живой ссылкой и финальным "
            "чеклистом проверки."
        )
        TASK_REQUIREMENTS_RU = (
            "• Flask (API + frontend) работает на реальном хостинге как Web Service\n"
            "• Пути к статическим файлам построены абсолютно, на основе os.path.dirname(os.path.abspath(__file__))\n"
            "• Главная страница и все CSS/JS файлы загружаются ПРАВИЛЬНО в production (не 404)\n"
            "• Telegram-бот работает на реальном хостинге как Background Worker (не Web Service)\n"
            "• Бот и Flask подключены к ОДНОЙ И ТОЙ ЖЕ production-базе PostgreSQL\n"
            "• Работает и добавление расхода на сайте, и добавление расхода через Telegram-бот текстом\n"
            "• README.md: живая ссылка, чеклист завершения 7/7 этапов, список проверки\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (Flask + бот), отдельное поле live_demo_url больше не обязательно"
        )
        TASK_TECHNOLOGIES_RU = "Render/Railway (Web Service + Background Worker), PostgreSQL, os.path"
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
