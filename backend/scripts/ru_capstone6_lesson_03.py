"""Russian translation for Capstone 6: Accessibility va Brauzer API, lesson order=2 (L3)."""
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

LESSON_ID = 804

TITLE_RU = "3-Навигация с клавиатуры + WebSocket"

TEXT_RU = """\
<h2>Этап 3: Навигация с клавиатуры + WebSocket — как "теряется" фокус</h2>

<pre class="mermaid">
flowchart LR
    NAV["Пользователь клавиатуры сфокусирован на 3-й карточке"] --> WS["Другой пользователь перемещает карточку - приходит сообщение WebSocket"]
    WS --> RENDER["boardEl.innerHTML = ... - ВЕСЬ DOM пересоздаётся"]
    RENDER --> LOST["Старый сфокусированный элемент УНИЧТОЖАЕТСЯ, фокус переходит на document.body"]
    LOST --> CONFUSED["Пользователь теряет ориентацию, вынужден начинать Tab СНАЧАЛА"]
</pre>

<p>В курсе Veb Accessibility вы уже изучили навигацию с клавиатуры, а в курсе JavaScript: Brauzer API — WebSocket. На этом уроке вы объедините их: построите полную навигацию с клавиатуры И синхронизацию в реальном времени в AccessBoard. Но когда эти два используются <strong>вместе</strong>, возникает новая опасность, невидимая по отдельности: <strong>обновление, пришедшее через WebSocket, может уничтожить фокус пользователя клавиатуры.</strong></p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — навигация Tab + ВИДИМЫЙ индикатор фокуса</h4>
<pre><code>/* style.css */
.card:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}
/* ❗ outline НИКОГДА полностью не убирается ("outline: none"
   вообще не используется) - он лишь заново, красивее
   переоформляется через :focus-visible. */</code></pre>

<h4>БЛОК 2 — обновление в реальном времени через WebSocket</h4>
<pre><code>// app.js
const socket = new WebSocket('ws://localhost:3000');

socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  renderBoard(update.state);   // перерисовывает доску
});</code></pre>

<h4>БЛОК 3 — СОХРАНЕНИЕ ФОКУСА при повторном рендере</h4>
<pre><code>function renderBoard(state) {
  // ❗ ПЕРЕД перезаписью запоминаем карточку, на которой сейчас фокус
  const focusedCardId = document.activeElement?.dataset?.cardId;

  boardEl.innerHTML = renderCardsHTML(state);

  // ❗ ПОСЛЕ перезаписи находим НОВЫЙ элемент с тем же ID и
  // ВОССТАНАВЛИВАЕМ на нём фокус
  if (focusedCardId) {
    const sameCard = boardEl.querySelector(`[data-card-id="${focusedCardId}"]`);
    if (sameCard) sameCard.focus();
  }
}</code></pre>

<h3>🐛 Намеренная ошибка — обновление WebSocket заменяет DOM без сохранения фокуса</h3>
<pre><code>// Решив "обновить доску легко - просто заменю innerHTML":
socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  boardEl.innerHTML = renderCardsHTML(update.state);   // ❌ без сохранения фокуса!
});

// Сценарий:
// 1. Пользователь клавиатуры нажал Tab, сфокусировался на 3-й карточке
// 2. Другой пользователь (мышью) перемещает какую-то карточку
// 3. Сервер отправляет НОВОЕ состояние всем клиентам через WebSocket
// 4. В браузере пользователя клавиатуры boardEl.innerHTML ПОЛНОСТЬЮ
//    заменяется - СТАРАЯ <button> (сфокусированная) УДАЛЯЕТСЯ из DOM,
//    вместо неё создаётся НОВАЯ <button> (хотя на экране выглядит
//    ТАК ЖЕ!)
// 5. Браузер: "сфокусированного элемента больше нет в DOM" - фокус
//    автоматически переходит на document.body
//
// ❌ Пользователь теперь не знает, ГДЕ он находится - на экране
//    ничего "не сломано", но фокус потерян, и приходится начинать
//    Tab СНАЧАЛА, с самого начала доски.</code></pre>

<p><strong>Результат:</strong> визуально экран выглядит <strong>точно так же</strong> - пользователь мыши не замечает никакой разницы. Но для пользователя клавиатуры эта <strong>функция совместной работы в реальном времени</strong> означает, что каждый раз, когда кто-то другой перемещает карточку, ваш фокус <strong>неожиданно теряется</strong>, и вам приходится заново перемещаться по доске с самого начала. Эта ошибка особенно <strong>характерна именно для этого capstone</strong> - потому что она возникает только когда обновления в реальном времени через WebSocket И навигация с клавиатуры используются <strong>одновременно</strong>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему полное удаление <code>outline</code> (<code>outline: none</code>) опасно?</h4>
<p><code>outline</code> — <strong>единственный</strong> визуальный сигнал для пользователя клавиатуры "где я сейчас нахожусь". Многие разработчики убирают его, думая, что он "портит внешний вид", но убрать его <strong>без замены</strong> оставляет пользователя клавиатуры полностью "слепым". Правильное решение — переоформить его <strong>красивее</strong> через <code>:focus-visible</code>, а не убирать полностью.</p>

<h4>2. Почему повторный рендер через <code>innerHTML = ...</code> теряет фокус?</h4>
<p>Когда <code>innerHTML</code> получает новое значение, браузер <strong>уничтожает все старые</strong> DOM-элементы и создаёт на их месте <strong>совершенно новые</strong> элементы - даже если они выглядят визуально одинаково. Поскольку фокус привязан к <strong>элементу</strong>, когда старый элемент исчезает, фокус исчезает вместе с ним, и браузер возвращает его на <code>document.body</code>.</p>

<h4>3. Почему эта ошибка влияет только на пользователя клавиатуры?</h4>
<p>Пользователь мыши <strong>никогда не полагается</strong> на "состояние фокуса" - он всегда сам кликает глазами в нужное место. Пользователь клавиатуры же <strong>полностью полагается</strong> на состояние фокуса - это его "текущее местоположение". Неожиданная потеря фокуса - как будто у пользователя мыши курсор вдруг "перепрыгнул" в другое место экрана.</p>

<h4>4. Как работает правильное решение (сохранение фокуса)?</h4>
<p><strong>Перед</strong> повторным рендером сохраняется информация, идентифицирующая текущий сфокусированный элемент (например <code>data-card-id</code>). <strong>После</strong> повторного рендера нужно найти <strong>новый</strong> элемент с тем же ID и <strong>вручную вернуть</strong> на него фокус - это "исправляет" автоматическое поведение браузера.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>Это - новый тип опасности, характерный для capstone, возникающий когда доступность и функциональность реального времени (WebSocket) используются <strong>вместе</strong>. В отличие от статических ошибок доступности, увиденных на уроках 1-2, эта ошибка проявляется только в <strong>динамическом</strong> состоянии - когда действие другого пользователя меняет ваш экран в реальном времени.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>outline: none</code> оставляет пользователя клавиатуры "слепым" - нужно переоформить через <code>:focus-visible</code>, а не убирать полностью</li>
<li>✅ Повторный рендер через <code>innerHTML</code> уничтожает старые DOM-элементы, унося с собой и фокус</li>
<li>✅ Потеря фокуса влияет только на пользователя клавиатуры, пользователь мыши этого не замечает</li>
<li>✅ Правильное решение: запомнить фокус перед повторным рендером, вручную восстановить после</li>
<li>✅ Это - динамический тип ошибки, возникающий при совместном использовании доступности и функциональности реального времени</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 3: Навигация с клавиатуры + WebSocket
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) style.css - :focus-visible (в комментарии - CSS)
// ─────────────────────────────────────────────────────────────────────

// .card:focus-visible {
//   outline: 3px solid #2563eb;
//   outline-offset: 2px;
// }

// ─────────────────────────────────────────────────────────────────────
// 2) app.js - WebSocket + повторный рендер С СОХРАНЕНИЕМ фокуса
// ─────────────────────────────────────────────────────────────────────

const socket = new WebSocket('ws://localhost:3000');
const boardEl = document.querySelector('#board');

socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  renderBoard(update.state);
});

function renderBoard(state) {
  const focusedCardId = document.activeElement?.dataset?.cardId;

  boardEl.innerHTML = renderCardsHTML(state);

  if (focusedCardId) {
    const sameCard = boardEl.querySelector(`[data-card-id="${focusedCardId}"]`);
    if (sameCard) sameCard.focus();
  }
}

function renderCardsHTML(state) {
  // ... формирует карточки как HTML-строку ...
  return state.cards.map((c) => `
    <button class="card" type="button" data-card-id="${c.id}">
      ${c.title}
    </button>
  `).join('');
}

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - повторный рендер без сохранения фокуса (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// socket.addEventListener('message', (event) => {
//   const update = JSON.parse(event.data);
//   boardEl.innerHTML = renderCardsHTML(update.state);   // фокус не сохранён!
// });
// Если во время фокуса пользователя клавиатуры другой пользователь
// перемещает карточку, фокус "перепрыгивает" на document.body.
"""

EX = {
    4624: {
        "title": "Почему outline: none опасен?",
        "description": "Почему полное отключение индикатора фокуса через outline: none в CSS считается опасным?",
        "hint": "Как пользователь мыши узнаёт 'где он находится'? А пользователь клавиатуры?",
        "explanation": "outline - единственный визуальный сигнал для пользователя клавиатуры 'где я сейчас' - убрать его без замены оставляет пользователя клавиатуры полностью без ориентирующего сигнала.",
    },
    4625: {
        "title": "Как повторный рендер через innerHTML влияет на фокус?",
        "description": "Когда DOM перезаписывается через boardEl.innerHTML = ..., что происходит с ранее сфокусированным элементом?",
        "hint": "Когда innerHTML получает новое значение, СТАРЫЕ элементы всё ещё существуют?",
        "explanation": "Когда innerHTML получает новое значение, браузер уничтожает все старые DOM-элементы и создаёт на их месте совершенно новые - поскольку фокус привязан к элементу, когда старый элемент исчезает, фокус исчезает вместе с ним.",
    },
    4626: {
        "title": "Расположите процесс потери фокуса",
        "description": "Расположите процесс того, как при фокусе пользователя клавиатуры приходит обновление WebSocket, и фокус теряется.",
        "hint": "",
        "explanation": "",
    },
    4627: {
        "title": "Какой CSS псевдокласс используется вместо полного отключения outline?",
        "description": "Вместо outline: none, какой CSS псевдокласс используется, чтобы показывать индикатор фокуса красивее только при фокусировке с клавиатуры?",
        "hint": "Это современный, более 'умный' вариант :focus.",
        "expected_answer": ":focus-visible",
    },
    4628: {
        "title": "Почему эта ошибка влияет только на пользователя клавиатуры, а не мыши?",
        "description": (
            "Почему перерисовка экрана при перемещении карточки другим "
            "пользователем не создаёт никакой проблемы для пользователя "
            "мыши, но становится серьёзной проблемой для пользователя "
            "клавиатуры? Объясните своими словами."
        ),
        "hint": "Как оба пользователя узнают 'где они находятся' - глазами, или по состоянию фокуса?",
        "expected_answer": "Пользователь мыши никогда не полагается на 'состояние фокуса' - он смотрит на экран и каждый раз сам кликает в нужное место, поэтому при перерисовке доски он просто снова находит нужное место и кликает. Пользователь клавиатуры же ПОЛНОСТЬЮ полагается на состояние фокуса, чтобы знать 'где он находится' - это его единственный индикатор 'текущего местоположения'. Когда при перерисовке доски фокус переходит на document.body, для пользователя клавиатуры это как будто он вдруг полностью потерял ориентацию - ему приходится заново начинать нажимать Tab с самого начала доски.",
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
        TASK_TITLE_RU = "AccessBoard — навигация с клавиатуры + WebSocket (с сохранением фокуса)"
        TASK_DESCRIPTION_RU = (
            "Добавьте полную навигацию Tab/Shift+Tab для всех карточек и "
            "видимый индикатор фокуса через :focus-visible. Добавьте "
            "обновление в реальном времени через WebSocket — при "
            "повторном рендере DOM карточка с текущим фокусом должна "
            "определяться, и фокус должен ВОССТАНАВЛИВАТЬСЯ на ней в "
            "обновлённом DOM."
        )
        TASK_REQUIREMENTS_RU = (
            "• Ко всем карточкам можно последовательно перейти через Tab/Shift+Tab\n"
            "• Есть видимый индикатор фокуса через .card:focus-visible (outline: none НЕ ИСПОЛЬЗУЕТСЯ)\n"
            "• Изменения другого пользователя видны в реальном времени через WebSocket\n"
            "• При повторном вызове renderBoard() фокус ВОССТАНАВЛИВАЕТСЯ через ID ранее сфокусированной карточки\n"
            "• Ручная проверка: подтверждено, что при фокусе на карточке и изменении в другом окне фокус НЕ ТЕРЯЕТСЯ\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, JavaScript, WebSocket, ARIA, навигация с клавиатуры"
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
