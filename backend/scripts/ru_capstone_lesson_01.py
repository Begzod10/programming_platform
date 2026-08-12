"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=0 (L1)."""
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

LESSON_ID = 732

TITLE_RU = "1-Планирование и repo skeleton"

TEXT_RU = """\
<h2>TaskFlow — полноценный full-stack проект за 6 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> API["2-Backend API"]
    API --> FE["3-React frontend"]
    FE --> AUTH["4-Аутентификация"]
    AUTH --> SEARCH["5-Поиск/фильтр"]
    SEARCH --> DEPLOY["6-Deploy"]
</pre>

<p>В этом курсе вы объедините всё, что изучили <strong>отдельно</strong> на курсах React и Node.js/Express, в <strong>один настоящий проект</strong>: <strong>TaskFlow</strong> — командный менеджер задач. Каждый урок &mdash; очередной этап этого одного проекта, и каждый этап оценивается как <strong>настоящее задание проекта</strong> (через GitHub-репозиторий + описание).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — структура репозитория: monorepo</h4>
<pre><code># Для TaskFlow используем две папки в одном репозитории - подход "monorepo"
taskflow/
  backend/          # Express + PostgreSQL (строится в уроках 2-4)
    package.json
    server.js
  frontend/          # React + Redux Toolkit (строится в уроке 3)
    package.json
    src/
  README.md          # описание проекта, инструкция по запуску
  .gitignore          # исключает node_modules, .env и подобные файлы

# Почему monorepo? В небольших командных проектах удобнее видеть
# изменения frontend и backend В ОДНОМ месте, легче синхронизировать версии.</code></pre>

<h4>БЛОК 2 — проектирование схемы БД ДО написания кода</h4>
<pre><code># Основные таблицы для TaskFlow (на уровне ER-диаграммы, ещё не SQL):
#
# users        (id, ism, email, parol_hash, yaratilgan_vaqt)
# categories   (id, nomi, user_id -> users.id)
# tasks        (id, sarlavha, matn, bajarilgan, category_id -> categories.id,
#               user_id -> users.id, yaratilgan_vaqt)
#
# Связи:
# - Один user -> много categories (один ко многим)
# - Один user -> много tasks (один ко многим)
# - Одна category -> много tasks (один ко многим)

# Эта схема превратится в реальные таблицы PostgreSQL в уроке 2.</code></pre>

<h4>БЛОК 3 — README.md: "дверь" проекта</h4>
<pre><code># README.md
# TaskFlow

## О проекте
Командный менеджер задач - React + Node/Express + PostgreSQL.

## Установка
1. `cd backend && npm install`
2. Создайте файл `.env` (скопируйте из `.env.example`)
3. `npm run dev`

## Технологии
- Backend: Node.js, Express, PostgreSQL
- Frontend: React, Redux Toolkit

## Статус
- [x] Планирование и repo skeleton
- [ ] Backend API
- [ ] React frontend
- [ ] Аутентификация
- [ ] Поиск и фильтрация
- [ ] Deploy</code></pre>

<h3>🐛 Намеренная сложность: попытка сразу писать код без схемы БД</h3>
<p>Многие начинающие разработчики откладывают проектирование схемы БД "на потом" и сразу начинают писать маршруты Express или компоненты React. Это приводит к следующей проблеме:</p>
<pre><code>// Когда вы начинаете писать backend в уроке 2:
app.post('/tasks', async (req, res) => {
  // вопрос: какому user принадлежит task? нужна ли category?
  // Если схема заранее не определена, здесь начинаются КОЛЕБАНИЯ,
  // и позже потребуется ПЕРЕДЕЛЫВАТЬ структуру таблиц (миграция)
});</code></pre>
<p><strong>Результат:</strong> если схема БД (таблицы, столбцы, связи) <strong>не определена заранее</strong>, во время написания backend-кода постоянно возникают вопросы вроде "нужно ли это поле?", "как это связано?" &mdash; это тратит время впустую и часто вынуждает <strong>позже переделывать миграцию</strong>. Правильный порядок: <strong>сначала</strong> нарисовать схему на бумаге (или как диаграмму), <strong>затем</strong> писать код.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему выбран monorepo (один репозиторий, две папки)?</h4>
<p>Для небольших full-stack проектов, создаваемых одним разработчиком (или небольшой командой), monorepo удобен: легче отслеживать изменения frontend и backend <strong>в одном месте</strong>, синхронизировать версии. В крупных компаниях часто используют отдельные репозитории, но это другой вопрос.</p>

<h4>2. Почему схема БД проектируется в первую очередь?</h4>
<p>Почти <strong>всё</strong> &mdash; эндпоинты backend, форма данных на frontend, аутентификация &mdash; зависит от схемы БД. Если схема неясна, на каждом следующем этапе придётся принимать решения заново. Проектирование схемы заранее ускоряет все последующие этапы.</p>

<h4>3. Почему важен README.md?</h4>
<p>README &mdash; "дверь" проекта: когда другой разработчик (или проверяющий) видит проект впервые, именно отсюда он узнаёт, <strong>как запустить</strong> проект, какие технологии использованы и каков текущий статус. Это будет очень важно и при деплое в уроке 6.</p>

<h4>4. Чем "задание" в этом курсе отличается от предыдущих курсов?</h4>
<p>В предыдущих курсах каждый урок был <strong>самостоятельной</strong> темой. Здесь же каждый урок &mdash; следующий этап <strong>одного, продолжающегося</strong> проекта &mdash; вы каждый раз отправляете ссылку на <strong>тот же</strong> (обновлённый) GitHub-репозиторий, и к концу урока 6 проект должен стать <strong>полностью развёрнутым</strong> приложением.</p>

<h4>5. Зачем нужен .gitignore?</h4>
<p><code>.gitignore</code> определяет, что файлы вроде <code>node_modules</code> (очень большой, можно переустановить) и <code>.env</code> (секретные ключи) <strong>не попадают</strong> в репозиторий. Добавление их в репозиторий излишне увеличивает его размер и (если это <code>.env</code>) создаёт <strong>риск раскрытия секретных данных</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Monorepo — хранение frontend+backend небольшого full-stack проекта в одном репозитории</li>
<li>✅ Схема БД должна проектироваться <strong>до</strong> написания кода</li>
<li>✅ README.md — показывает инструкцию по запуску и текущий статус проекта</li>
<li>✅ В этом курсе каждый урок — этап одного продолжающегося проекта, а не самостоятельная тема</li>
<li>✅ <code>.gitignore</code> исключает из репозитория такие файлы, как <code>node_modules</code>/<code>.env</code></li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 1: Планирование и repo skeleton
// ════════════════════════════════════════════════════════════════════

// Этот урок посвящён ПЛАНИРОВАНИЮ, а не написанию кода.
// Ниже - "бумажное" представление схемы БД для TaskFlow в виде
// JavaScript-объекта (ещё не настоящий SQL/миграция - это будет в уроке 2):

const dbSxemasi = {
  users: {
    id: 'SERIAL PRIMARY KEY',
    ism: 'VARCHAR(100)',
    email: 'VARCHAR(255) UNIQUE',
    parol_hash: 'VARCHAR(255)',
    yaratilgan_vaqt: 'TIMESTAMP DEFAULT NOW()',
  },
  categories: {
    id: 'SERIAL PRIMARY KEY',
    nomi: 'VARCHAR(100)',
    user_id: 'INTEGER REFERENCES users(id)',
  },
  tasks: {
    id: 'SERIAL PRIMARY KEY',
    sarlavha: 'VARCHAR(200)',
    matn: 'TEXT',
    bajarilgan: 'BOOLEAN DEFAULT false',
    category_id: 'INTEGER REFERENCES categories(id)',
    user_id: 'INTEGER REFERENCES users(id)',
    yaratilgan_vaqt: 'TIMESTAMP DEFAULT NOW()',
  },
};

console.log(dbSxemasi);

// ─────────────────────────────────────────────────────────────────────
// Структура репозитория (в комментарии - структура папок/файлов, не код)
// ─────────────────────────────────────────────────────────────────────

// taskflow/
//   backend/
//   frontend/
//   README.md
//   .gitignore
"""

TASK_TITLE_RU = "TaskFlow — repo skeleton и документ схемы БД"

TASK_DESCRIPTION_RU = (
    "Создайте на GitHub monorepo для проекта TaskFlow (с папками backend/ и "
    "frontend/), напишите полноценный README.md и добавьте в README схему БД "
    "(в виде ER-диаграммы или текста) для таблиц users/categories/tasks. Этот "
    "проект будет продолжен на этом же репозитории в следующих 5 этапах."
)

TASK_REQUIREMENTS_RU = (
    "• На GitHub создан публичный репозиторий с именем 'taskflow'\n"
    "• Присутствуют папки backend/ и frontend/ (пустые или с package.json)\n"
    "• README.md: описание проекта, список технологий, чеклист статуса\n"
    "• В README.md описаны таблицы users/categories/tasks и связи между ними "
    "(в виде изображения ER-диаграммы или в текстовом/табличном виде)\n"
    "• Присутствует файл .gitignore (node_modules, .env исключены)"
)

TASK_TECHNOLOGIES_RU = "Git, GitHub, Markdown, PostgreSQL (проектирование схемы)"

EX = {
    4264: {
        "title": "Почему выбран monorepo?",
        "description": "Почему для TaskFlow выбраны папки backend/ и frontend/ в одном репозитории (monorepo)?",
        "hint": "Это вопрос удобства для небольшой команды/одного разработчика.",
        "explanation": "Monorepo облегчает отслеживание изменений frontend и backend в одном месте и синхронизацию версий в небольших full-stack проектах.",
    },
    4265: {
        "title": "Когда должна проектироваться схема БД?",
        "description": "Когда должна быть определена схема БД TaskFlow (таблицы users, categories, tasks)?",
        "hint": "Почти всё зависит от этой схемы.",
        "explanation": "Так как схема БД является основой для эндпоинтов backend и формы данных frontend, она должна быть чётко спроектирована до написания кода.",
    },
    4266: {
        "title": "Расположите связи TaskFlow",
        "description": "Расположите в логическом порядке направление связи между таблицами users, categories, tasks.",
        "hint": "",
        "explanation": "",
    },
    4267: {
        "title": "Файл/папка, обязательные для .gitignore",
        "description": "Напишите имя файла, хранящего секретные ключи, который НИКОГДА не должен попадать в репозиторий (например: .env).",
        "hint": "Этот файл хранит переменные окружения.",
        "expected_answer": ".env",
    },
    4268: {
        "title": "Почему написание кода без схемы БД создаёт проблемы позже?",
        "description": (
            "Если разработчик, не спроектировав заранее схему БД, сразу "
            "начинает писать маршруты Express, к каким проблемам это может "
            "привести позже? Объясните своими словами."
        ),
        "hint": "Какие решения приходится принимать в спешке во время написания backend-кода, если схема неясна?",
        "expected_answer": "Если схема БД не определена заранее, во время написания backend-кода часто возникают вопросы вроде \"нужно ли это поле\", \"как эта таблица связана с другой\", и разработчик вынужден принимать эти решения в спешке, прямо в процессе написания кода. Это не только тратит время впустую, но и часто вынуждает позже (например, когда нужен новый столбец или связь) переделывать миграцию существующих таблиц, а иногда переписывать уже написанный код — это требует значительно больше времени и усилий, чем если бы схема была нарисована заранее.",
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
