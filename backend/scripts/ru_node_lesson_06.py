"""Russian translation for Node.js/Express Asoslari, lesson order=6 (L6)."""
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

LESSON_ID = 618

TITLE_RU = "6-CRUD-операции"

TEXT_RU = """\
<h2>CRUD-операции — полноценная работа с базой данных</h2>

<pre class="mermaid">
flowchart LR
    C["Create — POST"] --> DB[("PostgreSQL")]
    R["Read — GET"] --> DB
    U["Update — PUT"] --> DB
    D["Delete — DELETE"] --> DB
</pre>

<p>В уроке 5 мы разобрали <code>SELECT</code>. Теперь подключим <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> к route'ам Express и научимся <strong>правильно проверять</strong> результат каждого из них.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — Create (POST, RETURNING)</h4>
<pre><code>app.post('/products', async (req, res) =&gt; {
  const { nomi, narxi } = req.body;
  if (!nomi || typeof narxi !== 'number') {
    return res.status(400).json({ xato: "'nomi' va 'narxi' majburiy" });
  }
  const result = await pool.query(
    'INSERT INTO products (nomi, narxi) VALUES ($1, $2) RETURNING *', // ❗ RETURNING * — возвращает новую строку
    [nomi, narxi]
  );
  res.status(201).json(result.rows[0]);
});</code></pre>

<h4>БЛОК 2 — Update (PUT, проверка rowCount)</h4>
<pre><code>app.put('/products/:id', async (req, res) =&gt; {
  const { nomi, narxi } = req.body;
  const result = await pool.query(
    'UPDATE products SET nomi = $1, narxi = $2 WHERE id = $3 RETURNING *',
    [nomi, narxi, req.params.id]
  );
  if (result.rowCount === 0) { // ❗ ни одна строка не обновлена
    return res.status(404).json({ xato: 'Mahsulot topilmadi' });
  }
  res.json(result.rows[0]);
});</code></pre>

<h4>БЛОК 3 — Delete (rowCount для 404 или 204)</h4>
<pre><code>app.delete('/products/:id', async (req, res) =&gt; {
  const result = await pool.query('DELETE FROM products WHERE id = $1', [req.params.id]);
  if (result.rowCount === 0) {
    return res.status(404).json({ xato: 'Mahsulot topilmadi' });
  }
  res.status(204).send();
});</code></pre>

<h3>🐛 Намеренная ошибка — отсутствие проверки rowCount</h3>
<pre><code>// ❌ rowCount не проверяется
app.put('/products-xato/:id', async (req, res) =&gt; {
  const result = await pool.query(
    'UPDATE products SET nomi = $1 WHERE id = $2 RETURNING *',
    [req.body.nomi, req.params.id]
  );
  res.json(result.rows[0]); // ❌ если id не найден — result.rows[0] === undefined!
});

// Если клиент отправит /products-xato/9999 (несуществующий id):
// - в DB ничего не изменится (обновлено 0 строк)
// - но сервер вернёт статус 200 с "undefined"
// - клиент может ошибочно понять это как "успешно обновлено"!</code></pre>

<p><strong>Результат:</strong> запрос <code>UPDATE</code> или <code>DELETE</code> может выполниться <strong>без ошибок</strong>, даже если не найдено ни одной строки — для SQL это нормальная ситуация, а не ошибка. Если не проверять <code>result.rowCount</code>, сервер ответит «всё в порядке» даже для несуществующего <code>id</code>, хотя в базе данных на самом деле ничего не изменилось. Это тихая ошибка, вводящая клиента в заблуждение.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен RETURNING *?</h4>
<p>В PostgreSQL <code>INSERT</code>/<code>UPDATE</code> по умолчанию ничего не возвращают. С <code>RETURNING *</code> можно получить полную строку после операции одним запросом, без отдельного <code>SELECT</code>.</p>

<h4>2. result.rowCount — сколько строк затронуто?</h4>
<p>После <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> <code>result.rowCount</code> показывает, сколько строк было изменено или удалено. Если <code>0</code> — такой <code>id</code> вообще не найден, значит нужно вернуть <code>404</code>.</p>

<h4>3. Почему SQL выполняется без ошибок, но результат может быть неверным?</h4>
<p><code>WHERE id = 9999</code> — правильный, безошибочный SQL, даже если такого <code>id</code> не существует. PostgreSQL не выдаёт ошибку «ничего не найдено» — он просто затрагивает 0 строк. Поэтому проверка результата — задача разработчика, а не базы данных.</p>

<h4>4. CRUD и статус-коды (напоминание из урока 3)</h4>
<table>
<tr><th>Действие</th><th>HTTP-метод</th><th>Успех</th><th>Не найдено</th></tr>
<tr><td>Create</td><td>POST</td><td>201</td><td>—</td></tr>
<tr><td>Read</td><td>GET</td><td>200</td><td>404</td></tr>
<tr><td>Update</td><td>PUT</td><td>200</td><td>404</td></tr>
<tr><td>Delete</td><td>DELETE</td><td>204</td><td>404</td></tr>
</table>

<h4>5. try/catch — обязателен и в этом уроке</h4>
<p>Каждый DB-запрос (как и в уроке 5) должен быть обёрнут в <code>try/catch</code> — возможен обрыв сети, неверный SQL или временная недоступность базы данных.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>INSERT ... RETURNING *</code> — возвращает новую строку одним запросом</li>
<li>✅ <code>result.rowCount</code> — показывает количество затронутых строк, используется для определения 404 в <code>UPDATE</code>/<code>DELETE</code></li>
<li>✅ <code>UPDATE</code>/<code>DELETE</code> для несуществующего <code>id</code> — не ошибка SQL, но <code>rowCount === 0</code></li>
<li>✅ Отсутствие проверки <code>rowCount</code> — даёт клиенту ложный сигнал «успеха»</li>
<li>✅ CRUD — POST(201), GET(200/404), PUT(200/404), DELETE(204/404)</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 6: CRUD-операции
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());

// pool — предполагается подключённым как в уроке 5 (const pool = require('./db'))

// ─────────────────────────────────────────────────────────────────────
// 1) Create — POST, RETURNING *
// ─────────────────────────────────────────────────────────────────────

app.post('/products', async (req, res) => {
  try {
    const { nomi, narxi } = req.body;
    if (!nomi || typeof narxi !== 'number') {
      return res.status(400).json({ xato: "'nomi' va 'narxi' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO products (nomi, narxi) VALUES ($1, $2) RETURNING *',
      [nomi, narxi]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 2) Update — PUT, проверка rowCount
// ─────────────────────────────────────────────────────────────────────

app.put('/products/:id', async (req, res) => {
  try {
    const { nomi, narxi } = req.body;
    const result = await pool.query(
      'UPDATE products SET nomi = $1, narxi = $2 WHERE id = $3 RETURNING *',
      [nomi, narxi, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Mahsulot topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Delete — rowCount для 404 или 204
// ─────────────────────────────────────────────────────────────────────

app.delete('/products/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM products WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Mahsulot topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — rowCount не проверяется (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
app.put('/products-xato/:id', async (req, res) => {
  const result = await pool.query(
    'UPDATE products SET nomi = $1 WHERE id = $2 RETURNING *',
    [req.body.nomi, req.params.id]
  );
  res.json(result.rows[0]); // ❌ если id не найден — undefined, но статус всё ещё 200!
});
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3687: {
        "title": "Зачем используется RETURNING *?",
        "description": "Для чего в запросе INSERT добавляется RETURNING *?",
        "hint": "По умолчанию INSERT/UPDATE ничего не возвращают.",
        "explanation": "RETURNING * возвращает полностью изменённую строку в результате INSERT или UPDATE, поэтому отдельный SELECT не требуется.",
    },
    3688: {
        "title": "Что показывает result.rowCount?",
        "description": "Какое значение показывает result.rowCount после запроса UPDATE или DELETE?",
        "hint": "Значение 0 означает, что ни одна строка не подошла — значит, не найдено.",
        "explanation": "result.rowCount показывает количество строк, затронутых UPDATE или DELETE. Если 0 — ни одна строка не соответствовала условию WHERE.",
    },
    3689: {
        "title": "Расположите поток PUT /products/:id в правильном порядке",
        "description": "Упорядочите события, происходящие при запросе PUT для несуществующего id.",
        "hint": "SQL не выдаёт ошибку — он просто изменяет 0 строк, и сервер должен сам это проверить.",
    },
    3690: {
        "title": "Какая проблема возникает без проверки rowCount?",
        "description": (
            "Если в route PUT /products/:id не проверять rowCount и "
            "отправить несуществующий id, какой неверный результат получит "
            "клиент? Почему это считается «тихой ошибкой»? Объясните "
            "своими словами."
        ),
        "expected_answer": "Если rowCount не проверяется, сервер вернёт статус 200 даже для несуществующего id, хотя result.rows[0] на самом деле будет undefined (потому что в DB не найдено и не изменено ни одной строки). Клиент может ошибочно понять это как «обновление прошло успешно», хотя на самом деле ничего не изменилось. Это считается тихой ошибкой, потому что ни сервер, ни SQL не выдают явного сообщения об ошибке — проблема заметна только по тому, что тело ответа отличается от ожидаемого, если это специально не проверять.",
        "hint": "SQL сам по себе не выдаёт ошибку — проблема только в отсутствии проверки результата.",
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
