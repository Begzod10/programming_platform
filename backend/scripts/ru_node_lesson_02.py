"""Russian translation for Node.js/Express Asoslari, lesson order=1 (L2)."""
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

LESSON_ID = 608

TITLE_RU = "2-Routing и middleware"

TEXT_RU = """\
<h2>Routing и middleware — цепочка запросов</h2>

<pre class="mermaid">
flowchart LR
    REQ["Пришёл запрос"] --> MW1["logger middleware"]
    MW1 -->|next()| MW2["auth middleware"]
    MW2 -->|next()| R["обработчик route"]
    R --> RES["Ответ"]
</pre>

<p>В уроке 1 мы писали для каждого route отдельно <code>(req, res) =&gt; {...}</code>. Но у многих route есть общая работа: логирование каждого запроса, проверка аутентификации и т.д. Вместо повторения этого в каждом handler'е — используем <strong>middleware</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — параметры route и методы REST</h4>
<pre><code>const users = [
  { id: 1, ism: 'Олим' },
  { id: 2, ism: 'Вали' },
];

app.get('/users', (req, res) =&gt; {
  res.json(users); // GET — чтение всех пользователей
});

app.get('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id); // :id — параметр route, берётся через req.params
  const user = users.find(u =&gt; u.id === id);
  if (!user) return res.status(404).json({ xato: 'Не найдено' });
  res.json(user);
});

app.post('/users', (req, res) =&gt; {
  res.status(201).json({ xabar: 'Новый пользователь создан' }); // POST — создание
});

app.delete('/users/:id', (req, res) =&gt; {
  res.json({ xabar: `${req.params.id} удалён` }); // DELETE — удаление
});</code></pre>

<p>Это — конвенция REST: <code>GET</code> используется для чтения, <code>POST</code> для создания, <code>PUT</code>/<code>PATCH</code> для обновления, <code>DELETE</code> для удаления. Адрес (<code>/users/:id</code>) один и тот же, различается только HTTP-метод.</p>

<h4>БЛОК 2 — первый middleware</h4>
<pre><code>function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next(); // ❗ ВАЖНО — обязательно вызывается для перехода к следующему middleware/route
}

app.use(logger); // запускается для КАЖДОГО запроса

app.get('/', (req, res) =&gt; {
  res.send('Главная страница');
});</code></pre>

<p>Теперь каждый запрос будет записываться в консоль в виде <code>GET /</code>, <code>POST /users</code> — без необходимости писать <code>logger</code> отдельно в каждом route.</p>

<h4>БЛОК 3 — цепочка из нескольких middleware</h4>
<pre><code>function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Нет токена' });
  next(); // токен есть — переходим дальше
}

// Middleware только для ОПРЕДЕЛЁННОГО route:
app.get('/profil', authTekshir, (req, res) =&gt; {
  res.json({ xabar: 'Это защищённая страница' });
});</code></pre>

<p><code>authTekshir</code> передан не через <code>app.use()</code>, а напрямую как второй аргумент <code>app.get()</code>. Это — middleware, относящийся только к route <code>/profil</code>.</p>

<h3>🐛 Намеренная ошибка — неправильный порядок middleware</h3>
<pre><code>// ❌ Route написан ДО middleware!
app.get('/profil', (req, res) =&gt; {
  res.json({ xabar: 'Защищённая страница' });
});

function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Нет токена' });
  next();
}

app.use(authTekshir); // ❌ зарегистрирован ПОСЛЕ /profil</code></pre>

<p><strong>Результат:</strong> даже если отправить запрос на <code>/profil</code> без токена — <strong>защита не сработает</strong>, страница откроется! Причина: Express проверяет route и middleware в <strong>порядке регистрации</strong>, сверху вниз. Так как route <code>/profil</code> написан раньше <code>authTekshir</code>, запрос вообще не доходит до <code>authTekshir</code> — он работает только для route, зарегистрированных <strong>после</strong> <code>/profil</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое middleware?</h4>
<p>Middleware — обычная функция с сигнатурой <code>(req, res, next)</code>. Она может просмотреть запрос, изменить его, или остановить его. Если вызван <code>next()</code> — запрос переходит к следующему middleware/route. Если <code>next()</code> не вызван (и ответ тоже не отправлен) — запрос "зависает", как в уроке 1.</p>

<h4>2. Порядок — всё зависит от последовательности регистрации</h4>
<p>Когда приходит запрос, Express проверяет <code>app.use()</code>/<code>app.get()</code> и т.д. <strong>в том порядке, в котором написан код</strong>. Это — самое важное, но часто забываемое правило в Express: <strong>middleware защиты всегда должен быть написан ДО</strong> защищаемых route.</p>

<h4>3. app.use() против app.get()</h4>
<table>
<tr><th></th><th>app.use(fn)</th><th>app.get(адрес, fn)</th></tr>
<tr><td>Для какого HTTP-метода</td><td>Для всех (GET, POST, ...)</td><td>Только для GET</td></tr>
<tr><td>Для какого адреса</td><td>Для всех (если адрес не указан)</td><td>Только для указанного адреса</td></tr>
</table>

<h4>4. Параметр route (:id) против query string (?key=val)</h4>
<pre><code>// Параметр route — часть адреса
app.get('/users/:id', (req, res) =&gt; {
  console.log(req.params.id); // /users/5 -> "5"
});

// Query string — часть после ?
app.get('/search', (req, res) =&gt; {
  console.log(req.query.q); // /search?q=olim -> "olim"
});</code></pre>

<h4>5. Коды статуса HTTP — почему это важно?</h4>
<p><code>res.status(201)</code> — "создано", <code>res.status(404)</code> — "не найдено", <code>res.status(401)</code> — "нет авторизации". Фронтенд (React) решает, как себя вести, ориентируясь на эти коды — правильная установка кода статуса делает "язык" backend'а понятным.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Конвенция REST: GET для чтения, POST для создания, PUT/PATCH для обновления, DELETE для удаления</li>
<li>✅ Параметр route (<code>:id</code>) берётся через <code>req.params</code>, query string — через <code>req.query</code></li>
<li>✅ Middleware — функция <code>(req, res, next)</code>, если <code>next()</code> не вызван, запрос останавливается</li>
<li>✅ Express проверяет middleware/route в порядке регистрации — порядок важен</li>
<li>✅ Middleware защиты обязательно должен быть написан ДО защищаемых route</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 2: Routing и middleware
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

const users = [
  { id: 1, ism: 'Олим' },
  { id: 2, ism: 'Вали' },
];

// ─────────────────────────────────────────────────────────────────────
// 1) Параметры route и методы REST
// ─────────────────────────────────────────────────────────────────────

app.get('/users', (req, res) => {
  res.json(users);
});

app.get('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  const user = users.find(u => u.id === id);
  if (!user) return res.status(404).json({ xato: 'Не найдено' });
  res.json(user);
});

app.post('/users', (req, res) => {
  res.status(201).json({ xabar: 'Новый пользователь создан' });
});

app.delete('/users/:id', (req, res) => {
  res.json({ xabar: `${req.params.id} удалён` });
});

// ─────────────────────────────────────────────────────────────────────
// 2) Первый middleware — для каждого запроса
// ─────────────────────────────────────────────────────────────────────

function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next(); // ВАЖНО — для перехода к следующему
}

app.use(logger);

// ─────────────────────────────────────────────────────────────────────
// 3) Middleware только для определённого route
// ─────────────────────────────────────────────────────────────────────

function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Нет токена' });
  next();
}

app.get('/profil', authTekshir, (req, res) => {
  res.json({ xabar: 'Это — защищённая страница' });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — неправильный порядок middleware
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/profilXato', (req, res) => {
  res.json({ xabar: 'Должна была быть защищённой' });
});

function authTekshirXato(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Нет токена' });
  next();
}

app.use(authTekshirXato); // ❌ зарегистрирован ПОСЛЕ /profilXato —
// никогда не доходит до route, защита не работает.
*/

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3647: {
        "title": "Какой метод REST соответствует действию?",
        "description": "В конвенции REST, какой HTTP-метод используется для \"создания нового ресурса\"?",
        "hint": "GET — чтение, POST — создание, PUT/PATCH — обновление, DELETE — удаление.",
        "explanation": "В конвенции REST POST используется для создания нового ресурса. GET — для чтения, PUT/PATCH — для обновления, DELETE — для удаления.",
    },
    3648: {
        "title": "Что произойдёт, если в middleware не вызвать next()?",
        "description": "Если внутри функции middleware не вызван next() и ответ тоже не отправлен, что произойдёт?",
        "hint": "Вспомните урок 1 — если ответ не отправлен, запрос ждёт бесконечно.",
        "explanation": "next() передаёт запрос следующему middleware/route. Если он не вызван и ответ тоже не отправлен, запрос никогда не продолжится и \"зависнет\".",
    },
    3649: {
        "title": "Разница между req.params и req.query",
        "description": "Для запроса /users/5?faol=true, правильно сопоставьте: какая часть станет req.params, а какая req.query.",
        "hint": "Часть адреса, начинающаяся с : — params, часть после ? — query.",
    },
    3650: {
        "title": "Почему middleware обязательно нужно писать ДО защищаемого route?",
        "description": (
            "Если middleware authTekshir зарегистрирован через app.use() "
            "ПОСЛЕ route /profil, почему защита не сработает? Объясните "
            "своими словами."
        ),
        "expected_answer": "Express при получении запроса проверяет middleware и route в том порядке, в котором написан код, сверху вниз. Если route /profil зарегистрирован раньше middleware authTekshir, запрос к /profil вообще не доходит до authTekshir, а сразу обрабатывается собственным handler'ом /profil. authTekshir работает только для route, зарегистрированных ПОСЛЕ него, поэтому правильный порядок регистрации критически важен.",
        "hint": "Вспомните, в каком порядке Express проверяет route/middleware.",
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
