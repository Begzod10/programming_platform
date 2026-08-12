"""Russian translation for TypeScript Asoslari, lesson order=9 (L10, CAPSTONE)."""
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

LESSON_ID = 684

TITLE_RU = "10-CAPSTONE: Полностью типизированный мини-проект"

TEXT_RU = """\
<h2>CAPSTONE — полностью типизированный Репозиторий задач</h2>

<pre class="mermaid">
flowchart TB
    IFACE["interface Vazifa"] --> DTO1["Omit&lt;Vazifa,'id'&gt; — для создания"]
    IFACE --> DTO2["Partial&lt;Omit&lt;Vazifa,'id'&gt;&gt; — для обновления"]
    GEN["interface Repozitoriy&lt;T&gt;"] -->|implements| REPO["class VazifaRepozitoriyi"]
    REPO --> CRUD["hamma() / topish() / qoshish() / yangilash() / ochirish()"]
</pre>

<p>Объединим всё, что изучили за 8 уроков &mdash; <code>interface</code>, типизацию функций, union/generics, классы, enum и utility types &mdash; и построим настоящий небольшой проект: <strong>типизированный Репозиторий задач (Task)</strong>. Это &mdash; финальное испытание курса.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — базовый интерфейс и производные от него DTO-типы</h4>
<pre><code>interface Vazifa {
  id: number;
  sarlavha: string;
  holat: "kutilmoqda" | "bajarilmoqda" | "tugallandi"; // ❗ literal type (урок 8)
  muhimlik: number;
}

// Для создания - id не нужен (даётся автоматически)
type VazifaYaratishDTO = Omit<Vazifa, "id">; // ❗ Omit (урок 9)

// Для обновления - id не меняется, все остальные поля опциональны
type VazifaYangilashDTO = Partial<Omit<Vazifa, "id">>; // ❗ Partial + Omit вместе</code></pre>

<h4>БЛОК 2 — generic-интерфейс Repozitoriy и его реализация через класс</h4>
<pre><code>interface Repozitoriy<T extends { id: number }> { // ❗ generic constraint (урок 6)
  hamma(): T[];
  topish(id: number): T | undefined;
  qoshish(item: Omit<T, "id">): T;
  yangilash(id: number, ozgarishlar: Partial<Omit<T, "id">>): T | undefined;
  ochirish(id: number): boolean;
}

class VazifaRepozitoriyi implements Repozitoriy<Vazifa> { // ❗ implements (урок 7)
  private vazifalar: Vazifa[] = []; // ❗ private (урок 7)
  private keyingiId = 1;

  hamma(): Vazifa[] {
    return this.vazifalar;
  }

  topish(id: number): Vazifa | undefined {
    return this.vazifalar.find((v) => v.id === id);
  }

  qoshish(item: Omit<Vazifa, "id">): Vazifa {
    const yangi: Vazifa = { id: this.keyingiId++, ...item };
    this.vazifalar.push(yangi);
    return yangi;
  }

  yangilash(id: number, ozgarishlar: Partial<Omit<Vazifa, "id">>): Vazifa | undefined {
    const vazifa = this.topish(id);
    if (!vazifa) return undefined;
    Object.assign(vazifa, ozgarishlar);
    return vazifa;
  }

  ochirish(id: number): boolean {
    const boshlangichUzunlik = this.vazifalar.length;
    this.vazifalar = this.vazifalar.filter((v) => v.id !== id);
    return this.vazifalar.length < boshlangichUzunlik;
  }
}</code></pre>

<h4>БЛОК 3 — использование репозитория</h4>
<pre><code>const repo = new VazifaRepozitoriyi();

const vazifa1 = repo.qoshish({ sarlavha: "TypeScript o'rganish", holat: "bajarilmoqda", muhimlik: 5 });
const vazifa2 = repo.qoshish({ sarlavha: "Loyihani topshirish", holat: "kutilmoqda", muhimlik: 4 });

console.log(repo.hamma().length); // 2

repo.yangilash(vazifa1.id, { holat: "tugallandi" }); // ✅ обновляет только поле 'holat'
console.log(repo.topish(vazifa1.id)?.holat); // "tugallandi"

console.log(repo.ochirish(vazifa2.id)); // true
console.log(repo.hamma().length); // 1</code></pre>

<h3>🐛 Намеренная ошибка — передача поля id в DTO-типе</h3>
<pre><code>const yangiVazifa: VazifaYaratishDTO = {
  id: 99, // ❌ Ошибка: Object literal may only specify known properties,
          //         и 'id' отсутствует в VazifaYaratishDTO (Omit<Vazifa, "id">)
  sarlavha: "Test",
  holat: "kutilmoqda",
  muhimlik: 1,
};</code></pre>

<p><strong>Результат:</strong> так как тип <code>VazifaYaratishDTO</code> получен через <code>Omit&lt;Vazifa, "id"&gt;</code>, поле <code>id</code> в нём <strong>полностью отсутствует</strong>. Поэтому попытка добавить значение <code>id</code> в объект этого типа считается TypeScript ошибкой &mdash; это и есть цель <code>Omit</code>: предотвратить, чтобы пользователь (или разработчик) случайно сам задавал ID на этапе создания (так как ID обычно автоматически присваивает сам репозиторий).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему для VazifaYaratishDTO нужен отдельный тип?</h4>
<p>При создании новой задачи пользователь не передаёт <code>id</code> &mdash; его автоматически присваивает сам репозиторий (<code>keyingiId++</code>). <code>Omit&lt;Vazifa, "id"&gt;</code> точно отражает эту ситуацию: "все поля Vazifa, кроме <code>id</code>".</p>

<h4>2. Почему при обновлении Partial и Omit используются ВМЕСТЕ?</h4>
<p>При обновлении: (1) <code>id</code> вообще нельзя менять (<code>Omit</code>), и (2) КАЖДОЕ из остальных полей должно быть опциональным, потому что пользователь может обновить только одно поле (например <code>holat</code>) (<code>Partial</code>). Их объединение одновременно удовлетворяет оба этих требования.</p>

<h4>3. Почему Repozitoriy&lt;T&gt; требует generic constraint (<code>extends { id: number }</code>)?</h4>
<p>Внутренние методы репозитория (<code>topish</code>, <code>ochirish</code>) полагаются на поле <code>id</code>. Если бы для <code>T</code> не было никакого ограничения, TypeScript не смог бы гарантировать наличие поля <code>id</code> у <code>T</code>. <code>extends { id: number }</code> даёт именно эту гарантию.</p>

<h4>4. Почему класс использует private-свойство (<code>vazifalar</code>)?</h4>
<p>Если бы массив <code>vazifalar</code> был <code>public</code>, внешний код мог бы напрямую, без какой-либо проверки, изменить его (например, добавить задачу без ID). Сделав его <code>private</code>, изменить его можно только через методы <code>qoshish</code>/<code>yangilash</code>/<code>ochirish</code> &mdash; это инкапсуляция.</p>

<h4>5. Какие концепции из 8 уроков объединяет этот проект?</h4>
<p><code>interface</code> (урок 3), literal types (урок 8), generics и constraint (урок 6), класс и <code>implements</code>/<code>private</code> (урок 7), utility types <code>Omit</code>/<code>Partial</code> (урок 9) &mdash; все они работают вместе в одном небольшом, но реальном проекте.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Как в реальных проектах из <code>interface</code> через <code>Omit</code>/<code>Partial</code> создаются DTO-типы</li>
<li>✅ Как и зачем используется generic <code>Repozitoriy&lt;T extends { id: number }&gt;</code></li>
<li>✅ Как <code>class ... implements Repozitoriy&lt;Vazifa&gt;</code> реализует generic-интерфейс через класс</li>
<li>✅ Как private-свойство обеспечивает инкапсуляцию</li>
<li>✅ Как все основные концепции из 8 уроков объединяются в одном проекте</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 10 (CAPSTONE): Полностью типизированный Репозиторий задач
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Базовый интерфейс и DTO-типы
// ─────────────────────────────────────────────────────────────────────

interface Vazifa {
  id: number;
  sarlavha: string;
  holat: "kutilmoqda" | "bajarilmoqda" | "tugallandi";
  muhimlik: number;
}

type VazifaYaratishDTO = Omit<Vazifa, "id">;
type VazifaYangilashDTO = Partial<Omit<Vazifa, "id">>;

// ─────────────────────────────────────────────────────────────────────
// 2) Generic-интерфейс Repozitoriy и реализация через класс
// ─────────────────────────────────────────────────────────────────────

interface Repozitoriy<T extends { id: number }> {
  hamma(): T[];
  topish(id: number): T | undefined;
  qoshish(item: Omit<T, "id">): T;
  yangilash(id: number, ozgarishlar: Partial<Omit<T, "id">>): T | undefined;
  ochirish(id: number): boolean;
}

class VazifaRepozitoriyi implements Repozitoriy<Vazifa> {
  private vazifalar: Vazifa[] = [];
  private keyingiId = 1;

  hamma(): Vazifa[] {
    return this.vazifalar;
  }

  topish(id: number): Vazifa | undefined {
    return this.vazifalar.find((v) => v.id === id);
  }

  qoshish(item: Omit<Vazifa, "id">): Vazifa {
    const yangi: Vazifa = { id: this.keyingiId++, ...item };
    this.vazifalar.push(yangi);
    return yangi;
  }

  yangilash(id: number, ozgarishlar: Partial<Omit<Vazifa, "id">>): Vazifa | undefined {
    const vazifa = this.topish(id);
    if (!vazifa) return undefined;
    Object.assign(vazifa, ozgarishlar);
    return vazifa;
  }

  ochirish(id: number): boolean {
    const boshlangichUzunlik = this.vazifalar.length;
    this.vazifalar = this.vazifalar.filter((v) => v.id !== id);
    return this.vazifalar.length < boshlangichUzunlik;
  }
}

// ─────────────────────────────────────────────────────────────────────
// 3) Использование
// ─────────────────────────────────────────────────────────────────────

const repo = new VazifaRepozitoriyi();

const vazifa1 = repo.qoshish({ sarlavha: "TypeScript o'rganish", holat: "bajarilmoqda", muhimlik: 5 });
const vazifa2 = repo.qoshish({ sarlavha: "Loyihani topshirish", holat: "kutilmoqda", muhimlik: 4 });

console.log(repo.hamma().length);

repo.yangilash(vazifa1.id, { holat: "tugallandi" });
console.log(repo.topish(vazifa1.id)?.holat);

console.log(repo.ochirish(vazifa2.id));
console.log(repo.hamma().length);

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - передача id в DTO (в комментарии)
// ─────────────────────────────────────────────────────────────────────

/*
const yangiVazifa: VazifaYaratishDTO = {
  id: 99, // ❌ 'id' отсутствует в VazifaYaratishDTO
  sarlavha: "Test",
  holat: "kutilmoqda",
  muhimlik: 1,
};
*/
"""

EX = {
    4030: {
        "title": "Почему VazifaYaratishDTO создаётся через Omit?",
        "description": "Почему type VazifaYaratishDTO = Omit<Vazifa, \"id\"> сделан именно так?",
        "hint": "Откуда берётся ID при добавлении новой задачи?",
        "explanation": "При создании id автоматически присваивает сам репозиторий (keyingiId++), поэтому в DTO-типе поля id вообще не должно быть — это обеспечивает Omit<Vazifa, \"id\">.",
    },
    4031: {
        "title": "Совместное использование Partial и Omit при обновлении",
        "description": "Почему VazifaYangilashDTO = Partial<Omit<Vazifa, \"id\">> использует ОБА вместе?",
        "hint": "При обновлении есть два требования: id не должен меняться, остальное — опционально.",
        "explanation": "Omit<Vazifa, \"id\"> исключает id (чтобы его нельзя было изменить), Partial делает все остальные поля опциональными (чтобы можно было обновить только нужное поле).",
    },
    4032: {
        "title": "Расположите процесс работы VazifaRepozitoriyi.qoshish()",
        "description": "Расположите внутренний процесс при вызове repo.qoshish({ sarlavha: ..., holat: ..., muhimlik: ... }).",
        "hint": "",
        "explanation": "",
    },
    4033: {
        "title": "Запись generic constraint в Repozitoriy<T>",
        "description": "В записи interface Repozitoriy<T extends { id: number }>, какая часть является generic constraint? (напишите именно эту часть, например: extends { id: number })",
        "hint": "Вспомните синтаксис constraint из урока 6.",
        "expected_answer": "extends { id: number }",
    },
    4034: {
        "title": "Почему свойство vazifalar сделано private?",
        "description": (
            "Внутри class VazifaRepozitoriyi объявлено private vazifalar: "
            "Vazifa[] = []. Какая проблема могла бы возникнуть, будь это "
            "свойство public? Как private решает эту проблему? Объясните "
            "своими словами."
        ),
        "hint": "Как внешний код мог бы бесконтрольно повлиять на public-свойство?",
        "expected_answer": "Если бы свойство vazifalar было public, внешний код мог бы напрямую, без какой-либо проверки, изменить его — например, добавить в массив задачу без ID или в некорректном состоянии, что нарушило бы внутреннюю целостность репозитория. Сделав vazifalar private, эта проблема решается, потому что теперь изменить его можно только через методы внутри класса (qoshish, yangilash, ochirish), то есть только по правилам, которые задаёт сам репозиторий — это практическая польза принципа инкапсуляции.",
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
