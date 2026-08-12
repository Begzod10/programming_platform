"""Seed "Python: Ilg'or Mavzular" (11 lessons): fills a real gap — the Python
track's highest tier before Django was only "Keyingi Bosqich" (Intermediate),
with no course covering deep Python language internals, mirroring the
existing "JavaScript: Ilg'or Mavzular" (course 67, Advanced) course structure
(6 topics + review + 3 topics + final review).

Usage:
    cd backend
    python -m scripts.seed_python_advanced
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
    "title": "Python: Ilg'or Mavzular",
    "description": (
        "Python: Keyingi Bosqich kursini tugatgan dasturchilar uchun: "
        "dekoratorlar, generator va iteratorlar, context manager'lar, "
        "functools, chuqur type hints, asyncio, thread/process va magic "
        "methods orqali Python tilining ichki mexanizmlarini chuqur "
        "o'rganing."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 4,
    "max_points": 170,
    "category_id": 8,  # Python
    "prerequisite_course_id": 37,  # Python: Keyingi Bosqich
    "is_active": True,
    "is_published": False,  # flip to True once all 11 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Dekoratorlar",
     "scope": "Function decorators, @wraps, decorators with arguments."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Generator va Iterator",
     "scope": "yield, generator expressions, iterator protocol (__iter__/__next__)."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-Context Manager'lar",
     "scope": "with statement, __enter__/__exit__, contextlib.contextmanager."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-functools chuqurroq",
     "scope": "lru_cache, partial, reduce, singledispatch."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Comprehensions chuqurroq",
     "scope": "Nested comprehensions, generator expressions vs list comprehensions, walrus operator."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Type Hints chuqurroq",
     "scope": "typing module: Optional, Union, Generic, Protocol, TypedDict."},
    {"order": 6, "ref": "R1", "status": "done",
     "title": "Review 1: Dekorator, Generator, Context Manager, functools, Type Hints",
     "scope": "Repetition project combining lessons 1-6."},
    {"order": 7, "ref": "L7", "status": "done",
     "title": "7-Asyncio asoslari",
     "scope": "async/await, asyncio.run, asyncio.gather, coroutines vs threads."},
    {"order": 8, "ref": "L8", "status": "done",
     "title": "8-Threading vs Multiprocessing (GIL)",
     "scope": "GIL, threading module, multiprocessing module, when to use which."},
    {"order": 9, "ref": "L9", "status": "done",
     "title": "9-Magic methods chuqurroq",
     "scope": "__eq__, __lt__, __repr__, __len__, dataclasses."},
    {"order": 10, "ref": "R2", "status": "done",
     "title": "Review 2: Ilg'or mavzular yakuniy (CAPSTONE)",
     "scope": "Final capstone combining async, GIL-aware design, and magic methods."},
]


L1_TEXT = """\
<h2>Dekoratorlar — funksiyani "o'rab" yangi xatti-harakat qo'shish</h2>

<pre class="mermaid">
flowchart LR
    ORIG["original_funksiya"] --> DEC["@dekorator"]
    DEC --> WRAP["wrapper(*args, **kwargs)"]
    WRAP -->|oldin qo'shimcha ish| ORIG
    ORIG -->|natija| WRAP
    WRAP -->|keyin qo'shimcha ish| RESULT["yakuniy natija"]
</pre>

<p>Ba'zan funksiyaning <strong>o'zini o'zgartirmasdan</strong>, unga qo'shimcha xatti-harakat (masalan, ishlash vaqtini o'lchash, log yozish) qo'shish kerak bo'ladi. <strong>Dekorator</strong> — funksiyani boshqa funksiya bilan "o'rab", uning atrofiga qo'shimcha kod qo'shish imkonini beruvchi Python mexanizmi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — oddiy dekorator</h4>
<pre><code>def vaqt_olchagich(func):                    # ❗ dekorator — funksiyani argument sifatida oladi
    def wrapper(*args, **kwargs):             # ❗ ichki funksiya — asl funksiyani "o'raydi"
        import time
        boshlanish = time.time()
        natija = func(*args, **kwargs)        # ❗ asl funksiya shu yerda chaqiriladi
        tugash = time.time()
        print(f"{func.__name__} {tugash - boshlanish:.4f} soniyada bajarildi")
        return natija
    return wrapper                             # ❗ wrapper funksiya qaytariladi

@vaqt_olchagich                                # ❗ '@' sintaksisi - hisoblash = vaqt_olchagich(hisoblash)
def hisoblash(n):
    return sum(range(n))

hisoblash(1000000)   # "hisoblash 0.0123 soniyada bajarildi" chiqadi</code></pre>

<h4>BLOKA 2 — @wraps: metama'lumotni saqlash</h4>
<pre><code>from functools import wraps

def vaqt_olchagich(func):
    @wraps(func)                                # ❗ func'ning __name__, __doc__ kabi ma'lumotlarini saqlaydi
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))

print(hisoblash.__name__)   # "hisoblash" (✅ @wraps bilan)
print(hisoblash.__doc__)    # "n gacha bo'lgan sonlar yig'indisini hisoblaydi." (✅)</code></pre>

<h4>BLOKA 3 — parametrli dekorator (dekoratorlar fabrikasi)</h4>
<pre><code>def takrorlash(necha_marta):                  # ❗ tashqi funksiya - parametr qabul qiladi
    def dekorator(func):                       # ❗ haqiqiy dekorator - shu yerda
        @wraps(func)
        def wrapper(*args, **kwargs):
            natija = None
            for _ in range(necha_marta):
                natija = func(*args, **kwargs)
            return natija
        return wrapper
    return dekorator                            # ❗ dekoratorning o'zi qaytariladi

@takrorlash(3)                                  # ❗ takrorlash(3) - dekorator hosil qiladi, keyin uni qo'llaydi
def salomlash():
    print("Salom!")

salomlash()   # "Salom!" 3 marta chiqadi</code></pre>

<h3>🐛 Ataylab xato — @wraps'ni unutish</h3>
<pre><code>def vaqt_olchagich(func):
    def wrapper(*args, **kwargs):    # ❗ @wraps YO'Q!
        return func(*args, **kwargs)
    return wrapper

@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))

print(hisoblash.__name__)   # ❌ "wrapper" (kutilgan "hisoblash" EMAS!)
print(hisoblash.__doc__)    # ❌ None (asl docstring YO'QOLDI!)</code></pre>

<p><strong>Natija:</strong> dekorator asl funksiyani <code>wrapper</code> nomli yangi funksiya bilan <strong>almashtiradi</strong>. <code>@wraps</code> ishlatilmasa, <code>hisoblash.__name__</code> va <code>hisoblash.__doc__</code> kabi metama'lumotlar asl <code>hisoblash</code> funksiyasiniki emas, balki <code>wrapper</code>niki bo'lib qoladi — bu debugging, dokumentatsiya generatorlar va introspection (masalan <code>help()</code>) uchun <strong>chalkashlik</strong> tug'diradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Dekorator nima uchun kerak?</h4>
<p>Dekorator funksiyaning <strong>o'z kodini o'zgartirmasdan</strong>, unga umumiy xatti-harakat (log yozish, vaqt o'lchash, keshlash, ruxsat tekshirish) qo'shish imkonini beradi. Bu kodni takrorlamasdan (DRY) bir xil "qo'shimcha xatti-harakat"ni ko'p funksiyaga qo'llash uchun ishlatiladi.</p>

<h4>2. *args, **kwargs nima uchun wrapper'da kerak?</h4>
<p>Dekorator <strong>istalgan</strong> imzoga ega funksiyani o'rashi kerak — funksiya 0, 1 yoki 10 ta argument qabul qilishi mumkin. <code>*args, **kwargs</code> wrapper'ga <strong>qanday argumentlar kelsa ham</strong>, ularni o'zgarishsiz asl funksiyaga uzatish imkonini beradi.</p>

<h4>3. @wraps nima uchun muhim?</h4>
<p>Python'da funksiya ham bir obyekt, va uning <code>__name__</code>, <code>__doc__</code> kabi metama'lumotlari bor. Dekorator qo'llanilganda, funksiya nomi aslida <code>wrapper</code>ga almashadi. <code>functools.wraps(func)</code> bu metama'lumotlarni asl funksiyadan <code>wrapper</code>ga <strong>nusxalab qo'yadi</strong>, shunda tashqi kod (masalan debugger, IDE) funksiyani hali ham to'g'ri nom bilan "taniydi".</p>

<h4>4. Parametrli dekorator qanday ishlaydi?</h4>
<p><code>@takrorlash(3)</code> yozilganda, avval <code>takrorlash(3)</code> chaqiriladi — bu <strong>haqiqiy dekoratorni</strong> (ya'ni <code>dekorator</code> funksiyasini) qaytaradi, va aynan shu qaytgan dekorator keyin <code>salomlash</code>ga qo'llaniladi. Shuning uchun parametrli dekoratorlar uch qavatli (tashqi funksiya → dekorator → wrapper) tuzilishga ega.</p>

<h4>5. Dekorator qachon chaqiriladi?</h4>
<p>Dekorator (<code>@dekorator</code> qatori) funksiya <strong>e'lon qilinganda</strong>, darhol bir marta ishlaydi (funksiyani <code>wrapper</code> bilan almashtiradi). <code>wrapper</code>ning ichidagi kod esa funksiya <strong>har safar chaqirilganda</strong> ishlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Dekorator — funksiyani o'zgartirmasdan unga qo'shimcha xatti-harakat qo'shish mexanizmi</li>
<li>✅ <code>*args, **kwargs</code> — wrapper istalgan imzoli funksiyani o'rashi uchun zarur</li>
<li>✅ <code>@functools.wraps(func)</code> — <code>__name__</code>/<code>__doc__</code> kabi metama'lumotlarni saqlaydi</li>
<li>✅ Parametrli dekorator — uch qavatli tuzilish: tashqi funksiya → dekorator → wrapper</li>
<li>✅ Dekorator e'lon qilinganda bir marta, wrapper esa har chaqiruvda ishlaydi</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 1: Dekoratorlar
# ════════════════════════════════════════════════════════════════════

from functools import wraps
import time


# ─────────────────────────────────────────────────────────────────────
# 1) Oddiy dekorator
# ─────────────────────────────────────────────────────────────────────

def vaqt_olchagich(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = func(*args, **kwargs)
        tugash = time.time()
        print(f"{func.__name__} {tugash - boshlanish:.4f} soniyada bajarildi")
        return natija
    return wrapper


@vaqt_olchagich
def hisoblash(n):
    '''n gacha bo'lgan sonlar yig'indisini hisoblaydi.'''
    return sum(range(n))


hisoblash(1000000)
print(hisoblash.__name__)
print(hisoblash.__doc__)

# ─────────────────────────────────────────────────────────────────────
# 2) Parametrli dekorator
# ─────────────────────────────────────────────────────────────────────

def takrorlash(necha_marta):
    def dekorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            natija = None
            for _ in range(necha_marta):
                natija = func(*args, **kwargs)
            return natija
        return wrapper
    return dekorator


@takrorlash(3)
def salomlash():
    print("Salom!")


salomlash()

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - @wraps'ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# def vaqt_olchagich_xato(func):
#     def wrapper(*args, **kwargs):    # @wraps YO'Q!
#         return func(*args, **kwargs)
#     return wrapper
#
# @vaqt_olchagich_xato
# def hisoblash_xato(n):
#     \"\"\"n gacha bo'lgan sonlar yig'indisini hisoblaydi.\"\"\"
#     return sum(range(n))
#
# print(hisoblash_xato.__name__)   # ❌ "wrapper", "hisoblash_xato" EMAS!
"""

L1_EX = [
    {
        "title": "Dekorator nima uchun ishlatiladi?",
        "description": "Dekoratorlar asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Funksiyaning kodini butunlay o'zgartirish uchun",
            "Funksiyaning o'z kodini o'zgartirmasdan, unga qo'shimcha xatti-harakat qo'shish uchun",
            "Faqat class'lar bilan ishlash uchun",
            "Xotira sarfini kamaytirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Masalan, vaqt o'lchash yoki log yozishni ko'p funksiyaga qo'shish kerak bo'lsa.",
        "explanation": "Dekorator funksiyaning o'z kodini o'zgartirmasdan, uni boshqa funksiya bilan \"o'rab\", unga umumiy qo'shimcha xatti-harakat (log, vaqt o'lchash, keshlash) qo'shish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "*args, **kwargs nima uchun wrapper'da kerak?",
        "description": "wrapper(*args, **kwargs) yozuvida *args, **kwargs nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat kod chiroyliroq ko'rinishi uchun",
            "Wrapper istalgan sondagi va turdagi argumentga ega funksiyani o'rashi uchun",
            "Xotira tejash uchun",
            "Bu majburiy emas, olib tashlash mumkin",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Dekorator har xil funksiyalarga qo'llanilishi mumkin - ularning imzosi har xil bo'ladi.",
        "explanation": "*args, **kwargs wrapper'ga qanday argumentlar kelsa ham, ularni o'zgarishsiz asl funksiyaga uzatish imkonini beradi, shuning uchun dekorator istalgan imzoli funksiyaga qo'llanilishi mumkin.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "@takrorlash(3) ishlash jarayonini tartiblang",
        "description": "@takrorlash(3) dekoratori salomlash() funksiyasiga qo'llanilganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "takrorlash(3) chaqiriladi - bu dekorator() funksiyasini qaytaradi",
            "Qaytgan dekorator() funksiyasi salomlash'ga qo'llaniladi",
            "salomlash endi wrapper bilan almashtiriladi",
            "salomlash() chaqirilganda, wrapper ichida sikl 3 marta ishga tushadi",
        ],
        "correct_order": [
            "takrorlash(3) chaqiriladi - bu dekorator() funksiyasini qaytaradi",
            "Qaytgan dekorator() funksiyasi salomlash'ga qo'llaniladi",
            "salomlash endi wrapper bilan almashtiriladi",
            "salomlash() chaqirilganda, wrapper ichida sikl 3 marta ishga tushadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Metama'lumotni saqlovchi dekorator",
        "description": "Dekorator ichida asl funksiyaning __name__ va __doc__ kabi metama'lumotlarini saqlash uchun qaysi dekorator (functools'dan) ishlatiladi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "wraps",
        "hint": "functools.___(func) shaklida ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega @wraps'siz __name__ noto'g'ri chiqadi?",
        "description": (
            "@wraps ishlatilmagan dekoratorda, nega "
            "hisoblash.__name__ \"hisoblash\" emas, balki \"wrapper\" "
            "deb chiqadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "@dekorator qo'llanilganda, aslida hisoblash nomli o'zgaruvchi "
            "endi asl hisoblash funksiyasiga emas, balki dekorator "
            "ichida yaratilgan wrapper funksiyasiga ishora qiladi. "
            "Python'da har bir funksiya obyekt bo'lib, o'zining "
            "__name__ metama'lumotiga ega - wrapper funksiyasining "
            "__name__'i esa standart holda \"wrapper\" bo'ladi, chunki "
            "aynan shunday nomlangan. @functools.wraps(func) ishlatilmasa, "
            "hech kim wrapper'ning __name__'ini asl func'ning __name__'iga "
            "almashtirmaydi, shuning uchun tashqaridan hisoblash.__name__ "
            "chaqirilganda \"wrapper\" chiqadi, kutilgan \"hisoblash\" emas."
        ),
        "hint": "@dekorator qo'llanilgandan keyin, hisoblash o'zgaruvchisi aslida qaysi funksiyaga ishora qiladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TEXT = """\
<h2>Generator va Iterator — elementlarni "birma-bir", xotirani tejab ishlab chiqarish</h2>

<pre class="mermaid">
flowchart LR
    LIST["[1,2,3,...1000000] - hammasi XOTIRADA"] --> MEM["Ko'p xotira"]
    GEN["generator: yield 1, yield 2, ..."] --> LAZY["Har safar SO'RALGANDA bittasi hisoblanadi"]
    LAZY --> MEM2["Kam xotira"]
</pre>

<p>Ba'zan katta hajmdagi ma'lumotlar ketma-ketligini <strong>bir vaqtning o'zida xotiraga yuklamasdan</strong>, birma-bir ishlab chiqarish kerak bo'ladi. <strong>Generator</strong> — <code>yield</code> kalit so'zi yordamida shunday "dangasa" (lazy) ketma-ketlik yaratish imkonini beruvchi maxsus funksiya turi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — oddiy generator funksiya</h4>
<pre><code>def sonlar_generatori(n):
    for i in range(n):
        yield i              # ❗ 'return' emas, 'yield' - qiymatni "beradi" va TO'XTAB TURADI

gen = sonlar_generatori(3)    # ❗ funksiya hali ISHGA TUSHMAYDI - generator obyekt yaratiladi
print(next(gen))              # 0 - shu yergacha bajariladi, keyin to'xtaydi
print(next(gen))              # 1 - qolgan joydan davom etadi
print(next(gen))              # 2
# print(next(gen))            # ❌ StopIteration - boshqa element yo'q

for son in sonlar_generatori(3):   # ❗ for sikli StopIteration'ni o'zi avtomatik ushlaydi
    print(son)                      # 0, 1, 2</code></pre>

<h4>BLOKA 2 — generator expression</h4>
<pre><code># List comprehension - HAMMASI darhol xotirada yaratiladi
kvadratlar_royxat = [x**2 for x in range(1000000)]   # ❗ katta massiv - ko'p xotira

# Generator expression - qavs o'rniga () ishlatiladi, elementlar "dangasa" hisoblanadi
kvadratlar_gen = (x**2 for x in range(1000000))      # ❗ deyarli xotira sarflamaydi!

print(sum(kvadratlar_gen))    # ✅ generator'ni to'g'ridan-to'g'ri sum() bilan ishlatish mumkin</code></pre>

<h4>BLOKA 3 — Iterator protokoli (__iter__ / __next__)</h4>
<pre><code># Generator - iteratorning "qulay" shakli. Iteratorni qo'lda ham yasash mumkin:
class Sanagich:
    def __init__(self, chegara):
        self.hozirgi = 0
        self.chegara = chegara

    def __iter__(self):            # ❗ obyektning o'zi "iteratsiya qilinadigan" ekanini bildiradi
        return self

    def __next__(self):            # ❗ har safar keyingi qiymatni qaytaradi
        if self.hozirgi >= self.chegara:
            raise StopIteration     # ❗ tugaganda MAJBURIY shu xatoni ko'tarish kerak
        qiymat = self.hozirgi
        self.hozirgi += 1
        return qiymat

for son in Sanagich(3):
    print(son)   # 0, 1, 2</code></pre>

<h3>🐛 Ataylab xato — generatorni ikkinchi marta ishlatishga urinish</h3>
<pre><code>gen = (x for x in range(3))
print(list(gen))   # [0, 1, 2] - generator "sarflandi"

print(list(gen))   # ❌ [] - BO'SH! Generator faqat BIR MARTA aylanadi</code></pre>

<p><strong>Natija:</strong> generator — bu <strong>bir martalik</strong> ketma-ketlik. Har bir <code>next()</code> chaqiruvi (yoki <code>for</code>/<code>list()</code> orqali to'liq aylanish) generatorning ichki holatini <strong>o'zgartirib qo'yadi</strong> — u qayta boshiga qaytmaydi. Ro'yxatdan (list) farqli, generatorni ikkinchi marta aylanmoqchi bo'lsangiz, uni <strong>qaytadan yaratishingiz</strong> kerak.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. yield va return orasidagi farq</h4>
<p><code>return</code> funksiyani <strong>butunlay tugatadi</strong>. <code>yield</code> esa funksiyaning holatini <strong>saqlab, to'xtab turadi</strong> — keyingi <code>next()</code> chaqirilganda, funksiya aynan to'xtagan joyidan davom etadi. Shuning uchun generator funksiyada bir nechta <code>yield</code> bo'lishi mumkin.</p>

<h4>2. Generator nima uchun xotirani tejaydi?</h4>
<p>List comprehension <strong>barcha</strong> elementlarni darhol hisoblab, xotiraga joylaydi. Generator esa elementlarni <strong>faqat so'ralganda</strong> (bittalab) hisoblaydi va hech qachon to'liq ro'yxatni xotirada saqlamaydi — bu katta yoki cheksiz ketma-ketliklar bilan ishlashda muhim.</p>

<h4>3. Generator expression qanday yoziladi?</h4>
<p>List comprehension kvadrat qavs <code>[...]</code> ishlatadi, generator expression esa oddiy qavs <code>(...)</code> ishlatadi. Sintaksis deyarli bir xil, lekin natija butunlay farqli: biri to'liq ro'yxat, ikkinchisi "dangasa" generator obyekti.</p>

<h4>4. Iterator protokoli (<code>__iter__</code>/<code>__next__</code>) nima?</h4>
<p>Python'da <code>for</code> sikli ishlashi uchun obyekt <strong>iterator protokoli</strong>ga amal qilishi kerak: <code>__iter__()</code> obyektning o'zini qaytaradi, <code>__next__()</code> keyingi qiymatni beradi va tugaganda <code>StopIteration</code> ko'taradi. Generator funksiyalar bu protokolni <strong>avtomatik</strong> amalga oshiradi — <code>yield</code> ishlatilgan funksiya orqa fonda <code>__iter__</code>/<code>__next__</code>ga ega obyekt yaratadi.</p>

<h4>5. Nega generatorni ikkinchi marta ishlatib bo'lmaydi?</h4>
<p>Generator o'zining "qayerda to'xtaganini" ichki holatida saqlaydi. Bir marta oxirigacha aylantirilgandan keyin, uning ichki holati "tugadi" holatida qoladi — uni qayta "boshidan" ishga tushirish imkoni <strong>yo'q</strong>. Qayta ishlatish uchun generator funksiyani (yoki generator expression'ni) <strong>qaytadan chaqirish</strong> kerak, bu yangi generator obyekt yaratadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>yield</code> funksiyani to'xtatib, holatni saqlaydi; <code>return</code> esa uni butunlay tugatadi</li>
<li>✅ Generator elementlarni "dangasa" (lazy) ishlab chiqarib, xotirani tejaydi</li>
<li>✅ Generator expression — <code>(...)</code> orqali yoziladi, list comprehension'ning xotira tejaydigan versiyasi</li>
<li>✅ Iterator protokoli — <code>__iter__</code> + <code>__next__</code> + <code>StopIteration</code></li>
<li>✅ Generator bir martalik — ikkinchi marta ishlatish uchun qayta yaratish kerak</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 2: Generator va Iterator
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Oddiy generator funksiya
# ─────────────────────────────────────────────────────────────────────

def sonlar_generatori(n):
    for i in range(n):
        yield i


gen = sonlar_generatori(3)
print(next(gen))
print(next(gen))
print(next(gen))

for son in sonlar_generatori(3):
    print(son)

# ─────────────────────────────────────────────────────────────────────
# 2) Generator expression
# ─────────────────────────────────────────────────────────────────────

kvadratlar_royxat = [x**2 for x in range(1000000)]
kvadratlar_gen = (x**2 for x in range(1000000))

print(sum(kvadratlar_gen))

# ─────────────────────────────────────────────────────────────────────
# 3) Iterator protokoli
# ─────────────────────────────────────────────────────────────────────


class Sanagich:
    def __init__(self, chegara):
        self.hozirgi = 0
        self.chegara = chegara

    def __iter__(self):
        return self

    def __next__(self):
        if self.hozirgi >= self.chegara:
            raise StopIteration
        qiymat = self.hozirgi
        self.hozirgi += 1
        return qiymat


for son in Sanagich(3):
    print(son)

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - generatorni ikkinchi marta ishlatish (izohda)
# ─────────────────────────────────────────────────────────────────────

# gen_xato = (x for x in range(3))
# print(list(gen_xato))   # [0, 1, 2]
# print(list(gen_xato))   # ❌ [] - BO'SH!
"""

L2_EX = [
    {
        "title": "yield va return orasidagi farq",
        "description": "yield kalit so'zi return'dan asosan nimasi bilan farq qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "yield funksiyani butunlay tugatadi, xuddi return kabi",
            "yield funksiyaning holatini saqlab, to'xtab turadi; keyingi chaqiruvda davom etadi",
            "yield faqat class'lar ichida ishlatiladi",
            "Ular butunlay bir xil, faqat nomi boshqa",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Generator funksiyada bir nechta yield bo'lishi mumkin.",
        "explanation": "return funksiyani butunlay tugatadi, yield esa funksiyaning holatini saqlab to'xtaydi va keyingi next() chaqirilganda o'sha joydan davom etadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Generator nima uchun xotirani tejaydi?",
        "description": "Generator list comprehension'dan farqli, nima uchun xotirani tejaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki generator elementlarni umuman hisoblamaydi",
            "Chunki generator elementlarni faqat so'ralganda, bittalab hisoblaydi, to'liq ro'yxatni xotiraga saqlamaydi",
            "Chunki generator faqat butun sonlar bilan ishlaydi",
            "Xotira farqi yo'q, ikkalasi bir xil",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu \"dangasa\" (lazy) hisoblash deb ataladi.",
        "explanation": "Generator elementlarni faqat so'ralganda (bittalab) hisoblaydi va hech qachon to'liq ro'yxatni xotirada saqlamaydi, list comprehension esa barcha elementlarni darhol xotiraga joylaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Sanagich orqali iteratsiya jarayonini tartiblang",
        "description": "for son in Sanagich(3) sikli ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "for sikli __iter__() metodini chaqiradi",
            "__iter__() obyektning o'zini qaytaradi",
            "Har bir qadamda __next__() chaqiriladi va keyingi qiymat qaytariladi",
            "chegara'ga yetganda __next__() StopIteration ko'taradi, sikl tugaydi",
        ],
        "correct_order": [
            "for sikli __iter__() metodini chaqiradi",
            "__iter__() obyektning o'zini qaytaradi",
            "Har bir qadamda __next__() chaqiriladi va keyingi qiymat qaytariladi",
            "chegara'ga yetganda __next__() StopIteration ko'taradi, sikl tugaydi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Generator expression yozuvi",
        "description": "List comprehension kvadrat qavs ishlatadi. Generator expression esa qanday qavs ishlatadi? (belgini yozing, masalan: ())",
        "exercise_type": "text_input",
        "expected_answer": "()",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega generatorni ikkinchi marta ishlatib bo'lmaydi?",
        "description": (
            "gen = (x for x in range(3)) deb yaratilib, list(gen) bir "
            "marta chaqirilgandan keyin, nega list(gen)ni qayta "
            "chaqirish bo'sh ro'yxat [] qaytaradi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Generator o'z ichida \"qayerda to'xtaganini\" ko'rsatuvchi "
            "ichki holatni saqlaydi, ro'yxat (list) kabi barcha "
            "elementlarni bir joyda saqlamaydi. list(gen) chaqirilganda, "
            "generator __next__() orqali barcha elementlarni bittalab "
            "berib, oxiriga (StopIteration) yetadi va shu holatda "
            "\"tugagan\" deb qoladi. Generatorni \"boshiga qaytarish\" "
            "imkoni yo'q, shuning uchun uni qayta chaqirish endi hech "
            "qanday yangi element bermaydi va bo'sh ro'yxat qaytaradi. "
            "Qayta ishlatish uchun generator expression'ni qaytadan "
            "yaratish kerak."
        ),
        "hint": "Generator o'zining \"qayerda to'xtaganini\" saqlaydimi, yoki har safar \"boshidan\" boshlaydimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>Context Manager'lar — resurslarni xavfsiz ochish va yopish</h2>

<pre class="mermaid">
flowchart LR
    WITH["with ochish(...) as f:"] --> ENTER["__enter__() chaqiriladi"]
    ENTER --> BLOCK["blok kodi ishga tushadi"]
    BLOCK --> EXIT["__exit__() HAR DOIM chaqiriladi"]
    BLOCK -->|xato yuz bersa ham| EXIT
</pre>

<p>Fayl ochish, ma'lumotlar bazasi ulanishi, lock (qulf) kabi <strong>resurslarni</strong> ishlatgandan keyin ularni <strong>albatta yopish</strong> kerak — hatto xato yuz bersa ham. <strong>Context manager</strong> (<code>with</code> operatori) bu jarayonni avtomatlashtiradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — fayl bilan ishlashda with</h4>
<pre><code># with'siz - qo'lda yopish kerak, va xato bo'lsa file yopilmasligi mumkin
f = open("malumot.txt", "w")
f.write("Salom")
f.close()          # ❗ agar write() xato bersa, close() HECH QACHON chaqirilmaydi!

# with bilan - AVTOMATIK yopiladi, xato bo'lsa ham
with open("malumot.txt", "w") as f:    # ❗ __enter__() chaqiriladi, f qaytariladi
    f.write("Salom")                    # ❗ bu yerda xato yuz bersa ham...
# ❗ blok tugagach (yoki xato yuz berganda ham) __exit__() AVTOMATIK chaqiriladi - fayl yopiladi</code></pre>

<h4>BLOKA 2 — o'z context manager'ingizni klass orqali yaratish</h4>
<pre><code>class BazaUlanishi:
    def __enter__(self):                          # ❗ 'with' boshlanganda chaqiriladi
        print("Ulanish ochildi")
        return self                                # ❗ 'as' so'zidan keyingi o'zgaruvchiga beriladi

    def __exit__(self, exc_type, exc_value, traceback):  # ❗ 'with' bloki tugaganda (xato bo'lsa ham) chaqiriladi
        print("Ulanish yopildi")
        return False                                # ❗ False - xatoni "yutib yubormaslik", uni yuqoriga uzatish

with BazaUlanishi() as baza:
    print("Baza bilan ishlash...")
# Natija: "Ulanish ochildi" -> "Baza bilan ishlash..." -> "Ulanish yopildi"</code></pre>

<h4>BLOKA 3 — contextlib.contextmanager: qisqaroq yozuv</h4>
<pre><code>from contextlib import contextmanager

@contextmanager                       # ❗ generator funksiyani context manager'ga aylantiradi
def baza_ulanishi():
    print("Ulanish ochildi")
    yield "baza-obyekti"               # ❗ yield'gacha bo'lgan qism - __enter__, yield'dan keyingi - __exit__
    print("Ulanish yopildi")

with baza_ulanishi() as baza:
    print(f"Ishlatilmoqda: {baza}")
# Natija xuddi klass bilan yozilgani kabi, lekin qisqaroq</code></pre>

<h3>🐛 Ataylab xato — __exit__'ni yozmasdan faqat __enter__ berish</h3>
<pre><code>class YomonManager:
    def __enter__(self):
        print("Ochildi")
        return self
    # __exit__ METODI YO'Q!

with YomonManager() as m:
    print("Ishlatilmoqda")

# ❌ Xato: AttributeError: __exit__
# ('with' operatori HAR IKKALA metodni ham talab qiladi, faqat __enter__ yetarli emas!)</code></pre>

<p><strong>Natija:</strong> <code>with</code> operatori ishlashi uchun obyektda <strong>ikkalasi ham</strong> &mdash; <code>__enter__</code> VA <code>__exit__</code> &mdash; mavjud bo'lishi <strong>shart</strong>. Faqat <code>__enter__</code> yozilib, <code>__exit__</code> unutilsa, Python <code>with</code> blokidan chiqishda <code>__exit__</code>ni chaqirishga urinadi va uni topa olmay <code>AttributeError</code> beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Context manager nima uchun kerak?</h4>
<p>Resurslarni (fayl, tarmoq ulanishi, lock) ishlatgandan keyin <strong>albatta</strong> yopish/tozalash kerak &mdash; hatto ichida xato yuz bersa ham. <code>with</code> operatori bu "har doim yopish" mantig'ini <strong>avtomatik</strong> ta'minlaydi, dasturchi <code>try/finally</code> qo'lda yozishi shart bo'lmaydi.</p>

<h4>2. __enter__ va __exit__ qachon chaqiriladi?</h4>
<p><code>__enter__()</code> — <code>with</code> bloki <strong>boshlanganda</strong> chaqiriladi, uning qaytargan qiymati <code>as</code>'dan keyingi o'zgaruvchiga beriladi. <code>__exit__()</code> — <code>with</code> bloki <strong>tugaganda</strong> chaqiriladi, <strong>hatto ichida xato (exception) yuz bersa ham</strong> — bu kafolatlangan.</p>

<h4>3. __exit__ning 3 argumenti nima uchun kerak?</h4>
<p><code>__exit__(self, exc_type, exc_value, traceback)</code> — agar <code>with</code> blokida xato yuz bersa, bu argumentlar xato haqida ma'lumot beradi (xato turi, qiymati, traceback). Agar xato yuz bermasa, hammasi <code>None</code> bo'ladi. <code>__exit__</code> <code>True</code> qaytarsa, xato "yutib yuboriladi" (bostirilar), <code>False</code> qaytarsa (yoki hech narsa qaytarmasa), xato yuqoriga uzatiladi.</p>

<h4>4. @contextmanager dekoratori nima qiladi?</h4>
<p><code>contextlib.contextmanager</code> oddiy generator funksiyani <strong>to'liq klass yozmasdan</strong> context manager'ga aylantiradi: <code>yield</code>gacha bo'lgan kod <code>__enter__</code> vazifasini, <code>yield</code>dan keyingi kod <code>__exit__</code> vazifasini bajaradi. Bu kichik context manager'lar uchun ancha qisqaroq yozuv.</p>

<h4>5. Nega __exit__siz AttributeError chiqadi?</h4>
<p><code>with</code> operatori Python tomonidan <strong>protokol</strong> sifatida belgilangan — u obyektda <strong>ikkala</strong> metod (<code>__enter__</code> VA <code>__exit__</code>) borligini talab qiladi. Blok tugaganda Python <strong>avtomatik ravishda</strong> <code>__exit__</code>ni chaqirishga harakat qiladi; agar bu metod mavjud bo'lmasa, oddiy Python qoidasi bo'yicha <code>AttributeError</code> ko'tariladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>with</code> operatori resurslarni ochish/yopishni avtomatlashtiradi, xato yuz bersa ham</li>
<li>✅ <code>__enter__</code> — blok boshida, <code>__exit__</code> — blok tugaganda (xato bo'lsa ham) chaqiriladi</li>
<li>✅ <code>__exit__</code>ning argumentlari xato haqida ma'lumot beradi; <code>True</code> qaytarsa xato bostiriladi</li>
<li>✅ <code>@contextlib.contextmanager</code> — generator orqali qisqaroq context manager yaratadi</li>
<li>✅ <code>with</code> uchun ham <code>__enter__</code>, ham <code>__exit__</code> mavjud bo'lishi shart</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 3: Context Manager'lar
# ════════════════════════════════════════════════════════════════════

from contextlib import contextmanager

# ─────────────────────────────────────────────────────────────────────
# 1) Fayl bilan ishlashda with (izohda - misol uchun)
# ─────────────────────────────────────────────────────────────────────

# with open("malumot.txt", "w") as f:
#     f.write("Salom")

# ─────────────────────────────────────────────────────────────────────
# 2) O'z context manager'ini klass orqali yaratish
# ─────────────────────────────────────────────────────────────────────


class BazaUlanishi:
    def __enter__(self):
        print("Ulanish ochildi")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Ulanish yopildi")
        return False


with BazaUlanishi() as baza:
    print("Baza bilan ishlash...")

# ─────────────────────────────────────────────────────────────────────
# 3) contextlib.contextmanager bilan qisqaroq yozuv
# ─────────────────────────────────────────────────────────────────────


@contextmanager
def baza_ulanishi():
    print("Ulanish ochildi")
    yield "baza-obyekti"
    print("Ulanish yopildi")


with baza_ulanishi() as baza:
    print(f"Ishlatilmoqda: {baza}")

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - __exit__siz klass (izohda)
# ─────────────────────────────────────────────────────────────────────

# class YomonManager:
#     def __enter__(self):
#         print("Ochildi")
#         return self
#     # __exit__ METODI YO'Q!
#
# with YomonManager() as m:
#     print("Ishlatilmoqda")
# ❌ AttributeError: __exit__
"""

L3_EX = [
    {
        "title": "with operatori nima uchun ishlatiladi?",
        "description": "with operatori asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodni tezroq ishlashi uchun",
            "Resurslarni (fayl, ulanish) xato yuz bersa ham albatta yopish/tozalashni avtomatlashtirish uchun",
            "Faqat class'lar yaratish uchun",
            "Generatorlarni to'xtatish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu try/finally yozishning oldini oladi.",
        "explanation": "with operatori resurslarni ishlatgandan keyin ularni albatta yopish/tozalashni, hatto ichida xato yuz bersa ham, avtomatik ta'minlaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "__exit__ qachon chaqiriladi?",
        "description": "__exit__ metodi qachon chaqiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat xato yuz bermasa",
            "with bloki tugaganda, hatto ichida xato yuz bersa ham",
            "Faqat dastur to'liq tugaganda",
            "__enter__ chaqirilishidan oldin",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu kafolatlangan tozalash mexanizmi.",
        "explanation": "__exit__ with bloki tugaganda chaqiriladi — bu hatto blok ichida xato (exception) yuz berganda ham kafolatlangan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "with BazaUlanishi() as baza: ishlash jarayonini tartiblang",
        "description": "with BazaUlanishi() as baza bloki ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "__enter__() chaqiriladi, 'Ulanish ochildi' chop etiladi",
            "__enter__() qaytargan qiymat baza o'zgaruvchisiga beriladi",
            "with blokidagi kod (Baza bilan ishlash) bajariladi",
            "__exit__() chaqiriladi, 'Ulanish yopildi' chop etiladi",
        ],
        "correct_order": [
            "__enter__() chaqiriladi, 'Ulanish ochildi' chop etiladi",
            "__enter__() qaytargan qiymat baza o'zgaruvchisiga beriladi",
            "with blokidagi kod (Baza bilan ishlash) bajariladi",
            "__exit__() chaqiriladi, 'Ulanish yopildi' chop etiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Generator orqali context manager yaratuvchi dekorator",
        "description": "contextlib modulidagi, oddiy generator funksiyani context manager'ga aylantiruvchi dekoratorning nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "contextmanager",
        "hint": "@contextlib.___ shaklida ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega __exit__siz AttributeError chiqadi?",
        "description": (
            "YomonManager klassida faqat __enter__ yozilgan, __exit__ "
            "yo'q. with YomonManager() as m bloki tugaganda nega "
            "AttributeError xatosi chiqadi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "with operatori Python tomonidan aniq protokol sifatida "
            "belgilangan — u ishlashi uchun obyektda ikkala metod, ham "
            "__enter__, ham __exit__, mavjud bo'lishi shart. with "
            "bloki tugaganda (yoki xato yuz berganda), Python avtomatik "
            "ravishda o'sha obyektning __exit__ metodini chaqirishga "
            "harakat qiladi, chunki resursni \"tozalash\" aynan shu "
            "metod orqali amalga oshiriladi. YomonManager klassida "
            "__exit__ metodi umuman yozilmagani uchun, Python bu metodni "
            "topa olmaydi va oddiy Python qoidasi bo'yicha "
            "AttributeError xatosini ko'taradi."
        ),
        "hint": "with operatori obyektdan aynan qanday metodlar mavjudligini talab qiladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>functools chuqurroq — funksional dasturlash uchun tayyor vositalar</h2>

<pre class="mermaid">
flowchart LR
    CACHE["@lru_cache"] --> FAST["Qayta hisoblamasdan, keshdan qaytaradi"]
    PARTIAL["partial(func, x)"] --> FIXED["Ba'zi argumentlari OLDINDAN belgilangan yangi funksiya"]
    REDUCE["reduce(func, ro'yxat)"] --> ACC["Ro'yxatni bitta qiymatga 'yig'adi'"]
</pre>

<p><code>functools</code> moduli — funksiyalar bilan ishlashni osonlashtiruvchi tayyor vositalar to'plami. 1-darsda o'zimiz dekorator yozishni o'rgandik; endi Python'ning <strong>tayyor, optimallashtirilgan</strong> dekorator va funksiyalarini ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — @lru_cache: natijalarni keshlash</h4>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=None)              # ❗ hisoblangan natijalarni xotirada saqlab qoladi
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(30)   # ❗ birinchi chaqiruv - sekin (rekursiya ko'p marta hisoblaydi)
fibonacci(30)   # ❗ ikkinchi chaqiruv - DARHOL (keshdan olinadi, qayta hisoblanmaydi)

print(fibonacci.cache_info())   # CacheInfo(hits=1, misses=31, maxsize=None, currsize=31)</code></pre>

<h4>BLOKA 2 — partial: qisman argumentli funksiya yasash</h4>
<pre><code>from functools import partial

def daraja(asos, korsatkich):
    return asos ** korsatkich

kvadrat = partial(daraja, korsatkich=2)     # ❗ korsatkich HAR DOIM 2 bo'ladigan yangi funksiya
kub = partial(daraja, korsatkich=3)          # ❗ korsatkich HAR DOIM 3 bo'ladigan yangi funksiya

print(kvadrat(5))    # daraja(5, korsatkich=2) - 25
print(kub(5))         # daraja(5, korsatkich=3) - 125</code></pre>

<h4>BLOKA 3 — reduce: ro'yxatni bitta qiymatga "yig'ish"</h4>
<pre><code>from functools import reduce

sonlar = [1, 2, 3, 4, 5]

# reduce(funksiya, ro'yxat) - funksiyani ketma-ket, "to'plab boruvchi" tarzda qo'llaydi
kopaytma = reduce(lambda x, y: x * y, sonlar)   # ❗ (((1*2)*3)*4)*5 = 120
print(kopaytma)   # 120

# sum() singari - lekin ixtiyoriy amal bilan ishlaydi
maksimum = reduce(lambda x, y: x if x > y else y, sonlar)
print(maksimum)   # 5</code></pre>

<h3>🐛 Ataylab xato — lru_cache'ni o'zgaruvchan (mutable) argument bilan ishlatish</h3>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=None)
def royxatni_qayta_ishlash(royxat):     # ❗ ro'yxat (list) - mutable, hash qilib bo'lmaydi!
    return sum(royxat)

royxatni_qayta_ishlash([1, 2, 3])
# ❌ TypeError: unhashable type: 'list'
# (lru_cache argumentlarni "kalit" sifatida ishlatadi, ular hash qilinishi SHART)</code></pre>

<p><strong>Natija:</strong> <code>lru_cache</code> har bir <strong>argumentlar kombinatsiyasini</strong> "kalit" sifatida saqlab, natijani shu kalit bilan bog'laydi. Buning uchun argumentlar <strong>hash qilinadigan</strong> (immutable) bo'lishi kerak — <code>list</code> kabi o'zgaruvchan (mutable) turlar hash qilinmaydi, shuning uchun <code>TypeError</code> chiqadi. Yechim: <code>list</code> o'rniga <code>tuple</code> (masalan <code>tuple(royxat)</code>) ishlatish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. lru_cache qachon foydali?</h4>
<p><code>lru_cache</code> bir xil argumentlar bilan <strong>qayta-qayta</strong> chaqiriladigan, "qimmat" (ko'p vaqt oladigan) funksiyalar uchun juda foydali — masalan rekursiv <code>fibonacci</code>. U natijani birinchi marta hisoblab, keyingi bir xil chaqiruvlarda darhol keshdan qaytaradi.</p>

<h4>2. partial nima uchun kerak?</h4>
<p><code>partial</code> mavjud funksiyadan, <strong>ba'zi argumentlari oldindan belgilangan</strong> yangi funksiya yasaydi. Bu funksiyani "moslashtirish" (masalan, umumiy <code>daraja</code> funksiyasidan maxsus <code>kvadrat</code> funksiyasini yasash) uchun ishlatiladi, qaytadan to'liq funksiya yozmasdan.</p>

<h4>3. reduce qanday ishlaydi?</h4>
<p><code>reduce(funksiya, royxat)</code> ro'yxatning birinchi ikkita elementiga funksiyani qo'llaydi, natijani keyingi element bilan yana qo'llaydi, va h.k. — natijada butun ro'yxat <strong>bitta</strong> qiymatga "yig'iladi". <code>sum()</code>, <code>max()</code> kabi funksiyalar aslida <code>reduce</code>ning maxsus holatlari hisoblanadi.</p>

<h4>4. Nega lru_cache argumentlari hash qilinadigan bo'lishi kerak?</h4>
<p><code>lru_cache</code> ichki tomondan natijalarni <strong>dictionary</strong> (lug'at) shaklida saqlaydi, unda argumentlar kombinatsiyasi "kalit" vazifasini bajaradi. Python'da dictionary kaliti <strong>hash qilinadigan</strong> (odatda immutable) bo'lishi shart — <code>list</code> kabi o'zgaruvchan turlar kalit bo'la olmaydi.</p>

<h4>5. functools qachon o'z dekoratoringizni yozishdan afzal?</h4>
<p>1-darsda o'zimiz dekorator yozishni o'rgandik — bu <strong>tushunish</strong> uchun muhim. Lekin real loyihalarda <code>functools</code>dagi tayyor vositalar (masalan <code>lru_cache</code>) <strong>optimallashtirilgan</strong>, sinovdan o'tgan va ko'p chekka holatlarni (masalan thread-safety) hisobga oladi — shuning uchun ular mavjud bo'lganda, ularni qo'lda qayta yozish o'rniga ishlatish tavsiya etiladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>@lru_cache</code> — funksiya natijalarini keshlab, qayta hisoblashning oldini oladi</li>
<li>✅ <code>partial(func, arg=qiymat)</code> — ba'zi argumentlari oldindan belgilangan yangi funksiya yasaydi</li>
<li>✅ <code>reduce(func, royxat)</code> — ro'yxatni ketma-ket qo'llab, bitta qiymatga "yig'adi"</li>
<li>✅ <code>lru_cache</code> argumentlari hash qilinadigan (immutable) bo'lishi shart</li>
<li>✅ Tayyor <code>functools</code> vositalari real loyihalarda qo'lda yozilgan versiyalardan ko'pincha ustunroq</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 4: functools chuqurroq
# ════════════════════════════════════════════════════════════════════

from functools import lru_cache, partial, reduce

# ─────────────────────────────────────────────────────────────────────
# 1) @lru_cache - natijalarni keshlash
# ─────────────────────────────────────────────────────────────────────


@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


fibonacci(30)
fibonacci(30)
print(fibonacci.cache_info())

# ─────────────────────────────────────────────────────────────────────
# 2) partial - qisman argumentli funksiya
# ─────────────────────────────────────────────────────────────────────


def daraja(asos, korsatkich):
    return asos ** korsatkich


kvadrat = partial(daraja, korsatkich=2)
kub = partial(daraja, korsatkich=3)

print(kvadrat(5))
print(kub(5))

# ─────────────────────────────────────────────────────────────────────
# 3) reduce - ro'yxatni bitta qiymatga yig'ish
# ─────────────────────────────────────────────────────────────────────

sonlar = [1, 2, 3, 4, 5]

kopaytma = reduce(lambda x, y: x * y, sonlar)
print(kopaytma)

maksimum = reduce(lambda x, y: x if x > y else y, sonlar)
print(maksimum)

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - lru_cache'ni mutable argument bilan ishlatish (izohda)
# ─────────────────────────────────────────────────────────────────────

# @lru_cache(maxsize=None)
# def royxatni_qayta_ishlash(royxat):
#     return sum(royxat)
#
# royxatni_qayta_ishlash([1, 2, 3])
# ❌ TypeError: unhashable type: 'list'
"""

L4_EX = [
    {
        "title": "lru_cache qachon foydali?",
        "description": "@lru_cache dekoratori qanday funksiyalar uchun asosan foydali?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har safar butunlay boshqa argument bilan chaqiriladigan funksiyalar uchun",
            "Bir xil argumentlar bilan qayta-qayta chaqiriladigan, ko'p vaqt oluvchi funksiyalar uchun",
            "Faqat argumentsiz funksiyalar uchun",
            "Faqat class metodlar uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Rekursiv fibonacci - klassik misol.",
        "explanation": "lru_cache bir xil argumentlar bilan qayta-qayta chaqiriladigan, \"qimmat\" funksiyalar uchun foydali - natijani bir marta hisoblab, keyingi chaqiruvlarda keshdan qaytaradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "partial nima qiladi?",
        "description": "partial(daraja, korsatkich=2) nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "daraja funksiyasini butunlay o'chiradi",
            "korsatkich argumenti har doim 2 bo'ladigan yangi funksiya yaratadi",
            "daraja funksiyasini ikki marta chaqiradi",
            "Xatolikni ushlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu mavjud funksiyadan \"moslashtirilgan\" yangi funksiya yasaydi.",
        "explanation": "partial mavjud funksiyadan, ba'zi argumentlari (bu holda korsatkich=2) oldindan belgilangan yangi funksiya yasaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "reduce(lambda x,y: x*y, [1,2,3,4,5]) hisoblash jarayonini tartiblang",
        "description": "reduce funksiyasi [1,2,3,4,5] ro'yxatini ko'paytirish orqali qanday qadamlarda bitta qiymatga yig'ishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "1 va 2 ko'paytiriladi - natija 2",
            "2 (oldingi natija) va 3 ko'paytiriladi - natija 6",
            "6 va 4 ko'paytiriladi - natija 24",
            "24 va 5 ko'paytiriladi - yakuniy natija 120",
        ],
        "correct_order": [
            "1 va 2 ko'paytiriladi - natija 2",
            "2 (oldingi natija) va 3 ko'paytiriladi - natija 6",
            "6 va 4 ko'paytiriladi - natija 24",
            "24 va 5 ko'paytiriladi - yakuniy natija 120",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "lru_cache statistikasini ko'rish metodi",
        "description": "lru_cache bilan bezatilgan funksiyaning kesh statistikasini (hits, misses) ko'rsatuvchi metodni yozing.",
        "exercise_type": "text_input",
        "expected_answer": "cache_info",
        "hint": "funksiya_nomi.___() shaklida chaqiriladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega lru_cache mutable argument bilan TypeError beradi?",
        "description": (
            "@lru_cache bilan bezatilgan funksiyaga list argument "
            "sifatida berilsa (masalan royxatni_qayta_ishlash([1,2,3])), "
            "nega \"TypeError: unhashable type: 'list'\" xatosi chiqadi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "lru_cache ichki tomondan hisoblangan natijalarni dictionary "
            "(lug'at) shaklida saqlaydi, bu yerda funksiyaga berilgan "
            "argumentlar kombinatsiyasi \"kalit\" vazifasini bajaradi. "
            "Python'da dictionary kaliti sifatida faqat hash qilinadigan "
            "(odatda immutable) qiymatlar ishlatilishi mumkin. list "
            "turi esa mutable (o'zgaruvchan) va hash qilinmaydigan tur "
            "hisoblanadi, shuning uchun uni kalit sifatida ishlatishga "
            "urinilganda Python \"unhashable type: 'list'\" xatosini "
            "beradi. Yechim - list o'rniga tuple(royxat) kabi immutable "
            "turdan foydalanish."
        ),
        "hint": "lru_cache argumentlarni qanday saqlaydi - oddiy ro'yxatdami, yoki dictionary kaliti sifatidami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>Comprehensions chuqurroq — bir qatorda qulay ma'lumot yasash</h2>

<pre class="mermaid">
flowchart LR
    NESTED["ikki qavatli for"] --> FLAT["nested comprehension - bitta qatorda"]
    WALRUS[":= walrus operatori"] --> REUSE["hisoblangan qiymatni QAYTA hisoblamasdan ishlatish"]
</pre>

<p>List/dict/set comprehension'larning asosini avvalgi kurslarda o'rgangansiz. Endi ularning <strong>chuqurroq</strong> imkoniyatlari: ichma-ich (nested) comprehension'lar va Python 3.8'da qo'shilgan <strong>walrus operatori</strong> (<code>:=</code>).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ichma-ich (nested) list comprehension</h4>
<pre><code># Oddiy sikl bilan matritsani "tekislash" (flatten):
matritsa = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
tekis = []
for qator in matritsa:
    for son in qator:
        tekis.append(son)

# Xuddi shu narsa - nested comprehension bilan, bitta qatorda:
tekis_comp = [son for qator in matritsa for son in qator]   # ❗ tashqi sikl BIRINCHI, ichki sikl IKKINCHI
print(tekis_comp)   # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Shart bilan filtrlash ham qo'shish mumkin
juft_sonlar = [son for qator in matritsa for son in qator if son % 2 == 0]
print(juft_sonlar)   # [2, 4, 6, 8]</code></pre>

<h4>BLOKA 2 — dict va set comprehension</h4>
<pre><code>sonlar = [1, 2, 3, 4, 5]

# Dict comprehension - {kalit: qiymat for ...}
kvadratlar_lugat = {son: son**2 for son in sonlar}
print(kvadratlar_lugat)   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Set comprehension - takrorlanuvchi qiymatlarni avtomatik olib tashlaydi
takrorlanuvchi = [1, 2, 2, 3, 3, 3]
noyob_kvadratlar = {son**2 for son in takrorlanuvchi}
print(noyob_kvadratlar)   # {1, 4, 9} - takrorlanmagan</code></pre>

<h4>BLOKA 3 — walrus operatori (:=): hisoblab, saqlab, ishlatish</h4>
<pre><code># := ISHLATILMASA - funksiya IKKI marta chaqiriladi (samarasiz)
natijalar = [uzun_hisoblash(x) for x in range(10) if uzun_hisoblash(x) > 5]

# := BILAN - funksiya faqat BIR marta chaqiriladi, natija saqlanib qayta ishlatiladi
natijalar = [natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5]
# ❗ (natija := uzun_hisoblash(x)) - hisoblaydi VA natijaga saqlaydi, BIR vaqtning o'zida</code></pre>

<h3>🐛 Ataylab xato — nested comprehension'da sikllar tartibini aralashtirib yuborish</h3>
<pre><code>matritsa = [[1, 2, 3], [4, 5, 6]]

# ❌ XATO tartib - "ichki" va "tashqi" sikl joyi almashtirilgan deb o'ylab yozilgan
xato_natija = [son for son in qator for qator in matritsa]
# ❌ NameError: name 'qator' is not defined
# (chunki 'qator' o'zgaruvchisi FAQAT ikkinchi 'for'da e'lon qilinadi,
#  lekin birinchi 'for' unga birinchi bo'lib murojaat qilishga urinadi)</code></pre>

<p><strong>Natija:</strong> nested comprehension'da sikllar <strong>chapdan o'ngga, yozilgan tartibda</strong> bajariladi — xuddi oddiy ichma-ich <code>for</code> sikllaridagi kabi: <strong>birinchi</strong> <code>for</code> — <strong>tashqi</strong> sikl, <strong>ikkinchi</strong> <code>for</code> — <strong>ichki</strong> sikl. Agar tartib noto'g'ri yozilsa (masalan ichki o'zgaruvchi tashqi sikldan oldin ishlatilsa), Python u o'zgaruvchini hali "tanimaganligi" sababli <code>NameError</code> beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nested comprehension'da sikllar tartibi qanday?</h4>
<p>Qoidasi oddiy: nested comprehension'dagi <code>for</code>larning tartibi, ularni <strong>oddiy ichma-ich yozilgan <code>for</code> sikllariga</strong> "yozib chiqqandagi" tartib bilan bir xil. <strong>Birinchi</strong> yozilgan <code>for</code> — <strong>eng tashqi</strong> sikl.</p>

<h4>2. Dict va set comprehension qachon ishlatiladi?</h4>
<p>Dict comprehension (<code>{k: v for ...}</code>) — kalit-qiymat juftliklarini tez yaratish uchun. Set comprehension (<code>{x for ...}</code>) — natijada <strong>takrorlanmaydigan</strong> (unique) elementlar kerak bo'lganda, list comprehension o'rniga ishlatiladi.</p>

<h4>3. Walrus operatori (<code>:=</code>) nima uchun kerak?</h4>
<p><code>:=</code> ifodani <strong>hisoblash bilan bir vaqtda</strong> natijani o'zgaruvchiga <strong>saqlash</strong> imkonini beradi. Bu, ayniqsa comprehension shartlarida, bir xil "qimmat" hisoblashni (masalan funksiya chaqiruvini) <strong>ikki marta</strong> emas, <strong>bir marta</strong> bajarish uchun foydali.</p>

<h4>4. := qanday samaradorlikni oshiradi?</h4>
<p><code>:=</code>siz, agar shart va natija bir xil "qimmat" hisoblashga bog'liq bo'lsa (masalan <code>uzun_hisoblash(x)</code>), bu hisoblash <strong>ikki marta</strong> (bir marta shart uchun, bir marta natija uchun) bajariladi. <code>:=</code> bilan u <strong>bir marta</strong> hisoblanadi va natija ikkalasi uchun ham qayta ishlatiladi.</p>

<h4>5. Nega noto'g'ri tartibda NameError chiqadi?</h4>
<p>Python nested comprehension'ni <strong>chapdan o'ngga</strong>, yozilgan ketma-ketlikda "ochib" ishlaydi. Agar birinchi <code>for</code> ichida ikkinchi <code>for</code>dagi o'zgaruvchiga (masalan <code>qator</code>) murojaat qilinsa, lekin <code>qator</code> hali <strong>e'lon qilinmagan</strong> bo'lsa (chunki u keyingi <code>for</code>da), Python bu nomni <strong>topa olmay</strong> <code>NameError</code> beradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Nested comprehension'da <code>for</code>lar tartibi — oddiy ichma-ich sikllardagi kabi, birinchisi tashqi</li>
<li>✅ Dict comprehension (<code>{k: v for ...}</code>) va set comprehension (<code>{x for ...}</code>) — turli maqsadlar uchun</li>
<li>✅ Walrus operatori (<code>:=</code>) — hisoblash va saqlashni bir vaqtda bajaradi</li>
<li>✅ <code>:=</code> bir xil "qimmat" hisoblashni ikki marta emas, bir marta bajarish imkonini beradi</li>
<li>✅ Nested comprehension'da noto'g'ri tartib <code>NameError</code>ga olib keladi</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 5: Comprehensions chuqurroq
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Ichma-ich (nested) list comprehension
# ─────────────────────────────────────────────────────────────────────

matritsa = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

tekis = []
for qator in matritsa:
    for son in qator:
        tekis.append(son)

tekis_comp = [son for qator in matritsa for son in qator]
print(tekis_comp)

juft_sonlar = [son for qator in matritsa for son in qator if son % 2 == 0]
print(juft_sonlar)

# ─────────────────────────────────────────────────────────────────────
# 2) Dict va set comprehension
# ─────────────────────────────────────────────────────────────────────

sonlar = [1, 2, 3, 4, 5]

kvadratlar_lugat = {son: son**2 for son in sonlar}
print(kvadratlar_lugat)

takrorlanuvchi = [1, 2, 2, 3, 3, 3]
noyob_kvadratlar = {son**2 for son in takrorlanuvchi}
print(noyob_kvadratlar)

# ─────────────────────────────────────────────────────────────────────
# 3) Walrus operatori (izohda - uzun_hisoblash ta'rif berilmagan)
# ─────────────────────────────────────────────────────────────────────

# natijalar = [uzun_hisoblash(x) for x in range(10) if uzun_hisoblash(x) > 5]
# natijalar = [natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - sikllar tartibini aralashtirib yuborish (izohda)
# ─────────────────────────────────────────────────────────────────────

# xato_natija = [son for son in qator for qator in matritsa]
# ❌ NameError: name 'qator' is not defined
"""

L5_EX = [
    {
        "title": "Nested comprehension'da sikllar tartibi",
        "description": "[son for qator in matritsa for son in qator] yozuvida qaysi for tashqi sikl hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkinchi for (son uchun)",
            "Birinchi for (qator uchun)",
            "Ikkalasi ham bir vaqtda ishlaydi",
            "Tartib ahamiyatsiz",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu oddiy ichma-ich yozilgan for sikllariga o'xshaydi.",
        "explanation": "Nested comprehension'da birinchi yozilgan for eng tashqi sikl hisoblanadi, xuddi oddiy ichma-ich yozilgan for sikllaridagi kabi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Set comprehension qachon ishlatiladi?",
        "description": "{son**2 for son in takrorlanuvchi} kabi set comprehension list comprehension'dan qanday farq qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Set comprehension tezroq ishlaydi, boshqa farqi yo'q",
            "Set comprehension natijada takrorlanuvchi qiymatlarni avtomatik olib tashlaydi (noyob elementlar)",
            "Set comprehension faqat sonlar bilan ishlaydi",
            "Ular butunlay bir xil",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "{} bilan yaratilgan to'plam qanday xususiyatga ega?",
        "explanation": "Set comprehension natijada takrorlanmaydigan (unique) elementlarni beradi, chunki set (to'plam) turi takrorlanuvchi qiymatlarni saqlamaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Walrus operatori bilan ishlash jarayonini tartiblang",
        "description": "[natija for x in range(10) if (natija := uzun_hisoblash(x)) > 5] ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "x qiymati range(10)dan olinadi",
            "uzun_hisoblash(x) HISOBLANADI va natija o'zgaruvchisiga SAQLANADI",
            "natija > 5 sharti tekshiriladi",
            "Shart to'g'ri bo'lsa, saqlangan natija (qayta hisoblanmasdan) ro'yxatga qo'shiladi",
        ],
        "correct_order": [
            "x qiymati range(10)dan olinadi",
            "uzun_hisoblash(x) HISOBLANADI va natija o'zgaruvchisiga SAQLANADI",
            "natija > 5 sharti tekshiriladi",
            "Shart to'g'ri bo'lsa, saqlangan natija (qayta hisoblanmasdan) ro'yxatga qo'shiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Walrus operatorining belgisi",
        "description": "Python 3.8'da qo'shilgan, hisoblash bilan bir vaqtda o'zgaruvchiga saqlash imkonini beruvchi operator qanday belgi bilan yoziladi? (belgini yozing)",
        "exercise_type": "text_input",
        "expected_answer": ":=",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega noto'g'ri tartibda NameError chiqadi?",
        "description": (
            "[son for son in qator for qator in matritsa] deb yozilsa "
            "(tartib almashtirilgan holda), nega \"NameError: name "
            "'qator' is not defined\" xatosi chiqadi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Python nested comprehension'ni chapdan o'ngga, xuddi oddiy "
            "ichma-ich yozilgan for sikllaridagi kabi, yozilgan tartibda "
            "\"ochib\" bajaradi. Bu yozuvda birinchi for (for son in "
            "qator) eng tashqi sikl hisoblanadi va u qator degan "
            "o'zgaruvchiga murojaat qiladi, lekin qator o'zgaruvchisi "
            "aslida faqat KEYINGI, ikkinchi for'da (for qator in "
            "matritsa) e'lon qilinadi. Birinchi sikl ishga tushganda "
            "Python hali qator nomini \"tanimaydi\" (u hali aniqlanmagan), "
            "shuning uchun NameError xatosi beradi."
        ),
        "hint": "Nested comprehension qaysi tartibda \"ochiladi\" - yozilgandek ketma-ketlikdami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>Type Hints chuqurroq — typing moduli bilan aniq turlarni belgilash</h2>

<pre class="mermaid">
flowchart LR
    OPT["Optional[str]"] --> NONE["str YOKI None"]
    UNION["Union[int, str]"] --> EITHER["int YOKI str"]
    GENERIC["Stack[T]"] --> ANYTYPE["ixtiyoriy T turi bilan ishlaydigan class"]
    PROTOCOL["Protocol"] --> DUCK["meros olmasdan, faqat 'shakli' mos kelishi"]
</pre>

<p>Oddiy type hints (<code>def f(x: int) -> str</code>) allaqachon tanish. Endi <code>typing</code> moduli orqali <strong>murakkabroq</strong> holatlarni — "yo shu, yo boshqasi" qiymatlar, generic class'lar va "protokol" asosidagi tur tekshiruvini — qanday belgilashni ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Optional va Union</h4>
<pre><code>from typing import Optional, Union

def foydalanuvchi_topish(id: int) -> Optional[str]:   # ❗ Optional[str] = Union[str, None]
    if id == 1:
        return "Olim"
    return None                                          # ❗ None qaytarish RUXSAT ETILGAN

def id_korsatish(id: Union[int, str]) -> str:          # ❗ id YO INT, YO STR bo'lishi mumkin
    return f"ID: {id}"

id_korsatish(101)        # ✅ int
id_korsatish("ABC-101")  # ✅ str</code></pre>

<h4>BLOKA 2 — Generic class (TypeVar)</h4>
<pre><code>from typing import Generic, TypeVar

T = TypeVar('T')                       # ❗ "tur o'zgaruvchisi" - istalgan turni bildirishi mumkin

class Stack(Generic[T]):               # ❗ Stack - IXTIYORIY T turi bilan ishlaydigan generic class
    def __init__(self) -> None:
        self._elementlar: list[T] = []

    def qoshish(self, item: T) -> None:
        self._elementlar.append(item)

    def olish(self) -> T:
        return self._elementlar.pop()

son_stack: Stack[int] = Stack()        # ❗ Stack[int] - faqat int bilan ishlaydigan Stack
son_stack.qoshish(5)
# son_stack.qoshish("matn")             # ❌ type checker (mypy) xato beradi: str emas, int kutilgan</code></pre>

<h4>BLOKA 3 — Protocol: "duck typing" uchun tur tekshiruvi</h4>
<pre><code>from typing import Protocol

class ChizishMumkin(Protocol):          # ❗ Protocol - meros olish SHART EMAS, faqat "shakli" mos kelishi kerak
    def chizish(self) -> str: ...

class Doira:                            # ❗ ChizishMumkin'dan MEROS OLMAYDI!
    def chizish(self) -> str:
        return "○ chizildi"

class Kvadrat:
    def chizish(self) -> str:
        return "□ chizildi"

def shaklni_korsatish(shakl: ChizishMumkin) -> None:   # ❗ har qanday "chizish() -> str" metodli obyekt mos keladi
    print(shakl.chizish())

shaklni_korsatish(Doira())     # ✅ ishlaydi - Doira'da chizish() bor
shaklni_korsatish(Kvadrat())   # ✅ ishlaydi - meros olmasa ham</code></pre>

<h3>🐛 Ataylab xato — Optional'ni None tekshiruvisiz ishlatish</h3>
<pre><code>def foydalanuvchi_topish(id: int) -> Optional[str]:
    if id == 1:
        return "Olim"
    return None

ism = foydalanuvchi_topish(2)
print(ism.upper())    # ❌ AttributeError: 'NoneType' object has no attribute 'upper'
# (type checker BUNI OLDINDAN OGOHLANTIRARDI, lekin runtime'da Python o'zi tekshirmaydi!)</code></pre>

<p><strong>Natija:</strong> <code>Optional[str]</code> funksiya <strong>yo <code>str</code>, yo <code>None</code></strong> qaytarishi mumkinligini <strong>type checker</strong> (masalan <code>mypy</code>) uchun bildiradi. Lekin <strong>Python runtime'ning o'zi</strong> type hints'ni <strong>tekshirmaydi</strong> — ular faqat "hujjatlashtirilgan va'da" va tashqi vositalar (mypy, IDE) uchun signal. Shuning uchun <code>None</code> bo'lishi mumkinligini bilib turib, kod ichida <code>if ism is not None</code> kabi haqiqiy tekshiruv yozish dasturchining <strong>o'z mas'uliyati</strong>.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Optional[str] va Union[str, None] farqi bormi?</h4>
<p>Yo'q — <code>Optional[X]</code> aslida <code>Union[X, None]</code>ning <strong>qisqartmasi</strong>. <code>Optional[str]</code> "bu qiymat <code>str</code> yoki <code>None</code> bo'lishi mumkin" degani.</p>

<h4>2. TypeVar va Generic nima uchun kerak?</h4>
<p><code>TypeVar('T')</code> "tur o'zgaruvchisi" yaratadi — bu <code>T</code> keyinchalik <strong>istalgan</strong> aniq turga (<code>int</code>, <code>str</code>, boshqa class) mos kelishi mumkin. <code>Generic[T]</code> orqali class'ni bu tur o'zgaruvchisi bilan yozib, bitta <code>Stack</code> class'ini <strong>har xil turdagi</strong> ma'lumotlar bilan (<code>Stack[int]</code>, <code>Stack[str]</code>) xavfsiz ishlatish mumkin bo'ladi.</p>

<h4>3. Protocol nima uchun kerak?</h4>
<p><code>Protocol</code> Python'ning "duck typing" falsafasini (<em>"agar u o'rdakdek yursa va o'rdakdek qichqirsa, u o'rdak"</em>) tur tizimi bilan birlashtiradi: klass <code>Protocol</code>dan <strong>meros olishi shart emas</strong> — faqat kerakli metodlarga (masalan <code>chizish() -> str</code>) ega bo'lsa, u shu Protocol turiga <strong>mos</strong> deb hisoblanadi.</p>

<h4>4. Type hints runtime'da tekshiriladimi?</h4>
<p><strong>Yo'q.</strong> Python'ning o'zi (CPython) type hints'ga qarab hech qanday xato bermaydi — ular faqat <code>mypy</code> kabi <strong>alohida</strong> type checker vositalari va IDE'lar uchun. Kod <strong>yozish vaqtida</strong> xatolarni oldindan aniqlash uchun juda foydali, lekin dasturni <strong>ishga tushirishda</strong> hech qanday himoya bermaydi.</p>

<h4>5. Nega Optional bilan ishlashda None tekshiruvi kerak?</h4>
<p><code>Optional[str]</code> funksiya <code>None</code> qaytarishi <strong>mumkinligini</strong> bildiradi, lekin bu ogohlantirish faqat type checker darajasida. Runtime'da <code>None</code>ning <code>.upper()</code> kabi <code>str</code> metodlari <strong>yo'q</strong>, shuning uchun dasturchi <strong>o'zi</strong> <code>if natija is not None:</code> kabi tekshiruv yozib, xatoning oldini olishi kerak.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>Optional[X]</code> — <code>Union[X, None]</code>ning qisqartmasi</li>
<li>✅ <code>Union[A, B]</code> — qiymat A yoki B turida bo'lishi mumkinligini bildiradi</li>
<li>✅ <code>Generic[T]</code> + <code>TypeVar</code> — bitta class'ni har xil tur bilan xavfsiz ishlatish imkonini beradi</li>
<li>✅ <code>Protocol</code> — meros olmasdan, faqat "shakli" mos kelgan obyektlarni tur sifatida tanib olish</li>
<li>✅ Type hints faqat tashqi vositalar (mypy, IDE) uchun — Python runtime'da ularni tekshirmaydi</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 6: Type Hints chuqurroq
# ════════════════════════════════════════════════════════════════════

from typing import Optional, Union, Generic, TypeVar, Protocol

# ─────────────────────────────────────────────────────────────────────
# 1) Optional va Union
# ─────────────────────────────────────────────────────────────────────


def foydalanuvchi_topish(id: int) -> Optional[str]:
    if id == 1:
        return "Olim"
    return None


def id_korsatish(id: Union[int, str]) -> str:
    return f"ID: {id}"


id_korsatish(101)
id_korsatish("ABC-101")

# ─────────────────────────────────────────────────────────────────────
# 2) Generic class (TypeVar)
# ─────────────────────────────────────────────────────────────────────

T = TypeVar('T')


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._elementlar: list = []

    def qoshish(self, item: T) -> None:
        self._elementlar.append(item)

    def olish(self) -> T:
        return self._elementlar.pop()


son_stack: Stack = Stack()
son_stack.qoshish(5)

# ─────────────────────────────────────────────────────────────────────
# 3) Protocol
# ─────────────────────────────────────────────────────────────────────


class ChizishMumkin(Protocol):
    def chizish(self) -> str: ...


class Doira:
    def chizish(self) -> str:
        return "○ chizildi"


class Kvadrat:
    def chizish(self) -> str:
        return "□ chizildi"


def shaklni_korsatish(shakl: ChizishMumkin) -> None:
    print(shakl.chizish())


shaklni_korsatish(Doira())
shaklni_korsatish(Kvadrat())

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - Optional'ni None tekshiruvisiz ishlatish (izohda)
# ─────────────────────────────────────────────────────────────────────

# ism = foydalanuvchi_topish(2)
# print(ism.upper())    # ❌ AttributeError: 'NoneType' object has no attribute 'upper'
"""

L6_EX = [
    {
        "title": "Optional[str] nimani bildiradi?",
        "description": "Optional[str] type hint'i nimani bildiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Qiymat faqat str bo'lishi mumkin",
            "Qiymat str yoki None bo'lishi mumkin",
            "Qiymat ixtiyoriy, uni hech qachon berish shart emas",
            "Qiymat faqat None bo'lishi mumkin",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Union[str, None]ning qisqartmasi.",
        "explanation": "Optional[str] — Union[str, None]ning qisqartmasi, ya'ni qiymat str yoki None bo'lishi mumkinligini bildiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Protocol nima uchun kerak?",
        "description": "typing.Protocol nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Klasslarni meros olishga majburlash uchun",
            "Meros olmasdan, faqat kerakli metodlarga ega bo'lgan obyektlarni bir tur sifatida tanib olish uchun",
            "Faqat funksiyalar uchun ishlatiladi, class'lar uchun emas",
            "Xatolarni runtime'da ushlash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Python'ning \"duck typing\" falsafasiga mos keladi.",
        "explanation": "Protocol klass Protocol'dan meros olmasa ham, faqat kerakli metodlarga (masalan chizish() -> str) ega bo'lsa, uni shu Protocol turiga mos deb hisoblash imkonini beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Stack[int] bilan ishlash jarayonini tartiblang",
        "description": "son_stack: Stack[int] = Stack() yaratilib, undan foydalanish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "TypeVar('T') orqali tur o'zgaruvchisi yaratiladi",
            "class Stack(Generic[T]) - T bilan ishlaydigan generic class e'lon qilinadi",
            "Stack[int] - T o'rniga int qo'yilgan aniq tur hosil qilinadi",
            "son_stack.qoshish(5) - faqat int qiymatlar xavfsiz qo'shiladi",
        ],
        "correct_order": [
            "TypeVar('T') orqali tur o'zgaruvchisi yaratiladi",
            "class Stack(Generic[T]) - T bilan ishlaydigan generic class e'lon qilinadi",
            "Stack[int] - T o'rniga int qo'yilgan aniq tur hosil qilinadi",
            "son_stack.qoshish(5) - faqat int qiymatlar xavfsiz qo'shiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Type hints runtime'da tekshiriladimi?",
        "description": "Python (CPython)ning o'zi kod ishga tushirilganda type hints'ga mos kelmagan qiymatlar uchun avtomatik xato beradimi? (ha/yo'q deb javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "yo'q",
        "hint": "Type hints faqat qanday vositalar uchun ishlaydi?",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Optional bilan ishlashda None tekshiruvi kerak?",
        "description": (
            "foydalanuvchi_topish(2) Optional[str] qaytaradigan "
            "funksiyadan None qaytarsa, va shu natijaga darhol .upper() "
            "chaqirilsa, nega AttributeError xatosi chiqadi, garchi "
            "type hint buni \"kutgan\" bo'lsa ham? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Optional[str] faqat type checker (masalan mypy) va IDE "
            "uchun \"bu funksiya str yoki None qaytarishi mumkin\" degan "
            "signal beradi - bu \"hujjatlashtirilgan va'da\", lekin "
            "Python runtime'ning o'zi (CPython) kod ishga tushganda "
            "buni tekshirmaydi va hech qanday himoya bermaydi. None "
            "obyektida .upper() kabi str metodlari umuman mavjud emas, "
            "shuning uchun agar natija haqiqatan None bo'lib chiqsa va "
            "kod ichida bu holat oldindan tekshirilmagan bo'lsa "
            "(masalan if natija is not None: orqali), dastur runtime'da "
            "AttributeError xatosiga uchraydi."
        ),
        "hint": "Type hints kimlar uchun \"signal\" beradi — Python'ning o'ziga, yoki tashqi vositalarga?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R1_TEXT = """\
<h2>Review 1 — 1-6-darslarni takrorlash: Kutubxona qidiruv tizimi</h2>

<p>1-6 darslarning hammasini birlashtirib, kichik kutubxona qidiruv tizimini yasaymiz: dekorator, generator, context manager, functools va type hints — hammasi birga.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>@lru_cache</code> bilan qidiruv funksiyasini keshlash (4-dars)</li>
<li>Mavjud kitoblarni <strong>generator</strong> orqali birma-bir "ishlab chiqarish" (2-dars)</li>
<li>Kutubxona "faylini" <strong>context manager</strong> orqali xavfsiz ochish/yopish (3-dars)</li>
<li>Qidiruv natijasini <strong>list comprehension</strong> va <code>Optional</code> type hint bilan qaytarish (5, 6-darslar)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Kutubxona context manager</h4>
<p><code>__enter__</code>/<code>__exit__</code> metodlari bilan <code>Kutubxona</code> klassini yarating — <code>__enter__</code> "Kutubxona ochildi" deb chop etadi va kitoblar ro'yxatini qaytaradi, <code>__exit__</code> "Kutubxona yopildi" deb chop etadi (3-darsdagidek).</p>

<h4>Vazifa 2 — kitoblar generatori</h4>
<p>Kitoblar ro'yxatidan faqat <code>mavjud=True</code> bo'lganlarini birma-bir <code>yield</code> qiluvchi generator funksiya yozing (2-darsdagidek).</p>

<h4>Vazifa 3 — qidiruvni keshlash</h4>
<p>Sarlavha bo'yicha qidiruvchi funksiyani <code>@lru_cache</code> bilan bezang, natijani <code>Optional[str]</code> turi bilan belgilang (4, 6-darslardagidek).</p>

<h4>Vazifa 4 — list comprehension bilan filtrlash</h4>
<p>Mualliflar ro'yxatidan faqat noyob (takrorlanmagan) mualliflarni <code>set comprehension</code> orqali oling (5-darsdagidek).</p>

<h3>🐛 Ataylab qiyin: generatorga @lru_cache qo'llash</h3>
<p>Agar generator funksiyaga <code>@lru_cache</code> qo'llasangiz, quyidagi tuzoqqa tushishingiz mumkin:</p>
<pre><code>@lru_cache(maxsize=None)
def mavjud_kitoblar(kitoblar_royxati):     # ❗ generator funksiya + lru_cache
    for kitob in kitoblar_royxati:
        if kitob.mavjud:
            yield kitob.sarlavha

# Birinchi chaqiruv - to'g'ri ishlaydi:
for sarlavha in mavjud_kitoblar(kitoblar):
    print(sarlavha)

# Ikkinchi chaqiruv (BIR XIL argumentlar bilan) - BO'SH natija beradi!
for sarlavha in mavjud_kitoblar(kitoblar):
    print(sarlavha)   # ❌ hech narsa chiqmaydi!</code></pre>
<p><strong>Natija:</strong> <code>lru_cache</code> generator funksiyaga qo'llanilganda, u <strong>generator obyektining o'zini</strong> keshlaydi, uning <strong>qiymatlarini emas</strong>. Birinchi <code>for</code> sikli generatorni <strong>to'liq "sarflab" qo'yadi</strong> (2-darsni eslang — generator bir martalik). Ikkinchi chaqiruvda <code>lru_cache</code> xuddi shu (allaqachon "sarflangan") generator obyektini qaytaradi, shuning uchun ikkinchi <code>for</code> sikli bo'sh natija beradi. <strong>Yechim:</strong> generator funksiyalarga <code>lru_cache</code> qo'llamang — buning o'rniga natijani <code>list()</code>ga aylantirib keshlang, yoki alohida keshlash mexanizmi ishlating.</p>

<h3>Boshlang'ich kod</h3>
<pre><code>from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])   # ❗ namedtuple - hash qilinadigan (lru_cache uchun kerak)

class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        # Vazifa 1: "Kutubxona ochildi" chop eting, self.kitoblar'ni qaytaring
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        # Vazifa 1: "Kutubxona yopildi" chop eting
        pass

def mavjud_kitoblar_generatori(kitoblar):
    # Vazifa 2: faqat mavjud=True kitoblarning sarlavhasini yield qiling
    pass

@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar, sarlavha) -> Optional[str]:
    # Vazifa 3: mos kitobni toping, topilmasa None qaytaring
    pass</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code>from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])

class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        print("Kutubxona ochildi")
        return self.kitoblar

    def __exit__(self, exc_type, exc_value, traceback):
        print("Kutubxona yopildi")
        return False

def mavjud_kitoblar_generatori(kitoblar):
    for kitob in kitoblar:
        if kitob.mavjud:
            yield kitob.sarlavha

@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar: tuple, sarlavha: str) -> Optional[str]:
    for kitob in kitoblar:
        if kitob.sarlavha == sarlavha:
            return kitob.sarlavha
    return None

kitoblar = (
    Kitob("Python asoslari", "Ali", True),
    Kitob("Django darslari", "Vali", False),
    Kitob("Algoritmlar", "Ali", True),
)

with Kutubxona(kitoblar) as royxat:
    for sarlavha in mavjud_kitoblar_generatori(royxat):
        print(sarlavha)

noyob_mualliflar = {kitob.muallif for kitob in kitoblar}
print(noyob_mualliflar)   # {'Ali', 'Vali'}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-6 darslarning hammasi birga: dekorator, generator, context manager, functools, comprehensions, type hints</li>
<li>✅ Context manager resurslarni (kutubxona "ulanishi") xavfsiz ochish/yopish uchun ishlatiladi</li>
<li>✅ <code>lru_cache</code>ni generator funksiyaga qo'llash xavfli — u faqat generator obyektini keshlaydi, qiymatlarni emas</li>
<li>✅ Set comprehension noyob qiymatlarni tez olish uchun qulay</li>
</ul>
"""

R1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVIEW 1: Kutubxona qidiruv tizimi (1-6-darslar)
# ════════════════════════════════════════════════════════════════════

from functools import lru_cache
from typing import Optional
from collections import namedtuple

Kitob = namedtuple("Kitob", ["sarlavha", "muallif", "mavjud"])


class Kutubxona:
    def __init__(self, kitoblar):
        self.kitoblar = kitoblar

    def __enter__(self):
        print("Kutubxona ochildi")
        return self.kitoblar

    def __exit__(self, exc_type, exc_value, traceback):
        print("Kutubxona yopildi")
        return False


def mavjud_kitoblar_generatori(kitoblar):
    for kitob in kitoblar:
        if kitob.mavjud:
            yield kitob.sarlavha


@lru_cache(maxsize=None)
def sarlavha_boyicha_qidirish(kitoblar: tuple, sarlavha: str) -> Optional[str]:
    for kitob in kitoblar:
        if kitob.sarlavha == sarlavha:
            return kitob.sarlavha
    return None


kitoblar = (
    Kitob("Python asoslari", "Ali", True),
    Kitob("Django darslari", "Vali", False),
    Kitob("Algoritmlar", "Ali", True),
)

with Kutubxona(kitoblar) as royxat:
    for sarlavha in mavjud_kitoblar_generatori(royxat):
        print(sarlavha)

noyob_mualliflar = {kitob.muallif for kitob in kitoblar}
print(noyob_mualliflar)

# ─────────────────────────────────────────────────────────────────────
# Ataylab qiyin - lru_cache'ni generatorga qo'llash (izohda)
# ─────────────────────────────────────────────────────────────────────

# @lru_cache(maxsize=None)
# def mavjud_kitoblar_xato(kitoblar_royxati):
#     for kitob in kitoblar_royxati:
#         if kitob.mavjud:
#             yield kitob.sarlavha
# # Ikkinchi chaqiruv BO'SH natija beradi - generator "sarflangan"!
"""

R1_EX = [
    {
        "title": "Kutubxona context manager vazifasi",
        "description": "with Kutubxona(kitoblar) as royxat: bloki ishlaganda, __enter__ nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kitoblarni ma'lumotlar bazasiga saqlaydi",
            "\"Kutubxona ochildi\" deb chop etadi va kitoblar ro'yxatini qaytaradi",
            "Barcha kitoblarni o'chirib tashlaydi",
            "Faqat mavjud kitoblarni sanaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "__enter__ 'with' boshlanganda chaqiriladi.",
        "explanation": "__enter__ metodi \"Kutubxona ochildi\" deb chop etadi va self.kitoblar ro'yxatini qaytaradi, bu qiymat royxat o'zgaruvchisiga beriladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "lru_cache'ni generatorga qo'llash muammosi",
        "description": "Generator funksiyaga @lru_cache qo'llanilganda, ikkinchi bir xil chaqiruv nega bo'sh natija beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "lru_cache generatorlar bilan umuman ishlamaydi, xato beradi",
            "lru_cache generator obyektining o'zini keshlaydi, birinchi to'liq aylanishdan keyin u \"sarflangan\" bo'ladi",
            "Ikkinchi chaqiruvda argumentlar noto'g'ri",
            "Bu Python versiyasiga bog'liq xato",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "2-darsni eslang: generator bir martalik.",
        "explanation": "lru_cache generator funksiyaga qo'llanilganda, u qiymatlarni emas, balki generator obyektining o'zini keshlaydi. Birinchi to'liq aylanishdan keyin generator \"sarflanadi\", va lru_cache xuddi shu sarflangan obyektni qaytaradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Kutubxona loyihasi ishlash jarayonini tartiblang",
        "description": "with Kutubxona(kitoblar) as royxat bloki ichida mavjud_kitoblar_generatori(royxat) ishlatilganda, to'liq jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "__enter__() chaqiriladi, kitoblar ro'yxati royxat'ga beriladi",
            "mavjud_kitoblar_generatori(royxat) generator obyekt yaratadi",
            "for sikli generatorni aylantirib, faqat mavjud=True kitoblarni chiqaradi",
            "with bloki tugagach, __exit__() chaqirilib \"Kutubxona yopildi\" chop etiladi",
        ],
        "correct_order": [
            "__enter__() chaqiriladi, kitoblar ro'yxati royxat'ga beriladi",
            "mavjud_kitoblar_generatori(royxat) generator obyekt yaratadi",
            "for sikli generatorni aylantirib, faqat mavjud=True kitoblarni chiqaradi",
            "with bloki tugagach, __exit__() chaqirilib \"Kutubxona yopildi\" chop etiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega lru_cache'ni generatorga qo'llash tavsiya etilmaydi va nima qilish kerak?",
        "description": (
            "1-6 darslarni birlashtirgan holda, nega @lru_cache'ni "
            "generator funksiyalarga qo'llash xavfli, va bu muammoni "
            "hal qilish uchun nima qilish kerak? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "lru_cache funksiya chaqiruvining NATIJASINI keshlaydi. "
            "Generator funksiya chaqirilganda, uning \"natijasi\" "
            "aslida generator obyektining o'zi (hali hech qanday "
            "qiymat hisoblanmagan holda) bo'ladi — qiymatlar faqat "
            "generator aylantirilganda (masalan for sikli orqali) "
            "birma-bir hisoblanadi. lru_cache aynan shu generator "
            "obyektini keshlab qo'yadi. Birinchi marta generator to'liq "
            "aylantirilgach, u \"sarflanadi\" (2-darsni eslang, "
            "generator bir martalik). Bir xil argumentlar bilan "
            "qayta chaqirilganda, lru_cache xuddi shu (allaqachon "
            "sarflangan) generator obyektini qaytaradi, shuning uchun "
            "ikkinchi aylantirish bo'sh natija beradi. Yechim: "
            "generator funksiyalarga lru_cache qo'llamaslik — buning "
            "o'rniga natijani list()ga aylantirib keshlash yoki umuman "
            "boshqa keshlash usulini qo'llash kerak."
        ),
        "hint": "lru_cache aslida nimani keshlaydi — funksiya QIYMATLARINI, yoki funksiya chaqiruvining natijaviy OBYEKTINI?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L7_TEXT = """\
<h2>Asyncio asoslari — kutish vaqtida boshqa ishni bajarish</h2>

<pre class="mermaid">
flowchart LR
    MAIN["asyncio.run(main())"] --> T1["vazifa1() - tarmoq so'rovi kutmoqda..."]
    MAIN --> T2["vazifa2() - tarmoq so'rovi kutmoqda..."]
    T1 -->|kutish vaqtida| T2
    T2 -->|kutish vaqtida| T1
    T1 --> DONE["ikkalasi deyarli BIR VAQTDA tugaydi"]
</pre>

<p>Ko'p funksiyalar (tarmoq so'rovi, fayl o'qish, ma'lumotlar bazasi so'rovi) <strong>kutish</strong> bilan bog'liq — dastur javobni kutib, hech narsa qilmay turadi. <code>asyncio</code> shu "kutish" vaqtida <strong>boshqa vazifalarni</strong> bajarish imkonini beradi, bitta oqim (thread) ichida.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi async funksiya (coroutine)</h4>
<pre><code>import asyncio

async def salomlash(ism):              # ❗ 'async def' - bu coroutine funksiya
    print(f"{ism} - boshlandi")
    await asyncio.sleep(1)              # ❗ 'await' - kutish, lekin BOSHQA vazifalarga yo'l beradi
    print(f"{ism} - tugadi")

asyncio.run(salomlash("Olim"))          # ❗ asyncio.run() - event loop'ni ishga tushiradi</code></pre>

<h4>BLOKA 2 — asyncio.gather: bir nechta vazifani BIR VAQTDA bajarish</h4>
<pre><code>import time

async def main():
    boshlanish = time.time()

    # Ketma-ket bajarish - 3 soniya vaqt oladi (1+1+1)
    # await salomlash("Olim")
    # await salomlash("Vali")
    # await salomlash("Ali")

    # gather bilan - BARCHASI BIR VAQTDA boshlanadi - atigi 1 soniya!
    await asyncio.gather(
        salomlash("Olim"),
        salomlash("Vali"),
        salomlash("Ali"),
    )

    print(f"Jami vaqt: {time.time() - boshlanish:.2f} soniya")

asyncio.run(main())   # "Jami vaqt: 1.00 soniya" (3.00 emas!)</code></pre>

<h4>BLOKA 3 — coroutine (asyncio) va thread orasidagi farq</h4>
<pre><code># asyncio - BITTA oqim (thread) ichida, "kutish" paytida boshqa vazifaga o'tadi
# Bu I/O-bound ishlar uchun juda samarali: tarmoq so'rovi, fayl/baza operatsiyalari
# (chunki bu vaqtda protsessor "bo'sh" turadi, shuni boshqa vazifaga berish mumkin)

# threading - HAQIQIY ko'p oqim, protsessor darajasida parallel (lekin Python'da GIL tufayli
# CPU-bound ishlarda haqiqiy parallellik yo'q - buni 8-darsda batafsil ko'ramiz)

# Qisqacha qoida:
# I/O kutish ko'p bo'lsa (tarmoq, fayl)  -> asyncio
# CPU hisoblash ko'p bo'lsa               -> multiprocessing (8-dars)</code></pre>

<h3>🐛 Ataylab xato — await'ni unutib, coroutine'ni to'g'ridan-to'g'ri chaqirish</h3>
<pre><code>async def salomlash(ism):
    await asyncio.sleep(1)
    return f"Salom, {ism}!"

async def main():
    natija = salomlash("Olim")   # ❗ 'await' YO'Q!
    print(natija)                  # ❌ "<coroutine object salomlash at 0x...>"
    # Coroutine HECH QACHON ishga tushmadi - faqat "reja" yaratildi!

asyncio.run(main())</code></pre>

<p><strong>Natija:</strong> <code>async def</code> bilan e'lon qilingan funksiyani chaqirish uni <strong>darhol ishga tushirmaydi</strong> &mdash; u faqat <strong>coroutine obyekt</strong> ("bajarilishi kerak bo'lgan reja") yaratadi. Bu rejani haqiqatan <strong>bajarish</strong> uchun uni <code>await</code> qilish yoki <code>asyncio.run()</code>/<code>asyncio.gather()</code> orqali event loop'ga topshirish <strong>shart</strong>. <code>await</code>siz, coroutine hech qachon ishlamaydi va print orqali faqat "coroutine object" degan matn chiqadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. async/await nima?</h4>
<p><code>async def</code> — funksiyani <strong>coroutine</strong> (kutish mumkin bo'lgan funksiya) qilib belgilaydi. <code>await</code> — coroutine ichida, boshqa coroutine (yoki kutish mumkin narsa)ni "kutish" nuqtasini belgilaydi — shu nuqtada Python boshqa vazifalarga o'tishi mumkin.</p>

<h4>2. asyncio.gather() nima uchun kerak?</h4>
<p>Bir nechta coroutine'ni <strong>ketma-ket</strong> <code>await</code> qilish ularni birma-bir, navbat bilan bajaradi (jami vaqt — barchasining yig'indisi). <code>asyncio.gather()</code> ularni <strong>bir vaqtda</strong> boshlab, "kutish" vaqtlarini bir-biriga qo'shmasdan, deyarli parallel bajaradi.</p>

<h4>3. asyncio qachon foydali (I/O-bound)?</h4>
<p><code>asyncio</code> ayniqsa <strong>I/O-bound</strong> vazifalar uchun foydali — bunda dastur ko'p vaqtini protsessor ishlashiga emas, balki <strong>tashqi javobni kutishga</strong> (tarmoq, fayl, baza) sarflaydi. Kutish paytida protsessor "bo'sh" turadi, va <code>asyncio</code> shu vaqtdan foydalanib boshqa vazifani bajaradi.</p>

<h4>4. asyncio va threading orasidagi farq</h4>
<p><code>asyncio</code> <strong>bitta</strong> oqim (thread) ichida ishlaydi, faqat "kutish" nuqtalarida vazifalar orasida almashadi. <code>threading</code> esa <strong>bir nechta</strong> haqiqiy oqim yaratadi. Ammo Python'da GIL (Global Interpreter Lock) tufayli threading CPU-bound (hisoblash ko'p) ishlarda haqiqiy parallellik bermaydi — bu 8-darsda batafsil ko'riladi.</p>

<h4>5. Nega await'siz coroutine ishlamaydi?</h4>
<p><code>async def</code> funksiyasini chaqirish faqat <strong>coroutine obyekt</strong> yaratadi — bu "bajarilishi kerak bo'lgan reja"ning o'zi, hali <strong>bajarilmagan</strong>. Bu rejani <strong>haqiqatan ishga tushirish</strong> uchun uni <code>await</code> qilish (yoki <code>asyncio.run()</code>/<code>gather()</code>ga berish) shart — bu Python'ga "endi shu rejani bajar" deb aytishga o'xshaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>async def</code> — coroutine funksiya yaratadi, <code>await</code> — kutish nuqtasini belgilaydi</li>
<li>✅ <code>asyncio.run()</code> — event loop'ni ishga tushirib, coroutine'ni bajaradi</li>
<li>✅ <code>asyncio.gather()</code> — bir nechta coroutine'ni bir vaqtda (parallel) bajaradi</li>
<li>✅ asyncio I/O-bound (kutish ko'p) vazifalar uchun, multiprocessing CPU-bound vazifalar uchun mos</li>
<li>✅ <code>await</code>siz chaqirilgan coroutine hech qachon ishlamaydi, faqat obyekt yaratiladi</li>
</ul>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 7: Asyncio asoslari
# ════════════════════════════════════════════════════════════════════

import asyncio
import time

# ─────────────────────────────────────────────────────────────────────
# 1) Birinchi async funksiya (coroutine)
# ─────────────────────────────────────────────────────────────────────


async def salomlash(ism):
    print(f"{ism} - boshlandi")
    await asyncio.sleep(1)
    print(f"{ism} - tugadi")


asyncio.run(salomlash("Olim"))

# ─────────────────────────────────────────────────────────────────────
# 2) asyncio.gather - bir nechta vazifani bir vaqtda bajarish
# ─────────────────────────────────────────────────────────────────────


async def main():
    boshlanish = time.time()

    await asyncio.gather(
        salomlash("Olim"),
        salomlash("Vali"),
        salomlash("Ali"),
    )

    print(f"Jami vaqt: {time.time() - boshlanish:.2f} soniya")


asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - await'ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────


async def salomlash2(ism):
    await asyncio.sleep(1)
    return f"Salom, {ism}!"


# async def main_xato():
#     natija = salomlash2("Olim")   # await YO'Q!
#     print(natija)                  # ❌ "<coroutine object salomlash2 at 0x...>"
#
# asyncio.run(main_xato())
"""

L7_EX = [
    {
        "title": "async/await nima uchun ishlatiladi?",
        "description": "async/await asosan qanday holatlar uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat matematik hisoblashlarni tezlashtirish uchun",
            "Kutish (I/O) bilan bog'liq vazifalarda, kutish vaqtida boshqa ishni bajarish uchun",
            "Faqat class'lar bilan ishlash uchun",
            "Xotira sarfini kamaytirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Tarmoq so'rovi yoki fayl o'qish - dastur ko'pincha kutib turadi.",
        "explanation": "async/await kutish (I/O) bilan bog'liq vazifalarda (tarmoq so'rovi, fayl o'qish) kutish vaqtida boshqa vazifalarni bajarish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "asyncio.gather() nima qiladi?",
        "description": "asyncio.gather(vazifa1(), vazifa2(), vazifa3()) nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Vazifalarni birma-bir, ketma-ket bajaradi",
            "Barcha vazifalarni bir vaqtda boshlab, deyarli parallel bajaradi",
            "Faqat birinchi vazifani bajaradi",
            "Vazifalarni butunlay bekor qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu ketma-ket await qilishdan tezroq.",
        "explanation": "asyncio.gather() barcha berilgan coroutine'larni bir vaqtda boshlab, ularning \"kutish\" vaqtlarini qo'shmasdan, deyarli parallel bajaradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "asyncio.gather bilan ishlash jarayonini tartiblang",
        "description": "await asyncio.gather(salomlash('Olim'), salomlash('Vali')) ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Ikkala coroutine (Olim va Vali uchun) bir vaqtda boshlanadi",
            "Har biri 'boshlandi' deb chop etadi, keyin await asyncio.sleep(1) orqali kutishga o'tadi",
            "Kutish paytida ikkalasi bir-biriga xalaqit bermay, navbat bilan ishlaydi",
            "Ikkalasi deyarli bir vaqtda tugaydi - jami atigi 1 soniya",
        ],
        "correct_order": [
            "Ikkala coroutine (Olim va Vali uchun) bir vaqtda boshlanadi",
            "Har biri 'boshlandi' deb chop etadi, keyin await asyncio.sleep(1) orqali kutishga o'tadi",
            "Kutish paytida ikkalasi bir-biriga xalaqit bermay, navbat bilan ishlaydi",
            "Ikkalasi deyarli bir vaqtda tugaydi - jami atigi 1 soniya",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Event loop'ni ishga tushiruvchi funksiya",
        "description": "asyncio'da eng tashqi coroutine'ni ishga tushirish uchun ishlatiladigan funksiyani yozing (masalan: asyncio.___(main())).",
        "exercise_type": "text_input",
        "expected_answer": "run",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega await'siz coroutine ishlamaydi?",
        "description": (
            "natija = salomlash2(\"Olim\") deb yozilib (await'siz), keyin "
            "print(natija) chaqirilsa, nega funksiyaning o'zi bajarilmay, "
            "faqat \"<coroutine object ...>\" degan matn chiqadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "async def bilan e'lon qilingan funksiyani chaqirish uni "
            "darhol ishga tushirmaydi — bu faqat \"bajarilishi kerak "
            "bo'lgan reja\"ni ifodalovchi coroutine obyektini yaratadi, "
            "hali hech qanday kod bajarilmagan bo'ladi. Bu rejani "
            "haqiqatan bajarish uchun uni await qilish yoki "
            "asyncio.run()/gather() orqali event loop'ga topshirish "
            "shart. await yozilmagani uchun Python coroutine'ni hech "
            "qachon ishga tushirmaydi, shuning uchun print(natija) "
            "chaqirilganda funksiya natijasi emas, balki hali "
            "bajarilmagan coroutine obyektining o'zi (\"<coroutine "
            "object ...>\") chop etiladi."
        ),
        "hint": "async funksiyani chaqirish uni darhol ISHGA TUSHIRADIMI, yoki faqat \"reja\" yaratadimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L8_TEXT = """\
<h2>Threading vs Multiprocessing — GIL nima va qachon nima ishlatiladi</h2>

<pre class="mermaid">
flowchart LR
    GIL["GIL - bir vaqtda faqat 1 ta thread Python bytecode bajaradi"] --> CPU["CPU-bound: threading YORDAM BERMAYDI"]
    GIL --> IO["I/O-bound: threading YORDAM BERADI (kutish paytida GIL bo'shatiladi)"]
    MP["multiprocessing - HAR BIR protsess o'zining GIL'iga ega"] --> CPUFAST["CPU-bound: haqiqiy parallellik"]
</pre>

<p>7-darsda <code>asyncio</code>ni ko'rdik. Endi Python'ning eng ko'p chalkashtiriladigan mavzusi — <strong>GIL (Global Interpreter Lock)</strong> — va u <code>threading</code> hamda <code>multiprocessing</code>ga qanday ta'sir qilishini tushunamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — GIL nima?</h4>
<pre><code># GIL (Global Interpreter Lock) - CPython'da bir vaqtning o'zida
# FAQAT BITTA thread Python bytecode'ni bajarishini ta'minlovchi "qulf"

# Bu shuni anglatadi: threading bilan "parallel" ishlayotgandek ko'ringan
# kod ham, aslida protsessor darajasida HAQIQIY parallel EMAS -
# threadlar navbat bilan, juda tez almashib ishlaydi</code></pre>

<h4>BLOKA 2 — threading: CPU-bound ishda foyda YO'Q</h4>
<pre><code>import threading
import time

def hisoblash():
    natija = 0
    for i in range(50_000_000):     # ❗ CPU-bound - faqat hisoblash, kutish yo'q
        natija += i

boshlanish = time.time()
t1 = threading.Thread(target=hisoblash)
t2 = threading.Thread(target=hisoblash)
t1.start(); t2.start()
t1.join(); t2.join()
print(f"2 thread bilan: {time.time() - boshlanish:.2f}s")
# ❗ Natija BITTA thread bilan bajarilgandan TEZROQ EMAS - GIL tufayli!</code></pre>

<h4>BLOKA 3 — multiprocessing: CPU-bound ishda haqiqiy tezlik</h4>
<pre><code>from multiprocessing import Process
import time

def hisoblash():
    natija = 0
    for i in range(50_000_000):
        natija += i

if __name__ == "__main__":
    boshlanish = time.time()
    p1 = Process(target=hisoblash)      # ❗ Process - alohida, o'z GIL'iga ega PROTSESS yaratadi
    p2 = Process(target=hisoblash)
    p1.start(); p2.start()
    p1.join(); p2.join()
    print(f"2 protsess bilan: {time.time() - boshlanish:.2f}s")
    # ✅ Bu safar HAQIQIY tezlashish - har bir protsess mustaqil GIL'ga ega!</code></pre>

<h3>🐛 Ataylab xato — CPU-bound vazifa uchun threading tanlash</h3>
<pre><code># Rasm qayta ishlash (ko'p hisoblash talab qiladi) - CPU-bound vazifa
import threading

def rasmni_qayta_ishlash(rasm):
    # ... ko'p CPU hisoblash (piksellarni qayta ishlash) ...
    pass

threadlar = [threading.Thread(target=rasmni_qayta_ishlash, args=(r,)) for r in rasmlar]
# ❌ Bu YORDAM BERMAYDI! GIL tufayli, bir vaqtda faqat bitta thread haqiqatan ishlaydi
# Kod "parallel ishlayotgandek" ko'rinadi, lekin tezlik deyarli bitta thread bilan bir xil</code></pre>

<p><strong>Natija:</strong> rasmni qayta ishlash <strong>CPU-bound</strong> vazifa (ko'p hisoblash, kam kutish). GIL sababli, <code>threading</code> bilan bir nechta thread yaratilsa ham, ular <strong>bir vaqtda</strong> Python bytecode'ni bajara olmaydi — protsessor darajasida haqiqiy parallellik <strong>yo'q</strong>. To'g'ri yechim — <code>multiprocessing</code>, chunki har bir protsess o'zining mustaqil GIL'iga ega va haqiqatan parallel protsessor yadrolarida ishlaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. GIL nima?</h4>
<p><strong>GIL (Global Interpreter Lock)</strong> — CPython'ning ichki mexanizmi bo'lib, bir vaqtning o'zida <strong>faqat bitta</strong> thread Python bytecode'ini bajarishini ta'minlaydi. Bu xotira boshqaruvini soddalashtirish uchun qilingan, lekin natijada Python threading'i CPU-bound ishlarda haqiqiy parallellik bermaydi.</p>

<h4>2. Nega threading I/O-bound uchun ishlaydi, lekin CPU-bound uchun yo'q?</h4>
<p>I/O kutish paytida (masalan tarmoq javobini kutish), thread GIL'ni <strong>bo'shatadi</strong> — shu payt boshqa thread ishlashi mumkin. Lekin CPU-bound hisoblashda thread <strong>doimiy</strong> GIL'ni band qiladi, boshqa thread'ga deyarli imkoniyat qolmaydi — shuning uchun 7-darsdagi <code>asyncio</code> ham, <code>threading</code> ham CPU-bound ishlarni tezlashtirmaydi.</p>

<h4>3. multiprocessing nima uchun haqiqiy tezlashtiradi?</h4>
<p><code>multiprocessing</code> har bir vazifa uchun <strong>alohida Python protsessi</strong> yaratadi, va har bir protsessning <strong>o'z GIL'i</strong> bor. Shuning uchun protsesslar haqiqatan protsessorning turli yadrolarida <strong>parallel</strong> ishlaydi — bu CPU-bound vazifalar uchun haqiqiy tezlashish beradi.</p>

<h4>4. Qachon nima ishlatiladi (qisqa qoida)?</h4>
<p><strong>I/O-bound</strong> (tarmoq, fayl, baza — ko'p kutish): <code>asyncio</code> (7-dars) yoki <code>threading</code>. <strong>CPU-bound</strong> (ko'p hisoblash, rasm/video qayta ishlash, murakkab algoritmlar): <code>multiprocessing</code>. Noto'g'ri vositani tanlash — kod "ishlaydi", lekin kutilgan tezlashishni bermaydi.</p>

<h4>5. Nega threading CPU-bound vazifada yordam bermaydi?</h4>
<p>GIL bir vaqtning o'zida faqat bitta thread'ga Python kodini bajarish huquqini beradi. CPU-bound vazifada thread'lar deyarli <strong>hech qachon</strong> kutishga o'tmaydi (GIL'ni bo'shatmaydi), shuning uchun ular navbat bilan, ketma-ket ishlaydi — bir nechta thread yaratish qo'shimcha overhead (xarajat) qo'shadi, lekin haqiqiy tezlik bermaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ GIL — bir vaqtda faqat bitta thread Python bytecode bajarishini ta'minlaydi</li>
<li>✅ threading I/O-bound ishlarda foydali (GIL kutish paytida bo'shaydi)</li>
<li>✅ threading CPU-bound ishlarda yordam bermaydi (GIL doim band)</li>
<li>✅ multiprocessing har bir protsessga alohida GIL beradi — CPU-bound uchun haqiqiy parallellik</li>
<li>✅ Qoida: I/O-bound → asyncio/threading, CPU-bound → multiprocessing</li>
</ul>
"""

L8_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 8: Threading vs Multiprocessing (GIL)
# ════════════════════════════════════════════════════════════════════

import threading
import time
from multiprocessing import Process

# ─────────────────────────────────────────────────────────────────────
# 1) threading - CPU-bound ishda foyda yo'q
# ─────────────────────────────────────────────────────────────────────


def hisoblash():
    natija = 0
    for i in range(50_000_000):
        natija += i


def threading_sinov():
    boshlanish = time.time()
    t1 = threading.Thread(target=hisoblash)
    t2 = threading.Thread(target=hisoblash)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"2 thread bilan: {time.time() - boshlanish:.2f}s")

# ─────────────────────────────────────────────────────────────────────
# 2) multiprocessing - CPU-bound ishda haqiqiy tezlik
# ─────────────────────────────────────────────────────────────────────


def multiprocessing_sinov():
    boshlanish = time.time()
    p1 = Process(target=hisoblash)
    p2 = Process(target=hisoblash)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"2 protsess bilan: {time.time() - boshlanish:.2f}s")


if __name__ == "__main__":
    threading_sinov()
    multiprocessing_sinov()

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - CPU-bound vazifa uchun threading (izohda)
# ─────────────────────────────────────────────────────────────────────

# def rasmni_qayta_ishlash(rasm):
#     pass  # ko'p CPU hisoblash
#
# threadlar = [threading.Thread(target=rasmni_qayta_ishlash, args=(r,)) for r in rasmlar]
# ❌ GIL tufayli bu yordam bermaydi!
"""

L8_EX = [
    {
        "title": "GIL nima?",
        "description": "GIL (Global Interpreter Lock) nimani ta'minlaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir vaqtda faqat bitta thread Python bytecode'ini bajarishini",
            "Bir vaqtda cheksiz thread ishlashini",
            "Xotirani avtomatik tozalashni",
            "Faqat multiprocessing modulida ishlaydigan cheklovni",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bu CPython'ning ichki \"qulfi\".",
        "explanation": "GIL bir vaqtning o'zida faqat bitta thread Python bytecode'ini bajarishini ta'minlaydigan CPython'ning ichki mexanizmi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "threading qachon foydali?",
        "description": "threading moduli qanday vazifalar uchun foydali?",
        "exercise_type": "multiple_choice",
        "options": [
            "CPU-bound (ko'p hisoblash) vazifalar uchun",
            "I/O-bound (tarmoq, fayl - ko'p kutish) vazifalar uchun",
            "Faqat matematik amallar uchun",
            "Hech qanday vaziyatda foydali emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Kutish paytida GIL bo'shaydi.",
        "explanation": "threading I/O-bound vazifalar uchun foydali, chunki kutish paytida thread GIL'ni bo'shatadi va boshqa thread ishlashi mumkin bo'ladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CPU-bound vazifada multiprocessing tezligini tartiblang",
        "description": "Ikkita Process orqali CPU-bound hisoblash bajarilganda, nega bu haqiqatan tezroq bo'lishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Process(target=hisoblash) chaqirilib, alohida Python protsessi yaratiladi",
            "Har bir protsess o'zining MUSTAQIL GIL'iga ega bo'ladi",
            "Ikkala protsess protsessorning turli yadrolarida HAQIQATAN parallel ishlaydi",
            "Natijada 2 protsess bilan umumiy vaqt sezilarli kamayadi",
        ],
        "correct_order": [
            "Process(target=hisoblash) chaqirilib, alohida Python protsessi yaratiladi",
            "Har bir protsess o'zining MUSTAQIL GIL'iga ega bo'ladi",
            "Ikkala protsess protsessorning turli yadrolarida HAQIQATAN parallel ishlaydi",
            "Natijada 2 protsess bilan umumiy vaqt sezilarli kamayadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CPU-bound vazifa uchun mos modul",
        "description": "CPU-bound (ko'p hisoblash talab qiluvchi) vazifalarda haqiqiy parallellik olish uchun qaysi modul ishlatiladi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "multiprocessing",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega threading CPU-bound vazifada yordam bermaydi?",
        "description": (
            "hisoblash() funksiyasi (ko'p CPU ishlatadigan, kutishsiz "
            "funksiya) 2 ta threading.Thread orqali bajarilsa, nega "
            "bitta thread bilan bajarilgandan sezilarli tezroq "
            "bo'lmaydi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "GIL bir vaqtning o'zida faqat bitta thread'ga Python "
            "bytecode'ini bajarish huquqini beradi. hisoblash() "
            "funksiyasida hech qanday kutish (I/O) yo'q — u faqat "
            "protsessorni band qiladigan hisoblashdan iborat, shuning "
            "uchun thread hech qachon GIL'ni \"bo'shatishga\" imkoniyat "
            "topa olmaydi. Natijada ikkita thread yaratilgan bo'lsa ham, "
            "ular haqiqatan bir vaqtda emas, balki GIL orqali navbat "
            "bilan, ketma-ket bajariladi — bu esa qo'shimcha thread "
            "yaratish xarajatini (overhead) qo'shadi, lekin haqiqiy "
            "tezlik bermaydi."
        ),
        "hint": "hisoblash() funksiyasida GIL'ni \"bo'shatadigan\" biror kutish nuqtasi bormi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L9_TEXT = """\
<h2>Magic methods chuqurroq — obyektlaringizga Python xatti-harakatini qo'shish</h2>

<pre class="mermaid">
flowchart LR
    EQ["__eq__"] --> COMPARE["== operatori qanday ishlashini belgilaydi"]
    REPR["__repr__"] --> DEBUG["print()/debug'da qanday ko'rinishini belgilaydi"]
    DATACLASS["@dataclass"] --> AUTO["__init__, __repr__, __eq__ AVTOMATIK yaratiladi"]
</pre>

<p>1-darsda <code>__str__</code>/<code>__doc__</code>ni, 3-darsda <code>__enter__</code>/<code>__exit__</code>ni ko'rdik. Bular — <strong>magic methods</strong> (yoki "dunder methods") deb ataladigan katta oilaning a'zolari. Endi <code>==</code>, <code>&lt;</code>, <code>len()</code> kabi standart operatorlarni <strong>o'z klassingiz</strong> uchun qanday belgilashni ko'ramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — __eq__ va __repr__: solishtirish va ko'rsatish</h4>
<pre><code>class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __eq__(self, boshqa):              # ❗ == operatori chaqirilganda ishlaydi
        return (self.sarlavha == boshqa.sarlavha and
                self.sahifalar == boshqa.sahifalar)

    def __repr__(self):                     # ❗ print() yoki konsolda ko'rsatishda ishlaydi
        return f"Kitob('{self.sarlavha}', {self.sahifalar} sahifa)"

k1 = Kitob("Python", 300)
k2 = Kitob("Python", 300)
print(k1 == k2)     # ✅ True - __eq__ tufayli, garchi ular XOTIRADA turli obyekt bo'lsa ham
print(k1)            # Kitob('Python', 300 sahifa) - __repr__ tufayli chiroyli chiqadi</code></pre>

<h4>BLOKA 2 — __lt__ va sort(): obyektlarni saralash</h4>
<pre><code>class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __lt__(self, boshqa):               # ❗ '<' operatori uchun, sort()ga kerak
        return self.sahifalar < boshqa.sahifalar

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar})"

kitoblar = [Kitob("A", 300), Kitob("B", 150), Kitob("C", 450)]
kitoblar.sort()                              # ❗ sort() ichida __lt__ ishlatiladi
print(kitoblar)   # [Kitob('B', 150), Kitob('A', 300), Kitob('C', 450)]</code></pre>

<h4>BLOKA 3 — @dataclass: magic method'larni avtomatik yaratish</h4>
<pre><code>from dataclasses import dataclass

@dataclass                                   # ❗ __init__, __repr__, __eq__'ni AVTOMATIK yaratadi
class Kitob:
    sarlavha: str
    sahifalar: int

k1 = Kitob("Python", 300)    # ❗ __init__ qo'lda yozilmagan, lekin ishlaydi!
k2 = Kitob("Python", 300)

print(k1)          # Kitob(sarlavha='Python', sahifalar=300) - __repr__ avtomatik
print(k1 == k2)    # True - __eq__ avtomatik</code></pre>

<h3>🐛 Ataylab xato — __eq__ yozib, __hash__ni unutish</h3>
<pre><code>class Kitob:
    def __init__(self, sarlavha):
        self.sarlavha = sarlavha

    def __eq__(self, boshqa):
        return self.sarlavha == boshqa.sarlavha
    # __hash__ YOZILMAGAN!

kitoblar_set = {Kitob("Python"), Kitob("Django")}
# ❌ TypeError: unhashable type: 'Kitob'
# (__eq__ yozilganda, Python __hash__ni AVTOMATIK None qilib qo'yadi!)</code></pre>

<p><strong>Natija:</strong> Python'da qoidaga ko'ra, agar ikkita obyekt <code>__eq__</code> orqali <strong>teng</strong> hisoblansa, ularning <code>hash()</code> qiymati ham <strong>bir xil</strong> bo'lishi kerak. Shuning uchun klassda <code>__eq__</code> <strong>qo'lda</strong> yozilsa, Python xavfsizlik uchun <code>__hash__</code>ni <strong>avtomatik <code>None</code></strong> qilib qo'yadi (klass "hash qilinmaydigan" bo'lib qoladi) — bu obyektni <code>set</code> yoki <code>dict</code> kaliti sifatida ishlatishga to'sqinlik qiladi. Yechim: agar obyekt hash qilinishi kerak bo'lsa, <code>__hash__</code>ni ham <strong>qo'lda</strong> yozish kerak (yoki <code>@dataclass(frozen=True)</code> ishlatish, u buni avtomatik hal qiladi).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Magic methods (dunder methods) nima?</h4>
<p>Ikki pastki chiziq bilan boshlanib tugaydigan metodlar (<code>__init__</code>, <code>__eq__</code>, <code>__repr__</code> va h.k.) — Python'ga sizning klassingiz standart operatorlar (<code>==</code>, <code>&lt;</code>, <code>len()</code>, <code>print()</code>) bilan <strong>qanday ishlashi kerakligini</strong> "o'rgatadi".</p>

<h4>2. __eq__ va __repr__ orasidagi farq</h4>
<p><code>__eq__</code> — <code>==</code> operatori chaqirilganda ishga tushadi, ikkita obyektni <strong>solishtiradi</strong>. <code>__repr__</code> — obyektni <code>print()</code> qilganda yoki konsolda ko'rsatilganda qanday <strong>matn</strong> chiqishini belgilaydi (debugging uchun juda foydali).</p>

<h4>3. __lt__ nima uchun kerak?</h4>
<p><code>__lt__</code> (<em>less than</em>) <code>&lt;</code> operatorini belgilaydi. <code>list.sort()</code> va <code>sorted()</code> funksiyalari ichki tomondan aynan <code>__lt__</code>dan foydalanadi — shuning uchun <code>__lt__</code> yozilgan klass obyektlarini to'g'ridan-to'g'ri saralash mumkin bo'ladi.</p>

<h4>4. @dataclass nima qiladi?</h4>
<p><code>@dataclass</code> dekoratori asosan <strong>ma'lumot saqlash</strong> uchun mo'ljallangan klasslarda <code>__init__</code>, <code>__repr__</code> va <code>__eq__</code>ni <strong>avtomatik</strong> yaratadi — faqat klass maydonlarini (turlari bilan) e'lon qilish yetarli, qolgan "andoza" (boilerplate) kodni yozish shart emas.</p>

<h4>5. Nega __eq__ yozilsa, __hash__ ham kerak bo'ladi?</h4>
<p>Python qoidasi: <strong>teng</strong> obyektlar bir xil <code>hash()</code> qiymatiga ega bo'lishi <strong>shart</strong> (bu <code>set</code>/<code>dict</code>ning to'g'ri ishlashi uchun zarur). Klassda <code>__eq__</code> qo'lda yozilganda, Python bu qoidani avtomatik ta'minlay olmasligi uchun ehtiyot chorasi sifatida <code>__hash__</code>ni <code>None</code>ga o'rnatadi. Agar obyekt hash qilinishi kerak bo'lsa, dasturchi buni <strong>qo'lda</strong> tuzatishi (yoki <code>@dataclass(frozen=True)</code> ishlatishi) kerak.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Magic methods (<code>__eq__</code>, <code>__repr__</code>, <code>__lt__</code>) klassingizga standart operatorlar xatti-harakatini qo'shadi</li>
<li>✅ <code>__eq__</code> — <code>==</code> uchun, <code>__repr__</code> — <code>print()</code>/debug uchun, <code>__lt__</code> — <code>&lt;</code>/<code>sort()</code> uchun</li>
<li>✅ <code>@dataclass</code> — <code>__init__</code>, <code>__repr__</code>, <code>__eq__</code>ni avtomatik yaratadi</li>
<li>✅ <code>__eq__</code> qo'lda yozilsa, Python <code>__hash__</code>ni avtomatik <code>None</code> qiladi</li>
<li>✅ Hash qilinishi kerak bo'lgan obyektlar uchun <code>__hash__</code>ni ham qo'lda yozish yoki <code>frozen=True</code> ishlatish kerak</li>
</ul>
"""

L9_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 9: Magic methods chuqurroq
# ════════════════════════════════════════════════════════════════════

from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────
# 1) __eq__ va __repr__
# ─────────────────────────────────────────────────────────────────────


class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __eq__(self, boshqa):
        return (self.sarlavha == boshqa.sarlavha and
                self.sahifalar == boshqa.sahifalar)

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar} sahifa)"


k1 = Kitob("Python", 300)
k2 = Kitob("Python", 300)
print(k1 == k2)
print(k1)

# ─────────────────────────────────────────────────────────────────────
# 2) __lt__ - saralash
# ─────────────────────────────────────────────────────────────────────


class KitobSaralanuvchi:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __lt__(self, boshqa):
        return self.sahifalar < boshqa.sahifalar

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar})"


kitoblar = [KitobSaralanuvchi("A", 300), KitobSaralanuvchi("B", 150), KitobSaralanuvchi("C", 450)]
kitoblar.sort()
print(kitoblar)

# ─────────────────────────────────────────────────────────────────────
# 3) @dataclass - avtomatik magic methods
# ─────────────────────────────────────────────────────────────────────


@dataclass
class KitobDC:
    sarlavha: str
    sahifalar: int


k3 = KitobDC("Python", 300)
k4 = KitobDC("Python", 300)

print(k3)
print(k3 == k4)

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - __eq__ yozib __hash__ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# class KitobXato:
#     def __init__(self, sarlavha):
#         self.sarlavha = sarlavha
#     def __eq__(self, boshqa):
#         return self.sarlavha == boshqa.sarlavha
#     # __hash__ YOZILMAGAN!
#
# kitoblar_set = {KitobXato("Python"), KitobXato("Django")}
# ❌ TypeError: unhashable type: 'KitobXato'
"""

L9_EX = [
    {
        "title": "__eq__ nima uchun ishlatiladi?",
        "description": "Klassda __eq__ metodini yozish asosan nima uchun kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Obyektni print() qilganda chiroyli ko'rsatish uchun",
            "== operatori chaqirilganda ikkita obyektni qanday solishtirish kerakligini belgilash uchun",
            "Obyektlarni saralash uchun",
            "Xotira sarfini kamaytirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu == belgisi ishlatilganda ishga tushadi.",
        "explanation": "__eq__ metodi == operatori chaqirilganda ishga tushadi va ikkita obyektning \"teng\" hisoblanishi uchun qaysi shartlar bajarilishi kerakligini belgilaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "@dataclass nima qiladi?",
        "description": "@dataclass dekoratori klassga qo'llanilganda nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Klassni butunlay o'chiradi",
            "__init__, __repr__ va __eq__ metodlarini avtomatik yaratadi",
            "Faqat klass nomini o'zgartiradi",
            "Klassni abstract qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu \"andoza\" (boilerplate) kod yozishning oldini oladi.",
        "explanation": "@dataclass dekoratori klass maydonlari asosida __init__, __repr__ va __eq__ metodlarini avtomatik yaratadi, dasturchi ularni qo'lda yozishi shart bo'lmaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "kitoblar.sort() ishlash jarayonini tartiblang",
        "description": "__lt__ yozilgan Kitob obyektlari ro'yxatida sort() chaqirilganda jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "sort() ro'yxatdagi elementlarni ikkitalab solishtirishni boshlaydi",
            "Har bir solishtirishda avtomatik __lt__ metodi chaqiriladi",
            "__lt__ sahifalar sonini solishtirib, True/False qaytaradi",
            "sort() shu natijalar asosida ro'yxatni to'g'ri tartibda joylashtiradi",
        ],
        "correct_order": [
            "sort() ro'yxatdagi elementlarni ikkitalab solishtirishni boshlaydi",
            "Har bir solishtirishda avtomatik __lt__ metodi chaqiriladi",
            "__lt__ sahifalar sonini solishtirib, True/False qaytaradi",
            "sort() shu natijalar asosida ro'yxatni to'g'ri tartibda joylashtiradi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "__eq__ yozilganda avtomatik None bo'ladigan metod",
        "description": "Klassda __eq__ qo'lda yozilganda, Python qaysi metodni avtomatik None qilib qo'yadi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "__hash__",
        "hint": "Bu metod set/dict kaliti sifatida ishlatish uchun kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega __eq__ yozilganda __hash__ ham kerak bo'ladi?",
        "description": (
            "Kitob klassida __eq__ yozilib, __hash__ yozilmagan holda, "
            "{Kitob(\"Python\"), Kitob(\"Django\")} kabi set yaratilsa, "
            "nega \"TypeError: unhashable type\" xatosi chiqadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Python'da qoida bor: agar ikkita obyekt __eq__ orqali teng "
            "hisoblansa, ularning hash() qiymati ham albatta bir xil "
            "bo'lishi shart (set va dict'ning to'g'ri ishlashi shu "
            "qoidaga tayanadi). Klassda __eq__ dasturchi tomonidan "
            "qo'lda yozilganda, Python bu qoidaga avtomatik rioya "
            "qilinishini kafolatlay olmaydi, shuning uchun ehtiyot "
            "chorasi sifatida __hash__ metodini avtomatik None qilib "
            "qo'yadi — bu klassni \"hash qilinmaydigan\" qiladi. "
            "Natijada bunday klass obyektlarini set yoki dict kaliti "
            "sifatida ishlatishga urinilganda, Python \"unhashable "
            "type\" xatosini beradi."
        ),
        "hint": "Python'da \"teng\" obyektlarning hash qiymati qanday bo'lishi shart?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R2_TEXT = """\
<h2>Review 2 (CAPSTONE) — Vazifa bajaruvchi: async, GIL va magic methods birgalikda</h2>

<pre class="mermaid">
flowchart TB
    TASK["@dataclass Vazifa (ustuvorlik, __lt__)"] --> QUEUE["ustuvorlik bo'yicha saralangan navbat"]
    QUEUE --> IOTASK["I/O-bound vazifalar -> asyncio.gather (bir vaqtda)"]
    QUEUE --> CPUTASK["CPU-bound vazifalar -> multiprocessing (7,8-darslar)"]
    DECORATOR["@vaqt_olchagich"] --> IOTASK
</pre>

<p>9 ta darsda o'rgangan hamma narsani &mdash; dekorator, generator, context manager, functools, comprehensions, type hints, asyncio, GIL-ni hisobga olgan dizayn, magic methods &mdash; birlashtirib, kichik <strong>vazifa bajaruvchi tizim</strong> quramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — @dataclass bilan Vazifa va ustuvorlik bo'yicha saralash</h4>
<pre><code>from dataclasses import dataclass, field

@dataclass
class Vazifa:
    nomi: str
    ustuvorlik: int          # ❗ kichikroq son - yuqoriroq ustuvorlik
    cpu_bound: bool = False   # ❗ True bo'lsa, bu CPU-bound vazifa (8-dars)

    def __lt__(self, boshqa):     # ❗ 9-dars: sort() uchun kerak
        return self.ustuvorlik < boshqa.ustuvorlik

vazifalar = [
    Vazifa("Email yuborish", ustuvorlik=2),
    Vazifa("Hisobot generatsiya qilish", ustuvorlik=1, cpu_bound=True),
    Vazifa("Fayl yuklab olish", ustuvorlik=3),
]
vazifalar.sort()   # ❗ __lt__ orqali ustuvorlik bo'yicha saralanadi</code></pre>

<h4>BLOKA 2 — I/O-bound vazifalarni asyncio bilan bajarish</h4>
<pre><code>import asyncio
import time
from functools import wraps

def vaqt_olchagich(func):                    # ❗ 1-dars: dekorator
    @wraps(func)
    async def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = await func(*args, **kwargs)
        print(f"{args[0].nomi}: {time.time() - boshlanish:.2f}s")
        return natija
    return wrapper

@vaqt_olchagich
async def io_vazifani_bajarish(vazifa: Vazifa) -> str:    # ❗ 6-dars: type hints
    await asyncio.sleep(1)                                  # ❗ 7-dars: I/O kutishni simulyatsiya qiladi
    return f"{vazifa.nomi} bajarildi"

async def main():
    io_vazifalar = [v for v in vazifalar if not v.cpu_bound]   # ❗ 5-dars: list comprehension
    natijalar = await asyncio.gather(*(io_vazifani_bajarish(v) for v in io_vazifalar))
    print(natijalar)

asyncio.run(main())</code></pre>

<h4>BLOKA 3 — CPU-bound vazifalarni to'g'ri ajratish (GIL-ni hisobga olgan qaror)</h4>
<pre><code># 8-darsni eslang: GIL tufayli CPU-bound vazifalar uchun asyncio/threading YORDAM BERMAYDI.
# Shuning uchun CPU-bound vazifalarni ALOHIDA, multiprocessing orqali bajarish kerak:

from multiprocessing import Process

def cpu_vazifani_bajarish(vazifa: Vazifa) -> None:
    print(f"{vazifa.nomi} - CPU-bound, alohida protsessda bajarilmoqda...")
    # ... ko'p hisoblash talab qiluvchi kod ...

cpu_vazifalar = [v for v in vazifalar if v.cpu_bound]
protsesslar = [Process(target=cpu_vazifani_bajarish, args=(v,)) for v in cpu_vazifalar]
# for p in protsesslar: p.start(); p.join()</code></pre>

<h3>🐛 Ataylab xato — CPU-bound kodni async funksiya ICHIDA to'g'ridan-to'g'ri chaqirish</h3>
<pre><code>async def vazifani_bajarish(vazifa: Vazifa):
    if vazifa.cpu_bound:
        # ❌ XATO: CPU-bound (bloklovchi) kod to'g'ridan-to'g'ri coroutine ichida!
        natija = 0
        for i in range(50_000_000):
            natija += i
        return natija
    await asyncio.sleep(1)
    return "bajarildi"

async def main():
    await asyncio.gather(
        vazifani_bajarish(Vazifa("Email", 2)),
        vazifani_bajarish(Vazifa("Hisobot", 1, cpu_bound=True)),   # ❗ bu BUTUN event loop'ni "muzlatib qo'yadi"!
    )
# Natija: "Email" vazifasi ham Hisobot tugagunicha KUTIB TURADI - garchi
# ular "bir vaqtda" ishlashi kerak bo'lsa ham! asyncio bitta oqimda ishlaydi.</code></pre>

<p><strong>Natija:</strong> <code>asyncio</code> <strong>bitta</strong> oqim (thread)da ishlaydi va vazifalar orasida faqat <code>await</code> nuqtalarida almashadi (7-dars). Agar coroutine ichida <strong>bloklovchi</strong> (uzoq davom etadigan, <code>await</code>siz) CPU-bound kod to'g'ridan-to'g'ri yozilsa, u <code>await</code> nuqtasiga yetmasdan butun event loop'ni <strong>band qilib qo'yadi</strong> — hech qanday boshqa coroutine (hatto oddiy <code>asyncio.sleep(1)</code> kutayotgan vazifa ham) shu vaqt ichida ishlamaydi. Bu 8-darsdagi GIL mavzusi bilan bevosita bog'liq: CPU-bound ishni <code>asyncio</code> ichiga qo'yish emas, balki <strong>alohida protsess</strong>ga (<code>multiprocessing</code>) ajratish kerak.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega Vazifa uchun @dataclass va __lt__ birga ishlatiladi?</h4>
<p><code>@dataclass</code> <code>__init__</code>/<code>__repr__</code>/<code>__eq__</code>ni avtomatik beradi, lekin <code>__lt__</code>ni <strong>bermaydi</strong> (bu solishtirish mantig'i loyihaga xos bo'lgani uchun avtomatik yaratilmaydi). Shuning uchun saralash kerak bo'lsa, <code>__lt__</code>ni <strong>qo'lda</strong> qo'shish kerak — bu 9-darsdagi tamoyilning davomi.</p>

<h4>2. Nega I/O-bound va CPU-bound vazifalar ALOHIDA ishlatiladi?</h4>
<p>8-darsda ko'rganimizdek, GIL tufayli <code>asyncio</code> (va <code>threading</code>) CPU-bound ishlarni tezlashtirmaydi. Shuning uchun vazifalarni turiga qarab <strong>ajratish</strong> shart: I/O-bound vazifalar <code>asyncio.gather()</code> bilan (bir vaqtda, samarali), CPU-bound vazifalar <code>multiprocessing</code> bilan (haqiqiy parallel protsesslarda) bajariladi.</p>

<h4>3. Nega CPU-bound kodni coroutine ichiga yozish xato?</h4>
<p><code>asyncio</code> hamkorlikka asoslangan (cooperative) — coroutine faqat <code>await</code> nuqtasida "boshqa vazifaga yo'l beraman" deydi. Agar coroutine ichida uzoq davom etadigan, <code>await</code>siz oddiy Python kodi (masalan katta <code>for</code> sikli) bo'lsa, u hech qachon "yo'l bermaydi" — bu butun event loop'ni bloklaydi, va <code>asyncio</code>ning asosiy afzalligi (bir vaqtda ko'p vazifa) yo'qoladi.</p>

<h4>4. @vaqt_olchagich dekoratori nega async funksiya bilan ishlaydi?</h4>
<p>1-darsdagi oddiy dekoratordan farqli, bu yerda <code>wrapper</code> ham <code>async def</code> deb e'lon qilingan va ichida <code>await func(...)</code> ishlatilgan — chunki <code>async</code> funksiyani "o'rovchi" wrapper ham coroutine bo'lishi, va asl coroutine'ni <code>await</code> orqali chaqirishi kerak.</p>

<h4>5. Bu loyiha 9 ta darsning qaysi tushunchalarini birlashtiradi?</h4>
<p>Dekorator (1-dars), list comprehension (5-dars), type hints (6-dars), asyncio/await/gather (7-dars), GIL-ni hisobga olgan I/O vs CPU-bound qaror (8-dars), <code>@dataclass</code> va <code>__lt__</code> (9-dars) — barchasi bitta, real arxitektura qarorini (vazifalarni to'g'ri ijro mexanizmiga yo'naltirish) qabul qilish uchun birgalikda ishlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>@dataclass</code> + qo'lda yozilgan <code>__lt__</code> — ma'lumot klassini saralanadigan qilish</li>
<li>✅ I/O-bound vazifalar <code>asyncio.gather()</code>, CPU-bound vazifalar <code>multiprocessing</code> bilan bajarilishi kerak</li>
<li>✅ Bloklovchi (uzoq, <code>await</code>siz) kodni coroutine ichiga yozish butun event loop'ni "muzlatib qo'yadi"</li>
<li>✅ Async dekoratorlar ham <code>async def</code> va <code>await</code> ishlatishi kerak</li>
<li>✅ 9 ta darsning barcha asosiy tushunchalari real arxitektura qarorlarida birlashib ishlaydi</li>
</ul>
"""

R2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVIEW 2 (CAPSTONE): Vazifa bajaruvchi
# ════════════════════════════════════════════════════════════════════

import asyncio
import time
from dataclasses import dataclass
from functools import wraps


@dataclass
class Vazifa:
    nomi: str
    ustuvorlik: int
    cpu_bound: bool = False

    def __lt__(self, boshqa):
        return self.ustuvorlik < boshqa.ustuvorlik


def vaqt_olchagich(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        boshlanish = time.time()
        natija = await func(*args, **kwargs)
        print(f"{args[0].nomi}: {time.time() - boshlanish:.2f}s")
        return natija
    return wrapper


@vaqt_olchagich
async def io_vazifani_bajarish(vazifa: Vazifa) -> str:
    await asyncio.sleep(1)
    return f"{vazifa.nomi} bajarildi"


async def main():
    vazifalar = [
        Vazifa("Email yuborish", ustuvorlik=2),
        Vazifa("Hisobot generatsiya qilish", ustuvorlik=1, cpu_bound=True),
        Vazifa("Fayl yuklab olish", ustuvorlik=3),
    ]
    vazifalar.sort()

    io_vazifalar = [v for v in vazifalar if not v.cpu_bound]
    natijalar = await asyncio.gather(*(io_vazifani_bajarish(v) for v in io_vazifalar))
    print(natijalar)


asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# CPU-bound vazifalarni multiprocessing bilan ajratish (izohda)
# ─────────────────────────────────────────────────────────────────────

# from multiprocessing import Process
#
# def cpu_vazifani_bajarish(vazifa: Vazifa) -> None:
#     print(f"{vazifa.nomi} - CPU-bound, alohida protsessda bajarilmoqda...")
#
# cpu_vazifalar = [v for v in vazifalar if v.cpu_bound]
# protsesslar = [Process(target=cpu_vazifani_bajarish, args=(v,)) for v in cpu_vazifalar]
# for p in protsesslar: p.start(); p.join()

# ─────────────────────────────────────────────────────────────────────
# Ataylab xato - CPU-bound kodni coroutine ichida chaqirish (izohda)
# ─────────────────────────────────────────────────────────────────────

# async def vazifani_bajarish_xato(vazifa):
#     if vazifa.cpu_bound:
#         natija = 0
#         for i in range(50_000_000):   # ❌ bloklovchi, await'siz CPU-bound kod!
#             natija += i
#         return natija
#     await asyncio.sleep(1)
#     return "bajarildi"
"""

R2_EX = [
    {
        "title": "@dataclass'da __lt__ nega qo'lda yozilishi kerak?",
        "description": "@dataclass avtomatik __init__/__repr__/__eq__ beradi, lekin nega __lt__ni qo'lda yozish kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki __lt__ Python'da umuman mavjud emas",
            "Chunki solishtirish mantig'i (masalan qaysi maydon bo'yicha) loyihaga xos, @dataclass buni avtomatik bila olmaydi",
            "Chunki dataclass __lt__ni har doim xato yaratadi",
            "__lt__ yozish shart emas, sort() baribir ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "@dataclass qaysi maydon bo'yicha saralashni qanday bilsin?",
        "explanation": "@dataclass __init__/__repr__/__eq__ni avtomatik yaratadi, lekin __lt__ni bermaydi, chunki qaysi maydon (yoki qaysi mantiq) bo'yicha solishtirish kerakligi loyihaga xos qaror — buni dasturchi qo'lda belgilashi kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "I/O-bound va CPU-bound vazifalar nega alohida ishlatiladi?",
        "description": "Vazifa bajaruvchi tizimda nega I/O-bound vazifalar asyncio bilan, CPU-bound vazifalar esa multiprocessing bilan alohida bajariladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki ular bir xil kodni talab qiladi, farq yo'q",
            "GIL tufayli asyncio/threading CPU-bound ishlarni tezlashtirmaydi, shuning uchun CPU-bound uchun multiprocessing kerak",
            "Chunki multiprocessing I/O-bound uchun ham eng tez usul",
            "Chunki asyncio faqat CPU-bound uchun mo'ljallangan",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "8-darsni eslang.",
        "explanation": "GIL sababli asyncio va threading CPU-bound ishlarni tezlashtirmaydi (8-dars), shuning uchun I/O-bound vazifalar asyncio.gather() bilan, CPU-bound vazifalar esa multiprocessing bilan alohida bajarilishi kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Vazifa bajaruvchining ishlash jarayonini tartiblang",
        "description": "main() funksiyasida vazifalar ro'yxati tayyorlanib, ishga tushirilishi jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "vazifalar ro'yxati yaratiladi va __lt__ orqali ustuvorlik bo'yicha sort() qilinadi",
            "List comprehension orqali faqat io-bound vazifalar ajratib olinadi",
            "asyncio.gather() barcha io-bound vazifalarni bir vaqtda boshlaydi",
            "Har bir vazifa @vaqt_olchagich dekoratori orqali vaqti bilan chop etiladi",
        ],
        "correct_order": [
            "vazifalar ro'yxati yaratiladi va __lt__ orqali ustuvorlik bo'yicha sort() qilinadi",
            "List comprehension orqali faqat io-bound vazifalar ajratib olinadi",
            "asyncio.gather() barcha io-bound vazifalarni bir vaqtda boshlaydi",
            "Har bir vazifa @vaqt_olchagich dekoratori orqali vaqti bilan chop etiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CPU-bound vazifalar uchun to'g'ri modul",
        "description": "GIL tufayli CPU-bound vazifalarda haqiqiy parallellik olish uchun qaysi modul ishlatilishi kerak? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "multiprocessing",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega CPU-bound kodni coroutine ichiga yozish butun event loop'ni bloklaydi?",
        "description": (
            "vazifani_bajarish_xato() coroutine'i ichida cpu_bound=True "
            "bo'lgan vazifa uchun 50 million marta sikl bajarilsa (await "
            "qilinmagan holda), nega bu paytda BOSHQA coroutine'lar "
            "(hatto oddiy asyncio.sleep(1) kutayotganlari ham) "
            "ishlamay qoladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "asyncio bitta oqim (thread) ichida, hamkorlikka asoslangan "
            "(cooperative) tarzda ishlaydi — coroutine'lar orasida "
            "almashish FAQAT await nuqtalarida sodir bo'ladi, ya'ni "
            "coroutine o'zi \"men hozir kutaman, boshqa vazifa ishlasin\" "
            "deb signal berganda. Agar coroutine ichida uzoq davom "
            "etadigan, await ishlatilmagan oddiy Python kodi (masalan "
            "50 million marta sikl) bo'lsa, bu kod hech qachon \"yo'l "
            "bermaydi\" — u tugagunicha bitta oqimning o'zi butunlay "
            "band bo'lib qoladi. Natijada, boshqa barcha coroutine'lar "
            "(hatto ular faqat asyncio.sleep(1) kabi oddiy kutish "
            "bajarayotgan bo'lsa ham) bu bloklovchi kod tugamaguncha "
            "umuman ishga tushirilmaydi — bu asyncio'ning asosiy "
            "afzalligini (bir vaqtda ko'p vazifani boshqarish) "
            "yo'qqa chiqaradi."
        ),
        "hint": "asyncio coroutine'lar orasida qachon almashadi — istalgan vaqtda, yoki faqat await nuqtalarida?",
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


def build_sections_json(order, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "python",
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
            lang = ldata.get("lang", "python")

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
                    [{"filename": f"misol.py", "language": lang, "code": code}],
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
