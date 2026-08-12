"""Russian translation for Capstone: To'liq Stack Loyiha, lesson order=4 (L5)."""
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

LESSON_ID = 740

TITLE_RU = "5-Поиск и фильтрация"

TEXT_RU = """\
<h2>Этап 5: Поиск и фильтрация — full-stack функция</h2>

<pre class="mermaid">
flowchart LR
    INPUT["Пользователь печатает: 'a'"] --> REQ1["Отправляется запрос 1"]
    INPUT --> INPUT2["Пользователь продолжает: 'al'"] --> REQ2["Отправляется запрос 2"]
    REQ2 -->|возвращается быстрее| SHOW2["Показывается результат 'al'"]
    REQ1 -->|возвращается медленнее| SHOW1["ЗАТИРАЕТ старым результатом 'a' - ОШИБКА!"]
</pre>

<p>На этом этапе добавим на backend query-параметры поиска/фильтра, а на frontend &mdash; поле поиска &mdash; это <strong>настоящая</strong> full-stack функция: запрос backend <strong>и</strong> состояние frontend должны работать правильно вместе.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — backend: поиск и фильтр через query-параметры</h4>
<pre><code>app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const { qidiruv, category_id, sahifa = 1 } = req.query;    // ❗ ?qidiruv=...&category_id=...&sahifa=...
  const sahifaHajmi = 10;
  const offset = (sahifa - 1) * sahifaHajmi;

  let sqlSorov = 'SELECT tasks.*, categories.nomi AS category_nomi FROM tasks JOIN categories ON tasks.category_id = categories.id WHERE tasks.user_id = $1';
  const params = [req.userId];

  if (qidiruv) {
    params.push(`%${qidiruv}%`);
    sqlSorov += ` AND tasks.sarlavha ILIKE $${params.length}`;   // ❗ ILIKE - без учёта регистра
  }
  if (category_id) {
    params.push(category_id);
    sqlSorov += ` AND tasks.category_id = $${params.length}`;
  }
  params.push(sahifaHajmi, offset);
  sqlSorov += ` ORDER BY tasks.yaratilgan_vaqt DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;

  const natija = await pool.query(sqlSorov, params);
  res.json(natija.rows);
});</code></pre>

<h4>БЛОК 2 — frontend: поле поиска и debounce</h4>
<pre><code>import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { tasklarniOlish } from '../features/tasksSlice';

function QidiruvMaydoni() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  useEffect(() => {
    const timerId = setTimeout(() => {                 // ❗ debounce - отправляет запрос, когда пользователь ОСТАНОВИЛСЯ печатать
      dispatch(tasklarniOlish({ qidiruv: matn }));
    }, 400);                                             // ❗ ждёт 400ms - не на каждую букву!

    return () => clearTimeout(timerId);                 // ❗ очистка - отменяет старый таймер
  }, [matn, dispatch]);

  return <input value={matn} onChange={(e) => setMatn(e.target.value)} placeholder="Qidirish..." />;
}</code></pre>

<h4>БЛОК 3 — передача параметров в createAsyncThunk</h4>
<pre><code>export const tasklarniOlish = createAsyncThunk('tasks/olish', async ({ qidiruv, category_id } = {}) => {
  const params = new URLSearchParams();
  if (qidiruv) params.append('qidiruv', qidiruv);
  if (category_id) params.append('category_id', category_id);

  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await javob.json();
});</code></pre>

<h3>🐛 Намеренная ошибка — запрос на каждую букву без debounce (race condition)</h3>
<pre><code>// БЕЗ debounce:
function QidiruvMaydoniXato() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const onChange = (e) => {
    setMatn(e.target.value);
    dispatch(tasklarniOlish({ qidiruv: e.target.value }));   // ❌ запрос НА КАЖДУЮ букву сразу!
  };

  return <input value={matn} onChange={onChange} />;
}

// Если пользователь быстро печатает "a", затем "al":
// - для "a" отправляется запрос 1 (ответ может вернуться медленнее)
// - для "al" отправляется запрос 2 (ответ может вернуться быстрее)
// Если запрос 1 вернётся ПОЗЖЕ - он ЗАТРЁТ результат "al" результатом "a"!
// Пользователь напечатал "al", но видит результат по "a".</code></pre>

<p><strong>Результат:</strong> не гарантируется, что сетевые запросы вернутся <strong>в отправленном порядке</strong>. Если для каждой буквы отправляется отдельный запрос, запрос, отправленный раньше (но выполнившийся медленнее), может вернуться <strong>позже</strong> и <strong>затереть</strong> более новый результат старым &mdash; это называется <strong>race condition</strong> (состояние гонки). <strong>Debounce</strong> (немного подождать после того, как пользователь перестал печатать, и только потом отправить запрос) предотвращает эту проблему, так как для промежуточных состояний запрос вообще не отправляется.</p>

<h3>Теперь объясним</h3>

<h4>1. Разница между ILIKE и LIKE</h4>
<p><code>LIKE</code> <strong>чувствителен</strong> к регистру (например <code>"Python"</code> не совпадёт с <code>"python"</code>). <code>ILIKE</code> в PostgreSQL же <strong>не чувствителен</strong> к регистру &mdash; для пользовательского поиска это обычно ожидаемое поведение.</p>

<h4>2. Зачем нужны LIMIT/OFFSET (пагинация)?</h4>
<p>Если у пользователя тысячи задач, возврат <strong>всех</strong> их одним запросом был бы медленным и требовал бы много памяти. <code>LIMIT</code> определяет, сколько результатов вернуть на одной странице, <code>OFFSET</code> &mdash; сколько "пропустить" &mdash; это даёт возможность <strong>пагинации</strong> (постраничной разбивки).</p>

<h4>3. Что такое debounce и зачем он нужен?</h4>
<p>Debounce &mdash; техника отправки запроса <strong>после того, как</strong> пользователь перестал печатать (например через 400мс). <code>setTimeout</code> в <code>useEffect</code> и его очистка через <code>clearTimeout</code> &mdash; при каждом новом введённом символе отменяет предыдущее "ожидание" и начинает новое, так что запрос отправляется только <strong>после того, как</strong> пользователь действительно остановился.</p>

<h4>4. Что такое race condition?</h4>
<p>Race condition &mdash; ситуация, когда результат двух (или более) параллельных процессов зависит от <strong>порядка их завершения</strong>, а этот порядок не гарантирован. Здесь: два сетевых запроса могут вернуться с <strong>разной скоростью</strong>, и если код показывает "последний пришедший ответ" вместо "ответ на последний отправленный запрос", результат может не соответствовать тому, что ожидал пользователь.</p>

<h4>5. Почему debounce снижает вероятность race condition?</h4>
<p>С debounce, пока пользователь быстро печатает, для промежуточных состояний (например <code>"a"</code>, <code>"al"</code>) запрос <strong>вообще не отправляется</strong> &mdash; отправляется только один запрос для <strong>финального</strong> значения после остановки. Это резко снижает количество отправляемых запросов, тем самым снижая и вероятность race condition (хотя и не устраняя её полностью &mdash; для этого нужны дополнительные техники вроде отмены запросов через AbortController).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ На backend поиск/фильтр/пагинация через query-параметры (<code>?qidiruv=...&category_id=...</code>)</li>
<li>✅ <code>ILIKE</code> — поиск без учёта регистра</li>
<li>✅ <code>LIMIT</code>/<code>OFFSET</code> — механизм пагинации</li>
<li>✅ Debounce отправляет запрос после остановки пользователя, снижая количество лишних запросов</li>
<li>✅ Race condition — ошибка, возникающая из-за непредсказуемого порядка возврата параллельных запросов</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 5: Поиск и фильтрация - full-stack функция
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Backend - поиск/фильтр/пагинация через query-параметры
// ─────────────────────────────────────────────────────────────────────

app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const { qidiruv, category_id, sahifa = 1 } = req.query;
  const sahifaHajmi = 10;
  const offset = (sahifa - 1) * sahifaHajmi;

  let sqlSorov = 'SELECT tasks.*, categories.nomi AS category_nomi FROM tasks JOIN categories ON tasks.category_id = categories.id WHERE tasks.user_id = $1';
  const params = [req.userId];

  if (qidiruv) {
    params.push(`%${qidiruv}%`);
    sqlSorov += ` AND tasks.sarlavha ILIKE $${params.length}`;
  }
  if (category_id) {
    params.push(category_id);
    sqlSorov += ` AND tasks.category_id = $${params.length}`;
  }
  params.push(sahifaHajmi, offset);
  sqlSorov += ` ORDER BY tasks.yaratilgan_vaqt DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;

  const natija = await pool.query(sqlSorov, params);
  res.json(natija.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 2) Frontend - поле поиска с debounce (в комментарии - JSX)
// ─────────────────────────────────────────────────────────────────────

// function QidiruvMaydoni() {
//   const [matn, setMatn] = useState('');
//   const dispatch = useDispatch();
//
//   useEffect(() => {
//     const timerId = setTimeout(() => {
//       dispatch(tasklarniOlish({ qidiruv: matn }));
//     }, 400);
//
//     return () => clearTimeout(timerId);
//   }, [matn, dispatch]);
//
//   return <input value={matn} onChange={(e) => setMatn(e.target.value)} placeholder="Qidirish..." />;
// }

// ─────────────────────────────────────────────────────────────────────
// 3) Передача параметров в createAsyncThunk
// ─────────────────────────────────────────────────────────────────────

export const tasklarniOlish = createAsyncThunk('tasks/olish', async ({ qidiruv, category_id } = {}) => {
  const params = new URLSearchParams();
  if (qidiruv) params.append('qidiruv', qidiruv);
  if (category_id) params.append('category_id', category_id);

  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await javob.json();
});

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - запрос на каждую букву без debounce (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// function QidiruvMaydoniXato() {
//   const [matn, setMatn] = useState('');
//   const dispatch = useDispatch();
//   const onChange = (e) => {
//     setMatn(e.target.value);
//     dispatch(tasklarniOlish({ qidiruv: e.target.value }));   // запрос сразу на каждую букву!
//   };
//   return <input value={matn} onChange={onChange} />;
// }
// ❌ При быстрой печати медленный ответ может затереть более быстрый (race condition)
"""

TASK_TITLE_RU = "TaskFlow — Поиск, фильтр и пагинация"

TASK_DESCRIPTION_RU = (
    "Добавьте в эндпоинт GET /tasks query-параметры поиска (по заголовку "
    "через ILIKE), фильтра по category и пагинации (LIMIT/OFFSET). На "
    "frontend создайте поле поиска с debounce и dropdown фильтра по category."
)

TASK_REQUIREMENTS_RU = (
    "• GET /tasks — поддерживает query-параметры ?qidiruv=...&category_id=...&sahifa=...\n"
    "• Поиск через ILIKE, без учёта регистра\n"
    "• Пагинация реализована через LIMIT/OFFSET\n"
    "• На frontend поле поиска работает с debounce 400мс (не на каждую букву)\n"
    "• Присутствует dropdown фильтра по category\n"
    "• Обновлён чеклист статуса в README.md"
)

TASK_TECHNOLOGIES_RU = "Node.js, Express, PostgreSQL (ILIKE/LIMIT/OFFSET), React, Redux Toolkit"

EX = {
    4304: {
        "title": "Разница между ILIKE и LIKE",
        "description": "В чём основная разница между ILIKE и LIKE в PostgreSQL?",
        "hint": "Что удобнее для пользовательского поиска?",
        "explanation": "ILIKE не чувствителен к регистру (case-insensitive), обычный LIKE же чувствителен — в пользовательском поиске обычно используется ILIKE.",
    },
    4305: {
        "title": "Зачем используется debounce?",
        "description": "Зачем в поле поиска используется техника debounce (setTimeout + clearTimeout)?",
        "hint": "Не на каждую букву, а только когда пользователь остановился.",
        "explanation": "Debounce отправляет один запрос после того, как пользователь перестал печатать (например через 400мс), предотвращая отправку отдельного запроса на каждую букву.",
    },
    4306: {
        "title": "Расположите процесс работы debounce",
        "description": "Расположите, как работает debounce, когда пользователь часто вводит символы в поле поиска.",
        "hint": "",
        "explanation": "",
    },
    4307: {
        "title": "SQL-ключевые слова для пагинации",
        "description": "Напишите два ключевых слова, используемых в PostgreSQL для пагинации (например: LIMIT OFFSET).",
        "hint": "",
        "expected_answer": "LIMIT OFFSET",
    },
    4308: {
        "title": "Почему без debounce может возникнуть race condition?",
        "description": (
            "Если поле поиска отправляет запрос сразу при вводе каждой "
            "буквы (без debounce), и пользователь быстро печатает "
            "\"a\", затем \"al\", почему на экране может появиться "
            "результат \"a\" вместо \"al\"? Объясните своими словами."
        ),
        "hint": "",
        "expected_answer": "Не гарантируется, что сетевые запросы вернутся в отправленном порядке — время обработки на сервере и задержка сети у каждого запроса могут отличаться. Хотя запрос для \"a\" был отправлен первым, он мог обработаться на сервере медленнее, поэтому ответ на запрос \"al\", отправленный позже, может вернуться РАНЬШЕ него. Если код записывает в состояние каждый пришедший ответ напрямую (не проверяя, к какому запросу он относится), пришедший позже ответ \"a\" затирает более ранний ответ \"al\" — из-за чего пользователь, реально искавший \"al\", видит результаты по \"a\".",
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
