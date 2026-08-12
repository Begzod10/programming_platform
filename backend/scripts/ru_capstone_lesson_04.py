"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=3 (L4)."""
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

LESSON_ID = 738

TITLE_RU = "4-Аутентификация"

TEXT_RU = """\
<h2>Этап 4: Аутентификация — JWT на backend, вход/защита на frontend</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /login"] --> JWT["создаётся JWT-токен"]
    JWT --> STORE["Frontend сохраняет токен"]
    STORE --> REQ["К каждому следующему запросу добавляется Authorization header"]
    REQ -->|нет header| REJECT["401 Unauthorized"]
</pre>

<p>TaskFlow теперь должен стать <strong>многопользовательским</strong> &mdash; каждый пользователь должен видеть только <strong>свои</strong> задачи. Для этого построим JWT-аутентификацию на backend, а на frontend &mdash; страницы входа/регистрации и <strong>защищённые</strong> запросы.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — backend: регистрация и создание JWT</h4>
<pre><code>// backend/routes/auth.js
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

router.post('/register', async (req, res) => {
  const { ism, email, parol } = req.body;
  const parol_hash = await bcrypt.hash(parol, 10);          // ❗ пароль НИКОГДА не хранится в открытом виде
  const natija = await pool.query(
    'INSERT INTO users (ism, email, parol_hash) VALUES ($1, $2, $3) RETURNING id, ism, email',
    [ism, email, parol_hash]
  );
  res.status(201).json(natija.rows[0]);
});

router.post('/login', async (req, res) => {
  const { email, parol } = req.body;
  const natija = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  const user = natija.rows[0];
  if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
    return res.status(401).json({ xato: "Email yoki parol noto'g'ri" });
  }
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, ism: user.ism });
});</code></pre>

<h4>БЛОК 2 — backend: защищённый маршрут (middleware)</h4>
<pre><code>// backend/middleware/auth.js
function autentifikatsiyaTalabQilish(req, res, next) {
  const authHeader = req.headers.authorization;             // ❗ ожидается в формате "Bearer <token>"
  if (!authHeader) return res.status(401).json({ xato: 'Token yo\\'q' });

  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = payload.userId;                              // ❗ передаёт userId следующим обработчикам
    next();
  } catch {
    res.status(401).json({ xato: 'Token yaroqsiz' });
  }
}

// server.js
app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const natija = await pool.query(
    'SELECT * FROM tasks WHERE user_id = $1', [req.userId]   // ❗ только задачи ЭТОГО пользователя
  );
  res.json(natija.rows);
});</code></pre>

<h4>БЛОК 3 — frontend: сохранение токена и добавление к каждому запросу</h4>
<pre><code>// frontend/src/features/authSlice.js
export const kirish = createAsyncThunk('auth/kirish', async ({ email, parol }) => {
  const javob = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, parol }),
  });
  const data = await javob.json();
  localStorage.setItem('token', data.token);                  // ❗ токен сохраняется в браузере
  return data;
});

// frontend/src/features/tasksSlice.js - ЗАЩИЩЁННЫЙ запрос
export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks`, {
    headers: { Authorization: `Bearer ${token}` },             // ❗ ОБЯЗАТЕЛЬНО - здесь отправляется токен
  });
  return await javob.json();
});</code></pre>

<h3>🐛 Намеренная ошибка — забыли добавить Authorization header</h3>
<pre><code>// tasklarniOlish() без Authorization header:
export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);   // ❌ НЕТ Authorization header!
  return await javob.json();
});

// Пользователь успешно вошёл, токен есть в localStorage -
// но так как он не отправляется в запросе:
// ❌ 401 Unauthorized: "Token yo'q"
// (Пользователь удивляется: "я же вошёл в систему"!)</code></pre>

<p><strong>Результат:</strong> само по себе хранение токена в <code>localStorage</code> <strong>ничего не гарантирует</strong> &mdash; backend ожидает токен через заголовок <code>Authorization</code> <strong>именно в каждом</strong> защищённом запросе. Даже если вход выполнен успешно и токен сохранён, если следующий вызов <code>fetch()</code> <strong>не добавляет</strong> этот заголовок, backend "не узнаёт" пользователя и возвращает <code>401</code> &mdash; это одна из самых распространённых ошибок интеграции во многих начинающих full-stack проектах.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему пароль хешируется через bcrypt, а не хранится обычным текстом?</h4>
<p>Если база данных станет доступной злоумышленникам, обычные (plain-text) пароли будут украдены мгновенно. <code>bcrypt.hash()</code> преобразует пароль в <strong>необратимую</strong> форму &mdash; даже если база станет доступной, восстановить настоящий пароль невозможно. При входе введённый пароль сравнивается с хешем через <code>bcrypt.compare()</code>.</p>

<h4>2. Что такое JWT и зачем он нужен?</h4>
<p>JWT (JSON Web Token) &mdash; "подписанный" сервером блок данных, обычно содержащий ID пользователя. Сервер каждый раз проверяет этот токен, подтверждая (через подпись), кто его создал &mdash; это позволяет проводить аутентификацию "без состояния" (stateless), не храня сессию на сервере.</p>

<h4>3. Что делает middleware (<code>autentifikatsiyaTalabQilish</code>)?</h4>
<p>Этот middleware запускается <strong>перед</strong> каждым защищённым маршрутом: берёт токен из заголовка <code>Authorization</code>, проверяет его, и если он верен, устанавливает <code>req.userId</code> и передаёт управление следующему обработчику. Это предотвращает ручную проверку токена в каждом маршруте (знакомый паттерн из курса Node.js).</p>

<h4>4. Почему важно <code>WHERE user_id = $1</code>?</h4>
<p>Без этого условия <code>GET /tasks</code> вернул бы задачи <strong>всех</strong> пользователей &mdash; это серьёзная проблема безопасности и конфиденциальности. Фильтрация по <code>req.userId</code> (полученному из JWT) обеспечивает, что каждый пользователь видит только <strong>свои</strong> данные.</p>

<h4>5. Почему без Authorization header возникает ошибка 401?</h4>
<p>Middleware <code>autentifikatsiyaTalabQilish</code> на backend ищет заголовок <code>Authorization</code> в <strong>каждом</strong> защищённом запросе. То, что токен хранится в браузере (<code>localStorage</code>), не означает, что этот заголовок добавляется <strong>автоматически</strong> &mdash; разработчик должен <strong>вручную</strong> добавлять его в <strong>каждый</strong> защищённый вызов <code>fetch()</code>. Если этот шаг пропущен, backend считает, что токена "нет".</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Пароли хешируются через <code>bcrypt.hash()</code>, а не хранятся в открытом виде</li>
<li>✅ JWT — "stateless" токен, подписанный сервером, содержащий ID пользователя</li>
<li>✅ Middleware проверяет токен перед защищёнными маршрутами</li>
<li>✅ <code>WHERE user_id = $1</code> обеспечивает, что каждый пользователь видит только свои данные</li>
<li>✅ Хранения токена недостаточно — его нужно вручную добавлять к каждому защищённому запросу через заголовок Authorization</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 4: Аутентификация - JWT на backend, вход на frontend
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/routes/auth.js
// ─────────────────────────────────────────────────────────────────────

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

router.post('/register', async (req, res) => {
  const { ism, email, parol } = req.body;
  const parol_hash = await bcrypt.hash(parol, 10);
  const natija = await pool.query(
    'INSERT INTO users (ism, email, parol_hash) VALUES ($1, $2, $3) RETURNING id, ism, email',
    [ism, email, parol_hash]
  );
  res.status(201).json(natija.rows[0]);
});

router.post('/login', async (req, res) => {
  const { email, parol } = req.body;
  const natija = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  const user = natija.rows[0];
  if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
    return res.status(401).json({ xato: "Email yoki parol noto'g'ri" });
  }
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, ism: user.ism });
});

// ─────────────────────────────────────────────────────────────────────
// 2) backend/middleware/auth.js
// ─────────────────────────────────────────────────────────────────────

function autentifikatsiyaTalabQilish(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ xato: "Token yo'q" });

  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = payload.userId;
    next();
  } catch {
    res.status(401).json({ xato: 'Token yaroqsiz' });
  }
}

// app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
//   const natija = await pool.query('SELECT * FROM tasks WHERE user_id = $1', [req.userId]);
//   res.json(natija.rows);
// });

// ─────────────────────────────────────────────────────────────────────
// 3) frontend/src/features/authSlice.js (в комментарии - createAsyncThunk)
// ─────────────────────────────────────────────────────────────────────

// export const kirish = createAsyncThunk('auth/kirish', async ({ email, parol }) => {
//   const javob = await fetch(`${API_URL}/login`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ email, parol }),
//   });
//   const data = await javob.json();
//   localStorage.setItem('token', data.token);
//   return data;
// });

// export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
//   const token = localStorage.getItem('token');
//   const javob = await fetch(`${API_URL}/tasks`, {
//     headers: { Authorization: `Bearer ${token}` },
//   });
//   return await javob.json();
// });

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - без Authorization header (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// export const tasklarniOlishXato = createAsyncThunk('tasks/olish', async () => {
//   const javob = await fetch(`${API_URL}/tasks`);   // НЕТ Authorization header!
//   return await javob.json();
// });
// ❌ 401 Unauthorized: "Token yo'q"
"""

TASK_TITLE_RU = "TaskFlow — JWT-аутентификация"

TASK_DESCRIPTION_RU = (
    "Постройте на backend эндпоинты /register и /login с JWT, хешируйте "
    "пароль через bcrypt. Напишите middleware для защищённых маршрутов и "
    "сделайте так, чтобы GET /tasks возвращал только задачи текущего "
    "пользователя. На frontend реализуйте формы входа/регистрации и "
    "добавление токена к каждому защищённому запросу."
)

TASK_REQUIREMENTS_RU = (
    "• POST /register — сохраняет пароль через bcrypt.hash()\n"
    "• POST /login — проверяет через bcrypt.compare(), возвращает JWT-токен\n"
    "• Middleware autentifikatsiyaTalabQilish — проверяет заголовок Authorization\n"
    "• GET /tasks — через WHERE user_id = $1 возвращает только задачи текущего пользователя\n"
    "• Frontend: формы входа/регистрации, токен сохраняется в localStorage\n"
    "• Ко всем защищённым запросам добавлен заголовок Authorization\n"
    "• Обновлён чеклист статуса в README.md"
)

TASK_TECHNOLOGIES_RU = "Node.js, Express, JWT (jsonwebtoken), bcrypt, React"

EX = {
    4294: {
        "title": "Почему пароль хешируется через bcrypt?",
        "description": "Почему пароль пользователя хранится через bcrypt.hash(), а не обычным текстом (plain-text)?",
        "hint": "Это учитывает ситуацию, когда база данных станет доступной злоумышленникам.",
        "explanation": "bcrypt.hash() преобразует пароль в необратимую форму — даже если база данных станет доступной, восстановить настоящий пароль невозможно.",
    },
    4295: {
        "title": "Почему важно WHERE user_id = $1?",
        "description": "Если в запросе GET /tasks нет условия WHERE user_id = $1, какая проблема возникнет?",
        "hint": "Это вопрос разделения данных в многопользовательской системе.",
        "explanation": "Без этого условия GET /tasks вернёт задачи всех пользователей — это серьёзная проблема безопасности/конфиденциальности, раскрывающая личные данные других пользователей.",
    },
    4296: {
        "title": "Расположите процесс входа в систему",
        "description": "Расположите процесс от отправки формы входа пользователем до защищённого запроса /tasks.",
        "hint": "",
        "explanation": "",
    },
    4297: {
        "title": "HTTP-заголовок для отправки токена",
        "description": "Через какой HTTP-заголовок frontend отправляет JWT-токен в защищённом запросе? (напишите название)",
        "hint": "Обычно отправляется в формате \"Bearer <token>\".",
        "expected_answer": "Authorization",
    },
    4298: {
        "title": "Почему без Authorization header возникает ошибка 401?",
        "description": (
            "Пользователь успешно вошёл в систему, токен сохранён в "
            "localStorage, но в функции tasklarniOlish() не добавлен "
            "заголовок Authorization. Почему в этом случае backend всё "
            "равно возвращает 401 Unauthorized, хотя пользователь "
            "\"вошёл в систему\"? Объясните своими словами."
        ),
        "hint": "Означает ли хранение токена в localStorage, что он АВТОМАТИЧЕСКИ добавляется к запросу?",
        "expected_answer": "Само по себе хранение токена в localStorage ничего не гарантирует — это просто текст, сохранённый в браузере. Middleware autentifikatsiyaTalabQilish на backend ищет токен именно через заголовок Authorization, в самом запросе. Если этот заголовок вручную не добавлен в вызов fetch(), токен вообще не доходит до backend — для backend это равносильно запросу без токена, поэтому он возвращает ошибку 401, даже если пользователь ранее успешно вошёл в систему и токен есть в браузере.",
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
