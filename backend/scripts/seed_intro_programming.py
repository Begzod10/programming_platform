"""Seed the "Dasturlash dunyosiga kirish" course (8 lessons, ~45 exercises).

A short, punchy intro-to-programming course for absolute beginners with no
prior coding experience. Sits BEFORE every other beginner course
(HTML/CSS, Python Asoslari, Javascript) and answers two questions:

  1. What is programming, how does code run, and what can I build with it?
  2. Which language should I learn next?

Capstone: deploy a one-page HTML "About me" site to GitHub Pages.

Usage:
    cd backend
    python scripts/seed_intro_programming.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.
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
    "title": "Dasturlash dunyosiga kirish",
    "description": (
        "Dasturlash dunyosiga birinchi qadam. Hech qachon kod yozmagan bo'lsangiz "
        "ham — bu yerdan boshlang. 8 ta qisqa dars: dasturlash nima, qaysi tilni "
        "tanlash, kompyuter qanday ishlaydi, terminal va Git. Yakuniy loyiha: "
        "birinchi sahifangizni internetga chiqarish (GitHub Pages)."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 3,
    "max_points": 160,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# L1 — Dasturlash nima va u qayerda yashaydi
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Salom! Birinchi kodingizni 5 daqiqada yozasiz</h2>

<pre class="mermaid">
flowchart LR
    Y["1. Siz kod yozasiz"] -->|alert salom| I["2. Interpreter o'qib tushunadi"]
    I -->|tarjima qiladi| CPU["3. CPU bajaradi"]
    CPU -->|natija| OUT["4. Siz ekranda ko'rasiz"]
</pre>

<p>Bu kurs <strong>asoslar</strong> (foundations) darsidir — biz hozir haqiqiy dastur yozishni boshlamaymiz. Maqsad boshqa: <em>dasturchi miyasini qurish</em>. Kompyuter qanday "o'ylaydi", kod nima, xato qanday o'qiladi. Real kod keyingi kurslarda boshlanadi.</p>

<p>Lekin nazariyadan oldin — amaliyot. Siz hozir, shu daqiqaning o'zida, brauzeringizda birinchi buyrug'ingizni berasiz. Va u sizni tinglaydi.</p>

<h3>⚡ Birinchi 5 daqiqa — siz dasturchi bo'lasiz</h3>
<p>Hech narsani o'rnatish kerak emas. Brauzeringiz yetarli. Quyidagi 4 ta qadamni AYNAN bajaring:</p>

<ol>
<li><strong>Brauzerda yangi yorliq oching</strong> va <code>https://google.com</code> ga kiring.</li>
<li><strong>Klaviaturada <code>F12</code> tugmasini bosing.</strong> (Mac uchun: <code>Option + Cmd + I</code>). Yuqorida yashirin panel — <strong>DevTools</strong> — ochiladi.</li>
<li><strong>Panelning yuqorisida <code>Console</code> yorlig'ini bosing.</strong></li>
<li><strong>Quyidagi qatorni AYNAN yozing va <code>Enter</code> bosing:</strong>
<pre><code>alert("Salom, men dastur yozyapman!")</code></pre>
</li>
</ol>

<p>Ekranda xabar oynasi paydo bo'ldi?</p>
<p>🎉 <strong>Tabriklaymiz.</strong> Siz hozir hayotingizdagi birinchi kod qatoringizni yozdingiz va kompyuter sizning buyrug'ingizni bajardi. Bu — dasturlash. Boshqa hech narsa emas: <strong>siz aytdingiz, kompyuter qildi.</strong></p>

<h3>🎮 Ko'proq o'ynaymiz</h3>
<p>Konsolni yopmang. Quyidagi har bir qatorni alohida yozing, <code>Enter</code> bosing, natijani ko'ring.</p>

<h4>1. Kompyuter sizning kalkulyatoringiz</h4>
<pre><code>console.log(2 + 2)
console.log(1000 * 365)
console.log(100 / 7)</code></pre>
<p>Pastda raqamlar chiqdimi? Demak konsol — dunyodagi eng kuchli kalkulyator.</p>

<h4>2. So'zlar bilan ishlash</h4>
<pre><code>console.log("Men" + " " + "dasturchi" + " " + "bo'ldim!")</code></pre>

<h4>3. Saytni o'zgartiring</h4>
<pre><code>document.body.style.background = "pink"</code></pre>
<p>Google sahifasi pushti bo'ldi! Sahifani yangilang (<code>F5</code>) — hammasi qaytariladi. Bu o'zgarish <strong>faqat sizning brauzerangizda</strong> — boshqa hech kim ko'rmaydi.</p>

<h4>4. Sizdan savol so'rang</h4>
<pre><code>let ism = prompt("Ismingiz nima?");
alert("Xush kelibsiz, " + ism + "!");</code></pre>

<h3>💡 Endi tushuntiramiz — sizning kodingiz qanday ishladi?</h3>
<p>Siz <code>alert("Salom")</code> yozdingiz. Bu uzoq sayohatni boshladi:</p>
<ol>
<li><strong>Code</strong> — sizning yozganingiz brauzerga uzatildi.</li>
<li><strong>JavaScript interpreter</strong> — brauzer ichidagi tarjimon sizning kodni o'qidi va uni mashina tushunadigan signallarga aylantirdi.</li>
<li><strong>CPU</strong> — kompyuterning "miyasi" signallarni bajardi: elektr orqali xabar oynasini chizdi.</li>
<li><strong>Natija</strong> — siz ekranda <code>alert</code> ni ko'rdingiz.</li>
</ol>
<p>Bu — har qanday dasturlashning asosi. Til o'zgaradi (Python, Java, C++, Go), lekin zanjir bir xil: <strong>Code → Interpreter (yoki Compiler) → CPU → Natija</strong>.</p>

<h3>🔧 Interpreter vs Compiler — kichik farq</h3>
<table>
<tr><th></th><th>Interpreter</th><th>Compiler</th></tr>
<tr><td>Misol tillar</td><td>JavaScript, Python, Ruby</td><td>C, C++, Go, Rust</td></tr>
<tr><td>Qanday ishlaydi</td><td>Qatorma-qator o'qib darhol bajaradi</td><td>Butun kodni bir marta mashina tiliga aylantiradi</td></tr>
<tr><td>Tezlik</td><td>Sekinroq</td><td>Tezroq</td></tr>
<tr><td>Tuzatish</td><td>Tezroq sinash mumkin</td><td>Har o'zgarishdan keyin qayta compile qilish kerak</td></tr>
</table>

<h3>🌍 Dastur qayerda yashaydi?</h3>
<table>
<tr><th>Joy</th><th>Misol</th><th>Til</th></tr>
<tr><td>Veb-sayt</td><td>Google, YouTube, Telegram Web</td><td>JavaScript, Python, Go</td></tr>
<tr><td>Mobil ilova</td><td>Instagram, Uber, banking ilovasi</td><td>Swift (iOS), Kotlin (Android)</td></tr>
<tr><td>Sun'iy intellekt</td><td>ChatGPT, Midjourney</td><td>Python</td></tr>
<tr><td>O'yinlar</td><td>Minecraft, Fortnite</td><td>C++, C#</td></tr>
<tr><td>Smart soat / robot</td><td>Apple Watch, robot pylesos</td><td>C, Rust</td></tr>
</table>

<h3>📝 Algoritm — kompyuterning "fikr-tartibi"</h3>
<p><strong>Algoritm</strong> — bu tartibli qadamlar ro'yxati. Algoritm — bu <strong>kod EMAS</strong>. Kod — algoritmni biror tilda yozish.</p>
<p>Choy damlash — bu algoritm:</p>
<ol>
<li>Qaynoq suv tayyorlang</li>
<li>Choynakka 1 qoshiq choy soling</li>
<li>Qaynoq suv quying</li>
<li>3–5 daqiqa kuting</li>
<li>Stakanga quying</li>
</ol>
<p>Algoritmda 3 ta "qurilish bloki" bor:</p>
<ul>
<li><strong>Ketma-ket</strong> qadamlar (1 → 2 → 3)</li>
<li><strong>Shart</strong> ("agar choy juda qattiq bo'lsa, ko'proq suv qo'shing")</li>
<li><strong>Takror</strong> ("stakan to'lguncha quying")</li>
</ul>
<p>Kompyuter dasturlari ham xuddi shunaqa: ketma-ket + shartlar + takrorlar.</p>

<h3>⚠️ Xato chiqdi — qo'rqmang!</h3>
<p>Konsolda quyidagini yozib ko'ring (ataylab katta harf bilan):</p>
<pre><code>Alert("Test")</code></pre>
<p>Qizil xato chiqadi:</p>
<pre><code>Uncaught ReferenceError: Alert is not defined</code></pre>
<p><strong>Bu juda yaxshi!</strong> Siz xato qildingiz. Tabriklaymiz — siz endi haqiqiy dasturchisiz, chunki dasturchining ishi 80% xatolarni tuzatishdir.</p>
<p>Xato xabari sizga aytayotgan narsa:</p>
<ul>
<li><code>Alert</code> — mavjud emas (kompyuter "Alert" ni bilmaydi)</li>
<li><code>alert</code> (kichik harf) — mavjud. Qayta yozing.</li>
</ul>
<p>📚 <strong>Dasturchining birinchi qoidasi:</strong> Xato — bu kompyuteringizning sizga aniq nima xato ekanligini aytayotgani. Qo'rqmang — <em>o'qing</em>. Xato matnidagi BIRINCHI muhim so'zni o'qing va Google'da qidiring.</p>

<h3>🚀 Sizning yo'lingiz endi boshlandi</h3>
<p>Bu kursni tugatganingizda siz:</p>
<ul>
<li>Dasturlashning butun olamini ko'rasiz (8 ta qisqa dars)</li>
<li>Algoritmik fikrlashni o'rganasiz</li>
<li>Terminal va Git ishlay olasiz</li>
<li>Yakuniy loyihada o'z saytingizni internetga chiqarasiz (GitHub Pages)</li>
</ul>
<p>Lekin bu darsdagi eng muhim narsa — siz <strong>"men buni uddalayman"</strong> degan ishonchni qo'lga kiritdingiz. Bu — dasturchi bo'lishning yarmi.</p>
"""

L1_CODE = """\
// 🎉 Brauzer konsoliga (DevTools -> Console) yozish uchun
// nusxa olib, har bir qatorni alohida Enter bilan ishga tushiring.
// Avval https://google.com ni oching, keyin F12 (Mac: Option+Cmd+I).

// 1. Birinchi buyruq — xabar oynasi
alert("Salom, men dastur yozyapman!");

// 2. Konsol — sizning kalkulyatoringiz
console.log(2 + 2);
console.log(1000 * 365);
console.log(100 / 7);

// 3. So'zlarni qo'shish (concatenation)
console.log("Men" + " " + "dasturchi" + " " + "bo'ldim!");

// 4. Saytni o'zgartirish — faqat sizning brauzerangizda
document.body.style.background = "pink";
document.body.style.color = "darkblue";

// 5. Foydalanuvchi bilan muloqot
let ism = prompt("Ismingiz nima?");
let yosh = prompt("Yoshingiz nechida?");
alert("Salom " + ism + "! Siz " + yosh + " yoshda dasturchi bo'ldingiz!");

// 6. Xato — ataylab katta harf bilan, qo'rqmang!
// Alert("Test")
// -> Uncaught ReferenceError: Alert is not defined
// Sabab: "Alert" mavjud emas. Yechim: "alert" (kichik harf).

// Bularning hammasi — sizning birinchi haqiqiy
// dasturlash tajribangiz. Sahifani yangilang —
// hammasi qaytadi, hech narsani buzmaysiz.
"""


# ═════════════════════════════════════════════════════════════════════════════
# L2 — Qaysi tilni o'rganay?
# ═════════════════════════════════════════════════════════════════════════════
L2_TEXT = """\
<h2>3 ta tilni 5 daqiqada sinab ko'rasiz</h2>

<pre class="mermaid">
flowchart TB
    Q["Nima qurmoqchisiz"] --> WEB["veb-sayt"]
    Q --> MOB["mobile ilova"]
    Q --> AI["AI ML"]
    Q --> DATA["ma'lumotlar tahlili"]
    Q --> GAME["o'yin"]
    Q --> SYS["tizim past darajadagi"]
    WEB --> HCJ["HTML CSS JavaScript"]
    MOB --> SK["Swift iOS yoki Kotlin Android"]
    AI --> PY1["Python"]
    DATA --> PY2["Python yoki R"]
    GAME --> CS["C plus plus yoki C sharp"]
    SYS --> RC["C Rust"]
</pre>

<p>Bu darsda biz "qaysi til eng yaxshi?" savoliga javob beramiz. Lekin nazariyadan oldin — siz hozir, shu daqiqaning o'zida, <strong>3 ta tilda</strong> dastur yozasiz. Hech narsani o'rnatish kerak emas. Brauzeringiz va internet yetarli.</p>

<h3>⚡ Birinchi 5 daqiqa — siz polyglot bo'lasiz</h3>
<p>Quyidagi 3 ta tilda bir xil amalni — <strong>"Salom, dunyo!" matnini ekranga chiqarish</strong> — bajaring. Sintaksis farqlanadi, g'oya bir xil.</p>

<h4>🟨 Til 1: JavaScript (brauzer konsoli)</h4>
<ol>
<li>Yangi yorliqda <code>https://google.com</code> ni oching.</li>
<li><code>F12</code> (Mac: <code>Option + Cmd + I</code>) → <code>Console</code> yorlig'i.</li>
<li>Yozing va <code>Enter</code>:
<pre><code>console.log("Salom, dunyo!")</code></pre>
</li>
</ol>
<p>Natija: konsolda <code>Salom, dunyo!</code> chiqadi. (1-darsdan tanish.)</p>

<h4>🟧 Til 2: HTML (brauzer manzil satrida — server kerak emas!)</h4>
<ol>
<li>Brauzeringizning yuqorisidagi <strong>manzil satriga</strong> (URL bar) quyidagini AYNAN ko'chiring va <code>Enter</code> bosing:
<pre><code>data:text/html,&lt;h1&gt;Salom, dunyo!&lt;/h1&gt;&lt;p&gt;Men HTML yozdim.&lt;/p&gt;</code></pre>
</li>
</ol>
<p>Brauzer to'liq sahifa shaklida ko'rsatadi! Bu — <strong>HTML</strong> — sahifa tuzilmasini tasvirlash tili. <code>data:text/html,...</code> sxemasi brauzerga "matn HTML deb tushun, fayldan o'qima" deydi — server ham, fayl ham kerak emas.</p>

<h4>🟦 Til 3: Python (onlayn shell)</h4>
<ol>
<li>Yangi yorliqda <code>https://www.python.org/shell/</code> ni oching. (Bu Python tilining rasmiy onlayn interpreteri.)</li>
<li>Yuklanguncha bir oz kuting (Loading skameykalari).</li>
<li><code>&gt;&gt;&gt;</code> belgisidan keyin yozing va <code>Enter</code>:
<pre><code>print("Salom, dunyo!")</code></pre>
</li>
</ol>
<p>Natija: <code>Salom, dunyo!</code></p>

<p>🎉 <strong>Tabriklaymiz!</strong> Siz hozir <strong>3 ta tilda</strong> dastur yozdingiz va brauzeringizdan tashqari hech narsa o'rnatmadingiz. Sintaksis 3 xil edi, lekin g'oya bir xil: "matnni ekranga chiqar". Bu — har qanday dasturlash tilining birinchi va eng muhim qadami.</p>

<h3>💡 Endi tushuntiramiz — nima uchun 3 xil til?</h3>
<p>Har bir dasturlash tili muayyan ish uchun yaratilgan. Til tanlash — bu asbob tanlash: bolg'a bilan o'tin yorish mumkin, lekin tikuv mashinasi uchun u ishlamaydi.</p>

<table>
<tr><th>Til</th><th>Qayerda ishlaydi</th><th>Eng yaxshi nimaga</th></tr>
<tr><td><strong>JavaScript</strong></td><td>Brauzer (frontend), server (Node.js)</td><td>Veb-saytni jonlantirish</td></tr>
<tr><td><strong>HTML + CSS</strong></td><td>Brauzer</td><td>Sahifa tuzilmasi va stillari (asl dasturlash tili emas — "markup" tili)</td></tr>
<tr><td><strong>Python</strong></td><td>Server, AI, skriptlar, ma'lumot tahlili</td><td>Universal — har joyda ishlatiladi</td></tr>
<tr><td><strong>Swift / Kotlin</strong></td><td>Telefon — iOS / Android</td><td>Mobil ilovalar</td></tr>
<tr><td><strong>C / C++ / Rust</strong></td><td>Tizim darajasi, drayverlar</td><td>Tezlik kerak bo'lganda</td></tr>
<tr><td><strong>C# / C++</strong></td><td>Game engine (Unity, Unreal)</td><td>O'yinlar</td></tr>
</table>

<h3>🎯 Maqsadingizga qarab tanlash</h3>
<table>
<tr><th>Maqsadingiz</th><th>Tavsiya</th><th>Sabab</th></tr>
<tr><td>Birinchi marta o'rganaman, qanday ekanini bilmoqchiman</td><td><strong>Python</strong> yoki HTML+CSS</td><td>Sodda sintaksis, tez natija</td></tr>
<tr><td>Veb-sayt yasamoqchiman</td><td>HTML/CSS → JavaScript → Python (Flask/Django)</td><td>Frontend va backend ikkalasi kerak</td></tr>
<tr><td>iPhone yoki Android ilova</td><td>Swift (iOS), Kotlin (Android), Flutter (ikkalasi)</td><td>Har platforma o'z tilini sevadi</td></tr>
<tr><td>AI / ChatGPT kabi loyihalar</td><td><strong>Python</strong></td><td>PyTorch, TensorFlow, sklearn — barchasi Python uchun</td></tr>
<tr><td>O'yin yasamoqchiman</td><td>C# (Unity), C++ (Unreal)</td><td>Game engine'lar shu tillarda yozilgan</td></tr>
<tr><td>Ish topish (umumiy)</td><td>JavaScript yoki Python yoki Java</td><td>Eng ko'p vakansiya bor</td></tr>
<tr><td>Tizim, drayver, OS</td><td>C, Rust, C++</td><td>Mashinaga yaqin, juda tez</td></tr>
</table>

<h3>⚠️ 3 ta katta yolg'on (ehtiyot bo'ling)</h3>
<ol>
<li><strong>"Eng yaxshi til bor"</strong> — yo'q. Har birining o'z joyi bor. Python AI uchun yaxshi, lekin o'yin uchun emas.</li>
<li><strong>"Bitta tilni mukammal bilish kifoya"</strong> — yo'q. Tajribali dasturchilar 3-5 ta tilni biladi.</li>
<li><strong>"30 kunda dasturchi bo'lasan"</strong> — yo'q. Asoslarni 30 kunda — ha. Tajribali bo'lish — 2-5 yil. Sabr-toqat kerak.</li>
</ol>

<h3>⚠️ Xato chiqdi — qo'rqmang!</h3>
<p>Python shell ga quyidagini yozib ko'ring (ataylab tirnoq ochiq):</p>
<pre><code>print("Salom)</code></pre>
<p>Xato chiqadi:</p>
<pre><code>SyntaxError: EOL while scanning string literal</code></pre>
<p>Bu xato sizga aytayotgan narsa: <code>EOL</code> = "end of line" (satr oxiri). Demak: <strong>satr oxiriga keldim, lekin string yopilmagan</strong>. Yechim: yopuvchi tirnoq qo'shing → <code>print("Salom")</code>.</p>
<p>📚 <strong>Eslatma:</strong> Har tilda xato xabarlari boshqacha so'zlarda yoziladi, lekin g'oya bir xil — kompyuter sizga aniq nima xato ekanligini aytadi. Birinchi muhim so'zni topib o'qing.</p>

<h3>🚀 Bu platformada quyidagi yo'llar bor</h3>
<p>Bu kursdan keyin keyingi kursingizni tanlash uchun:</p>
<ul>
<li>📘 <strong>HTML CSS</strong> — vizual natijani tezda ko'rishni xohlovchilar uchun</li>
<li>📗 <strong>Javascript</strong> — saytni jonlantirish uchun</li>
<li>📕 <strong>Python Asoslari</strong> — universal yo'l (AI, web, avtomatlash)</li>
<li>📓 <strong>Python Flask</strong> — Python ni bilganlar uchun veb ilovalar</li>
</ul>
<p><strong>Tavsiya:</strong></p>
<ul>
<li>Agar vizual natija tezda kerak bo'lsa — <strong>HTML CSS</strong> dan boshlang.</li>
<li>Agar mantiqiy fikrlash va keng imkoniyatlar kerak bo'lsa — <strong>Python Asoslari</strong>.</li>
<li>Agar siz allaqachon HTML ni bilsangiz — <strong>Javascript</strong>.</li>
</ul>

<h3>🧠 Bu darsdan qoldiriladigan asosiy fikr</h3>
<p>Til — bu asbob. Asbobni tanlash uchun avval <strong>nima qurmoqchi ekanligingizni</strong> aniqlang. Til avval — yo'l keyin emas. Yo'l avval — til keyin. 🚀</p>
"""

L2_CODE = """\
// 3 ta tilda "Salom, dunyo!" — siz hozir o'zingiz sinab ko'rasiz.
// Hech narsa o'rnatish kerak emas, faqat brauzer.

// ─── Til 1: JavaScript (brauzer konsoli) ──────────────────
// F12 → Console, keyin yozing va Enter:
console.log("Salom, dunyo!");

// ─── Til 2: HTML (brauzer manzil satrida) ─────────────────
// Brauzeringizning yuqorisidagi URL satriga AYNAN ko'chiring:
//
//   data:text/html,<h1>Salom, dunyo!</h1><p>Men HTML yozdim.</p>
//
// "data:" sxemasi brauzerga "matn HTML deb tushun" deydi.
// Server kerak emas, .html fayl ham kerak emas.

// ─── Til 3: Python (onlayn shell) ─────────────────────────
// https://www.python.org/shell/ ni oching, >>> dan keyin:
//
//   print("Salom, dunyo!")

// ─── Til 4 (bonus): C — compiled, tez ─────────────────────
// Bu tilni o'rnatish kerak — hozir faqat ko'ring:
//
//   #include <stdio.h>
//   int main() {
//       printf("Salom, dunyo!\\n");
//       return 0;
//   }

// Til o'zgaradi — g'oya bir xil:
//   1. "Salom, dunyo!" matnini ol
//   2. Ekranga chiqar
//
// Sintaksis farqi sizni qo'rqitmasin — har tilning o'z sababi bor.
//
// Veb-sayt        → JavaScript (+ HTML/CSS)
// AI / ma'lumot   → Python
// Mobil ilova     → Swift (iOS) yoki Kotlin (Android)
// O'yin           → C# (Unity) yoki C++ (Unreal)
// Tezlik / tizim  → C yoki Rust
"""


# ═════════════════════════════════════════════════════════════════════════════
# L3 — Kompyuter qisqacha
# ═════════════════════════════════════════════════════════════════════════════
L3_TEXT = """\
<h2>Kompyuteringizni siz o'zingiz tahlil qilasiz</h2>

<pre class="mermaid">
flowchart LR
    KB["keyboard mouse"] --> CPU["CPU miya"]
    CPU <--> RAM["RAM tez vaqtinchalik"]
    CPU <--> DISK["disk doimiy"]
    CPU --> SC["screen output"]
    NET["network internet"] <--> CPU
    OS["operatsion tizim"] -.->|boshqaradi| CPU
</pre>

<p>Dasturchi kompyuter ichida nima bo'layotganini tushunishi kerak — kod nega tez yoki sekin ishlaydi, fayl qayerda yashaydi, "RAM yetmaydi" xabari nima degani. Lekin biz nazariyadan oldin — siz hozir <strong>o'zingizning kompyuteringizning aniq texnik xususiyatlarini</strong> brauzeringizdan ko'rib chiqasiz.</p>

<h3>⚡ Birinchi 5 daqiqa — o'z kompyuteringizning ichini ochasiz</h3>
<p>Hech qanday dastur o'rnatish kerak emas. F12 → Console — 1-darsdan tanish. Quyidagi har bir qatorni yozing va <code>Enter</code> bosing:</p>

<pre><code>// 1. Brauzer + OS haqida
navigator.userAgent

// 2. CPU yadrolar (cores) soni
navigator.hardwareConcurrency

// 3. RAM darajasi (GB taxminan)
navigator.deviceMemory

// 4. OS turi
navigator.platform

// 5. Ekran o'lchami
screen.width + " x " + screen.height

// 6. Internet tezligi (so'rovga oid)
navigator.connection &amp;&amp; navigator.connection.effectiveType</code></pre>

<p>🎉 Tabriklaymiz — siz hozir <strong>o'z kompyuteringizning pasportini</strong> ochdingiz. Bu raqamlarni yodda saqlang — loyihada keraksiz.</p>

<h3>🎮 RAM vs Disk — siz buni qo'lda sezasiz</h3>
<p>Endi eng chalkashtiriladigan tushuncha — RAM va Disk farqi. Demo:</p>

<h4>Tajriba 1: Disk-kabi xotira (saqlanib qoladi)</h4>
<pre><code>// localStorage — brauzerdagi "mini-disk"
localStorage.setItem("mening_ismim", "Aziz")
localStorage.getItem("mening_ismim")
// "Aziz" qaytadi</code></pre>

<p>Endi brauzerni <strong>butunlay yoping va qayta oching</strong>. Konsolda yana yozing:</p>
<pre><code>localStorage.getItem("mening_ismim")
// "Aziz" — hali ham bor!</code></pre>

<h4>Tajriba 2: RAM-kabi xotira (yo'qoladi)</h4>
<pre><code>// Oddiy o'zgaruvchi — vaqtinchalik
let mening_ismim = "Aziz"
console.log(mening_ismim)
// "Aziz"</code></pre>

<p>Endi <strong>sahifani yangilang (F5)</strong>. Konsolda yana yozing:</p>
<pre><code>console.log(mening_ismim)
// Uncaught ReferenceError: mening_ismim is not defined
// yo'q bo'lib ketdi!</code></pre>

<p>👏 Siz hozir <strong>RAM va Disk farqini qo'lda his qildingiz</strong>:</p>
<ul>
<li><strong>RAM (oddiy o'zgaruvchi)</strong>: tez ishlaydi, lekin sahifa o'chsa — yo'qoladi</li>
<li><strong>Disk (localStorage)</strong>: sekinroq, lekin doimo saqlanadi</li>
</ul>

<h3>💡 Endi tushuntiramiz — 4 ta asosiy qism</h3>
<table>
<tr><th>Qism</th><th>Vazifasi</th><th>Misol</th></tr>
<tr><td><strong>CPU</strong> (protsessor)</td><td>"Miya" — barcha hisob-kitoblar va qarorlar shu yerda. Yadro (core) qancha ko'p — parallel ishlar shuncha ko'p</td><td>Intel Core i5, Apple M2, AMD Ryzen</td></tr>
<tr><td><strong>RAM</strong> (operativ xotira)</td><td>Tez lekin vaqtinchalik. Kompyuter o'chsa — hammasi yo'qoladi. Hozir ochiq dasturlar shu yerda yashaydi</td><td>4 GB, 8 GB, 16 GB</td></tr>
<tr><td><strong>Disk</strong> (HDD / SSD)</td><td>Doimiy xotira — kompyuter o'chsa ham saqlanadi. Sekinroq, lekin katta hajmli. SSD — HDD dan 10-100 marta tezroq</td><td>256 GB SSD, 1 TB HDD</td></tr>
<tr><td><strong>Network</strong></td><td>Boshqa kompyuterlar bilan bog'lanish — internet</td><td>Wi-Fi, Ethernet kabel, 4G/5G</td></tr>
</table>

<h3>📊 RAM vs Disk — taqqoslash</h3>
<table>
<tr><th></th><th>RAM</th><th>Disk</th></tr>
<tr><td>Tezlik</td><td>~10-100 GB/s</td><td>SSD: 0.5-5 GB/s, HDD: 0.1 GB/s</td></tr>
<tr><td>Hajm</td><td>4-32 GB</td><td>256 GB - 4 TB</td></tr>
<tr><td>O'chsa nima bo'ladi?</td><td>Hammasi yo'qoladi 💨</td><td>Saqlanib qoladi ✅</td></tr>
<tr><td>Misol</td><td>Hozir ochiq dasturlar</td><td>Fayllar, rasm, video</td></tr>
</table>
<p>Tasavvur qiling: ish stolingiz — bu <strong>RAM</strong>. Kitob javoningiz — bu <strong>Disk</strong>. Stoldagi narsalarga tez kirasiz, lekin u kichik. Javondan kerakli kitobni stolga olasiz (Disk → RAM), ish tugagach javonga qaytarasiz.</p>

<h3>🖥 Operatsion tizim (OS)</h3>
<p>OS — kompyuterning <strong>menejeri</strong>. Dasturlar va qismlar o'rtasida mediator:</p>
<ul>
<li><strong>Windows</strong> — keng tarqalgan ish kompyuterlarida</li>
<li><strong>macOS</strong> — Apple kompyuterlari</li>
<li><strong>Linux</strong> — serverlar, dasturchilar, embedded qurilmalar (Ubuntu, Fedora...)</li>
<li><strong>Android / iOS</strong> — mobile</li>
</ul>
<p>Dasturchilar ko'pincha <strong>Linux</strong> yoki <strong>macOS</strong> ni afzal ko'radi — chunki ular Unix asosida qurilgan va terminal bilan yaxshi ishlaydi.</p>

<h3>📁 Fayllar, papkalar va path</h3>
<p>Hamma ma'lumot diskda <strong>fayl</strong> shaklida saqlanadi. Fayllar <strong>papkalar</strong>da guruhlanadi. Har faylning manzili — <strong>path</strong> (yo'l):</p>
<pre><code># Linux / macOS — forward slash
/home/aziz/Documents/loyiha/index.html

# Windows — backward slash
C:\\Users\\Aziz\\Documents\\loyiha\\index.html</code></pre>

<h3>🗺 Ikki turdagi path</h3>
<table>
<tr><th>Tur</th><th>Boshlanishi</th><th>Misol</th><th>Qachon ishlatiladi</th></tr>
<tr><td><strong>Absolute</strong></td><td>"/" dan (yoki "C:\\")</td><td><code>/home/aziz/file.txt</code></td><td>Aniq joyni ko'rsatish kerak bo'lganda</td></tr>
<tr><td><strong>Relative</strong></td><td>"./" yoki ".." dan</td><td><code>./file.txt</code>, <code>../boshqa/file.txt</code></td><td>Joriy joydan boshqa joyni topish</td></tr>
</table>
<ul>
<li><code>.</code> — joriy papka (bu yerda)</li>
<li><code>..</code> — yuqoridagi papka (parent)</li>
<li><code>~</code> — uy papkangiz (Linux/macOS)</li>
<li><code>/</code> — Linux/Mac: ildiz papka, Windows: drive ildiz</li>
</ul>

<h3>📏 Bayt, kilobayt, megabayt — birliklar</h3>
<ul>
<li><strong>1 bit</strong> = 0 yoki 1</li>
<li><strong>1 bayt</strong> = 8 bit (bitta inglizcha harfni saqlash uchun yetadi)</li>
<li><strong>1 KB</strong> = 1024 bayt (qisqa matn)</li>
<li><strong>1 MB</strong> = 1024 KB (kichik rasm yoki MP3 qo'shig'i)</li>
<li><strong>1 GB</strong> = 1024 MB (1 soat HD video)</li>
<li><strong>1 TB</strong> = 1024 GB (deyarli butun musiqa kolleksiyasi)</li>
</ul>

<h3>⚠️ Xato chiqdi — qo'rqmang!</h3>
<p>Konsolda yangi sahifani oching (yangi yorliqda <code>google.com</code>) va yozing:</p>
<pre><code>localStorage.getItem("mening_ismim")</code></pre>
<p>Natija: <code>null</code> — bo'sh. Bu xato emas — bu shunchaki <strong>"bu sayt uchun bunday nom bor emas"</strong> degani.</p>
<p>Lekin xato namunasi ko'ring:</p>
<pre><code>navigator.deviceMemori   // ataylab xato yozildi</code></pre>
<p>Natija:</p>
<pre><code>undefined</code></pre>
<p><code>undefined</code> — JavaScript da "bunday xususiyat yo'q" degani. To'g'risi: <code>deviceMemory</code> (oxirida "y"). 📚 <strong>Eslatma:</strong> dasturlashda har bir harf muhim — typo eng ko'p uchraydigan xato.</p>

<h3>🚀 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Sizning kompyuteringizning aniq texnik xususiyatlari</li>
<li>RAM va Disk orasidagi farq (siz buni qo'lda his qildingiz)</li>
<li>Path nima va u qanday yoziladi</li>
<li>Operatsion tizim qaysi rolda</li>
</ul>
<p>Bu bilim keyingi darslarda — fayllar bilan ishlashda, terminalda, Git ishlatishda — kerak bo'ladi.</p>
"""

L3_CODE = """\
// ═══════════════════════════════════════════════════════
// O'z kompyuteringizning pasportini brauzerdan oching
// (F12 → Console, har qatorni alohida Enter bilan)
// ═══════════════════════════════════════════════════════

// 1. Brauzer + OS
navigator.userAgent;

// 2. CPU yadrolar (parallel ishlar uchun)
navigator.hardwareConcurrency;

// 3. RAM taxminiy darajasi (GB)
navigator.deviceMemory;

// 4. OS turi
navigator.platform;

// 5. Ekran o'lchami
screen.width + " x " + screen.height;

// 6. Internet turi (4g, 3g, slow-2g ...)
navigator.connection && navigator.connection.effectiveType;


// ═══════════════════════════════════════════════════════
// RAM vs Disk — siz qo'lda his qilasiz
// ═══════════════════════════════════════════════════════

// Disk-kabi (localStorage — saqlanib qoladi)
localStorage.setItem("mening_ismim", "Aziz");
localStorage.getItem("mening_ismim");
// Brauzerni yopib qayta oching — qiymat hali ham bor

// RAM-kabi (oddiy o'zgaruvchi — yo'qoladi)
let mening_ismim = "Aziz";
console.log(mening_ismim);
// Sahifani yangilang (F5) — qayta yozsangiz: ReferenceError


// ═══════════════════════════════════════════════════════
// Universal — fayl tizimi haqida (terminal komandalari)
// Bu komandalarni keyingi darslarda terminalda ishlatasiz
// ═══════════════════════════════════════════════════════

// Linux / macOS:
//   pwd          — joriy papka
//   ls -lah      — papkadagi fayllar (yashirin bilan)
//   lscpu        — CPU info (Linux)
//   free -h      — RAM info (Linux)
//   df -h        — disk bo'shligi
//   du -sh .     — joriy papka hajmi

// Windows (PowerShell):
//   Get-Location           — joriy papka
//   Get-ChildItem          — papkadagi fayllar
//   Get-ComputerInfo       — CPU + RAM info
//   Get-PSDrive            — disk bo'shligi
"""


# ═════════════════════════════════════════════════════════════════════════════
# L4 — Algoritmik fikrlash
# ═════════════════════════════════════════════════════════════════════════════
L4_TEXT = """\
<h2>Google sahifasini robotga aylantiramiz</h2>

<pre class="mermaid">
flowchart TB
    S["alarm chaldi"] --> W["uyg'onish"]
    W --> CHK["ish kunimi"]
    CHK -->|ha| WK["yuvinish kiyinish"]
    CHK -->|yoq| RX["dam olish"]
    WK --> B["nonushta"]
    B --> GO["ish ga"]
    RX --> EN["uy ishlari"]
    GO --> END["kun boshlandi"]
    EN --> END
</pre>

<p>Bu darsda <strong>algoritmik fikrlashni</strong> o'rganamiz — bu dasturlashning eng muhim ko'nikmasi (til bilish — 20%, algoritmik fikrlash — 80%). Lekin nazariyadan oldin — siz hozir <strong>algoritmning 3 ta qurilish blokini</strong> brauzeringizda his qilasiz.</p>

<h3>⚡ Birinchi 5 daqiqa — 3 ta blokni his qilasiz</h3>
<p>Hech narsa o'rnatish kerak emas. Yangi yorliqda <code>https://google.com</code> ni oching. <code>F12</code> → Console. Quyidagi 3 ta blokni navbati bilan ko'chirib, har birini alohida ishga tushiring.</p>

<h4>🟢 Bloka 1: Ketma-ketlik (Sequence) — qadamlar tartibda bajariladi</h4>
<pre><code>document.body.style.background = "red";
document.title = "TO'XTANG!";
document.body.style.fontSize = "30px";</code></pre>
<p>Natija: Google sahifasi qizil rangga aylanadi, sarlavhasi (yorliq nomi) o'zgaradi, matnlar kattalashadi. <strong>3 ta qadam ketma-ket bajarildi.</strong></p>

<h4>🟡 Bloka 2: Shart (Condition) — "agar ... bo'lsa"</h4>
<pre><code>let yosh = prompt("Yoshingiz nechida?");
if (yosh &gt;= 18) {
    document.body.style.background = "green";
    alert("Voyaga yetgansiz!");
} else {
    document.body.style.background = "yellow";
    alert("Hali bolasiz");
}</code></pre>
<p>Natija: yoshingizga qarab sahifa <strong>yashil yoki sariq</strong> bo'ladi. Kompyuter <strong>qaror qabul qildi</strong>. Bir hil shart, ikki natijaning biri.</p>

<h4>🔴 Bloka 3: Takror (Loop) — bir xil amal qayta-qayta</h4>
<pre><code>const ranglar = ["red", "orange", "yellow", "green", "blue", "purple"];
for (let i = 0; i &lt; ranglar.length; i++) {
    setTimeout(() =&gt; {
        document.body.style.background = ranglar[i];
    }, i * 500);
}</code></pre>
<p>Natija: Google sahifasi har yarim soniyada rangini o'zgartiradi — qizil, to'q sariq, sariq, yashil, ko'k, binafsha. <strong>Bir amal 6 marta takrorlandi.</strong></p>

<p>🎉 <strong>Tabriklaymiz!</strong> Siz hozir <strong>algoritmning 3 ta qurilish blokini</strong> ishlatdingiz: ketma-ketlik, shart, takror. Bu uchtasi bilan dunyodagi har qanday dasturni yozish mumkin — Google, Telegram, Instagram, ChatGPT — barchasi shu 3 blokdan qurilgan.</p>

<h3>💡 Endi tushuntiramiz — algoritm nima?</h3>
<p><strong>Algoritm</strong> — bu muayyan natijaga olib boruvchi aniq qadamlar ketma-ketligi. Sizning ertalabki odatingiz — algoritm. Choy damlash — algoritm. Manzilni topish — algoritm. Har qanday "qanday qilamiz?" savoliga javob — algoritm.</p>

<h3>📐 3 ta qurilish bloki — kundalik misollarda</h3>

<h4>1️⃣ Ketma-ketlik (sequence) — har dasturda bor</h4>
<p>Qadamlarni tartib bilan bajarish. 1 → 2 → 3 → 4.</p>
<pre><code>Choy damlash:
1. Suv qaynat
2. Choynakka choy sol
3. Suv quy
4. 5 daqiqa kut
5. Stakanga quy</code></pre>

<h4>2️⃣ Shart (condition / decision) — qaror qabul qilish</h4>
<p>"Agar ... bo'lsa, ... qil. Aks holda — ... qil."</p>
<pre><code>Tashqariga chiqish:
1. Tashqarini ko'r
2. AGAR yomg'ir yog'sa:
       Soyabon ol
   AKS HOLDA:
       Quyoshli ko'zoynak ol
3. Tashqariga chiq</code></pre>

<h4>3️⃣ Takror (loop) — bir amalni qayta bajarish</h4>
<p>Bir xil ishni har xil narsalarga qo'llash.</p>
<pre><code>Pol yuvish:
1. Vedrani suv bilan to'ldir
2. HAR XONA UCHUN takrorlash:
       Xonaga kir
       Polni yuv
       Keyingi xonaga o't
3. Vedrani to'k</code></pre>

<h3>📊 Flowchart — algoritmni rasm shaklida</h3>
<p>Algoritmni so'z bilan emas, rasm bilan tasvirlash mumkin. Bu — <strong>flowchart</strong>:</p>
<ul>
<li><strong>Oval</strong> — boshlanish va tugash</li>
<li><strong>To'rtburchak</strong> — amal (nimadir qilish)</li>
<li><strong>Romb</strong> — shart (qaror qabul qilish)</li>
<li><strong>Strelka</strong> — qaysi qadamga o'tish</li>
</ul>
<p>Yuqoridagi hero rasm — "ertalabki odat" algoritmining flowchart'i. Romb shakli — shart ("ish kunimi?"), to'rtburchaklar — amallar.</p>

<h3>✅ Yaxshi algoritm qanday yoziladi?</h3>
<ol>
<li><strong>Aniq (precise)</strong> — har qadam bitta ma'noli. "Choy damla" — noaniq. "1 qoshiq choy sol" — aniq. Kompyuter taxmin qilmaydi.</li>
<li><strong>To'liq (complete)</strong> — barcha holatlar qamrab olingan. Yomg'ir holatini unutmang.</li>
<li><strong>Cheklangan (finite)</strong> — algoritm har doim tugaydi. Cheksiz sikldan ehtiyot bo'ling!</li>
<li><strong>Samarali (efficient)</strong> — bir ishni 100 qadamda emas, 5 qadamda bajarish.</li>
</ol>

<h3>⚠️ Cheksiz sikl — qo'rqing!</h3>
<p>Konsolga quyidagini yozmang (yoki yozing, lekin keyingi qadamga tayyor bo'ling):</p>
<pre><code>while (true) {
    console.log("Cheksiz sikl");
}</code></pre>
<p>Brauzer "qotib qoladi" — sikl hech qachon tugamaydi. Yechim: yorliqni yopish (X tugma) yoki <code>Ctrl+W</code>.</p>
<p>Bu — algoritmning "to'rtinchi qoidasi" buzilishi. <strong>Har qanday sikl tugashi shart.</strong> Aks holda kompyuter foydasiz ish bilan band bo'lib qoladi.</p>

<h3>🌍 Mashhur algoritmlar — siz har kuni ishlatasiz</h3>
<table>
<tr><th>Nom</th><th>Vazifasi</th><th>Qayerda ko'rinadi</th></tr>
<tr><td><strong>Binary search</strong></td><td>Saralanga ro'yxatdan tezda topish</td><td>Lug'atda so'z izlash, baza qidiruv</td></tr>
<tr><td><strong>Dijkstra</strong></td><td>Eng qisqa yo'lni topish</td><td>Yandex Maps, Google Maps</td></tr>
<tr><td><strong>PageRank</strong></td><td>Sahifalarni reytinglash</td><td>Google qidiruv natijalari</td></tr>
<tr><td><strong>SHA-256</strong></td><td>Ma'lumotning "barmoq izi"</td><td>Parol saqlash, Bitcoin</td></tr>
<tr><td><strong>RSA / TLS</strong></td><td>Ma'lumotni shifrlash</td><td>HTTPS saytlar, bank kartalari</td></tr>
</table>

<h3>🧠 Eng muhim ko'nikma</h3>
<p>Algoritmik fikrlash — bu kompyuterga emas, <strong>o'zingizga</strong> aytadigan ko'nikma:</p>
<ul>
<li><strong>Katta muammoni</strong> kichik bo'laklarga ajratish (decomposition)</li>
<li><strong>Har bo'lakka</strong> aniq ism berish</li>
<li><strong>Har bo'lakni</strong> alohida hal qilish</li>
<li><strong>Keyin birlashtirish</strong></li>
</ul>
<p>Bu — dasturlashning yuragi. Hech qachon kod yoza olmaydigan dasturchi yo'q — algoritmik fikrlay olmaydigan dasturchi bor. <strong>Til bilish — 20%. Algoritmik fikrlash — 80%.</strong></p>

<h3>🚀 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Algoritm — bu hayotning bir qismi, faqat kompyuter dunyosi emas</li>
<li>3 ta qurilish bloki: ketma-ketlik, shart, takror</li>
<li>Yaxshi algoritmning 4 ta xususiyati</li>
<li>Cheksiz sikldan qanday qutulish</li>
</ul>
<p>Keyingi darsda — o'zgaruvchilar va turlar. Algoritmlardan kodga o'tishimiz boshlanadi.</p>
"""

L4_CODE = """\
// ═══════════════════════════════════════════════════════
// Algoritmning 3 ta blokini brauzeringizda his qiling
// (google.com → F12 → Console → har blokni alohida)
// ═══════════════════════════════════════════════════════

// ─── 🟢 BLOKA 1: KETMA-KETLIK (Sequence) ───
// Qadamlar tartib bilan bajariladi
document.body.style.background = "red";
document.title = "TO'XTANG!";
document.body.style.fontSize = "30px";


// ─── 🟡 BLOKA 2: SHART (Condition / Decision) ───
// "Agar ... bo'lsa, ... qil. Aks holda — ... qil."
let yosh = prompt("Yoshingiz nechida?");
if (yosh >= 18) {
    document.body.style.background = "green";
    alert("Voyaga yetgansiz!");
} else {
    document.body.style.background = "yellow";
    alert("Hali bolasiz");
}


// ─── 🔴 BLOKA 3: TAKROR (Loop) ───
// Bir amal qayta-qayta — har xil rangda
const ranglar = ["red", "orange", "yellow", "green", "blue", "purple"];
for (let i = 0; i < ranglar.length; i++) {
    setTimeout(() => {
        document.body.style.background = ranglar[i];
    }, i * 500);
}


// ─── ⚠️ EHTIYOT: Cheksiz sikl — qo'rqing! ───
// Quyidagi kodni YOZMANG — brauzer qotib qoladi:
//
//   while (true) {
//       console.log("cheksiz");
//   }
//
// Sikl shartining tugashini ta'minlash — algoritmning
// 4-qoidasi: "har sikl tugashi shart" (finite).


// ═══════════════════════════════════════════════════════
// Pseudo-kod — "Manzilga borish" algoritmi
// Hech qanday tilda bajarilmaydi, lekin keyingi tilda
// yozish oson bo'ladi (mantiq tayyor)
// ═══════════════════════════════════════════════════════

// ALGORITM Manzilga_borish(boshlanish, manzil):
//     xarita_ochish()                          // sequence
//     yo'l_qidirish(boshlanish, manzil)
//
//     HAR yo'l_qadami UCHUN:                   // loop
//         AGAR yo'lda traffic bor:             // condition
//             muqobil_yo'l_qidir()
//         AGAR yoqilg'i kam (< 10%):
//             yoqilg'i_quygich_top()
//             yoqilg'i_qo'sh()
//         davom_etish()
//
//     manzilga_yetdik()
//     QAYTAR muvaffaqiyat
"""


# ═════════════════════════════════════════════════════════════════════════════
# L5 — O'zgaruvchilar va turlar (universal)
# ═════════════════════════════════════════════════════════════════════════════
L5_TEXT = """\
<h2>O'zgaruvchilar — qutichalarga yorliq yopishtiramiz</h2>

<pre class="mermaid">
flowchart LR
    L1["ism = Aziz"] -->|string| B1["matn quticha"]
    L2["yosh = 20"] -->|number| B2["son quticha"]
    L3["talaba = true"] -->|boolean| B3["ha yoki yoq"]
    L4["ranglar = qizil kok"] -->|array| B4["royhat quticha"]
    B1 --> CODE["dastur xotirasi"]
    B2 --> CODE
    B3 --> CODE
    B4 --> CODE
</pre>

<h3>🏆 5 daqiqada g'alaba — brauzer konsoli bizning xotiramiz</h3>
<p>Hech narsa o'rnatmaymiz. Yangi brauzer oynasi oching → URL qatoriga <code>about:blank</code> yozing → <kbd>F12</kbd> bosing → <strong>Console</strong> tabini tanlang. Endi kompyuter sizning komandalaringizni eshitishga tayyor.</p>

<h4>BLOKA 1 — Qutichalarga ism beramiz</h4>
<p>Pastdagi kodni nusxalang va konsolga yopishtiring (Enter bosing):</p>
<pre><code>// Har bir qatorda: yorliq = qiymat
let ism = "Aziz";
let yosh = 20;
let boy = 1.75;
let talaba = true;
let ranglar = ["qizil", "ko'k", "yashil"];

// Endi yorliq nomini yozing — quticha ichidagi qiymat qaytadi
console.log(ism);
console.log(yosh, "yosh,", boy, "metr");
console.log("Sevimli ranglar:", ranglar);
console.log("Talaba?", talaba);</code></pre>
<p><strong>Nima bo'ldi:</strong> 5 ta o'zgaruvchi yaratdingiz. Har biri — yorliq yopishtirilgan quticha. <code>console.log</code> qutichalarga qarab, ichidagi qiymatlarni ko'rsatadi. Brauzer xotirasi sizning komandangizni eslab qoldi.</p>

<h4>BLOKA 2 — Turlarni "ko'rish"</h4>
<p>Konsolda <code>typeof</code> komandasi har bir qiymatning turi nima ekanligini aytib beradi:</p>
<pre><code>console.log(typeof ism);      // "string"
console.log(typeof yosh);     // "number"
console.log(typeof talaba);   // "boolean"
console.log(typeof ranglar);  // "object"  (massiv ham object)
console.log(Array.isArray(ranglar));  // true — bu massiv</code></pre>
<p><strong>5 ta universal tur:</strong> string (matn), number (son), boolean (rost/yolg'on), array (ro'yxat), object (obyekt). Bu turlar deyarli har bir dasturlash tilida bor — Python, Java, Go, C++ — faqat nomi biroz boshqacha.</p>

<h4>BLOKA 3 — Tabriknoma robotini quramiz</h4>
<p>Foydalanuvchidan ma'lumot olamiz va shaxsiy javob qaytaramiz:</p>
<pre><code>let foydaIsm = prompt("Ismingizni kiriting:");
let foydaYosh = Number(prompt("Yoshingizni kiriting:"));
let keyingiYil = foydaYosh + 1;

if (foydaYosh >= 18) {
    alert(foydaIsm + ", siz voyaga yetgansiz! Kelgusi yil " + keyingiYil + " yoshda bo'lasiz.");
} else {
    let qolgan = 18 - foydaYosh;
    alert(foydaIsm + ", siz hali bolasiz. " + qolgan + " yildan keyin voyaga yetasiz.");
}</code></pre>
<p>3 ta qutichada uchta turli tur: <code>foydaIsm</code> — string, <code>foydaYosh</code> — number, <code>keyingiYil</code> — number. Kompyuter qiymatlarni eslab, ular bilan amallar bajarib, javob qurdi.</p>

<h3>🐛 Ataylab xato — eng mashhur "tuzoq"</h3>
<p>Quyidagi qatorlarni konsolga yopishtiring va natijaga qarang:</p>
<pre><code>let a = "5";    // matn — tirnoq ichida!
let b = 3;      // son
console.log(a + b);   // Nima chiqdi?</code></pre>
<p>Javob: <code>"53"</code> chiqdi, <code>8</code> emas. Sababi: <code>a</code> ichida matn ("5"), shuning uchun JavaScript <code>+</code> ni qo'shish emas — <strong>yopishtirish</strong> deb tushundi ("5" yoniga "3" yopishtirdi).</p>
<p><strong>Tuzatish:</strong> matnni avval songa aylantiring:</p>
<pre><code>console.log(Number(a) + b);   // 8 — endi to'g'ri qo'shildi</code></pre>
<p>Bu xato yangi boshlovchilarning №1 hayratlanish manbai. Endi siz uni biladigan birinchilardansiz.</p>

<h3>Endi tushuntiramiz — turlar nima uchun muhim</h3>

<h4>O'zgaruvchi = yorliqli quticha</h4>
<p>Kod yozayotganingizda, har bir qiymat (son, matn, ha/yo'q) xotirada qaerdadir saqlanadi. Siz <strong>yorliq</strong> yopishtirasiz — keyin shu yorliq bo'yicha qiymatga murojaat qilasiz.</p>
<pre><code>let yosh = 20;     // quticha yaratildi, yorliq yopishtirildi, ichida 20
yosh = 21;         // o'sha qutichaga endi 21 qo'yildi (qiymat o'zgardi)
yosh = yosh + 1;   // o'qing → 1 qo'shing → qaytarib qo'ying = 22</code></pre>

<h4>Dynamic vs Static — turni kim tekshiradi?</h4>
<table>
<tr><th>Til</th><th>Sintaksis</th><th>Qoida</th></tr>
<tr><td>JavaScript</td><td><code>let yosh = 20;</code></td><td>Tur avtomatik — dynamic</td></tr>
<tr><td>Python</td><td><code>yosh = 20</code></td><td>Tur avtomatik — dynamic</td></tr>
<tr><td>Java</td><td><code>int yosh = 20;</code></td><td>Tur oldindan e'lon — static</td></tr>
<tr><td>Go</td><td><code>var yosh int = 20</code></td><td>Static (yoki <code>:=</code> bilan auto)</td></tr>
</table>
<p><strong>Static</strong>: kompilator boshida turni biladi → xatoni dasturdan oldin tutadi. <strong>Dynamic</strong>: tezroq yoziladi, lekin xato faqat ishga tushganda chiqadi (yuqoridagi <code>"5" + 3</code> kabi).</p>

<h4>Nom qoidalari (deyarli har bir tilda bir xil)</h4>
<ul>
<li>✅ Harf yoki <code>_</code> bilan boshlanadi: <code>yosh</code>, <code>_temp</code></li>
<li>❌ Raqamdan boshlanmaydi: <code>1ism</code> — xato</li>
<li>❌ Bo'sh joy yo'q: <code>mening yoshim</code> — xato</li>
<li>❌ Tilning kalit so'zlari: <code>let</code>, <code>if</code>, <code>class</code> — ishlatilmaydi</li>
<li>✅ Tushunarli, ma'noli: <code>foydaYoshi</code> > <code>fY</code></li>
</ul>

<h4>Yaxshi nom — kelajakdagi sizga sovg'a</h4>
<p>"Kod bir marta yoziladi, lekin 100 marta o'qiladi" — tajribali dasturchilar qoidasi.</p>
<pre><code>// Yomon — 3 oydan keyin tushunmaysiz
let x = 25;
let y = x * 0.12;

// Yaxshi — bir qarashda aniq
let mahsulotNarxi = 25;
let soliqSummasi = mahsulotNarxi * 0.12;</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>O'zgaruvchi — qiymatni saqlash uchun yorliqli quticha</li>
<li>5 ta universal tur bor: string, number, boolean, array, object</li>
<li><code>typeof</code> bilan turini ko'rasiz</li>
<li><code>"5" + 3</code> = <code>"53"</code> — chunki matn bilan son qo'shilganda matnga aylanadi</li>
<li>Static til (Java, Go) turini oldindan biladi; dynamic til (JS, Python) — ish vaqtida aniqlaydi</li>
<li>Nom qoidalari va yaxshi nom = yaxshi kod</li>
</ul>
"""

L5_CODE = """\
// ═══ DARS 5 — KONSOLDA TUSHUNCHALARNI SINASH ═══
// about:blank → F12 → Console → pastdagilarni yopishtiring

// ─── BLOKA 1: Qutichalarga yorliq yopishtirish ───────
let ism = "Aziz";
let yosh = 20;
let boy = 1.75;
let talaba = true;
let ranglar = ["qizil", "ko'k", "yashil"];

console.log(ism);
console.log(yosh, "yosh,", boy, "metr");
console.log("Sevimli ranglar:", ranglar);

// ─── BLOKA 2: Turlarni ko'rish ───────────────────────
console.log(typeof ism);       // "string"
console.log(typeof yosh);      // "number"
console.log(typeof talaba);    // "boolean"
console.log(Array.isArray(ranglar));  // true

// ─── BLOKA 3: Interaktiv tabriknoma ──────────────────
let foydaIsm = prompt("Ismingiz?");
let foydaYosh = Number(prompt("Yoshingiz?"));
if (foydaYosh >= 18) {
    alert(foydaIsm + ", voyaga yetgansiz!");
} else {
    alert(foydaIsm + ", " + (18 - foydaYosh) + " yil qolgan.");
}

// ─── XATO TUZOG'I: matn + son = matn ─────────────────
let a = "5";
let b = 3;
console.log(a + b);          // "53" — yopishtirildi
console.log(Number(a) + b);  // 8 — to'g'ri qo'shildi

// ─── O'zgartirish mumkin (shuning uchun "o'zgaruvchi") ─
yosh = 21;
yosh = yosh + 1;   // 22
"""


# ═════════════════════════════════════════════════════════════════════════════
# L6 — Brauzer, tarmoq, veb
# ═════════════════════════════════════════════════════════════════════════════
L6_TEXT = """\
<h2>Brauzer, tarmoq va veb</h2>

<pre class="mermaid">
flowchart LR
    B["brauzer client"] -->|HTTP GET URL| S["server"]
    DNS["DNS lookup"] -->|domain ni IP ga| B
    S -->|HTML CSS JS| B
    B --> R["sahifani ko'rsatadi"]
    B -.->|click form| S
</pre>

<p>Internet aslida juda sodda g'oyaga asoslangan: <strong>siz so'rov yuborasiz, server javob qaytaradi</strong>. Brauzer (Chrome, Firefox, Safari) — siz va server o'rtasidagi vositachi.</p>

<h3>Sodda misol — google.com ga kirish</h3>
<ol>
<li>Siz <code>google.com</code> deb yozasiz</li>
<li>Brauzer "google.com qayerda?" deb DNS server'ga so'raydi</li>
<li>DNS javob qaytaradi: "google.com = 142.250.180.46" (IP manzil)</li>
<li>Brauzer 142.250.180.46 ga HTTP so'rov yuboradi: "menga / sahifasini ber"</li>
<li>Google server HTML, CSS, JavaScript ni qaytaradi</li>
<li>Brauzer ularni o'qib, sizga sahifa ko'rsatadi</li>
</ol>
<p>Bularning hammasi 0.3 sekundda bo'ladi!</p>

<h3>URL anatomiyasi</h3>
<pre><code>https://www.example.com:443/blog/post-1?id=42&amp;source=email#section-2
  ↑         ↑           ↑    ↑              ↑               ↑
protokol   domain      port  path           query          fragment</code></pre>
<ul>
<li><strong>Protokol</strong>: <code>http://</code> (oddiy) yoki <code>https://</code> (xavfsiz, shifrlangan)</li>
<li><strong>Domain</strong>: server nomi</li>
<li><strong>Port</strong>: server qaysi "eshik"da kutmoqda (HTTP — 80, HTTPS — 443)</li>
<li><strong>Path</strong>: server ichidagi resurs yo'li</li>
<li><strong>Query</strong>: qo'shimcha parametrlar (key=value)</li>
<li><strong>Fragment</strong>: sahifaning bir qismi (anchor)</li>
</ul>

<h3>HTTP — internetning tili</h3>
<p>Brauzer va server <strong>HTTP</strong> (HyperText Transfer Protocol) orqali muloqot qiladi. Asosiy "fe'llari":</p>
<table>
<tr><th>Method</th><th>Ma'no</th><th>Misol</th></tr>
<tr><td><code>GET</code></td><td>"Menga ber"</td><td>Sahifani yuklash</td></tr>
<tr><td><code>POST</code></td><td>"Menga yangi yarating"</td><td>Forma yuborish</td></tr>
<tr><td><code>PUT</code></td><td>"Buni yangilang"</td><td>Profilingizni o'zgartirish</td></tr>
<tr><td><code>DELETE</code></td><td>"Buni o'chirib tashlang"</td><td>Postingizni o'chirish</td></tr>
</table>

<h3>HTTP status kodlari</h3>
<ul>
<li><strong>200 OK</strong> — hammasi yaxshi</li>
<li><strong>301 Redirect</strong> — manzil o'zgargan, boshqa joyga o'ting</li>
<li><strong>404 Not Found</strong> — resurs topilmadi (eng mashhur xato)</li>
<li><strong>500 Server Error</strong> — serverda xato</li>
<li><strong>403 Forbidden</strong> — sizga ruxsat yo'q</li>
</ul>

<h3>Sahifaning 3 qismi</h3>
<p>Har bir veb-sahifa 3 ta texnologiyadan iborat:</p>
<ul>
<li>📄 <strong>HTML</strong> — struktura (sarlavhalar, paragraflar, tugmalar)</li>
<li>🎨 <strong>CSS</strong> — dizayn (ranglar, shriftlar, joylashuv)</li>
<li>⚡ <strong>JavaScript</strong> — interaktivlik (click qilganda nima bo'ladi)</li>
</ul>
<p>HTML — kostyum. CSS — kiyimning rangi va shakli. JavaScript — odam — harakat qiladi.</p>

<h3>Frontend vs Backend</h3>
<table>
<tr><th></th><th>Frontend (mijoz)</th><th>Backend (server)</th></tr>
<tr><td>Qayerda</td><td>Sizning brauzeringizda</td><td>Uzoq serverda</td></tr>
<tr><td>Til</td><td>HTML, CSS, JavaScript</td><td>Python, Java, Go, Node.js, PHP</td></tr>
<tr><td>Ma'lumot</td><td>Hozir ko'rinayotgan ma'lumot</td><td>Baza, autentifikatsiya, logika</td></tr>
<tr><td>Misol</td><td>Tugma, forma, animatsiya</td><td>Login tekshirish, postlarni saqlash</td></tr>
</table>

<h3>DevTools — har dasturchining do'sti</h3>
<p>Har brauzerda <strong>Developer Tools</strong> bor. F12 yoki Cmd+Option+I bilan oching:</p>
<ul>
<li><strong>Elements</strong> — HTML va CSS ni ko'rish va o'zgartirish</li>
<li><strong>Console</strong> — JavaScript komandalarni yozish va xatolarni ko'rish</li>
<li><strong>Network</strong> — har so'rov va javobni ko'rish</li>
<li><strong>Application</strong> — saqlangan ma'lumotlar (cookies, localStorage)</li>
</ul>
"""

L6_CODE = """\
# Brauzer DevTools — Console da yozib sinab ko'ring!

# F12 bosing → Console tabini oching → quyidagi qatorlarni yozing:

# JavaScript Console misollari:
# alert("Salom, dunyo!");
# console.log("Bu konsolga chiqadi");
# document.title    // sahifaning nomi
# location.href     // joriy URL
# document.body.style.background = "lightblue"   // fonni ko'k qiling!

# Network tab da har resursni ko'rishingiz mumkin:
#   Status (200 OK?)
#   Type (HTML, CSS, JS, image)
#   Size va Time

# ─── HTTP so'rov yuborish — Python bilan ────────────
import urllib.request

with urllib.request.urlopen("https://api.github.com") as response:
    print("Status:", response.status)
    print("Server:", response.headers.get("Server"))
    # data = response.read()
    # print(data[:200])
"""



# ═════════════════════════════════════════════════════════════════════════════
# L7 — Terminal va Git
# ═════════════════════════════════════════════════════════════════════════════
L7_TEXT = """\
<h2>Terminal va Git — boshlovchilar uchun</h2>

<pre class="mermaid">
flowchart LR
    T["terminal"] -->|cd ls mkdir| FS["fayl tizim"]
    T -->|git init| REPO["local repo"]
    REPO -->|git add commit| STAGE["staged"]
    STAGE -->|git push| GH["GitHub remote"]
    GH --> WORLD["dunyo ko'radi"]
</pre>

<p>Ikki vosita har dasturchining doimiy hamrohi: <strong>terminal</strong> (matn orqali kompyuter bilan muloqot) va <strong>Git</strong> (kod tarixini saqlash). Bularni o'rganmasdan haqiqiy dasturchi bo'lib bo'lmaydi.</p>

<h3>Terminal nima?</h3>
<p>Terminal — bu kompyuter bilan <strong>matn orqali</strong> muloqot qilish usuli. Tugmalar va sichqoncha o'rniga — komandalar yozasiz. Birinchi qarashda qiyin, lekin tezroq va kuchliroq.</p>
<ul>
<li><strong>Linux/macOS</strong>: Terminal ilovasi (avval o'rnatilgan)</li>
<li><strong>Windows</strong>: PowerShell yoki Windows Terminal (yangi)</li>
</ul>

<h3>Eng muhim 10 ta komanda</h3>
<table>
<tr><th>Komanda</th><th>Vazifasi</th><th>Misol</th></tr>
<tr><td><code>pwd</code></td><td>Hozir qayerdaman?</td><td><code>pwd</code> → <code>/home/aziz</code></td></tr>
<tr><td><code>ls</code></td><td>Papkadagi fayllarni ko'rsat</td><td><code>ls -lah</code></td></tr>
<tr><td><code>cd</code></td><td>Boshqa papkaga o't</td><td><code>cd Documents</code></td></tr>
<tr><td><code>cd ..</code></td><td>Yuqori papkaga</td><td><code>cd ..</code></td></tr>
<tr><td><code>mkdir</code></td><td>Yangi papka yarat</td><td><code>mkdir loyiha</code></td></tr>
<tr><td><code>touch</code></td><td>Bo'sh fayl yarat</td><td><code>touch index.html</code></td></tr>
<tr><td><code>cat</code></td><td>Fayl ichini ko'rsat</td><td><code>cat README.md</code></td></tr>
<tr><td><code>rm</code></td><td>Faylni o'chir</td><td><code>rm old.txt</code></td></tr>
<tr><td><code>cp</code></td><td>Nusxa olish</td><td><code>cp a.txt b.txt</code></td></tr>
<tr><td><code>mv</code></td><td>Ko'chirish / nomini o'zgartirish</td><td><code>mv old new</code></td></tr>
</table>
<p><strong>Maslahat</strong>: <code>Tab</code> tugmasini bosib avtotugatishdan foydalaning. <code>cd Doc</code> + Tab → <code>cd Documents/</code>.</p>

<h3>Git — nima va nima uchun?</h3>
<p><strong>Git</strong> — bu kodingizning <strong>vaqt mashinasi</strong>. Har o'zgarishni saqlaydi, kerak bo'lsa ortga qaytarish mumkin. Jamoa bilan ishlashda — ajralmas.</p>
<p>Tasavvur qiling: 200 qator yozdingiz, hammasini buzdingiz, ortga qaytmoqchisiz. Git'siz — yo'q. Git bilan — bitta komanda.</p>

<h3>Git ish jarayoni — 4 qadam</h3>
<ol>
<li><strong>Edit</strong>: faylni o'zgartirasiz (yangi qator yozasiz)</li>
<li><strong>Add</strong>: o'zgarishlarni "staging" ga qo'shasiz (<code>git add</code>)</li>
<li><strong>Commit</strong>: snapshot saqlaysiz xabar bilan (<code>git commit -m "..."</code>)</li>
<li><strong>Push</strong>: serverga yuborasiz (<code>git push</code>)</li>
</ol>

<h3>Eng muhim Git komandalari</h3>
<pre><code># Yangi loyiha boshlash
git init

# Holatni ko'rish (nima o'zgargan)
git status

# Yangi fayllarni qo'shish
git add .                    # hammasini
git add index.html           # bittasini

# Snapshot saqlash
git commit -m "Birinchi sahifa"

# Tarixni ko'rish
git log --oneline

# GitHub ga yuborish
git push origin main</code></pre>

<h3>GitHub — Git uchun "ijtimoiy tarmoq"</h3>
<p><strong>GitHub</strong> — bu sizning kodingizni saqlash va boshqalar bilan ulashish uchun platforma. Hozir har dasturchi GitHub'da hisobga ega bo'lishi shart — bu sizning <em>portfoliyo</em>ngiz.</p>
<ul>
<li>Bepul hisob: <a href="https://github.com">github.com</a></li>
<li>Loyihalaringizni yuklang — kelajakdagi ish beruvchilar ko'radi</li>
<li>Boshqalar kodini o'qing — bu ham o'rganish</li>
<li><strong>GitHub Pages</strong> — bepul vebsite hosting (keyingi darsda ishlatamiz)</li>
</ul>

<h3>Birinchi marta sozlash</h3>
<pre><code>git config --global user.name "Sizning Ismingiz"
git config --global user.email "siz@example.com"

# Tekshirish
git config --list</code></pre>
<p>Bu komandalar git'ga sizning kim ekanligingizni aytadi — har commit shu ism bilan saqlanadi.</p>

<h3>.gitignore — Git ga nimani saqlamaslikni aytish</h3>
<p>Ba'zi fayllar git'da bo'lmasligi kerak: parollar, katta video fayllar, build natijalari.</p>
<pre><code># .gitignore fayli
.env                # parollar
node_modules/       # JavaScript paketlar
__pycache__/        # Python keshi
*.log               # log fayllar</code></pre>

<h3>Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong><code>git push</code> rad etiladi</strong>: remote'da yangi commit bor. Avval <code>git pull</code> qiling.</li>
<li><strong><code>git commit</code> ishlamaydi</strong>: <code>git add</code> qilmagansiz</li>
<li><strong>Parolingizni so'raydi</strong>: GitHub endi parol qabul qilmaydi. <a href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens">Personal Access Token</a> ishlatish kerak.</li>
</ul>
"""

L7_CODE = """\
# Terminal + Git — birinchi loyiha yaratish

# ─── Terminal komandalari ───────────────────────
# Yangi papka yaratish va kirish
mkdir mening-birinchi-saytim
cd mening-birinchi-saytim

# Fayl yaratish
touch index.html
touch README.md

# Faylni o'zgartirish (nano yoki sizning muharriringiz)
# nano index.html

# Papkadagi fayllarni ko'rish
ls -lah


# ─── Git boshlash ───────────────────────────────
# Birinchi marta — git ni sozlash (bir marta qilinadi)
git config --global user.name "Sizning Ismingiz"
git config --global user.email "siz@example.com"

# Yangi loyiha — git tarixini boshlash
git init

# Holat
git status

# Hamma fayllarni qo'shish
git add .

# Snapshot saqlash
git commit -m "Birinchi commit: bo'sh sahifa"

# Tarix
git log --oneline


# ─── GitHub ga yuborish ─────────────────────────
# 1. github.com da yangi (bo'sh) repo yarating
# 2. URL ni nusxa oling
# 3. Local repo'ga remote sifatida qo'shing:

git remote add origin https://github.com/SIZNING-USERNAME/mening-birinchi-saytim.git

# Yuborish
git branch -M main
git push -u origin main

# Tabriklayman! Sizning kodingiz endi GitHub'da.
"""


# ═════════════════════════════════════════════════════════════════════════════
# L8 — Birinchi publik sahifa (CAPSTONE)
# ═════════════════════════════════════════════════════════════════════════════
L8_TEXT = """\
<h2>🚀 Birinchi publik sahifa — CAPSTONE</h2>

<pre class="mermaid">
flowchart LR
    F["index.html"] --> R["git repo"]
    R -->|git push| GH["GitHub"]
    GH -->|Pages enabled| URL["yourname.github.io"]
    URL --> WORLD["publik URL"]
    YOU["siz"] -.->|share link| FR["do'stlar ish beruvchilar"]
</pre>

<p>Mana, kursning yakuniy darsi. Endi biz hammasini birga ishlatamiz: HTML (struktura), Git (saqlash), GitHub (uzoq saqlash) va <strong>GitHub Pages</strong> (bepul hosting). 30 daqiqada — sizning birinchi sahifangiz internetda yashaydi.</p>

<h3>GitHub Pages nima?</h3>
<p>GitHub Pages — bu bepul vebsite hosting xizmati. Repo ichidagi HTML/CSS/JS fayllarni avtomatik publik URL ga joylashtiradi. Format: <code>yourusername.github.io/repo-nomi</code>.</p>
<p>Bu — talabalar uchun <strong>oltin</strong>: hech qanday hosting to'lovi yo'q, oddiy, ishonchli. Real veb-saytlar GitHub Pages'da joylashgan: jamoa loyihalari, blog, dokumentatsiya.</p>

<h3>4 qadam — internetga chiqish</h3>

<h4>1️⃣ HTML sahifani yarating</h4>
<p>Oddiy "About me" sahifasini yozing. Ko'p narsa kerak emas — sodda va aniq.</p>
<pre><code>&lt;!DOCTYPE html&gt;
&lt;html lang="uz"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;title&gt;Aziz Karimov — Frontend talabasi&lt;/title&gt;
    &lt;style&gt;
        body {
            font-family: sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
        }
        h1 { color: #6c5ce7; }
        a { color: #6c5ce7; }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Salom, men Aziz! 👋&lt;/h1&gt;
    &lt;p&gt;Men 20 yoshli talaba va dasturlashni o'rganmoqdaman.&lt;/p&gt;
    &lt;h2&gt;Hozir o'rganayotganlarim&lt;/h2&gt;
    &lt;ul&gt;
        &lt;li&gt;HTML va CSS&lt;/li&gt;
        &lt;li&gt;JavaScript&lt;/li&gt;
        &lt;li&gt;Python&lt;/li&gt;
    &lt;/ul&gt;
    &lt;h2&gt;Aloqa&lt;/h2&gt;
    &lt;p&gt;Telegram: &lt;a href="https://t.me/aziz"&gt;@aziz&lt;/a&gt;&lt;/p&gt;
    &lt;p&gt;GitHub: &lt;a href="https://github.com/aziz"&gt;github.com/aziz&lt;/a&gt;&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>

<h4>2️⃣ Git va GitHub'ga joylash</h4>
<pre><code># Loyiha papkasi ichida
git init
git add .
git commit -m "Birinchi sahifa: about me"

# GitHub'da yangi repo yarating: about-me yoki yourname.github.io
# Keyin local ni unga ulang:
git remote add origin https://github.com/USERNAME/about-me.git
git branch -M main
git push -u origin main</code></pre>

<h4>3️⃣ GitHub Pages ni yoqing</h4>
<ol>
<li>GitHub'da repo sahifasiga kiring</li>
<li><strong>Settings</strong> → <strong>Pages</strong> bo'limi</li>
<li>"Branch" ni <code>main</code> ga qo'ying va Save</li>
<li>1-2 daqiqa kuting</li>
</ol>

<h4>4️⃣ URL ni oling va ulashing!</h4>
<p>Settings → Pages'da yashil tasma paydo bo'ladi: "Your site is live at <strong>https://USERNAME.github.io/about-me/</strong>"</p>
<p>Bu — sizning sahifangiz. Telegram'da ulashing. Resume'ga qo'shing. Birinchi haqiqiy onlayn izingiz.</p>

<h3>Maxsus repo: <code>USERNAME.github.io</code></h3>
<p>Agar repo nomingizni aynan <code>SIZNING-USERNAME.github.io</code> qilsangiz, URL <code>https://SIZNING-USERNAME.github.io/</code> bo'ladi — bu sizning "asosiy" sahifangiz. Tavsiya etamiz.</p>

<h3>Keyingi qadam — qaysi kursni tanlay?</h3>
<p>Tabriklaymiz! Siz dasturlash dunyosiga kirdingiz. Endi yo'lni tanlash vaqti:</p>
<table>
<tr><th>Agar siz ...</th><th>Keyingi kurs</th></tr>
<tr><td>Vizual natija va veb-saytlarni sevsangiz</td><td>📘 <strong>HTML CSS</strong> kursi</td></tr>
<tr><td>Saytlarni jonlantirmoqchi bo'lsangiz</td><td>📗 <strong>Javascript</strong> kursi</td></tr>
<tr><td>Keng imkoniyatlarni va AI'ni xohlasangiz</td><td>📕 <strong>Python Asoslari</strong></td></tr>
<tr><td>Python'ni bilsangiz va veb-ilovalar quring</td><td>📓 <strong>Python Flask</strong></td></tr>
</table>

<h3>3 ta yakuniy maslahat</h3>
<ol>
<li><strong>Har kuni 30 daqiqa</strong> — haftada 3 soatdan ko'ra yaxshi</li>
<li><strong>Loyiha quring</strong> — faqat o'qish — yetarli emas. Yozish, buzish, qayta qurish</li>
<li><strong>Sabr qiling</strong> — birinchi 3 oy — eng qiyin. Keyin oson bo'lib boradi</li>
</ol>
<p>Yo'lda omad! Endi haqiqiy o'rganish boshlanadi. 🚀</p>
"""

L8_CODE = """\
<!-- index.html — sizning birinchi sahifangiz -->
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aziz Karimov — About Me</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 640px;
            margin: 40px auto;
            padding: 0 20px;
            color: #1a1a2e;
            line-height: 1.6;
            background: #fafafd;
        }
        header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid #e1e3ee;
        }
        h1 {
            color: #6c5ce7;
            font-size: 2.5em;
            margin: 0;
        }
        h2 {
            color: #2d3148;
            margin-top: 2em;
            padding-bottom: 8px;
            border-bottom: 2px solid #6c5ce7;
        }
        .avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #6c5ce7, #a29bfe);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            color: white;
        }
        a { color: #6c5ce7; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul { line-height: 2; }
        footer {
            text-align: center;
            margin-top: 60px;
            padding: 20px;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <header>
        <div class="avatar">👋</div>
        <h1>Salom, men Aziz!</h1>
        <p>20 yoshli talaba · dasturlash o'rganmoqdaman</p>
    </header>

    <h2>Hozir o'rganayotganlarim</h2>
    <ul>
        <li>HTML va CSS — sahifa qurishni</li>
        <li>JavaScript — saytni jonlantirishni</li>
        <li>Python — universal til</li>
    </ul>

    <h2>Yoqtirgan loyihalarim</h2>
    <ul>
        <li><a href="#">Tashrif kartasi — birinchi sahifam</a></li>
        <li><a href="#">Kalkulyator (JavaScript)</a></li>
    </ul>

    <h2>Aloqa</h2>
    <p>📨 Telegram: <a href="https://t.me/aziz">@aziz</a></p>
    <p>💼 GitHub: <a href="https://github.com/aziz">github.com/aziz</a></p>
    <p>📧 Email: aziz@example.com</p>

    <footer>
        Yaratildi 💜 bilan, hosting: GitHub Pages
    </footer>
</body>
</html>
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
# Per-lesson project tasks
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {
        "title": "Algoritm sifatida — kunlik rejim",
        "description": (
            "Kompyuter kabi fikrlash uchun: 1 ta kunlik amaliyotingizni (masalan, "
            "ertalabki rejim, choy damlash, ishga borish) raqamlangan, aniq qadamlar "
            "ko'rinishida yozing. Hech qanday dasturlash tili kerak emas — toza tilda."
        ),
        "requirements": (
            "• Kamida 8 ta qadam, raqamlangan\n"
            "• Kamida 1 ta shart bo'lishi kerak (\"agar ... bo'lsa\")\n"
            "• Kamida 1 ta takror bo'lishi kerak (\"barcha X uchun\")\n"
            "• Markdown yoki oddiy matn (README.md yoki .txt)\n"
            "• Faylning boshida sarlavha va qisqa tavsif"
        ),
        "technologies": "Hech qanday — toza fikrlash",
        "deadline_days": 2,
    },
    1: {
        "title": "Mening yo'lim — qaysi tilni tanlayman?",
        "description": (
            "1 sahifali yozma asar: qaysi dasturlash tilini birinchi o'rganishni "
            "tanlaganingizni va NIMA UCHUN. Bu kursdagi til xaritasiga (web/mobile/AI/...) "
            "qarab tanlang. Kamida 3 ta sabab keltiring."
        ),
        "requirements": (
            "• 300-500 so'z (judha qisqa ham, juda uzun ham emas)\n"
            "• Tanlangan til + uning oilasi (frontend/backend/AI/...)\n"
            "• Kamida 3 ta aniq sabab\n"
            "• Kamida 1 ta haqiqiy loyiha misoli (siz qurmoqchi bo'lgan narsa)\n"
            "• 6 oydan keyingi maqsadingiz\n"
            "• Markdown formatda (README.md)"
        ),
        "technologies": "Markdown",
        "deadline_days": 3,
    },
    2: {
        "title": "Mening kompyuterim — texnik ma'lumotlar",
        "description": (
            "Kompyuteringizning texnik xususiyatlarini hujjatlashtiring. Terminal "
            "yoki System Info ishlatib quyidagi ma'lumotlarni toping va saqlang."
        ),
        "requirements": (
            "• OS nomi va versiyasi (Windows 11, macOS Sonoma, Ubuntu 22.04 ...)\n"
            "• CPU modeli va yadrolar soni\n"
            "• RAM hajmi (GB)\n"
            "• Disk umumiy va bo'sh hajmi\n"
            "• Internet tezligi (speedtest.net)\n"
            "• Brauzeringiz va uning versiyasi\n"
            "• Hammasi README.md yoki Notion sahifasida"
        ),
        "technologies": "Terminal, System Info, speedtest",
        "deadline_days": 2,
    },
    3: {
        "title": "Algoritm flowchart — diagramma chizish",
        "description": (
            "Bitta kundalik vazifani (masalan, oziq-ovqat sotib olish, transport "
            "tanlash, parol o'rnatish) flowchart shaklida chizing. Kamida 1 ta shart "
            "(romb) va 1 ta takror (sikl) bo'lishi shart."
        ),
        "requirements": (
            "• Vositalardan biri: draw.io, Miro, Whimsical, qog'oz+rasm\n"
            "• Boshlanish va tugash ovallari\n"
            "• Kamida 4 ta to'rtburchak (amal)\n"
            "• Kamida 1 ta romb (shart)\n"
            "• Kamida 1 ta sikl (qaytib keluvchi strelka)\n"
            "• Yakuniy rasm — PNG, JPG yoki PDF — repo'ga yuklang\n"
            "• README'da algoritmni 3-4 jumlada izoh bering"
        ),
        "technologies": "draw.io / Miro / Whimsical / qog'oz",
        "deadline_days": 3,
    },
    4: {
        "title": "Pseudo-kod daftarchasi",
        "description": (
            "5 ta mini-vazifani pseudo-kodda yozing. Hech qanday real tilni ishlatmang — "
            "shunchaki aniq, mantiqiy qadamlar. Maqsad: algoritmni \"o'ylash\" mashqlari."
        ),
        "requirements": (
            "• 5 ta vazifa har biri uchun pseudo-kod yozilgan:\n"
            "  1. Foydalanuvchi ismidagi harflar sonini hisoblash\n"
            "  2. Ikki sondan kattasini topish\n"
            "  3. 1 dan 100 gacha sonlar yig'indisi\n"
            "  4. Ro'yxatda eng katta sonni topish\n"
            "  5. Sonning juft yoki toq ekanligini aniqlash\n"
            "• Har vazifa uchun o'zgaruvchilar, shart, sikl ishlatilgan\n"
            "• Markdown formatda README.md\n"
            "• Har vazifaning yonida 1 jumla izoh"
        ),
        "technologies": "Pseudo-kod, Markdown",
        "deadline_days": 4,
    },
    5: {
        "title": "Veb-sayt tahlilchisi (DevTools)",
        "description": (
            "3 ta mashhur veb-saytni DevTools orqali tekshiring va screenshotlar bilan "
            "hujjatlashtiring. Maqsad: brauzer ichkarisini ko'rish."
        ),
        "requirements": (
            "• 3 ta sayt tanlang (masalan: google.com, wikipedia.org, github.com)\n"
            "• Har sayt uchun F12 oching\n"
            "• Elements tab — HTML strukturasi screenshot\n"
            "• Network tab — sahifa yuklash davomida har resurs screenshot\n"
            "• Console — bitta JavaScript komanda yozib natija ko'rsating\n"
            "• Har sayt uchun 3 ta ajoyib topganlaringizni yozing\n"
            "• Markdown + rasmlar repo'da"
        ),
        "technologies": "Brauzer DevTools, Markdown",
        "deadline_days": 3,
    },
    6: {
        "title": "Birinchi GitHub repo",
        "description": (
            "Bu — eng muhim qadam: GitHub'da hisob yarating, local'da git ishga "
            "tushiring va birinchi repongizni yuklang. Bu sizning kelajakdagi portfoliongizning "
            "asosi."
        ),
        "requirements": (
            "• github.com da hisob yarating (ism familiyangizga yaqin username tanlang)\n"
            "• git config bilan ism va emailingizni o'rnating\n"
            "• Local da yangi loyiha papkasi yarating\n"
            "• README.md yozing: kim siz, nima o'rganmoqdasiz, ulanish ma'lumotlari\n"
            "• git init, git add, git commit ishlatilgan\n"
            "• GitHub repo yaratilgan va kod push qilingan\n"
            "• README chiroyli formatda (markdown sintaksisi ishlatilgan)\n"
            "• Repo URL ni topshiring"
        ),
        "technologies": "Git, GitHub, Markdown, terminal",
        "deadline_days": 3,
    },
    7: {
        "title": "🚀 CAPSTONE: Birinchi publik sahifa (GitHub Pages)",
        "description": (
            "Kursning yakuniy loyihasi. Sizning birinchi \"About me\" sahifangiz "
            "internetda yashasin. Bu sahifa kelajakdagi ish beruvchilar ko'radigan "
            "birinchi izingiz bo'ladi."
        ),
        "requirements": (
            "• To'liq ishlaydigan index.html (HTML + inline yoki external CSS)\n"
            "• Sahifa ichida: avatar/emoji, ism, qisqa tavsif, qiziqishlar, aloqa ma'lumotlari\n"
            "• Hech bo'lmasa 3 ta link (GitHub, Telegram, Email)\n"
            "• Mobile-friendly (viewport meta + responsive padding)\n"
            "• Mavzuli ranglar va shriftlar (kamida 2 rang)\n"
            "• Repo nomi: <username>.github.io yoki about-me\n"
            "• GitHub Pages yoqilgan\n"
            "• Yashil tasma: \"Your site is live at https://...\"\n"
            "• URL ni README'da va topshirishda ko'rsating\n"
            "• Bonus: dark mode toggle (JavaScript bilan)"
        ),
        "technologies": "HTML, CSS, Git, GitHub, GitHub Pages",
        "deadline_days": 5,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {
        "order": 0, "title": "1-Dasturlash nima va qayerda yashaydi",
        "text": L1_TEXT, "code": L1_CODE, "lang": "javascript",
        "video": "https://youtu.be/zOjov-2OZ0E",
        "exercises": [
            mc("Brauzerda F12 tugmasi nima qiladi?",
               ["Saytni yopadi",
                "DevTools panelini ochadi",
                "Yangi sayt ochadi",
                "Kompyuterni qayta yoqadi"],
               "B",
               hint="F12 — dasturchilar uchun yashirin oyna.",
               explanation="F12 (Mac uchun Option+Cmd+I) brauzer ichidagi DevTools panelini ochadi. Console yorlig'i orqali siz JavaScript kod yoza olasiz.",
               diff="Easy", pts=2),
            mc("Konsolda alert(\"Salom\") yozsangiz nima bo'ladi?",
               ["Sayt o'chadi",
                "Ekranda \"Salom\" matnli xabar oynasi paydo bo'ladi",
                "Email yuboriladi",
                "Hech narsa — xato beradi"],
               "B",
               explanation="alert() — JavaScript ning eng oddiy buyrug'i. Foydalanuvchiga modal oyna chiqaradi.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari konsolda haqiqatda ishlaydi?",
               ["alert(\"salom\")",
                "console.log(2 + 2)",
                "document.body.style.background = \"red\"",
                "Alert(\"salom\")",
                "Console.Log(\"salom\")"],
               "A,B,C", multi=True,
               hint="JavaScript case-sensitive — katta harf bilan boshlangani ishlamaydi.",
               explanation="JavaScript da alert va console.log kichik harflar bilan yoziladi. Alert va Console.Log — noma'lum identifikatorlar, ReferenceError beradi.",
               diff="Medium", pts=3),
            dd("Kod ishga tushish zanjirini to'g'ri tartibda joylang",
               ["Siz kod yozasiz (alert salom)",
                "Brauzer ichidagi JavaScript interpreter kodni o'qiydi",
                "Interpreter kodni mashina signallariga aylantiradi",
                "CPU signallarni bajaradi",
                "Siz natijani ekranda ko'rasiz"],
               hint="Code → Interpreter → CPU → Natija. Hero diagrammasiga qarang.",
               diff="Medium", pts=3),
            ti("Algoritm va kod orasida qanday farq bor?",
               "Algoritm — bu tartibli qadamlar ro'yxati. U til-erkin: choy damlash retsepti, "
               "kunlik rejim ham algoritm. Kod esa — algoritmni biror dasturlash tilida "
               "(Python, JavaScript, C va boshqalar) yozish. Bitta algoritmni 10 ta turli "
               "tilda yozish mumkin — algoritm bir xil bo'lib qoladi. Kod algoritmsiz "
               "yozilmaydi: avval algoritmni o'ylab topish, keyin uni kodga aylantirish kerak.",
               hint="Algoritm — bu fikr; kod — bu fikrning yozma shakli.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 1, "title": "2-Qaysi tilni o'rganay?",
        "text": L2_TEXT, "code": L2_CODE, "lang": "javascript",
        "video": "https://youtu.be/Q8eHsRZ81bI",
        "exercises": [
            mc("Brauzer manzil satrida data:text/html,<h1>Salom</h1> yozsangiz nima bo'ladi?",
               ["Brauzer xato beradi",
                "Sahifada \"Salom\" sarlavhasi ko'rinadi",
                "HTML fayl yuklab olinadi",
                "Console paneli ochiladi"],
               "B",
               hint="data: sxemasi brauzerga \"matn HTML deb tushun\" deydi — fayl ham, server ham kerak emas.",
               explanation="data:text/html,... brauzerga inline HTML ni darhol render qilishga buyuradi. Bu — server va fayl yaratmasdan HTML sinab ko'rish usuli.",
               diff="Easy", pts=2),
            mc("AI / ChatGPT kabi loyihalar uchun eng keng ishlatiladigan til qaysi?",
               ["JavaScript", "Python", "Swift", "C"],
               "B",
               explanation="PyTorch, TensorFlow, scikit-learn — barcha mashhur AI/ML kutubxonalari Python uchun yozilgan.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari brauzeringizda HECH NARSA o'rnatmay ishlay oladi?",
               ["JavaScript (F12 → Console)",
                "HTML (data: URL yoki .html fayl)",
                "Python (python.org/shell — onlayn)",
                "Swift (iPhone uchun)",
                "C / C++"],
               "A,B,C", multi=True,
               hint="Swift va C ni ishlatish uchun maxsus dasturlar o'rnatish kerak. Birinchi 3 ta — brauzeringizdan ishlaydi.",
               explanation="JavaScript brauzerda allaqachon bor. HTML faylsiz ham data: URL orqali ishlaydi. Python esa python.org/shell onlayn interpreter beradi. Swift va C — kompilyator / IDE talab qiladi.",
               diff="Medium", pts=3),
            dd("Til tanlash jarayonini to'g'ri tartibda joylang",
               ["Loyihangizning maqsadini aniqlang (nima qurmoqchisiz)",
                "Sohani tanlang (web, mobile, AI, o'yin, tizim)",
                "Tegishli tillar ro'yxatini ko'rib chiqing",
                "Bittasini tanlang va boshlang",
                "30 kun ichida asoslarni o'rganing"],
               hint="Til — bu asbob. Avval nima qurish kerakligini bilish, keyin asbob tanlash.",
               explanation="Eng katta xato — \"qaysi til eng yaxshi?\" deb so'rash. To'g'ri savol: \"nima qurmoqchiman?\". Maqsad → soha → tilning oilasi → aniq til.",
               diff="Medium", pts=3),
            ti("Nima uchun bitta til hammasini hal qila olmaydi?",
               "Har bir dasturlash tili muayyan vazifa va kontekst uchun yaratilgan. C — "
               "tezlik va past darajadagi nazorat uchun. Python — sodda sintaksis va ilmiy "
               "hisob-kitoblar uchun. JavaScript — brauzer uchun (faqat brauzer bilan ishlovchi til). "
               "Swift — Apple ekotizimi uchun. Bitta til hammasini hal qilishga harakat qilsa, "
               "u har vazifada o'rtacha bo'ladi — hech narsada eng yaxshi emas. Shuning uchun "
               "tajribali dasturchilar 3-5 ta tilni biladi va har birini o'z joyida ishlatadi.",
               hint="Bolg'a bilan o'tin yorish mumkin, lekin tikuv mashinasi uchun u ishlamaydi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 2, "title": "3-Kompyuter qisqacha (CPU, RAM, disk, OS)",
        "text": L3_TEXT, "code": L3_CODE, "lang": "javascript",
        "video": "https://youtu.be/8YBpgKHU7HM",
        "exercises": [
            mc("Brauzer konsolida navigator.hardwareConcurrency nima qaytaradi?",
               ["Brauzer versiyasi",
                "CPU yadrolar (core) soni",
                "Internet tezligi",
                "RAM hajmi GB da"],
               "B",
               hint="\"hardware\" + \"concurrency\" (parallellik) — kompyuteringiz nechta amalni bir vaqtda bajara olishi.",
               explanation="navigator.hardwareConcurrency CPU dagi mantiqiy yadrolar sonini qaytaradi. Ko'p yadro = ko'p parallel ish.",
               diff="Easy", pts=2),
            mc("RAM va Disk orasidagi asosiy farq qaysi?",
               ["RAM tez lekin vaqtinchalik, Disk sekin lekin doimiy",
                "RAM doimiy, Disk vaqtinchalik",
                "Hech qanday farq yo'q",
                "RAM faqat Windows uchun"],
               "A",
               hint="Brauzerda localStorage Disk kabi (saqlanib qoladi), oddiy o'zgaruvchi RAM kabi (sahifa yangilansa yo'qoladi) — siz buni darsda sinab ko'rdingiz.",
               explanation="RAM — vaqtinchalik tez xotira (elektr o'chsa yo'qoladi). Disk (SSD/HDD) — sekinroq lekin doimiy. Kod o'zgaruvchilari RAM da, fayllar Disk da.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari sahifa yangilanganda saqlanib qoladi?",
               ["localStorage.setItem(\"x\", \"5\")",
                "sessionStorage.setItem(\"y\", \"10\")",
                "let z = 5",
                "document.cookie qiymati",
                "console.log(...) chiqishi"],
               "A,D", multi=True,
               hint="localStorage va cookie — disk kabi doimiy. sessionStorage — yorliq yopilguncha. let — oddiy o'zgaruvchi, sahifa yangilansa yo'q bo'ladi.",
               explanation="localStorage va cookie diskda saqlanadi — sahifa yangilansa yoki brauzer o'chsa ham qoladi. sessionStorage — faqat yorliq (tab) tirik bo'lguncha. let bilan e'lon qilingan o'zgaruvchi RAM da — har refresh da nol dan boshlanadi.",
               diff="Medium", pts=3),
            dd("Siz Photoshop ni ochganingizda nima bo'lishini to'g'ri tartibda joylang",
               ["Photoshop fayli Disk da yashaydi (masalan, Program Files ichida)",
                "Siz ikonkani bosasiz — OS dasturni boshlaydi",
                "OS Photoshop ni Disk dan RAM ga ko'chiradi",
                "CPU RAM dagi kodni o'qib bajaradi",
                "Ekrandan natija siz ko'rasiz"],
               hint="Dastur har doim avval Disk da yashaydi. Ishga tushish uchun u RAM ga ko'chirilishi shart — CPU faqat RAM bilan ishlaydi.",
               explanation="Dastur Disk da fayl sifatida turadi. Ishga tushganda OS uni RAM ga yuklaydi (chunki CPU faqat RAM dan o'qiy oladi). CPU ko'rsatmalarni bajarib, natijani ekranga uzatadi. Dastur yopilsa RAM dagi qismi yo'qoladi, lekin Disk dagi fayl saqlanib qoladi.",
               diff="Medium", pts=3),
            ti("Absolute path va relative path farqi nima?",
               "Absolute path — tugamagan to'liq manzil, ildiz (/) yoki drive (C:\\) dan "
               "boshlanadi va aniq joyni ko'rsatadi: /home/aziz/Documents/file.txt. "
               "Relative path — joriy joydan boshlanadi: ./file.txt (joriy papkada), "
               "../file.txt (yuqori papka), boshqa-papka/file.txt (qo'shni papka). "
               "Absolute path har joydan bir xil ishlaydi (joriy papka muhim emas), "
               "relative path esa joriy papkaga bog'liq. Skript ichida absolute path "
               "ko'pincha xavfsizroq, lekin loyihani boshqa joyga ko'chirsangiz buziladi. "
               "Loyiha ichidagi fayllar uchun relative path yaxshi — loyiha har joyda ishlaydi.",
               hint=". = joriy papka, .. = yuqori papka, / = ildiz papka",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 3, "title": "4-Algoritmik fikrlash",
        "text": L4_TEXT, "code": L4_CODE, "lang": "javascript",
        "video": "https://youtu.be/6hfOvs8pY1k",
        "exercises": [
            mc("Brauzer konsolida if/else bloki nima qiladi?",
               ["Sikl yaratadi va qayta-qayta ishlaydi",
                "Shartga qarab ikki yo'ldan birini tanlaydi",
                "Sahifani yangilaydi",
                "Faqat matnni chiqaradi"],
               "B",
               hint="\"agar yosh 18 dan katta bo'lsa — yashil, aks holda — sariq\" — bu shart.",
               explanation="if/else — shartli ifoda. Kompyuter shartni baholaydi (true yoki false) va shunga qarab if-bloki yoki else-bloki ichidagi kodni bajaradi.",
               diff="Easy", pts=2),
            mc("Algoritmning 3 ta asosiy qurilish bloki qaysilari?",
               ["Sequence, Decision, Loop (ketma-ketlik, shart, takror)",
                "Variable, Function, Class",
                "HTML, CSS, JavaScript",
                "Print, Input, Output"],
               "A",
               hint="Siz hozir darsda 3 ta bloka bilan google.com ni robotga aylantirdingiz.",
               explanation="Bu uchtasi bilan dunyodagi har qanday algoritmni yozish mumkin: qadamlarni ketma-ket bajarish, shartga qarab yo'l tanlash, amalni takrorlash.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari algoritm hisoblanadi?",
               ["Choy damlash retsepti",
                "Avtobusda kompostlash tartibi (kart kiritish, tugmani bosish)",
                "Tasodifiy ravishda bir narsa o'ylash",
                "Google qidiruv natijalarini reytinglash usuli",
                "Telefon parolini kiritish va bosh sahifaga o'tish"],
               "A,B,D,E", multi=True,
               hint="Algoritm — aniq qadamlar ketma-ketligi muayyan natijaga olib boruvchi. Tasodifiy fikr — algoritm emas (qadam yo'q, natija yo'q).",
               explanation="Algoritm — har qanday \"qanday qilamiz?\" savoliga aniq javob. Hatto eng oddiy ish (parolni kiritish) ham algoritm. Tasodifiy fikr esa algoritm emas — unda na qadamlar, na natija belgilangan.",
               diff="Medium", pts=3),
            dd("Sendvich tayyorlash algoritmini to'g'ri tartibda joylang",
               ["Nonni paketdan oling",
                "Pichoq oling va nonni ikkiga kesing",
                "Pastki tilimga moy yoki sous suring",
                "Ustiga pomidor, tarvuz va boshqa ingredientlarni qo'ying",
                "Yuqori tilim bilan yoping",
                "Tarelka ga qo'yib xizmat qiling"],
               hint="Algoritm — aniq, batafsil, har qadam mantiqiy. \"Sendvich qil\" yetarli emas — kompyuter taxmin qilmaydi.",
               explanation="Bu — algoritmning birinchi qoidasi (aniqlik) tushuntiruvchi misol. Kompyuter \"nonni paketdan oling\" deb aytmasangiz — paket ichidagi nondan sendvich qiladi va paket ham qo'shadi. Har qadam aniq bo'lishi shart.",
               diff="Medium", pts=3),
            ti("Cheksiz sikl (infinite loop) nima va nima uchun yomon?",
               "Cheksiz sikl — bu hech qachon to'xtamaydigan loop. Sikl shartning yolg'on "
               "bo'lishini hech narsa o'zgartirmaydi. Misol: \"while X kichik 10\" lekin X "
               "hech qachon o'smaydi. Yomon, chunki: 1) dastur to'xtamaydi va ishlatuvchi "
               "kuta-kuta charchadi; 2) CPU 100% band qoladi va kompyuter sekinlashadi; "
               "3) batareya tez tugaydi (mobil). 4) brauzerda — yorliq qotib qoladi. "
               "Yechim: sikl shartini ichkaridan o'zgartirish (X ni oshirish) yoki break "
               "bilan to'xtatish. Algoritmning 4 qoidasidan biri — \"finite\" — har sikl tugashi shart.",
               hint="while (true) — eng mashhur cheksiz sikl. Hech qachon yozmang!",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 4, "title": "5-O'zgaruvchilar va turlar (universal)",
        "text": L5_TEXT, "code": L5_CODE, "lang": "javascript",
        "video": "https://youtu.be/v6Bm9JzkAv4",
        "exercises": [
            mc("Brauzer konsolida `typeof \"Aziz\"` qaysi natijani qaytaradi?",
               ['"string"', '"number"', '"text"', '"object"'],
               "A", explanation='Tirnoq ichidagi qiymat — har doim string turidagi.',
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari TO'G'RI o'zgaruvchi nomi?",
               ["yosh", "foydaYoshi", "1ism", "user-name", "_temp"],
               "A,B,E", multi=True,
               hint="Raqamdan boshlanmaslik va '-' belgisi bo'lmasligi kerak. _ ruxsat etilgan.",
               diff="Medium", pts=3),
            mc("`let a = \"5\"; let b = 3; console.log(a + b);` — konsolda nima chiqadi?",
               ['"53"', "8", '"8"', "Xato (TypeError)"],
               "A",
               explanation='a — string. String + number → JavaScript ikkalasini ham stringga aylantirib yopishtiradi. Number(a) + b qilsangiz 8 chiqadi.',
               hint='Yodda tuting: matn bilan son qo\'shilsa — yopishtirish bo\'ladi.',
               diff="Medium", pts=3),
            dd("Qiymatni mos turga ulang",
               ['number — 20',
                'string — "Aziz"',
                'boolean — true',
                'array — [1, 2, 3]',
                'object — { ism: "Aziz" }'],
               diff="Medium", pts=3),
            ti("`yosh = yosh + 1` qatori nima qiladi? Bosqichma-bosqich tushuntiring.",
               "Bu qator 3 bosqichda ishlaydi: 1) o'ng tomon hisoblanadi — kompyuter yosh "
               "qutichasidan eski qiymatni o'qiydi (masalan 20) va unga 1 qo'shadi (20 + 1 = 21); "
               "2) natija (21) vaqtinchalik xotirada turadi; 3) chap tomondagi yosh qutichasiga "
               "yangi qiymat (21) yoziladi — eski qiymat o'chiriladi. Natijada yosh qutichasi "
               "ichida endi 21 turadi. Bu naqsh dasturlashda eng ko'p uchraydigan amal — counter "
               "(hisoblagich) oshirish, ball qo'shish, indeks oldinga siljitish va h.k.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 5, "title": "6-Brauzer, tarmoq va veb",
        "text": L6_TEXT, "code": L6_CODE, "lang": "javascript",
        "video": "https://youtu.be/guvsH5OFizE",
        "exercises": [
            mc("HTTP nima?",
               ["Brauzer va server orasida muloqot qilish protokoli",
                "Faqat HTML yuklash usuli",
                "Internet provayder turi",
                "Operatsion tizim"],
               "A", diff="Easy", pts=2),
            mc("HTTP status kodi 404 nimani anglatadi?",
               ["Hammasi yaxshi",
                "Resurs topilmadi",
                "Server xatosi",
                "Sizga ruxsat yo'q"],
               "B", diff="Easy", pts=2),
            mc("Veb-sahifaning 3 ta asosiy qismi qaysilar?",
               ["HTML (struktura)",
                "CSS (dizayn)",
                "JavaScript (interaktivlik)",
                "Python",
                "PHP"],
               "A,B,C", multi=True,
               diff="Medium", pts=3),
            dd("URL ga kirishdagi qadamlarni tartiblang",
               ["Foydalanuvchi URL ni yozadi",
                "Brauzer DNS dan IP manzilni so'raydi",
                "DNS IP manzilni qaytaradi",
                "Brauzer serverga HTTP so'rov yuboradi",
                "Server HTML, CSS, JS qaytaradi",
                "Brauzer sahifani ko'rsatadi"],
               diff="Medium", pts=3),
            ti("Frontend va backend orasidagi farqni tushuntiring",
               "Frontend — foydalanuvchi ko'radigan va bevosita o'zaro aloqa qiladigan qism. "
               "Brauzerda ishlaydi. HTML, CSS, JavaScript tilllarida yoziladi. Misol: tugmalar, "
               "formalar, animatsiyalar, ranglar. Backend — server tomonda ishlaydi, "
               "foydalanuvchi ko'rmaydi. Ma'lumotlar bazasi, autentifikatsiya, biznes mantiq. "
               "Python (Django, Flask), Java, Node.js, Go, PHP. Frontend so'raydi — backend "
               "javob qaytaradi. Misol: Telegram'da xabar yozish — frontend; o'sha xabarni "
               "boshqa foydalanuvchiga yetkazish, saqlash — backend.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 6, "title": "7-Terminal va Git",
        "text": L7_TEXT, "code": L7_CODE, "lang": "bash",
        "video": "https://youtu.be/RGOj5yH7evk",
        "exercises": [
            mc("Terminalda joriy papkani aniqlash uchun qaysi komanda?",
               ["pwd", "cd", "ls", "where"],
               "A", explanation="pwd — 'print working directory' qisqartmasi.",
               diff="Easy", pts=2),
            mc("Git ish jarayonining to'g'ri tartibi qaysi?",
               ["edit → add → commit → push",
                "commit → add → edit → push",
                "push → commit → add → edit",
                "edit → commit → add → push"],
               "A", diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari TO'G'RI Git komandalari?",
               ["git init", "git add .", "git commit -m", "git push", "git delete"],
               "A,B,C,D", multi=True,
               hint="git delete — bunday komanda yo'q. git rm bor.",
               diff="Medium", pts=3),
            mc("GitHub Pages nima?",
               ["Bepul vebsite hosting (HTML/CSS/JS uchun)",
                "GitHub'ning yangi versiyasi",
                "Kommersiya hosting xizmati",
                "Faqat dokumentatsiya uchun"],
               "A", diff="Easy", pts=2),
            dd("Birinchi marta git ni sozlash va birinchi commit qadamlari",
               ["git config --global user.name \"Ismingiz\"",
                "git config --global user.email \"siz@example.com\"",
                "mkdir loyiha && cd loyiha",
                "git init",
                "echo \"Hello\" > README.md",
                "git add README.md",
                "git commit -m \"Birinchi commit\""],
               diff="Medium", pts=3),
            ti(".gitignore fayl nima va nima uchun kerak?",
               ".gitignore — Git ga qaysi fayllar va papkalarni KUZATMASLIK kerakligini "
               "aytadigan fayl. Loyiha ichidagi ba'zi narsalar Git'da bo'lmasligi kerak: "
               "1) parol va maxfiy ma'lumotlar (.env fayl) — xavfsizlik; "
               "2) katta paket fayllar (node_modules, __pycache__) — repo hajmini kichik tutish; "
               "3) IDE va OS sozlamalari (.vscode, .DS_Store) — har odamning kompyuteri turlicha; "
               "4) build natijalari (dist, build) — kerak bo'lganda qayta yaratiladi. "
               ".gitignore yo'q bo'lsa, parollar GitHub'da xalqqa ko'rinib qoladi — eng katta xato.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 7, "title": "8-Birinchi publik sahifa (CAPSTONE)",
        "text": L8_TEXT, "code": L8_CODE, "lang": "html",
        "video": "https://youtu.be/2MsN8gpT6jY",
        "exercises": [
            mc("GitHub Pages qaysi turdagi sahifalar uchun ishlatiladi?",
               ["Statik (HTML, CSS, JS) sahifalar",
                "Faqat Wordpress saytlar",
                "Server-side rendered ilovalar",
                "Faqat dokumentatsiya"],
               "A", explanation="GitHub Pages statik HTML/CSS/JS uchun. Backend (Python, Node) yo'q.",
               diff="Easy", pts=2),
            mc("Repo nomi <username>.github.io bo'lsa, URL qanday bo'ladi?",
               ["https://username.github.io/",
                "https://github.com/username/",
                "https://username.github.com/",
                "https://pages.github.io/username/"],
               "A", hint="Maxsus format — root URL beradi.",
               diff="Medium", pts=3),
            mc("HTML sahifa eng kamida qaysi teglarga ega bo'lishi kerak?",
               ["<!DOCTYPE html>", "<html>", "<head>", "<body>", "<title>"],
               "A,B,C,D,E", multi=True,
               diff="Medium", pts=3),
            dd("GitHub Pages bilan sahifani ishga tushirish qadamlari",
               ["Local'da index.html yaratish",
                "git init va commit",
                "GitHub'da yangi repo yaratish",
                "git push origin main",
                "Settings → Pages → branch tanlash",
                "Yashil URL paydo bo'lishini kutish"],
               diff="Medium", pts=3),
            ti("Sizning birinchi GitHub Pages sahifangiz qanday bo'lishi kerak — strategiya?",
               "Mening birinchi GitHub Pages sahifam — bu mening dunyoga \"birinchi xat\"im. "
               "Maqsadlar: 1) o'zimni qisqacha tanishtirish — kim, qayerdan, nima o'rganmoqdaman; "
               "2) hozirgi va kelajakdagi o'qishim/maqsadlarim; 3) ulanish ma'lumotlari — Telegram, "
               "GitHub, email; 4) loyihalar uchun joy qoldirish — keyinroq qo'shaman. Dizayn: sodda, "
               "o'qishga oson, mobile-friendly. Ranglar: 1-2 ta asosiy + neutral. Shrift: standart "
               "system fontlardan biri. Bu sahifa keyinchalik portfolio ga aylanadi.",
               diff="Hard", pts=4),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Seeding logic
# ─────────────────────────────────────────────────────────────────────────────
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
            print(f"Course {COURSE['title']!r} already exists (id={existing.id}). Delete it first if you want to re-seed.")
            return

        course = Course(**COURSE)
        db.add(course); await db.flush()
        print(f"Created course: id={course.id}  title={course.title!r}")

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
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  ex={len(ex_rows)}  {lesson.title[:55]}")

        if dry_run:
            await db.rollback(); print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            total_ex = sum(len(l["exercises"]) for l in LESSONS)
            print(f"\n✓ Seeded course {COURSE['title']!r} — {len(LESSONS)} lessons, {total_ex} exercises.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed(dry_run=("--dry-run" in sys.argv)))
