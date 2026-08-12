"""Russian translation for Node.js/Express Asoslari, lesson order=3 (L4)."""
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

LESSON_ID = 612

TITLE_RU = "4-Организация проекта с помощью Router"

TEXT_RU = """\
<h2>Организация проекта с помощью Router</h2>

<pre class="mermaid">
flowchart LR
    A["server.js"] -->|app.use('/users', ...)| UR["routes/users.js — Router"]
    A -->|app.use('/products', ...)| PR["routes/products.js — Router"]
    UR --> U1["GET /users"]
    UR --> U2["POST /users"]
    PR --> P1["GET /products"]
</pre>

<p>До сих пор мы писали все route'ы в одном файле <code>server.js</code>. Для 5-10 route'ов это нормально работает, но если их 50 — один файл становится нечитаемым. <code>express.Router()</code> — мини-приложение Express, предназначенное для разделения route'ов на отдельные файлы по темам.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первый Router</h4>
<pre><code>// routes/users.js
const express = require('express');
const router = express.Router(); // ❗ мини-приложение со своими get/post/put/delete

router.get('/', (req, res) =&gt; {
  res.json([{ id: 1, ism: 'Олим' }]);
});

router.get('/:id', (req, res) =&gt; {
  res.json({ id: Number(req.params.id), ism: 'Олим' });
});

module.exports = router; // ❗ экспортируем для использования в другом файле</code></pre>

<h4>БЛОК 2 — подключение router'а в server.js</h4>
<pre><code>// server.js
const express = require('express');
const usersRouter = require('./routes/users');

const app = express();
app.use(express.json());

app.use('/users', usersRouter); // ❗ отсюда добавляется префикс /users

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});

// Результат: router.get('/') -&gt; GET /users
//            router.get('/:id') -&gt; GET /users/:id</code></pre>

<h4>БЛОК 3 — несколько Router и структура проекта</h4>
<pre><code>// routes/products.js
const express = require('express');
const router = express.Router();

router.get('/', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Ноутбук' }]);
});

module.exports = router;</code></pre>

<pre><code>// server.js — подключение всех router'ов
const usersRouter = require('./routes/users');
const productsRouter = require('./routes/products');

app.use('/users', usersRouter);
app.use('/products', productsRouter);

// Структура проекта:
// project/
//   server.js
//   routes/
//     users.js
//     products.js</code></pre>

<h3>🐛 Намеренная ошибка — забыть подключить router через app.use()</h3>
<pre><code>// routes/orders.js — написан полностью, без ошибок
const router = express.Router();
router.get('/', (req, res) =&gt; res.json([{ id: 1 }]));
module.exports = router;

// server.js
const ordersRouter = require('./routes/orders');
// ❌ app.use('/orders', ordersRouter) — НЕ НАПИСАНО!

app.listen(3000);</code></pre>

<p><strong>Результат:</strong> запрос на <code>GET /orders</code> вернёт <code>404 Not Found</code>. Код без ошибок, route написан правильно, даже <code>require</code> выполнен — но Express никогда не узнает об этом Router, потому что вы не подключили его к приложению. <code>require()</code> загружает файл, но только <code>app.use()</code> реально добавляет его в цепочку routing.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен Router?</h4>
<p>По мере роста проекта хранение всех route'ов в одном файле затрудняет их поиск и изменение. Router позволяет разделить route'ы по темам (пользователи, товары, заказы) на отдельные файлы, упрощая чтение и поддержку кода.</p>

<h4>2. router.get/post/put/delete — то же самое, что app.*, но "scoped"</h4>
<p><code>express.Router()</code> — уменьшенная копия <code>app</code>: имеет те же методы <code>.get()</code>, <code>.post()</code>, <code>.put()</code>, <code>.delete()</code>, но адреса route'ов работают только внутри префикса, к которому подключён этот Router.</p>

<h4>3. module.exports = router</h4>
<p>Каждый файл route'ов экспортирует объект Router через <code>module.exports</code>, чтобы его можно было импортировать в другом файле (обычно в <code>server.js</code>) через <code>require()</code>.</p>

<h4>4. app.use(префикс, router) — как работает префикс</h4>
<pre><code>app.use('/users', usersRouter);
// router.get('/')       внутри usersRouter -&gt; GET  /users
// router.get('/:id')    внутри usersRouter -&gt; GET  /users/:id
// router.post('/')      внутри usersRouter -&gt; POST /users</code></pre>
<p>Внутри файла router'а вы пишете только <strong>относительный</strong> путь (<code>'/'</code>, <code>'/:id'</code>) — полный путь Express сам составляет, объединяя его с префиксом из <code>app.use()</code>.</p>

<h4>5. Рекомендуемая структура проекта</h4>
<pre><code>project/
  server.js          # только: middleware, подключение router'ов, listen
  routes/
    users.js          # все route'ы, связанные с /users
    products.js        # все route'ы, связанные с /products
  package.json</code></pre>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>express.Router()</code> — мини-приложение для разделения route'ов на отдельные файлы</li>
<li>✅ Каждый файл route'ов заканчивается строкой <code>module.exports = router</code></li>
<li>✅ <code>app.use(префикс, router)</code> — подключает Router к основному приложению и добавляет префикс</li>
<li>✅ <code>require()</code> загружает файл, но без <code>app.use()</code> Router никогда не заработает — результат: тихий 404</li>
<li>✅ В больших проектах разделение route'ов по папке <code>routes/</code> — стандартная практика</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 4: Организация проекта с помощью Router
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// routes/users.js
// ─────────────────────────────────────────────────────────────────────
const express = require('express');
const usersRouter = express.Router();

usersRouter.get('/', (req, res) => {
  res.json([{ id: 1, ism: 'Олим' }, { id: 2, ism: 'Вали' }]);
});

usersRouter.get('/:id', (req, res) => {
  res.json({ id: Number(req.params.id), ism: 'Олим' });
});

usersRouter.post('/', (req, res) => {
  const { ism } = req.body;
  if (!ism) {
    return res.status(400).json({ xato: "'ism' majburiy" });
  }
  res.status(201).json({ id: Date.now(), ism });
});

// module.exports = usersRouter;  // обязательно, если файл отдельный

// ─────────────────────────────────────────────────────────────────────
// routes/products.js
// ─────────────────────────────────────────────────────────────────────
const productsRouter = express.Router();

productsRouter.get('/', (req, res) => {
  res.json([{ id: 1, nomi: 'Ноутбук' }, { id: 2, nomi: 'Мышь' }]);
});

// module.exports = productsRouter;

// ─────────────────────────────────────────────────────────────────────
// server.js — подключение всех router'ов
// ─────────────────────────────────────────────────────────────────────
// const usersRouter = require('./routes/users');
// const productsRouter = require('./routes/products');

const app = express();
app.use(express.json());

app.use('/users', usersRouter);
app.use('/products', productsRouter);

// ─────────────────────────────────────────────────────────────────────
// Намеренная ошибка — забыть подключить (в комментарии, не выполняется)
// ─────────────────────────────────────────────────────────────────────
/*
const ordersRouter = express.Router();
ordersRouter.get('/', (req, res) => res.json([{ id: 1 }]));
// ❌ app.use('/orders', ordersRouter) — НЕ НАПИСАНО!
// Результат: GET /orders -> 404 Not Found, даже если route написан правильно.
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
  console.log('Проверьте: GET /users, GET /products');
});
"""

EX = {
    3663: {
        "title": "Что такое express.Router()?",
        "description": "Какую функцию на самом деле выполняет express.Router()?",
        "hint": "Он похож на app, но меньше и посвящён одной теме.",
        "explanation": "express.Router() — уменьшенная копия app: имеет свои методы get/post/put/delete, используется для разделения route'ов по темам на отдельные файлы.",
    },
    3664: {
        "title": "Как подключается Router?",
        "description": "Что нужно сделать, чтобы Router, написанный в файле routes/users.js, заработал в основном приложении?",
        "hint": "require() загружает файл, но не добавляет его в цепочку routing.",
        "explanation": "require() загружает файл и возвращает объект, но Express добавляет этот Router в реальную цепочку routing только после вызова app.use(префикс, router).",
    },
    3665: {
        "title": "Как путь внутри Router превращается в полный адрес?",
        "description": "Написано app.use('/users', usersRouter), внутри usersRouter есть router.get('/:id'). Расположите элементы в правильном порядке: что добавляется первым, что — в конце.",
        "hint": "Префикс из app.use() и относительный путь внутри Router объединяются в полный адрес.",
    },
    3666: {
        "title": "Router написан, но не подключён — что произойдёт?",
        "description": (
            "В файле routes/orders.js Router написан полностью и без ошибок, "
            "require() в server.js тоже выполнен, но app.use('/orders', "
            "ordersRouter) не написан. Какой ответ вернётся на запрос "
            "GET /orders и почему? Объясните своими словами."
        ),
        "expected_answer": "Ответом будет 404 Not Found. Причина: require() загружает файл и берёт в память объект Router, но это не означает \"Express, эти route'ы существуют\". Только вызов app.use(префикс, router) добавляет этот Router в собственную цепочку routing Express и начинает направлять к нему запросы. Без этого шага Express вообще не знает об адресе /orders и возвращает стандартный ответ \"не найдено\" — даже если код самого Router написан полностью правильно.",
        "hint": "require() и app.use() нужны оба — один загружает, другой подключает. Подумайте о разнице.",
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
