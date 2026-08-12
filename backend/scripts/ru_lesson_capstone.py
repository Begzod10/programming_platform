"""Russian translation for course 72, lesson order=13 (CAPSTONE).

Handled specially: the project section's `requirements`/`techStack` keys
aren't in translation_service._TRANSLATABLE_KEYS, so the generic
collect-and-set mechanism in translate_lesson() would silently leave them
in Uzbek. This script builds the translated sections_json tree directly
instead, so every field the student actually sees is translated.
"""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from write_ru_translations import _write  # noqa: E402

LESSON_ID = 604

TITLE_RU = "12-CAPSTONE: Типизированная корзина покупок (RTK + TS + тесты)"

TASK_TITLE_RU = "🚀 CAPSTONE: Типизированная корзина покупок (Redux Toolkit + TypeScript + тесты)"

TASK_DESCRIPTION_RU = (
    "Финальный проект курса: полностью типизированное (.tsx) приложение "
    "товаров и корзины покупок. Загрузите товары через RTK Query, управляйте "
    "корзиной через RTK slice, типизируйте всё с помощью TypeScript и "
    "напишите минимум 5 тестов на Vitest + React Testing Library."
)

TASK_REQUIREMENTS_RU = (
    "• React + TypeScript (.tsx) — все компоненты типизированы\n"
    "• RTK Query — загрузка списка товаров (useGetProductsQuery)\n"
    "• Slice Redux Toolkit — состояние корзины (добавление, удаление, изменение количества)\n"
    "• RootState/AppDispatch + useAppSelector/useAppDispatch — везде\n"
    "• Использован минимум 1 generic или utility type (Partial/Pick/Omit)\n"
    "• Состояния loading/error — через isLoading/error из RTK Query\n"
    "• Минимум 5 тестов (Vitest + React Testing Library):\n"
    "  - Тест, проверяющий рендер компонента\n"
    "  - Тест нажатия кнопки \"добавить в корзину\" через userEvent\n"
    "  - Тест правильного расчёта итоговой суммы корзины\n"
    "  - Тест асинхронной загрузки с мокированным fetch (findBy)\n"
    "  - Тест ошибочной ситуации (сервер вернул 500)\n"
    "• README — инструкция по запуску проекта и тестов"
)

TASK_TECHNOLOGIES_RU = "React, TypeScript, Redux Toolkit, RTK Query, Vitest, React Testing Library"

TEXT_RU = """\
<h2>🚀 CAPSTONE: Типизированная корзина покупок</h2>

<p>Это — финальный проект курса. Всё, что вы изучили в уроках 1-11 — Redux Toolkit (slice, thunk, RTK Query, selector'ы), TypeScript (props, generics, типизированный Redux), и тестирование (RTL, userEvent, мокирование) — объединяется в одном реальном проекте.</p>

<h3>Структура проекта</h3>
<pre class="mermaid">
flowchart LR
    RTKQ["RTK Query — товары"] --> UI["Список товаров"]
    UI -->|добавить в корзину| CS["cartSlice"]
    CS --> SUM["Страница корзины — итоговая сумма"]
    TESTS["Vitest + RTL"] -.проверяет.-> UI
    TESTS -.проверяет.-> CS
</pre>

<h3>Что нужно сделать</h3>
<ol>
<li><strong>Товары</strong> — <code>createApi</code> с <code>useGetProductsQuery()</code>, состояния loading/error (урок 5)</li>
<li><strong>Корзина</strong> — отдельный <code>cartSlice</code>: <code>addToCart</code>, <code>removeFromCart</code>, <code>updateQuantity</code> (уроки 2-3)</li>
<li><strong>Типизация</strong> — все компоненты, состояние, thunk'и полностью типизированы (уроки 7-9)</li>
<li><strong>Тесты</strong> — минимум 5, render/userEvent/async/мокирование (уроки 10-11)</li>
</ol>

<h3>Скелет для начала</h3>
<pre><code>interface Product {
  id: number;
  name: string;
  price: number;
}

interface CartItem {
  productId: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

// Задание: apiSlice (RTK Query) — endpoint getProducts
// Задание: cartSlice — addToCart, removeFromCart, updateQuantity
// Задание: RootState/AppDispatch + useAppSelector/useAppDispatch
// Задание: компонент SavatSahifasi — расчёт и показ итоговой суммы
// Задание: минимум 5 тестов (Product.test.tsx, Cart.test.tsx)
</code></pre>

<h3>💡 Напоминание</h3>
<p>Этот проект — для самостоятельной работы. Пересмотрите код из уроков 1-11, особенно уроки-повторения R1/R2 — они показывали те же паттерны в меньшем масштабе.</p>

<h3>📌 После сдачи вы будете знать</h3>
<ul>
<li>✅ Как объединить RTK Query и slice Redux Toolkit в одном реальном проекте</li>
<li>✅ Как построить полностью типизированное приложение React + Redux от начала до конца</li>
<li>✅ Как защитить логику компонентов и состояния автоматизированными тестами</li>
<li>✅ Небольшой готовый проект уровня продакшена для портфолио</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// CAPSTONE: Типизированная корзина покупок — начальный скелет
// ════════════════════════════════════════════════════════════════════

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { createSlice, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook, Provider } from 'react-redux';

// ─────────────────────────────────────────────────────────────────────
// Типы
// ─────────────────────────────────────────────────────────────────────

interface Product {
  id: number;
  name: string;
  price: number;
}

interface CartItem {
  productId: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

// ─────────────────────────────────────────────────────────────────────
// RTK Query — товары (паттерн из урока 5)
// ─────────────────────────────────────────────────────────────────────

export const productsApi = createApi({
  reducerPath: 'productsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getProducts: builder.query<Product[], void>({
      query: () => '/products',
    }),
  }),
});

export const { useGetProductsQuery } = productsApi;

// ─────────────────────────────────────────────────────────────────────
// cartSlice — Задание: заполните
// ─────────────────────────────────────────────────────────────────────

const initialCartState: CartState = { items: [] };

const cartSlice = createSlice({
  name: 'cart',
  initialState: initialCartState,
  reducers: {
    addToCart: (state, action: PayloadAction<number>) => {
      // Задание: если productId уже в корзине — quantity += 1,
      // иначе добавьте новый CartItem.
    },
    removeFromCart: (state, action: PayloadAction<number>) => {
      // Задание: удалите из state.items по productId.
    },
    updateQuantity: (state, action: PayloadAction<{ productId: number; quantity: number }>) => {
      // Задание: обновите quantity у соответствующего CartItem.
    },
  },
});

export const { addToCart, removeFromCart, updateQuantity } = cartSlice.actions;

// ─────────────────────────────────────────────────────────────────────
// Store + типизированные хуки (паттерн из урока 9)
// ─────────────────────────────────────────────────────────────────────

const store = configureStore({
  reducer: {
    [productsApi.reducerPath]: productsApi.reducer,
    cart: cartSlice.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(productsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// Задание: компоненты MahsulotlarRoyxati, SavatSahifasi
// Задание: минимум 5 тестов — в файлах Product.test.tsx, Cart.test.tsx
// ─────────────────────────────────────────────────────────────────────

function App() {
  return (
    <Provider store={store}>
      {/* Задание: добавьте компоненты MahsulotlarRoyxati и SavatSahifasi */}
    </Provider>
  );
}
"""


async def _run():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()

        # Flat fields (translated independently of sections_json)
        await _write(db, "lesson", LESSON_ID, "title", lesson.title, TITLE_RU)
        await _write(db, "lesson", LESSON_ID, "text_content", lesson.text_content, TEXT_RU)
        await _write(db, "lesson", LESSON_ID, "task_title", lesson.task_title, TASK_TITLE_RU)
        await _write(db, "lesson", LESSON_ID, "task_description",
                     lesson.task_description, TASK_DESCRIPTION_RU)
        await _write(db, "lesson", LESSON_ID, "task_requirements",
                     lesson.task_requirements, TASK_REQUIREMENTS_RU)
        await _write(db, "lesson", LESSON_ID, "task_technologies",
                     lesson.task_technologies, TASK_TECHNOLOGIES_RU)

        # sections_json — built manually (not via collect/set) so requirements/
        # techStack — not in _TRANSLATABLE_KEYS — still get translated.
        tree = json.loads(lesson.sections_json)
        for section in tree:
            if section["type"] == "text":
                section["html"] = TEXT_RU
            elif section["type"] == "code":
                section["code"] = CODE_RU
            elif section["type"] == "project":
                section["label"] = TASK_TITLE_RU
                section["description"] = TASK_DESCRIPTION_RU
                section["requirements"] = TASK_REQUIREMENTS_RU
                section["techStack"] = TASK_TECHNOLOGIES_RU
        translated_json = json.dumps(tree, ensure_ascii=False)
        await _write(db, "lesson", LESSON_ID, "sections_json",
                     lesson.sections_json, translated_json)

        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote capstone translation "
              f"(title, text_content, task_*, sections_json)")


if __name__ == "__main__":
    asyncio.run(_run())
