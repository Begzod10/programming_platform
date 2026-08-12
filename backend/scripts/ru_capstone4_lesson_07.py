"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=6 (L7)."""
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

LESSON_ID = 784

TITLE_RU = "7-Финальная полировка и деплой (завершение CAPSTONE)"

TEXT_RU = """\
<h2>Этап 7 (завершение CAPSTONE): деплой и ошибка "tsc успешен, production сломан"</h2>

<pre class="mermaid">
flowchart TB
    DEV["Dev: ts-node + tsconfig-paths - @shared/types РАБОТАЕТ"] --> BUILD["npm run build: tsc"]
    BUILD --> CHECK{"tsc использует карту paths ТОЛЬКО для проверки типов"}
    CHECK --> DIST["dist/server.js: require('@shared/types') - НЕ ИЗМЕНЁН!"]
    DIST --> PROD["node dist/server.js"]
    PROD --> CRASH["❌ Cannot find module '@shared/types' - хотя tsc завершился с 0 ошибками!"]
</pre>

<p>В курсе Node.js/Express вы уже изучили настройку CORS и подключение React к backend'у. Это — последний, финальный этап IssueForge, и здесь проявляется самое <strong>наглядное</strong> воплощение идеи, которую вы видели на протяжении всего capstone: на этот раз даже сам <code>tsc</code> считает, что "всё в порядке" — компиляция завершается с 0 ошибками — но production всё равно <strong>не работает</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — path alias: короткий, легко читаемый импорт вместо относительных путей</h4>
<pre><code>// backend/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["../shared/*"]
    }
  }
}</code></pre>
<pre><code>// ОБЫЧНЫЙ (относительный) импорт - чем глубже файл, тем сложнее читать:
// import { Issue } from '../../../shared/types';

// С PATH ALIAS - коротко и понятно:
import { Issue } from '@shared/types';</code></pre>

<h4>БЛОК 2 — запуск path alias в разработке</h4>
<pre><code># package.json
{
  "scripts": {
    "dev": "ts-node -r tsconfig-paths/register src/server.ts"
  }
}

# npm install -D tsconfig-paths
# ts-node -r tsconfig-paths/register - превращает alias @shared/* в
# реальный путь к файлу НА RUNTIME. В dev-режиме всё работает ИДЕАЛЬНО.</code></pre>

<h4>БЛОК 3 — production build: разрешение alias также во время сборки</h4>
<pre><code># npm install -D tsc-alias
# package.json
{
  "scripts": {
    "build": "tsc && tsc-alias"
  }
}

# tsc-alias - ПЕРЕПИСЫВАЕТ записи '@shared/*' в скомпилированных
# tsc файлах dist/*.js в РЕАЛЬНЫЕ относительные пути. Только после
# этого 'node dist/server.js' работает в production без ошибок.</code></pre>

<h3>🐛 Намеренная ошибка — сборка только через "tsc", без alias</h3>
<pre><code># package.json - tsc-alias НЕ ДОБАВЛЕН:
{
  "scripts": {
    "build": "tsc"
  }
}

# Локально (в dev-режиме) всё работает, потому что ts-node -r
# tsconfig-paths/register разрешает alias НА RUNTIME. Поэтому эта
# проблема ВООБЩЕ НЕ заметна при "тестировании"!

$ npm run build
# ✅ tsc: 0 ошибок! "Успешно скомпилировано."
#
# НО если открыть файл dist/server.js:
#   const types_1 = require("@shared/types");   // ❗ НЕ ИЗМЕНЁН!
#
# tsc использует карту "paths" ТОЛЬКО во время компиляции для проверки
# ТИПОВ - он НИКОГДА не переписывает пути import/require в
# сгенерированном JavaScript (это - документированное, намеренное
# поведение tsc).

$ node dist/server.js
# ❌ Error: Cannot find module '@shared/types'
#    Require stack: - /app/dist/server.js
# Production сразу же не запускается - хотя tsc дал 0 ошибок!</code></pre>

<p><strong>Результат:</strong> <code>tsc</code> использует карту <code>paths</code> из <code>tsconfig.json</code> <strong>только</strong> во время компиляции для правильной проверки типов — <strong>зная</strong>, куда указывает <code>@shared/types</code>, он на этой основе находит ошибки типов. Но в сгенерированных <code>.js</code> файлах запись <code>@shared/types</code> остаётся <strong>без изменений</strong> — потому что этот alias знаком <strong>только</strong> самому TypeScript'у во время компиляции, а механизму <code>require()</code> в Node.js он <strong>совершенно неизвестен</strong>. Когда Node запускается, реального npm-пакета или файла с именем <code>@shared/types</code> не существует — поэтому сразу падает ошибка <code>Cannot find module</code>. Это — самая <strong>обнажённая</strong> форма всех ошибок "OK при компиляции, проблема на runtime", встреченных за весь capstone: на этот раз неверный сигнал даёт даже <strong>сам</strong> <code>tsc</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему path alias (<code>@shared/*</code>) в dev-режиме (с <code>ts-node</code>) работает без проблем?</h4>
<p><code>ts-node -r tsconfig-paths/register</code> — это дополнительный инструмент, работающий на <strong>runtime</strong>. Он "перехватывает" каждый импорт <code>@shared/*</code> в момент запуска программы и <strong>сам</strong> превращает его в реальный путь к файлу. Поэтому в dev-окружении этот процесс работает <strong>полностью незаметно</strong>, без проблем.</p>

<h4>2. Для чего <code>tsc</code> использует карту <code>paths</code>, а для чего — нет?</h4>
<p><code>tsc</code> использует <code>paths</code> <strong>только</strong> во время компиляции, чтобы <strong>знать</strong>, какому реальному файлу/интерфейсу на самом деле соответствует <code>@shared/types</code> — это позволяет ему правильно проверять типы. Но задача <code>tsc</code> — <strong>превращать</strong> TypeScript в JavaScript, а не <strong>переписывать</strong> пути импорта — поэтому в сгенерированном <code>.js</code> файле оригинальная строка <code>@shared/types</code> остаётся <strong>без изменений</strong>.</p>

<h4>3. Почему эта ошибка проявляется именно в production, при запуске <code>node dist/server.js</code>?</h4>
<p>В production обычно не используются ни <code>ts-node</code>, ни <code>tsconfig-paths/register</code> — запускается только заранее скомпилированный, "чистый" JavaScript (<code>node dist/server.js</code>). Стандартный механизм <code>require()</code> в Node.js <strong>вообще ничего не знает</strong> о <code>tsconfig.json</code> и воспринимает <code>@shared/types</code> как обычное имя npm-пакета — а поскольку такого пакета нет в <code>node_modules</code>, возникает ошибка.</p>

<h4>4. Каково правильное решение этой проблемы?</h4>
<p>Добавить в процесс <code>build</code> инструмент вроде <code>tsc-alias</code> — он <strong>переписывает</strong> записи alias вроде <code>@shared/*</code> в сгенерированных <code>tsc</code> файлах <code>.js</code> в реальные <strong>относительные</strong> пути, после чего <code>node dist/server.js</code> работает в production без ошибок. Альтернативное решение — вообще не использовать alias, а всегда работать с относительными путями (менее удобно, но полностью обходит эту проблему).</p>

<h4>5. Каково <strong>финальное</strong> воплощение идеи, которую вы видели на протяжении всего capstone, в этой ошибке?</h4>
<p>На уроках 1–6 сам TypeScript работал правильно — проблема всегда возникала, когда <strong>разработчик</strong> чрезмерно доверял информации времени компиляции и пропускал runtime-проверку. Здесь же вы видите, что даже сообщение <code>tsc</code> "успешная компиляция, 0 ошибок" <strong>не гарантирует</strong>, что всё будет работать в production — потому что <code>tsc</code> использует карту <code>paths</code> только для проверки типов и не переписывает реальные пути импорта в сгенерированном JavaScript. Это завершает главный урок, изученный за весь capstone, в самой обнажённой форме: <strong>никакой сигнал "OK" времени компиляции — даже от самого TypeScript-компилятора — не гарантирует, что всё будет правильно работать в production.</strong> Подтвердить это может только настоящий, живой тест (деплой и реальный запуск).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Path alias'ы (<code>@shared/*</code>) в dev-режиме разрешаются на runtime через <code>tsconfig-paths/register</code></li>
<li>✅ <code>tsc</code> использует <code>paths</code> только для проверки типов - не переписывает пути импорта в сгенерированном JS</li>
<li>✅ Без инструмента вроде <code>tsc-alias</code> в production <code>node dist/...</code> падает с "Cannot find module"</li>
<li>✅ Сообщение tsc "0 ошибок" тоже не гарантирует успех на runtime</li>
<li>✅ Только реальный деплой и живой тест — более надёжная проверка, чем любой сигнал "OK" времени компиляции</li>
</ul>

<h3>🎉 Поздравляем!</h3>
<p>Вы построили IssueForge с нуля - с пустого репозитория на этапе 1, через общую TypeScript-схему, Express + TypeScript backend, типизированные запросы с PostgreSQL, JWT-аутентификацию, React + Redux Toolkit frontend, тесты и, наконец, до <strong>правильного, состоящего из двух частей production-деплоя</strong>. За этот capstone вы объединили знания, полученные отдельно на курсах TypeScript Asoslari, Node.js/Express Asoslari и React: Redux Toolkit, TypeScript va Testlash, в <strong>одном реальном проекте</strong> — и, что самое важное, увидели главную истину TypeScript в семи разных проявлениях: <strong>он помогает вам во время компиляции, но ничего не проверяет вместо вас во время выполнения.</strong></p>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 7 (ЗАВЕРШЕНИЕ CAPSTONE): Деплой и ошибка path alias
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/tsconfig.json - настройка path alias
// ─────────────────────────────────────────────────────────────────────

// {
//   "compilerOptions": {
//     "baseUrl": ".",
//     "paths": { "@shared/*": ["../shared/*"] }
//   }
// }

import { Issue } from '@shared/types';

// ─────────────────────────────────────────────────────────────────────
// 2) package.json - dev и ПРАВИЛЬНАЯ сборка (в комментарии - JSON, не код)
// ─────────────────────────────────────────────────────────────────────

// {
//   "scripts": {
//     "dev": "ts-node -r tsconfig-paths/register src/server.ts",
//     "build": "tsc && tsc-alias"
//   }
// }
//
// npm install -D tsconfig-paths tsc-alias

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - сборка без tsc-alias (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// {
//   "scripts": { "build": "tsc" }        // tsc-alias ОТСУТСТВУЕТ!
// }
//
// $ npm run build   -> tsc: 0 ошибок
// $ cat dist/server.js
//   const types_1 = require("@shared/types");   // не изменён!
// $ node dist/server.js
//   -> Error: Cannot find module '@shared/types'
"""

EX = {
    4524: {
        "title": "Для чего tsc использует карту paths?",
        "description": "Для чего в основном используется карта \"paths\" из tsconfig.json компилятором tsc во время компиляции?",
        "hint": "Задача tsc - превращать TypeScript в JavaScript, а не переписывать пути импорта.",
        "explanation": "tsc использует карту paths только для правильной проверки типов во время компиляции - он никогда не переписывает пути import/require в сгенерированных JavaScript-файлах.",
    },
    4525: {
        "title": "Почему path alias работает в dev, но не работает в production без tsc-alias?",
        "description": "Почему alias вроде @shared/types работает без проблем в dev-режиме с ts-node, но после сборки без tsc-alias node dist/server.js выдаёт ошибку Cannot find module?",
        "hint": "В production не используются ни ts-node, ни tsconfig-paths/register - запускается только чистый JS.",
        "explanation": "В dev-окружении ts-node -r tsconfig-paths/register превращает alias в реальный путь на runtime. В production же запускается чистый node dist/server.js - стандартный механизм require() в Node ничего не знает о tsconfig.json, поэтому не может найти @shared/types.",
    },
    4526: {
        "title": "Расположите процесс правильного деплоя IssueForge",
        "description": "Расположите правильный процесс production-сборки и деплоя, свободный от ошибки path alias.",
        "hint": "",
        "explanation": "",
    },
    4527: {
        "title": "Инструмент, переписывающий alias в реальные пути в JS, сгенерированном tsc",
        "description": "Напишите название npm-пакета, который после сборки tsc переписывает записи alias вроде @shared/* в папке dist/ в реальные относительные пути.",
        "hint": "Этот пакет добавляется в скрипт сборки после 'tsc && ...'.",
        "expected_answer": "tsc-alias",
    },
    4528: {
        "title": "Как эта ошибка завершает главную идею всего capstone?",
        "description": (
            "Как факт того, что tsc завершается с \"0 ошибок\", но в "
            "production падает с \"Cannot find module\", завершает общую "
            "идею всех ошибок, встреченных за весь IssueForge? Объясните "
            "своими словами."
        ),
        "hint": "Есть ли гарантированная связь между сообщением tsc \"0 ошибок\" и работой программы в production?",
        "expected_answer": "На уроках 1-6 сам TypeScript работал правильно - проблема всегда возникала, когда разработчик чрезмерно доверял интерфейсу или типу времени компиляции и пропускал runtime-проверку. На этом уроке показывается, что даже само сообщение tsc \"успешная компиляция, 0 ошибок\" НЕ ГАРАНТИРУЕТ, что всё будет работать в production - потому что tsc использует карту paths только для проверки типов, не переписывая реальные пути импорта в сгенерированном JavaScript. Это завершает главный урок, изученный за весь capstone, в самой обнажённой форме: никакой сигнал компиляции \"OK\" - даже от самого TypeScript-компилятора - не гарантирует, что всё правильно заработает в production; подтвердить это может только настоящий, живой тест.",
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
        TASK_TITLE_RU = "IssueForge — завершение CAPSTONE: полностью задеплоенный проект"
        TASK_DESCRIPTION_RU = (
            "Задеплойте IssueForge на реальный хостинг: backend (Express + "
            "TypeScript) и frontend (React) как отдельные Web Service. "
            "Убедитесь, что path alias'ы в production-сборке правильно "
            "разрешены через tsc-alias (или относительные пути). Обновите "
            "README.md с живыми ссылками и финальным чеклистом проверки."
        )
        TASK_REQUIREMENTS_RU = (
            "• Backend (Express + TypeScript) работает на реальном хостинге как Web Service\n"
            "• Frontend (React) задеплоен на реальном хостинге отдельно\n"
            "• В процессе сборки использован tsc-alias (или path alias вообще не используется) — node dist/server.js запускается без ошибок\n"
            "• CORS правильно настроен на production-домен frontend'а\n"
            "• Регистрация, вход, создание/просмотр issue — всё работает на живом сайте\n"
            "• README.md: живые ссылки, технологии, чеклист завершения 7/7 этапов\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория — AI-проверка анализирует весь код "
            "репозитория (backend + frontend), отдельное поле live_demo_url больше не обязательно"
        )
        TASK_TECHNOLOGIES_RU = "Render/Railway/Vercel, tsc-alias, CORS, environment variables"
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
