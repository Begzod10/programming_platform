"""Russian translation for course 72, lesson order=7 (L7)."""
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

LESSON_ID = 592

TITLE_RU = "7-React + TypeScript: типизация props и state"

TEXT_RU = """\
<h2>React + TypeScript: типизация props и state</h2>

<pre class="mermaid">
flowchart LR
    P["interface CardProps"] -->|проверяет во время компиляции| C["компонент Card"]
    C -->|передан неверный prop| E["Ошибка компиляции — не доходит до runtime"]
</pre>

<p>В курсе "React Asoslari" все написанные вами компоненты — <code>.jsx</code>. Если ошибётесь в имени prop'а или передадите значение неверного типа, узнаете об этом только в <strong>runtime</strong>, часто уже после того, как пользователь увидит это в продакшене. TypeScript показывает эти ошибки <strong>во время написания кода</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — от .jsx к .tsx: первый типизированный компонент</h4>
<pre><code>// Терминал — для нового проекта:
npm create vite@latest mening-app -- --template react-ts</code></pre>

<pre><code>// Card.tsx
interface CardProps {
  sarlavha: string;
  matn: string;
  yulduzlar?: number; // ? — необязательный prop
}

function Card({ sarlavha, matn, yulduzlar = 0 }: CardProps) {
  return (
    &lt;div className="card"&gt;
      &lt;h3&gt;{sarlavha}&lt;/h3&gt;
      &lt;p&gt;{matn}&lt;/p&gt;
      &lt;span&gt;{'⭐'.repeat(yulduzlar)}&lt;/span&gt;
    &lt;/div&gt;
  );
}

// ❌ Ошибка компиляции — нет matn:
// &lt;Card sarlavha="React" /&gt;
// Property 'matn' is missing in type '{ sarlavha: string; }' but required in type 'CardProps'.

// ❌ Ошибка компиляции — неверный тип:
// &lt;Card sarlavha="React" matn="..." yulduzlar="пять" /&gt;
// Type 'string' is not assignable to type 'number | undefined'.</code></pre>

<h4>БЛОК 2 — типизация useState&lt;T&gt;</h4>
<pre><code>function Forma() {
  // TS автоматически выводит: useState("") → string
  const [ism, setIsm] = useState("");

  // Но если начальное значение null — TS выведет тип "null",
  // и передача string позже вызовет ошибку. Нужен явный тип:
  const [xato, setXato] = useState&lt;string | null&gt;(null);

  // Для массива/объекта — так же:
  interface Foydalanuvchi { id: number; ism: string; }
  const [royxat, setRoyxat] = useState&lt;Foydalanuvchi[]&gt;([]);

  return null;
}</code></pre>

<h4>БЛОК 3 — типизация обработчиков событий</h4>
<pre><code>function Input() {
  const [qiymat, setQiymat] = useState("");

  // ChangeEvent<HTMLInputElement> — точный тип для изменения input
  const onChange = (e: React.ChangeEvent&lt;HTMLInputElement&gt;) =&gt; {
    setQiymat(e.target.value); // TS знает — target это input, .value существует
  };

  const onSubmit = (e: React.FormEvent&lt;HTMLFormElement&gt;) =&gt; {
    e.preventDefault();
    console.log(qiymat);
  };

  return (
    &lt;form onSubmit={onSubmit}&gt;
      &lt;input value={qiymat} onChange={onChange} /&gt;
    &lt;/form&gt;
  );
}</code></pre>

<h3>🐛 Намеренная ошибка — неверная типизация события</h3>
<pre><code>function InputXato() {
  const [qiymat, setQiymat] = useState("");

  // ❌ Тип e вообще не указан — "implicitly has an 'any' type"
  const onChange = (e) =&gt; {
    setQiymat(e.target.value);
  };

  return &lt;input value={qiymat} onChange={onChange} /&gt;;
}</code></pre>

<pre><code>Parameter 'e' implicitly has an 'any' type.
  ts(7006)</code></pre>

<p><strong>Причина:</strong> если в <code>tsconfig.json</code> включён <code>strict: true</code> (или <code>noImplicitAny</code>), TypeScript требует явный тип для каждого параметра. Если тип не указан — он автоматически становится <code>any</code>, что равносильно "отключению TypeScript": для значения типа <code>any</code> TS вообще не проверяет ничего, даже если вы допустите ошибку, он промолчит.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему эти ошибки компиляции важны?</h4>
<p>В JS если написать <code>&lt;Card sarlavha="X" /&gt;</code> (без matn) — код будет работать, просто на месте <code>matn</code> появится <code>undefined</code>, без какого-либо сообщения об ошибке. В TS же это <strong>останавливается на этапе сборки</strong>, до попадания в продакшен.</p>

<h4>2. interface против type — что использовать для компонентов?</h4>
<pre><code>// Оба работают, для props больше рекомендуется interface
interface CardProps { sarlavha: string; }
type CardPropsAlt = { sarlavha: string; };</code></pre>

<h4>3. Когда нужен useState&lt;T&gt;?</h4>
<table>
<tr><th>TS выводит автоматически</th><th>Нужен явный тип</th></tr>
<tr><td><code>useState(0)</code> → number</td><td><code>useState&lt;string | null&gt;(null)</code></td></tr>
<tr><td><code>useState("")</code> → string</td><td><code>useState&lt;Foydalanuvchi[]&gt;([])</code></td></tr>
<tr><td><code>useState(false)</code> → boolean</td><td><code>useState&lt;'idle'|'loading'|'error'&gt;('idle')</code></td></tr>
</table>
<p>Правило: если начальное значение "не может показать" все будущие состояния (например, начинается с <code>null</code>, а потом станет string) — указывайте явный generic-тип.</p>

<h4>4. Наиболее часто используемые типы событий</h4>
<table>
<tr><th>Элемент</th><th>Тип события</th></tr>
<tr><td><code>&lt;input onChange&gt;</code></td><td><code>React.ChangeEvent&lt;HTMLInputElement&gt;</code></td></tr>
<tr><td><code>&lt;form onSubmit&gt;</code></td><td><code>React.FormEvent&lt;HTMLFormElement&gt;</code></td></tr>
<tr><td><code>&lt;button onClick&gt;</code></td><td><code>React.MouseEvent&lt;HTMLButtonElement&gt;</code></td></tr>
<tr><td><code>&lt;input onKeyDown&gt;</code></td><td><code>React.KeyboardEvent&lt;HTMLInputElement&gt;</code></td></tr>
</table>

<h4>5. Необязательные props и значение по умолчанию</h4>
<pre><code>interface TugmaProps {
  label: string;
  turi?: 'primary' | 'danger'; // ? — необязательный, ограничен union-типом
}

function Tugma({ label, turi = 'primary' }: TugmaProps) { /* ... */ }</code></pre>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Props типизируются через <code>interface</code> — неверный/отсутствующий prop вызывает ошибку компиляции</li>
<li>✅ <code>useState&lt;T&gt;</code> — явный тип нужен там, где TS не может вывести его сам (например, начальное <code>null</code>)</li>
<li>✅ Обработчики событий типизируются точными типами вроде <code>React.ChangeEvent&lt;HTMLInputElement&gt;</code></li>
<li>✅ Отсутствие типа (при включённом <code>noImplicitAny</code>) — ошибка компиляции "implicitly has an 'any' type"</li>
<li>✅ <code>any</code> отключает проверки TypeScript, по возможности избегайте его</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 7: React + TypeScript — типизация props и state
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Props — типизация через interface
// ─────────────────────────────────────────────────────────────────────

interface CardProps {
  sarlavha: string;
  matn: string;
  yulduzlar?: number;
}

function Card({ sarlavha, matn, yulduzlar = 0 }: CardProps) {
  return (
    <div className="card">
      <h3>{sarlavha}</h3>
      <p>{matn}</p>
      <span>{'⭐'.repeat(yulduzlar)}</span>
    </div>
  );
}

// <Card sarlavha="React" />                          // ❌ не хватает matn
// <Card sarlavha="React" matn="..." yulduzlar="5" />  // ❌ yulduzlar должен быть number, не string

// ─────────────────────────────────────────────────────────────────────
// 2) useState<T> — случаи, требующие явного типа
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi {
  id: number;
  ism: string;
}

function ForamaDemo() {
  const [ism, setIsm] = useState("");                       // TS выводит: string
  const [xato, setXato] = useState<string | null>(null);     // нужен явный тип
  const [royxat, setRoyxat] = useState<Foydalanuvchi[]>([]); // нужен явный тип

  return (
    <div>
      <input value={ism} onChange={(e) => setIsm(e.target.value)} />
      {xato && <p>{xato}</p>}
      <ul>{royxat.map(f => <li key={f.id}>{f.ism}</li>)}</ul>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Типизация обработчиков событий
// ─────────────────────────────────────────────────────────────────────

function Forma() {
  const [qiymat, setQiymat] = useState("");

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQiymat(e.target.value);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(qiymat);
  };

  const onButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Нажато', e.currentTarget.name);
  };

  return (
    <form onSubmit={onSubmit}>
      <input value={qiymat} onChange={onChange} />
      <button name="yubor" onClick={onButtonClick}>Отправить</button>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — не указать тип события
// ─────────────────────────────────────────────────────────────────────

/*
function InputXato() {
  const [qiymat, setQiymat] = useState("");

  // ❌ Parameter 'e' implicitly has an 'any' type. ts(7006)
  const onChange = (e) => {
    setQiymat(e.target.value);
  };

  return <input value={qiymat} onChange={onChange} />;
}
*/

// ─────────────────────────────────────────────────────────────────────
// 5) Необязательный prop + ограничение union-типом
// ─────────────────────────────────────────────────────────────────────

interface TugmaProps {
  label: string;
  turi?: 'primary' | 'danger';
}

function Tugma({ label, turi = 'primary' }: TugmaProps) {
  return <button className={`btn btn-${turi}`}>{label}</button>;
}
"""

EX = {
    3591: {
        "title": "Как типизируются props?",
        "description": "Какой стандартный способ типизации props компонента в React + TypeScript?",
        "hint": "function Card({ ... }: CardProps) — откуда берётся CardProps?",
        "explanation": "В TypeScript props обычно объявляются как отдельный `interface` (или `type`) и присоединяются к параметру компонента в виде `: CardProps`.",
    },
    3592: {
        "title": "Когда нужен явный тип для useState<T>?",
        "description": "В каком случае для useState обязательно нужно указывать явный generic-тип (<T>), а TS не может вывести его автоматически?",
        "hint": "Если начальное значение null, TS знает только тип \"null\", а не будущую строку.",
        "explanation": "С useState(null) TS выводит тип состояния только как `null`. Если ожидается, что позже будет присвоено значение типа string, нужно указать явный union-тип (`string | null`).",
    },
    3593: {
        "title": "Какой правильный тип события для onChange у input?",
        "description": "Какой правильный TypeScript-тип для параметра обработчика события у <input onChange={...}>?",
        "hint": "Изменение значения input — событие Change, тип элемента — HTMLInputElement.",
        "explanation": "Правильный тип для изменения input — `React.ChangeEvent<HTMLInputElement>`. Он говорит TS о существовании `e.target.value` и проверяет это.",
    },
    3594: {
        "title": "Почему ошибка на этапе компиляции лучше, чем runtime-ошибка?",
        "description": "Если вызвать <Card sarlavha=\"X\" /> (без prop matn), в JS код всё равно выполнится (matn станет undefined), а в TS возникнет ошибка компиляции. Почему эта разница важна, особенно в большой команде/проекте? Объясните своими словами.",
        "expected_answer": "В JavaScript отсутствующий prop проявляется только в runtime, часто в виде \"undefined\" или пустого места на экране пользователя, и это не всегда сразу заметно. TypeScript же показывает эту ошибку разработчику сразу при написании кода, в IDE и на этапе сборки — до попадания в продакшен. Это особенно важно в большой команде или проекте: если один разработчик изменит интерфейс компонента, все места, где он используется, автоматически проверяются, и несовместимые места сразу показываются как ошибки компиляции.",
        "hint": "Подумайте о том, когда (во время сборки или после того, как увидит пользователь) и кто увидит ошибку.",
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
