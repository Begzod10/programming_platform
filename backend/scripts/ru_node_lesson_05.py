"""Russian translation for Node.js/Express Asoslari, lesson order=5 (L5)."""
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

LESSON_ID = 616

TITLE_RU = "5-Подключение PostgreSQL (pg)"

TEXT_RU = """\
<h2>Подключение PostgreSQL — node-postgres (pg)</h2>

<pre class="mermaid">
flowchart LR
    A["Express route"] --> B["pool.query(sql, params)"]
    B --> C[("PostgreSQL")]
    C --> B
    B --> A
</pre>

<p>До сих пор мы хранили данные в обычном JavaScript-массиве (в памяти) — при перезапуске сервера всё пропадало. На курсе SQL вы изучили работу с PostgreSQL; теперь подключим Express именно к этой базе данных — с помощью пакета <code>pg</code>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка pg и подключение</h4>
<pre><code>// Терминал:
npm install pg</code></pre>

<pre><code>// db.js
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'parol',
  database: 'mening_bazam',
});

module.exports = pool;</code></pre>

<pre><code>// server.js — проверка подключения
const pool = require('./db');

pool.query('SELECT NOW()')
  .then(res =&gt; console.log('DB подключена:', res.rows[0]))
  .catch(err =&gt; console.error('Ошибка DB:', err.message));</code></pre>

<h4>БЛОК 2 — параметризованный запрос</h4>
<pre><code>app.get('/users/:id', async (req, res) =&gt; {
  const id = req.params.id;
  const result = await pool.query(
    'SELECT * FROM users WHERE id = $1', // ❗ $1 — placeholder, не значение
    [id]                                  // ❗ значения передаются отдельным массивом
  );
  if (result.rows.length === 0) {
    return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
  }
  res.json(result.rows[0]);
});</code></pre>

<h4>БЛОК 3 — async/await + try/catch</h4>
<pre><code>app.get('/users', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT id, ism, email FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});</code></pre>

<h3>🐛 Намеренная ошибка — SQL Injection (склейка строк)</h3>
<pre><code>// ❌ ОПАСНО — вставка значения от пользователя напрямую
app.get('/users/:id', async (req, res) =&gt; {
  const id = req.params.id;
  const result = await pool.query(
    `SELECT * FROM users WHERE id = ${id}` // ❌ строковый template — опасно!
  );
  res.json(result.rows[0]);
});

// Атака: клиент вместо id отправляет:
//   /users/1 OR 1=1
// Запрос превращается в:
//   SELECT * FROM users WHERE id = 1 OR 1=1
// Результат: возвращаются ВСЕ пользователи — вне контроля!</code></pre>

<p><strong>Результат:</strong> если <code>req.params.id</code> вставляется напрямую в текст SQL, пользователь может отправить особое значение и полностью изменить смысл запроса — это называется <strong>SQL Injection</strong> и является одной из самых опасных уязвимостей безопасности. Решение — никогда не вставлять значение напрямую, всегда использовать placeholder'ы <code>$1, $2, ...</code> и отдельный массив значений.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое Pool, и почему не Client?</h4>
<p><code>Pool</code> — «пул подключений», заранее подготавливающий несколько DB-подключений и переиспользующий их между запросами. Открывать новое подключение для каждого запроса медленно и дорого; Pool этого избегает. На практике почти всегда используется <code>Pool</code>, а не отдельный <code>Client</code>.</p>

<h4>2. Параметризованные запросы — $1, $2...</h4>
<pre><code>pool.query('SELECT * FROM users WHERE id = $1 AND faol = $2', [id, true]);
// $1 -&gt; id, $2 -&gt; true — библиотека pg безопасно экранирует значения</code></pre>
<p><code>$1</code>, <code>$2</code> — это не просто текст, а специальный маркер, говорящий библиотеке pg: «подставь сюда значение, но используй его как данные, а не как SQL-код».</p>

<h4>3. Запрос с async/await</h4>
<p><code>pool.query()</code> возвращает Promise, поэтому используется с <code>async/await</code> или <code>.then()</code>. Всегда рекомендуется оборачивать в <code>try/catch</code> — база данных может быть временно недоступна, или запрос может завершиться ошибкой.</p>

<h4>4. result.rows — где результат?</h4>
<p>Результат <code>pool.query()</code> — объект, в котором массив <code>.rows</code> хранит реальные строки. Если ожидается одна строка — <code>result.rows[0]</code>, если список — весь <code>result.rows</code>.</p>

<h4>5. Хранение секретов через .env</h4>
<p>Никогда не пишите пароль и другие секретные настройки прямо в коде — храните их в файле <code>.env</code> и читайте через <code>process.env.DB_PASSWORD</code> (подробнее в следующих уроках).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Пакет <code>pg</code> — стандартная библиотека для подключения Node.js к PostgreSQL</li>
<li>✅ <code>Pool</code> — пул переиспользуемых подключений, быстрее, чем открывать новое на каждый запрос</li>
<li>✅ Параметризованные запросы (<code>$1, $2</code>) — защищают от SQL Injection</li>
<li>✅ Вставка значения пользователя напрямую в текст SQL — серьёзная уязвимость безопасности</li>
<li>✅ <code>result.rows</code> — массив строк из результата запроса</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 5: Подключение PostgreSQL (pg)
// ════════════════════════════════════════════════════════════════════

// ─── db.js ───
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'parol',
  database: 'mening_bazam',
});

// module.exports = pool;

// ─── server.js ───
const express = require('express');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) Проверка подключения
// ─────────────────────────────────────────────────────────────────────

pool.query('SELECT NOW()')
  .then(res => console.log('DB подключена:', res.rows[0]))
  .catch(err => console.error('Ошибка DB:', err.message));

// ─────────────────────────────────────────────────────────────────────
// 2) Параметризованный запрос — БЕЗОПАСНО
// ─────────────────────────────────────────────────────────────────────

app.get('/users/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM users WHERE id = $1',
      [req.params.id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Возврат списка
// ─────────────────────────────────────────────────────────────────────

app.get('/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, ism, email FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — SQL Injection (в комментарии, не выполняется)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/users-xato/:id', async (req, res) => {
  const result = await pool.query(
    `SELECT * FROM users WHERE id = ${req.params.id}` // ❌ строковый template — опасно!
  );
  // Атака: /users-xato/1 OR 1=1 -> вернутся ВСЕ пользователи
  res.json(result.rows[0]);
});
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3679: {
        "title": "Зачем используется Pool?",
        "description": "Зачем в node-postgres используется Pool (вместо отдельного Client)?",
        "hint": "Открывать новое подключение для каждого запроса медленно и требует ресурсов.",
        "explanation": "Pool — заранее подготовленный набор подключений, переиспользуемых между запросами. Это гораздо эффективнее, чем открывать новое DB-подключение на каждый запрос.",
    },
    3680: {
        "title": "Какую роль играет $1?",
        "description": "В записи pool.query('SELECT * FROM users WHERE id = $1', [id]) что означает $1?",
        "hint": "Значение не вставляется напрямую в текст SQL — оно передаётся отдельно.",
        "explanation": "$1, $2... — placeholder'ы, относящиеся к библиотеке pg. Значения, переданные через них, безопасно используются как данные, а не как SQL-код, что предотвращает SQL Injection.",
    },
    3681: {
        "title": "Расположите поток запроса в правильном порядке",
        "description": "Упорядочите шаги от момента поступления запроса GET /users/:id до возврата ответа.",
        "hint": "Запрос возвращает Promise — мы ждём результат через await, затем проверяем его.",
    },
    3682: {
        "title": "Как работает SQL Injection и почему это опасно?",
        "description": (
            "Почему опасен запрос, написанный через строковый template вида "
            "`SELECT * FROM users WHERE id = ${req.params.id}`? Как "
            "пользователь может этим злоупотребить, и как параметризованный "
            "запрос ($1) это предотвращает? Объясните своими словами."
        ),
        "expected_answer": "При использовании строкового template значение, введённое пользователем, вставляется напрямую в текст SQL, что позволяет пользователю изменить реальную логику запроса. Например, если вместо id отправить '1 OR 1=1', условие всегда будет истинным, и запрос вернёт все строки таблицы — хотя запрашивался только один пользователь. В худших случаях так можно даже удалить или изменить данные. Параметризованный запрос ($1, $2 и отдельный массив значений) предотвращает это, потому что библиотека pg отправляет значения не как SQL-код, а как чистые данные — они никак не могут повлиять на логику запроса.",
        "hint": "Представьте, что пользователь отправит вместо id что-то, кроме простого числа.",
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
