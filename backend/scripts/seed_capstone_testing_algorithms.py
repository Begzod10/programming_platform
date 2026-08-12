"""Seed "Capstone 5: Testlash va Algoritmlar" (7 lessons): combines Python:
Testlash and Python: Algoritmlar va Ma'lumotlar Tuzilmasi into ONE project —
'RankVault', a competitive leaderboard/ranking engine (Flask + PostgreSQL,
single deploy unit — no bot, no separate frontend framework, since the
focus here is correctness, not architecture).

Unlike Capstones 1-4, every lesson's deliberate bug belongs to a DIFFERENT
family: the bug isn't in the application code alone — it's in what the
TESTS (or the algorithm's untested edge cases) FAIL TO CATCH. A green test
suite, a high coverage percentage, and a "successful" CI run can all lie
about correctness. Each lesson shows this illusion in a different place
(faking-it TDD, shared-state flaky tests, unstable-sort tie-breaking,
coverage-without-correctness, mocks that hide a real failure path, and a
CI pipeline that exits 0 even when tests fail).

Uses the same project-submission mechanism as every other capstone via
task_title/task_description/task_requirements/task_technologies/
task_deadline_days on Lesson — students build ONE evolving 'RankVault' app
across all 7 milestones, resubmitting the same (updated) github_url each
time via the existing Submission + AI-grading pipeline (GitHub URL only —
see fix_capstone_final_github_only.py). No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_testing_algorithms
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.

Every lesson is authored bilingually in the same pass: Uzbek content goes
directly into the Lesson/Exercise rows (source_lang='uz'), Russian goes
directly into translation_cache via write_ru_translations.py (see the
matching scripts/ru_capstone5_lesson_0X.py for each lesson).

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
    "title": "Capstone 5: Testlash va Algoritmlar",
    "description": (
        "Python: Testlash va Python: Algoritmlar va Ma'lumotlar Tuzilmasi "
        "kurslarini tugatgan dasturchilar uchun: uchalasini emas, ikkalasini "
        "BIR loyihada birlashtirasiz. 7 bosqichda 'RankVault' — musobaqa "
        "reyting/ball tizimini (leaderboard) TDD (Red-Green-Refactor) "
        "orqali qurasiz: Flask + PostgreSQL, bot yo'q, alohida frontend "
        "freymvork yo'q — e'tibor arxitekturaga emas, TO'G'RILIKKA "
        "qaratilgan. Har bir bosqichda TypeScript-mavzusidagi capstone'dan "
        "farqli, boshqa chegara bilan tanishasiz: yashil test, yuqori "
        "coverage va muvaffaqiyatli CI — bularning barchasi HAQIQIY "
        "to'g'rilikni kafolatlamaydi. Har bir bosqich haqiqiy loyiha "
        "topshirig'i sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 8,  # Python
    "prerequisite_course_id": 76,  # Python: Testlash (also assumes course 78: Python: Algoritmlar va Ma'lumotlar Tuzilmasi)
    "is_active": True,
    "is_published": False,  # flip to True once all 7 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done", "lang": "python",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "TDD workflow policy, DB schema (users, scores), pytest+coverage tooling setup for RankVault."},
    {"order": 1, "ref": "L2", "status": "done", "lang": "python",
     "title": "2-Flask API + TDD asoslari",
     "scope": "Red-Green-Refactor on POST /scores; the 'faking it' TDD anti-pattern."},
    {"order": 2, "ref": "L3", "status": "done", "lang": "python",
     "title": "3-PostgreSQL CRUD + Fixture'lar",
     "scope": "conftest.py, isolated test DB; flaky order-dependent tests from shared state."},
    {"order": 3, "ref": "L4", "status": "done", "lang": "python",
     "title": "4-Ranking algoritmi",
     "scope": "Big O + sorting; unstable sort causing non-deterministic tie-breaking."},
    {"order": 4, "ref": "L5", "status": "done", "lang": "python",
     "title": "5-Test Coverage + Binary Search",
     "scope": "O(log n) rank lookup; high coverage % that never exercises boundary cases."},
    {"order": 5, "ref": "L6", "status": "done", "lang": "python",
     "title": "6-HashMap cache + Mocking",
     "scope": "O(1) rank cache; a mock that always succeeds, hiding a real failure path."},
    {"order": 6, "ref": "L7", "status": "done", "lang": "python",
     "title": "7-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "Full test suite as the final artifact; a CI script that exits 0 even when tests fail."},
]


L1_TEXT = """\
<h2>RankVault — 7 bosqichda testlash va algoritmlar orqali qurilgan loyiha</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> API["2-Flask API + TDD"]
    API --> DB["3-PostgreSQL + Fixture'lar"]
    DB --> RANK["4-Ranking algoritmi"]
    RANK --> COV["5-Coverage + Binary Search"]
    COV --> CACHE["6-HashMap + Mocking"]
    CACHE --> DEPLOY["7-Deploy (CAPSTONE yakuni)"]
</pre>

<p>Bu kursda siz Python: Testlash va Python: Algoritmlar va Ma'lumotlar Tuzilmasi kurslarida <strong>alohida</strong> o'rgangan hamma narsani <strong>bitta haqiqiy loyiha</strong>da birlashtirasiz: <strong>RankVault</strong> — musobaqa reyting/ball tizimi (leaderboard). Har bir dars — shu bitta loyihaning navbatdagi bosqichi.</p>

<p>Lekin bu capstone oldingi to'rttasidan bir narsa bilan farq qiladi: bu safar "ataylab xato" <strong>kodning o'zida</strong> emas — u <strong>testlarning</strong> yoki <strong>algoritmning tekshirilmagan holatlari</strong>ning <strong>yolg'on ishonch</strong> berishida yashiringan. Yashil test, yuqori coverage foizi, "muvaffaqiyatli" CI — bularning <strong>barchasi</strong> haqiqiy to'g'rilikni yolg'on tasdiqlashi mumkin. Har bir bosqich shu g'oyani yangi joyda ko'rsatadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo skeleton va TDD siyosati</h4>
<pre><code># RankVault uchun repo tuzilmasi
rankvault/
  app/
    __init__.py
    models.py
    routes.py
  tests/
    conftest.py        # ❗ 3-darsda to'ldiriladi - alohida test bazasi
    test_scores.py
  requirements.txt
  README.md
  .gitignore

# README.md'ga yoziladigan TDD siyosati:
# "Har bir yangi funksiya AVVAL test bilan boshlanadi (RED),
#  keyin uni o'tkazadigan eng oddiy kod yoziladi (GREEN),
#  so'ng kod tozalanadi (REFACTOR)."</code></pre>

<h4>BLOKA 2 — DB sxemasi: users va scores</h4>
<pre><code># RankVault uchun asosiy jadvallar (ER diagramma darajasida):
#
# users   (id, username, created_at)
# scores  (id, user_id -> users.id, points, submitted_at)
#
# Bog'lanish: bitta user -> ko'p scores (1 ga ko'p)
# - "reyting" - barcha userlarning ENG YUQORI (yoki umumiy) balli bo'yicha tartiblanishi</code></pre>

<h4>BLOKA 3 — pytest + pytest-cov + alohida test bazasi UCHUN JOY tayyorlash</h4>
<pre><code># requirements.txt
# flask
# psycopg2-binary
# pytest
# pytest-cov

# tests/conftest.py - HOZIRCHA skelet, 3-darsda to'ldiriladi
import pytest

@pytest.fixture
def client():
    # ❗ Bu yerga 3-darsda ALOHIDA test bazasiga ulanadigan
    # app konfiguratsiyasi qo'shiladi - hozircha placeholder.
    raise NotImplementedError("3-darsda to'ldiriladi")</code></pre>

<h3>🐛 Ataylab qiyin: test infratuzilmasini "keyinroq sozlayman" deb qoldirish</h3>
<p>TaskFlow'da (Capstone 1) DB sxemasisiz kod yozishga urinish muammo tug'dirgan edi. Bu yerda xuddi shunga o'xshash, lekin <strong>test infratuzilmasi</strong> haqida bo'lgan xato bor: ko'p dasturchilar <code>conftest.py</code>da alohida test bazasini (masalan <code>TEST_DATABASE_URL</code> orqali) <strong>loyiha boshida</strong> emas, "keyinroq, testlar ko'payganda" sozlashni rejalashtiradi:</p>
<pre><code># "Hozircha production bazasidan foydalanavoraman, keyin ajrataman" deb
# o'ylab, tests/conftest.py'ni bo'sh qoldirish yoki to'g'ridan-to'g'ri
# asosiy DATABASE_URL'ga ulash:
@pytest.fixture
def client():
    app.config['DATABASE_URL'] = os.environ['DATABASE_URL']  # ❗ PRODUCTION baza!
    return app.test_client()</code></pre>
<p><strong>Natija:</strong> hozircha (loyiha kichik, testlar kam bo'lganda) bu <strong>zararsiz</strong> ko'rinadi. Lekin 3-darsda testlar soni ko'payganda, bu qaror <strong>flaky (beqaror) testlar</strong>ga olib keladi — testlar bir-birining ma'lumotlariga ta'sir qiladi, ishga tushirish tartibiga qarab natija o'zgaradi. To'g'ri yondashuv: test infratuzilmasini (alohida baza, transaction rollback) <strong>loyiha boshidanoq</strong>, hali muammo yuzaga kelmasdan turib rejalashtirish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega bu capstone'dagi "ataylab xato"lar boshqa capstone'lardan farq qiladi?</h4>
<p>Oldingi to'rtta capstone'da xato har doim <strong>kodning o'zida</strong> edi (masalan noto'g'ri SQL, tekshiruvsiz cast). Bu yerda esa xato ko'pincha <strong>testlarning yoki algoritmning o'zida</strong> — kod "ishlab turgandek" ko'rinadi, testlar "yashil", lekin aslida biror muhim holat <strong>hech qachon sinovdan o'tkazilmagan</strong> yoki noto'g'ri sinovdan o'tkazilgan.</p>

<h4>2. Nega TDD siyosatini loyiha boshidanoq README'ga yozib qo'yish kerak?</h4>
<p>TDD (avval test, keyin kod) — bu <strong>odat</strong>, va odatlar loyiha boshida qat'iy belgilanmasa, loyiha kattalashgan sari "vaqt tejash" bahonasi bilan tashlab yuboriladi. README'ga yozib qo'yish — jamoaviy (yoki hatto yakka o'zi ishlaydigan) loyihada bu qoidani <strong>eslatib turuvchi</strong> hujjat vazifasini bajaradi.</p>

<h4>3. Nega alohida test bazasi (<code>TEST_DATABASE_URL</code>) boshidan rejalashtirilishi kerak?</h4>
<p>Agar testlar production (yoki development) bazasi bilan <strong>bir xil</strong> ma'lumotlar bazasida ishlasa, bir test yozgan/o'chirgan ma'lumot boshqa testga <strong>ta'sir qilishi</strong> mumkin. Bu — 3-darsda ko'radigan "flaky test" muammosining ildizi. Buni oldindan rejalashtirish keyinroq katta qayta qurishni oldini oladi.</p>

<h4>4. Nega aynan "reyting/ball tizimi" (leaderboard) tanlandi?</h4>
<p>Reyting hisoblash — tashqi ko'rinishda oddiy (userlarni ball bo'yicha tartiblash), lekin ichida <strong>ko'p nozik holatlar</strong> yashiringan: teng ballar qanday hal qilinadi, bo'sh ro'yxat qanday ishlov ko'radi, katta hajmda tezlik qanday ta'minlanadi. Bu — algoritmlar (tartiblash, qidiruv, hash) va testlash (chekka holatlarni qamrab olish) uchun <strong>boy</strong> material.</p>

<h4>5. Bu 7 bosqichning umumiy yo'nalishi nima?</h4>
<p>Har bir bosqich — "yashil belgi" (✅ test o'tdi, ✅ coverage yuqori, ✅ CI muvaffaqiyatli) <strong>haqiqiy to'g'rilikni</strong> avtomatik kafolatlamasligini, turli ko'rinishda ko'rsatadi. Capstone oxirida siz nafaqat testlashni, balki <strong>testlarning o'ziga qanday ishonmaslik kerakligini</strong> ham o'rganasiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Bu capstone'dagi xatolar kodda emas, ko'pincha testlar yoki tekshirilmagan holatlarda yashiringan</li>
<li>✅ TDD siyosatini README'ga yozib qo'yish — loyiha kattalashganda uni eslatib turadi</li>
<li>✅ Alohida test bazasi loyiha boshidanoq rejalashtirilishi kerak — keyinroq flaky testlarning oldini oladi</li>
<li>✅ Reyting/ball tizimi — algoritmlar va testlash uchun boy, nozik holatlarga to'la material</li>
<li>✅ Bu kursda "yashil belgi" (test o'tdi, coverage yuqori, CI muvaffaqiyatli) har doim haqiqiy to'g'rilik degani emas</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 1-BOSQICH: Loyihalash va repo skeleton
# ════════════════════════════════════════════════════════════════════

# Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.
# Quyida - RankVault uchun DB sxemasi va test skeleti:

# ─────────────────────────────────────────────────────────────────────
# schema.sql (hali haqiqiy migratsiya emas - 3-darsda bo'ladi)
# ─────────────────────────────────────────────────────────────────────

# CREATE TABLE users (
#   id SERIAL PRIMARY KEY,
#   username VARCHAR(50) UNIQUE NOT NULL,
#   created_at TIMESTAMP DEFAULT NOW()
# );
#
# CREATE TABLE scores (
#   id SERIAL PRIMARY KEY,
#   user_id INTEGER REFERENCES users(id),
#   points INTEGER NOT NULL,
#   submitted_at TIMESTAMP DEFAULT NOW()
# );

# ─────────────────────────────────────────────────────────────────────
# tests/conftest.py - skelet, 3-darsda to'ldiriladi
# ─────────────────────────────────────────────────────────────────────

import pytest


@pytest.fixture
def client():
    # 3-darsda: ALOHIDA test bazasiga ulanadigan konfiguratsiya
    # shu yerga qo'shiladi (TEST_DATABASE_URL orqali).
    raise NotImplementedError("3-darsda to'ldiriladi")


# ─────────────────────────────────────────────────────────────────────
# Ataylab qiyin - production bazasiga ulanadigan fixture (izohda)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def client():
#     app.config['DATABASE_URL'] = os.environ['DATABASE_URL']  # PRODUCTION!
#     return app.test_client()
# Hozircha zararsiz ko'rinadi, lekin testlar ko'paygach flaky bo'ladi.
"""

L1_EX = [
    {
        "title": "Bu capstone'dagi xatolar nimada yashiringan?",
        "description": "RankVault capstone'sida 'ataylab xato'lar odatda qayerda yashiringan bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim SQL so'rovlarida",
            "Ko'pincha testlarning o'zida yoki algoritmning tekshirilmagan holatlarida - kod 'ishlab turgandek' ko'rinadi",
            "Har doim frontend kodida",
            "Har doim autentifikatsiya kodida",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu capstone testlash va algoritmlarga bag'ishlangan.",
        "explanation": "Bu capstone'da xato ko'pincha testlarning yoki algoritmning o'zida yashiringan - kod ishlayotgandek, testlar yashil ko'rinadi, lekin muhim holat hech qachon to'g'ri sinovdan o'tkazilmagan.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega alohida test bazasi kerak?",
        "description": "Testlarni production/development bazasi bilan bir xil bazada ishlatish nega muammoli?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu texnik jihatdan umuman ishlamaydi",
            "Bitta test yozgan/o'chirgan ma'lumot boshqa testga ta'sir qilib, natija ishga tushirish tartibiga qarab o'zgarishi (flaky test) mumkin",
            "Chunki bu PostgreSQL'ning cheklovi",
            "Chunki bu faqat pullik hosting'larda muammo",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Testlar bir-birining ma'lumotiga ta'sir qilishi mumkinmi?",
        "explanation": "Agar testlar bir xil bazada ishlasa, bitta testning ma'lumoti boshqa testga ta'sir qilishi mumkin - bu testlarni ishga tushirish tartibiga qarab natija o'zgaradigan, 'flaky' qiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "RankVault'ni rejalashtirish jarayonini tartiblang",
        "description": "RankVault uchun 1-bosqichning to'g'ri rejalashtirish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "README'ga TDD siyosati (avval test, keyin kod) yoziladi",
            "users va scores jadvallari uchun DB sxemasi loyihalanadi",
            "pytest, pytest-cov requirements.txt'ga qo'shiladi",
            "tests/conftest.py skeleti yaratiladi (alohida test bazasi uchun joy qoldirilib)",
        ],
        "correct_order": [
            "README'ga TDD siyosati (avval test, keyin kod) yoziladi",
            "users va scores jadvallari uchun DB sxemasi loyihalanadi",
            "pytest, pytest-cov requirements.txt'ga qo'shiladi",
            "tests/conftest.py skeleti yaratiladi (alohida test bazasi uchun joy qoldirilib)",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TDD siklining uch bosqichi",
        "description": "TDD (Test Driven Development) siklining uch bosqichini ketma-ket, vergul bilan ajratib yozing (masalan: X, Y, Z).",
        "exercise_type": "text_input",
        "expected_answer": "RED, GREEN, REFACTOR",
        "hint": "Avval muvaffaqiyatsiz test, keyin uni o'tkazadigan kod, so'ng tozalash.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega test infratuzilmasini keyinga qoldirish xavfli?",
        "description": (
            "Agar dasturchi alohida test bazasini sozlashni \"loyiha "
            "kichik hali, keyinroq qilaman\" deb keyinga qoldirsa, bu "
            "keyinchalik qanday muammoga olib kelishi mumkin? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Loyiha kichik va testlar kam bo'lganda, production/development "
            "bazasidan foydalanish zararsiz ko'rinadi. Lekin testlar soni "
            "ko'paygan sari, turli testlar bir xil bazadagi bir xil "
            "ma'lumotlarni o'qib/yozib, bir-biriga ta'sir qila boshlaydi - "
            "natijada testlar ishga tushirish TARTIBIGA qarab har xil "
            "natija berishi mumkin (flaky testlar). Bu holatni loyiha "
            "kattalashib ketgandan keyin tuzatish, boshidanoq alohida test "
            "bazasi va transaction rollback mexanizmini qurishga qaraganda "
            "ancha ko'proq vaqt va qayta qurishni talab qiladi."
        ),
        "hint": "Loyiha kichik bo'lganda bu qaror zararsiz ko'rinadi - nega?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "RankVault — repo skeleton va TDD siyosati hujjati",
    "task_description": (
        "RankVault loyihasi uchun GitHub'da repo yarating (app/ va tests/ "
        "papkalari bilan), to'liq README.md yozing (TDD siyosati va "
        "users/scores jadvallari sxemasi bilan), va pytest + pytest-cov "
        "o'rnatilgan tests/conftest.py skeletini yarating."
    ),
    "task_requirements": (
        "• GitHub'da 'rankvault' nomli public repo yaratilgan\n"
        "• app/ va tests/ papkalari mavjud\n"
        "• README.md: loyiha tavsifi, TDD siyosati (RED-GREEN-REFACTOR), texnologiyalar, holat checklist'i\n"
        "• README.md ichida users va scores jadvallari va ular orasidagi bog'lanish tasvirlangan\n"
        "• requirements.txt: flask, psycopg2-binary, pytest, pytest-cov qo'shilgan\n"
        "• tests/conftest.py skeleti mavjud (hozircha NotImplementedError bilan)\n"
        "• .gitignore fayli mavjud (venv, __pycache__, .env chiqarib tashlangan)"
    ),
    "task_technologies": "Python, Flask, pytest, pytest-cov, PostgreSQL, Git, GitHub",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Flask API + TDD asoslari — RED-GREEN-REFACTOR va "firib berish" xatosi</h2>

<pre class="mermaid">
flowchart LR
    RED["RED: muvaffaqiyatsiz test yoziladi"] --> GREEN{"GREEN: testni qanday o'tkazamiz?"}
    GREEN -->|"Haqiqiy, umumiy logika"| REAL["Har qanday kirish uchun ishlaydi"]
    GREEN -->|"Faqat kutilgan qiymatni qattiq yozish"| FAKE["'Firib berish' - FAQAT shu bitta holat uchun ishlaydi"]
    FAKE --> HIDDEN["Bitta test bilan bu firibgarlik sezilmay qoladi"]
</pre>

<p>Python: Testlash kursida pytest asoslarini va TDD (Red-Green-Refactor) siklini allaqachon o'rgangansiz. Bu darsda ularni RankVault'ning birinchi haqiqiy endpoint'iga — <code>POST /scores</code>ga — qo'llaysiz. Lekin bu yerda TDD'ning eng ko'p tushunmaydigan joyi ochiladi: GREEN bosqichida "testni o'tkazadigan ENG ODDIY kod" yozish tavsiyasi, agar noto'g'ri tushunilsa, <strong>"firib berish" (faking it)</strong> degan xatoga aylanib qolishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — RED: avval muvaffaqiyatsiz test yoziladi</h4>
<pre><code># tests/test_scores.py
def test_post_score_returns_created_score(client):
    response = client.post('/scores', json={'user_id': 1, 'points': 100})
    assert response.status_code == 201
    assert response.get_json()['points'] == 100

# Bu bosqichda /scores endpoint umuman yo'q - test albatta MUVAFFAQIYATSIZ
# bo'ladi (404 yoki xato). Bu - RED. Testning HAQIQATAN muvaffaqiyatsiz
# bo'lishini ko'rish MUHIM - aks holda test hech narsani sinamayotgan
# bo'lishi ham mumkin.</code></pre>

<h4>BLOKA 2 — GREEN: testni o'tkazadigan HAQIQIY, umumiy kod</h4>
<pre><code># app/routes.py
from flask import request, jsonify
from app import app, db
from app.models import Score

@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    score = Score(user_id=data['user_id'], points=data['points'])
    db.session.add(score)
    db.session.commit()
    return jsonify({'id': score.id, 'points': score.points}), 201</code></pre>

<h4>BLOKA 3 — Triangulation: IKKINCHI test bilan umumiylikni tasdiqlash</h4>
<pre><code># tests/test_scores.py - IKKINCHI, boshqa qiymatlar bilan test qo'shiladi
def test_post_score_with_different_values(client):
    response = client.post('/scores', json={'user_id': 2, 'points': 250})
    assert response.status_code == 201
    assert response.get_json()['points'] == 250

# Agar kod HAQIQIY logika bo'lsa, bu test HAM avtomatik o'tadi -
# chunki funksiya istalgan kirish uchun ishlaydi. Bu - "triangulation":
# bir nechta har xil test holati orqali, kodning FAQAT bitta holatga
# emas, UMUMIY yechimga majburlanishi.</code></pre>

<h3>🐛 Ataylab xato — "firib berish" (faking it): faqat kutilgan qiymatni qattiq yozish</h3>
<pre><code># "Testni eng oddiy usulda o'tkazaman" deb, HAQIQIY logika o'rniga -
# faqat test kutayotgan aniq qiymatlarni qattiq yozib qo'yish:
@app.route('/scores', methods=['POST'])
def create_score():
    return jsonify({'id': 1, 'points': 100}), 201   # ❌ QATTIQ YOZILGAN!
    # Hech qanday DB yozuvi yo'q, request.get_json() umuman o'qilmaydi!

# BLOKA 1'dagi yagona test bilan bu kod TO'LIQ "yashil" o'tadi:
# ✅ test_post_score_returns_created_score PASSED
#
# Lekin bu endpoint aslida HECH NARSA qilmaydi - u istalgan so'rovga
# har doim BIR XIL { "id": 1, "points": 100 } javobini qaytaradi.
# Ma'lumot hech qachon bazaga saqlanmaydi!</code></pre>

<p><strong>Natija:</strong> "firib berish" (faking it) — TDD'da GREEN bosqichini <strong>noto'g'ri</strong> tushunishdan kelib chiqadigan xato: "eng oddiy kod" degani "test kutayotgan qiymatni qattiq yozish" degani <strong>emas</strong> — bu "har qanday to'g'ri kirish uchun ishlaydigan, eng oddiy <strong>umumiy</strong> yechim" degani. Agar loyihada faqat <strong>bitta</strong> test holati bo'lsa, bu ikkalasi orasidagi farq <strong>ko'rinmaydi</strong> — ikkalasi ham testni "yashil" qiladi. Farq faqat <strong>ikkinchi, boshqa qiymatlar bilan</strong> test qo'shilganda ko'rinadi: qattiq yozilgan kod ikkinchi testda albatta <strong>muvaffaqiyatsiz</strong> bo'ladi, chunki u faqat bitta holatni "yodlab olgan".</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega RED bosqichida testning HAQIQATAN muvaffaqiyatsiz bo'lishini ko'rish shart?</h4>
<p>Agar test yozilgach darhol "yashil" chiqsa (masalan yozuv xatosi tufayli test hech narsani tekshirmayotgan bo'lsa), bu testning <strong>o'zi</strong> ishonchsiz ekanini bildiradi. RED bosqichini ko'rish — test <strong>haqiqatan</strong> kerakli narsani tekshirayotganiga ishonch hosil qilish usuli.</p>

<h4>2. "Eng oddiy kod" va "firib berish" orasidagi farq nima?</h4>
<p>"Eng oddiy kod" — testni o'tkazadigan, lekin <strong>haqiqiy, umumiy</strong> mantiq (masalan kirish ma'lumotini bazaga saqlash). "Firib berish" — testni faqat <strong>aniq kutilgan qiymatlarni qattiq yozib</strong> o'tkazish, hech qanday umumiy mantiqsiz. Ikkalasi ham "oddiy" ko'rinadi, lekin faqat biri <strong>haqiqatan ishlaydi</strong>.</p>

<h4>3. Nega bitta test yetarli emas — "triangulation" nima?</h4>
<p>Bitta test holati bilan "firib berish" va haqiqiy yechim <strong>farqlanmaydi</strong>. Ikkinchi, <strong>boshqa</strong> qiymatlar bilan test qo'shilganda, qattiq yozilgan "firibgarlik" kodi albatta buziladi — bu dasturchini <strong>umumiy</strong> yechim yozishga "majburlaydi". Bu texnika — <strong>triangulation</strong> deb ataladi.</p>

<h4>4. REFACTOR bosqichi firibgarlikni har doim fosh qiladimi?</h4>
<p><strong>Yo'q</strong> — agar loyihada hali ham faqat bitta test bo'lsa, REFACTOR bosqichida ham hech kim buni sezmasligi mumkin, chunki kod baribir "yashil" turadi. Firibgarlik faqat <strong>yangi, boshqa holat</strong> bilan test qo'shilganda aniqlanadi.</p>

<h4>5. Bu real loyihada qanday oqibatga olib keladi?</h4>
<p>Agar boshqa dasturchi (yoki keyingi darsda — siz o'zingiz) <code>/scores</code> endpoint'i <strong>haqiqatan</strong> ma'lumotni saqlaydi deb ishonib, ustiga qurishni boshlasa (masalan reyting hisoblash — 4-darsda), lekin aslida hech narsa bazaga yozilmagan bo'lsa, bu <strong>keyingi bosqichlarda</strong> tushunarsiz, "ma'lumot yo'qolgan" kabi xatolarga olib keladi — bu xatoning haqiqiy manbai (qattiq yozilgan endpoint) esa <strong>ancha oldin</strong> yashiringan bo'ladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ RED bosqichida testning haqiqatan muvaffaqiyatsiz bo'lishini ko'rish — testning o'ziga ishonch hosil qilish usuli</li>
<li>✅ "Eng oddiy kod" — umumiy, haqiqiy mantiq, "qattiq yozilgan qiymat" emas</li>
<li>✅ Bitta test holati "firib berish" va haqiqiy yechimni farqlay olmaydi</li>
<li>✅ Triangulation — bir nechta har xil test holati orqali kodni umumiy yechimga majburlash</li>
<li>✅ Qattiq yozilgan "firibgarlik" faqat yangi test qo'shilganda fosh bo'ladi — bu safargacha xavfli, yashirin holatda qoladi</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 2-BOSQICH: Flask API + TDD asoslari
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) tests/test_scores.py - RED, keyin triangulation uchun 2-test
# ─────────────────────────────────────────────────────────────────────

def test_post_score_returns_created_score(client):
    response = client.post('/scores', json={'user_id': 1, 'points': 100})
    assert response.status_code == 201
    assert response.get_json()['points'] == 100


def test_post_score_with_different_values(client):
    response = client.post('/scores', json={'user_id': 2, 'points': 250})
    assert response.status_code == 201
    assert response.get_json()['points'] == 250


# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - GREEN: haqiqiy, umumiy kod
# ─────────────────────────────────────────────────────────────────────

from flask import request, jsonify
from app import app, db
from app.models import Score


@app.route('/scores', methods=['POST'])
def create_score():
    data = request.get_json()
    score = Score(user_id=data['user_id'], points=data['points'])
    db.session.add(score)
    db.session.commit()
    return jsonify({'id': score.id, 'points': score.points}), 201


# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - "firib berish" (izohda)
# ─────────────────────────────────────────────────────────────────────

# @app.route('/scores', methods=['POST'])
# def create_score():
#     return jsonify({'id': 1, 'points': 100}), 201   # qattiq yozilgan!
#     # request.get_json() umuman o'qilmaydi, DB'ga hech narsa yozilmaydi.
#
# Yagona test bilan bu "yashil" o'tadi - lekin ikkinchi, boshqa
# qiymatlar bilan test qo'shilsa, albatta muvaffaqiyatsiz bo'ladi.
"""

L2_EX = [
    {
        "title": "RED bosqichida test nega HAQIQATAN muvaffaqiyatsiz bo'lishi kerak?",
        "description": "TDD'ning RED bosqichida yozilgan testning darhol emas, HAQIQATAN muvaffaqiyatsiz bo'lishini ko'rish nima uchun muhim?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bu shunchaki TDD qoidasi, boshqa sababi yo'q",
            "Test haqiqatan kerakli narsani tekshirayotganiga ishonch hosil qilish uchun - aks holda test hech narsani sinamayotgan bo'lishi mumkin",
            "Chunki pytest boshqa tartibda ishlamaydi",
            "Muvaffaqiyatsiz test tezroq ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agar test yozilgach darhol yashil chiqsa, bu nimani anglatishi mumkin?",
        "explanation": "RED bosqichini ko'rish - test haqiqatan kerakli narsani tekshirayotganiga ishonch hosil qilish usuli. Agar test yozilishi bilanoq yashil chiqsa, ehtimol u hech narsani to'g'ri tekshirmayotgan bo'lishi mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "'Eng oddiy kod' va 'firib berish' orasidagi farq",
        "description": "TDD'ning GREEN bosqichida tavsiya etilgan 'eng oddiy kod' bilan 'firib berish' (faking it) orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Farqi yo'q, ikkalasi bir xil narsa",
            "'Eng oddiy kod' - umumiy, haqiqiy mantiq; 'firib berish' - faqat kutilgan qiymatni qattiq yozish, hech qanday umumiy mantiqsiz",
            "'Firib berish' har doim tezroq ishlaydi",
            "'Eng oddiy kod' faqat Flask'da, 'firib berish' faqat Django'da ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ikkalasi ham 'oddiy' ko'rinadi, lekin faqat biri haqiqatan ishlaydi.",
        "explanation": "'Eng oddiy kod' - testni o'tkazadigan, lekin haqiqiy, umumiy mantiq. 'Firib berish' esa faqat aniq kutilgan qiymatlarni qattiq yozib testni o'tkazish - hech qanday umumiy mantiqsiz.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "TDD siklini to'g'ri tartibda joylang (triangulation bilan)",
        "description": "POST /scores endpoint'ini TDD orqali, triangulation yordamida qurish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Birinchi test yoziladi (RED) - /scores hali mavjud emas",
            "Testni o'tkazadigan kod yoziladi (GREEN)",
            "Ikkinchi, boshqa qiymatlar bilan test qo'shiladi (triangulation)",
            "Agar ikkinchi test ham avtomatik o'tsa, kod umumiy ekanligi tasdiqlanadi",
        ],
        "correct_order": [
            "Birinchi test yoziladi (RED) - /scores hali mavjud emas",
            "Testni o'tkazadigan kod yoziladi (GREEN)",
            "Ikkinchi, boshqa qiymatlar bilan test qo'shiladi (triangulation)",
            "Agar ikkinchi test ham avtomatik o'tsa, kod umumiy ekanligi tasdiqlanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bir nechta test holati orqali kodni umumiy yechimga majburlash usuli",
        "description": "TDD'da bir nechta har xil test holatlari orqali kodni 'firib berish'dan umumiy yechimga majburlash texnikasining nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "triangulation",
        "hint": "Bu so'z geometriyadagi \"uchburchaklash\" so'zidan olingan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega 'firib berish' xatosi real loyihada xavfli?",
        "description": (
            "Agar /scores endpoint'i aslida hech narsani bazaga "
            "saqlamasdan, faqat qattiq yozilgan qiymat qaytarsa, va "
            "boshqa dasturchi bu endpoint ustiga (masalan reyting "
            "hisoblash funksiyasini) qura boshlasa, bu qanday oqibatga "
            "olib kelishi mumkin? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar /scores endpoint'i \"firib berish\" orqali yozilgan bo'lsa, "
            "u hech qanday ma'lumotni bazaga saqlamaydi - faqat bitta "
            "yagona, qattiq yozilgan javobni qaytaradi. Agar boshqa "
            "dasturchi (yoki keyingi darsda o'zi) bu endpoint HAQIQATAN "
            "ma'lumotni saqlaydi deb ishonib, uning ustiga reyting hisoblash "
            "kabi funksiyalarni qura boshlasa, keyingi bosqichlarda "
            "\"ma'lumot yo'qolgan\", \"reyting noto'g'ri hisoblanmoqda\" kabi "
            "tushunarsiz xatolar paydo bo'ladi - va bu xatolarning haqiqiy "
            "manbai (dastlabki qattiq yozilgan, ishlamaydigan endpoint) "
            "ancha oldin, ko'rinmas holda qolgan bo'ladi, uni topish qiyin "
            "bo'ladi."
        ),
        "hint": "Endpoint aslida ma'lumotni saqlamasa, keyingi funksiyalar qanday ma'lumotga tayanadi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "RankVault — Flask API + TDD asoslari (POST /scores)",
    "task_description": (
        "TDD (RED-GREEN-REFACTOR) siklidan foydalanib POST /scores "
        "endpoint'ini yozing. Kamida IKKITA har xil qiymat bilan test "
        "yozing (triangulation) — kod faqat bitta holatni emas, HAR "
        "QANDAY to'g'ri kirishni qabul qilishi va bazaga saqlashi shart."
    ),
    "task_requirements": (
        "• tests/test_scores.py: kamida 2 ta har xil qiymat bilan test (triangulation)\n"
        "• POST /scores — haqiqiy, umumiy mantiq bilan yozilgan (qattiq yozilgan qiymat EMAS)\n"
        "• Har bir POST so'rovi Score jadvaliga haqiqatan yozuv qo'shishi tasdiqlangan\n"
        "• Git commit tarixida RED (muvaffaqiyatsiz test) va GREEN (o'tgan test) bosqichlari ko'rinadi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Python, Flask, pytest, TDD",
    "task_deadline_days": 4,
}


L3_TEXT = """\
<h2>3-bosqich: PostgreSQL CRUD + Fixture'lar — flaky (beqaror) testlar</h2>

<pre class="mermaid">
flowchart LR
    T1["test_get_scores_empty ishga tushadi - bazada 0 ta yozuv"] --> DB[("Bitta umumiy test bazasi")]
    T2["test_post_score keyin ishga tushadi - 1 ta yozuv qo'shadi"] --> DB
    DB --> T3["test_get_scores_empty QAYTA ishga tushirilsa - ENDI muvaffaqiyatsiz!"]
</pre>

<p>1-darsda <code>tests/conftest.py</code>ni "keyinroq to'ldiramiz" deb qoldirgan edik — mana shu daqiqa keldi. Python: Testlash kursida <code>@pytest.fixture</code>, <code>conftest.py</code> va <code>app.test_client()</code>ni allaqachon o'rgangansiz. Bu darsda ularni RankVault'ga qo'llaymiz — va 1-darsda ogohlantirilgan xavfning aynan o'zini <strong>jonli</strong> ko'ramiz: alohida test bazasi bo'lsa ham, agar testlar orasida ma'lumot <strong>tozalanmasa</strong>, testlar baribir bir-biriga ta'sir qiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — conftest.py'ni to'ldirish: alohida test bazasi</h4>
<pre><code># tests/conftest.py
import pytest
from app import create_app, db as _db

@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])   # ❗ ALOHIDA baza!
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()</code></pre>

<h4>BLOKA 2 — HAR BIR test uchun TOZA holat: avtomatik tozalash fixture'i</h4>
<pre><code># tests/conftest.py - davomi
@pytest.fixture(autouse=True)
def clean_tables(app):
    yield   # ❗ avval test ishga tushadi
    with app.app_context():
        _db.session.query(Score).delete()   # ❗ HAR bir testdan KEYIN tozalanadi
        _db.session.query(User).delete()
        _db.session.commit()</code></pre>

<h4>BLOKA 3 — GET /scores uchun to'liq test, toza holatga tayanib</h4>
<pre><code># tests/test_scores.py
def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.status_code == 200
    assert response.get_json() == []   # ❗ Bo'sh baza kutiladi

def test_get_scores_after_post(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    response = client.get('/scores')
    assert len(response.get_json()) == 1</code></pre>

<h3>🐛 Ataylab xato — alohida baza BOR, lekin tozalash YO'Q</h3>
<pre><code># conftest.py - ALOHIDA test bazasiga ulangan (to'g'ri!), lekin
# `clean_tables` fixture'i YOZILMAGAN - testlar orasida ma'lumot qoladi:
@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()   # ❗ Bu FAQAT butun test SESSIYASI oxirida ishlaydi!

@pytest.fixture
def client(app):
    return app.test_client()
# ❌ Testlar orasida hech narsa TOZALANMAYDI!

# tests/test_scores.py - ikkita test, KETMA-KET yoziladi:
def test_post_score(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    # bu yozuv bazada QOLIB KETADI

def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.get_json() == []   # ❌ Agar test_post_score OLDIN
    # ishga tushgan bo'lsa, bazada ALLAQACHON 1 ta yozuv bor - bu test
    # MUVAFFAQIYATSIZ bo'ladi!

# Lekin agar pytest ularni TESKARI tartibda ishga tushirsa (masalan
# fayl ichida boshqa joylashuv, yoki -p no:randomly o'chirilgan holda),
# ikkalasi ham "yashil" bo'lib ko'rinishi mumkin!</code></pre>

<p><strong>Natija:</strong> alohida test bazasiga ulanish (<code>TEST_DATABASE_URL</code>) — bu <strong>zarur</strong>, lekin <strong>yetarli emas</strong>. Agar testlar orasida jadvallar tozalanmasa, bitta test yozgan ma'lumot <strong>keyingi</strong> testga "sizib o'tadi". Bunday testlar <strong>flaky</strong> (beqaror) deyiladi — ular <strong>qanday tartibda</strong> ishga tushirilishiga qarab har xil natija berishi mumkin. Bugun "yashil" bo'lgan test suite ertaga, boshqa tartibda ishga tushirilganda, <strong>hech qanday kod o'zgarishisiz</strong> "qizil" bo'lib qolishi mumkin — bu esa dasturchilarni chalg'itadi: "nima o'zgardi?" degan savol tug'iladi, aslida hech narsa o'zgarmagan, faqat testlar tartibi boshqacha bo'lgan.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega alohida test bazasi (<code>TEST_DATABASE_URL</code>) yetarli emas?</h4>
<p>Alohida baza faqat <strong>testlarni production'dan</strong> ajratadi — bu muhim, lekin u testlarning <strong>bir-biridan</strong> ajratilishini kafolatlamaydi. Agar barcha testlar bitta test bazasini <strong>baham ko'rsa</strong> va hech kim uni tozalamasa, testlar hamon bir-biriga ta'sir qiladi — faqat endi production emas, balki <strong>boshqa testlar</strong> ta'sirlanadi.</p>

<h4>2. <code>autouse=True</code> bilan yozilgan <code>clean_tables</code> fixture'i nima qiladi?</h4>
<p><code>autouse=True</code> — bu fixture <strong>har bir</strong> test uchun avtomatik ishlatilishini bildiradi, uni alohida chaqirish shart emas. <code>yield</code>dan keyingi kod har bir testdan <strong>keyin</strong> ishga tushadi — bu yerda jadvallarni tozalash orqali, keyingi test har doim <strong>toza</strong> holatdan boshlanishini ta'minlaydi.</p>

<h4>3. Nega flaky testlar ayniqsa xavfli?</h4>
<p>Oddiy, doimiy muvaffaqiyatsiz test darhol e'tiborni tortadi va tuzatiladi. Flaky test esa <strong>vaqti-vaqti bilan</strong> muvaffaqiyatsiz bo'lgani uchun, dasturchilar ko'pincha uni "tasodifiy xato" deb <strong>e'tiborsiz qoldiradilar</strong> yoki qayta ishga tushirib "o'tib ketishini" kutadilar — bu esa haqiqiy, jiddiy muammolarni ham "tasodifiy xato" fonida yashirib qo'yishi mumkin.</p>

<h4>4. Nega bu muammo ba'zan ko'rinmaydi, ba'zan ko'rinadi?</h4>
<p>Test tartibi <strong>determinist</strong> emas — pytest standart holda fayllarni alifbo tartibida ishga tushiradi, lekin plagin (masalan <code>pytest-randomly</code>) yoki testlarni tanlab ishga tushirish tartibni <strong>o'zgartirishi</strong> mumkin. Shu sababli xato faqat <strong>ma'lum</strong> tartibda paydo bo'ladi — bu uni topishni yanada qiyinlashtiradi.</p>

<h4>5. Bu 1-darsdagi "ataylab qiyin" bilan qanday bog'liq?</h4>
<p>1-darsda biz "test infratuzilmasini keyinga qoldirish" xavfli ekanini <strong>nazariy</strong> tarzda ko'rgan edik. Bu darsda esa siz uni <strong>jonli</strong> ko'rdingiz: hatto alohida baza to'g'ri sozlangan bo'lsa ham, agar <strong>tozalash</strong> mexanizmi bo'lmasa, xavf baribir yuzaga keladi — bu shuni ko'rsatadiki, test infratuzilmasi <strong>bir martalik sozlash</strong> emas, balki har bir yangi test yozilganda <strong>e'tiborda tutilishi</strong> kerak bo'lgan doimiy amaliyot.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Alohida test bazasi zarur, lekin yetarli emas — testlar orasidagi ma'lumot ham tozalanishi shart</li>
<li>✅ <code>autouse=True</code> fixture — har bir testdan keyin avtomatik tozalash uchun ishlatiladi</li>
<li>✅ Flaky testlar tartibga qarab har xil natija beradi — bu ularni ayniqsa xavfli va aniqlash qiyin qiladi</li>
<li>✅ Test tartibi determinist emas — plagin yoki tanlab ishga tushirish uni o'zgartirishi mumkin</li>
<li>✅ Test infratuzilmasi bir martalik sozlash emas, har doim e'tiborda tutilishi kerak bo'lgan amaliyot</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 3-BOSQICH: PostgreSQL CRUD + Fixture'lar
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) tests/conftest.py - alohida test bazasi + avtomatik tozalash
# ─────────────────────────────────────────────────────────────────────

import os
import pytest
from app import create_app, db as _db
from app.models import Score, User


@pytest.fixture
def app():
    app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_tables(app):
    yield
    with app.app_context():
        _db.session.query(Score).delete()
        _db.session.query(User).delete()
        _db.session.commit()


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_scores.py - GET /scores, toza holatga tayanib
# ─────────────────────────────────────────────────────────────────────

def test_get_scores_empty_list(client):
    response = client.get('/scores')
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_scores_after_post(client):
    client.post('/scores', json={'user_id': 1, 'points': 100})
    response = client.get('/scores')
    assert len(response.get_json()) == 1


# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - tozalashsiz conftest.py (izohda)
# ─────────────────────────────────────────────────────────────────────

# @pytest.fixture
# def app():
#     app = create_app(database_url=os.environ['TEST_DATABASE_URL'])
#     with app.app_context():
#         _db.create_all()
#         yield app
#         _db.drop_all()   # faqat BUTUN sessiya oxirida!
# # clean_tables fixture'i UMUMAN YO'Q - testlar orasida ma'lumot qoladi,
# # natija test ishga tushirish TARTIBIGA qarab o'zgaradi (flaky).
"""

L3_EX = [
    {
        "title": "Nega alohida test bazasi yetarli emas?",
        "description": "TEST_DATABASE_URL orqali alohida test bazasiga ulanish nima uchun flaky testlarning oldini olish uchun YETARLI emas?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki PostgreSQL alohida bazalarni qo'llab-quvvatlamaydi",
            "Alohida baza testlarni production'dan ajratadi, lekin testlarning bir-biridan ajratilishini (ma'lumot tozalanishini) kafolatlamaydi",
            "Chunki alohida baza sekinroq ishlaydi",
            "Chunki bu faqat MySQL uchun ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Alohida baza NIMADAN ajratadi, va NIMANI hali ham baham ko'radi?",
        "explanation": "Alohida test bazasi testlarni production ma'lumotlaridan ajratadi, lekin agar barcha testlar shu bitta test bazasini baham ko'rib, hech kim uni tozalamasa, testlar hamon bir-biriga (endi boshqa testlarga) ta'sir qiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "autouse=True fixture nima qiladi?",
        "description": "@pytest.fixture(autouse=True) bilan belgilangan clean_tables fixture'ining vazifasi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat aniq chaqirilgan testlarda ishlaydi",
            "Har bir test uchun avtomatik ishlaydi (alohida chaqirish shart emas), yield'dan keyingi kod esa har testdan keyin bajariladi",
            "Faqat bitta marta, butun test sessiyasi boshida ishlaydi",
            "Testlarni tezroq ishga tushiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "'autouse' so'zi 'avtomatik ishlatiladi' degan ma'noni bildiradi.",
        "explanation": "autouse=True fixture har bir test uchun avtomatik ishlatiladi. yield'dan keyingi kod har bir testdan keyin bajariladi - bu yerda jadvallarni tozalash orqali keyingi test har doim toza holatdan boshlanishini ta'minlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Flaky test qanday yuzaga kelishini tartiblang",
        "description": "Tozalash fixture'i yo'q holatda, ikkita test orasida flaky xatti-harakat qanday yuzaga kelishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "test_post_score ishga tushadi, bazaga 1 ta yozuv qo'shadi",
            "Yozuv testlar orasida TOZALANMAYDI, bazada qolib ketadi",
            "test_get_scores_empty_list keyin ishga tushadi, bo'sh ro'yxat kutadi",
            "Bazada allaqachon 1 ta yozuv borligi uchun bu test MUVAFFAQIYATSIZ bo'ladi",
        ],
        "correct_order": [
            "test_post_score ishga tushadi, bazaga 1 ta yozuv qo'shadi",
            "Yozuv testlar orasida TOZALANMAYDI, bazada qolib ketadi",
            "test_get_scores_empty_list keyin ishga tushadi, bo'sh ro'yxat kutadi",
            "Bazada allaqachon 1 ta yozuv borligi uchun bu test MUVAFFAQIYATSIZ bo'ladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Tartibga qarab har xil natija beradigan testlarning nomi",
        "description": "Ishga tushirish tartibiga qarab ba'zan o'tib, ba'zan muvaffaqiyatsiz bo'ladigan testlar qanday deb ataladi? (inglizcha atama bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "flaky",
        "hint": "Bu so'z darsning sarlavhasida ham ishlatilgan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega flaky testlar oddiy muvaffaqiyatsiz testlardan ko'ra xavfliroq?",
        "description": (
            "Doimiy ravishda muvaffaqiyatsiz bo'ladigan test bilan "
            "solishtirganda, flaky (vaqti-vaqti bilan muvaffaqiyatsiz "
            "bo'ladigan) test nega ko'proq xavf tug'diradi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Doimiy muvaffaqiyatsiz test darhol ko'rinadi va e'tibor "
            "qaratilib, albatta tuzatiladi. Flaky test esa faqat "
            "VAQTI-VAQTI bilan muvaffaqiyatsiz bo'lgani uchun, dasturchilar "
            "ko'pincha uni jiddiy qabul qilmay, \"tasodifiy xato\" yoki "
            "\"tarmoq/muhit muammosi\" deb hisoblab, shunchaki qayta ishga "
            "tushirib \"o'tib ketishini\" kutishadi. Bu esa jamoada flaky "
            "testlarni e'tiborsiz qoldirish odatini shakllantiradi - va "
            "aynan shu odat orqali HAQIQIY, jiddiy xatolar ham \"yana bitta "
            "flaky test\" deb chalg'itilib, e'tiborsiz qoldirilishi mumkin."
        ),
        "hint": "Doimiy xato darhol e'tibor tortadi. Vaqti-vaqti bilan chiqadigan xatoga qanday munosabatda bo'lishadi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "RankVault — PostgreSQL CRUD + Fixture'lar (flaky testlarsiz)",
    "task_description": (
        "2-bosqichdagi POST /scores'ni davom ettirib, GET /scores, GET "
        "/scores/:id va DELETE /scores/:id endpoint'larini yozing. "
        "tests/conftest.py'ni alohida TEST_DATABASE_URL bilan HAMDA "
        "autouse=True clean_tables fixture'i bilan to'ldiring — testlar "
        "qaysi tartibda ishga tushirilishidan qat'i nazar barqaror "
        "o'tishi shart."
    ),
    "task_requirements": (
        "• tests/conftest.py: TEST_DATABASE_URL orqali alohida test bazasiga ulanadi\n"
        "• autouse=True clean_tables fixture'i — har bir testdan keyin jadvallarni tozalaydi\n"
        "• GET /scores, GET /scores/:id, DELETE /scores/:id endpoint'lari yozilgan\n"
        "• pytest --count=3 (yoki testlarni qayta-qayta ishga tushirish) barqaror natija beradi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Python, Flask, pytest, PostgreSQL, SQLAlchemy",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Ranking algoritmi — "barqaror sort" va durang holatlarning yashirin xatosi</h2>

<pre class="mermaid">
flowchart LR
    SCORES["Bir xil ball: Ali=100, Vali=100"] --> QUERY{"Score.query.all() - ORDER BY bormi?"}
    QUERY -->|"ORDER BY yo'q"| UNDEFINED["SQL: qatorlar tartibi ANIQLANMAGAN"]
    UNDEFINED --> SORT["Python sorted() - BARQAROR, lekin noaniq kirishga nisbatan"]
    SORT --> INCONSISTENT["Natija: har xil so'rovda Ali/Vali tartibi o'zgarishi mumkin"]
</pre>

<p>Python: Algoritmlar va Ma'lumotlar Tuzilmasi kursida Big O notatsiyasini va tartiblash algoritmlarini (Bubble/Selection/Insertion, Merge/Quick Sort) allaqachon o'rgangansiz. Bu darsda RankVault'ning yuragi — reyting hisoblash — ni qurasiz. Lekin bu yerda keng tarqalgan noto'g'ri tushuncha bilan tanishasiz: <strong>"Python'ning <code>sorted()</code> barqaror (stable)"</strong> degan haqiqat, agar noto'g'ri qo'llanilsa, sizni <strong>yolg'on xotirjamlikka</strong> olib kelishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — GET /leaderboard: ball bo'yicha kamayish tartibida</h4>
<pre><code># app/routes.py
@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.points.desc(), Score.user_id.asc()).all()
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(scores)
    ])</code></pre>

<h4>BLOKA 2 — Big O: nega bu O(n log n)?</h4>
<pre><code># PostgreSQL'ning ORDER BY'i (odatda) va Python'ning sorted() funksiyasi
# (Timsort algoritmi) ikkalasi ham O(n log n) murakkablikka ega -
# bu 5-6-darslarda o'rgangan Merge Sort/Quick Sort oilasidan.
#
# n = 1,000 foydalanuvchi uchun: ~10,000 solishtirish
# n = 1,000,000 foydalanuvchi uchun: ~20,000,000 solishtirish
# (O(n^2) - Bubble Sort bo'lganda edi: 1,000,000,000,000!)</code></pre>

<h4>BLOKA 3 — ANIQ ikkinchi kalit (tie-break) bilan durang holatni hal qilish</h4>
<pre><code># Ikki foydalanuvchi BIR XIL ballga ega bo'lsa (masalan Ali=100, Vali=100),
# tartib nima asosida hal qilinishi ANIQ ko'rsatilishi shart:
Score.query.order_by(
    Score.points.desc(),      # 1) asosiy: ball bo'yicha kamayish
    Score.user_id.asc()       # 2) ANIQ tie-break: teng ball bo'lsa, user_id bo'yicha
).all()
# Endi natija HAR DOIM, HAR SO'ROVDA bir xil - chunki tartib TO'LIQ aniqlangan.</code></pre>

<h3>🐛 Ataylab xato — ORDER BY'siz so'rov + "Python sort barqaror" degan yolg'on xotirjamlik</h3>
<pre><code># "Python'ning sorted() barqaror, demak muammo yo'q" deb o'ylab:
@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.all()   # ❌ ORDER BY YO'Q!
    ranked = sorted(scores, key=lambda s: -s.points)
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(ranked)
    ])

# Bu yerdagi mantiq xatosi: Python'ning sorted() HAQIQATAN barqaror -
# u TENG elementlarning NISBIY tartibini saqlaydi. LEKIN "nisbiy tartib"
# NIMAGA nisbatan? Score.query.all()NING o'zi qaytaradigan tartibga!
#
# PostgreSQL esa ORDER BY bo'lmasa, qatorlar tartibini HECH QACHON
# kafolatlamaydi - bu SQL standartining o'zida shunday belgilangan.
# Amalda bu tartib jadval kichik bo'lganda ko'pincha "yozilgan tartibda"
# ko'rinadi, lekin bu KAFOLAT emas - VACUUM, ANALYZE, yoki jadval
# kattalashib query planner boshqa yo'l tanlasa, bu "amaliy" tartib
# HECH QANDAY kod o'zgarishisiz o'zgarishi mumkin.
#
# Natija: Ali va Vali ikkalasi ham 100 ball. Bugun /leaderboard
# Ali'ni 1-o'rinda ko'rsatadi. Ertaga, xuddi shu ma'lumot bilan,
# u Vali'ni 1-o'rinda ko'rsatishi mumkin - HECH KIM hech narsani
# o'zgartirmagan bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> bu xato ayniqsa <strong>nozik</strong>, chunki u yarim <strong>to'g'ri</strong> faktga asoslangan — Python'ning <code>sorted()</code> funksiyasi <strong>haqiqatan ham</strong> barqaror. Muammo shundaki, "barqarorlik" faqat <strong>kirish tartibiga nisbatan</strong> ma'no beradi — agar kirishning o'zi (bu yerda: <code>Score.query.all()</code>ning <code>ORDER BY</code>siz qaytargan tartibi) <strong>aniqlanmagan</strong> bo'lsa, "barqaror" sort ustiga qurilgan yakuniy natija ham <strong>aniqlanmagan</strong> bo'lib qoladi. Bu — algoritm darajasidagi to'g'rilik (sort barqaror) bilan <strong>tizim darajasidagi</strong> to'g'rilik (butun oqim deterministik) orasidagi farq.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Python'ning <code>sorted()</code>si haqiqatan barqarormi?</h4>
<p><strong>Ha</strong> — Python'ning <code>sorted()</code> (va <code>list.sort()</code>) Timsort algoritmidan foydalanadi, bu <strong>barqaror</strong>: agar ikki element solishtirish kaliti bo'yicha teng bo'lsa, ular <strong>kirish ro'yxatidagi</strong> nisbiy tartibini saqlaydi. Bu haqiqat — muammo bu yerda emas.</p>

<h4>2. Unda muammo qayerda?</h4>
<p>Muammo shundaki, <strong>kirish ro'yxatining o'zi</strong> — <code>Score.query.all()</code>, <code>ORDER BY</code>siz — <strong>aniqlanmagan</strong> tartibda keladi. PostgreSQL SQL standartiga ko'ra, <code>ORDER BY</code> bo'lmasa, qatorlar tartibini <strong>hech qachon</strong> kafolatlamaydi. "Barqaror sort ustiga aniqlanmagan kirish" — natijada butun oqim <strong>hali ham aniqlanmagan</strong>.</p>

<h4>3. Nega bu amalda ko'pincha "ishlab turgandek" ko'rinadi?</h4>
<p>Kichik, hali ko'p o'zgarmagan jadvalda PostgreSQL <strong>amalda</strong> ko'pincha yozuvlarni jismoniy saqlangan (ko'pincha yaratilgan) tartibda qaytaradi — bu <strong>tasodifiy</strong> xatti-harakat, kafolat emas. <code>VACUUM</code>, <code>ANALYZE</code>, indekslardan foydalanish, yoki jadval kattalashib query planner parallel worker'lar ishlatishga qaror qilishi kabi omillar bu "amaliy" tartibni <strong>hech qanday kod o'zgarishisiz</strong> buzishi mumkin.</p>

<h4>4. To'g'ri yechim nima?</h4>
<p><strong>Aniq</strong>, ikkinchi (yoki uchinchi) tie-break kalitini qo'shish — masalan <code>user_id</code> yoki <code>submitted_at</code> bo'yicha — shunda teng ball holatida ham tartib <strong>to'liq aniqlangan</strong> bo'ladi. Bundan tashqari, SQL darajasida <code>ORDER BY</code>ning o'zini ishlatish (Python darajasida qo'shimcha <code>sorted()</code> chaqirmasdan) ko'pincha yanada samarali va ishonchli.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>Bu — capstone'dagi birinchi xato turi bu safar <strong>test yozilishida emas</strong>, balki <strong>algoritmning o'zida</strong>, hatto <strong>to'g'ri, hujjatlashtirilgan</strong> xususiyat (Python sort'ning barqarorligi) haqidagi <strong>yarim tushuncha</strong>dan kelib chiqadi. Bu shuni ko'rsatadiki, "men to'g'ri, ishonchli vositadan foydalanyapman" degan fikr ham, agar butun tizim (SQL + Python) birga qanday ishlashini tushunmasangiz, yetarli emas.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Python'ning <code>sorted()</code>si haqiqatan barqaror, lekin bu faqat kirish tartibiga nisbatan ma'noga ega</li>
<li>✅ PostgreSQL <code>ORDER BY</code>siz qatorlar tartibini <strong>hech qachon</strong> kafolatlamaydi (SQL standarti)</li>
<li>✅ "Barqaror sort" + "aniqlanmagan kirish" = baribir aniqlanmagan yakuniy natija</li>
<li>✅ Durang holatlar uchun aniq, ikkinchi tie-break kaliti (masalan <code>user_id</code>) qo'shish shart</li>
<li>✅ To'g'ri vositadan foydalanish (barqaror sort) ham, agar butun oqimni tushunmasangiz, yetarli emas</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 4-BOSQICH: Ranking algoritmi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) GET /leaderboard - ANIQ tie-break bilan
# ─────────────────────────────────────────────────────────────────────

@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.order_by(
        Score.points.desc(),      # asosiy: ball bo'yicha kamayish
        Score.user_id.asc()       # ANIQ tie-break: teng ball bo'lsa
    ).all()
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(scores)
    ])


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_leaderboard.py - durang holatni aniq tekshirish
# ─────────────────────────────────────────────────────────────────────

def test_leaderboard_tie_break_is_deterministic(client):
    client.post('/scores', json={'user_id': 5, 'points': 100})
    client.post('/scores', json={'user_id': 2, 'points': 100})

    first_call = client.get('/leaderboard').get_json()
    second_call = client.get('/leaderboard').get_json()

    assert first_call == second_call   # ikkala chaqiruv HAM bir xil bo'lishi shart
    assert first_call[0]['user_id'] == 2   # kichikroq user_id birinchi (tie-break)


# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - ORDER BY'siz so'rov (izohda)
# ─────────────────────────────────────────────────────────────────────

# @app.route('/leaderboard')
# def leaderboard():
#     scores = Score.query.all()   # ORDER BY YO'Q!
#     ranked = sorted(scores, key=lambda s: -s.points)
#     return jsonify([...])
# Python sorted() barqaror - LEKIN kirish tartibining o'zi ORDER BY'siz
# ANIQLANMAGAN. "Barqaror sort ustidagi aniqlanmagan kirish" - natija
# hali ham aniqlanmagan bo'lib qoladi.
"""

L4_EX = [
    {
        "title": "Python'ning sorted() funksiyasi haqiqatan barqarormi?",
        "description": "Python'ning sorted() (va list.sort()) funksiyasi haqiqatan barqaror (stable) sort algoritmi ekanligi to'g'rimi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Yo'q, Python sort'i har doim beqaror",
            "Ha, Python Timsort ishlatadi va bu haqiqatan barqaror - lekin bu faqat kirish tartibiga nisbatan ma'noga ega",
            "Faqat ro'yxat 100 elementdan kichik bo'lsa barqaror",
            "Faqat raqamlar uchun barqaror, matnlar uchun emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu darsdagi xato Python'ning o'zida emas.",
        "explanation": "Python'ning sorted() funksiyasi Timsort algoritmidan foydalanadi va bu haqiqatan barqaror - lekin 'barqarorlik' faqat kirish ro'yxatidagi nisbiy tartibga nisbatan ma'noga ega.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "ORDER BY'siz PostgreSQL so'rovi qatorlar tartibini kafolatlaydimi?",
        "description": "Score.query.all() (ORDER BY qo'shilmagan holda) chaqirilganda, PostgreSQL qatorlarni qanday tartibda qaytarishini kafolatlaydimi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ha, har doim yaratilgan tartibda qaytaradi",
            "Yo'q, SQL standartiga ko'ra ORDER BY bo'lmasa, qatorlar tartibi umuman aniqlanmagan",
            "Ha, har doim id bo'yicha o'sish tartibida",
            "Yo'q, lekin faqat MySQL'da shunday, PostgreSQL'da tartib kafolatlangan",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu SQL standartining o'zida belgilangan qoida.",
        "explanation": "SQL standartiga ko'ra, ORDER BY bo'lmasa, PostgreSQL qatorlar tartibini hech qachon kafolatlamaydi - amalda ko'rinadigan tartib faqat tasodifiy natija, kafolat emas.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Durang holatning aniqlanmagan natijaga olib kelish jarayonini tartiblang",
        "description": "ORDER BY'siz so'rov + barqaror Python sort qanday qilib aniqlanmagan reyting natijasiga olib kelishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Score.query.all() ORDER BY'siz chaqiriladi - PostgreSQL tartibni kafolatlamaydi",
            "Python sorted() bu aniqlanmagan ro'yxatni ball bo'yicha tartiblaydi",
            "Bir xil ballga ega ikki foydalanuvchi (masalan Ali va Vali) uchun sort ularning KIRISH tartibini saqlaydi",
            "Lekin kirish tartibining o'zi aniqlanmagani uchun, Ali/Vali tartibi so'rovdan-so'rovga o'zgarishi mumkin",
        ],
        "correct_order": [
            "Score.query.all() ORDER BY'siz chaqiriladi - PostgreSQL tartibni kafolatlamaydi",
            "Python sorted() bu aniqlanmagan ro'yxatni ball bo'yicha tartiblaydi",
            "Bir xil ballga ega ikki foydalanuvchi (masalan Ali va Vali) uchun sort ularning KIRISH tartibini saqlaydi",
            "Lekin kirish tartibining o'zi aniqlanmagani uchun, Ali/Vali tartibi so'rovdan-so'rovga o'zgarishi mumkin",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Reyting so'rovining Big O murakkabligi",
        "description": "n ta foydalanuvchini ball bo'yicha tartiblash (Merge Sort/Timsort kabi samarali algoritm bilan) qanday Big O murakkablikka ega? (Big O yozuvi bilan javob bering, masalan: O(x))",
        "exercise_type": "text_input",
        "expected_answer": "O(n log n)",
        "hint": "Bu 5-6-darslarda o'rgangan Merge Sort/Quick Sort murakkabligi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega 'barqaror sort ishlatyapman' fikri yetarli emas?",
        "description": (
            "Dasturchi 'men Python'ning barqaror sorted() funksiyasidan "
            "foydalanyapman, demak reytingim deterministik' deb "
            "ishonsa, bu fikr nega noto'g'ri bo'lishi mumkin? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Sort'ning 'barqarorligi' faqat TENG elementlarning KIRISH "
            "ro'yxatidagi nisbiy tartibini saqlashni anglatadi - bu "
            "kirish ro'yxatining o'zi qanday tartibda kelganiga hech "
            "qanday ta'sir qilmaydi. Agar kirish ro'yxati (masalan "
            "ORDER BY'siz SQL so'rovidan kelgan) allaqachon aniqlanmagan "
            "tartibda bo'lsa, sort'ning o'zi qancha 'barqaror' bo'lmasin, "
            "yakuniy natija baribir aniqlanmagan bo'lib qoladi - chunki "
            "'barqaror' faqat 'teng elementlar aralashtirilmaydi' "
            "degani, 'kirish tartibi doim bir xil' degani emas. "
            "Deterministik natija olish uchun aniq, alohida tie-break "
            "kaliti (masalan user_id) kerak."
        ),
        "hint": "'Barqaror' so'zi aynan NIMANI kafolatlaydi - kirish tartibini, yoki chiqish tartibining doimiyligini?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "RankVault — Ranking algoritmi (aniq tie-break bilan)",
    "task_description": (
        "GET /leaderboard endpoint'ini yozing — barcha foydalanuvchilarni "
        "ball bo'yicha kamayish tartibida, ANIQ tie-break kaliti (masalan "
        "user_id) bilan qaytaring. Bir xil ballga ega foydalanuvchilar "
        "har doim BIR XIL, bashorat qilinadigan tartibda chiqishi shart."
    ),
    "task_requirements": (
        "• GET /leaderboard — Score.query.order_by() orqali, ANIQ ikkinchi (tie-break) kalit bilan tartiblangan\n"
        "• Score.query.all() (ORDER BY'siz) + Python sorted() kombinatsiyasi ISHLATILMAGAN\n"
        "• Test: bir xil ballga ega ikki foydalanuvchi bilan /leaderboard ikki marta chaqirilib, natijalar bir xil ekanligi tekshiriladi\n"
        "• README.md: tie-break strategiyasi tushuntirilgan, holat checklist'i yangilangan"
    ),
    "task_technologies": "Python, Flask, PostgreSQL, SQLAlchemy, algoritmlar",
    "task_deadline_days": 4,
}


L5_TEXT = """\
<h2>5-bosqich: Test Coverage + Binary Search — coverage foizining yolg'oni</h2>

<pre class="mermaid">
flowchart LR
    FUNC["find_rank_by_points() - binary search funksiyasi"] --> TESTS["Faqat 'element mavjud, ro'yxat o'rtasida' holati sinaladi"]
    TESTS --> COV["pytest-cov: 95%+ coverage - deyarli barcha QATORLAR bajarilgan"]
    COV --> BLIND["Lekin: bo'sh ro'yxat va bitta elementli ro'yxat HECH QACHON sinalmagan"]
    BLIND --> BUG["Production'da bitta elementli reytingda /rank chaqirilsa - noto'g'ri natija"]
</pre>

<p>Python: Algoritmlar va Ma'lumotlar Tuzilmasi kursida Binary Search'ni, Python: Testlash kursida esa Test Coverage (<code>pytest-cov</code>)ni allaqachon o'rgangansiz. Bu darsda ularni birlashtirasiz: "mening reytingim nechanchi?" so'rovini <strong>O(log n)</strong> tezlikda javob beruvchi <code>find_rank_by_points()</code> funksiyasini yozasiz. Lekin bu safar eng xavfli tushunchalardan biri bilan tanishasiz: <strong>yuqori coverage foizi HAM to'g'rilikni kafolatlamaydi.</strong></p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Binary Search: O(log n) tezlikda reyting topish</h4>
<pre><code># app/ranking.py
def find_rank_by_points(sorted_points_desc, target_points):
    \"\"\"sorted_points_desc - kamayish tartibida saralangan ball ro'yxati.
    target_points shu ro'yxatda BIRINCHI marta qayerda uchrashini topadi
    (rank = shu indeks + 1).\"\"\"
    low, high = 0, len(sorted_points_desc) - 1
    while low <= high:                              # ❗ <= MUHIM - pastda ko'rasiz
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            # Chapga siljib, BIRINCHI mos kelgan indeksni topamiz
            while mid > 0 and sorted_points_desc[mid - 1] == target_points:
                mid -= 1
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None   # topilmadi</code></pre>

<h4>BLOKA 2 — pytest-cov: coverage report nimani o'lchaydi?</h4>
<pre><code># Terminal:
pytest --cov=app --cov-report=term-missing

# Natija (misol):
# app/ranking.py    24 stmts   1 miss   96%
#
# ❗ 96% - bu FAQAT "24 qatordan 23 tasi kamida BIR marta bajarildi"
# degani. U hech qanday "qaysi QIYMATLAR bilan sinaldi" haqida
# ma'lumot bermaydi!</code></pre>

<h4>BLOKA 3 — chekka holatlarni ANIQ sinaydigan testlar</h4>
<pre><code># tests/test_ranking.py
def test_find_rank_empty_list():
    assert find_rank_by_points([], 100) is None

def test_find_rank_single_element_found():
    assert find_rank_by_points([100], 100) == 1

def test_find_rank_single_element_not_found():
    assert find_rank_by_points([100], 50) is None

def test_find_rank_target_not_in_list():
    assert find_rank_by_points([300, 200, 100], 250) is None</code></pre>

<h3>🐛 Ataylab xato — yuqori coverage, lekin chekka holatlar sinalmagan</h3>
<pre><code># find_rank_by_points()da NOZIK off-by-one xato bor:
def find_rank_by_points(sorted_points_desc, target_points):
    low, high = 0, len(sorted_points_desc) - 1
    while low < high:                                # ❌ <= o'rniga <  !
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None

# tests/test_ranking.py - FAQAT "happy path" sinaladi:
def test_find_rank_middle_of_large_list():
    scores = [500, 400, 300, 200, 100]
    assert find_rank_by_points(scores, 300) == 3   # ✅ BU test o'tadi

# $ pytest --cov=app --cov-report=term-missing
# app/ranking.py   12 stmts   0 miss   100%   ✅✅✅
#
# 100% COVERAGE! Lekin:
find_rank_by_points([100], 100)   # ❌ None qaytaradi - XATO! (1 bo'lishi kerak)
# Chunki low=0, high=0 bo'lganda `while low < high` DARHOL False bo'ladi -
# tsikl HECH QACHON ishlamaydi, garchi 100 albatta ro'yxatda bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> 100% coverage — bu <strong>xato yo'q</strong> degani emas, bu <strong>"har bir qator kamida bir marta bajarildi"</strong> degani, xolos. Yuqoridagi <code>while low &lt; high</code> xatosi katta ro'yxatlar bilan sinalganda <strong>hech qachon</strong> ko'rinmaydi — chunki katta ro'yxatda tsikl baribir bir necha marta bajariladi, va coverage vositasi bu qatorni "bajarilgan" deb belgilaydi. Xato faqat <strong>chekka holatda</strong> — bitta elementli ro'yxatda — namoyon bo'ladi, chunki aynan shu holatda <code>low == high</code> darhol teng bo'lib qoladi. Agar hech kim <strong>aynan shu</strong> chekka holatni sinamagan bo'lsa, coverage 100% bo'lsa ham, xato <strong>yashiringan</strong> qoladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Coverage foizi aslida nimani o'lchaydi?</h4>
<p>Coverage — kod <strong>qatorlari</strong> (yoki branch'lari) test paytida kamida <strong>bir marta bajarilganini</strong> o'lchaydi. U <strong>qanday qiymatlar</strong> bilan bajarilgani, yoki natija <strong>to'g'rimi</strong> yo'qmi haqida <strong>hech narsa</strong> bilmaydi.</p>

<h4>2. Nega binary search chekka holatlarga ayniqsa sezgir?</h4>
<p>Binary search'da <code>low</code>, <code>high</code>, <code>mid</code> chegaralari bilan ishlash — <code>&lt;</code> va <code>&lt;=</code>, <code>-1</code> va <code>+1</code> kabi <strong>bir birlik</strong> farqlar butun natijani o'zgartirishi mumkin (off-by-one xatolar). Bu xatolar aynan <strong>chegaraviy</strong> holatlarda (bo'sh ro'yxat, bitta element, birinchi/oxirgi element) namoyon bo'ladi — o'rtadagi "oddiy" holatlarda esa yashirinib qoladi.</p>

<h4>3. Nega yuqoridagi xato katta ro'yxatda sezilmaydi, lekin kichikida sezilib qoladi?</h4>
<p><code>while low &lt; high</code> xatosi faqat <code>low == high</code> bo'lgan <strong>bitta</strong> qadamda muammo tug'diradi. Katta ro'yxatda tsikl bu holatga yetguncha <strong>ko'p</strong> marta to'g'ri ishlaydi va natija ko'pincha (lekin har doim emas) tasodifan to'g'ri chiqadi. Bitta elementli ro'yxatda esa <code>low</code> va <code>high</code> BOSHIDANOQ teng — xato <strong>darhol</strong> ko'rinadi.</p>

<h4>4. Testlarni yozishda nimaga alohida e'tibor berish kerak?</h4>
<p>Har qanday algoritm uchun, ayniqsa qidiruv/tartiblash kabi <strong>chegara-sezgir</strong> algoritmlar uchun: bo'sh kirish, bitta elementli kirish, va qidirilayotgan qiymat ro'yxatning <strong>eng boshida/oxirida</strong> bo'lgan holatlarni <strong>aniq</strong> test qilish kerak — bularsiz coverage foizi qanchalik yuqori bo'lmasin, ishonch yolg'on bo'lib qoladi.</p>

<h4>5. Bu darsning capstone bo'ylab qanday o'rni bor?</h4>
<p>3-darsda "yashil test" yolg'on bo'lishi mumkinligini ko'rgan edingiz (flaky testlar). Bu darsda esa <strong>"yuqori coverage" ham</strong> yolg'on ishonch berishi mumkinligini ko'rdingiz. Ikkalasi ham bir xil umumiy saboqning turli ko'rinishi: <strong>metrikalar (yashil belgi, foiz) — to'g'rilikning o'zi emas, balki uning noaniq, ba'zan aldamchi ko'rsatkichi.</strong></p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Coverage foizi faqat qatorlar bajarilganini o'lchaydi, natijaning to'g'riligini emas</li>
<li>✅ Binary search — off-by-one xatolarga ayniqsa moyil, chunki chegara shartlariga (<code>&lt;</code>/<code>&lt;=</code>) juda sezgir</li>
<li>✅ Bunday xatolar odatda faqat chekka holatlarda (bo'sh, bitta element) namoyon bo'ladi</li>
<li>✅ Yuqori coverage'ga qaramay, chekka holatlar sinalmagan bo'lsa, xato yashiringan qolishi mumkin</li>
<li>✅ "Yashil test" (3-dars) va "yuqori coverage" (bu dars) — ikkalasi ham metrika, to'g'rilikning o'zi emas</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 5-BOSQICH: Test Coverage + Binary Search
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/ranking.py - to'g'ri binary search (<=  bilan)
# ─────────────────────────────────────────────────────────────────────

def find_rank_by_points(sorted_points_desc, target_points):
    low, high = 0, len(sorted_points_desc) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_points_desc[mid] == target_points:
            while mid > 0 and sorted_points_desc[mid - 1] == target_points:
                mid -= 1
            return mid + 1
        elif sorted_points_desc[mid] > target_points:
            low = mid + 1
        else:
            high = mid - 1
    return None


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_ranking.py - chekka holatlarni ANIQ sinovdan o'tkazish
# ─────────────────────────────────────────────────────────────────────

def test_find_rank_empty_list():
    assert find_rank_by_points([], 100) is None


def test_find_rank_single_element_found():
    assert find_rank_by_points([100], 100) == 1


def test_find_rank_single_element_not_found():
    assert find_rank_by_points([100], 50) is None


def test_find_rank_target_not_in_list():
    assert find_rank_by_points([300, 200, 100], 250) is None


def test_find_rank_middle_of_large_list():
    scores = [500, 400, 300, 200, 100]
    assert find_rank_by_points(scores, 300) == 3


# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - off-by-one, faqat happy path sinalgan (izohda)
# ─────────────────────────────────────────────────────────────────────

# def find_rank_by_points(sorted_points_desc, target_points):
#     low, high = 0, len(sorted_points_desc) - 1
#     while low < high:                    # <= o'rniga < !
#         ...
#     return None
#
# Faqat katta ro'yxat bilan sinalsa - 100% coverage, lekin
# find_rank_by_points([100], 100) NOTO'G'RI None qaytaradi.
"""

L5_EX = [
    {
        "title": "Coverage foizi aslida nimani o'lchaydi?",
        "description": "pytest-cov tomonidan ko'rsatiladigan '95% coverage' ko'rsatkichi aslida nimani anglatadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kodning 95% qismi to'g'ri ishlashi tasdiqlangan",
            "Kod qatorlarining 95% qismi test paytida kamida bir marta bajarilgan - bu natijaning to'g'riligi haqida hech narsa aytmaydi",
            "Testlarning 95% qismi muvaffaqiyatli o'tgan",
            "Kodning 95% qismi bug'lardan xoli ekanligi kafolatlangan",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Coverage - qatorlar BAJARILGANMI, degan savolga javob beradi, TO'G'RIMI degan savolga emas.",
        "explanation": "Coverage faqat kod qatorlari (yoki branch'lari) test paytida kamida bir marta bajarilganini o'lchaydi - u qanday qiymatlar bilan bajarilgani yoki natija to'g'ri-noto'g'riligi haqida hech narsa bilmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega binary search off-by-one xatolarga ayniqsa moyil?",
        "description": "Binary search algoritmi nega boshqa algoritmlarga qaraganda off-by-one (bir birlik) xatolarga ko'proq moyil?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki u Python'da yomon qo'llab-quvvatlanadi",
            "Chunki low/high/mid chegaralari bilan ishlash, < va <= kabi bir birlik farqlar butun natijani o'zgartirishi mumkin",
            "Chunki u faqat matnlar uchun ishlatiladi",
            "Chunki u har doim O(n^2) murakkablikka ega",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "while low < high va while low <= high orasidagi farqni o'ylab ko'ring.",
        "explanation": "Binary search'da low, high, mid chegaralari bilan ishlash - < va <=, -1 va +1 kabi bir birlik farqlar butun natijani o'zgartirishi mumkin (off-by-one xatolar), va bu xatolar aynan chegaraviy holatlarda namoyon bo'ladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "100% coverage'ga qaramay xato qanday yashirin qolishini tartiblang",
        "description": "while low < high xatosi bilan yozilgan find_rank_by_points() 100% coverage bilan qanday qilib yashirin xato saqlab qolishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Faqat katta ro'yxat bilan 'happy path' testi yoziladi",
            "Katta ro'yxatda tsikl bir necha marta bajariladi, coverage 100% ko'rsatadi",
            "Bitta elementli ro'yxat HECH QACHON test qilinmaydi",
            "Production'da bitta elementli reytingda funksiya chaqirilsa, noto'g'ri None qaytadi",
        ],
        "correct_order": [
            "Faqat katta ro'yxat bilan 'happy path' testi yoziladi",
            "Katta ro'yxatda tsikl bir necha marta bajariladi, coverage 100% ko'rsatadi",
            "Bitta elementli ro'yxat HECH QACHON test qilinmaydi",
            "Production'da bitta elementli reytingda funksiya chaqirilsa, noto'g'ri None qaytadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Binary search'ning samaradorlik murakkabligi",
        "description": "Saralangan ro'yxatda binary search orqali elementni topish qanday Big O murakkablikka ega? (Big O yozuvi bilan javob bering, masalan: O(x))",
        "exercise_type": "text_input",
        "expected_answer": "O(log n)",
        "hint": "Har bir qadamda qidiruv doirasi ikki baravar qisqaradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega chekka holatlarni maxsus sinash zarur?",
        "description": (
            "Coverage foizi yuqori bo'lsa ham, nega bo'sh ro'yxat, bitta "
            "elementli ro'yxat kabi chekka holatlarni ALOHIDA, ANIQ "
            "sinash zarur? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Coverage foizi faqat kod qatorlarining kamida bir marta "
            "bajarilganini ko'rsatadi, lekin QANDAY qiymatlar bilan "
            "bajarilganini ko'rsatmaydi. Off-by-one kabi xatolar odatda "
            "faqat MA'LUM, chegaraviy kirish qiymatlarida (masalan bo'sh "
            "ro'yxat, yoki low va high bir xil bo'lgan bitta elementli "
            "ro'yxat) namoyon bo'ladi - katta yoki 'oddiy' o'rtacha "
            "holatlarda esa tsikl baribir bir necha marta to'g'ri ishlab, "
            "coverage vositasini \"qator bajarildi\" deb belgilashga "
            "majburlaydi, garchi natija chegaraviy holatda noto'g'ri "
            "bo'lsa ham. Shuning uchun faqat coverage foiziga tayanish "
            "yetarli emas - chekka holatlar aniq, alohida testlar bilan "
            "tekshirilishi shart."
        ),
        "hint": "Coverage NIMANI o'lchaydi - qator bajarilganinimi, yoki u qanday qiymat bilan bajarilganinimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "RankVault — Test Coverage + Binary Search (find_rank_by_points)",
    "task_description": (
        "O(log n) tezlikda ishlaydigan find_rank_by_points() funksiyasini "
        "binary search orqali yozing va GET /rank/<user_id> endpoint'ida "
        "ishlating. pytest-cov orqali coverage hisobotini oling — LEKIN "
        "faqat foizga emas, chekka holatlarni ANIQ sinovdan o'tkazishga "
        "e'tibor bering."
    ),
    "task_requirements": (
        "• app/ranking.py: find_rank_by_points() to'g'ri chegara shartlari (low <= high) bilan yozilgan\n"
        "• GET /rank/<user_id> — find_rank_by_points()dan foydalanadi (chiziqli qidiruv EMAS)\n"
        "• tests/test_ranking.py: bo'sh ro'yxat, bitta elementli ro'yxat (topilgan va topilmagan), va o'rtadagi element uchun ALOHIDA testlar\n"
        "• pytest --cov=app --cov-report=term-missing 90%+ coverage ko'rsatadi\n"
        "• README.md: coverage'ning cheklovlari (nimani o'lchamasligi) tushuntirilgan, holat checklist'i yangilangan"
    ),
    "task_technologies": "Python, Flask, pytest, pytest-cov, algoritmlar",
    "task_deadline_days": 5,
}


L6_TEXT = """\
<h2>6-bosqich: HashMap cache + Mocking — muvaffaqiyatni "soxtalashtiruvchi" mock</h2>

<pre class="mermaid">
flowchart LR
    RANK["Foydalanuvchi TOP 10'ga kiradi"] --> NOTIFY["notify_top_10() - tashqi xabar xizmatini chaqiradi"]
    NOTIFY --> MOCK["Testda: @patch orqali HAR DOIM muvaffaqiyat qaytariladi"]
    MOCK --> BLIND["Xizmat XATOSI/TIMEOUT holati HECH QACHON sinalmagan"]
    BLIND --> PROD["Production'da xizmat ishlamay qolsa - kutilmagan crash"]
</pre>

<p>Python: Algoritmlar va Ma'lumotlar Tuzilmasi kursida HashMap (Hash Table)ni, Python: Testlash kursida esa Mock va <code>@patch</code>ni allaqachon o'rgangansiz. Bu darsda ularni birlashtirasiz: reyting uchun O(1) tezlikdagi HashMap cache va foydalanuvchi TOP 10'ga kirganda tashqi xabar xizmatini chaqiruvchi funksiya yozasiz. Lekin bu safar Mock'ning eng xavfli noto'g'ri qo'llanilishi bilan tanishasiz: <strong>faqat muvaffaqiyat holatini mock qilish.</strong></p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — HashMap cache: O(1) username → rank qidiruv</h4>
<pre><code># app/cache.py
class RankCache:
    def __init__(self):
        self._cache = {}   # HashMap: username -> rank

    def get(self, username):
        return self._cache.get(username)          # O(1) - Hash Table darsidan tanish

    def set_all(self, ranked_list):
        self._cache = {
            entry.username: i + 1
            for i, entry in enumerate(ranked_list)
        }   # HAR safar reyting yangilanganda qayta quriladi</code></pre>

<h4>BLOKA 2 — tashqi xabar xizmatini chaqirish</h4>
<pre><code># app/notifications.py
import requests

def notify_top_10(username):
    response = requests.post(
        'https://notify.example.com/send',
        json={'username': username, 'message': "Siz TOP 10'ga kirdingiz!"},
        timeout=5,
    )
    response.raise_for_status()
    return True</code></pre>

<h4>BLOKA 3 — @patch bilan HAM muvaffaqiyat, HAM xato holatini sinash</h4>
<pre><code># tests/test_notifications.py
from unittest.mock import patch
import requests

@patch('app.notifications.requests.post')
def test_notify_top_10_success(mock_post):
    mock_post.return_value.status_code = 200
    assert notify_top_10('ali') is True

@patch('app.notifications.requests.post')
def test_notify_top_10_service_down(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    # Xizmat javob bermasa, funksiya CRASH bo'lmasligi kerak:
    result = notify_top_10_safe('ali')
    assert result is False   # xato "tutildi", dastur ishlashda davom etadi</code></pre>

<h3>🐛 Ataylab xato — mock FAQAT muvaffaqiyat holatini qaytaradi</h3>
<pre><code># tests/test_notifications.py - FAQAT muvaffaqiyat holati sinaladi:
@patch('app.notifications.requests.post')
def test_notify_top_10(mock_post):
    mock_post.return_value.status_code = 200   # ❌ HAR DOIM muvaffaqiyat!
    assert notify_top_10('ali') is True

# Xizmat XATOSI yoki TIMEOUT holati HECH QACHON sinalmagan!

# app/notifications.py - real kodda ham xatoni ushlaydigan try/except YO'Q:
def notify_top_10(username):
    response = requests.post(
        'https://notify.example.com/send',
        json={'username': username, 'message': "Siz TOP 10'ga kirdingiz!"},
        timeout=5,
    )
    response.raise_for_status()   # ❗ Agar xizmat 500/timeout qaytarsa - bu QATOR XATO tashlaydi!
    return True

# app/routes.py - bu funksiya POST /scores ICHIDA, sinxron chaqiriladi:
@app.route('/scores', methods=['POST'])
def create_score():
    score = save_score(request.get_json())
    if is_top_10(score):
        notify_top_10(score.user_id)   # ❌ Agar bu yerda xato tashlansa...
    return jsonify(score.to_dict()), 201

# Test suite 100% "yashil" - lekin production'da xabar xizmati
# BIR MARTA ham sekinlashsa yoki ishlamay qolsa, HAR BIR /scores
# so'rovi (nafaqat TOP 10'ga tegishlisi!) 500 xato bilan yiqiladi -
# chunki notify_top_10() ichidagi xato ushlanmagan holda yuqoriga
# "otiladi" va butun endpoint'ni buzadi.</code></pre>

<p><strong>Natija:</strong> mock — bu <strong>haqiqiy tashqi xizmatni</strong> almashtiruvchi soxta obyekt, va uni <strong>faqat muvaffaqiyat qaytaradigan</strong> qilib sozlash — testlarni tezlashtiradi, lekin xizmat <strong>muvaffaqiyatsiz</strong> bo'lganda kod qanday xatti-harakat qilishini <strong>hech qachon</strong> sinamaydi. Agar real kodda bu holat uchun <code>try/except</code> bo'lmasa, test suite 100% "yashil" bo'lgan holda ham, production'da <strong>haqiqiy</strong> xizmat nosozligi butun endpoint'ni yiqitishi mumkin — bu esa <strong>mock testlarning eng xavfli yolg'on ishonch</strong> turi: "men bu qismni sinadim" degan tuyg'u, aslida faqat <strong>bitta, eng yaxshi</strong> stsenariy sinalgan bo'lsa ham.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. HashMap cache nega O(1) tezlikda ishlaydi?</h4>
<p>Python <code>dict</code>i (HashMap) — kalit (username) uchun hash funksiyasidan foydalanib, qiymatga (rank) <strong>to'g'ridan-to'g'ri</strong> murojaat qiladi, ro'yxat bo'ylab qidirish shart emas. Bu — Algoritmlar kursida o'rgangan <strong>O(1) o'rtacha holat</strong> murakkabligi, chiziqli qidiruvning O(n) murakkabligidan farqli.</p>

<h4>2. Mock nima uchun ishlatiladi?</h4>
<p>Mock — testlarda <strong>haqiqiy</strong> tashqi xizmatga (internetga, boshqa serverga) murojaat qilmasdan, uning <strong>xatti-harakatini soxtalashtirish</strong> uchun ishlatiladi. Bu testlarni tezroq, barqarorroq va tashqi xizmatning ishlab-ishlamasligidan mustaqil qiladi.</p>

<h4>3. Nega faqat muvaffaqiyat holatini mock qilish xavfli?</h4>
<p>Haqiqiy hayotda tashqi xizmatlar <strong>doim</strong> ishlab turmaydi — tarmoq xatosi, timeout, 500 xato kabi holatlar <strong>muqarrar</strong>. Agar test suite faqat "hammasi yaxshi" stsenariysini sinasa, kod bu <strong>muqarrar</strong> muvaffaqiyatsizlik holatlarida qanday ishlashi <strong>hech qachon</strong> tekshirilmaydi — garchi bu holatlar production'da <strong>albatta</strong> yuz beradi.</p>

<h4>4. Bitta endpoint'dagi xato nega BOSHQA, aloqasi yo'q so'rovlarga ham ta'sir qiladi?</h4>
<p>Agar <code>notify_top_10()</code> <code>POST /scores</code> ichida, <strong>sinxron</strong> va <code>try/except</code>siz chaqirilsa, undagi har qanday ushlanmagan xato butun so'rov ishlov berishini <strong>to'xtatadi</strong>. Natijada nafaqat TOP 10'ga chiqqan foydalanuvchi, balki <strong>istalgan</strong> foydalanuvchining oddiy ball qo'shish so'rovi ham xizmat nosozligi tufayli 500 xato bilan yiqiladi.</p>

<h4>5. To'g'ri yechim nima?</h4>
<p>Ikkita narsa kerak: (1) <strong>testlarda</strong> mock orqali HAM muvaffaqiyat, HAM xato/timeout holatlarini sinash, va (2) <strong>real kodda</strong> tashqi xizmat chaqiruvini <code>try/except</code> bilan o'rab, xato yuz berganda dasturning qolgan qismi (ball saqlash) <strong>baribir</strong> muvaffaqiyatli yakunlanishini ta'minlash — xabar yuborilmasa ham, ball saqlanishi kerak.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ HashMap (Python dict) — kalit orqali O(1) tezlikda qiymatga murojaat qilish imkonini beradi</li>
<li>✅ Mock — testlarda tashqi xizmatning xatti-harakatini soxtalashtirish uchun ishlatiladi</li>
<li>✅ Faqat muvaffaqiyat holatini mock qilish — xizmat muvaffaqiyatsizligiga tayyorgarlikni hech qachon sinamaydi</li>
<li>✅ Sinxron, try/except'siz tashqi chaqiruv — bitta xizmat nosozligini butun endpoint'ga "yuqtirishi" mumkin</li>
<li>✅ To'g'ri yondashuv: HAM muvaffaqiyat, HAM xato holatini test qilish + real kodda xatoni tutish</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 6-BOSQICH: HashMap cache + Mocking
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/cache.py - HashMap orqali O(1) rank cache
# ─────────────────────────────────────────────────────────────────────

class RankCache:
    def __init__(self):
        self._cache = {}

    def get(self, username):
        return self._cache.get(username)

    def set_all(self, ranked_list):
        self._cache = {
            entry.username: i + 1
            for i, entry in enumerate(ranked_list)
        }


# ─────────────────────────────────────────────────────────────────────
# 2) app/notifications.py - xatoni TUTADIGAN, xavfsiz versiya
# ─────────────────────────────────────────────────────────────────────

import requests


def notify_top_10_safe(username):
    try:
        response = requests.post(
            'https://notify.example.com/send',
            json={'username': username, 'message': "Siz TOP 10'ga kirdingiz!"},
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False   # xato tutildi - dastur ishlashda davom etadi


# ─────────────────────────────────────────────────────────────────────
# 3) tests/test_notifications.py - HAM muvaffaqiyat, HAM xato holati
# ─────────────────────────────────────────────────────────────────────

from unittest.mock import patch


@patch('app.notifications.requests.post')
def test_notify_top_10_success(mock_post):
    mock_post.return_value.status_code = 200
    assert notify_top_10_safe('ali') is True


@patch('app.notifications.requests.post')
def test_notify_top_10_service_down(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    assert notify_top_10_safe('ali') is False


# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - faqat muvaffaqiyat mock qilingan, try/except yo'q (izohda)
# ─────────────────────────────────────────────────────────────────────

# def notify_top_10(username):
#     response = requests.post(..., timeout=5)
#     response.raise_for_status()   # try/exceptSIZ!
#     return True
#
# @patch('app.notifications.requests.post')
# def test_notify_top_10(mock_post):
#     mock_post.return_value.status_code = 200   # FAQAT muvaffaqiyat!
#     assert notify_top_10('ali') is True
# Xizmat XATOSI HECH QACHON sinalmagan - production'da xizmat
# ishlamasa, POST /scores butunlay 500 bilan yiqiladi.
"""

L6_EX = [
    {
        "title": "HashMap cache nega O(1) tezlikda ishlaydi?",
        "description": "RankCache klassida self._cache.get(username) nega O(1) (o'rtacha holatda) tezlikda ishlaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki Python dict'lari har doim kichik hajmda saqlanadi",
            "dict (HashMap) kalit uchun hash funksiyasidan foydalanib qiymatga to'g'ridan-to'g'ri murojaat qiladi, ro'yxat bo'ylab qidirish shart emas",
            "Chunki username har doim raqamlardan iborat",
            "Chunki Flask buni avtomatik optimallashtiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Algoritmlar kursidagi Hash Table darsidan tanish tushuncha.",
        "explanation": "dict (HashMap) kalit uchun hash funksiyasidan foydalanib qiymatga to'g'ridan-to'g'ri murojaat qiladi - bu ro'yxat bo'ylab birma-bir qidirishni talab qilmaydi, shuning uchun O(1) o'rtacha murakkablikka ega.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega faqat muvaffaqiyat holatini mock qilish xavfli?",
        "description": "Test suite'da tashqi xabar xizmati FAQAT muvaffaqiyatli javob qaytaradigan qilib mock qilinsa, bu nima uchun xavfli?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki mock qilish umuman tavsiya etilmaydi",
            "Chunki haqiqiy hayotda tashqi xizmatlar muqarrar ravishda vaqti-vaqti bilan ishlamay qoladi, va kod bu holatda qanday ishlashi hech qachon sinalmaydi",
            "Chunki mock qilingan testlar sekinroq ishlaydi",
            "Chunki bu faqat pullik API'lar uchun muammo",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Tashqi xizmatlar har doim ishlab turadimi?",
        "explanation": "Haqiqiy hayotda tashqi xizmatlar muqarrar ravishda ba'zan ishlamay qoladi (tarmoq xatosi, timeout, 500 xato) - agar bu holat hech qachon sinalmasa, kod bunday holatda qanday ishlashi noma'lum bo'lib qoladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Xizmat nosozligi butun endpoint'ni qanday buzishini tartiblang",
        "description": "try/except'siz notify_top_10() qanday qilib butun POST /scores endpoint'ini yiqitishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi ball qo'shadi, u TOP 10'ga kiradi",
            "notify_top_10() sinxron, try/exceptsiz chaqiriladi",
            "Tashqi xabar xizmati ishlamay qolgani uchun response.raise_for_status() xato tashlaydi",
            "Ushlanmagan xato yuqoriga 'otiladi' va butun POST /scores so'rovi 500 bilan yiqiladi",
        ],
        "correct_order": [
            "Foydalanuvchi ball qo'shadi, u TOP 10'ga kiradi",
            "notify_top_10() sinxron, try/exceptsiz chaqiriladi",
            "Tashqi xabar xizmati ishlamay qolgani uchun response.raise_for_status() xato tashlaydi",
            "Ushlanmagan xato yuqoriga 'otiladi' va butun POST /scores so'rovi 500 bilan yiqiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Mock'da xizmat xatosini simulyatsiya qilish usuli",
        "description": "unittest.mock'da mock_post ob'ekti chaqirilganda XATO (masalan Timeout) tashlashini simulyatsiya qilish uchun qaysi atribut ishlatiladi? (masalan: mock_post.xxx = ...)",
        "exercise_type": "text_input",
        "expected_answer": "side_effect",
        "hint": "return_value emas, balki xatoni 'yon ta'sir' sifatida tashlaydigan atribut.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "To'g'ri yechim ikki qismdan iborat - nega ikkalasi ham kerak?",
        "description": (
            "Bu muammoni to'g'ri hal qilish uchun HAM testlarda xato "
            "holatini mock qilish, HAM real kodda try/except qo'shish "
            "kerak. Nega faqat bittasi (masalan faqat testlarda sinash, "
            "kodda try/except qo'shmasdan) yetarli emas? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar faqat testlarda xato holati sinalsa-yu, real kodda "
            "try/except bo'lmasa, test buzilgan xatti-harakatni "
            "(masalan crash bo'lishini) ANIQLAB BERADI, lekin buni "
            "TUZATMAYDI - test hali ham muvaffaqiyatsiz bo'lib qolaveradi, "
            "chunki kodning o'zi xatoni tutmaydi. Agar faqat real kodga "
            "try/except qo'shilsa-yu, lekin bu holat testlarda hech qachon "
            "sinalmasa, kelajakda kimdir try/except'ni bilmasdan olib "
            "tashlasa yoki noto'g'ri o'zgartirsa, buni HECH QANDAY test "
            "ushlab qolmaydi. Shuning uchun ikkalasi birga ishlatilishi "
            "kerak: test xato holatini ANIQLAYDI va KELAJAKDA HAM "
            "tekshirib turadi, kod esa xatoni HAQIQATDA tutadi."
        ),
        "hint": "Faqat testda sinash nimani ANIQLAYDI, lekin nimani TUZATMAYDI?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "RankVault — HashMap cache + Mocking (xato holatlari bilan)",
    "task_description": (
        "RankCache klassini (HashMap orqali O(1) username->rank) va "
        "notify_top_10_safe() funksiyasini yozing. Testlarda tashqi "
        "xabar xizmatini @patch orqali mock qiling — HAM muvaffaqiyat, "
        "HAM xizmat nosozligi (Timeout/xato) holatlarini sinang."
    ),
    "task_requirements": (
        "• app/cache.py: RankCache — dict orqali O(1) username->rank qidiruv\n"
        "• app/notifications.py: notify_top_10_safe() — try/except bilan xatoni tutadi, False qaytaradi\n"
        "• tests/test_notifications.py: @patch orqali muvaffaqiyat HAMDA xato/timeout holati ALOHIDA sinalgan\n"
        "• POST /scores — notify chaqiruvi xato bersa ham, ball saqlanishi va 201 qaytarilishi tasdiqlangan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Python, Flask, pytest, unittest.mock, algoritmlar",
    "task_deadline_days": 5,
}


L7_TEXT = """\
<h2>7-bosqich (CAPSTONE yakuni): deploy va "yashil CI, qizil haqiqat" xatosi</h2>

<pre class="mermaid">
flowchart LR
    PUSH["Kod push qilinadi"] --> CI["CI: test skripti ishga tushiriladi"]
    CI --> SCRIPT{"Skript chiqish kodini TO'G'RI uzatadimi?"}
    SCRIPT -->|"Noto'g'ri: xato yutiladi"| GREEN["CI: 'muvaffaqiyatli' - yashil belgi"]
    SCRIPT -->|"To'g'ri: chiqish kodi uzatiladi"| RED["CI: muvaffaqiyatsiz testlar bo'lsa - QIZIL"]
    GREEN --> DEPLOY["Deploy amalga oshadi - garchi testlar BUZILGAN bo'lsa ham!"]
</pre>

<p>Python: Testlash kursining o'z mini-capstone'i (6-dars: "To'liq testlangan Flask API") va Python: Algoritmlar kursining o'z mini-capstone'i (10-dars: "Algoritmlar amaliyot") — ikkalasi ham "yakunlangan, sinovdan o'tgan loyiha" g'oyasini kichik miqyosda ko'rsatgan edi. Bu — RankVault'ning haqiqiy, katta miqyosdagi yakuniy bosqichi. Va bu yerda capstone bo'ylab ko'rgan g'oyaning eng <strong>yalang'och</strong> ko'rinishi ochiladi: bu safar hatto <strong>CI'ning o'zi</strong> — sizni himoya qilishi kerak bo'lgan tizim — yolg'on signal berishi mumkin.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — CI: har bir push'da testlarni ishga tushirish</h4>
<pre><code># .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-fail-under=80</code></pre>

<h4>BLOKA 2 — Deploy FAQAT testlar muvaffaqiyatli bo'lganda</h4>
<pre><code># .github/workflows/deploy.yml
jobs:
  deploy:
    needs: test   # ❗ 'test' job MUVAFFAQIYATLI bo'lishi SHART - aks holda deploy ishga tushmaydi
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh</code></pre>

<h4>BLOKA 3 — mahalliy test skripti: chiqish kodini TO'G'RI uzatish</h4>
<pre><code>#!/bin/bash
# run_tests.sh - to'g'ri versiya
set -o pipefail   # ❗ MUHIM: pipeline'dagi BIRINCHI muvaffaqiyatsiz buyruq kodini saqlaydi

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Test skripti chiqish kodi: $?"   # endi pytest'ning HAQIQIY natijasi</code></pre>

<h3>🐛 Ataylab xato — bash pipeline'da chiqish kodi yo'qolishi</h3>
<pre><code>#!/bin/bash
# run_tests.sh - XATO versiya (set -o pipefail YO'Q)

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Testlar bajarildi, natija test_output.log'da saqlandi"
# ❌ 'exit 0' aniq yozilmagan bo'lsa ham, skript BARIBIR muvaffaqiyatli
# chiqadi - chunki oxirgi buyruq `tee`, va `tee` DEYARLI HAR DOIM
# muvaffaqiyatli bajariladi (u shunchaki oqimni faylga yozadi).

# Bash pipeline (cmd1 | cmd2)da, STANDART holda, chiqish kodi FAQAT
# OXIRGI buyruq (tee)nikini aks ettiradi - pytest'ning o'zi ICHIDA
# testlar MUVAFFAQIYATSIZ bo'lsa ham, bu HECH QANDAY ta'sir qilmaydi!

# CI natijasi:
# $ ./run_tests.sh; echo $?
# ... (pytest 3 ta testni FAIL qildi, lekin buni ko'rmaymiz) ...
# 0   ❌ "Muvaffaqiyatli" - garchi 3 ta test buzilgan bo'lsa ham!
#
# GitHub Actions bu skriptni "muvaffaqiyatli" deb hisoblaydi, "deploy"
# job'i ishga tushadi - BUZILGAN kod production'ga chiqadi.</code></pre>

<p><strong>Natija:</strong> bash'da <code>cmd1 | cmd2</code> pipeline yozilganda, <strong>standart</strong> xatti-harakat — butun pipeline'ning chiqish kodi <strong>faqat oxirgi</strong> buyruq (bu yerda <code>tee</code>)nikiga teng bo'ladi. <code>tee</code> esa deyarli hech qachon o'zi muvaffaqiyatsiz bo'lmaydi — u shunchaki kelayotgan oqimni faylga yozadi va ekranga chiqaradi. Shuning uchun <code>pytest</code>ning <strong>o'zi</strong> ichida testlar muvaffaqiyatsiz bo'lsa ham (chiqish kodi ≠ 0 bo'lsa ham), butun <code>pytest | tee ...</code> pipeline'i <strong>muvaffaqiyatli</strong> (chiqish kodi 0) deb hisoblanadi. CI tizimi bu chiqish kodiga qarab qaror qabul qiladi — "0 = muvaffaqiyatli, demak deploy qilsa bo'ladi" deb, <strong>buzilgan</strong> kodni ham production'ga chiqaradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Bash pipeline'da chiqish kodi standart holda nimani aks ettiradi?</h4>
<p><code>cmd1 | cmd2</code> yozilganda, bash standart sozlamada butun pipeline'ning chiqish kodi sifatida <strong>faqat oxirgi</strong> buyruq (<code>cmd2</code>)ning chiqish kodini qaytaradi. <code>cmd1</code> (bu yerda <code>pytest</code>) qanday chiqish kodi bilan tugagani <strong>e'tiborga olinmaydi</strong>.</p>

<h4>2. Nega <code>tee</code> deyarli har doim "muvaffaqiyatli" chiqadi?</h4>
<p><code>tee</code>ning vazifasi — kelayotgan matnli oqimni <strong>o'qib, faylga yozib, ekranga ham chiqarish</strong>. Bu vazifani bajarish uchun <code>tee</code>ga kiruvchi ma'lumotning "muvaffaqiyatli" yoki "muvaffaqiyatsiz" test natijasi ekanligi <strong>umuman ahamiyatsiz</strong> — u shunchaki matnni ko'chiradi va deyarli har doim 0 (muvaffaqiyat) bilan tugaydi.</p>

<h4>3. <code>set -o pipefail</code> nima qiladi?</h4>
<p>Bu bash sozlamasi pipeline'ning chiqish kodini <strong>oxirgi</strong> buyruqdan emas, balki pipeline ichidagi <strong>birinchi muvaffaqiyatsiz</strong> buyruqning chiqish kodidan olishga majburlaydi. Shu sozlama bilan, agar <code>pytest</code> muvaffaqiyatsiz bo'lsa, butun <code>pytest | tee ...</code> pipeline'i ham muvaffaqiyatsiz (nolga teng bo'lmagan chiqish kodi bilan) hisoblanadi — hatto <code>tee</code>ning o'zi muvaffaqiyatli bo'lsa ham.</p>

<h4>4. Nega bu xato ayniqsa xavfli?</h4>
<p>Bu xato CI'ning <strong>eng asosiy</strong> vazifasini — buzilgan kodni production'ga chiqishdan <strong>saqlashni</strong> — butunlay <strong>bekor</strong> qiladi. Boshqa capstone'lardagi xatolar (masalan noto'g'ri SQL, tekshiruvsiz cast) kodning <strong>bir qismini</strong> buzadi. Bu xato esa butun <strong>xavfsizlik tizimini</strong> (CI gate) ishlamay qo'yadi — endi HAR QANDAY xato (hatto oldingi darslarda o'rgangan barcha xatolar ham) hech qanday to'sqinliksiz production'ga chiqib ketishi mumkin.</p>

<h4>5. Bu 7 bosqichlik capstone'ning umumiy g'oyasini qanday yakunlaydi?</h4>
<p>1-6-darslarda siz "yashil test", "yuqori coverage" kabi <strong>metrikalarning o'zi</strong> ham to'g'rilikni kafolatlamasligini ko'rdingiz. Bu yerda esa <strong>eng yakuniy</strong> haqiqat ochiladi: hatto CI'ning "muvaffaqiyatli" degan <strong>o'zi</strong> ham, agar skriptning o'zida nozik xato bo'lsa, <strong>yolg'on</strong> bo'lishi mumkin. Bu — "yashil belgi ko'rish" bilan "haqiqatan to'g'ri ekanligiga ishonch hosil qilish" orasidagi farqni <strong>hech qachon</strong> unutmaslik kerakligini ko'rsatuvchi, capstone'ning yakuniy saboqi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Bash pipeline (<code>|</code>)da chiqish kodi standart holda faqat oxirgi buyruqnikini aks ettiradi</li>
<li>✅ <code>tee</code> kabi buyruqlar deyarli har doim muvaffaqiyatli chiqadi, oldingi buyruq natijasidan qat'i nazar</li>
<li>✅ <code>set -o pipefail</code> — pipeline'dagi birinchi muvaffaqiyatsiz buyruq kodini saqlab qolish uchun ishlatiladi</li>
<li>✅ Bunday xato CI'ning asosiy vazifasini (buzilgan kodni to'xtatish) butunlay bekor qiladi</li>
<li>✅ Hatto CI'ning "muvaffaqiyatli" signali ham, agar skriptning o'zida xato bo'lsa, yolg'on bo'lishi mumkin</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz RankVault'ni 1-bosqichdagi TDD siyosati hujjatidan boshlab, Flask API, PostgreSQL, ranking algoritmi, test coverage, HashMap cache va nihoyat <strong>to'g'ri, ishonchli CI/CD pipeline</strong>gacha qurdingiz. Bu capstone davomida siz Python: Testlash va Python: Algoritmlar va Ma'lumotlar Tuzilmasi kurslarida alohida o'rgangan bilimlarni <strong>bitta, real loyiha</strong>da birlashtirdingiz — va eng muhimi, boshqa to'rtta capstone'dan farqli, TypeScript'ning emas, balki <strong>testlarning va metrikalarning o'zi</strong> qanday yolg'on ishonch berishi mumkinligini yetti xil ko'rinishda ko'rdingiz: <strong>yashil test, yuqori coverage va "muvaffaqiyatli" CI — bularning hech biri, yakka o'zi, haqiqiy to'g'rilikni kafolatlamaydi.</strong></p>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 7-BOSQICH (CAPSTONE YAKUNI): Deploy va CI chiqish kodi xatosi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) .github/workflows/test.yml - har push'da testlarni ishga tushirish
# ─────────────────────────────────────────────────────────────────────

# name: Test
# on: [push]
# jobs:
#   test:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: pip install -r requirements.txt
#       - run: pytest --cov=app --cov-fail-under=80

# ─────────────────────────────────────────────────────────────────────
# 2) .github/workflows/deploy.yml - FAQAT testlar o'tgandan keyin
# ─────────────────────────────────────────────────────────────────────

# jobs:
#   deploy:
#     needs: test
#     runs-on: ubuntu-latest
#     steps:
#       - run: ./deploy.sh

# ─────────────────────────────────────────────────────────────────────
# 3) run_tests.sh - TO'G'RI versiya
# ─────────────────────────────────────────────────────────────────────

#!/bin/bash
set -o pipefail

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Test skripti chiqish kodi: $?"


# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - pipefail'siz skript (izohda)
# ─────────────────────────────────────────────────────────────────────

# #!/bin/bash
# # set -o pipefail YO'Q!
#
# pytest --cov=app --cov-fail-under=80 | tee test_output.log
# echo "Testlar bajarildi"
# # Chiqish kodi HAR DOIM tee'nikiga teng (deyarli har doim 0) -
# # pytest ICHIDA muvaffaqiyatsiz testlar bo'lsa ham CI buni "yashil"
# # deb hisoblaydi va BUZILGAN kodni deploy qiladi.
"""

L7_EX = [
    {
        "title": "Bash pipeline'da chiqish kodi standart holda nimani aks ettiradi?",
        "description": "cmd1 | cmd2 pipeline'i standart bash sozlamasida qaysi buyruqning chiqish kodini butun pipeline natijasi sifatida qaytaradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkala buyruqning ENG YOMON (eng katta) chiqish kodini",
            "Faqat OXIRGI buyruq (cmd2)ning chiqish kodini - cmd1 qanday tugagani e'tiborga olinmaydi",
            "Faqat BIRINCHI buyruq (cmd1)ning chiqish kodini",
            "Har doim 0 - pipeline'lar hech qachon muvaffaqiyatsiz bo'lmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu darsdagi xato aynan shu standart xatti-harakatdan kelib chiqadi.",
        "explanation": "Bash standart sozlamada pipeline'ning chiqish kodi sifatida faqat oxirgi buyruqning chiqish kodini qaytaradi - pipeline'dagi oldingi buyruqlar qanday tugagani e'tiborga olinmaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "set -o pipefail nima qiladi?",
        "description": "Bash skriptida set -o pipefail buyrug'i qo'shilishi pipeline'ning chiqish kodini qanday o'zgartiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Pipeline'ni butunlay o'chiradi",
            "Pipeline'ning chiqish kodini oxirgi buyruqdan emas, pipeline ichidagi BIRINCHI muvaffaqiyatsiz buyruqdan oladi",
            "Barcha buyruqlarni parallel ishga tushiradi",
            "Faqat tee buyrug'ining ishlashini tezlashtiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "'pipefail' so'zi 'pipeline muvaffaqiyatsizligi' degan ma'noni anglatadi.",
        "explanation": "set -o pipefail pipeline'ning chiqish kodini oxirgi buyruqdan emas, balki pipeline ichidagi birinchi muvaffaqiyatsiz buyruqning chiqish kodidan olishga majburlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Buzilgan kod qanday deploy bo'lib ketishini tartiblang",
        "description": "set -o pipefail bo'lmagan holatda, muvaffaqiyatsiz testlar qanday qilib baribir production'ga deploy bo'lib ketishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "pytest ichida 3 ta test MUVAFFAQIYATSIZ bo'ladi (pytest chiqish kodi ≠ 0)",
            "pytest | tee test_output.log pipeline'ida oxirgi buyruq (tee) muvaffaqiyatli bajariladi",
            "set -o pipefail yo'qligi uchun butun pipeline chiqish kodi 0 (tee'nikiga teng) bo'ladi",
            "CI skriptni 'muvaffaqiyatli' deb hisoblaydi, deploy job'i ishga tushib, buzilgan kod production'ga chiqadi",
        ],
        "correct_order": [
            "pytest ichida 3 ta test MUVAFFAQIYATSIZ bo'ladi (pytest chiqish kodi ≠ 0)",
            "pytest | tee test_output.log pipeline'ida oxirgi buyruq (tee) muvaffaqiyatli bajariladi",
            "set -o pipefail yo'qligi uchun butun pipeline chiqish kodi 0 (tee'nikiga teng) bo'ladi",
            "CI skriptni 'muvaffaqiyatli' deb hisoblaydi, deploy job'i ishga tushib, buzilgan kod production'ga chiqadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "tee buyrug'i deyarli har doim qanday chiqish kodi bilan tugaydi?",
        "description": "tee buyrug'i (kelayotgan oqimni faylga yozadigan) o'zi ODATDA qanday chiqish kodi bilan tugaydi, oldingi buyruq natijasidan qat'i nazar? (raqam bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "0",
        "hint": "0 - muvaffaqiyatni bildiradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bu xato boshqa capstone xatolaridan ko'ra jiddiyroq?",
        "description": (
            "CI'dagi bu 'chiqish kodi yo'qolishi' xatosi, oldingi "
            "darslardagi (masalan flaky testlar, off-by-one) xatolarga "
            "solishtirganda, nega ayniqsa jiddiy hisoblanadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Oldingi darslardagi xatolar (flaky testlar, off-by-one, "
            "tekshiruvsiz mock) odatda kodning MA'LUM BIR QISMIGA yoki "
            "bitta funksiyaga tegishli edi. Bu CI xatosi esa butun "
            "XAVFSIZLIK TIZIMINI (deploy'dan oldin testlarni majburiy "
            "tekshirish gate'ini) ishlamay qo'yadi - bu shuni anglatadiki, "
            "ENDI istalgan boshqa xato (hatto oldingi 6 darsda o'rgangan "
            "barcha xatolar ham, agar ular hali tuzatilmagan bo'lsa) hech "
            "qanday to'sqinliksiz, CI tomonidan 'ushlanmasdan' to'g'ridan-"
            "to'g'ri production'ga chiqib ketishi mumkin. Ya'ni bu xato "
            "boshqa barcha himoya choralarini samarasiz qilib qo'yadi."
        ),
        "hint": "Bu xato bitta funksiyaga ta'sir qiladimi, yoki BUTUN himoya tizimigami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L7_TASK = {
    "task_title": "RankVault — CAPSTONE yakuni: to'g'ri CI/CD bilan deploy qilingan loyiha",
    "task_description": (
        "RankVault'ni haqiqiy hostingga deploy qiling va CI pipeline "
        "(GitHub Actions) sozlang — testlar MUVAFFAQIYATSIZ bo'lganda "
        "deploy HECH QACHON ishga tushmasligini tasdiqlang. Barcha test "
        "skriptlarida chiqish kodi to'g'ri uzatilishini (set -o pipefail "
        "yoki tenglashtirilgan yechim) ta'minlang."
    ),
    "task_requirements": (
        "• .github/workflows/test.yml — har push'da pytest --cov=app ishga tushiriladi\n"
        "• .github/workflows/deploy.yml — deploy job'i 'needs: test' orqali test job'iga bog'liq\n"
        "• Barcha bash skriptlarida set -o pipefail (yoki teng yechim) ishlatilgan — pipeline chiqish kodi yo'qolmaydi\n"
        "• Qo'lda tekshiruv: ataylab bitta testni buzib, CI HAQIQATAN 'qizil' bo'lishini va deploy ISHGA TUSHMASLIGINI tasdiqlang\n"
        "• Flask backend haqiqiy hostingda ishlab turibdi\n"
        "• README.md: jonli havola, 7/7 bosqich yakunlangan checklist, CI/CD diagrammasi\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi"
    ),
    "task_technologies": "Python, Flask, pytest, GitHub Actions, Render/Railway",
    "task_deadline_days": 5,
}


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
                    [{"filename": "misol.py", "language": lang, "code": code}],
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
