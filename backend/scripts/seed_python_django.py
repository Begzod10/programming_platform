"""Seed "Python: Django Asoslari" (12 lessons): fills a real gap — the Python
track has Flask covered twice (Beginner course 21 + Intermediate course 28)
but has zero Django coverage, even though Django is one of the two most
in-demand Python web frameworks alongside Flask.

Usage:
    cd backend
    python -m scripts.seed_python_django
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
    "title": "Python: Django Asoslari",
    "description": (
        "Python: Keyingi Bosqich kursini tugatgan dasturchilar uchun: Django "
        "bilan to'liq veb-ilova qurishni o'rganing — MTV arxitekturasi, "
        "URL routing, templates, ORM va migratsiyalar, admin panel, forms, "
        "autentifikatsiya va class-based views. Flask'dan farqli, katta va "
        "'batteries-included' frameworkni real loyiha orqali egallaysiz."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 6,
    "max_points": 200,
    "category_id": 8,  # Python
    "prerequisite_course_id": 37,  # Python: Keyingi Bosqich
    "is_active": True,
    "is_published": False,  # flip to True once all 12 lessons are written
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done",
     "title": "1-Django'ga kirish va MTV arxitekturasi",
     "scope": "Why Django vs Flask, django-admin startproject/startapp, MTV (Model-Template-View), runserver."},
    {"order": 1, "ref": "L2", "status": "done",
     "title": "2-URL routing va views",
     "scope": "urls.py, path(), function-based views, HttpResponse, dynamic URL params."},
    {"order": 2, "ref": "L3", "status": "done",
     "title": "3-Templates va shablon tili",
     "scope": "Django Template Language: {{ }}, {% %}, template inheritance (extends/block), static files."},
    {"order": 3, "ref": "L4", "status": "done",
     "title": "4-Models va ORM asoslari",
     "scope": "models.Model, field types, makemigrations/migrate, QuerySet basics (all/filter/get)."},
    {"order": 4, "ref": "R1", "status": "done",
     "title": "R1-Mini blog (takrorlash)",
     "scope": "Repetition project combining routing + templates + models from lessons 1-4."},
    {"order": 5, "ref": "L5", "status": "done",
     "title": "5-Django Admin paneli",
     "scope": "admin.py, ModelAdmin, list_display/search_fields, createsuperuser."},
    {"order": 6, "ref": "L6", "status": "done",
     "title": "6-Forms va validatsiya",
     "scope": "forms.Form vs ModelForm, is_valid(), cleaned_data, CSRF token."},
    {"order": 7, "ref": "L7", "status": "done",
     "title": "7-ORM chuqurroq: querysets va bog'lanishlar",
     "scope": "ForeignKey, ManyToMany, related_name, filter chaining, select_related."},
    {"order": 8, "ref": "R2", "status": "done",
     "title": "R2-Forms + relationships mini-loyiha (takrorlash)",
     "scope": "Repetition project combining admin + forms + model relationships."},
    {"order": 9, "ref": "L8", "status": "done",
     "title": "8-Autentifikatsiya",
     "scope": "django.contrib.auth, login/logout/register views, login_required, permissions."},
    {"order": 10, "ref": "L9", "status": "done",
     "title": "9-Class-Based Views (CBV)",
     "scope": "ListView, DetailView, CreateView/UpdateView/DeleteView, generic CBV vs function-based."},
    {"order": 11, "ref": "L10", "status": "done",
     "title": "10-CAPSTONE: To'liq Django loyihasi",
     "scope": "Combining models + admin + forms + auth + CBV into a real mini blog/task app."},
]


L1_TEXT = """\
<h2>Django'ga kirish — 5 daqiqada birinchi sahifa</h2>

<pre class="mermaid">
flowchart LR
    REQ["Brauzer so'rovi"] --> URL["urls.py — qaysi View?"]
    URL --> VIEW["views.py — mantiq, Model'dan ma'lumot olish"]
    VIEW --> MODEL["models.py — ma'lumotlar bazasi"]
    VIEW --> TEMPLATE["template.html — HTML natija"]
    TEMPLATE --> RESP["Brauzerga javob"]
</pre>

<p>Siz Flask'da veb-ilova qurishni bilasiz — routing, view funksiyalari, shablonlar. <strong>Django</strong> ham Python veb-freymvorki, lekin Flask'dan farqli, u "batteries-included" &mdash; ya'ni ORM, admin panel, autentifikatsiya, forms tekshiruvi kabi ko'p narsa <strong>tayyor holda</strong> keladi. Katta, jiddiy loyihalar uchun sanoat standarti aynan Django hisoblanadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — loyiha va app yaratish</h4>
<pre><code># Terminalda:
django-admin startproject mysite    # ❗ loyiha (butun sayt) yaratiladi
cd mysite
python manage.py startapp blog      # ❗ app (bitta funksional bo'lak) yaratiladi

# Natijada quyidagi tuzilma hosil bo'ladi:
# mysite/
#   manage.py          <- barcha buyruqlar shu orqali ishga tushadi
#   mysite/settings.py <- loyiha sozlamalari (INSTALLED_APPS shu yerda)
#   mysite/urls.py      <- bosh URL yo'nalishlari
#   blog/
#     models.py         <- ma'lumotlar bazasi jadvallari
#     views.py          <- mantiq (nima ko'rsatish kerak)
#     admin.py          <- admin panelga ro'yxatdan o'tkazish

python manage.py runserver           # ❗ lokal serverni ishga tushiradi (127.0.0.1:8000)</code></pre>

<h4>BLOKA 2 — appni ro'yxatdan o'tkazish (INSTALLED_APPS)</h4>
<pre><code># mysite/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # ❗ yaratilgan appni Django'ga "tanishtirish" shart, aks holda u ishlamaydi
]</code></pre>

<h4>BLOKA 3 — MTV arxitekturasi (Model-Template-View)</h4>
<pre><code># Django o'zining MVC (Model-View-Controller) versiyasini MTV deb ataydi:
#
# Model    -> ma'lumotlar bazasi bilan ishlaydi (models.py)
# Template -> foydalanuvchiga ko'rinadigan HTML (templates/)
# View     -> Model'dan ma'lumot oladi, Template'ga uzatadi - "controller" vazifasini bajaradi

# blog/views.py
from django.http import HttpResponse

def salomlash(request):          # ❗ har bir view - HttpRequest oladi, HttpResponse qaytaradi
    return HttpResponse("Salom, Django!")</code></pre>

<h3>🐛 Ataylab xato — appni INSTALLED_APPS'ga qo'shishni unutish</h3>
<pre><code># blog/models.py da model yaratilgan, lekin settings.py'da:
INSTALLED_APPS = [
    'django.contrib.admin',
    # 'blog' qatori yo'q!
]

# python manage.py makemigrations blog buyrug'ini ishga tushirsangiz:
# ❌ Xato: App 'blog' could not be found. Is it in INSTALLED_APPS?</code></pre>

<p><strong>Natija:</strong> Django loyihadagi papkalarni avtomatik "his qilmaydi" &mdash; har bir app <strong>aniq</strong> <code>INSTALLED_APPS</code> ro'yxatiga qo'shilishi shart, aks holda Django uning models, admin yoki boshqa qismlarini <strong>umuman ko'rmaydi</strong>. Bu Flask'dagi kabi "papkani yaratdim, ishlayapti" mantig'idan farq qiladi &mdash; Django'da har bir bo'lak <strong>aniq ro'yxatdan o'tishi</strong> kerak.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Django va Flask orasidagi asosiy farq</h4>
<p>Flask &mdash; "micro-framework": minimal, kerakli narsalarni o'zingiz qo'shasiz (ORM, forms, auth). Django &mdash; "batteries-included": ORM, admin panel, autentifikatsiya tizimi, forms validatsiyasi kabi ko'p narsa <strong>allaqachon</strong> mavjud. Katta loyihalarda bu tezlik beradi, lekin Django'ning o'z qoidalariga (konventsiyalariga) rioya qilish kerak.</p>

<h4>2. Loyiha (project) va app orasidagi farq</h4>
<p><strong>Loyiha</strong> &mdash; butun sayt (sozlamalar, bosh URL'lar). <strong>App</strong> &mdash; loyiha ichidagi bitta mustaqil funksional bo'lak (masalan <code>blog</code>, <code>users</code>, <code>shop</code>). Bitta loyihada bir nechta app bo'lishi mumkin, va app'lar boshqa loyihalarda ham qayta ishlatilishi mumkin.</p>

<h4>3. MTV arxitekturasi</h4>
<p>Django'ning MTV'si klassik MVC'ga juda o'xshash, faqat nomlanishi boshqacha: <strong>Model</strong> (ma'lumotlar bazasi) — MVC'dagi Model bilan bir xil. <strong>Template</strong> (HTML) — MVC'dagi View'ga mos keladi. <strong>View</strong> (Django'da) — MVC'dagi Controller vazifasini bajaradi, ya'ni Model'dan ma'lumot olib, Template'ga uzatadi.</p>

<h4>4. Nega har bir app INSTALLED_APPS'ga qo'shilishi kerak?</h4>
<p>Django katta, murakkab freymvork bo'lgani uchun, u qaysi app'lar "faol" ekanligini <strong>aniq</strong> bilishi kerak — bu app'larning migratsiyalarini kuzatish, admin'ga ro'yxatdan o'tkazish va boshqa ko'p ichki jarayonlar uchun zarur. Ro'yxatga qo'shilmagan app Django uchun "mavjud emas" hisoblanadi.</p>

<h4>5. manage.py nima uchun kerak?</h4>
<p><code>manage.py</code> &mdash; loyihaning "boshqaruv markazi": server ishga tushirish (<code>runserver</code>), migratsiya yaratish/qo'llash (<code>makemigrations</code>/<code>migrate</code>), superuser yaratish va boshqa barcha Django buyruqlari shu fayl orqali ishga tushiriladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>django-admin startproject</code> — loyiha, <code>python manage.py startapp</code> — app yaratadi</li>
<li>✅ Har bir app <code>INSTALLED_APPS</code>'ga qo'shilishi <strong>shart</strong>, aks holda Django uni "ko'rmaydi"</li>
<li>✅ MTV: Model (DB) — Template (HTML) — View (mantiq, MVC'dagi Controller)</li>
<li>✅ Django "batteries-included" — Flask'dan farqli ko'p narsa tayyor keladi</li>
<li>✅ <code>manage.py runserver</code> — lokal serverni ishga tushiradi</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 1: Django'ga kirish va MTV arxitekturasi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Loyiha va app yaratish (terminal buyruqlari, izohda)
# ─────────────────────────────────────────────────────────────────────

# django-admin startproject mysite
# cd mysite
# python manage.py startapp blog
# python manage.py runserver

# ─────────────────────────────────────────────────────────────────────
# 2) mysite/settings.py - appni ro'yxatdan o'tkazish
# ─────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
]

# ─────────────────────────────────────────────────────────────────────
# 3) blog/views.py - birinchi view (MTV'dagi View qismi)
# ─────────────────────────────────────────────────────────────────────

from django.http import HttpResponse


def salomlash(request):
    return HttpResponse("Salom, Django!")

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - INSTALLED_APPS'ga qo'shishni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     # 'blog' qatori yo'q!
# ]
# python manage.py makemigrations blog
# ❌ App 'blog' could not be found. Is it in INSTALLED_APPS?
"""

L1_EX = [
    {
        "title": "Django va Flask orasidagi asosiy farq",
        "description": "Django va Flask orasidagi asosiy farq nimada?",
        "exercise_type": "multiple_choice",
        "options": [
            "Django faqat frontend uchun, Flask faqat backend uchun",
            "Django \"batteries-included\" (ORM, admin, auth tayyor), Flask esa minimal \"micro-framework\"",
            "Ular aslida bir xil, faqat nomi boshqa",
            "Flask faqat katta loyihalar uchun, Django faqat kichik loyihalar uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bittasida ko'p narsa tayyor keladi, ikkinchisida o'zingiz qo'shasiz.",
        "explanation": "Django \"batteries-included\" — ORM, admin panel, autentifikatsiya kabi ko'p narsa tayyor keladi. Flask esa minimal micro-framework, kerakli narsalarni o'zingiz qo'shasiz.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "App qanday ro'yxatdan o'tkaziladi?",
        "description": "Yangi yaratilgan Django app'ni loyihaga \"tanishtirish\" uchun nima qilish kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa, Django avtomatik topadi",
            "settings.py faylidagi INSTALLED_APPS ro'yxatiga qo'shish kerak",
            "App papkasini urls.py'ga ko'chirish kerak",
            "manage.py faylini o'chirish kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu sozlamalar faylida turadigan ro'yxat.",
        "explanation": "Har bir app settings.py faylidagi INSTALLED_APPS ro'yxatiga qo'shilishi shart, aks holda Django uni \"ko'rmaydi\".",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "MTV so'rov jarayonini tartiblang",
        "description": "Brauzerdan so'rov kelganda, MTV arxitekturasida jarayon qanday tartibda ketishini joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Brauzer so'rov yuboradi",
            "urls.py qaysi View chaqirilishini aniqlaydi",
            "View Model orqali ma'lumotlar bazasidan ma'lumot oladi",
            "View ma'lumotni Template'ga uzatadi va HTML natija qaytariladi",
        ],
        "correct_order": [
            "Brauzer so'rov yuboradi",
            "urls.py qaysi View chaqirilishini aniqlaydi",
            "View Model orqali ma'lumotlar bazasidan ma'lumot oladi",
            "View ma'lumotni Template'ga uzatadi va HTML natija qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Lokal serverni ishga tushiruvchi buyruq",
        "description": "Django loyihasida lokal serverni ishga tushirish uchun qaysi buyruq ishlatiladi? (aynan shu buyruqni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "python manage.py runserver",
        "hint": "manage.py fayli orqali ishga tushiriladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega app INSTALLED_APPS'ga qo'shilmasa xato beradi?",
        "description": (
            "blog/models.py'da model yaratilgan, lekin 'blog' "
            "INSTALLED_APPS ro'yxatiga qo'shilmagan holda "
            "makemigrations buyrug'i ishga tushirilsa, nega Django "
            "\"App 'blog' could not be found\" xatosini beradi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django papkalar tuzilmasini avtomatik \"his qilmaydi\" — u "
            "qaysi app'lar loyihada \"faol\" ekanligini faqat "
            "INSTALLED_APPS ro'yxati orqali biladi. Agar 'blog' bu "
            "ro'yxatga qo'shilmagan bo'lsa, Django uchun bu app "
            "\"mavjud emas\" hisoblanadi — shuning uchun uning models.py "
            "faylini ham, migratsiyalarini ham topa olmaydi va xato "
            "beradi. Bu Django'ning har bir bo'lak aniq ro'yxatdan "
            "o'tishi kerakligi qoidasi."
        ),
        "hint": "Django app'larni qanday \"tanib oladi\" — papkani ko'rib emas, balki qaysi ro'yxat orqali?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L2_TEXT = """\
<h2>URL routing va views — so'rovni to'g'ri funksiyaga yo'naltirish</h2>

<pre class="mermaid">
flowchart LR
    A["/blog/"] --> V1["views.postlar_royxati"]
    B["/blog/5/"] --> V2["views.post_detail(post_id=5)"]
    C["mysite/urls.py"] -->|include| D["blog/urls.py"]
</pre>

<p>Flask'da <code>@app.route("/blog/&lt;int:post_id&gt;")</code> deb yozgan bo'lar edingiz. Django'da routing alohida <code>urls.py</code> faylida, <strong>views'dan ajratilgan holda</strong> saqlanadi — bu katta loyihalarda barcha yo'nalishlarni bir joydan ko'rish imkonini beradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — oddiy path() va view</h4>
<pre><code># blog/views.py
from django.http import HttpResponse

def postlar_royxati(request):
    return HttpResponse("Barcha postlar ro'yxati")

def salomlash(request):
    return HttpResponse("Salom, Django!")

# blog/urls.py (yangi fayl - alohida yaratiladi)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),      # ❗ '' - blog/ ning o'zi
    path('salom/', views.salomlash, name='salomlash'),        # ❗ blog/salom/
]</code></pre>

<h4>BLOKA 2 — bosh urls.py'ga include() qilish</h4>
<pre><code># mysite/urls.py (loyihaning bosh routing fayli)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # ❗ blog/ bilan boshlangan barcha URL'lar blog/urls.py'ga yo'naltiriladi
]
# Natijada: mysite.com/blog/salom/  ->  blog/urls.py'dagi 'salom/' -> views.salomlash</code></pre>

<h4>BLOKA 3 — dinamik URL parametrlari</h4>
<pre><code># blog/urls.py
urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),  # ❗ <int:post_id> - butun son qabul qiladi
]

# blog/views.py
def post_detail(request, post_id):          # ❗ URL'dagi parametr view'ga argument sifatida keladi
    return HttpResponse(f"Post ID: {post_id}")

# blog/5/  ->  post_detail(request, post_id=5)  ->  "Post ID: 5"
# blog/abc/ -> ❌ mos kelmaydi, chunki <int:...> faqat butun sonni qabul qiladi</code></pre>

<h3>🐛 Ataylab xato — mysite/urls.py'da include() qilishni unutish</h3>
<pre><code># blog/urls.py to'g'ri yozilgan, lekin mysite/urls.py'da:
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('blog/', include('blog.urls')) qatori yo'q!
]

# Brauzerda mysite.com/blog/ ochilsa:
# ❌ Xato: Page not found (404) - Django blog/urls.py haqida umuman bilmaydi</code></pre>

<p><strong>Natija:</strong> har bir app'ning <code>urls.py</code> fayli <strong>o'zi mustaqil ishlamaydi</strong> — uni loyihaning bosh <code>urls.py</code> fayliga <code>include()</code> orqali ulash <strong>shart</strong>. Aks holda, blog app'idagi barcha routing to'g'ri yozilgan bo'lsa ham, Django ularni umuman "ko'rmaydi", chunki bosh routing fayli ularga hech qanday yo'l ko'rsatmagan.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega routing alohida urls.py faylida saqlanadi?</h4>
<p>Flask'da odatda routing va view bir joyda (<code>@app.route</code> dekoratori) yoziladi. Django'da routing <strong>alohida</strong> saqlanadi — bu katta loyihalarda barcha URL'larni bitta joydan ko'rish, tartiblash va app'lar orasida qayta ishlatish imkonini beradi.</p>

<h4>2. include() nima uchun kerak?</h4>
<p><code>include('blog.urls')</code> — loyihaning bosh <code>urls.py</code> fayliga "agar URL <code>blog/</code> bilan boshlansa, qolgan qismini <code>blog/urls.py</code> faylidan qidir" deb aytadi. Bu har bir app'ning routing'ini mustaqil, alohida faylda saqlash imkonini beradi.</p>

<h4>3. Dinamik URL parametrlari qanday ishlaydi?</h4>
<p><code>&lt;int:post_id&gt;</code> kabi yozuv URL'ning bir qismini "ushlab olib", uni view funksiyasiga <strong>argument sifatida</strong> uzatadi. <code>int:</code> qismi — konverter, faqat butun sonlarga mos kelishini ta'minlaydi (masalan <code>str:</code>, <code>slug:</code> kabi boshqa konverterlar ham bor).</p>

<h4>4. name= parametri nima uchun kerak?</h4>
<p>Har bir <code>path()</code>ga <code>name=</code> berish, keyinchalik shu URL'ga template yoki view kodida <strong>qattiq yozilgan matn</strong> (masalan <code>"/blog/5/"</code>) o'rniga <code>{% url 'post-detail' post_id=5 %}</code> kabi nom orqali murojaat qilish imkonini beradi — URL manzili o'zgarsa ham, kodni o'zgartirish shart bo'lmaydi.</p>

<h4>5. Nega include() qilinmasa 404 xato beriladi?</h4>
<p>Django brauzerdan kelgan so'rovni <strong>faqat</strong> loyihaning bosh <code>urls.py</code> fayli orqali qidiradi. Agar bosh fayl biror app'ning <code>urls.py</code>'siga <code>include()</code> orqali yo'naltirilmagan bo'lsa, o'sha app ichidagi barcha yo'llar Django uchun "mavjud emas" — natijada 404 (Page not found) xatosi beriladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Routing <code>urls.py</code> faylida, view'lardan alohida saqlanadi</li>
<li>✅ <code>include('app.urls')</code> — app'ning routing'ini bosh <code>urls.py</code>'ga ulaydi</li>
<li>✅ <code>&lt;int:param&gt;</code> — dinamik URL qismini view'ga argument sifatida uzatadi</li>
<li>✅ <code>name=</code> — URL'ga nom berib, uni kodda qattiq yozilgan matn o'rniga nom orqali chaqirish imkonini beradi</li>
<li>✅ <code>include()</code> qilinmasa, app'ning routing'i butunlay "ko'rinmaydi" va 404 xato beriladi</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 2: URL routing va views
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - oddiy view'lar
# ─────────────────────────────────────────────────────────────────────

from django.http import HttpResponse


def postlar_royxati(request):
    return HttpResponse("Barcha postlar ro'yxati")


def salomlash(request):
    return HttpResponse("Salom, Django!")


def post_detail(request, post_id):
    return HttpResponse(f"Post ID: {post_id}")

# ─────────────────────────────────────────────────────────────────────
# 2) blog/urls.py - app'ning routing fayli
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.postlar_royxati, name='post-list'),
#     path('salom/', views.salomlash, name='salomlash'),
#     path('<int:post_id>/', views.post_detail, name='post-detail'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 3) mysite/urls.py - bosh routing fayli
# ─────────────────────────────────────────────────────────────────────

# from django.contrib import admin
# from django.urls import path, include
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('blog/', include('blog.urls')),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - include() qilishni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # path('blog/', include('blog.urls')) qatori yo'q!
# ]
# mysite.com/blog/ -> ❌ Page not found (404)
"""

L2_EX = [
    {
        "title": "Django'da routing qayerda saqlanadi?",
        "description": "Flask'dan farqli, Django'da URL routing odatda qayerda saqlanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "views.py faylida, view funksiyalari bilan bir joyda",
            "Alohida urls.py faylida, view'lardan ajratilgan holda",
            "settings.py faylida",
            "models.py faylida",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Flask'da @app.route bir joyda, Django'da esa...",
        "explanation": "Django'da routing view'lardan alohida, maxsus urls.py faylida saqlanadi — bu barcha yo'nalishlarni bir joydan ko'rish imkonini beradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "include() nima uchun ishlatiladi?",
        "description": "mysite/urls.py'dagi path('blog/', include('blog.urls')) qatori nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "blog.urls faylini o'chiradi",
            "blog/ bilan boshlangan URL'larni blog/urls.py fayliga yo'naltiradi",
            "Faqat admin panel uchun ishlatiladi",
            "Yangi app yaratadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu ikkita urls.py faylini bir-biriga ulaydi.",
        "explanation": "include('blog.urls') bosh urls.py fayliga, blog/ bilan boshlangan URL'larning qolgan qismini blog/urls.py faylidan qidirishni buyuradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Dinamik URL so'rovi jarayonini tartiblang",
        "description": "blog/5/ manzili ochilganda, path('<int:post_id>/', views.post_detail) orqali ishlash jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Brauzerda blog/5/ manzili ochiladi",
            "Django <int:post_id> shabloniga mos qidiradi",
            "5 raqami post_id sifatida ushlab olinadi",
            "post_detail(request, post_id=5) chaqiriladi",
        ],
        "correct_order": [
            "Brauzerda blog/5/ manzili ochiladi",
            "Django <int:post_id> shabloniga mos qidiradi",
            "5 raqami post_id sifatida ushlab olinadi",
            "post_detail(request, post_id=5) chaqiriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "path()ga name= berish sababi",
        "description": "path()ga name= parametrini berish nima uchun foydali? (bir so'z bilan: template yoki kodda nima orqali murojaat qilish uchun ishlatiladi?)",
        "exercise_type": "text_input",
        "expected_answer": "nom",
        "hint": "{% url '...' %} tegida ishlatiladigan narsa.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega include() qilinmasa 404 xato beriladi?",
        "description": (
            "blog/urls.py to'g'ri yozilgan, lekin mysite/urls.py'da "
            "path('blog/', include('blog.urls')) qatori yo'q. Nega "
            "brauzerda blog/ manzili ochilganda 404 (Page not found) "
            "xatosi chiqadi, garchi blog/urls.py'da mos routing mavjud "
            "bo'lsa ham? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django brauzerdan kelgan har qanday so'rovni FAQAT "
            "loyihaning bosh urls.py fayli orqali qidiradi va tekshiradi "
            "— u boshqa app'larning urls.py fayllarini o'zi mustaqil "
            "ravishda qidirib topmaydi. Agar bosh urls.py'da "
            "include('blog.urls') qatori bo'lmasa, Django blog app "
            "ichidagi routing haqida umuman bilmaydi — u uchun bu "
            "yo'llar \"mavjud emas\". Shuning uchun blog/urls.py'da "
            "to'g'ri yozilgan bo'lsa ham, unga hech qanday yo'l "
            "ko'rsatilmagani sababli Django 404 xatosini qaytaradi."
        ),
        "hint": "Django so'rovni qidirishni qayerdan boshlaydi — barcha urls.py fayllaridanmi, yoki faqat bosh fayldanmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L3_TEXT = """\
<h2>Templates va shablon tili — Model'dan HTML'gacha</h2>

<pre class="mermaid">
flowchart LR
    VIEW["render(request, 'post_list.html', context)"] --> TPL["templates/post_list.html"]
    BASE["base.html"] -->|extends| TPL
    TPL -->|block content| BASE
</pre>

<p>View'da olingan ma'lumotni foydalanuvchiga <strong>ko'rinadigan HTML</strong> shaklida chiqarish uchun Django o'zining <strong>Django Template Language (DTL)</strong>'ini ishlatadi — Jinja2'ga (Flask'da ishlatilgan) juda o'xshash, lekin ba'zi farqlari bor.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — render() va oddiy template</h4>
<pre><code># blog/views.py
from django.shortcuts import render

def postlar_royxati(request):
    postlar = ["Birinchi post", "Ikkinchi post", "Uchinchi post"]
    return render(request, 'blog/post_list.html', {'postlar': postlar})  # ❗ context - dict

# templates/blog/post_list.html
&lt;h1&gt;Postlar&lt;/h1&gt;
&lt;ul&gt;
{% for post in postlar %}                 {# ❗ {% %} - mantiq (tag) uchun #}
  &lt;li&gt;{{ post }}&lt;/li&gt;                     {# ❗ {{ }} - qiymatni chiqarish uchun #}
{% empty %}
  &lt;li&gt;Postlar yo'q&lt;/li&gt;
{% endfor %}
&lt;/ul&gt;</code></pre>

<h4>BLOKA 2 — template inheritance (extends/block)</h4>
<pre><code>{# templates/base.html - barcha sahifalar uchun umumiy "skelet" #}
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;&lt;title&gt;{% block title %}Mening Blogim{% endblock %}&lt;/title&gt;&lt;/head&gt;
&lt;body&gt;
  &lt;nav&gt;Bosh sahifa | Blog&lt;/nav&gt;
  {% block content %}
  {% endblock %}
&lt;/body&gt;
&lt;/html&gt;

{# templates/blog/post_list.html #}
{% extends 'base.html' %}                  {# ❗ base.html'dan meros olinadi #}

{% block title %}Postlar ro'yxati{% endblock %}

{% block content %}                        {# ❗ base.html'dagi bo'sh joy TO'LDIRILADI #}
  &lt;h1&gt;Postlar&lt;/h1&gt;
  &lt;ul&gt;
  {% for post in postlar %}
    &lt;li&gt;{{ post }}&lt;/li&gt;
  {% endfor %}
  &lt;/ul&gt;
{% endblock %}</code></pre>

<h4>BLOKA 3 — filtrlar va static fayllar</h4>
<pre><code>{# Filtrlar - qiymatni "|" orqali o'zgartiradi #}
&lt;p&gt;{{ post.sarlavha|upper }}&lt;/p&gt;         {# katta harflarga o'giradi #}
&lt;p&gt;{{ post.matn|truncatewords:10 }}&lt;/p&gt; {# faqat 10 so'zni ko'rsatadi #}
&lt;p&gt;{{ postlar|length }}&lt;/p&gt;              {# ro'yxat uzunligi #}

{# Static fayllar (CSS, JS, rasm) uchun #}
{% load static %}                          {# ❗ har doim faylning boshida yozilishi shart #}
&lt;link rel="stylesheet" href="{% static 'blog/style.css' %}"&gt;</code></pre>

<h3>🐛 Ataylab xato — {% load static %}'ni unutish</h3>
<pre><code>{# {% load static %} yo'q holda: #}
&lt;link rel="stylesheet" href="{% static 'blog/style.css' %}"&gt;
{# ❌ Xato: Invalid block tag on line N: 'static'. Did you forget to
   register or load this tag? #}</code></pre>

<p><strong>Natija:</strong> Django Template Language'dagi ba'zi teglar (masalan <code>{% static %}</code>) <strong>standart</strong> emas — ular alohida "kutubxona" sifatida <code>{% load static %}</code> orqali <strong>aniq yuklanishi</strong> kerak. Agar bu qator yozilmasa, Django <code>{% static %}</code> tegini <strong>umuman tanimaydi</strong> va xato beradi — bu <code>import</code> qilishni unutgan Python kodiga o'xshaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. {{ }} va {% %} orasidagi farq</h4>
<p><code>{{ o'zgaruvchi }}</code> &mdash; qiymatni HTML ichiga <strong>chiqarish</strong> uchun (masalan <code>{{ post.sarlavha }}</code>). <code>{% tag %}</code> &mdash; mantiq va boshqaruv strukturalari uchun (<code>for</code>, <code>if</code>, <code>block</code>, <code>extends</code> kabi).</p>

<h4>2. Template inheritance qanday ishlaydi?</h4>
<p><code>base.html</code> umumiy "skelet"ni belgilaydi, unda <code>{% block content %}</code> kabi "bo'sh joy"lar qoldiriladi. Boshqa shablon <code>{% extends 'base.html' %}</code> deb, o'sha bo'sh joylarni <code>{% block content %}...{% endblock %}</code> orqali <strong>to'ldiradi</strong>. Bu navbar, footer kabi takrorlanadigan qismlarni har bir sahifada qayta yozishning oldini oladi.</p>

<h4>3. Filtrlar (<code>|</code>) nima uchun kerak?</h4>
<p>Filtrlar qiymatni shablon ichida <strong>o'zgartirish</strong> imkonini beradi &mdash; masalan matnni katta harfga o'tkazish, uzun matnni qisqartirish, ro'yxat uzunligini olish. Ular Python kodini shablon ichiga yozmasdan, kichik transformatsiyalarni amalga oshirish uchun mo'ljallangan.</p>

<h4>4. Nega {% load static %} kerak?</h4>
<p>Django ba'zi teglarni (masalan <code>{% static %}</code>) <strong>standart</strong> deb hisoblamaydi &mdash; ular alohida modul sifatida keladi va foydalanishdan oldin <code>{% load static %}</code> orqali <strong>aniq yuklanishi</strong> kerak. Bu Python'da <code>import</code> qilmasdan modul funksiyasidan foydalanishga urinishga o'xshaydi.</p>

<h4>5. render() funksiyasi nima qiladi?</h4>
<p><code>render(request, template_nomi, context)</code> &mdash; berilgan template faylini <code>context</code> (dict) bilan birlashtirib, tayyor HTML matn shaklidagi <code>HttpResponse</code> qaytaradi. Bu <code>HttpResponse</code>ni qo'lda yaratishdan ko'ra ancha qulay va Django'da eng ko'p ishlatiladigan usul.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>{{ }}</code> — qiymat chiqarish, <code>{% %}</code> — mantiq/tag uchun</li>
<li>✅ <code>{% extends %}</code> + <code>{% block %}</code> — shablonlar orasida meros olish (DRY)</li>
<li>✅ Filtrlar (<code>|upper</code>, <code>|truncatewords</code>, <code>|length</code>) qiymatni shablon ichida o'zgartiradi</li>
<li>✅ <code>{% load static %}</code> — static fayllar tegini yuklash uchun majburiy</li>
<li>✅ <code>render()</code> — template + context'ni birlashtirib, HTML HttpResponse qaytaradi</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 3: Templates va shablon tili
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - render() bilan
# ─────────────────────────────────────────────────────────────────────

from django.shortcuts import render


def postlar_royxati(request):
    postlar = ["Birinchi post", "Ikkinchi post", "Uchinchi post"]
    return render(request, 'blog/post_list.html', {'postlar': postlar})

# ─────────────────────────────────────────────────────────────────────
# 2) templates/base.html (izohda - HTML fayl, Python emas)
# ─────────────────────────────────────────────────────────────────────

# <!DOCTYPE html>
# <html>
# <head><title>{% block title %}Mening Blogim{% endblock %}</title></head>
# <body>
#   <nav>Bosh sahifa | Blog</nav>
#   {% block content %}
#   {% endblock %}
# </body>
# </html>

# ─────────────────────────────────────────────────────────────────────
# 3) templates/blog/post_list.html (izohda)
# ─────────────────────────────────────────────────────────────────────

# {% extends 'base.html' %}
# {% block title %}Postlar ro'yxati{% endblock %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li>{{ post }}</li>
#   {% empty %}
#     <li>Postlar yo'q</li>
#   {% endfor %}
#   </ul>
# {% endblock %}

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - {% load static %}'ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# <link rel="stylesheet" href="{% static 'blog/style.css' %}">
# ❌ Invalid block tag: 'static'. Did you forget to load this tag?
# (to'g'ri: faylning boshida {% load static %} yozilishi shart)
"""

L3_EX = [
    {
        "title": "{{ }} va {% %} orasidagi farq",
        "description": "Django shablonida {{ post.sarlavha }} va {% for post in postlar %} orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkalasi ham bir xil ishlaydi",
            "{{ }} qiymat chiqaradi, {% %} mantiq/tag uchun ishlatiladi",
            "{{ }} faqat raqamlar uchun, {% %} faqat matnlar uchun",
            "{% %} eskirgan, endi ishlatilmaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bittasi qiymat ko'rsatadi, ikkinchisi buyruq beradi.",
        "explanation": "{{ o'zgaruvchi }} qiymatni HTML ichiga chiqaradi, {% tag %} esa mantiq va boshqaruv strukturalari (for, if, block) uchun ishlatiladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Template inheritance qanday ishlaydi?",
        "description": "{% extends 'base.html' %} va {% block content %} birgalikda nimani ta'minlaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "base.html faylini o'chiradi",
            "Bola shablon base.html'dagi umumiy skeletni meros oladi va faqat block qismini to'ldiradi",
            "Ikkita mustaqil, bog'liq bo'lmagan sahifa yaratadi",
            "Faqat CSS fayllarni yuklaydi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu navbar/footer kabi takrorlanadigan qismlarni qayta yozmaslik uchun.",
        "explanation": "extends orqali bola shablon base.html'ning umumiy tuzilishini meros oladi, block esa faqat kerakli qismni (masalan content) to'ldirish imkonini beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "render() ishlash jarayonini tartiblang",
        "description": "return render(request, 'blog/post_list.html', {'postlar': postlar}) chaqirilganda jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "View postlar ro'yxatini tayyorlaydi",
            "render() chaqiriladi: template nomi va context beriladi",
            "Django template faylini topib, context bilan birlashtiradi",
            "Tayyor HTML matn HttpResponse sifatida qaytariladi",
        ],
        "correct_order": [
            "View postlar ro'yxatini tayyorlaydi",
            "render() chaqiriladi: template nomi va context beriladi",
            "Django template faylini topib, context bilan birlashtiradi",
            "Tayyor HTML matn HttpResponse sifatida qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Static fayllar tegini yuklash",
        "description": "{% static %} tegidan foydalanishdan oldin, faylning boshida qaysi qatorni yozish shart? (aynan shu qatorni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "{% load static %}",
        "hint": "Bu Python'dagi import'ga o'xshaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega {% load static %}'ni unutish xato beradi?",
        "description": (
            "Agar shablon boshida {% load static %} yozilmagan holda "
            "{% static 'blog/style.css' %} ishlatilsa, nega Django "
            "\"Invalid block tag: 'static'\" xatosini beradi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django Template Language'dagi barcha teglar standart "
            "(built-in) emas — {% static %} kabi ba'zi teglar alohida "
            "kutubxona (modul) sifatida keladi va ulardan foydalanishdan "
            "oldin {% load static %} orqali aniq yuklanishi shart. Agar "
            "bu qator yozilmasa, Django {% static %} tegini umuman "
            "tanimaydi va uni \"noto'g'ri/mavjud bo'lmagan tag\" deb "
            "hisoblab xato beradi — bu xuddi Python'da bir modul "
            "funksiyasidan import qilmasdan foydalanishga urinishga "
            "o'xshaydi."
        ),
        "hint": "{% static %} — standart tegmi, yoki alohida yuklanishi kerak bo'lgan tegmi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L4_TEXT = """\
<h2>Models va ORM asoslari — SQL yozmasdan ma'lumotlar bazasi bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    MODEL["class Post(models.Model)"] --> MAKEM["makemigrations — o'zgarishni fayl sifatida yozadi"]
    MAKEM --> MIGRATE["migrate — haqiqiy jadval yaratadi/yangilaydi"]
    MODEL --> QS["Post.objects.all() / .filter() / .get()"]
</pre>

<p>Flask'da odatda SQLAlchemy ishlatgansiz. Django'ning <strong>o'z ORM'i</strong> bor &mdash; u ham Python klassi orqali ma'lumotlar bazasi jadvalini belgilash va SQL yozmasdan so'rov yuborish imkonini beradi, lekin sintaksisi biroz farq qiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi model</h4>
<pre><code># blog/models.py
from django.db import models

class Post(models.Model):                        # ❗ har bir model - jadval
    sarlavha = models.CharField(max_length=200)   # ❗ VARCHAR(200)
    matn = models.TextField()                     # ❗ TEXT
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)  # ❗ yaratilganda avtomatik to'ldiriladi
    nashr_qilingan = models.BooleanField(default=False)

    def __str__(self):
        return self.sarlavha                      # ❗ admin panel va shell'da chiroyli ko'rinish uchun</code></pre>

<h4>BLOKA 2 — migratsiyalar</h4>
<pre><code># Terminalda:
python manage.py makemigrations blog   # ❗ Post modeliga mos "reja" (migration fayl) yaratadi
python manage.py migrate                # ❗ o'sha rejani haqiqiy ma'lumotlar bazasida bajaradi (jadval yaratadi)

# Har safar models.py o'zgarganda (yangi maydon qo'shilganda ham),
# YANA makemigrations + migrate qilish kerak!</code></pre>

<h4>BLOKA 3 — QuerySet: ma'lumot olish</h4>
<pre><code># Django shell'da (python manage.py shell) yoki view ichida:
from blog.models import Post

barcha_postlar = Post.objects.all()                     # ❗ hammasi
nashr_qilingan = Post.objects.filter(nashr_qilingan=True)  # ❗ shartga mos KO'PLAB natija
bitta_post = Post.objects.get(id=1)                      # ❗ ANIQ BITTA natija (topilmasa/2ta bo'lsa xato)

yangi_post = Post.objects.create(                        # ❗ yaratish va saqlash bir qatorda
    sarlavha="Birinchi post",
    matn="Bu mening birinchi Django postim",
)</code></pre>

<h3>🐛 Ataylab xato — models.py o'zgargandan keyin migratsiya qilishni unutish</h3>
<pre><code># models.py'ga yangi maydon qo'shildi:
class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif_ismi = models.CharField(max_length=100)  # ❗ YANGI maydon

# Lekin makemigrations/migrate ISHGA TUSHIRILMADI, va view'da:
Post.objects.create(sarlavha="Test", matn="...", muallif_ismi="Olim")
# ❌ Xato: OperationalError: no such column: blog_post.muallif_ismi
# (yoki ma'lumotlar bazasiga qarab boshqa xabar)</code></pre>

<p><strong>Natija:</strong> Django modeli (Python klassi) va haqiqiy ma'lumotlar bazasidagi jadval &mdash; ikkita <strong>alohida</strong> narsa. <code>models.py</code>'ni o'zgartirish <strong>hech qachon</strong> haqiqiy jadvalni avtomatik o'zgartirmaydi &mdash; buning uchun <strong>albatta</strong> <code>makemigrations</code> (o'zgarishni "reja" sifatida yozib olish) va <code>migrate</code> (rejani bajarish) ketma-ketligi kerak. Bu qadam tashlab ketilsa, kod bilan haqiqiy baza mos kelmay qoladi va xato beriladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Model nima?</h4>
<p>Har bir <code>models.Model</code>'dan meros olgan Python klassi &mdash; ma'lumotlar bazasidagi bitta jadvalni ifodalaydi. Klassning har bir xususiyati (<code>CharField</code>, <code>TextField</code> va h.k.) &mdash; jadvalning bitta ustuniga mos keladi.</p>

<h4>2. makemigrations va migrate orasidagi farq</h4>
<p><code>makemigrations</code> &mdash; <code>models.py</code>'dagi o'zgarishlarni <strong>fayl</strong> (migration) sifatida yozib oladi, lekin ma'lumotlar bazasiga hali tegmaydi. <code>migrate</code> &mdash; o'sha yozilgan migratsiya fayllarini <strong>haqiqiy</strong> ma'lumotlar bazasida bajaradi (jadval yaratadi/o'zgartiradi). Ikkalasi ham har safar model o'zgarganda ketma-ket bajarilishi kerak.</p>

<h4>3. filter() va get() orasidagi farq</h4>
<p><code>filter()</code> &mdash; shartga mos <strong>bir nechta</strong> (yoki nolta) natijani QuerySet sifatida qaytaradi, hech qachon xato bermaydi. <code>get()</code> &mdash; <strong>aynan bitta</strong> natija kutadi: agar hech narsa topilmasa <code>DoesNotExist</code>, agar bir nechta topilsa <code>MultipleObjectsReturned</code> xatosini beradi.</p>

<h4>4. objects nima?</h4>
<p><code>Post.objects</code> &mdash; Django tomonidan har bir modelga avtomatik qo'shiladigan "manager" &mdash; u orqali <code>all()</code>, <code>filter()</code>, <code>get()</code>, <code>create()</code> kabi metodlarga kirish mumkin. Bu &mdash; ORM'ning "kirish nuqtasi".</p>

<h4>5. Nega migratsiya qilinmasa xato chiqadi?</h4>
<p>Ma'lumotlar bazasidagi haqiqiy jadval tuzilishi <strong>faqat</strong> qo'llanilgan migratsiyalar orqali o'zgaradi. <code>models.py</code>'ga yangi maydon qo'shish &mdash; bu shunchaki Python kodini o'zgartirish, u hali bazaga "yetib bormagan". Shu sababli, yangi maydonga yozishga urinilsa, ma'lumotlar bazasi bunday ustunni <strong>hali</strong> tanimaydi va xato beradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>models.Model</code>'dan meros olgan klass &mdash; ma'lumotlar bazasi jadvali</li>
<li>✅ <code>makemigrations</code> — o'zgarishni fayl qiladi, <code>migrate</code> — bazada bajaradi</li>
<li>✅ <code>filter()</code> — ko'p natija (xatosiz), <code>get()</code> — aynan bitta natija (xato berishi mumkin)</li>
<li>✅ <code>Model.objects</code> — ORM'ga kirish nuqtasi (manager)</li>
<li>✅ models.py o'zgarishi migratsiyasiz haqiqiy bazaga ta'sir qilmaydi</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 4: Models va ORM asoslari
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/models.py - birinchi model
# ─────────────────────────────────────────────────────────────────────

from django.db import models


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    nashr_qilingan = models.BooleanField(default=False)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) Migratsiyalar (terminal buyruqlari, izohda)
# ─────────────────────────────────────────────────────────────────────

# python manage.py makemigrations blog
# python manage.py migrate

# ─────────────────────────────────────────────────────────────────────
# 3) QuerySet - ma'lumot olish
# ─────────────────────────────────────────────────────────────────────

# from blog.models import Post
#
# barcha_postlar = Post.objects.all()
# nashr_qilingan = Post.objects.filter(nashr_qilingan=True)
# bitta_post = Post.objects.get(id=1)
#
# yangi_post = Post.objects.create(
#     sarlavha="Birinchi post",
#     matn="Bu mening birinchi Django postim",
# )

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - migratsiya qilishni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# class Post(models.Model):
#     ...
#     muallif_ismi = models.CharField(max_length=100)  # yangi maydon
#
# # makemigrations/migrate ISHLATILMADI, keyin:
# Post.objects.create(sarlavha="Test", matn="...", muallif_ismi="Olim")
# ❌ OperationalError: no such column: blog_post.muallif_ismi
"""

L4_EX = [
    {
        "title": "Model nimani ifodalaydi?",
        "description": "Django'da models.Model'dan meros olgan Python klassi nimani ifodalaydi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bitta HTML sahifani",
            "Ma'lumotlar bazasidagi bitta jadvalni",
            "Bitta URL yo'nalishini",
            "Bitta view funksiyasini",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Har bir xususiyat (CharField, TextField) — ustunga mos keladi.",
        "explanation": "Har bir models.Model'dan meros olgan klass ma'lumotlar bazasidagi bitta jadvalni ifodalaydi, uning xususiyatlari esa jadval ustunlariga mos keladi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "makemigrations va migrate farqi",
        "description": "makemigrations va migrate buyruqlari orasidagi farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkalasi ham bir xil ishlaydi, ikkalasidan birini ishlatish yetarli",
            "makemigrations o'zgarishni faylga yozadi, migrate esa uni haqiqiy bazada bajaradi",
            "makemigrations bazani o'chiradi, migrate uni tiklaydi",
            "migrate faqat birinchi marta, makemigrations har safar kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Biri \"reja yozadi\", ikkinchisi \"rejani bajaradi\".",
        "explanation": "makemigrations models.py'dagi o'zgarishlarni migration fayliga yozib oladi, migrate esa o'sha faylni haqiqiy ma'lumotlar bazasida bajaradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Yangi post yaratish jarayonini tartiblang",
        "description": "Post.objects.create(sarlavha=\"...\", matn=\"...\") chaqirilganda jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Post.objects.create() chaqiriladi",
            "Yangi Post obyekti xotirada yaratiladi",
            "Obyekt ma'lumotlar bazasiga saqlanadi (INSERT)",
            "Saqlangan Post obyekti qaytariladi",
        ],
        "correct_order": [
            "Post.objects.create() chaqiriladi",
            "Yangi Post obyekti xotirada yaratiladi",
            "Obyekt ma'lumotlar bazasiga saqlanadi (INSERT)",
            "Saqlangan Post obyekti qaytariladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Aynan bitta natija kutuvchi metod",
        "description": "Qaysi QuerySet metodi aynan bitta natija kutadi va agar topilmasa yoki bir nechta topilsa xato beradi? (nomini yozing)",
        "exercise_type": "text_input",
        "expected_answer": "get",
        "hint": "filter()dan farqli, bu metod faqat bittaga mo'ljallangan.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega migratsiya qilinmasa OperationalError chiqadi?",
        "description": (
            "Post modeliga muallif_ismi degan yangi maydon qo'shildi, "
            "lekin makemigrations/migrate ishga tushirilmadi. Nega "
            "keyinchalik Post.objects.create(..., muallif_ismi=\"Olim\") "
            "chaqirilganda \"no such column\" xatosi chiqadi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Python klassi (models.py) va ma'lumotlar bazasidagi haqiqiy "
            "jadval — ikkita alohida narsa. models.py'ga yangi maydon "
            "qo'shish shunchaki Python kodini o'zgartiradi, lekin bu "
            "o'zgarish haqiqiy ma'lumotlar bazasi jadvaliga hali \"yetib "
            "bormagan\" bo'ladi — buning uchun makemigrations (o'zgarishni "
            "reja sifatida yozish) va migrate (rejani bazada bajarish) "
            "ishga tushirilishi shart. Bu qadam bajarilmagani uchun "
            "haqiqiy jadvalda muallif_ismi degan ustun hali mavjud emas, "
            "shuning uchun ma'lumotlar bazasi bunday ustunni topa olmay "
            "xato beradi."
        ),
        "hint": "Python klassidagi o'zgarish avtomatik ravishda haqiqiy bazaga ta'sir qiladimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R1_TEXT = """\
<h2>R1 — 1-4-darslarni takrorlash: Mini blog</h2>

<p>1-4 darslarning hammasini birlashtirib, to'liq ishlaydigan mini blog yasaymiz: Post modeli, migratsiya, routing va template inheritance — hammasi birga.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>Post</code> modeli — <code>sarlavha</code>, <code>matn</code>, <code>yaratilgan_vaqt</code> maydonlari bilan (4-dars)</li>
<li><code>blog/urls.py</code> — ro'yxat (<code>/blog/</code>) va detail (<code>/blog/&lt;int:post_id&gt;/</code>) sahifalari uchun routing (2-dars)</li>
<li><code>base.html</code>'dan meros olgan <code>post_list.html</code> va <code>post_detail.html</code> shablonlari (3-dars)</li>
<li>App to'g'ri <code>INSTALLED_APPS</code>'ga qo'shilgan va migratsiya qilingan bo'lishi kerak (1-dars)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Post modeli</h4>
<p><code>sarlavha</code> (CharField), <code>matn</code> (TextField), <code>yaratilgan_vaqt</code> (DateTimeField, <code>auto_now_add=True</code>) maydonlari bilan <code>Post</code> modelini yarating, so'ng <code>makemigrations</code> + <code>migrate</code> qiling (4-darsdagidek).</p>

<h4>Vazifa 2 — routing</h4>
<p><code>blog/urls.py</code>'da ro'yxat sahifasi (<code>''</code>) va detail sahifasi (<code>'&lt;int:post_id&gt;/'</code>) uchun ikkita <code>path()</code> yozing, ularni bosh <code>urls.py</code>'ga <code>include()</code> orqali ulang (2-darsdagidek).</p>

<h4>Vazifa 3 — view'lar va templates</h4>
<p><code>postlar_royxati</code> view'i <code>Post.objects.all()</code>ni oladi va <code>post_list.html</code>'ni render qiladi; <code>post_detail</code> view'i <code>Post.objects.get(id=post_id)</code>ni oladi va <code>post_detail.html</code>'ni render qiladi. Ikkala shablon ham <code>base.html</code>'dan <code>extends</code> qilishi kerak (3-darsdagidek).</p>

<h4>Vazifa 4 — birlashtirish</h4>
<p>Hamma narsani sinab ko'ring: <code>/blog/</code> — barcha postlar ro'yxatini, <code>/blog/1/</code> — bitta postning to'liq matnini ko'rsatishi kerak.</p>

<h3>🐛 Ataylab qiyin: migratsiyasiz view'ni sinash</h3>
<p>Agar <code>Post</code> modelini yozib, lekin <code>makemigrations</code>/<code>migrate</code>'ni ISHGA TUSHIRMASDAN <code>postlar_royxati</code> view'iga kirsangiz, <code>Post.objects.all()</code> chaqirilganda <strong>OperationalError: no such table: blog_post</strong> xatosiga duch kelasiz — 4-darsda ko'rgan muammoning aynan o'zi, endi to'liq loyihada. To'g'ri tartib: <strong>avval</strong> model yozing, <strong>keyin</strong> darhol migratsiya qiling, va <strong>faqat shundan keyin</strong> view/template'ni sinab ko'ring.</p>

<h3>Boshlang'ich kod</h3>
<pre><code># blog/models.py
from django.db import models

class Post(models.Model):
    # Vazifa 1: sarlavha, matn, yaratilgan_vaqt maydonlarini qo'shing
    pass

# blog/views.py
from django.shortcuts import render
from .models import Post

def postlar_royxati(request):
    # Vazifa 3: Post.objects.all() olib, post_list.html'ni render qiling
    pass

def post_detail(request, post_id):
    # Vazifa 3: Post.objects.get(id=post_id) olib, post_detail.html'ni render qiling
    pass

# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vazifa 2: ikkita path() yozing
]</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code># ─── blog/models.py ───
from django.db import models

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# Terminalda: python manage.py makemigrations blog && python manage.py migrate

# ─── blog/views.py ───
from django.shortcuts import render
from .models import Post

def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})

def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# ─── blog/urls.py ───
from django.urls import path
from . import views

urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),
]

# ─── mysite/urls.py ───
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]

# ─── templates/blog/post_list.html ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li><a href="{% url 'post-detail' post.id %}">{{ post.sarlavha }}</a></li>
#   {% endfor %}
#   </ul>
# {% endblock %}

# ─── templates/blog/post_detail.html ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>{{ post.sarlavha }}</h1>
#   <p>{{ post.matn }}</p>
# {% endblock %}</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 1-4 darslarning hammasi birga: app ro'yxati, model, migratsiya, routing, templates</li>
<li>✅ To'g'ri tartib: model yozish → migratsiya qilish → view/template'ni sinash</li>
<li>✅ <code>{% url 'post-detail' post.id %}</code> — name= orqali dinamik havola yaratish</li>
<li>✅ Migratsiyasiz view'ni sinash "no such table" xatosini beradi</li>
</ul>
"""

R1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 1: Mini blog (1-4-darslar)
# ════════════════════════════════════════════════════════════════════

# ─── blog/models.py ───
from django.db import models


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# Terminalda: python manage.py makemigrations blog && python manage.py migrate

# ─── blog/views.py ───
from django.shortcuts import render


def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# ─── blog/urls.py ───
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.postlar_royxati, name='post-list'),
#     path('<int:post_id>/', views.post_detail, name='post-detail'),
# ]

# ─── templates/blog/post_list.html (izohda) ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li><a href="{% url 'post-detail' post.id %}">{{ post.sarlavha }}</a></li>
#   {% endfor %}
#   </ul>
# {% endblock %}
"""

R1_EX = [
    {
        "title": "To'g'ri ishlash tartibi",
        "description": "Post modelini yozgandan keyin, view'ni sinashdan oldin nima qilish shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Darhol view'ni sinash mumkin, hech narsa qilish shart emas",
            "makemigrations va migrate buyruqlarini ishga tushirish",
            "Faqat serverni qayta ishga tushirish",
            "Post modelini o'chirib qayta yozish",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "4-darsni eslang: Python klass va haqiqiy jadval alohida narsa.",
        "explanation": "Model yozilgandan keyin, haqiqiy ma'lumotlar bazasi jadvalini yaratish uchun makemigrations va migrate ishga tushirilishi shart, aks holda \"no such table\" xatosi chiqadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Template'da dinamik havola yaratish",
        "description": "post_list.html'da har bir post uchun uning detail sahifasiga havola yaratish uchun qaysi yozuv ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "<a href=\"/blog/{{ post.id }}/\">",
            "<a href=\"{% url 'post-detail' post.id %}\">",
            "<a href=\"{{ post-detail }}\">",
            "<a href=\"{% post_detail %}\">",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "2-darsda o'rgangan name= parametrini eslang.",
        "explanation": "{% url 'post-detail' post.id %} — path()ga berilgan name= orqali dinamik havola yaratadi, URL manzili o'zgarsa ham kod ishlayveradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Mini blog so'rovini to'g'ri tartibda joylang",
        "description": "Brauzerda /blog/1/ ochilganda, server ichida bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "mysite/urls.py so'rovni blog/urls.py'ga include() orqali yo'naltiradi",
            "blog/urls.py <int:post_id>/ shablonini topib, post_detail view'ini chaqiradi",
            "post_detail Post.objects.get(id=post_id) orqali ma'lumot oladi",
            "post_detail.html render qilinib, to'liq HTML javob qaytariladi",
        ],
        "correct_order": [
            "mysite/urls.py so'rovni blog/urls.py'ga include() orqali yo'naltiradi",
            "blog/urls.py <int:post_id>/ shablonini topib, post_detail view'ini chaqiradi",
            "post_detail Post.objects.get(id=post_id) orqali ma'lumot oladi",
            "post_detail.html render qilinib, to'liq HTML javob qaytariladi",
        ],
        "hint": "1-4 darslarda o'rgangan barcha qadamlarni ketma-ket eslang.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega app ro'yxati, migratsiya, routing va templates birga ishlatiladi?",
        "description": (
            "Mini blog loyihasida app ro'yxati (1-dars), migratsiya "
            "(4-dars), routing (2-dars) va template inheritance "
            "(3-dars)ni birga qo'llash nima uchun muhim? Ularning har "
            "biri qanday muammoning oldini oladi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "App ro'yxati (INSTALLED_APPS) Django'ga blog app'ini "
            "\"tanishtiradi\" — bo'lmasa, Django uning modellarini ham, "
            "migratsiyalarini ham umuman ko'rmaydi. Migratsiya Python "
            "klassidagi Post modelini haqiqiy ma'lumotlar bazasi "
            "jadvaliga aylantiradi — bo'lmasa \"no such table\" xatosi "
            "chiqadi. Routing (urls.py + include()) brauzerdan kelgan "
            "so'rovni to'g'ri view funksiyasiga yo'naltiradi — bo'lmasa "
            "404 xato beriladi. Template inheritance (extends/block) esa "
            "har bir sahifada bir xil HTML skeletni qayta yozmaslikni "
            "ta'minlaydi. Ularning har biri o'z bosqichida ishlamasa, "
            "keyingi bosqich ham ishlamaydi — shuning uchun barchasi "
            "birga, to'g'ri tartibda kerak."
        ),
        "hint": "Har birini alohida-alohida o'ylang: ular bo'lmasa nima buziladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L5_TEXT = """\
<h2>Django Admin paneli — bir necha qatorda tayyor boshqaruv paneli</h2>

<pre class="mermaid">
flowchart LR
    MODEL["class Post(models.Model)"] --> ADMIN["admin.py: admin.site.register(Post)"]
    ADMIN --> PANEL["/admin/ — avtomatik CRUD interfeys"]
    SUPER["createsuperuser"] --> PANEL
</pre>

<p>Flask'da admin panel kerak bo'lsa, uni <strong>o'zingiz</strong> qo'lda yozishingiz kerak edi (Flask-Admin kabi qo'shimcha kutubxona bilan ham). Django'da esa admin panel <strong>ichki tayyor</strong> &mdash; bor-yo'g'i bir necha qator kod bilan modelni to'liq CRUD interfeysga ega qilasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — superuser yaratish va modelni ro'yxatdan o'tkazish</h4>
<pre><code># Terminalda (bir marta):
python manage.py createsuperuser   # ❗ admin panelga kirish uchun foydalanuvchi yaratadi

# blog/admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)   # ❗ shu bitta qator - Post uchun to'liq CRUD interfeys yaratadi!

# Endi /admin/ manzilida Post'larni ko'rish, qo'shish, o'zgartirish, o'chirish mumkin</code></pre>

<h4>BLOKA 2 — ModelAdmin bilan sozlash</h4>
<pre><code># blog/admin.py
from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt', 'nashr_qilingan')  # ❗ ro'yxatda ko'rinadigan ustunlar
    search_fields = ('sarlavha', 'matn')                              # ❗ qidiruv maydoni ustida qidiriladigan maydonlar
    list_filter = ('nashr_qilingan',)                                 # ❗ o'ng tomondagi filtr paneli

admin.site.register(Post, PostAdmin)   # ❗ endi ModelAdmin bilan birga ro'yxatdan o'tkaziladi</code></pre>

<h4>BLOKA 3 — dekorator sintaksisi (qisqaroq yozuv)</h4>
<pre><code># Yuqoridagi bilan bir xil, lekin dekorator orqali
from django.contrib import admin
from .models import Post

@admin.register(Post)              # ❗ admin.site.register(Post, PostAdmin) bilan bir xil natija
class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt')
    search_fields = ('sarlavha',)</code></pre>

<h3>🐛 Ataylab xato — list_display'da mavjud bo'lmagan maydon nomini yozish</h3>
<pre><code>class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')  # ❌ Post modelida 'muallif' degan maydon YO'Q

admin.site.register(Post, PostAdmin)

# /admin/blog/post/ ochilganda:
# ❌ Xato: PostAdmin.list_display[1], 'muallif' is not a callable, an
#    attribute of 'PostAdmin', or an attribute or method on 'Post'.</code></pre>

<p><strong>Natija:</strong> <code>list_display</code>'dagi har bir nom <strong>albatta</strong> modelning haqiqiy maydoni, uning metodi yoki <code>PostAdmin</code>ning metodi bo'lishi kerak. Modelda mavjud bo'lmagan nom yozilsa, Django admin panelni ochishga <strong>urinishda</strong> (server ishga tushganda emas) xato beradi &mdash; bu odatiy Python <code>AttributeError</code>ga o'xshash muammo, faqat admin panel kontekstida.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. admin.site.register() nima qiladi?</h4>
<p>Bu bitta qator kod berilgan modelga mos <strong>to'liq CRUD interfeys</strong> (ro'yxat ko'rish, qo'shish, tahrirlash, o'chirish) ni avtomatik yaratadi &mdash; hech qanday HTML, view yoki forma yozmasdan.</p>

<h4>2. ModelAdmin nima uchun kerak?</h4>
<p>Standart <code>admin.site.register(Post)</code> juda oddiy ko'rinishni beradi. <code>ModelAdmin</code> klassi orqali bu ko'rinishni <strong>sozlash</strong> mumkin: qaysi ustunlar ro'yxatda ko'rinsin (<code>list_display</code>), qaysi maydonlar bo'yicha qidirish mumkin bo'lsin (<code>search_fields</code>), qanday filtrlar ko'rsatilsin (<code>list_filter</code>).</p>

<h4>3. createsuperuser nima uchun kerak?</h4>
<p>Admin panel &mdash; himoyalangan joy, faqat <strong>autentifikatsiyadan o'tgan</strong> (va odatda <code>is_staff=True</code>/<code>is_superuser=True</code> bo'lgan) foydalanuvchilar kira oladi. <code>createsuperuser</code> buyrug'i shunday to'liq huquqli foydalanuvchi yaratadi.</p>

<h4>4. Dekorator (<code>@admin.register</code>) va oddiy <code>admin.site.register()</code> farqi</h4>
<p>Ikkalasi ham bir xil natijaga olib keladi &mdash; farqi faqat <strong>yozuv uslubi</strong>da: dekorator klassni e'lon qilish bilan bir vaqtda ro'yxatdan o'tkazadi, bu ko'proq "Pythonic" va zamonaviy Django loyihalarida ko'proq ishlatiladi.</p>

<h4>5. Nega list_display'da mavjud bo'lmagan maydon xato beradi?</h4>
<p>Django admin panelni yaratishda <code>list_display</code>'dagi har bir nomni model (yoki <code>ModelAdmin</code>) ichidan <strong>qidiradi</strong>. Agar bunday nom <strong>hech qayerda</strong> topilmasa (na model maydoni, na metod), Django buni xato deb hisoblaydi, chunki ro'yxatda <strong>nima ko'rsatishni</strong> u bilmaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>admin.site.register(Model)</code> — bir qatorda to'liq CRUD interfeys yaratadi</li>
<li>✅ <code>ModelAdmin</code> — <code>list_display</code>, <code>search_fields</code>, <code>list_filter</code> orqali admin ko'rinishini sozlaydi</li>
<li>✅ <code>createsuperuser</code> — admin panelga kirish uchun to'liq huquqli foydalanuvchi yaratadi</li>
<li>✅ <code>@admin.register(Model)</code> — <code>admin.site.register()</code>ning dekorator shakli</li>
<li>✅ <code>list_display</code>'da faqat model/ModelAdmin'da haqiqatan mavjud bo'lgan nomlar ishlatilishi mumkin</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 5: Django Admin paneli
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Superuser yaratish (terminal buyrug'i, izohda)
# ─────────────────────────────────────────────────────────────────────

# python manage.py createsuperuser

# ─────────────────────────────────────────────────────────────────────
# 2) blog/admin.py - oddiy ro'yxatdan o'tkazish
# ─────────────────────────────────────────────────────────────────────

from django.contrib import admin
from .models import Post

# admin.site.register(Post)

# ─────────────────────────────────────────────────────────────────────
# 3) ModelAdmin bilan sozlash
# ─────────────────────────────────────────────────────────────────────


class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt', 'nashr_qilingan')
    search_fields = ('sarlavha', 'matn')
    list_filter = ('nashr_qilingan',)


admin.site.register(Post, PostAdmin)

# ─────────────────────────────────────────────────────────────────────
# 4) Dekorator sintaksisi (izohda, bir xil natija)
# ─────────────────────────────────────────────────────────────────────

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('sarlavha', 'yaratilgan_vaqt')
#     search_fields = ('sarlavha',)

# ─────────────────────────────────────────────────────────────────────
# 5) Ataylab xato - mavjud bo'lmagan maydon (izohda)
# ─────────────────────────────────────────────────────────────────────

# class PostAdminXato(admin.ModelAdmin):
#     list_display = ('sarlavha', 'muallif')  # ❌ Post'da 'muallif' yo'q
# ❌ 'muallif' is not a callable, an attribute of 'PostAdminXato', or
#    an attribute or method on 'Post'.
"""

L5_EX = [
    {
        "title": "admin.site.register() nima qiladi?",
        "description": "admin.site.register(Post) qatori nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Post modeli uchun avtomatik to'liq CRUD admin interfeysi yaratadi",
            "Post modelini o'chirib tashlaydi",
            "Faqat Post'ni ko'rish (read-only) imkonini beradi",
            "Yangi migratsiya yaratadi",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bu bitta qator kod - ko'p ish qiladi.",
        "explanation": "admin.site.register(Post) berilgan model uchun ro'yxat, qo'shish, tahrirlash, o'chirish imkoniyatlarining barchasini o'z ichiga olgan to'liq CRUD interfeysni avtomatik yaratadi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "search_fields nima uchun ishlatiladi?",
        "description": "ModelAdmin'dagi search_fields = ('sarlavha', 'matn') nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat sarlavha va matn maydonlarini ko'rsatadi",
            "Admin panelda shu maydonlar bo'yicha qidirish imkonini beruvchi qidiruv maydonini qo'shadi",
            "Bu maydonlarni o'chirib tashlaydi",
            "Bu maydonlarni readonly qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu admin panelning yuqori qismidagi qidiruv maydoniga tegishli.",
        "explanation": "search_fields admin panelga qidiruv maydoni qo'shadi va ko'rsatilgan maydonlar (sarlavha, matn) bo'yicha qidirish imkonini beradi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Admin panel orqali post qo'shish jarayonini tartiblang",
        "description": "Admin foydalanuvchi /admin/ orqali yangi Post qo'shish jarayonini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "createsuperuser orqali yaratilgan hisob bilan /admin/ ga kirish",
            "Post modeli ro'yxatidan 'Add Post' tugmasi bosiladi",
            "Avtomatik yaratilgan forma to'ldiriladi (sarlavha, matn)",
            "Saqlash bosilganda, yangi Post ma'lumotlar bazasiga yoziladi",
        ],
        "correct_order": [
            "createsuperuser orqali yaratilgan hisob bilan /admin/ ga kirish",
            "Post modeli ro'yxatidan 'Add Post' tugmasi bosiladi",
            "Avtomatik yaratilgan forma to'ldiriladi (sarlavha, matn)",
            "Saqlash bosilganda, yangi Post ma'lumotlar bazasiga yoziladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Admin panelga kirish uchun foydalanuvchi yaratish buyrug'i",
        "description": "Admin panelga kirish uchun to'liq huquqli foydalanuvchi yaratadigan buyruqni yozing.",
        "exercise_type": "text_input",
        "expected_answer": "python manage.py createsuperuser",
        "hint": "manage.py orqali ishga tushiriladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega list_display'da mavjud bo'lmagan maydon xato beradi?",
        "description": (
            "PostAdmin.list_display = ('sarlavha', 'muallif') deb "
            "yozilgan, lekin Post modelida 'muallif' degan maydon yo'q. "
            "Nega /admin/blog/post/ ochilganda Django xato beradi? O'z "
            "so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django admin panelni tayyorlashda list_display ro'yxatidagi "
            "har bir nomni model ichidan (yoki ModelAdmin metodlari "
            "ichidan) qidiradi, chunki ro'yxatda har bir ustun uchun "
            "aynan qaysi qiymatni ko'rsatishni bilishi kerak. "
            "'muallif' nomi na Post modelining maydoni, na PostAdmin'ning "
            "metodi sifatida mavjud emas, shuning uchun Django bu nomga "
            "mos hech qanday qiymat topa olmaydi va admin sahifasini "
            "ochishga urinishda xato beradi — bu oddiy Python "
            "AttributeError'ga o'xshash muammo, faqat admin panel "
            "kontekstida yuz beradi."
        ),
        "hint": "Django list_display'dagi nomni qayerdan qidiradi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L6_TEXT = """\
<h2>Forms va validatsiya — foydalanuvchi ma'lumotini xavfsiz qabul qilish</h2>

<pre class="mermaid">
flowchart LR
    GET["GET so'rov"] --> BOSH["Bo'sh forma ko'rsatiladi"]
    POST["POST so'rov"] --> VALID{"form.is_valid()?"}
    VALID -->|True| SAVE["form.cleaned_data / form.save()"]
    VALID -->|False| ERR["form.errors bilan qayta ko'rsatiladi"]
</pre>

<p>Flask'da forma ma'lumotini <code>request.form</code> orqali qo'lda olib, o'zingiz tekshirar edingiz (yoki Flask-WTF ishlatgan bo'lsangiz). Django'ning <strong>o'z Forms tizimi</strong> bor &mdash; validatsiya, xato xabarlari va hatto HTML forma chiqarishning o'zi ham avtomatik amalga oshadi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — oddiy forms.Form</h4>
<pre><code># blog/forms.py
from django import forms

class KontaktForm(forms.Form):
    ism = forms.CharField(max_length=100)               # ❗ bo'sh bo'lishi mumkin emas (default: required=True)
    email = forms.EmailField()                          # ❗ email formatini avtomatik tekshiradi
    xabar = forms.CharField(widget=forms.Textarea)       # ❗ &lt;textarea&gt; sifatida ko'rsatiladi

# blog/views.py
from django.shortcuts import render
from .forms import KontaktForm

def kontakt(request):
    if request.method == 'POST':
        form = KontaktForm(request.POST)                # ❗ POST ma'lumoti bilan to'ldirilgan forma
        if form.is_valid():                              # ❗ HAMMA validatsiyalarni bir yo'la tekshiradi
            ism = form.cleaned_data['ism']                # ❗ tozalangan, xavfsiz ma'lumot
            # ... email yuborish yoki saqlash ...
            return render(request, 'blog/rahmat.html')
    else:
        form = KontaktForm()                              # ❗ bo'sh forma (GET so'rovda)
    return render(request, 'blog/kontakt.html', {'form': form})</code></pre>

<h4>BLOKA 2 — template'da forma va CSRF token</h4>
<pre><code>{# blog/kontakt.html #}
&lt;form method="post"&gt;
  {% csrf_token %}          {# ❗ MAJBURIY — CSRF hujumidan himoya qiladi #}
  {{ form.as_p }}           {# ❗ formaning barcha maydonlarini &lt;p&gt; teglar bilan chiqaradi #}
  &lt;button type="submit"&gt;Yuborish&lt;/button&gt;
&lt;/form&gt;</code></pre>

<h4>BLOKA 3 — ModelForm: modeldan avtomatik forma</h4>
<pre><code># blog/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):     # ❗ ModelForm - modeldan avtomatik forma yasaydi
    class Meta:
        model = Post
        fields = ['sarlavha', 'matn']  # ❗ faqat shu maydonlar formada bo'ladi

# blog/views.py
def post_yaratish(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()                # ❗ ModelForm'da to'g'ridan-to'g'ri saqlash mumkin!
            return redirect('post-list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})</code></pre>

<h3>🐛 Ataylab xato — {% csrf_token %}ni unutish</h3>
<pre><code>&lt;form method="post"&gt;
  {# {% csrf_token %} yo'q! #}
  {{ form.as_p }}
  &lt;button type="submit"&gt;Yuborish&lt;/button&gt;
&lt;/form&gt;

# Forma yuborilganda:
# ❌ Xato: 403 Forbidden - CSRF verification failed. Request aborted.</code></pre>

<p><strong>Natija:</strong> Django <strong>standart holda</strong> barcha POST so'rovlarni CSRF (Cross-Site Request Forgery) hujumidan himoya qiladi. Har bir HTML forma <code>{% csrf_token %}</code> orqali yashirin token chiqarishi <strong>shart</strong> &mdash; server shu tokenni tekshiradi. Agar token yo'q bo'lsa, Django so'rovni <strong>ishonchsiz</strong> deb hisoblab, uni 403 xatosi bilan rad etadi &mdash; bu xavfsizlik uchun qasddan qilingan qattiq talab.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. is_valid() nima qiladi?</h4>
<p><code>form.is_valid()</code> formadagi <strong>barcha</strong> maydonlarning validatsiya qoidalarini (masalan, <code>EmailField</code> uchun email formati, <code>required=True</code> bo'lgan maydonlar bo'shligi) bir yo'la tekshiradi va <code>True</code>/<code>False</code> qaytaradi. Agar <code>False</code> bo'lsa, xatolar <code>form.errors</code>'da to'planadi.</p>

<h4>2. cleaned_data nima uchun kerak?</h4>
<p><code>form.cleaned_data</code> &mdash; validatsiyadan <strong>muvaffaqiyatli o'tgan</strong>, to'g'ri turga (masalan <code>EmailField</code> uchun string, <code>IntegerField</code> uchun int) o'tkazilgan, <strong>xavfsiz</strong> ma'lumot. Xom <code>request.POST</code>'dan farqli, bu ma'lumotga ishonish mumkin.</p>

<h4>3. forms.Form va ModelForm orasidagi farq</h4>
<p><code>forms.Form</code> &mdash; har qanday forma uchun (masalan, kontakt formasi, model bilan bog'liq bo'lmagan forma). <code>ModelForm</code> &mdash; mavjud modeldan (masalan <code>Post</code>) <strong>avtomatik</strong> forma maydonlarini yasaydi va <code>form.save()</code> orqali to'g'ridan-to'g'ri ma'lumotlar bazasiga saqlash imkonini beradi.</p>

<h4>4. CSRF token nima uchun kerak?</h4>
<p>CSRF hujumida yomon niyatli sayt foydalanuvchi nomidan (uning bilmasdan) sizning saytingizga so'rov yuborishga harakat qiladi. <code>{% csrf_token %}</code> har bir foydalanuvchi sessiyasi uchun noyob, taxmin qilib bo'lmaydigan token chiqaradi &mdash; server bu tokenni tekshirib, so'rov <strong>haqiqatan</strong> sizning saytingizdagi formadan kelganini tasdiqlaydi.</p>

<h4>5. Nega csrf_token'siz forma 403 xato beradi?</h4>
<p>Django xavfsizlik nuqtai nazaridan <strong>"default deny"</strong> yondashuvini qo'llaydi: agar POST so'rovda to'g'ri CSRF token bo'lmasa, bu so'rov <strong>ishonchsiz</strong> (balki hujum) deb hisoblanadi va serverga <strong>yetib bormasdan</strong> rad etiladi. Bu dasturchini majburiy ravishda xavfsizlik choralarini ko'rishga undaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>form.is_valid()</code> — barcha validatsiya qoidalarini bir yo'la tekshiradi</li>
<li>✅ <code>form.cleaned_data</code> — validatsiyadan o'tgan, xavfsiz ma'lumot</li>
<li>✅ <code>forms.Form</code> — har qanday forma, <code>ModelForm</code> — modeldan avtomatik forma + <code>save()</code></li>
<li>✅ <code>{% csrf_token %}</code> — har bir POST formada MAJBURIY, CSRF hujumidan himoya qiladi</li>
<li>✅ Token bo'lmasa, Django so'rovni 403 xatosi bilan rad etadi</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 6: Forms va validatsiya
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/forms.py - oddiy forms.Form
# ─────────────────────────────────────────────────────────────────────

from django import forms


class KontaktForm(forms.Form):
    ism = forms.CharField(max_length=100)
    email = forms.EmailField()
    xabar = forms.CharField(widget=forms.Textarea)

# ─────────────────────────────────────────────────────────────────────
# 2) blog/views.py - forma bilan ishlash
# ─────────────────────────────────────────────────────────────────────

from django.shortcuts import render


def kontakt(request):
    if request.method == 'POST':
        form = KontaktForm(request.POST)
        if form.is_valid():
            ism = form.cleaned_data['ism']
            return render(request, 'blog/rahmat.html')
    else:
        form = KontaktForm()
    return render(request, 'blog/kontakt.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# 3) blog/kontakt.html (izohda)
# ─────────────────────────────────────────────────────────────────────

# <form method="post">
#   {% csrf_token %}
#   {{ form.as_p }}
#   <button type="submit">Yuborish</button>
# </form>

# ─────────────────────────────────────────────────────────────────────
# 4) ModelForm - modeldan avtomatik forma
# ─────────────────────────────────────────────────────────────────────

# from .models import Post
#
# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['sarlavha', 'matn']
#
# def post_yaratish(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('post-list')
#     else:
#         form = PostForm()
#     return render(request, 'blog/post_form.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# 5) Ataylab xato - {% csrf_token %}ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# <form method="post">
#   {# {% csrf_token %} yo'q! #}
#   {{ form.as_p }}
# </form>
# ❌ 403 Forbidden - CSRF verification failed. Request aborted.
"""

L6_EX = [
    {
        "title": "is_valid() nima qiladi?",
        "description": "form.is_valid() metodi nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Formani ma'lumotlar bazasiga saqlaydi",
            "Barcha maydonlarning validatsiya qoidalarini bir yo'la tekshirib, True/False qaytaradi",
            "Faqat forma bo'shligini tekshiradi",
            "HTML formani yaratadi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu tekshiruv natijasini boolean sifatida qaytaradi.",
        "explanation": "form.is_valid() barcha maydonlarning validatsiya qoidalarini (required, EmailField formati va h.k.) bir yo'la tekshiradi va True/False qaytaradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "forms.Form va ModelForm farqi",
        "description": "forms.Form va ModelForm orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ular bir xil, faqat nomi boshqa",
            "ModelForm mavjud modeldan avtomatik maydon yasaydi va save() imkonini beradi, forms.Form esa mustaqil",
            "forms.Form faqat GET so'rovlar uchun",
            "ModelForm CSRF himoyasini o'chiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bittasi modelga bog'langan, ikkinchisi mustaqil.",
        "explanation": "ModelForm mavjud modeldan (masalan Post) avtomatik forma maydonlarini yasaydi va form.save() orqali to'g'ridan-to'g'ri saqlash imkonini beradi. forms.Form esa modeldan mustaqil, har qanday forma uchun ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Forma yuborish jarayonini tartiblang",
        "description": "Foydalanuvchi KontaktForm'ni to'ldirib yuborganda (POST) bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi formani to'ldirib, 'Yuborish' tugmasini bosadi",
            "form = KontaktForm(request.POST) - forma POST ma'lumoti bilan to'ldiriladi",
            "form.is_valid() barcha maydonlarni tekshiradi",
            "Agar True bo'lsa, form.cleaned_data orqali xavfsiz ma'lumot olinadi",
        ],
        "correct_order": [
            "Foydalanuvchi formani to'ldirib, 'Yuborish' tugmasini bosadi",
            "form = KontaktForm(request.POST) - forma POST ma'lumoti bilan to'ldiriladi",
            "form.is_valid() barcha maydonlarni tekshiradi",
            "Agar True bo'lsa, form.cleaned_data orqali xavfsiz ma'lumot olinadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "CSRF himoyasi uchun majburiy teg",
        "description": "Har bir POST HTML formada CSRF himoyasi uchun qaysi tegni yozish shart? (aynan shu tegni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "{% csrf_token %}",
        "hint": "Bu forma ichida, submit tugmasidan oldin yoziladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega csrf_token'siz forma 403 xato beradi?",
        "description": (
            "Agar HTML formada {% csrf_token %} yozilmagan bo'lsa, "
            "forma yuborilganda nega Django \"403 Forbidden - CSRF "
            "verification failed\" xatosini beradi? Bu qanday hujumdan "
            "himoya qiladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django xavfsizlik uchun \"default deny\" (standart rad "
            "etish) yondashuvini qo'llaydi: har bir POST so'rovda "
            "haqiqiy, sessiyaga xos CSRF token bo'lishi shart. Bu token "
            "Cross-Site Request Forgery (CSRF) hujumidan himoya qiladi "
            "— bunda yomon niyatli boshqa sayt foydalanuvchi nomidan, "
            "uning bilmasdan, sizning saytingizga so'rov yuborishga "
            "harakat qiladi. Agar {% csrf_token %} yozilmagan bo'lsa, "
            "forma to'g'ri tokenni yubormaydi, va Django bu so'rovni "
            "ishonchsiz (potentsial hujum) deb hisoblab, uni serverga "
            "yetkazmasdan 403 xatosi bilan rad etadi."
        ),
        "hint": "CSRF nima degani va u qanday hujumdan himoya qiladi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L7_TEXT = """\
<h2>ORM chuqurroq — jadvallar orasidagi bog'lanishlar</h2>

<pre class="mermaid">
flowchart LR
    AUTHOR["Author"] -->|ForeignKey - 1 ga ko'p| POST["Post"]
    POST -->|ManyToMany - ko'pga ko'p| TAG["Tag"]
    POST -->|post.muallif| AUTHOR
    AUTHOR -->|muallif.post_set / muallif.postlar| POST
</pre>

<p>Haqiqiy loyihalarda jadvallar bir-biriga <strong>bog'liq</strong> bo'ladi — bitta muallifning ko'p posti, bitta postning ko'p tegi bo'ladi. Django ORM bu bog'lanishlarni <code>ForeignKey</code> va <code>ManyToManyField</code> orqali ifodalaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ForeignKey (1 ga ko'p bog'lanish)</h4>
<pre><code># blog/models.py
from django.db import models

class Author(models.Model):
    ism = models.CharField(max_length=100)

    def __str__(self):
        return self.ism

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(                    # ❗ bitta muallifning KO'P posti bo'lishi mumkin
        Author,
        on_delete=models.CASCADE,                    # ❗ muallif o'chirilsa, uning postlari HAM o'chadi
        related_name='postlar',                       # ❗ teskari tomondan murojaat qilish nomi
    )

# Foydalanish:
muallif = Author.objects.get(id=1)
muallif.postlar.all()          # ❗ related_name orqali - shu muallifning barcha postlari
post = Post.objects.get(id=1)
post.muallif.ism               # ❗ to'g'ridan-to'g'ri - postning muallifi</code></pre>

<h4>BLOKA 2 — ManyToMany (ko'pga ko'p bog'lanish)</h4>
<pre><code># blog/models.py
class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    # ... boshqa maydonlar ...
    teglar = models.ManyToManyField(Tag, related_name='postlar')  # ❗ bitta post KO'P tegga, bitta teg KO'P postga ega bo'lishi mumkin

# Foydalanish:
post = Post.objects.get(id=1)
post.teglar.add(tag1, tag2)     # ❗ teg qo'shish
post.teglar.all()               # ❗ shu postning barcha teglari

tag = Tag.objects.get(nomi='Django')
tag.postlar.all()               # ❗ related_name orqali - shu tegga ega barcha postlar</code></pre>

<h4>BLOKA 3 — filter chaining va select_related</h4>
<pre><code># Zanjir bilan filtrlash - bog'langan jadval maydoni bo'yicha qidirish
Post.objects.filter(muallif__ism='Olim')              # ❗ '__' - bog'langan jadvalga "o'tish"
Post.objects.filter(teglar__nomi='Django')             # ❗ ManyToMany orqali ham ishlaydi

# select_related - N+1 muammosining oldini oladi (SQL JOIN qiladi)
postlar = Post.objects.select_related('muallif').all()  # ❗ bitta so'rovda muallifni ham oladi
for post in postlar:
    print(post.muallif.ism)     # ✅ har bir iteratsiyada YANGI so'rov YO'Q</code></pre>

<h3>🐛 Ataylab xato — select_related'siz N+1 muammosi</h3>
<pre><code># select_related ISHLATILMASA:
postlar = Post.objects.all()          # 1 ta so'rov - barcha postlarni oladi
for post in postlar:
    print(post.muallif.ism)           # ❌ HAR BIR post uchun ALOHIDA so'rov!

# Natijada: 100 ta post bo'lsa - 1 (postlar) + 100 (har biri uchun muallif) = 101 ta SQL so'rov!
# Bu "N+1 muammosi" deb ataladi va katta ma'lumotlar bazasida saytni SEKINLASHTIRADI</code></pre>

<p><strong>Natija:</strong> <code>ForeignKey</code> maydoniga (<code>post.muallif</code>) har safar murojaat qilganda, agar oldindan <code>select_related</code> qilinmagan bo'lsa, Django <strong>alohida SQL so'rov</strong> yuboradi. 100 ta post uchun sikl ichida bu 100 ta qo'shimcha so'rovga olib keladi — bu "N+1 muammosi" deb ataladi va ishlash tezligiga <strong>jiddiy</strong> ta'sir qiladi. <code>select_related</code> esa SQL <code>JOIN</code> orqali hammasini <strong>bitta</strong> so'rovda oladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. ForeignKey qachon ishlatiladi?</h4>
<p><code>ForeignKey</code> &mdash; "1 ga ko'p" (one-to-many) bog'lanish uchun: bitta <code>Author</code>ning ko'p <code>Post</code>i bo'lishi mumkin, lekin har bir <code>Post</code>ning faqat bitta <code>Author</code>i bor. <code>on_delete=models.CASCADE</code> &mdash; muallif o'chirilganda, uning barcha postlari ham avtomatik o'chishini bildiradi.</p>

<h4>2. ManyToManyField qachon ishlatiladi?</h4>
<p><code>ManyToManyField</code> &mdash; "ko'pga ko'p" (many-to-many) bog'lanish uchun: bitta <code>Post</code> bir nechta <code>Tag</code>ga, va bitta <code>Tag</code> bir nechta <code>Post</code>ga tegishli bo'lishi mumkin. Django buning uchun orqa fonda alohida "oraliq jadval" yaratadi.</p>

<h4>3. related_name nima uchun kerak?</h4>
<p><code>related_name</code> &mdash; bog'lanishning <strong>teskari tomonidan</strong> murojaat qilish uchun nom beradi (masalan <code>muallif.postlar.all()</code>). Agar <code>related_name</code> berilmasa, Django standart holda <code>post_set</code> kabi avtomatik nom beradi, lekin aniq nom berish kodni o'qishni osonlashtiradi.</p>

<h4>4. Filter chaining (<code>__</code>) qanday ishlaydi?</h4>
<p><code>filter(muallif__ism='Olim')</code>dagi ikki pastki chiziq (<code>__</code>) Django ORM'ga "bog'langan jadvalga o'tib, shu yerdagi maydon bo'yicha filtrlash" kerakligini bildiradi. Bu SQL <code>JOIN</code>ni qo'lda yozmasdan amalga oshiradi.</p>

<h4>5. select_related nima uchun kerak?</h4>
<p>Standart holda, <code>ForeignKey</code> maydoniga murojaat har safar <strong>alohida</strong> SQL so'rov yuboradi (lazy loading). <code>select_related('muallif')</code> Django'ga oldindan SQL <code>JOIN</code> orqali bog'langan ma'lumotni <strong>bitta</strong> so'rovda olishni buyuradi — bu N+1 muammosining oldini oladi va ishlashni sezilarli tezlashtiradi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>ForeignKey</code> — "1 ga ko'p" bog'lanish, <code>on_delete</code> muallif o'chirilganda nima bo'lishini belgilaydi</li>
<li>✅ <code>ManyToManyField</code> — "ko'pga ko'p" bog'lanish (masalan post-teg)</li>
<li>✅ <code>related_name</code> — bog'lanishning teskari tomonidan murojaat qilish nomi</li>
<li>✅ <code>filter(bog'lanish__maydon=...)</code> — bog'langan jadval bo'yicha filtrlash</li>
<li>✅ <code>select_related()</code> — N+1 muammosining oldini olib, SQL JOIN orqali bitta so'rovda ma'lumot oladi</li>
</ul>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 7: ORM chuqurroq - querysets va bog'lanishlar
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) ForeignKey (1 ga ko'p)
# ─────────────────────────────────────────────────────────────────────

from django.db import models


class Author(models.Model):
    ism = models.CharField(max_length=100)

    def __str__(self):
        return self.ism


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─────────────────────────────────────────────────────────────────────
# 2) Foydalanish (izohda)
# ─────────────────────────────────────────────────────────────────────

# muallif = Author.objects.get(id=1)
# muallif.postlar.all()
# post = Post.objects.get(id=1)
# post.muallif.ism
#
# post.teglar.add(tag1, tag2)
# post.teglar.all()

# ─────────────────────────────────────────────────────────────────────
# 3) Filter chaining va select_related
# ─────────────────────────────────────────────────────────────────────

# Post.objects.filter(muallif__ism='Olim')
# Post.objects.filter(teglar__nomi='Django')
#
# postlar = Post.objects.select_related('muallif').all()
# for post in postlar:
#     print(post.muallif.ism)

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - select_related'siz N+1 muammosi (izohda)
# ─────────────────────────────────────────────────────────────────────

# postlar = Post.objects.all()          # 1 ta so'rov
# for post in postlar:
#     print(post.muallif.ism)           # ❌ har bir post uchun alohida so'rov!
# # 100 ta post = 101 ta SQL so'rov (N+1 muammosi)
"""

L7_EX = [
    {
        "title": "ForeignKey qachon ishlatiladi?",
        "description": "ForeignKey qanday bog'lanish turi uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ko'pga ko'p bog'lanish uchun",
            "1 ga ko'p bog'lanish uchun (bitta Author, ko'p Post)",
            "Faqat bitta-bittaga bog'lanish uchun",
            "Hech qanday bog'lanish uchun emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bitta muallifning ko'p posti bo'lishi mumkin, lekin har bir post bitta muallifga tegishli.",
        "explanation": "ForeignKey \"1 ga ko'p\" bog'lanish uchun ishlatiladi: bitta Author'ning ko'p Post'i bo'lishi mumkin, lekin har bir Post'ning faqat bitta Author'i bor.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "select_related nima uchun ishlatiladi?",
        "description": "Post.objects.select_related('muallif').all() nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat muallif maydoni bo'lgan postlarni filtrlash uchun",
            "N+1 muammosining oldini olib, bog'langan ma'lumotni bitta SQL JOIN so'rovida olish uchun",
            "Muallif modelini o'chirish uchun",
            "Postlarni tasodifiy tartibda saralash uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu ishlashni tezlashtirish uchun ishlatiladi.",
        "explanation": "select_related() SQL JOIN orqali bog'langan ma'lumotni (masalan muallif) bitta so'rovda oladi, bu har bir post uchun alohida so'rov yuborilishining (N+1 muammosi) oldini oladi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "N+1 muammosi yuzaga kelish jarayonini tartiblang",
        "description": "select_related ishlatilmagan holda Post.objects.all() siklida N+1 muammosi qanday yuzaga kelishini tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Post.objects.all() chaqiriladi - 1 ta SQL so'rov barcha postlarni oladi",
            "for post in postlar sikli boshlanadi",
            "Har bir iteratsiyada post.muallif.ism chaqiriladi",
            "Har safar ALOHIDA SQL so'rov yuboriladi - jami N+1 ta so'rov",
        ],
        "correct_order": [
            "Post.objects.all() chaqiriladi - 1 ta SQL so'rov barcha postlarni oladi",
            "for post in postlar sikli boshlanadi",
            "Har bir iteratsiyada post.muallif.ism chaqiriladi",
            "Har safar ALOHIDA SQL so'rov yuboriladi - jami N+1 ta so'rov",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Bog'lanishning teskari tomonidan murojaat qilish nomi",
        "description": "ForeignKey yoki ManyToManyField'da bog'lanishning teskari tomonidan (masalan muallif.postlar.all()) murojaat qilish uchun ishlatiladigan parametr nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "related_name",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega select_related'siz N+1 muammosi yuzaga keladi?",
        "description": (
            "Post.objects.all() chaqirilib, keyin sikl ichida har bir "
            "post uchun post.muallif.ism o'qilsa (select_related "
            "ishlatilmasdan), nega bu 100 ta post uchun 101 ta SQL "
            "so'rovga olib keladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Standart holda, ForeignKey maydoniga (post.muallif) har "
            "safar murojaat qilinganda, Django \"lazy loading\" "
            "printsipi bo'yicha ishlaydi — ya'ni bog'langan ma'lumotni "
            "oldindan emas, faqat aynan shu maydonga murojaat qilingan "
            "paytda alohida SQL so'rov yuborib oladi. Post.objects.all() "
            "1 ta so'rov bilan barcha postlarni oladi, lekin sikl "
            "ichida har bir post uchun post.muallif.ism chaqirilganda, "
            "har birida ALOHIDA so'rov yuboriladi. 100 ta post uchun bu "
            "100 ta qo'shimcha so'rov, jami 1 (postlar) + 100 (har bir "
            "muallif) = 101 ta SQL so'rov degani — aynan shuning uchun "
            "bu \"N+1 muammosi\" deb ataladi va katta ma'lumotlar "
            "bazasida saytni sezilarli sekinlashtiradi."
        ),
        "hint": "ForeignKey maydoniga murojaat qilinganda Django qachon SQL so'rov yuboradi — oldindanmi, yoki har safar alohida?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


R2_TEXT = """\
<h2>R2 — 5-7-darslarni takrorlash: Forms + Relationships mini-loyiha</h2>

<p>5-7 darslarni birlashtirib, <code>Tag</code> bilan bog'langan postlarni admin panel va forma orqali boshqarish imkoniyatini qo'shamiz: admin sozlash, ModelForm va ManyToMany bog'lanish — hammasi birga.</p>

<h3>Loyihaning maqsadi</h3>
<ul>
<li><code>Tag</code> modeli va uni <code>Post</code>ga <code>ManyToManyField</code> orqali bog'lash (7-dars)</li>
<li><code>PostAdmin</code>'da <code>list_display</code>, <code>search_fields</code> sozlangan bo'lishi (5-dars)</li>
<li><code>PostForm</code> (ModelForm) orqali post yaratish, formada <code>teglar</code> maydoni ham bo'lishi (6-dars)</li>
<li>Yangi post yaratilganda teglarni <strong>to'g'ri</strong> saqlash (ManyToMany'ning maxsus qoidasi)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Tag modeli va bog'lanish</h4>
<p><code>Tag</code> modelini (<code>nomi</code> maydoni bilan) yarating, <code>Post</code>ga <code>teglar = models.ManyToManyField(Tag)</code> qo'shing, migratsiya qiling (7-darsdagidek).</p>

<h4>Vazifa 2 — admin sozlash</h4>
<p><code>PostAdmin</code>'da <code>list_display = ('sarlavha', 'muallif')</code> va <code>search_fields = ('sarlavha',)</code> qo'shing; <code>Tag</code>ni ham oddiy <code>admin.site.register(Tag)</code> bilan ro'yxatdan o'tkazing (5-darsdagidek).</p>

<h4>Vazifa 3 — PostForm (ModelForm)</h4>
<p><code>fields = ['sarlavha', 'matn', 'teglar']</code> bilan <code>PostForm</code> yarating — <code>ModelForm</code> <code>ManyToManyField</code>ni ham avtomatik forma maydoniga aylantiradi (6-darsdagidek).</p>

<h4>Vazifa 4 — view'da to'g'ri saqlash</h4>
<p><code>post_yaratish</code> view'ida <code>form.save()</code>ni chaqiring va bu <code>ManyToManyField</code>ni ham to'g'ri saqlashini tekshiring (Django'ning <code>ModelForm.save()</code>'i buni avtomatik uddalaydi).</p>

<h3>🐛 Ataylab qiyin: ManyToMany'ni saqlashdan oldin belgilash</h3>
<p>Agar siz <code>ModelForm.save()</code>dan foydalanmasdan, <strong>qo'lda</strong> post yaratmoqchi bo'lsangiz, quyidagi xato tuzoqqa tushishingiz mumkin:</p>
<pre><code>post = Post(sarlavha="Test", matn="...", muallif=muallif)
post.teglar.set([tag1, tag2])  # ❌ Xato: post hali saqlanmagan (id yo'q)!
post.save()

# ❌ ValueError: "&lt;Post: Test&gt;" needs to have a value for field "id"
#    before this many-to-many relationship can be used.</code></pre>
<p><strong>Natija:</strong> <code>ManyToManyField</code> orqa fonda alohida "oraliq jadval"da saqlanadi, va bu jadvalga yozish uchun <strong>ikkala tomonning ham</strong> (bu holda <code>Post</code>ning) <code>id</code>si <strong>allaqachon</strong> mavjud bo'lishi kerak. Shuning uchun to'g'ri tartib: <strong>avval</strong> <code>post.save()</code> (id beriladi), <strong>keyingina</strong> <code>post.teglar.set(...)</code>. Django'ning <code>ModelForm.save()</code>'i esa buni <strong>ichkarida to'g'ri tartibda</strong> avtomatik bajaradi — shuning uchun ModelForm ishlatish qo'lda yozishdan xavfsizroq.</p>

<h3>Boshlang'ich kod</h3>
<pre><code># blog/models.py
class Tag(models.Model):
    # Vazifa 1: nomi maydonini qo'shing
    pass

class Post(models.Model):
    # ... mavjud maydonlar ...
    # Vazifa 1: teglar = models.ManyToManyField(Tag) qo'shing
    pass

# blog/forms.py
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Vazifa 3: fields ro'yxatiga 'teglar'ni ham qo'shing
        fields = ['sarlavha', 'matn']</code></pre>

<h3>Yechim</h3>
<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code># ─── blog/models.py ───
class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─── blog/admin.py ───
from django.contrib import admin
from .models import Post, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')
    search_fields = ('sarlavha',)

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

# ─── blog/forms.py ───
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['sarlavha', 'matn', 'teglar']

# ─── blog/views.py ───
def post_yaratish(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()   # ❗ ModelForm avval Post'ni saqlaydi, keyin teglarni to'g'ri bog'laydi
            return redirect('post-list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 5-7 darslarning hammasi birga: admin sozlash, ModelForm, ManyToMany bog'lanish</li>
<li>✅ ModelForm ManyToManyField'ni ham avtomatik forma maydoniga aylantiradi</li>
<li>✅ ManyToMany'ni belgilashdan oldin obyekt saqlangan (id bor) bo'lishi shart</li>
<li>✅ form.save() to'g'ri tartibni (avval save, keyin ManyToMany) avtomatik ta'minlaydi</li>
</ul>
"""

R2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 2: Forms + Relationships (5-7-darslar)
# ════════════════════════════════════════════════════════════════════

# ─── blog/models.py ───
from django.db import models


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

# class Post(models.Model):
#     sarlavha = models.CharField(max_length=200)
#     matn = models.TextField()
#     muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
#     teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─── blog/admin.py ───
from django.contrib import admin


class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')
    search_fields = ('sarlavha',)

# admin.site.register(Post, PostAdmin)
# admin.site.register(Tag)

# ─── blog/forms.py ───
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        # model = Post
        fields = ['sarlavha', 'matn', 'teglar']

# ─── blog/views.py ───
# def post_yaratish(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('post-list')
#     else:
#         form = PostForm()
#     return render(request, 'blog/post_form.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# Ataylab qiyin - ManyToMany'ni saqlashdan oldin belgilash (izohda)
# ─────────────────────────────────────────────────────────────────────

# post = Post(sarlavha="Test", matn="...", muallif=muallif)
# post.teglar.set([tag1, tag2])  # ❌ post hali saqlanmagan!
# post.save()
# ❌ ValueError: needs to have a value for field "id" before this
#    many-to-many relationship can be used.
"""

R2_EX = [
    {
        "title": "ModelForm va ManyToManyField",
        "description": "PostForm.Meta.fields ro'yxatida 'teglar' (ManyToManyField) bo'lsa, ModelForm bu maydon bilan nima qiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Xato beradi, ManyToManyField formada ishlatib bo'lmaydi",
            "Uni ham avtomatik forma maydoniga aylantiradi",
            "Uni e'tiborsiz qoldiradi",
            "Faqat o'qish uchun (readonly) qiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "ModelForm modeldagi ko'p turdagi maydonlar bilan ishlay oladi.",
        "explanation": "ModelForm ManyToManyField'ni ham avtomatik forma maydoniga (odatda ko'p tanlovli ro'yxat sifatida) aylantiradi va form.save() uni to'g'ri tartibda saqlaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "Nega qo'lda ManyToMany belgilash xato beradi?",
        "description": "post = Post(...); post.teglar.set([tag1, tag2]); post.save() ketma-ketligi nega xato beradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "tag1, tag2 obyektlari mavjud emas",
            "post hali saqlanmagan (id yo'q), ManyToMany esa ikkala tomonning id'sini talab qiladi",
            "teglar maydoni umuman noto'g'ri yozilgan",
            "set() metodi Django'da mavjud emas",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "ManyToMany orqa fonda alohida jadvalda saqlanadi.",
        "explanation": "ManyToManyField orqa fonda alohida oraliq jadvalda saqlanadi, va bu jadvalga yozish uchun Post'ning id'si allaqachon mavjud bo'lishi shart — shuning uchun avval save(), keyin teglar.set() qilinishi kerak.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "form.save() ichki ishlash tartibini joylang",
        "description": "PostForm(ModelForm)'da form.save() chaqirilganda, teglarni to'g'ri saqlash uchun ichki jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "form.is_valid() cleaned_data'ni tayyorlaydi",
            "Yangi Post obyekti yaratiladi va DARHOL saqlanadi (id beriladi)",
            "Endi Post'ning id'si mavjud",
            "teglar ManyToMany bog'lanishi endi xavfsiz saqlanadi",
        ],
        "correct_order": [
            "form.is_valid() cleaned_data'ni tayyorlaydi",
            "Yangi Post obyekti yaratiladi va DARHOL saqlanadi (id beriladi)",
            "Endi Post'ning id'si mavjud",
            "teglar ManyToMany bog'lanishi endi xavfsiz saqlanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega ModelForm qo'lda yozishdan xavfsizroq?",
        "description": (
            "Post yaratishda ManyToManyField (teglar) bilan ishlashda, "
            "nega form.save() (ModelForm) qo'lda post.teglar.set() "
            "chaqirishdan ko'ra xavfsizroq? O'z so'zlaringiz bilan "
            "tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "ManyToManyField'ni belgilash uchun obyektning (Post) id'si "
            "allaqachon mavjud bo'lishi shart, chunki bu bog'lanish "
            "orqa fonda alohida oraliq jadvalda saqlanadi va bu jadvalga "
            "yozish uchun ikkala tomonning id'si kerak. Agar dasturchi "
            "buni qo'lda yozsa, save() va teglar.set() ni noto'g'ri "
            "tartibda chaqirib qo'yish xavfi bor (masalan avval set(), "
            "keyin save()), bu esa ValueError xatosiga olib keladi. "
            "Django'ning ModelForm.save() metodi esa bu tartibni "
            "(avval obyektni saqlash, keyin ManyToMany bog'lanishlarni "
            "belgilash) ichkarida avtomatik va to'g'ri bajaradi, shuning "
            "uchun dasturchi bu tartib xatosiga yo'l qo'yish xavfidan "
            "xoli bo'ladi."
        ),
        "hint": "ManyToMany'ni belgilash uchun obyektning nimasi allaqachon mavjud bo'lishi kerak?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L8_TEXT = """\
<h2>Autentifikatsiya — django.contrib.auth bilan tayyor tizim</h2>

<pre class="mermaid">
flowchart LR
    REG["Ro'yxatdan o'tish"] --> LOGIN["Kirish (login)"]
    LOGIN --> SESSION["Session cookie yaratiladi"]
    SESSION --> PROTECTED["@login_required bilan himoyalangan sahifa"]
    PROTECTED -->|kirmagan| REDIRECT["login sahifasiga yo'naltiriladi"]
</pre>

<p>Flask'da autentifikatsiyani Flask-Login kabi qo'shimcha kutubxona bilan qo'lda qurgan bo'lardingiz. Django'da <code>django.contrib.auth</code> &mdash; <strong>ichki, tayyor</strong> autentifikatsiya tizimi: foydalanuvchi modeli, login/logout, parolni xavfsiz saqlash (hashing) va ruxsatlar — hammasi <strong>allaqachon</strong> mavjud.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ro'yxatdan o'tish va kirish</h4>
<pre><code># blog/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

def royxatdan_otish(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)         # ❗ Django'ning tayyor ro'yxatdan o'tish formasi
        if form.is_valid():
            user = form.save()                          # ❗ parol AVTOMATIK hash qilinib saqlanadi
            login(request, user)                         # ❗ darhol kirish sessiyasini boshlaydi
            return redirect('post-list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/royxat.html', {'form': form})

def kirish(request):
    if request.method == 'POST':
        username = request.POST['username']
        parol = request.POST['password']
        user = authenticate(request, username=username, password=parol)  # ❗ tekshiradi, lekin hali kirmaydi
        if user is not None:
            login(request, user)                          # ❗ endigina session yaratiladi
            return redirect('post-list')
    return render(request, 'blog/kirish.html')</code></pre>

<h4>BLOKA 2 — chiqish va himoyalangan sahifalar</h4>
<pre><code># blog/views.py
from django.contrib.auth.decorators import login_required

def chiqish(request):
    logout(request)                    # ❗ sessiyani tugatadi
    return redirect('post-list')

@login_required                        # ❗ faqat autentifikatsiyadan o'tgan foydalanuvchi kira oladi
def post_yaratish(request):
    # ... forma bilan ishlash ...
    pass
# login_required(login_url='/kirish/') deb ham yozish mumkin - qayerga yo'naltirishni belgilash uchun</code></pre>

<h4>BLOKA 3 — template'da request.user</h4>
<pre><code>{# Har qanday template'da request.user avtomatik mavjud #}
{% if user.is_authenticated %}
  &lt;p&gt;Salom, {{ user.username }}!&lt;/p&gt;
  &lt;a href="{% url 'chiqish' %}"&gt;Chiqish&lt;/a&gt;
{% else %}
  &lt;a href="{% url 'kirish' %}"&gt;Kirish&lt;/a&gt;
{% endif %}</code></pre>

<h3>🐛 Ataylab xato — login_required'siz himoyalanishi kerak bo'lgan view</h3>
<pre><code># @login_required DEKORATORI YO'Q holda:
def post_yaratish(request):
    # ... post yaratish mantiqi ...
    pass

# Natijada: kirmagan (anonim) foydalanuvchi ham /blog/yaratish/ manziliga
# to'g'ridan-to'g'ri kirib, post yarata oladi - bu XAVFSIZLIK MUAMMOSI!</code></pre>

<p><strong>Natija:</strong> Django autentifikatsiya tizimini o'rnatish (foydalanuvchi modeli, login/logout) <strong>hali</strong> sahifalarni <strong>avtomatik himoya qilmaydi</strong>. Har bir himoyalanishi kerak bo'lgan view'ga <code>@login_required</code> dekoratorini <strong>aniq</strong> qo'shish kerak. Bu qo'shilmasa, kirmagan foydalanuvchi ham o'sha view'ga to'g'ridan-to'g'ri (URL orqali) kirib, harakatlarni bajarishi mumkin — bu jiddiy xavfsizlik zaifligi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. UserCreationForm nima?</h4>
<p>Django'ning <code>django.contrib.auth.forms</code>'dagi <strong>tayyor</strong> formasi &mdash; username, parol va parolni tasdiqlash maydonlarini o'z ichiga oladi, parolni <strong>avtomatik hash</strong> qilib (xavfsiz shaklda) saqlaydi.</p>

<h4>2. authenticate() va login() orasidagi farq</h4>
<p><code>authenticate()</code> &mdash; berilgan username/parol <strong>to'g'rimi</strong> yoki yo'qligini tekshiradi va agar to'g'ri bo'lsa <code>User</code> obyektini qaytaradi (hech qanday session yaratmaydi). <code>login()</code> &mdash; berilgan <code>User</code> uchun <strong>haqiqatan</strong> session (kirish holatini) boshlaydi. Ular odatda ketma-ket, birga ishlatiladi.</p>

<h4>3. @login_required nima qiladi?</h4>
<p>Bu dekorator view funksiyasini <strong>o'rab oladi</strong>: agar foydalanuvchi autentifikatsiyadan o'tmagan bo'lsa, view'ning o'zi ishga tushmasdan, foydalanuvchi avtomatik login sahifasiga yo'naltiriladi. Bu har bir view ichida qo'lda <code>if not request.user.is_authenticated</code> tekshiruvi yozishning oldini oladi.</p>

<h4>4. request.user nima?</h4>
<p>Django har bir so'rovga <code>request.user</code>ni <strong>avtomatik</strong> qo'shadi &mdash; agar foydalanuvchi kirgan bo'lsa, haqiqiy <code>User</code> obyekti, aks holda <code>AnonymousUser</code> (maxsus "kirmagan foydalanuvchi" obyekti) bo'ladi. Shuning uchun <code>{% if user.is_authenticated %}</code> har doim xavfsiz ishlaydi.</p>

<h4>5. Nega login_required qo'shilmasa xavfsizlik muammosi bo'ladi?</h4>
<p>Django autentifikatsiya tizimi <strong>"opt-in"</strong> tarzda ishlaydi &mdash; ya'ni <strong>siz</strong> qaysi view'ni himoyalashni <strong>aniq</strong> belgilashingiz kerak. Agar <code>@login_required</code> qo'shilmasa, Django bu view'ni "ochiq" deb hisoblaydi va kirmagan foydalanuvchi ham unga to'g'ridan-to'g'ri (URL orqali) murojaat qilib, harakatni bajarishi mumkin bo'lib qoladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>UserCreationForm</code> — tayyor ro'yxatdan o'tish formasi, parolni avtomatik hash qiladi</li>
<li>✅ <code>authenticate()</code> — tekshiradi, <code>login()</code> — session boshlaydi</li>
<li>✅ <code>@login_required</code> — kirmagan foydalanuvchini avtomatik login sahifasiga yo'naltiradi</li>
<li>✅ <code>request.user</code> — har doim mavjud: haqiqiy User yoki AnonymousUser</li>
<li>✅ Himoya "opt-in" — har bir himoyalanishi kerak bo'lgan view'ga aniq qo'shilishi shart</li>
</ul>
"""

L8_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 8: Autentifikatsiya
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - ro'yxatdan o'tish va kirish
# ─────────────────────────────────────────────────────────────────────

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect


def royxatdan_otish(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post-list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/royxat.html', {'form': form})


def kirish(request):
    if request.method == 'POST':
        username = request.POST['username']
        parol = request.POST['password']
        user = authenticate(request, username=username, password=parol)
        if user is not None:
            login(request, user)
            return redirect('post-list')
    return render(request, 'blog/kirish.html')

# ─────────────────────────────────────────────────────────────────────
# 2) Chiqish va himoyalangan view
# ─────────────────────────────────────────────────────────────────────

from django.contrib.auth.decorators import login_required


def chiqish(request):
    logout(request)
    return redirect('post-list')


@login_required
def post_yaratish(request):
    pass

# ─────────────────────────────────────────────────────────────────────
# 3) templates/blog/base.html (izohda) - request.user
# ─────────────────────────────────────────────────────────────────────

# {% if user.is_authenticated %}
#   <p>Salom, {{ user.username }}!</p>
#   <a href="{% url 'chiqish' %}">Chiqish</a>
# {% else %}
#   <a href="{% url 'kirish' %}">Kirish</a>
# {% endif %}

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - login_required'siz himoyalanishi kerak bo'lgan view (izohda)
# ─────────────────────────────────────────────────────────────────────

# def post_yaratish_xato(request):
#     # @login_required YO'Q!
#     pass
# # Kirmagan foydalanuvchi ham to'g'ridan-to'g'ri kirib, post yarata oladi!
"""

L8_EX = [
    {
        "title": "UserCreationForm nima qiladi?",
        "description": "django.contrib.auth.forms'dagi UserCreationForm nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat parolni ko'rsatish uchun",
            "Tayyor ro'yxatdan o'tish formasi, parolni avtomatik hash qilib saqlaydi",
            "Foydalanuvchini o'chirish uchun",
            "Faqat admin panelda ishlatiladi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu Django'ning tayyor formalaridan biri.",
        "explanation": "UserCreationForm — username, parol va parolni tasdiqlash maydonlarini o'z ichiga olgan tayyor forma bo'lib, parolni avtomatik xavfsiz (hash) shaklda saqlaydi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": "authenticate() va login() farqi",
        "description": "authenticate() va login() funksiyalari orasidagi asosiy farq nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ular bir xil ishlaydi",
            "authenticate() username/parolni tekshiradi (session yaratmaydi), login() esa session boshlaydi",
            "authenticate() faqat admin uchun, login() oddiy foydalanuvchi uchun",
            "login() foydalanuvchini o'chiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bittasi \"tekshiradi\", ikkinchisi \"kirishni boshlaydi\".",
        "explanation": "authenticate() berilgan ma'lumotlar to'g'riligini tekshirib User obyektini qaytaradi, lekin session yaratmaydi. login() esa haqiqatan session (kirish holatini) boshlaydi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Kirish jarayonini tartiblang",
        "description": "Foydalanuvchi login formasini to'ldirib yuborganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi username va parolni yuboradi",
            "authenticate() ma'lumotlar to'g'riligini tekshiradi",
            "Agar to'g'ri bo'lsa, login() chaqirilib session boshlanadi",
            "Foydalanuvchi post-list sahifasiga yo'naltiriladi",
        ],
        "correct_order": [
            "Foydalanuvchi username va parolni yuboradi",
            "authenticate() ma'lumotlar to'g'riligini tekshiradi",
            "Agar to'g'ri bo'lsa, login() chaqirilib session boshlanadi",
            "Foydalanuvchi post-list sahifasiga yo'naltiriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "View'ni himoyalash uchun dekorator",
        "description": "Faqat autentifikatsiyadan o'tgan foydalanuvchi kirishi uchun view funksiyasi ustiga qaysi dekorator qo'yiladi? (aynan shu dekoratorni yozing)",
        "exercise_type": "text_input",
        "expected_answer": "@login_required",
        "hint": "django.contrib.auth.decorators'dan import qilinadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega login_required qo'shilmasa xavfsizlik muammosi bo'ladi?",
        "description": (
            "post_yaratish view'iga @login_required dekoratori "
            "qo'shilmagan holda, nega kirmagan (anonim) foydalanuvchi "
            "ham to'g'ridan-to'g'ri /blog/yaratish/ manziliga kirib, "
            "post yarata oladi? O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Django autentifikatsiya tizimi \"opt-in\" tarzida ishlaydi "
            "— ya'ni foydalanuvchi tizimini o'rnatish (login/logout, "
            "User modeli) hali hech qanday view'ni avtomatik "
            "himoyalamaydi. Har bir himoyalanishi kerak bo'lgan view'ga "
            "dasturchi aniq @login_required dekoratorini qo'shishi "
            "shart. Agar bu qo'shilmasa, Django o'sha view'ni \"ochiq\" "
            "deb hisoblaydi — foydalanuvchi kirgan yoki kirmaganidan "
            "qat'i nazar, view ishga tushaveradi, shuning uchun anonim "
            "foydalanuvchi ham URL orqali to'g'ridan-to'g'ri murojaat "
            "qilib, post yaratish kabi harakatlarni bajarishi mumkin "
            "bo'lib qoladi — bu jiddiy xavfsizlik zaifligi."
        ),
        "hint": "Django autentifikatsiya tizimini o'rnatish avtomatik ravishda barcha view'larni himoyalaydimi?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L9_TEXT = """\
<h2>Class-Based Views (CBV) — takrorlanadigan view'larni klass orqali qisqartirish</h2>

<pre class="mermaid">
flowchart LR
    FBV["Function-based view (ko'p takrorlangan kod)"] -->|refactor| CBV["ListView/DetailView/CreateView"]
    CBV --> URLS["path(..., PostListView.as_view())"]
</pre>

<p>1-8 darslarda barcha view'larni <strong>function-based</strong> (oddiy funksiya) sifatida yozdik. Ammo "ro'yxatni ko'rsatish", "bittasini ko'rsatish", "yaratish/tahrirlash/o'chirish" kabi vazifalar deyarli <strong>har doim bir xil</strong> tuzilishga ega. Django bu uchun tayyor <strong>Class-Based Views (CBV)</strong> beradi — ular ko'p takrorlanadigan kodni qisqartiradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ListView va DetailView</h4>
<pre><code># blog/views.py
from django.views.generic import ListView, DetailView
from .models import Post

class PostListView(ListView):          # ❗ Post.objects.all()ni avtomatik oladi va render qiladi
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'postlar'    # ❗ template'da ishlatiladigan o'zgaruvchi nomi

class PostDetailView(DetailView):      # ❗ Post.objects.get(pk=...)ni avtomatik oladi
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

# blog/urls.py
from django.urls import path
from .views import PostListView, PostDetailView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),          # ❗ .as_view() MAJBURIY!
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]</code></pre>

<h4>BLOKA 2 — CreateView, UpdateView, DeleteView</h4>
<pre><code># blog/views.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class PostCreateView(LoginRequiredMixin, CreateView):   # ❗ Mixin - login_required'ga o'xshash himoya
    model = Post
    fields = ['sarlavha', 'matn']       # ❗ ModelForm avtomatik yaratiladi (6-darsdagidek)
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')  # ❗ muvaffaqiyatdan keyin qayerga yo'naltirish

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')</code></pre>

<h4>BLOKA 3 — CBV va function-based view solishtiruvi</h4>
<pre><code># Function-based (4-darsdagi kabi) - 5 qator:
def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})

# CBV bilan xuddi shu natija - kamroq takrorlanadigan kod:
class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
# CBV o'zi avtomatik: Post.objects.all() + render() + template_name (model nomidan chiqarilgan)</code></pre>

<h3>🐛 Ataylab xato — urls.py'da .as_view()ni unutish</h3>
<pre><code># blog/urls.py
urlpatterns = [
    path('', PostListView, name='post-list'),   # ❌ .as_view() YO'Q!
]

# Server ishga tushirilganda yoki sahifa ochilganda:
# ❌ Xato: View function did not return an HttpResponse object. It
#    returned None instead. (yoki TypeError turidagi xato)</code></pre>

<p><strong>Natija:</strong> Django'ning routing tizimi (<code>urls.py</code>) faqat <strong>funksiyalarni</strong> chaqira oladi (chunki har bir view — HTTP so'rovni qabul qilib, javob qaytaradigan chaqiriladigan narsa). CBV esa <strong>klass</strong>, funksiya emas. <code>.as_view()</code> metodi klassni <strong>chaqiriladigan funksiyaga aylantiradi</strong> — bu qadam tashlab ketilsa, Django klassni to'g'ridan-to'g'ri chaqirishga urinadi va bu kutilgan natijani bermaydi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. CBV nima uchun kerak?</h4>
<p>"Ro'yxatni ko'rsatish", "bittasini ko'rsatish", "yaratish/tahrirlash/o'chirish" kabi vazifalar har bir modelda deyarli <strong>bir xil</strong> tarzda takrorlanadi. CBV bu umumiy naqshni <code>ListView</code>, <code>DetailView</code>, <code>CreateView</code> kabi tayyor klasslar sifatida beradi — dasturchi faqat <code>model</code>, <code>fields</code> kabi kichik sozlamalarni belgilaydi.</p>

<h4>2. .as_view() nima uchun majburiy?</h4>
<p>Django routing tizimi view sifatida <strong>chaqiriladigan funksiya</strong>ni kutadi. <code>PostListView.as_view()</code> klassdan har bir so'rov uchun yangi obyekt yaratib, so'rovni to'g'ri metodga (masalan <code>get()</code>) yo'naltiruvchi <strong>funksiya</strong> qaytaradi.</p>

<h4>3. context_object_name nima uchun kerak?</h4>
<p>Standart holda CBV context'ga <code>object_list</code> (ListView uchun) yoki <code>object</code> (DetailView uchun) kabi umumiy nom beradi. <code>context_object_name</code> bu nomni <strong>o'zgartirish</strong> imkonini beradi (masalan <code>postlar</code>), shunda template kod o'qilishi osonroq bo'ladi.</p>

<h4>4. LoginRequiredMixin nima?</h4>
<p>Bu — CBV uchun <code>@login_required</code>ning <strong>klass versiyasi</strong>: <code>class PostCreateView(LoginRequiredMixin, CreateView)</code> deb yozilsa, faqat autentifikatsiyadan o'tgan foydalanuvchilar bu view'ga kira oladi, aks holda login sahifasiga yo'naltiriladi.</p>

<h4>5. Nega .as_view()siz xato chiqadi?</h4>
<p>Klassning o'zi (masalan <code>PostListView</code>) &mdash; HTTP so'rovni qanday qayta ishlashni <strong>bilmaydigan</strong> oddiy Python klassi. <code>.as_view()</code> uni har bir so'rov kelganda yangi obyekt yaratib, so'rovni mos metodga yo'naltiradigan <strong>haqiqiy funksiyaga</strong> aylantiradi. Bu qadamsiz, <code>urls.py</code> klassning o'zini chaqirishga urinadi, bu esa kutilgan <code>HttpResponse</code>ni bermaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>ListView</code>/<code>DetailView</code> — ro'yxat/bitta obyektni ko'rsatishning tayyor CBV'lari</li>
<li>✅ <code>CreateView</code>/<code>UpdateView</code>/<code>DeleteView</code> — CRUD amallarining tayyor CBV'lari</li>
<li>✅ Har bir CBV <code>urls.py</code>'da <code>.as_view()</code> orqali funksiyaga aylantirilishi <strong>shart</strong></li>
<li>✅ <code>LoginRequiredMixin</code> — CBV uchun <code>@login_required</code>ning klass ekvivalenti</li>
<li>✅ CBV takrorlanadigan kodni kamaytiradi, lekin murakkab, o'ziga xos mantiq uchun function-based view ko'proq moslashuvchan</li>
</ul>
"""

L9_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 9: Class-Based Views (CBV)
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) ListView va DetailView
# ─────────────────────────────────────────────────────────────────────

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class PostListView(ListView):
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'


class PostDetailView(DetailView):
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

# ─────────────────────────────────────────────────────────────────────
# 2) CreateView, UpdateView, DeleteView
# ─────────────────────────────────────────────────────────────────────


class PostCreateView(LoginRequiredMixin, CreateView):
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

# ─────────────────────────────────────────────────────────────────────
# 3) blog/urls.py (izohda)
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from .views import PostListView, PostDetailView
#
# urlpatterns = [
#     path('', PostListView.as_view(), name='post-list'),
#     path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - .as_view()ni unutish (izohda)
# ─────────────────────────────────────────────────────────────────────

# urlpatterns = [
#     path('', PostListView, name='post-list'),   # ❌ .as_view() YO'Q!
# ]
# ❌ View function did not return an HttpResponse object. It returned
#    None instead.
"""

L9_EX = [
    {
        "title": "CBV nima uchun ishlatiladi?",
        "description": "Class-Based Views (CBV) asosan nima uchun ishlatiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Function-based view'lardan sekinroq ishlashi uchun",
            "Ro'yxat ko'rsatish, CRUD kabi takrorlanadigan naqshlarni tayyor klass sifatida qisqartirish uchun",
            "Faqat admin panelda ishlatish uchun",
            "Templates'ni butunlay bekor qilish uchun",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Ko'p view'lar bir xil tuzilishga ega bo'ladi.",
        "explanation": "CBV ro'yxat ko'rsatish, bitta obyektni ko'rsatish, yaratish/tahrirlash/o'chirish kabi deyarli har doim bir xil bo'lgan naqshlarni tayyor klasslar sifatida taqdim etib, takrorlanadigan kodni kamaytiradi.",
        "difficulty_level": "Easy",
        "points": 2,
    },
    {
        "title": ".as_view() nima uchun majburiy?",
        "description": "urls.py'da PostListView.as_view() yozishning sababi nima?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bu shunchaki tasodifiy konventsiya, majburiy emas",
            "Django routing faqat chaqiriladigan funksiyani kutadi, .as_view() klassni funksiyaga aylantiradi",
            "as_view() modelni migratsiya qiladi",
            "as_view() CSRF himoyasini o'chiradi",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Klassning o'zi HTTP so'rovni qanday qayta ishlashni bilmaydi.",
        "explanation": "Django routing tizimi view sifatida chaqiriladigan funksiyani kutadi. .as_view() klassdan har bir so'rov uchun to'g'ri metodga yo'naltiruvchi funksiya yaratadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "PostCreateView ishlash jarayonini tartiblang",
        "description": "Foydalanuvchi PostCreateView orqali yangi post yaratganda bo'ladigan jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "LoginRequiredMixin foydalanuvchi kirganligini tekshiradi",
            "GET so'rovda avtomatik yaratilgan ModelForm ko'rsatiladi",
            "Foydalanuvchi formani to'ldirib POST yuboradi",
            "Forma to'g'ri bo'lsa, post saqlanadi va success_url'ga yo'naltiriladi",
        ],
        "correct_order": [
            "LoginRequiredMixin foydalanuvchi kirganligini tekshiradi",
            "GET so'rovda avtomatik yaratilgan ModelForm ko'rsatiladi",
            "Foydalanuvchi formani to'ldirib POST yuboradi",
            "Forma to'g'ri bo'lsa, post saqlanadi va success_url'ga yo'naltiriladi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "@login_required'ning CBV uchun klass ekvivalenti",
        "description": "CBV uchun @login_required'ga o'xshash himoyani ta'minlaydigan mixin klassining nomini yozing.",
        "exercise_type": "text_input",
        "expected_answer": "LoginRequiredMixin",
        "hint": "django.contrib.auth.mixins'dan import qilinadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega .as_view()siz xato chiqadi?",
        "description": (
            "urls.py'da path('', PostListView, name='post-list') deb "
            "(ya'ni .as_view()siz) yozilsa, nega Django xato beradi? "
            "O'z so'zlaringiz bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "PostListView'ning o'zi — HTTP so'rovni qanday qayta "
            "ishlashni bilmaydigan, oddiy Python klassi. Django routing "
            "tizimi esa view sifatida faqat chaqiriladigan (callable) "
            "funksiyani kutadi, chunki har bir so'rov kelganda o'sha "
            "funksiya chaqiriladi va HttpResponse qaytarishi kutiladi. "
            ".as_view() metodi klassni shu talabga mos, haqiqiy "
            "chaqiriladigan funksiyaga aylantiradi — u har bir so'rov "
            "uchun yangi klass obyektini yaratib, so'rovni mos metodga "
            "(masalan GET uchun get()) yo'naltiradi. Bu qadam tashlab "
            "ketilsa, Django klassning o'zini chaqirishga urinadi, bu "
            "esa kutilgan HttpResponse'ni bermaydi va xato chiqaradi."
        ),
        "hint": "Klassning o'zi va .as_view() natijasi — ikkalasi ham \"chaqiriladigan\" narsami?",
        "difficulty_level": "Hard",
        "points": 4,
    },
]


L10_TEXT = """\
<h2>CAPSTONE — to'liq Django blog loyihasi</h2>

<pre class="mermaid">
flowchart TB
    MODEL["Post: muallif (FK) + teglar (M2M)"] --> ADMIN["PostAdmin - ro'yxat/qidiruv"]
    MODEL --> CBV["PostListView / PostDetailView / PostCreateView"]
    AUTH["LoginRequiredMixin"] --> CBV
    CBV -->|form_valid override| SETAUTHOR["muallif = request.user avtomatik belgilanadi"]
</pre>

<p>1-9 darslarda o'rgangan hamma narsani &mdash; models va bog'lanishlar, admin, forms, autentifikatsiya, CBV &mdash; birlashtirib, haqiqiy kichik loyiha quramiz: <strong>kirgan foydalanuvchi post yozadigan blog</strong>. Bu &mdash; kursning yakuniy sinovi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Post modeli, muallif avtomatik belgilanishi kerak</h4>
<pre><code># blog/models.py
from django.db import models
from django.contrib.auth.models import User            # ❗ Django'ning tayyor User modeli

class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postlar')  # ❗ MUHIM: majburiy maydon
    teglar = models.ManyToManyField(Tag, related_name='postlar', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha</code></pre>

<h4>BLOKA 2 — CBV: ro'yxat, detail, va yaratish (auth bilan)</h4>
<pre><code># blog/views.py
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Post

class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):   # ❗ faqat kirgan foydalanuvchi kira oladi
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']              # ❗ 'muallif' FORMADA YO'Q - qo'lda belgilanadi!
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):                          # ❗ ASOSIY qism: saqlashdan oldin muallifni belgilash
        form.instance.muallif = self.request.user        # ❗ request.user - 8-darsdan
        return super().form_valid(form)</code></pre>

<h4>BLOKA 3 — admin va urls.py birlashtirish</h4>
<pre><code># blog/admin.py
from django.contrib import admin
from .models import Post, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif', 'yaratilgan_vaqt')
    search_fields = ('sarlavha', 'matn')

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

# blog/urls.py
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('yaratish/', PostCreateView.as_view(), name='post-create'),
]</code></pre>

<h3>🐛 Ataylab xato — form_valid()ni override qilishni unutish</h3>
<pre><code># form_valid() METODI YOZILMASA:
class PostCreateViewXato(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']   # 'muallif' formada yo'q, hech qayerda ham belgilanmagan!
    template_name = 'blog/post_form.html'

# Foydalanuvchi formani to'ldirib yuborganda:
# ❌ Xato: IntegrityError: NOT NULL constraint failed: blog_post.muallif_id
# (chunki Post.muallif majburiy ForeignKey, lekin hech qanday qiymat berilmagan)</code></pre>

<p><strong>Natija:</strong> <code>fields</code> ro'yxatida <code>muallif</code>ni <strong>ataylab</strong> qoldirmadik &mdash; chunki foydalanuvchi o'zi "men muallifman" deb yozishi <strong>xavfsiz emas</strong> (u boshqa birovning nomidan post yozishi mumkin bo'lardi). Buning o'rniga <code>muallif</code> <strong>avtomatik</strong>, joriy kirgan foydalanuvchidan (<code>request.user</code>) olinishi kerak. Agar <code>form_valid()</code> override qilinmasa, Django <code>muallif</code> uchun hech qanday qiymat topa olmay, ma'lumotlar bazasiga saqlashda xato beradi (chunki bu maydon <code>NOT NULL</code>).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Nega muallif fields ro'yxatiga qo'shilmagan?</h4>
<p>Agar <code>muallif</code> formada bo'lganida, foydalanuvchi HTML orqali <strong>istalgan</strong> muallif ID'sini yuborishi mumkin bo'lardi &mdash; bu boshqa birovning nomidan post yozish imkonini beradi (xavfsizlik zaifligi). Shuning uchun <code>muallif</code> hech qachon foydalanuvchi kiritadigan maydon bo'lmasligi kerak &mdash; u <strong>serverda</strong>, ishonchli manbadan (<code>request.user</code>) belgilanadi.</p>

<h4>2. form_valid() nima uchun override qilinadi?</h4>
<p><code>form_valid()</code> &mdash; forma validatsiyadan <strong>muvaffaqiyatli o'tgandan keyin</strong>, lekin obyekt <strong>saqlanishidan oldin</strong> chaqiriladigan metod. Uni override qilib, <code>form.instance.muallif = self.request.user</code> deb yozish orqali, saqlanishidan oldin obyektga qo'shimcha (formada yo'q) qiymat qo'shish mumkin.</p>

<h4>3. LoginRequiredMixin va form_valid() qanday birga ishlaydi?</h4>
<p><code>LoginRequiredMixin</code> foydalanuvchi <strong>umuman kirmagan bo'lsa</strong>, view'ga kirishning o'zini bloklaydi (login sahifasiga yo'naltiradi). <code>form_valid()</code> ichidagi <code>self.request.user</code> esa, foydalanuvchi <strong>allaqachon kirganligi</strong> tasdiqlangani uchun, har doim haqiqiy <code>User</code> obyektini beradi &mdash; ikkalasi birga ishlab, xavfsiz va to'g'ri natija beradi.</p>

<h4>4. blank=True nima uchun teglar maydoniga qo'shilgan?</h4>
<p><code>ManyToManyField(..., blank=True)</code> &mdash; formada bu maydonni <strong>to'ldirish shart emasligini</strong> bildiradi (post teglarsiz ham yaratilishi mumkin). Bu <code>null=True</code>dan farqli &mdash; <code>ManyToMany</code> uchun <code>null=True</code> odatda ma'nosiz, chunki bog'lanish alohida jadvalda saqlanadi.</p>

<h4>5. Nega bu loyiha 1-9 darslarning yakuniy sinovi hisoblanadi?</h4>
<p>Bu yerda: model va <code>ForeignKey</code>/<code>ManyToMany</code> bog'lanishlar (4, 7-darslar), admin sozlash (5-dars), forma va uning cheklovlari (6-dars), autentifikatsiya va <code>request.user</code> (8-dars), CBV va uni override qilish (9-dars) &mdash; barchasi <strong>bitta, real xavfsizlik talabini</strong> (foydalanuvchi o'z nomidan emas, balki boshqa birovning nomidan post yoza olmasligi) hal qilish uchun birlashadi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Xavfsizlik uchun muhim maydonlar (masalan muallif) formaga qo'shilmasligi, server tomonida belgilanishi kerak</li>
<li>✅ <code>form_valid()</code> override qilib, saqlanishidan oldin obyektga qo'shimcha qiymat qo'shish mumkin</li>
<li>✅ <code>LoginRequiredMixin</code> + <code>form_valid()</code> birgalikda xavfsiz "joriy foydalanuvchi muallif" naqshini beradi</li>
<li>✅ <code>ManyToManyField(blank=True)</code> — formada majburiy bo'lmagan bog'lanish</li>
<li>✅ Real loyihada models, admin, forms, auth, CBV bir-biri bilan chambarchas bog'liq ishlaydi</li>
</ul>
"""

L10_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 10 (CAPSTONE): To'liq Django blog loyihasi
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/models.py
# ─────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) blog/views.py - CBV + auth + form_valid()
# ─────────────────────────────────────────────────────────────────────

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.muallif = self.request.user
        return super().form_valid(form)

# ─────────────────────────────────────────────────────────────────────
# 3) blog/admin.py va urls.py (izohda)
# ─────────────────────────────────────────────────────────────────────

# class PostAdmin(admin.ModelAdmin):
#     list_display = ('sarlavha', 'muallif', 'yaratilgan_vaqt')
#     search_fields = ('sarlavha', 'matn')
#
# urlpatterns = [
#     path('', PostListView.as_view(), name='post-list'),
#     path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
#     path('yaratish/', PostCreateView.as_view(), name='post-create'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Ataylab xato - form_valid()ni yozmaslik (izohda)
# ─────────────────────────────────────────────────────────────────────

# class PostCreateViewXato(LoginRequiredMixin, CreateView):
#     model = Post
#     fields = ['sarlavha', 'matn', 'teglar']
#     template_name = 'blog/post_form.html'
#     # form_valid() YO'Q - muallif hech qayerda belgilanmagan!
# ❌ IntegrityError: NOT NULL constraint failed: blog_post.muallif_id
"""

L10_EX = [
    {
        "title": "Nega muallif fields ro'yxatiga qo'shilmagan?",
        "description": "PostCreateView.fields = ['sarlavha', 'matn', 'teglar'] ro'yxatida nega 'muallif' YO'Q?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki Post modelida muallif maydoni umuman yo'q",
            "Chunki muallif foydalanuvchi tomonidan emas, server tomonida request.user orqali xavfsiz belgilanishi kerak",
            "Chunki ForeignKey maydonlarni formada ko'rsatib bo'lmaydi",
            "Bu shunchaki tasodifiy, ahamiyati yo'q",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Agar foydalanuvchi o'zi muallif ID'sini yuborsa, nima xavf tug'ilardi?",
        "explanation": "Agar muallif formada bo'lganida, foydalanuvchi istalgan muallif ID'sini yuborib, boshqa birovning nomidan post yoza olardi. Shuning uchun muallif server tomonida, request.user orqali xavfsiz belgilanadi.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "form_valid() qachon chaqiriladi?",
        "description": "CreateView'da form_valid() metodi qachon chaqiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Forma validatsiyadan o'tmasdan oldin",
            "Forma validatsiyadan muvaffaqiyatli o'tgandan keyin, lekin obyekt saqlanishidan oldin",
            "Foydalanuvchi sahifani ochganda (GET so'rovda)",
            "Faqat xato yuz berganda",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Bu obyektni saqlashdan oldingi \"oxirgi bosqich\".",
        "explanation": "form_valid() forma validatsiyadan muvaffaqiyatli o'tgandan keyin, lekin obyekt ma'lumotlar bazasiga saqlanishidan oldin chaqiriladi — shu yerda qo'shimcha qiymatlarni (masalan muallifni) belgilash mumkin.",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Post yaratish jarayonini tartiblang",
        "description": "PostCreateView orqali kirgan foydalanuvchi yangi post yaratganda to'liq jarayonni tartiblang.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "LoginRequiredMixin foydalanuvchi kirganligini tekshiradi",
            "Foydalanuvchi formani (sarlavha, matn, teglar) to'ldirib yuboradi",
            "form_valid() ichida form.instance.muallif = self.request.user belgilanadi",
            "super().form_valid(form) chaqirilib, Post to'liq ma'lumot bilan saqlanadi",
        ],
        "correct_order": [
            "LoginRequiredMixin foydalanuvchi kirganligini tekshiradi",
            "Foydalanuvchi formani (sarlavha, matn, teglar) to'ldirib yuboradi",
            "form_valid() ichida form.instance.muallif = self.request.user belgilanadi",
            "super().form_valid(form) chaqirilib, Post to'liq ma'lumot bilan saqlanadi",
        ],
        "hint": "",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "ManyToMany maydonini formada majburiy emas qilish",
        "description": "ManyToManyField'ni formada to'ldirish shart emasligini bildiruvchi parametrni yozing (masalan: blank=True).",
        "exercise_type": "text_input",
        "expected_answer": "blank=True",
        "hint": "",
        "difficulty_level": "Medium",
        "points": 3,
    },
    {
        "title": "Nega form_valid() yozilmasa IntegrityError chiqadi?",
        "description": (
            "PostCreateViewXato'da form_valid() metodi yozilmagan va "
            "fields ro'yxatida 'muallif' yo'q. Foydalanuvchi formani "
            "to'ldirib yuborganda, nega \"NOT NULL constraint failed: "
            "blog_post.muallif_id\" xatosi chiqadi? O'z so'zlaringiz "
            "bilan tushuntiring."
        ),
        "exercise_type": "text_input",
        "expected_answer": (
            "Post modelida muallif ForeignKey sifatida majburiy "
            "(NOT NULL) maydon qilib belgilangan, lekin fields "
            "ro'yxatida yo'qligi sababli forma hech qachon muallif uchun "
            "qiymat bermaydi. Agar form_valid() override qilinmasa, "
            "hech kim (na forma, na kod) muallif maydoniga biror qiymat "
            "bermaydi. CreateView Post obyektini ma'lumotlar bazasiga "
            "saqlashga uringanda, muallif_id ustuni bo'sh (None) "
            "qolganini ko'radi, lekin bu ustun NOT NULL sifatida "
            "belgilangani uchun ma'lumotlar bazasi bu yozuvni rad etadi "
            "va IntegrityError xatosini beradi."
        ),
        "hint": "Agar hech kim muallif qiymatini bermasa, u nima bo'lib qoladi, va bazada bu ustun qanday cheklovga ega?",
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
