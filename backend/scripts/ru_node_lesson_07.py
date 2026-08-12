"""Russian translation for Node.js/Express Asoslari, lesson order=8 (L7)."""
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

LESSON_ID = 622

TITLE_RU = "7-Валидация и централизованная обработка ошибок"

TEXT_RU = """\
<h2>Валидация и централизованная обработка ошибок</h2>

<pre class="mermaid">
flowchart LR
    R["Route handler"] -->|next(err)| EH["Error middleware (4 аргумента!)"]
    EH --> C["JSON-ответ единого формата"]
</pre>

<p>До урока 6 в каждом route был свой <code>try/catch</code> и свой <code>res.status(...).json({...})</code> — это приводит к дублированию. В Express есть <strong>централизованный error middleware</strong>: позволяет обрабатывать все ошибки в одном месте, в едином формате.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — передача ошибки через next(err)</h4>
<pre><code>app.get('/users/:id', async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      const err = new Error('Foydalanuvchi topilmadi');
      err.status = 404;
      return next(err); // ❗ не res.json() — передаём через next(err)
    }
    res.json(result.rows[0]);
  } catch (err) {
    next(err); // ❗ неожиданные ошибки тоже через next()
  }
});</code></pre>

<h4>БЛОК 2 — централизованный error middleware (4 аргумента!)</h4>
<pre><code>// Этот middleware пишется ПОСЛЕ ВСЕХ route'ов, в конце файла
app.use((err, req, res, next) =&gt; { // ❗ именно 4 аргумента — по ним Express его распознаёт
  console.error(err.message);
  const status = err.status || 500;
  res.status(status).json({
    xato: {
      xabar: err.message || 'Server xatosi',
      status,
    },
  });
});</code></pre>

<h4>БЛОК 3 — вспомогательная функция валидации</h4>
<pre><code>function validateNote(body) {
  const { sarlavha, matn } = body;
  if (!sarlavha || typeof sarlavha !== 'string') {
    const err = new Error("'sarlavha' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
  if (!matn || typeof matn !== 'string') {
    const err = new Error("'matn' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
}

app.post('/notes', async (req, res, next) =&gt; {
  try {
    validateNote(req.body); // при ошибке — throw, catch её перехватит
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [req.body.sarlavha, req.body.matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h3>🐛 Намеренная ошибка — 3 аргумента в error middleware</h3>
<pre><code>// ❌ только 3 аргумента — Express считает это ОБЫЧНЫМ middleware, а НЕ error handler'ом!
app.use((req, res, next) =&gt; {
  console.error('Xato yuz berdi');
  res.status(500).json({ xato: 'Server xatosi' });
});</code></pre>

<p><strong>Результат:</strong> Express определяет error middleware только по наличию <strong>ровно 4 аргументов</strong> (<code>err, req, res, next</code>) — это строгое правило, а не по комментарию или названию. Версия с 3 аргументами воспринимается как обычный middleware и вообще не срабатывает при вызове <code>next(err)</code>. В результате ошибка «не перехватывается», и клиенту возвращается стандартная, не-JSON страница ошибки Express.</p>

<h3>Теперь объясним</h3>

<h4>1. Разница между next(err) и next()</h4>
<p><code>next()</code> без аргумента — Express переходит к следующему обычному middleware/route. <code>next(err)</code> с аргументом — Express <strong>пропускает</strong> обычные middleware и сразу переходит к error middleware.</p>

<h4>2. Почему error middleware пишется в конце?</h4>
<p>Express запускает middleware в порядке написания. Error middleware должен быть написан после всех route'ов — иначе он не сможет перехватывать ошибки из route'ов, которые ещё не были зарегистрированы.</p>

<h4>3. Почему важен единый формат ошибки?</h4>
<p>Если каждый route возвращает ошибку в своём формате (где-то <code>{xato: "..."}</code>, где-то <code>{error: "..."}</code>), фронтенду приходится обрабатывать каждый случай отдельно. Централизованный middleware гарантирует, что все ошибки возвращаются в едином формате <code>{xato: {xabar, status}}</code>.</p>

<h4>4. throw vs next(err) — когда что использовать?</h4>
<p>Ошибка, вызванная через <code>throw</code> внутри <code>async</code>-функции, автоматически попадает в <code>catch</code>, откуда передаётся через <code>next(err)</code>. В синхронном коде использование <code>throw</code>, а затем перехват через <code>try/catch</code> и передача в <code>next()</code> — стандартный паттерн.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Error middleware определяется именно 4 аргументами (<code>err, req, res, next</code>), не иначе</li>
<li>✅ Error middleware всегда пишется <strong>после</strong> всех route'ов</li>
<li>✅ <code>next(err)</code> пропускает обычные middleware и переходит прямо к error handler'у</li>
<li>✅ Централизованная обработка ошибок гарантирует единый JSON-формат для всех ошибок</li>
<li>✅ Error middleware с 3 аргументами — Express считает его обычным middleware, он никогда не сработает</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 7: Валидация и централизованная обработка ошибок
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());
// const pool = require('./db');

// ─────────────────────────────────────────────────────────────────────
// 1) Вспомогательная функция валидации
// ─────────────────────────────────────────────────────────────────────

function validateNote(body) {
  const { sarlavha, matn } = body;
  if (!sarlavha || typeof sarlavha !== 'string') {
    const err = new Error("'sarlavha' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
  if (!matn || typeof matn !== 'string') {
    const err = new Error("'matn' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
}

// ─────────────────────────────────────────────────────────────────────
// 2) Route'ы — передают ошибки через next(err)
// ─────────────────────────────────────────────────────────────────────

app.get('/notes/:id', async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      const err = new Error('Eslatma topilmadi');
      err.status = 404;
      return next(err);
    }
    res.json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

app.post('/notes', async (req, res, next) => {
  try {
    validateNote(req.body);
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [req.body.sarlavha, req.body.matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Централизованный error middleware — ПОСЛЕ ВСЕХ route'ов
// ─────────────────────────────────────────────────────────────────────

app.use((err, req, res, next) => { // 4 аргумента — по ним Express его распознаёт
  console.error(err.message);
  const status = err.status || 500;
  res.status(status).json({
    xato: {
      xabar: err.message || 'Server xatosi',
      status,
    },
  });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — "error" middleware с 3 аргументами (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
app.use((req, res, next) => { // ❌ 3 аргумента — Express считает это ОБЫЧНЫМ middleware
  console.error('Xato yuz berdi');
  res.status(500).json({ xato: 'Server xatosi' });
});
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3703: {
        "title": "Как определяется error middleware?",
        "description": "По какому признаку Express определяет, что функция-middleware является \"error middleware\"?",
        "hint": "Это строгое правило — определяется по количеству аргументов, а не по названию.",
        "explanation": "Express определяет error middleware только по количеству аргументов (ровно 4: err, req, res, next). Любое другое количество (например 3) воспринимается как обычный middleware.",
    },
    3704: {
        "title": "Что происходит при вызове next(err)?",
        "description": "Что делает Express, когда внутри route handler'а вызывается next(err)?",
        "hint": "next() и next(err) направляют выполнение по-разному.",
        "explanation": "Если next() вызывается с аргументом, Express пропускает все обычные middleware/route'ы и сразу переходит к error middleware (с 4 аргументами).",
    },
    3705: {
        "title": "Расположите поток ошибки в правильном порядке",
        "description": "Упорядочите события, происходящие при ошибке валидации в POST /notes.",
        "hint": "throw -> catch -> next(err) -> централизованный handler.",
    },
    3706: {
        "title": "Почему error middleware с 3 аргументами не работает?",
        "description": (
            "Если централизованный error middleware написать по ошибке с "
            "(req, res, next) — 3 аргументами вместо (err, req, res, next), "
            "что произойдёт при вызове next(err) и почему возникает эта "
            "ошибка? Объясните своими словами."
        ),
        "expected_answer": "Express определяет, является ли middleware-функция error handler'ом, только по количеству её аргументов (ровно 4: err, req, res, next). Если middleware написан только с 3 аргументами, Express считает его обычным middleware, а не error handler'ом. При вызове next(err) Express ищет error middleware, но эта функция не распознаётся как таковая по количеству аргументов, поэтому она никогда не срабатывает, и ошибка «не перехватывается» — в результате клиенту возвращается стандартная, не-JSON страница ошибки Express.",
        "hint": "По какому признаку Express распознаёт error middleware — не по названию и не по расположению?",
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
