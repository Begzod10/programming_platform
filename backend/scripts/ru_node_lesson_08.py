"""Russian translation for Node.js/Express Asoslari, lesson order=9 (L8)."""
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

LESSON_ID = 624

TITLE_RU = "8-JWT-аутентификация"

TEXT_RU = """\
<h2>JWT-аутентификация — регистрация и вход</h2>

<pre class="mermaid">
flowchart LR
    R["POST /register"] -->|bcrypt.hash| DB[("таблица users")]
    L["POST /login"] -->|bcrypt.compare| DB
    L -->|если верно| JWT["jwt.sign() — создание токена"]
    JWT --> C["Токен возвращается клиенту"]
</pre>

<p>До сих пор все route'ы были «открыты для всех». Теперь научимся <strong>распознавать</strong> пользователя: безопасно хранить пароль (<code>bcrypt</code>) и выдавать токен, подтверждающий вход (<code>JWT</code>).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — регистрация: хеширование пароля</h4>
<pre><code>// Терминал:
npm install bcrypt jsonwebtoken</code></pre>

<pre><code>const bcrypt = require('bcrypt');

app.post('/register', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) {
      const err = new Error("'email' va 'parol' majburiy");
      err.status = 400;
      throw err;
    }
    const hash = await bcrypt.hash(parol, 10); // ❗ 10 — "salt rounds", уровень безопасности
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>БЛОК 2 — вход: проверка пароля и выдача JWT</h4>
<pre><code>const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET; // ❗ никогда не пишется в код, берётся из .env

app.post('/login', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const err = new Error("Email yoki parol noto'g'ri");
      err.status = 401;
      throw err;
    }
    const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>БЛОК 3 — проверка токена</h4>
<pre><code>app.get('/profile', (req, res, next) =&gt; {
  const authHeader = req.headers.authorization; // "Bearer eyJhbGci..."
  const token = authHeader &amp;&amp; authHeader.split(' ')[1];
  if (!token) {
    const err = new Error('Token yo\\'q'); err.status = 401; return next(err);
  }
  try {
    const payload = jwt.verify(token, SECRET); // при ошибке — throw
    res.json({ userId: payload.userId });
  } catch {
    const err = new Error('Token noto\\'g\\'ri yoki muddati o\\'tgan');
    err.status = 401;
    next(err);
  }
});</code></pre>

<h3>🐛 Намеренная ошибка — хранение пароля в открытом виде</h3>
<pre><code>// ❌ ОЧЕНЬ ОПАСНО — пароль не захеширован!
app.post('/register-xato', async (req, res) =&gt; {
  const { email, parol } = req.body;
  await pool.query(
    'INSERT INTO users (email, parol_hash) VALUES ($1, $2)',
    [email, parol] // ❌ сам пароль — не хеш!
  );
  res.status(201).json({ email });
});

// сравнение при логине:
// if (parol === user.parol_hash) { ... } // ❌ обычное сравнение</code></pre>

<p><strong>Результат:</strong> если базу данных увидит посторонний или произойдёт утечка данных (data breach) — реальные пароли всех пользователей окажутся в открытом виде. Это одна из самых серьёзных ошибок безопасности. <code>bcrypt.hash()</code> превращает пароль в <strong>необратимую</strong> форму; при входе же <code>bcrypt.compare()</code> безопасно сравнивает введённый пароль с хешем, никогда не через <code>===</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему пароль нельзя хранить напрямую?</h4>
<p>Если база данных каким-либо образом утечёт (взлом, ошибка конфигурации), пароли в открытом виде сразу подвергают риску и другие аккаунты пользователей (email, банк) — потому что люди часто используют один и тот же пароль повторно.</p>

<h4>2. bcrypt.hash() и bcrypt.compare()</h4>
<p><code>bcrypt.hash(parol, 10)</code> превращает пароль в односторонне (необратимо) зашифрованный текст. При входе не нужно повторно хешировать и сравнивать вручную — <code>bcrypt.compare(введённыйПароль, сохранённыйХеш)</code> делает это безопасно.</p>

<h4>3. Что такое JWT и зачем он нужен?</h4>
<p>JWT (JSON Web Token) — токен, подтверждающий личность пользователя, не хранящийся на сервере (stateless). Выдаётся при успешном входе, в последующих запросах отправляется через заголовок <code>Authorization: Bearer &lt;token&gt;</code>.</p>

<h4>4. process.env.JWT_SECRET — почему в .env?</h4>
<p>Секретный ключ, используемый для подписи JWT, никогда не пишется в коде — если он станет известен, любой сможет создать поддельный токен. Хранится через файл <code>.env</code> (подробнее в следующем уроке).</p>

<h4>5. Что делает jwt.verify()?</h4>
<p>Проверяет подпись токена и подтверждает, что срок его действия не истёк. Если токен поддельный или просрочен — выбрасывает ошибку (<code>throw</code>), поэтому его обязательно нужно вызывать внутри <code>try/catch</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <strong>Никогда</strong> не храните пароли в открытом виде — всегда через <code>bcrypt.hash()</code></li>
<li>✅ При входе используется <code>bcrypt.compare()</code>, а не <code>===</code></li>
<li>✅ <code>jwt.sign()</code> создаёт токен после успешного входа</li>
<li>✅ <code>jwt.verify()</code> проверяет токен, при ошибке выбрасывает исключение</li>
<li>✅ Секретные ключи (JWT_SECRET) никогда не пишутся в код</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 8: JWT-аутентификация
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
// const pool = require('./db');

const SECRET = process.env.JWT_SECRET;

// ─────────────────────────────────────────────────────────────────────
// 1) Регистрация — хранение пароля в хешированном виде
// ─────────────────────────────────────────────────────────────────────

app.post('/register', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) {
      const err = new Error("'email' va 'parol' majburiy");
      err.status = 400;
      throw err;
    }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 2) Вход — bcrypt.compare + выдача JWT
// ─────────────────────────────────────────────────────────────────────

app.post('/login', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const err = new Error("Email yoki parol noto'g'ri");
      err.status = 401;
      throw err;
    }
    const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Проверка токена
// ─────────────────────────────────────────────────────────────────────

app.get('/profile', (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) {
    const err = new Error("Token yo'q");
    err.status = 401;
    return next(err);
  }
  try {
    const payload = jwt.verify(token, SECRET);
    res.json({ userId: payload.userId });
  } catch {
    const err = new Error("Token noto'g'ri yoki muddati o'tgan");
    err.status = 401;
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — хранение пароля в открытом виде (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
app.post('/register-xato', async (req, res) => {
  const { email, parol } = req.body;
  await pool.query(
    'INSERT INTO users (email, parol_hash) VALUES ($1, $2)',
    [email, parol] // ❌ сам пароль — не хеш!
  );
  res.status(201).json({ email });
});
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
    3711: {
        "title": "Зачем используется bcrypt.hash()?",
        "description": "Зачем при регистрации вызывается bcrypt.hash(parol, 10)?",
        "hint": "Цель — чтобы реальный пароль не раскрылся, даже если DB утечёт.",
        "explanation": "bcrypt.hash() превращает пароль в необратимую хешированную форму. Даже в случае утечки DB реальные пароли не окажутся открытыми.",
    },
    3712: {
        "title": "Как правильно сравнивать пароль при входе?",
        "description": "Как правильно сравнить введённый пароль с сохранённым хешем в route входа?",
        "hint": "Хеш необратим, поэтому обычное === не сработает.",
        "explanation": "bcrypt.compare() повторно хеширует введённый пароль и безопасно сравнивает его с сохранённым хешем. Сравнение через обычное === невозможно, потому что хеш каждый раз создаётся со случайной 'солью'.",
    },
    3713: {
        "title": "Расположите поток входа в правильном порядке",
        "description": "Упорядочите шаги от момента входа пользователя до получения токена.",
        "hint": "Сначала находится пользователь, затем проверяется пароль, затем создаётся токен.",
    },
    3714: {
        "title": "Почему опасно хранить пароль в открытом виде?",
        "description": (
            "Если при регистрации пароль записывается в DB напрямую, без "
            "хеширования через bcrypt, почему это считается серьёзной "
            "проблемой безопасности? Как bcrypt это предотвращает? "
            "Объясните своими словами."
        ),
        "expected_answer": "Если пароль хранится в открытом виде, любой, у кого есть доступ к базе данных (хакер, ошибка конфигурации, злоупотребление изнутри), может напрямую увидеть реальные пароли всех пользователей. Поскольку многие люди повторно используют один и тот же пароль в разных сервисах (email, банк), это ставит под угрозу не только эту систему, но и другие аккаунты пользователя. bcrypt.hash() превращает пароль в одностороннюю, необратимую форму — даже если хеш будет получен из DB, восстановить из него исходный пароль напрямую невозможно.",
        "hint": "Представьте ситуацию утечки DB — какая разница в зависимости от того, каким был пароль?",
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
