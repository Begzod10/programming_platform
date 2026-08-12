"""Russian translation for Node.js/Express Asoslari, lesson order=11 (R3)."""
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

LESSON_ID = 628

TITLE_RU = "R3-Auth + CRUD полный проект (повторение)"

TEXT_RU = """\
<h2>R3 — Повторение уроков 5-9: Auth + CRUD полный проект</h2>

<p>Объединив все уроки 5-9, создадим полностью аутентифицированный REST API, где каждый пользователь может видеть <strong>только свои собственные</strong> задачи (tasks).</p>

<h3>Цель проекта</h3>
<ul>
<li><code>POST /register</code>, <code>POST /login</code> — bcrypt + JWT (урок 8)</li>
<li><code>authMiddleware</code> — защита всех route'ов под <code>/tasks</code> (урок 9)</li>
<li>Полный CRUD: <code>GET/POST/PUT/DELETE /tasks</code> — <strong>только</strong> строки, принадлежащие <code>req.user.id</code> (уроки 5-6)</li>
<li>Централизованный error middleware (урок 7)</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — register/login</h4>
<p>Таблица <code>users</code>: <code>id</code>, <code>email</code>, <code>parol_hash</code>. При регистрации — <code>bcrypt.hash</code>, при входе — <code>bcrypt.compare</code> + <code>jwt.sign</code>.</p>

<h4>Задание 2 — защита через authMiddleware</h4>
<p>Добавьте <code>authMiddleware</code> ко всем route'ам, связанным с <code>/tasks</code>; он устанавливает <code>req.user = { id: ... }</code>.</p>

<h4>Задание 3 — CRUD, привязанный к пользователю</h4>
<p>Таблица <code>tasks</code>: <code>id</code>, <code>user_id</code>, <code>matn</code>, <code>bajarildi</code>. В каждом запросе <strong>обязательно</strong> добавляйте условие <code>WHERE user_id = $X</code> — иначе пользователь сможет видеть или удалять чужие задачи.</p>

<h4>Задание 4 — централизованная обработка ошибок</h4>
<p>Передавайте все ошибки через <code>next(err)</code>, перехватывайте их в одном месте и возвращайте в едином JSON-формате.</p>

<h3>🐛 Намеренная сложность: забыть условие WHERE user_id (уязвимость IDOR)</h3>
<pre><code>// ❌ ОПАСНО — user_id не проверяется!
app.get('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE id = $1', [req.params.id]);
    // ❌ в WHERE только id, нет user_id!
    if (result.rows.length === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

// Пользователь A вошёл в систему, но отправит /tasks/57 (id
// задачи другого пользователя B), угадав его —
// запрос пройдёт, потому что токен верен, и СЕКРЕТНАЯ
// задача B будет возвращена A!</code></pre>

<p><strong>Результат:</strong> это уязвимость безопасности, называемая <strong>IDOR</strong> (Insecure Direct Object Reference). Одной лишь верности токена недостаточно — <strong>каждый запрос обязан проверять</strong>, что запрошенные данные действительно принадлежат этому пользователю. Правильная версия: <code>WHERE id = $1 AND user_id = $2</code> с <code>[req.params.id, req.user.id]</code>.</p>

<h3>Стартовый код</h3>
<pre><code>const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());
// const pool = require('./db');
// const authMiddleware = require('./middleware/auth');

// Задание 1: POST /register, POST /login

// Задания 2-3: route'ы /tasks, с authMiddleware, ВСЕГДА
// с WHERE user_id = $X

// Задание 4: централизованный error middleware (в конце файла)

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>app.post('/register', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) { const e = new Error("'email' va 'parol' majburiy"); e.status = 400; throw e; }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.post('/login', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const e = new Error("Email yoki parol noto'g'ri"); e.status = 401; throw e;
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) { next(err); }
});

app.get('/tasks', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE user_id = $1 ORDER BY id', [req.user.id]);
    res.json(result.rows);
  } catch (err) { next(err); }
});

app.post('/tasks', authMiddleware, async (req, res, next) =&gt; {
  try {
    const { matn } = req.body;
    if (!matn) { const e = new Error("'matn' majburiy"); e.status = 400; throw e; }
    const result = await pool.query(
      'INSERT INTO tasks (user_id, matn, bajarildi) VALUES ($1, $2, false) RETURNING *',
      [req.user.id, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.put('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query(
      'UPDATE tasks SET bajarildi = NOT bajarildi WHERE id = $1 AND user_id = $2 RETURNING *',
      [req.params.id, req.user.id] // ❗ оба условия — нельзя изменить чужую задачу
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

app.delete('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.status(204).send();
  } catch (err) { next(err); }
});

app.use((err, req, res, next) =&gt; {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Уроки 5-9 все вместе: DB, CRUD, валидация, обработка ошибок, JWT, protected routes</li>
<li>✅ Верность токена не гарантирует право владения данными — каждый запрос должен также проверять <code>user_id</code></li>
<li>✅ IDOR — одна из самых распространённых, но легко предотвратимых уязвимостей безопасности</li>
<li>✅ <code>WHERE id = $1 AND user_id = $2</code> — стандартный паттерн CRUD, привязанного к пользователю</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ПОВТОРЕНИЕ 3: Auth + CRUD полный проект (уроки 5-9)
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());
// const pool = require('./db');
// const authMiddleware = require('./middleware/auth'); // как в уроке 9

app.post('/register', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) { const e = new Error("'email' va 'parol' majburiy"); e.status = 400; throw e; }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.post('/login', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const e = new Error("Email yoki parol noto'g'ri"); e.status = 401; throw e;
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) { next(err); }
});

app.get('/tasks', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE user_id = $1 ORDER BY id', [req.user.id]);
    res.json(result.rows);
  } catch (err) { next(err); }
});

app.post('/tasks', authMiddleware, async (req, res, next) => {
  try {
    const { matn } = req.body;
    if (!matn) { const e = new Error("'matn' majburiy"); e.status = 400; throw e; }
    const result = await pool.query(
      'INSERT INTO tasks (user_id, matn, bajarildi) VALUES ($1, $2, false) RETURNING *',
      [req.user.id, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.put('/tasks/:id', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query(
      'UPDATE tasks SET bajarildi = NOT bajarildi WHERE id = $1 AND user_id = $2 RETURNING *',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

app.delete('/tasks/:id', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.status(204).send();
  } catch (err) { next(err); }
});

// ─────────────────────────────────────────────────────────────────────
// Намеренная ошибка — в WHERE нет user_id, IDOR (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/tasks-xato/:id', authMiddleware, async (req, res, next) => {
  const result = await pool.query('SELECT * FROM tasks WHERE id = $1', [req.params.id]);
  // ❌ user_id не проверяется — любой пользователь может увидеть любую задачу!
  res.json(result.rows[0]);
});
*/

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3727: {
        "title": "Почему в каждом запросе /tasks нужен WHERE user_id?",
        "description": "Почему в запросах GET/PUT/DELETE /tasks/:id нужно добавлять user_id к условию WHERE?",
        "hint": "Верность токена не означает право владения данными.",
        "explanation": "authMiddleware определяет только то, кто является пользователем. Проверка того, что данные действительно принадлежат этому пользователю, — отдельная задача каждого запроса, выполняемая через WHERE user_id = $X.",
    },
    3728: {
        "title": "Что такое IDOR?",
        "description": "Что означает уязвимость IDOR (Insecure Direct Object Reference)?",
        "hint": "Токен верен, но никто не проверил владение запрошенным ресурсом.",
        "explanation": "IDOR — уязвимость, при которой корректно аутентифицированный (с токеном) пользователь может, просто изменив ID, получить доступ к данным другого пользователя или изменить их, потому что сервер не проверяет, действительно ли эти данные принадлежат запрашивающему.",
    },
    3729: {
        "title": "Расположите поток запроса PUT /tasks/:id в правильном порядке",
        "description": "Упорядочите проверки, происходящие при обновлении пользователем своей задачи.",
        "hint": "Сначала определяется, кто пользователь, затем проверяется владение и запись в DB.",
    },
    3730: {
        "title": "Какую роль играет каждый из уроков 5-9 в предотвращении IDOR?",
        "description": (
            "Как подключение к DB, CRUD, валидация/обработка ошибок, JWT-"
            "аутентификация и protected routes — каждый из них — играют роль "
            "в предотвращении уязвимости вроде IDOR? Что произойдёт, если "
            "чего-то из этого не хватает (например, есть только "
            "authMiddleware, но нет WHERE user_id)? Объясните своими "
            "словами."
        ),
        "expected_answer": "authMiddleware (JWT-аутентификация) подтверждает только то, от какого пользователя пришёл запрос — это проверка «личности». Но это не гарантирует, что запрошенные данные принадлежат именно этому пользователю — это проверка «владения», которая должна выполняться в самих CRUD-запросах (WHERE user_id = $X). Если есть только аутентификация, но нет проверки владения, любой вошедший в систему пользователь сможет увидеть или изменить данные другого человека, угадав ID — это и есть уязвимость IDOR. Поэтому аутентификация и проверка владения должны присутствовать вместе в каждом защищённом route.",
        "hint": "Аутентификация знает «кто», проверка владения знает «на что есть право» — это разные вещи.",
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
