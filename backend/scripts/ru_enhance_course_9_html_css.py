"""Russian translations for the enhance_course_9_html_css.py content additions.

Same approach as ru_enhance_course_56_bootstrap.py: take the existing cached
RU text_content/sections_json as a base and append the RU translation of the
new bug-marker block + new exercise.
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
    5: f"""<h3>{MARKER_RU}</h3>
<p>Ученик вкладывает <code>&lt;div&gt;</code> внутрь <code>&lt;p&gt;</code>:</p>
<pre><code class="lang-html">&lt;p&gt;Этот текст &lt;div&gt;вложенный div&lt;/div&gt; и снова текст&lt;/p&gt;</code></pre>
<p><strong>Результат:</strong> если проверить в DevTools, браузер сохраняет это <strong>не так, как вы написали</strong>! Он автоматически закрывает <code>&lt;p&gt;</code> перед <code>&lt;div&gt;</code> и открывает новый: <code>&lt;p&gt;Этот текст &lt;/p&gt;&lt;div&gt;...&lt;/div&gt;&lt;p&gt; и снова текст&lt;/p&gt;</code>. Причина: по правилам HTML5 внутрь <code>&lt;p&gt;</code> нельзя вкладывать блочные элементы (<code>div</code>, <code>h1</code>, <code>ul</code> и т.д.) — браузер это "исправляет".</p>
<p><strong>Правильное решение:</strong> внутри <code>&lt;p&gt;</code> должны быть только inline-элементы (<code>span</code>, <code>a</code>, <code>strong</code>); для блочного контента используйте <code>&lt;div&gt;</code>.</p>""",
    7: f"""<h3>{MARKER_RU}</h3>
<p>Ученик присваивает один и тот же <code>id</code> нескольким элементам (часто из-за копипаста):</p>
<pre><code class="lang-html">&lt;button id="btn"&gt;Сохранить&lt;/button&gt;
&lt;button id="btn"&gt;Отменить&lt;/button&gt;

&lt;script&gt;
document.getElementById('btn').addEventListener('click', () =&gt; alert('нажато'));
&lt;/script&gt;</code></pre>
<p><strong>Результат:</strong> CSS применяет стиль к обеим кнопкам (браузер "не возражает"), но <code>getElementById('btn')</code> возвращает <strong>только первый</strong> элемент — вторая кнопка не получает обработчик события, и при клике ничего не происходит. Эта ошибка может долго оставаться незамеченной, потому что визуально всё выглядит правильно.</p>
<p><strong>Правильное решение:</strong> <code>id</code> используется на странице <strong>только один раз</strong>. Если нужен один стиль для нескольких элементов — используйте <code>class</code>.</p>""",
    8: f"""<h3>{MARKER_RU}</h3>
<p>Ученик ставит 3 карточки <code>inline-block</code> в ряд:</p>
<pre><code class="lang-html">&lt;div class="card"&gt;1&lt;/div&gt;
&lt;div class="card"&gt;2&lt;/div&gt;
&lt;div class="card"&gt;3&lt;/div&gt;

&lt;style&gt;
.card {{ display: inline-block; width: 33.33%; }}
&lt;/style&gt;</code></pre>
<p><strong>Результат:</strong> три карточки <strong>не помещаются</strong> в общие 100%, третья съезжает на новую строку! Причина — <strong>пробел (перенос строки)</strong> между карточками в HTML-коде превращается в реальный отступ для <code>inline-block</code> элементов (примерно 4px между каждой) — точно так же, как пробел между словами. 3 × 33.33% + 2 отступа &gt; 100%.</p>
<p><strong>Правильное решение:</strong> убрать пробелы между тегами в HTML (<code>&lt;div&gt;1&lt;/div&gt;&lt;div&gt;2&lt;/div&gt;</code>), либо задать <code>font-size: 0</code> родителю, либо (лучший вариант) перейти на <code>display: flex</code>.</p>""",
    10: f"""<h3>{MARKER_RU}</h3>
<p>Ученик ставит два <code>div</code> рядом через <code>float: left</code>:</p>
<pre><code class="lang-html">&lt;div class="konteyner" style="border: 2px solid black;"&gt;
  &lt;div style="float:left; width:200px; height:150px; background:lightblue;"&gt;Слева&lt;/div&gt;
  &lt;div style="float:left; width:200px; height:150px; background:lightcoral;"&gt;Справа&lt;/div&gt;
&lt;/div&gt;
&lt;p&gt;Этот текст должен был быть под контейнером&lt;/p&gt;</code></pre>
<p><strong>Результат:</strong> чёрная рамка <code>.konteyner</code> становится <strong>высотой 0</strong> — как будто внутри ничего нет! А <code>&lt;p&gt;</code> ниже "заезжает" поверх карточек. Причина: <code>float</code>-элементы выходят из обычного потока, родитель <strong>не учитывает</strong> их высоту ("схлопывание").</p>
<p><strong>Правильное решение:</strong> задать родителю <code>overflow: hidden</code> (или классическую технику "clearfix") — это заставляет родителя "охватывать" плавающих потомков.</p>""",
    11: f"""<h3>{MARKER_RU}</h3>
<p>Ученик кладёт в flex-контейнер карточку с длинным текстом и надеется на <code>flex-shrink</code>:</p>
<pre><code class="lang-html">&lt;div style="display:flex; width:300px;"&gt;
  &lt;div style="flex: 1;"&gt;Коротко&lt;/div&gt;
  &lt;div style="flex: 1;"&gt;ОченьОченьДлинноеСловоКотороеДолжноПереноситьсяНоНеПереносится&lt;/div&gt;
&lt;/div&gt;</code></pre>
<p><strong>Результат:</strong> вторая карточка <strong>не сжимается</strong> и вылезает за пределы контейнера (появляется горизонтальный скролл) — несмотря на <code>flex: 1</code>! Причина: у flex-элементов по умолчанию <code>min-width: auto</code>, то есть они <strong>не могут сжаться меньше своего контента</strong>. Одно длинное (неразрывное) слово задаёт минимальную ширину элемента.</p>
<p><strong>Правильное решение:</strong> задать <code>min-width: 0</code> (или <code>overflow-wrap: break-word</code>) — это позволяет flex-элементу сжиматься меньше своего контента.</p>""",
    13: f"""<h3>{MARKER_RU}</h3>
<p>Ученик хочет добавить иконку через <code>::before</code>, но ничего не появляется:</p>
<pre><code class="lang-css">.karta::before {{
  width: 20px;
  height: 20px;
  background: red;
  display: block;
}}</code></pre>
<p><strong>Результат:</strong> на экране <strong>нет красного квадрата</strong> — хотя width, height и background написаны верно! Причина: псевдоэлементы <code>::before</code> и <code>::after</code> вообще <strong>не добавляются</strong> в DOM, пока не указано свойство <code>content</code> — для браузера их "не существует".</p>
<p><strong>Правильное решение:</strong> добавить <code>content: "";</code> (даже если пустая строка) — это обязательно для "создания" псевдоэлемента.</p>""",
    15: f"""<h3>{MARKER_RU}</h3>
<p>Ученик хочет, чтобы карточка после нажатия кнопки сдвинулась вправо и <strong>осталась в этом положении</strong>:</p>
<pre><code class="lang-css">@keyframes surish {{
  from {{ transform: translateX(0); }}
  to {{ transform: translateX(200px); }}
}}
.karta {{
  animation: surish 1s ease;
}}</code></pre>
<p><strong>Результат:</strong> анимация красиво проигрывается, но по завершении карточка <strong>мгновенно "прыгает" обратно</strong> в исходное положение! Причина: CSS-анимация по умолчанию — лишь временный визуальный эффект: после завершения браузер возвращает элемент в исходное (доанимационное) состояние, если не указано иное.</p>
<p><strong>Правильное решение:</strong> добавить <code>animation-fill-mode: forwards;</code> — это указывает элементу остаться в состоянии <strong>последнего кадра</strong> анимации.</p>""",
}

NEW_EXERCISES_RU = {
    5: {
        "exercise_id": None,  # filled at runtime by matching title
        "uz_title": "`<p>` ichiga `<div>` qo'yilsa, brauzer nima qiladi?",
        "title": "Что делает браузер, если `<div>` вложен внутрь `<p>`?",
        "description": "Код <code>&lt;p&gt;Текст &lt;div&gt;внутри&lt;/div&gt; снова текст&lt;/p&gt;</code> при проверке в DevTools браузера сохраняется иначе, чем вы его написали. Почему?",
        "options": '["Браузер выдаёт ошибку, страница не загружается", "Внутрь &lt;p&gt; нельзя вкладывать блочный элемент, браузер автоматически закрывает &lt;p&gt; и разбивает его на два", "div автоматически превращается в span", "Ничего не меняется, код работает точно как написан"]',
        "correct_answers": "B",
        "hint": "Вспомните, какие элементы может содержать тег &lt;p&gt;.",
        "explanation": "По спецификации HTML5 &lt;p&gt; принимает только 'phrasing content' (inline-элементы). Если встречается блочный элемент, браузер автоматически закрывает &lt;p&gt; и перестраивает DOM.",
    },
    7: {
        "exercise_id": None,
        "uz_title": "Bitta id ikkita tugmaga qo'yilsa, nima uchun ikkinchi tugma bosilganda hech narsa bo'lmaydi?",
        "title": "Почему при одинаковом id у двух кнопок вторая не реагирует на клик?",
        "description": "Обеим &lt;button&gt; присвоен id=\"btn\", затем через document.getElementById('btn') добавлен обработчик клика. Первая кнопка работает, вторая — нет. Почему?",
        "expected_answer": "id должен быть уникальным на странице. getElementById возвращает только ПЕРВЫЙ подходящий элемент в DOM, поэтому обработчик привязывается только к нему. Вторая кнопка не получает обработчик. Решение: дать каждой кнопке свой id, либо использовать class + querySelectorAll.",
        "hint": "Сколько элементов возвращает getElementById — один или несколько?",
        "explanation": "getElementById по спецификации возвращает первый найденный элемент, игнорируя остальные — а CSS применяет стиль ко всем совпадающим элементам, из-за этой разницы ошибка остаётся незаметной.",
    },
    8: {
        "exercise_id": None,
        "uz_title": "3 ta inline-block karta (har biri 33.33%) nega bitta qatorga sig'maydi?",
        "title": "Почему 3 карточки inline-block (по 33.33% каждая) не помещаются в одну строку?",
        "description": "В HTML между .card div есть перенос строки/пробел. Каждой задано width:33.33%, но 3-я карточка съезжает на новую строку. В чём причина?",
        "options": '["33.33% x 3 = 99.99%, недостаточно", "Пробел/перенос строки в HTML-коде превращается в реальный отступ между inline-block элементами", "inline-block не принимает width", "Ошибка браузера, у всех браузеров по-разному"]',
        "correct_answers": "B",
        "hint": "inline-block ведёт себя как слова в тексте — что находится между словами?",
        "explanation": "inline-block элементы ведут себя как слова в текстовом потоке: пробел/перенос строки в исходном коде превращается в отступ примерно в один символ. Несколько таких отступов увеличивают общую ширину сверх 100%.",
    },
    10: {
        "exercise_id": None,
        "uz_title": "Nega ichida 2 ta float qilingan div bor konteynerning balandligi 0 bo'lib qoladi?",
        "title": "Почему высота контейнера с двумя float-элементами внутри становится равной 0?",
        "description": "Внутри .konteyner два div с float:left (высотой 150px каждый), но сам контейнер отображается высотой 0px. Почему?",
        "expected_answer": "float-элементы выходят из обычного потока документа. Родительский элемент (если сам не находится в float или другом режиме компоновки) не учитывает высоту таких потомков при расчёте собственной высоты — происходит 'схлопывание' до 0px. Решение: задать родителю overflow:hidden или применить clearfix.",
        "hint": "float выводит элемент из потока. Родитель об этом 'не знает'.",
        "explanation": "Это классическая проблема 'схлопывания float' — одна из самых распространённых ловушек CSS, поэтому для неё специально придумана техника clearfix.",
    },
    11: {
        "exercise_id": None,
        "uz_title": "flex:1 berilgan bo'lsa ham, nega uzun so'zli karta siqilmay tashqariga chiqib ketadi?",
        "title": "Почему при flex:1 карточка с длинным словом всё равно вылезает за пределы контейнера?",
        "description": "Обоим flex-потомкам задано flex:1, но карточка с длинным (неразрывным) словом вылезает за пределы контейнера. Почему flex-shrink не срабатывает?",
        "options": '["flex:1 не задаёт значение shrink", "У flex-элементов по умолчанию min-width:auto, что не даёт им сжаться меньше своего контента", "Длинное слово считается ошибкой CSS", "display:flex написан неверно"]',
        "correct_answers": "B",
        "hint": "Какой должна быть МИНИМАЛЬНАЯ ширина элемента, чтобы flex-shrink сработал?",
        "explanation": "Сокращение flex: 1 задаёт flex-grow:1, flex-shrink:1, flex-basis:0 — но стандартное значение min-width:auto оказывается сильнее и не даёт элементу сжаться меньше своего контента (длинного слова).",
    },
    13: {
        "exercise_id": None,
        "uz_title": "width/height/background yozilgan bo'lsa ham, nega ::before hech narsa ko'rsatmaydi?",
        "title": "Почему ::before ничего не показывает, даже если заданы width/height/background?",
        "description": ".karta::before{width:20px; height:20px; background:red; display:block;} написано, но на экране ничего не видно. Чего не хватает?",
        "correct_answers": "content",
        "hint": "Есть одно специальное свойство, которое 'создаёт' псевдоэлемент ::before/::after в DOM.",
        "explanation": "Если свойство content не задано, браузер вообще не создаёт псевдоэлемент ::before/::after — он не существует в DOM, поэтому никакие другие стили не видны. content: \"\"; обязателен, даже если пустой.",
    },
    15: {
        "exercise_id": None,
        "uz_title": "Animatsiya tugagach, nega element boshlang'ich joyiga sakrab qaytadi?",
        "title": "Почему после окончания анимации элемент прыгает обратно в исходное положение?",
        "description": "Написана @keyframes с translateX(200px), задано animation:surish 1s ease. Анимация красиво работает, но по завершении элемент сразу возвращается на старое место. Почему, и как это исправить?",
        "expected_answer": "CSS-анимация по умолчанию — лишь временный эффект: по завершении браузер возвращает элемент в состояние до анимации. Исправление: добавить animation-fill-mode: forwards; — это гарантирует, что элемент останется в состоянии последнего кадра.",
        "hint": "Есть свойство, которое определяет, в каком состоянии элемент остаётся 'после' завершения анимации.",
        "explanation": "Значение animation-fill-mode по умолчанию — 'none': вне времени анимации элемент не сохраняет никакой стиль из неё. Значение 'forwards' заставляет сохранить стиль последнего keyframe.",
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
            uz_ex_dict = next(e for e in uz_exercise_section["exercises"] if e["title"] == spec["uz_title"])
            ex_id = uz_ex_dict["id"]
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
