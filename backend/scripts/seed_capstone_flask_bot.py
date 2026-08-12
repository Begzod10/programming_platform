"""Seed "Capstone 3: Flask + JavaScript + Telegram Bot" (7 lessons): the third
entry in the cross-course capstone track. Spans HTML/CSS + vanilla JavaScript
(no framework, no build step) + Flask (course 28) + Telegram Bot aiogram
(course 48), building "MoneyLog" — a personal expense tracker with a web app
AND a Telegram bot reading/writing the SAME database, sending monthly budget
alerts.

Key differentiator from the first two capstones: since vanilla JS needs no
build step, the frontend is served BY Flask itself (same origin) instead of
a separately-hosted SPA — so there's no CORS lesson here. Instead L3 teaches
a classic vanilla-JS gotcha (var-in-loop closure capture), and L2/L4/L5/L6/L7
each teach a Flask/SQLAlchemy-specific gotcha distinct from the Django/Node
capstones (jsonify serialization, forgetting password hashing, forgetting
app.app_context() in the bot, aggregate query missing a user filter, and a
relative static-path deploy bug).

Like the other capstones, every lesson carries a real project-submission
assignment via task_title/task_description/task_requirements/
task_technologies/task_deadline_days on Lesson (same mechanism as 255 other
lessons platform-wide) — students build ONE evolving project across all 7
milestones, resubmitting the same (updated) github_url/live_demo_url each
time via the existing Submission + AI-grading pipeline. No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_flask_bot
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
    "title": "Capstone 3: Flask + JavaScript + Telegram Bot",
    "description": (
        "Python Flask — O'rta daraja, JavaScript: Keyingi Bosqich va Telegram "
        "Bot aiogram kurslarini tugatgan dasturchilar uchun: HTML/CSS/vanilla "
        "JavaScript, Flask va Telegram Bot'ni BIR loyihada birlashtirasiz. 7 "
        "bosqichda 'MoneyLog' — shaxsiy xarajatlar kuzatuvchisini qurasiz: "
        "Flask backend, vanilla JS frontend (build qadamisiz, Flask'ning o'zi "
        "orqali serverlanadi) HAMDA matn orqali tezkor xarajat qo'shish va "
        "oylik byudjet ogohlantirishi beruvchi Telegram bot — hammasi bitta "
        "ma'lumotlar bazasi bilan ishlaydi. Har bir bosqich haqiqiy loyiha "
        "topshirig'i sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 8,  # Python
    "prerequisite_course_id": 28,  # Python Flask — O'rta daraja (also assumes HTML/CSS + JS Keyingi Bosqich, course 48: Telegram Bot aiogram)
    "is_active": True,
    "is_published": False,  # flip to True once all 7 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "DB schema (users, categories, expenses, telegram fields), repo scaffold, decide Flask serves the static frontend."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Flask backend API",
     "scope": "Flask-SQLAlchemy models + Blueprint JSON API for categories/expenses CRUD."},
    {"order": 2, "ref": "L3", "status": "done", "lang": "javascript",
     "title": "3-Vanilla JS frontend",
     "scope": "No-build-step JS served same-origin by Flask, DOM rendering, fetch()."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Autentifikatsiya",
     "scope": "Hand-rolled token auth with werkzeug.security password hashing."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Telegram bot: tezkor xarajat va hisob bog'lash",
     "scope": "aiogram bot parsing free-text expense messages, sharing the Flask-SQLAlchemy DB via app_context()."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Oylik hisobot va byudjet ogohlantirishi",
     "scope": "Scheduled job aggregating expenses per user, sending Telegram budget alerts."},
    {"order": 6, "ref": "L7", "status": "done",
     "title": "7-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "Deploy Flask (serving frontend) + bot as background worker; final README + live_demo_url."},
]


L1_TEXT = """\
<h2>MoneyLog — 7 bosqichda vanilla JS, Flask va Telegram Bot'ni birlashtirish</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> API["2-Flask API"]
    API --> FE["3-Vanilla JS frontend"]
    FE --> AUTH["4-Autentifikatsiya"]
    AUTH --> BOT["5-Bot: tezkor xarajat"]
    BOT --> REPORT["6-Oylik hisobot"]
    REPORT --> DEPLOY["7-Deploy"]
</pre>

<p>Bu safar HTML/CSS, <strong>vanilla</strong> JavaScript (React'siz), Flask va Telegram Bot'ni birlashtirasiz: <strong>MoneyLog</strong> — shaxsiy xarajatlar kuzatuvchisi. Web sahifa orqali ham, Telegram bot orqali (matn yozib!) ham xarajat qo'sha olasiz — ikkalasi bitta ma'lumotlar bazasi bilan ishlaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo tuzilmasi: nega frontend alohida deploy qilinmaydi?</h4>
<pre><code># MoneyLog uchun monorepo
moneylog/
  flask_backend/
    app/
      static/          # ❗ vanilla JS/CSS shu yerda - Flask'ning O'ZI serverlaydi!
      templates/        # ❗ index.html shu yerda
      models.py
      routes.py
    run.py
  telegram_bot/
    bot.py
  README.md

# ❗ MUHIM farq: React'dan farqli, vanilla JS'ga "build qadami" (webpack/vite)
#   kerak emas - brauzer .js faylni to'g'ridan-to'g'ri o'qiy oladi.
#   Shuning uchun alohida Vercel/Netlify shart EMAS - Flask frontend'ni
#   HAM o'zi serverlashi mumkin (bitta deploy, CORS ham kerak emas!)</code></pre>

<h4>BLOKA 2 — DB sxemasi: pul summasini TO'G'RI turda saqlash</h4>
<pre><code># MoneyLog uchun asosiy jadvallar:
#
# users            (id, ism, email, parol_hash, telegram_chat_id NULLABLE,
#                    link_kodi NULLABLE, oylik_byudjet NUMERIC(10,2))
# categories       (id, nomi, user_id -> users.id)
# expenses         (id, summa NUMERIC(10,2), tavsif, sana,
#                    category_id -> categories.id, user_id -> users.id,
#                    yaratilgan_vaqt)
#
# ❗ summa NUMERIC(10,2) - pul miqdorini ANIQ saqlash uchun,
#   FLOAT emas! (buni 3-BLOKAda ko'ramiz)</code></pre>

<h4>BLOKA 3 — README.md: uchta qismning holati</h4>
<pre><code># README.md
# MoneyLog

## Loyiha haqida
Shaxsiy xarajatlar kuzatuvchisi - Flask + vanilla JS + Telegram Bot,
bitta umumiy ma'lumotlar bazasi bilan.

## Texnologiyalar
- Backend: Flask, Flask-SQLAlchemy, PostgreSQL
- Frontend: HTML, CSS, vanilla JavaScript (Flask orqali serverlanadi)
- Bot: aiogram (Telegram)

## Holat
- [x] Loyihalash va repo skeleton
- [ ] Flask backend API
- [ ] Vanilla JS frontend
- [ ] Autentifikatsiya
- [ ] Telegram bot: tezkor xarajat va bog'lash
- [ ] Oylik hisobot va byudjet ogohlantirishi
- [ ] Deploy</code></pre>

<h3>🐛 Ataylab xato — pul summasini FLOAT sifatida rejalashtirish</h3>
<pre><code># ❌ XATO reja:
# expenses.summa = FLOAT  # "oddiy kasr son" kabi ko'rinadi, lekin...

# Python/JavaScript'da FLOAT bilan sinab ko'ring:
0.1 + 0.2 == 0.3     # ❌ False! (natija 0.30000000000000004 bo'ladi)

# Agar summa FLOAT'da saqlansa, 1000 ta 10.10 so'mlik xarajatni qo'shsangiz,
# yig'indi 10100.00 o'rniga 10099.999999999998 kabi noaniq son chiqishi mumkin!</code></pre>
<p><strong>Natija:</strong> <code>FLOAT</code> (yoki <code>double</code>) turi <strong>ikkilik</strong> (binary) tizimda saqlanadi, va ko'plab o'nlik kasrlar (masalan <code>0.1</code>) ikkilik tizimda <strong>aniq</strong> ifodalanmaydi — bu kichik, ammo real yig'indilash xatolariga olib keladi. Pul bilan ishlaydigan har qanday tizimda (MoneyLog kabi) bu <strong>jiddiy</strong> muammo: oylik hisobotlar bir necha tiyin farq bilan noto'g'ri chiqishi mumkin. To'g'ri yechim: <code>NUMERIC(10, 2)</code> (yoki Python'da <code>Decimal</code>) turini ishlatish — bu <strong>o'nlik</strong> tizimda aniq saqlaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega bu safar frontend uchun alohida hosting kerak emas?</h4>
<p>React kabi kutubxonalar <strong>build qadami</strong>ni (JSX'ni brauzer tushunadigan JS'ga aylantirish) talab qiladi, shuning uchun alohida statik hosting (Vercel/Netlify) qulay. Vanilla JS esa brauzer tomonidan <strong>to'g'ridan-to'g'ri</strong> o'qiladi — hech qanday build kerak emas, shuning uchun Flask uni <code>static/</code>/<code>templates/</code> orqali <strong>o'zi</strong> serverlashi mumkin. Bu CORS muammosini ham butunlay yo'q qiladi (hammasi bir xil origin'dan xizmat qiladi)!</p>

<h4>2. Nega <code>telegram_chat_id</code> va <code>link_kodi</code> yana kerak?</h4>
<p>Bu — ikkinchi capstone kursida ko'rgan naqshning davomi: foydalanuvchi web akkauntini Telegram akkaunti bilan bog'lash uchun. MoneyLog'da ham foydalanuvchi botga xarajat yozishi uchun, bot uni <strong>qaysi</strong> web foydalanuvchisi ekanini bilishi kerak.</p>

<h4>3. Nega <code>oylik_byudjet</code> maydoni <code>users</code> jadvaliga qo'shilgan?</h4>
<p>6-bosqichda foydalanuvchiga "byudjetdan oshib ketdingiz" degan ogohlantirish yuborish uchun, tizim har bir foydalanuvchining <strong>o'z</strong> byudjet chegarasini bilishi kerak — bu shaxsiy sozlama bo'lgani uchun <code>users</code> jadvalida saqlanadi.</p>

<h4>4. Nega <code>NUMERIC(10,2)</code>, oddiy <code>FLOAT</code> emas?</h4>
<p><code>FLOAT</code> ikkilik kasrlarda ishlaydi va ko'plab oddiy o'nlik sonlarni (masalan <code>0.1</code>) <strong>aniq</strong> ifodalay olmaydi — bu ko'p marta qo'shish/ayirishda kichik xatolar to'planishiga olib keladi. <code>NUMERIC(10,2)</code> (yoki <code>DECIMAL</code>) esa o'nlik sonlarni <strong>aynan</strong> saqlaydi — pul bilan ishlashda bu standart va <strong>majburiy</strong> amaliyot.</p>

<h4>5. Bu loyiha uchta alohida kursni qanday birlashtiradi?</h4>
<p>HTML/CSS va JavaScript (frontend), Flask (backend + ma'lumotlar bazasi) va Telegram Bot (aiogram) kurslarida <strong>alohida</strong> o'rgangan bilimlar endi <strong>bitta</strong>, real maqsad (shaxsiy moliyani kuzatish) uchun birlashadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Vanilla JS'ga build qadami kerak emas — Flask uni to'g'ridan-to'g'ri serverlashi mumkin (CORS'siz)</li>
<li>✅ <code>telegram_chat_id</code>/<code>link_kodi</code> — web va Telegram akkauntlarini bog'lash uchun</li>
<li>✅ Pul miqdori <strong>hech qachon</strong> <code>FLOAT</code>da saqlanmasligi kerak — <code>NUMERIC(10,2)</code> ishlatiladi</li>
<li>✅ Shaxsiy sozlamalar (masalan byudjet) tegishli foydalanuvchi yozuvida saqlanadi</li>
<li>✅ Bu kurs uchta texnologiyani (HTML/CSS/JS, Flask, Telegram Bot) bitta real loyihada birlashtiradi</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 1-BOSQICH: Loyihalash va repo skeleton
# ════════════════════════════════════════════════════════════════════

# Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.

db_sxemasi = {
    "users": {
        "id": "SERIAL PRIMARY KEY",
        "ism": "VARCHAR(100)",
        "email": "VARCHAR(255) UNIQUE",
        "parol_hash": "VARCHAR(255)",
        "telegram_chat_id": "BIGINT NULL",
        "link_kodi": "VARCHAR(10) NULL",
        "oylik_byudjet": "NUMERIC(10, 2) NULL",   # ❗ FLOAT emas!
    },
    "categories": {
        "id": "SERIAL PRIMARY KEY",
        "nomi": "VARCHAR(100)",
        "user_id": "INTEGER REFERENCES users(id)",
    },
    "expenses": {
        "id": "SERIAL PRIMARY KEY",
        "summa": "NUMERIC(10, 2)",                 # ❗ pul miqdori - aniq tur SHART
        "tavsif": "VARCHAR(200)",
        "sana": "DATE",
        "category_id": "INTEGER REFERENCES categories(id)",
        "user_id": "INTEGER REFERENCES users(id)",
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
}

print(db_sxemasi)

# ─────────────────────────────────────────────────────────────────────
# Repo tuzilmasi (izohda)
# ─────────────────────────────────────────────────────────────────────

# moneylog/
#   flask_backend/
#     app/
#       static/       <- vanilla JS/CSS shu yerda
#       templates/     <- index.html shu yerda
#       models.py
#       routes.py
#     run.py
#   telegram_bot/
#     bot.py
#   README.md

# ─────────────────────────────────────────────────────────────────────
# Ataylab xato - FLOAT bilan pul hisoblash (izohda)
# ─────────────────────────────────────────────────────────────────────

# print(0.1 + 0.2)          # 0.30000000000000004 - aniq emas!
# print(0.1 + 0.2 == 0.3)   # False
"""

L1_EX = [
    {
        "title": "Nega frontend bu safar alohida deploy qilinmaydi?",
        "description": "MoneyLog'da nega vanilla JS frontend alohida Vercel/Netlify'ga emas, Flask orqali serverlanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki vanilla JS Vercel'da ishlamaydi",
            "Vanilla JS'ga build qadami kerak emas, brauzer uni to'g'ridan-to'g'ri o'qiy oladi",
            "Chunki Flask boshqa hech narsani serverlay olmaydi",
            "Bu Flask'ning majburiy talabi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "React'ga JSX'ni JS'ga aylantirish uchun build kerak, vanilla JS'ga esa...",
        "explanation": "Vanilla JS hech qanday build qadamini (webpack/vite) talab qilmaydi — brauzer .js faylni to'g'ridan-to'g'ri o'qiy oladi, shuning uchun Flask uni static/templates orqali o'zi serverlashi mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Pul miqdori uchun to'g'ri ma'lumot turi",
        "description": "Pul summasini (masalan xarajat miqdorini) ma'lumotlar bazasida saqlash uchun qaysi tur to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": [
            "FLOAT, chunki u kasr sonlar uchun",
            "NUMERIC(10,2) yoki DECIMAL, chunki u o'nlik sonlarni aniq saqlaydi",
            "VARCHAR, matn sifatida saqlash xavfsizroq",
            "INTEGER, chunki u eng tez tur",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "0.1 + 0.2 == 0.3 natijasini FLOAT bilan sinab ko'ring.",
        "explanation": "NUMERIC(10,2) (yoki DECIMAL) o'nlik sonlarni aniq saqlaydi, FLOAT esa ikkilik tizimda ishlagani uchun ko'plab o'nlik kasrlarni aniq ifodalay olmaydi — bu pul hisob-kitoblarida jiddiy xatolarga olib keladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "MoneyLog repo tuzilmasini mantiqiy tartibda joylang",
        "description": "moneylog/ repo'sidagi papkalarning vazifasini mos ravishda tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "flask_backend/app/static/ — vanilla JS va CSS fayllari saqlanadi",
            "flask_backend/app/templates/ — index.html saqlanadi",
            "flask_backend/app/models.py — Flask-SQLAlchemy modellari",
            "telegram_bot/bot.py — aiogram bot, xuddi shu bazaga ulanadi",
        ],
        "correct_order": [
            "flask_backend/app/static/ — vanilla JS va CSS fayllari saqlanadi",
            "flask_backend/app/templates/ — index.html saqlanadi",
            "flask_backend/app/models.py — Flask-SQLAlchemy modellari",
            "telegram_bot/bot.py — aiogram bot, xuddi shu bazaga ulanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "0.1 + 0.2 natijasi FLOAT'da",
        "description": "Python yoki JavaScript'da 0.1 + 0.2 == 0.3 ifodasi FLOAT bilan True qaytaradimi yoki False? (javobingizni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "False",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega FLOAT bilan pul hisoblash xavfli?",
        "description": (
            "Agar expenses.summa maydoni FLOAT sifatida saqlansa, va "
            "minglab xarajat yozuvlari qo'shilib, umumiy yig'indi "
            "hisoblansa, bu qanday muammoga olib kelishi mumkin? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "FLOAT turi sonlarni ikkilik (binary) tizimda saqlaydi, va "
            "0.1 kabi ko'plab oddiy o'nlik kasrlarni bu tizimda aynan "
            "ifodalab bo'lmaydi — buning o'rniga ularga juda yaqin, "
            "lekin aynan bir xil bo'lmagan qiymat saqlanadi. Bitta "
            "xarajat uchun bu farq juda kichik va sezilmasligi mumkin, "
            "lekin minglab yozuv qo'shilib, ular yig'indisi hisoblanganda, "
            "bu kichik xatolar to'planib, umumiy summa kutilgan aniq "
            "qiymatdan (masalan bir necha tiyin) farq qilishi mumkin — "
            "bu moliyaviy tizimda jiddiy, ishonchsizlik tug'diruvchi "
            "muammo hisoblanadi."
        ),
        "hint": "FLOAT ikkilik tizimda ishlaydi - bu o'nlik kasrlarni har doim ANIQ ifodalay oladimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "MoneyLog — repo skeleton va DB sxema hujjati",
    "task_description": (
        "MoneyLog loyihasi uchun GitHub'da monorepo yarating (flask_backend/, "
        "telegram_bot/ papkalari bilan), to'liq README.md yozing va users/"
        "categories/expenses jadvallari uchun DB sxemasini README'ga qo'shing. "
        "Sxemada pul summasi uchun NUMERIC(10,2) turi ishlatilganini va nega "
        "FLOAT emasligini tushuntiring."
    ),
    "task_requirements": (
        "• GitHub'da 'moneylog' nomli public repo yaratilgan\n"
        "• flask_backend/ (app/static/, app/templates/ bilan) va telegram_bot/ papkalari mavjud\n"
        "• README.md: loyiha tavsifi, texnologiyalar, holat checklist'i\n"
        "• README.md'da users (telegram_chat_id, link_kodi, oylik_byudjet bilan), "
        "categories, expenses jadvallari va bog'lanishlari tasvirlangan\n"
        "• README'da summa maydoni nega NUMERIC(10,2) (FLOAT emas) ekanligi 2-3 gapda tushuntirilgan\n"
        "• .gitignore fayli mavjud (venv, .env, __pycache__ chiqarib tashlangan)"
    ),
    "task_technologies": "Git, GitHub, Markdown, PostgreSQL (sxema loyihalash)",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Flask backend API — Category va Expense uchun CRUD</h2>

<pre class="mermaid">
flowchart LR
    MODEL["Flask-SQLAlchemy modeli"] --> DICT["to_dict() - JSON-mos dict"]
    DICT --> JSONIFY["jsonify(dict) - to'g'ri ishlaydi"]
    MODEL -->|to'g'ridan-to'g'ri jsonify()| ERROR["TypeError: Object of type Expense is not JSON serializable"]
</pre>

<p>Flask O'rta daraja kursida Flask-SQLAlchemy va REST API'ni allaqachon ko'rgansiz. Bu bosqichda ularni <strong>Blueprint</strong> orqali tuzilgan, vanilla JS frontend (3-darsda) va Telegram bot (5-darsda) <strong>ikkalasi ham</strong> foydalanadigan JSON API sifatida quramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Flask-SQLAlchemy modellari (1-darsdagi sxemadan)</h4>
<pre><code># app/models.py
from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summa = db.Column(db.Numeric(10, 2), nullable=False)   # ❗ 1-darsdagidek - NUMERIC
    tavsif = db.Column(db.String(200))
    sana = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):                          # ❗ modelni JSON-mos dict'ga aylantiradi
        return {
            "id": self.id,
            "summa": float(self.summa),           # ❗ Decimal ham JSON'ning standart turi emas!
            "tavsif": self.tavsif,
            "sana": self.sana.isoformat(),         # ❗ date ham matnga aylantiriladi
            "category_nomi": self.category.nomi,
        }</code></pre>

<h4>BLOKA 2 — Blueprint orqali JSON API</h4>
<pre><code># app/routes.py
from flask import Blueprint, jsonify, request
from app import db
from app.models import Expense, Category

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/expenses', methods=['GET'])
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=1).all()   # ❗ 4-darsda request.user bilan almashtiriladi
    return jsonify([x.to_dict() for x in xarajatlar])         # ❗ to_dict() orqali - TO'G'RI

@api.route('/expenses', methods=['POST'])
def expense_yaratish():
    ma_lumot = request.get_json()
    yangi = Expense(
        summa=ma_lumot["summa"], tavsif=ma_lumot.get("tavsif", ""),
        sana=ma_lumot["sana"], category_id=ma_lumot["category_id"], user_id=1,
    )
    db.session.add(yangi)
    db.session.commit()
    return jsonify(yangi.to_dict()), 201</code></pre>

<h4>BLOKA 3 — app/__init__.py: Blueprint'ni ro'yxatdan o'tkazish</h4>
<pre><code># app/__init__.py (Application Factory pattern - 1-darsdagi Flask O'rta daraja kursidan tanish)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = '...'
    db.init_app(app)

    from app.routes import api
    app.register_blueprint(api)

    return app</code></pre>

<h3>🐛 Ataylab xato — model obyektini to'g'ridan-to'g'ri jsonify() qilish</h3>
<pre><code>@api.route('/expenses/<int:id>')
def expense_korish(id):
    xarajat = Expense.query.get_or_404(id)
    return jsonify(xarajat)   # ❌ to_dict() ISHLATILMAGAN!

# So'rov yuborilganda:
# ❌ TypeError: Object of type Expense is not JSON serializable
# (Flask'ning jsonify()i Expense obyektini "tushunmaydi" - u faqat
#  dict, list, string, son kabi oddiy Python turlarini kutadi)</code></pre>

<p><strong>Natija:</strong> <code>jsonify()</code> faqat Python'ning <strong>standart</strong> turlarini (dict, list, str, int, float, bool, None) JSON'ga aylantira oladi. <code>Expense</code> — bu <strong>maxsus</strong> Python klassi (SQLAlchemy modeli), va <code>jsonify()</code> uni qanday JSON'ga aylantirishni "bilmaydi" — shuning uchun <code>TypeError</code> beradi. Yechim: modelni <strong>avval</strong> <code>to_dict()</code> orqali oddiy <code>dict</code>ga aylantirish, <strong>keyin</strong> shu dict'ni <code>jsonify()</code>ga berish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega <code>to_dict()</code> metodi model klassining o'ziga yoziladi?</h4>
<p>Bu — kodni <strong>tartibli</strong> saqlash uchun yaxshi amaliyot: har bir model o'zining JSON-ga qanday "tarjima qilinishini" o'zi biladi. Bu logikani har bir route funksiyasida qayta yozmaslik imkonini beradi.</p>

<h4>2. Nega <code>float(self.summa)</code> ishlatiladi?</h4>
<p><code>summa</code> ustuni <code>Numeric</code> turida, va Python'da bu <code>Decimal</code> obyekti sifatida qaytadi. <code>Decimal</code> ham <code>jsonify()</code>ning standart qo'llab-quvvatlaydigan turlaridan <strong>emas</strong> — shuning uchun uni JSON'ga chiqarishdan oldin <code>float()</code>ga aylantirish kerak (1-darsda ta'kidlangan "saqlashda aniqlik" muhimligi bazada saqlash va hisoblashga tegishli, JSON orqali <strong>bitta</strong> qiymatni ko'rsatishda emas).</p>

<h4>3. Application Factory pattern (<code>create_app()</code>) nega ishlatiladi?</h4>
<p>Bu — Flask O'rta daraja kursining 1-darsida ko'rgan naqsh: <code>Flask</code> ilovasini funksiya ichida yaratish, turli konfiguratsiyalar (test, production) bilan moslashuvchan ishlatish imkonini beradi.</p>

<h4>4. Blueprint nima uchun ishlatiladi?</h4>
<p><code>Blueprint</code> — Flask O'rta daraja kursining 2-darsida ko'rgan naqsh: route'larni <strong>alohida, tartibli</strong> modulga ajratish imkonini beradi. Loyiha kattalashganda (masalan bot uchun ham qo'shimcha route'lar qo'shilsa), bu tuzilma saqlab qolinadi.</p>

<h4>5. Nega model obyektini to'g'ridan-to'g'ri <code>jsonify()</code>ga berish xato beradi?</h4>
<p><code>jsonify()</code> ichki tomondan Python'ning standart <code>json</code> modulidan foydalanadi, u esa faqat <strong>oddiy</strong> turlarni (dict, list va h.k.) qanday "seriyalashtirish"ni biladi. <code>Expense</code> klassi maxsus Python obyekti bo'lgani uchun, <code>json</code> moduli uni qanday matn (JSON)ga aylantirishni "bilmaydi" va xato beradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Model klassiga <code>to_dict()</code> metodini qo'shish — JSON API uchun tartibli amaliyot</li>
<li>✅ <code>Decimal</code> (Numeric ustunlar) JSON'ga chiqarishdan oldin <code>float()</code>ga aylantirilishi kerak</li>
<li>✅ Application Factory va Blueprint — Flask O'rta daraja kursidan tanish naqshlar, bu yerda ham qo'llaniladi</li>
<li>✅ <code>jsonify()</code> faqat oddiy Python turlarini (dict, list, str, son) qo'llab-quvvatlaydi</li>
<li>✅ Model obyektini to'g'ridan-to'g'ri <code>jsonify()</code>ga berish <code>TypeError</code> beradi — avval <code>to_dict()</code> kerak</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 2-BOSQICH: Flask backend API - Category va Expense uchun CRUD
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/models.py
# ─────────────────────────────────────────────────────────────────────

from app import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summa = db.Column(db.Numeric(10, 2), nullable=False)
    tavsif = db.Column(db.String(200))
    sana = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.relationship('Category')

    def to_dict(self):
        return {
            "id": self.id,
            "summa": float(self.summa),
            "tavsif": self.tavsif,
            "sana": self.sana.isoformat(),
            "category_nomi": self.category.nomi,
        }

# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - Blueprint orqali JSON API
# ─────────────────────────────────────────────────────────────────────

from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/expenses', methods=['GET'])
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=1).all()
    return jsonify([x.to_dict() for x in xarajatlar])


@api.route('/expenses', methods=['POST'])
def expense_yaratish():
    ma_lumot = request.get_json()
    yangi = Expense(
        summa=ma_lumot["summa"], tavsif=ma_lumot.get("tavsif", ""),
        sana=ma_lumot["sana"], category_id=ma_lumot["category_id"], user_id=1,
    )
    db.session.add(yangi)
    db.session.commit()
    return jsonify(yangi.to_dict()), 201

# ─────────────────────────────────────────────────────────────────────
# 3) app/__init__.py (izohda - Application Factory)
# ─────────────────────────────────────────────────────────────────────

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy()
#
# def create_app():
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = '...'
#     db.init_app(app)
#     from app.routes import api
#     app.register_blueprint(api)
#     return app

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - model obyektini to'g'ridan-to'g'ri jsonify() (izohda)
# ─────────────────────────────────────────────────────────────────────

# @api.route('/expenses/<int:id>')
# def expense_korish_xato(id):
#     xarajat = Expense.query.get_or_404(id)
#     return jsonify(xarajat)   # to_dict() ISHLATILMAGAN!
# ❌ TypeError: Object of type Expense is not JSON serializable
"""

L2_EX = [
    {
        "title": "to_dict() metodi nima uchun kerak?",
        "description": "Nega Expense modeliga to_dict() metodi qo'shiladi, model obyekti to'g'ridan-to'g'ri jsonify()ga berilmaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu kodni tezroq ishlashini ta'minlaydi",
            "jsonify() faqat oddiy Python turlarini (dict, list) qo'llab-quvvatlaydi, model obyekti esa maxsus klass",
            "Bu Flask'ning majburiy sintaksisi",
            "Faqat debugging uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "jsonify() qanday turlarni \"tushunadi\"?",
        "explanation": "jsonify() faqat Python'ning standart turlarini (dict, list, str, son) JSON'ga aylantira oladi — model obyekti maxsus klass bo'lgani uchun, avval to_dict() orqali oddiy dict'ga aylantirilishi kerak.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega float(self.summa) ishlatiladi?",
        "description": "to_dict() metodida summa maydoni nega to'g'ridan-to'g'ri emas, float(self.summa) orqali qaytariladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu tasodifiy tanlangan, ahamiyati yo'q",
            "Numeric ustun Python'da Decimal sifatida qaytadi, u ham jsonify()ning standart turi emas",
            "Chunki float har doim aniqroq",
            "Chunki Numeric ustunlar avtomatik xato beradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "db.Numeric ustuni Python'da qanday turga aylanadi?",
        "explanation": "Numeric ustun Python'da Decimal obyekti sifatida qaytadi, va Decimal ham jsonify()ning standart qo'llab-quvvatlaydigan turlaridan emas — shuning uchun JSON'ga chiqarishdan oldin float()ga aylantiriladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "GET /api/expenses so'rovi jarayonini tartiblang",
        "description": "Vanilla JS'dan GET /api/expenses so'rovi kelganda expenses_royxati() ichida bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Expense.query.filter_by(user_id=1).all() orqali ma'lumot olinadi",
            "Har bir Expense obyekti to_dict() orqali oddiy dict'ga aylantiriladi",
            "Dict'lar ro'yxati jsonify() ga beriladi",
            "JSON javob brauzerga qaytariladi",
        ],
        "correct_order": [
            "Expense.query.filter_by(user_id=1).all() orqali ma'lumot olinadi",
            "Har bir Expense obyekti to_dict() orqali oddiy dict'ga aylantiriladi",
            "Dict'lar ro'yxati jsonify() ga beriladi",
            "JSON javob brauzerga qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Route'larni alohida modulga ajratuvchi Flask vositasi",
        "description": "Flask'da route'larni alohida, tartibli modulga ajratish uchun ishlatiladigan vositani yozing (Flask O'rta daraja kursidan tanish).",
        "exercise_type": "text_input",
        "expected_answer": "Blueprint",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega model obyektini to'g'ridan-to'g'ri jsonify() qilish TypeError beradi?",
        "description": (
            "expense_korish_xato() funksiyasida jsonify(xarajat) "
            "to_dict()siz chaqirilsa (xarajat — Expense obyekti), nega "
            "Flask \"TypeError: Object of type Expense is not JSON "
            "serializable\" xatosini beradi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "jsonify() ichki tomondan Python'ning standart json "
            "modulidan foydalanadi, u esa faqat dict, list, str, son "
            "kabi oddiy, \"tanish\" Python turlarini JSON matniga qanday "
            "aylantirishni biladi. Expense klassi esa SQLAlchemy "
            "tomonidan yaratilgan maxsus Python obyekti — json moduli "
            "bu maxsus klassni qanday JSON ko'rinishiga \"tarjima "
            "qilish\" kerakligini oldindan bilmaydi, shuning uchun uni "
            "\"seriyalashtirib bo'lmaydigan\" (not JSON serializable) "
            "deb hisoblab TypeError xatosini beradi. to_dict() metodi "
            "aynan shu \"tarjima\"ni qo'lda amalga oshiradi, shundan "
            "keyingina natija jsonify() uchun tanish, oddiy dict "
            "shaklida bo'ladi."
        ),
        "hint": "jsonify() (yoki uning ichidagi json moduli) qanday turlarni \"tanийdi\", va Expense klassi shu turlardan birimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "MoneyLog — Flask backend API (Category + Expense)",
    "task_description": (
        "1-bosqichdagi sxema asosida Category va Expense Flask-SQLAlchemy "
        "modellarini yarating, migratsiya qiling. Har ikkalasiga to_dict() "
        "metodini qo'shing. Blueprint orqali GET va POST so'rovlarini "
        "qo'llab-quvvatlovchi JSON API quring."
    ),
    "task_requirements": (
        "• Category va Expense modellari to'g'ri ForeignKey'lar bilan yaratilgan\n"
        "• summa ustuni Numeric(10,2) turida (FLOAT emas)\n"
        "• Har ikkala modelda to_dict() metodi mavjud, Decimal/date to'g'ri JSON-mos qilingan\n"
        "• GET /api/expenses — barcha xarajatlarni category_nomi bilan birga JSON ro'yxat sifatida qaytaradi\n"
        "• POST /api/expenses — yangi xarajat yaratadi, 201 qaytaradi\n"
        "• Route'lar Blueprint orqali tashkil qilingan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Flask, Flask-SQLAlchemy, PostgreSQL",
    "task_deadline_days": 5,
}


L3_TEXT = """\
<h2>3-bosqich: Vanilla JS frontend — Flask orqali serverlanadi</h2>

<pre class="mermaid">
flowchart LR
    HTML["templates/index.html"] -->|Flask render_template| BROWSER["Brauzer"]
    BROWSER -->|fetch('/api/expenses')| SAMEORIGIN["Bir xil origin - CORS kerak emas!"]
    RENDER["Ro'yxatni chizish"] -->|var bilan sikl| BUG["Barcha tugmalar OXIRGI elementga ishora qiladi"]
</pre>

<p>1-darsda qaror qilganimizdek, vanilla JS'ga build kerak emas — shuning uchun bu bosqichda frontend to'g'ridan-to'g'ri <strong>Flask'ning o'zi</strong> orqali serverlanadi. Bu CORS muammosini butunlay yo'q qiladi, lekin vanilla JS'ning o'ziga xos, <strong>klassik</strong> bir muammosi bilan tanishasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Flask'da statik sahifani ko'rsatish</h4>
<pre><code># app/routes.py
from flask import render_template

@api.route('/')
def bosh_sahifa():
    return render_template('index.html')   # ❗ templates/index.html'ni ko'rsatadi

# app/templates/index.html
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
  &lt;link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"&gt;
&lt;/head&gt;
&lt;body&gt;
  &lt;ul id="xarajatlar-royxati"&gt;&lt;/ul&gt;
  &lt;script src="{{ url_for('static', filename='app.js') }}"&gt;&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>

<h4>BLOKA 2 — vanilla JS bilan ma'lumot olish va chizish</h4>
<pre><code>// app/static/app.js
async function xarajatlarniYuklash() {
  const javob = await fetch('/api/expenses');       // ❗ NISBIY manzil - CORS kerak emas, bir xil origin!
  const xarajatlar = await javob.json();

  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  xarajatlar.forEach((x) => {                        // ❗ forEach - har bir elementga o'z 'x' beradi
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm`;
    royxat.appendChild(li);
  });
}

xarajatlarniYuklash();</code></pre>

<h4>BLOKA 3 — har bir elementga alohida tugma qo'shish (let bilan TO'G'RI)</h4>
<pre><code>function royxatniChizish(xarajatlar) {
  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  for (let i = 0; i &lt; xarajatlar.length; i++) {      // ❗ 'let' - har bir iteratsiya o'ZINING 'i'siga ega
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm `;

    const ochirishTugmasi = document.createElement('button');
    ochirishTugmasi.textContent = "O'chirish";
    ochirishTugmasi.addEventListener('click', () => {
      xarajatniOchirish(x.id);                        // ❗ 'let' tufayli - HAR BIR tugma O'Z x.id'siga ishora qiladi
    });

    li.appendChild(ochirishTugmasi);
    royxat.appendChild(li);
  }
}</code></pre>

<h3>🐛 Ataylab xato — sikl o'zgaruvchisi uchun 'let' o'rniga 'var' ishlatish</h3>
<pre><code>function royxatniChizishXato(xarajatlar) {
  for (var i = 0; i &lt; xarajatlar.length; i++) {      // ❌ 'var' ishlatilgan!
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = x.tavsif;

    const tugma = document.createElement('button');
    tugma.addEventListener('click', () => {
      console.log(i);   // ❌ HAR BIR tugma bosilganda - doim OXIRGI 'i' qiymatini chiqaradi!
    });
    li.appendChild(tugma);
    royxat.appendChild(li);
  }
}
// 5 ta xarajat bo'lsa, BARCHA 5 ta tugma ham "4" (oxirgi indeks) ni chiqaradi -
// garchi ular turli qatorlarda joylashgan bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> <code>var</code> bilan e'lon qilingan o'zgaruvchi <strong>funksiya darajasida</strong> (function-scoped) mavjud bo'ladi — sikl tugagach, <strong>bitta</strong> <code>i</code> o'zgaruvchisi qoladi, va u siklning <strong>oxirgi</strong> qiymatiga ega bo'ladi. Barcha <code>addEventListener</code> callback'lari bu <strong>bitta, umumiy</strong> <code>i</code>ga "yopishib qoladi" (closure), shuning uchun tugma qachon bosilishidan qat'i nazar, ular hammasi <strong>oxirgi</strong> qiymatni ko'radi. <code>let</code> esa <strong>har bir iteratsiya</strong> uchun <strong>yangi, alohida</strong> o'zgaruvchi yaratadi — shuning uchun har bir callback o'zining "muzlatilgan" qiymatiga ega bo'ladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega bu safar CORS kerak emas?</h4>
<p>Frontend (<code>index.html</code>, <code>app.js</code>) va backend (<code>/api/expenses</code>) <strong>bir xil</strong> Flask serveridan, <strong>bir xil</strong> origin (domen+port)dan xizmat qiladi. Brauzerning Same-Origin Policy'si faqat <strong>turli</strong> origin'lar orasidagi so'rovlarga tegishli — bu yerda bunday farq umuman yo'q.</p>

<h4>2. <code>closure</code> nima?</h4>
<p>Closure — funksiya o'zi yaratilgan paytdagi <strong>tashqi o'zgaruvchilarni</strong> "eslab qoladigan" xususiyati. <code>addEventListener</code>ga berilgan har bir callback funksiya — o'sha paytdagi <code>i</code> (yoki <code>x</code>) o'zgaruvchisini "eslab qoladi", lekin <strong>qaysi</strong> <code>i</code>ni eslab qolishi <code>var</code> yoki <code>let</code>ga bog'liq.</p>

<h4>3. Nega <code>let</code> bu muammoni hal qiladi?</h4>
<p><code>let</code> <strong>blok darajasida</strong> (block-scoped) ishlaydi — <code>for</code> siklining har bir aylanishida <code>let i</code> <strong>yangi nusxa</strong> yaratadi. Shuning uchun har bir callback o'zining <strong>alohida</strong> <code>i</code> nusxasiga "yopishadi", umumiy, oxirgi qiymatga emas.</p>

<h4>4. Nega bu xato ko'pincha "tasodifiy" ko'rinadi?</h4>
<p>Kod <strong>yozilganda</strong> to'g'ri ishlayotgandek ko'rinadi — ro'yxat to'g'ri chiziladi, tugmalar ham ko'rinadi. Muammo faqat foydalanuvchi <strong>tugmani bosganda</strong> paydo bo'ladi, va natija har doim <strong>oxirgi</strong> elementga tegishli bo'ladi — bu debug qilishni qiyinlashtiradi, chunki xato kod yozish paytida emas, foydalanuvchi harakati vaqtida namoyon bo'ladi.</p>

<h4>5. Bu xato nega <code>forEach</code>da yuzaga kelmaydi?</h4>
<p><code>forEach((x) => {...})</code>dagi <code>x</code> — har bir chaqiruv uchun <strong>yangi</strong> parametr sifatida beriladi (JavaScript funksiya parametrlari doim shu tarzda ishlaydi), shuning uchun <code>forEach</code> bilan bu muammo tabiiy ravishda yuzaga kelmaydi. Muammo faqat qo'lda yozilgan <code>for (var i = ...)</code> siklida, tashqi <code>i</code> o'zgaruvchisiga to'g'ridan-to'g'ri murojaat qilinganda paydo bo'ladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Bir xil origin'dan xizmat qilingan frontend/backend uchun CORS kerak emas</li>
<li>✅ Closure — funksiyaning tashqi o'zgaruvchilarni "eslab qolish" xususiyati</li>
<li>✅ <code>var</code> — function-scoped (bitta umumiy nusxa), <code>let</code> — block-scoped (har iteratsiya uchun alohida nusxa)</li>
<li>✅ <code>for</code> siklida event listener'lar bilan ishlaganda har doim <code>let</code> ishlatish kerak, <code>var</code> emas</li>
<li>✅ <code>forEach</code>'da bu muammo yuzaga kelmaydi, chunki parametr har chaqiruv uchun yangi beriladi</li>
</ul>
"""

L3_CODE = """\
// ════════════════════════════════════════════════════════════════════
// 3-BOSQICH: Vanilla JS frontend - Flask orqali serverlanadi
// ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) app/static/app.js - ma'lumot olish va chizish
// ─────────────────────────────────────────────────────────────────────

async function xarajatlarniYuklash() {
  const javob = await fetch('/api/expenses');
  const xarajatlar = await javob.json();
  royxatniChizish(xarajatlar);
}

// ─────────────────────────────────────────────────────────────────────
// 2) TO'G'RI: let bilan sikl - har bir tugma o'z x.id'siga ishora qiladi
// ─────────────────────────────────────────────────────────────────────

function royxatniChizish(xarajatlar) {
  const royxat = document.getElementById('xarajatlar-royxati');
  royxat.innerHTML = '';

  for (let i = 0; i < xarajatlar.length; i++) {
    const x = xarajatlar[i];
    const li = document.createElement('li');
    li.textContent = `${x.tavsif}: ${x.summa} so'm `;

    const ochirishTugmasi = document.createElement('button');
    ochirishTugmasi.textContent = "O'chirish";
    ochirishTugmasi.addEventListener('click', () => {
      xarajatniOchirish(x.id);
    });

    li.appendChild(ochirishTugmasi);
    royxat.appendChild(li);
  }
}

async function xarajatniOchirish(id) {
  await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
  xarajatlarniYuklash();
}

xarajatlarniYuklash();

// ─────────────────────────────────────────────────────────────────────
// 3) Ataylab xato - 'var' bilan sikl (izohda)
// ─────────────────────────────────────────────────────────────────────

// function royxatniChizishXato(xarajatlar) {
//   for (var i = 0; i < xarajatlar.length; i++) {   // var ishlatilgan!
//     const tugma = document.createElement('button');
//     tugma.addEventListener('click', () => {
//       console.log(i);   // HAR DOIM oxirgi qiymatni chiqaradi!
//     });
//   }
// }
"""

L3_EX = [
    {
        "title": "Nega bu safar CORS kerak emas?",
        "description": "MoneyLog'da vanilla JS frontend va Flask API orasida nega CORS sozlash kerak emas?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki vanilla JS CORS'ni qo'llab-quvvatlamaydi",
            "Frontend va backend bir xil Flask serveridan, bir xil origin'dan xizmat qiladi",
            "Chunki fetch() CORS'ni avtomatik o'chiradi",
            "Bu Flask'ning yashirin xususiyati",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "CORS faqat TURLI origin'lar orasida kerak bo'ladi.",
        "explanation": "Frontend (index.html, app.js) va backend (/api/expenses) bir xil Flask serveridan, bir xil origin'dan xizmat qilgani uchun, Same-Origin Policy bunga taalluqli emas.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "var va let orasidagi asosiy farq",
        "description": "for siklida var va let ishlatilishi orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ular butunlay bir xil ishlaydi",
            "var function-scoped (bitta umumiy nusxa), let esa block-scoped (har iteratsiya uchun alohida nusxa)",
            "let faqat raqamlar uchun, var faqat matnlar uchun",
            "var eskirgan va ishlamaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu closure'lar bilan ishlashda katta farq yaratadi.",
        "explanation": "var function-scoped bo'lib, butun sikl uchun bitta umumiy o'zgaruvchi yaratadi. let esa block-scoped bo'lib, har bir iteratsiya uchun yangi, alohida nusxa yaratadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "royxatniChizish() ishlash jarayonini tartiblang",
        "description": "xarajatlarniYuklash() chaqirilgandan, ro'yxat va tugmalar to'g'ri chizilishigacha bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "fetch('/api/expenses') orqali ma'lumot olinadi",
            "royxatniChizish(xarajatlar) chaqiriladi",
            "for (let i = ...) sikli har bir xarajat uchun <li> va tugma yaratadi",
            "Har bir tugmaga addEventListener orqali o'z x.id'siga bog'langan click handler qo'shiladi",
        ],
        "correct_order": [
            "fetch('/api/expenses') orqali ma'lumot olinadi",
            "royxatniChizish(xarajatlar) chaqiriladi",
            "for (let i = ...) sikli har bir xarajat uchun <li> va tugma yaratadi",
            "Har bir tugmaga addEventListener orqali o'z x.id'siga bog'langan click handler qo'shiladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bu muammo yuzaga kelmaydigan usul",
        "description": "for (var i = ...) o'rniga qaysi massiv metodini ishlatish bu closure muammosini tabiiy ravishda oldini oladi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "forEach",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega var bilan barcha tugmalar oxirgi qiymatga ishora qiladi?",
        "description": (
            "for (var i = 0; ...) siklida yaratilgan har bir tugmaga "
            "addEventListener('click', () => console.log(i)) qo'shilsa, "
            "nega BARCHA tugmalar bosilganda bir xil, OXIRGI 'i' "
            "qiymatini chiqaradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "var kalit so'zi bilan e'lon qilingan o'zgaruvchi function-"
            "scoped, ya'ni butun funksiya (yoki global) darajasida "
            "mavjud bo'ladi - sikl har safar YANGI i yaratmaydi, balki "
            "bitta, UMUMIY i o'zgaruvchisini o'zgartiradi. Sikl "
            "tugagach, bu bitta i o'zgaruvchisi eng oxirgi qiymatga ega "
            "bo'lib qoladi. Har bir addEventListener'ga berilgan "
            "callback funksiya closure orqali aynan shu BITTA, umumiy i "
            "o'zgaruvchisiga \"ishora qiladi\" (uni nusxalab olmaydi, "
            "balki unga havola saqlaydi). Shuning uchun foydalanuvchi "
            "istalgan tugmani bossa ham, barcha callback'lar bir xil, "
            "siklning oxirida qolgan qiymatni ko'rsatadi."
        ),
        "hint": "var function-scoped - bu sikl har iteratsiyada YANGI o'zgaruvchi yaratadimi, yoki bitta umumiyni o'zgartiradimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "MoneyLog — Vanilla JS frontend Flask'ga ulangan",
    "task_description": (
        "templates/index.html va static/app.js yarating. Flask orqali bosh "
        "sahifani ko'rsating, fetch() orqali xarajatlar ro'yxatini oling va "
        "DOM'da chizing. Har bir xarajatga o'chirish tugmasini let bilan "
        "to'g'ri bog'lang."
    ),
    "task_requirements": (
        "• app/templates/index.html — url_for('static', ...) orqali CSS/JS ulangan\n"
        "• app/static/app.js — fetch('/api/expenses') orqali ma'lumot oladi\n"
        "• Ro'yxat DOM'ga to'g'ri chiziladi (innerHTML yoki createElement bilan)\n"
        "• Har bir xarajatga o'chirish tugmasi qo'shilgan, let orqali TO'G'RI id'ga bog'langan\n"
        "• Alohida CORS sozlamasi YO'Q (bir xil origin'dan ishlaydi)\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "HTML, CSS, Vanilla JavaScript, Flask (render_template)",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Autentifikatsiya — werkzeug.security bilan parol, token bilan API</h2>

<pre class="mermaid">
flowchart LR
    REGISTER["POST /api/register"] --> HASH["generate_password_hash() - parol hash qilinadi"]
    HASH --> LOGIN["POST /api/login"]
    LOGIN --> CHECK["check_password_hash() - solishtiriladi"]
    CHECK --> TOKEN["Token yaratiladi va qaytariladi"]
    TOKEN --> JS["Vanilla JS token'ni saqlaydi va har so'rovga qo'shadi"]
</pre>

<p>Flask O'rta daraja kursida <code>werkzeug.security</code> bilan parol hash qilishni ko'rgansiz. Bu bosqichda buni MoneyLog'ning ro'yxatdan o'tish/kirish tizimida qo'llaymiz, va vanilla JS frontend uchun (2-capstone kursidagidek) hand-rolled token autentifikatsiya quramiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ro'yxatdan o'tish: parolni TO'G'RI hash qilish</h4>
<pre><code># app/routes.py
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

@api.route('/register', methods=['POST'])
def register():
    ma_lumot = request.get_json()
    parol_hash = generate_password_hash(ma_lumot["parol"])   # ❗ parol HECH QACHON ochiq saqlanmaydi!

    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"], parol_hash=parol_hash,
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201</code></pre>

<h4>BLOKA 2 — kirish: parolni tekshirish va token yaratish</h4>
<pre><code>@api.route('/login', methods=['POST'])
def login():
    ma_lumot = request.get_json()
    user = User.query.filter_by(email=ma_lumot["email"]).first()

    if user is None or not check_password_hash(user.parol_hash, ma_lumot["parol"]):
        return jsonify({"xato": "Email yoki parol noto'g'ri"}), 401

    user.token = secrets.token_hex(20)   # ❗ User modelida 'token' ustuni bor deb faraz qilamiz
    db.session.commit()
    return jsonify({"token": user.token, "ism": user.ism})</code></pre>

<h4>BLOKA 3 — himoyalangan endpoint uchun dekorator</h4>
<pre><code># app/auth_utils.py
from functools import wraps
from flask import request, jsonify
from app.models import User

def token_talab_qilish(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return jsonify({"xato": "Token yo'q"}), 401

        token = auth_header.split(' ')[1]
        user = User.query.filter_by(token=token).first()
        if user is None:
            return jsonify({"xato": "Token yaroqsiz"}), 401

        request.joriy_user = user   # ❗ keyingi route uchun foydalanuvchini beradi
        return f(*args, **kwargs)
    return wrapper

# app/routes.py
@api.route('/expenses', methods=['GET'])
@token_talab_qilish
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=request.joriy_user.id).all()
    return jsonify([x.to_dict() for x in xarajatlar])</code></pre>

<h3>🐛 Ataylab xato — parolni hash qilishni unutish</h3>
<pre><code>@api.route('/register', methods=['POST'])
def register_xato():
    ma_lumot = request.get_json()
    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"],
        parol_hash=ma_lumot["parol"],   # ❌ generate_password_hash() ISHLATILMAGAN - ochiq parol!
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201

# Ma'lumotlar bazasida:
# parol_hash ustuni "mening_parolim123" kabi OCHIQ MATN sifatida saqlanadi!
# ❌ Agar baza oshkor bo'lib qolsa, BARCHA foydalanuvchilarning haqiqiy
#    parollari darhol ko'rinadi</code></pre>

<p><strong>Natija:</strong> agar parol <strong>hash qilinmasdan</strong> to'g'ridan-to'g'ri saqlansa, ma'lumotlar bazasi (yoki uning zaxira nusxasi) <strong>istalgan sababga ko'ra</strong> oshkor bo'lib qolsa — xakerlik, noto'g'ri sozlangan ruxsatlar, yoki hatto ichki xodim orqali — <strong>barcha</strong> foydalanuvchilarning haqiqiy parollari <strong>darhol</strong> oshkor bo'ladi. Bundan tashqari, ko'p foydalanuvchi <strong>bir xil</strong> parolni boshqa saytlarda ham ishlatadi — bu boshqa xizmatlarga ham xavf tug'diradi. <code>generate_password_hash()</code> parolni <strong>qaytarib bo'lmaydigan</strong> shaklga o'tkazadi, shuning uchun hatto baza oshkor bo'lsa ham, haqiqiy parolni tiklab bo'lmaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. <code>generate_password_hash()</code> va <code>check_password_hash()</code> qanday ishlaydi?</h4>
<p><code>generate_password_hash(parol)</code> parolni <strong>bir tomonlama</strong> (qaytarib bo'lmaydigan) hash'ga aylantiradi. Kirishda, <code>check_password_hash(saqlangan_hash, kiritilgan_parol)</code> kiritilgan parolni <strong>xuddi shu algoritm</strong> bilan qayta hash qilib, saqlangan hash bilan solishtiradi — asl parolni "tiklamasdan" solishtirish mumkin.</p>

<h4>2. Nega token <code>User</code> modelining o'zida saqlanadi (alohida Token jadvali emas)?</h4>
<p>Bu — soddalashtirilgan yondashuv: har bir foydalanuvchida <strong>bitta</strong> faol token bo'ladi deb faraz qilinadi (yangi login qilinganda eskisi almashtiriladi). Django capstone kursida alohida <code>Token</code> jadvali ishlatilgan edi — bu ham to'g'ri, bu yerda esa soddaroq variant ko'rsatilmoqda.</p>

<h4>3. Dekorator (<code>token_talab_qilish</code>) qanday ishlaydi?</h4>
<p>Bu — Django capstone kursidagi <code>@token_talab_qilish</code>ning Flask versiyasi: <code>Authorization</code> header'ni tekshiradi, token bo'yicha foydalanuvchini topadi, va <code>request.joriy_user</code>ga biriktirib, asl route funksiyasiga o'tkazadi.</p>

<h4>4. Nega parolni hash qilmaslik <strong>ayniqsa</strong> xavfli?</h4>
<p>Parol — foydalanuvchining <strong>o'zi</strong> tanlagan, ko'pincha boshqa xizmatlarda ham ishlatiladigan maxfiy ma'lumot. Email yoki ism kabi ma'lumotlardan farqli, parolning oshkor bo'lishi foydalanuvchining <strong>boshqa</strong> hisoblariga ham (agar u bir xil parolni qayta ishlatgan bo'lsa) xavf tug'diradi.</p>

<h4>5. Nega bu xato darhol sezilmaydi?</h4>
<p>Ro'yxatdan o'tish va kirish <strong>funksional</strong> jihatdan to'g'ri ishlayveradi — foydalanuvchi ro'yxatdan o'tadi, keyin kira oladi, hammasi "ishlab turgandek" ko'rinadi. Muammo faqat ma'lumotlar bazasi oshkor bo'lib qolganda (yoki xavfsizlik auditida) <strong>keyinroq</strong> ma'lum bo'ladi — bu uni ayniqsa xavfli qiladi, chunki hech kim uni darhol payqamaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>generate_password_hash()</code>/<code>check_password_hash()</code> — parolni xavfsiz saqlash va tekshirish</li>
<li>✅ Parol <strong>hech qachon</strong> ochiq matn sifatida saqlanmasligi kerak</li>
<li>✅ Hand-rolled token autentifikatsiya — vanilla JS frontend uchun mos yechim</li>
<li>✅ Dekorator himoyalangan route'larni tartibli, qayta ishlatiladigan tarzda yozish imkonini beradi</li>
<li>✅ Parolni hash qilmaslik xatosi darhol emas, faqat baza oshkor bo'lganda ma'lum bo'ladi — bu uni jiddiy xavfli qiladi</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 4-BOSQICH: Autentifikatsiya - werkzeug.security va token
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/routes.py - ro'yxatdan o'tish (parolni hash qilib)
# ─────────────────────────────────────────────────────────────────────

from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask import request, jsonify
from app import db
from app.models import User


@api.route('/register', methods=['POST'])
def register():
    ma_lumot = request.get_json()
    parol_hash = generate_password_hash(ma_lumot["parol"])

    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"], parol_hash=parol_hash,
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201

# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - kirish (parolni tekshirib, token yaratish)
# ─────────────────────────────────────────────────────────────────────


@api.route('/login', methods=['POST'])
def login():
    ma_lumot = request.get_json()
    user = User.query.filter_by(email=ma_lumot["email"]).first()

    if user is None or not check_password_hash(user.parol_hash, ma_lumot["parol"]):
        return jsonify({"xato": "Email yoki parol noto'g'ri"}), 401

    user.token = secrets.token_hex(20)
    db.session.commit()
    return jsonify({"token": user.token, "ism": user.ism})

# ─────────────────────────────────────────────────────────────────────
# 3) app/auth_utils.py - himoyalangan endpoint dekoratori
# ─────────────────────────────────────────────────────────────────────

from functools import wraps


def token_talab_qilish(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return jsonify({"xato": "Token yo'q"}), 401

        token = auth_header.split(' ')[1]
        user = User.query.filter_by(token=token).first()
        if user is None:
            return jsonify({"xato": "Token yaroqsiz"}), 401

        request.joriy_user = user
        return f(*args, **kwargs)
    return wrapper

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - parolni hash qilishni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# @api.route('/register', methods=['POST'])
# def register_xato():
#     ma_lumot = request.get_json()
#     yangi_user = User(
#         ism=ma_lumot["ism"], email=ma_lumot["email"],
#         parol_hash=ma_lumot["parol"],   # generate_password_hash() ISHLATILMAGAN!
#     )
#     db.session.add(yangi_user)
#     db.session.commit()
# ❌ Baza oshkor bo'lsa, barcha parollar OCHIQ MATN sifatida ko'rinadi!
"""

L4_EX = [
    {
        "title": "generate_password_hash() va check_password_hash() qanday ishlaydi?",
        "description": "Login jarayonida check_password_hash() nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Saqlangan hash'ni asl parolga \"qaytaradi\"",
            "Kiritilgan parolni xuddi shu algoritm bilan hash qilib, saqlangan hash bilan solishtiradi",
            "Parolni internetga yuboradi",
            "Faqat parol uzunligini tekshiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Hash'ni \"orqaga qaytarib bo'lmaydi\" - buning o'rniga qanday solishtiriladi?",
        "explanation": "check_password_hash() kiritilgan parolni qayta hash qilib, saqlangan hash bilan solishtiradi — bu orqali asl parolni \"tiklamasdan\" to'g'riligini tekshirish mumkin.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega parolni hash qilmaslik ayniqsa xavfli?",
        "description": "Nega parolni hash qilmasdan saqlash boshqa (masalan ism yoki email) ma'lumotlarni oshkor qilishdan ham xavfliroq hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki parol boshqa ma'lumotlardan uzunroq",
            "Ko'p foydalanuvchi bir xil parolni boshqa saytlarda ham ishlatadi, shuning uchun oshkor bo'lishi boshqa hisoblarga ham xavf tug'diradi",
            "Chunki parol maydoni ma'lumotlar bazasida eng katta joy egallaydi",
            "Bu xavfli emas, oddiy ma'lumot kabi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Odamlar ko'pincha bir xil parolni qayta ishlatishadi.",
        "explanation": "Parol foydalanuvchining boshqa xizmatlarda ham ishlatadigan maxfiy ma'lumoti bo'lgani uchun, uning oshkor bo'lishi faqat shu tizimga emas, foydalanuvchining boshqa hisoblariga ham xavf tug'diradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Ro'yxatdan o'tish va kirish jarayonini tartiblang",
        "description": "Foydalanuvchi ro'yxatdan o'tib, keyin kirganda bo'ladigan to'liq jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "POST /api/register - parol generate_password_hash() bilan hash qilinib saqlanadi",
            "POST /api/login - email bo'yicha user topiladi",
            "check_password_hash() kiritilgan parolni saqlangan hash bilan solishtiradi",
            "To'g'ri bo'lsa, yangi token yaratilib, foydalanuvchiga qaytariladi",
        ],
        "correct_order": [
            "POST /api/register - parol generate_password_hash() bilan hash qilinib saqlanadi",
            "POST /api/login - email bo'yicha user topiladi",
            "check_password_hash() kiritilgan parolni saqlangan hash bilan solishtiradi",
            "To'g'ri bo'lsa, yangi token yaratilib, foydalanuvchiga qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Parolni hash qilish uchun ishlatiladigan funksiya",
        "description": "werkzeug.security modulida parolni hash qilish uchun ishlatiladigan funksiya nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "generate_password_hash",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega parolni hash qilmaslik darhol sezilmaydi?",
        "description": (
            "register_xato() funksiyasida parol hash qilinmasdan "
            "to'g'ridan-to'g'ri saqlansa, ro'yxatdan o'tish va kirish "
            "baribir \"to'g'ri ishlayveradi\". Nega bu xato darhol "
            "sezilmaydi, va u aslida qachon jiddiy oqibatga olib "
            "keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Parol hash qilinmasdan saqlansa ham, ro'yxatdan o'tish va "
            "kirish funksional jihatdan to'g'ri ishlayveradi, chunki "
            "kod shunchaki kiritilgan parolni saqlangan (ochiq) parol "
            "bilan to'g'ridan-to'g'ri solishtiradi — bu tashqi "
            "ko'rinishda xatosiz. Muammo faqat ma'lumotlar bazasining "
            "o'zi (yoki uning zaxira nusxasi) qandaydir sababga ko'ra "
            "(xakerlik, noto'g'ri sozlangan ruxsatlar) oshkor bo'lib "
            "qolganda paydo bo'ladi — o'sha daqiqada barcha "
            "foydalanuvchilarning haqiqiy, ochiq parollari darhol "
            "ko'rinadi. Bu xavf odatiy ishlatishda hech qachon "
            "sezilmaydi, faqat xavfsizlik buzilishi yuz berganda "
            "amalga oshadi — shuning uchun uni oldindan, ehtiyot chorasi "
            "sifatida bartaraf etish juda muhim."
        ),
        "hint": "Kod \"ishlab turgan\" paytda bu xato ko'rinadimi, yoki faqat qandaydir boshqa hodisa sodir bo'lganda?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "MoneyLog — autentifikatsiya (parol hash + token)",
    "task_description": (
        "POST /api/register va POST /api/login endpoint'larini yarating. "
        "Parolni werkzeug.security orqali hash qiling va tekshiring. "
        "token_talab_qilish dekoratorini yozib, uni expenses endpoint'lariga "
        "qo'llang. Frontend'da login/register formalarini amalga oshiring."
    ),
    "task_requirements": (
        "• POST /api/register — parolni generate_password_hash() bilan saqlaydi (ochiq matn EMAS)\n"
        "• POST /api/login — check_password_hash() orqali tekshiradi, token qaytaradi\n"
        "• token_talab_qilish dekoratori — Authorization header'ni tekshiradi\n"
        "• GET/POST /api/expenses — faqat request.joriy_user'ga tegishli ma'lumotni qaytaradi/yaratadi\n"
        "• Frontend: login/register formalari, token localStorage'da saqlanadi va har so'rovga qo'shiladi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Flask, werkzeug.security, secrets moduli, Vanilla JS",
    "task_deadline_days": 4,
}


L5_TEXT = """\
<h2>5-bosqich: Telegram bot — tezkor xarajat va hisob bog'lash</h2>

<pre class="mermaid">
flowchart LR
    BOTFILE["telegram_bot/bot.py"] -->|app.app_context()| CTX["Flask-SQLAlchemy'ga ulanish tayyor"]
    CTX --> MODELS["from app.models import ..."]
    MSG["Foydalanuvchi botga yozadi: '50000 ovqat'"] --> PARSE["Matn tahlil qilinadi"]
    PARSE --> SAVE["Expense yaratiladi - SHU foydalanuvchi uchun"]
</pre>

<p>MoneyLog'ning eng qulay xususiyati shu yerda: foydalanuvchi web saytga kirmasdan, Telegram'da shunchaki <strong>"50000 ovqat"</strong> deb yozib, xarajatni <strong>tezkor</strong> qo'sha oladi. Bot Flask-SQLAlchemy'ning <strong>xuddi shu</strong> bazasiga ulanadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — botga Flask ilova kontekstini ulash</h4>
<pre><code># telegram_bot/bot.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'flask_backend'))

from app import create_app, db                # ❗ Flask'ning Application Factory'si (2-bosqichdan)
from app.models import User, Category, Expense

app = create_app()                              # ❗ Flask ilova obyektini yaratadi (server ishga tushirilmaydi!)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()</code></pre>

<h4>BLOKA 2 — /link buyrug'i: app_context() ICHIDA so'rov yuborish</h4>
<pre><code>@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    with app.app_context():                      # ❗ MAJBURIY - Flask-SQLAlchemy so'rovlari shu blok ICHIDA
        user = User.query.filter_by(link_kodi=kod).first()
        if user is None:
            await message.answer("Kod noto'g'ri yoki eskirgan")
            return

        user.telegram_chat_id = message.chat.id
        user.link_kodi = None
        db.session.commit()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.ism}!")</code></pre>

<h4>BLOKA 3 — matn orqali tezkor xarajat qo'shish</h4>
<pre><code>@dp.message()                                    # ❗ /buyruq bilan boshlanmagan HAR QANDAY matn uchun
async def tezkor_xarajat_handler(message: types.Message):
    qismlar = message.text.split(maxsplit=1)      # ❗ "50000 ovqat" -> ["50000", "ovqat"]
    if len(qismlar) != 2 or not qismlar[0].isdigit():
        await message.answer("Format: SUMMA TAVSIF (masalan: 50000 ovqat)")
        return

    summa, tavsif = qismlar

    with app.app_context():
        user = User.query.filter_by(telegram_chat_id=message.chat.id).first()
        if user is None:
            await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
            return

        category = Category.query.filter_by(user_id=user.id, nomi=tavsif).first()
        if category is None:
            category = Category(nomi=tavsif, user_id=user.id)
            db.session.add(category)
            db.session.flush()

        xarajat = Expense(
            summa=summa, tavsif=tavsif, sana=date.today(),
            category_id=category.id, user_id=user.id,
        )
        db.session.add(xarajat)
        db.session.commit()

    await message.answer(f"✅ {summa} so'm '{tavsif}' uchun yozildi")</code></pre>

<h3>🐛 Ataylab xato — app_context()siz Flask-SQLAlchemy so'rov yuborish</h3>
<pre><code>@dp.message(Command("link"))
async def link_handler_xato(message: types.Message):
    kod = message.text.split()[1]
    user = User.query.filter_by(link_kodi=kod).first()   # ❌ app.app_context() YO'Q!
    # ...

# Bot ishga tushganda va foydalanuvchi /link yuborganda:
# ❌ RuntimeError: Working outside of application context.
#    This typically means that you attempted to use functionality that
#    needed the current application.</code></pre>

<p><strong>Natija:</strong> Flask-SQLAlchemy'ning <code>User.query</code> kabi so'rovlari ishlashi uchun, Flask "qaysi ilova kontekstida ekanligini" <strong>bilishi</strong> kerak — bu odatda har bir HTTP so'rovda <strong>avtomatik</strong> ta'minlanadi (Flask buni o'zi boshqaradi). Bot esa HTTP so'rov doirasida ishlamaydi — u Django capstone kursidagi <code>django.setup()</code>ga o'xshab, <strong>qo'lda</strong> ilova kontekstini <code>with app.app_context():</code> orqali "ochishi" kerak. Bu qilinmasa, Flask-SQLAlchemy qayerga (qaysi bazaga, qaysi konfiguratsiyaga) murojaat qilishni "bilmay", <code>RuntimeError</code> beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega botga Flask ilova konteksti kerak?</h4>
<p>Flask-SQLAlchemy ma'lumotlar bazasi ulanishi, konfiguratsiya kabi ma'lumotlarni Flask ilova obyekti (<code>app</code>) ichida saqlaydi. Odatda bu ma'lumotlarga faqat HTTP so'rov ichida (Flask avtomatik "kontekst" o'rnatganda) murojaat qilinadi. Bot esa HTTP so'rov emas, shuning uchun bu kontekstni <strong>qo'lda</strong> yaratishi kerak.</p>

<h4>2. <code>app.app_context()</code> Django'dagi <code>django.setup()</code>ga qanday o'xshaydi?</h4>
<p>Ikkalasi ham <strong>bir xil muammoni</strong> hal qiladi: ORM'ni (Django ORM yoki Flask-SQLAlchemy) veb-serverdan <strong>tashqarida</strong> ishlatish. Farqi: <code>django.setup()</code> bir marta, dastur boshida chaqiriladi; <code>app.app_context()</code> esa <code>with</code> bloki sifatida, <strong>har bir</strong> ma'lumotlar bazasiga murojaat kerak bo'lgan joyda alohida ochiladi.</p>

<h4>3. <code>@dp.message()</code> (filtrsiz) nima uchun ishlatiladi?</h4>
<p>aiogram'da filtrsiz <code>@dp.message()</code> — <strong>hech qanday buyruqqa mos kelmagan</strong> (masalan <code>/link</code>, <code>/start</code> emas) barcha matnli xabarlarni ushlaydi. Bu foydalanuvchi shunchaki "50000 ovqat" deb yozganida ishga tushadigan handler'ni yozish imkonini beradi.</p>

<h4>4. Nega yangi category avtomatik yaratiladi (agar mavjud bo'lmasa)?</h4>
<p>Foydalanuvchi botga tezkor yozganda, u oldindan category yaratib qo'ymagan bo'lishi mumkin. Kod "agar shu nomdagi category mavjud bo'lmasa, uni avtomatik yarat" mantig'ini qo'llaydi — bu foydalanuvchi tajribasini soddalashtiradi, lekin web saytdagi rasmiy category yaratish jarayonidan farqli.</p>

<h4>5. Nega <code>app_context()</code>siz <code>RuntimeError</code> chiqadi?</h4>
<p><code>User.query</code> kabi Flask-SQLAlchemy so'rovlari orqa fonda joriy Flask ilova kontekstidan konfiguratsiya (masalan <code>DATABASE_URL</code>) va ulanishni "so'raydi". Agar hech qanday kontekst <strong>ochilmagan</strong> bo'lsa (bot HTTP so'rov ichida emas), Flask-SQLAlchemy bu ma'lumotni <strong>qayerdan olishni bilmay</strong>, "siz ilova kontekstidan tashqarida ishlatyapsiz" degan <code>RuntimeError</code>ni ko'taradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>app.app_context()</code> — Flask-SQLAlchemy'ni veb-serverdan tashqarida (masalan botda) ishlatish uchun MAJBURIY</li>
<li>✅ Bu Django'dagi <code>django.setup()</code>ga o'xshaydi, lekin har bir DB murojaati atrofida <code>with</code> bloki sifatida ishlatiladi</li>
<li>✅ <code>@dp.message()</code> (filtrsiz) — buyruq bo'lmagan erkin matnni ushlaydi</li>
<li>✅ Bot va Flask backend BIR XIL ma'lumotlar bazasiga ulangani uchun, botda yaratilgan yozuv web saytda ham darhol ko'rinadi</li>
<li>✅ <code>app_context()</code>siz Flask-SQLAlchemy so'rovi <code>RuntimeError: Working outside of application context</code> beradi</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 5-BOSQICH: Telegram bot - tezkor xarajat va hisob bog'lash
# ════════════════════════════════════════════════════════════════════

import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'flask_backend'))

from app import create_app, db
from app.models import User, Category, Expense

app = create_app()

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()


@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    with app.app_context():
        user = User.query.filter_by(link_kodi=kod).first()
        if user is None:
            await message.answer("Kod noto'g'ri yoki eskirgan")
            return

        user.telegram_chat_id = message.chat.id
        user.link_kodi = None
        db.session.commit()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.ism}!")


@dp.message()
async def tezkor_xarajat_handler(message: types.Message):
    qismlar = message.text.split(maxsplit=1)
    if len(qismlar) != 2 or not qismlar[0].isdigit():
        await message.answer("Format: SUMMA TAVSIF (masalan: 50000 ovqat)")
        return

    summa, tavsif = qismlar

    with app.app_context():
        user = User.query.filter_by(telegram_chat_id=message.chat.id).first()
        if user is None:
            await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
            return

        category = Category.query.filter_by(user_id=user.id, nomi=tavsif).first()
        if category is None:
            category = Category(nomi=tavsif, user_id=user.id)
            db.session.add(category)
            db.session.flush()

        xarajat = Expense(
            summa=summa, tavsif=tavsif, sana=date.today(),
            category_id=category.id, user_id=user.id,
        )
        db.session.add(xarajat)
        db.session.commit()

    await message.answer(f"✅ {summa} so'm '{tavsif}' uchun yozildi")

# ─────────────────────────────────────────────────────────────────────
# Ataylab xato - app_context()siz so'rov yuborish (izohda)
# ─────────────────────────────────────────────────────────────────────

# @dp.message(Command("link"))
# async def link_handler_xato(message: types.Message):
#     kod = message.text.split()[1]
#     user = User.query.filter_by(link_kodi=kod).first()   # app_context() YO'Q!
# ❌ RuntimeError: Working outside of application context.
"""

L5_EX = [
    {
        "title": "Nega botga app.app_context() kerak?",
        "description": "Telegram bot skriptida Flask-SQLAlchemy so'rovini ishlatishdan oldin app.app_context() nega kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Botni tezroq ishga tushirish uchun",
            "Flask-SQLAlchemy'ni HTTP so'rovdan tashqarida (masalan botda) ishlatish uchun",
            "Faqat xato xabarlarini o'chirish uchun",
            "Bu ixtiyoriy, hech qanday amaliy ta'siri yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bot Django capstone kursidagi django.setup()ga o'xshash muammoga duch keladi.",
        "explanation": "Flask-SQLAlchemy odatda faqat HTTP so'rov ichida (Flask avtomatik kontekst o'rnatganda) ishlatiladi. Bot HTTP so'rov emas, shuning uchun app.app_context() orqali bu kontekstni qo'lda yaratish kerak.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "app.app_context() va django.setup() o'xshashligi",
        "description": "app.app_context() Django capstone kursidagi django.setup()ga qanday o'xshaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ular butunlay bir xil, farqi yo'q",
            "Ikkalasi ham ORM'ni veb-serverdan tashqarida ishlatish muammosini hal qiladi, lekin ishlatilish usuli farqli",
            "django.setup() faqat test uchun, app_context() esa production uchun",
            "Ular hech qanday umumiylikka ega emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ikkalasi ham xuddi shunday muammoni - ORM'ni serverdan tashqarida ishlatishni - hal qiladi.",
        "explanation": "Ikkalasi ham ORM'ni veb-serverdan tashqarida ishlatish muammosini hal qiladi, lekin django.setup() bir marta chaqiriladi, app.app_context() esa har bir DB murojaati uchun with bloki sifatida alohida ochiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Tezkor xarajat qo'shish jarayonini tartiblang",
        "description": "Foydalanuvchi botga '50000 ovqat' deb yozganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Matn split(maxsplit=1) orqali ['50000', 'ovqat']ga ajratiladi",
            "app.app_context() ichida telegram_chat_id bo'yicha User qidiriladi",
            "Agar 'ovqat' nomli category mavjud bo'lmasa, u avtomatik yaratiladi",
            "Yangi Expense yaratilib saqlanadi, foydalanuvchiga tasdiqlash xabari yuboriladi",
        ],
        "correct_order": [
            "Matn split(maxsplit=1) orqali ['50000', 'ovqat']ga ajratiladi",
            "app.app_context() ichida telegram_chat_id bo'yicha User qidiriladi",
            "Agar 'ovqat' nomli category mavjud bo'lmasa, u avtomatik yaratiladi",
            "Yangi Expense yaratilib saqlanadi, foydalanuvchiga tasdiqlash xabari yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Buyruqsiz erkin matnni ushlovchi aiogram dekoratori",
        "description": "aiogram'da /buyruq bilan boshlanmagan HAR QANDAY matnli xabarni ushlash uchun ishlatiladigan dekoratorni yozing (filtrsiz).",
        "exercise_type": "text_input",
        "expected_answer": "@dp.message()",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega app_context()siz RuntimeError chiqadi?",
        "description": (
            "Agar link_handler_xato() funksiyasida User.query "
            "app.app_context() ICHIDA emas, to'g'ridan-to'g'ri "
            "chaqirilsa, nega \"RuntimeError: Working outside of "
            "application context\" xatosi chiqadi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "User.query kabi Flask-SQLAlchemy so'rovlari ishlashi uchun, "
            "ular orqa fonda joriy Flask ilova kontekstidan qaysi "
            "ma'lumotlar bazasiga ulanish kerakligi (DATABASE_URL) va "
            "boshqa konfiguratsiya ma'lumotlarini \"so'raydi\". Odatda bu "
            "kontekst faqat Flask HTTP so'rovni qayta ishlayotganda "
            "avtomatik mavjud bo'ladi. Bot esa HTTP so'rov doirasida "
            "ishlamaydi, shuning uchun hech qanday Flask konteksti "
            "avtomatik ochilmaydi. Agar dasturchi with app.app_context() "
            "orqali bu kontekstni qo'lda ochmasa, Flask-SQLAlchemy qaysi "
            "konfiguratsiyaga murojaat qilishni bilmay, \"siz ilova "
            "kontekstidan tashqarida ishlatyapsiz\" degan RuntimeError "
            "xatosini beradi."
        ),
        "hint": "Flask-SQLAlchemy so'rovlari konfiguratsiya ma'lumotini qayerdan (qanday \"kontekst\"dan) oladi, va bot bu kontekstga avtomatik egami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "MoneyLog — Telegram bot: tezkor xarajat va bog'lash",
    "task_description": (
        "telegram_bot/bot.py yarating, unda create_app() orqali Flask ilova "
        "obyektini yarating (server ishga tushirmasdan). /link KOD buyrug'i "
        "orqali hisob bog'lashni, erkin matn ('summa tavsif' formatida) orqali "
        "esa tezkor xarajat qo'shishni amalga oshiring."
    ),
    "task_requirements": (
        "• telegram_bot/bot.py — create_app() chaqirilgan, barcha DB so'rovlari "
        "app.app_context() ICHIDA\n"
        "• /link KOD — link_kodi bo'yicha foydalanuvchini topib, "
        "telegram_chat_id'ni yozadi, link_kodi'ni None qiladi\n"
        "• @dp.message() (filtrsiz) — 'SUMMA TAVSIF' formatidagi matnni tahlil qiladi\n"
        "• Mos category mavjud bo'lmasa, avtomatik yaratiladi\n"
        "• Yangi Expense to'g'ri user_id va category_id bilan saqlanadi\n"
        "• Bog'lanmagan foydalanuvchi uchun tushunarli xabar chiqadi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "aiogram, Flask-SQLAlchemy, app.app_context()",
    "task_deadline_days": 5,
}


L6_TEXT = """\
<h2>6-bosqich: Oylik hisobot va byudjet ogohlantirishi</h2>

<pre class="mermaid">
flowchart LR
    CRON["cron: har kuni ishga tushadi"] --> CLI["flask send-budget-alerts"]
    CLI --> LOOP["Har bir foydalanuvchi uchun sikl"]
    LOOP --> SUM{"func.sum() - FAQAT shu user_id uchunmi?"}
    SUM -->|filter yo'q| BUG["Hamma foydalanuvchining umumiy summasi qaytadi"]
    SUM -->|filter bor| OK["Faqat shu foydalanuvchining summasi"]
</pre>

<p>MoneyLog'ning yakuniy "aqlli" xususiyati: har oy, har bir foydalanuvchi <strong>o'z</strong> xarajatlari yig'indisini <strong>o'z</strong> byudjeti bilan solishtirib, agar oshib ketgan bo'lsa, Telegram orqali ogohlantirilishi kerak.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Flask CLI komandasi yaratish</h4>
<pre><code># app/commands.py
import click
from flask import current_app
from sqlalchemy import func
from datetime import date
import requests
from app import db
from app.models import User, Expense

@current_app.cli.command('send-budget-alerts')     # ❗ Flask'ning o'z CLI naqshi - 'flask send-budget-alerts'
def send_budget_alerts():
    bugun = date.today()
    oy_boshi = bugun.replace(day=1)

    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    for user in foydalanuvchilar:
        jami = db.session.query(func.sum(Expense.summa)).filter(
            Expense.user_id == user.id,               # ❗ MUHIM - FAQAT shu foydalanuvchi!
            Expense.sana >= oy_boshi,
        ).scalar() or 0

        if user.oylik_byudjet and jami > user.oylik_byudjet:
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)</code></pre>

<h4>BLOKA 2 — Telegram xabarini yuborish</h4>
<pre><code>def xabar_yuborish(chat_id, jami, byudjet):
    matn = (
        f"⚠️ Diqqat! Bu oy siz {jami} so'm sarfladingiz, "
        f"byudjetingiz esa {byudjet} so'm edi."
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": matn},
    )</code></pre>

<h4>BLOKA 3 — cron orqali rejalashtirish</h4>
<pre><code># crontab -e
# Har kuni soat 20:00da ishga tushirish:
0 20 * * * cd /path/to/flask_backend && flask send-budget-alerts</code></pre>

<h3>🐛 Ataylab xato — agregat so'rovda foydalanuvchi bo'yicha filtrlashni unutish</h3>
<pre><code>def send_budget_alerts_xato():
    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    # ❌ Bitta umumiy yig'indi - HAMMA foydalanuvchilar uchun BIR MARTA hisoblanadi!
    jami = db.session.query(func.sum(Expense.summa)).scalar() or 0

    for user in foydalanuvchilar:
        if user.oylik_byudjet and jami > user.oylik_byudjet:   # ❌ 'jami' HAMMA uchun bir xil!
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)

# Natija: agar 100 ta foydalanuvchi bo'lsa va ularning umumiy xarajati katta bo'lsa,
# HAR BIR foydalanuvchi (hatto atigi 5000 so'm sarflagan bo'lsa ham) "byudjetdan
# oshib ketdingiz" degan XATO ogohlantirish oladi!</code></pre>

<p><strong>Natija:</strong> <code>func.sum(Expense.summa)</code> <strong>hech qanday</strong> <code>.filter(Expense.user_id == ...)</code>siz chaqirilsa, u ma'lumotlar bazasidagi <strong>barcha</strong> foydalanuvchilarning <strong>barcha</strong> xarajatlarini bitta yig'indiga qo'shib beradi. Bu bitta "global" son keyin <strong>har bir</strong> foydalanuvchi uchun (sikl ichida) qayta-qayta solishtirilsa, natija <strong>mutlaqo noto'g'ri</strong> bo'ladi — kam xarajat qilgan foydalanuvchilar ham boshqalarning xarajati tufayli soxta ogohlantirish olishi mumkin. To'g'ri yechim: har doim <code>.filter(Expense.user_id == user.id)</code>ni <strong>sikl ichida, har bir foydalanuvchi uchun alohida</strong> qo'shish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Flask CLI komandasi (<code>@app.cli.command()</code>) nima?</h4>
<p>Bu — Flask'ning Django management command'lariga <strong>o'xshash</strong> mexanizmi: <code>flask &lt;buyruq-nomi&gt;</code> orqali terminal'dan ishga tushiriladigan, HTTP so'rovga bog'liq bo'lmagan vazifalar yozish usuli. Ikkalasi ham xuddi shu maqsadga xizmat qiladi — vaqt bo'yicha (cron orqali) ishga tushadigan vazifalarni tuzilgan tarzda yozish.</p>

<h4>2. Nega <code>func.sum()</code> ma'lumotlar bazasi darajasida hisoblanadi?</h4>
<p><code>db.session.query(func.sum(...))</code> yig'indini <strong>Python kodida emas</strong>, balki <strong>SQL so'rovi ichida</strong> (masalan <code>SELECT SUM(summa) FROM expenses WHERE ...</code>) hisoblaydi. Bu ming-minglab yozuv bo'lganda ham juda tez ishlaydi, chunki barcha ma'lumotni Python'ga yuklab olish shart emas.</p>

<h4>3. Nega <code>.filter(Expense.user_id == user.id)</code> MAJBURIY?</h4>
<p>Agregat funksiyalar (<code>SUM</code>, <code>COUNT</code>, <code>AVG</code>) <strong>standart holda</strong> so'rovga mos <strong>barcha</strong> qatorlarni hisoblaydi. Agar <code>WHERE user_id = ...</code> sharti bo'lmasa, SQL "barcha foydalanuvchilarning barcha xarajatlari" ma'nosini beradi — bu esa har bir alohida foydalanuvchining shaxsiy yig'indisi emas.</p>

<h4>4. Nega bu xato sikl ichida <strong>ayniqsa</strong> xavfli?</h4>
<p>Agregat so'rov sikldan <strong>tashqarida, bir marta</strong> chaqirilgani uchun, natija (noto'g'ri, umumiy son) <strong>har bir</strong> foydalanuvchi uchun qayta ishlatiladi — bu xatoni "ko'paytiradi": bitta noto'g'ri so'rov <strong>barcha</strong> foydalanuvchilarga noto'g'ri ogohlantirish yuborilishiga olib keladi.</p>

<h4>5. <code>func.sum(...) or 0</code> nima uchun kerak?</h4>
<p>Agar foydalanuvchida umuman xarajat bo'lmasa, <code>SUM()</code> SQL'da <code>NULL</code> qaytaradi (<code>0</code> emas). Python'da <code>None > byudjet</code> solishtirishga urinish xato beradi. <code>or 0</code> — <code>None</code> holatini <code>0</code>ga almashtirib, xavfsiz solishtirish imkonini beradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>@app.cli.command()</code> — Flask'ning Django management command'iga o'xshash CLI mexanizmi</li>
<li>✅ <code>func.sum()</code> yig'indini SQL darajasida, tez hisoblaydi</li>
<li>✅ Agregat so'rovlarda foydalanuvchi bo'yicha <code>.filter()</code> MAJBURIY, aks holda barcha foydalanuvchilar aralashib ketadi</li>
<li>✅ Sikl ichidagi noto'g'ri agregat so'rov xatoni barcha foydalanuvchilarga "ko'paytiradi"</li>
<li>✅ <code>SUM()</code> natijasiz holatda <code>NULL</code> qaytaradi — <code>or 0</code> bilan xavfsiz qilinadi</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 6-BOSQICH: Oylik hisobot va byudjet ogohlantirishi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/commands.py - Flask CLI komandasi
# ─────────────────────────────────────────────────────────────────────

import click
from flask import current_app
from sqlalchemy import func
from datetime import date
import requests
from app import db
from app.models import User, Expense

BOT_TOKEN = "..."  # environment o'zgaruvchisidan olinadi


@current_app.cli.command('send-budget-alerts')
def send_budget_alerts():
    bugun = date.today()
    oy_boshi = bugun.replace(day=1)

    foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()

    for user in foydalanuvchilar:
        jami = db.session.query(func.sum(Expense.summa)).filter(
            Expense.user_id == user.id,
            Expense.sana >= oy_boshi,
        ).scalar() or 0

        if user.oylik_byudjet and jami > user.oylik_byudjet:
            xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)


def xabar_yuborish(chat_id, jami, byudjet):
    matn = (
        f"⚠️ Diqqat! Bu oy siz {jami} so'm sarfladingiz, "
        f"byudjetingiz esa {byudjet} so'm edi."
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": matn},
    )

# ─────────────────────────────────────────────────────────────────────
# 2) crontab (izohda - server sozlamasi, Python emas)
# ─────────────────────────────────────────────────────────────────────

# 0 20 * * * cd /path/to/flask_backend && flask send-budget-alerts

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - agregatda user filtrisiz (izohda)
# ─────────────────────────────────────────────────────────────────────

# def send_budget_alerts_xato():
#     foydalanuvchilar = User.query.filter(User.telegram_chat_id.isnot(None)).all()
#     jami = db.session.query(func.sum(Expense.summa)).scalar() or 0   # filter YO'Q!
#     for user in foydalanuvchilar:
#         if user.oylik_byudjet and jami > user.oylik_byudjet:   # 'jami' HAMMA uchun bir xil!
#             xabar_yuborish(user.telegram_chat_id, jami, user.oylik_byudjet)
"""

L6_EX = [
    {
        "title": "Flask CLI komandasi (@app.cli.command()) nima?",
        "description": "@app.cli.command() nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat test yozish uchun",
            "Terminal orqali 'flask <buyruq>' shaklida ishga tushiriladigan, HTTP so'rovga bog'liq bo'lmagan vazifa yaratish uchun",
            "HTML formalarni validatsiya qilish uchun",
            "Faqat production muhitida ishlaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Django management command'iga o'xshash mexanizm.",
        "explanation": "@app.cli.command() Flask'ning Django management command'iga o'xshash mexanizmi bo'lib, terminal orqali 'flask <buyruq-nomi>' shaklida ishga tushiriladigan, HTTP so'rovsiz vazifalarni yaratish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega .filter(Expense.user_id == user.id) majburiy?",
        "description": "func.sum(Expense.summa) chaqirilganda nega .filter(Expense.user_id == user.id) qo'shilishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu so'rovni tezroq qiladi",
            "Bo'lmasa, SUM barcha foydalanuvchilarning barcha xarajatlarini bitta yig'indiga qo'shib beradi",
            "Bu SQLAlchemy'ning majburiy sintaksisi, amaliy ahamiyati yo'q",
            "Faqat production muhitida kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agregat funksiyalar standart holda QANDAY qatorlarni hisoblaydi?",
        "explanation": "Agregat funksiyalar (SUM) standart holda so'rovga mos barcha qatorlarni hisoblaydi. filter(user_id=...) bo'lmasa, natija barcha foydalanuvchilarning umumiy yig'indisi bo'lib qoladi, faqat bitta foydalanuvchining emas.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "send_budget_alerts() ishlash jarayonini tartiblang",
        "description": "flask send-budget-alerts komandasi ishga tushirilganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Telegram akkaunti bog'langan barcha foydalanuvchilar olinadi",
            "Har bir foydalanuvchi uchun, FAQAT shu user_id bo'yicha filtrlangan holda oylik yig'indi hisoblanadi",
            "Yig'indi foydalanuvchining o'z oylik_byudjet qiymati bilan solishtiriladi",
            "Agar oshib ketgan bo'lsa, shu foydalanuvchiga Telegram orqali ogohlantirish yuboriladi",
        ],
        "correct_order": [
            "Telegram akkaunti bog'langan barcha foydalanuvchilar olinadi",
            "Har bir foydalanuvchi uchun, FAQAT shu user_id bo'yicha filtrlangan holda oylik yig'indi hisoblanadi",
            "Yig'indi foydalanuvchining o'z oylik_byudjet qiymati bilan solishtiriladi",
            "Agar oshib ketgan bo'lsa, shu foydalanuvchiga Telegram orqali ogohlantirish yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "SUM() natijasiz holatda nima qaytaradi?",
        "description": "Agar foydalanuvchida umuman xarajat bo'lmasa, SQL'dagi SUM() funksiyasi qanday qiymat qaytaradi? (javobingizni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "NULL",
        "hint": "Bu 0 emas.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega sikldan tashqaridagi umumiy agregat so'rov barcha foydalanuvchilarga xato ogohlantirish beradi?",
        "description": (
            "send_budget_alerts_xato()da jami = db.session.query(func.sum(...))"
            ".scalar() sikldan TASHQARIDA, filtersiz bir marta hisoblanadi. "
            "Nega bu holda hatto kam xarajat qilgan foydalanuvchi ham "
            "\"byudjetdan oshib ketdingiz\" degan xato ogohlantirish "
            "olishi mumkin? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "filter(Expense.user_id == ...) qo'shilmagani uchun, "
            "func.sum(Expense.summa) ma'lumotlar bazasidagi BARCHA "
            "foydalanuvchilarning BARCHA xarajatlarini bitta umumiy "
            "songa qo'shib beradi. Bu bitta \"global\" son 'jami' "
            "o'zgaruvchisida saqlanib, keyin sikl ICHIDA har bir "
            "foydalanuvchining shaxsiy oylik_byudjet qiymati bilan "
            "solishtiriladi. Natijada, agar ba'zi foydalanuvchilar "
            "juda ko'p xarajat qilgan bo'lsa, ularning yig'indisi "
            "umumiy 'jami'ni katta qilib yuboradi, va bu katta, "
            "umumiy son endi kam xarajat qilgan (masalan atigi 5000 "
            "so'mlik) foydalanuvchining shaxsiy byudjeti bilan "
            "solishtirilib, unga ham noto'g'ri, soxta \"byudjetdan "
            "oshib ketdingiz\" ogohlantirishi yuborilishiga olib keladi."
        ),
        "hint": "filter(user_id=...) bo'lmasa, func.sum() aynan KIMNING xarajatlarini qo'shib beradi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "MoneyLog — oylik hisobot va byudjet ogohlantirishi",
    "task_description": (
        "send-budget-alerts nomli Flask CLI komandasini yarating — u har bir "
        "foydalanuvchining shu oydagi xarajatlar yig'indisini FAQAT o'ziga "
        "tegishli holda hisoblab, agar oylik_byudjet'dan oshib ketgan bo'lsa, "
        "Telegram orqali ogohlantirish yuboradi."
    ),
    "task_requirements": (
        "• app/commands.py: send-budget-alerts CLI komandasi @app.cli.command() bilan yaratilgan\n"
        "• Har bir foydalanuvchi uchun func.sum() FAQAT shu user_id bo'yicha filtrlangan\n"
        "• SUM() natijasi None bo'lsa, 0 sifatida ishlatiladi (or 0)\n"
        "• Faqat oylik_byudjet'dan oshib ketgan foydalanuvchilarga xabar yuboriladi\n"
        "• Komanda muvaffaqiyatli ishga tushirilgani (qo'lda yoki cron orqali) ko'rsatilgan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Flask CLI commands, SQLAlchemy func.sum, requests, Telegram Bot API",
    "task_deadline_days": 4,
}


L7_TEXT = """\
<h2>7-bosqich (CAPSTONE yakuni): deploy va nisbiy yo'l xatosi</h2>

<pre class="mermaid">
flowchart TB
    FLASK["Flask (API + frontend, BIR joyda)"] -->|"Web Service"| RENDER["Render/Railway"]
    BOT["bot/bot.py"] -->|"Background Worker!"| RENDER2["Render/Railway worker"]
    FLASK -. "bir xil DATABASE_URL" .-> DB[("PostgreSQL")]
    BOT -. "bir xil DATABASE_URL" .-> DB
</pre>

<p>MoneyLog boshqa ikkita capstone'dan farqli — 1-bosqichda frontend uchun alohida hosting kerak emasligini tanladingiz (Flask uni o'zi serverlaydi). Shu sababli bu yerda faqat <strong>ikkita</strong> deploy birligi bor: Flask (API + frontend, BITTA "Web Service") va bot (alohida "Background Worker"). Lekin aynan shu "bitta Flask hammasini beradi" yechimi production'da yangi, o'ziga xos xato turiga olib kelishi mumkin: <strong>nisbiy yo'l (relative path) xatosi</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — statik fayllarni TO'G'RI, mutlaq yo'l bilan berish</h4>
<pre><code># app.py
import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # ❗ app.py qayerda joylashgan bo'lsa, SHU yerdan hisoblanadi
FRONTEND_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)</code></pre>

<h4>BLOKA 2 — ikkita xizmat turi bilan deploy</h4>
<pre><code># Render/Railway kabi platformalarda:
#
# moneylog-web  -> "Web Service" (Flask: API + frontend, BIR jarayon, $PORT'da tinglaydi)
# moneylog-bot  -> "Background Worker" (bot/bot.py: doim ishlab turadi, polling)
#
# Ikkalasi HAM bir xil DATABASE_URL'ga ulanishi shart (5-darsdan boshlangan tamoyil)</code></pre>

<h4>BLOKA 3 — yakuniy README va tekshiruv ro'yxati</h4>
<pre><code># README.md
# MoneyLog

## Jonli havolalar
- Web + API: https://moneylog.onrender.com
- Telegram bot: @MoneyLogBot

## Holat
- [x] Barcha 7 bosqich yakunlandi ✅

## Sinov ro'yxati (deploy qilingandan keyin)
- [ ] Bosh sahifa (index.html) va style.css/app.js TO'G'RI yuklanadi (404 emas)
- [ ] Ro'yxatdan o'tish/kirish ishlaydi
- [ ] Xarajat qo'shish web saytda ishlaydi
- [ ] Telegram bot orqali matn bilan xarajat qo'shish ishlaydi
- [ ] Oy oxirida byudjet ogohlantirishi keladi</code></pre>

<h3>🐛 Ataylab xato — statik papka uchun oddiy nisbiy yo'l</h3>
<pre><code># app.py
FRONTEND_DIR = "static"          # ❌ joriy ishchi papkaga (cwd) nisbatan hisoblanadi!

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

# Lokalda ishlaydi, chunki siz doim
#   cd moneylog/backend && python app.py
# buyrug'ini AYNAN app.py joylashgan papkadan ishga tushirasiz - shuning
# uchun cwd va app.py joylashgan joy TASODIFAN bir xil.
#
# Production serverda esa gunicorn/systemd ko'pincha BOSHQA "working
# directory"dan ishga tushiriladi (masalan repo tub papkasidan):
#   WorkingDirectory=/srv/moneylog
#   ExecStart=gunicorn backend.app:app
#
# Endi cwd = /srv/moneylog, lekin "static" papka aslida
# /srv/moneylog/backend/static'da joylashgan!</code></pre>

<p><strong>Natija:</strong> <code>send_from_directory("static", ...)</code> ichidagi <code>"static"</code> satri <strong>nisbiy yo'l</strong> &mdash; u <code>app.py</code> qayerda joylashganiga emas, balki jarayon <strong>qaysi papkadan ishga tushirilganiga (working directory)</strong> nisbatan hisoblanadi. Lokal rivojlantirishda siz odatda buyruqni to'g'ridan-to'g'ri loyihaning o'zidan ishga tushirganingiz uchun bu ikkalasi <strong>tasodifan</strong> bir xil bo'lib chiqadi va xato sezilmay qoladi. Production serverda esa deploy jarayoni (gunicorn, systemd, Docker) ko'pincha butunlay <strong>boshqa</strong> papkadan ishga tushiriladi &mdash; natijada <code>"static"</code> noto'g'ri joyga ishora qiladi va barcha CSS/JS fayllar uchun <code>404 Not Found</code> qaytadi, garchi <code>/api/...</code> kabi JSON endpoint'lar odatdagidek ishlab tursa ham (chunki ular fayl tizimiga bog'liq emas). To'g'ri yechim &mdash; yo'lni doim <code>os.path.dirname(os.path.abspath(__file__))</code> asosida, <strong>mutlaq</strong> holda hisoblash.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega MoneyLog'da faqat IKKITA deploy birligi bor (React capstone'larida uchta edi)?</h4>
<p>1-bosqichda tanlangan arxitektura tufayli: vanilla JS build qadamini talab qilmagani uchun, Flask uni <strong>o'zi</strong> statik fayl sifatida bera oladi. Shu sababli API va frontend <strong>bitta</strong> jarayonda ("Web Service") birlashadi &mdash; faqat bot alohida ("Background Worker") qoladi.</p>

<h4>2. Nisbiy (relative) va mutlaq (absolute) yo'l orasidagi farq nima?</h4>
<p>Nisbiy yo'l (masalan <code>"static"</code>) jarayonning <strong>joriy ishchi papkasi</strong> (working directory, cwd)ga nisbatan hisoblanadi &mdash; bu esa dastur qanday ishga tushirilishiga qarab <strong>o'zgarishi mumkin</strong>. Mutlaq yo'l (<code>os.path.dirname(os.path.abspath(__file__))</code> orqali qurilgan) esa doim <code>app.py</code> faylining haqiqiy joylashgan joyidan hisoblanadi &mdash; dastur qayerdan ishga tushirilishidan qat'i nazar <strong>o'zgarmaydi</strong>.</p>

<h4>3. Nega bu xato lokalda umuman sezilmaydi?</h4>
<p>Chunki rivojlantirish paytida siz deyarli doim <code>cd moneylog/backend && python app.py</code> kabi buyruqni loyihaning o'zidan ishga tushirasiz &mdash; shu sababli cwd va faylning haqiqiy joyi <strong>tasodifan</strong> mos keladi. Xato faqat production'da, deploy jarayoni boshqa working directory tanlaganda paydo bo'ladi.</p>

<h4>4. Nega bunda faqat frontend buziladi, API esa ishlab turaveradi?</h4>
<p><code>/api/expenses</code> kabi endpoint'lar ma'lumotlar bazasi bilan ishlaydi, fayl tizimidagi nisbiy yo'lga bog'liq emas. Faqat <code>send_from_directory()</code> chaqiruvi fayl tizimidan statik fayl o'qiydi &mdash; shuning uchun aynan shu qism, va faqat shu qism, noto'g'ri yo'l tufayli 404 qaytaradi.</p>

<h4>5. Nega bot va Flask baribir BIR XIL <code>DATABASE_URL</code>ga muhtoj (yana)?</h4>
<p>5-darsdan boshlab ta'kidlangan tamoyil deploy bosqichida ham amal qiladi: ikkalasi ham bitta production ma'lumotlar bazasidagi <strong>bir xil</strong> foydalanuvchilar va xarajatlar bilan ishlashi kerak, aks holda web sahifada qo'shilgan xarajat botda ko'rinmaydi (yoki aksincha).</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Vanilla JS + Flask'da frontend va API bitta "Web Service" sifatida deploy qilinishi mumkin</li>
<li>✅ Bot baribir alohida "Background Worker" sifatida deploy qilinishi shart</li>
<li>✅ Nisbiy yo'l (masalan <code>"static"</code>) jarayonning ishchi papkasiga bog'liq, mutlaq yo'l esa emas</li>
<li>✅ <code>os.path.dirname(os.path.abspath(__file__))</code> - statik/shablon yo'llarini har doim mutlaq qilib qurish usuli</li>
<li>✅ Noto'g'ri nisbiy yo'l odatda lokalda sezilmaydi, faqat production deploy'da 404 sifatida chiqadi</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz MoneyLog'ni 1-bosqichdagi bo'sh repo'dan boshlab, ma'lumotlar bazasi sxemasi, Flask API, vanilla JS frontend, autentifikatsiya, Telegram bot orqali tezkor xarajat qo'shish, avtomatik oylik byudjet ogohlantirishi va nihoyat <strong>to'g'ri, ikki qismli production deploy</strong>gacha qurdingiz. Bu &mdash; Flask va Telegram Bot kurslarida alohida o'rgangan bilimlarni, build qadamisiz vanilla JavaScript bilan birga, <strong>bitta, real loyiha</strong>da birlashtirish tajribasi edi.</p>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 7-BOSQICH (CAPSTONE YAKUNI): Deploy va nisbiy yo'l xatosi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app.py - statik fayllarni TO'G'RI, mutlaq yo'l bilan berish
# ─────────────────────────────────────────────────────────────────────

import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ─────────────────────────────────────────────────────────────────────
# 2) Xizmat turlari va environment (izohda - deploy tushunchasi, kod emas)
# ─────────────────────────────────────────────────────────────────────

# moneylog-web  -> "Web Service" (Flask: API + frontend, bitta jarayon)
# moneylog-bot  -> "Background Worker" (bot/bot.py: doim ishlab turadi)
#
# .env (ikkalasida HAM bir xil):
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - oddiy nisbiy yo'l (izohda)
# ─────────────────────────────────────────────────────────────────────

# FRONTEND_DIR = "static"          # ❌ joriy ishchi papkaga (cwd) nisbatan!
#
# @app.route("/")
# def index():
#     return send_from_directory(FRONTEND_DIR, "index.html")
#
# Lokalda ishlaydi (cwd == app.py papkasi), production'da esa gunicorn/
# systemd boshqa working directory'dan ishga tushirilsa - 404!
"""

L7_EX = [
    {
        "title": "MoneyLog'da nechta deploy birligi bor?",
        "description": "1-bosqichdagi arxitektura tanlovi tufayli, MoneyLog production'da nechta alohida deploy birligiga (xizmatga) ega?",
        "exercise_type": "multiple_choice",
        "options": [
            "Uchta: Flask API, statik frontend, bot",
            "Ikkita: Flask (API + frontend birga), bot",
            "Bitta: hammasi bir konteynerda",
            "To'rtta: Flask, frontend, bot, va ma'lumotlar bazasi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Vanilla JS build qadamini talab qilmaydi - shuning uchun Flask uni o'zi bera oladi.",
        "explanation": "1-bosqichda Flask frontendni o'zi statik fayl sifatida berishga qaror qilingani uchun API va frontend BITTA \"Web Service\"da birlashadi; faqat bot alohida \"Background Worker\" bo'lib qoladi - jami ikkita deploy birligi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nisbiy va mutlaq yo'l orasidagi farq",
        "description": "send_from_directory(\"static\", ...) kabi nisbiy yo'l nimaga nisbatan hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "app.py fayli qayerda joylashgan bo'lsa, shu joyga nisbatan",
            "Jarayonning joriy ishchi papkasiga (working directory, cwd) nisbatan",
            "Har doim loyihaning tub (root) papkasiga nisbatan",
            "Server domenining URL manziliga nisbatan",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "cwd - dastur QAYERDAN ishga tushirilgani, dastur QAYERDA joylashgani emas.",
        "explanation": "Nisbiy yo'l jarayonning joriy ishchi papkasiga (cwd) nisbatan hisoblanadi - bu esa dastur qanday va qayerdan ishga tushirilishiga qarab o'zgarishi mumkin, shuning uchun ishonchsiz.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "MoneyLog deploy jarayonini tartiblang",
        "description": "MoneyLog'ni production'ga deploy qilish umumiy jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Statik yo'llar os.path.abspath(__file__) asosida mutlaq qilib qurilganiga ishonch hosil qilinadi",
            "Flask (API + frontend) \"Web Service\" sifatida deploy qilinadi",
            "bot/bot.py \"Background Worker\" sifatida, Flask bilan BIR XIL DATABASE_URL bilan deploy qilinadi",
            "Bosh sahifa, statik fayllar va bot jonli holatda tekshiriladi, README yangilanadi",
        ],
        "correct_order": [
            "Statik yo'llar os.path.abspath(__file__) asosida mutlaq qilib qurilganiga ishonch hosil qilinadi",
            "Flask (API + frontend) \"Web Service\" sifatida deploy qilinadi",
            "bot/bot.py \"Background Worker\" sifatida, Flask bilan BIR XIL DATABASE_URL bilan deploy qilinadi",
            "Bosh sahifa, statik fayllar va bot jonli holatda tekshiriladi, README yangilanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nisbiy yo'lni mutlaq qilib qurish usuli",
        "description": "Statik/shablon papka yo'lini app.py joylashgan joydan mustaqil, doim to'g'ri hisoblash uchun qanday funksiya kombinatsiyasi ishlatiladi? (nomini yozing, masalan: os.path.xxx(os.path.xxx(__file__)))",
        "exercise_type": "text_input",
        "expected_answer": "os.path.dirname(os.path.abspath(__file__))",
        "hint": "Ikkita os.path funksiyasi ketma-ket ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega nisbiy yo'l xatosi lokalda sezilmay, faqat production'da chiqadi?",
        "description": (
            "FRONTEND_DIR = \"static\" kabi nisbiy yo'l lokal rivojlantirishda "
            "odatda muammosiz ishlaydi, lekin production serverga deploy "
            "qilinganda 404 xatosiga olib keladi. Nega bu farq yuzaga "
            "keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Lokal rivojlantirishda dasturchi deyarli doim 'python app.py' "
            "yoki 'flask run' buyrug'ini AYNAN app.py fayli joylashgan "
            "papkaning ichidan ishga tushiradi - shuning uchun jarayonning "
            "joriy ishchi papkasi (cwd) va app.py joylashgan joy TASODIFAN "
            "bir xil bo'lib chiqadi, va 'static' kabi nisbiy yo'l to'g'ri "
            "ishlaydi. Production serverda esa deploy vositasi (gunicorn, "
            "systemd, Docker) ko'pincha butunlay boshqa working "
            "directory'dan (masalan repo tub papkasidan) ishga tushiradi - "
            "endi cwd va app.py joylashgan joy ENDI bir xil emas, shuning "
            "uchun 'static' noto'g'ri joyga ishora qiladi va barcha CSS/JS "
            "fayllar uchun 404 xatosi qaytadi."
        ),
        "hint": "Lokalda siz dasturni QAYERDAN ishga tushirasiz? Production serverda buni KIM va QAYERDAN ishga tushiradi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L7_TASK = {
    "task_title": "MoneyLog — CAPSTONE yakuni: to'liq deploy qilingan loyiha",
    "task_description": (
        "MoneyLog'ni haqiqiy hostingga deploy qiling: Flask (API + "
        "frontend, bitta Web Service) va Telegram bot (Background "
        "Worker). Ikkalasi BIR XIL production ma'lumotlar bazasiga "
        "ulanganini tekshiring, statik fayl yo'llari mutlaq ekanini "
        "tasdiqlang. README.md'ni jonli havola va yakuniy sinov ro'yxati "
        "bilan yangilang."
    ),
    "task_requirements": (
        "• Flask (API + frontend) haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
        "• Statik fayl yo'llari os.path.dirname(os.path.abspath(__file__)) asosida mutlaq qurilgan\n"
        "• Bosh sahifa va barcha CSS/JS fayllar production'da TO'G'RI yuklanadi (404 emas)\n"
        "• Telegram bot haqiqiy hostingda Background Worker sifatida ishlab turibdi (Web Service emas)\n"
        "• Bot va Flask BIR XIL production PostgreSQL bazasiga ulangan\n"
        "• Web saytda xarajat qo'shish HAMDA Telegram bot orqali matn bilan xarajat qo'shish ikkalasi ham ishlaydi\n"
        "• README.md: jonli havola, 7/7 bosqich yakunlangan checklist, sinov ro'yxati\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
        "(Flask + bot) tekshiradi, alohida live_demo_url maydoni endi shart emas"
    ),
    "task_technologies": "Render/Railway (Web Service + Background Worker), PostgreSQL, os.path",
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
