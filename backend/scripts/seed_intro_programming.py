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
<h2>Brauzer va veb — so'rov-javob raqsi</h2>

<pre class="mermaid">
flowchart LR
    B["brauzer"] -->|1 GET URL| DNS["DNS"]
    DNS -->|2 IP qaytaradi| B
    B -->|3 HTTP request| S["server"]
    S -->|4 HTML CSS JS| B
    B --> R["sahifa"]
</pre>

<h3>🏆 5 daqiqada g'alaba — internet jonli ko'rinadi</h3>
<p>Hech narsa o'rnatmaymiz. Brauzer ichida har bir so'rov va javobni o'z ko'zingiz bilan ko'rasiz.</p>

<h4>BLOKA 1 — Network tab (so'rovlarni ushlash)</h4>
<ol>
<li>Yangi brauzer oynasi: <code>https://github.com</code> ga kiring</li>
<li><kbd>F12</kbd> bosing → <strong>Network</strong> tabini tanlang</li>
<li>Sahifani <kbd>Ctrl+R</kbd> (Mac: <kbd>Cmd+R</kbd>) bilan qayta yuklang</li>
<li>Endi ro'yxat to'ldi — har bir qator bitta so'rov</li>
</ol>
<p>Har qatorda quyidagilar ko'rinadi:</p>
<ul>
<li><strong>Name</strong> — qaysi fayl (HTML, logo.png, style.css ...)</li>
<li><strong>Status</strong> — 200 (OK), 304 (cached), 404 (topilmadi)</li>
<li><strong>Type</strong> — document, script, image, font, xhr</li>
<li><strong>Size</strong> — necha KB</li>
<li><strong>Time</strong> — necha millisekund</li>
</ul>
<p>Birinchi qatorni bosing → o'ng paneldan <strong>Headers</strong> ni tanlang. Bu yerda <code>Request Method: GET</code>, <code>Status: 200</code>, <code>Content-Type: text/html</code> va boshqa "ko'rinmaydigan" muloqotni ko'rasiz. Mana — internet aslida shunday ko'rinadi.</p>

<h4>BLOKA 2 — Konsoldan API ga so'rov</h4>
<p>Endi siz brauzer bo'lasiz. <kbd>Console</kbd> tabiga o'ting va yozing:</p>
<pre><code>// GitHub'ning ochiq API'sidan ma'lumot olamiz
fetch("https://api.github.com/users/torvalds")
    .then(r => r.json())
    .then(data => {
        console.log("Ism:", data.name);
        console.log("Joy:", data.location);
        console.log("Public repos:", data.public_repos);
        console.log("Followers:", data.followers);
    });</code></pre>
<p><strong>Nima bo'ldi:</strong> sizning brauzer GitHub serveriga HTTP GET so'rov yubordi. Server JSON ko'rinishidagi ma'lumotni qaytardi. <code>fetch</code> — bu zamonaviy JavaScript komandasi, server bilan muloqot uchun. Network tabga qaytsangiz — yangi qator paydo bo'lgan: <code>torvalds</code>, Status 200, Type xhr.</p>

<h4>BLOKA 3 — Sahifani jonli o'zgartirish</h4>
<p>Hozir ham GitHub.com da turibsiz. Konsolda yozing:</p>
<pre><code>// Sahifaning 3 qismini "qo'l bilan" o'zgartiramiz

// 1. HTML strukturasini o'qing
console.log(document.title);
console.log(document.querySelectorAll("a").length, "ta havola bor");

// 2. CSS — fonni o'zgartiring
document.body.style.background = "linear-gradient(45deg, #ff6ec4, #7873f5)";

// 3. JavaScript — tugma qo'shing
let btn = document.createElement("button");
btn.textContent = "Bosing!";
btn.style.cssText = "position:fixed;top:20px;right:20px;padding:10px 20px;font-size:20px;z-index:9999";
btn.onclick = () => alert("Sahifani men o'zgartirdim!");
document.body.appendChild(btn);</code></pre>
<p><strong>Nima bo'ldi:</strong> 3 ta qatorda 3 ta texnologiyaga tegdingiz — <strong>HTML</strong> (struktura), <strong>CSS</strong> (dizayn), <strong>JavaScript</strong> (interaktivlik). Sahifani <kbd>F5</kbd> bilan yangilasangiz — hammasi yo'qoladi, chunki o'zgarishlar faqat sizning brauzer xotirangizda edi, serverda emas.</p>

<h3>🐛 Ataylab xato — 404 ni ko'ramiz</h3>
<p>Konsolda yozing:</p>
<pre><code>fetch("https://api.github.com/users/bumantxtaitarmiymis123abc")
    .then(r => {
        console.log("Status:", r.status);   // 404 chiqadi
        console.log("OK?", r.ok);           // false
        return r.json();
    })
    .then(data => console.log(data));</code></pre>
<p>Status <strong>404 Not Found</strong> — bu foydalanuvchi mavjud emas. Eslab qoling: 404 — bu serverning aybi emas, sizning so'rovingiz noto'g'ri manzilga ketgan. Eng mashhur xato kodi.</p>

<h3>Endi tushuntiramiz — internet qanday ishlaydi</h3>

<h4>5 bosqichda google.com ochish</h4>
<ol>
<li>Siz <code>google.com</code> deb yozasiz</li>
<li>Brauzer DNS server'ga so'raydi: "google.com qaysi IP?"</li>
<li>DNS javob: "google.com = 142.250.180.46"</li>
<li>Brauzer 142.250.180.46 ga HTTP GET / yuboradi</li>
<li>Server HTML+CSS+JS qaytaradi → brauzer rasm chizadi</li>
</ol>
<p>Bu 0.3 sekundda bo'ladi. Har gal.</p>

<h4>URL anatomiyasi</h4>
<pre><code>https://api.github.com:443/users/torvalds?tab=repos#main
  ↑           ↑          ↑      ↑           ↑       ↑
protokol    domain     port    path        query  fragment</code></pre>

<h4>HTTP methodlar (so'rov turlari)</h4>
<table>
<tr><th>Method</th><th>Ma'no</th><th>Hayotiy misol</th></tr>
<tr><td><code>GET</code></td><td>Menga ber</td><td>Sahifa yuklash, qidirish</td></tr>
<tr><td><code>POST</code></td><td>Yangi yarating</td><td>Forma yuborish, ro'yxatdan o'tish</td></tr>
<tr><td><code>PUT/PATCH</code></td><td>Mavjudni yangilang</td><td>Profil tahrirlash</td></tr>
<tr><td><code>DELETE</code></td><td>O'chiring</td><td>Postni o'chirish</td></tr>
</table>

<h4>HTTP status kodlari</h4>
<ul>
<li><strong>200 OK</strong> — hammasi yaxshi</li>
<li><strong>301 / 302</strong> — manzil o'zgargan, boshqa joyga yo'naltirildi</li>
<li><strong>400 Bad Request</strong> — sizning so'rovingiz xato</li>
<li><strong>401 Unauthorized</strong> — login qiling</li>
<li><strong>403 Forbidden</strong> — login bor, lekin ruxsat yo'q</li>
<li><strong>404 Not Found</strong> — yo'q, topilmadi</li>
<li><strong>500 Internal Server Error</strong> — serverning aybi</li>
</ul>
<p>Qoida: <strong>2xx</strong> = yaxshi, <strong>3xx</strong> = yo'naltirish, <strong>4xx</strong> = sizning xato, <strong>5xx</strong> = serverning xato.</p>

<h4>Sahifaning 3 qismi (siz konsolda tegdingiz)</h4>
<ul>
<li>📄 <strong>HTML</strong> — struktura (sarlavha, paragraf, tugma)</li>
<li>🎨 <strong>CSS</strong> — dizayn (rang, shrift, joylashuv)</li>
<li>⚡ <strong>JavaScript</strong> — interaktivlik (click → nima bo'ladi)</li>
</ul>

<h4>Frontend vs Backend</h4>
<table>
<tr><th></th><th>Frontend</th><th>Backend</th></tr>
<tr><td>Qayerda</td><td>Sizning brauzeringizda</td><td>Uzoq serverda</td></tr>
<tr><td>Til</td><td>HTML, CSS, JavaScript</td><td>Python, Go, Node.js, Java, PHP</td></tr>
<tr><td>Vazifa</td><td>Ko'rinish va interaktivlik</td><td>Ma'lumot, login, biznes logika</td></tr>
</table>
<p>Misol: Telegram'da xabar yozish — frontend. O'sha xabarni boshqa odamga yetkazish va saqlash — backend.</p>

<h4>DevTools — har dasturchining oynasi</h4>
<table>
<tr><th>Tab</th><th>Nima uchun</th></tr>
<tr><td><strong>Elements</strong></td><td>HTML+CSS ni o'qish va o'zgartirish</td></tr>
<tr><td><strong>Console</strong></td><td>JS yozish, xatolarni ko'rish</td></tr>
<tr><td><strong>Network</strong></td><td>Har so'rov-javobni kuzatish</td></tr>
<tr><td><strong>Application</strong></td><td>localStorage, cookies, cache</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Internet — bu so'rov (GET/POST/PUT/DELETE) va javob (200/404/500)</li>
<li>DNS — domen nomini IP manzilga o'giradi</li>
<li>Network tab har bir so'rovni ko'rsatadi</li>
<li><code>fetch()</code> bilan konsoldan API ga so'rov yuborasiz</li>
<li>Sahifa = HTML + CSS + JavaScript</li>
<li>Frontend brauzeringda, Backend serverda</li>
</ul>
"""

L6_CODE = """\
// ═══ DARS 6 — BRAUZER KONSOLI BILAN INTERNETNI USHLASH ═══
// github.com ga kiring → F12 → quyidagilarni sinab ko'ring

// ─── BLOKA 1: Network tab ───────────────────────────
// Network tabini oching, Ctrl+R bilan yangilang
// Har qatorni bosing — Headers/Response da nimalar borligini ko'ring

// ─── BLOKA 2: fetch() bilan API ga so'rov ───────────
fetch("https://api.github.com/users/torvalds")
    .then(r => r.json())
    .then(data => {
        console.log("Ism:", data.name);
        console.log("Joy:", data.location);
        console.log("Public repos:", data.public_repos);
    });

// ─── BLOKA 3: Sahifaning 3 qismi (HTML+CSS+JS) ──────
console.log(document.title);
document.body.style.background = "linear-gradient(45deg, #ff6ec4, #7873f5)";

let btn = document.createElement("button");
btn.textContent = "Bosing!";
btn.style.cssText = "position:fixed;top:20px;right:20px;padding:10px;z-index:9999";
btn.onclick = () => alert("Sahifani men o'zgartirdim!");
document.body.appendChild(btn);

// ─── XATO TUZOG'I: 404 ni ko'rish ───────────────────
fetch("https://api.github.com/users/bumantxtaitarmiymis123abc")
    .then(r => {
        console.log("Status:", r.status);   // 404
        console.log("OK?", r.ok);           // false
    });
"""



# ═════════════════════════════════════════════════════════════════════════════
# L7 — Terminal va Git
# ═════════════════════════════════════════════════════════════════════════════
L7_TEXT = """\
<h2>Terminal va Git — 10 daqiqada birinchi publik kodingiz</h2>

<pre class="mermaid">
flowchart LR
    WEB["github.com web"] -->|1 Create repo| REPO["public repo"]
    REPO -->|2 git clone| LOCAL["local papka"]
    LOCAL -->|3 edit + add + commit| STAGE["snapshot"]
    STAGE -->|4 git push| REPO
    REPO --> WORLD["dunyo ko'radi"]
</pre>

<h3>🏆 10 daqiqada g'alaba — birinchi publik repo</h3>
<p>Hech qanday komanda yoki o'rnatish yo'q. Sizda faqat brauzer kerak. Oxirida — sizning kodingiz <code>github.com/sizning-ism/salom-dunyo</code> URL'da yashaydi.</p>

<h4>BLOKA 1 — Web UI bilan repo yaratish (faqat brauzer)</h4>
<ol>
<li>github.com'da ro'yxatdan o'ting (agar hisobingiz bo'lmasa)</li>
<li>O'ng yuqorida <strong>+</strong> tugmasini bosing → <strong>New repository</strong></li>
<li>Repository name: <code>salom-dunyo</code></li>
<li><strong>Public</strong> ni tanlang</li>
<li><strong>Initialize with README</strong> ga ✓ qo'ying</li>
<li><strong>Create repository</strong> bosing</li>
</ol>
<p>Tabriklayman — sizda birinchi publik repo bor. URL: <code>github.com/SIZNING-ISM/salom-dunyo</code>. Bu havolani do'stingizga yuboring — ular ko'radi.</p>

<h4>BLOKA 2 — Web orqali faylni tahrirlash</h4>
<ol>
<li>Repo ichida <code>README.md</code> ga bosing</li>
<li>O'ng yuqoridagi <strong>qalam</strong> ikonkasini bosing</li>
<li>Matnni o'zgartiring:
<pre><code># Salom dunyo!

Men Aziz, dasturlashni o'rganmoqdaman.

## Mening rejam
- HTML/CSS o'rganish
- JavaScript bilan tanishish
- Birinchi sahifani GitHub Pages'ga joylashtirish</code></pre>
</li>
<li>Pastga tushing → <strong>Commit message</strong>: "README ni yangiladim" → <strong>Commit changes</strong></li>
</ol>
<p>Mana, sizning birinchi commit'ingiz. Repo bosh sahifasiga qayting — README yangilangan. Tarix uchun <strong>Commits</strong> tugmasini bosing — 2 ta commit ko'rinadi.</p>

<h4>BLOKA 3 — Endi terminal bilan (lokal kompyuterda)</h4>
<p>Terminalni oching:</p>
<ul>
<li><strong>Mac</strong>: Cmd+Space → "Terminal" → Enter</li>
<li><strong>Windows</strong>: Win → "PowerShell" → Enter</li>
<li><strong>Linux</strong>: Ctrl+Alt+T</li>
</ul>
<p>Avval terminalda yashashni o'rganamiz — 5 ta komanda:</p>
<pre><code>pwd                  # qayerdaman? — masalan /home/aziz
ls                   # nima bor shu papkada?
cd Desktop           # Desktop papkasiga o'tdim
mkdir loyihalar      # yangi papka yaratdim
cd loyihalar         # ichkariga kirdim</code></pre>
<p>Endi GitHub'dagi repo'ni shu kompyuterga ko'chiramiz. Repo sahifasidagi yashil <strong>Code</strong> tugmasini bosing → HTTPS URL'ni nusxa oling. Terminalda:</p>
<pre><code>git config --global user.name "Sizning Ism"
git config --global user.email "siz@example.com"

git clone https://github.com/SIZNING-ISM/salom-dunyo.git
cd salom-dunyo
ls                   # README.md ko'rinadi — bu o'sha fayl!</code></pre>
<p><strong>Hayrat 1:</strong> GitHub'dagi fayllar endi lokal kompyuteringizda. <code>cat README.md</code> bilan ichini ko'ring.</p>

<p>Endi lokal o'zgarish kiritamiz va GitHub'ga qaytarib yuboramiz:</p>
<pre><code># Yangi fayl qo'shamiz
echo "Salom!" > hello.txt

# Git ga nima o'zgarganini ko'rsating
git status                   # hello.txt — Untracked

# Stage'ga qo'shish
git add hello.txt

# Snapshot saqlash
git commit -m "hello.txt qo'shildi"

# GitHub'ga yuborish
git push</code></pre>
<p>Brauzerga qayting → repo sahifasini yangilang (<kbd>F5</kbd>) → <code>hello.txt</code> ro'yxatda paydo bo'ldi. Lokal terminalda yozgan fayl endi internetda jonli!</p>

<h3>🐛 Ataylab xato — git add ni unutamiz</h3>
<p>Yangi faylni qo'shing-u, lekin git add ni o'tkazib yuboring:</p>
<pre><code>echo "yana bitta" > yangi.txt
git commit -m "yangi.txt qo'shildi"</code></pre>
<p>Natija: <code>nothing to commit, working tree clean</code> yoki <code>untracked files: yangi.txt</code> ogohlantirishi. Sababi: git fayllarni 2 bosqichda saqlaydi. Birinchi <strong>stage</strong> (git add) — qaysi fayllarni saqlashni tanlash; ikkinchi <strong>commit</strong> — snapshot olish. <code>git add</code>'siz commit topa olmaydi. Tuzating:</p>
<pre><code>git add yangi.txt
git commit -m "yangi.txt qo'shildi"
git push</code></pre>

<h3>Endi tushuntiramiz — Terminal va Git asoslari</h3>

<h4>Terminal nima va nega kerak?</h4>
<p>Terminal — kompyuter bilan <strong>matn orqali</strong> muloqot. Sichqoncha + tugma o'rniga — komandalar yozasiz. Boshida qiyin, lekin: tez, takrorlanadigan, masofadan ishlaydi (server admin uchun majburiy).</p>

<h4>Eng muhim 10 ta terminal komandasi</h4>
<table>
<tr><th>Komanda</th><th>Vazifa</th><th>Misol</th></tr>
<tr><td><code>pwd</code></td><td>Qayerdaman?</td><td><code>pwd</code> → <code>/home/aziz</code></td></tr>
<tr><td><code>ls</code></td><td>Papkani ko'rsat</td><td><code>ls -lah</code></td></tr>
<tr><td><code>cd</code></td><td>Papkaga o't</td><td><code>cd Documents</code></td></tr>
<tr><td><code>cd ..</code></td><td>Yuqori papka</td><td><code>cd ..</code></td></tr>
<tr><td><code>mkdir</code></td><td>Yangi papka</td><td><code>mkdir loyiha</code></td></tr>
<tr><td><code>touch</code></td><td>Bo'sh fayl</td><td><code>touch index.html</code></td></tr>
<tr><td><code>cat</code></td><td>Fayl ichini ko'rsat</td><td><code>cat README.md</code></td></tr>
<tr><td><code>echo</code></td><td>Yozish (yoki faylga)</td><td><code>echo "hi" > a.txt</code></td></tr>
<tr><td><code>rm</code></td><td>Faylni o'chir</td><td><code>rm old.txt</code></td></tr>
<tr><td><code>mv</code></td><td>Ko'chirish / nom</td><td><code>mv a.txt b.txt</code></td></tr>
</table>
<p><strong>Pro maslahat</strong>: <kbd>Tab</kbd> avtotugatish — yarim yozsangiz Tab bosing, qolganini terminal o'zi yozadi.</p>

<h4>Git ish jarayoni — 4 bosqich</h4>
<ol>
<li><strong>Edit</strong> — faylni o'zgartirasiz</li>
<li><strong>Add</strong> — <code>git add</code> bilan stage'ga qo'yasiz ("buni saqlamoqchiman")</li>
<li><strong>Commit</strong> — <code>git commit -m "xabar"</code> bilan snapshot</li>
<li><strong>Push</strong> — <code>git push</code> bilan GitHub'ga yuborasiz</li>
</ol>

<pre class="mermaid">
flowchart LR
    E["working dir"] -->|git add| S["staging"]
    S -->|git commit| L["local history"]
    L -->|git push| R["remote GitHub"]
    R -->|git pull| L
</pre>

<h4>Eng muhim git komandalari</h4>
<pre><code># Loyiha boshida (bir marta)
git config --global user.name "..."
git config --global user.email "..."

# Mavjud repo'ni olish
git clone URL

# Yangi (bo'sh) loyiha boshlash
git init

# Holatni ko'rish
git status

# Stage va commit
git add fayl.txt           # bittasini
git add .                  # hammasini
git commit -m "xabar"

# Tarix
git log --oneline

# Sync
git push                   # GitHub'ga yubor
git pull                   # GitHub'dan ol</code></pre>

<h4>.gitignore — git'ga nimani UNUTISHNI aytish</h4>
<p>Ba'zi fayllar git'da bo'lmasligi kerak: parollar, katta build natijalari, paket papkalari.</p>
<pre><code># .gitignore fayli
.env                # maxfiy parollar
node_modules/       # JS paketlari
__pycache__/        # Python cache
*.log               # log fayllar
.DS_Store           # macOS xizmat fayli</code></pre>

<h4>Eng ko'p uchraydigan 3 ta xato</h4>
<table>
<tr><th>Xato</th><th>Sabab</th><th>Yechim</th></tr>
<tr><td><code>nothing to commit</code></td><td><code>git add</code> qilmagansiz</td><td><code>git add</code> + qaytadan commit</td></tr>
<tr><td><code>push rejected</code></td><td>Remote'da yangi commit bor</td><td><code>git pull</code> → keyin push</td></tr>
<tr><td><code>Authentication failed</code></td><td>Parol ishlamaydi — token kerak</td><td>GitHub Settings → Personal Access Token</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>GitHub'da repo yaratish — web UI orqali ham, terminal orqali ham mumkin</li>
<li>Terminal — pwd, ls, cd, mkdir, touch — kunlik komandalar</li>
<li>Git workflow: edit → add → commit → push</li>
<li><code>git add</code> va <code>git commit</code> alohida bosqichlar — stage qaysi fayllarni saqlashni boshqaradi</li>
<li><code>.gitignore</code> bilan parollar va kesh git'ga tushmaydi</li>
<li><code>git clone</code> — remote repo'ni lokal'ga ko'chiradi; <code>git push</code> — orqaga yuboradi</li>
</ul>
"""

L7_CODE = """\
# ═══ DARS 7 — TERMINAL + GIT BIRINCHI SAYKLI ═══

# ─── BLOKA 1: WEB UI orqali repo (brauzer) ──────
# github.com → + → New repository
# Name: salom-dunyo  → Public → Init with README → Create
# Sizda endi: github.com/SIZNING-ISM/salom-dunyo

# ─── BLOKA 2: Terminal asoslari ─────────────────
pwd                              # qayerdaman?
ls                               # nima bor?
cd Desktop                       # papkaga o'tdim
mkdir loyihalar && cd loyihalar  # yangi papka + ichkari

# ─── BLOKA 3: Lokal sykl (clone → edit → push) ──
git config --global user.name "Sizning Ism"
git config --global user.email "siz@example.com"

git clone https://github.com/SIZNING-ISM/salom-dunyo.git
cd salom-dunyo
ls                               # README.md — GitHub'dan keldi
cat README.md                    # ichini ko'rish

# Yangi fayl + commit + push
echo "Salom!" > hello.txt
git status                       # hello.txt — Untracked
git add hello.txt
git commit -m "hello.txt qo'shildi"
git push                         # brauzerni F5 bosing — hello.txt jonli!

# ─── XATO TUZOG'I: git add ni unutish ───────────
echo "yana bitta" > yangi.txt
git commit -m "yangi.txt qo'shildi"   # XATO: nothing to commit
# Tuzatish:
git add yangi.txt
git commit -m "yangi.txt qo'shildi"
git push

# ─── Tez-tez kerak ──────────────────────────────
git log --oneline                # tarix
git status                       # nima o'zgargan
git pull                         # remote'dan yangiliklar
"""


# ═════════════════════════════════════════════════════════════════════════════
# L8 — Birinchi publik sahifa (CAPSTONE)
# ═════════════════════════════════════════════════════════════════════════════
L8_TEXT = """\
<h2>🚀 Birinchi publik sahifa — CAPSTONE</h2>

<pre class="mermaid">
flowchart LR
    F["index.html"] --> LOCAL["dbl click brauzer"]
    F --> REPO["git push"]
    REPO --> GH["GitHub"]
    GH -->|Pages on| URL["yourname.github.io"]
    URL --> WORLD["publik URL"]
</pre>

<h3>🏆 5 daqiqada g'alaba — kompyuterda jonli sahifa</h3>
<p>Hech qanday tarmoq, hosting yoki server kerak emas. Brauzeringiz HTML faylni <strong>to'g'ridan-to'g'ri</strong> ochib, sahifani ko'rsata oladi.</p>

<h4>BLOKA 1 — Yangi fayl, jonli sahifa</h4>
<ol>
<li>Ish stolida yangi papka yarating: <code>mening-sahifam</code></li>
<li>O'sha papka ichida yangi matn fayli yarating, nomini <strong>aynan</strong> <code>index.html</code> qo'ying (txt emas!)</li>
<li>Fayl ichini quyidagicha to'ldiring (Notepad, TextEdit, VS Code — har qanday muharrir):</li>
</ol>
<pre><code>&lt;!DOCTYPE html&gt;
&lt;html lang="uz"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;title&gt;Mening birinchi sahifam&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Salom, dunyo!&lt;/h1&gt;
    &lt;p&gt;Mana, mening birinchi sahifam.&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
<p>Faylni saqlang. Endi <strong>fayl ustiga ikki marta bosing</strong> — brauzer ochiladi va sahifangizni ko'rsatadi. URL qatorida: <code>file:///.../mening-sahifam/index.html</code>. Tabriklayman — sizda jonli HTML sahifa bor.</p>

<h4>BLOKA 2 — Dizayn qo'shamiz (CSS)</h4>
<p><code>&lt;/title&gt;</code> dan keyin va <code>&lt;/head&gt;</code> dan oldin <code>&lt;style&gt;</code> blokini qo'shing:</p>
<pre><code>&lt;style&gt;
    body {
        font-family: sans-serif;
        max-width: 600px;
        margin: 60px auto;
        padding: 0 20px;
        color: #1a1a2e;
        background: linear-gradient(135deg, #fafafd, #e8e9f7);
        line-height: 1.6;
    }
    h1 {
        color: #6c5ce7;
        font-size: 3em;
        margin-bottom: 10px;
    }
&lt;/style&gt;</code></pre>
<p>Faylni saqlang (<kbd>Ctrl+S</kbd>) → brauzerda <kbd>F5</kbd> bosing. Mana, dizayn paydo bo'ldi — gradient fon, katta binafsha sarlavha. CSS sahifaning "kostyumi".</p>

<h4>BLOKA 3 — Interaktivlik qo'shamiz (JS)</h4>
<p><code>&lt;/body&gt;</code> dan oldin tugma va JavaScript qo'shing:</p>
<pre><code>&lt;button id="say-hi"&gt;Bosing!&lt;/button&gt;
&lt;p id="output"&gt;&lt;/p&gt;

&lt;script&gt;
    let count = 0;
    document.getElementById("say-hi").onclick = () =&gt; {
        count = count + 1;
        document.getElementById("output").textContent =
            "Siz tugmani " + count + " marta bosdingiz!";
    };
&lt;/script&gt;</code></pre>
<p>Saqlang → F5 → tugmani bir necha marta bosing. Hisoblagich oshib boradi. <strong>3 ta texnologiya birga ishlamoqda</strong>: HTML (struktura), CSS (rang), JavaScript (interaktivlik).</p>

<h3>🐛 Ataylab xato — kichik harf masalasi</h3>
<p>Sinab ko'ring: papka ichida fayl nomini <code>Index.HTML</code> qiling. Brauzer URL qatorida <code>index.html</code> deb yozing va Enter bosing. Linux/Mac da — <strong>404 yoki ochilmaydi</strong>; Windows da — ochiladi. Sababi: serverlar (va Linux) <strong>katta-kichik harflarga sezgir</strong>. <code>Index.HTML</code> ≠ <code>index.html</code>. GitHub Pages — Linux serverda turadi. Qoida: fayl nomlari har doim kichik harfda, bo'sh joysiz, <code>my-page.html</code> ko'rinishida.</p>

<h3>Endi internetga chiqaramiz — GitHub Pages 4 qadam</h3>

<h4>1️⃣ Lokal repo'ni tayyorlang</h4>
<p>Terminalni <code>mening-sahifam</code> papkasi ichida oching. Avvalgi darsdagi git komandalarini ishlating:</p>
<pre><code>git init
git add .
git commit -m "Birinchi sahifa"</code></pre>

<h4>2️⃣ GitHub'da repo yarating</h4>
<p>github.com → + → New repository. Tavsiya: nomini aynan <strong><code>SIZNING-USERNAME.github.io</code></strong> qo'ying (kichik harflarda). Bu maxsus nom — URL'ingiz <code>https://SIZNING-USERNAME.github.io/</code> bo'ladi (root URL).</p>

<h4>3️⃣ Lokalni GitHub'ga ulang</h4>
<pre><code>git remote add origin https://github.com/SIZNING-USERNAME/SIZNING-USERNAME.github.io.git
git branch -M main
git push -u origin main</code></pre>

<h4>4️⃣ Pages'ni yoqing (faqat boshqa nom uchun)</h4>
<p>Agar repo nomi <code>SIZNING-USERNAME.github.io</code> bo'lsa — Pages avtomatik yoqiladi. Boshqa nom (masalan <code>about-me</code>) bo'lsa:</p>
<ol>
<li>Repo → <strong>Settings</strong> → <strong>Pages</strong></li>
<li>Source: Deploy from a branch</li>
<li>Branch: <code>main</code> → <code>/ (root)</code> → Save</li>
<li>1–2 daqiqa kuting</li>
<li>Yashil banner: "Your site is live at <strong>https://SIZNING-USERNAME.github.io/about-me/</strong>"</li>
</ol>
<p>Bu URL'ni do'stlaringizga yuboring. Resume'ga qo'shing. Telegram'da ulashing. <strong>Internetda sizning izingiz bor</strong> — kompyuteringiz o'chsa ham, sahifa ishlaydi.</p>

<h3>Endi tushuntiramiz — nima sodir bo'ldi</h3>

<h4>3 ta texnologiya qanday birga ishlaydi</h4>
<table>
<tr><th>Texnologiya</th><th>Vazifa</th><th>Misol</th></tr>
<tr><td>HTML</td><td>Sahifa <strong>tuzilishi</strong></td><td><code>&lt;h1&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;button&gt;</code></td></tr>
<tr><td>CSS</td><td>Sahifa <strong>ko'rinishi</strong></td><td>rang, shrift, joylashuv</td></tr>
<tr><td>JavaScript</td><td>Sahifa <strong>xulq-atvori</strong></td><td>click, hisoblagich, animatsiya</td></tr>
</table>

<h4>HTML eng kamida nima kerak?</h4>
<ul>
<li><code>&lt;!DOCTYPE html&gt;</code> — brauzerga "bu HTML5"</li>
<li><code>&lt;html&gt;</code> — butun sahifaning idishi</li>
<li><code>&lt;head&gt;</code> — sahifa haqida ma'lumot (title, meta, CSS)</li>
<li><code>&lt;body&gt;</code> — ko'rinadigan tarkib</li>
</ul>

<h4>file:// vs https://</h4>
<ul>
<li><code>file:///home/aziz/.../index.html</code> — fayl bevosita siz turgan kompyuterdan ochilgan. Faqat siz ko'rasiz.</li>
<li><code>https://aziz.github.io/</code> — internetdagi server'dan, dunyodagi har kim ko'radi.</li>
</ul>
<p>Lokal sinov uchun <code>file://</code> yetarli. Lekin <code>fetch()</code> va boshqa "haqiqiy" funksiyalar faqat <code>http(s)://</code> da to'liq ishlaydi.</p>

<h4>GitHub Pages — nima yaxshi, nima yo'q</h4>
<table>
<tr><th>✅ Ishlaydi</th><th>❌ Ishlamaydi</th></tr>
<tr><td>HTML, CSS, JavaScript</td><td>Python, Node, PHP (backend)</td></tr>
<tr><td>Statik sahifa</td><td>Ma'lumotlar bazasi (PostgreSQL, ...)</td></tr>
<tr><td>API'larga so'rov (frontend)</td><td>Login tizimi (server logikasi)</td></tr>
<tr><td>To'liq bepul</td><td>Real-time websocket server</td></tr>
</table>
<p>GitHub Pages — frontend uchun mukammal. Backend kerak bo'lsa — keyingi kurslar (Python Flask, Node) buni qoplaydi.</p>

<h3>🎓 CAPSTONE topshiriq</h3>
<p>"About me" sahifa yarating va GitHub Pages'ga joylang. Minimum talablar:</p>
<ul>
<li>Sarlavha (ism) + 1 abzats tanishuv</li>
<li>2 ta ro'yxat: hozir o'rganayotganlaringiz, kelajak maqsadlar</li>
<li>Aloqa havolalari (Telegram, email, GitHub)</li>
<li>O'z CSS dizayningiz — kamida rang va shrift tanlangan</li>
<li>Mobile'da yaxshi ko'rinadi (<code>viewport</code> meta tegi va max-width)</li>
<li>Real publik URL: <code>https://SIZNING-USERNAME.github.io/...</code></li>
</ul>
<p>O'qituvchiga URL'ni yuboring → tasdiqlanadi.</p>

<h3>🧭 Keyingi qadam — qaysi kursni tanlay?</h3>
<table>
<tr><th>Agar siz...</th><th>Keyingi kurs</th></tr>
<tr><td>Vizual sahifa va dizaynni sevsangiz</td><td>📘 <strong>HTML CSS</strong> chuqurroq</td></tr>
<tr><td>Saytni jonlantirishni xohlasangiz</td><td>📗 <strong>JavaScript</strong></td></tr>
<tr><td>Universal til va AI yo'lini xohlasangiz</td><td>📕 <strong>Python Asoslari</strong></td></tr>
<tr><td>Backend va veb-ilovalar quring</td><td>📓 <strong>Python Flask</strong></td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>index.html</code> faylini yaratib, brauzerda ochish — server kerak emas</li>
<li>HTML + CSS + JS — 3 texnologiya bir sahifada birga ishlaydi</li>
<li>Fayl nomlari kichik harf, bo'sh joysiz — chunki GitHub Pages = Linux server</li>
<li>GitHub Pages bepul, statik sahifalar uchun</li>
<li>Maxsus repo <code>username.github.io</code> — root URL beradi</li>
<li>Endi sizda dunyo ko'radigan publik URL bor</li>
</ul>

<p>Yo'lda omad! 🚀 Endi haqiqiy o'rganish boshlanadi — har kuni 30 daqiqa, har hafta yangi loyiha.</p>
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
            mc("DevTools'da Network tab nimani ko'rsatadi?",
               ["Brauzer va server o'rtasidagi har bir so'rov va javob",
                "Faqat xato xabarlarini",
                "Faqat tezlik testini",
                "Internet provayder ma'lumotlarini"],
               "A", explanation='Network tab — har bir HTTP so\'rovni real-time ko\'rsatadi: Status, Type, Size, Time.',
               diff="Easy", pts=2),
            mc("Konsolda `fetch(\"https://api.github.com/users/yo'qodam123abc\")` qaytarsa, Status qanday bo'ladi?",
               ["200", "301", "404", "500"],
               "C", hint='Yo\'q foydalanuvchi → server "topilmadi" deydi.',
               explanation='404 = Not Found. Server topa olmadi → 4xx oilasidagi xato (sizning so\'rovingiz xato).',
               diff="Easy", pts=2),
            mc("HTTP method'lar qaysilari mavjud va to'g'ri ishlatiladi?",
               ["GET — ma'lumot olish (sahifa yuklash)",
                "POST — yangi ma'lumot yaratish (forma yuborish)",
                "PUT — mavjud ma'lumotni yangilash",
                "DELETE — o'chirish",
                "RUN — funksiyani ishga tushirish"],
               "A,B,C,D", multi=True,
               explanation='RUN — yo\'q. Asosiy 4 ta: GET, POST, PUT (yoki PATCH), DELETE.',
               diff="Medium", pts=3),
            dd("URL ga kirishdagi qadamlarni to'g'ri tartibda joylang",
               ["Foydalanuvchi google.com yozadi",
                "Brauzer DNS'dan google.com ning IP manzilini so'raydi",
                "DNS IP manzilni qaytaradi (masalan 142.250.180.46)",
                "Brauzer o'sha IP'ga HTTP GET / so'rovini yuboradi",
                "Server HTML, CSS, JS faylarini qaytaradi",
                "Brauzer fayllarni o'qib, sahifani ekranga chiqaradi"],
               diff="Medium", pts=3),
            ti("Konsolda `document.body.style.background = \"red\"` yozsangiz — fon qizil bo'ladi. F5 bosgandan keyin nima uchun yana eski rangga qaytadi?",
               "O'zgarish faqat sizning brauzeringizning operativ xotirasida sodir bo'ldi, "
               "serverda emas. Brauzer sahifani ko'rsatish uchun serverdan HTML/CSS/JS ni yuklab "
               "olib, o'zining xotirasida (DOM) rasm chizadi. Siz o'sha DOM'ga teging — faqat "
               "lokal o'zgarish. F5 bosganingizda brauzer sahifani serverdan qaytadan yuklaydi — "
               "asl HTML/CSS qaytadan keladi, sizning lokal o'zgarishlaringiz tushib qoladi. "
               "Doimiy o'zgarish kerak bo'lsa — serverda saqlanishi kerak (backend), yoki "
               "brauzer'ning localStorage'iga yozish kerak. Bu farq frontend va backend "
               "ajralishining mohiyati: frontend — vaqtinchalik ko'rinish, backend — doimiy haqiqat.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 6, "title": "7-Terminal va Git",
        "text": L7_TEXT, "code": L7_CODE, "lang": "bash",
        "video": "https://youtu.be/RGOj5yH7evk",
        "exercises": [
            mc("Terminalda `pwd` komandasi nima qiladi?",
               ["Joriy ish papkasini ko'rsatadi (print working directory)",
                "Parol o'rnatadi (password)",
                "Fayllarni o'chiradi",
                "Yangi papka yaratadi"],
               "A", explanation="pwd = 'print working directory'. Har terminalda birinchi savol: 'qayerdaman?'",
               diff="Easy", pts=2),
            mc("Lokal o'zgarishni GitHub'da ko'rsatish uchun to'g'ri tartib qaysi?",
               ["edit fayl → git add → git commit → git push",
                "git push → edit fayl → git add → git commit",
                "git commit → git add → edit fayl → git push",
                "edit fayl → git commit → git push (git add kerak emas)"],
               "A", hint='add — "saqlamoqchiman" deyish; commit — snapshot; push — GitHub\'ga jo\'natish.',
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari TO'G'RI Git komandalari?",
               ["git clone URL",
                "git status",
                "git add .",
                "git commit -m \"xabar\"",
                "git delete fayl.txt"],
               "A,B,C,D", multi=True,
               hint='git delete — yo\'q. Faylni o\'chirish: rm fayl.txt va keyin git add yoki git rm fayl.txt.',
               diff="Medium", pts=3),
            dd("GitHub repo'ni klonlab birinchi o'zgarishni qaytarib yuborish qadamlarini tartiblang",
               ["github.com'da repo yaratish (web UI)",
                "Terminalda `git clone https://github.com/.../repo.git`",
                "`cd repo` bilan ichkariga kirish",
                "Faylni yaratish yoki tahrirlash (masalan `echo \"hi\" > hello.txt`)",
                "`git add hello.txt` — stage'ga qo'shish",
                "`git commit -m \"hello qo'shildi\"` — snapshot saqlash",
                "`git push` — GitHub'ga yuborish"],
               diff="Medium", pts=3),
            ti("`git add` va `git commit` nima uchun ALOHIDA bosqichlar? Nima uchun bittada qilmaydi?",
               "Git fayllarni 3 ta zonada saqlaydi: 1) working directory — siz tahrir qilayotgan "
               "joriy fayllar; 2) staging area — keyingi snapshot'ga qo'shmoqchi bo'lgan fayllar; "
               "3) repository — saqlangan snapshotlar tarixi. git add fayl'ni working'dan "
               "staging'ga ko'chiradi; git commit staging'dagi hammasini birgalikda snapshot "
               "qiladi. Bu ajralishning sababi: bitta loyiha ustida ishlayotganda siz bir vaqtning "
               "o'zida 10 ta faylni o'zgartirgan bo'lishingiz mumkin — lekin ulardan faqat 3 tasi "
               "bir-biriga bog'liq va alohida commit'ga loyiq. git add bilan o'sha 3 tasini "
               "tanlaysiz, commit qilasiz, keyin qolganlarini boshqa commit'da yuborasiz. "
               "Bu — git'ning kuchli tomoni: tarixingiz toza va ma'noli bo'ladi, har commit bitta "
               "fikrni anglatadi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 7, "title": "8-Birinchi publik sahifa (CAPSTONE)",
        "text": L8_TEXT, "code": L8_CODE, "lang": "html",
        "video": "https://youtu.be/2MsN8gpT6jY",
        "exercises": [
            mc("`index.html` faylini ish stolida yaratib, ustiga ikki marta bossangiz — nima bo'ladi?",
               ["Brauzer ochiladi va sahifani ko'rsatadi (file:// URL)",
                "Hech narsa — server kerak",
                "Faqat matn muharririda ochiladi",
                "Internet aloqasi tekshiriladi"],
               "A", explanation='Brauzer HTML faylni to\'g\'ridan-to\'g\'ri rasm chiza oladi — server ham, internet ham kerak emas.',
               diff="Easy", pts=2),
            mc("HTML sahifa eng kamida qaysi teglarga ega bo'lishi kerak?",
               ["<!DOCTYPE html>", "<html>", "<head>", "<body>", "<title>"],
               "A,B,C,D,E", multi=True,
               explanation='5 ta ham majburiy minimum: DOCTYPE → html → head (title bilan) → body.',
               diff="Medium", pts=3),
            mc("Repo nomi `aziz.github.io` bo'lsa, GitHub Pages URL'i qanday bo'ladi?",
               ["https://aziz.github.io/",
                "https://github.com/aziz/",
                "https://aziz.github.com/",
                "https://pages.github.io/aziz/"],
               "A", hint='Maxsus repo nomi — root URL beradi (boshqa repo nomlari /repo-nomi/ qo\'shadi).',
               diff="Medium", pts=3),
            dd("Lokal HTML faylni publik GitHub Pages URL'ga aylantirish qadamlarini tartiblang",
               ["Lokal'da `index.html` faylini yaratish va tahrir qilish",
                "Terminalda `git init`, `git add .`, `git commit -m \"...\"`",
                "github.com'da yangi repo yaratish (preferred: username.github.io)",
                "`git remote add origin URL` va `git push -u origin main`",
                "Repo Settings → Pages → branch=main → Save (agar maxsus nom emas bo'lsa)",
                "1-2 daqiqa kutish — yashil banner'da publik URL paydo bo'ladi"],
               diff="Medium", pts=3),
            ti("Lokal'da `index.html` ishladi, GitHub Pages'ga push'dan keyin 404 chiqdi. Nima uchun va qanday topish/tuzatish?",
               "Eng ko'p sabab — fayl nomida katta-kichik harf. Lokal kompyuter (ayniqsa Windows va "
               "macOS default) fayl nomlarida katta-kichikni e'tiborga olmaydi: Index.HTML va "
               "index.html bir xil deb biladi. GitHub Pages — Linux serverda turadi, Linux'da "
               "Index.HTML va index.html — IKKI XIL fayl. Brauzer `https://username.github.io/` "
               "ga kirganda server faqat `index.html` nomli faylni qidiradi — agar Index.HTML "
               "bo'lsa, topa olmay 404 qaytaradi. Yechim: 1) `git mv Index.HTML index.html` "
               "bilan kichik harflarga o'zgartirish; 2) commit + push; 3) brauzerda hard refresh "
               "(Ctrl+Shift+R). Qoida: barcha fayl va papka nomlarini kichik harf + chiziqcha "
               "ko'rinishida (`about-me.html`, `images/`) saqlash. Bu hosil odat butun "
               "professional dasturlash uchun standard.",
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
