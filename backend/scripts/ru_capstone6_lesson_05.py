"""Russian translation for Capstone 6: Accessibility va Brauzer API, lesson order=4 (L5)."""
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

LESSON_ID = 808

TITLE_RU = "5-Доступность форм + File API/Drag-and-Drop"

TEXT_RU = """\
<h2>Этап 5: Доступность форм + File API/Drag-and-Drop — функция "только для мыши"</h2>

<pre class="mermaid">
flowchart LR
    ATTACH["Функция прикрепления файла"] --> ONLY["ТОЛЬКО через drag-and-drop - другого пути нет"]
    ONLY --> MOUSE["Пользователь мыши: работает"]
    ONLY --> KEY["Пользователь клавиатуры/сенсора: функция ВООБЩЕ НЕДОСТУПНА"]
    KEY --> BLOCKED["Это — НЕ деградация, а ПОЛНОЕ ОТСУТСТВИЕ"]
</pre>

<p>В курсе Veb Accessibility вы уже изучили доступность форм, а в курсе JavaScript: Brauzer API — File API и Drag-and-Drop. Этот урок — <strong>полное</strong> проявление опасности, о которой предупреждали на 1-м уроке: если drag-and-drop строится <strong>только для мыши</strong>, а эквивалента для клавиатуры вообще нет, результат — не "усложнённый опыт", как в предыдущих уроках, а <strong>полностью уничтоженная функция</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — форма редактирования карточки: у каждого поля свой &lt;label&gt;</h4>
<pre><code>&lt;form id="edit-card-form"&gt;
  &lt;label for="card-title"&gt;Заголовок&lt;/label&gt;
  &lt;input id="card-title" name="title" type="text" required&gt;

  &lt;label for="card-desc"&gt;Описание&lt;/label&gt;
  &lt;textarea id="card-desc" name="description"&gt;&lt;/textarea&gt;
&lt;/form&gt;

&lt;!-- ❗ &lt;label for="..."&gt; ТОЧНО связан с id поля -
     screen reader объявляет текст label при входе в поле. --&gt;</code></pre>

<h4>БЛОК 2 — прикрепление файла: И через drag-and-drop, И через кнопку, ОБА способа</h4>
<pre><code>&lt;div class="dropzone" id="dropzone"&gt;
  Перетащите файл сюда, или
  &lt;label for="file-input" class="button-like" tabindex="0"&gt;выберите файл&lt;/label&gt;
  &lt;input type="file" id="file-input" class="sr-only-focusable"&gt;
&lt;/div&gt;</code></pre>
<pre><code>// app.js
dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', handleDrop);           // для мыши
fileInput.addEventListener('change', handleFileSelect);  // ❗ работает
                                                           //   и для клавиатуры/сенсора</code></pre>

<h4>БЛОК 3 — объявление ошибок валидации для screen reader</h4>
<pre><code>&lt;input id="card-title" aria-invalid="true" aria-describedby="title-error"&gt;
&lt;span id="title-error" role="alert"&gt;Заголовок не может быть пустым&lt;/span&gt;

&lt;!-- role="alert" - при появлении ошибки screen reader объявляет её
     НЕМЕДЛЕННО, даже без действия пользователя. --&gt;</code></pre>

<h3>🐛 Намеренная ошибка — прикрепление файла ТОЛЬКО через drag-and-drop, другого пути нет</h3>
<pre><code>&lt;!-- Решив "drag-and-drop современно и удобно", не добавили другой способ: --&gt;
&lt;div class="dropzone" id="dropzone"&gt;
  Перетащите файл сюда
&lt;/div&gt;
&lt;!-- НЕТ input type="file", НЕТ кнопки - ТОЛЬКО один способ! --&gt;</code></pre>
<pre><code>// app.js
dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', handleDrop);
// ❌ Больше НИКАКИХ обработчиков событий не написано - выбрать файл
// через клавиатуру или сенсорный экран ВООБЩЕ НЕВОЗМОЖНО.</code></pre>
<pre><code>&lt;!-- Для полей формы тоже: placeholder используется ВМЕСТО label: --&gt;
&lt;input type="text" placeholder="Заголовок" name="title"&gt;
&lt;!-- &lt;label&gt; ВООБЩЕ НЕТ! Screen reader не знает, что это за поле -
     текст placeholder обычно ИСЧЕЗАЕТ при фокусе. --&gt;</code></pre>

<p><strong>Результат:</strong> это — самая <strong>резкая</strong> ошибка, встреченная за весь capstone. Если проблемы на уроках 2-4 <strong>усложняли</strong> или <strong>запутывали</strong> пользовательский опыт (например потеря фокуса, непонимание статуса), здесь проблема иная: для пользователя клавиатуры или сенсорного экрана функция прикрепления файла <strong>доступна на 0%</strong> — это <strong>не деградация, а полное отсутствие</strong>. Такой пользователь <strong>полностью исключается</strong> из этой части приложения, не находя никакого альтернативного пути.</p>

<h3>Теперь объясним</h3>

<h4>1. Чем <code>&lt;label for="..."&gt;</code> отличается от placeholder?</h4>
<p><code>&lt;label for="input-id"&gt;</code> <strong>постоянно, программно</strong> связан с полем: screen reader объявляет его КАЖДЫЙ раз, когда пользователь входит в поле. <code>placeholder</code> же — лишь <strong>визуальная подсказка</strong> — обычно <strong>исчезает</strong>, как только пользователь начинает печатать, а некоторые screen reader вообще его не объявляют.</p>

<h4>2. Почему добавление ТОЛЬКО drag-and-drop — это "полное отсутствие", а не "усложнённый опыт"?</h4>
<p>В ошибках предыдущих уроков (например медленный фокус, низкий контраст) пользователь всё же мог выполнить задачу <strong>каким-то</strong> способом, хоть и сложнее. Здесь же для пользователя клавиатуры/сенсора <strong>вообще нет</strong> пути прикрепить файл — эта функция для них <strong>0%</strong>, полностью недоступна.</p>

<h4>3. Почему <code>&lt;input type="file"&gt;</code> добавляется ВМЕСТЕ с drag-and-drop, а не вместо него?</h4>
<p>Оба ведут к <strong>одному и тому же результату</strong> (выбор файла), но предназначены для разных способов ввода. <code>&lt;input type="file"&gt;</code> естественным образом открывается с клавиатуры (Enter/Space) и вызывает нативный диалог выбора файла операционной системы — это полноценный, естественный эквивалент клавиатуры для drag-and-drop.</p>

<h4>4. Для чего используется <code>role="alert"</code>?</h4>
<p>Обычно screen reader объявляет новый текст только когда пользователь <strong>меняет</strong> фокус. Элемент, помеченный <code>role="alert"</code>, же объявляется <strong>немедленно</strong>, как только он <strong>добавлен в DOM</strong>, даже без действия пользователя — это критически важно для ошибок валидации, потому что пользователь должен узнать об ошибке <strong>сразу</strong>.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>Это — <strong>полное осуществление</strong> предсказания с 1-го урока: "построить сначала для мыши, добавить клавиатуру потом - сложно" - здесь "добавить потом" даже <strong>не было предпринято</strong>, и результат проявляется в самой тяжёлой форме: <strong>отсутствие</strong> целой функции для целой группы пользователей.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>&lt;label for="..."&gt;</code> постоянно связан с полем, <code>placeholder</code> - лишь временная визуальная подсказка</li>
<li>✅ Добавление только drag-and-drop - это не "усложнённый опыт", а полное отсутствие функции</li>
<li>✅ <code>&lt;input type="file"&gt;</code> добавляется ВМЕСТЕ с drag-and-drop, как его естественный эквивалент клавиатуры</li>
<li>✅ <code>role="alert"</code> объявляет ошибки валидации немедленно, без действия пользователя</li>
<li>✅ Это - самое тяжёлое, полное проявление опасности "построить сначала для мыши, добавить клавиатуру потом"</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 5: Доступность форм + File API/Drag-and-Drop
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) edit-card-form - у каждого поля свой <label> (в комментарии - HTML)
// ─────────────────────────────────────────────────────────────────────

// <form id="edit-card-form">
//   <label for="card-title">Заголовок</label>
//   <input id="card-title" name="title" type="text" required
//          aria-invalid="false" aria-describedby="title-error">
//   <span id="title-error" role="alert"></span>
//
//   <label for="card-desc">Описание</label>
//   <textarea id="card-desc" name="description"></textarea>
// </form>

// ─────────────────────────────────────────────────────────────────────
// 2) attach.js - прикрепление файла: И drag-and-drop, И input, ОБА способа
// ─────────────────────────────────────────────────────────────────────

const dropzone = document.querySelector('#dropzone');
const fileInput = document.querySelector('#file-input');

dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  handleFiles(e.dataTransfer.files);
});

// Альтернативный путь, работающий И для клавиатуры/сенсора:
fileInput.addEventListener('change', (e) => {
  handleFiles(e.target.files);
});

function handleFiles(files) {
  for (const file of files) {
    console.log(`Прикреплённый файл: ${file.name}`);
  }
}

// ─────────────────────────────────────────────────────────────────────
// 3) validation.js - объявление ошибки через role="alert"
// ─────────────────────────────────────────────────────────────────────

function showError(inputEl, message) {
  const errorEl = document.getElementById(inputEl.getAttribute('aria-describedby'));
  errorEl.textContent = message;
  inputEl.setAttribute('aria-invalid', 'true');
}

// ─────────────────────────────────────────────────────────────────────
// 4) Намеренная ошибка - только drag-and-drop, placeholder=label (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// <div class="dropzone" id="dropzone">Перетащите файл сюда</div>
// <!-- НЕТ input type="file", НЕТ кнопки -->
// dropzone.addEventListener('drop', handleDrop);
// <!-- Больше никакого пути не написано! -->
//
// <input type="text" placeholder="Заголовок" name="title">
// <!-- <label> ВООБЩЕ НЕТ! -->
"""

EX = {
    4644: {
        "title": "Чем <label for=\"...\"> отличается от placeholder?",
        "description": "Чем <label for=\"input-id\"> отличается от атрибута placeholder для screen reader?",
        "hint": "Что происходит с placeholder, когда пользователь начинает печатать?",
        "explanation": "label постоянно, программно связан с полем и screen reader объявляет его каждый раз, когда пользователь входит в поле. placeholder же лишь визуальная подсказка - обычно исчезает при начале печати, некоторые screen reader вообще его не объявляют.",
    },
    4645: {
        "title": "Почему добавление только drag-and-drop - это 'полное отсутствие', а не 'усложнённый опыт'?",
        "description": "Почему добавление ТОЛЬКО drag-and-drop для прикрепления файла отличается от ошибок предыдущих уроков (например низкого контраста)?",
        "hint": "Мог ли пользователь ВЫПОЛНИТЬ задачу в предыдущих уроках, хоть и в более сложном варианте?",
        "explanation": "В ошибках предыдущих уроков пользователь мог выполнить задачу каким-то способом (хоть и сложнее). Здесь же для пользователя клавиатуры/сенсора вообще нет пути прикрепить файл - эта функция для них полностью недоступна.",
    },
    4646: {
        "title": "Расположите построение правильной функции прикрепления файла",
        "description": "Расположите процесс построения функции прикрепления файла, работающей и для пользователя мыши, и для пользователя клавиатуры.",
        "hint": "",
        "explanation": "",
    },
    4647: {
        "title": "Роль ARIA для немедленного объявления ошибки валидации",
        "description": "Какая роль ARIA используется, чтобы объявить ошибку валидации формы для screen reader НЕМЕДЛЕННО, без действия пользователя? (например: role=\"xxx\")",
        "hint": "Это роль, объявляемая немедленно после добавления в DOM.",
        "expected_answer": "alert",
    },
    4648: {
        "title": "Почему <input type=\"file\"> используется ВМЕСТЕ с drag-and-drop, а не ВМЕСТО него?",
        "description": (
            "Почему в правильном решении dropzone (drag-and-drop) не "
            "убирается, а вместо этого добавляется ещё и <input "
            "type=\"file\">? В чём преимущество сохранения обоих "
            "способов? Объясните своими словами."
        ),
        "hint": "Приводят ли оба способа к ОДНОМУ И ТОМУ ЖЕ результату? Удобны ли оба для ОДНОГО И ТОГО ЖЕ способа ввода?",
        "expected_answer": "Drag-and-drop и <input type=\"file\"> приводят к ОДНОМУ И ТОМУ ЖЕ результату (выбор файла), но оптимизированы для разных способов ввода - drag-and-drop быстр и удобен для пользователя мыши, <input type=\"file\"> же открывается с клавиатуры (через Enter/Space), вызывая нативный диалог выбора файла операционной системы. Если оставить только один из них, пользователи другого способа ввода будут исключены - поэтому оба должны сохраняться ВМЕСТЕ, как два разных пути к одному результату.",
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
        TASK_TITLE_RU = "AccessBoard — доступность форм + File API/Drag-and-Drop"
        TASK_DESCRIPTION_RU = (
            "Постройте форму редактирования карточки с правильными "
            "элементами <label>. Напишите функцию прикрепления файла И "
            "через drag-and-drop, И через <input type=\"file\"> (чтобы "
            "работали оба способа). Объявляйте ошибки валидации через "
            "role=\"alert\"."
        )
        TASK_REQUIREMENTS_RU = (
            "• Каждое поле формы имеет связанный через <label for=\"...\"> ярлык (НЕ placeholder)\n"
            "• Прикрепление файла работает И через dropzone (drag-and-drop), И через <input type=\"file\">\n"
            "• Ручная проверка: подтверждена ВОЗМОЖНОСТЬ прикрепить файл только клавишами Tab и Enter (без мыши)\n"
            "• Ошибки валидации немедленно объявляются в элементе, помеченном role=\"alert\"\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, JavaScript, File API, ARIA, доступность форм"
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
