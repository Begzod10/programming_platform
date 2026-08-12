"""Russian translation for course 72, lesson order=1 (L2)."""
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

LESSON_ID = 580

TITLE_RU = "2-configureStore + createSlice"

TEXT_RU = """\
<h2>configureStore + createSlice — запускаем Redux Toolkit</h2>

<pre class="mermaid">
flowchart LR
    S["createSlice"] -->|создаёт автоматически| AC["action creators"]
    S -->|создаёт автоматически| R["reducer"]
    R -->|внутри configureStore| ST["store"]
    ST -->|через Provider| APP["всё приложение"]
</pre>

<p>В прошлом уроке мы дали обещание: <code>useSelector</code> подписывается только на нужный кусок. Теперь построим это на самом деле — решим проблему <code>ThemeLabel</code>/<code>CounterLabel</code> из прошлого урока с помощью Redux Toolkit.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка и первый slice</h4>
<pre><code>// Терминал:
npm install @reduxjs/toolkit react-redux</code></pre>

<pre><code>// src/features/appSlice.js
import { createSlice } from '@reduxjs/toolkit';

const appSlice = createSlice({
  name: 'app',
  initialState: {
    theme: 'light',
    count: 0,
  },
  reducers: {
    toggleTheme: (state) =&gt; {
      state.theme = state.theme === 'light' ? 'dark' : 'light'; // выглядит как мутация
    },
    increment: (state) =&gt; {
      state.count += 1;
    },
  },
});

export const { toggleTheme, increment } = appSlice.actions;
export default appSlice.reducer;</code></pre>

<p>Обратите внимание: <code>state.count += 1</code> — выглядит как настоящая мутация! Но не переживайте — причину объясним ниже (Immer).</p>

<h4>БЛОК 2 — создание store и подключение Provider</h4>
<pre><code>// src/store.js
import { configureStore } from '@reduxjs/toolkit';
import appReducer from './features/appSlice';

export const store = configureStore({
  reducer: {
    app: appReducer, // state.app.theme, state.app.count
  },
});</code></pre>

<pre><code>// src/main.jsx
import { Provider } from 'react-redux';
import { store } from './store';

ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;Provider store={store}&gt;
    &lt;App /&gt;
  &lt;/Provider&gt;
);</code></pre>

<h4>БЛОК 3 — решение проблемы из прошлого урока</h4>
<pre><code>import { useSelector, useDispatch } from 'react-redux';
import { toggleTheme, increment } from './features/appSlice';

function ThemeLabel() {
  const theme = useSelector((state) =&gt; state.app.theme); // подписка ТОЛЬКО на theme
  console.log("🎨 ThemeLabel перерендерился");
  return &lt;p&gt;Тема: {theme}&lt;/p&gt;;
}

function CounterLabel() {
  const count = useSelector((state) =&gt; state.app.count); // подписка ТОЛЬКО на count
  console.log("🔢 CounterLabel перерендерился");
  return &lt;p&gt;Число: {count}&lt;/p&gt;;
}

function App() {
  const dispatch = useDispatch();
  return (
    &lt;&gt;
      &lt;ThemeLabel /&gt;
      &lt;CounterLabel /&gt;
      &lt;button onClick={() =&gt; dispatch(increment())}&gt;+1 (только число)&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>Теперь нажмите <strong>+1</strong> и посмотрите в консоль: появится только <code>🔢 CounterLabel перерендерился</code>. <code>ThemeLabel</code> — <strong>вообще не перерендерится</strong>, потому что <code>state.app.theme</code> не изменился. Это и есть решение проблемы из прошлого урока.</p>

<h3>🐛 Намеренная ошибка — забыть Provider</h3>
<pre><code>// main.jsx — нет Provider!
ReactDOM.createRoot(document.getElementById('root')).render(
  &lt;App /&gt; {/* ❌ не обёрнуто в store */}
);</code></pre>

<p>Если внутри <code>App</code> вызывается <code>useSelector</code>:</p>
<pre><code>Error: could not find react-redux context value; please ensure the component is wrapped in a &lt;Provider&gt;</code></pre>

<p><strong>Причина:</strong> <code>useSelector</code>/<code>useDispatch</code> из <code>react-redux</code> используют внутренний Context, чтобы найти store. Без <code>&lt;Provider store={store}&gt;</code> этот внутренний Context пуст, и возникает ошибка.</p>

<h3>Теперь объясним</h3>

<h4>1. Подождите — Redux тоже использует Context?! Мы же критиковали его в прошлом уроке!</h4>
<p>Да, <code>react-redux</code> внутри использует Context — но совершенно с другой целью. Через Context передаётся только <strong>сам объект store</strong> (единственная, никогда не меняющаяся ссылка). Перерендерится компонент или нет — решает не Context, а <strong>собственный механизм подписки</strong> <code>useSelector</code>: он напрямую подписывается на store и заставляет компонент перерендериться, только если изменилась именно запрошенная им часть. Context здесь — просто "труба" для передачи store, а не решение производительности.</p>

<h4>2. Анатомия configureStore</h4>
<pre><code>configureStore({
  reducer: {
    app: appReducer,     // state.app.*
    cart: cartReducer,   // state.cart.* (в следующих уроках)
  },
});</code></pre>
<p>Каждый ключ в объекте <code>reducer</code> становится разделом внутри <code>state</code>. Кроме того, <code>configureStore</code> автоматически: включает Redux DevTools и добавляет полезные middleware (например, проверку immutability в dev-режиме). В классическом Redux всё это настраивалось вручную.</p>

<h4>3. Анатомия createSlice</h4>
<pre><code>createSlice({
  name: 'app',           // префикс action type: "app/increment"
  initialState: {...},   // начальное состояние
  reducers: {             // каждый = один action + одна логика reducer'а
    increment: (state) =&gt; { state.count += 1 },
  },
});</code></pre>
<p><code>createSlice</code> автоматически создаёт:</p>
<ul>
<li><strong>action creator</strong>: <code>appSlice.actions.increment()</code> → <code>{ type: "app/increment" }</code></li>
<li><strong>функцию reducer</strong>: <code>appSlice.reducer</code> — передаётся в <code>configureStore</code></li>
</ul>

<h4>4. Immer — почему "мутация" безопасна?</h4>
<p>Внутри <code>createSlice</code> Redux Toolkit автоматически использует библиотеку <strong>Immer</strong>. Когда вы пишете <code>state.count += 1</code>, на самом деле:</p>
<ul>
<li>Immer даёт вам "черновик" (draft) версии</li>
<li>Когда вы "мутируете" draft, Immer отслеживает это</li>
<li>После завершения функции Immer создаёт <strong>новое, immutable</strong> состояние на основе изменений в draft</li>
</ul>
<p>То есть код выглядит как мутация, но результат — всегда новый объект. Одно правило: <strong>либо возвращайте новое состояние, либо мутируйте draft — не смешивайте оба подхода.</strong></p>
<pre><code>// ✅ Мутация draft (Immer управляет этим)
increment: (state) =&gt; { state.count += 1; }

// ✅ Возврат нового объекта (тоже правильно)
increment: (state) =&gt; ({ ...state, count: state.count + 1 })

// ❌ Смешивание обоих подходов — неправильное поведение
increment: (state) =&gt; { state.count += 1; return { ...state }; }</code></pre>

<h4>5. Provider — подключение store ко всему приложению</h4>
<p><code>&lt;Provider store={store}&gt;</code> — на самом верху дерева, один раз. Любой компонент внутри (независимо от глубины) может получить доступ к store через <code>useSelector</code>/<code>useDispatch</code> — передавать через пропсы не нужно.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>createSlice</code> автоматически создаёт action creator и reducer из name, initialState, reducers</li>
<li>✅ <code>configureStore</code> объединяет reducer'ы slice'ов, автоматически настраивает DevTools и middleware</li>
<li>✅ Immer позволяет безопасно писать "мутации" внутри reducer, поскольку работает с draft и возвращает новое immutable состояние</li>
<li>✅ <code>&lt;Provider store={store}&gt;</code> — всё приложение получает доступ к store, но это лишь "труба"; перерендер решает собственная подписка useSelector</li>
<li>✅ Без Provider <code>useSelector</code>/<code>useDispatch</code> выдают ошибку "could not find react-redux context value"</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 2: configureStore + createSlice
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) src/features/appSlice.js
// ─────────────────────────────────────────────────────────────────────

import { createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';

const appSlice = createSlice({
  name: 'app',
  initialState: {
    theme: 'light',
    count: 0,
  },
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    increment: (state) => {
      state.count += 1;
    },
  },
});

export const { toggleTheme, increment } = appSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// 2) src/store.js
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});

// ─────────────────────────────────────────────────────────────────────
// 3) Решение проблемы прошлого урока — подписка только на нужный кусок
// ─────────────────────────────────────────────────────────────────────

function ThemeLabel() {
  const theme = useSelector((state) => state.app.theme);
  console.log("🎨 ThemeLabel перерендерился");
  return <p>Тема: {theme}</p>;
}

function CounterLabel() {
  const count = useSelector((state) => state.app.count);
  console.log("🔢 CounterLabel перерендерился");
  return <p>Число: {count}</p>;
}

function AppIchki() {
  const dispatch = useDispatch();
  return (
    <>
      <ThemeLabel />
      <CounterLabel />
      <button onClick={() => dispatch(increment())}>+1 (только число)</button>
      <button onClick={() => dispatch(toggleTheme())}>Сменить тему</button>
    </>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppIchki />
    </Provider>
  );
}

// Смотрите в консоль: при нажатии "+1" перерендерится только CounterLabel.
// ThemeLabel останется полностью спокоен. Это решение проблемы из 1-го урока.

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — забыть Provider
// ─────────────────────────────────────────────────────────────────────

/*
function AppXato() {
  return <AppIchki />; // ❌ нет Provider
}
// Когда внутри AppIchki вызывается useSelector:
// Error: could not find react-redux context value;
// please ensure the component is wrapped in a <Provider>
*/

// ─────────────────────────────────────────────────────────────────────
// 5) Immer — пишем как мутацию, на деле immutable
// ─────────────────────────────────────────────────────────────────────

const demoSlice = createSlice({
  name: 'demo',
  initialState: { count: 0 },
  reducers: {
    // ✅ Мутация draft — Immer управляет этим, безопасно
    incrementOk: (state) => { state.count += 1; },

    // ✅ Возврат нового объекта — тоже правильно
    incrementAlsoOk: (state) => ({ ...state, count: state.count + 1 }),

    // ❌ Смешивание обоих подходов — неправильное поведение
    // incrementXato: (state) => { state.count += 1; return { ...state }; }
  },
});
"""

EX = {
    3543: {
        "title": "Что createSlice создаёт автоматически?",
        "description": "Что автоматически создаётся при вызове createSlice({ name, initialState, reducers })?",
        "hint": "appSlice.actions и appSlice.reducer — оба являются результатом createSlice.",
        "explanation": "createSlice автоматически создаёт для каждой функции в объекте reducers соответствующий action creator (appSlice.actions.increment) И одну функцию reducer для всего slice (appSlice.reducer).",
    },
    3544: {
        "title": "Какой Context используется внутри Provider?",
        "description": "В прошлом уроке мы видели проблему перерендера Context. react-redux тоже внутри использует Context. В чём разница?",
        "hint": "Когда меняется сам объект store? Практически никогда.",
        "explanation": "react-redux через Context передаёт только одну, стабильную ссылку на store. Перерендер решает не объект store, а собственная подписка (subscription) useSelector — поэтому проблема из 1-го урока здесь отсутствует.",
    },
    3545: {
        "title": "Расположите в правильном порядке этапы настройки RTK",
        "description": "Расположите в правильном порядке этапы настройки Redux Toolkit в новом проекте.",
        "hint": "Сначала библиотека, потом определение состояния, потом store, потом подключение, потом использование.",
    },
    3546: {
        "title": "Почему state.count += 1 внутри reducer безопасно?",
        "description": "Написание `state.count += 1` внутри функции reducer в createSlice выглядит как нарушение правила Redux/React \"никогда не мутируйте состояние\". Почему это на самом деле безопасно? Объясните своими словами.",
        "expected_answer": "Внутри createSlice Redux Toolkit использует библиотеку Immer. `state` внутри reducer на самом деле не настоящее состояние, а \"черновик\" (draft), предоставленный Immer. Когда вы \"мутируете\" draft, Immer отслеживает это и после завершения reducer автоматически создаёт новый, immutable объект состояния. Поэтому код выглядит как мутация, но результат всегда — новый объект, а исходное состояние не изменяется.",
        "hint": "Подумайте про Immer, draft и что происходит после завершения reducer.",
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
