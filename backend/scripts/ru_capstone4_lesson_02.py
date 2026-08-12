"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=1 (L2)."""
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

LESSON_ID = 774

TITLE_RU = "2-Backend API (Express + TypeScript)"

TEXT_RU = """\
<h2>Этап 2: Backend API (Express + TypeScript) — разрыв между интерфейсом и runtime</h2>

<pre class="mermaid">
flowchart LR
    CLIENT["Клиент: отправляет JSON неправильной формы"] --> ROUTE["POST /issues"]
    ROUTE --> IFACE{"req.body: 'типизирован' как CreateIssueBody"}
    IFACE -->|"TypeScript: 'OK, тип совпадает'"| HANDLER["используется внутри handler'а"]
    HANDLER --> CRASH["Runtime: неожиданное значение - ошибка или неверный результат"]
</pre>

<p>В курсе Node.js/Express вы уже изучили роутинг и middleware, а в курсе TypeScript Asoslari — интерфейсы. На этом уроке вы объединяете оба: даёте эндпоинтам Express типы через TypeScript-интерфейсы. Но именно здесь идея, с которой вы познакомились на 1-м уроке, впервые проявляется <strong>внутри кода</strong>: написать интерфейс — это <strong>не то же самое</strong>, что провалидировать данные.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — настройка Express + TypeScript</h4>
<pre><code># Terminal:
cd backend
npm init -y
npm install express
npm install -D typescript ts-node @types/express @types/node

# backend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true
  }
}</code></pre>

<h4>БЛОК 2 — POST /issues: типизация тела запроса через интерфейс</h4>
<pre><code>// backend/src/server.ts
import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const app = express();
app.use(express.json());

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

let issues: Issue[] = [];
let nextId = 1;

app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;   // ❗ TS "верит" - но не проверяет!

  const issue: Issue = {
    id: nextId++,
    title,
    description,
    status: 'open',
    assigneeId: null,
    reporterId,
    createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});</code></pre>

<h4>БЛОК 3 — GET /issues: ответ с общим типом Issue</h4>
<pre><code>app.get('/issues', (req: Request, res: Response) => {
  res.json(issues);   // ❗ TypeScript знает "issues это Issue[]", потому что так объявлено выше
});

app.listen(4000, () => console.log('IssueForge API: http://localhost:4000'));</code></pre>

<h3>🐛 Намеренная ошибка — считать, что интерфейс заменяет "валидацию"</h3>
<pre><code>app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;

  // ❌ Никакой проверки нет - разработчик "верит", что раз TypeScript
  // сказал "CreateIssueBody", то эти поля точно придут правильными.
  const issue: Issue = {
    id: nextId++, title, description, status: 'open',
    assigneeId: null, reporterId, createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});

// Если клиент отправит ТАКОЙ запрос (title вообще отсутствует, reporterId - строка):
// curl -X POST http://localhost:4000/issues -H "Content-Type: application/json" \\
//   -d '{"description": "есть ошибка", "reporterId": "два"}'
//
// ❌ tsc ЭТОГО ВООБЩЕ НЕ ОБНАРУЖИТ - потому что tsc работает во время
//    компиляции, а это - реальный запрос во время RUNTIME. title = undefined,
//    reporterId = "два" (строка, не число!) - но программа "успешно"
//    вернёт 201, сломанный issue будет сохранён.</code></pre>

<p><strong>Результат:</strong> "типизация" <code>req.body</code> через <code>Request&lt;{}, {}, CreateIssueBody&gt;</code> помогает TypeScript только <strong>во время компиляции</strong> — например, если вы напишете <code>req.body.titel</code> (с опечаткой), <code>tsc</code> это ОБНАРУЖИТ, потому что в <code>CreateIssueBody</code> нет поля <code>titel</code>. Но <strong>реальное runtime-значение</strong> <code>req.body</code> — это просто JSON-объект, распарсенный через <code>express.json()</code>, <strong>без какой-либо проверки</strong>. Если клиент вообще не отправит <code>title</code> или отправит <code>reporterId</code> строкой вместо числа, TypeScript этого <strong>никогда</strong> не поймает — потому что интерфейс уже "выполнил свою роль" во время компиляции и полностью отсутствует в скомпилированном <code>.js</code> файле.</p>

<h3>Теперь объясним</h3>

<h4>1. Что на самом деле говорит TypeScript запись <code>Request&lt;{}, {}, CreateIssueBody&gt;</code>?</h4>
<p>Эта запись просто говорит TypeScript: <em>"если я обращусь к <code>req.body</code> как к <code>CreateIssueBody</code>, считай, что следующие поля (<code>title</code>, <code>description</code>, <code>reporterId</code>) существуют"</em>. Это — <strong>предположение</strong>, а не гарантия. Компилятор вам верит, потому что другого способа проверки у него нет.</p>

<h4>2. Каково реальное runtime-значение <code>req.body</code>?</h4>
<p>Middleware <code>express.json()</code> преобразует пришедший JSON-текст в обычный JavaScript-объект через <code>JSON.parse()</code> и кладёт его в <code>req.body</code>. Это — объект <strong>без какой-либо гарантированной структуры</strong>. Дженерик <code>Request&lt;{}, {}, CreateIssueBody&gt;</code> лишь <strong>указывает</strong> TypeScript "считай его таким", но это <strong>никто не проверяет</strong>.</p>

<h4>3. Почему написание интерфейса — это не то же самое, что валидация?</h4>
<p>Интерфейс — это описание структуры <strong>во время компиляции</strong>. Валидация — это процесс проверки реальных значений <strong>во время выполнения (runtime)</strong>, для каждого пришедшего запроса (например: <code>typeof title === 'string'</code>, <code>title.length &gt; 0</code>). Одно не заменяет другое — они работают в <strong>совершенно разное время</strong>.</p>

<h4>4. Что может произойти без runtime-валидации?</h4>
<p>Данные неправильной формы (например, отсутствующий <code>title</code> или <code>reporterId</code>-строка) <strong>сохраняются</strong> без какой-либо ошибки в базу данных (или, в этом уроке, в массив в памяти). Ошибка проявляется не сразу, а <strong>позже</strong> — например, когда frontend попытается отобразить этот <code>issue</code> или когда будет выполняться поиск по <code>reporterId</code> как по числу — а это усложняет поиск истинного источника ошибки.</p>

<h4>5. Чем это отличается от "намеренной сложности" 1-го урока?</h4>
<p>На 1-м уроке проблема была <strong>потенциальной</strong> (интерфейсы ещё не синхронизированы, но пока ничего "не сломано"). На этом уроке ошибка — в <strong>реальном, работающем коде</strong>: на этот раз вы видите самое большое ограничение TypeScript "вживую", через эндпоинт, который написали сами.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>Request&lt;{}, {}, T&gt;</code> — способ типизировать тело запроса в Express</li>
<li>✅ Это лишь <strong>предположение</strong> во время компиляции, а не <strong>гарантия</strong> во время выполнения</li>
<li>✅ Реальное runtime-значение <code>req.body</code> — обычный JSON-объект, ничем не проверенный</li>
<li>✅ Интерфейс (во время компиляции) и валидация (во время выполнения) — два <strong>совершенно разных</strong> понятия</li>
<li>✅ Без runtime-валидации данные неправильной формы сохраняются без ошибок, и проблема проявляется позже и в другом месте</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 2: Backend API (Express + TypeScript)
// ════════════════════════════════════════════════════════════════════

import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) Интерфейс для тела запроса
// ─────────────────────────────────────────────────────────────────────

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

let issues: Issue[] = [];
let nextId = 1;

// ─────────────────────────────────────────────────────────────────────
// 2) POST /issues - типизирован, но БЕЗ ВАЛИДАЦИИ
// ─────────────────────────────────────────────────────────────────────

app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;

  const issue: Issue = {
    id: nextId++,
    title,
    description,
    status: 'open',
    assigneeId: null,
    reporterId,
    createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});

// ─────────────────────────────────────────────────────────────────────
// 3) GET /issues - с общим типом Issue
// ─────────────────────────────────────────────────────────────────────

app.get('/issues', (req: Request, res: Response) => {
  res.json(issues);
});

app.listen(4000, () => console.log('IssueForge API: http://localhost:4000'));

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - запрос без runtime-валидации (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// curl -X POST http://localhost:4000/issues -H "Content-Type: application/json" \\
//   -d '{"description": "есть ошибка", "reporterId": "два"}'
//
// title = undefined, reporterId = "два" (строка!) - но tsc НЕ МОЖЕТ
// обнаружить это во время компиляции, потому что это реальный runtime-
// запрос. Программа вернёт "успешный" ответ 201.
"""

EX = {
    4474: {
        "title": "Что означает Request<{}, {}, CreateIssueBody>?",
        "description": "В записи app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res) => {...}) что на самом деле сообщает этот дженерик TypeScript'у?",
        "hint": "Это помощь во время компиляции, а не проверка во время выполнения.",
        "explanation": "Request<{}, {}, CreateIssueBody> просто говорит TypeScript, что можно обращаться к req.body как к этому интерфейсу - это предположение во время компиляции, а не проверка во время выполнения.",
    },
    4475: {
        "title": "Каков реальный runtime-тип req.body?",
        "description": "Каким на самом деле (во время выполнения) является req.body, пришедший через middleware express.json()?",
        "hint": "Что делает express.json() - во что превращает JSON-текст?",
        "explanation": "express.json() превращает пришедший JSON-текст в обычный JavaScript-объект через JSON.parse() - это значение без гарантированной структуры, интерфейс лишь даёт указание TypeScript.",
    },
    4476: {
        "title": "Расположите порядок обработки неверного запроса",
        "description": "Расположите порядок обработки запроса POST /issues без title и с reporterId в виде строки (в коде без валидации).",
        "hint": "",
        "explanation": "",
    },
    4477: {
        "title": "Основное различие между интерфейсом и валидацией",
        "description": "В какое время работает интерфейс, а в какое - валидация? (напишите оба слова подряд, через запятую, например: во время X, во время Y)",
        "hint": "Одно работает при запуске tsc, другое - при запуске программы.",
        "expected_answer": "во время компиляции, во время выполнения",
    },
    4478: {
        "title": "Почему опасно, когда данные неправильной формы сохраняются без ошибок?",
        "description": (
            "Если эндпоинт POST /issues не имеет runtime-валидации, и "
            "клиент отправляет запрос без title или с reporterId "
            "неправильного типа, к какой долгосрочной проблеме это может "
            "привести? Объясните своими словами."
        ),
        "hint": "Ошибка проявляется сразу, или позже, в другом месте?",
        "expected_answer": "Из-за отсутствия runtime-валидации данные неправильной формы (например, title = undefined или reporterId в виде строки) сохраняются без какой-либо ошибки, и возвращается успешный ответ 201 - ошибка НЕ проявляется сразу. Проблема проявляется только ПОЗЖЕ, например когда frontend попытается отобразить этот issue и получит ошибку из-за отсутствующего title, или когда будет выполняться поиск/сравнение по reporterId как по числу. Это значительно усложняет поиск истинного источника ошибки, потому что между местом, где проблема проявилась, и её настоящей причиной (изначальным неверным POST-запросом) - большая дистанция во времени и месте.",
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
        TASK_TITLE_RU = "IssueForge — Backend API (Express + TypeScript)"
        TASK_DESCRIPTION_RU = (
            "На основе shared/types.ts из 1-го этапа создайте Express + "
            "TypeScript backend: напишите эндпоинты POST /issues "
            "(типизированный интерфейсом CreateIssueBody) и GET /issues "
            "(возвращающий Issue[]). Пока достаточно хранения в памяти "
            "(массив) — PostgreSQL добавится на 3-м этапе."
        )
        TASK_REQUIREMENTS_RU = (
            "• backend/tsconfig.json: настроено \"strict\": true\n"
            "• POST /issues — типизирован через Request<{}, {}, CreateIssueBody>\n"
            "• GET /issues — ответ соответствует типу Issue[] из shared/types.ts\n"
            "• Сервер запускается без ошибок через npm run dev (ts-node)\n"
            "• Обновлён чеклист статуса в README.md\n"
            "• В README показан хотя бы один вручную протестированный пример (например, команда curl)"
        )
        TASK_TECHNOLOGIES_RU = "Node.js, Express, TypeScript, ts-node"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
