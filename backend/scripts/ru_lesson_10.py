"""Russian translation for course 72, lesson order=11 (L10)."""
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

LESSON_ID = 600

TITLE_RU = "10-Jest + React Testing Library: первый тест"

TEXT_RU = """\
<h2>Jest + React Testing Library — первый тест</h2>

<pre class="mermaid">
flowchart LR
    R["render(&lt;Component /&gt;)"] --> S["screen.getByRole(...)"]
    S --> A["expect(...).toBeInTheDocument()"]
    A --> V["Проверка того, что видит пользователь"]
</pre>

<p>До сих пор вы проверяли код <strong>вручную</strong> — открывали браузер, нажимали кнопку, видели результат своими глазами. Это работает, но по мере роста проекта становится медленнее и о нём забывают. В этом уроке начинаем проверять код <strong>автоматически</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — установка и первый тестовый файл</h4>
<pre><code>// Терминал (в проекте на Vite):
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom</code></pre>

<pre><code>// Counter.tsx
function Counter() {
  const [son, setSon] = useState(0);
  return (
    &lt;div&gt;
      &lt;h2&gt;Счётчик&lt;/h2&gt;
      &lt;p&gt;Число: {son}&lt;/p&gt;
      &lt;button onClick={() =&gt; setSon(s =&gt; s + 1)}&gt;+1&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<pre><code>// Counter.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';
import Counter from './Counter';

describe('Counter', () =&gt; {
  test('в начальном состоянии показывает 0', () =&gt; {
    render(&lt;Counter /&gt;);
    expect(screen.getByText('Число: 0')).toBeInTheDocument();
  });
});</code></pre>

<h4>БЛОК 2 — поиск через screen: getByRole, getByText</h4>
<pre><code>test('заголовок и кнопка видны', () =&gt; {
  render(&lt;Counter /&gt;);

  // getByRole — самый рекомендуемый способ: ищите так, как видит пользователь
  expect(screen.getByRole('heading', { name: 'Счётчик' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: '+1' })).toBeInTheDocument();

  // getByText — по тексту
  expect(screen.getByText('Число: 0')).toBeInTheDocument();
});</code></pre>

<h4>БЛОК 3 — несколько assertion, matcher'ы</h4>
<pre><code>test('Counter полностью рендерится', () =&gt; {
  render(&lt;Counter /&gt;);
  const sarlavha = screen.getByRole('heading');

  expect(sarlavha).toBeInTheDocument();
  expect(sarlavha).toHaveTextContent('Счётчик');
  expect(sarlavha).toBeVisible();
});</code></pre>

<h3>🐛 Намеренная ошибка — тестирование деталей реализации</h3>
<pre><code>// ❌ Поиск через CSS-класс или структуру DOM
test('кнопка работает (плохой тест)', () =&gt; {
  const { container } = render(&lt;Counter /&gt;);
  const tugma = container.querySelector('.counter-btn-primary'); // ❌
  expect(tugma).toBeInTheDocument();
});</code></pre>

<p><strong>Проблема:</strong> этот тест работает — <strong>пока что</strong>. Но если дизайнер изменит имя CSS-класса с <code>.counter-btn-primary</code> на <code>.btn-counter-main</code> (для пользователя <strong>ничего не изменится</strong> — кнопка выглядит и работает так же), тест <strong>сломается</strong>. Вы правильно изменили код, но тест сигнализирует "ошибка" — это <strong>ложный сигнал</strong> (false negative).</p>

<pre><code>// ✅ Поиск через то, что видит пользователь — работает даже если CSS изменится
test('кнопка работает (хороший тест)', () =&gt; {
  render(&lt;Counter /&gt;);
  const tugma = screen.getByRole('button', { name: '+1' });
  expect(tugma).toBeInTheDocument();
});</code></pre>

<h3>Теперь объясним</h3>

<h4>1. Философия RTL — "тестируйте как пользователь"</h4>
<p>Основное правило React Testing Library: <em>"Чем больше ваш тест похож на то, как код используют пользователи, тем больше уверенности он даёт."</em> Пользователь не знает имени CSS-класса или внутренней переменной состояния — он знает только то, что видит на экране, и то, что может нажать.</p>

<h4>2. Приоритет поиска (от лучшего к худшему)</h4>
<table>
<tr><th>Уровень</th><th>Метод</th><th>Почему</th></tr>
<tr><td>1 (лучший)</td><td><code>getByRole</code></td><td>Соответствует accessibility, самый стабильный</td></tr>
<tr><td>2</td><td><code>getByLabelText</code></td><td>Для форм</td></tr>
<tr><td>3</td><td><code>getByText</code></td><td>Для обычного текста</td></tr>
<tr><td>4 (последний вариант)</td><td><code>getByTestId</code></td><td>Только когда другого пути нет</td></tr>
<tr><td>❌</td><td><code>container.querySelector('.class')</code></td><td>Деталь реализации — не используйте</td></tr>
</table>

<h4>3. getBy против queryBy против findBy — кратко</h4>
<ul>
<li><code>getByX</code> — если не найден, СРАЗУ ошибка (throw) — когда элемент обязательно должен быть</li>
<li><code>queryByX</code> — если не найден, возвращает <code>null</code> — для проверки ОТСУТСТВИЯ элемента</li>
<li><code>findByX</code> — асинхронный, ждёт — в следующем уроке (асинхронное тестирование)</li>
</ul>

<h4>4. Почему не стоит тестировать детали реализации?</h4>
<p>Тест должен проверять <strong>внешнее поведение</strong> кода, а не <strong>то, как</strong> оно достигнуто. Если вы замените <code>useState</code> на <code>useReducer</code> (результат остаётся тем же), хороший тест пройдёт без изменений. Тест, проверяющий реализацию, сломается там, где не должен.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>render(&lt;Component /&gt;)</code> + <code>screen.getByX()</code> — основной паттерн написания теста</li>
<li>✅ <code>getByRole</code> — самый рекомендуемый способ поиска (соответствует accessibility)</li>
<li>✅ <code>toBeInTheDocument()</code>, <code>toHaveTextContent()</code>, <code>toBeVisible()</code> — часто используемые matcher'ы</li>
<li>✅ Поиск через CSS-класс/структуру DOM — деталь реализации, не используйте</li>
<li>✅ Философия RTL: "тестируйте так, как пользователь использует"</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 10: Jest/Vitest + React Testing Library — первый тест
// ════════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';

// ─────────────────────────────────────────────────────────────────────
// 1) Тестируемый компонент
// ─────────────────────────────────────────────────────────────────────

function Counter() {
  const [son, setSon] = useState(0);
  return (
    <div>
      <h2>Счётчик</h2>
      <p>Число: {son}</p>
      <button className="counter-btn-primary" onClick={() => setSon(s => s + 1)}>+1</button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 2) Тесты — getByRole, getByText, matcher'ы
// ─────────────────────────────────────────────────────────────────────

describe('Counter', () => {
  test('в начальном состоянии показывает 0', () => {
    render(<Counter />);
    expect(screen.getByText('Число: 0')).toBeInTheDocument();
  });

  test('заголовок и кнопка видны', () => {
    render(<Counter />);
    expect(screen.getByRole('heading', { name: 'Счётчик' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '+1' })).toBeInTheDocument();
  });

  test('Counter полностью рендерится', () => {
    render(<Counter />);
    const sarlavha = screen.getByRole('heading');

    expect(sarlavha).toBeInTheDocument();
    expect(sarlavha).toHaveTextContent('Счётчик');
    expect(sarlavha).toBeVisible();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка — тестирование детали реализации
// ─────────────────────────────────────────────────────────────────────

/*
test('кнопка работает (ПЛОХОЙ тест — через CSS-класс)', () => {
  const { container } = render(<Counter />);
  // ❌ Если имя класса .counter-btn-primary изменится (рефакторинг дизайна),
  // этот тест сломается, хотя кнопка работает так же для пользователя.
  const tugma = container.querySelector('.counter-btn-primary');
  expect(tugma).toBeInTheDocument();
});
*/

// ✅ Правильный вариант — работает даже если CSS изменится
test('кнопка работает (ХОРОШИЙ тест — через role)', () => {
  render(<Counter />);
  const tugma = screen.getByRole('button', { name: '+1' });
  expect(tugma).toBeInTheDocument();
});
"""

EX = {
    3623: {
        "title": "Какова основная философия RTL?",
        "description": "Какая фраза правильно выражает основной принцип React Testing Library?",
        "hint": "RTL — библиотека \"тестирования как пользователь\".",
        "explanation": "Философия RTL: тест должен симулировать не то, как код используется внутри, а то, как его использует пользователь — тогда тест даёт реальную уверенность.",
    },
    3624: {
        "title": "Какой способ поиска самый рекомендуемый?",
        "description": "При поиске элемента через screen, какой способ по RTL наиболее приоритетный (рекомендуемый)?",
        "hint": "Поиск, соответствующий accessibility-роли — самый стабильный и ближе всего к опыту пользователя.",
        "explanation": "getByRole — самый рекомендуемый способ, так как основан на ролях accessibility и остаётся стабильным даже при изменении CSS/структуры DOM.",
    },
    3625: {
        "title": "Почему поиск через CSS-класс — плохая практика?",
        "description": "Почему поиск кнопки через container.querySelector('.btn-primary') не считается хорошей практикой написания тестов?",
        "hint": "CSS-класс — деталь реализации, пользователь этого не знает и не видит.",
        "explanation": "Имена CSS-классов считаются деталью реализации — они часто меняются при рефакторинге дизайна, даже если опыт пользователя остаётся тем же. Тест, зависящий от этого, даёт ложный сигнал.",
    },
    3626: {
        "title": "Почему нужно тестировать поведение, а не деталь реализации?",
        "description": (
            "Если внутри компонента useState заменить на useReducer (при "
            "неизменном внешнем поведении), почему хорошо написанный тест "
            "не должен сломаться? Объясните своими словами."
        ),
        "expected_answer": "Хороший тест проверяет видимое пользователю поведение компонента (например, что показывается на экране при нажатии кнопки), а не детали внутренней реализации (какой хук используется, имя внутренней переменной состояния). Переход с useState на useReducer — это внутренний рефакторинг, для пользователя ничего не меняется: при нажатии кнопки число всё так же увеличивается. Поэтому тест, написанный через getByRole/getByText, должен пройти успешно и после этого рефакторинга — иначе тест мешает свободно рефакторить код.",
        "hint": "Вспомните, что рефакторинг — это улучшение внутреннего кода без изменения внешнего поведения.",
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
