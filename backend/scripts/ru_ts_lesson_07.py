"""Russian translation for TypeScript Asoslari, lesson order=6 (L7)."""
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

LESSON_ID = 678

TITLE_RU = "7-Классы и модификаторы доступа"

TEXT_RU = """\
<h2>Классы и модификаторы доступа (Access Modifiers)</h2>

<pre class="mermaid">
flowchart TB
    CLASS["class BankHisobi"] --> PUB["public — доступен отовсюду"]
    CLASS --> PRIV["private — только внутри класса"]
    CLASS --> PROT["protected — в классе и его потомках"]
    IMPL["interface"] -.->|implements| CLASS
</pre>

<p>В JavaScript классы существуют, но возможность "скрыть" свойства ограничена. TypeScript добавляет к классам <strong>модификаторы доступа</strong> (access modifiers) &mdash; с их помощью можно точно задать, откуда можно обращаться к тому или иному свойству/методу.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — public, private, protected</h4>
<pre><code>class BankHisobi {
  public egasi: string;      // ❗ public — доступен отовсюду (по умолчанию)
  private balans: number;    // ❗ private — доступен ТОЛЬКО внутри этого класса
  protected hisobRaqami: string; // ❗ protected — в этом классе И его потомках

  constructor(egasi: string, boshlangichBalans: number, hisobRaqami: string) {
    this.egasi = egasi;
    this.balans = boshlangichBalans;
    this.hisobRaqami = hisobRaqami;
  }

  balansniKorish(): number {
    return this.balans; // ✅ внутри класса к private-свойству можно обращаться
  }
}

const hisob = new BankHisobi("Olim", 1000000, "UZ-001");
console.log(hisob.egasi);          // ✅ public — доступен извне
// console.log(hisob.balans);      // ❌ Ошибка: 'balans' private, извне доступа нет
console.log(hisob.balansniKorish()); // ✅ безопасный доступ через метод</code></pre>

<h4>БЛОК 2 — реализация интерфейса через класс (implements)</h4>
<pre><code>interface Hayvon {
  ism: string;
  ovozChiqarish(): string;
}

class It implements Hayvon { // ❗ класс It обязан предоставить ВСЁ из интерфейса Hayvon
  ism: string;

  constructor(ism: string) {
    this.ism = ism;
  }

  ovozChiqarish(): string {
    return "Vov-vov!";
  }
}

const kuchuk = new It("Rex");
console.log(kuchuk.ovozChiqarish()); // "Vov-vov!"</code></pre>

<h4>БЛОК 3 — abstract-класс</h4>
<pre><code>abstract class Shakl { // ❗ abstract — нельзя напрямую создать объект через 'new Shakl()'
  abstract yuzaniHisoblash(): number; // ❗ класс-потомок обязан реализовать

  malumotChiqarish(): string {
    return `Yuza: ${this.yuzaniHisoblash()}`;
  }
}

class Kvadrat extends Shakl {
  constructor(private tomon: number) {
    super();
  }
  yuzaniHisoblash(): number {
    return this.tomon * this.tomon;
  }
}

const kvadrat = new Kvadrat(5);
console.log(kvadrat.malumotChiqarish()); // "Yuza: 25"
// const shakl = new Shakl(); // ❌ Ошибка: Cannot create an instance of an abstract class</code></pre>

<h3>🐛 Намеренная ошибка — обращение к private-свойству извне</h3>
<pre><code>class BankHisobi {
  private balans: number = 1000;
}

const hisob = new BankHisobi();
console.log(hisob.balans); // ❌ Ошибка: Property 'balans' is private and only
                            //         accessible within class 'BankHisobi'.</code></pre>

<p><strong>Результат:</strong> при попытке обратиться к свойству, обозначенному <code>private</code>, <strong>извне</strong> класса TypeScript выдаёт ошибку компиляции. Это практическое применение принципа <strong>инкапсуляции</strong> (encapsulation): внешний код не может напрямую изменять внутреннее состояние класса, а может работать только через "контролируемые" методы, предоставленные самим классом (обычно <code>public</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Разница между public, private, protected</h4>
<p><code>public</code> (по умолчанию) &mdash; доступ отовсюду. <code>private</code> &mdash; только внутри этого класса. <code>protected</code> &mdash; доступ в этом классе и в унаследовавших (extends) от него классах-потомках, но не извне.</p>

<h4>2. Зачем нужен implements?</h4>
<p>Запись <code>class X implements InterfeysY</code> означает, что класс <code>X</code> <strong>обязан предоставить</strong> все свойства и методы, заданные в <code>InterfeysY</code>. Если чего-то не хватает, TypeScript выдаст ошибку компиляции.</p>

<h4>3. Что такое abstract class?</h4>
<p><code>abstract class</code> &mdash; класс, объект которого нельзя создать напрямую (через <code>new</code>), он служит только "шаблоном" (template) для других классов. <code>abstract</code>-методы <strong>обязательно</strong> должны быть реализованы в классе-потомке.</p>

<h4>4. Почему важна инкапсуляция (private)?</h4>
<p>Если бы все свойства были <code>public</code>, любой внешний код мог бы бесконтрольно изменять внутреннее состояние класса &mdash; это легко приводит к ошибкам. <code>private</code>-свойства гарантируют, что изменение возможно только по собственным правилам класса (например, что баланс никогда не станет отрицательным).</p>

<h4>5. Сокращённая запись внутри constructor</h4>
<p><code>constructor(private tomon: number)</code> &mdash; удобное сокращение TypeScript: одновременно объявляется <code>private</code>-свойство с именем <code>tomon</code> И значение из параметра конструктора автоматически присваивается <code>this.tomon</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>public</code> — доступен отовсюду, <code>private</code> — только внутри класса, <code>protected</code> — в классе и его потомках</li>
<li>✅ <code>implements</code> делает обязательным предоставление классом всех свойств/методов интерфейса</li>
<li>✅ <code>abstract class</code> — класс-шаблон для потомков, объект которого нельзя создать напрямую</li>
<li>✅ Обращение к <code>private</code>-свойству извне даёт ошибку компиляции (инкапсуляция)</li>
<li>✅ <code>constructor(private x: тип)</code> объединяет объявление свойства и присвоение значения в одной строке</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 7: Классы и модификаторы доступа
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) public, private, protected
// ─────────────────────────────────────────────────────────────────────

class BankHisobi {
  public egasi: string;
  private balans: number;
  protected hisobRaqami: string;

  constructor(egasi: string, boshlangichBalans: number, hisobRaqami: string) {
    this.egasi = egasi;
    this.balans = boshlangichBalans;
    this.hisobRaqami = hisobRaqami;
  }

  balansniKorish(): number {
    return this.balans;
  }
}

const hisob = new BankHisobi("Olim", 1000000, "UZ-001");
console.log(hisob.egasi);
console.log(hisob.balansniKorish());

// ─────────────────────────────────────────────────────────────────────
// 2) implements - реализация интерфейса через класс
// ─────────────────────────────────────────────────────────────────────

interface Hayvon {
  ism: string;
  ovozChiqarish(): string;
}

class It implements Hayvon {
  ism: string;

  constructor(ism: string) {
    this.ism = ism;
  }

  ovozChiqarish(): string {
    return "Vov-vov!";
  }
}

const kuchuk = new It("Rex");
console.log(kuchuk.ovozChiqarish());

// ─────────────────────────────────────────────────────────────────────
// 3) abstract-класс
// ─────────────────────────────────────────────────────────────────────

abstract class Shakl {
  abstract yuzaniHisoblash(): number;

  malumotChiqarish(): string {
    return `Yuza: ${this.yuzaniHisoblash()}`;
  }
}

class Kvadrat extends Shakl {
  constructor(private tomon: number) {
    super();
  }
  yuzaniHisoblash(): number {
    return this.tomon * this.tomon;
  }
}

const kvadrat = new Kvadrat(5);
console.log(kvadrat.malumotChiqarish());

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - доступ к private-свойству извне (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
class BankHisobiXato {
  private balans: number = 1000;
}
const hisobXato = new BankHisobiXato();
console.log(hisobXato.balans); // ❌ Property 'balans' is private
*/
"""

EX = {
    4000: {
        "title": "Откуда доступно private-свойство?",
        "description": "Откуда можно обращаться к свойству, обозначенному private?",
        "hint": "Это самый ограниченный уровень доступа.",
        "explanation": "К private-свойству можно обращаться только внутри того класса, где оно объявлено, даже не из классов-потомков.",
    },
    4001: {
        "title": "Для чего используется implements?",
        "description": "Что означает запись class X implements InterfeysY?",
        "hint": "Это \"контракт\" между интерфейсом и классом.",
        "explanation": "implements обязывает класс предоставить все свойства и методы, заданные в интерфейсе.",
    },
    4002: {
        "title": "Расположите процесс использования abstract-класса",
        "description": "Расположите процесс использования abstract class Shakl и его потомка Kvadrat.",
        "hint": "",
    },
    4003: {
        "title": "Какой модификатор доступа даёт доступ и в классах-потомках?",
        "description": "Какой модификатор доступа даёт доступ в этом классе И в унаследовавших от него классах-потомках (но не извне)? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "protected",
    },
    4004: {
        "title": "Почему важны private-свойства (инкапсуляция)?",
        "description": (
            "Если свойство balans в классе BankHisobi будет задано как "
            "public вместо private, к какой проблеме это может привести? "
            "Как использование private решает эту проблему? Объясните "
            "своими словами."
        ),
        "hint": "Как внешний код сможет изменить balans, если он public — без проверки?",
        "expected_answer": "Если balans будет public, любой внешний код сможет напрямую, без какой-либо проверки, присвоить hisob.balans любое значение (например отрицательное число) — это может привести к серьёзным ошибкам в такой системе, как банковский счёт (например к отрицательному балансу). Обозначение balans как private решает эту проблему, потому что теперь его можно изменить только через методы внутри класса (например через методы вроде pulQoshish или pulYechish, содержащие проверки) — это практическая польза принципа инкапсуляции.",
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
