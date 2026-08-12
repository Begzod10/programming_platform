"""Russian translation for Node.js/Express Asoslari, lesson order=10 (L9)."""
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

LESSON_ID = 626

TITLE_RU = "9-Защищённые route'ы и цепочка middleware"

TEXT_RU = """\
<h2>Protected routes — защищённые route'ы и цепочка middleware</h2>

<pre class="mermaid">
flowchart LR
    Req["Запрос"] --> Auth["authMiddleware — проверяет токен"]
    Auth -->|верно| Handler["Route handler — req.user доступен"]
    Auth -->|неверно| Err["401 — next(err)"]
</pre>

<p>В уроке 8 мы проверяли токен внутри одного route. Но если нужно защитить много route'ов, повторять проверку в каждом неудобно. В этом уроке создадим <strong>переиспользуемый auth middleware</strong> и применим его только к нужным route'ам.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — middleware/auth.js: переиспользуемый middleware</h4>
<pre><code>// middleware/auth.js
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader &amp;&amp; authHeader.split(' ')[1];
  if (!token) {
    const err = new Error('Token yo\\'q'); err.status = 401; return next(err);
  }
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.userId }; // ❗ следующие handler'ы используют req.user
    next();
  } catch {
    const err = new Error('Token noto\\'g\\'ri yoki muddati o\\'tgan');
    err.status = 401;
    next(err);
  }
}

module.exports = authMiddleware;</code></pre>

<h4>БЛОК 2 — применение только к нужным route'ам</h4>
<pre><code>const authMiddleware = require('./middleware/auth');

app.get('/public-info', (req, res) =&gt; {
  res.json({ xabar: 'Bu ochiq route — hamma ko\\'ra oladi' });
});

app.get('/profile', authMiddleware, (req, res) =&gt; { // ❗ защищён только этот route
  res.json({ userId: req.user.id, xabar: 'Bu maxfiy ma\\'lumot' });
});

app.get('/my-orders', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM orders WHERE user_id = $1', [req.user.id]);
    res.json(result.rows);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>БЛОК 3 — проверка на основе роли (role-based)</h4>
<pre><code>function requireAdmin(req, res, next) {
  if (req.user.role !== 'admin') { // ❗ используется ПОСЛЕ authMiddleware, req.user уже есть
    const err = new Error('Bu amal uchun admin huquqi kerak');
    err.status = 403;
    return next(err);
  }
  next();
}

app.delete('/users/:id', authMiddleware, requireAdmin, async (req, res, next) =&gt; {
  // Если дошло до сюда — токен верен И пользователь администратор
  // ...
});</code></pre>

<h3>🐛 Намеренная ошибка — глобальное подключение authMiddleware</h3>
<pre><code>// ❌ ОШИБКА — влияет на все route'ы, даже на login/register!
app.use(authMiddleware); // ❌ здесь, ДО всех route'ов

app.post('/register', ...);  // теперь и это требует токен!
app.post('/login', ...);     // и это тоже! Но у пользователя ещё НЕТ токена!</code></pre>

<p><strong>Результат:</strong> если применить <code>authMiddleware</code> глобально через <code>app.use()</code>, он повлияет на <strong>все</strong> последующие route'ы, включая <code>/login</code> и <code>/register</code>. Но пользователь до входа в систему естественно ещё не имеет токена — в результате никто не сможет войти в систему, потому что для входа нужен токен, а для получения токена нужен вход: замкнутый круг (ловушка). Решение — подключать <code>authMiddleware</code> отдельно только к тем route'ам, которые действительно нужно защитить.</p>

<h3>Теперь объясним</h3>

<h4>1. Middleware на уровне route'а</h4>
<pre><code>app.get('/yol', middleware1, middleware2, handler);
// middleware выполняются до handler'а, слева направо по порядку</code></pre>
<p><code>app.get(путь, middleware, handler)</code> — middleware работает только для этого одного route'а, не влияя на другие. Несколько middleware можно записать цепочкой через запятую.</p>

<h4>2. Почему req.user хранится под таким именем?</h4>
<p><code>authMiddleware</code> проверяет токен и добавляет данные пользователя в объект <code>req</code> как <code>req.user</code>. После этого <strong>следующий</strong> middleware или handler в цепочке может использовать эти данные — потому что <code>req</code> общий для всех middleware в рамках одного запроса.</p>

<h4>3. Почему нельзя смешивать открытые и закрытые route'ы?</h4>
<p>Каждый route должен явно показывать, как он защищён (или не защищён). Глобальный <code>app.use(authMiddleware)</code> означает «всё защищено», что блокирует и route'ы вроде login/register, которые естественным образом должны быть открытыми.</p>

<h4>4. Цепочка middleware — несколько проверок</h4>
<p><code>authMiddleware, requireAdmin</code> — оба при вызове <code>next()</code> переходят к следующему. Если <code>authMiddleware</code> определит, что токен неверен, он вызовет <code>next(err)</code>, и <code>requireAdmin</code> никогда не сработает — это правильное поведение.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Вынесение auth middleware в отдельный файл предотвращает дублирование</li>
<li>✅ Middleware применяется только к нужным route'ам через <code>app.get(путь, middleware, handler)</code></li>
<li>✅ Глобальное подключение (<code>app.use</code>) authMiddleware блокирует и login/register, создавая замкнутый круг</li>
<li>✅ <code>req.user</code> — данные, добавленные middleware и передаваемые следующим handler'ам</li>
<li>✅ Цепочка middleware — каждый выполняет свою проверку и передаёт дальше через <code>next()</code></li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 9: Protected routes и цепочка middleware
// ════════════════════════════════════════════════════════════════════

// ─── middleware/auth.js ───
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) {
    const err = new Error("Token yo'q");
    err.status = 401;
    return next(err);
  }
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.userId };
    next();
  } catch {
    const err = new Error("Token noto'g'ri yoki muddati o'tgan");
    err.status = 401;
    next(err);
  }
}

function requireAdmin(req, res, next) {
  if (req.user.role !== 'admin') {
    const err = new Error("Bu amal uchun admin huquqi kerak");
    err.status = 403;
    return next(err);
  }
  next();
}

// module.exports = { authMiddleware, requireAdmin };

// ─── server.js ───
const express = require('express');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// Открытые route'ы — без защиты
// ─────────────────────────────────────────────────────────────────────

app.post('/register', async (req, res) => { /* как в уроке 8 */ });
app.post('/login', async (req, res) => { /* как в уроке 8 */ });

app.get('/public-info', (req, res) => {
  res.json({ xabar: "Bu ochiq route — hamma ko'ra oladi" });
});

// ─────────────────────────────────────────────────────────────────────
// Защищённые route'ы — middleware добавлен только здесь
// ─────────────────────────────────────────────────────────────────────

app.get('/profile', authMiddleware, (req, res) => {
  res.json({ userId: req.user.id, xabar: "Bu maxfiy ma'lumot" });
});

app.get('/my-orders', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM orders WHERE user_id = $1', [req.user.id]);
    res.json(result.rows);
  } catch (err) {
    next(err);
  }
});

app.delete('/users/:id', authMiddleware, requireAdmin, async (req, res, next) => {
  try {
    await pool.query('DELETE FROM users WHERE id = $1', [req.params.id]);
    res.status(204).send();
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// Намеренная ошибка — глобальное подключение authMiddleware (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
app.use(authMiddleware); // ❌ влияет на ВСЕ route'ы, включая /login и /register!
// Результат: для входа нужен токен, для получения токена нужен вход — замкнутый круг.
*/

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

app.listen(3000, () => {
  console.log('Сервер запущен: http://localhost:3000');
});
"""

EX = {
    3719: {
        "title": "Как применить middleware только к одному route?",
        "description": "Какой способ правильный, чтобы применить authMiddleware только к route /profile (и не к другим)?",
        "hint": "app.get(путь, middleware, handler) — middleware работает только для этого route.",
        "explanation": "В записи app.get(путь, middleware, handler) middleware относится только к этому одному route и не влияет на остальные.",
    },
    3720: {
        "title": "Откуда берётся req.user?",
        "description": "Как req.user становится доступным внутри route handler'а?",
        "hint": "req — общий объект между всеми middleware в рамках одного запроса.",
        "explanation": "authMiddleware, проверив токен, при успехе добавляет req.user = {...}. Следующие middleware/handler'ы могут использовать этот же объект req и получить доступ к req.user.",
    },
    3721: {
        "title": "Расположите поток DELETE /users/:id (только для admin) в правильном порядке",
        "description": "Упорядочите проверки, происходящие при запросе к route, защищённому и authMiddleware, и requireAdmin.",
        "hint": "Middleware выполняются в порядке, указанном в app.get(), слева направо.",
    },
    3722: {
        "title": "Почему глобальное подключение authMiddleware — проблема?",
        "description": (
            "Если authMiddleware подключить глобально через "
            "app.use(authMiddleware) ко ВСЕМ route'ам (включая /login и "
            "/register), к какой проблеме это приведёт? Объясните своими "
            "словами."
        ),
        "expected_answer": "app.use(authMiddleware) влияет на все последующие route'ы, включая /login и /register, потому что Express применяет middleware в порядке написания ко всем запросам. Но пользователь, ещё не вошедший в систему, естественно ещё не имеет никакого токена. В результате для входа требуется токен, а токен можно получить только через успешный вход — это замкнутый круг, из-за которого никто не сможет войти в систему. Решение — подключать authMiddleware отдельно, только к тем route'ам, которые действительно нужно защитить, на уровне route'а.",
        "hint": "Подумайте, есть ли у пользователя токен до входа в систему.",
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
