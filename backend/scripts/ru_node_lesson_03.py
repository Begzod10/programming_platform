"""Russian translation for Node.js/Express Asoslari, lesson order=2 (L3)."""
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

LESSON_ID = 610

TITLE_RU = "3-Request/Response подробнее"

TEXT_RU = """\
<h2>Request/Response подробнее — req.body, коды статуса</h2>

<pre class="mermaid">
flowchart LR
    C["Клиент: POST с JSON body"] --> P["express.json() — превращает текст в объект"]
    P --> H["handler: req.body работает"]
    H --> S["ответ с правильным кодом статуса"]
</pre>

<p>В уроке 2 мы видели <code>req.params</code> и <code>req.query</code>. Теперь посмотрим, как читать <strong>JSON body</strong>, когда клиент его отправляет (например, при создании нового пользователя).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — express.json() и req.body</h4>
<pre><code>const express = require('express');
const app = express();

app.use(express.json()); // ❗ превращает HTTP body в JSON-объект

app.post('/users', (req, res) =&gt; {
  console.log(req.body); // { ism: 'Олим', yosh: 22 }
  const yangiUser = { id: Date.now(), ...req.body };
  res.status(201).json(yangiUser);
});</code></pre>

<pre><code>// Со стороны клиента (например, через fetch):
fetch('/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ism: 'Олим', yosh: 22 }),
});</code></pre>

<h4>БЛОК 2 — PUT/PATCH и правильные коды статуса</h4>
<pre><code>let users = [{ id: 1, ism: 'Олим', yosh: 22 }];

app.put('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  const index = users.findIndex(u =&gt; u.id === id);
  if (index === -1) {
    return res.status(404).json({ xato: 'Пользователь не найден' });
  }
  users[index] = { ...users[index], ...req.body };
  res.status(200).json(users[index]);
});

app.delete('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  users = users.filter(u =&gt; u.id !== id);
  res.status(204).send(); // 204 — успешно, но без body
});</code></pre>

<h4>БЛОК 3 — простая валидация</h4>
<pre><code>app.post('/users', (req, res) =&gt; {
  const { ism, yosh } = req.body;

  if (!ism || typeof ism !== 'string') {
    return res.status(400).json({ xato: "'ism' обязателен и должен быть строкой" });
  }
  if (yosh !== undefined &amp;&amp; typeof yosh !== 'number') {
    return res.status(400).json({ xato: "'yosh' должен быть числом" });
  }

  const yangiUser = { id: Date.now(), ism, yosh };
  res.status(201).json(yangiUser);
});</code></pre>

<h3>🐛 Намеренная ошибка — забыть express.json()</h3>
<pre><code>const express = require('express');
const app = express();

// ❌ app.use(express.json()) НЕТ!

app.post('/users', (req, res) =&gt; {
  console.log(req.body); // undefined!
  const yangiUser = { id: Date.now(), ...req.body }; // ...undefined — не ошибка, но результат пуст
  res.status(201).json(yangiUser); // { id: 12345 } — ism/yosh потеряны!
});</code></pre>

<p><strong>Результат:</strong> даже если клиент отправит <code>{ ism: 'Олим', yosh: 22 }</code>, <code>req.body</code> будет <code>undefined</code>. Никакой ошибки не появится (<code>...undefined</code> в JavaScript не ошибка, ничего не добавляет), но данные пользователя <strong>тихо теряются</strong>. Причина: Express по умолчанию принимает тело HTTP-запроса как <strong>сырой текст</strong> — чтобы превратить его в JSON-объект, нужен middleware <code>express.json()</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему req.body не работает автоматически?</h4>
<p>"Тело" (body) HTTP-запроса — это поток сырых байтов/текста, приходящий по сети. Express не считает этот поток автоматически JSON'ом — ведь это может быть и XML, обычный текст, файл и т.д. <code>express.json()</code> именно читает запросы с <code>Content-Type: application/json</code> и помещает готовый объект в <code>req.body</code>.</p>

<h4>2. express.json() против express.urlencoded()</h4>
<pre><code>app.use(express.json());                       // для JSON body (API, fetch)
app.use(express.urlencoded({ extended: true })); // для HTML &lt;form&gt; POST</code></pre>

<h4>3. Наиболее часто используемые коды статуса</h4>
<table>
<tr><th>Код</th><th>Значение</th><th>Когда</th></tr>
<tr><td>200</td><td>OK</td><td>Успешный GET/PUT</td></tr>
<tr><td>201</td><td>Created</td><td>Успешный POST (новый ресурс)</td></tr>
<tr><td>204</td><td>No Content</td><td>Успешно, но нет возвращаемого body (например, DELETE)</td></tr>
<tr><td>400</td><td>Bad Request</td><td>Клиент отправил неверные/недостающие данные</td></tr>
<tr><td>401</td><td>Unauthorized</td><td>Нужна аутентификация</td></tr>
<tr><td>404</td><td>Not Found</td><td>Ресурс не найден</td></tr>
<tr><td>500</td><td>Internal Server Error</td><td>Непредвиденная ошибка на стороне сервера</td></tr>
</table>

<h4>4. Простая валидация — почему нужна ручная проверка?</h4>
<p>Клиент не всегда отправляет правильные данные — иногда не хватает поля, иногда неверный тип (например, строка вместо числа). Серверу нельзя доверять: <strong>всегда проверяйте внешние данные</strong> — тип и обязательные поля — перед записью в базу данных.</p>

<h4>5. Ранний выход через return</h4>
<p><code>return res.status(400).json(...)</code> — слово <code>return</code> здесь останавливает функцию. Если забыть <code>return</code>, код продолжится и может повторно вызваться <code>res.json()</code>, что приведёт к ошибке <code>"Cannot set headers after they are sent"</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>express.json()</code> превращает HTTP body в JSON-объект, включает работу <code>req.body</code></li>
<li>✅ Забыть <code>express.json()</code> — <code>req.body</code> остаётся <code>undefined</code>, тихая ошибка</li>
<li>✅ Коды статуса: 200/201/204 — успех, 400/401/404 — ошибка клиента, 500 — ошибка сервера</li>
<li>✅ Внешние данные (req.body) всегда проверяйте перед использованием</li>
<li>✅ <code>return res.json(...)</code> — останавливает функцию, гарантируя, что дальнейший код не выполнится</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 3: Request/Response подробнее
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

app.use(express.json()); // превращает HTTP body в JSON-объект

let users = [{ id: 1, ism: 'Олим', yosh: 22 }];

// ─────────────────────────────────────────────────────────────────────
// 1) req.body — создание нового ресурса через POST
// ─────────────────────────────────────────────────────────────────────

app.post('/users', (req, res) => {
  const { ism, yosh } = req.body;

  // ─── Простая валидация ───
  if (!ism || typeof ism !== 'string') {
    return res.status(400).json({ xato: "'ism' обязателен и должен быть строкой" });
  }
  if (yosh !== undefined && typeof yosh !== 'number') {
    return res.status(400).json({ xato: "'yosh' должен быть числом" });
  }

  const yangiUser = { id: Date.now(), ism, yosh };
  users.push(yangiUser);
  res.status(201).json(yangiUser);
});

// ─────────────────────────────────────────────────────────────────────
// 2) PUT — полное обновление
// ─────────────────────────────────────────────────────────────────────

app.put('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  const index = users.findIndex(u => u.id === id);
  if (index === -1) {
    return res.status(404).json({ xato: 'Пользователь не найден' });
  }
  users[index] = { ...users[index], ...req.body };
  res.status(200).json(users[index]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) DELETE — 204 No Content
// ─────────────────────────────────────────────────────────────────────

app.delete('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  users = users.filter(u => u.id !== id);
  res.status(204).send();
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — забыть express.json()
// ─────────────────────────────────────────────────────────────────────

/*
const appXato = express();
// ❌ appXato.use(express.json()) НЕТ!

appXato.post('/users', (req, res) => {
  console.log(req.body); // undefined!
  const yangiUser = { id: Date.now(), ...req.body }; // только { id }
  res.status(201).json(yangiUser); // ism/yosh тихо теряются
});
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3655: {
        "title": "Что нужно, чтобы работал req.body?",
        "description": "Что нужно настроить в Express, чтобы req.body правильно работал (как JSON-объект)?",
        "hint": "Express по умолчанию считает HTTP body сырым текстом.",
        "explanation": "Middleware express.json() читает тело запроса с JSON Content-Type и предоставляет его как готовый объект через req.body. Без этого middleware req.body остаётся undefined.",
    },
    3656: {
        "title": "Какой код статуса подходит для успешного DELETE?",
        "description": "Ресурс успешно удалён, но в ответе нет данных для возврата. Какой код статуса наиболее подходит?",
        "hint": "204 — \"No Content\": успешно, но нет возвращаемого body.",
        "explanation": "204 No Content означает, что операция успешно выполнена, но в ответе нет тела для возврата. Это особенно подходит для DELETE.",
    },
    3657: {
        "title": "Что произойдёт, если забыть express.json()?",
        "description": "Если не написать app.use(express.json()), а клиент отправит JSON body, какое значение будет иметь req.body?",
        "hint": "Без парсера body Express не читает и не превращает тело запроса в объект.",
        "explanation": "Без express.json() req.body никогда не заполняется и остаётся undefined — без какой-либо ошибки, тихо.",
    },
    3658: {
        "title": "Почему req.body всегда нужно проверять перед использованием?",
        "description": (
            "Почему поля ism/yosh, пришедшие из req.body в route POST /users, "
            "нужно проверять (валидировать) ПЕРЕД записью в базу данных? "
            "Объясните своими словами."
        ),
        "expected_answer": "Данным, отправленным клиентом, никогда нельзя полностью доверять — из-за программной ошибки, ошибки пользователя, или намеренной отправки неверных данных ожидаемое поле может отсутствовать, может прийти значение неверного типа. Если записывать такие данные напрямую в базу данных без проверки, могут сохраниться повреждённые или неверные данные, либо возникнуть неожиданные runtime-ошибки. Валидация должна всегда выполняться на границе системы (здесь: данные, пришедшие от клиента).",
        "hint": "Подумайте, насколько можно доверять данным, пришедшим от клиента.",
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
