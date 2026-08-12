"""Russian translation for the rewritten course 9 lesson id=8 (block/inline/
inline-block). Reuses the exercise section's existing RU translations
verbatim (untouched by the content fix) and only retranslates text/code."""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

LESSON_ID = 8

TEXT_RU = """\
<pre class="mermaid">
flowchart TB
    BLOCK["block: div h1 p"] -->|с новой строки| FULL["100% ширины, width/height задаются"]
    INLINE["inline: span a strong"] -->|в той же строке| CONTENT["только ширина текста, width/height не работают"]
    IB["inline-block"] -->|в той же строке| MIX["но width/height тоже работают"]
    DI["свойство display"] --> BLOCK
    DI --> INLINE
    DI --> IB
</pre>

<h2>📦 Block, Inline и Inline-block — все три вида</h2>
<p>Каждый HTML-элемент может вести себя в браузере <strong>тремя разными</strong> способами: <code>block</code>, <code>inline</code> или <code>inline-block</code>. Это управляется CSS-свойством <code>display</code>, и множество проблем с версткой возникает именно из-за незнания разницы между этими тремя.</p>

<h3>1. Block (Блочные) элементы</h3>
<p>Эти элементы занимают всю строку целиком — даже если есть место, они не позволяют разместить другой элемент рядом с собой.</p>
<ul>
<li>Всегда начинаются <strong>с новой строки</strong></li>
<li>Можно задавать <code>width</code> и <code>height</code></li>
<li><code>margin</code> и <code>padding</code> работают полностью со всех сторон</li>
<li>Примеры: <code>&lt;div&gt;</code>, <code>&lt;h1&gt;...&lt;h6&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;ul&gt;</code>, <code>&lt;li&gt;</code></li>
</ul>

<h3>2. Inline (Строчные) элементы</h3>
<p>Эти элементы занимают только необходимое им место, а остальное пространство остаётся для других элементов.</p>
<ul>
<li><strong>Не начинаются с новой строки</strong> — остаются в потоке текста</li>
<li><code>width</code> и <code>height</code> задать нельзя — браузер их игнорирует</li>
<li>Работают только левый-правый <code>margin</code>/<code>padding</code>, верхний-нижний не сдвигают layout</li>
<li>Примеры: <code>&lt;span&gt;</code>, <code>&lt;a&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;img&gt;</code></li>
</ul>

<h3>3. Inline-block — лучшее из обоих</h3>
<p>Элемент со свойством <code>display: inline-block</code> располагается в одной строке с другими элементами, как <strong>inline</strong>, но при этом принимает <code>width</code>, <code>height</code> и полные <code>margin</code>/<code>padding</code>, как <strong>block</strong>. Именно поэтому кнопки, карточки и элементы навигации часто делают <code>inline-block</code>.</p>
<pre><code>.tugma {
  display: inline-block; /* остаётся в строке, но получает размер */
  width: 140px;
  height: 40px;
  background: #3498db;
  color: white;
  text-align: center;
}</code></pre>

<h3>📊 Сравнение всех трёх</h3>
<table>
<tr><th>Свойство</th><th>block</th><th>inline</th><th>inline-block</th></tr>
<tr><td>Начинается с новой строки</td><td>✅ да</td><td>❌ нет</td><td>❌ нет</td></tr>
<tr><td>width/height задаются</td><td>✅ да</td><td>❌ нет</td><td>✅ да</td></tr>
<tr><td>Полный margin/padding</td><td>✅ да</td><td>❌ только лево-право</td><td>✅ да</td></tr>
<tr><td>Пример</td><td>&lt;div&gt;, &lt;p&gt;</td><td>&lt;span&gt;, &lt;a&gt;</td><td>кнопка, карточка</td></tr>
</table>

<h3>⚠️ Частая ошибка</h3>
<p>Задать <code>&lt;span&gt;</code> напрямую <code>width: 200px; height: 100px;</code> — браузер полностью игнорирует эти значения, потому что <code>span</code> — inline-элемент. Если нужно задать размер для <code>span</code>, обязательно нужно добавить <code>display: inline-block</code>:</p>
<pre><code>span {
  width: 200px;   /* ❌ не работает — span всё ещё inline */
  height: 100px;  /* ❌ не работает */
}

span.mos {
  display: inline-block; /* ✅ теперь width/height работают */
  width: 200px;
  height: 100px;
}</code></pre>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>block</code> — начинается с новой строки, width/height работают (div, h1, p)</li>
<li>✅ <code>inline</code> — остаётся в строке, width/height не работают (span, a, strong)</li>
<li>✅ <code>inline-block</code> — остаётся в строке, НО width/height тоже работают</li>
<li>✅ Если inline-элементу нужен размер — добавляется <code>display: inline-block</code></li>
<li>✅ Кнопки и карточки часто делают <code>inline-block</code></li>
</ul>
"""

CODE_RU = """\
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Урок 5: block, inline, inline-block</title>
  <style>
    .block-misol {
      background: lightblue;
      width: 250px;
      height: 60px;
    }
    .inline-misol {
      background: yellow;
      width: 250px;  /* игнорируется — span это inline */
      height: 60px;  /* игнорируется */
    }
    .inline-block-misol {
      display: inline-block; /* теперь width/height работают */
      background: lightgreen;
      width: 140px;
      height: 40px;
      text-align: center;
      margin: 0 8px;
    }
  </style>
</head>
<body>

  <div class="block-misol">Это block-элемент (div) — начинается с новой строки</div>

  <p>
    Внутри текста
    <span class="inline-misol">это inline (span)</span>
    продолжается — width/height не работают.
  </p>

  <span class="inline-block-misol">Кнопка 1</span>
  <span class="inline-block-misol">Кнопка 2</span>
  <!-- Обе "кнопки" остаются в одной строке, но имеют заданный размер -->

</body>
</html>
"""


async def main():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()

        old_ru_row = (await db.execute(select(TranslationCache).where(
            TranslationCache.entity_type == "lesson", TranslationCache.entity_id == LESSON_ID,
            TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
        ))).scalar_one()
        old_ru_tree = json.loads(old_ru_row.translated_text)
        ru_exercise_section = next(s for s in old_ru_tree if s["type"] == "exercise")

        await _write(db, "lesson", LESSON_ID, "text_content", lesson.text_content, TEXT_RU)

        tree = json.loads(lesson.sections_json)
        for section in tree:
            if section["type"] == "text":
                section["html"] = TEXT_RU
            elif section["type"] == "code":
                section["code"] = CODE_RU
            elif section["type"] == "exercise":
                section["exercises"] = ru_exercise_section["exercises"]
        translated_json = json.dumps(tree, ensure_ascii=False)
        await _write(db, "lesson", LESSON_ID, "sections_json", lesson.sections_json, translated_json)

        await db.commit()
        print(f"Lesson {LESSON_ID}: RU text_content + sections_json rewritten "
              f"(exercises' existing RU translations preserved unchanged)")


if __name__ == "__main__":
    asyncio.run(main())
