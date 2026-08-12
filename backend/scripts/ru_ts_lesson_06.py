"""Russian translation for TypeScript Asoslari, lesson order=5 (L6)."""
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

LESSON_ID = 676

TITLE_RU = "6-Основы Generics"

TEXT_RU = """\
<h2>Основы Generics — гибкий и безопасный код</h2>

<pre class="mermaid">
flowchart LR
    CALL1["birinchi(5)"] --> GEN["function birinchi&lt;T&gt;(arr: T[]): T"]
    CALL2["birinchi(['a','b'])"] --> GEN
    GEN -->|если T=number| OUT1["возвращает number"]
    GEN -->|если T=string| OUT2["возвращает string"]
</pre>

<p>В уроке 4 мы типизировали функции конкретными типами (например <code>number</code>). Но некоторые функции работают по одной и той же логике с <strong>любым типом</strong> &mdash; например, функция, возвращающая первый элемент массива, одинаково работает и для массива чисел, и для массива строк. <strong>Generics</strong> &mdash; именно для таких случаев: позволяют использовать тип как "переменную".</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первая generic-функция</h4>
<pre><code>function birinchiElement&lt;T&gt;(arr: T[]): T { // ❗ T — "переменная типа", может означать любой тип
  return arr[0];
}

const son = birinchiElement([10, 20, 30]);       // ❗ TypeScript определяет T как 'number'
const matn = birinchiElement(["olma", "uzum"]);  // ❗ TypeScript определяет T как 'string'

console.log(son.toFixed(1));       // ✅ son — number, toFixed работает
console.log(matn.toUpperCase());   // ✅ matn — string, toUpperCase работает</code></pre>

<h4>БЛОК 2 — generic-интерфейс</h4>
<pre><code>interface Qути&lt;T&gt; { // ❗ Qути — обобщённая структура, хранящая значение любого типа
  qiymat: T;
}

const sonQutisi: Qути&lt;number&gt; = { qiymat: 42 };
const matnQutisi: Qути&lt;string&gt; = { qiymat: "Salom" };

// const notoGri: Qути&lt;number&gt; = { qiymat: "Salom" };
// ❌ Ошибка: нельзя присвоить 'string' типу 'number'</code></pre>

<h4>БЛОК 3 — Generic constraints (ограничение через <code>extends</code>)</h4>
<pre><code>// Generic без ограничения — нельзя обращаться к свойству .length!
// function uzunlikOlish&lt;T&gt;(item: T): number {
//   return item.length; // ❌ Ошибка: не гарантировано, что у T есть .length
// }

// ✅ С constraint (ограничением) — принимаются только типы со свойством 'length'
interface UzunlikBor {
  length: number;
}

function uzunlikOlish&lt;T extends UzunlikBor&gt;(item: T): number {
  return item.length; // ✅ теперь безопасно — T точно имеет .length
}

console.log(uzunlikOlish("salom"));        // ✅ у string есть length — 5
console.log(uzunlikOlish([1, 2, 3, 4]));   // ✅ у массива есть length — 4
// console.log(uzunlikOlish(42));           // ❌ Ошибка: у number нет length</code></pre>

<h3>🐛 Намеренная ошибка — использование any вместо generic</h3>
<pre><code>// ❌ С any — связь типов полностью теряется
function birinchiElementXato(arr: any[]): any {
  return arr[0];
}

const natija = birinchiElementXato([10, 20, 30]);
console.log(natija.toUpperCase()); // ❌ Ошибка во время выполнения: 10.toUpperCase is not a function
// TypeScript здесь НИКАКОГО предупреждения не даёт, потому что 'any' разрешает всё!</code></pre>

<p><strong>Результат:</strong> при использовании <code>any[]</code> <strong>полностью теряется связь</strong> между входным и выходным типами функции &mdash; TypeScript "забывает", какого типа реальный элемент <code>arr</code>. В результате даже совершенно несоответствующий вызов вроде <code>natija.toUpperCase()</code> не перехватывается во время компиляции, а "взрывает" программу во время выполнения (<code>toUpperCase is not a function</code>). Generics же <strong>сохраняют</strong> связь между входным и выходным типами через <code>T</code>, при этом позволяя использовать функцию с любым типом.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужны Generics?</h4>
<p>Generics позволяют написать функцию или интерфейс <strong>один раз</strong> и <strong>переиспользовать</strong> её с разными типами &mdash; при этом, в отличие от <code>any</code>, связь между входным и выходным типами сохраняется.</p>

<h4>2. Что такое <code>&lt;T&gt;</code>?</h4>
<p><code>T</code> &mdash; "параметр типа" (type parameter), "переменный тип", который при вызове функции заменяется реальным типом. Имя может быть любым (обычно используются <code>T</code>, <code>U</code>, <code>K</code>, <code>V</code>), но должно быть последовательным внутри одной функции/интерфейса.</p>

<h4>3. Основное различие между Generic и any</h4>
<p><code>any</code> полностью отключает проверку типов. Generic (<code>T</code>) же даёт гибкость, <strong>сохраняя связь</strong> между входным и выходным типами: если <code>T</code> = <code>number</code>, гарантируется, что функция вернёт <code>number</code>.</p>

<h4>4. Зачем нужен generic constraint (<code>extends</code>)?</h4>
<p>Иногда <code>T</code> должен быть не любым типом, а типом, обладающим <strong>определёнными свойствами</strong> (например, свойством <code>.length</code>). Запись <code>T extends UzunlikBor</code> говорит TypeScript: "независимо от того, какой это тип T, он обязательно должен обладать свойством length".</p>

<h4>5. Как работает generic-интерфейс?</h4>
<p><code>interface Quti&lt;T&gt;</code> позволяет позже (в момент использования) указать, значение какого типа хранится внутри: <code>Quti&lt;number&gt;</code>, <code>Quti&lt;string&gt;</code> и т.д.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Generics (<code>&lt;T&gt;</code>) позволяют написать функцию/интерфейс один раз и переиспользовать с разными типами</li>
<li>✅ Generic, в отличие от <code>any</code>, сохраняет связь между входным и выходным типами</li>
<li>✅ Generic-интерфейс (<code>Quti&lt;T&gt;</code>) позволяет указать точный тип в момент использования</li>
<li>✅ <code>T extends Свойство</code> ограничивает generic-тип типами с определёнными свойствами</li>
<li>✅ Использование <code>any[]</code> теряет связь типов, что может привести к ошибкам во время выполнения</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 6: Основы Generics
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Первая generic-функция
// ─────────────────────────────────────────────────────────────────────

function birinchiElement<T>(arr: T[]): T {
  return arr[0];
}

const son = birinchiElement([10, 20, 30]);
const matn = birinchiElement(["olma", "uzum"]);

console.log(son.toFixed(1));
console.log(matn.toUpperCase());

// ─────────────────────────────────────────────────────────────────────
// 2) Generic-интерфейс
// ─────────────────────────────────────────────────────────────────────

interface Quti<T> {
  qiymat: T;
}

const sonQutisi: Quti<number> = { qiymat: 42 };
const matnQutisi: Quti<string> = { qiymat: "Salom" };

// ─────────────────────────────────────────────────────────────────────
// 3) Generic constraint - ограничение через extends
// ─────────────────────────────────────────────────────────────────────

interface UzunlikBor {
  length: number;
}

function uzunlikOlish<T extends UzunlikBor>(item: T): number {
  return item.length;
}

console.log(uzunlikOlish("salom"));
console.log(uzunlikOlish([1, 2, 3, 4]));

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - потеря связи типов через any (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
function birinchiElementXato(arr: any[]): any {
  return arr[0];
}
const natija = birinchiElementXato([10, 20, 30]);
console.log(natija.toUpperCase()); // ❌ Ошибка во время выполнения: 10.toUpperCase is not a function
*/
"""

EX = {
    3990: {
        "title": "Для чего используются generics?",
        "description": "Для чего в основном используются generics (например <T>) в TypeScript?",
        "hint": "Это безопасная гибкость, в отличие от any.",
        "explanation": "Generics позволяют написать функцию/интерфейс один раз и переиспользовать с разными типами, сохраняя связь между входным/выходным типами.",
    },
    3991: {
        "title": "Основное различие между Generic и any",
        "description": "В чём основное различие между Generic (<T>) и any?",
        "hint": "Один даёт безопасную гибкость, другой полностью отключает проверку типов.",
        "explanation": "any полностью отключает проверку типов и теряет связь между входным/выходным типами. Generic же даёт гибкость, сохраняя эту связь.",
    },
    3992: {
        "title": "Расположите процесс применения generic constraint",
        "description": "Расположите процесс создания функции uzunlikOlish<T extends UzunlikBor>.",
        "hint": "",
    },
    3993: {
        "title": "Какое ключевое слово используется для ограничения generic-типа?",
        "description": "Какое ключевое слово используется для ограничения параметра generic-типа типами с определёнными свойствами? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "extends",
    },
    3994: {
        "title": "Почему опасно использовать any[]?",
        "description": (
            "Если функция birinchiElement написана с параметром any[] "
            "вместо T[], и выполняется несоответствующий вызов вроде "
            "natija.toUpperCase(), когда (или обнаружит ли вообще) "
            "TypeScript это заметит? Почему это опасно? Объясните своими "
            "словами."
        ),
        "hint": "Сохраняется ли связь между входным и выходным типом функции при any[]?",
        "expected_answer": "Если параметр задан как any[], TypeScript не сохраняет никакой информации о реальном типе элемента массива — результат функции тоже остаётся типа any. Поэтому неверный вызов вроде natija.toUpperCase() не даёт никакой ошибки во время компиляции, но если реальный элемент (например число) не имеет метода toUpperCase, программа \"взрывается\" во время выполнения (runtime) с ошибкой вроде 'toUpperCase is not a function'. Это опасно, потому что именно цель TypeScript — обнаруживать такие ошибки заранее, во время компиляции, но при использовании any эта защита полностью пропадает.",
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
