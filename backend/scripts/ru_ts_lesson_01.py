"""Russian translation for TypeScript Asoslari, lesson order=0 (L1)."""
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

LESSON_ID = 666

TITLE_RU = "1-Введение в TypeScript и основные типы"

TEXT_RU = """\
<h2>Введение в TypeScript — первый типизированный код за 5 минут</h2>

<pre class="mermaid">
flowchart LR
    TS["TypeScript код (.ts)"] -->|tsc компиляция| JS["Чистый JavaScript (.js)"]
    JS --> BROWSER["Браузер / Node.js"]
    ERR["Ошибка типа"] -->|обнаруживается при компиляции| TS
</pre>

<p>До сих пор в JavaScript переменной можно было присвоить значение любого типа — если написать <code>let yosh = 25</code>, а потом <code>yosh = "yigirma besh"</code>, никакой ошибки не возникнет, проблема проявится только когда программа запустится (runtime). <strong>TypeScript</strong> — язык от Microsoft, добавляющий JavaScript <strong>статическую типизацию</strong> (static typing): ошибки обнаруживаются ещё во время написания кода, до его запуска.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка TypeScript и первый файл</h4>
<pre><code>// Терминал:
npm install -g typescript
tsc --version</code></pre>

<pre><code>// birinchi.ts
let ism: string = "Olim";
let yosh: number = 22;
let faol: boolean = true;

console.log(`${ism} - ${yosh} yoshda, faolmi: ${faol}`);</code></pre>

<pre><code>// Терминал — превращение .ts файла в .js:
tsc birinchi.ts
// В результате создаётся файл birinchi.js, его можно запустить через node:
node birinchi.js</code></pre>

<h4>БЛОК 2 — обнаружение ошибки типа при компиляции</h4>
<pre><code>let yosh: number = 25;
yosh = "yigirma besh"; // ❌ TypeScript ВЫДАСТ ОШИБКУ: сюда нельзя присвоить string!

// Сообщение об ошибке:
// Type 'string' is not assignable to type 'number'.</code></pre>

<p>Именно это &mdash; главная сила TypeScript: эта ошибка видна <strong>ещё до запуска кода</strong>, сразу в IDE или при запуске <code>tsc</code>. В обычном же JavaScript эта ошибка "взрывается" только когда программа доходит до этой строки во время выполнения.</p>

<h4>БЛОК 3 — Type Inference (автоматическое определение типа)</h4>
<pre><code>// Тип не всегда обязательно писать явно — TypeScript сам его "выводит"
let shahar = "Toshkent"; // TypeScript автоматически считает это 'string'
let masofa = 150.5;      // автоматически 'number'

shahar = 42; // ❌ Ошибка: нельзя присвоить тип 'number' типу 'string'
             // TypeScript помнит это, даже если мы не писали ':string'!</code></pre>

<h3>🐛 Намеренная ошибка — использование синтаксиса TypeScript с расширением .js</h3>
<pre><code>// fayl.js (расширение .js, НЕ .ts!)
let yosh: number = 25; // ❌ Здесь ':number' — это синтаксис TypeScript!</code></pre>

<p><strong>Результат:</strong> если расширение файла остаётся <code>.js</code> (не изменено на <code>.ts</code>), компилятор <code>tsc</code> вообще не проверяет этот файл — потому что он ищет только файлы <code>.ts</code>. Node.js или браузер же не понимают специфичный для TypeScript синтаксис вроде <code>: number</code> и выдают <strong>syntax error</strong>. Это одна из самых частых ошибок новичков: синтаксис TypeScript работает только в файлах <code>.ts</code> (или <code>.tsx</code> для React).</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое TypeScript и как он связан с JavaScript?</h4>
<p>TypeScript &mdash; <strong>надмножество</strong> (superset) JavaScript: любой правильный JavaScript-код одновременно является правильным TypeScript-кодом. TypeScript просто добавляет к нему возможность указывать <strong>аннотации типов</strong> (type annotations). Браузер или Node.js не понимают TypeScript напрямую &mdash; поэтому компилятор <code>tsc</code> превращает его в чистый JavaScript.</p>

<h4>2. Основные примитивные типы</h4>
<pre><code>let ism: string = "Olim";       // текст
let yosh: number = 22;          // ОДИН тип для целых и дробных чисел
let faol: boolean = true;       // true или false</code></pre>
<p>В отличие от некоторых языков, в TypeScript нет отдельных числовых типов вроде <code>int</code>, <code>float</code> &mdash; для всех чисел используется один тип <code>number</code>.</p>

<h4>3. Почему важно знать ошибку типа во время компиляции?</h4>
<p>При работе в большой команде или над крупным проектом кто-то может передать функции значение неверного типа. В обычном JavaScript эта ошибка станет известна только в production, когда пользователь вызовет эту функцию. TypeScript же покажет это <strong>прямо во время написания кода</strong>.</p>

<h4>4. Type Inference — не всегда обязательно писать тип</h4>
<p>TypeScript может автоматически определять тип по значению (<em>type inference</em>). Поэтому в простых случаях необязательно писать <code>: string</code>, <code>: number</code> &mdash; но в параметрах функций рекомендуется указывать это явно (увидим в следующем уроке).</p>

<h4>5. Разница между файлами .ts и .js</h4>
<p>Компилятор <code>tsc</code> проверяет как TypeScript только файлы с расширением <code>.ts</code>. Если в файле <code>.js</code> написан синтаксис TypeScript (например, <code>: number</code>), ни <code>tsc</code>, ни браузер не поймут это правильно.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ TypeScript &mdash; язык, добавляющий JavaScript статическую типизацию, превращается в чистый JS через <code>tsc</code></li>
<li>✅ <code>string</code>, <code>number</code>, <code>boolean</code> &mdash; три самых основных примитивных типа</li>
<li>✅ Ошибка типа обнаруживается во время компиляции, без запуска кода</li>
<li>✅ Type Inference &mdash; TypeScript во многих случаях сам "выводит" тип</li>
<li>✅ Синтаксис TypeScript работает только в файлах <code>.ts</code>/<code>.tsx</code>, не в <code>.js</code></li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 1: Введение в TypeScript и основные типы
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Основные примитивные типы
// ─────────────────────────────────────────────────────────────────────

let ism: string = "Olim";
let yosh: number = 22;
let faol: boolean = true;

console.log(`${ism} - ${yosh} yoshda, faolmi: ${faol}`);

// ─────────────────────────────────────────────────────────────────────
// 2) Type Inference - TypeScript сам определяет тип, даже если не написан
// ─────────────────────────────────────────────────────────────────────

let shahar = "Toshkent"; // автоматически: string
let masofa = 150.5;      // автоматически: number

// ─────────────────────────────────────────────────────────────────────
// 3) Ошибка типа - обнаруживается во время компиляции
// ─────────────────────────────────────────────────────────────────────

// yosh = "yigirma besh"; // ❌ Ошибка: Type 'string' is not assignable to type 'number'
// shahar = 42;            // ❌ Ошибка: Type 'number' is not assignable to type 'string'

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - синтаксис TypeScript в файле .js (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
// Если этот код находится в fayl.js (НЕ fayl.ts):
let narx: number = 100; // ❌ Node.js/браузер не понимает ": number" - syntax error!
*/

// Терминал:
//   npm install -g typescript
//   tsc birinchi.ts   // создаётся birinchi.js
//   node birinchi.js
"""

EX = {
    3940: {
        "title": "Что такое TypeScript?",
        "description": "Чем на самом деле является TypeScript?",
        "hint": "Любой правильный код JavaScript одновременно является правильным кодом TypeScript.",
        "explanation": "TypeScript — надмножество (superset) JavaScript, добавляющее статическую типизацию (static typing). Компилятор tsc превращает его в чистый JavaScript.",
    },
    3941: {
        "title": "Когда обнаруживается ошибка типа?",
        "description": "Если в TypeScript присвоено значение неверного типа, когда обычно обнаруживается эта ошибка?",
        "hint": "Это главное преимущество TypeScript, отличие от обычного JavaScript.",
        "explanation": "Главная сила TypeScript в том, что ошибки типов обнаруживаются во время компиляции (или прямо во время написания кода в IDE) — запускать код не требуется.",
    },
    3942: {
        "title": "Порядок запуска проекта",
        "description": "Расположите шаги написания и запуска нового файла TypeScript в правильном порядке.",
        "hint": "Сначала устанавливается библиотека, затем пишется файл, затем компилируется, затем запускается.",
    },
    3943: {
        "title": "Сколько основных числовых типов в TypeScript?",
        "description": "Сколько общих числовых типов используется в JavaScript/TypeScript вместо отдельных типов вроде int, float? (ответьте числом)",
        "hint": "Для целых и дробных чисел есть один общий тип.",
        "expected_answer": "1",
    },
    3944: {
        "title": "Что произойдёт при использовании синтаксиса TypeScript в файле .js?",
        "description": (
            "Если разработчик напишет синтаксис TypeScript вроде "
            "'let narx: number = 100;' внутри fayl.js (не fayl.ts), что "
            "произойдёт и почему? Объясните своими словами."
        ),
        "hint": "Какие файлы по расширению tsc считает \"TypeScript\"?",
        "expected_answer": "Компилятор tsc проверяет как TypeScript только файлы с расширением .ts, поэтому файл .js он вообще не рассматривает. Node.js или браузер же не понимают специфичный для TypeScript синтаксис вроде ': number', потому что этот синтаксис не является частью стандартного JavaScript. В результате при запуске файла возникает syntax error, потому что движок JavaScript не может понять эту запись.",
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
