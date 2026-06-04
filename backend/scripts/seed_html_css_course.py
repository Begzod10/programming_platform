"""Seed the "HTML CSS" beginner course (11 lessons + ~56 exercises).

Generated from the existing DB content (course id=9) and augmented with:
  - hero Mermaid diagrams (11 lessons)
  - project tasks for the 10 lessons that lacked one
  - 2 extra exercises for L3 (Class id) — was 3, now 5
  - 1 extra exercise for L8 (position) — was 4, now 5
  - L2 title trailing-space fix

Usage:
    cd backend
    python scripts/seed_html_css_course.py
    # add --dry-run to preview without writing

For updating an existing course in-place (preserving student progress)
use refresh_html_css_text.py instead.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


COURSE = {
    "title": "HTML CSS",
    "description": "HTML (HyperText Markup Language) va CSS (Cascading Style Sheets) — zamonaviy veb-saytlarni yaratishning asosi hisoblangan ikkita asosiy texnologiyadir.",
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 4,
    "max_points": 100,
    "is_active": True,
    "is_published": True,
}


L0_TEXT = """\
<pre class="mermaid">
flowchart LR
    H["HTML structure tags"] -->|content| B["Browser"]
    C["CSS styles"] -->|appearance| B
    J["JavaScript"] -.->|behavior| B
    B --> WEB["Web sahifa"]
</pre>

<h2 data-path-to-node="2">🌐 IT va Dasturlash nima?</h2><p data-path-to-node="3"><b data-path-to-node="3" data-index-in-node="0">IT (Axborot Texnologiyalari)</b> — bu ma'lumotlarni saqlash, qayta ishlash va uzatish bilan bog'liq barcha sohalar (kompyuterlar, internet, xavfsizlik).
<b data-path-to-node="3" data-index-in-node="149">Dasturlash</b> esa kompyuterga ma'lum bir vazifani bajarishi uchun "ko'rsatma" berish jarayonidir. Siz o'rganayotgan tillar aynan shu "ko'rsatmalar"ni yozish uchun xizmat qiladi.</p><hr data-path-to-node="4"><h2 data-path-to-node="5">🎨 Frontend: Saytning tashqi ko'rinishi</h2><p data-path-to-node="6">Bu qismda siz foydalanuvchi ko'radigan vizual qismlarni yasaysiz.</p><ul data-path-to-node="7"><li><p data-path-to-node="7,0,0"><b data-path-to-node="7,0,0" data-index-in-node="0">HTML (HyperText Markup Language):</b> Saytning "skeleti". Masalan, matn qayerda turishi, rasm qayerga qo'yilishi va tugmalarning joylashishini belgilaydi.</p></li><li><p data-path-to-node="7,1,0"><b data-path-to-node="7,1,0" data-index-in-node="0">CSS (Cascading Style Sheets):</b> Saytning "kiyimi" yoki dizayni. Ranglar, shriftlar, masofalar va chiroyli effektlar aynan CSS orqali beriladi.</p></li><li><p data-path-to-node="7,2,0"><b data-path-to-node="7,2,0" data-index-in-node="0">SASS:</b> Bu CSS’ning "kuchaytirilgan" versiyasi. U kodni tezroq va tartibliroq yozishga yordam beradi (Professional dizaynerlar asbobidir).</p></li><li><p data-path-to-node="7,3,0"><b data-path-to-node="7,3,0" data-index-in-node="0">JavaScript (JS):</b> Saytning "miyasi". Saytni jonlantiradi. Masalan, tugma bosilganda oyna ochilishi yoki ma'lumotlar o'zgarishi JS orqali amalga oshadi.</p></li></ul><hr data-path-to-node="8"><h2 data-path-to-node="9">🐍 Backend: Saytning ichki logikasi va Python</h2><p data-path-to-node="10">Bu qism foydalanuvchiga ko'rinmaydi, lekin barcha asosiy ishlar shu yerda bo'ladi.</p><ul data-path-to-node="11"><li><p data-path-to-node="11,0,0"><b data-path-to-node="11,0,0" data-index-in-node="0">Python:</b> Dunyodagi eng mashhur va o'rganishga oson dasturlash tili. U orqali sun'iy intelekt, veb-saytlar va turli dasturlar yaratiladi.</p></li><li><p data-path-to-node="11,1,0"><b data-path-to-node="11,1,0" data-index-in-node="0">Telegram Bot:</b> Python yordamida yaratiladigan avtomatik yordamchilar. Ular foydalanuvchi bilan muloqot qiladi, buyurtmalar qabul qiladi yoki ma'lumot beradi.</p></li><li><p data-path-to-node="11,2,0"><b data-path-to-node="11,2,0" data-index-in-node="0">Flask:</b> Bu Python uchun "mikro-freymvork". Uning yordamida juda tez va osonlik bilan veb-saytlarning orqa qismini (serverini) qurish mumkin.</p></li></ul><hr data-path-to-node="12"><h2 data-path-to-node="13">💡 Xulosa: Qanday ishlaydi?</h2><p data-path-to-node="14">Tasavvur qiling, siz <b data-path-to-node="14" data-index-in-node="21">uy</b> qurayapsiz:</p><ol start="1" data-path-to-node="15"><li><p data-path-to-node="15,0,0"><b data-path-to-node="15,0,0" data-index-in-node="0">HTML</b> — Uyning poydevori va devorlari.</p></li><li><p data-path-to-node="15,1,0"><b data-path-to-node="15,1,0" data-index-in-node="0">CSS/SASS</b> — Devorlarning rangi, pardalar va dizayn.</p></li><li><p data-path-to-node="15,2,0"><b data-path-to-node="15,2,0" data-index-in-node="0">JS</b> — Uyning chirog'ini yoqadigan tugmalar va eshik qo'ng'irog'i.</p></li><li><p data-path-to-node="15,3,0"><b data-path-to-node="15,3,0" data-index-in-node="0">Python/Flask</b> — Uyning isitish tizimi, suv quvurlari va xavfsizlik tizimi (ya'ni ichki motori).</p></li><li><p data-path-to-node="15,4,0"><b data-path-to-node="15,4,0" data-index-in-node="0">Telegram Bot</b> — Uyga kelgan mehmonlarga avtomatik javob beradigan robot-darvozabon.</p></li></ol>
"""

L0_CODE = """\

"""

L1_TEXT = """\
<pre class="mermaid">
flowchart TB
    DOC["DOCTYPE html"] --> HTML["html"]
    HTML --> HEAD["head meta title link"]
    HTML --> BODY["body"]
    BODY --> SH["h1 h2 h3 sarlavhalar"]
    BODY --> P["p paragraph"]
    BODY --> A["a link"]
    BODY --> IMG["img"]
    BODY --> LIST["ul ol li"]
</pre>

<h2 data-path-to-node="2">🏗️ HTML Teqi nima?</h2><p data-path-to-node="3"><b data-path-to-node="3" data-index-in-node="0">Teg (Tag)</b> — bu brauzerga (masalan, Chrome yoki Safari) ma'lumotni qanday ko'rsatish kerakligini aytadigan maxsus buyruqdir. Teglar har doim burchakli qavslar <code data-path-to-node="3" data-index-in-node="158">&lt; &gt;</code> ichida yoziladi.</p><ul data-path-to-node="4"><li><p data-path-to-node="4,0,0">Odatda ular juft bo'ladi: ochuvchi teg <code data-path-to-node="4,0,0" data-index-in-node="39">&lt;tag&gt;</code> va yopuvchi teg <code data-path-to-node="4,0,0" data-index-in-node="61">&lt;/tag&gt;</code>.</p></li><li><p data-path-to-node="4,1,0">Ular orasida esa biz ko'rmoqchi bo'lgan ma'lumot bo'ladi.</p></li></ul><hr data-path-to-node="5"><h2 data-path-to-node="6">📑 Asosiy teglar va ularning vazifasi</h2><h3 data-path-to-node="7">1. <code data-path-to-node="7" data-index-in-node="3">&lt;title&gt;</code> — Sayt sarlavhasi</h3><p data-path-to-node="8">Bu teg saytning ichida emas, balki brauzerning yuqori qismidagi <b data-path-to-node="8" data-index-in-node="64">vkladka (tab)</b> oynasida ko'rinadigan nomni belgilaydi.</p><ul data-path-to-node="9"><li><p data-path-to-node="9,0,0"><i data-path-to-node="9,0,0" data-index-in-node="0">Nima uchun kerak:</i> Foydalanuvchi qaysi saytda turganini bilishi va Google qidiruv tizimi saytingizni topishi uchun.</p></li></ul><h3 data-path-to-node="10">2. <code data-path-to-node="10" data-index-in-node="3">&lt;h1&gt;</code> dan <code data-path-to-node="10" data-index-in-node="12">&lt;h6&gt;</code> gacha — Sarlavhalar</h3><p data-path-to-node="11">Bular matnning sarlavhalari hisoblanadi.</p><ul data-path-to-node="12"><li><p data-path-to-node="12,0,0"><code data-path-to-node="12,0,0" data-index-in-node="0">&lt;h1&gt;</code>: Eng muhim va eng katta sarlavha (odatda saytda 1 marta ishlatiladi).</p></li><li><p data-path-to-node="12,1,0"><code data-path-to-node="12,1,0" data-index-in-node="0">&lt;h6&gt;</code>: Eng kichik va eng past darajadagi sarlavha.</p></li><li><p data-path-to-node="12,2,0"><i data-path-to-node="12,2,0" data-index-in-node="0">Nima uchun kerak:</i> Matnni tartiblash va o'quvchiga nima muhimligini ko'rsatish uchun.</p></li></ul><h3 data-path-to-node="13">3. <code data-path-to-node="13" data-index-in-node="3">&lt;p&gt;</code> — Paragraf (Xatboshi)</h3><p data-path-to-node="14">Oddiy matnlarni yozish uchun ishlatiladi. Har bir <code data-path-to-node="14" data-index-in-node="50">&lt;p&gt;</code> tegi matnni yangi qatordan boshlaydi.</p><hr data-path-to-node="15"><h2 data-path-to-node="16">🔗 Aloqalar va Rasmlar</h2><h3 data-path-to-node="17">4. <code data-path-to-node="17" data-index-in-node="3">&lt;a&gt;</code> — Giperhavola (Link)</h3><p data-path-to-node="18">Boshqa saytga yoki sahifaga o'tish uchun ishlatiladi.</p><ul data-path-to-node="19"><li><p data-path-to-node="19,0,0"><b data-path-to-node="19,0,0" data-index-in-node="0">href</b>: Bu attribut ichiga boriladigan manzil (link) yoziladi.</p></li><li><p data-path-to-node="19,1,0"><i data-path-to-node="19,1,0" data-index-in-node="0">Misol:</i> <code data-path-to-node="19,1,0" data-index-in-node="7">&lt;a href="https://google.com"&gt;Googlega o'tish&lt;/a&gt;</code></p></li></ul><h3 data-path-to-node="20">5. <code data-path-to-node="20" data-index-in-node="3">&lt;img&gt;</code> — Rasm qo'yish</h3><p data-path-to-node="21">Bu tegning yopiluvchisi yo'q (toq teg). U rasm chiqarish uchun xizmat qiladi.</p><ul data-path-to-node="22"><li><p data-path-to-node="22,0,0"><b data-path-to-node="22,0,0" data-index-in-node="0">src (source)</b>: Rasm qayerda joylashgani (manzili).</p></li><li><p data-path-to-node="22,1,0"><b data-path-to-node="22,1,0" data-index-in-node="0">alt (alternative)</b>: Agar rasm yuklanmay qolsa, uning o'rnida chiqadigan matn. Bu ko'zi ojizlar uchun o'qiydigan dasturlarga va Googlega rasmda nima borligini tushunishga yordam beradi.</p></li></ul>
"""

L1_CODE = """\
<!DOCTYPE html>
<html>
<head>
    <title>Mening 2-darsim</title>
</head>
<body>

    <h1>Dasturlashni o'rganamiz</h1>
    <p>Bu mening birinchi paragrafim. HTML juda qiziqarli!</p>

    <h3>Foydali havola:</h3>
    <a href="https://telegram.org">Telegramga o'tish</a>

    <br> <img src="rasm.jpg" alt="Dasturlash haqida rasm">

</body>
</html>
"""

L2_TEXT = """\
<pre class="mermaid">
flowchart TB
    HTML["HTML element"] --> IN["inline style attribute"]
    HTML --> INT["internal style tag"]
    HTML --> EXT["external file.css"]
    EXT -->|link rel stylesheet| HTML
    PR["priority"] --> ID1["id selector"]
    PR --> CL["class selector"]
    PR --> TAG["tag selector"]
</pre>

<h2 data-path-to-node="3">🎨 CSS ulanishining 3 xil turi</h2><ol start="1" data-path-to-node="4"><li><p data-path-to-node="4,0,0"><b data-path-to-node="4,0,0" data-index-in-node="0">Inline Style (Qator ichidagi):</b> Bevosita HTML tegining ichida <code data-path-to-node="4,0,0" data-index-in-node="61">style</code> atributi orqali yoziladi.</p></li><li><p data-path-to-node="4,1,0"><b data-path-to-node="4,1,0" data-index-in-node="0">Internal Style (Ichki):</b> HTML hujjatining <code data-path-to-node="4,1,0" data-index-in-node="41">&lt;head&gt;</code> qismida <code data-path-to-node="4,1,0" data-index-in-node="56">&lt;style&gt;</code> tegi ichida yoziladi.</p></li><li><p data-path-to-node="4,2,0"><b data-path-to-node="4,2,0" data-index-in-node="0">External Style (Tashqi):</b> Alohida <code data-path-to-node="4,2,0" data-index-in-node="33">.css</code> fayl ochilib, HTML-ga <code data-path-to-node="4,2,0" data-index-in-node="60">&lt;link&gt;</code> orqali ulanadi (Eng to'g'ri yo'l shu).</p></li></ol><hr data-path-to-node="5"><h2 data-path-to-node="6">🛠️ CSS Xossalari (Properties)</h2><p data-path-to-node="7">Keling, siz aytgan xossalarni bitta misolda ko'rib chiqamiz:</p><h3 data-path-to-node="8">1. Rang va Matn (Color, Font)</h3><ul data-path-to-node="9"><li><p data-path-to-node="9,0,0"><b data-path-to-node="9,0,0" data-index-in-node="0"><code data-path-to-node="9,0,0" data-index-in-node="0">color</code></b>: Matnning rangi (masalan: <code data-path-to-node="9,0,0" data-index-in-node="32">red</code>, <code data-path-to-node="9,0,0" data-index-in-node="37">#ffffff</code>, <code data-path-to-node="9,0,0" data-index-in-node="46">blue</code>).</p></li><li><p data-path-to-node="9,1,0"><b data-path-to-node="9,1,0" data-index-in-node="0"><code data-path-to-node="9,1,0" data-index-in-node="0">background-color</code></b>: Elementning orqa foni rangi.</p></li><li><p data-path-to-node="9,2,0"><b data-path-to-node="9,2,0" data-index-in-node="0"><code data-path-to-node="9,2,0" data-index-in-node="0">font-size</code></b>: Harflarning kattaligi (masalan: <code data-path-to-node="9,2,0" data-index-in-node="43">20px</code>, <code data-path-to-node="9,2,0" data-index-in-node="49">2rem</code>).</p></li><li><p data-path-to-node="9,3,0"><b data-path-to-node="9,3,0" data-index-in-node="0"><code data-path-to-node="9,3,0" data-index-in-node="0">font-family</code></b>: Shrift turi (masalan: <code data-path-to-node="9,3,0" data-index-in-node="35">Arial</code>, <code data-path-to-node="9,3,0" data-index-in-node="42">Times New Roman</code>).</p></li></ul><h3 data-path-to-node="10">2. O'lcham va Shakl (Width, Height, Border)</h3><ul data-path-to-node="11"><li><p data-path-to-node="11,0,0"><b data-path-to-node="11,0,0" data-index-in-node="0"><code data-path-to-node="11,0,0" data-index-in-node="0">width</code> va <code data-path-to-node="11,0,0" data-index-in-node="9">height</code></b>: Elementning eni va bo'yi.</p></li><li><p data-path-to-node="11,1,0"><b data-path-to-node="11,1,0" data-index-in-node="0"><code data-path-to-node="11,1,0" data-index-in-node="0">border</code></b>: Element atrofiga chiziq (ramka) chizish. U 3 ta qiymat oladi: <i data-path-to-node="11,1,0" data-index-in-node="70">qalinligi, turi va rangi</i>. Masalan: <code data-path-to-node="11,1,0" data-index-in-node="105">2px solid black</code>.</p></li><li><p data-path-to-node="11,2,0"><b data-path-to-node="11,2,0" data-index-in-node="0"><code data-path-to-node="11,2,0" data-index-in-node="0">border-radius</code></b>: Burchaklarni yumshatish (aylana qilish).</p></li></ul>
"""

L2_CODE = """\
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>2-dars: HTML va CSS Jamlanmasi</title>
    
    <style>
        /* Internal Style - Ichki usul */
        h1 {
            color: #2c3e50;
            font-family: 'Arial', sans-serif;
            text-align: center;
        }

        h3 {
            color: #e67e22;
            font-family: Verdana;
        }

        p {
            font-size: 18px;
            color: #34495e;
            line-height: 1.6;
        }

        a {
            color: white;
            background-color: #3498db;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px; /* Tugmacha ko'rinishiga keltirish */
            display: inline-block;
        }

        img {
            width: 200px;
            height: 200px;
            border: 5px solid #2ecc71;
            border-radius: 50%; /* Rasmni aylana qiladi */
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <h1>HTML va CSS darsimiz natijasi</h1>
    
    <p style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid blue;">
        Bugun biz teglar bilan ishlashni va ularga rang, o'lcham, shakl berishni o'rgandik. 
        Ushbu matn orqa foni CSS orqali o'zgartirildi.
    </p>

    <h3>Foydali havolalar:</h3>
    <a href="https://google.com">Google-ga o'tish</a>

    <br><br>

    <h3>Bizning rasm:</h3>
    <img src="https://via.placeholder.com/200" alt="Dasturlash rasmi">

    <h6>Sahifa yakuni - 2026</h6>

</body>
</html>
"""

L3_TEXT = """\
<pre class="mermaid">
flowchart LR
    HTML["HTML elements"] -->|class=card| C[".card CSS"]
    HTML -->|id=hero| I["#hero CSS"]
    C -->|reusable| MANY["bir nechta element"]
    I -->|unique| ONE["faqat bitta element"]
    SP["specificity"] -->|id wins| ID1["id higher"]
    SP -->|then| CL2["class lower"]
</pre>

<h2 data-path-to-node="3">💎 Class (Sinf) nima?</h2><p data-path-to-node="4">Class — bu guruhlash degani. Bir xil stilda bo'lishi kerak bo'lgan bir nechta elementga bitta klassni berishingiz mumkin.</p><ul data-path-to-node="5"><li><p data-path-to-node="5,0,0"><b data-path-to-node="5,0,0" data-index-in-node="0">Belgisi:</b> CSS-da nuqta <b data-path-to-node="5,0,0" data-index-in-node="22"><code data-path-to-node="5,0,0" data-index-in-node="22">.</code></b> bilan yoziladi.</p></li><li><p data-path-to-node="5,1,0"><b data-path-to-node="5,1,0" data-index-in-node="0">Xususiyati:</b> Bir xil klassni xohlagancha elementga berish mumkin.</p></li></ul><h2 data-path-to-node="6">🆔 ID (Identifikator) nima?</h2><p data-path-to-node="7">ID — bu yagona (unikal) nom. U xuddi odamning pasport raqami kabi faqat bitta elementga tegishli bo'lishi kerak.</p><ul data-path-to-node="8"><li><p data-path-to-node="8,0,0"><b data-path-to-node="8,0,0" data-index-in-node="0">Belgisi:</b> CSS-da panjara <b data-path-to-node="8,0,0" data-index-in-node="24"><code data-path-to-node="8,0,0" data-index-in-node="24">#</code></b> bilan yoziladi.</p></li><li><p data-path-to-node="8,1,0"><b data-path-to-node="8,1,0" data-index-in-node="0">Xususiyati:</b> Bir sahifada bitta ID nomidan faqat bir marta foydalanish tavsiya etiladi.&nbsp;<br><br><br><br></p><table data-path-to-node="15" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; color: rgb(31, 31, 31); columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 32px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; font-family: &quot;Google Sans Text&quot;, sans-serif !important; line-height: 1.15 !important;"><thead style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><tr style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgb(239, 239, 239); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><strong style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; margin-bottom: 0px !important; line-height: 1.15 !important;">Xususiyat</strong></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgb(239, 239, 239); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><strong style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; margin-bottom: 0px !important; line-height: 1.15 !important;">Class (.)</strong></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgb(239, 239, 239); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><strong style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; margin-bottom: 0px !important; line-height: 1.15 !important;">ID (#)</strong></td></tr></thead><tbody style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><tr style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,1,0,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><b data-path-to-node="15,1,0,0" data-index-in-node="0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Soni</b></span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,1,1,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Bir sahifada ko'p marta ishlatsa bo'ladi.</span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,1,2,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Faqat 1 marta ishlatish kerak.</span></td></tr><tr style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,2,0,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><b data-path-to-node="15,2,0,0" data-index-in-node="0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">CSS-da yozilishi</b></span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,2,1,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><code data-path-to-node="15,2,1,0" data-index-in-node="0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgb(233, 238, 246); border: 0px rgb(68, 71, 70); inset: auto; clear: none; clip: auto; color: rgb(68, 71, 70); columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(68, 71, 70) none 3.33333px; overlay: none; padding: 1px 6px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; font-family: &quot;Google Sans Text&quot;, sans-serif !important; line-height: 1.15 !important;">.nom { ... }</code></span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,2,2,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><code data-path-to-node="15,2,2,0" data-index-in-node="0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgb(233, 238, 246); border: 0px rgb(68, 71, 70); inset: auto; clear: none; clip: auto; color: rgb(68, 71, 70); columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(68, 71, 70) none 3.33333px; overlay: none; padding: 1px 6px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; font-family: &quot;Google Sans Text&quot;, sans-serif !important; line-height: 1.15 !important;">#nom { ... }</code></span></td></tr><tr style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,3,0,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;"><b data-path-to-node="15,3,0,0" data-index-in-node="0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Maqsadi</b></span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 12px 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,3,1,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Bir xil stillarni guruhlash uchun.</span></td><td style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 16px 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; border: 1px solid; margin-top: 0px !important; line-height: 1.15 !important;"><span data-path-to-node="15,3,2,0" style="animation: auto ease 0s 1 normal none running none; appearance: none; background: none 0% 0% / auto repeat scroll padding-box border-box rgba(0, 0, 0, 0); border: 0px rgb(31, 31, 31); inset: auto; clear: none; clip: auto; columns: auto; contain: none; container: none; content: normal; cursor: auto; cx: 0px; cy: 0px; d: none; direction: ltr; display: inline; fill: rgb(0, 0, 0); filter: none; flex: 0 1 auto; float: none; gap: normal; hyphens: manual; interactivity: auto; isolation: auto; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; marker: none; mask: none; offset: normal; opacity: 1; order: 0; outline: rgb(31, 31, 31) none 3.33333px; overlay: none; padding: 0px; page: auto; perspective: none; position: static; quotes: auto; r: 0px; resize: none; rotate: none; rx: auto; ry: auto; scale: none; speak: normal; stroke: none; transform: none; transition: all; translate: none; visibility: visible; x: 0px; y: 0px; zoom: 1; margin-top: 0px !important; line-height: 1.15 !important;">Maxsus, yagona elementni belgilash uchun.</span></td></tr></tbody></table></li></ul>
"""

L3_CODE = """\
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Class uchun nuqta (.) qo'yiladi */
        .qizil-matn {
            color: red;
            font-size: 20px;
        }

        .dumaloq-rasm {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 2px solid black;
        }

        /* ID uchun panjara (#) qo'yiladi */
        #asosiy-sarlavha {
            color: darkblue;
            text-align: center;
            text-decoration: underline;
        }
    </style>
</head>
<body>

    <h1 id="asosiy-sarlavha">Bu yagona sarlavha</h1>

    <p class="qizil-matn">Bu birinchi qizil paragraf.</p>
    <p class="qizil-matn">Bu ikkinchi qizil paragraf (klass bir xil).</p>

    <h3>Bizning rasmlar:</h3>
    <img src="rasm1.jpg" class="dumaloq-rasm" alt="Rasm 1">
    <img src="rasm2.jpg" class="dumaloq-rasm" alt="Rasm 2">

    <br><br>
    <a href="#" class="qizil-matn">Qizil rangli havola</a>

</body>
</html>
"""

L4_TEXT = """\
<pre class="mermaid">
flowchart TB
    BLOCK["block: div h1 p"] -->|new line| FULL["100% width"]
    INLINE["inline: span a strong"] -->|same line| CONTENT["content width"]
    IB["inline-block"] -->|width height ok| MIX["both"]
    DI["display property"] --> BLOCK
    DI --> INLINE
    DI --> IB
</pre>

📦 Block va Inline elementlar nima?
HTML elementlari tabiatan ikki xil ko'rinishda bo'ladi:

1. Block (Blokli) elementlar
Bu elementlar o'zidan keyin hech kimni yoniga qo'ymaydi — xuddi "egoist" kabi butun bir qatorni egallab oladi.

Xususiyati: Har doim yangi qatordan boshlanadi. Ularga width (en) va height (bo'y) berish mumkin.

Misollar: &lt;h1&gt;...&lt;h6&gt;, &lt;p&gt;, &lt;ul&gt;, &lt;li&gt;.

2. Inline (Qatorli) elementlar
Bu elementlar faqat o'ziga kerakli bo'lgan joynigina egallaydi va qolgan joyni boshqa elementlarga bo'shatib beradi.

Xususiyati: Yangi qatordan boshlanmaydi. Ularga width va height berib bo'lmaydi (chunki ular matnning bir qismi hisoblanadi).

Misollar: &lt;a&gt;, &lt;img&gt;, &lt;span&gt;.<br>
"""

L4_CODE = """\
<p>Bu oddiy matn <span style="color:red;">qizil rang</span> bilan</p>

<div style="background: lightblue;">
  Bu block element (div)
</div>
"""

L5_TEXT = """\
<pre class="mermaid">
flowchart LR
    D["div"] -->|generic container| GROUP["elementlarni guruhlash"]
    D -.->|class id| ST["styled"]
    BX["box model"] --> CN["content"]
    BX --> PD["padding"]
    BX --> BR["border"]
    BX --> MG["margin"]
</pre>

<h3 data-path-to-node="2">📦 HTML dunyosida <code data-path-to-node="2" data-index-in-node="18">&lt;div&gt;</code> nima?</h3><h2><p data-path-to-node="3">Agar HTML saytning <b data-path-to-node="3" data-index-in-node="19">skeleti</b> yoki <b data-path-to-node="3" data-index-in-node="32">g'ishtlari</b> bo'lsa, <code data-path-to-node="3" data-index-in-node="51">&lt;div&gt;</code> tegi — bu uydagi <b data-path-to-node="3" data-index-in-node="74">XONALAR</b> yoki <b data-path-to-node="3" data-index-in-node="87">QUTILAR</b>dir.</p><p data-path-to-node="4">Tasavvur qiling, uyingiz bor, lekin ichida devorlar yo'q — hamma narsa (karovat, muzlatgich, televizor, kiyimlar) bir joyda, aralashib yotibdi. Judayam tartibsiz, to'g'rimi?</p><p data-path-to-node="5">Siz uy ichini tartibga solish uchun devorlar urib, <b data-path-to-node="5" data-index-in-node="51">xonalar</b> (oshxona, yotoqxona, mehmonxona) ajratasiz.</p><p data-path-to-node="6">Mana shu ajratilgan <b data-path-to-node="6" data-index-in-node="20">har bir xona — bu bitta <code data-path-to-node="6" data-index-in-node="44">&lt;div&gt;</code> elementidir</b>.</p><ul data-path-to-node="7"><li><p data-path-to-node="7,0,0"><code data-path-to-node="7,0,0" data-index-in-node="0">&lt;div&gt;</code> (Oshxona xonasi) ichiga: muzlatgich, gaz plitasi va stolni joylaysiz.</p></li><li><p data-path-to-node="7,1,0"><code data-path-to-node="7,1,0" data-index-in-node="0">&lt;div&gt;</code> (Mehmonxona xonasi) ichiga: divan, televizor va gilamni joylaysiz.</p></li></ul><hr data-path-to-node="8"></h2><h3 data-path-to-node="9">🎨 CSS va JavaScript bilan qanday bog'lanadi?</h3><h2><p data-path-to-node="10">Boyagi o'xshatishimizni davom ettiramiz:</p><ul data-path-to-node="11"><li><p data-path-to-node="11,0,0"><b data-path-to-node="11,0,0" data-index-in-node="0">HTML (<code data-path-to-node="11,0,0" data-index-in-node="6">&lt;div&gt;</code>)</b>: Bu shunchaki xonaning quruq devorlari. Hali ichida hech narsa yo'q, rangi ham yo'q.</p></li><li><p data-path-to-node="11,1,0"><b data-path-to-node="11,1,0" data-index-in-node="0">CSS</b>: Bu xonani bezatish. Siz CSS-ga aytasiz: <i data-path-to-node="11,1,0" data-index-in-node="45">"Mening <code data-path-to-node="11,1,0" data-index-in-node="53">.oshxona</code> degan <code data-path-to-node="11,1,0" data-index-in-node="68">div</code>-imning devorlarini yashil rangga bo'ya, enini 5 metr, bo'yini 4 metr qil"</i>. CSS aynan shu quti (xona) ichidagi narsalarni tartib bilan joylashtiradi.</p></li><li><p data-path-to-node="11,2,0"><b data-path-to-node="11,2,0" data-index-in-node="0">JavaScript (JS)</b>: Bu xonadagi "aqlli" jihozlar. Masalan, <code data-path-to-node="11,2,0" data-index-in-node="56">.mehmonxona</code> degan <code data-path-to-node="11,2,0" data-index-in-node="74">div</code>-ga kirganda chiroq avtomatik yonishi yoki tugma bosilganda konditsioner ishga tushishi JS orqali bo'ladi.</p></li></ul><hr data-path-to-node="12"></h2><h3 data-path-to-node="13">🛠 Kodda bu qanday ko'rinadi?</h3><h2><p data-path-to-node="14">Uyingizning bir qismini kodda mana shunday tasvirlash mumkin:</p><response-element class="" ng-version="0.0.0-PLACEHOLDER"><!----><!----><!----><!----><!----><!----><code-block _nghost-ng-c1115935386="" class="ng-tns-c1115935386-38 ng-star-inserted"><!----><!----><div _ngcontent-ng-c1115935386="" class="code-block ng-tns-c1115935386-38 ng-animate-disabled ng-trigger ng-trigger-codeBlockRevealAnimation" jslog="223238;track:impression,attention;BardVeMetadataKey:[[&quot;r_d46e79392d940bc4&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6ce27b0483a2250e&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]]" data-hveid="0" decode-data-ved="1" data-ved="0CAAQhtANahcKEwjX-qGwwsCUAxUAAAAAHQAAAAAQUg"><div _ngcontent-ng-c1115935386="" class="code-block-decoration header-formatted gds-title-s ng-tns-c1115935386-38 ng-star-inserted"><span _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-38">HTML</span><div _ngcontent-ng-c1115935386="" class="buttons ng-tns-c1115935386-38 ng-star-inserted"><button _ngcontent-ng-c1115935386="" aria-label="Скачать код" mat-icon-button="" mattooltip="Скачать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger download-button ng-tns-c1115935386-38 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered=""><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="download" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="download"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----><!----><!----><button _ngcontent-ng-c1115935386="" aria-label="Скопировать код" mat-icon-button="" mattooltip="Скопировать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger copy-button ng-tns-c1115935386-38 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered="" jslog="179062;track:generic_click,impression;BardVeMetadataKey:[[&quot;r_d46e79392d940bc4&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6ce27b0483a2250e&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]];mutable:true"><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="content_copy" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="content_copy"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----></div><!----><!----></div><!----><div _ngcontent-ng-c1115935386="" class="formatted-code-block-internal-container ng-tns-c1115935386-38"><div _ngcontent-ng-c1115935386="" class="animated-opacity ng-tns-c1115935386-38"><!----><pre _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-38"><code _ngcontent-ng-c1115935386="" role="text" data-test-id="code-content" class="code-container formatted ng-tns-c1115935386-38"><span class="hljs-comment">&lt;!-- MEHMONXONA XONASI --&gt;</span>
<span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"mehmonxona"</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">h1</span>&gt;</span>Mehmonxonaga xush kelibsiz<span class="hljs-tag">&lt;/<span class="hljs-name">h1</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">p</span>&gt;</span>Bu yerda siz televizor ko'rib dam olishingiz mumkin.<span class="hljs-tag">&lt;/<span class="hljs-name">p</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">button</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"chiroq-tugmasi"</span>&gt;</span>Chiroqni yoqish<span class="hljs-tag">&lt;/<span class="hljs-name">button</span>&gt;</span>
<span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>

<span class="hljs-comment">&lt;!-- OSHXONA XONASI --&gt;</span>
<span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"oshxona"</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">h1</span>&gt;</span>Oshxona qismi<span class="hljs-tag">&lt;/<span class="hljs-name">h1</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">p</span>&gt;</span>Mazali taomlar shu yerda pishiriladi.<span class="hljs-tag">&lt;/<span class="hljs-name">p</span>&gt;</span>
<span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
</code></pre><!----></div></div></div><!----><!----><!----></code-block><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----></response-element></h2><h3 data-path-to-node="16">💡 Xulosa:</h3><h2><p data-path-to-node="17"><code data-path-to-node="17" data-index-in-node="0">&lt;div&gt;</code> — bu saytdagi tartibsizlikning oldini oladigan, elementlarni to'plab, ularni bitta guruh (quti) qilib beradigan eng asosiy asbobdir. Agar <code data-path-to-node="17" data-index-in-node="144">&lt;div&gt;</code> bo'lmaganida, CSS-da saytlarga chiroyli dizayn berish va ularni vizual qismlarga ajratish imkonsiz bo'lar edi.</p></h2>
"""

L5_CODE = """\
<div style="background: lightgray; padding: 10px;">
  <h2>Sarlavha</h2>
  <p>Bu div ichidagi matn</p>
</div>

<div style="background: lightgreen;">
  Ikkinchi blok
</div>
"""

L6_TEXT = """\
<pre class="mermaid">
flowchart TB
    P["parent display flex"] --> JC["justify-content"]
    P --> AI["align-items"]
    P --> FD["flex-direction"]
    JC --> S1["start center end space-between"]
    AI --> S2["start center end stretch"]
    FD --> S3["row column"]
    CH["children"] -->|flex 1| GROW["grow shrink basis"]
</pre>

<h2><p data-path-to-node="0">Dasturlashdagi "uy" o'xshatishimizni davom ettirsak, <b data-path-to-node="0" data-index-in-node="53">Flexbox (Display: flex)</b> — bu xonadagi jihozlarni (mebel, texnika) millimetrigacha aniqlikda, juda oson va aqlli tarzda joylashtiradigan <b data-path-to-node="0" data-index-in-node="189">"sehrli tartiblagich"</b> hisoblanadi.</p><p data-path-to-node="1">Oldinlari elementlarni yonma-yon qo'yish uchun dasturchilar ancha qiynalishgan, lekin <code data-path-to-node="1" data-index-in-node="86">flex</code> kelgach, hammasi o'zgardi.</p><hr data-path-to-node="2"></h2><h3 data-path-to-node="3">🧱 Flexbox qanday ishlaydi?</h3><h2><p data-path-to-node="4">Flexbox ishlatish uchun sizga doim ikki xil narsa kerak:</p><ol start="1" data-path-to-node="5"><li><p data-path-to-node="5,0,0"><b data-path-to-node="5,0,0" data-index-in-node="0">Flex Container (Ota quti):</b> Ichidagi narsalarni tartibga soluvchi asosiy <code data-path-to-node="5,0,0" data-index-in-node="72">div</code>.</p></li><li><p data-path-to-node="5,1,0"><b data-path-to-node="5,1,0" data-index-in-node="0">Flex Items (Bola elementlar):</b> O'sha quti ichida turgan buyumlar.</p></li></ol><p data-path-to-node="6">Siz "Ota quti"ga <code data-path-to-node="6" data-index-in-node="17">display: flex;</code> buyrug'ini bersangiz, uning ichidagi barcha "bolalar" darrov gapga kirib, tartibga tushadi.</p><hr data-path-to-node="7"></h2><h3 data-path-to-node="8">⚙️ Flexbox-ning asosiy "sehrli" buyruqlari:</h3><h2><p data-path-to-node="9">Tasavvur qiling, oshxonadagi 3 ta stulni joylashtiryapsiz:</p></h2><h4 data-path-to-node="10">1. <code data-path-to-node="10" data-index-in-node="3">justify-content</code> (Gorizontal tartiblash)</h4><h2><p data-path-to-node="11">Bu buyruq elementlarni chapdan o'ngga qarab qanday joylashishini belgilaydi:</p><ul data-path-to-node="12"><li><p data-path-to-node="12,0,0"><code data-path-to-node="12,0,0" data-index-in-node="0">flex-start</code>: Hammasi chapga yopishib turadi.</p></li><li><p data-path-to-node="12,1,0"><code data-path-to-node="12,1,0" data-index-in-node="0">flex-end</code>: Hammasi o'ngga borib taqaladi.</p></li><li><p data-path-to-node="12,2,0"><b data-path-to-node="12,2,0" data-index-in-node="0"><code data-path-to-node="12,2,0" data-index-in-node="0">center</code></b>: Hammasi markazda jamlanadi.</p></li><li><p data-path-to-node="12,3,0"><b data-path-to-node="12,3,0" data-index-in-node="0"><code data-path-to-node="12,3,0" data-index-in-node="0">space-between</code></b>: Birinchisi chapda, oxirgisi o'ngda, qolganlari esa o'rtada teng masofada tarqaladi.</p></li></ul></h2><h4 data-path-to-node="13">2. <code data-path-to-node="13" data-index-in-node="3">align-items</code> (Vertikal tartiblash)</h4><h2><p data-path-to-node="14">Agar xonangizning shifti baland bo'lsa, elementlarni tepada, pastda yoki qoq o'rtada turishini belgilaydi:</p><ul data-path-to-node="15"><li><p data-path-to-node="15,0,0"><code data-path-to-node="15,0,0" data-index-in-node="0">center</code>: Elementlarni vertikal (yuqoridan pastga nisbatan) markazga qo'yadi.</p></li></ul></h2><h4 data-path-to-node="16">3. <code data-path-to-node="16" data-index-in-node="3">flex-direction</code> (Yo'nalish)</h4><h2><ul data-path-to-node="17"><li><p data-path-to-node="17,0,0"><code data-path-to-node="17,0,0" data-index-in-node="0">row</code>: Elementlarni yonma-yon (qatorda) tizadi (standart holat).</p></li><li><p data-path-to-node="17,1,0"><code data-path-to-node="17,1,0" data-index-in-node="0">column</code>: Elementlarni ustma-ust (ustun shaklida) taxlaydi.</p></li></ul><hr data-path-to-node="18"></h2><h3 data-path-to-node="19">💡 Jonli misol</h3><h2><p data-path-to-node="20">Aytaylik, siz saytning yuqori qismidagi <b data-path-to-node="20" data-index-in-node="40">Logo</b> va <b data-path-to-node="20" data-index-in-node="48">Menyu</b>ni ikki chetga surib qo'ymoqchisiz:</p><p data-path-to-node="21"><b data-path-to-node="21" data-index-in-node="0">HTML:</b></p><response-element class="" ng-version="0.0.0-PLACEHOLDER"><!----><!----><!----><!----><!----><!----><code-block _nghost-ng-c1115935386="" class="ng-tns-c1115935386-49 ng-star-inserted"><!----><!----><div _ngcontent-ng-c1115935386="" class="code-block ng-tns-c1115935386-49 ng-animate-disabled ng-trigger ng-trigger-codeBlockRevealAnimation" jslog="223238;track:impression,attention;BardVeMetadataKey:[[&quot;r_8385b860d05ebb65&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6b7a7e54c5dd6786&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]]" data-hveid="0" decode-data-ved="1" data-ved="0CAAQhtANahcKEwjX-qGwwsCUAxUAAAAAHQAAAAAQaA"><div _ngcontent-ng-c1115935386="" class="code-block-decoration header-formatted gds-title-s ng-tns-c1115935386-49 ng-star-inserted"><span _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-49">HTML</span><div _ngcontent-ng-c1115935386="" class="buttons ng-tns-c1115935386-49 ng-star-inserted"><button _ngcontent-ng-c1115935386="" aria-label="Скачать код" mat-icon-button="" mattooltip="Скачать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger download-button ng-tns-c1115935386-49 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered=""><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="download" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="download"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----><!----><!----><button _ngcontent-ng-c1115935386="" aria-label="Скопировать код" mat-icon-button="" mattooltip="Скопировать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger copy-button ng-tns-c1115935386-49 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered="" jslog="179062;track:generic_click,impression;BardVeMetadataKey:[[&quot;r_8385b860d05ebb65&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6b7a7e54c5dd6786&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]];mutable:true"><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="content_copy" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="content_copy"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----></div><!----><!----></div><!----><div _ngcontent-ng-c1115935386="" class="formatted-code-block-internal-container ng-tns-c1115935386-49"><div _ngcontent-ng-c1115935386="" class="animated-opacity ng-tns-c1115935386-49"><!----><pre _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-49"><code _ngcontent-ng-c1115935386="" role="text" data-test-id="code-content" class="code-container formatted ng-tns-c1115935386-49"><span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"navbar"</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"logo"</span>&gt;</span>Mening Logotipim<span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">ul</span> <span class="hljs-attr">class</span>=<span class="hljs-string">"menu"</span>&gt;</span>
        <span class="hljs-tag">&lt;<span class="hljs-name">li</span>&gt;</span>Asosiy<span class="hljs-tag">&lt;/<span class="hljs-name">li</span>&gt;</span>
        <span class="hljs-tag">&lt;<span class="hljs-name">li</span>&gt;</span>Xizmatlar<span class="hljs-tag">&lt;/<span class="hljs-name">li</span>&gt;</span>
        <span class="hljs-tag">&lt;<span class="hljs-name">li</span>&gt;</span>Aloqa<span class="hljs-tag">&lt;/<span class="hljs-name">li</span>&gt;</span>
    <span class="hljs-tag">&lt;/<span class="hljs-name">ul</span>&gt;</span>
<span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
</code></pre><!----></div></div></div><!----><!----><!----></code-block><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----></response-element><p data-path-to-node="23"><b data-path-to-node="23" data-index-in-node="0">CSS:</b></p><response-element class="" ng-version="0.0.0-PLACEHOLDER"><!----><!----><!----><!----><!----><!----><code-block _nghost-ng-c1115935386="" class="ng-tns-c1115935386-50 ng-star-inserted"><!----><!----><div _ngcontent-ng-c1115935386="" class="code-block ng-tns-c1115935386-50 ng-animate-disabled ng-trigger ng-trigger-codeBlockRevealAnimation" jslog="223238;track:impression,attention;BardVeMetadataKey:[[&quot;r_8385b860d05ebb65&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6b7a7e54c5dd6786&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]]" data-hveid="0" decode-data-ved="1" data-ved="0CAAQhtANahcKEwjX-qGwwsCUAxUAAAAAHQAAAAAQaQ"><div _ngcontent-ng-c1115935386="" class="code-block-decoration header-formatted gds-title-s ng-tns-c1115935386-50 ng-star-inserted"><span _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-50">CSS</span><div _ngcontent-ng-c1115935386="" class="buttons ng-tns-c1115935386-50 ng-star-inserted"><button _ngcontent-ng-c1115935386="" aria-label="Скачать код" mat-icon-button="" mattooltip="Скачать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger download-button ng-tns-c1115935386-50 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered=""><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="download" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="download"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----><!----><!----><button _ngcontent-ng-c1115935386="" aria-label="Скопировать код" mat-icon-button="" mattooltip="Скопировать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger copy-button ng-tns-c1115935386-50 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered="" jslog="179062;track:generic_click,impression;BardVeMetadataKey:[[&quot;r_8385b860d05ebb65&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_6b7a7e54c5dd6786&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]];mutable:true"><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="content_copy" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="content_copy"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----></div><!----><!----></div><!----><div _ngcontent-ng-c1115935386="" class="formatted-code-block-internal-container ng-tns-c1115935386-50"><div _ngcontent-ng-c1115935386="" class="animated-opacity ng-tns-c1115935386-50"><!----><pre _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-50"><code _ngcontent-ng-c1115935386="" role="text" data-test-id="code-content" class="code-container formatted ng-tns-c1115935386-50"><span class="hljs-selector-class">.navbar</span> {
    <span class="hljs-attribute">display</span>: flex; <span class="hljs-comment">/* Sehrli tayoqchani ishga tushiramiz */</span>
    <span class="hljs-attribute">justify-content</span>: space-between; <span class="hljs-comment">/* Logoni chapga, menyuni o'ngga suradi */</span>
    <span class="hljs-attribute">align-items</span>: center; <span class="hljs-comment">/* Hammasini vertikal tekislaydi */</span>
    <span class="hljs-attribute">background-color</span>: <span class="hljs-number">#333</span>;
    <span class="hljs-attribute">padding</span>: <span class="hljs-number">10px</span>;
}
</code></pre><!----></div></div></div><!----><!----><!----></code-block><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----></response-element></h2><h3 data-path-to-node="25">🌟 Nega bu qiziqarli?</h3><h2><p data-path-to-node="26">Flexbox-siz siz elementlarni surish uchun ming xil "margin" va "padding" ishlatib, har bir ekran (telefon yoki kompyuter) uchun alohida o'lcham berib chiqishingiz kerak edi. <code data-path-to-node="26" data-index-in-node="174">flex</code> esa hamma narsani <b data-path-to-node="26" data-index-in-node="197">elastik</b> (flexible) qiladi — ekran toraysa ham, elementlar o'zini aqlli tutib, siqiladi yoki joyini o'zgartiradi.</p><p data-path-to-node="27"></p></h2>
"""

L6_CODE = """\
<div style="display: flex; gap: 10px;">
  <div style="background: red; width: 100px; height: 100px;"></div>
  <div style="background: blue; width: 100px; height: 100px;"></div>
  <div style="background: green; width: 100px; height: 100px;"></div>
</div>
"""

L7_TEXT = """\
<pre class="mermaid">
flowchart TB
    T["table"] --> THEAD["thead"]
    T --> TBODY["tbody"]
    T --> TFOOT["tfoot"]
    THEAD --> TR1["tr"]
    TR1 --> TH["th sarlavha"]
    TBODY --> TR2["tr"]
    TR2 --> TD["td qiymat"]
    CS["colspan rowspan"] -.->|merge| TD
</pre>

<h2><p data-path-to-node="0">Dasturlashdagi "uy" misolimizga qaytsak, <b data-path-to-node="0" data-index-in-node="41"><code data-path-to-node="0" data-index-in-node="41">&lt;table&gt;</code> (Jadval)</b> — bu uydagi <b data-path-to-node="0" data-index-in-node="70">javon (shkaf)</b> yoki <b data-path-to-node="0" data-index-in-node="89">kitob javoni</b> kabidir.</p><p data-path-to-node="1">Agar <code data-path-to-node="1" data-index-in-node="5">&lt;div&gt;</code> shunchaki bo'sh xona bo'lsa, <code data-path-to-node="1" data-index-in-node="40">&lt;table&gt;</code> — bu ma'lumotlarni qat'iy tartibda, kataklarga joylashtirish uchun ishlatiladigan maxsus tizim. Masalan, mahsulotlar narxi, o'quvchilar reytingi yoki ish grafigini ko'rsatish uchun jadvaldan yaxshisi yo'q.</p><hr data-path-to-node="2"></h2><h3 data-path-to-node="3">🧱 Jadvalning "G'ishtlari" (Teglar)</h3><h2><p data-path-to-node="4">Jadval qurishda sizga 4 ta asosiy teg kerak bo'ladi:</p><ol start="1" data-path-to-node="5"><li><p data-path-to-node="5,0,0"><b data-path-to-node="5,0,0" data-index-in-node="0"><code data-path-to-node="5,0,0" data-index-in-node="0">&lt;table&gt;</code></b>: Jadvalning o'zi (Javonning tashqi korpusi).</p></li><li><p data-path-to-node="5,1,0"><b data-path-to-node="5,1,0" data-index-in-node="0"><code data-path-to-node="5,1,0" data-index-in-node="0">&lt;tr&gt;</code></b> (Table Row): Jadvalning <b data-path-to-node="5,1,0" data-index-in-node="29">qatori</b> (Javonning har bir qavati).</p></li><li><p data-path-to-node="5,2,0"><b data-path-to-node="5,2,0" data-index-in-node="0"><code data-path-to-node="5,2,0" data-index-in-node="0">&lt;th&gt;</code></b> (Table Header): Jadvalning <b data-path-to-node="5,2,0" data-index-in-node="32">sarlavhasi</b> (Qavatdagi bo'lim nomi, masalan: "Nomi", "Narxi"). Odatda matn qalin bo'ladi.</p></li><li><p data-path-to-node="5,3,0"><b data-path-to-node="5,3,0" data-index-in-node="0"><code data-path-to-node="5,3,0" data-index-in-node="0">&lt;td&gt;</code></b> (Table Data): Jadvalning <b data-path-to-node="5,3,0" data-index-in-node="30">katagi</b> (Qavat ichidagi haqiqiy buyum yoki ma'lumot).</p></li></ol><hr data-path-to-node="6"></h2><h3 data-path-to-node="7">📝 Oddiy misol: Meva do'koni</h3><h2><p data-path-to-node="8">Keling, mevalar va ularning narxini jadvalga solamiz:</p><response-element class="" ng-version="0.0.0-PLACEHOLDER"><!----><!----><!----><!----><!----><!----><code-block _nghost-ng-c1115935386="" class="ng-tns-c1115935386-60 ng-star-inserted"><!----><!----><div _ngcontent-ng-c1115935386="" class="code-block ng-tns-c1115935386-60 ng-animate-disabled ng-trigger ng-trigger-codeBlockRevealAnimation" jslog="223238;track:impression,attention;BardVeMetadataKey:[[&quot;r_e6d7141ba0365415&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_bea045cf52968e89&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]]" data-hveid="0" decode-data-ved="1" data-ved="0CAAQhtANahcKEwjX-qGwwsCUAxUAAAAAHQAAAAAQfQ"><div _ngcontent-ng-c1115935386="" class="code-block-decoration header-formatted gds-title-s ng-tns-c1115935386-60 ng-star-inserted"><span _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-60">HTML</span><div _ngcontent-ng-c1115935386="" class="buttons ng-tns-c1115935386-60 ng-star-inserted"><button _ngcontent-ng-c1115935386="" aria-label="Скачать код" mat-icon-button="" mattooltip="Скачать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger download-button ng-tns-c1115935386-60 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered=""><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="download" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="download"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----><!----><!----><button _ngcontent-ng-c1115935386="" aria-label="Скопировать код" mat-icon-button="" mattooltip="Скопировать код" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-mdc-tooltip-trigger copy-button ng-tns-c1115935386-60 mat-unthemed ng-star-inserted" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered="" jslog="179062;track:generic_click,impression;BardVeMetadataKey:[[&quot;r_e6d7141ba0365415&quot;,&quot;c_8bcd8cc593fb6429&quot;,null,&quot;rc_bea045cf52968e89&quot;,null,null,&quot;&quot;,null,1,null,null,1,0]];mutable:true"><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1115935386="" role="img" fonticon="content_copy" class="mat-icon notranslate gds-icon-s google-symbols mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font" data-mat-icon-name="content_copy"></mat-icon><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button><!----><!----><!----></div><!----><!----></div><!----><div _ngcontent-ng-c1115935386="" class="formatted-code-block-internal-container ng-tns-c1115935386-60"><div _ngcontent-ng-c1115935386="" class="animated-opacity ng-tns-c1115935386-60"><!----><pre _ngcontent-ng-c1115935386="" class="ng-tns-c1115935386-60"><code _ngcontent-ng-c1115935386="" role="text" data-test-id="code-content" class="code-container formatted ng-tns-c1115935386-60"><span class="hljs-tag">&lt;<span class="hljs-name">table</span> <span class="hljs-attr">border</span>=<span class="hljs-string">"1"</span>&gt;</span>
  <span class="hljs-comment">&lt;!-- 1-qator: Sarlavhalar --&gt;</span>
  <span class="hljs-tag">&lt;<span class="hljs-name">tr</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">th</span>&gt;</span>Meva nomi<span class="hljs-tag">&lt;/<span class="hljs-name">th</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">th</span>&gt;</span>Narxi (1kg)<span class="hljs-tag">&lt;/<span class="hljs-name">th</span>&gt;</span>
  <span class="hljs-tag">&lt;/<span class="hljs-name">tr</span>&gt;</span>
  
  <span class="hljs-comment">&lt;!-- 2-qator: Birinchi ma'lumot --&gt;</span>
  <span class="hljs-tag">&lt;<span class="hljs-name">tr</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">td</span>&gt;</span>Olma<span class="hljs-tag">&lt;/<span class="hljs-name">td</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">td</span>&gt;</span>15 000 so'm<span class="hljs-tag">&lt;/<span class="hljs-name">td</span>&gt;</span>
  <span class="hljs-tag">&lt;/<span class="hljs-name">tr</span>&gt;</span>
  
  <span class="hljs-comment">&lt;!-- 3-qator: Ikkinchi ma'lumot --&gt;</span>
  <span class="hljs-tag">&lt;<span class="hljs-name">tr</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">td</span>&gt;</span>Banan<span class="hljs-tag">&lt;/<span class="hljs-name">td</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">td</span>&gt;</span>22 000 so'm<span class="hljs-tag">&lt;/<span class="hljs-name">td</span>&gt;</span>
  <span class="hljs-tag">&lt;/<span class="hljs-name">tr</span>&gt;</span>
<span class="hljs-tag">&lt;/<span class="hljs-name">table</span>&gt;</span>
</code></pre><!----></div></div></div><!----><!----><!----></code-block><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----><!----></response-element><hr data-path-to-node="10"></h2><h3 data-path-to-node="11">🎨 Jadvalni "bezash" (CSS)</h3><h2><p data-path-to-node="12">Jadvallar boshida juda xunuk va oddiy ko'rinadi. Ularni "zamonaviy mebel"ga aylantirish uchun CSS ishlatamiz:</p><ul data-path-to-node="13"><li><p data-path-to-node="13,0,0"><b data-path-to-node="13,0,0" data-index-in-node="0"><code data-path-to-node="13,0,0" data-index-in-node="0">border-collapse: collapse;</code></b>: Kataklar orasidagi ortiqcha chiziqlarni birlashtirib, bitta chiroyli chiziq qiladi.</p></li><li><p data-path-to-node="13,1,0"><b data-path-to-node="13,1,0" data-index-in-node="0"><code data-path-to-node="13,1,0" data-index-in-node="0">padding</code></b>: Katak ichidagi matnga "nafas olishi" uchun joy beradi.</p></li><li><p data-path-to-node="13,2,0"><b data-path-to-node="13,2,0" data-index-in-node="0"><code data-path-to-node="13,2,0" data-index-in-node="0">nth-child(even)</code></b>: Jadvalning har bir ikkinchi qatorini rangli qilib qo'yadi (zebra uslubi), shunda o'qish oson bo'ladi.</p></li></ul><hr data-path-to-node="14"></h2><h3 data-path-to-node="15">⚠️ Qachon ishlatish kerak?</h3><h2><p data-path-to-node="16">Dasturlashda oltin qoida bor:</p><ul data-path-to-node="17"><li><p data-path-to-node="17,0,0"><b data-path-to-node="17,0,0" data-index-in-node="0"><code data-path-to-node="17,0,0" data-index-in-node="0">&lt;table&gt;</code></b>: Faqat haqiqiy <b data-path-to-node="17,0,0" data-index-in-node="23">ma'lumotlar to'plami</b> (statistika, hisobotlar) uchun ishlatiladi.</p></li><li><p data-path-to-node="17,1,0"><b data-path-to-node="17,1,0" data-index-in-node="0"><code data-path-to-node="17,1,0" data-index-in-node="0">&lt;div&gt;</code> + Flexbox</b>: Saytning umumiy ko'rinishini (dizaynini) qurish uchun ishlatiladi.</p></li></ul><p data-path-to-node="18"><b data-path-to-node="18" data-index-in-node="0">Xulosa:</b> Agar sizga tartibli ro'yxat, narxlar jadvali yoki dars jadvali kerak bo'lsa — <code data-path-to-node="18" data-index-in-node="86">&lt;table&gt;</code> sizning eng yaqin yordamchingiz!</p></h2>
"""

L7_CODE = """\
<table border="1">
  <tr>
    <th>Ism</th>
    <th>Yosh</th>
  </tr>
  <tr>
    <td>Ali</td>
    <td>18</td>
  </tr>
  <tr>
    <td>Vali</td>
    <td>20</td>
  </tr>
</table>
"""

L8_TEXT = """\
<pre class="mermaid">
flowchart LR
    POS["position"] --> ST["static default"]
    POS --> RE["relative offset"]
    POS --> AB["absolute parent relative"]
    POS --> FI["fixed viewport"]
    POS --> SK["sticky scroll"]
    OFF["top right bottom left"] -->|move| RE
    OFF --> AB
    OFF --> FI
</pre>

<h3 data-path-to-node="3">1. <code data-path-to-node="3" data-index-in-node="3">static</code> (Default - Standart)</h3><p data-path-to-node="4">Barcha elementlar odatda <code data-path-to-node="4" data-index-in-node="25">static</code> holatda bo'ladi. Ular kodda qaysi tartibda yozilgan bo'lsa, brauzerda ham shunday tartibda chiqadi.</p><ul data-path-to-node="5"><li><p data-path-to-node="5,0,0"><b data-path-to-node="5,0,0" data-index-in-node="0">Xususiyati:</b> <code data-path-to-node="5,0,0" data-index-in-node="12">top</code>, <code data-path-to-node="5,0,0" data-index-in-node="17">bottom</code>, <code data-path-to-node="5,0,0" data-index-in-node="25">left</code>, <code data-path-to-node="5,0,0" data-index-in-node="31">right</code> buyruqlari bunga ta'sir qilmaydi.</p></li></ul><h3 data-path-to-node="6">2. <code data-path-to-node="6" data-index-in-node="3">relative</code> (Nisbiy)</h3><p data-path-to-node="7">Element o'zining asl turgan joyiga nisbatan suriladi.</p><ul data-path-to-node="8"><li><p data-path-to-node="8,0,0"><b data-path-to-node="8,0,0" data-index-in-node="0">Xususiyati:</b> Agar siz <code data-path-to-node="8,0,0" data-index-in-node="21">left: 20px</code> bersangiz, u o'z joyidan 20 piksel o'ngga suriladi, lekin <b data-path-to-node="8,0,0" data-index-in-node="90">asl joyi bo'sh bo'lib qoladi</b> (boshqa elementlar uning joyini egallamaydi).</p></li></ul><h3 data-path-to-node="9">3. <code data-path-to-node="9" data-index-in-node="3">absolute</code> (Mutloq)</h3><p data-path-to-node="10">Bu element o'zining "ota" (yordamchi) elementiga nisbatan joylashadi.</p><ul data-path-to-node="11"><li><p data-path-to-node="11,0,0"><b data-path-to-node="11,0,0" data-index-in-node="0">Sharti:</b> "Ota" elementida <code data-path-to-node="11,0,0" data-index-in-node="25">position: relative</code> bo'lishi shart. Agar bo'lmasa, u butun sahifaga (body) nisbatan joy oladi.</p></li><li><p data-path-to-node="11,1,0"><b data-path-to-node="11,1,0" data-index-in-node="0">Xususiyati:</b> U sahifa oqimidan chiqib ketadi (boshqa elementlar uni bor deb hisoblamaydi).</p></li></ul><h3 data-path-to-node="12">4. <code data-path-to-node="12" data-index-in-node="3">fixed</code> (Qat'iy/Yopishgan)</h3><p data-path-to-node="13">Element brauzer oynasiga (ekranga) yopishib qoladi.</p><ul data-path-to-node="14"><li><p data-path-to-node="14,0,0"><b data-path-to-node="14,0,0" data-index-in-node="0">Xususiyati:</b> Sahifani pastga tushirsangiz ham (scroll qilsangiz), u joyidan qimirlamaydi. Masalan: Tepada turadigan menyular (Navbar).</p></li></ul><h3 data-path-to-node="15">5. <code data-path-to-node="15" data-index-in-node="3">sticky</code> (Yopishqoq)</h3><p data-path-to-node="16">Bu <code data-path-to-node="16" data-index-in-node="3">relative</code> va <code data-path-to-node="16" data-index-in-node="15">fixed</code> qorishmasi. Element ma'lum bir masofaga yetguncha oddiy turadi, o'sha nuqtaga yetganda ekranga yopishib qoladi.</p><ul data-path-to-node="17"><li><p data-path-to-node="17,0,0"><b data-path-to-node="17,0,0" data-index-in-node="0">Misol:</b> Jadval sarlavhalari yoki yon tarafdagi reklamalar.</p></li></ul>
"""

L8_CODE = """\
<!DOCTYPE html>
<html>
<head>
    <style>
        .box {
            width: 100px;
            height: 100px;
            color: white;
            padding: 10px;
            margin: 10px;
        }

        /* Fixed - Ekranda qotib turadi */
        .header {
            position: fixed;
            top: 0;
            width: 100%;
            background-color: black;
            text-align: center;
        }

        /* Relative - O'z joyidan suriladi */
        .relativ-blok {
            position: relative;
            top: 20px;
            left: 50px;
            background-color: blue;
        }

        /* Absolute uchun ota element */
        .ota {
            position: relative;
            width: 300px;
            height: 200px;
            background-color: lightgrey;
            margin-top: 50px;
        }

        /* Absolute - Ota elementning ichida xohlagan joyga qo'yamiz */
        .abs-blok {
            position: absolute;
            bottom: 0;
            right: 0;
            background-color: red;
        }
    </style>
</head>
<body>

    <div class="header">Men har doim tepada turaman (Fixed)</div>

    <br><br><br>

    <div class="box relativ-blok">Men Relativeman</div>

    <div class="ota">
        Men Ota elementman (Relative)
        <div class="box abs-blok">Men Absoluteman (Pastki o'ngda)</div>
    </div>

    <p style="height: 1000px;">
        Pastga scroll qiling, Fixed element joyida qolishini ko'rasiz...
    </p>

</body>
</html>
"""

L9_TEXT = """\
<pre class="mermaid">
flowchart LR
    EL["element"] --> BEF["::before"]
    EL --> AFT["::after"]
    BEF -->|content required| INS["inserted before"]
    AFT -->|content required| AP["appended after"]
    USE["use cases"] --> DECO["dekoratsiya"]
    USE --> ICON["icons"]
    USE --> CLR["clearfix"]
</pre>

<p data-path-to-node="0"><b data-path-to-node="0" data-index-in-node="0"><code data-path-to-node="0" data-index-in-node="0">::before</code></b> va <b data-path-to-node="0" data-index-in-node="12"><code data-path-to-node="0" data-index-in-node="12">::after</code></b> — bular CSS-da <b data-path-to-node="0" data-index-in-node="35">psevdo-elementlar</b> deb ataladi. Ular HTML-da mavjud bo'lmagan "virtual" kontentni CSS orqali qo'shish uchun ishlatiladi.</p><p data-path-to-node="1">Buni oddiy qilib tushuntiradigan bo'lsak:</p><ul data-path-to-node="2"><li><p data-path-to-node="2,0,0"><b data-path-to-node="2,0,0" data-index-in-node="0"><code data-path-to-node="2,0,0" data-index-in-node="0">::before</code></b> — Elementning ichidagi kontentdan <b data-path-to-node="2,0,0" data-index-in-node="43">oldin</b> nimanidir joylashtiradi.</p></li><li><p data-path-to-node="2,1,0"><b data-path-to-node="2,1,0" data-index-in-node="0"><code data-path-to-node="2,1,0" data-index-in-node="0">::after</code></b> — Elementning ichidagi kontentdan <b data-path-to-node="2,1,0" data-index-in-node="42">keyin</b> nimanidir joylashtiradi.</p></li></ul><hr data-path-to-node="3"><h3 data-path-to-node="4">⚠️ Eng muhim qoida</h3><p data-path-to-node="5">Ushbu psevdo-elementlar ishlashi uchun ularning ichida <b data-path-to-node="5" data-index-in-node="55"><code data-path-to-node="5" data-index-in-node="55">content: "";</code></b> xossasi bo'lishi <b data-path-to-node="5" data-index-in-node="85">shart</b>. Agar bu bo'lmasa, element ekranda ko'rinmaydi.</p>
"""

L9_CODE = """\
<!DOCTYPE html>
<html>
<head>
    <style>
        /* 1. Sarlavhadan oldin va keyin yulduzcha qo'yish */
        h1::before {
            content: "⭐ ";
        }
        h1::after {
            content: " ⭐";
            color: gold;
        }

        /* 2. Havoladan keyin chiziqcha qo'yish */
        a {
            text-decoration: none;
            font-size: 20px;
            color: blue;
            position: relative;
        }

        a::after {
            content: " →"; /* Havoladan keyin strelka chiqadi */
            color: red;
            font-weight: bold;
        }

        /* 3. Dizayn uchun ishlatish (border o'rniga pastidan chiziq) */
        .tag-p {
            position: relative;
            display: inline-block;
        }

        .tag-p::after {
            content: ""; /* Bo'sh kontent */
            position: absolute;
            left: 0;
            bottom: -5px;
            width: 100%;
            height: 3px;
            background-color: green; /* Matn tegidan yashil chiziq tortadi */
        }
    </style>
</head>
<body>

    <h1>Darsimiz: Pseudo-elements</h1>

    <p class="tag-p">Bu matnning pastida yashil chiziq bor (CSS orqali yaratilgan).</p>
    
    <br><br>
    
    <a href="#">Batafsil o'qish</a>

</body>
</html>
"""

L10_TEXT = """\
<pre class="mermaid">
flowchart LR
    KF["@keyframes name"] -->|from to or 0 to 100| ST["steps"]
    EL["element"] -->|animation name dur| KF
    EL -->|transition prop dur| TR["smooth state change"]
    PR["properties"] -->|transform opacity| CP["compositor friendly"]
</pre>

<p data-path-to-node="0">11-darsimizga xush kelibsiz! Bugun biz CSS-ning eng sehrli qismi — <b data-path-to-node="0" data-index-in-node="67">Animation (Animatsiya)</b> haqida gaplashamiz. Animatsiya yordamida biz elementlarni qimirlatishimiz, rangini o'zgartirishimiz va ularga "jon" kiritishimiz mumkin.</p><p data-path-to-node="1">CSS animatsiyasi ikki asosiy qismdan iborat:</p><ol start="1" data-path-to-node="2"><li><p data-path-to-node="2,0,0"><b data-path-to-node="2,0,0" data-index-in-node="0"><code data-path-to-node="2,0,0" data-index-in-node="0">@keyframes</code></b>: Animatsiyaning "ssenariysi" (qaysi vaqtda nima sodir bo'lishi).</p></li><li><p data-path-to-node="2,1,0"><b data-path-to-node="2,1,0" data-index-in-node="0"><code data-path-to-node="2,1,0" data-index-in-node="0">animation</code> xossalari</b>: Bu ssenariyni qaysi elementga va qancha vaqt davomida qo'llash.</p></li></ol><hr data-path-to-node="3"><h3 data-path-to-node="4">1. <code data-path-to-node="4" data-index-in-node="3">@keyframes</code> — Animatsiya ssenariysi</h3><p data-path-to-node="5">Bu yerda biz harakatning boshlanishi (<code data-path-to-node="5" data-index-in-node="38">from</code>) va tugashini (<code data-path-to-node="5" data-index-in-node="58">to</code>) yoki foizlar yordamida qadamlarini belgilaymiz.</p>
"""

L10_CODE = """\
@keyframes meningHarakatim {
    from { left: 0px; background-color: red; }
    to { left: 200px; background-color: yellow; }
}
"""

LESSON_TASKS: dict[int, dict] = {
    0: {
        "title": "Shaxsiy profil sahifasi (HTML only)",
        "description": "Faqat HTML ishlatib o'zingiz haqingizda oddiy bir sahifali sayt yarating. CSS yo'q — toza HTML struktura. Bu — birinchi loyihangiz.",
        "requirements": "• DOCTYPE, html, head, body to'g'ri ketma-ketlikda\n• head ichida: meta charset, title\n• h1 (ism familiya), h2 (qisqa tavsif)\n• 2-3 paragraph (o'zingiz haqingizda)\n• ul yoki ol (qiziqishlar ro'yxati)\n• Kamida 1 ta a (havola) va 1 ta img (rasm)\n• Faylda izoh (HTML comment) bilan bo'limlar belgilangan",
        "technologies": "HTML5",
        "deadline_days": 2,
    },
    1: {
        "title": "Loyiha",
        "description": "",
        "requirements": "",
        "technologies": "",
        "deadline_days": 2,
    },
    2: {
        "title": "Stillangan vizit kartochka (3 ta CSS usuli)",
        "description": "1-dars sahifasiga 3 ta usulda CSS qo'shing: inline (1 element), internal (head ichida style tag), external (alohida style.css). Har usulning afzalligi va kamchiligini bilib oling.",
        "requirements": "• Kamida 1 ta inline style attribute (masalan, hero matn rangi)\n• head ichida style tag bilan kamida 3 ta selector\n• style.css fayli + link rel=stylesheet bilan ulangan\n• Kamida 5 ta CSS property: color, background, font-size, padding, margin\n• README'da har usulning qachon yaxshi ekanligi yozilgan",
        "technologies": "HTML5, CSS3, inline/internal/external CSS",
        "deadline_days": 3,
    },
    3: {
        "title": "Kartochkalar to'plami (class va id)",
        "description": "Mahsulotlar yoki xizmatlar uchun 6 ta kartochka ro'yxati. Har kartochka umumiy .card class ishlatadi, lekin alohida #header sticky qismi unique id bilan stilladi. Class qayta ishlatish va id unique ekanligini ko'rsating.",
        "requirements": "• .card class kamida 6 ta elementga qo'llangan\n• #header unique id (sahifada faqat 1 marta)\n• .card-title, .card-body, .card-footer kabi sub-selectorlar\n• 3 ta turli ranglardagi card variants (.card.primary, .card.danger ...)\n• #cta unique id li 'asosiy harakat' tugmasi\n• README: nima uchun class va qachon id kerakligi izohlangan",
        "technologies": "HTML5, CSS3, class, id, selectors",
        "deadline_days": 3,
    },
    4: {
        "title": "block vs inline demo sahifasi",
        "description": "Bir sahifada display rejimlarini namoyish eting: div ning block xulqi, span ning inline xulqi va inline-block ning kombinatsiyasini. Har bir tahlil yoniga matnda tushuntirish.",
        "requirements": "• Kamida 3 ta div (block — har biri yangi qatorda)\n• Kamida 5 ta span (inline — bir qatorda)\n• Kamida 3 ta inline-block elementlar (width/height qo'llangan)\n• Har bo'lim oldida h3 va izoh paragraph\n• Border yoki background bilan vizual ajratib ko'rsatilgan",
        "technologies": "HTML5, CSS3, display, block, inline, inline-block",
        "deadline_days": 3,
    },
    5: {
        "title": "Konteyner layout (div bilan)",
        "description": "div yordamida 3 bo'limli sahifa quring: header, main (3 ustun), footer. Box model (padding, border, margin) ni vizual o'rganing — har bo'lim yonida border ko'rinib tursin.",
        "requirements": "• .header, .main, .footer div lari bor\n• Main ichida .left-col, .center-col, .right-col\n• Har konteynerga padding, border, margin qo'llangan\n• background-color bilan har bo'lim aniq ajraladi\n• max-width: 1200px markazlashtirilgan\n• Box-sizing: border-box global ravishda",
        "technologies": "HTML5, CSS3, div, box model, padding, margin, border",
        "deadline_days": 4,
    },
    6: {
        "title": "Flexbox bilan responsive nav va hero",
        "description": "Display flex ishlatib zamonaviy nav bar va 3-ustunli hero bo'limini yarating. Mobile da column ga aylanadi (kichik ekran uchun).",
        "requirements": "• Nav: justify-content: space-between, align-items: center\n• Hero: 3 ta teng ustun (flex: 1)\n• Kamida 1 ta @media (max-width: 768px) bilan column ga o'tish\n• gap property ishlatilgan (margin emas)\n• Hover effects nav linklarda\n• Logo + 4 ta nav link + CTA tugma",
        "technologies": "HTML5, CSS3, flexbox, responsive, media queries",
        "deadline_days": 4,
    },
    7: {
        "title": "Narxlar jadvali (table)",
        "description": "Mahsulotlar yoki xizmatlar uchun chiroyli narxlar jadvalini yarating. thead/tbody/tfoot, colspan/rowspan ishlatilgan, zebra-striping bilan.",
        "requirements": "• thead, tbody, tfoot bo'limlari bor\n• Kamida 5 ustun (Nom, Tavsif, Narx, Soni, Jami)\n• tfoot ichida 'Jami' qatori colspan bilan\n• Zebra striping: tr:nth-child(even) bilan\n• Hover effect: tr:hover\n• Border, padding, font-weight bilan chiroyli ko'rinish",
        "technologies": "HTML5, CSS3, table, thead, tbody, colspan, nth-child",
        "deadline_days": 4,
    },
    8: {
        "title": "Sticky nav + tooltip (position)",
        "description": "Position property bilan ishlash: yuqorida sticky nav (scrollda qoladi), kartochka yonida absolute tooltip va relative ota element.",
        "requirements": "• position: sticky bilan nav (top: 0)\n• Kamida 3 ta kartochka: parent position: relative\n• Har kartochkada position: absolute bilan badge yoki tooltip\n• z-index ishlatilgan (overlap holatlari uchun)\n• position: fixed bilan floating 'Yuqoriga' tugmasi\n• Smooth scroll yoki transition qo'shilgan",
        "technologies": "HTML5, CSS3, position, sticky, absolute, fixed, z-index",
        "deadline_days": 4,
    },
    9: {
        "title": "Pseudo-elementlar bilan dizayn (::before ::after)",
        "description": "::before va ::after pseudo-elementlarini ishlatib HTML ga qo'shimcha elementlar qo'shmasdan dizayn qo'shing: custom dekoratsiya, quote belgilari, icons va clearfix.",
        "requirements": "• Tugma yonida ::before bilan icon\n• Quote paragraph::before content uchun quote belgisi\n• Kartochka::after bilan dekorativ chiziq yoki triangle\n• Clearfix pattern .clearfix::after { content: ''; clear: both; }\n• Custom checkbox: input + label::before\n• content property har joyda to'g'ri ishlatilgan",
        "technologies": "HTML5, CSS3, ::before, ::after, content, clearfix",
        "deadline_days": 4,
    },
    10: {
        "title": "Animatsiyali landing sahifasi",
        "description": "Bu kursning yakuniy loyihasi. @keyframes va transition bilan jonli landing sahifasini yarating: loader, hero matn animatsiyasi, card hover effektlari va scroll-triggered fade-in.",
        "requirements": "• Loader animation (rotate yoki dots)\n• Hero matn: fade-in + slide-up @keyframes\n• Card hover: transform: translateY + box-shadow transition\n• Tugma hover: scale + background color transition\n• Kamida 3 ta @keyframes va 5 ta transition\n• animation-delay bilan ketma-ket effekt\n• transform va opacity faqat (compositor friendly)",
        "technologies": "HTML5, CSS3, @keyframes, animation, transition, transform",
        "deadline_days": 5,
    },
}


LESSONS = [
    {
        "order": 0, "title": "1-Kirish",
        "text": L0_TEXT, "code": L0_CODE, "lang": "html",
        "video": "https://youtu.be/NKnrOBLXmKo",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "html nima ekan?",
                "description": "html nima ekan?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "css nima?",
                "description": "css nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "javascript nima ekan?",
                "description": "javascript nima ekan?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "python nima?",
                "description": "python nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "saytga harakat qoshish tili qaysi?",
                "description": "saytga harakat qoshish tili qaysi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 2,
            },
        ],
    },
    {
        "order": 1, "title": "2-dars Teglar bilan ishlash",
        "text": L1_TEXT, "code": L1_CODE, "lang": "html",
        "video": "https://youtu.be/02DjEJt7JIM",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "sarlavhalar turi neshta?",
                "description": "sarlavhalar turi neshta?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "eng kotta sarlavha turi qaysi?",
                "description": "eng kotta sarlavha turi qaysi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "text uchun qaysi tegdan foydalanamiz?",
                "description": "text uchun qaysi tegdan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "img src qismi nima uchun kerak?",
                "description": "img src qismi nima uchun kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "saytdan saytga otish uchun teg nomi?",
                "description": "saytdan saytga otish uchun teg nomi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "<title></title> bu teg nima uchun kerak?",
                "description": "<title></title> bu teg nima uchun kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 4,
            },
        ],
    },
    {
        "order": 2, "title": "3-dars CSS style turlari",
        "text": L2_TEXT, "code": L2_CODE, "lang": "html",
        "video": "https://youtu.be/WOeF7h9KOqs",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "dizayn berish turlari qaysilar?",
                "description": "dizayn berish turlari qaysilar?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
            },
            {
                "exercise_type": "text_input",
                "title": "inline style dep nimaga aytamiz?",
                "description": "inline style dep nimaga aytamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "external style dep nimaga aytamiz?",
                "description": "external style dep nimaga aytamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "css style ozi nima?",
                "description": "css style ozi nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "nima dep oylaysiz dizayn berish nima uchun kerak?",
                "description": "nima dep oylaysiz dizayn berish nima uchun kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 4,
            },
        ],
    },
    {
        "order": 3, "title": "4-dars Class id",
        "text": L3_TEXT, "code": L3_CODE, "lang": "html",
        "video": "https://youtu.be/nSmlH1KTCl0",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "class ozi nima?",
                "description": "class ozi nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "id nima?",
                "description": "id nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
            },
            {
                "exercise_type": "text_input",
                "title": "clas va id ortasidagi farq nimada?",
                "description": "class va id ortasidagi farq nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
            },
            {
                "exercise_type": "multiple_choice",
                "title": "Quyidagi selectorlardan qaysi biri eng yuqori specificity ga ega?",
                "description": "Quyidagi selectorlardan qaysi biri eng yuqori specificity ga ega?",
                "options": [".card (class)", "#header (id)", "div (tag)", "* (universal)"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Specificity tartibi: tag < class < id < !important",
                "explanation": "id selectori class va tag dan kuchliroq. Lekin !important ulardan ham ustun.",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "Class va id ni qachon ishlatish kerak — farqi qanday?",
                "description": "Class va id ni qachon ishlatish kerak — farqi qanday?",
                "expected_answer": "class — bir necha elementga bir xil stil qo'llash uchun (qayta ishlatish). Sahifada bir xil class li bir nechta element bo'lishi mumkin: .card, .button. id — sahifada FAQAT BITTA element uchun unique identifikator. JavaScript getElementById, anchor link (#header) yoki form label uchun. Bir xil id ni ikki marta ishlatish HTML validatorda xato beradi.",
                "is_multiple_select": False,
                "hint": "class — ko'p element uchun, id — yagona element uchun.",
                "explanation": "class — reusable, id — unique. Ikkalasi ham CSS va JS dan ishlatiladi.",
                "difficulty_level": "Hard",
                "points": 4,
            },
        ],
    },
    {
        "order": 4, "title": "5-dars inline block va span",
        "text": L4_TEXT, "code": L4_CODE, "lang": "html",
        "video": "https://youtu.be/Dy9NXEV-sc4?feature=shared",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Exercise ",
                "description": "inline element nima?\n",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "block element nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "span nima vazifa bajaradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "span yordamida matn rangini o‘zgartiring",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "div va span farqi nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
        ],
    },
    {
        "order": 5, "title": "6-dars Div tegi",
        "text": L5_TEXT, "code": L5_CODE, "lang": "html",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "HTML exercise",
                "description": "Div nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "1 ta div yarating",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "2 ta div yarating va rang bering",
                "description": "2 ta div yarating va rang bering",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "div nima uchun ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "div ichiga matn yozing",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 2,
            },
        ],
    },
    {
        "order": 6, "title": "7-dars Display Flex",
        "text": L6_TEXT, "code": L6_CODE, "lang": "css",
        "video": "https://youtu.be/PPBn2w102lg?si=zgltriR55ZVxCsGl",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "flex nima?",
                "description": "flex nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "2 ta blokni yonma-yon chiqaring",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "3 ta blok qo‘shing",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "justify-content ishlating",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "flex qayerda ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
        ],
    },
    {
        "order": 7, "title": "8-dars Table",
        "text": L7_TEXT, "code": L7_CODE, "lang": "html",
        "video": "https://youtu.be/91h0E5HfSr8?si=PYvw6_YEKZKKZtkC",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "table nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "tr nima vazifa bajaradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "2 qatorli jadval yarating",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "th qo‘shing",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "",
                "description": "o‘zingiz haqingizda jadval yarating",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
        ],
    },
    {
        "order": 8, "title": "9-dars position",
        "text": L8_TEXT, "code": L8_CODE, "lang": "html",
        "video": "https://youtu.be/GFPfegCoLj0",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Position neshta turi bor? ",
                "description": "Position neshta turi bor? ",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "Position static nima ekan? ",
                "description": "Position static nima ekan? ",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "Position sticky nima uchun kerak? ",
                "description": "Position sticky nima uchun kerak? ",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "Ota elementda position realitive bolmasa div nimaga nisbatan joylashadi? ",
                "description": "Ota elementda position realitive bolmasa div nimaga nisbatan joylashadi? ",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
            },
            {
                "exercise_type": "multiple_choice",
                "title": "position: sticky qachon va qanday ishlaydi?",
                "description": "position: sticky qachon va qanday ishlaydi?",
                "options": ["Element scroll vaqtida belgilangan offset ga yetganda 'yopishadi' (fixed bo'ladi)", "Element har doim viewport ga yopishadi", "Element parent ichida absolute pozitsiyada turadi", "Element scroll bilan birga harakatlanadi va to'xtaydi"],
                "correct_answers": "A,D",
                "is_multiple_select": True,
                "hint": "Sticky — 'yopishuvchi' nav yoki sarlavhalar uchun. Bu relative va fixed ning aralashmasi.",
                "explanation": "Sticky element scroll holatiga qadar relative kabi, offset ga yetganda fixed kabi xatti-harakat qiladi.",
                "difficulty_level": "Medium",
                "points": 3,
            },
        ],
    },
    {
        "order": 9, "title": "10-dars before-after",
        "text": L9_TEXT, "code": L9_CODE, "lang": "html",
        "video": "https://youtu.be/VHEqRJtkFpM",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "::before elementni matnning qayeriga qo'shadi: boshigami yoki oxirigami?",
                "description": "::before elementni matnning qayeriga qo'shadi: boshigami yoki oxirigami?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "Agar biz CSS-da p::after { color: red; } deb yozsak-u, lekin ichiga content: \"\"; yozishni unutib qoldirsak, ekranda biror narsa ko'rinadimi?",
                "description": "Agar biz CSS-da p::after { color: red; } deb yozsak-u, lekin ichiga content: \"\"; yozishni unutib qoldirsak, ekranda biror narsa ko'rinadimi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
            },
            {
                "exercise_type": "text_input",
                "title": "HTML elementining o'zidan (masalan p) psevdo-elementni ajratib ko'rsatish uchun nechta nuqta ishlatiladi ( : yoki :: )?",
                "description": "HTML elementining o'zidan (masalan p) psevdo-elementni ajratib ko'rsatish uchun nechta nuqta ishlatiladi ( : yoki :: )?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
            },
            {
                "exercise_type": "text_input",
                "title": "::before orqali qo'shilgan belgi odatda o'zidan keyingi matnni yangi qatorga tushirib yuboradimi yoki bir qatorda turadimi? (Ya'ni u inline-mi yoki block?)",
                "description": "::before orqali qo'shilgan belgi odatda o'zidan keyingi matnni yangi qatorga tushirib yuboradimi yoki bir qatorda turadimi? (Ya'ni u inline-mi yoki block?)",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
            },
            {
                "exercise_type": "text_input",
                "title": "Bizda <p>Salom</p> bor. Agar biz CSS-da p::after { content: \"!\"; } deb yozsak, ekranda nima deb yoziladi?",
                "description": "Bizda <p>Salom</p> bor. Agar biz CSS-da p::after { content: \"!\"; } deb yozsak, ekranda nima deb yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 10,
            },
        ],
    },
    {
        "order": 10, "title": "11-dars animation",
        "text": L10_TEXT, "code": L10_CODE, "lang": "html",
        "video": "https://youtu.be/7I7CRiwSrK8",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Animatsiya yaratishda @keyframes nima uchun ishlatiladi?",
                "description": "Animatsiya yaratishda @keyframes nima uchun ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
            },
            {
                "exercise_type": "text_input",
                "title": "Animatsiya to‘xtovsiz, abadiy takrorlanib turishi uchun animation-iteration-count xossasiga qanday qiymat berish kerak?",
                "description": "Animatsiya to‘xtovsiz, abadiy takrorlanib turishi uchun animation-iteration-count xossasiga qanday qiymat berish kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "Animatsiya tugagandan keyin orqaga qaytishi (masalan, koptok borib, yana o‘z joyiga qaytib kelishi) uchun animation-direction xossasiga nima deb yoziladi?",
                "description": "Animatsiya tugagandan keyin orqaga qaytishi (masalan, koptok borib, yana o‘z joyiga qaytib kelishi) uchun animation-direction xossasiga nima deb yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "text_input",
                "title": "Animatsiya boshida sekin, o‘rtasida tez va oxirida yana sekinlashib tugashi uchun qaysi xossadan foydalanamiz?",
                "description": "Animatsiya boshida sekin, o‘rtasida tez va oxirida yana sekinlashib tugashi uchun qaysi xossadan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 4,
            },
            {
                "exercise_type": "text_input",
                "title": "Foydalanuvchi sichqonchani element ustiga olib kelganida (:hover), animatsiyani to‘xtatib (pauza qilib) qo‘yish mumkinmi? Agar mumkin bo‘lsa, qaysi xossa bilan?",
                "description": "Foydalanuvchi sichqonchani element ustiga olib kelganida (:hover), animatsiyani to‘xtatib (pauza qilib) qo‘yish mumkinmi? Agar mumkin bo‘lsa, qaysi xossa bilan?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
            },
        ],
    },
]


def _jdump(value):
    if value is None: return ""
    if isinstance(value, (list, dict)): return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson, exercise_rows):
    sections = [
        {"id": f"t{lesson['order']}", "type": "text", "label": "Текст", "html": lesson["text"], "order": 0},
        {"id": f"c{lesson['order']}", "type": "code", "label": "Код", "code": lesson["code"], "lang": lesson["lang"], "order": 1},
        {"id": f"v{lesson['order']}", "type": "video", "label": "Видео", "videoUrl": lesson["video"], "order": 2},
        {"id": f"e{lesson['order']}", "type": "exercise", "label": "Упражнения",
         "exercises": [{
             "_localId": e.id, "id": e.id,
             "title": e.title, "description": e.description,
             "exercise_type": e.exercise_type,
             "options": e.options or "", "correct_answers": e.correct_answers or "",
             "drag_items": e.drag_items or "", "correct_order": e.correct_order or "",
             "is_multiple_select": bool(e.is_multiple_select),
             "expected_answer": e.expected_answer or "",
             "hint": e.hint or "", "explanation": e.explanation or "",
             "difficulty_level": e.difficulty_level,
             "points": e.points, "order": e.order,
         } for e in exercise_rows],
         "order": 3},
    ]
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run=False):
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Course).where(Course.title == COURSE["title"]))).scalar_one_or_none()
        if existing:
            print(f"Course {COURSE['title']!r} already exists (id={existing.id}). Use refresh_html_css_text.py to update.")
            return
        course = Course(**COURSE)
        db.add(course); await db.flush()
        print(f"Created course id={course.id}")
        for ldata in LESSONS:
            task = LESSON_TASKS.get(ldata["order"], {})
            lesson = Lesson(
                course_id=course.id, title=ldata["title"], order=ldata["order"],
                points_reward=10, text_content=ldata["text"], code_content=ldata["code"],
                code_language=ldata["lang"], video_url=ldata["video"], sections_json=None,
                task_title=task.get("title"), task_description=task.get("description"),
                task_requirements=task.get("requirements"),
                task_technologies=task.get("technologies"),
                task_deadline_days=task.get("deadline_days"),
                is_active=True, is_published=True,
            )
            db.add(lesson); await db.flush()
            ex_rows = []
            for ex_order, ex in enumerate(ldata["exercises"]):
                row = Exercise(
                    lesson_id=lesson.id, title=ex["title"], description=ex.get("description", ex["title"]),
                    exercise_type=ex["exercise_type"],
                    options=_jdump(ex.get("options")),
                    correct_answers=_jdump(ex.get("correct_answers")),
                    drag_items=_jdump(ex.get("drag_items")),
                    correct_order=_jdump(ex.get("correct_order")),
                    is_multiple_select=bool(ex.get("is_multiple_select", False)),
                    expected_answer=ex.get("expected_answer", ""),
                    hint=ex.get("hint", ""), explanation=ex.get("explanation", ""),
                    difficulty_level=ex["difficulty_level"], points=ex["points"],
                    order=ex_order, is_active=True,
                )
                db.add(row); ex_rows.append(row)
            await db.flush()
            lesson.sections_json = build_sections_json(ldata, ex_rows)
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  ex={len(ex_rows)}  {lesson.title[:50]}")
        if dry_run:
            await db.rollback(); print("DRY RUN — rolled back")
        else:
            await db.commit(); print(f"Seeded {len(LESSONS)} lessons.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed(dry_run=("--dry-run" in sys.argv)))
