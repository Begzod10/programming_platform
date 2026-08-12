"""Russian translation for course 72, lesson order=4 (R1)."""
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

LESSON_ID = 586

TITLE_RU = "R1-Повторение: Todo + Корзина (RTK)"

TEXT_RU = """\
<h2>R1 — Повторение модуля 1: Todo + Корзина (полностью на RTK)</h2>

<p>Используя вместе уроки 1-4, создадим два реальных slice: <strong>Todo</strong> (action'ы с payload, безопасный selector) и <strong>Корзина</strong> (загрузка товаров через createAsyncThunk). Это — всё из прошедших 4 уроков вместе.</p>

<h3>Цель проекта</h3>
<ul>
<li><code>todosSlice</code> — добавление, удаление, отметка "выполнено" (уроки 2-3)</li>
<li><code>cartSlice</code> — загрузка товаров "с сервера" через <code>createAsyncThunk</code> (урок 4)</li>
<li>Наверху — общая статистика: число невыполненных todo, итоговая сумма в корзине</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — todosSlice</h4>
<p>Reducers: <code>addTodo(text)</code>, <code>toggleTodo(id)</code>, <code>removeTodo(id)</code> — как в уроке 3.</p>

<h4>Задание 2 — cartSlice + thunk fetchProducts</h4>
<p><code>createAsyncThunk('cart/fetchProducts', ...)</code> — <code>extraReducers</code> для pending/fulfilled/rejected. При fulfilled — сохраните в <code>state.products</code>. Отдельный reducer: <code>addToCart(productId)</code>.</p>

<h4>Задание 3 — общая статистика</h4>
<p>Через <code>useSelector</code>: число невыполненных todo (безопасный вариант из урока 3 — возвращайте <code>.length</code>, а не весь array!) и число товаров в корзине.</p>

<h4>Задание 4 — UI loading/error</h4>
<p>Пока товары загружаются — "Загрузка...", при ошибке — сообщение об ошибке (паттерн из урока 4).</p>

<h3>🐛 Намеренно сложное: два независимых slice, один store</h3>
<p>Новички часто пытаются написать оба slice как один большой. Правильный подход — <strong>отдельный slice для каждого домена</strong>, объединённый в <code>configureStore</code>:</p>
<pre><code>const store = configureStore({
  reducer: {
    todos: todosSlice.reducer,
    cart: cartSlice.reducer,
  },
});</code></pre>

<h3>Начальный код</h3>
<pre><code>const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    // Задание: addTodo, toggleTodo, removeTodo
  },
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    // Задание: addToCart
  },
  extraReducers: (builder) =&gt; {
    // Задание: fetchProducts.pending/fulfilled/rejected
  },
});</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect, useState } from 'react';

// ─── Todos ───
const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) =&gt; {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) =&gt; {
      const t = state.items.find(x =&gt; x.id === action.payload);
      if (t) t.done = !t.done;
    },
    removeTodo: (state, action) =&gt; {
      state.items = state.items.filter(x =&gt; x.id !== action.payload);
    },
  },
});

// ─── Cart ───
export const fetchProducts = createAsyncThunk('cart/fetchProducts', async () =&gt; {
  const res = await fetch('/api/products');
  if (!res.ok) throw new Error('Не удалось загрузить товары');
  return res.json();
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    addToCart: (state, action) =&gt; { state.inCart.push(action.payload); },
  },
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchProducts.pending, (state) =&gt; { state.loading = true; state.error = null; })
      .addCase(fetchProducts.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { addToCart } = cartSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, cart: cartSlice.reducer },
});

// ─── Статистика (безопасные selector'ы — возвращают только число) ───
function Statistika() {
  const qolgan = useSelector((state) =&gt;
    state.todos.items.filter(t =&gt; !t.done).length // .length — примитив, безопасно
  );
  const savatSoni = useSelector((state) =&gt; state.cart.inCart.length);
  return &lt;h2&gt;Осталось: {qolgan} | В корзине: {savatSoni}&lt;/h2&gt;;
}

// ─── UI Todo ───
function TodoApp() {
  const [matn, setMatn] = useState('');
  const items = useSelector((state) =&gt; state.todos.items);
  const dispatch = useDispatch();

  return (
    &lt;div&gt;
      &lt;input value={matn} onChange={e =&gt; setMatn(e.target.value)} /&gt;
      &lt;button onClick={() =&gt; { dispatch(addTodo(matn)); setMatn(''); }}&gt;+&lt;/button&gt;
      &lt;ul&gt;
        {items.map(t =&gt; (
          &lt;li key={t.id} style={{ textDecoration: t.done ? 'line-through' : 'none' }}&gt;
            &lt;input type="checkbox" checked={t.done} onChange={() =&gt; dispatch(toggleTodo(t.id))} /&gt;
            {t.text}
            &lt;button onClick={() =&gt; dispatch(removeTodo(t.id))}&gt;x&lt;/button&gt;
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}

// ─── UI Cart ───
function CartApp() {
  const dispatch = useDispatch();
  const { products, loading, error } = useSelector((state) =&gt; state.cart);

  useEffect(() =&gt; { dispatch(fetchProducts()); }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Загрузка...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ {error}&lt;/p&gt;;
  return (
    &lt;ul&gt;
      {products.map(p =&gt; (
        &lt;li key={p.id}&gt;
          {p.name} — {p.price} сум
          &lt;button onClick={() =&gt; dispatch(addToCart(p.id))}&gt;В корзину&lt;/button&gt;
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

function App() {
  return (
    &lt;Provider store={store}&gt;
      &lt;Statistika /&gt;
      &lt;TodoApp /&gt;
      &lt;CartApp /&gt;
    &lt;/Provider&gt;
  );
}</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Всё из уроков 1-4 вместе: createSlice, action с payload, безопасный selector, createAsyncThunk</li>
<li>✅ Каждый домен — отдельный slice, объединяемый внутри configureStore</li>
<li>✅ Такие вычисляемые значения, как статистика, безопасны, только если возвращают примитив (число)</li>
<li>✅ Каждый slice работает независимо, но всё приложение видит их через один store</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ПОВТОРЕНИЕ 1: Todo + Корзина (полностью на RTK)
// Модуль 1: createSlice + action с payload + selector + createAsyncThunk
// ════════════════════════════════════════════════════════════════════

import { createSlice, createAsyncThunk, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect, useState } from 'react';

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [] },
  reducers: {
    addTodo: (state, action) => {
      state.items.push({ id: Date.now(), text: action.payload, done: false });
    },
    toggleTodo: (state, action) => {
      const t = state.items.find(x => x.id === action.payload);
      if (t) t.done = !t.done;
    },
    removeTodo: (state, action) => {
      state.items = state.items.filter(x => x.id !== action.payload);
    },
  },
});

export const fetchProducts = createAsyncThunk('cart/fetchProducts', async () => {
  const res = await fetch('/api/products');
  if (!res.ok) throw new Error('Не удалось загрузить товары');
  return res.json();
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: { products: [], inCart: [], loading: false, error: null },
  reducers: {
    addToCart: (state, action) => { state.inCart.push(action.payload); },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export const { addToCart } = cartSlice.actions;

const store = configureStore({
  reducer: { todos: todosSlice.reducer, cart: cartSlice.reducer },
});

function Statistika() {
  const qolgan = useSelector((state) => state.todos.items.filter(t => !t.done).length);
  const savatSoni = useSelector((state) => state.cart.inCart.length);
  return <h2>Осталось: {qolgan} | В корзине: {savatSoni}</h2>;
}

function TodoApp() {
  const [matn, setMatn] = useState('');
  const items = useSelector((state) => state.todos.items);
  const dispatch = useDispatch();

  return (
    <div>
      <input value={matn} onChange={e => setMatn(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && (dispatch(addTodo(matn)), setMatn(''))} />
      <button onClick={() => { dispatch(addTodo(matn)); setMatn(''); }}>+</button>
      <ul>
        {items.map(t => (
          <li key={t.id} style={{ textDecoration: t.done ? 'line-through' : 'none' }}>
            <input type="checkbox" checked={t.done} onChange={() => dispatch(toggleTodo(t.id))} />
            {t.text}
            <button onClick={() => dispatch(removeTodo(t.id))}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CartApp() {
  const dispatch = useDispatch();
  const { products, loading, error } = useSelector((state) => state.cart);

  useEffect(() => { dispatch(fetchProducts()); }, [dispatch]);

  if (loading) return <p>⏳ Загрузка...</p>;
  if (error) return <p>❌ {error}</p>;
  return (
    <ul>
      {products.map(p => (
        <li key={p.id}>
          {p.name} — {p.price} сум
          <button onClick={() => dispatch(addToCart(p.id))}>В корзину</button>
        </li>
      ))}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <Statistika />
      <TodoApp />
      <CartApp />
    </Provider>
  );
}
"""

EX = {
    3567: {
        "title": "Правильная структура для двух доменов",
        "description": "Если есть два независимых домена, вроде Todo и Корзины, какая структура рекомендуется в RTK?",
        "hint": "Объект reducer в configureStore предназначен именно для объединения нескольких slice.",
        "explanation": "У каждого домена (todos, cart) должен быть свой отдельный slice. configureStore объединяет их в одном store через `reducer: { todos: ..., cart: ... }`.",
    },
    3568: {
        "title": "Безопасное получение числа товаров в корзине",
        "description": "Как безопасно (без лишнего перерендера) получить число товаров из массива state.cart.inCart через useSelector?",
        "hint": "Вспомните урок 3 — число является примитивом, сравнение работает правильно.",
        "explanation": "`.length` — число (примитив), поэтому сравнение === работает правильно. Возврат самого массива или его копии/отфильтрованной версии каждый раз даёт новую ссылку.",
    },
    3569: {
        "title": "Расположите в правильном порядке ход выполнения fetchProducts",
        "description": "Расположите в порядке события от монтирования компонента до появления товаров на экране.",
        "hint": "Всегда: dispatch → pending → работа с сервером → fulfilled/rejected → обновление UI.",
    },
    3570: {
        "title": "Почему не стоит объединять todosSlice и cartSlice?",
        "description": "Почему создание двух отдельных slice для Todo и Корзины лучше, чем один большой slice? Объясните своими словами.",
        "expected_answer": "Каждый slice изолирует состояние и логику своего домена. Если todos и cart находятся в одном slice, код становится запутанным, имена action'ов могут конфликтовать, и растёт риск того, что изменение в одном домене повлияет на код, не имеющий к нему отношения. Отдельные slice облегчают чтение кода, тестирование и параллельную работу в команде; configureStore просто объединяет их через объект reducer.",
        "hint": "Подумайте с точки зрения удобства чтения кода, тестирования и командной работы.",
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
