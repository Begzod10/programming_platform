"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=5 (L6, CAPSTONE finale)."""
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

LESSON_ID = 742

TITLE_RU = "6-Полировка и Deploy (финал CAPSTONE)"

TEXT_RU = """\
<h2>Этап 6 (финал CAPSTONE): Полировка и Deploy</h2>

<pre class="mermaid">
flowchart LR
    LOCAL["Локально: localhost:3000/3001"] --> DEPLOY["Deploy: настоящие домены"]
    DEPLOY --> CORS_CHECK{"CORS origin настроен на production?"}
    CORS_CHECK -->|нет| FAIL["Ошибка CORS в production - даже если локально работало!"]
    CORS_CHECK -->|да| LIVE["TaskFlow работает вживую"]
</pre>

<p>Все функции TaskFlow готовы &mdash; теперь выведем проект в <strong>настоящий интернет</strong>. Этот этап &mdash; финальное задание CAPSTONE курса: проект должен быть сдан <strong>развёрнутым, с рабочей ссылкой</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — переменные окружения для production</h4>
<pre><code># backend/.env.example (без реальных значений, только образец)
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
JWT_SECRET=juda-uzun-tasodifiy-maxfiy-satr
PORT=3000
FRONTEND_URL=https://taskflow-frontend.vercel.app   # ❗ адрес production frontend

# frontend/.env.production
REACT_APP_API_URL=https://taskflow-backend.onrender.com   # ❗ адрес production backend</code></pre>

<h4>БЛОК 2 — адаптация CORS к production-адресу</h4>
<pre><code>// backend/server.js
const cors = require('cors');

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',   // ❗ меняется в зависимости от окружения
}));

// В разработке: FRONTEND_URL не задан -> используется localhost:3001
// В production: FRONTEND_URL=https://taskflow-frontend.vercel.app -> разрешён этот адрес</code></pre>

<h4>БЛОК 3 — шаги деплоя и финальный README</h4>
<pre><code># Деплой backend (например Render/Railway):
# 1. Подключить GitHub-репозиторий к платформе
# 2. Настроить переменные окружения (из .env) в панели платформы
# 3. Создать базу данных PostgreSQL на этой же платформе
# 4. Деплой - backend запускается на https://taskflow-backend.onrender.com

# Деплой frontend (например Vercel/Netlify):
# 1. Подключить GitHub-репозиторий, указать root directory как frontend/
# 2. Настроить REACT_APP_API_URL на адрес production backend
# 3. Деплой - frontend запускается на https://taskflow-frontend.vercel.app

# Финальный статус README.md:
## Рабочая ссылка
- Frontend: https://taskflow-frontend.vercel.app
- Backend API: https://taskflow-backend.onrender.com

## Статус
- [x] Все 6 этапов завершены ✅</code></pre>

<h3>🐛 Намеренная ошибка — забыли обновить CORS origin на production</h3>
<pre><code>// backend/server.js - всё ещё с жёстко прописанным localhost:
app.use(cors({
  origin: 'http://localhost:3001',   // ❌ В production ЭТОГО АДРЕСА НЕ СУЩЕСТВУЕТ!
}));

// После деплоя:
// - Backend: https://taskflow-backend.onrender.com (работает)
// - Frontend: https://taskflow-frontend.vercel.app (открывается)
// - Когда frontend отправляет запрос backend:
// ❌ Ошибка CORS - потому что backend всё ещё разрешает ТОЛЬКО localhost:3001,
//    а НЕ https://taskflow-frontend.vercel.app!</code></pre>

<p><strong>Результат:</strong> настройка CORS, <strong>идеально</strong> работавшая в локальной среде, если значение <code>origin</code> было <strong>жёстко прописано</strong> (<code>localhost:3001</code>), <strong>перестаёт работать</strong> в production &mdash; потому что развёрнутый frontend находится на совершенно другом домене (<code>https://taskflow-frontend.vercel.app</code>), а backend всё ещё разрешает только <code>localhost</code>. Это классическая проблема деплоя "работает локально, не работает в production" &mdash; решение: настроить <code>origin</code> через <strong>переменную окружения</strong> (продолжение принципа <code>.env</code> из урока 3).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему создаётся .env.example, а не .env?</h4>
<p><code>.env</code> содержит реальные секретные значения (пароли, токены) и <strong>никогда</strong> не должен добавляться в репозиторий (вспомните <code>.gitignore</code> из урока 1). <code>.env.example</code> же показывает только <strong>какие</strong> переменные нужны (без значений) &mdash; другой разработчик (или проверяющий), клонировав проект, знает, какой <code>.env</code> нужно создать.</p>

<h4>2. Почему backend и frontend деплоятся на отдельные платформы?</h4>
<p>Backend (сервер Node.js + PostgreSQL) и frontend (статичная сборка React) требуют <strong>разных</strong> ресурсов. Такие платформы, как Render/Railway, специализируются на backend, а Vercel/Netlify &mdash; на статичном frontend, поэтому часто удобнее размещать их раздельно.</p>

<h4>3. Почему CORS origin должен настраиваться через переменную окружения?</h4>
<p>В среде разработки и production адрес frontend <strong>совершенно разный</strong> &mdash; <code>localhost:3001</code> и <code>https://taskflow-frontend.vercel.app</code>. Если это значение жёстко прописано в коде, оно <strong>не может</strong> правильно работать в обеих средах одновременно. Настройка через переменную окружения обеспечивает, что один и тот же код правильно работает в обеих средах.</p>

<h4>4. Почему эта проблема "работает локально, не работает в production" так распространена?</h4>
<p>Разработчик часто тестирует только в <strong>локальной</strong> среде, и там всё (CORS, адрес API) работает правильно, так как все значения соответствуют <code>localhost</code>. Только после деплоя, при тестировании с <strong>реальными</strong> доменами, становится ясно, что жёстко прописанные значения <code>localhost</code> являются проблемой.</p>

<h4>5. Почему важен финальный README?</h4>
<p>Это &mdash; "финальная презентация" проекта: рабочие ссылки (frontend, backend), технологии и чеклист, показывающий выполнение всех 6 этапов. Это позволяет проверяющему (или будущему работодателю) <strong>быстро</strong> понять и протестировать проект.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>.env.example</code> показывает, какие переменные окружения нужны, без секретных значений</li>
<li>✅ Backend и frontend обычно деплоятся на отдельные, специализированные платформы</li>
<li>✅ CORS origin должен настраиваться через переменную окружения, а не прописываться жёстко</li>
<li>✅ "Работает локально, не работает в production" — обычно из-за жёстко прописанных значений localhost</li>
<li>✅ Финальный README показывает текущее рабочее состояние проекта и проделанную работу</li>
</ul>

<h3>🎉 Поздравляем!</h3>
<p>Вы построили TaskFlow с пустого репозитория этапа 1 до схемы БД, backend API, React frontend, аутентификации, поиска/фильтра и, наконец, <strong>настоящего деплоя</strong>. Это был опыт объединения всего, что вы изучили отдельно на курсах React и Node.js/Express, в <strong>один работающий, живой проект</strong>.</p>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 6 (ФИНАЛ CAPSTONE): Полировка и Deploy
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/.env.example (в комментарии - образец, без реальных значений)
// ─────────────────────────────────────────────────────────────────────

// DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
// JWT_SECRET=juda-uzun-tasodifiy-maxfiy-satr
// PORT=3000
// FRONTEND_URL=https://taskflow-frontend.vercel.app

// frontend/.env.production
// REACT_APP_API_URL=https://taskflow-backend.onrender.com

// ─────────────────────────────────────────────────────────────────────
// 2) backend/server.js - настройка CORS через переменную окружения
// ─────────────────────────────────────────────────────────────────────

const cors = require('cors');
const express = require('express');
const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
}));

app.listen(process.env.PORT || 3000, () => {
  console.log('TaskFlow API ishga tushdi');
});

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - жёстко прописанный CORS origin (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// app.use(cors({
//   origin: 'http://localhost:3001',   // в production этого адреса не существует!
// }));
// ❌ В production: ошибка CORS, так как frontend на совершенно другом домене
"""

TASK_TITLE_RU = "TaskFlow — финал CAPSTONE: полностью развёрнутый проект"

TASK_DESCRIPTION_RU = (
    "Разверните TaskFlow на реальном хостинге (например Render/Railway для "
    "backend, Vercel/Netlify для frontend). Адаптируйте CORS origin и адрес "
    "API к production через переменные окружения. Обновите README.md с "
    "рабочими ссылками и финальным статусом."
)

TASK_REQUIREMENTS_RU = (
    "• Backend работает на реальном хостинге (связан с репозиторием из github_url)\n"
    "• Frontend работает на реальном хостинге, развёрнут\n"
    "• CORS origin правильно настроен на домен production frontend (localhost не прописан жёстко)\n"
    "• Адрес API во frontend настроен на домен production backend\n"
    "• Регистрация, вход, добавление/удаление задач, поиск — всё работает на живом сайте\n"
    "• README.md: рабочие ссылки (frontend + backend), технологии, чеклист завершения 6/6 этапов\n"
    "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
    "репозитория (backend + frontend), отдельное поле live_demo_url больше не обязательно"
)

TASK_TECHNOLOGIES_RU = "Render/Railway, Vercel/Netlify, environment variables, CORS"

EX = {
    4314: {
        "title": "Зачем нужен .env.example?",
        "description": "Для чего в основном добавляется в репозиторий файл .env.example (не реальный .env)?",
        "hint": "Вспомните тему .gitignore из урока 1.",
        "explanation": ".env.example показывает, какие переменные окружения нужны (без значений), без реальных секретных данных — другой разработчик, клонировав проект, знает, какой .env нужно создать.",
    },
    4315: {
        "title": "Почему CORS origin должен настраиваться через переменную окружения?",
        "description": "Почему cors({ origin: process.env.FRONTEND_URL }) на backend лучше, чем жёстко прописанный origin?",
        "hint": "localhost:3001 и https://taskflow-frontend.vercel.app - оба должны работать правильно.",
        "explanation": "Так как адрес frontend совершенно разный в разработке и production, настройка CORS origin через переменную окружения позволяет одному и тому же коду правильно работать в обеих средах.",
    },
    4316: {
        "title": "Расположите процесс деплоя TaskFlow",
        "description": "Расположите общий процесс деплоя backend и frontend.",
        "hint": "",
        "explanation": "",
    },
    4317: {
        "title": "Переменная окружения для настройки CORS origin",
        "description": "Из какой переменной окружения backend в L6_CODE считывает CORS origin? (напишите название)",
        "hint": "",
        "expected_answer": "FRONTEND_URL",
    },
    4318: {
        "title": "Почему возникает проблема \"работает локально, не работает в production\"?",
        "description": (
            "Если на backend жёстко прописано cors({ origin: "
            "'http://localhost:3001' }) (не через переменную окружения), "
            "и проект идеально работал локально, почему после деплоя "
            "возникает ошибка CORS? Объясните своими словами."
        ),
        "hint": "Одинаков ли адрес frontend в локальной среде и в production?",
        "expected_answer": "В локальной среде frontend действительно работает на адресе http://localhost:3001, поэтому жёстко прописанный CORS origin совпадает, и всё работает идеально. Но после деплоя frontend размещается на совершенно другом, реальном домене (например https://taskflow-frontend.vercel.app). Код backend же всё ещё написан так, чтобы разрешать только localhost:3001, поэтому он \"не узнаёт\" запросы, пришедшие с реального домена frontend в production, и отклоняет их — это и вызывает классическую проблему \"работает локально, не работает в production\". Решение — настроить значение origin через переменную окружения, чтобы оно принимало подходящее значение в каждой среде.",
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
