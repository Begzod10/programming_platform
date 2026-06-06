"""Seed the "Python: Keyingi Bosqich" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_python_next_level.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: "Python Asoslari" graduates. Skips variables/loops/basic OOP
and jumps straight into idiomatic Python: comprehensions, generators,
decorators, dataclasses, JSON/CSV/HTTP, regex, deep OOP, and a CLI capstone.
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
    "title": "Python: Keyingi Bosqich",
    "description": (
        "Python Asoslari kursini tugatgan dasturchilar uchun: idiomatik Python, "
        "list/dict comprehension'lar, generatorlar, dekoratorlar, dataclasses, "
        "type hints, JSON/CSV/HTTP, regex, chuqurroq OOP. Har bir modul oxirida "
        "loyiha. Maqsad — endi siz Python'da 'pythonic' yozasiz."
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
# Each L*_TEXT is the HTML body, each L*_CODE is the runnable code section.
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Comprehension'lar — bir qatorda yangi ro'yxat</h2>

<pre class="mermaid">
flowchart LR
    SRC["manba kolleksiyasi"] -->|for x in src| EACH["har element"]
    EACH -->|if shart| KEEP["filterdan o'tdi"]
    KEEP -->|expr x| NEW["yangi element"]
    NEW --> OUT["new_list"]
</pre>

<p><strong>List comprehension</strong> — Python'ning eng pythonic xususiyatlaridan biri. 4 qator <code>for</code> kodini bitta qatorga yig'adi. Endi siz <code>for</code> sikli ichida <code>append</code> qilmaysiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>
<p>F12 yoki terminalda <code>python</code> ochib quyidagilarni sinab ko'ring.</p>

<h4>BLOKA 1 — eski uslubdan yangiga</h4>
<pre><code># Eski uslub (uzun)
kvadratlar = []
for x in range(10):
    kvadratlar.append(x * x)
print(kvadratlar)

# Pythonic — bir qatorda
kvadratlar = [x * x for x in range(10)]
print(kvadratlar)
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]</code></pre>

<h4>BLOKA 2 — filter bilan</h4>
<pre><code>sonlar = [1, 5, -3, 8, -2, 11, 0, 7]
musbat = [x for x in sonlar if x &gt; 0]
print(musbat)
# [1, 5, 8, 11, 7]

# Filter + transformatsiya birga
juft_kvadrat = [x * x for x in sonlar if x &gt; 0 and x % 2 == 0]
print(juft_kvadrat)
# [64]</code></pre>

<h4>BLOKA 3 — dict va set comprehension</h4>
<pre><code>ismlar = ["Olim", "Salim", "Karim", "Olim"]

# Dict comprehension — kalit:qiymat
uzunliklar = {ism: len(ism) for ism in ismlar}
print(uzunliklar)
# {'Olim': 4, 'Salim': 5, 'Karim': 5}

# Set comprehension — takrorlanmas to'plam
unik = {ism.lower() for ism in ismlar}
print(unik)
# {'olim', 'salim', 'karim'}</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Quyidagi kod nima qaytaradi deb o'ylaysiz?
natija = [for x in range(5): x * 2]
print(natija)</code></pre>
<p><strong>Natija:</strong> <code>SyntaxError</code>. Comprehension'da <code>for</code> oldin <em>ifoda</em> kelishi shart: <code>[x * 2 for x in range(5)]</code>. Bu eng ko'p uchraydigan xato — odam <code>for</code> sikli bilan adashtirib yuboradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Umumiy shakl</h4>
<pre><code>[ &lt;ifoda&gt; for &lt;element&gt; in &lt;iterable&gt; if &lt;shart&gt; ]</code></pre>
<ul>
<li><strong>ifoda</strong> — har element ustida nima qilamiz (transformatsiya)</li>
<li><strong>element</strong> — har iteratsiyadagi qiymat</li>
<li><strong>iterable</strong> — manba kolleksiyasi (list, str, range, dict, generator, ...)</li>
<li><strong>shart</strong> — ixtiyoriy, faqat shu shartga to'g'ri kelganlarni saqlaymiz</li>
</ul>

<h4>2. Uch turi</h4>
<table>
<tr><th>Tur</th><th>Sintaksis</th><th>Natija</th></tr>
<tr><td>list</td><td><code>[x*2 for x in nums]</code></td><td>yangi <code>list</code></td></tr>
<tr><td>dict</td><td><code>{k: v for k, v in pairs}</code></td><td>yangi <code>dict</code></td></tr>
<tr><td>set</td><td><code>{x for x in nums}</code></td><td>yangi <code>set</code> (takrorsiz)</td></tr>
<tr><td>generator</td><td><code>(x*2 for x in nums)</code></td><td>lazy generator (2-darsda)</td></tr>
</table>

<h4>3. if/else bilan ifoda ichida</h4>
<pre><code># Faqat filter (if oxirida)
[x for x in nums if x &gt; 0]

# Har element uchun if/else (ifoda ichida)
[("musbat" if x &gt; 0 else "manfiy") for x in nums]</code></pre>
<p>Qoidasi: <strong>filter</strong> uchun <code>if</code> sikldan <em>keyin</em>. <strong>Ifoda ichida tanlov</strong> uchun <code>if/else</code> ifodaning <em>ichida</em>.</p>

<h4>4. Ichki (nested) comprehension</h4>
<pre><code># 2D matritsa yarating
matritsa = [[i * j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Matritsani tekislash (flatten)
flat = [el for qator in matritsa for el in qator]
# [0, 0, 0, 0, 1, 2, 0, 2, 4]</code></pre>
<p><strong>Qoida:</strong> ichki comprehension'da <code>for</code>'lar chap-o'ng tartibida o'qiladi — xuddi oddiy ikkita ichma-ich sikldek.</p>

<h4>5. Qachon ishlatmaslik kerak?</h4>
<ul>
<li>Tana 1-2 qatordan ko'p bo'lsa — oddiy <code>for</code> aniqroq</li>
<li>Yon ta'siri bor (print, fayl yozish) — comprehension'ni faqat <em>yangi list yaratish</em> uchun ishlating</li>
<li>3+ darajali nested — o'qishga qiyin, oddiy sikl yaxshiroq</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>List comprehension — <code>append</code> bilan sikldan tezroq va o'qimliroq</li>
<li>Dict va set comprehension ham bor — <code>{}</code> bilan</li>
<li>Filter — <code>if</code> oxirida, ifoda ichidagi tanlov — <code>if/else</code> ifodaning ichida</li>
<li>Yon ta'siri bo'lsa — comprehension emas, oddiy sikl ishlating</li>
<li><code>[for x in ...]</code> — SyntaxError. Ifoda <code>for</code> dan oldin keladi</li>
</ul>
"""

L1_CODE = """\
# ─── Comprehension'lar bo'yicha 1 fayl, 1 nafas demo ──────────────────────
# Faylni saqlab `python demo.py` deb chiqaring.

# 1) List comprehension — minimal
print([x * x for x in range(6)])

# 2) Filter bilan
sonlar = [1, 5, -3, 8, -2, 11, 0, 7]
print([x for x in sonlar if x > 0])

# 3) Filter + ifoda ichidagi if/else
print([("+" if x > 0 else "-" if x < 0 else "0") for x in sonlar])

# 4) Dict comprehension — so'zlardan {so'z: uzunligi}
sozlar = ["python", "ai", "data", "ml"]
print({s: len(s) for s in sozlar})

# 5) Set comprehension — takrorsiz alifbo harflari
matn = "Misol uchun bu matn"
print({ch.lower() for ch in matn if ch.isalpha()})

# 6) Nested — ko'paytirish jadvali
jadval = [[i * j for j in range(1, 6)] for i in range(1, 6)]
for qator in jadval:
    print(qator)

# 7) Flatten — 2D ni 1D ga
flat = [el for qator in jadval for el in qator]
print(flat)

# 8) Practical — talabalar bahlari
talabalar = [
    {"ism": "Ali", "ball": 87},
    {"ism": "Vali", "ball": 54},
    {"ism": "Gulya", "ball": 92},
    {"ism": "Doniyor", "ball": 68},
]

# 70+ bahlilar ismlari
otliklar = [t["ism"] for t in talabalar if t["ball"] >= 70]
print("70+:", otliklar)

# Ism -> harf (90+: A, 70+: B, 60+: C, qolgani: F)
def harf(b):
    return "A" if b >= 90 else "B" if b >= 70 else "C" if b >= 60 else "F"

baholar = {t["ism"]: harf(t["ball"]) for t in talabalar}
print(baholar)
"""

L2_TEXT = """\
<h2>Generatorlar va <code>yield</code> — xotirani band qilmasdan oqim</h2>

<pre class="mermaid">
flowchart LR
    CALL["gen() chaqiruvi"] -->|hech narsa hisoblanmaydi| GEN["generator obyekt"]
    GEN -->|next gen| Y1["yield 1"]
    Y1 --> P1["pauza"]
    P1 -->|next gen| Y2["yield 2"]
    Y2 --> P2["pauza"]
    P2 -->|StopIteration| END["tugadi"]
</pre>

<p>List comprehension darhol <strong>butun ro'yxatni xotirada qurib</strong> qaytaradi. Generator — <strong>kerakli paytida hisoblaydi</strong>. 1 milliard sonni list qilsangiz — xotira yetmaydi. Generator qilsangiz — 1 element band qiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Generator function (yield bilan)</h4>
<pre><code>def kvadratlar(n):
    for i in range(n):
        yield i * i        # return emas — yield!

gen = kvadratlar(5)
print(gen)                  # &lt;generator object kvadratlar at 0x...&gt;
print(next(gen))            # 0
print(next(gen))            # 1
print(next(gen))            # 4
print(list(gen))            # [9, 16] — qolganlari</code></pre>
<p><code>yield</code> bilan funksiya pauza qiladi, navbatdagi <code>next()</code> da qaytadan davom etadi.</p>

<h4>BLOKA 2 — Generator expression (lazy comprehension)</h4>
<pre><code># [] o'rniga ()
katta_oqim = (x * x for x in range(10**8))
print(katta_oqim)
# &lt;generator object &lt;genexpr&gt; at 0x...&gt;

# Xotira deyarli nol — chunki hali hech narsa hisoblanmagan
print(next(katta_oqim))     # 0
print(next(katta_oqim))     # 1

# Faqat birinchi 10 tasini olamiz — qolgan 99,999,990 ta hech qachon yaratilmaydi
from itertools import islice
print(list(islice(katta_oqim, 10)))</code></pre>

<h4>BLOKA 3 — Cheksiz oqim</h4>
<pre><code>def cheksiz_natural_sonlar():
    n = 1
    while True:
        yield n
        n += 1

gen = cheksiz_natural_sonlar()
for son in gen:
    if son &gt; 5:
        break
    print(son)
# 1, 2, 3, 4, 5</code></pre>
<p>Cheksiz sikl — odatda xato. Lekin generator bilan <em>kerakli vaqtda to'xtatish</em> mumkin.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>def sonlar():
    for i in range(3):
        yield i

g = sonlar()
print(list(g))    # [0, 1, 2]
print(list(g))    # ???</code></pre>
<p><strong>Natija:</strong> ikkinchi <code>list(g)</code> — <strong>bo'sh ro'yxat <code>[]</code></strong>. Generator <em>bir martalik</em>. Tugagandan keyin uni qayta o'qib bo'lmaydi. Qayta kerak bo'lsa — <code>sonlar()</code> ni qaytadan chaqirish kerak.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Lazy vs eager</h4>
<table>
<tr><th>Eager (list)</th><th>Lazy (generator)</th></tr>
<tr><td>Darhol hammasini xotirada quradi</td><td>Kerakli paytida bittadan beradi</td></tr>
<tr><td>Ko'p marta o'qish mumkin</td><td>Bir martalik</td></tr>
<tr><td>len(), [i] indexing ishlaydi</td><td>len, indexing — yo'q</td></tr>
<tr><td>Xotira: O(n)</td><td>Xotira: O(1)</td></tr>
</table>

<h4>2. Qachon generator?</h4>
<ul>
<li>Katta fayl — qator-qator o'qish (<code>for line in open(...)</code>)</li>
<li>API'dan paginated data — sahifa-sahifa</li>
<li>Cheksiz oqim — vaqt belgilari, raqamlar generatori</li>
<li>Pipeline — bir generator boshqa generatorni feed qiladi</li>
</ul>

<h4>3. <code>yield from</code> — boshqa iterable'ni qayta uzatish</h4>
<pre><code>def birlashma(a, b):
    yield from a
    yield from b

print(list(birlashma([1, 2, 3], (4, 5))))   # [1, 2, 3, 4, 5]</code></pre>

<h4>4. Generator pipeline (chiroyli pattern)</h4>
<pre><code>def o_qish(fayl):
    for qator in open(fayl):
        yield qator.strip()

def filterlash(qatorlar, kalit):
    for q in qatorlar:
        if kalit in q:
            yield q

def upperga(qatorlar):
    for q in qatorlar:
        yield q.upper()

# Hech bir bosqich xotirada to'liq yig'ilmaydi
oqim = upperga(filterlash(o_qish("log.txt"), "ERROR"))
for q in oqim:
    print(q)</code></pre>

<h4>5. Generator vs list — qaror jadvali</h4>
<table>
<tr><th>Holatga qarab</th><th>Tanlang</th></tr>
<tr><td>Bir necha marta o'qish kerak</td><td>list</td></tr>
<tr><td>Indeks bilan kirish, len</td><td>list</td></tr>
<tr><td>Katta yoki cheksiz oqim</td><td>generator</td></tr>
<tr><td>Faqat bir marta sweep</td><td>generator</td></tr>
<tr><td>Pipeline / zanjir</td><td>generator</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>yield</code> — funksiyani pauza qilib turadi, <code>next()</code> da davom etadi</li>
<li><code>(x for x in ...)</code> — generator expression, <code>[...]</code> ning lazy varianti</li>
<li>Generator bir martalik — tugagach qayta o'qib bo'lmaydi</li>
<li>Katta / cheksiz oqimlar uchun — list emas, generator</li>
<li><code>yield from</code> — boshqa iterable'ni hech ochmasdan qayta uzatadi</li>
</ul>
"""

L2_CODE = """\
# ─── Generatorlar bilan ishlash ──────────────────────────────────────────
import sys
from itertools import islice
import time

# 1) Eng oddiy yield
def son_qatori(n):
    for i in range(n):
        yield i * 2

g = son_qatori(5)
print(type(g))
print(list(g))                 # [0, 2, 4, 6, 8]

# 2) Generator vs list — xotira solishtirish
katta_list = [x for x in range(10**6)]
katta_gen  = (x for x in range(10**6))
print("list  bayt:", sys.getsizeof(katta_list))
print("gen   bayt:", sys.getsizeof(katta_gen))

# 3) Cheksiz fibonacchi
def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Birinchi 10 tasini olamiz — generatorning kuchi
print(list(islice(fib(), 10)))

# 4) Pipeline pattern (logni filterlash)
def manba():
    yield "INFO: server start"
    yield "ERROR: db timeout"
    yield "INFO: request 200"
    yield "ERROR: auth failed"
    yield "INFO: shutdown"

def faqat_error(qatorlar):
    for q in qatorlar:
        if q.startswith("ERROR"):
            yield q

def vaqt_qoshish(qatorlar):
    for q in qatorlar:
        yield f"[{time.strftime('%H:%M:%S')}] {q}"

oqim = vaqt_qoshish(faqat_error(manba()))
for q in oqim:
    print(q)

# 5) Generator faqat bir marta
g = (x for x in range(3))
print("birinchi:", list(g))    # [0, 1, 2]
print("ikkinchi:", list(g))    # []  — bo'sh

# 6) yield from — birlashtirish
def birlashma(*iterables):
    for it in iterables:
        yield from it

print(list(birlashma([1, 2], (3, 4), range(5, 8))))
# [1, 2, 3, 4, 5, 6, 7]
"""

L3_TEXT = """\
<h2>Lambda, map, filter, sorted — <code>key=</code> paradigmasi</h2>

<pre class="mermaid">
flowchart LR
    DATA["ma'lumot"] -->|key= funksiya| TRANS["har element uchun qiymat"]
    TRANS -->|sorted| OUT_S["saralangan"]
    TRANS -->|max/min| OUT_M["eng katta/kichik"]
    DATA -->|filter| F["shartga to'g'ri keladiganlar"]
    DATA -->|map| M["transformatsiya"]
</pre>

<p>Endi siz <strong>bir satrlik funksiyalarni</strong> <code>lambda</code> bilan yozasiz va <code>key=</code> argumenti orqali Python'ning standart funksiyalariga "qanday taqqoslashni" o'rgatasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Lambda — bir qatorli funksiya</h4>
<pre><code># Oddiy def
def qosh(x):
    return x + 5

# Bir qatorda
qosh = lambda x: x + 5

print(qosh(10))               # 15

# Lambda ko'p argumentli ham
maydon = lambda en, bo_y: en * bo_y
print(maydon(3, 4))           # 12</code></pre>

<h4>BLOKA 2 — sorted bilan key=</h4>
<pre><code>foydalanuvchilar = [
    {"ism": "Doniyor", "yosh": 25},
    {"ism": "Ali",     "yosh": 19},
    {"ism": "Karim",   "yosh": 33},
]

# Yosh bo'yicha saralash
print(sorted(foydalanuvchilar, key=lambda u: u["yosh"]))

# Ism uzunligi bo'yicha
print(sorted(foydalanuvchilar, key=lambda u: len(u["ism"])))

# Kamayuvchi (reverse=True)
print(sorted(foydalanuvchilar, key=lambda u: u["yosh"], reverse=True))</code></pre>

<h4>BLOKA 3 — map va filter</h4>
<pre><code>sonlar = [1, 2, 3, 4, 5, 6]

# map — har element ustida transformatsiya
kvadratlar = list(map(lambda x: x * x, sonlar))
print(kvadratlar)             # [1, 4, 9, 16, 25, 36]

# filter — shartga to'g'ri keladiganlar
juftlar = list(filter(lambda x: x % 2 == 0, sonlar))
print(juftlar)                # [2, 4, 6]

# Bunday "kalit" sifatida tayyor funksiyalar ham ishlaydi
matnlar = ["python", "AI", "data"]
print(list(map(str.upper, matnlar)))     # ['PYTHON', 'AI', 'DATA']</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>kvadrat = lambda x: print(x * x)
natija = kvadrat(5)
print("Qaytdi:", natija)</code></pre>
<p><strong>Natija:</strong> <code>25</code>, keyin <code>Qaytdi: None</code>. <code>print()</code> qiymat <strong>qaytarmaydi</strong> (<code>None</code> qaytaradi). Lambda doim <em>ifoda</em> qiymatini qaytaradi — agar tanasida <code>print(...)</code> bo'lsa, lambda <code>None</code> qaytaradi. Lambda — <strong>qiymat qaytarish</strong> uchun, yon ta'sir uchun emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Lambda — qachon va qachon emas?</h4>
<ul>
<li><strong>Qachon ✅:</strong> <code>sorted(..., key=...)</code>, <code>map</code>, <code>filter</code>, <code>max</code>, <code>min</code>, <code>functools.reduce</code> uchun bir qatorli kalit funksiyasi</li>
<li><strong>Qachon emas ❌:</strong> 1 qatordan ko'p logika, takror ishlatiladigan funksiya (oddiy <code>def</code> ishlating)</li>
<li><strong>Qachon emas ❌:</strong> tanasida <code>if/else</code>, <code>try</code>, <code>print</code> bor — lambda emas, oddiy <code>def</code></li>
</ul>

<h4>2. key= paradigmasi — eng kuchli idiom</h4>
<p><code>key=</code> argumenti — "Python, har elementdan qaysi qiymatni taqqoslash uchun olishimni ayt". Quyidagi funksiyalarda ishlaydi: <code>sorted</code>, <code>min</code>, <code>max</code>, <code>list.sort()</code>.</p>
<pre><code>narxlar = [{"nom": "olma", "narx": 12000}, {"nom": "non", "narx": 4000}]

# Eng arzonini topish
eng_arzon = min(narxlar, key=lambda p: p["narx"])

# Bir nechta mezon — tuple qaytaring
sorted(narxlar, key=lambda p: (p["narx"], p["nom"]))
# avval narx, keyin nom bo'yicha</code></pre>

<h4>3. map/filter vs comprehension</h4>
<table>
<tr><th>map/filter</th><th>Comprehension</th></tr>
<tr><td><code>list(map(f, xs))</code></td><td><code>[f(x) for x in xs]</code></td></tr>
<tr><td><code>list(filter(p, xs))</code></td><td><code>[x for x in xs if p(x)]</code></td></tr>
</table>
<p>Pythonic — odatda <strong>comprehension</strong> ishlatiladi. <code>map/filter</code> ishlatish ma'qul: tayyor funksiya bilan (<code>str.upper</code>, <code>int</code>), agar lambda bo'lsa — comprehension yaxshiroq.</p>

<h4>4. functools.reduce — yig'uvchi</h4>
<pre><code>from functools import reduce

# Yig'indi (sum bor — bu shunchaki misol)
print(reduce(lambda acc, x: acc + x, [1, 2, 3, 4]))   # 10

# Eng katta sonni topish
print(reduce(lambda a, b: a if a &gt; b else b, [3, 7, 2, 9, 4]))   # 9</code></pre>
<p>Sum/max/min uchun tayyor funksiya bor. reduce — boshqa "yig'ish" turlari uchun (masalan, dict birlashtirish, kustom akkumulyatsiya).</p>

<h4>5. Tezkor "kalit" idiomalari</h4>
<pre><code>from operator import itemgetter, attrgetter

# Lambda emas — itemgetter (tezroq, o'qimliroq)
sorted(narxlar, key=itemgetter("narx"))

# Class instance'lar bo'yicha — attrgetter
sorted(talabalar, key=attrgetter("ball"))</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>lambda x: ifoda</code> — bir qatorli anonim funksiya</li>
<li><code>key=</code> — har elementdan taqqoslash uchun qiymat oluvchi funksiya</li>
<li>Bir nechta mezon uchun <code>key</code>'da <code>tuple</code> qaytaring</li>
<li><code>map/filter + lambda</code> o'rniga ko'pincha comprehension yaxshiroq</li>
<li><code>operator.itemgetter</code> / <code>attrgetter</code> — lambda'dan tezroq alternativa</li>
</ul>
"""

L3_CODE = """\
# ─── Lambda, map, filter, sorted — key= bilan ─────────────────────────────
from operator import itemgetter
from functools import reduce

# 1) Lambda asoslari
kub = lambda x: x ** 3
print(kub(4))

salom = lambda ism, salom_so_zi="Salom": f"{salom_so_zi}, {ism}!"
print(salom("Olim"))
print(salom("Karim", salom_so_zi="Assalomu alaykum"))

# 2) sorted + key — list of dict
talabalar = [
    {"ism": "Ali",     "ball": 87, "yosh": 21},
    {"ism": "Vali",    "ball": 54, "yosh": 19},
    {"ism": "Gulya",   "ball": 92, "yosh": 22},
    {"ism": "Doniyor", "ball": 68, "yosh": 20},
]

# Ball bo'yicha kamayuvchi tartibda
top = sorted(talabalar, key=lambda t: t["ball"], reverse=True)
for t in top:
    print(t["ism"], t["ball"])

# Bir nechta mezon: avval ball (kamayuvchi), keyin yosh (oshib)
saralangan = sorted(talabalar, key=lambda t: (-t["ball"], t["yosh"]))
print("Saralangan:", saralangan)

# 3) map — tayyor funksiya bilan
ismlar = ["ali", "vali", "gulya"]
print(list(map(str.capitalize, ismlar)))    # ['Ali', 'Vali', 'Gulya']

# 4) filter — shartga to'g'ri keladiganlar
otliklar = list(filter(lambda t: t["ball"] >= 70, talabalar))
print("70+ ballilar:", [t["ism"] for t in otliklar])

# 5) min/max with key
eng_yosh = min(talabalar, key=lambda t: t["yosh"])
eng_baholi = max(talabalar, key=lambda t: t["ball"])
print(f"Eng yosh: {eng_yosh['ism']}  Eng baholi: {eng_baholi['ism']}")

# 6) operator.itemgetter — lambda'dan tezroq
print(sorted(talabalar, key=itemgetter("ball")))

# 7) reduce — kustom akkumulyatsiya (umumiy ball)
jami = reduce(lambda acc, t: acc + t["ball"], talabalar, 0)
print(f"Jami ball: {jami}")

# 8) Real misol — mahsulotlar ro'yxati
mahsulotlar = [
    {"nom": "Olma", "narx": 12000, "soni": 5},
    {"nom": "Non",  "narx": 4000,  "soni": 12},
    {"nom": "Sut",  "narx": 9000,  "soni": 3},
]

# Umumiy summa
print("Jami:", sum(map(lambda m: m["narx"] * m["soni"], mahsulotlar)))

# Faqat 5000 dan qimmat
qimmat = list(filter(lambda m: m["narx"] >= 5000, mahsulotlar))
print(qimmat)

# Nomi bo'yicha alifbo tartibida
print(sorted(mahsulotlar, key=lambda m: m["nom"]))
"""

R1_TEXT = """\
<h2>🔁 R1 — Sotuvchi statistikasi (Modul 1 takrori)</h2>

<pre class="mermaid">
flowchart LR
    SAVDOS["savdolar list"] -->|gen expr| OQIM["oqim"]
    OQIM -->|filter| F["sotuvchi bo'yicha"]
    F -->|sum / max| AGG["agregatsiya"]
    AGG -->|sorted key=| TOP["TOP 3"]
</pre>

<p>3 ta darsda olgan bilimlarni birlashtiramiz: <strong>comprehension</strong>, <strong>generator</strong>, <strong>lambda + sorted</strong>. Ma'lumotlar: sotuvchilar savdolari ro'yxati. Vazifa: TOP sotuvchini topish, kategoriya bo'yicha statistika, eng yaxshi 3 sotuvchi.</p>

<h3>🏆 5 daqiqada g'alaba — bitta katta misol</h3>

<pre><code>savdolar = [
    {"sotuvchi": "Ali",  "mahsulot": "noutbuk",  "narx": 12_000_000},
    {"sotuvchi": "Vali", "mahsulot": "telefon",  "narx": 5_500_000},
    {"sotuvchi": "Ali",  "mahsulot": "klaviatura","narx": 450_000},
    {"sotuvchi": "Gulya","mahsulot": "monitor",  "narx": 3_200_000},
    {"sotuvchi": "Vali", "mahsulot": "noutbuk",  "narx": 11_800_000},
    {"sotuvchi": "Ali",  "mahsulot": "telefon",  "narx": 6_200_000},
]

# 1) Sotuvchilar to'plami — set comprehension
sotuvchilar = {s["sotuvchi"] for s in savdolar}
print(sotuvchilar)

# 2) Har sotuvchi uchun jami summa — dict comprehension + generator
jami_summa = {
    sotuvchi: sum(s["narx"] for s in savdolar if s["sotuvchi"] == sotuvchi)
    for sotuvchi in sotuvchilar
}
print(jami_summa)

# 3) TOP — sorted + key=
top = sorted(jami_summa.items(), key=lambda x: x[1], reverse=True)
print("TOP:", top)

# 4) Eng qimmat mahsulotni sotgan kim?
eng_qimmat = max(savdolar, key=lambda s: s["narx"])
print(f"Eng qimmat: {eng_qimmat['sotuvchi']} — {eng_qimmat['mahsulot']}")
</code></pre>

<h3>3 ta texnikani birga ko'rib chiqamiz</h3>

<h4>Comprehension — yangi shakl</h4>
<ul>
<li>Set comprehension takrorni o'chiradi: <code>{s["sotuvchi"] for s in savdolar}</code></li>
<li>Dict comprehension agregatsiya uchun ideal</li>
<li>Generator expression <code>sum()</code>, <code>max()</code> ichida — xotirani band qilmaydi</li>
</ul>

<h4>Generator — oqim</h4>
<ul>
<li><code>sum(s["narx"] for s in savdolar if s["sotuvchi"] == sotuvchi)</code> — bu <strong>generator expression</strong>, list yaratmaydi</li>
<li>Katta CSV / log fayl bilan ishlasangiz — pipeline pattern (avvalgi darsdan)</li>
</ul>

<h4>Lambda + key</h4>
<ul>
<li><code>sorted(..., key=lambda x: x[1])</code> — tuple'lar list'ini ikkinchi qiymat bo'yicha saralaydi</li>
<li><code>max</code>, <code>min</code> ham <code>key=</code> qabul qiladi</li>
<li>Bir nechta mezon — <code>key=lambda x: (-x.summa, x.ism)</code></li>
</ul>

<h3>📌 Module 1 ni siz endi bilasiz</h3>
<ul>
<li>Yangi kolleksiya yaratish — <strong>comprehension</strong></li>
<li>Katta yoki tek martalik oqim — <strong>generator</strong></li>
<li>Saralash / agregatsiya — <strong>lambda + key=</strong></li>
<li>Bu 3 ta birga ishlaganda — siz "ma'lumotlar bilan ishlovchi" Python kodisiz</li>
</ul>
"""

R1_CODE = """\
# ─── R1: Sotuvchi statistikasi to'liq misoli ──────────────────────────────
from collections import defaultdict
from operator import itemgetter

savdolar = [
    {"sotuvchi": "Ali",   "mahsulot": "noutbuk",   "narx": 12_000_000, "miqdori": 1},
    {"sotuvchi": "Vali",  "mahsulot": "telefon",   "narx":  5_500_000, "miqdori": 2},
    {"sotuvchi": "Ali",   "mahsulot": "klaviatura","narx":    450_000, "miqdori": 3},
    {"sotuvchi": "Gulya", "mahsulot": "monitor",   "narx":  3_200_000, "miqdori": 1},
    {"sotuvchi": "Vali",  "mahsulot": "noutbuk",   "narx": 11_800_000, "miqdori": 1},
    {"sotuvchi": "Ali",   "mahsulot": "telefon",   "narx":  6_200_000, "miqdori": 1},
    {"sotuvchi": "Doniyor","mahsulot":"monitor",   "narx":  3_500_000, "miqdori": 2},
]

# 1) Jami summa har savdo uchun (generator expression, list yaratmaydi)
jami = sum(s["narx"] * s["miqdori"] for s in savdolar)
print(f"Jami savdo: {jami:,} so'm")

# 2) Sotuvchilar to'plami — set comprehension
sotuvchilar = sorted({s["sotuvchi"] for s in savdolar})
print("Sotuvchilar:", sotuvchilar)

# 3) Har sotuvchi uchun jami — dict comprehension
jami_per_sot = {
    sot: sum(s["narx"] * s["miqdori"] for s in savdolar if s["sotuvchi"] == sot)
    for sot in sotuvchilar
}
print("Sotuvchi -> jami:", jami_per_sot)

# 4) TOP 3 sotuvchi
top_3 = sorted(jami_per_sot.items(), key=lambda x: x[1], reverse=True)[:3]
print("\\nTOP 3 sotuvchi:")
for o_rin, (ism, sum_val) in enumerate(top_3, start=1):
    print(f"  {o_rin}. {ism:<10}  {sum_val:>12,} so'm")

# 5) Eng qimmat bitta savdo
eng_qimmat = max(savdolar, key=lambda s: s["narx"])
print(f"\\nEng qimmat: {eng_qimmat['sotuvchi']} — "
      f"{eng_qimmat['mahsulot']} ({eng_qimmat['narx']:,})")

# 6) Filter: 5M dan ortiq savdolar
katta = [s for s in savdolar if s["narx"] >= 5_000_000]
print(f"\\n5M+ savdolar: {len(katta)} ta")

# 7) Generator pipeline — pythonic oqim
def faqat_kategoriya(savdolar, mahsulot):
    for s in savdolar:
        if s["mahsulot"] == mahsulot:
            yield s

def faqat_qimmatlar(oqim, eng_kam):
    for s in oqim:
        if s["narx"] >= eng_kam:
            yield s

# "noutbuk" toifasidagi 10M+ savdolar
oqim = faqat_qimmatlar(faqat_kategoriya(savdolar, "noutbuk"), 10_000_000)
for s in oqim:
    print(s)

# 8) defaultdict bilan agregatsiya (collections moduli)
mahsulot_jami = defaultdict(int)
for s in savdolar:
    mahsulot_jami[s["mahsulot"]] += s["narx"] * s["miqdori"]

print("\\nMahsulot bo'yicha jami:")
for nom, summa in sorted(mahsulot_jami.items(), key=itemgetter(1), reverse=True):
    print(f"  {nom:<12}  {summa:>12,} so'm")
"""

L4_TEXT = """\
<h2><code>*args</code>, <code>**kwargs</code> va unpacking</h2>

<pre class="mermaid">
flowchart LR
    CALL["chaqiruv: f(1, 2, x=3)"] -->|positional| ARGS["*args -> tuple (1, 2)"]
    CALL -->|keyword| KW["**kwargs -> dict {x: 3}"]
    LIST["list [1,2,3]"] -->|*list ochish| F1["f(1, 2, 3)"]
    DICT["dict a:1, b:2"] -->|**dict ochish| F2["f(a=1, b=2)"]
</pre>

<p><strong>Yulduzcha</strong> Python'da ikki ma'noda ishlatiladi: <em>funksiya tanasida</em> argumentlarni "yig'ish" uchun va <em>chaqiruv joyida</em> kolleksiyani "ochib yuborish" uchun. Bu bilan istalgan sondagi argumentni qabul qiluvchi va boshqalarga qayta uzatuvchi funksiyalar yoziladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — *args (istalgan sondagi pozitsion)</h4>
<pre><code>def jami(*sonlar):
    return sum(sonlar)

print(jami(1, 2, 3))            # 6
print(jami(10, 20, 30, 40, 50)) # 150
print(jami())                    # 0

# Tanasida `sonlar` — bu tuple
def show(*sonlar):
    print(type(sonlar), sonlar)

show(1, 2, 3)   # &lt;class 'tuple'&gt; (1, 2, 3)</code></pre>

<h4>BLOKA 2 — **kwargs (istalgan keyword argument)</h4>
<pre><code>def foydalanuvchi_yaratish(**maydonlar):
    print(maydonlar)

foydalanuvchi_yaratish(ism="Ali", yosh=21, kasb="dev")
# {'ism': 'Ali', 'yosh': 21, 'kasb': 'dev'}

# args + kwargs birga
def log(level, *xabarlar, **meta):
    print(level, xabarlar, meta)

log("INFO", "server", "start", request_id=42, user="ali")</code></pre>

<h4>BLOKA 3 — Unpacking — yulduzcha chaqiruvda</h4>
<pre><code>def qosh(a, b, c):
    return a + b + c

nums = [10, 20, 30]
print(qosh(*nums))         # = qosh(10, 20, 30) = 60

cfg = {"a": 1, "b": 2, "c": 3}
print(qosh(**cfg))         # = qosh(a=1, b=2, c=3) = 6

# Tuple va list ochib yuborish
a, *qolgani = [1, 2, 3, 4, 5]
print(a)            # 1
print(qolgani)      # [2, 3, 4, 5]

a, *o_rta, oxirgi = [1, 2, 3, 4, 5]
print(o_rta)        # [2, 3, 4]
print(oxirgi)       # 5</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>def buggy(**kwargs, *args):
    print(args, kwargs)

buggy(1, 2, x=3)</code></pre>
<p><strong>Natija:</strong> <code>SyntaxError</code>. <strong>Tartib qat'iy</strong>: oddiy positional → <code>*args</code> → keyword-only → <code>**kwargs</code>. <code>**kwargs</code> doim oxirgi. To'g'ri: <code>def f(*args, **kwargs):</code></p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Parametrlar tartibi (yodlang)</h4>
<pre><code>def f(pos1, pos2, /, oddiy1, oddiy2, *args, faqat_kw1, faqat_kw2, **kwargs):
    pass
#     ^^^^^^^^^^  ^^^^^^^^^^^^^^^^  ^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^
#     positional   normal           args   keyword-only             kwargs
#     -only        (oba turda)            (faqat ism bilan)</code></pre>
<ul>
<li><code>/</code> — undan oldingilar <strong>faqat positional</strong></li>
<li><code>*args</code> — qolgan positional'lar tuple ga yig'iladi</li>
<li><code>*args</code> dan keyingilar — <strong>keyword-only</strong> (ism bilan kerak)</li>
<li><code>**kwargs</code> — doim oxirgi, qolgan keyword'lar dict ga yig'iladi</li>
</ul>

<h4>2. Keyword-only argumentlar — xavfsizlik vositasi</h4>
<pre><code># Yomon — pozitsiya bilan chaqirsa, ma'no chalkash
def yuborish(adress, port, ssl):
    pass

yuborish("ya.ru", 443, True)   # 443 — port? 80? Boolean qaerda?

# Yaxshi — keyword-only
def yuborish(adress, *, port, ssl=False):
    pass

yuborish("ya.ru", port=443, ssl=True)  # aniq, o'qimli</code></pre>

<h4>3. Unpacking xato sodir bo'ladigan joylar</h4>
<pre><code>def f(a, b, c):
    pass

nums = [1, 2]
# f(*nums)             # TypeError: c yo'q

nums = [1, 2, 3, 4]
# f(*nums)             # TypeError: ortiqcha 1 ta argument

# Dict unpacking — bir xil kalit ikki marta bo'lmasin
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}
# Yangi sintaksis — birlashma
birlashma = {**d1, **d2}
print(birlashma)       # {'a': 1, 'b': 99, 'c': 3}  — d2 'b' ustunlik qiladi</code></pre>

<h4>4. Wrapper pattern — ko'p uchraydigan idiom</h4>
<pre><code>def loglashtirilgan(funk):
    def wrapper(*args, **kwargs):
        print(f"Chaqirilmoqda: {funk.__name__} args={args} kwargs={kwargs}")
        natija = funk(*args, **kwargs)
        print(f"Qaytdi: {natija}")
        return natija
    return wrapper

# Decoratorlar — keyingi darsda. Lekin *args/**kwargs siz ularni
# yozib bo'lmaydi.</code></pre>

<h4>5. * — list/tuple/dict birlashtirish (Python 3.5+)</h4>
<pre><code># List birlashtirish
a = [1, 2, 3]
b = [4, 5, 6]
birga = [*a, *b, 100]            # [1, 2, 3, 4, 5, 6, 100]

# Dict birlashtirish
defaults = {"theme": "dark", "lang": "uz"}
override = {"lang": "en"}
final = {**defaults, **override}  # {'theme': 'dark', 'lang': 'en'}</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>*args</code> — tanasida positional'larni tuple ga yig'adi</li>
<li><code>**kwargs</code> — tanasida keyword'larni dict ga yig'adi</li>
<li>Chaqiruv joyida <code>*list</code> / <code>**dict</code> — ochib yuborish (unpacking)</li>
<li>Tartib: positional → <code>*args</code> → keyword-only → <code>**kwargs</code></li>
<li><code>{**a, **b}</code> — dict'larni birlashtirish; <code>[*a, *b]</code> — list'larni</li>
</ul>
"""

L4_CODE = """\
# ─── *args, **kwargs va unpacking — to'liq sweep ─────────────────────────

# 1) *args — istalgan sondagi pozitsion
def eng_kattasi(*sonlar):
    if not sonlar:
        return None
    return max(sonlar)

print(eng_kattasi(3, 7, 2, 9, 4))     # 9
print(eng_kattasi())                   # None

# 2) **kwargs — istalgan keyword
def obyekt_yaratish(**maydonlar):
    return maydonlar

user = obyekt_yaratish(ism="Ali", yosh=21, faol=True)
print(user)

# 3) Birga ishlatish
def chaqiruv_logi(funk_nomi, *args, **kwargs):
    args_str = ", ".join(str(a) for a in args)
    kw_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    barchasi = ", ".join(filter(None, [args_str, kw_str]))
    print(f"{funk_nomi}({barchasi})")

chaqiruv_logi("send", "ya.ru", 443, ssl=True, retry=3)

# 4) Keyword-only — xavfsiz API
def fayl_o_chirish(yo_l, *, tasdiqlash=False, backup=True):
    if not tasdiqlash:
        raise ValueError("tasdiqlash=True kerak")
    print(f"O'chirilmoqda: {yo_l} (backup={backup})")

# fayl_o_chirish("/tmp/x", True)            # TypeError — keyword bilan kerak
fayl_o_chirish("/tmp/x", tasdiqlash=True)   # OK

# 5) Unpacking chaqiruvda
def maydon(en, bo_y, baland):
    return en * bo_y * baland

oC_lcham = [3, 4, 5]
print(maydon(*oC_lcham))      # 60

konfig = {"en": 3, "bo_y": 4, "baland": 5}
print(maydon(**konfig))       # 60

# 6) Variable unpacking
boshlanish, *o_rta, oxirgi = list(range(10))
print(boshlanish, oxirgi, "o'rta uzunligi:", len(o_rta))

# 7) Dict birlashtirish
default_kfg = {"timeout": 30, "retries": 3, "log": "info"}
user_kfg    = {"timeout": 60, "verbose": True}
final_kfg   = {**default_kfg, **user_kfg}
print(final_kfg)
# {'timeout': 60, 'retries': 3, 'log': 'info', 'verbose': True}

# 8) Wrapper pattern — *args, **kwargs siz yozib bo'lmaydi
def chaqiruv_son(funk):
    counter = {"n": 0}
    def wrapper(*args, **kwargs):
        counter["n"] += 1
        print(f"[{counter['n']}-marta chaqirildi]")
        return funk(*args, **kwargs)
    return wrapper

@chaqiruv_son
def salom(ism):
    return f"Salom, {ism}!"

print(salom("Ali"))
print(salom("Vali"))
print(salom("Gulya"))
"""

L5_TEXT = """\
<h2>Dekoratorlar — funksiyani "qayta o'rab" yangi qobiliyat beradi</h2>

<pre class="mermaid">
flowchart LR
    FUNC["original f"] -->|decorator(f)| WRAP["wrapper funksiyasi"]
    WRAP -->|chaqiruvda| BEFORE["oldindan logika"]
    BEFORE --> CALL_F["f(*args, **kwargs)"]
    CALL_F --> AFTER["keyin logika"]
    AFTER --> OUT["natija"]
</pre>

<p><strong>Dekorator</strong> — funksiyani argument sifatida qabul qilib, yangi (kengaytirilgan) funksiya qaytaradigan funksiya. <code>@decorator</code> sintaksisi <code>f = decorator(f)</code> ning qisqartmasi. Logging, timing, caching, retry — bularning hammasi dekorator bilan bir qatorga sig'adi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Eng oddiy timer dekoratori</h4>
<pre><code>import time

def timer(funk):
    def wrapper(*args, **kwargs):
        boshlanish = time.perf_counter()
        natija = funk(*args, **kwargs)
        tugadi = time.perf_counter() - boshlanish
        print(f"{funk.__name__} — {tugadi:.4f}s")
        return natija
    return wrapper

@timer
def sekin_summa(n):
    return sum(i * i for i in range(n))

print(sekin_summa(1_000_000))
# sekin_summa — 0.0823s
# 333332833333500000</code></pre>

<h4>BLOKA 2 — functools.lru_cache (1 qator → memoization)</h4>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n &lt; 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))   # 354224848179261915075 — bir lahzada
# lru_cache bo'lmasa — bir umr kutardik</code></pre>

<h4>BLOKA 3 — Parametrli dekorator (retry)</h4>
<pre><code>import random

def retry(marotaba=3):
    def haqiqiy_dekorator(funk):
        def wrapper(*args, **kwargs):
            for urinish in range(marotaba):
                try:
                    return funk(*args, **kwargs)
                except Exception as xato:
                    print(f"Urinish {urinish+1}: {xato}")
            raise RuntimeError(f"{marotaba} marta urinishdan keyin muvaffaqiyatsiz")
        return wrapper
    return haqiqiy_dekorator

@retry(marotaba=5)
def shubhali():
    if random.random() &lt; 0.7:
        raise ValueError("Tarmoq xatosi")
    return "Muvaffaqiyatli!"

print(shubhali())</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>def timer(funk):
    def wrapper(*args, **kwargs):
        return funk(*args, **kwargs)
    return wrapper

@timer
def assalom(ism):
    "Bu funksiya salom beradi"
    return f"Salom, {ism}!"

print(assalom.__name__)   # ???
print(assalom.__doc__)    # ???</code></pre>
<p><strong>Natija:</strong> <code>__name__</code> = "wrapper", <code>__doc__</code> = None. Dekorator funksiya metadata'sini <strong>yutib yuboradi</strong>. Yechim:</p>
<pre><code>from functools import wraps

def timer(funk):
    @wraps(funk)                  # &lt;-- metadata'ni saqlaydi
    def wrapper(*args, **kwargs):
        return funk(*args, **kwargs)
    return wrapper</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>@</code> nimaning qisqartmasi?</h4>
<pre><code>@timer
def f(x):
    return x * 2

# Ekvivalent:
def f(x):
    return x * 2
f = timer(f)</code></pre>
<p>Boshqa hech qanday sehrli narsa yo'q. <code>@</code> — sintaktik shakar.</p>

<h4>2. Dekoratorning 3 qatlami</h4>
<pre><code>def parametrli_dek(parametr):       # 1) parametrlarni qabul qiladi
    def dek(funk):                  # 2) funksiyani qabul qiladi
        @wraps(funk)
        def wrapper(*args, **kw):   # 3) chaqiruvni qabul qiladi
            # ... oldidan
            res = funk(*args, **kw)
            # ... keyin
            return res
        return wrapper
    return dek</code></pre>
<ul>
<li><strong>Parametrsiz</strong> dekoratorda faqat 2 va 3 darajalari bor</li>
<li><strong>Parametrli</strong> dekoratorda 1, 2, 3 darajalari</li>
<li><code>@wraps(funk)</code> — har doim qo'shing</li>
</ul>

<h4>3. Standart kutubxonadagi tayyor dekoratorlar</h4>
<table>
<tr><th>Dekorator</th><th>Maqsadi</th></tr>
<tr><td><code>@functools.lru_cache</code></td><td>Memoization — bir xil argument bilan qayta hisoblamaslik</td></tr>
<tr><td><code>@functools.cached_property</code></td><td>Class atributi sifatida lazy hisoblash</td></tr>
<tr><td><code>@property</code></td><td>Atributga geter (10-darsda)</td></tr>
<tr><td><code>@staticmethod</code> / <code>@classmethod</code></td><td>OOP — instance kerak emas</td></tr>
<tr><td><code>@dataclass</code></td><td>Class'ni dataclass'ga aylantirish (6-dars)</td></tr>
</table>

<h4>4. Bir necha dekoratorni stack qilish</h4>
<pre><code>@timer
@retry(marotaba=3)
def fetch():
    ...

# Ekvivalent: fetch = timer(retry(marotaba=3)(fetch))
# Eng pastdagi @retry birinchi qo'llaniladi, keyin @timer</code></pre>
<p><strong>Tartib muhim</strong> — eng pastdagi dekorator funksiyaga eng yaqin.</p>

<h4>5. Qachon dekorator?</h4>
<ul>
<li>Bir necha funksiyaga <strong>bir xil "g'ilof"</strong> kerak (timing, logging, auth check)</li>
<li>Original funksiya tanasini <strong>o'zgartirmasdan</strong> xulq qo'shish</li>
<li>Tezda yoqib-o'chirish: <code>@cache</code> ni olib tashlash — kod qaytadan ishlaydi</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>@dec</code> — bu <code>f = dec(f)</code> ning qisqartmasi</li>
<li>Dekorator wrapper'ida <code>*args, **kwargs</code> ishlatib istalgan funksiyani o'rab oling</li>
<li><code>@functools.wraps</code> — metadata'ni saqlaydi (har doim qo'shing)</li>
<li>Parametrli dekorator — 3 qatlam (param → funk → wrapper)</li>
<li><code>@lru_cache</code>, <code>@cached_property</code> — bepul caching</li>
</ul>
"""

L5_CODE = """\
# ─── Dekoratorlar amaliyoti ──────────────────────────────────────────────
import time
import random
from functools import wraps, lru_cache

# 1) Eng oddiy timer
def timer(funk):
    @wraps(funk)
    def wrapper(*args, **kwargs):
        boshlanish = time.perf_counter()
        natija = funk(*args, **kwargs)
        tugadi = time.perf_counter() - boshlanish
        print(f"⏱  {funk.__name__:<20} {tugadi*1000:>8.2f} ms")
        return natija
    return wrapper

@timer
def sekin(n):
    return sum(i * i for i in range(n))

sekin(500_000)
print(sekin.__name__)   # "sekin" — wraps tufayli

# 2) lru_cache — fibonacci tezligi
@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))    # bir lahzada

# 3) Parametrli retry
def retry(marotaba=3, kutish=0.1):
    def dek(funk):
        @wraps(funk)
        def wrapper(*args, **kwargs):
            oxirgi_xato = None
            for u in range(marotaba):
                try:
                    return funk(*args, **kwargs)
                except Exception as e:
                    oxirgi_xato = e
                    print(f"  urinish {u+1}/{marotaba} ❌ {e}")
                    time.sleep(kutish)
            raise oxirgi_xato
        return wrapper
    return dek

@retry(marotaba=5, kutish=0.05)
def shubhali_api():
    if random.random() < 0.6:
        raise ConnectionError("network down")
    return {"ok": True}

print(shubhali_api())

# 4) Authorization dekoratori — chaqiruvni bloklaydi
def faqat_admin(funk):
    @wraps(funk)
    def wrapper(foydalanuvchi, *args, **kwargs):
        if foydalanuvchi.get("rol") != "admin":
            raise PermissionError("Faqat admin uchun")
        return funk(foydalanuvchi, *args, **kwargs)
    return wrapper

@faqat_admin
def o_chirish(foydalanuvchi, fayl):
    print(f"{fayl} o'chirildi")

o_chirish({"rol": "admin"}, "/tmp/x")
# o_chirish({"rol": "user"}, "/tmp/x")     # PermissionError

# 5) Dekoratorlar stacki — tartib muhim
@timer
@retry(marotaba=3)
def ko_p_qatlamli():
    if random.random() < 0.5:
        raise ValueError("ko'p urinish kerak")
    return 42

print(ko_p_qatlamli())

# 6) cached_property — class atributi sifatida lazy hisob
class Hisoblovchi:
    def __init__(self, sonlar):
        self.sonlar = sonlar

    @property
    def jami(self):                       # har murojaatda qayta hisoblanadi
        print("(jami hisoblanmoqda)")
        return sum(self.sonlar)

h = Hisoblovchi([1, 2, 3, 4, 5])
print(h.jami)
print(h.jami)                              # qayta hisoblanadi
"""

L6_TEXT = """\
<h2>Type hints va dataclasses — kodga "shakl" beradi</h2>

<pre class="mermaid">
flowchart LR
    DICT["dict — kalitlar yashirin"] -->|@dataclass| CLASS["aniq class"]
    CLASS -->|type hints| IDE["IDE autocomplete"]
    CLASS -->|__init__/__repr__/__eq__| TEKIN["bepul metodlar"]
    HINTS["x: int, name: str"] -->|mypy| LINT["statik tekshirish"]
</pre>

<p>Endi siz <strong>dict bilan ma'lumot tashish</strong> uslubini tashlaysiz. <code>@dataclass</code> bilan har bir ma'lumot strukturasi <strong>aniq nomli class</strong> bo'ladi. Type hints bilan IDE sizga autocomplete va xato uchun ogohlantirish beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Eski uslub vs dataclass</h4>
<pre><code># Eski uslub — dict
foydalanuvchi = {"ism": "Ali", "yosh": 21, "email": "ali@ya.ru"}

# Tekshirish kerak: kalit borligi, tipi, default qiymat...
print(foydalanuvchi.get("ism"))   # bor-yo'qligi noaniq

# Pythonic
from dataclasses import dataclass

@dataclass
class Foydalanuvchi:
    ism: str
    yosh: int
    email: str = ""

f = Foydalanuvchi("Ali", 21, "ali@ya.ru")
print(f)
# Foydalanuvchi(ism='Ali', yosh=21, email='ali@ya.ru')
print(f.ism)                      # autocomplete bilan</code></pre>

<h4>BLOKA 2 — Type hints funksiyalarda</h4>
<pre><code>def salomlash(ism: str, marotaba: int = 1) -> str:
    return ("Salom, " + ism + "! ") * marotaba

print(salomlash("Ali", 3))

# Murakkab turlar
def filterlash(sonlar: list[int], min_qiymat: int) -> list[int]:
    return [x for x in sonlar if x &gt;= min_qiymat]

# Optional — qiymat None ham bo'lishi mumkin
def topish(id: int) -> Foydalanuvchi | None:
    ...</code></pre>

<h4>BLOKA 3 — Dataclass'ning bonuslari</h4>
<pre><code>@dataclass
class Nuqta:
    x: float
    y: float

a = Nuqta(1.0, 2.0)
b = Nuqta(1.0, 2.0)
c = Nuqta(3.0, 4.0)

print(a == b)              # True — __eq__ bepul
print(a == c)              # False
print(repr(a))             # Nuqta(x=1.0, y=2.0) — bepul __repr__

# Frozen — immutable
@dataclass(frozen=True)
class Pul:
    summa: float
    valyuta: str

p = Pul(100.0, "USD")
# p.summa = 200          # FrozenInstanceError</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>@dataclass
class Savat:
    mahsulotlar: list = []     # ⚠️

s1 = Savat()
s2 = Savat()
s1.mahsulotlar.append("olma")
print(s2.mahsulotlar)          # ???</code></pre>
<p><strong>Natija:</strong> <code>ValueError</code> (yangi Python'larda) yoki <code>['olma']</code> (eski versiyalarda) — bo'sh savat bo'lishi kerak edi. Sabab: <strong>mutable default</strong> hammasi uchun bir xil obyekt. To'g'ri:</p>
<pre><code>from dataclasses import dataclass, field

@dataclass
class Savat:
    mahsulotlar: list = field(default_factory=list)   # ✅ har instance uchun yangi list</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Type hints — Python ularni TEKSHIRMAYDI</h4>
<pre><code>def f(x: int) -> str:
    return x * 2     # int qaytaradi — Python xato bermaydi

f("salom")          # str ham qabul qiladi — runtime'da</code></pre>
<p>Type hints — bu <strong>sizga, IDE'ga va mypy'ga</strong> ishora. Python runtime'da tekshirmaydi. Lekin:</p>
<ul>
<li>IDE autocomplete va xato ogohlantirishi</li>
<li><code>mypy fayl.py</code> — statik tekshiruv</li>
<li><code>@dataclass</code>, <code>pydantic</code>, FastAPI — type hints'dan foydalanadi</li>
<li>Dokumentatsiya — kod o'qishni osonlashtiradi</li>
</ul>

<h4>2. Tez-tez kerak bo'ladigan turlar</h4>
<table>
<tr><th>Tur</th><th>Misol</th></tr>
<tr><td><code>int, str, float, bool</code></td><td>asosiy</td></tr>
<tr><td><code>list[int]</code></td><td>butun sonlar ro'yxati</td></tr>
<tr><td><code>dict[str, int]</code></td><td>string -&gt; int dict</td></tr>
<tr><td><code>tuple[str, int]</code></td><td>aniq juftlik</td></tr>
<tr><td><code>X | None</code></td><td>X yoki None (Optional)</td></tr>
<tr><td><code>X | Y</code></td><td>X yoki Y (Union)</td></tr>
<tr><td><code>Callable[[int], str]</code></td><td>funksiya turi</td></tr>
</table>
<p>Python 3.10+ da <code>list[int]</code>, <code>X | None</code> sintaksisi ishlaydi. Eski versiyada: <code>from typing import List, Optional</code> va <code>List[int]</code>, <code>Optional[X]</code>.</p>

<h4>3. @dataclass — bepul nima oladi?</h4>
<ul>
<li><code>__init__</code> — <code>Foydalanuvchi(ism="Ali", yosh=21)</code></li>
<li><code>__repr__</code> — print qilganda chiroyli ko'rinish</li>
<li><code>__eq__</code> — bir xil maydonli ikki instance teng</li>
<li><code>frozen=True</code> — immutable</li>
<li><code>order=True</code> — taqqoslash operatorlari (<, >=)</li>
</ul>

<h4>4. dataclass va dict — qachon qaysi?</h4>
<table>
<tr><th>Dataclass</th><th>dict</th></tr>
<tr><td>Shakli aniq, doimiy</td><td>Shakli o'zgaruvchan / kalit dinamik</td></tr>
<tr><td>Bir necha joyda ishlatiladi</td><td>Bir martalik</td></tr>
<tr><td>Type hints bilan</td><td>JSON dan parse qilingan</td></tr>
<tr><td>Metod qo'shish kerak</td><td>Faqat saqlash</td></tr>
</table>

<h4>5. dataclass ichida metod ham bo'ladi</h4>
<pre><code>@dataclass
class Doira:
    radius: float

    def maydon(self) -&gt; float:
        import math
        return math.pi * self.radius ** 2

    def aylana(self) -&gt; float:
        import math
        return 2 * math.pi * self.radius

d = Doira(5.0)
print(d.maydon())</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Type hints — IDE va mypy uchun; Python runtime'da tekshirmaydi</li>
<li><code>@dataclass</code> — class'ni bir necha qatorda yozish, <code>__init__/__repr__/__eq__</code> bepul</li>
<li>Mutable default ⚠️ — <code>field(default_factory=list)</code> ishlating</li>
<li><code>frozen=True</code> — immutable struktura</li>
<li><code>dict</code> dinamik, <code>dataclass</code> aniq shakl uchun</li>
</ul>
"""

L6_CODE = """\
# ─── Type hints va dataclasses — sweep ───────────────────────────────────
from dataclasses import dataclass, field, asdict
from typing import Callable
import math


# 1) Oddiy type hints
def ulushni_olish(narx: float, foiz: float) -> float:
    return narx * foiz / 100

print(ulushni_olish(50000, 15))

# 2) Murakkab — list[int], dict[str, X], X | None
def eng_yaxshi_ball(ballar: list[int]) -> int | None:
    return max(ballar) if ballar else None

print(eng_yaxshi_ball([72, 88, 95, 60]))
print(eng_yaxshi_ball([]))

# 3) Callable — funksiya turi
def shartga_qarab(sonlar: list[int], shart: Callable[[int], bool]) -> list[int]:
    return [x for x in sonlar if shart(x)]

print(shartga_qarab([1, 2, 3, 4, 5], lambda x: x > 2))

# 4) Dataclass — minimal
@dataclass
class Foydalanuvchi:
    ism: str
    yosh: int
    email: str = ""

ali = Foydalanuvchi("Ali", 21, "ali@ya.ru")
print(ali)
print(ali == Foydalanuvchi("Ali", 21, "ali@ya.ru"))

# 5) Mutable default — to'g'ri yo'l
@dataclass
class Savat:
    egasi: str
    mahsulotlar: list[str] = field(default_factory=list)
    chegirma: float = 0.0

s1 = Savat("Ali")
s2 = Savat("Vali")
s1.mahsulotlar.append("Olma")
print(s1.mahsulotlar)    # ['Olma']
print(s2.mahsulotlar)    # [] — alohida list

# 6) frozen=True — immutable
@dataclass(frozen=True)
class Pul:
    summa: float
    valyuta: str

p = Pul(100.0, "USD")
# p.summa = 200    # FrozenInstanceError

# 7) Method ham bo'ladi
@dataclass
class Doira:
    radius: float

    def maydon(self) -> float:
        return math.pi * self.radius ** 2

    def aylana(self) -> float:
        return 2 * math.pi * self.radius

d = Doira(5.0)
print(f"Maydon: {d.maydon():.2f}  Aylana: {d.aylana():.2f}")

# 8) asdict — dict ga konvertatsiya (JSON uchun foydali, 7-darsda)
@dataclass
class Vazifa:
    id: int
    matn: str
    bajarildi: bool = False
    teglar: list[str] = field(default_factory=list)

v = Vazifa(1, "Python o'rganish", teglar=["learn", "code"])
print(asdict(v))
# {'id': 1, 'matn': "Python o'rganish", 'bajarildi': False, 'teglar': ['learn', 'code']}

# 9) order=True — taqqoslash uchun
@dataclass(order=True)
class Talaba:
    ball: int
    ism: str = field(compare=False)

talabalar = [Talaba(85, "Ali"), Talaba(92, "Vali"), Talaba(70, "Gulya")]
print(sorted(talabalar, reverse=True))
"""

R2_TEXT = """\
<h2>🔁 R2 — Mini analytics dashboard (Modul 2 takrori)</h2>

<pre class="mermaid">
flowchart LR
    LOGS["log yozuvlari"] -->|@dataclass| OBJ["LogYozuv obyektlari"]
    OBJ -->|@timed dekorator| METRICS["agregatsiya"]
    OBJ -->|*args/**kwargs| PIPE["pipeline"]
    METRICS --> REPORT["report dict"]
</pre>

<p>Modul 2 ning 3 ta texnikasi: <strong>*args/**kwargs</strong>, <strong>dekoratorlar</strong>, <strong>dataclasses+typing</strong>. Mavzu: server log'larini tahlil qiluvchi mini dashboard. <em>Real</em> data, har bir bosqich sof Python idiomalari bilan.</p>

<h3>🏆 5 daqiqada g'alaba — 3 ta texnika birga</h3>

<pre><code>from dataclasses import dataclass, field
from functools import wraps
import time

# 1) Dataclass — log yozuv shakli
@dataclass
class LogYozuv:
    sana: str
    level: str
    xabar: str
    foydalanuvchi_id: int | None = None
    meta: dict = field(default_factory=dict)

# 2) Dekorator — har funksiyaning vaqtini o'lchaydi
def timed(funk):
    @wraps(funk)
    def wrapper(*args, **kwargs):
        b = time.perf_counter()
        natija = funk(*args, **kwargs)
        print(f"⏱  {funk.__name__}: {(time.perf_counter()-b)*1000:.2f}ms")
        return natija
    return wrapper

# 3) Pipeline funksiyalar — *args, **kwargs bilan
@timed
def report(yozuvlar, **filtrlar):
    # ERROR / WARN / INFO bo'yicha agregatsiya
    natija = {"jami": len(yozuvlar)}
    for level in ("ERROR", "WARN", "INFO"):
        natija[level] = sum(1 for y in yozuvlar if y.level == level)
    return natija
</code></pre>

<h3>Module 2 ning kalit takrorlash nuqtalari</h3>

<h4>*args / **kwargs</h4>
<ul>
<li>Funksiya tanasida — argumentlarni yig'ish</li>
<li>Chaqiruv joyida — kolleksiyalarni ochib yuborish</li>
<li>Wrapper / decorator yozish uchun majburiy</li>
</ul>

<h4>Decorators</h4>
<ul>
<li><code>@</code> = <code>f = dec(f)</code></li>
<li><code>@wraps(funk)</code> — metadata saqlaydi</li>
<li>Parametrli dekorator — 3 qatlam (param → funk → wrapper)</li>
</ul>

<h4>Dataclasses + typing</h4>
<ul>
<li>Aniq nomli class — dict'dan o'qimliroq</li>
<li>Mutable default uchun <code>field(default_factory=list)</code></li>
<li><code>frozen=True</code> — immutable, hashable</li>
<li>Type hints — IDE, mypy va dokumentatsiya uchun</li>
</ul>

<h3>📌 Module 2 ni siz endi bilasiz</h3>
<ul>
<li>Tabularasaning shaklini <code>@dataclass</code> bilan aniqlaysiz</li>
<li>Behavior'ni dekoratorlar bilan qo'shasiz va olib tashlaysiz</li>
<li>API'larni <code>*args, **kwargs</code> bilan moslashuvchan qilasiz</li>
<li>Type hints — IDE va siz uchun "shartnoma"</li>
</ul>
"""

R2_CODE = """\
# ─── R2: Mini analytics dashboard — 3 texnika birga ───────────────────────
from dataclasses import dataclass, field, asdict
from functools import wraps
from collections import Counter
import time

# 1) Dataclass — log yozuv shakli
@dataclass
class LogYozuv:
    sana: str
    level: str
    xabar: str
    foydalanuvchi_id: int | None = None
    meta: dict = field(default_factory=dict)


# 2) Dekorator — funksiya vaqtini o'lchaydi
def timed(funk):
    @wraps(funk)
    def wrapper(*args, **kwargs):
        b = time.perf_counter()
        natija = funk(*args, **kwargs)
        ms = (time.perf_counter() - b) * 1000
        print(f"⏱  {funk.__name__:<20} {ms:>6.2f} ms")
        return natija
    return wrapper


# 3) Test data
yozuvlar = [
    LogYozuv("2026-06-01", "INFO",  "server start"),
    LogYozuv("2026-06-01", "INFO",  "login OK",     foydalanuvchi_id=1),
    LogYozuv("2026-06-01", "ERROR", "db timeout",   meta={"q": "SELECT *"}),
    LogYozuv("2026-06-01", "WARN",  "slow query",   foydalanuvchi_id=1),
    LogYozuv("2026-06-02", "INFO",  "login OK",     foydalanuvchi_id=2),
    LogYozuv("2026-06-02", "ERROR", "auth failed",  foydalanuvchi_id=99),
    LogYozuv("2026-06-02", "ERROR", "db connect",   meta={"host": "primary"}),
    LogYozuv("2026-06-02", "INFO",  "logout",       foydalanuvchi_id=2),
]


# 4) Analytics funksiyalar — har biri dekoratorlangan
@timed
def levellar_jami(yozuvlar: list[LogYozuv]) -> dict[str, int]:
    return dict(Counter(y.level for y in yozuvlar))


@timed
def kunlik_jami(yozuvlar: list[LogYozuv]) -> dict[str, int]:
    return dict(Counter(y.sana for y in yozuvlar))


@timed
def filterlash(yozuvlar: list[LogYozuv], **filtrlar) -> list[LogYozuv]:
    # **kwargs bilan istalgan maydon bo'yicha filterlash
    natija = []
    for y in yozuvlar:
        ok = True
        for kalit, qiymat in filtrlar.items():
            if getattr(y, kalit, None) != qiymat:
                ok = False
                break
        if ok:
            natija.append(y)
    return natija


@timed
def top_xabarlar(yozuvlar: list[LogYozuv], n: int = 3) -> list[tuple[str, int]]:
    return Counter(y.xabar for y in yozuvlar).most_common(n)


# 5) Dashboard
print("\\n=== DASHBOARD ===")
print("Levellar:", levellar_jami(yozuvlar))
print("Kunlik:  ", kunlik_jami(yozuvlar))
print("ERROR'lar:", [asdict(y) for y in filterlash(yozuvlar, level="ERROR")])
print("Top:",      top_xabarlar(yozuvlar, n=3))

# 6) Pipeline misoli — 1 foydalanuvchining INFO eventlari
foyd_1_info = filterlash(yozuvlar, foydalanuvchi_id=1, level="INFO")
print("\\nUser 1 INFO eventlari:", len(foyd_1_info))
"""

L7_TEXT = """\
<h2>JSON va CSV — real ma'lumotlar bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    PY["Python dict/list"] -->|json.dump| F1["fayl.json"]
    F1 -->|json.load| PY2["dict/list"]
    PY -->|csv.DictWriter| F2["fayl.csv"]
    F2 -->|csv.DictReader| ROWS["list of dict"]
</pre>

<p>Real dunyo ma'lumotlari ko'pincha JSON yoki CSV ko'rinishida bo'ladi. API'lardan JSON keladi, hisobotlar va Excel'ga CSV. Bu darsda <code>json</code> va <code>csv</code> standart modullari bilan o'qiymiz va yozamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — JSON yozish va o'qish</h4>
<pre><code>import json

talabalar = [
    {"ism": "Ali",   "ball": 87, "teglar": ["python", "ai"]},
    {"ism": "Vali",  "ball": 92, "teglar": ["js"]},
    {"ism": "Gulya", "ball": 78, "teglar": ["python", "web"]},
]

# Faylga yozish
with open("talabalar.json", "w", encoding="utf-8") as f:
    json.dump(talabalar, f, ensure_ascii=False, indent=2)

# Qayta o'qish
with open("talabalar.json", encoding="utf-8") as f:
    qaytarilgan = json.load(f)

print(qaytarilgan[0]["ism"])    # Ali
print(type(qaytarilgan))         # list</code></pre>
<p>⚠️ <code>ensure_ascii=False</code> bo'lmasa, kirilcha/o'zbekcha harflar <code>\\u...</code> qilib yoziladi.</p>

<h4>BLOKA 2 — CSV DictReader / DictWriter</h4>
<pre><code>import csv

# Yozish — DictWriter dict elementlarini ustun-ustun qiladi
with open("talabalar.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ism", "ball"])
    writer.writeheader()
    for t in talabalar:
        writer.writerow({"ism": t["ism"], "ball": t["ball"]})

# O'qish — har qator dict bo'ladi
with open("talabalar.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for qator in reader:
        print(qator["ism"], "->", qator["ball"])</code></pre>
<p>⚠️ <code>newline=""</code> Windows'da bo'sh qator qo'shilmasligi uchun zarur.</p>

<h4>BLOKA 3 — String orqali (fayl ochmasdan)</h4>
<pre><code># JSON string -> Python obyekt
matn = '{"ism": "Ali", "ball": 87}'
obj = json.loads(matn)
print(obj["ism"])

# Python obyekt -> JSON string
s = json.dumps({"ism": "Ali"}, ensure_ascii=False)
print(s)         # {"ism": "Ali"}

# CSV string'larini ham parse qilish mumkin
from io import StringIO
csv_str = "ism,ball\\nAli,87\\nVali,92"
reader = csv.DictReader(StringIO(csv_str))
print(list(reader))</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>import csv

with open("test.csv", "w", encoding="utf-8") as f:    # ⚠️ newline yo'q
    writer = csv.writer(f)
    writer.writerow(["a", "b", "c"])
    writer.writerow([1, 2, 3])

# Windows'da:
# a,b,c
#                   &lt;-- ortiqcha bo'sh qator
# 1,2,3</code></pre>
<p><strong>Fix:</strong> <code>open(..., newline="")</code> — CSV moduli o'zining qator ajratuvchisini yozadi, OS'ning emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. JSON — 4 ta funksiya</h4>
<table>
<tr><th>Funksiya</th><th>Maqsadi</th></tr>
<tr><td><code>json.dump(obj, fayl)</code></td><td>Faylga yozish</td></tr>
<tr><td><code>json.load(fayl)</code></td><td>Fayldan o'qish</td></tr>
<tr><td><code>json.dumps(obj)</code></td><td>String'ga aylantirish</td></tr>
<tr><td><code>json.loads(string)</code></td><td>String'dan parse qilish</td></tr>
</table>
<p><code>s</code> harfi — string'ga / string'dan.</p>

<h4>2. JSON dump opsiyalari</h4>
<pre><code>json.dump(
    obj, f,
    ensure_ascii=False,     # Unicode harflarni o'zicha yozadi
    indent=2,               # Chiroyli formatlash (2 bo'shliq)
    sort_keys=True,         # Kalitlarni alifbo tartibida
    default=str,            # JSON tushunmaydigan turlar uchun (datetime ga str)
)</code></pre>

<h4>3. CSV — DictReader vs reader</h4>
<table>
<tr><th>Tur</th><th>Qaytaradi</th></tr>
<tr><td><code>csv.reader</code></td><td>Har qator — list of str</td></tr>
<tr><td><code>csv.writer</code></td><td><code>writerow([...])</code> qabul qiladi</td></tr>
<tr><td><code>csv.DictReader</code></td><td>Har qator — dict, birinchi qator header</td></tr>
<tr><td><code>csv.DictWriter</code></td><td><code>writerow({...})</code> qabul qiladi</td></tr>
</table>

<h4>4. Maxsus turlarni JSON ga o'tkazish</h4>
<pre><code>from dataclasses import asdict, dataclass
from datetime import datetime
import json

@dataclass
class Buyurtma:
    id: int
    sana: datetime
    summa: float

b = Buyurtma(1, datetime.now(), 1500.0)

# datetime — JSON tushunmaydi. default=str orqali stringga
s = json.dumps(asdict(b), default=str, ensure_ascii=False)
print(s)</code></pre>

<h4>5. CSV — encoding va separator nyuanslari</h4>
<ul>
<li>Excel <em>ba'zan</em> <code>;</code> ni separator deb qabul qiladi (mintaqaga qarab). Yozayotganda <code>csv.writer(f, delimiter=";")</code> berishingiz mumkin</li>
<li><code>utf-8-sig</code> encoding — Excel o'zbekcha harflarni to'g'ri ko'rsatsin</li>
<li>Qator ichida vergul bo'lsa — CSV avtomatik tirnoqlaydi (csv moduli o'zi bilan)</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>json.dump/load</code> — faylga; <code>dumps/loads</code> — stringga</li>
<li><code>ensure_ascii=False</code> — Unicode harflar uchun majburiy</li>
<li>CSV uchun <code>newline=""</code> doim ishlating</li>
<li><code>DictReader/DictWriter</code> — dict bilan ishlash uchun ideal</li>
<li>Maxsus turlar (datetime, dataclass) uchun <code>default=str</code> yoki <code>asdict()</code></li>
</ul>
"""

L7_CODE = """\
# ─── JSON va CSV bilan ishlash — to'liq sweep ────────────────────────────
import json
import csv
from io import StringIO
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path

# Test fayllarni shu skript joyiga yaratamiz
HERE = Path(__file__).parent

# 1) Dataclass + JSON
@dataclass
class Foydalanuvchi:
    id: int
    ism: str
    yosh: int
    teglar: list[str] = field(default_factory=list)

ali = Foydalanuvchi(1, "Ali", 21, ["python"])
vali = Foydalanuvchi(2, "Vali", 19, ["js", "react"])
gulya = Foydalanuvchi(3, "Gulya", 22, ["data"])

foydalanuvchilar = [ali, vali, gulya]

# Faylga JSON yozish
json_yo_l = HERE / "demo_foydalanuvchilar.json"
with open(json_yo_l, "w", encoding="utf-8") as f:
    json.dump(
        [asdict(u) for u in foydalanuvchilar],
        f, ensure_ascii=False, indent=2,
    )
print(f"JSON yozildi: {json_yo_l}")

# Qayta o'qish
with open(json_yo_l, encoding="utf-8") as f:
    qaytarilgan = json.load(f)
print(f"O'qildi: {len(qaytarilgan)} ta foydalanuvchi")
print("Birinchisi:", qaytarilgan[0])

# 2) JSON string bilan (fayl emas)
matn = '{"ism": "Doniyor", "yosh": 25}'
obj = json.loads(matn)
print(f"\\nParse: {obj['ism']} — {obj['yosh']} yoshda")

# Python -> string
s = json.dumps({"x": [1, 2, 3], "y": None}, ensure_ascii=False)
print("Dump string:", s)

# 3) Maxsus turlar — datetime
buyurtma = {
    "id": 42,
    "sana": datetime.now(),
    "summa": 12500.0,
}

# datetime ni JSON tushunmaydi — default=str bilan stringga
buy_json = json.dumps(buyurtma, default=str, ensure_ascii=False, indent=2)
print(f"\\nBuyurtma JSON:\\n{buy_json}")

# 4) CSV yozish — DictWriter
csv_yo_l = HERE / "demo_foydalanuvchilar.csv"
with open(csv_yo_l, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "ism", "yosh", "teglar"])
    writer.writeheader()
    for u in foydalanuvchilar:
        row = asdict(u)
        row["teglar"] = ";".join(row["teglar"])    # list -> string
        writer.writerow(row)
print(f"\\nCSV yozildi: {csv_yo_l}")

# 5) CSV o'qish — DictReader
print("\\nCSV dan o'qildi:")
with open(csv_yo_l, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for qator in reader:
        teglar = qator["teglar"].split(";") if qator["teglar"] else []
        print(f"  #{qator['id']:>2}  {qator['ism']:<8}  {qator['yosh']} yoshda  teglar={teglar}")

# 6) CSV string (fayl yaratmasdan)
csv_matn = (
    "mahsulot,narx,soni\\n"
    "Olma,12000,5\\n"
    "Non,4000,12\\n"
    "Sut,9000,3\\n"
)
reader = csv.DictReader(StringIO(csv_matn))
jami = sum(int(r["narx"]) * int(r["soni"]) for r in reader)
print(f"\\nJami summa: {jami:,} so'm")

# 7) Real transformatsiya — JSON dan CSV ga
data = [
    {"ism": "Ali",   "ball": 87, "teglar": ["python"]},
    {"ism": "Vali",  "ball": 92, "teglar": ["js"]},
    {"ism": "Gulya", "ball": 78, "teglar": ["python", "web"]},
]

with open(HERE / "demo_top.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["ism", "ball", "asosiy_teg"])
    w.writeheader()
    for t in sorted(data, key=lambda x: x["ball"], reverse=True):
        w.writerow({
            "ism": t["ism"],
            "ball": t["ball"],
            "asosiy_teg": t["teglar"][0] if t["teglar"] else "",
        })
print("Top CSV yozildi.")
"""

L8_TEXT = """\
<h2>HTTP so'rovlari — <code>requests</code> bilan API'lar</h2>

<pre class="mermaid">
flowchart LR
    PY["Python kodi"] -->|requests.get url| SRV["server"]
    SRV --> RESP["Response: status, headers, body"]
    RESP -->|.json| DICT["Python dict / list"]
    PY -->|requests.post url, json=| SRV
</pre>

<p>Real Python ko'pincha API'lar bilan gaplashadi: ob-havo, valyuta kurslari, tarjima, GitHub statistikasi. <code>requests</code> kutubxonasi shu vazifani 2 qatorga sig'diradi. (O'rnatish: <code>pip install requests</code>.)</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Eng oddiy GET so'rov</h4>
<pre><code>import requests

r = requests.get("https://httpbin.org/json")
print(r.status_code)         # 200
print(r.json())              # {'slideshow': {'title': '...', 'slides': [...]}}

# Yoki to'g'ridan-to'g'ri
data = requests.get("https://api.github.com/repos/python/cpython").json()
print(data["stargazers_count"])
print(data["language"])</code></pre>

<h4>BLOKA 2 — Status, headers, errors</h4>
<pre><code>r = requests.get("https://httpbin.org/status/404")
print(r.status_code)         # 404
print(r.ok)                  # False (200-299 — True)

# raise_for_status — 4xx/5xx bo'lsa exception
try:
    r = requests.get("https://httpbin.org/status/500", timeout=5)
    r.raise_for_status()
    data = r.json()
except requests.HTTPError as e:
    print(f"HTTP xato: {e}")
except requests.Timeout:
    print("Timeout")
except requests.ConnectionError:
    print("Tarmoq xatosi")</code></pre>

<h4>BLOKA 3 — POST + JSON body + headers</h4>
<pre><code>r = requests.post(
    "https://httpbin.org/post",
    json={"ism": "Ali", "yosh": 21},          # body — JSON
    headers={"Authorization": "Bearer XXX"},  # auth
    timeout=10,
)
print(r.json()["json"])      # server bizga yuborgan body ni qaytarib beradi

# Query params (URL ga ?key=value)
r = requests.get(
    "https://httpbin.org/get",
    params={"q": "python", "page": 2},
)
print(r.url)
# https://httpbin.org/get?q=python&amp;page=2</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>import requests

# ⚠️ timeout=... yo'q
r = requests.get("https://sekin-server.example.com/data")
print(r.json())</code></pre>
<p><strong>Muammo:</strong> server javob bermaydi, dastur <em>cheksiz</em> kutadi. Productionda — butun servis to'xtab qoladi. <strong>Yechim:</strong> <em>doim</em> <code>timeout=10</code> (yoki shunga o'xshash). Default — no timeout, bu xavfli.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Asosiy metodlar</h4>
<table>
<tr><th>Metod</th><th>Maqsadi</th></tr>
<tr><td><code>get(url, params=)</code></td><td>O'qish — server'dan ma'lumot olish</td></tr>
<tr><td><code>post(url, json=)</code></td><td>Yangi resurs yaratish</td></tr>
<tr><td><code>put(url, json=)</code></td><td>Mavjudini almashtirish</td></tr>
<tr><td><code>patch(url, json=)</code></td><td>Qisman yangilash</td></tr>
<tr><td><code>delete(url)</code></td><td>O'chirish</td></tr>
</table>

<h4>2. Response obyektidan nimalar oladi?</h4>
<pre><code>r = requests.get(url)
r.status_code     # 200, 404, 500 ...
r.ok              # True agar 200-299
r.text            # body — string
r.json()          # body — dict/list (agar JSON bo'lsa)
r.headers         # dict — javob headerlari
r.url             # qaytarilgan final URL
r.elapsed         # qancha vaqt ketdi
r.cookies         # cookies</code></pre>

<h4>3. Auth turlari</h4>
<pre><code># Token (Bearer)
requests.get(url, headers={"Authorization": "Bearer XXXX"})

# Basic auth (ism + parol)
requests.get(url, auth=("foydalanuvchi", "parol"))

# API key (query param yoki header — API'ga qarab)
requests.get(url, params={"api_key": "XXXX"})
requests.get(url, headers={"X-Api-Key": "XXXX"})</code></pre>

<h4>4. Session — bir nechta so'rov uchun konfiguratsiyani saqlash</h4>
<pre><code>s = requests.Session()
s.headers.update({"Authorization": "Bearer XXX"})
s.timeout = 10

# Endi har bir s.get/s.post da auth va timeout bor
r1 = s.get("https://api.example.com/users")
r2 = s.get("https://api.example.com/posts")</code></pre>

<h4>5. Status kodlar va ma'nosi</h4>
<table>
<tr><th>Kod</th><th>Ma'nosi</th></tr>
<tr><td>200</td><td>OK</td></tr>
<tr><td>201</td><td>Created (POST muvaffaqiyatli)</td></tr>
<tr><td>204</td><td>No Content (DELETE muvaffaqiyatli)</td></tr>
<tr><td>400</td><td>Bad Request — siz noto'g'ri jo'natdingiz</td></tr>
<tr><td>401</td><td>Unauthorized — auth yo'q yoki noto'g'ri</td></tr>
<tr><td>403</td><td>Forbidden — auth bor, lekin ruxsat yo'q</td></tr>
<tr><td>404</td><td>Not Found</td></tr>
<tr><td>429</td><td>Rate limit — ko'p so'rov</td></tr>
<tr><td>5xx</td><td>Server tomonidagi xato</td></tr>
</table>

<h4>6. Xato boshqarish patterni</h4>
<pre><code>def xavfsiz_olish(url, **kwargs):
    try:
        r = requests.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.Timeout:
        print(f"⏱  Timeout: {url}")
    except requests.HTTPError as e:
        print(f"❌ HTTP {r.status_code}: {url}")
    except requests.RequestException as e:
        print(f"⚠️  Xato: {e}")
    return None</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>requests.get(url).json()</code> — JSON API'ni 1 qatorda o'qiysiz</li>
<li><code>timeout=</code> ⚠️ <strong>HAR DOIM</strong> bering</li>
<li><code>raise_for_status()</code> — 4xx/5xx ni exception qiladi</li>
<li><code>params=</code> — URL ga query string, <code>json=</code> — body</li>
<li>Authorization — header, auth tuple yoki API key</li>
</ul>
"""

L8_CODE = """\
# ─── HTTP so'rovlari — requests bilan ────────────────────────────────────
# Eslatma: skript ishlatishdan oldin `pip install requests`
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError as ReqConnErr

# 1) Eng oddiy GET — httpbin.org bilan ishlash (test API)
r = requests.get("https://httpbin.org/json", timeout=10)
print(f"Status: {r.status_code}  OK: {r.ok}")
print("JSON kalitlari:", list(r.json().keys()))

# 2) Query params
r = requests.get(
    "https://httpbin.org/get",
    params={"qidiruv": "python", "sahifa": 2, "lang": "uz"},
    timeout=10,
)
print(f"\\nGenerator URL: {r.url}")
print("Args:", r.json()["args"])

# 3) POST + JSON body
r = requests.post(
    "https://httpbin.org/post",
    json={"ism": "Ali", "yosh": 21, "teglar": ["python", "ai"]},
    headers={"User-Agent": "Python-NextLevel/1.0"},
    timeout=10,
)
echo = r.json()
print(f"\\nServer bizdan oldi: {echo['json']}")
print(f"Bizning User-Agent: {echo['headers']['User-Agent']}")

# 4) Status kod va xato
r = requests.get("https://httpbin.org/status/404", timeout=10)
print(f"\\n404 javob: status={r.status_code}  ok={r.ok}")

# raise_for_status — 4xx/5xx -> exception
try:
    r = requests.get("https://httpbin.org/status/500", timeout=10)
    r.raise_for_status()
except HTTPError as e:
    print(f"❌ Tutib oldim: {e}")

# 5) Xavfsiz wrapper — har holatni boshqaradi
def xavfsiz_olish(url, **kwargs):
    try:
        r = requests.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except Timeout:
        print(f"⏱  Timeout: {url}")
    except HTTPError:
        print(f"❌ HTTP {r.status_code}: {url}")
    except ReqConnErr:
        print(f"🌐 Tarmoq xatosi: {url}")
    except Exception as e:
        print(f"⚠️  Boshqa xato: {e}")
    return None

# 6) Real foydalanish — GitHub API
data = xavfsiz_olish("https://api.github.com/repos/python/cpython")
if data:
    print(f"\\n📦 {data['full_name']}")
    print(f"   ⭐ stars: {data['stargazers_count']:,}")
    print(f"   🍴 forks: {data['forks_count']:,}")
    print(f"   📝 til:   {data['language']}")
    print(f"   📅 yaratilgan: {data['created_at']}")

# 7) Session — ko'p so'rov uchun auth saqlash
s = requests.Session()
s.headers.update({
    "User-Agent": "Python-NextLevel/1.0",
    "Accept":     "application/json",
})

for repo in ("python/cpython", "django/django"):
    r = s.get(f"https://api.github.com/repos/{repo}", timeout=10)
    if r.ok:
        d = r.json()
        print(f"  {d['full_name']:<25} ⭐ {d['stargazers_count']:>7,}")

# 8) Headers ko'rish
r = requests.get("https://httpbin.org/get", timeout=10)
print(f"\\nServer headerlari (birinchi 3):")
for k in list(r.headers)[:3]:
    print(f"  {k}: {r.headers[k]}")
"""

L9_TEXT = """\
<h2>Regex — <code>re</code> moduli bilan matn ichidan namuna topish</h2>

<pre class="mermaid">
flowchart LR
    TEXT["matn"] -->|re.search| FIRST["birinchi mos kelish"]
    TEXT -->|re.findall| ALL["barcha mos kelishlar"]
    TEXT -->|re.sub| REPL["almashtirilgan matn"]
    PATTERN["pattern: \\d{4}"] --> FIRST
</pre>

<p><strong>Regex</strong> (regular expression) — matnda qoidaga muvofiq qism qidirish va almashtirish tili. Email topish, telefon raqami ajratish, log'dan ID chiqarish, sana parse qilish — bularning hammasi 1-2 qatorda. Boshida g'alati ko'rinadi, lekin 10 ta asosiy belgini o'rgansangiz — kuchli quroldir.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Findall: barcha namunalarni topish</h4>
<pre><code>import re

matn = \"\"\"\\
Ali: 998 90 123 45 67
Vali: 998-90-555-66-77
Gulya: +998901112233
\"\"\"

# 9 ta raqamli ketma-ketliklar — har qanday formatda
raqamlar = re.findall(r"\\+?998[\\s-]?\\d{2}[\\s-]?\\d{3}[\\s-]?\\d{2}[\\s-]?\\d{2}", matn)
print(raqamlar)
# ['998 90 123 45 67', '998-90-555-66-77', '+998901112233']</code></pre>

<h4>BLOKA 2 — Search + groups: bo'laklarga ajratish</h4>
<pre><code>matn = "Bugun 2026-03-15 da yig'ilish bor."

m = re.search(r"(\\d{4})-(\\d{2})-(\\d{2})", matn)
if m:
    yil, oy, kun = m.groups()
    print(f"Yil: {yil}, Oy: {oy}, Kun: {kun}")
    # Yil: 2026, Oy: 03, Kun: 15
    print(m.group(0))    # to'liq mos kelish: "2026-03-15"
    print(m.group(1))    # birinchi guruh: "2026"</code></pre>

<h4>BLOKA 3 — Sub: topish va almashtirish</h4>
<pre><code># Telefon raqamlarni yashirish (asterisk bilan)
matn = "Mening raqamim: 998 90 123 45 67. Akamniki: 998-91-222-33-44."

yashirilgan = re.sub(r"\\d{2,3}[\\s-]?\\d{2,3}[\\s-]?\\d{2,3}[\\s-]?\\d{2}", "***", matn)
print(yashirilgan)
# Mening raqamim: ***. Akamniki: ***.

# Group bilan almashtirish — sanani format o'zgartirish
matn = "Sana: 2026-03-15"
yangi = re.sub(r"(\\d{4})-(\\d{2})-(\\d{2})", r"\\3.\\2.\\1", matn)
print(yangi)        # Sana: 15.03.2026</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>import re

matn = "&lt;b&gt;qalin&lt;/b&gt; va &lt;i&gt;qiyshiq&lt;/i&gt; matn"

# Greedy — eng katta mos kelishni oladi
print(re.findall(r"&lt;.*&gt;", matn))
# ['&lt;b&gt;qalin&lt;/b&gt; va &lt;i&gt;qiyshiq&lt;/i&gt;']  — butun bo'lakni qamragan!

# Non-greedy — eng kichik mos kelishni oladi
print(re.findall(r"&lt;.*?&gt;", matn))
# ['&lt;b&gt;', '&lt;/b&gt;', '&lt;i&gt;', '&lt;/i&gt;']</code></pre>
<p><strong>Sabab:</strong> <code>.*</code> "imkon qadar ko'p" oladi. <code>.*?</code> "imkon qadar kam" oladi. HTML/XML uchun deyarli har doim <code>?</code> qo'shing.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Asosiy belgilar (yodlash kerakli)</h4>
<table>
<tr><th>Belgi</th><th>Ma'nosi</th></tr>
<tr><td><code>.</code></td><td>Istalgan bir belgi (yangi qator bundan istisno)</td></tr>
<tr><td><code>\\d</code></td><td>Raqam (0-9)</td></tr>
<tr><td><code>\\D</code></td><td>Raqam emas</td></tr>
<tr><td><code>\\w</code></td><td>Harf, raqam, _</td></tr>
<tr><td><code>\\W</code></td><td>So'z belgisi emas</td></tr>
<tr><td><code>\\s</code></td><td>Bo'sh joy (space, tab, newline)</td></tr>
<tr><td><code>\\S</code></td><td>Bo'sh joy emas</td></tr>
<tr><td><code>[abc]</code></td><td>a, b, yoki c</td></tr>
<tr><td><code>[a-z]</code></td><td>Diapazon — a dan z gacha</td></tr>
<tr><td><code>[^abc]</code></td><td>a, b, c dan tashqari</td></tr>
</table>

<h4>2. Miqdorlar</h4>
<table>
<tr><th>Belgi</th><th>Ma'nosi</th></tr>
<tr><td><code>*</code></td><td>0 yoki ko'p</td></tr>
<tr><td><code>+</code></td><td>1 yoki ko'p</td></tr>
<tr><td><code>?</code></td><td>0 yoki 1</td></tr>
<tr><td><code>{3}</code></td><td>aniq 3 marta</td></tr>
<tr><td><code>{2,5}</code></td><td>2 dan 5 gacha</td></tr>
<tr><td><code>{3,}</code></td><td>3 yoki ko'proq</td></tr>
<tr><td><code>*?</code> / <code>+?</code></td><td>Non-greedy (eng kam)</td></tr>
</table>

<h4>3. Lyumolar / chegaralar</h4>
<table>
<tr><th>Belgi</th><th>Ma'nosi</th></tr>
<tr><td><code>^</code></td><td>Boshi (yoki har satr boshi MULTILINE bilan)</td></tr>
<tr><td><code>$</code></td><td>Oxiri</td></tr>
<tr><td><code>\\b</code></td><td>So'z chegarasi</td></tr>
<tr><td><code>(...)</code></td><td>Guruh (saqlanadi)</td></tr>
<tr><td><code>(?:...)</code></td><td>Guruh (saqlanmaydi — tezroq)</td></tr>
<tr><td><code>|</code></td><td>Yoki</td></tr>
</table>

<h4>4. Asosiy funksiyalar</h4>
<pre><code>re.search(pat, text)   # birinchi mos kelishni qaytaradi (Match yoki None)
re.match(pat, text)    # FAQAT matn BOSHIDAN — odatda search yaxshiroq
re.findall(pat, text)  # barcha mos kelishlar (list)
re.finditer(pat, text) # generator — har bir Match
re.sub(pat, new, text) # almashtirish
re.split(pat, text)    # regex bo'yicha split

# Compile — bir necha bor ishlatiladigan pattern uchun (tezroq)
pat = re.compile(r"\\d+")
pat.findall("12 va 34 va 56")    # ['12', '34', '56']</code></pre>

<h4>5. Flagslar</h4>
<table>
<tr><th>Flag</th><th>Maqsadi</th></tr>
<tr><td><code>re.IGNORECASE</code></td><td>Bosh/kichik harf farqlamaslik</td></tr>
<tr><td><code>re.MULTILINE</code></td><td>^ va $ har satr uchun</td></tr>
<tr><td><code>re.DOTALL</code></td><td>. ham newline ni qamraydi</td></tr>
<tr><td><code>re.VERBOSE</code></td><td>Bo'sh joy va izohlarga ruxsat (uzun patternlar uchun)</td></tr>
</table>

<h4>6. Raw string — <code>r"..."</code></h4>
<p>Pattern'ni doim <code>r"..."</code> bilan yozing. Aks holda Python <code>"\\n"</code> ni newline'ga aylantiradi, regex tushunmaydi:</p>
<pre><code>r"\\d+"     # to'g'ri — regex \\d+ ni ko'radi
"\\d+"      # noto'g'ri — Python "\\d" ni \\d ga aylantiradi (bu yerda omadli) lekin "\\n" — newline</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>Doim <code>r"..."</code> bilan pattern yozing</li>
<li><code>\\d \\w \\s</code> — eng tez-tez kerak bo'ladigan klasslar</li>
<li><code>*</code> greedy, <code>*?</code> non-greedy — HTML uchun <code>?</code> qo'shing</li>
<li><code>(...)</code> — bo'lakka ajratish (groups)</li>
<li>Ko'p marta ishlatiladigan pattern uchun <code>re.compile</code></li>
</ul>
"""

L9_CODE = """\
# ─── Regex praktikum — re moduli ─────────────────────────────────────────
import re

# 1) Email topish
matn = "Aloqa: ali@gmail.com yoki ofis@company.uz. Reklama: spam@spam.com"
emails = re.findall(r"[\\w.+-]+@[\\w-]+\\.[\\w.-]+", matn)
print("Emails:", emails)

# 2) O'zbek telefon raqamlari — har xil formatda
matn = (
    "Ali:    +998 90 123 45 67\\n"
    "Vali:   998-91-555-66-77\\n"
    "Gulya:  998901112233\\n"
    "Doniyor: 990 555 12 34\\n"
)
pat = re.compile(r"\\+?998[\\s-]?\\d{2}[\\s-]?\\d{3}[\\s-]?\\d{2}[\\s-]?\\d{2}")
print("\\nTelefonlar:", pat.findall(matn))

# 3) Sanani parse qilish — groups bilan
matn = "Loyiha 2026-03-15 dan 2026-09-30 gacha"
for m in re.finditer(r"(\\d{4})-(\\d{2})-(\\d{2})", matn):
    y, o, k = m.groups()
    print(f"  Sana: {k}.{o}.{y}")

# 4) Almashtirish — format o'zgartirish
matn = "Tug'ilgan kun: 1995-08-22"
yangi = re.sub(r"(\\d{4})-(\\d{2})-(\\d{2})", r"\\3.\\2.\\1", matn)
print("\\nYangi format:", yangi)

# 5) Log faylni parsing — IP va status code
log = (
    '192.168.1.10 - - "GET /index.html" 200 1024\\n'
    '10.0.0.5    - - "POST /api/login" 401 256\\n'
    '192.168.1.10 - - "GET /admin" 403 128\\n'
    '172.16.0.1  - - "GET /api/data" 500 512\\n'
)
pat = re.compile(r'(\\d+\\.\\d+\\.\\d+\\.\\d+)\\s+-\\s+-\\s+"(\\w+)\\s+(\\S+)"\\s+(\\d+)\\s+(\\d+)')
for m in pat.finditer(log):
    ip, metod, yo_l, status, bayt = m.groups()
    flag = "❌" if int(status) >= 400 else "✅"
    print(f"  {flag} {ip:<14} {metod:<5} {yo_l:<15} -> {status}  ({bayt} bayt)")

# 6) Greedy vs non-greedy — HTML
html = "<b>qalin</b> va <i>qiyshiq</i> matn"
print("\\nGreedy:    ", re.findall(r"<.*>", html))
print("Non-greedy:", re.findall(r"<.*?>", html))

# 7) Verbose mode — uzun pattern uchun
email_pat = re.compile(
    r"[\\w.+-]+@[\\w-]+\\.[\\w.-]+",   # foydalanuvchi @ domen . TLD
)
print("\\nVerbose patterndan:", email_pat.findall("foo@bar.com baz@qux.uz"))

# 8) Split — regex bo'yicha
matn = "olma, banan;uzum  shaftoli"
qismlar = re.split(r"[,;\\s]+", matn)
print("\\nQismlar:", qismlar)

# 9) IGNORECASE flag
matn = "Python PYTHON pyThOn jAvA"
print("\\nPython lar:", re.findall(r"python", matn, flags=re.IGNORECASE))

# 10) Real foydalanish — markdown linkdan URL ni ajratish
md = "Hujjat bu yerda [Python docs](https://docs.python.org) va [PEP 8](https://peps.python.org/pep-0008/)"
linklar = re.findall(r"\\[([^\\]]+)\\]\\((https?://[^\\)]+)\\)", md)
print("\\nLinks:")
for nom, url in linklar:
    print(f"  {nom:<15} -> {url}")
"""

R3_TEXT = """\
<h2>🔁 R3 — Yangiliklar yig'uvchi (Modul 3 takrori)</h2>

<pre class="mermaid">
flowchart LR
    API["JSON API"] -->|requests.get| RESP["Response"]
    RESP -->|.json| DATA["yangiliklar list"]
    DATA -->|regex bilan tagsni tozalash| CLEAN["tozalangan matn"]
    CLEAN -->|csv.DictWriter| FILE["news.csv"]
</pre>

<p>Modul 3 ning 3 ta texnikasini birlashtiramiz: <strong>HTTP</strong>, <strong>regex</strong>, <strong>JSON/CSV</strong>. Vazifa: API'dan yangiliklarni olib, sarlavhalardan HTML teglarni va keraksiz bo'shliqlarni tozalab, faqat keraklilarini CSV ga yozish.</p>

<h3>🏆 5 daqiqada g'alaba — pipeline</h3>

<pre><code>import requests
import re
import csv
import json
from pathlib import Path

URL = "https://jsonplaceholder.typicode.com/posts"   # test API

def yangiliklar_olish(url):
    # 1) HTTP — JSON olamiz
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def matnni_tozalash(matn):
    # 2) Regex — HTML teglarni va ko'p bo'shliqlarni olib tashlaymiz
    matn = re.sub(r"&lt;[^&gt;]+&gt;", "", matn)          # &lt;p&gt; va &lt;a&gt; teglarni o'chirish
    matn = re.sub(r"\\s+", " ", matn)            # bir nechta bo'sh joyni bittaga
    return matn.strip()

def csv_ga_yozish(yangiliklar, yo_l):
    # 3) CSV — DictWriter bilan
    with open(yo_l, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "sarlavha", "matn_qisqacha"])
        w.writeheader()
        for n in yangiliklar:
            w.writerow({
                "id": n["id"],
                "sarlavha": matnni_tozalash(n["title"]),
                "matn_qisqacha": matnni_tozalash(n["body"])[:100],
            })

# Asosiy oqim
raw = yangiliklar_olish(URL)
csv_ga_yozish(raw[:10], "yangiliklar.csv")
print(f"✅ {len(raw[:10])} ta yangilik yozildi")
</code></pre>

<h3>3 ta texnika birga ishlaganda</h3>

<h4>HTTP — kirish (input)</h4>
<ul>
<li><code>timeout=</code> doim qo'shiladi</li>
<li><code>raise_for_status()</code> — xatolar uchun</li>
<li><code>r.json()</code> — JSON parse</li>
</ul>

<h4>Regex — tozalash (transform)</h4>
<ul>
<li>HTML teg: <code>r"&lt;[^&gt;]+&gt;"</code></li>
<li>Ko'p bo'sh joy: <code>r"\\s+"</code></li>
<li>Maxsus belgilarni olish: <code>r"&amp;[a-z]+;"</code></li>
</ul>

<h4>CSV — chiqish (output)</h4>
<ul>
<li><code>DictWriter</code> + <code>fieldnames</code></li>
<li><code>newline=""</code></li>
<li><code>encoding="utf-8-sig"</code> — Excel uchun</li>
</ul>

<h3>📌 Module 3 ni siz endi bilasiz</h3>
<ul>
<li>Real API'dan ma'lumot olishni 5 qatorda yozasiz</li>
<li>Matnni regex bilan tozalashni bilasiz</li>
<li>Natijani JSON yoki CSV ga saqlaysiz</li>
<li>Endi sizda "data pipeline" tushunchasi bor</li>
</ul>
"""

R3_CODE = """\
# ─── R3: Yangiliklar yig'uvchi — to'liq pipeline ──────────────────────────
# Bu skript jsonplaceholder.typicode.com test API'sidan post'larni oladi,
# matnlarni regex bilan tozalaydi va CSV/JSON ga saqlaydi.
import requests
import re
import csv
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from requests.exceptions import RequestException

HERE = Path(__file__).parent
API_URL = "https://jsonplaceholder.typicode.com/posts"


@dataclass
class Yangilik:
    id: int
    user_id: int
    sarlavha: str
    matn: str
    so_zlar_soni: int = 0
    olindi_vaqti: str = field(default_factory=lambda: "2026-06-06T00:00:00")


# 1) HTTP qatlami
def yangiliklar_olish(url: str, limit: int = 10) -> list[dict]:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()[:limit]
    except RequestException as e:
        print(f"❌ Tarmoq xatosi: {e}")
        return []


# 2) Regex qatlami — matn tozalash
HTML_TEG = re.compile(r"<[^>]+>")
KOP_BOSHLIQ = re.compile(r"\\s+")
URL_PAT = re.compile(r"https?://\\S+")

def matnni_tozalash(matn: str) -> str:
    matn = HTML_TEG.sub("", matn)
    matn = URL_PAT.sub("[URL]", matn)
    matn = KOP_BOSHLIQ.sub(" ", matn)
    return matn.strip()


def so_zlarni_sanash(matn: str) -> int:
    return len(re.findall(r"\\b\\w+\\b", matn))


# 3) Transformatsiya — raw dict -> Yangilik
def yarat(raw: dict) -> Yangilik:
    sarlavha = matnni_tozalash(raw["title"])
    matn = matnni_tozalash(raw["body"])
    return Yangilik(
        id=raw["id"],
        user_id=raw["userId"],
        sarlavha=sarlavha,
        matn=matn,
        so_zlar_soni=so_zlarni_sanash(matn),
    )


# 4) Output qatlami — JSON va CSV
def json_ga_yozish(yangiliklar: list[Yangilik], yo_l: Path) -> None:
    with open(yo_l, "w", encoding="utf-8") as f:
        json.dump(
            [asdict(n) for n in yangiliklar],
            f, ensure_ascii=False, indent=2,
        )

def csv_ga_yozish(yangiliklar: list[Yangilik], yo_l: Path) -> None:
    with open(yo_l, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["id", "user_id", "sarlavha", "so_zlar_soni", "matn"],
        )
        w.writeheader()
        for n in yangiliklar:
            w.writerow({
                "id": n.id,
                "user_id": n.user_id,
                "sarlavha": n.sarlavha,
                "so_zlar_soni": n.so_zlar_soni,
                "matn": n.matn[:200],
            })


# ── Pipeline ──────────────────────────────────────────────────────────────
print("📡 Yangiliklar API dan olinmoqda...")
raw = yangiliklar_olish(API_URL, limit=10)
print(f"✅ {len(raw)} ta yangilik olindi")

yangiliklar = [yarat(r) for r in raw]

# Statistika
jami_so_zlar = sum(n.so_zlar_soni for n in yangiliklar)
o_rta_so_zlar = jami_so_zlar / len(yangiliklar) if yangiliklar else 0
eng_uzun = max(yangiliklar, key=lambda n: n.so_zlar_soni, default=None)

print(f"\\nJami so'zlar: {jami_so_zlar}")
print(f"O'rtacha:     {o_rta_so_zlar:.1f} so'z")
if eng_uzun:
    print(f"Eng uzun:     #{eng_uzun.id} ({eng_uzun.so_zlar_soni} so'z)")

# Yozish
json_ga_yozish(yangiliklar, HERE / "demo_news.json")
csv_ga_yozish(yangiliklar, HERE / "demo_news.csv")
print(f"\\n💾 Yozildi: demo_news.json, demo_news.csv")
"""

L10_TEXT = """\
<h2>Chuqur OOP — meros, <code>super</code>, <code>@property</code> va dunder metodlar</h2>

<pre class="mermaid">
flowchart TB
    BASE["Hayvon (asos klass)"] -->|meros| DOG["It"]
    BASE -->|meros| CAT["Mushuk"]
    DOG -->|super init| BASE
    PROP["@property"] --> HISOB["computed atribut"]
    DUNDER["__add__, __str__, __eq__"] --> NATIVE["class native his qiladi"]
</pre>

<p>Python Asoslari kursida class va __init__ bilan tanishdik. Endi <strong>klass'lar bir-biriga aloqadosh bo'lganda</strong> kuchli idiomalarni o'rganamiz: meros, <code>super()</code>, <code>@property</code>, dunder metodlar. Bularsiz sizning klasslaringiz "anketa" bo'lib qoladi — bu darsdan keyin ular <strong>tirik obyektlar</strong> bo'ladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Meros + super()</h4>
<pre><code>class Hayvon:
    def __init__(self, nom, ovqat):
        self.nom = nom
        self.ovqat = ovqat

    def gapir(self):
        return f"{self.nom}: ..."

class It(Hayvon):
    def __init__(self, nom, zot):
        super().__init__(nom, ovqat="suyak")    # &lt;-- ota __init__
        self.zot = zot

    def gapir(self):
        return f"{self.nom} (it): vov-vov!"

it = It("Rex", "labrador")
print(it.nom, it.ovqat, it.zot)    # Rex suyak labrador
print(it.gapir())                  # Rex (it): vov-vov!</code></pre>

<h4>BLOKA 2 — @property — atribut sifatida ko'ringan metod</h4>
<pre><code>class Talaba:
    def __init__(self, ism, ballar):
        self.ism = ism
        self.ballar = ballar

    @property
    def o_rta_ball(self):
        if not self.ballar:
            return 0
        return sum(self.ballar) / len(self.ballar)

    @property
    def darajasi(self):
        ob = self.o_rta_ball
        if ob &gt;= 90: return "A'lo"
        if ob &gt;= 70: return "Yaxshi"
        return "Qoniqarsiz"

t = Talaba("Ali", [85, 92, 78, 88])
print(t.o_rta_ball)        # 85.75    — qavslarsiz!
print(t.darajasi)          # Yaxshi
# t.o_rta_ball = 100        # AttributeError — geter only</code></pre>

<h4>BLOKA 3 — Dunder metodlar — class'ni native qiladi</h4>
<pre><code>class Pul:
    def __init__(self, summa, valyuta="UZS"):
        self.summa = summa
        self.valyuta = valyuta

    def __str__(self):
        return f"{self.summa:,} {self.valyuta}"

    def __repr__(self):
        return f"Pul({self.summa!r}, {self.valyuta!r})"

    def __add__(self, other):
        if self.valyuta != other.valyuta:
            raise ValueError("Valyutalar mos kelmaydi")
        return Pul(self.summa + other.summa, self.valyuta)

    def __eq__(self, other):
        return self.summa == other.summa and self.valyuta == other.valyuta

a = Pul(100_000)
b = Pul(250_000)
c = a + b                       # __add__ bilan
print(c)                        # 350,000 UZS    — __str__ bilan
print(a == Pul(100_000))        # True           — __eq__ bilan</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>class Mashina:
    def __init__(self, marka):
        self.marka = marka

class Elektromobil(Mashina):
    def __init__(self, marka, batareya):
        # super().__init__(marka)    &lt;-- UNUTILDI
        self.batareya = batareya

e = Elektromobil("Tesla", 100)
print(e.batareya)        # 100
print(e.marka)           # AttributeError!</code></pre>
<p><strong>Sabab:</strong> <code>super().__init__()</code> chaqirilmadi — ota klass o'z maydonlarini sozlamadi. Default qoidasi: <strong>sub-class __init__ doim super().__init__() chaqiradi</strong> (agar ota faqat default qiymatlar ishlatmasa).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Meros — qachon?</h4>
<ul>
<li><strong>"is-a"</strong> munosabati: <em>It IS-A Hayvon</em>, <em>Quadrant IS-A Shakl</em></li>
<li>Sub-class ota'ning behavior'ini <strong>kengaytiradi yoki o'zgartiradi</strong></li>
<li><strong>Yomon misol</strong>: <em>Mashina IS-A Yo'l</em> — yo'q, mashina yo'lda <em>yuradi</em> (kompozitsiya kerak, meros emas)</li>
</ul>

<h4>2. super() — ota klassga murojaat</h4>
<pre><code>class B(A):
    def __init__(self, x, y):
        super().__init__(x)     # A.__init__(x) ga ekvivalent
        self.y = y

    def method(self):
        natija = super().method()    # ota metodini chaqiradi
        return natija + " (kengaytirilgan)"</code></pre>
<p>super() — bir klass yoki ko'p meros (MRO) muhitida ham to'g'ri ishlaydi. <code>A.__init__(self, x)</code> ham ishlaydi, lekin super yaxshiroq.</p>

<h4>3. @property — geter; @maydon.setter — seter</h4>
<pre><code>class Doira:
    def __init__(self, radius):
        self._radius = radius   # _radius — "ichki", tashqaridan o'zgartirmang

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        if val &lt; 0:
            raise ValueError("Radius manfiy bo'la olmaydi")
        self._radius = val

    @property
    def maydon(self):
        import math
        return math.pi * self._radius ** 2

d = Doira(5)
print(d.radius)     # 5     — geter
d.radius = 10       # seter — validatsiya bilan
# d.radius = -1     # ValueError
print(d.maydon)     # 314.15...    — computed atribut</code></pre>

<h4>4. Dunder metodlar — eng ko'p ishlatiladiganlar</h4>
<table>
<tr><th>Metod</th><th>Maqsadi</th><th>Chaqiruv</th></tr>
<tr><td><code>__init__</code></td><td>Konstruktor</td><td><code>Cls(...)</code></td></tr>
<tr><td><code>__str__</code></td><td>Foydalanuvchiga ko'rsatish</td><td><code>str(obj)</code>, <code>print(obj)</code></td></tr>
<tr><td><code>__repr__</code></td><td>Debug uchun ko'rsatish</td><td><code>repr(obj)</code>, REPL</td></tr>
<tr><td><code>__eq__</code></td><td>Tenglik</td><td><code>a == b</code></td></tr>
<tr><td><code>__lt__</code></td><td>Kichik</td><td><code>a &lt; b</code> — sortable qiladi</td></tr>
<tr><td><code>__hash__</code></td><td>Hash qiymati</td><td><code>set</code>, <code>dict</code> kalit</td></tr>
<tr><td><code>__len__</code></td><td>Uzunlik</td><td><code>len(obj)</code></td></tr>
<tr><td><code>__contains__</code></td><td>Ichida bormi</td><td><code>x in obj</code></td></tr>
<tr><td><code>__iter__</code></td><td>Iteratsiya</td><td><code>for x in obj</code></td></tr>
<tr><td><code>__add__</code></td><td>Qo'shish</td><td><code>a + b</code></td></tr>
<tr><td><code>__getitem__</code></td><td>Indeks bilan</td><td><code>obj[i]</code></td></tr>
</table>

<h4>5. __str__ va __repr__ farqi</h4>
<ul>
<li><code>__str__</code> — <strong>foydalanuvchiga</strong> ("100,000 UZS")</li>
<li><code>__repr__</code> — <strong>dasturchiga</strong>, debug uchun ("Pul(100000, 'UZS')")</li>
<li>Qoida: <code>repr(obj)</code> dan <code>eval()</code> bilan obyektni qayta yaratish mumkin bo'lsa, eng yaxshi</li>
<li>Faqat <code>__repr__</code> qo'ysangiz, <code>__str__</code> ham shu — ikkalasini ham tavsiya</li>
</ul>

<h4>6. Composition vs Inheritance</h4>
<pre><code># Meros — IS-A
class It(Hayvon):
    ...

# Kompozitsiya — HAS-A (afzalroq, ko'p hollarda)
class Mashina:
    def __init__(self):
        self.dvigatel = Dvigatel()        # mashina dvigatelga EGA
        self.g_ildirak = [G_ildirak() for _ in range(4)]</code></pre>
<p><strong>Qoida:</strong> kompozitsiyani afzal ko'ring. Meros — faqat haqiqiy IS-A munosabati bo'lganda.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li><code>super().__init__()</code> — sub-class ichida birinchi qator bo'lsin</li>
<li><code>@property</code> — atribut sifatida ko'rinadigan getter</li>
<li><code>__str__</code>/<code>__repr__</code>/<code>__eq__</code>/<code>__add__</code> — sizning class'ingiz native his qildiradi</li>
<li>Meros yoki kompozitsiya? IS-A bo'lsa meros, HAS-A bo'lsa kompozitsiya</li>
<li>Dataclass ham bularning hammasini avtomatik qiladi — lekin asoslarini bilish kerak</li>
</ul>
"""

L10_CODE = """\
# ─── Chuqur OOP — meros, super, properties, dunder metodlar ──────────────
from dataclasses import dataclass
from functools import total_ordering
import math


# 1) Asosiy klass va meros
class Hayvon:
    def __init__(self, nom: str, yoshi: int):
        self.nom = nom
        self.yoshi = yoshi

    def gapir(self) -> str:
        return f"{self.nom}: ..."

    def __repr__(self):
        return f"{type(self).__name__}({self.nom!r}, {self.yoshi})"


class It(Hayvon):
    def __init__(self, nom: str, yoshi: int, zot: str):
        super().__init__(nom, yoshi)
        self.zot = zot

    def gapir(self) -> str:
        return f"{self.nom} ({self.zot}): vov-vov!"


class Mushuk(Hayvon):
    def gapir(self) -> str:
        return f"{self.nom}: myau!"


it = It("Rex", 3, "labrador")
mushuk = Mushuk("Mursik", 5)

for h in (it, mushuk):
    print(h.gapir())          # polimorfizm
    print(repr(h))


# 2) @property + setter + computed
class Doira:
    def __init__(self, radius: float):
        self.radius = radius   # setter chaqiriladi

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, val: float):
        if val < 0:
            raise ValueError("Radius manfiy bo'la olmaydi")
        self._radius = val

    @property
    def maydon(self) -> float:
        return math.pi * self._radius ** 2

    @property
    def aylana(self) -> float:
        return 2 * math.pi * self._radius


d = Doira(5)
print(f"\\nDoira: radius={d.radius}  maydon={d.maydon:.2f}  aylana={d.aylana:.2f}")
d.radius = 10
print(f"Yangi: maydon={d.maydon:.2f}")
try:
    d.radius = -1
except ValueError as e:
    print(f"Tutib oldim: {e}")


# 3) Dunder metodlar — Pul class native ish his qiladi
@total_ordering
class Pul:
    def __init__(self, summa: float, valyuta: str = "UZS"):
        self.summa = summa
        self.valyuta = valyuta

    def __str__(self):
        return f"{self.summa:,.2f} {self.valyuta}"

    def __repr__(self):
        return f"Pul({self.summa!r}, {self.valyuta!r})"

    def _tekshir(self, other):
        if not isinstance(other, Pul):
            return NotImplemented
        if self.valyuta != other.valyuta:
            raise ValueError(f"Valyuta nosozligi: {self.valyuta} vs {other.valyuta}")
        return True

    def __add__(self, other):
        ok = self._tekshir(other)
        if ok is NotImplemented:
            return NotImplemented
        return Pul(self.summa + other.summa, self.valyuta)

    def __sub__(self, other):
        ok = self._tekshir(other)
        if ok is NotImplemented:
            return NotImplemented
        return Pul(self.summa - other.summa, self.valyuta)

    def __mul__(self, k: float):
        return Pul(self.summa * k, self.valyuta)

    def __eq__(self, other):
        if not isinstance(other, Pul):
            return NotImplemented
        return self.summa == other.summa and self.valyuta == other.valyuta

    def __lt__(self, other):
        self._tekshir(other)
        return self.summa < other.summa

    def __hash__(self):
        return hash((self.summa, self.valyuta))


print()
a = Pul(100_000)
b = Pul(250_000)
print(f"a + b = {a + b}")
print(f"b - a = {b - a}")
print(f"a * 1.5 = {a * 1.5}")
print(f"a < b: {a < b}")
print(f"sorted: {sorted([b, a, Pul(50_000)])}")
print(f"set bilan unique: {set([a, Pul(100_000), b])}")


# 4) Iterable / container class
class Sinf:
    def __init__(self, nom: str):
        self.nom = nom
        self._talabalar: list[str] = []

    def qosh(self, talaba: str):
        self._talabalar.append(talaba)

    def __len__(self):
        return len(self._talabalar)

    def __contains__(self, talaba: str) -> bool:
        return talaba in self._talabalar

    def __iter__(self):
        return iter(self._talabalar)

    def __getitem__(self, i: int) -> str:
        return self._talabalar[i]

    def __repr__(self):
        return f"Sinf({self.nom!r}, talabalar={len(self)})"


s = Sinf("10-A")
for ism in ["Ali", "Vali", "Gulya", "Doniyor"]:
    s.qosh(ism)

print(f"\\n{s}")
print(f"len: {len(s)}")
print(f"'Ali' in s: {'Ali' in s}")
print(f"s[0]: {s[0]}")
print("Ro'yxat:")
for t in s:
    print(f"  - {t}")
"""

L11_TEXT = """\
<h2>🚀 CAPSTONE — Xarajatlar trekkeri (CLI ilova)</h2>

<pre class="mermaid">
flowchart TB
    USER["foydalanuvchi CLI"] -->|qo'shish/ro'yxat/hisobot| MENU["menu funksiyasi"]
    MENU -->|@dataclass| EX["Xarajat obyektlari"]
    EX -->|JSON saqlash| FILE["xarajatlar.json"]
    EX -->|comprehension + lambda| RAPORT["statistika"]
    RAPORT -->|f-string| OUT["chiroyli chiqish"]
</pre>

<p>Endi bu kursning <strong>11 ta texnikasi</strong> birga ishlaydi. Loyiha — terminalda ishlovchi xarajatlar trekkeri:</p>

<ul>
<li><strong>dataclass</strong> — Xarajat shakli</li>
<li><strong>JSON</strong> — fayl bilan saqlash</li>
<li><strong>type hints</strong> — har funksiyada</li>
<li><strong>dekoratorlar</strong> — <code>@timed</code>, <code>@with_save</code></li>
<li><strong>comprehensions</strong> — filterlash va agregatsiya</li>
<li><strong>lambda + sorted</strong> — top kategoriyalar</li>
<li><strong>generator</strong> — katta fayl o'qish</li>
<li><strong>regex</strong> — kategoriyani matn ichidan ajratish</li>
<li><strong>OOP</strong> — Tracker class + properties + dunder</li>
<li><strong>*args/**kwargs</strong> — menu komandalar</li>
</ul>

<h3>🏆 Loyiha demosi</h3>

<pre><code>$ python xarajatlar.py

=== Xarajatlar trekkeri ===
1) Qo'shish    2) Ro'yxat    3) Statistika    4) Kategoriya bo'yicha    0) Chiqish

Tanlov: 1
Tavsif: Tushlik #ovqat
Summa:  35000

✅ Qo'shildi: Xarajat(1, 'Tushlik', 35000.0, 'ovqat', '2026-06-06')

Tanlov: 3

=== STATISTIKA ===
Jami yozuvlar:    7
Jami summa:       412,000 UZS
O'rtacha xarajat: 58,857 UZS
Eng katta:        Noutbuk — 250,000 UZS
TOP kategoriyalar:
  1. texnika    250,000 UZS
  2. ovqat       95,000 UZS
  3. transport   67,000 UZS

⏱  hisobot_chiqish:   0.32 ms
</code></pre>

<h3>Loyihaning klass shakli</h3>

<pre><code>@dataclass
class Xarajat:
    id: int
    tavsif: str
    summa: float
    kategoriya: str
    sana: str

    @property
    def tasvir(self) -&gt; str:
        return f"#{self.id} {self.tavsif:&lt;20} {self.summa:&gt;10,.0f} UZS"


class Tracker:
    def __init__(self, fayl: Path):
        self.fayl = fayl
        self.xarajatlar: list[Xarajat] = []
        self._yuklash()

    def __len__(self):
        return len(self.xarajatlar)

    def __iter__(self):
        return iter(self.xarajatlar)

    @property
    def jami_summa(self) -&gt; float:
        return sum(x.summa for x in self.xarajatlar)

    @property
    def kategoriya_bo_yicha(self) -&gt; dict[str, float]:
        natija: dict[str, float] = {}
        for x in self.xarajatlar:
            natija[x.kategoriya] = natija.get(x.kategoriya, 0) + x.summa
        return natija

    def qo_sh(self, tavsif: str, summa: float, kategoriya: str = "boshqa"):
        x = Xarajat(
            id=self._keyingi_id(),
            tavsif=tavsif,
            summa=summa,
            kategoriya=kategoriya,
            sana=datetime.now().strftime("%Y-%m-%d"),
        )
        self.xarajatlar.append(x)
        self._saqlash()
        return x</code></pre>

<h3>Texnikalar qaerda ishlatilgan</h3>

<table>
<tr><th>Texnika</th><th>Qaerda</th></tr>
<tr><td>@dataclass</td><td>Xarajat shakli — `__init__/__repr__/__eq__` bepul</td></tr>
<tr><td>type hints</td><td>Har funksiya signaturasi — IDE va mypy uchun</td></tr>
<tr><td>JSON</td><td>`_yuklash`, `_saqlash` — fayl persistensiyasi</td></tr>
<tr><td>@property</td><td>jami_summa, kategoriya_bo_yicha — computed atributlar</td></tr>
<tr><td>@timed dekorator</td><td>Hisobot funksiyasini o'lchaydi</td></tr>
<tr><td>Comprehension</td><td>Filter va agregatsiya</td></tr>
<tr><td>sorted + lambda</td><td>TOP kategoriyalar</td></tr>
<tr><td>Generator</td><td>Katta fayl o'qish (.jsonl format ham)</td></tr>
<tr><td>Regex</td><td>Tavsifdan #kategoriya tegini ajratish</td></tr>
<tr><td>__len__, __iter__</td><td>Tracker'ni native container kabi ishlatish</td></tr>
</table>

<h3>Sizning vazifangiz</h3>

<p>Code section'dagi to'liq ishchi versiyani saqlang va kengaytirib chiqing:</p>

<ol>
<li><strong>Kategoriya filtri</strong> — faqat bitta kategoriya bo'yicha ro'yxat</li>
<li><strong>Vaqt filtri</strong> — oxirgi 7 kun yoki bu oy</li>
<li><strong>CSV export</strong> — Excel bilan ochish uchun</li>
<li><strong>Eng katta xarajat oyiga</strong> — sana parse qilish</li>
<li><strong>Budjet ogohlantirish</strong> — kategoriya bo'yicha chegara</li>
</ol>

<h3>📌 Kurs yakuni</h3>
<ul>
<li>Endi siz <strong>idiomatik Python</strong>'da yozasiz</li>
<li>Sizning kod'laringiz <strong>aniq shaklli, tip-xavfsiz va o'qimli</strong></li>
<li>Real APIs, fayllar va matn bilan ishlay olasiz</li>
<li>Class'laringiz endi anketa emas — <strong>tirik obyektlar</strong></li>
<li>Keyingi qadam: testlash (<code>pytest</code>), CI/CD, va katta loyihalar</li>
</ul>

<p><strong>Tabriklaymiz!</strong> Siz Python: Keyingi Bosqich kursini tamomladingiz. 🎉</p>
"""

L11_CODE = """\
# ─── CAPSTONE: Xarajatlar trekkeri (CLI ilova) ────────────────────────────
# To'liq ishchi versiya. Saqlang va `python capstone.py` bilan ishga tushiring.
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from functools import wraps
from pathlib import Path

DATA_FILE = Path(__file__).parent / "demo_xarajatlar.json"


# ── Dekorator: vaqt o'lchash ──────────────────────────────────────────────
def timed(funk):
    @wraps(funk)
    def wrapper(*args, **kwargs):
        b = time.perf_counter()
        natija = funk(*args, **kwargs)
        ms = (time.perf_counter() - b) * 1000
        print(f"⏱  {funk.__name__:<22} {ms:>6.2f} ms")
        return natija
    return wrapper


# ── Domain model: Xarajat ─────────────────────────────────────────────────
@dataclass
class Xarajat:
    id: int
    tavsif: str
    summa: float
    kategoriya: str = "boshqa"
    sana: str = ""
    teglar: list[str] = field(default_factory=list)

    @property
    def tasvir(self) -> str:
        teg_s = " ".join(f"#{t}" for t in self.teglar)
        return (
            f"#{self.id:>3}  {self.sana}  "
            f"{self.tavsif:<22}  {self.summa:>12,.0f} UZS  "
            f"[{self.kategoriya}]  {teg_s}"
        )


# ── Tracker class — OOP qatlami ───────────────────────────────────────────
class Tracker:
    KATEGORIYA_PAT = re.compile(r"#(\\w+)")

    def __init__(self, fayl: Path):
        self.fayl = fayl
        self.xarajatlar: list[Xarajat] = []
        self._yuklash()

    # ── Dunder metodlar — container behavior ─────────────────────────────
    def __len__(self) -> int:
        return len(self.xarajatlar)

    def __iter__(self):
        return iter(self.xarajatlar)

    def __getitem__(self, i: int) -> Xarajat:
        return self.xarajatlar[i]

    def __repr__(self) -> str:
        return f"Tracker({len(self)} ta xarajat, {self.jami_summa:,.0f} UZS)"

    # ── Computed atributlar (@property) ──────────────────────────────────
    @property
    def jami_summa(self) -> float:
        return sum(x.summa for x in self.xarajatlar)

    @property
    def o_rta_summa(self) -> float:
        return self.jami_summa / len(self) if self else 0

    @property
    def kategoriya_bo_yicha(self) -> dict[str, float]:
        natija: dict[str, float] = {}
        for x in self.xarajatlar:
            natija[x.kategoriya] = natija.get(x.kategoriya, 0) + x.summa
        return natija

    # ── O'zgartiruvchi metodlar ──────────────────────────────────────────
    def qo_sh(self, tavsif: str, summa: float, **maydonlar) -> Xarajat:
        kategoriya = maydonlar.get("kategoriya", "boshqa")
        teglar = self.KATEGORIYA_PAT.findall(tavsif)
        tavsif_toza = self.KATEGORIYA_PAT.sub("", tavsif).strip()
        if teglar and kategoriya == "boshqa":
            kategoriya = teglar[0]

        x = Xarajat(
            id=self._keyingi_id(),
            tavsif=tavsif_toza,
            summa=summa,
            kategoriya=kategoriya,
            sana=maydonlar.get("sana", datetime.now().strftime("%Y-%m-%d")),
            teglar=teglar,
        )
        self.xarajatlar.append(x)
        self._saqlash()
        return x

    def filter(self, **shartlar) -> list[Xarajat]:
        natija = self.xarajatlar
        for kalit, qiymat in shartlar.items():
            natija = [x for x in natija if getattr(x, kalit, None) == qiymat]
        return natija

    # ── Persistensiya (JSON) ─────────────────────────────────────────────
    def _yuklash(self) -> None:
        if not self.fayl.exists():
            return
        with open(self.fayl, encoding="utf-8") as f:
            raw = json.load(f)
        self.xarajatlar = [Xarajat(**r) for r in raw]

    def _saqlash(self) -> None:
        with open(self.fayl, "w", encoding="utf-8") as f:
            json.dump(
                [asdict(x) for x in self.xarajatlar],
                f, ensure_ascii=False, indent=2,
            )

    def _keyingi_id(self) -> int:
        return max((x.id for x in self.xarajatlar), default=0) + 1


# ── Hisobot funksiyasi (@timed dekoratorlangan) ───────────────────────────
@timed
def hisobot(tr: Tracker) -> None:
    if not tr:
        print("Hech qanday yozuv yo'q.")
        return

    print("\\n=== STATISTIKA ===")
    print(f"Jami yozuvlar:    {len(tr)}")
    print(f"Jami summa:       {tr.jami_summa:>12,.0f} UZS")
    print(f"O'rtacha xarajat: {tr.o_rta_summa:>12,.0f} UZS")

    eng_katta = max(tr.xarajatlar, key=lambda x: x.summa)
    eng_kichik = min(tr.xarajatlar, key=lambda x: x.summa)
    print(f"Eng katta:        {eng_katta.tavsif} — {eng_katta.summa:,.0f}")
    print(f"Eng kichik:       {eng_kichik.tavsif} — {eng_kichik.summa:,.0f}")

    print("\\nTOP kategoriyalar:")
    top = sorted(
        tr.kategoriya_bo_yicha.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )
    for o_rin, (kat, summa) in enumerate(top[:5], 1):
        print(f"  {o_rin}. {kat:<15} {summa:>12,.0f} UZS")


# ── CLI menu ─────────────────────────────────────────────────────────────
def menu_ko_rsatish():
    print("\\n=== Xarajatlar trekkeri ===")
    print("1) Qo'shish    2) Ro'yxat    3) Statistika    4) Kategoriya filtri    0) Chiqish")


def main():
    tr = Tracker(DATA_FILE)
    print(repr(tr))

    while True:
        menu_ko_rsatish()
        tanlov = input("Tanlov: ").strip()

        if tanlov == "1":
            tavsif = input("Tavsif (#kategoriya bilan): ").strip()
            try:
                summa = float(input("Summa: "))
            except ValueError:
                print("❌ Summa noto'g'ri")
                continue
            x = tr.qo_sh(tavsif, summa)
            print(f"✅ Qo'shildi: {x.tasvir}")

        elif tanlov == "2":
            if not tr:
                print("Bo'sh.")
                continue
            for x in tr:
                print(x.tasvir)

        elif tanlov == "3":
            hisobot(tr)

        elif tanlov == "4":
            kat = input("Kategoriya: ").strip()
            mos = tr.filter(kategoriya=kat)
            if not mos:
                print("Topilmadi.")
            else:
                for x in mos:
                    print(x.tasvir)
                print(f"  Jami: {sum(x.summa for x in mos):,.0f} UZS ({len(mos)} ta)")

        elif tanlov == "0":
            print("Xayr! 👋")
            break

        else:
            print("Noma'lum tanlov")


if __name__ == "__main__":
    main()
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise builders — identical contract to seed_python_basics.py
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
# Per-lesson exercises — filled in by subsequent edits.
# ─────────────────────────────────────────────────────────────────────────────
L1_EX: list = [
    mc("Quyidagi kod nima qaytaradi?\n`[x * 2 for x in range(4)]`",
       ["[0, 2, 4, 6]", "[2, 4, 6, 8]", "[1, 2, 3, 4]", "SyntaxError"],
       "A", hint="range(4) — 0, 1, 2, 3. Har birini 2 ga ko'paytiring.",
       diff="Easy", pts=2),
    mc("`{x: x*x for x in range(3)}` nima qaytaradi?",
       ["{0: 0, 1: 1, 2: 4}", "[0, 1, 4]", "{0, 1, 4}", "(0, 1, 4)"],
       "A", hint="`{kalit: qiymat ...}` — bu dict comprehension.",
       diff="Easy", pts=2),
    mc("Comprehension ichidagi `if` qaerda kelishi mumkin?",
       ["Faqat `for` dan oldin (ifoda ichida if/else)",
        "Faqat `for` dan keyin (filter)",
        "Ikkalasi ham — har xil ma'noda",
        "Comprehension ichida `if` ishlatib bo'lmaydi"],
       "C",
       hint="Filterlash uchun for dan keyin, har element uchun tanlov uchun ifoda ichida.",
       explanation="`[x for x in nums if x>0]` — filter. `[(\"+\" if x>0 else \"-\") for x in nums]` — har element uchun tanlov.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari TO'G'RI Python sintaksisi?",
       ["[x*2 for x in range(5)]",
        "{x: x*2 for x in range(5)}",
        "{x*2 for x in range(5)}",
        "[for x in range(5): x*2]",
        "(x*2 for x in range(5))"],
       "A,B,C,E", multi=True,
       hint="To'rttasi — list/dict/set/generator. Bittasi noto'g'ri (for oldin ifoda kerak).",
       diff="Medium", pts=3),
    dd("Talabalar ro'yxatidan 80+ ballilarni ismlari bilan dict qilish bosqichlari",
       ["talabalar = [{'ism': 'Ali', 'ball': 87}, {'ism': 'Vali', 'ball': 54}]",
        "# Dict comprehension boshlanadi",
        "natija = {",
        "    t['ism']: t['ball']",
        "    for t in talabalar",
        "    if t['ball'] >= 80",
        "}",
        "print(natija)"],
       diff="Medium", pts=3),
    ti("`[x for qator in matritsa for x in qator]` — bu nima qiladi va `for`'lar tartibi nima uchun shu tarzda?",
       "Bu — flatten (tekislash). 2 darajali list'ni 1 darajaga aylantiradi. "
       "for'lar oddiy ichma-ich sikldek o'qiladi: tashqi `for qator in matritsa`, "
       "uning ichida `for x in qator`. Demak chap-o'ng tartibida — tashqaridan ichkariga. "
       "Agar tartib teskari yozilsa (`for x in qator for qator in matritsa`) — NameError, "
       "chunki qator hali aniqlanmagan.",
       hint="Comprehension ichidagi for'lar oddiy nested sikldek o'qilishini eslang.",
       diff="Hard", pts=4),
    mc("Comprehension qachon EMAS ideal tanlov?",
       ["Yangi list yaratish kerak bo'lganda",
        "Filterlash kerak bo'lganda",
        "Yon ta'siri (print, fayl yozish) bilan ishlash kerak bo'lganda",
        "Ko'paytirish jadvali yaratganda"],
       "C",
       explanation="Comprehension faqat yangi kolleksiya yaratish uchun. print yoki fayl yozish kerak bo'lsa — oddiy for siklini ishlating.",
       diff="Medium", pts=3),
]
L2_EX: list = [
    mc("Generator function nimasi bilan oddiy funksiyadan farq qiladi?",
       ["`return` o'rniga `yield` ishlatadi",
        "Faqat tug'ma sonlar qaytaradi",
        "Hech qachon to'xtamaydi",
        "Faqat class ichida bo'lishi kerak"],
       "A",
       hint="Funksiya tanasida `yield` bo'lsa — bu generator funksiyasi.",
       diff="Easy", pts=2),
    mc("`g = (x*x for x in range(3))` qatori darhol qancha hisoblaydi?",
       ["3 ta kvadratni hisoblaydi va xotirada saqlaydi",
        "Hech narsa hisoblamaydi — faqat generator obyekt yaratadi",
        "Faqat birinchi elementni hisoblaydi",
        "Xatolik beradi — sintaksis noto'g'ri"],
       "B",
       explanation="Generator expression lazy — chaqirilmaguncha hech narsa hisoblamaydi. Bu uning katta afzalligi.",
       diff="Medium", pts=3),
    mc("Quyidagi kod nima chiqaradi?\n```\ng = (x for x in [1, 2, 3])\nprint(list(g))\nprint(list(g))\n```",
       ["[1, 2, 3]\\n[1, 2, 3]",
        "[1, 2, 3]\\n[]",
        "[1, 2, 3]\\nStopIteration",
        "[]\\n[]"],
       "B",
       hint="Generatorni ikki marta to'liq o'qish mumkinmi?",
       explanation="Generator bir martalik. Birinchi list() uni to'liq o'qib bo'ldi, ikkinchisida hech narsa qolmadi.",
       diff="Medium", pts=3),
    mc("Quyidagi holatlarda qaysisi GENERATOR uchun yaxshiroq tanlov?",
       ["10 ta talabaning bahlarini saqlash",
        "1 milliard tasodifiy sonni bittadan ishlatish",
        "Indeks bo'yicha mahsulotni topish",
        "Nomlarni alifbo tartibida saralash",
        "1GB log faylidan ERROR satrlarini chiqarish"],
       "B,E", multi=True,
       hint="Generator — katta yoki cheksiz, bir marta sweep qilinadigan oqimlar uchun. Kichik kolleksiyalar yoki random access kerak bo'lsa — list.",
       diff="Medium", pts=3),
    dd("Logdan faqat ERROR qatorlarni vaqt belgisi bilan chiqaruvchi pipeline qadamlari",
       ["def manba():",
        "    for q in open('log.txt'):",
        "        yield q.strip()",
        "",
        "def faqat_error(qatorlar):",
        "    for q in qatorlar:",
        "        if q.startswith('ERROR'):",
        "            yield q",
        "",
        "for satr in faqat_error(manba()):",
        "    print(satr)"],
       diff="Medium", pts=3),
    ti("`yield from` qachon kerak va oddiy `for ... yield` dan nimasi yaxshi?",
       "`yield from` boshqa iterable yoki sub-generatorni birma-bir 'qayta uzatadi'. "
       "`for x in other: yield x` bilan funksional bir xil, ammo qisqaroq va PEP380 bo'yicha "
       "sub-generator'ning natijasini, .send() va istisnolarini ham to'g'ri propagatsiya qiladi. "
       "Tipik foydalanish — bir nechta iterable'ni birlashtirish, rekursiv generator ichida "
       "(masalan, daraxtni traverse), yoki sub-generator orqali quvvatni delegate qilish.",
       hint="Bir nechta iterable yoki rekursiv generator ichida juda foydali.",
       diff="Hard", pts=4),
    mc("`for line in open('big.log'):` qatorida `open()` qaytadigan obyekt qanday?",
       ["Butun faylni RAM ga yuklaydi",
        "Generator/iterator — qator-qator lazy o'qiydi",
        "List of strings — har element bitta qator",
        "Faqat birinchi qatorni qaytaradi"],
       "B",
       explanation="Fayl obyekti iterator — har iteratsiyada keyingi qatorni o'qiydi. Shuning uchun 100 GB faylni ham xotirani buzmasdan o'qish mumkin.",
       diff="Medium", pts=3),
]
L3_EX: list = [
    mc("`(lambda x, y: x * y)(3, 4)` nima qaytaradi?",
       ["7", "12", "x * y", "Xatolik"],
       "B",
       hint="Lambda darhol chaqirilgan — ikki argument bilan.",
       diff="Easy", pts=2),
    mc("`sorted([{'a': 2}, {'a': 1}], key=lambda d: d['a'])` natijasi qanday?",
       ["[{'a': 1}, {'a': 2}]",
        "[{'a': 2}, {'a': 1}]",
        "[1, 2]",
        "TypeError"],
       "A",
       hint="key=lambda — har element uchun taqqoslash qiymatini ajratib chiqaradi.",
       diff="Easy", pts=2),
    mc("`max(['ali', 'vali', 'doniyor'], key=len)` nima qaytaradi?",
       ["'ali'", "'vali'", "'doniyor'", "3"],
       "C",
       hint="`key=len` — har stringning uzunligi bo'yicha taqqoslash. Eng uzun stringni topadi.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysi holatlarda LAMBDA YOMON tanlov?",
       ["sorted uchun bir qatorli kalit",
        "Tanasida 10 qatorlik logika va try/except",
        "Funksiyani 50 ta joyda ishlatish",
        "filter uchun shart",
        "Tanasida print() va boshqa yon ta'sirlar"],
       "B,C,E", multi=True,
       hint="Lambda — qisqa, qayta ishlatilmaydigan, sof ifodalar uchun. Murakkab logika yoki yon ta'sirlar uchun oddiy `def` yaxshiroq.",
       diff="Medium", pts=3),
    dd("Mahsulotlar ro'yxatidan eng arzon 3 tasini chiqarish bosqichlari",
       ["mahsulotlar = [",
        "    {'nom': 'Olma', 'narx': 12000},",
        "    {'nom': 'Non',  'narx': 4000},",
        "    {'nom': 'Sut',  'narx': 9000},",
        "]",
        "arzon = sorted(mahsulotlar, key=lambda m: m['narx'])",
        "eng_arzon_3 = arzon[:3]",
        "for m in eng_arzon_3:",
        "    print(m['nom'], m['narx'])"],
       diff="Medium", pts=3),
    ti("`map(f, xs)` va `[f(x) for x in xs]` — qaysi biri qachon yaxshiroq, nima uchun?",
       "Funksional jihatdan ikkalasi bir xil natija beradi (map'ni list() bilan o'rab). "
       "Comprehension ko'pchilik holatda pythonic — sintaksisi tanish, filter (`if`) qo'shish oson, "
       "ifoda murakkablashganda o'qish oson. map — tayyor funksiya bilan ishlatilganda (`map(str.upper, xs)`, "
       "`map(int, qatorlar)`) qisqaroq va tezroq, chunki lambda yaratish overheadi yo'q. "
       "Qoidasi: lambda yozishingiz kerak bo'lsa — comprehension; tayyor funksiya bo'lsa — map ham yaxshi.",
       hint="Tayyor funksiya borligi yoki yo'qligi tanlovni qiladi.",
       diff="Hard", pts=4),
    mc("`sorted(talabalar, key=lambda t: (-t['ball'], t['ism']))` nima qiladi?",
       ["Ball oshib bormoqda, ism tartibida saralaydi",
        "Ball kamayib boradi, teng ball uchun ism alifbo tartibida",
        "Faqat ism bo'yicha saralaydi",
        "TypeError beradi"],
       "B",
       hint="Tuple kalitda elementlar ketma-ket taqqoslanadi. `-t['ball']` — kamayuvchi tartib, `t['ism']` — oshib boruvchi.",
       explanation="Kalit sifatida tuple qaytarilganda Python avval birinchi elementni, keyin teng bo'lganda ikkinchisini taqqoslaydi.",
       diff="Hard", pts=4),
]
R1_EX: list = [
    mc("`sum(s['narx'] for s in savdolar)` qatorida `()` o'rniga `[]` yozsak qanday farq bor?",
       ["Hech qanday farq yo'q",
        "`[]` butun list yaratadi (xotira), `()` generator (xotira saqlanadi)",
        "`()` — set, `[]` — list",
        "`()` xato beradi — sum() faqat list qabul qiladi"],
       "B",
       hint="sum() ikkalasi bilan ham ishlaydi, lekin xotira sarfi farq qiladi.",
       diff="Medium", pts=3),
    mc("Sotuvchilar nomlari to'plamini olish uchun qaysi to'g'ri?",
       ["[s['sotuvchi'] for s in savdolar]",
        "{s['sotuvchi'] for s in savdolar}",
        "{s['sotuvchi']: 0 for s in savdolar}",
        "list(map(lambda s: s['sotuvchi'], savdolar))"],
       "B",
       hint="Takrorlanmas to'plam — set comprehension `{}`.",
       explanation="A va D list (takror bilan), B set (takrorsiz), C dict.",
       diff="Easy", pts=2),
    mc("Eng katta savdoni topish uchun qaysilari TO'G'RI?",
       ["max(savdolar, key=lambda s: s['narx'])",
        "max([s['narx'] for s in savdolar])",
        "sorted(savdolar, key=lambda s: s['narx'])[-1]",
        "max(savdolar)['narx']"],
       "A,B,C", multi=True,
       hint="A — butun dict qaytaradi, B — eng katta narx, C — saralab oxirgini olish. D — savdolar dict'lar bo'lgani uchun max() to'g'ridan-to'g'ri ishlamaydi.",
       diff="Medium", pts=3),
    dd("Har sotuvchi uchun jami summani hisoblovchi dict yaratish bosqichlari",
       ["sotuvchilar = {s['sotuvchi'] for s in savdolar}",
        "jami = {",
        "    sot: sum(",
        "        s['narx'] for s in savdolar",
        "        if s['sotuvchi'] == sot",
        "    )",
        "    for sot in sotuvchilar",
        "}",
        "print(jami)"],
       diff="Medium", pts=3),
    ti("Generator pipeline pattern (filter -> transform -> filter) kichik list uchun ham foydalimi?",
       "Kichik list uchun ham foydali, lekin asosiy yutuq emas — bu yerda comprehension yoki "
       "oddiy for ham ishlatish mumkin. Generator pipeline'ning haqiqiy kuchi quyidagilarda: "
       "1) katta yoki cheksiz oqim (CSV, log, API stream); "
       "2) erta to'xtatish — `for x in oqim: if shart: break` — qolgan elementlar hech qachon hisoblanmaydi; "
       "3) modullilik — har bosqich alohida funksiya, qayta ishlatish va testlash oson. "
       "Kichik list uchun list comprehension odatda o'qimli va tez.",
       hint="Erta to'xtatish va xotira — asosiy yutuq.",
       diff="Hard", pts=4),
    mc("TOP 3 sotuvchini ball bo'yicha kamayuvchi tartibda olish — qaysi biri to'g'ri?",
       ["sorted(jami.items(), key=lambda x: x[1], reverse=True)[:3]",
        "sorted(jami.items(), key=lambda x: x[1])[:3]",
        "list(jami.items())[:3]",
        "max(jami.items(), key=lambda x: x[1])"],
       "A",
       hint="Kamayuvchi tartib — `reverse=True`. Birinchi 3 ta — `[:3]`.",
       diff="Medium", pts=3),
]
L4_EX: list = [
    mc("`def f(*args): print(type(args))` chaqirilganda nima chiqaradi?",
       ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"],
       "B",
       hint="*args — positional argumentlarni TUPLE ga yig'adi.",
       diff="Easy", pts=2),
    mc("`f(**{'a': 1, 'b': 2})` qatori `f` ga qanday argumentlar yuboradi?",
       ["f([{'a': 1, 'b': 2}])",
        "f(a=1, b=2)",
        "f({'a': 1, 'b': 2})",
        "f('a', 1, 'b', 2)"],
       "B",
       hint="`**dict` chaqiruv joyida — kalitlarni keyword argumentga aylantiradi.",
       diff="Easy", pts=2),
    mc("Quyidagi qaysilari TO'G'RI funksiya signaturasi?",
       ["def f(a, b, *args, **kwargs):",
        "def f(*args, a, b, **kwargs):",
        "def f(**kwargs, *args):",
        "def f(a, *, b):",
        "def f(*, a, b):"],
       "A,B,D,E", multi=True,
       hint="**kwargs DOIM oxirgi. * yoki *args dan keyin — keyword-only.",
       explanation="C noto'g'ri — **kwargs *args dan keyin kelishi shart, lekin DOIM oxirgi parametr.",
       diff="Medium", pts=3),
    mc("`a, *o, c = [1, 2, 3, 4, 5]` natijasi qanday?",
       ["a=1, o=[2,3,4], c=5",
        "a=1, o=2, c=3 — qolgani tashlanadi",
        "a=[1], o=[2,3,4,5], c=[] ",
        "ValueError"],
       "A",
       hint="* — 'qolganlari', list ga yig'iladi. Boshi va oxiri alohida o'zgaruvchilarga.",
       diff="Medium", pts=3),
    dd("`config` ni `defaults` ustiga qo'yib birlashma yaratish bosqichlari",
       ["defaults = {'theme': 'dark', 'lang': 'uz', 'timeout': 30}",
        "config = {'lang': 'en', 'verbose': True}",
        "# defaults ustiga config qo'yiladi — config kalitlari ustun",
        "final = {**defaults, **config}",
        "print(final)"],
       diff="Medium", pts=3),
    ti("`def yuborish(adress, *, port, ssl=False)` — nima uchun `*` shu yerda foydali?",
       "`*` undan keyingi argumentlarni KEYWORD-ONLY qiladi. Demak `yuborish('ya.ru', port=443, ssl=True)` "
       "majburiy, `yuborish('ya.ru', 443, True)` — TypeError. Bu chaqiruvni o'qimli qiladi: "
       "har bir flag/sozlama ismi bilan ko'rinadi, pozitsiya bilan adashtirib bo'lmaydi. "
       "Ayniqsa boolean argumentlar uchun foydali — kelajakda yangi parametr qo'shsangiz "
       "tartibni o'zgartirib eskilarni buzmaysiz.",
       hint="Keyword-only — API dizayni va kelajakdagi parametrlar uchun.",
       diff="Hard", pts=4),
    mc("`def wrapper(*args, **kwargs): return funk(*args, **kwargs)` — `*` va `**` chaqiruv joyida nima qiladi?",
       ["Tanasidan tuple va dict yaratadi",
        "Tuple va dict elementlarini ochib funk ga argumentga aylantiradi",
        "Argumentlarni kvadratga ko'taradi",
        "Hech narsa — sintaktik shovqin"],
       "B",
       explanation="def ichida * yig'adi, chaqiruvda * ochadi. wrapper qabul qilgan har qanday argumentni funk ga qayta uzatadi — bu decorator'larning asosi.",
       diff="Medium", pts=3),
]
L5_EX: list = [
    mc("`@decorator` qatori `def f(): ...` ustida nimaning qisqartmasi?",
       ["f.decorator()",
        "f = decorator(f)",
        "decorator.f = f",
        "decorator(f, decorator)"],
       "B",
       hint="Dekorator funksiyani argument qiladi va yangi funksiyani qaytaradi.",
       diff="Easy", pts=2),
    mc("Dekorator wrapper'ida `@functools.wraps(funk)` qo'shilmasa nima yo'qoladi?",
       ["Funksiya umuman ishlamaydi",
        "`funk.__name__`, `funk.__doc__` va boshqa metadata wrapper'niki bilan almashinadi",
        "`return` qiymati o'zgaradi",
        "Hech narsa — wraps faqat dekoratsiya"],
       "B",
       hint="wraps — metadata ko'chiruvchi.",
       explanation="wraps siz dekoratorlangan funksiyaning __name__='wrapper', __doc__=None bo'lib qoladi. Debug va help() ishonchsiz.",
       diff="Medium", pts=3),
    mc("`@lru_cache` nimani qiladi?",
       ["Funksiya tezligini sun'iy oshiradi",
        "Bir xil argumentlar bilan qayta chaqirilganda saqlangan natijani qaytaradi",
        "Funksiyani parallel ishlatadi",
        "Argumentlarni avtomatik tekshiradi"],
       "B",
       hint="Cache — saqlash. Bir marta hisoblangan natijani saqlab qayta foydalanadi.",
       diff="Medium", pts=3),
    mc("`@retry(marotaba=5)` — bu qaysi turdagi dekorator?",
       ["Parametrsiz dekorator",
        "Parametrli dekorator — `retry(marotaba=5)` chaqiruvi dekoratorni qaytaradi",
        "Class dekoratori",
        "Bu sintaksis xato"],
       "B",
       hint="Qavslar bor — chaqiruv. Chaqiruv natijasi dekorator bo'lishi kerak.",
       explanation="Parametrli dekorator 3 qatlamli: parametr → funk → wrapper.",
       diff="Medium", pts=3),
    dd("Parametrli `@log_level('INFO')` dekoratorini yozish bosqichlari",
       ["from functools import wraps",
        "",
        "def log_level(level):",
        "    def dek(funk):",
        "        @wraps(funk)",
        "        def wrapper(*args, **kwargs):",
        "            print(f'[{level}] {funk.__name__}({args}, {kwargs})')",
        "            return funk(*args, **kwargs)",
        "        return wrapper",
        "    return dek",
        "",
        "@log_level('INFO')",
        "def f(x): return x * 2"],
       diff="Hard", pts=4),
    ti("`@timer` va `@retry(3)` ni bitta funksiyaga stack qilganda tartib nima uchun muhim?",
       "Eng pastdagi dekorator (funksiyaga eng yaqin) birinchi qo'llaniladi. "
       "`@timer / @retry(3) / def f` — `f` avval retry bilan o'raladi (3 marta urinish), "
       "keyin natija timer bilan o'raladi (BUTUN retry mantiqining vaqtini o'lchaydi). "
       "Teskari yozsak (`@retry(3) / @timer / def f`) — retry har urinishni alohida timer "
       "bilan o'raydi. Birinchi shakli odatda kerak: 'shu funksiya muvaffaqiyatga erishish "
       "uchun necha sekund sarflandi'. Demak: tashqi dekorator — umumiy o'lchash; ichki — har urinish.",
       hint="Pastdagi dekorator funksiyaga yaqinroq → birinchi o'raladi.",
       diff="Hard", pts=4),
    mc("Quyidagi qaysi vaziyatlar uchun dekorator IDEAL?",
       ["Bir necha funksiyaga timing qo'shish",
        "Class atributini saqlash",
        "Auth tekshirish (faqat admin ishlatsin)",
        "Bir funksiyaga 1 ta if shartini qo'shish",
        "Retry / caching mexanizmi"],
       "A,C,E", multi=True,
       hint="Dekorator — qayta ishlatiladigan 'g'ilof'. Bir martalik o'zgarish uchun overkill.",
       diff="Medium", pts=3),
]
L6_EX: list = [
    mc("`def f(x: int) -> str:` qatoriga `f('salom')` chaqirilsa nima bo'ladi?",
       ["TypeError — int kerak",
        "Python type hint'ni runtime'da tekshirmaydi — odatda ishlaydi",
        "Avtomatik str ga konvertatsiya",
        "Ogohlantirish chiqaradi, lekin davom etadi"],
       "B",
       hint="Type hints — IDE va mypy uchun, Python runtime'da tekshirmaydi.",
       diff="Easy", pts=2),
    mc("`@dataclass` qaysi metodlarni avtomatik yaratadi?",
       ["__init__",
        "__repr__",
        "__eq__",
        "__add__",
        "__hash__ (default holatda)"],
       "A,B,C", multi=True,
       hint="dataclass default holatda 3 ta asosiy dunder beradi. __add__ va __hash__ default emas.",
       diff="Medium", pts=3),
    mc("`@dataclass class X: items: list = []` — bu yerda muammo nima?",
       ["Hech qanday muammo yo'q",
        "list type hint noto'g'ri",
        "Mutable default — barcha instance bir xil list'ni baham ko'radi (yangi Python'da xato beradi)",
        "list'ga qiymat berish kerak"],
       "C",
       hint="Mutable default class darajasida bir marta yaratilib, barcha instance baham ko'radi.",
       explanation="To'g'ri: `items: list = field(default_factory=list)` — har instance uchun yangi list.",
       diff="Medium", pts=3),
    mc("`def first(xs: list[int]) -> int | None:` — qaytarish turi nima ma'noda?",
       ["Faqat int qaytaradi",
        "int yoki None qaytarishi mumkin",
        "Avval int, keyin None",
        "Sintaksis xato"],
       "B",
       hint="`X | None` — Optional[X] sintaksisi (Python 3.10+).",
       diff="Easy", pts=2),
    dd("`Vazifa` dataclass'ini default teglar list bilan to'g'ri yozish bosqichlari",
       ["from dataclasses import dataclass, field",
        "",
        "@dataclass",
        "class Vazifa:",
        "    id: int",
        "    matn: str",
        "    bajarildi: bool = False",
        "    teglar: list[str] = field(default_factory=list)"],
       diff="Medium", pts=3),
    ti("`@dataclass(frozen=True)` qachon foydali va qachon emas?",
       "Frozen instance — yaratilgandan keyin maydonlarni o'zgartirib bo'lmaydi (xato beradi). "
       "Foydali: 1) dict yoki set kalit sifatida ishlatish (hashable bo'ladi); "
       "2) immutable value objects (Pul, Nuqta, Sana) — debugging soddalashadi; "
       "3) concurrency — bir nechta thread bir vaqtning o'zida xavfsiz o'qiy oladi. "
       "Foydali emas: 1) maydonlari tez-tez o'zgarib turuvchi entities (Foydalanuvchi profili); "
       "2) builder pattern bilan asta-sekin to'ldiriladigan struktura; "
       "3) ichida o'zgaruvchan struktura (list, dict) — frozen faqat to'p darajasida ishlaydi.",
       hint="Hashability, debugging va concurrency — foydasi. Tez-tez o'zgarsa — to'siq.",
       diff="Hard", pts=4),
    mc("`asdict(dataclass_instance)` nima qaytaradi va qachon foydali?",
       ["Dataclass'ning class nomini string sifatida",
        "Maydonlardan tuzilgan dict — JSON ga konvertatsiya / API javobi uchun foydali",
        "Maydonlar ro'yxatini list sifatida",
        "Yangi instance yaratadi"],
       "B",
       hint="dataclasses moduli — asdict, astuple.",
       explanation="JSON yozish, API javobi, log uchun dataclass'ni dict'ga aylantirish odatiy.",
       diff="Medium", pts=3),
]
R2_EX: list = [
    mc("`def filterlash(yozuvlar, **filtrlar):` chaqirilganda `filtrlar` qanday turdagi?",
       ["list", "tuple", "dict", "set"],
       "C",
       hint="**kwargs — keyword'larni dict ga yig'adi.",
       diff="Easy", pts=2),
    mc("`@dataclass` `LogYozuv` ni dict ga aylantirish uchun qaysisi to'g'ri?",
       ["dict(LogYozuv)",
        "LogYozuv.to_dict()",
        "asdict(yozuv) — dataclasses moduli bilan",
        "json.dumps(yozuv)"],
       "C",
       hint="dataclasses moduli — asdict.",
       diff="Medium", pts=3),
    mc("Counter([y.level for y in yozuvlar]) qaytaradigan obyekt nima qiladi?",
       ["Sortirovka qiladi",
        "Har levelning soni: {'INFO': 4, 'ERROR': 3, 'WARN': 1}",
        "Faqat birinchi levelni qaytaradi",
        "TypeError beradi"],
       "B",
       hint="Counter — collections moduli, takrorlarni sanaydi.",
       diff="Medium", pts=3),
    dd("`@timed` dekoratorlangan funksiyani filter argumentlari bilan chaqirish bosqichlari",
       ["from dataclasses import dataclass",
        "from functools import wraps",
        "import time",
        "",
        "def timed(funk):",
        "    @wraps(funk)",
        "    def wrapper(*args, **kwargs):",
        "        b = time.perf_counter()",
        "        res = funk(*args, **kwargs)",
        "        print(f'{funk.__name__}: {time.perf_counter()-b:.3f}s')",
        "        return res",
        "    return wrapper",
        "",
        "@timed",
        "def filterlash(yozuvlar, **filtrlar): ...",
        "",
        "filterlash(yozuvlar, level='ERROR', sana='2026-06-01')"],
       diff="Hard", pts=4),
    ti("Nima uchun analytics funksiyalarni dataclass + dekorator kombinatsiyasi bilan yozish dict-only versiyadan yaxshiroq?",
       "1) Tip xavfsizligi — IDE `y.level` ni autocomplete qiladi, `y['levle']` (typo) ni darhol "
       "ko'rsatadi (dict'da kalit yo'qligi runtime'gacha sezilmaydi). "
       "2) O'qish — `y.foydalanuvchi_id` aniqligi `y.get('user_id')` dan ko'ra ravshan. "
       "3) Default qiymat va validation joyi (dataclass'ning __init__) — yaratish joyida tekshiramiz. "
       "4) Dekorator — har funksiyaga 1 qatorda timing, retry yoki cache qo'shamiz, oddiy "
       "funksiyalar o'zgarmaydi. 5) Refactoring xavfsizligi — maydon nomi o'zgarsa mypy aytadi.",
       hint="Tipiklik, o'qimlilik, refactoring xavfsizligi.",
       diff="Hard", pts=4),
    mc("`filterlash(yozuvlar, level='ERROR', foydalanuvchi_id=1)` — chaqiruv mantig'i nima?",
       ["Faqat birinchi argumentni qaytaradi",
        "level='ERROR' VA foydalanuvchi_id=1 ikkalasi to'g'ri keladigan yozuvlar",
        "level='ERROR' YOKI foydalanuvchi_id=1",
        "TypeError — birdaniga ikki filtr berib bo'lmaydi"],
       "B",
       explanation="**filtrlar dict bo'lib keladi, kod har kalit-qiymat juftligini tekshiradi — bu AND mantig'i.",
       diff="Medium", pts=3),
]
L7_EX: list = [
    mc("`json.dump(obj, f)` va `json.dumps(obj)` farqi nima?",
       ["Hech qanday farq yo'q",
        "dump faylga yozadi, dumps string qaytaradi",
        "dump str qaytaradi, dumps fayl yozadi",
        "dumps faqat dict qabul qiladi"],
       "B",
       hint="`s` harfi — string. `dump` faylga, `dumps` stringga.",
       diff="Easy", pts=2),
    mc("`json.dump(data, f, ensure_ascii=False)` da `ensure_ascii=False` nima uchun kerak?",
       ["JSON faylni kichraytirish uchun",
        "Unicode harflar (o'zbekcha, ruscha, xitoycha) `\\u...` ko'rinishida emas, o'z holicha yozilishi uchun",
        "Encoding xatosini oldini olish uchun",
        "Tezroq yozish uchun"],
       "B",
       hint="Default holatda JSON ASCII'dan tashqaridagi harflarni `\\u0410` ko'rinishida saqlaydi.",
       diff="Medium", pts=3),
    mc("CSV yozish uchun `open()` ga `newline=''` argumenti nima uchun majburiy?",
       ["Faqat Windows'da kerak",
        "csv moduli o'zining qator ajratuvchisini boshqaradi — `newline=''` bo'lmasa ortiqcha bo'sh qatorlar paydo bo'ladi",
        "Encoding muammosini hal qiladi",
        "Ixtiyoriy — hech qanday ta'siri yo'q"],
       "B",
       explanation="newline='' bo'lmasa, OS o'zining `\\n` qo'shadi va csv moduli ham qo'shadi — natijada qator orasida bo'sh qator paydo bo'ladi.",
       diff="Medium", pts=3),
    mc("Quyidagi qaysi tur'lar JSON ga to'g'ridan-to'g'ri yozilmaydi?",
       ["int, float, str, bool",
        "list, dict",
        "datetime",
        "set",
        "tuple",
        "dataclass instance"],
       "C,D,F", multi=True,
       hint="JSON faqat: object, array, string, number, true/false, null. Boshqalari uchun konvertatsiya kerak.",
       explanation="datetime — `default=str` orqali. set — list ga. dataclass — `asdict()` orqali. tuple JSON da array bo'lib yoziladi, lekin qaytarganda list bo'ladi.",
       diff="Hard", pts=4),
    dd("Foydalanuvchilar JSON faylidan o'qib, ball bo'yicha saralangan CSV yozish bosqichlari",
       ["import json, csv",
        "",
        "with open('foydalanuvchilar.json', encoding='utf-8') as f:",
        "    data = json.load(f)",
        "",
        "saralangan = sorted(data, key=lambda u: u['ball'], reverse=True)",
        "",
        "with open('top.csv', 'w', encoding='utf-8-sig', newline='') as f:",
        "    w = csv.DictWriter(f, fieldnames=['ism', 'ball'])",
        "    w.writeheader()",
        "    for u in saralangan:",
        "        w.writerow({'ism': u['ism'], 'ball': u['ball']})"],
       diff="Hard", pts=4),
    ti("`csv.reader` va `csv.DictReader` orasidagi tanlovni nima belgilaydi?",
       "DictReader — har qatorni dict ga aylantiradi (kalit = header). Foydali: kolonkalar tartibi "
       "o'zgarsa kod sinmaydi (chunki kalit bilan murojaat qilamiz), o'qish ravshan "
       "(`row['narx']` aniqligi `row[2]` dan ko'ra). Reader — list of strings. Foydali: header yo'q "
       "(faqat data qatorlari), katta fayllarni juda tez o'qish (dict yaratish overheadi yo'q), "
       "har qator bir xil shaklda. Standart tavsiya: header bor — DictReader, yo'q — reader.",
       hint="Tartib o'zgarishiga moslashish va o'qimlilikning sof tezlikka teng-tenglashtirish.",
       diff="Hard", pts=4),
    mc("`json.dumps({'sana': datetime.now()})` qatori nima qaytaradi?",
       ["ISO format string'ga aylantirilgan JSON",
        "TypeError — datetime serializable emas",
        "Bo'sh dict",
        "None"],
       "B",
       hint="JSON datetime ni qo'llab-quvvatlamaydi. `default=str` qo'shish kerak.",
       diff="Medium", pts=3),
]
L8_EX: list = [
    mc("`requests.get(url).json()` — bu nima qiladi?",
       ["URL ga JSON yuboradi",
        "GET so'rov yuboradi va javob body'sini Python obyektga (dict/list) parse qiladi",
        "URL ni JSON formatiga aylantiradi",
        "Faqat status code qaytaradi"],
       "B",
       hint="GET — o'qish, .json() — javob body'sini parse.",
       diff="Easy", pts=2),
    mc("`requests.get(url, params={'q': 'python', 'page': 2})` qatori qanday URL yaratadi?",
       ["{url}?q=python&page=2",
        "{url}/q=python/page=2",
        "{url} (params body'da yuboriladi)",
        "{url}?body={'q': 'python', 'page': 2}"],
       "A",
       hint="`params=` — query string. GET uchun body emas, URL ga qo'shiladi.",
       diff="Medium", pts=3),
    mc("`timeout=10` argumenti nima uchun MUHIM?",
       ["Estetik tartib uchun",
        "Default holatda timeout YO'Q — server javob bermasa dastur cheksiz kutadi",
        "10 sekundda javob bermasa cache'dan oladi",
        "Optimallashtirish uchun"],
       "B",
       explanation="Productionda timeout bermaslik xavfli — bitta sekin endpoint butun servisni to'xtatishi mumkin.",
       diff="Medium", pts=3),
    mc("Quyidagi HTTP status kodlardan qaysilari MUVAFFAQIYAT degan ma'noda?",
       ["200", "201", "204", "301", "400", "404"],
       "A,B,C", multi=True,
       hint="2xx — muvaffaqiyat. 3xx — redirect. 4xx — client xato. 5xx — server xato.",
       diff="Medium", pts=3),
    dd("API'dan ma'lumot olib, xato bo'lsa to'g'ri ushlash bosqichlari",
       ["import requests",
        "from requests.exceptions import HTTPError, Timeout",
        "",
        "try:",
        "    r = requests.get(",
        "        'https://api.example.com/data',",
        "        timeout=10,",
        "        headers={'Authorization': 'Bearer XXX'},",
        "    )",
        "    r.raise_for_status()",
        "    data = r.json()",
        "except Timeout:",
        "    print('Timeout — server javob bermayapti')",
        "except HTTPError as e:",
        "    print(f'HTTP xato: {e}')"],
       diff="Hard", pts=4),
    ti("`r.raise_for_status()` nima qiladi va nima uchun manual `if r.status_code != 200` dan yaxshiroq?",
       "raise_for_status() — agar javob 4xx yoki 5xx bo'lsa `HTTPError` exception ko'taradi. "
       "Yaxshiroq: 1) `try/except HTTPError` bilan ushlash bir joyda — manual `if` har joyda takrorlanadi; "
       "2) 200 dan tashqari muvaffaqiyat kodlar ham bor (201 Created, 204 No Content, 206 Partial) — "
       "manual `== 200` ularni xato hisoblaydi. raise_for_status butun 2xx ni o'tkazib yuboradi; "
       "3) Pattern: try/except — xato ishlovchisi alohida block'da, asosiy logika toza qoladi; "
       "4) Stack trace — `requests.HTTPError` debug uchun aniq ma'lumot beradi.",
       hint="2xx oilasi keng. Pattern — try/except qulay.",
       diff="Hard", pts=4),
    mc("`requests.post(url, json=data)` va `requests.post(url, data=data)` farqi nima?",
       ["Hech qanday farq yo'q",
        "json= — JSON encoding + Content-Type: application/json. data= — form-encoded yoki raw.",
        "json= faqat GET uchun",
        "data= avtomatik dict ga aylantiradi"],
       "B",
       explanation="`json=` content-type ni avtomatik 'application/json' qiladi va Python obyektni JSON ga konvertatsiya qiladi. `data=` form-urlencoded yoki raw bytes uchun.",
       diff="Hard", pts=4),
]
L9_EX: list = [
    mc("`r\"\\d+\"` patterni nimani topadi?",
       ["Bir yoki ko'p raqamlar (123, 4567)",
        "Faqat bitta raqam",
        "Raqam VA harf",
        "Hech narsani — bu noto'g'ri sintaksis"],
       "A",
       hint="`\\d` — raqam, `+` — bir yoki ko'p.",
       diff="Easy", pts=2),
    mc("Nima uchun pattern oldida `r` qo'yiladi (`r\"\\d+\"`)?",
       ["Pattern qaytariladigan bo'lishi uchun",
        "Backslash'larni Python escape qilmasligi uchun (raw string)",
        "Tezroq ishlashi uchun",
        "Faqat dekoratsiya — farqi yo'q"],
       "B",
       hint="`\\n` — newline. Pattern uchun esa biz aniq `\\n` belgisini istaymiz.",
       explanation="Raw string `r\"...\"` — Python escape sequences'ni o'zgarishsiz qoldiradi, regex parser o'z ishini qiladi.",
       diff="Medium", pts=3),
    mc("`re.findall(r\"<.*>\", \"<b>a</b><i>b</i>\")` nima qaytaradi?",
       ["['<b>', '</b>', '<i>', '</i>']",
        "['<b>a</b><i>b</i>'] — butun bo'lakni",
        "['<b>', '<i>']",
        "Bo'sh list"],
       "B",
       hint="`*` — greedy. `<.*>` boshidan oxirgi `>` gacha hammasini oladi.",
       explanation="Non-greedy uchun `<.*?>` ishlatish kerak — eng kichik mos kelish.",
       diff="Medium", pts=3),
    mc("Quyidagi sintaksislarning qaysilari TO'G'RI regex?",
       ["[a-z]+",
        "(?:abc|def)",
        "\\d{3,5}",
        "\\b\\w+\\b",
        "[^abc]"],
       "A,B,C,D,E", multi=True,
       hint="Bu yerda hammasi to'g'ri. Yodlash uchun: diapazon, non-capturing group, miqdor, so'z chegarasi, negation.",
       diff="Medium", pts=3),
    dd("Matn ichidagi sanalarni `YYYY-MM-DD` dan `DD.MM.YYYY` ga aylantirish bosqichlari",
       ["import re",
        "matn = 'Bugun 2026-03-15 da yig\\'ilish'",
        "yangi = re.sub(",
        "    r'(\\d{4})-(\\d{2})-(\\d{2})',",
        "    r'\\3.\\2.\\1',",
        "    matn,",
        ")",
        "print(yangi)"],
       diff="Hard", pts=4),
    ti("`re.match` va `re.search` farqi nima va qachon qaysi biri kerak?",
       "re.match faqat matnning BOSHIDAN qidiradi — agar pattern oxiriga emas, boshiga "
       "to'g'ri kelmasa None qaytaradi. re.search — matnning HAR YERIDAN qidiradi, birinchi "
       "topilgan mos kelishni qaytaradi. Qachon match: validatsiya (butun matn shu shaklda bo'lsa "
       "kerak — masalan, paroldek). Qachon search: matn ichida biror joydan namuna izlash "
       "(odatda haqiqiy holatlarda kerak). Yangi boshlovchilar match deb noto'g'ri ishlatadi — "
       "agar matn boshida pattern bo'lmasa, None qaytadi va kod 'pattern yo'q' deb xato xulosa qiladi. "
       "Default tavsiya: search. Match — faqat butun matn validatsiyasi uchun.",
       hint="match — boshidan, search — istalgan joydan.",
       diff="Hard", pts=4),
    mc("`re.compile(r\"\\d+\")` qachon foydali?",
       ["Faqat bir marta ishlatiladigan pattern uchun",
        "Bir necha bor ishlatiladigan pattern uchun — pattern parse qilinmasdan saqlanadi (tezroq)",
        "Pattern xavfsizligi uchun",
        "Faqat fayl o'qish uchun"],
       "B",
       hint="Compile — pattern'ni oldindan tayyorlab qo'yadi. Tsikl ichida har safar yangidan parse qilmaslik uchun.",
       diff="Medium", pts=3),
]
R3_EX: list = [
    mc("R3 pipeline'da 3 ta qatlam qaysi tartibda ishlaydi?",
       ["CSV -> Regex -> HTTP",
        "HTTP -> Regex -> CSV (input -> transform -> output)",
        "Regex -> HTTP -> CSV",
        "Tartib muhim emas"],
       "B",
       hint="Input -> transform -> output — odatiy pattern.",
       diff="Easy", pts=2),
    mc("`re.compile(r'<[^>]+>')` pattern nimani qiladi?",
       ["Faqat <b> tegni topadi",
        "Istalgan HTML/XML teg (`<...>` ichida `>` belgisi bo'lmasligi shart)",
        "Faqat ochilgan teglarni",
        "Markdown'ni"],
       "B",
       hint="`[^>]+` — `>` dan tashqari bir yoki ko'p belgilar.",
       diff="Medium", pts=3),
    mc("Yangiliklar pipeline'iga qaysi qo'shimchalar foydali bo'ladi?",
       ["raise_for_status() bilan xato boshqaruvi",
        "@dataclass bilan Yangilik strukturasi",
        "@timed dekorator bilan har qatlam vaqtini o'lchash",
        "Yangiliklarni xotirada cheksiz to'plash"],
       "A,B,C", multi=True,
       hint="Production'da xato boshqaruvi, tip-xavfsizlik va vaqt o'lchovi har doim foydali. Cheksiz to'plash emas.",
       diff="Medium", pts=3),
    dd("API dan olib regex bilan tozalab CSV ga yozuvchi pipeline funksiyalari tartibi",
       ["import requests, re, csv",
        "",
        "def olish(url):",
        "    r = requests.get(url, timeout=10)",
        "    r.raise_for_status()",
        "    return r.json()",
        "",
        "def tozalash(matn):",
        "    return re.sub(r'<[^>]+>', '', matn).strip()",
        "",
        "def csv_yozish(elementlar, yo_l):",
        "    with open(yo_l, 'w', encoding='utf-8-sig', newline='') as f:",
        "        w = csv.DictWriter(f, fieldnames=['id', 'sarlavha'])",
        "        w.writeheader()",
        "        for e in elementlar:",
        "            w.writerow({'id': e['id'], 'sarlavha': tozalash(e['title'])})"],
       diff="Hard", pts=4),
    ti("Production pipeline'da xato qaerda boshqarilishi kerak — har funksiyadami yoki bitta joydami?",
       "Optimal pattern: ICHKI funksiyalar (yangiliklar_olish, matnni_tozalash) FAQAT o'z masuliyatiga "
       "tegishli xatolarni ushlaydi va specific exception ko'taradi (`NetworkError`, `ParseError`). "
       "TASHQI orkestrator (`main` yoki `run_pipeline`) — barchasini ushlaydi va loglashtiradi/foydalanuvchiga "
       "ko'rsatadi. Sabablari: 1) yangiliklar_olish'da timeout bo'lsa — qayta urinish (retry) yoki "
       "cache'dan olish foydali, lekin csv_ga_yozish bilan bir xil emas; 2) Test yozish oson — har "
       "funksiya alohida xatolanish stsenariylarini ushlaydi; 3) Stack trace yo'qolmaydi — `raise X from e` "
       "bilan kontekst saqlanadi. Yomon pattern: har funksiyada `try/except Exception: pass` — xatolar yashirinadi.",
       hint="Specific xato — past darajada. Umumiy boshqaruv — yuqori darajada.",
       diff="Hard", pts=4),
    mc("`asdict(yangilik)` qatori nima qaytaradi?",
       ["Yangilik klassining metodlari ro'yxati",
        "Dataclass maydonlaridan tuzilgan dict — JSON yozish uchun tayyor",
        "Yangilik instansiyasi nusxasi",
        "TypeError"],
       "B",
       hint="dataclasses.asdict — dataclass -> dict.",
       explanation="asdict ko'pincha JSON ga konvertatsiya yoki API javobi sifatida qaytarishdan oldin ishlatiladi.",
       diff="Medium", pts=3),
]
L10_EX: list = [
    mc("Sub-class `__init__` da `super().__init__(...)` chaqirmaslik nima oqibatlarga olib keladi?",
       ["Hech narsa — Python avtomatik chaqiradi",
        "Ota klassdagi atributlar yaratilmaydi — ularga murojaat AttributeError beradi",
        "Sub-class umuman yaratilmaydi",
        "SyntaxError"],
       "B",
       hint="Python avtomatik chaqirmaydi — siz aniq chaqirishingiz kerak.",
       explanation="Ota __init__ atributlarni o'rnatadi. Chaqirmasangiz, ular yaratilmaydi.",
       diff="Medium", pts=3),
    mc("`@property` bilan dekoratlangan metod qanday chaqiriladi?",
       ["obj.method()",
        "obj.method — qavslarsiz, xuddi atributga o'xshab",
        "property(obj.method)",
        "Metod ichidan o'zi chaqiriladi"],
       "B",
       hint="Property — metodni atributga o'xshatadi.",
       diff="Easy", pts=2),
    mc("`__str__` va `__repr__` orasidagi farq nima?",
       ["Hech qanday farq — bir narsa",
        "`__str__` foydalanuvchiga, `__repr__` dasturchiga (debug uchun)",
        "`__str__` faqat print uchun, `__repr__` faqat REPL uchun",
        "`__repr__` ko'proq raqamlar uchun"],
       "B",
       hint="`__str__` -> insonga; `__repr__` -> dasturchiga, ideal holatda eval() qilsa obyekt qaytadi.",
       diff="Medium", pts=3),
    mc("Quyidagi dunder metodlardan qaysilari `class`'ni LIST/SET kabi ishlatish imkonini beradi?",
       ["__iter__", "__len__", "__getitem__", "__contains__", "__add__"],
       "A,B,C,D", multi=True,
       hint="`__add__` qo'shish uchun, qolganlari container behavior beradi.",
       diff="Medium", pts=3),
    dd("`Pul` class'ini qo'shish, teng-tenglik va saralash uchun to'g'ri yozish bosqichlari",
       ["from functools import total_ordering",
        "",
        "@total_ordering",
        "class Pul:",
        "    def __init__(self, summa, valyuta='UZS'):",
        "        self.summa = summa",
        "        self.valyuta = valyuta",
        "",
        "    def __eq__(self, other):",
        "        return self.summa == other.summa and self.valyuta == other.valyuta",
        "",
        "    def __lt__(self, other):",
        "        return self.summa < other.summa",
        "",
        "    def __add__(self, other):",
        "        return Pul(self.summa + other.summa, self.valyuta)",
        "",
        "    def __hash__(self):",
        "        return hash((self.summa, self.valyuta))"],
       diff="Hard", pts=4),
    ti("`@property` bilan validatsiya qo'shish — qachon va nima uchun?",
       "Property + setter — atribut o'rniga ko'rinadi, lekin qiymat berishda VALIDATSIYA qiladi. "
       "Qachon: 1) qiymat fizikaviy/biznes chegaralariga ega (radius >= 0, yosh >= 0, foiz 0-100); "
       "2) bir atribut o'zgarsa boshqasini ham yangilash kerak (cache invalidatsiya); "
       "3) backward compatibility — eski `obj.x = 5` interfeysi qoladi, lekin endi tekshiriladi. "
       "Nima uchun atributdan ko'ra: 1) foydalanuvchi metod chaqirilayotganini sezmaydi — toza API; "
       "2) eski kodni buzmaydi; 3) hisoblanadigan atributlar (`obj.maydon` har safar hisoblanadi). "
       "Qoidalar: ichki saqlash uchun `_x` ishlating (private convention), setter'da `ValueError` ko'taring.",
       hint="Tashqi API toza, ichi tekshiruvchi.",
       diff="Hard", pts=4),
    mc("`Mashina IS-A Yo'l` — bu meros uchun TO'G'RI munosabatmi?",
       ["Ha, mashina yo'lda yuradi",
        "Yo'q — mashina yo'lga EGA emas. To'g'ri munosabat: Mashina yo'ldan foydalanadi (kompozitsiya)",
        "Ha, agar tezligi yo'l tezligidan past bo'lsa",
        "Faqat agar mashinada 4 g'ildirak bo'lsa"],
       "B",
       hint="IS-A va HAS-A munosabatlarini farqlash. Mashina yo'l emas — ular alohida obyektlar.",
       explanation="Meros — IS-A. It IS-A Hayvon ✅. Mashina IS-A Yo'l ❌ — kompozitsiya yoki assotsiatsiya kerak.",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("CAPSTONE Tracker'da `__len__` qaytaradigan funksiya nima imkonini beradi?",
       ["`Tracker()` yaratish",
        "`len(tr)` ishlatish va `if tr:` (truthy/falsy) tekshirish",
        "JSON saqlash",
        "Faqat dekoratsiya"],
       "B",
       hint="`len()` va boolean kontekst — `__len__` dan keladi.",
       diff="Easy", pts=2),
    mc("Tavsifda `#ovqat` deb yozilsa, regex `r'#(\\w+)'` qanday ishlaydi?",
       ["Hech narsani topmaydi",
        "['ovqat'] ni topadi va kategoriya sifatida ishlatadi",
        "Tavsifni o'chiradi",
        "Faylga yozadi"],
       "B",
       hint="Capture group `(\\w+)` — `#` dan keyin keladigan so'zni oladi.",
       diff="Medium", pts=3),
    mc("CAPSTONE'da `@timed` dekorator hisobot funksiyasi ustida nima qiladi?",
       ["Hisobotni 2 marta chiqaradi",
        "Hisobotning ishlash vaqtini millisekundlarda chiqaradi",
        "Hisobotni cache qiladi",
        "Hech narsa — dekoratsiya"],
       "B",
       diff="Easy", pts=2),
    mc("Quyidagi qaysi texnikalar CAPSTONE loyihasida ishlatilgan?",
       ["@dataclass va @property",
        "JSON saqlash (json.dump/load)",
        "Regex bilan tagsni ajratish",
        "sorted + lambda bilan TOP kategoriyalar",
        "@timed dekorator",
        "Type hints"],
       "A,B,C,D,E,F", multi=True,
       hint="Loyiha kursning barcha texnikalarini bir joyga jamlaydi.",
       diff="Medium", pts=3),
    dd("Tracker'ga yangi xarajat qo'shish va saqlash bosqichlari",
       ["from dataclasses import dataclass, asdict",
        "from datetime import datetime",
        "import json",
        "",
        "x = Xarajat(",
        "    id=tr._keyingi_id(),",
        "    tavsif='Tushlik',",
        "    summa=35000,",
        "    kategoriya='ovqat',",
        "    sana=datetime.now().strftime('%Y-%m-%d'),",
        ")",
        "tr.xarajatlar.append(x)",
        "",
        "with open(tr.fayl, 'w', encoding='utf-8') as f:",
        "    json.dump([asdict(y) for y in tr.xarajatlar], f, ensure_ascii=False, indent=2)"],
       diff="Hard", pts=4),
    ti("Tracker class'ga `__add__` qo'shilsa qaysi behavior'lar foydali bo'lishi mumkin?",
       "Bir nechta variant: 1) Ikki Tracker'ni qo'shish — yangi Tracker yaratiladi va ikkalasining "
       "xarajatlari birlashtiriladi (id konflikt bo'lmasligi uchun qayta nomerlash). Foydali: "
       "ikki kishining xarajatlarini birlashtirish, ikki oydagi yozuvlarni jamlash. "
       "2) Tracker + Xarajat — yangi xarajatni qo'shish — sintaktik shakar (`tr += x`). "
       "Lekin ehtiyot: __add__ immutable shaklda yaxshi (yangi Tracker), in-place o'zgarish "
       "uchun `__iadd__` ishlatish kerak. Yomon variant: __add__ ichida self.xarajatlar.append — "
       "`a + b` ifodasi `a` ni o'zgartirsa, foydalanuvchi hayron bo'ladi.",
       hint="Birlashma yoki qo'shish — har xil semantika.",
       diff="Hard", pts=4),
    mc("Loyihani productionga olib chiqish uchun keyingi qadam qaysi?",
       ["pytest bilan testlar yozish",
        "GUI qo'shish (tkinter/PyQt)",
        "SQLite ga ko'chirish",
        "Hammasi — qaysi ehtiyojga qarab",
        "Hech narsa — tayyor"],
       "D",
       hint="Loyiha tayyor — keyingi qadam ehtiyojga qarab tanlanadi.",
       explanation="Testlar — har doim. GUI/DB — foydalanuvchi soni va talablarga qarab.",
       diff="Medium", pts=3),
]


# ─────────────────────────────────────────────────────────────────────────────
# Per-lesson assignments
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {  # L1 — Comprehensions
        "title": "Talabalar hisobotchi (comprehension marafoni)",
        "description": (
            "Talabalar ro'yxatidan turli statistikani comprehension'lar bilan "
            "hisoblovchi modul. Hech qaysi `for` sikli `append` bilan ishlatilmasin."
        ),
        "requirements": (
            "• Kamida 4 ta list comprehension (filter va transform aralash)\n"
            "• Kamida 1 ta dict comprehension (ism -> daraja)\n"
            "• Kamida 1 ta set comprehension (takrorlanmas teglar)\n"
            "• Kamida 1 ta nested comprehension (matritsa yoki flatten)\n"
            "• Hech qaysi joyda `for ...: append(...)` ishlatilmasin\n"
            "• Bo'sh kirish uchun xavfsizlik (ValueError yoki default)"
        ),
        "technologies": "Python, list/dict/set comprehension, if/else ifoda ichida",
        "deadline_days": 3,
    },
    1: {  # L2 — Generators
        "title": "Log analyzer (generator pipeline)",
        "description": (
            "Katta log faylni xotirani band qilmasdan o'qib, ERROR satrlarni "
            "filterlovchi va statistikani qaytaruvchi pipeline. List ishlatilmasin."
        ),
        "requirements": (
            "• Generator funksiya: faylni qator-qator o'qish (`yield`)\n"
            "• Generator: faqat ERROR satrlarini filterlash\n"
            "• Generator: har satrga vaqt belgisi qo'shish\n"
            "• Pipeline 3 ta generator ketma-ket\n"
            "• Asosiy oqim — `for satr in pipeline` (list yaratilmaydi)\n"
            "• Statistika: jami satrlar va ERROR soni"
        ),
        "technologies": "Python, yield, generator expressions, fayl iteratori",
        "deadline_days": 3,
    },
    2: {  # L3 — Lambda, map, filter, sorted
        "title": "Mahsulot katalog qidiruvchisi",
        "description": (
            "Mahsulotlar ro'yxatidan turli mezonlar bilan saralash va qidirish. "
            "Asosan `sorted`, `min`, `max`, `filter`, `map` va `lambda` ishlatilsin."
        ),
        "requirements": (
            "• 10+ mahsulot dict ro'yxati (nom, narx, soni, kategoriya)\n"
            "• Narx bo'yicha saralash (oshib va kamayuvchi)\n"
            "• Bir nechta mezon bilan saralash — `key=lambda p: (-p['narx'], p['nom'])`\n"
            "• `min` va `max` ishlatib eng arzon/eng qimmatni topish\n"
            "• `filter` + `lambda` bilan kategoriya bo'yicha izlash\n"
            "• `map` ishlatib summa hisoblash (narx * soni)\n"
            "• Natijalar chiroyli f-string formatda"
        ),
        "technologies": "Python, lambda, sorted, key=, min/max, map, filter",
        "deadline_days": 4,
    },
    3: {  # R1 — Sotuvchi statistikasi
        "title": "🔁 R1: Restoran buyurtmalar statistikasi",
        "description": (
            "Restoran buyurtmalari ro'yxati asosida 3 ta texnikani birlashtirgan "
            "tahlil moduli. Eng yaxshi 3 ofitsiant, kunlik daromad, kategoriya."
        ),
        "requirements": (
            "• 15+ buyurtma (ofitsiant, taom, narx, sana, kategoriya)\n"
            "• Set comprehension bilan unique ofitsiantlar\n"
            "• Dict comprehension bilan ofitsiant -> jami summa\n"
            "• Sorted + lambda bilan TOP 3 ofitsiant\n"
            "• Generator expression bilan summa hisoblash\n"
            "• max(buyurtmalar, key=...) bilan eng katta buyurtmani topish\n"
            "• Kunlik (sana bo'yicha) statistika\n"
            "• Natija chiroyli jadval ko'rinishida"
        ),
        "technologies": "Python, comprehensions, generators, sorted+lambda",
        "deadline_days": 5,
    },
    4: {  # L4 — *args, **kwargs
        "title": "Konfiguratsiya birlashtiruvchi",
        "description": (
            "Bir nechta konfiguratsiya manbalaridan (default, env, user) yakuniy "
            "konfigni birlashtiruvchi moduli. *args, **kwargs va unpacking ishlatilsin."
        ),
        "requirements": (
            "• Funksiya `birlashtirish(*dictlar, **override)` qabul qiladi\n"
            "• Ichida `{**dict1, **dict2, **override}` bilan birlashma\n"
            "• Wrapper funksiya — `*args, **kwargs` ni qayta uzatadi\n"
            "• Keyword-only argument bilan funksiya — `def f(*, strict=False):`\n"
            "• Tuple unpacking ishlatish: `a, *qolgan, oxirgi = ro_yxat`\n"
            "• Default qiymatlar va override mantig'i tushuntirilsin (izoh bilan)"
        ),
        "technologies": "Python, *args, **kwargs, dict unpacking, keyword-only",
        "deadline_days": 3,
    },
    5: {  # L5 — Decorators
        "title": "Dekoratorlar to'plami (timer, retry, cache, log)",
        "description": (
            "4 ta turli dekorator yozish va ularni real funksiyalarda sinab ko'rish. "
            "Ulardan kamida bittasi parametrli bo'lsin."
        ),
        "requirements": (
            "• `@timer` — funksiya vaqtini millisekundlarda chiqaradi\n"
            "• `@retry(marotaba=N)` — parametrli, N marta urinadi\n"
            "• `@once` — funksiyani faqat bir marta chaqirishga ruxsat beradi\n"
            "• `@log_calls` — chaqiruv argumentlarini logga yozadi\n"
            "• Har bir dekoratorda `@functools.wraps` ishlatilgan\n"
            "• Kamida 2 ta dekorator stack qilingan misol\n"
            "• Test funksiyalar bilan ko'rsatish"
        ),
        "technologies": "Python, decorators, functools.wraps, *args/**kwargs, closures",
        "deadline_days": 5,
    },
    6: {  # L6 — Type hints + dataclasses
        "title": "Vazifa boshqaruvchisi (dataclasses bilan)",
        "description": (
            "Vazifalarni dataclass'lar bilan boshqaruvchi modul. Har funksiyada "
            "to'liq type hints, mutable default'lar to'g'ri ishlatilsin."
        ),
        "requirements": (
            "• `@dataclass class Vazifa` — id, matn, bajarildi, sana, teglar (default list)\n"
            "• `field(default_factory=list)` ishlatilgan\n"
            "• `@dataclass(frozen=True) class VazifaSnapshot` — immutable nusxa\n"
            "• Har funksiyada to'liq type hints: `def f(xs: list[Vazifa]) -> dict[str, int]:`\n"
            "• Kamida bitta `Callable[...]` parametri qabul qiluvchi funksiya\n"
            "• `asdict()` bilan JSON ga yozish demosi\n"
            "• `order=True` bilan vazifalarni saralash"
        ),
        "technologies": "Python, @dataclass, type hints, Callable, asdict, frozen",
        "deadline_days": 5,
    },
    7: {  # R2 — Analytics dashboard
        "title": "🔁 R2: Server log dashboard",
        "description": (
            "Server log yozuvlarini 3 ta texnika bilan tahlil qiluvchi mini dashboard: "
            "@dataclass, @timed dekorator va **kwargs bilan filterlash."
        ),
        "requirements": (
            "• `@dataclass class LogYozuv` — sana, level, xabar, user_id, meta (default dict)\n"
            "• `@timed` dekorator har funksiya uchun\n"
            "• `filterlash(yozuvlar, **filtrlar)` — istalgan maydon bo'yicha\n"
            "• Counter bilan har level soni\n"
            "• Kunlik agregatsiya\n"
            "• Eng ko'p uchragan top 3 xabar\n"
            "• Dashboard chiroyli formatda chiqadi"
        ),
        "technologies": "Python, @dataclass, decorators, **kwargs, Counter",
        "deadline_days": 6,
    },
    8: {  # L7 — JSON va CSV
        "title": "Ma'lumot konvertor (JSON ↔ CSV)",
        "description": (
            "Foydalanuvchilar ro'yxatini JSON dan CSV ga va aksincha o'tkazuvchi modul. "
            "Maxsus turlar (datetime, list, dataclass) to'g'ri boshqarilsin."
        ),
        "requirements": (
            "• Kamida 10 ta @dataclass instance — `Buyurtma(id, sana, mahsulotlar, summa)`\n"
            "• `json.dump` bilan `ensure_ascii=False, indent=2, default=str`\n"
            "• `csv.DictWriter` bilan `newline=''` va `encoding='utf-8-sig'`\n"
            "• JSON dan o'qib qaytadan dataclass instance'ga aylantirish\n"
            "• CSV dan o'qib filterlash (sana bo'yicha)\n"
            "• List of strings ni CSV uchun `;` bilan birlashtirish va parse qilish\n"
            "• Xato boshqaruvi: fayl yo'qligi, noto'g'ri JSON"
        ),
        "technologies": "Python, json, csv, dataclasses, datetime, encoding",
        "deadline_days": 5,
    },
    9: {  # L8 — HTTP requests
        "title": "Ob-havo monitori (requests bilan)",
        "description": (
            "API'dan ob-havo ma'lumotlarini olib, log qiluvchi va statistika "
            "qiluvchi CLI. Bir necha shahar uchun ketma-ket so'rov."
        ),
        "requirements": (
            "• `requests.get` bilan ob-havo API (wttr.in formatida `?format=j1`)\n"
            "• `timeout=10` har so'rovda\n"
            "• `raise_for_status()` va Try/except (Timeout, HTTPError, RequestException)\n"
            "• Session ishlatib bir nechta shahar uchun ketma-ket\n"
            "• Har shahar uchun temperatura va shamol natijasi\n"
            "• Natijalarni JSON faylga yozish (vaqt belgilari bilan)\n"
            "• Xato uchun retry dekoratori (5-darsdan)"
        ),
        "technologies": "Python, requests, JSON, Session, try/except",
        "deadline_days": 6,
    },
    10: {  # L9 — Regex
        "title": "Log analyzer (regex bilan)",
        "description": (
            "Server log faylidan IP manzillar, status code'lar, URL'lar va "
            "vaqt belgilarini regex bilan ajratuvchi modul."
        ),
        "requirements": (
            "• Kamida 3 ta `re.compile` qilingan pattern\n"
            "• Sana-vaqt belgisi parse qilish (groups bilan)\n"
            "• IPv4 manzil ekstraksiyasi\n"
            "• HTTP metod + URL + status code\n"
            "• `re.sub` bilan maxfiy ma'lumotlarni yashirish (telefon, email)\n"
            "• `re.findall` bilan barcha ERROR satrlarini topish\n"
            "• VERBOSE flag bilan murakkab pattern\n"
            "• Statistika: IP soni, top URL'lar, status taqsimoti"
        ),
        "technologies": "Python, re, groups, findall, sub, VERBOSE",
        "deadline_days": 5,
    },
    11: {  # R3 — News fetcher
        "title": "🔁 R3: Yangiliklar pipeline (HTTP + regex + CSV)",
        "description": (
            "Modul 3 ning 3 ta texnikasi birga: API'dan yangiliklarni olib, "
            "regex bilan tozalab, statistika qilib, CSV ga yozish."
        ),
        "requirements": (
            "• `requests` bilan API'dan ma'lumot (timeout=10, raise_for_status)\n"
            "• `@dataclass class Yangilik` — id, sarlavha, matn, sana, teglar\n"
            "• `re.sub` bilan HTML tegslar va ko'p bo'shliqlarni tozalash\n"
            "• So'zlar sonini hisoblash (`re.findall(r'\\b\\w+\\b', matn)`)\n"
            "• `csv.DictWriter` bilan yozish (`encoding='utf-8-sig'`)\n"
            "• `asdict` bilan JSON ga yozish ham\n"
            "• Statistika: jami yangilik, jami so'z, eng uzun yangilik\n"
            "• Pipeline funksiyalar alohida ajratilgan"
        ),
        "technologies": "Python, requests, re, csv, json, dataclass, pipeline",
        "deadline_days": 7,
    },
    12: {  # L10 — Advanced OOP
        "title": "Kutubxona tizimi (OOP chuqurroq)",
        "description": (
            "Kutubxona tizimini OOP bilan modellashtiruvchi modul: Kitob, "
            "Foydalanuvchi, Kutubxona class'lari va ular orasidagi munosabatlar."
        ),
        "requirements": (
            "• `class Kitob` — sarlavha, muallif, sahifalar (`@property` bilan validatsiya)\n"
            "• `class Foydalanuvchi` — ism, olgan kitoblar (max 3 ta)\n"
            "• `class AVIPUser(Foydalanuvchi)` — meros, max 10 ta kitob (super() bilan)\n"
            "• `class Kutubxona` — `__len__`, `__iter__`, `__contains__`, `__getitem__`\n"
            "• `@property` bilan computed: `mavjud_kitoblar`, `bandilik_foizi`\n"
            "• `__str__` va `__repr__` har class uchun\n"
            "• `__eq__` Kitob uchun (sarlavha + muallif teng bo'lsa)\n"
            "• Xato class'lari (`KitobBand`, `LimitOshib`)\n"
            "• Demo skript natijasi"
        ),
        "technologies": "Python, OOP, super, @property, dunder methods, exceptions",
        "deadline_days": 7,
    },
    13: {  # L11 — CAPSTONE
        "title": "🚀 CAPSTONE: Shaxsiy xarajatlar trekkeri (CLI)",
        "description": (
            "Kursning yakuniy loyihasi: terminalda ishlovchi xarajatlar trekkeri "
            "kursning barcha texnikalarini birga ishlatadi. Real foydalanish uchun mos."
        ),
        "requirements": (
            "• `@dataclass class Xarajat` — id, tavsif, summa, kategoriya, sana, teglar\n"
            "• `class Tracker` — `__len__`, `__iter__`, `__getitem__`, `__repr__`\n"
            "• `@property` — `jami_summa`, `o_rta_summa`, `kategoriya_bo_yicha`\n"
            "• Persistensiya: `json.dump/load` bilan saqlash va yuklash\n"
            "• Regex: tavsif ichidan `#kategoriya` teg ajratish\n"
            "• Comprehension'lar bilan filterlash va agregatsiya\n"
            "• `sorted + lambda` bilan TOP kategoriyalar\n"
            "• `@timed` dekorator hisobot funksiyasida\n"
            "• Type hints har funksiyada\n"
            "• CLI menu — qo'shish, ro'yxat, statistika, kategoriya filtri\n"
            "• Bonus: CSV export, vaqt filtri (oxirgi 7 kun)\n"
            "• Bonus: budjet ogohlantirish kategoriya bo'yicha"
        ),
        "technologies": (
            "Python, dataclasses, @property, decorators, JSON, regex, "
            "comprehensions, lambda, type hints, OOP, CLI"
        ),
        "deadline_days": 14,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list — order, title, refs to content globals above.
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {"order": 0,  "title": "1-Comprehension'lar (list, dict, set)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/3dt4OGnU5sM", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-Generatorlar va yield",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/bD05uGo_sVI", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-Lambda, map, filter, sorted",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/cKlnR-CB3tk", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Sotuvchi statistikasi (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/HGOBQPFzWKo", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-*args, **kwargs va unpacking",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/CqGzdT4WBcg", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-Dekoratorlar",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/FsAPt_9Bf3U", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-Type hints va dataclasses",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/CT2PD-S6BMs", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-Mini analytics dashboard (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/vmEHCJofslg", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-JSON va CSV bilan ishlash",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/9N6a-VLBa2I", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-HTTP so'rovlari (requests)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/tb8gHvYlCFs", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-Regex (re moduli)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/K8L6KVGG-7o", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Yangiliklar yig'uvchi (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/7sCV4qbm38c", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Chuqur OOP: meros, properties, dunder metodlar",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/RSl87lqOXDE", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: Xarajatlar trekkeri (CLI)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/kvO_nHnvPtQ", "exercises": L11_EX, "_ref": "L11"},
]


def _resolve_lessons() -> None:
    """Wire text/code globals into LESSONS rows by their _ref slug."""
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
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

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
