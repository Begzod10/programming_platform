"""Russian translation for Node.js/Express Asoslari, lesson order=4 (R1)."""
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

LESSON_ID = 614

TITLE_RU = "R1-Мини Todo REST API (повторение)"

TEXT_RU = """\
<h2>R1 — Повторение уроков 1-4: Мини Todo REST API</h2>

<p>Объединив всё из уроков 1-4, создадим полноценный Todo REST API: routing, middleware, req.body/статус-коды и структуру проекта с Router — всё вместе.</p>

<h3>Цель проекта</h3>
<ul>
<li><code>routes/todos.js</code> — все route'ы todo в отдельном файле (урок 4)</li>
<li>Middleware логирования — записывает каждый запрос в консоль (урок 2)</li>
<li>Полный CRUD: <code>GET /todos</code>, <code>POST /todos</code>, <code>PUT /todos/:id</code>, <code>DELETE /todos/:id</code> (уроки 1-3)</li>
<li>Валидация и правильные статус-коды (урок 3)</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — middleware логирования</h4>
<p>Напишите middleware, выводящий метод и адрес каждого запроса в консоль, подключите его через <code>app.use()</code> <strong>самым первым</strong> (как в уроке 2).</p>

<h4>Задание 2 — routes/todos.js (Router)</h4>
<p>С помощью <code>express.Router()</code> вынесите все route'ы todo в отдельный модуль, экспортируйте через <code>module.exports</code> (как в уроке 4).</p>

<h4>Задание 3 — полный CRUD</h4>
<p><code>GET /todos</code> — все, <code>POST /todos</code> — добавление нового (201), <code>PUT /todos/:id</code> — переключение статуса <code>bajarildi</code>, <code>DELETE /todos/:id</code> — удаление (204).</p>

<h4>Задание 4 — валидация</h4>
<p>Если в <code>POST /todos</code> поле <code>matn</code> отсутствует или пустое — верните <code>400</code> с понятным сообщением об ошибке (как в уроке 3).</p>

<h3>🐛 Намеренная сложность: порядок middleware</h3>
<p>Если разместить middleware логирования <strong>после</strong> <code>app.use('/todos', todosRouter)</code>, оно будет работать только для запросов, не относящихся к <code>/todos</code> (потому что Router уже отправит ответ раньше). Правильный порядок: middleware всегда регистрируются <strong>до</strong> route'ов, на которые они должны влиять (вспомните урок 2 — Express запускает middleware в порядке написания).</p>

<h3>Стартовый код</h3>
<pre><code>const express = require('express');
const app = express();

// Задание 1: middleware логирования (здесь, ДО route'ов)

app.use(express.json());

// Задание 2: routes/todos.js — создайте Router, подключите здесь
// app.use('/todos', todosRouter);

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>// ─── routes/todos.js ───
const express = require('express');
const todosRouter = express.Router();

let todos = [{ id: 1, matn: 'Изучение Node.js', bajarildi: false }];

todosRouter.get('/', (req, res) =&gt; {
  res.json(todos);
});

todosRouter.post('/', (req, res) =&gt; {
  const { matn } = req.body;
  if (!matn || typeof matn !== 'string' || !matn.trim()) {
    return res.status(400).json({ xato: "'matn' majburiy va bo'sh bo'lmasligi kerak" });
  }
  const yangiTodo = { id: Date.now(), matn, bajarildi: false };
  todos.push(yangiTodo);
  res.status(201).json(yangiTodo);
});

todosRouter.put('/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  const todo = todos.find(t =&gt; t.id === id);
  if (!todo) {
    return res.status(404).json({ xato: 'Todo topilmadi' });
  }
  todo.bajarildi = !todo.bajarildi;
  res.status(200).json(todo);
});

todosRouter.delete('/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  todos = todos.filter(t =&gt; t.id !== id);
  res.status(204).send();
});

module.exports = todosRouter;

// ─── server.js ───
const express = require('express');
const todosRouter = require('./routes/todos');

const app = express();

// Задание 1: middleware логирования — ДО route'ов
app.use((req, res, next) =&gt; {
  console.log(`${req.method} ${req.url}`);
  next();
});

app.use(express.json());
app.use('/todos', todosRouter);

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Уроки 1-4 все вместе: routing, middleware, req.body, Router</li>
<li>✅ Middleware обязательно должны регистрироваться до route'ов</li>
<li>✅ Router — способ вынести CRUD route'ы в отдельный, упорядоченный файл</li>
<li>✅ Правильные статус-коды: 201 (создано), 200 (обновлено), 204 (удалено), 400/404 (ошибка)</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ПОВТОРЕНИЕ 1: Мини Todo REST API (уроки 1-4)
// ════════════════════════════════════════════════════════════════════

// ─── routes/todos.js ───
const express = require('express');
const todosRouter = express.Router();

let todos = [{ id: 1, matn: 'Изучение Node.js', bajarildi: false }];

todosRouter.get('/', (req, res) => {
  res.json(todos);
});

todosRouter.post('/', (req, res) => {
  const { matn } = req.body;
  if (!matn || typeof matn !== 'string' || !matn.trim()) {
    return res.status(400).json({ xato: "'matn' majburiy va bo'sh bo'lmasligi kerak" });
  }
  const yangiTodo = { id: Date.now(), matn, bajarildi: false };
  todos.push(yangiTodo);
  res.status(201).json(yangiTodo);
});

todosRouter.put('/:id', (req, res) => {
  const id = Number(req.params.id);
  const todo = todos.find(t => t.id === id);
  if (!todo) {
    return res.status(404).json({ xato: 'Todo topilmadi' });
  }
  todo.bajarildi = !todo.bajarildi;
  res.status(200).json(todo);
});

todosRouter.delete('/:id', (req, res) => {
  const id = Number(req.params.id);
  todos = todos.filter(t => t.id !== id);
  res.status(204).send();
});

// module.exports = todosRouter;

// ─── server.js ───
const app = express();

// Middleware логирования — регистрируется ДО route'ов
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

app.use(express.json());
app.use('/todos', todosRouter);

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3671: {
        "title": "Где нужно регистрировать middleware?",
        "description": "Чтобы middleware логирования влияло и на route'ы /todos, куда его нужно поместить?",
        "hint": "Express запускает middleware и route'ы в порядке их написания.",
        "explanation": "Express пропускает запрос через middleware и route'ы в порядке написания кода. Если middleware логирования написан после Router, то для запросов /todos Router уже успеет отправить ответ, и до middleware логирования очередь не дойдёт.",
    },
    3672: {
        "title": "Какой статус-код для успешного DELETE?",
        "description": "Какой статус-код нужно вернуть при успешном выполнении DELETE /todos/:id (когда в ответе нет body)?",
        "hint": "Вспомните урок 3: успешно, но без данных для возврата.",
        "explanation": "204 No Content — операция успешна, но в ответе нет данных для возврата. Наиболее подходящий статус-код для DELETE.",
    },
    3673: {
        "title": "Расположите запрос POST /todos в правильном порядке",
        "description": "Упорядочите шаги от момента, когда клиент отправляет новый todo, до момента, когда сервер возвращает ответ.",
        "hint": "Middleware всегда работают перед handler'ом, в порядке написания.",
    },
    3674: {
        "title": "Почему важно использовать Router + порядок middleware + валидацию вместе?",
        "description": (
            "Почему даже в небольшом Todo API важно применять вместе Router "
            "(урок 4), порядок middleware (урок 2) и валидацию (урок 3)? "
            "Какую проблему предотвращает каждый из них? Объясните своими "
            "словами."
        ),
        "expected_answer": "Router упорядочивает код по темам в отдельных файлах, облегчая управление проектом по мере его роста. Правильный порядок регистрации middleware гарантирует, что общие функции — например логирование или, позже, аутентификация — обязательно срабатывают для каждого нужного запроса, иначе они могут остаться незамеченными. Валидация же проверяет ненадёжные данные, пришедшие от клиента, предотвращая запись повреждённых или некорректных данных в базу данных. Используемые вместе, эти три элемента делают код одновременно упорядоченным, безопасным и предсказуемым.",
        "hint": "Подумайте о каждом отдельно: зачем нужен Router, зачем порядок middleware, зачем валидация.",
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
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={"title": TITLE_RU, "text_content": TEXT_RU},
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
