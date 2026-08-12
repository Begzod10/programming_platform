"""Russian translation for TypeScript Asoslari, lesson order=3 (L4)."""
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

LESSON_ID = 672

TITLE_RU = "4-Типизация функций"

TEXT_RU = """\
<h2>Типизация функций — типы параметров и возвращаемого значения</h2>

<pre class="mermaid">
flowchart LR
    PARAM["Типы параметров"] --> FUNC["function(a: number, b: number)"]
    FUNC --> RETURN["Тип возврата: number"]
    RETURN -->|не совпадает| ERR["Ошибка компиляции"]
</pre>

<p>В уроке 3 мы типизировали объекты. Теперь изучим самую часто используемую часть проекта: типизацию <strong>функций</strong>. Каждый параметр и возвращаемое значение функции могут иметь точный тип.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — типы параметров и возврата</h4>
<pre><code>function qoshish(a: number, b: number): number {
  return a + b;
}

qoshish(2, 3);       // ✅ 5
// qoshish("2", 3);   // ❌ Ошибка: аргумент 'string' нельзя передать параметру 'number'
// qoshish(2, 3, 4);  // ❌ Ошибка: функция ожидает только 2 аргумента</code></pre>

<h4>БЛОК 2 — необязательные и стандартные (default) параметры</h4>
<pre><code>function salomlash(ism: string, unvon?: string): string { // ❗ '?' — необязательный параметр
  if (unvon) {
    return `Salom, ${unvon} ${ism}!`;
  }
  return `Salom, ${ism}!`;
}

console.log(salomlash("Olim"));            // "Salom, Olim!"
console.log(salomlash("Olim", "Janob"));   // "Salom, Janob Olim!"

// Параметр со стандартным значением — необязателен, но если значение не передано, используется стандартное
function daraja(son: number, ko_rsatkich: number = 2): number {
  return Math.pow(son, ko_rsatkich);
}

console.log(daraja(5));    // 25 (ko_rsatkich по умолчанию 2)
console.log(daraja(5, 3)); // 125</code></pre>

<h4>БЛОК 3 — тип функции (function type) и стрелочная функция</h4>
<pre><code>// Тип функции можно задать отдельно
type MatematikAmal = (a: number, b: number) => number;

const ayirish: MatematikAmal = (a, b) => a - b; // ❗ типы параметров определяются автоматически
const kopaytirish: MatematikAmal = (a, b) => a * b;

console.log(ayirish(10, 4));      // 6
console.log(kopaytirish(3, 4));   // 12

// void — функция ничего не возвращает
function logYozish(xabar: string): void {
  console.log(`[LOG]: ${xabar}`);
}</code></pre>

<h3>🐛 Намеренная ошибка — написание необязательного параметра перед обязательным</h3>
<pre><code>// ❌ function foydalanuvchiYaratish(unvon?: string, ism: string) { ... }
// TypeScript ВЫДАСТ ОШИБКУ:
// A required parameter cannot follow an optional parameter.

// ✅ Правильный вариант — необязательный параметр ВСЕГДА должен быть в конце
function foydalanuvchiYaratish(ism: string, unvon?: string) {
  return { ism, unvon };
}</code></pre>

<p><strong>Результат:</strong> если необязательный параметр (с <code>?</code>) написан <strong>перед</strong> обязательным, TypeScript выдаст ошибку компиляции. Причина в том, что при вызове функции TypeScript определяет, какой аргумент относится к какому параметру, по <strong>позиции</strong> (порядку); если первый параметр необязателен и его можно пропустить, становится неясным, на какой позиции должен идти аргумент для второго (обязательного) параметра. Поэтому правило строгое: <strong>необязательные параметры всегда пишутся после обязательных</strong>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему важно указывать тип параметра и возврата?</h4>
<p>Тип параметра определяет, какой аргумент можно передать функции, а тип возврата &mdash; каким типом будет результат функции. Оба предотвращают неправильное использование функции.</p>

<h4>2. Разница между необязательным (<code>?</code>) и параметром со стандартным значением</h4>
<p><code>параметр?: тип</code> &mdash; если параметр не передан, его значение будет <code>undefined</code>. <code>параметр: тип = значение</code> &mdash; если параметр не передан, автоматически используется указанное стандартное значение.</p>

<h4>3. Отдельное задание типа функции (function type)</h4>
<p><code>type MatematikAmal = (a: number, b: number) => number;</code> задаёт "форму" функции (какие параметры принимает, какой тип возвращает). Это особенно полезно при передаче функции как параметра в другую функцию.</p>

<h4>4. Тип void</h4>
<p><code>void</code> означает, что функция не возвращает никакого значения (например, функция, вызывающая только <code>console.log</code>). Это отличается от <code>never</code>, который мы видели в уроке 2 &mdash; функция с <code>void</code> завершается нормально, просто без значения возврата.</p>

<h4>5. Почему необязательный параметр должен быть в конце?</h4>
<p>TypeScript (и JavaScript) связывают аргументы с функцией по их <strong>позиции</strong>. Если необязательный параметр находится в середине или начале, становится неясным, на какую позицию влияет его пропуск &mdash; поэтому это строго запрещено.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Параметры и возвращаемое значение функции могут иметь точный тип: <code>function(a: number): string</code></li>
<li>✅ <code>параметр?: тип</code> — необязательный, <code>параметр: тип = значение</code> — параметр со стандартным значением</li>
<li>✅ Тип функции можно задать отдельно через <code>type</code>: <code>(a: number, b: number) => number</code></li>
<li>✅ <code>void</code> — функция не возвращает значение, но завершается нормально</li>
<li>✅ Необязательные параметры всегда должны идти <strong>после</strong> обязательных</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 4: Типизация функций
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Типы параметров и возврата
// ─────────────────────────────────────────────────────────────────────

function qoshish(a: number, b: number): number {
  return a + b;
}

console.log(qoshish(2, 3));

// ─────────────────────────────────────────────────────────────────────
// 2) Необязательные и стандартные параметры
// ─────────────────────────────────────────────────────────────────────

function salomlash(ism: string, unvon?: string): string {
  if (unvon) {
    return `Salom, ${unvon} ${ism}!`;
  }
  return `Salom, ${ism}!`;
}

function daraja(son: number, ko_rsatkich: number = 2): number {
  return Math.pow(son, ko_rsatkich);
}

console.log(salomlash("Olim"));
console.log(daraja(5));

// ─────────────────────────────────────────────────────────────────────
// 3) Тип функции (function type)
// ─────────────────────────────────────────────────────────────────────

type MatematikAmal = (a: number, b: number) => number;

const ayirish: MatematikAmal = (a, b) => a - b;
const kopaytirish: MatematikAmal = (a, b) => a * b;

console.log(ayirish(10, 4), kopaytirish(3, 4));

// ─────────────────────────────────────────────────────────────────────
// 4) void - функция, не возвращающая значение
// ─────────────────────────────────────────────────────────────────────

function logYozish(xabar: string): void {
  console.log(`[LOG]: ${xabar}`);
}

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - необязательный параметр перед обязательным (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
function foydalanuvchiYaratishXato(unvon?: string, ism: string) {
  // ❌ Ошибка: A required parameter cannot follow an optional parameter.
  return { ism, unvon };
}
*/

// ✅ Правильный вариант
function foydalanuvchiYaratish(ism: string, unvon?: string) {
  return { ism, unvon };
}
"""

EX = {
    3970: {
        "title": "Запись типа функции",
        "description": "Как записывается тип функции, принимающей два number и возвращающей number?",
        "hint": "Параметры в скобках, затем через => тип возврата.",
        "explanation": "Тип функции записывается в виде (a: number, b: number) => number: параметры в скобках, затем через '=>' указывается тип возврата.",
    },
    3971: {
        "title": "Где пишется необязательный параметр?",
        "description": "Где должен располагаться необязательный (?) параметр в объявлении функции?",
        "hint": "Аргументы связываются по позиции.",
        "explanation": "Необязательные параметры всегда должны быть написаны после обязательных, в конце списка параметров функции.",
    },
    3972: {
        "title": "Определение результата вызова daraja(5)",
        "description": "Объявлено function daraja(son: number, ko_rsatkich: number = 2). Сопоставьте следующие вызовы с их результатами.",
        "hint": "",
    },
    3973: {
        "title": "Для чего используется тип void?",
        "description": "Какой тип используется, чтобы показать, что функция не возвращает никакого значения, но завершается нормально? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "void",
    },
    3974: {
        "title": "Почему написание необязательного параметра перед обязательным даёт ошибку?",
        "description": (
            "Если написать function foydalanuvchi(unvon?: string, "
            "ism: string), почему TypeScript выдаст ошибку? Какую "
            "проблему предотвращает это правило? Объясните своими "
            "словами."
        ),
        "hint": "Аргументы связываются с функцией по имени или по позиции?",
        "expected_answer": "TypeScript и JavaScript связывают аргументы с функцией по их ПОЗИЦИИ (порядку). Если необязательный параметр стоит первым и его можно пропустить при вызове, становится невозможным определить, к какой позиции относится аргумент, переданный для следующего (обязательного) параметра — например, при вызове foydalanuvchi(\"Olim\") неясно, относится ли \"Olim\" к unvon или к ism. Поэтому TypeScript, чтобы предотвратить эту неоднозначность, разрешает писать необязательные параметры только после обязательных.",
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
