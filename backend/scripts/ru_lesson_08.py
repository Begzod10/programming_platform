"""Russian translation for course 72, lesson order=8 (L8)."""
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

LESSON_ID = 594

TITLE_RU = "8-Generics и сложные типы в компонентах"

TEXT_RU = """\
<h2>Generics и сложные типы — переиспользуемые типизированные компоненты</h2>

<pre class="mermaid">
flowchart LR
    L["List&lt;T&gt;"] -->|T = Foydalanuvchi| U["List of users"]
    L -->|T = Mahsulot| P["List of products"]
    L -->|один код, много типов| REUSE["Переиспользование + типобезопасность"]
</pre>

<p>В уроке 7 мы типизировали props для одного конкретного типа данных. Но некоторые компоненты — например, компонент "показать любой список" — должны работать с <strong>любым</strong> типом данных, не теряя типобезопасность. Для этого используются <strong>generics</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — generic-компонент</h4>
<pre><code>interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function List&lt;T&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return &lt;ul&gt;{items.map((item, i) =&gt; &lt;li key={i}&gt;{renderItem(item)}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<pre><code>interface Foydalanuvchi { id: number; ism: string; }
interface Mahsulot { id: number; nomi: string; narx: number; }

// Один компонент List — работает с обоими типами С ПОЛНОЙ типобезопасностью:
&lt;List&lt;Foydalanuvchi&gt; items={foydalanuvchilar}
  renderItem={(f) =&gt; &lt;span&gt;{f.ism}&lt;/span&gt;} /&gt;

&lt;List&lt;Mahsulot&gt; items={mahsulotlar}
  renderItem={(m) =&gt; &lt;span&gt;{m.nomi} — {m.narx} сум&lt;/span&gt;} /&gt;</code></pre>

<h4>БЛОК 2 — утилитарные типы: Partial, Pick, Omit</h4>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
  yosh: number;
}

// Partial<T> — делает все поля необязательными (идеально для функций обновления)
function foydalanuvchiniYangila(id: number, ozgarish: Partial&lt;Foydalanuvchi&gt;) {
  // ozgarish = { ism: "Новое имя" } — достаточно одного поля
}

// Pick<T, K> — выбирает только нужные поля
type FoydalanuvchiQisqa = Pick&lt;Foydalanuvchi, 'id' | 'ism'&gt;;
// { id: number; ism: string } — нет email и yosh

// Omit<T, K> — исключает ненужные поля
type YangiFoydalanuvchi = Omit&lt;Foydalanuvchi, 'id'&gt;;
// { ism: string; email: string; yosh: number } — нет id (создаёт сервер)</code></pre>

<h4>БЛОК 3 — типизация children</h4>
<pre><code>interface LayoutProps {
  children: React.ReactNode; // всё, что можно рендерить: текст, JSX, массив, null
}

function Layout({ children }: LayoutProps) {
  return &lt;div className="container"&gt;{children}&lt;/div&gt;;
}

// Или удобнее — утилита PropsWithChildren:
import { PropsWithChildren } from 'react';

interface CardProps { sarlavha: string; }

function Card({ sarlavha, children }: PropsWithChildren&lt;CardProps&gt;) {
  return (
    &lt;div className="card"&gt;
      &lt;h3&gt;{sarlavha}&lt;/h3&gt;
      {children}
    &lt;/div&gt;
  );
}</code></pre>

<h3>🐛 Намеренная ошибка — неограниченный generic</h3>
<pre><code>interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function ListWithId&lt;T&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return (
    &lt;ul&gt;
      {items.map((item) =&gt; (
        // ❌ Ошибка компиляции!
        &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<pre><code>Property 'id' does not exist on type 'T'.</code></pre>

<p><strong>Причина:</strong> <code>T</code> — <strong>неограниченный</strong> generic, то есть означает "любой тип". TypeScript ничего не знает о <code>T</code> — у него может быть поле <code>id</code>, а может и не быть. Чтобы обращаться к <code>item.id</code>, нужно <strong>ограничить</strong> <code>T</code>: сказать "T обязательно должен иметь поле id".</p>

<pre><code>// ✅ Правильно — T ограничен
function ListWithId&lt;T extends { id: number | string }&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return (
    &lt;ul&gt;
      {items.map((item) =&gt; (
        &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt; // ✅ теперь работает
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<h3>Теперь объясним</h3>

<h4>1. Generic — переменная для "типа, определяемого в будущем"</h4>
<p><code>&lt;T&gt;</code> — похож на обычный параметр функции, только не для значения, а для <strong>типа</strong>. При вызове <code>List&lt;Foydalanuvchi&gt;</code> TS внутри заменяет <code>T</code> на <code>Foydalanuvchi</code> и проверяет весь компонент соответственно.</p>

<h4>2. Ограничение через extends</h4>
<pre><code>function birinchi&lt;T extends { id: number }&gt;(royxat: T[]): T | undefined {
  return royxat[0];
}
// Теперь TS знает: T обязательно имеет поле id — item.id безопасен</code></pre>

<h4>3. Partial/Pick/Omit — когда что использовать?</h4>
<table>
<tr><th>Утилита</th><th>Применение</th></tr>
<tr><td><code>Partial&lt;T&gt;</code></td><td>Функции обновления — только изменённые поля</td></tr>
<tr><td><code>Pick&lt;T, K&gt;</code></td><td>Показ только нескольких полей из полного объекта (например, элемент списка)</td></tr>
<tr><td><code>Omit&lt;T, K&gt;</code></td><td>Создание типа "формы создания", исключая генерируемые сервером поля (id, createdAt)</td></tr>
</table>

<h4>4. children — React.ReactNode</h4>
<p><code>React.ReactNode</code> — <strong>всё</strong>, что React может отрендерить: string, number, JSX-элемент, массив, <code>null</code>, <code>undefined</code>, boolean. <code>PropsWithChildren&lt;Props&gt;</code> автоматически добавляет к <code>Props</code> поле <code>children?: ReactNode</code>, заменяя ручное написание.</p>

<h4>5. Когда нужен generic, а когда нет?</h4>
<p>Если компонент работает с <strong>одним конкретным</strong> типом данных (например, только карточка <code>Foydalanuvchi</code>) — достаточно обычного <code>interface</code>. Generic нужен только когда компонент <strong>действительно</strong> должен переиспользоваться с разными типами данных (List, Table, Select и подобные универсальные компоненты).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Generic-компонент (<code>&lt;T&gt;</code>) — один код с полной типобезопасностью для разных типов данных</li>
<li>✅ <code>T extends {...}</code> — ограничивает generic, позволяя безопасно обращаться к его полям</li>
<li>✅ <code>Partial&lt;T&gt;</code> — для обновления; <code>Pick&lt;T,K&gt;</code> — выбор; <code>Omit&lt;T,K&gt;</code> — исключение</li>
<li>✅ <code>children: React.ReactNode</code> или <code>PropsWithChildren&lt;Props&gt;</code> — типизация дочерних элементов</li>
<li>✅ Generic используется только при реальной необходимости переиспользования — не всегда</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 8: Generics и сложные типы
// ════════════════════════════════════════════════════════════════════

import { PropsWithChildren } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Generic-компонент — неограниченный (чтобы показать проблему)
// ─────────────────────────────────────────────────────────────────────

interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function ListOddiy<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, i) => <li key={i}>{renderItem(item)}</li>)}
    </ul>
  );
}

interface Foydalanuvchi { id: number; ism: string; email: string; yosh: number; }
interface Mahsulot { id: number; nomi: string; narx: number; }

function RoyxatlarDemo() {
  const foydalanuvchilar: Foydalanuvchi[] = [
    { id: 1, ism: 'Олим', email: 'olim@mail.uz', yosh: 22 },
  ];
  const mahsulotlar: Mahsulot[] = [
    { id: 1, nomi: 'Ноутбук', narx: 5000000 },
  ];

  return (
    <>
      <ListOddiy<Foydalanuvchi> items={foydalanuvchilar}
        renderItem={(f) => <span>{f.ism}</span>} />
      <ListOddiy<Mahsulot> items={mahsulotlar}
        renderItem={(m) => <span>{m.nomi} — {m.narx} сум</span>} />
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Намеренная ошибка — неограниченный generic, попытка item.id
// ─────────────────────────────────────────────────────────────────────

/*
function ListWithIdXato<T>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        // ❌ Property 'id' does not exist on type 'T'.
        <li key={item.id}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}
*/

// ✅ Правильно — T ограничен: "обязательно имеет поле id"
function ListWithId<T extends { id: number | string }>({ items, renderItem }: ListProps<T>) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Partial / Pick / Omit
// ─────────────────────────────────────────────────────────────────────

function foydalanuvchiniYangila(id: number, ozgarish: Partial<Foydalanuvchi>) {
  console.log(`Обновление #${id}:`, ozgarish);
}
// foydalanuvchiniYangila(1, { ism: 'Новое имя' }); — достаточно одного поля

type FoydalanuvchiQisqa = Pick<Foydalanuvchi, 'id' | 'ism'>;
// { id: number; ism: string }

type YangiFoydalanuvchi = Omit<Foydalanuvchi, 'id'>;
// { ism: string; email: string; yosh: number } — id нет, создаёт сервер

function RoyxatQisqaKorinish({ user }: { user: FoydalanuvchiQisqa }) {
  return <span>{user.id}: {user.ism}</span>;
}

// ─────────────────────────────────────────────────────────────────────
// 4) children — React.ReactNode и PropsWithChildren
// ─────────────────────────────────────────────────────────────────────

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  return <div className="container">{children}</div>;
}

interface CardProps { sarlavha: string; }

function Card({ sarlavha, children }: PropsWithChildren<CardProps>) {
  return (
    <div className="card">
      <h3>{sarlavha}</h3>
      {children}
    </div>
  );
}
"""

EX = {
    3599: {
        "title": "Зачем нужен generic-компонент?",
        "description": "Какова основная цель создания generic-компонента вроде List<T>?",
        "hint": "List<Foydalanuvchi> и List<Mahsulot> — один код, два разных полностью типизированных использования.",
        "explanation": "Generic-компоненты позволяют переиспользовать однажды написанный компонент с разными типами данных, сохраняя полную проверку типов каждый раз.",
    },
    3600: {
        "title": "Почему item.id вызывает ошибку с неограниченным T?",
        "description": "Внутри function List<T>({ items }: {...}) при написании items.map(item => item.id), почему TypeScript выдаёт ошибку компиляции?",
        "hint": "T означает \"любой тип\". TS ничего не знает про T, если это не указано через extends.",
        "explanation": "Неограниченный T может быть любым типом, включая тип без поля id. Без ограничения `T extends { id: ... }`, TS не может безопасно разрешить обращение к item.id.",
    },
    3601: {
        "title": "Какой utility type подходит?",
        "description": "Вы хотите создать новый тип, содержащий из объекта пользователя только поля 'id' и 'ism'. Какой utility type используется?",
        "hint": "Pick — ВЫБИРАЕТ (остаются только эти поля).",
        "explanation": "Pick<T, K> создаёт новый тип, содержащий из T только поля, указанные в K.",
    },
    3602: {
        "title": "Почему generic нужно использовать не всегда, а только по необходимости?",
        "description": "Если компонент должен работать только с одним конкретным типом данных (например, только Foydalanuvchi), почему делать его всё равно generic не считается хорошей практикой? Объясните своими словами.",
        "expected_answer": "Generic-компоненты добавляют дополнительную сложность — их сложнее читать и понимать, потому что не сразу видно, с каким типом данных работает компонент. Если компонент реально используется только с одним конкретным типом (например, Foydalanuvchi), обычный interface яснее, понятнее для чтения, и автодополнение в IDE работает лучше. Generic оправдывает себя только тогда, когда компонент действительно должен переиспользоваться с несколькими разными типами данных.",
        "hint": "Подумайте об удобстве чтения кода и ненужной сложности.",
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
