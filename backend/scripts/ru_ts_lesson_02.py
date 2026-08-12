"""Russian translation for TypeScript Asoslari, lesson order=1 (L2)."""
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

LESSON_ID = 668

TITLE_RU = "2-Массивы, Tuple и any/unknown/never"

TEXT_RU = """\
<h2>Массивы, Tuple и специальные типы: any, unknown, never</h2>

<pre class="mermaid">
flowchart TB
    ARR["number[] — элементы одного типа"] --> USE1["Для списков"]
    TUP["[string, number] — Tuple, точная длина и порядок"] --> USE2["Для строго структурированных данных"]
    ANY["any — отключает проверку типов"] --> DANGER["Опасно, следует избегать"]
    UNK["unknown — безопасный any"] --> SAFE["Требует проверки перед использованием"]
</pre>

<p>В уроке 1 мы рассмотрели простые типы. Теперь изучим типы <strong>массив</strong> и <strong>tuple</strong> для хранения нескольких значений вместе, а также специальные типы, предназначенные для "обхода" системы типов.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — типы массивов</h4>
<pre><code>let sonlar: number[] = [1, 2, 3, 4, 5];
let ismlar: string[] = ["Olim", "Vali", "Guli"];

// Альтернативный синтаксис (generics — подробнее в уроке 6)
let baholar: Array&lt;number&gt; = [90, 85, 78];

sonlar.push(6);       // ✅ верно, добавлено number
// sonlar.push("olti"); // ❌ Ошибка: массиву 'string' ожидался 'number'</code></pre>

<h4>БЛОК 2 — Tuple: массив с точной длиной и порядком</h4>
<pre><code>// Tuple — количество элементов и их типы СТРОГО заданы
let foydalanuvchi: [string, number] = ["Olim", 22];

console.log(foydalanuvchi[0]); // "Olim" — string
console.log(foydalanuvchi[1]); // 22 — number

// foydalanuvchi[0] = 25; // ❌ Ошибка: здесь должна быть только строка
// let xato: [string, number] = [22, "Olim"]; // ❌ Ошибка: неверный порядок</code></pre>

<h4>БЛОК 3 — any, unknown и never</h4>
<pre><code>// any — ПОЛНОСТЬЮ ОТКЛЮЧАЕТ ПРОВЕРКУ ТИПОВ (по возможности не используйте!)
let narsa: any = "matn";
narsa = 42;         // ✅ никакой ошибки
narsa.notoGriMetod(); // ✅ TypeScript И ЗДЕСЬ не даст ошибку — опасно!

// unknown — похож на any, но БЕЗОПАСЕН: требует проверки перед использованием
let nomalum: unknown = "matn";
// nomalum.toUpperCase(); // ❌ Ошибка: сначала нужно проверить тип

if (typeof nomalum === "string") {
  console.log(nomalum.toUpperCase()); // ✅ теперь безопасно, тип проверен
}

// never — для функций, никогда не возвращающих значение
function xatoTashlash(xabar: string): never {
  throw new Error(xabar); // функция никогда не завершается нормально
}</code></pre>

<h3>🐛 Намеренная ошибка — использование any "для удобства"</h3>
<pre><code>function foydalanuvchiOlish(id: any) { // ❌ any поставлен "для удобства"
  return { ism: "Olim", yosh: 22 };
}

const user = foydalanuvchiOlish("noto'g'ri-id-123");
console.log(user.yash); // ❌ "yash" — опечатка (нужно "yosh"), но TypeScript НИКАКОЙ ошибки не даёт!
// Результат: undefined — программа "молча" работает неправильно</code></pre>

<p><strong>Результат:</strong> там, где указан тип <code>any</code>, TypeScript <strong>полностью</strong> отключает проверку типов — даже при явной опечатке (нужно было <code>user.yosh</code>, а не <code>user.yash</code>) не появляется никакого предупреждения. Это сводит на нет весь смысл использования TypeScript. <code>any</code> &mdash; крайняя мера "для временных, вынужденных случаев", а не "для удобства".</p>

<h3>Теперь объясним</h3>

<h4>1. Когда используется тип массива?</h4>
<p><code>number[]</code> или <code>string[]</code> используются для списков, все элементы которых <strong>одного типа</strong>, а длина заранее неизвестна (например, список пользователей, последовательность чисел).</p>

<h4>2. Когда используется Tuple?</h4>
<p>Tuple предназначен для случаев, когда количество элементов и тип каждого <strong>строго заданы</strong>, например <code>[string, number]</code> — пара "имя и возраст". В отличие от массива, у каждой позиции в tuple свой точный тип.</p>

<h4>3. Разница между any и unknown</h4>
<p><code>any</code> полностью отключает проверку типов, опасен. <code>unknown</code> &mdash; безопасная альтернатива: показывает, что значение имеет "неизвестный тип", но требует его "подтверждения" через <code>typeof</code> или другую проверку типа перед использованием.</p>

<h4>4. Зачем нужен тип never?</h4>
<p><code>never</code> означает, что функция никогда не возвращает нормальное значение: либо она всегда выбрасывает ошибку (<code>throw</code>), либо остаётся в бесконечном цикле. Это сигнализирует вызывающему коду, что "код после этой функции никогда не выполнится".</p>

<h4>5. Разница между void и never</h4>
<p><code>void</code> означает, что функция не возвращает никакого значения, но завершается нормально (например, функция, вызывающая <code>console.log</code>). <code>never</code> же означает, что функция <strong>вообще не завершается</strong> (выбрасывает ошибку или работает бесконечно).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>number[]</code>/<code>string[]</code> — для списков элементов одного типа</li>
<li>✅ Tuple (<code>[string, number]</code>) — для данных с точной длиной и порядком</li>
<li>✅ <code>any</code> полностью отключает проверку типов, по возможности следует избегать</li>
<li>✅ <code>unknown</code> — безопасная альтернатива, требует проверки типа перед использованием</li>
<li>✅ <code>never</code> — для функций, никогда не завершающихся нормально (например, выбрасывающих ошибку)</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 2: Массивы, Tuple и any/unknown/never
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Типы массивов
// ─────────────────────────────────────────────────────────────────────

let sonlar: number[] = [1, 2, 3, 4, 5];
let ismlar: string[] = ["Olim", "Vali", "Guli"];
let baholar: Array<number> = [90, 85, 78];

sonlar.push(6);

// ─────────────────────────────────────────────────────────────────────
// 2) Tuple - точная длина и порядок
// ─────────────────────────────────────────────────────────────────────

let foydalanuvchi: [string, number] = ["Olim", 22];
console.log(foydalanuvchi[0], foydalanuvchi[1]);

// ─────────────────────────────────────────────────────────────────────
// 3) unknown - безопасный any, с проверкой типа
// ─────────────────────────────────────────────────────────────────────

let nomalum: unknown = "matn";

if (typeof nomalum === "string") {
  console.log(nomalum.toUpperCase()); // безопасно - тип подтверждён
}

// ─────────────────────────────────────────────────────────────────────
// 4) never - функция, никогда не завершающаяся нормально
// ─────────────────────────────────────────────────────────────────────

function xatoTashlash(xabar: string): never {
  throw new Error(xabar);
}

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - сокрытие ошибки через any (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
function foydalanuvchiOlish(id: any) {
  return { ism: "Olim", yosh: 22 };
}
const user = foydalanuvchiOlish("noto'g'ri-id-123");
console.log(user.yash); // ❌ Опечатка, но из-за any TypeScript молчит!
*/
"""

EX = {
    3950: {
        "title": "Как записывается тип массива?",
        "description": "Какая запись типа верна для массива, состоящего только из чисел?",
        "hint": "После имени типа ставятся квадратные скобки.",
        "explanation": "Тип массива записывается добавлением [] после имени типа: number[], string[] и т.д.",
    },
    3951: {
        "title": "Основное различие между any и unknown",
        "description": "В чём основное различие между типами any и unknown?",
        "hint": "Один безопасен, другой опасен.",
        "explanation": "any полностью отключает проверку типов. unknown же безопаснее — требует проверки типа значения (например через typeof) перед его использованием.",
    },
    3952: {
        "title": "Определение свойств Tuple",
        "description": "Объявлено let user: [string, number] = [\"Olim\", 22];. Расположите следующие действия в порядке (сначала верные, затем неверное).",
        "hint": "",
    },
    3953: {
        "title": "Когда используется тип never?",
        "description": "Какой тип используется, чтобы показать, что функция никогда не завершается нормально (например, всегда выбрасывает ошибку)? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "never",
    },
    3954: {
        "title": "Почему опасно использовать тип any?",
        "description": (
            "Если параметру функции задан тип 'any', и впоследствии "
            "обращаются к неправильно написанному свойству этого значения "
            "(например user.yash, хотя нужно было user.yosh), "
            "предупредит ли об этом TypeScript? Почему это считается "
            "опасным? Объясните своими словами."
        ),
        "hint": "any отключает всю систему типов для этого значения.",
        "expected_answer": "Нет, TypeScript не даст никакого предупреждения. Для значения с типом any TypeScript полностью отключает проверку типов — обращение к любому свойству этого значения, приведение его к любому типу или вызов любого метода всегда считается TypeScript \"правильным\". Это опасно, потому что именно опечатки (например yash вместо yosh) или неверные вызовы методов не обнаруживаются во время компиляции, а проявляются только при запуске программы (или вообще не обнаруживаются, тихо давая неверный результат) — это сводит на нет саму цель использования TypeScript.",
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
