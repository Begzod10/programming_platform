"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=0 (L1)."""
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

LESSON_ID = 758

TITLE_RU = "1-Планирование и repo skeleton"

TEXT_RU = """\
<h2>MoneyLog — объединение vanilla JS, Flask и Telegram Bot за 7 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> API["2-Flask API"]
    API --> FE["3-Vanilla JS frontend"]
    FE --> AUTH["4-Аутентификация"]
    AUTH --> BOT["5-Бот: быстрый расход"]
    BOT --> REPORT["6-Месячный отчёт"]
    REPORT --> DEPLOY["7-Deploy"]
</pre>

<p>На этот раз вы объедините HTML/CSS, <strong>vanilla</strong> JavaScript (без React), Flask и Telegram Bot: <strong>MoneyLog</strong> — трекер личных расходов. Вы сможете добавлять расходы и через веб-страницу, и через Telegram-бота (просто написав текст!) — оба работают с одной базой данных.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — структура репозитория: почему frontend не деплоится отдельно?</h4>
<pre><code># Monorepo для MoneyLog
moneylog/
  flask_backend/
    app/
      static/          # ❗ vanilla JS/CSS здесь - Flask САМ их обслуживает!
      templates/        # ❗ index.html здесь
      models.py
      routes.py
    run.py
  telegram_bot/
    bot.py
  README.md

# ❗ ВАЖНОЕ отличие: в отличие от React, vanilla JS не требует "шага сборки"
#   (webpack/vite) - браузер может напрямую читать .js файл.
#   Поэтому отдельный Vercel/Netlify НЕ НУЖЕН - Flask может САМ обслуживать
#   и frontend (один деплой, CORS тоже не нужен!)</code></pre>

<h4>БЛОК 2 — схема БД: правильный тип для хранения денежной суммы</h4>
<pre><code># Основные таблицы для MoneyLog:
#
# users            (id, ism, email, parol_hash, telegram_chat_id NULLABLE,
#                    link_kodi NULLABLE, oylik_byudjet NUMERIC(10,2))
# categories       (id, nomi, user_id -> users.id)
# expenses         (id, summa NUMERIC(10,2), tavsif, sana,
#                    category_id -> categories.id, user_id -> users.id,
#                    yaratilgan_vaqt)
#
# ❗ summa NUMERIC(10,2) - для ТОЧНОГО хранения денежной суммы,
#   НЕ FLOAT! (увидим в БЛОКЕ 3)</code></pre>

<h4>БЛОК 3 — README.md: статус трёх частей</h4>
<pre><code># README.md
# MoneyLog

## О проекте
Трекер личных расходов - Flask + vanilla JS + Telegram Bot,
с одной общей базой данных.

## Технологии
- Backend: Flask, Flask-SQLAlchemy, PostgreSQL
- Frontend: HTML, CSS, vanilla JavaScript (обслуживается через Flask)
- Bot: aiogram (Telegram)

## Статус
- [x] Планирование и repo skeleton
- [ ] Flask backend API
- [ ] Vanilla JS frontend
- [ ] Аутентификация
- [ ] Telegram-бот: быстрый расход и связка
- [ ] Месячный отчёт и уведомление о бюджете
- [ ] Deploy</code></pre>

<h3>🐛 Намеренная ошибка — планирование суммы денег как FLOAT</h3>
<pre><code># ❌ НЕВЕРНЫЙ план:
# expenses.summa = FLOAT  # выглядит как "обычное дробное число", но...

# Попробуйте в Python/JavaScript с FLOAT:
0.1 + 0.2 == 0.3     # ❌ False! (результат 0.30000000000000004)

# Если сумма хранится в FLOAT, и вы сложите 1000 расходов по 10.10, итог
# может получиться не 10100.00, а неточным числом вроде 10099.999999999998!</code></pre>
<p><strong>Результат:</strong> тип <code>FLOAT</code> (или <code>double</code>) хранится в <strong>двоичной</strong> (binary) системе, и многие десятичные дроби (например <code>0.1</code>) <strong>не могут быть точно</strong> представлены в этой системе &mdash; это приводит к небольшим, но реальным ошибкам при суммировании. В любой системе, работающей с деньгами (как MoneyLog), это <strong>серьёзная</strong> проблема: месячные отчёты могут получаться неточными на несколько копеек. Правильное решение: использовать тип <code>NUMERIC(10, 2)</code> (или <code>Decimal</code> в Python) &mdash; он хранит числа точно, в <strong>десятичной</strong> системе.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему на этот раз не нужен отдельный хостинг для frontend?</h4>
<p>Такие библиотеки, как React, требуют <strong>шага сборки</strong> (превращение JSX в понятный браузеру JS), поэтому удобен отдельный статичный хостинг (Vercel/Netlify). Vanilla JS же читается браузером <strong>напрямую</strong> &mdash; сборка не нужна, поэтому Flask может обслуживать его <strong>сам</strong> через <code>static/</code>/<code>templates/</code>. Это также полностью устраняет проблему CORS (всё обслуживается с одного origin)!</p>

<h4>2. Почему снова нужны <code>telegram_chat_id</code> и <code>link_kodi</code>?</h4>
<p>Это продолжение паттерна из второго capstone-курса: для связи веб-аккаунта пользователя с его Telegram-аккаунтом. В MoneyLog тоже, чтобы пользователь мог писать расходы боту, бот должен знать, <strong>какому</strong> веб-пользователю он принадлежит.</p>

<h4>3. Почему поле <code>oylik_byudjet</code> добавлено в таблицу <code>users</code>?</h4>
<p>Чтобы на этапе 6 отправить пользователю предупреждение "вы превысили бюджет", система должна знать <strong>лимит бюджета каждого</strong> пользователя &mdash; так как это персональная настройка, она хранится в таблице <code>users</code>.</p>

<h4>4. Почему <code>NUMERIC(10,2)</code>, а не обычный <code>FLOAT</code>?</h4>
<p><code>FLOAT</code> работает с двоичными дробями и не может <strong>точно</strong> представить многие простые десятичные числа (например <code>0.1</code>) &mdash; это приводит к накоплению небольших ошибок при многократном сложении/вычитании. <code>NUMERIC(10,2)</code> (или <code>DECIMAL</code>) же хранит десятичные числа <strong>точно</strong> &mdash; это стандартная и <strong>обязательная</strong> практика при работе с деньгами.</p>

<h4>5. Как этот проект объединяет три отдельных курса?</h4>
<p>Знания, полученные <strong>отдельно</strong> на курсах HTML/CSS и JavaScript (frontend), Flask (backend + база данных) и Telegram Bot (aiogram), теперь объединяются для <strong>одной</strong> реальной цели (отслеживание личных финансов).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Vanilla JS не требует шага сборки — Flask может обслуживать его напрямую (без CORS)</li>
<li>✅ <code>telegram_chat_id</code>/<code>link_kodi</code> — для связи веб- и Telegram-аккаунтов</li>
<li>✅ Денежная сумма <strong>никогда</strong> не должна храниться в <code>FLOAT</code> — используется <code>NUMERIC(10,2)</code></li>
<li>✅ Персональные настройки (например бюджет) хранятся в записи соответствующего пользователя</li>
<li>✅ Этот курс объединяет три технологии (HTML/CSS/JS, Flask, Telegram Bot) в одном реальном проекте</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 1: Планирование и repo skeleton
# ════════════════════════════════════════════════════════════════════

# Этот урок посвящён ПЛАНИРОВАНИЮ, а не написанию кода.

db_sxemasi = {
    "users": {
        "id": "SERIAL PRIMARY KEY",
        "ism": "VARCHAR(100)",
        "email": "VARCHAR(255) UNIQUE",
        "parol_hash": "VARCHAR(255)",
        "telegram_chat_id": "BIGINT NULL",
        "link_kodi": "VARCHAR(10) NULL",
        "oylik_byudjet": "NUMERIC(10, 2) NULL",   # ❗ не FLOAT!
    },
    "categories": {
        "id": "SERIAL PRIMARY KEY",
        "nomi": "VARCHAR(100)",
        "user_id": "INTEGER REFERENCES users(id)",
    },
    "expenses": {
        "id": "SERIAL PRIMARY KEY",
        "summa": "NUMERIC(10, 2)",                 # ❗ денежная сумма - точный тип ОБЯЗАТЕЛЕН
        "tavsif": "VARCHAR(200)",
        "sana": "DATE",
        "category_id": "INTEGER REFERENCES categories(id)",
        "user_id": "INTEGER REFERENCES users(id)",
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
}

print(db_sxemasi)

# ─────────────────────────────────────────────────────────────────────
# Структура репозитория (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# moneylog/
#   flask_backend/
#     app/
#       static/       <- vanilla JS/CSS здесь
#       templates/     <- index.html здесь
#       models.py
#       routes.py
#     run.py
#   telegram_bot/
#     bot.py
#   README.md

# ─────────────────────────────────────────────────────────────────────
# Намеренная ошибка - расчёт денег через FLOAT (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# print(0.1 + 0.2)          # 0.30000000000000004 - неточно!
# print(0.1 + 0.2 == 0.3)   # False
"""

EX = {
    4394: {
        "title": "Почему frontend на этот раз не деплоится отдельно?",
        "description": "Почему в MoneyLog vanilla JS frontend обслуживается через Flask, а не отдельно на Vercel/Netlify?",
        "hint": "Для React нужна сборка JSX в JS, а для vanilla JS...",
        "explanation": "Vanilla JS не требует никакого шага сборки (webpack/vite) — браузер может читать .js файл напрямую, поэтому Flask может обслуживать его сам через static/templates.",
    },
    4395: {
        "title": "Правильный тип данных для денежной суммы",
        "description": "Какой тип правильный для хранения денежной суммы (например суммы расхода) в базе данных?",
        "hint": "Попробуйте результат 0.1 + 0.2 == 0.3 с FLOAT.",
        "explanation": "NUMERIC(10,2) (или DECIMAL) точно хранит десятичные числа, FLOAT же, работая в двоичной системе, не может точно представить многие десятичные дроби — это приводит к серьёзным ошибкам в денежных расчётах.",
    },
    4396: {
        "title": "Расположите структуру репозитория MoneyLog в логическом порядке",
        "description": "Расположите соответствующим образом назначение папок в репозитории moneylog/.",
        "hint": "",
        "explanation": "",
    },
    4397: {
        "title": "Результат 0.1 + 0.2 в FLOAT",
        "description": "В Python или JavaScript выражение 0.1 + 0.2 == 0.3 с FLOAT возвращает True или False? (напишите ваш ответ)",
        "hint": "",
        "expected_answer": "False",
    },
    4398: {
        "title": "Почему опасно считать деньги через FLOAT?",
        "description": (
            "Если поле expenses.summa хранится как FLOAT, и добавляются "
            "тысячи записей расходов, а затем вычисляется общая сумма, "
            "к какой проблеме это может привести? Объясните своими "
            "словами."
        ),
        "hint": "FLOAT работает в двоичной системе - может ли она ВСЕГДА точно представить десятичные дроби?",
        "expected_answer": "Тип FLOAT хранит числа в двоичной (binary) системе, и многие простые десятичные дроби, такие как 0.1, невозможно точно представить в этой системе — вместо этого сохраняется очень близкое, но не абсолютно точное значение. Для одного расхода эта разница очень мала и может быть незаметна, но когда добавляются тысячи записей и вычисляется их сумма, эти небольшие ошибки накапливаются, и итоговая сумма может отличаться от ожидаемой точной величины (например на несколько копеек) — это серьёзная, подрывающая доверие проблема в финансовой системе.",
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
        TASK_TITLE_RU = "MoneyLog — repo skeleton и документ схемы БД"
        TASK_DESCRIPTION_RU = (
            "Создайте на GitHub monorepo для проекта MoneyLog (с папками "
            "flask_backend/, telegram_bot/), напишите полноценный README.md и "
            "добавьте в README схему БД для таблиц users/categories/expenses. "
            "Объясните, почему для денежной суммы используется NUMERIC(10,2), "
            "а не FLOAT."
        )
        TASK_REQUIREMENTS_RU = (
            "• На GitHub создан публичный репозиторий с именем 'moneylog'\n"
            "• Присутствуют папки flask_backend/ (с app/static/, app/templates/) и telegram_bot/\n"
            "• README.md: описание проекта, технологии, чеклист статуса\n"
            "• В README.md описаны таблицы users (с telegram_chat_id, link_kodi, "
            "oylik_byudjet), categories, expenses и их связи\n"
            "• В README в 2-3 предложениях объяснено, почему поле summa имеет тип "
            "NUMERIC(10,2), а не FLOAT\n"
            "• Присутствует файл .gitignore (venv, .env, __pycache__ исключены)"
        )
        TASK_TECHNOLOGIES_RU = "Git, GitHub, Markdown, PostgreSQL (проектирование схемы)"
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
