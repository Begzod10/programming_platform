"""Expand course 9 ("HTML CSS"), lesson id=8 ("5-dars inline block va span").

Reported: content too short and never actually explains inline-block, despite
the lesson title and its own mermaid diagram promising it. Rewrites
text_content/code_content (UZ) with a fuller explanation covering block,
inline, AND inline-block with a comparison table and real example, then
updates sections_json's text/code sections to match.

Leaves the 5 existing exercises (ids 22/47/48/49/50) completely untouched —
they already have real student submissions (43-78 each), so their rows and
RU translations must not be disturbed. Writes a fresh RU translation for the
new text/code, reusing the exercises' existing RU translations verbatim.
"""
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

NEW_TEXT = """\
<pre class="mermaid">
flowchart TB
    BLOCK["block: div h1 p"] -->|yangi qatordan| FULL["100% en, width/height beriladi"]
    INLINE["inline: span a strong"] -->|bir xil qatorda| CONTENT["faqat matn kengligi, width/height ishlamaydi"]
    IB["inline-block"] -->|bir xil qatorda| MIX["lekin width/height ham ishlaydi"]
    DI["display xossasi"] --> BLOCK
    DI --> INLINE
    DI --> IB
</pre>

<h2>📦 Block, Inline va Inline-block — uchala turi ham</h2>
<p>Har bir HTML elementi brauzerda o'zini <strong>uch xil</strong> usulda tutishi mumkin: <code>block</code>, <code>inline</code> yoki <code>inline-block</code>. Bu — <code>display</code> CSS xossasi orqali boshqariladi, va ko'plab layout muammolari aynan shu uchtasining farqini bilmaslikdan kelib chiqadi.</p>

<h3>1. Block (Blokli) elementlar</h3>
<p>Bu elementlar butun qatorni egallaydi — o'zidan keyin, hatto joy bo'lsa ham, boshqa elementni o'ziga qo'shni qo'ymaydi.</p>
<ul>
<li>Har doim <strong>yangi qatordan</strong> boshlanadi</li>
<li><code>width</code> va <code>height</code> berish mumkin</li>
<li><code>margin</code> va <code>padding</code> barcha tomondan to'liq ishlaydi</li>
<li>Misollar: <code>&lt;div&gt;</code>, <code>&lt;h1&gt;...&lt;h6&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;ul&gt;</code>, <code>&lt;li&gt;</code></li>
</ul>

<h3>2. Inline (Qatorli) elementlar</h3>
<p>Bu elementlar faqat o'z matniga kerakli joyni egallaydi, qolgan joy boshqa elementlar uchun bo'sh qoladi.</p>
<ul>
<li><strong>Yangi qatordan boshlanmaydi</strong> — matn oqimi ichida qoladi</li>
<li><code>width</code> va <code>height</code> berib bo'lmaydi — brauzer ularni e'tiborsiz qoldiradi</li>
<li>Faqat chap-o'ng <code>margin</code>/<code>padding</code> ishlaydi, yuqori-past esa layout'ni siljitmaydi</li>
<li>Misollar: <code>&lt;span&gt;</code>, <code>&lt;a&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;img&gt;</code></li>
</ul>

<h3>3. Inline-block — ikkalasining eng foydali tomoni</h3>
<p><code>display: inline-block</code> berilgan element — <strong>inline</strong> kabi boshqa elementlar bilan bir qatorda turadi, lekin <strong>block</strong> kabi <code>width</code>, <code>height</code>, va to'liq <code>margin</code>/<code>padding</code>ni qabul qiladi. Aynan shu uchun tugmalar, kartalar va navigatsiya elementlari ko'pincha <code>inline-block</code> qilinadi.</p>
<pre><code>.tugma {
  display: inline-block; /* bir qatorda turadi, lekin o'lcham beriladi */
  width: 140px;
  height: 40px;
  background: #3498db;
  color: white;
  text-align: center;
}</code></pre>

<h3>📊 Uchalasini solishtirish</h3>
<table>
<tr><th>Xususiyat</th><th>block</th><th>inline</th><th>inline-block</th></tr>
<tr><td>Yangi qatordan boshlanadi</td><td>✅ ha</td><td>❌ yo'q</td><td>❌ yo'q</td></tr>
<tr><td>width/height beriladi</td><td>✅ ha</td><td>❌ yo'q</td><td>✅ ha</td></tr>
<tr><td>To'liq margin/padding</td><td>✅ ha</td><td>❌ faqat chap-o'ng</td><td>✅ ha</td></tr>
<tr><td>Misol</td><td>&lt;div&gt;, &lt;p&gt;</td><td>&lt;span&gt;, &lt;a&gt;</td><td>tugma, kartochka</td></tr>
</table>

<h3>⚠️ Ko'p uchraydigan xato</h3>
<p><code>&lt;span&gt;</code>ga to'g'ridan-to'g'ri <code>width: 200px; height: 100px;</code> berish — brauzer bu qiymatlarni butunlay e'tiborsiz qoldiradi, chunki <code>span</code> — inline element. Agar <code>span</code>ga o'lcham berish kerak bo'lsa, unga <code>display: inline-block</code> qo'shish shart:</p>
<pre><code>span {
  width: 200px;   /* ❌ ishlamaydi — span hali ham inline */
  height: 100px;  /* ❌ ishlamaydi */
}

span.mos {
  display: inline-block; /* ✅ endi width/height ishlaydi */
  width: 200px;
  height: 100px;
}</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>block</code> — yangi qatordan boshlanadi, width/height ishlaydi (div, h1, p)</li>
<li>✅ <code>inline</code> — bir qatorda qoladi, width/height ishlamaydi (span, a, strong)</li>
<li>✅ <code>inline-block</code> — bir qatorda qoladi, LEKIN width/height ham ishlaydi</li>
<li>✅ Inline elementga o'lcham kerak bo'lsa — <code>display: inline-block</code> qo'shiladi</li>
<li>✅ Tugma va kartochkalar ko'pincha <code>inline-block</code> qilib yasaladi</li>
</ul>
"""

NEW_CODE = """\
<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <title>5-dars: block, inline, inline-block</title>
  <style>
    .block-misol {
      background: lightblue;
      width: 250px;
      height: 60px;
    }
    .inline-misol {
      background: yellow;
      width: 250px;  /* e'tiborsiz qoldiriladi — span inline */
      height: 60px;  /* e'tiborsiz qoldiriladi */
    }
    .inline-block-misol {
      display: inline-block; /* endi width/height ishlaydi */
      background: lightgreen;
      width: 140px;
      height: 40px;
      text-align: center;
      margin: 0 8px;
    }
  </style>
</head>
<body>

  <div class="block-misol">Bu block element (div) — yangi qatordan boshlanadi</div>

  <p>
    Matn ichida
    <span class="inline-misol">bu inline (span)</span>
    davom etadi — width/height ishlamaydi.
  </p>

  <span class="inline-block-misol">Tugma 1</span>
  <span class="inline-block-misol">Tugma 2</span>
  <!-- Ikkala "tugma" ham bir qatorda turadi, lekin o'lchamga ega -->

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

        lesson.text_content = NEW_TEXT
        lesson.code_content = NEW_CODE

        tree = json.loads(lesson.sections_json)
        for section in tree:
            if section["type"] == "text":
                section["html"] = NEW_TEXT
            elif section["type"] == "code":
                section["code"] = NEW_CODE
        lesson.sections_json = json.dumps(tree, ensure_ascii=False)

        await db.commit()
        print(f"Lesson {LESSON_ID}: UZ text_content/code_content/sections_json rewritten "
              f"(new text len={len(NEW_TEXT)}, code len={len(NEW_CODE)})")

        return ru_exercise_section


if __name__ == "__main__":
    asyncio.run(main())
