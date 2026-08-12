"""Russian translation for course 72, lesson order=5 (L5)."""
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

LESSON_ID = 589

TITLE_RU = "5-Основы RTK Query"

TEXT_RU = """\
<h2>Основы RTK Query — избавляемся от бойлерплейта createAsyncThunk</h2>

<pre class="mermaid">
flowchart LR
    API["createApi({ endpoints })"] -->|автоматически| H["useGetProductsQuery()"]
    H --> D["data, isLoading, error — всё готово"]
    M["useAddProductMutation()"] -->|invalidatesTags| H
</pre>

<p>В уроке 4 с <code>createAsyncThunk</code> для одного запроса нужно было вручную писать: thunk, slice, 3 case в extraReducers, состояние loading/error. <strong>RTK Query</strong> сводит всё это к нескольким строкам и вдобавок даёт кеширование, автоматическую перезагрузку, дедупликацию.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание API slice</h4>
<pre><code>// src/features/apiSlice.js
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) =&gt; ({
    getProducts: builder.query({
      query: () =&gt; '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) =&gt; ({
        url: '/products',
        method: 'POST',
        body: newProduct,
      }),
      invalidatesTags: ['Product'],
    }),
  }),
});

// Соглашение об именовании автоматическое: getProducts → useGetProductsQuery
//                                            addProduct → useAddProductMutation
export const { useGetProductsQuery, useAddProductMutation } = api;</code></pre>

<h4>БЛОК 2 — подключение к store</h4>
<pre><code>import { configureStore } from '@reduxjs/toolkit';
import { api } from './features/apiSlice';

const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer, // "api": {...}
  },
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware().concat(api.middleware), // через это работает кеширование/перезагрузка
});</code></pre>

<h4>БЛОК 3 — использование в компоненте (без createAsyncThunk!)</h4>
<pre><code>function MahsulotlarRoyxati() {
  // Одна строка — data, isLoading, error, всё готово!
  const { data, isLoading, error } = useGetProductsQuery();

  if (isLoading) return &lt;p&gt;⏳ Загрузка...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ Произошла ошибка&lt;/p&gt;;
  return &lt;ul&gt;{data.map(p =&gt; &lt;li key={p.id}&gt;{p.name}&lt;/li&gt;)}&lt;/ul&gt;;
}

function YangiMahsulotForma() {
  const [addProduct, { isLoading }] = useAddProductMutation();

  const yuborish = async () =&gt; {
    await addProduct({ name: 'Новый товар', price: 10000 });
    // MahsulotlarRoyxati АВТОМАТИЧЕСКИ перезагрузится — никакой
    // ручной dispatch(fetchProducts()) не нужен!
  };

  return &lt;button onClick={yuborish} disabled={isLoading}&gt;Добавить&lt;/button&gt;;
}</code></pre>

<p>В уроке 4 для этого вручную нужно было: thunk, 3 case в extraReducers, а затем после каждой мутации заново вызывать <code>dispatch(fetchProducts())</code>. В RTK Query это происходит <strong>автоматически</strong> через <code>invalidatesTags</code>/<code>providesTags</code>.</p>

<h3>🐛 Намеренная ошибка — забыть invalidatesTags</h3>
<pre><code>addProduct: builder.mutation({
  query: (newProduct) =&gt; ({ url: '/products', method: 'POST', body: newProduct }),
  // ❌ invalidatesTags: ['Product'] НЕТ!
}),</code></pre>

<p><strong>Результат:</strong> мутация <code>addProduct</code> выполняется <strong>успешно</strong> — сервер сохраняет новый товар, ошибок нет. Но компонент <code>MahsulotlarRoyxati</code> <strong>не обновляется</strong> — новый товар не появляется в списке, пока не обновить страницу вручную (F5). Причина: RTK Query ещё не пометил кешированный результат <code>getProducts</code> как "устаревший", потому что никто ему об этом не сказал. Это — успешный, но запутывающий пользователя баг: "я же добавил, почему не видно?"</p>

<h3>Теперь объясним</h3>

<h4>1. Анатомия createApi</h4>
<table>
<tr><th>Поле</th><th>Назначение</th></tr>
<tr><td><code>reducerPath</code></td><td>под каким ключом хранится в store ("api")</td></tr>
<tr><td><code>baseQuery</code></td><td>общая настройка для всех запросов (baseUrl, заголовки)</td></tr>
<tr><td><code>tagTypes</code></td><td>имена "тегов" для группировки кеша ("Product")</td></tr>
<tr><td><code>endpoints</code></td><td>каждый запрос — <code>builder.query</code> (GET) или <code>builder.mutation</code> (POST/PUT/DELETE)</td></tr>
</table>

<h4>2. Соглашение об именовании — автоматические хуки</h4>
<p>Для каждого имени внутри <code>endpoints</code> RTK Query автоматически создаёт хук: <code>getProducts</code> → <code>useGetProductsQuery</code>, <code>addProduct</code> → <code>useAddProductMutation</code>. Вручную экспортировать не обязательно — можно обращаться и через <code>api.endpoints.getProducts</code>, но хуки удобнее.</p>

<h4>3. providesTags / invalidatesTags — секрет автоматического обновления</h4>
<ul>
<li><code>getProducts</code> — <code>providesTags: ['Product']</code> — "я предоставляю данные типа Product"</li>
<li><code>addProduct</code> — <code>invalidatesTags: ['Product']</code> — "я делаю кеш типа Product устаревшим"</li>
</ul>
<p>После успешной мутации RTK Query для каждого тега в <code>invalidatesTags</code> <strong>автоматически перезапрашивает</strong> все запросы, объявившие этот тег в <code>providesTags</code>. Это заменяет ручной вызов <code>dispatch(fetch...())</code>.</p>

<h4>4. Зачем всё ещё нужен createAsyncThunk?</h4>
<p>RTK Query идеален для CRUD (GET/POST/PUT/DELETE) с сервером. Но не всякая асинхронная операция — это запрос к серверу: например, чтение <code>localStorage</code>, сложные вычисления, или последовательный вызов нескольких API с условной логикой. В таких случаях <code>createAsyncThunk</code> по-прежнему правильный инструмент.</p>

<h4>5. isLoading против isFetching</h4>
<p><code>useGetProductsQuery()</code> возвращает: <code>data</code>, <code>isLoading</code> (при первой загрузке), <code>isFetching</code> (при любой перезагрузке, даже если есть кешированные данные), <code>error</code>, <code>refetch</code> (ручной повторный запрос).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>createApi</code> автоматически создаёт хуки useGetXQuery/useAddXMutation из endpoints</li>
<li>✅ В store обязательно нужно добавить <code>[api.reducerPath]: api.reducer</code> и <code>api.middleware</code></li>
<li>✅ <code>providesTags</code>/<code>invalidatesTags</code> автоматически перезагружают соответствующие запросы после мутации</li>
<li>✅ Забыть invalidatesTags — мутация успешна, но UI не обновляется (тихий баг)</li>
<li>✅ RTK Query — для CRUD с сервером; createAsyncThunk — для не-серверной или сложной асинхронной логики</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 5: Основы RTK Query
// ════════════════════════════════════════════════════════════════════

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// 1) API slice — хуки создаются автоматически из endpoints
// ─────────────────────────────────────────────────────────────────────

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) => ({
    getProducts: builder.query({
      query: () => '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) => ({
        url: '/products',
        method: 'POST',
        body: newProduct,
      }),
      invalidatesTags: ['Product'], // без этого — 🐛 смотрите ниже
    }),
  }),
});

export const { useGetProductsQuery, useAddProductMutation } = api;

// ─────────────────────────────────────────────────────────────────────
// 2) Store — reducerPath + middleware
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

// ─────────────────────────────────────────────────────────────────────
// 3) Компоненты — без createAsyncThunk
// ─────────────────────────────────────────────────────────────────────

function MahsulotlarRoyxati() {
  const { data, isLoading, error } = useGetProductsQuery();

  if (isLoading) return <p>⏳ Загрузка...</p>;
  if (error) return <p>❌ Произошла ошибка</p>;
  return (
    <ul>
      {data.map(p => <li key={p.id}>{p.name} — {p.price} сум</li>)}
    </ul>
  );
}

function YangiMahsulotForma() {
  const [addProduct, { isLoading }] = useAddProductMutation();

  const yuborish = async () => {
    await addProduct({ name: 'Новый товар', price: 10000 });
    // MahsulotlarRoyxati автоматически перезагрузится благодаря invalidatesTags
  };

  return <button onClick={yuborish} disabled={isLoading}>Добавить</button>;
}

function App() {
  return (
    <Provider store={store}>
      <MahsulotlarRoyxati />
      <YangiMahsulotForma />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — забыть invalidatesTags
// ─────────────────────────────────────────────────────────────────────

/*
const apiXato = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Product'],
  endpoints: (builder) => ({
    getProducts: builder.query({
      query: () => '/products',
      providesTags: ['Product'],
    }),
    addProduct: builder.mutation({
      query: (newProduct) => ({ url: '/products', method: 'POST', body: newProduct }),
      // ❌ Нет invalidatesTags — мутация успешна, но кеш
      // MahsulotlarRoyxati не помечается устаревшим.
      // Пользователь не увидит новый товар, пока не нажмёт F5.
    }),
  }),
});
*/
"""

EX = {
    3579: {
        "title": "Какой хук создаёт createApi?",
        "description": "Если в createApi внутри endpoints есть builder.query с именем getProducts, какой хук создаётся автоматически?",
        "hint": "Соглашение: use + ИмяEndpoint (с большой буквы) + Query/Mutation.",
        "explanation": "Соглашение об именовании RTK Query: для query endpoint — `use{EndpointName}Query`, для mutation — `use{EndpointName}Mutation`. getProducts → useGetProductsQuery.",
    },
    3580: {
        "title": "Что нужно для автоматической перезагрузки списка после мутации?",
        "description": "Что нужно настроить, чтобы список getProducts автоматически перезапрашивался после мутации addProduct?",
        "hint": "Нужна настройка с двух сторон: кто предоставляет (provides), кто делает устаревшим (invalidates).",
        "explanation": "providesTags и invalidatesTags должны совпадать по имени тега. Только тогда RTK Query знает, какие запросы перезапросить после мутации.",
    },
    3581: {
        "title": "Порядок настройки RTK Query",
        "description": "Расположите в правильном порядке этапы настройки RTK Query в новом проекте.",
        "hint": "Сначала определение API, затем подключение к store, затем использование в компоненте.",
    },
    3582: {
        "title": "Почему забыть invalidatesTags — тихий баг?",
        "description": "Если в мутации addProduct не написан invalidatesTags, почему пользователь не увидит новый товар, несмотря на успешный запрос к серверу? Объясните своими словами.",
        "expected_answer": "RTK Query кеширует результат getProducts и перезапрашивает его только тогда, когда он помечен как \"устаревший\" через invalidatesTags. Даже если addProduct выполнится успешно, если для неё не указан invalidatesTags: ['Product'], RTK Query не считает кеш getProducts устаревшим и не перезапрашивает его. Хотя данные на сервере уже обновлены, пользователь на экране продолжает видеть старый, кешированный список — пока не обновит страницу вручную.",
        "hint": "Когда кеш считается \"устаревшим\", и кто должен об этом сообщить?",
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
