"""Seed "Capstone 6: Accessibility va Brauzer API" (7 lessons): combines Veb
Accessibility (a11y) and JavaScript: Brauzer API va Web into ONE project —
'AccessBoard', a real-time collaborative task board (vanilla HTML/CSS/JS +
a minimal Node/Express + ws backend as a WebSocket relay — no bot, no
frontend framework, no server-side database since IndexedDB handles
client-side persistence; single deploy unit).

Unlike Capstones 1-5, every lesson's deliberate bug belongs to yet another
family: the interface visibly, functionally "works" for the person building
it (mouse user, sighted user, an automated checker giving it a green score)
while silently excluding someone else (keyboard-only user, screen-reader
user, colorblind user, someone whose installed PWA never got the fix). Each
lesson shows this illusion in a different place (mouse-first design with no
keyboard equivalent, non-semantic clickable divs, focus stolen by a live
WebSocket re-render, color-only status with failing contrast, a
drag-and-drop feature with zero keyboard path, a stale service-worker
cache, and blind trust in an automated accessibility score).

Uses the same project-submission mechanism as every other capstone via
task_title/task_description/task_requirements/task_technologies/
task_deadline_days on Lesson — students build ONE evolving 'AccessBoard'
app across all 7 milestones, resubmitting the same (updated) github_url
each time via the existing Submission + AI-grading pipeline (GitHub URL
only). No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_accessibility
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py (see the
matching scripts/ru_capstone6_lesson_0X.py for each lesson).

STATUS: fill in LESSON_PLAN status "done" as each lesson's UZ + RU content
is written; run --dry-run after each to review before applying.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson_sample import LessonSample  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "Capstone 6: Accessibility va Brauzer API",
    "description": (
        "Veb Accessibility (a11y) va JavaScript: Brauzer API va Web "
        "kurslarini tugatgan dasturchilar uchun: ikkalasini BIR loyihada "
        "birlashtirasiz. 7 bosqichda 'AccessBoard' — real vaqtli jamoaviy "
        "vazifalar taxtasini (Trello uslubida) qurasiz: vanilla HTML/CSS/"
        "JS, WebSocket orqali real vaqtli sinxronizatsiya, IndexedDB "
        "orqali offline saqlash, Service Worker orqali PWA. Har bir "
        "bosqichda boshqa chegara bilan tanishasiz: interfeys sichqoncha "
        "uchun, ko'zi ko'radigan foydalanuvchi uchun, avtomatik tekshiruv "
        "vositasi uchun 'ishlab turgandek' ko'rinishi mumkin — lekin "
        "klaviatura yoki ekran o'quvchisidan foydalanuvchi uchun butunlay "
        "ishlamasligi mumkin. Har bir bosqich haqiqiy loyiha topshirig'i "
        "sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 6,  # HTML & CSS
    "prerequisite_course_id": 68,  # JavaScript: Brauzer API va Web (also assumes course 57: Veb Accessibility a11y)
    "is_active": True,
    "is_published": False,  # flip to True once all 7 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done", "lang": "javascript",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "Document outline, keyboard-first interaction plan for AccessBoard, repo scaffold."},
    {"order": 1, "ref": "L2", "status": "done", "lang": "javascript",
     "title": "2-Semantic HTML + ARIA asoslari",
     "scope": "Board/column/card markup with real elements and ARIA; the clickable-div anti-pattern."},
    {"order": 2, "ref": "L3", "status": "done", "lang": "javascript",
     "title": "3-Klaviatura Navigatsiyasi + WebSocket",
     "scope": "Full keyboard navigation + live sync; missing focus outline and WebSocket re-renders stealing focus."},
    {"order": 3, "ref": "L4", "status": "done", "lang": "javascript",
     "title": "4-Rang Kontrasti + IndexedDB",
     "scope": "Offline-first storage; color-only status indicators and failing contrast ratios."},
    {"order": 4, "ref": "L5", "status": "done", "lang": "javascript",
     "title": "5-Forms Accessibility + File API/Drag-and-Drop",
     "scope": "Attachment upload + card edit form; drag-and-drop with zero keyboard path."},
    {"order": 5, "ref": "L6", "status": "done", "lang": "javascript",
     "title": "6-Service Worker + PWA",
     "scope": "Installable offline app; a stale cache-first service worker hiding shipped a11y fixes."},
    {"order": 6, "ref": "L7", "status": "done", "lang": "javascript",
     "title": "7-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "Final audit and deploy; trusting an automated accessibility score alone."},
]


L1_TEXT = """\
<h2>AccessBoard — 7 bosqichda accessibility va brauzer API'lari orqali qurilgan loyiha</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> HTML["2-Semantic HTML + ARIA"]
    HTML --> KEY["3-Klaviatura + WebSocket"]
    KEY --> COLOR["4-Rang kontrasti + IndexedDB"]
    COLOR --> FORM["5-Forms + Drag-and-Drop"]
    FORM --> PWA["6-Service Worker + PWA"]
    PWA --> DEPLOY["7-Deploy (CAPSTONE yakuni)"]
</pre>

<p>Bu kursda siz Veb Accessibility va JavaScript: Brauzer API va Web kurslarida <strong>alohida</strong> o'rgangan hamma narsani <strong>bitta haqiqiy loyiha</strong>da birlashtirasiz: <strong>AccessBoard</strong> — real vaqtli jamoaviy vazifalar taxtasi (Trello uslubida). Har bir dars — shu bitta loyihaning navbatdagi bosqichi.</p>

<p>Bu capstone oldingi beshtasidan bir narsa bilan farq qiladi: bu safar "ataylab xato" — kodning <strong>o'zi buzilgan</strong> degani emas. Kod <strong>ishlaydi</strong>, sinov ham "yashil" bo'lishi mumkin — lekin faqat <strong>siz</strong> uchun: sichqoncha bilan, ko'zingiz bilan, standart brauzerda sinaganingizda. Har bir bosqich shuni ko'rsatadi: interfeys <strong>sizga</strong> ishlab turgandek tuyulishi, uni <strong>boshqacha</strong> foydalanadigan odam uchun ishlashini kafolatlamaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo skeleton: frontend + minimal WebSocket server</h4>
<pre><code># AccessBoard uchun repo tuzilmasi
accessboard/
  frontend/
    index.html
    style.css
    app.js
    sw.js               # ❗ 6-darsda to'ldiriladi - Service Worker
  server/
    server.js           # Express + ws - statik fayllarni beradi + WebSocket relay
    package.json
  README.md
  .gitignore

# Backend BU YERDA ATAYLAB minimal - bazasi yo'q, faqat WebSocket orqali
# xabarlarni uzatadi. Haqiqiy ma'lumot IndexedDB orqali BRAUZERNING
# o'zida saqlanadi (4-darsda).</code></pre>

<h4>BLOKA 2 — hujjat sxemasi (document outline): semantik tuzilma REJASI</h4>
<pre><code># AccessBoard'ning semantik tuzilmasi (hali HTML emas - reja):
#
# <header>   - taxta nomi, foydalanuvchi ma'lumoti
# <nav>      - taxtalar ro'yxati (agar bir nechta taxta bo'lsa)
# <main>
#   <section> har bir ustun (masalan "Bajarilmoqda", "Tayyor")
#     <ul>    - shu ustundagi kartalar ro'yxati
#       <li>  - har bir vazifa kartasi
# <footer>   - qo'shimcha havolalar
#
# Bu tuzilma ekran o'quvchisi (screen reader) foydalanuvchisiga
# sahifani "eshitib" tushunish imkonini beradi - HTML elementlarining
# TABIIY ma'nosidan foydalangan holda.</code></pre>

<h4>BLOKA 3 — klaviatura-birinchi o'zaro ta'sir rejasi</h4>
<pre><code># Har bir sichqoncha bilan bajariladigan harakat uchun, ALDINDAN,
# klaviatura ORQALI qanday bajarilishi REJALASHTIRILADI:
#
# Sichqoncha harakati              ->  Klaviatura ekvivalenti
# ────────────────────────────────────────────────────────────
# Kartani sichqoncha bilan sudrab   ->  Enter bilan kartani "tanlash",
# boshqa ustunga tashlash               keyin Arrow tugmalari bilan
#                                        ustunlar orasida ko'chirish,
#                                        Enter bilan tasdiqlash
# Faylni sichqoncha bilan sudrab    ->  "Fayl tanlash" tugmasi (input
# yuklash                               type="file") - klaviatura bilan
#                                        ham ochiladigan</code></pre>

<h3>🐛 Ataylab qiyin: sichqoncha uchun o'ylab, "klaviaturani keyin qo'shaman" deb qoldirish</h3>
<p>Ko'p dasturchilar drag-and-drop (kartani sudrab ko'chirish) kabi interaktiv funksiyani <strong>avval sichqoncha uchun</strong> loyihalab, "klaviatura qo'llab-quvvatlashini keyinroq qo'shaman" deb rejalashtiradi:</p>
<pre><code>// "Hozircha faqat sichqoncha uchun ishlaydi, keyin klaviatura
// qo'shaman" deb o'ylab, faqat drag/drop hodisalari bilan yozish:
card.addEventListener('dragstart', handleDragStart);
card.addEventListener('dragend', handleDragEnd);
column.addEventListener('drop', handleDrop);
// Klaviatura uchun HECH QANDAY reja yo'q - keydown, focus, ARIA
// live region kabi tushunchalar HALI umuman ko'rib chiqilmagan.</code></pre>
<p><strong>Natija:</strong> drag-and-drop hodisalari (<code>dragstart</code>, <code>drop</code>) va klaviatura hodisalari (<code>keydown</code>, <code>focus</code>) — <strong>butunlay boshqa</strong> hodisa modeli va foydalanuvchi tajribasi mantig'iga asoslangan. Agar avval faqat sichqoncha uchun kod yozilsa, keyinroq klaviatura qo'llab-quvvatlashini "qo'shish" — bu ko'pincha butun o'zaro ta'sir mantig'ini <strong>qayta yozish</strong>ga teng, chunki ikkalasi bir xil "harakat" tushunchasini <strong>ikki xil</strong> yo'l bilan ifodalaydi. To'g'ri yondashuv: har ikkala kirish usulini <strong>boshidanoq birga</strong> loyihalash.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega backend bu safar ataylab minimal — bazasi yo'q?</h4>
<p>Bu capstone'ning maqsadi — accessibility va brauzer API'larini chuqur o'rganish, murakkab backend arxitekturasini emas. WebSocket server faqat foydalanuvchilar orasida xabar "estafeta"si vazifasini bajaradi; haqiqiy saqlash <strong>IndexedDB</strong> orqali brauzerning o'zida amalga oshadi (4-darsda ko'rasiz).</p>

<h4>2. Hujjat sxemasi (document outline) nima uchun muhim?</h4>
<p>Ekran o'quvchisi foydalanuvchilari sahifani <strong>vizual</strong> emas, balki <strong>eshitib</strong> tushunishadi. To'g'ri semantik tuzilma (<code>header</code>, <code>nav</code>, <code>main</code>, <code>section</code>) — bu foydalanuvchilarga sahifaning "xaritasi"ni beradi, ular sahifa bo'ylab tezda harakatlanishlariga yordam beradi.</p>

<h4>3. Nega "klaviatura ekvivalenti" jadvali kod yozishdan OLDIN tuziladi?</h4>
<p>Agar har bir sichqoncha harakati uchun klaviatura ekvivalenti <strong>oldindan</strong> aniq belgilansa, kod yozish paytida "buni klaviatura bilan qanday qilish mumkin?" degan savol <strong>hech qachon</strong> keyinga qoldirilmaydi — bu savolga javob loyihalash bosqichidayoq berilgan bo'ladi.</p>

<h4>4. Drag-and-drop va klaviatura hodisalari nega "butunlay boshqa" hisoblanadi?</h4>
<p><code>dragstart</code>/<code>drop</code> — sichqoncha (yoki teginish) harakatlariga bog'liq brauzer hodisalari. <code>keydown</code>/<code>focus</code> — klaviatura va fokus holatiga bog'liq, butunlay boshqa hodisalar. Ular orasida <strong>avtomatik</strong> hech qanday bog'liqlik yo'q — ikkalasini ham qo'llab-quvvatlash uchun ikkalasi uchun <strong>alohida</strong> mantiq yozish kerak.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — capstone davomida qaytarilaydigan asosiy g'oyaning <strong>birinchi</strong> ko'rinishi: accessibility — loyihaning oxirida "qo'shiladigan" narsa emas, balki <strong>boshidanoq</strong> qaror qabul qilinadigan dizayn tanlovi. Keyingi darslarda buni e'tiborsiz qoldirishning aniq oqibatlarini ko'rasiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Bu capstone'da backend ataylab minimal — asosiy e'tibor frontend accessibility va brauzer API'lariga qaratilgan</li>
<li>✅ To'g'ri semantik tuzilma (document outline) ekran o'quvchisi foydalanuvchilariga sahifa "xaritasi"ni beradi</li>
<li>✅ Har bir sichqoncha harakati uchun klaviatura ekvivalenti kod yozishdan OLDIN rejalashtirilishi kerak</li>
<li>✅ Drag-and-drop va klaviatura hodisalari butunlay boshqa hodisa modellariga asoslangan</li>
<li>✅ Accessibility — loyihaning oxirida qo'shiladigan narsa emas, boshidanoq qabul qilinadigan dizayn qarori</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 1-BOSQICH: Loyihalash va repo skeleton
// ════════════════════════════════════════════════════════════════════

// Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.

// ─────────────────────────────────────────────────────────────────────
// Repo tuzilmasi (izohda - papka/fayl tuzilmasi, kod emas)
// ─────────────────────────────────────────────────────────────────────

// accessboard/
//   frontend/
//     index.html
//     style.css
//     app.js
//     sw.js               (6-darsda to'ldiriladi)
//   server/
//     server.js           (Express + ws)
//     package.json
//   README.md
//   .gitignore

// ─────────────────────────────────────────────────────────────────────
// server/server.js - minimal WebSocket relay (bazasiz)
// ─────────────────────────────────────────────────────────────────────

const express = require('express');
const { WebSocketServer } = require('ws');

const app = express();
app.use(express.static('../frontend'));

const server = app.listen(3000, () => console.log('AccessBoard: http://localhost:3000'));
const wss = new WebSocketServer({ server });

wss.on('connection', (socket) => {
  socket.on('message', (data) => {
    // Kelgan xabarni BOSHQA barcha ulangan klientlarga uzatish
    wss.clients.forEach((client) => {
      if (client !== socket && client.readyState === client.OPEN) {
        client.send(data.toString());
      }
    });
  });
});

// ─────────────────────────────────────────────────────────────────────
// Ataylab qiyin - faqat sichqoncha uchun reja (izohda)
// ─────────────────────────────────────────────────────────────────────

// card.addEventListener('dragstart', handleDragStart);
// card.addEventListener('dragend', handleDragEnd);
// column.addEventListener('drop', handleDrop);
// Klaviatura uchun HECH QANDAY reja yo'q - keydown/focus/ARIA live
// region hali umuman ko'rib chiqilmagan.
"""

L1_EX = [
    {
        "title": "Bu capstone'da backend nega ataylab minimal?",
        "description": "AccessBoard'ning WebSocket server'i nega bazasiz, faqat xabar 'estafeta'si vazifasini bajaradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki Node.js bazalar bilan ishlay olmaydi",
            "Chunki bu capstone'ning maqsadi accessibility va brauzer API'larini chuqur o'rganish - haqiqiy saqlash IndexedDB orqali brauzerning o'zida amalga oshadi",
            "Chunki WebSocket bazalar bilan mos kelmaydi",
            "Chunki bu vaqtinchalik yechim, keyinroq baza qo'shiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu capstone'ning asosiy e'tibori nimaga qaratilgan?",
        "explanation": "Bu capstone'ning maqsadi accessibility va brauzer API'larini chuqur o'rganish, murakkab backend arxitekturasini emas - WebSocket server faqat xabar estafetasi, haqiqiy saqlash IndexedDB orqali brauzerda amalga oshadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Document outline (hujjat sxemasi) nima uchun muhim?",
        "description": "To'g'ri semantik tuzilma (header, nav, main, section) ekran o'quvchisi foydalanuvchilari uchun nima uchun muhim?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu sahifani tezroq yuklaydi",
            "Bu foydalanuvchilarga sahifaning 'xaritasi'ni beradi - ular sahifani vizual emas, eshitib tushunishadi va shu tuzilma bo'ylab tezda harakatlanishadi",
            "Chunki qidiruv tizimlari faqat semantik HTML'ni indekslaydi",
            "Chunki CSS faqat semantik elementlarga qo'llaniladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ekran o'quvchisi foydalanuvchisi sahifani qanday 'ko'radi'?",
        "explanation": "Ekran o'quvchisi foydalanuvchilari sahifani eshitib tushunishadi - to'g'ri semantik tuzilma ularga sahifaning xaritasini beradi va tezda harakatlanish imkonini yaratadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "AccessBoard'ni rejalashtirish jarayonini tartiblang",
        "description": "AccessBoard uchun 1-bosqichning to'g'ri rejalashtirish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Repo skeleton yaratiladi (frontend/ va server/ papkalari bilan)",
            "Semantik hujjat sxemasi (header/nav/main/section) rejalashtiriladi",
            "Har bir sichqoncha harakati uchun klaviatura ekvivalenti jadvali tuziladi",
            "Minimal WebSocket relay server yoziladi",
        ],
        "correct_order": [
            "Repo skeleton yaratiladi (frontend/ va server/ papkalari bilan)",
            "Semantik hujjat sxemasi (header/nav/main/section) rejalashtiriladi",
            "Har bir sichqoncha harakati uchun klaviatura ekvivalenti jadvali tuziladi",
            "Minimal WebSocket relay server yoziladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Kartani ko'chirishning klaviatura ekvivalenti",
        "description": "Sichqoncha bilan kartani sudrab boshqa ustunga tashlash (drag-and-drop) harakatining klaviatura ekvivalenti sifatida qaysi ikkita tugma turkumi ishlatiladi? (ikkalasini vergul bilan ajratib yozing)",
        "exercise_type": "text_input",
        "expected_answer": "Enter, Arrow",
        "hint": "Birinchisi 'tanlash/tasdiqlash' uchun, ikkinchisi ustunlar orasida ko'chirish uchun.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega drag-and-drop'ni avval qurib, klaviaturani keyin qo'shish qiyin?",
        "description": (
            "Agar dasturchi drag-and-drop funksiyasini AVVAL faqat "
            "sichqoncha hodisalari (dragstart/drop) bilan qursa, "
            "keyinroq klaviatura qo'llab-quvvatlashini 'qo'shish' nega "
            "oddiy qo'shimcha emas, balki qiyin ish bo'lib chiqadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Drag-and-drop hodisalari (dragstart, dragend, drop) va "
            "klaviatura hodisalari (keydown, focus) butunlay boshqa "
            "hodisa modeliga va foydalanuvchi tajribasi mantig'iga "
            "asoslangan - ular orasida avtomatik hech qanday bog'liqlik "
            "yo'q. Agar kod boshidanoq FAQAT drag/drop hodisalari atrofida "
            "qurilgan bo'lsa (masalan holat faqat drag paytida saqlanadigan "
            "qilib loyihalangan bo'lsa), klaviatura qo'llab-quvvatlashini "
            "qo'shish odatda shunchaki yangi event listener qo'shish emas, "
            "balki butun 'kartani tanlash va ko'chirish' mantig'ini "
            "boshqa asosda (fokus va holat boshqaruvi asosida) QAYTA "
            "YOZISHni talab qiladi."
        ),
        "hint": "dragstart/drop va keydown/focus - bir xil 'harakat' tushunchasini bir xil usulda ifodalaydimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "AccessBoard — repo skeleton va klaviatura-birinchi reja hujjati",
    "task_description": (
        "AccessBoard loyihasi uchun GitHub'da repo yarating (frontend/ va "
        "server/ papkalari bilan), to'liq README.md yozing (semantik "
        "hujjat sxemasi va klaviatura ekvivalentlari jadvali bilan), va "
        "minimal Express + ws WebSocket relay server yozing."
    ),
    "task_requirements": (
        "• GitHub'da 'accessboard' nomli public repo yaratilgan\n"
        "• frontend/ va server/ papkalari mavjud\n"
        "• README.md: loyiha tavsifi, semantik hujjat sxemasi (header/nav/main/section), texnologiyalar, holat checklist'i\n"
        "• README.md ichida kamida 3 ta sichqoncha harakati va ularning klaviatura ekvivalenti jadvalda ko'rsatilgan\n"
        "• server/server.js: Express statik fayllarni beradi, ws orqali WebSocket xabarlarini boshqa klientlarga uzatadi\n"
        "• .gitignore fayli mavjud (node_modules, .env chiqarib tashlangan)"
    ),
    "task_technologies": "HTML, CSS, JavaScript, Node.js, Express, WebSocket (ws), Git, GitHub",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Semantic HTML + ARIA asoslari — "klikланadigan div" xatosi</h2>

<pre class="mermaid">
flowchart LR
    CARD["Vazifa kartasi - bosilganda ochiladi"] --> CHOICE{"&lt;div onclick&gt; yoki &lt;button&gt;?"}
    CHOICE -->|"&lt;div onclick&gt;"| INVISIBLE["Ekran o'quvchisi: karta - oddiy matn, hech qanday rol yo'q"]
    CHOICE -->|"&lt;button&gt;"| VISIBLE["Ekran o'quvchisi: 'Tugma, ...' deb e'lon qilinadi, Tab bilan yetib boriladi"]
    INVISIBLE --> BLOCKED["Klaviatura foydalanuvchisi kartani OCHIRA OLMAYDI"]
</pre>

<p>Veb Accessibility kursida semantik HTML va ARIA rollarini allaqachon o'rgangansiz. Bu darsda ularni AccessBoard'ning yuragi — taxta, ustun va kartalar tuzilmasi — ga qo'llaysiz. Bu safar bug crash bermaydi, konsolda xato chiqmaydi — kod <strong>xuddi rejalashtirilgandek ishlaydi</strong>, siz sichqoncha bilan bosganingizda. Muammo faqat <strong>boshqacha</strong> sinaganingizda ko'rinadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — semantik tuzilma: taxta, ustun, karta</h4>
<pre><code>&lt;main&gt;
  &lt;section aria-labelledby="col-todo-heading"&gt;
    &lt;h2 id="col-todo-heading"&gt;Bajarilmoqda&lt;/h2&gt;
    &lt;ul class="card-list"&gt;
      &lt;li&gt;
        &lt;button class="card" type="button"&gt;
          Login sahifasini tuzatish
        &lt;/button&gt;
      &lt;/li&gt;
    &lt;/ul&gt;
  &lt;/section&gt;
&lt;/main&gt;

&lt;!-- ❗ &lt;button&gt; - NATIV element: brauzer AVTOMATIK ravishda
     unga rol="button", tabindex, Enter/Space orqali faollashtirishni
     beradi. Hech qanday qo'shimcha ARIA kerak emas! --&gt;</code></pre>

<h4>BLOKA 2 — ARIA faqat native element YETARLI bo'lmaganda</h4>
<pre><code>&lt;!-- Agar dizayn talabiga ko'ra &lt;button&gt; ishlatib bo'lmasa
     (masalan, karta ICHIDA boshqa interaktiv elementlar bo'lsa),
     ARIA orqali qo'lda "tugma" xususiyatlarini qo'shish kerak: --&gt;
&lt;li
  class="card"
  role="button"
  tabindex="0"
  aria-describedby="card-1-status"
&gt;
  Login sahifasini tuzatish
  &lt;span id="card-1-status" class="sr-only"&gt;Holat: bajarilmoqda&lt;/span&gt;
&lt;/li&gt;

&lt;!-- LEKIN: role="button" + tabindex="0" qo'shish YETARLI EMAS -
     Enter/Space bosilganda funksiyani chaqiruvchi JS ham YOZILISHI
     kerak (native &lt;button&gt;da bu BEPUL keladi, custom'da YO'Q). --&gt;</code></pre>

<h4>BLOKA 3 — "birinchi qoida": native element bormi? Uni ishlating</h4>
<pre><code># ARIA Authoring Practices'ning "birinchi qoidasi":
# Agar vazifangiz uchun mos NATIV HTML elementi (masalan <button>,
# <a href>, <input>) mavjud bo'lsa - o'sha elementni ishlating.
# ARIA'ni faqat native element YETARLI bo'lmagan HOLATLARDA qo'shing.
#
# Nega? Chunki native elementlar rol, klaviatura xatti-harakati,
# fokus boshqaruvini AVTOMATIK, brauzerning o'zi tomonidan to'g'ri
# amalga oshiradi - ARIA esa faqat "e'lon qiladi", xatti-harakatni
# o'zi TA'MINLAMAYDI.</code></pre>

<h3>🐛 Ataylab xato — karta uchun &lt;div onclick&gt; ishlatish</h3>
<pre><code>&lt;!-- "Tezroq yozaman, div'ga onclick qo'shsam bo'ladi" deb: --&gt;
&lt;div class="card" onclick="openCard(1)"&gt;
  Login sahifasini tuzatish
&lt;/div&gt;

&lt;!-- CSS bilan bu &lt;button&gt;dan VIZUAL jihatdan FARQ QILMAYDI -
     xuddi shunday ko'rinadi, sichqoncha bilan bosilganda ISHLAYDI. --&gt;</code></pre>

<p><strong>Natija:</strong> <code>&lt;div onclick&gt;</code> vizual jihatdan mukammal ishlaydi — sichqoncha bilan sinaganingizda hech qanday farq sezmaysiz. Lekin <code>&lt;div&gt;</code> — <strong>semantik jihatdan neytral</strong> element: unda tabiiy ravishda <strong>na</strong> rol (screen reader uni oddiy matn deb hisoblaydi, "tugma" emas), <strong>na</strong> klaviatura fokusi (<code>tabindex</code>siz <code>Tab</code> tugmasi uni <strong>umuman o'tkazib yuboradi</strong>), <strong>na</strong> klaviatura orqali faollashtirish (<code>onclick</code> faqat sichqoncha bosilishiga <strong>javob beradi</strong> — <code>Enter</code> yoki <code>Space</code> bosilganda <strong>hech narsa</strong> sodir bo'lmaydi) mavjud. Natija: klaviatura yoki ekran o'quvchisidan foydalanuvchi uchun <strong>butun ilovaning asosiy funksiyasi</strong> — kartani ochish — <strong>butunlay yopiq</strong> qoladi, garchi kod "ishlab tursa" ham.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega <code>&lt;button&gt;</code> ARIA'siz ham "tugma kabi" ishlaydi?</h4>
<p><code>&lt;button&gt;</code> — brauzerning <strong>o'zi</strong> tomonidan avtomatik ravishda <code>role="button"</code>, klaviatura fokusi (<code>tabindex</code>), va <code>Enter</code>/<code>Space</code> orqali faollashtirish bilan <strong>ta'minlangan</strong>. Bularning barchasi brauzer ichida <strong>o'rnatilgan</strong> — dasturchi ularni qo'lda yozishi shart emas.</p>

<h4>2. <code>&lt;div onclick&gt;</code>da nima YETISHMAYDI?</h4>
<p><code>&lt;div&gt;</code> — semantik jihatdan <strong>hech qanday</strong> maxsus ma'noga ega emas (u shunchaki "konteyner"). <code>onclick</code> atributi faqat sichqoncha (yoki teginish) hodisasiga <strong>javob beradi</strong> — u avtomatik ravishda <code>role</code>, <code>tabindex</code>, yoki klaviatura hodisalarini <strong>qo'shmaydi</strong>. Bularning har biri <strong>qo'lda</strong> yozilishi kerak.</p>

<h4>3. "Birinchi qoida" (ARIA First Rule) nima?</h4>
<p>Agar vazifa uchun mos <strong>native</strong> HTML elementi mavjud bo'lsa (<code>&lt;button&gt;</code>, <code>&lt;a href&gt;</code>, <code>&lt;input&gt;</code>), <strong>o'shani</strong> ishlatish kerak — ARIA'ni faqat native element <strong>haqiqatan yetarli bo'lmagan</strong> holatlarda (masalan murakkab custom komponentlar) qo'shish tavsiya etiladi. ARIA — <strong>qo'shimcha</strong> vosita, native HTML'ning <strong>o'rnini bosuvchi</strong> emas.</p>

<h4>4. Nega bu xato "ko'rinmas" — hech qanday konsol xatosi bermaydi?</h4>
<p>JavaScript nuqtai nazaridan <code>onclick</code> to'g'ri ishlaydi — funksiya chaqiriladi, xato tashlanmaydi. Muammo <strong>faqat</strong> boshqacha kirish usuli (klaviatura) yoki boshqacha tarqatish vositasi (ekran o'quvchisi) bilan sinalganda ko'rinadi — bu esa oddiy, faqat sichqoncha bilan sinovdan o'tkazishda <strong>hech qachon</strong> aniqlanmasligini bildiradi.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>1-darsda "klaviaturani keyin qo'shaman" degan xavfni nazariy ko'rgan edingiz. Bu darsda uni <strong>eng oddiy, eng tez-tez uchraydigan</strong> ko'rinishida ko'rdingiz: bitta noto'g'ri element tanlovi (<code>div</code> o'rniga <code>button</code>) butun funksiyani bir foydalanuvchi guruhi uchun <strong>butunlay</strong> yo'qqa chiqarishi mumkin — hech qanday murakkab sabab, faqat noto'g'ri HTML elementi tufayli.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>&lt;button&gt;</code> rol, klaviatura fokusi va faollashtirishni brauzerdan AVTOMATIK oladi</li>
<li>✅ <code>&lt;div onclick&gt;</code> — semantik jihatdan neytral, hech qanday accessibility xususiyatini o'zi bilan olib kelmaydi</li>
<li>✅ "Birinchi qoida": mos native element bo'lsa, o'shani ishlating, ARIA'ni faqat zarurat bo'lganda qo'shing</li>
<li>✅ Bunday xato konsolda ko'rinmaydi - faqat klaviatura/ekran o'quvchisi bilan sinaganda aniqlanadi</li>
<li>✅ Bitta noto'g'ri element tanlovi butun funksiyani bir foydalanuvchi guruhi uchun butunlay yopib qo'yishi mumkin</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 2-BOSQICH: Semantic HTML + ARIA asoslari
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) index.html - semantik tuzilma, native <button> bilan (izohda - HTML)
// ─────────────────────────────────────────────────────────────────────

// <main>
//   <section aria-labelledby="col-todo-heading">
//     <h2 id="col-todo-heading">Bajarilmoqda</h2>
//     <ul class="card-list">
//       <li>
//         <button class="card" type="button" data-card-id="1">
//           Login sahifasini tuzatish
//         </button>
//       </li>
//     </ul>
//   </section>
// </main>

// ─────────────────────────────────────────────────────────────────────
// 2) app.js - kartalarni ochish, native button'ga tayanib
// ─────────────────────────────────────────────────────────────────────

document.querySelectorAll('.card').forEach((card) => {
  card.addEventListener('click', () => {
    openCard(card.dataset.cardId);
  });
  // Qo'shimcha kod SHART EMAS - <button> Enter/Space'ni ham
  // avtomatik 'click' hodisasiga aylantiradi!
});

function openCard(cardId) {
  console.log(`Karta ${cardId} ochildi`);
}

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - <div onclick> (izohda - HTML)
// ─────────────────────────────────────────────────────────────────────

// <div class="card" onclick="openCard(1)">
//   Login sahifasini tuzatish
// </div>
// Vizual jihatdan bir xil ko'rinadi, sichqoncha bilan ishlaydi -
// lekin klaviatura bilan UMUMAN yetib bo'lmaydi, ekran o'quvchisi
// uni oddiy matn deb hisoblaydi.
"""

L2_EX = [
    {
        "title": "Nega <button> ARIA'siz ham 'tugma kabi' ishlaydi?",
        "description": "<button> elementi qo'shimcha ARIA atributlarisiz ham klaviatura orqali faollashtirilishi mumkinligining sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki barcha brauzerlar <button>ni maxsus CSS bilan bezaydi",
            "Chunki brauzer <button>ga avtomatik rol, klaviatura fokusi va Enter/Space orqali faollashtirishni ta'minlaydi",
            "Chunki <button> har doim JavaScript'siz ishlaydi",
            "Chunki <button> HTML5'da yangi qo'shilgan",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu xususiyatlar qayerdan - dasturchi yozganidanmi, yoki brauzerning o'zidanmi keladi?",
        "explanation": "<button> brauzerning o'zi tomonidan avtomatik ravishda role='button', tabindex va Enter/Space orqali faollashtirish bilan ta'minlangan - bularning barchasi brauzer ichida o'rnatilgan.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "<div onclick>da nima yetishmaydi?",
        "description": "<div onclick=\"...\"> ishlatilganda, <button>dan farqli, klaviatura foydalanuvchisi uchun nima YETISHMAYDI?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa yetishmaydi, ikkalasi bir xil ishlaydi",
            "Rol, klaviatura fokusi (tabindex) va Enter/Space orqali faollashtirish - bularning hech biri div'ga avtomatik qo'shilmaydi",
            "Faqat CSS uslublari yetishmaydi",
            "Faqat rang kontrasti yetishmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "div - semantik jihatdan qanday element?",
        "explanation": "div semantik jihatdan neytral element - onclick faqat sichqoncha hodisasiga javob beradi, u avtomatik ravishda rol, tabindex yoki klaviatura hodisalarini qo'shmaydi, bularning har biri qo'lda yozilishi kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Klaviatura foydalanuvchisi kartani ocholmasligi jarayonini tartiblang",
        "description": "<div onclick> bilan yozilgan karta, klaviatura foydalanuvchisi uchun qanday qilib butunlay ishlamay qolishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Karta <div onclick=\"openCard(1)\"> sifatida yoziladi, tabindex yo'q",
            "Klaviatura foydalanuvchisi Tab tugmasini bosadi - div FOKUSGA UMUMAN kirmaydi",
            "Ekran o'quvchisi kartani oddiy matn deb e'lon qiladi, 'tugma' emas",
            "Foydalanuvchi kartani hech qanday usul bilan ocholmaydi - funksiya butunlay yopiq",
        ],
        "correct_order": [
            "Karta <div onclick=\"openCard(1)\"> sifatida yoziladi, tabindex yo'q",
            "Klaviatura foydalanuvchisi Tab tugmasini bosadi - div FOKUSGA UMUMAN kirmaydi",
            "Ekran o'quvchisi kartani oddiy matn deb e'lon qiladi, 'tugma' emas",
            "Foydalanuvchi kartani hech qanday usul bilan ocholmaydi - funksiya butunlay yopiq",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "ARIA qo'llash tartibidagi asosiy qoida",
        "description": "Agar vazifa uchun mos native HTML elementi mavjud bo'lsa, ARIA rollarini qo'shishdan oldin nima qilish tavsiya etiladi? (bitta so'z/ibora bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "native elementni ishlatish",
        "hint": "Bu ARIA Authoring Practices'ning 'birinchi qoidasi'.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bu xato konsolda hech qanday xato bermaydi?",
        "description": (
            "<div onclick> bilan yozilgan karta xatosi nega brauzer "
            "konsolida hech qanday xato yoki ogohlantirish bermaydi, "
            "garchi u butun bir foydalanuvchi guruhi uchun ilovani "
            "ishlatib bo'lmaydigan qilib qo'ysa ham? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "JavaScript nuqtai nazaridan onclick to'g'ri ishlayapti - "
            "funksiya chaqirilyapti, hech qanday sintaktik yoki runtime "
            "xatosi yo'q. Muammo kodning o'zida emas, balki foydalanuvchi "
            "TAJRIBASIDA - aniqrog'i, kod faqat BITTA kirish usuli "
            "(sichqoncha) bilan sinalganda hech qanday muammo ko'rinmaydi. "
            "Muammo faqat kimdir ilovani boshqacha usul bilan (klaviatura "
            "bilan Tab bosib, yoki ekran o'quvchisi bilan) sinaganda "
            "namoyon bo'ladi - va odatiy, faqat sichqoncha bilan qilinadigan "
            "qo'lda sinovlar bu holatni hech qachon aniqlamaydi."
        ),
        "hint": "Bu xato JavaScript darajasidami, yoki foydalanuvchi tajribasi darajasidami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "AccessBoard — Semantic HTML + ARIA asoslari (taxta tuzilmasi)",
    "task_description": (
        "AccessBoard'ning statik tuzilmasini (taxta, ustunlar, kartalar) "
        "semantik HTML bilan quring. Barcha interaktiv kartalar uchun "
        "native <button> ishlating (yoki, agar bu mumkin bo'lmasa, "
        "role='button' + tabindex='0' + klaviatura hodisasi bilan)."
    ),
    "task_requirements": (
        "• Taxta tuzilmasi: <main>, <section aria-labelledby>, <h2>, <ul>/<li> orqali qurilgan\n"
        "• Har bir vazifa kartasi <button> (yoki mos ARIA role/tabindex bilan) sifatida yozilgan\n"
        "• Hech qanday interaktiv element uchun <div onclick> yoki <span onclick> ISHLATILMAGAN\n"
        "• Tab tugmasi bilan barcha kartalarga ketma-ket yetib borish mumkinligi tasdiqlangan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, JavaScript, ARIA, semantic HTML",
    "task_deadline_days": 4,
}


L3_TEXT = """\
<h2>3-bosqich: Klaviatura Navigatsiyasi + WebSocket — fokus qanday "yo'qoladi"</h2>

<pre class="mermaid">
flowchart LR
    NAV["Klaviatura foydalanuvchisi 3-kartaga fokusda"] --> WS["Boshqa foydalanuvchi kartani ko'chiradi - WebSocket xabari keladi"]
    WS --> RENDER["boardEl.innerHTML = ... - BUTUN DOM qayta yaratiladi"]
    RENDER --> LOST["Eski fokusdagi element YO'Q QILINADI, fokus document.body'ga o'tadi"]
    LOST --> CONFUSED["Foydalanuvchi QAYERDA ekanini yo'qotadi, Tab'ni BOSHIDAN boshlashga majbur"]
</pre>

<p>Veb Accessibility kursida klaviatura navigatsiyasini, JavaScript: Brauzer API kursida esa WebSocket'ni allaqachon o'rgangansiz. Bu darsda ularni birlashtirasiz: AccessBoard'da to'liq klaviatura navigatsiyasi VA real vaqtli sinxronizatsiyani qurasiz. Lekin bu ikkalasi <strong>birga</strong> ishlatilganda, birinchisida ko'rinmagan yangi xavf paydo bo'ladi: <strong>WebSocket orqali kelgan yangilanish klaviatura foydalanuvchisining fokusini yo'q qilishi mumkin.</strong></p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Tab navigatsiyasi + KO'RINADIGAN fokus indikatori</h4>
<pre><code>/* style.css */
.card:focus-visible {
  outline: 3px solid #2563eb;
  outline-offset: 2px;
}
/* ❗ outline HECH QACHON butunlay o'chirilmaydi ("outline: none"
   umuman ishlatilmaydi) - u faqat :focus-visible bilan chiroyliroq
   qilib qayta uslublanadi. */</code></pre>

<h4>BLOKA 2 — WebSocket orqali real vaqtli yangilanish</h4>
<pre><code>// app.js
const socket = new WebSocket('ws://localhost:3000');

socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  renderBoard(update.state);   // taxtani qayta chizadi
});</code></pre>

<h4>BLOKA 3 — qayta render qilishda FOKUSNI SAQLAB QOLISH</h4>
<pre><code>function renderBoard(state) {
  // ❗ Qayta yozishdan OLDIN, hozir fokusda turgan kartani eslab qolamiz
  const focusedCardId = document.activeElement?.dataset?.cardId;

  boardEl.innerHTML = renderCardsHTML(state);

  // ❗ Qayta yozgandan KEYIN, o'sha ID'ga ega YANGI elementni topib,
  // fokusni unga QAYTA TIKLAYMIZ
  if (focusedCardId) {
    const sameCard = boardEl.querySelector(`[data-card-id="${focusedCardId}"]`);
    if (sameCard) sameCard.focus();
  }
}</code></pre>

<h3>🐛 Ataylab xato — WebSocket yangilanishi fokusni saqlashsiz DOM'ni almashtiradi</h3>
<pre><code>// "Taxtani yangilash oson - shunchaki innerHTML'ni almashtiraman" deb:
socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  boardEl.innerHTML = renderCardsHTML(update.state);   // ❌ fokusni saqlashsiz!
});

// Ssenariy:
// 1. Klaviatura foydalanuvchisi Tab bosib, 3-kartaga fokus qo'ygan
// 2. Boshqa foydalanuvchi (sichqoncha bilan) biror kartani ko'chiradi
// 3. Server WebSocket orqali YANGI holatni barcha klientlarga yuboradi
// 4. Klaviatura foydalanuvchisining brauzerida boardEl.innerHTML
//    BUTUNLAY almashtiriladi - ESKI <button> (fokusdagi) DOM'DAN
//    OLIB TASHLANADI, uning o'rniga YANGI <button> yaratiladi
//    (garchi ekranda BIR XIL ko'rinsa ham!)
// 5. Brauzer: "fokusdagi element endi DOM'da yo'q" - fokus avtomatik
//    ravishda document.body'ga o'tadi
//
// ❌ Foydalanuvchi endi QAYERDA ekanini bilmaydi - ekranda hech narsa
//    "buzilmagan" ko'rinadi, lekin fokus yo'qolgan, Tab bosishni
//    BOSHIDAN, taxtaning eng boshidan boshlashga majbur bo'ladi.</code></pre>

<p><strong>Natija:</strong> vizual jihatdan ekran <strong>xuddi oldingidek</strong> ko'rinadi — sichqoncha foydalanuvchisi hech qanday farq sezmaydi. Lekin klaviatura foydalanuvchisi uchun bu <strong>real vaqtli hamkorlik xususiyati</strong> — boshqa har bir odam kartani ko'chirganda, sizning fokusingiz <strong>kutilmaganda yo'qoladi</strong>, va siz taxtaning boshidan qayta navigatsiya qilishga majbur bo'lasiz. Bu xato ayniqsa <strong>ushbu capstone'ga xos</strong> — chunki u faqat WebSocket orqali real vaqtli yangilanish VA klaviatura navigatsiyasi <strong>bir vaqtda</strong> ishlatilganda yuzaga keladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega <code>outline</code>ni butunlay o'chirish (<code>outline: none</code>) xavfli?</h4>
<p><code>outline</code> — klaviatura foydalanuvchisi uchun <strong>yagona</strong> vizual signal, "hozir men qayerdaman". Ko'p dasturchilar uni "ko'rinishni buzadi" deb o'ylab olib tashlaydi, lekin uni <strong>almashtirmasdan</strong> olib tashlash klaviatura foydalanuvchisini butunlay "ko'zsiz" qoldiradi. To'g'ri yechim — <code>:focus-visible</code> bilan uni <strong>chiroyliroq</strong> qilib qayta uslublash, butunlay o'chirish emas.</p>

<h4>2. Nega <code>innerHTML = ...</code> fokusni yo'qotadi?</h4>
<p><code>innerHTML</code>ga yangi qiymat berilganda, brauzer <strong>eski DOM elementlarining barchasini yo'q qiladi</strong> va ularning o'rniga <strong>butunlay yangi</strong> elementlar yaratadi — hatto ular vizual jihatdan bir xil ko'rinsa ham. Fokus <strong>elementga</strong> bog'langani uchun, eski element yo'qolganda, fokus ham birga yo'qoladi va brauzer uni <code>document.body</code>ga qaytaradi.</p>

<h4>3. Nega bu xato faqat klaviatura foydalanuvchisiga ta'sir qiladi?</h4>
<p>Sichqoncha foydalanuvchisi hech qachon "fokus"ga <strong>tayanmaydi</strong> — u har doim ko'zi bilan kerakli joyga bosadi. Klaviatura foydalanuvchisi esa <strong>fokus holati</strong>ga to'liq tayanadi — bu uning "joriy o'rni". Fokus kutilmaganda yo'qolishi, xuddi sichqoncha kursori to'satdan ekranning boshqa joyiga "sakrab ketishi" kabi.</p>

<h4>4. To'g'ri yechim (fokusni saqlash) qanday ishlaydi?</h4>
<p>Qayta render qilishdan <strong>oldin</strong>, joriy fokusdagi elementni aniqlovchi ma'lumot (masalan <code>data-card-id</code>) saqlab qolinadi. Qayta render qilingandan <strong>keyin</strong>, xuddi shu ID'ga ega <strong>yangi</strong> elementni topib, fokusni unga <strong>qo'lda qaytarish</strong> kerak — bu brauzerning avtomatik xatti-harakatini "tuzatadi".</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — accessibility va real vaqtli (WebSocket) funksionallik <strong>birga</strong> ishlatilganda paydo bo'ladigan, capstone'ga xos yangi xavf turi. 1-2-darslarda ko'rgan statik accessibility xatolaridan farqli, bu xato faqat <strong>dinamik</strong> holatda — boshqa foydalanuvchining harakati sizning ekranizni real vaqtda o'zgartirganda — namoyon bo'ladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>outline: none</code> klaviatura foydalanuvchisini "ko'zsiz" qoldiradi - <code>:focus-visible</code> bilan qayta uslublash kerak, butunlay o'chirish emas</li>
<li>✅ <code>innerHTML</code> orqali qayta render qilish eski DOM elementlarini yo'q qiladi, fokusni ham birga olib ketadi</li>
<li>✅ Fokus yo'qolishi faqat klaviatura foydalanuvchisiga ta'sir qiladi, sichqoncha foydalanuvchisi buni sezmaydi</li>
<li>✅ To'g'ri yechim: qayta render qilishdan oldin fokusni eslab qolish, keyin qo'lda qaytarish</li>
<li>✅ Bu — accessibility va real vaqtli funksionallik birga ishlatilganda paydo bo'ladigan, dinamik xato turi</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 3-BOSQICH: Klaviatura Navigatsiyasi + WebSocket
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) style.css - :focus-visible (izohda - CSS)
// ─────────────────────────────────────────────────────────────────────

// .card:focus-visible {
//   outline: 3px solid #2563eb;
//   outline-offset: 2px;
// }

// ─────────────────────────────────────────────────────────────────────
// 2) app.js - WebSocket + fokusni SAQLAB QOLGAN holda qayta render
// ─────────────────────────────────────────────────────────────────────

const socket = new WebSocket('ws://localhost:3000');
const boardEl = document.querySelector('#board');

socket.addEventListener('message', (event) => {
  const update = JSON.parse(event.data);
  renderBoard(update.state);
});

function renderBoard(state) {
  const focusedCardId = document.activeElement?.dataset?.cardId;

  boardEl.innerHTML = renderCardsHTML(state);

  if (focusedCardId) {
    const sameCard = boardEl.querySelector(`[data-card-id="${focusedCardId}"]`);
    if (sameCard) sameCard.focus();
  }
}

function renderCardsHTML(state) {
  // ... kartalarni HTML satr sifatida hosil qiladi ...
  return state.cards.map((c) => `
    <button class="card" type="button" data-card-id="${c.id}">
      ${c.title}
    </button>
  `).join('');
}

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - fokusni saqlashsiz qayta render (izohda)
// ─────────────────────────────────────────────────────────────────────

// socket.addEventListener('message', (event) => {
//   const update = JSON.parse(event.data);
//   boardEl.innerHTML = renderCardsHTML(update.state);   // fokus saqlanmagan!
// });
// Klaviatura foydalanuvchisi fokusda bo'lgan vaqtda boshqa foydalanuvchi
// kartani ko'chirsa, fokus document.body'ga "sakrab ketadi".
"""

L3_EX = [
    {
        "title": "Nega outline: none xavfli?",
        "description": "CSS'da outline: none orqali fokus indikatorini butunlay o'chirish nima uchun xavfli hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu sahifani sekinlashtiradi",
            "outline klaviatura foydalanuvchisi uchun 'hozir men qayerdaman' degan yagona vizual signal - uni almashtirmasdan olib tashlash uni 'ko'zsiz' qoldiradi",
            "Chunki bu SEO'ga salbiy ta'sir qiladi",
            "Chunki brauzerlar bu CSS qoidasini qo'llab-quvvatlamaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Sichqoncha foydalanuvchisi 'qayerdaligini' qanday biladi? Klaviatura foydalanuvchisi-chi?",
        "explanation": "outline klaviatura foydalanuvchisi uchun yagona vizual signal - uni almashtirmasdan olib tashlash klaviatura foydalanuvchisini butunlay yo'naltiruvchi signalsiz qoldiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "innerHTML orqali qayta render qilish fokusga qanday ta'sir qiladi?",
        "description": "boardEl.innerHTML = ... orqali DOM qayta yozilganda, avvalgi fokusdagi elementga nima bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Fokus avtomatik ravishda yangi, bir xil ko'rinadigan elementga o'tkaziladi",
            "Eski element DOM'dan yo'q qilinadi, fokus ham u bilan birga yo'qoladi va brauzer uni document.body'ga qaytaradi",
            "Fokus o'zgarishsiz qoladi, chunki HTML matni bir xil",
            "Brauzer avtomatik ravishda xato xabarini ko'rsatadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "innerHTML yangi qiymat qabul qilganda, ESKI elementlar hali ham mavjudmi?",
        "explanation": "innerHTML'ga yangi qiymat berilganda, brauzer eski DOM elementlarining barchasini yo'q qiladi va ularning o'rniga butunlay yangi elementlar yaratadi - fokus elementga bog'langani uchun, eski element yo'qolganda fokus ham yo'qoladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Fokus qanday yo'qolishini tartiblang",
        "description": "Klaviatura foydalanuvchisi fokusda bo'lganda, WebSocket yangilanishi kelib, fokus qanday yo'qolishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Klaviatura foydalanuvchisi Tab bosib, 3-kartaga fokus qo'ygan",
            "Boshqa foydalanuvchi kartani ko'chiradi, server WebSocket orqali yangi holatni yuboradi",
            "boardEl.innerHTML fokusni saqlashsiz butunlay almashtiriladi",
            "Eski fokusdagi element yo'q bo'ladi, brauzer fokusni document.body'ga qaytaradi",
        ],
        "correct_order": [
            "Klaviatura foydalanuvchisi Tab bosib, 3-kartaga fokus qo'ygan",
            "Boshqa foydalanuvchi kartani ko'chiradi, server WebSocket orqali yangi holatni yuboradi",
            "boardEl.innerHTML fokusni saqlashsiz butunlay almashtiriladi",
            "Eski fokusdagi element yo'q bo'ladi, brauzer fokusni document.body'ga qaytaradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Outline'ni butunlay o'chirish o'rniga qanday CSS pseudo-klass ishlatiladi?",
        "description": "outline: none o'rniga, fokus indikatorini faqat klaviatura orqali fokus qilinganda chiroyliroq ko'rsatish uchun qaysi CSS pseudo-klass ishlatiladi?",
        "exercise_type": "text_input",
        "expected_answer": ":focus-visible",
        "hint": "Bu :focus'ning zamonaviy, aqlliroq varianti.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bu xato faqat klaviatura foydalanuvchisiga ta'sir qiladi, sichqoncha foydalanuvchisiga emas?",
        "description": (
            "Boshqa foydalanuvchi kartani ko'chirganda ekran qayta "
            "chizilishi, nega sichqoncha foydalanuvchisi uchun hech "
            "qanday muammo tug'dirmaydi, lekin klaviatura foydalanuvchisi "
            "uchun jiddiy muammo bo'lib chiqadi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Sichqoncha foydalanuvchisi hech qachon 'fokus holati'ga "
            "tayanmaydi - u ekranga qarab, har safar kerakli joyga o'zi "
            "bosadi, shuning uchun taxta qayta chizilganda ham u shunchaki "
            "yana kerakli joyni topib bosaveradi. Klaviatura foydalanuvchisi "
            "esa 'qayerdaligini' bilish uchun TO'LIQ fokus holatiga "
            "tayanadi - bu uning yagona 'joriy o'rni' ko'rsatkichi. Taxta "
            "qayta chizilganda fokus document.body'ga o'tib ketishi, "
            "klaviatura foydalanuvchisi uchun xuddi birdan 'qayerda "
            "ekanini' butunlay yo'qotgandek - u endi qayta, taxtaning "
            "boshidan Tab bosishni boshlashga majbur bo'ladi."
        ),
        "hint": "Ikkala foydalanuvchi ham 'qayerdaligini' qanday biladi - ko'zi bilanmi, yoki fokus holati bilanmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "AccessBoard — Klaviatura Navigatsiyasi + WebSocket (fokusni saqlash bilan)",
    "task_description": (
        "Barcha kartalar uchun to'liq Tab/Shift+Tab navigatsiyasini va "
        ":focus-visible orqali ko'rinadigan fokus indikatorini qo'shing. "
        "WebSocket orqali real vaqtli yangilanishni qo'shing — DOM qayta "
        "render qilinganda, joriy fokusdagi karta ANIQLANIB, yangilangan "
        "DOM'da SHU kartaga fokus QAYTA TIKLANISHI shart."
    ),
    "task_requirements": (
        "• Barcha kartalarga Tab/Shift+Tab bilan ketma-ket yetib borish mumkin\n"
        "• .card:focus-visible orqali ko'rinadigan fokus indikatori mavjud (outline: none ISHLATILMAGAN)\n"
        "• WebSocket orqali boshqa foydalanuvchining o'zgarishi real vaqtda ko'rinadi\n"
        "• renderBoard() qayta chaqirilganda, oldingi fokusdagi karta ID'si orqali fokus QAYTA TIKLANADI\n"
        "• Qo'lda tekshiruv: bir kartaga fokus qo'yib, boshqa oynada o'zgarish qilinganda fokus YO'QOLMASLIGI tasdiqlangan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, JavaScript, WebSocket, ARIA, klaviatura navigatsiyasi",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Rang Kontrasti + IndexedDB — "ko'zga chiroyli" lekin noto'g'ri rang tanlovi</h2>

<pre class="mermaid">
flowchart LR
    STATUS["Karta holati: Shoshilinch"] --> DESIGN{"Faqat rang bilanmi, matn/belgi bilanmi?"}
    DESIGN -->|"Faqat rang (qizil nuqta)"| BLIND["Rangni farqlamaydigan foydalanuvchi holatni KO'RA OLMAYDI"]
    DESIGN -->|"Rang + matn/belgi"| CLEAR["Har qanday foydalanuvchi holatni tushunadi"]
    CONTRAST["Kulrang matn, oq fon"] --> CHECK{"WCAG 4.5:1 nisbatiga javob beradimi?"}
    CHECK -->|"Yo'q, lekin ko'zga 'toza' ko'rinadi"| INVISIBLE_BUG["Sog'lom ko'zli dasturchi buni SEZMAYDI"]
</pre>

<p>Veb Accessibility kursida rang kontrasti va vizual dizaynni, JavaScript: Brauzer API kursida esa IndexedDB'ni allaqachon o'rgangansiz. Bu darsda ularni birlashtirasiz: AccessBoard'ning ma'lumotlarini offline saqlash uchun IndexedDB'dan foydalanasiz, va kartalar uchun holat (status) indikatorlarini rang bilan bezaysiz. Lekin bu safar xato — ekranda hech narsa "buzilmagan" ko'rinadi, hatto <strong>sizning</strong> ko'zingiz uchun ham chiroyli ko'rinadi, lekin obyektiv o'lchov (kontrast nisbati) yoki boshqacha ko'radigan ko'z uchun <strong>muvaffaqiyatsiz</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — IndexedDB: taxta holatini brauzerda saqlash</h4>
<pre><code>// app/db.js
const request = indexedDB.open('AccessBoardDB', 1);

request.onupgradeneeded = (event) => {
  const db = event.target.result;
  db.createObjectStore('cards', { keyPath: 'id' });
};

function saveCard(card) {
  const db = request.result;
  const tx = db.transaction('cards', 'readwrite');
  tx.objectStore('cards').put(card);
}</code></pre>

<h4>BLOKA 2 — holat indikatori: RANG + MATN/BELGI birga</h4>
<pre><code>&lt;span class="status status--urgent"&gt;
  &lt;span aria-hidden="true"&gt;🔴&lt;/span&gt; Shoshilinch
&lt;/span&gt;

&lt;span class="status status--done"&gt;
  &lt;span aria-hidden="true"&gt;✅&lt;/span&gt; Bajarildi
&lt;/span&gt;

&lt;!-- ❗ Rang HAR DOIM matn yoki belgi bilan BIRGA ishlatiladi -
     hech qachon YAGONA signal sifatida emas. --&gt;</code></pre>

<h4>BLOKA 3 — WCAG kontrast nisbatini tekshirish</h4>
<pre><code>/* style.css - matn/fon rangi kombinatsiyasi WCAG AA talabiga javob berishi shart: */
.card-title {
  color: #1a1a2e;       /* to'q rang */
  background: #ffffff;  /* och fon */
  /* Kontrast nisbati: ~15.8:1 - WCAG AA (4.5:1) dan ANCHA yuqori ✅ */
}

/* Tekshirish: kontrast nisbatini onlayn vosita (masalan WebAIM
   Contrast Checker) yoki brauzer DevTools orqali HAR BIR rang
   kombinatsiyasi uchun o'lchash kerak - ko'z bilan "chamalash" EMAS. */</code></pre>

<h3>🐛 Ataylab xato — faqat rang + past kontrast, ko'zga "toza" ko'rinadi</h3>
<pre><code>&lt;!-- Holat FAQAT rang orqali ko'rsatiladi - matn yoki belgi yo'q: --&gt;
&lt;span class="status" style="background: red; width: 12px; height: 12px; border-radius: 50%;"&gt;&lt;/span&gt;
&lt;!-- Rangni farqlamaydigan (colorblind) foydalanuvchi uchun bu nuqta
     "qizil" ekanini bilmaydi - u shunchaki bo'sh doira ko'rinadi. --&gt;

&lt;!-- "Zamonaviy, tinch" ko'rinish uchun kulrang matn: --&gt;
&lt;p style="color: #999999; background: #ffffff;"&gt;Muddati: ertaga&lt;/p&gt;
&lt;!-- Kontrast nisbati: ~2.8:1 - WCAG AA talab qiladigan 4.5:1'DAN
     PASTROQ! Lekin sog'lom ko'zli dasturchi buni EKRANDA sinaganda
     "o'qish mumkin, chiroyli" deb o'ylaydi - farq FAQAT o'lchov
     vositasi bilan tekshirilganda ko'rinadi. --&gt;</code></pre>

<p><strong>Natija:</strong> bu ikkala xato ham <strong>ko'zga ko'rinmas</strong> — chunki ular faqat <strong>sizning</strong> ko'rish sharoitingizda (odatiy rang idroki, yaxshi ekran, yorug' xona) sinalgan. Faqat rang orqali holat ko'rsatish — rang ko'rligi (color blindness, aholining <strong>taxminan 8% erkaklarida</strong> uchraydi) bo'lgan foydalanuvchi uchun holat <strong>umuman ko'rinmas</strong> bo'lib qoladi. Past kontrast — past ko'rish qobiliyatiga ega yoki yorug' muhitda (masalan quyosh nurida telefon ekrani) foydalanuvchi uchun matnni <strong>o'qib bo'lmaydigan</strong> qiladi. Ikkalasi ham <strong>faqat obyektiv o'lchov</strong> (kontrast nisbati kalkulyatori, rang ko'rligi simulyatori) yoki <strong>haqiqiy, boshqacha foydalanuvchi</strong> bilan sinalganda aniqlanadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega holat FAQAT rang bilan ko'rsatilmasligi kerak?</h4>
<p>Rang ko'rligi (masalan qizil-yashilni farqlamaslik) — nisbatan keng tarqalgan holat. Agar "shoshilinch"/"oddiy" holati FAQAT qizil/yashil rang bilan farqlansa, bu foydalanuvchilar uchun ikkalasi <strong>bir xil</strong> ko'rinadi. Rang har doim <strong>qo'shimcha</strong> signal — matn yoki belgi bilan <strong>birga</strong> ishlatilishi kerak.</p>

<h4>2. WCAG kontrast nisbati (4.5:1) nimani anglatadi?</h4>
<p>Bu — matn rangi va fon rangi orasidagi <strong>yorqinlik farqi</strong>ning matematik o'lchovi. Oddiy matn uchun WCAG AA darajasi kamida <strong>4.5:1</strong> nisbatini talab qiladi — bu son past ko'rish qobiliyatiga ega odamlar ham matnni o'qiy olishini kafolatlaydi.</p>

<h4>3. Nega dasturchi past kontrastni ko'zi bilan sezmaydi?</h4>
<p>Sog'lom ko'zli, yaxshi ekranli, boshqaruvchi muhitda (masalan xira ofis yorug'ligi) ishlayotgan dasturchi uchun <code>#999</code> kulrang matn <code>#fff</code> oq fonda <strong>o'qilishi mumkin</strong> bo'lib tuyuladi. Muammo faqat boshqacha sharoitda (quyosh nurida, past ko'rish qobiliyati bilan, yomon ekranda) yoki <strong>aniq o'lchov</strong> bilan tekshirilganda ko'rinadi.</p>

<h4>4. IndexedDB'ning bu darsdagi vazifasi nima?</h4>
<p>IndexedDB — taxta ma'lumotlarini (kartalar, holatlar) <strong>brauzerning o'zida</strong> saqlash imkonini beradi, shunda foydalanuvchi internet aloqasisiz ham taxtani ko'ra oladi. Bu darsda u holat ma'lumotlarini saqlash uchun ishlatiladi — lekin saqlanadigan MA'LUMOT to'g'ri bo'lishi kifoya emas, uni <strong>ko'rsatish usuli</strong> ham accessibility talablariga javob berishi kerak.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — capstone davomida qaytarilaydigan g'oyaning yana bir ko'rinishi: xato <strong>sizning</strong> sinovingizda (ko'zingiz, ekranangiz) <strong>hech qanday</strong> signal bermaydi. Faqat obyektiv o'lchov vositasi yoki <strong>boshqacha</strong> foydalanuvchi tajribasi bu farqni fosh qiladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Holat/ma'lumot FAQAT rang orqali ko'rsatilmasligi kerak - rang doim matn yoki belgi bilan birga ishlatiladi</li>
<li>✅ WCAG AA oddiy matn uchun kamida 4.5:1 kontrast nisbatini talab qiladi</li>
<li>✅ Past kontrastni sog'lom ko'zli dasturchi odatiy sharoitda sezmasligi mumkin - faqat o'lchov vositasi buni aniqlaydi</li>
<li>✅ IndexedDB ma'lumotni offline saqlaydi, lekin ma'lumotni TO'G'RI ko'rsatish alohida masala</li>
<li>✅ Bu xatolar faqat obyektiv o'lchov yoki boshqacha foydalanuvchi tajribasi bilan aniqlanadi, ko'z bilan emas</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 4-BOSQICH: Rang Kontrasti + IndexedDB
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) app/db.js - IndexedDB orqali offline saqlash
// ─────────────────────────────────────────────────────────────────────

const request = indexedDB.open('AccessBoardDB', 1);

request.onupgradeneeded = (event) => {
  const db = event.target.result;
  db.createObjectStore('cards', { keyPath: 'id' });
};

function saveCard(card) {
  const db = request.result;
  const tx = db.transaction('cards', 'readwrite');
  tx.objectStore('cards').put(card);
}

function loadAllCards() {
  return new Promise((resolve) => {
    const db = request.result;
    const tx = db.transaction('cards', 'readonly');
    const getAll = tx.objectStore('cards').getAll();
    getAll.onsuccess = () => resolve(getAll.result);
  });
}

// ─────────────────────────────────────────────────────────────────────
// 2) status.js - holat indikatori: RANG + MATN/BELGI birga (izohda - HTML)
// ─────────────────────────────────────────────────────────────────────

// <span class="status status--urgent">
//   <span aria-hidden="true">🔴</span> Shoshilinch
// </span>
//
// <span class="status status--done">
//   <span aria-hidden="true">✅</span> Bajarildi
// </span>

// ─────────────────────────────────────────────────────────────────────
// 3) style.css - WCAG'ga mos kontrast (izohda - CSS)
// ─────────────────────────────────────────────────────────────────────

// .card-title {
//   color: #1a1a2e;
//   background: #ffffff;
//   /* Kontrast nisbati: ~15.8:1 - WCAG AA'dan ancha yuqori */
// }

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - faqat rang + past kontrast (izohda - HTML/CSS)
// ─────────────────────────────────────────────────────────────────────

// <span class="status" style="background: red; width: 12px; height: 12px; border-radius: 50%;"></span>
// <!-- Faqat rang - matn/belgi yo'q, rangni farqlamaydigan foydalanuvchi
//      buni sezmaydi -->
//
// <p style="color: #999999; background: #ffffff;">Muddati: ertaga</p>
// <!-- Kontrast nisbati ~2.8:1 - WCAG AA (4.5:1)'dan pastroq, lekin
//      ko'zga "chiroyli" ko'rinadi -->
"""

L4_EX = [
    {
        "title": "Nega holat FAQAT rang bilan ko'rsatilmasligi kerak?",
        "description": "Karta holatini (masalan 'shoshilinch'/'oddiy') FAQAT rang bilan (masalan qizil/yashil nuqta) ko'rsatish nima uchun muammoli?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki rang orqali ma'lumot uzatish CSS'da texnik jihatdan imkonsiz",
            "Rang ko'rligi bo'lgan foydalanuvchilar uchun bu ikki holat bir xil ko'rinadi - rang har doim matn yoki belgi bilan birga ishlatilishi kerak",
            "Chunki rang animatsiyasi sekin ishlaydi",
            "Chunki brauzerlar rangларни turlicha ko'rsatadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Aholining muayyan foizi ikki rangni farqlay olmaydi.",
        "explanation": "Rang ko'rligi bo'lgan foydalanuvchilar uchun faqat rang bilan farqlanadigan holatlar bir xil ko'rinadi - shuning uchun rang doim matn yoki belgi bilan birga, qo'shimcha signal sifatida ishlatilishi kerak.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "WCAG AA oddiy matn uchun qanday kontrast nisbatini talab qiladi?",
        "description": "WCAG AA standarti oddiy (kichik) matn uchun matn va fon rangi orasida kamida qanday kontrast nisbatini talab qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "2:1",
            "4.5:1",
            "10:1",
            "1.5:1",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu darsda kod misolida aniq shu son ko'rsatilgan.",
        "explanation": "WCAG AA darajasi oddiy matn uchun kamida 4.5:1 kontrast nisbatini talab qiladi - bu son past ko'rish qobiliyatiga ega odamlar ham matnni o'qiy olishini kafolatlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Past kontrast xatosi qanday aniqlanmay qolishini tartiblang",
        "description": "Kulrang matn/oq fon kombinatsiyasi WCAG'ga javob bermasa ham, u qanday qilib sinovdan 'omon qolishini' tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Dasturchi #999999 rangli matnni #ffffff fonda yozadi",
            "Dasturchi sog'lom ko'z bilan, yaxshi ekranda ekranga qaraydi - 'o'qsa bo'ladi' deb o'ylaydi",
            "Kontrast nisbati hech qachon o'lchov vositasi bilan tekshirilmaydi",
            "Past ko'rish qobiliyatiga ega yoki yorug' muhitdagi foydalanuvchi matnni o'qiy olmaydi",
        ],
        "correct_order": [
            "Dasturchi #999999 rangli matnni #ffffff fonda yozadi",
            "Dasturchi sog'lom ko'z bilan, yaxshi ekranda ekranga qaraydi - 'o'qsa bo'ladi' deb o'ylaydi",
            "Kontrast nisbati hech qachon o'lchov vositasi bilan tekshirilmaydi",
            "Past ko'rish qobiliyatiga ega yoki yorug' muhitdagi foydalanuvchi matnni o'qiy olmaydi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "IndexedDB qanday ma'lumotlar bazasi turi?",
        "description": "IndexedDB brauzerning o'zida ishlaydigan, qaysi turdagi (relatsion emas) ma'lumotlar bazasi hisoblanadi? (bitta so'z bilan javob bering, masalan: xxx-value yoki object store asosidagi)",
        "exercise_type": "text_input",
        "expected_answer": "object store",
        "hint": "Kodda createObjectStore() metodi ishlatilgan edi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bu ikkala xatoni sog'lom ko'zli dasturchi o'zi sinaganda sezmaydi?",
        "description": (
            "Faqat rang bilan holat ko'rsatish va past kontrastli matn - "
            "ikkalasi ham dasturchining o'z ko'zi bilan ekranga "
            "qaraganda nega muammosiz ko'rinadi? Bu qanday sharoitda "
            "aniqlanadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Bu ikkala xato ham faqat dasturchining O'ZINING ko'rish "
            "sharoitida - odatiy rang idroki, yaxshi sifatli ekran, "
            "boshqaruvchi (masalan ofis) yoritilishi - sinalgan. Dasturchi "
            "o'zi rangларни farqlay oladi va matnni o'qiy oladi, shuning "
            "uchun unga hammasi 'toza' va 'chiroyli' ko'rinadi. Bu "
            "muammolar faqat: (1) obyektiv o'lchov vositasi (masalan "
            "kontrast nisbati kalkulyatori yoki rang ko'rligi simulyatori) "
            "ishlatilganda, yoki (2) haqiqiy, boshqacha ko'rish "
            "qobiliyatiga ega yoki boshqacha muhitda (masalan quyosh "
            "nurida) bo'lgan foydalanuvchi bilan sinalganda aniqlanadi."
        ),
        "hint": "Dasturchi ekranga qanday sharoitda qaraydi - bu sharoit HAMMA foydalanuvchining sharoitiga o'xshaydimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "AccessBoard — Rang Kontrasti + IndexedDB (offline saqlash bilan)",
    "task_description": (
        "IndexedDB orqali taxta ma'lumotlarini brauzerda offline saqlang. "
        "Barcha holat indikatorlari uchun rang bilan BIRGA matn yoki "
        "belgi qo'shing, va barcha matn/fon rang kombinatsiyalarini WCAG "
        "AA (4.5:1) kontrast nisbatiga moslang."
    ),
    "task_requirements": (
        "• app/db.js: IndexedDB orqali kartalar saqlanadi va o'qiladi (createObjectStore, put, getAll)\n"
        "• Sahifa qayta yuklanganda, IndexedDB'dan saqlangan kartalar ko'rsatiladi\n"
        "• Hech qanday holat FAQAT rang orqali ko'rsatilmagan — har birida matn yoki belgi ham bor\n"
        "• Barcha matn/fon rang kombinatsiyalari onlayn kontrast tekshiruvchi vosita bilan tasdiqlangan (kamida 4.5:1)\n"
        "• README.md: tekshirilgan rang kombinatsiyalari va ularning kontrast nisbati ro'yxati, holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, JavaScript, IndexedDB, WCAG",
    "task_deadline_days": 5,
}


L5_TEXT = """\
<h2>5-bosqich: Forms Accessibility + File API/Drag-and-Drop — "faqat sichqoncha uchun" funksiya</h2>

<pre class="mermaid">
flowchart LR
    ATTACH["Faylni biriktirish funksiyasi"] --> ONLY["FAQAT drag-and-drop orqali - boshqa yo'l yo'q"]
    ONLY --> MOUSE["Sichqoncha foydalanuvchisi: ishlaydi"]
    ONLY --> KEY["Klaviatura/teginish foydalanuvchisi: funksiya UMUMAN MAVJUD EMAS"]
    KEY --> BLOCKED["Bu — DEGRADATSIYA emas, TO'LIQ YO'QLIK"]
</pre>

<p>Veb Accessibility kursida forma accessibility'sini, JavaScript: Brauzer API kursida esa File API va Drag-and-Drop'ni allaqachon o'rgangansiz. Bu dars — 1-darsda ogohlantirilgan xavfning <strong>to'liq</strong> namoyon bo'lishi: agar drag-and-drop <strong>faqat sichqoncha uchun</strong> qurilsa va klaviatura ekvivalenti umuman bo'lmasa, natija oldingi darslardagi kabi "qiyinlashtirilgan tajriba" emas — bu <strong>butunlay yo'q qilingan funksiya</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — karta tahrirlash formasi: har bir input o'z &lt;label&gt;iga ega</h4>
<pre><code>&lt;form id="edit-card-form"&gt;
  &lt;label for="card-title"&gt;Sarlavha&lt;/label&gt;
  &lt;input id="card-title" name="title" type="text" required&gt;

  &lt;label for="card-desc"&gt;Tavsif&lt;/label&gt;
  &lt;textarea id="card-desc" name="description"&gt;&lt;/textarea&gt;
&lt;/form&gt;

&lt;!-- ❗ &lt;label for="..."&gt; input'ning id'siga ANIQ bog'langan -
     ekran o'quvchisi input'ga kirganda LABEL matnini e'lon qiladi. --&gt;</code></pre>

<h4>BLOKA 2 — fayl biriktirish: drag-and-drop VA tugma ORQALI, IKKALASI HAM</h4>
<pre><code>&lt;div class="dropzone" id="dropzone"&gt;
  Faylni shu yerga tashlang, yoki
  &lt;label for="file-input" class="button-like" tabindex="0"&gt;fayl tanlang&lt;/label&gt;
  &lt;input type="file" id="file-input" class="sr-only-focusable"&gt;
&lt;/div&gt;</code></pre>
<pre><code>// app.js
dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', handleDrop);           // sichqoncha uchun
fileInput.addEventListener('change', handleFileSelect);  // ❗ klaviatura/
                                                           //   teginish uchun HAM ishlaydi</code></pre>

<h4>BLOKA 3 — validatsiya xatolarini ekran o'quvchisiga e'lon qilish</h4>
<pre><code>&lt;input id="card-title" aria-invalid="true" aria-describedby="title-error"&gt;
&lt;span id="title-error" role="alert"&gt;Sarlavha bo'sh bo'lishi mumkin emas&lt;/span&gt;

&lt;!-- role="alert" - xato paydo bo'lganda ekran o'quvchisi uni
     DARHOL, foydalanuvchi harakat qilmasdan ham, e'lon qiladi. --&gt;</code></pre>

<h3>🐛 Ataylab xato — fayl biriktirish FAQAT drag-and-drop, boshqa yo'l yo'q</h3>
<pre><code>&lt;!-- "Drag-and-drop zamonaviy va qulay" deb, boshqa yo'lni qo'shmaslik: --&gt;
&lt;div class="dropzone" id="dropzone"&gt;
  Faylni shu yerga tashlang
&lt;/div&gt;
&lt;!-- input type="file" YO'Q, tugma YO'Q - FAQAT bitta yo'l! --&gt;</code></pre>
<pre><code>// app.js
dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', handleDrop);
// ❌ Boshqa HECH QANDAY hodisa yozilmagan - klaviatura yoki teginish
// ekrani orqali faylni tanlashning umuman IMKONI YO'Q.</code></pre>
<pre><code>&lt;!-- Forma maydonlari uchun ham: placeholder LABEL o'rnida ishlatilgan: --&gt;
&lt;input type="text" placeholder="Sarlavha" name="title"&gt;
&lt;!-- &lt;label&gt; UMUMAN YO'Q! Ekran o'quvchisi bu maydon nima ekanini
     bilmaydi - placeholder matni FOKUS qilinganda odatda YO'QOLADI. --&gt;</code></pre>

<p><strong>Natija:</strong> bu — capstone davomida ko'rgan eng <strong>keskin</strong> xato. 2-4-darslardagi muammolar foydalanuvchi tajribasini <strong>qiyinlashtirgan</strong> yoki <strong>chalkashtirgan</strong> bo'lsa (masalan fokus yo'qolishi, holatni tushunmaslik), bu yerda muammo boshqacha: klaviatura yoki teginish ekrani foydalanuvchisi uchun fayl biriktirish funksiyasi <strong>0% mavjud</strong> — bu <strong>degradatsiya emas, to'liq yo'qlik</strong>. Bunday foydalanuvchi ilovaning bu qismidan <strong>butunlay chetlab qo'yiladi</strong>, hech qanday muqobil yo'l topa olmaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega &lt;label for="..."&gt; placeholder'dan farqli?</h4>
<p><code>&lt;label for="input-id"&gt;</code> — input bilan <strong>doimiy, dasturiy</strong> bog'langan: ekran o'quvchisi foydalanuvchi input'ga kirgan HAR SAFAR uni e'lon qiladi. <code>placeholder</code> esa faqat <strong>vizual maslahat</strong> — u odatda foydalanuvchi yozishni boshlagach <strong>yo'qoladi</strong>, va ba'zi ekran o'quvchilar uni umuman e'lon qilmaydi.</p>

<h4>2. Nega FAQAT drag-and-drop qo'shish "degradatsiya" emas, "to'liq yo'qlik"?</h4>
<p>Oldingi darslardagi xatolarda (masalan sekin fokus, past kontrast) foydalanuvchi baribir <strong>qandaydir</strong> yo'l bilan vazifani bajarishi mumkin edi, garchi qiyinroq bo'lsa ham. Bu yerda esa klaviatura/teginish foydalanuvchisi uchun fayl biriktirishning <strong>hech qanday</strong> yo'li yo'q — bu funksiya ular uchun <strong>0%</strong>, mutlaqo mavjud emas.</p>

<h4>3. <code>&lt;input type="file"&gt;</code> nega drag-and-drop bilan BIRGA qo'shiladi, uning O'RNIGA emas?</h4>
<p>Ikkalasi <strong>bir xil natijaga</strong> (fayl tanlash) olib keladi, lekin turli kirish usullari uchun mo'ljallangan. <code>&lt;input type="file"&gt;</code> tabiiy ravishda klaviatura bilan ochiladi (Enter/Space) va operatsion tizimning fayl tanlash dialogini chaqiradi — bu drag-and-drop'ning to'liq, tabiiy klaviatura ekvivalenti.</p>

<h4>4. <code>role="alert"</code> nima uchun ishlatiladi?</h4>
<p>Odatda ekran o'quvchisi faqat foydalanuvchi fokusni <strong>o'zgartirganda</strong> yangi matnni e'lon qiladi. <code>role="alert"</code> bilan belgilangan element esa, u <strong>DOM'ga qo'shilgan zahoti</strong>, foydalanuvchi hech narsa qilmasa ham, <strong>darhol</strong> e'lon qilinadi — bu validatsiya xatolari uchun juda muhim, chunki foydalanuvchi xatoni <strong>darhol</strong> bilishi kerak.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — 1-darsda aytilgan bashoratning <strong>to'liq amalga oshishi</strong>: "sichqoncha uchun avval qurib, klaviaturani keyin qo'shish qiyin" — bu yerda "keyin qo'shish" hatto <strong>urinilmagan</strong> ham, va natija eng og'ir shaklda ko'rinadi: butun funksiyaning bir foydalanuvchi guruhi uchun <strong>yo'qligi</strong>.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>&lt;label for="..."&gt;</code> input bilan doimiy bog'langan, <code>placeholder</code> esa faqat vaqtinchalik vizual maslahat</li>
<li>✅ Faqat drag-and-drop qo'shish — "qiyinlashtirilgan tajriba" emas, balki funksiyaning butunlay yo'qligi</li>
<li>✅ <code>&lt;input type="file"&gt;</code> drag-and-drop bilan BIRGA, uning tabiiy klaviatura ekvivalenti sifatida qo'shiladi</li>
<li>✅ <code>role="alert"</code> validatsiya xatolarini foydalanuvchi harakatisiz ham darhol e'lon qiladi</li>
<li>✅ Bu — "sichqoncha uchun avval qurib, klaviaturani keyin qo'shish" xavfining eng og'ir, to'liq ko'rinishi</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 5-BOSQICH: Forms Accessibility + File API/Drag-and-Drop
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) edit-card-form - har bir input o'z <label>iga ega (izohda - HTML)
// ─────────────────────────────────────────────────────────────────────

// <form id="edit-card-form">
//   <label for="card-title">Sarlavha</label>
//   <input id="card-title" name="title" type="text" required
//          aria-invalid="false" aria-describedby="title-error">
//   <span id="title-error" role="alert"></span>
//
//   <label for="card-desc">Tavsif</label>
//   <textarea id="card-desc" name="description"></textarea>
// </form>

// ─────────────────────────────────────────────────────────────────────
// 2) attach.js - fayl biriktirish: drag-and-drop VA input, IKKALASI HAM
// ─────────────────────────────────────────────────────────────────────

const dropzone = document.querySelector('#dropzone');
const fileInput = document.querySelector('#file-input');

dropzone.addEventListener('dragover', (e) => e.preventDefault());
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  handleFiles(e.dataTransfer.files);
});

// Klaviatura/teginish uchun HAM ishlaydigan muqobil yo'l:
fileInput.addEventListener('change', (e) => {
  handleFiles(e.target.files);
});

function handleFiles(files) {
  for (const file of files) {
    console.log(`Biriktirilgan fayl: ${file.name}`);
  }
}

// ─────────────────────────────────────────────────────────────────────
// 3) validation.js - xatoni role="alert" bilan e'lon qilish
// ─────────────────────────────────────────────────────────────────────

function showError(inputEl, message) {
  const errorEl = document.getElementById(inputEl.getAttribute('aria-describedby'));
  errorEl.textContent = message;
  inputEl.setAttribute('aria-invalid', 'true');
}

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - faqat drag-and-drop, placeholder=label (izohda)
// ─────────────────────────────────────────────────────────────────────

// <div class="dropzone" id="dropzone">Faylni shu yerga tashlang</div>
// <!-- input type="file" YO'Q, tugma YO'Q -->
// dropzone.addEventListener('drop', handleDrop);
// <!-- Boshqa hech qanday yo'l yozilmagan! -->
//
// <input type="text" placeholder="Sarlavha" name="title">
// <!-- <label> UMUMAN YO'Q! -->
"""

L5_EX = [
    {
        "title": "<label for=\"...\"> placeholder'dan nima bilan farq qiladi?",
        "description": "<label for=\"input-id\"> ekran o'quvchisi uchun placeholder atributidan nimasi bilan farq qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Farqi yo'q, ikkalasi bir xil ishlaydi",
            "label input bilan doimiy, dasturiy bog'langan va HAR SAFAR e'lon qilinadi; placeholder esa faqat vaqtinchalik vizual maslahat, yozish boshlangach yo'qoladi",
            "placeholder har doim label'dan ko'ra ishonchliroq",
            "label faqat matn input'lari uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Foydalanuvchi yozishni boshlaganda placeholder'ga nima bo'ladi?",
        "explanation": "label input bilan doimiy bog'langan va ekran o'quvchisi foydalanuvchi input'ga kirgan har safar uni e'lon qiladi. placeholder esa faqat vizual maslahat - odatda yozish boshlangach yo'qoladi, ba'zi ekran o'quvchilar uni umuman e'lon qilmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega faqat drag-and-drop qo'shish 'to'liq yo'qlik', 'qiyinlashtirilgan tajriba' emas?",
        "description": "Fayl biriktirish uchun FAQAT drag-and-drop qo'shilishi nega oldingi darslardagi xatolardan (masalan past kontrast) farqli hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki drag-and-drop texnik jihatdan yomon texnologiya",
            "Chunki oldingi xatolarda foydalanuvchi baribir qandaydir yo'l bilan vazifani bajara olardi, bu yerda esa klaviatura/teginish foydalanuvchisi uchun HECH QANDAY yo'l yo'q - funksiya 0% mavjud",
            "Chunki drag-and-drop faqat Chrome brauzerida ishlaydi",
            "Chunki fayl biriktirish umuman kerak emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Oldingi darslarda foydalanuvchi vazifani BAJARA olganmi, faqat qiyinroq holatdami?",
        "explanation": "Oldingi darslardagi xatolarda foydalanuvchi qandaydir yo'l bilan vazifani bajara olardi (garchi qiyinroq bo'lsa ham). Bu yerda esa klaviatura/teginish foydalanuvchisi uchun fayl biriktirishning hech qanday yo'li yo'q - bu funksiya ular uchun butunlay mavjud emas.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "To'g'ri fayl biriktirish funksiyasi qanday qurilishini tartiblang",
        "description": "Ham sichqoncha, ham klaviatura foydalanuvchisi uchun ishlaydigan fayl biriktirish funksiyasini qurish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "dropzone elementiga dragover va drop hodisalari qo'shiladi (sichqoncha uchun)",
            "Yashirin, lekin fokus qilinadigan <input type=\"file\"> qo'shiladi",
            "input uchun <label> orqali klikланadigan 'fayl tanlash' tugmasi yaratiladi",
            "input'ning change hodisasiga ham handleFiles() funksiyasi bog'lanadi (klaviatura uchun)",
        ],
        "correct_order": [
            "dropzone elementiga dragover va drop hodisalari qo'shiladi (sichqoncha uchun)",
            "Yashirin, lekin fokus qilinadigan <input type=\"file\"> qo'shiladi",
            "input uchun <label> orqali klikланadigan 'fayl tanlash' tugmasi yaratiladi",
            "input'ning change hodisasiga ham handleFiles() funksiyasi bog'lanadi (klaviatura uchun)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Validatsiya xatosini darhol e'lon qilish uchun ARIA rol",
        "description": "Forma validatsiya xatosi paydo bo'lganda, uni ekran o'quvchisiga foydalanuvchi harakatisiz ham DARHOL e'lon qilish uchun qaysi ARIA roli ishlatiladi? (masalan: role=\"xxx\")",
        "exercise_type": "text_input",
        "expected_answer": "alert",
        "hint": "Bu DOM'ga qo'shilgan zahoti darhol e'lon qilinadigan rol.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega <input type=\"file\"> drag-and-drop'ning O'RNIGA emas, UNGA QO'SHIMCHA sifatida ishlatiladi?",
        "description": (
            "To'g'ri yechimda nega dropzone (drag-and-drop) olib "
            "tashlanmaydi, balki unga qo'shimcha ravishda <input "
            "type=\"file\"> ham qo'shiladi? Ikkalasini birga saqlashning "
            "afzalligi nimada? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Drag-and-drop va <input type=\"file\"> ikkalasi ham BIR XIL "
            "natijaga (fayl tanlash) olib keladi, lekin ular turli kirish "
            "usullari uchun optimallashtirilgan - drag-and-drop sichqoncha "
            "foydalanuvchisi uchun tez va qulay, <input type=\"file\"> esa "
            "klaviatura bilan (Enter/Space orqali) ochiladigan, "
            "operatsion tizimning tabiiy fayl tanlash dialogini chaqiradi. "
            "Agar faqat bittasi qoldirilsa, boshqa kirish usulidan "
            "foydalanuvchilar chetlab qo'yiladi - shuning uchun ikkalasi "
            "BIRGA, bir xil natijaga olib keluvchi ikki xil yo'l sifatida "
            "saqlanishi kerak."
        ),
        "hint": "Ikkalasi bir xil NATIJAGA olib keladimi? Ikkalasi bir xil KIRISH usuli uchun qulaymi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "AccessBoard — Forms Accessibility + File API/Drag-and-Drop",
    "task_description": (
        "Karta tahrirlash formasini to'g'ri <label> elementlari bilan "
        "quring. Fayl biriktirish funksiyasini HAM drag-and-drop, HAM "
        "<input type=\"file\"> orqali (ikkalasi ham ishlaydigan qilib) "
        "yozing. Validatsiya xatolarini role=\"alert\" orqali e'lon qiling."
    ),
    "task_requirements": (
        "• Formadagi har bir input o'ziga <label for=\"...\"> orqali bog'langan yorliqqa ega (placeholder EMAS)\n"
        "• Fayl biriktirish HAM dropzone (drag-and-drop), HAM <input type=\"file\"> orqali ishlaydi\n"
        "• Qo'lda tekshiruv: faqat Tab va Enter tugmalari bilan (sichqonchasiz) fayl biriktirish MUMKIN ekanligi tasdiqlangan\n"
        "• Validatsiya xatolari role=\"alert\" bilan belgilangan elementda darhol e'lon qilinadi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, JavaScript, File API, ARIA, forms accessibility",
    "task_deadline_days": 5,
}


L6_TEXT = """\
<h2>6-bosqich: Service Worker + PWA — "tuzatilgan, lekin hech kim ko'rmaydigan" xato</h2>

<pre class="mermaid">
flowchart LR
    FIX["Jamoa 2-darsdagi div/button xatosini TUZATADI, production'ga deploy qiladi"] --> SW{"Service Worker cache versiyasi o'zgarganmi?"}
    SW -->|"Yo'q - cache nomi o'zgarmagan"| STALE["O'rnatilgan PWA foydalanuvchilari ESKI, tuzatilmagan versiyani ko'rishda DAVOM ETADI"]
    SW -->|"Ha - versiya oshirilgan"| FRESH["Foydalanuvchilar yangi, tuzatilgan versiyani oladi"]
</pre>

<p>JavaScript: Brauzer API kursida Service Worker va PWA'ni allaqachon o'rgangansiz. Bu darsda AccessBoard'ni o'rnatiladigan, offline ishlaydigan PWA qilasiz. Lekin bu safar xato — hatto agar siz 2-5-darslardagi BARCHA accessibility xatolarini to'g'ri tuzatgan bo'lsangiz ham, <strong>hech kim buni hech qachon ko'rmasligi</strong> mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Service Worker'ni ro'yxatdan o'tkazish</h4>
<pre><code>// app.js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}</code></pre>

<h4>BLOKA 2 — manifest.json: o'rnatiladigan qilish</h4>
<pre><code>{
  "name": "AccessBoard",
  "short_name": "AccessBoard",
  "start_url": "/",
  "display": "standalone",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" }
  ]
}</code></pre>

<h4>BLOKA 3 — cache'ni TO'G'RI versiyalash: har bir deploy'da o'zgaruvchi nom</h4>
<pre><code>// sw.js
const CACHE_VERSION = 'accessboard-v3';   // ❗ HAR bir deploy'da OSHIRILADI

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();   // ❗ yangi Service Worker DARHOL faollashadi
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      )
    )   // ❗ ESKI versiyadagi cache'lar TOZALANADI
  );
});</code></pre>

<h3>🐛 Ataylab xato — cache nomi hech qachon o'zgarmaydi, cache-first strategiya</h3>
<pre><code>// sw.js - XATO versiya
const CACHE_NAME = 'accessboard-cache';   // ❌ HECH QACHON o'zgarmaydi!

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
    // ❌ Agar so'ralgan fayl cache'da BOR bo'lsa, u HECH QACHON
    // tarmoqdan yangi versiyani tekshirmaydi!
  );
});</code></pre>
<pre><code>// Ssenariy:
// 1. Jamoa 2-darsdagi <div onclick> xatosini tuzatadi - endi <button>
//    ishlatiladi. Yangi index.html/app.js production'ga deploy qilinadi.
// 2. AccessBoard'ni PWA sifatida O'RNATGAN foydalanuvchi ilovani ochadi.
// 3. Brauzer fetch so'rovini Service Worker'ga yo'naltiradi.
// 4. Service Worker: "index.html cache'da BOR" - tarmoqqa UMUMAN
//    so'rov yubormaydi, ESKI, tuzatilmagan versiyani qaytaradi.
//
// ❌ Bu foydalanuvchi accessibility TUZATISHLARINI HECH QACHON
//    ko'rmaydi - u hali ham <div onclick> bilan yozilgan, klaviatura
//    uchun ishlamaydigan ESKI versiyani ishlatishda davom etadi,
//    garchi production'da fix ALLAQACHON joylashtirilgan bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> cache nomi hech qachon o'zgarmasa, brauzer "bu fayl allaqachon cache'da bor" deb hisoblaydi va <strong>hech qachon</strong> tarmoqdan yangi versiyani so'ramaydi. Bu — PWA o'rnatgan foydalanuvchilar uchun <strong>eng aldamchi</strong> holat: siz production kodini <strong>to'g'ri</strong> tuzatgansiz, deploy <strong>muvaffaqiyatli</strong> bo'lgan, lekin allaqachon ilovani o'rnatib olgan foydalanuvchilar buni <strong>hech qachon</strong> ko'rmaydi — ular qo'lda brauzer keshini tozalamaguncha yoki ilovani qayta o'rnatmaguncha.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega cache nomini versiyalash (masalan <code>v2</code>, <code>v3</code>) muhim?</h4>
<p><code>caches.open(CACHE_VERSION)</code> — agar bu nom <strong>o'zgarmasa</strong>, brauzer buni "xuddi shu cache" deb hisoblaydi va uni qayta yaratmaydi. Nomni o'zgartirish (masalan <code>v2</code> dan <code>v3</code>ga) brauzerga "bu <strong>yangi</strong> cache, eski fayllarni qayta yuklash kerak" degan signalni beradi.</p>

<h4>2. <code>activate</code> hodisasidagi eski cache'larni tozalash nima uchun kerak?</h4>
<p>Yangi versiya o'rnatilgandan keyin, <strong>eski</strong> versiyadagi cache hali ham brauzer xotirasida qolib ketishi mumkin. <code>activate</code> hodisasida joriy versiyaga mos kelmaydigan barcha eski cache'larni o'chirish — xotirani tejash va faqat <strong>joriy</strong> versiya ishlatilishini ta'minlash uchun kerak.</p>

<h4>3. Nega bu xato ayniqsa "aldamchi" hisoblanadi?</h4>
<p>Boshqa xatolardan farqli, bu yerda dasturchining o'zi qilgan <strong>hamma narsa to'g'ri</strong> — kod tuzatilgan, test o'tgan, deploy muvaffaqiyatli. Muammo <strong>butunlay boshqa</strong> qatlamda — brauzer cache strategiyasida — joylashgan, va bu qatlam accessibility tuzatishlarining o'zi bilan <strong>hech qanday</strong> aloqasi yo'qdek tuyuladi.</p>

<h4>4. <code>self.skipWaiting()</code> nima qiladi?</h4>
<p>Odatda yangi Service Worker "kutish" holatida turadi — u faqat barcha ochiq tab'lar yopilgandan keyin faollashadi. <code>skipWaiting()</code> bu kutishni o'tkazib yuborib, yangi Service Worker'ni <strong>darhol</strong> faollashtiradi — bu yangilanishlarning tezroq yetib borishini ta'minlaydi.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — capstone'dagi eng "meta" xato: bu safar muammo bironta <strong>yangi</strong> accessibility kamchiligi emas, balki oldingi darslarda <strong>to'g'ri qilingan tuzatishlarning o'zi</strong> real foydalanuvchilarga <strong>hech qachon yetib bormasligi</strong> mumkinligini ko'rsatadi. "To'g'ri kod yozish" va "bu kod haqiqatan foydalanuvchiga yetib borishi" — ikki <strong>alohida</strong> masala ekanini eslatadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Cache nomini versiyalash — brauzerga "bu yangi cache" deb signal berish usuli</li>
<li>✅ <code>activate</code> hodisasida eski cache'larni tozalash — faqat joriy versiya ishlatilishini ta'minlaydi</li>
<li>✅ O'zgarmas cache nomi + cache-first strategiya — o'rnatilgan foydalanuvchilarni ESKI versiyada abadiy ushlab qolishi mumkin</li>
<li>✅ <code>skipWaiting()</code> yangi Service Worker'ni darhol faollashtiradi, yangilanishni tezlashtiradi</li>
<li>✅ To'g'ri kod yozish va uning haqiqiy foydalanuvchiga yetib borishi — ikki alohida masala</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 6-BOSQICH: Service Worker + PWA
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) app.js - Service Worker'ni ro'yxatdan o'tkazish
// ─────────────────────────────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// ─────────────────────────────────────────────────────────────────────
// 2) sw.js - TO'G'RI versiyalash bilan
// ─────────────────────────────────────────────────────────────────────

const CACHE_VERSION = 'accessboard-v3';
const ASSETS = ['/', '/index.html', '/style.css', '/app.js'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      )
    )
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - versiyalanmagan cache (izohda)
// ─────────────────────────────────────────────────────────────────────

// const CACHE_NAME = 'accessboard-cache';   // hech qachon o'zgarmaydi!
//
// self.addEventListener('install', (event) => {
//   event.waitUntil(
//     caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
//   );
// });
// // activate hodisasida eski cache tozalash YO'Q, skipWaiting() YO'Q
//
// O'rnatilgan foydalanuvchilar accessibility tuzatishlarini HECH
// QACHON ko'rmaydi - service worker eski, cache'langan fayllarni
// abadiy qaytaraveradi.
"""

L6_EX = [
    {
        "title": "Cache nomini versiyalash nima uchun muhim?",
        "description": "sw.js'da CACHE_VERSION nomini har bir deploy'da o'zgartirish (masalan v2'dan v3'ga) nima uchun muhim?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki brauzer eski nomni saqlab qololmaydi",
            "Agar nom o'zgarmasa, brauzer buni 'xuddi shu cache' deb hisoblaydi va qayta yaratmaydi - nomni o'zgartirish 'bu yangi cache' signalini beradi",
            "Chunki bu ilovani tezroq ishga tushiradi",
            "Chunki versiyalash faqat production muhitida majburiy",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Brauzer 'yangi cache' va 'eski, xuddi shu cache'ni qanday farqlaydi?",
        "explanation": "Agar cache nomi o'zgarmasa, brauzer buni xuddi shu, avvaldan mavjud cache deb hisoblaydi va qayta yaratmaydi. Nomni o'zgartirish brauzerga bu yangi cache ekanligi va eski fayllarni qayta yuklash kerakligi haqida signal beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Versiyalanmagan cache + cache-first strategiya nima uchun xavfli?",
        "description": "Cache nomi hech qachon o'zgarmaydigan va fetch hodisasi doim avval cache'ni tekshiradigan Service Worker nima uchun xavfli?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu ilovani sekinlashtiradi",
            "O'rnatilgan foydalanuvchilar yangi deploy qilingan tuzatishlarni hech qachon olmaydi - Service Worker doim eski, cache'langan versiyani qaytaraveradi",
            "Chunki cache-first strategiyasi hech qachon ishlamaydi",
            "Chunki bu faqat offline holatda muammo tug'diradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agar so'ralgan fayl cache'da 'bor' deb topilsa, Service Worker tarmoqqa umuman murojaat qiladimi?",
        "explanation": "Cache nomi o'zgarmasa va fetch handler har doim avval cache'dan qaytarsa, Service Worker hech qachon tarmoqdan yangi versiyani so'ramaydi - o'rnatilgan foydalanuvchilar yangi deploy qilingan tuzatishlarni hech qachon olmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Accessibility tuzatishi foydalanuvchiga yetib bormasligi jarayonini tartiblang",
        "description": "Jamoa 2-darsdagi div/button xatosini tuzatgach, versiyalanmagan cache tufayli bu tuzatish o'rnatilgan foydalanuvchiga qanday yetib bormasligini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Jamoa <div onclick>ni <button>ga almashtiradi, production'ga deploy qiladi",
            "sw.js'dagi CACHE_NAME o'zgartirilmagan qoladi",
            "O'rnatilgan foydalanuvchi ilovani ochadi, fetch so'rovi Service Worker'ga yo'naltiriladi",
            "Service Worker 'fayl cache'da bor' deb, tarmoqqa murojaat qilmasdan ESKI versiyani qaytaradi",
        ],
        "correct_order": [
            "Jamoa <div onclick>ni <button>ga almashtiradi, production'ga deploy qiladi",
            "sw.js'dagi CACHE_NAME o'zgartirilmagan qoladi",
            "O'rnatilgan foydalanuvchi ilovani ochadi, fetch so'rovi Service Worker'ga yo'naltiriladi",
            "Service Worker 'fayl cache'da bor' deb, tarmoqqa murojaat qilmasdan ESKI versiyani qaytaradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Yangi Service Worker'ni darhol faollashtirish metodi",
        "description": "install hodisasida yangi Service Worker'ning 'kutish' bosqichini o'tkazib, uni DARHOL faollashtirish uchun qaysi metod chaqiriladi? (masalan: self.xxx())",
        "exercise_type": "text_input",
        "expected_answer": "skipWaiting",
        "hint": "Bu 'kutishni o'tkazib yuborish' degan ma'noni bildiradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bu xato boshqalardan ko'ra 'aldamchiroq' hisoblanadi?",
        "description": (
            "Versiyalanmagan cache xatosi nega boshqa darslardagi "
            "accessibility xatolaridan ko'ra ayniqsa 'aldamchi' "
            "hisoblanadi - dasturchi nima qilganida ham muammo yuz "
            "beradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Boshqa darslardagi xatolarda muammo odatda kodning o'zida - "
            "noto'g'ri element, tekshirilmagan holat va h.k. Bu yerda esa "
            "dasturchi HAMMA NARSANI to'g'ri qilgan: accessibility "
            "xatosini to'g'ri tuzatgan, kod to'g'ri yozilgan, deploy "
            "muvaffaqiyatli bo'lgan. Muammo butunlay BOSHQA qatlamda - "
            "brauzer cache strategiyasida - joylashgan, va bu qatlam "
            "accessibility tuzatishlarining mazmuni bilan hech qanday "
            "bog'liq emasdek tuyuladi. Shuning uchun bu xato ayniqsa "
            "aldamchi: 'men hammasini to'g'ri qildim' degan to'liq "
            "asosli ishonch bilan, real foydalanuvchi baribir eski, "
            "tuzatilmagan versiyani ko'rishda davom etadi."
        ),
        "hint": "Bu safar muammo kodning ICHIDAmi, yoki kod bilan foydalanuvchi ORASIDAGI boshqa qatlamdami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "AccessBoard — Service Worker + PWA (to'g'ri versiyalash bilan)",
    "task_description": (
        "AccessBoard'ni o'rnatiladigan, offline ishlaydigan PWA qiling: "
        "manifest.json, Service Worker (sw.js). Cache nomini har bir "
        "deploy'da versiyalang, activate hodisasida eski cache'larni "
        "tozalang, va skipWaiting() orqali yangi versiyani darhol "
        "faollashtiring."
    ),
    "task_requirements": (
        "• manifest.json: name, short_name, start_url, display, icons to'ldirilgan\n"
        "• sw.js: CACHE_VERSION o'zgaruvchisi (statik, o'zgarmas nom EMAS) orqali versiyalangan\n"
        "• activate hodisasida joriy versiyaga mos kelmaydigan eski cache'lar o'chiriladi\n"
        "• install hodisasida self.skipWaiting() chaqiriladi\n"
        "• README.md: cache versiyasini har deploy'da qanday oshirish kerakligi tushuntirilgan, holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, JavaScript, Service Worker, PWA, Cache API",
    "task_deadline_days": 5,
}


L7_TEXT = """\
<h2>7-bosqich (CAPSTONE yakuni): deploy va "Lighthouse 100 ball berdi" xatosi</h2>

<pre class="mermaid">
flowchart LR
    DEPLOY["AccessBoard deploy qilinadi"] --> AUDIT["Lighthouse/axe avtomatik audit ishga tushiriladi"]
    AUDIT --> SCORE["Natija: 100/100 - 'Accessibility: A'"]
    SCORE --> SHIP["Jamoa: 'Hammasi joyida' deb, QO'LDA sinovni O'TKAZIB YUBORADI"]
    SHIP --> REAL["Haqiqiy ekran o'quvchisi bilan sinaganda: 3-va 5-darsdagi xatolar HALI HAM bor bo'lishi mumkin"]
</pre>

<p>Bu — AccessBoard'ning yakuniy bosqichi. Va bu yerda capstone davomida ko'rgan g'oyaning eng <strong>yakuniy</strong> ko'rinishi ochiladi: avtomatik accessibility tekshiruv vositalari (Lighthouse, axe) <strong>foydali</strong>, lekin ular <strong>hammasini</strong> tekshira olmaydi — va "100/100 ball" ko'rinishi, xuddi Capstone 5'dagi "yashil CI" kabi, <strong>yolg'on xotirjamlik</strong> berishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — avtomatik audit: Lighthouse/axe</h4>
<pre><code># Terminal:
npx lighthouse https://accessboard.example.com \\
  --only-categories=accessibility --output=json --output-path=report.json

# Natija (misol):
# Accessibility: 100/100</code></pre>

<h4>BLOKA 2 — avtomatik vositalar TEKSHIRA OLADIGAN narsalar</h4>
<pre><code># Lighthouse/axe QODIR bo'lgan tekshiruvlar (strukturaviy/sintaktik):
# - <img>larda alt atributi bormi?
# - Har bir <input> uchun <label> (yoki aria-label) bormi?
# - Matn/fon kontrast nisbati RAQAMLI hisoblanadimi (4.5:1)?
# - ARIA atributlari TO'G'RI SINTAKSISDA yozilganmi?
# - HTML tili (lang atributi) belgilanganmi?
#
# Bularning barchasi HAQIQIY va MUHIM - lekin ular faqat "STRUKTURA
# to'g'rimi" savoliga javob beradi, "TAJRIBA to'g'rimi" savoliga emas.</code></pre>

<h4>BLOKA 3 — QO'LDA sinov: avtomatik vosita ASLO tekshira OLMAYDIGAN narsalar</h4>
<pre><code># Qo'lda, HAQIQIY klaviatura va ekran o'quvchisi bilan tekshiriladi:
# - Tab tartibi MANTIQIY (vizual tartibga mos) ketyaptimi?
# - Ekran o'quvchisi bilan tinglaganda, MA'NO to'g'ri tushuniladimi?
# - 3-darsdagi kabi: WebSocket yangilanishida fokus HAQIQATAN saqlanadimi?
# - 5-darsdagi kabi: klaviatura bilan HAQIQATAN barcha vazifani
#   (jumladan fayl biriktirishni) bajarish mumkinmi?
#
# BULARNI Lighthouse/axe HECH QACHON avtomatik tekshira OLMAYDI - ular
# faqat HAQIQIY foydalanuvchi tajribasini simulyatsiya qilib ko'rish
# orqali aniqlanadi.</code></pre>

<h3>🐛 Ataylab xato — faqat avtomatik ballga ishonib, qo'lda sinovni o'tkazib yuborish</h3>
<pre><code># .github/workflows/deploy.yml
jobs:
  a11y-check:
    steps:
      - run: npx lighthouse $URL --only-categories=accessibility --output=json > report.json
      - run: node check-score.js report.json   # 90+ bo'lsa muvaffaqiyat deb hisoblanadi
  deploy:
    needs: a11y-check
    # ❌ Bu YAGONA tekshiruv - qo'lda ekran o'quvchisi/klaviatura sinovi
    #    HECH QACHON qilinmagan!

# Jamoa: "Lighthouse 100/100 berdi, demak AccessBoard to'liq accessible" deb
# ISHONADI va deploy qiladi.
#
# LEKIN: Lighthouse quyidagilarni HECH QACHON aniqlay OLMAYDI:
# - 3-darsdagi fokus-yo'qotish xatosi HALI HAM mavjud bo'lishi mumkin
#   (chunki WebSocket yangilanishi paytidagi fokus xatti-harakatini
#   avtomatik vosita "sinab ko'rish" imkoniga ega emas)
# - 5-darsdagi "faqat drag-and-drop" xatosi ham HALI HAM mavjud bo'lishi
#   mumkin (chunki dropzone o'zi to'g'ri ARIA atributlariga ega
#   bo'lishi mumkin, lekin klaviatura bilan HAQIQATAN ishlamasligi
#   mumkin - Lighthouse buni "sinab ko'rmaydi", faqat statik kodni
#   tekshiradi)
#
# ❌ 100/100 ball bilan HAM, AccessBoard haqiqiy klaviatura/ekran
#    o'quvchisi foydalanuvchisi uchun HALI HAM qisman ishlamay qolishi
#    mumkin - bu HECH QACHON avtomatik audit orqali aniqlanmaydi.</code></pre>

<p><strong>Natija:</strong> avtomatik accessibility tekshiruv vositalari (Lighthouse, axe) haqiqiy WCAG muammolarining <strong>taxminan 30-40% ini</strong> aniqlay oladi (bu — keng tan olingan, hujjatlashtirilgan haqiqat) — qolgan <strong>60-70%</strong> faqat <strong>haqiqiy, qo'lda</strong> sinov (klaviatura bilan har bir vazifani bajarib ko'rish, ekran o'quvchisi bilan tinglash) orqali aniqlanadi. "100/100 ball" — bu <strong>strukturaviy to'g'rilik</strong> signali, <strong>tajriba to'g'riligi</strong> signali emas. Xuddi Capstone 5'dagi "yashil CI" kabi, bu ham <strong>haqiqiy foydalanuvchi tajribasi</strong> o'rniga <strong>avtomatlashtirilgan proksi</strong>ga ishonishning xavfini ko'rsatadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Lighthouse/axe kabi vositalar aslida NIMANI tekshiradi?</h4>
<p>Bu vositalar HTML/CSS/ARIA <strong>strukturasini statik tahlil qiladi</strong> — masalan "bu <code>&lt;img&gt;</code>da <code>alt</code> bormi", "bu rang kombinatsiyasi 4.5:1'dan yuqorimi". Ular kodni <strong>o'qiydi</strong>, lekin uni <strong>haqiqiy foydalanuvchi kabi ishlatib ko'rmaydi</strong>.</p>

<h4>2. Nega ular fokus boshqaruvi (3-dars) yoki klaviatura to'liqligini (5-dars) tekshira olmaydi?</h4>
<p>Bu muammolar <strong>dinamik xatti-harakat</strong>ga bog'liq — WebSocket yangilanishi kelganda fokus qayerga ketishi, yoki klaviatura bilan haqiqatan fayl biriktirib bo'ladimi. Avtomatik vosita sahifani <strong>statik holatda</strong> tahlil qiladi — u WebSocket xabari yuborib, keyin fokus qayerdaligini "sinab ko'rmaydi".</p>

<h4>3. "30-40%" raqami nimani anglatadi?</h4>
<p>Bu — accessibility hamjamiyatida keng tan olingan, turli tadqiqotlar bilan tasdiqlangan taxminiy ko'rsatkich: avtomatik vositalar WCAG mezonlarining faqat bir qismini <strong>dasturiy ravishda</strong> tekshira oladi. Qolgan qism — <strong>ma'no</strong>, <strong>mantiqiy tartib</strong>, <strong>haqiqiy foydalanish qulayligi</strong> kabi — inson qarori va sinovini talab qiladi.</p>

<h4>4. To'g'ri yondashuv nima?</h4>
<p>Avtomatik vositalarni <strong>birinchi qatlam</strong> sifatida ishlatish (tez, arzon, ko'p oddiy xatolarni ushlaydi), lekin ularni <strong>yagona</strong> gate sifatida ishlatmaslik. Deploy'dan oldin kamida bir marta <strong>haqiqiy</strong> klaviatura-faqat sinovi va (agar imkon bo'lsa) haqiqiy ekran o'quvchisi bilan sinov o'tkazish shart.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — 7 bosqichlik capstone'ning <strong>yakuniy</strong> saboqi: xuddi Capstone 5'da "yashil test/yuqori coverage/muvaffaqiyatli CI" haqiqiy to'g'rilikni kafolatlamagani kabi, bu yerda "yuqori avtomatik accessibility bali" ham haqiqiy, <strong>inklyuziv</strong> tajribani kafolatlamaydi. Ikkalasi ham bir xil chuqur haqiqatni ko'rsatadi: <strong>o'lchov vositasi — bu haqiqatning o'zi emas, uning cheklangan proksisi.</strong></p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Avtomatik accessibility vositalari (Lighthouse, axe) haqiqiy muammolarning faqat taxminan 30-40% ini aniqlaydi</li>
<li>✅ Ular strukturaviy/sintaktik narsalarni tekshiradi, dinamik xatti-harakat yoki ma'noni emas</li>
<li>✅ "100/100 ball" strukturaviy to'g'rilik signali, haqiqiy tajriba to'g'riligi kafolati emas</li>
<li>✅ Fokus boshqaruvi va klaviatura to'liqligi kabi muammolar faqat qo'lda sinov bilan topiladi</li>
<li>✅ To'g'ri yondashuv: avtomatik vositalar + majburiy qo'lda klaviatura/ekran o'quvchisi sinovi, ikkalasi birga</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz AccessBoard'ni 1-bosqichdagi klaviatura-birinchi reja hujjatidan boshlab, semantik HTML va ARIA, klaviatura navigatsiyasi va WebSocket, rang kontrasti va IndexedDB, forms accessibility va File API, Service Worker va PWA, va nihoyat <strong>to'g'ri, ishonchli accessibility tekshiruvi</strong>gacha qurdingiz. Bu capstone davomida siz Veb Accessibility va JavaScript: Brauzer API va Web kurslarida alohida o'rgangan bilimlarni <strong>bitta, real loyiha</strong>da birlashtirdingiz — va eng muhimi, boshqa besh capstone'dan farqli, TypeScript'ning yoki testlarning emas, balki <strong>"ishlaydi" degan tushunchaning o'zi</strong> qanday nisbiy ekanini yetti xil ko'rinishda ko'rdingiz: <strong>interfeys sizga, sichqoncha bilan, ko'zingiz bilan, avtomatik vosita uchun ishlab tursa ham, bu uni ishlatuvchi HAR BIR odam uchun ishlashini kafolatlamaydi.</strong></p>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 7-BOSQICH (CAPSTONE YAKUNI): Deploy va avtomatik audit xatosi
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) .github/workflows/deploy.yml - TO'G'RI: avtomatik + majburiy qo'lda checklist (izohda)
// ─────────────────────────────────────────────────────────────────────

// jobs:
//   a11y-automated-check:
//     steps:
//       - run: npx lighthouse $URL --only-categories=accessibility --output=json > report.json
//       - run: node check-score.js report.json
//   deploy:
//     needs: a11y-automated-check
//     steps:
//       - run: ./deploy.sh
//
// # README.md'da MAJBURIY qo'lda tekshiruv ro'yxati (deploy'dan OLDIN,
// # inson tomonidan bajariladi):
// # - [ ] Faqat Tab/Shift+Tab/Enter bilan barcha vazifalar bajarildi
// # - [ ] VoiceOver/NVDA bilan taxtani "eshitib" tushunish mumkin
// # - [ ] WebSocket yangilanishida fokus saqlanishi tekshirildi

// ─────────────────────────────────────────────────────────────────────
// 2) check-score.js - avtomatik ball tekshiruvi (bu FAQAT birinchi qatlam)
// ─────────────────────────────────────────────────────────────────────

const fs = require('fs');
const report = JSON.parse(fs.readFileSync(process.argv[2]));
const score = report.categories.accessibility.score * 100;

console.log(`Lighthouse accessibility bali: ${score}/100`);
if (score < 90) {
  console.error('Ball 90 dan past - deploy to\\'xtatildi.');
  process.exit(1);
}
// ❗ Bu FAQAT birinchi filtr - qo'lda sinovning o'rnini bosmaydi!

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - FAQAT avtomatik ball, qo'lda sinov yo'q (izohda)
// ─────────────────────────────────────────────────────────────────────

// jobs:
//   a11y-check:
//     steps:
//       - run: npx lighthouse $URL --only-categories=accessibility --output=json > report.json
//       - run: node check-score.js report.json
//   deploy:
//     needs: a11y-check
//     # Boshqa HECH QANDAY tekshiruv yo'q!
//
// 100/100 ball bilan ham, 3-darsdagi fokus xatosi va 5-darsdagi
// faqat-drag-and-drop xatosi HALI HAM production'da bo'lishi mumkin -
// Lighthouse bularni HECH QACHON aniqlamaydi.
"""

L7_EX = [
    {
        "title": "Lighthouse/axe kabi vositalar aslida nimani tekshiradi?",
        "description": "Avtomatik accessibility tekshiruv vositalari (Lighthouse, axe) asosan qanday turdagi tekshiruvlarni bajaradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ular haqiqiy foydalanuvchi kabi klaviatura bilan barcha vazifalarni bajarib ko'radi",
            "Ular HTML/CSS/ARIA strukturasini statik tahlil qiladi (masalan alt atributi bormi, kontrast raqami yetarlimi) - kodni ishlatib ko'rmaydi",
            "Ular faqat rasm fayllarini tekshiradi",
            "Ular faqat mobil qurilmalarda ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu vositalar kodni 'o'qiydi', lekin uni 'ishlatib ko'radimi'?",
        "explanation": "Avtomatik vositalar HTML/CSS/ARIA strukturasini statik tahlil qiladi - kodni o'qiydi, lekin uni haqiqiy foydalanuvchi kabi ishlatib ko'rmaydi, shuning uchun dinamik xatti-harakatlarni aniqlay olmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega Lighthouse 3-darsdagi fokus xatosini aniqlay olmaydi?",
        "description": "Lighthouse kabi avtomatik vosita, WebSocket yangilanishi paytida fokus yo'qolishi (3-dars) xatosini nega aniqlay olmaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu xato juda kichik va ahamiyatsiz",
            "Bu xato dinamik xatti-harakatga bog'liq - avtomatik vosita sahifani statik holatda tahlil qiladi, WebSocket xabari yuborib fokusni 'sinab ko'rmaydi'",
            "Chunki Lighthouse WebSocket'ni umuman qo'llab-quvvatlamaydi",
            "Chunki bu xato faqat production serverda yuz beradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Fokus xatosi qachon yuz beradi - sahifa ochilganda, yoki keyinroq, biror hodisa yuz berganda?",
        "explanation": "Bu muammo dinamik xatti-harakatga bog'liq - avtomatik vosita sahifani statik holatda tahlil qiladi, u WebSocket xabari yuborib, keyin fokus qayerdaligini sinab ko'rish imkoniga ega emas.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "100/100 ball bilan ham xato qanday production'ga chiqib ketishini tartiblang",
        "description": "Faqat avtomatik ballga ishonib, qo'lda sinovni o'tkazib yuborish qanday qilib buzilgan accessibility'ni production'ga olib chiqishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "CI'da Lighthouse ishga tushiriladi, natija 100/100 chiqadi",
            "Jamoa 'ball yuqori, demak hammasi joyida' deb ishonadi",
            "Qo'lda klaviatura/ekran o'quvchisi sinovi HECH QACHON o'tkazilmaydi",
            "3-va 5-darsdagi dinamik xatolar HALI HAM production'da qoladi, hech kim aniqlamaydi",
        ],
        "correct_order": [
            "CI'da Lighthouse ishga tushiriladi, natija 100/100 chiqadi",
            "Jamoa 'ball yuqori, demak hammasi joyida' deb ishonadi",
            "Qo'lda klaviatura/ekran o'quvchisi sinovi HECH QACHON o'tkazilmaydi",
            "3-va 5-darsdagi dinamik xatolar HALI HAM production'da qoladi, hech kim aniqlamaydi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Avtomatik vositalar haqiqiy WCAG muammolarining taxminan necha foizini aniqlaydi?",
        "description": "Accessibility hamjamiyatida keng tan olingan taxminiy ko'rsatkichga ko'ra, avtomatik tekshiruv vositalari haqiqiy WCAG muammolarining taxminan necha foizini dasturiy ravishda aniqlay oladi? (raqam oralig'ini foiz bilan yozing, masalan: X-Y%)",
        "exercise_type": "text_input",
        "expected_answer": "30-40%",
        "hint": "Bu darsning matnida aniq shu raqam ko'rsatilgan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega 'yuqori avtomatik ball' va 'yashil CI' (Capstone 5) bir xil chuqur xatoga ega?",
        "description": (
            "Bu darsdagi 'yuqori Lighthouse bali' xatosi, Capstone "
            "5'dagi 'yashil CI, lekin testlar aslida muvaffaqiyatsiz' "
            "xatosi bilan qanday umumiy chuqur g'oyaga ega? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Ikkalasi ham bir xil chuqur haqiqatni ko'rsatadi: o'lchov "
            "vositasi (avtomatik accessibility bali, yoki CI'ning "
            "\"muvaffaqiyatli\" signali) - bu haqiqatning o'zi emas, balki "
            "uning CHEKLANGAN, to'liq bo'lmagan PROKSISI (o'rinbosari). "
            "Ikkala holatda ham jamoa qulay, tez, raqamli signalga "
            "(yuqori ball, yashil belgi) ishonib, sekinroq, lekin "
            "ANIQROQ tekshiruvni (qo'lda accessibility sinovi, yoki "
            "testlarning haqiqatan o'tganini tekshirish) o'tkazib "
            "yuborish xavfi bor. Ikkalasida ham xavf shundaki - metrika "
            "yuqori bo'lishi mumkin, garchi haqiqiy tizim (kod, yoki "
            "foydalanuvchi tajribasi) hali ham buzilgan bo'lsa ham."
        ),
        "hint": "Ikkalasida ham qanday umumiy narsa bor - raqamli/vizual signal, va u nimani KAFOLATLAMAYDI?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L7_TASK = {
    "task_title": "AccessBoard — CAPSTONE yakuni: to'liq accessibility tekshiruvi bilan deploy qilingan loyiha",
    "task_description": (
        "AccessBoard'ni haqiqiy hostingga deploy qiling va CI'ga avtomatik "
        "accessibility auditini (Lighthouse yoki axe) qo'shing. Bundan "
        "tashqari, deploy'dan OLDIN majburiy QO'LDA sinov o'tkazing: "
        "faqat klaviatura bilan barcha asosiy vazifalarni bajarib ko'ring "
        "va (imkon bo'lsa) ekran o'quvchisi bilan sinang."
    ),
    "task_requirements": (
        "• CI'da Lighthouse yoki axe orqali avtomatik accessibility auditi ishga tushadi (90+ ball talab qilinadi)\n"
        "• Qo'lda tekshiruv: faqat Tab/Shift+Tab/Enter bilan barcha asosiy vazifalar (karta ochish, ko'chirish, fayl biriktirish) bajarilgan\n"
        "• Qo'lda tekshiruv: WebSocket yangilanishida fokus saqlanishi HAQIQATAN tasdiqlangan\n"
        "• Flask/Node backend haqiqiy hostingda ishlab turibdi\n"
        "• README.md: jonli havola, avtomatik + qo'lda sinov natijalari, 7/7 bosqich yakunlangan checklist\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi"
    ),
    "task_technologies": "Node.js, Express, Lighthouse, axe DevTools, Render/Railway",
    "task_deadline_days": 5,
}


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "javascript",
                         project_task: dict | None = None) -> str:
    sections = [
        {"id": f"t{order}", "type": "text", "label": "Текст",
         "html": text, "order": 0},
        {"id": f"c{order}", "type": "code", "label": "Код",
         "code": code, "lang": lang, "order": 1},
    ]
    if video:
        sections.append({"id": f"v{order}", "type": "video", "label": "Видео",
                          "videoUrl": video, "order": 2})
    if exercise_rows:
        sections.append({
            "id": f"e{order}", "type": "exercise", "label": "Упражнения",
            "exercises": [
                {
                    "_localId": e.id, "id": e.id,
                    "title": e.title, "description": e.description,
                    "exercise_type": e.exercise_type,
                    "options": e.options or "",
                    "correct_answers": e.correct_answers or "",
                    "drag_items": e.drag_items or "",
                    "correct_order": e.correct_order or "",
                    "is_multiple_select": bool(e.is_multiple_select),
                    "expected_answer": e.expected_answer or "",
                    "hint": e.hint or "",
                    "explanation": e.explanation or "",
                    "difficulty_level": e.difficulty_level,
                    "points": e.points, "order": e.order,
                }
                for e in exercise_rows
            ],
            "order": 3,
        })
    if project_task:
        sections.append({
            "id": f"p{order}", "type": "project", "label": project_task["task_title"],
            "description": project_task["task_description"],
            "requirements": project_task["task_requirements"],
            "techStack": project_task["task_technologies"],
            "deadline": project_task["task_deadline_days"],
            "order": 4,
        })
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()

        if existing:
            course = existing
            print(f"Course '{COURSE['title']}' already exists (id={course.id}). "
                  f"Adding/updating lessons only.")
        else:
            course = Course(**COURSE)
            db.add(course)
            await db.flush()
            print(f"Created course: id={course.id}  title='{course.title}'")

        existing_orders = {
            row[0] for row in (
                await db.execute(select(Lesson.order).where(Lesson.course_id == course.id))
            ).all()
        }

        done_lessons = [l for l in LESSON_PLAN if l["status"] == "done"]
        print(f"\nSeeding {len(done_lessons)}/{len(LESSON_PLAN)} lessons "
              f"(rest are still 'todo' in LESSON_PLAN):\n")

        for ldata in done_lessons:
            if ldata["order"] in existing_orders:
                print(f"  ⏭️  order={ldata['order']:>2}  {ldata['title']:<55}  "
                      f"already seeded, skipped")
                continue

            text = globals()[f"{ldata['ref']}_TEXT"]
            code = globals()[f"{ldata['ref']}_CODE"]
            ex_list = globals().get(f"{ldata['ref']}_EX", [])
            task = globals().get(f"{ldata['ref']}_TASK")
            lang = ldata.get("lang", "javascript")

            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=15,
                text_content=text,
                code_content=code,
                code_language=lang,
                video_url=None,  # TODO: add a real video link before publishing
                sections_json=None,
                task_title=task.get("task_title") if task else None,
                task_description=task.get("task_description") if task else None,
                task_requirements=task.get("task_requirements") if task else None,
                task_technologies=task.get("task_technologies") if task else None,
                task_deadline_days=task.get("task_deadline_days") if task else None,
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ex_list):
                row = Exercise(
                    lesson_id=lesson.id,
                    title=ex["title"],
                    description=ex.get("description", ex["title"]),
                    exercise_type=ex["exercise_type"],
                    options=_jdump(ex.get("options")),
                    correct_answers=_jdump(ex.get("correct_answers")),
                    drag_items=_jdump(ex.get("drag_items")),
                    correct_order=_jdump(ex.get("correct_order")),
                    is_multiple_select=bool(ex.get("is_multiple_select", False)),
                    expected_answer=ex.get("expected_answer", ""),
                    hint=ex.get("hint", ""),
                    explanation=ex.get("explanation", ""),
                    difficulty_level=ex["difficulty_level"],
                    points=ex["points"],
                    order=ex_order,
                    is_active=True,
                )
                db.add(row)
                ex_rows.append(row)
            await db.flush()

            lesson.sections_json = build_sections_json(
                ldata["order"], text, code, None, ex_rows, lang=lang,
                project_task=task,
            )

            sample = LessonSample(
                lesson_id=lesson.id,
                title=f"Namuna: {ldata['title']}",
                description=ldata["scope"],
                sample_type="code",
                code_files_json=json.dumps(
                    [{"filename": "misol.js", "language": lang, "code": code}],
                    ensure_ascii=False,
                ),
            )
            db.add(sample)

            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded {len(done_lessons)} lesson(s).")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed(dry_run="--dry-run" in sys.argv))
