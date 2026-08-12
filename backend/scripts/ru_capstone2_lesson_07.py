"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=6 (L7, CAPSTONE finale)."""
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

LESSON_ID = 756

TITLE_RU = "7-Полировка и Deploy (финал CAPSTONE)"

TEXT_RU = """\
<h2>Этап 7 (финал CAPSTONE): совместный деплой трёх частей</h2>

<pre class="mermaid">
flowchart TB
    DJANGO["Django backend"] -->|"Web Service"| RENDER["Render/Railway"]
    REACT["React frontend"] -->|статичная сборка| VERCEL["Vercel/Netlify"]
    BOT["telegram_bot/bot.py"] -->|"Background Worker!"| RENDER2["Render/Railway worker"]
    BOT -->|неверно как "Web Service"| CRASH["Ошибка health check, постоянный перезапуск"]
</pre>

<p>Все три части StudyMate готовы — теперь выведем их в <strong>настоящий интернет</strong>. Здесь есть важное отличие: Django и React работают по принципу "запрос-ответ", а <strong>бот должен работать постоянно</strong> — это требует другого "типа сервиса" на платформе деплоя.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — деплой трёх частей с правильным "типом сервиса"</h4>
<pre><code># На платформах вроде Render/Railway ОБЫЧНО есть два основных типа сервиса:
#
# 1. "Web Service" - отвечает на HTTP-запросы, слушает на $PORT
#    -> Django backend ПОДХОДИТ под этот тип (он ожидает запросы)
#
# 2. "Background Worker" - работает постоянно, не ждёт HTTP-запросов
#    -> telegram_bot/bot.py ИМЕННО ПОД ЭТОТ тип подходит! (он "опрашивает" Telegram на наличие сообщений)
#
# React же отдельно - деплоится как статичная сборка на Vercel/Netlify
# (сервер не нужен, только готовые файлы HTML/CSS/JS)</code></pre>

<h4>БЛОК 2 — переменные окружения (для всех трёх частей)</h4>
<pre><code># django_backend/.env.example
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
BOT_TOKEN=...                         # ❗ И бот, И send_reminders используют этот же токен
FRONTEND_URL=https://studymate.vercel.app

# telegram_bot/.env.example
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi   # ❗ ТОТ ЖЕ, что и в django_backend!
BOT_TOKEN=...
DJANGO_SETTINGS_MODULE=studymate.settings

# frontend/.env.production
REACT_APP_API_URL=https://studymate-api.onrender.com</code></pre>

<h4>БЛОК 3 — финальный README и чеклист проверки</h4>
<pre><code># README.md
# StudyMate

## Рабочие ссылки
- Frontend: https://studymate.vercel.app
- Backend API: https://studymate-api.onrender.com
- Telegram bot: @StudyMateBot

## Статус
- [x] Все 7 этапов завершены ✅

## Чеклист проверки (после деплоя)
- [ ] Регистрация и вход работают на веб-сайте
- [ ] Добавление/отметка выполнения задания работает на веб-сайте
- [ ] Telegram-аккаунт связывается через /link КОД
- [ ] Команда /topshiriqlar показывает данные с веб-сайта
- [ ] Автоматическое сообщение приходит для задания с близким сроком</code></pre>

<h3>🐛 Намеренная ошибка — деплой бота как "Web Service"</h3>
<pre><code># Разработчик настраивает telegram_bot/ как "Web Service", как Django:
# Платформа спрашивает: "На каком порту слушает бот?"
# Разработчик: не открывает никакой $PORT, так как бот не HTTP-сервер!

# В результате:
# ❌ Платформа считает "health check" неудачным и ПОСТОЯННО перезапускает
#    бота (так как он никогда не отвечает на $PORT)
# ❌ Бот иногда работает несколько секунд, затем платформа считает его
#    "мёртвым" и перезапускает - пользователи, пишущие боту, могут
#    не получать ответ в случайные моменты времени</code></pre>

<p><strong>Результат:</strong> <code>telegram_bot/bot.py</code> не ожидает HTTP-запросов — он <strong>сам запрашивает</strong> сообщения у серверов Telegram (polling) или принимает через webhook, но <strong>никогда</strong> не даёт обычный HTTP-ответ, которого ожидает проверка платформы "жив ли этот сервис". Если бот настроен как "Web Service", платформа постоянно считает его "не отвечающим" и регулярно <strong>перезапускает</strong> его — это нарушает стабильную работу бота. Правильное решение: разместить бота как <strong>"Background Worker"</strong> (или аналогичный тип сервиса, не ожидающий HTTP).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему три части требуют трёх разных способов деплоя?</h4>
<p>Django (запрос-ответ), React (статичные файлы) и бот (постоянно работающий процесс) &mdash; <strong>все три</strong> имеют принципиально разные модели работы. Если для каждой не выбран подходящий "тип сервиса", они либо вообще не работают, либо работают нестабильно.</p>

<h4>2. Почему бот и send_reminders используют один и тот же <code>BOT_TOKEN</code>?</h4>
<p>Оба отправляют/принимают сообщения, относящиеся к <strong>одному</strong> Telegram-боту &mdash; Telegram идентифицирует один бот одним токеном. Если бы они использовали разные токены, это были бы <strong>два разных</strong> бота.</p>

<h4>3. Почему бот и Django backend должны использовать ОДИН <code>DATABASE_URL</code> (снова)?</h4>
<p>Принцип, подчёркнутый с урока 1, действует и на этапе деплоя. Если развёрнутому боту дать другой (или неверный) <code>DATABASE_URL</code>, он <strong>не сможет видеть</strong> реальные данные пользователей в production, даже если всё "выглядит рабочим".</p>

<h4>4. В чём разница между "Web Service" и "Background Worker"?</h4>
<p>"Web Service" &mdash; сервис, ожидающий внешние HTTP-запросы, "слушающий" на <code>$PORT</code>. "Background Worker" &mdash; процесс, работающий <strong>непрерывно сам по себе</strong>, не ожидая никаких внешних запросов (например, постоянно опрашивающий Telegram на новые сообщения, или обрабатывающий очередь). Платформа управляет ими <strong>по-разному</strong>.</p>

<h4>5. Почему размещение бота с неверным типом сервиса создаёт впечатление "работает время от времени"?</h4>
<p>Бот иногда работает правильно <strong>до тех пор, пока</strong> платформа его не выключит и не перезапустит (так как код на самом деле верный, просто работает в "неверном контейнере"). Но когда платформа регулярно считает его "не отвечающим" и перезапускает, бот временно "отключается" &mdash; это делает сбой "случайным" на вид и усложняет поиск причины.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Django — "Web Service", React — статичная сборка, бот — "Background Worker"</li>
<li>✅ Бот и send_reminders обязаны использовать один и тот же <code>BOT_TOKEN</code> (относящийся к одному Telegram-боту)</li>
<li>✅ Бот и Django backend должны подключаться к ОДНОМУ <code>DATABASE_URL</code> и в production</li>
<li>✅ "Web Service" ожидает HTTP-запрос, "Background Worker" же работает непрерывно сам</li>
<li>✅ Размещение бота с неверным типом сервиса приводит к регулярным, "случайным" на вид перезапускам</li>
</ul>

<h3>🎉 Поздравляем!</h3>
<p>Вы построили StudyMate с пустого репозитория этапа 1 до схемы БД, Django API, React frontend, аутентификации, связки Telegram-бота, автоматических уведомлений и, наконец, <strong>настоящего деплоя из трёх частей</strong>. Это был опыт объединения знаний, полученных отдельно на курсах Django, React и Telegram Bot, в <strong>один реальный, многоинтерфейсный</strong> проект.</p>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 7 (ФИНАЛ CAPSTONE): Совместный деплой трёх частей
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Типы сервисов (в комментарии - понятие платформы деплоя, не код)
# ─────────────────────────────────────────────────────────────────────

# django_backend/  -> "Web Service" (ожидает HTTP-запрос, слушает на $PORT)
# frontend/         -> статичная сборка (Vercel/Netlify, сервер не нужен)
# telegram_bot/     -> "Background Worker" (работает постоянно, polling)

# ─────────────────────────────────────────────────────────────────────
# 2) Переменные окружения (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# django_backend/.env.example
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...
# FRONTEND_URL=https://studymate.vercel.app

# telegram_bot/.env.example
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...
# DJANGO_SETTINGS_MODULE=studymate.settings

# frontend/.env.production
# REACT_APP_API_URL=https://studymate-api.onrender.com

# ─────────────────────────────────────────────────────────────────────
# 3) telegram_bot/bot.py - правильный запуск (polling)
# ─────────────────────────────────────────────────────────────────────

import asyncio


async def main():
    # ... dp = Dispatcher(), обработчики ...
    # await dp.start_polling(bot)   # ❗ эта функция НИКОГДА не возвращается - работает постоянно
    pass


if __name__ == "__main__":
    asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - настройка бота как "Web Service" (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# Если платформа ожидает от бота HTTP-ответ на $PORT, но бот никогда
# его не даёт:
# ❌ Health check неудачен -> платформа регулярно перезапускает бота
"""

EX = {
    4384: {
        "title": "Правильный тип сервиса для Django backend",
        "description": "Какому типу сервиса на платформе деплоя соответствует Django backend?",
        "hint": "Django — сервер, отвечающий на HTTP-запросы.",
        "explanation": "Django backend соответствует типу \"Web Service\", ожидающему HTTP-запросы и слушающему на $PORT.",
    },
    4385: {
        "title": "Правильный тип сервиса для Telegram-бота",
        "description": "К какому типу сервиса должен быть размещён telegram_bot/bot.py при деплое?",
        "hint": "Бот \"опрашивает\" Telegram на сообщения, не ожидая HTTP-запрос.",
        "explanation": "Так как бот — процесс, работающий постоянно и опрашивающий Telegram на сообщения (не ожидая HTTP-запрос), он должен быть размещён как \"Background Worker\".",
    },
    4386: {
        "title": "Расположите процесс деплоя StudyMate",
        "description": "Расположите общий процесс деплоя трёхчастного проекта StudyMate.",
        "hint": "",
        "explanation": "",
    },
    4387: {
        "title": "Общая переменная окружения бота и send_reminders",
        "description": "Какую переменную окружения обязаны использовать с одинаковым значением и Telegram-бот, и команда send_reminders? (напишите название)",
        "hint": "",
        "expected_answer": "BOT_TOKEN",
    },
    4388: {
        "title": "Почему размещение бота как Web Service приводит к регулярным перезапускам?",
        "description": (
            "Если telegram_bot/ на платформе деплоя настроен как \"Web "
            "Service\" (а бот вообще не даёт HTTP-ответ ни на каком "
            "$PORT), почему платформа регулярно перезапускает бота? "
            "Объясните своими словами."
        ),
        "hint": "Как платформа проверяет \"живость\" сервисов типа \"Web Service\", и может ли бот ответить на эту проверку?",
        "expected_answer": "Сервисы типа \"Web Service\" контролируются платформой через регулярную проверку \"health check\" — эта проверка обычно ожидает, что сервис ответит по HTTP на назначенном $PORT. telegram_bot/bot.py же не является HTTP-сервером — это процесс, опрашивающий серверы Telegram на сообщения (polling), поэтому он никогда не даёт ожидаемый платформой HTTP-ответ. Платформа интерпретирует это \"отсутствие ответа\" как \"сервис мёртв\" или не работает и перезапускает его — хотя бот на самом деле работал правильно. Этот процесс повторяется регулярно, так как бот никогда не сможет дать ожидаемый платформой HTTP-ответ.",
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
        TASK_TITLE_RU = "StudyMate — финал CAPSTONE: развёрнутый проект из трёх частей"
        TASK_DESCRIPTION_RU = (
            "Разверните все три части StudyMate на реальном хостинге: Django "
            "backend (Web Service), React frontend (статичная сборка), "
            "Telegram-бот (Background Worker). Убедитесь, что бот и Django "
            "подключены к ОДНОЙ базе. Обновите README.md с рабочими ссылками "
            "и финальным чеклистом проверки."
        )
        TASK_REQUIREMENTS_RU = (
            "• Django backend работает на реальном хостинге как Web Service\n"
            "• React frontend работает на реальном хостинге как статичная сборка\n"
            "• Telegram-бот работает на реальном хостинге как Background Worker (не Web Service)\n"
            "• Бот и Django backend подключены к ОДНОЙ production-базе PostgreSQL\n"
            "• Регистрация, вход, добавление задания работают на веб-сайте\n"
            "• Команды /link и /topshiriqlar работают в реальном боте\n"
            "• README.md: рабочие ссылки (frontend, backend, бот), чеклист завершения 7/7 этапов, чеклист проверки\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (backend + frontend + бот), отдельное поле live_demo_url больше не обязательно"
        )
        TASK_TECHNOLOGIES_RU = "Render/Railway (Web Service + Background Worker), Vercel/Netlify, PostgreSQL"
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
