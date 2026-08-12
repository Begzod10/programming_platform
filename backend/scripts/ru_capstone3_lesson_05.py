"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=4 (L5)."""
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

LESSON_ID = 766

TITLE_RU = "5-Telegram-бот: быстрый расход и связка аккаунта"

TEXT_RU = """\
<h2>Этап 5: Telegram-бот — быстрый расход и связка аккаунта</h2>

<pre class="mermaid">
flowchart LR
    BOTFILE["telegram_bot/bot.py"] -->|app.app_context()| CTX["Подключение к Flask-SQLAlchemy готово"]
    CTX --> MODELS["from app.models import ..."]
    MSG["Пользователь пишет боту: '50000 ovqat'"] --> PARSE["Текст анализируется"]
    PARSE --> SAVE["Создаётся Expense - для ЭТОГО пользователя"]
</pre>

<p>Самая удобная функция MoneyLog именно здесь: пользователь, не заходя на веб-сайт, может <strong>быстро</strong> добавить расход, просто написав в Telegram <strong>"50000 ovqat"</strong>. Бот подключается к <strong>той же самой</strong> базе Flask-SQLAlchemy.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — подключение контекста приложения Flask к боту</h4>
<pre><code># telegram_bot/bot.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'flask_backend'))

from app import create_app, db                # ❗ Application Factory Flask (из этапа 2)
from app.models import User, Category, Expense

app = create_app()                              # ❗ создаёт объект приложения Flask (сервер не запускается!)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()</code></pre>

<h4>БЛОК 2 — команда /link: отправка запроса ВНУТРИ app_context()</h4>
<pre><code>@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    with app.app_context():                      # ❗ ОБЯЗАТЕЛЬНО - запросы Flask-SQLAlchemy ВНУТРИ этого блока
        user = User.query.filter_by(link_kodi=kod).first()
        if user is None:
            await message.answer("Kod noto'g'ri yoki eskirgan")
            return

        user.telegram_chat_id = message.chat.id
        user.link_kodi = None
        db.session.commit()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.ism}!")</code></pre>

<h4>БЛОК 3 — быстрое добавление расхода через текст</h4>
<pre><code>@dp.message()                                    # ❗ для ЛЮБОГО текста, не начинающегося с /команды
async def tezkor_xarajat_handler(message: types.Message):
    qismlar = message.text.split(maxsplit=1)      # ❗ "50000 ovqat" -> ["50000", "ovqat"]
    if len(qismlar) != 2 or not qismlar[0].isdigit():
        await message.answer("Format: SUMMA TAVSIF (masalan: 50000 ovqat)")
        return

    summa, tavsif = qismlar

    with app.app_context():
        user = User.query.filter_by(telegram_chat_id=message.chat.id).first()
        if user is None:
            await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
            return

        category = Category.query.filter_by(user_id=user.id, nomi=tavsif).first()
        if category is None:
            category = Category(nomi=tavsif, user_id=user.id)
            db.session.add(category)
            db.session.flush()

        xarajat = Expense(
            summa=summa, tavsif=tavsif, sana=date.today(),
            category_id=category.id, user_id=user.id,
        )
        db.session.add(xarajat)
        db.session.commit()

    await message.answer(f"✅ {summa} so'm '{tavsif}' uchun yozildi")</code></pre>

<h3>🐛 Намеренная ошибка — отправка запроса Flask-SQLAlchemy без app_context()</h3>
<pre><code>@dp.message(Command("link"))
async def link_handler_xato(message: types.Message):
    kod = message.text.split()[1]
    user = User.query.filter_by(link_kodi=kod).first()   # ❌ НЕТ app.app_context()!
    # ...

# Когда бот запущен и пользователь отправляет /link:
# ❌ RuntimeError: Working outside of application context.
#    This typically means that you attempted to use functionality that
#    needed the current application.</code></pre>

<p><strong>Результат:</strong> чтобы запросы Flask-SQLAlchemy вроде <code>User.query</code> работали, Flask должен <strong>знать</strong>, "в каком контексте приложения" он находится &mdash; обычно это <strong>автоматически</strong> обеспечивается при каждом HTTP-запросе (Flask сам это управляет). Бот же не работает в рамках HTTP-запроса &mdash; он, подобно <code>django.setup()</code> из курса Django capstone, должен <strong>вручную</strong> "открыть" контекст приложения через <code>with app.app_context():</code>. Если этого не сделать, Flask-SQLAlchemy "не знает", к какой базе (какой конфигурации) обращаться, и выдаёт <code>RuntimeError</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему боту нужен контекст приложения Flask?</h4>
<p>Flask-SQLAlchemy хранит данные о подключении к базе, конфигурации внутри объекта приложения Flask (<code>app</code>). Обычно к этим данным обращаются только внутри HTTP-запроса (когда Flask автоматически устанавливает "контекст"). Бот же — не HTTP-запрос, поэтому должен создать этот контекст <strong>вручную</strong>.</p>

<h4>2. Чем <code>app.app_context()</code> похож на <code>django.setup()</code> из Django?</h4>
<p>Оба решают <strong>одну и ту же проблему</strong>: использование ORM (Django ORM или Flask-SQLAlchemy) <strong>вне</strong> веб-сервера. Разница: <code>django.setup()</code> вызывается один раз, в начале программы; <code>app.app_context()</code> же открывается отдельно, как блок <code>with</code>, <strong>в каждом</strong> месте, где нужно обратиться к базе данных.</p>

<h4>3. Зачем используется <code>@dp.message()</code> (без фильтра)?</h4>
<p>В aiogram <code>@dp.message()</code> без фильтра перехватывает <strong>все</strong> текстовые сообщения, не соответствующие <strong>никакой команде</strong> (например не <code>/link</code>, не <code>/start</code>). Это позволяет написать обработчик, срабатывающий, когда пользователь просто пишет "50000 ovqat".</p>

<h4>4. Почему новая category создаётся автоматически (если её нет)?</h4>
<p>Когда пользователь быстро пишет боту, он мог заранее не создать category. Код применяет логику "если category с этим именем не существует, создать её автоматически" &mdash; это упрощает пользовательский опыт, хотя и отличается от официального процесса создания category на веб-сайте.</p>

<h4>5. Почему без <code>app_context()</code> возникает <code>RuntimeError</code>?</h4>
<p>Запросы Flask-SQLAlchemy вроде <code>User.query</code> внутренне "запрашивают" конфигурацию (например <code>DATABASE_URL</code>) и подключение из текущего контекста приложения Flask. Если контекст <strong>не открыт</strong> (бот работает не в рамках HTTP-запроса), Flask-SQLAlchemy "не знает, откуда взять" эту информацию, и выбрасывает <code>RuntimeError</code> с сообщением "вы используете это вне контекста приложения".</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>app.app_context()</code> ОБЯЗАТЕЛЕН для использования Flask-SQLAlchemy вне веб-сервера (например в боте)</li>
<li>✅ Это похоже на <code>django.setup()</code> из Django, но используется как блок <code>with</code> вокруг каждого обращения к БД</li>
<li>✅ <code>@dp.message()</code> (без фильтра) перехватывает свободный текст, не являющийся командой</li>
<li>✅ Так как бот и Flask backend подключены к ОДНОЙ базе данных, запись, созданная в боте, сразу видна и на веб-сайте</li>
<li>✅ Запрос Flask-SQLAlchemy без <code>app_context()</code> даёт <code>RuntimeError: Working outside of application context</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 5: Telegram-бот - быстрый расход и связка аккаунта
# ════════════════════════════════════════════════════════════════════

import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'flask_backend'))

from app import create_app, db
from app.models import User, Category, Expense

app = create_app()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()


@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    with app.app_context():
        user = User.query.filter_by(link_kodi=kod).first()
        if user is None:
            await message.answer("Kod noto'g'ri yoki eskirgan")
            return

        user.telegram_chat_id = message.chat.id
        user.link_kodi = None
        db.session.commit()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.ism}!")


@dp.message()
async def tezkor_xarajat_handler(message: types.Message):
    qismlar = message.text.split(maxsplit=1)
    if len(qismlar) != 2 or not qismlar[0].isdigit():
        await message.answer("Format: SUMMA TAVSIF (masalan: 50000 ovqat)")
        return

    summa, tavsif = qismlar

    with app.app_context():
        user = User.query.filter_by(telegram_chat_id=message.chat.id).first()
        if user is None:
            await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
            return

        category = Category.query.filter_by(user_id=user.id, nomi=tavsif).first()
        if category is None:
            category = Category(nomi=tavsif, user_id=user.id)
            db.session.add(category)
            db.session.flush()

        xarajat = Expense(
            summa=summa, tavsif=tavsif, sana=date.today(),
            category_id=category.id, user_id=user.id,
        )
        db.session.add(xarajat)
        db.session.commit()

    await message.answer(f"✅ {summa} so'm '{tavsif}' uchun yozildi")

# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка - запрос без app_context() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @dp.message(Command("link"))
# async def link_handler_xato(message: types.Message):
#     kod = message.text.split()[1]
#     user = User.query.filter_by(link_kodi=kod).first()   # НЕТ app_context()!
# ❌ RuntimeError: Working outside of application context.
"""

EX = {
    4434: {
        "title": "Зачем боту нужен app.app_context()?",
        "description": "Зачем в скрипте Telegram-бота перед использованием запроса Flask-SQLAlchemy нужен app.app_context()?",
        "hint": "Бот сталкивается с проблемой, похожей на django.setup() из курса Django capstone.",
        "explanation": "Flask-SQLAlchemy обычно используется только внутри HTTP-запроса (когда Flask автоматически устанавливает контекст). Бот не является HTTP-запросом, поэтому этот контекст нужно создать вручную через app.app_context().",
    },
    4435: {
        "title": "Сходство app.app_context() и django.setup()",
        "description": "Чем app.app_context() похож на django.setup() из курса Django capstone?",
        "hint": "Оба решают одну и ту же проблему — использование ORM вне сервера.",
        "explanation": "Оба решают проблему использования ORM вне веб-сервера, но django.setup() вызывается один раз, а app.app_context() открывается отдельно как блок with для каждого обращения к БД.",
    },
    4436: {
        "title": "Расположите процесс добавления быстрого расхода",
        "description": "Расположите процесс, происходящий, когда пользователь пишет боту '50000 ovqat'.",
        "hint": "",
        "explanation": "",
    },
    4437: {
        "title": "Декоратор aiogram, перехватывающий свободный текст без команды",
        "description": "Напишите декоратор aiogram, используемый для перехвата ЛЮБОГО текстового сообщения, не начинающегося с /команды (без фильтра).",
        "hint": "",
        "expected_answer": "@dp.message()",
    },
    4438: {
        "title": "Почему без app_context() возникает RuntimeError?",
        "description": (
            "Если в функции link_handler_xato() вызвать User.query "
            "напрямую, НЕ ВНУТРИ app.app_context(), почему возникает "
            "ошибка \"RuntimeError: Working outside of application "
            "context\"? Объясните своими словами."
        ),
        "hint": "Откуда запросы Flask-SQLAlchemy берут данные конфигурации, и есть ли этот контекст у бота автоматически?",
        "expected_answer": "Запросы Flask-SQLAlchemy вроде User.query внутренне \"запрашивают\" из текущего контекста приложения Flask, к какой базе данных подключаться (DATABASE_URL), и другую конфигурационную информацию. Обычно этот контекст доступен автоматически только тогда, когда Flask обрабатывает HTTP-запрос. Бот же не работает в рамках HTTP-запроса, поэтому никакой контекст Flask автоматически не открывается. Если разработчик не откроет этот контекст вручную через with app.app_context(), Flask-SQLAlchemy не знает, к какой конфигурации обращаться, и выбрасывает ошибку RuntimeError о том, что \"вы используете это вне контекста приложения\".",
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
        TASK_TITLE_RU = "MoneyLog — Telegram-бот: быстрый расход и связка"
        TASK_DESCRIPTION_RU = (
            "Создайте telegram_bot/bot.py, создайте в нём объект приложения "
            "Flask через create_app() (не запуская сервер). Реализуйте связку "
            "аккаунта через команду /link КОД, и быстрое добавление расхода "
            "через свободный текст (в формате 'сумма описание')."
        )
        TASK_REQUIREMENTS_RU = (
            "• telegram_bot/bot.py — вызван create_app(), все запросы к БД "
            "ВНУТРИ app.app_context()\n"
            "• /link КОД — находит пользователя по link_kodi, записывает "
            "telegram_chat_id, устанавливает link_kodi в None\n"
            "• @dp.message() (без фильтра) — анализирует текст в формате 'СУММА ОПИСАНИЕ'\n"
            "• Если соответствующей category нет, она создаётся автоматически\n"
            "• Новый Expense сохраняется с правильными user_id и category_id\n"
            "• Для несвязанного пользователя выводится понятное сообщение\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "aiogram, Flask-SQLAlchemy, app.app_context()"
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
