"""Russian translation for Node.js/Express Asoslari, lesson order=13 (L11, final)."""
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

LESSON_ID = 632

TITLE_RU = "11-Подготовка к деплою"

TEXT_RU = """\
<h2>Подготовка к деплою — перед выходом в production</h2>

<pre class="mermaid">
flowchart LR
    ENV[".env — секретные настройки"] --> APP["Express-приложение"]
    APP --> HEALTH["GET /health — проверка статуса"]
    APP --> LOG["Ошибки логируются"]
    APP -->|деплой| PROD["Production-сервер"]
</pre>

<p>На протяжении курса мы много раз упоминали секретные значения вроде <code>process.env.JWT_SECRET</code>. Теперь реализуем это полностью и разберём, как проверить приложение перед выходом в production.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — подключение файла .env через dotenv</h4>
<pre><code>// Терминал:
npm install dotenv</code></pre>

<pre><code>// файл .env (этот файл ОБЯЗАН быть в .gitignore!)
DATABASE_URL=postgresql://user:parol@localhost:5432/mening_bazam
JWT_SECRET=juda-maxfiy-va-uzun-satr-2024
CORS_ORIGINS=http://localhost:3000,https://mysite.uz
PORT=5000</code></pre>

<pre><code>// server.js — самая первая строка
require('dotenv').config(); // ❗ вызывается ПЕРЕД всем остальным

const express = require('express');
const app = express();

const PORT = process.env.PORT || 3000;</code></pre>

<h4>БЛОК 2 — health-check endpoint</h4>
<pre><code>app.get('/health', (req, res) =&gt; {
  res.status(200).json({
    status: 'ok',
    vaqt: new Date().toISOString(),
  });
});
// ❗ Системы деплоя (например, Docker, load balancer) регулярно
// отправляют запрос на этот адрес, проверяя, что сервер "жив".</code></pre>

<h4>БЛОК 3 — скрипты package.json и production start</h4>
<pre><code>{
  "scripts": {
    "dev": "nodemon server.js",
    "start": "node server.js"
  }
}</code></pre>
<pre><code>// Терминал (на production-сервере):
npm install --production   // devDependencies (например, nodemon) не устанавливаются
npm start                  // node server.js — НЕ nodemon!</code></pre>

<h3>🐛 Намеренная ошибка — секретный ключ в коде и коммит в git</h3>
<pre><code>// ❌ прямо внутри server.js
const JWT_SECRET = 'mening-maxfiy-kalitim-123'; // ❌ записан в коде!

// ❌ файл .env не в .gitignore — попадёт в репозиторий через git add .
// $ git status
//   modified: .env    ← ЭТОГО НЕ ДОЛЖНО БЫТЬ ВИДНО!</code></pre>

<p><strong>Результат:</strong> если файл <code>.env</code> случайно попадёт на GitHub (даже в приватный репозиторий), секретный ключ JWT, пароль базы данных и другие секретные данные окажутся полностью открытыми. Удалить их полностью из истории репозитория (git history) впоследствии тоже сложно — то, что однажды закоммичено, может остаться там «навсегда». Поэтому <code>.env</code> должен быть добавлен в <code>.gitignore</code> <strong>с самого первого дня</strong> проекта, а не после.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему require('dotenv').config() — самая первая строка?</h4>
<p>Этот вызов читает файл <code>.env</code> и загружает его значения в <code>process.env</code>. Если он вызван после другого кода, тот код может успеть прочитать <code>process.env.JWT_SECRET</code> как <code>undefined</code>.</p>

<h4>2. .gitignore — почему это важно?</h4>
<pre><code># файл .gitignore
.env
node_modules/</code></pre>
<p>Файлы, добавленные в <code>.gitignore</code>, игнорируются при <code>git add</code>. <code>.env</code> никогда не должен попадать в git-репозиторий — вместо него коммитится <code>.env.example</code> (без реальных значений, только с именами ключей).</p>

<h4>3. Зачем нужен health-check?</h4>
<p>В production-среде (Docker, Kubernetes, load balancer) система автоматически проверяет, «жив» ли сервер. Без простого эндпоинта вроде <code>/health</code> у системы нет удобного способа узнать, действительно ли сервер работает.</p>

<h4>4. npm start vs npm run dev — в чём разница</h4>
<p><code>nodemon</code> удобен для разработки (автоматический перезапуск), но в production он лишь расходует ресурсы и следить за файлами не требуется. В production используется обычный <code>node server.js</code> (через <code>npm start</code>).</p>

<h4>5. Чек-лист перед production (кратко)</h4>
<ul>
<li>Все секретные значения в <code>.env</code>, добавленном в <code>.gitignore</code></li>
<li>Эндпоинт <code>/health</code> существует</li>
<li>Централизованный error middleware (урок 7) работает</li>
<li>CORS ограничен только нужными доменами (урок 10)</li>
<li><code>npm start</code> запускается без <code>nodemon</code>, простым <code>node</code></li>
</ul>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>dotenv</code> загружает значения из файла <code>.env</code> в <code>process.env</code></li>
<li>✅ <code>.env</code> никогда не коммитится в git — добавляется в <code>.gitignore</code> с первого дня</li>
<li>✅ Эндпоинт <code>/health</code> — признак «живости» сервера для систем деплоя</li>
<li>✅ В production используется <code>npm start</code> (обычный <code>node</code>), а не <code>nodemon</code></li>
<li>✅ Это — этап подготовки к production всего, что изучено за курс (routing, DB, auth, CORS, обработка ошибок)</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 11: Подготовка к деплою
// ════════════════════════════════════════════════════════════════════

require('dotenv').config(); // ❗ самая первая строка

const express = require('express');
const cors = require('cors');
const app = express();

const PORT = process.env.PORT || 3000;

// ─────────────────────────────────────────────────────────────────────
// 1) CORS + JSON — как в изученных уроках
// ─────────────────────────────────────────────────────────────────────

const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({ origin: allowedOrigins, credentials: true }));
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 2) Health-check endpoint
// ─────────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    vaqt: new Date().toISOString(),
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Простой route
// ─────────────────────────────────────────────────────────────────────

app.get('/api/products', (req, res) => {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});

// ─────────────────────────────────────────────────────────────────────
// 4) Централизованный error middleware (как в уроке 7)
// ─────────────────────────────────────────────────────────────────────

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка — секретный ключ в коде (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
const JWT_SECRET_XATO = 'mening-maxfiy-kalitim-123'; // ❌ записан в коде, не в .env!
// Это значение попадёт в git-репозиторий и никогда не станет по-настоящему секретным.
*/

app.listen(PORT, () => {
  console.log(`Сервер запущен: http://localhost:${PORT}`);
});

// package.json:
// {
//   "scripts": {
//     "dev": "nodemon server.js",
//     "start": "node server.js"
//   }
// }
//
// На production-сервере:
//   npm install --production
//   npm start
"""

EX = {
    3743: {
        "title": "Куда пишется require('dotenv').config()?",
        "description": "Куда обычно пишется require('dotenv').config() для загрузки значений .env через dotenv?",
        "hint": "Если вызвать позже, предыдущий код ещё не сможет получить значения process.env.",
        "explanation": "require('dotenv').config() должен вызываться в самом начале файла, иначе код, написанный до него, при попытке прочитать значения .env через process.env получит undefined, так как они ещё не загружены.",
    },
    3744: {
        "title": "Где обязательно должен быть указан файл .env?",
        "description": "Куда нужно добавить файл .env, чтобы он не попал в git-репозиторий?",
        "hint": "Файлы, добавленные в .gitignore, игнорируются при git add.",
        "explanation": "Файл .env обязательно должен быть добавлен в .gitignore, иначе он попадёт в репозиторий через git add ., и все секретные данные (пароли, ключи) окажутся открытыми.",
    },
    3745: {
        "title": "Расположите порядок запуска сервера (dev и production)",
        "description": "Упорядочите шаги от разработки проекта до его вывода в production.",
        "hint": "Сначала разработка, затем подготовка настроек, затем вывод в production.",
    },
    3746: {
        "title": "Что произойдёт, если .env случайно попадёт на GitHub?",
        "description": (
            "Если файл .env, не добавленный в .gitignore, случайно попадёт "
            "на GitHub (даже в приватный репозиторий), почему это серьёзная "
            "проблема? Что нужно было сделать для предотвращения этого? "
            "Объясните своими словами."
        ),
        "expected_answer": "Если файл .env попадёт в git-репозиторий, все содержащиеся в нём секретные данные — секретный ключ JWT, пароль базы данных, API-ключи — станут доступны каждому, у кого есть доступ к репозиторию, даже если репозиторий приватный (например, коллегам, участникам, добавленным позже, или если репозиторий случайно станет публичным). Хуже того, история git обычно сохраняется — даже если позже удалить файл, он может остаться в предыдущих коммитах, и полностью убрать его из истории — сложный процесс. Чтобы этого избежать, файл .env нужно было добавить в .gitignore в САМОМ НАЧАЛЕ проекта, до первого коммита.",
        "hint": "История git — то, что закоммичено, не исчезает легко и полностью.",
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
