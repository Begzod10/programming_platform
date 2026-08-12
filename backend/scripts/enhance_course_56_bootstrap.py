"""Enhance course 56 (Bootstrap 5 Asoslari) from ~2.5 to 4-5 star ambition.

Adds a real "🐛 Ataylab xato" gotcha to each of the 5 lessons (matching the
pattern used in the platform's 5-star courses) plus one reasoning exercise
per lesson tied directly to that gotcha. Idempotent: re-running is safe
because each append is keyed by a marker string checked before insertion.
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
    514: {  # Grid System
        "html": f"""<h3>{MARKER}</h3>
<p>Yangi boshlovchi shunday yozadi — va grid "buzilib" ketadi:</p>
<pre><code class="lang-html">&lt;div class="container"&gt;
  &lt;div class="col-md-4"&gt;Karta 1&lt;/div&gt;
  &lt;div class="col-md-4"&gt;Karta 2&lt;/div&gt;
  &lt;div class="col-md-4"&gt;Karta 3&lt;/div&gt;
&lt;/div&gt;</code></pre>
<p><strong>Natija:</strong> Kartalar chapga siljigan, container chetidan tashqariga chiqib ketadi (gorizontal scroll paydo bo'ladi). Sabab: <code>.col-*</code> klasslari <code>padding</code> orqali gutter yaratadi, buni <strong>faqat</strong> <code>.row</code>ning <code>margin: 0 -0.75rem</code> kompensatsiya qiladi. <code>.row</code> yo'q bo'lsa, padding hech narsa bilan kompensatsiya qilinmaydi va butun blok o'ngga-chapga siljib chiqib ketadi.</p>
<p><strong>To'g'ri yechim:</strong> <code>.col-*</code> — har doim <code>.row</code>ning bevosita farzandi bo'lishi shart: <code>.container &gt; .row &gt; .col-*</code>.</p>""",
        "exercise": {
            "title": "Nega .col-md-4 lar container'dan tashqariga chiqib ketadi?",
            "description": "<code>&lt;div class=\"container\"&gt;&lt;div class=\"col-md-4\"&gt;...&lt;/div&gt;&lt;/div&gt;</code> — .row o'tkazib yuborilgan. Nima uchun bu gorizontal scroll paydo qiladi?",
            "exercise_type": "multiple_choice",
            "options": '["col-md-4 klassi mavjud emas", ".row ning manfiy margin kompensatsiyasi yo\'q, shu uchun col padding tashqariga chiqadi", "container har doim col-4 talab qiladi", "Bootstrap CSS fayli yuklanmagan"]',
            "correct_answers": "B",
            "hint": ".row nima uchun kerakligini eslang — u faqat vizual emas, matematik kompensatsiya ham beradi.",
            "explanation": ".col-* o'ng-chap padding oladi (gutter uchun). .row bu padding'ni -0.75rem margin bilan tashqariga siljitib kompensatsiya qiladi. .row bo'lmasa, kompensatsiya yo'q va col'lar container chetidan tashqariga chiqadi.",
        },
    },
    515: {  # Components (dropdown/tooltip need Popper)
        "html": f"""<h3>{MARKER}</h3>
<p>Loyihaga faqat <code>bootstrap.min.js</code> (bundle emas) ulanган va dropdown/tooltip ishlamayapti:</p>
<pre><code class="lang-html">&lt;script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"&gt;&lt;/script&gt;
&lt;!-- dropdown tugmasi bosilsa — hech narsa chiqmaydi, konsolda xato --&gt;</code></pre>
<p><strong>Natija:</strong> Konsolda <code>Popper is not defined</code>. Dropdown, tooltip va popover komponentlari joylashuvni hisoblash uchun <strong>Popper.js</strong> kutubxonasiga muhtoj. <code>bootstrap.min.js</code> — Popper'siz "yalang'och" versiya; <code>bootstrap.bundle.min.js</code> esa Popper allaqachon ichiga o'ralgan versiya.</p>
<p><strong>To'g'ri yechim:</strong> Doim <code>bootstrap.bundle.min.js</code> ni ulang (agar Popper'ni alohida boshqarmasangiz).</p>""",
        "exercise": {
            "title": "Dropdown tugmasi bosilganda hech narsa chiqmayapti — sabab nima?",
            "description": "Loyihada faqat <code>bootstrap.min.js</code> ulanган, <code>bootstrap.bundle.min.js</code> emas. Dropdown ishlamayapti, konsolda 'Popper is not defined' xatosi bor. Nima uchun?",
            "exercise_type": "text_input",
            "expected_answer": "bootstrap.min.js Popper.js'ni o'z ichiga olmaydi. Dropdown/tooltip/popover joylashuvni hisoblash uchun Popper'ga muhtoj. bootstrap.bundle.min.js esa Popper allaqachon qo'shilgan versiya. Yechim: bundle versiyasini ulash yoki Popper'ni alohida CDN orqali qo'shish.",
            "hint": "'bundle' so'zi nimani anglatishini o'ylab ko'ring — ichiga nima 'o'ralgan'?",
            "explanation": "Bootstrap 5 JS komponentlari (dropdown, tooltip, popover) Popper.js'ga tayanadi. Bundle versiya buni ichiga oladi, oddiy versiya olmaydi.",
        },
    },
    516: {  # Modals — manual toggling leaves backdrop stuck
        "html": f"""<h3>{MARKER}</h3>
<p>O'quvchi modalni <code>data-bs-toggle</code> o'rniga qo'lda JS bilan ochadi va yopadi:</p>
<pre><code class="lang-javascript">// Modal'ni ochish (qo'lda)
document.querySelector('#myModal').classList.add('show');
document.querySelector('#myModal').style.display = 'block';

// "Yopish" tugmasi bosilganda
document.querySelector('#myModal').classList.remove('show');
document.querySelector('#myModal').style.display = 'none';</code></pre>
<p><strong>Natija:</strong> Modal vizual yopilganday ko'rinadi, lekin sahifa hali ham scroll bo'lmaydi va orqa fonda qorong'i qatlam (<code>.modal-backdrop</code>) qolib ketadi — chunki bu elementlarni Bootstrap'ning <code>Modal</code> JS klassi qo'shgan va olib tashlaydi, siz esa faqat <code>&lt;div id="myModal"&gt;</code>ning o'zini boshqardingiz.</p>
<p><strong>To'g'ri yechim:</strong> Har doim Bootstrap'ning o'z API'sidan foydalaning: <code>bootstrap.Modal.getInstance(el).hide()</code> yoki <code>data-bs-dismiss="modal"</code>.</p>""",
        "exercise": {
            "title": "Modalni qo'lda display:none qilib 'yopgandan' keyin sahifa nega hali ham scroll bo'lmayapti?",
            "description": "Dasturchi modalni JS bilan classList.add('show') orqali ochdi, keyin classList.remove('show') bilan 'yopdi'. Lekin sahifa hamon qorong'i, scroll ishlamayapti. Sababi nima?",
            "exercise_type": "multiple_choice",
            "options": '["CSS fayli yuklanmagan", ".modal-backdrop va body.modal-open klassini faqat Bootstrap Modal API qo\'shadi/olib tashlaydi, qo\'lda boshqarish buni chetlab o\'tadi", "Modal ID xato yozilgan", "JavaScript versiyasi eski"]',
            "correct_answers": "B",
            "hint": "Modal ochilganda faqat #myModal o'zi emas, boshqa 2 ta narsa ham qo'shiladi — ular qayerda?",
            "explanation": "Bootstrap Modal.show() chaqirilganda .modal-backdrop elementi document.body'ga qo'shiladi va body'ga modal-open klassi (overflow:hidden) beriladi. Bularni faqat Modal.hide() olib tashlaydi. Qo'lda display:none qilish bu ikkalasini chetlab o'tadi.",
        },
    },
    517: {  # Utility classes — mobile-first "and up" surprise
        "html": f"""<h3>{MARKER}</h3>
<p>Dasturchi "faqat md ekranda" yashirishni xohlaydi va shunday yozadi:</p>
<pre><code class="lang-html">&lt;div class="d-md-none"&gt;Faqat md'da yashirin bo'lishi kerak edi&lt;/div&gt;</code></pre>
<p><strong>Natija:</strong> Element md (768px) dan boshlab <strong>lg, xl, xxl</strong> — barcha kattaroq ekranlarda ham yashirin qoladi, faqat kichik (sm va undan kichik) ekranlarda ko'rinadi. Kutilgan "faqat md oralig'ida" xatti-harakat emas.</p>
<p><strong>Sabab:</strong> Bootstrap utility'lari mobile-first — <code>-md-</code> prefiksi "md va undan katta" degani, "faqat md" emas.</p>
<p><strong>To'g'ri yechim:</strong> Faqat bitta breakpoint oralig'ida yashirish uchun ikkita klass kerak: <code>d-none d-md-block d-lg-none</code>.</p>""",
        "exercise": {
            "title": "d-md-none nima uchun lg va xl ekranlarda ham elementni yashiradi?",
            "description": "<code>&lt;div class=\"d-md-none\"&gt;</code> yozilgan, maqsad — faqat md (768-991px) oralig'ida yashirish edi. Lekin lg va undan katta ekranlarda ham element ko'rinmayapti. Nega?",
            "exercise_type": "text_input",
            "expected_answer": "Bootstrap utility klasslari mobile-first: -md- prefiksi 'md va undan katta barcha ekranlar' degani, faqat md emas. d-md-none md dan boshlab hamma joyda none qiladi. Faqat md oralig'ida yashirish uchun d-none d-md-block d-lg-none kombinatsiyasi kerak.",
            "hint": "Bootstrap breakpoint prefikslari 'shu o'lchamdan boshlab' deb o'qiladi, 'faqat shu o'lchamda' emas.",
            "explanation": "Har bir breakpoint prefiksi (masalan -md-) 'min-width' media query bilan ishlaydi, ya'ni shu nuqtadan yuqoriga qarab qo'llanadi, faqat o'sha oraliqda emas.",
        },
    },
    518: {  # Real project — fixed sidebar overlap
        "html": f"""<h3>{MARKER}</h3>
<p>Admin dashboard'da sidebar <code>position: fixed</code> qilib qo'yilgan, lekin asosiy kontent bloki o'zgartirilmagan:</p>
<pre><code class="lang-html">&lt;div class="sidebar" style="position:fixed; width:250px; height:100vh;"&gt;...&lt;/div&gt;
&lt;div class="main-content"&gt;
  &lt;h1&gt;Dashboard&lt;/h1&gt;
  &lt;!-- Bootstrap kartalar shu yerda --&gt;
&lt;/div&gt;</code></pre>
<p><strong>Natija:</strong> <code>main-content</code>ning boshlang'ich 250px qismi sidebar ostida yashirinib qoladi — chunki <code>position: fixed</code> element normal document flow'dan butunlay chiqib ketadi, boshqa elementlar uning bor-yo'qligini "bilmaydi".</p>
<p><strong>To'g'ri yechim:</strong> <code>main-content</code>ga <code>margin-left: 250px</code> (yoki Bootstrap grid bilan <code>col-md-2</code> sidebar + <code>col-md-10</code> content, ikkalasi ham normal flow'da) berish kerak.</p>""",
        "exercise": {
            "title": "Fixed sidebar qo'yilgandan keyin nega dashboard matni sidebar ostida yashirinib qoladi?",
            "description": "position: fixed bilan 250px sidebar qo'yildi, main-content'ga hech qanday margin berilmadi. Natijada kontentning chap qismi sidebar orqasida ko'rinmay qoladi. Nega?",
            "exercise_type": "multiple_choice",
            "options": '["Bootstrap eskirgan versiyada", "position: fixed element normal flow\'dan chiqadi, boshqa elementlar joy ajratmaydi", "Sidebar width\'i noto\'g\'ri", "z-index kerak emas edi"]',
            "correct_answers": "B",
            "hint": "Fixed va absolute pozitsiyalash umumiy xususiyati — ular oqimga qanday ta'sir qiladi?",
            "explanation": "position: fixed (va absolute) elementlar normal document flow'dan chiqariladi — layout hisoblashda ular 'yo'q' deb hisoblanadi. Shuning uchun ularning ostida/yonida qolgan elementlarga qo'lda joy (margin/padding) ochib berish kerak.",
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
