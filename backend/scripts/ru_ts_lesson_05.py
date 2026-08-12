"""Russian translation for TypeScript Asoslari, lesson order=4 (L5)."""
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

LESSON_ID = 674

TITLE_RU = "5-Union, Intersection и Type Narrowing"

TEXT_RU = """\
<h2>Union, Intersection и Type Narrowing</h2>

<pre class="mermaid">
flowchart LR
    UNION["string | number — ЛИБО одно, ЛИБО другое"] --> NARROW["проверка typeof"]
    NARROW -->|если string| STR["работают методы string"]
    NARROW -->|если number| NUM["работают методы number"]
    INTER["A & B — ОБА вместе"] --> BOTH["Все свойства обязательны"]
</pre>

<p>Иногда значение может быть <strong>одним из</strong> нескольких типов (например, ID может быть числом или текстом), а иногда нам нужны <strong>все свойства обоих типов сразу</strong>. Для этих двух случаев используются типы <strong>Union</strong> (<code>|</code>) и <strong>Intersection</strong> (<code>&amp;</code>) соответственно.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — тип Union (<code>|</code>)</h4>
<pre><code>function idChiqarish(id: string | number): string { // ❗ id может быть ЛИБО string, ЛИБО number
  return `ID: ${id}`;
}

idChiqarish(101);      // ✅ верно
idChiqarish("ABC-101"); // ✅ верно
// idChiqarish(true);   // ❌ Ошибка: 'boolean' не соответствует 'string | number'</code></pre>

<h4>БЛОК 2 — Type Narrowing: "сужение" типа</h4>
<pre><code>function narxKorsatish(narx: string | number): string {
  if (typeof narx === "number") {
    // ❗ В этом блоке TypeScript считает narx ТОЛЬКО number
    return `${narx.toFixed(2)} so'm`; // ✅ toFixed — метод только для number
  }
  // ❗ А здесь TypeScript считает narx ТОЛЬКО string
  return narx.toUpperCase(); // ✅ toUpperCase — метод только для string
}</code></pre>

<h4>БЛОК 3 — тип Intersection (<code>&amp;</code>) и Discriminated Union</h4>
<pre><code>interface Ism { ism: string; }
interface Yosh { yosh: number; }

type ShaxsMalumoti = Ism &amp; Yosh; // ❗ ОБЯЗАТЕЛЬНЫ все свойства ОБОИХ

const shaxs: ShaxsMalumoti = { ism: "Olim", yosh: 22 }; // нужны оба

// Discriminated Union — различение типов через общее "отличительное" свойство
interface MuvaffaqiyatliJavob {
  holat: "success"; // ❗ конкретное литеральное значение — "отличие"
  malumot: string;
}
interface XatoJavob {
  holat: "error";
  xabar: string;
}
type ApiJavob = MuvaffaqiyatliJavob | XatoJavob;

function javobniQayta(javob: ApiJavob) {
  if (javob.holat === "success") {
    console.log(javob.malumot); // ✅ TypeScript знает: это MuvaffaqiyatliJavob
  } else {
    console.log(javob.xabar);   // ✅ TypeScript знает: это XatoJavob
  }
}</code></pre>

<h3>🐛 Намеренная ошибка — использование union-типа без Type Narrowing</h3>
<pre><code>function narxKorsatishXato(narx: string | number): string {
  return narx.toFixed(2); // ❌ Ошибка: Property 'toFixed' does not exist on type 'string'
  // TypeScript знает, что narx может быть и string,
  // а у string нет метода toFixed() — поэтому выдаёт ошибку!
}</code></pre>

<p><strong>Результат:</strong> для значения union-типа (<code>string | number</code>) напрямую можно вызывать только методы/свойства, <strong>общие для обоих типов</strong>. <code>toFixed()</code> &mdash; метод, специфичный только для <code>number</code>, у <code>string</code> его нет. Поэтому TypeScript, <strong>ещё не зная</strong>, какого именно типа значение на самом деле, выдаёт ошибку. Решение &mdash; выполнить <strong>Type Narrowing</strong> через <code>typeof</code> (или другую проверку типа): только после этого TypeScript узнаёт, какого конкретного типа значение в данном блоке.</p>

<h3>Теперь объясним</h3>

<h4>1. Когда используется тип Union (<code>|</code>)?</h4>
<p>Используется в случаях, когда значение может быть <strong>любым из</strong> нескольких типов, например <code>string | number</code> &mdash; "либо текст, либо число".</p>

<h4>2. Когда используется тип Intersection (<code>&amp;</code>)?</h4>
<p>Используется в случаях, когда требуются <strong>все свойства сразу</strong> двух (или более) типов. <code>A &amp; B</code> &mdash; результирующий тип обязан обладать всеми свойствами и <code>A</code>, и <code>B</code>.</p>

<h4>3. Что такое Type Narrowing?</h4>
<p>Процесс "проверки" через <code>typeof</code>, <code>instanceof</code> или другое условие, каким конкретным типом на самом деле является значение union-типа, после чего в блоке кода внутри этой проверки TypeScript знает, что значение имеет <strong>только этот конкретный тип</strong>.</p>

<h4>4. Discriminated Union — различение через "отличительное" свойство</h4>
<p>Если несколько интерфейсов имеют общее по имени, но в каждом <strong>своё уникальное литеральное значение</strong> свойство (например <code>holat: "success"</code> или <code>holat: "error"</code>), TypeScript, проверяя это свойство, автоматически "узнаёт", какой это интерфейс. Это самый надёжный способ управления ответами API и состояниями в реальных проектах.</p>

<h4>5. Почему нельзя напрямую вызвать метод у union-типа без Type Narrowing?</h4>
<p>TypeScript <strong>заранее не знает</strong>, какой из типов представляет значение, поэтому считает безопасными только методы, присутствующие в обоих типах (общие). Вызов метода, специфичного только для одного типа, означает, что программа может "сломаться", если тип окажется другим, поэтому TypeScript заранее это запрещает.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>A | B</code> (Union) — значение может быть одним из типов A или B</li>
<li>✅ <code>A &amp; B</code> (Intersection) — значение обязано обладать всеми свойствами и A, и B</li>
<li>✅ Type Narrowing — "сужение" union-типа до конкретного типа через <code>typeof</code>/<code>instanceof</code></li>
<li>✅ Discriminated Union — надёжное различение типов через общее свойство с литеральным значением</li>
<li>✅ Вызов метода, не общего для union-типа, без Type Narrowing даёт ошибку компиляции</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 5: Union, Intersection и Type Narrowing
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Тип Union
// ─────────────────────────────────────────────────────────────────────

function idChiqarish(id: string | number): string {
  return `ID: ${id}`;
}

console.log(idChiqarish(101), idChiqarish("ABC-101"));

// ─────────────────────────────────────────────────────────────────────
// 2) Type Narrowing - сужение типа через typeof
// ─────────────────────────────────────────────────────────────────────

function narxKorsatish(narx: string | number): string {
  if (typeof narx === "number") {
    return `${narx.toFixed(2)} so'm`;
  }
  return narx.toUpperCase();
}

// ─────────────────────────────────────────────────────────────────────
// 3) Тип Intersection
// ─────────────────────────────────────────────────────────────────────

interface Ism {
  ism: string;
}
interface Yosh {
  yosh: number;
}

type ShaxsMalumoti = Ism & Yosh;

const shaxs: ShaxsMalumoti = { ism: "Olim", yosh: 22 };

// ─────────────────────────────────────────────────────────────────────
// 4) Discriminated Union
// ─────────────────────────────────────────────────────────────────────

interface MuvaffaqiyatliJavob {
  holat: "success";
  malumot: string;
}
interface XatoJavob {
  holat: "error";
  xabar: string;
}
type ApiJavob = MuvaffaqiyatliJavob | XatoJavob;

function javobniQayta(javob: ApiJavob) {
  if (javob.holat === "success") {
    console.log(javob.malumot);
  } else {
    console.log(javob.xabar);
  }
}

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - union-тип без Type Narrowing (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
function narxKorsatishXato(narx: string | number): string {
  return narx.toFixed(2); // ❌ Property 'toFixed' does not exist on type 'string'
}
*/
"""

EX = {
    3980: {
        "title": "Как задаётся тип Union?",
        "description": "Как записывается тип для значения, которое может быть либо string, либо number?",
        "hint": "Символ, означающий \"или\".",
        "explanation": "Тип Union записывается символом '|': string | number — значение может быть одним из двух.",
    },
    3981: {
        "title": "Что означает тип Intersection?",
        "description": "Что говорит о значении тип A & B (Intersection)?",
        "hint": "Символ, означающий \"и\".",
        "explanation": "Intersection (A & B) требует, чтобы значение обладало всеми свойствами и A, и B одновременно.",
    },
    3982: {
        "title": "Расположите процесс Type Narrowing",
        "description": "Расположите процесс безопасного вызова метода, специфичного для конкретного типа, у значения union-типа.",
        "hint": "",
    },
    3983: {
        "title": "Какое свойство используется в Discriminated Union?",
        "description": "Как называется способ различения нескольких интерфейсов через общее, но в каждом своё уникальное литеральное свойство? (например: 'discriminated union')",
        "hint": "",
        "expected_answer": "discriminated union",
    },
    3984: {
        "title": "Почему нельзя вызвать метод у union-типа без Type Narrowing?",
        "description": (
            "Если напрямую вызвать narx.toFixed(2) у параметра "
            "narx: string | number, почему TypeScript выдаст ошибку, "
            "хотя toFixed() является верным методом для number? "
            "Объясните своими словами."
        ),
        "hint": "TypeScript ещё не знает конкретный тип значения — доверяет только общему для обоих.",
        "expected_answer": "TypeScript знает, что значение narx может быть и string, а у типа string метода toFixed() не существует. Для значения union-типа TypeScript считает безопасными только методы, общие для обоих (всех) типов, потому что ещё не знает, каким конкретным типом является значение. Если не выполнить Type Narrowing (например проверку typeof narx === 'number'), TypeScript считает этот вызов небезопасным и выдаёт ошибку компиляции — потому что если narx на самом деле окажется string, программа столкнётся с ошибкой во время выполнения.",
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
