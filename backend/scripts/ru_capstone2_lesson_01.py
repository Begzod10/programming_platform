"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=0 (L1)."""
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

LESSON_ID = 744

TITLE_RU = "1-Планирование и repo skeleton"

TEXT_RU = """\
<h2>StudyMate — объединение трёх технологий за 7 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> API["2-Django API"]
    API --> FE["3-React frontend"]
    FE --> AUTH["4-Аутентификация"]
    AUTH --> BOT["5-Связка Telegram-бота"]
    BOT --> NOTIFY["6-Уведомления"]
    NOTIFY --> DEPLOY["7-Deploy"]
</pre>

<p>В первом capstone-курсе вы объединили React и Node.js/Express. На этот раз вы соедините <strong>три</strong> технологии — Django, React и Telegram Bot (aiogram) &mdash; в <strong>одном</strong> проекте: <strong>StudyMate</strong> &mdash; трекер учебных заданий для студентов. И через веб-страницу, и через Telegram-бота работа идёт с <strong>одной и той же</strong> базой данных.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — структура репозитория: три части, одна база</h4>
<pre><code># Для StudyMate используем monorepo - теперь ТРИ папки
studymate/
  django_backend/     # Django + PostgreSQL (строится в уроке 2)
    manage.py
    studymate/
  frontend/             # React (строится в уроке 3)
    package.json
    src/
  telegram_bot/         # aiogram-бот (строится в уроках 5-6)
    bot.py
    requirements.txt
  README.md
  .gitignore

# ❗ САМОЕ ВАЖНОЕ решение: telegram_bot/ НЕ создаёт СВОЮ отдельную базу -
# он подключается к ТОЙ ЖЕ базе PostgreSQL, что и django_backend/!</code></pre>

<h4>БЛОК 2 — схема БД: ОДНИ И ТЕ ЖЕ таблицы для бота и веба</h4>
<pre><code># Основные таблицы для StudyMate:
#
# users            (id, ism, email, parol_hash, telegram_chat_id NULLABLE,
#                    link_kodi NULLABLE, yaratilgan_vaqt)
# fanlar           (id, nomi, user_id -> users.id)
# topshiriqlar     (id, sarlavha, matn, muddat_vaqti, bajarilgan,
#                    fan_id -> fanlar.id, user_id -> users.id, yaratilgan_vaqt)
#
# ❗ telegram_chat_id - заполняется после того, как пользователь "связал"
#   свой Telegram-аккаунт с веб-аккаунтом (увидим в уроке 5)
# ❗ link_kodi - уникальный код, используемый временно в процессе связки

# Эта схема станет опорой одновременно для моделей Django (в уроке 2)
# И для кода aiogram-бота (в уроке 5) - ОБА читают/пишут эти же таблицы.</code></pre>

<h4>БЛОК 3 — README.md: статус трёх частей</h4>
<pre><code># README.md
# StudyMate

## О проекте
Трекер учебных заданий для студентов - Django + React + Telegram Bot,
с одной общей базой данных PostgreSQL.

## Технологии
- Backend: Django, PostgreSQL
- Frontend: React
- Bot: aiogram (Telegram)

## Статус
- [x] Планирование и repo skeleton
- [ ] Django backend API
- [ ] React frontend
- [ ] Аутентификация
- [ ] Telegram-бот: связка и команды
- [ ] Автоматические уведомления
- [ ] Deploy</code></pre>

<h3>🐛 Намеренная сложность: планирование отдельной базы для бота</h3>
<p>Многие начинающие разработчики, думая о Telegram-боте как об "отдельном маленьком проекте", планируют для него <strong>собственную</strong> базу SQLite:</p>
<pre><code># ❌ НЕВЕРНЫЙ план:
# telegram_bot/bot.py использует свой файл bot_data.db (SQLite)
# django_backend/ же использует отдельную базу PostgreSQL

# Проблема: если пользователь добавит задание на веб-сайте, эта информация
# окажется ТОЛЬКО в базе Django. Бот же читает свою SQLite-базу -
# он вообще "не видит" задания с веб-сайта!</code></pre>
<p><strong>Результат:</strong> если бот и веб-приложение подключены к <strong>разным</strong> базам, они <strong>не могут видеть данные друг друга</strong> &mdash; это разрушает саму цель всего проекта (работа с одними и теми же данными и через бота, и через веб). Правильное решение: создать <strong>одну</strong> базу PostgreSQL и дать <strong>боту, и Django</strong> одинаковые данные подключения (<code>DATABASE_URL</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему три папки (django_backend/frontend/telegram_bot) в одном репозитории?</h4>
<p>Это &mdash; продолжение принципа monorepo из первого capstone, теперь с третьей частью (ботом). Хранение кода всех трёх частей в одном месте облегчает отслеживание их взаимозависимости (особенно через общую базу).</p>

<h4>2. Почему бот и Django ДОЛЖНЫ подключаться к ОДНОЙ базе?</h4>
<p>Вся идея StudyMate &mdash; чтобы пользователь мог вводить данные через <strong>любой</strong> интерфейс (веб или Telegram), и они <strong>сразу</strong> отображались в другом интерфейсе. Это возможно только если оба подключены к <strong>одной</strong> реальной базе данных.</p>

<h4>3. Зачем нужны telegram_chat_id и link_kodi?</h4>
<p><code>telegram_chat_id</code> &mdash; для связи пользователя Django с его Telegram-аккаунтом. <code>link_kodi</code> же &mdash; уникальный код, временно используемый в процессе "связки", который рассмотрим в уроке 5 &mdash; пользователь получает код на веб-сайте, отправляет его боту, и таким образом два аккаунта связываются.</p>

<h4>4. Почему эта схема опора для ОБЕИХ кодовых баз (Django И бота)?</h4>
<p>Модели Django (в уроке 2) и код aiogram-бота (в уроке 5) <strong>оба</strong> обращаются именно к этим таблицам &mdash; один через Django ORM, другой напрямую через SQL или тоже через Django ORM внутри бота. Если схема неясна, между этими двумя отдельными кодовыми базами может возникнуть <strong>несоответствие</strong>.</p>

<h4>5. Почему этот проект объединяет три отдельных курса?</h4>
<p>Знания, полученные <strong>отдельно</strong> на курсах Django (backend + ORM), React (frontend) и Telegram Bot (aiogram), здесь объединяются для <strong>одной реальной цели</strong> (помочь студентам отслеживать задания) &mdash; это распространённая в реальных проектах архитектура "несколько интерфейсов, один backend".</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Monorepo из трёх частей: django_backend/, frontend/, telegram_bot/</li>
<li>✅ Бот и веб-приложение должны подключаться к <strong>одной, общей</strong> базе данных</li>
<li>✅ <code>telegram_chat_id</code> и <code>link_kodi</code> — для связи веб-аккаунта и Telegram-аккаунта</li>
<li>✅ Схема БД — единая опора и для Django, и для кода бота</li>
<li>✅ Этот курс объединяет три отдельные технологии в одной реальной архитектуре</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 1: Планирование и repo skeleton
# ════════════════════════════════════════════════════════════════════

# Этот урок посвящён ПЛАНИРОВАНИЮ, а не написанию кода.
# Ниже - "бумажное" представление схемы БД для StudyMate:

db_sxemasi = {
    "users": {
        "id": "SERIAL PRIMARY KEY",
        "ism": "VARCHAR(100)",
        "email": "VARCHAR(255) UNIQUE",
        "parol_hash": "VARCHAR(255)",
        "telegram_chat_id": "BIGINT NULL",   # NULL, если не связан
        "link_kodi": "VARCHAR(10) NULL",     # временный, для процесса связки
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
    "fanlar": {
        "id": "SERIAL PRIMARY KEY",
        "nomi": "VARCHAR(100)",
        "user_id": "INTEGER REFERENCES users(id)",
    },
    "topshiriqlar": {
        "id": "SERIAL PRIMARY KEY",
        "sarlavha": "VARCHAR(200)",
        "matn": "TEXT",
        "muddat_vaqti": "TIMESTAMP",
        "bajarilgan": "BOOLEAN DEFAULT false",
        "fan_id": "INTEGER REFERENCES fanlar(id)",
        "user_id": "INTEGER REFERENCES users(id)",
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
}

print(db_sxemasi)

# ─────────────────────────────────────────────────────────────────────
# Структура репозитория (в комментарии - структура папок/файлов, не код)
# ─────────────────────────────────────────────────────────────────────

# studymate/
#   django_backend/
#   frontend/
#   telegram_bot/
#   README.md
#   .gitignore

# ─────────────────────────────────────────────────────────────────────
# САМОЕ ВАЖНОЕ РЕШЕНИЕ (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# telegram_bot/ И django_backend/ подключаются к ОДНОМУ DATABASE_URL -
# у бота НЕТ своей отдельной базы!
"""

EX = {
    4324: {
        "title": "Почему три папки в одном репозитории (monorepo)?",
        "description": "Почему для StudyMate django_backend/, frontend/ и telegram_bot/ хранятся в одном репозитории?",
        "hint": "Это продолжение идеи monorepo из первого capstone.",
        "explanation": "Monorepo хранит код трёх частей в одном месте, облегчая отслеживание их взаимозависимости (особенно через общую базу данных).",
    },
    4325: {
        "title": "Почему бот и Django должны подключаться к одной базе?",
        "description": "Почему Telegram-бот и Django backend должны подключаться именно к одной, общей базе данных?",
        "hint": "Цель StudyMate - доступ к одним и тем же данным через два разных интерфейса.",
        "explanation": "Цель StudyMate — чтобы пользователь мог вводить данные через любой интерфейс и сразу видеть их в другом — это возможно только если оба подключены к одной реальной базе.",
    },
    4326: {
        "title": "Расположите процесс связки аккаунта",
        "description": "Расположите в логическом порядке процесс связки веб-аккаунта и Telegram-аккаунта через link_kodi (подробно рассмотрим в уроке 5).",
        "hint": "",
        "explanation": "",
    },
    4327: {
        "title": "Значение telegram_chat_id у несвязанного пользователя",
        "description": "Если пользователь ещё не связал свой Telegram-аккаунт, каким должно быть значение столбца telegram_chat_id в таблице users? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "NULL",
    },
    4328: {
        "title": "Почему планирование отдельной базы SQLite для бота — ошибка?",
        "description": (
            "Если разработчик спланирует для telegram_bot/ отдельный "
            "файл SQLite (например bot_data.db), а django_backend/ "
            "будет использовать отдельную базу PostgreSQL, к какой "
            "практической проблеме это приведёт? Объясните своими "
            "словами."
        ),
        "hint": "Могут ли две отдельные базы данных \"видеть\" записи друг друга?",
        "expected_answer": "Если бот и приложение Django подключены к двум отдельным базам данных, они вообще не могут видеть данные друг друга. Например, если пользователь добавит новое задание на веб-сайте, эта запись сохранится только в базе PostgreSQL Django. Telegram-бот же, читая свою отдельную базу SQLite, вообще не будет знать об этом новом задании и не сможет показать его пользователю. Это полностью разрушает главную цель StudyMate — возможность доступа к одним и тем же данным через любой интерфейс.",
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
        if lesson.task_title:
            section_map[lesson.task_title] = "StudyMate — repo skeleton и документ общей схемы БД"
        if lesson.task_description:
            section_map[lesson.task_description] = (
                "Создайте на GitHub monorepo для проекта StudyMate (с папками "
                "django_backend/, frontend/, telegram_bot/), напишите полноценный "
                "README.md и добавьте в README схему БД для таблиц "
                "users/fanlar/topshiriqlar. В схеме должны быть поля "
                "telegram_chat_id и link_kodi с объяснением, зачем они нужны."
            )
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
                "task_title": "StudyMate — repo skeleton и документ общей схемы БД",
                "task_description": (
                    "Создайте на GitHub monorepo для проекта StudyMate (с папками "
                    "django_backend/, frontend/, telegram_bot/), напишите полноценный "
                    "README.md и добавьте в README схему БД для таблиц "
                    "users/fanlar/topshiriqlar. В схеме должны быть поля "
                    "telegram_chat_id и link_kodi с объяснением, зачем они нужны."
                ),
                "task_requirements": (
                    "• На GitHub создан публичный репозиторий с именем 'studymate'\n"
                    "• Присутствуют папки django_backend/, frontend/, telegram_bot/\n"
                    "• README.md: описание проекта, технологии, чеклист статуса\n"
                    "• В README.md описаны таблицы users (с telegram_chat_id, link_kodi), "
                    "fanlar, topshiriqlar и связи между ними\n"
                    "• В README в 2-3 предложениях объяснено, почему бот должен "
                    "подключаться к ТОЙ ЖЕ базе, что и Django\n"
                    "• Присутствует файл .gitignore (node_modules, .env, __pycache__ исключены)"
                ),
                "task_technologies": "Git, GitHub, Markdown, PostgreSQL (проектирование схемы)",
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
