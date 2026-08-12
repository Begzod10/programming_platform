"""Seed "TypeScript Asoslari" (10 lessons): fills a real gap — course 72
("React: Redux Toolkit, TypeScript va Testlash") assumes TypeScript
knowledge, but its prerequisite (course 43, "React Asoslari") is plain
JS/JSX, and no standalone TypeScript course exists anywhere in the catalog.

Usage:
    cd backend
    python scripts/seed_typescript_asoslari.py
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
    "title": "TypeScript Asoslari",
    "description": (
        "JavaScript'ga statik turlash qo'shuvchi TypeScript'ni o'rganing: "
        "asosiy turlar, interfeys, generics, union/intersection turlari, "
        "class'lar va utility types. React: Redux Toolkit, TypeScript va "
        "Testlash kursidan oldin o'qish uchun mo'ljallangan."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 4,
    "max_points": 100,
    "category_id": 7,  # JavaScript
    "prerequisite_course_id": 39,  # JavaScript: Keyingi Bosqich
    "is_active": True,
    "is_published": False,  # flip to True once all 10 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-TypeScriptga kirish va asosiy turlar",
     "scope": "Why TypeScript, tsc, first .ts file, string/number/boolean, type inference."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Massivlar, Tuple va any/unknown/never",
     "scope": "Array types, tuples, any vs unknown, never, void."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-Interfeys va Type Alias",
     "scope": "interface vs type, optional/readonly fields, extending interfaces."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Funksiyalarni tiplashtirish",
     "scope": "Parameter/return types, optional/default params, function types."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Union, Intersection va Type Narrowing",
     "scope": "Union/intersection types, typeof/instanceof guards, discriminated unions."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Generics asoslari",
     "scope": "Generic functions, generic interfaces, constraints (extends)."},
    {"order": 6, "ref": "L7", "status": "done",
     "title": "7-Classlar va Access Modifiers",
     "scope": "public/private/protected, implements, abstract classes."},
    {"order": 7, "ref": "L8", "status": "done",
     "title": "8-Enum va Literal Types",
     "scope": "Numeric/string enums, literal types, const assertions."},
    {"order": 8, "ref": "L9", "status": "done",
     "title": "9-Utility Types",
     "scope": "Partial, Pick, Omit, Record, Readonly."},
    {"order": 9, "ref": "L10", "status": "done",
     "title": "10-CAPSTONE: To'liq tiplashtirilgan kichik loyiha",
     "scope": "Combining interfaces + generics + utility types on a real mini-project."},
]


L1_TEXT = """\
<h2>TypeScriptga kirish — birinchi tiplashtirilgan kod 5 daqiqada</h2>

<pre class="mermaid">
flowchart LR
    TS["TypeScript kod (.ts)"] -->|tsc kompilyatsiya| JS["Sof JavaScript (.js)"]
    JS --> BROWSER["Brauzer / Node.js"]
    ERR["Tur xatosi"] -->|kompilyatsiya vaqtida aniqlanadi| TS
</pre>

<p>Hozirgacha JavaScript'da o'zgaruvchiga istalgan turdagi qiymat berish mumkin edi — <code>let yosh = 25</code> keyin <code>yosh = "yigirma besh"</code> deb yozsangiz ham hech qanday xato chiqmaydi, muammo faqat dastur ishga tushganda (runtime) yuzaga chiqadi. <strong>TypeScript</strong> — Microsoft yaratgan, JavaScript'ga <strong>statik turlash</strong> (static typing) qo'shuvchi til: xatolarni kodni yozish paytida, hali ishga tushirmasdan turib aniqlaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — TypeScript o'rnatish va birinchi fayl</h4>
<pre><code>// Terminal:
npm install -g typescript
tsc --version</code></pre>

<pre><code>// birinchi.ts
let ism: string = "Olim";
let yosh: number = 22;
let faol: boolean = true;

console.log(`${ism} - ${yosh} yoshda, faolmi: ${faol}`);</code></pre>

<pre><code>// Terminal — .ts faylni .js ga aylantirish:
tsc birinchi.ts
// Natijada birinchi.js fayli yaratiladi, uni node bilan ishga tushirish mumkin:
node birinchi.js</code></pre>

<h4>BLOKA 2 — Tur xatosini kompilyatsiya vaqtida ushlash</h4>
<pre><code>let yosh: number = 25;
yosh = "yigirma besh"; // ❌ TypeScript XATO BERADI: bu yerga string berib bo'lmaydi!

// Xato xabari:
// Type 'string' is not assignable to type 'number'.</code></pre>

<p>Aynan shu — TypeScript'ning asosiy kuchi: bu xato <strong>hali kodni ishga tushirmasdan</strong>, IDE'da yoki <code>tsc</code> ishga tushirilganda darhol ko'rinadi. Oddiy JavaScript'da esa bu xato faqat dastur ishlab, o'sha qatorga yetganda "portlaydi".</p>

<h4>BLOKA 3 — Type Inference (turni avtomatik aniqlash)</h4>
<pre><code>// Turni har doim yozish shart emas — TypeScript o'zi "xulosa chiqaradi"
let shahar = "Toshkent"; // TypeScript buni avtomatik 'string' deb biladi
let masofa = 150.5;      // avtomatik 'number'

shahar = 42; // ❌ Xato: 'number' turini 'string'ga berib bo'lmaydi
             // TypeScript buni eslab qoladi, garchi biz ':string' yozmagan bo'lsak ham!</code></pre>

<h3>🐛 Ataylab xato — .js kengaytmasi bilan TypeScript sintaksisini ishlatish</h3>
<pre><code>// fayl.js (kengaytma .js, .ts EMAS!)
let yosh: number = 25; // ❌ Bu yerda ':number' — TypeScript sintaksisi!</code></pre>

<p><strong>Natija:</strong> agar fayl kengaytmasi <code>.js</code> bo'lib qolsa (<code>.ts</code>ga o'zgartirilmasa), <code>tsc</code> kompilyatori bu faylni umuman tekshirmaydi — chunki u faqat <code>.ts</code> fayllarni qidiradi. Node.js yoki brauzer esa <code>: number</code> kabi TypeScript-maxsus sintaksisni tushunmaydi va <strong>syntax error</strong> beradi. Bu — eng ko'p uchraydigan boshlang'ich xato: TypeScript sintaksisi faqat <code>.ts</code> (yoki React uchun <code>.tsx</code>) fayllarida ishlaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. TypeScript nima va u JavaScript bilan qanday bog'liq?</h4>
<p>TypeScript — JavaScript'ning <strong>ustki qatlami</strong> (superset): har qanday to'g'ri JavaScript kodi ayni paytda to'g'ri TypeScript kodi hisoblanadi. TypeScript shunchaki unga <strong>tur annotatsiyalari</strong> (type annotations) qo'shish imkonini beradi. Brauzer yoki Node.js TypeScript'ni to'g'ridan-to'g'ri tushunmaydi — shuning uchun <code>tsc</code> kompilyatori uni sof JavaScript'ga aylantiradi.</p>

<h4>2. Asosiy primitiv turlar</h4>
<pre><code>let ism: string = "Olim";       // matn
let yosh: number = 22;          // butun va kasr sonlar uchun BITTA tur
let faol: boolean = true;       // true yoki false</code></pre>
<p>JavaScript'dan farqli o'laroq, TypeScript'da <code>int</code>, <code>float</code> kabi alohida sonli turlar yo'q — barchasi uchun bitta <code>number</code> turi ishlatiladi.</p>

<h4>3. Nega tur xatosini kompilyatsiya vaqtida bilish muhim?</h4>
<p>Katta jamoada ishlaganda yoki katta loyihada, kimdir funksiyaga noto'g'ri turdagi qiymat yuborishi mumkin. Oddiy JavaScript'da bu xato faqat production'da, foydalanuvchi o'sha funksiyani chaqirganda ma'lum bo'ladi. TypeScript esa buni <strong>siz kodni yozayotganingiz paytidayoq</strong> ko'rsatadi.</p>

<h4>4. Type Inference — har doim tur yozish shart emas</h4>
<p>TypeScript qiymatga qarab turni avtomatik aniqlay oladi (<em>type inference</em>). Shuning uchun oddiy hollarda <code>: string</code>, <code>: number</code> yozish shart emas — lekin funksiya parametrlarida buni aniq yozish tavsiya etiladi (keyingi darsda ko'ramiz).</p>

<h4>5. .ts va .js fayllarining farqi</h4>
<p><code>tsc</code> kompilyatori faqat <code>.ts</code> kengaytmali fayllarni TypeScript sifatida tekshiradi. <code>.js</code> faylida TypeScript sintaksisi (masalan, <code>: number</code>) yozilsa, na <code>tsc</code>, na brauzer buni to'g'ri tushunadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ TypeScript — JavaScript'ga statik turlash qo'shuvchi til, <code>tsc</code> orqali sof JS'ga aylantiriladi</li>
<li>✅ <code>string</code>, <code>number</code>, <code>boolean</code> — eng asosiy uchta primitiv tur</li>
<li>✅ Tur xatosi kodni ishga tushirmasdan, kompilyatsiya paytida aniqlanadi</li>
<li>✅ Type Inference — TypeScript ko'p hollarda turni o'zi "xulosa chiqarib" aniqlaydi</li>
<li>✅ TypeScript sintaksisi faqat <code>.ts</code>/<code>.tsx</code> fayllarida ishlaydi, <code>.js</code>da emas</li>
</ul>
"""

L1_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 1: TypeScriptga kirish va asosiy turlar
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Asosiy primitiv turlar
// ─────────────────────────────────────────────────────────────────────

let ism: string = "Olim";
let yosh: number = 22;
let faol: boolean = true;

console.log(`${ism} - ${yosh} yoshda, faolmi: ${faol}`);

// ─────────────────────────────────────────────────────────────────────
// 2) Type Inference - turni yozmasak ham TypeScript o'zi aniqlaydi
// ─────────────────────────────────────────────────────────────────────

let shahar = "Toshkent"; // avtomatik: string
let masofa = 150.5;      // avtomatik: number

// ─────────────────────────────────────────────────────────────────────
// 3) Tur xatosi - kompilyatsiya vaqtida aniqlanadi
// ─────────────────────────────────────────────────────────────────────

// yosh = "yigirma besh"; // ❌ Xato: Type 'string' is not assignable to type 'number'
// shahar = 42;            // ❌ Xato: Type 'number' is not assignable to type 'string'

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - .js faylida TypeScript sintaksisi (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
// Agar bu kod fayl.js (fayl.ts EMAS) ichida bo'lsa:
let narx: number = 100; // ❌ Node.js/brauzer ": number"ni tushunmaydi - syntax error!
*/

// Terminal:
//   npm install -g typescript
//   tsc birinchi.ts   // birinchi.js yaratiladi
//   node birinchi.js
"""

L1_EX = [
    {
        "title": "TypeScript nima?",
        "description": "TypeScript aslida nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Butunlay yangi, JavaScript'ga aloqasi yo'q til",
            "JavaScript'ga statik turlash qo'shuvchi ustki qatlam (superset)",
            "Faqat backend uchun mo'ljallangan til",
            "CSS preprocessori"
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Har qanday to'g'ri JavaScript kodi ayni paytda to'g'ri TypeScript kodi hisoblanadi.",
        "explanation": "TypeScript — JavaScript'ning ustki qatlami (superset) bo'lib, unga statik turlash (static typing) qo'shadi. tsc kompilyatori uni sof JavaScript'ga aylantiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Tur xatosi qachon aniqlanadi?",
        "description": "TypeScript'da noto'g'ri turdagi qiymat berilsa, bu xato odatda qachon aniqlanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat dastur ishga tushib, o'sha qatorga yetganda (runtime)",
            "Kompilyatsiya vaqtida, kodni ishga tushirmasdan turib",
            "Hech qachon aniqlanmaydi",
            "Faqat production serverida"
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — TypeScript'ning asosiy afzalligi, oddiy JavaScript'dan farqi.",
        "explanation": "TypeScript'ning asosiy kuchi shundaki, tur xatolari kompilyatsiya vaqtida (yoki IDE'da yozayotganingizda) aniqlanadi — kodni ishga tushirishga hojat qolmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Loyihani ishga tushirish ketma-ketligi",
        "description": "Yangi TypeScript faylini yozib, uni ishga tushirish qadamlarini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "npm install -g typescript",
            ".ts kengaytmali fayl yaratiladi",
            "tsc fayl.ts buyrug'i ishga tushiriladi",
            "Yaratilgan fayl.js faylini node bilan ishga tushirish",
        ],
        "correct_order": [
            "npm install -g typescript",
            ".ts kengaytmali fayl yaratiladi",
            "tsc fayl.ts buyrug'i ishga tushiriladi",
            "Yaratilgan fayl.js faylini node bilan ishga tushirish",
        ],
        "hint": "Avval kutubxona o'rnatiladi, keyin fayl yoziladi, keyin kompilyatsiya qilinadi, so'ng ishga tushiriladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TypeScript'da nechta asosiy sonli tur bor?",
        "description": "JavaScript/TypeScript'da int, float kabi alohida sonli turlar o'rniga nechta umumiy sonli tur ishlatiladi? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "1",
        "hint": "Butun va kasr sonlar uchun bitta umumiy tur bor.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": ".js faylida TypeScript sintaksisi ishlatilsa nima bo'ladi?",
        "description": (
            "Agar dasturchi 'let narx: number = 100;' kabi TypeScript "
            "sintaksisini fayl.js (fayl.ts emas) ichiga yozsa, nima "
            "sodir bo'ladi va nega? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "tsc kompilyatori faqat .ts kengaytmali fayllarni TypeScript "
            "sifatida qabul qilib tekshiradi, shuning uchun .js fayli uni "
            "umuman ko'rib chiqmaydi. Node.js yoki brauzer esa ': number' "
            "kabi TypeScript-maxsus sintaksisni tushunmaydi, chunki bu "
            "sintaksis standart JavaScript'ning bir qismi emas. Natijada "
            "fayl ishga tushirilganda syntax error yuz beradi, chunki "
            "JavaScript motori bu yozuvni tushuna olmaydi."
        ),
        "hint": "tsc qaysi kengaytmali fayllarni \"TypeScript\" deb hisoblaydi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L2_TEXT = """\
<h2>Massivlar, Tuple va maxsus turlar: any, unknown, never</h2>

<pre class="mermaid">
flowchart TB
    ARR["number[] — bir xil turdagi elementlar"] --> USE1["Ro'yxatlar uchun"]
    TUP["[string, number] — Tuple, aniq uzunlik va tartib"] --> USE2["Qat'iy tuzilgan ma'lumot uchun"]
    ANY["any — tur tekshiruvini o'chiradi"] --> DANGER["Xavfli, imkon qadar qochish kerak"]
    UNK["unknown — xavfsiz any"] --> SAFE["Ishlatishdan oldin tekshirish talab qilinadi"]
</pre>

<p>1-darsda oddiy turlarni ko'rdik. Endi — bir nechta qiymatni birga saqlash uchun <strong>massiv</strong> va <strong>tuple</strong> turlarini, hamda tur tizimidan "chetlab o'tish" uchun mo'ljallangan maxsus turlarni o'rganamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — massiv turlari</h4>
<pre><code>let sonlar: number[] = [1, 2, 3, 4, 5];
let ismlar: string[] = ["Olim", "Vali", "Guli"];

// Muqobil sintaksis (generics — 6-darsda chuqurroq ko'ramiz)
let baholar: Array&lt;number&gt; = [90, 85, 78];

sonlar.push(6);       // ✅ to'g'ri, number qo'shildi
// sonlar.push("olti"); // ❌ Xato: 'string' massivга 'number' kutilgan</code></pre>

<h4>BLOKA 2 — Tuple: aniq uzunlik va tartibdagi massiv</h4>
<pre><code>// Tuple — nechta element va ularning turlari QAT'IY belgilangan
let foydalanuvchi: [string, number] = ["Olim", 22];

console.log(foydalanuvchi[0]); // "Olim" — string
console.log(foydalanuvchi[1]); // 22 — number

// foydalanuvchi[0] = 25; // ❌ Xato: bu joyda faqat string bo'lishi kerak
// let xato: [string, number] = [22, "Olim"]; // ❌ Xato: tartib noto'g'ri</code></pre>

<h4>BLOKA 3 — any, unknown va never</h4>
<pre><code>// any — TUR TEKSHIRUVINI BUTUNLAY O'CHIRADI (imkon qadar ishlatmang!)
let narsa: any = "matn";
narsa = 42;         // ✅ hech qanday xato yo'q
narsa.notoGriMetod(); // ✅ TypeScript BU YERDA HAM xato bermaydi — xavfli!

// unknown — any'ga o'xshaydi, lekin XAVFSIZ: ishlatishdan oldin tekshirish shart
let nomalum: unknown = "matn";
// nomalum.toUpperCase(); // ❌ Xato: avval turini tekshirish kerak

if (typeof nomalum === "string") {
  console.log(nomalum.toUpperCase()); // ✅ endi xavfsiz, tur tekshirilgan
}

// never — hech qachon qiymat qaytarmaydigan funksiya uchun
function xatoTashlash(xabar: string): never {
  throw new Error(xabar); // funksiya hech qachon normal tugamaydi
}</code></pre>

<h3>🐛 Ataylab xato — any turidan "qulaylik uchun" foydalanish</h3>
<pre><code>function foydalanuvchiOlish(id: any) { // ❌ "qulay" bo'lsin deb any qo'yilgan
  return { ism: "Olim", yosh: 22 };
}

const user = foydalanuvchiOlish("noto'g'ri-id-123");
console.log(user.yash); // ❌ "yash" — xato yozilgan ("yosh" emas), lekin TypeScript HECH QANDAY xato bermaydi!
// Natija: undefined — dastur "jimgina" noto'g'ri ishlaydi</code></pre>

<p><strong>Natija:</strong> <code>any</code> turi qo'yilgan joyda TypeScript <strong>butunlay</strong> tur tekshiruvini o'chirib qo'yadi — hatto aniq yozuv xatosi (<code>user.yash</code> o'rniga <code>user.yosh</code> kerak edi) bo'lsa ham, hech qanday ogohlantirish chiqmaydi. Bu — TypeScript ishlatishning butun ma'nosini yo'qqa chiqaradi. <code>any</code> — "vaqtincha, majburiy holatlarda" ishlatiladigan oxirgi chora, "qulaylik uchun" emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Massiv turi qachon ishlatiladi?</h4>
<p><code>number[]</code> yoki <code>string[]</code> — barcha elementlari <strong>bir xil turdagi</strong>, uzunligi oldindan noma'lum ro'yxatlar uchun ishlatiladi (masalan, foydalanuvchilar ro'yxati, sonlar ketma-ketligi).</p>

<h4>2. Tuple qachon ishlatiladi?</h4>
<p>Tuple — elementlar soni va har birining turi <strong>qat'iy belgilangan</strong> holatlar uchun mo'ljallangan, masalan <code>[string, number]</code> — "ism va yosh" juftligi. Massivdan farqli o'laroq, tuple'da har bir pozitsiyaning o'z aniq turi bor.</p>

<h4>3. any va unknown orasidagi farq</h4>
<p><code>any</code> — tur tekshiruvini butunlay o'chiradi, xavfli. <code>unknown</code> — xavfsiz muqobil: qiymat "noma'lum tur"da ekanini bildiradi, lekin uni ishlatishdan oldin <code>typeof</code> yoki boshqa tur tekshiruvi orqali "tasdiqlash" talab qilinadi.</p>

<h4>4. never turi nima uchun kerak?</h4>
<p><code>never</code> — funksiya hech qachon normal qiymat qaytarmasligini bildiradi: yoki u doim xato tashlaydi (<code>throw</code>), yoki cheksiz sikl ichida qoladi. Bu funksiya chaqiruvchilariga "bu funksiyadan keyingi kod hech qachon ishga tushmaydi" deb signal beradi.</p>

<h4>5. void bilan never farqi</h4>
<p><code>void</code> — funksiya biror qiymat qaytarmaydi, lekin normal tugaydi (masalan, <code>console.log</code>ni chaqiruvchi funksiya). <code>never</code> esa funksiya <strong>umuman tugamaydi</strong> (xato tashlaydi yoki cheksiz ishlaydi) degani.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>number[]</code>/<code>string[]</code> — bir xil turdagi elementlar ro'yxati uchun</li>
<li>✅ Tuple (<code>[string, number]</code>) — aniq uzunlik va tartibdagi ma'lumot uchun</li>
<li>✅ <code>any</code> — tur tekshiruvini butunlay o'chiradi, imkon qadar qochish kerak</li>
<li>✅ <code>unknown</code> — xavfsiz muqobil, ishlatishdan oldin tur tekshiruvi talab qiladi</li>
<li>✅ <code>never</code> — hech qachon normal tugamaydigan funksiyalar uchun (masalan, xato tashlovchi)</li>
</ul>
"""

L2_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 2: Massivlar, Tuple va any/unknown/never
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Massiv turlari
// ─────────────────────────────────────────────────────────────────────

let sonlar: number[] = [1, 2, 3, 4, 5];
let ismlar: string[] = ["Olim", "Vali", "Guli"];
let baholar: Array<number> = [90, 85, 78];

sonlar.push(6);

// ─────────────────────────────────────────────────────────────────────
// 2) Tuple - aniq uzunlik va tartib
// ─────────────────────────────────────────────────────────────────────

let foydalanuvchi: [string, number] = ["Olim", 22];
console.log(foydalanuvchi[0], foydalanuvchi[1]);

// ─────────────────────────────────────────────────────────────────────
// 3) unknown - xavfsiz any, tur tekshiruvi bilan
// ─────────────────────────────────────────────────────────────────────

let nomalum: unknown = "matn";

if (typeof nomalum === "string") {
  console.log(nomalum.toUpperCase()); // xavfsiz - tur tasdiqlangan
}

// ─────────────────────────────────────────────────────────────────────
// 4) never - hech qachon normal tugamaydigan funksiya
// ─────────────────────────────────────────────────────────────────────

function xatoTashlash(xabar: string): never {
  throw new Error(xabar);
}

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - any orqali xatoni yashirish (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
function foydalanuvchiOlish(id: any) {
  return { ism: "Olim", yosh: 22 };
}
const user = foydalanuvchiOlish("noto'g'ri-id-123");
console.log(user.yash); // ❌ Yozuv xatosi, lekin any tufayli TypeScript sukut saqlaydi!
*/
"""

L2_EX = [
    {
        "title": "Massiv turi qanday yoziladi?",
        "description": "Faqat sonlardan iborat massiv uchun to'g'ri tur yozuvi qaysi?",
        "exercise_type": "multiple_choice",
        "options": ["number[]", "array(number)", "[number]", "num[]"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Tur nomidan keyin kvadrat qavs qo'yiladi.",
        "explanation": "Massiv turi tur nomidan keyin [] qo'shish orqali yoziladi: number[], string[] va h.k.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "any va unknown orasidagi asosiy farq",
        "description": "any va unknown turlari orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech qanday farqi yo'q",
            "unknown ishlatishdan oldin tur tekshiruvini talab qiladi, any esa yo'q",
            "any faqat sonlar uchun, unknown faqat matnlar uchun",
            "unknown eskirgan, endi ishlatilmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Biri xavfsiz, biri xavfli.",
        "explanation": "any tur tekshiruvini butunlay o'chiradi. unknown esa xavfsizroq — qiymatdan foydalanishdan oldin uning turini tekshirish (masalan typeof bilan) talab qilinadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Tuple xususiyatlarini aniqlash",
        "description": "let user: [string, number] = [\"Olim\", 22]; deb e'lon qilingan. Quyidagi amallarni to'g'ri/xato tartibida (avval to'g'ri, keyin xato) joylang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "user[0] ni string sifatida o'qish",
            "user[1] ni number sifatida o'qish",
            "user[0]ga son yozishga urinish (xato beradi)",
        ],
        "correct_order": [
            "user[0] ni string sifatida o'qish",
            "user[1] ni number sifatida o'qish",
            "user[0]ga son yozishga urinish (xato beradi)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "never turi qachon ishlatiladi?",
        "description": "Funksiya hech qachon normal tugamasligini (masalan, doim xato tashlashini) bildirish uchun qaysi tur ishlatiladi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "never",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "any turidan foydalanish nega xavfli?",
        "description": (
            "Agar funksiya parametriga 'any' turi berilsa, va keyinchalik "
            "shu qiymatning noto'g'ri yozilgan xususiyatiga (masalan "
            "user.yash, aslida user.yosh kerak bo'lsa) murojaat qilinsa, "
            "TypeScript bu haqda ogohlantiradimi? Nega bu xavfli "
            "hisoblanadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Yo'q, TypeScript hech qanday ogohlantirish bermaydi. any turi "
            "qo'yilgan qiymat uchun TypeScript butunlay tur tekshiruvini "
            "o'chirib qo'yadi — shu qiymatning istalgan xususiyatiga "
            "murojaat qilish, uni istalgan turga o'zgartirish yoki "
            "istalgan metodini chaqirish TypeScript nazaridan har doim "
            "\"to'g'ri\" hisoblanadi. Bu xavfli, chunki aynan yozuv xatolari "
            "(masalan yash o'rniga yosh) yoki noto'g'ri metod chaqiruvlari "
            "kompilyatsiya vaqtida aniqlanmay, faqat dastur ishga "
            "tushganda (yoki umuman aniqlanmasdan, jimgina noto'g'ri "
            "natija berib) yuzaga chiqadi — bu esa TypeScript ishlatishning "
            "asosiy maqsadini yo'qqa chiqaradi."
        ),
        "hint": "any butun tur tizimini shu qiymat uchun o'chirib qo'yadi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>Interfeys va Type Alias — obyekt shaklini belgilash</h2>

<pre class="mermaid">
flowchart LR
    INT["interface User { ... }"] -->|obyekt "shakli"ni belgilaydi| OBJ["Foydalanuvchi obyekti"]
    TYPE["type User = { ... }"] -->|shu vazifani ham bajaradi| OBJ
    OBJ -->|shu shaklga mos kelmasa| ERR["Kompilyatsiya xatosi"]
</pre>

<p>Hozirgacha oddiy qiymatlarni tiplashtirdik. Lekin real loyihalarda ko'pincha <strong>obyektlar</strong> bilan ishlaymiz — foydalanuvchi, mahsulot, buyurtma va h.k. <code>interface</code> va <code>type</code> — obyektning aniq "shakli" (qanday xususiyatlarga ega bo'lishi kerakligi) qanday bo'lishini belgilash uchun ishlatiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi interfeys</h4>
<pre><code>interface Foydalanuvchi {
  ism: string;
  yosh: number;
  faol: boolean;
}

const user: Foydalanuvchi = {
  ism: "Olim",
  yosh: 22,
  faol: true,
};

// const notoGriUser: Foydalanuvchi = { ism: "Vali" };
// ❌ Xato: 'yosh' va 'faol' xususiyatlari yetishmayapti!</code></pre>

<h4>BLOKA 2 — ixtiyoriy (optional) va faqat-o'qish (readonly) xususiyatlar</h4>
<pre><code>interface Mahsulot {
  readonly id: number;    // ❗ faqat bir marta belgilanadi, keyin o'zgartirib bo'lmaydi
  nomi: string;
  chegirma?: number;      // ❗ '?' — bu xususiyat MAJBURIY EMAS
}

const mahsulot: Mahsulot = { id: 1, nomi: "Noutbuk" }; // chegirmasiz ham to'g'ri!

// mahsulot.id = 2; // ❌ Xato: 'id' readonly, o'zgartirib bo'lmaydi</code></pre>

<h4>BLOKA 3 — interface va type Alias, kengaytirish (extends)</h4>
<pre><code>// type Alias — interface'ga o'xshash, lekin boshqa sintaksis bilan
type Nuqta = {
  x: number;
  y: number;
};

// Interfeyslarni kengaytirish mumkin
interface Shaxs {
  ism: string;
}

interface Talaba extends Shaxs { // ❗ Shaxs'ning barcha xususiyatlarini oladi
  fakultet: string;
}

const talaba: Talaba = { ism: "Guli", fakultet: "IT" };</code></pre>

<h3>🐛 Ataylab xato — interfeysga mos kelmaydigan obyekt yaratish</h3>
<pre><code>interface Buyurtma {
  id: number;
  mahsulot: string;
  narx: number;
}

const buyurtma: Buyurtma = {
  id: 501,
  mahsulot: "Kitob",
  narxi: 45000, // ❌ 'narxi' emas, 'narx' kerak edi!
};
// TypeScript XATO BERADI: Object literal may only specify known properties,
// and 'narxi' does not exist in type 'Buyurtma'.</code></pre>

<p><strong>Natija:</strong> agar interfeysda belgilangan xususiyat nomi bilan obyektdagi nom bir harf bilan ham farq qilsa (<code>narx</code> o'rniga <code>narxi</code>), TypeScript buni darhol <strong>kompilyatsiya xatosi</strong> sifatida ko'rsatadi. Bu — interfeyslarning eng katta afzalligi: yozuv xatolari yoki unutilgan xususiyatlar production'ga yetib bormasdan, hali kod yozilayotganda aniqlanadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Interfeys nima uchun kerak?</h4>
<p><code>interface</code> — obyektning qanday xususiyatlarga (va ularning turlariga) ega bo'lishi kerakligini belgilaydigan "shartnoma" (contract). Bu shartnomaga mos kelmagan obyekt yaratilsa, TypeScript kompilyatsiya vaqtida xato beradi.</p>

<h4>2. Optional (<code>?</code>) va readonly xususiyatlar</h4>
<p><code>xususiyat?: tur</code> — bu xususiyat obyektda bo'lishi <strong>shart emas</strong>. <code>readonly xususiyat: tur</code> — bu xususiyatga faqat yaratilganda qiymat berish mumkin, keyin uni o'zgartirib bo'lmaydi.</p>

<h4>3. interface va type Alias orasidagi farq</h4>
<p>Ko'p hollarda ular bir xil vazifani bajaradi — obyekt shaklini belgilaydi. Asosiy amaliy farq: <code>interface</code>larni <code>extends</code> orqali kengaytirish odatiy va qulay, <code>type</code> esa union/intersection kabi murakkabroq tur kombinatsiyalarini yaratishda ko'proq qulaylik beradi (5-darsda ko'ramiz).</p>

<h4>4. extends — interfeyslarni kengaytirish</h4>
<p><code>interface B extends A</code> yozuvi <code>B</code>ga <code>A</code>ning barcha xususiyatlarini "meros" qilib beradi, ustiga o'zining qo'shimcha xususiyatlarini qo'shadi. Bu — kod takrorlanishini kamaytirishning qulay usuli.</p>

<h4>5. TypeScript obyektni qanday tekshiradi?</h4>
<p>TypeScript obyekt interfeysga mos kelish-kelmasligini <strong>xususiyat nomlari va ularning turlari</strong> orqali tekshiradi. Kerakli xususiyat yetishmasa, ortiqcha (interfeysda yo'q) xususiyat qo'shilsa yoki tur mos kelmasa — barchasi kompilyatsiya xatosiga olib keladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>interface</code> — obyektning qanday shaklga (xususiyatlar va turlarga) ega bo'lishi kerakligini belgilaydi</li>
<li>✅ <code>xususiyat?: tur</code> — ixtiyoriy, <code>readonly xususiyat: tur</code> — faqat bir marta belgilanadigan xususiyat</li>
<li>✅ <code>interface</code> va <code>type</code> ko'p hollarda bir xil ishlaydi, farqi — kengaytirish uslubida</li>
<li>✅ <code>extends</code> — bir interfeysning xususiyatlarini boshqasiga "meros" qilib berish</li>
<li>✅ Obyektdagi noto'g'ri yozilgan yoki yetishmayotgan xususiyat — kompilyatsiya vaqtida darhol aniqlanadi</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 3: Interfeys va Type Alias
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Oddiy interfeys
// ─────────────────────────────────────────────────────────────────────

interface Foydalanuvchi {
  ism: string;
  yosh: number;
  faol: boolean;
}

const user: Foydalanuvchi = {
  ism: "Olim",
  yosh: 22,
  faol: true,
};

// ─────────────────────────────────────────────────────────────────────
// 2) Optional va readonly xususiyatlar
// ─────────────────────────────────────────────────────────────────────

interface Mahsulot {
  readonly id: number;
  nomi: string;
  chegirma?: number;
}

const mahsulot: Mahsulot = { id: 1, nomi: "Noutbuk" };

// ─────────────────────────────────────────────────────────────────────
// 3) type Alias
// ─────────────────────────────────────────────────────────────────────

type Nuqta = {
  x: number;
  y: number;
};

const markaz: Nuqta = { x: 0, y: 0 };

// ─────────────────────────────────────────────────────────────────────
// 4) Interfeysni kengaytirish (extends)
// ─────────────────────────────────────────────────────────────────────

interface Shaxs {
  ism: string;
}

interface Talaba extends Shaxs {
  fakultet: string;
}

const talaba: Talaba = { ism: "Guli", fakultet: "IT" };

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - noto'g'ri xususiyat nomi (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
interface Buyurtma {
  id: number;
  mahsulot: string;
  narx: number;
}

const buyurtma: Buyurtma = {
  id: 501,
  mahsulot: "Kitob",
  narxi: 45000, // ❌ 'narx' emas, 'narxi' deb yozilgan!
};
*/
"""

L3_EX = [
    {
        "title": "Interfeys nima uchun ishlatiladi?",
        "description": "TypeScript'da interface asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Funksiyani ishga tushirish uchun",
            "Obyektning qanday xususiyatlarga ega bo'lishi kerakligini belgilash uchun",
            "Massivni saralash uchun",
            "Kutubxona import qilish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — obyekt uchun \"shartnoma\" (contract).",
        "explanation": "interface obyektning qanday xususiyatlarga va ularning qanday turlarga ega bo'lishi kerakligini belgilaydigan shartnoma vazifasini bajaradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Ixtiyoriy xususiyat qanday belgilanadi?",
        "description": "Interfeysda bir xususiyatni ixtiyoriy (majburiy emas) qilib belgilash uchun qanday belgi ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": ["!", "?", "*", "&"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Xususiyat nomidan keyin, ':' dan oldin qo'yiladi.",
        "explanation": "xususiyat?: tur yozuvidagi '?' belgisi bu xususiyat obyektda bo'lishi shart emasligini bildiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "readonly xususiyatining ta'siri",
        "description": "Quyidagi amallarni to'g'ri tartibda joylang: avval readonly xususiyatga qiymat berish (yaratishda), keyin uni o'zgartirishga urinish (xato).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Obyekt yaratilganda readonly xususiyatga qiymat beriladi",
            "Obyekt yaratilgandan keyin shu xususiyatni o'zgartirishga urinilsa",
            "TypeScript kompilyatsiya xatosini beradi",
        ],
        "correct_order": [
            "Obyekt yaratilganda readonly xususiyatga qiymat beriladi",
            "Obyekt yaratilgandan keyin shu xususiyatni o'zgartirishga urinilsa",
            "TypeScript kompilyatsiya xatosini beradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Interfeyslarni kengaytirish uchun qaysi kalit so'z ishlatiladi?",
        "description": "Bir interfeysning barcha xususiyatlarini boshqasiga \"meros\" qilib berish uchun qaysi kalit so'z ishlatiladi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "extends",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Noto'g'ri yozilgan xususiyat nomi qanday aniqlanadi?",
        "description": (
            "Agar interfeysda 'narx' deb belgilangan xususiyat, obyekt "
            "yaratilganda xato qilib 'narxi' deb yozilsa, TypeScript buni "
            "qachon va qanday aniqlaydi? Bu nega foydali? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "TypeScript bu xatoni darhol, kompilyatsiya vaqtida (yoki "
            "IDE'da kod yozilayotganda) aniqlaydi va xato xabarini "
            "ko'rsatadi, chunki obyektning xususiyat nomlari interfeysda "
            "belgilangan nomlarga aniq mos kelishi shart. Bu foydali, "
            "chunki yozuv xatolari yoki unutilgan xususiyatlar production "
            "muhitiga yetib bormasdan, hali dasturchi kod yozayotgan "
            "paytida ko'rinadi va tuzatiladi — bu ishonchsiz, jimgina "
            "buziladigan kodning oldini oladi."
        ),
        "hint": "Interfeys — bu shartnoma, va TypeScript uni har doim tekshiradi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>Funksiyalarni tiplashtirish — parametr va qaytish turlari</h2>

<pre class="mermaid">
flowchart LR
    PARAM["Parametr turlari"] --> FUNC["function(a: number, b: number)"]
    FUNC --> RETURN["Qaytish turi: number"]
    RETURN -->|mos kelmasa| ERR["Kompilyatsiya xatosi"]
</pre>

<p>3-darsda obyektlarni tiplashtirdik. Endi — loyihaning eng ko'p ishlatiladigan qismi: <strong>funksiyalar</strong>ni tiplashtirishni o'rganamiz. Har bir parametr va funksiyaning qaytish qiymati aniq turga ega bo'lishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — parametr va qaytish turlari</h4>
<pre><code>function qoshish(a: number, b: number): number {
  return a + b;
}

qoshish(2, 3);       // ✅ 5
// qoshish("2", 3);   // ❌ Xato: 'string' argumentni 'number' parametrga berib bo'lmaydi
// qoshish(2, 3, 4);  // ❌ Xato: funksiya faqat 2 ta argument kutadi</code></pre>

<h4>BLOKA 2 — ixtiyoriy va standart (default) parametrlar</h4>
<pre><code>function salomlash(ism: string, unvon?: string): string { // ❗ '?' — ixtiyoriy parametr
  if (unvon) {
    return `Salom, ${unvon} ${ism}!`;
  }
  return `Salom, ${ism}!`;
}

console.log(salomlash("Olim"));            // "Salom, Olim!"
console.log(salomlash("Olim", "Janob"));   // "Salom, Janob Olim!"

// Standart qiymatli parametr — ixtiyoriy, lekin qiymat berilmasa standart ishlatiladi
function daraja(son: number, ko_rsatkich: number = 2): number {
  return Math.pow(son, ko_rsatkich);
}

console.log(daraja(5));    // 25 (ko_rsatkich standart 2)
console.log(daraja(5, 3)); // 125</code></pre>

<h4>BLOKA 3 — funksiya turi (function type) va arrow function</h4>
<pre><code>// Funksiya turini alohida belgilash mumkin
type MatematikAmal = (a: number, b: number) => number;

const ayirish: MatematikAmal = (a, b) => a - b; // ❗ parametr turlari avtomatik aniqlanadi
const kopaytirish: MatematikAmal = (a, b) => a * b;

console.log(ayirish(10, 4));      // 6
console.log(kopaytirish(3, 4));   // 12

// void — funksiya hech narsa qaytarmaydi
function logYozish(xabar: string): void {
  console.log(`[LOG]: ${xabar}`);
}</code></pre>

<h3>🐛 Ataylab xato — ixtiyoriy parametrni majburiy parametrdan oldin yozish</h3>
<pre><code>// ❌ function foydalanuvchiYaratish(unvon?: string, ism: string) { ... }
// TypeScript XATO BERADI:
// A required parameter cannot follow an optional parameter.

// ✅ To'g'ri variant — ixtiyoriy parametr HAR DOIM oxirida bo'lishi kerak
function foydalanuvchiYaratish(ism: string, unvon?: string) {
  return { ism, unvon };
}</code></pre>

<p><strong>Natija:</strong> agar ixtiyoriy parametr (<code>?</code> bilan) majburiy parametrdan <strong>oldin</strong> yozilsa, TypeScript kompilyatsiya xatosini beradi. Sabab — funksiya chaqirilganda, TypeScript qaysi argument qaysi parametrga tegishli ekanini pozitsiya (tartib) orqali aniqlaydi; agar birinchi parametr ixtiyoriy bo'lib, uni tashlab ketish mumkin bo'lsa, ikkinchi (majburiy) parametr uchun argument qaysi pozitsiyada kelishi noaniq bo'lib qoladi. Shuning uchun qoida qat'iy: <strong>ixtiyoriy parametrlar har doim majburiy parametrlardan keyin</strong> yoziladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Parametr va qaytish turini yozish nima uchun muhim?</h4>
<p>Parametr turi — funksiyaga qanday argument yuborilishi kerakligini, qaytish turi esa funksiyaning natijasi qanday tur bo'lishini belgilaydi. Ikkalasi ham funksiyani noto'g'ri ishlatishning oldini oladi.</p>

<h4>2. Ixtiyoriy (<code>?</code>) va standart qiymatli parametrlar farqi</h4>
<p><code>parametr?: tur</code> — parametr berilmasa, uning qiymati <code>undefined</code> bo'ladi. <code>parametr: tur = qiymat</code> — parametr berilmasa, avtomatik ravishda ko'rsatilgan standart qiymat ishlatiladi.</p>

<h4>3. Funksiya turini (function type) alohida belgilash</h4>
<p><code>type MatematikAmal = (a: number, b: number) => number;</code> — bu funksiyaning "shakli"ni (qanday parametrlar qabul qilib, qanday tur qaytarishini) belgilaydi. Bu ayniqsa funksiyani parametr sifatida boshqa funksiyaga uzatishda foydali.</p>

<h4>4. void turi</h4>
<p><code>void</code> — funksiya hech qanday qiymat qaytarmasligini bildiradi (masalan, faqat <code>console.log</code> chaqiruvchi funksiya). Bu 2-darsda ko'rgan <code>never</code>dan farq qiladi — <code>void</code>li funksiya normal tugaydi, faqat qaytish qiymati yo'q.</p>

<h4>5. Nega ixtiyoriy parametr oxirida bo'lishi shart?</h4>
<p>TypeScript (va JavaScript) argumentlarni <strong>pozitsiya</strong> bo'yicha funksiyaga bog'laydi. Agar ixtiyoriy parametr o'rtada yoki boshida bo'lsa, uni "tashlab ketish" qanday pozitsiyaga ta'sir qilishi noaniq bo'lib qoladi — shuning uchun bu qat'iy taqiqlangan.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Funksiya parametrlari va qaytish qiymati aniq turga ega bo'lishi mumkin: <code>function(a: number): string</code></li>
<li>✅ <code>parametr?: tur</code> — ixtiyoriy, <code>parametr: tur = qiymat</code> — standart qiymatli parametr</li>
<li>✅ Funksiya turini <code>type</code> orqali alohida belgilash mumkin: <code>(a: number, b: number) => number</code></li>
<li>✅ <code>void</code> — funksiya qiymat qaytarmaydi, lekin normal tugaydi</li>
<li>✅ Ixtiyoriy parametrlar har doim majburiy parametrlardan <strong>keyin</strong> yozilishi shart</li>
</ul>
"""

L4_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 4: Funksiyalarni tiplashtirish
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Parametr va qaytish turlari
// ─────────────────────────────────────────────────────────────────────

function qoshish(a: number, b: number): number {
  return a + b;
}

console.log(qoshish(2, 3));

// ─────────────────────────────────────────────────────────────────────
// 2) Ixtiyoriy va standart parametrlar
// ─────────────────────────────────────────────────────────────────────

function salomlash(ism: string, unvon?: string): string {
  if (unvon) {
    return `Salom, ${unvon} ${ism}!`;
  }
  return `Salom, ${ism}!`;
}

function daraja(son: number, ko_rsatkich: number = 2): number {
  return Math.pow(son, ko_rsatkich);
}

console.log(salomlash("Olim"));
console.log(daraja(5));

// ─────────────────────────────────────────────────────────────────────
// 3) Funksiya turi (function type)
// ─────────────────────────────────────────────────────────────────────

type MatematikAmal = (a: number, b: number) => number;

const ayirish: MatematikAmal = (a, b) => a - b;
const kopaytirish: MatematikAmal = (a, b) => a * b;

console.log(ayirish(10, 4), kopaytirish(3, 4));

// ─────────────────────────────────────────────────────────────────────
// 4) void - qiymat qaytarmaydigan funksiya
// ─────────────────────────────────────────────────────────────────────

function logYozish(xabar: string): void {
  console.log(`[LOG]: ${xabar}`);
}

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - ixtiyoriy parametr majburiydan oldin (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
function foydalanuvchiYaratishXato(unvon?: string, ism: string) {
  // ❌ Xato: A required parameter cannot follow an optional parameter.
  return { ism, unvon };
}
*/

// ✅ To'g'ri variant
function foydalanuvchiYaratish(ism: string, unvon?: string) {
  return { ism, unvon };
}
"""

L4_EX = [
    {
        "title": "Funksiya turi yozuvi",
        "description": "Ikkita number qabul qilib, number qaytaruvchi funksiya turi qanday yoziladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "function(number, number): number",
            "(a: number, b: number) => number",
            "number => number => number",
            "[number, number, number]",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Parametrlar qavs ichida, keyin => bilan qaytish turi yoziladi.",
        "explanation": "Funksiya turi (a: number, b: number) => number ko'rinishida yoziladi: parametrlar qavsda, so'ng '=>' orqali qaytish turi ko'rsatiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Ixtiyoriy parametr qayerda yoziladi?",
        "description": "Ixtiyoriy (?) parametr funksiya e'lonida qayerda joylashishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim birinchi bo'lib",
            "Majburiy parametrlardan keyin, oxirida",
            "Joyi ahamiyatsiz",
            "Faqat arrow function'larda ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Argumentlar pozitsiya bo'yicha bog'lanadi.",
        "explanation": "Ixtiyoriy parametrlar har doim majburiy parametrlardan keyin, funksiya parametrlar ro'yxatining oxirida yozilishi shart.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "daraja(5) chaqiruvi natijasini aniqlash",
        "description": "function daraja(son: number, ko_rsatkich: number = 2) deb e'lon qilingan. Quyidagi chaqiruvlarni natijalariga mos ravishda tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "daraja(5) -> 25 (standart ko_rsatkich=2 ishlatiladi)",
            "daraja(5, 3) -> 125 (ko_rsatkich=3 beriladi)",
        ],
        "correct_order": [
            "daraja(5) -> 25 (standart ko_rsatkich=2 ishlatiladi)",
            "daraja(5, 3) -> 125 (ko_rsatkich=3 beriladi)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "void turi nima uchun ishlatiladi?",
        "description": "Funksiya hech qanday qiymat qaytarmasligini, lekin normal tugashini bildirish uchun qaysi tur ishlatiladi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "void",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Ixtiyoriy parametrni majburiydan oldin yozish nega xato beradi?",
        "description": (
            "function foydalanuvchi(unvon?: string, ism: string) deb "
            "yozilsa, TypeScript nega xato beradi? Bu qoida qanday "
            "muammoning oldini oladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "TypeScript va JavaScript argumentlarni funksiyaga ularning "
            "POZITSIYASI (tartibi) bo'yicha bog'laydi. Agar ixtiyoriy "
            "parametr birinchi o'rinda bo'lsa va uni chaqiruvda tashlab "
            "ketish mumkin bo'lsa, keyingi (majburiy) parametr uchun "
            "berilgan argument qaysi pozitsiyaga tegishli ekanini aniqlash "
            "imkonsiz bo'lib qoladi — masalan foydalanuvchi(\"Olim\") "
            "chaqiruvida \"Olim\" unvon uchunmi yoki ism uchunmi, aniq "
            "emas. Shuning uchun TypeScript bu noaniqlikning oldini olish "
            "uchun ixtiyoriy parametrlarni faqat majburiy parametrlardan "
            "keyin yozishga ruxsat beradi."
        ),
        "hint": "Argumentlar funksiyaga qanday bog'lanadi — nom orqalimi yoki pozitsiya orqalimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>Union, Intersection va Type Narrowing</h2>

<pre class="mermaid">
flowchart LR
    UNION["string | number — YOKI biri, YOKI ikkinchisi"] --> NARROW["typeof tekshiruvi"]
    NARROW -->|string bo'lsa| STR["string metodlari ishlaydi"]
    NARROW -->|number bo'lsa| NUM["number metodlari ishlaydi"]
    INTER["A & B — IKKALASI HAM birga"] --> BOTH["Barcha xususiyatlar majburiy"]
</pre>

<p>Ba'zan qiymat bir nechta turdan <strong>biri</strong> bo'lishi mumkin (masalan, ID son yoki matn bo'lishi mumkin), ba'zida esa ikkita turning <strong>barcha xususiyatlarini birga</strong> talab qilamiz. Bu ikki holat uchun mos ravishida <strong>Union</strong> (<code>|</code>) va <strong>Intersection</strong> (<code>&amp;</code>) turlari ishlatiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Union turi (<code>|</code>)</h4>
<pre><code>function idChiqarish(id: string | number): string { // ❗ id YOKI string, YOKI number bo'lishi mumkin
  return `ID: ${id}`;
}

idChiqarish(101);      // ✅ to'g'ri
idChiqarish("ABC-101"); // ✅ to'g'ri
// idChiqarish(true);   // ❌ Xato: 'boolean' 'string | number'ga mos kelmaydi</code></pre>

<h4>BLOKA 2 — Type Narrowing: turni "toraytirish"</h4>
<pre><code>function narxKorsatish(narx: string | number): string {
  if (typeof narx === "number") {
    // ❗ Shu blokda TypeScript narx'ni FAQAT number deb biladi
    return `${narx.toFixed(2)} so'm`; // ✅ toFixed — faqat number metodi
  }
  // ❗ Bu yerda esa TypeScript narx'ni FAQAT string deb biladi
  return narx.toUpperCase(); // ✅ toUpperCase — faqat string metodi
}</code></pre>

<h4>BLOKA 3 — Intersection turi (<code>&amp;</code>) va Discriminated Union</h4>
<pre><code>interface Ism { ism: string; }
interface Yosh { yosh: number; }

type ShaxsMalumoti = Ism &amp; Yosh; // ❗ IKKALASINING HAM barcha xususiyatlari majburiy

const shaxs: ShaxsMalumoti = { ism: "Olim", yosh: 22 }; // ikkalasi ham kerak

// Discriminated Union — umumiy "belgi" xususiyati orqali turlarni ajratish
interface MuvaffaqiyatliJavob {
  holat: "success"; // ❗ aniq literal qiymat — "belgi"
  malumot: string;
}
interface XatoJavob {
  holat: "error";
  xabar: string;
}
type ApiJavob = MuvaffaqiyatliJavob | XatoJavob;

function javobniQayta(javob: ApiJavob) {
  if (javob.holat === "success") {
    console.log(javob.malumot); // ✅ TypeScript biladi: bu MuvaffaqiyatliJavob
  } else {
    console.log(javob.xabar);   // ✅ TypeScript biladi: bu XatoJavob
  }
}</code></pre>

<h3>🐛 Ataylab xato — Type Narrowing'siz union turdan foydalanish</h3>
<pre><code>function narxKorsatishXato(narx: string | number): string {
  return narx.toFixed(2); // ❌ Xato: Property 'toFixed' does not exist on type 'string'
  // TypeScript narx string HAM bo'lishi mumkinligini biladi,
  // va string'da toFixed() metodi yo'q — shuning uchun xato beradi!
}</code></pre>

<p><strong>Natija:</strong> union turdagi (<code>string | number</code>) qiymatga nisbatan, faqat <strong>ikkala turga ham umumiy</strong> bo'lgan metodlar/xususiyatlarni to'g'ridan-to'g'ri chaqirish mumkin. <code>toFixed()</code> — faqat <code>number</code>ga xos metod, <code>string</code>da mavjud emas. Shuning uchun TypeScript, qiymat aslida qaysi tur ekanini <strong>hali bilmagani</strong> uchun xato beradi. Yechim — <code>typeof</code> (yoki boshqa tur tekshiruvi) orqali <strong>Type Narrowing</strong> qilish: shundan keyingina TypeScript qaysi blokda qiymat qaysi aniq turga ega ekanini biladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Union turi (<code>|</code>) qachon ishlatiladi?</h4>
<p>Qiymat bir nechta turdan <strong>istalgan biri</strong> bo'lishi mumkin bo'lgan holatlarda ishlatiladi, masalan <code>string | number</code> — "yoki matn, yoki son".</p>

<h4>2. Intersection turi (<code>&amp;</code>) qachon ishlatiladi?</h4>
<p>Ikkita (yoki undan ko'p) turning <strong>barcha xususiyatlarini birga</strong> talab qiladigan holatlarda ishlatiladi. <code>A &amp; B</code> — natija turi <code>A</code>ning ham, <code>B</code>ning ham barcha xususiyatlariga ega bo'lishi shart.</p>

<h4>3. Type Narrowing nima?</h4>
<p>Union turdagi qiymatning qaysi aniq turga ega ekanini <code>typeof</code>, <code>instanceof</code> yoki boshqa shart orqali "tekshirib", shu tekshiruv ichidagi kod blokida TypeScript qiymatning <strong>faqat shu aniq turga</strong> ega ekanini bilishi jarayoni.</p>

<h4>4. Discriminated Union — "belgi" xususiyati orqali ajratish</h4>
<p>Bir nechta interfeys umumiy nomdagi, lekin har birida <strong>o'ziga xos literal qiymatli</strong> (masalan <code>holat: "success"</code> yoki <code>holat: "error"</code>) xususiyatga ega bo'lsa, TypeScript shu xususiyatni tekshirish orqali qaysi interfeys ekanini avtomatik "biladi". Bu — real loyihalarda API javoblarini, holatlarni boshqarishning eng ishonchli usuli.</p>

<h4>5. Nega Type Narrowing'siz union turdan to'g'ridan-to'g'ri metod chaqirib bo'lmaydi?</h4>
<p>TypeScript qiymat ikkala turdan qaysi biri ekanini <strong>oldindan bilmaydi</strong>, shuning uchun faqat ikkala turda ham mavjud bo'lgan (umumiy) metodlarni xavfsiz deb hisoblaydi. Faqat bittasiga xos metodni chaqirish — boshqa tur bo'lganda dastur "portlashi" mumkinligini bildiradi, shuning uchun TypeScript buni oldindan taqiqlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>A | B</code> (Union) — qiymat A yoki B turlaridan biri bo'lishi mumkin</li>
<li>✅ <code>A &amp; B</code> (Intersection) — qiymat A va B'ning barcha xususiyatlariga ega bo'lishi shart</li>
<li>✅ Type Narrowing — <code>typeof</code>/<code>instanceof</code> orqali union turni aniq turga "toraytirish"</li>
<li>✅ Discriminated Union — umumiy literal-qiymatli xususiyat orqali turlarni ishonchli ajratish</li>
<li>✅ Type Narrowing qilinmasdan union turga xos bo'lmagan metod chaqirilsa — kompilyatsiya xatosi chiqadi</li>
</ul>
"""

L5_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 5: Union, Intersection va Type Narrowing
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Union turi
// ─────────────────────────────────────────────────────────────────────

function idChiqarish(id: string | number): string {
  return `ID: ${id}`;
}

console.log(idChiqarish(101), idChiqarish("ABC-101"));

// ─────────────────────────────────────────────────────────────────────
// 2) Type Narrowing - typeof orqali turni toraytirish
// ─────────────────────────────────────────────────────────────────────

function narxKorsatish(narx: string | number): string {
  if (typeof narx === "number") {
    return `${narx.toFixed(2)} so'm`;
  }
  return narx.toUpperCase();
}

// ─────────────────────────────────────────────────────────────────────
// 3) Intersection turi
// ─────────────────────────────────────────────────────────────────────

interface Ism {
  ism: string;
}
interface Yosh {
  yosh: number;
}

type ShaxsMalumoti = Ism & Yosh;

const shaxs: ShaxsMalumoti = { ism: "Olim", yosh: 22 };

// ─────────────────────────────────────────────────────────────────────
// 4) Discriminated Union
// ─────────────────────────────────────────────────────────────────────

interface MuvaffaqiyatliJavob {
  holat: "success";
  malumot: string;
}
interface XatoJavob {
  holat: "error";
  xabar: string;
}
type ApiJavob = MuvaffaqiyatliJavob | XatoJavob;

function javobniQayta(javob: ApiJavob) {
  if (javob.holat === "success") {
    console.log(javob.malumot);
  } else {
    console.log(javob.xabar);
  }
}

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - Type Narrowing'siz union tur (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
function narxKorsatishXato(narx: string | number): string {
  return narx.toFixed(2); // ❌ Property 'toFixed' does not exist on type 'string'
}
*/
"""

L5_EX = [
    {
        "title": "Union turi qanday belgilanadi?",
        "description": "String YOKI number bo'lishi mumkin bo'lgan qiymat uchun tur qanday yoziladi?",
        "exercise_type": "multiple_choice",
        "options": ["string & number", "string | number", "string + number", "[string, number]"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "\"Yoki\" ma'nosini beruvchi belgi.",
        "explanation": "Union turi '|' belgisi bilan yoziladi: string | number — qiymat ikkalasidan biri bo'lishi mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Intersection turi nimani anglatadi?",
        "description": "A & B (Intersection) turi qiymat haqida nimani bildiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Qiymat A yoki B bo'lishi mumkin",
            "Qiymat A va B'ning barcha xususiyatlariga ega bo'lishi shart",
            "Qiymat faqat A bo'lishi kerak",
            "Qiymat hech qanday turga mos kelmasligi kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "\"Va\" ma'nosini beruvchi belgi.",
        "explanation": "Intersection (A & B) qiymatning A'ning ham, B'ning ham barcha xususiyatlariga birga ega bo'lishini talab qiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Type Narrowing jarayonini tartiblang",
        "description": "Union turdagi qiymatdan uning turiga xos metodni xavfsiz chaqirish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Parametr union turida e'lon qilinadi (masalan string | number)",
            "typeof orqali aniq turi tekshiriladi",
            "Tekshiruv ichidagi blokda TypeScript turni 'toraytiradi'",
            "Endi shu turga xos metodni xavfsiz chaqirish mumkin",
        ],
        "correct_order": [
            "Parametr union turida e'lon qilinadi (masalan string | number)",
            "typeof orqali aniq turi tekshiriladi",
            "Tekshiruv ichidagi blokda TypeScript turni 'toraytiradi'",
            "Endi shu turga xos metodni xavfsiz chaqirish mumkin",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Discriminated Union'da qaysi xususiyat ishlatiladi?",
        "description": "Bir nechta interfeysni umumiy, lekin har birida o'ziga xos literal qiymatga ega xususiyat orqali ajratish usuli nima deb ataladi? (masalan: 'discriminated union')",
        "exercise_type": "text_input",
        "expected_answer": "discriminated union",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Type Narrowing'siz union turga metod chaqirib bo'lmaydi?",
        "description": (
            "narx: string | number parametriga to'g'ridan-to'g'ri "
            "narx.toFixed(2) chaqirilsa, nega TypeScript xato beradi, "
            "garchi toFixed() number uchun to'g'ri metod bo'lsa ham? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "TypeScript narx qiymati string ham bo'lishi mumkinligini "
            "biladi, va string turida toFixed() metodi mavjud emas. Union "
            "turdagi qiymat uchun TypeScript faqat ikkala (barcha) turga "
            "umumiy bo'lgan metodlarni xavfsiz deb hisoblaydi, chunki u "
            "hali qiymat aniq qaysi tur ekanini bilmaydi. Agar Type "
            "Narrowing (masalan typeof narx === 'number' tekshiruvi) "
            "qilinmasa, TypeScript bu chaqiruvni xavfli deb hisoblaydi va "
            "kompilyatsiya xatosini beradi — chunki agar narx aslida "
            "string bo'lib chiqsa, dastur ishga tushganda xatoga uchraydi."
        ),
        "hint": "TypeScript qiymat aniq qaysi tur ekanini hali bilmaydi — faqat ikkalasiga umumiy narsalarga ishonadi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>Generics asoslari — moslashuvchan va xavfsiz kod</h2>

<pre class="mermaid">
flowchart LR
    CALL1["birinchi(5)"] --> GEN["function birinchi&lt;T&gt;(arr: T[]): T"]
    CALL2["birinchi(['a','b'])"] --> GEN
    GEN -->|T=number bo'lsa| OUT1["number qaytaradi"]
    GEN -->|T=string bo'lsa| OUT2["string qaytaradi"]
</pre>

<p>4-darsda funksiyalarni aniq turlar bilan (masalan <code>number</code>) tiplashtirdik. Lekin ba'zi funksiyalar <strong>istalgan tur</strong> bilan bir xil mantiqda ishlaydi — masalan, massivning birinchi elementini qaytaruvchi funksiya son massivi uchun ham, matn massivi uchun ham bir xil ishlaydi. <strong>Generics</strong> — aynan shu holatlar uchun: turni "o'zgaruvchi" sifatida ishlatish imkonini beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi generic funksiya</h4>
<pre><code>function birinchiElement&lt;T&gt;(arr: T[]): T { // ❗ T — "tur o'zgaruvchisi", istalgan turni anglatishi mumkin
  return arr[0];
}

const son = birinchiElement([10, 20, 30]);       // ❗ TypeScript T'ni 'number' deb aniqlaydi
const matn = birinchiElement(["olma", "uzum"]);  // ❗ TypeScript T'ni 'string' deb aniqlaydi

console.log(son.toFixed(1));       // ✅ son — number, toFixed ishlaydi
console.log(matn.toUpperCase());   // ✅ matn — string, toUpperCase ishlaydi</code></pre>

<h4>BLOKA 2 — generic interfeys</h4>
<pre><code>interface Qути&lt;T&gt; { // ❗ Qути — istalgan turdagi qiymatni saqlovchi umumiy tuzilma
  qiymat: T;
}

const sonQutisi: Qути&lt;number&gt; = { qiymat: 42 };
const matnQutisi: Qути&lt;string&gt; = { qiymat: "Salom" };

// const notoGri: Qути&lt;number&gt; = { qiymat: "Salom" };
// ❌ Xato: 'string'ni 'number'ga berib bo'lmaydi</code></pre>

<h4>BLOKA 3 — Generic constraints (<code>extends</code> bilan cheklash)</h4>
<pre><code>// Cheklovsiz generic — .length xususiyatiga kirish mumkin emas!
// function uzunlikOlish&lt;T&gt;(item: T): number {
//   return item.length; // ❌ Xato: T'da .length borligi kafolatlanmagan
// }

// ✅ Constraint (cheklov) bilan — faqat 'length' xususiyatiga ega turlar qabul qilinadi
interface UzunlikBor {
  length: number;
}

function uzunlikOlish&lt;T extends UzunlikBor&gt;(item: T): number {
  return item.length; // ✅ endi xavfsiz — T albatta .length'ga ega
}

console.log(uzunlikOlish("salom"));        // ✅ string'da length bor — 5
console.log(uzunlikOlish([1, 2, 3, 4]));   // ✅ massivda length bor — 4
// console.log(uzunlikOlish(42));           // ❌ Xato: number'da length yo'q</code></pre>

<h3>🐛 Ataylab xato — generic o'rniga any ishlatish</h3>
<pre><code>// ❌ any bilan — tur bog'lanishi butunlay yo'qoladi
function birinchiElementXato(arr: any[]): any {
  return arr[0];
}

const natija = birinchiElementXato([10, 20, 30]);
console.log(natija.toUpperCase()); // ❌ Runtime xato: 10.toUpperCase is not a function
// TypeScript bu yerda HECH QANDAY ogohlantirish bermaydi, chunki 'any' hamma narsani ruxsat beradi!</code></pre>

<p><strong>Natija:</strong> <code>any[]</code> ishlatilganda, funksiya kirish va chiqish turlari orasidagi <strong>bog'lanish butunlay yo'qoladi</strong> — TypeScript <code>arr</code>ning haqiqiy elementi qanday tur ekanini "unutadi". Natijada <code>natija.toUpperCase()</code> kabi mutlaqo mos kelmaydigan chaqiruv ham kompilyatsiya vaqtida ushlanmaydi, balki dastur ishga tushganda "portlaydi" (<code>toUpperCase is not a function</code>). Generics esa — <code>T</code> orqali kirish va chiqish turlari orasidagi bog'lanishni <strong>saqlab qoladi</strong>, shu bilan birga funksiyani istalgan tur bilan ishlatish imkonini beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Generics nima uchun kerak?</h4>
<p>Generics funksiya yoki interfeysni <strong>bir marta</strong> yozib, uni turli xil turlar bilan <strong>qayta ishlatish</strong> imkonini beradi — bunda <code>any</code>dan farqli o'laroq, kirish va chiqish turlari orasidagi bog'lanish saqlanib qoladi.</p>

<h4>2. <code>&lt;T&gt;</code> nima?</h4>
<p><code>T</code> — "tur parametri" (type parameter), funksiya chaqirilganda haqiqiy turga almashtiriladigan "o'zgaruvchi tur"dir. Nomi istalgancha bo'lishi mumkin (odatda <code>T</code>, <code>U</code>, <code>K</code>, <code>V</code> ishlatiladi), lekin bitta funksiya/interfeys ichida izchil bo'lishi kerak.</p>

<h4>3. Generic va any orasidagi asosiy farq</h4>
<p><code>any</code> — tur tekshiruvini butunlay o'chiradi. Generic (<code>T</code>) esa — kirish turi bilan chiqish turi orasidagi <strong>bog'lanishni saqlagan holda</strong> moslashuvchanlik beradi: agar <code>T</code> = <code>number</code> bo'lsa, funksiya <code>number</code> qaytarishi kafolatlanadi.</p>

<h4>4. Generic constraint (<code>extends</code>) nima uchun kerak?</h4>
<p>Ba'zida <code>T</code> istalgan tur emas, balki <strong>ma'lum xususiyatlarga ega</strong> tur bo'lishi kerak (masalan, <code>.length</code>ga ega bo'lishi). <code>T extends UzunlikBor</code> yozuvi TypeScript'ga "<code>T</code> qanday tur bo'lishidan qat'i nazar, albatta <code>length</code> xususiyatiga ega bo'lishi kerak" deb aytadi.</p>

<h4>5. Generic interfeys qanday ishlaydi?</h4>
<p><code>interface Quti&lt;T&gt;</code> — ichida qanday turdagi qiymat saqlanishini keyinroq (foydalanish paytida) belgilash imkonini beradi: <code>Quti&lt;number&gt;</code>, <code>Quti&lt;string&gt;</code> va h.k.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Generics (<code>&lt;T&gt;</code>) — funksiya/interfeysni bir marta yozib, turli turlar bilan qayta ishlatish imkonini beradi</li>
<li>✅ Generic — <code>any</code>dan farqli o'laroq, kirish va chiqish turlari orasidagi bog'lanishni saqlaydi</li>
<li>✅ Generic interfeys (<code>Quti&lt;T&gt;</code>) — foydalanish paytida aniq turni belgilash imkonini beradi</li>
<li>✅ <code>T extends Xususiyat</code> — generic turni ma'lum xususiyatlarga ega turlar bilan cheklaydi</li>
<li>✅ <code>any[]</code> ishlatish — tur bog'lanishini yo'qotadi, runtime xatolarga olib kelishi mumkin</li>
</ul>
"""

L6_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 6: Generics asoslari
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Birinchi generic funksiya
// ─────────────────────────────────────────────────────────────────────

function birinchiElement<T>(arr: T[]): T {
  return arr[0];
}

const son = birinchiElement([10, 20, 30]);
const matn = birinchiElement(["olma", "uzum"]);

console.log(son.toFixed(1));
console.log(matn.toUpperCase());

// ─────────────────────────────────────────────────────────────────────
// 2) Generic interfeys
// ─────────────────────────────────────────────────────────────────────

interface Quti<T> {
  qiymat: T;
}

const sonQutisi: Quti<number> = { qiymat: 42 };
const matnQutisi: Quti<string> = { qiymat: "Salom" };

// ─────────────────────────────────────────────────────────────────────
// 3) Generic constraint - extends bilan cheklash
// ─────────────────────────────────────────────────────────────────────

interface UzunlikBor {
  length: number;
}

function uzunlikOlish<T extends UzunlikBor>(item: T): number {
  return item.length;
}

console.log(uzunlikOlish("salom"));
console.log(uzunlikOlish([1, 2, 3, 4]));

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - any bilan tur bog'lanishini yo'qotish (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
function birinchiElementXato(arr: any[]): any {
  return arr[0];
}
const natija = birinchiElementXato([10, 20, 30]);
console.log(natija.toUpperCase()); // ❌ Runtime xato: 10.toUpperCase is not a function
*/
"""

L6_EX = [
    {
        "title": "Generics nima uchun ishlatiladi?",
        "description": "TypeScript'da generics (masalan <T>) asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Tur tekshiruvini butunlay o'chirish uchun",
            "Funksiya/interfeysni bir marta yozib, turli turlar bilan qayta ishlatish uchun",
            "Faqat sonlar bilan ishlash uchun",
            "Kodni sekinlashtirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — any'dan farqli, xavfsiz moslashuvchanlik.",
        "explanation": "Generics funksiya yoki interfeysni bir marta yozib, uni turli xil turlar bilan qayta ishlatish imkonini beradi, shu bilan birga kirish/chiqish turlari orasidagi bog'lanishni saqlaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Generic va any orasidagi asosiy farq",
        "description": "Generic (<T>) bilan any orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech qanday farqi yo'q",
            "Generic kirish va chiqish turlari orasidagi bog'lanishni saqlaydi, any esa yo'qotadi",
            "any faqat massivlar uchun ishlatiladi",
            "Generic faqat interfeyslar uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Biri xavfsiz moslashuvchanlik, biri tur tekshiruvini butunlay o'chiradi.",
        "explanation": "any tur tekshiruvini butunlay o'chiradi va kirish/chiqish turlari orasidagi bog'lanishni yo'qotadi. Generic esa shu bog'lanishni saqlagan holda moslashuvchanlik beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Generic constraint qo'llash jarayonini tartiblang",
        "description": "uzunlikOlish<T extends UzunlikBor> funksiyasini yaratish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "'length' xususiyatiga ega UzunlikBor interfeysi yaratiladi",
            "Funksiya <T extends UzunlikBor> bilan e'lon qilinadi",
            "Funksiya ichida item.length xavfsiz ishlatiladi",
            "Faqat 'length'ga ega qiymatlar (string, massiv) bilan chaqirish mumkin bo'ladi",
        ],
        "correct_order": [
            "'length' xususiyatiga ega UzunlikBor interfeysi yaratiladi",
            "Funksiya <T extends UzunlikBor> bilan e'lon qilinadi",
            "Funksiya ichida item.length xavfsiz ishlatiladi",
            "Faqat 'length'ga ega qiymatlar (string, massiv) bilan chaqirish mumkin bo'ladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Generic turni cheklash uchun qaysi kalit so'z ishlatiladi?",
        "description": "Generic tur parametrini ma'lum xususiyatlarga ega turlar bilan cheklash uchun qaysi kalit so'z ishlatiladi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "extends",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "any[] ishlatish nega xavfli?",
        "description": (
            "Agar birinchiElement funksiyasi T[] o'rniga any[] parametr "
            "bilan yozilsa, va natija.toUpperCase() kabi mos kelmaydigan "
            "chaqiruv qilinsa, TypeScript buni qachon aniqlaydi (yoki "
            "aniqlamaydi)? Bu nega xavfli? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar parametr any[] deb belgilansa, TypeScript massiv "
            "elementining haqiqiy turi haqida hech qanday ma'lumotni "
            "saqlamaydi — funksiya natijasi ham any turida bo'lib qoladi. "
            "Shuning uchun natija.toUpperCase() kabi noto'g'ri chaqiruv "
            "kompilyatsiya vaqtida hech qanday xato bermaydi, lekin agar "
            "haqiqiy element (masalan son) toUpperCase metodiga ega "
            "bo'lmasa, dastur ishga tushganda (runtime) 'toUpperCase is "
            "not a function' kabi xato bilan portlaydi. Bu xavfli, chunki "
            "aynan TypeScript'ning maqsadi — bunday xatolarni oldindan, "
            "kompilyatsiya vaqtida aniqlash, lekin any ishlatilganda bu "
            "himoya butunlay yo'qoladi."
        ),
        "hint": "any[] bilan funksiya kirish va chiqish turi orasidagi bog'lanish saqlanadimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L7_TEXT = """\
<h2>Class'lar va Access Modifiers</h2>

<pre class="mermaid">
flowchart TB
    CLASS["class BankHisobi"] --> PUB["public — hamma joydan kirish mumkin"]
    CLASS --> PRIV["private — faqat class ichida"]
    CLASS --> PROT["protected — class va uning avlodlarida"]
    IMPL["interface"] -.->|implements| CLASS
</pre>

<p>JavaScript'da class'lar mavjud, lekin ularda xususiyatlarni "yashirish" imkoniyati cheklangan. TypeScript class'larga <strong>access modifier</strong>lar (kirish darajasi belgilovchilari) qo'shadi — bu orqali qaysi xususiyat/metodga qayerdan murojaat qilish mumkinligini aniq belgilash mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — public, private, protected</h4>
<pre><code>class BankHisobi {
  public egasi: string;      // ❗ public — hamma joydan kirish mumkin (standart)
  private balans: number;    // ❗ private — FAQAT shu class ichida kirish mumkin
  protected hisobRaqami: string; // ❗ protected — shu class VA uning avlodlarida

  constructor(egasi: string, boshlangichBalans: number, hisobRaqami: string) {
    this.egasi = egasi;
    this.balans = boshlangichBalans;
    this.hisobRaqami = hisobRaqami;
  }

  balansniKorish(): number {
    return this.balans; // ✅ class ichidan private xususiyatga kirish mumkin
  }
}

const hisob = new BankHisobi("Olim", 1000000, "UZ-001");
console.log(hisob.egasi);          // ✅ public — tashqaridan kirish mumkin
// console.log(hisob.balans);      // ❌ Xato: 'balans' private, tashqaridan kirib bo'lmaydi
console.log(hisob.balansniKorish()); // ✅ metod orqali xavfsiz kirish</code></pre>

<h4>BLOKA 2 — interfeysni class orqali amalga oshirish (implements)</h4>
<pre><code>interface Hayvon {
  ism: string;
  ovozChiqarish(): string;
}

class It implements Hayvon { // ❗ It class'i Hayvon interfeysidagi HAMMA narsani taqdim etishi shart
  ism: string;

  constructor(ism: string) {
    this.ism = ism;
  }

  ovozChiqarish(): string {
    return "Vov-vov!";
  }
}

const kuchuk = new It("Rex");
console.log(kuchuk.ovozChiqarish()); // "Vov-vov!"</code></pre>

<h4>BLOKA 3 — abstract class</h4>
<pre><code>abstract class Shakl { // ❗ abstract — bevosita 'new Shakl()' bilan obyekt yaratib bo'lmaydi
  abstract yuzaniHisoblash(): number; // ❗ avlod class majburiy amalga oshirishi kerak

  malumotChiqarish(): string {
    return `Yuza: ${this.yuzaniHisoblash()}`;
  }
}

class Kvadrat extends Shakl {
  constructor(private tomon: number) {
    super();
  }
  yuzaniHisoblash(): number {
    return this.tomon * this.tomon;
  }
}

const kvadrat = new Kvadrat(5);
console.log(kvadrat.malumotChiqarish()); // "Yuza: 25"
// const shakl = new Shakl(); // ❌ Xato: Cannot create an instance of an abstract class</code></pre>

<h3>🐛 Ataylab xato — private xususiyatga tashqaridan murojaat qilish</h3>
<pre><code>class BankHisobi {
  private balans: number = 1000;
}

const hisob = new BankHisobi();
console.log(hisob.balans); // ❌ Xato: Property 'balans' is private and only
                            //         accessible within class 'BankHisobi'.</code></pre>

<p><strong>Natija:</strong> <code>private</code> deb belgilangan xususiyatga class'dan <strong>tashqarida</strong> murojaat qilishga urinilsa, TypeScript kompilyatsiya xatosini beradi. Bu — <strong>inkapsulyatsiya</strong> (encapsulation) tamoyilining amalda qo'llanishi: class'ning ichki holatini tashqi kod to'g'ridan-to'g'ri o'zgartira olmaydi, faqat class o'zi taqdim etgan (odatda <code>public</code>) metodlar orqali "nazorat qilingan" tarzda ishlashi mumkin.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. public, private, protected orasidagi farq</h4>
<p><code>public</code> (standart) — istalgan joydan kirish mumkin. <code>private</code> — faqat shu class ichida. <code>protected</code> — shu class va undan meros olgan (extends qilingan) avlod class'larida kirish mumkin, lekin tashqaridan yo'q.</p>

<h4>2. implements nima uchun kerak?</h4>
<p><code>class X implements InterfeysY</code> yozuvi <code>X</code> class'i <code>InterfeysY</code>da belgilangan barcha xususiyat va metodlarni <strong>taqdim etishi shart</strong>ligini bildiradi. Agar biror narsa yetishmasa, TypeScript kompilyatsiya xatosini beradi.</p>

<h4>3. abstract class nima?</h4>
<p><code>abstract class</code> — undan to'g'ridan-to'g'ri obyekt (<code>new</code> orqali) yaratib bo'lmaydigan, faqat boshqa class'lar uchun "andoza" (template) vazifasini bajaradigan class. <code>abstract</code> metodlar avlod class'da <strong>majburiy</strong> amalga oshirilishi kerak.</p>

<h4>4. Nega inkapsulyatsiya (private) muhim?</h4>
<p>Agar barcha xususiyatlar <code>public</code> bo'lsa, istalgan tashqi kod class'ning ichki holatini nazoratsiz o'zgartirishi mumkin — bu xatolarga olib kelishi oson. <code>private</code> xususiyatlar class o'ziga xos qoidalar (masalan, balans hech qachon manfiy bo'lmasligi) orqaligina o'zgarishini kafolatlaydi.</p>

<h4>5. constructor ichida qisqartma yozuv</h4>
<p><code>constructor(private tomon: number)</code> — bu TypeScript'ning qulay qisqartmasi: bir vaqtning o'zida <code>tomon</code> nomli <code>private</code> xususiyat e'lon qilinadi VA konstruktor parametridan qiymat olib, avtomatik ravishda <code>this.tomon</code>ga belgilanadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>public</code> — hamma joydan, <code>private</code> — faqat class ichida, <code>protected</code> — class va avlodlarida kirish mumkin</li>
<li>✅ <code>implements</code> — class interfeysdagi barcha xususiyat/metodlarni taqdim etishini majburiy qiladi</li>
<li>✅ <code>abstract class</code> — to'g'ridan-to'g'ri obyekt yaratib bo'lmaydigan, avlodlar uchun andoza class</li>
<li>✅ <code>private</code> xususiyatga tashqaridan murojaat qilish — kompilyatsiya xatosi beradi (inkapsulyatsiya)</li>
<li>✅ <code>constructor(private x: tur)</code> — xususiyat e'lon qilish va qiymat berishni bitta qatorda birlashtiradi</li>
</ul>
"""

L7_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 7: Class'lar va Access Modifiers
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) public, private, protected
// ─────────────────────────────────────────────────────────────────────

class BankHisobi {
  public egasi: string;
  private balans: number;
  protected hisobRaqami: string;

  constructor(egasi: string, boshlangichBalans: number, hisobRaqami: string) {
    this.egasi = egasi;
    this.balans = boshlangichBalans;
    this.hisobRaqami = hisobRaqami;
  }

  balansniKorish(): number {
    return this.balans;
  }
}

const hisob = new BankHisobi("Olim", 1000000, "UZ-001");
console.log(hisob.egasi);
console.log(hisob.balansniKorish());

// ─────────────────────────────────────────────────────────────────────
// 2) implements - interfeysni class orqali amalga oshirish
// ─────────────────────────────────────────────────────────────────────

interface Hayvon {
  ism: string;
  ovozChiqarish(): string;
}

class It implements Hayvon {
  ism: string;

  constructor(ism: string) {
    this.ism = ism;
  }

  ovozChiqarish(): string {
    return "Vov-vov!";
  }
}

const kuchuk = new It("Rex");
console.log(kuchuk.ovozChiqarish());

// ─────────────────────────────────────────────────────────────────────
// 3) abstract class
// ─────────────────────────────────────────────────────────────────────

abstract class Shakl {
  abstract yuzaniHisoblash(): number;

  malumotChiqarish(): string {
    return `Yuza: ${this.yuzaniHisoblash()}`;
  }
}

class Kvadrat extends Shakl {
  constructor(private tomon: number) {
    super();
  }
  yuzaniHisoblash(): number {
    return this.tomon * this.tomon;
  }
}

const kvadrat = new Kvadrat(5);
console.log(kvadrat.malumotChiqarish());

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - private xususiyatga tashqaridan kirish (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
class BankHisobiXato {
  private balans: number = 1000;
}
const hisobXato = new BankHisobiXato();
console.log(hisobXato.balans); // ❌ Property 'balans' is private
*/
"""

L7_EX = [
    {
        "title": "private xususiyatga qayerdan kirish mumkin?",
        "description": "private deb belgilangan xususiyatga qayerdan kirish mumkin?",
        "exercise_type": "multiple_choice",
        "options": ["Faqat shu class ichidan", "Hamma joydan", "Faqat avlod class'lardan", "Faqat boshqa fayldan"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bu — eng cheklangan kirish darajasi.",
        "explanation": "private xususiyat faqat shu xususiyat e'lon qilingan class ichida murojaat qilinishi mumkin, hatto avlod class'lardan ham emas.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "implements nima uchun ishlatiladi?",
        "description": "class X implements InterfeysY yozuvi nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "X class'i Y class'idan meros oladi",
            "X class'i InterfeysY'da belgilangan barcha xususiyat/metodlarni taqdim etishi shart",
            "X interfeysi Y class'iga aylanadi",
            "Hech qanday ma'no bermaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — interfeys va class orasidagi \"shartnoma\".",
        "explanation": "implements class'ning interfeysda belgilangan barcha xususiyat va metodlarni albatta taqdim etishini majburiy qiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Abstract class'dan foydalanish jarayonini tartiblang",
        "description": "abstract class Shakl va uning Kvadrat avlodini ishlatish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "abstract class Shakl abstract metod bilan e'lon qilinadi",
            "Kvadrat class'i Shakl'dan extends qiladi",
            "Kvadrat abstract metodni majburiy amalga oshiradi",
            "new Kvadrat(5) orqali obyekt yaratiladi (Shakl'dan to'g'ridan-to'g'ri emas)",
        ],
        "correct_order": [
            "abstract class Shakl abstract metod bilan e'lon qilinadi",
            "Kvadrat class'i Shakl'dan extends qiladi",
            "Kvadrat abstract metodni majburiy amalga oshiradi",
            "new Kvadrat(5) orqali obyekt yaratiladi (Shakl'dan to'g'ridan-to'g'ri emas)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Qaysi access modifier avlod class'larda ham kirish imkonini beradi?",
        "description": "Shu class VA undan meros olgan avlod class'larida (lekin tashqarida emas) kirish imkonini beruvchi access modifier qaysi? (bitta so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "protected",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega private xususiyatlar (inkapsulyatsiya) muhim?",
        "description": (
            "Agar BankHisobi class'idagi balans xususiyati private o'rniga "
            "public qilib belgilansa, bu qanday muammoga olib kelishi "
            "mumkin? private ishlatish bu muammoni qanday hal qiladi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar balans public bo'lsa, istalgan tashqi kod hisobga=hisob.balans "
            "orqali to'g'ridan-to'g'ri, hech qanday tekshiruvsiz istalgan "
            "qiymat (masalan manfiy son) yozishi mumkin bo'lib qoladi — bu "
            "bank hisobi kabi tizimda jiddiy xatolarga (masalan manfiy "
            "balansga) olib kelishi mumkin. balans'ni private qilib "
            "belgilash bu muammoni hal qiladi, chunki endi uni faqat "
            "class ichidagi metodlar (masalan pulQoshish yoki pulYechish "
            "kabi, ichida tekshiruv bo'lgan metodlar) orqaligina "
            "o'zgartirish mumkin bo'ladi — bu inkapsulyatsiya tamoyilining "
            "amaliy foydasi."
        ),
        "hint": "public bo'lsa, tashqi kod balansni qanday o'zgartirishi mumkin — tekshiruvsizmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L8_TEXT = """\
<h2>Enum va Literal Types — cheklangan qiymatlar to'plami</h2>

<pre class="mermaid">
flowchart LR
    ENUM["enum Holat { Kutilmoqda, Tasdiqlandi, Bekor }"] --> USE["Holat.Tasdiqlandi"]
    LIT["type O'lcham = 'kichik' | 'orta' | 'katta'"] --> USE2["Faqat shu 3 qiymatdan biri"]
</pre>

<p>Ba'zan o'zgaruvchi <strong>faqat oldindan belgilangan, cheklangan</strong> qiymatlardan birini olishi kerak — masalan, buyurtma holati faqat "kutilmoqda", "tasdiqlandi" yoki "bekor qilindi" bo'lishi mumkin, boshqa hech narsa emas. <strong>Enum</strong> va <strong>literal types</strong> — aynan shu maqsad uchun.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — string enum</h4>
<pre><code>enum BuyurtmaHolati {
  Kutilmoqda = "KUTILMOQDA",
  Tasdiqlandi = "TASDIQLANDI",
  BekorQilindi = "BEKOR_QILINDI",
}

function holatniKorsatish(holat: BuyurtmaHolati): string {
  return `Holat: ${holat}`;
}

console.log(holatniKorsatish(BuyurtmaHolati.Tasdiqlandi)); // "Holat: TASDIQLANDI"
// holatniKorsatish("boshqa-narsa"); // ❌ Xato: enum'dagi qiymatlardan biri emas</code></pre>

<h4>BLOKA 2 — literal types (aniq qiymatli turlar)</h4>
<pre><code>// Enum'siz ham xuddi shunday cheklov yaratish mumkin
type OlchamTuri = "kichik" | "o'rta" | "katta"; // ❗ FAQAT shu 3 ta matn qiymati

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  if (olcham === "o'rta") return 35000;
  return 50000;
}

console.log(narxHisoblash("o'rta")); // 35000
// narxHisoblash("gigant"); // ❌ Xato: 'gigant' OlchamTuri'ga mos kelmaydi</code></pre>

<h4>BLOKA 3 — numeric enum va const assertion</h4>
<pre><code>enum Yonalish {
  Yuqori,  // ❗ standart holda 0
  Past,    // 1
  Chap,    // 2
  Ong,     // 3
}

console.log(Yonalish.Chap); // 2

// const assertion — obyektni "faqat o'qish" va aniq literal qiymatlar bilan belgilash
const sozlamalar = {
  til: "uz",
  rejim: "qorong'i",
} as const; // ❗ endi til va rejim ANIQ shu qiymatlarga "qulflangan"

// sozlamalar.til = "ru"; // ❌ Xato: readonly, o'zgartirib bo'lmaydi</code></pre>

<h3>🐛 Ataylab xato — literal type'ga mos kelmaydigan matn yuborish</h3>
<pre><code>type OlchamTuri = "kichik" | "o'rta" | "katta";

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  return 50000;
}

narxHisoblash("O'RTA"); // ❌ Xato: katta-kichik harf farq qiladi, "O'RTA" ≠ "o'rta"!</code></pre>

<p><strong>Natija:</strong> literal type'lar <strong>aynan mos keladigan</strong> qiymatlarnigina qabul qiladi — katta-kichik harf farqi, bo'sh joy yoki boshqa har qanday farq TypeScript uchun "butunlay boshqa qiymat" hisoblanadi. <code>"o'rta"</code> va <code>"O'RTA"</code> — ikkita <strong>turli</strong> string literal, garchi inson ko'zi bilan "bir xil narsa" bo'lib tuyulsa ham. Bu — literal type'larning qat'iyligi va aynan shu qat'iylik xatolarni oldindan aniqlash imkonini beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Enum nima uchun kerak?</h4>
<p><code>enum</code> — cheklangan, nomlangan qiymatlar to'plamini belgilash imkonini beradi. Bu qiymatlarni kodning istalgan joyida <code>BuyurtmaHolati.Tasdiqlandi</code> kabi o'qilishi oson nom bilan ishlatish mumkin, xom matn ("TASDIQLANDI") yozish o'rniga.</p>

<h4>2. String enum va numeric enum farqi</h4>
<p>String enum'da har bir a'zoga aniq matn qiymati beriladi (masalan <code>"KUTILMOQDA"</code>). Numeric enum'da esa, agar qiymat berilmasa, TypeScript avtomatik 0'dan boshlab raqam beradi. String enum odatda tushunarli va debug qilish osonroq, shuning uchun ko'proq tavsiya etiladi.</p>

<h4>3. Literal types nima va ular enum'dan qanday farq qiladi?</h4>
<p><code>type O'lcham = "kichik" | "o'rta" | "katta"</code> — bu union type'ning maxsus holati bo'lib, o'zgaruvchi faqat shu aniq matn qiymatlaridan birini olishi mumkinligini bildiradi. Enum'dan farqli o'laroq, bu faqat kompilyatsiya vaqtidagi tur tekshiruvi — runtime'da alohida obyekt yaratilmaydi (kichikroq, "yengilroq" yechim).</p>

<h4>4. <code>as const</code> (const assertion) nima qiladi?</h4>
<p>Odatda obyekt xususiyatlari o'zgaruvchan turlar (masalan <code>string</code>) deb hisoblanadi. <code>as const</code> qo'shilsa, TypeScript har bir xususiyatni <strong>aniq shu qiymat</strong> (literal) va <code>readonly</code> deb belgilaydi — bu sozlamalar yoki konstantalar uchun juda foydali.</p>

<h4>5. Literal type'lar nega katta-kichik harfga sezgir?</h4>
<p>TypeScript string literal'larni <strong>aniq matn</strong> sifatida solishtiradi, inson tilidagi "ma'no" emas. Shuning uchun <code>"o'rta"</code> va <code>"O'RTA"</code> — ikki butunlay boshqa qiymat hisoblanadi, va faqat aniq belgilangan variantlardan biri qabul qilinadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>enum</code> — cheklangan, nomlangan qiymatlar to'plamini belgilaydi (string yoki numeric)</li>
<li>✅ Literal types (<code>"a" | "b" | "c"</code>) — enum'ga muqobil, yengilroq yechim</li>
<li>✅ <code>as const</code> — obyekt xususiyatlarini aniq literal qiymat va readonly qilib "qulflaydi"</li>
<li>✅ Literal type'lar katta-kichik harfga sezgir — aniq mos kelishi shart</li>
<li>✅ Enum va literal types — funksiyaga faqat oldindan belgilangan qiymatlarni qabul qildirish uchun ishlatiladi</li>
</ul>
"""

L8_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 8: Enum va Literal Types
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) String enum
// ─────────────────────────────────────────────────────────────────────

enum BuyurtmaHolati {
  Kutilmoqda = "KUTILMOQDA",
  Tasdiqlandi = "TASDIQLANDI",
  BekorQilindi = "BEKOR_QILINDI",
}

function holatniKorsatish(holat: BuyurtmaHolati): string {
  return `Holat: ${holat}`;
}

console.log(holatniKorsatish(BuyurtmaHolati.Tasdiqlandi));

// ─────────────────────────────────────────────────────────────────────
// 2) Literal types
// ─────────────────────────────────────────────────────────────────────

type OlchamTuri = "kichik" | "o'rta" | "katta";

function narxHisoblash(olcham: OlchamTuri): number {
  if (olcham === "kichik") return 20000;
  if (olcham === "o'rta") return 35000;
  return 50000;
}

console.log(narxHisoblash("o'rta"));

// ─────────────────────────────────────────────────────────────────────
// 3) Numeric enum
// ─────────────────────────────────────────────────────────────────────

enum Yonalish {
  Yuqori,
  Past,
  Chap,
  Ong,
}

console.log(Yonalish.Chap);

// ─────────────────────────────────────────────────────────────────────
// 4) const assertion
// ─────────────────────────────────────────────────────────────────────

const sozlamalar = {
  til: "uz",
  rejim: "qorong'i",
} as const;

// ─────────────────────────────────────────────────────────────────────
// 5) Ataylab xato - katta-kichik harf mos kelmasligi (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
narxHisoblash("O'RTA"); // ❌ Xato: "o'rta" bilan "O'RTA" bir xil emas!
*/
"""

L8_EX = [
    {
        "title": "Enum nima uchun ishlatiladi?",
        "description": "TypeScript'da enum asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Cheksiz qiymatlar to'plamini belgilash uchun",
            "Cheklangan, nomlangan qiymatlar to'plamini belgilash uchun",
            "Faqat sonlarni saqlash uchun",
            "Massivni saralash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Buyurtma holati kabi, faqat ma'lum variantlardan biri bo'lishi mumkin.",
        "explanation": "enum cheklangan, nomlangan qiymatlar to'plamini belgilaydi va ularni o'qilishi oson nom bilan ishlatish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Literal type qanday yoziladi?",
        "description": "Faqat \"kichik\", \"o'rta\", \"katta\" qiymatlaridan birini qabul qiluvchi tur qanday yoziladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "type O'lcham = \"kichik\" & \"o'rta\" & \"katta\"",
            "type O'lcham = \"kichik\" | \"o'rta\" | \"katta\"",
            "type O'lcham = [\"kichik\", \"o'rta\", \"katta\"]",
            "type O'lcham = string",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — union type'ning maxsus holati.",
        "explanation": "Literal types union sintaksisi (|) bilan yoziladi: har bir aniq qiymat '|' orqali ajratiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "as const ta'sirini tartiblang",
        "description": "as const qo'llanilganda obyektga bo'ladigan o'zgarishlarni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Obyekt {til: \"uz\"} kabi oddiy tur bilan yaratiladi",
            "as const qo'shiladi",
            "Har bir xususiyat aniq literal qiymat va readonly deb belgilanadi",
            "Xususiyatni o'zgartirishga urinish endi xato beradi",
        ],
        "correct_order": [
            "Obyekt {til: \"uz\"} kabi oddiy tur bilan yaratiladi",
            "as const qo'shiladi",
            "Har bir xususiyat aniq literal qiymat va readonly deb belgilanadi",
            "Xususiyatni o'zgartirishga urinish endi xato beradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Numeric enum'da standart qiymat qayerdan boshlanadi?",
        "description": "Qiymat berilmagan numeric enum'da birinchi a'zo qanday songa teng bo'ladi? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "0",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Literal type nega katta-kichik harfga sezgir?",
        "description": (
            "type OlchamTuri = \"kichik\" | \"o'rta\" | \"katta\" deb "
            "belgilangan holda, narxHisoblash(\"O'RTA\") chaqiruvi nega "
            "xato beradi, garchi \"o'rta\" ro'yxatda bo'lsa ham? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "TypeScript string literal turlarni aniq matn ketma-ketligi "
            "sifatida solishtiradi, inson uchun \"bir xil ma'noli\" "
            "so'zlar sifatida emas. \"o'rta\" va \"O'RTA\" — katta-kichik "
            "harflari farqli bo'lgani uchun, kompyuter nuqtai nazaridan "
            "ular ikkita butunlay boshqa qiymat hisoblanadi. OlchamTuri "
            "turi faqat aynan \"kichik\", \"o'rta\", \"katta\" (kichik "
            "harflar bilan, aynan shu yozilishda) qiymatlarni qabul "
            "qiladi, shuning uchun \"O'RTA\" bu ro'yxatga kiritilmagan "
            "deb hisoblanadi va TypeScript kompilyatsiya xatosini beradi."
        ),
        "hint": "Kompyuter uchun matnlarni solishtirish — aynan bir xil belgilarni talab qiladi.",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L9_TEXT = """\
<h2>Utility Types — tayyor tur transformatorlari</h2>

<pre class="mermaid">
flowchart LR
    IFACE["interface Foydalanuvchi"] --> PARTIAL["Partial&lt;Foydalanuvchi&gt; — barcha maydon ixtiyoriy"]
    IFACE --> PICK["Pick&lt;Foydalanuvchi, 'ism'&gt; — faqat tanlangan maydonlar"]
    IFACE --> OMIT["Omit&lt;Foydalanuvchi, 'parol'&gt; — ba'zi maydonlar chiqarib tashlanadi"]
    IFACE --> READONLY["Readonly&lt;Foydalanuvchi&gt; — barcha maydon o'zgarmas"]
</pre>

<p>Ko'p hollarda bizga mavjud <code>interface</code>'ning "biroz o'zgartirilgan" versiyasi kerak bo'ladi — masalan, yangilash formasi uchun barcha maydonlar ixtiyoriy bo'lsin, yoki parolsiz foydalanuvchi ma'lumoti kerak bo'lsin. Har safar yangi interfeys yozish o'rniga, TypeScript <strong>utility types</strong> deb ataladigan tayyor "tur transformatorlari"ni taqdim etadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Partial va Readonly</h4>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

// Partial<T> — barcha maydonlarni ixtiyoriy qiladi
function foydalanuvchiniYangilash(id: number, ozgarishlar: Partial<Foydalanuvchi>): void {
  console.log(`Foydalanuvchi ${id} yangilanmoqda:`, ozgarishlar);
}

foydalanuvchiniYangilash(1, { ism: "Yangi Ism" }); // ✅ faqat 1 ta maydon yetarli

// Readonly<T> — barcha maydonlarni o'zgarmas (readonly) qiladi
const sobitFoydalanuvchi: Readonly<Foydalanuvchi> = { id: 1, ism: "Olim", email: "olim@mail.uz" };
// sobitFoydalanuvchi.ism = "Boshqa"; // ❌ Xato: readonly, o'zgartirib bo'lmaydi</code></pre>

<h4>BLOKA 2 — Pick va Omit</h4>
<pre><code>// Pick<T, Keys> — faqat ko'rsatilgan maydonlarni oladi
type FoydalanuvchiIsmi = Pick<Foydalanuvchi, "id" | "ism">;
// natija: { id: number; ism: string; } — email YO'Q

const qisqaMalumot: FoydalanuvchiIsmi = { id: 1, ism: "Olim" };

// Omit<T, Keys> — ko'rsatilgan maydonlarni CHIQARIB TASHLAYDI, qolganini oladi
type FoydalanuvchiParolsiz = Omit<Foydalanuvchi, "email">;
// natija: { id: number; ism: string; } — email chiqarib tashlangan

const xavfsizMalumot: FoydalanuvchiParolsiz = { id: 1, ism: "Olim" };</code></pre>

<h4>BLOKA 3 — Record</h4>
<pre><code>// Record<Keys, ValueType> — barcha kalitlari Keys, qiymatlari ValueType bo'lgan obyekt turi
type ViloyatAholisi = Record<string, number>; // ❗ kalit — string, qiymat — number

const aholi: ViloyatAholisi = {
  Toshkent: 2900000,
  Samarqand: 550000,
};

// Kalitlarni ham cheklash mumkin (literal type bilan)
type RangKodlari = Record<"qizil" | "yashil" | "kok", string>;
const ranglar: RangKodlari = {
  qizil: "#FF0000",
  yashil: "#00FF00",
  kok: "#0000FF",
};</code></pre>

<h3>🐛 Ataylab xato — Pick'da mavjud bo'lmagan maydon nomini yozish</h3>
<pre><code>interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

type Xato = Pick<Foydalanuvchi, "id" | "familiya">;
// ❌ Xato: Property 'familiya' does not exist on type 'Foydalanuvchi'.</code></pre>

<p><strong>Natija:</strong> <code>Pick</code> (va <code>Omit</code>) ikkinchi generic parametrida <strong>faqat</strong> asl interfeysda haqiqatan mavjud bo'lgan maydon nomlarini qabul qiladi. <code>Foydalanuvchi</code> interfeysida <code>familiya</code> degan maydon yo'q, shuning uchun TypeScript darhol kompilyatsiya xatosini beradi — bu yozuvdagi xatolarni (typo) yoki noto'g'ri taxminlarni erta aniqlash imkonini beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Utility types nima uchun kerak?</h4>
<p>Ular mavjud tur (masalan <code>interface</code>)dan <strong>yangi tur yasash</strong> imkonini beradi, uni qaytadan qo'lda yozmasdan. Bu kodni takrorlashning oldini oladi va asl interfeys o'zgarganda hosila turlar ham avtomatik yangilanadi.</p>

<h4>2. Partial va Readonly farqi</h4>
<p><code>Partial&lt;T&gt;</code> barcha maydonlarni <strong>ixtiyoriy</strong> qiladi (<code>?</code> qo'shadi) — odatda yangilash (update) funksiyalarida ishlatiladi. <code>Readonly&lt;T&gt;</code> esa barcha maydonlarni <strong>o'zgarmas</strong> qiladi — obyektni yaratilgandan keyin o'zgartirib bo'lmaydi.</p>

<h4>3. Pick va Omit — bir-biriga qarama-qarshi</h4>
<p><code>Pick&lt;T, Keys&gt;</code> faqat ko'rsatilgan maydonlarni <strong>oladi</strong> (qolganini tashlaydi). <code>Omit&lt;T, Keys&gt;</code> esa ko'rsatilgan maydonlarni <strong>chiqarib tashlaydi</strong> (qolganini oladi). Ikkalasi ham bir xil maqsadga ikki xil yo'ldan erishadi.</p>

<h4>4. Record qachon ishlatiladi?</h4>
<p><code>Record&lt;Keys, ValueType&gt;</code> "kalit-qiymat" (key-value) shaklidagi obyektlar uchun ishlatiladi — masalan viloyat nomidan aholi soniga, yoki rang nomidan kod qiymatiga xarita (map) kabi tuzilmalar uchun juda qulay.</p>

<h4>5. Nega Pick'da mavjud bo'lmagan maydon xato beradi?</h4>
<p>TypeScript utility types'ni <strong>generic</strong> sifatida amalga oshiradi — <code>Pick&lt;T, K&gt;</code>'dagi <code>K</code> albatta <code>T</code>'ning haqiqiy maydon nomlaridan biri bo'lishi <strong>shart</strong> (bu <code>keyof T</code> constraint orqali ta'minlanadi). Mavjud bo'lmagan nom yozilsa, bu shartga mos kelmaydi va xato beriladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>Partial&lt;T&gt;</code> — barcha maydonlarni ixtiyoriy qiladi</li>
<li>✅ <code>Readonly&lt;T&gt;</code> — barcha maydonlarni o'zgarmas qiladi</li>
<li>✅ <code>Pick&lt;T, Keys&gt;</code> — faqat ko'rsatilgan maydonlarni oladi</li>
<li>✅ <code>Omit&lt;T, Keys&gt;</code> — ko'rsatilgan maydonlarni chiqarib tashlaydi</li>
<li>✅ <code>Record&lt;Keys, ValueType&gt;</code> — "kalit-qiymat" shaklidagi obyekt turi yaratadi</li>
</ul>
"""

L9_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 9: Utility Types
// ════════════════════════════════════════════════════════════════════

interface Foydalanuvchi {
  id: number;
  ism: string;
  email: string;
}

// ─────────────────────────────────────────────────────────────────────
// 1) Partial va Readonly
// ─────────────────────────────────────────────────────────────────────

function foydalanuvchiniYangilash(id: number, ozgarishlar: Partial<Foydalanuvchi>): void {
  console.log(`Foydalanuvchi ${id} yangilanmoqda:`, ozgarishlar);
}

foydalanuvchiniYangilash(1, { ism: "Yangi Ism" });

const sobitFoydalanuvchi: Readonly<Foydalanuvchi> = { id: 1, ism: "Olim", email: "olim@mail.uz" };

// ─────────────────────────────────────────────────────────────────────
// 2) Pick va Omit
// ─────────────────────────────────────────────────────────────────────

type FoydalanuvchiIsmi = Pick<Foydalanuvchi, "id" | "ism">;
const qisqaMalumot: FoydalanuvchiIsmi = { id: 1, ism: "Olim" };

type FoydalanuvchiParolsiz = Omit<Foydalanuvchi, "email">;
const xavfsizMalumot: FoydalanuvchiParolsiz = { id: 1, ism: "Olim" };

// ─────────────────────────────────────────────────────────────────────
// 3) Record
// ─────────────────────────────────────────────────────────────────────

type ViloyatAholisi = Record<string, number>;

const aholi: ViloyatAholisi = {
  Toshkent: 2900000,
  Samarqand: 550000,
};

type RangKodlari = Record<"qizil" | "yashil" | "kok", string>;
const ranglar: RangKodlari = {
  qizil: "#FF0000",
  yashil: "#00FF00",
  kok: "#0000FF",
};

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - Pick'da mavjud bo'lmagan maydon (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
type Xato = Pick<Foydalanuvchi, "id" | "familiya">;
// ❌ Property 'familiya' does not exist on type 'Foydalanuvchi'.
*/
"""

L9_EX = [
    {
        "title": "Partial<T> nima qiladi?",
        "description": "Partial<Foydalanuvchi> turi asl interfeysga nisbatan nimani o'zgartiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Barcha maydonlarni o'chirib tashlaydi",
            "Barcha maydonlarni ixtiyoriy (optional) qiladi",
            "Barcha maydonlarni o'zgarmas (readonly) qiladi",
            "Yangi maydon qo'shadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Yangilash (update) funksiyalarida ko'p ishlatiladi.",
        "explanation": "Partial<T> asl interfeysning barcha maydonlarini ixtiyoriy qiladi — har biriga '?' qo'shilgandek bo'ladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Pick va Omit orasidagi farq",
        "description": "Pick<T, Keys> va Omit<T, Keys> orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkalasi ham bir xil ishlaydi",
            "Pick faqat ko'rsatilgan maydonlarni oladi, Omit ularni chiqarib tashlaydi",
            "Pick faqat massivlar uchun, Omit faqat obyektlar uchun",
            "Omit yangi maydon qo'shadi, Pick maydonni o'chiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ular bir-biriga qarama-qarshi maqsadga xizmat qiladi.",
        "explanation": "Pick<T, Keys> faqat ko'rsatilgan maydonlarni oladi (qolganini tashlaydi), Omit<T, Keys> esa ko'rsatilgan maydonlarni chiqarib tashlaydi (qolganini oladi).",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Record turi yaratish jarayonini tartiblang",
        "description": "type ViloyatAholisi = Record<string, number> turi yaratilib ishlatilish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Record<string, number> deb tur belgilanadi",
            "Kalitlari string, qiymatlari number bo'lgan obyekt turi hosil bo'ladi",
            "const aholi: ViloyatAholisi = { Toshkent: 2900000 } deb obyekt yaratiladi",
            "TypeScript har bir kalit-qiymat juftligini tekshiradi",
        ],
        "correct_order": [
            "Record<string, number> deb tur belgilanadi",
            "Kalitlari string, qiymatlari number bo'lgan obyekt turi hosil bo'ladi",
            "const aholi: ViloyatAholisi = { Toshkent: 2900000 } deb obyekt yaratiladi",
            "TypeScript har bir kalit-qiymat juftligini tekshiradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Barcha maydonlarni o'zgarmas qiluvchi utility type",
        "description": "Qaysi utility type interfeysning barcha maydonlarini o'zgarmas (readonly) qiladi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "Readonly",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Pick'da mavjud bo'lmagan maydon nomi xato beradi?",
        "description": (
            "interface Foydalanuvchi { id: number; ism: string; email: "
            "string; } deb belgilangan holda, "
            "Pick<Foydalanuvchi, \"id\" | \"familiya\"> yozilsa, nega "
            "TypeScript xato beradi, garchi familiya - odatiy so'z bo'lsa "
            "ham? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Pick<T, Keys> generic sifatida amalga oshirilgan bo'lib, "
            "ikkinchi parametr (Keys) albatta T interfeysida haqiqatan "
            "mavjud bo'lgan maydon nomlaridan (keyof T) biri bo'lishi "
            "shart. Foydalanuvchi interfeysida familiya degan maydon "
            "umuman e'lon qilinmagan, shuning uchun \"familiya\" bu "
            "cheklovga (constraint) mos kelmaydi va TypeScript "
            "kompilyatsiya vaqtida xato beradi. Bu himoya yozuvdagi "
            "xatolarni (masalan familiya o'rniga familya deb yozib "
            "qo'yishni) darhol aniqlash imkonini beradi."
        ),
        "hint": "Pick ichidagi Keys parametri qanday cheklovga bo'ysunadi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L10_TEXT = """\
<h2>CAPSTONE — to'liq tiplashtirilgan Vazifalar Repozitoriyasi</h2>

<pre class="mermaid">
flowchart TB
    IFACE["interface Vazifa"] --> DTO1["Omit&lt;Vazifa,'id'&gt; — yaratish uchun"]
    IFACE --> DTO2["Partial&lt;Omit&lt;Vazifa,'id'&gt;&gt; — yangilash uchun"]
    GEN["interface Repozitoriy&lt;T&gt;"] -->|implements| REPO["class VazifaRepozitoriyi"]
    REPO --> CRUD["hamma() / topish() / qoshish() / yangilash() / ochirish()"]
</pre>

<p>8 ta darsda o'rgangan hamma narsani &mdash; <code>interface</code>, funksiyalarni tiplashtirish, union/generics, class'lar, enum va utility types &mdash; birlashtirib, haqiqiy kichik loyiha quramiz: <strong>tiplashtirilgan Vazifalar (Task) Repozitoriyasi</strong>. Bu — kursning yakuniy sinovi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — asosiy interfeys va undan hosil qilingan DTO turlari</h4>
<pre><code>interface Vazifa {
  id: number;
  sarlavha: string;
  holat: "kutilmoqda" | "bajarilmoqda" | "tugallandi"; // ❗ literal type (5-dars)
  muhimlik: number;
}

// Yaratish uchun - id kerak emas (avtomatik beriladi)
type VazifaYaratishDTO = Omit<Vazifa, "id">; // ❗ Omit (9-dars)

// Yangilash uchun - id o'zgarmaydi, qolgan HAMMA maydon ixtiyoriy
type VazifaYangilashDTO = Partial<Omit<Vazifa, "id">>; // ❗ Partial + Omit birgalikda</code></pre>

<h4>BLOKA 2 — generic Repozitoriy interfeysi va uni class orqali amalga oshirish</h4>
<pre><code>interface Repozitoriy<T extends { id: number }> { // ❗ generic constraint (6-dars)
  hamma(): T[];
  topish(id: number): T | undefined;
  qoshish(item: Omit<T, "id">): T;
  yangilash(id: number, ozgarishlar: Partial<Omit<T, "id">>): T | undefined;
  ochirish(id: number): boolean;
}

class VazifaRepozitoriyi implements Repozitoriy<Vazifa> { // ❗ implements (7-dars)
  private vazifalar: Vazifa[] = []; // ❗ private (7-dars)
  private keyingiId = 1;

  hamma(): Vazifa[] {
    return this.vazifalar;
  }

  topish(id: number): Vazifa | undefined {
    return this.vazifalar.find((v) => v.id === id);
  }

  qoshish(item: Omit<Vazifa, "id">): Vazifa {
    const yangi: Vazifa = { id: this.keyingiId++, ...item };
    this.vazifalar.push(yangi);
    return yangi;
  }

  yangilash(id: number, ozgarishlar: Partial<Omit<Vazifa, "id">>): Vazifa | undefined {
    const vazifa = this.topish(id);
    if (!vazifa) return undefined;
    Object.assign(vazifa, ozgarishlar);
    return vazifa;
  }

  ochirish(id: number): boolean {
    const boshlangichUzunlik = this.vazifalar.length;
    this.vazifalar = this.vazifalar.filter((v) => v.id !== id);
    return this.vazifalar.length < boshlangichUzunlik;
  }
}</code></pre>

<h4>BLOKA 3 — repozitoriyadan foydalanish</h4>
<pre><code>const repo = new VazifaRepozitoriyi();

const vazifa1 = repo.qoshish({ sarlavha: "TypeScript o'rganish", holat: "bajarilmoqda", muhimlik: 5 });
const vazifa2 = repo.qoshish({ sarlavha: "Loyihani topshirish", holat: "kutilmoqda", muhimlik: 4 });

console.log(repo.hamma().length); // 2

repo.yangilash(vazifa1.id, { holat: "tugallandi" }); // ✅ faqat 'holat' maydonini yangilaydi
console.log(repo.topish(vazifa1.id)?.holat); // "tugallandi"

console.log(repo.ochirish(vazifa2.id)); // true
console.log(repo.hamma().length); // 1</code></pre>

<h3>🐛 Ataylab xato — DTO turida id maydonini ham yuborish</h3>
<pre><code>const yangiVazifa: VazifaYaratishDTO = {
  id: 99, // ❌ Xato: Object literal may only specify known properties,
          //         va 'id' VazifaYaratishDTO (Omit<Vazifa, "id">) da yo'q
  sarlavha: "Test",
  holat: "kutilmoqda",
  muhimlik: 1,
};</code></pre>

<p><strong>Natija:</strong> <code>VazifaYaratishDTO</code> turi <code>Omit&lt;Vazifa, "id"&gt;</code> orqali hosil qilingani uchun, unda <code>id</code> maydoni <strong>umuman yo'q</strong>. Shuning uchun bu turdagi obyektga <code>id</code> qiymatini qo'shishga urinish TypeScript tomonidan xato deb hisoblanadi — bu aynan Omit'ning maqsadi: yaratish bosqichida foydalanuvchi (yoki dasturchi) tasodifan o'zi ID belgilab qo'yishining oldini olish (chunki ID'ni odatda repozitoriy o'zi avtomatik beradi).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega VazifaYaratishDTO uchun alohida tur kerak?</h4>
<p>Yangi vazifa yaratishda foydalanuvchi <code>id</code>'ni bermaydi — uni repozitoriy o'zi avtomatik beradi (<code>keyingiId++</code>). <code>Omit&lt;Vazifa, "id"&gt;</code> aynan shu holatni ifodalaydi: "Vazifa'ning barcha maydonlari, <code>id</code>'dan tashqari".</p>

<h4>2. Nega yangilashda Partial VA Omit birga ishlatiladi?</h4>
<p>Yangilashda: (1) <code>id</code>'ni umuman o'zgartirib bo'lmaydi (<code>Omit</code>), va (2) qolgan maydonlarning HAR BIRI ixtiyoriy bo'lishi kerak, chunki foydalanuvchi faqat bitta maydonni (masalan <code>holat</code>ni) yangilashi mumkin (<code>Partial</code>). Ikkalasini birlashtirish aynan shu ikki talabni bir vaqtda qanoatlantiradi.</p>

<h4>3. Repozitoriy&lt;T&gt; nega generic constraint (<code>extends { id: number }</code>) talab qiladi?</h4>
<p>Repozitoriyning ichki metodlari (<code>topish</code>, <code>ochirish</code>) <code>id</code> maydoniga tayanib ishlaydi. Agar <code>T</code> uchun hech qanday cheklov qo'yilmasa, TypeScript <code>T</code>'da <code>id</code> maydoni borligiga kafolat bera olmaydi. <code>extends { id: number }</code> shu kafolatni beradi.</p>

<h4>4. Nega class private xususiyat (<code>vazifalar</code>) ishlatadi?</h4>
<p>Agar <code>vazifalar</code> massivi <code>public</code> bo'lganida, tashqi kod uni to'g'ridan-to'g'ri, hech qanday tekshiruvsiz o'zgartirib yuborishi mumkin edi (masalan, ID'siz vazifa qo'shish). <code>private</code> qilib, faqat <code>qoshish</code>/<code>yangilash</code>/<code>ochirish</code> metodlari orqaligina o'zgartirish mumkin &mdash; bu inkapsulyatsiya.</p>

<h4>5. Bu loyiha 8 ta darsdan qaysi tushunchalarni birlashtiradi?</h4>
<p><code>interface</code> (3-dars), literal types (8-dars), generics va constraint (6-dars), class va <code>implements</code>/<code>private</code> (7-dars), utility types <code>Omit</code>/<code>Partial</code> (9-dars) — barchasi bitta kichik, ammo haqiqiy loyihada birgalikda ishlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Real loyihalarda <code>interface</code>dan <code>Omit</code>/<code>Partial</code> orqali DTO turlari qanday hosil qilinadi</li>
<li>✅ Generic <code>Repozitoriy&lt;T extends { id: number }&gt;</code> qanday va nega ishlatiladi</li>
<li>✅ <code>class ... implements Repozitoriy&lt;Vazifa&gt;</code> generic interfeysni class orqali qanday amalga oshiradi</li>
<li>✅ <code>private</code> xususiyat inkapsulyatsiyani qanday ta'minlaydi</li>
<li>✅ 8 ta darsning barcha asosiy tushunchalari bitta loyihada qanday birlashishini</li>
</ul>
"""

L10_CODE = """\
// ════════════════════════════════════════════════════════════════════
// DARS 10 (CAPSTONE): To'liq tiplashtirilgan Vazifalar Repozitoriyasi
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) Asosiy interfeys va DTO turlari
// ─────────────────────────────────────────────────────────────────────

interface Vazifa {
  id: number;
  sarlavha: string;
  holat: "kutilmoqda" | "bajarilmoqda" | "tugallandi";
  muhimlik: number;
}

type VazifaYaratishDTO = Omit<Vazifa, "id">;
type VazifaYangilashDTO = Partial<Omit<Vazifa, "id">>;

// ─────────────────────────────────────────────────────────────────────
// 2) Generic Repozitoriy interfeysi va class orqali amalga oshirish
// ─────────────────────────────────────────────────────────────────────

interface Repozitoriy<T extends { id: number }> {
  hamma(): T[];
  topish(id: number): T | undefined;
  qoshish(item: Omit<T, "id">): T;
  yangilash(id: number, ozgarishlar: Partial<Omit<T, "id">>): T | undefined;
  ochirish(id: number): boolean;
}

class VazifaRepozitoriyi implements Repozitoriy<Vazifa> {
  private vazifalar: Vazifa[] = [];
  private keyingiId = 1;

  hamma(): Vazifa[] {
    return this.vazifalar;
  }

  topish(id: number): Vazifa | undefined {
    return this.vazifalar.find((v) => v.id === id);
  }

  qoshish(item: Omit<Vazifa, "id">): Vazifa {
    const yangi: Vazifa = { id: this.keyingiId++, ...item };
    this.vazifalar.push(yangi);
    return yangi;
  }

  yangilash(id: number, ozgarishlar: Partial<Omit<Vazifa, "id">>): Vazifa | undefined {
    const vazifa = this.topish(id);
    if (!vazifa) return undefined;
    Object.assign(vazifa, ozgarishlar);
    return vazifa;
  }

  ochirish(id: number): boolean {
    const boshlangichUzunlik = this.vazifalar.length;
    this.vazifalar = this.vazifalar.filter((v) => v.id !== id);
    return this.vazifalar.length < boshlangichUzunlik;
  }
}

// ─────────────────────────────────────────────────────────────────────
// 3) Foydalanish
// ─────────────────────────────────────────────────────────────────────

const repo = new VazifaRepozitoriyi();

const vazifa1 = repo.qoshish({ sarlavha: "TypeScript o'rganish", holat: "bajarilmoqda", muhimlik: 5 });
const vazifa2 = repo.qoshish({ sarlavha: "Loyihani topshirish", holat: "kutilmoqda", muhimlik: 4 });

console.log(repo.hamma().length);

repo.yangilash(vazifa1.id, { holat: "tugallandi" });
console.log(repo.topish(vazifa1.id)?.holat);

console.log(repo.ochirish(vazifa2.id));
console.log(repo.hamma().length);

// ─────────────────────────────────────────────────────────────────────
// 4) Ataylab xato - DTO'da id yuborish (izohda)
// ─────────────────────────────────────────────────────────────────────

/*
const yangiVazifa: VazifaYaratishDTO = {
  id: 99, // ❌ 'id' VazifaYaratishDTO'da yo'q
  sarlavha: "Test",
  holat: "kutilmoqda",
  muhimlik: 1,
};
*/
"""

L10_EX = [
    {
        "title": "VazifaYaratishDTO nega Omit orqali yasaladi?",
        "description": "type VazifaYaratishDTO = Omit<Vazifa, \"id\"> nega aynan shunday yasalgan?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki id maydoni umuman kerak emas",
            "Chunki yaratishda id'ni foydalanuvchi bermaydi, uni repozitoriy o'zi avtomatik beradi",
            "Chunki Omit tasodifan tanlangan, Pick ham bo'lardi",
            "Chunki Vazifa interfeysida id yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Yangi vazifa qo'shilganda ID qayerdan keladi?",
        "explanation": "Yaratishda id'ni repozitoriyning o'zi (keyingiId++) avtomatik beradi, shuning uchun DTO turida id maydoni umuman bo'lmasligi kerak — buni Omit<Vazifa, \"id\"> ta'minlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Yangilashda Partial va Omit birga ishlatilishi",
        "description": "Nega VazifaYangilashDTO = Partial<Omit<Vazifa, \"id\">> deb, ikkalasi BIRGA ishlatilgan?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat kod chiroyliroq ko'rinishi uchun",
            "Omit id'ni chiqarib tashlaydi, Partial esa qolgan maydonlarni ixtiyoriy qiladi — ikkalasi ham kerak",
            "Partial va Omit aslida bir xil ishlaydi",
            "TypeScript talab qiladi, boshqa yo'l yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Yangilashda ikkita talab bor: id o'zgarmasin, qolgani ixtiyoriy bo'lsin.",
        "explanation": "Omit<Vazifa, \"id\"> id'ni chiqarib tashlaydi (o'zgartirib bo'lmasligi uchun), Partial esa qolgan barcha maydonlarni ixtiyoriy qiladi (faqat kerakli maydonni yangilash uchun).",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "VazifaRepozitoriyi.qoshish() ishlash jarayonini tartiblang",
        "description": "repo.qoshish({ sarlavha: ..., holat: ..., muhimlik: ... }) chaqirilganda ichki jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "qoshish(item: Omit<Vazifa, 'id'>) chaqiriladi",
            "yangi obyekt { id: this.keyingiId++, ...item } shaklida yaratiladi",
            "yangi obyekt this.vazifalar massiviga qo'shiladi",
            "yaratilgan to'liq Vazifa obyekti qaytariladi",
        ],
        "correct_order": [
            "qoshish(item: Omit<Vazifa, 'id'>) chaqiriladi",
            "yangi obyekt { id: this.keyingiId++, ...item } shaklida yaratiladi",
            "yangi obyekt this.vazifalar massiviga qo'shiladi",
            "yaratilgan to'liq Vazifa obyekti qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Repozitoriy<T> generic constraint yozuvi",
        "description": "interface Repozitoriy<T extends { id: number }> yozuvida qaysi qism generic constraint hisoblanadi? (aynan shu qismni yozing, masalan: extends { id: number })",
        "exercise_type": "text_input",
        "expected_answer": "extends { id: number }",
        "hint": "6-darsda o'rgangan constraint sintaksisini eslang.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega vazifalar xususiyati private qilingan?",
        "description": (
            "class VazifaRepozitoriyi ichida private vazifalar: Vazifa[] "
            "= [] deb belgilangan. Agar bu xususiyat public bo'lganida, "
            "qanday muammo yuzaga kelishi mumkin edi? private buni "
            "qanday hal qiladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar vazifalar xususiyati public bo'lganida, tashqi kod uni "
            "to'g'ridan-to'g'ri, hech qanday tekshiruvsiz o'zgartirib "
            "yuborishi mumkin edi — masalan, ID'siz yoki noto'g'ri "
            "holatdagi vazifa massivga to'g'ridan-to'g'ri qo'shilib "
            "qolishi mumkin edi, bu esa repozitoriyning ichki holatini "
            "buzardi. vazifalar'ni private qilish bu muammoni hal "
            "qiladi, chunki endi uni faqat class ichidagi metodlar "
            "(qoshish, yangilash, ochirish) orqaligina, ya'ni "
            "repozitoriyning o'zi belgilagan qoidalar asosidagina "
            "o'zgartirish mumkin — bu inkapsulyatsiya printsipining "
            "amaliy foydasi."
        ),
        "hint": "Public xususiyatga tashqi kod qanday cheklovsiz ta'sir qilishi mumkin?",
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
                    [{"filename": f"misol.ts", "language": lang, "code": code}],
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
