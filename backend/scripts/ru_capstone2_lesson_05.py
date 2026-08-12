"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=4 (L5)."""
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

LESSON_ID = 752

TITLE_RU = "5-Telegram-бот: связка аккаунта и команды"

TEXT_RU = """\
<h2>Этап 5: Telegram-бот — связка аккаунта и чтение из базы Django</h2>

<pre class="mermaid">
flowchart LR
    BOTFILE["telegram_bot/bot.py"] -->|django.setup()| ORM["Django ORM готов к работе"]
    ORM --> MODELS["from studymate.models import ..."]
    USER["Пользователь получает link_kodi на веб-сайте"] --> LINK["/link код - отправляется боту"]
    LINK --> DB["telegram_chat_id записывается в таблицу users"]
    DB --> CMD["/topshiriqlar - бот читает ИЗ ЭТОЙ таблицы"]
</pre>

<p>Это &mdash; <strong>центральный</strong> этап курса: знания, полученные на курсе Telegram Bot aiogram, теперь работают с <strong>той же самой</strong> базой данных Django. Бот — не отдельный проект, а <strong>третий интерфейс</strong> StudyMate.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — модель Profile: добавление полей telegram к User</h4>
<pre><code># studymate/models.py
# ❗ Нельзя напрямую добавить новое поле в готовую модель User Django -
#   поэтому расширяем её через OneToOne с "Profile"
#   (telegram_chat_id/link_kodi из таблицы "users" урока 1 находятся здесь)

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    link_kodi = models.CharField(max_length=10, null=True, blank=True)</code></pre>

<h4>БЛОК 2 — "подключение" Django ORM к боту (django.setup())</h4>
<pre><code># telegram_bot/bot.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")   # ❗ указывает, какие настройки использовать
django.setup()                                                            # ❗ ОБЯЗАТЕЛЬНО - загружает приложения Django

# ❗ ДОЛЖНО импортироваться ПОСЛЕ django.setup() - иначе Django ещё не готов!
from studymate.models import Fan, Topshiriq, Profile
from django.contrib.auth.models import User

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()</code></pre>

<h4>БЛОК 3 — команда /link: связка аккаунтов</h4>
<pre><code>@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    try:
        user = await User.objects.aget(profile__link_kodi=kod)   # ❗ aget() - async Django ORM (4.1+)
    except User.DoesNotExist:
        await message.answer("Kod noto'g'ri yoki eskirgan")
        return

    user.profile.telegram_chat_id = message.chat.id    # ❗ связывается с пользователем, созданным на веб-сайте
    user.profile.link_kodi = None                       # ❗ код одноразовый - очищается после использования
    await user.profile.asave()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.first_name}!")</code></pre>

<h4>БЛОК 4 — команда /topshiriqlar: показ через бота данных, созданных на ВЕБ-САЙТЕ</h4>
<pre><code>@dp.message(Command("topshiriqlar"))
async def topshiriqlar_handler(message: types.Message):
    try:
        user = await User.objects.aget(profile__telegram_chat_id=message.chat.id)
    except User.DoesNotExist:
        await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
        return

    topshiriqlar = [t async for t in Topshiriq.objects.filter(
        user=user, bajarilgan=False
    ).select_related('fan')]

    if not topshiriqlar:
        await message.answer("Bajarilmagan topshiriqlar yo'q 🎉")
        return

    matn = "\\n".join(f"📌 {t.sarlavha} ({t.fan.nomi}) — {t.muddat_vaqti:%d.%m %H:%M}" for t in topshiriqlar)
    await message.answer(matn)</code></pre>

<h3>🐛 Намеренная ошибка — импорт моделей ДО django.setup()</h3>
<pre><code># telegram_bot/bot.py
from studymate.models import Fan, Topshiriq   # ❌ импортировано ДО django.setup()!

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
django.setup()

# При попытке запустить бота:
# ❌ django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.</code></pre>

<p><strong>Результат:</strong> чтобы модели Django (<code>Fan</code>, <code>Topshiriq</code> и т.д.) работали, Django должен сначала загрузить <strong>все свои приложения</strong> (<code>INSTALLED_APPS</code>) и подготовить внутренний "реестр" &mdash; это делает <code>django.setup()</code>. Если модели импортируются <strong>до</strong> вызова <code>django.setup()</code>, Django ещё "не готов", и возникает ошибка <code>AppRegistryNotReady</code>. <strong>Строгий порядок</strong>: сначала <code>os.environ.setdefault(...)</code> и <code>django.setup()</code>, <strong>только затем</strong> можно импортировать модели.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем боту нужен django.setup()?</h4>
<p>Обычно модели Django используются только внутри самого сервера Django (через <code>manage.py runserver</code>), в этот момент Django автоматически "настраивается". Бот же — <strong>совершенно отдельный</strong> Python-скрипт, не являющийся частью сервера Django. <code>django.setup()</code> даёт этому отдельному скрипту возможность использовать Django ORM <strong>так же, как на сервере Django</strong>.</p>

<h4>2. Почему link_kodi одноразовый (очищается после использования)?</h4>
<p>Если бы <code>link_kodi</code> оставался в базе после использования, кто-то мог бы <strong>повторно</strong> использовать этот код и "связаться" с чужим аккаунтом (если бы узнал код). Установка кода в <code>None</code> сразу после использования устраняет этот риск безопасности.</p>

<h4>3. Почему бот использует Django ORM напрямую, а не отправляет отдельный HTTP-запрос?</h4>
<p>Предполагается, что бот и Django backend работают <strong>на одном</strong> сервере (или хотя бы в среде с доступом к одной базе). Прямое использование Django ORM гораздо эффективнее и проще, чем отправка HTTP-запроса самому себе (backend вызывает свой же API).</p>

<h4>4. Что такое <code>aget()</code>/<code>asave()</code> и зачем они нужны?</h4>
<p>aiogram — <strong>асинхронная</strong> библиотека (вы видели <code>asyncio</code> в уроке 7 курса Ilg'or Mavzular). Начиная с Django 4.1 существуют <strong>асинхронные версии</strong> ORM (<code>aget</code>, <code>asave</code>, <code>acreate</code> и т.д.) &mdash; это версии обычных <code>get()</code>/<code>save()</code>, работающие с <code>await</code>, необходимые для правильной работы внутри асинхронных обработчиков aiogram.</p>

<h4>5. Почему django.setup() должен быть сразу ПОСЛЕ импортов, а не до них?</h4>
<p>Python выполняет файл сверху вниз. Если строка <code>from studymate.models import ...</code> написана <strong>до</strong> <code>django.setup()</code>, то к моменту достижения Python этой строки Django ещё "не зарегистрировал приложения", и попытка импортировать модель приводит к ошибке <code>AppRegistryNotReady</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>django.setup()</code> ОБЯЗАТЕЛЕН для использования Django ORM вне сервера Django (например в боте), вызывается перед импортами моделей</li>
<li>✅ <code>link_kodi</code> — одноразовый код связки, очищаемый сразу после использования</li>
<li>✅ Бот использует Django ORM напрямую — не отправляет отдельный HTTP-запрос</li>
<li>✅ <code>aget()</code>/<code>asave()</code> — версии Django ORM, используемые внутри асинхронных обработчиков</li>
<li>✅ <code>django.setup()</code> должен вызываться СРАЗУ (но перед импортом моделей), а не до всех импортов</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 5: Telegram-бот - связка аккаунта и команды
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 0) studymate/models.py - модель Profile (для полей telegram)
# ─────────────────────────────────────────────────────────────────────

# from django.db import models
# from django.contrib.auth.models import User
#
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     telegram_chat_id = models.BigIntegerField(null=True, blank=True)
#     link_kodi = models.CharField(max_length=10, null=True, blank=True)

# ─────────────────────────────────────────────────────────────────────
# 1) telegram_bot/bot.py - django.setup()
# ─────────────────────────────────────────────────────────────────────

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
django.setup()

from studymate.models import Fan, Topshiriq, Profile
from django.contrib.auth.models import User

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
    try:
        user = await User.objects.aget(profile__link_kodi=kod)
    except User.DoesNotExist:
        await message.answer("Kod noto'g'ri yoki eskirgan")
        return

    user.profile.telegram_chat_id = message.chat.id
    user.profile.link_kodi = None
    await user.profile.asave()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.first_name}!")


@dp.message(Command("topshiriqlar"))
async def topshiriqlar_handler(message: types.Message):
    try:
        user = await User.objects.aget(profile__telegram_chat_id=message.chat.id)
    except User.DoesNotExist:
        await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
        return

    topshiriqlar = [t async for t in Topshiriq.objects.filter(
        user=user, bajarilgan=False
    ).select_related('fan')]

    if not topshiriqlar:
        await message.answer("Bajarilmagan topshiriqlar yo'q 🎉")
        return

    matn = "\\n".join(f"📌 {t.sarlavha} ({t.fan.nomi}) — {t.muddat_vaqti:%d.%m %H:%M}" for t in topshiriqlar)
    await message.answer(matn)

# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка - импорт ДО django.setup() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# from studymate.models import Fan, Topshiriq   # ДО django.setup()!
#
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
# django.setup()
# ❌ django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
"""

EX = {
    4364: {
        "title": "Зачем нужен django.setup()?",
        "description": "В чём основная причина вызова django.setup() в скрипте Telegram-бота?",
        "hint": "Бот не является частью сервера Django, это отдельный скрипт.",
        "explanation": "django.setup() загружает приложения Django и готовит внутренний \"реестр\" — это необходимо для использования Django ORM вне сервера Django (например в боте).",
    },
    4365: {
        "title": "Почему link_kodi очищается после использования?",
        "description": "Почему после использования команды /link значение user.profile.link_kodi сразу устанавливается в None?",
        "hint": "Это вопрос безопасности - код должен быть \"одноразовым\".",
        "explanation": "Если бы link_kodi оставался в базе после использования, любой узнавший этот код мог бы повторно связаться с чужим аккаунтом — поэтому он сразу очищается после использования.",
    },
    4366: {
        "title": "Расположите процесс работы команды /topshiriqlar",
        "description": "Расположите внутренний процесс, происходящий при отправке пользователем боту команды /topshiriqlar.",
        "hint": "",
        "explanation": "",
    },
    4367: {
        "title": "Асинхронная версия метода Django ORM",
        "description": "Как называется асинхронная версия обычного метода get(), которую можно использовать в обработчиках aiogram (Django 4.1+)? (напишите название)",
        "hint": "",
        "expected_answer": "aget",
    },
    4368: {
        "title": "Почему импорт моделей до django.setup() даёт ошибку?",
        "description": (
            "Если в файле telegram_bot/bot.py строка from studymate.models "
            "import ... написана ДО вызова django.setup(), почему "
            "возникает ошибка \"AppRegistryNotReady: Apps aren't loaded "
            "yet\"? Объясните своими словами."
        ),
        "hint": "В каком порядке Python выполняет код, и что должно быть готово до работы моделей Django?",
        "expected_answer": "Чтобы модели Django работали, Django должен сначала загрузить все свои приложения (INSTALLED_APPS) и подготовить внутренний \"реестр\" — именно это делает django.setup(). Python выполняет файл сверху вниз, поэтому если строка импорта модели написана до вызова django.setup(), к моменту достижения Python этой строки Django ещё \"не готов\" (приложения ещё не зарегистрированы). Из-за этого Django считает попытку импортировать модель небезопасной и выдаёт ошибку AppRegistryNotReady.",
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
        TASK_TITLE_RU = "StudyMate — Telegram-бот: связка и команды"
        TASK_DESCRIPTION_RU = (
            "Создайте telegram_bot/bot.py, подключитесь к Django ORM через "
            "django.setup(). Реализуйте связку аккаунта через команду /link КОД, "
            "и показ созданных на веб-сайте заданий через команду /topshiriqlar."
        )
        TASK_REQUIREMENTS_RU = (
            "• Модель Profile (user, telegram_chat_id, link_kodi) создана и мигрирована\n"
            "• telegram_bot/bot.py — django.setup() правильно вызван ДО импортов, "
            "но ПОСЛЕ него идёт импорт моделей\n"
            "• /link КОД — находит пользователя по link_kodi, записывает "
            "telegram_chat_id, устанавливает link_kodi в None\n"
            "• /topshiriqlar — определяет пользователя по telegram_chat_id, "
            "показывает его невыполненные задания\n"
            "• Для несвязанного пользователя выводится понятное сообщение\n"
            "• Бот и Django backend подключены к ОДНОЙ базе PostgreSQL "
            "(не отдельный SQLite)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "aiogram, Django ORM, PostgreSQL"
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
