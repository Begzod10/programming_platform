"""Seed the "JavaScript: Keyingi Bosqich" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_javascript_next_level.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: graduates of the "Javascript" basics course.
Skips variables/loops/arrays/objects basics and jumps straight into idiomatic
modern JS: arrow functions, destructuring, array iterators, closures,
async/await + fetch, ES6 classes and a localStorage TODO capstone.
Language: Uzbek content with Russian section labels. Each lesson uses the
WIN-FIRST shape: BLOKA 1/2/3 hands-on hook -> deliberate-error -> theory ->
"Bu darsdan keyin siz bilasizki" wrap.
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


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "JavaScript: Keyingi Bosqich",
    "description": (
        "JavaScript asoslarini tugatganlar uchun: arrow funksiyalar, destructuring, "
        "massiv iteratorlari (map/filter/reduce), closures, this/call/apply/bind, "
        "ES6 modullar, Promiselar, async/await, fetch API va chuqurroq class'lar. "
        "Har bir modul oxirida loyiha. Maqsad — endi siz 'modern JavaScript' yozasiz."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 7,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson content placeholders — filled in by subsequent edits.
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Arrow funksiyalar, destructuring va spread/rest</h2>

<pre class="mermaid">
flowchart LR
    OLD["function f(a,b){return a+b}"] -->|=>| ARROW["(a,b) => a+b"]
    OBJ["{ism, yosh}"] -->|destructuring| VARS["const {ism, yosh} = obj"]
    ARR["[1,2,3]"] -->|spread| CALL["f(...arr)"]
    PARAMS["...args"] -->|rest| TUPLE["argumentlar massivi"]
</pre>

<p>3 ta belgi — <code>=&gt;</code>, <code>{ }</code>, <code>...</code> — sizning JS kodingiz ko'rinishini tubdan o'zgartiradi. Endi siz <code>function</code> kalit so'zini deyarli yozmaysiz va dict/array'lardan kerakli qiymatni bitta qatorga ajratib olasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>
<p>F12 -&gt; Console oching va sinab ko'ring.</p>

<h4>BLOKA 1 — Arrow funksiya</h4>
<pre><code>// Eski uslub
function qosh(a, b) {
    return a + b;
}

// Arrow
const qosh = (a, b) =&gt; a + b;

console.log(qosh(3, 4));     // 7

// Bir argument — qavslar shart emas
const ikkilash = x =&gt; x * 2;

// Tana bir qatordan ortiq bo'lsa — { } va return
const salom = ism =&gt; {
    const xabar = `Salom, ${ism}!`;
    return xabar;
};</code></pre>

<h4>BLOKA 2 — Destructuring</h4>
<pre><code>// Obyektdan
const foydalanuvchi = { ism: "Ali", yosh: 21, email: "ali@ya.ru" };
const { ism, yosh } = foydalanuvchi;
console.log(ism, yosh);              // Ali 21

// Default qiymat va yangi nom
const { ism: name, kasb = "dev" } = foydalanuvchi;
console.log(name, kasb);             // Ali dev

// Massivdan
const [birinchi, ikkinchi] = [10, 20, 30];
console.log(birinchi, ikkinchi);     // 10 20

// Funksiya argumentini destructure
const tasvir = ({ ism, yosh }) =&gt; `${ism} — ${yosh} yosh`;
console.log(tasvir(foydalanuvchi));</code></pre>

<h4>BLOKA 3 — Spread va rest</h4>
<pre><code>// Spread — yoyish
const a = [1, 2, 3];
const b = [4, 5];
const birga = [...a, ...b, 100];           // [1,2,3,4,5,100]

const obj1 = { x: 1, y: 2 };
const obj2 = { y: 99, z: 3 };
const final = { ...obj1, ...obj2 };        // { x:1, y:99, z:3 }

// Rest — yig'ish
const eng_kattasi = (...sonlar) =&gt; Math.max(...sonlar);
console.log(eng_kattasi(3, 7, 2, 9, 4));    // 9

// Tuple split
const [boshi, ...qolgani] = [10, 20, 30, 40];
console.log(boshi);                          // 10
console.log(qolgani);                        // [20, 30, 40]</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const tugma = document.querySelector("#bosish");

tugma.addEventListener("click", function() {
    console.log(this);     // tugma elementi
});

tugma.addEventListener("click", () =&gt; {
    console.log(this);     // ???
});</code></pre>
<p><strong>Natija:</strong> ikkinchi <code>this</code> — tugma EMAS. Arrow funksiyada <code>this</code> mavjud emas — u atrofdagi (lexical) <code>this</code> ni meros qiladi. Brauzerda — <code>window</code>. <strong>Qoida:</strong> event handler yoki metod ichida <code>this</code> kerak bo'lsa — <code>function</code>. Aks holda — arrow.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Arrow vs function — farqlar</h4>
<table>
<tr><th>Arrow <code>=&gt;</code></th><th>function</th></tr>
<tr><td>Qisqaroq sintaksis</td><td>Uzunroq</td></tr>
<tr><td><code>this</code> meros — lexical</td><td><code>this</code> chaqiruvga qarab</td></tr>
<tr><td><code>arguments</code> yo'q</td><td><code>arguments</code> mavjud</td></tr>
<tr><td><code>new</code> bilan ishlatib bo'lmaydi</td><td>Constructor bo'lishi mumkin</td></tr>
<tr><td>Hoisting yo'q</td><td>Hoist qilinadi (declarationda)</td></tr>
</table>

<h4>2. Arrow sintaksisining 4 shakli</h4>
<pre><code>// 1) Bir argument, ifoda
x =&gt; x * 2

// 2) Bir necha argument, ifoda
(a, b) =&gt; a + b

// 3) Tana { } bilan
(a, b) =&gt; {
    const sum = a + b;
    return sum;
}

// 4) Obyekt qaytarish — qavs ichida { } yashirin
const yarat = (id) =&gt; ({ id, vaqt: Date.now() });
// ({ ... }) shart — aks holda { } funksiya tanasi deb tushuniladi</code></pre>

<h4>3. Destructuring nyuanslari</h4>
<pre><code>// Default qiymat + nom o'zgartirish
const { ism: name = "Mehmon", yosh = 0 } = foydalanuvchi;

// Chuqurroq (nested)
const javob = { user: { ism: "Ali", manzil: { shahar: "Toshkent" } } };
const { user: { manzil: { shahar } } } = javob;
console.log(shahar);    // Toshkent

// Massiv'ning o'rtasini o'tkazib yuborish
const [birinchi, , uchinchi] = [1, 2, 3];
console.log(birinchi, uchinchi);    // 1 3

// Funksiya parametrida default
const f = ({ a = 1, b = 2 } = {}) =&gt; a + b;
console.log(f());                    // 3
console.log(f({ a: 10 }));            // 12</code></pre>

<h4>4. Spread/rest — qachon qaysi?</h4>
<table>
<tr><th>Holat</th><th>Qaysi</th><th>Misol</th></tr>
<tr><td>Massiv/obyekt'ni ochish (chaqiruv)</td><td>spread</td><td><code>f(...arr)</code>, <code>[...a, ...b]</code></td></tr>
<tr><td>Funksiya parametri (yig'ish)</td><td>rest</td><td><code>(...args) =&gt; ...</code></td></tr>
<tr><td>Destructuring (qolganlari)</td><td>rest</td><td><code>const [a, ...qolgan] = arr</code></td></tr>
<tr><td>Obyekt birlashtirish</td><td>spread</td><td><code>{ ...a, ...b }</code></td></tr>
</table>

<h4>5. Real foydalanish — immutable yangilash</h4>
<pre><code>// State ni o'zgartirmasdan yangilash (React stilida)
const eski = { ism: "Ali", yosh: 21, sevimli: ["python"] };
const yangi = {
    ...eski,
    yosh: 22,                          // bu maydonni almashtir
    sevimli: [...eski.sevimli, "js"],  // massivni "kengaytirish"
};
console.log(eski.yosh);    // 21 — eski o'zgarmadi
console.log(yangi.yosh);   // 22</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Arrow <code>=&gt;</code> — qisqaroq, lexical <code>this</code></li>
<li>Event handler ichida <code>this</code> kerak bo'lsa — arrow EMAS, <code>function</code></li>
<li>Destructuring — obyekt/massivdan kerakli qiymatni bitta qatorda ajratish</li>
<li>Spread <code>...</code> — ochish, rest <code>...</code> — yig'ish (kontekstga qarab)</li>
<li><code>{ ...eski, x: yangi }</code> — immutable yangilash patterni</li>
</ul>
"""

L1_CODE = """\
// ─── Arrow, destructuring, spread/rest — to'liq sweep ─────────────────────

// 1) Arrow — barcha shakllar
const ikkilash = x => x * 2;
const qosh = (a, b) => a + b;
const yarat = (id, nom) => ({ id, nom, vaqt: Date.now() });
const ko_p = (a, b) => {
    const natija = a * b;
    return natija;
};

console.log(ikkilash(5));
console.log(qosh(3, 4));
console.log(yarat(1, "olma"));

// 2) Default parametrlar
const salom = (ism, salom_so_zi = "Salom") => `${salom_so_zi}, ${ism}!`;
console.log(salom("Ali"));
console.log(salom("Vali", "Assalomu alaykum"));

// 3) Obyektdan destructuring
const foydalanuvchi = {
    ism: "Ali",
    yosh: 21,
    manzil: { shahar: "Toshkent", indeks: 100000 },
    teglar: ["dev", "js"],
};

const { ism, yosh } = foydalanuvchi;
console.log(ism, yosh);

// Nested + default + nom o'zgartirish
const {
    ism: name,
    kasb = "dev",
    manzil: { shahar },
    teglar: [birinchi_teg],
} = foydalanuvchi;
console.log(name, kasb, shahar, birinchi_teg);

// 4) Funksiya argumentini destructure
const tasvir = ({ ism, yosh, kasb = "noma'lum" }) =>
    `${ism} (${yosh} yosh) — ${kasb}`;
console.log(tasvir(foydalanuvchi));

// 5) Massivdan
const [birinchi, ikkinchi, ...qolgani] = [10, 20, 30, 40, 50];
console.log(birinchi, ikkinchi, qolgani);

// O'rtasini o'tkazib yuborish
const [bosh, , uchinchi] = [1, 2, 3];
console.log(bosh, uchinchi);

// 6) Spread — array
const a = [1, 2, 3];
const b = [4, 5];
console.log([...a, ...b, 100]);
console.log(Math.max(...a, ...b));

// 7) Spread — obyekt
const defaults = { theme: "dark", lang: "uz", timeout: 30 };
const user = { lang: "en", verbose: true };
console.log({ ...defaults, ...user });

// 8) Rest — funksiya parametri
const eng_kattasi = (...sonlar) => {
    if (sonlar.length === 0) return null;
    return Math.max(...sonlar);
};
console.log(eng_kattasi(3, 7, 2, 9, 4));

// 9) Real misol — immutable update (React patterni)
const eski = { ism: "Ali", yosh: 21, sevimli: ["python"] };
const yangilangan = {
    ...eski,
    yosh: 22,
    sevimli: [...eski.sevimli, "js", "ts"],
};
console.log("Eski:", eski);
console.log("Yangi:", yangilangan);
console.log("Eski o'zgarmagan:", eski.yosh === 21);

// 10) Pipeline — talaba ballarini transformatsiya
const talabalar = [
    { ism: "Ali", ball: 87 },
    { ism: "Vali", ball: 54 },
    { ism: "Gulya", ball: 92 },
];

const tasvirlar = talabalar.map(({ ism, ball }) =>
    `${ism}: ${ball >= 70 ? "✅" : "❌"} ${ball}`,
);
console.log(tasvirlar);
"""

L2_TEXT = """\
<h2>Massiv iteratorlari — <code>map</code>, <code>filter</code>, <code>reduce</code>, <code>find</code></h2>

<pre class="mermaid">
flowchart LR
    ARR["[1,2,3,4,5]"] -->|map| TRANS["transformatsiya"]
    ARR -->|filter| F["shartga to'g'ri"]
    ARR -->|reduce| ACC["yagona qiymat"]
    ARR -->|find| FIRST["birinchi mos"]
    ARR -->|forEach| SIDE["yon ta'sir"]
</pre>

<p>Bu yetti metod — modern JS'ning yuragi. <code>for</code> sikli o'rniga deklarativ chain. Bir nechta operatsiyani zanjirga yig'ish — bitta o'qimli qator.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — map va filter zanjiri</h4>
<pre><code>const sonlar = [1, 2, 3, 4, 5, 6];

// Eski uslub — for sikli
const juftKvadratlar = [];
for (let i = 0; i &lt; sonlar.length; i++) {
    if (sonlar[i] % 2 === 0) {
        juftKvadratlar.push(sonlar[i] ** 2);
    }
}

// Modern — chain
const juftKvadratlar2 = sonlar
    .filter(x =&gt; x % 2 === 0)
    .map(x =&gt; x ** 2);

console.log(juftKvadratlar2);    // [4, 16, 36]</code></pre>

<h4>BLOKA 2 — reduce — yagona qiymatga yig'ish</h4>
<pre><code>const ballar = [85, 92, 78, 90];

// Yig'indi
const jami = ballar.reduce((acc, x) =&gt; acc + x, 0);
console.log(jami);     // 345

// O'rtacha
const o_rta = jami / ballar.length;

// Maksimal — Math.max bilan ham bo'ladi, lekin reduce ham
const eng_katta = ballar.reduce((a, b) =&gt; a &gt; b ? a : b);

// Sanab chiqish — har element nechta marta
const matnlar = ["olma", "olma", "non", "olma", "non", "sut"];
const son = matnlar.reduce((acc, m) =&gt; {
    acc[m] = (acc[m] || 0) + 1;
    return acc;
}, {});
console.log(son);    // { olma: 3, non: 2, sut: 1 }</code></pre>

<h4>BLOKA 3 — find, some, every</h4>
<pre><code>const talabalar = [
    { ism: "Ali", ball: 87 },
    { ism: "Vali", ball: 54 },
    { ism: "Gulya", ball: 92 },
];

// find — birinchi mos kelganini topadi (yoki undefined)
const a_lochi = talabalar.find(t =&gt; t.ball &gt;= 90);
console.log(a_lochi);    // { ism: 'Gulya', ball: 92 }

// some — biror bittasi mos keladimi (true/false)
const bor_yaxshi = talabalar.some(t =&gt; t.ball &gt;= 90);
console.log(bor_yaxshi);    // true

// every — hammasi mos keladimi
const hamma_o_tdi = talabalar.every(t =&gt; t.ball &gt;= 50);
console.log(hamma_o_tdi);    // true</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const sonlar = [1, 2, 3];

const ikkilangan = sonlar.map(x =&gt; {
    x * 2;
});

console.log(ikkilangan);    // ???</code></pre>
<p><strong>Natija:</strong> <code>[undefined, undefined, undefined]</code>. Arrow funksiya tanasi <code>{ }</code> bilan — <code>return</code> kerak. To'g'ri variantlar:</p>
<pre><code>const ikkilangan = sonlar.map(x =&gt; x * 2);          // ifoda — return yashirin
const ikkilangan2 = sonlar.map(x =&gt; { return x * 2; });  // tana — return aniq</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Asosiy metodlar — qachon qaysi?</h4>
<table>
<tr><th>Metod</th><th>Qaytaradi</th><th>Qachon</th></tr>
<tr><td><code>map</code></td><td>Yangi massiv (bir xil uzunlik)</td><td>Har elementni transformatsiya</td></tr>
<tr><td><code>filter</code></td><td>Yangi massiv (qisqaroq)</td><td>Shartga to'g'ri keladiganlar</td></tr>
<tr><td><code>reduce</code></td><td>Yagona qiymat</td><td>Yig'ish, agregatsiya</td></tr>
<tr><td><code>find</code></td><td>Element yoki undefined</td><td>Birinchi mos kelgani</td></tr>
<tr><td><code>findIndex</code></td><td>Indeks yoki -1</td><td>Birinchi mosning indeksi</td></tr>
<tr><td><code>some</code></td><td>true/false</td><td>Hech bo'lmasa bittasi</td></tr>
<tr><td><code>every</code></td><td>true/false</td><td>Hammasi</td></tr>
<tr><td><code>forEach</code></td><td>undefined</td><td>Faqat yon ta'sir (console.log)</td></tr>
</table>

<h4>2. Chain — zanjir</h4>
<pre><code>const top3 = talabalar
    .filter(t =&gt; t.ball &gt;= 70)              // o'tganlari
    .map(t =&gt; ({ ...t, harf: t.ball &gt;= 90 ? "A" : "B" }))
    .sort((a, b) =&gt; b.ball - a.ball)        // kamayuvchi
    .slice(0, 3);                            // birinchi 3 tasi</code></pre>
<p>Har metod yangi massiv qaytaradi — zanjirni davom ettirish mumkin. Lekin: 1000+ element bo'lsa, 5 ta chain = 5 marta to'liq sweep. Performance kerak bo'lsa, oddiy <code>for</code> tezroq.</p>

<h4>3. reduce — eng kuchli, eng murakkab</h4>
<pre><code>// Shakli:
arr.reduce((accumulator, currentValue, index, array) =&gt; {
    // ...
    return accumulator;
}, initialValue);   // initialValue muhim!</code></pre>
<ul>
<li><strong>accumulator</strong> — har iteratsiyada yig'ilgan qiymat</li>
<li><strong>currentValue</strong> — joriy element</li>
<li><strong>initialValue</strong> — boshlang'ich (0 yoki <code>{}</code> yoki <code>[]</code>)</li>
</ul>
<p>⚠️ initialValue bermasangiz, reduce <em>birinchi elementni</em> initialValue deb oladi va siklni 2-elementdan boshlaydi. Bo'sh massiv uchun esa TypeError.</p>

<h4>4. forEach vs map — eng ko'p adashtiriladigan</h4>
<table>
<tr><th>forEach</th><th>map</th></tr>
<tr><td>Hech narsa qaytarmaydi (undefined)</td><td>Yangi massiv qaytaradi</td></tr>
<tr><td>Yon ta'sir uchun (DOM, console)</td><td>Transformatsiya uchun</td></tr>
<tr><td>Zanjirga yaroqsiz</td><td>Chain qilish mumkin</td></tr>
<tr><td><code>break</code> ishlamaydi</td><td><code>break</code> ishlamaydi</td></tr>
</table>

<h4>5. Iterator metodlari va arrow funksiyalar — kombinatsiya</h4>
<pre><code>// Eng pythonic-ish JS — arrow + destructuring + chain
const top_a_lochilar = talabalar
    .filter(({ ball }) =&gt; ball &gt;= 90)
    .map(({ ism, ball }) =&gt; ({ ism, daraja: ball &gt;= 95 ? "ustun" : "yaxshi" }));</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>for</code> sikli kamdan-kam kerak — <code>map/filter/reduce</code> ko'pchilik holatda yetadi</li>
<li><code>reduce</code> ga doim <code>initialValue</code> bering — bug'larni oldini oladi</li>
<li>Arrow tana <code>{ }</code> bilan — <code>return</code> kerak; ifoda bilan — yashirin return</li>
<li>Chain — har metod yangi massiv qaytaradi, davom ettirish mumkin</li>
<li><code>forEach</code> — faqat yon ta'sir; transformatsiya uchun <code>map</code></li>
</ul>
"""

L2_CODE = """\
// ─── Massiv iteratorlari — to'liq sweep ──────────────────────────────────

const sonlar = [1, 5, -3, 8, -2, 11, 0, 7];

// 1) map — har elementni transformatsiya
console.log(sonlar.map(x => x * x));

// 2) filter — shartga to'g'ri keladiganlar
console.log(sonlar.filter(x => x > 0));

// 3) filter + map zanjiri
const musbat_kvadratlar = sonlar
    .filter(x => x > 0)
    .map(x => x * x);
console.log("Musbat kvadratlar:", musbat_kvadratlar);

// 4) reduce — yig'indi
const jami = sonlar.reduce((acc, x) => acc + x, 0);
console.log("Jami:", jami);

// 5) reduce — group by (eng kuchli pattern)
const matnlar = ["olma", "olma", "non", "olma", "non", "sut", "sut"];
const sanash = matnlar.reduce((acc, m) => {
    acc[m] = (acc[m] || 0) + 1;
    return acc;
}, {});
console.log("Sanash:", sanash);

// 6) reduce — eng katta sonni topish
const eng_katta = sonlar.reduce((a, b) => (a > b ? a : b));
console.log("Eng katta:", eng_katta);

// 7) Real ma'lumot — talabalar
const talabalar = [
    { ism: "Ali",     ball: 87, kasb: "dev" },
    { ism: "Vali",    ball: 54, kasb: "designer" },
    { ism: "Gulya",   ball: 92, kasb: "dev" },
    { ism: "Doniyor", ball: 68, kasb: "qa" },
    { ism: "Karim",   ball: 95, kasb: "dev" },
];

// find — birinchi yuqori ballini topish
const a_lo = talabalar.find(t => t.ball >= 90);
console.log("Birinchi A'lo:", a_lo);

// some / every
console.log("Bor a'lo:",      talabalar.some(t => t.ball >= 90));
console.log("Hammasi >50:",   talabalar.every(t => t.ball > 50));

// 8) Chain — TOP 3 dev
const top3_dev = talabalar
    .filter(t => t.kasb === "dev")
    .sort((a, b) => b.ball - a.ball)
    .slice(0, 3);
console.log("TOP 3 dev:", top3_dev);

// 9) reduce — kasb bo'yicha guruhlash
const kasb_guruhlari = talabalar.reduce((acc, t) => {
    if (!acc[t.kasb]) acc[t.kasb] = [];
    acc[t.kasb].push(t.ism);
    return acc;
}, {});
console.log("Kasb guruhlari:", kasb_guruhlari);

// 10) reduce — kasb bo'yicha o'rta ball
const o_rta_per_kasb = Object.entries(kasb_guruhlari).map(([kasb, ismlar]) => {
    const ballar = ismlar.map(ism =>
        talabalar.find(t => t.ism === ism).ball,
    );
    const o_rta = ballar.reduce((a, b) => a + b, 0) / ballar.length;
    return { kasb, o_rta };
});
console.log("O'rta per kasb:", o_rta_per_kasb);

// 11) Mahsulotlar misoli
const mahsulotlar = [
    { nom: "Olma", narx: 12000, soni: 5 },
    { nom: "Non",  narx: 4000,  soni: 12 },
    { nom: "Sut",  narx: 9000,  soni: 3 },
];

const jami_summa = mahsulotlar.reduce(
    (acc, m) => acc + m.narx * m.soni,
    0,
);
console.log("Jami:", jami_summa.toLocaleString(), "so'm");
"""

L3_TEXT = """\
<h2>Template literallar va string metodlari</h2>

<pre class="mermaid">
flowchart LR
    OLD["'Salom, ' + ism + '!'"] -->|backtick| TPL["`Salom, ${ism}!`"]
    TPL -->|ko'p qatorli| MULTI["yangi qator saqlanadi"]
    STR["matn"] -->|metodlar| TRIM["trim, split, includes, replaceAll, padStart"]
    TAG["tag`...`"] -->|tagged template| CUSTOM["maxsus parsing"]
</pre>

<p><strong>Template literal</strong> — backtick (<code>`</code>) bilan yozilgan string. Ichida ifoda <code>${...}</code>, ko'p qatorli matn, va hatto tagged template'lar. Hozir <code>"a" + b + "c"</code> deb yozish — eski.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Template literal asoslari</h4>
<pre><code>const ism = "Ali";
const yosh = 21;

// Eski uslub
const xabar1 = "Salom, " + ism + "! Sizga " + yosh + " yosh.";

// Modern — backtick (`)
const xabar2 = `Salom, ${ism}! Sizga ${yosh} yosh.`;

console.log(xabar2);

// Ichida hisob ham bo'ladi
const a = 5, b = 3;
console.log(`${a} + ${b} = ${a + b}`);    // 5 + 3 = 8

// Funksiya chaqiruvi
console.log(`KATTA: ${ism.toUpperCase()}`);    // KATTA: ALI</code></pre>

<h4>BLOKA 2 — Ko'p qatorli matn</h4>
<pre><code>// Eski uslub — \\n
const sms = "Salom!\\nIltimos, bizga qaytib oling.\\nRaxmat.";

// Modern — backtick saqlaydi
const xat = `Salom, ${ism}!

Bizning ofisga 2026-yil 15-iyul kuni keling.
Manzil: Toshkent shahar.

Hurmat bilan,
Jamoa`;

console.log(xat);    // qator ajratuvchilar saqlanadi</code></pre>

<h4>BLOKA 3 — String metodlari</h4>
<pre><code>const matn = "   Modern JavaScript juda kuchli!   ";

console.log(matn.trim());                  // bo'sh joylarni olib tashlaydi
console.log(matn.trim().toUpperCase());    // MODERN JAVASCRIPT JUDA KUCHLI!
console.log(matn.includes("JavaScript"));  // true
console.log(matn.startsWith("   Mo"));     // true
console.log(matn.replaceAll(" ", "_"));    // _ _ _ Modern_JavaScript_..._

// split va join — string &lt;-&gt; massiv
const teglar = "html,css,js,react";
const massiv = teglar.split(",");          // ["html", "css", "js", "react"]
const qaytarilgan = massiv.join(" | ");    // "html | css | js | react"

// padStart, padEnd — chiroyli formatlash
console.log("5".padStart(3, "0"));         // "005"
console.log("Ali".padEnd(10, "-"));         // "Ali-------"</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const ism = "Ali";

// Tirnoq bilan yozdik
const xabar = "Salom, ${ism}!";    // ⚠️
console.log(xabar);

// Backtick bilan
const xabar2 = `Salom, ${ism}!`;
console.log(xabar2);</code></pre>
<p><strong>Natija:</strong> birinchisi — <code>Salom, ${ism}!</code> (literal matn). Template literal FAQAT backtick <code>`</code> bilan ishlaydi. Oddiy <code>"</code> yoki <code>'</code> ichida <code>${...}</code> — oddiy belgilar.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Template literal — 4 qobiliyat</h4>
<table>
<tr><th>Qobiliyat</th><th>Sintaksis</th></tr>
<tr><td>O'zgaruvchi/ifoda</td><td><code>`${expr}`</code></td></tr>
<tr><td>Ko'p qatorli</td><td>backtick ichidagi har yangi qator saqlanadi</td></tr>
<tr><td>Tirnoqlar erkin</td><td><code>`"matn" va 'boshqa'`</code> ishlaydi</td></tr>
<tr><td>Tagged template</td><td><code>tag`...`</code> — pastda</td></tr>
</table>

<h4>2. Tez-tez kerak string metodlari</h4>
<table>
<tr><th>Metod</th><th>Misol</th></tr>
<tr><td><code>trim()</code></td><td>bo'sh joylarni olib tashlash</td></tr>
<tr><td><code>toLowerCase / toUpperCase</code></td><td>katta/kichik</td></tr>
<tr><td><code>includes(s)</code></td><td>ichida bormi (boolean)</td></tr>
<tr><td><code>startsWith / endsWith</code></td><td>boshi/oxiri</td></tr>
<tr><td><code>indexOf(s)</code></td><td>topilgan o'rin yoki -1</td></tr>
<tr><td><code>slice(a, b)</code></td><td>kesma</td></tr>
<tr><td><code>split(sep)</code></td><td>massivga</td></tr>
<tr><td><code>replace / replaceAll</code></td><td>almashtirish</td></tr>
<tr><td><code>padStart / padEnd</code></td><td>chap/o'ngdan to'ldirish</td></tr>
<tr><td><code>repeat(n)</code></td><td><code>"ab".repeat(3)</code> -&gt; "ababab"</td></tr>
</table>

<h4>3. <code>.replace</code> vs <code>.replaceAll</code></h4>
<pre><code>const s = "olma olma olma";

console.log(s.replace("olma", "non"));        // "non olma olma"  ⚠️
console.log(s.replace(/olma/g, "non"));        // "non non non"  (regex /g)
console.log(s.replaceAll("olma", "non"));      // "non non non"  (ES2021+)</code></pre>

<h4>4. Templates ichida funksiya chaqiruvi va tanlov</h4>
<pre><code>const ball = 87;
const xabar = `Sizning baholaringiz: ${
    ball &gt;= 90 ? "A'lo" :
    ball &gt;= 70 ? "Yaxshi" :
    "Qoniqarsiz"
}`;
console.log(xabar);    // "Sizning baholaringiz: Yaxshi"</code></pre>

<h4>5. Tagged template — qisqacha tanishish</h4>
<pre><code>function highlight(qismlar, ...qiymatlar) {
    return qismlar.reduce((acc, q, i) =&gt;
        acc + q + (qiymatlar[i] ? `[${qiymatlar[i]}]` : ""),
    "");
}

const ism = "Ali";
const yosh = 21;
console.log(highlight`Salom, ${ism}! Sizga ${yosh} yosh.`);
// "Salom, [Ali]! Sizga [21] yosh."</code></pre>
<p>Tagged template — <code>tag\`...\`</code> shaklida. Funksiya stringning bo'laklarini va qiymatlarini alohida oladi. SQL queries (sanitizatsiya), HTML render, i18n uchun foydali.</p>

<h4>6. Sonlarni formatlash — toLocaleString</h4>
<pre><code>const summa = 1500000;

console.log(summa);                                // 1500000
console.log(summa.toLocaleString());               // 1,500,000
console.log(summa.toLocaleString("uz-UZ"));         // 1 500 000
console.log(summa.toLocaleString("uz-UZ", {
    style: "currency",
    currency: "UZS",
}));                                                // 1 500 000 UZS</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Template literal — faqat backtick <code>`</code> bilan</li>
<li><code>${...}</code> ichida har qanday ifoda — funksiya, hisob, tanlov</li>
<li>Ko'p qatorli matn uchun backtick — <code>\\n</code> kerak emas</li>
<li><code>replaceAll</code> — barcha mos kelishlarni almashtiradi (ES2021+)</li>
<li><code>toLocaleString</code> — sonlar/sanalar uchun chiroyli format</li>
</ul>
"""

L3_CODE = """\
// ─── Template literallar va string metodlari ─────────────────────────────

// 1) Template literal asoslari
const ism = "Ali";
const yosh = 21;
const kasb = "frontend dev";

console.log(`Salom, ${ism}! ${yosh} yoshdagi ${kasb}.`);

// 2) Ichida ifoda — hisob va metod chaqirish
const ball = 87;
console.log(`Ball: ${ball}, daraja: ${ball >= 90 ? "A'lo" : ball >= 70 ? "Yaxshi" : "F"}`);
console.log(`Katta: ${ism.toUpperCase()} (${ism.length} ta harf)`);

// 3) Ko'p qatorli xat
const xat = `Salom, ${ism}!

Bu — sizning yutuqlaringizning oylik hisoboti:
  • Ball:   ${ball}
  • Kasb:   ${kasb}
  • Maqsad: 95+ ball

Hurmat bilan,
Jamoa`;
console.log(xat);

// 4) String metodlari — sweep
const matn = "   Modern JavaScript juda kuchli!   ";

console.log(matn.trim());
console.log(matn.trim().toLowerCase());
console.log(matn.includes("Java"));
console.log(matn.startsWith("   Modern"));
console.log(matn.endsWith("!   "));
console.log(matn.indexOf("Java"));
console.log(matn.slice(3, 9));                    // "Modern"
console.log(matn.replaceAll(" ", "_"));

// 5) split + join — matnni qayta tartiblash
const teglar = "html, css, js, react, vue";
const massiv = teglar.split(",").map(t => t.trim());
console.log(massiv);
console.log(massiv.join(" | "));

// 6) padStart, padEnd — jadval kabi formatlash
console.log("Ism".padEnd(15, ".") + "Ball");
console.log("".padEnd(20, "─"));

const talabalar = [
    { ism: "Ali",     ball: 87 },
    { ism: "Vali",    ball: 54 },
    { ism: "Gulya",   ball: 92 },
    { ism: "Doniyor", ball: 68 },
];

talabalar.forEach(t => {
    console.log(t.ism.padEnd(15, ".") + String(t.ball).padStart(3, "0"));
});

// 7) toLocaleString — sonlarni chiroyli
const summa = 1_500_000;
console.log(summa.toLocaleString("uz-UZ"));
console.log(summa.toLocaleString("uz-UZ", { style: "currency", currency: "UZS" }));
console.log((0.875).toLocaleString("uz-UZ", { style: "percent" }));

// 8) Tagged template — kichik HTML highlighter
function escape_html(s) {
    return String(s)
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}

function html(qismlar, ...qiymatlar) {
    return qismlar.reduce((acc, q, i) =>
        acc + q + (i < qiymatlar.length ? escape_html(qiymatlar[i]) : ""),
    "");
}

const xavfli = "<script>alert(1)</script>";
console.log(html`<p>Foydalanuvchi: ${xavfli}</p>`);
// <p>Foydalanuvchi: &lt;script&gt;alert(1)&lt;/script&gt;</p>

// 9) repeat va string yaratish
console.log("─".repeat(40));
console.log(" ".repeat(10) + "Yakuniy hisobot");
console.log("─".repeat(40));
"""

R1_TEXT = """\
<h2>🔁 R1 — Sotuvchi statistikasi (Modul 1 takrori)</h2>

<pre class="mermaid">
flowchart LR
    SAVDOS["savdolar array"] -->|destructuring| ITEMS["({sotuvchi, narx, ...})"]
    ITEMS -->|filter| F["filterlash"]
    F -->|map| TRANS["transformatsiya"]
    TRANS -->|reduce| AGG["agregatsiya"]
    AGG -->|template literal| OUT["chiroyli chiqish"]
</pre>

<p>Modul 1 ning 3 ta texnikasi: <strong>arrow + destructuring + spread/rest</strong>, <strong>massiv iteratorlari</strong>, <strong>template literallar</strong>. Vazifa: sotuvchilar savdolari ro'yxatidan TOP sotuvchini, kategoriya bo'yicha summalarni va chiroyli hisobotni chiqarish.</p>

<h3>🏆 5 daqiqada g'alaba — bitta katta misol</h3>

<pre><code>const savdolar = [
    { sotuvchi: "Ali",  mahsulot: "noutbuk",    narx: 12_000_000 },
    { sotuvchi: "Vali", mahsulot: "telefon",    narx: 5_500_000 },
    { sotuvchi: "Ali",  mahsulot: "klaviatura", narx: 450_000 },
    { sotuvchi: "Gulya","mahsulot": "monitor",  narx: 3_200_000 },
    { sotuvchi: "Vali", mahsulot: "noutbuk",    narx: 11_800_000 },
    { sotuvchi: "Ali",  mahsulot: "telefon",    narx: 6_200_000 },
];

// 1) Sotuvchilar to'plami — Set
const sotuvchilar = [...new Set(savdolar.map(s =&gt; s.sotuvchi))];

// 2) Har sotuvchi uchun jami — reduce
const jami_per_sot = savdolar.reduce((acc, { sotuvchi, narx }) =&gt; {
    acc[sotuvchi] = (acc[sotuvchi] || 0) + narx;
    return acc;
}, {});

// 3) TOP — sort + slice
const top = Object.entries(jami_per_sot)
    .sort(([, a], [, b]) =&gt; b - a)
    .slice(0, 3);

// 4) Hisobot — template literal
const hisobot = top
    .map(([ism, summa], i) =&gt;
        `${i + 1}. ${ism.padEnd(10)} ${summa.toLocaleString("uz-UZ")} so'm`,
    )
    .join("\\n");

console.log(hisobot);
</code></pre>

<h3>3 ta texnikani birga ko'rib chiqamiz</h3>

<h4>Arrow + destructuring + rest/spread</h4>
<ul>
<li><code>(acc, { sotuvchi, narx }) =&gt; ...</code> — destructure parametrda</li>
<li><code>[...new Set(arr)]</code> — Set'ni massivga ochish (takrorsiz)</li>
<li><code>{ ...obj, key: val }</code> — immutable yangilash</li>
</ul>

<h4>Massiv iteratorlari</h4>
<ul>
<li><code>map</code> — transformatsiya</li>
<li><code>filter</code> — shartga to'g'ri keladiganlar</li>
<li><code>reduce</code> — yagona qiymatga yig'ish (sum, group, count)</li>
<li><code>sort</code> — saralash (immutable emas! `.toSorted()` da bor)</li>
<li><code>find</code> / <code>some</code> / <code>every</code> — qidirish</li>
</ul>

<h4>Template literallar</h4>
<ul>
<li><code>`${ism}: ${narx}`</code> — interpolatsiya</li>
<li><code>`${ball &gt;= 90 ? "A" : "B"}`</code> — ifoda</li>
<li><code>padStart</code>, <code>padEnd</code>, <code>repeat</code> — formatlash</li>
<li><code>toLocaleString</code> — sonlar uchun chiroyli format</li>
</ul>

<h3>📌 Module 1 ni siz endi bilasiz</h3>
<ul>
<li>Modern JS — kichik <code>function</code>, ko'p arrow</li>
<li>Obyekt/massivdan kerakli qiymatni 1 qatorda destructure qilasiz</li>
<li><code>for</code> sikli — kamdan-kam; <code>map/filter/reduce</code> ko'pchilik holatda yetadi</li>
<li>Template literal — string konkatenatsiyani unutdik</li>
</ul>
"""

R1_CODE = """\
// ─── R1: Sotuvchi statistikasi to'liq misoli ──────────────────────────────

const savdolar = [
    { sotuvchi: "Ali",     mahsulot: "noutbuk",    narx: 12_000_000, miqdor: 1 },
    { sotuvchi: "Vali",    mahsulot: "telefon",    narx: 5_500_000,  miqdor: 2 },
    { sotuvchi: "Ali",     mahsulot: "klaviatura", narx: 450_000,    miqdor: 3 },
    { sotuvchi: "Gulya",   mahsulot: "monitor",    narx: 3_200_000,  miqdor: 1 },
    { sotuvchi: "Vali",    mahsulot: "noutbuk",    narx: 11_800_000, miqdor: 1 },
    { sotuvchi: "Ali",     mahsulot: "telefon",    narx: 6_200_000,  miqdor: 1 },
    { sotuvchi: "Doniyor", mahsulot: "monitor",    narx: 3_500_000,  miqdor: 2 },
];

// 1) Jami savdo summasi
const jami = savdolar.reduce((acc, { narx, miqdor }) => acc + narx * miqdor, 0);
console.log(`Jami savdo: ${jami.toLocaleString("uz-UZ")} so'm`);

// 2) Takrorlanmas sotuvchilar — Set
const sotuvchilar = [...new Set(savdolar.map(s => s.sotuvchi))].sort();
console.log("Sotuvchilar:", sotuvchilar);

// 3) Sotuvchi -> jami summa
const jami_per_sot = savdolar.reduce((acc, { sotuvchi, narx, miqdor }) => {
    acc[sotuvchi] = (acc[sotuvchi] || 0) + narx * miqdor;
    return acc;
}, {});
console.log("Per sotuvchi:", jami_per_sot);

// 4) TOP 3 sotuvchi
const top3 = Object.entries(jami_per_sot)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

console.log("\\n=== TOP 3 SOTUVCHI ===");
top3.forEach(([ism, summa], i) => {
    console.log(`${i + 1}. ${ism.padEnd(10)} ${summa.toLocaleString("uz-UZ").padStart(15)} so'm`);
});

// 5) Eng katta bitta savdo
const eng_qimmat = savdolar.reduce((a, b) => (a.narx > b.narx ? a : b));
console.log(`\\nEng qimmat: ${eng_qimmat.sotuvchi} — ${eng_qimmat.mahsulot} (${eng_qimmat.narx.toLocaleString("uz-UZ")} so'm)`);

// 6) Mahsulot bo'yicha guruhlash
const per_mahsulot = savdolar.reduce((acc, { mahsulot, narx, miqdor }) => {
    acc[mahsulot] = (acc[mahsulot] || 0) + narx * miqdor;
    return acc;
}, {});

console.log("\\nMahsulot bo'yicha:");
Object.entries(per_mahsulot)
    .sort(([, a], [, b]) => b - a)
    .forEach(([nom, summa]) => {
        console.log(`  ${nom.padEnd(12)} ${summa.toLocaleString("uz-UZ").padStart(15)} so'm`);
    });

// 7) Pipeline — kategoriya filterlash
const noutbuk_savdolar = savdolar
    .filter(s => s.mahsulot === "noutbuk")
    .map(({ sotuvchi, narx }) => ({ sotuvchi, narx_mln: narx / 1_000_000 }));

console.log("\\nNoutbuk savdolari (mln):", noutbuk_savdolar);

// 8) every / some
console.log("Hammasi 100k+:", savdolar.every(s => s.narx >= 100_000));
console.log("Bor 10M+:    ", savdolar.some(s => s.narx >= 10_000_000));

// 9) Hisobot — bitta katta template literal
const hisobot = `
═══════════════════════════════════════
       SAVDO HISOBOTI
═══════════════════════════════════════
Jami savdo:    ${jami.toLocaleString("uz-UZ")} so'm
Savdo soni:    ${savdolar.length} ta
O'rtacha:      ${Math.round(jami / savdolar.length).toLocaleString("uz-UZ")} so'm

TOP sotuvchi:  ${top3[0][0]} (${top3[0][1].toLocaleString("uz-UZ")} so'm)
═══════════════════════════════════════
`;
console.log(hisobot);
"""

L4_TEXT = """\
<h2>Closures — yopilmalar (eng kuchli JS tushunchasi)</h2>

<pre class="mermaid">
flowchart LR
    OUTER["tashqi funksiya"] -->|local vars| SCOPE["scope: count=0"]
    OUTER -->|qaytaradi| INNER["ichki funksiya"]
    INNER -->|hali ham ko'radi| SCOPE
    CALL["wrapper() chaqirilganda"] -->|count o'sadi| MEMO["holat saqlanadi"]
</pre>

<p><strong>Closure</strong> — ichki funksiya o'zining tashqi funksiyasi <em>scope</em>'iga kira oladi, hatto tashqi funksiya tugagandan keyin ham. Bu JS'ning "yashirin holati" (private state) yaratish, modullar va dekoratorlarning asosi. Bu bitta tushuncha sizni "yangi boshlovchi" dan "mid-level" ga olib chiqadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Eng oddiy closure: counter</h4>
<pre><code>function counterYarat() {
    let count = 0;            // tashqi funksiya scope'i

    return function() {
        count++;              // ichki funksiya count ni "ko'radi"
        return count;
    };
}

const counter = counterYarat();
console.log(counter());    // 1
console.log(counter());    // 2
console.log(counter());    // 3

// count bu yerda — qaerda? Tashqaridan ko'rinmaydi, lekin SAQLANGAN
// console.log(count);    // ReferenceError</code></pre>

<h4>BLOKA 2 — Private state — encapsulation</h4>
<pre><code>function hisobYarat(boshlangich = 0) {
    let pul = boshlangich;       // PRIVATE — tashqaridan ko'rinmaydi

    return {
        qoshish: (n) =&gt; { pul += n; return pul; },
        ayirish: (n) =&gt; { pul -= n; return pul; },
        qoldiq:  ()  =&gt; pul,
    };
}

const hisob = hisobYarat(100);
console.log(hisob.qoshish(50));    // 150
console.log(hisob.ayirish(30));    // 120
console.log(hisob.qoldiq());       // 120

// console.log(hisob.pul);     // undefined — tashqaridan kirish yo'q!</code></pre>

<h4>BLOKA 3 — Funksiya fabrikasi</h4>
<pre><code>function ko_paytiruvchi(k) {
    return (x) =&gt; x * k;
}

const ikkilash = ko_paytiruvchi(2);
const uchlash = ko_paytiruvchi(3);
const o_nlash = ko_paytiruvchi(10);

console.log(ikkilash(5));    // 10
console.log(uchlash(5));     // 15
console.log(o_nlash(5));     // 50</code></pre>
<p>Har <code>ko_paytiruvchi</code> chaqirig'i o'zining <code>k</code> ni "yopib oladi" — har biri alohida closure.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>const funksiyalar = [];

for (var i = 0; i &lt; 3; i++) {
    funksiyalar.push(function() {
        return i;
    });
}

console.log(funksiyalar[0]());    // ???
console.log(funksiyalar[1]());    // ???
console.log(funksiyalar[2]());    // ???</code></pre>
<p><strong>Natija:</strong> Hammasi <code>3</code>. Sabab: <code>var i</code> — function scope'li, butun sikl bitta <code>i</code> ni baham ko'radi. Funksiyalar chaqirilganda — sikl tugagan, <code>i = 3</code>. <strong>Yechim:</strong> <code>let i</code> — block scope, har iteratsiya alohida <code>i</code>:</p>
<pre><code>for (let i = 0; i &lt; 3; i++) {
    funksiyalar.push(() =&gt; i);
}
// Endi: 0, 1, 2</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Closure — ta'rif</h4>
<p>Funksiya <strong>+</strong> uning yaratilgan paytdagi scope. Funksiya "tug'ilgan joyini" yodida saqlaydi. Bu joydagi o'zgaruvchilar yashashda davom etadi, hatto tashqi funksiya tugaganidan keyin ham.</p>

<h4>2. Qachon closure ishlatiladi?</h4>
<ul>
<li><strong>Private state</strong> — class'siz "private" maydonlar (hozir <code>#</code> bor, lekin closure tarixiy)</li>
<li><strong>Funksiya fabrikasi</strong> — bir xil shaklli, lekin parametrli funksiyalar</li>
<li><strong>Dekorator</strong> — funksiyani o'rab kengaytirish (timing, retry, memoize)</li>
<li><strong>Event handler</strong> — element holatini yodda saqlash</li>
<li><strong>Modul pattern</strong> (eski) — ES6 modullar oldidan</li>
<li><strong>Debounce / throttle</strong> — vaqt belgisini saqlash</li>
</ul>

<h4>3. Real misol — debounce</h4>
<pre><code>function debounce(funk, kutish) {
    let timeoutId;           // closure ichidagi state

    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() =&gt; funk.apply(this, args), kutish);
    };
}

// Search input — har harf yozilganda emas, foydalanuvchi to'xtaganda
const qidirish = debounce((qatori) =&gt; {
    console.log(`Qidirilmoqda: ${qatori}`);
}, 300);

qidirish("p");
qidirish("py");
qidirish("pyt");
qidirish("pyth");
// Faqat oxirgi 300ms dan keyin "Qidirilmoqda: pyth" chiqadi</code></pre>

<h4>4. Memoize — natijani cache qilish</h4>
<pre><code>function memoize(funk) {
    const cache = new Map();   // har funksiya uchun ALOHIDA cache

    return function(...args) {
        const kalit = JSON.stringify(args);
        if (!cache.has(kalit)) {
            cache.set(kalit, funk(...args));
        }
        return cache.get(kalit);
    };
}

const sekinHisob = (n) =&gt; {
    console.log(`Hisoblanmoqda ${n}...`);
    return n * 2;
};

const tezHisob = memoize(sekinHisob);
tezHisob(5);    // "Hisoblanmoqda 5..." -> 10
tezHisob(5);    // 10 (cache'dan, log chiqmaydi)
tezHisob(3);    // "Hisoblanmoqda 3..." -> 6</code></pre>

<h4>5. var vs let vs const — scope farqi</h4>
<table>
<tr><th>Kalit so'z</th><th>Scope</th><th>Hoisting</th><th>Reassign</th></tr>
<tr><td><code>var</code></td><td>function</td><td>undefined sifatida</td><td>Ha</td></tr>
<tr><td><code>let</code></td><td>block</td><td>Temporal Dead Zone</td><td>Ha</td></tr>
<tr><td><code>const</code></td><td>block</td><td>Temporal Dead Zone</td><td>Yo'q</td></tr>
</table>
<p>Default: <code>const</code>. Faqat o'zgartirish kerak bo'lsa — <code>let</code>. <code>var</code> — eski, deyarli kerak emas.</p>

<h4>6. Closure va xotira — diqqat</h4>
<p>Closure tashqi scope'ni "ushlab turadi" — agar shu scope'da katta obyekt bo'lsa, u garbage collect bo'lmaydi. Memory leak ehtimoli. Yechim: closure tugagach reference'ni <code>null</code> qiling yoki kerak bo'lmagan o'zgaruvchini scope'dan chiqaring.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Closure — ichki funksiya + tashqi scope. Ichi tashqi'ga ko'ra oladi, aksincha emas.</li>
<li>Closure orqali private state yaratish — class'dan oldingi vaqtdagi idiom</li>
<li>Debounce, throttle, memoize — closure'siz yozib bo'lmaydi</li>
<li><code>var</code> + <code>for</code> sikli + closure — klassik bug. <code>let</code> ishlating</li>
<li>Har <code>function</code> chaqirig'i o'z scope'ini yaratadi — har closure alohida</li>
</ul>
"""

L4_CODE = """\
// ─── Closures — to'liq sweep ─────────────────────────────────────────────

// 1) Eng oddiy counter
function counterYarat() {
    let count = 0;
    return () => ++count;
}

const c1 = counterYarat();
const c2 = counterYarat();
console.log(c1(), c1(), c1());    // 1 2 3
console.log(c2());                 // 1 — alohida closure

// 2) Private state — class'siz encapsulation
function hisobYarat(boshlangich = 0) {
    let pul = boshlangich;
    let tarix = [];

    return {
        qoshish(n) {
            pul += n;
            tarix.push({ amal: "+", n, qoldiq: pul });
            return pul;
        },
        ayirish(n) {
            if (n > pul) throw new Error("Yetarli pul yo'q");
            pul -= n;
            tarix.push({ amal: "-", n, qoldiq: pul });
            return pul;
        },
        qoldiq()    { return pul; },
        tarixOl()   { return [...tarix]; },    // nusxa qaytaradi
    };
}

const hisob = hisobYarat(1000);
hisob.qoshish(500);
hisob.ayirish(200);
console.log(`Qoldiq: ${hisob.qoldiq()}`);
console.log("Tarix:", hisob.tarixOl());

// pul va tarix tashqaridan ko'rinmaydi — to'liq private
console.log("Maydon ko'rinadimi:", hisob.pul);   // undefined

// 3) Funksiya fabrikasi
const ko_paytiruvchi = (k) => (x) => x * k;

const [ikki, besh, o_n] = [2, 5, 10].map(ko_paytiruvchi);
console.log(ikki(7), besh(7), o_n(7));    // 14 35 70

// 4) Debounce
function debounce(funk, kutish) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => funk.apply(this, args), kutish);
    };
}

const log_d = debounce((s) => console.log(`Qidirilmoqda: ${s}`), 300);
log_d("p"); log_d("py"); log_d("pyt"); log_d("pyth");
// Faqat 300ms dan keyin oxirgisi chiqadi

// 5) Memoize
function memoize(funk) {
    const cache = new Map();
    return function (...args) {
        const k = JSON.stringify(args);
        if (cache.has(k)) {
            console.log(`(cache hit: ${k})`);
            return cache.get(k);
        }
        const natija = funk(...args);
        cache.set(k, natija);
        return natija;
    };
}

const sekinFib = (n) => (n < 2 ? n : sekinFib(n - 1) + sekinFib(n - 2));
const tezFib = memoize((n) => (n < 2 ? n : tezFib(n - 1) + tezFib(n - 2)));
console.log("Tez fib(30):", tezFib(30));

// 6) Klassik for-var bug
console.log("\\nvar bilan (bug):");
const fns_var = [];
for (var i = 0; i < 3; i++) {
    fns_var.push(() => i);
}
console.log(fns_var.map((f) => f()));    // [3, 3, 3]

console.log("let bilan (fix):");
const fns_let = [];
for (let j = 0; j < 3; j++) {
    fns_let.push(() => j);
}
console.log(fns_let.map((f) => f()));    // [0, 1, 2]

// 7) once — funksiyani faqat bir marta chaqirish
function once(funk) {
    let bajarildi = false;
    let natija;
    return function (...args) {
        if (!bajarildi) {
            bajarildi = true;
            natija = funk.apply(this, args);
        }
        return natija;
    };
}

const bittaSalom = once(() => {
    console.log("Salom! (faqat 1 marta)");
    return Math.random();
});
bittaSalom();
bittaSalom();
bittaSalom();    // birinchi marta natija qaytadi, faqat birinchisi log qiladi

// 8) Closure + setTimeout — timer
function timerYarat(soniya) {
    let qolgan = soniya;
    return new Promise((resolve) => {
        const interval = setInterval(() => {
            console.log(`Qolgan: ${qolgan}s`);
            qolgan--;
            if (qolgan < 0) {
                clearInterval(interval);
                resolve("Tugadi!");
            }
        }, 1000);
    });
}
// timerYarat(3).then(console.log);
"""

L5_TEXT = """\
<h2><code>this</code>, <code>call</code>, <code>apply</code>, <code>bind</code></h2>

<pre class="mermaid">
flowchart LR
    METHOD["obj.metod()"] -->|this = obj| THIS1["this -> obj"]
    LOOSE["const f = obj.metod; f()"] -->|this = undefined yoki window| LOST["this yo'qoldi"]
    CALL["f.call(obj, a, b)"] -->|this aniq| THIS2["this -> obj"]
    BIND["const bound = f.bind(obj)"] -->|doim shu obj| THIS3["this fixed"]
    ARROW["() => this"] -->|lexical| OUTER["tashqi this"]
</pre>

<p><code>this</code> — JS'ning eng adashtiruvchi tushunchasi. Chaqiruv joyiga qarab boshqacha bo'ladi. 5 ta qoidani bilsangiz — bu boshqa sirli emas. <code>call</code>/<code>apply</code>/<code>bind</code> — <code>this</code>'ni AYNI majburlash vositalari.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — <code>this</code> ning 5 ta shakli</h4>
<pre><code>// 1) Metod chaqiruvi — this = chaqirilgan obyekt
const it = {
    nom: "Rex",
    gapir() { console.log(`${this.nom}: vov!`); }
};
it.gapir();                    // "Rex: vov!"

// 2) Funksiya chaqiruvi — this = undefined (strict) yoki window
function oddiy() { console.log(this); }
oddiy();                       // strict: undefined; loose: window

// 3) Yo'qotilgan metod — this YO'QOLADI
const gap = it.gapir;
// gap();                       // TypeError: this.nom — undefined

// 4) Arrow — lexical this (tashqi scope'dan)
const arrow_fn = () =&gt; console.log(this);
arrow_fn();                    // tashqi this (modulda — undefined)

// 5) new bilan — this = yangi obyekt
function Hayvon(nom) {
    this.nom = nom;
}
const mushuk = new Hayvon("Mursik");
console.log(mushuk.nom);       // "Mursik"</code></pre>

<h4>BLOKA 2 — call, apply</h4>
<pre><code>function tasvirla(yosh, kasb) {
    console.log(`${this.nom}, ${yosh} yosh, ${kasb}`);
}

const ali = { nom: "Ali" };

// call — argumentlarni alohida beradi
tasvirla.call(ali, 21, "dev");        // "Ali, 21 yosh, dev"

// apply — argumentlarni MASSIV sifatida beradi
tasvirla.apply(ali, [21, "dev"]);     // "Ali, 21 yosh, dev"

// Modern: spread bilan call — apply o'rniga
const args = [21, "dev"];
tasvirla.call(ali, ...args);</code></pre>

<h4>BLOKA 3 — bind — this'ni doimiy "yopib qo'yish"</h4>
<pre><code>const t = {
    ism: "Ali",
    salomlash() { console.log(`Salom, ${this.ism}!`); }
};

// Oddiy chaqiruvda yo'qolardi
const fn = t.salomlash;
// fn();                       // this.ism — undefined

// bind — this ni doimiy biriktiradi
const fnBound = t.salomlash.bind(t);
fnBound();                     // "Salom, Ali!"

// Event handler uchun foydali
const tugma = document.querySelector("#btn");
// tugma.addEventListener("click", t.salomlash);          // YOMON — this yo'qoladi
tugma.addEventListener("click", t.salomlash.bind(t));    // YAXSHI</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const counter = {
    son: 0,
    boshlash() {
        setInterval(function() {
            this.son++;          // ⚠️ this — bu yerda nima?
            console.log(this.son);
        }, 1000);
    }
};
counter.boshlash();</code></pre>
<p><strong>Natija:</strong> <code>NaN</code> har sekundda. setInterval callback'i oddiy funksiya — <code>this</code> = <code>undefined</code>/<code>window</code>. <code>window.son</code> — undefined, <code>undefined++</code> — NaN. <strong>Yechim:</strong> arrow funksiya (lexical this) yoki bind:</p>
<pre><code>setInterval(() =&gt; { this.son++; console.log(this.son); }, 1000);
// yoki
setInterval(function() { this.son++; console.log(this.son); }.bind(this), 1000);</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>this</code> qoidasi — chaqiruv joyiga qarang</h4>
<table>
<tr><th>Chaqiruv shakli</th><th><code>this</code></th></tr>
<tr><td><code>obj.method()</code></td><td><code>obj</code></td></tr>
<tr><td><code>method()</code> (oddiy)</td><td><code>undefined</code> (strict) yoki <code>window</code> (loose)</td></tr>
<tr><td><code>new Func()</code></td><td>Yangi obyekt</td></tr>
<tr><td><code>func.call(ctx, ...)</code></td><td><code>ctx</code></td></tr>
<tr><td><code>func.apply(ctx, [...])</code></td><td><code>ctx</code></td></tr>
<tr><td><code>func.bind(ctx)()</code></td><td><code>ctx</code></td></tr>
<tr><td><code>() =&gt; this</code> (arrow)</td><td>Tashqi scope'dan</td></tr>
</table>

<h4>2. call vs apply vs bind</h4>
<table>
<tr><th>Metod</th><th>Argumentlar</th><th>Qachon ishga tushadi</th></tr>
<tr><td><code>call</code></td><td>Vergul bilan: <code>(ctx, a, b, c)</code></td><td>Darhol</td></tr>
<tr><td><code>apply</code></td><td>Massiv: <code>(ctx, [a, b, c])</code></td><td>Darhol</td></tr>
<tr><td><code>bind</code></td><td>Vergul: <code>(ctx, a, b)</code></td><td>Bog'langan funksiya qaytadi (keyinroq chaqiriladi)</td></tr>
</table>

<h4>3. Partial application — bind bilan</h4>
<pre><code>function ko_paytirish(a, b) {
    return a * b;
}

const ikkilash = ko_paytirish.bind(null, 2);
// null — this kerak emas, 2 — birinchi argument bog'langan

console.log(ikkilash(5));    // 10 (2 * 5)
console.log(ikkilash(7));    // 14 (2 * 7)</code></pre>

<h4>4. Class metodlari va <code>this</code> bug'i</h4>
<pre><code>class Hisoblovchi {
    constructor() {
        this.son = 0;
    }
    qoshish() {
        this.son++;
    }
}

const c = new Hisoblovchi();
c.qoshish();       // OK — this = c

const fn = c.qoshish;
// fn();           // TypeError — this.son: undefined

// Yechim 1: arrow funksiya class maydonida
class Hisoblovchi2 {
    son = 0;
    qoshish = () =&gt; { this.son++; };    // bound to instance
}

// Yechim 2: constructor'da bind
class Hisoblovchi3 {
    constructor() {
        this.son = 0;
        this.qoshish = this.qoshish.bind(this);
    }
    qoshish() { this.son++; }
}</code></pre>

<h4>5. Arrow funksiya va <code>this</code> — qachon ideal</h4>
<ul>
<li>Callback ichida tashqi <code>this</code> ga kirish kerak (setTimeout, map, event)</li>
<li>Class maydonida metodni instance'ga bog'lash</li>
<li>Functional helper funksiyalar (this kerak emas)</li>
</ul>
<p>Qachon arrow EMAS:</p>
<ul>
<li>Obyekt metodi sifatida (this = obyekt kerak)</li>
<li>Constructor (new bilan)</li>
<li>DOM event handler (this = element kerak bo'lsa)</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>this</code> — chaqiruv joyiga qarab; obyekt metodi -&gt; obyekt; oddiy chaqiruv -&gt; undefined</li>
<li><code>call</code> — argumentlar verguldan; <code>apply</code> — massivda; <code>bind</code> — keyinroq</li>
<li>Arrow — <code>this</code>ni TASHQARIDAN olib keladi (lexical)</li>
<li>Event handler / setTimeout / metodni boshqaga uzatish — <code>this</code> yo'qolish risk</li>
<li>Class metodini callback sifatida uzatsa — bind yoki arrow class maydon</li>
</ul>
"""

L5_CODE = """\
// ─── this, call, apply, bind — sweep ─────────────────────────────────────

"use strict";

// 1) Obyekt metodida this
const it = {
    nom: "Rex",
    gapir() { console.log(`${this.nom}: vov!`); },
};
it.gapir();

// 2) Metodni boshqaga uzatganda this yo'qoladi
const gap = it.gapir;
try {
    gap();
} catch (e) {
    console.log("Tutib oldim:", e.message);
}

// 3) call — this'ni aniq berish
function tasvirla(yosh, kasb) {
    return `${this.nom}, ${yosh} yosh, ${kasb}`;
}

const ali = { nom: "Ali" };
const vali = { nom: "Vali" };
console.log(tasvirla.call(ali, 21, "frontend"));
console.log(tasvirla.call(vali, 19, "backend"));

// 4) apply — argumentlar massivda
console.log(tasvirla.apply(ali, [25, "fullstack"]));

// 5) bind — this'ni doimiy biriktirish
const aliTasvir = tasvirla.bind(ali);
console.log(aliTasvir(21, "dev"));
console.log(aliTasvir(22, "lead dev"));

// 6) Partial application — bind bilan argumentni ham biriktirish
const yoshKattaDev = tasvirla.bind(ali, 30);
console.log(yoshKattaDev("senior dev"));

// 7) setInterval bug — strict mode'da
const counter = {
    son: 0,
    boshlash() {
        // YOMON:
        // setInterval(function () { this.son++; }, 100);

        // YAXSHI 1: arrow (lexical this)
        const id = setInterval(() => {
            this.son++;
            console.log(`Arrow this — son: ${this.son}`);
            if (this.son >= 3) clearInterval(id);
        }, 50);
    },
};
counter.boshlash();

// 8) Class va arrow class maydon
class Servis {
    constructor(nom) {
        this.nom = nom;
        this.so_rovlar = 0;
    }

    // Oddiy metod — uzatilganda this yo'qoladi
    so_rov() {
        this.so_rovlar++;
        console.log(`${this.nom}: ${this.so_rovlar}-so'rov`);
    }

    // Arrow class maydon — doim bound
    so_rov_bound = () => {
        this.so_rovlar++;
        console.log(`${this.nom} (bound): ${this.so_rovlar}-so'rov`);
    };
}

const api = new Servis("API");

// Oddiy chaqiruvda OK
api.so_rov();

// Uzatilganda — bug
const yo_qol = api.so_rov;
try {
    yo_qol();
} catch (e) {
    console.log("Bound emas — tutildi");
}

// bound — har joyda ishlaydi
const ishla = api.so_rov_bound;
ishla();
ishla();

// 9) Real misol — array metodlari ichidagi this
const utils = {
    prefix: "user_",
    tegla(ismlar) {
        // Arrow — tashqi this'ga kirish mumkin
        return ismlar.map((ism) => this.prefix + ism);
    },
};
console.log(utils.tegla(["ali", "vali", "gulya"]));
// ["user_ali", "user_vali", "user_gulya"]

// Agar oddiy function ishlatsa:
const utils2 = {
    prefix: "user_",
    tegla(ismlar) {
        // function ichida this — undefined, .prefix ko'rinmaydi
        return ismlar.map(function (ism) {
            // return this.prefix + ism;    // TypeError
            return ism;
        });
    },
};
"""

L6_TEXT = """\
<h2>ES6 modullar — <code>import</code> / <code>export</code></h2>

<pre class="mermaid">
flowchart LR
    MOD_A["math.js"] -->|export| FN["sum, mul"]
    FN -->|import| MOD_B["app.js"]
    MOD_C["user.js"] -->|export default| CLASS["class User"]
    CLASS -->|import default| MOD_B
    MOD_B -->|namespace| ALL["import * as utils"]
</pre>

<p>JS uzoq yillar modul tizimi'siz yashagan — barcha kod global scope'da edi. ES6 (ES2015) bunga chek qo'ydi. Endi har <code>.js</code> fayl — alohida modul. <strong>Named exports</strong> bir nechta narsa eksport qiladi, <strong>default export</strong> — bittasi. Bu kursdan keyin siz "spaghetti script" yozmaysiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<p>Modullar ishlashi uchun:</p>
<ol>
<li>HTML'da <code>&lt;script type="module" src="app.js"&gt;&lt;/script&gt;</code></li>
<li>Yoki Node.js'da <code>package.json</code> ga <code>"type": "module"</code></li>
<li>Yoki Vite/Webpack kabi build tool</li>
</ol>

<h4>BLOKA 1 — Named exports</h4>
<pre><code>// math.js
export const PI = 3.14159;

export function sum(a, b) {
    return a + b;
}

export const mul = (a, b) =&gt; a * b;

// Yoki barchasini oxirida
const div = (a, b) =&gt; a / b;
const sub = (a, b) =&gt; a - b;
export { div, sub };

// app.js
import { sum, mul, PI } from "./math.js";

console.log(sum(3, 4));    // 7
console.log(mul(5, 6));    // 30
console.log(PI);            // 3.14159</code></pre>

<h4>BLOKA 2 — Default export</h4>
<pre><code>// user.js
export default class User {
    constructor(ism, yosh) {
        this.ism = ism;
        this.yosh = yosh;
    }
    salomlash() {
        return `Salom, ${this.ism}!`;
    }
}

// app.js
import User from "./user.js";           // istalgan nom (qavssiz)

const u = new User("Ali", 21);
console.log(u.salomlash());</code></pre>

<h4>BLOKA 3 — Aralash, alias va namespace</h4>
<pre><code>// utils.js
export const formatla = (s) =&gt; s.trim().toLowerCase();
export const log = (s) =&gt; console.log(`[LOG] ${s}`);
export default function init() {
    console.log("Boshlandi");
}

// app.js
import init, { formatla, log as logla } from "./utils.js";
//        ^^                       ^^^^^^^^^^
//        default                  alias

init();
logla(formatla("  SALOM  "));    // [LOG] salom

// Yoki barchasini namespace bilan
import * as utils from "./utils.js";
utils.formatla("...");
utils.log("...");
utils.default();    // default — `default` deb chaqiriladi</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>// counter.js
let count = 0;
export const oshirish = () =&gt; count++;
export { count };

// app.js
import { count, oshirish } from "./counter.js";

console.log(count);    // 0
oshirish();
oshirish();
console.log(count);    // ???</code></pre>
<p><strong>Natija:</strong> <code>0</code>. Modullar <strong>live binding</strong> — agar eksport qiluvchi modul ichidagi qiymat o'zgarsa, importchi tomon <em>asl reference</em>ni ko'radi... LEKIN <code>let count</code> — primitive. Modulda qiymat oshadi, lekin <code>app.js</code> dagi ko'rinish ham yangilanadi.</p>
<p>Aslida: ES module live bindings — qiymat o'zgarsa importchi ham yangi qiymatni ko'radi. Demak natija aslida <code>2</code> bo'ladi. <strong>Lekin</strong> CommonJS'da (Node eski) — snapshot, primitive nusxalanadi. Esda saqlash: ES module — live, CommonJS — snapshot. Shu farqni bilmaslik — eng ko'p uchraydigan migration bug.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Named vs default export</h4>
<table>
<tr><th>Named</th><th>Default</th></tr>
<tr><td>Bir necha</td><td>Faqat bittasi</td></tr>
<tr><td>Aniq nom kerak: <code>{ sum }</code></td><td>Istalgan nom: <code>import X from ...</code></td></tr>
<tr><td>Yordamchi funksiyalar uchun</td><td>Modulning asosiy "qahramoni" uchun</td></tr>
<tr><td>Refactoring xavfsiz (rename topiladi)</td><td>Rename qiyin — har joyda boshqa nom</td></tr>
</table>
<p>Best practice: <strong>default'siz</strong>, faqat named. Hammasi bir-biriga moslashadi va katta loyihalarda boshqarish oson. Default — kichik modul + bittagina narsa eksport bo'lganda OK.</p>

<h4>2. Reexport — bir joydan boshqaga uzatish</h4>
<pre><code>// index.js — "barrel" file
export { sum, mul } from "./math.js";
export { default as User } from "./user.js";
export * from "./utils.js";

// boshqa joyda
import { sum, User, formatla } from "./index.js";</code></pre>

<h4>3. Dynamic import — runtime'da yuklash</h4>
<pre><code>// Faqat kerak bo'lganda yuklab olish (code splitting)
button.addEventListener("click", async () =&gt; {
    const { katta_kutubxona } = await import("./katta-kutubxona.js");
    katta_kutubxona();
});

// Promise qaytaradi
import("./kichik.js").then((mod) =&gt; mod.salom());</code></pre>

<h4>4. Modul properties</h4>
<ul>
<li><strong>Strict mode</strong> — har modul avtomatik strict</li>
<li><strong>Top-level</strong> — <code>this</code> = <code>undefined</code> (window emas)</li>
<li><strong>Live bindings</strong> — eksport qiymati o'zgarsa, importchi yangi qiymatni ko'radi</li>
<li><strong>Singleton</strong> — modul faqat bir marta yuklanadi va cache'lanadi</li>
<li><strong>Async</strong> — modullar parallel yuklanadi</li>
</ul>

<h4>5. ES modules vs CommonJS</h4>
<table>
<tr><th>ES modules (ESM)</th><th>CommonJS (CJS)</th></tr>
<tr><td><code>import / export</code></td><td><code>require() / module.exports</code></td></tr>
<tr><td>Statik (build-time tahlil)</td><td>Dinamik (runtime)</td></tr>
<tr><td>Live bindings</td><td>Snapshot</td></tr>
<tr><td>Top-level await</td><td>Yo'q</td></tr>
<tr><td>Async yuklash</td><td>Sync</td></tr>
<tr><td>Brauzer + modern Node</td><td>Eski Node</td></tr>
</table>

<h4>6. Qachon import path'iga <code>.js</code> qo'shish kerak?</h4>
<ul>
<li><strong>Brauzer ESM</strong> — <code>.js</code> majburiy: <code>./math.js</code></li>
<li><strong>Node ESM</strong> — <code>.js</code> majburiy (yangi qoidasi)</li>
<li><strong>Webpack / Vite / TS bilan</strong> — odatda <code>.js</code> shart emas (resolver topadi)</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>export</code>/<code>import</code> — modul tizimi (ES2015+)</li>
<li>Named export — bir nechtasi; default export — bittagina</li>
<li><code>{ }</code> ichida — named; qavssiz — default</li>
<li><code>import * as X</code> — namespace, <code>as alias</code> — qayta nomlash</li>
<li>HTML'da <code>&lt;script type="module"&gt;</code> kerak; modulda strict mode default</li>
</ul>
"""

L6_CODE = """\
// ─── ES6 modullar misoli ─────────────────────────────────────────────────
// Eslatma: bu kodlar HTML'da <script type="module"> bilan ishga tushadi.
// Bu yerda kod misol sifatida — har bir blok alohida fayl deb tasavvur qiling.

// ═══════════ math.js ═══════════
// export const PI = 3.14159;
// export function sum(a, b) { return a + b; }
// export const mul = (a, b) => a * b;
// const div = (a, b) => a / b;
// export { div };

// ═══════════ user.js ═══════════
// export default class User {
//     constructor(ism, yosh) {
//         this.ism = ism;
//         this.yosh = yosh;
//     }
//     salomlash() {
//         return `Salom, ${this.ism}!`;
//     }
// }

// ═══════════ utils.js ═══════════
// export const formatla = s => s.trim().toLowerCase();
// export const log = s => console.log(`[LOG] ${s}`);
// export default function init() { console.log("Boshlandi"); }

// ═══════════ index.js — barrel ═══════════
// export { sum, mul, PI } from "./math.js";
// export { default as User } from "./user.js";
// export * from "./utils.js";

// ═══════════ app.js ═══════════
// // 1) Named import
// import { sum, mul, PI } from "./math.js";
// console.log(sum(3, 4));
// console.log(mul(5, 6));
// console.log(PI);
//
// // 2) Default import
// import User from "./user.js";
// const ali = new User("Ali", 21);
// console.log(ali.salomlash());
//
// // 3) Aralash + alias
// import init, { formatla, log as logla } from "./utils.js";
// init();
// logla(formatla("  SALOM  "));
//
// // 4) Namespace
// import * as math from "./math.js";
// console.log(math.sum(1, 2));
// console.log(math.PI);
//
// // 5) Barrel orqali
// import { sum, User, formatla } from "./index.js";
//
// // 6) Dynamic import — code splitting
// document.querySelector("#tugma").addEventListener("click", async () => {
//     const { huge_lib } = await import("./big-library.js");
//     huge_lib();
// });

// ─── Brauzer console'da test qilish uchun bir fayllik misol ───────────────
// (modulsiz, lekin shaklini ko'rsatish uchun)

const moduleSimulator = {
    // math
    PI: 3.14159,
    sum: (a, b) => a + b,
    mul: (a, b) => a * b,

    // user
    User: class {
        constructor(ism, yosh) {
            this.ism = ism;
            this.yosh = yosh;
        }
        salomlash() { return `Salom, ${this.ism}!`; }
    },

    // utils
    formatla: (s) => s.trim().toLowerCase(),
    log: (s) => console.log(`[LOG] ${s}`),
};

// Bu kod — agar har biri alohida modul bo'lsa, qanday ko'rinishini ko'rsatuvchi
// "fake import" simulyatsiyasi:
const { sum, mul, PI, User, formatla, log } = moduleSimulator;

console.log("=== math demo ===");
console.log(`sum(3, 4) = ${sum(3, 4)}`);
console.log(`mul(5, 6) = ${mul(5, 6)}`);
console.log(`PI = ${PI}`);

console.log("\\n=== user demo ===");
const u = new User("Ali", 21);
console.log(u.salomlash());

console.log("\\n=== utils demo ===");
log(formatla("  Modern JS  "));

// ─── Modul shakli bo'yicha qoidalar ───────────────────────────────────────
// 1) Default export DIQQAT BILAN — refactoring qiyin
// 2) Named export'lar — IDE yaxshi qo'llaydi
// 3) Barrel (index.js) — ko'p eksport bo'lsa
// 4) Dynamic import — katta libraries uchun (code splitting)
// 5) `import.meta.url` — modul URL'i (kerak bo'lsa)

console.log("\\nModul URL (Node ESM uchun):", typeof import.meta !== "undefined" ? "available" : "n/a");
"""

R2_TEXT = """\
<h2>🔁 R2 — State'li hisoblovchi (closure + this + modul)</h2>

<pre class="mermaid">
flowchart LR
    MOD["counter.js modul"] -->|export| API["create, increment, ..."]
    API -->|closure| STATE["private state"]
    CLICK["DOM click"] -->|bind/arrow| HANDLER["handler bilan this"]
    HANDLER --> STATE
</pre>

<p>Modul 2 ning 3 ta texnikasi birga: <strong>closures</strong>, <strong>this+bind</strong> va <strong>ES6 modullar</strong>. Vazifa: bir nechta nazoratlanuvchi hisoblovchini yaratuvchi modul. Har biri o'z private state'iga ega, DOM tugmasiga bog'lash mumkin.</p>

<h3>🏆 5 daqiqada g'alaba — bitta katta misol</h3>

<pre><code>// ═══════════ counter.js ═══════════
// Public API — factory pattern (closure orqali private state)
export function createCounter({ boshlangich = 0, qadam = 1, max = Infinity } = {}) {
    let value = boshlangich;
    let tarix = [];

    const o_zgartirish = (yangi) =&gt; {
        tarix.push({ eski: value, yangi, vaqt: Date.now() });
        value = yangi;
    };

    return {
        oshirish() {
            if (value + qadam &gt; max) throw new Error("Max dan oshib ketdi");
            o_zgartirish(value + qadam);
            return value;
        },
        kamaytirish() {
            o_zgartirish(value - qadam);
            return value;
        },
        nollash() { o_zgartirish(boshlangich); return value; },
        get joriy() { return value; },
        get tarix() { return [...tarix]; },
    };
}

// ═══════════ app.js ═══════════
import { createCounter } from "./counter.js";

const limitli = createCounter({ boshlangich: 0, qadam: 5, max: 20 });
console.log(limitli.oshirish());    // 5
console.log(limitli.oshirish());    // 10
console.log(limitli.oshirish());    // 15
console.log(limitli.oshirish());    // 20
// limitli.oshirish();              // Error: Max dan oshib ketdi

console.log(limitli.tarix);          // 4 ta o'zgarish
</code></pre>

<h3>3 ta texnikani birga ko'rib chiqamiz</h3>

<h4>Closures</h4>
<ul>
<li><code>value</code>, <code>tarix</code>, <code>qadam</code>, <code>max</code> — privatе state</li>
<li>Har <code>createCounter</code> chaqirig'i alohida closure</li>
<li>Tashqaridan kirish yo'q — <code>limitli.value</code> undefined</li>
</ul>

<h4>this / bind</h4>
<ul>
<li>Metod sifatida — <code>{ oshirish() { ... } }</code> qisqartmasi</li>
<li>DOM event handler'ga uzatishda <code>this</code> yo'qoladi — <code>arrow</code> yoki <code>bind</code></li>
<li>Getter <code>get joriy</code> — atribut sifatida ko'rinadi (qavssiz)</li>
</ul>

<h4>ES6 modullar</h4>
<ul>
<li><code>export function createCounter</code> — named export</li>
<li><code>import { createCounter } from "./counter.js"</code></li>
<li>Modul faqat bir marta yuklanadi (singleton), lekin har <code>createCounter</code> chaqirig'i yangi closure</li>
</ul>

<h3>📌 Module 2 ni siz endi bilasiz</h3>
<ul>
<li>Private state — class kerak emas, closure yetadi</li>
<li><code>this</code> mantig'ini biling — event handler uchun arrow yoki bind</li>
<li>Har <code>.js</code> fayl — alohida modul; sof named export</li>
<li>3 ta birga ishlatilganda — siz "modular, encapsulated JS" yozyapsiz</li>
</ul>
"""

R2_CODE = """\
// ─── R2: State'li hisoblovchi to'plami (closure + this + modul) ──────────
//
// Tasavvur qiling: counter.js modul bor. Bu yerda bir-fayllik to'liq misol.

// ═══════════ counter.js (factory pattern) ═══════════
function createCounter({ boshlangich = 0, qadam = 1, max = Infinity, min = -Infinity } = {}) {
    let value = boshlangich;
    let tarix = [];

    const o_zgartirish = (yangi) => {
        tarix.push({ eski: value, yangi, vaqt: Date.now() });
        value = yangi;
    };

    return {
        oshirish() {
            if (value + qadam > max) {
                throw new Error(`Max chegarasi (${max}) dan oshib ketdi`);
            }
            o_zgartirish(value + qadam);
            return value;
        },
        kamaytirish() {
            if (value - qadam < min) {
                throw new Error(`Min chegarasi (${min}) dan kichik`);
            }
            o_zgartirish(value - qadam);
            return value;
        },
        nollash() {
            o_zgartirish(boshlangich);
            return value;
        },
        get joriy() { return value; },
        get tarix() { return [...tarix]; },
        get o_zgarish_soni() { return tarix.length; },
    };
}

// ═══════════ app.js ═══════════
// 1) Oddiy hisoblovchi
const sodda = createCounter();
console.log(sodda.oshirish());        // 1
console.log(sodda.oshirish());        // 2
console.log(sodda.oshirish());        // 3
console.log("Sodda joriy:", sodda.joriy);

// 2) Limitli hisoblovchi
const limitli = createCounter({ qadam: 5, max: 20 });
limitli.oshirish();
limitli.oshirish();
limitli.oshirish();
console.log("Limitli joriy:", limitli.joriy);
try {
    limitli.oshirish();
    limitli.oshirish();    // 4-marta — 20, ok
    limitli.oshirish();    // 5-marta — 25, max ortib ketadi
} catch (e) {
    console.log("Tutib oldim:", e.message);
}

// 3) Alohida instance — alohida closure
const a = createCounter();
const b = createCounter();
a.oshirish();
a.oshirish();
b.oshirish();
console.log(`a=${a.joriy}, b=${b.joriy}`);    // a=2, b=1 — alohida state

// 4) Private state isboti
console.log("Private value ko'rinmaydi:", a.value);    // undefined

// 5) Tarix
console.log("Tarix:", a.tarix);

// 6) DOM bog'lash (brauzer kontekstida)
// const tugma = document.querySelector("#qoshish");
// tugma.addEventListener("click", () => {
//     const yangi = limitli.oshirish();
//     document.querySelector("#display").textContent = yangi;
// });

// 7) Sinov bilan inputdan o'qish — debounced
function debounce(funk, kutish) {
    let id;
    return (...args) => {
        clearTimeout(id);
        id = setTimeout(() => funk.apply(this, args), kutish);
    };
}

const yangilash = debounce((q) => console.log(`Joriy: ${q}`), 200);
const search = createCounter();
yangilash(search.oshirish());
yangilash(search.oshirish());
yangilash(search.oshirish());
// Faqat 200ms keyin oxirgisi

// 8) Bir nechtasini boshqarish — registry pattern
function createRegistry() {
    const counters = new Map();

    return {
        qosh(nom, opts) {
            counters.set(nom, createCounter(opts));
        },
        olish(nom) { return counters.get(nom); },
        joriy(nom) { return counters.get(nom)?.joriy ?? null; },
        hammasi() {
            const natija = {};
            for (const [nom, c] of counters) natija[nom] = c.joriy;
            return natija;
        },
    };
}

const registry = createRegistry();
registry.qosh("oshxona", { qadam: 1 });
registry.qosh("vannaxona", { qadam: 2 });
registry.olish("oshxona").oshirish();
registry.olish("oshxona").oshirish();
registry.olish("vannaxona").oshirish();

console.log("Registry:", registry.hammasi());
// { oshxona: 2, vannaxona: 2 }
"""

L7_TEXT = """\
<h2>Promiselar — async ish'ning birinchi qatlami</h2>

<pre class="mermaid">
flowchart LR
    NEW["new Promise"] -->|pending| WAIT["kutilmoqda"]
    WAIT -->|resolve| OK["fulfilled"]
    WAIT -->|reject| FAIL["rejected"]
    OK -->|.then| HANDLE["natijani ishlat"]
    FAIL -->|.catch| ERR["xatoni ushla"]
    OK -->|.finally| END["tugadi"]
    FAIL -->|.finally| END
</pre>

<p>JS — single-threaded. Lekin server, fayl, timer, animatsiya — vaqt oladi. <strong>Promise</strong> — kelajakda keladigan natijaning "vakuum kartochkasi". Promise <em>resolved</em>, <em>rejected</em> yoki <em>pending</em> bo'ladi. Bu — async/await va fetch'ning poydevori.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Promise yaratish</h4>
<pre><code>const promise = new Promise((resolve, reject) =&gt; {
    // Kechiktirilgan ish
    setTimeout(() =&gt; {
        const ok = Math.random() &gt; 0.5;
        if (ok) {
            resolve("Muvaffaqiyatli!");      // pending -&gt; fulfilled
        } else {
            reject(new Error("Xatolik"));     // pending -&gt; rejected
        }
    }, 1000);
});

console.log(promise);    // Promise { &lt;pending&gt; }

promise
    .then((natija) =&gt; console.log("✅", natija))
    .catch((xato) =&gt;  console.log("❌", xato.message))
    .finally(()    =&gt;  console.log("Tugadi"));</code></pre>

<h4>BLOKA 2 — Chain — .then ketma-ket</h4>
<pre><code>function kutish(ms) {
    return new Promise((resolve) =&gt; setTimeout(resolve, ms));
}

kutish(1000)
    .then(() =&gt; { console.log("1 sek o'tdi"); return kutish(1000); })
    .then(() =&gt; { console.log("Yana 1 sek o'tdi"); return kutish(500); })
    .then(() =&gt; console.log("3 sekund jami"));

// Yoki .then ichida qiymat qaytarish
Promise.resolve(5)
    .then((x) =&gt; x * 2)              // 10
    .then((x) =&gt; x + 1)               // 11
    .then((x) =&gt; console.log(x));     // 11</code></pre>

<h4>BLOKA 3 — Promise.all va Promise.race</h4>
<pre><code>// Hammasini parallel kutish
const url1 = "https://api.github.com/users/torvalds";
const url2 = "https://api.github.com/users/gvanrossum";

Promise.all([
    fetch(url1).then(r =&gt; r.json()),
    fetch(url2).then(r =&gt; r.json()),
])
    .then(([linus, guido]) =&gt; {
        console.log(`${linus.name} va ${guido.name}`);
    })
    .catch((e) =&gt; console.log("Bittasi ham yiqilsa — catch"));

// Eng birinchi javob keladigan
Promise.race([
    fetch("https://api1.example.com"),
    fetch("https://api2.example.com"),
])
    .then((r) =&gt; r.json())
    .then(console.log);</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const p = new Promise((resolve) =&gt; resolve(42));
p.then((natija) =&gt; {
    console.log(natija);
    throw new Error("Ichida xato");
});

// Konsolda — UnhandledPromiseRejection</code></pre>
<p><strong>Muammo:</strong> <code>.then</code> ichida xato chiqsa va <code>.catch</code> qo'shilmagan bo'lsa — silently fail (lekin Node yangi versiyalarda crash). <strong>Qoida:</strong> har chain'da DOIM oxirida <code>.catch</code> bo'lsin:</p>
<pre><code>p
    .then((natija) =&gt; {
        if (notog'ri) throw new Error("...");
        return natija;
    })
    .catch((e) =&gt; console.error("Ushladim:", e.message));</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Promise — 3 holat</h4>
<table>
<tr><th>Holat</th><th>Ma'nosi</th></tr>
<tr><td><code>pending</code></td><td>Kutilmoqda — hali tugamagan</td></tr>
<tr><td><code>fulfilled</code></td><td>Muvaffaqiyatli tugadi (resolve chaqirilgan)</td></tr>
<tr><td><code>rejected</code></td><td>Xato bilan tugadi (reject chaqirilgan)</td></tr>
</table>
<p>Bir marta pending'dan chiqsa — qaytmaydi (immutable). Resolve yoki reject — bitta marta.</p>

<h4>2. Promise statik metodlar</h4>
<table>
<tr><th>Metod</th><th>Maqsadi</th></tr>
<tr><td><code>Promise.resolve(x)</code></td><td>Darhol fulfilled Promise</td></tr>
<tr><td><code>Promise.reject(e)</code></td><td>Darhol rejected Promise</td></tr>
<tr><td><code>Promise.all([p1, p2])</code></td><td>Hammasi tugashini kutadi. Bittasi rejected -&gt; butun array fail</td></tr>
<tr><td><code>Promise.allSettled([p1, p2])</code></td><td>Hammasini kutadi — fail bo'lganlari ham natijada</td></tr>
<tr><td><code>Promise.race([p1, p2])</code></td><td>Birinchi tugagani (fulfilled yoki rejected)</td></tr>
<tr><td><code>Promise.any([p1, p2])</code></td><td>Birinchi fulfilled. Hammasi rejected bo'lsa — AggregateError</td></tr>
</table>

<h4>3. Chain'da xato'ni boshqarish</h4>
<pre><code>fetch(url)
    .then((r) =&gt; {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    })
    .then((data) =&gt; processData(data))
    .catch((e) =&gt; {
        if (e.message.includes("HTTP")) {
            // tarmoq xatosi
        } else {
            // boshqa
        }
    });</code></pre>
<p><code>.catch</code> chain'dagi HAR QANDAY xatoni ushlaydi — qaerda yuz berishidan qat'i nazar.</p>

<h4>4. Promise.all — paralel</h4>
<pre><code>// 3 ta API chaqiruvi — birgalikda
const [users, posts, comments] = await Promise.all([
    fetch("/api/users").then(r =&gt; r.json()),
    fetch("/api/posts").then(r =&gt; r.json()),
    fetch("/api/comments").then(r =&gt; r.json()),
]);
// Eng sekin so'rovning vaqti — emas barcha vaqtlarning yig'indisi</code></pre>

<h4>5. Promise.allSettled — har biri haqida ma'lumot</h4>
<pre><code>const natijalar = await Promise.allSettled([
    fetch("/api/a"),
    fetch("/api/b"),     // bu fail bo'lsin
    fetch("/api/c"),
]);

natijalar.forEach((r, i) =&gt; {
    if (r.status === "fulfilled") {
        console.log(`API ${i}: OK`, r.value);
    } else {
        console.log(`API ${i}: FAIL`, r.reason);
    }
});</code></pre>

<h4>6. Callback hell vs Promise chain</h4>
<pre><code>// Callback hell — eski stil
authenticate(user, (err, token) =&gt; {
    if (err) return console.error(err);
    fetchProfile(token, (err, profile) =&gt; {
        if (err) return console.error(err);
        fetchPosts(profile.id, (err, posts) =&gt; {
            if (err) return console.error(err);
            console.log(posts);
        });
    });
});

// Promise chain — toza
authenticate(user)
    .then(fetchProfile)
    .then((profile) =&gt; fetchPosts(profile.id))
    .then(console.log)
    .catch(console.error);</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Promise — kelajakdagi natija "vakuum kartochkasi": pending -&gt; fulfilled/rejected</li>
<li><code>.then(...)</code> — natija; <code>.catch(...)</code> — xato; <code>.finally(...)</code> — har holatda</li>
<li>Chain'da xato — har qaysi <code>.then</code>'dan oxirgi <code>.catch</code> ga "tushadi"</li>
<li><code>Promise.all</code> — parallel kutish; <code>allSettled</code> — har biri haqida ma'lumot</li>
<li>Har chain oxirida <code>.catch</code> qo'shing — silently fail oldini olish uchun</li>
</ul>
"""

L7_CODE = """\
// ─── Promiselar — to'liq sweep ───────────────────────────────────────────

// 1) Eng oddiy Promise — kutish
function kutish(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

console.log("Boshlandi");
kutish(500).then(() => console.log("500ms o'tdi"));
kutish(1000).then(() => console.log("1000ms o'tdi"));

// 2) Resolve / Reject — tasodifiy
function shubhali(success_rate = 0.5) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() < success_rate) {
                resolve({ ok: true, vaqt: Date.now() });
            } else {
                reject(new Error("network down"));
            }
        }, 200);
    });
}

shubhali(0.7)
    .then((r) => console.log("✅", r))
    .catch((e) => console.log("❌", e.message));

// 3) Chain — qiymat o'zgaradi
Promise.resolve(5)
    .then((x) => x * 2)
    .then((x) => x + 10)
    .then((x) => `Natija: ${x}`)
    .then(console.log);

// 4) Chain ichida Promise qaytarish — keyinchalik kutish
function olish(id) {
    return kutish(100).then(() => ({ id, nom: `User ${id}` }));
}

olish(1)
    .then((u) => {
        console.log("1-step:", u);
        return olish(u.id + 1);
    })
    .then((u) => {
        console.log("2-step:", u);
        return olish(u.id + 1);
    })
    .then((u) => console.log("3-step:", u));

// 5) Promise.all — parallel
const idlar = [10, 20, 30];
Promise.all(idlar.map(olish))
    .then((natijalar) => {
        console.log("Hammasi parallel:", natijalar.map((u) => u.nom));
    });

// 6) Promise.allSettled — fail bo'lsa ham hammasi
Promise.allSettled([
    shubhali(0.9),
    shubhali(0.1),       // ehtimol fail
    shubhali(0.5),
]).then((natijalar) => {
    natijalar.forEach((r, i) => {
        if (r.status === "fulfilled") {
            console.log(`#${i}: OK`, r.value);
        } else {
            console.log(`#${i}: FAIL`, r.reason.message);
        }
    });
});

// 7) Promise.race — eng birinchisi
function timeout(ms) {
    return new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Timeout ${ms}ms`)), ms),
    );
}

function fetchWithTimeout(promise, ms) {
    return Promise.race([promise, timeout(ms)]);
}

fetchWithTimeout(shubhali(0.9), 500)
    .then((r) => console.log("Tez:", r))
    .catch((e) => console.log("Timeout/xato:", e.message));

// 8) Retry pattern — Promise bilan
function retry(funk, marotaba = 3, kutish_ms = 100) {
    return funk().catch((e) => {
        if (marotaba <= 1) throw e;
        return kutish(kutish_ms).then(() => retry(funk, marotaba - 1, kutish_ms));
    });
}

retry(() => shubhali(0.2), 5)
    .then((r) => console.log("Retry muvaffaqiyatli:", r))
    .catch((e) => console.log("Retry chiqdi:", e.message));

// 9) Promisify — eski callback API'ni Promise'ga aylantirish
function callback_style(arg, callback) {
    setTimeout(() => callback(null, arg * 2), 100);
}

function promisify(funk) {
    return function (...args) {
        return new Promise((resolve, reject) => {
            funk(...args, (err, natija) => {
                if (err) reject(err);
                else resolve(natija);
            });
        });
    };
}

const promised = promisify(callback_style);
promised(5).then((x) => console.log("Promisified:", x));    // 10
"""

L8_TEXT = """\
<h2><code>async/await</code> — Promise'ni sinxron kabi yozish</h2>

<pre class="mermaid">
flowchart LR
    PROM[".then ketma-ket"] -->|qiyin o'qish| CHAIN["chain noise"]
    ASYNC["async function"] -->|await x| WAIT["xayoldai sinxron"]
    WAIT --> RESULT["natija — Promise'ning value'si"]
    ERR["xato"] -->|try/catch| HANDLE["sodda xato boshqaruvi"]
</pre>

<p>Promise'lar zo'r, lekin <code>.then</code> chain'lari uzun bo'lib ketadi. <code>async/await</code> — bu chain'larni xuddi <strong>sinxron kod</strong>dek yozish imkonini beradi. Aslida — sintaktik shakar. <code>await</code> ostidagi Promise — to'xtatib turadi, natijani qaytaradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — .then dan async/await ga</h4>
<pre><code>// Eski stil — .then chain
function eskiUsul() {
    return fetch("/api/user")
        .then(r =&gt; r.json())
        .then(user =&gt; fetch(`/api/posts/${user.id}`))
        .then(r =&gt; r.json())
        .then(posts =&gt; ({ user_id: user.id, posts }));    // ⚠️ user yo'q!
}

// Modern — async/await
async function yangiUsul() {
    const user = await fetch("/api/user").then(r =&gt; r.json());
    const posts = await fetch(`/api/posts/${user.id}`).then(r =&gt; r.json());
    return { user_id: user.id, posts };          // ✅ user mavjud
}</code></pre>

<h4>BLOKA 2 — try/catch — xatoni ushlash</h4>
<pre><code>async function olish(url) {
    try {
        const r = await fetch(url);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } catch (e) {
        console.error("Xato:", e.message);
        return null;
    } finally {
        console.log("Tugadi");
    }
}

const data = await olish("/api/users");</code></pre>

<h4>BLOKA 3 — Parallel — Promise.all bilan</h4>
<pre><code>// SEKVENSIAL — ketma-ket, sekinroq
async function sekin() {
    const a = await fetch("/api/a").then(r =&gt; r.json());
    const b = await fetch("/api/b").then(r =&gt; r.json());
    const c = await fetch("/api/c").then(r =&gt; r.json());
    return { a, b, c };
    // Vaqt: a + b + c
}

// PARALLEL — birgalikda, tezroq
async function tez() {
    const [a, b, c] = await Promise.all([
        fetch("/api/a").then(r =&gt; r.json()),
        fetch("/api/b").then(r =&gt; r.json()),
        fetch("/api/c").then(r =&gt; r.json()),
    ]);
    return { a, b, c };
    // Vaqt: max(a, b, c)
}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const ismlar = ["ali", "vali", "gulya"];

ismlar.forEach(async (ism) =&gt; {
    const data = await fetch(`/api/users/${ism}`).then(r =&gt; r.json());
    console.log(data);
});

console.log("Hammasi tugadi!");    // ⚠️ Yolg'on</code></pre>
<p><strong>Muammo:</strong> <code>forEach</code> Promise'ni KUTMAYDI. <code>async</code> callback shunchaki Promise qaytaradi va <code>forEach</code> uni e'tiborsiz qoldiradi. "Hammasi tugadi" — async ishlar tugashidan oldin. <strong>Yechim:</strong></p>
<pre><code>// 1) for...of — kutadi
for (const ism of ismlar) {
    const data = await fetch(`/api/users/${ism}`).then(r =&gt; r.json());
    console.log(data);
}

// 2) Promise.all + map — parallel
const datalar = await Promise.all(
    ismlar.map(ism =&gt; fetch(`/api/users/${ism}`).then(r =&gt; r.json())),
);</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. async funksiya nima qaytaradi?</h4>
<pre><code>async function f() { return 5; }

const x = f();
console.log(x);           // Promise { 5 }
console.log(await x);     // 5

// async funksiya — DOIM Promise qaytaradi
// `return 5` — Promise.resolve(5) ga ekvivalent
// `throw err` — Promise.reject(err) ga ekvivalent</code></pre>

<h4>2. await qoidalari</h4>
<ul>
<li><code>await</code> — FAQAT <code>async</code> funksiya ichida (yoki top-level modulda)</li>
<li>Promise <em>resolved</em> bo'lsa — qiymat qaytaradi</li>
<li>Promise <em>rejected</em> bo'lsa — <code>throw</code> kabi exception</li>
<li>Promise BO'LMAGAN qiymatga <code>await</code> — darhol shu qiymat</li>
</ul>

<h4>3. try/catch va Promise xato boshqaruvi</h4>
<pre><code>// async/await — sinxron kodga o'xshash try/catch
async function v1() {
    try {
        const data = await fetch(url);
        return await data.json();
    } catch (e) {
        console.error(e);
    }
}

// .then chain bilan ekvivalent
function v2() {
    return fetch(url)
        .then((r) =&gt; r.json())
        .catch((e) =&gt; console.error(e));
}</code></pre>

<h4>4. Sekvensial vs Parallel — diqqat</h4>
<pre><code>// ⚠️ Sekin (sekvensial) — har biri avvalgisini kutadi
async function sekin() {
    const a = await fetchA();    // 1s
    const b = await fetchB();    // 1s
    const c = await fetchC();    // 1s
    return [a, b, c];            // jami 3s
}

// ✅ Tez (parallel) — birga boshlanadi
async function tez() {
    const aP = fetchA();          // 1s (boshlandi)
    const bP = fetchB();          // 1s (boshlandi)
    const cP = fetchC();          // 1s (boshlandi)
    return [await aP, await bP, await cP];    // jami 1s
}

// Idiomatic — Promise.all
async function eng_yaxshi() {
    return Promise.all([fetchA(), fetchB(), fetchC()]);    // jami 1s
}</code></pre>

<h4>5. Top-level await — modullarda</h4>
<pre><code>// ES2022+ va ESM modullar
// app.js
import { fetchConfig } from "./config.js";

const config = await fetchConfig();   // OK — top-level
console.log(config);

// Funksiya tashqarisida await — faqat modul'da ishlaydi</code></pre>

<h4>6. Async/await va loop ichida</h4>
<table>
<tr><th>Tanlov</th><th>Behavior</th></tr>
<tr><td><code>for...of + await</code></td><td>Sekvensial — biror tartib kerak bo'lganda</td></tr>
<tr><td><code>Promise.all + map</code></td><td>Parallel — tartib muhim emas</td></tr>
<tr><td><code>forEach + async</code></td><td>❌ Kutmaydi — xato</td></tr>
<tr><td><code>for (const p of promises) await p</code></td><td>Sekvensial wait</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>async function</code> — doim Promise qaytaradi</li>
<li><code>await</code> — faqat <code>async</code> ichida; Promise tugashini kutadi</li>
<li>Sinxron stilda <code>try/catch</code> bilan xato boshqarish</li>
<li>Parallel uchun <code>Promise.all</code>; sekvensial uchun <code>for...of</code></li>
<li><code>forEach + async</code> — KUTMAYDI, xato</li>
</ul>
"""

L8_CODE = """\
// ─── async/await — to'liq sweep ──────────────────────────────────────────

// 1) Eng oddiy async funksiya
async function salom() {
    return "Salom!";
}

console.log(salom());           // Promise { 'Salom!' }
salom().then(console.log);      // "Salom!"

// IIFE — async ni top-level'da chaqirish
(async () => {
    const xabar = await salom();
    console.log("await bilan:", xabar);
})();

// 2) Promise yaratish va await
function kutish(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

(async () => {
    console.log("Boshlandi");
    await kutish(500);
    console.log("500ms o'tdi");
    await kutish(500);
    console.log("Yana 500ms");
})();

// 3) try/catch — xato boshqaruvi
async function olish(url) {
    try {
        // fetch yo'q test muhitida — simulyatsiya
        if (url.includes("bad")) throw new Error("404 Not Found");
        await kutish(100);
        return { ok: true, url };
    } catch (e) {
        console.log("Xato ushlandi:", e.message);
        return null;
    } finally {
        console.log(`finally: ${url}`);
    }
}

(async () => {
    console.log(await olish("/api/users"));
    console.log(await olish("/api/bad"));
})();

// 4) Sekvensial vs Parallel
async function sekvensial() {
    const t0 = Date.now();
    await kutish(100);
    await kutish(100);
    await kutish(100);
    console.log(`Sekvensial: ${Date.now() - t0}ms`);    // ~300
}

async function parallel() {
    const t0 = Date.now();
    await Promise.all([kutish(100), kutish(100), kutish(100)]);
    console.log(`Parallel: ${Date.now() - t0}ms`);      // ~100
}

(async () => {
    await sekvensial();
    await parallel();
})();

// 5) Loop bilan — to'g'ri va noto'g'ri
const idlar = [1, 2, 3];

async function fakeOlish(id) {
    await kutish(50);
    return { id, nom: `User ${id}` };
}

// ✅ for...of — sekvensial wait
(async () => {
    console.log("\\nfor...of:");
    for (const id of idlar) {
        const u = await fakeOlish(id);
        console.log(u);
    }
})();

// ✅ Promise.all + map — parallel
(async () => {
    console.log("\\nPromise.all:");
    const users = await Promise.all(idlar.map(fakeOlish));
    console.log(users);
})();

// ❌ forEach + async — kutmaydi
(async () => {
    console.log("\\nforEach (noto'g'ri):");
    idlar.forEach(async (id) => {
        const u = await fakeOlish(id);
        console.log("forEach:", u);
    });
    console.log("forEach tugadi (lekin user'lar hali kutmoqda!)");
})();

// 6) Real foydalanish — JSON API
async function repoOlish(nomi) {
    try {
        const r = await fetch(`https://api.github.com/repos/${nomi}`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        return {
            nom: data.full_name,
            stars: data.stargazers_count,
            til: data.language,
        };
    } catch (e) {
        console.error(`${nomi}: ${e.message}`);
        return null;
    }
}

(async () => {
    console.log("\\n=== GitHub repos (parallel) ===");
    const repos = ["python/cpython", "facebook/react", "vuejs/vue"];
    const natijalar = await Promise.all(repos.map(repoOlish));
    natijalar.filter(Boolean).forEach((r) =>
        console.log(`⭐ ${r.stars.toLocaleString().padStart(8)}  ${r.nom}  [${r.til}]`),
    );
})();
"""

L9_TEXT = """\
<h2><code>fetch</code> va REST API'lar</h2>

<pre class="mermaid">
flowchart LR
    JS["fetch url"] -->|GET| API["server"]
    JS -->|POST + body| API
    API --> RESP["Response: status, headers, body"]
    RESP -->|.json| OBJ["JS obyekt"]
    JS -->|Authorization header| AUTH["auth"]
    JS -->|AbortController| CANCEL["bekor qilish"]
</pre>

<p><code>fetch</code> — brauzerga "borib shu URL'ni o'qib kel" deyish. Browser API, hozir Node.js da ham bor. Promise qaytaradi. <code>async/await</code> bilan birga — kuchli kombo.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Eng oddiy GET</h4>
<pre><code>const r = await fetch("https://api.github.com/users/torvalds");
console.log(r.status);             // 200
console.log(r.ok);                  // true (2xx bo'lsa)

const user = await r.json();
console.log(user.name);             // "Linus Torvalds"
console.log(user.bio);

// Query params — URLSearchParams bilan
const params = new URLSearchParams({ q: "python", page: 2 });
const search = await fetch(`https://api.github.com/search/users?${params}`);</code></pre>

<h4>BLOKA 2 — POST + JSON body</h4>
<pre><code>const r = await fetch("https://api.example.com/users", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer XXX",
    },
    body: JSON.stringify({ ism: "Ali", yosh: 21 }),
});

if (!r.ok) {
    throw new Error(`HTTP ${r.status}`);
}

const created = await r.json();
console.log(created.id);</code></pre>

<h4>BLOKA 3 — Xato boshqaruvi va bekor qilish</h4>
<pre><code>// AbortController — so'rovni to'xtatish
const controller = new AbortController();

setTimeout(() =&gt; controller.abort(), 3000);    // 3 sekunddan keyin to'xtat

try {
    const r = await fetch(url, { signal: controller.signal });
    const data = await r.json();
} catch (e) {
    if (e.name === "AbortError") {
        console.log("So'rov bekor qilindi");
    } else {
        console.log("Xato:", e.message);
    }
}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>const r = await fetch("https://api.example.com/data");
console.log(r);              // Response obyekt, lekin data emas
console.log(r.json());       // ⚠️ Promise — to'g'ri ishlatish kerak

// To'g'ri
const data = await r.json();
console.log(data);</code></pre>
<p><strong>Sabab:</strong> <code>r.json()</code> Promise qaytaradi (body ni asynchronously parse qiladi). <code>await</code> qo'shilmasa — Promise obyektni ko'rasiz, kerakli data emas. <strong>Esda saqlang:</strong> <code>fetch</code> 2 ta <code>await</code> oladi:</p>
<ol>
<li><code>await fetch(...)</code> — response keladi</li>
<li><code>await r.json()</code> — body parse bo'ladi</li>
</ol>

<h3>Endi tushuntiramiz</h3>

<h4>1. fetch ⚠️ — yopiq holatga ham reject qilmaydi</h4>
<pre><code>// HTTP 404 — fetch reject EMAS qiladi
const r = await fetch("/api/yo'q");
console.log(r.ok);          // false
console.log(r.status);       // 404

// Faqat tarmoq xatosi (DNS, offline) Promise'ni reject qiladi
// 4xx/5xx — Promise resolved! r.ok ni qo'lda tekshirish kerak

if (!r.ok) {
    throw new Error(`HTTP ${r.status}: ${r.statusText}`);
}</code></pre>

<h4>2. Response obyekt nimasi bor</h4>
<table>
<tr><th>Maydon</th><th>Qaytaradi</th></tr>
<tr><td><code>r.status</code></td><td>200, 404, 500 ...</td></tr>
<tr><td><code>r.statusText</code></td><td>"OK", "Not Found"</td></tr>
<tr><td><code>r.ok</code></td><td><code>true</code> agar 200-299</td></tr>
<tr><td><code>r.headers.get("Content-Type")</code></td><td>Header qiymati</td></tr>
<tr><td><code>r.url</code></td><td>Final URL (redirect'lardan keyin)</td></tr>
<tr><td><code>await r.json()</code></td><td>Body — JSON parse</td></tr>
<tr><td><code>await r.text()</code></td><td>Body — string</td></tr>
<tr><td><code>await r.blob()</code></td><td>Body — bayt (rasm, fayl)</td></tr>
<tr><td><code>await r.formData()</code></td><td>Body — FormData</td></tr>
</table>

<h4>3. HTTP metodlar</h4>
<table>
<tr><th>Metod</th><th>Maqsadi</th></tr>
<tr><td>GET</td><td>O'qish — body yo'q</td></tr>
<tr><td>POST</td><td>Yangi yaratish — body kerak</td></tr>
<tr><td>PUT</td><td>To'liq almashtirish</td></tr>
<tr><td>PATCH</td><td>Qisman yangilash</td></tr>
<tr><td>DELETE</td><td>O'chirish</td></tr>
</table>

<h4>4. Authorization patterns</h4>
<pre><code>// Bearer token
headers: { "Authorization": "Bearer XXXX" }

// API key (header'da)
headers: { "X-Api-Key": "XXXX" }

// API key (query param'da)
const url = `https://api.../endpoint?api_key=XXXX`;

// Basic auth (eski stil)
headers: { "Authorization": "Basic " + btoa("user:pass") }

// Cookie (avtomatik) — credentials sozlamasi bilan
fetch(url, { credentials: "include" })</code></pre>

<h4>5. Universal xavfsiz wrapper</h4>
<pre><code>async function api(url, options = {}) {
    const timeout = options.timeout || 10000;
    const controller = new AbortController();
    const tid = setTimeout(() =&gt; controller.abort(), timeout);

    try {
        const r = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
            body: options.body ? JSON.stringify(options.body) : undefined,
        });

        if (!r.ok) {
            const xato = await r.text();
            throw new Error(`HTTP ${r.status}: ${xato}`);
        }

        return await r.json();
    } finally {
        clearTimeout(tid);
    }
}

// Foydalanish
const user = await api("/api/user");
const created = await api("/api/posts", {
    method: "POST",
    body: { title: "Salom", content: "..." },
});</code></pre>

<h4>6. Qachon fetch, qachon axios / library</h4>
<table>
<tr><th>fetch</th><th>axios va o'xshashlari</th></tr>
<tr><td>Native — qo'shimcha kutubxonasiz</td><td>Tashqi paket</td></tr>
<tr><td>4xx/5xx — manual tekshirish</td><td>Avtomatik throw</td></tr>
<tr><td>JSON parse — qo'lda <code>.json()</code></td><td>Avtomatik</td></tr>
<tr><td>Timeout — AbortController</td><td>Sozlama bilan</td></tr>
<tr><td>Interceptors yo'q</td><td>Bor (har so'rovga qo'shimcha logika)</td></tr>
<tr><td>Brauzer + modern Node</td><td>Hammasi</td></tr>
</table>
<p>Default: <code>fetch</code> + kichik wrapper. Katta loyiha + ko'p o'ziga xos so'rovlar — <code>axios</code> qulayroq.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>fetch</code> 4xx/5xx ni rejection qilmaydi — <code>r.ok</code> ni tekshiring</li>
<li><code>fetch</code> 2 ta <code>await</code> oladi: response uchun, keyin <code>.json()</code> uchun</li>
<li>POST/PUT body — <code>JSON.stringify(...)</code> bilan</li>
<li><code>AbortController</code> — timeout va manual bekor qilish</li>
<li>Productionda — wrapper yozish; timeout va xato boshqaruvi har joyda</li>
</ul>
"""

L9_CODE = """\
// ─── fetch va REST API'lar — sweep ───────────────────────────────────────

// 1) Eng oddiy GET (Node 18+ / brauzer)
async function getUser(username) {
    const r = await fetch(`https://api.github.com/users/${username}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
}

// 2) Query params bilan
async function search(qatori, page = 1) {
    const params = new URLSearchParams({ q: qatori, page });
    const r = await fetch(`https://api.github.com/search/users?${params}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
}

// 3) POST + JSON body
async function createPost(token, post) {
    const r = await fetch("https://jsonplaceholder.typicode.com/posts", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(post),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
}

// 4) PUT — yangilash
async function updatePost(id, data) {
    const r = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    return await r.json();
}

// 5) DELETE
async function deletePost(id) {
    const r = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`, {
        method: "DELETE",
    });
    return r.ok;
}

// 6) Xato boshqaruvi va timeout — to'liq wrapper
async function api(url, options = {}) {
    const { timeout = 10000, body, ...rest } = options;
    const controller = new AbortController();
    const tid = setTimeout(() => controller.abort(), timeout);

    try {
        const r = await fetch(url, {
            ...rest,
            signal: controller.signal,
            headers: {
                "Content-Type": "application/json",
                ...rest.headers,
            },
            body: body !== undefined ? JSON.stringify(body) : undefined,
        });

        if (!r.ok) {
            const xato_matn = await r.text();
            throw new Error(`HTTP ${r.status}: ${xato_matn || r.statusText}`);
        }

        const tip = r.headers.get("Content-Type") || "";
        if (tip.includes("application/json")) {
            return await r.json();
        }
        return await r.text();
    } catch (e) {
        if (e.name === "AbortError") {
            throw new Error(`Timeout ${timeout}ms: ${url}`);
        }
        throw e;
    } finally {
        clearTimeout(tid);
    }
}

// 7) Real foydalanish
(async () => {
    try {
        const user = await api("https://api.github.com/users/torvalds");
        console.log(`${user.name} (${user.login}) — ${user.public_repos} repo`);
    } catch (e) {
        console.error("Xato:", e.message);
    }

    // POST misol
    try {
        const post = await api("https://jsonplaceholder.typicode.com/posts", {
            method: "POST",
            body: { title: "Test", body: "Mazmun", userId: 1 },
        });
        console.log("Yaratildi:", post);
    } catch (e) {
        console.error("Xato:", e.message);
    }

    // Parallel olish
    const repos = ["python/cpython", "facebook/react", "vuejs/vue"];
    const natijalar = await Promise.allSettled(
        repos.map((r) => api(`https://api.github.com/repos/${r}`)),
    );

    console.log("\\n=== Reposlar ===");
    natijalar.forEach((res, i) => {
        if (res.status === "fulfilled") {
            const r = res.value;
            console.log(`✅ ${r.full_name.padEnd(25)} ⭐ ${r.stargazers_count.toLocaleString()}`);
        } else {
            console.log(`❌ ${repos[i]}: ${res.reason.message}`);
        }
    });
})();

// 8) Pagination — sahifa-sahifa
async function* repoSahifalari(user) {
    let page = 1;
    while (true) {
        const repos = await api(
            `https://api.github.com/users/${user}/repos?page=${page}&per_page=30`,
        );
        if (!repos.length) break;
        yield repos;
        page++;
    }
}

(async () => {
    let jami = 0;
    for await (const sahifa of repoSahifalari("torvalds")) {
        jami += sahifa.length;
        console.log(`Sahifa olindi (${sahifa.length} ta). Jami: ${jami}`);
        if (jami >= 50) break;    // misol uchun chegara
    }
})();
"""

R3_TEXT = """\
<h2>🔁 R3 — Yangiliklar yig'uvchi (Modul 3 takrori)</h2>

<pre class="mermaid">
flowchart LR
    API["JSON API"] -->|fetch async/await| RAW["raw yangiliklar"]
    RAW -->|regex bilan tozalash| CLEAN["tozalangan matn"]
    CLEAN -->|map + dataclass-style| OBJ["Yangilik obyektlari"]
    OBJ -->|localStorage| SAVE["saqlash"]
    OBJ -->|DOM| RENDER["sahifaga chiqish"]
</pre>

<p>Modul 3 ning 3 ta texnikasi birga: <strong>Promise/async/await</strong>, <strong>fetch</strong>, <strong>xato boshqaruvi</strong>. Vazifa: API'dan yangiliklar olib, regex bilan tozalab, lokal saqlash va render qilish.</p>

<h3>🏆 5 daqiqada g'alaba — bitta katta misol</h3>

<pre><code>// 1) Fetch + xato boshqaruvi
async function olish(url, opts = {}) {
    const controller = new AbortController();
    const tid = setTimeout(() =&gt; controller.abort(), 10000);
    try {
        const r = await fetch(url, { ...opts, signal: controller.signal });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } finally {
        clearTimeout(tid);
    }
}

// 2) Tozalash
const HTML_TEG = /&lt;[^&gt;]+&gt;/g;
const KOP_BOSHLIQ = /\\s+/g;

function tozalash(matn) {
    return String(matn)
        .replace(HTML_TEG, "")
        .replace(KOP_BOSHLIQ, " ")
        .trim();
}

// 3) Transformatsiya
function yarat(raw) {
    return {
        id: raw.id,
        sarlavha: tozalash(raw.title),
        matn: tozalash(raw.body),
        so_z_soni: tozalash(raw.body).split(/\\s+/).length,
    };
}

// 4) Pipeline
async function pipeline() {
    const raw = await olish("https://jsonplaceholder.typicode.com/posts?_limit=10");
    const yangiliklar = raw.map(yarat);

    localStorage.setItem("yangiliklar", JSON.stringify(yangiliklar));

    return yangiliklar;
}

pipeline()
    .then((y) =&gt; console.log(`${y.length} ta yangilik`, y[0]))
    .catch((e) =&gt; console.error(e));
</code></pre>

<h3>3 ta texnika birga ishlaganda</h3>

<h4>Promise / async / await</h4>
<ul>
<li>Top-level <code>async</code> wrapper</li>
<li><code>try/catch</code> bilan xato — sinxron kabi</li>
<li><code>Promise.allSettled</code> — bir nechta source dan ma'lumot</li>
</ul>

<h4>fetch</h4>
<ul>
<li><code>timeout</code> bilan AbortController</li>
<li><code>r.ok</code> tekshirish — 4xx/5xx uchun</li>
<li><code>await r.json()</code> — body parse</li>
</ul>

<h4>Xato boshqaruvi</h4>
<ul>
<li>Per-operation try/catch + global handler</li>
<li>Retry / fallback patterns</li>
<li>User'ga aniq xabar — texnik detail emas</li>
</ul>

<h3>📌 Module 3 ni siz endi bilasiz</h3>
<ul>
<li>Real API'dan ma'lumot olishni 5 qatorga sig'dirasiz</li>
<li>Sinxron stilda async kod yozasiz</li>
<li>Parallel vs sekvensial — qachon qaysi</li>
<li>Productionga tayyor xato boshqaruvi</li>
</ul>
"""

R3_CODE = """\
// ─── R3: Yangiliklar yig'uvchi pipeline ──────────────────────────────────

const API = "https://jsonplaceholder.typicode.com";

// 1) Universal fetch wrapper
async function api(url, options = {}) {
    const { timeout = 10000, body, ...rest } = options;
    const controller = new AbortController();
    const tid = setTimeout(() => controller.abort(), timeout);

    try {
        const r = await fetch(url, {
            ...rest,
            signal: controller.signal,
            headers: { "Content-Type": "application/json", ...rest.headers },
            body: body !== undefined ? JSON.stringify(body) : undefined,
        });

        if (!r.ok) {
            const xato = await r.text();
            throw new Error(`HTTP ${r.status}: ${xato || r.statusText}`);
        }

        return await r.json();
    } finally {
        clearTimeout(tid);
    }
}

// 2) Regex bilan tozalash
const HTML_TEG = /<[^>]+>/g;
const KOP_BOSHLIQ = /\\s+/g;
const SO_Z = /\\b\\w+\\b/g;

function tozalash(matn) {
    return String(matn || "")
        .replace(HTML_TEG, "")
        .replace(KOP_BOSHLIQ, " ")
        .trim();
}

function so_zSoni(matn) {
    return (matn.match(SO_Z) || []).length;
}

// 3) Transformatsiya — raw -> Yangilik
function yarat(raw) {
    const sarlavha = tozalash(raw.title);
    const matn = tozalash(raw.body);
    return {
        id: raw.id,
        user_id: raw.userId,
        sarlavha,
        matn,
        so_zlar: so_zSoni(matn),
        sana: new Date().toISOString(),
    };
}

// 4) Saqlash (Node muhitida fayl, brauzerda localStorage)
function saqlash(yangiliklar) {
    if (typeof localStorage !== "undefined") {
        localStorage.setItem("yangiliklar", JSON.stringify(yangiliklar));
        console.log(`💾 localStorage ga ${yangiliklar.length} ta yangilik saqlandi`);
    } else {
        console.log(`(Test muhitida — saqlash skip)`);
    }
}

// 5) Render (brauzer'da)
function render(yangiliklar) {
    if (typeof document === "undefined") return;

    const root = document.querySelector("#root");
    if (!root) return;

    root.innerHTML = yangiliklar
        .map((y) => `
            <article style="margin: 1em 0; padding: 1em; border: 1px solid #ddd; border-radius: 6px;">
                <h3>${y.sarlavha}</h3>
                <p>${y.matn}</p>
                <small>${y.so_zlar} so'z • #${y.id}</small>
            </article>
        `)
        .join("");
}

// 6) Pipeline — bitta async funksiya
async function pipeline(limit = 10) {
    console.log("📡 Yangiliklar olinmoqda...");
    const raw = await api(`${API}/posts?_limit=${limit}`);
    console.log(`✅ ${raw.length} ta yangilik olindi`);

    const yangiliklar = raw.map(yarat);

    const jami_so_zlar = yangiliklar.reduce((acc, n) => acc + n.so_zlar, 0);
    const o_rta = jami_so_zlar / yangiliklar.length;
    const eng_uzun = yangiliklar.reduce((a, b) => (a.so_zlar > b.so_zlar ? a : b));

    console.log("\\n=== STATISTIKA ===");
    console.log(`Jami so'zlar: ${jami_so_zlar}`);
    console.log(`O'rtacha:     ${o_rta.toFixed(1)} so'z`);
    console.log(`Eng uzun:     #${eng_uzun.id} (${eng_uzun.so_zlar} so'z)`);

    saqlash(yangiliklar);
    render(yangiliklar);

    return yangiliklar;
}

// 7) Asosiy ishga tushish — xato boshqaruvi bilan
(async () => {
    try {
        const yangiliklar = await pipeline(10);
        console.log("\\nBirinchi yangilik:", yangiliklar[0]);
    } catch (e) {
        console.error("❌ Pipeline yiqildi:", e.message);
    }
})();

// 8) Bir nechta source dan ma'lumot — allSettled
async function ko_pSource() {
    const natijalar = await Promise.allSettled([
        api(`${API}/posts?_limit=3`),
        api(`${API}/comments?_limit=3`),
        api(`${API}/users?_limit=3`),
    ]);

    natijalar.forEach((r, i) => {
        const nom = ["posts", "comments", "users"][i];
        if (r.status === "fulfilled") {
            console.log(`✅ ${nom}: ${r.value.length} ta`);
        } else {
            console.log(`❌ ${nom}: ${r.reason.message}`);
        }
    });
}

ko_pSource();
"""

L10_TEXT = """\
<h2>ES6+ class'lar chuqurroq — private, static, inheritance</h2>

<pre class="mermaid">
flowchart TB
    BASE["class Hayvon"] -->|extends| DOG["class It"]
    BASE -->|extends| CAT["class Mushuk"]
    DOG -->|super init| BASE
    PRIVATE["#balans"] --> ENCAP["haqiqiy private"]
    STATIC["static count"] --> SHARED["instance'lar baham ko'radi"]
    GETSET["get/set balance"] --> COMPUTED["computed atribut"]
</pre>

<p>Class'lar asoslarini bildingiz. Endi: <strong>private maydonlar</strong> (<code>#</code>), <strong>static</strong>, <strong>getter/setter</strong>, <strong>extends + super</strong>, <strong>polimorfizm</strong>. Bu darsdan keyin sizning class'laringiz Python'dagi yaxshi tuzilgan klasslar darajasida bo'ladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Private maydonlar (#)</h4>
<pre><code>class BankHisobi {
    #balans = 0;                  // HAQIQIY private — # bilan
    #tarix = [];

    constructor(boshlangich = 0) {
        this.#balans = boshlangich;
    }

    qoshish(n) {
        if (n &lt;= 0) throw new Error("Manfiy raqam");
        this.#balans += n;
        this.#tarix.push({ amal: "+", n, vaqt: Date.now() });
    }

    get balans() { return this.#balans; }
    get tarix()  { return [...this.#tarix]; }
}

const h = new BankHisobi(100);
h.qoshish(50);
console.log(h.balans);        // 150
console.log(h.#balans);        // SyntaxError — # tashqaridan kirib bo'lmaydi</code></pre>

<h4>BLOKA 2 — Static — class'ning o'zida, instance'siz</h4>
<pre><code>class Counter {
    static instanceSoni = 0;        // class'ning maydoni
    static MAX = 1000;

    constructor() {
        Counter.instanceSoni++;
        if (Counter.instanceSoni &gt; Counter.MAX) {
            throw new Error("Juda ko'p");
        }
        this.id = Counter.instanceSoni;
    }

    static yangiManba() {            // static metod
        return new Counter();
    }

    static reset() {
        Counter.instanceSoni = 0;
    }
}

const a = new Counter();      // id=1
const b = new Counter();      // id=2
const c = Counter.yangiManba();    // id=3

console.log(Counter.instanceSoni);    // 3
// a.instanceSoni                      // undefined — static class'da, instance'da emas</code></pre>

<h4>BLOKA 3 — extends va super</h4>
<pre><code>class Hayvon {
    constructor(nom) {
        this.nom = nom;
    }
    gapir() {
        return `${this.nom}: ...`;
    }
}

class It extends Hayvon {
    constructor(nom, zot) {
        super(nom);                  // ota __init__ ni chaqirish
        this.zot = zot;
    }

    gapir() {
        return `${this.nom} (${this.zot}): vov-vov!`;
    }
}

class A_lochiIt extends It {
    constructor(nom) {
        super(nom, "labrador");
    }

    yugur() {
        const base = super.gapir();         // ota metodini chaqirish
        return `${base} (yugurmoqda)`;
    }
}

const rex = new A_lochiIt("Rex");
console.log(rex.yugur());    // "Rex (labrador): vov-vov! (yugurmoqda)"</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>class Servis {
    nom = "Default";

    constructor(nom) {
        this.nom = nom;
    }

    log() {
        console.log(`Servis: ${this.nom}`);
    }
}

const s = new Servis("API");
const fn = s.log;
fn();                  // ???</code></pre>
<p><strong>Natija:</strong> <code>TypeError: Cannot read properties of undefined</code>. Metodni boshqaga uzatganda <code>this</code> yo'qoladi (avvalgi darsdan eslang). <strong>Yechim:</strong></p>
<pre><code>// 1) Class field arrow funksiya
class Servis {
    log = () =&gt; console.log(`Servis: ${this.nom}`);     // bound to instance
}

// 2) Constructor'da bind
class Servis {
    constructor(nom) {
        this.nom = nom;
        this.log = this.log.bind(this);
    }
    log() { console.log(`Servis: ${this.nom}`); }
}</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Private maydonlar — <code>#</code></h4>
<table>
<tr><th>Sintaksis</th><th>Maqsadi</th></tr>
<tr><td><code>#field = value</code></td><td>Private instance maydoni</td></tr>
<tr><td><code>#method()</code></td><td>Private metod</td></tr>
<tr><td><code>static #field</code></td><td>Private static maydon</td></tr>
<tr><td><code>this.#field</code></td><td>Class ichida murojaat</td></tr>
</table>
<p>⚠️ Eski <code>_field</code> (underscore) — faqat <em>conventional</em> private (tashqaridan kirib bo'ladi). <code>#</code> — haqiqiy private, syntax-level himoyalangan.</p>

<h4>2. static — class'ning o'zida</h4>
<ul>
<li><strong>static maydon</strong> — barcha instance baham ko'radi (counter, MAX, config)</li>
<li><strong>static metod</strong> — instance kerak emas (factory, helper, utility)</li>
<li>Chaqirish: <code>ClassName.method()</code>, <code>ClassName.field</code></li>
</ul>

<h4>3. Getter/setter — atribut sifatida ko'rinadigan metod</h4>
<pre><code>class Doira {
    #radius;

    constructor(radius) {
        this.radius = radius;     // setter chaqiriladi
    }

    get radius() { return this.#radius; }

    set radius(val) {
        if (val &lt; 0) throw new Error("Manfiy radius");
        this.#radius = val;
    }

    get maydon() {                  // computed atribut
        return Math.PI * this.#radius ** 2;
    }
}

const d = new Doira(5);
console.log(d.radius);     // 5     — getter
d.radius = 10;             // setter — validatsiya
console.log(d.maydon);     // 314.15 — computed</code></pre>

<h4>4. extends + super — meros</h4>
<ul>
<li><code>class Sub extends Base</code> — Sub Base'dan meros oladi</li>
<li><code>super(args)</code> — constructor ichida ota constructor'ni chaqirish (BIRINCHI qator!)</li>
<li><code>super.method()</code> — ota metodini chaqirish</li>
<li>JS faqat single inheritance — mixin'lar uchun boshqa pattern'lar</li>
</ul>

<h4>5. instanceof va polimorfizm</h4>
<pre><code>console.log(rex instanceof A_lochiIt);    // true
console.log(rex instanceof It);             // true
console.log(rex instanceof Hayvon);          // true
console.log(rex instanceof Mushuk);          // false

// Polimorfizm — bir interface, har xil implementation
const hayvonlar = [new It("Rex", "lab"), new Mushuk("Mursik")];
hayvonlar.forEach((h) =&gt; console.log(h.gapir()));    // har biri o'zicha</code></pre>

<h4>6. Class vs Object literal vs Factory function</h4>
<table>
<tr><th>Class</th><th>Object literal</th><th>Factory (closure)</th></tr>
<tr><td>Bir nechta instance</td><td>Bittagina obyekt</td><td>Bir nechta + private</td></tr>
<tr><td>Inheritance qulay</td><td>Yo'q</td><td>Yo'q (mixin bilan)</td></tr>
<tr><td>this bilan diqqat</td><td>this yo'q</td><td>Closure orqali</td></tr>
<tr><td>OOP idiom</td><td>Singleton</td><td>Functional idiom</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>#field</code> — haqiqiy private (ES2022+)</li>
<li><code>static</code> — class'ning maydoni, instance'siz</li>
<li><code>get/set</code> — atribut sifatida ko'rinadigan metod, validation joyi</li>
<li><code>extends</code> + <code>super</code> — meros + ota'ga murojaat</li>
<li>Metodni uzatishda this yo'qoladi — arrow class field yoki bind</li>
</ul>
"""

L10_CODE = """\
// ─── ES6+ class'lar chuqurroq — sweep ────────────────────────────────────

// 1) Private maydonlar va metodlar
class BankHisobi {
    #balans;
    #tarix = [];
    static #ochilgan_hisoblar = 0;       // private static

    static MAX_BALANS = 1_000_000_000;

    constructor(boshlangich = 0) {
        if (boshlangich < 0) throw new Error("Manfiy boshlangich");
        this.#balans = boshlangich;
        BankHisobi.#ochilgan_hisoblar++;
        this.raqami = BankHisobi.#ochilgan_hisoblar;
    }

    static jamiOchilgan() {
        return BankHisobi.#ochilgan_hisoblar;
    }

    #yozish(amal, n) {                    // private metod
        this.#tarix.push({ amal, n, vaqt: Date.now() });
    }

    qoshish(n) {
        if (n <= 0) throw new Error("Manfiy yoki nol");
        if (this.#balans + n > BankHisobi.MAX_BALANS) {
            throw new Error("Limit oshib ketdi");
        }
        this.#balans += n;
        this.#yozish("+", n);
        return this.#balans;
    }

    ayirish(n) {
        if (n > this.#balans) throw new Error("Yetarli mablag' yo'q");
        this.#balans -= n;
        this.#yozish("-", n);
        return this.#balans;
    }

    get balans() { return this.#balans; }
    get tarix()  { return [...this.#tarix]; }

    toString() {
        return `BankHisobi #${this.raqami} balans=${this.#balans}`;
    }
}

const h1 = new BankHisobi(1000);
const h2 = new BankHisobi(500);
h1.qoshish(500);
h2.qoshish(200);
console.log(h1.toString());
console.log(h2.toString());
console.log(`Jami ochilgan: ${BankHisobi.jamiOchilgan()}`);

// 2) Getter/setter bilan validatsiya
class Doira {
    #radius;

    constructor(radius) {
        this.radius = radius;        // setter ishlatadi
    }

    get radius() { return this.#radius; }

    set radius(val) {
        if (typeof val !== "number" || val < 0) {
            throw new TypeError("Radius musbat son bo'lishi kerak");
        }
        this.#radius = val;
    }

    get maydon() { return Math.PI * this.#radius ** 2; }
    get aylana() { return 2 * Math.PI * this.#radius; }

    toString() { return `Doira r=${this.#radius} S=${this.maydon.toFixed(2)}`; }
}

const d = new Doira(5);
console.log(`${d}`);
d.radius = 10;
console.log(`Yangi: ${d}`);
try { d.radius = -1; } catch (e) { console.log("Tutib oldim:", e.message); }

// 3) Inheritance + super
class Hayvon {
    constructor(nom, yoshi) {
        this.nom = nom;
        this.yoshi = yoshi;
    }

    gapir() {
        return `${this.nom}: ...`;
    }

    toString() {
        return `${this.constructor.name}(${this.nom}, ${this.yoshi} yosh)`;
    }
}

class It extends Hayvon {
    constructor(nom, yoshi, zot) {
        super(nom, yoshi);
        this.zot = zot;
    }

    gapir() {
        return `${this.nom} (${this.zot}): vov-vov!`;
    }
}

class A_lochiIt extends It {
    constructor(nom, yoshi) {
        super(nom, yoshi, "labrador");
    }

    gapirVaYugur() {
        const base = super.gapir();      // ota metodi
        return `${base} *yugurmoqda*`;
    }
}

const rex = new A_lochiIt("Rex", 3);
console.log(rex.gapir());
console.log(rex.gapirVaYugur());
console.log(rex.toString());
console.log(rex instanceof A_lochiIt, rex instanceof It, rex instanceof Hayvon);

// 4) Polimorfizm
class Mushuk extends Hayvon {
    gapir() { return `${this.nom}: myau!`; }
}

const hayvonlar = [
    new It("Rex", 3, "lab"),
    new Mushuk("Mursik", 5),
    new A_lochiIt("Rocky", 2),
];

console.log("\\n=== Polimorfizm ===");
hayvonlar.forEach((h) => console.log(h.gapir()));

// 5) Static factory pattern
class Foydalanuvchi {
    constructor(ism, yosh, rol) {
        this.ism = ism;
        this.yosh = yosh;
        this.rol = rol;
    }

    static admin(ism) {
        return new Foydalanuvchi(ism, 25, "admin");
    }

    static guest() {
        return new Foydalanuvchi("Mehmon", 0, "guest");
    }
}

const a = Foydalanuvchi.admin("Ali");
const g = Foydalanuvchi.guest();
console.log(a, g);

// 6) Iterable class
class Sinf {
    #talabalar = [];

    constructor(nom) { this.nom = nom; }

    qosh(t) { this.#talabalar.push(t); }

    get talabalar_soni() { return this.#talabalar.length; }

    *[Symbol.iterator]() {                // generator metodi
        for (const t of this.#talabalar) yield t;
    }
}

const s = new Sinf("10-A");
["Ali", "Vali", "Gulya"].forEach((n) => s.qosh(n));

console.log(`\\n${s.nom} (${s.talabalar_soni} ta):`);
for (const t of s) console.log(`  - ${t}`);
console.log([...s]);    // ['Ali', 'Vali', 'Gulya']
"""

L11_TEXT = """\
<h2>🚀 CAPSTONE — TODO ilova (class + localStorage + fetch)</h2>

<pre class="mermaid">
flowchart TB
    USER["foydalanuvchi (DOM)"] -->|qo'shish, o'chirish, belgilash| STORE["TodoStore class"]
    STORE -->|@private | STATE["private todos"]
    STATE -->|JSON.stringify| LS["localStorage"]
    STORE -->|fetch| API["mock API"]
    STATE -->|render| DOM["DOM yangilanishi"]
</pre>

<p>Endi bu kursning <strong>11 ta texnikasi</strong> birga ishlaydi. Loyiha — brauzerda ishlovchi TODO ilova:</p>

<ul>
<li><strong>ES6+ class</strong> — TodoStore, Todo</li>
<li><strong>private maydonlar</strong> — <code>#todos</code>, <code>#counter</code></li>
<li><strong>get/set</strong> — computed (filter natijasi, statistika)</li>
<li><strong>localStorage</strong> — persistensiya</li>
<li><strong>fetch + async/await</strong> — server bilan sinxronlash (mock)</li>
<li><strong>arrow + destructuring</strong> — har joyda</li>
<li><strong>map/filter/reduce</strong> — filter va statistika</li>
<li><strong>template literallar</strong> — DOM render</li>
<li><strong>closures</strong> — event handler state'i</li>
<li><strong>spread/rest</strong> — immutable update</li>
<li><strong>this + bind</strong> — DOM event handler</li>
</ul>

<h3>🏆 Loyiha demosi</h3>

<pre><code>const store = new TodoStore({ apiBase: "/api" });

// Yangi vazifa
store.qosh("Python o'rganish", { kategoriya: "ta'lim", muhim: true });
store.qosh("Sport zal", { kategoriya: "sog'liq" });
store.qosh("Loyihani tugatish", { kategoriya: "ish", muhim: true });

// Bajarilgan deb belgilash
store.belgilab(1);

// Filterlash
console.log(store.bajarilmagan);
console.log(store.kategoriya_bo_yicha("ish"));

// Statistika
console.log(store.statistika);
// { jami: 3, bajarildi: 1, qolgan: 2, foiz: 33.3 }

// localStorage'ga avtomatik saqlanadi
// Sahifa qayta yuklansa — vazifalar saqlangan
</code></pre>

<h3>Loyihaning class shakli</h3>

<pre><code>class Todo {
    constructor({ id, matn, bajarildi = false, kategoriya = "boshqa", muhim = false }) {
        this.id = id;
        this.matn = matn;
        this.bajarildi = bajarildi;
        this.kategoriya = kategoriya;
        this.muhim = muhim;
        this.sana = new Date().toISOString();
    }

    get tasvir() {
        const tick = this.bajarildi ? "✅" : "⏳";
        const star = this.muhim ? "⭐" : "  ";
        return `${tick} ${star} [${this.kategoriya}] ${this.matn}`;
    }
}

class TodoStore {
    #todos = [];
    #counter = 0;
    #saqlash_kaliti = "todos-v1";
    #apiBase;

    constructor({ apiBase = "" } = {}) {
        this.#apiBase = apiBase;
        this.#yuklash();
    }

    // Public API
    qosh(matn, opts = {}) {
        const id = ++this.#counter;
        this.#todos.push(new Todo({ id, matn, ...opts }));
        this.#saqlash();
        return id;
    }

    belgilab(id) {
        const t = this.#todos.find(t =&gt; t.id === id);
        if (!t) throw new Error("Topilmadi");
        t.bajarildi = !t.bajarildi;
        this.#saqlash();
    }

    o_chir(id) {
        const idx = this.#todos.findIndex(t =&gt; t.id === id);
        if (idx === -1) return;
        this.#todos.splice(idx, 1);
        this.#saqlash();
    }

    // Computed (getter'lar)
    get hammasi()         { return [...this.#todos]; }
    get bajarilmagan()    { return this.#todos.filter(t =&gt; !t.bajarildi); }
    get bajarilgan()      { return this.#todos.filter(t =&gt;  t.bajarildi); }
    get muhimlar()        { return this.#todos.filter(t =&gt;  t.muhim); }

    kategoriya_bo_yicha(kat) {
        return this.#todos.filter(t =&gt; t.kategoriya === kat);
    }

    get statistika() {
        const jami = this.#todos.length;
        const bajarildi = this.bajarilgan.length;
        return {
            jami,
            bajarildi,
            qolgan: jami - bajarildi,
            foiz: jami ? Math.round((bajarildi / jami) * 100) : 0,
        };
    }

    // Server bilan sinxronlash
    async sync() {
        try {
            const r = await fetch(`${this.#apiBase}/todos`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(this.#todos),
            });
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return await r.json();
        } catch (e) {
            console.error("Sync xato:", e.message);
            return null;
        }
    }

    // Private — localStorage
    #saqlash() {
        localStorage.setItem(this.#saqlash_kaliti, JSON.stringify(this.#todos));
    }

    #yuklash() {
        try {
            const raw = localStorage.getItem(this.#saqlash_kaliti);
            if (!raw) return;
            const data = JSON.parse(raw);
            this.#todos = data.map(t =&gt; new Todo(t));
            this.#counter = Math.max(0, ...this.#todos.map(t =&gt; t.id));
        } catch (e) {
            console.error("Yuklash xatosi:", e);
        }
    }
}
</code></pre>

<h3>Texnikalar qaerda ishlatilgan</h3>

<table>
<tr><th>Texnika</th><th>Qaerda</th></tr>
<tr><td>ES6+ class + #</td><td><code>TodoStore</code>, <code>Todo</code>, <code>#todos</code>, <code>#counter</code></td></tr>
<tr><td>get / set</td><td><code>hammasi</code>, <code>bajarilmagan</code>, <code>statistika</code></td></tr>
<tr><td>destructuring</td><td>constructor argumenti, <code>{ matn, opts }</code></td></tr>
<tr><td>arrow + array methods</td><td><code>.filter</code>, <code>.find</code>, <code>.map</code></td></tr>
<tr><td>spread</td><td>immutable nusxa <code>[...this.#todos]</code></td></tr>
<tr><td>async/await + fetch</td><td><code>sync()</code> metodida</td></tr>
<tr><td>localStorage</td><td><code>#saqlash</code>, <code>#yuklash</code></td></tr>
<tr><td>template literallar</td><td><code>get tasvir</code></td></tr>
<tr><td>closures (DOM bilan)</td><td>event handler'larda (UI qatlamida)</td></tr>
<tr><td>try/catch</td><td>fetch va JSON parsing'da</td></tr>
</table>

<h3>Sizning vazifangiz</h3>

<p>Code section'dagi to'liq versiyani saqlang va kengaytirib chiqing:</p>

<ol>
<li><strong>Filterlash UI</strong> — barchasi / bajarilmagan / muhim'lar</li>
<li><strong>Tahrirlash</strong> — vazifa matnini click qilib o'zgartirish</li>
<li><strong>Saralash</strong> — sana, muhim, kategoriya bo'yicha</li>
<li><strong>Qidirish</strong> — debounce bilan</li>
<li><strong>Dark mode toggle</strong> — localStorage bilan</li>
<li><strong>Drag-and-drop</strong> — vazifalarni tartibga solish</li>
<li><strong>Eksport / Import</strong> — JSON yuklab olish, yuklash</li>
</ol>

<h3>📌 Kurs yakuni</h3>
<ul>
<li>Endi siz <strong>modern JavaScript</strong>'da yozasiz</li>
<li>Sizning kod'laringiz <strong>encapsulated, async-friendly, idiomatic</strong></li>
<li>Real APIs, brauzer storage va DOM bilan ishlay olasiz</li>
<li>Class'laringiz endi anketa emas — <strong>boshqaruvchi entitilar</strong></li>
<li>Keyingi qadam: React (yoki Vue), TypeScript, testlash (Jest/Vitest)</li>
</ul>

<p><strong>Tabriklaymiz!</strong> Siz JavaScript: Keyingi Bosqich kursini tamomladingiz. 🎉</p>
"""

L11_CODE = """\
// ─── CAPSTONE: TODO ilova (class + localStorage + fetch) ─────────────────
//
// To'liq ishchi versiya. Brauzerda HTML fayl bilan birga ishlatish mumkin:
//
//   <!doctype html>
//   <html>
//   <body>
//     <input id="matn" placeholder="Yangi vazifa..."/>
//     <button id="qosh">Qo'shish</button>
//     <ul id="lst"></ul>
//     <pre id="stat"></pre>
//     <script type="module" src="app.js"></script>
//   </body>
//   </html>

// 1) Todo domain klassi
class Todo {
    constructor({ id, matn, bajarildi = false, kategoriya = "boshqa", muhim = false, sana }) {
        this.id = id;
        this.matn = matn;
        this.bajarildi = bajarildi;
        this.kategoriya = kategoriya;
        this.muhim = muhim;
        this.sana = sana || new Date().toISOString();
    }

    get tasvir() {
        const tick = this.bajarildi ? "✅" : "⏳";
        const star = this.muhim ? "⭐" : "  ";
        return `${tick} ${star} [${this.kategoriya}] ${this.matn}`;
    }
}

// 2) TodoStore — encapsulated state
class TodoStore {
    #todos = [];
    #counter = 0;
    #kalit = "todos-v1";
    #apiBase;
    #listeners = [];

    constructor({ apiBase = "" } = {}) {
        this.#apiBase = apiBase;
        this.#yuklash();
    }

    // Subscribe — DOM yangilanish uchun
    on_change(fn) {
        this.#listeners.push(fn);
        return () => {
            this.#listeners = this.#listeners.filter((f) => f !== fn);
        };
    }

    #notify() {
        this.#listeners.forEach((fn) => fn(this));
    }

    // ── Public API ────────────────────────────────────────────────────
    qosh(matn, opts = {}) {
        if (!matn || !matn.trim()) throw new Error("Bo'sh matn");
        const id = ++this.#counter;
        this.#todos.push(new Todo({ id, matn: matn.trim(), ...opts }));
        this.#saqlash();
        this.#notify();
        return id;
    }

    belgilab(id) {
        const t = this.#todos.find((t) => t.id === id);
        if (!t) throw new Error(`Topilmadi: ${id}`);
        t.bajarildi = !t.bajarildi;
        this.#saqlash();
        this.#notify();
    }

    o_chir(id) {
        const idx = this.#todos.findIndex((t) => t.id === id);
        if (idx === -1) return;
        this.#todos.splice(idx, 1);
        this.#saqlash();
        this.#notify();
    }

    tahrirla(id, yangi_matn) {
        const t = this.#todos.find((t) => t.id === id);
        if (!t) return;
        t.matn = yangi_matn.trim();
        this.#saqlash();
        this.#notify();
    }

    nollash() {
        this.#todos = [];
        this.#counter = 0;
        this.#saqlash();
        this.#notify();
    }

    // ── Computed atributlar ──────────────────────────────────────────
    get hammasi()      { return [...this.#todos]; }
    get bajarilmagan() { return this.#todos.filter((t) => !t.bajarildi); }
    get bajarilgan()   { return this.#todos.filter((t) =>  t.bajarildi); }
    get muhimlar()     { return this.#todos.filter((t) =>  t.muhim); }

    kategoriya_bo_yicha(kat) {
        return this.#todos.filter((t) => t.kategoriya === kat);
    }

    qidirish(qatori) {
        const q = qatori.toLowerCase();
        return this.#todos.filter((t) => t.matn.toLowerCase().includes(q));
    }

    get statistika() {
        const jami = this.#todos.length;
        const bajarildi = this.bajarilgan.length;
        return {
            jami,
            bajarildi,
            qolgan: jami - bajarildi,
            foiz: jami ? Math.round((bajarildi / jami) * 100) : 0,
            kategoriyalar: [...new Set(this.#todos.map((t) => t.kategoriya))],
        };
    }

    // ── Server bilan sinxronlash ─────────────────────────────────────
    async sync() {
        if (!this.#apiBase) return;
        try {
            const r = await fetch(`${this.#apiBase}/todos`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(this.#todos),
            });
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const natija = await r.json();
            console.log("Sync OK:", natija);
            return natija;
        } catch (e) {
            console.error("Sync xato:", e.message);
            return null;
        }
    }

    // ── Private persistensiya ────────────────────────────────────────
    #saqlash() {
        try {
            localStorage.setItem(this.#kalit, JSON.stringify(this.#todos));
        } catch (e) {
            console.error("Saqlash xato:", e);
        }
    }

    #yuklash() {
        try {
            const raw = localStorage.getItem(this.#kalit);
            if (!raw) return;
            const data = JSON.parse(raw);
            this.#todos = data.map((d) => new Todo(d));
            this.#counter = Math.max(0, ...this.#todos.map((t) => t.id));
        } catch (e) {
            console.error("Yuklash xato:", e);
        }
    }
}

// 3) Demo (Node yoki test muhitida — localStorage bo'lmasa skip)
if (typeof localStorage !== "undefined") {
    const store = new TodoStore({ apiBase: "" });
    store.nollash();

    store.qosh("Python o'rganish", { kategoriya: "ta'lim", muhim: true });
    store.qosh("Sport zal", { kategoriya: "sog'liq" });
    store.qosh("Loyihani tugatish", { kategoriya: "ish", muhim: true });
    store.qosh("Kitob o'qish", { kategoriya: "ta'lim" });

    store.belgilab(1);

    console.log("\\n=== HAMMASI ===");
    store.hammasi.forEach((t) => console.log(t.tasvir));

    console.log("\\n=== STATISTIKA ===");
    console.log(store.statistika);

    console.log("\\n=== MUHIMLAR ===");
    store.muhimlar.forEach((t) => console.log(t.tasvir));

    console.log("\\n=== Bajarilmagan ish kategoriyasi ===");
    store.kategoriya_bo_yicha("ish")
        .filter((t) => !t.bajarildi)
        .forEach((t) => console.log(t.tasvir));
}

// 4) DOM bog'lash (brauzer'da) — kommentdan chiqarib ishlating
//
// const store = new TodoStore({ apiBase: "/api" });
// const $matn = document.querySelector("#matn");
// const $qosh = document.querySelector("#qosh");
// const $lst  = document.querySelector("#lst");
// const $stat = document.querySelector("#stat");
//
// function render(s) {
//     $lst.innerHTML = s.hammasi
//         .map((t) => `
//             <li data-id="${t.id}">
//                 <span style="text-decoration:${t.bajarildi ? "line-through" : "none"}">
//                     ${t.tasvir}
//                 </span>
//                 <button data-act="toggle">✓</button>
//                 <button data-act="o_chir">×</button>
//             </li>
//         `)
//         .join("");
//
//     $stat.textContent = JSON.stringify(s.statistika, null, 2);
// }
//
// // Subscribe — har o'zgarishda DOM yangilanadi
// store.on_change(render);
//
// // Initial render
// render(store);
//
// // Add tugmasi
// $qosh.addEventListener("click", () => {
//     try {
//         store.qosh($matn.value);
//         $matn.value = "";
//         $matn.focus();
//     } catch (e) {
//         alert(e.message);
//     }
// });
//
// // Enter bilan ham qo'shish
// $matn.addEventListener("keydown", (e) => {
//     if (e.key === "Enter") $qosh.click();
// });
//
// // Event delegation — har LI tugmasi uchun alohida listener emas
// $lst.addEventListener("click", (e) => {
//     const li = e.target.closest("li");
//     if (!li) return;
//     const id = Number(li.dataset.id);
//     const act = e.target.dataset.act;
//     if (act === "toggle") store.belgilab(id);
//     if (act === "o_chir") store.o_chir(id);
// });
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise builders
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# Per-lesson exercises
# ─────────────────────────────────────────────────────────────────────────────
L1_EX: list = [
    mc("`const f = x => x * 2` — bu nima qaytaradi?",
       ["Funksiya — bir argument oluvchi va uni 2 ga ko'paytirib qaytaruvchi",
        "Sonni 2 ga ko'paytiradi",
        "Xatolik — sintaksis noto'g'ri",
        "undefined"],
       "A",
       hint="Arrow funksiyaning eng qisqa shakli — bitta argument, ifoda.",
       diff="Easy", pts=2),
    mc("Quyidagi qaysi qator obyektdan TO'G'RI destructuring?",
       ["const { ism, yosh } = foydalanuvchi;",
        "const ism, yosh = foydalanuvchi;",
        "const [ism, yosh] = foydalanuvchi;",
        "const ism = foydalanuvchi.ism, yosh = foydalanuvchi.yosh;"],
       "A,D", multi=True,
       hint="A — destructuring. D — manual eski uslub (ham to'g'ri). B — sintaksis xato. C — array destructuring, obyekt uchun emas.",
       diff="Medium", pts=3),
    mc("`(...args) => Math.max(...args)` — qaysi qism rest, qaysi spread?",
       ["Ikkalasi rest",
        "Ikkalasi spread",
        "Birinchi `...args` — rest (parametr), ikkinchi `...args` — spread (chaqiruv)",
        "Birinchi spread, ikkinchi rest"],
       "C",
       hint="Parametrda yig'adi (rest), chaqiruvda ochadi (spread).",
       explanation="`...` belgisi joyga qarab ikki xil ma'noda — kontekst muhim.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi holatlarda arrow funksiya YOMON tanlov?",
       ["Massiv .map() callback'i",
        "Obyekt metodi — `this` orqali obyektga murojaat kerak",
        "DOM event handler — `this` element bo'lishi kerak",
        "Constructor — `new` bilan chaqirish",
        "setTimeout callback"],
       "B,C,D", multi=True,
       hint="Arrow lexical `this` qiladi — chaqirilgan obyekt yoki elementga emas, atrofdagi scope ga ishora qiladi.",
       diff="Medium", pts=3),
    dd("`eski` obyektining `sevimli` massiviga yangi element qo'shgan yangi obyekt yaratish bosqichlari",
       ["const eski = { ism: 'Ali', sevimli: ['python'] };",
        "const yangi = {",
        "    ...eski,",
        "    sevimli: [...eski.sevimli, 'js'],",
        "};",
        "console.log(eski);    // o'zgarmagan",
        "console.log(yangi);   // yangi sevimli bilan"],
       diff="Medium", pts=3),
    ti("`const yarat = id => { id }` — bu nima qaytaradi va nima uchun?",
       "undefined qaytaradi. Sabab: { } belgisi — funksiya tanasi (block), obyekt emas. Tana ichida "
       "`id` ifodasi bor lekin `return` yo'q, shuning uchun undefined. Obyekt qaytarish uchun "
       "qavslar ichida olish kerak: `const yarat = id => ({ id });`. Bu yerda ({ ... }) — yashirin "
       "shorthand `({ id: id })` uchun, va tashqi qavs Python parser'ga 'bu obyekt, block emas' "
       "deydi. Bu juda ko'p uchraydigan xato, ayniqsa React'da setState callback yozayotganda.",
       hint="{ } — block tanasi yoki obyekt. Arrow uchun obyekt qaytarmoqchi bo'lsang qavsga ol.",
       diff="Hard", pts=4),
    mc("`function f({ ism, yosh = 18 } = {}) { return ism; }` — `f()` chaqirilganda nima bo'ladi?",
       ["TypeError",
        "undefined qaytaradi",
        "'ism' string qaytaradi",
        "yosh 18 bo'ladi"],
       "B",
       hint="Default qiymat `= {}` — argument berilmasa bo'sh obyekt. Undan destructure qilingan `ism` — undefined.",
       explanation="Destructuring + default kombinatsiyasi — fail-safe API uchun ideal.",
       diff="Hard", pts=4),
]
L2_EX: list = [
    mc("`[1, 2, 3].map(x => x + 1)` nima qaytaradi?",
       ["[2, 3, 4]", "[1, 2, 3]", "6", "undefined"],
       "A",
       hint="map — har elementga funksiyani qo'llaydi, yangi massiv qaytaradi.",
       diff="Easy", pts=2),
    mc("`reduce` da `initialValue` (boshlang'ich qiymat) berilmasa nima bo'ladi?",
       ["TypeError doimo",
        "Birinchi element initialValue deb olinadi, sikl 2-elementdan boshlanadi (bo'sh massiv uchun TypeError)",
        "0 deb olinadi",
        "undefined qaytadi"],
       "B",
       hint="reduce har doim 2 argument bilan ishlatish tavsiya etiladi — buglarni oldini oladi.",
       explanation="Boshlang'ich qiymat tipini ham aniqlaydi — yig'indi uchun 0, obyekt uchun {}, massiv uchun [].",
       diff="Medium", pts=3),
    mc("`forEach` va `map` orasidagi farq nima?",
       ["Hech qanday farq — bir narsa",
        "forEach hech narsa qaytarmaydi (yon ta'sir uchun), map yangi massiv qaytaradi",
        "forEach faqat sonlar uchun, map har narsa uchun",
        "map tezroq"],
       "B",
       hint="forEach — undefined qaytaradi, transformatsiya uchun emas.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi holatlarda QAYSI metod ideal?",
       ["Birinchi 70+ ballini topish — find",
        "Hamma talaba o'tganmi tekshirish — every",
        "Talabalar ballini 100 ga ko'paytirish — map",
        "Faqat 70+ ballilarni saqlash — filter",
        "Hech bo'lmasa bittasi o'tganmi — some"],
       "A,B,C,D,E", multi=True,
       hint="Hammasi to'g'ri. Metodni semantikasi bo'yicha tanlash idiomatic JS belgisi.",
       diff="Medium", pts=3),
    dd("Mahsulot ro'yxatidan TOP 3 eng qimmat 5000+ narxlilarni topish bosqichlari",
       ["const mahsulotlar = [",
        "    { nom: 'Olma', narx: 12000 },",
        "    { nom: 'Non',  narx: 4000 },",
        "    { nom: 'Sut',  narx: 9000 },",
        "];",
        "",
        "const top3 = mahsulotlar",
        "    .filter(m => m.narx >= 5000)",
        "    .sort((a, b) => b.narx - a.narx)",
        "    .slice(0, 3);",
        "",
        "console.log(top3);"],
       diff="Medium", pts=3),
    ti("`reduce` bilan obyektlar massivini ID bo'yicha dict ga aylantirish — qanday yoziladi?",
       "Pattern: const dict = arr.reduce((acc, item) => { acc[item.id] = item; return acc; }, {}); "
       "Yoki spread bilan: arr.reduce((acc, item) => ({ ...acc, [item.id]: item }), {}); "
       "Birinchi varianti tezroq (har iteratsiyada yangi obyekt yaratmaydi). "
       "Foydaliroq: arr.reduce((acc, item) => Object.assign(acc, { [item.id]: item }), {}); "
       "ES2019+ da yana qulayroq: Object.fromEntries(arr.map(item => [item.id, item])). "
       "Bu pattern ID -> obyekt qidiruvini O(1) qiladi (oddiy find — O(n)).",
       hint="initialValue — {}. acc[item.id] = item; return acc; — eng tez.",
       diff="Hard", pts=4),
    mc("`[1, 2, 3].map(x => { x * 2 })` nima qaytaradi?",
       ["[2, 4, 6]",
        "[undefined, undefined, undefined] — { } tana, return yo'q",
        "[1, 2, 3]",
        "TypeError"],
       "B",
       hint="Arrow tana { } bilan — return aniq kerak.",
       explanation="To'g'ri: `.map(x => x * 2)` (ifoda) yoki `.map(x => { return x * 2; })`.",
       diff="Medium", pts=3),
]
L3_EX: list = [
    mc("Template literal qaysi belgi bilan o'raladi?",
       ["Bir tirnoq '...'",
        "Qo'sh tirnoq \"...\"",
        "Backtick `...`",
        "Slash /.../"],
       "C",
       hint="Backtick — klaviaturada Tab tugmasi tepasidagi.",
       diff="Easy", pts=2),
    mc("`\"Salom, ${ism}!\"` (qo'sh tirnoq bilan) — nima chiqaradi?",
       ["Salom, Ali!",
        "Salom, ${ism}!",
        "TypeError",
        "undefined"],
       "B",
       hint="Template literal FAQAT backtick bilan ishlaydi.",
       diff="Easy", pts=2),
    mc("`\"olma olma\".replace(\"olma\", \"non\")` natijasi qanday?",
       ["non non",
        "non olma",
        "olma non",
        "olma olma"],
       "B",
       hint="replace — faqat BIRINCHI mos kelishni almashtiradi.",
       explanation="Hammasini almashtirish uchun replaceAll yoki regex /g flag bilan.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi string metodlari boolean qaytaradi?",
       ["includes",
        "startsWith",
        "endsWith",
        "trim",
        "split"],
       "A,B,C", multi=True,
       hint="trim — yangi string qaytaradi, split — massiv. Qolganlari true/false.",
       diff="Medium", pts=3),
    dd("Talabalar ro'yxatini jadval ko'rinishida chiqarish bosqichlari",
       ["const talabalar = [",
        "    { ism: 'Ali',   ball: 87 },",
        "    { ism: 'Gulya', ball: 92 },",
        "];",
        "",
        "console.log('Ism'.padEnd(12) + 'Ball');",
        "console.log('─'.repeat(18));",
        "",
        "talabalar.forEach(t => {",
        "    console.log(t.ism.padEnd(12) + String(t.ball).padStart(3, '0'));",
        "});"],
       diff="Medium", pts=3),
    ti("Tagged template (`tag\\`...\\``) qachon foydali va oddiy template literal'dan nimasi yaxshi?",
       "Tagged template — funksiya stringning literal bo'laklarini va ${ } qiymatlarini ALOHIDA "
       "argumentlar sifatida qabul qiladi. Foydali holatlar: 1) SQL queries — qiymatlarni sanitizatsiya "
       "qilish (SQL injection oldini olish); 2) HTML render — XSS oldini olish (qiymatlarni escape "
       "qilish, lekin literal HTML belgilarini buzmasdan); 3) i18n — qiymat o'rinlarini tarjima "
       "bilan ko'paytirish; 4) Custom formatting — har qiymat bo'yicha har xil transformatsiya. "
       "Oddiy template literal — string concatenatsiya, hammasi sof matn bo'lib chiqadi. "
       "Tagged template — siz hisoblanuvchi qiymatlarni LITERAL matndan ajrata olasiz.",
       hint="Sanitizatsiya, XSS oldini olish, i18n.",
       diff="Hard", pts=4),
    mc("`(1500000).toLocaleString('uz-UZ', {style: 'currency', currency: 'UZS'})` nima chiqaradi?",
       ["1500000",
        "1 500 000 UZS yoki 1,500,000 UZS (format'ga qarab)",
        "UZS 1500000",
        "TypeError"],
       "B",
       hint="toLocaleString — locale va options'ga qarab chiroyli format.",
       diff="Medium", pts=3),
]
R1_EX: list = [
    mc("`[...new Set(arr)]` — bu nima qiladi?",
       ["Massivni nusxalaydi",
        "Massivdan takrorlanmas (unique) qiymatlar massivini olish",
        "Set yaratadi",
        "TypeError"],
       "B",
       hint="Set — takrorsiz; spread bilan massivga ochiladi.",
       diff="Easy", pts=2),
    mc("`savdolar.reduce((acc, {sotuvchi, narx}) => { ... })` — qaysi texnikalar birga ishlatilgan?",
       ["reduce + destructuring + arrow",
        "Faqat reduce",
        "for sikl + obyekt",
        "filter + map"],
       "A",
       hint="3 ta texnika birga: deklarativ JS belgisi.",
       diff="Easy", pts=2),
    mc("`Object.entries(jami_per_sot).sort(([, a], [, b]) => b - a)` natijasi qanday?",
       ["Sotuvchi -> summa juftliklarining alifbo tartibida",
        "Summa bo'yicha kamayuvchi tartibda saralangan juftliklar",
        "Faqat summa massivi",
        "TypeError"],
       "B",
       hint="`([, a], [, b])` — destructuring: birinchi elementni o'tkazib yuboradi, ikkinchini (summa) oladi. `b - a` — kamayuvchi.",
       explanation="Object.entries -> [[key, value], ...]. Compare function destructure qilib summalarni taqqoslaydi.",
       diff="Hard", pts=4),
    mc("Hisobot uchun chiroyli summa formatlash uchun qaysilari TO'G'RI?",
       ["summa.toLocaleString('uz-UZ')",
        "summa.toString()",
        "summa.toFixed(2)",
        "summa.toLocaleString('uz-UZ', {style: 'currency', currency: 'UZS'})"],
       "A,C,D", multi=True,
       hint="A va D — chiroyli format. C — o'nlik raqam. B — oddiy.",
       diff="Medium", pts=3),
    dd("Sotuvchi -> jami summa dict yaratish bosqichlari",
       ["const savdolar = [",
        "    { sotuvchi: 'Ali', narx: 100 },",
        "    { sotuvchi: 'Vali', narx: 50 },",
        "    { sotuvchi: 'Ali', narx: 30 },",
        "];",
        "",
        "const jami = savdolar.reduce((acc, { sotuvchi, narx }) => {",
        "    acc[sotuvchi] = (acc[sotuvchi] || 0) + narx;",
        "    return acc;",
        "}, {});",
        "",
        "console.log(jami);"],
       diff="Medium", pts=3),
    ti("Nima uchun `reduce` ichida `acc[key] = (acc[key] || 0) + val` patterni ishlatiladi?",
       "Birinchi marta key uchrasa acc[key] undefined bo'ladi — `undefined + val` natijasi NaN beradi. "
       "`(acc[key] || 0)` — agar undefined yoki 0 bo'lsa 0 qaytaradi, bo'lmasa hozirgi qiymat. Shunday "
       "qilib har key uchun yig'ish ishonchli boshlanadi. Alternatives: 1) `acc[key] ??= 0` (nullish "
       "assignment, ES2021+); 2) Map ishlatish — get/set bilan ravshanroq; 3) Object.fromEntries + "
       "filter. Eng tez-tez uchraydigan: || 0 patterni. Lekin: `0 || 0` — to'g'ri 0 qaytaradi (falsy), "
       "lekin agar bizning value boshqa falsy qiymat bo'lsa (masalan, bo'sh string), muammo bo'ladi. "
       "Shu sababli `??` (nullish coalescing) yaxshiroq variant — faqat null/undefined bilan ishlaydi.",
       hint="undefined + N = NaN — buni oldini olish kerak.",
       diff="Hard", pts=4),
]
L4_EX: list = [
    mc("Closure nima?",
       ["Class'ning private maydoni",
        "Ichki funksiya + uning yaratilgan paytdagi tashqi scope",
        "Faqat ES6 da paydo bo'lgan yangi xususiyat",
        "Funksiya nomining boshqacha aytilishi"],
       "B",
       hint="Funksiya 'tug'ilgan joyini' yodda saqlaydi.",
       diff="Easy", pts=2),
    mc("`counterYarat()` 3 marta chaqirilsa nima bo'ladi?",
       ["3 ta closure — har birining o'z count'i bor",
        "1 ta umumiy count — uchovi baham ko'radi",
        "TypeError",
        "Birinchi marta count yaratiladi, qolgan 2 ta nusxa"],
       "A",
       hint="Har funksiya chaqiruvi alohida scope yaratadi.",
       explanation="Bu pattern modul/instans yaratish uchun ishlatiladi — har biri o'z holatiga ega.",
       diff="Medium", pts=3),
    mc("Quyidagi for siklida nima chiqadi?\n```\nfor (var i = 0; i < 3; i++) {\n    setTimeout(() => console.log(i), 100);\n}\n```",
       ["0 1 2",
        "3 3 3",
        "undefined undefined undefined",
        "TypeError"],
       "B",
       hint="`var i` function-scoped — sikl tugaganda i=3.",
       explanation="100ms keyin chaqirilganda — sikl allaqachon tugagan, hammasi bitta `i` ni ko'radi.",
       diff="Medium", pts=3),
    mc("Yuqoridagi bug'ni qanday tuzatish mumkin?",
       ["var o'rniga let ishlatish",
        "setTimeout ichida IIFE — `(function(j){setTimeout(()=>console.log(j),100)})(i)`",
        ".forEach bilan ishlash",
        "Hech qaysisi — bu xato emas"],
       "A,B,C", multi=True,
       hint="3 ta yo'l: let (block scope), IIFE (har iteratsiya alohida scope), forEach (parametr alohida).",
       diff="Medium", pts=3),
    dd("Private `secret` saqlaydigan obyekt yaratish bosqichlari (closure pattern)",
       ["function makeSafe(secret) {",
        "    let _secret = secret;",
        "",
        "    return {",
        "        get: () => _secret,",
        "        set: (yangi) => {",
        "            if (typeof yangi !== 'string') throw new Error('string kerak');",
        "            _secret = yangi;",
        "        },",
        "    };",
        "}",
        "",
        "const safe = makeSafe('parol');",
        "console.log(safe.get());      // 'parol'",
        "console.log(safe._secret);    // undefined — closure ichida"],
       diff="Hard", pts=4),
    ti("`debounce(funk, ms)` qanday ishlaydi va u nima uchun closure'siz yozib bo'lmaydi?",
       "debounce — funksiya tez-tez chaqirilsa, faqat oxirgi chaqiruvdan ms millisekund o'tgandan keyin "
       "ishga tushiradi. Mexanizm: ichki funksiya `timeoutId` ni closure ichida saqlaydi. Har chaqiruvda "
       "eski timeoutni clearTimeout bilan o'chiradi va yangisini setTimeout bilan boshlaydi. Closure'siz "
       "timeoutId ni global yoki obyekt maydonida saqlash kerak — bu har debounce instansiyasi alohida "
       "state'ga ega bo'lishini buzadi. Closure har debounce chaqirig'ida ALOHIDA scope yaratadi — "
       "har debounce-langan funksiya o'z timeoutId'siga ega bo'ladi. Foydalanish: search input "
       "(har klavishada API chaqirmaslik), window resize, autosave.",
       hint="timeoutId state'ni qaerda saqlash kerak?",
       diff="Hard", pts=4),
    mc("`const ko_paytiruvchi = k => x => x * k;` — bu qaysi pattern?",
       ["Currying — ko'p argumentli funksiyani bir argumentli zanjirga aylantirish",
        "Closure pattern",
        "Funksiya fabrikasi",
        "Hammasi — bu currying VA closure pattern (funksiya fabrikasi)"],
       "D",
       hint="Bir nechta nomi bor — currying / partial application / factory.",
       diff="Hard", pts=4),
]
L5_EX: list = [
    mc("`const it = { nom: 'Rex', gapir() { console.log(this.nom); } }; it.gapir();` — nima chiqadi?",
       ["undefined", "'Rex'", "TypeError", "this"],
       "B",
       hint="Metod chaqirilganda this = chaqirilgan obyekt.",
       diff="Easy", pts=2),
    mc("`call` va `apply` orasidagi farq nima?",
       ["call argumentlarni vergul bilan, apply massivda qabul qiladi",
        "call darhol, apply keyinroq ishga tushadi",
        "Hech qanday farq yo'q",
        "apply tezroq"],
       "A",
       hint="Esda saqlash: A — Array (apply), C — Comma (call).",
       diff="Medium", pts=3),
    mc("`function f() { console.log(this); }` — strict mode'da `f()` chaqirilganda nima chiqadi?",
       ["window",
        "undefined",
        "TypeError",
        "global"],
       "B",
       hint="Strict mode'da oddiy chaqiruv this'ni undefined qiladi (loose mode'da window).",
       diff="Medium", pts=3),
    mc("`bind` qachon ideal tanlov?",
       ["Event handler'ga class metodini uzatish",
        "setTimeout callback'da this'ni saqlash",
        "Partial application — argumentni oldindan biriktirish",
        "Funksiyani darhol chaqirish",
        "Array elementlarini transformatsiya"],
       "A,B,C", multi=True,
       hint="bind keyinroq chaqirish uchun. Darhol chaqirish uchun call/apply.",
       diff="Medium", pts=3),
    dd("Class metodini event handler sifatida ishlatish uchun this'ni biriktirish bosqichlari",
       ["class Form {",
        "    constructor(input) {",
        "        this.input = input;",
        "        this.qiymat = '';",
        "    }",
        "    o_zgartirish(event) {",
        "        this.qiymat = event.target.value;",
        "        console.log(this.qiymat);",
        "    }",
        "}",
        "",
        "const form = new Form(document.querySelector('#x'));",
        "// Bind bilan — this saqlanadi",
        "form.input.addEventListener('input', form.o_zgartirish.bind(form));"],
       diff="Hard", pts=4),
    ti("Arrow funksiya va oddiy `function` orasidagi `this` farqi — qachon arrow YOMON tanlov?",
       "Arrow — lexical this (yaratilgan paytdagi tashqi scope'dan). function — chaqiruvga qarab. "
       "Arrow YOMON: 1) Obyekt metodi sifatida (`obj.metod = () => this.nom` — this obyekt EMAS, "
       "tashqi scope); 2) DOM event handler'da `this` element bo'lishi kerak; 3) Constructor "
       "(`new arrow()` — TypeError); 4) Prototip metodlari; 5) `arguments` obyektidan foydalanish "
       "kerak (arrow'da yo'q). Arrow IDEAL: 1) callback ichida tashqi this kerak (map, setTimeout); "
       "2) class field — instance'ga bound; 3) sof yordamchi funksiyalar (this kerak emas). "
       "Default tavsiya: ko'pchilik holatda arrow. Obyekt metodi yoki this kerak — function.",
       hint="Lexical vs chaqiruvga qarab — tanlovning asosi.",
       diff="Hard", pts=4),
    mc("`function double(x) { return x * 2; }; const fives = double.bind(null, 5);` — `fives()` nima qaytaradi?",
       ["10",
        "5",
        "Funksiya — argumentsiz chaqirsa 5 bilan ishlatadi",
        "TypeError"],
       "A",
       hint="bind ikkinchi va undan keyingi argumentlarni oldindan biriktiradi. fives() — 5 ni argument deb oladi.",
       diff="Medium", pts=3),
]
L6_EX: list = [
    mc("`export default class User { ... }` ni qanday import qilish to'g'ri?",
       ["import User from './user.js';",
        "import { User } from './user.js';",
        "import * as User from './user.js';",
        "require('./user.js').User"],
       "A",
       hint="Default — qavssiz, istalgan nom bilan.",
       diff="Easy", pts=2),
    mc("`export const PI = 3.14` ni qanday import qilish to'g'ri?",
       ["import PI from './math.js';",
        "import { PI } from './math.js';",
        "import * as PI from './math.js';",
        "import 'PI' from './math.js';"],
       "B",
       hint="Named — { } ichida, aniq nom bilan.",
       diff="Easy", pts=2),
    mc("`import * as utils from './utils.js'` qanday foydalanish to'g'ri?",
       ["utils.formatla('...')",
        "utils.log('...')",
        "utils.default() — default eksportni shu nom bilan chaqirish",
        "Hammasini bir vaqtning o'zida"],
       "A,B,C", multi=True,
       hint="Namespace import — barchasini bitta obyekt ichiga oladi.",
       diff="Medium", pts=3),
    mc("HTML'da ESM ishlatish uchun script tegi qanday bo'lishi kerak?",
       ["<script src='app.js'></script>",
        "<script type='module' src='app.js'></script>",
        "<script type='esm' src='app.js'></script>",
        "<module src='app.js'></module>"],
       "B",
       hint="type='module' atributi — brauzerga 'bu ES modul' deydi.",
       diff="Medium", pts=3),
    dd("Barrel (index.js) orqali bir nechta modulni eksport qilish bosqichlari",
       ["// index.js — barrel fayl",
        "",
        "export { sum, mul, PI } from './math.js';",
        "export { default as User } from './user.js';",
        "export * from './utils.js';",
        "",
        "// app.js — barcha import bir joydan",
        "import { sum, User, formatla } from './index.js';"],
       diff="Medium", pts=3),
    ti("Named export va default export — qaysi biri ko'pchilik holatda yaxshiroq, nima uchun?",
       "Named export — ko'pchilik loyihalarda yaxshiroq tavsiya. Sabablar: 1) Refactoring xavfsiz — "
       "rename qilsangiz IDE har joyda topib o'zgartiradi (default'da har joyda boshqa nom bo'lishi mumkin); "
       "2) Aniqlik — `import { sum } from './math'` o'qish ravshan, `import math from './math'` keyin "
       "`math()` chaqiruvi nima qilishini bilmaslik; 3) Auto-import IDE'lar — named eksportlarni topa "
       "oladi, default uchun manual yozish kerak; 4) Bir modulda bir nechta narsa eksport bo'lishi tabiiy. "
       "Default export — qachon: kichik bitta narsali modul (bitta class yoki bitta funksiya), uning "
       "asosiy nomi modul nomi bilan to'g'ri keladi (User class — user.js). React komponentlari ham "
       "ko'pincha default — har faylga bitta komponent. Lekin katta loyihalarda named'ga o'tish odat.",
       hint="Refactoring xavfsizligi, aniqlik, IDE qo'llab-quvvatlash.",
       diff="Hard", pts=4),
    mc("ES modules va CommonJS orasidagi farq qaysilari?",
       ["ES — `import/export`, CJS — `require/module.exports`",
        "ES — statik (build-time tahlil), CJS — dinamik (runtime)",
        "ES — live bindings, CJS — snapshot",
        "ES — async, CJS — sync",
        "Hech qanday farq yo'q"],
       "A,B,C,D", multi=True,
       hint="4 ta farq bor — hammasi muhim.",
       diff="Hard", pts=4),
]
R2_EX: list = [
    mc("`createCounter()` 3 marta chaqirilsa nima bo'ladi?",
       ["3 ta alohida closure — har birining o'z value'si bor",
        "Bitta umumiy value uchovi baham ko'radi",
        "TypeError",
        "Faqat 1 ta yaratiladi, qolgan 2 ta nusxa"],
       "A",
       hint="Har funksiya chaqiruvi alohida scope.",
       diff="Easy", pts=2),
    mc("`get joriy() { return value; }` — bu nima va qanday ishlatiladi?",
       ["Getter — atribut sifatida ko'rinadi: `counter.joriy` (qavssiz)",
        "Oddiy metod — `counter.joriy()` chaqiriladi",
        "Faqat dekoratsiya",
        "Static metod"],
       "A",
       hint="Getter metod — chaqirayotganda qavs yo'q.",
       explanation="Getter — computed atribut. Pythonning @property bilan o'xshash.",
       diff="Medium", pts=3),
    mc("`registry.olish('oshxona').oshirish()` — chain'ni nima qiladi?",
       ["TypeError",
        "Counter obyektini olib, uning oshirish metodini chaqiradi",
        "Faqat oshxonani qaytaradi",
        "Yangi counter yaratadi"],
       "B",
       hint="Map'dan qiymat olinadi (counter obyekti), keyin metodi chaqiriladi.",
       diff="Medium", pts=3),
    mc("Qaysi vaziyatda CLOSURE pattern class'dan yaxshiroq?",
       ["Private state kerak (haqiqiy private — # bilan ham bo'ladi lekin)",
        "Bir nechta factory parametri bilan instance yaratish",
        "Funksional API — har metod alohida import",
        "DOM event handler — bound state bilan",
        "Inheritance va polimorfizm"],
       "A,B,C,D", multi=True,
       hint="Inheritance/polimorfizm uchun class qulayroq. Qolgani uchun closure ham yetadi.",
       diff="Hard", pts=4),
    dd("Limitli counter modul yaratish va ishlatish bosqichlari",
       ["// counter.js",
        "export function createCounter({ qadam = 1, max = Infinity } = {}) {",
        "    let value = 0;",
        "    return {",
        "        oshirish() {",
        "            if (value + qadam > max) throw new Error('Max!');",
        "            value += qadam;",
        "            return value;",
        "        },",
        "        get joriy() { return value; },",
        "    };",
        "}",
        "",
        "// app.js",
        "import { createCounter } from './counter.js';",
        "",
        "const c = createCounter({ qadam: 5, max: 20 });",
        "console.log(c.oshirish());  // 5",
        "console.log(c.oshirish());  // 10",
        "console.log(c.joriy);       // 10"],
       diff="Hard", pts=4),
    ti("`createCounter` qaytaradigan obyektga `get tarix()` qo'shish — nima uchun `[...tarix]` (spread) bilan qaytariladi?",
       "Tashqi kodga MUTABLE reference bermaslik uchun. Agar `return tarix` qilsangiz — tashqi kod "
       "`counter.tarix.push(...)` yoki `counter.tarix.length = 0` qila oladi va private state'ni "
       "buzadi. `[...tarix]` — sayoz nusxa, tashqi kod nusxani o'zgartirsa ham asl ichki tarix "
       "saqlanadi. Bu encapsulation kompleksining bir qismi: 1) `let` orqali state private; "
       "2) o'zgartiruvchi metodlar faqat ichkarida; 3) o'qiluvchi getter'lar nusxa qaytaradi. "
       "Diqqat: ichkarida obyektlar bo'lsa, sayoz nusxa yetmaydi — chuqurroq nusxa kerak "
       "(structuredClone yoki manual). Bu pattern Pythonda ham qo'llaniladi (list ni return qilishda).",
       hint="Tashqi kod private state'ni MUTATE qilmasin.",
       diff="Hard", pts=4),
]
L7_EX: list = [
    mc("Promise'ning 3 ta holatini tanlang",
       ["pending, fulfilled, rejected",
        "loading, success, error",
        "wait, ok, fail",
        "start, done, broken"],
       "A",
       hint="Promise spec'idagi rasmiy nomlar.",
       diff="Easy", pts=2),
    mc("`Promise.resolve(5).then(x => x * 2).then(x => x + 1).then(console.log)` nima chiqaradi?",
       ["5", "10", "11", "Promise"],
       "C",
       hint="Chain: 5 -> 10 -> 11 -> log.",
       diff="Medium", pts=3),
    mc("`Promise.all([p1, p2, p3])` qachon reject bo'ladi?",
       ["Hammasi reject bo'lganda",
        "Hech bo'lmasa bittasi reject bo'lganda (eng birinchisi)",
        "Hech qachon",
        "Foydalanuvchi tomonidan to'xtatilganda"],
       "B",
       hint="Promise.all — `all or nothing`.",
       explanation="Hammasi haqida ma'lumot kerak bo'lsa — Promise.allSettled.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysilari TO'G'RI Promise pattern?",
       ["fetch(url).then(r => r.json()).catch(e => console.log(e))",
        "new Promise((resolve) => setTimeout(resolve, 100))",
        "Promise.all([p1, p2]).then(([a, b]) => ...)",
        "promise.then().catch().finally()",
        "promise.then(success).then().catch(error)"],
       "A,B,C,D,E", multi=True,
       hint="Hammasi to'g'ri Promise pattern.",
       diff="Medium", pts=3),
    dd("Promise.all bilan parallel API so'rovlari va xato boshqaruvi bosqichlari",
       ["const urls = [",
        "    'https://api.example.com/users',",
        "    'https://api.example.com/posts',",
        "    'https://api.example.com/comments',",
        "];",
        "",
        "Promise.all(urls.map(u => fetch(u).then(r => r.json())))",
        "    .then(([users, posts, comments]) => {",
        "        console.log('Users:', users.length);",
        "        console.log('Posts:', posts.length);",
        "    })",
        "    .catch((e) => console.error('Bittasi yiqildi:', e));"],
       diff="Hard", pts=4),
    ti("`Promise.all` va `Promise.allSettled` orasidagi farq va qaysi qachon foydali?",
       "Promise.all — barcha Promiselarni parallel kutadi. Bittasi reject bo'lsa — butun array darhol "
       "reject bo'ladi va boshqa Promiselar natijalari yo'qoladi. Foydali: barcha so'rovlar muvaffaqiyatli "
       "bo'lishi shart (transaction-like — bittasi yiqilsa, hammasi yiqilishi kerak). "
       "Promise.allSettled — hammasini kutadi va har birining holatini ({status, value/reason}) qaytaradi. "
       "Foydali: bittasi yiqilsa ham qolganlari ishlatilishi mumkin (rasm yuklash — 1 ta rasm yiqilsa "
       "boshqalari ko'rsatilsin), reporting (qaysi muvaffaqiyatli/qaysi yiqildi), batch operatsiyalar "
       "(har birining holatini alohida ko'rib chiqish). Default tavsiya: agar bittasi yiqilsa qolganini "
       "ham ishlatishingiz mumkin bo'lsa — allSettled. Aks holda all.",
       hint="all - 'all or nothing'; allSettled - 'har biri haqida ma'lumot'.",
       diff="Hard", pts=4),
    mc("`fetch(url).then(...).catch(...)` da `.catch` nimani ushlaydi?",
       ["Faqat fetch xatolarini",
        "Faqat .then ichidagi xatolarni",
        "Chain'dagi har qanday xatoni — fetch yoki har qaysi .then dan",
        "Hech narsa — silent fail"],
       "C",
       hint="Promise chain'da .catch — global ushlovchi, hamma xatolar shu yerga keladi.",
       diff="Medium", pts=3),
]
L8_EX: list = [
    mc("`async function f() { return 5; }` — `f()` nima qaytaradi?",
       ["5", "Promise { 5 }", "undefined", "Funksiya"],
       "B",
       hint="async funksiya DOIM Promise qaytaradi — `return 5` Promise.resolve(5) ga ekvivalent.",
       diff="Easy", pts=2),
    mc("`await` ni qaerda ishlatish mumkin?",
       ["Har qanday joyda",
        "Faqat async funksiya ichida yoki ESM modulda top-level",
        "Faqat .then ichida",
        "Hech qachon — eski sintaksis"],
       "B",
       hint="async function ichida — yoki ESM top-level (yangi versiya).",
       diff="Easy", pts=2),
    mc("Quyidagi kod nimaga olib keladi?\n```\n[1,2,3].forEach(async (id) => {\n  await fetch(url);\n});\nconsole.log('Tugadi');\n```",
       ["'Tugadi' eng oxirgida chiqadi",
        "'Tugadi' fetch'lar tugashidan oldin chiqadi (forEach kutmaydi)",
        "TypeError",
        "Hech narsa — forEach to'g'ri kutadi"],
       "B",
       hint="forEach async callback'larni kutmaydi — kutish kerak bo'lsa for-of yoki Promise.all.",
       explanation="Bu eng ko'p uchraydigan async xato. To'g'risi — `for (const id of arr) { await ... }` yoki `await Promise.all(arr.map(...))`.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi qator PARALLEL bajarish uchun to'g'ri?",
       ["await fetch(a); await fetch(b); await fetch(c);",
        "await Promise.all([fetch(a), fetch(b), fetch(c)])",
        "const aP = fetch(a); const bP = fetch(b); await aP; await bP;",
        "[a, b, c].forEach(async (u) => await fetch(u))"],
       "B,C", multi=True,
       hint="A sekvensial — ketma-ket. B va C parallel. D kutmaydi.",
       diff="Medium", pts=3),
    dd("GitHub'dan bir nechta repo ma'lumotlarini parallel olish va xato boshqarish bosqichlari",
       ["async function repoOlish(nomi) {",
        "    try {",
        "        const r = await fetch(`https://api.github.com/repos/${nomi}`);",
        "        if (!r.ok) throw new Error(`HTTP ${r.status}`);",
        "        return await r.json();",
        "    } catch (e) {",
        "        console.error(`${nomi}: ${e.message}`);",
        "        return null;",
        "    }",
        "}",
        "",
        "const repos = ['python/cpython', 'facebook/react', 'vuejs/vue'];",
        "const natijalar = await Promise.all(repos.map(repoOlish));",
        "console.log(natijalar.filter(Boolean));"],
       diff="Hard", pts=4),
    ti("Sekvensial `await` va `Promise.all` qachon qaysi biri to'g'ri tanlov?",
       "Sekvensial (await ketma-ket) — keyingisi avvalgisining natijasiga bog'liq bo'lganda. Masalan: "
       "user'ni olish, keyin user.id orqali postlarni olish — postlarni boshlashdan oldin user kerak. "
       "Yana: rate-limited API — har so'rov orasida pauza kerak; tartib muhim operatsiyalar "
       "(buyurtmalarni ketma-ket qayta ishlash). Promise.all — barchasi mustaqil va birga boshlash "
       "mumkin. Masalan: 5 ta foydalanuvchi profilini olish, parallel rasm yuklash, dashboard uchun "
       "har xil API'lardan ma'lumot. Tezlik farqi katta: 5 ta 200ms so'rov sekvensial = 1s, parallel "
       "= 200ms. Default tavsiya: agar bog'liqlik yo'q bo'lsa — Promise.all. Bog'liqlik bor — sekvensial.",
       hint="Bog'liqlik bormi? Rate limit? Tartib?",
       diff="Hard", pts=4),
    mc("`async function f() { throw new Error('x'); }` — `f()` chaqirilganda nima bo'ladi?",
       ["Darhol exception otadi",
        "Rejected Promise qaytaradi — `.catch` yoki try/catch bilan ushlash kerak",
        "Hech narsa",
        "Konsolda print qiladi"],
       "B",
       hint="async funksiya ichidagi throw — Promise.reject ga aylanadi.",
       diff="Medium", pts=3),
]
L9_EX: list = [
    mc("`fetch` HTTP 404 status'da nima qiladi?",
       ["Promise reject bo'ladi (.catch ushlaydi)",
        "Promise resolve bo'ladi — r.ok false bo'ladi, qo'lda tekshirish kerak",
        "Avtomatik retry qiladi",
        "Hech narsa qaytarmaydi"],
       "B",
       hint="fetch faqat tarmoq xatosi'da (DNS, offline) reject qiladi. 4xx/5xx — resolved.",
       explanation="Bu fetch'ning klassik tuyog'i. Productionda har fetch dan keyin `if (!r.ok) throw ...` zarur.",
       diff="Medium", pts=3),
    mc("`r.json()` chaqirish uchun nima qilish kerak?",
       ["await qo'shish — `await r.json()`",
        "Hech narsa — qaytaradi to'g'ridan-to'g'ri",
        ".then() bilan chain qilish",
        "JSON.parse qilish"],
       "A,C", multi=True,
       hint="r.json() Promise qaytaradi — await yoki .then.",
       diff="Easy", pts=2),
    mc("POST so'rovi uchun body qanday formatlanishi kerak?",
       ["JSON.stringify(obyekt) + Content-Type header",
        "Faqat obyekt — fetch o'zi konvertatsiya qiladi",
        "URL ga query params sifatida",
        "FormData ichida"],
       "A,D", multi=True,
       hint="JSON uchun stringify + header. Form-encoded uchun FormData yoki URLSearchParams.",
       diff="Medium", pts=3),
    mc("AbortController qanday ishlaydi?",
       ["Promise'ni darhol to'xtatadi",
        "fetch ga signal beradi — controller.abort() chaqirilsa fetch reject bo'ladi (AbortError)",
        "fetch'ni qayta urinadi",
        "Cache'ni tozalaydi"],
       "B",
       hint="signal: controller.signal — option sifatida fetch'ga beriladi.",
       explanation="Timeout va manual bekor qilish uchun ideal pattern.",
       diff="Medium", pts=3),
    dd("Timeout bilan xavfsiz GET so'rovi yozish bosqichlari",
       ["async function safeFetch(url, ms = 5000) {",
        "    const controller = new AbortController();",
        "    const tid = setTimeout(() => controller.abort(), ms);",
        "    try {",
        "        const r = await fetch(url, { signal: controller.signal });",
        "        if (!r.ok) throw new Error(`HTTP ${r.status}`);",
        "        return await r.json();",
        "    } finally {",
        "        clearTimeout(tid);",
        "    }",
        "}"],
       diff="Hard", pts=4),
    ti("Productionda har fetch'ga wrapper yozish nima foyda beradi?",
       "Wrapper sizga: 1) Markazlashgan xato boshqaruvi — har joyda try/catch yozmasdan, wrapper "
       "ichida bir marta; 2) Timeout — har so'rov uchun bir xil chegaralar (Productionda hech qachon "
       "timeout'siz fetch qilmang); 3) Auth header avtomatik — interceptor pattern; 4) Loglashtirish "
       "va telemetry — har so'rovning vaqti, statusi log'ga; 5) Retry mantig'i — server xatolarida "
       "qayta urinish; 6) Base URL — `/api/users` deb yozish (https://... har joyda emas); 7) Content-Type "
       "default'i va body auto-stringify; 8) JSON parsing avtomatik. Bularning hammasini har joyda "
       "qo'lda yozish — bug manbai. Wrapper — bir marta yozasiz, hammasi qutqarish. Axios library'lari "
       "shu tartibni tayyor beradi, lekin kichik wrapper ham yetadi.",
       hint="Markazlashgan xato, timeout, auth, log, retry.",
       diff="Hard", pts=4),
    mc("`Promise.allSettled` va `Promise.all` — qachon qaysi?",
       ["allSettled: hammasi muvaffaqiyatli bo'lishi shart bo'lganda",
        "all: hammasi muvaffaqiyatli bo'lishi shart bo'lganda",
        "allSettled: bittasi yiqilsa qolganlari ham kerak bo'lganda",
        "all: bittasi yiqilsa hech narsa qilmaslik kerak bo'lganda"],
       "B,C,D", multi=True,
       hint="all — strict, biri yiqilsa hammasi. allSettled — har biri haqida natija.",
       diff="Medium", pts=3),
]
R3_EX: list = [
    mc("R3 pipeline'da 3 ta qatlam qaysi tartibda ishlaydi?",
       ["Render -> Fetch -> Transform",
        "Fetch (API) -> Transform (tozalash) -> Save/Render",
        "Transform -> Save -> Fetch",
        "Tartib muhim emas"],
       "B",
       hint="Input -> Transform -> Output.",
       diff="Easy", pts=2),
    mc("`String(matn || '').replace(/<[^>]+>/g, '')` — bu nima qiladi?",
       ["Hech narsa",
        "matn'ni stringga aylantiradi va HTML teglarni o'chiradi (global flag /g bilan barchasi)",
        "Faqat birinchi tegni o'chiradi",
        "TypeError"],
       "B",
       hint="`/g` flag — global, barcha mos kelishlar. `String()` — null/undefined uchun xavfsizlik.",
       diff="Medium", pts=3),
    mc("Pipeline'da `try/catch` qaerda joylashishi kerak?",
       ["Har ichki funksiyada — yashirin xato bo'lmasin",
        "Faqat tashqi orkestratorda — har bosqichdagi xato bir joyga",
        "Har ikkalasi ham — ichki specific, tashqi global",
        "Hech qaerda — fetch o'zi boshqaradi"],
       "C",
       hint="Specific xatolar past darajada, umumiy boshqaruv yuqori darajada.",
       explanation="Ichki funksiyalar — domain'ga oid xatolarni ushlaydi. Tashqi — barchasini log va foydalanuvchiga ko'rsatadi.",
       diff="Hard", pts=4),
    mc("Pipeline'da qaysi qo'shimchalar foydali bo'ladi?",
       ["AbortController bilan timeout",
        "raise_for_status bilan xato boshqaruvi",
        "@timed dekorator har qatlam vaqtini o'lchash",
        "Yangiliklarni xotirada cheksiz to'plash"],
       "A,C", multi=True,
       hint="Production'da timeout va vaqt monitoringi — har doim foydali. Cheksiz xotira yo'q.",
       diff="Medium", pts=3),
    dd("Pipeline'ni API -> tozalash -> saqlash ko'rinishida yozish bosqichlari",
       ["async function pipeline(limit = 10) {",
        "    const raw = await api(`${API}/posts?_limit=${limit}`);",
        "",
        "    const yangiliklar = raw.map(r => ({",
        "        id: r.id,",
        "        sarlavha: tozalash(r.title),",
        "        matn: tozalash(r.body),",
        "    }));",
        "",
        "    localStorage.setItem('yangiliklar', JSON.stringify(yangiliklar));",
        "    return yangiliklar;",
        "}"],
       diff="Hard", pts=4),
    ti("`Promise.allSettled` qachon `Promise.all` dan yaxshiroq?",
       "Promise.all — barcha so'rovlar muvaffaqiyatli bo'lishi shart. Bittasi yiqilsa — darhol reject "
       "va boshqalar natijalari yo'qoladi (chunki butun chain reject bo'ladi). allSettled — har birining "
       "holatini ({status, value/reason}) qaytaradi. Yaxshiroq holatlar: 1) Dashboard - 5 ta API'dan "
       "ma'lumot, bittasi yiqilsa qolganlari ko'rsatilsin; 2) Reports — qaysi muvaffaqiyatli/qaysi yiqildi "
       "ko'rsatish; 3) Batch operations — bir necha foydalanuvchini yangilash, ba'zilari yiqilsa ham; "
       "4) Multiple data sources — primary va backup; 5) Independent data — yangiliklar va rasm yuklash. "
       "Default tavsiya: agar bittasi yiqilsa qolgani ham kerak bo'lsa — allSettled. Transaction-like "
       "barchasi yoki hech narsa — all.",
       hint="all - atomic, allSettled - per-item natijalar.",
       diff="Hard", pts=4),
]
L10_EX: list = [
    mc("`#balans` private maydonni tashqaridan qanday o'qish mumkin?",
       ["obj.#balans",
        "obj['#balans']",
        "Hech qanday yo'l — # haqiqiy private (syntax-level)",
        "Faqat console.log bilan"],
       "C",
       hint="# bilan boshlangan maydonlar — class tashqarisida murojaat SyntaxError beradi.",
       explanation="Conventional `_field` o'zgartirib bo'ladi, lekin `#field` umuman ko'rinmaydi.",
       diff="Medium", pts=3),
    mc("`static MAX = 1000` qanday chaqiriladi?",
       ["obj.MAX",
        "ClassName.MAX",
        "this.MAX",
        "Constructor ichidan"],
       "B",
       hint="static — class'ning maydoni, instance'ning emas.",
       diff="Easy", pts=2),
    mc("`super()` ni sub-class constructor'ida qaerda chaqirish kerak?",
       ["Hech qaerda — Python avtomatik chaqiradi",
        "Constructor'ning BIRINCHI qatorida (this ishlatishdan oldin)",
        "Constructor'ning oxirida",
        "Bittagina marta — istalgan joyda"],
       "B",
       hint="`this` ga murojaat qilishdan oldin super() bo'lishi shart.",
       explanation="super() chaqirilmaguncha `this` mavjud emas. ReferenceError.",
       diff="Medium", pts=3),
    mc("`get balans() { return this.#balans; }` — bu nima?",
       ["Oddiy metod — `obj.balans()` chaqiriladi",
        "Getter — `obj.balans` (qavssiz) bilan ishlatiladi",
        "Static metod",
        "Private metod"],
       "B",
       hint="Getter — atribut sifatida ko'rinadigan metod.",
       diff="Easy", pts=2),
    dd("Doira class'ini private radius, validatsiya va computed maydon bilan yozish bosqichlari",
       ["class Doira {",
        "    #radius;",
        "",
        "    constructor(radius) {",
        "        this.radius = radius;   // setter chaqiriladi",
        "    }",
        "",
        "    get radius() { return this.#radius; }",
        "",
        "    set radius(val) {",
        "        if (val < 0) throw new Error('Manfiy radius');",
        "        this.#radius = val;",
        "    }",
        "",
        "    get maydon() {",
        "        return Math.PI * this.#radius ** 2;",
        "    }",
        "}"],
       diff="Medium", pts=3),
    ti("Sub-class metodida `super.method()` chaqirish nima foyda beradi?",
       "Ota klass behavior'ini KENGAYTIRISH (override emas, qo'shimcha qilish). Sub-class metodi "
       "ko'pincha 'avval ota qiladigan ishni qil, keyin men o'zimning logikamni qo'shaman' pattern'ini "
       "talab qiladi. Misol: A_lochiIt.gapirVaYugur() — super.gapir() bilan oddiy gapirish, keyin "
       "'yugurmoqda' qo'shadi. Boshqa holatlar: 1) Constructor'da super(args) — ota maydonlarini ham "
       "yaratish; 2) toString() ichida — ota class nomini olish; 3) Hook metodlari (lifecycle) — render() "
       "metodida avval super.render() ni chaqirish keyin o'z DOM o'zgarishi. super'siz override qilsangiz "
       "— ota behavior'i butunlay yo'qoladi. super bilan — to'ldirib boyitasiz. Python'da ham xuddi shu pattern.",
       hint="Override va kengaytirish farqi.",
       diff="Hard", pts=4),
    mc("Quyidagi qaysi pattern'lar JS class'larida YAXSHI?",
       ["Private maydonlar uchun #",
        "Validatsiya uchun getter/setter",
        "Factory uchun static metod",
        "Static config (MAX, DEFAULT_*)",
        "Inheritance — Mashina extends Yo'l (mashina yo'l emas)"],
       "A,B,C,D", multi=True,
       hint="A,B,C,D — yaxshi pattern'lar. E — yomon (IS-A munosabati noto'g'ri).",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("CAPSTONE TodoStore'da `#todos` qaerda saqlanadi?",
       ["Global scope'da",
        "TodoStore class instansiyasining private maydonida (# bilan)",
        "localStorage'da to'g'ridan-to'g'ri",
        "Constructor parametrida"],
       "B",
       hint="# bilan boshlangan maydon — haqiqiy private instance maydoni.",
       diff="Easy", pts=2),
    mc("`get statistika()` — qanday ishlatiladi?",
       ["store.statistika()",
        "store.statistika — qavssiz, computed atribut sifatida",
        "TodoStore.statistika()",
        "Faqat class ichidan"],
       "B",
       hint="Getter — atribut sifatida ko'rinadi.",
       diff="Easy", pts=2),
    mc("`on_change` metodi nima qiladi?",
       ["DOM event handler",
        "Observer pattern — store o'zgarganda listener funksiyalarni chaqiradi",
        "Async sync",
        "Validatsiya"],
       "B",
       hint="Subscribe/publish pattern — store o'zgarsa UI avtomatik yangilanadi.",
       explanation="React'ning useEffect bilan ham o'xshash idea — state o'zgarsa render.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi texnikalar CAPSTONE'da ishlatilgan?",
       ["#private maydonlar va metodlar",
        "@dataclass (Python)",
        "get/set computed atributlar",
        "async/await + fetch",
        "localStorage persistensiyasi",
        "array map/filter/reduce",
        "template literallar"],
       "A,C,D,E,F,G", multi=True,
       hint="@dataclass — Python; qolgani — JavaScript.",
       diff="Medium", pts=3),
    dd("Subscribe pattern bilan TodoStore yaratish bosqichlari",
       ["class TodoStore {",
        "    #todos = [];",
        "    #listeners = [];",
        "",
        "    on_change(fn) {",
        "        this.#listeners.push(fn);",
        "        return () => {",
        "            this.#listeners = this.#listeners.filter(f => f !== fn);",
        "        };",
        "    }",
        "",
        "    #notify() {",
        "        this.#listeners.forEach(fn => fn(this));",
        "    }",
        "",
        "    qosh(matn) {",
        "        this.#todos.push({ matn });",
        "        this.#notify();   // har o'zgarishdan keyin",
        "    }",
        "}"],
       diff="Hard", pts=4),
    ti("`store.on_change(render)` qaytaradigan funksiya nima va qachon ishlatiladi?",
       "Unsubscribe funksiyasini qaytaradi — chaqirilganda render funksiyasini listeners ro'yxatidan "
       "o'chiradi. Foydali holatlar: 1) React komponenti unmount bo'lganda (useEffect cleanup) — "
       "memory leak'ni oldini olish; 2) Komponent qayta chaqirilganda eski listener'ni o'chirish; "
       "3) Test'lar oxirida tozalash. Bu pattern — observer/pub-sub'da klassik: subscribe doim "
       "unsubscribe ni qaytaradi. Aks holda — listener'lar to'planib boradi va store har xabarni "
       "minglarcha marta yuborib turadi. EventEmitter, RxJS, React'ning useEffect — hammasi shu "
       "pattern bilan ishlaydi: subscribe paytida cleanup tayyorlab qo'yish.",
       hint="Unsubscribe — cleanup mexanizmi. Memory leak oldini olish.",
       diff="Hard", pts=4),
    mc("Loyihani productionga olib chiqish uchun keyingi qadam qaysi?",
       ["Jest yoki Vitest bilan testlar yozish",
        "Server backend qo'shish (Express/FastAPI)",
        "React/Vue ga ko'chirish",
        "TypeScript ga migration",
        "Hammasi — ehtiyojga qarab"],
       "E",
       hint="Loyiha tayyor — keyingi qadam ehtiyojga qarab.",
       diff="Medium", pts=3),
]


# ─────────────────────────────────────────────────────────────────────────────
# Per-lesson assignments
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {  # L1
        "title": "Profile transformer (destructuring + spread bilan)",
        "description": (
            "Foydalanuvchi profil obyektlarini bir formatdan boshqasiga "
            "o'tkazuvchi modul. Hech qaysi joyda old uslubdagi string konkatenatsiya "
            "yoki function keyword ishlatilmasin (constructor'lardan tashqari)."
        ),
        "requirements": (
            "• 10+ foydalanuvchi obyekt (ism, yosh, email, manzil...)\n"
            "• Destructuring funksiya parametrida (`({ ism, yosh })`)\n"
            "• Spread bilan immutable update — kamida 3 ta misol\n"
            "• Default qiymat destructuring'da (`{ rol = 'user' }`)\n"
            "• Nested destructuring (manzil.shahar)\n"
            "• Rest parameter funksiyada (`(...args)`)\n"
            "• Hech qaysi joyda `function` keyword — faqat arrow"
        ),
        "technologies": "JavaScript, arrow, destructuring, spread/rest",
        "deadline_days": 3,
    },
    1: {  # L2
        "title": "Talabalar dashboard (map/filter/reduce zanjiri)",
        "description": (
            "Talabalar ro'yxatidan statistika va saralash chiqaruvchi modul. "
            "Hech qaysi joyda for sikli ishlatilmasin (forEach faqat yon ta'sir uchun)."
        ),
        "requirements": (
            "• 15+ talaba (ism, yosh, kasb, ball, teglar massivi)\n"
            "• Kamida 3 ta map+filter zanjiri\n"
            "• Kamida 2 ta reduce — group by, jami, count\n"
            "• find/some/every — har biri ishlatilgan\n"
            "• Bir nechta mezon bilan sort (key tuple-pattern)\n"
            "• Hech qaysi joyda oddiy `for` yoki `forEach`+push\n"
            "• Bo'sh massiv uchun xavfsiz default qiymatlar"
        ),
        "technologies": "JavaScript, array methods, chain, arrow",
        "deadline_days": 4,
    },
    2: {  # L3
        "title": "Hisobot generatori (template literallar bilan)",
        "description": (
            "Ma'lumotlar massividan chiroyli formatlangan matnli hisobot "
            "yaratuvchi modul. Bir nechta turli hisobot shaklini qo'llab-quvvatlaydi."
        ),
        "requirements": (
            "• Kamida 3 turdagi hisobot (jadval, summary, detailed)\n"
            "• Template literallar bilan har bir hisobot\n"
            "• padStart/padEnd bilan jadval shakli\n"
            "• toLocaleString bilan summalarni formatlash\n"
            "• Ko'p qatorli matn (xat shakli)\n"
            "• String metodlari (trim, includes, replaceAll, split, join)\n"
            "• Tagged template bilan kichik HTML escaping helper"
        ),
        "technologies": "JavaScript, template literals, string methods, toLocaleString",
        "deadline_days": 4,
    },
    3: {  # R1
        "title": "🔁 R1: Restoran buyurtmalar statistikasi",
        "description": (
            "Restoran buyurtmalari ro'yxati asosida 3 ta texnikani birlashtirgan "
            "tahlil moduli. TOP 3 ofitsiant, kunlik daromad, taom kategoriyasi."
        ),
        "requirements": (
            "• 15+ buyurtma (ofitsiant, taom, narx, sana, kategoriya)\n"
            "• Destructuring funksiya parametrida\n"
            "• reduce bilan group by (ofitsiant, kategoriya, sana)\n"
            "• sorted + lambda — TOP 3 ofitsiant\n"
            "• Set bilan unique kategoriyalar\n"
            "• Template literal bilan jadval hisobot\n"
            "• toLocaleString bilan summalar\n"
            "• Hech qaysi joyda for sikli"
        ),
        "technologies": "JavaScript, modern syntax, array methods, template literals",
        "deadline_days": 5,
    },
    4: {  # L4
        "title": "Counter va Memo factory'lar (closure bilan)",
        "description": (
            "Closure'lar bilan funksional pattern'lar yaratuvchi modul. "
            "Hech qaysi closure'ni class bilan almashtirilmasin (closure pattern'ini ishlatib)."
        ),
        "requirements": (
            "• `createCounter` factory — qadam, max, min sozlamalari\n"
            "• `memoize(funk)` — natija cache'lash\n"
            "• `once(funk)` — faqat bir marta chaqirish\n"
            "• `debounce(funk, ms)` — kechiktirilgan chaqiruv\n"
            "• Har biri o'z private state'i bilan\n"
            "• Demo: Fibonacci memoize bilan tezligini taqqoslash\n"
            "• Hech qaysi joyda `class` — faqat factory functions"
        ),
        "technologies": "JavaScript, closures, factory pattern, IIFE",
        "deadline_days": 5,
    },
    5: {  # L5
        "title": "Event handler manager (this + bind)",
        "description": (
            "DOM event handler'larni boshqaruvchi class. this/bind/arrow farqlari "
            "amaliyotda ko'rsatilsin va xato pattern'lardan saqlanish o'rgatilsin."
        ),
        "requirements": (
            "• `class EventManager` — bir necha element uchun bog'liqlik\n"
            "• Class metodlari handler sifatida — bind bilan to'g'ri ishlatilgan\n"
            "• Arrow class field bilan ham misol\n"
            "• `call`/`apply` bilan funksiyani boshqa kontekstda chaqirish misoli\n"
            "• Partial application — bind bilan argumentni biriktirish\n"
            "• Setinterval/setTimeout ichida this — arrow yoki bind bilan to'g'ri\n"
            "• Manual handler removeEventListener bilan xavfsiz olib tashlash"
        ),
        "technologies": "JavaScript, this, call/apply/bind, arrow class fields",
        "deadline_days": 4,
    },
    6: {  # L6
        "title": "Multi-module loyiha (ES6 modullar bilan)",
        "description": (
            "Kichik kalkulyator ilovasini bir necha modul bo'lib yozish. "
            "Har modulning aniq roli bo'lsin, named/default eksport to'g'ri tanlangan."
        ),
        "requirements": (
            "• 4-5 ta modul: math.js, format.js, history.js, ui.js, app.js\n"
            "• math.js — sof funksiyalar, named exports\n"
            "• history.js — class, default export\n"
            "• format.js — yordamchi funksiyalar (toLocaleString wrapper)\n"
            "• Bir nechta named, bittagina default eksport\n"
            "• Barrel file (index.js) bilan jamlangan eksport\n"
            "• HTML'da `<script type=\"module\">` bilan ishlatilgan\n"
            "• Dynamic import bilan og'ir kutubxonani lazy load qilish"
        ),
        "technologies": "JavaScript, ES6 modules, named/default exports, barrel",
        "deadline_days": 6,
    },
    7: {  # R2
        "title": "🔁 R2: Reactive counter system",
        "description": (
            "Modul 2 ning 3 ta texnikasi birga: closure factory bilan counter, "
            "subscribe/unsubscribe pattern, va modullarga ajratish."
        ),
        "requirements": (
            "• `createCounter` factory closure pattern bilan\n"
            "• `subscribe(fn)` — listener qo'shish, unsubscribe qaytarish\n"
            "• Counter o'zgarsa — barcha listener chaqiriladi\n"
            "• `this` bog'lash misoli (DOM event handler)\n"
            "• Bir necha counter — alohida state\n"
            "• Counter Registry — counter'larni nom bo'yicha boshqarish\n"
            "• ES6 modul shaklida tashkil qilingan\n"
            "• Demo: 2 ta counter + 1 ta jami"
        ),
        "technologies": "JavaScript, closures, observer pattern, ES6 modules",
        "deadline_days": 6,
    },
    8: {  # L7
        "title": "Promiseli yordamchi'lar to'plami",
        "description": (
            "Promise'lar bilan ishlovchi yordamchi funksiyalar to'plami. "
            "Real loyihada qayta-qayta ishlatiladigan utility'lar."
        ),
        "requirements": (
            "• `kutish(ms)` — Promise bilan kutish\n"
            "• `retry(fn, marotaba, kutish)` — qayta urinish\n"
            "• `withTimeout(promise, ms)` — timeout qo'shish\n"
            "• `promisify(callback_fn)` — eski API ni Promise'ga aylantirish\n"
            "• `parallelLimit(tasks, limit)` — N ta parallel chaqirish\n"
            "• Har biri uchun test demo va xato boshqaruvi\n"
            "• Promise.all/allSettled/race kamida bittasi ishlatilgan"
        ),
        "technologies": "JavaScript, Promise, async control flow",
        "deadline_days": 6,
    },
    9: {  # L8
        "title": "Async data loader (async/await bilan)",
        "description": (
            "Bir necha source dan ma'lumot yig'uvchi async modul. "
            "Sekvensial vs parallel rejimlarni qo'llab-quvvatlaydi va statistika beradi."
        ),
        "requirements": (
            "• Kamida 3 ta source (JSON URL yoki simulyatsiya)\n"
            "• `parallel()` rejim — Promise.all bilan\n"
            "• `sequential()` rejim — for...of + await bilan\n"
            "• `withRetry` opsiyasi — har source uchun\n"
            "• try/catch bilan xato boshqaruvi\n"
            "• Performance taqqoslash — har rejim qancha vaqt oldi\n"
            "• AbortController bilan bekor qilish funksiyasi"
        ),
        "technologies": "JavaScript, async/await, Promise.all, AbortController",
        "deadline_days": 5,
    },
    10: {  # L9
        "title": "GitHub API explorer (fetch wrapper bilan)",
        "description": (
            "GitHub REST API'dan ma'lumot oluvchi mini-CLI. Productionga "
            "tayyor xato boshqaruvi, timeout, retry, pagination bilan."
        ),
        "requirements": (
            "• Universal `api(url, options)` wrapper — timeout, retry, headers\n"
            "• User profile olish\n"
            "• Repo statistika (stars, forks, language)\n"
            "• Pagination bilan barcha repolari (async generator)\n"
            "• Rate limit headerlari tahlili\n"
            "• AbortController bilan timeout\n"
            "• Chiroyli jadval ko'rinishidagi natija\n"
            "• .env yoki const bilan token (agar private API)"
        ),
        "technologies": "JavaScript, fetch, REST API, async/await, async generators",
        "deadline_days": 7,
    },
    11: {  # R3
        "title": "🔁 R3: News feed (Pipeline + persistence)",
        "description": (
            "Modul 3 ning 3 ta texnikasi: async fetch, regex bilan tozalash, "
            "localStorage'ga saqlash + brauzer'da render."
        ),
        "requirements": (
            "• Async pipeline: fetch -> transform -> save -> render\n"
            "• `class Yangilik` shakl ma'lumot uchun\n"
            "• Regex bilan HTML tegslar va keraksiz bo'shliqlarni tozalash\n"
            "• localStorage'ga saqlash (key: 'news-v1')\n"
            "• Bir necha source — Promise.allSettled\n"
            "• Brauzer'da DOM render (article'lar)\n"
            "• Yuklash holati (loading state) ko'rsatish\n"
            "• Xato bo'lsa — cache'dan ko'rsatish"
        ),
        "technologies": "JavaScript, async/await, fetch, regex, localStorage, DOM",
        "deadline_days": 7,
    },
    12: {  # L10
        "title": "Bank tizimi simulyatsiyasi (chuqur OOP bilan)",
        "description": (
            "Bank hisoblarini, foydalanuvchilarni va tranzaksiyalarni modellashtiruvchi "
            "modul. Inheritance, private maydonlar, static factory'lar bilan."
        ),
        "requirements": (
            "• `class Hisob` — #balans, #tarix private\n"
            "• `class SaqlovchiHisob extends Hisob` — foiz bilan\n"
            "• `class KartaHisob extends Hisob` — kunlik limit bilan\n"
            "• Validatsiya getter/setter bilan\n"
            "• `static yangiHisob(turi, opts)` factory metod\n"
            "• `static instanceSoni` — ochilgan hisoblar\n"
            "• Polimorfizm — barcha hisoblar uchun `.qoshish/.ayirish`\n"
            "• Custom error class'lari (`HisobLimitError`)\n"
            "• `[Symbol.iterator]` — tranzaksiya tarixi iteratsiya"
        ),
        "technologies": "JavaScript, classes, private, static, inheritance, super",
        "deadline_days": 7,
    },
    13: {  # L11
        "title": "🚀 CAPSTONE: TODO ilova (full-stack ready)",
        "description": (
            "Kursning yakuniy loyihasi: brauzerda ishlovchi TODO ilova kursning "
            "barcha texnikalarini birga ishlatadi. Real foydalanish uchun mos."
        ),
        "requirements": (
            "• `class Todo` — domain model, get tasvir() bilan\n"
            "• `class TodoStore` — #todos, #counter, #saqlash, #yuklash private\n"
            "• get computed: hammasi, bajarilmagan, statistika\n"
            "• localStorage bilan persistensiya\n"
            "• Subscribe/unsubscribe pattern (on_change)\n"
            "• DOM render — template literallar bilan\n"
            "• Event delegation — bitta listener barcha LI uchun\n"
            "• Enter tugmasi bilan qo'shish\n"
            "• Filter UI — barchasi/bajarilmagan/muhim\n"
            "• Qidirish — debounce bilan (5-darsdan)\n"
            "• Server sync — async fetch bilan (mock OK)\n"
            "• Bonus: dark mode, drag-and-drop, eksport JSON"
        ),
        "technologies": (
            "JavaScript, ES6+ classes, private, async/await, fetch, "
            "localStorage, DOM, event delegation, all modern syntax"
        ),
        "deadline_days": 14,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {"order": 0,  "title": "1-Arrow funksiyalar, destructuring, spread/rest",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/h33Srr5J9nY", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-Massiv iteratorlari (map, filter, reduce, find)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/Y-fovP3VLkY", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-Template literallar va string metodlari",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/NgF9-pdTDGs", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Sotuvchi statistikasi (takrorlash)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/HGOBQPFzWKo", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-Closures (yopilmalar)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/3a0I8ICR1Vg", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-this, call, apply, bind",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/zE9iro4r918", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-ES6 modullar (import/export)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/cRHQNNcYf6s", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-State'li hisoblovchi (closure + this)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/vmEHCJofslg", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-Promiselar (.then, .catch, Promise.all)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/DHvZLI7Db8E", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-async/await",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/V_Kr9OSfDeU", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-fetch va REST API",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/cuEtnrL9-H0", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Yangiliklar yig'uvchi (takrorlash)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/7sCV4qbm38c", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Class'lar chuqurroq (private, static, inheritance)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/2ZphE5HcQPQ", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: TODO ilova (class + localStorage + fetch)",
     "text": None, "code": None, "lang": "javascript",
     "video": "https://youtu.be/Hej48pi_lOc", "exercises": L11_EX, "_ref": "L11"},
]


def _resolve_lessons() -> None:
    g = globals()
    for row in LESSONS:
        ref = row["_ref"]
        row["text"] = g[f"{ref}_TEXT"]
        row["code"] = g[f"{ref}_CODE"]


# ─────────────────────────────────────────────────────────────────────────────
# Seed / persistence
# ─────────────────────────────────────────────────────────────────────────────
def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson: dict, exercise_rows: list[Exercise]) -> str:
    sections = [
        {"id": f"t{lesson['order']}", "type": "text", "label": "Текст",
         "html": lesson["text"], "order": 0},
        {"id": f"c{lesson['order']}", "type": "code", "label": "Код",
         "code": lesson["code"], "lang": lesson["lang"], "order": 1},
        {"id": f"v{lesson['order']}", "type": "video", "label": "Видео",
         "videoUrl": lesson["video"], "order": 2},
        {"id": f"e{lesson['order']}", "type": "exercise", "label": "Упражнения",
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
         "order": 3},
    ]
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    _resolve_lessons()

    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if existing:
            print(f"Course '{COURSE['title']}' already exists (id={existing.id}). "
                  f"Delete it first if you want to re-seed.")
            return

        course = Course(**COURSE)
        db.add(course)
        await db.flush()
        print(f"Created course: id={course.id}  title='{course.title}'")

        for ldata in LESSONS:
            task = LESSON_TASKS.get(ldata["order"], {})
            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=10,
                text_content=ldata["text"],
                code_content=ldata["code"],
                code_language=ldata["lang"],
                video_url=ldata["video"],
                sections_json=None,
                task_title=task.get("title"),
                task_description=task.get("description"),
                task_requirements=task.get("requirements"),
                task_technologies=task.get("technologies"),
                task_deadline_days=task.get("deadline_days"),
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ldata["exercises"]):
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

            lesson.sections_json = build_sections_json(ldata, ex_rows)
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<60}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded course '{COURSE['title']}' with "
                  f"{len(LESSONS)} lessons and "
                  f"{sum(len(l['exercises']) for l in LESSONS)} exercises.")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
