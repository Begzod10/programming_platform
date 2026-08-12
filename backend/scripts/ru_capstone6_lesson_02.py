"""Russian translation for Capstone 6: Accessibility va Brauzer API, lesson order=1 (L2)."""
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

LESSON_ID = 802

TITLE_RU = "2-Семантический HTML + основы ARIA"

TEXT_RU = """\
<h2>Этап 2: Семантический HTML + основы ARIA — ошибка "кликабельного div"</h2>

<pre class="mermaid">
flowchart LR
    CARD["Карточка задачи - открывается по клику"] --> CHOICE{"&lt;div onclick&gt; или &lt;button&gt;?"}
    CHOICE -->|"&lt;div onclick&gt;"| INVISIBLE["Screen reader: карточка - обычный текст, никакой роли нет"]
    CHOICE -->|"&lt;button&gt;"| VISIBLE["Screen reader: объявляется 'Кнопка, ...', доступна по Tab"]
    INVISIBLE --> BLOCKED["Пользователь клавиатуры НЕ МОЖЕТ открыть карточку"]
</pre>

<p>В курсе Veb Accessibility вы уже изучили семантический HTML и роли ARIA. На этом уроке вы применяете их к сердцу AccessBoard — структуре доски, колонок и карточек. На этот раз баг не вызывает краха, в консоли не появляется ошибка — код <strong>работает именно так, как задумано</strong>, когда вы кликаете мышью. Проблема видна только при тестировании <strong>по-другому</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — семантическая структура: доска, колонка, карточка</h4>
<pre><code>&lt;main&gt;
  &lt;section aria-labelledby="col-todo-heading"&gt;
    &lt;h2 id="col-todo-heading"&gt;В процессе&lt;/h2&gt;
    &lt;ul class="card-list"&gt;
      &lt;li&gt;
        &lt;button class="card" type="button"&gt;
          Исправить страницу логина
        &lt;/button&gt;
      &lt;/li&gt;
    &lt;/ul&gt;
  &lt;/section&gt;
&lt;/main&gt;

&lt;!-- ❗ &lt;button&gt; - НАТИВНЫЙ элемент: браузер АВТОМАТИЧЕСКИ
     даёт ему role="button", tabindex, активацию через Enter/Space.
     Никакой дополнительный ARIA не нужен! --&gt;</code></pre>

<h4>БЛОК 2 — ARIA только когда нативного элемента НЕДОСТАТОЧНО</h4>
<pre><code>&lt;!-- Если по требованиям дизайна &lt;button&gt; использовать нельзя
     (например, ВНУТРИ карточки есть другие интерактивные элементы),
     нужно вручную добавить "свойства кнопки" через ARIA: --&gt;
&lt;li
  class="card"
  role="button"
  tabindex="0"
  aria-describedby="card-1-status"
&gt;
  Исправить страницу логина
  &lt;span id="card-1-status" class="sr-only"&gt;Статус: в процессе&lt;/span&gt;
&lt;/li&gt;

&lt;!-- НО: добавления role="button" + tabindex="0" НЕДОСТАТОЧНО -
     нужно ТАКЖЕ написать JS, вызывающий функцию по нажатию
     Enter/Space (в нативном &lt;button&gt; это идёт БЕСПЛАТНО, в
     кастомном - НЕТ). --&gt;</code></pre>

<h4>БЛОК 3 — "первое правило": есть нативный элемент? Используйте его</h4>
<pre><code># "Первое правило" ARIA Authoring Practices:
# Если для вашей задачи существует подходящий НАТИВНЫЙ HTML-элемент
# (например <button>, <a href>, <input>) - используйте именно его.
# ARIA добавляйте ТОЛЬКО в случаях, когда нативного элемента
# НЕДОСТАТОЧНО.
#
# Почему? Потому что нативные элементы АВТОМАТИЧЕСКИ, самим браузером,
# правильно реализуют роль, поведение клавиатуры, управление фокусом -
# ARIA же лишь "объявляет", но САМО поведение НЕ ОБЕСПЕЧИВАЕТ.</code></pre>

<h3>🐛 Намеренная ошибка — использование &lt;div onclick&gt; для карточки</h3>
<pre><code>&lt;!-- Решив "напишу быстрее, добавлю onclick к div": --&gt;
&lt;div class="card" onclick="openCard(1)"&gt;
  Исправить страницу логина
&lt;/div&gt;

&lt;!-- С помощью CSS это ВИЗУАЛЬНО НЕ ОТЛИЧАЕТСЯ от &lt;button&gt; -
     выглядит так же, работает при клике мышью. --&gt;</code></pre>

<p><strong>Результат:</strong> <code>&lt;div onclick&gt;</code> работает визуально безупречно — при тестировании мышью вы не заметите никакой разницы. Но <code>&lt;div&gt;</code> — <strong>семантически нейтральный</strong> элемент: у него от природы <strong>нет</strong> ни роли (screen reader считает его обычным текстом, не "кнопкой"), <strong>нет</strong> фокуса клавиатуры (без <code>tabindex</code> клавиша <code>Tab</code> его <strong>полностью пропускает</strong>), <strong>нет</strong> активации через клавиатуру (<code>onclick</code> реагирует <strong>только</strong> на клик мышью — при нажатии <code>Enter</code> или <code>Space</code> <strong>ничего</strong> не происходит). Результат: для пользователя клавиатуры или screen reader'а <strong>основная функция всего приложения</strong> — открытие карточки — становится <strong>полностью недоступной</strong>, хотя код "работает".</p>

<h3>Теперь объясним</h3>

<h4>1. Почему <code>&lt;button&gt;</code> работает "как кнопка" даже без ARIA?</h4>
<p><code>&lt;button&gt;</code> <strong>автоматически</strong> обеспечивается самим браузером: <code>role="button"</code>, фокус клавиатуры (<code>tabindex</code>), и активация через <code>Enter</code>/<code>Space</code>. Всё это <strong>встроено</strong> в браузер — разработчику не нужно писать это вручную.</p>

<h4>2. Чего НЕ ХВАТАЕТ в <code>&lt;div onclick&gt;</code>?</h4>
<p><code>&lt;div&gt;</code> семантически <strong>не имеет</strong> особого значения (это просто "контейнер"). Атрибут <code>onclick</code> реагирует только на событие мыши (или касания) — он <strong>автоматически не добавляет</strong> <code>role</code>, <code>tabindex</code> или обработку клавиатурных событий. Каждое из этого нужно писать <strong>вручную</strong>.</p>

<h4>3. Что такое "первое правило" (ARIA First Rule)?</h4>
<p>Если для задачи существует подходящий <strong>нативный</strong> HTML-элемент (<code>&lt;button&gt;</code>, <code>&lt;a href&gt;</code>, <code>&lt;input&gt;</code>), нужно использовать <strong>именно его</strong> — ARIA рекомендуется добавлять только в случаях, когда нативный элемент <strong>действительно недостаточен</strong> (например сложные кастомные компоненты). ARIA — <strong>дополнительный</strong> инструмент, а не <strong>замена</strong> нативного HTML.</p>

<h4>4. Почему эта ошибка "невидима" - не даёт ошибки в консоли?</h4>
<p>С точки зрения JavaScript <code>onclick</code> работает правильно — функция вызывается, ошибка не выбрасывается. Проблема проявляется <strong>только</strong> при тестировании другим способом ввода (клавиатура) или другим средством воспроизведения (screen reader) — а это значит, что обычное тестирование только мышью <strong>никогда</strong> её не обнаружит.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>На 1-м уроке вы теоретически увидели опасность "добавлю клавиатуру потом". На этом уроке вы увидели её в <strong>самом простом, самом частом</strong> проявлении: один неверный выбор элемента (<code>div</code> вместо <code>button</code>) может <strong>полностью</strong> лишить функциональности целую группу пользователей — без какой-либо сложной причины, просто из-за неверного HTML-элемента.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>&lt;button&gt;</code> АВТОМАТИЧЕСКИ получает роль, фокус клавиатуры и активацию от браузера</li>
<li>✅ <code>&lt;div onclick&gt;</code> — семантически нейтрален, сам по себе не несёт никаких свойств доступности</li>
<li>✅ "Первое правило": если есть подходящий нативный элемент, используйте его, ARIA добавляйте только при необходимости</li>
<li>✅ Такая ошибка не видна в консоли - обнаруживается только при тестировании клавиатурой/screen reader'ом</li>
<li>✅ Один неверный выбор элемента может полностью закрыть функцию для целой группы пользователей</li>
</ul>
"""

CODE_RU = """\
// ════════════════════════════════════════════════════════════════════
// ЭТАП 2: Семантический HTML + основы ARIA
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) index.html - семантическая структура, с нативным <button> (в комментарии - HTML)
// ─────────────────────────────────────────────────────────────────────

// <main>
//   <section aria-labelledby="col-todo-heading">
//     <h2 id="col-todo-heading">В процессе</h2>
//     <ul class="card-list">
//       <li>
//         <button class="card" type="button" data-card-id="1">
//           Исправить страницу логина
//         </button>
//       </li>
//     </ul>
//   </section>
// </main>

// ─────────────────────────────────────────────────────────────────────
// 2) app.js - открытие карточек, опираясь на нативную button
// ─────────────────────────────────────────────────────────────────────

document.querySelectorAll('.card').forEach((card) => {
  card.addEventListener('click', () => {
    openCard(card.dataset.cardId);
  });
  // Дополнительный код НЕ НУЖЕН - <button> автоматически превращает
  // Enter/Space тоже в событие 'click'!
});

function openCard(cardId) {
  console.log(`Карточка ${cardId} открыта`);
}

// ─────────────────────────────────────────────────────────────────────
// 3) Намеренная ошибка - <div onclick> (в комментарии - HTML)
// ─────────────────────────────────────────────────────────────────────

// <div class="card" onclick="openCard(1)">
//   Исправить страницу логина
// </div>
// Выглядит визуально так же, работает мышью - но клавиатурой её
// ВООБЩЕ нельзя достичь, screen reader считает её обычным текстом.
"""

EX = {
    4614: {
        "title": "Почему <button> работает 'как кнопка' даже без ARIA?",
        "description": "В чём причина того, что элемент <button> может активироваться через клавиатуру даже без дополнительных атрибутов ARIA?",
        "hint": "Эти свойства идут откуда - от разработчика, или от самого браузера?",
        "explanation": "<button> автоматически обеспечивается самим браузером: role='button', фокус клавиатуры и активация через Enter/Space - всё это встроено в браузер.",
    },
    4615: {
        "title": "Чего не хватает в <div onclick>?",
        "description": "При использовании <div onclick=\"...\">, в отличие от <button>, чего НЕ ХВАТАЕТ для пользователя клавиатуры?",
        "hint": "div - какой элемент семантически?",
        "explanation": "div семантически нейтральный элемент - onclick реагирует только на событие мыши, он автоматически не добавляет роль, tabindex или обработку клавиатурных событий, каждое из этого нужно писать вручную.",
    },
    4616: {
        "title": "Расположите процесс невозможности открыть карточку клавиатурой",
        "description": "Расположите процесс того, как карточка, написанная через <div onclick>, становится полностью недоступной для пользователя клавиатуры.",
        "hint": "",
        "explanation": "",
    },
    4617: {
        "title": "Основное правило применения ARIA",
        "description": "Если для задачи существует подходящий нативный HTML-элемент, что рекомендуется сделать перед добавлением ролей ARIA? (ответьте одним словом/фразой)",
        "hint": "Это 'первое правило' ARIA Authoring Practices.",
        "expected_answer": "использовать нативный элемент",
    },
    4618: {
        "title": "Почему эта ошибка не даёт ошибки в консоли?",
        "description": (
            "Почему ошибка карточки, написанной через <div onclick>, не "
            "выдаёт никакой ошибки или предупреждения в консоли "
            "браузера, хотя делает приложение непригодным для "
            "использования целой группой пользователей? Объясните "
            "своими словами."
        ),
        "hint": "Эта ошибка на уровне JavaScript, или на уровне пользовательского опыта?",
        "expected_answer": "С точки зрения JavaScript onclick работает правильно - функция вызывается, никакой синтаксической или runtime-ошибки нет. Проблема не в самом коде, а в ОПЫТЕ пользователя - точнее, при тестировании кода ТОЛЬКО одним способом ввода (мышь) никакой проблемы не видно. Проблема проявляется только когда кто-то тестирует приложение другим способом (нажимая Tab с клавиатуры, или используя screen reader) - а обычное ручное тестирование только мышью никогда не обнаружит эту ситуацию.",
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
        TASK_TITLE_RU = "AccessBoard — семантический HTML + основы ARIA (структура доски)"
        TASK_DESCRIPTION_RU = (
            "Постройте статическую структуру AccessBoard (доска, колонки, "
            "карточки) с помощью семантического HTML. Для всех "
            "интерактивных карточек используйте нативный <button> (или, "
            "если это невозможно, role='button' + tabindex='0' + "
            "обработку клавиатурных событий)."
        )
        TASK_REQUIREMENTS_RU = (
            "• Структура доски построена через <main>, <section aria-labelledby>, <h2>, <ul>/<li>\n"
            "• Каждая карточка задачи написана как <button> (или с соответствующими ARIA role/tabindex)\n"
            "• Ни для одного интерактивного элемента НЕ ИСПОЛЬЗУЕТСЯ <div onclick> или <span onclick>\n"
            "• Подтверждена возможность последовательно достичь всех карточек клавишей Tab\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "HTML, CSS, JavaScript, ARIA, semantic HTML"
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
