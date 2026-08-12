"""Russian translation for course 72, lesson order=2 (L3)."""
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

LESSON_ID = 582

TITLE_RU = "3-useSelector / useDispatch и подключение компонентов"

TEXT_RU = """\
<h2>useSelector / useDispatch подробнее — action'ы с payload и ловушки selector'ов</h2>

<pre class="mermaid">
flowchart LR
    UI["dispatch(addTodo({text}))"] --> R["reducer: читает action.payload"]
    R --> ST["store обновляется"]
    ST -->|только подходящий selector| SEL["useSelector пересчитывается"]
</pre>

<p>В 1-2 уроках мы видели <code>increment()</code> и <code>toggleTheme()</code> — им ничего не передавалось. Большинство реальных action'ов приходят с <strong>payload</strong> (данными): "добавь todo с этим текстом", "удали элемент с этим id". В этом уроке разберём это, а также распространённую ловушку в selector'ах.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — action'ы с payload</h4>
<pre><code>const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) =&gt; {
      // action.payload — данные, переданные при dispatch
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) =&gt; {
      const todo = state.items.find(t =&gt; t.id === action.payload);
      if (todo) todo.done = !todo.done;
    },
    removeTodo: (state, action) =&gt; {
      state.items = state.items.filter(t =&gt; t.id !== action.payload);
    },
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;</code></pre>

<h4>БЛОК 2 — использование в компоненте</h4>
<pre><code>function TodoForm() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const qoshish = () =&gt; {
    if (!matn.trim()) return;
    dispatch(addTodo(matn)); // addTodo('Купить хлеб') → { type: 'todos/addTodo', payload: 'Купить хлеб' }
    setMatn('');
  };

  return (
    &lt;div&gt;
      &lt;input value={matn} onChange={e =&gt; setMatn(e.target.value)} /&gt;
      &lt;button onClick={qoshish}&gt;Добавить&lt;/button&gt;
    &lt;/div&gt;
  );
}

function TodoItem({ todo }) {
  const dispatch = useDispatch();
  return (
    &lt;li style={{ textDecoration: todo.done ? 'line-through' : 'none' }}&gt;
      &lt;input type="checkbox" checked={todo.done}
        onChange={() =&gt; dispatch(toggleTodo(todo.id))} /&gt;
      {todo.text}
      &lt;button onClick={() =&gt; dispatch(removeTodo(todo.id))}&gt;x&lt;/button&gt;
    &lt;/li&gt;
  );
}</code></pre>

<h4>БЛОК 3 — получение вычисленного (derived) значения в selector'е</h4>
<pre><code>function QolganSoni() {
  // Внутри selector'а .filter() — КАЖДЫЙ РАЗ возвращает НОВЫЙ array!
  const qolgan = useSelector((state) =&gt;
    state.todos.items.filter((t) =&gt; !t.done)
  );
  console.log("📋 QolganSoni перерендерился");
  return &lt;p&gt;Невыполнено: {qolgan.length}&lt;/p&gt;;
}</code></pre>

<p>Это работает, но — если вы отправите (dispatch) любой другой action, не связанный с <code>todos</code> (например, сменю тему), перерендерится ли этот компонент? Давайте проверим.</p>

<h3>🐛 Намеренная ошибка — selector каждый раз возвращает новую ссылку</h3>
<pre><code>// Смените theme (не связано с todos!) и посмотрите в консоль:
dispatch(toggleTheme());

// Результат в консоли:
// 📋 QolganSoni перерендерился   ← почему?! todos же не менялись!</code></pre>

<p><strong>Причина:</strong> <code>useSelector</code> — при каждом dispatch action'а <strong>заново вызывает</strong> функцию selector'а и сравнивает результат с предыдущим через <code>===</code>. <code>.filter()</code> — при каждом вызове создаёт <strong>новый объект array</strong>, даже если элементы внутри одинаковые. <code>новыйArray === старыйArray</code> — <strong>всегда false</strong>. Поэтому React считает, что этот компонент "изменился", и перерендеривает его — даже если <code>todos</code> на самом деле не изменились.</p>

<p>В маленьком приложении это незаметно, но в большом каждый action заставляет пересчитываться каждый такой selector. (В 6-м уроке решим это правильно с помощью <code>createSelector</code> — пока достаточно уметь распознавать проблему.)</p>

<h3>Теперь объясним</h3>

<h4>1. action.payload — соглашение, а не обязательство</h4>
<p>В reducer, созданном через <code>createSlice</code>, вторым аргументом приходит объект <code>action</code>: <code>{ type: 'todos/addTodo', payload: ... }</code>. <code>action.payload</code> — стандартное соглашение Redux Toolkit (можно было назвать как угодно, но RTK всегда называет его <code>payload</code>).</p>

<h4>2. Если нужно несколько аргументов</h4>
<pre><code>// payload должен быть одним значением, но это значение может быть объектом:
dispatch(addTodo({ text: matn, priority: 'high' }));

// в reducer:
addTodo: (state, action) =&gt; {
  state.items.push({
    id: Date.now(),
    text: action.payload.text,
    priority: action.payload.priority,
    done: false,
  });
}</code></pre>

<h4>3. useSelector — вызывается ЗАНОВО при каждом dispatch</h4>
<p>Это принцип работы <code>useSelector</code>: когда в store приходит любой action, <strong>каждый</strong> selector в <strong>каждом</strong> компоненте пересчитывается заново (это дешёвая, быстрая операция). Только если результат отличается по <code>===</code>, компонент перерендеривается. Проблема не в повторном вызове selector'а — а в том, что он <strong>возвращает новую ссылку</strong>.</p>

<h4>4. Какие selector'ы опасны?</h4>
<table>
<tr><th>Безопасно (возвращает примитив)</th><th>Опасно (каждый раз новая ссылка)</th></tr>
<tr><td><code>state =&gt; state.todos.items.length</code></td><td><code>state =&gt; state.todos.items.filter(...)</code></td></tr>
<tr><td><code>state =&gt; state.app.theme</code></td><td><code>state =&gt; ({ theme: state.app.theme })</code> (новый объект!)</td></tr>
<tr><td><code>state =&gt; state.todos.items[0]?.id</code></td><td><code>state =&gt; state.todos.items.map(...)</code></td></tr>
</table>

<h4>5. Временное решение (полное решение — в 6-м уроке)</h4>
<p>Пока: если selector использует <code>.filter()/.map()/.sort()</code> или возвращает новый объект — будьте внимательны. В маленьких приложениях это не проблема, но <strong>научиться распознавать</strong> это — первый шаг отладки производительности.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Action'ы передают данные через <code>action.payload</code> — <code>addTodo(matn)</code> → <code>{ type, payload: matn }</code></li>
<li>✅ Если нужно несколько значений — payload передаётся объектом</li>
<li>✅ <code>useSelector</code> вызывается заново при КАЖДОМ dispatch, но компонент перерендеривается только если результат отличается по <code>===</code></li>
<li>✅ <code>.filter()/.map()</code> внутри selector'а — каждый раз возвращает новый array/объект → лишний перерендер</li>
<li>✅ Распознавание проблемы: если selector трансформирует данные (filter/map/новый объект) — будьте внимательны</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 3: useSelector / useDispatch подробнее
// ════════════════════════════════════════════════════════════════════

import { createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useState } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Action'ы с payload
// ─────────────────────────────────────────────────────────────────────

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) todo.done = !todo.done;
    },
    removeTodo: (state, action) => {
      state.items = state.items.filter(t => t.id !== action.payload);
    },
  },
});

const themeSlice = createSlice({
  name: 'theme',
  initialState: { value: 'light' },
  reducers: {
    toggleTheme: (state) => { state.value = state.value === 'light' ? 'dark' : 'light'; },
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { toggleTheme } = themeSlice.actions;

const store = configureStore({
  reducer: {
    todos: todosSlice.reducer,
    theme: themeSlice.reducer,
  },
});

// ─────────────────────────────────────────────────────────────────────
// 2) Компоненты — с dispatch
// ─────────────────────────────────────────────────────────────────────

function TodoForm() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const qoshish = () => {
    if (!matn.trim()) return;
    dispatch(addTodo(matn));
    setMatn('');
  };

  return (
    <div>
      <input value={matn} onChange={e => setMatn(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && qoshish()} />
      <button onClick={qoshish}>Добавить</button>
    </div>
  );
}

function TodoItem({ todo }) {
  const dispatch = useDispatch();
  return (
    <li style={{ textDecoration: todo.done ? 'line-through' : 'none' }}>
      <input type="checkbox" checked={todo.done}
        onChange={() => dispatch(toggleTodo(todo.id))} />
      {todo.text}
      <button onClick={() => dispatch(removeTodo(todo.id))}>x</button>
    </li>
  );
}

function TodoList() {
  const items = useSelector((state) => state.todos.items); // безопасно — reducer сам возвращает новый array только при изменении
  return (
    <ul>
      {items.map(t => <TodoItem key={t.id} todo={t} />)}
    </ul>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка — selector каждый раз возвращает новую ссылку
// ─────────────────────────────────────────────────────────────────────

function QolganSoniXato() {
  // ❌ .filter() каждый раз новый array — перерендер даже при смене theme
  const qolgan = useSelector((state) =>
    state.todos.items.filter((t) => !t.done)
  );
  console.log("📋 QolganSoniXato перерендерился");
  return <p>Невыполнено: {qolgan.length}</p>;
}

// Для доказательства: нажмите ThemeButton и посмотрите в консоль —
// QolganSoniXato тоже перерендерится, хотя todos не менялись.

function ThemeButton() {
  const dispatch = useDispatch();
  const theme = useSelector((state) => state.theme.value); // безопасно — примитив
  return (
    <button onClick={() => dispatch(toggleTheme())}>
      Тема: {theme} (нажмите и смотрите в консоль)
    </button>
  );
}

// ✅ Более безопасный временный вариант — сохраняем только число, а не результат filter
function QolganSoniYaxshiroq() {
  const qolganSoni = useSelector((state) =>
    state.todos.items.filter((t) => !t.done).length // число — примитив, сравнение работает правильно
  );
  console.log("📋 QolganSoniYaxshiroq перерендерился (только при изменении числа)");
  return <p>Невыполнено: {qolganSoni}</p>;
}

function App() {
  return (
    <Provider store={store}>
      <TodoForm />
      <TodoList />
      <QolganSoniXato />
      <QolganSoniYaxshiroq />
      <ThemeButton />
    </Provider>
  );
}
"""

EX = {
    3551: {
        "title": "Что такое action.payload?",
        "description": "Когда вызывается dispatch(addTodo('Купить хлеб')), как будет выглядеть объект action внутри reducer'а?",
        "hint": "createSlice автоматически создаёт action creator: addTodo(x) → { type, payload: x }.",
        "explanation": "Action creator, созданный createSlice, автоматически помещает переданный аргумент в поле `payload`, а `type` формирует из имени slice + имени reducer'а.",
    },
    3552: {
        "title": "Когда selector заставляет компонент перерендериться?",
        "description": "В каком случае useSelector заставляет компонент перерендериться?",
        "hint": "Selector вызывается заново при КАЖДОМ dispatch, но перерендер — отдельное решение.",
        "explanation": "useSelector при каждом action заново вызывает selector, но компонент перерендеривается только если новый результат отличается от старого по ===.",
    },
    3553: {
        "title": "Какой selector опасен (даёт лишний перерендер)?",
        "description": "Какой из следующих selector'ов может при каждом вызове возвращать новую ссылку, вызывая лишний перерендер?",
        "hint": ".filter() создаёт новый array при каждом вызове, даже если содержимое одинаковое.",
        "explanation": ".filter() каждый раз возвращает НОВЫЙ объект array, даже если результат логически одинаков. Новая ссылка !== старая ссылка, поэтому компонент перерендеривается при каждом dispatch.",
    },
    3554: {
        "title": "Почему selector с .filter() вызывает проблему?",
        "description": "Почему useSelector((state) => state.todos.items.filter(t => !t.done)) заставляет компонент перерендериться даже при dispatch action'а, \"не связанного с todos\"? Объясните своими словами.",
        "expected_answer": "useSelector после каждого отправленного (dispatch) action заново вызывает все selector'ы, даже если action не связан с этой частью state. Метод .filter() при каждом вызове создаёт новый объект array — даже если элементы внутри такие же, как раньше, этот новый array не равен старому по сравнению ===. Именно через это сравнение === useSelector определяет необходимость перерендера, поэтому каждый раз считает состояние \"изменившимся\" и перерендеривает компонент.",
        "hint": "Подумайте, как useSelector определяет необходимость перерендера (сравнение ===) и что возвращает .filter().",
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
