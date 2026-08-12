"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=5 (L6)."""
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

LESSON_ID = 782

TITLE_RU = "6-Тестирование (Jest + React Testing Library)"

TEXT_RU = """\
<h2>Этап 6: Тестирование (Jest + React Testing Library) — "зелёный" тест не значит "всё работает"</h2>

<pre class="mermaid">
flowchart LR
    MOCK["Тест: пишется mock-объект issue"] --> TYPE{"С типом Issue, или через 'as any'?"}
    TYPE -->|"с типом Issue"| SAFE["Если backend меняет форму Issue - ОШИБКА КОМПИЛЯЦИИ"]
    TYPE -->|"через 'as any'"| BLIND["Если backend меняет форму Issue - тест ВСЁ РАВНО ЗЕЛЁНЫЙ"]
    BLIND --> FALSE["🟢 Зелёный тест, но реальная интеграция СЛОМАНА"]
</pre>

<p>В курсе React: Redux Toolkit, TypeScript va Testlash вы уже изучили Jest + React Testing Library, запросы <code>render</code>/<code>screen</code> и мокирование API. Этот урок — об инструменте, который <strong>должен был</strong> отлавливать все ошибки, встреченные за весь capstone: о тестах. Но именно здесь раскрывается последняя, самая тонкая истина: <strong>само написание теста</strong>, если оно сделано неправильно, — как и интерфейс — может давать <strong>ложную уверенность</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — настройка Jest + React Testing Library (знакомо по курсу React: RTK+TS)</h4>
<pre><code># Terminal:
npm install -D jest @testing-library/react @testing-library/jest-dom ts-jest @types/jest</code></pre>

<h4>БЛОК 2 — IssueCard ПРАВИЛЬНО: mock написан с типом Issue</h4>
<pre><code>// frontend/src/components/IssueCard.test.tsx
import { render, screen } from '@testing-library/react';
import IssueCard from './IssueCard';
import { Issue } from '../../../shared/types';

// ❗ mock-объект объявлен с типом Issue - если Issue изменится,
//    эта строка даст ОШИБКУ КОМПИЛЯЦИИ, автор теста узнает СРАЗУ!
const mockIssue: Issue = {
  id: 1,
  title: 'Страница логина сломана',
  description: 'Кнопка сброса пароля не работает',
  status: 'open',
  assigneeId: 7,
  reporterId: 2,
  createdAt: '2026-01-01T10:00:00Z',
};

test('IssueCard показывает заголовок и статус', () =&gt; {
  render(&lt;IssueCard {...mockIssue} /&gt;);
  expect(screen.getByText('Страница логина сломана')).toBeInTheDocument();
  expect(screen.getByText('open')).toBeInTheDocument();
});</code></pre>

<h4>БЛОК 3 — тестирование async thunk: мокирование fetch</h4>
<pre><code>// frontend/src/features/issuesSlice.test.ts
import { configureStore } from '@reduxjs/toolkit';
import issuesReducer, { fetchIssues } from './issuesSlice';
import { Issue } from '../../../shared/types';

test('fetchIssues корректно обновляет успешное состояние', async () =&gt; {
  const mockData: Issue[] = [
    { id: 1, title: 'Test', description: '...', status: 'open',
      assigneeId: null, reporterId: 1, createdAt: '2026-01-01T00:00:00Z' },
  ];
  global.fetch = jest.fn(() =&gt;
    Promise.resolve({ ok: true, json: () =&gt; Promise.resolve(mockData) })
  ) as jest.Mock;

  const store = configureStore({ reducer: { issues: issuesReducer } });
  await store.dispatch(fetchIssues());

  expect(store.getState().issues.list).toEqual(mockData);
});</code></pre>

<h3>🐛 Намеренная ошибка — mock написан через "as any"</h3>
<pre><code>// Решив "написать быстрее" вместо импорта типа Issue:
const mockIssue = {
  id: 1,
  title: 'Страница логина сломана',
  status: 'open',
  assigneeId: 7,
} as any;   // ❌ отключает ВЕСЬ контроль типов!

test('IssueCard показывает заголовок и статус', () =&gt; {
  render(&lt;IssueCard {...mockIssue} /&gt;);
  expect(screen.getByText('Страница логина сломана')).toBeInTheDocument();
});
// ✅ Тест ЗЕЛЁНЫЙ - пока всё выглядит работающим.

// ТЕПЕРЬ происходит история с 5-го этапа: backend меняет assigneeId
// на объект assignee{id,name}. Реальный компонент IssueCard теперь
// сломан (как вы видели на 5-м уроке). НО:
//
// ❌ Этот тест ОСТАЁТСЯ ЗЕЛЁНЫМ! Потому что mockIssue написан через
//    "as any" - он ПОЛНОСТЬЮ независим от интерфейса Issue и никогда
//    не даёт СИГНАЛ "Issue изменился, mock нужно обновить". Тест
//    даёт ложную уверенность "IssueCard работает", хотя в
//    production он на самом деле СЛОМАН.</code></pre>

<p><strong>Результат:</strong> <code>as any</code> — это "аварийный выход", <strong>полностью отключающий</strong> систему контроля типов TypeScript. Если mock-данные написаны с типом <code>Issue</code>, и впоследствии интерфейс <code>Issue</code> изменится (как на 5-м этапе), <code>tsc</code> <strong>не сможет скомпилировать</strong> тест — это <strong>немедленный</strong> сигнал автору теста: "внимание, mock-данные устарели". Mock, написанный через <code>as any</code>, <strong>никогда</strong> не даёт такого сигнала — тест всегда остаётся "зелёным", даже если он больше <strong>не тестирует</strong> реальный production-код.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему важно писать mock-объект с типом <code>Issue</code> (а НЕ через <code>as any</code>)?</h4>
<p>Когда написано <code>const mockIssue: Issue = {...}</code>, TypeScript проверяет mock-объект против <strong>реального</strong> интерфейса <code>Issue</code> — так же, как и любое другое значение в production-коде. Это <strong>всегда, автоматически</strong> держит mock синхронизированным с реальным типом.</p>

<h4>2. Что на самом деле делает <code>as any</code>?</h4>
<p><code>any</code> — самый "опасный" тип, изученный в курсе TypeScript Asoslari: он отключает <strong>весь</strong> контроль типов. Написать <code>as any</code> означает "больше не проверяй это значение никак". Это <strong>хуже</strong>, чем <code>as SomeInterface</code>, потому что не сравнивается вообще ни с каким интерфейсом.</p>

<h4>3. Что происходит с ПРАВИЛЬНО написанным mock'ом, если backend меняет форму <code>Issue</code>, как на 5-м уроке?</h4>
<p>Если интерфейс <code>Issue</code> в <code>shared/types.ts</code> обновится (например <code>assigneeId</code> будет убран), строка <code>const mockIssue: Issue = {...}</code> теперь даст <strong>ошибку компиляции</strong> — потому что mock-объект больше не соответствует новому интерфейсу. Это — <strong>полезная</strong> ошибка: она немедленно сигнализирует автору теста "это нужно обновить".</p>

<h4>4. Почему mock, написанный через <code>as any</code>, не даёт такого сигнала?</h4>
<p><code>as any</code> <strong>полностью отделяет</strong> mock-объект от интерфейса <code>Issue</code> — TypeScript больше <strong>никогда</strong> их не сравнивает. Как бы ни менялся <code>Issue</code>, mock, написанный через <code>as any</code>, <strong>никогда</strong> не даст ошибку компиляции — он остаётся "замороженным", в устаревшем виде.</p>

<h4>5. Что означает "зелёный" тест, а что — нет?</h4>
<p>"Зелёный" (успешный) тест означает лишь то, что ничего не сломалось <strong>в том виде, в каком написан тест</strong> — это <strong>не значит</strong>, что production-код работает правильно, если сам тест <strong>оторван</strong> от реальной формы данных (например через <code>as any</code>). Хороший тест должен быть не только "зелёным", но и <strong>чувствительным</strong> к реальным production-условиям.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Написание mock-данных с реальным типом интерфейса (НЕ через <code>as any</code>) держит тест синхронизированным с реальным типом</li>
<li>✅ <code>as any</code> — самая опасная конструкция, отключающая всю систему контроля типов TypeScript</li>
<li>✅ Правильно написанный mock даёт полезный сигнал через ошибку компиляции при изменении интерфейса</li>
<li>✅ Mock, написанный через <code>as any</code>, никогда не даёт такого сигнала — тест "замораживается"</li>
<li>✅ "Зелёный" тест — источник реального доверия только тогда, когда сам тест написан правильно</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 6: Тестирование (Jest + React Testing Library)
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) IssueCard.test.tsx - mock с типом Issue (ПРАВИЛЬНО)
// ─────────────────────────────────────────────────────────────────────

import { render, screen } from '@testing-library/react';
import IssueCard from './IssueCard';
import { Issue } from '../../../shared/types';

const mockIssue: Issue = {
  id: 1,
  title: 'Страница логина сломана',
  description: 'Кнопка сброса пароля не работает',
  status: 'open',
  assigneeId: 7,
  reporterId: 2,
  createdAt: '2026-01-01T10:00:00Z',
};

test('IssueCard показывает заголовок и статус', () => {
  render(<IssueCard {...mockIssue} />);
  expect(screen.getByText('Страница логина сломана')).toBeInTheDocument();
  expect(screen.getByText('open')).toBeInTheDocument();
});

// ─────────────────────────────────────────────────────────────────────
// 2) issuesSlice.test.ts - async thunk, fetch замокан
// ─────────────────────────────────────────────────────────────────────

import { configureStore } from '@reduxjs/toolkit';
import issuesReducer, { fetchIssues } from './issuesSlice';

test('fetchIssues корректно обновляет успешное состояние', async () => {
  const mockData: Issue[] = [
    { id: 1, title: 'Test', description: '...', status: 'open',
      assigneeId: null, reporterId: 1, createdAt: '2026-01-01T00:00:00Z' },
  ];
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })
  ) as jest.Mock;

  const store = configureStore({ reducer: { issues: issuesReducer } });
  await store.dispatch(fetchIssues());

  expect(store.getState().issues.list).toEqual(mockData);
});

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - mock через "as any" (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// const mockIssue = {
//   id: 1, title: 'Страница логина сломана', status: 'open', assigneeId: 7,
// } as any;   // отключает ВЕСЬ контроль типов!
//
// Даже если интерфейс Issue изменится, как на 5-м этапе, этот тест
// ОСТАЁТСЯ ЗЕЛЁНЫМ - даёт ложную уверенность.
"""

EX = {
    4514: {
        "title": "Что делает as any?",
        "description": "В TypeScript, в записи const mockIssue = {...} as any; что на самом деле делает as any?",
        "hint": "any - самый опасный тип, изученный в курсе TypeScript Asoslari.",
        "explanation": "as any отключает ВЕСЬ контроль типов для этого значения - это опаснее, чем as SomeInterface, потому что вообще не сравнивается ни с каким интерфейсом.",
    },
    4515: {
        "title": "Почему полезно писать mock с типом Issue?",
        "description": "Чем запись const mockIssue: Issue = {...}, в отличие от as any, полезна?",
        "hint": "Может ли mock-объект перестать соответствовать интерфейсу, если тот изменится?",
        "explanation": "Написание mock с типом Issue держит его синхронизированным с реальным интерфейсом - если Issue впоследствии изменится, несоответствующий mock даст ошибку компиляции, что является полезным, немедленным сигналом.",
    },
    4516: {
        "title": "Расположите процесс появления 'ложно-зелёного' теста",
        "description": "Расположите процесс того, почему тест с mock'ом через as any остаётся зелёным даже при изменении интерфейса Issue.",
        "hint": "",
        "explanation": "",
    },
    4517: {
        "title": "Конструкция, не рекомендуемая для mock-данных в тестах",
        "description": "Напишите не рекомендуемую конструкцию TypeScript, которая отделяет mock-объекты от реального интерфейса (например: as xxx).",
        "hint": "Это 'аварийный выход', отключающий весь контроль типов.",
        "expected_answer": "as any",
    },
    4518: {
        "title": "Почему 'тест прошёл зелёным' не всегда значит 'код работает правильно'?",
        "description": (
            "Объясните, почему успешное ('зелёное') прохождение тестов "
            "не всегда означает, что production-код работает правильно. "
            "При каком условии это верно? Объясните своими словами."
        ),
        "hint": "Что на самом деле проверяет тест - сам интерфейс, или 'замороженную' копию, написанную в тесте?",
        "expected_answer": "Зелёное прохождение теста означает лишь то, что ничего не сломалось В ТОМ ВИДЕ, В КАКОМ НАПИСАН тест - этот показатель полностью зависит от того, насколько ПРАВИЛЬНО и чувствительно к РЕАЛЬНЫМ данным написан сам тест. Если mock-данные теста отделены от реального интерфейса способом вроде 'as any', то даже когда интерфейс (то есть реальная форма production-данных) изменится, тест НИКОГДА этого не заметит и останется зелёным - хотя реальный код (например компонент IssueCard) теперь работает с совершенно другими, сломанными данными. Поэтому 'зелёный тест' является настоящим источником доверия только тогда, когда сам тест написан правильно, привязанным к реальной форме данных.",
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
        TASK_TITLE_RU = "IssueForge — Тестирование (Jest + React Testing Library)"
        TASK_DESCRIPTION_RU = (
            "Напишите тесты для компонента IssueCard и issuesSlice. Все "
            "mock-данные (объекты issue) должны быть объявлены с типом "
            "Issue из shared/types.ts — 'as any' или другие конструкции "
            "без проверки НЕ ДОЛЖНЫ использоваться."
        )
        TASK_REQUIREMENTS_RU = (
            "• IssueCard.test.tsx — минимум 2 теста, mock написан с типом Issue\n"
            "• issuesSlice.test.ts — минимум 1 тест для fetchIssues, fetch замокан\n"
            "• Ни в одном mock-данных не используется 'as any'\n"
            "• npm test успешно проходит все тесты без ошибок\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Jest, React Testing Library, TypeScript, ts-jest"
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
