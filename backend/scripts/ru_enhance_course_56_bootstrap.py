"""Russian translations for the enhance_course_56_bootstrap.py content additions.

The lessons already have hand-authored RU translations cached (provider=
'manual') for their pre-existing content. This script does NOT redo those —
it takes the existing cached RU text_content/sections_json as a base and
appends the RU translation of the new bug-marker block + new exercise,
mirroring exactly what enhance_course_56_bootstrap.py did on the UZ side.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

MARKER_RU = "🐛 Намеренная ошибка"

BUG_HTML_RU = {
    514: f"""<h3>{MARKER_RU}</h3>
<p>Новичок пишет так — и грид "ломается":</p>
<pre><code class="lang-html">&lt;div class="container"&gt;
  &lt;div class="col-md-4"&gt;Карточка 1&lt;/div&gt;
  &lt;div class="col-md-4"&gt;Карточка 2&lt;/div&gt;
  &lt;div class="col-md-4"&gt;Карточка 3&lt;/div&gt;
&lt;/div&gt;</code></pre>
<p><strong>Результат:</strong> карточки сдвинуты влево, вылезают за пределы container (появляется горизонтальный скролл). Причина: класс <code>.col-*</code> создаёт gutter через <code>padding</code>, а компенсирует его <strong>только</strong> отрицательный <code>margin: 0 -0.75rem</code> у <code>.row</code>. Без <code>.row</code> этот padding ничем не компенсируется, и весь блок съезжает.</p>
<p><strong>Правильное решение:</strong> <code>.col-*</code> всегда должен быть прямым потомком <code>.row</code>: <code>.container &gt; .row &gt; .col-*</code>.</p>""",
    515: f"""<h3>{MARKER_RU}</h3>
<p>В проект подключён только <code>bootstrap.min.js</code> (не bundle), и dropdown/tooltip не работают:</p>
<pre><code class="lang-html">&lt;script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"&gt;&lt;/script&gt;
&lt;!-- клик по dropdown — ничего не появляется --&gt;</code></pre>
<p><strong>Результат:</strong> в консоли <code>Popper is not defined</code>. Компонентам dropdown, tooltip и popover нужен <strong>Popper.js</strong> для расчёта позиционирования. <code>bootstrap.min.js</code> — версия без Popper; <code>bootstrap.bundle.min.js</code> уже включает его.</p>
<p><strong>Правильное решение:</strong> всегда подключайте <code>bootstrap.bundle.min.js</code> (если не управляете Popper отдельно).</p>""",
    516: f"""<h3>{MARKER_RU}</h3>
<p>Студент открывает и "закрывает" модалку вручную через JS вместо <code>data-bs-toggle</code>:</p>
<pre><code class="lang-javascript">// Открытие модалки вручную
document.querySelector('#myModal').classList.add('show');
document.querySelector('#myModal').style.display = 'block';

// "Закрытие" по нажатию кнопки
document.querySelector('#myModal').classList.remove('show');
document.querySelector('#myModal').style.display = 'none';</code></pre>
<p><strong>Результат:</strong> модалка визуально закрылась, но страница всё ещё не скроллится, а тёмный фон (<code>.modal-backdrop</code>) остаётся — потому что эти элементы добавляет и убирает именно JS-класс <code>Modal</code> из Bootstrap, а вы управляли только самим <code>&lt;div id="myModal"&gt;</code>.</p>
<p><strong>Правильное решение:</strong> всегда используйте собственный API Bootstrap: <code>bootstrap.Modal.getInstance(el).hide()</code> или <code>data-bs-dismiss="modal"</code>.</p>""",
    517: f"""<h3>{MARKER_RU}</h3>
<p>Разработчик хочет скрыть элемент "только на md" и пишет:</p>
<pre><code class="lang-html">&lt;div class="d-md-none"&gt;Должен быть скрыт только на md&lt;/div&gt;</code></pre>
<p><strong>Результат:</strong> элемент скрыт начиная с md (768px) и на <strong>всех</strong> экранах крупнее — lg, xl, xxl, — видим только на маленьких экранах. Это не то поведение "только в диапазоне md", которое ожидалось.</p>
<p><strong>Причина:</strong> утилитные классы Bootstrap mobile-first — префикс <code>-md-</code> означает "md и крупнее", а не "только md".</p>
<p><strong>Правильное решение:</strong> чтобы скрыть только в одном диапазоне, нужны два класса: <code>d-none d-md-block d-lg-none</code>.</p>""",
    518: f"""<h3>{MARKER_RU}</h3>
<p>В админ-дашборде sidebar сделан <code>position: fixed</code>, а основной контент не изменён:</p>
<pre><code class="lang-html">&lt;div class="sidebar" style="position:fixed; width:250px; height:100vh;"&gt;...&lt;/div&gt;
&lt;div class="main-content"&gt;
  &lt;h1&gt;Dashboard&lt;/h1&gt;
  &lt;!-- Карточки Bootstrap здесь --&gt;
&lt;/div&gt;</code></pre>
<p><strong>Результат:</strong> первые 250px блока <code>main-content</code> скрыты под sidebar — потому что <code>position: fixed</code> полностью выводит элемент из обычного потока документа, и другие элементы "не знают" о его существовании.</p>
<p><strong>Правильное решение:</strong> дать <code>main-content</code> <code>margin-left: 250px</code> (или использовать grid Bootstrap: <code>col-md-2</code> для sidebar + <code>col-md-10</code> для контента — оба в обычном потоке).</p>""",
}

NEW_EXERCISES_RU = {
    514: {
        "exercise_id": 4669,
        "title": "Почему .col-md-4 вылезают за пределы container?",
        "description": "<code>&lt;div class=\"container\"&gt;&lt;div class=\"col-md-4\"&gt;...&lt;/div&gt;&lt;/div&gt;</code> — .row пропущен. Почему это вызывает горизонтальный скролл?",
        "hint": "Вспомните, зачем нужен .row — он даёт не только визуальный, но и математический компенсирующий эффект.",
        "explanation": ".col-* получает padding слева-справа (для gutter). .row компенсирует этот padding через margin: -0.75rem. Без .row компенсации нет, и колонки вылезают за край container.",
    },
    515: {
        "exercise_id": 4670,
        "title": "Почему при клике на dropdown ничего не появляется?",
        "description": "В проекте подключён только <code>bootstrap.min.js</code>, а не <code>bootstrap.bundle.min.js</code>. Dropdown не работает, в консоли ошибка 'Popper is not defined'. Почему?",
        "expected_answer": "bootstrap.min.js не включает Popper.js. Компонентам dropdown/tooltip/popover нужен Popper для расчёта позиционирования. bootstrap.bundle.min.js — версия, куда Popper уже встроен. Решение: подключить bundle-версию или добавить Popper отдельным CDN.",
        "hint": "Подумайте, что означает слово 'bundle' — что во что 'упаковано'?",
        "explanation": "JS-компоненты Bootstrap 5 (dropdown, tooltip, popover) зависят от Popper.js. Bundle-версия включает его, обычная — нет.",
    },
    516: {
        "exercise_id": 4671,
        "title": "Почему страница не скроллится после ручного 'закрытия' модалки через display:none?",
        "description": "Разработчик открыл модалку через classList.add('show'), а потом 'закрыл' через classList.remove('show'). Но страница всё ещё тёмная, скролл не работает. В чём причина?",
        "options": '["CSS-файл не загружен", "Классы .modal-backdrop и body.modal-open добавляет/убирает только API Bootstrap Modal, ручное управление их не затрагивает", "ID модалки написан неверно", "Устаревшая версия JavaScript"]',
        "correct_answers": "B",
        "hint": "При открытии модалки добавляется не только сам #myModal — там есть ещё два элемента. Где они?",
        "explanation": "При вызове Modal.show() Bootstrap добавляет .modal-backdrop в document.body и класс modal-open (overflow:hidden) на body. Убрать их может только Modal.hide(). Ручной display:none этого не делает.",
    },
    517: {
        "exercise_id": 4672,
        "title": "Почему d-md-none скрывает элемент и на lg, и на xl экранах?",
        "description": "Написан класс <code>d-md-none</code>, цель — скрыть элемент только в диапазоне md (768-991px). Но на lg и более крупных экранах элемент тоже не виден. Почему?",
        "expected_answer": "Утилитные классы Bootstrap mobile-first: префикс -md- означает 'md и все более крупные экраны', а не только md. d-md-none скрывает начиная с md везде. Чтобы скрыть только в диапазоне md, нужна комбинация d-none d-md-block d-lg-none.",
        "hint": "Префиксы breakpoint у Bootstrap читаются как 'начиная с этого размера', а не 'только на этом размере'.",
        "explanation": "Каждый префикс -{breakpoint}- работает через media query min-width, то есть применяется начиная с этой точки и выше.",
    },
    518: {
        "exercise_id": 4673,
        "title": "Почему текст dashboard прячется под fixed sidebar?",
        "description": "Sidebar сделан position: fixed шириной 250px, main-content не получил никакого margin. В итоге левая часть контента скрыта за sidebar. Почему?",
        "options": '["Используется устаревшая версия Bootstrap", "position: fixed выводит элемент из обычного потока, другие элементы не резервируют под него место", "Неверно указана ширина sidebar", "z-index был не нужен"]',
        "correct_answers": "B",
        "hint": "Общее свойство fixed и absolute позиционирования — как они влияют на поток документа?",
        "explanation": "position: fixed (как и absolute) выводит элемент из обычного потока документа — при расчёте layout он как бы 'не существует'. Поэтому соседним элементам нужно вручную выделить отступ (margin/padding).",
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, bug_html_ru in BUG_HTML_RU.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

            old_ru_text = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "text_content",
            ))).scalar_one().translated_text
            old_ru_sections = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
            ))).scalar_one().translated_text

            new_ru_text = old_ru_text + "\n\n" + bug_html_ru
            await _write(db, "lesson", lesson_id, "text_content", lesson.text_content, new_ru_text)

            ru_tree = json.loads(old_ru_sections)
            uz_tree = json.loads(lesson.sections_json)
            uz_text_sections = [s for s in uz_tree if s["type"] == "text"]
            ru_text_sections = [s for s in ru_tree if s["type"] == "text"]
            assert len(uz_text_sections) == len(ru_text_sections)
            ru_text_sections[-1]["html"] = (ru_text_sections[-1].get("html") or "") + "\n\n" + bug_html_ru

            uz_exercise_section = next(s for s in uz_tree if s["type"] == "exercise")
            ru_exercise_section = next(s for s in ru_tree if s["type"] == "exercise")
            spec = NEW_EXERCISES_RU[lesson_id]
            ex_id = spec["exercise_id"]
            uz_ex_dict = next(e for e in uz_exercise_section["exercises"] if e["id"] == ex_id)
            ru_ex_dict = dict(uz_ex_dict)
            ru_ex_dict["title"] = spec["title"]
            ru_ex_dict["description"] = spec["description"]
            ru_ex_dict["hint"] = spec["hint"]
            ru_ex_dict["explanation"] = spec.get("explanation", "")
            if "expected_answer" in spec:
                ru_ex_dict["expected_answer"] = spec["expected_answer"]
            ru_exercise_section["exercises"].append(ru_ex_dict)

            new_ru_sections_json = json.dumps(ru_tree, ensure_ascii=False)
            await _write(db, "lesson", lesson_id, "sections_json", lesson.sections_json, new_ru_sections_json)

            ex = (await db.execute(select(Exercise).where(Exercise.id == ex_id))).scalar_one()
            await _write(db, "exercise", ex_id, "title", ex.title, spec["title"])
            await _write(db, "exercise", ex_id, "description", ex.description, spec["description"])
            await _write(db, "exercise", ex_id, "hint", ex.hint or "", spec["hint"])
            await _write(db, "exercise", ex_id, "explanation", ex.explanation or "", spec.get("explanation", ""))
            if ex.expected_answer:
                await _write(db, "exercise", ex_id, "expected_answer", ex.expected_answer, spec.get("expected_answer", ""))

            print(f"lesson {lesson_id}: RU translation written (exercise {ex_id})")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
