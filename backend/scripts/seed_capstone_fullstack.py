"""Seed "Capstone: To'liq Stack Loyiha" (6 lessons): fills a real gap — every
existing course is siloed within one technology, with no course that forces
students to actually integrate a frontend (React) and backend (Node/Express)
into one deployed project across multiple milestones.

Unlike other courses, every lesson here also carries a real project-submission
assignment via the existing task_title/task_description/task_requirements/
task_technologies/task_deadline_days fields on Lesson (the same mechanism
already used by 255 other lessons platform-wide, e.g. lesson 186's Flask
factory-pattern task) — students build ONE evolving "TaskFlow" app across all
6 milestones, resubmitting the same (updated) github_url/live_demo_url each
time via the existing Submission + AI-grading pipeline. No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_fullstack
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py.

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
    "title": "Capstone: To'liq Stack Loyiha",
    "description": (
        "React: Redux Toolkit, TypeScript va Testlash HAMDA Node.js/Express "
        "Asoslari kurslarini tugatgan dasturchilar uchun: alohida "
        "texnologiyalarni emas, balki ularni BIR loyihada birlashtirishni "
        "o'rganing. 6 bosqichda 'TaskFlow' nomli jamoaviy vazifalar "
        "boshqaruvchisini rejalashtirish, backend API, React frontend, "
        "autentifikatsiya, qidiruv/filtr va real deploy'gacha qurasiz — "
        "har bir bosqich haqiqiy loyiha topshirig'i sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 5,
    "max_points": 220,
    "category_id": 9,  # React
    "prerequisite_course_id": 74,  # Node.js/Express Asoslari (also assumes course 72: React Redux/TS/Testing)
    "is_active": True,
    "is_published": False,  # flip to True once all 6 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "DB schema design, repo scaffold, README, project planning for TaskFlow."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Backend API",
     "scope": "Express + PostgreSQL CRUD endpoints for tasks/categories."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-React frontend",
     "scope": "React + Redux Toolkit consuming the backend API, rendering tasks."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Autentifikatsiya",
     "scope": "JWT auth on backend + login/register UI + protected routes on frontend."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Qidiruv va filtrlash",
     "scope": "Full-stack search/filter/pagination feature spanning both ends."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "CORS, env vars, real deployment, final README, live_demo_url submission."},
]


L1_TEXT = """\
<h2>TaskFlow — 6 bosqichda to'liq stack loyiha</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> API["2-Backend API"]
    API --> FE["3-React frontend"]
    FE --> AUTH["4-Autentifikatsiya"]
    AUTH --> SEARCH["5-Qidiruv/filtr"]
    SEARCH --> DEPLOY["6-Deploy"]
</pre>

<p>Bu kursda siz React va Node.js/Express kurslarida <strong>alohida</strong> o'rgangan hamma narsani <strong>bitta haqiqiy loyiha</strong>da birlashtirasiz: <strong>TaskFlow</strong> — jamoaviy vazifalar boshqaruvchisi. Har bir dars — shu bitta loyihaning navbatdagi bosqichi, va har bir bosqich <strong>haqiqiy loyiha topshirig'i</strong> sifatida (GitHub repo + tavsif orqali) baholanadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo tuzilmasi: monorepo</h4>
<pre><code># TaskFlow uchun bitta repo ichida ikkita papka - "monorepo" yondashuvi
taskflow/
  backend/          # Express + PostgreSQL (2-4-darsda quriladi)
    package.json
    server.js
  frontend/          # React + Redux Toolkit (3-darsda quriladi)
    package.json
    src/
  README.md          # loyiha tavsifi, ishga tushirish yo'riqnomasi
  .gitignore          # node_modules, .env kabi fayllarni chiqarib tashlaydi

# Nega monorepo? Kichik jamoaviy loyihalarda frontend va backend'ni
# BIR joyda ko'rish, versiyalashni sinxronlashtirish osonroq bo'ladi.</code></pre>

<h4>BLOKA 2 — DB sxemasini KOD YOZISHDAN OLDIN loyihalash</h4>
<pre><code># TaskFlow uchun asosiy jadvallar (ER diagramma darajasida, hali SQL emas):
#
# users        (id, ism, email, parol_hash, yaratilgan_vaqt)
# categories   (id, nomi, user_id -> users.id)
# tasks        (id, sarlavha, matn, bajarilgan, category_id -> categories.id,
#               user_id -> users.id, yaratilgan_vaqt)
#
# Bog'lanishlar:
# - Bitta user -> ko'p categories (1 ga ko'p)
# - Bitta user -> ko'p tasks (1 ga ko'p)
# - Bitta category -> ko'p tasks (1 ga ko'p)

# Bu sxema 2-darsda haqiqiy PostgreSQL jadvallariga aylantiriladi.</code></pre>

<h4>BLOKA 3 — README.md: loyihaning "eshigi"</h4>
<pre><code># README.md
# TaskFlow

## Loyiha haqida
Jamoaviy vazifalar boshqaruvchisi - React + Node/Express + PostgreSQL.

## O'rnatish
1. `cd backend && npm install`
2. `.env` faylini yarating (`.env.example`dan nusxa oling)
3. `npm run dev`

## Texnologiyalar
- Backend: Node.js, Express, PostgreSQL
- Frontend: React, Redux Toolkit

## Holat
- [x] Loyihalash va repo skeleton
- [ ] Backend API
- [ ] React frontend
- [ ] Autentifikatsiya
- [ ] Qidiruv va filtrlash
- [ ] Deploy</code></pre>

<h3>🐛 Ataylab qiyin: DB sxemasisiz to'g'ridan-to'g'ri kod yozishga urinish</h3>
<p>Ko'p boshlang'ich dasturchilar DB sxemasini loyihalashni "keyinroq qilaman" deb, darhol Express route'lari yoki React componentlarini yoza boshlaydi. Bu quyidagi muammoga olib keladi:</p>
<pre><code>// 2-darsda backend yozishni boshlaganingizda:
app.post('/tasks', async (req, res) => {
  // savol: task qaysi user'ga tegishli? category kerakmi?
  // Agar sxema oldindan aniq bo'lmasa, bu yerda IKKILANISH boshlanadi,
  // va keyinchalik jadval tuzilishini o'zgartirish (migratsiya) kerak bo'ladi
});</code></pre>
<p><strong>Natija:</strong> DB sxemasi (jadvallar, ustunlar, bog'lanishlar) <strong>oldindan aniq bo'lmasa</strong>, backend kodini yozish paytida doimiy "bu maydon kerakmi?", "bu qanday bog'lanadi?" kabi savollar tug'iladi — bu vaqtni behuda sarflaydi va ko'pincha keyinroq <strong>qayta migratsiya</strong> qilishga majbur qiladi. To'g'ri tartib: <strong>avval</strong> sxemani qog'ozda (yoki diagram sifatida) chizib, <strong>keyin</strong> kodni yozish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega monorepo (bitta repo, ikkita papka) tanlandi?</h4>
<p>Kichik, bitta dasturchi (yoki kichik jamoa) tomonidan qurilayotgan to'liq stack loyihalar uchun monorepo qulay: frontend va backend o'zgarishlarini <strong>bitta joyda</strong> kuzatish, versiyalashni sinxronlashtirish osonroq. Katta kompaniyalarda ko'pincha alohida repo'lar ishlatiladi, lekin bu boshqa masala.</p>

<h4>2. Nega DB sxemasi eng birinchi loyihalanadi?</h4>
<p>Deyarli <strong>hamma narsa</strong> — backend endpoint'lari, frontend'dagi ma'lumot shakli, autentifikatsiya — DB sxemasiga bog'liq. Sxema noaniq bo'lsa, keyingi bosqichlarning har birida qayta-qayta qaror qabul qilishga to'g'ri keladi. Sxemani oldindan loyihalash — keyingi bosqichlarni tezlashtiradi.</p>

<h4>3. README.md nima uchun muhim?</h4>
<p>README — loyihaning "eshigi": boshqa dasturchi (yoki baholovchi) loyihani birinchi marta ko'rganda, uni <strong>qanday ishga tushirish</strong>, qaysi texnologiyalar ishlatilgani va joriy holatni shu yerdan biladi. Bu 6-darsda deploy qilinganda ham juda muhim bo'ladi.</p>

<h4>4. Bu kursda "topshiriq" oldingi kurslardan nima bilan farq qiladi?</h4>
<p>Oldingi kurslarda har bir dars <strong>mustaqil</strong> mavzu edi. Bu yerda har bir dars <strong>bitta, davom etayotgan loyihaning</strong> keyingi bosqichi — siz har safar <strong>bir xil</strong> GitHub repo'ga (yangilangan holda) havola yuborasiz, va loyiha 6-darsning oxirida <strong>to'liq, deploy qilingan</strong> ilova bo'lishi kerak.</p>

<h4>5. .gitignore nima uchun kerak?</h4>
<p><code>.gitignore</code> — <code>node_modules</code> (juda katta, qayta o'rnatish mumkin) va <code>.env</code> (maxfiy kalitlar) kabi fayllarni repo'ga <strong>tushmasligi</strong> uchun belgilaydi. Bularni repo'ga qo'shish — repo hajmini keraksiz kattalashtiradi va (agar <code>.env</code> bo'lsa) <strong>maxfiy ma'lumotlarni oshkor qilish xavfi</strong> tug'diradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Monorepo — kichik to'liq stack loyihalar uchun frontend+backend'ni bitta repo'da saqlash</li>
<li>✅ DB sxemasi kod yozishdan <strong>oldin</strong> loyihalanishi kerak</li>
<li>✅ README.md — loyihaning ishga tushirish yo'riqnomasi va joriy holatini ko'rsatadi</li>
<li>✅ Bu kursda har bir dars — bitta davom etayotgan loyihaning bosqichi, mustaqil mavzu emas</li>
<li>✅ <code>.gitignore</code> — <code>node_modules</code>/<code>.env</code> kabi fayllarni repo'dan chiqarib tashlaydi</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 1-BOSQICH: Loyihalash va repo skeleton
// ════════════════════════════════════════════════════════════════════

// Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.
// Quyida - TaskFlow uchun DB sxemasining JavaScript obyekt shaklidagi
// "qog'ozdagi" tasviri (hali haqiqiy SQL/migratsiya emas - bu 2-darsda bo'ladi):

const dbSxemasi = {
  users: {
    id: 'SERIAL PRIMARY KEY',
    ism: 'VARCHAR(100)',
    email: 'VARCHAR(255) UNIQUE',
    parol_hash: 'VARCHAR(255)',
    yaratilgan_vaqt: 'TIMESTAMP DEFAULT NOW()',
  },
  categories: {
    id: 'SERIAL PRIMARY KEY',
    nomi: 'VARCHAR(100)',
    user_id: 'INTEGER REFERENCES users(id)',
  },
  tasks: {
    id: 'SERIAL PRIMARY KEY',
    sarlavha: 'VARCHAR(200)',
    matn: 'TEXT',
    bajarilgan: 'BOOLEAN DEFAULT false',
    category_id: 'INTEGER REFERENCES categories(id)',
    user_id: 'INTEGER REFERENCES users(id)',
    yaratilgan_vaqt: 'TIMESTAMP DEFAULT NOW()',
  },
};

console.log(dbSxemasi);

// ─────────────────────────────────────────────────────────────────────
// Repo tuzilmasi (izohda - papka/fayl tuzilmasi, kod emas)
// ─────────────────────────────────────────────────────────────────────

// taskflow/
//   backend/
//   frontend/
//   README.md
//   .gitignore
"""

L1_EX = [
    {
        "title": "Monorepo nima uchun tanlandi?",
        "description": "TaskFlow uchun nega bitta repo ichida backend/ va frontend/ papkalari (monorepo) tanlandi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki alohida repo'lar Git'da ishlamaydi",
            "Kichik loyihalarda frontend va backend o'zgarishlarini bitta joyda kuzatish qulayroq",
            "Chunki React faqat monorepo bilan ishlaydi",
            "Bu majburiy Git qoidasi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu kichik jamoa/yakka dasturchi uchun qulaylik masalasi.",
        "explanation": "Monorepo kichik to'liq stack loyihalarda frontend va backend o'zgarishlarini bitta joyda kuzatish va versiyalashni sinxronlashtirishni osonlashtiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "DB sxemasi qachon loyihalanishi kerak?",
        "description": "TaskFlow'ning DB sxemasi (users, categories, tasks jadvallari) qachon aniqlanishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Loyiha tugagandan keyin",
            "Backend/frontend kodini yozishdan oldin",
            "Faqat deploy qilishdan oldin",
            "Sxema kerak emas, kod yozib ko'rish yetarli",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Deyarli hamma narsa shu sxemaga bog'liq.",
        "explanation": "DB sxemasi backend endpoint'lari va frontend ma'lumot shakliga asos bo'lgani uchun, u kod yozishdan oldin aniq loyihalanishi kerak.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "TaskFlow bog'lanishlarini tartiblang",
        "description": "users, categories, tasks jadvallari orasidagi bog'lanish yo'nalishini mantiqiy tartibda joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Bitta user ro'yxatdan o'tadi",
            "User o'ziga tegishli categories yaratadi (1 ga ko'p)",
            "Har bir category ostida ko'plab tasks yaratiladi (1 ga ko'p)",
            "Har bir task aynan bitta user va bitta category'ga bog'lanadi",
        ],
        "correct_order": [
            "Bitta user ro'yxatdan o'tadi",
            "User o'ziga tegishli categories yaratadi (1 ga ko'p)",
            "Har bir category ostida ko'plab tasks yaratiladi (1 ga ko'p)",
            "Har bir task aynan bitta user va bitta category'ga bog'lanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": ".gitignore'ga qo'shilishi shart bo'lgan fayl/papka",
        "description": "Maxfiy kalitlarni saqlaydigan, repo'ga HECH QACHON qo'shilmasligi kerak bo'lgan fayl nomini yozing (masalan: .env).",
        "exercise_type": "text_input",
        "expected_answer": ".env",
        "hint": "Bu fayl environment o'zgaruvchilarini saqlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega DB sxemasisiz kod yozish keyinroq muammo tug'diradi?",
        "description": (
            "Agar dasturchi DB sxemasini oldindan loyihalamasdan, "
            "darhol Express route'larini yoza boshlasa, bu keyinchalik "
            "qanday muammolarga olib kelishi mumkin? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "DB sxemasi oldindan aniq bo'lmasa, backend kodini yozish "
            "paytida \"bu maydon kerakmi\", \"bu jadval boshqasiga qanday "
            "bog'lanadi\" kabi savollar tez-tez tug'iladi, va dasturchi "
            "bu qarorlarni kodni yozish jarayonining o'zida, shoshilinch "
            "qabul qilishga majbur bo'ladi. Bu nafaqat vaqtni behuda "
            "sarflaydi, balki ko'pincha keyinroq (masalan yangi ustun "
            "yoki bog'lanish kerak bo'lganda) mavjud jadvallarni qayta "
            "migratsiya qilishga, ba'zan esa allaqachon yozilgan kodni "
            "qayta yozishga majbur qiladi — bu esa sxemani oldindan "
            "chizib olganga qaraganda ancha ko'proq vaqt va kuch talab "
            "qiladi."
        ),
        "hint": "Sxema noaniq bo'lganda, backend kodini yozish jarayonida qanday qarorlarni shoshilinch qabul qilishga to'g'ri keladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "TaskFlow — repo skeleton va DB sxema hujjati",
    "task_description": (
        "TaskFlow loyihasi uchun GitHub'da monorepo yarating (backend/ va "
        "frontend/ papkalari bilan), to'liq README.md yozing va users/"
        "categories/tasks jadvallari uchun DB sxemasini (ER diagramma yoki "
        "matn shaklida) README'ga qo'shing. Bu loyiha keyingi 5 bosqichda "
        "shu repo ustida davom etadi."
    ),
    "task_requirements": (
        "• GitHub'da 'taskflow' nomli public repo yaratilgan\n"
        "• backend/ va frontend/ bo'sh papkalar (yoki package.json bilan) mavjud\n"
        "• README.md: loyiha tavsifi, texnologiyalar ro'yxati, holat checklist'i\n"
        "• README.md ichida users/categories/tasks jadvallari va ular orasidagi "
        "bog'lanishlar tasvirlangan (ER diagramma rasmi yoki matn/jadval shaklida)\n"
        "• .gitignore fayli mavjud (node_modules, .env chiqarib tashlangan)"
    ),
    "task_technologies": "Git, GitHub, Markdown, PostgreSQL (sxema loyihalash)",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Backend API — tasks va categories uchun CRUD</h2>

<pre class="mermaid">
flowchart LR
    SCHEMA["1-darsdagi sxema"] --> TABLES["haqiqiy PostgreSQL jadvallari"]
    TABLES --> CRUD["GET/POST/PUT/DELETE /tasks va /categories"]
    CRUD --> JOIN["JOIN orqali category nomi bilan birga qaytariladi"]
</pre>

<p>1-darsda chizgan sxemani endi <strong>haqiqiy</strong> PostgreSQL jadvallariga va Express endpoint'lariga aylantiramiz. Node.js/Express kursida CRUD'ni allaqachon o'rgangansiz — bu safar uni <strong>ikkita bog'langan resurs</strong> (tasks va categories) bilan qurasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — jadvallarni yaratish (1-darsdagi sxemadan)</h4>
<pre><code>-- schema.sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  ism VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  parol_hash VARCHAR(255) NOT NULL,
  yaratilgan_vaqt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  nomi VARCHAR(100) NOT NULL,
  user_id INTEGER REFERENCES users(id)
);

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  sarlavha VARCHAR(200) NOT NULL,
  matn TEXT,
  bajarilgan BOOLEAN DEFAULT false,
  category_id INTEGER REFERENCES categories(id),   -- ❗ 1-darsdagi bog'lanish
  user_id INTEGER REFERENCES users(id),
  yaratilgan_vaqt TIMESTAMP DEFAULT NOW()
);</code></pre>

<h4>BLOKA 2 — GET /tasks: JOIN orqali category nomini ham qaytarish</h4>
<pre><code>const express = require('express');
const pool = require('./db');   // pg Pool obyekti
const app = express();
app.use(express.json());

app.get('/tasks', async (req, res) => {
  const natija = await pool.query(`
    SELECT tasks.*, categories.nomi AS category_nomi
    FROM tasks
    JOIN categories ON tasks.category_id = categories.id   -- ❗ 2 ta jadvalni birlashtiradi
    ORDER BY tasks.yaratilgan_vaqt DESC
  `);
  res.json(natija.rows);
});

app.post('/tasks', async (req, res) => {
  const { sarlavha, matn, category_id } = req.body;
  if (!sarlavha || !category_id) {
    return res.status(400).json({ xato: "'sarlavha' va 'category_id' majburiy" });
  }
  const natija = await pool.query(
    'INSERT INTO tasks (sarlavha, matn, category_id) VALUES ($1, $2, $3) RETURNING *',
    [sarlavha, matn, category_id]   -- ❗ parametrlashtirilgan so'rov - SQL injection'dan himoya
  );
  res.status(201).json(natija.rows[0]);
});</code></pre>

<h4>BLOKA 3 — categoryni o'chirish: bog'liq tasks bo'lsa nima bo'ladi?</h4>
<pre><code>app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;

  // ❗ AVVAL tekshiramiz: shu categoryga bog'liq tasks bormi?
  const bogliqTasks = await pool.query(
    'SELECT COUNT(*) FROM tasks WHERE category_id = $1', [id]
  );
  if (Number(bogliqTasks.rows[0].count) > 0) {
    return res.status(400).json({
      xato: "Bu kategoriyada vazifalar bor, avval ularni o'chiring yoki boshqa kategoriyaga ko'chiring"
    });
  }

  await pool.query('DELETE FROM categories WHERE id = $1', [id]);
  res.status(204).send();
});</code></pre>

<h3>🐛 Ataylab xato — bog'liq tasks borligini tekshirmasdan categoryni o'chirish</h3>
<pre><code>app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM categories WHERE id = $1', [id]);   // ❌ tekshiruvsiz!
  res.status(204).send();
});

// Agar bu categoryga bog'liq tasks mavjud bo'lsa:
// ❌ Xato: update or delete on table "categories" violates foreign key
//    constraint "tasks_category_id_fkey" on table "tasks"
// (500 Internal Server Error - foydalanuvchiga tushunarsiz xato chiqadi!)</code></pre>

<p><strong>Natija:</strong> <code>categories</code> jadvalidagi bir qatorni <code>tasks</code> jadvalidagi biror qator <code>category_id</code> orqali <strong>hali ham ishora qilib turgan</strong> holda o'chirishga urinilsa, PostgreSQL <strong>foreign key constraint</strong>ni buzilishini aniqlab, o'chirishni <strong>rad etadi</strong>. Bu xato Express'da qo'lda ushlanmasa, u to'g'ridan-to'g'ri <strong>500 Internal Server Error</strong> sifatida foydalanuvchiga chiqib ketadi — bu foydalanuvchi uchun tushunarsiz va yomon tajriba. To'g'ri yechim: o'chirishdan <strong>oldin</strong> bog'liq qatorlar borligini tekshirib, aniq <code>400</code> xato xabari qaytarish (yoki loyihaga qarab, <code>ON DELETE CASCADE</code>/<code>SET NULL</code> ishlatish).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega JOIN ishlatiladi?</h4>
<p><code>tasks</code> jadvalida faqat <code>category_id</code> (raqam) saqlanadi, category <strong>nomi</strong> emas. Frontend'da foydalanuvchiga category nomini ko'rsatish uchun, backend <code>JOIN</code> orqali ikkita jadvalni birlashtirib, bitta so'rovda ikkalasining ma'lumotini qaytaradi — bu har bir task uchun alohida category so'rovi yuborishning (N+1 muammosi) oldini oladi.</p>

<h4>2. Nega parametrlashtirilgan so'rovlar (<code>$1</code>, <code>$2</code>) ishlatiladi?</h4>
<p>Agar foydalanuvchi kiritgan matn to'g'ridan-to'g'ri SQL so'roviga "yopishtirilsa" (string concatenation), bu <strong>SQL injection</strong> zaifligiga olib keladi. Parametrlashtirilgan so'rovlar (<code>$1</code>, <code>$2</code>) foydalanuvchi ma'lumotini <strong>alohida</strong> yuboradi, PostgreSQL uni hech qachon "buyruq" sifatida emas, faqat "qiymat" sifatida talqin qiladi.</p>

<h4>3. Foreign key (<code>category_id INTEGER REFERENCES categories(id)</code>) nima qiladi?</h4>
<p>Bu cheklov <code>tasks.category_id</code>'ning <strong>faqat</strong> haqiqatan mavjud bo'lgan <code>categories.id</code>ga ishora qilishini ta'minlaydi — mavjud bo'lmagan category_id bilan task yaratishga urinish xato beradi. Bu ma'lumotlar bazasi darajasidagi <strong>yaxlitlik</strong> (integrity) kafolati.</p>

<h4>4. Nega category o'chirishdan oldin tekshiruv kerak?</h4>
<p>Foreign key cheklovi <strong>bog'liq</strong> qatorlar mavjud bo'lganda o'chirishni avtomatik rad etadi — bu ma'lumotlar yaxlitligini saqlaydi, lekin xato xabari foydalanuvchi uchun tushunarsiz (xom SQL xatosi). Backend bu holatni <strong>oldindan</strong> tekshirib, tushunarli xabar bilan <code>400</code> qaytarishi kerak.</p>

<h4>5. status kodlar: 201, 400, 204 qachon ishlatiladi?</h4>
<p><code>201 Created</code> — yangi resurs (task) muvaffaqiyatli yaratilganda. <code>400 Bad Request</code> — foydalanuvchi so'rovi noto'g'ri (majburiy maydon yo'q, yoki bog'liq resurslar bor). <code>204 No Content</code> — o'chirish muvaffaqiyatli, lekin qaytariladigan ma'lumot yo'q.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-darsdagi ER sxema haqiqiy <code>CREATE TABLE</code> buyruqlariga aylantirildi</li>
<li>✅ <code>JOIN</code> ikkita bog'langan jadvalning ma'lumotini bitta so'rovda birlashtiradi</li>
<li>✅ Parametrlashtirilgan so'rovlar (<code>$1</code>, <code>$2</code>) SQL injection'dan himoya qiladi</li>
<li>✅ Foreign key cheklovi bog'liq qatorlar mavjud bo'lganda o'chirishni rad etadi</li>
<li>✅ O'chirishdan oldin bog'liqlikni tekshirib, tushunarli xato xabari qaytarish kerak</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 2-BOSQICH: Backend API - tasks va categories uchun CRUD
// ════════════════════════════════════════════════════════════════════

const express = require('express');
const pool = require('./db');
const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) GET /tasks - JOIN orqali category nomi bilan birga
// ─────────────────────────────────────────────────────────────────────

app.get('/tasks', async (req, res) => {
  const natija = await pool.query(`
    SELECT tasks.*, categories.nomi AS category_nomi
    FROM tasks
    JOIN categories ON tasks.category_id = categories.id
    ORDER BY tasks.yaratilgan_vaqt DESC
  `);
  res.json(natija.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 2) POST /tasks - validatsiya + parametrlashtirilgan so'rov
// ─────────────────────────────────────────────────────────────────────

app.post('/tasks', async (req, res) => {
  const { sarlavha, matn, category_id } = req.body;
  if (!sarlavha || !category_id) {
    return res.status(400).json({ xato: "'sarlavha' va 'category_id' majburiy" });
  }
  const natija = await pool.query(
    'INSERT INTO tasks (sarlavha, matn, category_id) VALUES ($1, $2, $3) RETURNING *',
    [sarlavha, matn, category_id]
  );
  res.status(201).json(natija.rows[0]);
});

// ─────────────────────────────────────────────────────────────────────
// 3) DELETE /categories/:id - bog'liq tasks tekshiruvi bilan
// ─────────────────────────────────────────────────────────────────────

app.delete('/categories/:id', async (req, res) => {
  const { id } = req.params;

  const bogliqTasks = await pool.query(
    'SELECT COUNT(*) FROM tasks WHERE category_id = $1', [id]
  );
  if (Number(bogliqTasks.rows[0].count) > 0) {
    return res.status(400).json({
      xato: "Bu kategoriyada vazifalar bor, avval ularni o'chiring yoki boshqa kategoriyaga ko'chiring"
    });
  }

  await pool.query('DELETE FROM categories WHERE id = $1', [id]);
  res.status(204).send();
});

app.listen(3000, () => console.log('TaskFlow API: http://localhost:3000'));

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - tekshiruvsiz o'chirish (izohda)
// ─────────────────────────────────────────────────────────────────────

// app.delete('/categories/:id', async (req, res) => {
//   const { id } = req.params;
//   await pool.query('DELETE FROM categories WHERE id = $1', [id]);   // tekshiruvsiz!
//   res.status(204).send();
// });
// ❌ Agar bog'liq tasks bo'lsa: foreign key constraint xatosi, 500 Internal Server Error
"""

L2_EX = [
    {
        "title": "GET /tasks'da JOIN nima uchun ishlatiladi?",
        "description": "GET /tasks endpoint'ida tasks va categories jadvallari orasida JOIN ishlatilishining sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumotlar bazasini tezroq ishga tushirish uchun",
            "Bitta so'rovda ham task, ham uning category nomini birga olish uchun",
            "categories jadvalini o'chirish uchun",
            "Faqat tasks sonini hisoblash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "tasks jadvalida faqat category_id (raqam) bor, nomi emas.",
        "explanation": "JOIN tasks va categories jadvallarini birlashtirib, bitta so'rovda ham task ma'lumotini, ham uning category nomini qaytaradi — bu har bir task uchun alohida so'rov yuborishning oldini oladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Parametrlashtirilgan so'rov ($1, $2) nima uchun ishlatiladi?",
        "description": "pool.query('INSERT ... VALUES ($1, $2, $3)', [sarlavha, matn, category_id]) yozuvida $1, $2, $3 nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun, ahamiyati yo'q",
            "Foydalanuvchi ma'lumotini xavfsiz, SQL injection'dan himoyalangan holda yuborish uchun",
            "So'rovni tezroq bajarish uchun",
            "Faqat raqamlar uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu foydalanuvchi kiritgan matnni to'g'ridan-to'g'ri SQL'ga \"yopishtirish\"dan farq qiladi.",
        "explanation": "Parametrlashtirilgan so'rovlar foydalanuvchi ma'lumotini alohida yuboradi, PostgreSQL uni hech qachon SQL buyrug'ining bir qismi sifatida emas, faqat qiymat sifatida talqin qiladi — bu SQL injection'dan himoya qiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Category o'chirish so'rovini to'g'ri tartibda joylang",
        "description": "DELETE /categories/:id to'g'ri (xavfsiz) ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "So'rov keladi: DELETE /categories/5",
            "Avval: SELECT COUNT(*) FROM tasks WHERE category_id=5 tekshiriladi",
            "Agar count > 0 bo'lsa, 400 xato qaytariladi va o'chirilmaydi",
            "Agar count 0 bo'lsa, DELETE FROM categories WHERE id=5 bajariladi",
        ],
        "correct_order": [
            "So'rov keladi: DELETE /categories/5",
            "Avval: SELECT COUNT(*) FROM tasks WHERE category_id=5 tekshiriladi",
            "Agar count > 0 bo'lsa, 400 xato qaytariladi va o'chirilmaydi",
            "Agar count 0 bo'lsa, DELETE FROM categories WHERE id=5 bajariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Yangi resurs yaratilganda qaytariladigan status kod",
        "description": "POST /tasks orqali yangi task muvaffaqiyatli yaratilganda qaysi HTTP status kod qaytarilishi kerak? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "201",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega tekshiruvsiz category o'chirish 500 xato beradi?",
        "description": (
            "Agar DELETE /categories/:id endpoint'i bog'liq tasks "
            "borligini oldindan tekshirmasdan to'g'ridan-to'g'ri DELETE "
            "so'rovini yuborsa, va shu categoryga bog'liq tasks mavjud "
            "bo'lsa, nega bu 500 Internal Server Error bilan tugaydi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "tasks jadvalidagi category_id ustuni categories jadvaliga "
            "REFERENCES orqali bog'langan foreign key. PostgreSQL bu "
            "cheklovni ma'lumotlar yaxlitligini saqlash uchun ishlatadi "
            "— agar biror category'ga hali ham bog'liq (uning id'siga "
            "ishora qiluvchi) tasks qatorlari mavjud bo'lsa, PostgreSQL "
            "o'sha category'ni o'chirishga umuman ruxsat bermaydi va "
            "\"foreign key constraint\" xatosini qaytaradi. Agar Express "
            "kodi bu xatoni oldindan tekshirib, o'zi boshqarmasa, bu "
            "xato qo'lga olinmagan holda to'g'ridan-to'g'ri 500 "
            "Internal Server Error sifatida foydalanuvchiga chiqib "
            "ketadi — bu esa nima uchun o'chira olmaganini tushuntirib "
            "bermaydi."
        ),
        "hint": "tasks.category_id ustuni categories jadvaliga qanday bog'langan, va bu bog'lanish o'chirishga qanday ta'sir qiladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "TaskFlow — Backend API (tasks + categories)",
    "task_description": (
        "1-bosqichdagi sxema asosida PostgreSQL jadvallarini yarating "
        "(users, categories, tasks) va Express'da tasks hamda categories "
        "uchun to'liq CRUD API quring. GET /tasks JOIN orqali category "
        "nomini ham qaytarishi, DELETE /categories/:id esa bog'liq tasks "
        "borligini tekshirishi shart."
    ),
    "task_requirements": (
        "• schema.sql: users, categories, tasks jadvallari to'g'ri foreign key'lar bilan\n"
        "• GET /tasks — JOIN orqali category_nomi bilan birga qaytaradi\n"
        "• POST /tasks — sarlavha va category_id validatsiya qilinadi, 201 qaytaradi\n"
        "• PUT /tasks/:id — bajarilgan holatini yangilaydi\n"
        "• DELETE /categories/:id — bog'liq tasks bo'lsa 400 xato qaytaradi, bo'lmasa o'chiradi\n"
        "• Barcha SQL so'rovlar parametrlashtirilgan ($1, $2, ...)\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Node.js, Express, PostgreSQL, pg (node-postgres)",
    "task_deadline_days": 5,
}


L3_TEXT = """\
<h2>3-bosqich: React frontend — 2-bosqichdagi API'ga ulanish</h2>

<pre class="mermaid">
flowchart LR
    REACT["React (localhost:3001)"] -->|fetch| API["Express API (localhost:3000)"]
    API -->|CORS header'siz| BLOCKED["Brauzer so'rovni BLOKLAYDI"]
    API -->|CORS header bilan| OK["Ma'lumot muvaffaqiyatli qaytadi"]
</pre>

<p>2-bosqichda tayyor bo'lgan backend API'ga endi <strong>React</strong> frontend orqali ulanamiz. React va Redux Toolkit kursida <code>createAsyncThunk</code>ni allaqachon o'rgangansiz — bu safar uni <strong>haqiqiy, o'zingiz yozgan</strong> backend bilan ishlatasiz, va frontend/backend turli portlarda ishlaganda yuzaga keladigan <strong>CORS</strong> muammosi bilan tanishasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — createAsyncThunk orqali haqiqiy API'dan ma'lumot olish</h4>
<pre><code>// frontend/src/features/tasksSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';   // ❗ .env orqali sozlanadi

export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);          // ❗ 2-bosqichdagi haqiqiy endpoint
  if (!javob.ok) throw new Error('Tasklarni olishda xato');
  return await javob.json();
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { royxat: [], holat: 'idle' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(tasklarniOlish.pending, (state) => { state.holat = 'yuklanmoqda'; })
      .addCase(tasklarniOlish.fulfilled, (state, action) => {
        state.holat = 'muvaffaqiyatli';
        state.royxat = action.payload;
      })
      .addCase(tasklarniOlish.rejected, (state) => { state.holat = 'xato'; });
  },
});

export default tasksSlice.reducer;</code></pre>

<h4>BLOKA 2 — component'da ishlatish</h4>
<pre><code>// frontend/src/components/TaskRoyxati.jsx
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { tasklarniOlish } from '../features/tasksSlice';

function TaskRoyxati() {
  const dispatch = useDispatch();
  const { royxat, holat } = useSelector((state) => state.tasks);

  useEffect(() => {
    dispatch(tasklarniOlish());                // ❗ component yuklanganda API'ga so'rov yuboradi
  }, [dispatch]);

  if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;

  return (
    <ul>
      {royxat.map((task) => (
        <li key={task.id}>{task.sarlavha} ({task.category_nomi})</li>
      ))}
    </ul>
  );
}</code></pre>

<h4>BLOKA 3 — backend'da CORS'ni yoqish</h4>
<pre><code>// backend/server.js
const cors = require('cors');
const app = express();

app.use(cors({
  origin: 'http://localhost:3001',   // ❗ FAQAT frontend manzilidan kelgan so'rovlarga ruxsat
}));
app.use(express.json());
// ... qolgan route'lar ...</code></pre>

<h3>🐛 Ataylab xato — backend'da CORS'ni sozlashni unutish</h3>
<pre><code>// backend/server.js - cors() ISHLATILMAGAN holda:
const app = express();
app.use(express.json());
app.get('/tasks', async (req, res) => { /* ... */ });

// React'da (localhost:3001) fetch('http://localhost:3000/tasks') chaqirilsa:
// ❌ Brauzer konsolida: Access to fetch at 'http://localhost:3000/tasks' from
//    origin 'http://localhost:3001' has been blocked by CORS policy
// (Network tabda so'rov "ketgan" ko'rinadi, lekin javob brauzer TOMONIDAN bloklanadi!)</code></pre>

<p><strong>Natija:</strong> brauzerlar <strong>Same-Origin Policy</strong> deb ataladigan xavfsizlik qoidasiga amal qiladi — standart holda bir <strong>origin</strong> (protokol+domen+port)dagi sahifa boshqa origin'ga so'rov yubora olsa ham, <strong>javobni o'qiy olmaydi</strong>, agar server buni aniq ruxsat bermasa. React (<code>localhost:3001</code>) va Express (<code>localhost:3000</code>) <strong>turli portlarda</strong> ishlagani uchun ular <strong>turli origin</strong> hisoblanadi. Backend <code>cors()</code> middleware orqali "bu origin'ga ruxsat beraman" deb <strong>aniq</strong> aytmasa, brauzer javobni JavaScript kodiga <strong>yetkazmaydi</strong> — bu server tomonidagi xato emas, balki brauzerning xavfsizlik mexanizmi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega API_URL .env orqali sozlanadi, kodga qattiq yozilmaydi?</h4>
<p>Development'da API <code>localhost:3000</code>da, lekin production'da (6-darsda) u butunlay boshqa domenda joylashgan bo'ladi. <code>.env</code> orqali sozlash — kodni o'zgartirmasdan, faqat environment o'zgaruvchisini almashtirib, turli muhitlarda (development/production) ishlatish imkonini beradi.</p>

<h4>2. createAsyncThunk'ning uch holati (pending/fulfilled/rejected) nima uchun kerak?</h4>
<p>Tarmoq so'rovi <strong>vaqt oladi</strong> va <strong>muvaffaqiyatsiz</strong> bo'lishi mumkin. <code>pending</code> — "yuklanmoqda" holatini ko'rsatish uchun, <code>fulfilled</code> — muvaffaqiyatli ma'lumotni saqlash uchun, <code>rejected</code> — xatoni foydalanuvchiga ko'rsatish uchun. Bu uchalasi birga foydalanuvchi tajribasini (loading spinner, xato xabari) to'g'ri boshqarish imkonini beradi.</p>

<h4>3. CORS nima va nega kerak?</h4>
<p>CORS (Cross-Origin Resource Sharing) — brauzerga <strong>boshqa origin</strong>dan kelgan javobni JavaScript kodiga o'qishga ruxsat berish mexanizmi. Server <code>Access-Control-Allow-Origin</code> header'ini yuborishi kerak — <code>cors()</code> middleware'i buni avtomatik qo'shadi.</p>

<h4>4. Nega CORS xatosi "server ishlamayapti" bilan chalkashtiriladi?</h4>
<p>Brauzerning Network tabida so'rov <strong>yuborilgan va server javob qaytargan</strong> ko'rinadi (status 200 bo'lishi ham mumkin) — lekin brauzer bu javobni React kodiga <strong>berishdan bosh tortadi</strong>. Bu boshlang'ich dasturchilarni chalg'itadi, chunki "server ishlamayapti" deb o'ylashadi, aslida muammo <strong>faqat</strong> CORS ruxsatida.</p>

<h4>5. origin: 'http://localhost:3001' nima uchun aniq ko'rsatiladi?</h4>
<p><code>cors({ origin: '...' })</code> orqali <strong>faqat</strong> ko'rsatilgan origin'dan kelgan so'rovlarga ruxsat beriladi — bu <code>cors()</code>ni hech qanday parametrsiz (barcha origin'larga ochiq) ishlatishdan <strong>xavfsizroq</strong>, ayniqsa production'da haqiqiy foydalanuvchi ma'lumotlari bilan ishlaganda.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>createAsyncThunk</code> haqiqiy backend API bilan ishlatildi — pending/fulfilled/rejected uch holati</li>
<li>✅ API manzili <code>.env</code> orqali sozlanadi, kodga qattiq yozilmaydi</li>
<li>✅ CORS — brauzerning Same-Origin Policy'siga asoslangan xavfsizlik mexanizmi</li>
<li>✅ Turli port — turli origin, va bu CORS ruxsatini talab qiladi</li>
<li>✅ CORS xatosi server emas, brauzer tomonidan bloklanadi (Network tabda "so'rov ketgan" ko'rinishi mumkin)</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 3-BOSQICH: React frontend - backend API'ga ulanish
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) frontend/src/features/tasksSlice.js
// ─────────────────────────────────────────────────────────────────────

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);
  if (!javob.ok) throw new Error('Tasklarni olishda xato');
  return await javob.json();
});

const tasksSlice = createSlice({
  name: 'tasks',
  initialState: { royxat: [], holat: 'idle' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(tasklarniOlish.pending, (state) => { state.holat = 'yuklanmoqda'; })
      .addCase(tasklarniOlish.fulfilled, (state, action) => {
        state.holat = 'muvaffaqiyatli';
        state.royxat = action.payload;
      })
      .addCase(tasklarniOlish.rejected, (state) => { state.holat = 'xato'; });
  },
});

export default tasksSlice.reducer;

// ─────────────────────────────────────────────────────────────────────
// 2) frontend/src/components/TaskRoyxati.jsx (izohda - JSX)
// ─────────────────────────────────────────────────────────────────────

// function TaskRoyxati() {
//   const dispatch = useDispatch();
//   const { royxat, holat } = useSelector((state) => state.tasks);
//
//   useEffect(() => {
//     dispatch(tasklarniOlish());
//   }, [dispatch]);
//
//   if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;
//
//   return (
//     <ul>
//       {royxat.map((task) => (
//         <li key={task.id}>{task.sarlavha} ({task.category_nomi})</li>
//       ))}
//     </ul>
//   );
// }

// ─────────────────────────────────────────────────────────────────────
// 3) backend/server.js - CORS'ni yoqish
// ─────────────────────────────────────────────────────────────────────

// const cors = require('cors');
// app.use(cors({ origin: 'http://localhost:3001' }));

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - CORS'ni unutish (izohda)
// ─────────────────────────────────────────────────────────────────────

// backend/server.js da cors() YO'Q holda:
// React'dan fetch('http://localhost:3000/tasks') chaqirilsa:
// ❌ Access to fetch at 'http://localhost:3000/tasks' from origin
//    'http://localhost:3001' has been blocked by CORS policy
"""

L3_EX = [
    {
        "title": "API_URL nega .env orqali sozlanadi?",
        "description": "process.env.REACT_APP_API_URL ishlatilishining asosiy sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun",
            "Development va production muhitlarida kodni o'zgartirmasdan turli API manzilini ishlatish uchun",
            "Faqat xavfsizlik uchun, boshqa sababi yo'q",
            "React'da bu majburiy sintaksis",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "6-bosqichda API butunlay boshqa domenda bo'ladi.",
        "explanation": "API manzilini .env orqali sozlash, kodni o'zgartirmasdan, faqat environment o'zgaruvchisini almashtirib turli muhitlarda (development/production) ishlatish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "CORS xatosi nima uchun yuzaga keladi?",
        "description": "React (localhost:3001) va Express (localhost:3000) orasida CORS xatosi nega paydo bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki Express server ishlamayapti",
            "Chunki ular turli port bilan turli origin hisoblanadi, va server aniq ruxsat bermasa brauzer javobni bloklaydi",
            "Chunki React fetch() ishlata olmaydi",
            "Chunki internet aloqasi yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu brauzerning xavfsizlik siyosati bilan bog'liq.",
        "explanation": "React va Express turli portlarda ishlagani uchun turli origin hisoblanadi. Brauzerning Same-Origin Policy'siga ko'ra, server aniq CORS ruxsati bermasa, brauzer javobni JavaScript kodiga yetkazmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "tasklarniOlish() dispatch qilinganda holatlarni tartiblang",
        "description": "dispatch(tasklarniOlish()) chaqirilgandan tortib, ma'lumot component'da ko'rinishigacha bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "pending holati - state.holat = 'yuklanmoqda' bo'ladi, 'Yuklanmoqda...' ko'rsatiladi",
            "fetch() backend'ga so'rov yuboradi",
            "fulfilled holati - kelgan ma'lumot state.royxat'ga saqlanadi",
            "Component qayta render bo'lib, tasklar ro'yxati ko'rsatiladi",
        ],
        "correct_order": [
            "pending holati - state.holat = 'yuklanmoqda' bo'ladi, 'Yuklanmoqda...' ko'rsatiladi",
            "fetch() backend'ga so'rov yuboradi",
            "fulfilled holati - kelgan ma'lumot state.royxat'ga saqlanadi",
            "Component qayta render bo'lib, tasklar ro'yxati ko'rsatiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CORS'ni yoqish uchun ishlatiladigan Express middleware'i",
        "description": "Backend'da boshqa origin'dan kelgan so'rovlarga ruxsat berish uchun ishlatiladigan npm paketi/middleware nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "cors",
        "hint": "app.use(___()) shaklida ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega CORS xatosi \"server ishlamayapti\" bilan chalkashtiriladi?",
        "description": (
            "Brauzerning Network tabida fetch('http://localhost:3000/tasks') "
            "so'rovi \"yuborilgan\" va hatto status 200 ko'rinishi mumkin, "
            "lekin baribir CORS xatosi chiqadi. Nega bu holat ko'pincha "
            "\"server ishlamayapti\" deb noto'g'ri tushuniladi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "CORS xatosida server so'rovni haqiqatan qabul qilib, "
            "javob ham qaytargan bo'lishi mumkin (shuning uchun Network "
            "tabida status 200 ko'rinishi mumkin) — muammo serverda emas, "
            "brauzerning o'zida. Brauzer Same-Origin Policy qoidasiga "
            "ko'ra, agar server javobida to'g'ri Access-Control-Allow-"
            "Origin header'i bo'lmasa, bu javobni JavaScript kodiga "
            "(masalan fetch()ning .then() qismiga) yetkazishni rad "
            "etadi. Boshlang'ich dasturchilar buni ko'pincha \"server "
            "ishlamayapti\" deb tushunishadi, chunki React tomonida "
            "ma'lumot kelmaydi, lekin aslida server to'g'ri ishlagan — "
            "muammo faqat brauzer va server orasidagi CORS ruxsatining "
            "yo'qligida."
        ),
        "hint": "CORS xatosida server so'rovga umuman javob QAYTARMAGANMI, yoki javob qaytargan-u brauzer uni blokladimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "TaskFlow — React frontend backend'ga ulangan",
    "task_description": (
        "React + Redux Toolkit'da tasksSlice yarating, createAsyncThunk "
        "orqali 2-bosqichdagi haqiqiy GET /tasks endpoint'idan ma'lumot "
        "oling va ro'yxat sifatida ko'rsating. Backend'da CORS'ni to'g'ri "
        "sozlang, .env orqali API manzilini boshqaring."
    ),
    "task_requirements": (
        "• frontend/src/features/tasksSlice.js: createAsyncThunk bilan tasklarniOlish\n"
        "• pending/fulfilled/rejected uch holati ham to'g'ri boshqarilgan (loading, ro'yxat, xato)\n"
        "• Component tasklar ro'yxatini category_nomi bilan birga ko'rsatadi\n"
        "• API manzili .env (REACT_APP_API_URL) orqali sozlangan, kodga qattiq yozilmagan\n"
        "• Backend'da cors() middleware to'g'ri origin bilan sozlangan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "React, Redux Toolkit, createAsyncThunk, cors (Express)",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Autentifikatsiya — JWT backend'da, login/himoya frontend'da</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /login"] --> JWT["JWT token yaratiladi"]
    JWT --> STORE["Frontend token'ni saqlaydi"]
    STORE --> REQ["Har bir keyingi so'rovga Authorization header qo'shiladi"]
    REQ -->|header yo'q| REJECT["401 Unauthorized"]
</pre>

<p>TaskFlow endi <strong>ko'p foydalanuvchili</strong> bo'lishi kerak — har bir foydalanuvchi faqat <strong>o'z</strong> tasklarini ko'rishi kerak. Buning uchun backend'da JWT autentifikatsiya, frontend'da esa login/register sahifalari va <strong>himoyalangan</strong> so'rovlarni quramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — backend: ro'yxatdan o'tish va JWT yaratish</h4>
<pre><code>// backend/routes/auth.js
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

router.post('/register', async (req, res) => {
  const { ism, email, parol } = req.body;
  const parol_hash = await bcrypt.hash(parol, 10);          // ❗ parol HECH QACHON ochiq saqlanmaydi
  const natija = await pool.query(
    'INSERT INTO users (ism, email, parol_hash) VALUES ($1, $2, $3) RETURNING id, ism, email',
    [ism, email, parol_hash]
  );
  res.status(201).json(natija.rows[0]);
});

router.post('/login', async (req, res) => {
  const { email, parol } = req.body;
  const natija = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  const user = natija.rows[0];
  if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
    return res.status(401).json({ xato: "Email yoki parol noto'g'ri" });
  }
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, ism: user.ism });
});</code></pre>

<h4>BLOKA 2 — backend: himoyalangan route (middleware)</h4>
<pre><code>// backend/middleware/auth.js
function autentifikatsiyaTalabQilish(req, res, next) {
  const authHeader = req.headers.authorization;             // ❗ "Bearer <token>" formatida kutiladi
  if (!authHeader) return res.status(401).json({ xato: 'Token yo\\'q' });

  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = payload.userId;                              // ❗ keyingi handler'lar uchun userId'ni beradi
    next();
  } catch {
    res.status(401).json({ xato: 'Token yaroqsiz' });
  }
}

// server.js
app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const natija = await pool.query(
    'SELECT * FROM tasks WHERE user_id = $1', [req.userId]   // ❗ faqat SHU foydalanuvchining tasklari
  );
  res.json(natija.rows);
});</code></pre>

<h4>BLOKA 3 — frontend: token'ni saqlash va har so'rovga qo'shish</h4>
<pre><code>// frontend/src/features/authSlice.js
export const kirish = createAsyncThunk('auth/kirish', async ({ email, parol }) => {
  const javob = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, parol }),
  });
  const data = await javob.json();
  localStorage.setItem('token', data.token);                  // ❗ token brauzerda saqlanadi
  return data;
});

// frontend/src/features/tasksSlice.js - HIMOYALANGAN so'rov
export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks`, {
    headers: { Authorization: `Bearer ${token}` },             // ❗ MAJBURIY - token shu yerda yuboriladi
  });
  return await javob.json();
});</code></pre>

<h3>🐛 Ataylab xato — Authorization header'ni qo'shishni unutish</h3>
<pre><code>// tasklarniOlish() Authorization header'siz:
export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
  const javob = await fetch(`${API_URL}/tasks`);   // ❌ Authorization header YO'Q!
  return await javob.json();
});

// Foydalanuvchi muvaffaqiyatli login qilgan, token localStorage'da bor -
// lekin so'rovda yuborilmagani uchun:
// ❌ 401 Unauthorized: "Token yo'q"
// (Foydalanuvchi "men kirdim-ku" deb hayron qoladi!)</code></pre>

<p><strong>Natija:</strong> token <code>localStorage</code>da saqlanishi <strong>o'zi</strong> hech narsani ta'minlamaydi — backend har bir <strong>himoyalangan</strong> so'rovda tokenni <code>Authorization</code> header orqali <strong>aynan shu so'rov ichida</strong> kutadi. Login muvaffaqiyatli bo'lib, token saqlangan bo'lsa ham, agar keyingi <code>fetch()</code> chaqiruvida bu header <strong>qo'shilmasa</strong>, backend foydalanuvchini "tanimaydi" va <code>401</code> qaytaradi — bu ko'plab boshlang'ich to'liq stack loyihalarida uchraydigan eng keng tarqalgan integratsiya xatolaridan biri.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega parol bcrypt bilan hash qilinadi, oddiy saqlanmaydi?</h4>
<p>Agar ma'lumotlar bazasi oshkor bo'lib qolsa, oddiy (plain-text) parollar darhol o'g'irlanadi. <code>bcrypt.hash()</code> parolni <strong>qaytarib bo'lmaydigan</strong> shaklga o'tkazadi — hatto baza oshkor bo'lsa ham, haqiqiy parolni tiklab bo'lmaydi. Kirishda <code>bcrypt.compare()</code> orqali kiritilgan parol hash bilan solishtiriladi.</p>

<h4>2. JWT nima va nima uchun kerak?</h4>
<p>JWT (JSON Web Token) — server tomonidan "imzolangan" ma'lumot bloki, odatda foydalanuvchi ID'sini o'z ichiga oladi. Server bu token'ni <strong>har safar</strong> tekshirib, uni kim yaratganini (imzo orqali) tasdiqlaydi — bu server tomonida session saqlamasdan, "stateless" autentifikatsiya qilish imkonini beradi.</p>

<h4>3. Middleware (<code>autentifikatsiyaTalabQilish</code>) nima qiladi?</h4>
<p>Bu middleware har bir himoyalangan route'dan <strong>oldin</strong> ishga tushadi: <code>Authorization</code> header'dan tokenni oladi, uni tekshiradi, va agar to'g'ri bo'lsa <code>req.userId</code>ni belgilab, keyingi handler'ga o'tkazadi. Bu har bir route ichida qo'lda token tekshirishning oldini oladi (2-darsdagi Node.js kursidan tanish naqsh).</p>

<h4>4. Nega <code>WHERE user_id = $1</code> muhim?</h4>
<p>Agar bu shart bo'lmasa, <code>GET /tasks</code> <strong>barcha</strong> foydalanuvchilarning tasklarini qaytarardi — bu jiddiy xavfsizlik va maxfiylik muammosi. <code>req.userId</code> (JWT'dan olingan) orqali filtrlash — har bir foydalanuvchi faqat <strong>o'ziga tegishli</strong> ma'lumotni ko'rishini ta'minlaydi.</p>

<h4>5. Nega Authorization header'siz 401 chiqadi?</h4>
<p>Backend'dagi <code>autentifikatsiyaTalabQilish</code> middleware'i <strong>har bir</strong> himoyalangan so'rovda <code>Authorization</code> header'ni qidiradi. Token brauzerda (<code>localStorage</code>da) saqlangan bo'lishi bu header <strong>avtomatik</strong> qo'shilishini anglatmaydi — dasturchi uni <strong>har bir</strong> himoyalangan <code>fetch()</code> chaqiruviga <strong>qo'lda</strong> qo'shishi shart. Bu qadam tashlab ketilsa, backend token'ni "yo'q" deb hisoblaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Parollar <code>bcrypt.hash()</code> bilan hash qilinadi, oddiy saqlanmaydi</li>
<li>✅ JWT — server imzolagan, foydalanuvchi ID'sini o'z ichiga olgan "stateless" token</li>
<li>✅ Middleware himoyalangan route'lardan oldin tokenni tekshiradi</li>
<li>✅ <code>WHERE user_id = $1</code> — har bir foydalanuvchi faqat o'z ma'lumotini ko'rishini ta'minlaydi</li>
<li>✅ Token saqlangan bo'lishi kifoya emas — uni har bir himoyalangan so'rovga Authorization header orqali qo'lda qo'shish kerak</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 4-BOSQICH: Autentifikatsiya - JWT backend'da, login frontend'da
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/routes/auth.js
// ─────────────────────────────────────────────────────────────────────

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

router.post('/register', async (req, res) => {
  const { ism, email, parol } = req.body;
  const parol_hash = await bcrypt.hash(parol, 10);
  const natija = await pool.query(
    'INSERT INTO users (ism, email, parol_hash) VALUES ($1, $2, $3) RETURNING id, ism, email',
    [ism, email, parol_hash]
  );
  res.status(201).json(natija.rows[0]);
});

router.post('/login', async (req, res) => {
  const { email, parol } = req.body;
  const natija = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  const user = natija.rows[0];
  if (!user || !(await bcrypt.compare(parol, user.parol_hash))) {
    return res.status(401).json({ xato: "Email yoki parol noto'g'ri" });
  }
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
  res.json({ token, ism: user.ism });
});

// ─────────────────────────────────────────────────────────────────────
// 2) backend/middleware/auth.js
// ─────────────────────────────────────────────────────────────────────

function autentifikatsiyaTalabQilish(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ xato: "Token yo'q" });

  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = payload.userId;
    next();
  } catch {
    res.status(401).json({ xato: 'Token yaroqsiz' });
  }
}

// app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
//   const natija = await pool.query('SELECT * FROM tasks WHERE user_id = $1', [req.userId]);
//   res.json(natija.rows);
// });

// ─────────────────────────────────────────────────────────────────────
// 3) frontend/src/features/authSlice.js (izohda - createAsyncThunk)
// ─────────────────────────────────────────────────────────────────────

// export const kirish = createAsyncThunk('auth/kirish', async ({ email, parol }) => {
//   const javob = await fetch(`${API_URL}/login`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ email, parol }),
//   });
//   const data = await javob.json();
//   localStorage.setItem('token', data.token);
//   return data;
// });

// export const tasklarniOlish = createAsyncThunk('tasks/olish', async () => {
//   const token = localStorage.getItem('token');
//   const javob = await fetch(`${API_URL}/tasks`, {
//     headers: { Authorization: `Bearer ${token}` },
//   });
//   return await javob.json();
// });

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - Authorization header'siz (izohda)
// ─────────────────────────────────────────────────────────────────────

// export const tasklarniOlishXato = createAsyncThunk('tasks/olish', async () => {
//   const javob = await fetch(`${API_URL}/tasks`);   // Authorization header YO'Q!
//   return await javob.json();
// });
// ❌ 401 Unauthorized: "Token yo'q"
"""

L4_EX = [
    {
        "title": "Nega parol bcrypt bilan hash qilinadi?",
        "description": "Foydalanuvchi paroli nima uchun bcrypt.hash() orqali saqlanadi, oddiy matn (plain-text) sifatida emas?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu ma'lumotlar bazasida joy tejaydi",
            "Baza oshkor bo'lib qolsa ham, haqiqiy parolni tiklab bo'lmasligi uchun",
            "Chunki PostgreSQL faqat hash qilingan matnni qabul qiladi",
            "Bu ixtiyoriy, ahamiyati yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu ma'lumotlar bazasi oshkor bo'lib qolgan holatni hisobga oladi.",
        "explanation": "bcrypt.hash() parolni qaytarib bo'lmaydigan shaklga o'tkazadi — hatto ma'lumotlar bazasi oshkor bo'lsa ham, haqiqiy parolni tiklab bo'lmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "WHERE user_id = $1 nima uchun muhim?",
        "description": "GET /tasks so'rovida WHERE user_id = $1 sharti bo'lmasa, nima muammo tug'iladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech qanday muammo bo'lmaydi, so'rov tezroq ishlaydi",
            "Barcha foydalanuvchilarning tasklari qaytariladi - jiddiy xavfsizlik/maxfiylik muammosi",
            "So'rov butunlay ishlamay qoladi",
            "Faqat admin foydalanuvchi ta'sirlanadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu ko'p foydalanuvchili tizimda ma'lumotlarni ajratish masalasi.",
        "explanation": "Bu shart bo'lmasa, GET /tasks barcha foydalanuvchilarning tasklarini qaytaradi — bu boshqa foydalanuvchining shaxsiy ma'lumotini oshkor qiladigan jiddiy xavfsizlik muammosi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Login jarayonini tartiblang",
        "description": "Foydalanuvchi login formasini yuborganidan, himoyalangan /tasks so'roviga qadar bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "POST /login email va parol bilan yuboriladi",
            "Backend bcrypt.compare() orqali parolni tekshiradi va JWT token yaratadi",
            "Frontend token'ni localStorage'ga saqlaydi",
            "Keyingi /tasks so'rovida token Authorization header orqali yuboriladi",
        ],
        "correct_order": [
            "POST /login email va parol bilan yuboriladi",
            "Backend bcrypt.compare() orqali parolni tekshiradi va JWT token yaratadi",
            "Frontend token'ni localStorage'ga saqlaydi",
            "Keyingi /tasks so'rovida token Authorization header orqali yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Tokenni yuborish uchun ishlatiladigan HTTP header",
        "description": "Frontend himoyalangan so'rovga JWT tokenni qaysi HTTP header orqali yuboradi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "Authorization",
        "hint": "Odatda \"Bearer <token>\" formatida yuboriladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Authorization header'siz 401 xato chiqadi?",
        "description": (
            "Foydalanuvchi muvaffaqiyatli login qilgan, token "
            "localStorage'da saqlangan, lekin tasklarniOlish() "
            "funksiyasida Authorization header qo'shilmagan. Nega bu "
            "holda backend baribir 401 Unauthorized qaytaradi, garchi "
            "foydalanuvchi \"kirgan\" bo'lsa ham? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Token localStorage'da saqlangan bo'lishi o'zi hech narsani "
            "ta'minlamaydi — bu shunchaki brauzerda saqlangan matn. "
            "Backend'dagi autentifikatsiyaTalabQilish middleware'i har "
            "bir himoyalangan so'rovda tokenni aynan Authorization "
            "header orqali, o'sha so'rovning o'zida qidiradi. Agar "
            "fetch() chaqiruvida bu header qo'lda qo'shilmagan bo'lsa, "
            "token backend'ga umuman yetib bormaydi — backend uchun bu "
            "\"token berilmagan\" so'rov bilan bir xil, shuning uchun u "
            "401 xatosini qaytaradi, garchi foydalanuvchi avval "
            "muvaffaqiyatli login qilgan va token brauzerda mavjud "
            "bo'lsa ham."
        ),
        "hint": "Token localStorage'da saqlanishi, uning avtomatik ravishda so'rovga QO'SHILISHINI ham anglatadimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "TaskFlow — JWT autentifikatsiya",
    "task_description": (
        "Backend'da /register va /login endpoint'larini JWT bilan quring, "
        "parolni bcrypt orqali hash qiling. Himoyalangan route'lar uchun "
        "middleware yozing va GET /tasks'ni faqat joriy foydalanuvchining "
        "tasklarini qaytaradigan qiling. Frontend'da login/register "
        "formalarini va tokenni har bir himoyalangan so'rovga qo'shishni "
        "amalga oshiring."
    ),
    "task_requirements": (
        "• POST /register — parolni bcrypt.hash() bilan saqlaydi\n"
        "• POST /login — bcrypt.compare() orqali tekshiradi, JWT token qaytaradi\n"
        "• autentifikatsiyaTalabQilish middleware — Authorization header'ni tekshiradi\n"
        "• GET /tasks — WHERE user_id = $1 orqali faqat joriy foydalanuvchi tasklarini qaytaradi\n"
        "• Frontend: login/register formalari, token localStorage'da saqlanadi\n"
        "• Barcha himoyalangan so'rovlarga Authorization header qo'shilgan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Node.js, Express, JWT (jsonwebtoken), bcrypt, React",
    "task_deadline_days": 4,
}


L5_TEXT = """\
<h2>5-bosqich: Qidiruv va filtrlash — to'liq stack funksiya</h2>

<pre class="mermaid">
flowchart LR
    INPUT["Foydalanuvchi yozadi: 'a'"] --> REQ1["So'rov 1 yuboriladi"]
    INPUT --> INPUT2["Foydalanuvchi davom etadi: 'al'"] --> REQ2["So'rov 2 yuboriladi"]
    REQ2 -->|tezroq qaytadi| SHOW2["'al' natijasi ko'rsatiladi"]
    REQ1 -->|sekinroq qaytadi| SHOW1["ESKI 'a' natijasi ustidan yozadi - XATO!"]
</pre>

<p>Bu bosqichda backend'ga qidiruv/filtr query parametrlarini, frontend'ga esa qidiruv maydonini qo'shamiz — bu <strong>haqiqiy</strong> full-stack funksiya: backend so'rovi <strong>va</strong> frontend holati birga to'g'ri ishlashi kerak.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — backend: query parametrlari orqali qidiruv va filtr</h4>
<pre><code>app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const { qidiruv, category_id, sahifa = 1 } = req.query;    // ❗ ?qidiruv=...&category_id=...&sahifa=...
  const sahifaHajmi = 10;
  const offset = (sahifa - 1) * sahifaHajmi;

  let sqlSorov = 'SELECT tasks.*, categories.nomi AS category_nomi FROM tasks JOIN categories ON tasks.category_id = categories.id WHERE tasks.user_id = $1';
  const params = [req.userId];

  if (qidiruv) {
    params.push(`%${qidiruv}%`);
    sqlSorov += ` AND tasks.sarlavha ILIKE $${params.length}`;   // ❗ ILIKE - katta-kichik harfga sezgir emas
  }
  if (category_id) {
    params.push(category_id);
    sqlSorov += ` AND tasks.category_id = $${params.length}`;
  }
  params.push(sahifaHajmi, offset);
  sqlSorov += ` ORDER BY tasks.yaratilgan_vaqt DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;

  const natija = await pool.query(sqlSorov, params);
  res.json(natija.rows);
});</code></pre>

<h4>BLOKA 2 — frontend: qidiruv maydoni va debounce</h4>
<pre><code>import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { tasklarniOlish } from '../features/tasksSlice';

function QidiruvMaydoni() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  useEffect(() => {
    const timerId = setTimeout(() => {                 // ❗ debounce - foydalanuvchi yozishni TO'XTATGANDA so'rov yuboradi
      dispatch(tasklarniOlish({ qidiruv: matn }));
    }, 400);                                             // ❗ 400ms kutadi - har harf uchun emas!

    return () => clearTimeout(timerId);                 // ❗ tozalash - eski timer bekor qilinadi
  }, [matn, dispatch]);

  return <input value={matn} onChange={(e) => setMatn(e.target.value)} placeholder="Qidirish..." />;
}</code></pre>

<h4>BLOKA 3 — createAsyncThunk'ga parametr uzatish</h4>
<pre><code>export const tasklarniOlish = createAsyncThunk('tasks/olish', async ({ qidiruv, category_id } = {}) => {
  const params = new URLSearchParams();
  if (qidiruv) params.append('qidiruv', qidiruv);
  if (category_id) params.append('category_id', category_id);

  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await javob.json();
});</code></pre>

<h3>🐛 Ataylab xato — debounce'siz har harfda so'rov yuborish (race condition)</h3>
<pre><code>// debounce YO'Q holda:
function QidiruvMaydoniXato() {
  const [matn, setMatn] = useState('');
  const dispatch = useDispatch();

  const onChange = (e) => {
    setMatn(e.target.value);
    dispatch(tasklarniOlish({ qidiruv: e.target.value }));   // ❌ HAR bir harfda darhol so'rov!
  };

  return <input value={matn} onChange={onChange} />;
}

// Foydalanuvchi "a" keyin tez "al" deb yozsa:
// - "a" uchun so'rov 1 yuboriladi (sekinroq javob qaytishi mumkin)
// - "al" uchun so'rov 2 yuboriladi (tezroq javob qaytishi mumkin)
// Agar so'rov 1 KEYINROQ qaytsa - u "al" natijasini "a" natijasi bilan
// ALMASHTIRIB QO'YADI! Foydalanuvchi "al" yozgan, lekin "a" natijasini ko'radi.</code></pre>

<p><strong>Natija:</strong> tarmoq so'rovlari <strong>yuborilgan tartibda</strong> qaytishi kafolatlanmaydi. Agar har harfda alohida so'rov yuborilsa, oldinroq yuborilgan (lekin sekinroq bajarilgan) so'rov <strong>keyinroq</strong> qaytib, yangiroq natijani <strong>eskisi bilan almashtirib qo'yishi</strong> mumkin — bu <strong>race condition</strong> deb ataladi. <strong>Debounce</strong> (foydalanuvchi yozishni to'xtatgandan keyin biroz kutib, keyin so'rov yuborish) bu muammoning oldini oladi, chunki oraliq holatlar uchun umuman so'rov yuborilmaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. ILIKE va LIKE orasidagi farq</h4>
<p><code>LIKE</code> katta-kichik harfga <strong>sezgir</strong> (masalan <code>"Python"</code> <code>"python"</code>ga mos kelmaydi). PostgreSQL'ning <code>ILIKE</code>si esa katta-kichik harfga <strong>sezgir emas</strong> — foydalanuvchi qidiruvi uchun bu odatda kutilgan xatti-harakat.</p>

<h4>2. LIMIT/OFFSET (pagination) nima uchun kerak?</h4>
<p>Agar foydalanuvchida minglab task bo'lsa, ularning <strong>barchasini</strong> bir so'rovda qaytarish sekin va xotira talab qiluvchi bo'lardi. <code>LIMIT</code> — bir sahifada nechta natija qaytarishni, <code>OFFSET</code> — nechtasini "o'tkazib yuborish"ni belgilaydi — bu <strong>sahifalash</strong> (pagination) imkonini beradi.</p>

<h4>3. Debounce nima va nega kerak?</h4>
<p>Debounce — foydalanuvchi <strong>yozishni to'xtatgandan</strong> keyin (masalan 400ms) so'rov yuborish texnikasi. <code>useEffect</code>dagi <code>setTimeout</code> va uni <code>clearTimeout</code> bilan tozalash — har yangi harf kiritilganda oldingi "kutish"ni bekor qilib, yangisini boshlaydi, shunda faqat foydalanuvchi <strong>haqiqatan to'xtagandan</strong> keyin bitta so'rov yuboriladi.</p>

<h4>4. Race condition nima?</h4>
<p>Race condition — ikkita (yoki undan ortiq) parallel jarayonning natijasi <strong>ularning tugash tartibiga</strong> bog'liq bo'lgan, va bu tartib kafolatlanmagan holat. Bu yerda: ikkita tarmoq so'rovi <strong>turli tezlikda</strong> qaytishi mumkin, va agar kod "oxirgi qaytgan javobni" emas, balki "oxirgi <strong>kelgan</strong> javobni" ko'rsatsa, natija foydalanuvchi kutgan holatga mos kelmasligi mumkin.</p>

<h4>5. Nega debounce race condition'ni kamaytiradi?</h4>
<p>Debounce bilan, foydalanuvchi tez yozayotganda oraliq holatlar (masalan <code>"a"</code>, <code>"al"</code>) uchun <strong>umuman so'rov yuborilmaydi</strong> — faqat foydalanuvchi to'xtagandan keyingi <strong>yakuniy</strong> qiymat uchun bitta so'rov ketadi. Bu yuboriladigan so'rovlar sonini keskin kamaytiradi, shu bilan race condition ehtimolini ham kamaytiradi (garchi to'liq yo'q qilmasa ham — buning uchun so'rovlarni "bekor qilish" (AbortController) kabi qo'shimcha texnikalar kerak bo'ladi).</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Backend'da query parametrlari (<code>?qidiruv=...&category_id=...</code>) orqali qidiruv/filtr/pagination</li>
<li>✅ <code>ILIKE</code> — katta-kichik harfga sezgir bo'lmagan qidiruv</li>
<li>✅ <code>LIMIT</code>/<code>OFFSET</code> — sahifalash (pagination) mexanizmi</li>
<li>✅ Debounce — foydalanuvchi to'xtagandan keyin so'rov yuborish, ortiqcha so'rovlarni kamaytiradi</li>
<li>✅ Race condition — parallel so'rovlarning noaniq tartibda qaytishi natijasida yuzaga keladigan xato</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 5-BOSQICH: Qidiruv va filtrlash - to'liq stack funksiya
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Backend - query parametrlari orqali qidiruv/filtr/pagination
// ─────────────────────────────────────────────────────────────────────

app.get('/tasks', autentifikatsiyaTalabQilish, async (req, res) => {
  const { qidiruv, category_id, sahifa = 1 } = req.query;
  const sahifaHajmi = 10;
  const offset = (sahifa - 1) * sahifaHajmi;

  let sqlSorov = 'SELECT tasks.*, categories.nomi AS category_nomi FROM tasks JOIN categories ON tasks.category_id = categories.id WHERE tasks.user_id = $1';
  const params = [req.userId];

  if (qidiruv) {
    params.push(`%${qidiruv}%`);
    sqlSorov += ` AND tasks.sarlavha ILIKE $${params.length}`;
  }
  if (category_id) {
    params.push(category_id);
    sqlSorov += ` AND tasks.category_id = $${params.length}`;
  }
  params.push(sahifaHajmi, offset);
  sqlSorov += ` ORDER BY tasks.yaratilgan_vaqt DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;

  const natija = await pool.query(sqlSorov, params);
  res.json(natija.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 2) Frontend - qidiruv maydoni debounce bilan (izohda - JSX)
// ─────────────────────────────────────────────────────────────────────

// function QidiruvMaydoni() {
//   const [matn, setMatn] = useState('');
//   const dispatch = useDispatch();
//
//   useEffect(() => {
//     const timerId = setTimeout(() => {
//       dispatch(tasklarniOlish({ qidiruv: matn }));
//     }, 400);
//
//     return () => clearTimeout(timerId);
//   }, [matn, dispatch]);
//
//   return <input value={matn} onChange={(e) => setMatn(e.target.value)} placeholder="Qidirish..." />;
// }

// ─────────────────────────────────────────────────────────────────────
// 3) createAsyncThunk'ga parametr uzatish
// ─────────────────────────────────────────────────────────────────────

export const tasklarniOlish = createAsyncThunk('tasks/olish', async ({ qidiruv, category_id } = {}) => {
  const params = new URLSearchParams();
  if (qidiruv) params.append('qidiruv', qidiruv);
  if (category_id) params.append('category_id', category_id);

  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/tasks?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await javob.json();
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - debounce'siz, har harfda so'rov (izohda)
// ─────────────────────────────────────────────────────────────────────

// function QidiruvMaydoniXato() {
//   const [matn, setMatn] = useState('');
//   const dispatch = useDispatch();
//   const onChange = (e) => {
//     setMatn(e.target.value);
//     dispatch(tasklarniOlish({ qidiruv: e.target.value }));   // har harfda darhol so'rov!
//   };
//   return <input value={matn} onChange={onChange} />;
// }
// ❌ Tez yozganda, sekinroq javob tezroq javobning ustidan yozib qo'yishi mumkin (race condition)
"""

L5_EX = [
    {
        "title": "ILIKE va LIKE farqi",
        "description": "PostgreSQL'da ILIKE va LIKE orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "ILIKE tezroq ishlaydi, boshqa farqi yo'q",
            "ILIKE katta-kichik harfga sezgir emas, LIKE esa sezgir",
            "LIKE faqat raqamlar uchun ishlatiladi",
            "Ular butunlay bir xil",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Foydalanuvchi qidiruvi uchun qaysi biri qulayroq?",
        "explanation": "ILIKE katta-kichik harfga sezgir emas (case-insensitive), oddiy LIKE esa sezgir — foydalanuvchi qidiruvida odatda ILIKE ishlatiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Debounce nima uchun ishlatiladi?",
        "description": "Qidiruv maydonida debounce texnikasi (setTimeout + clearTimeout) nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun",
            "Foydalanuvchi yozishni to'xtatgandan keyin bitta so'rov yuborish, ortiqcha so'rovlarni kamaytirish uchun",
            "Backend'ni tezroq ishlashga majburlash uchun",
            "Faqat CSS animatsiyalar uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Har harf uchun emas, faqat foydalanuvchi to'xtaganda.",
        "explanation": "Debounce foydalanuvchi yozishni to'xtatgandan keyin (masalan 400ms) bitta so'rov yuborish orqali, har harf uchun alohida so'rov yuborilishining oldini oladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Debounce ishlash jarayonini tartiblang",
        "description": "Foydalanuvchi qidiruv maydoniga tez-tez harf kiritganda debounce qanday ishlashini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi 'a' harfini kiritadi, setTimeout(400ms) boshlanadi",
            "Foydalanuvchi darhol 'l' harfini qo'shadi - eski timer clearTimeout bilan bekor qilinadi, yangi timer boshlanadi",
            "Foydalanuvchi yozishni to'xtatadi",
            "400ms o'tgach, faqat YAKUNIY qiymat ('al') uchun bitta so'rov yuboriladi",
        ],
        "correct_order": [
            "Foydalanuvchi 'a' harfini kiritadi, setTimeout(400ms) boshlanadi",
            "Foydalanuvchi darhol 'l' harfini qo'shadi - eski timer clearTimeout bilan bekor qilinadi, yangi timer boshlanadi",
            "Foydalanuvchi yozishni to'xtatadi",
            "400ms o'tgach, faqat YAKUNIY qiymat ('al') uchun bitta so'rov yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Sahifalash uchun ishlatiladigan SQL kalit so'zlari",
        "description": "PostgreSQL'da sahifalash (pagination) uchun ishlatiladigan ikkita kalit so'zni yozing (masalan: LIMIT OFFSET).",
        "exercise_type": "text_input",
        "expected_answer": "LIMIT OFFSET",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega debounce'siz race condition yuzaga kelishi mumkin?",
        "description": (
            "Agar qidiruv maydoni har harf kiritilganda darhol so'rov "
            "yuborsa (debounce'siz), foydalanuvchi tez 'a' keyin 'al' "
            "deb yozganda, nega ekranda 'al' o'rniga 'a' natijasi "
            "ko'rinib qolishi mumkin? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Tarmoq so'rovlari yuborilgan tartibda qaytishi kafolatlanmaydi "
            "— har bir so'rovning serverda qayta ishlanish vaqti va "
            "tarmoq kechikishi turlicha bo'lishi mumkin. 'a' uchun "
            "so'rov birinchi yuborilgan bo'lsa-da, u serverda sekinroq "
            "qayta ishlangan bo'lishi mumkin, shuning uchun keyinroq "
            "yuborilgan 'al' so'rovining javobi UNDAN OLDIN qaytishi "
            "mumkin. Agar kod har bir kelgan javobni state'ga to'g'ridan-"
            "to'g'ri yozib qo'ysa (qaysi so'rovga tegishli ekanini "
            "tekshirmasdan), keyinroq kelgan 'a' javobi avvalroq kelgan "
            "'al' javobini ustidan yozib qo'yadi — bu esa foydalanuvchi "
            "haqiqatda 'al' deb qidirgan bo'lsa-da, ekranda 'a' bo'yicha "
            "natijalarni ko'rishiga olib keladi."
        ),
        "hint": "Ikkita parallel tarmoq so'rovi HAR DOIM yuborilgan tartibda javob qaytaradimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "TaskFlow — Qidiruv, filtr va sahifalash",
    "task_description": (
        "GET /tasks endpoint'iga qidiruv (sarlavha bo'yicha ILIKE), category "
        "bo'yicha filtr va sahifalash (LIMIT/OFFSET) query parametrlarini "
        "qo'shing. Frontend'da debounce bilan ishlaydigan qidiruv maydoni "
        "va category bo'yicha filtr dropdown yarating."
    ),
    "task_requirements": (
        "• GET /tasks — ?qidiruv=...&category_id=...&sahifa=... query parametrlarini qo'llab-quvvatlaydi\n"
        "• Qidiruv ILIKE orqali, katta-kichik harfga sezgir emas\n"
        "• Sahifalash LIMIT/OFFSET orqali amalga oshirilgan\n"
        "• Frontend'da qidiruv maydoni 400ms debounce bilan ishlaydi (har harfda emas)\n"
        "• Category bo'yicha filtr dropdown mavjud\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Node.js, Express, PostgreSQL (ILIKE/LIMIT/OFFSET), React, Redux Toolkit",
    "task_deadline_days": 4,
}


L6_TEXT = """\
<h2>6-bosqich (CAPSTONE yakuni): Polish va Deploy</h2>

<pre class="mermaid">
flowchart LR
    LOCAL["Lokal: localhost:3000/3001"] --> DEPLOY["Deploy: haqiqiy domenlar"]
    DEPLOY --> CORS_CHECK{"CORS origin production'ga sozlanganmi?"}
    CORS_CHECK -->|yo'q| FAIL["Production'da CORS xatosi - lokalda ishlagan bo'lsa ham!"]
    CORS_CHECK -->|ha| LIVE["TaskFlow jonli ishlaydi"]
</pre>

<p>TaskFlow'ning barcha funksiyalari tayyor — endi uni <strong>haqiqiy internetga</strong> chiqaramiz. Bu bosqich kursning yakuniy CAPSTONE topshirig'i: loyiha <strong>deploy qilingan, jonli havola bilan</strong> topshirilishi kerak.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — production uchun environment o'zgaruvchilari</h4>
<pre><code># backend/.env.example (haqiqiy qiymatlarsiz, faqat namuna)
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
JWT_SECRET=juda-uzun-tasodifiy-maxfiy-satr
PORT=3000
FRONTEND_URL=https://taskflow-frontend.vercel.app   # ❗ production frontend manzili

# frontend/.env.production
REACT_APP_API_URL=https://taskflow-backend.onrender.com   # ❗ production backend manzili</code></pre>

<h4>BLOKA 2 — CORS'ni production manziliga moslashtirish</h4>
<pre><code>// backend/server.js
const cors = require('cors');

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',   // ❗ environment'ga qarab almashadi
}));

// Development'da: FRONTEND_URL sozlanmagan -> localhost:3001 ishlatiladi
// Production'da: FRONTEND_URL=https://taskflow-frontend.vercel.app -> shu manzilga ruxsat</code></pre>

<h4>BLOKA 3 — deploy qadamlari va yakuniy README</h4>
<pre><code># Backend deploy (masalan Render/Railway):
# 1. GitHub repo'ni platformaga ulash
# 2. Environment o'zgaruvchilarini (.env'dagilarni) platforma panelida sozlash
# 3. PostgreSQL ma'lumotlar bazasini ham shu platformada yaratish
# 4. Deploy - backend https://taskflow-backend.onrender.com da ishga tushadi

# Frontend deploy (masalan Vercel/Netlify):
# 1. GitHub repo'ni ulash, root directory'ni frontend/ deb ko'rsatish
# 2. REACT_APP_API_URL'ni production backend manziliga sozlash
# 3. Deploy - frontend https://taskflow-frontend.vercel.app da ishga tushadi

# README.md yakuniy holati:
## Jonli havola
- Frontend: https://taskflow-frontend.vercel.app
- Backend API: https://taskflow-backend.onrender.com

## Holat
- [x] Barcha 6 bosqich yakunlandi ✅</code></pre>

<h3>🐛 Ataylab xato — CORS origin'ni production'ga yangilashni unutish</h3>
<pre><code>// backend/server.js - hali ham qattiq yozilgan localhost bilan:
app.use(cors({
  origin: 'http://localhost:3001',   // ❌ productionda BU MANZIL MAVJUD EMAS!
}));

// Deploy qilingandan keyin:
// - Backend: https://taskflow-backend.onrender.com (ishlaydi)
// - Frontend: https://taskflow-frontend.vercel.app (ochiladi)
// - Frontend backend'ga so'rov yuborganda:
// ❌ CORS xatosi - chunki backend hali ham FAQAT localhost:3001'ga ruxsat beradi,
//    https://taskflow-frontend.vercel.app'ga EMAS!</code></pre>

<p><strong>Natija:</strong> lokal muhitda <strong>mukammal</strong> ishlagan CORS sozlamasi, agar <code>origin</code> qiymati <strong>qattiq</strong> (<code>localhost:3001</code>) yozilgan bo'lsa, production'da <strong>ishlamay qoladi</strong> — chunki deploy qilingan frontend butunlay boshqa domenda (<code>https://taskflow-frontend.vercel.app</code>) joylashgan, backend esa hali ham faqat <code>localhost</code>ga ruxsat beradi. Bu "lokalda ishlaydi, productionda ishlamaydi" degan klassik deploy muammosi — yechimi: <code>origin</code>ni <strong>environment o'zgaruvchisi</strong> orqali sozlash (3-darsdagi <code>.env</code> tamoyilining davomi).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega .env.example yaratiladi, .env emas?</h4>
<p><code>.env</code> haqiqiy maxfiy qiymatlarni (parollar, tokenlar) o'z ichiga oladi va <strong>hech qachon</strong> repo'ga qo'shilmasligi kerak (1-darsdagi <code>.gitignore</code>ni eslang). <code>.env.example</code> esa faqat <strong>qaysi</strong> o'zgaruvchilar kerakligini ko'rsatadi (qiymatlarsiz) — boshqa dasturchi (yoki baholovchi) loyihani klonlaganda qaysi <code>.env</code> yaratishi kerakligini biladi.</p>

<h4>2. Nega backend va frontend alohida platformalarga deploy qilinadi?</h4>
<p>Backend (Node.js server + PostgreSQL) va frontend (statik React build) <strong>turli xil</strong> resurslarni talab qiladi. Render/Railway kabi platformalar backend uchun, Vercel/Netlify esa statik frontend uchun ixtisoslashgan — shuning uchun ko'pincha ularni alohida joylashtirish qulayroq.</p>

<h4>3. Nega CORS origin environment orqali sozlanishi kerak?</h4>
<p>Development va production muhitida frontend manzili <strong>butunlay boshqa</strong> — <code>localhost:3001</code> va <code>https://taskflow-frontend.vercel.app</code>. Agar bu qiymat kodga qattiq yozilsa, ikkala muhitda ham to'g'ri ishlashi <strong>mumkin emas</strong>. Environment o'zgaruvchisi orqali sozlash — bir xil kod ikkala muhitda ham to'g'ri ishlashini ta'minlaydi.</p>

<h4>4. Nega bu "lokalda ishlaydi, productionda ishlamaydi" muammosi keng tarqalgan?</h4>
<p>Dasturchi ko'pincha faqat <strong>lokal</strong> muhitda sinab ko'radi, va u yerda hamma narsa (CORS, API manzili) to'g'ri ishlaydi, chunki barcha qiymatlar <code>localhost</code>ga mos. Deploy qilingandan keyingina, <strong>haqiqiy</strong> domenlar bilan sinab ko'rilganda, qattiq yozilgan <code>localhost</code> qiymatlari muammo ekanligi ma'lum bo'ladi.</p>

<h4>5. Yakuniy README nima uchun muhim?</h4>
<p>Bu — loyihaning "yakuniy taqdimoti": jonli havolalar (frontend, backend), texnologiyalar, va barcha 6 bosqichning bajarilganligini ko'rsatuvchi checklist. Bu baholovchi (yoki kelajakdagi ish beruvchi) uchun loyihani <strong>tezda</strong> tushunish va sinab ko'rish imkonini beradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>.env.example</code> — qaysi environment o'zgaruvchilari kerakligini ko'rsatadi, maxfiy qiymatlarsiz</li>
<li>✅ Backend va frontend odatda alohida, ixtisoslashgan platformalarga deploy qilinadi</li>
<li>✅ CORS origin environment o'zgaruvchisi orqali sozlanishi kerak, qattiq yozilmasligi kerak</li>
<li>✅ "Lokalda ishlaydi, productionda ishlamaydi" — odatda qattiq yozilgan localhost qiymatlari sababli</li>
<li>✅ Yakuniy README — loyihaning jonli holatini va bajarilgan ishni ko'rsatadi</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz TaskFlow'ni 1-bosqichdagi bo'sh repo'dan boshlab, DB sxemasi, backend API, React frontend, autentifikatsiya, qidiruv/filtr va nihoyat <strong>haqiqiy deploy</strong>gacha qurdingiz. Bu — React va Node.js/Express kurslarida alohida o'rgangan hamma narsani <strong>bitta, ishlaydigan, jonli loyiha</strong>da birlashtirish tajribasi edi.</p>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 6-BOSQICH (CAPSTONE YAKUNI): Polish va Deploy
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/.env.example (izohda - namuna, haqiqiy qiymatsiz)
// ─────────────────────────────────────────────────────────────────────

// DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
// JWT_SECRET=juda-uzun-tasodifiy-maxfiy-satr
// PORT=3000
// FRONTEND_URL=https://taskflow-frontend.vercel.app

// frontend/.env.production
// REACT_APP_API_URL=https://taskflow-backend.onrender.com

// ─────────────────────────────────────────────────────────────────────
// 2) backend/server.js - CORS'ni environment orqali sozlash
// ─────────────────────────────────────────────────────────────────────

const cors = require('cors');
const express = require('express');
const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
}));

app.listen(process.env.PORT || 3000, () => {
  console.log('TaskFlow API ishga tushdi');
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - CORS origin'ni qattiq yozish (izohda)
// ─────────────────────────────────────────────────────────────────────

// app.use(cors({
//   origin: 'http://localhost:3001',   // production'da bu manzil mavjud emas!
// }));
// ❌ Production'da: CORS xatosi, chunki frontend butunlay boshqa domenda
"""

L6_EX = [
    {
        "title": ".env.example nima uchun kerak?",
        "description": ".env.example fayli asosan nima uchun repo'ga qo'shiladi (haqiqiy .env emas)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki .env repo'ga qo'shilishi mumkin emas, .env.example esa mumkin",
            "Qaysi environment o'zgaruvchilari kerakligini (qiymatlarsiz) ko'rsatish uchun",
            "Ikkalasi bir xil, farqi yo'q",
            "Faqat test uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "1-darsdagi .gitignore mavzusini eslang.",
        "explanation": ".env.example haqiqiy maxfiy qiymatlarsiz, faqat qaysi environment o'zgaruvchilari kerakligini ko'rsatadi — boshqa dasturchi loyihani klonlaganda qaysi .env yaratishi kerakligini biladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "CORS origin nega environment orqali sozlanishi kerak?",
        "description": "Backend'da cors({ origin: process.env.FRONTEND_URL }) nega qattiq yozilgan origin'dan yaxshiroq?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu kodni qisqartiradi",
            "Development va production'da frontend manzili butunlay boshqa bo'lgani uchun, bir xil kod ikkalasida ham to'g'ri ishlashi uchun",
            "Chunki environment o'zgaruvchilari tezroq ishlaydi",
            "Bu majburiy Express qoidasi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "localhost:3001 va https://taskflow-frontend.vercel.app - ikkalasi ham to'g'ri bo'lishi kerak.",
        "explanation": "Development va production muhitida frontend manzili butunlay boshqa bo'lgani uchun, CORS origin'ni environment o'zgaruvchisi orqali sozlash bir xil kodni ikkala muhitda ham to'g'ri ishlatish imkonini beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TaskFlow deploy jarayonini tartiblang",
        "description": "Backend va frontend'ni deploy qilish umumiy jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "GitHub repo backend platformasiga (masalan Render) ulanadi",
            "Environment o'zgaruvchilari (.env'dagilar) platforma panelida sozlanadi",
            "Backend deploy qilinib, haqiqiy domen (masalan onrender.com) beriladi",
            "Frontend platformasida REACT_APP_API_URL shu backend domeniga sozlanib, deploy qilinadi",
        ],
        "correct_order": [
            "GitHub repo backend platformasiga (masalan Render) ulanadi",
            "Environment o'zgaruvchilari (.env'dagilar) platforma panelida sozlanadi",
            "Backend deploy qilinib, haqiqiy domen (masalan onrender.com) beriladi",
            "Frontend platformasida REACT_APP_API_URL shu backend domeniga sozlanib, deploy qilinadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CORS origin'ni sozlash uchun ishlatiladigan environment o'zgaruvchisi",
        "description": "L6_CODE'da backend CORS origin'ini qaysi environment o'zgaruvchisidan o'qiydi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "FRONTEND_URL",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega \"lokalda ishlaydi, productionda ishlamaydi\" muammosi yuzaga keladi?",
        "description": (
            "Agar backend'da cors({ origin: 'http://localhost:3001' }) "
            "qattiq yozilgan bo'lsa (environment o'zgaruvchisi orqali "
            "emas), loyiha lokalda mukammal ishlagandan keyin, nega "
            "deploy qilingandan keyin CORS xatosi chiqadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Lokal muhitda frontend haqiqatan http://localhost:3001 "
            "manzilida ishlaydi, shuning uchun qattiq yozilgan CORS "
            "origin to'g'ri keladi va hamma narsa mukammal ishlaydi. "
            "Lekin deploy qilingandan keyin, frontend butunlay boshqa, "
            "haqiqiy domenda (masalan "
            "https://taskflow-frontend.vercel.app) joylashadi. Backend "
            "kodi esa hali ham faqat localhost:3001'ga ruxsat berish "
            "uchun yozilgan, shuning uchun u productiondagi haqiqiy "
            "frontend domenidan kelgan so'rovlarni \"tanimaydi\" va rad "
            "etadi — bu esa \"lokalda ishlaydi, productionda ishlamaydi\" "
            "degan klassik muammoni keltirib chiqaradi. Yechim - "
            "origin qiymatini environment o'zgaruvchisi orqali sozlash, "
            "shunda u har bir muhitda mos qiymatni oladi."
        ),
        "hint": "Lokal va production muhitida frontend manzili bir xilmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "TaskFlow — CAPSTONE yakuni: to'liq deploy qilingan loyiha",
    "task_description": (
        "TaskFlow'ni haqiqiy hostingga (masalan Render/Railway backend uchun, "
        "Vercel/Netlify frontend uchun) deploy qiling. CORS origin va API "
        "manzilini environment o'zgaruvchilari orqali production'ga moslang. "
        "README.md'ni jonli havolalar va yakuniy holat bilan yangilang."
    ),
    "task_requirements": (
        "• Backend haqiqiy hostingda ishlab turibdi (github_url'dagi repo bilan bog'liq)\n"
        "• Frontend haqiqiy hostingda ishlab turibdi, deploy qilingan\n"
        "• CORS origin production frontend domeniga to'g'ri sozlangan (localhost qattiq yozilmagan)\n"
        "• Frontend'dagi API manzili production backend domeniga sozlangan\n"
        "• Ro'yxatdan o'tish, kirish, task qo'shish/o'chirish, qidiruv — barchasi jonli saytda ishlaydi\n"
        "• README.md: jonli havolalar (frontend + backend), texnologiyalar, 6/6 bosqich yakunlangan checklist\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
        "(backend + frontend) tekshiradi, alohida live_demo_url maydoni endi shart emas"
    ),
    "task_technologies": "Render/Railway, Vercel/Netlify, environment variables, CORS",
    "task_deadline_days": 3,
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
