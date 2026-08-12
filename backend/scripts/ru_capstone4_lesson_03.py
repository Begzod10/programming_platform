"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=2 (L3)."""
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

LESSON_ID = 776

TITLE_RU = "3-PostgreSQL CRUD (типизированные запросы)"

TEXT_RU = """\
<h2>Этап 3: PostgreSQL CRUD — типизированные запросы</h2>

<pre class="mermaid">
flowchart LR
    SQL["SELECT id, title, status FROM issues"] --> ROWS["строки с 3 колонками"]
    ROWS --> CAST["приведены к 'полному' типу Issue как Issue[]"]
    CAST --> USE["вызывается issue.description.length"]
    USE --> CRASH["Runtime: Cannot read properties of undefined"]
</pre>

<p>В курсе Node.js/Express вы уже изучили подключение к PostgreSQL через пакет <code>pg</code> и параметризованные запросы. На этом уроке вы переносите массив в памяти (с этапа 2) в реальную таблицу PostgreSQL. Но на этот раз граница TypeScript проявляется в ещё более тонком месте: даже "официальная", рекомендуемая запись <code>pool.query&lt;Issue&gt;()</code> <strong>не проверяет</strong>, действительно ли результат SQL соответствует интерфейсу.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — настройка pg с TypeScript</h4>
<pre><code># Terminal:
npm install pg
npm install -D @types/pg

// backend/src/db.ts
import { Pool } from 'pg';

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});</code></pre>

<h4>БЛОК 2 — полный CRUD: таблица и параметризованные запросы</h4>
<pre><code>-- schema.sql
CREATE TABLE issues (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'open',
  assignee_id INTEGER,
  reporter_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);</code></pre>
<pre><code>// backend/src/server.ts
app.post('/issues', async (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;
  const result = await pool.query&lt;Issue&gt;(
    `INSERT INTO issues (title, description, reporter_id)
     VALUES ($1, $2, $3) RETURNING *`,
    [title, description, reporterId]
  );
  res.status(201).json(result.rows[0]);
});

app.get('/issues', async (req: Request, res: Response) => {
  const result = await pool.query&lt;Issue&gt;('SELECT * FROM issues ORDER BY created_at DESC');
  res.json(result.rows);   // ❗ SELECT * - все колонки на месте, поэтому это БЕЗОПАСНО
});</code></pre>

<h4>БЛОК 3 — для частичного SELECT создаётся ОТДЕЛЬНЫЙ, более точный тип</h4>
<pre><code>// Для страницы списка полное description не нужно - достаточно 3 колонок.
// Поэтому вместо Issue создаётся НОВЫЙ, более УЗКИЙ интерфейс:
interface IssueSummary {
  id: number;
  title: string;
  status: 'open' | 'in_progress' | 'closed';
}

app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query&lt;IssueSummary&gt;(
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);   // ❗ теперь тип СООТВЕТСТВУЕТ SQL - description вообще не обещан
});</code></pre>

<h3>🐛 Намеренная ошибка — "приведение" частичного SELECT к полному типу Issue</h3>
<pre><code>// Решив "написать быстрее" вместо создания нового интерфейса, разработчик
// использует существующий тип Issue - хотя SQL выбирает только 3 колонки:
app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query&lt;Issue&gt;(          // ❌ Issue требует description, assigneeId и т.д.!
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);
});

// Frontend (на 5-м уроке) получает этот список и пытается показать
// короткий текст для каждого issue:
// issues.map(issue =&gt; issue.description.slice(0, 50))
//
// ❌ TypeError: Cannot read properties of undefined (reading 'slice')
// - потому что description в SQL-результате ВООБЩЕ ОТСУТСТВУЕТ, но
//   TypeScript "ВЕРИЛ", что в Issue description есть.</code></pre>

<p><strong>Результат:</strong> запись <code>pool.query&lt;Issue&gt;(...)</code> — даже сама библиотека <code>pg</code> лишь <strong>указывает</strong> TypeScript "интерпретируй строки результата как этот тип", и не более того. <code>pg</code> <strong>никогда не сравнивает</strong> реальный результат SQL с интерфейсом <code>Issue</code> — такой проверки просто нет. Если SQL-запрос выбирает только <code>id, title, status</code>, но результат "объявлен" как <code>Issue</code> (то есть требующий также <code>description</code>, <code>assigneeId</code>, <code>reporterId</code>, <code>createdAt</code>), TypeScript <strong>полностью примет это во время компиляции</strong> — потому что параметр дженерика — это просто <strong>ярлык</strong>, не связанный с самим текстом SQL. Ошибка проявится только <strong>позже</strong>, когда кто-то обратится к <code>issue.description</code> и попытается работать со значением <code>undefined</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Что на самом деле делает дженерик <code>pool.query&lt;Issue&gt;(...)</code>?</h4>
<p>Это лишь говорит TypeScript "считай массив <code>rows</code> в результате типом <code>Issue[]</code>". Библиотека <code>pg</code> <strong>никак</strong> не сравнивает это с текстом SQL — параметр дженерика и текст SQL-запроса пишутся <strong>независимо</strong> друг от друга.</p>

<h4>2. Какая связь между колонками SQL SELECT и типом TypeScript?</h4>
<p><strong>Никакой.</strong> Это два совершенно разных языка — текст SQL (как строка) и тип TypeScript (структура во время компиляции). Ни один из них не "читает" и не проверяет другой. Их соответствие нужно поддерживать <strong>вручную</strong>, самому разработчику.</p>

<h4>3. Почему особенно опасно совмещать частичный SELECT с приведением к полному типу?</h4>
<p>При использовании <code>SELECT *</code> вероятность ошибки ниже (все колонки присутствуют). Но ради производительности выбирать только нужные колонки (например <code>id, title, status</code>) — хорошая практика. Проблема в том, что когда эта практика (частичный SELECT ради производительности) совмещается с "быстрым" повторным использованием существующего более крупного типа, результат — <strong>несоответствие между SQL и типом</strong>, которое ничто не отлавливает.</p>

<h4>4. Откуда берётся runtime-ошибка <code>undefined.slice()</code>?</h4>
<p>Поскольку SQL не выбрал колонку <code>description</code>, в результирующей строке этого поля <strong>вообще нет</strong> (<code>undefined</code>). Код же, поскольку TypeScript сказал "это <code>Issue</code>, в нём есть <code>description</code>", пишет <code>issue.description.slice(...)</code> — это попытка вызвать метод у <code>undefined</code>, и в JavaScript это сразу вызывает ошибку.</p>

<h4>5. Каково правильное решение этой проблемы?</h4>
<p>Создание <strong>отдельного</strong> интерфейса (например <code>IssueSummary</code>), соответствующего <strong>реальным колонкам</strong>, которые возвращает конкретный SQL-запрос — без "удобного" повторного использования существующего более крупного типа. Это даёт TypeScript <strong>более правдивую</strong> информацию, хотя runtime-гарантии всё равно нет.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Дженерик <code>pool.query&lt;T&gt;()</code> — тоже лишь <strong>ярлык</strong> времени компиляции, не сравнивается с SQL</li>
<li>✅ Между колонками SQL и типом TypeScript нет никакой автоматической связи</li>
<li>✅ Частичный SELECT + приведение к более крупному типу приводит к несоответствию между SQL и типом</li>
<li>✅ Runtime-ошибки вызова метода у <code>undefined</code> часто возникают именно из-за этого несоответствия</li>
<li>✅ Для каждого SQL-запроса безопаснее создавать отдельный (более узкий) интерфейс, соответствующий результату</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 3: PostgreSQL CRUD - типизированные запросы
// ════════════════════════════════════════════════════════════════════

import { Pool } from 'pg';
import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const app = express();
app.use(express.json());

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

// ─────────────────────────────────────────────────────────────────────
// 1) POST /issues - параметризованный INSERT, возвращает полный Issue
// ─────────────────────────────────────────────────────────────────────

app.post('/issues', async (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;
  const result = await pool.query<Issue>(
    `INSERT INTO issues (title, description, reporter_id)
     VALUES ($1, $2, $3) RETURNING *`,
    [title, description, reporterId]
  );
  res.status(201).json(result.rows[0]);
});

// ─────────────────────────────────────────────────────────────────────
// 2) GET /issues - SELECT * - все колонки на месте, БЕЗОПАСНО
// ─────────────────────────────────────────────────────────────────────

app.get('/issues', async (req: Request, res: Response) => {
  const result = await pool.query<Issue>('SELECT * FROM issues ORDER BY created_at DESC');
  res.json(result.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 3) GET /issues/summary - частичный SELECT + ОТДЕЛЬНЫЙ, более узкий тип
// ─────────────────────────────────────────────────────────────────────

interface IssueSummary {
  id: number;
  title: string;
  status: 'open' | 'in_progress' | 'closed';
}

app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query<IssueSummary>(
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - приведение частичного SELECT к Issue (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// app.get('/issues/summary', async (req: Request, res: Response) => {
//   const result = await pool.query<Issue>(          // ❌ Issue требует description!
//     'SELECT id, title, status FROM issues ORDER BY created_at DESC'
//   );
//   res.json(result.rows);
// });
// Позже: issue.description.slice(0, 50) -> TypeError: undefined
"""

EX = {
    4484: {
        "title": "Как дженерик pool.query<Issue>(...) связан с SQL?",
        "description": "В библиотеке pg, когда написано pool.query<Issue>('SELECT ...'), как проверяется дженерик <Issue> относительно текста SQL?",
        "hint": "Параметр дженерика и текст SQL - это два независимо написанных элемента.",
        "explanation": "Дженерик pool.query<Issue>() лишь говорит TypeScript считать результат типом Issue - библиотека pg никогда не сравнивает текст SQL с интерфейсом Issue.",
    },
    4485: {
        "title": "Почему опасно приводить частичный SELECT к полному типу Issue?",
        "description": "Почему проблематично получать результат запроса SELECT id, title, status FROM issues через pool.query<Issue>()?",
        "hint": "Сколько полей требует интерфейс Issue, и сколько выбрал SQL?",
        "explanation": "Интерфейс Issue требует поля вроде description, assigneeId, reporterId, createdAt, но SQL выбрал только id/title/status - в результате эти поля будут undefined, но TypeScript этого не знает, и при последующем обращении к ним возникает runtime-ошибка.",
    },
    4486: {
        "title": "Расположите процесс возникновения ошибки IssueSummary",
        "description": "Расположите процесс от приведения частичного SELECT к типу Issue в GET /issues/summary до появления ошибки на frontend.",
        "hint": "",
        "explanation": "",
    },
    4487: {
        "title": "Правильное решение: что создаётся для частичного SELECT?",
        "description": "Для SQL-запроса, возвращающего только колонки id, title, status, что рекомендуется сделать вместо повторного использования типа Issue? (ответьте одним словом: что создаётся?)",
        "hint": "Что пишется под новым, более узким именем, соответствующим точным колонкам, которые возвращает SQL?",
        "expected_answer": "интерфейс",
    },
    4488: {
        "title": "Почему при использовании SELECT * эта ошибка менее вероятна?",
        "description": (
            "Почему получение результата SELECT * FROM issues через "
            "pool.query<Issue>() безопаснее, чем частичный запрос вроде "
            "SELECT id, title, status? Объясните своими словами."
        ),
        "hint": "Сколько колонок возвращает SELECT *, и сколько полей требует интерфейс Issue - совпадают ли они случайно или всегда?",
        "expected_answer": "SELECT * возвращает ВСЕ колонки таблицы, поэтому если интерфейс Issue соответствует реальным колонкам таблицы, то в результирующей строке действительно будут присутствовать все поля, требуемые Issue (description, assigneeId и т.д.) - совпадение получается случайно, но верно. Частичный же SELECT (например только id, title, status) НАМЕРЕННО возвращает меньше колонок - если этот урезанный результат всё равно приводится к полному типу Issue, возникает несоответствие между типом и реальными данными, потому что SQL и тип TypeScript написаны независимо друг от друга, и никто их не сравнивает.",
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
        TASK_TITLE_RU = "IssueForge — PostgreSQL CRUD (типизированные запросы)"
        TASK_DESCRIPTION_RU = (
            "Перенесите массив в памяти со 2-го этапа в реальную таблицу "
            "PostgreSQL: напишите полный CRUD (GET списка + одного issue, "
            "POST, PUT, DELETE) и параметризованные запросы. Дополнительно "
            "напишите эндпоинт GET /issues/summary с ОТДЕЛЬНЫМ интерфейсом "
            "IssueSummary, НЕ используя повторно тип Issue."
        )
        TASK_REQUIREMENTS_RU = (
            "• schema.sql: таблица issues создана с правильными колонками\n"
            "• GET /issues, GET /issues/:id, POST /issues, PUT /issues/:id, DELETE /issues/:id — все типизированы через pool.query<Issue>()\n"
            "• Все SQL-запросы параметризованы ($1, $2, ...)\n"
            "• GET /issues/summary — возвращает только id/title/status, с ОТДЕЛЬНЫМ интерфейсом IssueSummary (не Issue)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Node.js, Express, TypeScript, PostgreSQL, pg (node-postgres)"
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
