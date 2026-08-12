"""Russian translation for course 72, lesson order=10 (R2)."""
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

LESSON_ID = 598

TITLE_RU = "R2-Мини-проект TS + RTK (повторение)"

TEXT_RU = """\
<h2>R2 — Повторение модуля 2: Типизированное приложение "Библиотека"</h2>

<p>Используя вместе уроки 7-9, создадим небольшое приложение <strong>Библиотека</strong>: generic-компонент <code>List&lt;T&gt;</code> (урок 8), типизированные props/state (урок 7), и полностью типизированный Redux Toolkit — RootState, AppDispatch, типизированный thunk (урок 9).</p>

<h3>Цель проекта</h3>
<ul>
<li>Интерфейс <code>Book</code>: <code>id, title, author, available: boolean</code></li>
<li><code>booksSlice</code> — загрузка книг через <code>createAsyncThunk&lt;Book[], void&gt;</code></li>
<li>Generic-компонент <code>List&lt;T extends {'{'} id: number {'}'}&gt;</code> — переиспользуется для показа книг</li>
<li><code>useAppSelector</code>/<code>useAppDispatch</code> — везде, без сырых версий</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — интерфейс Book и booksSlice</h4>
<p><code>initialState: { items: Book[]; loading: boolean; error: string | null }</code>. Thunk <code>fetchBooks</code> — <code>createAsyncThunk&lt;Book[], void&gt;</code>.</p>

<h4>Задание 2 — RootState/AppDispatch + типизированные хуки</h4>
<p>Как в уроке 9 — выведены из store, не написаны вручную.</p>

<h4>Задание 3 — generic-компонент List&lt;T&gt;</h4>
<p>Переиспользуйте <code>ListWithId&lt;T extends {'{'} id: number {'}'}&gt;</code> из урока 8 — показывайте список книг через него.</p>

<h4>Задание 4 — отметка доступности</h4>
<p>Рядом с каждой книгой: <code>available ? "✅ Доступна" : "❌ Занята"</code>.</p>

<h3>🐛 Намеренно сложное: объединение generic-компонента с типизированным Redux state</h3>
<p>Чаще всего путаются в следующем: передача <code>Book[]</code>, возвращённого <code>useAppSelector((state) =&gt; state.books.items)</code>, напрямую в generic <code>List&lt;T&gt;</code> — хотя это две независимые системы (тип Redux и generic-тип компонента), TypeScript автоматически их согласует, потому что <code>Book</code> уже удовлетворяет ограничению <code>{'{'} id: number {'}'}</code>.</p>

<h3>Начальный код</h3>
<pre><code>interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

// Задание: thunk fetchBooks, booksSlice, RootState/AppDispatch, типизированные хуки
</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code>import { createSlice, createAsyncThunk, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';
import { useEffect } from 'react';

interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

const initialState: BooksState = { items: [], loading: false, error: null };

export const fetchBooks = createAsyncThunk&lt;Book[], void&gt;(
  'books/fetchBooks',
  async () =&gt; {
    const res = await fetch('/api/books');
    if (!res.ok) throw new Error('Не удалось загрузить книги');
    return res.json() as Promise&lt;Book[]&gt;;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchBooks.pending, (state) =&gt; { state.loading = true; state.error = null; })
      .addCase(fetchBooks.fulfilled, (state, action: PayloadAction&lt;Book[]&gt;) =&gt; {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.error.message ?? "Неизвестная ошибка";
      });
  },
});

const store = configureStore({ reducer: { books: booksSlice.reducer } });

export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;

// Generic List — паттерн из урока 8
interface ListProps&lt;T&gt; {
  items: T[];
  renderItem: (item: T) =&gt; React.ReactNode;
}

function List&lt;T extends { id: number }&gt;({ items, renderItem }: ListProps&lt;T&gt;) {
  return &lt;ul&gt;{items.map((item) =&gt; &lt;li key={item.id}&gt;{renderItem(item)}&lt;/li&gt;)}&lt;/ul&gt;;
}

function KutubxonaRoyxati() {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) =&gt; state.books);

  useEffect(() =&gt; { dispatch(fetchBooks()); }, [dispatch]);

  if (loading) return &lt;p&gt;⏳ Загрузка...&lt;/p&gt;;
  if (error) return &lt;p&gt;❌ {error}&lt;/p&gt;;

  return (
    &lt;List&lt;Book&gt; items={items} renderItem={(book) =&gt; (
      &lt;span&gt;{book.title} — {book.author} {book.available ? '✅ Доступна' : '❌ Занята'}&lt;/span&gt;
    )} /&gt;
  );
}

function App() {
  return (
    &lt;Provider store={store}&gt;
      &lt;KutubxonaRoyxati /&gt;
    &lt;/Provider&gt;
  );
}</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Уроки 7-9 вместе: типизированные props/state, generic-компоненты, полностью типизированный Redux Toolkit</li>
<li>✅ Типизированные данные из Redux (Book[]) напрямую подходят generic-компоненту, если удовлетворяют ограничению</li>
<li>✅ RootState/AppDispatch/типизированные хуки создаются один раз и переиспользуются по всему проекту</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ПОВТОРЕНИЕ 2: Типизированное приложение "Библиотека"
// Модуль 2: типизированные props/state + generics + типизированный Redux Toolkit
// ════════════════════════════════════════════════════════════════════

import { createSlice, createAsyncThunk, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';
import { useEffect } from 'react';

interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

const initialState: BooksState = { items: [], loading: false, error: null };

export const fetchBooks = createAsyncThunk<Book[], void>(
  'books/fetchBooks',
  async () => {
    const res = await fetch('/api/books');
    if (!res.ok) throw new Error('Не удалось загрузить книги');
    return res.json() as Promise<Book[]>;
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchBooks.fulfilled, (state, action: PayloadAction<Book[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Неизвестная ошибка";
      });
  },
});

const store = configureStore({ reducer: { books: booksSlice.reducer } });

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// Generic List — паттерн из урока 8, переиспользован
// ─────────────────────────────────────────────────────────────────────

interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T extends { id: number }>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map((item) => <li key={item.id}>{renderItem(item)}</li>)}</ul>;
}

function KutubxonaRoyxati() {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) => state.books);

  useEffect(() => { dispatch(fetchBooks()); }, [dispatch]);

  if (loading) return <p>⏳ Загрузка...</p>;
  if (error) return <p>❌ {error}</p>;

  return (
    <List<Book> items={items} renderItem={(book) => (
      <span>{book.title} — {book.author} {book.available ? '✅ Доступна' : '❌ Занята'}</span>
    )} />
  );
}

function App() {
  return (
    <Provider store={store}>
      <KutubxonaRoyxati />
    </Provider>
  );
}
"""

EX = {
    3615: {
        "title": "Подходит ли Book[] для generic List<T>?",
        "description": "Можно ли передать Book[] (с полями id, title, author, available) в компонент List<T extends { id: number }>?",
        "hint": "Ограничение говорит только \"id: number обязателен\" — дополнительные поля не проблема.",
        "explanation": "T extends { id: number } требует, чтобы T имел хотя бы поле id: number. Book удовлетворяет этому условию (и имеет дополнительные поля), поэтому подходит напрямую.",
    },
    3616: {
        "title": "Generic'и thunk'а fetchBooks",
        "description": "Что означает второй generic (void) в createAsyncThunk<Book[], void>('books/fetchBooks', ...)?",
        "hint": "Второй generic — ThunkArg, то есть тип аргумента внутри dispatch(fetchBooks(???)).",
        "explanation": "createAsyncThunk<Returned, ThunkArg> — второй generic это тип аргумента thunk'а. void означает, что dispatch(fetchBooks()) вызывается без какого-либо аргумента.",
    },
    3617: {
        "title": "Откуда должен импортироваться useAppSelector?",
        "description": "В приложении Библиотека, в каждом компоненте, какой хук должен использоваться для доступа к state?",
        "hint": "Вспомните урок 9 — сырой useSelector теряет типобезопасность.",
        "explanation": "Всегда должен использоваться useAppSelector, созданный в проекте и типизированный через RootState — сырой useSelector оставляет параметр state без проверки.",
    },
    3618: {
        "title": "Почему generic-компонент и типизированный Redux хорошо работают вместе?",
        "description": (
            "Когда generic-компонент List<T> используется вместе с полностью "
            "типизированным Redux Toolkit (RootState, типизированный thunk), "
            "какую практическую пользу даёт это объединение? Объясните "
            "своими словами."
        ),
        "expected_answer": "Поскольку данные, приходящие из store Redux Toolkit (например, Book[]), полностью типизированы, при передаче их в generic-компонент TypeScript автоматически проверяет, что функция renderItem внутри компонента использует правильные поля (title, author, available). Если кто-то напишет неверное имя поля (например, book.nomi), это сразу проявится как ошибка компиляции. Эти два слоя — глобальное состояние и переиспользуемые UI-компоненты — согласуются друг с другом, и весь поток данных от начала до конца остаётся типобезопасным.",
        "hint": "Подумайте о том, что весь путь данных от store до компонента охватывается типобезопасностью.",
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
