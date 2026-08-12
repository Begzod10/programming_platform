"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=4 (L5)."""
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

LESSON_ID = 780

TITLE_RU = "5-React frontend + Redux Toolkit (TypeScript)"

TEXT_RU = """\
<h2>Этап 5: React frontend + Redux Toolkit (TypeScript) — "тихое" расхождение между backend и frontend</h2>

<pre class="mermaid">
flowchart LR
    BACKEND["Backend: assigneeId меняется на assignee{id,name}"] --> API["Ответ API обновлён"]
    SHARED["shared/types.ts НЕ ОБНОВЛЁН"] -.->|"остаётся устаревшим"| FRONTEND
    API --> FETCH["fetchJson&lt;Issue&gt;() - assertion без проверки"]
    FETCH --> UI["IssueCard: issue.assigneeId - ТЕПЕРЬ всегда undefined"]
    UI --> SILENT["🤫 Ошибки НЕТ, но UI ВСЕГДА показывает 'Не назначено'"]
</pre>

<p>В курсе React: Redux Toolkit, TypeScript va Testlash вы уже изучили <code>configureStore</code>, <code>createSlice</code>, <code>createAsyncThunk</code> и типизированные хуки (<code>useAppSelector</code>/<code>useAppDispatch</code>). На этом уроке вы используете их с реальным backend'ом, который написали сами. На этот раз граница TypeScript проявляется в самой <strong>опасной</strong> форме — потому что на этот раз не будет НИКАКОЙ ошибки, НИКАКОГО краха. UI просто будет показывать <strong>неверные</strong> данные, молча.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — createAsyncThunk: получение данных с реального API через общий тип Issue</h4>
<pre><code>// frontend/src/api/fetchJson.ts
export async function fetchJson&lt;T&gt;(url: string): Promise&lt;T&gt; {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Ошибка запроса: ${res.status}`);
  return res.json() as Promise&lt;T&gt;;   // ❗ assertion без проверки - знакомый паттерн со 2-го урока
}

// frontend/src/features/issuesSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Issue } from '../../../shared/types';
import { fetchJson } from '../api/fetchJson';

export const fetchIssues = createAsyncThunk('issues/fetch', async () =&gt; {
  return fetchJson&lt;Issue[]&gt;('/api/issues');
});

const issuesSlice = createSlice({
  name: 'issues',
  initialState: { list: [] as Issue[], status: 'idle' as 'idle' | 'loading' | 'succeeded' | 'failed' },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchIssues.pending, (state) =&gt; { state.status = 'loading'; })
      .addCase(fetchIssues.fulfilled, (state, action) =&gt; {
        state.status = 'succeeded';
        state.list = action.payload;
      });
  },
});

export default issuesSlice.reducer;</code></pre>

<h4>БЛОК 2 — типизированные хуки (знакомы по курсу React: RTK+TS)</h4>
<pre><code>// frontend/src/store/hooks.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch: () =&gt; AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;</code></pre>

<h4>БЛОК 3 — компонент: синхронизация props через Pick&lt;Issue, ...&gt;</h4>
<pre><code>// frontend/src/components/IssueCard.tsx
// ❗ вместо РУЧНОГО дублирования props, они ПОЛУЧАЮТСЯ через Pick из Issue -
// тогда при изменении Issue, IssueCardProps тоже АВТОМАТИЧЕСКИ обновится
type IssueCardProps = Pick&lt;Issue, 'id' | 'title' | 'status' | 'assigneeId'&gt;;

function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
  return (
    &lt;div className="issue-card"&gt;
      &lt;h4&gt;{title}&lt;/h4&gt;
      &lt;span&gt;{status}&lt;/span&gt;
      &lt;p&gt;{assigneeId ? `Назначено: #${assigneeId}` : 'Не назначено'}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h3>🐛 Намеренная ошибка — backend меняет поле, shared/types.ts не обновляется</h3>
<pre><code>// Backend развивается позже (например через несколько недель): теперь
// для каждого issue нужно возвращать не ТОЛЬКО id назначенного
// пользователя, но и его имя. Разработчик backend меняет ответ API:
//
// СТАРЫЙ ответ: { ..., "assigneeId": 7 }
// НОВЫЙ ответ: { ..., "assignee": { "id": 7, "name": "Азиз" } }
//
// НО: shared/types.ts ЗДЕСЬ НЕ ОБНОВЛЯЕТСЯ - он всё ещё объявляет
// старое поле "assigneeId: number | null"!

// frontend/src/components/IssueCard.tsx - НИЧЕГО не изменено:
function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
  return (
    &lt;div className="issue-card"&gt;
      &lt;h4&gt;{title}&lt;/h4&gt;
      &lt;p&gt;{assigneeId ? `Назначено: #${assigneeId}` : 'Не назначено'}&lt;/p&gt;
    &lt;/div&gt;
  );
}
// fetchJson&lt;Issue[]&gt;() из-за assertion без проверки не даёт никакой
// ошибки. TypeScript тоже доволен - он считает, что в Issue "есть
// assigneeId". НО в реальном runtime-ответе этого поля БОЛЬШЕ НЕТ!
//
// 🤫 issue.assigneeId ВСЕГДА undefined - в консоли НИКАКОЙ ошибки нет,
//    страница НЕ ломается. Просто КАЖДЫЙ issue показывается как
//    "Не назначено" - даже если он на самом деле назначен!</code></pre>

<p><strong>Результат:</strong> это — самый <strong>тихий</strong> тип ошибки, встреченный за весь capstone. В предыдущих уроках ошибка давала <strong>видимый</strong> результат: крах, 401, или неверно сохранённые данные. Здесь же ничего "не ломается" — страница работает как обычно, в консоли нет ошибок, только <strong>данные неверны</strong>. Причина: assertion без проверки <code>as Promise&lt;T&gt;</code> в <code>fetchJson&lt;Issue[]&gt;()</code> + <strong>рассинхронизация</strong> <code>shared/types.ts</code> с изменением backend'а — та же опасность, с которой вы познакомились на 1-м уроке, теперь с <strong>реальным, видимым</strong> последствием.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему <code>Pick&lt;Issue, 'id' | 'title' | 'status' | 'assigneeId'&gt;</code> лучше ручного написания?</h4>
<p><code>Pick</code> — знакомый по курсу TypeScript Asoslari utility type — формирует тип props компонента <strong>напрямую</strong> из <code>Issue</code>. Если тип поля <code>title</code> в <code>Issue</code> изменится, <code>IssueCardProps</code> тоже <strong>автоматически</strong> обновится. Вручную написанный интерфейс же <strong>никогда</strong> не изменится, даже если источник изменился.</p>

<h4>2. Почему эта ошибка <strong>особенно</strong> опасна — в отличие от предыдущих?</h4>
<p>Ошибки на 2, 3, 4 уроках давали <strong>видимый</strong> результат: крах, неверно сохранённые данные, ошибка 401. Здесь же программа <strong>выглядит</strong> работающей без ошибок — только данные <strong>молча</strong> неверны. Такие ошибки гораздо сложнее найти, потому что нет никакого сигнала (ошибки, краха) — есть только вопрос "почему этот issue показывается как 'Не назначено', хотя он назначен?"</p>

<h4>3. <code>shared/types.ts</code> был рекомендован на 1-м уроке — почему он на этот раз не помог?</h4>
<p><code>shared/types.ts</code> помогает только тогда, когда backend и frontend <strong>оба импортируют его И ОБА ОБНОВЛЯЮТ</strong>. Если backend меняет ответ API, но <strong>забывает</strong> обновить <code>shared/types.ts</code>, этот файл превращается в <strong>лживую документацию</strong> — он соответствует не реальному runtime-ответу, а <strong>устаревшему</strong> состоянию.</p>

<h4>4. Как можно обнаружить такую ошибку?</h4>
<p>Runtime-валидация (например реальная проверка ответа API с помощью библиотеки вроде Zod) или интеграционные тесты между backend и frontend (вы увидите их на 6-м уроке) — без них такие "тихие" ошибки можно найти только <strong>вручную тестируя</strong> или по жалобе пользователя.</p>

<h4>5. Какое место занимает этот урок во всём capstone?</h4>
<p>На 1-м уроке эта опасность была лишь <strong>теоретической</strong> ("может стать опасной в будущем"). Теперь, на 5-м уроке, вы увидели её как <strong>реальную, невидимую</strong> ошибку UI — это <strong>самое серьёзное</strong> следствие главной идеи TypeScript "проверяет во время компиляции, а не во время выполнения": ошибка никогда не "кричит", она просто остаётся <strong>неверной</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>Pick&lt;T, K&gt;</code> — способ автоматически формировать тип props компонента из исходного интерфейса</li>
<li>✅ Забыть обновить <code>shared/types.ts</code> при изменении ответа backend API — самый "тихий" тип ошибки</li>
<li>✅ В таких ошибках нет краха, только молча отображаются неверные данные</li>
<li>✅ <code>shared/types.ts</code> полезен только тогда, когда ОБЕ стороны <strong>всегда</strong> его обновляют</li>
<li>✅ Runtime-валидация или интеграционные тесты — единственные инструменты, отлавливающие такие тихие ошибки</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 5: React frontend + Redux Toolkit (TypeScript)
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) fetchJson<T> - assertion без проверки (знакомый паттерн со 2-го урока)
// ─────────────────────────────────────────────────────────────────────

export async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Ошибка запроса: ${res.status}`);
  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) issuesSlice.ts - createAsyncThunk + общий тип Issue
// ─────────────────────────────────────────────────────────────────────

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Issue } from '../../../shared/types';

export const fetchIssues = createAsyncThunk('issues/fetch', async () => {
  return fetchJson<Issue[]>('/api/issues');
});

const issuesSlice = createSlice({
  name: 'issues',
  initialState: { list: [] as Issue[], status: 'idle' as 'idle' | 'loading' | 'succeeded' | 'failed' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchIssues.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchIssues.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = action.payload;
      });
  },
});

export default issuesSlice.reducer;

// ─────────────────────────────────────────────────────────────────────
// 3) store/hooks.ts - типизированные хуки
// ─────────────────────────────────────────────────────────────────────

import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// 4) IssueCard.tsx - props через Pick<Issue, ...> (в комментарии - JSX)
// ─────────────────────────────────────────────────────────────────────

// type IssueCardProps = Pick<Issue, 'id' | 'title' | 'status' | 'assigneeId'>;
//
// function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
//   return (
//     <div className="issue-card">
//       <h4>{title}</h4>
//       <span>{status}</span>
//       <p>{assigneeId ? `Назначено: #${assigneeId}` : 'Не назначено'}</p>
//     </div>
//   );
// }

// ─────────────────────────────────────────────────────────────────────
// 5) Намеренная ошибка - backend меняет поле, shared/types.ts устарел (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// Backend НОВЫЙ ответ: { ..., "assignee": { "id": 7, "name": "Азиз" } }
// shared/types.ts СТАРЫЙ: assigneeId: number | null  (не обновлён!)
// Результат: issue.assigneeId ВСЕГДА undefined - но ошибки нет, краха нет,
// UI просто всегда показывает "Не назначено".
"""

EX = {
    4504: {
        "title": "Что делает Pick<Issue, 'id' | 'title'>?",
        "description": "Почему запись type IssueCardProps = Pick<Issue, 'id' | 'title' | 'status' | 'assigneeId'> лучше вручную написанного интерфейса?",
        "hint": "Это знакомый utility type из курса TypeScript Asoslari.",
        "explanation": "Pick<Issue, ...> формирует тип props компонента напрямую из интерфейса Issue - поэтому при изменении Issue, IssueCardProps тоже автоматически обновляется, вручную написанный интерфейс же никогда не изменится.",
    },
    4505: {
        "title": "Чем ошибка этого урока отличается от предыдущих?",
        "description": "Чем 'намеренная ошибка' 5-го этапа принципиально отличается от ошибок на 2-4 уроках?",
        "hint": "Работает ли страница? Есть ли ошибка в консоли?",
        "explanation": "Эта ошибка не даёт никакого краха или ошибки в консоли - программа выглядит работающей нормально, но поскольку assigneeId всегда undefined, UI молча показывает неверные ('Не назначено') данные.",
    },
    4506: {
        "title": "Расположите процесс возникновения 'тихой' ошибки",
        "description": "Расположите процесс от изменения backend'ом assigneeId на объект assignee до отображения неверных данных в UI.",
        "hint": "",
        "explanation": "",
    },
    4507: {
        "title": "Когда shared/types.ts полезен?",
        "description": "shared/types.ts был рекомендован на 1-м уроке, но на этом уроке не помог. При каком условии он полезен? (ответьте одним словом: что должно происходить с обеих сторон?)",
        "hint": "Файл сам по себе не волшебный - он работает только когда его ... .",
        "expected_answer": "обновляют",
    },
    4508: {
        "title": "Почему такие 'тихие' ошибки особенно сложно обнаружить?",
        "description": (
            "Почему особенно сложно обнаружить ситуацию, когда "
            "assigneeId всегда undefined, а UI без единой ошибки просто "
            "показывает неверные данные? Какими способами можно "
            "отловить такие ошибки? Объясните своими словами."
        ),
        "hint": "Появляется ли что-то в консоли при такой ошибке? Работает ли страница?",
        "expected_answer": "Такие ошибки сложно найти, потому что отсутствует обычный сигнал (ошибка в консоли, крах страницы, код ошибки HTTP) - программа выглядит идеально работающей. Чтобы заметить проблему, кто-то должен знать, что конкретный issue ДЕЙСТВИТЕЛЬНО назначен, и вручную сравнить это с тем, что UI показывает 'Не назначено' - случайным тестированием это обнаруживается редко. Для отлова таких ошибок используются: (1) runtime-валидация (например реальная проверка пришедшего ответа API с помощью библиотеки вроде Zod, а не просто объявление типа), или (2) интеграционные тесты между backend и frontend (передача реального ответа API во frontend-код и проверка результата).",
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
        TASK_TITLE_RU = "IssueForge — React frontend + Redux Toolkit (TypeScript)"
        TASK_DESCRIPTION_RU = (
            "Создайте React + Redux Toolkit frontend, подключённый к "
            "backend API из 3-4 этапов: получайте список issues через "
            "createAsyncThunk, используйте типизированные хуки, и "
            "сформируйте тип props компонента IssueCard через "
            "Pick<Issue, ...> (а НЕ вручную написанный интерфейс)."
        )
        TASK_REQUIREMENTS_RU = (
            "• issuesSlice.ts — получает Issue[] из /api/issues через createAsyncThunk\n"
            "• store/hooks.ts — useAppDispatch/useAppSelector типизированы\n"
            "• IssueCard.tsx — тип props сформирован через Pick<Issue, ...>, не продублирован вручную\n"
            "• Список issues корректно отображается на странице (с состояниями loading/succeeded)\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "React, Redux Toolkit, TypeScript"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
