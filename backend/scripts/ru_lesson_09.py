"""Russian translation for course 72, lesson order=9 (L9)."""
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

LESSON_ID = 596

TITLE_RU = "9-Redux Toolkit + TypeScript вместе"

TEXT_RU = """\
<h2>Redux Toolkit + TypeScript вместе — RootState, AppDispatch, типизированные хуки</h2>

<pre class="mermaid">
flowchart LR
    ST["store"] -->|ReturnType| RS["RootState"]
    ST -->|typeof| AD["AppDispatch"]
    RS --> UAS["useAppSelector"]
    AD --> UAD["useAppDispatch"]
</pre>

<p>В уроках 2-3 мы писали <code>useSelector</code>/<code>useDispatch</code> — но в TypeScript-проекте, если использовать обычный <code>useSelector</code>, параметр <code>state</code> становится <strong>автоматически <code>any</code></strong>. То есть при написании <code>state.app.theme</code> TS вообще не проверяет ничего, и даже если вы ошибётесь, промолчит. В этом уроке исправим это.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — вывод типов RootState и AppDispatch</h4>
<pre><code>// src/store.ts
import { configureStore } from '@reduxjs/toolkit';
import appReducer from './features/appSlice';

export const store = configureStore({
  reducer: { app: appReducer },
});

// ❗ Важно: эти типы НЕ пишутся вручную — они ВЫВОДЯТСЯ из store
export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;</code></pre>

<p>Почему не вручную? Если завтра вы добавите новый slice, <code>RootState</code> обновится автоматически — а вручную написанный interface устареет и создаст ложное чувство безопасности.</p>

<h4>БЛОК 2 — создание типизированных хуков</h4>
<pre><code>// src/hooks.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;</code></pre>

<pre><code>// Теперь в компонентах ВСЕГДА используйте эти вместо сырых useSelector/useDispatch:
function ThemeLabel() {
  const theme = useAppSelector((state) =&gt; state.app.theme); // ✅ полное автодополнение + проверка
  const dispatch = useAppDispatch(); // ✅ dispatch принимает только настоящие action'ы
  return &lt;p&gt;{theme}&lt;/p&gt;;
}</code></pre>

<h4>БЛОК 3 — типизация состояния slice и payload thunk'а</h4>
<pre><code>interface AppState {
  theme: 'light' | 'dark';
  count: number;
}

const initialState: AppState = { theme: 'light', count: 0 };

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    // тип action выводится автоматически через PayloadAction&lt;T&gt;
    setTheme: (state, action: PayloadAction&lt;'light' | 'dark'&gt;) =&gt; {
      state.theme = action.payload;
    },
  },
});

// Для thunk'а тоже два generic-параметра: <Возвращаемое, Аргумент>
interface Foydalanuvchi { id: number; ism: string; }

export const fetchUser = createAsyncThunk&lt;Foydalanuvchi, number&gt;(
  'user/fetchUser',
  async (userId) =&gt; { // userId — TS знает: number
    const res = await fetch(`/api/users/${userId}`);
    return res.json() as Promise&lt;Foydalanuvchi&gt;; // Тип возврата — Foydalanuvchi
  }
);</code></pre>

<h3>🐛 Намеренная ошибка — оставить "старый" useSelector в некоторых компонентах</h3>
<pre><code>import { useSelector } from 'react-redux'; // ❌ НЕТИПИЗИРОВАННЫЙ, прямо из react-redux

function EskiKomponent() {
  const theme = useSelector((state) =&gt; state.app.theme);
  // ❌ Parameter 'state' implicitly has an 'any' type.
  // Или (если noImplicitAny выключен) — state.app.theme
  // без всякой проверки, даже если ошибётесь (например state.apr.theme), промолчит.
}</code></pre>

<p><strong>Причина:</strong> даже если в проекте создан <code>useAppSelector</code>, если хотя бы один компонент по-прежнему импортирует <code>useSelector</code> напрямую из <code>react-redux</code> — именно в этом месте вся типобезопасность теряется. Эту ошибку можно предотвратить ESLint-правилом (<code>no-restricted-imports</code>), но самый надёжный путь — в команде придерживаться правила "всегда <code>useAppSelector</code>/<code>useAppDispatch</code>".</p>

<h3>Теперь объясним</h3>

<h4>1. Почему RootState нужно получать через ReturnType</h4>
<p><code>ReturnType&lt;typeof store.getState&gt;</code> означает "что бы функция getState ни возвращала, то и есть RootState". Это <strong>автоматически</strong> следует из реальной структуры store. Вручную написанный interface не обновится при добавлении нового slice и создаст ложную уверенность.</p>

<h4>2. Что делает TypedUseSelectorHook?</h4>
<p>Это готовый generic-тип из <code>react-redux</code>, который "запирает" <code>useSelector</code> на конкретный <code>RootState</code>. В результате каждый раз вручную писать <code>&lt;RootState&gt;</code> не нужно — сам <code>useAppSelector</code> уже это знает.</p>

<h4>3. PayloadAction&lt;T&gt; — типизация action.payload</h4>
<pre><code>import { PayloadAction } from '@reduxjs/toolkit';

reducers: {
  setTheme: (state, action: PayloadAction&lt;'light' | 'dark'&gt;) =&gt; {
    state.theme = action.payload; // TS знает: только 'light' или 'dark'
  },
}</code></pre>

<h4>4. createAsyncThunk&lt;Возвращаемое, Аргумент&gt;</h4>
<p>Два generic-параметра: первый — что вернёт thunk при успехе (тип <code>payload</code> у <code>fulfilled</code>), второй — какой аргумент ожидается при вызове thunk'а.</p>

<h4>5. Командное правило — никогда не использовать сырой useSelector/useDispatch</h4>
<p>Создайте <code>useAppSelector</code>/<code>useAppDispatch</code> с самого начала проекта и используйте их <strong>везде</strong>. Оставить где-то сырую версию — значит создать дыру в типобезопасности для всего проекта.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>RootState</code>/<code>AppDispatch</code> выводятся из store через <code>ReturnType</code>/<code>typeof</code>, а не пишутся вручную</li>
<li>✅ <code>useAppSelector</code>/<code>useAppDispatch</code> — используются ВСЕГДА по всему проекту, а не сырые useSelector/useDispatch</li>
<li>✅ <code>PayloadAction&lt;T&gt;</code> типизирует action.payload внутри reducer'а</li>
<li>✅ <code>createAsyncThunk&lt;Возвращаемое, Аргумент&gt;</code> — полностью типизирован двумя generic-параметрами</li>
<li>✅ Оставить сырой useSelector в одном месте ослабляет типобезопасность всего проекта</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 9: Redux Toolkit + TypeScript вместе
// ════════════════════════════════════════════════════════════════════

import { configureStore, createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// 1) Состояние slice и типизация через PayloadAction
// ─────────────────────────────────────────────────────────────────────

interface AppState {
  theme: 'light' | 'dark';
  count: number;
}

const initialState: AppState = { theme: 'light', count: 0 };

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    increment: (state) => { state.count += 1; },
  },
});

export const { setTheme, increment } = appSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// 2) Типизированный thunk — <Возвращаемое, Аргумент>
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi { id: number; ism: string; }

export const fetchUser = createAsyncThunk<Foydalanuvchi, number>(
  'user/fetchUser',
  async (userId) => {
    const res = await fetch(`/api/users/${userId}`);
    return res.json() as Promise<Foydalanuvchi>;
  }
);

// ─────────────────────────────────────────────────────────────────────
// 3) Store + RootState/AppDispatch — НЕ вручную, выведены из store
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: { app: appSlice.reducer },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ─────────────────────────────────────────────────────────────────────
// 4) Типизированные хуки — используются ВСЕГДА по всему проекту
// ─────────────────────────────────────────────────────────────────────

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// 5) Компонент — полностью типизирован
// ─────────────────────────────────────────────────────────────────────

function ThemeLabel() {
  const theme = useAppSelector((state) => state.app.theme); // полное автодополнение
  const dispatch = useAppDispatch();
  return (
    <div>
      <p>Тема: {theme}</p>
      <button onClick={() => dispatch(setTheme(theme === 'light' ? 'dark' : 'light'))}>
        Сменить
      </button>
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ThemeLabel />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 6) Намеренная ошибка — использование сырого useSelector
// ─────────────────────────────────────────────────────────────────────

/*
import { useSelector } from 'react-redux'; // ❌ нетипизированный, напрямую

function EskiKomponent() {
  const theme = useSelector((state) => state.app.theme);
  // ❌ Parameter 'state' implicitly has an 'any' type.
  // Если написать что-то вроде state.apr.theme — промолчит, без проверки.
}
*/
"""

EX = {
    3607: {
        "title": "Как правильно получать RootState?",
        "description": "Какой правильный, рекомендуемый способ создания типа RootState?",
        "hint": "Вручную написанный тип устареет при изменении store — автоматический вывод лучше.",
        "explanation": "RootState всегда выводится через `ReturnType<typeof store.getState>`, тогда при добавлении нового slice в store RootState обновляется автоматически и никогда не устаревает.",
    },
    3608: {
        "title": "Почему useAppSelector нужно использовать всегда по всему проекту?",
        "description": "Если в одном компоненте используется обычный useSelector из react-redux (вместо useAppSelector), что произойдёт?",
        "hint": "useAppSelector — это useSelector, \"запертый\" на RootState. Сырая версия так не заперта.",
        "explanation": "Сырой useSelector ничего не знает о RootState — state автоматически становится any (или непроверяемым). В этом одном компоненте вся типобезопасность теряется.",
    },
    3609: {
        "title": "В каком порядке идут generic'и у createAsyncThunk?",
        "description": "При написании createAsyncThunk<Foydalanuvchi, number>(...), в каком порядке идут значения generic'ов?",
        "hint": "createAsyncThunk<Returned, ThunkArg> — сначала результат, потом аргумент.",
        "explanation": "createAsyncThunk<Returned, ThunkArg> — первый generic это тип значения, которое thunk вернёт при успехе (payload у fulfilled), второй — тип ожидаемого аргумента при вызове thunk'а.",
    },
    3610: {
        "title": "Почему сырой useSelector в одном месте влияет на весь проект?",
        "description": (
            "Даже если в проекте созданы useAppSelector/useAppDispatch, если "
            "один старый компонент по-прежнему импортирует useSelector "
            "напрямую из react-redux, почему это не \"маленькая\", а "
            "проблема, влияющая на типобезопасность всего проекта? "
            "Объясните своими словами."
        ),
        "expected_answer": "Типобезопасность TypeScript работает только там, где она применена. Если один компонент использует сырой useSelector, внутри этого компонента параметр state не проверяется, и если разработчик ошибётся (например, напишет state.apr.theme вместо state.app.theme), TypeScript никак на это не укажет. Это создаёт \"дыру\" в кодовой базе: хотя весь остальной проект типизирован, именно в этом месте может возникнуть runtime-ошибка, и без code review или автоматического lint-правила это легко остаётся незамеченным.",
        "hint": "Типобезопасность работает только там, где применена — остальной типизированный проект этого не компенсирует.",
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
