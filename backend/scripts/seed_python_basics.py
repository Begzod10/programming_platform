"""Seed the "Python Asoslari" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_python_basics.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: absolute beginners with no programming experience.
Language: Uzbek content with Russian section labels.
Each lesson leads with a hero Mermaid diagram (safe-syntax: quoted labels,
single-word edge labels, no nested brackets/parens, no apostrophes in
subgraph titles).
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
    "title": "Python Asoslari",
    "description": (
        "Dasturlashga umuman tanish bo'lmagan boshlovchilar uchun Python tilining "
        "asoslari: o'zgaruvchilar, sikllar, funksiyalar, ro'yxatlar, lug'atlar, "
        "klasslar va fayllar bilan ishlash. Har bir modul oxirida loyiha."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 240,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 1 — Python bilan tanishish (L1, L2, L3 + R1)
# ═════════════════════════════════════════════════════════════════════════════

L1_TEXT = """\
<h2>Python bilan tanishish</h2>

<pre class="mermaid">
flowchart LR
    F["fayl.py kodi"] -->|python fayl.py| I["Python interpreter"]
    R["REPL python"] -->|interactive| I
    I --> RUN["mashinada bajariladi"]
    RUN --> OUT["natija ekranga"]
    C["# comment"] -.->|skip| I
</pre>

<p><strong>Python</strong> — dunyodagi eng mashhur dasturlash tillaridan biri. U sodda sintaksisi va kuchli imkoniyatlari bilan tanilgan. Python'da siz veb saytlar, mobil ilovalar, sun'iy intellekt modellari, ma'lumotlar tahlili va o'yinlar yarata olasiz.</p>

<h3>Nima uchun Python?</h3>
<ul>
<li><strong>O'qish oson</strong>: kod inglizcha gapga o'xshaydi</li>
<li><strong>Ko'p maqsadli</strong>: AI, web, ma'lumotlar tahlili, avtomatlash</li>
<li><strong>Katta jamoa</strong>: minglab kutubxonalar va o'quv materiallari</li>
<li><strong>Bepul</strong>: ochiq manbali (open source), istalgan platformada ishlaydi</li>
</ul>

<h3>Birinchi dastur — print</h3>
<p>An'anaviy birinchi qadam — ekranga "Salom, dunyo!" chiqarish. Python'da bu juda oson:</p>
<pre><code>print("Salom, dunyo!")</code></pre>
<p>Faylni <code>salom.py</code> nomi bilan saqlang va terminalda ishga tushiring:</p>
<pre><code>python salom.py</code></pre>
<p>Natija:</p>
<pre><code>Salom, dunyo!</code></pre>

<h3>Python'ni ikki rejimda ishlatish mumkin</h3>
<ul>
<li><strong>Fayl rejimi</strong>: kodni <code>.py</code> faylga yozib, <code>python fayl.py</code> orqali ishga tushirish</li>
<li><strong>REPL (interaktiv)</strong>: terminalda <code>python</code> deb yozib, satrma-satr buyruq berish</li>
</ul>
<pre><code>$ python
>>> print("Test")
Test
>>> 2 + 3
5
>>> exit()</code></pre>
<p>REPL — yangi g'oyani tezda sinab ko'rish uchun ajoyib. Lekin haqiqiy loyihalarni faylda yoziladi.</p>

<h3>Izohlar (comments)</h3>
<p><code>#</code> belgisi izoh boshlanishini bildiradi. Python interpreter izohni o'qiydi, lekin bajarmaydi. Izohlar — sizning yoki boshqa dasturchining kodni tushunishi uchun.</p>
<pre><code># Bu izoh — Python uni e'tiborsiz qoldiradi
print("Salom")   # Bu ham izoh, satr oxirida

# Ko'p qatorli izoh uchun har qator boshida # qo'yiladi
# Birinchi qator
# Ikkinchi qator</code></pre>

<h3>print funksiyasining boshqa imkoniyatlari</h3>
<pre><code>print("Salom", "dunyo")          # Ikki argument: "Salom dunyo"
print("Yosh:", 20)                # Matn + son: "Yosh: 20"
print("A", "B", "C", sep="-")     # Ajratuvchi: "A-B-C"
print("Salom", end="!\\n")         # Oxir: "Salom!"</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>Tirnoqsiz matn</strong>: <code>print(Salom)</code> — xato. To'g'risi: <code>print("Salom")</code></li>
<li><strong>Yopilmagan tirnoq</strong>: <code>print("Salom)</code> — SyntaxError</li>
<li><strong>Bosh harf</strong>: <code>Print()</code> emas, <code>print()</code> (Python case-sensitive)</li>
</ul>
"""

L1_CODE = """\
# salom.py — birinchi Python dasturingiz

# Eng oddiy chiqarish
print("Salom, dunyo!")

# Ko'p argumentli print
print("Mening ismim", "Aziz", "va men", 20, "yoshdaman")

# Maxsus ajratuvchi
print("2026", "06", "04", sep="-")

# Yangi satrsiz
print("Birinchi qism, ", end="")
print("ikkinchi qism")

# Matematik amal natijasi
print("2 + 3 =", 2 + 3)
print("10 * 5 =", 10 * 5)

# Bu satr bajarilmaydi — izoh
# print("Bu chiqmaydi")

print("Tabriklaymiz! Birinchi Python dasturingiz ishladi.")
"""


L2_TEXT = """\
<h2>O'zgaruvchilar va ma'lumot turlari</h2>

<pre class="mermaid">
flowchart TB
    I["input from user"] --> S["str type"]
    LIT1["42 literal"] --> N["int type"]
    LIT2["3.14 literal"] --> F["float type"]
    LIT3["True False"] --> B["bool type"]
    LIT4["salom literal"] --> S
    S -->|int x| N
    S -->|float x| F
    N -->|str x| S
    F -->|str x| S
    P["print x"] -->|stdout| OUT["ekranga"]
    T["type x"] -->|class| INFO["turini ko'rsatadi"]
</pre>

<p><strong>O'zgaruvchi (variable)</strong> — qiymatni saqlash uchun nom. Uni qutiga o'xshatish mumkin: nom — qutining yorlig'i, qiymat — qutidagi narsa.</p>

<h3>O'zgaruvchi yaratish</h3>
<pre><code>ism = "Aziz"
yosh = 20
boy = 1.75
talaba = True

print(ism, yosh, boy, talaba)</code></pre>
<p>Python o'zgaruvchini avtomatik ravishda qiymat asosida tushunadi — siz turini ko'rsatmaysiz.</p>

<h3>Asosiy ma'lumot turlari</h3>
<table>
<tr><th>Tur</th><th>Misol</th><th>Tavsif</th></tr>
<tr><td><code>int</code></td><td><code>42</code>, <code>-7</code></td><td>Butun son</td></tr>
<tr><td><code>float</code></td><td><code>3.14</code>, <code>-0.5</code></td><td>Kasr son</td></tr>
<tr><td><code>str</code></td><td><code>"salom"</code></td><td>Matn (string)</td></tr>
<tr><td><code>bool</code></td><td><code>True</code>, <code>False</code></td><td>Mantiqiy qiymat</td></tr>
</table>
<p>Turini bilish uchun <code>type()</code> funksiyasi:</p>
<pre><code>print(type(42))         # &lt;class 'int'&gt;
print(type("salom"))    # &lt;class 'str'&gt;
print(type(3.14))       # &lt;class 'float'&gt;
print(type(True))       # &lt;class 'bool'&gt;</code></pre>

<h3>input — foydalanuvchidan ma'lumot olish</h3>
<p><code>input()</code> foydalanuvchi yozgan narsani string sifatida qaytaradi:</p>
<pre><code>ism = input("Ismingizni kiriting: ")
print("Salom,", ism)</code></pre>
<p><strong>Muhim</strong>: <code>input()</code> har doim <code>str</code> qaytaradi. Sonni kiritmoqchi bo'lsangiz — o'zgartirishingiz kerak.</p>

<h3>Turlar o'rtasida o'tish (type casting)</h3>
<pre><code>matn = input("Yoshingizni kiriting: ")  # str: "20"
yosh = int(matn)                         # int: 20
print(yosh + 5)                          # 25

narx_str = "3.50"
narx = float(narx_str)
print(narx * 2)                          # 7.0

raqam = 42
matn = str(raqam)                        # "42"
print("Raqam:", matn)</code></pre>

<h3>O'zgaruvchi nomi qoidalari</h3>
<ul>
<li>Faqat harf, raqam va <code>_</code> dan iborat: <code>ism</code>, <code>foydalanuvchi_yoshi</code></li>
<li>Raqam bilan boshlanmaydi: ❌ <code>1ism</code>, ✅ <code>ism1</code></li>
<li>Bo'sh joy yo'q: ❌ <code>mening yoshim</code>, ✅ <code>mening_yoshim</code></li>
<li>Python kalit so'zlari ishlatib bo'lmaydi: <code>if</code>, <code>for</code>, <code>class</code>, ...</li>
<li>Katta/kichik harf farqlanadi: <code>Ism</code> va <code>ism</code> — boshqa o'zgaruvchilar</li>
</ul>

<h3>Arifmetik amallar</h3>
<table>
<tr><th>Belgi</th><th>Misol</th><th>Natija</th></tr>
<tr><td><code>+</code></td><td><code>5 + 3</code></td><td>8</td></tr>
<tr><td><code>-</code></td><td><code>5 - 3</code></td><td>2</td></tr>
<tr><td><code>*</code></td><td><code>5 * 3</code></td><td>15</td></tr>
<tr><td><code>/</code></td><td><code>10 / 3</code></td><td>3.333...</td></tr>
<tr><td><code>//</code></td><td><code>10 // 3</code></td><td>3 (butun bo'lish)</td></tr>
<tr><td><code>%</code></td><td><code>10 % 3</code></td><td>1 (qoldiq)</td></tr>
<tr><td><code>**</code></td><td><code>2 ** 5</code></td><td>32 (daraja)</td></tr>
</table>
"""

L2_CODE = """\
# variables.py — o'zgaruvchilar va turlar bilan ishlash

# 4 ta asosiy tur
ism = "Aziz"
yosh = 20
boy = 1.75
talaba = True

print("Tur tekshirish:")
print("ism:", type(ism).__name__)
print("yosh:", type(yosh).__name__)
print("boy:", type(boy).__name__)
print("talaba:", type(talaba).__name__)

# input doim str qaytaradi
print()
yosh_str = input("Yoshingizni kiriting: ")
print("type(yosh_str):", type(yosh_str).__name__)

# Sonni olish uchun int() ishlatamiz
yosh = int(yosh_str)
print("5 yildan keyin:", yosh + 5, "yoshda bo'lasiz")

# Float bilan ishlash
narx = float(input("Mahsulot narxi: "))
soni = int(input("Soni: "))
jami = narx * soni
print(f"Jami: {jami:.2f}")

# Arifmetik amallar
print()
print("10 / 3 =", 10 / 3)
print("10 // 3 =", 10 // 3)
print("10 % 3 =", 10 % 3)
print("2 ** 8 =", 2 ** 8)
"""


L3_TEXT = """\
<h2>Stringlar bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    S["salom dunyo"] -->|upper| U["SALOM DUNYO"]
    S -->|lower| L["salom dunyo"]
    S -->|len| C["uzunlik 11"]
    S -->|split| LST["list: salom, dunyo"]
    S -->|replace o, a| R["salam dunya"]
    S -->|slice 0 to 5| SL["salom"]
    F["f text {ism}"] -->|interpolation| OUT["natija qator"]
    PLUS["a plus b"] -->|concat| AB["ab"]
</pre>

<p><strong>String (qator)</strong> — matn ko'rinishidagi ma'lumot. Python'da stringlarni tirnoq ichida yoziladi: <code>"salom"</code> yoki <code>'salom'</code> — farqi yo'q.</p>

<h3>String yaratish</h3>
<pre><code>ism = "Aziz"
shahar = 'Toshkent'
xabar = "Salom, dunyo!"

# Ko'p qatorli string — uchta tirnoq (triple quote)
murojaat = \"\"\"Hurmatli mijoz,
Sizning so'rovingiz qabul qilindi.
Rahmat.\"\"\"</code></pre>

<h3>String ulash (concatenation)</h3>
<pre><code>ism = "Aziz"
familiya = "Karimov"

# + bilan ulash
toliq = ism + " " + familiya
print(toliq)   # Aziz Karimov

# * bilan takrorlash
chiziq = "-" * 20
print(chiziq)  # --------------------</code></pre>

<h3>f-string — eng qulay usul</h3>
<p>Python 3.6+ da <code>f""</code> orqali o'zgaruvchilarni string ichiga osongina qo'shamiz:</p>
<pre><code>ism = "Aziz"
yosh = 20

# Eski usul (qiyin)
print("Salom, " + ism + "! Sizga " + str(yosh) + " yosh.")

# Yangi usul (oson) — f-string
print(f"Salom, {ism}! Sizga {yosh} yosh.")

# Hatto ifoda yoziladi
print(f"Keyingi yili sizga {yosh + 1} yosh bo'ladi")
print(f"5 * 3 = {5 * 3}")</code></pre>

<h3>String metodlari</h3>
<pre><code>matn = "  Salom Dunyo  "

print(matn.upper())          # "  SALOM DUNYO  "
print(matn.lower())          # "  salom dunyo  "
print(matn.strip())          # "Salom Dunyo"  (bo'sh joylar olib tashlanadi)
print(matn.replace("Dunyo", "Toshkent"))   # "  Salom Toshkent  "
print(len(matn))             # 15 (bo'sh joylar bilan)

s = "olma,banan,uzum"
print(s.split(","))          # ['olma', 'banan', 'uzum']

t = ["a", "b", "c"]
print("-".join(t))           # "a-b-c"</code></pre>

<h3>String indekslash va slicing</h3>
<p>Stringdagi har bir belgi indeksga ega — 0 dan boshlanadi.</p>
<pre><code>matn = "Python"
#       P y t h o n
#       0 1 2 3 4 5
#      -6-5-4-3-2-1

print(matn[0])     # 'P'
print(matn[-1])    # 'n'  (oxiridan)
print(matn[0:3])   # 'Pyt'  (0 dan 3 gacha, 3 kirmaydi)
print(matn[:3])    # 'Pyt'  (boshidan 3 gacha)
print(matn[3:])    # 'hon'  (3 dan oxirgacha)
print(matn[::-1])  # 'nohtyP'  (teskari)</code></pre>

<h3>String ichida qidirish</h3>
<pre><code>matn = "Python — eng yaxshi til"

print("Python" in matn)      # True
print("Java" in matn)        # False
print(matn.startswith("Py")) # True
print(matn.endswith("til"))  # True
print(matn.count("y"))       # 2</code></pre>

<h3>String formatlash (sonlar)</h3>
<pre><code>pi = 3.141592653589

print(f"pi = {pi}")              # 3.141592653589
print(f"pi = {pi:.2f}")          # 3.14   (2 raqamga yaxlitlash)
print(f"pi = {pi:.5f}")          # 3.14159

# Maydon kengligi
for i in range(1, 4):
    print(f"{i:3} kvadrat = {i*i:5}")
# Natija:
#   1 kvadrat =     1
#   2 kvadrat =     4
#   3 kvadrat =     9</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>str va int qo'shish</strong>: <code>"Yosh: " + 20</code> — TypeError. To'g'risi: <code>f"Yosh: {20}"</code> yoki <code>"Yosh: " + str(20)</code></li>
<li><strong>O'zgarmaslik</strong>: string immutable, <code>s[0] = "X"</code> ishlamaydi. <code>s = "X" + s[1:]</code> qiling</li>
<li><strong>Slicing chegarasi</strong>: <code>s[0:3]</code> da 3-indeksdagi belgi <strong>kirmaydi</strong></li>
</ul>
"""

L3_CODE = """\
# strings.py — stringlar bilan ishlash

# String yaratish va ulash
ism = "Aziz"
familiya = "Karimov"
toliq = f"{ism} {familiya}"
print(toliq)

# String metodlari
matn = "  Hello, Python World!  "
print("upper:", matn.upper().strip())
print("lower:", matn.lower().strip())
print("replace:", matn.replace("Python", "Uzbek"))
print("len:", len(matn))

# Slicing
s = "Python dasturlash"
print("s[0]:", s[0])
print("s[-1]:", s[-1])
print("s[0:6]:", s[0:6])
print("s[7:]:", s[7:])
print("teskari:", s[::-1])

# split va join
ozgaruvchilar = "x=10,y=20,z=30"
juftliklar = ozgaruvchilar.split(",")
print("split:", juftliklar)
print("join:", " | ".join(juftliklar))

# Qidirish
xabar = "Python eng yaxshi dasturlash tili"
print("'Python' bormi?", "Python" in xabar)
print("'Java' bormi?", "Java" in xabar)
print("'y' soni:", xabar.count("y"))

# Sonlarni formatlash
pi = 3.141592653589
print(f"pi 2 xona: {pi:.2f}")
print(f"pi 4 xona: {pi:.4f}")

# Foydalanuvchi bilan
ism = input("Ismingiz: ")
print(f"Salom, {ism.strip().title()}!")
"""


R1_TEXT = """\
<h2>Takrorlash: Modul 1 — Print, o'zgaruvchilar, stringlar</h2>

<pre class="mermaid">
flowchart TB
    I1["input son 1"] --> CV1["float type cast"]
    I2["input son 2"] --> CV2["float type cast"]
    I3["input amal"] --> OP["plus minus mul div"]
    CV1 --> CALC["amal bajarish"]
    CV2 --> CALC
    OP --> CALC
    CALC --> FMT["f-string format"]
    FMT --> P["print natija"]
    OP -.->|noma'lum| ERR["Xato xabar"]
    CV1 -.->|matn kirsa| ERR
</pre>

<p>Tabriklaymiz! Siz Python tilining birinchi 3 darsini tugatdingiz. Endi vaqt keldi — uchta darsdagi bilimlarni birlashtirib, birinchi haqiqiy ilovangizni quring: <strong>Oddiy kalkulyator</strong>.</p>

<h3>📋 Modul 1 da nimalarni o'rgandingiz</h3>
<table>
<tr><th>Dars</th><th>Asosiy konsept</th><th>Misol</th></tr>
<tr><td>1</td><td>print + izoh + REPL</td><td><code>print("Salom")</code></td></tr>
<tr><td>2</td><td>O'zgaruvchilar, turlar, input, casting</td><td><code>yosh = int(input())</code></td></tr>
<tr><td>3</td><td>Stringlar, f-string, metodlar, slicing</td><td><code>f"{ism.upper()}"</code></td></tr>
</table>

<h3>🧩 Hammasini birlashtirish</h3>
<p>Real dasturlarda bu 3 ta konsept har doim birga ishlaydi. Oddiy kalkulyator misolida ko'ramiz:</p>
<ol>
<li><strong>print</strong> — foydalanuvchiga ko'rsatma berish: <code>"Birinchi sonni kiriting"</code></li>
<li><strong>input</strong> — javob olish: <code>matn = input(...)</code></li>
<li><strong>casting</strong> — strani songa o'zgartirish: <code>son = float(matn)</code></li>
<li><strong>arifmetika</strong> — amal bajarish: <code>natija = a + b</code></li>
<li><strong>f-string</strong> — chiroyli ko'rsatish: <code>print(f"{a} + {b} = {natija}")</code></li>
</ol>

<h3>⚠️ Modul 1 da eng ko'p uchragan xatolar</h3>
<ul>
<li><strong>input doim str qaytaradi</strong>: <code>yosh = input("Yosh:")</code> + <code>yosh + 5</code> — TypeError. Kasting unutmang.</li>
<li><strong>str va son qo'shish</strong>: <code>"Yosh: " + 20</code> — TypeError. <code>f"Yosh: {20}"</code> ishlating.</li>
<li><strong>Yopilmagan tirnoq</strong>: <code>print("Salom)</code> — SyntaxError. Tirnoqlar juftlik.</li>
<li><strong>Case sensitivity</strong>: <code>Print()</code>, <code>PRINT()</code> ishlamaydi. Faqat <code>print()</code>.</li>
<li><strong>f bilan boshlashni unutish</strong>: <code>"{ism}"</code> — bu shunchaki matn. <code>f"{ism}"</code> — o'rnini bosadi.</li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq ishlaydigan kalkulyator. U bu modulning hamma konseptlarini birgalikda ishlatadi. Birinchi navbatda kodni o'qib chiqing, har bir qatorning vazifasini tushuning. Keyin o'zingiz qaytadan yozing va loyihaga o'ting.</p>
"""

R1_CODE = """\
# kalkulyator.py — Modul 1 takrorlash loyihasi
# print + input + casting + arifmetika + f-string

print("=" * 40)
print("  ODDIY KALKULYATOR")
print("=" * 40)

# 1-dars: print bilan ko'rsatma
# 2-dars: input + casting bilan son olish
matn1 = input("Birinchi sonni kiriting: ")
matn2 = input("Ikkinchi sonni kiriting: ")

# float() — kasr ham qabul qiladi
son1 = float(matn1)
son2 = float(matn2)

# Amalni str ko'rinishida olamiz
amal = input("Amal (+, -, *, /): ").strip()

# Hamma 4 amalni hisoblaymiz
if amal == "+":
    natija = son1 + son2
elif amal == "-":
    natija = son1 - son2
elif amal == "*":
    natija = son1 * son2
elif amal == "/":
    if son2 == 0:
        print("⚠️ Nolga bo'lish mumkin emas")
        exit()
    natija = son1 / son2
else:
    print(f"⚠️ Noma'lum amal: {amal!r}")
    exit()

# 3-dars: f-string bilan chiroyli chiqarish
print()
print("-" * 40)
print(f"  {son1}  {amal}  {son2}  =  {natija:.2f}")
print("-" * 40)
print("Tabriklaymiz, kalkulyator ishladi!")
"""


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 2 — Boshqaruv strukturalari (L4, L5, L6 + R2)
# ═════════════════════════════════════════════════════════════════════════════

L4_TEXT = """\
<h2>Shartli ifodalar — if/elif/else</h2>

<pre class="mermaid">
flowchart TB
    A["bool ifoda"] --> IF["if shart True"]
    IF -->|True| THEN["asosiy blok"]
    IF -->|False| ELIF["elif shart True"]
    ELIF -->|True| EB["elif blok"]
    ELIF -->|False| EL["else blok"]
    THEN --> END["davom"]
    EB --> END
    EL --> END
    LOG["and or not"] -->|murakkab shart| A
</pre>

<p>Hozirgacha dasturlarimiz har doim bir xil ishlagan. Endi <strong>qaror qabul qilishni</strong> o'rganamiz: agar shart bajarilsa — bir narsa, aks holda — boshqa.</p>

<h3>Eng oddiy shart — if</h3>
<pre><code>yosh = int(input("Yoshingiz: "))

if yosh >= 18:
    print("Siz balog'at yoshidasiz")</code></pre>
<p><strong>E'tibor bering</strong>: Python <strong>indentatsiya</strong> (bo'sh joylar bilan ko'chirish) ishlatadi blok belgisi sifatida. Boshqa tillarda <code>{}</code> qavslar ishlatiladi — Python'da 4 ta bo'sh joy.</p>

<h3>if + else — ikki yo'l</h3>
<pre><code>yosh = int(input("Yoshingiz: "))

if yosh >= 18:
    print("Voyaga yetgan")
else:
    print("Voyaga yetmagan")</code></pre>

<h3>if + elif + else — bir nechta yo'l</h3>
<pre><code>baho = int(input("Bahoyingiz (0-100): "))

if baho >= 90:
    print("A — A'lo")
elif baho >= 75:
    print("B — Yaxshi")
elif baho >= 60:
    print("C — Qoniqarli")
elif baho >= 50:
    print("D — Yetarli")
else:
    print("F — Qoniqarsiz")</code></pre>
<p><code>elif</code> — "else if" ning qisqartmasi. Faqat bitta blok ishlaydi — birinchi <code>True</code> bo'lganida.</p>

<h3>Solishtirish operatorlari</h3>
<table>
<tr><th>Belgi</th><th>Ma'no</th><th>Misol</th></tr>
<tr><td><code>==</code></td><td>teng</td><td><code>x == 5</code></td></tr>
<tr><td><code>!=</code></td><td>teng emas</td><td><code>x != 0</code></td></tr>
<tr><td><code>&lt;</code></td><td>kichik</td><td><code>x &lt; 10</code></td></tr>
<tr><td><code>&gt;</code></td><td>katta</td><td><code>x &gt; 10</code></td></tr>
<tr><td><code>&lt;=</code></td><td>kichik yoki teng</td><td><code>x &lt;= 100</code></td></tr>
<tr><td><code>&gt;=</code></td><td>katta yoki teng</td><td><code>x &gt;= 0</code></td></tr>
</table>
<p>⚠️ <strong>Eng ko'p uchragan xato</strong>: <code>=</code> (qiymat berish) va <code>==</code> (solishtirish)ni aralashtirish. <code>if x = 5:</code> — SyntaxError. To'g'risi: <code>if x == 5:</code>.</p>

<h3>Mantiqiy operatorlar — and, or, not</h3>
<pre><code>yosh = 25
shahar = "Toshkent"

# and — ikkalasi ham True bo'lishi kerak
if yosh >= 18 and shahar == "Toshkent":
    print("Voyaga yetgan toshkentlik")

# or — kamida bittasi True bo'lsa yetadi
if shahar == "Toshkent" or shahar == "Samarqand":
    print("Katta shaharda yashayapsiz")

# not — qiymatni teskari qiladi
mehmon = False
if not mehmon:
    print("Siz mehmon emassiz")</code></pre>

<h3>Boolean qiymatlar va "truthy" tushunchasi</h3>
<p>Python'da har qiymat <code>True</code> yoki <code>False</code> deb baholanadi:</p>
<table>
<tr><th>False</th><th>True</th></tr>
<tr><td><code>False</code>, <code>0</code>, <code>0.0</code>, <code>""</code>, <code>None</code>, <code>[]</code>, <code>{}</code></td><td>Qolgan deyarli hamma narsa</td></tr>
</table>
<pre><code>ism = input("Ismingiz: ")
if ism:                  # bo'sh string False, demak boshqasi True
    print(f"Salom, {ism}")
else:
    print("Ism kiritmadingiz")</code></pre>

<h3>Ichki shartlar (nested)</h3>
<pre><code>yosh = 25
foydalanuvchi_id = 42

if foydalanuvchi_id:
    if yosh >= 18:
        print("Ruxsat berildi")
    else:
        print("Yosh kichik")
else:
    print("Login qiling")</code></pre>
<p>3 dan ortiq ichki blok — yomon belgi. Ko'pincha bittada birlashtirsa bo'ladi:</p>
<pre><code>if foydalanuvchi_id and yosh >= 18:
    print("Ruxsat berildi")</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>: ni unutish</strong>: <code>if x &gt; 5</code> — SyntaxError. <code>if x &gt; 5:</code> kerak.</li>
<li><strong>Indentatsiya buzilishi</strong>: blok ichidagi qatorlar bir xil ko'chirilishi kerak (har doim 4 bo'sh joy).</li>
<li><strong>= vs ==</strong>: <code>=</code> qiymat berish, <code>==</code> solishtirish.</li>
<li><strong>Bool natijani solishtirish</strong>: <code>if x == True:</code> — keraksiz. Qisqaroq: <code>if x:</code></li>
</ul>
"""

L4_CODE = """\
# conditions.py — shartli ifodalar

# Yosh va guruh aniqlash
yosh = int(input("Yoshingizni kiriting: "))

if yosh < 0:
    print("Yosh manfiy bo'lmaydi!")
elif yosh < 6:
    print("Bola")
elif yosh < 13:
    print("Maktab yoshi")
elif yosh < 18:
    print("O'smir")
elif yosh < 60:
    print("Voyaga yetgan")
else:
    print("Keksa yosh")

# Mantiqiy operatorlar
print()
shahar = input("Qaysi shaharda yashaysiz? ").strip().title()
ish = input("Ishlaysizmi? (ha/yoq): ").strip().lower()

if yosh >= 18 and ish == "ha":
    print("Siz mustaqil yashaysiz")
elif yosh >= 18 and ish != "ha":
    print("Voyaga yetgan, ammo ish topish kerak")
else:
    print("Hali bola — ota-onaga tayanasiz")

if shahar == "Toshkent" or shahar == "Samarqand" or shahar == "Buxoro":
    print(f"{shahar} — katta shahar!")
else:
    print(f"{shahar} — yaxshi joy")

# Truthy va falsy
print()
foydalanuvchi_nomi = input("Foydalanuvchi nomi (bo'sh qoldirish mumkin): ")
if foydalanuvchi_nomi:
    print(f"Xush kelibsiz, {foydalanuvchi_nomi}!")
else:
    print("Mehmon sifatida kirdingiz")

# Juft-toq tekshirish
son = int(input("Sonni kiriting: "))
if son % 2 == 0:
    print(f"{son} — juft son")
else:
    print(f"{son} — toq son")
"""


L5_TEXT = """\
<h2>Sikllar — for va while</h2>

<pre class="mermaid">
flowchart TB
    F["for i in range 5"] --> B1["body har iter"]
    B1 --> CHK1["yana qoldi"]
    CHK1 -->|yes| B1
    CHK1 -->|no| END["loop tugadi"]
    W["while shart"] --> CHK2["shart True"]
    CHK2 -->|yes| B2["body"]
    B2 -->|break| END
    B2 -->|continue| CHK2
    B2 --> CHK2
    CHK2 -->|no| END
</pre>

<p>Ba'zan bir xil amalni bir necha marta takrorlash kerak: 100 ta foydalanuvchini ro'yxatdan o'tkazish, 1 dan 1000 gacha sonlarni hisoblash, fayldagi har qatorni qayta ishlash. <strong>Sikl (loop)</strong> shu uchun.</p>

<h3>for sikli — ma'lum miqdorda takrorlash</h3>
<pre><code># range(5) → 0, 1, 2, 3, 4
for i in range(5):
    print("i =", i)</code></pre>
<p>Natija:</p>
<pre><code>i = 0
i = 1
i = 2
i = 3
i = 4</code></pre>

<h3>range — son ketma-ketligi</h3>
<table>
<tr><th>Chaqirish</th><th>Natija</th></tr>
<tr><td><code>range(5)</code></td><td>0, 1, 2, 3, 4</td></tr>
<tr><td><code>range(1, 6)</code></td><td>1, 2, 3, 4, 5</td></tr>
<tr><td><code>range(0, 10, 2)</code></td><td>0, 2, 4, 6, 8</td></tr>
<tr><td><code>range(10, 0, -1)</code></td><td>10, 9, 8, ..., 1</td></tr>
</table>

<h3>String yoki list bo'ylab aylanish</h3>
<pre><code>matn = "Python"
for harf in matn:
    print(harf)

mevalar = ["olma", "banan", "uzum"]
for meva in mevalar:
    print(meva)</code></pre>

<h3>while sikli — shart bajarilguncha</h3>
<pre><code>son = 1
while son <= 5:
    print(son)
    son = son + 1</code></pre>
<p>Sikl shart <code>True</code> bo'lguncha takrorlanadi. <strong>Ehtiyot</strong>: shartni o'zgartirishni unutmang — aks holda <strong>cheksiz sikl</strong> (infinite loop) yuz beradi va dastur to'xtamaydi.</p>

<h3>while True + break — foydalanuvchidan kutish</h3>
<pre><code>while True:
    javob = input("Davom etamizmi? (ha/yoq): ")
    if javob == "yoq":
        break  # sikldan chiqish
    print("Davom etyapmiz")
print("Tugadi")</code></pre>

<h3>break va continue</h3>
<ul>
<li><code>break</code> — sikldan butunlay chiqish</li>
<li><code>continue</code> — joriy iteratsiyani o'tkazib yuborish va keyingisiga o'tish</li>
</ul>
<pre><code>for i in range(10):
    if i == 5:
        break       # 0,1,2,3,4 chiqadi va to'xtaydi
    print(i)

for i in range(10):
    if i % 2 == 0:
        continue    # juftlarni o'tkazib yuboradi
    print(i)        # 1, 3, 5, 7, 9</code></pre>

<h3>Nested loops — sikl ichida sikl</h3>
<pre><code># Ko'paytirish jadvali
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} * {j} = {i * j}")
    print("---")</code></pre>

<h3>enumerate — indeks va element birga</h3>
<pre><code>mevalar = ["olma", "banan", "uzum"]
for indeks, meva in enumerate(mevalar):
    print(f"{indeks}: {meva}")
# 0: olma
# 1: banan
# 2: uzum</code></pre>

<h3>Foydali pattern — yig'ish (accumulator)</h3>
<pre><code># 1 dan 100 gacha sonlar yig'indisi
yigindi = 0
for son in range(1, 101):
    yigindi = yigindi + son
print("Yig'indi:", yigindi)  # 5050

# Eng katta sonni topish
sonlar = [3, 7, 2, 9, 4]
eng_katta = sonlar[0]
for son in sonlar:
    if son > eng_katta:
        eng_katta = son
print("Eng katta:", eng_katta)</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>Cheksiz sikl</strong>: <code>while x &lt; 10: print(x)</code> — <code>x</code> hech qachon o'zgarmagani uchun to'xtamaydi. Ctrl+C bilan to'xtating.</li>
<li><strong>range(1, 10) → 10 ham bormi?</strong> Yo'q. <code>range(1, 10)</code> = 1, 2, ..., 9. 10 kirmaydi.</li>
<li><strong>Sikl ichidagi o'zgaruvchini tashqarida ishlatish</strong>: ishlaydi, lekin oxirgi qiymat saqlanadi.</li>
</ul>
"""

L5_CODE = """\
# loops.py — for va while sikllari

# 1. Oddiy for sikli
print("1 dan 5 gacha:")
for i in range(1, 6):
    print(i, end=" ")
print()

# 2. Yig'indi hisoblash
yigindi = 0
for son in range(1, 11):
    yigindi += son
print(f"1+2+...+10 = {yigindi}")

# 3. Ko'paytirish jadvali (5 ga)
print()
print("5 ga ko'paytirish jadvali:")
for i in range(1, 11):
    print(f"5 x {i} = {5 * i}")

# 4. Stringdagi unli harflar sanash
matn = input("Matn kiriting: ")
unlilar = "aeiouAEIOU"
soni = 0
for harf in matn:
    if harf in unlilar:
        soni += 1
print(f"Unli harflar soni: {soni}")

# 5. while bilan menyu
print()
sonlar = []
while True:
    javob = input("Son kiriting (chiqish uchun 'q'): ")
    if javob == "q":
        break
    try:
        sonlar.append(float(javob))
    except ValueError:
        print("Bu son emas, qayta urinib ko'ring")
        continue

if sonlar:
    print(f"Kiritilgan sonlar: {sonlar}")
    print(f"O'rtacha: {sum(sonlar) / len(sonlar):.2f}")
else:
    print("Hech narsa kiritilmadi")
"""


L6_TEXT = """\
<h2>Ro'yxatlar (list) va kortejlar (tuple)</h2>

<pre class="mermaid">
flowchart LR
    L["list: 10, 20, 30"] -->|l[0]| L0["birinchi 10"]
    L -->|l[-1]| LN["oxirgi 30"]
    L -->|l[0:2]| LS["slice: 10, 20"]
    L -->|append 40| L2["10, 20, 30, 40"]
    L -->|pop| L3["element o'chiriladi"]
    L -->|len| C["uzunlik"]
    T["tuple: 1, 2"] -->|immutable| IMM["o'zgarmas"]
    LC["list comp"] -->|x*2 for x in nums| NEW["yangi list"]
</pre>

<p>Bir nechta qiymatni bitta o'zgaruvchida saqlash uchun <strong>list (ro'yxat)</strong> ishlatiladi. List — dasturlashning eng muhim ma'lumot strukturalaridan biri.</p>

<h3>List yaratish</h3>
<pre><code>mevalar = ["olma", "banan", "uzum"]
sonlar = [10, 20, 30, 40, 50]
aralash = [1, "salom", 3.14, True]
bosh = []

print(mevalar)        # ['olma', 'banan', 'uzum']
print(len(mevalar))   # 3</code></pre>

<h3>Indekslash va slicing</h3>
<pre><code>mevalar = ["olma", "banan", "uzum", "shaftoli", "anjir"]
#            0       1        2         3         4
#           -5      -4       -3        -2        -1

print(mevalar[0])      # 'olma'
print(mevalar[-1])     # 'anjir'  (oxiridan)
print(mevalar[1:3])    # ['banan', 'uzum']
print(mevalar[:2])     # ['olma', 'banan']
print(mevalar[2:])     # ['uzum', 'shaftoli', 'anjir']
print(mevalar[::-1])   # teskari tartib</code></pre>

<h3>List o'zgartirish — eng muhim metodlar</h3>
<pre><code>mevalar = ["olma", "banan"]

mevalar.append("uzum")           # oxiriga qo'shish
print(mevalar)                   # ['olma', 'banan', 'uzum']

mevalar.insert(0, "anjir")       # 0-indeksga qo'yish
print(mevalar)                   # ['anjir', 'olma', 'banan', 'uzum']

mevalar.remove("olma")           # qiymat bo'yicha o'chirish
oxirgi = mevalar.pop()           # oxirgini olib tashlash va qaytarish
print("Olib tashlangan:", oxirgi)

mevalar.sort()                   # alifbo tartibida
mevalar.reverse()                # teskari
print(mevalar)

mevalar.clear()                  # hammasini bo'shatish
print(mevalar)                   # []</code></pre>

<h3>List ichida bormi? — in operator</h3>
<pre><code>mevalar = ["olma", "banan", "uzum"]

if "olma" in mevalar:
    print("Bor!")
if "kiwi" not in mevalar:
    print("Yo'q!")</code></pre>

<h3>List bo'ylab aylanish</h3>
<pre><code>narxlar = [5.50, 12.30, 8.75]

# Oddiy
for narx in narxlar:
    print(f"${narx:.2f}")

# Indeks bilan
for i, narx in enumerate(narxlar):
    print(f"{i}. ${narx:.2f}")

# Yig'indi
print("Jami:", sum(narxlar))
print("Eng katta:", max(narxlar))
print("Eng kichik:", min(narxlar))</code></pre>

<h3>List comprehension — qisqa va kuchli</h3>
<pre><code># Klassik usul
kvadratlar = []
for i in range(1, 6):
    kvadratlar.append(i * i)
print(kvadratlar)  # [1, 4, 9, 16, 25]

# List comprehension — bir qatorda
kvadratlar = [i * i for i in range(1, 6)]
print(kvadratlar)  # [1, 4, 9, 16, 25]

# Shart bilan
juftlar = [i for i in range(1, 11) if i % 2 == 0]
print(juftlar)     # [2, 4, 6, 8, 10]

# Stringdagi unlilarni olish
matn = "Python dasturlash"
unlilar_list = [h for h in matn if h in "aeiou"]
print(unlilar_list)  # ['o', 'a', 'u', 'a']</code></pre>

<h3>Tuple — o'zgarmas list</h3>
<p><strong>Tuple</strong> — list ga o'xshaydi, lekin <strong>o'zgartirib bo'lmaydi</strong> (immutable). Doimiy ma'lumotlar uchun ishlatiladi.</p>
<pre><code>nuqta = (3.5, 4.8)         # tuple yaratish
ranglar = ("qizil", "yashil", "ko'k")

print(nuqta[0])            # 3.5
print(len(ranglar))        # 3

# nuqta[0] = 5.0   # ❌ TypeError — o'zgartirib bo'lmaydi

# Unpacking — bir nechta o'zgaruvchiga taqsimlash
x, y = nuqta
print(x, y)                # 3.5 4.8

r, g, b = ranglar
print(r, g, b)             # qizil yashil ko'k</code></pre>

<h3>List vs Tuple — qachon qaysisi?</h3>
<table>
<tr><th>List</th><th>Tuple</th></tr>
<tr><td>O'zgaradi (mutable)</td><td>O'zgarmas (immutable)</td></tr>
<tr><td><code>[1, 2, 3]</code></td><td><code>(1, 2, 3)</code></td></tr>
<tr><td>Ro'yxat, navbat, to'plam</td><td>Koordinata, RGB, doimiy ma'lumot</td></tr>
<tr><td>Sekinroq</td><td>Tezroq</td></tr>
</table>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>Index out of range</strong>: <code>mevalar[10]</code> — agar list 3 elementli bo'lsa.</li>
<li><strong>append vs extend</strong>: <code>a.append([1,2])</code> ichkariga list qo'yadi. <code>a.extend([1,2])</code> elementlarni qo'shadi.</li>
<li><strong>Tuple o'zgartirish</strong>: <code>(1, 2)[0] = 5</code> — TypeError.</li>
<li><strong>List va string aralashtirish</strong>: <code>"abc"[0]</code> = "a" (string), <code>["a","b","c"][0]</code> = "a" (list elementi).</li>
</ul>
"""

L6_CODE = """\
# lists.py — listlar va tuplelar bilan ishlash

# 1. List yaratish va o'zgartirish
mevalar = ["olma", "banan", "uzum"]
print("Boshlang'ich:", mevalar)

mevalar.append("shaftoli")
print("append:", mevalar)

mevalar.insert(0, "anjir")
print("insert(0):", mevalar)

oxirgi = mevalar.pop()
print(f"pop chiqdi: {oxirgi}, qoldi: {mevalar}")

# 2. Slicing
sonlar = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print()
print("sonlar[2:5]:", sonlar[2:5])
print("sonlar[:3]:", sonlar[:3])
print("sonlar[-3:]:", sonlar[-3:])
print("har 2-chi:", sonlar[::2])
print("teskari:", sonlar[::-1])

# 3. Statistika
print()
print(f"Jami: {sum(sonlar)}")
print(f"O'rtacha: {sum(sonlar) / len(sonlar):.2f}")
print(f"Min: {min(sonlar)}, Max: {max(sonlar)}")

# 4. List comprehension
kvadratlar = [x * x for x in range(1, 11)]
print()
print("Kvadratlar:", kvadratlar)

juftlar = [x for x in sonlar if x % 4 == 0]
print("4 ga karralilar:", juftlar)

# 5. Tuple
nuqta = (3.5, 4.8)
x, y = nuqta
print()
print(f"Nuqta: x={x}, y={y}")

# 6. Foydalanuvchi listi
print()
talabalar = []
for _ in range(3):
    ism = input("Talaba ismi: ").strip()
    if ism:
        talabalar.append(ism)

talabalar.sort()
print("Alifbo tartibida:")
for i, t in enumerate(talabalar, start=1):
    print(f"  {i}. {t}")
"""


R2_TEXT = """\
<h2>Takrorlash: Modul 2 — Shartlar, sikllar, listlar</h2>

<pre class="mermaid">
flowchart TB
    ITEMS["items list"] --> M["menu while True"]
    M -->|qoshish| A["input then append"]
    M -->|ochirish| R["input then remove"]
    M -->|korsatish| S["for then print"]
    M -->|saralash| SO["sort or sorted"]
    M -->|chiqish| Q["break"]
    A --> M
    R --> M
    S --> M
    SO --> M
    Q --> END["dastur tugaydi"]
</pre>

<p>Modul 2 da siz shartli ifodalar, sikllar, list va tuple bilan ishlashni o'rgandingiz. Endi bu 3 ta konseptni birga ishlatib, o'z <strong>tovarlar ro'yxati (TODO list)</strong> ilovasini yaratamiz.</p>

<h3>📋 Modul 2 da nimalarni o'rgandingiz</h3>
<table>
<tr><th>Dars</th><th>Asosiy konsept</th><th>Misol</th></tr>
<tr><td>4</td><td>if/elif/else, and/or/not, ==/!=</td><td><code>if x &gt; 0 and y &lt; 10:</code></td></tr>
<tr><td>5</td><td>for/while, range, break/continue</td><td><code>for i in range(10):</code></td></tr>
<tr><td>6</td><td>list, tuple, slicing, comprehension</td><td><code>[x*2 for x in nums]</code></td></tr>
</table>

<h3>🧩 Modul 1 + 2 = haqiqiy ilova</h3>
<p>Endi bizda quyidagi imkoniyatlar bor:</p>
<ol>
<li><strong>Foydalanuvchi bilan muloqot</strong>: <code>input</code>, <code>print</code>, <code>f-string</code> (1-modul)</li>
<li><strong>Qaror qabul qilish</strong>: <code>if/elif/else</code> (4-dars)</li>
<li><strong>Takrorlash</strong>: <code>while True</code> bilan menu (5-dars)</li>
<li><strong>Ma'lumotni saqlash</strong>: <code>list.append</code>, <code>list.remove</code> (6-dars)</li>
</ol>
<p>Bu to'rt narsa birga — interaktiv ilovaning poydevori. Tovarlar ro'yxati, kontakt kitobi, to-do list — hammasi shu shaklda yoziladi.</p>

<h3>🏗 Menu pattern — har bir interaktiv ilovaning poydevori</h3>
<pre><code>tovarlar = []

while True:
    print()
    print("1. Tovar qo'shish")
    print("2. Tovar o'chirish")
    print("3. Hammasini ko'rsatish")
    print("4. Chiqish")
    tanlov = input("Tanlovingiz: ").strip()

    if tanlov == "1":
        # ... qo'shish ...
    elif tanlov == "2":
        # ... o'chirish ...
    elif tanlov == "3":
        # ... ko'rsatish ...
    elif tanlov == "4":
        break
    else:
        print("Noma'lum tanlov")</code></pre>
<p>Bu shakl <strong>juda muhim</strong> — uni eslab qoling. Kelajakda har xil ilovalarga bu pattern asos bo'ladi.</p>

<h3>⚠️ Modul 2 da eng ko'p uchragan xatolar</h3>
<ul>
<li><strong>Sikl ichida o'zgaruvchini o'zgartirishni unutish</strong>: <code>while x &lt; 10:</code> — agar <code>x</code> ichkarida o'zgarmasa, cheksiz sikl.</li>
<li><strong>range() chegarasi</strong>: <code>range(1, 10)</code> da 10 KIRMAYDI. Faqat 1..9.</li>
<li><strong>List o'zgartirish vaqtida aylanish</strong>: <code>for x in lst: lst.remove(x)</code> — xato. Yangi list yarating.</li>
<li><strong>List index xatosi</strong>: bo'sh listdan <code>l[0]</code> olish — IndexError. Avval <code>if l:</code> tekshiring.</li>
<li><strong>Strani solishtirish</strong>: foydalanuvchi javobi katta/kichik harf bo'lishi mumkin. <code>.strip().lower()</code> ishlating.</li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq ishlaydigan tovarlar ro'yxati ilovasi. Birinchi navbatda kodni o'qib chiqing va har qatorni tushuning. Keyin o'zingizning loyihangizni qurishga o'ting — masalan, vazifalar ro'yxati (TODO) yoki kontakt kitobi.</p>
"""

R2_CODE = """\
# tovarlar_royxati.py — Modul 2 takrorlash loyihasi
# Menu pattern + if/elif/else + while + list

tovarlar = []

print("🛒 Tovarlar ro'yxati ilovasi")
print("=" * 40)

while True:
    print()
    print("1. Tovar qo'shish")
    print("2. Tovar o'chirish")
    print("3. Hammasini ko'rsatish")
    print("4. Alifbo tartibida saralash")
    print("5. Qidirish")
    print("6. Chiqish")

    tanlov = input("Tanlov (1-6): ").strip()

    if tanlov == "1":
        nom = input("Tovar nomi: ").strip()
        if not nom:
            print("⚠️ Bo'sh nom bo'lmaydi")
        elif nom.lower() in [t.lower() for t in tovarlar]:
            print(f"⚠️ '{nom}' allaqachon ro'yxatda")
        else:
            tovarlar.append(nom)
            print(f"✅ '{nom}' qo'shildi")

    elif tanlov == "2":
        if not tovarlar:
            print("⚠️ Ro'yxat bo'sh")
            continue
        nom = input("O'chirilsin: ").strip()
        # Case-insensitive remove
        for t in tovarlar:
            if t.lower() == nom.lower():
                tovarlar.remove(t)
                print(f"🗑 '{t}' o'chirildi")
                break
        else:
            print(f"⚠️ '{nom}' topilmadi")

    elif tanlov == "3":
        if not tovarlar:
            print("Ro'yxat bo'sh — birinchi tovarni qo'shing")
        else:
            print(f"\\n📋 Jami {len(tovarlar)} ta tovar:")
            for i, t in enumerate(tovarlar, start=1):
                print(f"  {i}. {t}")

    elif tanlov == "4":
        tovarlar.sort(key=str.lower)
        print("🔤 Alifbo tartibida saralandi")

    elif tanlov == "5":
        if not tovarlar:
            print("Ro'yxat bo'sh")
            continue
        kalit = input("Qidirilsin: ").strip().lower()
        topildi = [t for t in tovarlar if kalit in t.lower()]
        if topildi:
            print(f"🔍 {len(topildi)} ta natija:")
            for t in topildi:
                print(f"  • {t}")
        else:
            print(f"'{kalit}' uchun hech narsa topilmadi")

    elif tanlov == "6":
        print(f"\\nYakuniy ro'yxat ({len(tovarlar)} ta): {tovarlar}")
        print("Xayr!")
        break

    else:
        print(f"⚠️ Noma'lum tanlov: {tanlov!r}")
"""


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 3 — Funksiyalar, lug'atlar, modullar (L7, L8, L9 + R3)
# ═════════════════════════════════════════════════════════════════════════════

L7_TEXT = """\
<h2>Funksiyalar — def, return, parametrlar</h2>

<pre class="mermaid">
flowchart LR
    D["def salom ism"] --> CALL["salom Aziz"]
    CALL -->|args ism=Aziz| BODY["body"]
    BODY --> RET["return qiymat"]
    RET --> VAR["natija o'zgaruvchiga"]
    KW["def f *args **kwargs"] -->|variadic| FLEX["egiluvchan chaqirish"]
    SC["funksiyada local"] -->|hidden| OUT["tashqaridan ko'rinmaydi"]
    DEF["param=default"] -->|optional| OPT["argument bermasa default"]
</pre>

<p>Bir xil kodni qayta-qayta yozish o'rniga uni <strong>funksiya</strong> ichiga joylab, nom berib, kerak bo'lganda chaqirish mumkin. Funksiya — kodni qayta ishlatish uchun eng asosiy vosita.</p>

<h3>Funksiya yaratish — def</h3>
<pre><code>def salomlash():
    print("Salom!")
    print("Xush kelibsiz!")

# Chaqirish
salomlash()
salomlash()
salomlash()</code></pre>
<p><code>def</code> — funksiyani aniqlash kalit so'zi. Funksiya nomi keladi, qavslar (ehtimol parametrlar) va <code>:</code>. Ichidagi blok 4 bo'sh joy bilan ko'chiriladi.</p>

<h3>Parametrlar — kirish qiymatlari</h3>
<pre><code>def salomlash(ism):
    print(f"Salom, {ism}!")

salomlash("Aziz")
salomlash("Madina")
salomlash("Bobur")</code></pre>
<p><code>ism</code> — parametr. Chaqirilganda berilgan qiymat (argument) parametrga taqsimlanadi.</p>

<h3>Bir nechta parametr</h3>
<pre><code>def yigindi(a, b):
    natija = a + b
    print(f"{a} + {b} = {natija}")

yigindi(3, 5)        # 3 + 5 = 8
yigindi(10, 20)      # 10 + 20 = 30
yigindi(b=5, a=3)    # nomli argumentlar (kwargs)</code></pre>

<h3>return — qiymat qaytarish</h3>
<p>Funksiya natija qaytarishi mumkin. Bu juda muhim — print bilan farq qiladi.</p>
<pre><code>def kvadrat(x):
    return x * x

natija = kvadrat(5)      # natija = 25
print(natija)            # 25

print(kvadrat(7) + 10)   # 49 + 10 = 59</code></pre>
<p><strong>print vs return</strong>:</p>
<ul>
<li><code>print(...)</code> — ekranga chiqaradi, qiymat qaytarmaydi</li>
<li><code>return ...</code> — qiymatni chaqiruvchiga qaytaradi, ekranga chiqarmaydi</li>
</ul>

<h3>Default qiymat</h3>
<pre><code>def salomlash(ism, til="o'zbek"):
    if til == "ingliz":
        print(f"Hello, {ism}!")
    elif til == "rus":
        print(f"Привет, {ism}!")
    else:
        print(f"Salom, {ism}!")

salomlash("Aziz")                  # Salom, Aziz!
salomlash("Aziz", "ingliz")        # Hello, Aziz!
salomlash("Aziz", til="rus")       # Привет, Aziz!</code></pre>

<h3>*args va **kwargs — har qancha argument</h3>
<pre><code># *args — istalgan miqdordagi pozitsion argument (tuple)
def yigindi(*sonlar):
    return sum(sonlar)

print(yigindi(1, 2))                # 3
print(yigindi(1, 2, 3, 4, 5))       # 15

# **kwargs — istalgan miqdordagi nomli argument (dict)
def malumot(**details):
    for kalit, qiymat in details.items():
        print(f"{kalit}: {qiymat}")

malumot(ism="Aziz", yosh=20, shahar="Toshkent")</code></pre>

<h3>Scope — local va global</h3>
<pre><code>narx = 100   # global o'zgaruvchi

def hisoblash():
    narx = 50    # local — faqat shu funksiya ichida
    print("Local:", narx)

hisoblash()           # Local: 50
print("Global:", narx)  # Global: 100</code></pre>
<p>Funksiya ichida yaratilgan o'zgaruvchi tashqarida ko'rinmaydi. Tashqaridagi o'zgaruvchini funksiya O'QIY oladi, lekin uni o'zgartirish uchun <code>global</code> kerak (kam ishlatiladi).</p>

<h3>Docstring — funksiya tavsifi</h3>
<pre><code>def kvadrat(x):
    \"\"\"Sonni kvadratga ko'taradi.

    Args:
        x: butun yoki kasr son

    Returns:
        x ning kvadrati (x * x)
    \"\"\"
    return x * x

print(kvadrat.__doc__)
help(kvadrat)</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>def da : ni unutish</strong>: <code>def salom()</code> — SyntaxError. <code>def salom():</code></li>
<li><strong>return ni unutish</strong>: <code>def kvadrat(x): x * x</code> — None qaytaradi.</li>
<li><strong>Funksiyani chaqirmaslik</strong>: <code>salomlash</code> bu funksiya obyekti, <code>salomlash()</code> — chaqirish.</li>
<li><strong>print va return ni aralashtirish</strong>: <code>print(kvadrat(5))</code> — 25. Agar <code>kvadrat</code> ichida print bo'lsa, ikkita 25 chiqadi.</li>
<li><strong>Mutable default argument</strong>: <code>def f(x=[]):</code> — anti-pattern, chaqiruvlar orasida bir xil list ulashiladi.</li>
</ul>
"""

L7_CODE = """\
# functions.py — funksiyalar bilan ishlash

def salomlash(ism, til="o'zbek"):
    \"\"\"Foydalanuvchini turli tillarda salomlaydi.\"\"\"
    salomlar = {
        "o'zbek": f"Salom, {ism}!",
        "ingliz": f"Hello, {ism}!",
        "rus": f"Privet, {ism}!",
    }
    return salomlar.get(til, salomlar["o'zbek"])


def kvadrat(x):
    return x * x


def yigindi(*sonlar):
    \"\"\"Istalgan miqdordagi sonni qo'shadi.\"\"\"
    return sum(sonlar)


def malumot(**details):
    print("─" * 30)
    for kalit, qiymat in details.items():
        print(f"  {kalit:>10}: {qiymat}")
    print("─" * 30)


def juftmi(son):
    return son % 2 == 0


def eng_katta(*sonlar):
    if not sonlar:
        return None
    katta = sonlar[0]
    for s in sonlar[1:]:
        if s > katta:
            katta = s
    return katta


# Funksiyalarni sinash
print(salomlash("Aziz"))
print(salomlash("Aziz", "ingliz"))
print(salomlash("Aziz", til="rus"))

print()
print("kvadrat(5) =", kvadrat(5))
print("kvadrat(7) + 10 =", kvadrat(7) + 10)

print()
print("yigindi(1,2,3) =", yigindi(1, 2, 3))
print("yigindi(1,2,...,10) =", yigindi(*range(1, 11)))

print()
malumot(ism="Aziz", yosh=20, shahar="Toshkent", kasb="talaba")

print()
print("juftmi(4):", juftmi(4))
print("juftmi(7):", juftmi(7))

print()
print("eng_katta(3,7,2,9,4) =", eng_katta(3, 7, 2, 9, 4))
"""


L8_TEXT = """\
<h2>Lug'atlar (dict) va to'plamlar (set)</h2>

<pre class="mermaid">
flowchart TB
    D["dict name=Aziz age=20"] -->|d name| V["Aziz"]
    D -->|d.get email| N["None default"]
    D -->|d.keys| K["dict_keys"]
    D -->|d.items| IT["pair iter"]
    D -->|d.values| VV["dict_values"]
    S["set 1 2 3"] -->|unique| UN["no duplicate"]
    S -->|s.add 4| S2["1 2 3 4"]
    S -->|union intersect| OP["set ops"]
    L["list to set"] -->|set| DEDUP["takrorsiz"]
</pre>

<p>List indeksli ma'lumotlar uchun. Lekin agar siz <strong>kalit (key) bo'yicha</strong> ma'lumot izlamoqchi bo'lsangiz — masalan, "Azizning yoshi qancha?" — <strong>lug'at (dict)</strong> kerak.</p>

<h3>Dict yaratish</h3>
<pre><code>foydalanuvchi = {
    "ism": "Aziz",
    "yosh": 20,
    "shahar": "Toshkent",
    "talaba": True
}

print(foydalanuvchi["ism"])     # Aziz
print(foydalanuvchi["yosh"])    # 20</code></pre>

<h3>Qiymatni xavfsiz olish — get()</h3>
<pre><code># Agar kalit yo'q bo'lsa — KeyError
# print(foydalanuvchi["email"])    # ❌ KeyError

# get() — None yoki default qaytaradi
print(foydalanuvchi.get("email"))               # None
print(foydalanuvchi.get("email", "yo'q"))       # yo'q</code></pre>

<h3>Qiymat o'zgartirish va qo'shish</h3>
<pre><code>foydalanuvchi["yosh"] = 21                  # mavjud kalit — o'zgartiradi
foydalanuvchi["email"] = "aziz@example.com" # yangi kalit — qo'shadi
print(foydalanuvchi)

del foydalanuvchi["talaba"]                 # kalitni o'chirish
qiymat = foydalanuvchi.pop("shahar")        # o'chirib qiymatni qaytarish</code></pre>

<h3>Dict bo'ylab aylanish</h3>
<pre><code># Faqat kalitlar
for kalit in foydalanuvchi:
    print(kalit)

# Kalit + qiymat
for kalit, qiymat in foydalanuvchi.items():
    print(f"{kalit}: {qiymat}")

# Faqat qiymatlar
for q in foydalanuvchi.values():
    print(q)</code></pre>

<h3>Dict ichida list yoki dict — ko'pinchamiqdor</h3>
<pre><code>talabalar = {
    "Aziz": {"yosh": 20, "kurs": 2},
    "Madina": {"yosh": 19, "kurs": 1},
    "Bobur": {"yosh": 21, "kurs": 3},
}

print(talabalar["Aziz"]["yosh"])    # 20
talabalar["Aziz"]["kurs"] = 3       # o'zgartirish

# Yangi talaba
talabalar["Karim"] = {"yosh": 18, "kurs": 1}

for ism, data in talabalar.items():
    print(f"{ism}: {data['yosh']} yosh, {data['kurs']}-kurs")</code></pre>

<h3>Dict comprehension</h3>
<pre><code># Sonlar va ularning kvadratlari
kvadratlar = {n: n*n for n in range(1, 6)}
print(kvadratlar)   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Filtr bilan
narxlar = {"olma": 5000, "banan": 12000, "uzum": 30000}
qimmat = {nom: narx for nom, narx in narxlar.items() if narx > 10000}
print(qimmat)       # {'banan': 12000, 'uzum': 30000}</code></pre>

<h3>Set (to'plam) — takrorsiz qiymatlar</h3>
<p><strong>Set</strong> — tartibsiz, takrorlanmaydigan qiymatlar to'plami.</p>
<pre><code>ranglar = {"qizil", "yashil", "ko'k"}
print(ranglar)

# Takrorlangan qiymatlar yo'qoladi
sonlar = {1, 2, 2, 3, 3, 3, 4}
print(sonlar)       # {1, 2, 3, 4}

# Listdan takrorlarni olib tashlash
xom = [1, 2, 2, 3, 3, 4, 4, 4, 5]
toza = list(set(xom))
print(toza)         # [1, 2, 3, 4, 5]</code></pre>

<h3>Set amallari — union, intersection, difference</h3>
<pre><code>a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)        # birlashma: {1, 2, 3, 4, 5, 6}
print(a & b)        # kesishma: {3, 4}
print(a - b)        # ayirma:   {1, 2}
print(a ^ b)        # simmetrik ayirma: {1, 2, 5, 6}

# bormi?
print(3 in a)       # True
print(10 in a)      # False</code></pre>

<h3>Set metodlari</h3>
<pre><code>s = {1, 2, 3}
s.add(4)             # qo'shish
s.remove(2)          # o'chirish (yo'q bo'lsa KeyError)
s.discard(99)        # o'chirish (yo'q bo'lsa xato bermaydi)
print(s)             # {1, 3, 4}</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>KeyError</strong>: <code>d["yoq_kalit"]</code> — <code>d.get("yoq_kalit")</code> ishlating.</li>
<li><strong>Dict tartibsiz emas</strong>: Python 3.7+ dan boshlab kiritish tartibi saqlanadi.</li>
<li><strong>Set indekslash yo'q</strong>: <code>s[0]</code> ishlamaydi — set tartibsiz.</li>
<li><strong>{} bu dict, set emas</strong>: bo'sh dict — <code>{}</code>, bo'sh set — <code>set()</code>.</li>
</ul>
"""

L8_CODE = """\
# dicts_sets.py — lug'atlar va to'plamlar

# 1. Lug'at yaratish va ishlatish
foydalanuvchi = {
    "ism": "Aziz",
    "yosh": 20,
    "shahar": "Toshkent",
}

print("get('email'):", foydalanuvchi.get("email", "ko'rsatilmagan"))
foydalanuvchi["email"] = "aziz@example.com"
print("Email qo'shildi:", foydalanuvchi["email"])

print()
for kalit, qiymat in foydalanuvchi.items():
    print(f"  {kalit:>10}: {qiymat}")

# 2. Talabalar bazasi (dict ichida dict)
print()
talabalar = {
    "T001": {"ism": "Aziz", "yosh": 20, "baho": 87},
    "T002": {"ism": "Madina", "yosh": 19, "baho": 92},
    "T003": {"ism": "Bobur", "yosh": 21, "baho": 78},
}

# Eng yuqori bahoni topish
eng_yuqori_id = max(talabalar, key=lambda k: talabalar[k]["baho"])
eng_yuqori = talabalar[eng_yuqori_id]
print(f"🏆 Eng yuqori baho: {eng_yuqori['ism']} ({eng_yuqori['baho']})")

# O'rtacha baho
bahlar = [t["baho"] for t in talabalar.values()]
print(f"📊 O'rtacha baho: {sum(bahlar) / len(bahlar):.1f}")

# 3. Dict comprehension — narx 10% chegirma
print()
narxlar = {"olma": 5000, "banan": 12000, "uzum": 30000}
chegirma = {nom: narx * 0.9 for nom, narx in narxlar.items()}
print("Asl narxlar:", narxlar)
print("10% chegirma:", chegirma)

# 4. Set — takrorlarni olib tashlash
print()
xabarlar = ["salom", "rahmat", "salom", "xayr", "rahmat", "salom"]
unik = set(xabarlar)
print(f"Asl: {len(xabarlar)} ta, unik: {len(unik)} ta")
print("Unik xabarlar:", unik)

# Har xabar nechtadan?
hisob = {}
for x in xabarlar:
    hisob[x] = hisob.get(x, 0) + 1
print("Hisob:", hisob)

# 5. Set amallari
print()
guruh_A = {"Aziz", "Bobur", "Madina"}
guruh_B = {"Madina", "Karim", "Bobur"}
print("Birikkan:", guruh_A | guruh_B)
print("Ikkalasida:", guruh_A & guruh_B)
print("Faqat A da:", guruh_A - guruh_B)
"""


L9_TEXT = """\
<h2>Modullar va paketlar — import</h2>

<pre class="mermaid">
flowchart LR
    STD["Standard library"] --> M1["math"]
    STD --> M2["random"]
    STD --> M3["os"]
    STD --> M4["datetime"]
    USR["sizning kod"] -->|import paket| F["from math import sqrt"]
    USR -->|alias| AL["import numpy as np"]
    PIP["pip install paket"] --> EXT["external paketlar"]
    F --> CODE["asosiy kod"]
    EXT --> CODE
    OWN["myutils.py"] -->|import myutils| CODE
</pre>

<p>Python'da har bir <code>.py</code> fayl bu <strong>modul</strong>. Boshqa fayldagi kodni o'z kodingizga olib kelish uchun <code>import</code> ishlatiladi. Python o'z ichida juda katta <strong>standart kutubxona</strong> bilan keladi: matematika, vaqt, fayl tizimi, tasodifiy sonlar va boshqa minglab funksiyalar.</p>

<h3>import — eng oddiy usul</h3>
<pre><code>import math

print(math.pi)              # 3.141592653589793
print(math.sqrt(16))        # 4.0
print(math.floor(3.7))      # 3
print(math.ceil(3.2))       # 4</code></pre>

<h3>from ... import — faqat kerakli funksiyalar</h3>
<pre><code>from math import sqrt, pi

print(sqrt(25))    # 5.0
print(pi)          # 3.141592653589793
# math.sqrt — endi kerak emas, to'g'ridan-to'g'ri sqrt</code></pre>

<h3>import ... as — qisqartirish (alias)</h3>
<pre><code>import datetime as dt

bugun = dt.date.today()
print(bugun)</code></pre>

<h3>Standart kutubxonadan eng foydalilari</h3>

<h4>math — matematik funksiyalar</h4>
<pre><code>import math

print(math.sqrt(64))       # 8.0
print(math.pow(2, 10))     # 1024.0
print(math.factorial(5))   # 120
print(math.gcd(12, 18))    # 6 (eng katta umumiy bo'luvchi)
print(math.log(100, 10))   # 2.0
print(math.sin(math.pi/2)) # 1.0</code></pre>

<h4>random — tasodifiy sonlar</h4>
<pre><code>import random

print(random.randint(1, 100))                # 1-100 oralig'ida butun son
print(random.uniform(0, 1))                  # 0-1 oralig'ida float
print(random.choice(["olma", "uzum"]))       # listdan tasodifiy bittasi
random.shuffle([1, 2, 3, 4, 5])              # listni aralashtirish
print(random.sample([1,2,3,4,5,6], k=3))     # 3 ta takrorsiz</code></pre>

<h4>datetime — vaqt va sana</h4>
<pre><code>from datetime import date, datetime, timedelta

bugun = date.today()
print(bugun)                  # 2026-06-04

hozir = datetime.now()
print(hozir)                  # 2026-06-04 17:30:45.123456

# Formatlash
print(hozir.strftime("%Y-%m-%d %H:%M"))  # "2026-06-04 17:30"

# Vaqt qo'shish
keyingi_hafta = bugun + timedelta(days=7)
print(keyingi_hafta)</code></pre>

<h4>os va pathlib — fayl tizimi</h4>
<pre><code>import os
from pathlib import Path

print(os.getcwd())           # joriy papka
print(os.listdir("."))       # papkadagi fayllar

p = Path("data") / "file.txt"   # papka birlashtirish
print(p)                        # data/file.txt
print(p.exists())               # mavjudmi?</code></pre>

<h4>json — JSON bilan ishlash</h4>
<pre><code>import json

# Python obyektini JSON ga
foydalanuvchi = {"ism": "Aziz", "yosh": 20, "ranglar": ["qizil", "ko'k"]}
matn = json.dumps(foydalanuvchi, ensure_ascii=False, indent=2)
print(matn)

# JSON ni Python obyektiga
qaytib = json.loads(matn)
print(qaytib["ism"])</code></pre>

<h3>O'zingizning moduling</h3>
<p>O'zingiz yozgan funksiyalarni alohida fayllarga ajratish mumkin:</p>
<pre><code># utils.py
def kvadrat(x):
    return x * x

def kubik(x):
    return x ** 3</code></pre>
<pre><code># main.py — o'sha papkada
import utils

print(utils.kvadrat(5))     # 25
print(utils.kubik(3))       # 27

# Yoki
from utils import kvadrat
print(kvadrat(7))           # 49</code></pre>

<h3>pip — tashqi paketlar o'rnatish</h3>
<p>Standart kutubxonadan tashqari, Python uchun minglab tashqi paketlar bor: <code>requests</code>, <code>numpy</code>, <code>pandas</code>, <code>django</code>, <code>flask</code>...</p>
<pre><code># Terminal'da
pip install requests
pip install numpy</code></pre>
<pre><code># Kodda
import requests

javob = requests.get("https://api.github.com")
print(javob.status_code)    # 200
print(javob.json())         # JSON natija</code></pre>

<h3>__name__ va if __name__ == "__main__"</h3>
<p>Modul ikki usulda ishlatilishi mumkin: import sifatida yoki to'g'ridan-to'g'ri ishga tushirish (<code>python fayl.py</code>). Bu ikkisini farqlash uchun:</p>
<pre><code># utils.py
def kvadrat(x):
    return x * x

if __name__ == "__main__":
    # Bu kod faqat python utils.py orqali ishga tushganda bajariladi
    # import utils paytida bajarilmaydi
    print("Test:", kvadrat(5))</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>ModuleNotFoundError</strong>: <code>import requests</code> — paket o'rnatilmagan. <code>pip install requests</code> kerak.</li>
<li><strong>Aylanma import</strong>: A modul B ni import qiladi, B esa A ni — ImportError yoki nimagadir None bo'lib qoladi.</li>
<li><strong>from X import *</strong>: anti-pattern, qaysi nomlar import bo'lganini bilmaymiz.</li>
<li><strong>Modul nomi paket bilan to'qnashishi</strong>: <code>math.py</code> fayl yaratmang — standart <code>math</code> ni soyalaydi.</li>
</ul>
"""

L9_CODE = """\
# modules_demo.py — standart kutubxona modullari

import math
import random
from datetime import date, datetime, timedelta
import json

# 1. math — matematika
print("=== math ===")
print(f"pi = {math.pi:.6f}")
print(f"e  = {math.e:.6f}")
print(f"sqrt(2) = {math.sqrt(2):.4f}")
print(f"5! = {math.factorial(5)}")

# Pifagor teoremasi
a, b = 3, 4
c = math.sqrt(a ** 2 + b ** 2)
print(f"a={a}, b={b} -> c = {c}")

# 2. random — tasodif
print()
print("=== random ===")
random.seed(42)  # bir xil natija uchun

print(f"Tasodifiy 1-100: {random.randint(1, 100)}")
print(f"Tasodifiy float 0-1: {random.random():.4f}")

mevalar = ["olma", "banan", "uzum", "shaftoli"]
print(f"Tasodifiy meva: {random.choice(mevalar)}")

random.shuffle(mevalar)
print(f"Aralashtirilgan: {mevalar}")

# 3. datetime — vaqt
print()
print("=== datetime ===")
bugun = date.today()
hozir = datetime.now()
print(f"Bugun: {bugun}")
print(f"Hozir: {hozir.strftime('%Y-%m-%d %H:%M:%S')}")

tugilgan_kun = date(2000, 1, 15)
yashagan_kunlar = (bugun - tugilgan_kun).days
yoshi = yashagan_kunlar // 365
print(f"Tug'ilgandan beri {yashagan_kunlar} kun, taxminan {yoshi} yosh")

keyingi_oy = bugun + timedelta(days=30)
print(f"30 kundan keyin: {keyingi_oy}")

# 4. json — saqlash va o'qish
print()
print("=== json ===")
foydalanuvchi = {
    "ism": "Aziz",
    "yosh": 20,
    "qiziqishlar": ["dasturlash", "musiqa", "sport"],
    "manzil": {"shahar": "Toshkent", "indeks": "100000"},
}

# Python -> JSON string
matn = json.dumps(foydalanuvchi, ensure_ascii=False, indent=2)
print(matn)

# JSON string -> Python
qaytib = json.loads(matn)
print(f"Ism: {qaytib['ism']}, qiziqishlar soni: {len(qaytib['qiziqishlar'])}")

# 5. Random tovar tanlash o'yini
print()
print("=== Tovar tanlash o'yini ===")
tovarlar = {
    "Olma": 5000,
    "Banan": 12000,
    "Uzum": 30000,
    "Shaftoli": 25000,
    "Anjir": 18000,
}

n = random.randint(2, 4)
tanlangan = random.sample(list(tovarlar.keys()), k=n)
jami = sum(tovarlar[t] for t in tanlangan)
print(f"Tanlangan {n} ta tovar: {tanlangan}")
print(f"Jami narx: {jami:,} so'm")
"""


R3_TEXT = """\
<h2>Takrorlash: Modul 3 — Funksiyalar, lug'atlar, modullar</h2>

<pre class="mermaid">
flowchart TB
    DCT["dict words"] --> MENU["menu while"]
    MENU -->|qidirish| S["input then dict get"]
    MENU -->|qoshish| A["input then dict set"]
    MENU -->|ochirish| D["input then del"]
    MENU -->|hammasi| L["for then print"]
    MENU -->|saqlash| SA["json.dump file"]
    MENU -->|yuklash| LO["json.load file"]
    MENU -->|chiqish| Q["break"]
    SA --> END["fayl yangilandi"]
</pre>

<p>Modul 3 da siz funksiyalar, lug'atlar va modullarni o'rgandingiz. Endi bu uchtasini birlashtirib, ma'lumotni faylga saqlovchi <strong>so'zlik (dictionary lookup) ilovasi</strong>ni yaratamiz.</p>

<h3>📋 Modul 3 da nimalarni o'rgandingiz</h3>
<table>
<tr><th>Dars</th><th>Asosiy konsept</th><th>Misol</th></tr>
<tr><td>7</td><td>def, return, parametrlar, *args, **kwargs</td><td><code>def f(a, b=1): return a+b</code></td></tr>
<tr><td>8</td><td>dict, dict.get, items, comprehension, set</td><td><code>d.get('key', default)</code></td></tr>
<tr><td>9</td><td>import, math/random/datetime/json</td><td><code>import json; json.dump(d, f)</code></td></tr>
</table>

<h3>🧩 Hammasini birlashtirish — real ilova</h3>
<ol>
<li><strong>Funksiyalar</strong>: har bir amal alohida funksiya (qo'shish, qidirish, o'chirish, saqlash, yuklash)</li>
<li><strong>Lug'at</strong>: so'zlar va tarjimalarni dict ichida saqlash</li>
<li><strong>Modullar</strong>: <code>json</code> bilan faylga saqlash, <code>os.path</code> bilan fayl mavjudligini tekshirish</li>
</ol>

<h3>🏗 Foydali pattern — fayl bilan ishlash</h3>
<pre><code>import json

FAYL = "sozlik.json"

def yuklash():
    \"\"\"Fayldan dict yuklash. Yo'q bo'lsa — bo'sh dict qaytaradi.\"\"\"
    try:
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def saqlash(data):
    \"\"\"Dict ni JSON ko'rinishida faylga yozish.\"\"\"
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)</code></pre>
<p>Bu shakl — barcha "data persistence" ilovalarining asosi. Bir marta o'rganib oling, har joyda ishlataringiz.</p>

<h3>⚠️ Modul 3 da eng ko'p uchragan xatolar</h3>
<ul>
<li><strong>def da : ni unutish</strong>: <code>def f()</code> emas, <code>def f():</code></li>
<li><strong>return None xato</strong>: <code>def f(x): x*2</code> — None qaytaradi. <code>return x*2</code> yozing.</li>
<li><strong>Dict KeyError</strong>: <code>d["yoq_kalit"]</code> — <code>d.get("yoq_kalit", default)</code> ishlating.</li>
<li><strong>JSON unicode</strong>: <code>json.dump(d, f)</code> kirill harflarni <code>\\u041f</code> ga aylantiradi. <code>ensure_ascii=False</code> qo'shing.</li>
<li><strong>Mutable default</strong>: <code>def f(items=[]):</code> — anti-pattern. Yaxshisi: <code>def f(items=None): if items is None: items = []</code></li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq ishlaydigan so'zlik ilovasi. U fayldan ma'lumot yuklaydi, foydalanuvchi bilan ishlaydi va o'zgartirishlarni qayta faylga saqlaydi. Birinchi navbatda kodni o'qib chiqing va har funksiyaning vazifasini tushuning. Keyin o'z loyihangizga o'ting.</p>
"""

R3_CODE = """\
# sozlik.py — Modul 3 takrorlash loyihasi
# Funksiyalar + dict + json modulasi

import json
import os
from datetime import datetime

FAYL = "sozlik.json"


def yuklash():
    \"\"\"Fayldan so'zlikni o'qish. Yo'q bo'lsa — bo'sh dict.\"\"\"
    if not os.path.exists(FAYL):
        return {}
    try:
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Fayl buzilgan — bo'sh so'zlik yaratildi")
        return {}


def saqlash(sozlik):
    \"\"\"Dict ni JSON ko'rinishida faylga yozish.\"\"\"
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(sozlik, f, ensure_ascii=False, indent=2)


def qoshish(sozlik, sozluz, tarjima):
    sozluz = sozluz.strip().lower()
    if not sozluz or not tarjima.strip():
        return False, "Bo'sh maydon kiritilmadi"
    if sozluz in sozlik:
        return False, f"'{sozluz}' allaqachon bor: {sozlik[sozluz]}"
    sozlik[sozluz] = tarjima.strip()
    return True, f"✅ '{sozluz}' qo'shildi"


def qidirish(sozlik, sozluz):
    return sozlik.get(sozluz.strip().lower())


def ochirish(sozlik, sozluz):
    sozluz = sozluz.strip().lower()
    if sozluz in sozlik:
        del sozlik[sozluz]
        return True
    return False


def hammasi(sozlik):
    if not sozlik:
        return "So'zlik bo'sh"
    qatorlar = [f"📚 Jami {len(sozlik)} ta so'z:"]
    for s, t in sorted(sozlik.items()):
        qatorlar.append(f"  • {s} — {t}")
    return "\\n".join(qatorlar)


def menu():
    sozlik = yuklash()
    print(f"📖 So'zlik ilovasi (boshlang'ich: {len(sozlik)} ta so'z)")

    while True:
        print()
        print("1. Qo'shish")
        print("2. Qidirish")
        print("3. O'chirish")
        print("4. Hammasini ko'rsatish")
        print("5. Chiqish")
        tanlov = input("Tanlov: ").strip()

        if tanlov == "1":
            s = input("So'z (ingliz): ")
            t = input("Tarjima (uzbek): ")
            ok, xabar = qoshish(sozlik, s, t)
            print(xabar)
            if ok:
                saqlash(sozlik)

        elif tanlov == "2":
            s = input("Qidiriladigan so'z: ")
            tarjima = qidirish(sozlik, s)
            if tarjima:
                print(f"🔍 {s.strip().lower()} — {tarjima}")
            else:
                print(f"❌ '{s}' topilmadi")

        elif tanlov == "3":
            s = input("O'chiriladigan so'z: ")
            if ochirish(sozlik, s):
                print(f"🗑 '{s}' o'chirildi")
                saqlash(sozlik)
            else:
                print(f"⚠️ '{s}' topilmadi")

        elif tanlov == "4":
            print(hammasi(sozlik))

        elif tanlov == "5":
            saqlash(sozlik)
            print(f"💾 Faylga {len(sozlik)} ta so'z saqlandi. Xayr!")
            break

        else:
            print("Noma'lum tanlov")


if __name__ == "__main__":
    menu()
"""


# ═════════════════════════════════════════════════════════════════════════════
# MODULE 4 — OOP va fayllar (L10, L11)
# ═════════════════════════════════════════════════════════════════════════════

L10_TEXT = """\
<h2>Klasslar va obyektlar (OOP)</h2>

<pre class="mermaid">
flowchart TB
    C["class Talaba"] --> I["__init__ ism yosh"]
    I -->|self.ism = ism| F["attributes"]
    C --> M1["def salomlash self"]
    C --> M2["def yosh_oshirish self"]
    OBJ["t = Talaba Aziz 20"] -->|instance| O["object"]
    O -->|t.salomlash| RUN["method call"]
    O -->|t.ism| RD["attribute read"]
    P["class TalabaPro Talaba"] -->|inherits| C
    P --> NM["def yangi method"]
</pre>

<p><strong>OOP</strong> (Object-Oriented Programming) — obyektga yo'naltirilgan dasturlash. Bu ma'lumotlar va ular bilan ishlovchi funksiyalarni <strong>bitta obyektga</strong> birlashtirish g'oyasi. Real dunyo obyektlarini kodda modellashtirish uchun ideal.</p>

<h3>Class va Object — farqi</h3>
<ul>
<li><strong>Class (sinf)</strong> — chizma yoki shablon. Masalan, "Talaba" tushunchasi.</li>
<li><strong>Object (obyekt)</strong> — class asosida yaratilgan haqiqiy nusxa. Masalan, "Aziz" yoki "Madina".</li>
</ul>

<h3>Eng oddiy class</h3>
<pre><code>class Talaba:
    pass

# Obyekt yaratish
t = Talaba()
t.ism = "Aziz"
t.yosh = 20

print(t.ism)    # Aziz
print(t.yosh)   # 20</code></pre>

<h3>__init__ — konstruktor</h3>
<p>Har bir obyekt yaratilganda chaqiriladi va boshlang'ich qiymatlarni o'rnatadi.</p>
<pre><code>class Talaba:
    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh

# Yaratish — __init__ avtomatik chaqiriladi
t1 = Talaba("Aziz", 20)
t2 = Talaba("Madina", 19)

print(t1.ism, t1.yosh)   # Aziz 20
print(t2.ism, t2.yosh)   # Madina 19</code></pre>
<p><strong>self</strong> — obyektning o'ziga ishora qiluvchi maxsus parametr. <code>self.ism = ism</code> — "bu obyektning ism atributiga argumentni qo'y".</p>

<h3>Metodlar — funksiyalar class ichida</h3>
<pre><code>class Talaba:
    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh

    def salomlash(self):
        print(f"Salom, men {self.ism}!")

    def yosh_oshirish(self):
        self.yosh += 1

t = Talaba("Aziz", 20)
t.salomlash()            # Salom, men Aziz!
t.yosh_oshirish()
print(t.yosh)            # 21</code></pre>
<p>Har bir metod birinchi parametri <code>self</code> bo'lishi kerak. Bu obyekt o'zining ma'lumotlariga kirish uchun.</p>

<h3>__str__ — obyektni stringga aylantirish</h3>
<pre><code>class Talaba:
    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh

    def __str__(self):
        return f"Talaba({self.ism}, {self.yosh} yosh)"

t = Talaba("Aziz", 20)
print(t)                 # Talaba(Aziz, 20 yosh)
print(str(t))            # Talaba(Aziz, 20 yosh)</code></pre>
<p><code>__str__</code> bo'lmasa <code>print(t)</code> shunday narsa chiqaradi: <code>&lt;__main__.Talaba object at 0x7f...&gt;</code> — foydasiz.</p>

<h3>Inheritance — meros olish</h3>
<p>Bir class ikkinchisi asosida quriladi va uning xususiyatlarini meros oladi.</p>
<pre><code>class Inson:
    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh

    def salomlash(self):
        print(f"Salom, men {self.ism}")


# Talaba — Inson ning bolasi
class Talaba(Inson):
    def __init__(self, ism, yosh, kurs):
        super().__init__(ism, yosh)   # ota class init
        self.kurs = kurs

    def kurs_haqida(self):
        print(f"Men {self.kurs}-kursda o'qiyman")


t = Talaba("Aziz", 20, 2)
t.salomlash()        # Inson dan meros: Salom, men Aziz
t.kurs_haqida()      # O'zining metodi: Men 2-kursda o'qiyman</code></pre>

<h3>Class atribut vs instance atribut</h3>
<pre><code>class Maktab:
    nom = "Toshkent Maktabi"   # class atribut (hamma uchun bir xil)

    def __init__(self, talaba_ism):
        self.talaba_ism = talaba_ism   # instance atribut (har birida boshqa)


m1 = Maktab("Aziz")
m2 = Maktab("Madina")

print(m1.nom, m1.talaba_ism)    # Toshkent Maktabi Aziz
print(m2.nom, m2.talaba_ism)    # Toshkent Maktabi Madina</code></pre>

<h3>Real misol — Kitob class</h3>
<pre><code>class Kitob:
    def __init__(self, sarlavha, muallif, sahifalar, narx):
        self.sarlavha = sarlavha
        self.muallif = muallif
        self.sahifalar = sahifalar
        self.narx = narx
        self.oqilgan = False

    def __str__(self):
        holat = "✅ o'qilgan" if self.oqilgan else "❌ o'qilmagan"
        return f"'{self.sarlavha}' — {self.muallif} ({holat})"

    def oqish(self):
        self.oqilgan = True
        print(f"📖 '{self.sarlavha}' o'qildi!")

    def chegirma(self, foiz):
        \"\"\"Narxga chegirma qo'llaydi va yangi narxni qaytaradi.\"\"\"
        return self.narx * (1 - foiz / 100)


k = Kitob("Avliyo", "Cho'lpon", 250, 50000)
print(k)
k.oqish()
print(k)
print(f"20% chegirma: {k.chegirma(20):,.0f} so'm")</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>self ni unutish</strong>: <code>def salomlash(): ...</code> — TypeError ("missing positional argument"). Doim <code>def salomlash(self):</code>.</li>
<li><strong>__init__ da self.x = x ni unutish</strong>: keyin <code>obj.x</code> AttributeError beradi.</li>
<li><strong>Class va obyekt ni aralashtirish</strong>: <code>Talaba.ism</code> ❌ vs <code>t.ism</code> ✅.</li>
<li><strong>super().__init__ ni unutish</strong>: bola classda ota constructorni chaqirmaslik — ota atributlari bo'lmaydi.</li>
<li><strong>Mutable class atribut</strong>: <code>class A: items = []</code> — barcha obyektlar bir xil listni ulashishadi! Instance atribut qiling.</li>
</ul>
"""

L10_CODE = """\
# classes.py — klasslar va obyektlar bilan ishlash

class Inson:
    \"\"\"Asosiy 'Inson' classi — meros uchun asos.\"\"\"

    def __init__(self, ism, yosh):
        self.ism = ism
        self.yosh = yosh

    def __str__(self):
        return f"{self.ism} ({self.yosh} yosh)"

    def salomlash(self):
        return f"Salom, men {self.ism}"


class Talaba(Inson):
    \"\"\"Inson dan meros olgan Talaba classi.\"\"\"

    def __init__(self, ism, yosh, kurs, bahlar=None):
        super().__init__(ism, yosh)
        self.kurs = kurs
        self.bahlar = bahlar or []

    def __str__(self):
        return f"Talaba {self.ism} ({self.kurs}-kurs)"

    def baho_qoshish(self, baho):
        if 0 <= baho <= 100:
            self.bahlar.append(baho)
            return True
        return False

    def ortacha_baho(self):
        if not self.bahlar:
            return 0
        return sum(self.bahlar) / len(self.bahlar)

    def aloqimi(self):
        return self.ortacha_baho() >= 90


class Oqituvchi(Inson):
    \"\"\"Inson dan meros olgan O'qituvchi classi.\"\"\"

    def __init__(self, ism, yosh, fan, talabalar=None):
        super().__init__(ism, yosh)
        self.fan = fan
        self.talabalar = talabalar or []

    def __str__(self):
        return f"O'qituvchi {self.ism} ({self.fan})"

    def talaba_qoshish(self, talaba):
        self.talabalar.append(talaba)


# Sinash
print("=== Talabalar ===")
t1 = Talaba("Aziz", 20, 2)
t2 = Talaba("Madina", 19, 1)

print(t1)
print(t1.salomlash())   # Inson dan meros olingan metod

# Bahlar qo'shish
for b in [85, 92, 78, 95, 88]:
    t1.baho_qoshish(b)
for b in [95, 98, 92, 96]:
    t2.baho_qoshish(b)

print(f"\\n{t1.ism} bahlari: {t1.bahlar}")
print(f"O'rtacha: {t1.ortacha_baho():.1f}")
print(f"A'lochi: {'Ha' if t1.aloqimi() else 'Yo'q'}")

print(f"\\n{t2.ism} bahlari: {t2.bahlar}")
print(f"O'rtacha: {t2.ortacha_baho():.1f}")
print(f"A'lochi: {'Ha' if t2.aloqimi() else 'Yo'q'}")

# O'qituvchi
print("\\n=== O'qituvchi ===")
o = Oqituvchi("Karim Aliyev", 45, "Matematika")
o.talaba_qoshish(t1)
o.talaba_qoshish(t2)

print(o)
print(f"Talabalar soni: {len(o.talabalar)}")
for t in o.talabalar:
    print(f"  • {t}")
"""


L11_TEXT = """\
<h2>Fayllar va xatolar bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    O["open file.txt"] -->|with as f| F["file object"]
    F -->|f.read| R["string"]
    F -->|f.readlines| LST["list of lines"]
    F -->|f.write| W["yozish"]
    F -->|with auto close| CL["yopiladi"]
    T["try"] --> CODE["xatarli kod"]
    CODE -->|exception| EX["except"]
    EX -->|handle| EH["xato xabar"]
    CODE --> ELSE["else block"]
    ELSE --> FIN["finally har holda"]
    EX --> FIN
</pre>

<p>Ilovangiz yopilgandan keyin ham ma'lumot saqlanib qolishi kerak. Buning eng oddiy yo'li — <strong>faylga yozish</strong>. Va har qanday haqiqiy dasturda kutilmagan vaziyatlar bo'ladi: fayl yo'q, foydalanuvchi noto'g'ri kiritdi, internet uzildi. Buni <strong>xatolarni boshqarish (exception handling)</strong> hal qiladi.</p>

<h3>Fayldan o'qish — open + read</h3>
<pre><code>f = open("xabar.txt", "r", encoding="utf-8")
matn = f.read()
f.close()              # yopish — muhim!
print(matn)</code></pre>
<p><strong>Muammo</strong>: <code>f.close()</code> ni unutish oson. Yaxshi yo'l — <code>with</code> blok:</p>
<pre><code>with open("xabar.txt", "r", encoding="utf-8") as f:
    matn = f.read()
# Bu yerda fayl avtomatik yopiladi
print(matn)</code></pre>

<h3>O'qish rejimlari</h3>
<table>
<tr><th>Rejim</th><th>Ma'no</th></tr>
<tr><td><code>"r"</code></td><td>read — o'qish (default)</td></tr>
<tr><td><code>"w"</code></td><td>write — yozish (faylni o'chiradi)</td></tr>
<tr><td><code>"a"</code></td><td>append — qo'shish (oxiriga)</td></tr>
<tr><td><code>"r+"</code></td><td>o'qish va yozish</td></tr>
<tr><td><code>"rb"</code></td><td>binary read (rasm, fayl)</td></tr>
</table>

<h3>Yozish — write</h3>
<pre><code>with open("hisobot.txt", "w", encoding="utf-8") as f:
    f.write("Hisobot — 2026\\n")
    f.write("=" * 30 + "\\n")
    f.write("Jami foydalanuvchilar: 1247\\n")
    f.write("Faol: 856\\n")

# "w" rejimi mavjud faylni o'chiradi
# "a" — oxiriga qo'shadi
with open("hisobot.txt", "a", encoding="utf-8") as f:
    f.write(f"\\nQo'shimcha qator\\n")</code></pre>

<h3>Qatorma-qator o'qish</h3>
<pre><code># Variant 1: hammasi listga
with open("data.txt", "r", encoding="utf-8") as f:
    qatorlar = f.readlines()
for q in qatorlar:
    print(q.strip())

# Variant 2: bittadan o'qib turish (katta fayl uchun)
with open("data.txt", "r", encoding="utf-8") as f:
    for qator in f:
        print(qator.strip())</code></pre>

<h3>JSON fayl bilan ishlash</h3>
<pre><code>import json

foydalanuvchi = {"ism": "Aziz", "yosh": 20, "qiziqishlar": ["sport", "musiqa"]}

# Saqlash
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(foydalanuvchi, f, ensure_ascii=False, indent=2)

# Yuklash
with open("data.json", "r", encoding="utf-8") as f:
    yuklangan = json.load(f)

print(yuklangan["ism"])</code></pre>

<h3>Xatolar — exceptions</h3>
<p>Dasturda xato yuz berganda Python <strong>exception</strong> chiqaradi va dastur to'xtaydi (agar siz uni boshqarmasangiz).</p>
<pre><code>son = int(input("Son: "))    # Foydalanuvchi "abc" yozsa — ValueError
print(10 / son)              # 0 yozsa — ZeroDivisionError

f = open("yoq_fayl.txt")     # Fayl yo'q — FileNotFoundError</code></pre>

<h3>try / except — xatoni ushlash</h3>
<pre><code>try:
    son = int(input("Son: "))
    natija = 100 / son
    print("Natija:", natija)
except ValueError:
    print("⚠️ Bu son emas")
except ZeroDivisionError:
    print("⚠️ Nolga bo'lish mumkin emas")</code></pre>

<h3>except + else + finally</h3>
<pre><code>try:
    f = open("data.txt", "r")
    matn = f.read()
except FileNotFoundError:
    print("Fayl topilmadi")
else:
    print("Muvaffaqiyatli o'qildi:", len(matn), "belgi")
    f.close()
finally:
    print("Bu har holda chiqadi")</code></pre>
<ul>
<li><code>else</code> — try blokda hech qanday xato bo'lmasa</li>
<li><code>finally</code> — xato bormi-yo'qmi, har holda bajariladi</li>
</ul>

<h3>except Exception as e — xato haqida ma'lumot</h3>
<pre><code>try:
    son = int("abc")
except ValueError as e:
    print(f"Xato xabari: {e}")
    # invalid literal for int() with base 10: 'abc'</code></pre>

<h3>raise — o'z xatongizni chiqarish</h3>
<pre><code>def yosh_tekshirish(yosh):
    if yosh < 0:
        raise ValueError("Yosh manfiy bo'lmaydi")
    if yosh > 150:
        raise ValueError("Yosh 150 dan oshmaydi")
    return yosh

try:
    yosh_tekshirish(-5)
except ValueError as e:
    print(f"⚠️ {e}")</code></pre>

<h3>Real ilova — log fayli</h3>
<pre><code>from datetime import datetime

def log_yozish(xabar, fayl="log.txt"):
    vaqt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(fayl, "a", encoding="utf-8") as f:
        f.write(f"[{vaqt}] {xabar}\\n")

log_yozish("Ilova ishga tushdi")
log_yozish("Foydalanuvchi kirdi: Aziz")
log_yozish("Ilova yopildi")</code></pre>

<h3>⚠️ Eng ko'p uchraydigan xatolar</h3>
<ul>
<li><strong>f.close() unutilgan</strong>: fayl ochiq qoladi. <code>with</code> ishlating.</li>
<li><strong>encoding bermaslik</strong>: kirill harflar buziladi. Doim <code>encoding="utf-8"</code>.</li>
<li><strong>"w" rejimi mavjud faylni o'chiradi</strong>: ehtiyot bo'ling. Qo'shish uchun <code>"a"</code>.</li>
<li><strong>except Exception (juda umumiy)</strong>: aniq exception nomini yozish yaxshiroq.</li>
<li><strong>except: pass</strong>: anti-pattern, xato yashirin qoladi. Hech bo'lmasa <code>log_yozish(str(e))</code>.</li>
</ul>
"""

L11_CODE = """\
# files_errors.py — fayllar va xatolarni boshqarish

import json
from datetime import datetime

LOG_FAYL = "log.txt"
DATA_FAYL = "data.json"


def log_yozish(xabar):
    \"\"\"Log faylga vaqt bilan yozish.\"\"\"
    vaqt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FAYL, "a", encoding="utf-8") as f:
        f.write(f"[{vaqt}] {xabar}\\n")


def yuklash():
    \"\"\"JSON fayldan ma'lumot yuklash, xato bo'lsa bo'sh dict.\"\"\"
    try:
        with open(DATA_FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log_yozish("data.json topilmadi, bo'sh boshlash")
        return {}
    except json.JSONDecodeError as e:
        log_yozish(f"JSON xatosi: {e}")
        return {}


def saqlash(data):
    \"\"\"Ma'lumotni JSON ko'rinishida faylga yozish.\"\"\"
    try:
        with open(DATA_FAYL, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log_yozish(f"Saqlandi: {len(data)} ta yozuv")
        return True
    except OSError as e:
        log_yozish(f"Saqlash xatosi: {e}")
        return False


def son_olish(xabar):
    \"\"\"Foydalanuvchidan son olish, noto'g'ri kiritsa qayta so'rash.\"\"\"
    while True:
        try:
            return int(input(xabar))
        except ValueError:
            print("⚠️ Bu son emas, qayta urinib ko'ring")


def yosh_tekshirish(yosh):
    if yosh < 0:
        raise ValueError("Yosh manfiy bo'lmaydi")
    if yosh > 150:
        raise ValueError("Yosh 150 dan oshmaydi")
    return yosh


# Asosiy oqim
log_yozish("Ilova ishga tushdi")

data = yuklash()
print(f"Yuklandi: {len(data)} ta foydalanuvchi")

ism = input("Ismingiz: ").strip()
if not ism:
    print("⚠️ Ism kerak")
    log_yozish("Bo'sh ism")
else:
    yosh = son_olish("Yoshingiz: ")
    try:
        yosh_tekshirish(yosh)
        data[ism] = {
            "yosh": yosh,
            "qayd_etilgan": datetime.now().isoformat(),
        }
        if saqlash(data):
            print(f"✅ {ism} saqlandi. Jami: {len(data)} ta")
        else:
            print("❌ Saqlash xatosi (log faylni ko'ring)")
    except ValueError as e:
        print(f"⚠️ {e}")
        log_yozish(f"Yosh xatosi: {e}")

log_yozish("Ilova tugadi")
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise builders — identical contract to seed_flask_course.py
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
# Per-lesson assignments
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {  # L1 — Python bilan tanishish
        "title": "Tashrif kartasi (Business card)",
        "description": (
            "O'zingiz haqingizda kichik tashrif kartasini ekranga chiqaruvchi "
            "dastur yozing: ism, yosh, kasb, qiziqishlar va hayotiy maqsadingiz."
        ),
        "requirements": (
            "• Kamida 6 ta print() chaqiruvi\n"
            "• Maxsus belgilar bilan bezatilgan (=, -, *)\n"
            "• Kamida 1 ta sep= yoki end= parametri ishlatilgan\n"
            "• Faylning boshida izoh (komment) bilan dastur tavsifi"
        ),
        "technologies": "Python 3.10+, print, izohlar",
        "deadline_days": 2,
    },
    1: {  # L2 — O'zgaruvchilar
        "title": "Mini-kalkulyator",
        "description": (
            "Foydalanuvchidan ikkita son oluvchi va to'rt asosiy arifmetik amal "
            "natijalarini chiroyli f-string formatida chiqaradigan dastur."
        ),
        "requirements": (
            "• input + casting (int yoki float)\n"
            "• 4 ta amal: +, -, *, / (va 0 ga bo'lishni tekshirish)\n"
            "• Natijalarni f-string bilan formatlash (2 raqamdan keyin yumalash)\n"
            "• type() bilan o'zgaruvchi turini chiqarish"
        ),
        "technologies": "Python, input, type casting, arifmetik amallar, f-string",
        "deadline_days": 3,
    },
    2: {  # L3 — Stringlar
        "title": "Matn tahlilchisi",
        "description": (
            "Foydalanuvchi kiritgan matn haqida statistika chiqaruvchi dastur: "
            "belgilar soni, so'zlar soni, eng uzun so'z, unli/undosh harflar "
            "soni va matnni turli usullarda formatlash."
        ),
        "requirements": (
            "• Kamida 5 ta string metodi ishlatilgan (upper, lower, strip, split, replace ...)\n"
            "• Matn uzunligi va so'zlar soni\n"
            "• Slicing orqali matnning bir qismi chiqariladi (masalan, birinchi 10 belgi)\n"
            "• f-string bilan chiroyli natija\n"
            "• Bo'sh matn holatida xabar"
        ),
        "technologies": "Python, str metodlari, slicing, f-string, len, split",
        "deadline_days": 4,
    },
    3: {  # R1 — Kalkulyator (Module 1 revision)
        "title": "🔁 R1: Kengaytirilgan kalkulyator",
        "description": (
            "Modul 1 takrori: print, input, casting va stringlar birga ishlatilgan "
            "to'liq kalkulyator. Asosiy 4 amaldan tashqari ham foiz, daraja va "
            "kvadrat ildizni hisoblay olsin."
        ),
        "requirements": (
            "• Asosiy amallar: +, -, *, /, //, %, **\n"
            "• Foiz (a dan b foiz)\n"
            "• Kvadrat ildiz (math kerak emas — x ** 0.5)\n"
            "• Foydalanuvchi noto'g'ri kiritsa — aniq xato xabari\n"
            "• 0 ga bo'lish maxsus boshqariladi\n"
            "• Natija chiroyli formatda (2 xonali yaxlitlash)\n"
            "• Bonus: oxirgi 5 ta hisob tarixi (list bilan o'rganmadik — keyin)"
        ),
        "technologies": "Python, input, casting, if/elif, f-string, arifmetik amallar",
        "deadline_days": 5,
    },
    4: {  # L4 — Shartlar
        "title": "Bilet narxi hisoblovchi",
        "description": (
            "Avtobus bileti narxini hisoblovchi dastur. Narx yoshga, kun "
            "(hafta/dam olish), masofaga va talaba statusiga bog'liq."
        ),
        "requirements": (
            "• Yosh: 0-6 bepul, 7-17 yarim narx, 18+ to'liq narx, 60+ 30% chegirma\n"
            "• Hafta oxiri: dam olish kunlari 20% qimmat\n"
            "• Talaba uchun qo'shimcha 15% chegirma\n"
            "• Kamida 4 ta if/elif/else bloki\n"
            "• and / or operatorlari ishlatilgan\n"
            "• Yakuniy narx chiroyli formatda chiqariladi"
        ),
        "technologies": "Python, if/elif/else, mantiqiy operatorlar, input",
        "deadline_days": 4,
    },
    5: {  # L5 — Sikllar
        "title": "Sonlar o'yini",
        "description": (
            "1 dan 100 gacha tasodifiy son tanlovchi va foydalanuvchi uni "
            "topishi kerak bo'lgan o'yin. Har urinishda 'katta' yoki 'kichik' "
            "deb maslahat berib turadi."
        ),
        "requirements": (
            "• random.randint bilan son tanlanadi\n"
            "• while sikli urinishlar uchun (max 10 ta urinish)\n"
            "• Har urinishda 'katta/kichik/to'g'ri' xabari\n"
            "• Foydalanuvchi 'q' yozsa — break\n"
            "• Oxirida nechta urinishda topganini chiqarish\n"
            "• Bonus: 3-4 darajalik qiyinlik (50/100/200 chegara)"
        ),
        "technologies": "Python, while, if, random, break, continue",
        "deadline_days": 4,
    },
    6: {  # L6 — Listlar
        "title": "Talaba bahlari boshqaruvchisi",
        "description": (
            "Talabaning fanlardan olgan bahlarini ro'yxat ko'rinishida saqlovchi "
            "va statistika chiqaruvchi dastur. Bahlar dinamik kiritiladi va list "
            "comprehension hamda statistika funksiyalari ishlatiladi."
        ),
        "requirements": (
            "• Talaba kamida 5 ta baho kiritadi (0-100 oralig'ida)\n"
            "• O'rtacha, eng yuqori, eng past, mediana hisoblanadi\n"
            "• 60 dan kam bahlar 'qoniqarsiz' deb ajratiladi\n"
            "• A'lo bahlar (90+) list comprehension bilan filtrlanadi\n"
            "• Bahlar oshib boruvchi tartibda chiqariladi\n"
            "• Validatsiya: 0-100 oralig'idan tashqari rad etiladi"
        ),
        "technologies": "Python, list, list methods, list comprehension, sum, max, min",
        "deadline_days": 5,
    },
    7: {  # R2 — Tovarlar ro'yxati (Module 2 revision)
        "title": "🔁 R2: Vazifalar ro'yxati (TODO)",
        "description": (
            "Modul 2 takrori: if/while/list birga ishlatilgan vazifalar ro'yxati. "
            "Foydalanuvchi vazifa qo'shadi, bajarilganini belgilaydi, o'chiradi "
            "va statistika ko'radi. Menu pattern asos qilingan."
        ),
        "requirements": (
            "• Menu pattern (while True + tanlovlar)\n"
            "• Vazifa qo'shish (matn va muhimlik darajasi: low/medium/high)\n"
            "• Bajarilganini belgilash (bajarilgan list ga ko'chiriladi)\n"
            "• O'chirish (raqami bo'yicha)\n"
            "• Statistika: jami, bajarilgan, qolgan, bajarish foizi\n"
            "• Saralash: muhimlikka qarab\n"
            "• Bonus: bajarilmagan vazifalarni filtrlash"
        ),
        "technologies": "Python, list, dict in list, while, if/elif, list comprehension",
        "deadline_days": 6,
    },
    8: {  # L7 — Funksiyalar
        "title": "Geometrik kalkulyator",
        "description": (
            "Turli geometrik figuralarning maydoni va perimetrini hisoblovchi "
            "funksiyalar to'plami: kvadrat, to'rtburchak, doira, uchburchak. "
            "Har figura uchun alohida funksiya."
        ),
        "requirements": (
            "• Har figura uchun 2 ta funksiya (maydon va perimetr)\n"
            "• Funksiyalar return ishlatadi (print emas)\n"
            "• Docstring har funksiya uchun yozilgan\n"
            "• Default qiymatlar ishlatilgan (masalan, pi=3.14159)\n"
            "• Asosiy menu funksiyani chaqiradi va natijani f-string bilan chiqaradi\n"
            "• Manfiy o'lcham kiritilsa — xato xabari (raise ValueError ham ishlaydi)"
        ),
        "technologies": "Python, def, return, default arguments, docstrings",
        "deadline_days": 5,
    },
    9: {  # L8 — Lug'atlar
        "title": "Telefon kitobi",
        "description": (
            "Lug'at asosida ishlovchi telefon kitobi. Ism — kalit, telefon "
            "raqami va manzili — qiymat (ichki dict). Qidirish, qo'shish, "
            "o'chirish va eksport qilish imkoniyatlari bilan."
        ),
        "requirements": (
            "• dict ichida dict ({ism: {tel, manzil, email}})\n"
            "• Qo'shish, qidirish (ism yoki tel bo'yicha), o'chirish\n"
            "• Hammasini ko'rsatish (sorted alifbo tartibida)\n"
            "• Statistika (jami nechta kontakt, eng uzun ism)\n"
            "• Set bilan unique shaharlar ro'yxati\n"
            "• Dict comprehension bilan filtrlash (masalan, faqat Toshkentdagi)\n"
            "• Validatsiya: bo'sh ism yoki noto'g'ri tel rad etiladi"
        ),
        "technologies": "Python, dict, set, dict comprehension, sorted, in operator",
        "deadline_days": 6,
    },
    10: {  # L9 — Modullar
        "title": "Tasodifiy parol generatori",
        "description": (
            "random, string va datetime modullari yordamida xavfsiz tasodifiy "
            "parol generatori. Foydalanuvchi parol uzunligini va qaysi belgilarni "
            "ishlatishni tanlaydi."
        ),
        "requirements": (
            "• string.ascii_letters, digits, punctuation ishlatilgan\n"
            "• random.choices yoki random.choice bilan tanlash\n"
            "• Foydalanuvchi tanlovi: uzunlik (8-32), katta harf, raqam, belgi yoq/bor\n"
            "• Kamida 3 ta funksiya (alohida vazifa uchun)\n"
            "• datetime bilan generatsiya vaqtini chiqarish\n"
            "• Bonus: kuchini baholash (kuchsiz/o'rta/kuchli)"
        ),
        "technologies": "Python, random, string, datetime, funksiyalar",
        "deadline_days": 5,
    },
    11: {  # R3 — So'zlik (Module 3 revision)
        "title": "🔁 R3: Ingliz-O'zbek so'zlik",
        "description": (
            "Modul 3 takrori: funksiyalar + lug'at + json moduli birga ishlatilgan "
            "to'liq so'zlik. Ma'lumot faylga saqlanadi, qayta ochilganda yuklanadi. "
            "Bu — Python'da haqiqiy ma'lumot saqlovchi birinchi ilovangiz."
        ),
        "requirements": (
            "• Har asosiy amal alohida funksiya (qo'shish, qidirish, o'chirish, saqlash, yuklash)\n"
            "• Ma'lumot sozlik.json fayliga JSON ko'rinishida saqlanadi\n"
            "• Ilova ochilganda fayldan yuklanadi (yo'q bo'lsa — bo'sh dict)\n"
            "• Kamida 20 ta so'z qo'lda yoki kodda boshlang'ich bo'lib qo'shilgan\n"
            "• Qidirish ham kalit, ham qiymat bo'yicha ishlaydi\n"
            "• Menu pattern\n"
            "• try/except bilan fayl xatolari boshqariladi\n"
            "• Bonus: so'zlar soni statistikasi"
        ),
        "technologies": "Python, dict, def, json, with open, try/except",
        "deadline_days": 6,
    },
    12: {  # L10 — OOP
        "title": "Bank hisobi (Bank Account)",
        "description": (
            "Hisobni boshqarish uchun BankAccount classi. Pul qo'yish, "
            "chiqarish, qoldiqni ko'rish, transfer va tarix imkoniyatlari. "
            "Bu kursning eng murakkab loyihasi — diqqat bilan o'qing."
        ),
        "requirements": (
            "• class BankAccount: __init__ bilan ism, qoldiq=0, tarix=[]\n"
            "• Metodlar: pul_qoyish, pul_chiqarish, qoldiq_korish, transfer\n"
            "• Har amal tarixga (list yoki dict) yozilib boriladi\n"
            "• Salbiy qoldiq mumkin emas (raise ValueError yoki False qaytarish)\n"
            "• __str__ metodi obyektni chiroyli ko'rsatadi\n"
            "• Inheritance: PremiumAccount(BankAccount) — kredit limiti bor\n"
            "• Kamida 3 ta obyekt yaratilib transfer qilingan misol"
        ),
        "technologies": "Python, class, __init__, methods, inheritance, __str__",
        "deadline_days": 7,
    },
    13: {  # L11 — Fayllar va xatolar
        "title": "🚀 CAPSTONE: Kontakt kitobi (fayl bilan)",
        "description": (
            "Kursning yakuniy loyihasi. R2 dagi vazifalar ro'yxati va R3 dagi "
            "so'zlik tajribangizni birlashtirib, faylda saqlanuvchi to'liq "
            "kontakt kitobini OOP yondashuvi bilan quring. Bu — siz Python'da "
            "qila olishingizni isbotlovchi birinchi haqiqiy loyiha."
        ),
        "requirements": (
            "• class Contact (ism, telefon, email, manzil) va class ContactBook\n"
            "• ContactBook metodlari: qoshish, ochirish, qidirish, yangilash, list_all\n"
            "• Ma'lumot kontaktlar.json fayliga saqlanadi (JSON format)\n"
            "• Yuklash funksiyasi try/except bilan barcha xatolarni boshqaradi\n"
            "• log.txt fayliga har amal vaqt bilan yoziladi\n"
            "• Validatsiya: bo'sh ism, noto'g'ri tel rad etiladi (raise + except)\n"
            "• Menu pattern bilan to'liq UI\n"
            "• README.md faylida ishga tushirish va misol screenshot\n"
            "• Bonus: CSV ga eksport (csv moduli)"
        ),
        "technologies": "Python, class, OOP, file I/O, json, try/except, with, datetime",
        "deadline_days": 10,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {
        "order": 0, "title": "1-Python bilan tanishish",
        "text": L1_TEXT, "code": L1_CODE, "lang": "python",
        "video": "https://youtu.be/_uQrJ0TkZlc",
        "exercises": [
            mc("Python qanday turdagi til?",
               ["Frontend uchun stillash tili",
                "Umumiy maqsadli yuqori darajadagi dasturlash tili",
                "Faqat veb saytlar uchun",
                "Operatsion tizim"],
               "B", hint="U AI, web, ma'lumotlar tahlili — har joyda ishlatiladi.",
               diff="Easy", pts=2),
            mc("Salom, dunyo! ni chiqarish uchun qaysi to'g'ri?",
               ["echo('Salom, dunyo!')",
                "print('Salom, dunyo!')",
                "console.log('Salom, dunyo!')",
                "System.out.print('Salom, dunyo!')"],
               "B", diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari Python'da to'g'ri ishlaydi?",
               ["print(\"matn\")",
                "print('matn')",
                "PRINT('matn')",
                "Print('matn')"],
               "A,B", multi=True,
               hint="Python case-sensitive — bosh harf bilan boshlangani ishlamaydi.",
               diff="Medium", pts=3),
            dd("Birinchi Python dasturini ishga tushirish bosqichlarini tartiblang",
               ["Fayl yaratish (salom.py)",
                "Faylga print(\"Salom\") yozish",
                "Saqlash",
                "Terminalda 'python salom.py' bajarish",
                "Ekranda natijani ko'rish"],
               diff="Medium", pts=3),
            ti("Izoh (#) Python uchun nima ahamiyatga ega?",
               "Izoh — # belgisidan boshlanadi va Python uni e'tiborga olmaydi (bajarmaydi). "
               "Izohlar dasturchining o'zi yoki boshqa dasturchilar kodni tushunishi uchun "
               "yoziladi. Yaxshi yozilgan kodda izohlar 'nima' emas, 'nima uchun' degan "
               "savolga javob beradi.",
               hint="Python interpreter # dan keyingi narsani nima qiladi?",
               diff="Hard", pts=4),
            mc("print(\"A\", \"B\", \"C\", sep=\"-\") nima chiqaradi?",
               ["ABC", "A B C", "A-B-C", "A,B,C"],
               "C", hint="sep parametri — ajratuvchi belgi.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 1, "title": "2-O'zgaruvchilar va turlar",
        "text": L2_TEXT, "code": L2_CODE, "lang": "python",
        "video": "https://youtu.be/cQT33yu9pY8",
        "exercises": [
            mc("type(42) nima qaytaradi?",
               ["<class 'str'>", "<class 'int'>", "<class 'float'>", "<class 'number'>"],
               "B", diff="Easy", pts=2),
            mc("input() funksiyasi qaysi turdagi qiymatni qaytaradi?",
               ["int", "float", "str", "bool"],
               "C", hint="Foydalanuvchi 25 yozsa ham — bu raqam emas, matn ko'rinishida keladi.",
               explanation="input() har doim str qaytaradi. Sonni ishlatish uchun int() yoki float() ga o'zgartirish kerak.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari TO'G'RI o'zgaruvchi nomi?",
               ["yosh_1", "_data", "1ism", "user-name", "userName"],
               "A,B,E", multi=True,
               hint="Raqamdan boshlanmaslik va '-' belgisi bo'lmasligi kerak.",
               diff="Medium", pts=3),
            dd("Foydalanuvchi yoshini olib 5 yildan keyingi yoshini hisoblash bosqichlarini tuzing",
               ["matn = input(\"Yoshingiz: \")",
                "yosh = int(matn)",
                "keyingi = yosh + 5",
                "print(f\"5 yildan keyin: {keyingi}\")"],
               diff="Medium", pts=3),
            ti("type casting (turlar orasida o'tish) nima va nima uchun kerak?",
               "Type casting — qiymatni bir turdan boshqasiga o'zgartirish. Masalan, "
               "input() doim str qaytaradi, ammo arifmetik amal uchun int yoki float kerak. "
               "int(matn), float(matn), str(son) — eng ko'p ishlatiladigan kastingiar. "
               "Kasting kerak bo'lmasdan str va son qo'shilsa — TypeError.",
               diff="Hard", pts=4),
            mc("10 // 3 va 10 % 3 natijalari qaysilari?",
               ["3 va 1", "3 va 0", "3.33 va 1", "1 va 3"],
               "A", hint="// — butun bo'lish, % — qoldiq.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 2, "title": "3-Stringlar bilan ishlash",
        "text": L3_TEXT, "code": L3_CODE, "lang": "python",
        "video": "https://youtu.be/iAzShkKzpJo",
        "exercises": [
            mc("\"Python\"[1:4] nima qaytaradi?",
               ["\"Pyt\"", "\"yth\"", "\"ytho\"", "\"Pyth\""],
               "B", hint="Slicing 1 dan boshlanadi va 4 ga yetmaydi. 'P','y','t','h','o','n' — indekslar 0,1,2,3,4,5.",
               diff="Easy", pts=2),
            mc("f-string sintaksisi qaysi biri to'g'ri?",
               ["f\"{ism}\"", "f'{ism}'", "F\"{ism}\"", "string.format(ism)"],
               "A,B,C", multi=True,
               hint="3 ta f-string variant + 1 ta eski usul.",
               diff="Medium", pts=3),
            mc("\"  Salom  \".strip() natijasi qanday?",
               ["\"Salom\"", "\"  Salom  \"", "\"  Salom\"", "\"Salom  \""],
               "A", explanation="strip() ikkala tomondan bo'sh joylarni olib tashlaydi.",
               diff="Easy", pts=2),
            dd("\"olma,banan,uzum\" stringidan list yasash va alifbo tartibida saralash qadamlari",
               ["matn = \"olma,banan,uzum\"",
                "ro_yxat = matn.split(\",\")",
                "ro_yxat.sort()",
                "print(ro_yxat)"],
               diff="Medium", pts=3),
            ti("String immutable degani nima va bu qanday oqibatlarga olib keladi?",
               "Immutable — o'zgarmas. Yaratilgan stringni o'zgartirib bo'lmaydi. "
               "s[0] = \"X\" — TypeError. Stringni 'o'zgartirish' uchun yangi string yaratiladi: "
               "s = \"X\" + s[1:]. Bu xotira tejash va xavfsizlik uchun foydali, ammo katta "
               "stringlar bilan tez-tez ishlasangiz — performance pasayishi mumkin.",
               diff="Hard", pts=4),
            mc("\"Python\".upper() ning natijasi qanday?",
               ["\"PYTHON\"", "\"Python\"", "\"python\"", "\"Python.upper()\""],
               "A", diff="Easy", pts=2),
            mc("f\"pi = {3.14159:.2f}\" qaysi qatorni chiqaradi?",
               ["pi = 3.14", "pi = 3.14159", "pi = 3.2f", "pi = 3.14159f"],
               "A", hint=":.2f — 2 ta o'nlik raqam bilan.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 3, "title": "R1-Kalkulyator (takrorlash)",
        "text": R1_TEXT, "code": R1_CODE, "lang": "python",
        "video": "https://youtu.be/eAd3eDS09kw",
        "exercises": [
            mc("Kalkulyatorda 0 ga bo'lish ehtimolini qanday boshqarish to'g'ri?",
               ["Hech narsa qilmaslik — Python o'zi xato beradi",
                "if son2 == 0: xato xabari chiqarish va exit() qilish",
                "try/except ZeroDivisionError bilan ushlash",
                "print bilan ogohlantirib davom etish"],
               "B,C", multi=True,
               hint="Ikki to'g'ri yondashuv bor — biri proaktiv (if), ikkinchisi reaktiv (try).",
               diff="Medium", pts=3),
            mc("float(\"3.14\") va int(\"3.14\") ning natijasi qanday farq qiladi?",
               ["Ikkalasi ham 3.14 qaytaradi",
                "float() 3.14 qaytaradi, int() ValueError beradi",
                "Ikkalasi ham 3 qaytaradi",
                "float() 3 qaytaradi, int() ValueError beradi"],
               "B", hint="int() faqat butun ko'rinishidagi stringni qabul qiladi.",
               diff="Easy", pts=2),
            dd("Kalkulyator dasturining oqimini tartiblang",
               ["Foydalanuvchidan 2 ta sonni input bilan olish",
                "float() bilan songa o'tkazish",
                "Amal belgisini olish va tekshirish",
                "if/elif bilan tegishli amalni bajarish",
                "f-string bilan natijani chiqarish"],
               diff="Medium", pts=3),
            ti("input() doim str qaytaradi — bu kalkulyatorda nima uchun muammo?",
               "Arifmetik amallarni str ustida bajarib bo'lmaydi. \"5\" + \"3\" — \"53\" "
               "(string concatenation), \"5\" - \"3\" — TypeError. Shuning uchun input dan kelgan "
               "qiymatni avval int() yoki float() bilan songa o'zgartirish kerak. Aks holda "
               "kalkulyator noto'g'ri ishlaydi yoki umuman ishlamaydi.",
               diff="Hard", pts=4),
            mc("f\"{son1} + {son2} = {natija:.2f}\" — bu nima qiladi?",
               ["natija ni 2 raqamga yumalab f-string ko'rinishida chiqaradi",
                "Faqat son1 ni 2 raqamga yumalab chiqaradi",
                "natija ni qator ko'rinishida 2 belgida chiqaradi",
                "Hech narsa qilmaydi — bu noto'g'ri sintaksis"],
               "A", diff="Medium", pts=3),
            ti("Kalkulyatoringizga foiz hisoblash imkoniyatini qanday qo'shgan bo'lardingiz?",
               "Yangi amal sifatida '%' belgisini ajratish kerak — chunki bu Python'da qoldiq. "
               "Foydalanuvchi 'foiz' yoki 'p' belgisini tanlasin. Hisoblash: a dan b foiz = a * b / 100. "
               "if amal == 'p': natija = son1 * son2 / 100. Foydalanuvchiga shu shaklda izoh berish kerak: "
               "'200 sonidan 15 foiz' uchun son1=200, son2=15.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 4, "title": "4-Shartli ifodalar",
        "text": L4_TEXT, "code": L4_CODE, "lang": "python",
        "video": "https://youtu.be/f4KOjWS_KZs",
        "exercises": [
            mc("if shart oxirida nima qo'yiladi?",
               ["; (nuqta-vergul)", ": (ikki nuqta)", ", (vergul)", ". (nuqta)"],
               "B", diff="Easy", pts=2),
            mc("if x == 5 va if x = 5 farqi nima?",
               ["Hech qanday farq yo'q",
                "== solishtirish, = qiymat berish (= ishlatsa SyntaxError)",
                "= solishtirish, == qiymat berish",
                "Ikkalasi ham solishtirish — birinchisi tezroq"],
               "B", hint="Eng ko'p uchraydigan xatolardan biri.",
               diff="Easy", pts=2),
            mc("Quyidagi qiymatlardan qaysilari Python'da Falsy?",
               ["0", "\"\" (bo'sh string)", "None", "[] (bo'sh list)", "\"False\" (matn)"],
               "A,B,C,D", multi=True,
               hint="\"False\" — bu matn, demak truthy. Bo'sh kollektsiyalar — falsy.",
               diff="Medium", pts=3),
            dd("yosh va shahar asosida xabar chiqarish blokini tuzing",
               ["yosh = int(input(\"Yoshingiz: \"))",
                "shahar = input(\"Shahar: \")",
                "if yosh >= 18 and shahar == \"Toshkent\":",
                "    print(\"Voyaga yetgan toshkentlik\")",
                "else:",
                "    print(\"Boshqa toifa\")"],
               diff="Medium", pts=3),
            ti("elif va bir nechta alohida if bloklari orasida qanday farq bor?",
               "elif — biri bajarilsa qolganlari tekshirilmaydi. Faqat bitta blok ishlaydi. "
               "Alohida if bloklarda esa har qaysisi mustaqil tekshiriladi va bir nechtasi "
               "bajarilishi mumkin. elif tezroq va aniqroq: agar bahlar 90+, 75+, 60+ kabi "
               "ketma-ket shartlar bo'lsa, elif kerak. Mustaqil shartlar (yosh>18 VA student=True) "
               "uchun alohida if (yoki and).",
               diff="Hard", pts=4),
            mc("not True or False and True natijasi qanday?",
               ["True", "False", "Xato beradi", "None"],
               "B", hint="not — eng kuchli, keyin and, keyin or. (not True) or (False and True) = False or False = False.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 5, "title": "5-Sikllar (for va while)",
        "text": L5_TEXT, "code": L5_CODE, "lang": "python",
        "video": "https://youtu.be/6iF8Xb7Z3wQ",
        "exercises": [
            mc("range(1, 10) nima qaytaradi?",
               ["1 dan 10 gacha (10 ham kiradi)",
                "1 dan 9 gacha (10 kirmaydi)",
                "0 dan 9 gacha",
                "0 dan 10 gacha"],
               "B", hint="range oxirgi sonni kiritmaydi.",
               diff="Easy", pts=2),
            mc("break va continue farqi nima?",
               ["break sikldan chiqadi, continue joriy iteratsiyani o'tkazib yuboradi",
                "continue sikldan chiqadi, break joriy iteratsiyani o'tkazib yuboradi",
                "Ikkalasi bir narsa qiladi",
                "break faqat for da, continue faqat while da ishlaydi"],
               "A", diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari TO'G'RI for sikli misoli?",
               ["for i in range(5):",
                "for x in [1, 2, 3]:",
                "for harf in \"Python\":",
                "for i in 5:"],
               "A,B,C", multi=True,
               hint="for sikli iterable obyekt bilan ishlaydi. 5 — son, iterable emas.",
               diff="Medium", pts=3),
            dd("1 dan 100 gacha sonlar yig'indisini hisoblash bosqichlarini tartiblang",
               ["yigindi = 0",
                "for son in range(1, 101):",
                "    yigindi = yigindi + son",
                "print(yigindi)"],
               diff="Medium", pts=3),
            ti("Cheksiz sikl (infinite loop) qanday yuz beradi va undan qanday qutulish mumkin?",
               "Cheksiz sikl — shart hech qachon False bo'lmasa yoki break ishga tushmasa. "
               "Misol: while x < 10 da agar x oshmasa, dastur to'xtamaydi. Yo'l: while ichida "
               "shartga ta'sir qiluvchi o'zgaruvchini o'zgartirish (x = x + 1). "
               "Foydalanuvchi menulariga while True + break ishlatish kerak. "
               "Ishlab tushib qolganda Ctrl+C bilan dasturni to'xtatish mumkin.",
               diff="Hard", pts=4),
            mc("enumerate([\"a\", \"b\", \"c\"]) nimani qaytaradi?",
               ["(0, \"a\"), (1, \"b\"), (2, \"c\") juftliklari",
                "[\"a\", \"b\", \"c\"]",
                "0, 1, 2 indekslar",
                "Xato"],
               "A", hint="enumerate indeks va qiymatni birga beradi.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 6, "title": "6-Ro'yxatlar va kortejlar",
        "text": L6_TEXT, "code": L6_CODE, "lang": "python",
        "video": "https://youtu.be/W8KRzm-HUcc",
        "exercises": [
            mc("list va tuple orasidagi asosiy farq nima?",
               ["list o'zgaradi (mutable), tuple o'zgarmas (immutable)",
                "list tezroq, tuple sekinroq",
                "tuple faqat sonlar saqlaydi",
                "Ular bir xil — sintaksis farqi"],
               "A", hint="() o'zgarmas, [] o'zgaradi.",
               diff="Easy", pts=2),
            mc("[1, 2, 3, 4, 5][1:4] nima qaytaradi?",
               ["[1, 2, 3]", "[2, 3, 4]", "[2, 3, 4, 5]", "[1, 2, 3, 4]"],
               "B", hint="Indeks 1 dan 4 gacha, 4 kirmaydi.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari to'g'ri list metodlari?",
               ["append", "insert", "remove", "extend", "delete"],
               "A,B,C,D", multi=True,
               hint="delete — bunday metod yo'q. del keyword bor.",
               diff="Medium", pts=3),
            dd("Listdagi takrorlanmas elementlarni saralangan ko'rinishda chiqarish bosqichlari",
               ["sonlar = [3, 1, 4, 1, 5, 9, 2, 6, 5]",
                "unik = list(set(sonlar))",
                "unik.sort()",
                "print(unik)"],
               diff="Medium", pts=3),
            ti("List comprehension nima va nega oddiy for siklidan yaxshiroq?",
               "List comprehension — bir qatorda yangi list yaratish: [x*2 for x in nums]. "
               "Yaxshilari: 1) qisqaroq va o'qishga oson (idiomatic Python); "
               "2) tezroq (Python ichkarida optimallashtirilgan); "
               "3) shart bilan birga ishlaydi: [x for x in nums if x > 0]. "
               "Lekin agar logika murakkab bo'lsa (nested if/else) — odatdagi for ko'proq tushunarli.",
               diff="Hard", pts=4),
            mc("Tuple o'zgartirib bo'lmagani uchun qachon ishlatiladi?",
               ["Doimiy ma'lumotlar (koordinata, RGB, kun nomlari)",
                "Foydalanuvchi tomonidan o'zgartiriladigan ro'yxat",
                "Faqat sonlarni saqlash",
                "Hech qachon — har doim list yaxshi"],
               "A", diff="Easy", pts=2),
            ti("nuqta = (3, 4); x, y = nuqta — bu nima va nima uchun foydali?",
               "Bu — tuple unpacking. Tuple elementlarini bir nechta o'zgaruvchiga birdaniga "
               "taqsimlash. x = nuqta[0]; y = nuqta[1] o'rniga bitta qatorda yoziladi. "
               "Foydali: koordinata, RGB, funksiyadan bir nechta qiymat qaytarish "
               "(return a, b → tuple sifatida qaytadi va unpack qilinadi). "
               "Eng zo'r ishlatish: for ism, yosh in [(\"Aziz\", 20), (\"Madina\", 19)].",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 7, "title": "R2-Tovarlar ro'yxati (takrorlash)",
        "text": R2_TEXT, "code": R2_CODE, "lang": "python",
        "video": "https://youtu.be/lyDLAutA88s",
        "exercises": [
            mc("Menu pattern (while True + tanlovlar) nima uchun foydali?",
               ["Foydalanuvchi bir nechta amallarni ketma-ket bajarishi mumkin",
                "Dastur o'zi yopilmaydi — faqat 'chiqish' tanlovi bilan",
                "Har amal o'zining if/elif blokida",
                "Kod chiroyli ko'rinadi"],
               "A,B,C", multi=True, diff="Medium", pts=3),
            mc("List o'rtasidan element o'chirish uchun qaysi to'g'ri?",
               ["lst.remove(qiymat)", "del lst[indeks]", "lst.pop(indeks)", "lst.delete(0)"],
               "A,B,C", multi=True,
               hint="3 ta to'g'ri usul + 1 ta noto'g'ri.",
               diff="Medium", pts=3),
            dd("Tovarlar ro'yxati ilovasining asosiy oqimi",
               ["Bo'sh list yaratish",
                "while True bilan menu ko'rsatish",
                "Foydalanuvchi tanlovini olish",
                "if/elif bilan tegishli amal",
                "tanlov 'chiqish' bo'lsa break"],
               diff="Medium", pts=3),
            ti("Nima uchun listdan element o'chirish for sikli ichida xavfli?",
               "for x in lst: lst.remove(x) — Python o'sha vaqtda listni o'zgartirib boradi, "
               "iteratsiya indekslari buzuladi. Natija: ba'zi elementlar o'tkazib yuboriladi. "
               "Yechim: 1) yangi list yaratish [x for x in lst if shart]; "
               "2) teskari yo'nalishda aylanish; "
               "3) lst.copy() ustida aylanish.",
               diff="Hard", pts=4),
            mc("input().strip().lower() — nima qiladi?",
               ["Foydalanuvchi yozganini bo'sh joylarsiz kichik harf bilan qaytaradi",
                "Faqat bo'sh joylarni olib tashlaydi",
                "Faqat kichik harfga o'tkazadi",
                "Hech narsa qilmaydi"],
               "A", hint="3 ta metod birga ishlatilgan.",
               diff="Easy", pts=2),
            ti("Tovarlar ro'yxatiga qanday yangi imkoniyat qo'shgan bo'lardingiz va nima uchun?",
               "Misol javoblar: 1) Kategoriyalar (oziq-ovqat, kiyim) — dict ichida list shaklida; "
               "2) Narx va miqdor — har tovar dict bo'ladi: {nom, narx, miqdor}; "
               "3) Saqlash — JSON faylga yozish; 4) Filtr (faqat oziq-ovqat); "
               "5) Saralash (alifbo, narx, miqdor). Asoslash bilan: foydalanuvchi tajribasi, "
               "ma'lumot saqlash, ko'p mahsulot bilan ishlash qulayligi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 8, "title": "7-Funksiyalar",
        "text": L7_TEXT, "code": L7_CODE, "lang": "python",
        "video": "https://youtu.be/9Os0o3wzS_I",
        "exercises": [
            mc("Funksiya yaratish uchun qaysi kalit so'z?",
               ["function", "def", "func", "lambda"],
               "B", diff="Easy", pts=2),
            mc("return va print farqi nima?",
               ["return qiymatni qaytaradi (boshqa kod ishlatishi mumkin), print ekranga chiqaradi",
                "print qiymatni qaytaradi, return ekranga chiqaradi",
                "Ikkalasi bir xil",
                "return faqat sonlar uchun"],
               "A", hint="kvadrat(5) ni boshqa amalda ishlatish — return bilan mumkin.",
               diff="Easy", pts=2),
            mc("def salomlash(ism, til=\"o'zbek\"): — bu qanday parametr?",
               ["Pozitsion va default qiymatli parametr",
                "Faqat default qiymatli parametr",
                "*args va **kwargs",
                "Noto'g'ri sintaksis"],
               "A", hint="Birinchi pozitsion, ikkinchi default qiymat bilan.",
               diff="Medium", pts=3),
            dd("Funksiya yaratib chaqirish qadamlari",
               ["def kvadrat(x):",
                "    return x * x",
                "natija = kvadrat(5)",
                "print(natija)"],
               diff="Medium", pts=3),
            ti("Scope (local va global) nima va nima uchun muhim?",
               "Scope — o'zgaruvchining ko'rinish doirasi. Funksiya ichida yaratilgan o'zgaruvchi "
               "(local) — faqat shu funksiya ichida ko'rinadi va funksiya tugagach yo'qoladi. "
               "Funksiya tashqarisidagi o'zgaruvchi (global) — har joydan o'qish mumkin, lekin "
               "funksiya ichida o'zgartirish uchun 'global' kalit so'zi kerak. "
               "Bu nomlar to'qnashuvi va kutilmagan o'zgarishlardan saqlaydi.",
               diff="Hard", pts=4),
            mc("def f(*args): pass — *args nima qiladi?",
               ["Istalgan miqdordagi pozitsion argumentni tuple sifatida qabul qiladi",
                "Faqat bitta argument qabul qiladi",
                "args nomli list qabul qiladi",
                "Xato sintaksis"],
               "A", hint="* bitta argumentni 'yoyadi', tuple shaklida yig'adi.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 9, "title": "8-Lug'atlar va to'plamlar",
        "text": L8_TEXT, "code": L8_CODE, "lang": "python",
        "video": "https://youtu.be/daefaLgNkw0",
        "exercises": [
            mc("Lug'atdan qiymatni xavfsiz olish uchun qaysi to'g'ri?",
               ["d[\"kalit\"]", "d.get(\"kalit\")", "d.get(\"kalit\", \"default\")", "d.find(\"kalit\")"],
               "B,C", multi=True,
               hint="Birinchisi yo'q kalit bo'lsa KeyError, 2 va 3 — xavfsiz.",
               diff="Medium", pts=3),
            mc("set ning asosiy xususiyati qaysi?",
               ["Tartiblangan", "Takrorlanmas elementlar", "Indeks bilan kirish mumkin", "Faqat sonlar"],
               "B", diff="Easy", pts=2),
            mc("Bo'sh dict va bo'sh set qanday yaratiladi?",
               ["{} bo'sh dict, set() bo'sh set",
                "{} bo'sh set, dict() bo'sh dict",
                "[] bo'sh dict, () bo'sh set",
                "Ikkalasi bir xil: {}"],
               "A", hint="{} default dict — set uchun maxsus set() chaqirish kerak.",
               diff="Easy", pts=2),
            dd("Dict ichidagi qiymatni o'zgartirish va yangi kalit qo'shish kodini tartiblang",
               ["foydalanuvchi = {\"ism\": \"Aziz\", \"yosh\": 20}",
                "foydalanuvchi[\"yosh\"] = 21",
                "foydalanuvchi[\"email\"] = \"a@b.com\"",
                "print(foydalanuvchi)"],
               diff="Medium", pts=3),
            ti("Set amallari (union, intersection, difference) qachon foydali?",
               "Set amallari — ma'lumot to'plamlarini solishtirish va birlashtirish uchun. "
               "Union (|) — barcha elementlar (masalan, ikki guruhdagi talabalar birga). "
               "Intersection (&) — umumiy elementlar (ikkala guruhda ham bor talabalar). "
               "Difference (-) — faqat birinchi to'plamda bor (A guruhda, B da yo'q). "
               "Real misollar: takrorlanmas tovarlar, umumiy do'stlar, kashf qilinmagan mahsulotlar.",
               diff="Hard", pts=4),
            mc("for kalit, qiymat in d.items(): — nima beradi?",
               ["Faqat kalitlar", "Faqat qiymatlar", "Kalit va qiymat juftliklari", "Faqat indekslar"],
               "C", diff="Easy", pts=2),
            ti("dict comprehension (masalan, {k: v*2 for k, v in d.items()}) qachon foydali?",
               "Dict comprehension — qisqa va o'qiladigan dict yaratish/o'zgartirish usuli. "
               "Misollar: 1) qiymatlarni o'zgartirish ({k: v*1.1 for k,v in narxlar.items()} — 10% qo'shish); "
               "2) filtr ({k: v for k,v in d.items() if v > 100}); "
               "3) yangi dict yaratish ({i: i*i for i in range(10)}). "
               "Klassik for sikli o'rniga 1 qatorda yoziladi va Python ichida tezroq.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 10, "title": "9-Modullar va paketlar",
        "text": L9_TEXT, "code": L9_CODE, "lang": "python",
        "video": "https://youtu.be/CqvZ3vGoGs0",
        "exercises": [
            mc("import math va from math import sqrt farqi nima?",
               ["Birinchisida math.sqrt(16), ikkinchisida sqrt(16) ishlatiladi",
                "Birinchisi tezroq, ikkinchisi sekinroq",
                "Hech qanday farq yo'q",
                "Faqat sintaksis farqi, lekin natija boshqa"],
               "A", diff="Easy", pts=2),
            mc("random.randint(1, 10) qaysi qiymatlarni qaytarishi mumkin?",
               ["1 dan 10 gacha (10 ham kiradi)",
                "1 dan 9 gacha (10 kirmaydi)",
                "0 dan 10 gacha",
                "0 dan 9 gacha"],
               "A", hint="randint INCLUSIVE, range esa exclusive.",
               diff="Easy", pts=2),
            mc("Quyidagi standart modullardan qaysilari Python bilan birga keladi?",
               ["math", "random", "datetime", "json", "requests"],
               "A,B,C,D", multi=True,
               hint="requests — bu tashqi paket, pip install kerak.",
               diff="Medium", pts=3),
            dd("JSON faylga ma'lumot saqlash va o'qish bosqichlari",
               ["import json",
                "data = {\"ism\": \"Aziz\", \"yosh\": 20}",
                "with open(\"data.json\", \"w\", encoding=\"utf-8\") as f:",
                "    json.dump(data, f, ensure_ascii=False, indent=2)",
                "with open(\"data.json\", \"r\", encoding=\"utf-8\") as f:",
                "    yuklangan = json.load(f)"],
               diff="Medium", pts=3),
            ti("if __name__ == \"__main__\": nima uchun ishlatiladi?",
               "Modulni ikki usulda ishlatish mumkin: 1) to'g'ridan-to'g'ri (python fayl.py); "
               "2) boshqa fayldan import qilish. Birinchi holatda __name__ = \"__main__\", "
               "ikkinchi holatda __name__ = modul nomi. Bu blok ichidagi kod faqat to'g'ridan-to'g'ri "
               "ishga tushganda bajariladi — import paytida emas. Bu test kodlari, demo va asosiy "
               "ilovani modul ichida saqlashga imkon beradi.",
               diff="Hard", pts=4),
            mc("pip install requests nima qiladi?",
               ["requests modulini Python'ga o'rnatadi",
                "requests modulini import qiladi",
                "requests xizmatini ishga tushiradi",
                "requests faylini ko'chiradi"],
               "A", diff="Easy", pts=2),
        ],
    },
    {
        "order": 11, "title": "R3-So'zlik ilovasi (takrorlash)",
        "text": R3_TEXT, "code": R3_CODE, "lang": "python",
        "video": "https://youtu.be/UMS5JtnLapw",
        "exercises": [
            mc("json.dump(d, f, ensure_ascii=False) ni nima uchun ishlatamiz?",
               ["Tezroq saqlash uchun",
                "Kirill va o'zbek harflar to'g'ri saqlanishi uchun",
                "Faqat sonlar saqlash uchun",
                "Kompressiya uchun"],
               "B", explanation="ensure_ascii=False bo'lmasa, o'zbek/kirill harflar \\uXXXX shaklida saqlanadi.",
               diff="Medium", pts=3),
            mc("try/except FileNotFoundError qanday holatga mo'ljallangan?",
               ["Faylda matn yo'q bo'lganda",
                "Fayl mavjud bo'lmaganda (yo'q yoki o'chirilgan)",
                "Fayl ochiq bo'lganda",
                "Faylga ruxsat yo'q bo'lganda"],
               "B", hint="PermissionError boshqa exception turi.",
               diff="Easy", pts=2),
            mc("So'zlik ilovasining qaysi qismlari alohida funksiya bo'lishi kerak?",
               ["yuklash() — fayldan o'qish",
                "saqlash() — faylga yozish",
                "qoshish() — yangi so'z qo'shish",
                "qidirish() — so'zni topish",
                "Hammasini bitta funksiyada qilish"],
               "A,B,C,D", multi=True,
               hint="Har vazifa alohida funksiyaga — bu single responsibility.",
               diff="Medium", pts=3),
            dd("So'zlik ilovasining boshlanish oqimini tartiblang",
               ["import json va os",
                "Fayl yo'lini global o'zgaruvchiga yozish",
                "yuklash() funksiyasini chaqirib dict olish",
                "while True menu pattern",
                "Tanlovga qarab funksiya chaqirish",
                "Yopilishda saqlash() chaqirish"],
               diff="Medium", pts=3),
            ti("Lug'at ma'lumotini faylga saqlash nima uchun muhim va qanday afzalliklarni beradi?",
               "Dastur o'chsa — RAM dagi barcha o'zgaruvchilar yo'qoladi. Faylga saqlash ma'lumotni "
               "doimiy qiladi: ilova qaytadan ochilganda yuklash mumkin. JSON — eng oddiy format: "
               "human-readable, har dasturlash tilida o'qish/yozish mumkin, struktura saqlanadi. "
               "Real ilovalarda esa SQLite, PostgreSQL kabi ma'lumotlar bazalari ishlatiladi.",
               diff="Hard", pts=4),
            mc("Default qiymatli mutable parametr (def f(items=[]):) nima uchun anti-pattern?",
               ["Funksiya har chaqirilganda bir xil list ulashiladi — kutilmagan natija",
                "Sekin ishlaydi",
                "Sintaksis xatosi beradi",
                "Hech qanday muammo yo'q"],
               "A", hint="Default qiymat bir marta yaratiladi va saqlanib qoladi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 12, "title": "10-Klasslar va obyektlar (OOP)",
        "text": L10_TEXT, "code": L10_CODE, "lang": "python",
        "video": "https://youtu.be/JeznW_7DlB0",
        "exercises": [
            mc("__init__ metodi qachon chaqiriladi?",
               ["Class yaratilganda",
                "Har obyekt yaratilganda (instantiate)",
                "Faqat birinchi obyekt uchun",
                "Hech qachon — biz qo'lda chaqiramiz"],
               "B", diff="Easy", pts=2),
            mc("Metod ichidagi 'self' parametri nimani anglatadi?",
               ["Class ni",
                "Joriy obyektni (instance)",
                "Funksiyani",
                "Ota class ni"],
               "B", hint="self.ism = ism — obyektning atributiga qo'yish.",
               diff="Easy", pts=2),
            mc("class Talaba(Inson) — bu qaysi OOP tushunchasini ifodalaydi?",
               ["Inheritance (meros)",
                "Polymorphism",
                "Encapsulation",
                "Abstraction"],
               "A", diff="Easy", pts=2),
            dd("Class yaratib obyekt bilan ishlash bosqichlari",
               ["class Kitob:",
                "    def __init__(self, sarlavha, muallif):",
                "        self.sarlavha = sarlavha",
                "        self.muallif = muallif",
                "    def __str__(self):",
                "        return f\"'{self.sarlavha}' — {self.muallif}\"",
                "k = Kitob(\"Avliyo\", \"Cho'lpon\")",
                "print(k)"],
               diff="Medium", pts=3),
            ti("super().__init__() ni qachon va nima uchun chaqiramiz?",
               "Inheritance da bola class o'zining __init__ ini yozsa, ota class init avtomatik "
               "chaqirilmaydi. super().__init__(args) — ota class init ni qo'lda chaqirish. "
               "Bu ota class atributlari to'g'ri o'rnatilishini ta'minlaydi. Aks holda obyektda "
               "ba'zi atributlar yo'q bo'lishi mumkin. Misol: class Talaba(Inson) da super().__init__(ism, yosh) "
               "chaqirilmasa — self.ism, self.yosh bo'lmaydi.",
               diff="Hard", pts=4),
            mc("__str__ metodi nima vazifani bajaradi?",
               ["Class nomini qaytaradi",
                "print(obj) chaqirilganda chiroyli string qaytaradi",
                "Obyektni o'chiradi",
                "Konstruktor"],
               "B", hint="Yo'q bo'lsa — <__main__.Class object at 0x...> chiqadi.",
               diff="Medium", pts=3),
            ti("OOP nima uchun foydali va u qaysi vaziyatlarda kerak?",
               "OOP — bog'liq ma'lumotlar va ular bilan ishlovchi funksiyalarni bir obyektga "
               "birlashtirish. Foydali: 1) Real dunyo modellashtirish (Talaba, Kitob, BankAccount); "
               "2) Kodni qayta ishlatish (inheritance orqali umumiy mantiq); "
               "3) Murakkab tizim — har qism o'z mas'uliyatida; "
               "4) Katta jamoada ishlash — har class alohida; "
               "Kerakmas: oddiy skript, bir martalik analiz, kichik script — odatdagi funksiya yaxshiroq.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 13, "title": "11-Fayllar va xatolar bilan ishlash",
        "text": L11_TEXT, "code": L11_CODE, "lang": "python",
        "video": "https://youtu.be/Lu1nskBkPJU",
        "exercises": [
            mc("with open(...) as f: nima uchun ishlatiladi?",
               ["Fayl avtomatik yopiladi — f.close() chaqirish shart emas",
                "Faylni faqat o'qish uchun ochadi",
                "Tezroq ochish uchun",
                "Faqat binary fayllar uchun"],
               "A", diff="Easy", pts=2),
            mc("Quyidagi rejimlardan qaysilari fayl yozish uchun?",
               ["r", "w", "a", "rb", "r+"],
               "B,C,E", multi=True,
               hint="r — faqat o'qish, rb — binary o'qish. Qolganlari yozish bilan bog'liq.",
               diff="Medium", pts=3),
            mc("try/except blokining oqimi qanday?",
               ["try blokda xato bo'lsa — except ishlaydi",
                "except blokda xato bo'lsa — try ishlaydi",
                "Har ikkalasi ham ishlaydi",
                "Faqat try ishlaydi"],
               "A", diff="Easy", pts=2),
            dd("Faylni xavfsiz o'qish bosqichlarini tartiblang",
               ["try:",
                "    with open(\"data.txt\", \"r\", encoding=\"utf-8\") as f:",
                "        matn = f.read()",
                "    print(matn)",
                "except FileNotFoundError:",
                "    print(\"Fayl topilmadi\")"],
               diff="Medium", pts=3),
            ti("try/except va raise farqi nima va qachon raise ishlatamiz?",
               "try/except — boshqa joyda chiqqan xatoni ushlash. raise — xatoni o'zi chiqarish. "
               "raise — input tekshirish (manfiy yosh, bo'sh ism), biznes qoidalari (qoldiq yetarli emas), "
               "noto'g'ri foydalanish (parametrlar nomos). Aniq xato turi yozish kerak: "
               "raise ValueError(\"Yosh manfiy bo'lmaydi\"). Chaqiruvchi bu xatoni try/except bilan ushlaydi.",
               diff="Hard", pts=4),
            mc("\"w\" rejimi mavjud faylga nima qiladi?",
               ["Mavjud faylni o'chiradi va bo'sh fayl yaratadi",
                "Oxiriga yozadi",
                "O'zgartirmaydi — faqat o'qiydi",
                "Xato beradi"],
               "A", hint="\"a\" rejimi — append, oxiriga qo'shadi. \"w\" — overwrite.",
               diff="Easy", pts=2),
            ti("encoding=\"utf-8\" parametrining ahamiyati nima?",
               "Fayl ichidagi belgilar qaysi kodlash sxemasi bilan saqlanishini bildiradi. "
               "UTF-8 — Unicode'ning eng keng tarqalgan kodlashi. O'zbek (lotin va kirill), "
               "rus, xitoy, arab — barcha harflar to'g'ri saqlanadi. encoding bermasa, "
               "tizim default ishlatadi (Windows'da odatda cp1252) — bu kirill yoki o'zbek "
               "harflar bilan ishlamaydi. Doim encoding=\"utf-8\" yozing.",
               diff="Hard", pts=4),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Seeding logic
# ─────────────────────────────────────────────────────────────────────────────
def _jdump(value):
    """Serialize lists to JSON for text columns; pass scalars through unchanged."""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson: dict, exercise_rows: list[Exercise]) -> str:
    """Mirror the HTML CSS course shape: text → code → video → exercise."""
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
                  f"{lesson.title:<40}  exercises={len(ex_rows)}")

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
