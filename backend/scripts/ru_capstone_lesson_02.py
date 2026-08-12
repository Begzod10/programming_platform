"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=1 (L2)."""
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

LESSON_ID = 734

TITLE_RU = "2-Backend API"

TEXT_RU = """\
<h2>Этап 2: Backend API — CRUD для tasks и categories</h2>

<pre class="mermaid">
flowchart LR
    SCHEMA["Схема из урока 1"] --> TABLES["реальные таблицы PostgreSQL"]
    TABLES --> CRUD["GET/POST/PUT/DELETE /tasks и /categories"]
    CRUD --> JOIN["через JOIN возвращается вместе с именем category"]
</pre>

<p>Схему, нарисованную в уроке 1, теперь превратим в <strong>настоящие</strong> таблицы PostgreSQL и эндпоинты Express. На курсе Node.js/Express вы уже изучили CRUD — на этот раз вы построите его с <strong>двумя связанными ресурсами</strong> (tasks и categories).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание таблиц (по схеме из урока 1)</h4>
<pre><code>-- schema.sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  ism VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  parol_hash VARCHAR(255) NOT NULL,
  yaratilgan_vaqt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  nomi VARCHAR(100) NOT NULL,
  user_id INTEGER REFERENCES users(id)
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  sarlavha VARCHAR(200) NOT NULL,
  matn TEXT,
  bajarilgan BOOLEAN DEFAULT false,
  category_id INTEGER REFERENCES categories(id),   -- ❗ связь из урока 1
  user_id INTEGER REFERENCES users(id),
  yaratilgan_vaqt TIMESTAMP DEFAULT NOW()
);</code></pre>

<h4>БЛОК 2 — GET /tasks: возврат и имени category через JOIN</h4>
<pre><code>const express = require('express');
const pool = require('./db');   // объект pg Pool
const app = express();
app.use(express.json());

app.get('/tasks', async (req, res) => {
  const natija = await pool.query(`
    SELECT tasks.*, categories.nomi AS category_nomi
    FROM tasks
    JOIN categories ON tasks.category_id = categories.id   -- ❗ объединяет 2 таблицы
    ORDER BY tasks.yaratilgan_vaqt DESC
  `);
  res.json(natija.rows);
});

app.post('/tasks', async (req, res) => {
  const { sarlavha, matn, category_id } = req.body;
  if (!sarlavha || !category_id) {
    return res.status(400).json({ xato: "'sarlavha' va 'category_id' majburiy" });
  }
  const natija = await pool.query(
    'INSERT INTO tasks (sarlavha, matn, category_id) VALUES ($1, $2, $3) RETURNING *',
    [sarlavha, matn, category_id]   -- ❗ параметризованный запрос - защита от SQL injection
  );
  res.status(201).json(natija.rows[0]);
});</code></pre>

<h4>БЛОК 3 — удаление category: что будет со связанными tasks?</h4>
<pre><code>app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;

  // ❗ СНАЧАЛА проверяем: есть ли tasks, связанные с этой category?
  const bogliqTasks = await pool.query(
    'SELECT COUNT(*) FROM tasks WHERE category_id = $1', [id]
  );
  if (Number(bogliqTasks.rows[0].count) > 0) {
    return res.status(400).json({
      xato: "Bu kategoriyada vazifalar bor, avval ularni o'chiring yoki boshqa kategoriyaga ko'chiring"
    });
  }

  await pool.query('DELETE FROM categories WHERE id = $1', [id]);
  res.status(204).send();
});</code></pre>

<h3>🐛 Намеренная ошибка — удаление category без проверки связанных tasks</h3>
<pre><code>app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM categories WHERE id = $1', [id]);   // ❌ без проверки!
  res.status(204).send();
});

// Если с этой category связаны существующие tasks:
// ❌ Ошибка: update or delete on table "categories" violates foreign key
//    constraint "tasks_category_id_fkey" on table "tasks"
// (500 Internal Server Error - выдаётся непонятная пользователю ошибка!)</code></pre>

<p><strong>Результат:</strong> при попытке удалить строку из таблицы <code>categories</code>, на которую <strong>всё ещё ссылается</strong> какая-то строка таблицы <code>tasks</code> через <code>category_id</code>, PostgreSQL обнаруживает нарушение <strong>foreign key constraint</strong> и <strong>отклоняет</strong> удаление. Если эта ошибка не перехвачена вручную в Express, она напрямую выдаётся пользователю как <strong>500 Internal Server Error</strong> &mdash; это непонятный и плохой пользовательский опыт. Правильное решение: <strong>перед</strong> удалением проверить наличие связанных строк и вернуть чёткое сообщение об ошибке <code>400</code> (или, в зависимости от проекта, использовать <code>ON DELETE CASCADE</code>/<code>SET NULL</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем используется JOIN?</h4>
<p>В таблице <code>tasks</code> хранится только <code>category_id</code> (число), а не <strong>имя</strong> category. Чтобы показать пользователю на frontend имя category, backend через <code>JOIN</code> объединяет две таблицы и возвращает данные обеих одним запросом &mdash; это предотвращает отправку отдельного запроса category для каждой task (проблема N+1).</p>

<h4>2. Зачем используются параметризованные запросы (<code>$1</code>, <code>$2</code>)?</h4>
<p>Если текст, введённый пользователем, напрямую "приклеить" к SQL-запросу (конкатенация строк), это приводит к уязвимости <strong>SQL injection</strong>. Параметризованные запросы (<code>$1</code>, <code>$2</code>) передают данные пользователя <strong>отдельно</strong>, и PostgreSQL никогда не интерпретирует их как "команду", только как "значение".</p>

<h4>3. Что делает foreign key (<code>category_id INTEGER REFERENCES categories(id)</code>)?</h4>
<p>Это ограничение обеспечивает, что <code>tasks.category_id</code> ссылается <strong>только</strong> на реально существующий <code>categories.id</code> &mdash; попытка создать task с несуществующим category_id выдаст ошибку. Это гарантия <strong>целостности</strong> на уровне базы данных.</p>

<h4>4. Почему перед удалением category нужна проверка?</h4>
<p>Ограничение foreign key автоматически отклоняет удаление, если существуют <strong>связанные</strong> строки &mdash; это сохраняет целостность данных, но сообщение об ошибке непонятно пользователю (сырая ошибка SQL). Backend должен <strong>заранее</strong> проверить эту ситуацию и вернуть <code>400</code> с понятным сообщением.</p>

<h4>5. Когда используются коды статуса 201, 400, 204?</h4>
<p><code>201 Created</code> — когда новый ресурс (task) успешно создан. <code>400 Bad Request</code> — запрос пользователя некорректен (нет обязательного поля, или есть связанные ресурсы). <code>204 No Content</code> — удаление успешно, но данных для возврата нет.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ ER-схема из урока 1 превращена в реальные команды <code>CREATE TABLE</code></li>
<li>✅ <code>JOIN</code> объединяет данные двух связанных таблиц в одном запросе</li>
<li>✅ Параметризованные запросы (<code>$1</code>, <code>$2</code>) защищают от SQL injection</li>
<li>✅ Ограничение foreign key отклоняет удаление при наличии связанных строк</li>
<li>✅ Перед удалением нужно проверить связанность и вернуть понятное сообщение об ошибке</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 2: Backend API - CRUD для tasks и categories
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const pool = require('./db');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) GET /tasks - вместе с именем category через JOIN
// ─────────────────────────────────────────────────────────────────────

app.get('/tasks', async (req, res) => {
  const natija = await pool.query(`
    SELECT tasks.*, categories.nomi AS category_nomi
    FROM tasks
    JOIN categories ON tasks.category_id = categories.id
    ORDER BY tasks.yaratilgan_vaqt DESC
  `);
  res.json(natija.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 2) POST /tasks - валидация + параметризованный запрос
// ─────────────────────────────────────────────────────────────────────

app.post('/tasks', async (req, res) => {
  const { sarlavha, matn, category_id } = req.body;
  if (!sarlavha || !category_id) {
    return res.status(400).json({ xato: "'sarlavha' va 'category_id' majburiy" });
  }
  const natija = await pool.query(
    'INSERT INTO tasks (sarlavha, matn, category_id) VALUES ($1, $2, $3) RETURNING *',
    [sarlavha, matn, category_id]
  );
  res.status(201).json(natija.rows[0]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) DELETE /categories/:id - с проверкой связанных tasks
// ─────────────────────────────────────────────────────────────────────

app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;

  const bogliqTasks = await pool.query(
    'SELECT COUNT(*) FROM tasks WHERE category_id = $1', [id]
  );
  if (Number(bogliqTasks.rows[0].count) > 0) {
    return res.status(400).json({
      xato: "Bu kategoriyada vazifalar bor, avval ularni o'chiring yoki boshqa kategoriyaga ko'chiring"
    });
  }

  await pool.query('DELETE FROM categories WHERE id = $1', [id]);
  res.status(204).send();
});

app.listen(3000, () => console.log('TaskFlow API: http://localhost:3000'));

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - удаление без проверки (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// app.delete('/categories/:id', async (req, res) => {
//   const { id } = req.params;
//   await pool.query('DELETE FROM categories WHERE id = $1', [id]);   // без проверки!
//   res.status(204).send();
// });
// ❌ Если есть связанные tasks: ошибка foreign key constraint, 500 Internal Server Error
"""

TASK_TITLE_RU = "TaskFlow — Backend API (tasks + categories)"

TASK_DESCRIPTION_RU = (
    "На основе схемы из этапа 1 создайте таблицы PostgreSQL (users, "
    "categories, tasks) и постройте на Express полноценный CRUD API для "
    "tasks и categories. GET /tasks должен возвращать и имя category через "
    "JOIN, а DELETE /categories/:id должен проверять наличие связанных tasks."
)

TASK_REQUIREMENTS_RU = (
    "• schema.sql: таблицы users, categories, tasks с правильными foreign key\n"
    "• GET /tasks — возвращает вместе с category_nomi через JOIN\n"
    "• POST /tasks — валидируются sarlavha и category_id, возвращает 201\n"
    "• PUT /tasks/:id — обновляет статус bajarilgan\n"
    "• DELETE /categories/:id — при наличии связанных tasks возвращает ошибку 400, иначе удаляет\n"
    "• Все SQL-запросы параметризованы ($1, $2, ...)\n"
    "• Обновлён чеклист статуса в README.md"
)

TASK_TECHNOLOGIES_RU = "Node.js, Express, PostgreSQL, pg (node-postgres)"

EX = {
    4274: {
        "title": "Зачем используется JOIN в GET /tasks?",
        "description": "В чём причина использования JOIN между таблицами tasks и categories в эндпоинте GET /tasks?",
        "hint": "В таблице tasks есть только category_id (число), не имя.",
        "explanation": "JOIN объединяет таблицы tasks и categories, возвращая одним запросом и данные task, и имя его category — это предотвращает отправку отдельного запроса для каждой task.",
    },
    4275: {
        "title": "Зачем используется параметризованный запрос ($1, $2)?",
        "description": "Зачем в записи pool.query('INSERT ... VALUES ($1, $2, $3)', [sarlavha, matn, category_id]) используются $1, $2, $3?",
        "hint": "Это отличается от прямой \"склейки\" введённого пользователем текста в SQL.",
        "explanation": "Параметризованные запросы передают данные пользователя отдельно, PostgreSQL никогда не интерпретирует их как часть SQL-команды, только как значение — это защищает от SQL injection.",
    },
    4276: {
        "title": "Расположите запрос удаления category в правильном порядке",
        "description": "Расположите процесс правильной (безопасной) работы DELETE /categories/:id.",
        "hint": "",
        "explanation": "",
    },
    4277: {
        "title": "Код статуса при создании нового ресурса",
        "description": "Какой код статуса HTTP должен возвращаться при успешном создании новой task через POST /tasks? (ответьте числом)",
        "hint": "",
        "expected_answer": "201",
    },
    4278: {
        "title": "Почему удаление category без проверки даёт ошибку 500?",
        "description": (
            "Если эндпоинт DELETE /categories/:id, не проверив заранее "
            "наличие связанных tasks, напрямую отправляет DELETE-запрос, "
            "и с этой category связаны существующие tasks, почему это "
            "заканчивается ошибкой 500 Internal Server Error? Объясните "
            "своими словами."
        ),
        "hint": "Как столбец category_id таблицы tasks связан с таблицей categories, и как эта связь влияет на удаление?",
        "expected_answer": "Столбец category_id таблицы tasks — это foreign key, связанный с таблицей categories через REFERENCES. PostgreSQL использует это ограничение для сохранения целостности данных — если с какой-то category всё ещё связаны (ссылающиеся на её id) строки tasks, PostgreSQL вообще не разрешает удалить эту category и возвращает ошибку \"foreign key constraint\". Если код Express не проверяет эту ситуацию заранее и не обрабатывает её сам, эта неперехваченная ошибка напрямую выдаётся пользователю как 500 Internal Server Error — что не объясняет, почему удаление не удалось.",
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
