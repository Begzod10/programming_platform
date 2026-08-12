"""Russian translation for TypeScript Asoslari, lesson order=7 (L8)."""
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

LESSON_ID = 680

TITLE_RU = "8-Enum и Literal Types"

TEXT_RU = """\
<h2>Enum и Literal Types — набор ограниченных значений</h2>

<pre class="mermaid">
flowchart LR
    ENUM["enum Holat { Kutilmoqda, Tasdiqlandi, Bekor }"] --> USE["Holat.Tasdiqlandi"]
    LIT["type O'lcham = 'kichik' | 'orta' | 'katta'"] --> USE2["Только одно из этих 3 значений"]
</pre>

<p>Иногда переменная должна принимать <strong>только одно из заранее заданных, ограниченных</strong> значений &mdash; например, статус заказа может быть только "в ожидании", "подтверждён" или "отменён", и ничем другим. <strong>Enum</strong> и <strong>literal types</strong> &mdash; именно для этой цели.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — строковый enum</h4>
<pre><code>enum BuyurtmaHolati {
  Kutilmoqda = "KUTILMOQDA",
  Tasdiqlandi = "TASDIQLANDI",
  BekorQilindi = "BEKOR_QILINDI",
}

function holatniKorsatish(holat: BuyurtmaHolati): string {
  return `Holat: ${holat}`;
}

console.log(holatniKorsatish(BuyurtmaHolati.Tasdiqlandi)); // "Holat: TASDIQLANDI"
// holatniKorsatish("boshqa-narsa"); // ❌ Ошибка: не одно из значений enum</code></pre>

<h4>БЛОК 2 — literal types (типы с точным значением)</h4>
<pre><code>// Такое же ограничение можно создать и без enum
type OlchamTuri = "kichik" | "o'rta" | "katta"; // ❗ ТОЛЬКО эти 3 текстовых значения

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  if (olcham === "o'rta") return 35000;
  return 50000;
}

console.log(narxHisoblash("o'rta")); // 35000
// narxHisoblash("gigant"); // ❌ Ошибка: 'gigant' не соответствует OlchamTuri</code></pre>

<h4>БЛОК 3 — числовой enum и const assertion</h4>
<pre><code>enum Yonalish {
  Yuqori,  // ❗ по умолчанию 0
  Past,    // 1
  Chap,    // 2
  Ong,     // 3
}

console.log(Yonalish.Chap); // 2

// const assertion - помечает объект как "только для чтения" с точными literal-значениями
const sozlamalar = {
  til: "uz",
  rejim: "qorong'i",
} as const; // ❗ теперь til и rejim "заблокированы" ИМЕННО этими значениями

// sozlamalar.til = "ru"; // ❌ Ошибка: readonly, изменить нельзя</code></pre>

<h3>🐛 Намеренная ошибка — передача текста, не соответствующего literal type</h3>
<pre><code>type OlchamTuri = "kichik" | "o'rta" | "katta";

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  return 50000;
}

narxHisoblash("O'RTA"); // ❌ Ошибка: регистр важен, "O'RTA" ≠ "o'rta"!</code></pre>

<p><strong>Результат:</strong> literal types принимают <strong>только точно совпадающие</strong> значения &mdash; разница в регистре, пробеле или любая другая разница считается для TypeScript "совершенно другим значением". <code>"o'rta"</code> и <code>"O'RTA"</code> &mdash; два <strong>разных</strong> строковых литерала, даже если человеческому глазу они кажутся "одним и тем же". Это &mdash; строгость literal types, и именно эта строгость позволяет заранее выявлять ошибки.</p>

<h3>Теперь объясним</h3>

<h4>1. Для чего нужен enum?</h4>
<p><code>enum</code> позволяет задать ограниченный, именованный набор значений. Эти значения можно использовать в любом месте кода под удобочитаемым именем вроде <code>BuyurtmaHolati.Tasdiqlandi</code>, вместо того чтобы писать "сырой" текст ("TASDIQLANDI").</p>

<h4>2. Разница между строковым и числовым enum</h4>
<p>В строковом enum каждому члену задаётся конкретное текстовое значение (например <code>"KUTILMOQDA"</code>). В числовом enum, если значение не задано, TypeScript автоматически присваивает числа, начиная с 0. Строковый enum обычно понятнее и легче отлаживается, поэтому рекомендуется чаще.</p>

<h4>3. Что такое literal types и чем они отличаются от enum?</h4>
<p><code>type O'lcham = "kichik" | "o'rta" | "katta"</code> &mdash; это частный случай union type, означающий, что переменная может принимать только одно из этих точных текстовых значений. В отличие от enum, это только проверка типов на этапе компиляции &mdash; во время выполнения (runtime) отдельный объект не создаётся (более компактное, "лёгкое" решение).</p>

<h4>4. Что делает <code>as const</code> (const assertion)?</h4>
<p>Обычно свойства объекта считаются изменяемыми типами (например <code>string</code>). При добавлении <code>as const</code> TypeScript помечает каждое свойство как <strong>точное это значение</strong> (literal) и <code>readonly</code> &mdash; это очень полезно для настроек или констант.</p>

<h4>5. Почему literal types чувствительны к регистру?</h4>
<p>TypeScript сравнивает строковые литералы как <strong>точный текст</strong>, а не как "смысл" на человеческом языке. Поэтому <code>"o'rta"</code> и <code>"O'RTA"</code> считаются двумя совершенно разными значениями, и принимается только один из точно заданных вариантов.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>enum</code> — задаёт ограниченный, именованный набор значений (строковый или числовой)</li>
<li>✅ Literal types (<code>"a" | "b" | "c"</code>) — более лёгкая альтернатива enum</li>
<li>✅ <code>as const</code> — "блокирует" свойства объекта точным literal-значением и readonly</li>
<li>✅ Literal types чувствительны к регистру — требуется точное совпадение</li>
<li>✅ Enum и literal types используются, чтобы функция принимала только заранее заданные значения</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 8: Enum и Literal Types
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Строковый enum
// ─────────────────────────────────────────────────────────────────────

enum BuyurtmaHolati {
  Kutilmoqda = "KUTILMOQDA",
  Tasdiqlandi = "TASDIQLANDI",
  BekorQilindi = "BEKOR_QILINDI",
}

function holatniKorsatish(holat: BuyurtmaHolati): string {
  return `Holat: ${holat}`;
}

console.log(holatniKorsatish(BuyurtmaHolati.Tasdiqlandi));

// ─────────────────────────────────────────────────────────────────────
// 2) Literal types
// ─────────────────────────────────────────────────────────────────────

type OlchamTuri = "kichik" | "o'rta" | "katta";

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  if (olcham === "o'rta") return 35000;
  return 50000;
}

console.log(narxHisoblash("o'rta"));

// ─────────────────────────────────────────────────────────────────────
// 3) Числовой enum
// ─────────────────────────────────────────────────────────────────────

enum Yonalish {
  Yuqori,
  Past,
  Chap,
  Ong,
}

console.log(Yonalish.Chap);

// ─────────────────────────────────────────────────────────────────────
// 4) const assertion
// ─────────────────────────────────────────────────────────────────────

const sozlamalar = {
  til: "uz",
  rejim: "qorong'i",
} as const;

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - несовпадение регистра (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
narxHisoblash("O'RTA"); // ❌ Ошибка: "o'rta" и "O'RTA" - не одно и то же!
*/
"""

EX = {
    4010: {
        "title": "Для чего в основном используется enum?",
        "description": "Для чего в основном используется enum в TypeScript?",
        "hint": "Как статус заказа — может быть только одним из определённых вариантов.",
        "explanation": "enum задаёт ограниченный, именованный набор значений и позволяет использовать их под удобочитаемым именем.",
    },
    4011: {
        "title": "Как записывается literal type?",
        "description": "Как записывается тип, принимающий только одно из значений \"kichik\", \"o'rta\", \"katta\"?",
        "hint": "Это частный случай union type.",
        "explanation": "Literal types записываются через синтаксис union (|): каждое точное значение разделяется '|'.",
    },
    4012: {
        "title": "Расположите последствия применения as const",
        "description": "Расположите по порядку изменения, происходящие с объектом при применении as const.",
        "hint": "",
        "explanation": "",
    },
    4013: {
        "title": "С какого значения начинается числовой enum по умолчанию?",
        "description": "Если значение не задано, чему будет равен первый член числового enum? (ответьте числом)",
        "hint": "",
        "expected_answer": "0",
    },
    4014: {
        "title": "Почему literal type чувствителен к регистру?",
        "description": (
            "При объявлении type OlchamTuri = \"kichik\" | \"o'rta\" | "
            "\"katta\", почему вызов narxHisoblash(\"O'RTA\") даёт ошибку, "
            "хотя \"o'rta\" есть в списке? Объясните своими словами."
        ),
        "hint": "Для компьютера сравнение текста требует точного совпадения символов.",
        "expected_answer": "TypeScript сравнивает строковые литеральные типы как точную последовательность символов, а не как слова с \"одинаковым смыслом\" для человека. \"o'rta\" и \"O'RTA\" различаются регистром букв, поэтому с точки зрения компьютера это два совершенно разных значения. Тип OlchamTuri принимает только именно \"kichik\", \"o'rta\", \"katta\" (строчными буквами, именно в таком написании), поэтому \"O'RTA\" считается не входящим в этот список, и TypeScript выдаёт ошибку компиляции.",
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
