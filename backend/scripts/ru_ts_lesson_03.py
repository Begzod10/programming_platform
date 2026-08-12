"""Russian translation for TypeScript Asoslari, lesson order=2 (L3)."""
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

LESSON_ID = 670

TITLE_RU = "3-Interface и Type Alias"

TEXT_RU = """\
<h2>Interface и Type Alias — задание формы объекта</h2>

<pre class="mermaid">
flowchart LR
    INT["interface User { ... }"] -->|задаёт "форму" объекта| OBJ["Объект пользователя"]
    TYPE["type User = { ... }"] -->|выполняет ту же задачу| OBJ
    OBJ -->|не соответствует форме| ERR["Ошибка компиляции"]
</pre>

<p>До сих пор мы типизировали простые значения. Но в реальных проектах часто приходится работать с <strong>объектами</strong> &mdash; пользователь, товар, заказ и т.д. <code>interface</code> и <code>type</code> используются для задания точной "формы" объекта (какими свойствами он должен обладать).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первый интерфейс</h4>
<pre><code>interface Foydalanuvchi {
  ism: string;
  yosh: number;
  faol: boolean;
}

const user: Foydalanuvchi = {
  ism: "Olim",
  yosh: 22,
  faol: true,
};

// const notoGriUser: Foydalanuvchi = { ism: "Vali" };
// ❌ Ошибка: не хватает свойств 'yosh' и 'faol'!</code></pre>

<h4>БЛОК 2 — необязательные (optional) и только для чтения (readonly) свойства</h4>
<pre><code>interface Mahsulot {
  readonly id: number;    // ❗ задаётся только один раз, потом изменить нельзя
  nomi: string;
  chegirma?: number;      // ❗ '?' — это свойство НЕОБЯЗАТЕЛЬНО
}

const mahsulot: Mahsulot = { id: 1, nomi: "Noutbuk" }; // верно и без скидки!

// mahsulot.id = 2; // ❌ Ошибка: 'id' readonly, изменить нельзя</code></pre>

<h4>БЛОК 3 — interface и type Alias, расширение (extends)</h4>
<pre><code>// type Alias — похож на interface, но с другим синтаксисом
type Nuqta = {
  x: number;
  y: number;
};

// Интерфейсы можно расширять
interface Shaxs {
  ism: string;
}

interface Talaba extends Shaxs { // ❗ получает все свойства Shaxs
  fakultet: string;
}

const talaba: Talaba = { ism: "Guli", fakultet: "IT" };</code></pre>

<h3>🐛 Намеренная ошибка — создание объекта, не соответствующего интерфейсу</h3>
<pre><code>interface Buyurtma {
  id: number;
  mahsulot: string;
  narx: number;
}

const buyurtma: Buyurtma = {
  id: 501,
  mahsulot: "Kitob",
  narxi: 45000, // ❌ нужно было 'narx', а не 'narxi'!
};
// TypeScript ВЫДАСТ ОШИБКУ: Object literal may only specify known properties,
// and 'narxi' does not exist in type 'Buyurtma'.</code></pre>

<p><strong>Результат:</strong> если имя свойства в объекте отличается от заданного в интерфейсе хотя бы на одну букву (<code>narxi</code> вместо <code>narx</code>), TypeScript сразу же покажет это как <strong>ошибку компиляции</strong>. Это главное преимущество интерфейсов: опечатки или забытые свойства обнаруживаются ещё во время написания кода, не доходя до production.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужен интерфейс?</h4>
<p><code>interface</code> &mdash; "контракт" (contract), задающий, какими свойствами (и их типами) должен обладать объект. Если создать объект, не соответствующий этому контракту, TypeScript выдаст ошибку во время компиляции.</p>

<h4>2. Необязательные (<code>?</code>) и readonly свойства</h4>
<p><code>свойство?: тип</code> &mdash; это свойство <strong>необязательно</strong> в объекте. <code>readonly свойство: тип</code> &mdash; значение этому свойству можно присвоить только при создании, потом изменить нельзя.</p>

<h4>3. Разница между interface и type Alias</h4>
<p>В большинстве случаев они выполняют одну и ту же задачу &mdash; задают форму объекта. Основное практическое различие: расширение <code>interface</code> через <code>extends</code> привычно и удобно, а <code>type</code> даёт больше удобства при создании более сложных комбинаций типов вроде union/intersection (увидим в уроке 5).</p>

<h4>4. extends — расширение интерфейсов</h4>
<p>Запись <code>interface B extends A</code> "наследует" в <code>B</code> все свойства <code>A</code>, добавляя к ним свои дополнительные свойства. Это удобный способ уменьшить дублирование кода.</p>

<h4>5. Как TypeScript проверяет объект?</h4>
<p>TypeScript проверяет соответствие объекта интерфейсу по <strong>именам свойств и их типам</strong>. Если не хватает нужного свойства, добавлено лишнее (отсутствующее в интерфейсе) свойство, или тип не совпадает &mdash; всё это приводит к ошибке компиляции.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>interface</code> задаёт, какой формой (свойствами и типами) должен обладать объект</li>
<li>✅ <code>свойство?: тип</code> — необязательное, <code>readonly свойство: тип</code> — задаётся только один раз</li>
<li>✅ <code>interface</code> и <code>type</code> в большинстве случаев работают одинаково, различие — в стиле расширения</li>
<li>✅ <code>extends</code> — "наследование" свойств одного интерфейса в другой</li>
<li>✅ Неправильно написанное или отсутствующее свойство объекта обнаруживается сразу во время компиляции</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 3: Interface и Type Alias
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Простой интерфейс
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi {
  ism: string;
  yosh: number;
  faol: boolean;
}

const user: Foydalanuvchi = {
  ism: "Olim",
  yosh: 22,
  faol: true,
};

// ─────────────────────────────────────────────────────────────────────
// 2) Optional и readonly свойства
// ─────────────────────────────────────────────────────────────────────

interface Mahsulot {
  readonly id: number;
  nomi: string;
  chegirma?: number;
}

const mahsulot: Mahsulot = { id: 1, nomi: "Noutbuk" };

// ─────────────────────────────────────────────────────────────────────
// 3) type Alias
// ─────────────────────────────────────────────────────────────────────

type Nuqta = {
  x: number;
  y: number;
};

const markaz: Nuqta = { x: 0, y: 0 };

// ─────────────────────────────────────────────────────────────────────
// 4) Расширение интерфейса (extends)
// ─────────────────────────────────────────────────────────────────────

interface Shaxs {
  ism: string;
}

interface Talaba extends Shaxs {
  fakultet: string;
}

const talaba: Talaba = { ism: "Guli", fakultet: "IT" };

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - неверное имя свойства (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
interface Buyurtma {
  id: number;
  mahsulot: string;
  narx: number;
}

const buyurtma: Buyurtma = {
  id: 501,
  mahsulot: "Kitob",
  narxi: 45000, // ❌ написано 'narxi' вместо 'narx'!
};
*/
"""

EX = {
    3960: {
        "title": "Для чего используется интерфейс?",
        "description": "Для чего в основном используется interface в TypeScript?",
        "hint": "Это \"контракт\" (contract) для объекта.",
        "explanation": "interface выполняет роль контракта, задающего, какими свойствами и какими типами должен обладать объект.",
    },
    3961: {
        "title": "Как обозначается необязательное свойство?",
        "description": "Какой символ используется, чтобы сделать свойство в интерфейсе необязательным (не обязательным)?",
        "hint": "Ставится после имени свойства, перед ':'.",
        "explanation": "Символ '?' в записи свойство?: тип означает, что это свойство необязательно должно присутствовать в объекте.",
    },
    3962: {
        "title": "Эффект readonly-свойства",
        "description": "Расположите следующие действия в правильном порядке: сначала присвоение значения readonly-свойству (при создании), затем попытка его изменить (ошибка).",
        "hint": "",
    },
    3963: {
        "title": "Какое ключевое слово используется для расширения интерфейсов?",
        "description": "Какое ключевое слово используется, чтобы \"унаследовать\" все свойства одного интерфейса в другой? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "extends",
    },
    3964: {
        "title": "Как обнаруживается неправильно написанное имя свойства?",
        "description": (
            "Если свойство, заданное в интерфейсе как 'narx', при создании "
            "объекта ошибочно написано как 'narxi', когда и как TypeScript "
            "это обнаружит? Почему это полезно? Объясните своими словами."
        ),
        "hint": "Интерфейс — это контракт, и TypeScript всегда его проверяет.",
        "expected_answer": "TypeScript обнаружит эту ошибку сразу, во время компиляции (или прямо во время написания кода в IDE), и покажет сообщение об ошибке, потому что имена свойств объекта должны точно соответствовать именам, заданным в интерфейсе. Это полезно, потому что опечатки или забытые свойства становятся видны и исправляются ещё во время написания кода разработчиком, не доходя до production-среды — это предотвращает ненадёжный, тихо ломающийся код.",
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
