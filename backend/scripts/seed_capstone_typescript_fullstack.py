"""Seed "Capstone 4: TypeScript Full-Stack" (7 lessons): combines TypeScript
Asoslari, Node.js/Express Asoslari and React: Redux Toolkit, TypeScript va
Testlash into ONE project — 'IssueForge', a small issue/bug tracker built
with an Express + TypeScript backend and a React + Redux Toolkit + TypeScript
frontend (no bot; 2 deploy units, same shape as Capstone 1).

Unlike Capstones 1-3, every lesson's deliberate bug belongs to the SAME
family: TypeScript only checks types at COMPILE time — nothing stops a wrong
value at RUNTIME. Each lesson finds this illusion in a different place
(unvalidated req.body interfaces, `as` casts on incomplete SQL results,
unchecked JWT payload casts, frontend/backend type drift, stale-shaped test
mocks, tsconfig path aliases that don't survive the production build).

Uses the same project-submission mechanism as every other capstone via
task_title/task_description/task_requirements/task_technologies/
task_deadline_days on Lesson — students build ONE evolving 'IssueForge' app
across all 7 milestones, resubmitting the same (updated) github_url/
live_demo_url each time via the existing Submission + AI-grading pipeline.
No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_typescript_fullstack
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py (see the
matching scripts/ru_capstone4_lesson_0X.py for each lesson).

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
    "title": "Capstone 4: TypeScript Full-Stack",
    "description": (
        "TypeScript Asoslari, Node.js/Express Asoslari va React: Redux "
        "Toolkit, TypeScript va Testlash kurslarini tugatgan dasturchilar "
        "uchun: uchalasini BIR loyihada birlashtirasiz. 7 bosqichda "
        "'IssueForge' — jamoaviy xato/vazifa kuzatuvchisini (issue tracker) "
        "qurasiz: Express + TypeScript backend HAMDA React + Redux Toolkit "
        "+ TypeScript frontend. Har bir bosqichda TypeScript'ning eng katta "
        "chegarasi bilan tanishasiz: u faqat COMPILE vaqtida tekshiradi — "
        "runtime'da hech narsani kafolatlamaydi. Har bir bosqich haqiqiy "
        "loyiha topshirig'i sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 9,  # React
    "prerequisite_course_id": 72,  # React: Redux Toolkit, TypeScript va Testlash (also assumes course 74: Node.js/Express Asoslari, course 80: TypeScript Asoslari)
    "is_active": True,
    "is_published": False,  # flip to True once all 7 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done", "lang": "typescript",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "Shared TS types strategy, DB schema as interfaces, repo scaffold for IssueForge."},
    {"order": 1, "ref": "L2", "status": "done", "lang": "typescript",
     "title": "2-Backend API (Express + TypeScript)",
     "scope": "Typed req/response interfaces; the limits of compile-time-only validation."},
    {"order": 2, "ref": "L3", "status": "done", "lang": "typescript",
     "title": "3-PostgreSQL CRUD (tiplashtirilgan so'rovlar)",
     "scope": "pg + parameterized queries with typed results; risk of `as` casts on incomplete SELECTs."},
    {"order": 3, "ref": "L4", "status": "done", "lang": "typescript",
     "title": "4-Autentifikatsiya (JWT + tiplashtirilgan payload)",
     "scope": "JWT auth with a typed decoded-token interface; risk of trusting an unchecked cast."},
    {"order": 4, "ref": "L5", "status": "done", "lang": "tsx",
     "title": "5-React frontend + Redux Toolkit (TypeScript)",
     "scope": "Typed hooks consuming the backend API; frontend/backend type drift."},
    {"order": 5, "ref": "L6", "status": "done", "lang": "tsx",
     "title": "6-Testing (Jest + React Testing Library)",
     "scope": "Mocking typed API calls; a stale mock shape that keeps tests green."},
    {"order": 6, "ref": "L7", "status": "done", "lang": "typescript",
     "title": "7-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "tsconfig path aliases, production build, CORS, real deploy — compiling clean is not the same as running clean."},
]


L1_TEXT = """\
<h2>IssueForge — 7 bosqichda TypeScript to'liq stack loyiha</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> API["2-Backend API"]
    API --> CRUD["3-PostgreSQL CRUD"]
    CRUD --> AUTH["4-Autentifikatsiya"]
    AUTH --> FE["5-React frontend"]
    FE --> TEST["6-Testing"]
    TEST --> DEPLOY["7-Deploy"]
</pre>

<p>Bu kursda siz TypeScript Asoslari, Node.js/Express Asoslari va React: Redux Toolkit, TypeScript va Testlash kurslarida <strong>alohida</strong> o'rgangan hamma narsani <strong>bitta haqiqiy loyiha</strong>da birlashtirasiz: <strong>IssueForge</strong> — jamoaviy xato/vazifa kuzatuvchisi (issue tracker). Har bir dars — shu bitta loyihaning navbatdagi bosqichi.</p>

<p>Lekin bu capstone oldingi uchtasidan bir narsa bilan farq qiladi: har bir darsdagi "ataylab xato" <strong>bitta oilaga</strong> tegishli bo'ladi — <strong>TypeScript faqat COMPILE vaqtida tekshiradi, runtime'da HECH NARSANI kafolatlamaydi.</strong> Bu darsda shu g'oyaning o'zi bilan tanishasiz; keyingi har bir bosqich uni yangi joyda ko'rsatadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo tuzilmasi: umumiy (shared) types papkasi bilan monorepo</h4>
<pre><code># IssueForge uchun repo tuzilmasi - TaskFlow'dagidek monorepo, lekin
# TypeScript loyihasi bo'lgani uchun UCHINCHI papka qo'shiladi: shared/
issueforge/
  backend/          # Express + TypeScript (2-4-darsda quriladi)
    src/
    tsconfig.json
  frontend/          # React + Redux Toolkit + TypeScript (5-darsda quriladi)
    src/
    tsconfig.json
  shared/            # ❗ backend VA frontend IKKALASI ham import qiladigan interfeyslar
    types.ts
  README.md
  .gitignore</code></pre>

<h4>BLOKA 2 — DB sxemasini TypeScript interfeyslari sifatida loyihalash</h4>
<pre><code>// shared/types.ts - IssueForge uchun asosiy interfeyslar
interface User {
  id: number;
  name: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

interface Issue {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  assigneeId: number | null;
  reporterId: number;
  createdAt: string;
}

// Bog'lanishlar:
// - Bitta User -> ko'p Issue (reporter sifatida)
// - Bitta User -> ko'p Issue (assignee sifatida, ixtiyoriy)</code></pre>

<h4>BLOKA 3 — README.md: loyihaning "eshigi"</h4>
<pre><code># README.md
# IssueForge

## Loyiha haqida
Jamoaviy issue/xato kuzatuvchisi - Express + TypeScript + React + Redux Toolkit.

## Umumiy types strategiyasi
shared/types.ts - backend VA frontend BIR XIL interfeyslarni import qiladi.

## Texnologiyalar
- Backend: Node.js, Express, TypeScript, PostgreSQL
- Frontend: React, Redux Toolkit, TypeScript

## Holat
- [x] Loyihalash va repo skeleton
- [ ] Backend API
- [ ] PostgreSQL CRUD
- [ ] Autentifikatsiya
- [ ] React frontend
- [ ] Testing
- [ ] Deploy</code></pre>

<h3>🐛 Ataylab qiyin: backend va frontend uchun interfeyslarni ALOHIDA yozish</h3>
<p>Ko'p boshlang'ich TypeScript loyihalarida dasturchi <code>shared/</code> papka haqida o'ylamasdan, backend uchun bitta <code>Issue</code> interfeysini, frontend uchun esa <strong>boshqa, alohida</strong> <code>Issue</code> interfeysini yozadi:</p>
<pre><code>// backend/src/types.ts
interface Issue {
  id: number;
  title: string;
  status: string;   // ❗ literal union emas, oddiy string
  assigneeId: number | null;
}

// frontend/src/types.ts (ALOHIDA fayl, ALOHIDA yozilgan!)
interface Issue {
  id: number;
  title: string;
  status: string;
  assignee_id: number | null;   // ❗ boshqa nom uslubi - kamera_case vs snake_case!
}</code></pre>
<p><strong>Natija:</strong> hozircha ikkala interfeys <strong>bir xilga o'xshaydi</strong>, shuning uchun xato ko'rinmaydi. Lekin ular <strong>ikkita mustaqil fayl</strong> — TypeScript compiler ularni <strong>hech qachon</strong> taqqoslamaydi, chunki ular boshqa-boshqa modullar. Agar kelajakda backend <code>assigneeId</code>'ni <code>assignee_id</code>ga o'zgartirsa (yoki aksincha), <strong>ikkala tomon ham</strong> "muvaffaqiyatli compile" bo'laveradi — chunki har biri faqat <strong>o'zining</strong> interfeysiga qarshi tekshiriladi. Xato faqat <strong>runtime</strong>da, frontend backend'dan kelgan haqiqiy JSON'ni o'qishga uringanda paydo bo'ladi (5-darsda aynan shu holatni ko'rasiz).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega <code>shared/types.ts</code> papkasi tavsiya etiladi?</h4>
<p>Agar backend va frontend <strong>bir xil</strong> faylni import qilsa, ular orasida farq paydo bo'lishi <strong>strukturaviy jihatdan imkonsiz</strong> bo'ladi — compiler ikkalasini ham <strong>bitta</strong> interfeys asosida tekshiradi. Agar ular alohida-alohida yozilsa, hech narsa ularni sinxron ushlab turmaydi.</p>

<h4>2. TypeScript interfeysi runtime'da nimani tekshiradi?</h4>
<p><strong>Hech narsani.</strong> Interfeys — faqat <code>tsc</code> compile qilayotganda ishlatiladigan "hujjat". Dastur ishga tushgandan (compile bo'lib, JavaScript'ga aylantirilgandan) keyin, interfeys butunlay <strong>yo'qoladi</strong> — u compile qilingan <code>.js</code> faylda umuman mavjud emas. Shuning uchun tarmoqdan kelgan haqiqiy JSON interfeysga mos kelmasa ham, buni hech kim <strong>runtime'da</strong> tekshirmaydi, agar buni siz <strong>aniq</strong> kod bilan qilmasangiz.</p>

<h4>3. Nega DB sxemasi endi interfeys sifatida ham yoziladi?</h4>
<p>TaskFlow'da (Capstone 1) sxema faqat "qog'ozda" (izohlarda) tasvirlangan edi. Bu safar, TypeScript loyihasi bo'lgani uchun, sxemani <strong>to'g'ridan-to'g'ri</strong> interfeys sifatida yozish mumkin — bu ham hujjat, ham (qisman) compile vaqtidagi tekshiruv vazifasini bajaradi.</p>

<h4>4. README bu safar nima uchun ayniqsa muhim?</h4>
<p>README endi nafaqat "qanday ishga tushirish"ni, balki <strong>umumiy types strategiyasi</strong>ni ham tushuntirishi kerak — jamoadagi boshqa dasturchi <code>shared/</code> papkani import qilishi kerakligini bilishi, aks holda xuddi yuqoridagi "ataylab qiyin" holatiga tushib qolishi mumkin.</p>

<h4>5. Nega bu kursning "xatolari" bir-biriga bog'liq (bitta oilaga tegishli)?</h4>
<p>Oldingi capstone'larda har bir darsning xatosi <strong>mustaqil</strong> edi (CORS, foreign key, nisbiy yo'l). Bu safar barcha 7 bosqichdagi xato <strong>bitta katta g'oyaning</strong> turli ko'rinishi: <em>"TypeScript compile vaqtida tekshiradi, runtime'da emas."</em> Bu safar siz nafaqat alohida xatolarni, balki TypeScript'ning <strong>o'zi haqidagi</strong> chuqurroq haqiqatni o'rganasiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>shared/types.ts</code> — backend va frontend interfeyslarini bitta manbaga bog'lash usuli</li>
<li>✅ TypeScript interfeysi runtime'da <strong>hech narsani</strong> tekshirmaydi — u faqat compile vaqtida ishlaydi</li>
<li>✅ Alohida yozilgan (sinxronlanmagan) interfeyslar hozir zararsiz ko'rinsa ham, kelajakda xavfli</li>
<li>✅ DB sxemasi endi to'g'ridan-to'g'ri TypeScript interfeysi sifatida ham hujjatlashtiriladi</li>
<li>✅ Bu kursdagi barcha 7 ta "ataylab xato" — bitta umumiy g'oyaning turli ko'rinishlari</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 1-BOSQICH: Loyihalash va repo skeleton
// ════════════════════════════════════════════════════════════════════

// Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.
// Quyida - IssueForge uchun shared/types.ts faylining to'liq tarkibi:

interface User {
  id: number;
  name: string;
  email: string;
  passwordHash: string;
  createdAt: string;
}

interface Issue {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  assigneeId: number | null;
  reporterId: number;
  createdAt: string;
}

export type { User, Issue };

// ─────────────────────────────────────────────────────────────────────
// Repo tuzilmasi (izohda - papka/fayl tuzilmasi, kod emas)
// ─────────────────────────────────────────────────────────────────────

// issueforge/
//   backend/
//     src/
//     tsconfig.json
//   frontend/
//     src/
//     tsconfig.json
//   shared/
//     types.ts
//   README.md
//   .gitignore

// ─────────────────────────────────────────────────────────────────────
// Ataylab qiyin - ALOHIDA yozilgan interfeyslar (izohda)
// ─────────────────────────────────────────────────────────────────────

// backend/src/types.ts va frontend/src/types.ts alohida-alohida
// yozilsa, TypeScript compiler ularni HECH QACHON taqqoslamaydi -
// ular ikkita mustaqil modul. shared/types.ts BU muammoni yo'q qiladi.
"""

L1_EX = [
    {
        "title": "Nega IssueForge uchun shared/types.ts tavsiya etiladi?",
        "description": "Backend va frontend uchun bitta umumiy shared/types.ts fayli ishlatilishining asosiy sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni qisqartirish uchun, boshqa sababi yo'q",
            "Backend va frontend bir xil interfeysdan foydalanadi - ular orasida farq paydo bo'lishi strukturaviy jihatdan imkonsiz bo'ladi",
            "TypeScript alohida fayllar bilan ishlamaydi",
            "Bu Express'ning majburiy talabi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agar ikkalasi HAM bitta faylni import qilsa, ular sinxron bo'lmasligi mumkinmi?",
        "explanation": "Backend va frontend bitta shared/types.ts faylini import qilganda, compiler ikkalasini ham bitta interfeys asosida tekshiradi - shuning uchun ular orasida farq paydo bo'lishi imkonsiz bo'ladi. Alohida yozilgan interfeyslar esa hech narsa bilan sinxronlanmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "TypeScript interfeysi runtime'da nimani tekshiradi?",
        "description": "Dastur compile bo'lib, JavaScript'ga aylangandan (ya'ni runtime'da ishga tushgandan) keyin, TypeScript interfeysi nimani tekshiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kelayotgan har bir JSON obyektini avtomatik tekshiradi",
            "Hech narsani - interfeys faqat compile vaqtida ishlatiladi va keyin butunlay yo'qoladi",
            "Faqat number turidagi maydonlarni tekshiradi",
            "Faqat production muhitida tekshiradi, development'da emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Compile qilingan .js faylni ochib ko'rsangiz, u yerda interfeys degan narsa umuman yo'q.",
        "explanation": "TypeScript interfeysi faqat tsc compile qilayotganda ishlatiladigan \"hujjat\" - dastur JavaScript'ga aylangandan keyin interfeys butunlay yo'qoladi va runtime'da hech narsani tekshirmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "IssueForge'ni rejalashtirish jarayonini tartiblang",
        "description": "IssueForge uchun 1-bosqichning to'g'ri rejalashtirish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "shared/types.ts uchun umumiy types strategiyasi qaror qilinadi",
            "User va Issue interfeyslari shared/types.ts'ga yoziladi",
            "backend/, frontend/, shared/ papkalari bilan repo skeleton yaratiladi",
            "README.md loyiha tavsifi, texnologiyalar va types strategiyasi bilan yoziladi",
        ],
        "correct_order": [
            "shared/types.ts uchun umumiy types strategiyasi qaror qilinadi",
            "User va Issue interfeyslari shared/types.ts'ga yoziladi",
            "backend/, frontend/, shared/ papkalari bilan repo skeleton yaratiladi",
            "README.md loyiha tavsifi, texnologiyalar va types strategiyasi bilan yoziladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TypeScript loyihasida .gitignore'ga qo'shiladigan build papkasi",
        "description": "tsc compile qilganda hosil bo'ladigan, .gitignore'ga qo'shilishi shart bo'lgan standart papka nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "dist",
        "hint": "Bu odatda tsconfig.json'dagi \"outDir\" bilan belgilanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega alohida yozilgan Issue interfeyslari hozir zararsiz, keyinchalik xavfli?",
        "description": (
            "backend/src/types.ts va frontend/src/types.ts'da ikkita "
            "alohida Issue interfeysi yozilgan, va ular hozircha bir xil "
            "ko'rinadi. Nega bu holat hozir muammo tug'dirmaydi, lekin "
            "kelajakda xavfli bo'lib qolishi mumkin? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Ikkala interfeys alohida fayllarda yozilgani uchun TypeScript "
            "compiler ularni bir-biriga umuman taqqoslamaydi - har biri "
            "faqat o'zining modulida mustaqil tekshiriladi. Hozircha ular "
            "tasodifan bir xil ko'rinadi, shuning uchun hech qanday xato "
            "chiqmaydi. Lekin kelajakda, masalan backend assigneeId "
            "maydonini o'zgartirsa yoki olib tashlasa, frontend'dagi "
            "interfeys BUNI BILMAYDI va hech qanday compile xatosi "
            "chiqmaydi - chunki ikkalasi ham faqat o'z nusxasiga qarshi "
            "tekshiriladi. Xato faqat runtime'da, frontend backend'dan "
            "kelgan haqiqiy JSON'ni ishlatishga uringanda paydo bo'ladi."
        ),
        "hint": "TypeScript compiler backend/src/types.ts va frontend/src/types.ts'ni bir-biri bilan taqqoslaydimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "IssueForge — repo skeleton va umumiy TypeScript sxema hujjati",
    "task_description": (
        "IssueForge loyihasi uchun GitHub'da monorepo yarating (backend/, "
        "frontend/, shared/ papkalari bilan), to'liq README.md yozing va "
        "User/Issue uchun TypeScript interfeyslarini shared/types.ts'ga "
        "yozing. Bu loyiha keyingi 6 bosqichda shu repo ustida davom etadi."
    ),
    "task_requirements": (
        "• GitHub'da 'issueforge' nomli public repo yaratilgan\n"
        "• backend/, frontend/, shared/ papkalari mavjud (bo'sh yoki tsconfig.json bilan)\n"
        "• shared/types.ts: User va Issue interfeyslari to'liq yozilgan\n"
        "• backend/tsconfig.json va frontend/tsconfig.json ikkalasida ham \"strict\": true\n"
        "• README.md: loyiha tavsifi, texnologiyalar, umumiy types strategiyasi tushuntirilgan, holat checklist'i\n"
        "• .gitignore fayli mavjud (node_modules, dist, .env chiqarib tashlangan)"
    ),
    "task_technologies": "TypeScript, Git, GitHub, Markdown",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Backend API (Express + TypeScript) — interfeys va runtime orasidagi bo'shliq</h2>

<pre class="mermaid">
flowchart LR
    CLIENT["Klient: noto'g'ri shaklda JSON yuboradi"] --> ROUTE["POST /issues"]
    ROUTE --> IFACE{"req.body: CreateIssueBody deb 'tiplashtirilgan'"}
    IFACE -->|"TypeScript: 'OK, tur mos'"| HANDLER["handler ichida ishlatiladi"]
    HANDLER --> CRASH["Runtime'da kutilmagan qiymat - xato yoki noto'g'ri natija"]
</pre>

<p>Node.js/Express kursida Express routing va middleware'ni, TypeScript Asoslari kursida esa interfeyslarni allaqachon o'rgangansiz. Bu darsda ikkalasini birlashtirasiz: Express endpoint'lariga TypeScript interfeyslari orqali <strong>turlar</strong> berasiz. Lekin shu yerda 1-darsda tanishgan g'oya birinchi marta <strong>kod ichida</strong> namoyon bo'ladi: interfeys yozish — <strong>validatsiya qilish bilan bir xil emas.</strong></p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Express + TypeScript sozlash</h4>
<pre><code># Terminal:
cd backend
npm init -y
npm install express
npm install -D typescript ts-node @types/express @types/node

# backend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true
  }
}</code></pre>

<h4>BLOKA 2 — POST /issues: request body'ni interfeys bilan tiplashtirish</h4>
<pre><code>// backend/src/server.ts
import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const app = express();
app.use(express.json());

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

let issues: Issue[] = [];
let nextId = 1;

app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;   // ❗ TS "ishonch" beradi - lekin tekshirmaydi!

  const issue: Issue = {
    id: nextId++,
    title,
    description,
    status: 'open',
    assigneeId: null,
    reporterId,
    createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});</code></pre>

<h4>BLOKA 3 — GET /issues: shared Issue turi bilan javob qaytarish</h4>
<pre><code>app.get('/issues', (req: Request, res: Response) => {
  res.json(issues);   // ❗ TypeScript "issues bu Issue[]" deb biladi, chunki yuqorida shunday e'lon qilingan
});

app.listen(4000, () => console.log('IssueForge API: http://localhost:4000'));</code></pre>

<h3>🐛 Ataylab xato — interfeys "validatsiya" o'rnini bosadi deb o'ylash</h3>
<pre><code>app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;

  // ❌ Hech qanday tekshiruv yo'q - TypeScript "CreateIssueBody" deb aytgani
  // uchun dasturchi "bu maydonlar albatta to'g'ri keladi" deb ISHONADI.
  const issue: Issue = {
    id: nextId++, title, description, status: 'open',
    assigneeId: null, reporterId, createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});

// Klient BUNDAY so'rov yuborsa (title umuman yo'q, reporterId - matn):
// curl -X POST http://localhost:4000/issues -H "Content-Type: application/json" \\
//   -d '{"description": "xato bor", "reporterId": "ikki"}'
//
// ❌ tsc BUNI umuman ANIQLAMAYDI - chunki tsc compile vaqtida ishlaydi,
//    bu esa RUNTIME'da kelayotgan haqiqiy so'rov. title = undefined,
//    reporterId = "ikki" (string, number emas!) - lekin dastur "muvaffaqiyatli"
//    201 qaytaradi, buzilgan issue saqlanadi.</code></pre>

<p><strong>Natija:</strong> <code>req.body</code>'ni <code>Request&lt;{}, {}, CreateIssueBody&gt;</code> orqali "tiplashtirish" TypeScript'ga faqat <strong>compile vaqtida</strong> yordam beradi — masalan, <code>req.body.titel</code> (xato yozilgan) deb yozsangiz, <code>tsc</code> buni ANIQLAYDI, chunki <code>CreateIssueBody</code>da <code>titel</code> maydoni yo'q. Lekin <code>req.body</code>ning <strong>haqiqiy runtime qiymati</strong> — bu shunchaki <code>express.json()</code> orqali parse qilingan, <strong>hech qanday tekshiruvsiz</strong> JSON obyekt. Agar klient <code>title</code>ni umuman yubormasa yoki <code>reporterId</code>ni son o'rniga matn qilib yuborsa, TypeScript buni <strong>hech qachon</strong> ushlamaydi — chunki interfeys allaqachon compile vaqtida "vazifasini bajargan" va kompilyatsiya qilingan <code>.js</code> faylda umuman mavjud emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>Request&lt;{}, {}, CreateIssueBody&gt;</code> yozish TypeScript'ga aslida nima deydi?</h4>
<p>Bu yozuv shunchaki TypeScript'ga: <em>"agar <code>req.body</code>ga <code>CreateIssueBody</code> sifatida murojaat qilsam, quyidagi maydonlar (<code>title</code>, <code>description</code>, <code>reporterId</code>) mavjud deb hisobla"</em> deydi. Bu — <strong>faraz</strong>, kafolat emas. Compiler sizga ishonadi, chunki tekshirishning boshqa usuli yo'q.</p>

<h4>2. <code>req.body</code>ning haqiqiy runtime turi nima?</h4>
<p><code>express.json()</code> middleware'i kelgan JSON matnni <code>JSON.parse()</code> orqali oddiy JavaScript obyektiga aylantiradi va uni <code>req.body</code>ga joylashtiradi. Bu — <strong>hech qanday struktura kafolatlanmagan</strong>, oddiy obyekt. <code>Request&lt;{}, {}, CreateIssueBody&gt;</code> generic'i esa faqat TypeScript'ga "buni shunday deb hisobla" deb <strong>ko'rsatma</strong> beradi, lekin buni <strong>hech kim tekshirmaydi</strong>.</p>

<h4>3. Nega interfeys yozish validatsiya bilan bir xil emas?</h4>
<p>Interfeys — <strong>compile vaqtidagi</strong> tuzilma tavsifi. Validatsiya — <strong>runtime'da</strong>, har bir kelgan so'rov uchun, haqiqiy qiymatlarni tekshirish jarayoni (masalan: <code>typeof title === 'string'</code>, <code>title.length &gt; 0</code>). Bittasi ikkinchisining o'rnini bosa olmaydi — ular <strong>butunlay boshqa vaqtda</strong> ishlaydi.</p>

<h4>4. Runtime validatsiyasi bo'lmasa, nima yuz berishi mumkin?</h4>
<p>Noto'g'ri shakldagi ma'lumot (masalan <code>title</code> yo'q, yoki <code>reporterId</code> matn) hech qanday xatosiz ma'lumotlar bazasiga (yoki bu darsda — xotiradagi massivga) <strong>saqlanadi</strong>. Bu xato darhol emas, balki <strong>keyinroq</strong>, masalan frontend bu <code>issue</code>ni ko'rsatishga uringanda yoki <code>reporterId</code> bo'yicha qidiruv qilinganda paydo bo'lishi mumkin — bu esa xatoning haqiqiy manbaini topishni qiyinlashtiradi.</p>

<h4>5. Bu 1-darsdagi "ataylab qiyin"dan nima bilan farq qiladi?</h4>
<p>1-darsda muammo <strong>potensial</strong> edi (interfeyslar hali sinxronlanmagan, lekin hali hech narsa "buzilmagan"). Bu darsda esa xato <strong>haqiqiy, ishlaydigan kodda</strong> — bu safar siz TypeScript'ning eng katta chegarasini "jonli" holatda, o'zingiz yozgan endpoint orqali ko'rasiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>Request&lt;{}, {}, T&gt;</code> — Express'da request body'ni tiplashtirish usuli</li>
<li>✅ Bu faqat compile vaqtidagi <strong>faraz</strong>, runtime'dagi <strong>kafolat</strong> emas</li>
<li>✅ <code>req.body</code>ning haqiqiy runtime qiymati — hech narsa bilan tekshirilmagan oddiy JSON obyekt</li>
<li>✅ Interfeys (compile vaqtida) va validatsiya (runtime'da) — ikki <strong>butunlay boshqa</strong> tushuncha</li>
<li>✅ Runtime validatsiyasiz, noto'g'ri shakldagi ma'lumot xatosiz saqlanib, xatoni keyinroq va uzoqroqda paydo bo'lishiga sabab bo'ladi</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 2-BOSQICH: Backend API (Express + TypeScript)
// ════════════════════════════════════════════════════════════════════

import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const app = express();
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────
// 1) So'rov tanasi uchun interfeys
// ─────────────────────────────────────────────────────────────────────

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

let issues: Issue[] = [];
let nextId = 1;

// ─────────────────────────────────────────────────────────────────────
// 2) POST /issues - tiplashtirilgan, lekin VALIDATSIYASIZ
// ─────────────────────────────────────────────────────────────────────

app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;

  const issue: Issue = {
    id: nextId++,
    title,
    description,
    status: 'open',
    assigneeId: null,
    reporterId,
    createdAt: new Date().toISOString(),
  };
  issues.push(issue);
  res.status(201).json(issue);
});

// ─────────────────────────────────────────────────────────────────────
// 3) GET /issues - shared Issue turi bilan
// ─────────────────────────────────────────────────────────────────────

app.get('/issues', (req: Request, res: Response) => {
  res.json(issues);
});

app.listen(4000, () => console.log('IssueForge API: http://localhost:4000'));

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - runtime validatsiyasiz so'rov (izohda)
// ─────────────────────────────────────────────────────────────────────

// curl -X POST http://localhost:4000/issues -H "Content-Type: application/json" \\
//   -d '{"description": "xato bor", "reporterId": "ikki"}'
//
// title = undefined, reporterId = "ikki" (string!) - lekin tsc buni
// compile vaqtida ANIQLAY OLMAYDI, chunki bu runtime'dagi haqiqiy so'rov.
// Dastur 201 bilan "muvaffaqiyatli" javob qaytaradi.
"""

L2_EX = [
    {
        "title": "Request<{}, {}, CreateIssueBody> nimani anglatadi?",
        "description": "Express'da app.post('/issues', (req: Request<{}, {}, CreateIssueBody>, res) => {...}) yozuvida bu generic TypeScript'ga aslida nima haqida ma'lumot beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "req.body kelgan JSON'ni avtomatik tekshiradi va noto'g'ri bo'lsa xato qaytaradi",
            "req.bodyga CreateIssueBody sifatida murojaat qilish mumkinligini TypeScript'ga aytadi - bu faraz, kafolat emas",
            "Bu Express serverini tezroq ishlashga majburlaydi",
            "Bu faqat production muhitida ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu compile vaqtidagi yordam, runtime tekshiruvi emas.",
        "explanation": "Request<{}, {}, CreateIssueBody> shunchaki TypeScript'ga req.bodyga shu interfeys sifatida murojaat qilish mumkinligini aytadi - bu compile vaqtidagi faraz, hech qanday runtime tekshiruvi emas.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "req.body'ning haqiqiy runtime turi nima?",
        "description": "express.json() middleware'i orqali kelgan req.body haqiqatda (runtime'da) qanday qiymat?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim aynan CreateIssueBody interfeysiga mos keladigan obyekt",
            "JSON.parse() natijasi - hech qanday struktura kafolatlanmagan oddiy JavaScript obyekt",
            "Har doim string turidagi qiymat",
            "Avtomatik ravishda Issue tipiga aylantirilgan obyekt",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "express.json() nima qiladi - JSON matnni qanday JS qiymatiga aylantiradi?",
        "explanation": "express.json() kelgan JSON matnni JSON.parse() orqali oddiy JavaScript obyektiga aylantiradi - bu hech qanday struktura kafolatlanmagan qiymat, interfeys esa faqat TypeScript'ga ko'rsatma beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Noto'g'ri so'rov qanday ishlov ko'rishini tartiblang",
        "description": "title'siz, reporterId matn shaklida yuborilgan POST /issues so'rovi qanday ishlov ko'rilishini tartiblang (validatsiyasiz kodda).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Klient noto'g'ri shakldagi JSON yuboradi (title yo'q, reporterId - matn)",
            "express.json() uni oddiy JS obyektiga aylantiradi, req.bodyga joylashtiradi",
            "TypeScript compile vaqtida bu holatni tekshira olmaydi - kod allaqachon compile bo'lgan",
            "Handler hech qanday tekshiruvsiz issue obyektini yaratadi va 201 bilan saqlaydi",
        ],
        "correct_order": [
            "Klient noto'g'ri shakldagi JSON yuboradi (title yo'q, reporterId - matn)",
            "express.json() uni oddiy JS obyektiga aylantiradi, req.bodyga joylashtiradi",
            "TypeScript compile vaqtida bu holatni tekshira olmaydi - kod allaqachon compile bo'lgan",
            "Handler hech qanday tekshiruvsiz issue obyektini yaratadi va 201 bilan saqlaydi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Interfeys va validatsiya orasidagi asosiy farq",
        "description": "Interfeys qaysi vaqtda ishlaydi, validatsiya esa qaysi vaqtda? (ikkala so'zni ketma-ket, vergul bilan ajratib yozing, masalan: X vaqtida, Y vaqtida)",
        "exercise_type": "text_input",
        "expected_answer": "compile vaqtida, runtime vaqtida",
        "hint": "Bittasi tsc ishlaganda, ikkinchisi dastur ishga tushganda ishlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega noto'g'ri shakldagi ma'lumot xatosiz saqlanib qolishi xavfli?",
        "description": (
            "Agar POST /issues endpoint'i runtime validatsiyasiga ega "
            "bo'lmasa, va klient title'siz yoki noto'g'ri turdagi "
            "reporterId bilan so'rov yuborsa, bu qanday uzoq muddatli "
            "muammoga olib kelishi mumkin? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Runtime validatsiyasi bo'lmagani uchun, noto'g'ri shakldagi "
            "ma'lumot (masalan title = undefined yoki reporterId matn "
            "shaklida) hech qanday xatosiz to'g'ridan-to'g'ri saqlanadi va "
            "201 muvaffaqiyatli javob qaytariladi - xato DARHOL "
            "ko'rinmaydi. Muammo faqat KEYINROQ, masalan frontend bu "
            "issue'ni ko'rsatishga urinib title'ning yo'qligidan xato "
            "chiqarganda, yoki reporterId bo'yicha son sifatida "
            "solishtirish/qidiruv qilinganda paydo bo'ladi. Bu esa xatoning "
            "haqiqiy kelib chiqish manbaini (aynan noto'g'ri POST so'rovi) "
            "topishni ancha qiyinlashtiradi, chunki muammo paydo bo'lgan "
            "joy va uning haqiqiy sababi orasida vaqt va joy jihatidan "
            "katta masofa bor."
        ),
        "hint": "Xato darhol ko'rinadimi, yoki keyinroq, boshqa joyda paydo bo'ladimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "IssueForge — Backend API (Express + TypeScript)",
    "task_description": (
        "1-bosqichdagi shared/types.ts asosida Express + TypeScript backend "
        "quring: POST /issues (CreateIssueBody interfeysi bilan tiplashtirilgan) "
        "va GET /issues (Issue[] qaytaradigan) endpoint'larini yozing. "
        "Hozircha xotirada saqlash (massiv) yetarli — PostgreSQL 3-bosqichda "
        "qo'shiladi."
    ),
    "task_requirements": (
        "• backend/tsconfig.json: \"strict\": true sozlangan\n"
        "• POST /issues — Request<{}, {}, CreateIssueBody> orqali tiplashtirilgan\n"
        "• GET /issues — javob shared/types.ts'dagi Issue[] turiga mos\n"
        "• Server npm run dev (ts-node) orqali xatosiz ishga tushadi\n"
        "• README.md holat checklist'i yangilangan\n"
        "• Kamida bitta qo'lda test qilingan misol (masalan curl buyrug'i) README'da ko'rsatilgan"
    ),
    "task_technologies": "Node.js, Express, TypeScript, ts-node",
    "task_deadline_days": 4,
}


L3_TEXT = """\
<h2>3-bosqich: PostgreSQL CRUD — tiplashtirilgan so'rovlar</h2>

<pre class="mermaid">
flowchart LR
    SQL["SELECT id, title, status FROM issues"] --> ROWS["3 ta ustunli qatorlar"]
    ROWS --> CAST["as Issue[] deb 'to'liq' Issue turiga cast qilinadi"]
    CAST --> USE["issue.description.length chaqiriladi"]
    USE --> CRASH["Runtime: Cannot read properties of undefined"]
</pre>

<p>Node.js/Express kursida <code>pg</code> paketi orqali PostgreSQL'ga ulanish va parametrlashtirilgan so'rovlarni allaqachon o'rgangansiz. Bu darsda xotiradagi massivni (2-bosqichdan) haqiqiy PostgreSQL jadvaliga o'tkazasiz. Lekin bu safar TypeScript'ning chegarasi yanada nozikroq joyda ko'rinadi: <code>pool.query&lt;Issue&gt;()</code> kabi "rasmiy", tavsiya etilgan generic yozuv ham SQL natijasi haqiqatan interfeysga mos kelishini <strong>tekshirmaydi</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — pg'ni TypeScript bilan sozlash</h4>
<pre><code># Terminal:
npm install pg
npm install -D @types/pg

// backend/src/db.ts
import { Pool } from 'pg';

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});</code></pre>

<h4>BLOKA 2 — to'liq CRUD: jadval va parametrlashtirilgan so'rovlar</h4>
<pre><code>-- schema.sql
CREATE TABLE issues (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'open',
  assignee_id INTEGER,
  reporter_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);</code></pre>
<pre><code>// backend/src/server.ts
app.post('/issues', async (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;
  const result = await pool.query&lt;Issue&gt;(
    `INSERT INTO issues (title, description, reporter_id)
     VALUES ($1, $2, $3) RETURNING *`,
    [title, description, reporterId]
  );
  res.status(201).json(result.rows[0]);
});

app.get('/issues', async (req: Request, res: Response) => {
  const result = await pool.query&lt;Issue&gt;('SELECT * FROM issues ORDER BY created_at DESC');
  res.json(result.rows);   // ❗ SELECT * - barcha ustunlar bor, shuning uchun bu XAVFSIZ
});</code></pre>

<h4>BLOKA 3 — qisman SELECT uchun ALOHIDA, aniqroq tur yaratish</h4>
<pre><code>// Ro'yxat sahifasi uchun to'liq description kerak emas - faqat 3 ustun yetarli.
// Shuning uchun Issue emas, YANGI, TORROQ interfeys yaratiladi:
interface IssueSummary {
  id: number;
  title: string;
  status: 'open' | 'in_progress' | 'closed';
}

app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query&lt;IssueSummary&gt;(
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);   // ❗ endi tur SQL bilan MOS - description umuman va'da qilinmagan
});</code></pre>

<h3>🐛 Ataylab xato — qisman SELECT'ni to'liq Issue turi bilan "cast" qilish</h3>
<pre><code>// "Tezroq yozaman" deb, YANGI interfeys yaratish o'rniga, dasturchi
// mavjud Issue turini ishlatadi - garchi SQL faqat 3 ustunni tanlasa ham:
app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query&lt;Issue&gt;(          // ❌ Issue - description, assigneeId va h.k. talab qiladi!
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);
});

// Frontend (5-darsda) bu ro'yxatni oladi va har bir issue uchun qisqacha
// matn ko'rsatishga urinadi:
// issues.map(issue =&gt; issue.description.slice(0, 50))
//
// ❌ TypeError: Cannot read properties of undefined (reading 'slice')
// - chunki description SQL natijasida umuman YO'Q, lekin TypeScript
//   "Issue - description bor" deb ISHONGAN edi.</code></pre>

<p><strong>Natija:</strong> <code>pool.query&lt;Issue&gt;(...)</code> generic yozuvi — <code>pg</code> kutubxonasining o'zi ham faqat TypeScript'ga "natija qatorlarini shu tur sifatida talqin qil" deb <strong>ko'rsatma</strong> beradi, xolos. <code>pg</code> haqiqiy SQL natijasini <code>Issue</code> interfeysi bilan <strong>hech qachon solishtirmaydi</strong> — bu tekshiruv umuman yo'q. Agar SQL so'rov faqat <code>id, title, status</code>'ni tanlasa, lekin natija <code>Issue</code> (ya'ni <code>description</code>, <code>assigneeId</code>, <code>reporterId</code>, <code>createdAt</code> ham talab qiluvchi) sifatida "e'lon qilinsa", TypeScript buni <strong>compile vaqtida to'liq qabul qiladi</strong> — chunki generic parametr shunchaki bir <strong>yorliq</strong>, SQL matnining o'zi bilan bog'liq emas. Xato faqat <strong>keyinroq</strong>, kimdir <code>issue.description</code>ga murojaat qilganda, <code>undefined</code> qiymat bilan ishlashga urinib, paydo bo'ladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>pool.query&lt;Issue&gt;(...)</code> generic'i haqiqatda nima qiladi?</h4>
<p>Bu faqat TypeScript'ga "natijadagi <code>rows</code> massivini <code>Issue[]</code> sifatida hisobla" deydi. <code>pg</code> kutubxonasi buni SQL matni bilan <strong>hech qanday</strong> tarzda solishtirmaydi — bu ikkalasi (generic parametr va SQL so'rov matni) bir-biridan <strong>mustaqil</strong> yoziladi.</p>

<h4>2. SQL SELECT ustunlari va TypeScript turi orasida qanday bog'liqlik bor?</h4>
<p><strong>Hech qanday.</strong> Bular ikkita butunlay boshqa til — SQL matni (satr sifatida) va TypeScript turi (compile vaqtidagi struktura). Hech biri ikkinchisini "o'qib" tekshirmaydi. Ularni <strong>qo'lda</strong>, dasturchi tomonidan mos tutish kerak.</p>

<h4>3. Nega qisman SELECT + to'liq tur bilan cast qilish ayniqsa xavfli?</h4>
<p><code>SELECT *</code> ishlatilganda xato ehtimoli kamroq (barcha ustunlar mavjud). Lekin unumdorlik uchun faqat kerakli ustunlarni tanlash (masalan <code>id, title, status</code>) — yaxshi amaliyot. Muammo shundaki, bu ikki amaliyot (unumdorlik uchun qisman SELECT, va "tezroq" mavjud kattaroq turni qayta ishlatish) birga qo'llanilganda, natija <strong>SQL va tur orasidagi nomuvofiqlik</strong> bo'ladi — buni hech narsa ushlamaydi.</p>

<h4>4. Runtime'dagi <code>undefined.slice()</code> xatosi qayerdan kelib chiqadi?</h4>
<p>SQL <code>description</code> ustunini tanlamagani uchun, natija qatorida bu maydon <strong>umuman yo'q</strong> (<code>undefined</code>). Kod esa TypeScript "bu <code>Issue</code>, <code>description</code> bor" deb aytgani uchun <code>issue.description.slice(...)</code> deb yozadi — bu <code>undefined</code>ning metodini chaqirishga urinish, va JavaScript'da bu darhol xato beradi.</p>

<h4>5. Bunga qarshi to'g'ri yechim nima?</h4>
<p>Har bir SQL so'rov <strong>qaytaradigan haqiqiy ustunlarga</strong> mos, <strong>alohida</strong> interfeys yaratish (masalan <code>IssueSummary</code>) — mavjud, kattaroq turni "qulaylik uchun" qayta ishlatmaslik. Bu TypeScript'ga <strong>haqiqatga yaqinroq</strong> ma'lumot beradi, garchi baribir runtime kafolati bo'lmasa ham.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>pool.query&lt;T&gt;()</code> generic'i ham faqat compile vaqtidagi <strong>yorliq</strong>, SQL bilan solishtirilmaydi</li>
<li>✅ SQL ustunlari va TypeScript turi orasida hech qanday avtomatik bog'liqlik yo'q</li>
<li>✅ Qisman SELECT + kattaroq tur bilan cast qilish — SQL va tur orasidagi nomuvofiqlikka olib keladi</li>
<li>✅ Runtime'dagi <code>undefined</code> metod chaqiruvi xatolari ko'pincha aynan shu nomuvofiqlikdan kelib chiqadi</li>
<li>✅ Har bir SQL so'rov uchun natijaga mos, alohida (torroq) interfeys yaratish xavfsizroq</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 3-BOSQICH: PostgreSQL CRUD - tiplashtirilgan so'rovlar
// ════════════════════════════════════════════════════════════════════

import { Pool } from 'pg';
import express, { Request, Response } from 'express';
import { Issue } from '../../shared/types';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const app = express();
app.use(express.json());

interface CreateIssueBody {
  title: string;
  description: string;
  reporterId: number;
}

// ─────────────────────────────────────────────────────────────────────
// 1) POST /issues - parametrlashtirilgan INSERT, to'liq Issue qaytadi
// ─────────────────────────────────────────────────────────────────────

app.post('/issues', async (req: Request<{}, {}, CreateIssueBody>, res: Response) => {
  const { title, description, reporterId } = req.body;
  const result = await pool.query<Issue>(
    `INSERT INTO issues (title, description, reporter_id)
     VALUES ($1, $2, $3) RETURNING *`,
    [title, description, reporterId]
  );
  res.status(201).json(result.rows[0]);
});

// ─────────────────────────────────────────────────────────────────────
// 2) GET /issues - SELECT * - barcha ustunlar bor, XAVFSIZ
// ─────────────────────────────────────────────────────────────────────

app.get('/issues', async (req: Request, res: Response) => {
  const result = await pool.query<Issue>('SELECT * FROM issues ORDER BY created_at DESC');
  res.json(result.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 3) GET /issues/summary - qisman SELECT + ALOHIDA, torroq tur
// ─────────────────────────────────────────────────────────────────────

interface IssueSummary {
  id: number;
  title: string;
  status: 'open' | 'in_progress' | 'closed';
}

app.get('/issues/summary', async (req: Request, res: Response) => {
  const result = await pool.query<IssueSummary>(
    'SELECT id, title, status FROM issues ORDER BY created_at DESC'
  );
  res.json(result.rows);
});

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - qisman SELECT'ni Issue bilan cast qilish (izohda)
// ─────────────────────────────────────────────────────────────────────

// app.get('/issues/summary', async (req: Request, res: Response) => {
//   const result = await pool.query<Issue>(          // ❌ Issue description talab qiladi!
//     'SELECT id, title, status FROM issues ORDER BY created_at DESC'
//   );
//   res.json(result.rows);
// });
// Keyinchalik: issue.description.slice(0, 50) -> TypeError: undefined
"""

L3_EX = [
    {
        "title": "pool.query<Issue>(...) generic'i SQL bilan qanday bog'lanadi?",
        "description": "pg kutubxonasida pool.query<Issue>('SELECT ...') yozilganda, <Issue> generic'i SQL matni bilan qanday tekshiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "pg SQL matnini o'qib, ustunlar Issue'ga mosligini avtomatik tekshiradi",
            "Hech qanday tekshirilmaydi - bu faqat TypeScript'ga natijani qanday turda hisoblashni aytadigan yorliq",
            "Faqat production muhitida tekshiriladi",
            "Postgres serverining o'zi buni tekshiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Generic parametr va SQL matni - ikkita mustaqil yozilgan narsa.",
        "explanation": "pool.query<Issue>() generic'i faqat TypeScript'ga natijani Issue sifatida hisoblashni aytadi - pg kutubxonasi SQL matnini Issue interfeysi bilan hech qachon solishtirmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega qisman SELECT + to'liq Issue turi bilan cast qilish xavfli?",
        "description": "SELECT id, title, status FROM issues so'rovi natijasini pool.query<Issue>() bilan olish nega muammoli?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu so'rov Postgres'da ishlamaydi",
            "Chunki Issue turi description, assigneeId kabi maydonlarni talab qiladi, lekin SQL ularni tanlamagan - keyinchalik ularga murojaat qilinsa undefined xatosi chiqadi",
            "Chunki bu SQL injection zaifligiga olib keladi",
            "Chunki bu so'rov juda sekin ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Issue interfeysida qancha maydon bor, SQL esa nechtasini tanlagan?",
        "explanation": "Issue interfeysi description, assigneeId, reporterId, createdAt kabi maydonlarni talab qiladi, lekin SQL faqat id/title/status'ni tanlagan - natijada bu maydonlar undefined bo'ladi, lekin TypeScript buni bilmaydi va keyinchalik murojaat qilinganda runtime xatosi chiqadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "IssueSummary xatosining yuzaga kelish jarayonini tartiblang",
        "description": "GET /issues/summary'da qisman SELECT'ni Issue bilan cast qilishdan boshlab, frontend'da xato chiqishigacha bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "SQL faqat id, title, status ustunlarini tanlaydi",
            "Natija pool.query<Issue>() orqali to'liq Issue turi sifatida e'lon qilinadi",
            "TypeScript compile vaqtida bu holatni tekshira olmaydi - description mavjud deb ishonadi",
            "Frontend issue.description.slice(...) chaqirganda TypeError: undefined xatosi chiqadi",
        ],
        "correct_order": [
            "SQL faqat id, title, status ustunlarini tanlaydi",
            "Natija pool.query<Issue>() orqali to'liq Issue turi sifatida e'lon qilinadi",
            "TypeScript compile vaqtida bu holatni tekshira olmaydi - description mavjud deb ishonadi",
            "Frontend issue.description.slice(...) chaqirganda TypeError: undefined xatosi chiqadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "To'g'ri yechim: qisman SELECT uchun qanday tur yaratiladi?",
        "description": "Faqat id, title, status ustunlarini qaytaradigan SQL so'rovi uchun, mavjud Issue turini qayta ishlatish o'rniga nima qilish tavsiya etiladi? (bitta so'z bilan javob bering: nima yaratiladi?)",
        "exercise_type": "text_input",
        "expected_answer": "interfeys",
        "hint": "SQL qaytaradigan aniq ustunlarga mos, YANGI, torroq nom bilan nima yoziladi?",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega SELECT * ishlatilganda bu xato kamroq ehtimolli?",
        "description": (
            "SELECT * FROM issues so'rovini pool.query<Issue>() bilan olish "
            "nima uchun SELECT id, title, status kabi qisman so'rovga "
            "qaraganda xavfsizroq? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "SELECT * jadvaldagi BARCHA ustunlarni qaytaradi, shuning uchun "
            "agar Issue interfeysi jadvaldagi haqiqiy ustunlarga mos "
            "bo'lsa, natija qatorida Issue talab qiladigan barcha maydonlar "
            "(description, assigneeId va h.k.) haqiqatan ham mavjud "
            "bo'ladi - tasodifan to'g'ri chiqadi. Qisman SELECT (masalan "
            "faqat id, title, status) esa ATAYLAB kamroq ustun qaytaradi - "
            "agar shu qisqartirilgan natija baribir to'liq Issue turi bilan "
            "cast qilinsa, tur va haqiqiy ma'lumot orasida nomuvofiqlik "
            "paydo bo'ladi, chunki SQL va TypeScript turi bir-biridan "
            "mustaqil yozilgan va hech kim ularni solishtirmagan."
        ),
        "hint": "SELECT * qancha ustun qaytaradi, Issue interfeysi qancha maydon talab qiladi - ular tasodifan mosmi yoki har doim?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "IssueForge — PostgreSQL CRUD (tiplashtirilgan so'rovlar)",
    "task_description": (
        "2-bosqichdagi xotiradagi massivni haqiqiy PostgreSQL jadvaliga "
        "o'tkazing: to'liq CRUD (GET ro'yxat + bitta issue, POST, PUT, "
        "DELETE) va parametrlashtirilgan so'rovlarni yozing. Qo'shimcha "
        "ravishda GET /issues/summary endpoint'ini, mavjud Issue turini "
        "QAYTA ISHLATMASDAN, alohida IssueSummary interfeysi bilan yozing."
    ),
    "task_requirements": (
        "• schema.sql: issues jadvali to'g'ri ustunlar bilan yaratilgan\n"
        "• GET /issues, GET /issues/:id, POST /issues, PUT /issues/:id, DELETE /issues/:id — barchasi pool.query<Issue>() bilan tiplashtirilgan\n"
        "• Barcha SQL so'rovlar parametrlashtirilgan ($1, $2, ...)\n"
        "• GET /issues/summary — faqat id/title/status qaytaradi, ALOHIDA IssueSummary interfeysi bilan (Issue emas)\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Node.js, Express, TypeScript, PostgreSQL, pg (node-postgres)",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Autentifikatsiya — JWT va tiplashtirilgan payload</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /login - JWT {userId, role} bilan chiqariladi"] --> TOKEN["Klient tokenni saqlaydi"]
    TOKEN --> PROTECTED["Himoyalangan route: Authorization header"]
    PROTECTED --> VERIFY["jwt.verify() - haqiqiy tur: JwtPayload | string"]
    VERIFY -->|"tekshiruvsiz 'as {userId, role}' cast"| TRUST["TypeScript: 'OK, obyekt ekan'"]
    TRUST --> BUG["Boshqa maqsaddagi token qayta ishlatilsa - userId/role undefined"]
</pre>

<p>Node.js/Express kursida JWT autentifikatsiyasini, parolni bcrypt bilan hash qilishni va himoyalangan route'lar uchun middleware zanjirini allaqachon o'rgangansiz. Bu darsda ularni TypeScript bilan tiplashtirasiz. Bu safar TypeScript'ning chegarasi ayniqsa nozik joyda ko'rinadi: <code>jsonwebtoken</code> kutubxonasining o'zi <code>jwt.verify()</code> uchun <code>JwtPayload | string</code> turini <strong>rasman e'lon qiladi</strong> — lekin ko'p dasturchilar buni e'tiborsiz qoldirib, to'g'ridan-to'g'ri o'z interfeysiga "cast" qiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — login: JWT'ni tiplashtirilgan payload bilan chiqarish</h4>
<pre><code># Terminal:
npm install jsonwebtoken bcrypt
npm install -D @types/jsonwebtoken @types/bcrypt</code></pre>
<pre><code>// backend/src/auth.ts
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const JWT_SECRET = process.env.JWT_SECRET as string;

interface AuthTokenPayload {
  userId: number;
  role: 'member' | 'admin';
}

export function issueToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });
}

app.post('/login', async (req: Request, res: Response) => {
  const user = await findUserByEmail(req.body.email);
  const ok = user && await bcrypt.compare(req.body.password, user.passwordHash);
  if (!ok) return res.status(401).json({ error: 'Email yoki parol noto\\'g\\'ri' });

  const token = issueToken({ userId: user!.id, role: user!.role });
  res.json({ token });
});</code></pre>

<h4>BLOKA 2 — himoyalangan route: jwt.verify() natijasini TO'G'RI tekshirish</h4>
<pre><code>// jsonwebtoken'ning O'ZI jwt.verify()ni shunday e'lon qiladi:
// function verify(token: string, secret: string): JwtPayload | string;
//                                                   ❗ HAM obyekt, HAM string bo'lishi mumkin!

function verifyAuthToken(token: string): AuthTokenPayload | null {
  const decoded = jwt.verify(token, JWT_SECRET);

  if (typeof decoded === 'string' || !('userId' in decoded) || !('role' in decoded)) {
    return null;   // ❗ RUNTIME'da tekshirilmoqda - shakl HAQIQATAN mosligi tasdiqlanmoqda
  }
  return decoded as AuthTokenPayload;   // Endi cast xavfsiz - tekshiruvdan keyin
}</code></pre>

<h4>BLOKA 3 — middleware: req.user'ni tiplashtirish</h4>
<pre><code>// backend/src/types/express.d.ts - Express Request'ni kengaytirish
declare global {
  namespace Express {
    interface Request {
      user?: AuthTokenPayload;
    }
  }
}

function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const payload = token ? verifyAuthToken(token) : null;
  if (!payload) return res.status(401).json({ error: 'Avtorizatsiyadan o\\'tilmagan' });

  req.user = payload;
  next();
}</code></pre>

<h3>🐛 Ataylab xato — jwt.verify() natijasini tekshiruvsiz cast qilish</h3>
<pre><code>// "Bu har doim AuthTokenPayload bo'ladi" deb, tekshiruv qadamini
// (BLOKA 2'dagi typeof/'userId' in tekshiruvini) o'tkazib yuborish:
function verifyAuthToken(token: string): AuthTokenPayload {
  const decoded = jwt.verify(token, JWT_SECRET) as AuthTokenPayload;   // ❌ tekshiruvsiz cast!
  return decoded;
}

// Loyihada BOSHQA maqsad uchun ham (masalan parolni tiklash) shu XIL
// jsonwebtoken kutubxonasi ishlatiladi, lekin BUTUNLAY BOSHQA shaklda:
// const resetToken = jwt.sign(user.email, JWT_SECRET);   // ❗ oddiy STRING, obyekt emas!

// Agar dasturchi xato bilan verifyAuthToken()ni reset-token uchun ham
// chaqirsa:
// const payload = verifyAuthToken(resetToken);
// payload.userId   -> undefined (chunki decoded aslida STRING edi!)
// payload.role     -> undefined
//
// ❌ tsc BUNI ANIQLAMAYDI - chunki "as AuthTokenPayload" TypeScript'ga
//    "ishon" deydi, jwt.verify()ning haqiqiy JwtPayload | string turini
//    butunlay e'tiborsiz qoldiradi.</code></pre>

<p><strong>Natija:</strong> <code>jsonwebtoken</code> kutubxonasi <code>jwt.verify()</code> uchun <strong>ataylab</strong> <code>JwtPayload | string</code> (union) turini e'lon qiladi — chunki JWT imzosi <strong>istalgan</strong> qiymat (obyekt HAM, oddiy satr HAM) ustida ishlashi mumkin. <code>as AuthTokenPayload</code> orqali <strong>tekshiruvsiz</strong> cast qilish shu union turini butunlay chetlab o'tadi. Agar shu <strong>umumiy</strong> tekshiruv funksiyasi loyihada boshqa, <strong>boshqacha shakldagi</strong> token uchun (masalan parolni tiklash — <code>jwt.sign(email, SECRET)</code>, oddiy satr) qayta ishlatilsa, <code>decoded</code> runtime'da <strong>haqiqatan ham</strong> <code>string</code> bo'lib chiqadi. TypeScript buni <strong>hech qachon</strong> ushlamaydi, chunki cast — bu "menga ishon" degani, tekshiruv emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega <code>jwt.verify()</code>ning e'lon qilingan turi <code>JwtPayload | string</code>?</h4>
<p>JWT — bu shunchaki imzolangan ma'lumot. <code>jwt.sign()</code>ga istalgan qiymat (obyekt <strong>yoki</strong> oddiy satr) berish mumkin, shuning uchun <code>jwt.verify()</code> ham nazariy jihatdan <strong>ikkalasini</strong> qaytarishi mumkin. Kutubxona buni <strong>halol</strong> e'lon qiladi — muammo shundaki, dasturchilar bu union turini ko'pincha e'tiborsiz qoldirib, to'g'ridan-to'g'ri cast qiladi.</p>

<h4>2. BLOKA 2'dagi <code>typeof decoded === 'string'</code> tekshiruvi nima uchun kerak?</h4>
<p>Bu — <strong>runtime narrowing</strong> (turni toraytirish): kod <code>decoded</code>ning haqiqatan ham obyekt ekanligini va kerakli maydonlar (<code>userId</code>, <code>role</code>) mavjudligini <strong>ishga tushgandan keyin</strong> tekshiradi. Faqat shundan keyingina <code>as AuthTokenPayload</code> cast qilish <strong>xavfsiz</strong> — chunki u endi haqiqiy tekshiruv natijasiga asoslangan.</p>

<h4>3. Nega bir xil <code>verifyAuthToken()</code> funksiyasini boshqa turdagi token uchun qayta ishlatish xavfli?</h4>
<p>TypeScript funksiyaning <strong>e'lon qilingan</strong> qaytish turiga (<code>AuthTokenPayload</code>) ishonadi, lekin bu funksiya <strong>ichida</strong> haqiqiy tekshiruv yo'q bo'lsa, funksiya haqiqatda <strong>istalgan</strong> shakldagi tokenni qabul qiladi va "ishonch bilan" noto'g'ri turni qaytaradi — chaqiruvchi tomon esa bundan bexabar qoladi.</p>

<h4>4. <code>declare global { namespace Express {...} } }</code> nima uchun ishlatiladi?</h4>
<p>Express'ning o'z <code>Request</code> interfeysida standart holda <code>user</code> maydoni yo'q. Bu yozuv orqali loyihaga xos <code>user</code> maydonini <strong>butun loyiha bo'ylab</strong> <code>Request</code> turiga qo'shib qo'yish mumkin — shunda <code>req.user</code>ga har bir route handler'da xavfsiz murojaat qilish mumkin bo'ladi.</p>

<h4>5. Bu xato nega ayniqsa xavfli — nafaqat funksional, balki xavfsizlik nuqtai nazaridan ham?</h4>
<p>Agar <code>userId</code>/<code>role</code> kutilmaganda <code>undefined</code> bo'lib chiqsa, va avtorizatsiya tekshiruvi (masalan <code>if (req.user.role === 'admin')</code>) buni hisobga olmasa, natija ikki xil bo'lishi mumkin: yo foydalanuvchi <strong>noto'g'ri rad etiladi</strong> (funksional xato), yoki — agar tekshiruv teskari yozilgan bo'lsa — <strong>noto'g'ri ruxsat beriladi</strong> (xavfsizlik zaifligi). Shuning uchun autentifikatsiya kodida runtime tekshiruvini o'tkazib yuborish ayniqsa xavfli.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>jwt.verify()</code>ning haqiqiy turi <code>JwtPayload | string</code> — kutubxonaning o'zi buni ochiq e'lon qiladi</li>
<li>✅ Cast qilishdan oldin <code>typeof</code> va <code>'field' in obj</code> orqali runtime narrowing qilish xavfsiz cast'ning sharti</li>
<li>✅ Umumiy tekshiruv funksiyasini boshqa shakldagi token uchun qayta ishlatish — turlar mos kelmasligiga olib kelishi mumkin</li>
<li>✅ Express <code>Request</code>ni <code>declare global</code> orqali kengaytirish — <code>req.user</code>ni butun loyihada xavfsiz tiplashtirish usuli</li>
<li>✅ Autentifikatsiya kodida tekshiruvsiz cast — funksional xatodan tashqari, xavfsizlik zaifligiga ham olib kelishi mumkin</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 4-BOSQICH: Autentifikatsiya - JWT va tiplashtirilgan payload
// ════════════════════════════════════════════════════════════════════

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { Request, Response, NextFunction } from 'express';

const JWT_SECRET = process.env.JWT_SECRET as string;

interface AuthTokenPayload {
  userId: number;
  role: 'member' | 'admin';
}

// ─────────────────────────────────────────────────────────────────────
// 1) Token chiqarish
// ─────────────────────────────────────────────────────────────────────

export function issueToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' });
}

// ─────────────────────────────────────────────────────────────────────
// 2) Token tekshirish - runtime narrowing bilan XAVFSIZ
// ─────────────────────────────────────────────────────────────────────

function verifyAuthToken(token: string): AuthTokenPayload | null {
  const decoded = jwt.verify(token, JWT_SECRET);

  if (typeof decoded === 'string' || !('userId' in decoded) || !('role' in decoded)) {
    return null;
  }
  return decoded as AuthTokenPayload;
}

// ─────────────────────────────────────────────────────────────────────
// 3) Express Request'ni kengaytirish + middleware
// ─────────────────────────────────────────────────────────────────────

declare global {
  namespace Express {
    interface Request {
      user?: AuthTokenPayload;
    }
  }
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const payload = token ? verifyAuthToken(token) : null;
  if (!payload) return res.status(401).json({ error: "Avtorizatsiyadan o'tilmagan" });

  req.user = payload;
  next();
}

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - tekshiruvsiz cast (izohda)
// ─────────────────────────────────────────────────────────────────────

// function verifyAuthToken(token: string): AuthTokenPayload {
//   const decoded = jwt.verify(token, JWT_SECRET) as AuthTokenPayload;   // tekshiruvsiz!
//   return decoded;
// }
// Boshqa maqsaddagi (masalan parolni tiklash) string-token bilan
// qayta ishlatilsa: payload.userId -> undefined, payload.role -> undefined
"""

L4_EX = [
    {
        "title": "jwt.verify()ning haqiqiy e'lon qilingan qaytish turi qanday?",
        "description": "jsonwebtoken kutubxonasida jwt.verify(token, secret) funksiyasi qanday turni qaytarishi rasman e'lon qilingan?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim faqat obyekt turi (JwtPayload)",
            "JwtPayload | string - ham obyekt, ham oddiy satr bo'lishi mumkin",
            "Har doim faqat string turi",
            "Har doim any turi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "JWT payload nazariy jihatdan oddiy satr ham bo'lishi mumkin, obyekt shart emas.",
        "explanation": "jsonwebtoken kutubxonasi jwt.verify() uchun JwtPayload | string union turini e'lon qiladi, chunki jwt.sign()ga obyekt yoki oddiy satr berilishi mumkin, va verify ham shunga mos ravishda ikkalasini qaytarishi mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "typeof decoded === 'string' tekshiruvi nima uchun kerak?",
        "description": "verifyAuthToken() funksiyasida cast qilishdan oldin typeof decoded === 'string' va 'userId' in decoded tekshiruvlari nima uchun yoziladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni chiroyliroq ko'rsatish uchun, funksional ahamiyati yo'q",
            "decoded haqiqatan ham kutilgan shaklga ega ekanligini runtime'da tasdiqlash uchun - shundan keyingina cast xavfsiz bo'ladi",
            "jwt.verify()ni tezroq ishlashga majburlash uchun",
            "Faqat TypeScript xatosini yashirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu - runtime narrowing, ya'ni turni ishga tushgandan keyin toraytirish.",
        "explanation": "Bu tekshiruvlar decoded qiymatining haqiqatan ham obyekt ekanligini va kerakli maydonlar mavjudligini runtime'da tasdiqlaydi - shundan keyingina keyingi cast xavfsiz hisoblanadi, chunki u haqiqiy tekshiruv natijasiga asoslangan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Umumiy tekshiruv funksiyasi noto'g'ri qayta ishlatilganda nima yuz beradi - tartiblang",
        "description": "verifyAuthToken() tekshiruvsiz cast bilan yozilgan holatda, uni parolni tiklash tokeni uchun qayta ishlatilganda yuz beradigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Parolni tiklash uchun jwt.sign(email, SECRET) - oddiy STRING sifatida token yaratiladi",
            "Dasturchi xato bilan shu tokenni verifyAuthToken() orqali tekshiradi",
            "jwt.verify() runtime'da haqiqatan ham string qaytaradi, lekin 'as AuthTokenPayload' bu holatni yashiradi",
            "payload.userId va payload.role undefined bo'lib chiqadi, lekin tsc buni compile vaqtida aniqlay olmagan",
        ],
        "correct_order": [
            "Parolni tiklash uchun jwt.sign(email, SECRET) - oddiy STRING sifatida token yaratiladi",
            "Dasturchi xato bilan shu tokenni verifyAuthToken() orqali tekshiradi",
            "jwt.verify() runtime'da haqiqatan ham string qaytaradi, lekin 'as AuthTokenPayload' bu holatni yashiradi",
            "payload.userId va payload.role undefined bo'lib chiqadi, lekin tsc buni compile vaqtida aniqlay olmagan",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Express Request'ni kengaytirish uchun ishlatiladigan kalit so'z",
        "description": "req.user kabi maydonni butun loyiha bo'ylab Express'ning Request turiga qo'shish uchun qanday TypeScript konstruksiyasi ishlatiladi? (masalan: declare xxx)",
        "exercise_type": "text_input",
        "expected_answer": "declare global",
        "hint": "Bu global namespace deklaratsiyasi bilan boshlanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega autentifikatsiya kodida tekshiruvsiz cast ayniqsa xavfli?",
        "description": (
            "verifyAuthToken() funksiyasida jwt.verify() natijasi runtime "
            "tekshiruvisiz to'g'ridan-to'g'ri AuthTokenPayload sifatida "
            "cast qilinsa, bu nafaqat funksional, balki xavfsizlik "
            "nuqtai nazaridan nega ayniqsa xavfli bo'lishi mumkin? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar decoded qiymati kutilgan obyekt shaklida bo'lmasa (masalan "
            "boshqa maqsaddagi string-token noto'g'ri qayta ishlatilgan "
            "bo'lsa), tekshiruvsiz cast tufayli userId va role kabi "
            "maydonlar undefined bo'lib chiqadi, lekin TypeScript bu holatni "
            "compile vaqtida hech qachon aniqlay olmaydi. Agar avtorizatsiya "
            "tekshiruvi (masalan if (req.user.role === 'admin')) bu holatni "
            "hisobga olmasa, natija ikki xil bo'lishi mumkin: yoki "
            "foydalanuvchi asossiz ravishda rad etiladi (funksional xato), "
            "yoki - agar tekshiruv mantig'i teskari yozilgan bo'lsa (masalan "
            "'agar role \\'admin\\' EMAS bo'lsa rad et' o'rniga xato yozilgan "
            "holatda) - undefined qiymat kutilmagan tarzda ruxsat berish "
            "yo'lini ochib qo'yishi mumkin, bu esa jiddiy xavfsizlik "
            "zaifligi hisoblanadi."
        ),
        "hint": "Agar req.user.role undefined bo'lib chiqsa, avtorizatsiya tekshiruvi buni qanday noto'g'ri talqin qilishi mumkin?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "IssueForge — Autentifikatsiya (JWT + tiplashtirilgan payload)",
    "task_description": (
        "Foydalanuvchi ro'yxatdan o'tishi (bcrypt bilan parol hash) va "
        "kirishi (JWT chiqarish) uchun endpoint'lar yozing. Himoyalangan "
        "route'lar uchun middleware yarating — jwt.verify() natijasini "
        "runtime'da tekshirmasdan cast QILMANG, avval typeof/'field' in "
        "orqali narrowing qiling."
    ),
    "task_requirements": (
        "• POST /register — bcrypt bilan parol hash qilinadi\n"
        "• POST /login — muvaffaqiyatli bo'lsa AuthTokenPayload asosida JWT qaytaradi\n"
        "• requireAuth middleware — jwt.verify() natijasini runtime'da tekshirib, shundan keyin cast qiladi\n"
        "• Express Request declare global orqali kengaytirilgan, req.user tiplashtirilgan\n"
        "• Himoyalanmagan (noto'g'ri/yo'q token bilan) so'rov 401 qaytaradi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Node.js, Express, TypeScript, jsonwebtoken, bcrypt",
    "task_deadline_days": 4,
}


L5_TEXT = """\
<h2>5-bosqich: React frontend + Redux Toolkit (TypeScript) — backend/frontend orasidagi "sukut" farq</h2>

<pre class="mermaid">
flowchart LR
    BACKEND["Backend: assigneeId -> assignee{id,name} qilib o'zgartiriladi"] --> API["API javobi yangilanadi"]
    SHARED["shared/types.ts YANGILANMAYDI"] -.->|"eskicha qoladi"| FRONTEND
    API --> FETCH["fetchJson&lt;Issue&gt;() - tekshiruvsiz assertion"]
    FETCH --> UI["IssueCard: issue.assigneeId - ENDI har doim undefined"]
    UI --> SILENT["🤫 Xato YO'Q, lekin UI HAR DOIM 'Tayinlanmagan' ko'rsatadi"]
</pre>

<p>React: Redux Toolkit, TypeScript va Testlash kursida <code>configureStore</code>, <code>createSlice</code>, <code>createAsyncThunk</code> va tiplashtirilgan hook'larni (<code>useAppSelector</code>/<code>useAppDispatch</code>) allaqachon o'rgangansiz. Bu darsda ularni haqiqiy, o'zingiz yozgan backend bilan ishlatasiz. Bu safar TypeScript'ning chegarasi eng <strong>xavfli</strong> shaklda ko'rinadi — chunki bu safar hech qanday xato, hech qanday crash <strong>bo'lmaydi</strong>. UI shunchaki <strong>noto'g'ri</strong> ma'lumot ko'rsatadi, sukut saqlab.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — createAsyncThunk: shared Issue turi bilan haqiqiy API'dan olish</h4>
<pre><code>// frontend/src/api/fetchJson.ts
export async function fetchJson&lt;T&gt;(url: string): Promise&lt;T&gt; {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`So'rov xato: ${res.status}`);
  return res.json() as Promise&lt;T&gt;;   // ❗ tekshiruvsiz assertion - 2-darsdagi kabi tanish naqsh
}

// frontend/src/features/issuesSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Issue } from '../../../shared/types';
import { fetchJson } from '../api/fetchJson';

export const fetchIssues = createAsyncThunk('issues/fetch', async () => {
  return fetchJson&lt;Issue[]&gt;('/api/issues');
});

const issuesSlice = createSlice({
  name: 'issues',
  initialState: { list: [] as Issue[], status: 'idle' as 'idle' | 'loading' | 'succeeded' | 'failed' },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchIssues.pending, (state) =&gt; { state.status = 'loading'; })
      .addCase(fetchIssues.fulfilled, (state, action) =&gt; {
        state.status = 'succeeded';
        state.list = action.payload;
      });
  },
});

export default issuesSlice.reducer;</code></pre>

<h4>BLOKA 2 — tiplashtirilgan hook'lar (React: RTK+TS kursidan tanish)</h4>
<pre><code>// frontend/src/store/hooks.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch: () =&gt; AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;</code></pre>

<h4>BLOKA 3 — komponent: Pick&lt;Issue, ...&gt; orqali props'ni SINXRON ushlab turish</h4>
<pre><code>// frontend/src/components/IssueCard.tsx
// ❗ props'ni QO'LDA qayta yozish o'rniga, Pick orqali Issue'dan OLINADI -
// shunda Issue o'zgarsa, IssueCardProps ham AVTOMATIK yangilanadi
type IssueCardProps = Pick&lt;Issue, 'id' | 'title' | 'status' | 'assigneeId'&gt;;

function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
  return (
    &lt;div className="issue-card"&gt;
      &lt;h4&gt;{title}&lt;/h4&gt;
      &lt;span&gt;{status}&lt;/span&gt;
      &lt;p&gt;{assigneeId ? `Tayinlangan: #${assigneeId}` : 'Tayinlanmagan'}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<h3>🐛 Ataylab xato — backend maydonni o'zgartiradi, shared/types.ts yangilanmaydi</h3>
<pre><code>// Backend keyinroq (masalan bir necha hafta o'tib) rivojlanadi:
// endi har bir issue'ga tayinlangan foydalanuvchining FAQAT id'sini emas,
// balki ism-familiyasini ham qaytarish kerak bo'ladi. Backend'dagi
// dasturchi API javobini o'zgartiradi:
//
// ESKI javob: { ..., "assigneeId": 7 }
// YANGI javob: { ..., "assignee": { "id": 7, "name": "Aziz" } }
//
// LEKIN: shared/types.ts BU YERDA YANGILANMAYDI - u hali ham eski
// "assigneeId: number | null" maydonini e'lon qiladi!

// frontend/src/components/IssueCard.tsx - HECH NARSA o'zgartirilmagan:
function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
  return (
    &lt;div className="issue-card"&gt;
      &lt;h4&gt;{title}&lt;/h4&gt;
      &lt;p&gt;{assigneeId ? `Tayinlangan: #${assigneeId}` : 'Tayinlanmagan'}&lt;/p&gt;
    &lt;/div&gt;
  );
}
// fetchJson&lt;Issue[]&gt;() tekshiruvsiz assertion tufayli hech qanday
// xato bermaydi. TypeScript ham xursand - Issue turi "assigneeId bor"
// deb hisoblaydi. LEKIN haqiqiy runtime javobida bu maydon ENDI YO'Q!
//
// 🤫 issue.assigneeId har doim undefined - console'da HECH QANDAY
//    xato yo'q, sahifa CRASH bo'lmaydi. Shunchaki HAR BIR issue
//    "Tayinlanmagan" deb ko'rsatiladi - hatto tayinlangan bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> bu — capstone davomida ko'rgan eng <strong>jimgina</strong> xato turi. Oldingi darslarda xato <strong>crash</strong> yoki <strong>401</strong> kabi ko'rinadigan natija berardi. Bu yerda esa hech narsa "buzilmaydi" — sahifa oddiy ishlaydi, konsolda xato yo'q, faqat <strong>ma'lumot noto'g'ri</strong>. Sababi: <code>fetchJson&lt;Issue[]&gt;()</code>dagi <code>as Promise&lt;T&gt;</code> tekshiruvsiz assertion + <code>shared/types.ts</code>ning backend o'zgarishi bilan <strong>sinxronlanmay qolishi</strong> — 1-darsda tanishgan xavfning aynan o'zi, endi <strong>real, ko'rinadigan</strong> oqibat bilan.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>Pick&lt;Issue, 'id' | 'title' | 'status' | 'assigneeId'&gt;</code> nima uchun qo'lda yozishdan yaxshiroq?</h4>
<p><code>Pick</code> — TypeScript Asoslari kursidan tanish utility type — component prop turini <strong>to'g'ridan-to'g'ri</strong> <code>Issue</code>dan hosil qiladi. Agar <code>Issue</code>ning <code>title</code> maydoni turi o'zgarsa, <code>IssueCardProps</code> ham <strong>avtomatik</strong> yangilanadi. Qo'lda yozilgan interfeys esa <strong>hech qachon</strong> o'zgarmaydi, hatto manba o'zgarsa ham.</p>

<h4>2. Nega bu xato <strong>ayniqsa</strong> xavfli — oldingilardan farqli?</h4>
<p>2, 3, 4-darslardagi xatolar <strong>ko'rinadigan</strong> natija berardi: crash, noto'g'ri saqlangan ma'lumot, 401 xato. Bu yerda esa dastur <strong>xatosiz ishlayotgandek</strong> ko'rinadi — faqat ma'lumot <strong>sukut saqlab</strong> noto'g'ri. Bunday xatolarni topish ancha qiyin, chunki hech qanday signal (xato, crash) yo'q — faqat "nega bu issue tayinlangan bo'lsa ham 'Tayinlanmagan' deb ko'rsatilyapti?" degan savol paydo bo'ladi.</p>

<h4>3. <code>shared/types.ts</code> 1-darsda tavsiya qilingan edi — nega u bu safar yordam bermadi?</h4>
<p><code>shared/types.ts</code> faqat backend va frontend <strong>ikkalasi ham uni import qilib, HAR IKKALASI YANGILANGANDA</strong> yordam beradi. Agar backend API javobini o'zgartirsa-yu, <code>shared/types.ts</code>ni yangilashni <strong>unutsa</strong>, bu fayl endi <strong>yolg'on hujjat</strong>ga aylanadi — u haqiqiy runtime javobiga emas, balki <strong>eski</strong> holatga mos keladi.</p>

<h4>4. Bunday xatoni qanday aniqlash mumkin?</h4>
<p>Runtime validatsiyasi (masalan Zod kabi kutubxona bilan API javobini haqiqatan tekshirish) yoki backend/frontend integratsiya testlari (6-darsda ko'rasiz) — bularsiz bunday "sukut" xatolarni faqat <strong>qo'lda sinab ko'rish</strong> yoki foydalanuvchi shikoyati orqali topish mumkin.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>1-darsda bu xavf faqat <strong>nazariy</strong> edi ("kelajakda xavfli bo'lishi mumkin"). Endi, 5-darsda, siz uni <strong>haqiqiy, ko'rinmas</strong> UI xatosi sifatida ko'rdingiz — bu TypeScript'ning "compile vaqtida tekshiradi, runtime'da emas" degan asosiy g'oyasining <strong>eng jiddiy</strong> oqibati: xato hech qachon "qichqirmaydi", u shunchaki <strong>noto'g'ri</strong> qoladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>Pick&lt;T, K&gt;</code> — component prop turini manba interfeysdan avtomatik hosil qilish usuli</li>
<li>✅ Backend API javobini o'zgartirganda <code>shared/types.ts</code>ni yangilashni unutish — eng "sukut" xato turi</li>
<li>✅ Bunday xatolarda crash yo'q, faqat noto'g'ri ma'lumot jimgina ko'rsatiladi</li>
<li>✅ <code>shared/types.ts</code> faqat ikkala tomon uni <strong>doim</strong> yangilab borsagina foydali</li>
<li>✅ Runtime validatsiyasi yoki integratsiya testlari — bunday sukut xatolarni ushlaydigan yagona vositalar</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 5-BOSQICH: React frontend + Redux Toolkit (TypeScript)
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) fetchJson<T> - tekshiruvsiz assertion (2-darsdagi kabi tanish naqsh)
// ─────────────────────────────────────────────────────────────────────

export async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`So'rov xato: ${res.status}`);
  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────────────────────────────
// 2) issuesSlice.ts - createAsyncThunk + shared Issue turi
// ─────────────────────────────────────────────────────────────────────

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { Issue } from '../../../shared/types';

export const fetchIssues = createAsyncThunk('issues/fetch', async () => {
  return fetchJson<Issue[]>('/api/issues');
});

const issuesSlice = createSlice({
  name: 'issues',
  initialState: { list: [] as Issue[], status: 'idle' as 'idle' | 'loading' | 'succeeded' | 'failed' },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchIssues.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchIssues.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.list = action.payload;
      });
  },
});

export default issuesSlice.reducer;

// ─────────────────────────────────────────────────────────────────────
// 3) store/hooks.ts - tiplashtirilgan hook'lar
// ─────────────────────────────────────────────────────────────────────

import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// ─────────────────────────────────────────────────────────────────────
// 4) IssueCard.tsx - Pick<Issue, ...> orqali props (izohda - JSX)
// ─────────────────────────────────────────────────────────────────────

// type IssueCardProps = Pick<Issue, 'id' | 'title' | 'status' | 'assigneeId'>;
//
// function IssueCard({ id, title, status, assigneeId }: IssueCardProps) {
//   return (
//     <div className="issue-card">
//       <h4>{title}</h4>
//       <span>{status}</span>
//       <p>{assigneeId ? `Tayinlangan: #${assigneeId}` : 'Tayinlanmagan'}</p>
//     </div>
//   );
// }

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - backend maydonni o'zgartiradi, shared/types.ts eski qoladi (izohda)
// ─────────────────────────────────────────────────────────────────────

// Backend YANGI javob: { ..., "assignee": { "id": 7, "name": "Aziz" } }
// shared/types.ts ESKI: assigneeId: number | null  (yangilanmagan!)
// Natija: issue.assigneeId HAR DOIM undefined - lekin xato yo'q, crash yo'q,
// faqat UI har doim "Tayinlanmagan" deb ko'rsatadi.
"""

L5_EX = [
    {
        "title": "Pick<Issue, 'id' | 'title'> nima qiladi?",
        "description": "type IssueCardProps = Pick<Issue, 'id' | 'title' | 'status' | 'assigneeId'> yozuvi nima uchun qo'lda yozilgan interfeysdan yaxshiroq?",
        "exercise_type": "multiple_choice",
        "options": [
            "U kodni tezroq ishlashga majburlaydi",
            "U component prop turini to'g'ridan-to'g'ri Issue'dan hosil qiladi - Issue o'zgarsa, bu ham avtomatik yangilanadi",
            "U runtime'da API javobini avtomatik tekshiradi",
            "Bu faqat production build uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu TypeScript Asoslari kursidan tanish utility type.",
        "explanation": "Pick<Issue, ...> component prop turini to'g'ridan-to'g'ri Issue interfeysidan hosil qiladi - shuning uchun Issue o'zgarganda IssueCardProps ham avtomatik yangilanadi, qo'lda yozilgan interfeys esa hech qachon o'zgarmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Bu darsdagi xato nega oldingilardan farq qiladi?",
        "description": "5-bosqichdagi 'ataylab xato' 2-4-darslardagi xatolardan asosan nimasi bilan farq qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bu xato compile vaqtida tsc tomonidan ushlanadi",
            "Bu xato hech qanday crash yoki console xatosi bermaydi - UI shunchaki sukut saqlab noto'g'ri ma'lumot ko'rsatadi",
            "Bu xato faqat mobil qurilmalarda yuzaga keladi",
            "Bu xato faqat production build'da paydo bo'ladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Sahifa ishlab turibdimi? Konsolda xato bormi?",
        "explanation": "Bu xato hech qanday crash yoki console xatosi bermaydi - dastur oddiy ishlayotgandek ko'rinadi, faqat assigneeId har doim undefined bo'lgani uchun UI sukut saqlab noto'g'ri ('Tayinlanmagan') ma'lumot ko'rsatadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "'Sukut' xatoning yuzaga kelish jarayonini tartiblang",
        "description": "Backend assigneeId'ni assignee obyektiga o'zgartirishidan boshlab, UI'da noto'g'ri ma'lumot ko'rsatilishigacha bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Backend API javobini assigneeId'dan assignee{id,name} obyektiga o'zgartiradi",
            "shared/types.ts yangilanishi UNUTILADI - hali ham eski assigneeId maydonini e'lon qiladi",
            "fetchJson<Issue[]>() tekshiruvsiz assertion tufayli hech qanday xato bermaydi",
            "IssueCard issue.assigneeId'ga murojaat qiladi - bu har doim undefined, UI sukut saqlab 'Tayinlanmagan' ko'rsatadi",
        ],
        "correct_order": [
            "Backend API javobini assigneeId'dan assignee{id,name} obyektiga o'zgartiradi",
            "shared/types.ts yangilanishi UNUTILADI - hali ham eski assigneeId maydonini e'lon qiladi",
            "fetchJson<Issue[]>() tekshiruvsiz assertion tufayli hech qanday xato bermaydi",
            "IssueCard issue.assigneeId'ga murojaat qiladi - bu har doim undefined, UI sukut saqlab 'Tayinlanmagan' ko'rsatadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "shared/types.ts qachon foydali bo'ladi?",
        "description": "shared/types.ts 1-darsda tavsiya qilingan, lekin bu darsda yordam bermadi. U qanday shartda foydali bo'ladi? (bitta so'z bilan javob bering: nima qilinishi kerak, ikkala tomonda ham?)",
        "exercise_type": "text_input",
        "expected_answer": "yangilanishi",
        "hint": "Fayl o'zi sehrli emas - u faqat ... qilinganda ishlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bunday 'sukut' xatolarni topish ayniqsa qiyin?",
        "description": (
            "assigneeId har doim undefined bo'lib, UI hech qanday xatosiz "
            "shunchaki noto'g'ri ma'lumot ko'rsatayotgan holatni "
            "aniqlash nega ayniqsa qiyin? Bunday xatolarni qanday "
            "usullar bilan ushlash mumkin? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Bunday xatolarni topish qiyin, chunki oddiy signal (console "
            "xatosi, sahifa crash'i, HTTP xato kodi) umuman yo'q - dastur "
            "tashqi ko'rinishda mukammal ishlayotgandek tuyuladi. Muammoni "
            "sezish uchun kimdir aniq bir issue'ning HAQIQATDA tayinlangan "
            "ekanligini bilishi va UI'da 'Tayinlanmagan' deb ko'rsatilganini "
            "qo'lda solishtirishi kerak - bu tasodifiy sinov orqali kam "
            "topiladi. Bunday xatolarni ushlash uchun: (1) runtime "
            "validatsiyasi (masalan Zod kabi kutubxona bilan kelgan API "
            "javobini haqiqiy tekshirish, faqat tur sifatida e'lon qilish "
            "emas), yoki (2) backend va frontend orasidagi integratsiya "
            "testlari (haqiqiy API javobini frontend kodiga uzatib, "
            "natijani tekshirish) ishlatiladi."
        ),
        "hint": "Bunday xatoda console'da biror narsa chiqadimi? Sahifa ishlayaptimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "IssueForge — React frontend + Redux Toolkit (TypeScript)",
    "task_description": (
        "3-4-bosqichlardagi backend API'ga ulangan React + Redux Toolkit "
        "frontend quring: issues ro'yxatini createAsyncThunk orqali oling, "
        "tiplashtirilgan hook'lardan foydalaning, va IssueCard "
        "komponentining props turini Pick<Issue, ...> orqali (qo'lda "
        "yozilgan interfeys EMAS) hosil qiling."
    ),
    "task_requirements": (
        "• issuesSlice.ts — createAsyncThunk orqali /api/issues'dan Issue[] oladi\n"
        "• store/hooks.ts — useAppDispatch/useAppSelector tiplashtirilgan\n"
        "• IssueCard.tsx — props turi Pick<Issue, ...> orqali hosil qilingan, qo'lda dublikat qilinmagan\n"
        "• Issues ro'yxati sahifada to'g'ri ko'rsatiladi (loading/succeeded holatlari bilan)\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "React, Redux Toolkit, TypeScript",
    "task_deadline_days": 5,
}


L6_TEXT = """\
<h2>6-bosqich: Testing (Jest + React Testing Library) — "yashil" test hammasi ishlayapti degani emas</h2>

<pre class="mermaid">
flowchart LR
    MOCK["Test: mock issue obyekti yoziladi"] --> TYPE{"Issue turi bilanmi, yoki 'as any' bilanmi?"}
    TYPE -->|"Issue turi bilan"| SAFE["Backend Issue shaklini o'zgartirsa - COMPILE XATOSI"]
    TYPE -->|"'as any' bilan"| BLIND["Backend Issue shaklini o'zgartirsa - test HAMON YASHIL"]
    BLIND --> FALSE["🟢 Yashil test, lekin haqiqiy integratsiya BUZILGAN"]
</pre>

<p>React: Redux Toolkit, TypeScript va Testlash kursida Jest + React Testing Library'ni, <code>render</code>/<code>screen</code> so'rovlarini va API'ni mock qilishni allaqachon o'rgangansiz. Bu dars — capstone bo'ylab ko'rgan barcha xatolarni <strong>ushlashi kerak bo'lgan</strong> vosita haqida: testlar. Lekin shu yerda oxirgi, eng nozik haqiqat ochiladi: <strong>test yozishning o'zi</strong> ham, agar noto'g'ri yozilsa, xuddi interfeys kabi — <strong>yolg'on ishonch</strong> berishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Jest + React Testing Library sozlash (React: RTK+TS kursidan tanish)</h4>
<pre><code># Terminal:
npm install -D jest @testing-library/react @testing-library/jest-dom ts-jest @types/jest</code></pre>

<h4>BLOKA 2 — IssueCard'ni TO'G'RI: mock'ni Issue turi bilan yozish</h4>
<pre><code>// frontend/src/components/IssueCard.test.tsx
import { render, screen } from '@testing-library/react';
import IssueCard from './IssueCard';
import { Issue } from '../../../shared/types';

// ❗ mock obyekt Issue turi bilan e'lon qilingan - agar Issue o'zgarsa,
//    bu qator COMPILE XATOSI beradi, testni yozgan kishi DARHOL biladi!
const mockIssue: Issue = {
  id: 1,
  title: 'Login sahifasi buzilgan',
  description: 'Parolni tiklash tugmasi ishlamayapti',
  status: 'open',
  assigneeId: 7,
  reporterId: 2,
  createdAt: '2026-01-01T10:00:00Z',
};

test('IssueCard sarlavha va holatni ko\\'rsatadi', () =&gt; {
  render(&lt;IssueCard {...mockIssue} /&gt;);
  expect(screen.getByText('Login sahifasi buzilgan')).toBeInTheDocument();
  expect(screen.getByText('open')).toBeInTheDocument();
});</code></pre>

<h4>BLOKA 3 — async thunk'ni test qilish: fetch'ni mock qilish</h4>
<pre><code>// frontend/src/features/issuesSlice.test.ts
import { configureStore } from '@reduxjs/toolkit';
import issuesReducer, { fetchIssues } from './issuesSlice';
import { Issue } from '../../../shared/types';

test('fetchIssues muvaffaqiyatli holatni yangilaydi', async () =&gt; {
  const mockData: Issue[] = [
    { id: 1, title: 'Test', description: '...', status: 'open',
      assigneeId: null, reporterId: 1, createdAt: '2026-01-01T00:00:00Z' },
  ];
  global.fetch = jest.fn(() =&gt;
    Promise.resolve({ ok: true, json: () =&gt; Promise.resolve(mockData) })
  ) as jest.Mock;

  const store = configureStore({ reducer: { issues: issuesReducer } });
  await store.dispatch(fetchIssues());

  expect(store.getState().issues.list).toEqual(mockData);
});</code></pre>

<h3>🐛 Ataylab xato — mock'ni "as any" bilan yozish</h3>
<pre><code>// "Tezroq yozaman" deb, Issue turini import qilish o'rniga:
const mockIssue = {
  id: 1,
  title: 'Login sahifasi buzilgan',
  status: 'open',
  assigneeId: 7,
} as any;   // ❌ BUTUN tur tekshiruvini o'chirib qo'yadi!

test('IssueCard sarlavha va holatni ko\\'rsatadi', () =&gt; {
  render(&lt;IssueCard {...mockIssue} /&gt;);
  expect(screen.getByText('Login sahifasi buzilgan')).toBeInTheDocument();
});
// ✅ Test YASHIL - hozircha hammasi ishlayotgandek ko'rinadi.

// ENDI 5-bosqichdagi voqea sodir bo'ladi: backend assigneeId'ni
// assignee{id,name}'ga o'zgartiradi. Haqiqiy IssueCard komponenti
// endi buziladi (5-darsda ko'rganingizdek). LEKIN:
//
// ❌ Bu test HAMON YASHIL turadi! Chunki mockIssue "as any" orqali
//    yozilgan - u Issue interfeysidan MUSTAQIL, hech qachon "Issue
//    o'zgardi, mockni yangilash kerak" degan SIGNAL bermaydi.
//    Test "IssueCard ishlayapti" deb yolg'on ishonch beradi, garchi
//    production'da u haqiqatan BUZILGAN bo'lsa ham.</code></pre>

<p><strong>Natija:</strong> <code>as any</code> — TypeScript'ning <strong>butun</strong> tur tekshiruvi tizimini <strong>o'chirib qo'yadigan</strong> "favqulodda chiqish eshigi". Agar mock ma'lumot <code>Issue</code> turi bilan yozilgan bo'lsa, va keyinchalik <code>Issue</code> interfeysi o'zgarsa (masalan 5-bosqichdagi kabi), <code>tsc</code> testni <strong>compile qila olmaydi</strong> — bu testni yozgan kishiga <strong>darhol</strong> signal: "diqqat, mock ma'lumot endi eskirgan". <code>as any</code> bilan yozilgan mock esa bunday signalni <strong>hech qachon</strong> bermaydi — test doim "yashil" bo'lib qolaveradi, garchi u endi <strong>haqiqiy</strong> production kodini sinamayotgan bo'lsa ham.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega mock obyektni <code>Issue</code> turi bilan (<code>as any</code> EMAS) yozish muhim?</h4>
<p><code>const mockIssue: Issue = {...}</code> yozilganda, TypeScript mock obyektni <strong>haqiqiy</strong> <code>Issue</code> interfeysiga qarshi tekshiradi — xuddi production kodidagi har qanday boshqa qiymat kabi. Bu mock'ni <strong>doim, avtomatik ravishda</strong> haqiqiy tur bilan sinxron ushlab turadi.</p>

<h4>2. <code>as any</code> aslida nima qiladi?</h4>
<p><code>any</code> — TypeScript Asoslari kursida o'rgangan eng "xavfli" tur: u <strong>butun</strong> tur tekshiruvini o'chiradi. <code>as any</code> deb yozish — "bu qiymat ustida endi hech qanday tekshiruv qilma" degani. Bu — <code>as SomeInterface</code>dan ham <strong>battar</strong>, chunki hech qanday interfeys bilan ham solishtirilmaydi.</p>

<h4>3. Agar 5-darsdagi kabi backend <code>Issue</code> shaklini o'zgartirsa, TO'G'RI yozilgan mock nima qiladi?</h4>
<p>Agar <code>shared/types.ts</code>dagi <code>Issue</code> interfeysi yangilansa (masalan <code>assigneeId</code> olib tashlansa), <code>const mockIssue: Issue = {...}</code> qatori endi <strong>compile xatosi</strong> beradi — chunki mock obyekt endi yangi interfeysga mos kelmaydi. Bu — <strong>foydali</strong> xato: u testni yozgan kishiga darhol "buni yangilash kerak" deb signal beradi.</p>

<h4>4. <code>as any</code> bilan yozilgan mock nega bunday signal bermaydi?</h4>
<p><code>as any</code> mock obyektni <code>Issue</code> interfeysidan <strong>butunlay ajratib qo'yadi</strong> — TypeScript endi ularni <strong>hech qachon</strong> solishtirmaydi. <code>Issue</code> qanchalik o'zgarmasin, <code>as any</code> bilan yozilgan mock <strong>hech qachon</strong> compile xatosi bermaydi — u "muzlab qolgan", eskirgan holicha qoladi.</p>

<h4>5. Test "yashil" bo'lishi nimani anglatadi, nimani anglatmaydi?</h4>
<p>Test "yashil" (muvaffaqiyatli) bo'lishi faqat <strong>test yozilgan tarzda</strong> hech narsa buzilmaganini bildiradi — bu <strong>production kodi to'g'ri ishlayapti</strong> degani emas, agar test <strong>o'zi</strong> haqiqiy ma'lumot shaklidan uzilib qolgan bo'lsa (masalan <code>as any</code> orqali). Yaxshi test — nafaqat "yashil" bo'lishi kerak, balki <strong>haqiqiy</strong> production shartlariga ham <strong>sezgir</strong> bo'lishi kerak.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Mock ma'lumotlarni haqiqiy interfeys turi bilan (<code>as any</code> EMAS) yozish — test'ni haqiqiy tur bilan sinxron ushlab turadi</li>
<li>✅ <code>as any</code> — TypeScript'ning butun tur tekshiruvi tizimini o'chiradigan eng xavfli konstruksiya</li>
<li>✅ To'g'ri yozilgan mock — interfeys o'zgarganda compile xatosi orqali <strong>foydali</strong> signal beradi</li>
<li>✅ <code>as any</code> bilan yozilgan mock — interfeys o'zgarsa ham hech qachon signal bermaydi, test "muzlab qoladi"</li>
<li>✅ "Yashil" test — faqat test o'zi to'g'ri yozilgan bo'lsagina, haqiqiy ishonch manbai hisoblanadi</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 6-BOSQICH: Testing (Jest + React Testing Library)
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) IssueCard.test.tsx - mock Issue turi bilan (TO'G'RI)
// ─────────────────────────────────────────────────────────────────────

import { render, screen } from '@testing-library/react';
import IssueCard from './IssueCard';
import { Issue } from '../../../shared/types';

const mockIssue: Issue = {
  id: 1,
  title: 'Login sahifasi buzilgan',
  description: 'Parolni tiklash tugmasi ishlamayapti',
  status: 'open',
  assigneeId: 7,
  reporterId: 2,
  createdAt: '2026-01-01T10:00:00Z',
};

test("IssueCard sarlavha va holatni ko'rsatadi", () => {
  render(<IssueCard {...mockIssue} />);
  expect(screen.getByText('Login sahifasi buzilgan')).toBeInTheDocument();
  expect(screen.getByText('open')).toBeInTheDocument();
});

// ─────────────────────────────────────────────────────────────────────
// 2) issuesSlice.test.ts - async thunk, fetch mock qilingan
// ─────────────────────────────────────────────────────────────────────

import { configureStore } from '@reduxjs/toolkit';
import issuesReducer, { fetchIssues } from './issuesSlice';

test('fetchIssues muvaffaqiyatli holatni yangilaydi', async () => {
  const mockData: Issue[] = [
    { id: 1, title: 'Test', description: '...', status: 'open',
      assigneeId: null, reporterId: 1, createdAt: '2026-01-01T00:00:00Z' },
  ];
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })
  ) as jest.Mock;

  const store = configureStore({ reducer: { issues: issuesReducer } });
  await store.dispatch(fetchIssues());

  expect(store.getState().issues.list).toEqual(mockData);
});

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - mock "as any" bilan (izohda)
// ─────────────────────────────────────────────────────────────────────

// const mockIssue = {
//   id: 1, title: 'Login sahifasi buzilgan', status: 'open', assigneeId: 7,
// } as any;   // BUTUN tur tekshiruvini o'chiradi!
//
// Issue interfeysi 5-bosqichdagi kabi o'zgarsa ham, bu test HAMON
// YASHIL turaveradi - yolg'on ishonch beradi.
"""

L6_EX = [
    {
        "title": "as any nima qiladi?",
        "description": "TypeScript'da const mockIssue = {...} as any; yozuvida as any aslida nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Obyektni Issue interfeysi bilan qattiqroq tekshiradi",
            "O'sha qiymat uchun BUTUN tur tekshiruvini o'chirib qo'yadi",
            "Faqat obyektning number maydonlarini tekshiradi",
            "Test'ni tezroq ishlashga majburlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "any - TypeScript Asoslari kursida o'rgangan eng xavfli tur.",
        "explanation": "as any o'sha qiymat uchun TypeScript'ning butun tur tekshiruvi tizimini o'chirib qo'yadi - bu as SomeInterface'dan ham xavfliroq, chunki hech qanday interfeys bilan solishtirilmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Mock'ni Issue turi bilan yozish nima uchun foydali?",
        "description": "const mockIssue: Issue = {...} deb yozish, as any'dan farqli, nima uchun foydali?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu testni tezroq ishga tushiradi",
            "Chunki agar Issue interfeysi keyinchalik o'zgarsa, bu qator compile xatosi berib, testni yangilash kerakligini darhol bildiradi",
            "Chunki bu Jest uchun majburiy sintaksis",
            "Chunki bu testni har doim yashil qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Interfeys o'zgarsa, mock obyekt endi mos kelmay qolishi mumkinmi?",
        "explanation": "Mock'ni Issue turi bilan yozish uni haqiqiy interfeys bilan sinxron ushlab turadi - agar Issue keyinchalik o'zgarsa, mos kelmagan mock compile xatosi beradi, bu esa foydali, darhol signal hisoblanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "'Yolg'on yashil' test yuzaga kelish jarayonini tartiblang",
        "description": "as any bilan yozilgan mock'ga ega test, Issue interfeysi o'zgarganda ham nega yashil qolib ketishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Test uchun mockIssue obyekti as any bilan yoziladi",
            "5-bosqichdagi kabi backend Issue shaklini o'zgartiradi (assigneeId -> assignee)",
            "as any tufayli TypeScript mockIssue'ni Issue interfeysi bilan hech qachon solishtirmaydi",
            "Test hamon 'yashil' o'tadi, garchi haqiqiy IssueCard production'da buzilgan bo'lsa ham",
        ],
        "correct_order": [
            "Test uchun mockIssue obyekti as any bilan yoziladi",
            "5-bosqichdagi kabi backend Issue shaklini o'zgartiradi (assigneeId -> assignee)",
            "as any tufayli TypeScript mockIssue'ni Issue interfeysi bilan hech qachon solishtirmaydi",
            "Test hamon 'yashil' o'tadi, garchi haqiqiy IssueCard production'da buzilgan bo'lsa ham",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Testda mock ma'lumot uchun ishlatilishi tavsiya etilmaydigan konstruksiya",
        "description": "Mock obyektlarni yozishda, ularni haqiqiy interfeysdan ajratib qo'yadigan, ishlatilishi tavsiya etilmaydigan TypeScript konstruksiyasini yozing (masalan: as xxx).",
        "exercise_type": "text_input",
        "expected_answer": "as any",
        "hint": "Bu butun tur tekshiruvini o'chiradigan 'favqulodda chiqish eshigi'.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega 'test yashil o'tishi' har doim 'kod to'g'ri ishlayapti' degani emas?",
        "description": (
            "Testlar 'yashil' (muvaffaqiyatli) natija bersa ham, bu "
            "nega har doim production kodi to'g'ri ishlayapti degani "
            "emasligini tushuntiring. Bunga qanday sharoitda amal "
            "qiladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Test 'yashil' o'tishi faqat test YOZILGAN tarzda hech narsa "
            "buzilmaganini bildiradi - bu ko'rsatkich test o'zi qanchalik "
            "TO'G'RI va HAQIQIY ma'lumotga sezgir yozilganiga to'liq "
            "bog'liq. Agar test mock ma'lumoti 'as any' kabi usul bilan "
            "haqiqiy interfeysdan ajratib qo'yilgan bo'lsa, unda interfeys "
            "(demak, haqiqiy production ma'lumot shakli) o'zgarganda ham, "
            "test bu o'zgarishni HECH QACHON sezmaydi va yashil bo'lib "
            "qolaveradi - garchi haqiqiy kod (masalan IssueCard komponenti) "
            "endi butunlay boshqacha, buzilgan ma'lumot bilan ishlayotgan "
            "bo'lsa ham. Shuning uchun 'yashil test' faqat testning o'zi "
            "ham to'g'ri, real ma'lumot shakliga bog'langan holda "
            "yozilganda haqiqiy ishonch manbai hisoblanadi."
        ),
        "hint": "Test nimani tekshiradi - haqiqiy interfeysning o'zinimi, yoki testda yozilgan 'muzlab qolgan' nusxasinimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "IssueForge — Testing (Jest + React Testing Library)",
    "task_description": (
        "IssueCard komponenti va issuesSlice uchun testlar yozing. Barcha "
        "mock ma'lumotlar (issue obyektlari) shared/types.ts'dagi Issue "
        "turi bilan e'lon qilinishi shart — 'as any' yoki boshqa "
        "tekshiruvsiz konstruksiyalar ISHLATILMASIN."
    ),
    "task_requirements": (
        "• IssueCard.test.tsx — kamida 2 ta test, mock Issue turi bilan yozilgan\n"
        "• issuesSlice.test.ts — fetchIssues uchun kamida 1 ta test, fetch mock qilingan\n"
        "• Hech qanday mock ma'lumotda 'as any' ishlatilmagan\n"
        "• npm test barcha testlarni xatosiz o'tkazadi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Jest, React Testing Library, TypeScript, ts-jest",
    "task_deadline_days": 4,
}


L7_TEXT = """\
<h2>7-bosqich (CAPSTONE yakuni): deploy va "tsc muvaffaqiyatli, production buzilgan" xatosi</h2>

<pre class="mermaid">
flowchart TB
    DEV["Dev: ts-node + tsconfig-paths - @shared/types ISHLAYDI"] --> BUILD["npm run build: tsc"]
    BUILD --> CHECK{"tsc paths xaritasini FAQAT tur tekshirish uchun ishlatadi"}
    CHECK --> DIST["dist/server.js: require('@shared/types') - O'ZGARTIRILMAGAN!"]
    DIST --> PROD["node dist/server.js"]
    PROD --> CRASH["❌ Cannot find module '@shared/types' - garchi tsc 0 xato bilan tugagan bo'lsa ham!"]
</pre>

<p>Node.js/Express kursida CORS'ni va React'ni backend bilan bog'lashni allaqachon o'rgangansiz. Bu — IssueForge'ning so'nggi, yakuniy bosqichi, va bu yerda capstone davomida ko'rgan g'oyaning eng <strong>aniq</strong> ko'rinishi paydo bo'ladi: bu safar hatto <code>tsc</code>ning o'zi ham "hammasi joyida" deb hisoblaydi — compile 0 xato bilan tugaydi — lekin production baribir <strong>ishlamay qoladi</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — path alias: nisbiy yo'llar o'rniga qisqa, o'qilishi oson import</h4>
<pre><code>// backend/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["../shared/*"]
    }
  }
}</code></pre>
<pre><code>// ODDIY (nisbiy) import - fayl chuqurlashgan sari o'qish qiyinlashadi:
// import { Issue } from '../../../shared/types';

// PATH ALIAS bilan - qisqa va aniq:
import { Issue } from '@shared/types';</code></pre>

<h4>BLOKA 2 — development'da path alias'ni ishga tushirish</h4>
<pre><code># package.json
{
  "scripts": {
    "dev": "ts-node -r tsconfig-paths/register src/server.ts"
  }
}

# npm install -D tsconfig-paths
# ts-node -r tsconfig-paths/register - RUNTIME'da @shared/* alias'ini
# haqiqiy fayl yo'liga aylantiradi. Dev'da hammasi MUKAMMAL ishlaydi.</code></pre>

<h4>BLOKA 3 — production build: alias'ni ham build vaqtida hal qilish</h4>
<pre><code># npm install -D tsc-alias
# package.json
{
  "scripts": {
    "build": "tsc && tsc-alias"
  }
}

# tsc-alias - tsc chiqargan dist/*.js fayllardagi '@shared/*'
# yozuvlarini HAQIQIY nisbiy yo'llarga QAYTA YOZADI. Shundan keyingina
# 'node dist/server.js' production'da xatosiz ishlaydi.</code></pre>

<h3>🐛 Ataylab xato — faqat "tsc" bilan build qilib, alias'ni unutish</h3>
<pre><code># package.json - tsc-alias QO'SHILMAGAN:
{
  "scripts": {
    "build": "tsc"
  }
}

# Lokalda (dev'da) hammasi ishlaydi, chunki ts-node -r tsconfig-paths/register
# RUNTIME'da alias'ni hal qiladi. Shuning uchun bu muammo "sinovda" umuman
# sezilmaydi!

$ npm run build
# ✅ tsc: 0 xato! "Muvaffaqiyatli compile qilindi."
#
# LEKIN dist/server.js faylini ochib qarasangiz:
#   const types_1 = require("@shared/types");   // ❗ O'ZGARTIRILMAGAN!
#
# tsc "paths" xaritasini FAQAT compile vaqtida TUR tekshirish uchun
# ishlatadi - u chiqargan JavaScript'dagi import/require yo'llarini
# HECH QACHON qayta yozmaydi (bu - hujjatlashtirilgan, ataylab qilingan
# tsc xatti-harakati).

$ node dist/server.js
# ❌ Error: Cannot find module '@shared/types'
#    Require stack: - /app/dist/server.js
# Production darhol ishga tushmay qoladi - garchi tsc 0 xato bergan
# bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> <code>tsc</code> <code>tsconfig.json</code>dagi <code>paths</code> xaritasini <strong>faqat</strong> compile vaqtida turlarni to'g'ri tekshirish uchun ishlatadi — <code>@shared/types</code> qayerga ishora qilishini <strong>bilib</strong>, shu asosda tur xatolarini topadi. Lekin u chiqargan <code>.js</code> fayllarda <code>@shared/types</code> yozuvi <strong>o'zgarishsiz</strong> qoladi — chunki bu alias faqat TypeScript'ning o'ziga, compile vaqtida tanish, Node.js'ning <code>require()</code> mexanizmiga esa <strong>butunlay notanish</strong>. Node ishga tushganda, <code>@shared/types</code> degan haqiqiy npm paketi yoki fayl yo'q — shuning uchun <code>Cannot find module</code> xatosi bilan darhol yiqiladi. Bu — capstone davomida ko'rgan barcha "compile vaqtida OK, runtime'da muammo" xatolarining eng <strong>yalang'och</strong> shakli: bu safar hatto <code>tsc</code>ning <strong>o'zi</strong> ham noto'g'ri signal beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega path alias (<code>@shared/*</code>) dev'da (<code>ts-node</code> bilan) muammosiz ishlaydi?</h4>
<p><code>ts-node -r tsconfig-paths/register</code> — bu <strong>runtime</strong>da ishlaydigan qo'shimcha vosita. U dastur ishga tushgan paytda, har bir <code>@shared/*</code> importini "ushlab", uni haqiqiy fayl yo'liga <strong>o'zi</strong> aylantiradi. Shuning uchun dev muhitida bu jarayon <strong>butunlay ko'rinmas</strong> holda, muammosiz ishlab turadi.</p>

<h4>2. <code>tsc</code> <code>paths</code> xaritasini nima uchun ishlatadi, va nima uchun ishlatmaydi?</h4>
<p><code>tsc</code> <code>paths</code>ni <strong>faqat</strong> compile vaqtida, <code>@shared/types</code>ning haqiqatda qaysi fayl/interfeysga mos kelishini <strong>bilish</strong> uchun ishlatadi — bu unga to'g'ri tur tekshiruvini o'tkazish imkonini beradi. Lekin <code>tsc</code>ning vazifasi TypeScript'ni JavaScript'ga <strong>aylantirish</strong>, import yo'llarini <strong>qayta yozish</strong> emas — shuning uchun u chiqargan <code>.js</code> faylda original <code>@shared/types</code> satri <strong>o'zgarishsiz</strong> qoladi.</p>

<h4>3. Nega bu xato aynan production'da, <code>node dist/server.js</code> ishga tushirilganda paydo bo'ladi?</h4>
<p>Production'da, oddatda, <code>ts-node</code> ham, <code>tsconfig-paths/register</code> ham ishlatilmaydi — faqat oldindan compile qilingan, "sof" JavaScript (<code>node dist/server.js</code>) ishga tushiriladi. Node.js'ning standart <code>require()</code> mexanizmi <code>tsconfig.json</code> haqida <strong>umuman bilmaydi</strong> va <code>@shared/types</code>ni oddiy npm paket nomi deb qabul qiladi — bunday paket <code>node_modules</code>da yo'qligi uchun xato beradi.</p>

<h4>4. Bu muammoning to'g'ri yechimi nima?</h4>
<p><code>tsc-alias</code> kabi vositani <code>build</code> jarayoniga qo'shish — bu vosita <code>tsc</code> chiqargan <code>.js</code> fayllardagi <code>@shared/*</code> kabi alias yozuvlarini haqiqiy <strong>nisbiy</strong> yo'llarga <strong>qayta yozadi</strong>, shundan keyin <code>node dist/server.js</code> production'da xatosiz ishlaydi. Muqobil yechim — umuman alias ishlatmasdan, doim nisbiy yo'llardan foydalanish (kamroq qulay, lekin bu muammoni butunlay chetlab o'tadi).</p>

<h4>5. Bu xato butun capstone bo'ylab ko'rgan g'oyaning qanday <strong>yakuniy</strong> ko'rinishi?</h4>
<p>1-6-darslarda TypeScript'ning o'zi "aldamadi" — muammo har doim <strong>dasturchi</strong> compile vaqtidagi ma'lumotga ortiqcha ishonganda paydo bo'lardi. Bu yerda esa hatto <code>tsc</code>ning <strong>muvaffaqiyatli compile</strong> xabari ham yetarli emasligini ko'rasiz — bu capstone davomida o'rgangan eng muhim saboqni yakunlaydi: <strong>hech qanday compile vaqtidagi "OK" signali, hatto tsc'ning o'zinikidan ham, production'da hamma narsa to'g'ri ishlashini kafolatlamaydi.</strong> Faqat haqiqiy, jonli sinov (deploy qilib, ishga tushirib ko'rish) buni tasdiqlay oladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Path alias'lar (<code>@shared/*</code>) dev'da <code>tsconfig-paths/register</code> orqali runtime'da hal qilinadi</li>
<li>✅ <code>tsc</code> <code>paths</code>ni faqat tur tekshirish uchun ishlatadi — chiqargan JS'dagi import yo'llarini qayta yozmaydi</li>
<li>✅ Production'da <code>tsc-alias</code> kabi vosita bo'lmasa, <code>node dist/...</code> "Cannot find module" bilan yiqiladi</li>
<li>✅ <code>tsc</code>ning "0 xato" xabari ham runtime muvaffaqiyatini kafolatlamaydi</li>
<li>✅ Faqat haqiqiy deploy va jonli sinov — compile vaqtidagi har qanday "OK" signalidan ko'ra ishonchliroq tekshiruv</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz IssueForge'ni 1-bosqichdagi bo'sh repo'dan boshlab, umumiy TypeScript sxemasi, Express + TypeScript backend, PostgreSQL bilan tiplashtirilgan so'rovlar, JWT autentifikatsiyasi, React + Redux Toolkit frontend, testlar va nihoyat <strong>to'g'ri, ikki qismli production deploy</strong>gacha qurdingiz. Bu capstone davomida siz TypeScript Asoslari, Node.js/Express Asoslari va React: Redux Toolkit, TypeScript va Testlash kurslarida alohida o'rgangan bilimlarni <strong>bitta, real loyiha</strong>da birlashtirdingiz — va eng muhimi, TypeScript'ning eng katta haqiqatini yetti xil ko'rinishda ko'rdingiz: <strong>u sizga compile vaqtida yordam beradi, lekin runtime'da hech narsani sizning o'rningizga tekshirmaydi.</strong></p>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 7-BOSQICH (CAPSTONE YAKUNI): Deploy va path alias xatosi
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) backend/tsconfig.json - path alias sozlash
// ─────────────────────────────────────────────────────────────────────

// {
//   "compilerOptions": {
//     "baseUrl": ".",
//     "paths": { "@shared/*": ["../shared/*"] }
//   }
// }

import { Issue } from '@shared/types';

// ─────────────────────────────────────────────────────────────────────
// 2) package.json - dev va TO'G'RI build (izohda - JSON, kod emas)
// ─────────────────────────────────────────────────────────────────────

// {
//   "scripts": {
//     "dev": "ts-node -r tsconfig-paths/register src/server.ts",
//     "build": "tsc && tsc-alias"
//   }
// }
//
// npm install -D tsconfig-paths tsc-alias

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - tsc-alias'siz build (izohda)
// ─────────────────────────────────────────────────────────────────────

// {
//   "scripts": { "build": "tsc" }        // tsc-alias YO'Q!
// }
//
// $ npm run build   -> tsc: 0 xato
// $ cat dist/server.js
//   const types_1 = require("@shared/types");   // o'zgartirilmagan!
// $ node dist/server.js
//   -> Error: Cannot find module '@shared/types'
"""

L7_EX = [
    {
        "title": "tsc paths xaritasini nima uchun ishlatadi?",
        "description": "tsconfig.json'dagi \"paths\" xaritasi tsc tomonidan compile vaqtida asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chiqarilgan .js fayllardagi import yo'llarini avtomatik qayta yozish uchun",
            "Faqat compile vaqtida tur tekshiruvini to'g'ri o'tkazish uchun - alias qayerga ishora qilishini bilish maqsadida",
            "Node.js'ning require() mexanizmini o'zgartirish uchun",
            "Faqat production build tezligini oshirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "tsc'ning vazifasi TypeScript'ni JavaScript'ga aylantirish, import yo'llarini qayta yozish emas.",
        "explanation": "tsc paths xaritasini faqat compile vaqtida to'g'ri tur tekshiruvini o'tkazish uchun ishlatadi - u chiqargan JavaScript fayllardagi import/require yo'llarini hech qachon qayta yozmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega path alias dev'da ishlaydi, lekin tsc-alias'siz production'da ishlamaydi?",
        "description": "@shared/types kabi alias ts-node bilan dev'da muammosiz ishlaydi, lekin tsc-alias qo'shilmagan build'dan keyin node dist/server.js nega Cannot find module xatosi beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki production serverlar odatda internetga ulanmagan",
            "Dev'da ts-node -r tsconfig-paths/register alias'ni runtime'da hal qiladi, lekin production'da sof node ishga tushiriladi va u tsconfig haqida bilmaydi",
            "Chunki @shared/types haqiqiy npm paketi emas",
            "Chunki tsc build vaqtida internetga ulanish talab qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Production'da ts-node yoki tsconfig-paths/register ishlatilmaydi - faqat sof, compile qilingan JS.",
        "explanation": "Dev muhitida ts-node -r tsconfig-paths/register alias'ni runtime'da haqiqiy yo'lga aylantiradi. Production'da esa sof node dist/server.js ishga tushiriladi - Node'ning standart require() mexanizmi tsconfig.json haqida umuman bilmaydi, shuning uchun @shared/types'ni topa olmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "IssueForge'ni to'g'ri deploy qilish jarayonini tartiblang",
        "description": "Path alias xatosidan xoli, to'g'ri production build va deploy jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "package.json'ga tsc-alias qo'shiladi, build skripti 'tsc && tsc-alias' qilib yangilanadi",
            "npm run build ishga tushiriladi - dist/ papkasidagi alias'lar haqiqiy nisbiy yo'llarga qayta yoziladi",
            "Backend va frontend alohida Web Service sifatida deploy qilinadi, CORS va environment variables sozlanadi",
            "node dist/server.js production'da xatosiz ishga tushishi tasdiqlanadi",
        ],
        "correct_order": [
            "package.json'ga tsc-alias qo'shiladi, build skripti 'tsc && tsc-alias' qilib yangilanadi",
            "npm run build ishga tushiriladi - dist/ papkasidagi alias'lar haqiqiy nisbiy yo'llarga qayta yoziladi",
            "Backend va frontend alohida Web Service sifatida deploy qilinadi, CORS va environment variables sozlanadi",
            "node dist/server.js production'da xatosiz ishga tushishi tasdiqlanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "tsc chiqargan JS'dagi alias'larni haqiqiy yo'llarga qayta yozadigan vosita",
        "description": "tsc build qilgandan keyin, dist/ papkasidagi @shared/* kabi alias yozuvlarini haqiqiy nisbiy yo'llarga qayta yozib beradigan npm paketining nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "tsc-alias",
        "hint": "Bu paket build skriptida 'tsc && ...' dan keyin qo'shiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bu xato butun capstone'ning asosiy g'oyasini qanday yakunlaydi?",
        "description": (
            "tsc \"0 xato\" bilan compile bo'lgan holda ham production'da "
            "\"Cannot find module\" bilan yiqilishi, IssueForge davomida "
            "ko'rgan barcha xatolarning umumiy g'oyasini qanday "
            "yakunlaydi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "1-6-darslarda TypeScript'ning o'zi to'g'ri ishlagan - muammo "
            "har doim dasturchi compile vaqtidagi interfeys yoki turga "
            "ortiqcha ishonib, runtime tekshiruvini o'tkazib yuborganda "
            "paydo bo'lgan. Bu darsda esa hatto tsc'ning \"muvaffaqiyatli "
            "compile qilindi, 0 xato\" degan xabarining o'zi ham "
            "production'da hamma narsa ishlashini KAFOLATLAMASLIGI "
            "ko'rsatiladi - chunki tsc paths xaritasini faqat tur "
            "tekshirish uchun ishlatadi, chiqargan JavaScript'dagi haqiqiy "
            "import yo'llarini qayta yozmaydi. Bu capstone davomida "
            "o'rgangan asosiy saboqni eng yalang'och shaklda yakunlaydi: "
            "hech qanday compile vaqtidagi \"OK\" signali - hatto "
            "TypeScript compilerining o'zinikidan ham - production'da "
            "hamma narsa to'g'ri ishlashini kafolatlamaydi; buni faqat "
            "haqiqiy, jonli sinov tasdiqlay oladi."
        ),
        "hint": "tsc \"0 xato\" deb aytishi bilan production'da dastur ishlashi orasida qanday bog'liqlik bor - bu bog'liqlik kafolatlanganmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L7_TASK = {
    "task_title": "IssueForge — CAPSTONE yakuni: to'liq deploy qilingan loyiha",
    "task_description": (
        "IssueForge'ni haqiqiy hostingga deploy qiling: backend (Express + "
        "TypeScript) va frontend (React) alohida Web Service sifatida. "
        "Path alias'lar production build'da tsc-alias (yoki nisbiy yo'llar) "
        "orqali to'g'ri hal qilinganini tasdiqlang. README.md'ni jonli "
        "havolalar va yakuniy sinov ro'yxati bilan yangilang."
    ),
    "task_requirements": (
        "• Backend (Express + TypeScript) haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
        "• Frontend (React) haqiqiy hostingda alohida deploy qilingan\n"
        "• Build jarayonida tsc-alias ishlatilgan (yoki path alias umuman ishlatilmagan) — node dist/server.js xatosiz ishga tushadi\n"
        "• CORS production frontend domeniga to'g'ri sozlangan\n"
        "• Ro'yxatdan o'tish, kirish, issue yaratish/ko'rish — barchasi jonli saytda ishlaydi\n"
        "• README.md: jonli havolalar, texnologiyalar, 7/7 bosqich yakunlangan checklist\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
        "(backend + frontend) tekshiradi, alohida live_demo_url maydoni endi shart emas"
    ),
    "task_technologies": "Render/Railway/Vercel, tsc-alias, CORS, environment variables",
    "task_deadline_days": 5,
}


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "typescript",
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
            lang = ldata.get("lang", "typescript")

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
                    [{"filename": "misol.ts" if lang != "tsx" else "misol.tsx",
                      "language": lang, "code": code}],
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
