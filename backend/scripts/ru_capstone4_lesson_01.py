"""Russian translation for Capstone 4: TypeScript Full-Stack, lesson order=0 (L1)."""
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

LESSON_ID = 772

TITLE_RU = "1-Планирование и скелет репозитория"

TEXT_RU = """\
<h2>IssueForge — full-stack проект на TypeScript в 7 этапов</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Планирование"] --> API["2-Backend API"]
    API --> CRUD["3-PostgreSQL CRUD"]
    CRUD --> AUTH["4-Аутентификация"]
    AUTH --> FE["5-React frontend"]
    FE --> TEST["6-Тестирование"]
    TEST --> DEPLOY["7-Деплой"]
</pre>

<p>В этом курсе вы объедините всё, что изучали <strong>по отдельности</strong> в курсах TypeScript Asoslari, Node.js/Express Asoslari и React: Redux Toolkit, TypeScript va Testlash, в <strong>одном реальном проекте</strong>: <strong>IssueForge</strong> — командный трекер задач/багов (issue tracker). Каждый урок — очередной этап этого одного проекта.</p>

<p>Но этот capstone отличается от предыдущих трёх одной вещью: "намеренная ошибка" каждого урока принадлежит <strong>одному семейству</strong> — <strong>TypeScript проверяет типы только во время COMPILE, и НИЧЕГО не гарантирует во время выполнения (runtime).</strong> В этом уроке вы познакомитесь с самой идеей; каждый следующий этап покажет её в новом месте.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — структура репозитория: монорепо с общей папкой types</h4>
<pre><code># Структура репозитория для IssueForge - монорепо как в TaskFlow, но
# поскольку это TypeScript-проект, добавляется ТРЕТЬЯ папка: shared/
issueforge/
  backend/          # Express + TypeScript (создаётся на этапах 2-4)
    src/
    tsconfig.json
  frontend/          # React + Redux Toolkit + TypeScript (этап 5)
    src/
    tsconfig.json
  shared/            # ❗ интерфейсы, которые импортируют И backend, И frontend
    types.ts
  README.md
  .gitignore</code></pre>

<h4>БЛОК 2 — проектирование схемы БД как TypeScript-интерфейсов</h4>
<pre><code>// shared/types.ts - основные интерфейсы для IssueForge
interface User {
  id: number;
  name: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

interface Issue {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  assigneeId: number | null;
  reporterId: number;
  createdAt: string;
}

// Связи:
// - Один User -> много Issue (как репортер)
// - Один User -> много Issue (как исполнитель, необязательно)</code></pre>

<h4>БЛОК 3 — README.md: "дверь" проекта</h4>
<pre><code># README.md
# IssueForge

## О проекте
Командный трекер задач/багов - Express + TypeScript + React + Redux Toolkit.

## Стратегия общих типов
shared/types.ts - backend И frontend импортируют ОДИНАКОВЫЕ интерфейсы.

## Технологии
- Backend: Node.js, Express, TypeScript, PostgreSQL
- Frontend: React, Redux Toolkit, TypeScript

## Статус
- [x] Планирование и скелет репозитория
- [ ] Backend API
- [ ] PostgreSQL CRUD
- [ ] Аутентификация
- [ ] React frontend
- [ ] Тестирование
- [ ] Деплой</code></pre>

<h3>🐛 Намеренная сложность: писать интерфейсы для backend и frontend ОТДЕЛЬНО</h3>
<p>Во многих начинающих TypeScript-проектах разработчик, не задумываясь о папке <code>shared/</code>, пишет один интерфейс <code>Issue</code> для backend и <strong>другой, отдельный</strong> интерфейс <code>Issue</code> для frontend:</p>
<pre><code>// backend/src/types.ts
interface Issue {
  id: number;
  title: string;
  status: string;   // ❗ не литеральный union, обычная строка
  assigneeId: number | null;
}

// frontend/src/types.ts (ОТДЕЛЬНЫЙ файл, написан ОТДЕЛЬНО!)
interface Issue {
  id: number;
  title: string;
  status: string;
  assignee_id: number | null;   // ❗ другой стиль именования - camelCase vs snake_case!
}</code></pre>
<p><strong>Результат:</strong> пока оба интерфейса <strong>выглядят одинаково</strong>, поэтому ошибка не видна. Но это <strong>два независимых файла</strong> — компилятор TypeScript <strong>никогда</strong> их не сравнивает, потому что это разные модули. Если в будущем backend изменит <code>assigneeId</code> на <code>assignee_id</code> (или наоборот), <strong>обе стороны</strong> продолжат "успешно компилироваться" — потому что каждая проверяется только против <strong>своего</strong> интерфейса. Ошибка проявится только на <strong>runtime</strong>, когда frontend попытается прочитать реальный JSON, пришедший от backend (именно эту ситуацию вы увидите на 5-м уроке).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему рекомендуется папка <code>shared/types.ts</code>?</h4>
<p>Если backend и frontend импортируют <strong>один и тот же</strong> файл, расхождение между ними становится <strong>структурно невозможным</strong> — компилятор проверяет обе стороны на основе <strong>одного</strong> интерфейса. Если же они написаны отдельно, ничто не удерживает их синхронными.</p>

<h4>2. Что проверяет TypeScript-интерфейс во время выполнения (runtime)?</h4>
<p><strong>Ничего.</strong> Интерфейс — это лишь "документация", используемая только во время компиляции <code>tsc</code>. После того как программа запущена (скомпилирована в JavaScript), интерфейс полностью <strong>исчезает</strong> — его вообще нет в скомпилированном <code>.js</code> файле. Поэтому, даже если реальный JSON из сети не соответствует интерфейсу, это никто не проверяет на <strong>runtime</strong>, если вы не сделали это <strong>явно</strong> в коде.</p>

<h4>3. Почему схема БД теперь пишется и как интерфейс?</h4>
<p>В TaskFlow (Capstone 1) схема была описана только "на бумаге" (в комментариях). На этот раз, поскольку это TypeScript-проект, схему можно записать <strong>напрямую</strong> как интерфейс — это одновременно и документация, и (частично) проверка на этапе компиляции.</p>

<h4>4. Почему README в этот раз особенно важен?</h4>
<p>README теперь должен объяснять не только "как запустить", но и <strong>стратегию общих типов</strong> — другой разработчик в команде должен знать, что нужно импортировать папку <code>shared/</code>, иначе он может попасть именно в описанную выше "намеренную сложность".</p>

<h4>5. Почему "ошибки" этого курса связаны друг с другом (принадлежат одной семье)?</h4>
<p>В предыдущих capstone-проектах ошибка каждого урока была <strong>независимой</strong> (CORS, foreign key, относительный путь). На этот раз ошибка всех 7 этапов — разные проявления <strong>одной большой идеи</strong>: <em>"TypeScript проверяет во время компиляции, а не во время выполнения."</em> На этот раз вы изучите не только отдельные ошибки, но и более глубокую истину <strong>о самом</strong> TypeScript.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>shared/types.ts</code> — способ привязать интерфейсы backend и frontend к одному источнику</li>
<li>✅ TypeScript-интерфейс <strong>ничего</strong> не проверяет во время выполнения — он работает только при компиляции</li>
<li>✅ Отдельно написанные (несинхронизированные) интерфейсы сейчас выглядят безобидно, но опасны в будущем</li>
<li>✅ Схема БД теперь документируется напрямую и как TypeScript-интерфейс</li>
<li>✅ Все 7 "намеренных ошибок" этого курса — разные проявления одной общей идеи</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 1: Планирование и скелет репозитория
// ════════════════════════════════════════════════════════════════════

// Этот урок посвящён скорее ПЛАНИРОВАНИЮ, чем написанию кода.
// Ниже - полное содержимое файла shared/types.ts для IssueForge:

interface User {
  id: number;
  name: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

interface Issue {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  assigneeId: number | null;
  reporterId: number;
  createdAt: string;
}

export type { User, Issue };

// ─────────────────────────────────────────────────────────────────────
// Структура репозитория (в комментарии - структура папок/файлов, не код)
// ─────────────────────────────────────────────────────────────────────

// issueforge/
//   backend/
//     src/
//     tsconfig.json
//   frontend/
//     src/
//     tsconfig.json
//   shared/
//     types.ts
//   README.md
//   .gitignore

// ─────────────────────────────────────────────────────────────────────
// Намеренная сложность - ОТДЕЛЬНО написанные интерфейсы (в комментарии)
// ─────────────────────────────────────────────────────────────────────

// Если backend/src/types.ts и frontend/src/types.ts написаны отдельно,
// компилятор TypeScript НИКОГДА их не сравнивает - это два независимых
// модуля. shared/types.ts УСТРАНЯЕТ эту проблему.
"""

EX = {
    4464: {
        "title": "Почему для IssueForge рекомендуется shared/types.ts?",
        "description": "В чём основная причина использования одного общего файла shared/types.ts для backend и frontend?",
        "hint": "Если обе стороны импортируют один и тот же файл, может ли между ними возникнуть расхождение?",
        "explanation": "Когда backend и frontend импортируют один файл shared/types.ts, компилятор проверяет обе стороны на основе одного интерфейса - поэтому расхождение между ними становится невозможным. Отдельно написанные интерфейсы ничем не синхронизированы.",
    },
    4465: {
        "title": "Что проверяет TypeScript-интерфейс во время выполнения?",
        "description": "После того как программа скомпилирована в JavaScript (то есть запущена во время выполнения), что проверяет TypeScript-интерфейс?",
        "hint": "Если открыть скомпилированный .js файл, там вообще нет понятия интерфейса.",
        "explanation": "TypeScript-интерфейс - это лишь \"документация\", используемая только во время компиляции tsc. После того как программа превращается в JavaScript, интерфейс полностью исчезает и ничего не проверяет во время выполнения.",
    },
    4466: {
        "title": "Расположите процесс планирования IssueForge",
        "description": "Расположите правильный процесс планирования этапа 1 для IssueForge.",
        "hint": "",
        "explanation": "",
    },
    4467: {
        "title": "Папка сборки TypeScript-проекта для .gitignore",
        "description": "Напишите название стандартной папки, создаваемой при компиляции tsc, которую обязательно нужно добавить в .gitignore.",
        "hint": "Обычно она задаётся параметром \"outDir\" в tsconfig.json.",
        "expected_answer": "dist",
    },
    4468: {
        "title": "Почему отдельно написанные интерфейсы Issue сейчас безобидны, а в будущем опасны?",
        "description": (
            "В backend/src/types.ts и frontend/src/types.ts написаны два "
            "отдельных интерфейса Issue, и сейчас они выглядят одинаково. "
            "Почему это не создаёт проблем сейчас, но может стать "
            "опасным в будущем? Объясните своими словами."
        ),
        "hint": "Сравнивает ли компилятор TypeScript backend/src/types.ts и frontend/src/types.ts друг с другом?",
        "expected_answer": "Поскольку оба интерфейса написаны в отдельных файлах, компилятор TypeScript вообще не сравнивает их друг с другом - каждый проверяется независимо только в своём модуле. Сейчас они случайно выглядят одинаково, поэтому никакой ошибки не возникает. Но в будущем, если, например, backend изменит или уберёт поле assigneeId, интерфейс на frontend ОБ ЭТОМ НЕ УЗНАЕТ, и никакой ошибки компиляции не появится - потому что обе стороны проверяются только против своей собственной копии. Ошибка проявится только во время выполнения, когда frontend попытается использовать реальный JSON, пришедший от backend.",
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
        TASK_TITLE_RU = "IssueForge — скелет репозитория и общая TypeScript-схема"
        TASK_DESCRIPTION_RU = (
            "Создайте монорепо на GitHub для проекта IssueForge (с папками "
            "backend/, frontend/, shared/), напишите полный README.md и "
            "запишите TypeScript-интерфейсы User/Issue в shared/types.ts. "
            "Этот проект будет продолжаться на этом же репозитории все "
            "следующие 6 этапов."
        )
        TASK_REQUIREMENTS_RU = (
            "• На GitHub создан публичный репозиторий с названием 'issueforge'\n"
            "• Есть папки backend/, frontend/, shared/ (пустые или с tsconfig.json)\n"
            "• shared/types.ts: полностью написаны интерфейсы User и Issue\n"
            "• В backend/tsconfig.json и frontend/tsconfig.json указано \"strict\": true\n"
            "• README.md: описание проекта, технологии, объяснена стратегия общих типов, чеклист статуса\n"
            "• Есть файл .gitignore (исключены node_modules, dist, .env)"
        )
        TASK_TECHNOLOGIES_RU = "TypeScript, Git, GitHub, Markdown"
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
