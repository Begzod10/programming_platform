"""Russian translation for course 72, lesson order=6 (L6)."""
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

LESSON_ID = 590

TITLE_RU = "6-Selector'ы и производительность (reselect)"

TEXT_RU = """\
<h2>Selector'ы и производительность — мемоизация с createSelector</h2>

<pre class="mermaid">
flowchart LR
    S1["state.todos.items"] --> CS["createSelector"]
    CS -->|входные данные не изменились| CACHE["возвращает кешированный результат"]
    CS -->|входные данные изменились| RECALC["пересчитывает + новый результат"]
</pre>

<p>В уроке 3 мы видели проблему: selector с <code>.filter()</code> каждый раз возвращает новый array, даже если результат одинаков. В этом уроке решим это правильно с помощью <strong>createSelector</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — вспомним проблему из урока 3</h4>
<pre><code>// Из урока 3 — каждый раз новый array при вызове:
const qolgan = useSelector((state) =&gt;
  state.todos.items.filter((t) =&gt; !t.done)
);</code></pre>

<h4>БЛОК 2 — решение с createSelector</h4>
<pre><code>import { createSelector } from '@reduxjs/toolkit';

// Входной selector — какую часть state отслеживаем
const selectTodoItems = (state) =&gt; state.todos.items;

// createSelector(inputSelectors[], resultFn)
export const selectQolganTodos = createSelector(
  [selectTodoItems],
  (items) =&gt; items.filter((t) =&gt; !t.done) // пересчитывается только при изменении items
);</code></pre>

<pre><code>function QolganSoni() {
  const qolgan = useSelector(selectQolganTodos);
  console.log("📋 QolganSoni перерендерился");
  return &lt;p&gt;Невыполнено: {qolgan.length}&lt;/p&gt;;
}</code></pre>

<p>Теперь при dispatch <code>toggleTheme()</code>: <code>selectTodoItems(state)</code> — не изменился (ссылка <code>items</code> осталась той же, так как todos slice не затронут). <code>createSelector</code> это видит и <strong>возвращает предыдущий кешированный array, не пересчитывая</strong>. Результат: <code>QolganSoni</code> не перерендерится.</p>

<h4>БЛОК 3 — несколько входных selector'ов</h4>
<pre><code>const selectTheme = (state) =&gt; state.app.theme;

export const selectStatistika = createSelector(
  [selectTodoItems, selectTheme],
  (items, theme) =&gt; ({
    qolgan: items.filter((t) =&gt; !t.done).length,
    theme,
  })
);
// Пересчитывается, только если изменился items ИЛИ theme — если оба не изменились, возвращается кеш</code></pre>

<h3>🐛 Намеренная ошибка — использование одного параметризованного selector'а в нескольких компонентах</h3>
<pre><code>// Selector "найти todo по ID" — с параметром
const selectTodoById = createSelector(
  [selectTodoItems, (state, id) =&gt; id],
  (items, id) =&gt; items.find((t) =&gt; t.id === id)
);

function TodoItem({ id }) {
  // ❌ Один и тот же selectTodoById используется для КАЖДОГО экземпляра TodoItem
  const todo = useSelector((state) =&gt; selectTodoById(state, id));
  return &lt;li&gt;{todo?.text}&lt;/li&gt;;
}

function TodoList() {
  const ids = useSelector((state) =&gt; state.todos.items.map(t =&gt; t.id));
  return ids.map(id =&gt; &lt;TodoItem key={id} id={id} /&gt;); // 10 TodoItem — один selectTodoById!
}</code></pre>

<p><strong>Результат:</strong> кеш по умолчанию у <code>createSelector</code> помнит <strong>только последний</strong> вызов. Если 10 <code>TodoItem</code> вызывают один <code>selectTodoById</code> с разными <code>id</code>, каждый раз кеш считает "другой параметр" и пересчитывает — кеш первого TodoItem "вытесняется" вторым, и так по кругу. В итоге мемоизация <strong>вообще не работает</strong> — при каждом рендере всё пересчитывается заново, хотя код "выглядел правильно".</p>

<h3>Теперь объясним</h3>

<h4>1. Как работает createSelector</h4>
<p><code>createSelector([inputSelectors], resultFn)</code>: при каждом вызове сначала запускает все входные selector'ы, сравнивает их результаты с результатами предыдущего вызова через <code>===</code>. Если <strong>все</strong> совпадают — возвращает кешированный результат, вообще не вызывая <code>resultFn</code>. Если хоть один отличается — заново вызывает <code>resultFn</code> и сохраняет новый результат в кеш.</p>

<h4>2. Размер кеша по умолчанию — 1</h4>
<p><code>createSelector</code> по умолчанию помнит только <strong>один</strong> (последний) вызов. Это отлично работает, если selector используется в одном месте (например, <code>selectQolganTodos</code> используется только в одном компоненте). Но если параметризованный selector используется в нескольких экземплярах компонента — кеш постоянно "вытесняется".</p>

<h4>3. Решение — свой экземпляр selector'а для каждого компонента</h4>
<pre><code>import { useMemo } from 'react';

function TodoItem({ id }) {
  // Каждый TodoItem создаёт свой отдельный, мемоизированный selector
  const selectThisTodo = useMemo(
    () =&gt; createSelector([selectTodoItems], (items) =&gt; items.find(t =&gt; t.id === id)),
    [id]
  );
  const todo = useSelector(selectThisTodo);
  return &lt;li&gt;{todo?.text}&lt;/li&gt;;
}</code></pre>
<p>Теперь у каждого <code>TodoItem</code> свой собственный кеш, они не "вытесняют" друг друга.</p>

<h4>4. Когда нужен createSelector, а когда нет?</h4>
<table>
<tr><th>Нужен (используйте createSelector)</th><th>Не обязателен (достаточно обычного selector'а)</th></tr>
<tr><td>Вычисления с <code>.filter()/.map()/.sort()</code></td><td>Прямое чтение одного поля: <code>state.app.theme</code></td></tr>
<tr><td>Создание нового объекта из нескольких частей state</td><td>Возврат числа или строки (уже примитив)</td></tr>
<tr><td>Дорогие вычисления (сортировка большого списка)</td><td>Маленькие, дешёвые операции</td></tr>
</table>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>createSelector([inputs], resultFn)</code> — если входные данные не изменились, возвращает кешированный результат и не вызывает resultFn заново</li>
<li>✅ Проблема <code>.filter()</code> из урока 3 правильно решается через createSelector</li>
<li>✅ Размер кеша по умолчанию — 1 (только последний вызов)</li>
<li>✅ Использование параметризованного selector'а в нескольких экземплярах компонента приводит к "вытеснению" кеша (cache thrashing)</li>
<li>✅ Решение — через useMemo создавать отдельный selector для каждого экземпляра компонента</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 6: Selector'ы и производительность — createSelector
// ════════════════════════════════════════════════════════════════════

import { createSlice, createSelector, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useMemo } from 'react';

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [{ id: 1, text: 'Купить хлеб', done: false }] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
  },
});

const appSlice = createSlice({
  name: 'app',
  initialState: { theme: 'light' },
  reducers: {
    toggleTheme: (state) => { state.theme = state.theme === 'light' ? 'dark' : 'light'; },
  },
});

export const { addTodo } = todosSlice.actions;
export const { toggleTheme } = appSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, app: appSlice.reducer },
});

// ─────────────────────────────────────────────────────────────────────
// 1) Входные selector'ы + мемоизированный производный selector
// ─────────────────────────────────────────────────────────────────────

const selectTodoItems = (state) => state.todos.items;
const selectTheme = (state) => state.app.theme;

export const selectQolganTodos = createSelector(
  [selectTodoItems],
  (items) => items.filter((t) => !t.done)
);

export const selectStatistika = createSelector(
  [selectTodoItems, selectTheme],
  (items, theme) => ({
    qolgan: items.filter((t) => !t.done).length,
    theme,
  })
);

function QolganSoni() {
  const qolgan = useSelector(selectQolganTodos);
  console.log("📋 QolganSoni перерендерился");
  return <p>Невыполнено: {qolgan.length}</p>;
}

function ThemeButton() {
  const dispatch = useDispatch();
  const theme = useSelector(selectTheme);
  return <button onClick={() => dispatch(toggleTheme())}>Тема: {theme}</button>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) Намеренная ошибка — общий параметризованный selector
// ─────────────────────────────────────────────────────────────────────

const selectTodoByIdXato = createSelector(
  [selectTodoItems, (state, id) => id],
  (items, id) => items.find((t) => t.id === id)
);

function TodoItemXato({ id }) {
  // ❌ Один и тот же selectTodoByIdXato используется всеми экземплярами —
  // из-за размера кеша 1 каждый экземпляр вытесняет кеш другого.
  const todo = useSelector((state) => selectTodoByIdXato(state, id));
  return <li>{todo?.text}</li>;
}

// ✅ Правильный вариант — каждый экземпляр создаёт свой selector
function TodoItemTogri({ id }) {
  const selectThisTodo = useMemo(
    () => createSelector([selectTodoItems], (items) => items.find(t => t.id === id)),
    [id]
  );
  const todo = useSelector(selectThisTodo);
  return <li>{todo?.text}</li>;
}

function TodoList() {
  const ids = useSelector((state) => state.todos.items.map(t => t.id));
  return (
    <ul>
      {ids.map(id => <TodoItemTogri key={id} id={id} />)}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <QolganSoni />
      <ThemeButton />
      <TodoList />
    </Provider>
  );
}
"""

EX = {
    3583: {
        "title": "Зачем используется createSelector?",
        "description": "Какова основная цель createSelector([inputSelectors], resultFn)?",
        "hint": "Кеш — если входные данные не изменились, результат тоже не пересчитывается.",
        "explanation": "createSelector сравнивает результаты входных selector'ов с предыдущим вызовом. Если совпадают, возвращает кешированный результат, не вызывая resultFn заново.",
    },
    3584: {
        "title": "Какой размер кеша у createSelector по умолчанию?",
        "description": "Сколько последних вызовов запоминает selector, созданный через createSelector, по умолчанию?",
        "hint": "Вспомните, почему использование одного параметризованного selector'а в нескольких компонентах — проблема.",
        "explanation": "Размер кеша по умолчанию — 1. Поэтому поочерёдный вызов одного параметризованного selector'а с разными аргументами (например, из нескольких экземпляров компонента) постоянно \"вытесняет\" кеш, и мемоизация становится бесполезной.",
    },
    3585: {
        "title": "Правильное использование параметризованного selector'а",
        "description": "Несколько компонентов TodoItem, каждый с разным id, хотят использовать selectTodoById. Какой подход правильный для избежания вытеснения кеша?",
        "hint": "Каждый экземпляр — свой кеш. useMemo сохраняет экземпляр selector'а, пока id не изменится.",
        "explanation": "С помощью useMemo каждый экземпляр компонента создаёт свой отдельный, мемоизированный selector — тогда вызовы других экземпляров не влияют на этот кеш.",
    },
    3586: {
        "title": "Почему использование одного параметризованного selector'а ломает мемоизацию?",
        "description": "Если 10 компонентов TodoItem, каждый с разным id, вызывают один общий selectTodoById(state, id), почему это сводит на нет пользу мемоизации createSelector? Объясните своими словами.",
        "expected_answer": "createSelector по умолчанию помнит только один последний вызов (размер кеша 1). Если 10 компонентов вызывают один экземпляр selector'а поочерёдно с разными значениями id, каждый раз id отличается, поэтому кеш считается \"несовпадающим\" и пересчитывается — а следующий вызов компонента вытесняет кеш предыдущего. В результате при каждом рендере все 10 вызовов пересчитываются заново, хотя каждый из них по отдельности вызывается повторно с одним и тем же id — от мемоизации не остаётся никакой пользы.",
        "hint": "Подумайте вместе о размере кеша 1 и том, что id меняется при каждом вызове.",
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
