"""Russian translation for TypeScript Asoslari, lesson order=8 (L9)."""
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

LESSON_ID = 682

TITLE_RU = "9-Utility Types"

TEXT_RU = """\
<h2>Utility Types — готовые трансформаторы типов</h2>

<pre class="mermaid">
flowchart LR
    IFACE["interface Foydalanuvchi"] --> PARTIAL["Partial&lt;Foydalanuvchi&gt; — все поля опциональны"]
    IFACE --> PICK["Pick&lt;Foydalanuvchi, 'ism'&gt; — только выбранные поля"]
    IFACE --> OMIT["Omit&lt;Foydalanuvchi, 'parol'&gt; — некоторые поля исключены"]
    IFACE --> READONLY["Readonly&lt;Foydalanuvchi&gt; — все поля неизменяемы"]
</pre>

<p>Часто нам нужна "немного изменённая" версия существующего <code>interface</code> &mdash; например, для формы обновления все поля должны быть опциональными, или нужны данные пользователя без пароля. Вместо того чтобы каждый раз писать новый интерфейс, TypeScript предоставляет готовые "трансформаторы типов", называемые <strong>utility types</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — Partial и Readonly</h4>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

// Partial<T> - делает все поля опциональными
function foydalanuvchiniYangilash(id: number, ozgarishlar: Partial<Foydalanuvchi>): void {
  console.log(`Foydalanuvchi ${id} yangilanmoqda:`, ozgarishlar);
}

foydalanuvchiniYangilash(1, { ism: "Yangi Ism" }); // ✅ достаточно всего 1 поля

// Readonly<T> - делает все поля неизменяемыми (readonly)
const sobitFoydalanuvchi: Readonly<Foydalanuvchi> = { id: 1, ism: "Olim", email: "olim@mail.uz" };
// sobitFoydalanuvchi.ism = "Boshqa"; // ❌ Ошибка: readonly, изменить нельзя</code></pre>

<h4>БЛОК 2 — Pick и Omit</h4>
<pre><code>// Pick<T, Keys> - берёт ТОЛЬКО указанные поля
type FoydalanuvchiIsmi = Pick<Foydalanuvchi, "id" | "ism">;
// результат: { id: number; ism: string; } — email ОТСУТСТВУЕТ

const qisqaMalumot: FoydalanuvchiIsmi = { id: 1, ism: "Olim" };

// Omit<T, Keys> - ИСКЛЮЧАЕТ указанные поля, берёт остальные
type FoydalanuvchiParolsiz = Omit<Foydalanuvchi, "email">;
// результат: { id: number; ism: string; } — email исключён

const xavfsizMalumot: FoydalanuvchiParolsiz = { id: 1, ism: "Olim" };</code></pre>

<h4>БЛОК 3 — Record</h4>
<pre><code>// Record<Keys, ValueType> - тип объекта, где все ключи Keys, значения ValueType
type ViloyatAholisi = Record<string, number>; // ❗ ключ - string, значение - number

const aholi: ViloyatAholisi = {
  Toshkent: 2900000,
  Samarqand: 550000,
};

// Ключи тоже можно ограничить (через literal type)
type RangKodlari = Record<"qizil" | "yashil" | "kok", string>;
const ranglar: RangKodlari = {
  qizil: "#FF0000",
  yashil: "#00FF00",
  kok: "#0000FF",
};</code></pre>

<h3>🐛 Намеренная ошибка — указание несуществующего имени поля в Pick</h3>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

type Xato = Pick<Foydalanuvchi, "id" | "familiya">;
// ❌ Ошибка: Property 'familiya' does not exist on type 'Foydalanuvchi'.</code></pre>

<p><strong>Результат:</strong> во втором generic-параметре <code>Pick</code> (и <code>Omit</code>) принимаются <strong>только</strong> имена полей, реально существующих в исходном интерфейсе. В интерфейсе <code>Foydalanuvchi</code> нет поля <code>familiya</code>, поэтому TypeScript сразу выдаёт ошибку компиляции &mdash; это позволяет заранее обнаружить опечатки или неверные предположения в коде.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужны utility types?</h4>
<p>Они позволяют <strong>создавать новый тип</strong> из существующего (например <code>interface</code>), не переписывая его вручную заново. Это предотвращает дублирование кода, и при изменении исходного интерфейса производные типы обновляются автоматически.</p>

<h4>2. Разница между Partial и Readonly</h4>
<p><code>Partial&lt;T&gt;</code> делает все поля <strong>опциональными</strong> (добавляет <code>?</code>) &mdash; обычно используется в функциях обновления (update). <code>Readonly&lt;T&gt;</code> же делает все поля <strong>неизменяемыми</strong> &mdash; объект нельзя изменить после создания.</p>

<h4>3. Pick и Omit — противоположны друг другу</h4>
<p><code>Pick&lt;T, Keys&gt;</code> <strong>берёт</strong> только указанные поля (остальные отбрасывает). <code>Omit&lt;T, Keys&gt;</code> же <strong>исключает</strong> указанные поля (берёт остальные). Оба достигают похожей цели, но разными путями.</p>

<h4>4. Когда используется Record?</h4>
<p><code>Record&lt;Keys, ValueType&gt;</code> используется для объектов в форме "ключ-значение" &mdash; например, очень удобен для структур вроде "название региона → численность населения" или "название цвета → код цвета".</p>

<h4>5. Почему несуществующее поле в Pick даёт ошибку?</h4>
<p>TypeScript реализует utility types как <strong>generic</strong> &mdash; параметр <code>K</code> в <code>Pick&lt;T, K&gt;</code> <strong>обязан</strong> быть одним из реальных имён полей <code>T</code> (это обеспечивается через constraint <code>keyof T</code>). Если указано несуществующее имя, оно не соответствует этому ограничению, и возникает ошибка.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>Partial&lt;T&gt;</code> — делает все поля опциональными</li>
<li>✅ <code>Readonly&lt;T&gt;</code> — делает все поля неизменяемыми</li>
<li>✅ <code>Pick&lt;T, Keys&gt;</code> — берёт только указанные поля</li>
<li>✅ <code>Omit&lt;T, Keys&gt;</code> — исключает указанные поля</li>
<li>✅ <code>Record&lt;Keys, ValueType&gt;</code> — создаёт тип объекта в форме "ключ-значение"</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 9: Utility Types
// ════════════════════════════════════════════════════════════════════

interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

// ─────────────────────────────────────────────────────────────────────
// 1) Partial и Readonly
// ─────────────────────────────────────────────────────────────────────

function foydalanuvchiniYangilash(id: number, ozgarishlar: Partial<Foydalanuvchi>): void {
  console.log(`Foydalanuvchi ${id} yangilanmoqda:`, ozgarishlar);
}

foydalanuvchiniYangilash(1, { ism: "Yangi Ism" });

const sobitFoydalanuvchi: Readonly<Foydalanuvchi> = { id: 1, ism: "Olim", email: "olim@mail.uz" };

// ─────────────────────────────────────────────────────────────────────
// 2) Pick и Omit
// ─────────────────────────────────────────────────────────────────────

type FoydalanuvchiIsmi = Pick<Foydalanuvchi, "id" | "ism">;
const qisqaMalumot: FoydalanuvchiIsmi = { id: 1, ism: "Olim" };

type FoydalanuvchiParolsiz = Omit<Foydalanuvchi, "email">;
const xavfsizMalumot: FoydalanuvchiParolsiz = { id: 1, ism: "Olim" };

// ─────────────────────────────────────────────────────────────────────
// 3) Record
// ─────────────────────────────────────────────────────────────────────

type ViloyatAholisi = Record<string, number>;

const aholi: ViloyatAholisi = {
  Toshkent: 2900000,
  Samarqand: 550000,
};

type RangKodlari = Record<"qizil" | "yashil" | "kok", string>;
const ranglar: RangKodlari = {
  qizil: "#FF0000",
  yashil: "#00FF00",
  kok: "#0000FF",
};

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - несуществующее поле в Pick (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
type Xato = Pick<Foydalanuvchi, "id" | "familiya">;
// ❌ Property 'familiya' does not exist on type 'Foydalanuvchi'.
*/
"""

EX = {
    4020: {
        "title": "Что делает Partial<T>?",
        "description": "Что изменяет тип Partial<Foydalanuvchi> по сравнению с исходным интерфейсом?",
        "hint": "Часто используется в функциях обновления (update).",
        "explanation": "Partial<T> делает все поля исходного интерфейса опциональными — как если бы к каждому добавили '?'.",
    },
    4021: {
        "title": "Разница между Pick и Omit",
        "description": "В чём основное различие между Pick<T, Keys> и Omit<T, Keys>?",
        "hint": "Они служат противоположным целям.",
        "explanation": "Pick<T, Keys> берёт только указанные поля (остальные отбрасывает), Omit<T, Keys> же исключает указанные поля (берёт остальные).",
    },
    4022: {
        "title": "Расположите процесс создания типа Record",
        "description": "Расположите процесс создания и использования типа type ViloyatAholisi = Record<string, number>.",
        "hint": "",
        "explanation": "",
    },
    4023: {
        "title": "Utility type, делающий все поля неизменяемыми",
        "description": "Какой utility type делает все поля интерфейса неизменяемыми (readonly)? (напишите название)",
        "hint": "",
        "expected_answer": "Readonly",
    },
    4024: {
        "title": "Почему несуществующее имя поля в Pick даёт ошибку?",
        "description": (
            "При объявлении interface Foydalanuvchi { id: number; ism: "
            "string; email: string; }, почему при написании "
            "Pick<Foydalanuvchi, \"id\" | \"familiya\"> TypeScript даёт "
            "ошибку, хотя familiya - обычное слово? Объясните своими "
            "словами."
        ),
        "hint": "Какому ограничению подчиняется параметр Keys внутри Pick?",
        "expected_answer": "Pick<T, Keys> реализован как generic, и второй параметр (Keys) обязан быть одним из реально существующих имён полей интерфейса T (keyof T). В интерфейсе Foydalanuvchi поле familiya вообще не объявлено, поэтому \"familiya\" не соответствует этому ограничению, и TypeScript выдаёт ошибку во время компиляции. Эта защита позволяет сразу обнаружить опечатки в коде (например, если написать familya вместо familiya).",
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
