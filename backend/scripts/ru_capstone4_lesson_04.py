"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=3 (L4)."""
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

LESSON_ID = 778

TITLE_RU = "4-Аутентификация (JWT + типизированный payload)"

TEXT_RU = """\
<h2>Этап 4: Аутентификация — JWT и типизированный payload</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /login - выдаётся JWT с {userId, role}"] --> TOKEN["Клиент сохраняет токен"]
    TOKEN --> PROTECTED["Защищённый route: заголовок Authorization"]
    PROTECTED --> VERIFY["jwt.verify() - реальный тип: JwtPayload | string"]
    VERIFY -->|"cast 'as {userId, role}' без проверки"| TRUST["TypeScript: 'OK, это объект'"]
    TRUST --> BUG["Токен другого назначения переиспользован - userId/role undefined"]
</pre>

<p>В курсе Node.js/Express вы уже изучили JWT-аутентификацию, хеширование пароля через bcrypt и цепочку middleware для защищённых маршрутов. На этом уроке вы типизируете всё это с помощью TypeScript. На этот раз граница TypeScript проявляется в особенно тонком месте: сама библиотека <code>jsonwebtoken</code> <strong>официально объявляет</strong> тип <code>JwtPayload | string</code> для <code>jwt.verify()</code> — но многие разработчики игнорируют это и напрямую приводят результат к своему интерфейсу.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — login: выдача JWT с типизированным payload</h4>
<pre><code># Terminal:
npm install jsonwebtoken bcrypt
npm install -D @types/jsonwebtoken @types/bcrypt</code></pre>
<pre><code>// backend/src/auth.ts
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const JWT_SECRET = process.env.JWT_SECRET as string;

interface AuthTokenPayload {
  userId: number;
  role: 'member' | 'admin';
}

export function issueToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });
}

app.post('/login', async (req: Request, res: Response) => {
  const user = await findUserByEmail(req.body.email);
  const ok = user && await bcrypt.compare(req.body.password, user.passwordHash);
  if (!ok) return res.status(401).json({ error: 'Неверный email или пароль' });

  const token = issueToken({ userId: user!.id, role: user!.role });
  res.json({ token });
});</code></pre>

<h4>БЛОК 2 — защищённый route: ПРАВИЛЬНАЯ проверка результата jwt.verify()</h4>
<pre><code>// САМА библиотека jsonwebtoken объявляет jwt.verify() именно так:
// function verify(token: string, secret: string): JwtPayload | string;
//                                                   ❗ может быть И объектом, И строкой!

function verifyAuthToken(token: string): AuthTokenPayload | null {
  const decoded = jwt.verify(token, JWT_SECRET);

  if (typeof decoded === 'string' || !('userId' in decoded) || !('role' in decoded)) {
    return null;   // ❗ проверка на RUNTIME - подтверждается, что форма ДЕЙСТВИТЕЛЬНО совпадает
  }
  return decoded as AuthTokenPayload;   // Теперь cast безопасен - после проверки
}</code></pre>

<h4>БЛОК 3 — middleware: типизация req.user</h4>
<pre><code>// backend/src/types/express.d.ts - расширение Express Request
declare global {
  namespace Express {
    interface Request {
      user?: AuthTokenPayload;
    }
  }
}

function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const payload = token ? verifyAuthToken(token) : null;
  if (!payload) return res.status(401).json({ error: 'Не авторизован' });

  req.user = payload;
  next();
}</code></pre>

<h3>🐛 Намеренная ошибка — приведение результата jwt.verify() без проверки</h3>
<pre><code>// Решив, что "это всегда будет AuthTokenPayload", пропускается шаг
// проверки (typeof/'userId' in из БЛОКА 2):
function verifyAuthToken(token: string): AuthTokenPayload {
  const decoded = jwt.verify(token, JWT_SECRET) as AuthTokenPayload;   // ❌ cast без проверки!
  return decoded;
}

// В проекте та же библиотека jsonwebtoken используется и для ДРУГОЙ цели
// (например сброс пароля), но в СОВЕРШЕННО ДРУГОЙ форме:
// const resetToken = jwt.sign(user.email, JWT_SECRET);   // ❗ обычная СТРОКА, не объект!

// Если разработчик по ошибке вызовет verifyAuthToken() и для reset-токена:
// const payload = verifyAuthToken(resetToken);
// payload.userId   -> undefined (потому что decoded на самом деле была СТРОКОЙ!)
// payload.role     -> undefined
//
// ❌ tsc ЭТОГО НЕ ОБНАРУЖИТ - потому что "as AuthTokenPayload" говорит
//    TypeScript "поверь мне", полностью игнорируя реальный тип
//    JwtPayload | string у jwt.verify().</code></pre>

<p><strong>Результат:</strong> библиотека <code>jsonwebtoken</code> <strong>намеренно</strong> объявляет union-тип <code>JwtPayload | string</code> для <code>jwt.verify()</code> — потому что подпись JWT может работать <strong>с любым</strong> значением (и с объектом, И с обычной строкой). Приведение <code>as AuthTokenPayload</code> <strong>без проверки</strong> полностью обходит этот union-тип. Если эта же <strong>общая</strong> функция проверки в проекте переиспользуется для токена <strong>другой формы</strong> (например сброс пароля — <code>jwt.sign(email, SECRET)</code>, обычная строка), <code>decoded</code> на runtime <strong>действительно</strong> окажется строкой. TypeScript этого <strong>никогда</strong> не поймает, потому что cast означает "поверь мне", а не проверку.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему объявленный тип <code>jwt.verify()</code> — это <code>JwtPayload | string</code>?</h4>
<p>JWT — это просто подписанные данные. В <code>jwt.sign()</code> можно передать любое значение (объект <strong>или</strong> обычную строку), поэтому <code>jwt.verify()</code> теоретически тоже может вернуть <strong>любое из двух</strong>. Библиотека объявляет это <strong>честно</strong> — проблема в том, что разработчики часто игнорируют этот union-тип и сразу приводят результат к нужному типу.</p>

<h4>2. Зачем нужна проверка <code>typeof decoded === 'string'</code> в БЛОКЕ 2?</h4>
<p>Это — <strong>runtime narrowing</strong> (сужение типа): код проверяет <strong>после запуска</strong>, что <code>decoded</code> действительно является объектом и содержит нужные поля (<code>userId</code>, <code>role</code>). Только после этого приведение <code>as AuthTokenPayload</code> становится <strong>безопасным</strong> — потому что оно теперь опирается на реальную проверку.</p>

<h4>3. Почему опасно переиспользовать одну и ту же функцию <code>verifyAuthToken()</code> для токена другого типа?</h4>
<p>TypeScript доверяет <strong>объявленному</strong> типу возврата функции (<code>AuthTokenPayload</code>), но если <strong>внутри</strong> функции нет реальной проверки, функция на самом деле принимает <strong>любой</strong> токен и "уверенно" возвращает неверный тип — а вызывающая сторона об этом даже не узнает.</p>

<h4>4. Для чего используется <code>declare global { namespace Express {...} } }</code>?</h4>
<p>В собственном интерфейсе <code>Request</code> у Express по умолчанию нет поля <code>user</code>. С помощью этой записи можно добавить специфичное для проекта поле <code>user</code> к типу <code>Request</code> <strong>во всём проекте</strong> — тогда к <code>req.user</code> можно безопасно обращаться в каждом обработчике маршрута.</p>

<h4>5. Почему эта ошибка особенно опасна — не только функционально, но и с точки зрения безопасности?</h4>
<p>Если <code>userId</code>/<code>role</code> неожиданно окажутся <code>undefined</code>, и проверка авторизации (например <code>if (req.user.role === 'admin')</code>) этого не учитывает, результат может быть двояким: либо пользователю <strong>необоснованно откажут</strong> в доступе (функциональная ошибка), либо — если логика проверки написана наоборот — <strong>неожиданно предоставят доступ</strong> (уязвимость безопасности). Поэтому пропуск runtime-проверки в коде аутентификации особенно опасен.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Реальный тип <code>jwt.verify()</code> — <code>JwtPayload | string</code>, сама библиотека это открыто объявляет</li>
<li>✅ Runtime narrowing через <code>typeof</code> и <code>'field' in obj</code> перед cast'ом — условие безопасного приведения</li>
<li>✅ Переиспользование общей функции проверки для токена другой формы может привести к несоответствию типов</li>
<li>✅ Расширение Express <code>Request</code> через <code>declare global</code> — способ безопасно типизировать <code>req.user</code> во всём проекте</li>
<li>✅ Приведение без проверки в коде аутентификации — риск не только функциональной ошибки, но и уязвимости безопасности</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 4: Аутентификация - JWT и типизированный payload
// ════════════════════════════════════════════════════════════════════

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { Request, Response, NextFunction } from 'express';

const JWT_SECRET = process.env.JWT_SECRET as string;

interface AuthTokenPayload {
  userId: number;
  role: 'member' | 'admin';
}

// ─────────────────────────────────────────────────────────────────────
// 1) Выдача токена
// ─────────────────────────────────────────────────────────────────────

export function issueToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });
}

// ─────────────────────────────────────────────────────────────────────
// 2) Проверка токена - БЕЗОПАСНО, с runtime narrowing
// ─────────────────────────────────────────────────────────────────────

function verifyAuthToken(token: string): AuthTokenPayload | null {
  const decoded = jwt.verify(token, JWT_SECRET);

  if (typeof decoded === 'string' || !('userId' in decoded) || !('role' in decoded)) {
    return null;
  }
  return decoded as AuthTokenPayload;
}

// ─────────────────────────────────────────────────────────────────────
// 3) Расширение Express Request + middleware
// ─────────────────────────────────────────────────────────────────────

declare global {
  namespace Express {
    interface Request {
      user?: AuthTokenPayload;
    }
  }
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const payload = token ? verifyAuthToken(token) : null;
  if (!payload) return res.status(401).json({ error: 'Не авторизован' });

  req.user = payload;
  next();
}

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - cast без проверки (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// function verifyAuthToken(token: string): AuthTokenPayload {
//   const decoded = jwt.verify(token, JWT_SECRET) as AuthTokenPayload;   // без проверки!
//   return decoded;
// }
// Переиспользование для токена другого назначения (например сброс пароля)
// в виде строки: payload.userId -> undefined, payload.role -> undefined
"""

EX = {
    4494: {
        "title": "Каков реальный объявленный тип возврата jwt.verify()?",
        "description": "Какой тип официально объявлен для функции jwt.verify(token, secret) в библиотеке jsonwebtoken?",
        "hint": "JWT payload теоретически может быть и обычной строкой, объект не обязателен.",
        "explanation": "Библиотека jsonwebtoken объявляет union-тип JwtPayload | string для jwt.verify(), потому что в jwt.sign() можно передать объект или обычную строку, и verify соответственно может вернуть оба варианта.",
    },
    4495: {
        "title": "Зачем нужна проверка typeof decoded === 'string'?",
        "description": "Зачем в функции verifyAuthToken() перед cast'ом пишутся проверки typeof decoded === 'string' и 'userId' in decoded?",
        "hint": "Это runtime narrowing - то есть сужение типа после запуска программы.",
        "explanation": "Эти проверки подтверждают на runtime, что значение decoded действительно является объектом и содержит нужные поля - только после этого последующий cast считается безопасным, так как он основан на реальной проверке.",
    },
    4496: {
        "title": "Расположите, что происходит при неверном переиспользовании общей функции проверки",
        "description": "Расположите процесс, происходящий при переиспользовании verifyAuthToken() (написанной с cast без проверки) для токена сброса пароля.",
        "hint": "",
        "explanation": "",
    },
    4497: {
        "title": "Ключевое слово для расширения Express Request",
        "description": "Какая конструкция TypeScript используется для добавления поля вроде req.user к типу Request Express во всём проекте? (например: declare xxx)",
        "hint": "Начинается с декларации глобального namespace.",
        "expected_answer": "declare global",
    },
    4498: {
        "title": "Почему cast без проверки в коде аутентификации особенно опасен?",
        "description": (
            "Если в функции verifyAuthToken() результат jwt.verify() "
            "приводится напрямую к AuthTokenPayload без runtime-проверки, "
            "почему это особенно опасно не только функционально, но и с "
            "точки зрения безопасности? Объясните своими словами."
        ),
        "hint": "Как проверка авторизации может неверно истолковать undefined значение req.user.role?",
        "expected_answer": "Если значение decoded не соответствует ожидаемой форме объекта (например, по ошибке переиспользован string-токен другого назначения), из-за cast без проверки поля вроде userId и role окажутся undefined, но TypeScript никогда не обнаружит это во время компиляции. Если проверка авторизации (например if (req.user.role === 'admin')) не учитывает этот случай, результат может быть двояким: либо пользователю необоснованно откажут в доступе (функциональная ошибка), либо - если логика проверки написана наоборот (например ошибка вместо 'отказать, если role НЕ admin') - неожиданное значение undefined может открыть путь к непредусмотренному разрешению доступа, что является серьёзной уязвимостью безопасности.",
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
        TASK_TITLE_RU = "IssueForge — Аутентификация (JWT + типизированный payload)"
        TASK_DESCRIPTION_RU = (
            "Напишите эндпоинты для регистрации пользователя (хеширование "
            "пароля через bcrypt) и входа (выдача JWT). Создайте middleware "
            "для защищённых маршрутов — НЕ приводите результат jwt.verify() "
            "без runtime-проверки, сначала выполните narrowing через "
            "typeof/'field' in."
        )
        TASK_REQUIREMENTS_RU = (
            "• POST /register — пароль хешируется через bcrypt\n"
            "• POST /login — при успехе возвращает JWT на основе AuthTokenPayload\n"
            "• Middleware requireAuth — проверяет результат jwt.verify() на runtime, только потом приводит тип\n"
            "• Express Request расширен через declare global, req.user типизирован\n"
            "• Незащищённый запрос (с неверным/отсутствующим токеном) возвращает 401\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Node.js, Express, TypeScript, jsonwebtoken, bcrypt"
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
