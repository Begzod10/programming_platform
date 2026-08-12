"""Russian translation for course 72, lesson order=3 (L4)."""
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

LESSON_ID = 584

TITLE_RU = "4-Асинхронное состояние: createAsyncThunk"

TEXT_RU = """\
<h2>Асинхронное состояние: createAsyncThunk — загрузка/ошибка/успех</h2>

<pre class="mermaid">
flowchart LR
    D["dispatch(fetchUsers())"] --> P["pending: loading=true"]
    P --> F["fulfilled: данные пришли"]
    P --> R["rejected: ошибка"]
    F --> UI1["Показать список"]
    R --> UI2["Показать сообщение об ошибке"]
</pre>

<p>В курсе "React Asoslari" вы вручную управляли <code>loading</code>/<code>error</code>/<code>data</code> через <code>useState</code> внутри <code>useEffect</code> с <code>fetch</code>. В этом уроке сделаем то же самое с помощью <code>createAsyncThunk</code> из Redux Toolkit — теперь loading/error/data находятся в одном месте, доступном из любого компонента.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — напоминание: старый способ (useEffect + useState)</h4>
<pre><code>// Знакомый способ из React Asoslari:
function FoydalanuvchilarEski() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() =&gt; {
    fetch('/api/users')
      .then(res =&gt; res.json())
      .then(setData)
      .catch(err =&gt; setError(err.message))
      .finally(() =&gt; setLoading(false));
  }, []);

  // Проблема: это состояние только в ЭТОМ компоненте. Если другому
  // компоненту тоже нужен список пользователей — придётся снова делать fetch.
}</code></pre>

<h4>БЛОК 2 — с createAsyncThunk</h4>
<pre><code>import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

// Первый аргумент — префикс action type, второй — асинхронная функция
export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async () =&gt; {
    const res = await fetch('/api/users');
    if (!res.ok) throw new Error('Ошибка сервера');
    return res.json(); // это станет action.payload у fulfilled
  }
);</code></pre>

<p><code>createAsyncThunk</code> из одной функции автоматически создаёт <strong>3 action type</strong>: <code>users/fetchUsers/pending</code>, <code>users/fetchUsers/fulfilled</code>, <code>users/fetchUsers/rejected</code>.</p>

<h4>БЛОК 3 — обработка в slice (extraReducers)</h4>
<pre><code>const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {}, // обычных action'ов нет — всё через thunk
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUsers.pending, (state) =&gt; {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.items = action.payload; // то, что вернул thunk
      })
      .addCase(fetchUsers.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});</code></pre>

<pre><code>function FoydalanuvchilarYangi() {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) =&gt; state.users);

  useEffect(() =&gt; {
    dispatch(fetchUsers());
  }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Загрузка...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ Ошибка: {error}&lt;/p&gt;;
  return &lt;ul&gt;{items.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<p>Теперь <strong>любой другой компонент</strong> может через <code>useSelector(state =&gt; state.users)</code> получить те же данные, то же состояние загрузки — без повторного fetch.</p>

<h3>🐛 Намеренная ошибка — забыть состояние rejected</h3>
<pre><code>const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUsers.pending, (state) =&gt; { state.loading = true; })
      .addCase(fetchUsers.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.items = action.payload;
      });
      // ❌ .addCase(fetchUsers.rejected, ...) НЕТ!
  },
});</code></pre>

<p><strong>Результат:</strong> если сервер вернёт ошибку (например, 500), action <code>rejected</code> будет отправлен (dispatch), но его никто не обработает. <code>state.loading</code> — <strong>никогда не станет <code>false</code></strong>, потому что только <code>fulfilled</code> делает его <code>false</code>. Пользователь бесконечно видит на экране "⏳ Загрузка..." — никакой ошибки не видно, никакой ошибки в консоли тоже нет. Это — <strong>самый опасный</strong> тип бага: тихий, медленный, причина которого не очевидна.</p>

<h3>Теперь объясним</h3>

<h4>1. createAsyncThunk — 3 action, 1 функция</h4>
<table>
<tr><th>Action</th><th>Когда</th><th>action.payload / action.error</th></tr>
<tr><td><code>pending</code></td><td>Сразу при вызове функции</td><td>нет</td></tr>
<tr><td><code>fulfilled</code></td><td>Если Promise успешно завершился</td><td><code>payload</code> = возвращённое значение</td></tr>
<tr><td><code>rejected</code></td><td>Если Promise отклонён или выброшено исключение</td><td><code>error.message</code> = текст ошибки</td></tr>
</table>

<h4>2. extraReducers — почему отдельно?</h4>
<p>Объект <code>reducers</code> — только для action'ов, созданных <strong>вами самими</strong> (например, <code>increment</code>). <code>extraReducers</code> — для реагирования на action'ы, созданные <strong>в другом месте</strong> (например, createAsyncThunk). <code>builder.addCase(actionType, handler)</code> означает "если придёт этот action, запусти эту функцию".</p>

<h4>3. rejectWithValue — своё сообщение об ошибке</h4>
<pre><code>export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (_, { rejectWithValue }) =&gt; {
    const res = await fetch('/api/users');
    if (!res.ok) {
      return rejectWithValue(`Сервер вернул ${res.status}`); // окажется в action.payload
    }
    return res.json();
  }
);

// в extraReducers:
.addCase(fetchUsers.rejected, (state, action) =&gt; {
  state.error = action.payload ?? action.error.message; // rejectWithValue имеет приоритет
})</code></pre>

<h4>4. Почему это лучше, чем useEffect+useState?</h4>
<ul>
<li>Данные <strong>глобальны</strong> — любой компонент использует их без повторного fetch</li>
<li>Состояние loading/error в одном месте — без дублирования</li>
<li>В Redux DevTools видно каждый этап fetch (pending/fulfilled/rejected)</li>
</ul>

<h4>5. В следующем уроке...</h4>
<p>Этот паттерн (thunk + pending/fulfilled/rejected + loading/error state) настолько распространён, что Redux Toolkit даёт отдельный инструмент, полностью его автоматизирующий — <strong>RTK Query</strong>. Увидим это в 5-м уроке.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>createAsyncThunk</code> из одной асинхронной функции автоматически создаёт action'ы pending/fulfilled/rejected</li>
<li>✅ <code>extraReducers</code> + <code>builder.addCase</code> — для реагирования на внешние (как thunk) action'ы</li>
<li>✅ <code>action.payload</code> у <code>fulfilled</code> — значение, которое вернула функция thunk'а</li>
<li>✅ <code>rejectWithValue</code> — для передачи своего, более точного сообщения об ошибке</li>
<li>✅ Необработка <code>rejected</code> приводит к тому, что состояние loading навсегда остаётся "true" (тихий баг)</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 4: Асинхронное состояние — createAsyncThunk
// ════════════════════════════════════════════════════════════════════

import { createAsyncThunk, createSlice, configureStore } from '@reduxjs/toolkit';
import { useSelector, useDispatch, Provider } from 'react-redux';
import { useEffect } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Thunk — 3 action автоматически: pending / fulfilled / rejected
// ─────────────────────────────────────────────────────────────────────

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (_, { rejectWithValue }) => {
    const res = await fetch('/api/users');
    if (!res.ok) {
      return rejectWithValue(`Сервер вернул ${res.status}`);
    }
    return res.json();
  }
);

// ─────────────────────────────────────────────────────────────────────
// 2) Slice — обработка 3 состояний thunk'а через extraReducers
// ─────────────────────────────────────────────────────────────────────

const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload ?? action.error.message;
      });
  },
});

const store = configureStore({
  reducer: { users: usersSlice.reducer },
});

// ─────────────────────────────────────────────────────────────────────
// 3) Компонент — три состояния: loading / error / data
// ─────────────────────────────────────────────────────────────────────

function FoydalanuvchilarRoyxati() {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  if (loading) return <p>⏳ Загрузка...</p>;
  if (error) return <p>❌ Ошибка: {error}</p>;
  return (
    <ul>
      {items.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}

function App() {
  return (
    <Provider store={store}>
      <FoydalanuvchilarRoyxati />
    </Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — забыть состояние rejected
// ─────────────────────────────────────────────────────────────────────

/*
const usersSliceXato = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => { state.loading = true; })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      });
      // ❌ Нет addCase для rejected — если сервер вернёт ошибку,
      // state.loading НИКОГДА не станет false. UI бесконечно показывает
      // "Загрузка...", без какой-либо видимой ошибки.
  },
});
*/
"""

EX = {
    3559: {
        "title": "Сколько action'ов создаёт createAsyncThunk?",
        "description": "При вызове createAsyncThunk('users/fetchUsers', asyncFn), сколько action type создаётся автоматически и каких?",
        "hint": "Каждая асинхронная операция может находиться в одном из трёх состояний: ожидание, успех, ошибка.",
        "explanation": "createAsyncThunk всегда создаёт 3 action type: `{prefix}/pending`, `{prefix}/fulfilled`, `{prefix}/rejected` — соответствующие трём возможным состояниям Promise.",
    },
    3560: {
        "title": "Где мы обрабатываем action'ы thunk'а?",
        "description": "Где внутри slice обрабатываются action'ы pending/fulfilled/rejected, созданные createAsyncThunk?",
        "hint": "reducers — только для action'ов, которые сам этот slice создал.",
        "explanation": "reducers — только для action'ов, созданных самим этим slice. createAsyncThunk создаёт action'ы в другом месте (внутри thunk'а), поэтому на них реагируют через extraReducers + builder.addCase.",
    },
    3561: {
        "title": "Расположите в правильном порядке жизненный цикл thunk'а",
        "description": "Расположите в правильном порядке события от вызова dispatch(fetchUsers()) до получения ответа API.",
        "hint": "pending отправляется сразу при начале функции, ДО получения результата.",
    },
    3562: {
        "title": "Почему опасно забыть состояние rejected?",
        "description": "Если в extraReducers обработаны только pending и fulfilled, а для rejected addCase не написан, что увидит пользователь при ошибке сервера, и почему это особенно опасный тип бага? Объясните своими словами.",
        "expected_answer": "Если addCase для rejected не написан, при ошибке сервера action rejected будет отправлен, но никто его не обработает, и состояние не изменится. Поле loading становится false только через fulfilled, поэтому оно навсегда останется true. В результате пользователь видит на экране постоянную надпись \"Загрузка...\" — без какой-либо ошибки в консоли или заметной неполадки. Это особенно опасно, потому что баг тихий (silent) — его трудно заметить без логов или специального теста.",
        "hint": "Когда loading становится false, и что будет, если fulfilled никогда не придёт?",
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
