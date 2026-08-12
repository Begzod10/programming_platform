"""Russian translation for Node.js/Express Asoslari, lesson order=12 (L10)."""
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

LESSON_ID = 630

TITLE_RU = "10-CORS и подключение React"

TEXT_RU = """\
<h2>CORS и подключение React</h2>

<pre class="mermaid">
flowchart LR
    R["React (localhost:3000)"] -->|fetch| E["Express API (localhost:5000)"]
    E -->|нет CORS-заголовка| BLOCK["Браузер: заблокировано!"]
    E -->|с cors()| OK["Браузер: разрешено"]
</pre>

<p>До сих пор мы отправляли все запросы через Postman или прямо из браузера (тот же адрес). Но ваше React-приложение работает на другом порту (например, <code>localhost:3000</code>), а Express — на другом (<code>localhost:5000</code>) — это считается <strong>разным источником</strong> (origin), и браузер по умолчанию это блокирует.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка и включение cors</h4>
<pre><code>// Терминал:
npm install cors</code></pre>

<pre><code>const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors()); // ❗ по умолчанию разрешает ВСЕ источники
app.use(express.json());

app.get('/api/products', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});</code></pre>

<h4>БЛОК 2 — отправка запроса со стороны React</h4>
<pre><code>// Внутри React-компонента:
useEffect(() =&gt; {
  fetch('http://localhost:5000/api/products')
    .then(res =&gt; res.json())
    .then(data =&gt; setProducts(data))
    .catch(err =&gt; console.error('Xato:', err));
}, []);</code></pre>

<h4>БЛОК 3 — разрешение только нужных источников (для production)</h4>
<pre><code>const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: allowedOrigins, // ❗ разрешены только эти источники, остальным нет
  credentials: true,       // для отправки cookie/auth-заголовков
}));</code></pre>

<h3>🐛 Намеренная ошибка — cors() после express.json() или в неправильном месте</h3>
<pre><code>// ❌ Здесь cors() вообще не вызван или размещён ПОСЛЕ route'ов
const app = express();
app.use(express.json());

app.get('/api/products', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});

app.use(cors()); // ❌ слишком поздно — route уже успел отправить ответ</code></pre>

<p><strong>Результат:</strong> при вызове <code>fetch()</code> из React-приложения в консоли браузера появится ошибка <code>"has been blocked by CORS policy"</code> — даже если сам сервер Express отработал правильно и вернул данные! Причина: заголовки CORS должны добавляться <strong>до</strong> срабатывания route ответа, иначе браузер получает ответ, но из-за отсутствия нужного заголовка <code>Access-Control-Allow-Origin</code> отказывается передать его в код JavaScript.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое CORS и зачем он существует?</h4>
<p>CORS (Cross-Origin Resource Sharing) — механизм безопасности браузера. Он по умолчанию блокирует запросы <strong>между разными источниками</strong>, чтобы один сайт (например, вредоносный) не мог тайно отправлять запросы к API другого сайта от имени пользователя.</p>

<h4>2. Что такое «источник» (origin)?</h4>
<p>Источник — сочетание протокола + домена + порта. <code>http://localhost:3000</code> и <code>http://localhost:5000</code> — два <strong>разных</strong> источника, даже если оба являются <code>localhost</code> (разницы в порте достаточно).</p>

<h4>3. Как работает middleware cors()?</h4>
<p><code>app.use(cors())</code> автоматически добавляет к каждому ответу заголовки вроде <code>Access-Control-Allow-Origin</code>. Без этих заголовков браузер не передаст ответ в код JavaScript — даже если сервер полностью отправил ответ.</p>

<h4>4. Почему origin: '*' опасен в production?</h4>
<p>По умолчанию <code>cors()</code> разрешает все источники (<code>*</code>). Это удобно для разработки, но может быть опасно в production, особенно в сочетании с <code>credentials: true</code>. Поэтому в production рекомендуется ограничивать <code>origin</code> явным списком.</p>

<h4>5. Расположение middleware — ещё раз</h4>
<p>Как мы видели в уроках 4 и 7, middleware выполняются в порядке написания. <code>cors()</code> всегда добавляется <strong>до</strong> route'ов, обычно в самых первых строках.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ CORS — политика безопасности браузера, блокирующая межисточниковые запросы</li>
<li>✅ Middleware <code>cors()</code> автоматически добавляет нужные заголовки</li>
<li>✅ <code>cors()</code> обязательно должен быть добавлен <strong>до</strong> route'ов, иначе заголовки не попадут в ответ</li>
<li>✅ В production безопаснее ограничивать <code>origin</code> явным списком доменов</li>
<li>✅ Когда React и Express работают на разных портах — это всегда считается «разным источником»</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 10: CORS и подключение React
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const cors = require('cors');
const app = express();

// ─────────────────────────────────────────────────────────────────────
// 1) CORS — добавляется ДО route'ов
// ─────────────────────────────────────────────────────────────────────

const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
}));

app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 2) Простой API route — React будет делать fetch на этот адрес
// ─────────────────────────────────────────────────────────────────────

app.get('/api/products', (req, res) => {
  res.json([
    { id: 1, nomi: 'Noutbuk', narxi: 8000000 },
    { id: 2, nomi: 'Sichqoncha', narxi: 150000 },
  ]);
});

// ─────────────────────────────────────────────────────────────────────
// Со стороны React (в отдельном frontend-проекте):
//
// useEffect(() => {
//   fetch('http://localhost:5000/api/products')
//     .then(res => res.json())
//     .then(data => setProducts(data))
//     .catch(err => console.error('Xato:', err));
// }, []);
// ─────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка — cors() после route'ов (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
const appXato = express();
appXato.use(express.json());
appXato.get('/api/products', (req, res) => res.json([]));
appXato.use(cors()); // ❌ слишком поздно — браузер заблокирует этот ответ
*/

app.listen(5000, () => {
  console.log('Сервер запущен: http://localhost:5000');
});
"""

EX = {
    3735: {
        "title": "Зачем существует CORS?",
        "description": "Зачем браузер применяет механизм CORS?",
        "hint": "Это механизм безопасности браузера, а не сервера.",
        "explanation": "CORS — политика безопасности браузера, по умолчанию блокирующая запросы между разными источниками, тем самым предотвращая тайную отправку запросов вредоносными сайтами к чужим API.",
    },
    3736: {
        "title": "Являются ли localhost:3000 и localhost:5000 одним источником?",
        "description": "С точки зрения CORS, являются ли http://localhost:3000 и http://localhost:5000 одним и тем же источником?",
        "hint": "Источник — сочетание протокола + домена + ПОРТА.",
        "explanation": "Источник (origin) состоит из сочетания протокола, домена и порта. Даже если различается только порт, они считаются разными источниками, и применяются правила CORS.",
    },
    3737: {
        "title": "Куда нужно поместить middleware cors()?",
        "description": "Упорядочите расположение cors(), чтобы запросы от React работали правильно.",
        "hint": "CORS всегда добавляется до route'ов, сразу после создания приложения.",
    },
    3738: {
        "title": "Что произойдёт, если cors() разместить после route'ов?",
        "description": (
            "Если app.use(cors()) написан ПОСЛЕ регистрации route'ов, что "
            "произойдёт с запросом fetch() из React-приложения? Почему "
            "возникает проблема, даже если сам сервер возвращает правильный "
            "ответ? Объясните своими словами."
        ),
        "expected_answer": "Express выполняет middleware и route'ы в порядке написания. Если cors() написан после route'ов, он либо вообще не вызывается (потому что route уже успел отправить ответ), либо заголовки CORS не добавляются к ответу. Хотя сервер сам вернул правильные данные, браузер, не найдя в ответе нужный заголовок Access-Control-Allow-Origin, согласно политике безопасности отказывается передать этот ответ в код JavaScript (например, внутрь .then() в React), и в консоли появляется ошибка CORS.",
        "hint": "Middleware выполняются в порядке написания — когда здесь сработает cors()?",
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
