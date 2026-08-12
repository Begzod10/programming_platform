"""Enhance course 9 (HTML CSS, beginner) from ~2 to 4-5 star ambition.

Adds a real "🐛 Ataylab xato" gotcha to 7 of 11 lessons plus one reasoning
exercise per lesson tied directly to that gotcha, matching the pattern used
in the platform's 5-star courses. Idempotent — checks for the marker/title
before writing.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from enhance_lesson_helpers import append_bug_marker, add_exercise, sync_exercise_section  # noqa: E402

MARKER = "🐛 Ataylab xato"

BUGS = {
    5: {  # Teglar bilan ishlash
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi <code>&lt;p&gt;</code> ichiga <code>&lt;div&gt;</code> joylaydi:</p>
<pre><code class="lang-html">&lt;p&gt;Bu matn &lt;div&gt;ichkariga solingan div&lt;/div&gt; va yana matn&lt;/p&gt;</code></pre>
<p><strong>Natija:</strong> DevTools'da tekshirsangiz, brauzer buni <strong>siz yozgandek</strong> saqlamaydi! U avtomatik ravishda <code>&lt;p&gt;</code>ni <code>&lt;div&gt;</code>dan oldin yopib qo'yadi va yangi <code>&lt;p&gt;</code> ochadi: <code>&lt;p&gt;Bu matn &lt;/p&gt;&lt;div&gt;...&lt;/div&gt;&lt;p&gt; va yana matn&lt;/p&gt;</code>. Sabab: HTML5 qoidasiga ko'ra <code>&lt;p&gt;</code> ichiga blok darajali element (<code>div</code>, <code>h1</code>, <code>ul</code> va h.k.) joylashtirib bo'lmaydi — brauzer buni "tuzatib" qo'yadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>&lt;p&gt;</code> ichida faqat inline elementlar (<code>span</code>, <code>a</code>, <code>strong</code>) bo'lishi kerak; blok kontent uchun <code>&lt;div&gt;</code>dan foydalaning.</p>""",
        "exercise": {
            "title": "`<p>` ichiga `<div>` qo'yilsa, brauzer nima qiladi?",
            "description": "<code>&lt;p&gt;Matn &lt;div&gt;ichida&lt;/div&gt; yana matn&lt;/p&gt;</code> kodini brauzerda DevTools orqali tekshirsangiz, u sizning yozganingizdan farqli ko'rinishda saqlanadi. Nima uchun?",
            "exercise_type": "multiple_choice",
            "options": '["Brauzer xato beradi va sahifa yuklanmaydi", "&lt;p&gt; ichiga blok element joylashtirib bo\'lmaydi, brauzer &lt;p&gt;ni avtomatik yopib, uni ikkiga bo\'lib qo\'yadi", "div avtomatik span ga aylanadi", "Hech narsa o\'zgarmaydi, kod aynan yozilganidek ishlaydi"]',
            "correct_answers": "B",
            "hint": "&lt;p&gt; teg qanday turdagi elementlarni ichiga olishi mumkinligini eslang.",
            "explanation": "HTML5 spetsifikatsiyasiga ko'ra &lt;p&gt; faqat 'phrasing content' (inline elementlar)ni qabul qiladi. Blok element uchrasa, brauzer &lt;p&gt;ni avtomatik yopib, DOM'ni qayta tuzadi.",
        },
    },
    7: {  # Class va id
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi bir xil <code>id</code>ni bir nechta elementga qo'yadi (ko'pincha nusxa-joylashtirish natijasida):</p>
<pre><code class="lang-html">&lt;button id="btn"&gt;Saqlash&lt;/button&gt;
&lt;button id="btn"&gt;Bekor qilish&lt;/button&gt;

&lt;script&gt;
document.getElementById('btn').addEventListener('click', () =&gt; alert('bosildi'));
&lt;/script&gt;</code></pre>
<p><strong>Natija:</strong> CSS ikkala tugmaga ham stil beradi (brauzer bunga "e'tiroz bildirmaydi"), lekin <code>getElementById('btn')</code> <strong>faqat birinchi</strong> elementni qaytaradi — ikkinchi tugma hech qanday event listener olmaydi va bosilganda hech narsa bo'lmaydi. Bu xato uzoq vaqt sezilmasligi mumkin, chunki vizual ravishda hammasi to'g'ri ko'rinadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>id</code> — sahifada <strong>faqat bitta marta</strong> ishlatiladi. Bir nechta elementga bir xil stil kerak bo'lsa — <code>class</code> ishlating.</p>""",
        "exercise": {
            "title": "Bitta id ikkita tugmaga qo'yilsa, nima uchun ikkinchi tugma bosilganda hech narsa bo'lmaydi?",
            "description": "Ikkala &lt;button&gt;ga ham id=\"btn\" berilgan, keyin document.getElementById('btn') orqali click listener qo'shilgan. Birinchi tugma ishlaydi, ikkinchisi ishlamaydi. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "id sahifada noyob bo'lishi kerak. getElementById faqat DOM'dagi BIRINCHI mos elementni qaytaradi, shuning uchun faqat unga listener biriktiriladi. Ikkinchi tugma hech qanday listener olmaydi. Yechim: har biriga alohida id berish yoki class + querySelectorAll ishlatish.",
            "hint": "getElementById nechta element qaytaradi — bittami, ko'pmi?",
            "explanation": "getElementById spetsifikatsiya bo'yicha birinchi topilgan elementni qaytaradi, qolganlarini e'tiborsiz qoldiradi — CSS esa barcha mos elementlarga stil beraveradi, shu farq xatoni yashiradi.",
        },
    },
    8: {  # inline-block va span
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi 3 ta <code>inline-block</code> kartani yonma-yon qo'yadi:</p>
<pre><code class="lang-html">&lt;div class="card"&gt;1&lt;/div&gt;
&lt;div class="card"&gt;2&lt;/div&gt;
&lt;div class="card"&gt;3&lt;/div&gt;

&lt;style&gt;
.card {{ display: inline-block; width: 33.33%; }}
&lt;/style&gt;</code></pre>
<p><strong>Natija:</strong> Uchta karta <strong>umumiy 100% ga sig'may</strong>, uchinchisi keyingi qatorga tushib ketadi! Sabab — HTML manbadagi kartalar orasidagi <strong>bo'sh joy (yangi qator/probel)</strong> <code>inline-block</code> elementlar uchun haqiqiy bo'shliqqa aylanadi (taxminan 4px har biri orasida) — xuddi so'zlar orasidagi probel kabi. 3 ta karta × 33.33% + 2 ta bo'shliq &gt; 100%.</p>
<p><strong>To'g'ri yechim:</strong> HTML teglar orasidagi bo'sh joyni olib tashlash (<code>&lt;div&gt;1&lt;/div&gt;&lt;div&gt;2&lt;/div&gt;</code>), yoki ota elementga <code>font-size: 0</code> berish, yoki (eng yaxshisi) <code>display: flex</code>ga o'tish.</p>""",
        "exercise": {
            "title": "3 ta inline-block karta (har biri 33.33%) nega bitta qatorga sig'maydi?",
            "description": "HTML manbada .card divlar orasida yangi qator/probel bor. Har biriga width:33.33% berilgan, lekin 3-karta keyingi qatorga tushadi. Sababi nima?",
            "exercise_type": "multiple_choice",
            "options": '["33.33% x 3 = 99.99%, yetarli emas", "HTML manbadagi probel/yangi qator inline-block elementlar orasida haqiqiy bo\'shliqqa aylanadi", "inline-block width qabul qilmaydi", "Brauzer xatosi, barcha brauzerlarda turlicha"]',
            "correct_answers": "B",
            "hint": "inline-block so'zlarga o'xshab ishlaydi — so'zlar orasida nima bor?",
            "explanation": "inline-block elementlar matn oqimidagi so'zlar kabi ishlaydi: manbadagi probel/yangi qator brauzerda taxminan bitta belgi kengligidagi bo'shliqqa aylanadi. Bir nechta shunday bo'shliq umumiy kenglikni 100%dan oshirib yuboradi.",
        },
    },
    10: {  # Div tegi — float collapse
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi ikkita <code>div</code>ni <code>float: left</code> bilan yonma-yon qo'yadi:</p>
<pre><code class="lang-html">&lt;div class="konteyner" style="border: 2px solid black;"&gt;
  &lt;div style="float:left; width:200px; height:150px; background:lightblue;"&gt;Chap&lt;/div&gt;
  &lt;div style="float:left; width:200px; height:150px; background:lightcoral;"&gt;O'ng&lt;/div&gt;
&lt;/div&gt;
&lt;p&gt;Bu matn konteyner ostida bo'lishi kerak edi&lt;/p&gt;</code></pre>
<p><strong>Natija:</strong> <code>.konteyner</code>ning qora chegarasi <strong>balandligi 0</strong> bo'lib qoladi — go'yo ichida hech narsa yo'qday! Pastdagi <code>&lt;p&gt;</code> esa kartalar ustiga "chiqib" ketadi. Sabab: <code>float</code> qilingan elementlar normal oqimdan chiqadi, ota element ularning balandligini <strong>hisobga olmaydi</strong> ("collapse" muammosi).</p>
<p><strong>To'g'ri yechim:</strong> Ota elementga <code>overflow: hidden</code> berish (yoki klassik "clearfix" texnikasi) — bu ota elementni ichidagi float'langan farzandlarni "o'rab olishga" majbur qiladi.</p>""",
        "exercise": {
            "title": "Nega ichida 2 ta float qilingan div bor konteynerning balandligi 0 bo'lib qoladi?",
            "description": ".konteyner ichida 2 ta float:left div bor (har biri 150px balandlikda), lekin konteynerning o'zi 0px balandlikda ko'rinadi. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "float qilingan elementlar normal document flow'dan chiqib ketadi. Ota element (agar o'zi float yoki boshqa layout rejimida bo'lmasa) farzandlarining balandligini hisoblashda ularni e'tiborga olmaydi, shuning uchun 0px balandlikka 'yig'iladi'. Yechim: ota elementga overflow:hidden yoki clearfix berish.",
            "hint": "float — elementni oqimdan chiqarib yuboradi. Ota element bu haqda 'bilmaydi'.",
            "explanation": "Bu klassik 'float collapse' muammosi — CSS'ning eng ko'p uchraydigan tuzoqlaridan biri, shuning uchun clearfix texnikasi maxsus ixtiro qilingan.",
        },
    },
    11: {  # Flex — min-width:auto
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi flex konteyner ichiga uzun matnli kartochka qo'yadi va <code>flex-shrink</code>ka umid qiladi:</p>
<pre><code class="lang-html">&lt;div style="display:flex; width:300px;"&gt;
  &lt;div style="flex: 1;"&gt;Qisqa&lt;/div&gt;
  &lt;div style="flex: 1;"&gt;ExtraOrdinarilyLongWordThatShouldWrapButDoesnt&lt;/div&gt;
&lt;/div&gt;</code></pre>
<p><strong>Natija:</strong> Ikkinchi karta <strong>siqilmaydi</strong> va konteynerdan tashqariga chiqib ketadi (gorizontal scroll paydo bo'ladi) — <code>flex: 1</code> yozilgan bo'lsa ham! Sabab: flex elementlarning standart <code>min-width</code> qiymati <code>auto</code>, ya'ni ular <strong>kontentidan kichikroq siqilmaydi</strong>. Uzun bir so'z (bo'linmaydigan) elementning minimal kengligini belgilab qo'yadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>min-width: 0</code> (yoki <code>overflow-wrap: break-word</code>) berish — bu flex elementga o'z kontentidan ham kichikroq bo'lishga ruxsat beradi.</p>""",
        "exercise": {
            "title": "flex:1 berilgan bo'lsa ham, nega uzun so'zli karta siqilmay tashqariga chiqib ketadi?",
            "description": "Ikkala flex farzandga ham flex:1 berilgan, lekin ichida uzun (bo'linmaydigan) so'z bo'lgan karta konteynerdan tashqariga chiqadi. Nima uchun flex-shrink ishlamayapti?",
            "exercise_type": "multiple_choice",
            "options": '["flex:1 shrink qiymatini bermaydi", "Flex elementlarning standart min-width:auto qiymati ularni kontentidan kichikroq siqilishga yo\'l qo\'ymaydi", "Uzun so\'z CSS xatosi hisoblanadi", "display:flex noto\'g\'ri yozilgan"]',
            "correct_answers": "B",
            "hint": "flex-shrink ishlashi uchun elementning MINIMAL kengligi qancha bo'lishi kerak?",
            "explanation": "flex: 1 qisqartmasi flex-grow:1, flex-shrink:1, flex-basis:0 beradi — lekin brauzerning standart min-width:auto qiymati bularning barchasidan ustun turadi va elementni o'z kontenti (uzun so'z)dan kichikroq siqilishiga yo'l qo'ymaydi.",
        },
    },
    13: {  # before/after
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi <code>::before</code> bilan ikonka qo'shmoqchi bo'ladi, lekin hech narsa chiqmaydi:</p>
<pre><code class="lang-css">.karta::before {{
  width: 20px;
  height: 20px;
  background: red;
  display: block;
}}</code></pre>
<p><strong>Natija:</strong> Ekranda <strong>hech qanday qizil kvadrat yo'q</strong> — width, height, background hammasi to'g'ri yozilgan bo'lsa ham! Sabab: <code>::before</code> va <code>::after</code> pseudo-elementlari <code>content</code> xossasi yozilmaguncha DOM'ga <strong>umuman qo'shilmaydi</strong> — brauzer uchun ular "mavjud emas".</p>
<p><strong>To'g'ri yechim:</strong> <code>content: "";</code> (bo'sh qatorli bo'lsa ham) qo'shish — bu pseudo-elementni "yaratish" uchun majburiy.</p>""",
        "exercise": {
            "title": "width/height/background yozilgan bo'lsa ham, nega ::before hech narsa ko'rsatmaydi?",
            "description": ".karta::before{width:20px; height:20px; background:red; display:block;} yozilgan, lekin ekranda hech narsa ko'rinmaydi. Nima yetishmayapti?",
            "exercise_type": "fill_in_blank",
            "correct_answers": "content",
            "hint": "::before va ::after pseudo-elementni DOM'da 'yaratadigan' bitta maxsus xossa bor.",
            "explanation": "content xossasi yozilmasa, brauzer ::before/::after pseudo-elementini butunlay yaratmaydi — u DOM'da mavjud bo'lmaydi, shuning uchun boshqa hech qanday stil ko'rinmaydi. content: \"\"; yozish shart, hatto bo'sh bo'lsa ham.",
        },
    },
    15: {  # Animation fill-mode
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi tugma bosilganda kartochka o'ngga surilib, <strong>shu holatda qolishini</strong> xohlaydi:</p>
<pre><code class="lang-css">@keyframes surish {{
  from {{ transform: translateX(0); }}
  to {{ transform: translateX(200px); }}
}}
.karta {{
  animation: surish 1s ease;
}}</code></pre>
<p><strong>Natija:</strong> Animatsiya chiroyli ishlaydi, lekin <strong>tugagach karta darhol boshlang'ich joyiga "sakrab" qaytadi</strong>! Sabab: CSS animatsiyasi standart holatda faqat vaqtinchalik vizual effekt — animatsiya tugagandan so'ng brauzer elementni asl (animatsiyagacha bo'lgan) holatiga qaytaradi, agar boshqacha ko'rsatilmasa.</p>
<p><strong>To'g'ri yechim:</strong> <code>animation-fill-mode: forwards;</code> qo'shish — bu elementga animatsiyaning <strong>oxirgi kadridagi</strong> holatda qolishni buyuradi.</p>""",
        "exercise": {
            "title": "Animatsiya tugagach, nega element boshlang'ich joyiga sakrab qaytadi?",
            "description": "@keyframes bilan translateX(200px)ga suriladigan animatsiya yozilgan, animation:surish 1s ease berilgan. Animatsiya chiroyli ishlaydi, lekin tugagach element darhol eski joyiga qaytadi. Nega, va qanday tuzatiladi?",
            "exercise_type": "text_input",
            "expected_answer": "CSS animatsiyasi standart holatda faqat vaqtinchalik effekt — tugagach brauzer elementni animatsiyadan oldingi holatiga qaytaradi. Tuzatish: animation-fill-mode: forwards; qo'shish, bu element oxirgi keyframe holatida qolishini ta'minlaydi.",
            "hint": "Animatsiya 'tugagandan keyin' element qaysi holatda qolishi kerakligini belgilaydigan xossa bor.",
            "explanation": "animation-fill-mode standart qiymati 'none' — animatsiyadan tashqarida element hech qanday stilni saqlamaydi. 'forwards' qiymati oxirgi keyframe'dagi stilni saqlab qolishga majbur qiladi.",
        },
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, spec in BUGS.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()
            if MARKER in (lesson.text_content or ""):
                print(f"lesson {lesson_id}: bug marker already present, skipping content append")
            else:
                await append_bug_marker(db, lesson_id, spec["html"])
                print(f"lesson {lesson_id}: appended bug marker")

            ex_spec = spec["exercise"]
            already = (await db.execute(
                select(Exercise).where(Exercise.lesson_id == lesson_id,
                                        Exercise.title == ex_spec["title"])
            )).scalar_one_or_none()
            if already is None:
                await add_exercise(
                    db, lesson_id,
                    title=ex_spec["title"], description=ex_spec["description"],
                    exercise_type=ex_spec["exercise_type"], options=ex_spec.get("options"),
                    correct_answers=ex_spec.get("correct_answers"),
                    expected_answer=ex_spec.get("expected_answer"),
                    hint=ex_spec["hint"], explanation=ex_spec["explanation"],
                    difficulty_level="Medium", points=4,
                )
                print(f"lesson {lesson_id}: added exercise")
            else:
                print(f"lesson {lesson_id}: exercise already present, skipping insert")
            await sync_exercise_section(db, lesson_id)
            print(f"lesson {lesson_id}: synced exercise section")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
