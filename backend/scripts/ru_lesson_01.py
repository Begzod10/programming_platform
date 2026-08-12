"""Russian translation for course 72, lesson order=0 (L1)."""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

LESSON_ID = 576

TITLE_RU = "1-Зачем Redux Toolkit? Пределы возможностей Context"

TEXT_RU = """\
<h2>Зачем Redux Toolkit? Прочувствуйте пределы Context</h2>

<pre class="mermaid">
flowchart LR
    P["Значение Provider изменилось"] --> A["useContext(X) — компонент A"]
    P --> B["useContext(X) — компонент B"]
    P --> C["useContext(X) — компонент C"]
    A -->|даже если ничего из X не используется| RA["перерендер"]
    B -->|даже если ничего из X не используется| RB["перерендер"]
    C -->|только это реально нужно| RC["перерендер"]
</pre>

<p>На курсе "React Asoslari" вы изучили <code>Context API</code> — хороший инструмент для глобального состояния. Но в больших приложениях разработчики часто отказываются от Context в пользу <strong>Redux Toolkit</strong>. Почему? В этом уроке вы это <em>почувствуете</em> — не через теорию, а через живую демонстрацию.</p>

<h3>🏆 Победа за 5 минут — почувствуйте проблему</h3>

<h4>БЛОК 1 — два независимых значения, один Context</h4>
<pre><code>import { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);

function ThemeLabel() {
  const { theme } = useContext(AppContext);
  console.log("🎨 ThemeLabel перерендерился");
  return &lt;p&gt;Тема: {theme}&lt;/p&gt;;
}

function CounterLabel() {
  const { count } = useContext(AppContext);
  console.log("🔢 CounterLabel перерендерился");
  return &lt;p&gt;Число: {count}&lt;/p&gt;;
}

function App() {
  const [theme, setTheme] = useState("light");
  const [count, setCount] = useState(0);

  return (
    &lt;AppContext.Provider value={{ theme, count }}&gt;
      &lt;ThemeLabel /&gt;
      &lt;CounterLabel /&gt;
      &lt;button onClick={() =&gt; setCount(c =&gt; c + 1)}&gt;+1 (только число)&lt;/button&gt;
    &lt;/AppContext.Provider&gt;
  );
}</code></pre>

<p>Откройте консоль и нажмите кнопку <strong>+1</strong>. Вы изменили только <code>count</code> — <code>theme</code> не трогали. Но что видно в консоли?</p>

<pre><code>🎨 ThemeLabel перерендерился   ← почему он перерендерился?!
🔢 CounterLabel перерендерился</code></pre>

<p><strong>Вот проблема.</strong> <code>ThemeLabel</code> — не использует ничего, кроме <code>theme</code>. Но он тоже перерендерился, потому что Context передаёт один цельный объект <code>value</code>. React не знает, какое именно поле изменилось — он лишь видит, что "объект value получил новую ссылку", и перерендеривает <strong>всех</strong> подписчиков.</p>

<h4>БЛОК 2 — увеличьте масштаб проблемы</h4>
<pre><code>// Теперь представьте 50 компонентов вроде ThemeLabel —
// каждый показывает только theme, к count не имеет отношения.
// При каждом нажатии "+1" все 50 будут перерендериваться.
// В 1 компоненте это незаметно. В 50 — вы почувствуете джанк (замедление).

function ManyThemeLabels() {
  return (
    &lt;&gt;
      {Array.from({ length: 50 }).map((_, i) =&gt; (
        &lt;ThemeLabel key={i} /&gt;
      ))}
    &lt;/&gt;
  );
}</code></pre>

<h4>БЛОК 3 — как решает Redux Toolkit (пока просто посмотрите, писать не будете)</h4>
<pre><code>// В следующем уроке разберём это полностью. Пока — просто взгляните на форму:

function ThemeLabelRTK() {
  // подписывается ТОЛЬКО на срез theme — если изменится count, этот компонент НЕ перерендерится
  const theme = useSelector((state) =&gt; state.app.theme);
  return &lt;p&gt;Тема: {theme}&lt;/p&gt;;
}</code></pre>

<p><code>useSelector</code> подписывается <strong>только</strong> на тот кусочек, который вы запросили. Когда меняется <code>count</code>, <code>state.app.theme</code> не меняется, поэтому <code>ThemeLabelRTK</code> не перерендерится. Это — ключевое отличие Redux Toolkit от Context.</p>

<h3>🐛 Намеренная ошибка — "запихнуть всё в один Context"</h3>
<pre><code>// Самая частая ошибка новичков:
const MegaContext = createContext(null);

function App() {
  const [user, setUser] = useState(null);        // меняется редко
  const [theme, setTheme] = useState("light");   // меняется редко
  const [mousePos, setMousePos] = useState({x:0,y:0}); // меняется ПРИ КАЖДОМ движении!

  useEffect(() =&gt; {
    const handler = (e) =&gt; setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () =&gt; window.removeEventListener("mousemove", handler);
  }, []);

  return (
    &lt;MegaContext.Provider value={{ user, theme, mousePos }}&gt;
      &lt;WholeApp /&gt;
    &lt;/MegaContext.Provider&gt;
  );
}</code></pre>

<p><strong>Результат:</strong> при движении мыши (десятки раз в секунду!) — перерендерится <strong>всё приложение</strong>, подписанное на <code>MegaContext</code>, даже компоненты, показывающие <code>user</code> или <code>theme</code>. Причина — часто меняющееся значение <code>mousePos</code> смешано в одном Context с редко меняющимися значениями.</p>

<p>Это не вина Context — это <strong>неправильное использование</strong>. Но в большом приложении подобные ситуации встречаются часто, и именно поэтому нужна внешняя библиотека управления состоянием.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему Context всегда работает по принципу "всё или ничего"</h4>
<p>Пропс <code>value</code> у Context — это один объект (или значение). React сравнивает "старое value === новое value" через <code>Object.is()</code>. Если не равны — перерендерятся <strong>все</strong> компоненты, вызвавшие <code>useContext</code>. React не знает и не хочет знать, какое поле внутри объекта изменилось — это осознанное архитектурное решение Context.</p>

<h4>2. Redux (и RTK) работают иначе — подписка через selector</h4>
<table>
<tr><th></th><th>Context</th><th>Redux / RTK</th></tr>
<tr><td>Единица подписки</td><td>Весь value Provider'а</td><td>Каждый <code>useSelector</code> — только запрошенный кусок</td></tr>
<tr><td>Триггер перерендера</td><td>Изменилась ссылка value — всё</td><td>Изменился только результат selector'а — только он</td></tr>
<tr><td>DevTools / time-travel</td><td>Нет</td><td>Есть (Redux DevTools)</td></tr>
<tr><td>Бойлерплейт</td><td>Мало</td><td>Мало с RTK, много в классическом Redux</td></tr>
</table>

<h4>3. Когда Context достаточно?</h4>
<ul>
<li>Редко меняющиеся значения: тема, язык (locale), авторизованный пользователь</li>
<li>Небольшие-средние приложения без глубокого дерева компонентов</li>
<li>Нужно решить только "проброс пропсов" (props drilling через 10 уровней)</li>
</ul>

<h4>4. Когда нужен Redux Toolkit?</h4>
<ul>
<li>Часто обновляемое состояние, используемое многими компонентами (корзина, фильтры, данные в реальном времени)</li>
<li>Сложная асинхронная логика (запросы к API, состояния загрузки/ошибки)</li>
<li>Нужны DevTools/time-travel для отладки</li>
<li>Большая команда — action/reducer дают чёткую структуру</li>
</ul>

<h4>5. RTK против классического Redux — в чём разница?</h4>
<pre><code>// Классический Redux — ручной код для каждого action
const INCREMENT = "counter/increment";
function increment() { return { type: INCREMENT }; }
function counterReducer(state = { value: 0 }, action) {
  switch (action.type) {
    case INCREMENT:
      return { ...state, value: state.value + 1 }; // ручное immutable-обновление
    default:
      return state;
  }
}

// Redux Toolkit — createSlice создаёт всё автоматически
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) =&gt; { state.value += 1; }, // Immer — выглядит как мутация, на деле immutable
  },
});
// action creator, action type, reducer — всё автоматически</code></pre>

<p>RTK — это не сам Redux, а <strong>официальный, рекомендуемый</strong> слой поверх Redux. Он уменьшает бойлерплейт и с помощью Immer превращает код, "написанный как мутация", в безопасное immutable-обновление.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Если value Context изменился — перерендерятся ВСЕ подписчики, независимо от того, какое поле изменилось</li>
<li>✅ Redux/RTK — через <code>useSelector</code> позволяют подписаться только на нужный кусок</li>
<li>✅ Context достаточен для редко меняющихся глобальных значений (тема, язык, пользователь)</li>
<li>✅ Redux Toolkit подходит для часто обновляемых, сложных, больших приложений</li>
<li>✅ RTK <code>createSlice</code> автоматизирует бойлерплейт action/reducer, позволяя безопасно писать "мутации" благодаря Immer</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// УРОК 1: Зачем Redux Toolkit? Пределы возможностей Context
// ════════════════════════════════════════════════════════════════════

import { createContext, useContext, useState, useEffect } from 'react';

// ─────────────────────────────────────────────────────────────────────
// 1) Демонстрация проблемы — один Context, два независимых значения
// ─────────────────────────────────────────────────────────────────────

const AppContext = createContext(null);

function ThemeLabel() {
  const { theme } = useContext(AppContext);
  console.log("🎨 ThemeLabel перерендерился");
  return <p>Тема: {theme}</p>;
}

function CounterLabel() {
  const { count } = useContext(AppContext);
  console.log("🔢 CounterLabel перерендерился");
  return <p>Число: {count}</p>;
}

function ContextMuammosiDemo() {
  const [theme, setTheme] = useState("light");
  const [count, setCount] = useState(0);

  return (
    <AppContext.Provider value={{ theme, count }}>
      <ThemeLabel />
      <CounterLabel />
      <button onClick={() => setCount(c => c + 1)}>+1 (только число)</button>
      <button onClick={() => setTheme(t => t === "light" ? "dark" : "light")}>
        Сменить тему
      </button>
    </AppContext.Provider>
  );
}

// Смотрите в консоль: при нажатии "+1" ThemeLabel тоже перерендерится —
// хотя использует только theme.

// ─────────────────────────────────────────────────────────────────────
// 2) Увеличение проблемы — 50 подписчиков
// ─────────────────────────────────────────────────────────────────────

function ManyThemeLabels() {
  return (
    <>
      {Array.from({ length: 50 }).map((_, i) => (
        <ThemeLabel key={i} />
      ))}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка — "запихнуть всё в один Context"
// ─────────────────────────────────────────────────────────────────────

const MegaContext = createContext(null);

function MegaProviderXato({ children }) {
  const [user] = useState({ name: "Олим" });          // меняется редко
  const [theme, setTheme] = useState("light");         // меняется редко
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 }); // меняется ПРИ КАЖДОМ движении!

  useEffect(() => {
    const handler = (e) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);

  return (
    <MegaContext.Provider value={{ user, theme, mousePos }}>
      {children}
    </MegaContext.Provider>
  );
}

function UserBadge() {
  const { user } = useContext(MegaContext);
  console.log("👤 UserBadge перерендерился (даже из-за изменения mousePos!)");
  return <span>{user.name}</span>;
}

// ─────────────────────────────────────────────────────────────────────
// 4) Направление решения — Redux Toolkit useSelector (полностью в след. уроке)
// ─────────────────────────────────────────────────────────────────────

/*
function ThemeLabelRTK() {
  // подписка только на срез theme — если изменится mousePos или другое
  // состояние, этот компонент НЕ перерендерится.
  const theme = useSelector((state) => state.app.theme);
  return <p>Тема: {theme}</p>;
}
*/

// ─────────────────────────────────────────────────────────────────────
// 5) RTK против классического Redux — сравнение бойлерплейта
// ─────────────────────────────────────────────────────────────────────

// Классический Redux:
const INCREMENT = "counter/increment";
function increment() { return { type: INCREMENT }; }
function counterReducerClassic(state = { value: 0 }, action) {
  switch (action.type) {
    case INCREMENT:
      return { ...state, value: state.value + 1 };
    default:
      return state;
  }
}

/*
// Redux Toolkit (импортируем в следующем уроке):
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1; }, // Immer — безопасная "мутация"
  },
});
*/
"""

EX = {
    3527: {
        "title": "Как обновляются подписчики Context?",
        "description": "Если значение ThemeContext изменится (например, только поле `theme`), что произойдёт со всеми компонентами, подписанными на этот Context через useContext?",
        "hint": "Context — это единый объект 'value'. React не знает, какое поле изменилось.",
        "explanation": "При каждом изменении value Context Provider перерендеривает ВСЕ компоненты, вызвавшие useContext — независимо от того, какое поле внутри объекта value изменилось.",
    },
    3528: {
        "title": "Когда Context становится проблемой?",
        "description": "В каком случае использование Context вызывает больше всего проблем с производительностью?",
        "hint": "Как часто меняется значение и сколько компонентов подписано — вот что определяет цену.",
        "explanation": "Часто меняющееся значение + множество компонентов-подписчиков = большой каскад перерендеров при каждом изменении. Это как раз тот случай, когда нужно внешнее хранилище вроде Redux.",
    },
    3529: {
        "title": "Расположите в правильном порядке цепочку обновления Context",
        "description": "Расположите в правильном порядке, что происходит при изменении value Provider'а.",
        "hint": "Context работает на уровне value, а не на уровне DOM.",
        "explanation": "Ценность Context проявляется в повторном вызове функций компонентов (рендер), а не в обновлении DOM. Сравнение DOM (diffing) — следующий, отдельный этап.",
    },
    3530: {
        "title": "Почему в больших приложениях одного Context недостаточно?",
        "description": "Объясните своими словами: почему в больших приложениях с часто обновляемым состоянием разработчики выбирают Redux Toolkit вместо Context?",
        "hint": "Подумайте о производительности перерендеров, избирательной подписке и инструментах отладки.",
        "expected_answer": "Context при каждом обновлении перерендеривает всех подписчиков, потому что не может различить, какое поле изменилось. В большом приложении это приводит к множеству лишних перерендеров и замедлению. Внешнее хранилище вроде Redux Toolkit позволяет через selector подписываться только на нужную часть состояния — благодаря этому перерендериваются только по-настоящему связанные компоненты. Кроме того, Redux даёт DevTools, middleware и другие инструменты, тогда как Context — это просто механизм передачи значения.",
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
            fields = EX[ex.id]
            for field_name, translated in fields.items():
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
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings + "
              f"{sum(len(v) for v in EX.values())} exercise fields")


if __name__ == "__main__":
    asyncio.run(_run())
