"""Russian translation for Capstone 6: Accessibility va Brauzer API, lesson order=0 (L1)."""
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

LESSON_ID = 800

TITLE_RU = "1-Планирование и скелет репозитория"

TEXT_RU = """\
<h2>AccessBoard — проект, построенный на доступности и браузерных API, в 7 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> HTML["2-Семантический HTML + ARIA"]
    HTML --> KEY["3-Клавиатура + WebSocket"]
    KEY --> COLOR["4-Контраст цветов + IndexedDB"]
    COLOR --> FORM["5-Формы + Drag-and-Drop"]
    FORM --> PWA["6-Service Worker + PWA"]
    PWA --> DEPLOY["7-Деплой (завершение CAPSTONE)"]
</pre>

<p>В этом курсе вы объедините всё, что изучали <strong>по отдельности</strong> в курсах Veb Accessibility и JavaScript: Brauzer API va Web, в <strong>одном реальном проекте</strong>: <strong>AccessBoard</strong> — доска задач для команды в реальном времени (в стиле Trello). Каждый урок — очередной этап этого одного проекта.</p>

<p>Этот capstone отличается от предыдущих пяти одной вещью: на этот раз "намеренная ошибка" не означает, что <strong>сам код сломан</strong>. Код <strong>работает</strong>, тест может быть "зелёным" — но только <strong>для вас</strong>: когда вы тестируете мышью, своими глазами, в стандартном браузере. Каждый этап показывает: то, что интерфейс кажется работающим <strong>вам</strong>, не гарантирует, что он работает для человека, использующего его <strong>по-другому</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — скелет репозитория: frontend + минимальный WebSocket-сервер</h4>
<pre><code># Структура репозитория для AccessBoard
accessboard/
  frontend/
    index.html
    style.css
    app.js
    sw.js               # ❗ дополняется на 6-м уроке - Service Worker
  server/
    server.js           # Express + ws - раздаёт статику + релей WebSocket
    package.json
  README.md
  .gitignore

# Backend ЗДЕСЬ НАМЕРЕННО минимален - без базы данных, только
# пересылает сообщения через WebSocket. Реальные данные хранятся через
# IndexedDB прямо в БРАУЗЕРЕ (на 4-м уроке).</code></pre>

<h4>БЛОК 2 — схема документа (document outline): ПЛАН семантической структуры</h4>
<pre><code># Семантическая структура AccessBoard (пока не HTML - план):
#
# <header>   - название доски, информация о пользователе
# <nav>      - список досок (если досок несколько)
# <main>
#   <section> каждая колонка (например "В процессе", "Готово")
#     <ul>    - список карточек в этой колонке
#       <li>  - каждая карточка задачи
# <footer>   - дополнительные ссылки
#
# Эта структура позволяет пользователю программы чтения с экрана
# (screen reader) понять страницу "на слух" - используя ЕСТЕСТВЕННЫЙ
# смысл HTML-элементов.</code></pre>

<h4>БЛОК 3 — план взаимодействия "клавиатура прежде всего"</h4>
<pre><code># Для каждого действия, выполняемого мышью, ЗАРАНЕЕ ПЛАНИРУЕТСЯ,
# как оно выполняется ЧЕРЕЗ клавиатуру:
#
# Действие мышью                    ->  Эквивалент клавиатуры
# ────────────────────────────────────────────────────────────
# Перетаскивание карточки мышью в    ->  "Выбор" карточки клавишей
# другую колонку                        Enter, затем перемещение между
#                                        колонками клавишами Arrow,
#                                        подтверждение клавишей Enter
# Загрузка файла перетаскиванием     ->  Кнопка "выбрать файл" (input
# мышью                                  type="file") - открывается
#                                        и с клавиатуры тоже</code></pre>

<h3>🐛 Намеренная сложность: планировать под мышь, откладывая клавиатуру "на потом"</h3>
<p>Многие разработчики проектируют интерактивную функцию вроде drag-and-drop (перетаскивание карточки) <strong>сначала для мыши</strong>, планируя "добавить поддержку клавиатуры позже":</p>
<pre><code>// Решив "пока работает только с мышью, клавиатуру добавлю
// потом", код пишется только с событиями drag/drop:
card.addEventListener('dragstart', handleDragStart);
card.addEventListener('dragend', handleDragEnd);
column.addEventListener('drop', handleDrop);
// НИКАКОГО плана для клавиатуры - понятия вроде keydown, focus,
// ARIA live region ещё вообще не рассмотрены.</code></pre>
<p><strong>Результат:</strong> события drag-and-drop (<code>dragstart</code>, <code>drop</code>) и события клавиатуры (<code>keydown</code>, <code>focus</code>) — основаны на <strong>совершенно разных</strong> моделях событий и логике пользовательского опыта. Если код сначала написан только для мыши, "добавление" поддержки клавиатуры позже часто означает <strong>переписывание</strong> всей логики взаимодействия, потому что оба способа выражают одно и то же "действие" <strong>двумя разными</strong> путями. Правильный подход: проектировать оба способа ввода <strong>вместе, с самого начала</strong>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему backend на этот раз намеренно минимален - без базы данных?</h4>
<p>Цель этого capstone — глубокое изучение доступности и браузерных API, а не сложной архитектуры backend'а. WebSocket-сервер выполняет лишь роль "эстафеты" сообщений между пользователями; реальное хранение происходит через <strong>IndexedDB</strong> прямо в браузере (вы увидите это на 4-м уроке).</p>

<h4>2. Почему важна схема документа (document outline)?</h4>
<p>Пользователи программ чтения с экрана понимают страницу не <strong>визуально</strong>, а <strong>на слух</strong>. Правильная семантическая структура (<code>header</code>, <code>nav</code>, <code>main</code>, <code>section</code>) даёт им "карту" страницы, помогая быстро перемещаться по ней.</p>

<h4>3. Почему таблица "эквивалентов клавиатуры" составляется ДО написания кода?</h4>
<p>Если для каждого действия мышью эквивалент клавиатуры определён <strong>заранее</strong>, вопрос "как это сделать с клавиатуры?" во время написания кода <strong>никогда</strong> не откладывается на потом - ответ на него уже дан на этапе проектирования.</p>

<h4>4. Почему события drag-and-drop и клавиатуры считаются "совершенно разными"?</h4>
<p><code>dragstart</code>/<code>drop</code> — браузерные события, связанные с действиями мыши (или касания). <code>keydown</code>/<code>focus</code> — события, связанные с клавиатурой и состоянием фокуса, совершенно другие. Между ними <strong>нет автоматической</strong> связи — для поддержки обоих нужно писать <strong>отдельную</strong> логику для каждого.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>Это — <strong>первое</strong> проявление главной идеи, которая будет повторяться на протяжении всего capstone: доступность — это не то, что "добавляется" в конце проекта, а решение по дизайну, принимаемое <strong>с самого начала</strong>. На следующих уроках вы увидите конкретные последствия игнорирования этого принципа.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ В этом capstone backend намеренно минимален - основное внимание уделено доступности frontend и браузерным API</li>
<li>✅ Правильная семантическая структура (document outline) даёт пользователям screen reader "карту" страницы</li>
<li>✅ Для каждого действия мышью эквивалент клавиатуры должен быть спланирован ДО написания кода</li>
<li>✅ События drag-and-drop и клавиатуры основаны на совершенно разных моделях событий</li>
<li>✅ Доступность - это не то, что добавляется в конце, а решение по дизайну, принимаемое с самого начала</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 1: Планирование и скелет репозитория
// ════════════════════════════════════════════════════════════════════

// Этот урок посвящён скорее ПЛАНИРОВАНИЮ, чем написанию кода.

// ─────────────────────────────────────────────────────────────────────
// Структура репозитория (в комментарии - структура папок/файлов, не код)
// ─────────────────────────────────────────────────────────────────────

// accessboard/
//   frontend/
//     index.html
//     style.css
//     app.js
//     sw.js               (дополняется на 6-м уроке)
//   server/
//     server.js           (Express + ws)
//     package.json
//   README.md
//   .gitignore

// ─────────────────────────────────────────────────────────────────────
// server/server.js - минимальный WebSocket-релей (без базы данных)
// ─────────────────────────────────────────────────────────────────────

const express = require('express');
const { WebSocketServer } = require('ws');

const app = express();
app.use(express.static('../frontend'));

const server = app.listen(3000, () => console.log('AccessBoard: http://localhost:3000'));
const wss = new WebSocketServer({ server });

wss.on('connection', (socket) => {
  socket.on('message', (data) => {
    // Пересылка пришедшего сообщения ВСЕМ ДРУГИМ подключённым клиентам
    wss.clients.forEach((client) => {
      if (client !== socket && client.readyState === client.OPEN) {
        client.send(data.toString());
      }
    });
  });
});

// ─────────────────────────────────────────────────────────────────────
// Намеренная сложность - план только для мыши (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// card.addEventListener('dragstart', handleDragStart);
// card.addEventListener('dragend', handleDragEnd);
// column.addEventListener('drop', handleDrop);
// НИКАКОГО плана для клавиатуры - keydown/focus/ARIA live region
// ещё вообще не рассмотрены.
"""

EX = {
    4604: {
        "title": "Почему backend в этом capstone намеренно минимален?",
        "description": "Почему WebSocket-сервер AccessBoard без базы данных, выполняет лишь роль 'эстафеты' сообщений?",
        "hint": "На чём сфокусирован основной акцент этого capstone?",
        "explanation": "Цель этого capstone - глубокое изучение доступности и браузерных API, а не сложной архитектуры backend'а - WebSocket-сервер лишь пересылает сообщения, реальное хранение происходит через IndexedDB в браузере.",
    },
    4605: {
        "title": "Почему важна схема документа (document outline)?",
        "description": "Почему правильная семантическая структура (header, nav, main, section) важна для пользователей программ чтения с экрана?",
        "hint": "Как пользователь screen reader 'видит' страницу?",
        "explanation": "Пользователи screen reader понимают страницу на слух - правильная семантическая структура даёт им карту страницы и возможность быстро перемещаться по ней.",
    },
    4606: {
        "title": "Расположите процесс планирования AccessBoard",
        "description": "Расположите правильный процесс планирования этапа 1 для AccessBoard.",
        "hint": "",
        "explanation": "",
    },
    4607: {
        "title": "Эквивалент клавиатуры для перемещения карточки",
        "description": "Какие два набора клавиш используются как эквивалент клавиатуры для перетаскивания карточки мышью в другую колонку (drag-and-drop)? (напишите оба через запятую)",
        "hint": "Первая - для 'выбора/подтверждения', вторая - для перемещения между колонками.",
        "expected_answer": "Enter, Arrow",
    },
    4608: {
        "title": "Почему сложно построить drag-and-drop сначала, а клавиатуру добавить потом?",
        "description": (
            "Если разработчик СНАЧАЛА строит функцию drag-and-drop "
            "только с событиями мыши (dragstart/drop), почему "
            "'добавление' поддержки клавиатуры позже оказывается не "
            "простым дополнением, а сложной работой? Объясните своими "
            "словами."
        ),
        "hint": "События dragstart/drop и keydown/focus выражают одно и то же 'действие' одинаковым способом?",
        "expected_answer": "События drag-and-drop (dragstart, dragend, drop) и события клавиатуры (keydown, focus) основаны на совершенно разной модели событий и логике пользовательского опыта - между ними нет никакой автоматической связи. Если код с самого начала построен ТОЛЬКО вокруг событий drag/drop (например, если состояние спроектировано так, что сохраняется только во время перетаскивания), добавление поддержки клавиатуры обычно означает не просто добавление нового обработчика событий, а ПЕРЕПИСЫВАНИЕ всей логики 'выбора и перемещения карточки' на другой основе (на основе управления фокусом и состоянием).",
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
        TASK_TITLE_RU = "AccessBoard — скелет репозитория и документ плана 'клавиатура прежде всего'"
        TASK_DESCRIPTION_RU = (
            "Создайте репозиторий на GitHub для проекта AccessBoard (с "
            "папками frontend/ и server/), напишите полный README.md (с "
            "семантической схемой документа и таблицей эквивалентов "
            "клавиатуры), и напишите минимальный WebSocket-релей сервер "
            "на Express + ws."
        )
        TASK_REQUIREMENTS_RU = (
            "• На GitHub создан публичный репозиторий с названием 'accessboard'\n"
            "• Есть папки frontend/ и server/\n"
            "• README.md: описание проекта, семантическая схема документа (header/nav/main/section), технологии, чеклист статуса\n"
            "• В README.md в таблице показаны минимум 3 действия мышью и их эквиваленты клавиатуры\n"
            "• server/server.js: Express раздаёт статику, ws пересылает WebSocket-сообщения другим клиентам\n"
            "• Есть файл .gitignore (исключены node_modules, .env)"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, JavaScript, Node.js, Express, WebSocket (ws), Git, GitHub"
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
