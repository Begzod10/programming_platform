"""Seed "Python: Testlash" (6 lessons): pytest fundamentals through a full
Flask API test suite. Mirrors "JavaScript: Testlash" (course 70) lesson
structure, closing the parity gap — Python has Asoslari/Flask/Flask O'rta/
Keyingi Bosqich but zero testing coverage, while JS has a dedicated course.

Usage:
    cd backend
    python scripts/seed_python_testing.py
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
    "title": "Python: Testlash",
    "description": (
        "Python kodini avtomatik testlashni o'rganing: pytest asoslari, "
        "fixture'lar, mock, Flask ilovalarini testlash, TDD (Test Driven "
        "Development) va test coverage. Python Flask kursini tugatgan "
        "dasturchilar uchun mo'ljallangan."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 4,
    "max_points": 80,
    "category_id": 8,  # Python
    "prerequisite_course_id": 21,  # Python Flask
    "is_active": True,
    "is_published": False,  # flip to True once all lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Pytest bilan tanishuv",
     "scope": "Installing pytest, writing simple test functions, assert "
              "statements, test discovery conventions, running pytest."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Fixture'lar va Mock",
     "scope": "@pytest.fixture, conftest.py, setup/teardown pattern, "
              "parametrize, unittest.mock (Mock, patch), monkeypatch."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-Flask ilovasini testlash",
     "scope": "app.test_client(), testing routes/status codes/JSON "
              "responses, test database fixture, isolating test DB."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-TDD (Test Driven Development)",
     "scope": "Red-Green-Refactor cycle, writing tests before "
              "implementation, TDD workflow on a small feature."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Test Coverage",
     "scope": "pytest-cov, coverage report, what percentage is "
              "meaningful, spotting untested edge cases."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-CAPSTONE: To'liq testlangan Flask API",
     "scope": "Final capstone: full Flask CRUD API with a complete test "
              "suite (fixtures, mocks, TDD) and high coverage."},
]


L1_TEXT = """\
<h2>Pytest bilan tanishuv — birinchi test 5 daqiqada</h2>

<pre class="mermaid">
flowchart LR
    F["test_*.py fayli"] --> D["pytest — testlarni topadi (discovery)"]
    D --> R["Har bir test_ funksiyasi ishga tushadi"]
    R -->|assert to'g'ri| P["✅ PASSED"]
    R -->|assert xato| X["❌ FAILED"]
</pre>

<p>Hozirgacha kodingizni qo'lda tekshirib kelgansiz: dasturni ishga tushirib, natijani ko'zingiz bilan solishtirasiz. Bu — sekin va xato qilish oson. <strong>pytest</strong> — Python'dagi eng mashhur test freymvorki: kodingizning to'g'ri ishlashini avtomatik, bir necha soniyada tekshirib beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — pytest o'rnatish va birinchi test</h4>
<pre><code># Terminal:
pip install pytest</code></pre>

<pre><code># kalkulyator.py
def qoshish(a, b):
    return a + b</code></pre>

<pre><code># test_kalkulyator.py
from kalkulyator import qoshish

def test_qoshish():
    assert qoshish(2, 3) == 5</code></pre>

<pre><code># Terminal:
pytest
# ================ 1 passed in 0.01s ================</code></pre>

<h4>BLOKA 2 — bir nechta assert va muvaffaqiyatsiz test</h4>
<pre><code>def test_qoshish_manfiy_sonlar():
    assert qoshish(-2, -3) == -5

def test_qoshish_nol_bilan():
    assert qoshish(5, 0) == 5

def test_qoshish_xato_kutilgan():
    assert qoshish(2, 2) == 5  # ❗ ataylab xato — 4 emas, 5 kutilmoqda</code></pre>

<pre><code># Terminal:
pytest
# ================ 2 passed, 1 failed in 0.02s ================
# FAILED test_kalkulyator.py::test_qoshish_xato_kutilgan
# assert 4 == 5</code></pre>

<p>pytest xato bo'lgan testni aniq ko'rsatadi: qaysi test, qaysi qatorda, va aynan qanday qiymatlar solishtirilgani (<code>4 == 5</code>). Bu — muammoni tezda topishga yordam beradi.</p>

<h4>BLOKA 3 — bir nechta test faylini ishga tushirish</h4>
<pre><code># Loyiha tuzilishi:
# loyiha/
#   kalkulyator.py
#   test_kalkulyator.py
#   validatsiya.py
#   test_validatsiya.py

# Terminal — barcha testlarni ishga tushirish:
pytest

# Faqat bitta faylni ishga tushirish:
pytest test_kalkulyator.py

# Faqat bitta funksiyani ishga tushirish:
pytest test_kalkulyator.py::test_qoshish</code></pre>

<h3>🐛 Ataylab xato — funksiya nomida test_ prefiksini unutish</h3>
<pre><code># test_kalkulyator.py
from kalkulyator import qoshish

def qoshishni_tekshir():  # ❌ 'test_' bilan boshlanmaydi!
    assert qoshish(2, 2) == 5  # bu yerda ATAYLAB xato bor — lekin hech qachon ishga tushmaydi!</code></pre>

<pre><code># Terminal:
pytest
# ================ no tests ran in 0.01s ================</code></pre>

<p><strong>Natija:</strong> funksiya nomi <code>test_</code> bilan boshlanmasa, pytest uni <strong>umuman testlar ro'yxatiga qo'shmaydi</strong> — hech qanday xato yoki ogohlantirish chiqmaydi, shunchaki "no tests ran" deydi. Bu juda xavfli: dasturchi "hammasi yashil (passed)" deb o'ylashi mumkin, aslida esa funksiya <strong>hech qachon tekshirilmagan</strong>. Bu — sinov yozishning eng ko'p uchraydigan, lekin sezilmaydigan xatolaridan biri.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. pytest testlarni qanday "topadi" (discovery)?</h4>
<p>pytest joriy papka va papkachalarni skanerlab, quyidagi qoidalarga mos fayl/funksiyalarni qidiradi: fayl nomi <code>test_*.py</code> yoki <code>*_test.py</code> bilan boshlanishi/tugashi, funksiya nomi <code>test_</code> bilan boshlanishi kerak. Shu qoidaga mos kelmagan narsa — <strong>butunlay e'tiborsiz qoldiriladi</strong>.</p>

<h4>2. assert — testning yuragi</h4>
<p><code>assert shart</code> — agar <code>shart</code> <code>False</code> bo'lsa, test <strong>FAILED</strong> deb belgilanadi va pytest aniq qaysi qiymatlar mos kelmaganini ko'rsatadi. Agar <code>shart</code> <code>True</code> bo'lsa, hech narsa sodir bo'lmaydi — test <strong>PASSED</strong>.</p>

<h4>3. Nega har bir funksiyani qo'lda emas, test orqali tekshirish kerak?</h4>
<p>Qo'lda tekshirish — bir martalik va unutiladi. Test funksiyasi esa doimiy saqlanadi: kodni keyinroq o'zgartirsangiz, <code>pytest</code>ni qayta ishga tushirib, hech narsa buzilmaganini soniyalarda bilib olasiz.</p>

<h4>4. Test fayli qayerda joylashadi?</h4>
<p>Odatda test fayli tekshirilayotgan modul bilan bir papkada yoki alohida <code>tests/</code> papkasida joylashadi. Muhimi — nomlanish qoidasiga rioya qilish.</p>

<h4>5. pytest chiqishi (output) nimani bildiradi?</h4>
<pre><code>================ 2 passed, 1 failed in 0.02s ================</code></pre>
<p><code>passed</code> — muvaffaqiyatli o'tgan testlar soni, <code>failed</code> — muvaffaqiyatsiz testlar soni. Har bir <code>FAILED</code> ostida qaysi <code>assert</code> ishlamagani va nima kutilib, nima olingani ko'rsatiladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ pytest — kod to'g'riligini avtomatik tekshiruvchi test freymvork</li>
<li>✅ Test fayli <code>test_*.py</code>, test funksiyasi <code>test_</code> bilan boshlanishi shart — aks holda pytest uni topmaydi</li>
<li>✅ <code>assert shart</code> — shart yolg'on bo'lsa test FAILED bo'ladi, aniq qiymatlar ko'rsatiladi</li>
<li>✅ <code>pytest</code> buyrug'i — barcha testlarni, <code>pytest fayl.py::funksiya</code> — bitta testni ishga tushiradi</li>
<li>✅ <code>test_</code> prefiksini unutish — eng xavfli, sezilmaydigan xato: test "yo'qolib qoladi", hech qanday ogohlantirishsiz</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 1: Pytest bilan tanishuv
# ════════════════════════════════════════════════════════════════════

# ─── kalkulyator.py ───
def qoshish(a, b):
    return a + b


def ayirish(a, b):
    return a - b


# ─── test_kalkulyator.py ───
# from kalkulyator import qoshish, ayirish

def test_qoshish():
    assert qoshish(2, 3) == 5


def test_qoshish_manfiy_sonlar():
    assert qoshish(-2, -3) == -5


def test_qoshish_nol_bilan():
    assert qoshish(5, 0) == 5


def test_ayirish():
    assert ayirish(10, 4) == 6


# ─────────────────────────────────────────────────────────────────────
# Ataylab xato — 'test_' prefiksisiz funksiya (izohda, pytet topmaydi)
# ─────────────────────────────────────────────────────────────────────

# def qoshishni_tekshir():  # ❌ 'test_' bilan boshlanmagani uchun pytest
#     assert qoshish(2, 2) == 5  # bu qatorni HECH QACHON ishga tushirmaydi!


# Terminal:
#   pip install pytest
#   pytest                              # barcha testlar
#   pytest test_kalkulyator.py          # bitta fayl
#   pytest test_kalkulyator.py::test_qoshish  # bitta test
"""

L1_EX = [
    {
        "title": "pytest test funksiyasini qanday topadi?",
        "description": "pytest qaysi funksiyalarni \"test\" deb hisoblab, avtomatik ishga tushiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Fayldagi barcha funksiyalarni",
            "Nomi 'test_' bilan boshlanadigan funksiyalarni",
            "Faqat 'main' nomli funksiyani",
            "Faqat argumentsiz funksiyalarni",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Nomlanish qoidasiga e'tibor bering — pytest buni qat'iy talab qiladi.",
        "explanation": "pytest test_*.py fayllaridagi, nomi 'test_' bilan boshlanadigan funksiyalarnigina avtomatik test deb hisoblab ishga tushiradi. Boshqacha nomlangan funksiyalar butunlay e'tiborsiz qoldiriladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "assert False bo'lsa nima bo'ladi?",
        "description": "Test funksiyasi ichida assert shartning natijasi False bo'lsa, pytest nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa, test davom etadi",
            "Testni FAILED deb belgilaydi va qaysi qiymatlar mos kelmaganini ko'rsatadi",
            "Dasturni butunlay to'xtatadi",
            "Testni avtomatik qayta ishga tushiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "assert — testning muvaffaqiyat/muvaffaqiyatsizligini aniqlovchi asosiy mexanizm.",
        "explanation": "assert shart False bo'lsa, pytest bu testni FAILED deb belgilaydi va konsolda aynan qaysi qiymatlar (masalan 4 == 5) mos kelmaganini aniq ko'rsatadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Testni ishga tushirish ketma-ketligini joylang",
        "description": "Yangi loyihada pytest bilan birinchi testni yozish va ishga tushirish qadamlarini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "pip install pytest",
            "test_*.py nomli fayl yaratiladi",
            "Ichida test_ bilan boshlanadigan funksiya yoziladi",
            "Funksiya ichida assert shart yoziladi",
            "Terminalda pytest buyrug'i ishga tushiriladi",
        ],
        "correct_order": [
            "pip install pytest",
            "test_*.py nomli fayl yaratiladi",
            "Ichida test_ bilan boshlanadigan funksiya yoziladi",
            "Funksiya ichida assert shart yoziladi",
            "Terminalda pytest buyrug'i ishga tushiriladi",
        ],
        "hint": "Avval kutubxona o'rnatiladi, keyin fayl va funksiya yoziladi, so'ng ishga tushiriladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "test_ prefiksi unutilsa nima muammo yuzaga keladi?",
        "description": (
            "Agar test funksiyasi nomi 'test_' bilan emas, boshqacha "
            "(masalan 'qoshishni_tekshir') deb yozilsa, pytest ishga "
            "tushirilganda nima sodir bo'ladi, va bu nega ayniqsa xavfli "
            "hisoblanadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "pytest bu funksiyani umuman test deb tanimaydi va uni testlar "
            "ro'yxatiga qo'shmaydi — natijada u hech qachon ishga tushmaydi. "
            "Bu ayniqsa xavfli, chunki pytest hech qanday xato yoki "
            "ogohlantirish bermaydi, shunchaki \"no tests ran\" yoki boshqa "
            "testlar bo'yicha \"hammasi passed\" deb ko'rsatadi. Dasturchi "
            "kodning to'g'ri tekshirilganiga ishonch hosil qiladi, aslida "
            "esa muhim funksiya hech qachon sinovdan o'tkazilmagan bo'ladi "
            "— bu tinch, sezilmaydigan xato turi."
        ),
        "hint": "pytest xato bermaydi — u shunchaki bu funksiyani \"ko'rmaydi\".",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L2_TEXT = """\
<h2>Fixture'lar va Mock — testlarni tayyorlash va soxtalashtirish</h2>

<pre class="mermaid">
flowchart LR
    FX["@pytest.fixture"] -->|tayyor ma'lumot beradi| T["test funksiyasi"]
    MOCK["mock/patch"] -->|haqiqiy chaqiruvni almashtiradi| T
    T --> R["Tez, ishonchli, tashqi bog'liqliksiz test"]
</pre>

<p>1-darsda oddiy funksiyalarni testladik. Lekin real loyihalarda testlar ko'pincha bir xil "tayyorgarlik"ni talab qiladi (masalan, test ma'lumotlari) yoki tashqi narsalarga bog'liq bo'ladi (API, vaqt, fayl tizimi). <strong>Fixture</strong> — tayyorgarlikni takrorlamaslik uchun, <strong>mock</strong> — tashqi bog'liqlikni "soxtalashtirish" uchun.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi fixture</h4>
<pre><code>import pytest

@pytest.fixture
def foydalanuvchi():
    return {"ism": "Olim", "yosh": 22}

def test_foydalanuvchi_ismi(foydalanuvchi):  # ❗ fixture nomi parametr sifatida
    assert foydalanuvchi["ism"] == "Olim"

def test_foydalanuvchi_yoshi(foydalanuvchi):  # ❗ har ikkala test yangi foydalanuvchi oladi
    assert foydalanuvchi["yosh"] == 22</code></pre>

<p>pytest <code>foydalanuvchi</code> nomli parametrni ko'rib, xuddi shu nomdagi fixture funksiyasini avtomatik chaqiradi va natijasini testga uzatadi. Har bir test — <strong>o'z nusxasini</strong> oladi.</p>

<h4>BLOKA 2 — conftest.py orqali fixture'ni bo'lishish</h4>
<pre><code># conftest.py — shu papkadagi BARCHA test fayllari uchun umumiy fixture'lar
import pytest

@pytest.fixture
def db_ulanish():
    print("DB ulanish ochildi")
    yield "fake_connection"  # ❗ yield'dan oldingi qism — setup
    print("DB ulanish yopildi")  # ❗ yield'dan keyingi qism — teardown</code></pre>

<pre><code># test_users.py — conftest.py'dagi fixture avtomatik ko'rinadi
def test_foydalanuvchi_saqlash(db_ulanish):
    assert db_ulanish == "fake_connection"</code></pre>

<h4>BLOKA 3 — mock bilan tashqi chaqiruvni almashtirish</h4>
<pre><code># ob_havo.py
import requests

def hozirgi_harorat(shahar):
    javob = requests.get(f"https://api.masalan.uz/weather?city={shahar}")
    return javob.json()["harorat"]</code></pre>

<pre><code># test_ob_havo.py
from unittest.mock import patch
from ob_havo import hozirgi_harorat

@patch("ob_havo.requests.get")  # ❗ ob_havo MODULIDA ishlatilgan joyi patch qilinadi
def test_hozirgi_harorat(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    natija = hozirgi_harorat("Toshkent")
    assert natija == 25
    # ❗ Haqiqiy internetga umuman so'rov ketmadi!</code></pre>

<h3>🐛 Ataylab xato — mock'ni noto'g'ri joyda patch qilish</h3>
<pre><code># ❌ requests kutubxonasining o'zini patch qilish — ISHLAMAYDI kutilganidek
@patch("requests.get")  # ❌ noto'g'ri manzil!
def test_hozirgi_harorat_xato(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    natija = hozirgi_harorat("Toshkent")
    # ❗ Bu test ba'zan ishlaydi, ba'zan haqiqiy internetga so'rov yuboradi —
    # chunki ob_havo.py ichida "requests" allaqachon import qilib olingan
    # va u yerdagi nusxa patch qilinmagan!</code></pre>

<p><strong>Natija:</strong> <code>@patch("requests.get")</code> — <code>requests</code> kutubxonasining <strong>o'zini</strong> global darajada almashtiradi, lekin <code>ob_havo.py</code> fayli <code>import requests</code> qilib, o'ziga xos nusxa (reference) yaratib olgan. Patch <code>ob_havo.requests.get</code> emas, balki boshqa joyni o'zgartirgani uchun, <code>hozirgi_harorat()</code> funksiyasi hali ham <strong>haqiqiy</strong> <code>requests.get</code>ni chaqirishga urinishi mumkin. Qoida: <strong>patch qilinadigan narsa qayerda ISHLATILSA, o'sha yerda patch qilinadi</strong> — qayerda e'lon qilingani emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Fixture nima uchun kerak?</h4>
<p>Ko'p testlar bir xil "boshlang'ich holat"ni talab qiladi (masalan, test foydalanuvchisi, DB ulanishi). Fixture shu tayyorgarlikni bitta joyda yozib, uni istalgan test funksiyasiga parametr sifatida "in'ektsiya" qilish imkonini beradi — kod takrorlanmaydi.</p>

<h4>2. yield — setup va teardown'ni bitta fixture'da birlashtirish</h4>
<p><code>yield</code>dan oldingi kod — <strong>setup</strong> (tayyorgarlik), <code>yield</code>dan keyingi kod — <strong>teardown</strong> (tozalash). Test tugagach, pytest avtomatik ravishda <code>yield</code>dan keyingi qismni ishga tushiradi — resurslarni to'g'ri yopish uchun.</p>

<h4>3. conftest.py nima uchun alohida?</h4>
<p><code>conftest.py</code>dagi fixture'lar <strong>import qilinmasdan</strong> ham, xuddi shu papka (va uning quyi papkalari)dagi barcha test fayllarida avtomatik mavjud bo'ladi. Bu — fixture'larni butun loyiha bo'ylab bo'lishishning standart usuli.</p>

<h4>4. Mock nima va nega kerak?</h4>
<p>Mock — haqiqiy funksiya/obyekt o'rniga "soxta" versiyasini qo'yish. Bu testlarni <strong>tez</strong> (internetga chiqmaydi), <strong>ishonchli</strong> (tarmoq ishlamasa ham test o'tadi) va <strong>bashorat qilinadigan</strong> (har doim bir xil natija) qiladi.</p>

<h4>5. Patch manzilini to'g'ri tanlash</h4>
<p>Eng ko'p uchraydigan xato — <code>@patch</code>ga kutubxonaning "asl" manzilini berish. To'g'ri yondashuv: patch qilinayotgan narsa <strong>qaysi modulda chaqirilsa</strong>, o'sha modul nomi bilan patch qilinadi (<code>@patch("ob_havo.requests.get")</code>, <code>@patch("requests.get")</code> emas).</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>@pytest.fixture</code> — testlar uchun qayta ishlatiladigan tayyorgarlikni yaratadi</li>
<li>✅ <code>conftest.py</code> — fixture'larni butun papka bo'ylab avtomatik bo'lishadi</li>
<li>✅ <code>yield</code> — fixture ichida setup va teardown'ni bitta joyda yozish imkonini beradi</li>
<li>✅ <code>@patch</code> — tashqi chaqiruvlarni (API, DB) soxta versiya bilan almashtiradi</li>
<li>✅ Patch <strong>ishlatilgan joyda</strong> qilinadi, e'lon qilingan joyda emas — bu eng ko'p uchraydigan mock xatosi</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 2: Fixture'lar va Mock
# ════════════════════════════════════════════════════════════════════

import pytest
from unittest.mock import patch

# ─────────────────────────────────────────────────────────────────────
# 1) Oddiy fixture
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def foydalanuvchi():
    return {"ism": "Olim", "yosh": 22}


def test_foydalanuvchi_ismi(foydalanuvchi):
    assert foydalanuvchi["ism"] == "Olim"


def test_foydalanuvchi_yoshi(foydalanuvchi):
    assert foydalanuvchi["yosh"] == 22


# ─────────────────────────────────────────────────────────────────────
# 2) yield bilan setup/teardown
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def db_ulanish():
    print("DB ulanish ochildi")
    yield "fake_connection"
    print("DB ulanish yopildi")


def test_foydalanuvchi_saqlash(db_ulanish):
    assert db_ulanish == "fake_connection"


# ─────────────────────────────────────────────────────────────────────
# 3) parametrize — bitta testni bir nechta qiymat bilan ishga tushirish
# ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("son,kutilgan", [
    (2, 4),
    (3, 9),
    (5, 25),
])
def test_kvadrat(son, kutilgan):
    assert son ** 2 == kutilgan


# ─────────────────────────────────────────────────────────────────────
# 4) Mock bilan tashqi chaqiruvni almashtirish — TO'G'RI usul
# ─────────────────────────────────────────────────────────────────────

# ob_havo.py:
# import requests
# def hozirgi_harorat(shahar):
#     javob = requests.get(f"https://api.masalan.uz/weather?city={shahar}")
#     return javob.json()["harorat"]

@patch("ob_havo.requests.get")  # ✅ ob_havo MODULIDA ishlatilgan joyi
def test_hozirgi_harorat(mock_get):
    mock_get.return_value.json.return_value = {"harorat": 25}
    # natija = hozirgi_harorat("Toshkent")
    # assert natija == 25


# ─────────────────────────────────────────────────────────────────────
# 5) Ataylab xato — noto'g'ri joyda patch (izohda)
# ─────────────────────────────────────────────────────────────────────

# @patch("requests.get")  # ❌ noto'g'ri — ob_havo.py o'z nusxasini oladi
# def test_hozirgi_harorat_xato(mock_get):
#     mock_get.return_value.json.return_value = {"harorat": 25}
#     # Bu ba'zan haqiqiy internetga so'rov yuborishi mumkin!
"""

L2_EX = [
    {
        "title": "Fixture nima uchun ishlatiladi?",
        "description": "pytest'da @pytest.fixture asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Testni sekinlashtirish uchun",
            "Testlar uchun qayta ishlatiladigan tayyorgarlik (ma'lumot, ulanish) yaratish uchun",
            "Faqat xato xabarlarini formatlash uchun",
            "Testlarni tasodifiy tartibda ishga tushirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Fixture — bir nechta testda kerak bo'ladigan tayyorgarlikni bitta joyda yozish usuli.",
        "explanation": "Fixture testlar uchun umumiy tayyorgarlikni (masalan test ma'lumotlari, DB ulanishi) bitta joyda yozib, uni istalgan test funksiyasiga parametr sifatida uzatish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "yield'dan keyingi kod fixture'da nima vazifani bajaradi?",
        "description": "Fixture ichida yield qatoridan KEYIN yozilgan kod odatda nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Setup (tayyorgarlik) uchun",
            "Teardown (tozalash, resurslarni yopish) uchun",
            "Faqat konsolga chiqarish uchun",
            "Hech qanday vazifasi yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "yield'dan oldin — tayyorlash, keyin — tozalash.",
        "explanation": "yield'dan oldingi kod setup, keyingi kod teardown hisoblanadi. Test tugagach, pytest avtomatik ravishda yield'dan keyingi qismni ishga tushiradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Mock qo'llash oqimini to'g'ri tartibda joylang",
        "description": "requests.get() chaqiruvini mock qilib testlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "@patch(\"modul.requests.get\") dekoratori qo'shiladi",
            "mock_get.return_value.json.return_value qiymati belgilanadi",
            "Test ichida haqiqiy funksiya chaqiriladi",
            "Funksiya ichida requests.get() o'rniga mock ishlatiladi",
            "assert bilan natija tekshiriladi",
        ],
        "correct_order": [
            "@patch(\"modul.requests.get\") dekoratori qo'shiladi",
            "mock_get.return_value.json.return_value qiymati belgilanadi",
            "Test ichida haqiqiy funksiya chaqiriladi",
            "Funksiya ichida requests.get() o'rniga mock ishlatiladi",
            "assert bilan natija tekshiriladi",
        ],
        "hint": "Avval patch o'rnatiladi, keyin mock javobi sozlanadi, so'ng funksiya chaqirilib tekshiriladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega @patch(\"requests.get\") kutilgandek ishlamasligi mumkin?",
        "description": (
            "ob_havo.py fayli 'import requests' qilib, requests.get()ni "
            "chaqiradi. Agar test @patch(\"requests.get\") (kutubxonaning "
            "o'zini) patch qilsa, nega bu ba'zan ishlamay, haqiqiy "
            "internetga so'rov ketishi mumkin? To'g'ri yechim qanday? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "ob_havo.py fayli 'import requests' qilganda, requests modulining "
            "o'ziga ishora qiluvchi nusxa (reference) ob_havo modulining "
            "nomlar makonida (namespace) yaratiladi. @patch(\"requests.get\") "
            "faqat requests kutubxonasining GLOBAL nusxasini almashtiradi, "
            "lekin ob_havo.py o'zining ichki nusxasi orqali requests.get'ni "
            "chaqiradi — bu nusxa patch qilinmagan bo'lib qolishi mumkin. "
            "To'g'ri yechim — patch qilinadigan narsa qayerda ISHLATILSA, "
            "o'sha modul nomi bilan patch qilish: @patch(\"ob_havo.requests.get\"), "
            "@patch(\"requests.get\") emas."
        ),
        "hint": "Import qilingandan keyin, funksiya qaysi modul nomi orqali chaqiruvni amalga oshiradi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>Flask ilovasini testlash — test_client va test ma'lumotlar bazasi</h2>

<pre class="mermaid">
flowchart LR
    TC["app.test_client()"] -->|so'rov yuboradi| R["Flask route"]
    R --> RESP["javob: status_code + JSON"]
    RESP --> A["assert bilan tekshiriladi"]
    TESTDB[("Test DB — alohida!")] --> R
</pre>

<p>1-2-darslarda oddiy funksiyalarni testladik. Endi — butun Flask ilovasini, ya'ni HTTP so'rov-javob jarayonini testlaymiz. Flask buning uchun maxsus vosita beradi: <strong>test_client</strong> — serverni haqiqatan ishga tushirmasdan, so'rov yuborish imkonini beruvchi "soxta klient".</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — test_client bilan birinchi so'rov</h4>
<pre><code># app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def bosh_sahifa():
    return jsonify({"xabar": "Salom!"})</code></pre>

<pre><code># test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    return app.test_client()  # ❗ haqiqiy server ishga tushmaydi!

def test_bosh_sahifa(client):
    javob = client.get('/')
    assert javob.status_code == 200
    assert javob.get_json() == {"xabar": "Salom!"}</code></pre>

<h4>BLOKA 2 — POST so'rov va status kodlarni tekshirish</h4>
<pre><code>@app.route('/users', methods=['POST'])
def user_yaratish():
    data = request.get_json()
    if not data.get('ism'):
        return jsonify({"xato": "ism majburiy"}), 400
    return jsonify({"id": 1, "ism": data['ism']}), 201</code></pre>

<pre><code>def test_user_yaratish_togri(client):
    javob = client.post('/users', json={"ism": "Olim"})
    assert javob.status_code == 201
    assert javob.get_json()["ism"] == "Olim"

def test_user_yaratish_xato(client):
    javob = client.post('/users', json={})  # ism yo'q
    assert javob.status_code == 400</code></pre>

<h4>BLOKA 3 — test ma'lumotlar bazasi fixture'i</h4>
<pre><code># conftest.py
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # ❗ xotiradagi vaqtinchalik DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # test uchun toza jadval yaratiladi
            yield client
            db.drop_all()  # test tugagach, hammasi tozalanadi</code></pre>

<h3>🐛 Ataylab xato — production ma'lumotlar bazasiga qarshi test yozish</h3>
<pre><code># ❌ conftest.py — TESTING sozlanmagan, haqiqiy DATABASE_URL ishlatilgan!
import pytest
from app import app, db

@pytest.fixture
def client():
    # app.config['SQLALCHEMY_DATABASE_URI'] hali ham .env'dagi HAQIQIY DB manzili!
    with app.test_client() as client:
        yield client

def test_user_ochirish(client):
    client.delete('/users/1')  # ❗ Bu HAQIQIY foydalanuvchini o'chirib yuboradi!</code></pre>

<p><strong>Natija:</strong> agar test fixture'ida <code>SQLALCHEMY_DATABASE_URI</code> aniq test bazasiga (masalan <code>sqlite:///:memory:</code>) o'zgartirilmasa, ilova <strong>hali ham production (haqiqiy) ma'lumotlar bazasiga</strong> ulanadi. Testlar odatda ma'lumot qo'shadi, o'zgartiradi va o'chiradi — bu haqiqiy foydalanuvchilar ma'lumotini butunlay buzishi yoki yo'q qilishi mumkin! Bu — testlashdagi eng xavfli, halokatli xatolardan biri.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. test_client() nima qiladi?</h4>
<p><code>app.test_client()</code> — haqiqiy portda server ishga tushirmasdan, Flask ilovasiga to'g'ridan-to'g'ri (xotira ichida) so'rov yuborish imkonini beruvchi maxsus obyekt. Bu testlarni juda tezlashtiradi — tarmoq, port band bo'lishi kabi muammolar umuman bo'lmaydi.</p>

<h4>2. javob.status_code va javob.get_json()</h4>
<p>Har bir <code>test_client</code> so'rovi (<code>client.get()</code>, <code>client.post()</code> va h.k.) javob obyektini qaytaradi. <code>status_code</code> — HTTP status (200, 201, 400...), <code>get_json()</code> — javob tanasini Python obyektiga (dict/list) aylantirib beradi.</p>

<h4>3. Nega test uchun ALOHIDA ma'lumotlar bazasi kerak?</h4>
<p>Testlar tez-tez ishga tushadi va odatda ma'lumot yaratish/o'chirish bilan bog'liq. Agar ular production DB'ga ulansa, har bir test ishga tushganda haqiqiy ma'lumotlar xavf ostida qoladi. Shuning uchun testlar uchun <strong>alohida, vaqtinchalik</strong> baza (masalan xotiradagi SQLite) ishlatiladi.</p>

<h4>4. sqlite:///:memory: nima?</h4>
<p>Bu — diskda emas, <strong>xotirada</strong> yashaydigan vaqtinchalik SQLite bazasi. Test tugagach, u avtomatik yo'qoladi — hech qanday fayl yoki tashqi bog'liqlik qolmaydi, va har bir test ishga tushganda "toza" holatdan boshlanadi.</p>

<h4>5. db.create_all() / db.drop_all() — nima uchun fixture ichida?</h4>
<p><code>db.create_all()</code> — test boshlanishidan oldin jadvallarni yaratadi, <code>db.drop_all()</code> — test tugagach hammasini tozalaydi. Bu <code>yield</code> orqali fixture ichiga joylashtirilib, har bir test <strong>toza, boshqa testlardan mustaqil</strong> muhitda ishlashini ta'minlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>app.test_client()</code> — Flask ilovasiga real server'siz so'rov yuborish imkonini beradi</li>
<li>✅ <code>javob.status_code</code> va <code>javob.get_json()</code> — HTTP javobini tekshirishning asosiy vositalari</li>
<li>✅ Testlar hech qachon production ma'lumotlar bazasiga ulanmasligi kerak — alohida test DB ishlatiladi</li>
<li>✅ <code>sqlite:///:memory:</code> — har safar toza holatdan boshlanadigan, xotiradagi vaqtinchalik baza</li>
<li>✅ <code>db.create_all()</code>/<code>db.drop_all()</code> fixture ichida — har bir test mustaqil, izolyatsiyalangan muhitda ishlaydi</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 3: Flask ilovasini testlash
# ════════════════════════════════════════════════════════════════════

import pytest
from flask import Flask, jsonify, request

# ─── app.py (soddalashtirilgan) ───
app = Flask(__name__)
users = []

@app.route('/')
def bosh_sahifa():
    return jsonify({"xabar": "Salom!"})


@app.route('/users', methods=['POST'])
def user_yaratish():
    data = request.get_json()
    if not data.get('ism'):
        return jsonify({"xato": "ism majburiy"}), 400
    yangi_user = {"id": len(users) + 1, "ism": data['ism']}
    users.append(yangi_user)
    return jsonify(yangi_user), 201


# ─────────────────────────────────────────────────────────────────────
# conftest.py — test uchun ALOHIDA konfiguratsiya
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # xotiradagi test DB
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────────────────────────────
# test_app.py
# ─────────────────────────────────────────────────────────────────────

def test_bosh_sahifa(client):
    javob = client.get('/')
    assert javob.status_code == 200
    assert javob.get_json() == {"xabar": "Salom!"}


def test_user_yaratish_togri(client):
    javob = client.post('/users', json={"ism": "Olim"})
    assert javob.status_code == 201
    assert javob.get_json()["ism"] == "Olim"


def test_user_yaratish_xato(client):
    javob = client.post('/users', json={})
    assert javob.status_code == 400


# ─────────────────────────────────────────────────────────────────────
# Ataylab xato — TESTING/test DB sozlanmagan (izohda)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client_xato():
#     # ❌ SQLALCHEMY_DATABASE_URI o'zgartirilmadi — hali ham .env'dagi HAQIQIY DB!
#     with app.test_client() as client:
#         yield client
#
# def test_user_ochirish_xato(client_xato):
#     client_xato.delete('/users/1')  # ❌ HAQIQIY foydalanuvchini o'chirib yuborishi mumkin!
"""

L3_EX = [
    {
        "title": "test_client() nima uchun kerak?",
        "description": "Flask'da app.test_client() asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ilovani production'ga joylashtirish uchun",
            "Haqiqiy server ishga tushirmasdan, so'rov yuborish uchun",
            "Ma'lumotlar bazasini yaratish uchun",
            "CSS'ni tekshirish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — testlar uchun mo'ljallangan \"soxta klient\".",
        "explanation": "app.test_client() haqiqiy portda server ishga tushirmasdan, Flask ilovasiga to'g'ridan-to'g'ri so'rov yuborish imkonini beradi, bu testlarni tezlashtiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "javob.get_json() nima qaytaradi?",
        "description": "test_client so'rovidan qaytgan javob obyektida get_json() nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "HTTP status kodini",
            "Javob tanasini Python obyektiga (dict/list) aylantirib beradi",
            "So'rov headerlarini",
            "Faqat matnni, hech qanday aylantirishsiz",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu metod JSON javobni Python'da ishlatish uchun tayyorlaydi.",
        "explanation": "get_json() javob tanasidagi JSON matnni Python dict yoki list obyektiga aylantirib beradi, shunda uni oddiy Python kod bilan tekshirish mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Flask test fixture'ini to'g'ri tartibda joylang",
        "description": "Test uchun izolyatsiyalangan Flask muhitini tayyorlash qadamlarini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "app.config['TESTING'] = True o'rnatiladi",
            "SQLALCHEMY_DATABASE_URI test bazasiga o'zgartiriladi",
            "db.create_all() bilan toza jadvallar yaratiladi",
            "yield orqali client testga uzatiladi",
            "Test tugagach db.drop_all() bilan tozalanadi",
        ],
        "correct_order": [
            "app.config['TESTING'] = True o'rnatiladi",
            "SQLALCHEMY_DATABASE_URI test bazasiga o'zgartiriladi",
            "db.create_all() bilan toza jadvallar yaratiladi",
            "yield orqali client testga uzatiladi",
            "Test tugagach db.drop_all() bilan tozalanadi",
        ],
        "hint": "Avval konfiguratsiya, keyin baza tayyorlanadi, keyin test ishlaydi, so'ng tozalanadi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Test uchun alohida ma'lumotlar bazasi nega shart?",
        "description": (
            "Agar test fixture'ida SQLALCHEMY_DATABASE_URI production "
            "bazasiga ishora qilib tursa (test bazasiga o'zgartirilmasa), "
            "bu nega jiddiy xavf hisoblanadi? Buning oldini qanday olish "
            "mumkin? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Testlar odatda ma'lumot yaratish, o'zgartirish va o'chirish "
            "bilan bog'liq amallarni bajaradi. Agar ular haqiqiy (production) "
            "ma'lumotlar bazasiga ulansa, har bir test ishga tushganda "
            "haqiqiy foydalanuvchilar ma'lumotlari o'zgartirilishi yoki "
            "butunlay o'chirilib yuborilishi mumkin — bu qaytarib bo'lmas "
            "zarar keltirishi mumkin. Buning oldini olish uchun testlar "
            "har doim alohida, vaqtinchalik ma'lumotlar bazasida (masalan "
            "sqlite:///:memory:) ishlashi kerak, va bu SQLALCHEMY_DATABASE_URI "
            "orqali test fixture'ida aniq belgilanishi shart."
        ),
        "hint": "Testlar ma'lumot yaratadi/o'chiradi — bu haqiqiy bazada bo'lsa nima yuz beradi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>TDD (Test Driven Development) — avval test, keyin kod</h2>

<pre class="mermaid">
flowchart LR
    RED["🔴 RED — muvaffaqiyatsiz test yoziladi"] --> GREEN["🟢 GREEN — testni o'tkazuvchi minimal kod"]
    GREEN --> REFACTOR["🔵 REFACTOR — kodni yaxshilash, testlar hali ham o'tadi"]
    REFACTOR --> RED
</pre>

<p>Hozirgacha avval kod yozib, keyin test qo'shdik. TDD (Test Driven Development) — buni <strong>teskarisiga</strong> qiladi: avval muvaffaqiyatsiz test yoziladi, keyin uni o'tkazish uchun eng oddiy kod yoziladi, so'ng kod yaxshilanadi. Bu — Red-Green-Refactor sikli.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — 🔴 RED: avval muvaffaqiyatsiz test</h4>
<pre><code># test_baholash.py — funksiya HALI mavjud emas!
from baholash import harfli_baho

def test_harfli_baho_a():
    assert harfli_baho(95) == "A"</code></pre>

<pre><code># Terminal:
pytest
# ModuleNotFoundError: No module named 'baholash'
# ❗ Bu — kutilgan holat! Hali kod yozilmagan.</code></pre>

<h4>BLOKA 2 — 🟢 GREEN: testni o'tkazadigan ENG ODDIY kod</h4>
<pre><code># baholash.py
def harfli_baho(ball):
    return "A"  # ❗ Hozircha shunchaki testni o'tkazish uchun</code></pre>

<pre><code># Terminal:
pytest
# ================ 1 passed in 0.01s ================</code></pre>

<p>Ajablanarli, lekin bu <strong>to'g'ri TDD</strong>: hozircha faqat bitta test bor, va u o'tdi. Keyingi qadam — yana bitta test qo'shib, kodni haqiqiy mantiqqa yaqinlashtirish.</p>

<h4>BLOKA 3 — yana RED → GREEN, kodni bosqichma-bosqich to'ldirish</h4>
<pre><code># Yana bitta test qo'shildi:
def test_harfli_baho_b():
    assert harfli_baho(82) == "B"

def test_harfli_baho_f():
    assert harfli_baho(40) == "F"</code></pre>

<pre><code># Terminal: pytest → 2 FAILED (chunki hali ham "A" qaytaradi)

# Endi kodni haqiqiy mantiq bilan to'ldiramiz — 🟢 GREEN:
def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    elif ball >= 70:
        return "C"
    else:
        return "F"</code></pre>

<pre><code># Terminal:
pytest
# ================ 3 passed in 0.01s ================</code></pre>

<h3>🐛 Ataylab xato — "GREEN" holatida to'xtab, faqat bitta testga moslashtirish</h3>
<pre><code># ❌ Faqat 1-testni ko'rib, funksiyani shunga "moslab" yozish:
def harfli_baho(ball):
    if ball == 95:  # ❌ faqat aynan shu qiymat uchun ishlaydi!
        return "A"
    return "F"  # boshqa hamma narsa uchun noto'g'ri</code></pre>

<p><strong>Natija:</strong> <code>test_harfli_baho_a()</code> (95 bilan) o'tadi, lekin funksiya aslida <strong>umumiy mantiqni</strong> amalga oshirmagan — u faqat bitta aniq test qiymatiga "moslashtirilgan". Agar boshqa hech qanday test yozilmasa, bu xato hech qachon aniqlanmaydi. TDD'ning kuchi aynan shunda: <strong>ko'proq test qo'shish</strong> orqali funksiya haqiqatan umumiy holatlar uchun ishlashini asta-sekin isbotlash. Bitta test — hech narsani kafolatlamaydi; testlar to'plami (turli chegaraviy holatlar bilan) haqiqiy ishonchni beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega avval test, keyin kod?</h4>
<p>Bu sizni <strong>aniq talabni</strong> avvaldan belgilashga majburlaydi: funksiya nima qilishi kerak, aniq qanday natija kutiladi. Kod yozilgandan keyin test qo'shilsa, ko'pincha test "kodga moslashtiriladi", aksincha bo'lishi kerak.</p>

<h4>2. RED bosqichi nima uchun muhim?</h4>
<p>Test avval <strong>muvaffaqiyatsiz</strong> bo'lishi shart — bu testning o'zi to'g'ri ishlayotganini tasdiqlaydi. Agar yozilgan test hali kod yo'q holda ham "passed" bo'lsa — demak test noto'g'ri yozilgan (hech narsani tekshirmayapti).</p>

<h4>3. GREEN bosqichida "eng oddiy kod" nima uchun yetarli?</h4>
<p>Maqsad — tezda ishlaydigan holatga o'tish. Keyingi testlar kodni tabiiy ravishda to'liqroq, umumiyroq qilishga majburlaydi. Bitta testda "A" qaytarish — vaqtinchalik, u keyingi testlar bilan albatta kengayadi.</p>

<h4>4. REFACTOR bosqichi nima qiladi?</h4>
<p>Barcha testlar o'tgandan keyin, kodni <strong>tozalash, tartibga solish, takrorlanishni olib tashlash</strong> mumkin — testlar "xavfsizlik to'ri" vazifasini o'taydi: agar refactor paytida biror narsa buzilsa, testlar darhol xato ko'rsatadi.</p>

<h4>5. Nega bitta test yetarli emas?</h4>
<p>Bitta muvaffaqiyatli test — funksiya <strong>faqat shu aniq holat uchun</strong> to'g'ri ekanini bildiradi, umumiy mantiq to'g'riligini emas. Chegaraviy holatlar (masalan 90, 89, 0, manfiy son) uchun alohida testlar yozish — funksiyaning haqiqatan ishonchli ekanini isbotlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ TDD — Red (muvaffaqiyatsiz test) → Green (minimal kod) → Refactor (yaxshilash) sikli</li>
<li>✅ Test avval yozilib, keyin kod — bu talabni aniq belgilashga majbur qiladi</li>
<li>✅ RED bosqichida test albatta FAILED bo'lishi kerak — bu testning o'zi ishlayotganini tasdiqlaydi</li>
<li>✅ GREEN bosqichida faqat testlarni o'tkazish uchun minimal kod yetarli</li>
<li>✅ Bitta testga "moslashtirilgan" kod xavfli — ko'proq test qo'shish orqaligina umumiy mantiq tekshiriladi</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 4: TDD (Test Driven Development)
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 🔴 RED — test_baholash.py (funksiya hali mavjud emas)
# ─────────────────────────────────────────────────────────────────────

# from baholash import harfli_baho
#
# def test_harfli_baho_a():
#     assert harfli_baho(95) == "A"
#
# Terminal: pytest -> ModuleNotFoundError (kutilgan holat!)


# ─────────────────────────────────────────────────────────────────────
# 🟢 GREEN — baholash.py (eng oddiy kod, faqat 1-testni o'tkazish uchun)
# ─────────────────────────────────────────────────────────────────────

def harfli_baho_v1(ball):
    return "A"  # vaqtinchalik — faqat bitta test bor


# ─────────────────────────────────────────────────────────────────────
# Yana testlar qo'shildi -> yana RED -> kodni kengaytiramiz -> GREEN
# ─────────────────────────────────────────────────────────────────────

def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    elif ball >= 70:
        return "C"
    else:
        return "F"


# test_baholash.py — to'liq test to'plami
def test_harfli_baho_a():
    assert harfli_baho(95) == "A"

def test_harfli_baho_b():
    assert harfli_baho(82) == "B"

def test_harfli_baho_c():
    assert harfli_baho(75) == "C"

def test_harfli_baho_f():
    assert harfli_baho(40) == "F"

def test_harfli_baho_chegara():
    assert harfli_baho(90) == "A"  # chegaraviy qiymat — 90 aynan A
    assert harfli_baho(89) == "B"  # chegaradan bir past — B


# ─────────────────────────────────────────────────────────────────────
# Ataylab xato — faqat bitta test qiymatiga moslashtirilgan kod (izohda)
# ─────────────────────────────────────────────────────────────────────

# def harfli_baho_xato(ball):
#     if ball == 95:  # ❌ faqat aynan shu qiymat uchun ishlaydi!
#         return "A"
#     return "F"  # boshqa hamma narsa uchun noto'g'ri
"""

L4_EX = [
    {
        "title": "TDD sikli qaysi tartibda bajariladi?",
        "description": "TDD (Test Driven Development)ning uch bosqichi qaysi tartibda ketma-ket bajariladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Green -> Red -> Refactor",
            "Red -> Green -> Refactor",
            "Refactor -> Red -> Green",
            "Green -> Refactor -> Red",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Avval muvaffaqiyatsiz test, keyin minimal kod, so'ng yaxshilash.",
        "explanation": "TDD sikli: RED (muvaffaqiyatsiz test yoziladi) -> GREEN (testni o'tkazuvchi minimal kod yoziladi) -> REFACTOR (kod yaxshilanadi, testlar hali ham o'tadi).",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "RED bosqichida test qanday natija berishi shart?",
        "description": "TDD'ning RED bosqichida yozilgan test ishga tushirilganda nima bo'lishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Albatta PASSED bo'lishi kerak",
            "Albatta FAILED bo'lishi kerak (kod hali yo'q yoki to'liq emas)",
            "Hech qanday natija bermasligi kerak",
            "Ahamiyati yo'q, ikkalasi ham bo'lishi mumkin",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu bosqichda kod hali yozilmagan yoki testni qondirmaydi.",
        "explanation": "RED bosqichida test albatta FAILED bo'lishi kerak — bu testning o'zi to'g'ri ishlayotganini va haqiqatan biror narsani tekshirayotganini tasdiqlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TDD amaliyoti ketma-ketligini to'g'ri joylang",
        "description": "harfli_baho funksiyasini TDD bilan yaratish qadamlarini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "test_harfli_baho_a() yoziladi (funksiya hali yo'q)",
            "pytest ishga tushiriladi — ModuleNotFoundError (RED)",
            "Eng oddiy kod yoziladi — faqat 'A' qaytaradi (GREEN)",
            "Yangi testlar (B, C, F) qo'shiladi",
            "Kod umumiy mantiq bilan to'ldiriladi, barcha testlar o'tadi",
        ],
        "correct_order": [
            "test_harfli_baho_a() yoziladi (funksiya hali yo'q)",
            "pytest ishga tushiriladi — ModuleNotFoundError (RED)",
            "Eng oddiy kod yoziladi — faqat 'A' qaytaradi (GREEN)",
            "Yangi testlar (B, C, F) qo'shiladi",
            "Kod umumiy mantiq bilan to'ldiriladi, barcha testlar o'tadi",
        ],
        "hint": "Avval test, keyin muvaffaqiyatsizlik, keyin minimal kod, so'ng kengaytirish.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bitta testga moslashtirilgan kod nega xavfli?",
        "description": (
            "Agar dasturchi harfli_baho(ball) funksiyasini faqat "
            "'if ball == 95: return \"A\"' deb yozib, boshqa barcha holatlar "
            "uchun umumiy mantiq yozmasa, lekin test o'tsa — bu nega "
            "xavfli? TDD bu muammoni qanday hal qiladi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar funksiya faqat bitta aniq test qiymatiga (masalan 95) "
            "moslashtirilgan bo'lsa, u test o'tishi mumkin, lekin bu "
            "funksiyaning umumiy mantiqni to'g'ri amalga oshirganini "
            "kafolatlamaydi — masalan 82 yoki 40 kabi boshqa qiymatlar "
            "uchun butunlay noto'g'ri natija berishi mumkin. Agar boshqa "
            "test yozilmasa, bu xato hech qachon aniqlanmaydi. TDD bu "
            "muammoni ko'proq test qo'shish orqali hal qiladi: har bir "
            "yangi test funksiyani haqiqiy, umumiy mantiqqa asta-sekin "
            "yaqinlashtirishga majbur qiladi, faqat bitta holatga "
            "moslashtirib qolishga imkon bermaydi."
        ),
        "hint": "Bitta test — faqat bitta holatni tekshiradi. Umumiy mantiqni qanday isbotlash mumkin?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>Test Coverage — kodning qancha qismi tekshirilgan?</h2>

<pre class="mermaid">
flowchart LR
    CODE["Manba kod"] --> COV["pytest-cov ishga tushadi"]
    TESTS["Testlar"] --> COV
    COV --> REPORT["Coverage hisobot: % va qatorlar"]
    REPORT -->|past %| GAP["Tekshirilmagan qatorlar topiladi"]
</pre>

<p>Testlar yozdik, lekin qanday bilamiz — kodning <strong>qaysi qismi</strong> haqiqatan test qilingan, qaysi qismi hali tekshirilmagan? <strong>Test coverage</strong> (test qamrovi) — aynan shu savolga javob beruvchi o'lchov: testlar ishga tushganda kodning necha foizi bajarilgani.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — pytest-cov o'rnatish va birinchi hisobot</h4>
<pre><code># Terminal:
pip install pytest-cov</code></pre>

<pre><code># baholash.py
def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    else:
        return "F"</code></pre>

<pre><code># test_baholash.py
from baholash import harfli_baho

def test_harfli_baho_a():
    assert harfli_baho(95) == "A"</code></pre>

<pre><code># Terminal:
pytest --cov=baholash

# Name           Stmts   Miss  Cover
# ----------------------------------
# baholash.py        5      2    60%</code></pre>

<h4>BLOKA 2 — qaysi qatorlar tekshirilmaganini ko'rish</h4>
<pre><code># Terminal — qaysi aniq qatorlar o'tkazib yuborilganini ko'rsatadi:
pytest --cov=baholash --cov-report=term-missing

# Name           Stmts   Miss  Cover   Missing
# ------------------------------------------------
# baholash.py        5      2    60%   5, 7</code></pre>

<p><code>Missing</code> ustuni — testlar hech qachon bajarmagan qator raqamlarini ko'rsatadi. Bu yerda 5 va 7-qatorlar (<code>elif</code> va <code>else</code> shoxobchalari) hech qachon ishga tushmagan — chunki faqat 95 ball bilan test qilingan.</p>

<h4>BLOKA 3 — coverage'ni 100%'ga yetkazish</h4>
<pre><code># Yetishmayotgan holatlar uchun testlar qo'shiladi:
def test_harfli_baho_b():
    assert harfli_baho(82) == "B"

def test_harfli_baho_f():
    assert harfli_baho(40) == "F"</code></pre>

<pre><code># Terminal:
pytest --cov=baholash --cov-report=term-missing

# Name           Stmts   Miss  Cover   Missing
# ------------------------------------------------
# baholash.py        5      0   100%</code></pre>

<h3>🐛 Ataylab xato — 100% coverage'ga faqat raqam uchun erishish</h3>
<pre><code># ❌ Qator ishga tushadi, lekin HECH NARSA tekshirilmaydi!
def test_harfli_baho_qamrov_uchun():
    harfli_baho(82)  # ❗ funksiya chaqirildi — qator "bajarildi" deb hisoblanadi
    # ❌ Lekin assert YO'Q! Natija hech qachon tekshirilmaydi.</code></pre>

<p><strong>Natija:</strong> coverage hisoboti 100%ni ko'rsatadi — chunki <code>harfli_baho(82)</code> qatori haqiqatan <strong>bajarilgan</strong>. Lekin bu test funksiyaning natijasi <strong>to'g'ri</strong> yoki <strong>noto'g'ri</strong> ekanini umuman tekshirmaydi — <code>assert</code> yo'q! Agar funksiya ichida xato bo'lsa ham (masalan noto'g'ri chegara), bu test baribir "passed" bo'lib qolaveradi. <strong>Coverage — qaysi qatorlar ishga tushganini o'lchaydi, xulq-atvor to'g'riligini emas.</strong> 100% coverage — kod xatosiz degani emas.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Coverage nimani o'lchaydi?</h4>
<p>Coverage — testlar ishga tushganda manba koddagi qaysi qatorlar (yoki shoxobchalar) <strong>bajarilgani</strong>ni foiz sifatida ko'rsatadi. Bu — kodning qanchalik "sinovdan o'tkazilgani" haqida ko'rsatkich, lekin sifat kafolati emas.</p>

<h4>2. Qaysi coverage foizi "yaxshi"?</h4>
<p>100% coverage — ideal ko'rinadi, lekin har doim ham amaliy maqsad emas. Ko'pchilik jamoalar 80-90% atrofida to'xtaydi va <strong>muhim, xavfli</strong> qismlarga (masalan to'lov, autentifikatsiya) alohida e'tibor berishadi. Muhimi — raqamning o'zi emas, balki <strong>qaysi qatorlar</strong> tekshirilmay qolgani.</p>

<h4>3. --cov-report=term-missing nima uchun foydali?</h4>
<p>Oddiy <code>--cov</code> faqat umumiy foizni ko'rsatadi. <code>term-missing</code> esa <strong>aniq qaysi qator raqamlari</strong> hech qachon ishga tushmaganini ko'rsatadi — bu qaysi testlarni qo'shish kerakligini aniq bildiradi.</p>

<h4>4. Nega 100% coverage kodning xatosiz ekanini bildirmaydi?</h4>
<p>Coverage faqat qator <strong>bajarilganini</strong> tekshiradi, natijaning <strong>to'g'riligini</strong> emas. <code>assert</code>siz yoki noto'g'ri <code>assert</code>li test qator sonini oshirishi mumkin, lekin haqiqiy xatolarni hech qachon topmaydi.</p>

<h4>5. Coverage'ni qanday ishlatish kerak?</h4>
<p>Coverage hisobotini <strong>"qaysi kod umuman tekshirilmagan"</strong>ni topish uchun ishlating, keyin o'sha qismlar uchun <strong>mazmunli</strong> (aniq assert bilan) testlar yozing. Coverage raqamining o'zini maqsad qilib olish — sifatsiz testlarga olib kelishi mumkin.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>pytest-cov</code> — testlar kodning necha foizini bajarganini o'lchaydi</li>
<li>✅ <code>--cov-report=term-missing</code> — aynan qaysi qatorlar tekshirilmaganini ko'rsatadi</li>
<li>✅ Yuqori coverage foizi — yaxshi belgi, lekin yagona maqsad bo'lmasligi kerak</li>
<li>✅ Coverage — qatorlar bajarilishini o'lchaydi, natija to'g'riligini emas</li>
<li>✅ <code>assert</code>siz test — coverage'ni "yolg'on" oshiradi, lekin hech qanday haqiqiy xatoni topmaydi</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 5: Test Coverage
# ════════════════════════════════════════════════════════════════════

# ─── baholash.py ───
def harfli_baho(ball):
    if ball >= 90:
        return "A"
    elif ball >= 80:
        return "B"
    else:
        return "F"


# ─── test_baholash.py — to'liq (barcha shoxobchalarni qamrab oluvchi) ───
def test_harfli_baho_a():
    assert harfli_baho(95) == "A"


def test_harfli_baho_b():
    assert harfli_baho(82) == "B"


def test_harfli_baho_f():
    assert harfli_baho(40) == "F"


# ─────────────────────────────────────────────────────────────────────
# Ataylab xato — coverage uchun chaqirish, lekin tekshirmaslik (izohda)
# ─────────────────────────────────────────────────────────────────────

# def test_harfli_baho_qamrov_uchun():
#     harfli_baho(82)  # ❌ qator "bajarildi" hisoblanadi, lekin assert yo'q!
#     # Natija umuman tekshirilmaydi — funksiyada xato bo'lsa ham bilinmaydi.


# Terminal:
#   pip install pytest-cov
#   pytest --cov=baholash                        # umumiy foiz
#   pytest --cov=baholash --cov-report=term-missing  # qaysi qatorlar yetishmayapti
"""

L5_EX = [
    {
        "title": "Test coverage nimani o'lchaydi?",
        "description": "Test coverage (test qamrovi) asosan nimani ko'rsatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Testlar necha soniyada ishlaganini",
            "Testlar ishga tushganda manba koddagi qaysi qatorlar bajarilganini",
            "Nechta dasturchi kod yozganini",
            "Loyihaning umumiy hajmini",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu — kod qanchalik \"ishga tushirilgani\", sifat emas.",
        "explanation": "Test coverage testlar ishga tushganda manba koddagi qaysi qatorlar (yoki shoxobchalar) bajarilganini foiz sifatida ko'rsatadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "--cov-report=term-missing nima uchun foydali?",
        "description": "pytest --cov-report=term-missing bayrog'i qanday qo'shimcha ma'lumot beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat umumiy foizni ko'rsatadi",
            "Aynan qaysi qator raqamlari hech qachon ishga tushmaganini ko'rsatadi",
            "Testlarni tezlashtiradi",
            "Xatolarni avtomatik tuzatadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "\"Missing\" so'zi nimani anglatishi mumkin?",
        "explanation": "--cov-report=term-missing oddiy foizdan tashqari, aniq qaysi qator raqamlari testlar tomonidan hech qachon bajarilmaganini ko'rsatadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Coverage'ni yaxshilash jarayonini to'g'ri tartibda joylang",
        "description": "Past coverage foizidan boshlab, uni oshirish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "pytest --cov=modul --cov-report=term-missing ishga tushiriladi",
            "Missing ustunida tekshirilmagan qator raqamlari ko'riladi",
            "O'sha qatorlarni ishga tushiruvchi holatlar uchun yangi testlar yoziladi",
            "Coverage qayta o'lchanadi",
        ],
        "correct_order": [
            "pytest --cov=modul --cov-report=term-missing ishga tushiriladi",
            "Missing ustunida tekshirilmagan qator raqamlari ko'riladi",
            "O'sha qatorlarni ishga tushiruvchi holatlar uchun yangi testlar yoziladi",
            "Coverage qayta o'lchanadi",
        ],
        "hint": "Avval hisobot olinadi, keyin bo'shliqlar topiladi, keyin test qo'shiladi.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega 100% coverage kod xatosiz ekanini kafolatlamaydi?",
        "description": (
            "Agar test funksiyasi harfli_baho(82)ni chaqirsa, lekin hech "
            "qanday assert yozmasa, va bu qator \"bajarilgan\" deb "
            "hisoblanib coverage 100%ga chiqsa — bu nega chalg'ituvchi? "
            "Coverage aslida nimani va nimani tekshirmaydi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Coverage faqat kodning qaysi qatorlari testlar ishga tushganda "
            "bajarilganini o'lchaydi — bu qatorlarning natijasi to'g'ri "
            "yoki noto'g'ri ekanini tekshirmaydi. Agar test funksiyasi "
            "harfli_baho(82)ni chaqirib, lekin natijani assert bilan "
            "solishtirmasa, qator \"bajarilgan\" deb hisoblanadi va coverage "
            "oshadi, lekin funksiya noto'g'ri natija qaytarsa ham (masalan "
            "\"A\" o'rniga \"C\"), test baribir \"passed\" bo'lib qolaveradi. "
            "Shuning uchun yuqori coverage foizi — kod to'g'ri ishlashining "
            "kafolati emas, faqat qancha kod \"ishga tushirilgani\"ning "
            "ko'rsatkichi."
        ),
        "hint": "Coverage \"bajarilgan qator\"ni sanaydi — bu \"to'g'ri natija\" bilan bir xil narsami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>🚀 CAPSTONE: To'liq testlangan Flask API</h2>

<p>Bu — kursning yakuniy loyihasi. 1-5-darslarda o'rgangan hamma narsa — pytest asoslari, fixture'lar, mock, Flask test_client, TDD, va coverage — bitta real loyihada birlashadi: <strong>Vazifalar (Tasks) REST API</strong> uchun to'liq test to'plami.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>GET /tasks</code>, <code>POST /tasks</code>, <code>PUT /tasks/:id</code>, <code>DELETE /tasks/:id</code> — to'liq CRUD uchun testlar</li>
<li>Har bir endpoint uchun <strong>ham muvaffaqiyatli, ham xato</strong> holatlar testlanadi</li>
<li>Test uchun izolyatsiyalangan fixture (har bir test — <strong>toza</strong> holatdan boshlanadi)</li>
<li>Tashqi bildirishnoma (notification) chaqiruvi <code>mock</code> bilan almashtiriladi</li>
<li>TDD yondashuvi bilan yangi funksiya (masalan, "faqat bajarilmagan vazifalarni ko'rsatish") qo'shiladi</li>
<li><code>pytest-cov</code> bilan coverage tekshiriladi</li>
</ul>

<h3>Skelet — boshlash uchun</h3>
<pre><code># app.py
from flask import Flask, jsonify, request

app = Flask(__name__)
vazifalar = []

@app.route('/tasks', methods=['GET'])
def royxat():
    return jsonify(vazifalar)

@app.route('/tasks', methods=['POST'])
def yaratish():
    # Vazifa: validatsiya + yangi vazifa qo'shish
    pass

@app.route('/tasks/&lt;int:task_id&gt;', methods=['PUT'])
def yangilash(task_id):
    # Vazifa: bajarildi holatini almashtirish
    pass

@app.route('/tasks/&lt;int:task_id&gt;', methods=['DELETE'])
def ochirish(task_id):
    # Vazifa: vazifani ro'yxatdan o'chirish
    pass</code></pre>

<pre><code># conftest.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        # Vazifa: har bir testdan keyin vazifalar ro'yxatini tozalang!</code></pre>

<h3>🐛 Ataylab qiyin: testlar orasida holat "sizib o'tishi" (test isolation)</h3>
<pre><code># ❌ conftest.py — tozalash YO'Q!
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # ❌ vazifalar ro'yxati testlar orasida TOZALANMAYDI!

# test_tasks.py
def test_royxat_bosh(client):
    javob = client.get('/tasks')
    assert javob.get_json() == []  # ❗ Bu test YOLG'IZ ishga tushsa — PASSED

def test_vazifa_yaratish(client):
    client.post('/tasks', json={"matn": "Non olish"})
    javob = client.get('/tasks')
    assert len(javob.get_json()) == 1</code></pre>

<p><strong>Natija:</strong> <code>test_royxat_bosh</code> alohida ishga tushirilsa — <strong>o'tadi</strong> (chunki ro'yxat hali bo'sh). Lekin <code>test_vazifa_yaratish</code>dan <strong>keyin</strong> ishga tushirilsa — <strong>FAILED</strong> bo'ladi! Chunki oldingi test qo'shgan vazifa hali ham global <code>vazifalar</code> ro'yxatida qolib ketgan. Bu — <strong>test isolation</strong> (testlar mustaqilligi) buzilishining klassik namunasi: testlar bir-biriga <strong>bog'liq</strong> bo'lib qoladi, ularning natijasi <strong>ishga tushirish tartibiga</strong> bog'liq bo'lib qoladi. 3-darsda ko'rgan <code>db.drop_all()</code> aynan shu muammoni hal qilgan edi — har bir test tugagach, holatni tozalash <strong>shart</strong>.</p>

<h3>Vazifalar</h3>

<h4>Vazifa 1 — to'liq CRUD + testlar</h4>
<p>Yuqoridagi skeletni to'ldiring, har bir endpoint uchun muvaffaqiyatli va xato holatlarni sinovdan o'tkazuvchi testlar yozing.</p>

<h4>Vazifa 2 — test izolyatsiyasi</h4>
<p>conftest.py'dagi <code>client</code> fixture'iga har bir testdan keyin <code>vazifalar</code> ro'yxatini tozalovchi kod qo'shing (<code>yield</code>dan keyin).</p>

<h4>Vazifa 3 — mock bilan bildirishnoma</h4>
<p>Vazifa yaratilganda tashqi xizmatga (masalan Telegram bot) bildirishnoma yuboruvchi funksiya qo'shing, uni testda <code>@patch</code> bilan almashtiring — haqiqiy tarmoqqa chiqmasdan.</p>

<h4>Vazifa 4 — TDD bilan yangi funksiya</h4>
<p><code>GET /tasks?bajarilmagan=true</code> — faqat bajarilmagan vazifalarni qaytaruvchi filtr. Avval test yozing (RED), keyin kodni yozing (GREEN).</p>

<h4>Vazifa 5 — coverage tekshiruvi</h4>
<p><code>pytest --cov=app --cov-report=term-missing</code> ishga tushiring, tekshirilmagan qatorlarni toping va ular uchun testlar qo'shing.</p>

<h3>📌 Bu loyihadan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-5-darslarning hammasi birga: fixture, mock, Flask testlash, TDD, coverage</li>
<li>✅ Test isolation (mustaqillik) — har bir test boshqalardan mustaqil, toza holatda ishlashi shart</li>
<li>✅ Testlar orasida holat "sizib o'tishi" — natijani ishga tushirish tartibiga bog'liq qiladigan xavfli xato</li>
<li>✅ To'liq testlangan kichik loyiha — portfolio uchun real ko'nikma namunasi</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# CAPSTONE: To'liq testlangan Flask API — boshlang'ich skelet
# ════════════════════════════════════════════════════════════════════

import pytest
from flask import Flask, jsonify, request
from unittest.mock import patch

app = Flask(__name__)
vazifalar = []


def bildirishnoma_yuborish(matn):
    # Haqiqiy loyihada bu yerda Telegram/email API chaqiriladi
    print(f"Bildirishnoma: {matn}")


@app.route('/tasks', methods=['GET'])
def royxat():
    bajarilmagan = request.args.get('bajarilmagan')
    if bajarilmagan == 'true':
        return jsonify([v for v in vazifalar if not v['bajarildi']])
    return jsonify(vazifalar)


@app.route('/tasks', methods=['POST'])
def yaratish():
    data = request.get_json()
    if not data.get('matn'):
        return jsonify({"xato": "'matn' majburiy"}), 400
    yangi = {"id": len(vazifalar) + 1, "matn": data['matn'], "bajarildi": False}
    vazifalar.append(yangi)
    bildirishnoma_yuborish(f"Yangi vazifa: {yangi['matn']}")
    return jsonify(yangi), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def yangilash(task_id):
    for v in vazifalar:
        if v['id'] == task_id:
            v['bajarildi'] = not v['bajarildi']
            return jsonify(v)
    return jsonify({"xato": "Topilmadi"}), 404


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def ochirish(task_id):
    global vazifalar
    oldingi_uzunlik = len(vazifalar)
    vazifalar = [v for v in vazifalar if v['id'] != task_id]
    if len(vazifalar) == oldingi_uzunlik:
        return jsonify({"xato": "Topilmadi"}), 404
    return '', 204


# ─────────────────────────────────────────────────────────────────────
# conftest.py — TO'G'RI izolyatsiya bilan
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    vazifalar.clear()  # ✅ har bir testdan keyin tozalash


# ─────────────────────────────────────────────────────────────────────
# test_tasks.py — to'liq test to'plami
# ─────────────────────────────────────────────────────────────────────

def test_royxat_bosh(client):
    javob = client.get('/tasks')
    assert javob.get_json() == []


def test_vazifa_yaratish(client):
    javob = client.post('/tasks', json={"matn": "Non olish"})
    assert javob.status_code == 201
    assert javob.get_json()["matn"] == "Non olish"


def test_vazifa_yaratish_xato(client):
    javob = client.post('/tasks', json={})
    assert javob.status_code == 400


@patch('app.bildirishnoma_yuborish')
def test_vazifa_yaratishda_bildirishnoma(mock_bildirish, client):
    client.post('/tasks', json={"matn": "Sut sotib olish"})
    mock_bildirish.assert_called_once()  # ✅ haqiqiy tarmoqqa chiqmasdan tekshiriladi


def test_bajarilmagan_filtri(client):
    client.post('/tasks', json={"matn": "1-vazifa"})
    client.post('/tasks', json={"matn": "2-vazifa"})
    client.put('/tasks/1')  # birinchisini bajarildi deb belgilash
    javob = client.get('/tasks?bajarilmagan=true')
    natijalar = javob.get_json()
    assert len(natijalar) == 1
    assert natijalar[0]['matn'] == "2-vazifa"


# ─────────────────────────────────────────────────────────────────────
# Ataylab xato — izolyatsiyasiz fixture (izohda)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client_xato():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#     # ❌ vazifalar.clear() YO'Q — keyingi test avvalgi ma'lumotni ko'radi!
"""

L6_EX = [
    {
        "title": "Test isolation nima uchun muhim?",
        "description": "Testlar orasida \"test isolation\" (mustaqillik) nima uchun muhim?",
        "exercise_type": "multiple_choice",
        "options": [
            "Testlar tezroq ishlashi uchun",
            "Har bir testning natijasi boshqa testlar ishga tushgan-tushmaganiga bog'liq bo'lmasligi uchun",
            "Kod chiroyliroq ko'rinishi uchun",
            "Faqat Flask uchun kerak, oddiy funksiyalar uchun kerak emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bir test boshqasiga \"ta'sir qilmasligi\" kerak.",
        "explanation": "Test isolation har bir testning mustaqil, boshqa testlar ishga tushgan-tushmaganiga yoki qanday tartibda ishga tushganiga bog'liq bo'lmasdan bir xil natija berishini ta'minlaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Global ro'yxat testlar orasida tozalanmasa nima bo'ladi?",
        "description": "Agar test fixture'i global vazifalar ro'yxatini har testdan keyin tozalamasa, bu nimaga olib kelishi mumkin?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech qanday muammo bo'lmaydi",
            "Testlar bir-biriga bog'liq bo'lib qoladi, natija ishga tushirish tartibiga bog'liq bo'ladi",
            "Testlar tezroq ishlaydi",
            "Faqat birinchi test ishlamay qoladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bir test qo'shgan ma'lumot keyingi testga \"o'tib qolishi\" mumkin.",
        "explanation": "Agar holat tozalanmasa, bir testda yaratilgan ma'lumot keyingi testga ta'sir qiladi — testlar mustaqil emas, bog'liq bo'lib qoladi, va natija ular qaysi tartibda ishga tushirilganiga bog'liq bo'lib qoladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Capstone loyihaning test yozish oqimini to'g'ri tartibda joylang",
        "description": "Yangi filtr funksiyasini TDD bilan qo'shish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "test_bajarilmagan_filtri() yoziladi (funksiya hali yo'q)",
            "pytest ishga tushiriladi — FAILED (RED)",
            "/tasks?bajarilmagan=true route'i yoziladi",
            "pytest qayta ishga tushiriladi — PASSED (GREEN)",
            "pytest --cov bilan coverage tekshiriladi",
        ],
        "correct_order": [
            "test_bajarilmagan_filtri() yoziladi (funksiya hali yo'q)",
            "pytest ishga tushiriladi — FAILED (RED)",
            "/tasks?bajarilmagan=true route'i yoziladi",
            "pytest qayta ishga tushiriladi — PASSED (GREEN)",
            "pytest --cov bilan coverage tekshiriladi",
        ],
        "hint": "TDD sikli: avval test, keyin kod, so'ng tekshiruv.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega test_royxat_bosh yolg'iz ishga tushsa PASSED, boshqasidan keyin FAILED bo'ladi?",
        "description": (
            "Agar conftest.py'dagi client fixture'i testlar orasida "
            "vazifalar ro'yxatini tozalamasa, test_royxat_bosh testi "
            "yolg'iz ishga tushirilganda nega o'tadi, lekin "
            "test_vazifa_yaratish'dan keyin ishga tushirilsa nega "
            "muvaffaqiyatsiz bo'ladi? Bu qanday muammoni ko'rsatadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "vazifalar — global (modul darajasidagi) ro'yxat, va agar "
            "fixture har testdan keyin uni tozalamasa, bir testda qo'shilgan "
            "ma'lumot xotirada saqlanib qoladi va keyingi testga \"o'tib "
            "qoladi\". test_royxat_bosh yolg'iz ishga tushirilganda ro'yxat "
            "hali bo'sh bo'lgani uchun assert javob == [] to'g'ri chiqadi. "
            "Lekin test_vazifa_yaratish'dan keyin ishga tushirilsa, o'sha "
            "testda qo'shilgan vazifa ro'yxatda qolib ketgani uchun ro'yxat "
            "endi bo'sh emas, va assert ishlamay qoladi. Bu — testlarning "
            "bir-biriga yashirin bog'liq bo'lib qolishi (test isolation "
            "yo'qligi) muammosini ko'rsatadi: testlarning natijasi ular "
            "qaysi tartibda ishga tushirilganiga bog'liq bo'lib qoladi, bu "
            "esa testlarni ishonchsiz va bashorat qilib bo'lmaydigan qiladi."
        ),
        "hint": "Global o'zgaruvchi testlar orasida \"tozalanmasa\", nima yuz beradi?",
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
                    [{"filename": f"test_app.{'py' if lang == 'python' else lang}",
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
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
