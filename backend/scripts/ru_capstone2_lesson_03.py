"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=2 (L3)."""
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

LESSON_ID = 748

TITLE_RU = "3-React frontend"

TEXT_RU = """\
<h2>Этап 3: React frontend — подключение к Django API</h2>

<pre class="mermaid">
flowchart LR
    REACT["React (localhost:3000)"] -->|fetch| DJANGO["Django API (localhost:8000)"]
    DJANGO -->|corsheaders в неверном порядке| BLOCKED["Ошибка CORS"]
    DJANGO -->|CorsMiddleware на своём месте| OK["Данные успешно возвращаются"]
</pre>

<p>Теперь подключимся к Django API из этапа 2 через React. В первом capstone-курсе вы настраивали CORS с Node/Express — в Django это делается через пакет <code>django-cors-headers</code>, и у него есть своё особое правило "порядка middleware".</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — получение данных из Django API в React</h4>
<pre><code>// frontend/src/api/topshiriqlar.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function topshiriqlarniOlish() {
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`);
  if (!javob.ok) throw new Error('Topshiriqlarni olishda xato');
  return await javob.json();
}

// frontend/src/components/TopshiriqRoyxati.jsx
import { useEffect, useState } from 'react';
import { topshiriqlarniOlish } from '../api/topshiriqlar';

function TopshiriqRoyxati() {
  const [royxat, setRoyxat] = useState([]);
  const [holat, setHolat] = useState('yuklanmoqda');

  useEffect(() => {
    topshiriqlarniOlish()
      .then((data) => { setRoyxat(data); setHolat('muvaffaqiyatli'); })
      .catch(() => setHolat('xato'));
  }, []);

  if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;

  return (
    <ul>
      {royxat.map((t) => (
        <li key={t.id}>{t.sarlavha} ({t.fan_nomi}) — {t.muddat_vaqti}</li>
      ))}
    </ul>
  );
}</code></pre>

<h4>БЛОК 2 — установка и настройка django-cors-headers</h4>
<pre><code># pip install django-cors-headers

# studymate/settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',            # ❗ добавляется в INSTALLED_APPS
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # ❗ ВАЖНО: должен стоять ПЕРЕД CommonMiddleware!
    'django.middleware.common.CommonMiddleware',
    # ... остальные middleware ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',   # ❗ разрешает запросы только с адреса React
]</code></pre>

<h4>БЛОК 3 — проверка работы CORS</h4>
<pre><code># После правильной настройки в консоли браузера не должно быть ошибок:
# fetch('http://localhost:8000/api/topshiriqlar/') -> 200 OK, данные возвращаются

# Если ошибка CORS всё ещё возникает, первое, что нужно проверить:
# Стоит ли CorsMiddleware в списке MIDDLEWARE ПЕРЕД CommonMiddleware?</code></pre>

<h3>🐛 Намеренная ошибка — неверный порядок CorsMiddleware</h3>
<pre><code># studymate/settings.py - порядок middleware ПЕРЕПУТАН:
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',   # ❌ стоит ПЕРЕД CorsMiddleware!
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# django-cors-headers установлен, CORS_ALLOWED_ORIGINS тоже настроен правильно,
# но при отправке запроса из React:
# ❌ Всё равно возникает ошибка CORS - хотя пакет установлен!</code></pre>

<p><strong>Результат:</strong> middleware Django выполняются <strong>в порядке, указанном в списке</strong>. <code>CommonMiddleware</code> в некоторых случаях может обработать запрос и "завершить" ответ <strong>до того</strong>, как <code>CorsMiddleware</code> успеет добавить CORS-заголовки. Официальная документация django-cors-headers требует размещать <code>CorsMiddleware</code> <strong>как можно выше</strong>, особенно <strong>перед</strong> <code>CommonMiddleware</code> &mdash; если этот порядок нарушен, CORS может не работать, даже если пакет установлен и настроен.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему CORS в Django настраивается иначе, чем в Node?</h4>
<p>В Express <code>cors()</code> — простая функция-middleware. В Django же CORS реализован через отдельный пакет (<code>django-cors-headers</code>), а система middleware Django очень чувствительна к <strong>порядку</strong> — middleware работают в последовательности, указанной в списке.</p>

<h4>2. Почему важен порядок middleware?</h4>
<p>Каждый middleware обрабатывает запрос "на входе" и ответ "на выходе" в порядке списка (на входе сверху вниз, на выходе снизу вверх). <code>CorsMiddleware</code> должен <strong>добавить</strong> CORS-заголовки в ответ &mdash; если он расположен <strong>после</strong> других middleware, некоторые ответы (например ответы с ошибками) могут остаться без этих заголовков.</p>

<h4>3. Что делает <code>CORS_ALLOWED_ORIGINS</code>?</h4>
<p>Это &mdash; список <strong>разрешённых</strong> origin (адресов frontend). Заголовок <code>Access-Control-Allow-Origin</code> добавляется только для запросов с адресов из этого списка &mdash; это Django-эквивалент <code>cors({ origin: '...' })</code> из Express.</p>

<h4>4. Почему эту ошибку путают с "пакет же установлен"?</h4>
<p>Разработчик правильно установил <code>django-cors-headers</code> и правильно настроил <code>CORS_ALLOWED_ORIGINS</code> &mdash; со стороны всё выглядит "правильно". Но если <strong>порядок</strong> в списке <code>MIDDLEWARE</code> неверен, эти настройки не работают как ожидается &mdash; это усложняет поиск ошибки, так как причина не в "настройке", а в "порядке".</p>

<h4>5. Почему CorsMiddleware должен быть выше (перед CommonMiddleware)?</h4>
<p>Согласно документации Django, <code>CorsMiddleware</code> должен располагаться как можно <strong>выше</strong>, чтобы он успел добавить CORS-заголовки до того, как другие middleware (например <code>CommonMiddleware</code>, который иногда сам обрабатывает редиректы или ответы 404) "завершат" запрос.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Получение данных из JSON API Django в React через <code>fetch()</code></li>
<li>✅ <code>django-cors-headers</code> — пакет CORS для Django</li>
<li>✅ <code>CORS_ALLOWED_ORIGINS</code> — Django-эквивалент <code>cors({ origin })</code> из Express</li>
<li>✅ Middleware Django работают <strong>в порядке списка</strong> — это строже, чем порядок middleware в Express</li>
<li>✅ <code>CorsMiddleware</code> должен располагаться <strong>перед</strong> <code>CommonMiddleware</code></li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 3: React frontend - подключение к Django API
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) frontend/src/api/topshiriqlar.js
// ─────────────────────────────────────────────────────────────────────

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function topshiriqlarniOlish() {
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`);
  if (!javob.ok) throw new Error('Topshiriqlarni olishda xato');
  return await javob.json();
}

// ─────────────────────────────────────────────────────────────────────
// 2) frontend/src/components/TopshiriqRoyxati.jsx (в комментарии - JSX)
// ─────────────────────────────────────────────────────────────────────

// function TopshiriqRoyxati() {
//   const [royxat, setRoyxat] = useState([]);
//   const [holat, setHolat] = useState('yuklanmoqda');
//
//   useEffect(() => {
//     topshiriqlarniOlish()
//       .then((data) => { setRoyxat(data); setHolat('muvaffaqiyatli'); })
//       .catch(() => setHolat('xato'));
//   }, []);
//
//   if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;
//
//   return (
//     <ul>
//       {royxat.map((t) => (
//         <li key={t.id}>{t.sarlavha} ({t.fan_nomi}) — {t.muddat_vaqti}</li>
//       ))}
//     </ul>
//   );
// }

// ─────────────────────────────────────────────────────────────────────
// 3) studymate/settings.py - настройка django-cors-headers (Python, в комментарии)
// ─────────────────────────────────────────────────────────────────────

// INSTALLED_APPS = [
//     # ...
//     'corsheaders',
// ]
//
// MIDDLEWARE = [
//     'corsheaders.middleware.CorsMiddleware',      # ПЕРЕД CommonMiddleware!
//     'django.middleware.common.CommonMiddleware',
//     # ...
// ]
//
// CORS_ALLOWED_ORIGINS = [
//     'http://localhost:3000',
// ]

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - перепутан порядок middleware (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// MIDDLEWARE = [
//     'django.middleware.common.CommonMiddleware',   # ПЕРЕД CorsMiddleware - ОШИБКА!
//     'corsheaders.middleware.CorsMiddleware',
// ]
// ❌ Хотя CORS_ALLOWED_ORIGINS настроен правильно, из-за неверного порядка CORS не работает
"""

TASK_TITLE_RU = "StudyMate — React frontend подключён к Django"

TASK_DESCRIPTION_RU = (
    "Создайте в React компонент, получающий задания из Django API и "
    "показывающий их. Установите django-cors-headers на backend и настройте "
    "его в правильном порядке, управляйте адресом API через .env."
)

TASK_REQUIREMENTS_RU = (
    "• frontend/src/api/topshiriqlar.js: функция topshiriqlarniOlish()\n"
    "• Компонент показывает список заданий вместе с fan_nomi и сроком\n"
    "• Обрабатываются состояния загрузки и ошибки\n"
    "• На backend установлен django-cors-headers, CorsMiddleware перед CommonMiddleware\n"
    "• CORS_ALLOWED_ORIGINS правильно настроен с адресом frontend\n"
    "• Адрес API настроен через .env\n"
    "• Обновлён чеклист статуса в README.md"
)

TASK_TECHNOLOGIES_RU = "React, django-cors-headers, fetch API"

EX = {
    4344: {
        "title": "Зачем нужен django-cors-headers?",
        "description": "Для чего в основном используется пакет django-cors-headers в Django?",
        "hint": "Это Django-эквивалент пакета cors() из Express.",
        "explanation": "django-cors-headers используется для разрешения запросов к Django API с другого origin (например React, работающего на отдельном порту).",
    },
    4345: {
        "title": "Где должен располагаться CorsMiddleware?",
        "description": "Где рекомендуется располагать CorsMiddleware в списке MIDDLEWARE?",
        "hint": "Middleware работают в порядке списка.",
        "explanation": "CorsMiddleware должен располагаться как можно выше, особенно перед CommonMiddleware, иначе другие middleware могут \"завершить\" ответ до добавления CORS-заголовков.",
    },
    4346: {
        "title": "Расположите процесс получения данных из Django API",
        "description": "Расположите процесс от вызова topshiriqlarniOlish() при загрузке компонента React до показа данных.",
        "hint": "",
        "explanation": "",
    },
    4347: {
        "title": "Настройка списка разрешённых origin",
        "description": "Через какую настройку в settings.py Django указывается список разрешённых адресов frontend? (напишите название)",
        "hint": "",
        "expected_answer": "CORS_ALLOWED_ORIGINS",
    },
    4348: {
        "title": "Почему при неверном порядке middleware CORS не работает?",
        "description": (
            "django-cors-headers установлен правильно, и CORS_ALLOWED_ORIGINS "
            "тоже настроен правильно, но в списке MIDDLEWARE CommonMiddleware "
            "стоит ПЕРЕД CorsMiddleware. Почему в этом случае CORS всё равно "
            "может не работать? Объясните своими словами."
        ),
        "hint": "В каком порядке работают middleware Django — в порядке списка, или в случайном порядке?",
        "expected_answer": "Middleware Django выполняются именно в том порядке, в котором они записаны в списке MIDDLEWARE. CommonMiddleware в некоторых случаях выполняет такие задачи, как перенаправление запроса или обработка ответов с ошибками, и если он стоит ПЕРЕД CorsMiddleware, ответ может быть \"завершён\" до того, как CorsMiddleware успеет добавить CORS-заголовки. Поэтому, даже если CORS_ALLOWED_ORIGINS настроен правильно, при неверном порядке middleware CORS-заголовки могут не добавляться к некоторым (или всем) ответам, и возникает ошибка CORS.",
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
