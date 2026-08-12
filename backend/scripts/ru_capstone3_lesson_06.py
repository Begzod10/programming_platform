"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=5 (L6)."""
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

LESSON_ID = 768

TITLE_RU = "6-Месячный отчёт и уведомление о бюджете"

TEXT_RU = """\
<h2>Этап 6: Месячный отчёт и уведомление о бюджете</h2>

<pre class="mermaid">
flowchart LR
    CRON["cron: запускается каждый день"] --> CLI["flask send-budget-alerts"]
    CLI --> LOOP["Цикл по каждому пользователю"]
    LOOP --> SUM{"func.sum() - ТОЛЬКО для этого user_id?"}
    SUM -->|нет фильтра| BUG["Возвращается общая сумма ВСЕХ пользователей"]
    SUM -->|есть фильтр| OK["Только сумма этого пользователя"]
</pre>

<p>Финальная "умная" функция MoneyLog: каждый месяц каждый пользователь должен сравнить сумму <strong>своих</strong> расходов со <strong>своим</strong> бюджетом, и если превышен — получить предупреждение через Telegram.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание Flask CLI команды</h4>
<pre><code># app/commands.py
import click
from flask import current_app
from sqlalchemy import func
from datetime import date
import requests
from app import db
from app.models import User, Expense

@current_app.cli.command('send-budget-alerts')     # ❗ собственный CLI-паттерн Flask - 'flask send-budget-alerts'
def send_budget_alerts():
    bugun = date.today()
    oy_boshi = bugun.replace(day=1)

    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    for user in foydalanuvchilar:
        jami = db.session.query(func.sum(Expense.summa)).filter(
            Expense.user_id == user.id,               # ❗ ВАЖНО - ТОЛЬКО этот пользователь!
            Expense.sana >= oy_boshi,
        ).scalar() or 0

        if user.oylik_byudjet and jami > user.oylik_byudjet:
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)</code></pre>

<h4>БЛОК 2 — отправка сообщения в Telegram</h4>
<pre><code>def xabar_yuborish(chat_id, jami, byudjet):
    matn = (
        f"⚠️ Diqqat! Bu oy siz {jami} so'm sarfladingiz, "
        f"byudjetingiz esa {byudjet} so'm edi."
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": matn},
    )</code></pre>

<h4>БЛОК 3 — планирование через cron</h4>
<pre><code># crontab -e
# Запуск каждый день в 20:00:
0 20 * * * cd /path/to/flask_backend && flask send-budget-alerts</code></pre>

<h3>🐛 Намеренная ошибка — забыли фильтр по пользователю в агрегатном запросе</h3>
<pre><code>def send_budget_alerts_xato():
    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    # ❌ Одна общая сумма - вычисляется ОДИН РАЗ для ВСЕХ пользователей!
    jami = db.session.query(func.sum(Expense.summa)).scalar() or 0

    for user in foydalanuvchilar:
        if user.oylik_byudjet and jami > user.oylik_byudjet:   # ❌ 'jami' одинакова для ВСЕХ!
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)

# Результат: если 100 пользователей, и их общие расходы велики,
# КАЖДЫЙ пользователь (даже потративший всего 5000 сум) получит
# ЛОЖНОЕ предупреждение "вы превысили бюджет"!</code></pre>

<p><strong>Результат:</strong> если <code>func.sum(Expense.summa)</code> вызвать <strong>без</strong> <code>.filter(Expense.user_id == ...)</code>, он суммирует <strong>все</strong> расходы <strong>всех</strong> пользователей в базе данных в одну сумму. Это одно "глобальное" число, если его затем сравнивать <strong>с каждым</strong> пользователем (внутри цикла) повторно, даёт <strong>абсолютно неверный</strong> результат &mdash; пользователи с малыми расходами тоже могут получить ложное предупреждение из-за расходов других. Правильное решение: всегда добавлять <code>.filter(Expense.user_id == user.id)</code> <strong>внутри цикла, отдельно для каждого</strong> пользователя.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое Flask CLI команда (<code>@app.cli.command()</code>)?</h4>
<p>Это &mdash; механизм Flask, <strong>похожий</strong> на management-команды Django: способ написания задач, запускаемых из терминала через <code>flask &lt;имя-команды&gt;</code>, не зависящих от HTTP-запроса. Оба служат одной цели — структурированному написанию задач, запускаемых по времени (через cron).</p>

<h4>2. Почему <code>func.sum()</code> вычисляется на уровне базы данных?</h4>
<p><code>db.session.query(func.sum(...))</code> вычисляет сумму <strong>не в коде Python</strong>, а <strong>внутри SQL-запроса</strong> (например <code>SELECT SUM(summa) FROM expenses WHERE ...</code>). Это работает очень быстро даже при тысячах записей, так как не нужно загружать все данные в Python.</p>

<h4>3. Почему <code>.filter(Expense.user_id == user.id)</code> ОБЯЗАТЕЛЕН?</h4>
<p>Агрегатные функции (<code>SUM</code>, <code>COUNT</code>, <code>AVG</code>) <strong>по умолчанию</strong> вычисляют <strong>все</strong> строки, соответствующие запросу. Без условия <code>WHERE user_id = ...</code> SQL означает "все расходы всех пользователей" &mdash; это не личная сумма отдельного пользователя.</p>

<h4>4. Почему эта ошибка <strong>особенно</strong> опасна внутри цикла?</h4>
<p>Так как агрегатный запрос вызывается <strong>вне цикла, один раз</strong>, результат (неверное, общее число) <strong>переиспользуется для каждого</strong> пользователя — это "умножает" ошибку: один неверный запрос приводит к отправке неверного предупреждения <strong>всем</strong> пользователям.</p>

<h4>5. Зачем нужно <code>func.sum(...) or 0</code>?</h4>
<p>Если у пользователя вообще нет расходов, <code>SUM()</code> в SQL возвращает <code>NULL</code> (не <code>0</code>). Попытка сравнить <code>None > бюджет</code> в Python вызовет ошибку. <code>or 0</code> заменяет состояние <code>None</code> на <code>0</code>, позволяя безопасное сравнение.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>@app.cli.command()</code> — CLI-механизм Flask, похожий на management-команды Django</li>
<li>✅ <code>func.sum()</code> быстро вычисляет сумму на уровне SQL</li>
<li>✅ В агрегатных запросах <code>.filter()</code> по пользователю ОБЯЗАТЕЛЕН, иначе все пользователи смешиваются</li>
<li>✅ Неверный агрегатный запрос внутри цикла "умножает" ошибку на всех пользователей</li>
<li>✅ <code>SUM()</code> без результата возвращает <code>NULL</code> — делается безопасным через <code>or 0</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 6: Месячный отчёт и уведомление о бюджете
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/commands.py - Flask CLI команда
# ─────────────────────────────────────────────────────────────────────

import click
from flask import current_app
from sqlalchemy import func
from datetime import date
import requests
from app import db
from app.models import User, Expense

BOT_TOKEN = "..."  # берётся из переменной окружения


@current_app.cli.command('send-budget-alerts')
def send_budget_alerts():
    bugun = date.today()
    oy_boshi = bugun.replace(day=1)

    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    for user in foydalanuvchilar:
        jami = db.session.query(func.sum(Expense.summa)).filter(
            Expense.user_id == user.id,
            Expense.sana >= oy_boshi,
        ).scalar() or 0

        if user.oylik_byudjet and jami > user.oylik_byudjet:
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)


def xabar_yuborish(chat_id, jami, byudjet):
    matn = (
        f"⚠️ Diqqat! Bu oy siz {jami} so'm sarfladingiz, "
        f"byudjetingiz esa {byudjet} so'm edi."
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": matn},
    )

# ─────────────────────────────────────────────────────────────────────
# 2) crontab (в комментарии - настройка сервера, не Python)
# ─────────────────────────────────────────────────────────────────────

# 0 20 * * * cd /path/to/flask_backend && flask send-budget-alerts

# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - агрегат без фильтра по пользователю (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def send_budget_alerts_xato():
#     foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()
#     jami = db.session.query(func.sum(Expense.summa)).scalar() or 0   # НЕТ фильтра!
#     for user in foydalanuvchilar:
#         if user.oylik_byudjet and jami > user.oylik_byudjet:   # 'jami' одинакова для ВСЕХ!
#             xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)
"""

EX = {
    4444: {
        "title": "Что такое Flask CLI команда (@app.cli.command())?",
        "description": "Для чего используется @app.cli.command()?",
        "hint": "Это механизм, похожий на management-команды Django.",
        "explanation": "@app.cli.command() — механизм Flask, похожий на management-команды Django, позволяющий создавать задачи, запускаемые через терминал в форме 'flask <имя-команды>', не зависящие от HTTP-запроса.",
    },
    4445: {
        "title": "Почему .filter(Expense.user_id == user.id) обязателен?",
        "description": "Почему при вызове func.sum(Expense.summa) обязательно нужно добавить .filter(Expense.user_id == user.id)?",
        "hint": "Какие строки агрегатные функции вычисляют по умолчанию?",
        "explanation": "Агрегатные функции (SUM) по умолчанию вычисляют все строки, соответствующие запросу. Без filter(user_id=...) результат окажется общей суммой всех пользователей, а не одного конкретного.",
    },
    4446: {
        "title": "Расположите процесс работы send_budget_alerts()",
        "description": "Расположите процесс, происходящий при запуске команды flask send-budget-alerts.",
        "hint": "",
        "explanation": "",
    },
    4447: {
        "title": "Что возвращает SUM() без результата?",
        "description": "Если у пользователя вообще нет расходов, какое значение возвращает функция SUM() в SQL? (напишите ваш ответ)",
        "hint": "Это не 0.",
        "expected_answer": "NULL",
    },
    4448: {
        "title": "Почему общий агрегатный запрос вне цикла даёт ложное предупреждение всем пользователям?",
        "description": (
            "В send_budget_alerts_xato() jami = db.session.query(func.sum(...))"
            ".scalar() вычисляется ВНЕ цикла, один раз, без фильтра. "
            "Почему в этом случае даже пользователь с малыми расходами "
            "может получить ложное предупреждение \"вы превысили "
            "бюджет\"? Объясните своими словами."
        ),
        "hint": "",
        "expected_answer": "Так как filter(Expense.user_id == ...) не добавлен, func.sum(Expense.summa) суммирует ВСЕ расходы ВСЕХ пользователей базы данных в одно общее число. Это одно \"глобальное\" число сохраняется в переменной 'jami', а затем ВНУТРИ цикла сравнивается с личным значением oylik_byudjet каждого пользователя. В результате, если некоторые пользователи потратили очень много, их сумма увеличивает общее 'jami', и это большое, общее число сравнивается с личным бюджетом пользователя с малыми расходами (например всего 5000 сум), что приводит к отправке ему ложного, ошибочного предупреждения \"вы превысили бюджет\".",
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
        TASK_TITLE_RU = "MoneyLog — месячный отчёт и уведомление о бюджете"
        TASK_DESCRIPTION_RU = (
            "Создайте Flask CLI команду с именем send-budget-alerts — она "
            "вычисляет сумму расходов каждого пользователя за этот месяц "
            "ТОЛЬКО для него, и отправляет предупреждение через Telegram, "
            "если превышен oylik_byudjet."
        )
        TASK_REQUIREMENTS_RU = (
            "• app/commands.py: CLI-команда send-budget-alerts создана через @app.cli.command()\n"
            "• Для каждого пользователя func.sum() отфильтрован ТОЛЬКО по его user_id\n"
            "• Если результат SUM() равен None, используется как 0 (or 0)\n"
            "• Сообщение отправляется только пользователям, превысившим oylik_byudjet\n"
            "• Показан успешный запуск команды (вручную или через cron)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Flask CLI commands, SQLAlchemy func.sum, requests, Telegram Bot API"
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
