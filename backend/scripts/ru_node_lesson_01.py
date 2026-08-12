"""Russian translation for Node.js/Express Asoslari, lesson order=0 (L1)."""
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

LESSON_ID = 606

TITLE_RU = "1-Введение в Node.js и Express"

TEXT_RU = """\
<h2>Введение в Node.js и Express — первый сервер за 5 минут</h2>

<pre class="mermaid">
flowchart LR
    B["Браузер / fetch"] -->|запрос| S["Express сервер"]
    S -->|находит route| H["функция-обработчик"]
    H -->|res.send/json| B
</pre>

<p>До сих пор вы использовали JavaScript только <strong>в браузере</strong>. <code>Node.js</code> — среда, запускающая тот же самый JavaScript вне браузера, напрямую на вашем компьютере. <code>Express</code> — небольшая библиотека, построенная поверх Node, упрощающая написание сервера.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первый сервер</h4>
<pre><code>// Терминал:
mkdir mening-serverim && cd mening-serverim
npm init -y
npm install express</code></pre>

<pre><code>// server.js
const express = require('express');
const app = express();

app.get('/', (req, res) =&gt; {
  res.send('Привет, я сервер!');
});

app.listen(3000, () =&gt; {
  console.log('Сервер запущен: http://localhost:3000');
});</code></pre>

<pre><code>// Терминал:
node server.js
// Откройте в браузере: http://localhost:3000</code></pre>

<p>Поздравляем — это ваш первый backend-сервер. <code>app.get('/', handler)</code> означает "если кто-то отправит GET-запрос на адрес <code>/</code>, запусти эту функцию".</p>

<h4>БЛОК 2 — несколько route и JSON-ответ</h4>
<pre><code>app.get('/', (req, res) =&gt; {
  res.send('Главная страница');
});

app.get('/about', (req, res) =&gt; {
  res.send('Это мой первый Express-сервер');
});

app.get('/api/user', (req, res) =&gt; {
  res.json({ ism: 'Олим', yosh: 22 }); // JSON — стандартный формат для API
});</code></pre>

<p><code>res.send()</code> отправляет текст или HTML. <code>res.json()</code> отправляет объект в виде JSON и автоматически устанавливает заголовок <code>Content-Type: application/json</code>. Большинство современных backend'ов (работающих с фронтендом вроде React) возвращают только JSON, а не HTML.</p>

<h4>БЛОК 3 — nodemon: автоматический перезапуск при каждом изменении</h4>
<pre><code>npm install -D nodemon</code></pre>

<pre><code>// добавьте в package.json:
"scripts": {
  "dev": "nodemon server.js"
}</code></pre>

<pre><code>npm run dev
// Теперь при изменении server.js сервер перезапустится сам —
// не нужно каждый раз нажимать Ctrl+C и заново писать node server.js.</code></pre>

<h3>🐛 Намеренная ошибка — не отправить ответ (сервер "зависает")</h3>
<pre><code>app.get('/xato', (req, res) =&gt; {
  console.log('Запрос пришёл');
  // ❌ res.send() или res.json() не вызваны!
});</code></pre>

<p><strong>Результат:</strong> если открыть <code>/xato</code> в браузере — страница <strong>бесконечно</strong> остаётся в состоянии "загрузка". Никакого сообщения об ошибке, ничего не подсвечивается красным в консоли — потому что технически ничего "неправильного" нет, вы просто <strong>забыли отправить ответ</strong> на HTTP-запрос. Браузер продолжает ждать ответ, ждёт, ждёт... и в конце концов происходит timeout.</p>

<p>Это — самая распространённая начинающая ошибка в backend: <strong>каждый route handler обязательно должен один раз отправить ответ</strong> (<code>res.send()</code>, <code>res.json()</code>, <code>res.end()</code> и т.д.).</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое Node.js?</h4>
<p>Node.js — среда, берущая движок V8 JavaScript из браузера Chrome и запускающая его вне браузера. Благодаря этому можно писать одним и тем же языком JavaScript и фронтенд (в браузере), и backend (на сервере). Node работает <strong>в одном потоке (single-threaded)</strong>, но выполняет "тяжёлые" операции вроде чтения файлов или сетевых запросов <strong>не блокируя</strong> (non-blocking) — так эффективно обрабатывая множество запросов одновременно.</p>

<h4>2. Зачем нужен Express?</h4>
<p>Сервер можно написать и на чистом Node.js (через модуль <code>http</code>), но это требует много ручного кода. Express упрощает routing (какая функция отвечает за какой адрес), удобную работу с запросом/ответом, и цепочку middleware (в следующем уроке).</p>

<h4>3. package.json — "паспорт" проекта</h4>
<pre><code>{
  "name": "mening-serverim",
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  },
  "scripts": {
    "dev": "nodemon server.js"
  }
}</code></pre>
<p><code>dependencies</code> — пакеты, нужные в production (express). <code>devDependencies</code> — нужны только в процессе разработки (nodemon — не нужен на production-сервере). <code>scripts</code> — сокращения для команд вроде <code>npm run dev</code>.</p>

<h4>4. req и res — два основных аргумента каждого handler'а</h4>
<ul>
<li><code>req</code> (request) — информация о пришедшем запросе: <code>req.method</code>, <code>req.url</code>, в следующих уроках <code>req.body</code>/<code>req.params</code>/<code>req.query</code></li>
<li><code>res</code> (response) — для отправки ответа: <code>res.send()</code>, <code>res.json()</code>, <code>res.status(404).send(...)</code></li>
</ul>

<h4>5. Зачем нужен nodemon?</h4>
<p>Обычный <code>node server.js</code> запускает файл один раз. Если изменить код, чтобы увидеть изменения, нужно вручную остановить и перезапустить сервер. <code>nodemon</code> отслеживает файлы и <strong>автоматически</strong> перезапускает сервер при изменении.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Node.js — среда, запускающая JavaScript вне браузера</li>
<li>✅ Express — небольшая библиотека, упрощающая routing и работу с запросом/ответом</li>
<li>✅ <code>app.get(адрес, handler)</code> — обработка GET-запросов</li>
<li>✅ <code>res.send()</code> — текст/HTML, <code>res.json()</code> — отправка JSON-ответа</li>
<li>✅ Каждый handler обязательно должен один раз отправить ответ — иначе запрос "зависнет" навсегда</li>
<li>✅ <code>nodemon</code> — автоматически перезапускает сервер во время разработки</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 1: Введение в Node.js и Express
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

// ─────────────────────────────────────────────────────────────────────
// 1) Несколько простых route
// ─────────────────────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.send('Главная страница');
});

app.get('/about', (req, res) => {
  res.send('Это мой первый Express-сервер');
});

// ─────────────────────────────────────────────────────────────────────
// 2) JSON-ответ — стандарт для современных backend'ов
// ─────────────────────────────────────────────────────────────────────

app.get('/api/user', (req, res) => {
  res.json({ ism: 'Олим', yosh: 22 });
});

app.get('/api/users', (req, res) => {
  res.json([
    { id: 1, ism: 'Олим' },
    { id: 2, ism: 'Вали' },
  ]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка — не отправить ответ (запрос зависнет навсегда)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/xato', (req, res) => {
  console.log("Запрос пришёл");
  // ❌ res.send() или res.json() не вызваны!
  // Браузер навсегда останется в состоянии "загрузка", без какой-либо ошибки.
});
*/

// ✅ Правильно — всегда отправляйте ответ
app.get('/togri', (req, res) => {
  console.log("Запрос пришёл");
  res.send('Ответ отправлен!');
});

// ─────────────────────────────────────────────────────────────────────
// 4) Запуск сервера
// ─────────────────────────────────────────────────────────────────────

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Сервер запущен: http://localhost:${PORT}`);
});

// package.json:
// {
//   "dependencies": { "express": "^4.18.0" },
//   "devDependencies": { "nodemon": "^3.0.0" },
//   "scripts": { "dev": "nodemon server.js" }
// }
//
// Терминал:
//   npm install express
//   npm install -D nodemon
//   npm run dev
"""

EX = {
    3639: {
        "title": "Что такое Node.js?",
        "description": "Что такое Node.js на самом деле?",
        "hint": "Node.js — не браузер, но использует тот же JS-движок, что и в браузере.",
        "explanation": "Node.js — среда, берущая движок V8 браузера Chrome и запускающая его вне браузера, напрямую на компьютере. Благодаря этому можно писать backend тем же самым языком JavaScript.",
    },
    3640: {
        "title": "Что произойдёт, если handler не отправит ответ?",
        "description": "Если внутри route handler не вызваны res.send() или res.json(), что увидит пользователь в браузере?",
        "hint": "Браузер ждёт ответ — если ответ не приходит, он продолжает ждать.",
        "explanation": "Если ответ не отправлен, технически никакой ошибки нет — сервер просто не отправил ответ. Браузер продолжает ждать, пока в итоге не произойдёт timeout.",
    },
    3641: {
        "title": "Порядок запуска сервера",
        "description": "Расположите в правильном порядке этапы запуска нового Express-проекта с нуля.",
        "hint": "Сначала проект, потом библиотека, потом код, потом запуск.",
    },
    3642: {
        "title": "Почему каждый handler обязательно должен отправить ответ?",
        "description": (
            "Почему в Express каждый route handler обязательно должен один "
            "раз отправить ответ (res.send/json/end), и что произойдёт, если "
            "это правило не соблюдается? Объясните своими словами."
        ),
        "expected_answer": "Модель запрос-ответ HTTP работает так: браузер (или другой клиент) отправляет запрос и ждёт ответ. Если сервер не отправит никакого ответа, для клиента ничего не \"завершится\" — он продолжит ждать ответ, без какой-либо ошибки, пока соединение не истечёт по timeout. Это тихий (silent) баг, который трудно отследить, потому что ни на стороне сервера, ни на стороне клиента не появляется чёткого сообщения об ошибке.",
        "hint": "Подумайте, как работает модель запрос-ответ HTTP, и что делает клиент, если ответ не приходит.",
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
