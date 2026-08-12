"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=2 (L3)."""
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

LESSON_ID = 736

TITLE_RU = "3-React frontend"

TEXT_RU = """\
<h2>Этап 3: React frontend — подключение к API из этапа 2</h2>

<pre class="mermaid">
flowchart LR
    REACT["React (localhost:3001)"] -->|fetch| API["Express API (localhost:3000)"]
    API -->|без CORS header| BLOCKED["Браузер БЛОКИРУЕТ запрос"]
    API -->|с CORS header| OK["Данные успешно возвращаются"]
</pre>

<p>Теперь подключимся к backend API, готовому с этапа 2, через <strong>React</strong> frontend. На курсе React и Redux Toolkit вы уже изучили <code>createAsyncThunk</code> &mdash; на этот раз вы используете его с <strong>реальным, написанным вами</strong> backend, и познакомитесь с проблемой <strong>CORS</strong>, возникающей, когда frontend и backend работают на разных портах.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — получение данных из реального API через createAsyncThunk</h4>
<pre><code>// frontend/src/features/tasksSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';   // ❗ настраивается через .env

export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);          // ❗ реальный эндпоинт из этапа 2
  if (!javob.ok) throw new Error('Tasklarni olishda xato');
  return await javob.json();
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { royxat: [], holat: 'idle' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(tasklarniOlish.pending, (state) => { state.holat = 'yuklanmoqda'; })
      .addCase(tasklarniOlish.fulfilled, (state, action) => {
        state.holat = 'muvaffaqiyatli';
        state.royxat = action.payload;
      })
      .addCase(tasklarniOlish.rejected, (state) => { state.holat = 'xato'; });
  },
});

export default tasksSlice.reducer;</code></pre>

<h4>БЛОК 2 — использование в компоненте</h4>
<pre><code>// frontend/src/components/TaskRoyxati.jsx
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { tasklarniOlish } from '../features/tasksSlice';

function TaskRoyxati() {
  const dispatch = useDispatch();
  const { royxat, holat } = useSelector((state) => state.tasks);

  useEffect(() => {
    dispatch(tasklarniOlish());                // ❗ отправляет запрос к API при загрузке компонента
  }, [dispatch]);

  if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;

  return (
    <ul>
      {royxat.map((task) => (
        <li key={task.id}>{task.sarlavha} ({task.category_nomi})</li>
      ))}
    </ul>
  );
}</code></pre>

<h4>БЛОК 3 — включение CORS на backend</h4>
<pre><code>// backend/server.js
const cors = require('cors');
const app = express();

app.use(cors({
  origin: 'http://localhost:3001',   // ❗ разрешает запросы ТОЛЬКО с адреса frontend
}));
app.use(express.json());
// ... остальные маршруты ...</code></pre>

<h3>🐛 Намеренная ошибка — забыли настроить CORS на backend</h3>
<pre><code>// backend/server.js - БЕЗ использования cors():
const app = express();
app.use(express.json());
app.get('/tasks', async (req, res) => { /* ... */ });

// Если в React (localhost:3001) вызвать fetch('http://localhost:3000/tasks'):
// ❌ В консоли браузера: Access to fetch at 'http://localhost:3000/tasks' from
//    origin 'http://localhost:3001' has been blocked by CORS policy
// (На вкладке Network запрос выглядит "отправленным", но ответ БЛОКИРУЕТСЯ браузером!)</code></pre>

<p><strong>Результат:</strong> браузеры соблюдают правило безопасности <strong>Same-Origin Policy</strong> &mdash; по умолчанию, даже если страница с одного <strong>origin</strong> (протокол+домен+порт) может отправить запрос на другой origin, она <strong>не может прочитать ответ</strong>, если сервер явно это не разрешил. React (<code>localhost:3001</code>) и Express (<code>localhost:3000</code>) работают на <strong>разных портах</strong>, поэтому считаются <strong>разными origin</strong>. Если backend через middleware <code>cors()</code> явно не скажет "я разрешаю этот origin", браузер <strong>не передаст</strong> ответ JavaScript-коду &mdash; это не ошибка сервера, а механизм безопасности браузера.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему API_URL настраивается через .env, а не прописывается жёстко в коде?</h4>
<p>В разработке API находится на <code>localhost:3000</code>, но в production (урок 6) он будет на совершенно другом домене. Настройка через <code>.env</code> позволяет использовать разные среды (разработка/production), не изменяя код, а лишь заменяя переменную окружения.</p>

<h4>2. Зачем нужны три состояния createAsyncThunk (pending/fulfilled/rejected)?</h4>
<p>Сетевой запрос <strong>занимает время</strong> и может <strong>завершиться неудачей</strong>. <code>pending</code> &mdash; для показа состояния "загрузка", <code>fulfilled</code> &mdash; для сохранения успешных данных, <code>rejected</code> &mdash; для показа ошибки пользователю. Все три вместе позволяют правильно управлять пользовательским опытом (индикатор загрузки, сообщение об ошибке).</p>

<h4>3. Что такое CORS и зачем он нужен?</h4>
<p>CORS (Cross-Origin Resource Sharing) &mdash; механизм, разрешающий браузеру прочитать в JavaScript-коде ответ, пришедший с <strong>другого origin</strong>. Сервер должен отправить заголовок <code>Access-Control-Allow-Origin</code> &mdash; middleware <code>cors()</code> добавляет его автоматически.</p>

<h4>4. Почему ошибку CORS путают с "сервер не работает"?</h4>
<p>На вкладке Network браузера видно, что запрос <strong>отправлен и сервер вернул ответ</strong> (статус может быть даже 200) &mdash; но браузер <strong>отказывается передать</strong> этот ответ React-коду. Это сбивает с толку начинающих разработчиков, которые думают "сервер не работает", хотя на самом деле проблема <strong>только</strong> в разрешении CORS.</p>

<h4>5. Почему явно указывается origin: 'http://localhost:3001'?</h4>
<p>Через <code>cors({ origin: '...' })</code> разрешаются запросы <strong>только</strong> с указанного origin &mdash; это <strong>безопаснее</strong>, чем использовать <code>cors()</code> без параметров (открыто для всех origin), особенно в production при работе с реальными данными пользователей.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>createAsyncThunk</code> использован с реальным backend API — три состояния pending/fulfilled/rejected</li>
<li>✅ Адрес API настраивается через <code>.env</code>, а не прописывается жёстко в коде</li>
<li>✅ CORS — механизм безопасности, основанный на Same-Origin Policy браузера</li>
<li>✅ Разные порты — разные origin, и это требует разрешения CORS</li>
<li>✅ Ошибка CORS блокируется браузером, а не сервером (на вкладке Network запрос может выглядеть "отправленным")</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 3: React frontend - подключение к backend API
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) frontend/src/features/tasksSlice.js
// ─────────────────────────────────────────────────────────────────────

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);
  if (!javob.ok) throw new Error('Tasklarni olishda xato');
  return await javob.json();
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { royxat: [], holat: 'idle' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(tasklarniOlish.pending, (state) => { state.holat = 'yuklanmoqda'; })
      .addCase(tasklarniOlish.fulfilled, (state, action) => {
        state.holat = 'muvaffaqiyatli';
        state.royxat = action.payload;
      })
      .addCase(tasklarniOlish.rejected, (state) => { state.holat = 'xato'; });
  },
});

export default tasksSlice.reducer;

// ─────────────────────────────────────────────────────────────────────
// 2) frontend/src/components/TaskRoyxati.jsx (в комментарии - JSX)
// ─────────────────────────────────────────────────────────────────────

// function TaskRoyxati() {
//   const dispatch = useDispatch();
//   const { royxat, holat } = useSelector((state) => state.tasks);
//
//   useEffect(() => {
//     dispatch(tasklarniOlish());
//   }, [dispatch]);
//
//   if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;
//
//   return (
//     <ul>
//       {royxat.map((task) => (
//         <li key={task.id}>{task.sarlavha} ({task.category_nomi})</li>
//       ))}
//     </ul>
//   );
// }

// ─────────────────────────────────────────────────────────────────────
// 3) backend/server.js - включение CORS
// ─────────────────────────────────────────────────────────────────────

// const cors = require('cors');
// app.use(cors({ origin: 'http://localhost:3001' }));

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - забыли CORS (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// В backend/server.js БЕЗ cors():
// Если из React вызвать fetch('http://localhost:3000/tasks'):
// ❌ Access to fetch at 'http://localhost:3000/tasks' from origin
//    'http://localhost:3001' has been blocked by CORS policy
"""

TASK_TITLE_RU = "TaskFlow — React frontend подключён к backend"

TASK_DESCRIPTION_RU = (
    "Создайте tasksSlice в React + Redux Toolkit, получите данные через "
    "createAsyncThunk из реального эндпоинта GET /tasks этапа 2 и покажите "
    "их в виде списка. Правильно настройте CORS на backend, управляйте "
    "адресом API через .env."
)

TASK_REQUIREMENTS_RU = (
    "• frontend/src/features/tasksSlice.js: tasklarniOlish через createAsyncThunk\n"
    "• Все три состояния pending/fulfilled/rejected правильно обрабатываются (загрузка, список, ошибка)\n"
    "• Компонент показывает список задач вместе с category_nomi\n"
    "• Адрес API настроен через .env (REACT_APP_API_URL), не прописан жёстко в коде\n"
    "• Middleware cors() на backend настроен с правильным origin\n"
    "• Обновлён чеклист статуса в README.md"
)

TASK_TECHNOLOGIES_RU = "React, Redux Toolkit, createAsyncThunk, cors (Express)"

EX = {
    4284: {
        "title": "Почему API_URL настраивается через .env?",
        "description": "В чём основная причина использования process.env.REACT_APP_API_URL?",
        "hint": "На этапе 6 API будет на совершенно другом домене.",
        "explanation": "Настройка адреса API через .env позволяет использовать разные среды (разработка/production), не изменяя код, а лишь заменяя переменную окружения.",
    },
    4285: {
        "title": "Почему возникает ошибка CORS?",
        "description": "Почему между React (localhost:3001) и Express (localhost:3000) возникает ошибка CORS?",
        "hint": "Это связано с политикой безопасности браузера.",
        "explanation": "React и Express работают на разных портах, поэтому считаются разными origin. По правилу Same-Origin Policy браузера, если сервер явно не даёт разрешение CORS, браузер не передаёт ответ JavaScript-коду.",
    },
    4286: {
        "title": "Расположите состояния при dispatch(tasklarniOlish())",
        "description": "Расположите процесс от вызова dispatch(tasklarniOlish()) до появления данных в компоненте.",
        "hint": "",
        "explanation": "",
    },
    4287: {
        "title": "Express middleware для включения CORS",
        "description": "Напишите название npm-пакета/middleware, используемого на backend для разрешения запросов с другого origin.",
        "hint": "Используется в форме app.use(___()).",
        "expected_answer": "cors",
    },
    4288: {
        "title": "Почему ошибку CORS путают с \"сервер не работает\"?",
        "description": (
            "На вкладке Network браузера запрос fetch('http://localhost:3000/tasks') "
            "выглядит \"отправленным\" и может даже показывать статус 200, "
            "но всё равно возникает ошибка CORS. Почему эту ситуацию "
            "часто неправильно понимают как \"сервер не работает\"? "
            "Объясните своими словами."
        ),
        "hint": "При ошибке CORS сервер вообще НЕ ВЕРНУЛ ответ, или вернул, но браузер его заблокировал?",
        "expected_answer": "При ошибке CORS сервер мог реально принять запрос и даже вернуть ответ (поэтому на вкладке Network может отображаться статус 200) — проблема не в сервере, а в самом браузере. По правилу Same-Origin Policy, если в ответе сервера нет правильного заголовка Access-Control-Allow-Origin, браузер отказывается передать этот ответ в JavaScript-код (например в часть .then() у fetch()). Начинающие разработчики часто понимают это как \"сервер не работает\", потому что данные не приходят на стороне React, но на самом деле сервер отработал правильно — проблема только в отсутствии разрешения CORS между браузером и сервером.",
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
