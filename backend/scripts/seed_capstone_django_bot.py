"""Seed "Capstone 2: Django + React + Telegram Bot" (7 lessons): the second
entry in the cross-course capstone track. Unlike the first capstone (React +
Node/Express), this one spans THREE tracks at once — Django (course 82),
React (course 43), and Telegram Bot aiogram (course 48) — building one
project, "StudyMate", a student assignment tracker with a web app AND a
Telegram bot reading/writing the SAME database, sending deadline reminders.

Like the first capstone, every lesson carries a real project-submission
assignment via task_title/task_description/task_requirements/
task_technologies/task_deadline_days on Lesson (same mechanism as 255 other
lessons platform-wide) — students build ONE evolving project across all 7
milestones, resubmitting the same (updated) github_url/live_demo_url each
time via the existing Submission + AI-grading pipeline. No schema changes.

Usage:
    cd backend
    python -m scripts.seed_capstone_django_bot
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
    "title": "Capstone 2: Django + React + Telegram Bot",
    "description": (
        "Python: Django Asoslari, React Asoslari va Telegram Bot aiogram "
        "kurslarini tugatgan dasturchilar uchun: uchta texnologiyani BIR "
        "loyihada birlashtirasiz. 7 bosqichda 'StudyMate' — talabalar uchun "
        "topshiriqlar (assignment) kuzatuvchisini qurasiz: Django backend, "
        "React frontend HAMDA muddati yaqinlashgan topshiriqlar haqida "
        "avtomatik xabar beruvchi Telegram bot — hammasi bitta ma'lumotlar "
        "bazasi bilan ishlaydi. Har bir bosqich haqiqiy loyiha topshirig'i "
        "sifatida baholanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 6,
    "max_points": 250,
    "category_id": 8,  # Python
    "prerequisite_course_id": 82,  # Python: Django Asoslari (also assumes course 43: React Asoslari, course 48: Telegram Bot aiogram)
    "is_active": True,
    "is_published": False,  # flip to True once all 7 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Loyihalash va repo skeleton",
     "scope": "DB schema design (users w/ telegram_chat_id, subjects, assignments), repo scaffold, README."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-Django backend API",
     "scope": "Django models + plain-view JSON API for subjects/assignments CRUD."},
    {"order": 2, "ref": "L3", "status": "done", "lang": "javascript",
     "title": "3-React frontend",
     "scope": "React consuming the Django API, rendering assignments."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Autentifikatsiya",
     "scope": "Token-based auth on Django (hand-rolled, consumed by React)."},
    {"order": 4, "ref": "L5", "status": "done",
     "title": "5-Telegram bot: hisobni bog'lash va buyruqlar",
     "scope": "aiogram bot linking telegram_chat_id to a user account, /topshiriqlar command reading the SAME DB."},
    {"order": 5, "ref": "L6", "status": "done",
     "title": "6-Avtomatik bildirishnomalar",
     "scope": "Scheduled job checking upcoming deadlines and sending Telegram reminders."},
    {"order": 6, "ref": "L7", "status": "done",
     "title": "7-Polish va Deploy (CAPSTONE yakuni)",
     "scope": "Deploy Django backend, React frontend, and the bot together; final README + live_demo_url."},
]


L1_TEXT = """\
<h2>StudyMate — 7 bosqichda uchta texnologiyani birlashtirish</h2>

<pre class="mermaid">
flowchart LR
    PLAN["1-Loyihalash"] --> API["2-Django API"]
    API --> FE["3-React frontend"]
    FE --> AUTH["4-Autentifikatsiya"]
    AUTH --> BOT["5-Telegram bot bog'lash"]
    BOT --> NOTIFY["6-Bildirishnomalar"]
    NOTIFY --> DEPLOY["7-Deploy"]
</pre>

<p>Birinchi capstone kursida React va Node.js/Express'ni birlashtirgan bo'lsangiz, bu safar <strong>uchta</strong> texnologiyani — Django, React va Telegram Bot (aiogram) — <strong>bitta</strong> loyihada qo'shasiz: <strong>StudyMate</strong> — talabalar uchun topshiriqlar (assignment) kuzatuvchisi. Web sahifa ORQALI ham, Telegram bot ORQALI ham <strong>bir xil</strong> ma'lumotlar bazasi bilan ishlaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — repo tuzilmasi: uchta qism, bitta baza</h4>
<pre><code># StudyMate uchun monorepo - endi UCHTA papka
studymate/
  django_backend/     # Django + PostgreSQL (2-darsda quriladi)
    manage.py
    studymate/
  frontend/             # React (3-darsda quriladi)
    package.json
    src/
  telegram_bot/         # aiogram bot (5-6-darslarda quriladi)
    bot.py
    requirements.txt
  README.md
  .gitignore

# ❗ ENG MUHIM qaror: telegram_bot/ O'ZINING alohida bazasini yaratmaydi -
# u django_backend/ bilan BIR XIL PostgreSQL bazasiga ulanadi!</code></pre>

<h4>BLOKA 2 — DB sxemasi: bot va web uchun BIR XIL jadvallar</h4>
<pre><code># StudyMate uchun asosiy jadvallar:
#
# users            (id, ism, email, parol_hash, telegram_chat_id NULLABLE,
#                    link_kodi NULLABLE, yaratilgan_vaqt)
# fanlar           (id, nomi, user_id -> users.id)
# topshiriqlar     (id, sarlavha, matn, muddat_vaqti, bajarilgan,
#                    fan_id -> fanlar.id, user_id -> users.id, yaratilgan_vaqt)
#
# ❗ telegram_chat_id — foydalanuvchi Telegram akkauntini web akkauntiga
#   "bog'lagandan" keyin to'ldiriladi (5-darsda ko'ramiz)
# ❗ link_kodi — bog'lash jarayonida vaqtincha ishlatiladigan noyob kod

# Bu sxema Django modellariga (2-darsda) VA aiogram bot kodiga (5-darsda)
# bab-baravar tayanch bo'ladi - IKKALASI HAM shu jadvallarni o'qiydi/yozadi.</code></pre>

<h4>BLOKA 3 — README.md: uchta qismning holati</h4>
<pre><code># README.md
# StudyMate

## Loyiha haqida
Talabalar uchun topshiriqlar kuzatuvchisi - Django + React + Telegram Bot,
bitta umumiy PostgreSQL bazasi bilan.

## Texnologiyalar
- Backend: Django, PostgreSQL
- Frontend: React
- Bot: aiogram (Telegram)

## Holat
- [x] Loyihalash va repo skeleton
- [ ] Django backend API
- [ ] React frontend
- [ ] Autentifikatsiya
- [ ] Telegram bot: bog'lash va buyruqlar
- [ ] Avtomatik bildirishnomalar
- [ ] Deploy</code></pre>

<h3>🐛 Ataylab qiyin: bot uchun alohida baza rejalashtirish</h3>
<p>Ko'p boshlang'ich dasturchilar Telegram botni "alohida kichik loyiha" deb o'ylab, unga <strong>o'zining</strong> SQLite bazasini rejalashtiradi:</p>
<pre><code># ❌ XATO reja:
# telegram_bot/bot.py o'zining bot_data.db (SQLite) faylini ishlatadi
# django_backend/ esa alohida PostgreSQL bazasini ishlatadi

# Muammo: agar foydalanuvchi web saytda topshiriq qo'shsa, bu ma'lumot
# FAQAT Django bazasida bo'ladi. Bot esa o'zining SQLite bazasini o'qiydi -
# u web saytdagi topshiriqlarni umuman "ko'rmaydi"!</code></pre>
<p><strong>Natija:</strong> agar bot va web ilova <strong>turli</strong> bazalarga ulansa, ular <strong>bir-birining ma'lumotini ko'ra olmaydi</strong> — bu butun loyihaning maqsadini (bot orqali ham, web orqali ham bir xil ma'lumot bilan ishlash) buzadi. To'g'ri yechim: <strong>bitta</strong> PostgreSQL bazasi yaratish, va botga ham, Django'ga ham <strong>bir xil</strong> ulanish ma'lumotlarini (<code>DATABASE_URL</code>) berish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega uchta papka (django_backend/frontend/telegram_bot) bitta repo'da?</h4>
<p>Bu — birinchi capstone'dagi monorepo tamoyilining davomi, endi uchinchi qism (bot) bilan. Barcha uch qismning kodi bitta joyda bo'lishi, ularning bir-biriga bog'liqligini (ayniqsa umumiy baza orqali) kuzatishni osonlashtiradi.</p>

<h4>2. Nega bot va Django BIR XIL bazaga ulanishi shart?</h4>
<p>StudyMate'ning butun g'oyasi — foydalanuvchi ma'lumotni <strong>istalgan</strong> interfeys (web yoki Telegram) orqali kirita olishi, va boshqa interfeysda ham <strong>darhol</strong> ko'rinishi. Bu faqat ikkalasi <strong>bitta</strong> haqiqiy ma'lumotlar bazasiga ulangandagina mumkin.</p>

<h4>3. telegram_chat_id va link_kodi nima uchun kerak?</h4>
<p><code>telegram_chat_id</code> — Django foydalanuvchisi bilan uning Telegram akkountini bog'lash uchun. <code>link_kodi</code> esa 5-darsda ko'radigan "bog'lash" jarayonida vaqtincha ishlatiladigan noyob kod — foydalanuvchi web saytda kod oladi, botga yuboradi, va shu orqali ikkala akkount bog'lanadi.</p>

<h4>4. Nega bu sxema ikkala kod bazasiga (Django VA bot) tayanch bo'ladi?</h4>
<p>Django modellari (2-darsda) va aiogram bot kodi (5-darsda) <strong>ikkalasi ham</strong> aynan shu jadvallarga murojaat qiladi — biri Django ORM orqali, ikkinchisi esa to'g'ridan-to'g'ri SQL yoki Django ORM'ni bot ichida ham ishlatib. Sxema noaniq bo'lsa, bu ikki alohida kod bazasi orasida <strong>mos kelmovchilik</strong> yuzaga kelishi mumkin.</p>

<h4>5. Bu loyiha nega uchta alohida kursni birlashtiradi?</h4>
<p>Django (backend + ORM), React (frontend) va Telegram Bot (aiogram) kurslarida <strong>alohida</strong> o'rgangan bilimlar bu yerda <strong>bitta, real maqsad</strong> uchun (talabalarga topshiriqlarni kuzatishda yordam berish) birlashadi — bu haqiqiy loyihalarda ko'p uchraydigan "bir nechta interfeys, bitta backend" arxitekturasi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Uch qismli monorepo: django_backend/, frontend/, telegram_bot/</li>
<li>✅ Bot va web ilova <strong>bitta, umumiy</strong> ma'lumotlar bazasiga ulanishi shart</li>
<li>✅ <code>telegram_chat_id</code> va <code>link_kodi</code> — web akkaunt va Telegram akkauntni bog'lash uchun</li>
<li>✅ DB sxemasi Django VA bot kodining ikkalasi uchun ham yagona tayanch</li>
<li>✅ Bu kurs uchta alohida texnologiyani bitta real arxitekturada birlashtiradi</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 1-BOSQICH: Loyihalash va repo skeleton
# ════════════════════════════════════════════════════════════════════

# Bu dars kod yozishdan ko'ra REJALASHTIRISHGA bag'ishlangan.
# Quyida - StudyMate uchun DB sxemasining "qog'ozdagi" tasviri:

db_sxemasi = {
    "users": {
        "id": "SERIAL PRIMARY KEY",
        "ism": "VARCHAR(100)",
        "email": "VARCHAR(255) UNIQUE",
        "parol_hash": "VARCHAR(255)",
        "telegram_chat_id": "BIGINT NULL",   # bog'lanmagan bo'lsa NULL
        "link_kodi": "VARCHAR(10) NULL",     # bog'lash jarayoni uchun vaqtinchalik
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
    "fanlar": {
        "id": "SERIAL PRIMARY KEY",
        "nomi": "VARCHAR(100)",
        "user_id": "INTEGER REFERENCES users(id)",
    },
    "topshiriqlar": {
        "id": "SERIAL PRIMARY KEY",
        "sarlavha": "VARCHAR(200)",
        "matn": "TEXT",
        "muddat_vaqti": "TIMESTAMP",
        "bajarilgan": "BOOLEAN DEFAULT false",
        "fan_id": "INTEGER REFERENCES fanlar(id)",
        "user_id": "INTEGER REFERENCES users(id)",
        "yaratilgan_vaqt": "TIMESTAMP DEFAULT NOW()",
    },
}

print(db_sxemasi)

# ─────────────────────────────────────────────────────────────────────
# Repo tuzilmasi (izohda - papka/fayl tuzilmasi, kod emas)
# ─────────────────────────────────────────────────────────────────────

# studymate/
#   django_backend/
#   frontend/
#   telegram_bot/
#   README.md
#   .gitignore

# ─────────────────────────────────────────────────────────────────────
# ENG MUHIM QAROR (izohda)
# ─────────────────────────────────────────────────────────────────────

# telegram_bot/ VA django_backend/ BIR XIL DATABASE_URL'ga ulanadi -
# botning o'zining alohida bazasi BO'LMAYDI!
"""

L1_EX = [
    {
        "title": "Nega uchta papka bitta repo'da (monorepo)?",
        "description": "StudyMate uchun nega django_backend/, frontend/ va telegram_bot/ bitta repo'da saqlanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki Git faqat bitta papkani qo'llab-quvvatlaydi",
            "Uch qismning kodi bitta joyda bo'lishi, ularning bog'liqligini kuzatishni osonlashtiradi",
            "Chunki Telegram bot alohida repo'da ishlay olmaydi",
            "Bu Django'ning majburiy talabi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu birinchi capstone'dagi monorepo g'oyasining davomi.",
        "explanation": "Monorepo uchta qismning kodini bitta joyda saqlab, ularning bir-biriga (ayniqsa umumiy baza orqali) bog'liqligini kuzatishni osonlashtiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Bot va Django nega bir xil bazaga ulanishi kerak?",
        "description": "Telegram bot va Django backend nega aynan bitta, umumiy ma'lumotlar bazasiga ulanishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki PostgreSQL faqat bitta ulanishga ruxsat beradi",
            "Foydalanuvchi web yoki bot orqali kiritgan ma'lumot ikkala interfeysda ham ko'rinishi uchun",
            "Chunki alohida bazalar qimmatga tushadi",
            "Bu shart emas, ikkalasi alohida ishlashi mumkin",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "StudyMate'ning maqsadi - bir xil ma'lumotga ikki xil interfeys orqali kirish.",
        "explanation": "StudyMate'ning maqsadi foydalanuvchi ma'lumotni istalgan interfeys orqali kiritib, boshqa interfeysda ham darhol ko'ra olishi — bu faqat ikkalasi bitta haqiqiy bazaga ulangandagina mumkin.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Hisob bog'lash jarayonini tartiblang",
        "description": "link_kodi orqali web akkaunt va Telegram akkauntni bog'lash jarayonini mantiqiy tartibda joylang (5-darsda batafsil ko'riladi).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi web saytda ro'yxatdan o'tadi, unga link_kodi beriladi",
            "Foydalanuvchi Telegram botga o'tib, /link buyrug'i bilan kodni yuboradi",
            "Bot kodni bazadan qidirib, mos foydalanuvchini topadi",
            "Foydalanuvchining telegram_chat_id maydoni to'ldiriladi - endi ikkala akkaunt bog'langan",
        ],
        "correct_order": [
            "Foydalanuvchi web saytda ro'yxatdan o'tadi, unga link_kodi beriladi",
            "Foydalanuvchi Telegram botga o'tib, /link buyrug'i bilan kodni yuboradi",
            "Bot kodni bazadan qidirib, mos foydalanuvchini topadi",
            "Foydalanuvchining telegram_chat_id maydoni to'ldiriladi - endi ikkala akkaunt bog'langan",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bog'lanmagan foydalanuvchida telegram_chat_id qiymati",
        "description": "Agar foydalanuvchi hali Telegram akkauntini bog'lamagan bo'lsa, users jadvalidagi telegram_chat_id ustuni qanday qiymatga ega bo'lishi kerak? (bir so'z bilan javob bering)",
        "exercise_type": "text_input",
        "expected_answer": "NULL",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega botga alohida SQLite baza rejalashtirish xato?",
        "description": (
            "Agar dasturchi telegram_bot/ uchun alohida SQLite fayl "
            "(masalan bot_data.db) rejalashtirsa, django_backend/ esa "
            "alohida PostgreSQL bazasidan foydalansa, bu qanday amaliy "
            "muammoga olib keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Agar bot va Django ilovasi ikkita alohida ma'lumotlar "
            "bazasiga ulansa, ular bir-birining ma'lumotini umuman "
            "ko'ra olmaydi. Masalan, foydalanuvchi web saytda yangi "
            "topshiriq qo'shsa, bu yozuv faqat Django'ning PostgreSQL "
            "bazasida saqlanadi. Telegram bot esa o'zining alohida "
            "SQLite bazasini o'qigani uchun, bu yangi topshiriq haqida "
            "umuman xabardor bo'lmaydi va uni foydalanuvchiga "
            "ko'rsata olmaydi. Bu StudyMate'ning asosiy maqsadini — "
            "bir xil ma'lumotga istalgan interfeys orqali kirish "
            "imkonini — butunlay buzadi."
        ),
        "hint": "Agar ikkita alohida baza mavjud bo'lsa, ular bir-birining yozuvlarini \"ko'rishi\" mumkinmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L1_TASK = {
    "task_title": "StudyMate — repo skeleton va umumiy DB sxema hujjati",
    "task_description": (
        "StudyMate loyihasi uchun GitHub'da monorepo yarating (django_backend/, "
        "frontend/, telegram_bot/ papkalari bilan), to'liq README.md yozing va "
        "users/fanlar/topshiriqlar jadvallari uchun DB sxemasini README'ga "
        "qo'shing. Sxemada telegram_chat_id va link_kodi maydonlari bo'lishi "
        "va nima uchun kerakligi tushuntirilishi shart."
    ),
    "task_requirements": (
        "• GitHub'da 'studymate' nomli public repo yaratilgan\n"
        "• django_backend/, frontend/, telegram_bot/ papkalari mavjud\n"
        "• README.md: loyiha tavsifi, texnologiyalar, holat checklist'i\n"
        "• README.md'da users (telegram_chat_id, link_kodi bilan), fanlar, "
        "topshiriqlar jadvallari va ular orasidagi bog'lanishlar tasvirlangan\n"
        "• README'da botning nega Django bilan BIR XIL bazaga ulanishi "
        "kerakligi 2-3 gapda tushuntirilgan\n"
        "• .gitignore fayli mavjud (node_modules, .env, __pycache__ chiqarib tashlangan)"
    ),
    "task_technologies": "Git, GitHub, Markdown, PostgreSQL (sxema loyihalash)",
    "task_deadline_days": 3,
}


L2_TEXT = """\
<h2>2-bosqich: Django backend API — Fan va Topshiriq uchun CRUD</h2>

<pre class="mermaid">
flowchart LR
    MODEL["Django modellari (1-darsdagi sxemadan)"] --> VIEW["oddiy view + JsonResponse"]
    VIEW --> JSON["React'ga JSON qaytariladi"]
    VIEW -->|safe=False YO'Q| ERROR["TypeError: ro'yxatni to'g'ridan-to'g'ri qaytarib bo'lmaydi"]
</pre>

<p>Django Asoslari kursida modellar va oddiy view'larni o'rgangansiz. Bu bosqichda ularni <strong>JSON API</strong> sifatida quramiz — React frontend (3-darsda) va Telegram bot (5-darsda) <strong>ikkalasi ham</strong> shu endpoint'lardan foydalanadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — 1-darsdagi sxemadan Django modellari</h4>
<pre><code># studymate/models.py
from django.db import models
from django.contrib.auth.models import User

class Fan(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fanlar')

    def __str__(self):
        return self.nomi

class Topshiriq(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField(blank=True)
    muddat_vaqti = models.DateTimeField()
    bajarilgan = models.BooleanField(default=False)
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='topshiriqlar')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topshiriqlar')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha</code></pre>

<h4>BLOKA 2 — JSON qaytaruvchi view'lar</h4>
<pre><code># studymate/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Topshiriq

def topshiriq_to_dict(t):                          # ❗ model obyektini JSON-mos dict'ga aylantiradi
    return {
        "id": t.id, "sarlavha": t.sarlavha, "matn": t.matn,
        "muddat_vaqti": t.muddat_vaqti.isoformat(),  # ❗ datetime JSON'da string bo'lishi kerak
        "bajarilgan": t.bajarilgan, "fan_nomi": t.fan.nomi,
    }

@require_http_methods(["GET", "POST"])
@csrf_exempt                                         # ❗ tashqi (React) so'rovlar uchun, token auth bilan almashtiriladi (4-dars)
def topshiriqlar_view(request):
    if request.method == "GET":
        topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
        natija = [topshiriq_to_dict(t) for t in topshiriqlar]
        return JsonResponse(natija, safe=False)      # ❗ ro'yxat qaytarganda safe=False MAJBURIY

    ma_lumot = json.loads(request.body)
    yangi = Topshiriq.objects.create(
        sarlavha=ma_lumot["sarlavha"], matn=ma_lumot.get("matn", ""),
        muddat_vaqti=ma_lumot["muddat_vaqti"], fan_id=ma_lumot["fan_id"],
        user=request.user,
    )
    return JsonResponse(topshiriq_to_dict(yangi), status=201)   # ❗ bitta obyekt - safe=False shart emas</code></pre>

<h4>BLOKA 3 — urls.py</h4>
<pre><code># studymate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/topshiriqlar/', views.topshiriqlar_view, name='topshiriqlar'),
]</code></pre>

<h3>🐛 Ataylab xato — ro'yxat qaytarishda safe=False'ni unutish</h3>
<pre><code>def topshiriqlar_view_xato(request):
    topshiriqlar = Topshiriq.objects.filter(user=request.user)
    natija = [topshiriq_to_dict(t) for t in topshiriqlar]
    return JsonResponse(natija)   # ❌ safe=False YO'Q!

# So'rov yuborilganda:
# ❌ TypeError: In order to allow non-dict objects to be serialized set the
#    safe parameter to False
# (Django standart holda FAQAT dict obyektlarni xavfsiz deb hisoblaydi!)</code></pre>

<p><strong>Natija:</strong> Django'ning <code>JsonResponse</code>i standart holda <strong>faqat dictionary</strong> (yagona obyekt) qaytarishni "xavfsiz" deb hisoblaydi — bu xavfsizlik choralaridan biri (ba'zi eski brauzer zaifliklarining oldini olish uchun). Agar siz <strong>ro'yxat</strong> (list) qaytarmoqchi bo'lsangiz (masalan barcha topshiriqlar), Django buni avtomatik rad etadi va <code>safe=False</code>ni <strong>aniq</strong> ko'rsatishingizni talab qiladi — bu "men bu ro'yxatni ataylab, bilib turib qaytaryapman" deb Django'ga aytishga o'xshaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega alohida <code>topshiriq_to_dict()</code> funksiyasi yozilgan?</h4>
<p>Django model obyektini (<code>Topshiriq</code>) to'g'ridan-to'g'ri JSON'ga aylantirib bo'lmaydi — u Python obyekti, JSON esa faqat oddiy turlarni (string, son, ro'yxat, dict) qo'llab-quvvatlaydi. <code>topshiriq_to_dict()</code> model obyektini JSON-mos <code>dict</code>ga "tarjima qiladi", va bu funksiyani har bir view'da qayta yozmaslik uchun alohida chiqarilgan.</p>

<h4>2. Nega <code>muddat_vaqti.isoformat()</code> ishlatiladi?</h4>
<p>Python'ning <code>datetime</code> obyekti JSON'ning standart turlaridan biri emas — uni to'g'ridan-to'g'ri <code>JsonResponse</code>ga berish xato beradi. <code>.isoformat()</code> uni JSON qo'llab-quvvatlaydigan <strong>matn</strong> ko'rinishiga ("2026-08-01T23:59:00") aylantiradi.</p>

<h4>3. <code>select_related('fan')</code> nega ishlatilgan?</h4>
<p>4-darsdagi (Django Asoslari kursi) N+1 muammosini eslang — <code>select_related</code> <code>Fan</code> ma'lumotini bitta so'rovda <code>Topshiriq</code> bilan birga oladi, har bir topshiriq uchun alohida so'rov yuborilishining oldini oladi.</p>

<h4>4. Nega <code>safe=False</code> faqat ro'yxat qaytarganda kerak?</h4>
<p>Django xavfsizlik choralaridan biri sifatida, faqat <code>dict</code> obyektlarni "xavfsiz" deb hisoblaydi. Bitta obyekt (<code>topshiriq_to_dict(yangi)</code>) allaqachon <code>dict</code> bo'lgani uchun <code>safe=False</code> shart emas — u faqat <code>list</code> qaytarilganda kerak bo'ladi.</p>

<h4>5. <code>@csrf_exempt</code> nega vaqtinchalik ishlatilmoqda?</h4>
<p>Django standart holda barcha POST so'rovlarda CSRF token talab qiladi (bu web-forma orqali to'ldiriladigan sahifalar uchun mo'ljallangan). Alohida frontend (React)dan kelgan API so'rovlari uchun bu boshqacha yondashuv (token-based autentifikatsiya) kerak bo'ladi — buni 4-darsda to'g'ri hal qilamiz, hozircha vaqtinchalik <code>@csrf_exempt</code> bilan o'tkazib turamiz.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-darsdagi sxema Django modellariga aylantirildi (ForeignKey bilan)</li>
<li>✅ Model obyektlarini JSON-mos <code>dict</code>ga aylantiruvchi alohida funksiya yozish yaxshi amaliyot</li>
<li>✅ <code>datetime</code> maydonlari JSON'ga qaytarishdan oldin <code>.isoformat()</code> bilan matnga aylantirilishi kerak</li>
<li>✅ <code>JsonResponse</code>da ro'yxat qaytarish uchun <code>safe=False</code> MAJBURIY</li>
<li>✅ <code>select_related</code> bog'langan ma'lumotni N+1 muammosisiz olish imkonini beradi</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 2-BOSQICH: Django backend API - Fan va Topshiriq uchun CRUD
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/models.py
# ─────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


class Fan(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fanlar')

    def __str__(self):
        return self.nomi


class Topshiriq(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField(blank=True)
    muddat_vaqti = models.DateTimeField()
    bajarilgan = models.BooleanField(default=False)
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='topshiriqlar')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topshiriqlar')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) studymate/views.py
# ─────────────────────────────────────────────────────────────────────

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def topshiriq_to_dict(t):
    return {
        "id": t.id, "sarlavha": t.sarlavha, "matn": t.matn,
        "muddat_vaqti": t.muddat_vaqti.isoformat(),
        "bajarilgan": t.bajarilgan, "fan_nomi": t.fan.nomi,
    }


@require_http_methods(["GET", "POST"])
@csrf_exempt
def topshiriqlar_view(request):
    if request.method == "GET":
        topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
        natija = [topshiriq_to_dict(t) for t in topshiriqlar]
        return JsonResponse(natija, safe=False)

    ma_lumot = json.loads(request.body)
    yangi = Topshiriq.objects.create(
        sarlavha=ma_lumot["sarlavha"], matn=ma_lumot.get("matn", ""),
        muddat_vaqti=ma_lumot["muddat_vaqti"], fan_id=ma_lumot["fan_id"],
        user=request.user,
    )
    return JsonResponse(topshiriq_to_dict(yangi), status=201)

# ─────────────────────────────────────────────────────────────────────
# 3) studymate/urls.py (izohda)
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('api/topshiriqlar/', views.topshiriqlar_view, name='topshiriqlar'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - safe=False'ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# def topshiriqlar_view_xato(request):
#     topshiriqlar = Topshiriq.objects.filter(user=request.user)
#     natija = [topshiriq_to_dict(t) for t in topshiriqlar]
#     return JsonResponse(natija)   # safe=False YO'Q!
# ❌ TypeError: In order to allow non-dict objects to be serialized set the
#    safe parameter to False
"""

L2_EX = [
    {
        "title": "topshiriq_to_dict() funksiyasi nima uchun kerak?",
        "description": "Nega Topshiriq model obyektini to'g'ridan-to'g'ri JsonResponse'ga bermasdan, avval topshiriq_to_dict() orqali dict'ga aylantiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu kodni tezroq ishlashini ta'minlaydi",
            "Django model obyekti Python obyekti bo'lib, JSON faqat oddiy turlarni (dict, list, string, son) qo'llab-quvvatlaydi",
            "Bu majburiy Django sintaksisi",
            "Faqat debugging uchun ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "JSON qanday turlarni qo'llab-quvvatlaydi?",
        "explanation": "Django model obyektini to'g'ridan-to'g'ri JSON'ga aylantirib bo'lmaydi, chunki u Python obyekti — topshiriq_to_dict() uni JSON qo'llab-quvvatlaydigan oddiy dict'ga \"tarjima qiladi\".",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "safe=False qachon kerak?",
        "description": "JsonResponse(natija, safe=False) yozuvida safe=False qachon zarur bo'ladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har doim, har qanday holatda",
            "Faqat natija ro'yxat (list) bo'lganda, dict bo'lmaganda",
            "Faqat POST so'rovlarda",
            "Hech qachon kerak emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Django standart holda faqat bitta turdagi obyektni \"xavfsiz\" deb hisoblaydi.",
        "explanation": "Django standart holda faqat dict obyektlarni xavfsiz deb hisoblaydi. Agar natija ro'yxat (list) bo'lsa, safe=False'ni aniq ko'rsatish shart.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "GET /api/topshiriqlar/ so'rovi jarayonini tartiblang",
        "description": "React'dan GET so'rovi kelganda topshiriqlar_view ichida bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "request.method == 'GET' tekshiriladi",
            "Topshiriq.objects.filter(user=...).select_related('fan') orqali ma'lumot olinadi",
            "Har bir topshiriq topshiriq_to_dict() orqali dict'ga aylantiriladi",
            "Natija ro'yxati JsonResponse(natija, safe=False) orqali qaytariladi",
        ],
        "correct_order": [
            "request.method == 'GET' tekshiriladi",
            "Topshiriq.objects.filter(user=...).select_related('fan') orqali ma'lumot olinadi",
            "Har bir topshiriq topshiriq_to_dict() orqali dict'ga aylantiriladi",
            "Natija ro'yxati JsonResponse(natija, safe=False) orqali qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "datetime maydonini JSON uchun matnga aylantiruvchi metod",
        "description": "Python datetime obyektini JSON qo'llab-quvvatlaydigan matn ko'rinishiga aylantiruvchi metodni yozing.",
        "exercise_type": "text_input",
        "expected_answer": "isoformat",
        "hint": "muddat_vaqti.___()",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega safe=False'siz TypeError chiqadi?",
        "description": (
            "topshiriqlar_view_xato() funksiyasida JsonResponse(natija) "
            "safe=False'siz chaqirilsa (natija — ro'yxat), nega Django "
            "TypeError xatosini beradi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django'ning JsonResponse'i xavfsizlik chorasi sifatida "
            "standart holda faqat dict (bitta obyekt) qaytarishni "
            "\"xavfsiz\" deb hisoblaydi — bu ba'zi eski brauzer "
            "zaifliklaridan himoyalanish uchun qilingan qaror. Agar "
            "natija list (ro'yxat) bo'lsa, Django buni avtomatik rad "
            "etadi va dasturchidan safe=False orqali \"bu ro'yxatni "
            "ataylab, bilib turib qaytaryapman\" deb aniq tasdiqlashni "
            "talab qiladi. Bu tasdiq berilmasa (safe=False yozilmasa), "
            "Django TypeError xatosini ko'taradi."
        ),
        "hint": "Django JsonResponse standart holda qaysi turdagi obyektni \"xavfsiz\" deb hisoblaydi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L2_TASK = {
    "task_title": "StudyMate — Django backend API (Fan + Topshiriq)",
    "task_description": (
        "1-bosqichdagi sxema asosida Fan va Topshiriq Django modellarini "
        "yarating, migratsiya qiling. topshiriqlar_view orqali GET (ro'yxat) "
        "va POST (yangi qo'shish) so'rovlarini qo'llab-quvvatlovchi JSON API "
        "quring. select_related orqali N+1 muammosining oldini oling."
    ),
    "task_requirements": (
        "• Fan va Topshiriq modellari to'g'ri ForeignKey'lar bilan yaratilgan\n"
        "• GET /api/topshiriqlar/ — joriy foydalanuvchining topshiriqlarini "
        "fan_nomi bilan birga JSON ro'yxat sifatida qaytaradi (safe=False)\n"
        "• POST /api/topshiriqlar/ — yangi topshiriq yaratadi, 201 qaytaradi\n"
        "• select_related('fan') ishlatilgan (N+1 muammosisiz)\n"
        "• datetime maydonlari .isoformat() bilan JSON-mos qilingan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Django, PostgreSQL, JsonResponse",
    "task_deadline_days": 5,
}


L3_TEXT = """\
<h2>3-bosqich: React frontend — Django API'ga ulanish</h2>

<pre class="mermaid">
flowchart LR
    REACT["React (localhost:3000)"] -->|fetch| DJANGO["Django API (localhost:8000)"]
    DJANGO -->|corsheaders noto'g'ri tartibda| BLOCKED["CORS xatosi"]
    DJANGO -->|CorsMiddleware to'g'ri joyda| OK["Ma'lumot muvaffaqiyatli qaytadi"]
</pre>

<p>2-bosqichdagi Django API'ga endi React orqali ulanamiz. Birinchi capstone kursida Node/Express bilan CORS'ni sozlagansiz — Django'da bu <code>django-cors-headers</code> paketi orqali amalga oshiriladi, va uning o'ziga xos "middleware tartibi" qoidasi bor.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — React'da Django API'dan ma'lumot olish</h4>
<pre><code>// frontend/src/api/topshiriqlar.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function topshiriqlarniOlish() {
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`);
  if (!javob.ok) throw new Error('Topshiriqlarni olishda xato');
  return await javob.json();
}

// frontend/src/components/TopshiriqRoyxati.jsx
import { useEffect, useState } from 'react';
import { topshiriqlarniOlish } from '../api/topshiriqlar';

function TopshiriqRoyxati() {
  const [royxat, setRoyxat] = useState([]);
  const [holat, setHolat] = useState('yuklanmoqda');

  useEffect(() => {
    topshiriqlarniOlish()
      .then((data) => { setRoyxat(data); setHolat('muvaffaqiyatli'); })
      .catch(() => setHolat('xato'));
  }, []);

  if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;

  return (
    <ul>
      {royxat.map((t) => (
        <li key={t.id}>{t.sarlavha} ({t.fan_nomi}) — {t.muddat_vaqti}</li>
      ))}
    </ul>
  );
}</code></pre>

<h4>BLOKA 2 — django-cors-headers o'rnatish va sozlash</h4>
<pre><code># pip install django-cors-headers

# studymate/settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',            # ❗ INSTALLED_APPS'ga qo'shiladi
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # ❗ MUHIM: CommonMiddleware'DAN OLDIN turishi shart!
    'django.middleware.common.CommonMiddleware',
    # ... qolgan middleware'lar ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',   # ❗ faqat React manzilidan kelgan so'rovlarga ruxsat
]</code></pre>

<h4>BLOKA 3 — CORS ishlashini tekshirish</h4>
<pre><code># To'g'ri sozlangandan keyin, brauzer konsolida xato chiqmasligi kerak:
# fetch('http://localhost:8000/api/topshiriqlar/') -> 200 OK, ma'lumot qaytadi

# Agar hali ham CORS xatosi chiqsa, birinchi tekshirish kerak bo'lgan narsa:
# MIDDLEWARE ro'yxatida CorsMiddleware CommonMiddleware'dan OLDIN turibdimi?</code></pre>

<h3>🐛 Ataylab xato — CorsMiddleware'ni noto'g'ri tartibga qo'yish</h3>
<pre><code># studymate/settings.py - middleware tartibi ALMASHTIRILGAN:
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',   # ❌ CorsMiddleware'dan OLDIN turibdi!
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

# django-cors-headers o'rnatilgan, CORS_ALLOWED_ORIGINS ham to'g'ri sozlangan,
# lekin React'dan so'rov yuborilganda:
# ❌ Baribir CORS xatosi chiqadi - garchi paket o'rnatilgan bo'lsa ham!</code></pre>

<p><strong>Natija:</strong> Django middleware'lari <strong>ro'yxatda yozilgan tartibda</strong> ishga tushadi. <code>CommonMiddleware</code> ba'zi holatlarda so'rovni <code>CorsMiddleware</code> CORS header'larini qo'shishidan <strong>oldin</strong> qayta ishlab, natijani "yopib qo'yishi" mumkin. Django-cors-headers'ning rasmiy hujjatlari <code>CorsMiddleware</code>ni <strong>iloji boricha yuqorida</strong>, ayniqsa <code>CommonMiddleware</code>dan <strong>oldin</strong> joylashtirishni talab qiladi — bu tartib buzilsa, paket o'rnatilgan va sozlangan bo'lsa ham, CORS ishlamay qolishi mumkin.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega Django'da CORS Node'dagidan boshqacha sozlanadi?</h4>
<p>Express'da <code>cors()</code> — oddiy middleware funksiyasi. Django'da esa CORS alohida paket (<code>django-cors-headers</code>) orqali amalga oshiriladi, va Django middleware tizimi <strong>tartibga</strong> juda sezgir — middleware'lar ro'yxatda yozilgan ketma-ketlikda ishlaydi.</p>

<h4>2. Middleware tartibi nega muhim?</h4>
<p>Har bir middleware so'rovni "kirishda" va javobni "chiqishda" qayta ishlaydi, ro'yxat tartibida (kirishda yuqoridan pastga, chiqishda pastdan yuqoriga). <code>CorsMiddleware</code> CORS header'larini javobga <strong>qo'shishi</strong> kerak — agar u boshqa middleware'lardan <strong>keyin</strong> joylashsa, ba'zi javoblar (masalan xato javoblari) bu header'larsiz qolishi mumkin.</p>

<h4>3. <code>CORS_ALLOWED_ORIGINS</code> nima qiladi?</h4>
<p>Bu — <strong>ruxsat etilgan</strong> origin'lar (frontend manzillari) ro'yxati. Faqat shu ro'yxatdagi manzillardan kelgan so'rovlarga <code>Access-Control-Allow-Origin</code> header'i qo'shiladi — bu Express'dagi <code>cors({ origin: '...' })</code>ning Django ekvivalenti.</p>

<h4>4. Nega bu xato "paket o'rnatilgan-ku" deb chalkashtiriladi?</h4>
<p>Dasturchi <code>django-cors-headers</code>ni to'g'ri o'rnatib, <code>CORS_ALLOWED_ORIGINS</code>ni ham to'g'ri sozlagan bo'ladi — sirtdan hamma narsa "to'g'ri" ko'rinadi. Lekin <code>MIDDLEWARE</code> ro'yxatidagi <strong>tartib</strong> noto'g'ri bo'lsa, bu sozlamalar kutilgancha ishlamaydi — bu xatoni topish qiyinroq qiladi, chunki sabab "sozlamada" emas, "tartibda".</p>

<h4>5. Nega CorsMiddleware yuqorida (CommonMiddleware'dan oldin) turishi kerak?</h4>
<p>Django hujjatlariga ko'ra, <code>CorsMiddleware</code> imkon qadar <strong>yuqorida</strong> joylashishi kerak, shunda u boshqa middleware'lar (masalan <code>CommonMiddleware</code>, u ba'zan qayta yo'naltirish yoki 404 javoblarini o'zi hal qiladi) so'rovni "yakunlashi"dan oldin CORS header'larini qo'shib ulguradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ React'da <code>fetch()</code> orqali Django JSON API'dan ma'lumot olish</li>
<li>✅ <code>django-cors-headers</code> — Django uchun CORS paketi</li>
<li>✅ <code>CORS_ALLOWED_ORIGINS</code> — Express'dagi <code>cors({ origin })</code>ning Django ekvivalenti</li>
<li>✅ Django middleware'lari <strong>ro'yxat tartibida</strong> ishlaydi — bu Express middleware tartibidan ham qattiqroq</li>
<li>✅ <code>CorsMiddleware</code> <code>CommonMiddleware</code>dan <strong>oldin</strong> joylashishi shart</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 3-BOSQICH: React frontend - Django API'ga ulanish
# ════════════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────────────────────────────
// 1) frontend/src/api/topshiriqlar.js
// ─────────────────────────────────────────────────────────────────────

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function topshiriqlarniOlish() {
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`);
  if (!javob.ok) throw new Error('Topshiriqlarni olishda xato');
  return await javob.json();
}

// ─────────────────────────────────────────────────────────────────────
// 2) frontend/src/components/TopshiriqRoyxati.jsx (izohda - JSX)
// ─────────────────────────────────────────────────────────────────────

// function TopshiriqRoyxati() {
//   const [royxat, setRoyxat] = useState([]);
//   const [holat, setHolat] = useState('yuklanmoqda');
//
//   useEffect(() => {
//     topshiriqlarniOlish()
//       .then((data) => { setRoyxat(data); setHolat('muvaffaqiyatli'); })
//       .catch(() => setHolat('xato'));
//   }, []);
//
//   if (holat === 'yuklanmoqda') return <p>Yuklanmoqda...</p>;
//
//   return (
//     <ul>
//       {royxat.map((t) => (
//         <li key={t.id}>{t.sarlavha} ({t.fan_nomi}) — {t.muddat_vaqti}</li>
//       ))}
//     </ul>
//   );
// }

# ─────────────────────────────────────────────────────────────────────
# 3) studymate/settings.py - django-cors-headers sozlash (Python, izohda)
# ─────────────────────────────────────────────────────────────────────

# INSTALLED_APPS = [
#     # ...
#     'corsheaders',
# ]
#
# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',      # CommonMiddleware'dan OLDIN!
#     'django.middleware.common.CommonMiddleware',
#     # ...
# ]
#
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - middleware tartibini almashtirish (izohda)
# ─────────────────────────────────────────────────────────────────────

# MIDDLEWARE = [
#     'django.middleware.common.CommonMiddleware',   # CorsMiddleware'dan OLDIN - XATO!
#     'corsheaders.middleware.CorsMiddleware',
# ]
# ❌ CORS_ALLOWED_ORIGINS to'g'ri bo'lsa ham, tartib xato bo'lgani uchun CORS ishlamaydi
"""

L3_EX = [
    {
        "title": "django-cors-headers nima uchun kerak?",
        "description": "Django'da django-cors-headers paketi asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumotlar bazasini tezlashtirish uchun",
            "Boshqa origin'dan (masalan React) kelgan so'rovlarga ruxsat berish uchun",
            "Django modellarini validatsiya qilish uchun",
            "Static fayllarni siqish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Express'dagi cors() paketining Django ekvivalenti.",
        "explanation": "django-cors-headers Django API'ga boshqa origin'dan (masalan alohida portda ishlayotgan React) kelgan so'rovlarga ruxsat berish uchun ishlatiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "CorsMiddleware qayerda joylashishi kerak?",
        "description": "MIDDLEWARE ro'yxatida CorsMiddleware qayerda joylashishi tavsiya etiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ro'yxatning eng oxirida",
            "Imkon qadar yuqorida, ayniqsa CommonMiddleware'dan oldin",
            "Joylashuvi ahamiyatsiz",
            "Faqat INSTALLED_APPS'da, MIDDLEWARE'da kerak emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Middleware'lar ro'yxat tartibida ishlaydi.",
        "explanation": "CorsMiddleware imkon qadar yuqorida, ayniqsa CommonMiddleware'dan oldin joylashishi kerak, aks holda boshqa middleware'lar CORS header qo'shilishidan oldin javobni \"yakunlab\" qo'yishi mumkin.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Django API'dan ma'lumot olish jarayonini tartiblang",
        "description": "React komponenti yuklanganda topshiriqlarniOlish() chaqirilib, ma'lumot ko'rsatilishigacha bo'lgan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "useEffect ichida topshiriqlarniOlish() chaqiriladi",
            "fetch() Django API'ga so'rov yuboradi",
            "CORS header'lari to'g'ri bo'lsa, brauzer javobni React kodiga uzatadi",
            "setRoyxat(data) chaqirilib, component qayta render bo'ladi",
        ],
        "correct_order": [
            "useEffect ichida topshiriqlarniOlish() chaqiriladi",
            "fetch() Django API'ga so'rov yuboradi",
            "CORS header'lari to'g'ri bo'lsa, brauzer javobni React kodiga uzatadi",
            "setRoyxat(data) chaqirilib, component qayta render bo'ladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Ruxsat etilgan origin'lar ro'yxati sozlamasi",
        "description": "Django settings.py'da ruxsat etilgan frontend manzillari ro'yxati qaysi sozlama orqali beriladi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "CORS_ALLOWED_ORIGINS",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega middleware tartibi noto'g'ri bo'lsa CORS ishlamaydi?",
        "description": (
            "django-cors-headers to'g'ri o'rnatilgan va CORS_ALLOWED_ORIGINS "
            "ham to'g'ri sozlangan, lekin MIDDLEWARE ro'yxatida "
            "CommonMiddleware CorsMiddleware'dan OLDIN joylashgan. Nega "
            "bu holda CORS baribir ishlamay qolishi mumkin? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django middleware'lari MIDDLEWARE ro'yxatida yozilgan aynan "
            "shu tartibda ishga tushadi. CommonMiddleware ba'zi "
            "holatlarda so'rovni qayta yo'naltirish yoki xato javoblarini "
            "hal qilish kabi vazifalarni bajaradi, va agar u "
            "CorsMiddleware'dan OLDIN turgan bo'lsa, javob CorsMiddleware "
            "CORS header'larini qo'shishga ulgurishidan oldin \"yakunlanib\" "
            "qolishi mumkin. Shuning uchun CORS_ALLOWED_ORIGINS to'g'ri "
            "sozlangan bo'lsa ham, agar middleware tartibi noto'g'ri "
            "bo'lsa, CORS header'lari ba'zi (yoki barcha) javoblarga "
            "qo'shilmay qolishi va CORS xatosi chiqishi mumkin."
        ),
        "hint": "Django middleware'lari qanday tartibda ishlaydi - yozilgan tartibda, yoki tasodifiy tartibda?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L3_TASK = {
    "task_title": "StudyMate — React frontend Django'ga ulangan",
    "task_description": (
        "React'da topshiriqlarni Django API'dan olib ko'rsatuvchi komponent "
        "yarating. Backend'da django-cors-headers'ni o'rnating va to'g'ri "
        "tartibda sozlang, .env orqali API manzilini boshqaring."
    ),
    "task_requirements": (
        "• frontend/src/api/topshiriqlar.js: topshiriqlarniOlish() funksiyasi\n"
        "• Component topshiriqlar ro'yxatini fan_nomi va muddat bilan birga ko'rsatadi\n"
        "• Yuklanish (loading) va xato holatlari boshqarilgan\n"
        "• Backend'da django-cors-headers o'rnatilgan, CorsMiddleware CommonMiddleware'dan oldin\n"
        "• CORS_ALLOWED_ORIGINS to'g'ri frontend manzili bilan sozlangan\n"
        "• API manzili .env orqali sozlangan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "React, django-cors-headers, fetch API",
    "task_deadline_days": 5,
}


L4_TEXT = """\
<h2>4-bosqich: Autentifikatsiya — token Django'da, React'da ishlatish</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /api/login/"] --> TOKEN["Token modelida yozuv yaratiladi"]
    TOKEN --> REACT["React token'ni saqlaydi"]
    REACT --> REQ["Har so'rovga Authorization: Token xxx qo'shiladi"]
    REQ --> CHECK{"Token.objects.get(key=...) muvaffaqiyatlimi?"}
    CHECK -->|DoesNotExist ushlanmasa| CRASH["500 Internal Server Error"]
    CHECK -->|to'g'ri ushlansa| OK["401 yoki foydalanuvchi aniqlanadi"]
</pre>

<p>StudyMate'da React alohida frontend bo'lgani uchun, Django'ning odatiy session-based autentifikatsiyasi (Django Asoslari kursidagi <code>login()</code>) to'g'ridan-to'g'ri ishlamaydi — React'ga <strong>token-based</strong> autentifikatsiya kerak. Bu darsda buni <strong>o'zimiz</strong> quramiz (DRF'siz, plain Django bilan).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Token modeli va login endpoint'i</h4>
<pre><code># studymate/models.py
import secrets
from django.db import models
from django.contrib.auth.models import User

class Token(models.Model):
    key = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def yaratish(user):
        key = secrets.token_hex(20)                  # ❗ 40 belgili tasodifiy, xavfsiz token
        return Token.objects.create(key=key, user=user)

# studymate/views.py
from django.contrib.auth import authenticate
from django.http import JsonResponse
import json

@csrf_exempt
def login_view(request):
    ma_lumot = json.loads(request.body)
    user = authenticate(username=ma_lumot["email"], password=ma_lumot["parol"])
    if user is None:
        return JsonResponse({"xato": "Email yoki parol noto'g'ri"}, status=401)

    token, _ = Token.objects.get_or_create(user=user, defaults={"key": secrets.token_hex(20)})
    return JsonResponse({"token": token.key, "ism": user.first_name})</code></pre>

<h4>BLOKA 2 — himoyalangan view uchun dekorator</h4>
<pre><code># studymate/auth_utils.py
from functools import wraps
from django.http import JsonResponse
from .models import Token

def token_talab_qilish(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Token "):
            return JsonResponse({"xato": "Token yo'q"}, status=401)

        key = auth_header.split(" ")[1]
        try:
            token = Token.objects.get(key=key)         # ❗ DoesNotExist ko'tarilishi MUMKIN
        except Token.DoesNotExist:
            return JsonResponse({"xato": "Token yaroqsiz"}, status=401)

        request.user = token.user                        # ❗ keyingi view uchun user'ni beradi
        return view_func(request, *args, **kwargs)
    return wrapper

# studymate/views.py
@token_talab_qilish
def topshiriqlar_view(request):
    topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
    # ...</code></pre>

<h4>BLOKA 3 — React: tokenni saqlash va yuborish</h4>
<pre><code>// frontend/src/api/auth.js
export async function kirish(email, parol) {
  const javob = await fetch(`${API_URL}/api/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, parol }),
  });
  const data = await javob.json();
  localStorage.setItem('token', data.token);
  return data;
}

// frontend/src/api/topshiriqlar.js - himoyalangan so'rov
export async function topshiriqlarniOlish() {
  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`, {
    headers: { Authorization: `Token ${token}` },      // ❗ "Bearer" emas, "Token" prefiksi
  });
  return await javob.json();
}</code></pre>

<h3>🐛 Ataylab xato — Token.DoesNotExist'ni ushlamaslik</h3>
<pre><code>def token_talab_qilish_xato(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        key = auth_header.split(" ")[1]
        token = Token.objects.get(key=key)   # ❌ try/except YO'Q!
        request.user = token.user
        return view_func(request, *args, **kwargs)
    return wrapper

# Agar noto'g'ri yoki eskirgan token yuborilsa:
# ❌ Django Token.DoesNotExist xatosini ko'taradi, u ushlanmagani uchun
#    500 Internal Server Error qaytadi (401 o'rniga)!</code></pre>

<p><strong>Natija:</strong> Django ORM'da <code>.get()</code> metodi, agar mos yozuv <strong>topilmasa</strong>, <code>Model.DoesNotExist</code> istisnosini <strong>ko'taradi</strong> (Django Asoslari kursidagi 4-darsni eslang). Agar bu istisno <code>try/except</code> bilan <strong>qo'lda ushlanmasa</strong>, u dasturning yuqori darajasigacha "ko'tarilib" ketadi va Django buni <strong>500 Internal Server Error</strong> deb qaytaradi — bu foydalanuvchiga (yoki React kodiga) "token noto'g'ri" (401) o'rniga tushunarsiz server xatosi ko'rsatadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega Django'ning odatiy session autentifikatsiyasi bu yerda ishlatilmaydi?</h4>
<p>Session autentifikatsiya brauzer cookie'siga tayanadi, va u odatda <strong>bir xil domendagi</strong> server-render qilingan sahifalar uchun mo'ljallangan. React <strong>alohida</strong> frontend bo'lgani va turli portda/domenda ishlagani uchun, token-based autentifikatsiya (har so'rovda aniq <code>Authorization</code> header yuborish) ancha mos yechim.</p>

<h4>2. <code>secrets.token_hex(20)</code> nima uchun ishlatiladi?</h4>
<p><code>secrets</code> moduli kriptografik jihatdan xavfsiz tasodifiy qiymatlar yaratadi (oddiy <code>random</code> modulidan farqli). Token — foydalanuvchini "tanib olish" uchun ishlatilgani sababli, u <strong>taxmin qilib bo'lmaydigan</strong> bo'lishi shart.</p>

<h4>3. Dekorator (<code>token_talab_qilish</code>) nima qiladi?</h4>
<p>Bu — 1-darsdagi (Ilg'or Mavzular kursi) dekorator naqshining amaliy qo'llanilishi: view funksiyasini "o'rab", <code>Authorization</code> header'ni tekshiradi, token'ni bazadan qidiradi, va agar to'g'ri bo'lsa <code>request.user</code>ni belgilab, asl view'ga o'tkazadi.</p>

<h4>4. Nega <code>Token.DoesNotExist</code>ni ushlash shart?</h4>
<p>Foydalanuvchi (yoki hujumchi) <strong>istalgan</strong> noto'g'ri token yuborishi mumkin — bu <strong>normal, kutilgan</strong> holat, xato emas. <code>try/except Token.DoesNotExist</code> bu holatni <strong>nazorat qilingan</strong> tarzda (401 bilan) boshqarish imkonini beradi, aks holda Django buni kutilmagan server xatosi (500) deb hisoblaydi.</p>

<h4>5. "Token xxx" va "Bearer xxx" orasidagi farq nima?</h4>
<p>Bular shunchaki <strong>konventsiya</strong> — <code>Authorization</code> header'ining formati <code>&lt;sxema&gt; &lt;qiymat&gt;</code> ko'rinishida bo'ladi. JWT uchun odatda <code>Bearer</code> ishlatiladi, hand-rolled token tizimlarida esa ko'pincha <code>Token</code> prefiksi ishlatiladi (Django REST Framework'ning o'zi ham shu konventsiyani ishlatadi). Muhimi — backend va frontend <strong>bir xil</strong> prefiksni kutishi va yuborishi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Token-based autentifikatsiya — alohida frontend (React) uchun session'dan ko'ra mosroq</li>
<li>✅ <code>secrets.token_hex()</code> — kriptografik xavfsiz, taxmin qilib bo'lmaydigan token yaratadi</li>
<li>✅ Dekorator orqali himoyalangan view'larni yozish — 1-darsdagi (Ilg'or Mavzular) naqshning amaliy qo'llanilishi</li>
<li>✅ Django ORM'ning <code>.get()</code> metodi topilmasa <code>DoesNotExist</code> ko'taradi — bu <strong>ushlanishi shart</strong></li>
<li>✅ <code>Authorization</code> header formati: <code>&lt;sxema&gt; &lt;qiymat&gt;</code>, backend/frontend bir xil sxemani kutishi kerak</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 4-BOSQICH: Autentifikatsiya - token Django'da, React'da ishlatish
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/models.py - Token modeli
# ─────────────────────────────────────────────────────────────────────

import secrets
from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    key = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def yaratish(user):
        key = secrets.token_hex(20)
        return Token.objects.create(key=key, user=user)

# ─────────────────────────────────────────────────────────────────────
# 2) studymate/views.py - login
# ─────────────────────────────────────────────────────────────────────

import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login_view(request):
    ma_lumot = json.loads(request.body)
    user = authenticate(username=ma_lumot["email"], password=ma_lumot["parol"])
    if user is None:
        return JsonResponse({"xato": "Email yoki parol noto'g'ri"}, status=401)

    token, _ = Token.objects.get_or_create(user=user, defaults={"key": secrets.token_hex(20)})
    return JsonResponse({"token": token.key, "ism": user.first_name})

# ─────────────────────────────────────────────────────────────────────
# 3) studymate/auth_utils.py - himoyalangan view dekoratori
# ─────────────────────────────────────────────────────────────────────

from functools import wraps


def token_talab_qilish(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Token "):
            return JsonResponse({"xato": "Token yo'q"}, status=401)

        key = auth_header.split(" ")[1]
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            return JsonResponse({"xato": "Token yaroqsiz"}, status=401)

        request.user = token.user
        return view_func(request, *args, **kwargs)
    return wrapper

# ─────────────────────────────────────────────────────────────────────
# 4) frontend/src/api/auth.js (izohda - JS)
# ─────────────────────────────────────────────────────────────────────

# export async function kirish(email, parol) {
#   const javob = await fetch(`${API_URL}/api/login/`, {
#     method: 'POST',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify({ email, parol }),
#   });
#   const data = await javob.json();
#   localStorage.setItem('token', data.token);
#   return data;
# }
#
# export async function topshiriqlarniOlish() {
#   const token = localStorage.getItem('token');
#   const javob = await fetch(`${API_URL}/api/topshiriqlar/`, {
#     headers: { Authorization: `Token ${token}` },
#   });
#   return await javob.json();
# }

# ─────────────────────────────────────────────────────────────────────
# 5) Ataylab xato - Token.DoesNotExist'ni ushlamaslik (izohda)
# ─────────────────────────────────────────────────────────────────────

# def token_talab_qilish_xato(view_func):
#     def wrapper(request, *args, **kwargs):
#         auth_header = request.headers.get("Authorization", "")
#         key = auth_header.split(" ")[1]
#         token = Token.objects.get(key=key)   # try/except YO'Q!
#         request.user = token.user
#         return view_func(request, *args, **kwargs)
#     return wrapper
# ❌ Noto'g'ri token -> Token.DoesNotExist -> 500 Internal Server Error
"""

L4_EX = [
    {
        "title": "Nega token-based autentifikatsiya ishlatiladi?",
        "description": "StudyMate'da nega Django'ning odatiy session autentifikatsiyasi o'rniga token-based autentifikatsiya ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki session autentifikatsiya Django'da mavjud emas",
            "React alohida frontend bo'lgani uchun, har so'rovda aniq token yuborish ko'proq mos keladi",
            "Chunki token har doim tezroq ishlaydi",
            "Bu ixtiyoriy, ahamiyati yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Session cookie'ga, token esa har bir so'rovga tayanadi.",
        "explanation": "React alohida frontend (boshqa port/domenda) bo'lgani uchun, brauzer cookie'siga tayanadigan session autentifikatsiya o'rniga, har so'rovda aniq yuboriladigan token-based autentifikatsiya ko'proq mos keladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "secrets moduli nima uchun ishlatiladi?",
        "description": "Token yaratishda oddiy random modul o'rniga secrets moduli nega ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki secrets tezroq ishlaydi",
            "secrets kriptografik jihatdan xavfsiz, taxmin qilib bo'lmaydigan qiymatlar yaratadi",
            "Chunki random moduli import qilinmaydi",
            "Ular bir xil, farqi yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Token foydalanuvchini \"tanib olish\" uchun ishlatiladi - u taxmin qilinishi xavfli.",
        "explanation": "secrets moduli kriptografik jihatdan xavfsiz, taxmin qilib bo'lmaydigan tasodifiy qiymatlar yaratadi, bu autentifikatsiya token'lari uchun zarur.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Himoyalangan so'rov jarayonini tartiblang",
        "description": "React'dan Authorization header bilan so'rov kelganda, token_talab_qilish dekoratori ichidagi jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Authorization header'dan 'Token ' prefiksidan keyingi qism ajratib olinadi",
            "Token.objects.get(key=...) orqali bazadan qidiriladi",
            "Agar topilsa, request.user = token.user belgilanadi",
            "Asl view funksiyasi (masalan topshiriqlar_view) chaqiriladi",
        ],
        "correct_order": [
            "Authorization header'dan 'Token ' prefiksidan keyingi qism ajratib olinadi",
            "Token.objects.get(key=...) orqali bazadan qidiriladi",
            "Agar topilsa, request.user = token.user belgilanadi",
            "Asl view funksiyasi (masalan topshiriqlar_view) chaqiriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Model.objects.get() topilmasa qanday istisno ko'taradi?",
        "description": "Django ORM'da .get() metodi mos yozuv topilmasa qaysi istisnoni ko'taradi? (masalan: DoesNotExist)",
        "exercise_type": "text_input",
        "expected_answer": "DoesNotExist",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega Token.DoesNotExist'ni ushlamaslik 500 xato beradi?",
        "description": (
            "token_talab_qilish_xato() dekoratorida try/except "
            "ishlatilmasdan Token.objects.get(key=key) chaqirilsa, va "
            "noto'g'ri token yuborilsa, nega bu 401 o'rniga 500 Internal "
            "Server Error bilan tugaydi? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django ORM'da .get() metodi, agar berilgan shartga mos "
            "yozuv umuman topilmasa, Model.DoesNotExist istisnosini "
            "ko'taradi (bu Django Asoslari kursida ham ko'rilgan xatti-"
            "harakat). Agar bu istisno try/except bilan qo'lda "
            "ushlanmasa, u view funksiyasidan \"chiqib\", Django'ning "
            "umumiy xato boshqaruv mexanizmigacha ko'tariladi, va Django "
            "buni kutilmagan, boshqarilmagan xato deb hisoblab, 500 "
            "Internal Server Error qaytaradi. Noto'g'ri token yuborish "
            "esa aslida oddiy, kutilishi mumkin bo'lgan holat (401 "
            "bo'lishi kerak edi) — lekin istisno ushlanmagani uchun u "
            "server xatosi sifatida ko'rinadi."
        ),
        "hint": "Django ORM'ning .get() metodi topilmasa nima qiladi, va bu \"xato\" qo'lda ushlanmasa nima bo'ladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L4_TASK = {
    "task_title": "StudyMate — token-based autentifikatsiya",
    "task_description": (
        "Django'da Token modeli va login endpoint'ini yarating. "
        "token_talab_qilish dekoratorini yozing va uni topshiriqlar_view'ga "
        "qo'llang. Token.DoesNotExist'ni to'g'ri ushlang. Frontend'da login "
        "formasi va tokenni har bir himoyalangan so'rovga qo'shishni "
        "amalga oshiring."
    ),
    "task_requirements": (
        "• Token modeli (key, user) yaratilgan va migratsiya qilingan\n"
        "• POST /api/login/ — authenticate() orqali tekshiradi, token qaytaradi\n"
        "• token_talab_qilish dekoratori — Authorization header'ni tekshiradi\n"
        "• Token.DoesNotExist try/except bilan to'g'ri ushlanadi (401 qaytaradi, 500 emas)\n"
        "• GET /api/topshiriqlar/ — faqat request.user'ga tegishli topshiriqlarni qaytaradi\n"
        "• Frontend: login formasi, token localStorage'da saqlanadi va har so'rovga qo'shiladi\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Django, secrets moduli, React",
    "task_deadline_days": 4,
}


L5_TEXT = """\
<h2>5-bosqich: Telegram bot — hisobni bog'lash va Django bazasidan o'qish</h2>

<pre class="mermaid">
flowchart LR
    BOTFILE["telegram_bot/bot.py"] -->|django.setup()| ORM["Django ORM ishga tayyor"]
    ORM --> MODELS["from studymate.models import ..."]
    USER["Foydalanuvchi web'da link_kodi oladi"] --> LINK["/link kod - botga yuboriladi"]
    LINK --> DB["telegram_chat_id users jadvalida yoziladi"]
    DB --> CMD["/topshiriqlar - bot SHU jadvaldan o'qiydi"]
</pre>

<p>Bu — kursning <strong>markaziy</strong> bosqichi: Telegram Bot aiogram kursida o'rgangan bilim endi Django'ning <strong>xuddi shu</strong> ma'lumotlar bazasi bilan ishlaydi. Bot alohida loyiha emas — u StudyMate'ning <strong>uchinchi interfeysi</strong>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Profile modeli: telegram maydonlarini User'ga qo'shish</h4>
<pre><code># studymate/models.py
# ❗ Django'ning tayyor User modeliga to'g'ridan-to'g'ri yangi maydon
#   qo'shib bo'lmaydi - shuning uchun OneToOne orqali "Profile" bilan kengaytiramiz
#   (1-darsdagi "users" jadvalidagi telegram_chat_id/link_kodi shu yerda joylashadi)

from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    link_kodi = models.CharField(max_length=10, null=True, blank=True)</code></pre>

<h4>BLOKA 2 — botga Django ORM'ni "ulash" (django.setup())</h4>
<pre><code># telegram_bot/bot.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")   # ❗ qaysi sozlamalarni ishlatishni ko'rsatadi
django.setup()                                                            # ❗ MAJBURIY - Django ilovalarini yuklaydi

# ❗ django.setup()DAN KEYIN import qilinishi SHART - aks holda Django hali tayyor emas!
from studymate.models import Fan, Topshiriq, Profile
from django.contrib.auth.models import User

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()</code></pre>

<h4>BLOKA 3 — /link buyrug'i: hisoblarni bog'lash</h4>
<pre><code>@dp.message(Command("link"))
async def link_handler(message: types.Message):
    qismlar = message.text.split()
    if len(qismlar) != 2:
        await message.answer("Foydalanish: /link KOD")
        return

    kod = qismlar[1]
    try:
        user = await User.objects.aget(profile__link_kodi=kod)   # ❗ aget() - async Django ORM (4.1+)
    except User.DoesNotExist:
        await message.answer("Kod noto'g'ri yoki eskirgan")
        return

    user.profile.telegram_chat_id = message.chat.id    # ❗ web sayt yaratgan foydalanuvchiga bog'lanadi
    user.profile.link_kodi = None                       # ❗ kod bir martalik - ishlatilgandan keyin tozalanadi
    await user.profile.asave()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.first_name}!")</code></pre>

<h4>BLOKA 4 — /topshiriqlar buyrug'i: WEB'DA yaratilgan ma'lumotni bot orqali ko'rsatish</h4>
<pre><code>@dp.message(Command("topshiriqlar"))
async def topshiriqlar_handler(message: types.Message):
    try:
        user = await User.objects.aget(profile__telegram_chat_id=message.chat.id)
    except User.DoesNotExist:
        await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
        return

    topshiriqlar = [t async for t in Topshiriq.objects.filter(
        user=user, bajarilgan=False
    ).select_related('fan')]

    if not topshiriqlar:
        await message.answer("Bajarilmagan topshiriqlar yo'q 🎉")
        return

    matn = "\\n".join(f"📌 {t.sarlavha} ({t.fan.nomi}) — {t.muddat_vaqti:%d.%m %H:%M}" for t in topshiriqlar)
    await message.answer(matn)</code></pre>

<h3>🐛 Ataylab xato — django.setup()dan OLDIN modellarni import qilish</h3>
<pre><code># telegram_bot/bot.py
from studymate.models import Fan, Topshiriq   # ❌ django.setup()DAN OLDIN import qilingan!

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
django.setup()

# Botni ishga tushirishga urinilganda:
# ❌ django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.</code></pre>

<p><strong>Natija:</strong> Django modellari (<code>Fan</code>, <code>Topshiriq</code> va h.k.) ishlashi uchun, Django avval <strong>barcha ilovalarini</strong> (<code>INSTALLED_APPS</code>) yuklab, ichki "registry"ni tayyorlashi kerak — buni <code>django.setup()</code> bajaradi. Agar model'lar <code>django.setup()</code> chaqirilishidan <strong>oldin</strong> import qilinsa, Django hali "tayyor emas" bo'lgani uchun <code>AppRegistryNotReady</code> xatosini beradi. <strong>Qat'iy tartib</strong>: avval <code>os.environ.setdefault(...)</code> va <code>django.setup()</code>, <strong>faqat shundan keyin</strong> model import qilish mumkin.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega botga django.setup() kerak?</h4>
<p>Odatda Django modellari faqat Django serverining o'zi ichida (<code>manage.py runserver</code> orqali) ishlatiladi, u paytda Django avtomatik "sozlanadi". Bot esa <strong>butunlay alohida</strong> Python skripti — u Django serverining bir qismi emas. <code>django.setup()</code> shu alohida skriptga Django ORM'dan <strong>xuddi Django serveridagidek</strong> foydalanish imkonini beradi.</p>

<h4>2. link_kodi nega bir martalik (bitta ishlatilgandan keyin tozalanadi)?</h4>
<p>Agar <code>link_kodi</code> ishlatilgandan keyin ham bazada qolib ketsa, kimdir bu kodni <strong>qayta</strong> ishlatib, boshqa birovning hisobiga "bog'lanishi" mumkin bo'lardi (agar u kodni bilib qolsa). Kodni ishlatilgandan keyin darhol <code>None</code>ga o'rnatish — bu xavfsizlik riskini yo'q qiladi.</p>

<h4>3. Nega bot Django ORM'ni to'g'ridan-to'g'ri ishlatadi, alohida HTTP so'rov yubormaydi?</h4>
<p>Bot va Django backend <strong>bir xil</strong> serverda (yoki hech bo'lmaganda bir xil bazaga kirish huquqiga ega muhitda) ishlaydi deb faraz qilinadi. Django ORM'ni to'g'ridan-to'g'ri ishlatish, HTTP orqali o'z-o'ziga so'rov yuborishdan (backend'ning o'ziga API chaqiruvi qilish) ancha samarali va oddiy.</p>

<h4>4. <code>aget()</code>/<code>asave()</code> nima va nega ishlatiladi?</h4>
<p>aiogram — <strong>async</strong> kutubxona (7-darsda, Ilg'or Mavzular kursida <code>asyncio</code>ni ko'rgansiz). Django 4.1 versiyasidan boshlab ORM'ning <strong>async versiyalari</strong> (<code>aget</code>, <code>asave</code>, <code>acreate</code> va h.k.) mavjud — bular oddiy <code>get()</code>/<code>save()</code>ning <code>await</code> bilan ishlaydigan versiyasi, aiogram'ning async handler'lari ichida to'g'ri ishlashi uchun zarur.</p>

<h4>5. Nega django.setup() import'lardan OLDIN emas, DARHOL keyin bo'lishi shart?</h4>
<p>Python fayllarni yuqoridan pastga qarab bajaradi. Agar <code>from studymate.models import ...</code> qatori <code>django.setup()</code>dan <strong>oldin</strong> yozilsa, Python bu qatorga yetganda Django hali "ilovalarni ro'yxatdan o'tkazmagan" bo'ladi, va model import qilishga urinish <code>AppRegistryNotReady</code> xatosiga olib keladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>django.setup()</code> — Django ORM'ni Django serveridan tashqarida (masalan botda) ishlatish uchun MAJBURIY, import'lardan oldin chaqiriladi</li>
<li>✅ <code>link_kodi</code> — bir martalik, ishlatilgandan keyin darhol tozalanadigan bog'lash kodi</li>
<li>✅ Bot Django ORM'ni to'g'ridan-to'g'ri ishlatadi — alohida HTTP so'rov yubormaydi</li>
<li>✅ <code>aget()</code>/<code>asave()</code> — Django ORM'ning async handler'lar ichida ishlatiladigan versiyalari</li>
<li>✅ <code>django.setup()</code> import'lardan OLDIN emas, DARHOL keyin (lekin model import'laridan oldin) chaqirilishi shart</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 5-BOSQICH: Telegram bot - hisobni bog'lash va buyruqlar
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 0) studymate/models.py - Profile modeli (telegram maydonlari uchun)
# ─────────────────────────────────────────────────────────────────────

# from django.db import models
# from django.contrib.auth.models import User
#
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     telegram_chat_id = models.BigIntegerField(null=True, blank=True)
#     link_kodi = models.CharField(max_length=10, null=True, blank=True)

# ─────────────────────────────────────────────────────────────────────
# 1) telegram_bot/bot.py - django.setup()
# ─────────────────────────────────────────────────────────────────────

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
django.setup()

from studymate.models import Fan, Topshiriq, Profile
from django.contrib.auth.models import User

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
    try:
        user = await User.objects.aget(profile__link_kodi=kod)
    except User.DoesNotExist:
        await message.answer("Kod noto'g'ri yoki eskirgan")
        return

    user.profile.telegram_chat_id = message.chat.id
    user.profile.link_kodi = None
    await user.profile.asave()

    await message.answer(f"✅ Hisobingiz bog'landi, {user.first_name}!")


@dp.message(Command("topshiriqlar"))
async def topshiriqlar_handler(message: types.Message):
    try:
        user = await User.objects.aget(profile__telegram_chat_id=message.chat.id)
    except User.DoesNotExist:
        await message.answer("Avval /link buyrug'i bilan hisobingizni bog'lang")
        return

    topshiriqlar = [t async for t in Topshiriq.objects.filter(
        user=user, bajarilgan=False
    ).select_related('fan')]

    if not topshiriqlar:
        await message.answer("Bajarilmagan topshiriqlar yo'q 🎉")
        return

    matn = "\\n".join(f"📌 {t.sarlavha} ({t.fan.nomi}) — {t.muddat_vaqti:%d.%m %H:%M}" for t in topshiriqlar)
    await message.answer(matn)

# ─────────────────────────────────────────────────────────────────────
# Ataylab xato - django.setup()dan OLDIN import (izohda)
# ─────────────────────────────────────────────────────────────────────

# from studymate.models import Fan, Topshiriq   # django.setup()DAN OLDIN!
#
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studymate.settings")
# django.setup()
# ❌ django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
"""

L5_EX = [
    {
        "title": "django.setup() nima uchun kerak?",
        "description": "Telegram bot skriptida django.setup() chaqirilishining asosiy sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Botni tezroq ishga tushirish uchun",
            "Django ORM'ni Django serveridan tashqarida (alohida skriptda) ishlatish imkonini berish uchun",
            "Faqat xato xabarlarini o'chirish uchun",
            "Bu ixtiyoriy, hech qanday amaliy ta'siri yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bot Django serverining bir qismi emas, alohida skript.",
        "explanation": "django.setup() Django'ning ilovalarini yuklab, ichki \"registry\"ni tayyorlaydi — bu Django ORM'ni Django serveridan tashqarida (masalan botda) ishlatish uchun zarur.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "link_kodi nega ishlatilgandan keyin tozalanadi?",
        "description": "/link buyrug'i ishlatilgandan keyin nega user.profile.link_kodi darhol None qilinadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumotlar bazasida joy tejash uchun",
            "Kodni takror ishlatib, boshqa birovga \"bog'lanib\" qolishning oldini olish uchun",
            "Bu Django'ning majburiy talabi",
            "Faqat kodni chiroyliroq qilish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu xavfsizlik masalasi - kod \"bir martalik\" bo'lishi kerak.",
        "explanation": "Agar link_kodi ishlatilgandan keyin ham qolib ketsa, uni bilib qolgan har qanday kishi shu kod orqali qayta bog'lanib, boshqa birovning hisobiga kirishi mumkin bo'lardi — shuning uchun u ishlatilgandan keyin darhol tozalanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "/topshiriqlar buyrug'i ishlash jarayonini tartiblang",
        "description": "Foydalanuvchi botga /topshiriqlar buyrug'ini yuborganda ichki jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "message.chat.id orqali telegram_chat_id bo'yicha User qidiriladi",
            "Agar topilmasa, 'avval /link qiling' xabari yuboriladi",
            "Topilsa, Topshiriq.objects.filter(user=..., bajarilgan=False) orqali ma'lumot olinadi",
            "Ro'yxat matn shaklida formatlanib, foydalanuvchiga yuboriladi",
        ],
        "correct_order": [
            "message.chat.id orqali telegram_chat_id bo'yicha User qidiriladi",
            "Agar topilmasa, 'avval /link qiling' xabari yuboriladi",
            "Topilsa, Topshiriq.objects.filter(user=..., bajarilgan=False) orqali ma'lumot olinadi",
            "Ro'yxat matn shaklida formatlanib, foydalanuvchiga yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Django ORM'ning async metod versiyasi",
        "description": "Django 4.1+ da oddiy get() metodining aiogram handler'lari ichida ishlatsa bo'ladigan async versiyasi qanday nomlanadi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "aget",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega modellarni django.setup()dan oldin import qilish xato beradi?",
        "description": (
            "Agar telegram_bot/bot.py faylida from studymate.models "
            "import ... qatori django.setup() chaqirilishidan OLDIN "
            "yozilsa, nega \"AppRegistryNotReady: Apps aren't loaded "
            "yet\" xatosi chiqadi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django modellari ishlashi uchun, Django avval o'zining "
            "barcha ilovalarini (INSTALLED_APPS) yuklab, ichki "
            "\"registry\"sini tayyorlashi shart — aynan shu vazifani "
            "django.setup() bajaradi. Python fayllarni yuqoridan pastga "
            "qarab bajaradi, shuning uchun agar model import qiluvchi "
            "qator django.setup() chaqirilishidan oldin yozilgan bo'lsa, "
            "Python bu qatorga yetganda Django hali \"tayyor emas\" "
            "(ilovalar hali ro'yxatdan o'tkazilmagan) bo'ladi. Shu "
            "sababli Django modelni import qilishga urinishni xavfsiz "
            "emas deb hisoblab, AppRegistryNotReady xatosini beradi."
        ),
        "hint": "Python kodni qanday tartibda bajaradi, va Django modellari ishlashi uchun avval nima tayyor bo'lishi kerak?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L5_TASK = {
    "task_title": "StudyMate — Telegram bot: bog'lash va buyruqlar",
    "task_description": (
        "telegram_bot/bot.py yarating, unda django.setup() orqali Django "
        "ORM'ga ulaning. /link KOD buyrug'i orqali hisob bog'lashni, "
        "/topshiriqlar buyrug'i orqali esa web saytda yaratilgan "
        "topshiriqlarni bot orqali ko'rsatishni amalga oshiring."
    ),
    "task_requirements": (
        "• Profile modeli (user, telegram_chat_id, link_kodi) yaratilgan va migratsiya qilingan\n"
        "• telegram_bot/bot.py — django.setup() import'lardan OLDIN, "
        "model import'laridan KEYIN to'g'ri chaqirilgan\n"
        "• /link KOD — link_kodi bo'yicha foydalanuvchini topib, "
        "telegram_chat_id'ni yozadi, link_kodi'ni None qiladi\n"
        "• /topshiriqlar — telegram_chat_id orqali foydalanuvchini "
        "aniqlab, uning bajarilmagan topshiriqlarini ko'rsatadi\n"
        "• Bog'lanmagan foydalanuvchi uchun tushunarli xabar chiqadi\n"
        "• Bot va Django backend BIR XIL PostgreSQL bazasiga ulangan "
        "(alohida SQLite emas)\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "aiogram, Django ORM, PostgreSQL",
    "task_deadline_days": 5,
}


L6_TEXT = """\
<h2>6-bosqich: Avtomatik bildirishnomalar — muddat yaqinlashganda eslatish</h2>

<pre class="mermaid">
flowchart LR
    CRON["cron: har soatda ishga tushadi"] --> CMD["manage.py send_reminders"]
    CMD --> QUERY["muddati 24 soat ichida, bajarilmagan topshiriqlar"]
    QUERY --> FILTER{"telegram_chat_id bormi?"}
    FILTER -->|yo'q| SKIP["o'tkazib yuboriladi"]
    FILTER -->|bor| SEND["Telegram Bot API orqali xabar yuboriladi"]
</pre>

<p>StudyMate'ning "sehri" shu yerda: foydalanuvchi web saytga <strong>kirmasa ham</strong>, muddati yaqinlashgan topshiriq haqida Telegram orqali <strong>avtomatik</strong> xabar oladi. Buning uchun <strong>alohida, rejalashtirilgan</strong> jarayon (Django management command) yaratamiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Django management command yaratish</h4>
<pre><code># studymate/management/commands/send_reminders.py
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from studymate.models import Topshiriq

class Command(BaseCommand):                      # ❗ Django'ning "python manage.py X" naqshi
    help = "Muddati yaqinlashgan topshiriqlar uchun Telegram orqali eslatma yuboradi"

    def handle(self, *args, **options):
        hozir = timezone.now()
        chegara = hozir + timedelta(hours=24)

        topshiriqlar = Topshiriq.objects.filter(
            bajarilgan=False,
            muddat_vaqti__gte=hozir,
            muddat_vaqti__lte=chegara,
        ).exclude(
            user__profile__telegram_chat_id__isnull=True   # ❗ bog'lanmagan foydalanuvchilarni chiqarib tashlaydi
        ).select_related('user__profile', 'fan')

        for t in topshiriqlar:
            self.xabar_yuborish(t)

    def xabar_yuborish(self, topshiriq):
        chat_id = topshiriq.user.profile.telegram_chat_id
        matn = f"⏰ Eslatma: '{topshiriq.sarlavha}' ({topshiriq.fan.nomi}) muddati yaqinlashmoqda!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": matn},
        )</code></pre>

<h4>BLOKA 2 — nega bu alohida jarayon (aiogram Dispatcher emas)?</h4>
<pre><code># aiogram'ning Dispatcher'i - foydalanuvchi BUYRUQ yuborganda ishlaydi (reaktiv)
# send_reminders esa - VAQT bo'yicha, hech kim so'ramasa ham ishga tushishi kerak (proaktiv)

# Shuning uchun ikkita alohida jarayon:
# 1. telegram_bot/bot.py (aiogram, doim ishlab turadi, buyruqlarga javob beradi)
# 2. send_reminders komandasi (vaqti-vaqti bilan, cron orqali ishga tushadi)

# Ikkalasi ham Telegram Bot API'ga to'g'ridan-to'g'ri (yoki aiogram orqali) so'rov yuborishi mumkin -
# lekin send_reminders ODDIY requests kutubxonasi bilan ham yozilishi mumkin,
# chunki unga foydalanuvchi xabarini "kutish" shart emas.</code></pre>

<h4>BLOKA 3 — cron orqali rejalashtirish</h4>
<pre><code># Deploy qilingan serverda crontab -e orqali:
# Har soatda ishga tushirish:
0 * * * * cd /path/to/django_backend && python manage.py send_reminders</code></pre>

<h3>🐛 Ataylab xato — bog'lanmagan foydalanuvchilarni filtrlashni unutish</h3>
<pre><code>def handle_xato(self, *args, **options):
    topshiriqlar = Topshiriq.objects.filter(
        bajarilgan=False,
        muddat_vaqti__lte=timezone.now() + timedelta(hours=24),
    ).select_related('user__profile', 'fan')   # ❌ .exclude(...) YO'Q!

    for t in topshiriqlar:
        chat_id = t.user.profile.telegram_chat_id   # ❗ bu None bo'lishi mumkin!
        requests.post(url, json={"chat_id": chat_id, "text": "..."})
        # ❌ Telegram API "chat_id topilmadi" xatosini qaytaradi,
        #    yoki dastur None bilan ishlashga urinib xato beradi</code></pre>

<p><strong>Natija:</strong> <strong>hamma</strong> foydalanuvchi Telegram akkauntini <strong>bog'lamagan</strong> bo'lishi mumkin — bunday foydalanuvchilarning <code>telegram_chat_id</code>si <code>None</code>. Agar filtrlashda bu holat <strong>hisobga olinmasa</strong>, kod <code>None</code> qiymatni haqiqiy chat ID sifatida Telegram API'ga yuborishga urinadi — bu <strong>muvaffaqiyatsiz</strong> so'rovlarga (yoki ba'zi hollarda dastur xatosiga) olib keladi. <code>.exclude(user__profile__telegram_chat_id__isnull=True)</code> bunday foydalanuvchilarni so'rov natijasidan <strong>oldindan chiqarib tashlaydi</strong>.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega bu alohida Django management command sifatida yozilgan?</h4>
<p>Django management command'lar (<code>python manage.py X</code>) — Django loyihasida <strong>bir martalik yoki rejalashtirilgan</strong> vazifalarni bajarish uchun standart usul. Bu vazifa foydalanuvchi so'roviga bog'liq emas — u <strong>vaqt</strong> bo'yicha (masalan har soatda) ishga tushishi kerak, shuning uchun oddiy view emas, alohida command sifatida yoziladi.</p>

<h4>2. Nega bu aiogram Dispatcher'idan alohida?</h4>
<p>aiogram'ning <code>Dispatcher</code>i — <strong>reaktiv</strong>: foydalanuvchi buyruq yuborganda ishga tushadi. Bildirishnomalar esa <strong>proaktiv</strong> bo'lishi kerak — hech kim so'ramasa ham, vaqt kelganda avtomatik yuborilishi kerak. Bular ikki xil "trigger" turi, shuning uchun ikkita alohida jarayon.</p>

<h4>3. Nega <code>requests</code> kutubxonasi ishlatiladi, aiogram emas?</h4>
<p><code>send_reminders</code> bitta martalik ishga tushadi va tugaydi — unga aiogram'ning doimiy ishlaydigan, foydalanuvchi xabarini "kutuvchi" murakkab tizimi shart emas. Telegram'ning oddiy HTTP API'siga to'g'ridan-to'g'ri <code>requests.post()</code> yuborish yetarli va soddaroq.</p>

<h4>4. <code>.exclude(user__profile__telegram_chat_id__isnull=True)</code> qanday ishlaydi?</h4>
<p>Bu — Django ORM'ning bog'langan jadval orqali filtrlash usuli (7-darsdagi <code>filter(bog'lanish__maydon=...)</code>ni eslang). U <code>Topshiriq</code>dan <code>user</code>ga, undan <code>profile</code>ga o'tib, <code>telegram_chat_id</code> <code>NULL</code> bo'lgan yozuvlarni natijadan <strong>chiqarib tashlaydi</strong>.</p>

<h4>5. Nega bog'lanmagan foydalanuvchini filtrlamaslik xavfli?</h4>
<p><code>None</code> qiymatni haqiqiy Telegram chat ID sifatida yuborish <strong>ma'nosiz</strong> so'rov hisoblanadi — Telegram API buni rad etadi. Bundan tashqari, katta hajmdagi ma'lumotlarda bunday "behuda" so'rovlar ko'payib, tizimni sekinlashtirishi yoki keraksiz xato loglarini to'ldirishi mumkin.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Django management command — vaqt bo'yicha ishga tushadigan vazifalar uchun standart yechim</li>
<li>✅ Proaktiv (bildirishnoma) va reaktiv (buyruqqa javob) jarayonlar alohida quriladi</li>
<li>✅ Oddiy, bir martalik HTTP so'rovlar uchun <code>requests</code> aiogram'dan soddaroq</li>
<li>✅ <code>.exclude(bog'lanish__maydon__isnull=True)</code> — bog'lanmagan yozuvlarni oldindan chiqarib tashlaydi</li>
<li>✅ cron — bu kabi vazifalarni muntazam vaqt oralig'ida avtomatik ishga tushiradi</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 6-BOSQICH: Avtomatik bildirishnomalar
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/management/commands/send_reminders.py
# ─────────────────────────────────────────────────────────────────────

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from studymate.models import Topshiriq

BOT_TOKEN = "..."  # environment o'zgaruvchisidan olinadi


class Command(BaseCommand):
    help = "Muddati yaqinlashgan topshiriqlar uchun Telegram orqali eslatma yuboradi"

    def handle(self, *args, **options):
        hozir = timezone.now()
        chegara = hozir + timedelta(hours=24)

        topshiriqlar = Topshiriq.objects.filter(
            bajarilgan=False,
            muddat_vaqti__gte=hozir,
            muddat_vaqti__lte=chegara,
        ).exclude(
            user__profile__telegram_chat_id__isnull=True
        ).select_related('user__profile', 'fan')

        for t in topshiriqlar:
            self.xabar_yuborish(t)

    def xabar_yuborish(self, topshiriq):
        chat_id = topshiriq.user.profile.telegram_chat_id
        matn = f"⏰ Eslatma: '{topshiriq.sarlavha}' ({topshiriq.fan.nomi}) muddati yaqinlashmoqda!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": matn},
        )

# ─────────────────────────────────────────────────────────────────────
# 2) crontab (izohda - server sozlamasi, Python emas)
# ─────────────────────────────────────────────────────────────────────

# 0 * * * * cd /path/to/django_backend && python manage.py send_reminders

# ─────────────────────────────────────────────────────────────────────
# 3) Ataylab xato - filtrlashni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# def handle_xato(self, *args, **options):
#     topshiriqlar = Topshiriq.objects.filter(
#         bajarilgan=False,
#         muddat_vaqti__lte=timezone.now() + timedelta(hours=24),
#     ).select_related('user__profile', 'fan')   # .exclude(...) YO'Q!
#     for t in topshiriqlar:
#         chat_id = t.user.profile.telegram_chat_id   # None bo'lishi mumkin!
#         requests.post(url, json={"chat_id": chat_id, "text": "..."})
"""

L6_EX = [
    {
        "title": "Nega bildirishnoma alohida management command sifatida yozilgan?",
        "description": "send_reminders nega oddiy Django view emas, balki alohida management command (python manage.py X) sifatida yozilgan?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki view'lar faqat GET/POST so'rovlarni qabul qiladi, vaqt bo'yicha emas",
            "Chunki management command'lar tezroq ishlaydi",
            "Bu ikkalasi ham to'g'ri, farqi yo'q",
            "Chunki view'lar Django'da mavjud emas",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "View foydalanuvchi so'roviga javob beradi, bu vazifa esa vaqt bo'yicha ishga tushishi kerak.",
        "explanation": "View'lar HTTP so'rovlarga javob berish uchun mo'ljallangan, lekin bildirishnoma vazifasi hech qanday so'rovsiz, faqat vaqt bo'yicha (cron orqali) ishga tushishi kerak — bu uchun Django management command mos yechim.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega send_reminders uchun requests ishlatiladi, aiogram emas?",
        "description": "send_reminders komandasida Telegram'ga xabar yuborish uchun nega oddiy requests kutubxonasi ishlatilgan, aiogram Dispatcher emas?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki aiogram bilan xabar yuborib bo'lmaydi",
            "Command bir martalik ishga tushib tugaydi, unga aiogram'ning doimiy ishlaydigan tizimi shart emas",
            "requests har doim tezroq ishlaydi",
            "aiogram faqat buyruqlarni qabul qilish uchun, xabar yuborish uchun emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "aiogram Dispatcher doimiy ishlab, foydalanuvchi xabarlarini \"kutadi\" - bu yerda kerakmi?",
        "explanation": "send_reminders bir martalik ishga tushib, ishini tugatib chiqadi — unga aiogram'ning doimiy ishlab, foydalanuvchi buyruqlarini kutadigan murakkab tizimi kerak emas, oddiy HTTP so'rov (requests.post) yetarli.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "send_reminders ishlash jarayonini tartiblang",
        "description": "cron send_reminders komandasini ishga tushirganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "cron belgilangan vaqtda python manage.py send_reminders'ni ishga tushiradi",
            "Muddati 24 soat ichida, bajarilmagan topshiriqlar so'raladi",
            "Telegram akkaunti bog'lanmagan foydalanuvchilar exclude() bilan chiqarib tashlanadi",
            "Qolgan har bir topshiriq uchun Telegram Bot API'ga xabar yuboriladi",
        ],
        "correct_order": [
            "cron belgilangan vaqtda python manage.py send_reminders'ni ishga tushiradi",
            "Muddati 24 soat ichida, bajarilmagan topshiriqlar so'raladi",
            "Telegram akkaunti bog'lanmagan foydalanuvchilar exclude() bilan chiqarib tashlanadi",
            "Qolgan har bir topshiriq uchun Telegram Bot API'ga xabar yuboriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Vazifalarni muntazam vaqt oralig'ida ishga tushiruvchi vosita",
        "description": "Linux serverida bir vazifani (masalan har soatda) avtomatik, muntazam vaqt oralig'ida ishga tushirish uchun ishlatiladigan klassik vositani yozing.",
        "exercise_type": "text_input",
        "expected_answer": "cron",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega bog'lanmagan foydalanuvchilarni filtrlamaslik muammo tug'diradi?",
        "description": (
            ".exclude(user__profile__telegram_chat_id__isnull=True) "
            "ishlatilmasa, va Telegram akkauntini bog'lamagan "
            "foydalanuvchining topshirig'i ham natijaga kirsa, nima "
            "muammo yuzaga keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Telegram akkauntini bog'lamagan foydalanuvchining "
            "telegram_chat_id qiymati None bo'ladi. Agar bunday "
            "foydalanuvchilar natijadan oldindan chiqarib tashlanmasa, "
            "kod ularning None qiymatini haqiqiy Telegram chat ID "
            "sifatida requests.post() orqali Telegram Bot API'ga "
            "yuborishga urinadi. Bu so'rov Telegram tomonidan rad "
            "etiladi (chat_id topilmadi degan xato bilan), chunki None "
            "haqiqiy chat identifikatori emas. Bundan tashqari, ko'p "
            "sonli foydalanuvchida bunday behuda so'rovlar ko'payib, "
            "tizim resurslarini behuda sarflashi va keraksiz xato "
            "loglarini to'ldirishi mumkin."
        ),
        "hint": "Bog'lanmagan foydalanuvchida telegram_chat_id qanday qiymatga ega, va bu qiymatni Telegram API'ga yuborish nima bilan tugaydi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L6_TASK = {
    "task_title": "StudyMate — avtomatik Telegram bildirishnomalari",
    "task_description": (
        "send_reminders nomli Django management command yarating — u "
        "muddati 24 soat ichida bo'lgan, bajarilmagan topshiriqlarni topib, "
        "Telegram akkaunti bog'langan foydalanuvchilarga avtomatik eslatma "
        "yuboradi. Bog'lanmagan foydalanuvchilarni to'g'ri filtrlang."
    ),
    "task_requirements": (
        "• studymate/management/commands/send_reminders.py yaratilgan\n"
        "• Faqat muddati 24 soat ichida va bajarilmagan topshiriqlar tanlanadi\n"
        "• .exclude(...) orqali Telegram bog'lanmagan foydalanuvchilar chiqarib tashlanadi\n"
        "• Har bir mos topshiriq uchun Telegram Bot API'ga to'g'ri formatlangan xabar yuboriladi\n"
        "• Komanda cron orqali (yoki hech bo'lmasa qo'lda) muvaffaqiyatli ishga tushirilgani ko'rsatilgan\n"
        "• README.md holat checklist'i yangilangan"
    ),
    "task_technologies": "Django management commands, requests, Telegram Bot API, cron",
    "task_deadline_days": 4,
}


L7_TEXT = """\
<h2>7-bosqich (CAPSTONE yakuni): uchta qismni birga deploy qilish</h2>

<pre class="mermaid">
flowchart TB
    DJANGO["Django backend"] -->|"Web Service"| RENDER["Render/Railway"]
    REACT["React frontend"] -->|statik build| VERCEL["Vercel/Netlify"]
    BOT["telegram_bot/bot.py"] -->|"Background Worker!"| RENDER2["Render/Railway worker"]
    BOT -->|"Web Service" deb noto'g'ri joylashtirilsa| CRASH["Health check xato, doim qayta ishga tushadi"]
</pre>

<p>StudyMate'ning uchala qismi tayyor — endi ularni <strong>haqiqiy internetga</strong> chiqaramiz. Bu yerda muhim farq bor: Django va React "so'rov-javob" tarzida ishlaydi, <strong>bot esa doim ishlab turishi kerak</strong> — bu deploy platformasida boshqacha "xizmat turi" talab qiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — uchta qismni to'g'ri "xizmat turi" bilan deploy qilish</h4>
<pre><code># Render/Railway kabi platformalarda ODATDA ikkita asosiy xizmat turi bor:
#
# 1. "Web Service" - HTTP so'rovlarga javob beradi, $PORT'da tinglaydi
#    -> Django backend SHU turga mos (u so'rovlarni kutadi)
#
# 2. "Background Worker" - doim ishlab turadi, HTTP so'rov kutmaydi
#    -> telegram_bot/bot.py AYNAN SHU turga mos! (u Telegram'dan xabar "poll" qiladi)
#
# React esa alohida - statik build sifatida Vercel/Netlify'ga deploy qilinadi
# (server kerak emas, faqat tayyor HTML/CSS/JS fayllar)</code></pre>

<h4>BLOKA 2 — environment o'zgaruvchilari (uchala qism uchun)</h4>
<pre><code># django_backend/.env.example
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
BOT_TOKEN=...                         # ❗ bot HAM, send_reminders HAM shu tokenni ishlatadi
FRONTEND_URL=https://studymate.vercel.app

# telegram_bot/.env.example
DATABASE_URL=postgresql://user:parol@host:5432/dbnomi   # ❗ django_backend bilan BIR XIL!
BOT_TOKEN=...
DJANGO_SETTINGS_MODULE=studymate.settings

# frontend/.env.production
REACT_APP_API_URL=https://studymate-api.onrender.com</code></pre>

<h4>BLOKA 3 — yakuniy README va tekshiruv ro'yxati</h4>
<pre><code># README.md
# StudyMate

## Jonli havolalar
- Frontend: https://studymate.vercel.app
- Backend API: https://studymate-api.onrender.com
- Telegram bot: @StudyMateBot

## Holat
- [x] Barcha 7 bosqich yakunlandi ✅

## Sinov ro'yxati (deploy qilingandan keyin)
- [ ] Ro'yxatdan o'tish va kirish web saytda ishlaydi
- [ ] Topshiriq qo'shish/bajarilgan qilish web saytda ishlaydi
- [ ] /link KOD orqali Telegram akkaunt bog'lanadi
- [ ] /topshiriqlar buyrug'i web saytdagi ma'lumotni ko'rsatadi
- [ ] Muddati yaqin topshiriq uchun avtomatik xabar keladi</code></pre>

<h3>🐛 Ataylab xato — botni "Web Service" sifatida deploy qilish</h3>
<pre><code># Dasturchi telegram_bot/'ni Django kabi "Web Service" sifatida sozlaydi:
# Platform: "Bot qaysi portda tinglaydi?" deb so'raydi
# Dasturchi: hech qanday $PORT ochmaydi, chunki bot HTTP server emas!

# Natijada:
# ❌ Platform "health check" muvaffaqiyatsiz deb hisoblab, botni DOIM
#    qayta ishga tushiradi (u hech qachon $PORT'da javob bermagani uchun)
# ❌ Bot ba'zan bir necha soniya ishlaydi-yu, keyin platform uni "o'lik"
#    deb hisoblab qayta ishga tushiradi - foydalanuvchilar botga yozganda
#    tasodifiy javob kelmasligi mumkin</code></pre>

<p><strong>Natija:</strong> <code>telegram_bot/bot.py</code> HTTP so'rovlarni kutmaydi — u Telegram serverlaridan xabarlarni <strong>o'zi so'rab turadi</strong> (polling) yoki webhook orqali qabul qiladi, lekin <strong>hech qachon</strong> platformaning "bu xizmat tirikmi?" tekshiruvi kutgan odatiy HTTP javobini bermaydi. Agar bot "Web Service" sifatida sozlansa, platform uni doimiy ravishda "javob bermayapti" deb hisoblab, muntazam ravishda <strong>qayta ishga tushiradi</strong> — bu botning barqaror ishlashini buzadi. To'g'ri yechim: botni <strong>"Background Worker"</strong> (yoki shunga o'xshash, HTTP kutmaydigan xizmat turi) sifatida joylashtirish.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega uchta qism uchta xil deploy usuli talab qiladi?</h4>
<p>Django (so'rov-javob), React (statik fayllar) va bot (doimiy ishlab turuvchi jarayon) — <strong>uchtasi ham tubdan boshqacha</strong> ishlash modeliga ega. Har biriga mos "xizmat turi" tanlanmasa, ular yoki umuman ishlamaydi, yoki barqarorsiz ishlaydi.</p>

<h4>2. Nega bot va send_reminders bir xil <code>BOT_TOKEN</code>ni ishlatadi?</h4>
<p>Ikkalasi ham <strong>bitta</strong> Telegram botiga tegishli xabarlarni yuboradi/qabul qiladi — Telegram tomonidan bitta bot bitta token bilan aniqlanadi. Agar ular turli token ishlatsa, ular <strong>ikki xil bot</strong> bo'lib qolar edi.</p>

<h4>3. Nega bot va Django backend BIR XIL <code>DATABASE_URL</code>ni ishlatishi kerak (yana)?</h4>
<p>1-darsdan boshlab ta'kidlangan tamoyil — deploy bosqichida ham amal qiladi. Agar deploy qilingan botga boshqa (yoki noto'g'ri) <code>DATABASE_URL</code> berilsa, u production'dagi haqiqiy foydalanuvchi ma'lumotlarini <strong>ko'ra olmaydi</strong>, garchi hammasi "ishlab turgandek" ko'rinsa ham.</p>

<h4>4. "Web Service" va "Background Worker" orasidagi farq nima?</h4>
<p>"Web Service" — tashqi HTTP so'rovlarni kutadigan, <code>$PORT</code>da "tinglaydigan" xizmat. "Background Worker" — hech qanday tashqi so'rovni kutmasdan, <strong>o'zi</strong> uzluksiz ishlab turadigan jarayon (masalan, Telegram'dan xabar so'rab turish, yoki navbatni qayta ishlash). Ular platformada <strong>turlicha</strong> boshqariladi.</p>

<h4>5. Nega botni noto'g'ri xizmat turi bilan joylashtirish "vaqti-vaqti bilan ishlaydi" degan taassurot beradi?</h4>
<p>Bot ba'zan platform uni <strong>o'chirib qayta yoqqunga qadar</strong> to'g'ri ishlaydi (chunki u aslida to'g'ri kod, faqat noto'g'ri "konteynerda" ishlaydi). Lekin platform muntazam ravishda uni "javob bermayapti" deb hisoblab qayta ishga tushirganda, bot vaqtincha "o'chib qoladi" — bu nosozlikni "tasodifiy" qilib ko'rsatadi va sababini topishni qiyinlashtiradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Django — "Web Service", React — statik build, bot — "Background Worker"</li>
<li>✅ Bot va send_reminders bir xil <code>BOT_TOKEN</code>ni ishlatishi shart (bitta Telegram botiga tegishli)</li>
<li>✅ Bot va Django backend production'da ham BIR XIL <code>DATABASE_URL</code>ga ulanishi shart</li>
<li>✅ "Web Service" HTTP so'rov kutadi, "Background Worker" esa doimiy o'zi ishlab turadi</li>
<li>✅ Botni noto'g'ri xizmat turida joylashtirish uni muntazam, "tasodifiy" ravishda qayta ishga tushirilishiga olib keladi</li>
</ul>

<h3>🎉 Tabriklaymiz!</h3>
<p>Siz StudyMate'ni 1-bosqichdagi bo'sh repo'dan boshlab, DB sxemasi, Django API, React frontend, autentifikatsiya, Telegram bot bog'lash, avtomatik bildirishnomalar va nihoyat <strong>uch qismli haqiqiy deploy</strong>gacha qurdingiz. Bu — Django, React va Telegram Bot kurslarida alohida o'rgangan bilimlarni <strong>bitta, real, ko'p interfeysli</strong> loyihada birlashtirish tajribasi edi.</p>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 7-BOSQICH (CAPSTONE YAKUNI): Uchta qismni birga deploy qilish
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Xizmat turlari (izohda - deploy platformasi tushunchasi, kod emas)
# ─────────────────────────────────────────────────────────────────────

# django_backend/  -> "Web Service" (HTTP so'rov kutadi, $PORT'da tinglaydi)
# frontend/         -> statik build (Vercel/Netlify, server kerak emas)
# telegram_bot/     -> "Background Worker" (doimiy ishlab turadi, polling)

# ─────────────────────────────────────────────────────────────────────
# 2) Environment o'zgaruvchilari (izohda)
# ─────────────────────────────────────────────────────────────────────

# django_backend/.env.example
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...
# FRONTEND_URL=https://studymate.vercel.app

# telegram_bot/.env.example
# DATABASE_URL=postgresql://user:parol@host:5432/dbnomi
# BOT_TOKEN=...
# DJANGO_SETTINGS_MODULE=studymate.settings

# frontend/.env.production
# REACT_APP_API_URL=https://studymate-api.onrender.com

# ─────────────────────────────────────────────────────────────────────
# 3) telegram_bot/bot.py - to'g'ri ishga tushirish (polling)
# ─────────────────────────────────────────────────────────────────────

import asyncio


async def main():
    # ... dp = Dispatcher(), handler'lar ...
    # await dp.start_polling(bot)   # ❗ bu funksiya HECH QACHON qaytmaydi - doim ishlab turadi
    pass


if __name__ == "__main__":
    asyncio.run(main())

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - botni "Web Service" sifatida sozlash (izohda)
# ─────────────────────────────────────────────────────────────────────

# Agar platform botdan $PORT'da HTTP javob kutsa, lekin bot buni
# hech qachon bermasa:
# ❌ Health check muvaffaqiyatsiz -> platform botni muntazam qayta ishga tushiradi
"""

L7_EX = [
    {
        "title": "Django backend uchun to'g'ri xizmat turi",
        "description": "Deploy platformasida Django backend qaysi xizmat turiga mos keladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Background Worker",
            "Web Service (HTTP so'rovlarni kutadi)",
            "Statik build",
            "Hech qaysi turga mos kelmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Django HTTP so'rovlarga javob beradigan server.",
        "explanation": "Django backend HTTP so'rovlarni kutadigan, $PORT'da tinglaydigan \"Web Service\" turiga mos keladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Telegram bot uchun to'g'ri xizmat turi",
        "description": "telegram_bot/bot.py deploy qilinganda qaysi xizmat turiga joylashtirilishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Web Service, chunki u ham serverdek ishlaydi",
            "Background Worker, chunki u HTTP so'rov kutmasdan doimiy ishlab turadi",
            "Statik build, chunki u ham fayl",
            "Hech qanday maxsus sozlash kerak emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bot Telegram'dan xabar \"poll\" qilib turadi, HTTP so'rov kutmaydi.",
        "explanation": "Bot HTTP so'rovlarni kutmasdan, doimiy ishlab, Telegram'dan xabar so'rab turadigan jarayon bo'lgani uchun \"Background Worker\" turiga joylashtirilishi kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "StudyMate deploy jarayonini tartiblang",
        "description": "Uch qismli StudyMate loyihasini deploy qilish umumiy jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Django backend Web Service sifatida deploy qilinadi, PostgreSQL ulanadi",
            "telegram_bot Background Worker sifatida, Django bilan BIR XIL DATABASE_URL bilan deploy qilinadi",
            "React frontend statik build sifatida Vercel/Netlify'ga deploy qilinadi",
            "Barcha uch qism jonli holatda tekshiriladi va README yangilanadi",
        ],
        "correct_order": [
            "Django backend Web Service sifatida deploy qilinadi, PostgreSQL ulanadi",
            "telegram_bot Background Worker sifatida, Django bilan BIR XIL DATABASE_URL bilan deploy qilinadi",
            "React frontend statik build sifatida Vercel/Netlify'ga deploy qilinadi",
            "Barcha uch qism jonli holatda tekshiriladi va README yangilanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bot va send_reminders'ning umumiy environment o'zgaruvchisi",
        "description": "Telegram bot va send_reminders komandasi ikkalasi ham qaysi environment o'zgaruvchisini bir xil qiymat bilan ishlatishi shart? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "BOT_TOKEN",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega botni Web Service sifatida joylashtirish uni muntazam qayta ishga tushiradi?",
        "description": (
            "Agar telegram_bot/ deploy platformasida \"Web Service\" "
            "sifatida sozlansa (bot esa hech qanday $PORT'da HTTP javob "
            "bermaydi), nega platform botni muntazam ravishda qayta "
            "ishga tushiraveradi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "\"Web Service\" turidagi xizmatlar platform tomonidan "
            "muntazam \"health check\" (sog'lom-ishlayaptimi tekshiruvi) "
            "orqali nazorat qilinadi — bu tekshiruv odatda xizmatning "
            "belgilangan $PORT'ida HTTP javob berishini kutadi. "
            "telegram_bot/bot.py esa HTTP server emas — u Telegram "
            "serverlaridan xabar so'rab turadigan (polling) jarayon, "
            "shuning uchun u hech qachon platform kutayotgan HTTP "
            "javobini bermaydi. Platform bu \"javobsizlik\"ni xizmat "
            "\"o'lgan\" yoki ishlamayapti deb talqin qiladi va uni qayta "
            "ishga tushiradi — garchi bot aslida to'g'ri ishlab turgan "
            "bo'lsa ham. Bu jarayon muntazam takrorlanadi, chunki bot "
            "hech qachon platform kutgan HTTP javobini bera olmaydi."
        ),
        "hint": "\"Web Service\" turidagi xizmatlarni platform qanday \"tirikligini\" tekshiradi, va bot bunga javob bera oladimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]

L7_TASK = {
    "task_title": "StudyMate — CAPSTONE yakuni: uch qismli to'liq deploy qilingan loyiha",
    "task_description": (
        "StudyMate'ning barcha uch qismini haqiqiy hostingga deploy qiling: "
        "Django backend (Web Service), React frontend (statik build), "
        "Telegram bot (Background Worker). Bot va Django BIR XIL bazaga "
        "ulanganini tekshiring. README.md'ni jonli havolalar va yakuniy "
        "sinov ro'yxati bilan yangilang."
    ),
    "task_requirements": (
        "• Django backend haqiqiy hostingda Web Service sifatida ishlab turibdi\n"
        "• React frontend haqiqiy hostingda statik build sifatida ishlab turibdi\n"
        "• Telegram bot haqiqiy hostingda Background Worker sifatida ishlab turibdi (Web Service emas)\n"
        "• Bot va Django backend BIR XIL production PostgreSQL bazasiga ulangan\n"
        "• Ro'yxatdan o'tish, kirish, topshiriq qo'shish web saytda ishlaydi\n"
        "• /link va /topshiriqlar buyruqlari haqiqiy botda ishlaydi\n"
        "• README.md: jonli havolalar (frontend, backend, bot), 7/7 bosqich yakunlangan checklist, sinov ro'yxati\n"
        "• Submission uchun FAQAT GitHub repository URL talab qilinadi — AI baholash butun repo kodini "
        "(backend + frontend + bot) tekshiradi, alohida live_demo_url maydoni endi shart emas"
    ),
    "task_technologies": "Render/Railway (Web Service + Background Worker), Vercel/Netlify, PostgreSQL",
    "task_deadline_days": 4,
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
