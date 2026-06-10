"""Seed the "Javascript" beginner course (15 lessons + ~80 exercises).

This file was generated from the existing DB content (course id=22) and
then augmented with hero Mermaid diagrams, a project task for L0, six
proper exercises for L4 (was 1), and a fix for L14's broken title.

Usage:
    cd backend
    python scripts/seed_javascript_course.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.
For updating an EXISTING course in-place (preserving student progress) use
refresh_javascript_text.py instead.
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
    "title": "Javascript",
    "description": "JavaScript nima? (Saytning \"Miyasi\" va \"Muskullari\")\nJavaScript — bu veb-sahifalarni interaktiv, jonli va harakatlanuvchi qilish uchun ishlatiladigan dasturlash tilidir. Agar HTML va CSS saytning tashqi ko'rinishini yaratsa, JavaScript unga \"jon\" beradi.",
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 4,
    "max_points": 100,
    "is_active": True,
    "is_published": True,
}


L0_TEXT = """\
<pre class="mermaid">
flowchart TB
    L["let yosh = 25"] -->|mutable| OK["yosh = 26 OK"]
    C["const pi = 3.14"] -->|immutable| ERR["pi = 5 TypeError"]
    V["var ism = Ali"] -->|legacy| OLD["eski usul"]
    L -.->|block scope| BS["faqat block ichida"]
    C -.->|block scope| BS
    V -.->|function scope| FS["funksiya ichida"]
</pre>

<h3 data-path-to-node="2">O'zgaruvchilar (Ma'lumot saqlash qutilari)</h3><ul data-path-to-node="3"><li><p data-path-to-node="3,0,0"><b data-path-to-node="3,0,0" data-index-in-node="0">let</b> — Ma'lumotlarni saqlash uchun mo'ljallangan zamonaviy kalit so'z. Unda saqlangan ma'lumotni keyinchalik dastur davomida istalgancha o'zgartirish mumkin.</p></li><li><p data-path-to-node="3,1,0"><b data-path-to-node="3,1,0" data-index-in-node="0">const</b> — O'zgarmas ma'lumotlarni saqlash uchun ishlatiladi. Unga bir marta qiymat berilgach, uni qayta o'zgartirib bo'lmaydi (masalan: tug'ilgan yil, matematika dagi Pi soni).</p></li><li><p data-path-to-node="3,2,0"><b data-path-to-node="3,2,0" data-index-in-node="0">var</b> — JavaScript-ning eski versiyalaridagi o'zgaruvchi yaratish usuli. U o'zining ba'zi noqulayliklari va xavfsizlik kamchiliklari tufayli hozirgi zamonaviy dasturlashda deyarli ishlatilmaydi.</p></li></ul>
"""

L0_CODE = """\
// let — qiymati o'zgaradigan quticha
let yosh = 25;
yosh = 26; // Muammosiz o'zgaradi

// const — mutloq o'zgarmas quticha
const pi = 3.14;
// pi = 5; // Xatolik beradi, o'zgartirib bo'lmaydi!

// var — eski usul (ishlatmaslik tavsiya etiladi)
var ism = "Ali";
"""

L1_TEXT = """\
<h2>if / else — dastur qaror qabul qiladi</h2>

<pre class="mermaid">
flowchart TB
    A["if shart"] -->|true| THEN["if bloki ishlaydi"]
    A -->|false| ELIF["else if shart"]
    ELIF -->|true| THEN2["else if bloki ishlaydi"]
    ELIF -->|false| EL["else bloki ishlaydi"]
    THEN --> END["davom"]
    THEN2 --> END
    EL --> END
</pre>

<h3>🏆 5 daqiqada g'alaba — svetoforni kod orqali boshqaramiz</h3>
<p>Hech narsa o'rnatmaymiz. <code>about:blank</code> oching → <kbd>F12</kbd> → <strong>Console</strong>. Pastdagilarni yopishtirib, Enter bosing.</p>

<h4>BLOKA 1 — Birinchi qaror</h4>
<pre><code>let chiroq = "yashil";

if (chiroq === "yashil") {
    console.log("🚶 Yuring!");
} else {
    console.log("🛑 To'xtang!");
}</code></pre>
<p>Natija: <code>🚶 Yuring!</code>. Endi <code>chiroq</code>'ni o'zgartiring va qaytadan yuring:</p>
<pre><code>chiroq = "qizil";
if (chiroq === "yashil") { console.log("🚶 Yuring!"); } else { console.log("🛑 To'xtang!"); }</code></pre>
<p>Endi <code>🛑 To'xtang!</code>. <strong>Bitta o'zgaruvchi — ikki xil natija</strong>. Dasturingiz qaror qabul qildi.</p>

<h4>BLOKA 2 — 3 ta variant (else if)</h4>
<p>Sariq chiroqni ham qo'shamiz:</p>
<pre><code>let svetofor = "sariq";

if (svetofor === "yashil") {
    console.log("🚶 Yuring!");
} else if (svetofor === "sariq") {
    console.log("⏸ Kuting!");
} else {
    console.log("🛑 To'xtang!");
}</code></pre>
<p>Natija: <code>⏸ Kuting!</code>. <code>else if</code> zanjirini istalgancha cho'zish mumkin — 4, 5, 10 ta variant.</p>

<h4>BLOKA 3 — Interaktiv yosh tekshiruvchi</h4>
<pre><code>let yosh = Number(prompt("Yoshingizni kiriting:"));

if (yosh < 0) {
    alert("Bunday yosh bo'lmaydi!");
} else if (yosh < 7) {
    alert("Bog'cha yoshi 🧒");
} else if (yosh < 18) {
    alert("Maktab yoshi 📚");
} else if (yosh < 60) {
    alert("Voyaga yetgan 💼");
} else {
    alert("Hurmatli yosh 🎩");
}</code></pre>
<p><strong>Hayrat:</strong> bitta dastur 5 xil natija qaytaradi. Sharti birinchi <code>true</code> bo'lganda to'xtaydi — boshqalarni tekshirmaydi. Tartib MUHIM.</p>

<h3>🐛 Ataylab xato — `=` va `===` farqi</h3>
<p>Bu — JavaScript'ning eng mashhur tuzog'i. Sinab ko'ring:</p>
<pre><code>let kun = "shanba";

// XATO: bir tenglik = bu o'zlashtirish!
if (kun = "yakshanba") {
    console.log("Dam olish!");
} else {
    console.log("Ish kuni");
}</code></pre>
<p>Natija: <code>Dam olish!</code> — hatto <code>kun = "shanba"</code> bo'lsa ham. Sababi: bitta <code>=</code> — <strong>o'zlashtirish</strong> ("kunga yakshanba qiymatini ber"), <strong>solishtirish emas</strong>. Natijada kun o'zgardi va shart "truthy" deb baholandi.</p>
<p>To'g'risi — <strong>uchta</strong> tenglik:</p>
<pre><code>if (kun === "yakshanba") { ... }   // taqqoslash</code></pre>
<p>Qoida: <strong>solishtirishda har doim <code>===</code> ishlating</strong>. Yagona <code>=</code> faqat qiymat berish uchun.</p>

<h3>Endi tushuntiramiz — if / else if / else</h3>

<h4>Sintaksis</h4>
<pre><code>if (SHART) {
    // shart true bo'lsa — bu blok ishlaydi
} else if (BOSHQA_SHART) {
    // birinchi shart false, ikkinchisi true bo'lsa
} else {
    // hech qaysi shart true bo'lmasa
}</code></pre>

<h4>Taqqoslash operatorlari</h4>
<table>
<tr><th>Operator</th><th>Ma'no</th><th>Misol</th></tr>
<tr><td><code>===</code></td><td>Qat'iy teng (tur + qiymat)</td><td><code>5 === 5</code> → true</td></tr>
<tr><td><code>!==</code></td><td>Qat'iy teng emas</td><td><code>5 !== "5"</code> → true</td></tr>
<tr><td><code>&gt;</code> <code>&lt;</code></td><td>Katta / kichik</td><td><code>10 &gt; 5</code> → true</td></tr>
<tr><td><code>&gt;=</code> <code>&lt;=</code></td><td>Katta-teng / kichik-teng</td><td><code>5 &gt;= 5</code> → true</td></tr>
</table>
<p><strong>Eslatma:</strong> <code>==</code> (ikkita tenglik) — turlarni avtomatik aylantiradi: <code>"5" == 5</code> → <strong>true</strong>. Bu xavfli. Har doim <code>===</code> ishlating.</p>

<h4>Mantiqiy operatorlar (qisqacha)</h4>
<ul>
<li><code>&&</code> — VA (ikkalasi ham true bo'lsa)</li>
<li><code>||</code> — YOKI (hech bo'lmaganda bittasi true bo'lsa)</li>
<li><code>!</code> — EMAS (true → false, false → true)</li>
</ul>
<pre><code>let yosh = 25;
let karta = true;

if (yosh >= 18 && karta === true) {
    console.log("✅ Sotib olishingiz mumkin");
}</code></pre>

<h4>Tartib — birinchi true to'xtatadi</h4>
<p>JavaScript shartlarni yuqoridan pastga tekshiradi. Birinchi <code>true</code> topilganda — boshqalarini ko'rmaydi.</p>
<pre><code>let ball = 85;

if (ball >= 90) { console.log("A"); }
else if (ball >= 80) { console.log("B"); }   // ← bu ishlaydi
else if (ball >= 70) { console.log("C"); }   // ← tekshirilmaydi ham
else { console.log("D"); }</code></pre>

<h4>Qachon if, qachon else if, qachon else?</h4>
<ul>
<li><strong>Faqat if</strong> — bitta shart bor, "agar shu bo'lsa qil"</li>
<li><strong>if + else</strong> — 2 ta variant ("yashil yoki qizil")</li>
<li><strong>if + else if + else</strong> — 3+ variant ("yashil/sariq/qizil")</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>if</code> shart <code>true</code> bo'lsa — bloki ishlaydi</li>
<li><code>else if</code> bilan zanjir cho'zilarli, <code>else</code> "boshqa hamma holatda"</li>
<li>Solishtirish — har doim <code>===</code>, <strong>hech qachon</strong> <code>=</code></li>
<li>Birinchi <code>true</code> shart bajariladi, qolganlar tekshirilmaydi</li>
<li><code>&&</code> (VA), <code>||</code> (YOKI), <code>!</code> (EMAS) bilan shartlarni birlashtirasiz</li>
</ul>
"""

L1_CODE = """\
// ═══ DARS 2 — if / else / else if ═══
// about:blank → F12 → Console → pastdagilarni yopishtiring

// ─── BLOKA 1: Birinchi qaror ─────────────────────
let chiroq = "yashil";
if (chiroq === "yashil") {
    console.log("🚶 Yuring!");
} else {
    console.log("🛑 To'xtang!");
}

// O'zgaruvchini almashtiring, qaytadan yuring
chiroq = "qizil";
if (chiroq === "yashil") { console.log("🚶 Yuring!"); }
else { console.log("🛑 To'xtang!"); }

// ─── BLOKA 2: 3 ta variant — else if ─────────────
let svetofor = "sariq";
if (svetofor === "yashil") {
    console.log("🚶 Yuring!");
} else if (svetofor === "sariq") {
    console.log("⏸ Kuting!");
} else {
    console.log("🛑 To'xtang!");
}

// ─── BLOKA 3: Interaktiv yosh tekshiruvchi ───────
let yosh = Number(prompt("Yoshingizni kiriting:"));
if (yosh < 0)        alert("Bunday yosh bo'lmaydi!");
else if (yosh < 7)   alert("Bog'cha yoshi 🧒");
else if (yosh < 18)  alert("Maktab yoshi 📚");
else if (yosh < 60)  alert("Voyaga yetgan 💼");
else                 alert("Hurmatli yosh 🎩");

// ─── XATO TUZOG'I: bitta = vs uchta === ──────────
let kun = "shanba";
if (kun = "yakshanba") console.log("Dam!");       // XATO: o'zlashtirish
else                    console.log("Ish kuni");
// Tuzatish:
if (kun === "yakshanba") console.log("Dam!");     // TO'G'RI: taqqoslash
else                      console.log("Ish kuni");

// ─── Mantiqiy operator (&& va ||) ────────────────
let yoshim = 25, kartam = true;
if (yoshim >= 18 && kartam === true) {
    console.log("✅ Sotib olishingiz mumkin");
}
"""

L2_TEXT = """\
<pre class="mermaid">
flowchart LR
    A["expression"] --> AND["AND &&"]
    A --> OR["OR ||"]
    A --> NOT["NOT !"]
    A --> EQ["strict ==="]
    SW["switch value"] --> C1["case 1 break"]
    SW --> C2["case 2 break"]
    SW --> D["default"]
</pre>

<h2>3-Dars: Mantiqiy operatorlar va Switch-case</h2>

<h3>1. Mantiqiy operatorlar (Logical Operators)</h3>
<p>Bu darsda biz bir nechta shartni bitta <code>if</code> ichida birlashtirishni va katta <code>else if</code> zanjirlarini tozaroq <code>switch-case</code> konstruksiyasi bilan almashtirishni o'rganamiz.</p>
<p>Hayotiy misollar bilan boshlaymiz:</p>
<ul>
  <li><i>"Agar sizda <b>bilet</b> bo'lsa <b>VA</b> pasportingiz bo'lsa, samolyotga chiqasiz"</i> — ikkala shart ham kerak.</li>
  <li><i>"Agar pulingiz bo'lsa <b>YOKI</b> plastik kartangiz bo'lsa, supermarketdan xarid qilasiz"</i> — bittasi yetadi.</li>
  <li><i>"Agar yomg'ir yog'ayotgan bo'lmasa, ko'chaga chiqamiz"</i> — shartni teskarisiga aylantiramiz.</li>
</ul>
<p>JavaScript-da bular 3 ta asosiy belgidan iborat:</p>
<ul>
  <li><b><code>&amp;&amp;</code> (VA / AND)</b> — har ikki shart ham <code>true</code> bo'lsa, natija <code>true</code>. Aks holda <code>false</code>.</li>
  <li><b><code>||</code> (YOKI / OR)</b> — shartlardan kamida bittasi <code>true</code> bo'lsa, natija <code>true</code>.</li>
  <li><b><code>!</code> (EMAS / NOT)</b> — <code>true</code> ni <code>false</code> ga, <code>false</code> ni <code>true</code> ga aylantiradi.</li>
</ul>

<h4>Ustuvorlik (operator precedence)</h4>
<p>Bitta qatorda <code>&amp;&amp;</code> va <code>||</code> aralash kelsa, JavaScript avval <b><code>&amp;&amp;</code> ni</b> hisoblaydi, keyin <b><code>||</code> ni</b>. Buni o'zgartirish uchun qavslar <code>( )</code> ishlatiladi — qavs ichidagi ifoda har doim birinchi bajariladi.</p>

<h4>Qat'iy taqqoslash <code>===</code></h4>
<p>JavaScript-da ikki xil tenglik bor: <code>==</code> qiymatlarni solishtiradi, ammo turini o'zgartirib yuboradi (<code>"10" == 10</code> → <code>true</code>). <code>===</code> esa qiymat <b>va</b> turni birga tekshiradi (<code>"10" === 10</code> → <code>false</code>). <b>Doim <code>===</code> dan foydalaning</b> — kutilmagan xatolarning oldini oladi.</p>

<h3>2. Switch-case operatori</h3>
<p>Bitta qiymatni ko'p variantlar bilan solishtirishga to'g'ri kelganda <code>if / else if / else</code> zanjiri uzun va o'qish qiyin bo'ladi. Shu sababli <b>switch-case</b> ishlatiladi — bir nechta variantni tartibli ko'rinishda yozish imkonini beradi.</p>
<p>Hayotiy misol: foydalanuvchi haftaning kun raqamini kiritsa (1–7), unga kun nomini chiqarib berish kerak. <code>if</code> bilan 7 ta tarmoq yozish o'rniga, <code>switch</code> bilan kompakt yozamiz.</p>

<h4>Sintaksis</h4>
<p>Konstruksiyaning umumiy ko'rinishi quyidagicha:</p>
<ul>
  <li><code>switch (qiymat) { ... }</code> — qavs ichidagi qiymat har bir <code>case</code> bilan <b>qat'iy</b> (<code>===</code>) solishtiriladi.</li>
  <li><code>case "X":</code> — agar qiymat <code>"X"</code> ga teng bo'lsa, shu yerdagi kodlar ishlaydi.</li>
  <li><code>break;</code> — <b>juda muhim</b>. <code>break</code> yozilmasa, dastur <b>keyingi <code>case</code> ga ham tushib ketadi</b> (bu "fall-through" deyiladi va ko'pincha xato hisoblanadi).</li>
  <li><code>default:</code> — hech qaysi <code>case</code> mos kelmasa, <code>default</code> bloki ishlaydi. Bu <code>else</code> ga o'xshaydi va ko'pincha xato xabari yoki standart javob uchun ishlatiladi.</li>
</ul>

<h4>Bir nechta case'ni birlashtirish</h4>
<p>Bitta natijani bir nechta qiymat uchun ishlatish kerak bo'lsa, <code>case</code> larni ketma-ket <code>break</code> siz yozish mumkin — bu <b>"intentional fall-through"</b> deyiladi:</p>
<pre><code>switch (kun) {
  case "Shanba":
  case "Yakshanba":
    console.log("Dam olish kuni");
    break;
  default:
    console.log("Ish kuni");
}</code></pre>

<h4>Qachon <code>switch</code>, qachon <code>if</code>?</h4>
<ul>
  <li><b><code>switch</code></b> — bitta qiymatni <b>ko'p aniq variantlar</b> bilan solishtirganda (3+ variant).</li>
  <li><b><code>if / else if</code></b> — diapazon, oraliq yoki murakkab mantiqiy shartlar (<code>x &gt; 10 &amp;&amp; y &lt; 5</code>) tekshirilganda.</li>
</ul>
"""

L2_CODE = """\
// ── 1. Mantiqiy operatorlar ─────────────────────────────────────────────

let pul = true;
let karta = false;

// YOKI (||) — bittasi to'g'ri bo'lsa yetarli
if (pul || karta) {
    console.log("Xarid qilishingiz mumkin.");
}

// VA (&&) — ikkalasi ham true bo'lishi kerak
let bilet = true;
let pasport = true;
if (bilet && pasport) {
    console.log("Samolyotga chiqing.");
}

// EMAS (!) — shartni teskariga aylantiradi
let yomgir = false;
if (!yomgir) {
    console.log("Ko'chaga chiqishimiz mumkin.");
}

// Qat'iy taqqoslash (===) qiymat + turni birga tekshiradi
console.log("10" == 10);   // true  (== — turini o'zgartiradi)
console.log("10" === 10);  // false (=== — turi ham muhim)


// ── 2. Switch-case ─────────────────────────────────────────────────────

let kunRaqami = 3;

switch (kunRaqami) {
    case 1:
        console.log("Dushanba");
        break;
    case 2:
        console.log("Seshanba");
        break;
    case 3:
        console.log("Chorshanba");
        break;
    case 4:
        console.log("Payshanba");
        break;
    case 5:
        console.log("Juma");
        break;
    case 6:
    case 7:
        // Bir nechta case'ni birlashtirish — break yo'q, pastga "tushadi"
        console.log("Dam olish kuni");
        break;
    default:
        // Hech qaysi case mos kelmasa shu blok ishlaydi
        console.log("Noto'g'ri kun raqami (1-7 bo'lishi kerak)");
}
// Natija: "Chorshanba"
"""

L3_TEXT = """\
<pre class="mermaid">
flowchart TB
    V["let const var"] --> COND["if else"]
    COND --> LOG["AND OR NOT"]
    LOG --> SW["switch case"]
    SW --> PROJ["Mini-loyiha"]
    PROJ --> NEXT["Modul 2 ga otish"]
</pre>

<h2>1-Takrorlash Bloki (1, 2 va 3-Darslar bo'yicha)</h2>
<p>Birinchi modul yakunida o'tilgan asosiy bilimlarni jamlab olamiz. Bu blokda yangi mavzu yo'q — biror joyni unutgan bo'lsangiz, tegishli darsga qaytib o'qib, keyin pastdagi savollarga javob bering.</p>

<h3>1. O'zgaruvchilar va ma'lumot turlari (Modul 1, 1-Dars)</h3>
<ul>
  <li><b><code>let</code></b> — qiymati keyinchalik <b>o'zgarishi mumkin</b> bo'lgan o'zgaruvchi (eng ko'p ishlatiladi).</li>
  <li><b><code>const</code></b> — qiymati bir marta berilgandan keyin <b>o'zgarmaydigan</b> doimiy (constant). Masalan, <code>const PI = 3.14;</code>.</li>
  <li><code>var</code> — eski standart, hozirgi loyihalarda ishlatilmaydi.</li>
</ul>
<p>Asosiy ma'lumot turlari:</p>
<ul>
  <li><b><code>string</code></b> — matn, qo'shtirnoq ichida: <code>"Salom"</code>, <code>'Aziz'</code>.</li>
  <li><b><code>number</code></b> — son, tirnoqsiz: <code>10</code>, <code>3.14</code>.</li>
  <li><b><code>boolean</code></b> — mantiqiy qiymat: <code>true</code> yoki <code>false</code>.</li>
  <li><b><code>null</code></b> / <b><code>undefined</code></b> — "qiymat yo'q" turlari.</li>
</ul>

<h3>2. Shartli operatorlar — <code>if / else if / else</code> (2-Dars)</h3>
<p>Dasturning ma'lum bir qismini faqat ma'lum shart bajarilganda ishga tushirish uchun ishlatiladi.</p>
<ul>
  <li><code>if (shart) { ... }</code> — shart <code>true</code> bo'lsa, blok ichidagi kod ishlaydi.</li>
  <li><code>else if (boshqa shart)</code> — birinchi shart bajarilmasa, ikkinchisini tekshiradi.</li>
  <li><code>else { ... }</code> — yuqoridagi shartlarning hech biri to'g'ri bo'lmasa, shu blok ishlaydi.</li>
</ul>

<h3>3. Mantiqiy operatorlar va qat'iy taqqoslash (3-Dars)</h3>
<ul>
  <li><code>&amp;&amp;</code> (VA) — har ikki shart <code>true</code> bo'lganda ishlaydi.</li>
  <li><code>||</code> (YOKI) — kamida bittasi <code>true</code> bo'lganda ishlaydi.</li>
  <li><code>!</code> (EMAS) — qiymatni teskariga aylantiradi.</li>
  <li><code>===</code> — qiymat <b>va</b> turini birga tekshiradi (har doim shuni ishlating).</li>
  <li><code>==</code> — faqat qiymatni tekshiradi, turini o'zgartiradi (kutilmagan natijalar beradi).</li>
</ul>
<p><b>Ustuvorlik:</b> <code>&amp;&amp;</code> har doim <code>||</code> dan oldin hisoblanadi.</p>

<h3>4. <code>switch-case</code> operatori (3-Dars)</h3>
<p>Bitta qiymatni ko'p variantlar bilan solishtirish uchun ishlatiladi — uzun <code>else if</code> zanjirlarini almashtiradi.</p>
<ul>
  <li>Har bir <code>case</code> oxiriga <b><code>break</code></b> yozish shart, aks holda dastur keyingi case'larga ham tushib ketadi.</li>
  <li><b><code>default</code></b> bloki — switch'ning <code>else</code> qismi: hech qaysi case mos kelmaganda ishlaydi.</li>
  <li>Bir nechta <code>case</code> ketma-ket <code>break</code> siz yozilsa, ular bitta kodga "ulanadi" (intentional fall-through).</li>
</ul>

<h3>5. Tekshirish savollari (o'zingizni sinab ko'ring)</h3>
<ol>
  <li>Qaysi kalit so'z bilan e'lon qilingan o'zgaruvchining qiymatini keyinchalik o'zgartirib bo'lmaydi?</li>
  <li><code>if (x === "10")</code> shart <code>x = 10</code> bo'lganda bajariladimi? Nima uchun?</li>
  <li><code>true &amp;&amp; false || true</code> ifodaning natijasi qanday va nima uchun?</li>
  <li><code>switch (rang) { case "qizil": ...; case "ko'k": ...; }</code> da <code>break</code> qo'yilmasa nima bo'ladi?</li>
  <li><code>if</code> qachon afzal, <code>switch</code> qachon afzal?</li>
</ol>

<p>Quyidagi kod blokida bu uchta dars birga ishlatilgan — diqqat bilan o'qing va har bir qatordagi kalit so'zni o'zingizga tushuntirib bera olishingizga ishonch hosil qiling. So'ngra mashqlarga o'ting.</p>
"""

L3_CODE = """\
// ── Modul 1 takrorlash: uchta darsni birlashtirgan kichik dastur ────────
//
// Ssenariy: kafe buyurtmasi. Foydalanuvchi ovqat turi va to'lov usulini
// tanlaydi. Dastur yetarli pul borligini tekshiradi va xabar chiqaradi.

const SOLIH_NARX = 25000;      // const — o'zgarmaydigan narx
let buyurtmaTuri = "lavash";   // string
let toLovUsuli  = "naqd";      // string
let pulMiqdori  = 30000;       // number — hamyondagi pul
let bonusKarta  = false;       // boolean — chegirma kartasi bormi?

// 1) if / else if / else + mantiqiy operatorlar
if (buyurtmaTuri === "lavash" && (pulMiqdori >= SOLIH_NARX || bonusKarta)) {
    console.log("Buyurtmangiz qabul qilindi.");
} else if (!bonusKarta && pulMiqdori < SOLIH_NARX) {
    console.log("Mablag' yetarli emas.");
} else {
    console.log("Boshqa taom tanlang.");
}

// 2) switch-case — to'lov usuli bo'yicha xabar
switch (toLovUsuli) {
    case "naqd":
        console.log("Naqd to'lov qabul qilindi.");
        break;
    case "karta":
    case "click":
    case "payme":
        // Bir nechta case birlashtirilgan — barchasi onlayn to'lov
        console.log("Onlayn to'lov qayta ishlanmoqda...");
        break;
    default:
        console.log("Noma'lum to'lov usuli.");
}
// Kutilgan natija:
//   "Buyurtmangiz qabul qilindi."
//   "Naqd to'lov qabul qilindi."
"""

L4_TEXT = """\
<pre class="mermaid">
flowchart TB
    F["for init cond step"] --> B1["body har iter"]
    B1 --> CHK1["cond true"]
    CHK1 -->|yes| B1
    CHK1 -->|no| END["loop tugadi"]
    W["while cond"] --> CHK2["cond true"]
    CHK2 -->|yes| B2["body"]
    B2 -->|break| END
    B2 -->|continue| CHK2
    B2 --> CHK2
    CHK2 -->|no| END
</pre>

<h2 data-path-to-node="2">JavaScript Tsikllari (Loops)</h2><h3 data-path-to-node="3">Tsikl o'zi nima va nima uchun kerak?</h3><p data-path-to-node="4"><b data-path-to-node="4" data-index-in-node="0">Tsikl (Loop)</b> — bu ma'lum bir kodlar blokini bir necha marta qayta-qayta bajarish uchun ishlatiladigan dasturlash vositasi.</p><p data-path-to-node="5">Dasturlashda ko'p hollarda bir xil harakatni takrorlashga to'g'ri keladi. Masalan, konsolga 1 dan 100 gacha bo'lgan sonlarni chiqarish kerak deylik. Tsikllarsiz biz 100 qator <code data-path-to-node="5" data-index-in-node="175">console.log()</code> yozishga majbur bo'lardik. Tsikl yordamida esa buni bor-yo'g'i 3 qator kod bilan hal qilish mumkin.</p><p data-path-to-node="6">Web-dasturlashda tsikllar juda muhim o'rin tutadi:</p><ul data-path-to-node="7"><li><p data-path-to-node="7,0,0">Internet do'kondagi yuzlab mahsulotlarni sahifaga birma-bir chiqarishda.</p></li><li><p data-path-to-node="7,1,0">Foydalanuvchining kiritgan paroli to'g'ri bo'lmaguncha qayta so'rashda.</p></li><li><p data-path-to-node="7,2,0">Ma'lumotlar bazasidagi ro'yxatlarni aylanib chiqishda.</p></li></ul><p data-path-to-node="8">JavaScript-da eng ko'p ishlatiladigan ikkita asosiy tsikl mavjud: <b data-path-to-node="8" data-index-in-node="66"><code data-path-to-node="8" data-index-in-node="66">for</code></b> va <b data-path-to-node="8" data-index-in-node="73"><code data-path-to-node="8" data-index-in-node="73">while</code></b>.</p>
"""

L4_CODE = """\
// Kod namunasi: 1 dan 5 gacha sanash
for (let i = 1; i <= 5; i++) {
    console.log("Bu " + i + "-chi aylanish");
}
"""

L5_TEXT = """\
<pre class="mermaid">
flowchart LR
    A["arr = 10, 20, 30"] -->|arr 0| A0["birinchi 10"]
    A -->|arr.length| LEN["uzunlik 3"]
    A -->|push 40| AP["yangi oxirda"]
    A -->|pop| LAST["oxirgi qaytadi"]
    A -->|map filter forEach| HOF["yangi array"]
    A -->|arr.indexOf| IDX["index yoki -1"]
</pre>

Dasturlashda ko'p miqdordagi ma'lumotlarni bitta joyda tartibli saqlash uchun <b data-path-to-node="26" data-index-in-node="78">Massivlar (Arrays)</b> ishlatiladi. Masalan, guruhdagi 10 ta o'quvchining ismini saqlash uchun 10 ta alohida o'zgaruvchi ochish o'rniga, bitta massiv ichiga hammasini jamlash qulay.
"""

L5_CODE = """\
let mevalar = ["Olma", "Anor", "Banan"];

// Massiv elementlarini indeks orqali chaqirish:
console.log(mevalar[0]); // Konsolga "Olma" chiqadi
console.log(mevalar[1]); // Konsolga "Anor" chiqadi
console.log(mevalar[2]); // Konsolga "Banan" chiqadi

// Massiv ichida nechta element borligini aniqlash (.length):
console.log(mevalar.length); // Natija: 3
"""

L6_TEXT = """\
<pre class="mermaid">
flowchart LR
    D["function salom ism"] --> CALL["salom Aziz"]
    CALL --> BODY["body"]
    BODY --> RET["return qiymat"]
    AF["const f = arrow"] -->|arrow =>| BODY
    PAR["default param"] -->|optional| BODY
    SC["scope local"] -->|hidden| OUT["tashqaridan korinmaydi"]
</pre>

<h1 data-path-to-node="0">Funksiyalar (Functions) — Kodlarni qayta ishlatish</h1><p data-path-to-node="1">Dastur yozish davomida bir xil kodlar to'plamini loyihaning turli joylarida qayta-qayta ishlatishga to'g'ri keladi. Har safar bir xil kodni nusxalab yozmaslik uchun <b data-path-to-node="1" data-index-in-node="165">Funksiyalar (Functions)</b> ishlatiladi. Funksiya — bu ma'lum bir vazifani bajaradigan va istalgan vaqtda qayta ishlatilishi mumkin bo'lgan tayyor kod blokidir.</p>
"""

L6_CODE = """\
// 1. Funksiyani yaratish
let salomBer = function() {
    console.log("Salom! Kursimizga xush kelibsiz!");
};

// 2. Funksiyani ishga tushirish (Chaqirish)
salomBer(); // Konsolga xabar chiqadi
salomBer(); // Kodni yana qayta ishlatish mumkin
"""

L7_TEXT = """\
<pre class="mermaid">
flowchart TB
    L["loops for while"] --> ARR["array methods"]
    ARR --> FN["functions"]
    FN --> COMBO["birga ishlatish"]
    COMBO --> PROJ["mini-loyiha"]
    PROJ --> NEXT["Modul 3 ga otish"]
</pre>

<b data-path-to-node="27" data-index-in-node="0">Mavzular:</b> Tsikllar (<code data-path-to-node="27" data-index-in-node="20">for</code>, <code data-path-to-node="27" data-index-in-node="25">while</code>), Massivlar (Arrays) va Funksiyalar (Functions).
"""

L7_CODE = """\

"""

L8_TEXT = """\
<pre class="mermaid">
flowchart TB
    O["obj ism yosh"] -->|obj.ism| RD["read qiymat"]
    O -->|obj.ism = X| WR["update"]
    O -->|Object.keys| KS["array keys"]
    O -->|Object.values| VS["array values"]
    O -->|destructuring| DST["const ism = obj"]
    O -->|JSON.stringify| JS["string"]
</pre>

<h1 data-path-to-node="0">Obyektlar (Objects) — Murakkab ma'lumotlar bilan ishlash</h1><p data-path-to-node="1">Massivlarni o'rganayotganda ma'lumotlarni shunchaki ketma-ket joylashtirishni ko'rdik. Ammo real hayotda bitta narsaning (masalan, foydalanuvchi, mashina yoki mahsulotning) bir nechta turli xil xususiyatlari bo'ladi. Ularni tartibli saqlash uchun JavaScript-da <b data-path-to-node="1" data-index-in-node="261">Obyektlar (Objects)</b> ishlatiladi.</p><p data-path-to-node="2">Obyekt — bu ma'lumotlarni <b data-path-to-node="2" data-index-in-node="26">"kalit: qiymat"</b> (key: value) juftligi ko'rinishida saqlaydigan quti.</p>
"""

L8_CODE = """\
let talaba = {
    ism: "Asadbek",
    yosh: 20,
    kurs: 3,
    yaxshiKoradi: "JavaScript"
};

// Obyekt ichidagi ma'lumotni o'qish (Nuqta "." operatori orqali):
console.log(talaba.ism);  // Natija: Asadbek
console.log(talaba.yosh); // Natija: 20
"""

L9_TEXT = """\
<pre class="mermaid">
flowchart LR
    H["HTML"] --> DOM["DOM tree"]
    DOM -->|getElementById| EL["element"]
    DOM -->|querySelector| EL
    EL -->|textContent| TX["matn"]
    EL -->|innerHTML| HT["html"]
    EL -->|addEventListener click| EV["handler"]
    EV --> ACT["action"]
</pre>

<h1 data-path-to-node="0">&nbsp;DOM bilan ishlash (Document Object Model) — Brauzerni boshqarish</h1><p data-path-to-node="1">Shu vaqtgacha biz yozgan barcha JavaScript kodlarimiz faqat konsolda (Console) ishladi. Bugun esa JavaScript-ni veb-saytimizga bog'laymiz. Brauzerda ochilgan HTML sahifani JavaScript orqali o'zgartirish, unga ta'sir o'tkazish <b data-path-to-node="1" data-index-in-node="226">DOM (Document Object Model)</b> orqali amalga oshiriladi.</p><p data-path-to-node="2">DOM — bu brauzer tomonidan HTML sahifani daraxtsimon tuzilishga keltirib, JavaScript boshqara olishi uchun yaratilgan muhitdir.</p>
"""

L9_CODE = """\
// HTML-da <h1 id="sarlavha">Salom</h1> bor deb tasavvur qilamiz
let boshSarlavha = document.getElementById("sarlavha");

// HTML-da <p class="matn">Xayr</p> bor deb tasavvur qilamiz
let asosiyMatn = document.querySelector(".matn");
"""

L10_TEXT = """\
<pre class="mermaid">
flowchart LR
    C["createElement div"] --> N["yangi node"]
    N -->|setAttribute| AT["attributes"]
    N -->|textContent| T["matn"]
    P["parent element"] -->|appendChild N| P2["DOM ga qoshildi"]
    R["el.remove"] -->|delete| GONE["DOM dan ochdi"]
    P -->|removeChild N| GONE
</pre>

<p data-path-to-node="1">O'tgan darsda biz sahifada allaqachon bor bo'lgan HTML elementlarini tutib olishni va ularni o'zgartirishni o'rgandik. Bu darsda esa JavaScript yordamida sahifada umuman yo'q bo'lgan yangi HTML elementlarini noldan <b data-path-to-node="1" data-index-in-node="215">yaratish</b>, ularni sahifaga <b data-path-to-node="1" data-index-in-node="241">joylashtirish</b> va kerak bo'lmaganida <b data-path-to-node="1" data-index-in-node="277">o'chirib tashlashni</b> o'rganamiz.</p><p data-path-to-node="2">Bu usul veb-saytlarda ma'lumotlarni dinamik (jonli) yangilab turish uchun juda muhim hisoblanadi.</p>
"""

L10_CODE = """\
// 1. Xotirada yangi <li> tegi yaratiladi (lekin hali sahifada ko'rinmaydi)
let yangiElement = document.createElement("li");

// 2. Ichiga matn yozamiz
yangiElement.innerText = "Yangi dars kursi";

// 3. Unga CSS klass qo'shamiz
yangiElement.classList.add("royxat-stil");
"""

L11_TEXT = """\
<pre class="mermaid">
flowchart TB
    O["objects"] --> DM["DOM access"]
    DM --> CR["create remove"]
    CR --> PROJ["loyiha"]
    PROJ --> NEXT["Modul 4 ga otish"]
</pre>

<b data-path-to-node="50" data-index-in-node="0">Mavzular:</b> Obyektlar (Objects), DOM bilan ishlash va Elementlarni dinamik yaratish/o'chirish.
"""

L11_CODE = """\

"""

L12_TEXT = """\
<pre class="mermaid">
flowchart LR
    L["localStorage"] -->|setItem k v| SAVE["browser save"]
    L -->|getItem k| READ["string yoki null"]
    L -->|removeItem k| DEL["ochiriladi"]
    O["object array"] -->|JSON.stringify| STR["string"]
    STR --> SAVE
    READ -->|JSON.parse| O2["object qaytadi"]
</pre>

<h1 data-path-to-node="0">LocalStorage — Ma'lumotlarni brauzer xotirasida saqlash</h1><p data-path-to-node="1">Shu vaqtgacha biz yaratgan dasturlarda (masalan, "Mehmonlar ro'yxati" yoki "Vazifalar ro'yxati" loyihalarida) bitta muammo bor edi: agar brauzer sahifasini yangilasak (Refresh qilsak), barcha kiritilgan ma'lumotlar o'chib ketardi.</p><p data-path-to-node="2">Bugun ma'lumotlarni foydalanuvchi kompyuterida (brauzerida) doimiy saqlashni o'rganamiz. Buning uchun <b data-path-to-node="2" data-index-in-node="102">LocalStorage</b> (Mahalliy xotira) ishlatiladi. LocalStorage-ga yozilgan ma'lumotlar brauzer yopilsa ham, kompyuter o'chirib yoqilsa ham o'chib ketmaydi.</p>
"""

L12_CODE = """\
// 1. Ismni xotiraga "foydalanuvchi" kaliti bilan saqlaymiz
localStorage.setItem("foydalanuvchi", "Sardor");

// 2. Sahifa yangilanganda xotiradan o'sha ismni qayta o'qib olamiz
let ism = localStorage.getItem("foydalanuvchi");

console.log(ism); // Natija: Sardor
"""

L13_TEXT = """\
<pre class="mermaid">
flowchart LR
    A["array"] -->|indexOf| I["index yoki -1"]
    A -->|includes| BL["true false"]
    A -->|find| EL["birinchi mos"]
    A -->|filter| NEW["yangi array"]
    A -->|map| TR["transform"]
    A -->|reduce| ACC["bitta qiymat"]
    A -->|sort| SO["saralash"]
</pre>

<h1 data-path-to-node="0">Massivlarning qidiruv va o'zgarish metodlari — <code data-path-to-node="0" data-index-in-node="56">map</code>, <code data-path-to-node="0" data-index-in-node="61">filter</code>, <code data-path-to-node="0" data-index-in-node="69">find</code></h1><p data-path-to-node="1">5-darsda biz massivlar bilan ishlashning oddiy usullarini (<code data-path-to-node="1" data-index-in-node="59">push</code>, <code data-path-to-node="1" data-index-in-node="65">pop</code>) ko'rgan edik. Real loyihalarda esa massiv ichidagi yuzlab ma'lumotlar orasidan keraklisini qidirib topish, saralash yoki ularni o'zgartirish talab etiladi. Buning uchun JavaScript-da juda kuchli va zamonaviy metodlar mavjud.</p>
"""

L13_CODE = """\
let eskiNarxlar = [1000, 2000, 3000];

let yangiNarxlar = eskiNarxlar.map(function(narx) {
    return narx * 2; 
});

console.log(yangiNarxlar); // Natija: [2000, 4000, 6000]
"""

L14_TEXT = """\
<pre class="mermaid">
flowchart TB
    LS["localStorage"] --> AM["array methods"]
    AM --> SAVE["JSON save load"]
    SAVE --> APP["TODO ilova"]
    APP --> END["Kursni tugatdingiz"]
</pre>

<b data-path-to-node="3" data-index-in-node="0">Mavzular:</b> LocalStorage (Xotira bilan ishlash) va Massivlarning qidiruv/oʻzgarish metodlari (<code data-path-to-node="3" data-index-in-node="92">map</code>, <code data-path-to-node="3" data-index-in-node="97">filter</code>, <code data-path-to-node="3" data-index-in-node="105">find</code>)
"""

L14_CODE = """\

"""

def mc(title, options, correct, *, multi=False, hint="", explanation="", diff="Easy", pts=2):
    return {"title": title, "description": title, "exercise_type": "multiple_choice",
            "options": options, "correct_answers": correct, "is_multiple_select": multi,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}

def dd(title, items_in_order, *, hint="", explanation="", diff="Medium", pts=3):
    return {"title": title, "description": title, "exercise_type": "drag_and_drop",
            "drag_items": list(items_in_order), "correct_order": list(items_in_order),
            "is_multiple_select": False, "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}

def ti(title, expected, *, hint="", explanation="", diff="Hard", pts=4):
    return {"title": title, "description": title, "exercise_type": "text_input",
            "expected_answer": expected, "is_multiple_select": False,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


LESSON_TASKS: dict[int, dict] = {
    0: {
        "title": "Tashrif kartasi (let / const / var)",
        "description": "Birinchi JavaScript loyihangiz. console.log yordamida o'zingiz haqingizda qisqa tashrif kartasini chiqaring. let, const va var farqini amaliyotda ko'rsating.",
        "requirements": "• Kamida 4 ta o'zgaruvchi: ism (const), yosh (let), shahar (let), pi (const)\n• Konsolga chiroyli formatda chiqarish (kamida 6 ta console.log)\n• yosh o'zgaruvchisi 1 marta o'zgartirilgan bo'lsin\n• const ni o'zgartirishga urinish izoh sifatida ko'rsatilgan\n• Faylning boshida izoh bilan dastur tavsifi\n• .js fayl va README.md (qanday ishga tushirish)",
        "technologies": "JavaScript ES6+, let/const/var, console.log",
        "deadline_days": 3,
    },
    1: {
        "title": "Loyiha",
        "description": "1-Loyiha: \"Aqlli Svetofor va Yo'l qoidasi\"\n(If, Else If, Else mavzulari uchun)\n\nVazifa sharti: O'quvchi shunday dastur tuzishi kerakki, unda svetoforning rangi va mashina tezligi o'zgaruvchi sifatida beriladi. Dastur shu ikki ma'lumotga qarab haydovchiga nima qilish kerakligini aytadi:\n\n1-shart: Agar chiroq \"qizil\" bo'lsa:\n\nTezlik 0 bo'lsa — konsolga \"To'g'ri, to'xtab turibsiz.\" chiqsin.\n\nTezlik 0 dan katta bo'lsa — \"Taqiqlangan! Sizga jarima yozildi!\" chiqsin.\n\n2-shart: Agar chiroq \"sariq\" bo'lsa:\n\nTezlik yuqori bo'lsa (masalan, 50 dan baland) — \"Tezlikni kamaytiring va to'xtashga tayyorlaning!\" chiqsin.\n\nTezlik past bo'lsa — \"To'xtab kuting.\" chiqsin.\n\n3-shart: Agar chiroq \"yashil\" bo'lsa:\n\nXavfsiz harakatlanish uchun \"Yo'lingiz ochiq, xavfsiz harakatlaning!\" chiqsin.\n\n4-shart (Aks holda): Agar svetofor rangi yuqoridagilardan boshqa narsa bo'lsa yoki ishlamayotgan bo'lsa — \"Svetofor buzilgan, tartibga soluvchiga qarang!\" deb chiqsin.",
        "requirements": "1-Loyiha: \"Aqlli Svetofor va Yo'l qoidasi\"\n(If, Else If, Else mavzulari uchun)\n\nVazifa sharti: O'quvchi shunday dastur tuzishi kerakki, unda svetoforning rangi va mashina tezligi o'zgaruvchi sifatida beriladi. Dastur shu ikki ma'lumotga qarab haydovchiga nima qilish kerakligini aytadi:\n\n1-shart: Agar chiroq \"qizil\" bo'lsa:\n\nTezlik 0 bo'lsa — konsolga \"To'g'ri, to'xtab turibsiz.\" chiqsin.\n\nTezlik 0 dan katta bo'lsa — \"Taqiqlangan! Sizga jarima yozildi!\" chiqsin.\n\n2-shart: Agar chiroq \"sariq\" bo'lsa:\n\nTezlik yuqori bo'lsa (masalan, 50 dan baland) — \"Tezlikni kamaytiring va to'xtashga tayyorlaning!\" chiqsin.\n\nTezlik past bo'lsa — \"To'xtab kuting.\" chiqsin.\n\n3-shart: Agar chiroq \"yashil\" bo'lsa:\n\nXavfsiz harakatlanish uchun \"Yo'lingiz ochiq, xavfsiz harakatlaning!\" chiqsin.\n\n4-shart (Aks holda): Agar svetofor rangi yuqoridagilardan boshqa narsa bo'lsa yoki ishlamayotgan bo'lsa — \"Svetofor buzilgan, tartibga soluvchiga qarang!\" deb chiqsin.",
        "technologies": "javascript ",
        "deadline_days": 1,
    },
    2: {
        "title": "Loyiha",
        "description": "\"Virtual Kafedra Yordamchisi\"\n(Mantiqiy operatorlar va Switch-case uchun)\n\nVazifa sharti: O'quvchi bitta umumiy o'zgaruvchi (masalan, haftaning kuni) va ikkita mantiqiy o'zgaruvchi (imtihonBor = true/false va vazifaBajarildi = true/false) e'lon qiladi. Dastur switch-case va mantiqiy operatorlar orqali talabaning kun tartibini belgilab berishi kerak:\n\n1-qism (switch-case yordamida):\n\nKun \"Dushanba\" yoki \"Chorshanba\" yoki \"Juma\" bo'lsa — konsolga \"Bugun asosiy dars kunlari.\" chiqsin.\n\nKun \"Seshanba\" yoki \"Payshanba\" bo'lsa — \"Bugun amaliyot va laboratoriya kuni.\" chiqsin.\n\nKun \"Shanba\" yoki \"Yakshanba\" bo'lsa — \"Dam olish kuni.\" chiqsin.\n\n2-qism (Mantiqiy operatorlar &&, || yordamida):\n\nAgar bugun dars kuni bo'lsa VA imtihonBor rost (true) bo'lsa — \"Darhol imtihon zaliga kiring!\" chiqsin.\n\nAgar imtihonBor yolg'on (false) bo'lsa VA vazifaBajarildi rost (true) bo'lsa — \"Siz darsga tayyorsiz, kirishingiz mumkin.\" chiqsin.\n\nAgar dars kuni bo'lsa-yu, lekin na imtihon bo'lsa va na vazifa bajarilgan bo'lsa — \"Vazifani bajarmaganingiz uchun darsga kiritilmaysiz!\" chiqsin.\n\nAgar kun dam olish kuni bo'lsa YOKI darslar rasman qoldirilgan bo'lsa — \"Miriqib dam oling!\" chiqsin.",
        "requirements": "\"Virtual Kafedra Yordamchisi\"\n(Mantiqiy operatorlar va Switch-case uchun)\n\nVazifa sharti: O'quvchi bitta umumiy o'zgaruvchi (masalan, haftaning kuni) va ikkita mantiqiy o'zgaruvchi (imtihonBor = true/false va vazifaBajarildi = true/false) e'lon qiladi. Dastur switch-case va mantiqiy operatorlar orqali talabaning kun tartibini belgilab berishi kerak:\n\n1-qism (switch-case yordamida):\n\nKun \"Dushanba\" yoki \"Chorshanba\" yoki \"Juma\" bo'lsa — konsolga \"Bugun asosiy dars kunlari.\" chiqsin.\n\nKun \"Seshanba\" yoki \"Payshanba\" bo'lsa — \"Bugun amaliyot va laboratoriya kuni.\" chiqsin.\n\nKun \"Shanba\" yoki \"Yakshanba\" bo'lsa — \"Dam olish kuni.\" chiqsin.\n\n2-qism (Mantiqiy operatorlar &&, || yordamida):\n\nAgar bugun dars kuni bo'lsa VA imtihonBor rost (true) bo'lsa — \"Darhol imtihon zaliga kiring!\" chiqsin.\n\nAgar imtihonBor yolg'on (false) bo'lsa VA vazifaBajarildi rost (true) bo'lsa — \"Siz darsga tayyorsiz, kirishingiz mumkin.\" chiqsin.\n\nAgar dars kuni bo'lsa-yu, lekin na imtihon bo'lsa va na vazifa bajarilgan bo'lsa — \"Vazifani bajarmaganingiz uchun darsga kiritilmaysiz!\" chiqsin.\n\nAgar kun dam olish kuni bo'lsa YOKI darslar rasman qoldirilgan bo'lsa — \"Miriqib dam oling!\" chiqsin.",
        "technologies": "javascript",
        "deadline_days": 1,
    },
    3: {
        "title": "1-Loyiha: \"Kinochi Bot\"",
        "description": "Shart: Foydalanuvchining yoshi va puli oʻzgaruvchi sifatida beriladi. Agar yoshi 16 dan katta VA puli 20 000 soʻmdan koʻp boʻlsa, konsolga \"Kinoga kirishingiz mumkin\" deb chiqsin. Agar shartlardan biri xato boʻlsa, \"Kirish taqiqlanadi\" degan yozuv chiqsin.",
        "requirements": "Shart: Foydalanuvchining yoshi va puli oʻzgaruvchi sifatida beriladi. Agar yoshi 16 dan katta VA puli 20 000 soʻmdan koʻp boʻlsa, konsolga \"Kinoga kirishingiz mumkin\" deb chiqsin. Agar shartlardan biri xato boʻlsa, \"Kirish taqiqlanadi\" degan yozuv chiqsin.",
        "technologies": "",
        "deadline_days": 1,
    },
    4: {
        "title": "Mini-Loyiha: Aqlli Bankomat va Do'kon tizimi",
        "description": "Ushbu loyihada siz JavaScript-dagi tsikllardan foydalanib, foydalanuvchi bilan muloqot qiluvchi dastur yaratasiz.\n\nDastur ikki qismdan iborat bo'ladi:\n\nBankomat qismi (while tsikli): Foydalanuvchi bankomat kartasining PIN kodini to'g'ri kiritmaguncha tizim undan parolni qayta-qayta so'raydi (maksimal 3 ta urinish).\n\nDo'kon qismi (for tsikli): Foydalanuvchi tizimga kirgach, unga do'kondagi mahsulotlar va ularning narxlari ro'yxati tsikl yordamida chiroyli qilib ko'rsatiladi.",
        "requirements": "while tsikli yordamida parol tekshirish tizimini tuzing. Agar parol xato bo'lsa, xatolikni aytib qayta so'rang. Urinishlar soni 3 tadan oshib ketsa, \"Karta bloklandi\" xabarini chiqaring.\n\nfor tsikli yordamida massiv (array) ichidagi kamida 5 ta mahsulot nomini va narxini konsolga ketma-ketlikda chiqaring.\n\nKodda break yoki continue operatorlaridan o'rinli foydalaning (masalan, parol to'g'ri topilsa, tsiklni to'xtatish uchun).\n\nKod toza, o'zgaruvchilar nomlari tushunarli (let, const) bo'lishi lo'zim.",
        "technologies": "JavaScript, HTML",
        "deadline_days": 2,
    },
    5: {
        "title": "5-Dars bo'yicha Mustaqil Loyiha Ishi: \"Kutubxona Tizimi\" Loyiha maqsadi: O'tilgan massivlar, ularning metodlari va for tsiklini real loyihada mustahkamlash.",
        "description": "Vazifa sharti:\nSiz kutubxona tizimini yaratishingiz kerak. Buning uchun quyidagi qadamlarni kod orqali bajaring:\n\nkitoblar nomli massiv oching va uning ichiga dastlab 3 ta kitob nomini matn (string) ko'rinishida joylashtiring.\n\nKutubxonaga yangi \"O'tkan kunlar\" va \"Kichik shahzoda\" kitoblari olib kelindi. Bu ikki kitobni massivning oxiriga qo'shing.\n\nKutubxonadagi eng birinchi turgan kitobni biror o'quvchi o'qishga olib ketdi. Ushbu kitobni massivning boshidan o'chirib tashlang.\n\nYakunda kutubxonada qolgan barcha kitoblarni for tsikli yordamida, foydalanuvchiga tushunarli bo'lishi uchun 1, 2, 3... qilib tartib raqami bilan konsolga chiqaring.",
        "requirements": "Vazifa sharti:\nSiz kutubxona tizimini yaratishingiz kerak. Buning uchun quyidagi qadamlarni kod orqali bajaring:\n\nkitoblar nomli massiv oching va uning ichiga dastlab 3 ta kitob nomini matn (string) ko'rinishida joylashtiring.\n\nKutubxonaga yangi \"O'tkan kunlar\" va \"Kichik shahzoda\" kitoblari olib kelindi. Bu ikki kitobni massivning oxiriga qo'shing.\n\nKutubxonadagi eng birinchi turgan kitobni biror o'quvchi o'qishga olib ketdi. Ushbu kitobni massivning boshidan o'chirib tashlang.\n\nYakunda kutubxonada qolgan barcha kitoblarni for tsikli yordamida, foydalanuvchiga tushunarli bo'lishi uchun 1, 2, 3... qilib tartib raqami bilan konsolga chiqaring.",
        "technologies": "Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): let kitoblar = [...]; — massiv yaratish.  .push() — oxiriga kitob qo'shish.  .shift() — boshidan kitobni o'chirish.  .length — tsiklda massiv uzunligini aniqlash.  for (let i = 0; i < kitoblar.length; i++) — elementlarni konsolga tartib bilan chiqarish.",
        "deadline_days": 5,
    },
    6: {
        "title": "Loyiha maqsadi: Funksiyalar, parametrlar va return operatorini amaliy masalada qo'llash.",
        "description": "Vazifa sharti:\nOnlayn do'kon tizimi uchun ikkita funksiyadan iborat kichik dastur tuzing:\n\nhisobla nomli funksiya yarating. U 2 ta parametr qabul qilsin: mahsulotNarxi va miqdori. Funksiya bularni o'zaro ko'paytirib, umumiy summani return orqali qaytarsin.\n\nchegirmaBer nomli ikkinchi funksiya yarating. U 1 ta umumiySumma parametrini qabul qilsin.\n\nAgar umumiy summa 100 000 so'mdan ko'p bo'lsa, unga 10% chegirma hisoblab, yakuniy to'lanadigan pulni return qilsin.\n\nAks holda, chegirmasiz asl narxni qaytarsin.\n\nDastur so'ngida ushbu ikki funksiyani ketma-ket chaqirib, foydalanuvchi 3 ta 40 000 so'mlik mahsulot olgandagi yakuniy to'lov miqdorini konsolga chiqaring.",
        "requirements": "Vazifa sharti:\nOnlayn do'kon tizimi uchun ikkita funksiyadan iborat kichik dastur tuzing:\n\nhisobla nomli funksiya yarating. U 2 ta parametr qabul qilsin: mahsulotNarxi va miqdori. Funksiya bularni o'zaro ko'paytirib, umumiy summani return orqali qaytarsin.\n\nchegirmaBer nomli ikkinchi funksiya yarating. U 1 ta umumiySumma parametrini qabul qilsin.\n\nAgar umumiy summa 100 000 so'mdan ko'p bo'lsa, unga 10% chegirma hisoblab, yakuniy to'lanadigan pulni return qilsin.\n\nAks holda, chegirmasiz asl narxni qaytarsin.\n\nDastur so'ngida ushbu ikki funksiyani ketma-ket chaqirib, foydalanuvchi 3 ta 40 000 so'mlik mahsulot olgandagi yakuniy to'lov miqdorini konsolga chiqaring.",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): function hisobla(mahsulotNarxi, miqdori) { ... }  return mahsulotNarxi * miqdori;  if (umumiySumma > 100000) { ... }  10% chegirmali narxni hisoblash formulasi: umumiySumma * 0.9",
        "deadline_days": 2,
    },
    7: {
        "title": "1-Loyiha: \"Sonlar yig'indisi\"",
        "description": "Shart: 1 dan 50 gacha boʻlgan sonlar orasidan faqat juft sonlarni ajratib, ularning umumiy yigʻindisini for tsikli yordamida hisoblaydigan dastur tuzing va yakuniy natijani konsolga chiqaring.",
        "requirements": "Shart: 1 dan 50 gacha boʻlgan sonlar orasidan faqat juft sonlarni ajratib, ularning umumiy yigʻindisini for tsikli yordamida hisoblaydigan dastur tuzing va yakuniy natijani konsolga chiqaring.",
        "technologies": "",
        "deadline_days": 1,
    },
    8: {
        "title": "Loyiha maqsadi: Obyektlar, ularning xususiyatlari va metodlarini amaliy topshiriqda mustahkamlash.",
        "description": "📋 Vazifa sharti:\nAvtosalon boshqaruv tizimi uchun bitta mashina obyektini yarating:\n\nmashina nomli obyekt oching. Unda quyidagi xususiyatlar bo'lsin:\n\nbrend (masalan: \"Chevrolet\")\n\nmodel (masalan: \"Gentra\")\n\nyil (masalan: 2022)\n\nnarx (masalan: 13000)\n\ntanirovka (boshida false bo'lsin)\n\nMashinaning rangi dastlab berilmagan. Obyektdan tashqarida unga rang: \"To'q kulrang\" xususiyatini qo'shing.\n\nMashinaning narxi o'zgardi, obyektdan tashqarida narxni 12500 ga yangilang.\n\nObyekt ichida malumotBering nomli metod yarating. U chaqirilganda konsolga: \"Brend: Chevrolet, Model: Gentra, Narxi: 12500$\" degan matnni this orqali chiqarib bersin.\n\nObyekt ichida tanirovkaQildir nomli ikkinchi metod yarating. U ishga tushganda obyekt ichidagi tanirovka qiymatini truega o'zgartirsin va narxiga 500 dollar qo'shib qo'ysin.\n\nDastur oxirida dastlab malumotBering() metodini chaqiring, keyin tanirovkaQildir() metodini ishga tushiring va yakunda mashina obyektini konsolga chiqarib o'zgarishlarni tekshiring.",
        "requirements": "📋 Vazifa sharti:\nAvtosalon boshqaruv tizimi uchun bitta mashina obyektini yarating:\n\nmashina nomli obyekt oching. Unda quyidagi xususiyatlar bo'lsin:\n\nbrend (masalan: \"Chevrolet\")\n\nmodel (masalan: \"Gentra\")\n\nyil (masalan: 2022)\n\nnarx (masalan: 13000)\n\ntanirovka (boshida false bo'lsin)\n\nMashinaning rangi dastlab berilmagan. Obyektdan tashqarida unga rang: \"To'q kulrang\" xususiyatini qo'shing.\n\nMashinaning narxi o'zgardi, obyektdan tashqarida narxni 12500 ga yangilang.\n\nObyekt ichida malumotBering nomli metod yarating. U chaqirilganda konsolga: \"Brend: Chevrolet, Model: Gentra, Narxi: 12500$\" degan matnni this orqali chiqarib bersin.\n\nObyekt ichida tanirovkaQildir nomli ikkinchi metod yarating. U ishga tushganda obyekt ichidagi tanirovka qiymatini truega o'zgartirsin va narxiga 500 dollar qo'shib qo'ysin.\n\nDastur oxirida dastlab malumotBering() metodini chaqiring, keyin tanirovkaQildir() metodini ishga tushiring va yakunda mashina obyektini konsolga chiqarib o'zgarishlarni tekshiring.",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): let mashina = { brend: \"...\", ... };  mashina.rang = \"...\"; — yangi qiymat qo'shish.  malumotBering: function() { return ... this.brend ... }  this.tanirovka = true; — metod ichida qiymatni o'zgartirish.",
        "deadline_days": 2,
    },
    9: {
        "title": "Loyiha maqsadi: DOM selektorlari, .style xususiyati va click hodisasini real misolda birlashtirish.",
        "description": "📋 Vazifa sharti:\nSaytda bitta sarlavha, bitta matn va bitta tugma bor. Tugma bosilganda saytning umumiy foni va matnlar rangi o'zgarishi kerak:\n\nHTML sahifada <body> ichida bitta <h1>, bitta <p> va bitta <button> yarating. Ularga mos ravishda id nomlarini bering.\n\nJavaScript-da sahifaning fonini boshqarish uchun document.body ni hamda yaratilgan tugmani alohida o'zgaruvchiga tutib oling.\n\nTugmaga addEventListener yordamida click (bosish) hodisasini biriktiring.\n\nTugma bosilganda shunday kod yozingki:\n\nSahifaning fon rangi qora bo'lsin (body.style.backgroundColor = \"black\").\n\nSarlavha va matnlar rangi oq rangga o'tsin.\n\nTugma ichidagi yozuv \"Kunduzgi rejimga o'tish\" so'ziga o'zgarsin.",
        "requirements": "📋 Vazifa sharti:\nSaytda bitta sarlavha, bitta matn va bitta tugma bor. Tugma bosilganda saytning umumiy foni va matnlar rangi o'zgarishi kerak:\n\nHTML sahifada <body> ichida bitta <h1>, bitta <p> va bitta <button> yarating. Ularga mos ravishda id nomlarini bering.\n\nJavaScript-da sahifaning fonini boshqarish uchun document.body ni hamda yaratilgan tugmani alohida o'zgaruvchiga tutib oling.\n\nTugmaga addEventListener yordamida click (bosish) hodisasini biriktiring.\n\nTugma bosilganda shunday kod yozingki:\n\nSahifaning fon rangi qora bo'lsin (body.style.backgroundColor = \"black\").\n\nSarlavha va matnlar rangi oq rangga o'tsin.\n\nTugma ichidagi yozuv \"Kunduzgi rejimga o'tish\" so'ziga o'zgarsin.",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): let tugma = document.getElementById(\"...\");  let sarlavha = document.querySelector(\"...\");  tugma.addEventListener(\"click\", function() { ... });  document.body.style.backgroundColor = \"black\";  tugma.innerText = \"Kun tartibi\";",
        "deadline_days": 2,
    },
    10: {
        "title": "Loyiha maqsadi: Elementlarni dinamik yaratish, joylashtirish va ularga o'chirish funksiyasini bog'lashni amaliyotda sinash.",
        "description": "📋 Vazifa sharti:\nFoydalanuvchi ism yozib tugmani bossa, u sahifaga chiroyli ro'yxat bo'lib qo'shiladigan va yonida o'chirish tugmasi bo'ladigan dastur tuzing:\n\nHTML sahifada bitta matn kiritish oynasi (<input>), bitta qo'shish tugmasi (<button>) va bitta bo'sh ro'yxat (<ul>) yarating.\n\nJavaScript-da inputni, tugmani va <ul> elementini o'zgaruvchilarga tutib oling.\n\nQo'shish tugmasiga click hodisasini biriktiring va tugma bosilganda quyidagilar bajarilsin:\n\nInput ichidagi qiymatni (input.value) oling.\n\nYangi <li> elementi yarating va inputdagi matnni uning ichiga yozing.\n\nYangi <button> (O'chirish tugmasi) yarating, ichiga \"X\" deb yozing va unga bosilganda o'sha <li> elementini .remove() qilib tashlaydigan kod yozing.\n\n\"X\" tugmasini <li> ichiga joylashtiring, keyin esa <li> ni <ul> ro'yxatining ichiga qo'shing.\n\nOxirida keyingi safar oson yozish uchun input ichini bo'shatib qo'ying (input.value = \"\").",
        "requirements": "📋 Vazifa sharti:\nFoydalanuvchi ism yozib tugmani bossa, u sahifaga chiroyli ro'yxat bo'lib qo'shiladigan va yonida o'chirish tugmasi bo'ladigan dastur tuzing:\n\nHTML sahifada bitta matn kiritish oynasi (<input>), bitta qo'shish tugmasi (<button>) va bitta bo'sh ro'yxat (<ul>) yarating.\n\nJavaScript-da inputni, tugmani va <ul> elementini o'zgaruvchilarga tutib oling.\n\nQo'shish tugmasiga click hodisasini biriktiring va tugma bosilganda quyidagilar bajarilsin:\n\nInput ichidagi qiymatni (input.value) oling.\n\nYangi <li> elementi yarating va inputdagi matnni uning ichiga yozing.\n\nYangi <button> (O'chirish tugmasi) yarating, ichiga \"X\" deb yozing va unga bosilganda o'sha <li> elementini .remove() qilib tashlaydigan kod yozing.\n\n\"X\" tugmasini <li> ichiga joylashtiring, keyin esa <li> ni <ul> ro'yxatining ichiga qo'shing.\n\nOxirida keyingi safar oson yozish uchun input ichini bo'shatib qo'ying (input.value = \"\").",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): let li = document.createElement(\"li\");  let ochirishBtn = document.createElement(\"button\");`  o'chirishBtn.innerText = \"X\";  o'chirishBtn.addEventListener(\"click\", function() { li.remove(); });  li.appendChild(o'chirishBtn);  ul.appendChild(li);",
        "deadline_days": 3,
    },
    11: {
        "title": "1-Loyiha: \"O'yinchi Profili\"",
        "description": "Shart: oyinchi nomli obyekt yarating. Unda ism, ochko (boshida 0) xususiyatlari boʻlsin. Shuningdek, obyekt ichida ochkoOshir nomli metod boʻlsin, u chaqirilganda this orqali oʻyinchining ochkosini 10 taga oshirib qoʻysin",
        "requirements": "Shart: oyinchi nomli obyekt yarating. Unda ism, ochko (boshida 0) xususiyatlari boʻlsin. Shuningdek, obyekt ichida ochkoOshir nomli metod boʻlsin, u chaqirilganda this orqali oʻyinchining ochkosini 10 taga oshirib qoʻysin",
        "technologies": "",
        "deadline_days": 3,
    },
    12: {
        "title": "Loyiha maqsadi: LocalStorage orqali ma'lumotlarni saqlash, o'qish va sahifa yangilanganda ham natijani saqlab qolishni o'rganish.",
        "description": "📋 Vazifa sharti:\nFoydalanuvchi o'z ismini kiritib \"Eslab qol\" tugmasini bossa, ism xotiraga yozilishi va sahifa necha marta yangilansa ham ekran tepasida o'sha ism turishi kerak. \"Xotirani o'chirish\" tugmasi bosilganda esa ism o'chib ketishi kerak.\n\nHTML sahifada bitta <h1> (ismni ko'rsatish uchun), bitta <input> (ism yozish uchun) va ikkita tugma (\"Eslab qol\" va \"O'chirish\") yarating.\n\nDastur boshida har doim LocalStorage-ni tekshiring: agar xotirada ism bo'lsa, uni darhol <h1> ichiga yozib qo'ying.\n\n\"Eslab qol\" tugmasi bosilganda:\n\nInput ichidagi qiymatni oling.\n\nUni localStorage.setItem yordamida \"foydalanuvchiIsmi\" kaliti ostida saqlang.\n\n<h1> ichidagi matnni o'sha ismga o'zgartiring.\n\n\"O'chirish\" tugmasi bosilganda:\n\nlocalStorage.removeItem yordamida ismni xotiradan o'chiring.\n\n<h1> ichidagi matnni qaytadan \"Ism kiritilmagan\" holatiga keltiring.",
        "requirements": "📋 Vazifa sharti:\nFoydalanuvchi o'z ismini kiritib \"Eslab qol\" tugmasini bossa, ism xotiraga yozilishi va sahifa necha marta yangilansa ham ekran tepasida o'sha ism turishi kerak. \"Xotirani o'chirish\" tugmasi bosilganda esa ism o'chib ketishi kerak.\n\nHTML sahifada bitta <h1> (ismni ko'rsatish uchun), bitta <input> (ism yozish uchun) va ikkita tugma (\"Eslab qol\" va \"O'chirish\") yarating.\n\nDastur boshida har doim LocalStorage-ni tekshiring: agar xotirada ism bo'lsa, uni darhol <h1> ichiga yozib qo'ying.\n\n\"Eslab qol\" tugmasi bosilganda:\n\nInput ichidagi qiymatni oling.\n\nUni localStorage.setItem yordamida \"foydalanuvchiIsmi\" kaliti ostida saqlang.\n\n<h1> ichidagi matnni o'sha ismga o'zgartiring.\n\n\"O'chirish\" tugmasi bosilganda:\n\nlocalStorage.removeItem yordamida ismni xotiradan o'chiring.\n\n<h1> ichidagi matnni qaytadan \"Ism kiritilmagan\" holatiga keltiring.",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): localStorage.setItem(\"foydalanuvchiIsmi\", kiritilganIsm);  let saqlanganIsm = localStorage.getItem(\"foydalanuvchiIsmi\");  if (saqlanganIsm) { sarlavha.innerText = saqlanganIsm; }  localStorage.removeItem(\"foydalanuvchiIsmi\");",
        "deadline_days": 3,
    },
    13: {
        "title": "Loyiha maqsadi: map, filter va find metodlarini real obyeklar massivi ustida ishlatishni o'rganish.",
        "description": "📋 Vazifa sharti:\nSizda onlayn do'kondagi mahsulotlar massivi bor. Kod orqali quyidagi 3 ta vazifani bajaring:\n\nJavaScript\nlet mahsulotlar = [\n    { id: 1, nomi: \"Telefon\", narxi: 4000000, kategoriya: \"Elektronika\" },\n    { id: 2, nomi: \"Ko'ylak\", narxi: 300000, kategoriya: \"Kiyim\" },\n    { id: 3, nomi: \"Noutbuk\", narxi: 8000000, kategoriya: \"Elektronika\" },\n    { id: 4, nomi: \"Tufli\", narxi: 500000, kategoriya: \"Kiyim\" }\n];\nSaralash (filter yordamida): Faqat \"Kiyim\" kategoriyasiga tegishli bo'lgan mahsulotlarni ajratib, yangi massivga oling va konsolga chiqaring.\n\nQidirish (find yordamida): Id raqami 3 ga teng bo'lgan mahsulotni qidirib toping va uning faqat nomini konsolga chiqaring.\n\nO'zgartirish (map yordamida): Do'konda aksiya e'lon qilindi va barcha mahsulotlarning narxi 20% ga arzonlashdi. Barcha mahsulotlarning narxini 20% ga kamaytirib (ya'ni asl narxini 0.8 ga ko'paytirib), yangi yangilangan mahsulotlar massivini hosil qiling va konsolga chiqaring.",
        "requirements": "📋 Vazifa sharti:\nSizda onlayn do'kondagi mahsulotlar massivi bor. Kod orqali quyidagi 3 ta vazifani bajaring:\n\nJavaScript\nlet mahsulotlar = [\n    { id: 1, nomi: \"Telefon\", narxi: 4000000, kategoriya: \"Elektronika\" },\n    { id: 2, nomi: \"Ko'ylak\", narxi: 300000, kategoriya: \"Kiyim\" },\n    { id: 3, nomi: \"Noutbuk\", narxi: 8000000, kategoriya: \"Elektronika\" },\n    { id: 4, nomi: \"Tufli\", narxi: 500000, kategoriya: \"Kiyim\" }\n];\nSaralash (filter yordamida): Faqat \"Kiyim\" kategoriyasiga tegishli bo'lgan mahsulotlarni ajratib, yangi massivga oling va konsolga chiqaring.\n\nQidirish (find yordamida): Id raqami 3 ga teng bo'lgan mahsulotni qidirib toping va uning faqat nomini konsolga chiqaring.\n\nO'zgartirish (map yordamida): Do'konda aksiya e'lon qilindi va barcha mahsulotlarning narxi 20% ga arzonlashdi. Barcha mahsulotlarning narxini 20% ga kamaytirib (ya'ni asl narxini 0.8 ga ko'paytirib), yangi yangilangan mahsulotlar massivini hosil qiling va konsolga chiqaring.",
        "technologies": "🛠 Loyiha uchun ishlatiladigan kodlar (G'ishtchalar): let kiyimlar = mahsulotlar.filter(function(p) { return p.kategoriya === \"Kiyim\"; });  let topilgan = mahsulotlar.find(function(p) { return p.id === 3; });  let yangiNarxlar = mahsulotlar.map(function(p) { p.narx = p.narx * 0.8; return p; });",
        "deadline_days": 3,
    },
    14: {
        "title": "1-Loyiha: \"Avtomatik Hisoblagich\" (Counter)",
        "description": "Shart: Sahifada bitta son (boshida 0) va bitta \"Oshirish (+1)\" tugmasi bo'lsin. Tugma har bosilganda son 1 taga oshsin va bu qiymat LocalStorage-ga saqlab borilsin. Sayt yangilanganda (Refresh boʻlganda) hisob nolga qaytib ketmay, xotiradagi oxirgi qolgan sondan davom etsin.",
        "requirements": "Shart: Sahifada bitta son (boshida 0) va bitta \"Oshirish (+1)\" tugmasi bo'lsin. Tugma har bosilganda son 1 taga oshsin va bu qiymat LocalStorage-ga saqlab borilsin. Sayt yangilanganda (Refresh boʻlganda) hisob nolga qaytib ketmay, xotiradagi oxirgi qolgan sondan davom etsin.",
        "technologies": "",
        "deadline_days": 3,
    },
}


LESSONS = [
    {
        "order": 0, "title": "Javascript asoslari",
        "text": L0_TEXT, "code": L0_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da ekran o'rtasiga faqat ogohlantirish yoki xabar beruvchi oyna chiqarish uchun qaysi buyruqdan foydalanamiz?",
                "description": "JavaScript-da ekran o'rtasiga faqat ogohlantirish yoki xabar beruvchi oyna chiqarish uchun qaysi buyruqdan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "alert",
            },
            {
                "exercise_type": "text_input",
                "title": "let va const kalit so'zlarining eng asosiy farqi nimada?",
                "description": "let va const kalit so'zlarining eng asosiy farqi nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "let yordamida yaratilgan o'zgaruvchi ichidagi ma'lumotni keyinchalik o'zgartirsa bo'ladi. const yordamida yaratilgan o'zgaruvchi esa o'zgarmas hisoblanadi, uning qiymatini qayta o'zgartirib bo'lmaydi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Qo'shtirnoq ichiga olingan har qanday harf, so'z yoki gap dasturlashda qaysi ma'lumot turiga (Data Type) kiradi?",
                "description": "Qo'shtirnoq ichiga olingan har qanday harf, so'z yoki gap dasturlashda qaysi ma'lumot turiga (Data Type) kiradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "String (Matn) ma'lumot turiga kiradi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Foydalanuvchidan ismini yoki yoshini so'rab, undan klaviaturadan biron bir ma'lumot yozib kiritishini talab qiladigan oyna qaysi buyruq orqali ochiladi?",
                "description": "Foydalanuvchidan ismini yoki yoshini so'rab, undan klaviaturadan biron bir ma'lumot yozib kiritishini talab qiladigan oyna qaysi buyruq orqali ochiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "prompt",
            },
            {
                "exercise_type": "text_input",
                "title": "let va const kalit so'zlarining eng asosiy farqi nimada?",
                "description": "let va const kalit so'zlarining eng asosiy farqi nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "let yordamida yaratilgan o'zgaruvchi ichidagi ma'lumotni keyinchalik o'zgartirsa bo'ladi. const yordamida yaratilgan o'zgaruvchi esa o'zgarmas hisoblanadi, uning qiymatini qayta o'zgartirib bo'lmaydi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Foydalanuvchidan ismini yoki yoshini so'rab, undan klaviaturadan biron bir ma'lumot yozib kiritishini talab qiladigan oyna qaysi buyruq orqali ochiladi?",
                "description": "Foydalanuvchidan ismini yoki yoshini so'rab, undan klaviaturadan biron bir ma'lumot yozib kiritishini talab qiladigan oyna qaysi buyruq orqali ochiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "prompt",
            },
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da ekran o'rtasiga faqat ogohlantirish yoki xabar beruvchi oyna chiqarish uchun qaysi buyruqdan foydalanamiz?",
                "description": "JavaScript-da ekran o'rtasiga faqat ogohlantirish yoki xabar beruvchi oyna chiqarish uchun qaysi buyruqdan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "alert",
            },
            {
                "exercise_type": "text_input",
                "title": "Qo'shtirnoq ichiga olingan har qanday harf, so'z yoki gap dasturlashda qaysi ma'lumot turiga (Data Type) kiradi?",
                "description": "Qo'shtirnoq ichiga olingan har qanday harf, so'z yoki gap dasturlashda qaysi ma'lumot turiga (Data Type) kiradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "String (Matn) ma'lumot turiga kiradi.",
            },
        ],
    },
    {
        "order": 1, "title": "if,else",
        "text": L1_TEXT, "code": L1_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            mc("Konsolda quyidagi kod nima chiqaradi?\n`let chiroq = \"sariq\"; if (chiroq === \"yashil\") console.log(\"yur\"); else if (chiroq === \"sariq\") console.log(\"kut\"); else console.log(\"to'xta\");`",
               ["yur", "kut", "to'xta", "Hech narsa"],
               "B",
               explanation='chiroq === "sariq" → true → else if bloki ishlaydi. else if true bo\'lganda qolgan shartlar tekshirilmaydi.',
               diff="Easy", pts=2),
            mc("`if (kun = \"yakshanba\")` — bu qator nima qiladi?",
               ["kun o'zgaruvchisini \"yakshanba\" qiymatiga aylantiradi va doim true qaytaradi",
                "kun va \"yakshanba\" ni solishtiradi",
                "Sintaksis xatosi (SyntaxError)",
                "Hech narsa qilmaydi"],
               "A",
               hint='= — o\'zlashtirish; === — solishtirish.',
               explanation='Bitta = o\'zlashtirish: kun ga "yakshanba" yoziladi. Natija "truthy", shart har doim true. Solishtirish uchun === ishlatiladi.',
               diff="Medium", pts=3),
            mc("Quyidagilardan qaysilari TO'G'RI taqqoslash operatorlari?",
               ["===", "!==", ">=", "<=", "=<", "<>"],
               "A,B,C,D", multi=True,
               hint='=< va <> — JavaScript da yo\'q.',
               diff="Medium", pts=3),
            dd("`let ball = 85;` bo'lganda, JS shu kodda qaysi tartibda harakat qiladi?",
               ["`if (ball >= 90)` tekshiriladi → false",
                "`else if (ball >= 80)` tekshiriladi → true",
                "console.log(\"B\") ishga tushadi",
                "Qolgan `else if` va `else` bloklar tekshirilmaydi"],
               explanation='Birinchi true topilganda qolganlari tashlanadi — bu if-else if zanjirining asosiy qoidasi.',
               diff="Medium", pts=3),
            ti("`5 === \"5\"` va `5 == \"5\"` — bu ikkisi nimani qaytaradi va NIMA UCHUN farqlanadi?",
               "5 === \"5\" → false. 5 == \"5\" → true. Farqi: === (qat'iy tenglik) ham qiymatni "
               "ham TURni solishtiradi: 5 (number) va \"5\" (string) — turlari turlicha, shuning "
               "uchun false. == (yumshoq tenglik) avval turlarni avtomatik aylantiradi (type "
               "coercion) — \"5\" ni number 5 ga aylantirib, keyin solishtiradi → true. "
               "Bu xavfli, chunki kutilmagan natijalar beradi (masalan 0 == \"\" → true, "
               "[] == false → true). Professional kodda har doim === ishlating — turni ham "
               "tekshirib turing. == ni faqat aniq sabab bilan ishlating.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 2, "title": "3-Dars: Mantiqiy operatorlar va Switch-case",
        "text": L2_TEXT, "code": L2_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Bitta qatorda mantiqiy \"VA\" (&&) va mantiqiy \"YOKI\" (||) operatorlari aralash kelganda, ustunlik (ustuvorlik) qaysi biriga beriladi, ya'ni birinchi bo'lib qaysi biri bajariladi?",
                "description": "Bitta qatorda mantiqiy \"VA\" (&&) va mantiqiy \"YOKI\" (||) operatorlari aralash kelganda, ustunlik (ustuvorlik) qaysi biriga beriladi, ya'ni birinchi bo'lib qaysi biri bajariladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "Birinchi bo'lib mantiqiy \"VA\" (&&) operatori bajariladi",
            },
            {
                "exercise_type": "text_input",
                "title": "Mantiqiy \"YOKI\" (||) operatorida yozilgan bir nechta shartlardan kamida bittasi rost (true) bo'lsa, umumiy javob nima chiqadi?",
                "description": "Mantiqiy \"YOKI\" (||) operatorida yozilgan bir nechta shartlardan kamida bittasi rost (true) bo'lsa, umumiy javob nima chiqadi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "Rost (true)",
            },
            {
                "exercise_type": "text_input",
                "title": "Mantiqiy \"VA\" (&&) operatori to'g'ri javob qaytarishi uchun undan chapdagi va o'ngdagi ikkala shart ham qanday bo'lishi kerak?",
                "description": "Mantiqiy \"VA\" (&&) operatori to'g'ri javob qaytarishi uchun undan chapdagi va o'ngdagi ikkala shart ham qanday bo'lishi kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "Ikkala shart ham majburiy ravishda rost (true) bo'lishi kerak.",
            },
            {
                "exercise_type": "text_input",
                "title": "Mantiqiy inkor (!) operatori o'zidan keyin kelgan rost (true) qiymatni qaysi qiymatga aylantirib qo'yadi?",
                "description": "Mantiqiy inkor (!) operatori o'zidan keyin kelgan rost (true) qiymatni qaysi qiymatga aylantirib qo'yadi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Yolg'on (false) qiymatga",
            },
            {
                "exercise_type": "text_input",
                "title": "switch-case ichidagi har bir case oxiriga break yozish nima uchun muhim?",
                "description": "switch-case ichidagi har bir case oxiriga break yozish nima uchun muhim?",
                "is_multiple_select": False,
                "hint": "break — switch'dan chiqib ketish buyrug'i.",
                "explanation": "break bo'lmasa dastur keyingi case'lar ichiga ham 'tushib ketadi' (fall-through) va kerak bo'lmagan kodlarni ham bajaradi.",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "break yozilmasa, dastur shu case'dan keyingi case'larga ham tushib ketib (fall-through) ularning kodini ham bajaradi. break esa switch'dan darhol chiqib ketishni ta'minlaydi.",
            },
            {
                "exercise_type": "text_input",
                "title": "switch-case operatorida agar berilgan variantlarning (case) hech biri qiymatga to'g'ri kelmasa, qaysi blok ishga tushadi?",
                "description": "switch-case operatorida agar berilgan variantlarning (case) hech biri qiymatga to'g'ri kelmasa, qaysi blok ishga tushadi?",
                "is_multiple_select": False,
                "hint": "if-else'dagi else'ga o'xshash blok.",
                "explanation": "default bloki — switch ichidagi 'else' rolini bajaradi: hech qaysi case mos kelmaganda ishlaydi.",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "default bloki",
            },
        ],
    },
    {
        "order": 3, "title": "1-Takrorlash Bloki (1, 2 va 3-Darslar bo'yicha)",
        "text": L3_TEXT, "code": L3_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da qiymati keyinchalik mutlaqo oʻzgarmaydigan, yaʼni oʻzgarmas qilib eʼlon qilinadigan oʻzgaruvchi qaysi kalit soʻz orqali yaratiladi?",
                "description": "JavaScript-da qiymati keyinchalik mutlaqo oʻzgarmaydigan, yaʼni oʻzgarmas qilib eʼlon qilinadigan oʻzgaruvchi qaysi kalit soʻz orqali yaratiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "const kalit soʻzi orqali",
            },
            {
                "exercise_type": "text_input",
                "title": "Mantiqiy \"YOKI\" (||) operatorida yozilgan bir nechta shartlardan kamida bittasi rost (true) boʻlsa, umumiy javob nima chiqadi?",
                "description": "Mantiqiy \"YOKI\" (||) operatorida yozilgan bir nechta shartlardan kamida bittasi rost (true) boʻlsa, umumiy javob nima chiqadi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "true (Rost)",
            },
            {
                "exercise_type": "text_input",
                "title": "if va else zanjiriga yana qoʻshimcha uchinchi yoki toʻrtinchi shartlarni kiritmoqchi boʻlsak, qaysi kalit soʻzlar birikmasidan foydalanamiz?",
                "description": "if va else zanjiriga yana qoʻshimcha uchinchi yoki toʻrtinchi shartlarni kiritmoqchi boʻlsak, qaysi kalit soʻzlar birikmasidan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "else if",
            },
            {
                "exercise_type": "text_input",
                "title": "switch-case operatorida agar berilgan variantlarning (case) hech biri toʻgʻri kelmasa, eng oxirida qaysi blok avtomatik ishga tushadi?",
                "description": "switch-case operatorida agar berilgan variantlarning (case) hech biri toʻgʻri kelmasa, eng oxirida qaysi blok avtomatik ishga tushadi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "default bloki",
            },
            {
                "exercise_type": "text_input",
                "title": "Dasturda let x = \"10\"; (matn) va let y = 10; (son) berilgan. Agar biz if (x === y) deb tekshirsak, shart bajariladimi yoki yoʻqmi? Nima uchun?",
                "description": "Dasturda let x = \"10\"; (matn) va let y = 10; (son) berilgan. Agar biz if (x === y) deb tekshirsak, shart bajariladimi yoki yoʻqmi? Nima uchun?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "Bajarilmaydi (shart xato boʻladi). Chunki qatʼiy tenglik (===) operatori qiymat bilan birga ularning maʼlumot turini ham tekshiradi. Bizda esa biri matn, biri son.",
            },
        ],
    },
    {
        "order": 4, "title": "for va while.",
        "text": L4_TEXT, "code": L4_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "multiple_choice",
                "title": "for sikli quyidagi qaysi qismlarga ega?",
                "description": "for sikli quyidagi qaysi qismlarga ega?",
                "options": ["boshlang'ich qiymat (let i = 0)", "shart (i < 10)", "qadam (i++)", "javob (return)"],
                "correct_answers": "A,B,C",
                "is_multiple_select": True,
                "hint": "for sikli 3 qismdan iborat — bittasi yetishmaydi.",
                "explanation": "for siklining 3 qismi: init, condition, step. 'return' funksiyaga tegishli.",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "multiple_choice",
                "title": "for (let i = 1; i <= 5; i++) sikli necha marta ishlaydi?",
                "description": "for (let i = 1; i <= 5; i++) sikli necha marta ishlaydi?",
                "options": ["4 marta", "5 marta", "6 marta", "Cheksiz"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "i 1, 2, 3, 4, 5 qiymatlarini olib chiqadi (5 ham kiradi chunki <=).",
                "explanation": "1 dan 5 gacha barcha sonlar — jami 5 ta iteratsiya.",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "multiple_choice",
                "title": "break va continue farqi nima?",
                "description": "break va continue farqi nima?",
                "options": ["break sikldan butunlay chiqadi, continue joriy iteratsiyani o'tkazib yuboradi", "continue sikldan chiqadi, break iteratsiyani o'tkazib yuboradi", "Ikkalasi bir xil narsa qiladi", "break faqat for da, continue faqat while da ishlaydi"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Birortasi loop ni butunlay to'xtatadi, ikkinchisi shu iteratsiyani 'tashlab ketadi'.",
                "explanation": "break — chiqish, continue — keyingi iteratsiyaga o'tish.",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "drag_and_drop",
                "title": "1 dan 10 gacha sonlar yig'indisini hisoblovchi for sikli qadamlarini tartiblang",
                "description": "1 dan 10 gacha sonlar yig'indisini hisoblovchi for sikli qadamlarini tartiblang",
                "drag_items": ["let yigindi = 0;", "for (let i = 1; i <= 10; i++) {", "    yigindi = yigindi + i;", "}", "console.log(yigindi);"],
                "correct_order": ["let yigindi = 0;", "for (let i = 1; i <= 10; i++) {", "    yigindi = yigindi + i;", "}", "console.log(yigindi);"],
                "is_multiple_select": False,
                "hint": "Avval yig'uvchi o'zgaruvchini yarating, keyin sikl ichida qo'shing, oxirida natijani chiqaring.",
                "explanation": "Bu — klassik accumulator pattern. Natija 55 bo'ladi.",
                "difficulty_level": "Medium",
                "points": 3,
            },
            {
                "exercise_type": "multiple_choice",
                "title": "while sikli qachon to'xtaydi?",
                "description": "while sikli qachon to'xtaydi?",
                "options": ["Shart false bo'lganda yoki break ishga tushganda", "Faqat break ishga tushganda", "Aniq sonli iteratsiyadan keyin", "Hech qachon"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Cheksiz sikldan ehtiyot bo'ling — bu eng ko'p uchraydigan xato.",
                "explanation": "while siklining sharti har iteratsiyadan oldin tekshiriladi.",
                "difficulty_level": "Easy",
                "points": 2,
            },
            {
                "exercise_type": "text_input",
                "title": "Cheksiz sikl (infinite loop) nima va undan qanday qutulish kerak?",
                "description": "Cheksiz sikl (infinite loop) nima va undan qanday qutulish kerak?",
                "expected_answer": "Cheksiz sikl — shart hech qachon false bo'lmaganida yoki break ishlamasligida yuz beradi. Misol: while (i < 10) — agar i o'sib bormasa, sikl to'xtamaydi va brauzer qotib qoladi. Undan qutulish uchun: 1) sikl ichida shartga ta'sir qiluvchi o'zgaruvchini o'zgartirish (i++), 2) muqobil chiqish sharti bilan break ishlatish, 3) brauzer sekinlashganda Stop tugmasini bosish.",
                "is_multiple_select": False,
                "hint": "Cheksiz sikl — yangi dasturchilar ko'p uchratadigan muammo.",
                "explanation": "Sikl shartini har doim ichkaridagi kod o'zgartirishi kerak — aks holda u abadiy ishlaydi.",
                "difficulty_level": "Hard",
                "points": 4,
            },
        ],
    },
    {
        "order": 5, "title": "5-Dars: Massivlar (Arrays) — Ma'lumotlar to'plami",
        "text": L5_TEXT, "code": L5_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Massiv ichidagi elementlar har doim nechchi sonidan boshlab raqamlanadi (indekslanadi)?",
                "description": "Massiv ichidagi elementlar har doim nechchi sonidan boshlab raqamlanadi (indekslanadi)?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "0 (nol) sonidan boshlab",
            },
            {
                "exercise_type": "text_input",
                "title": "Massiv ichida jami nechta element borligini, ya'ni uning uzunligini aniqlash uchun massiv nomidan keyin qaysi xususiyat yoziladi?",
                "description": "Massiv ichida jami nechta element borligini, ya'ni uning uzunligini aniqlash uchun massiv nomidan keyin qaysi xususiyat yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": ".length xususiyati.",
            },
            {
                "exercise_type": "text_input",
                "title": "Massivning eng oxiriga yangi ma'lumot qo'shish uchun qaysi maxsus metoddan (buyruqdan) foydalaniladi?",
                "description": "Massivning eng oxiriga yangi ma'lumot qo'shish uchun qaysi maxsus metoddan (buyruqdan) foydalaniladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "push() metodi",
            },
            {
                "exercise_type": "text_input",
                "title": "pop() va shift() metodlarining bir-biridan asosiy farqi nimada?",
                "description": "pop() va shift() metodlarining bir-biridan asosiy farqi nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "pop() massivning eng oxiridagi elementni o'chiradi, shift() esa massivning eng boshidagi elementni o'chiradi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Agar for tsikli yordamida massiv elementlarini aylanib chiqmoqchi bo'lsak, tsiklning tugash shartida nega i <= massiv.length emas, balki i < massiv.length deb yozilishi kerak?",
                "description": "Agar for tsikli yordamida massiv elementlarini aylanib chiqmoqchi bo'lsak, tsiklning tugash shartida nega i <= massiv.length emas, balki i < massiv.length deb yozilishi kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "Chunki massiv indekslari 0 dan boshlangani uchun, eng oxirgi elementning indeksi massiv uzunligidan (.length dan) har doim bittaga kam bo'ladi. Agar <= qo'yilsa, dastur mavjud bo'lmagan indeksni qidirib undefined natija qaytaradi.",
            },
        ],
    },
    {
        "order": 6, "title": "6-Dars: Funksiyalar (Functions) — Kodlarni qayta ishlatish",
        "text": L6_TEXT, "code": L6_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da yangi funksiya yaratish (e'lon qilish) uchun qaysi kalit so'zdan foydalaniladi?",
                "description": "JavaScript-da yangi funksiya yaratish (e'lon qilish) uchun qaysi kalit so'zdan foydalaniladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "function kalit so'zidan",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya ichida hisoblangan natijani funksiyadan tashqariga, ya'ni asosiy kodga qaytarib berish uchun qaysi kalit so'z ishlatiladi?",
                "description": "Funksiya ichida hisoblangan natijani funksiyadan tashqariga, ya'ni asosiy kodga qaytarib berish uchun qaysi kalit so'z ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "return kalit so'zi",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya ichida return buyrug'idan keyin yozilgan har qanday kodlar ishga tushadimi yoki yo'qmi? Nima uchun?",
                "description": "Funksiya ichida return buyrug'idan keyin yozilgan har qanday kodlar ishga tushadimi yoki yo'qmi? Nima uchun?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Ishga tushmaydi. Chunki return buyrug'i bajarilishi bilan funksiya o'z faoliyatini butunlay to'xtatadi va ichkaridagi qolgan kodlarni o'qimaydi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya yaratishda qavs ichida yoziladigan o'zgaruvchi (Parametr) va funksiyani chaqirishda unga berib yuboriladigan aniq qiymat (Argument) o'rtasidagi farq nimada?",
                "description": "Funksiya yaratishda qavs ichida yoziladigan o'zgaruvchi (Parametr) va funksiyani chaqirishda unga berib yuboriladigan aniq qiymat (Argument) o'rtasidagi farq nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Parametr — bu funksiya ochilayotganda ichkarida ishlatish uchun tayyorlab qo'yiladigan vaqtinchalik o'zgaruvchi (shablon). Argument — funksiya amalda chaqirilayotganda o'sha parametr o'rniga yuboriladigan real ma'lumot (qiymat) hisoblanadi",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya yaratilgandan keyin u o'z-o'zidan ishlab ketadimi yoki uni ishga tushirish uchun maxsus harakat kerakmi?",
                "description": "Funksiya yaratilgandan keyin u o'z-o'zidan ishlab ketadimi yoki uni ishga tushirish uchun maxsus harakat kerakmi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "O'z-o'zidan ishlamaydi, uni nomi va qavslar yordamida chaqirish (masalan: funkisyaNomi()) kerak",
            },
        ],
    },
    {
        "order": 7, "title": "2-Takrorlash Bloki (4, 5 va 6-Darslar bo'yicha)",
        "text": L7_TEXT, "code": L7_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Massivning eng oxiriga yangi maʼlumot qo'shish uchun qaysi tayyor metod (buyruq) ishlatiladi?",
                "description": "Massivning eng oxiriga yangi maʼlumot qo'shish uchun qaysi tayyor metod (buyruq) ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "push() metodi",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya ichida hisoblangan natijani funksiyadan tashqariga, yaʼni asosiy kodga qaytarib berish uchun qaysi kalit soʻz yoziladi?",
                "description": "Funksiya ichida hisoblangan natijani funksiyadan tashqariga, yaʼni asosiy kodga qaytarib berish uchun qaysi kalit soʻz yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "return kalit soʻzi",
            },
            {
                "exercise_type": "text_input",
                "title": "while tsikli ichida sanovchi oʻzgaruvchini oshirib borish (masalan: i++) esdan chiqib qolsa, dasturda qanday muammo yuzaga keladi?",
                "description": "while tsikli ichida sanovchi oʻzgaruvchini oshirib borish (masalan: i++) esdan chiqib qolsa, dasturda qanday muammo yuzaga keladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "Dastur toʻxtamaydigan \"Abadiy tsikl\"ga (Infinite loop) tushib qoladi va brauzer qotib qoladi",
            },
            {
                "exercise_type": "text_input",
                "title": "Funksiya ochilayotganda qavs ichida yoziladigan vaqtinchalik shablon nomlar (Parametr) va funksiya chaqirilayotganda unga berib yuboriladigan aniq qiymatlar (Argument) oʻrtasidagi farq nimada?",
                "description": "Funksiya ochilayotganda qavs ichida yoziladigan vaqtinchalik shablon nomlar (Parametr) va funksiya chaqirilayotganda unga berib yuboriladigan aniq qiymatlar (Argument) oʻrtasidagi farq nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Parametr — funksiya ichida ishlatiladigan oʻzgaruvchi. Argument — oʻsha oʻzgaruvchi oʻrniga tashqaridan yuborilgan real maʼlumot.",
            },
        ],
    },
    {
        "order": 8, "title": "7-Dars: Obyektlar (Objects)",
        "text": L8_TEXT, "code": L8_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da obyektlar qaysi qavslar yordamida yaratiladi?",
                "description": "JavaScript-da obyektlar qaysi qavslar yordamida yaratiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "Figurali qavslar {} yordamida",
            },
            {
                "exercise_type": "text_input",
                "title": "Obyekt ichidagi metod (funksiya) o'zi joylashgan obyektning boshqa xususiyatlarini (masalan, ismini yoki yoshini) ishlatishi uchun qaysi maxsus kalit so'zdan foydalanishi shart?",
                "description": "Obyekt ichidagi metod (funksiya) o'zi joylashgan obyektning boshqa xususiyatlarini (masalan, ismini yoki yoshini) ishlatishi uchun qaysi maxsus kalit so'zdan foydalanishi shart?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "this kalit so'zidan",
            },
            {
                "exercise_type": "text_input",
                "title": "Obyekt ichidagi biror xususiyatni (qiymatni) o'qib olish yoki konsolga chiqarish uchun qaysi belgi (operator) dan foydalanamiz?",
                "description": "Obyekt ichidagi biror xususiyatni (qiymatni) o'qib olish yoki konsolga chiqarish uchun qaysi belgi (operator) dan foydalanamiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "Nuqta . belgisidan (masalan: obyekt.xususiyat)",
            },
            {
                "exercise_type": "text_input",
                "title": "Obyekt ichida e'lon qilingan funksiya dasturlashda nima deb ataladi?",
                "description": "Obyekt ichida e'lon qilingan funksiya dasturlashda nima deb ataladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "Metod (Method)",
            },
            {
                "exercise_type": "text_input",
                "title": "Massivlar (Arrays) va Obyektlar (Objects) o'rtasidagi asosiy mantiqiy farq nimada? Qachon massiv, qachon obyekt ishlatgan ma'qul?",
                "description": "Massivlar (Arrays) va Obyektlar (Objects) o'rtasidagi asosiy mantiqiy farq nimada? Qachon massiv, qachon obyekt ishlatgan ma'qul?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "Massivlar — bir turdagi ma'lumotlarni (masalan, ismlar ruyxati, sonlar) shunchaki ketma-ketlik va tartib (indeks) bo'yicha saqlash uchun ishlatiladi. Obyektlar esa bitta real narsaning har xil turdagi xususiyatlarini (masalan, bitta foydalanuvchining ismi, yoshi, paroli) nomi (kaliti) bo'yicha guruhlab saqlash uchun ishlatiladi",
            },
        ],
    },
    {
        "order": 9, "title": "8-Dars: DOM bilan ishlash",
        "text": L9_TEXT, "code": L9_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "JavaScript orqali elementga fon rangi (background-color) bermoqchi bo'lsak, CSS-dagi chiziqcha o'rniga qanday yozish qoidasidan foydalanamiz? (Masalan, background-color qanday yoziladi?)",
                "description": "JavaScript orqali elementga fon rangi (background-color) bermoqchi bo'lsak, CSS-dagi chiziqcha o'rniga qanday yozish qoidasidan foydalanamiz? (Masalan, background-color qanday yoziladi?)",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "JavaScript-da CSS xususiyatlari chiziqchasiz, kichik-katta harflar zanjiri (CamelCase) orqali yoziladi. Shuning uchun u .style.backgroundColor ko'rinishida bo'ladi.",
            },
            {
                "exercise_type": "text_input",
                "title": "HTML-da bitta elementga berilgan maxsus id nomi orqali o'sha elementni JavaScript-da tutib olish uchun qaysi buyruq yoziladi?",
                "description": "HTML-da bitta elementga berilgan maxsus id nomi orqali o'sha elementni JavaScript-da tutib olish uchun qaysi buyruq yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "document.getElementById(\"id_nomi\")",
            },
            {
                "exercise_type": "text_input",
                "title": "Saytda foydalanuvchi tugmani bosganda (click bo'lganda) qandaydir kod ishga tushishi uchun funksiyani elementga qaysi metod orqali bog'laymiz?",
                "description": "Saytda foydalanuvchi tugmani bosganda (click bo'lganda) qandaydir kod ishga tushishi uchun funksiyani elementga qaysi metod orqali bog'laymiz?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "addEventListener() metodi orqali bog'laymiz (masalan: element.addEventListener(\"click\", funksiya))",
            },
            {
                "exercise_type": "text_input",
                "title": "HTML sahifadagi elementlarni JavaScript orqali boshqarish imkonini beruvchi brauzer modeli nima deb ataladi?",
                "description": "HTML sahifadagi elementlarni JavaScript orqali boshqarish imkonini beruvchi brauzer modeli nima deb ataladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "DOM (Document Object Model)",
            },
            {
                "exercise_type": "text_input",
                "title": "Tutib olingan biror HTML elementi ichidagi yozuvni (matnni) yangilash yoki o'zgartirish uchun qaysi xususiyatdan foydalaniladi?",
                "description": "Tutib olingan biror HTML elementi ichidagi yozuvni (matnni) yangilash yoki o'zgartirish uchun qaysi xususiyatdan foydalaniladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": ".innerText (yoki .textContent) xususiyatidan",
            },
        ],
    },
    {
        "order": 10, "title": "9-Dars: HTML elementlarini dinamik yaratish va o'chirish",
        "text": L10_TEXT, "code": L10_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Sahifadagi biror elementni (masalan, eski matn yoki rasm) butunlay yo'q qilib, o'chirib tashlash uchun qaysi qisqa metod chaqiriladi?",
                "description": "Sahifadagi biror elementni (masalan, eski matn yoki rasm) butunlay yo'q qilib, o'chirib tashlash uchun qaysi qisqa metod chaqiriladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": ".remove() metodi",
            },
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da elementga CSS klassini shunchaki matn ko'rinishida emas, balki xavfsiz va toza usulda qo'shish uchun element so'zidan keyin qanday buyruqlar zanjiri yoziladi?",
                "description": "JavaScript-da elementga CSS klassini shunchaki matn ko'rinishida emas, balki xavfsiz va toza usulda qo'shish uchun element so'zidan keyin qanday buyruqlar zanjiri yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "element.classList.add(\"klass_nomi\") ko'rinishida yoziladi.",
            },
            {
                "exercise_type": "text_input",
                "title": "JavaScript-da noldan boshlab mutlaqo yangi HTML elementi (masalan, <div> yoki <p>) yaratish uchun qaysi buyruq ishlatiladi?",
                "description": "JavaScript-da noldan boshlab mutlaqo yangi HTML elementi (masalan, <div> yoki <p>) yaratish uchun qaysi buyruq ishlatiladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "document.createElement(\"teg_nomi\")",
            },
            {
                "exercise_type": "text_input",
                "title": "Xotirada yaratilgan yangi HTML elementini sahifadagi biror bir ota elementning ichiga, eng oxirgi a'zo qilib joylashtiradigan metod nomi nima?",
                "description": "Xotirada yaratilgan yangi HTML elementini sahifadagi biror bir ota elementning ichiga, eng oxirgi a'zo qilib joylashtiradigan metod nomi nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "appendChild() metodi",
            },
        ],
    },
    {
        "order": 11, "title": "3-Takrorlash Bloki (7, 8 va 9-Darslar bo'yicha)",
        "text": L11_TEXT, "code": L11_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Obyekt ichida eʼlon qilingan va unga tegishli boʻlgan funksiyalar dasturlashda nima deb ataladi?",
                "description": "Obyekt ichida eʼlon qilingan va unga tegishli boʻlgan funksiyalar dasturlashda nima deb ataladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "Metod (Method)",
            },
            {
                "exercise_type": "text_input",
                "title": "HTML sahifadagi bitta elementni uning id nomi orqali JavaScript-da tutib olish uchun qaysi buyruq yoziladi?",
                "description": "HTML sahifadagi bitta elementni uning id nomi orqali JavaScript-da tutib olish uchun qaysi buyruq yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "document.getElementById(\"id_nomi\")",
            },
            {
                "exercise_type": "text_input",
                "title": "Obyekt ichidagi metod (funksiya) oʻzi joylashgan obyektning boshqa xususiyatlarini (masalan, ismi yoki narxini) ishlatishi uchun qaysi maxsus kalit soʻzdan foydalanishi shart?",
                "description": "Obyekt ichidagi metod (funksiya) oʻzi joylashgan obyektning boshqa xususiyatlarini (masalan, ismi yoki narxini) ishlatishi uchun qaysi maxsus kalit soʻzdan foydalanishi shart?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "this kalit soʻzidan",
            },
            {
                "exercise_type": "text_input",
                "title": "Xotirada document.createElement() orqali yangi yaratilgan element sahifada paydo boʻlishi uchun uni qaysi metod yordamida ota element ichiga joylashtirishimiz kerak?",
                "description": "Xotirada document.createElement() orqali yangi yaratilgan element sahifada paydo boʻlishi uchun uni qaysi metod yordamida ota element ichiga joylashtirishimiz kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "appendChild() metodi yordamida",
            },
            {
                "exercise_type": "text_input",
                "title": "Saytda mavjud boʻlgan biror elementni .remove() metodi yordamida oʻchirib tashlaganimizda, u faqat ekrandan yashirinadimi yoki HTML strukturasidan (DOM daraxtidan) butunlay yoʻqolib ketadimi?",
                "description": "Saytda mavjud boʻlgan biror elementni .remove() metodi yordamida oʻchirib tashlaganimizda, u faqat ekrandan yashirinadimi yoki HTML strukturasidan (DOM daraxtidan) butunlay yoʻqolib ketadimi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "HTML strukturasidan (DOM dan) butunlay oʻchib ketadi. Uni qayta tiklab boʻlmaydi, faqat qaytadan noldan yaratish mumkin",
            },
        ],
    },
    {
        "order": 12, "title": "10-Dars: LocalStorage",
        "text": L12_TEXT, "code": L12_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Dasturdagi obyekt yoki massivni LocalStorage-ga xavfsiz saqlash uchun uni matn ko'rinishiga o'tkazuvchi JSON buyrug'i qanday yoziladi?",
                "description": "Dasturdagi obyekt yoki massivni LocalStorage-ga xavfsiz saqlash uchun uni matn ko'rinishiga o'tkazuvchi JSON buyrug'i qanday yoziladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "JSON.stringify(obyekt_yoki_massiv) ko'rinishida yoziladi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Sayt birinchi marta ochilganda LocalStorage ichi bo'sh bo'ladi. Agar biz JSON.parse(localStorage.getItem(\"ro'yxat\")) kodini ishlatsak, xatolik (error) bermasligi uchun qanday chora ko'rish kerak?",
                "description": "Sayt birinchi marta ochilganda LocalStorage ichi bo'sh bo'ladi. Agar biz JSON.parse(localStorage.getItem(\"ro'yxat\")) kodini ishlatsak, xatolik (error) bermasligi uchun qanday chora ko'rish kerak?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "Mantiqiy \"YOKI\" (||) operatori orqali default qiymat berib ketish kerak. Masalan: JSON.parse(localStorage.getItem(\"ro'yxat\")) || []. Shunda xotira bo'sh bo'lsa, dastur xato bermay, bo'sh massivni ([]) qabul qilib ketaveradi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Brauzer yopib yoqilsa ham sayt ma'lumotlarini eslab qolishga xizmat qiladigan brauzer ichki xotirasi nima deb ataladi?",
                "description": "Brauzer yopib yoqilsa ham sayt ma'lumotlarini eslab qolishga xizmat qiladigan brauzer ichki xotirasi nima deb ataladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "LocalStorage",
            },
            {
                "exercise_type": "text_input",
                "title": "LocalStorage xotirasiga yangi ma'lumot yozish (saqlash) uchun qaysi metoddan foydalaniladi?",
                "description": "LocalStorage xotirasiga yangi ma'lumot yozish (saqlash) uchun qaysi metoddan foydalaniladi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "localStorage.setItem() metodi",
            },
            {
                "exercise_type": "text_input",
                "title": "LocalStorage o'z ichiga qanday turdagi ma'lumotlarni qabul qiladi? Unda son yoki massivlarni asl holicha saqlab bo'ladimi?",
                "description": "LocalStorage o'z ichiga qanday turdagi ma'lumotlarni qabul qiladi? Unda son yoki massivlarni asl holicha saqlab bo'ladimi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "Faqat matn (string) turidagi ma'lumotlarni qabul qiladi. Son, massiv yoki obyektlarni asl holicha saqlab bo'lmaydi, ularni matnga o'tkazish shart.",
            },
        ],
    },
    {
        "order": 13, "title": "11-Dars: Massivlarning qidiruv va o'zgarish metodlari",
        "text": L13_TEXT, "code": L13_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "Agar find() metodi massiv ichidan biz qidirgan shartga mos keladigan hech qanday element topa olmasa, dastur natija sifatida nima qaytaradi?",
                "description": "Agar find() metodi massiv ichidan biz qidirgan shartga mos keladigan hech qanday element topa olmasa, dastur natija sifatida nima qaytaradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "undefined qiymat qaytaradi.",
            },
            {
                "exercise_type": "text_input",
                "title": "Massivning har bir elementini aylanib chiqib, ularni o'zgartirgan holda yangi massiv ochib beruvchi metod nomi nima?",
                "description": "Massivning har bir elementini aylanib chiqib, ularni o'zgartirgan holda yangi massiv ochib beruvchi metod nomi nima?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "map()  metodi",
            },
            {
                "exercise_type": "text_input",
                "title": "filter() metodi o'ziga berilgan shartga mos keladigan elementlarni topsa, natijani qanday ko'rinishda qaytaradi?",
                "description": "filter() metodi o'ziga berilgan shartga mos keladigan elementlarni topsa, natijani qanday ko'rinishda qaytaradi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "Shartga mos kelgan barcha elementlardan iborat yangi massiv (array) ko'rinishida.",
            },
            {
                "exercise_type": "text_input",
                "title": "filter() va find() metodlarining asosiy mantiqiy farqi nimada?",
                "description": "filter() va find() metodlarining asosiy mantiqiy farqi nimada?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 3,
                "expected_answer": "filter() shartga mos keladigan barcha elementlarni massiv qilib qaytaradi. find() esa shartga mos keladigan eng birinchi uchragan bitta elementning o'zini (qiymatini yoki obyektini) qaytaradi va qolganlarini tekshirib o'tirmaydi.",
            },
            {
                "exercise_type": "text_input",
                "title": "map() yoki filter() metodlari ishlatilganda, dastlabki (asl) massivning ichidagi ma'lumotlar o'zgarib ketadimi yoki yo'qmi?",
                "description": "map() yoki filter() metodlari ishlatilganda, dastlabki (asl) massivning ichidagi ma'lumotlar o'zgarib ketadimi yoki yo'qmi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Yo'q, o'zgarmaydi. Bu metodlar asl massivga tegmagan holda, mutlaqo yangi massiv yaratib beradi.",
            },
        ],
    },
    {
        "order": 14, "title": "📝 Maxsus Takrorlash Bloki (10 va 11-Darslar bo'yicha)",
        "text": L14_TEXT, "code": L14_CODE, "lang": "javascript",
        "video": "",
        "exercises": [
            {
                "exercise_type": "text_input",
                "title": "LocalStorage brauzer xotirasiga matn koʻrinishidagi maʼlumotni saqlash (setItem) va uni qayta oʻqib olish (getItem) uchun qanday juftlik (shakl) dan foydalanadi?",
                "description": "LocalStorage brauzer xotirasiga matn koʻrinishidagi maʼlumotni saqlash (setItem) va uni qayta oʻqib olish (getItem) uchun qanday juftlik (shakl) dan foydalanadi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 1,
                "expected_answer": "\"Kalit va Qiymat\" (Key and Value) juftligidan foydalanadi",
            },
            {
                "exercise_type": "text_input",
                "title": "map() metodi massiv elementlari ustida biror amal bajarib boʻlgach, natijani qayerga qaytaradi? Asl massiv oʻzgarib ketadimi?",
                "description": "map() metodi massiv elementlari ustida biror amal bajarib boʻlgach, natijani qayerga qaytaradi? Asl massiv oʻzgarib ketadimi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Easy",
                "points": 2,
                "expected_answer": "Natijani mutlaqo yangi massivga yuklab qaytaradi. Asl (eski) massiv esa oʻzgarmasdan, dastlabki holatida qoladi",
            },
            {
                "exercise_type": "text_input",
                "title": "LocalStorage-dan JSON.parse() buyrugʻisiz, shunchaki localStorage.getItem() orqali massivni oʻqib olsak nima sodir boʻladi va u bilan nega ishlab boʻlmaydi?",
                "description": "LocalStorage-dan JSON.parse() buyrugʻisiz, shunchaki localStorage.getItem() orqali massivni oʻqib olsak nima sodir boʻladi va u bilan nega ishlab boʻlmaydi?",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Medium",
                "points": 4,
                "expected_answer": "Massiv shunchaki oddiy matn (string) boʻlib qaytadi (Masalan: \"[1,2,3]\" koʻrinishida). Matn boʻlib qolgani uchun unga massiv metodlarini (push, pop, map) qoʻllab boʻlmaydi. Uni massiv holiga keltirish uchun mantiqiy \"tarjimon\" yaʼni JSON.parse() shart",
            },
            {
                "exercise_type": "text_input",
                "title": "Agar filter() metodi massiv ichidan biz bergan shartga mos keladigan birorta ham element topa olmasa, natija sifatida nima qaytaradi? (Masalan, musbat sonlar ichidan manfiy sonni qidirganda)",
                "description": "Agar filter() metodi massiv ichidan biz bergan shartga mos keladigan birorta ham element topa olmasa, natija sifatida nima qaytaradi? (Masalan, musbat sonlar ichidan manfiy sonni qidirganda)",
                "is_multiple_select": False,
                "hint": "",
                "explanation": "",
                "difficulty_level": "Hard",
                "points": 5,
                "expected_answer": "Mutlaqo boʻsh massiv ([]) qaytaradi (find() metodiga oʻxshab undefined qaytarmaydi)",
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
            print(f"Course {COURSE['title']!r} already exists (id={existing.id}). Use refresh_javascript_text.py to update.")
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
