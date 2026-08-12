"""Russian translation for Node.js/Express Asoslari, lesson order=7 (R2)."""
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

LESSON_ID = 620

TITLE_RU = "R2-Notes REST API (повторение)"

TEXT_RU = """\
<h2>R2 — Повторение уроков 5-6: Notes REST API</h2>

<p>Объединив уроки 5-6, создадим полноценный Notes (заметки) REST API на PostgreSQL: подключение к DB, полный CRUD и правильную проверку результата каждой операции.</p>

<h3>Цель проекта</h3>
<ul>
<li>Таблица <code>notes</code>: <code>id</code>, <code>sarlavha</code>, <code>matn</code>, <code>yaratilgan_vaqt</code></li>
<li><code>GET /notes</code> — получить все, <code>GET /notes/:id</code> — получить одну</li>
<li><code>POST /notes</code> — создать новую заметку (с валидацией)</li>
<li><code>PUT /notes/:id</code>, <code>DELETE /notes/:id</code> — правильное определение 404 через <code>rowCount</code></li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — GET route'ы</h4>
<p><code>GET /notes</code> — верните все заметки с <code>ORDER BY id</code>. <code>GET /notes/:id</code> — одну заметку, если не найдена — <code>404</code>.</p>

<h4>Задание 2 — создание через POST</h4>
<p><code>sarlavha</code> и <code>matn</code> обязательны (не должны быть пустыми). Через <code>INSERT ... RETURNING *</code> верните новую заметку со статусом <code>201</code>.</p>

<h4>Задание 3 — обновление через PUT</h4>
<p><code>UPDATE ... WHERE id = $X RETURNING *</code> — если <code>result.rowCount === 0</code>, верните <code>404</code>, иначе — обновлённую заметку.</p>

<h4>Задание 4 — DELETE</h4>
<p><code>DELETE FROM notes WHERE id = $1</code> — проверив <code>rowCount</code>, верните <code>404</code> или <code>204</code>.</p>

<h3>🐛 Намеренная сложность: не забыть try/catch в каждом route</h3>
<p>При добавлении каждого нового route не забывайте добавлять и <code>try/catch</code> — в уроках 5-6 это показывалось по отдельности, но при большом числе route'ов легко забыть о нём в некоторых. Без <code>try/catch</code> ошибка DB не обрушит весь сервер (Express её перехватит), но клиенту вернётся непонятная HTML-страница «Internal Server Error» вместо JSON.</p>

<h3>Стартовый код</h3>
<pre><code>const express = require('express');
const app = express();
app.use(express.json());
const pool = require('./db'); // как в уроке 5

// Задание 1: GET /notes, GET /notes/:id
// Задание 2: POST /notes
// Задание 3: PUT /notes/:id
// Задание 4: DELETE /notes/:id

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>app.get('/notes', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM notes ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.get('/notes/:id', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.post('/notes', async (req, res) =&gt; {
  try {
    const { sarlavha, matn } = req.body;
    if (!sarlavha || !matn) {
      return res.status(400).json({ xato: "'sarlavha' va 'matn' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [sarlavha, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.put('/notes/:id', async (req, res) =&gt; {
  try {
    const { sarlavha, matn } = req.body;
    const result = await pool.query(
      'UPDATE notes SET sarlavha = $1, matn = $2 WHERE id = $3 RETURNING *',
      [sarlavha, matn, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.delete('/notes/:id', async (req, res) =&gt; {
  try {
    const result = await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Уроки 5-6 все вместе: подключение к DB, параметризованные запросы, полный CRUD</li>
<li>✅ Каждый route обязательно должен иметь свой <code>try/catch</code></li>
<li>✅ <code>rowCount</code> — единственный надёжный способ определить 404 в <code>UPDATE</code>/<code>DELETE</code></li>
<li>✅ Небольшой, чёткий набор route'ов — отправная точка реальных проектов</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ПОВТОРЕНИЕ 2: Notes REST API (уроки 5-6)
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());
// const pool = require('./db'); // как в уроке 5

app.get('/notes', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM notes ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.get('/notes/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.post('/notes', async (req, res) => {
  try {
    const { sarlavha, matn } = req.body;
    if (!sarlavha || !matn) {
      return res.status(400).json({ xato: "'sarlavha' va 'matn' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [sarlavha, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.put('/notes/:id', async (req, res) => {
  try {
    const { sarlavha, matn } = req.body;
    const result = await pool.query(
      'UPDATE notes SET sarlavha = $1, matn = $2 WHERE id = $3 RETURNING *',
      [sarlavha, matn, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.delete('/notes/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3695: {
        "title": "Почему в каждом route нужен try/catch?",
        "description": "При наличии нескольких DB route'ов зачем в каждом из них писать отдельный try/catch?",
        "hint": "Без try/catch сервер тоже не упадёт — но что получит клиент?",
        "explanation": "Даже без try/catch Express перехватит ошибку DB и сервер не упадёт, но клиенту может вернуться стандартная HTML-страница ошибки — не JSON. С try/catch можно вернуть понятную, единообразную JSON-ошибку.",
    },
    3696: {
        "title": "В каком случае DELETE /notes/:id вернёт 404?",
        "description": "В каком случае route DELETE /notes/:id должен вернуть 404?",
        "hint": "Вспомните урок 6: если rowCount равен 0 — ничего не удалено.",
        "explanation": "rowCount === 0 означает, что в таблице не найдено ни одной строки с таким id и ничего не удалено, поэтому правильно вернуть 404.",
    },
    3697: {
        "title": "Расположите запрос POST /notes в правильном порядке",
        "description": "Упорядочите шаги от момента поступления запроса на создание новой заметки до возврата ответа.",
        "hint": "Сначала подготавливается body, затем он проверяется, затем записывается в DB.",
    },
    3698: {
        "title": "Почему важно объединять уроки 5-6?",
        "description": (
            "Как в Notes REST API работают вместе подключение к DB (урок 5), "
            "параметризованные запросы и правильная обработка ошибок через "
            "rowCount (урок 6)? Какая проблема возникнет, если чего-то из "
            "этого не хватает? Объясните своими словами."
        ),
        "expected_answer": "Подключение к DB (Pool) служит основой для всех запросов. Параметризованные запросы безопасно передают данные от пользователя в SQL, предотвращая SQL Injection. Проверка через rowCount подтверждает, что операции UPDATE/DELETE действительно затронули ожидаемую строку. Если чего-то из этого не хватает — например, не проверяется rowCount — API создаёт впечатление, что работает безопасно, но на самом деле может давать неверные или вводящие в заблуждение результаты, даже если сам SQL не выдаёт никакой ошибки.",
        "hint": "У каждой части своя роль — что пропадёт, если убрать одну из них?",
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
