"""Seed "Node.js/Express Asoslari" (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_nodejs_express.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order (safe to re-run while filling in
more lessons over multiple sessions).

Target audience: "JavaScript: Keyingi Bosqich" (course 39) graduates —
assumes solid JS fundamentals (async/await, destructuring, modules) but
NOT React (this is backend-only). Mirrors the progression of the existing
"Python Flask" course (course 21) lesson-for-lesson: intro -> routing ->
request/response -> project structure -> revision -> database -> CRUD ->
revision -> validation -> auth -> protected routes -> revision -> CORS ->
deploy. Positioned explicitly as "the backend for your React apps" — no
server-rendered templating (EJS), JSON REST API from lesson 1, since
students already know React for UI.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py (hand-authored,
provider="manual" — NOT the OpenAI-based bulk_translate.py).

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
    "title": "Node.js/Express Asoslari",
    "description": (
        "JavaScript: Keyingi Bosqich kursini tugatgan dasturchilar uchun: "
        "Node.js va Express bilan backend qurish — routing, middleware, "
        "PostgreSQL bilan ma'lumotlar bazasi, CRUD, validatsiya, JWT "
        "autentifikatsiya, va React frontend bilan ulash. Frontend uchun "
        "React bilishingiz kifoya — bu kurs faqat backend'ga bag'ishlangan."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 7,  # JavaScript
    "prerequisite_course_id": 39,  # JavaScript: Keyingi Bosqich
    "is_active": True,
    "is_published": False,  # flip to True once all 14 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0,  "ref": "L1",  "status": "done",
     "title": "1-Node.js va Express'ga kirish",
     "scope": "Node runtime, npm, first Express server, understanding "
              "request/response, nodemon."},
    {"order": 1,  "ref": "L2",  "status": "done",
     "title": "2-Routing va middleware",
     "scope": "app.get/post/put/delete, route params, middleware chain "
              "(app.use, next())."},
    {"order": 2,  "ref": "L3",  "status": "done",
     "title": "3-Request/Response chuqurroq",
     "scope": "req.body/query/params, express.json(), status codes, "
              "error-first patterns."},
    {"order": 3,  "ref": "L4",  "status": "done",
     "title": "4-Router bilan loyihani tashkil qilish",
     "scope": "express.Router(), splitting routes into modules, project "
              "structure."},
    {"order": 4,  "ref": "R1",  "status": "done",
     "title": "R1-Mini Todo REST API (takrorlash)",
     "scope": "Combine routing, middleware, req/res, Router — revision "
              "covering lessons 1-4."},
    {"order": 5,  "ref": "L5",  "status": "done",
     "title": "5-PostgreSQL ulanish (pg)",
     "scope": "node-postgres (pg) pool, parameterized queries, connecting "
              "to the DB the SQL course already taught."},
    {"order": 6,  "ref": "L6",  "status": "done",
     "title": "6-CRUD operatsiyalar",
     "scope": "Full CRUD endpoints backed by the DB, async/await error "
              "handling around queries."},
    {"order": 7,  "ref": "R2",  "status": "done",
     "title": "R2-Notes REST API (takrorlash)",
     "scope": "Small app combining DB connection + full CRUD."},
    {"order": 8,  "ref": "L7",  "status": "done",
     "title": "7-Validatsiya va xatolarni boshqarish",
     "scope": "Centralized error-handling middleware, input validation, "
              "consistent error response shape."},
    {"order": 9,  "ref": "L8",  "status": "done",
     "title": "8-JWT autentifikatsiya",
     "scope": "Password hashing (bcrypt), issuing/verifying JWTs, "
              "register/login endpoints."},
    {"order": 10, "ref": "L9",  "status": "done",
     "title": "9-Protected routes va middleware zanjiri",
     "scope": "Auth middleware, req.user pattern, protecting specific "
              "routes, role-based checks."},
    {"order": 11, "ref": "R3",  "status": "done",
     "title": "R3-Auth + CRUD to'liq loyiha (takrorlash)",
     "scope": "Full app combining lessons 5-10: DB + CRUD + auth + "
              "protected routes."},
    {"order": 12, "ref": "L10", "status": "done",
     "title": "10-CORS va React bilan ulash",
     "scope": "CORS config, connecting a React frontend to this API, "
              "environment-based origin whitelisting."},
    {"order": 13, "ref": "L11", "status": "done",
     "title": "11-Deploy tayyorgarligi",
     "scope": "dotenv/config, logging, health-check endpoint, "
              "package.json scripts, prod checklist."},
]


L1_TEXT = """\
<h2>Node.js va Express'ga kirish — birinchi server 5 daqiqada</h2>

<pre class="mermaid">
flowchart LR
    B["Brauzer / fetch"] -->|so'rov| S["Express server"]
    S -->|route topadi| H["handler funksiya"]
    H -->|res.send/json| B
</pre>

<p>Hozirgacha JavaScript'ni faqat <strong>brauzerda</strong> ishlatdingiz. <code>Node.js</code> — bir xil JavaScript tilini brauzerdan tashqarida, to'g'ridan-to'g'ri kompyuteringizda ishga tushiradigan muhit. <code>Express</code> — Node ustida qurilgan, server yozishni sodda qiladigan kichik kutubxona.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi server</h4>
<pre><code>// Terminal:
mkdir mening-serverim && cd mening-serverim
npm init -y
npm install express</code></pre>

<pre><code>// server.js
const express = require('express');
const app = express();

app.get('/', (req, res) =&gt; {
  res.send('Salom, men serverman!');
});

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});</code></pre>

<pre><code>// Terminal:
node server.js
// Brauzerda oching: http://localhost:3000</code></pre>

<p>Tabriklaymiz — bu sizning birinchi backend serveringiz. <code>app.get('/', handler)</code> — "kimdir <code>/</code> manzilga GET so'rov yuborsa, shu funksiyani ishga tushir" degani.</p>

<h4>BLOKA 2 — bir nechta route va JSON javob</h4>
<pre><code>app.get('/', (req, res) =&gt; {
  res.send('Bosh sahifa');
});

app.get('/about', (req, res) =&gt; {
  res.send('Bu — mening birinchi Express serverim');
});

app.get('/api/user', (req, res) =&gt; {
  res.json({ ism: 'Olim', yosh: 22 }); // JSON — API'lar uchun standart format
});</code></pre>

<p><code>res.send()</code> — matn yoki HTML yuboradi. <code>res.json()</code> — obyektni JSON qilib yuboradi va <code>Content-Type: application/json</code> headerini avtomatik qo'yadi. Ko'pchilik zamonaviy backend'lar (React kabi frontend bilan ishlaydiganlar) — faqat JSON qaytaradi, HTML emas.</p>

<h4>BLOKA 3 — nodemon: har o'zgarishda avtomatik qayta ishga tushirish</h4>
<pre><code>npm install -D nodemon</code></pre>

<pre><code>// package.json ichiga qo'shing:
"scripts": {
  "dev": "nodemon server.js"
}</code></pre>

<pre><code>npm run dev
// Endi server.js'ni o'zgartirsangiz, server o'zi qayta ishga tushadi —
// har safar Ctrl+C bosib qayta node server.js yozish shart emas.</code></pre>

<h3>🐛 Ataylab xato — javob yubormaslik (server "osilib qoladi")</h3>
<pre><code>app.get('/xato', (req, res) =&gt; {
  console.log('So\\'rov keldi');
  // ❌ res.send() yoki res.json() chaqirilmagan!
});</code></pre>

<p><strong>Natija:</strong> brauzerda <code>/xato</code>ga kirsangiz — sahifa <strong>abadiy "yuklanmoqda"</strong> holatida qoladi. Hech qanday xato xabari yo'q, konsolda hech narsa qizarmaydi — chunki texnik jihatdan hech narsa "noto'g'ri" emas, siz shunchaki HTTP so'rovga <strong>javob yuborishni unutdingiz</strong>. Brauzer javobni kuta beradi, kuta beradi... va oxir-oqibat timeout bo'ladi.</p>

<p>Bu — backend'dagi eng keng tarqalgan boshlang'ich xato: <strong>har bir route handler — albatta bir marta javob yuborishi shart</strong> (<code>res.send()</code>, <code>res.json()</code>, <code>res.end()</code> va h.k.).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Node.js — bu nima?</h4>
<p>Node.js — Chrome brauzerining V8 JavaScript dvigatelini olib, uni brauzerdan tashqarida ishlatadigan muhit. Shu tufayli bir xil JavaScript tili bilan frontend (brauzerda) ham, backend (serverda) ham yozish mumkin. Node <strong>bitta oqimda (single-threaded)</strong> ishlaydi, lekin fayl o'qish, tarmoq so'rovlari kabi "og'ir" amallarni <strong>bloklamasdan</strong> (non-blocking) bajaradi — shu bilan bir vaqtda ko'plab so'rovlarni samarali boshqaradi.</p>

<h4>2. Express — nima uchun kerak?</h4>
<p>Node.js'ning o'zi bilan ham server yozish mumkin (<code>http</code> moduli orqali), lekin bu juda ko'p qo'lda kod talab qiladi. Express — routing (qaysi manzilga qaysi funksiya javob berishi), so'rov/javobni qulay boshqarish, va middleware zanjiri (keyingi darsda) kabi narsalarni soddalashtiradi.</p>

<h4>3. package.json — loyihaning "pasporti"</h4>
<pre><code>{
  "name": "mening-serverim",
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0"
  },
  "scripts": {
    "dev": "nodemon server.js"
  }
}</code></pre>
<p><code>dependencies</code> — production'da kerak bo'ladigan paketlar (express). <code>devDependencies</code> — faqat ishlab chiqish jarayonida kerak (nodemon — production serverda kerak emas). <code>scripts</code> — <code>npm run dev</code> kabi buyruqlarning qisqartmasi.</p>

<h4>4. req va res — har bir handler'ning ikki asosiy argumenti</h4>
<ul>
<li><code>req</code> (request) — kelgan so'rov haqida ma'lumot: <code>req.method</code>, <code>req.url</code>, keyingi darslarda <code>req.body</code>/<code>req.params</code>/<code>req.query</code></li>
<li><code>res</code> (response) — javob yuborish uchun: <code>res.send()</code>, <code>res.json()</code>, <code>res.status(404).send(...)</code></li>
</ul>

<h4>5. nodemon — nima uchun kerak?</h4>
<p>Oddiy <code>node server.js</code> — faylni bir marta ishga tushiradi. Kodni o'zgartirsangiz, o'zgarish ko'rinishi uchun serverni qo'lda to'xtatib qayta ishga tushirish kerak. <code>nodemon</code> — fayllarni kuzatib boradi va o'zgarish bo'lganda serverni <strong>avtomatik</strong> qayta ishga tushiradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Node.js — JavaScript'ni brauzerdan tashqarida ishga tushiradigan muhit</li>
<li>✅ Express — routing va so'rov/javobni soddalashtiruvchi kichik kutubxona</li>
<li>✅ <code>app.get(manzil, handler)</code> — GET so'rovlarga javob berish</li>
<li>✅ <code>res.send()</code> — matn/HTML, <code>res.json()</code> — JSON javob yuborish</li>
<li>✅ Har bir handler albatta bir marta javob yuborishi shart — aks holda so'rov abadiy "osilib qoladi"</li>
<li>✅ <code>nodemon</code> — ishlab chiqish paytida serverni avtomatik qayta ishga tushiradi</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 1: Node.js va Express'ga kirish
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

// ─────────────────────────────────────────────────────────────────────
// 1) Bir nechta oddiy route
// ─────────────────────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.send('Bosh sahifa');
});

app.get('/about', (req, res) => {
  res.send('Bu — mening birinchi Express serverim');
});

// ─────────────────────────────────────────────────────────────────────
// 2) JSON javob — zamonaviy backend'lar uchun standart
// ─────────────────────────────────────────────────────────────────────

app.get('/api/user', (req, res) => {
  res.json({ ism: 'Olim', yosh: 22 });
});

app.get('/api/users', (req, res) => {
  res.json([
    { id: 1, ism: 'Olim' },
    { id: 2, ism: 'Vali' },
  ]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato — javob yubormaslik (so'rov abadiy osilib qoladi)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/xato', (req, res) => {
  console.log("So'rov keldi");
  // ❌ res.send() yoki res.json() chaqirilmagan!
  // Brauzer abadiy "yuklanmoqda" holatida qoladi, hech qanday xato yo'q.
});
*/

// ✅ To'g'risi — har doim javob yuboring
app.get('/togri', (req, res) => {
  console.log("So'rov keldi");
  res.send('Javob yuborildi!');
});

// ─────────────────────────────────────────────────────────────────────
// 4) Serverni ishga tushirish
// ─────────────────────────────────────────────────────────────────────

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server ishga tushdi: http://localhost:${PORT}`);
});

// package.json:
// {
//   "dependencies": { "express": "^4.18.0" },
//   "devDependencies": { "nodemon": "^3.0.0" },
//   "scripts": { "dev": "nodemon server.js" }
// }
//
// Terminal:
//   npm install express
//   npm install -D nodemon
//   npm run dev
"""

L1_EX = [
    {
        "title": "Node.js nima?",
        "description": "Node.js aslida nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Yangi dasturlash tili",
            "Chrome'ning V8 JavaScript dvigatelini brauzerdan tashqarida ishlatadigan muhit",
            "Faqat frontend uchun kutubxona",
            "Ma'lumotlar bazasi tizimi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Node.js — brauzer emas, lekin brauzerdagi bilan bir xil JS dvigatelidan foydalanadi.",
        "explanation": (
            "Node.js — Chrome brauzerining V8 dvigatelini olib, uni brauzerdan "
            "tashqarida, to'g'ridan-to'g'ri kompyuterda ishga tushiradigan "
            "muhit. Shu tufayli bir xil JavaScript tili bilan backend yozish "
            "mumkin."
        ),
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Handler javob yubormasa nima bo'ladi?",
        "description": "Agar route handler ichida res.send() yoki res.json() chaqirilmasa, brauzerda nima ko'rinadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Darhol 404 xatosi",
            "Sahifa abadiy \"yuklanmoqda\" holatida qoladi, timeout'gacha",
            "Server darhol ishdan to'xtaydi",
            "Konsolda qizil xato chiqadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Brauzer javobni kutadi — javob kelmasa, kuta beradi.",
        "explanation": (
            "Javob yuborilmasa, texnik jihatdan hech qanday xato yo'q — server "
            "shunchaki javob yubormagan. Brauzer javobni kuta beradi, oxir-"
            "oqibat timeout bo'lguncha."
        ),
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Serverni ishga tushirish ketma-ketligi",
        "description": "Yangi Express loyihasini boshdan ishga tushirishning to'g'ri tartibini joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "npm init -y",
            "npm install express",
            "server.js faylida app.get(...) route'larini yozish",
            "app.listen(port, callback) chaqirish",
            "node server.js buyrug'i bilan ishga tushirish",
        ],
        "correct_order": [
            "npm init -y",
            "npm install express",
            "server.js faylida app.get(...) route'larini yozish",
            "app.listen(port, callback) chaqirish",
            "node server.js buyrug'i bilan ishga tushirish",
        ],
        "hint": "Avval loyiha, keyin kutubxona, keyin kod, keyin ishga tushirish.",
        "explanation": "",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega har bir handler albatta javob yuborishi shart?",
        "description": (
            "Nega Express'da har bir route handler albatta bir marta javob "
            "(res.send/json/end) yuborishi shart, va bu qoidaga rioya "
            "qilinmasa nima yuz beradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "HTTP so'rov-javob modeli shunday ishlaydi: brauzer (yoki boshqa "
            "klient) so'rov yuboradi va javob kelishini kutadi. Agar server "
            "hech qanday javob yubormasa, klient uchun hech narsa "
            "\"tugamagan\" bo'lib qoladi — u javobni kutishda davom etadi, "
            "hech qanday xato ko'rsatmasdan, toki ulanish timeout bo'lguncha. "
            "Bu — kuzatish qiyin bo'lgan jim (silent) bug, chunki na server "
            "tomonda, na klient tomonda aniq xato xabari chiqmaydi."
        ),
        "hint": "HTTP so'rov-javob modeli qanday ishlashini, va javob kelmasa klient nima qilishini o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L2_TEXT = """\
<h2>Routing va middleware — so'rovlar zanjiri</h2>

<pre class="mermaid">
flowchart LR
    REQ["So'rov keldi"] --> MW1["logger middleware"]
    MW1 -->|next()| MW2["auth middleware"]
    MW2 -->|next()| R["route handler"]
    R --> RES["Javob"]
</pre>

<p>1-darsda har bir route'ga alohida <code>(req, res) =&gt; {...}</code> yozdik. Lekin ko'p route'lar uchun umumiy ish bor: har bir so'rovni log qilish, autentifikatsiyani tekshirish, va h.k. Buni har bir handler ichida qaytarish o'rniga — <strong>middleware</strong> ishlatamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — route parametrlari va REST usullari</h4>
<pre><code>const users = [
  { id: 1, ism: 'Olim' },
  { id: 2, ism: 'Vali' },
];

app.get('/users', (req, res) =&gt; {
  res.json(users); // GET — barcha foydalanuvchilarni o'qish
});

app.get('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id); // :id — route parametri, req.params orqali olinadi
  const user = users.find(u =&gt; u.id === id);
  if (!user) return res.status(404).json({ xato: 'Topilmadi' });
  res.json(user);
});

app.post('/users', (req, res) =&gt; {
  res.status(201).json({ xabar: 'Yangi foydalanuvchi yaratildi' }); // POST — yaratish
});

app.delete('/users/:id', (req, res) =&gt; {
  res.json({ xabar: `${req.params.id} o'chirildi` }); // DELETE — o'chirish
});</code></pre>

<p>Bu — REST konvensiyasi: <code>GET</code> o'qish, <code>POST</code> yaratish, <code>PUT</code>/<code>PATCH</code> yangilash, <code>DELETE</code> o'chirish uchun ishlatiladi. Manzil (<code>/users/:id</code>) bir xil, faqat HTTP usuli farq qiladi.</p>

<h4>BLOKA 2 — birinchi middleware</h4>
<pre><code>function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next(); // ❗ MUHIM — keyingi middleware/route'ga o'tish uchun chaqirilishi shart
}

app.use(logger); // HAR BIR so'rov uchun ishga tushadi

app.get('/', (req, res) =&gt; {
  res.send('Bosh sahifa');
});</code></pre>

<p>Endi har bir so'rov konsolga <code>GET /</code>, <code>POST /users</code> kabi yozib boradi — <code>logger</code>ni har bir route ichiga alohida yozmasdan.</p>

<h4>BLOKA 3 — bir nechta middleware zanjiri</h4>
<pre><code>function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Token yo\\'q' });
  next(); // token bor — keyingisiga o'tamiz
}

// Faqat MA'LUM bir route uchun middleware:
app.get('/profil', authTekshir, (req, res) =&gt; {
  res.json({ xabar: 'Bu — himoyalangan sahifa' });
});</code></pre>

<p><code>authTekshir</code> — <code>app.use()</code> orqali emas, to'g'ridan-to'g'ri <code>app.get()</code>ning ikkinchi argumenti sifatida berilgan. Bu — faqat <code>/profil</code> route'iga tegishli middleware.</p>

<h3>🐛 Ataylab xato — middleware'ni noto'g'ri tartibda joylash</h3>
<pre><code>// ❌ Route middleware'dan OLDIN yozilgan!
app.get('/profil', (req, res) =&gt; {
  res.json({ xabar: 'Himoyalangan sahifa' });
});

function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: 'Token yo\\'q' });
  next();
}

app.use(authTekshir); // ❌ /profil'dan KEYIN ro'yxatga olindi</code></pre>

<p><strong>Natija:</strong> <code>/profil</code>ga token'siz so'rov yuborsangiz ham — <strong>himoya ishlamaydi</strong>, sahifa ochiladi! Sabab: Express route va middleware'larni <strong>ro'yxatga olingan tartibda</strong>, yuqoridan pastga qarab tekshiradi. <code>/profil</code> route'i <code>authTekshir</code>dan oldin yozilgani uchun, so'rov <code>authTekshir</code>ga umuman yetib bormaydi — u faqat <code>/profil</code>dan <strong>keyin</strong> ro'yxatga olingan route'lar uchun ishlaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Middleware — nima?</h4>
<p>Middleware — <code>(req, res, next)</code> imzosiga ega oddiy funksiya. U so'rovni ko'rishi, o'zgartirishi, yoki to'xtatishi mumkin. <code>next()</code> chaqirilsa — so'rov navbatdagi middleware/route'ga o'tadi. <code>next()</code> chaqirilmasa (va javob ham yuborilmasa) — so'rov 1-darsdagidek "osilib qoladi".</p>

<h4>2. Tartib — hammasi ro'yxatga olingan ketma-ketlikka bog'liq</h4>
<p>Express so'rov kelganda, <code>app.use()</code>/<code>app.get()</code> va h.k.larni <strong>kod qanday yozilgan bo'lsa, shu tartibda</strong> tekshiradi. Bu — Express'dagi eng muhim, lekin ko'pincha unutiladigan qoida: <strong>himoya middleware'i har doim himoyalanadigan route'lardan OLDIN</strong> yozilishi kerak.</p>

<h4>3. app.use() vs app.get()</h4>
<table>
<tr><th></th><th>app.use(fn)</th><th>app.get(manzil, fn)</th></tr>
<tr><td>Qaysi HTTP usulga</td><td>Barchasiga (GET, POST, ...)</td><td>Faqat GET'ga</td></tr>
<tr><td>Qaysi manzilga</td><td>Barchasiga (agar manzil berilmasa)</td><td>Faqat ko'rsatilgan manzilga</td></tr>
</table>

<h4>4. Route parametri (:id) vs query string (?key=val)</h4>
<pre><code>// Route parametri — manzilning bir qismi
app.get('/users/:id', (req, res) =&gt; {
  console.log(req.params.id); // /users/5 -> "5"
});

// Query string — ? dan keyingi qism
app.get('/search', (req, res) =&gt; {
  console.log(req.query.q); // /search?q=olim -> "olim"
});</code></pre>

<h4>5. HTTP status kodlari — nega muhim?</h4>
<p><code>res.status(201)</code> — "yaratildi", <code>res.status(404)</code> — "topilmadi", <code>res.status(401)</code> — "avtorizatsiya yo'q". Frontend (React) bu kodlarga qarab qanday xatti-harakat qilishni hal qiladi — status kodini to'g'ri qo'yish backend'ning "tili"ni tushunarli qiladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ REST konvensiyasi: GET o'qish, POST yaratish, PUT/PATCH yangilash, DELETE o'chirish uchun</li>
<li>✅ Route parametri (<code>:id</code>) — <code>req.params</code> orqali, query string — <code>req.query</code> orqali olinadi</li>
<li>✅ Middleware — <code>(req, res, next)</code> funksiyasi, <code>next()</code> chaqirilmasa so'rov to'xtaydi</li>
<li>✅ Express middleware/route'larni ro'yxatga olingan tartibda tekshiradi — tartib muhim</li>
<li>✅ Himoya middleware'i himoyalanadigan route'lardan OLDIN yozilishi shart</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 2: Routing va middleware
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

const users = [
  { id: 1, ism: 'Olim' },
  { id: 2, ism: 'Vali' },
];

// ─────────────────────────────────────────────────────────────────────
// 1) Route parametrlari va REST usullari
// ─────────────────────────────────────────────────────────────────────

app.get('/users', (req, res) => {
  res.json(users);
});

app.get('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  const user = users.find(u => u.id === id);
  if (!user) return res.status(404).json({ xato: 'Topilmadi' });
  res.json(user);
});

app.post('/users', (req, res) => {
  res.status(201).json({ xabar: 'Yangi foydalanuvchi yaratildi' });
});

app.delete('/users/:id', (req, res) => {
  res.json({ xabar: `${req.params.id} o'chirildi` });
});

// ─────────────────────────────────────────────────────────────────────
// 2) Birinchi middleware — har bir so'rov uchun
// ─────────────────────────────────────────────────────────────────────

function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next(); // MUHIM — keyingisiga o'tish uchun
}

app.use(logger);

// ─────────────────────────────────────────────────────────────────────
// 3) Faqat ma'lum route uchun middleware
// ─────────────────────────────────────────────────────────────────────

function authTekshir(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: "Token yo'q" });
  next();
}

app.get('/profil', authTekshir, (req, res) => {
  res.json({ xabar: 'Bu — himoyalangan sahifa' });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — middleware'ni noto'g'ri tartibda joylash
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/profilXato', (req, res) => {
  res.json({ xabar: 'Himoyalangan bo\\'lishi kerak edi' });
});

function authTekshirXato(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) return res.status(401).json({ xato: "Token yo'q" });
  next();
}

app.use(authTekshirXato); // ❌ /profilXato'dan KEYIN ro'yxatga olindi —
// route'ga hech qachon yetib bormaydi, himoya ishlamaydi.
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L2_EX = [
    {
        "title": "REST usullari qaysi amalga mos keladi?",
        "description": "REST konvensiyasida qaysi HTTP usuli \"yangi resurs yaratish\" uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": ["GET", "POST", "DELETE", "PUT"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "GET — o'qish, POST — yaratish, PUT/PATCH — yangilash, DELETE — o'chirish.",
        "explanation": "REST konvensiyasida POST yangi resurs yaratish uchun ishlatiladi. GET — o'qish, PUT/PATCH — yangilash, DELETE — o'chirish uchun.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Middleware'da next() chaqirilmasa nima bo'ladi?",
        "description": "Agar middleware funksiyasi ichida next() chaqirilmasa va javob ham yuborilmasa, nima yuz beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Keyingi middleware/route avtomatik ishga tushadi",
            "So'rov \"osilib qoladi\" — hech qanday javob kelmaydi",
            "Server darhol qayta ishga tushadi",
            "Xato xabari darhol chiqadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "1-darsni eslang — javob yuborilmasa, so'rov abadiy kutadi.",
        "explanation": "next() — so'rovni keyingi middleware/route'ga o'tkazadi. Agar u chaqirilmasa va javob ham yuborilmasa, so'rov hech qachon davom etmaydi va \"osilib qoladi\".",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "req.params va req.query orasidagi farq",
        "description": "/users/5?faol=true so'roviga to'g'ri mos qo'yish: qaysi qism req.params, qaysi qism req.query bo'ladi?",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "req.params.id — \"5\" (manzil qismi, :id)",
            "req.query.faol — \"true\" (? dan keyingi qism)",
        ],
        "correct_order": [
            "req.params.id — \"5\" (manzil qismi, :id)",
            "req.query.faol — \"true\" (? dan keyingi qism)",
        ],
        "hint": "Manzildagi : bilan boshlangan qism — params, ? dan keyingi qism — query.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega middleware'ni himoyalanadigan route'dan OLDIN yozish shart?",
        "description": (
            "Agar authTekshir middleware'i app.use() orqali /profil route'idan "
            "KEYIN ro'yxatga olinsa, nega himoya ishlamaydi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Express so'rov kelganda middleware va route'larni kod qanday "
            "yozilgan bo'lsa, shu ketma-ketlikda, yuqoridan pastga qarab "
            "tekshiradi. Agar /profil route'i authTekshir middleware'idan "
            "oldin ro'yxatga olingan bo'lsa, /profil'ga kelgan so'rov "
            "authTekshir'ga umuman yetib bormasdan, to'g'ridan-to'g'ri "
            "/profil'ning o'z handler'i tomonidan qayta ishlanadi. "
            "authTekshir faqat undan KEYIN ro'yxatga olingan route'lar uchun "
            "ishlaydi, shuning uchun tartibni to'g'ri qo'yish juda muhim."
        ),
        "hint": "Express route/middleware'larni qanday tartibda tekshirishini eslang.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>Request/Response chuqurroq — req.body, status kodlari</h2>

<pre class="mermaid">
flowchart LR
    C["Klient: JSON body bilan POST"] --> P["express.json() — matnni obyektga aylantiradi"]
    P --> H["handler: req.body ishlaydi"]
    H --> S["to'g'ri status kod bilan javob"]
</pre>

<p>2-darsda <code>req.params</code> va <code>req.query</code>ni ko'rdik. Endi — klient <strong>JSON body</strong> yuborganda (masalan, yangi foydalanuvchi yaratishda) buni qanday o'qish kerakligini ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — express.json() va req.body</h4>
<pre><code>const express = require('express');
const app = express();

app.use(express.json()); // ❗ HTTP body'ni JSON obyektga aylantiradi

app.post('/users', (req, res) =&gt; {
  console.log(req.body); // { ism: 'Olim', yosh: 22 }
  const yangiUser = { id: Date.now(), ...req.body };
  res.status(201).json(yangiUser);
});</code></pre>

<pre><code>// Klient tomondan (masalan, fetch orqali):
fetch('/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ism: 'Olim', yosh: 22 }),
});</code></pre>

<h4>BLOKA 2 — PUT/PATCH va to'g'ri status kodlar</h4>
<pre><code>let users = [{ id: 1, ism: 'Olim', yosh: 22 }];

app.put('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  const index = users.findIndex(u =&gt; u.id === id);
  if (index === -1) {
    return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
  }
  users[index] = { ...users[index], ...req.body };
  res.status(200).json(users[index]);
});

app.delete('/users/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  users = users.filter(u =&gt; u.id !== id);
  res.status(204).send(); // 204 — muvaffaqiyatli, lekin body yo'q
});</code></pre>

<h4>BLOKA 3 — oddiy validatsiya</h4>
<pre><code>app.post('/users', (req, res) =&gt; {
  const { ism, yosh } = req.body;

  if (!ism || typeof ism !== 'string') {
    return res.status(400).json({ xato: "'ism' majburiy va matn bo'lishi kerak" });
  }
  if (yosh !== undefined &amp;&amp; typeof yosh !== 'number') {
    return res.status(400).json({ xato: "'yosh' son bo'lishi kerak" });
  }

  const yangiUser = { id: Date.now(), ism, yosh };
  res.status(201).json(yangiUser);
});</code></pre>

<h3>🐛 Ataylab xato — express.json() ni unutish</h3>
<pre><code>const express = require('express');
const app = express();

// ❌ app.use(express.json()) YO'Q!

app.post('/users', (req, res) =&gt; {
  console.log(req.body); // undefined!
  const yangiUser = { id: Date.now(), ...req.body }; // ...undefined — xato emas, lekin natija bo'sh
  res.status(201).json(yangiUser); // { id: 12345 } — ism/yosh yo'qolgan!
});</code></pre>

<p><strong>Natija:</strong> klient <code>{ ism: 'Olim', yosh: 22 }</code> yuborsa ham, <code>req.body</code> — <code>undefined</code> bo'ladi. Xato xabari chiqmaydi (<code>...undefined</code> — JavaScript'da xato emas, hech narsa qo'shmaydi), lekin natijada foydalanuvchi ma'lumotlari <strong>jimgina yo'qoladi</strong>. Sabab: Express standart holatda HTTP so'rov tanasini (body) <strong>xom matn</strong> sifatida qabul qiladi — uni JSON obyektiga aylantirish uchun <code>express.json()</code> middleware'i kerak.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega req.body avtomatik ishlamaydi?</h4>
<p>HTTP so'rovining "body" qismi — tarmoq orqali kelayotgan xom bayt/matn oqimi. Express bu oqimni avtomatik JSON deb hisoblamaydi — chunki u XML, oddiy matn, fayl va h.k. ham bo'lishi mumkin. <code>express.json()</code> — aynan <code>Content-Type: application/json</code> so'rovlarini o'qib, <code>req.body</code>ga tayyor obyekt sifatida joylashtiradi.</p>

<h4>2. express.json() vs express.urlencoded()</h4>
<pre><code>app.use(express.json());                       // JSON body uchun (API'lar, fetch)
app.use(express.urlencoded({ extended: true })); // HTML &lt;form&gt; POST uchun</code></pre>

<h4>3. Eng ko'p ishlatiladigan status kodlar</h4>
<table>
<tr><th>Kod</th><th>Ma'nosi</th><th>Qachon</th></tr>
<tr><td>200</td><td>OK</td><td>Muvaffaqiyatli GET/PUT</td></tr>
<tr><td>201</td><td>Created</td><td>Muvaffaqiyatli POST (yangi resurs)</td></tr>
<tr><td>204</td><td>No Content</td><td>Muvaffaqiyatli, lekin qaytariladigan body yo'q (masalan, DELETE)</td></tr>
<tr><td>400</td><td>Bad Request</td><td>Klient noto'g'ri/yetishmayotgan ma'lumot yubordi</td></tr>
<tr><td>401</td><td>Unauthorized</td><td>Autentifikatsiya kerak</td></tr>
<tr><td>404</td><td>Not Found</td><td>Resurs topilmadi</td></tr>
<tr><td>500</td><td>Internal Server Error</td><td>Server tomonidagi kutilmagan xato</td></tr>
</table>

<h4>4. Oddiy validatsiya — nega qo'lda tekshirish kerak?</h4>
<p>Klient har doim to'g'ri ma'lumot yubormaydi — ba'zan maydon yetishmaydi, ba'zan noto'g'ri tur (masalan, son o'rniga matn). Serverga ishonib bo'lmaydi: <strong>har doim tashqi ma'lumotni tekshiring</strong>, tur va majburiy maydonlarni ma'lumotlar bazasiga yozishdan oldin.</p>

<h4>5. return bilan erta chiqish</h4>
<p><code>return res.status(400).json(...)</code> — <code>return</code> so'zi funksiyani shu yerda to'xtatadi. Agar <code>return</code>ni unutsangiz, kod davom etadi va ehtimol ikkinchi marta <code>res.json()</code> chaqirilib, <code>"Cannot set headers after they are sent"</code> xatosiga olib keladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>express.json()</code> — HTTP body'ni JSON obyektga aylantiradi, <code>req.body</code>ni ishga tushiradi</li>
<li>✅ <code>express.json()</code>ni unutish — <code>req.body</code> <code>undefined</code> bo'lib qoladi, jim xato</li>
<li>✅ Status kodlar: 200/201/204 — muvaffaqiyat, 400/401/404 — klient xatosi, 500 — server xatosi</li>
<li>✅ Tashqi ma'lumotni (req.body) har doim ishlatishdan oldin tekshiring</li>
<li>✅ <code>return res.json(...)</code> — funksiyani to'xtatib, keyingi kod ishga tushmasligini ta'minlaydi</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 3: Request/Response chuqurroq
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();

app.use(express.json()); // HTTP body'ni JSON obyektga aylantiradi

let users = [{ id: 1, ism: 'Olim', yosh: 22 }];

// ─────────────────────────────────────────────────────────────────────
// 1) req.body — POST bilan yangi resurs yaratish
// ─────────────────────────────────────────────────────────────────────

app.post('/users', (req, res) => {
  const { ism, yosh } = req.body;

  // ─── Oddiy validatsiya ───
  if (!ism || typeof ism !== 'string') {
    return res.status(400).json({ xato: "'ism' majburiy va matn bo'lishi kerak" });
  }
  if (yosh !== undefined && typeof yosh !== 'number') {
    return res.status(400).json({ xato: "'yosh' son bo'lishi kerak" });
  }

  const yangiUser = { id: Date.now(), ism, yosh };
  users.push(yangiUser);
  res.status(201).json(yangiUser);
});

// ─────────────────────────────────────────────────────────────────────
// 2) PUT — to'liq yangilash
// ─────────────────────────────────────────────────────────────────────

app.put('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  const index = users.findIndex(u => u.id === id);
  if (index === -1) {
    return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
  }
  users[index] = { ...users[index], ...req.body };
  res.status(200).json(users[index]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) DELETE — 204 No Content
// ─────────────────────────────────────────────────────────────────────

app.delete('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  users = users.filter(u => u.id !== id);
  res.status(204).send();
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — express.json()ni unutish
// ─────────────────────────────────────────────────────────────────────

/*
const appXato = express();
// ❌ appXato.use(express.json()) YO'Q!

appXato.post('/users', (req, res) => {
  console.log(req.body); // undefined!
  const yangiUser = { id: Date.now(), ...req.body }; // faqat { id }
  res.status(201).json(yangiUser); // ism/yosh jimgina yo'qoladi
});
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L3_EX = [
    {
        "title": "req.body ishlashi uchun nima kerak?",
        "description": "Express'da req.body to'g'ri ishlashi (JSON obyekt sifatida) uchun nima sozlanishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa — u avtomatik ishlaydi",
            "app.use(express.json()) middleware'ini qo'shish",
            "req.body ni qo'lda JSON.parse() qilish har bir route'da",
            "Faqat GET so'rovlarida ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Express HTTP body'ni standart holda xom matn deb hisoblaydi.",
        "explanation": "express.json() middleware'i JSON Content-Type'li so'rov tanasini o'qib, uni req.body sifatida tayyor obyekt qilib beradi. Bu middleware qo'shilmasa, req.body undefined bo'lib qoladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Qaysi status kod DELETE muvaffaqiyati uchun mos?",
        "description": "Resurs muvaffaqiyatli o'chirilgan, lekin javobda qaytariladigan ma'lumot yo'q. Qaysi status kod eng mos?",
        "exercise_type": "multiple_choice",
        "options": ["200", "201", "204", "404"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "204 — \"No Content\": muvaffaqiyatli, lekin qaytariladigan body yo'q.",
        "explanation": "204 No Content — operatsiya muvaffaqiyatli bajarilgan, lekin javobda qaytarish uchun body yo'qligini bildiradi. Bu ayniqsa DELETE uchun mos.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "express.json() unutilsa nima bo'ladi?",
        "description": "app.use(express.json()) yozilmasa va klient JSON body yuborsa, req.body qanday qiymatga ega bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Xato chiqadi, server ishlamay qoladi",
            "req.body — undefined bo'ladi",
            "req.body — bo'sh massiv bo'ladi",
            "Hech qanday farq bo'lmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Body parser bo'lmasa, Express so'rov tanasini o'qib obyektga aylantirmaydi.",
        "explanation": "express.json() bo'lmasa, req.body hech qachon to'ldirilmaydi va undefined bo'lib qoladi — hech qanday xato chiqmasdan, jim tarzda.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega req.body ni har doim ishlatishdan oldin tekshirish kerak?",
        "description": (
            "POST /users route'ida req.body dan kelgan ism/yosh maydonlarini "
            "ma'lumotlar bazasiga yozishdan OLDIN nega tekshirish (validatsiya "
            "qilish) kerak? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Klient tomonidan yuborilgan ma'lumotga hech qachon to'liq ishonib "
            "bo'lmaydi — dasturiy xato, foydalanuvchi xatosi, yoki ataylab "
            "noto'g'ri ma'lumot yuborish tufayli kutilgan maydon yo'q "
            "bo'lishi, noto'g'ri turdagi qiymat kelishi mumkin. Agar bunday "
            "ma'lumotni tekshirmasdan to'g'ridan-to'g'ri ma'lumotlar bazasiga "
            "yozsangiz, buzuq yoki noto'g'ri ma'lumotlar saqlanib qolishi, "
            "yoki kutilmagan runtime xatolari yuz berishi mumkin. Validatsiya "
            "— tizim chegarasida (bu yerda: klientdan kelgan ma'lumot) "
            "har doim amalga oshirilishi kerak."
        ),
        "hint": "Klientdan kelgan ma'lumotga qanchalik ishonish mumkinligi haqida o'ylang.",
        "difficulty_level": "Medium",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>Router bilan loyihani tashkil qilish</h2>

<pre class="mermaid">
flowchart LR
    A["server.js"] -->|app.use('/users', ...)| UR["routes/users.js — Router"]
    A -->|app.use('/products', ...)| PR["routes/products.js — Router"]
    UR --> U1["GET /users"]
    UR --> U2["POST /users"]
    PR --> P1["GET /products"]
</pre>

<p>Hozirgacha barcha route'larni bitta <code>server.js</code> faylida yozib keldik. 5-10 ta route uchun bu yaxshi ishlaydi, lekin 50 ta route bo'lsa — bitta fayl o'qib bo'lmas darajada uzun bo'lib ketadi. <code>express.Router()</code> — route'larni mavzu bo'yicha alohida fayllarga bo'lish uchun mo'ljallangan mini-Express ilova.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi Router</h4>
<pre><code>// routes/users.js
const express = require('express');
const router = express.Router(); // ❗ mini-app, o'ziga xos get/post/put/delete'ga ega

router.get('/', (req, res) =&gt; {
  res.json([{ id: 1, ism: 'Olim' }]);
});

router.get('/:id', (req, res) =&gt; {
  res.json({ id: Number(req.params.id), ism: 'Olim' });
});

module.exports = router; // ❗ boshqa faylda ishlatish uchun eksport qilamiz</code></pre>

<h4>BLOKA 2 — router'ni server.js'da ulash</h4>
<pre><code>// server.js
const express = require('express');
const usersRouter = require('./routes/users');

const app = express();
app.use(express.json());

app.use('/users', usersRouter); // ❗ shu yerdan boshlab /users prefiksi qo'shiladi

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});

// Natija: router.get('/') -&gt; GET /users
//         router.get('/:id') -&gt; GET /users/:id</code></pre>

<h4>BLOKA 3 — bir nechta Router va loyiha tuzilishi</h4>
<pre><code>// routes/products.js
const express = require('express');
const router = express.Router();

router.get('/', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});

module.exports = router;</code></pre>

<pre><code>// server.js — barcha router'larni ulash
const usersRouter = require('./routes/users');
const productsRouter = require('./routes/products');

app.use('/users', usersRouter);
app.use('/products', productsRouter);

// Loyiha tuzilishi:
// project/
//   server.js
//   routes/
//     users.js
//     products.js</code></pre>

<h3>🐛 Ataylab xato — router'ni app.use() bilan ulashni unutish</h3>
<pre><code>// routes/orders.js — to'liq yozilgan, xato yo'q
const router = express.Router();
router.get('/', (req, res) =&gt; res.json([{ id: 1 }]));
module.exports = router;

// server.js
const ordersRouter = require('./routes/orders');
// ❌ app.use('/orders', ordersRouter) — YOZILMAGAN!

app.listen(3000);</code></pre>

<p><strong>Natija:</strong> <code>GET /orders</code>ga so'rov yuborilsa — <code>404 Not Found</code>. Kod xatosiz, route to'g'ri yozilgan, hatto <code>require</code> ham qilingan — lekin Express bu Router haqida hech qachon bilmaydi, chunki uni ilovaga <strong>ulashmadingiz</strong>. <code>require()</code> faylni yuklaydi, lekin <code>app.use()</code>gina uni haqiqatan routing zanjiriga qo'shadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega Router kerak?</h4>
<p>Loyiha kattalashgan sari, barcha route'larni bitta faylda saqlash ularni topish va o'zgartirishni qiyinlashtiradi. Router — route'larni mavzu (foydalanuvchilar, mahsulotlar, buyurtmalar) bo'yicha alohida fayllarga ajratish, kodni o'qish va boshqarishni osonlashtirish imkonini beradi.</p>

<h4>2. router.get/post/put/delete — app.* bilan bir xil, lekin "scoped"</h4>
<p><code>express.Router()</code> — <code>app</code>ning kichik nusxasi: bir xil <code>.get()</code>, <code>.post()</code>, <code>.put()</code>, <code>.delete()</code> metodlariga ega, lekin route manzillari faqat shu Router ulanadigan prefiks ichida ishlaydi.</p>

<h4>3. module.exports = router</h4>
<p>Har bir route fayli Router obyektini <code>module.exports</code> orqali eksport qiladi, shunda uni <code>require()</code> yordamida boshqa faylda (odatda <code>server.js</code>da) import qilish mumkin.</p>

<h4>4. app.use(prefiks, router) — prefiks qanday ishlaydi</h4>
<pre><code>app.use('/users', usersRouter);
// usersRouter ichidagi router.get('/')       -&gt; GET  /users
// usersRouter ichidagi router.get('/:id')    -&gt; GET  /users/:id
// usersRouter ichidagi router.post('/')      -&gt; POST /users</code></pre>
<p>Router faylining ichida siz faqat <strong>nisbiy</strong> yo'lni yozasiz (<code>'/'</code>, <code>'/:id'</code>) — to'liq yo'lni <code>app.use()</code>dagi prefiks bilan Express o'zi birlashtiradi.</p>

<h4>5. Tavsiya etilgan loyiha tuzilishi</h4>
<pre><code>project/
  server.js          # faqat: middleware, router'larni ulash, listen
  routes/
    users.js          # /users bilan bog'liq barcha route'lar
    products.js        # /products bilan bog'liq barcha route'lar
  package.json</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>express.Router()</code> — route'larni alohida fayllarga bo'lish uchun mini-ilova</li>
<li>✅ Har bir route fayli <code>module.exports = router</code> bilan tugaydi</li>
<li>✅ <code>app.use(prefiks, router)</code> — Router'ni asosiy ilovaga ulaydi va prefiks qo'shadi</li>
<li>✅ <code>require()</code> faylni yuklaydi, lekin <code>app.use()</code>siz Router hech qachon ishlamaydi — natija: jim 404</li>
<li>✅ Katta loyihalarda route'larni mavzu bo'yicha <code>routes/</code> papkasiga bo'lish odatiy amaliyot</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 4: Router bilan loyihani tashkil qilish
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// routes/users.js
// ─────────────────────────────────────────────────────────────────────
const express = require('express');
const usersRouter = express.Router();

usersRouter.get('/', (req, res) => {
  res.json([{ id: 1, ism: 'Olim' }, { id: 2, ism: 'Vali' }]);
});

usersRouter.get('/:id', (req, res) => {
  res.json({ id: Number(req.params.id), ism: 'Olim' });
});

usersRouter.post('/', (req, res) => {
  const { ism } = req.body;
  if (!ism) {
    return res.status(400).json({ xato: "'ism' majburiy" });
  }
  res.status(201).json({ id: Date.now(), ism });
});

// module.exports = usersRouter;  // alohida faylda bo'lganda shart

// ─────────────────────────────────────────────────────────────────────
// routes/products.js
// ─────────────────────────────────────────────────────────────────────
const productsRouter = express.Router();

productsRouter.get('/', (req, res) => {
  res.json([{ id: 1, nomi: 'Noutbuk' }, { id: 2, nomi: 'Sichqoncha' }]);
});

// module.exports = productsRouter;

// ─────────────────────────────────────────────────────────────────────
// server.js — barcha router'larni ulash
// ─────────────────────────────────────────────────────────────────────
// const usersRouter = require('./routes/users');
// const productsRouter = require('./routes/products');

const app = express();
app.use(express.json());

app.use('/users', usersRouter);
app.use('/products', productsRouter);

// ─────────────────────────────────────────────────────────────────────
// Ataylab xato — ulashni unutish (izohda, ishga tushmaydi)
// ─────────────────────────────────────────────────────────────────────
/*
const ordersRouter = express.Router();
ordersRouter.get('/', (req, res) => res.json([{ id: 1 }]));
// ❌ app.use('/orders', ordersRouter) — YOZILMAGAN!
// Natija: GET /orders -> 404 Not Found, garchi route to'g'ri yozilgan bo'lsa ham.
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
  console.log('Sinab ko\\'ring: GET /users, GET /products');
});
"""

L4_EX = [
    {
        "title": "express.Router() nima?",
        "description": "express.Router() aslida nima vazifani bajaradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumotlar bazasiga ulanish",
            "Route'larni alohida faylga bo'lish uchun mini-Express ilova",
            "Xatolarni avtomatik tuzatuvchi vosita",
            "Serverni tezlashtiruvchi kesh tizimi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "U app'ga o'xshaydi, lekin kichikroq va bitta mavzuga bag'ishlangan.",
        "explanation": "express.Router() — app'ning kichik nusxasi: o'ziga xos get/post/put/delete metodlariga ega, route'larni mavzu bo'yicha alohida fayllarga ajratish uchun ishlatiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Router qanday ulanadi?",
        "description": "routes/users.js faylida yozilgan Router asosiy ilovada ishlashi uchun nima qilish kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat require() qilish yetarli",
            "app.use(prefiks, router) chaqirish shart",
            "Fayl nomini server.js deb o'zgartirish",
            "Hech narsa — u avtomatik ulanadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "require() faylni yuklaydi, lekin uni routing zanjiriga qo'shmaydi.",
        "explanation": "require() faylni yuklab, obyektni qaytaradi, lekin Express bu Router'ni faqat app.use(prefiks, router) chaqirilgandan keyingina haqiqiy routing zanjiriga qo'shadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Router ichidagi yo'l qanday to'liq manzilga aylanadi?",
        "description": "app.use('/users', usersRouter) yozilgan, usersRouter ichida router.get('/:id') bor. Elementlarni to'g'ri tartibda joylang: qaysi qism birinchi qo'shiladi, qaysi qism oxirida.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "app.use() dagi prefiks: '/users'",
            "Router ichidagi nisbiy yo'l: '/:id'",
            "Yakuniy to'liq manzil: '/users/:id'",
        ],
        "correct_order": [
            "app.use() dagi prefiks: '/users'",
            "Router ichidagi nisbiy yo'l: '/:id'",
            "Yakuniy to'liq manzil: '/users/:id'",
        ],
        "hint": "Prefiks va Router ichidagi nisbiy yo'l birlashib, to'liq manzilni hosil qiladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Router yozilgan, lekin ulanmagan — nima bo'ladi?",
        "description": (
            "routes/orders.js faylida Router to'liq va xatosiz yozilgan, "
            "server.js'da require() ham qilingan, lekin app.use('/orders', "
            "ordersRouter) yozilmagan. GET /orders so'roviga qanday javob "
            "qaytadi va nega? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Javob 404 Not Found bo'ladi. Sabab: require() faylni yuklaydi va "
            "undagi Router obyektini xotiraga oladi, lekin bu — Express'ga "
            "\"bu route'lar mavjud\" deb aytish emas. Faqat app.use(prefiks, "
            "router) chaqirilgandagina Express bu Router'ni o'zining routing "
            "zanjiriga qo'shadi va so'rovlarni unga yo'naltira boshlaydi. Bu "
            "qadam bo'lmasa, Express /orders manzilini umuman tanimaydi va "
            "standart \"topilmadi\" javobini qaytaradi — garchi Router kodi "
            "o'zi to'liq to'g'ri yozilgan bo'lsa ham."
        ),
        "hint": "require() va app.use() ikkalasi ham kerak — biri yuklaydi, ikkinchisi ulaydi. Farqini o'ylang.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R1_TEXT = """\
<h2>R1 — 1-4-darslarni takrorlash: Mini Todo REST API</h2>

<p>1-4 darslarning hammasini birlashtirib, to'liq ishlaydigan Todo REST API yasaymiz: routing, middleware, req.body/status kodlar, va Router bilan loyiha tuzilishi — hammasi birga.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>routes/todos.js</code> — barcha todo route'lari alohida faylda (4-dars)</li>
<li>Logging middleware — har bir so'rovni konsolga yozadi (2-dars)</li>
<li>To'liq CRUD: <code>GET /todos</code>, <code>POST /todos</code>, <code>PUT /todos/:id</code>, <code>DELETE /todos/:id</code> (1-3 darslar)</li>
<li>Validatsiya va to'g'ri status kodlar (3-dars)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — logging middleware</h4>
<p>Har bir so'rov uchun metod va manzilni konsolga chiqaruvchi middleware yozing, uni <code>app.use()</code> orqali <strong>eng birinchi</strong> qo'shing (2-darsdagidek).</p>

<h4>Vazifa 2 — routes/todos.js (Router)</h4>
<p><code>express.Router()</code> yordamida barcha todo route'larini alohida modulga chiqaring, <code>module.exports</code> qiling (4-darsdagidek).</p>

<h4>Vazifa 3 — to'liq CRUD</h4>
<p><code>GET /todos</code> — hammasi, <code>POST /todos</code> — yangi qo'shish (201), <code>PUT /todos/:id</code> — <code>bajarildi</code> holatini almashtirish, <code>DELETE /todos/:id</code> — o'chirish (204).</p>

<h4>Vazifa 4 — validatsiya</h4>
<p><code>POST /todos</code>da <code>matn</code> maydoni bo'lmasa yoki bo'sh bo'lsa — <code>400</code> va tushunarli xato xabari qaytaring (3-darsdagidek).</p>

<h3>🐛 Ataylab qiyin: middleware tartibi</h3>
<p>Logging middleware'ni <code>app.use('/todos', todosRouter)</code>dan <strong>keyin</strong> qo'ysangiz, u faqat <code>/todos</code>ga tegishli bo'lmagan so'rovlarda ishlaydi (chunki Router allaqachon javobni yuborib bo'lgan bo'ladi). To'g'ri tartib: middleware'lar har doim ular ta'sir qilishi kerak bo'lgan route'lardan <strong>oldin</strong> ro'yxatdan o'tkaziladi (2-darsni eslang — Express middleware'larni yozilish tartibida ishga tushiradi).</p>

<h3>Boshlang'ich kod</h3>
<pre><code>const express = require('express');
const app = express();

// Vazifa 1: logging middleware (bu yerda, route'lardan OLDIN)

app.use(express.json());

// Vazifa 2: routes/todos.js — Router yasang, shu yerda ulang
// app.use('/todos', todosRouter);

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>// ─── routes/todos.js ───
const express = require('express');
const todosRouter = express.Router();

let todos = [{ id: 1, matn: 'Node.js o\\'rganish', bajarildi: false }];

todosRouter.get('/', (req, res) =&gt; {
  res.json(todos);
});

todosRouter.post('/', (req, res) =&gt; {
  const { matn } = req.body;
  if (!matn || typeof matn !== 'string' || !matn.trim()) {
    return res.status(400).json({ xato: "'matn' majburiy va bo'sh bo'lmasligi kerak" });
  }
  const yangiTodo = { id: Date.now(), matn, bajarildi: false };
  todos.push(yangiTodo);
  res.status(201).json(yangiTodo);
});

todosRouter.put('/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  const todo = todos.find(t =&gt; t.id === id);
  if (!todo) {
    return res.status(404).json({ xato: 'Todo topilmadi' });
  }
  todo.bajarildi = !todo.bajarildi;
  res.status(200).json(todo);
});

todosRouter.delete('/:id', (req, res) =&gt; {
  const id = Number(req.params.id);
  todos = todos.filter(t =&gt; t.id !== id);
  res.status(204).send();
});

module.exports = todosRouter;

// ─── server.js ───
const express = require('express');
const todosRouter = require('./routes/todos');

const app = express();

// Vazifa 1: logging middleware — route'lardan OLDIN
app.use((req, res, next) =&gt; {
  console.log(`${req.method} ${req.url}`);
  next();
});

app.use(express.json());
app.use('/todos', todosRouter);

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-4 darslarning hammasi birga: routing, middleware, req.body, Router</li>
<li>✅ Middleware'lar route'lardan oldin ro'yxatdan o'tkazilishi shart</li>
<li>✅ Router — CRUD route'larini alohida, tartibli faylga chiqarish usuli</li>
<li>✅ To'g'ri status kodlar: 201 (yaratildi), 200 (yangilandi), 204 (o'chirildi), 400/404 (xato)</li>
</ul>
"""

R1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 1: Mini Todo REST API (1-4-darslar)
// ════════════════════════════════════════════════════════════════════

// ─── routes/todos.js ───
const express = require('express');
const todosRouter = express.Router();

let todos = [{ id: 1, matn: "Node.js o'rganish", bajarildi: false }];

todosRouter.get('/', (req, res) => {
  res.json(todos);
});

todosRouter.post('/', (req, res) => {
  const { matn } = req.body;
  if (!matn || typeof matn !== 'string' || !matn.trim()) {
    return res.status(400).json({ xato: "'matn' majburiy va bo'sh bo'lmasligi kerak" });
  }
  const yangiTodo = { id: Date.now(), matn, bajarildi: false };
  todos.push(yangiTodo);
  res.status(201).json(yangiTodo);
});

todosRouter.put('/:id', (req, res) => {
  const id = Number(req.params.id);
  const todo = todos.find(t => t.id === id);
  if (!todo) {
    return res.status(404).json({ xato: 'Todo topilmadi' });
  }
  todo.bajarildi = !todo.bajarildi;
  res.status(200).json(todo);
});

todosRouter.delete('/:id', (req, res) => {
  const id = Number(req.params.id);
  todos = todos.filter(t => t.id !== id);
  res.status(204).send();
});

// module.exports = todosRouter;

// ─── server.js ───
const app = express();

// Logging middleware — route'lardan OLDIN ro'yxatdan o'tkaziladi
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

app.use(express.json());
app.use('/todos', todosRouter);

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

R1_EX = [
    {
        "title": "Middleware qayerda ro'yxatdan o'tkazilishi kerak?",
        "description": "Logging middleware /todos route'lariga ham ta'sir qilishi uchun uni qayerga qo'yish kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "app.use('/todos', todosRouter) dan keyin",
            "app.use('/todos', todosRouter) dan oldin",
            "Faqat server.js oxirida",
            "Middleware joyi ahamiyatsiz",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Express middleware va route'larni ular yozilgan tartibda ishga tushiradi.",
        "explanation": "Express so'rovni middleware va route'lar orqali yozilish tartibida o'tkazadi. Agar logging middleware Router'dan keyin yozilsa, /todos so'rovlari uchun Router javobni allaqachon yuborib bo'lgan bo'ladi va logging middleware'ga navbat yetmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "DELETE muvaffaqiyati uchun qaysi status kod?",
        "description": "DELETE /todos/:id muvaffaqiyatli bajarilganda (va javobda body yo'q) qaysi status kod qaytarilishi kerak?",
        "exercise_type": "multiple_choice",
        "options": ["200", "201", "204", "404"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "3-darsni eslang: muvaffaqiyatli, lekin qaytariladigan ma'lumot yo'q.",
        "explanation": "204 No Content — operatsiya muvaffaqiyatli, lekin javobda qaytarish uchun body yo'q. DELETE uchun eng mos status kod.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "POST /todos so'rovini to'g'ri tartibda joylang",
        "description": "Klient yangi todo yuborganidan server javob qaytargunga qadar bo'lgan qadamlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Logging middleware so'rovni konsolga yozadi",
            "express.json() req.body ni obyektga aylantiradi",
            "todosRouter.post('/') handler ishga tushadi",
            "matn maydoni tekshiriladi (validatsiya)",
            "Yangi todo massivga qo'shiladi, 201 status bilan javob qaytariladi",
        ],
        "correct_order": [
            "Logging middleware so'rovni konsolga yozadi",
            "express.json() req.body ni obyektga aylantiradi",
            "todosRouter.post('/') handler ishga tushadi",
            "matn maydoni tekshiriladi (validatsiya)",
            "Yangi todo massivga qo'shiladi, 201 status bilan javob qaytariladi",
        ],
        "hint": "Middleware'lar har doim handler'dan oldin, yozilish tartibida ishlaydi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Router + middleware + validatsiyani birga ishlatish muhim?",
        "description": (
            "Kichik Todo API'da ham Router (4-dars), middleware tartibi "
            "(2-dars) va validatsiya (3-dars) ni birga qo'llash nima uchun "
            "muhim? Ularning har biri qanday muammoning oldini oladi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Router kodni mavzu bo'yicha tartibli fayllarga bo'lib, loyiha "
            "kattalashganda uni boshqarishni osonlashtiradi. Middleware'ning "
            "to'g'ri tartibda ro'yxatdan o'tkazilishi — masalan logging yoki "
            "keyinchalik autentifikatsiya kabi umumiy funksiyalarning har bir "
            "kerakli so'rovda albatta ishlashini ta'minlaydi, aks holda ular "
            "e'tibordan chetda qolib ketishi mumkin. Validatsiya esa "
            "klientdan kelgan ishonchsiz ma'lumotni tekshirib, buzuq yoki "
            "noto'g'ri ma'lumotlarning ma'lumotlar bazasiga yozilishining "
            "oldini oladi. Uchalasi birga ishlatilganda — kod ham tartibli, "
            "ham xavfsiz, ham bashorat qilinadigan bo'ladi."
        ),
        "hint": "Har birini alohida-alohida o'ylang: Router nima uchun, middleware tartibi nima uchun, validatsiya nima uchun kerak.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>PostgreSQL ulanish — node-postgres (pg)</h2>

<pre class="mermaid">
flowchart LR
    A["Express route"] --> B["pool.query(sql, params)"]
    B --> C[("PostgreSQL")]
    C --> B
    B --> A
</pre>

<p>Hozirgacha ma'lumotlarni oddiy JavaScript massivida (xotirada) saqlab keldik — server qayta ishga tushsa, hammasi yo'qoladi. SQL kursida PostgreSQL bilan ishlashni o'rgangan edingiz; endi Express'ni aynan shu ma'lumotlar bazasiga ulaymiz — <code>pg</code> paketi yordamida.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — pg o'rnatish va ulanish</h4>
<pre><code>// Terminal:
npm install pg</code></pre>

<pre><code>// db.js
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'parol',
  database: 'mening_bazam',
});

module.exports = pool;</code></pre>

<pre><code>// server.js — ulanishni tekshirish
const pool = require('./db');

pool.query('SELECT NOW()')
  .then(res =&gt; console.log('DB ulandi:', res.rows[0]))
  .catch(err =&gt; console.error('DB xatosi:', err.message));</code></pre>

<h4>BLOKA 2 — parametrlashtirilgan so'rov (parameterized query)</h4>
<pre><code>app.get('/users/:id', async (req, res) =&gt; {
  const id = req.params.id;
  const result = await pool.query(
    'SELECT * FROM users WHERE id = $1', // ❗ $1 — placeholder, qiymat emas
    [id]                                  // ❗ qiymatlar alohida massivda
  );
  if (result.rows.length === 0) {
    return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
  }
  res.json(result.rows[0]);
});</code></pre>

<h4>BLOKA 3 — async/await + try/catch</h4>
<pre><code>app.get('/users', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT id, ism, email FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});</code></pre>

<h3>🐛 Ataylab xato — SQL Injection (string birlashtirish)</h3>
<pre><code>// ❌ XAVFLI — foydalanuvchi kiritgan qiymatni to'g'ridan-to'g'ri qo'shish
app.get('/users/:id', async (req, res) =&gt; {
  const id = req.params.id;
  const result = await pool.query(
    `SELECT * FROM users WHERE id = ${id}` // ❌ string template — xavfli!
  );
  res.json(result.rows[0]);
});

// Hujum: klient id o'rniga shuni yuborsa:
//   /users/1 OR 1=1
// So'rov shunga aylanadi:
//   SELECT * FROM users WHERE id = 1 OR 1=1
// Natija: BARCHA foydalanuvchilar qaytadi — nazoratdan tashqari!</code></pre>

<p><strong>Natija:</strong> agar <code>req.params.id</code> to'g'ridan-to'g'ri SQL matniga qo'shilsa, foydalanuvchi maxsus qiymat yuborib so'rovning ma'nosini butunlay o'zgartirib yuborishi mumkin — bu <strong>SQL Injection</strong> deb ataladi va eng xavfli xavfsizlik zaifliklaridan biri. Yechim — hech qachon qiymatni to'g'ridan-to'g'ri qo'shmaslik, doim <code>$1, $2, ...</code> placeholder va alohida qiymatlar massividan foydalanish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Pool nima, nega Client emas?</h4>
<p><code>Pool</code> — bir nechta DB ulanishini oldindan tayyorlab, so'rovlar orasida qayta ishlatadigan "ulanishlar hovuzi". Har bir so'rov uchun yangi ulanish ochish sekin va qimmat; Pool buni oldini oladi. Amaliyotda deyarli har doim <code>Pool</code> ishlatiladi, alohida <code>Client</code> emas.</p>

<h4>2. Parametrlashtirilgan so'rovlar — $1, $2...</h4>
<pre><code>pool.query('SELECT * FROM users WHERE id = $1 AND faol = $2', [id, true]);
// $1 -&gt; id, $2 -&gt; true — pg kutubxonasi qiymatlarni xavfsiz ekranlaydi (escape)</code></pre>
<p><code>$1</code>, <code>$2</code> — bu shunchaki matn emas, balki pg kutubxonasiga "bu yerga qiymat qo'y, lekin uni SQL kodi sifatida emas, faqat ma'lumot sifatida ishlat" deb aytadigan maxsus belgi.</p>

<h4>3. async/await bilan so'rov</h4>
<p><code>pool.query()</code> — Promise qaytaradi, shuning uchun <code>async/await</code> yoki <code>.then()</code> bilan ishlatiladi. Har doim <code>try/catch</code> ichiga olish tavsiya etiladi — DB vaqtincha mavjud bo'lmasligi yoki so'rov xato bo'lishi mumkin.</p>

<h4>4. result.rows — natija qayerda?</h4>
<p><code>pool.query()</code> natijasi — obyekt, undagi <code>.rows</code> massivi haqiqiy qatorlarni saqlaydi. Bitta qator kutilsa — <code>result.rows[0]</code>, ro'yxat kutilsa — butun <code>result.rows</code>.</p>

<h4>5. .env orqali maxfiy ma'lumotlarni saqlash</h4>
<p>Parol va boshqa maxfiy sozlamalarni hech qachon kodga to'g'ridan-to'g'ri yozmang — <code>.env</code> faylida saqlab, <code>process.env.DB_PASSWORD</code> orqali o'qing (bu keyingi darslarda chuqurroq ko'riladi).</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>pg</code> paketi — Node.js'dan PostgreSQL'ga ulanish uchun standart kutubxona</li>
<li>✅ <code>Pool</code> — bir nechta ulanishni qayta ishlatuvchi hovuz, har bir so'rov uchun alohida ulanishdan tezroq</li>
<li>✅ Parametrlashtirilgan so'rovlar (<code>$1, $2</code>) — SQL Injection'dan himoya qiladi</li>
<li>✅ Foydalanuvchi kiritgan qiymatni SQL matniga to'g'ridan-to'g'ri qo'shish — jiddiy xavfsizlik xatosi</li>
<li>✅ <code>result.rows</code> — so'rov natijasidagi qatorlar massivi</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 5: PostgreSQL ulanish (pg)
// ════════════════════════════════════════════════════════════════════

// ─── db.js ───
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'parol',
  database: 'mening_bazam',
});

// module.exports = pool;

// ─── server.js ───
const express = require('express');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) Ulanishni tekshirish
// ─────────────────────────────────────────────────────────────────────

pool.query('SELECT NOW()')
  .then(res => console.log('DB ulandi:', res.rows[0]))
  .catch(err => console.error('DB xatosi:', err.message));

// ─────────────────────────────────────────────────────────────────────
// 2) Parametrlashtirilgan so'rov — XAVFSIZ
// ─────────────────────────────────────────────────────────────────────

app.get('/users/:id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM users WHERE id = $1',
      [req.params.id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Foydalanuvchi topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ro'yxat qaytarish
// ─────────────────────────────────────────────────────────────────────

app.get('/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, ism, email FROM users ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — SQL Injection (izohda, ishga tushmaydi)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/users-xato/:id', async (req, res) => {
  const result = await pool.query(
    `SELECT * FROM users WHERE id = ${req.params.id}` // ❌ string template — xavfli!
  );
  // Hujum: /users-xato/1 OR 1=1 -> BARCHA foydalanuvchilar qaytadi
  res.json(result.rows[0]);
});
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L5_EX = [
    {
        "title": "Pool nima uchun ishlatiladi?",
        "description": "node-postgres'da Pool nima uchun ishlatiladi (alohida Client o'rniga)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumotlar bazasini avtomatik yaratish uchun",
            "Bir nechta ulanishni qayta ishlatib, har safar yangi ulanish ochishning oldini olish uchun",
            "SQL so'rovlarni tezroq yozish uchun qisqartma",
            "Faqat test muhitida ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Har bir so'rov uchun yangi ulanish ochish sekin va resurs talab qiladi.",
        "explanation": "Pool — oldindan tayyorlangan ulanishlar to'plami bo'lib, so'rovlar orasida qayta ishlatiladi. Bu har bir so'rov uchun yangi DB ulanishi ochishga qaraganda ancha samaraliroq.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "$1 nima vazifani bajaradi?",
        "description": "pool.query('SELECT * FROM users WHERE id = $1', [id]) yozuvida $1 nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "SQL sintaksisi xatosi",
            "Xavfsiz placeholder — qiymat alohida massivdan olinadi va escape qilinadi",
            "Birinchi ustun nomi",
            "Jadval identifikatori",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Qiymat SQL matniga to'g'ridan-to'g'ri qo'shilmaydi — u alohida uzatiladi.",
        "explanation": "$1, $2... — pg kutubxonasiga tegishli placeholder'lar. Ular orqali uzatilgan qiymatlar SQL kodi sifatida emas, faqat ma'lumot sifatida xavfsiz ishlatiladi, bu SQL Injection'ning oldini oladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "So'rov oqimini to'g'ri tartibda joylang",
        "description": "GET /users/:id so'rovi kelganidan javob qaytargunga qadar bo'lgan qadamlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "req.params.id o'qiladi",
            "pool.query('...WHERE id = $1', [id]) chaqiriladi",
            "PostgreSQL so'rovni bajaradi va qator(lar)ni qaytaradi",
            "result.rows tekshiriladi (bo'sh yoki yo'q)",
            "res.json(result.rows[0]) bilan javob yuboriladi",
        ],
        "correct_order": [
            "req.params.id o'qiladi",
            "pool.query('...WHERE id = $1', [id]) chaqiriladi",
            "PostgreSQL so'rovni bajaradi va qator(lar)ni qaytaradi",
            "result.rows tekshiriladi (bo'sh yoki yo'q)",
            "res.json(result.rows[0]) bilan javob yuboriladi",
        ],
        "hint": "So'rov Promise qaytaradi — await orqali natijani kutamiz, keyin uni tekshiramiz.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "SQL Injection qanday ishlaydi va nega xavfli?",
        "description": (
            "`SELECT * FROM users WHERE id = ${req.params.id}` kabi string "
            "template orqali yozilgan so'rov nega xavfli? Foydalanuvchi buni "
            "qanday suiiste'mol qilishi mumkin, va parametrlashtirilgan "
            "so'rov ($1) buni qanday oldini oladi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "String template orqali foydalanuvchi kiritgan qiymat to'g'ridan-"
            "to'g'ri SQL matni ichiga qo'shiladi, bu esa foydalanuvchiga "
            "so'rovning haqiqiy mantiqini o'zgartirish imkonini beradi. "
            "Masalan, id o'rniga '1 OR 1=1' yuborilsa, shart har doim rost "
            "bo'lib qoladi va so'rov jadvaldagi barcha qatorlarni qaytaradi "
            "— garchi faqat bitta foydalanuvchi so'ralgan bo'lsa ham. Bundan "
            "battarroq holatlarda ma'lumotlarni o'chirish yoki o'zgartirish "
            "ham mumkin. Parametrlashtirilgan so'rov ($1, $2 va alohida "
            "qiymatlar massivi) buning oldini oladi, chunki pg kutubxonasi "
            "qiymatlarni SQL kodi sifatida emas, faqat toza ma'lumot "
            "sifatida yuboradi — ular so'rov mantig'iga hech qanday ta'sir "
            "qila olmaydi."
        ),
        "hint": "Foydalanuvchi id o'rniga oddiy sondan boshqa narsa yuborsa nima bo'lishini tasavvur qiling.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>CRUD operatsiyalar — ma'lumotlar bazasi bilan to'liq</h2>

<pre class="mermaid">
flowchart LR
    C["Create — POST"] --> DB[("PostgreSQL")]
    R["Read — GET"] --> DB
    U["Update — PUT"] --> DB
    D["Delete — DELETE"] --> DB
</pre>

<p>5-darsda <code>SELECT</code>ni ko'rdik. Endi — <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>ni Express route'lariga ulaymiz va har birida natijani <strong>to'g'ri tekshirishni</strong> o'rganamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Create (POST, RETURNING)</h4>
<pre><code>app.post('/products', async (req, res) =&gt; {
  const { nomi, narxi } = req.body;
  if (!nomi || typeof narxi !== 'number') {
    return res.status(400).json({ xato: "'nomi' va 'narxi' majburiy" });
  }
  const result = await pool.query(
    'INSERT INTO products (nomi, narxi) VALUES ($1, $2) RETURNING *', // ❗ RETURNING * — yangi qatorni qaytaradi
    [nomi, narxi]
  );
  res.status(201).json(result.rows[0]);
});</code></pre>

<h4>BLOKA 2 — Update (PUT, rowCount tekshirish)</h4>
<pre><code>app.put('/products/:id', async (req, res) =&gt; {
  const { nomi, narxi } = req.body;
  const result = await pool.query(
    'UPDATE products SET nomi = $1, narxi = $2 WHERE id = $3 RETURNING *',
    [nomi, narxi, req.params.id]
  );
  if (result.rowCount === 0) { // ❗ hech qanday qator yangilanmadi
    return res.status(404).json({ xato: 'Mahsulot topilmadi' });
  }
  res.json(result.rows[0]);
});</code></pre>

<h4>BLOKA 3 — Delete (rowCount bilan 404 yoki 204)</h4>
<pre><code>app.delete('/products/:id', async (req, res) =&gt; {
  const result = await pool.query('DELETE FROM products WHERE id = $1', [req.params.id]);
  if (result.rowCount === 0) {
    return res.status(404).json({ xato: 'Mahsulot topilmadi' });
  }
  res.status(204).send();
});</code></pre>

<h3>🐛 Ataylab xato — rowCount'ni tekshirmaslik</h3>
<pre><code>// ❌ rowCount tekshirilmagan
app.put('/products-xato/:id', async (req, res) =&gt; {
  const result = await pool.query(
    'UPDATE products SET nomi = $1 WHERE id = $2 RETURNING *',
    [req.body.nomi, req.params.id]
  );
  res.json(result.rows[0]); // ❌ agar id topilmasa — result.rows[0] === undefined!
});

// Klient /products-xato/9999 (mavjud bo'lmagan id) yuborsa:
// - DB'da hech narsa o'zgarmaydi (0 qator yangilandi)
// - Lekin server 200 status bilan "undefined" qaytaradi
// - Klient buni "muvaffaqiyatli yangilandi" deb noto'g'ri tushunishi mumkin!</code></pre>

<p><strong>Natija:</strong> <code>UPDATE</code> yoki <code>DELETE</code> so'rovi <strong>xatosiz</strong> bajarilishi mumkin, hattoki hech qanday qator topilmasa ham — bu SQL uchun normal holat, xato emas. Agar <code>result.rowCount</code>ni tekshirmasangiz, mavjud bo'lmagan <code>id</code> uchun ham server "hammasi joyida" degandek javob beradi, garchi DB'da haqiqatan hech narsa o'zgarmagan bo'lsa ham. Bu — klientni chalg'ituvchi jim xato.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. RETURNING * — nega kerak?</h4>
<p>PostgreSQL'da <code>INSERT</code>/<code>UPDATE</code> standart holda hech narsa qaytarmaydi. <code>RETURNING *</code> qo'shilsa — operatsiyadan keyingi to'liq qatorni bitta so'rovda olish mumkin, alohida <code>SELECT</code> yozishga hojat qolmaydi.</p>

<h4>2. result.rowCount — nechta qator ta'sirlandi?</h4>
<p><code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> natijasida <code>result.rowCount</code> — nechta qator o'zgartirilgani yoki o'chirilganini bildiradi. <code>0</code> bo'lsa — bunday <code>id</code> umuman topilmagan, demak <code>404</code> qaytarish kerak.</p>

<h4>3. Nega SQL xatosiz ishlaydi, lekin natija noto'g'ri bo'lishi mumkin?</h4>
<p><code>WHERE id = 9999</code> — to'g'ri, xatosiz SQL, garchi bunday <code>id</code> mavjud bo'lmasa ham. PostgreSQL "hech narsa topilmadi" deb xato bermaydi — u shunchaki 0 ta qatorni ta'sirlaydi. Shu sababli natijani tekshirish — dasturchining, ma'lumotlar bazasining emas, vazifasi.</p>

<h4>4. CRUD va status kodlar (3-darsni eslatma)</h4>
<table>
<tr><th>Amal</th><th>HTTP metod</th><th>Muvaffaqiyat</th><th>Topilmasa</th></tr>
<tr><td>Create</td><td>POST</td><td>201</td><td>—</td></tr>
<tr><td>Read</td><td>GET</td><td>200</td><td>404</td></tr>
<tr><td>Update</td><td>PUT</td><td>200</td><td>404</td></tr>
<tr><td>Delete</td><td>DELETE</td><td>204</td><td>404</td></tr>
</table>

<h4>5. try/catch — bu darsda ham shart</h4>
<p>Har bir DB so'rovi (5-darsdagidek) <code>try/catch</code> ichida bo'lishi kerak — tarmoq uzilishi, noto'g'ri SQL, yoki DB vaqtincha ishlamasligi mumkin.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>INSERT ... RETURNING *</code> — yangi qatorni bir so'rovda qaytaradi</li>
<li>✅ <code>result.rowCount</code> — nechta qator ta'sirlanganini bildiradi, <code>UPDATE</code>/<code>DELETE</code>da 404'ni aniqlash uchun ishlatiladi</li>
<li>✅ Mavjud bo'lmagan <code>id</code> uchun <code>UPDATE</code>/<code>DELETE</code> — SQL xatosi emas, lekin <code>rowCount === 0</code></li>
<li>✅ <code>rowCount</code>ni tekshirmaslik — klientga yolg'on "muvaffaqiyat" signalini beradi</li>
<li>✅ CRUD — POST(201), GET(200/404), PUT(200/404), DELETE(204/404)</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 6: CRUD operatsiyalar
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());

// pool — 5-darsdagi kabi ulangan deb faraz qilinadi (const pool = require('./db'))

// ─────────────────────────────────────────────────────────────────────
// 1) Create — POST, RETURNING *
// ─────────────────────────────────────────────────────────────────────

app.post('/products', async (req, res) => {
  try {
    const { nomi, narxi } = req.body;
    if (!nomi || typeof narxi !== 'number') {
      return res.status(400).json({ xato: "'nomi' va 'narxi' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO products (nomi, narxi) VALUES ($1, $2) RETURNING *',
      [nomi, narxi]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 2) Update — PUT, rowCount tekshirish
// ─────────────────────────────────────────────────────────────────────

app.put('/products/:id', async (req, res) => {
  try {
    const { nomi, narxi } = req.body;
    const result = await pool.query(
      'UPDATE products SET nomi = $1, narxi = $2 WHERE id = $3 RETURNING *',
      [nomi, narxi, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Mahsulot topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Delete — rowCount bilan 404 yoki 204
// ─────────────────────────────────────────────────────────────────────

app.delete('/products/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM products WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Mahsulot topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — rowCount tekshirilmagan (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
app.put('/products-xato/:id', async (req, res) => {
  const result = await pool.query(
    'UPDATE products SET nomi = $1 WHERE id = $2 RETURNING *',
    [req.body.nomi, req.params.id]
  );
  res.json(result.rows[0]); // ❌ id topilmasa — undefined, lekin status hali ham 200!
});
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L6_EX = [
    {
        "title": "RETURNING * nima uchun ishlatiladi?",
        "description": "INSERT so'rovida RETURNING * qo'shilishining sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "So'rovni tezlashtiradi",
            "Yangi yaratilgan qatorni bitta so'rovda qaytarish uchun",
            "Xatolarni avtomatik tuzatadi",
            "Faqat DELETE bilan ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Standart holda INSERT/UPDATE hech narsa qaytarmaydi.",
        "explanation": "RETURNING * — INSERT yoki UPDATE natijasida o'zgargan qatorni to'liq holda qaytaradi, shu tufayli alohida SELECT yozishga hojat qolmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "result.rowCount nimani bildiradi?",
        "description": "UPDATE yoki DELETE so'rovidan keyin result.rowCount qanday qiymatni ko'rsatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Jadvaldagi umumiy qatorlar soni",
            "So'rov qancha vaqt ishlaganini (millisekundlarda)",
            "Nechta qator o'zgartirilgani yoki o'chirilgani",
            "Xatolar sonini",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "0 qiymati — hech qanday qator mos kelmagani, demak topilmagan degani.",
        "explanation": "result.rowCount — UPDATE yoki DELETE ta'sir qilgan qatorlar sonini bildiradi. 0 bo'lsa, WHERE shartiga mos qator umuman topilmagan.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "PUT /products/:id oqimini to'g'ri tartibda joylang",
        "description": "Mavjud bo'lmagan id uchun PUT so'rovi kelganda bo'ladigan voqealarni tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "UPDATE ... WHERE id = $3 RETURNING * bajariladi",
            "PostgreSQL mos qator topa olmaydi",
            "result.rowCount === 0 bo'ladi",
            "Server 404 va xato xabari bilan javob beradi",
        ],
        "correct_order": [
            "UPDATE ... WHERE id = $3 RETURNING * bajariladi",
            "PostgreSQL mos qator topa olmaydi",
            "result.rowCount === 0 bo'ladi",
            "Server 404 va xato xabari bilan javob beradi",
        ],
        "hint": "SQL xato bermaydi — u shunchaki 0 ta qatorni o'zgartiradi, buni server o'zi tekshirishi kerak.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "rowCount tekshirilmasa nima muammo yuzaga keladi?",
        "description": (
            "PUT /products/:id route'ida rowCount tekshirilmasa va mavjud "
            "bo'lmagan id yuborilsa, klient qanday noto'g'ri natija oladi? "
            "Nega bu \"jim xato\" hisoblanadi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar rowCount tekshirilmasa, mavjud bo'lmagan id uchun ham "
            "server status 200 bilan javob qaytaradi, garchi result.rows[0] "
            "aslida undefined bo'lsa ham (chunki DB'da hech qanday qator "
            "topilmagan va o'zgartirilmagan). Klient buni \"yangilash "
            "muvaffaqiyatli bo'ldi\" deb noto'g'ri tushunishi mumkin, holbuki "
            "haqiqatda hech narsa o'zgarmagan. Bu jim xato hisoblanadi, "
            "chunki na server, na SQL hech qanday aniq xato xabari "
            "bermaydi — muammo faqat javob tanasi kutilganidan farq "
            "qilishida bilinadi, agar buni maxsus tekshirmasangiz."
        ),
        "hint": "SQL o'zi xato bermaydi — muammo faqat natijani tekshirmaslikda.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R2_TEXT = """\
<h2>R2 — 5-6-darslarni takrorlash: Notes REST API</h2>

<p>5-6 darslarni birlashtirib, PostgreSQL bilan to'liq ishlaydigan Notes (eslatmalar) REST API yasaymiz: DB ulanish, to'liq CRUD, va har bir operatsiyada natijani to'g'ri tekshirish.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>notes</code> jadvali: <code>id</code>, <code>sarlavha</code>, <code>matn</code>, <code>yaratilgan_vaqt</code></li>
<li><code>GET /notes</code> — hammasini olish, <code>GET /notes/:id</code> — bittasini olish</li>
<li><code>POST /notes</code> — yangi eslatma yaratish (validatsiya bilan)</li>
<li><code>PUT /notes/:id</code>, <code>DELETE /notes/:id</code> — <code>rowCount</code> orqali 404'ni to'g'ri aniqlash</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — GET route'lar</h4>
<p><code>GET /notes</code> — barcha eslatmalarni <code>ORDER BY id</code> bilan qaytaring. <code>GET /notes/:id</code> — bitta eslatma, topilmasa <code>404</code>.</p>

<h4>Vazifa 2 — POST bilan yaratish</h4>
<p><code>sarlavha</code> va <code>matn</code> majburiy (bo'sh bo'lmasligi kerak). <code>INSERT ... RETURNING *</code> orqali yangi eslatmani <code>201</code> bilan qaytaring.</p>

<h4>Vazifa 3 — PUT bilan yangilash</h4>
<p><code>UPDATE ... WHERE id = $X RETURNING *</code> — <code>result.rowCount === 0</code> bo'lsa <code>404</code>, aks holda yangilangan eslatmani qaytaring.</p>

<h4>Vazifa 4 — DELETE</h4>
<p><code>DELETE FROM notes WHERE id = $1</code> — <code>rowCount</code> tekshirib, <code>404</code> yoki <code>204</code> qaytaring.</p>

<h3>🐛 Ataylab qiyin: try/catch'ni har bir route'da unutmaslik</h3>
<p>Har bir yangi route qo'shganingizda <code>try/catch</code>ni ham qo'shishni unutmang — bu 5-6-darslarda alohida-alohida ko'rsatilgan, lekin ko'plab route bo'lganda ba'zilarida unutilib qolishi mumkin. <code>try/catch</code>siz DB xatosi butun serverni yiqitmaydi (Express buni tutadi), lekin klientga tushunarsiz "Internal Server Error" HTML sahifasi qaytadi — JSON o'rniga.</p>

<h3>Boshlang'ich kod</h3>
<pre><code>const express = require('express');
const app = express();
app.use(express.json());
const pool = require('./db'); // 5-darsdagi kabi

// Vazifa 1: GET /notes, GET /notes/:id
// Vazifa 2: POST /notes
// Vazifa 3: PUT /notes/:id
// Vazifa 4: DELETE /notes/:id

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>app.get('/notes', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM notes ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.get('/notes/:id', async (req, res) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.post('/notes', async (req, res) =&gt; {
  try {
    const { sarlavha, matn } = req.body;
    if (!sarlavha || !matn) {
      return res.status(400).json({ xato: "'sarlavha' va 'matn' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [sarlavha, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.put('/notes/:id', async (req, res) =&gt; {
  try {
    const { sarlavha, matn } = req.body;
    const result = await pool.query(
      'UPDATE notes SET sarlavha = $1, matn = $2 WHERE id = $3 RETURNING *',
      [sarlavha, matn, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.delete('/notes/:id', async (req, res) =&gt; {
  try {
    const result = await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 5-6 darslarning hammasi birga: DB ulanish, parametrlashtirilgan so'rovlar, to'liq CRUD</li>
<li>✅ Har bir route — o'z <code>try/catch</code>iga ega bo'lishi shart</li>
<li>✅ <code>rowCount</code> — <code>UPDATE</code>/<code>DELETE</code>da 404'ni aniqlashning yagona ishonchli usuli</li>
<li>✅ Kichik, aniq route'lar to'plami — real loyihalarning boshlang'ich nuqtasi</li>
</ul>
"""

R2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 2: Notes REST API (5-6-darslar)
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());
// const pool = require('./db'); // 5-darsdagi kabi

app.get('/notes', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM notes ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.get('/notes/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.post('/notes', async (req, res) => {
  try {
    const { sarlavha, matn } = req.body;
    if (!sarlavha || !matn) {
      return res.status(400).json({ xato: "'sarlavha' va 'matn' majburiy" });
    }
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [sarlavha, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.put('/notes/:id', async (req, res) => {
  try {
    const { sarlavha, matn } = req.body;
    const result = await pool.query(
      'UPDATE notes SET sarlavha = $1, matn = $2 WHERE id = $3 RETURNING *',
      [sarlavha, matn, req.params.id]
    );
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.delete('/notes/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
    if (result.rowCount === 0) {
      return res.status(404).json({ xato: 'Eslatma topilmadi' });
    }
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ xato: 'Server xatosi' });
  }
});

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

R2_EX = [
    {
        "title": "Nega har bir route try/catch'ga ega bo'lishi kerak?",
        "description": "Bir nechta DB route'i bo'lganda, har birida alohida try/catch yozishning sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni chiroyliroq ko'rsatish uchun",
            "DB xatosi yuz berganda serverni yiqitmaslik va klientga tushunarli JSON xato qaytarish uchun",
            "Faqat POST route'lariga kerak",
            "try/catch performance'ni yaxshilaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "try/catch bo'lmasa ham server yiqilmaydi, lekin klient nima oladi?",
        "explanation": "try/catch'siz ham Express DB xatosini tutadi va server yiqilmaydi, lekin klientga standart HTML xato sahifasi qaytishi mumkin — JSON emas. try/catch bilan esa tushunarli, izchil JSON xato qaytarish mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "DELETE /notes/:id qaysi holatda 404 qaytaradi?",
        "description": "DELETE /notes/:id route'i qanday holatda 404 qaytarishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim, DELETE muvaffaqiyatsiz bo'lgani uchun",
            "result.rowCount === 0 bo'lsa (bunday id topilmagan)",
            "Faqat id manfiy son bo'lsa",
            "Hech qachon, DELETE doim 204 qaytaradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "6-darsni eslang: rowCount 0 bo'lsa — hech narsa o'chirilmagan.",
        "explanation": "rowCount === 0 — bunday id bo'yicha jadvalda hech qanday qator topilmagani va o'chirilmaganini bildiradi, shuning uchun 404 qaytarish to'g'ri.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "POST /notes so'rovini to'g'ri tartibda joylang",
        "description": "Yangi eslatma yaratish so'rovi kelganidan javob qaytargunga qadar bo'lgan qadamlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "express.json() req.body ni tayyorlaydi",
            "sarlavha va matn mavjudligi tekshiriladi",
            "INSERT ... RETURNING * bajariladi",
            "201 status bilan yangi eslatma qaytariladi",
        ],
        "correct_order": [
            "express.json() req.body ni tayyorlaydi",
            "sarlavha va matn mavjudligi tekshiriladi",
            "INSERT ... RETURNING * bajariladi",
            "201 status bilan yangi eslatma qaytariladi",
        ],
        "hint": "Avval body tayyorlanadi, keyin tekshiriladi, keyin DB'ga yoziladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "5-6-darslarni birlashtirish nega muhim?",
        "description": (
            "Notes REST API'da DB ulanish (5-dars), parametrlashtirilgan "
            "so'rovlar, va rowCount orqali to'g'ri xato boshqarish (6-dars) "
            "birga qanday ishlaydi? Ulardan birortasi yetishmasa nima "
            "muammo yuzaga keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "DB ulanish (Pool) — barcha so'rovlar uchun asos bo'lib xizmat "
            "qiladi. Parametrlashtirilgan so'rovlar foydalanuvchidan kelgan "
            "ma'lumotni xavfsiz tarzda SQL'ga uzatadi, SQL Injection'ning "
            "oldini oladi. rowCount orqali tekshirish esa UPDATE/DELETE "
            "operatsiyalarining haqiqatan ham kutilgan qatorga ta'sir "
            "qilganini tasdiqlaydi. Agar shulardan birortasi yetishmasa — "
            "masalan rowCount tekshirilmasa — API xavfsiz ishlagan taassurot "
            "qoldiradi, lekin aslida noto'g'ri yoki chalg'ituvchi natijalar "
            "berishi mumkin, garchi SQL o'zi hech qanday xato bermasa ham."
        ),
        "hint": "Har bir qismning o'z vazifasi bor — ulardan birini olib tashlasangiz nima yo'qoladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L7_TEXT = """\
<h2>Validatsiya va xatolarni markazlashtirib boshqarish</h2>

<pre class="mermaid">
flowchart LR
    R["Route handler"] -->|next(err)| EH["Xato middleware (4 argument!)"]
    EH --> C["Bir xil shakldagi JSON javob"]
</pre>

<p>6-darsgacha har bir route'da o'z <code>try/catch</code>i va o'z <code>res.status(...).json({...})</code>i bor edi — bu takrorlanishga olib keladi. Express'da <strong>markazlashtirilgan xato middleware</strong> bor: barcha xatolarni bitta joyda, bir xil shaklda qayta ishlash imkonini beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — next(err) bilan xatoni uzatish</h4>
<pre><code>app.get('/users/:id', async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      const err = new Error('Foydalanuvchi topilmadi');
      err.status = 404;
      return next(err); // ❗ res.json() emas — next(err) orqali uzatamiz
    }
    res.json(result.rows[0]);
  } catch (err) {
    next(err); // ❗ kutilmagan xatolar ham next() orqali
  }
});</code></pre>

<h4>BLOKA 2 — markazlashtirilgan xato middleware (4 argument!)</h4>
<pre><code>// Bu middleware BARCHA route'lardan KEYIN, faylning oxirida yoziladi
app.use((err, req, res, next) =&gt; { // ❗ aynan 4 ta argument — Express buni shu orqali taniydi
  console.error(err.message);
  const status = err.status || 500;
  res.status(status).json({
    xato: {
      xabar: err.message || 'Server xatosi',
      status,
    },
  });
});</code></pre>

<h4>BLOKA 3 — validatsiya yordamchi funksiyasi</h4>
<pre><code>function validateNote(body) {
  const { sarlavha, matn } = body;
  if (!sarlavha || typeof sarlavha !== 'string') {
    const err = new Error("'sarlavha' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
  if (!matn || typeof matn !== 'string') {
    const err = new Error("'matn' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
}

app.post('/notes', async (req, res, next) =&gt; {
  try {
    validateNote(req.body); // xato bo'lsa throw qiladi, catch uni tutadi
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [req.body.sarlavha, req.body.matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h3>🐛 Ataylab xato — xato middleware'da 3 ta argument yozish</h3>
<pre><code>// ❌ faqat 3 ta argument — Express buni ODDIY middleware deb hisoblaydi, xato handler EMAS!
app.use((req, res, next) =&gt; {
  console.error('Xato yuz berdi');
  res.status(500).json({ xato: 'Server xatosi' });
});</code></pre>

<p><strong>Natija:</strong> Express xato-middleware'ni faqat <strong>aynan 4 ta argument</strong> (<code>err, req, res, next</code>) borligiga qarab aniqlaydi — bu qat'iy qoida, izoh yoki nom orqali emas. 3 argumentli versiya oddiy middleware sifatida qabul qilinadi va <code>next(err)</code> chaqirilganda umuman ishga tushmaydi. Natijada xato "tutilmay qoladi", va klientga Express'ning standart, JSON bo'lmagan xato sahifasi qaytadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. next(err) va next() farqi</h4>
<p><code>next()</code> — argumentsiz chaqirilsa, Express keyingi oddiy middleware/route'ga o'tadi. <code>next(err)</code> — argument bilan chaqirilsa, Express oddiy middleware'larni <strong>o'tkazib yuborib</strong>, to'g'ridan-to'g'ri xato-middleware'ga sakraydi.</p>

<h4>2. Nega xato middleware oxirida yoziladi?</h4>
<p>Express middleware'larni yozilish tartibida ishga tushiradi. Xato-middleware barcha route'lardan keyin yozilishi kerak — aks holda u hali ro'yxatdan o'tmagan route'lardagi xatolarni tuta olmaydi.</p>

<h4>3. Bir xil xato shakli — nega muhim?</h4>
<p>Agar har bir route o'zicha turlicha xato shaklini qaytarsa (ba'zisi <code>{xato: "..."}</code>, ba'zisi <code>{error: "..."}</code>), frontend har bir holatni alohida ishlashga majbur bo'ladi. Markazlashtirilgan middleware — barcha xatolar bir xil <code>{xato: {xabar, status}}</code> shaklida qaytishini kafolatlaydi.</p>

<h4>4. throw vs next(err) — qachon qaysi biri?</h4>
<p><code>async</code> funksiya ichida <code>throw</code> qilingan xato avtomatik <code>catch</code>ga tushadi, u yerdan <code>next(err)</code> bilan uzatiladi. Sinxron (oddiy) kodda <code>throw</code>dan foydalanish, keyin uni <code>try/catch</code> bilan tutib <code>next()</code>ga uzatish — standart naqsh.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Xato-middleware — aynan 4 argument (<code>err, req, res, next</code>) bilan aniqlanadi, boshqacha emas</li>
<li>✅ Xato-middleware har doim barcha route'lardan <strong>keyin</strong> yoziladi</li>
<li>✅ <code>next(err)</code> — oddiy middleware'larni o'tkazib, to'g'ridan-to'g'ri xato-handler'ga o'tkazadi</li>
<li>✅ Markazlashtirilgan xato boshqaruvi — barcha xatolar bir xil JSON shaklida qaytishini ta'minlaydi</li>
<li>✅ 3 argumentli xato-middleware — Express uni oddiy middleware deb hisoblaydi, hech qachon ishga tushmaydi</li>
</ul>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 7: Validatsiya va xatolarni markazlashtirib boshqarish
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const app = express();
app.use(express.json());
// const pool = require('./db');

// ─────────────────────────────────────────────────────────────────────
// 1) Validatsiya yordamchisi
// ─────────────────────────────────────────────────────────────────────

function validateNote(body) {
  const { sarlavha, matn } = body;
  if (!sarlavha || typeof sarlavha !== 'string') {
    const err = new Error("'sarlavha' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
  if (!matn || typeof matn !== 'string') {
    const err = new Error("'matn' majburiy va matn bo'lishi kerak");
    err.status = 400;
    throw err;
  }
}

// ─────────────────────────────────────────────────────────────────────
// 2) Route'lar — next(err) orqali xatolarni uzatadi
// ─────────────────────────────────────────────────────────────────────

app.get('/notes/:id', async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM notes WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      const err = new Error('Eslatma topilmadi');
      err.status = 404;
      return next(err);
    }
    res.json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

app.post('/notes', async (req, res, next) => {
  try {
    validateNote(req.body);
    const result = await pool.query(
      'INSERT INTO notes (sarlavha, matn) VALUES ($1, $2) RETURNING *',
      [req.body.sarlavha, req.body.matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Markazlashtirilgan xato middleware — BARCHA route'lardan KEYIN
// ─────────────────────────────────────────────────────────────────────

app.use((err, req, res, next) => { // 4 argument — Express buni shu orqali taniydi
  console.error(err.message);
  const status = err.status || 500;
  res.status(status).json({
    xato: {
      xabar: err.message || 'Server xatosi',
      status,
    },
  });
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — 3 argumentli "xato" middleware (izohda, ishlamaydi)
// ─────────────────────────────────────────────────────────────────────

/*
app.use((req, res, next) => { // ❌ 3 argument — Express buni ODDIY middleware deb biladi
  console.error('Xato yuz berdi');
  res.status(500).json({ xato: 'Server xatosi' });
});
*/

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L7_EX = [
    {
        "title": "Xato middleware qanday aniqlanadi?",
        "description": "Express bir middleware funksiyasini \"xato middleware\" deb qanday aniqlaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Funksiya nomi 'errorHandler' bo'lsa",
            "Funksiya aynan 4 ta argumentga ega bo'lsa: (err, req, res, next)",
            "Funksiya fayl oxirida yozilgan bo'lsa",
            "Funksiya try/catch ichida chaqirilsa",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu qat'iy qoida — argumentlar soniga qarab aniqlanadi, nomga emas.",
        "explanation": "Express xato-middleware'ni faqat argumentlar sonidan (aynan 4 ta: err, req, res, next) aniqlaydi. Boshqa har qanday son (masalan 3 ta) bo'lsa, u oddiy middleware sifatida qabul qilinadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "next(err) chaqirilganda nima bo'ladi?",
        "description": "Route handler ichida next(err) chaqirilganda Express nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Keyingi oddiy middleware'ga o'tadi",
            "Oddiy middleware'larni o'tkazib, to'g'ridan-to'g'ri xato-middleware'ga o'tadi",
            "So'rovni qayta boshidan boshlaydi",
            "Serverni to'xtatadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "next() va next(err) turlicha yo'nalishga yuboradi.",
        "explanation": "next()ga argument berilsa, Express barcha oddiy middleware/route'larni o'tkazib yuborib, to'g'ridan-to'g'ri xato-middleware'ga (4 argumentli) sakraydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Xato oqimini to'g'ri tartibda joylang",
        "description": "POST /notes'da validatsiya xatosi yuz berganda bo'ladigan voqealarni tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "validateNote(req.body) chaqiriladi va throw qiladi",
            "catch bloki xatoni ushlaydi",
            "next(err) chaqiriladi",
            "4-argumentli xato middleware ishga tushadi",
            "Bir xil shakldagi JSON xato javobi qaytariladi",
        ],
        "correct_order": [
            "validateNote(req.body) chaqiriladi va throw qiladi",
            "catch bloki xatoni ushlaydi",
            "next(err) chaqiriladi",
            "4-argumentli xato middleware ishga tushadi",
            "Bir xil shakldagi JSON xato javobi qaytariladi",
        ],
        "hint": "throw -> catch -> next(err) -> markazlashtirilgan handler.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "3 argumentli xato middleware nega ishlamaydi?",
        "description": (
            "Agar markazlashtirilgan xato middleware (err, req, res, next) "
            "o'rniga xato qilib (req, res, next) — 3 argument bilan "
            "yozilsa, next(err) chaqirilganda nima bo'ladi va nega bu xato "
            "sodir bo'ladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Express middleware funksiyasining xato-handler ekanligini "
            "faqat uning argumentlar soniga (aynan 4 ta: err, req, res, "
            "next) qarab aniqlaydi. Agar middleware faqat 3 ta argument "
            "bilan yozilgan bo'lsa, Express uni oddiy middleware deb "
            "hisoblaydi, xato-handler sifatida emas. next(err) chaqirilganda "
            "Express xato-middleware'larni izlaydi, lekin bu funksiya "
            "argumentlar soniga ko'ra bunday deb tan olinmagani uchun u "
            "hech qachon ishga tushmaydi va xato \"tutilmay qoladi\" — "
            "natijada klientga Express'ning standart, JSON bo'lmagan xato "
            "sahifasi qaytadi."
        ),
        "hint": "Express xato-middleware'ni nom yoki joylashuv orqali emas, balki qanday belgisi orqali aniqlaydi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L8_TEXT = """\
<h2>JWT autentifikatsiya — ro'yxatdan o'tish va kirish</h2>

<pre class="mermaid">
flowchart LR
    R["POST /register"] -->|bcrypt.hash| DB[("users jadvali")]
    L["POST /login"] -->|bcrypt.compare| DB
    L -->|to'g'ri bo'lsa| JWT["jwt.sign() — token yaratish"]
    JWT --> C["Klientga token qaytariladi"]
</pre>

<p>Hozirgacha barcha route'lar "hamma uchun ochiq" edi. Endi — foydalanuvchini <strong>tanib olish</strong>ni o'rganamiz: parolni xavfsiz saqlash (<code>bcrypt</code>) va kirganini tasdiqlovchi token berish (<code>JWT</code>).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ro'yxatdan o'tish: parolni hash qilish</h4>
<pre><code>// Terminal:
npm install bcrypt jsonwebtoken</code></pre>

<pre><code>const bcrypt = require('bcrypt');

app.post('/register', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) {
      const err = new Error("'email' va 'parol' majburiy");
      err.status = 400;
      throw err;
    }
    const hash = await bcrypt.hash(parol, 10); // ❗ 10 — "salt rounds", xavfsizlik darajasi
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>BLOKA 2 — kirish: parolni tekshirish va JWT berish</h4>
<pre><code>const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET; // ❗ hech qachon kodga yozilmaydi, .env'dan olinadi

app.post('/login', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const err = new Error("Email yoki parol noto'g'ri");
      err.status = 401;
      throw err;
    }
    const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>BLOKA 3 — tokenni tekshirish</h4>
<pre><code>app.get('/profile', (req, res, next) =&gt; {
  const authHeader = req.headers.authorization; // "Bearer eyJhbGci..."
  const token = authHeader &amp;&amp; authHeader.split(' ')[1];
  if (!token) {
    const err = new Error('Token yo\\'q'); err.status = 401; return next(err);
  }
  try {
    const payload = jwt.verify(token, SECRET); // xato bo'lsa — throw qiladi
    res.json({ userId: payload.userId });
  } catch {
    const err = new Error('Token noto\\'g\\'ri yoki muddati o\\'tgan');
    err.status = 401;
    next(err);
  }
});</code></pre>

<h3>🐛 Ataylab xato — parolni oddiy matn holida saqlash</h3>
<pre><code>// ❌ JUDA XAVFLI — parol hash qilinmagan!
app.post('/register-xato', async (req, res) =&gt; {
  const { email, parol } = req.body;
  await pool.query(
    'INSERT INTO users (email, parol_hash) VALUES ($1, $2)',
    [email, parol] // ❌ parol o'zi — hash emas!
  );
  res.status(201).json({ email });
});

// login'da solishtirish:
// if (parol === user.parol_hash) { ... } // ❌ oddiy taqqoslash</code></pre>

<p><strong>Natija:</strong> agar DB birov tomonidan ko'rilsa yoki sizib chiqsa (data breach) — barcha foydalanuvchilarning haqiqiy parollari ochiq matnda ko'rinadi. Bu — eng jiddiy xavfsizlik xatolaridan biri. <code>bcrypt.hash()</code> parolni <strong>qaytarib bo'lmaydigan</strong> shaklga aylantiradi; login vaqtida esa <code>bcrypt.compare()</code> kiritilgan parolni hash bilan xavfsiz solishtiradi, hech qachon <code>===</code> orqali emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega parolni to'g'ridan-to'g'ri saqlab bo'lmaydi?</h4>
<p>Ma'lumotlar bazasi qandaydir tarzda sizib chiqsa (hacking, xato konfiguratsiya), oddiy matndagi parollar darhol barcha foydalanuvchilarning boshqa xizmatlardagi (email, bank) hisoblarini ham xavf ostiga qo'yadi — chunki odamlar ko'pincha bir xil parolni qayta ishlatadi.</p>

<h4>2. bcrypt.hash() va bcrypt.compare()</h4>
<p><code>bcrypt.hash(parol, 10)</code> — parolni bir tomonlama (qaytarib bo'lmaydigan) shifrlangan matnga aylantiradi. Kirishda parolni qayta hash qilib solishtirish shart emas — <code>bcrypt.compare(kiritilganParol, saqlanganHash)</code> buni xavfsiz bajaradi.</p>

<h4>3. JWT nima va nima uchun kerak?</h4>
<p>JWT (JSON Web Token) — foydalanuvchi kim ekanini tasdiqlovchi, serverda saqlanmaydigan (stateless) token. Login muvaffaqiyatli bo'lganda beriladi, keyingi so'rovlarda <code>Authorization: Bearer &lt;token&gt;</code> header orqali yuboriladi.</p>

<h4>4. process.env.JWT_SECRET — nega .env'da?</h4>
<p>JWT'ni imzolash uchun ishlatiladigan maxfiy kalit hech qachon kodga yozilmaydi — u bilinsa, har kim o'zi uchun soxta token yasashi mumkin. <code>.env</code> fayli orqali saqlanadi (keyingi darsda chuqurroq ko'riladi).</p>

<h4>5. jwt.verify() nima qiladi?</h4>
<p>Token imzosini tekshiradi va muddati o'tmaganini tasdiqlaydi. Token soxta yoki muddati o'tgan bo'lsa — xato tashlaydi (<code>throw</code>), shuning uchun uni <code>try/catch</code> ichida chaqirish shart.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Parollarni <strong>hech qachon</strong> ochiq matnda saqlamang — doim <code>bcrypt.hash()</code> orqali</li>
<li>✅ Login'da <code>bcrypt.compare()</code> ishlatiladi, <code>===</code> emas</li>
<li>✅ <code>jwt.sign()</code> — muvaffaqiyatli login'dan keyin token yaratadi</li>
<li>✅ <code>jwt.verify()</code> — tokenni tekshiradi, xato bo'lsa throw qiladi</li>
<li>✅ Maxfiy kalitlar (JWT_SECRET) hech qachon kodga yozilmaydi</li>
</ul>
"""

L8_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 8: JWT autentifikatsiya
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
// const pool = require('./db');

const SECRET = process.env.JWT_SECRET;

// ─────────────────────────────────────────────────────────────────────
// 1) Ro'yxatdan o'tish — parolni hash qilib saqlash
// ─────────────────────────────────────────────────────────────────────

app.post('/register', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) {
      const err = new Error("'email' va 'parol' majburiy");
      err.status = 400;
      throw err;
    }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 2) Kirish — bcrypt.compare + JWT berish
// ─────────────────────────────────────────────────────────────────────

app.post('/login', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const err = new Error("Email yoki parol noto'g'ri");
      err.status = 401;
      throw err;
    }
    const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 3) Tokenni tekshirish
// ─────────────────────────────────────────────────────────────────────

app.get('/profile', (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) {
    const err = new Error("Token yo'q");
    err.status = 401;
    return next(err);
  }
  try {
    const payload = jwt.verify(token, SECRET);
    res.json({ userId: payload.userId });
  } catch {
    const err = new Error("Token noto'g'ri yoki muddati o'tgan");
    err.status = 401;
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato — parolni oddiy matnda saqlash (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
app.post('/register-xato', async (req, res) => {
  const { email, parol } = req.body;
  await pool.query(
    'INSERT INTO users (email, parol_hash) VALUES ($1, $2)',
    [email, parol] // ❌ parol o'zi — hash emas!
  );
  res.status(201).json({ email });
});
*/

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L8_EX = [
    {
        "title": "bcrypt.hash() nima uchun ishlatiladi?",
        "description": "Ro'yxatdan o'tishda bcrypt.hash(parol, 10) nima uchun chaqiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Parolni tezroq tekshirish uchun",
            "Parolni qaytarib bo'lmaydigan shifrlangan shaklga aylantirib, xavfsiz saqlash uchun",
            "Parolni boshqa foydalanuvchilarga ko'rsatish uchun",
            "Email manzilini tasdiqlash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Maqsad — DB sizib chiqsa ham, haqiqiy parol ochilmasligi.",
        "explanation": "bcrypt.hash() parolni bir tomonlama (qaytarib bo'lmaydigan) hash shakliga aylantiradi. DB sizib chiqqan taqdirda ham haqiqiy parollar ochiq qolmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Login'da parolni qanday solishtirish kerak?",
        "description": "Login route'ida kiritilgan parolni saqlangan hash bilan qanday solishtirish to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": [
            "parol === user.parol_hash",
            "bcrypt.compare(parol, user.parol_hash)",
            "JSON.stringify(parol) === user.parol_hash",
            "Solishtirish shart emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Hash — qaytarib bo'lmaydi, shuning uchun oddiy === ishlamaydi.",
        "explanation": "bcrypt.compare() kiritilgan parolni qayta hash qilib, saqlangan hash bilan xavfsiz solishtiradi. Oddiy === bilan solishtirish mumkin emas, chunki hash har safar tasodifiy 'salt' bilan yaratiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Login oqimini to'g'ri tartibda joylang",
        "description": "Foydalanuvchi login qilganidan token olguncha bo'lgan qadamlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "email bo'yicha foydalanuvchi DB'dan qidiriladi",
            "bcrypt.compare() kiritilgan parolni hash bilan solishtiradi",
            "Mos kelsa — jwt.sign() token yaratadi",
            "Token klientga JSON javobda qaytariladi",
        ],
        "correct_order": [
            "email bo'yicha foydalanuvchi DB'dan qidiriladi",
            "bcrypt.compare() kiritilgan parolni hash bilan solishtiradi",
            "Mos kelsa — jwt.sign() token yaratadi",
            "Token klientga JSON javobda qaytariladi",
        ],
        "hint": "Avval foydalanuvchi topiladi, keyin parol tekshiriladi, keyin token yaratiladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Parolni oddiy matnda saqlash nega xavfli?",
        "description": (
            "Agar ro'yxatdan o'tishda parol bcrypt orqali hash qilinmasdan "
            "to'g'ridan-to'g'ri DB'ga yozilsa, bu nima uchun jiddiy "
            "xavfsizlik muammosi hisoblanadi? Buning oldini bcrypt qanday "
            "oladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar parol oddiy matnda saqlansa, ma'lumotlar bazasiga kirish "
            "huquqiga ega bo'lgan har qanday shaxs (xaker, xato "
            "konfiguratsiya, ichki suiiste'mol) barcha foydalanuvchilarning "
            "haqiqiy parollarini to'g'ridan-to'g'ri ko'ra oladi. Ko'p odamlar "
            "bir xil parolni turli xizmatlarda (email, bank) qayta "
            "ishlatgani uchun, bu faqat shu tizimni emas, balki "
            "foydalanuvchining boshqa hisoblarini ham xavf ostiga qo'yadi. "
            "bcrypt.hash() parolni bir tomonlama, qaytarib bo'lmaydigan "
            "shaklga aylantiradi — hatto hash DB'dan olingan taqdirda ham, "
            "undan asl parolni to'g'ridan-to'g'ri tiklab bo'lmaydi."
        ),
        "hint": "DB sizib chiqqan holatni tasavvur qiling — parol qandayligiga qarab nima farq qiladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L9_TEXT = """\
<h2>Protected routes — himoyalangan route'lar va middleware zanjiri</h2>

<pre class="mermaid">
flowchart LR
    Req["So'rov"] --> Auth["authMiddleware — tokenni tekshiradi"]
    Auth -->|to'g'ri| Handler["Route handler — req.user mavjud"]
    Auth -->|noto'g'ri| Err["401 — next(err)"]
</pre>

<p>8-darsda tokenni bitta route ichida tekshirishni ko'rdik. Lekin ko'plab route'ni himoyalash kerak bo'lsa, tekshiruv kodini har birida takrorlash noqulay. Bu darsda — <strong>qayta ishlatiladigan auth middleware</strong> yasaymiz va uni faqat kerakli route'larga qo'llaymiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — middleware/auth.js: qayta ishlatiladigan middleware</h4>
<pre><code>// middleware/auth.js
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader &amp;&amp; authHeader.split(' ')[1];
  if (!token) {
    const err = new Error('Token yo\\'q'); err.status = 401; return next(err);
  }
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.userId }; // ❗ keyingi handler'lar req.user'dan foydalanadi
    next();
  } catch {
    const err = new Error('Token noto\\'g\\'ri yoki muddati o\\'tgan');
    err.status = 401;
    next(err);
  }
}

module.exports = authMiddleware;</code></pre>

<h4>BLOKA 2 — faqat kerakli route'larga qo'llash</h4>
<pre><code>const authMiddleware = require('./middleware/auth');

app.get('/public-info', (req, res) =&gt; {
  res.json({ xabar: 'Bu ochiq route — hamma ko\\'ra oladi' });
});

app.get('/profile', authMiddleware, (req, res) =&gt; { // ❗ faqat shu route himoyalangan
  res.json({ userId: req.user.id, xabar: 'Bu maxfiy ma\\'lumot' });
});

app.get('/my-orders', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM orders WHERE user_id = $1', [req.user.id]);
    res.json(result.rows);
  } catch (err) {
    next(err);
  }
});</code></pre>

<h4>BLOKA 3 — rol asosida tekshirish (role-based)</h4>
<pre><code>function requireAdmin(req, res, next) {
  if (req.user.role !== 'admin') { // ❗ authMiddleware'dan KEYIN ishlatiladi, req.user allaqachon bor
    const err = new Error('Bu amal uchun admin huquqi kerak');
    err.status = 403;
    return next(err);
  }
  next();
}

app.delete('/users/:id', authMiddleware, requireAdmin, async (req, res, next) =&gt; {
  // Bu yergacha yetib kelgan bo'lsa — token to'g'ri VA foydalanuvchi admin
  // ...
});</code></pre>

<h3>🐛 Ataylab xato — authMiddleware'ni GLOBAL qo'yish</h3>
<pre><code>// ❌ XATO — barcha route'larga, hattoki login/register'ga ham ta'sir qiladi!
app.use(authMiddleware); // ❌ shu yerda, barcha route'lardan OLDIN

app.post('/register', ...);  // endi bu ham token talab qiladi!
app.post('/login', ...);     // bu ham! Lekin foydalanuvchi hali tokenga ega EMAS!</code></pre>

<p><strong>Natija:</strong> <code>authMiddleware</code>ni <code>app.use()</code> orqali global qo'llasangiz, u <strong>barcha</strong> keyingi route'larga, jumladan <code>/login</code> va <code>/register</code>ga ham ta'sir qiladi. Lekin foydalanuvchi login qilishdan oldin tabiiyki hali tokenga ega emas — natijada hech kim tizimga kira olmaydi, chunki kirish uchun token kerak, token olish uchun esa kirish kerak: yopiq halqa (aylanma tuzoq). Yechim — <code>authMiddleware</code>ni faqat himoyalanishi kerak bo'lgan route'larga alohida-alohida qo'shish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Route-darajasidagi middleware</h4>
<pre><code>app.get('/yol', middleware1, middleware2, handler);
// middleware'lar handler'dan oldin, chapdan o'ngga tartibda ishga tushadi</code></pre>
<p><code>app.get(yo'l, middleware, handler)</code> — middleware faqat shu bitta route uchun ishlaydi, boshqalariga ta'sir qilmaydi. Bir nechta middleware vergul bilan zanjir qilib yozilishi mumkin.</p>

<h4>2. req.user — nega shunday nom bilan saqlanadi?</h4>
<p><code>authMiddleware</code> tokenni tekshirib, foydalanuvchi ma'lumotini <code>req</code> obyektiga <code>req.user</code> sifatida qo'shadi. Shundan keyin zanjirdagi <strong>keyingi</strong> middleware yoki handler bu ma'lumotdan foydalana oladi — chunki <code>req</code> bitta so'rov davomida barcha middleware'lar orasida umumiy.</p>

<h4>3. Nega ochiq va yopiq route'larni aralashtirmaslik kerak?</h4>
<p>Har bir route o'zi qanday himoyalanishi (yoki himoyalanmasligi) kerakligini aniq ko'rsatishi kerak. Global <code>app.use(authMiddleware)</code> — "hamma narsa himoyalangan" degani, bu esa login/register kabi tabiiy ravishda ochiq bo'lishi kerak bo'lgan route'larni ham to'sib qo'yadi.</p>

<h4>4. Middleware zanjiri — bir nechta tekshiruv</h4>
<p><code>authMiddleware, requireAdmin</code> — ikkalasi ham <code>next()</code> chaqirganda keyingisiga o'tadi. Agar <code>authMiddleware</code> token noto'g'ri deb topsa, <code>next(err)</code> chaqiradi va <code>requireAdmin</code> hech qachon ishga tushmaydi — bu to'g'ri xatti-harakat.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Auth middleware'ni alohida faylga chiqarish — takrorlanishning oldini oladi</li>
<li>✅ Middleware faqat kerakli route'larga <code>app.get(yo'l, middleware, handler)</code> orqali qo'llanadi</li>
<li>✅ <code>authMiddleware</code>ni global (<code>app.use</code>) qo'yish — login/register'ni ham to'sib, aylanma tuzoq yaratadi</li>
<li>✅ <code>req.user</code> — middleware orqali qo'shilib, keyingi handler'larga uzatiladigan ma'lumot</li>
<li>✅ Middleware'lar zanjiri — har biri o'z tekshiruvini bajarib, keyingisiga <code>next()</code> bilan o'tkazadi</li>
</ul>
"""

L9_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 9: Protected routes va middleware zanjiri
// ════════════════════════════════════════════════════════════════════

// ─── middleware/auth.js ───
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) {
    const err = new Error("Token yo'q");
    err.status = 401;
    return next(err);
  }
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.userId };
    next();
  } catch {
    const err = new Error("Token noto'g'ri yoki muddati o'tgan");
    err.status = 401;
    next(err);
  }
}

function requireAdmin(req, res, next) {
  if (req.user.role !== 'admin') {
    const err = new Error("Bu amal uchun admin huquqi kerak");
    err.status = 403;
    return next(err);
  }
  next();
}

// module.exports = { authMiddleware, requireAdmin };

// ─── server.js ───
const express = require('express');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// Ochiq route'lar — himoyasiz
// ─────────────────────────────────────────────────────────────────────

app.post('/register', async (req, res) => { /* 8-darsdagidek */ });
app.post('/login', async (req, res) => { /* 8-darsdagidek */ });

app.get('/public-info', (req, res) => {
  res.json({ xabar: "Bu ochiq route — hamma ko'ra oladi" });
});

// ─────────────────────────────────────────────────────────────────────
// Himoyalangan route'lar — faqat shu yerlarga middleware qo'shiladi
// ─────────────────────────────────────────────────────────────────────

app.get('/profile', authMiddleware, (req, res) => {
  res.json({ userId: req.user.id, xabar: "Bu maxfiy ma'lumot" });
});

app.get('/my-orders', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM orders WHERE user_id = $1', [req.user.id]);
    res.json(result.rows);
  } catch (err) {
    next(err);
  }
});

app.delete('/users/:id', authMiddleware, requireAdmin, async (req, res, next) => {
  try {
    await pool.query('DELETE FROM users WHERE id = $1', [req.params.id]);
    res.status(204).send();
  } catch (err) {
    next(err);
  }
});

// ─────────────────────────────────────────────────────────────────────
// Ataylab xato — authMiddleware'ni global qo'yish (izohda, ishlatilmaydi)
// ─────────────────────────────────────────────────────────────────────

/*
app.use(authMiddleware); // ❌ BARCHA route'larga, /login va /register'ga ham ta'sir qiladi!
// Natija: login qilish uchun token kerak, token olish uchun login kerak — aylanma tuzoq.
*/

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

L9_EX = [
    {
        "title": "Middleware faqat bitta route'ga qanday qo'llanadi?",
        "description": "authMiddleware'ni faqat /profile route'iga (boshqalariga emas) qo'llash uchun to'g'ri usul qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "app.use(authMiddleware) — faylning istalgan joyida",
            "app.get('/profile', authMiddleware, handler)",
            "authMiddleware'ni handler ichida qo'lda chaqirish",
            "Middleware'ni faqat bitta route'ga qo'llab bo'lmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "app.get(yo'l, middleware, handler) — middleware faqat shu route uchun ishlaydi.",
        "explanation": "app.get(yo'l, middleware, handler) yozuvida middleware faqat shu bitta route'ga tegishli bo'ladi va boshqa route'larga ta'sir qilmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "req.user qayerdan paydo bo'ladi?",
        "description": "Route handler ichida req.user qanday qilib mavjud bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Express uni avtomatik yaratadi",
            "authMiddleware token tekshirilgandan keyin uni req obyektiga qo'shadi",
            "Ma'lumotlar bazasi avtomatik yuboradi",
            "Klient uni so'rov headerida yuboradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "req — so'rov davomida barcha middleware'lar orasida umumiy obyekt.",
        "explanation": "authMiddleware tokenni tekshirib, muvaffaqiyatli bo'lsa req.user = {...} qo'shadi. Keyingi middleware/handler'lar shu req obyektidan foydalanib, req.user'ga kira oladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "DELETE /users/:id (admin-only) oqimini to'g'ri tartibda joylang",
        "description": "authMiddleware va requireAdmin ikkalasi bilan himoyalangan route'ga so'rov kelganda bo'ladigan tekshiruvlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "authMiddleware token mavjudligini va to'g'riligini tekshiradi",
            "req.user o'rnatiladi, next() chaqiriladi",
            "requireAdmin req.user.role ni tekshiradi",
            "Ikkalasi ham o'tsa — asosiy handler ishga tushadi",
        ],
        "correct_order": [
            "authMiddleware token mavjudligini va to'g'riligini tekshiradi",
            "req.user o'rnatiladi, next() chaqiriladi",
            "requireAdmin req.user.role ni tekshiradi",
            "Ikkalasi ham o'tsa — asosiy handler ishga tushadi",
        ],
        "hint": "Middleware'lar app.get() ichida yozilgan tartibda, chapdan o'ngga ishga tushadi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "authMiddleware'ni global qo'yish nega muammo?",
        "description": (
            "Agar authMiddleware app.use(authMiddleware) orqali BARCHA "
            "route'larga (jumladan /login va /register'ga ham) qo'llansa, "
            "bu qanday muammoga olib keladi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "app.use(authMiddleware) — barcha keyingi route'larga, jumladan "
            "/login va /register'ga ham ta'sir qiladi, chunki Express "
            "middleware'larni yozilgan tartibda barcha so'rovlarga qo'llaydi. "
            "Lekin foydalanuvchi hali tizimga kirmagan bo'lsa, u tabiiy "
            "ravishda hali hech qanday tokenga ega emas. Natijada login "
            "qilish uchun token talab qilinadi, token esa faqat muvaffaqiyatli "
            "login orqali olinadi — bu aylanma tuzoq bo'lib, hech kim "
            "tizimga kira olmay qoladi. Yechim — authMiddleware'ni faqat "
            "haqiqatan himoyalanishi kerak bo'lgan route'larga alohida-"
            "alohida, route darajasida qo'shish."
        ),
        "hint": "Login qilishdan oldin foydalanuvchida token bormi yoki yo'qmi, o'ylab ko'ring.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R3_TEXT = """\
<h2>R3 — 5-9-darslarni takrorlash: Auth + CRUD to'liq loyiha</h2>

<p>5-9 darslarning hammasini birlashtirib, har bir foydalanuvchi <strong>faqat o'z</strong> vazifalarini (tasks) ko'ra oladigan, to'liq autentifikatsiyalangan REST API yasaymiz.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>POST /register</code>, <code>POST /login</code> — bcrypt + JWT (8-dars)</li>
<li><code>authMiddleware</code> — <code>/tasks</code> ostidagi barcha route'larni himoyalash (9-dars)</li>
<li>To'liq CRUD: <code>GET/POST/PUT/DELETE /tasks</code> — <strong>faqat</strong> <code>req.user.id</code>ga tegishli qatorlar (5-6-darslar)</li>
<li>Markazlashtirilgan xato middleware (7-dars)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — register/login</h4>
<p><code>users</code> jadvali: <code>id</code>, <code>email</code>, <code>parol_hash</code>. Ro'yxatdan o'tishda <code>bcrypt.hash</code>, kirishda <code>bcrypt.compare</code> + <code>jwt.sign</code>.</p>

<h4>Vazifa 2 — authMiddleware bilan himoyalash</h4>
<p><code>/tasks</code> bilan bog'liq barcha route'larga <code>authMiddleware</code>ni qo'shing, u <code>req.user = { id: ... }</code>ni o'rnatadi.</p>

<h4>Vazifa 3 — foydalanuvchiga tegishli CRUD</h4>
<p><code>tasks</code> jadvali: <code>id</code>, <code>user_id</code>, <code>matn</code>, <code>bajarildi</code>. Har bir so'rovda <strong>albatta</strong> <code>WHERE user_id = $X</code> shartini qo'shing — aks holda foydalanuvchi boshqasining vazifalarini ko'rishi yoki o'chirishi mumkin.</p>

<h4>Vazifa 4 — markazlashtirilgan xato boshqaruvi</h4>
<p>Barcha xatolarni <code>next(err)</code> orqali uzating, bitta joyda ushlab, bir xil JSON shaklida qaytaring.</p>

<h3>🐛 Ataylab qiyin: WHERE user_id shartini unutish (IDOR zaifligi)</h3>
<pre><code>// ❌ XAVFLI — user_id tekshirilmagan!
app.get('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE id = $1', [req.params.id]);
    // ❌ WHERE'da faqat id bor, user_id yo'q!
    if (result.rows.length === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

// Foydalanuvchi A o'zi tizimga kirgan, lekin /tasks/57 (boshqa
// foydalanuvchi B'ning vazifasi) ID'sini taxmin qilib yuborsa —
// token to'g'ri bo'lgani uchun so'rov o'tadi, va B'ning MAXFIY
// vazifasi A'ga qaytariladi!</code></pre>

<p><strong>Natija:</strong> bu — <strong>IDOR</strong> (Insecure Direct Object Reference) deb ataladigan xavfsizlik zaifligi. Token to'g'ri bo'lishi kifoya emas — <strong>har bir so'rov o'zi so'ragan ma'lumot haqiqatan shu foydalanuvchiga tegishli ekanini</strong> tekshirishi shart. To'g'ri versiya: <code>WHERE id = $1 AND user_id = $2</code> — <code>[req.params.id, req.user.id]</code> bilan.</p>

<h3>Boshlang'ich kod</h3>
<pre><code>const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());
// const pool = require('./db');
// const authMiddleware = require('./middleware/auth');

// Vazifa 1: POST /register, POST /login

// Vazifa 2-3: /tasks route'lari, authMiddleware bilan, HAR DOIM
// WHERE user_id = $X bilan

// Vazifa 4: markazlashtirilgan xato middleware (fayl oxirida)

app.listen(3000, () =&gt; {
  console.log('Server ishga tushdi: http://localhost:3000');
});</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>app.post('/register', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) { const e = new Error("'email' va 'parol' majburiy"); e.status = 400; throw e; }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.post('/login', async (req, res, next) =&gt; {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const e = new Error("Email yoki parol noto'g'ri"); e.status = 401; throw e;
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) { next(err); }
});

app.get('/tasks', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE user_id = $1 ORDER BY id', [req.user.id]);
    res.json(result.rows);
  } catch (err) { next(err); }
});

app.post('/tasks', authMiddleware, async (req, res, next) =&gt; {
  try {
    const { matn } = req.body;
    if (!matn) { const e = new Error("'matn' majburiy"); e.status = 400; throw e; }
    const result = await pool.query(
      'INSERT INTO tasks (user_id, matn, bajarildi) VALUES ($1, $2, false) RETURNING *',
      [req.user.id, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.put('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query(
      'UPDATE tasks SET bajarildi = NOT bajarildi WHERE id = $1 AND user_id = $2 RETURNING *',
      [req.params.id, req.user.id] // ❗ ikkalasi ham — boshqasining vazifasini o'zgartirib bo'lmaydi
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

app.delete('/tasks/:id', authMiddleware, async (req, res, next) =&gt; {
  try {
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.status(204).send();
  } catch (err) { next(err); }
});

app.use((err, req, res, next) =&gt; {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 5-9 darslarning hammasi birga: DB, CRUD, validatsiya, xato boshqaruvi, JWT, protected routes</li>
<li>✅ Token to'g'riligi — ma'lumotga ega bo'lish huquqini kafolatlamaydi, har bir so'rov <code>user_id</code>ni ham tekshirishi shart</li>
<li>✅ IDOR — eng ko'p uchraydigan, lekin oson oldini olinadigan xavfsizlik zaifliklaridan biri</li>
<li>✅ <code>WHERE id = $1 AND user_id = $2</code> — foydalanuvchiga tegishli CRUD'ning standart naqshi</li>
</ul>
"""

R3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// REVISION 3: Auth + CRUD to'liq loyiha (5-9-darslar)
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());
// const pool = require('./db');
// const authMiddleware = require('./middleware/auth'); // 9-darsdagidek

app.post('/register', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    if (!email || !parol) { const e = new Error("'email' va 'parol' majburiy"); e.status = 400; throw e; }
    const hash = await bcrypt.hash(parol, 10);
    const result = await pool.query(
      'INSERT INTO users (email, parol_hash) VALUES ($1, $2) RETURNING id, email',
      [email, hash]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.post('/login', async (req, res, next) => {
  try {
    const { email, parol } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = result.rows[0];
    if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
      const e = new Error("Email yoki parol noto'g'ri"); e.status = 401; throw e;
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } catch (err) { next(err); }
});

app.get('/tasks', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM tasks WHERE user_id = $1 ORDER BY id', [req.user.id]);
    res.json(result.rows);
  } catch (err) { next(err); }
});

app.post('/tasks', authMiddleware, async (req, res, next) => {
  try {
    const { matn } = req.body;
    if (!matn) { const e = new Error("'matn' majburiy"); e.status = 400; throw e; }
    const result = await pool.query(
      'INSERT INTO tasks (user_id, matn, bajarildi) VALUES ($1, $2, false) RETURNING *',
      [req.user.id, matn]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});

app.put('/tasks/:id', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query(
      'UPDATE tasks SET bajarildi = NOT bajarildi WHERE id = $1 AND user_id = $2 RETURNING *',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.json(result.rows[0]);
  } catch (err) { next(err); }
});

app.delete('/tasks/:id', authMiddleware, async (req, res, next) => {
  try {
    const result = await pool.query(
      'DELETE FROM tasks WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (result.rowCount === 0) return res.status(404).json({ xato: 'Topilmadi' });
    res.status(204).send();
  } catch (err) { next(err); }
});

// ─────────────────────────────────────────────────────────────────────
// Ataylab xato — WHERE'da user_id yo'q, IDOR (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
app.get('/tasks-xato/:id', authMiddleware, async (req, res, next) => {
  const result = await pool.query('SELECT * FROM tasks WHERE id = $1', [req.params.id]);
  // ❌ user_id tekshirilmagan — istalgan foydalanuvchi istalgan taskni ko'ra oladi!
  res.json(result.rows[0]);
});
*/

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

app.listen(3000, () => {
  console.log('Server ishga tushdi: http://localhost:3000');
});
"""

R3_EX = [
    {
        "title": "Nega har bir /tasks so'rovida WHERE user_id kerak?",
        "description": "GET/PUT/DELETE /tasks/:id so'rovlarida nega WHERE shartiga user_id ham qo'shilishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat so'rovni tezlashtirish uchun",
            "Foydalanuvchi faqat o'ziga tegishli qatorlarni ko'rishi/o'zgartirishi mumkinligini ta'minlash uchun",
            "PostgreSQL buni talab qiladi",
            "Hech qanday sabab yo'q, ixtiyoriy",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Token to'g'riligi — bu ma'lumotga egalik huquqini bildirmaydi.",
        "explanation": "authMiddleware faqat foydalanuvchi kim ekanini aniqlaydi. Ma'lumot haqiqatan shu foydalanuvchiga tegishli ekanini tekshirish — har bir so'rovning o'z vazifasi, WHERE user_id = $X orqali amalga oshiriladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "IDOR nima?",
        "description": "IDOR (Insecure Direct Object Reference) zaifligi nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Server juda sekin ishlashi",
            "To'g'ri autentifikatsiyalangan foydalanuvchi, ID'ni taxmin qilib, boshqasiga tegishli ma'lumotga ruxsatsiz kira olishi",
            "Parolni unutib qo'yish",
            "Ma'lumotlar bazasi ulanishi uzilishi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Token to'g'ri, lekin so'ralgan resurs egaligini hech kim tekshirmagan.",
        "explanation": "IDOR — to'g'ri autentifikatsiyalangan (token bor) foydalanuvchi, faqat ID'ni o'zgartirib, boshqa foydalanuvchiga tegishli ma'lumotni ko'rishi yoki o'zgartirishi mumkin bo'lgan zaiflik, chunki server bu ma'lumot haqiqatan so'rovchiga tegishliligini tekshirmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "PUT /tasks/:id so'rovi oqimini to'g'ri tartibda joylang",
        "description": "Foydalanuvchi o'z taskini yangilaganda bo'ladigan tekshiruvlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "authMiddleware token to'g'riligini tekshiradi, req.user o'rnatiladi",
            "UPDATE ... WHERE id = $1 AND user_id = $2 bajariladi",
            "rowCount tekshiriladi — 0 bo'lsa 404",
            "Yangilangan task JSON sifatida qaytariladi",
        ],
        "correct_order": [
            "authMiddleware token to'g'riligini tekshiradi, req.user o'rnatiladi",
            "UPDATE ... WHERE id = $1 AND user_id = $2 bajariladi",
            "rowCount tekshiriladi — 0 bo'lsa 404",
            "Yangilangan task JSON sifatida qaytariladi",
        ],
        "hint": "Avval kim ekanligi aniqlanadi, keyin egalik tekshirilib DB'ga yoziladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "5-9-darslarning har biri IDOR'ning oldini olishda qanday rol o'ynaydi?",
        "description": (
            "DB ulanish, CRUD, validatsiya/xato boshqaruvi, JWT autentifikatsiya "
            "va protected routes — ularning har biri IDOR kabi zaiflikning "
            "oldini olishda qanday rol o'ynaydi? Agar ulardan biri yetishmasa "
            "(masalan, faqat authMiddleware bo'lib, WHERE user_id yo'q bo'lsa) "
            "nima yuz beradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "authMiddleware (JWT autentifikatsiya) faqat so'rov qaysi "
            "foydalanuvchidan kelayotganini tasdiqlaydi — bu \"kimlik\" "
            "tekshiruvi. Lekin bu, so'ralgan ma'lumotning aynan shu "
            "foydalanuvchiga tegishli ekanini kafolatlamaydi — bu \"egalik\" "
            "tekshiruvi bo'lib, CRUD so'rovlarining o'zida (WHERE user_id = "
            "$X) amalga oshirilishi kerak. Agar faqat autentifikatsiya bo'lib, "
            "egalikni tekshirish yo'q bo'lsa, har qanday tizimga kirgan "
            "foydalanuvchi boshqa birovning ma'lumotlarini ID'ni taxmin "
            "qilib ko'rishi yoki o'zgartirishi mumkin bo'ladi — bu aynan "
            "IDOR zaifligi. Shuning uchun autentifikatsiya va egalikni "
            "tekshirish — ikkalasi ham, birga, har bir himoyalangan route'da "
            "bo'lishi shart."
        ),
        "hint": "Autentifikatsiya \"kim ekanini\" bilsa, egalikni tekshirish \"nimaga ruxsati borligini\" bildiradi — ikkalasi turlicha narsa.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L10_TEXT = """\
<h2>CORS va React bilan ulash</h2>

<pre class="mermaid">
flowchart LR
    R["React (localhost:3000)"] -->|fetch| E["Express API (localhost:5000)"]
    E -->|CORS header yo'q| BLOCK["Brauzer: bloklandi!"]
    E -->|cors() bilan| OK["Brauzer: ruxsat berildi"]
</pre>

<p>Hozirgacha barcha so'rovlarni Postman yoki brauzerning o'zidan (bir xil manzil) yuborib keldik. Lekin React ilovangiz boshqa portda (masalan, <code>localhost:3000</code>) ishlaydi, Express esa boshqasida (<code>localhost:5000</code>) — bu <strong>turli manba</strong> (origin) hisoblanadi, va brauzer buni standart holda bloklaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — cors o'rnatish va yoqish</h4>
<pre><code>// Terminal:
npm install cors</code></pre>

<pre><code>const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors()); // ❗ standart holda BARCHA manbalarga ruxsat beradi
app.use(express.json());

app.get('/api/products', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});</code></pre>

<h4>BLOKA 2 — React tomonidan so'rov yuborish</h4>
<pre><code>// React komponenti ichida:
useEffect(() =&gt; {
  fetch('http://localhost:5000/api/products')
    .then(res =&gt; res.json())
    .then(data =&gt; setProducts(data))
    .catch(err =&gt; console.error('Xato:', err));
}, []);</code></pre>

<h4>BLOKA 3 — faqat kerakli manbalarga ruxsat berish (production uchun)</h4>
<pre><code>const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: allowedOrigins, // ❗ faqat shu manbalarga ruxsat, boshqalarga yo'q
  credentials: true,       // cookie/auth header yuborish uchun
}));</code></pre>

<h3>🐛 Ataylab xato — cors()ni express.json()dan keyin yoki noto'g'ri joyga qo'yish</h3>
<pre><code>// ❌ Bu yerda cors() umuman chaqirilmagan yoki route'lardan KEYIN qo'yilgan
const app = express();
app.use(express.json());

app.get('/api/products', (req, res) =&gt; {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});

app.use(cors()); // ❌ juda kech — route allaqachon javob yuborib bo'ladi</code></pre>

<p><strong>Natija:</strong> React ilovasidan <code>fetch()</code> chaqirilganda, brauzer konsolida <code>"has been blocked by CORS policy"</code> degan xato chiqadi — garchi Express serveri o'zi to'g'ri ishlab, ma'lumotni qaytargan bo'lsa ham! Sabab: CORS header'lari <strong>javob route ishlashidan oldin</strong> qo'shilishi kerak, aks holda brauzer javobni oladi, lekin kerakli <code>Access-Control-Allow-Origin</code> header'i yo'qligi sababli uni JavaScript kodiga o'tkazishdan bosh tortadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. CORS nima va nega mavjud?</h4>
<p>CORS (Cross-Origin Resource Sharing) — brauzerning xavfsizlik mexanizmi. U bir sayt (masalan, yovuz sayt) boshqa saytning API'siga foydalanuvchi nomidan yashirincha so'rov yubormasligi uchun standart holda <strong>turli manbalar orasidagi</strong> so'rovlarni bloklaydi.</p>

<h4>2. "Manba" (origin) nima?</h4>
<p>Manba — protokol + domen + port birikmasi. <code>http://localhost:3000</code> va <code>http://localhost:5000</code> — ikkita <strong>turli</strong> manba, garchi ikkalasi ham <code>localhost</code> bo'lsa ham (port farqi yetarli).</p>

<h4>3. cors() middleware qanday ishlaydi?</h4>
<p><code>app.use(cors())</code> — har bir javobga <code>Access-Control-Allow-Origin</code> va shunga o'xshash header'larni avtomatik qo'shadi. Bu header'lar bo'lmasa, brauzer javobni JavaScript kodiga bermaydi — garchi server javobni to'liq yuborgan bo'lsa ham.</p>

<h4>4. Nega production'da origin: '*' xavfli?</h4>
<p>Standart <code>cors()</code> — barcha manbalarga ruxsat beradi (<code>*</code>). Bu development uchun qulay, lekin production'da xavfli bo'lishi mumkin, ayniqsa <code>credentials: true</code> bilan birga ishlatilganda. Shuning uchun production'da <code>origin</code>ni aniq ro'yxat sifatida cheklash tavsiya etiladi.</p>

<h4>5. Middleware joylashuvi — yana bir bor</h4>
<p>4 va 7-darslarda ko'rganimizdek, middleware'lar yozilish tartibida ishlaydi. <code>cors()</code> har doim route'lardan <strong>oldin</strong>, odatda eng birinchi qatorlarda qo'shiladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ CORS — brauzerning turli-manbali so'rovlarni bloklovchi xavfsizlik siyosati</li>
<li>✅ <code>cors()</code> middleware'i kerakli header'larni avtomatik qo'shadi</li>
<li>✅ <code>cors()</code> route'lardan <strong>oldin</strong> qo'shilishi shart, aks holda header'lar javobga qo'shilmaydi</li>
<li>✅ Production'da <code>origin</code>ni aniq domenlar ro'yxati bilan cheklash xavfsizroq</li>
<li>✅ React va Express turli portlarda ishlaganda — bu har doim "turli manba" hisoblanadi</li>
</ul>
"""

L10_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 10: CORS va React bilan ulash
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const cors = require('cors');
const app = express();

// ─────────────────────────────────────────────────────────────────────
// 1) CORS — route'lardan OLDIN qo'shiladi
// ─────────────────────────────────────────────────────────────────────

const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
}));

app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 2) Oddiy API route — React shu manzilga fetch qiladi
// ─────────────────────────────────────────────────────────────────────

app.get('/api/products', (req, res) => {
  res.json([
    { id: 1, nomi: 'Noutbuk', narxi: 8000000 },
    { id: 2, nomi: 'Sichqoncha', narxi: 150000 },
  ]);
});

// ─────────────────────────────────────────────────────────────────────
// React tomonida (alohida frontend loyihasida):
//
// useEffect(() => {
//   fetch('http://localhost:5000/api/products')
//     .then(res => res.json())
//     .then(data => setProducts(data))
//     .catch(err => console.error('Xato:', err));
// }, []);
// ─────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato — cors() route'lardan keyin (izohda, ishlamaydi)
// ─────────────────────────────────────────────────────────────────────

/*
const appXato = express();
appXato.use(express.json());
appXato.get('/api/products', (req, res) => res.json([]));
appXato.use(cors()); // ❌ juda kech — brauzer bu javobni bloklaydi
*/

app.listen(5000, () => {
  console.log('Server ishga tushdi: http://localhost:5000');
});
"""

L10_EX = [
    {
        "title": "CORS nima uchun mavjud?",
        "description": "Brauzer CORS mexanizmini nima uchun qo'llaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Serverni tezlashtirish uchun",
            "Bir sayt boshqa saytning API'siga foydalanuvchi nomidan yashirincha so'rov yubormasligi uchun",
            "JSON formatini tekshirish uchun",
            "Ma'lumotlar bazasini himoyalash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — brauzerning xavfsizlik mexanizmi, serverniki emas.",
        "explanation": "CORS — brauzerning xavfsizlik siyosati bo'lib, turli manbalar orasidagi so'rovlarni standart holda bloklaydi, shu orqali yovuz saytlarning boshqa API'larga yashirin so'rov yuborishining oldini oladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "localhost:3000 va localhost:5000 bir xil manbami?",
        "description": "http://localhost:3000 va http://localhost:5000 — CORS nuqtai nazaridan bir xil manbami?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ha, ikkalasi ham localhost bo'lgani uchun bir xil",
            "Yo'q, port farqli bo'lgani uchun ular turli manba hisoblanadi",
            "Faqat domen muhim, port emas",
            "Bu HTTPS bo'lsa bir xil bo'ladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Manba — protokol + domen + PORT birikmasi.",
        "explanation": "Manba (origin) protokol, domen va portning birikmasidan iborat. Faqat port farqli bo'lsa ham, ular turli manba hisoblanadi va CORS qoidalari qo'llanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "cors() middleware qayerga qo'yilishi kerak?",
        "description": "React'dan kelayotgan so'rovlar to'g'ri ishlashi uchun cors() qayerga joylashtirilishi kerakligini tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "const app = express() — ilova yaratiladi",
            "app.use(cors()) — CORS header'lari yoqiladi",
            "app.use(express.json()) — body parser qo'shiladi",
            "app.get('/api/...', handler) — route'lar ro'yxatdan o'tadi",
        ],
        "correct_order": [
            "const app = express() — ilova yaratiladi",
            "app.use(cors()) — CORS header'lari yoqiladi",
            "app.use(express.json()) — body parser qo'shiladi",
            "app.get('/api/...', handler) — route'lar ro'yxatdan o'tadi",
        ],
        "hint": "CORS har doim route'lardan oldin, ilova yaratilgandan keyin darhol qo'shiladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "cors() route'lardan keyin qo'yilsa nima bo'ladi?",
        "description": (
            "Agar app.use(cors()) route'lar ro'yxatdan o'tkazilgandan KEYIN "
            "yozilsa, React ilovasidan qilingan fetch() so'roviga nima "
            "bo'ladi? Server o'zi to'g'ri javob qaytarayotgan bo'lsa ham, "
            "nega muammo yuzaga keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Express middleware va route'larni yozilish tartibida ishga "
            "tushiradi. Agar cors() route'lardan keyin yozilsa, u umuman "
            "chaqirilmaydi (chunki route allaqachon javobni yuborib "
            "bulgan bo'ladi) yoki CORS header'lari javobga qo'shilmasdan "
            "qoladi. Server o'zi to'g'ri ma'lumotni qaytargan bo'lsa ham, "
            "brauzer javobda kerakli Access-Control-Allow-Origin header'ini "
            "topa olmagani uchun, xavfsizlik siyosatiga ko'ra bu javobni "
            "JavaScript kodiga (masalan, React'dagi .then() ichiga) "
            "o'tkazishdan bosh tortadi va konsolda CORS xatosi chiqadi."
        ),
        "hint": "Middleware'lar yozilish tartibida ishlaydi — bu yerda cors() qachon ishga tushadi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L11_TEXT = """\
<h2>Deploy tayyorgarligi — production'ga chiqishdan oldin</h2>

<pre class="mermaid">
flowchart LR
    ENV[".env — maxfiy sozlamalar"] --> APP["Express ilova"]
    APP --> HEALTH["GET /health — status tekshiruvi"]
    APP --> LOG["Xatolar log qilinadi"]
    APP -->|deploy| PROD["Production server"]
</pre>

<p>Kursimiz davomida <code>process.env.JWT_SECRET</code> kabi maxfiy qiymatlarni ko'p marta eslatib o'tdik. Endi buni to'liq amalga oshiramiz va ilovani production'ga chiqarishdan oldin qanday tekshirish kerakligini o'rganamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — dotenv bilan .env faylini ulash</h4>
<pre><code>// Terminal:
npm install dotenv</code></pre>

<pre><code>// .env fayli (bu fayl .gitignore'da bo'lishi SHART!)
DATABASE_URL=postgresql://user:parol@localhost:5432/mening_bazam
JWT_SECRET=juda-maxfiy-va-uzun-satr-2024
CORS_ORIGINS=http://localhost:3000,https://mysite.uz
PORT=5000</code></pre>

<pre><code>// server.js — eng birinchi qatorda
require('dotenv').config(); // ❗ boshqa hamma narsadan OLDIN chaqiriladi

const express = require('express');
const app = express();

const PORT = process.env.PORT || 3000;</code></pre>

<h4>BLOKA 2 — health-check endpoint</h4>
<pre><code>app.get('/health', (req, res) =&gt; {
  res.status(200).json({
    status: 'ok',
    vaqt: new Date().toISOString(),
  });
});
// ❗ Deploy tizimlari (masalan, Docker, load balancer) shu manzilga
// muntazam so'rov yuborib, server "tirikligini" tekshiradi.</code></pre>

<h4>BLOKA 3 — package.json scripts va production start</h4>
<pre><code>{
  "scripts": {
    "dev": "nodemon server.js",
    "start": "node server.js"
  }
}</code></pre>
<pre><code>// Terminal (production serverida):
npm install --production   // devDependencies (nodemon kabi) o'rnatilmaydi
npm start                  // node server.js — nodemon EMAS!</code></pre>

<h3>🐛 Ataylab xato — maxfiy kalitni kodga yozib, git'ga qo'shish</h3>
<pre><code>// ❌ server.js ichida to'g'ridan-to'g'ri
const JWT_SECRET = 'mening-maxfiy-kalitim-123'; // ❌ kodga yozilgan!

// ❌ .env fayli .gitignore'da yo'q — git add . bilan repo'ga tushib ketadi
// $ git status
//   modified: .env    ← BU KO'RINMASLIGI KERAK!</code></pre>

<p><strong>Natija:</strong> agar <code>.env</code> fayli tasodifan GitHub'ga (hattoki xususiy repo'ga ham) yuklansa, JWT maxfiy kaliti, DB paroli va boshqa barcha maxfiy ma'lumotlar butunlay ochiq bo'lib qoladi. Repo tarixi (git history) dan ham keyinchalik butunlay o'chirish qiyin — bir marta commit qilingan narsa "abadiy" saqlanib qolishi mumkin. Shuning uchun <strong>loyihani boshlashning birinchi kunidayoq</strong> <code>.gitignore</code>ga <code>.env</code> qo'shilishi shart, undan keyin emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. require('dotenv').config() nega eng birinchi qatorda?</h4>
<p>Bu chaqiruv <code>.env</code> faylini o'qib, uning qiymatlarini <code>process.env</code>ga yuklaydi. Agar bu boshqa kodlardan keyin chaqirilsa, undan oldingi kodlar hali <code>process.env.JWT_SECRET</code>ni <code>undefined</code> deb o'qishi mumkin.</p>

<h4>2. .gitignore — nima uchun muhim?</h4>
<pre><code># .gitignore fayli
.env
node_modules/</code></pre>
<p><code>.gitignore</code>ga qo'shilgan fayllar <code>git add</code> paytida e'tiborsiz qoldiriladi. <code>.env</code> hech qachon git repo'ga tushmasligi kerak — buning o'rniga <code>.env.example</code> (haqiqiy qiymatlarsiz, faqat kalit nomlari bilan) commit qilinadi.</p>

<h4>3. Health-check nega kerak?</h4>
<p>Production muhitida (Docker, Kubernetes, load balancer) tizim serverning "tirik"ligini avtomatik tekshiradi. <code>/health</code> kabi oddiy endpoint bo'lmasa, tizim serverning haqiqatan ishlab turganini bilishning oson yo'liga ega bo'lmaydi.</p>

<h4>4. npm start vs npm run dev — farqi</h4>
<p><code>nodemon</code> — development uchun qulay (avtomatik qayta ishga tushirish), lekin production'da keraksiz resurs sarflaydi va fayllarni kuzatib turishning hojati yo'q. Production'da oddiy <code>node server.js</code> (<code>npm start</code> orqali) ishlatiladi.</p>

<h4>5. Production checklist (qisqacha)</h4>
<ul>
<li>Barcha maxfiy qiymatlar <code>.env</code>da, <code>.gitignore</code>ga qo'shilgan</li>
<li><code>/health</code> endpoint mavjud</li>
<li>Markazlashtirilgan xato middleware (7-dars) ishlaydi</li>
<li>CORS faqat kerakli domenlarga cheklangan (10-dars)</li>
<li><code>npm start</code> — <code>nodemon</code>siz, oddiy <code>node</code> bilan ishga tushadi</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>dotenv</code> — <code>.env</code> faylidagi qiymatlarni <code>process.env</code>ga yuklaydi</li>
<li>✅ <code>.env</code> hech qachon git'ga qo'shilmaydi — <code>.gitignore</code>ga birinchi kundanoq kiritiladi</li>
<li>✅ <code>/health</code> endpoint — deploy tizimlari uchun serverning tiriklik belgisi</li>
<li>✅ Production'da <code>npm start</code> (oddiy <code>node</code>) ishlatiladi, <code>nodemon</code> emas</li>
<li>✅ Bu — butun kursda o'rgangan hamma narsani (routing, DB, auth, CORS, xato boshqaruvi) production uchun tayyorlash bosqichi</li>
</ul>
"""

L11_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 11: Deploy tayyorgarligi
// ════════════════════════════════════════════════════════════════════

require('dotenv').config(); // ❗ eng birinchi qator

const express = require('express');
const cors = require('cors');
const app = express();

const PORT = process.env.PORT || 3000;

// ─────────────────────────────────────────────────────────────────────
// 1) CORS + JSON — o'rgangan darslardagidek
// ─────────────────────────────────────────────────────────────────────

const allowedOrigins = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({ origin: allowedOrigins, credentials: true }));
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 2) Health-check endpoint
// ─────────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    vaqt: new Date().toISOString(),
  });
});

// ─────────────────────────────────────────────────────────────────────
// 3) Oddiy route
// ─────────────────────────────────────────────────────────────────────

app.get('/api/products', (req, res) => {
  res.json([{ id: 1, nomi: 'Noutbuk' }]);
});

// ─────────────────────────────────────────────────────────────────────
// 4) Markazlashtirilgan xato middleware (7-darsdagidek)
// ─────────────────────────────────────────────────────────────────────

app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status || 500).json({ xato: { xabar: err.message, status: err.status || 500 } });
});

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato — maxfiy kalitni kodga yozish (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
const JWT_SECRET_XATO = 'mening-maxfiy-kalitim-123'; // ❌ kodga yozilgan, .env emas!
// Bu qiymat git repo'ga tushib qoladi va hech qachon haqiqiy maxfiy bo'lmaydi.
*/

app.listen(PORT, () => {
  console.log(`Server ishga tushdi: http://localhost:${PORT}`);
});

// package.json:
// {
//   "scripts": {
//     "dev": "nodemon server.js",
//     "start": "node server.js"
//   }
// }
//
// Production serverida:
//   npm install --production
//   npm start
"""

L11_EX = [
    {
        "title": "require('dotenv').config() qayerga yoziladi?",
        "description": "dotenv orqali .env qiymatlarini yuklash uchun require('dotenv').config() odatda qayerga yoziladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faylning istalgan joyiga, farqi yo'q",
            "Faylning eng boshiga, boshqa kod ishga tushishidan oldin",
            "Faqat app.listen() ichida",
            "package.json ichida",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agar keyinroq chaqirilsa, undan oldingi kod process.env qiymatlarini hali ololmaydi.",
        "explanation": "require('dotenv').config() faylning eng boshida chaqirilishi kerak, aks holda undan oldin yozilgan kod process.env orqali .env qiymatlarini o'qishga urinsa, hali yuklanmagani uchun undefined qaytaradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": ".env fayli qayerda bo'lishi shart?",
        "description": ".env fayli git repo'ga tushib ketmasligi uchun qayerga qo'shilishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "package.json ichiga",
            ".gitignore fayliga",
            "README.md fayliga",
            "Hech qayerga, avtomatik e'tiborsiz qoldiriladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": ".gitignore'ga qo'shilgan fayllar git add paytida e'tiborsiz qoldiriladi.",
        "explanation": ".env fayli .gitignore'ga qo'shilishi shart, aks holda u git add . bilan repo'ga tushib, barcha maxfiy ma'lumotlar (parollar, kalitlar) ochiq bo'lib qoladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Serverni ishga tushirish (dev va production) ketma-ketligini joylang",
        "description": "Loyihani development'dan production'gacha olib borish qadamlarini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "npm run dev — nodemon bilan development",
            ".env fayliga barcha maxfiy qiymatlar yoziladi (.gitignore'da)",
            "package.json'da 'start': 'node server.js' belgilanadi",
            "Production serverida npm install --production",
            "Production serverida npm start bilan ishga tushiriladi",
        ],
        "correct_order": [
            "npm run dev — nodemon bilan development",
            ".env fayliga barcha maxfiy qiymatlar yoziladi (.gitignore'da)",
            "package.json'da 'start': 'node server.js' belgilanadi",
            "Production serverida npm install --production",
            "Production serverida npm start bilan ishga tushiriladi",
        ],
        "hint": "Avval development, keyin sozlamalar tayyorlanadi, so'ng production'ga chiqariladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": ".env fayli tasodifan GitHub'ga yuklansa nima yuz beradi?",
        "description": (
            "Agar .env fayli .gitignore'ga qo'shilmasdan, tasodifan GitHub'ga "
            "(hattoki xususiy repo'ga ham) yuklab yuborilsa, bu nima uchun "
            "jiddiy muammo hisoblanadi? Muammoni oldini olish uchun nima "
            "qilish kerak edi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar .env fayli git repo'ga tushib qolsa, undagi barcha maxfiy "
            "ma'lumotlar — JWT maxfiy kaliti, ma'lumotlar bazasi paroli, API "
            "kalitlar — repo'ga kirish huquqiga ega bo'lgan har kimga ochiq "
            "bo'lib qoladi, hattoki repo xususiy bo'lsa ham (masalan, "
            "hamkasblar, keyinchalik qo'shilgan a'zolar, yoki repo tasodifan "
            "ochiq qilinsa). Bundan battarrog'i, git tarixi odatda saqlanib "
            "qoladi — faylni keyinroq o'chirsangiz ham, u avvalgi commit'larda "
            "qolib ketishi mumkin, uni butunlay tarixdan olib tashlash "
            "murakkab jarayon. Buning oldini olish uchun .env fayli "
            "loyihaning ENG BOSHIDA, birinchi commit'dan oldin .gitignore'ga "
            "qo'shilishi kerak edi."
        ),
        "hint": "Git tarixi — commit qilingan narsa oson-oson butunlay yo'q bo'lib ketmaydi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order: int, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "js",
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
            lang = ldata.get("lang", "js")

            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=10,
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
                    [{"filename": f"app.{lang}", "language": lang, "code": code}],
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
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
