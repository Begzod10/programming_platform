"""Russian translation for course 72, lesson order=12 (L11)."""
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

LESSON_ID = 602

TITLE_RU = "11-Пользовательские события, асинхронное тестирование и мокирование API"

TEXT_RU = """\
<h2>Пользовательские события, асинхронное тестирование и мокирование API</h2>

<pre class="mermaid">
flowchart LR
    UE["userEvent.click(кнопка)"] -->|dispatch(fetchUsers)| M["mock fetch отвечает"]
    M -->|Promise разрешается| FB["findByText — ждёт и находит"]
</pre>

<p>В уроке 10 мы тестировали статичные компоненты. Теперь посмотрим, как писать тесты, когда пользователь совершает <strong>настоящее действие</strong> (клик, ввод текста) и результат приходит <strong>асинхронно</strong> (после запроса к API).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — userEvent для настоящих действий пользователя</h4>
<pre><code>import userEvent from '@testing-library/user-event';
import { render, screen } from '@testing-library/react';

test('число увеличивается при нажатии кнопки', async () =&gt; {
  const user = userEvent.setup();
  render(&lt;Counter /&gt;);

  const tugma = screen.getByRole('button', { name: '+1' });
  await user.click(tugma); // ✅ настоящий клик — focus, pointerdown, pointerup, click

  expect(screen.getByText('Число: 1')).toBeInTheDocument();
});

test('ввод текста в input работает', async () =&gt; {
  const user = userEvent.setup();
  render(&lt;IsmForma /&gt;);

  const input = screen.getByRole('textbox');
  await user.type(input, 'Олим'); // "печатает" каждую букву по отдельности

  expect(screen.getByText('Привет, Олим!')).toBeInTheDocument();
});</code></pre>

<h4>БЛОК 2 — ожидание асинхронного результата: findBy</h4>
<pre><code>function FoydalanuvchilarRoyxati() {
  const [data, setData] = useState&lt;string[] | null&gt;(null);

  useEffect(() =&gt; {
    fetch('/api/users').then(res =&gt; res.json()).then(setData);
  }, []);

  if (!data) return &lt;p&gt;Загрузка...&lt;/p&gt;;
  return &lt;ul&gt;{data.map(u =&gt; &lt;li key={u}&gt;{u}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<pre><code>test('пользователи загружаются', async () =&gt; {
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  // Сначала видно "Загрузка..."
  expect(screen.getByText('Загрузка...')).toBeInTheDocument();

  // findByText — ЖДЁТ, ПОКА НЕ НАЙДЁТ (по умолчанию до 1000мс с повторными попытками)
  const olim = await screen.findByText('Олим');
  expect(olim).toBeInTheDocument();
});</code></pre>

<h4>БЛОК 3 — мокирование fetch</h4>
<pre><code>import { vi } from 'vitest';

beforeEach(() =&gt; {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () =&gt; ['Олим', 'Вали'],
  }) as any;
});</code></pre>

<p>Тест не отправляет настоящий запрос на сервер — сам <code>fetch</code> возвращает поддельный (mock) ответ. Это позволяет писать тесты быстрее, надёжнее (не нужен интернет) и независимо от сервера.</p>

<h3>🐛 Намеренная ошибка — использование getByText для асинхронного результата</h3>
<pre><code>test('пользователи загружаются (ОШИБКА)', async () =&gt; {
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  // ❌ getByText — СИНХРОННЫЙ, проверяет сразу. Fetch ещё не завершился!
  const olim = screen.getByText('Олим');
  expect(olim).toBeInTheDocument();
});</code></pre>

<pre><code>TestingLibraryElementError: Unable to find an element with the text: Олим.</code></pre>

<p><strong>Причина:</strong> <code>getByText</code> — проверяет <strong>сразу</strong>, не ждёт. Так как fetch ещё в состоянии <code>pending</code>, "Олим" ещё нет в DOM — компонент всё ещё показывает "Загрузка...". <code>findByText</code> же <strong>повторяет попытки</strong>, пока элемент не появится (или не истечёт timeout).</p>

<h3>Теперь объясним</h3>

<h4>1. userEvent против fireEvent</h4>
<p><code>fireEvent.click(btn)</code> создаёт одно сырое DOM-событие. <code>userEvent.click(btn)</code> симулирует <strong>всю цепочку</strong> действий настоящего пользователя: pointerdown → focus → pointerup → click. Некоторые баги (например, отключённая кнопка или <code>pointer-events: none</code>) правильно обнаруживаются только с <code>userEvent</code>.</p>

<h4>2. getBy против findBy — когда что использовать?</h4>
<table>
<tr><th>Query</th><th>Синхронный/Асинхронный</th><th>Когда используется</th></tr>
<tr><td><code>getByX</code></td><td>Синхронный</td><td>Элемент должен быть в DOM ПРЯМО СЕЙЧАС</td></tr>
<tr><td><code>findByX</code></td><td>Асинхронный (Promise)</td><td>Элемент появится АСИНХРОННО (fetch, timeout) позже</td></tr>
<tr><td><code>queryByX</code></td><td>Синхронный, возвращает null</td><td>Проверка ОТСУТСТВИЯ элемента</td></tr>
</table>

<h4>3. waitFor — более общий инструмент ожидания</h4>
<pre><code>import { waitFor } from '@testing-library/react';

await waitFor(() =&gt; {
  expect(mockFn).toHaveBeenCalledTimes(1);
});
// findBy — только для поиска элемента. waitFor — для ожидания любого assertion.</code></pre>

<h4>4. Зачем мокировать fetch?</h4>
<ul>
<li>Тест выполняется быстрее — нет реального сетевого запроса</li>
<li>Тест <strong>стабилен</strong> — проходит даже при отсутствии интернета или недоступности сервера</li>
<li>Легко симулировать ошибочные ситуации (<code>mockRejectedValue</code>)</li>
</ul>

<h4>5. Тестирование ошибочной ситуации</h4>
<pre><code>test('если сервер вернёт ошибку, видно сообщение об ошибке', async () =&gt; {
  global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as any;
  render(&lt;FoydalanuvchilarRoyxati /&gt;);

  const xato = await screen.findByText(/ошибка/i);
  expect(xato).toBeInTheDocument();
});</code></pre>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>userEvent</code> полностью симулирует настоящие действия пользователя, надёжнее <code>fireEvent</code></li>
<li>✅ <code>findByX</code> — для элементов, появляющихся асинхронно, ждёт, пока элемент не найдётся</li>
<li>✅ Использование <code>getByX</code> для асинхронного результата приводит к ошибке "Unable to find element"</li>
<li>✅ Мокирование <code>fetch</code> через <code>vi.fn()</code> — быстрые, стабильные тесты без сервера</li>
<li>✅ <code>waitFor</code> — для ожидания любого assertion, не только поиска элемента</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 11: Пользовательские события, асинхронное тестирование, мокирование API
// ════════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect, vi, beforeEach } from 'vitest';

// ─────────────────────────────────────────────────────────────────────
// 1) Тестируемые компоненты
// ─────────────────────────────────────────────────────────────────────

function Counter() {
  const [son, setSon] = useState(0);
  return (
    <div>
      <p>Число: {son}</p>
      <button onClick={() => setSon(s => s + 1)}>+1</button>
    </div>
  );
}

function IsmForma() {
  const [ism, setIsm] = useState('');
  return (
    <div>
      <input aria-label="Имя" value={ism} onChange={(e) => setIsm(e.target.value)} />
      <p>Привет, {ism || 'гость'}!</p>
    </div>
  );
}

function FoydalanuvchilarRoyxati() {
  const [data, setData] = useState<string[] | null>(null);
  const [xato, setXato] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/users')
      .then(res => {
        if (!res.ok) throw new Error('Ошибка сервера');
        return res.json();
      })
      .then(setData)
      .catch(() => setXato('Произошла ошибка'));
  }, []);

  if (xato) return <p>{xato}</p>;
  if (!data) return <p>Загрузка...</p>;
  return <ul>{data.map(u => <li key={u}>{u}</li>)}</ul>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) userEvent — настоящие действия пользователя
// ─────────────────────────────────────────────────────────────────────

describe('Тестирование с userEvent', () => {
  test('число увеличивается при нажатии кнопки', async () => {
    const user = userEvent.setup();
    render(<Counter />);

    await user.click(screen.getByRole('button', { name: '+1' }));

    expect(screen.getByText('Число: 1')).toBeInTheDocument();
  });

  test('ввод текста в input работает', async () => {
    const user = userEvent.setup();
    render(<IsmForma />);

    await user.type(screen.getByRole('textbox'), 'Олим');

    expect(screen.getByText('Привет, Олим!')).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Асинхронное тестирование + мок fetch
// ─────────────────────────────────────────────────────────────────────

describe('FoydalanuvchilarRoyxati (async)', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ['Олим', 'Вали'],
    }) as any;
  });

  test('пользователи загружаются', async () => {
    render(<FoydalanuvchilarRoyxati />);

    expect(screen.getByText('Загрузка...')).toBeInTheDocument();

    const olim = await screen.findByText('Олим'); // ✅ ждёт, пока не найдёт
    expect(olim).toBeInTheDocument();
  });

  test('если сервер вернёт ошибку, видно сообщение об ошибке', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as any;
    render(<FoydalanuvchilarRoyxati />);

    const xato = await screen.findByText('Произошла ошибка');
    expect(xato).toBeInTheDocument();
  });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка — использование getByText для асинхронного результата
// ─────────────────────────────────────────────────────────────────────

/*
test('пользователи загружаются (ОШИБКА — getByText)', () => {
  render(<FoydalanuvchilarRoyxati />);
  // ❌ getByText СИНХРОННЫЙ — fetch ещё не завершился, "Олим" ещё нет в DOM.
  // TestingLibraryElementError: Unable to find an element with the text: Олим.
  const olim = screen.getByText('Олим');
  expect(olim).toBeInTheDocument();
});
*/
"""

EX = {
    3631: {
        "title": "Разница между userEvent и fireEvent",
        "description": "Чем userEvent.click() отличается от fireEvent.click()?",
        "hint": "userEvent — полная цепочка событий, как в реальном браузере.",
        "explanation": "userEvent симулирует всю цепочку промежуточных событий, которые совершает настоящий пользователь (pointerdown, focus, pointerup, click), а fireEvent создаёт только одно сырое DOM-событие.",
    },
    3632: {
        "title": "Какой query для асинхронно появляющегося элемента?",
        "description": "Какой query нужно использовать для поиска текста, который появляется после завершения fetch?",
        "hint": "Только findBy — асинхронный, повторно проверяет, пока элемент не появится.",
        "explanation": "findByText возвращает Promise и повторно проверяет наличие элемента, пока он не появится (или не истечёт timeout). getByText же синхронный — проверяет сразу и не находит ещё не появившийся элемент.",
    },
    3633: {
        "title": "Причина мокирования fetch внутри теста",
        "description": "В чём основная причина замены global.fetch на vi.fn() внутри теста?",
        "hint": "Мок убирает зависимость от реального сервера: быстрее, стабильнее, можно протестировать и ошибочные ситуации.",
        "explanation": "Мокирование fetch ускоряет тест (нет сетевого запроса), делает его более стабильным (не зависит от состояния интернета/сервера) и позволяет легко симулировать ошибочные ситуации (например, статус 500).",
    },
    3634: {
        "title": "Почему getByText выдаёт ошибку \"Unable to find element\" для асинхронного результата?",
        "description": (
            "Если искать данные, приходящие через fetch, с помощью "
            "getByText, почему это почти всегда даёт ошибку, даже если "
            "данные приходят правильно? Объясните своими словами."
        ),
        "expected_answer": "getByText работает синхронно — он проверяет DOM один раз в момент вызова и сразу возвращает результат или ошибку. Запрос fetch же асинхронный — для его завершения нужно время (как минимум один оборот event loop/microtask). Когда код теста доходит до getByText, promise fetch ещё не разрешён, компонент всё ещё в состоянии \"Загрузка...\", и ожидаемого текста ещё нет в DOM. findByText же возвращает Promise и повторно проверяет наличие элемента в течение времени (пока не появится или не истечёт timeout), поэтому правильно работает для асинхронных результатов.",
        "hint": "Сравните, когда завершается fetch и когда проверяет getByText — порядок по времени.",
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
