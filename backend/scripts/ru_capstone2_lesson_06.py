"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=5 (L6)."""
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

LESSON_ID = 754

TITLE_RU = "6-Автоматические уведомления"

TEXT_RU = """\
<h2>Этап 6: Автоматические уведомления — напоминание о приближении срока</h2>

<pre class="mermaid">
flowchart LR
    CRON["cron: запускается каждый час"] --> CMD["manage.py send_reminders"]
    CMD --> QUERY["невыполненные задания со сроком в течение 24 часов"]
    QUERY --> FILTER{"есть telegram_chat_id?"}
    FILTER -->|нет| SKIP["пропускается"]
    FILTER -->|есть| SEND["отправляется сообщение через Telegram Bot API"]
</pre>

<p>"Магия" StudyMate именно здесь: пользователь, <strong>даже не заходя</strong> на веб-сайт, получает <strong>автоматическое</strong> сообщение в Telegram о приближающемся сроке задания. Для этого создадим <strong>отдельный, запланированный</strong> процесс (Django management command).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание Django management command</h4>
<pre><code># studymate/management/commands/send_reminders.py
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from studymate.models import Topshiriq

class Command(BaseCommand):                      # ❗ паттерн Django "python manage.py X"
    help = "Muddati yaqinlashgan topshiriqlar uchun Telegram orqali eslatma yuboradi"

    def handle(self, *args, **options):
        hozir = timezone.now()
        chegara = hozir + timedelta(hours=24)

        topshiriqlar = Topshiriq.objects.filter(
            bajarilgan=False,
            muddat_vaqti__gte=hozir,
            muddat_vaqti__lte=chegara,
        ).exclude(
            user__profile__telegram_chat_id__isnull=True   # ❗ исключает несвязанных пользователей
        ).select_related('user__profile', 'fan')

        for t in topshiriqlar:
            self.xabar_yuborish(t)

    def xabar_yuborish(self, topshiriq):
        chat_id = topshiriq.user.profile.telegram_chat_id
        matn = f"⏰ Eslatma: '{topshiriq.sarlavha}' ({topshiriq.fan.nomi}) muddati yaqinlashmoqda!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": matn},
        )</code></pre>

<h4>БЛОК 2 — почему это отдельный процесс (не aiogram Dispatcher)?</h4>
<pre><code># Dispatcher aiogram - работает, когда пользователь отправляет КОМАНДУ (реактивно)
# send_reminders же - должен запускаться по ВРЕМЕНИ, даже если никто не просит (проактивно)

# Поэтому два отдельных процесса:
# 1. telegram_bot/bot.py (aiogram, работает постоянно, отвечает на команды)
# 2. команда send_reminders (запускается периодически, через cron)

# Оба могут отправлять запросы напрямую (или через aiogram) в Telegram Bot API -
# но send_reminders можно написать и с помощью простой библиотеки requests,
# так как ей не нужно "ждать" сообщений от пользователя.</code></pre>

<h4>БЛОК 3 — планирование через cron</h4>
<pre><code># На развёрнутом сервере через crontab -e:
# Запуск каждый час:
0 * * * * cd /path/to/django_backend && python manage.py send_reminders</code></pre>

<h3>🐛 Намеренная ошибка — забыли отфильтровать несвязанных пользователей</h3>
<pre><code>def handle_xato(self, *args, **options):
    topshiriqlar = Topshiriq.objects.filter(
        bajarilgan=False,
        muddat_vaqti__lte=timezone.now() + timedelta(hours=24),
    ).select_related('user__profile', 'fan')   # ❌ НЕТ .exclude(...)!

    for t in topshiriqlar:
        chat_id = t.user.profile.telegram_chat_id   # ❗ может быть None!
        requests.post(url, json={"chat_id": chat_id, "text": "..."})
        # ❌ Telegram API возвращает ошибку "chat_id не найден",
        #    или программа выдаёт ошибку при работе с None</code></pre>

<p><strong>Результат:</strong> <strong>не все</strong> пользователи обязательно <strong>связали</strong> свой Telegram-аккаунт &mdash; у таких пользователей <code>telegram_chat_id</code> равен <code>None</code>. Если это <strong>не учтено</strong> при фильтрации, код пытается отправить значение <code>None</code> в Telegram API как настоящий chat ID &mdash; это приводит к <strong>неудачным</strong> запросам (или иногда к ошибке программы). <code>.exclude(user__profile__telegram_chat_id__isnull=True)</code> <strong>заранее исключает</strong> таких пользователей из результата запроса.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему это написано как отдельный Django management command?</h4>
<p>Management-команды Django (<code>python manage.py X</code>) &mdash; стандартный способ выполнения <strong>одноразовых или запланированных</strong> задач в проекте Django. Эта задача не зависит от запроса пользователя &mdash; она должна запускаться <strong>по времени</strong> (например каждый час), поэтому пишется не как обычный view, а как отдельная команда.</p>

<h4>2. Почему это отдельно от aiogram Dispatcher?</h4>
<p><code>Dispatcher</code> aiogram &mdash; <strong>реактивен</strong>: запускается, когда пользователь отправляет команду. Уведомления же должны быть <strong>проактивными</strong> &mdash; отправляться автоматически по наступлении времени, даже если никто не просит. Это два разных типа "триггера", поэтому два отдельных процесса.</p>

<h4>3. Почему используется библиотека <code>requests</code>, а не aiogram?</h4>
<p><code>send_reminders</code> запускается один раз и завершается &mdash; ей не нужна сложная, постоянно работающая система aiogram, "ожидающая" сообщений пользователя. Достаточно простого <code>requests.post()</code> напрямую к обычному HTTP API Telegram.</p>

<h4>4. Как работает <code>.exclude(user__profile__telegram_chat_id__isnull=True)</code>?</h4>
<p>Это &mdash; способ фильтрации Django ORM через связанную таблицу (вспомните <code>filter(связь__поле=...)</code> из урока 7). Он переходит от <code>Topshiriq</code> к <code>user</code>, затем к <code>profile</code>, и <strong>исключает</strong> из результата записи, где <code>telegram_chat_id</code> равен <code>NULL</code>.</p>

<h4>5. Почему опасно не фильтровать несвязанных пользователей?</h4>
<p>Отправка значения <code>None</code> как настоящего Telegram chat ID &mdash; <strong>бессмысленный</strong> запрос, Telegram API его отклоняет. Кроме того, при большом объёме данных такие "напрасные" запросы могут накапливаться, замедляя систему или заполняя логи ненужными ошибками.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Django management command — стандартное решение для задач, запускаемых по времени</li>
<li>✅ Проактивные (уведомления) и реактивные (ответ на команду) процессы строятся отдельно</li>
<li>✅ Для простых, одноразовых HTTP-запросов <code>requests</code> проще, чем aiogram</li>
<li>✅ <code>.exclude(связь__поле__isnull=True)</code> заранее исключает несвязанные записи</li>
<li>✅ cron автоматически запускает подобные задачи через регулярные промежутки времени</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 6: Автоматические уведомления
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/management/commands/send_reminders.py
# ─────────────────────────────────────────────────────────────────────

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from studymate.models import Topshiriq

BOT_TOKEN = "..."  # берётся из переменной окружения


class Command(BaseCommand):
    help = "Muddati yaqinlashgan topshiriqlar uchun Telegram orqali eslatma yuboradi"

    def handle(self, *args, **options):
        hozir = timezone.now()
        chegara = hozir + timedelta(hours=24)

        topshiriqlar = Topshiriq.objects.filter(
            bajarilgan=False,
            muddat_vaqti__gte=hozir,
            muddat_vaqti__lte=chegara,
        ).exclude(
            user__profile__telegram_chat_id__isnull=True
        ).select_related('user__profile', 'fan')

        for t in topshiriqlar:
            self.xabar_yuborish(t)

    def xabar_yuborish(self, topshiriq):
        chat_id = topshiriq.user.profile.telegram_chat_id
        matn = f"⏰ Eslatma: '{topshiriq.sarlavha}' ({topshiriq.fan.nomi}) muddati yaqinlashmoqda!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": matn},
        )

# ─────────────────────────────────────────────────────────────────────
# 2) crontab (в комментарии - настройка сервера, не Python)
# ─────────────────────────────────────────────────────────────────────

# 0 * * * * cd /path/to/django_backend && python manage.py send_reminders

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - забыли фильтрацию (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def handle_xato(self, *args, **options):
#     topshiriqlar = Topshiriq.objects.filter(
#         bajarilgan=False,
#         muddat_vaqti__lte=timezone.now() + timedelta(hours=24),
#     ).select_related('user__profile', 'fan')   # НЕТ .exclude(...)!
#     for t in topshiriqlar:
#         chat_id = t.user.profile.telegram_chat_id   # может быть None!
#         requests.post(url, json={"chat_id": chat_id, "text": "..."})
"""

EX = {
    4374: {
        "title": "Почему уведомление написано как отдельная management command?",
        "description": "Почему send_reminders написан не как обычный Django view, а как отдельная management command (python manage.py X)?",
        "hint": "View отвечает на запрос пользователя, а эта задача должна запускаться по времени.",
        "explanation": "View предназначены для ответа на HTTP-запросы, но задача уведомления должна запускаться без какого-либо запроса, просто по времени (через cron) — для этого подходит Django management command.",
    },
    4375: {
        "title": "Почему для send_reminders используется requests, а не aiogram?",
        "description": "Почему в команде send_reminders для отправки сообщения в Telegram используется обычная библиотека requests, а не Dispatcher aiogram?",
        "hint": "Dispatcher aiogram постоянно работает, \"ожидая\" сообщений пользователя — нужно ли это здесь?",
        "explanation": "send_reminders запускается один раз и завершает свою работу — ей не нужна сложная, постоянно работающая система aiogram, ожидающая команд пользователя, достаточно простого HTTP-запроса (requests.post).",
    },
    4376: {
        "title": "Расположите процесс работы send_reminders",
        "description": "Расположите процесс, происходящий при запуске cron команды send_reminders.",
        "hint": "",
        "explanation": "",
    },
    4377: {
        "title": "Инструмент для регулярного запуска задач по времени",
        "description": "Напишите классический инструмент Linux-сервера, используемый для автоматического, регулярного запуска задачи (например каждый час).",
        "hint": "",
        "expected_answer": "cron",
    },
    4378: {
        "title": "Почему отсутствие фильтрации несвязанных пользователей создаёт проблему?",
        "description": (
            "Если не использовать .exclude(user__profile__telegram_chat_id__isnull=True), "
            "и задание пользователя, не связавшего Telegram-аккаунт, "
            "попадёт в результат, какая проблема возникнет? Объясните "
            "своими словами."
        ),
        "hint": "Какое значение имеет telegram_chat_id у несвязанного пользователя, и чем закончится отправка этого значения в Telegram API?",
        "expected_answer": "У пользователя, не связавшего Telegram-аккаунт, значение telegram_chat_id равно None. Если таких пользователей заранее не исключить из результата, код попытается отправить их значение None как настоящий Telegram chat ID через requests.post() в Telegram Bot API. Этот запрос будет отклонён Telegram (с ошибкой \"chat_id не найден\"), так как None не является настоящим идентификатором чата. Кроме того, при большом количестве пользователей такие напрасные запросы могут накапливаться, впустую расходуя ресурсы системы и заполняя логи ненужными ошибками.",
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
        TASK_TITLE_RU = "StudyMate — автоматические уведомления Telegram"
        TASK_DESCRIPTION_RU = (
            "Создайте Django management command с именем send_reminders — она "
            "находит невыполненные задания со сроком в течение 24 часов и "
            "автоматически отправляет напоминание пользователям со связанным "
            "Telegram-аккаунтом. Правильно отфильтруйте несвязанных пользователей."
        )
        TASK_REQUIREMENTS_RU = (
            "• Создан файл studymate/management/commands/send_reminders.py\n"
            "• Выбираются только невыполненные задания со сроком в течение 24 часов\n"
            "• Через .exclude(...) исключены пользователи без связанного Telegram\n"
            "• Для каждого подходящего задания отправляется правильно оформленное сообщение в Telegram Bot API\n"
            "• Показан успешный запуск команды через cron (или хотя бы вручную)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Django management commands, requests, Telegram Bot API, cron"
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
