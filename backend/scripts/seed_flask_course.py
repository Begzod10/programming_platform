"""Seed the "Python Flask" course (11 lessons + ~55 exercises).

Usage:
    cd backend
    python scripts/seed_flask_course.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.
Run again after editing LESSONS to re-create from scratch — but first delete
the existing row manually (we don't auto-clobber existing content).

Target audience: students who know Python basics but haven't built a web app.
Language: Uzbek content with Russian section labels (matches HTML CSS course).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "Python Flask",
    "description": (
        "Python asoslarini biladiganlar uchun Flask web frameworkiga "
        "to'liq kirish: routing, shablonlar, formalar, ma'lumotlar bazasi, "
        "JSON API va production'ga deploy qilish."
    ),
    "instructor_id": 2,           # same teacher as HTML CSS course
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 200,
    "is_active": True,
    "is_published": True,
}


# ─────────────────────────────────────────────────────────────────────────────
# Lesson content — each entry produces one lessons row + N exercises rows
# and a sections_json that mirrors the HTML CSS course shape.
#
# Section convention (matches existing course):
#   order 0: text     label=Текст        html
#   order 1: code     label=Код          code + lang
#   order 2: video    label=Видео        videoUrl
#   order 3: exercise label=Упражнения   exercises (mirror of DB rows)
# ─────────────────────────────────────────────────────────────────────────────

L1_TEXT = """\
<h2>Flaskga kirish</h2>

<pre class="mermaid">
flowchart LR
    A["Brauzer"] -->|GET /| B["Flask app"]
    B --> C["@app.route handler"]
    C --> D["return Salom dunyo"]
    D -->|HTTP 200| A
    B -.->|debug=True| R["auto reload"]
</pre>

<p>Flask — bu Pythonda web ilovalar yozish uchun ishlatiladigan eng mashhur <strong>mikro</strong> framework. "Mikro" degani — Flask sizga faqat eng kerakli narsalarni beradi: URL routing, request/response cycle va template engine. Qolganini (ma'lumotlar bazasi, autentifikatsiya, formalar) o'zingiz tanlab qo'shasiz.</p>
<h3>Nima uchun aynan Flask?</h3>
<ul>
<li><strong>Sodda</strong>: 5 qatorlik kodda ishlovchi web ilova yozish mumkin</li>
<li><strong>Moslashuvchan</strong>: hech qanday majburiy struktura yo'q</li>
<li><strong>O'rganish oson</strong>: Django kabi katta frameworkga o'tishdan oldin Flask bilan boshlash mantiqiy</li>
<li><strong>Keng qo'llaniladi</strong>: Netflix, Reddit, LinkedIn — bularning hammasi qachondir Flask ishlatgan</li>
</ul>
<h3>1-qadam: Virtual muhit yaratamiz</h3>
<p>Har bir Python loyiha o'z paketlariga ega bo'lishi kerak — bu boshqa loyihadagi versiya to'qnashuvlarining oldini oladi. Buning uchun <code>venv</code> ishlatiladi.</p>
<pre><code>mkdir flask_app &amp;&amp; cd flask_app
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\\Scripts\\activate       # Windows</code></pre>
<p>Buyruq satrida <code>(venv)</code> belgisi paydo bo'lsa — siz virtual muhitdasiz.</p>
<h3>2-qadam: Flask o'rnatish</h3>
<pre><code>pip install flask</code></pre>
<p><code>pip</code> — Pythonning paket menejeri. Bu komanda Flask va uning bog'liqliklarini virtual muhitga yuklab oladi.</p>
<h3>3-qadam: Birinchi ilova</h3>
<p><code>app.py</code> faylini yarating va quyidagini yozing:</p>
<pre><code>from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Salom, dunyo!'

if __name__ == '__main__':
    app.run(debug=True)</code></pre>
<p>Faylni saqlang va <code>python app.py</code> bilan ishga tushiring. Brauzeringizda <code>http://127.0.0.1:5000</code> ni oching — <strong>"Salom, dunyo!"</strong> matnini ko'rasiz.</p>
<h3>Kodni qatorma-qator tushunamiz</h3>
<ul>
<li><code>app = Flask(__name__)</code> — ilova obyektini yaratamiz. <code>__name__</code> Flaskga sizning fayl joylashgan papkani topishga yordam beradi (statik fayllar va shablonlarni izlash uchun)</li>
<li><code>@app.route('/')</code> — bu <strong>dekorator</strong>. Pastdagi funksiyani <code>/</code> URL manziliga bog'laydi</li>
<li><code>app.run(debug=True)</code> — server ishga tushadi. Debug rejimida xato yuz bersa, brauzerda batafsil xato sahifasi chiqadi va kod o'zgarganda server avtomatik qayta ishga tushadi</li>
</ul>
<h3>⚠️ Muhim: <code>debug=True</code> faqat ishlab chiqish uchun</h3>
<p>Debug rejimi qulay, lekin u brauzerda <strong>kod ijro etish konsoli</strong>ni ochib qo'yadi. Hech qachon <code>debug=True</code> bilan publik serverga deploy qilmang.</p>
"""

L1_CODE = """\
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Salom, dunyo!'

@app.route('/about')
def about():
    return '<h1>Bu Flask ilova haqida sahifa</h1><p>2026-yilda yozilgan.</p>'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

L2_TEXT = """\
<h2>Routing va URL</h2>

<pre class="mermaid">
flowchart TB
    U1["GET /"] --> M["URL Map"]
    U2["GET /user/aziz"] --> M
    U3["GET /post/42"] --> M
    U4["POST /submit"] --> M
    M -->|matches| H1["home"]
    M -->|matches| H2["user_page username"]
    M -->|matches| H3["show_post id int"]
    M -->|matches| H4["submit"]
    M -.->|no match| E["404 Not Found"]
    H1 --> R["Response"]
    H2 --> R
    H3 --> R
    H4 --> R
</pre>

<p>Routing — bu turli URL manzillarni turli Python funksiyalariga bog'lash. Flask buni <code>@app.route()</code> dekoratori orqali qiladi.</p>
<h3>Bir nechta sahifa</h3>
<pre><code>@app.route('/')
def home(): return 'Bosh sahifa'

@app.route('/about')
def about(): return 'Biz haqimizda'

@app.route('/contact')
def contact(): return 'Aloqa'</code></pre>
<p>Endi <code>/</code>, <code>/about</code>, <code>/contact</code> manzillarining har biri o'z javobini qaytaradi.</p>
<h3>HTTP methodlar — GET va POST</h3>
<p>Odatda route faqat GET so'rovlarini qabul qiladi. Boshqa methodlarni ruxsat berish uchun:</p>
<pre><code>@app.route('/submit', methods=['GET', 'POST'])
def submit():
    return 'Forma yuborildi'</code></pre>
<h3>Dinamik URL — manzil ichidagi parametrlar</h3>
<p>URL'ning bir qismi o'zgaruvchan bo'lishi mumkin. Masalan, har bir foydalanuvchining alohida sahifasi:</p>
<pre><code>@app.route('/user/&lt;username&gt;')
def user_page(username):
    return f'Salom, {username}!'</code></pre>
<p><code>/user/aziz</code> ga kirsa — "Salom, aziz!". <code>/user/begzod</code> ga kirsa — "Salom, begzod!".</p>
<h3>Tip converters</h3>
<p>URL parametrining turini cheklash mumkin:</p>
<ul>
<li><code>&lt;int:id&gt;</code> — faqat butun son</li>
<li><code>&lt;float:price&gt;</code> — kasr son</li>
<li><code>&lt;string:name&gt;</code> — matn (default)</li>
<li><code>&lt;path:p&gt;</code> — slash <code>/</code> ni ham qabul qiladi</li>
</ul>
<pre><code>@app.route('/post/&lt;int:id&gt;')
def show_post(id):
    return f'Post raqami: {id}'</code></pre>
<p><code>/post/42</code> ishlaydi, <code>/post/abc</code> esa 404 qaytaradi — chunki <code>abc</code> int emas.</p>
<h3>url_for — URL yaratish</h3>
<p>URL'ni qo'lda yozish o'rniga (<code>"/user/" + username</code>), Flask <code>url_for</code> funksiyasini taklif qiladi:</p>
<pre><code>from flask import url_for

url_for('user_page', username='aziz')  # → '/user/aziz'
url_for('show_post', id=42)            # → '/post/42'</code></pre>
<p>Buning afzalligi: agar siz keyinroq route'ni <code>/u/&lt;username&gt;</code> ga o'zgartirsangiz — barcha url_for chaqiruvlari avtomatik to'g'rilanadi.</p>
"""

L2_CODE = """\
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return f'Bosh sahifa. <a href="{url_for("user_page", username="mehmon")}">Mehmon profili</a>'

@app.route('/user/<username>')
def user_page(username):
    return f'<h1>{username} ning profili</h1>'

@app.route('/post/<int:id>')
def show_post(id):
    return f'Post #{id} bu yerda ko\\'rsatiladi'

@app.route('/api/echo', methods=['GET', 'POST'])
def echo():
    return 'Bu route ham GET, ham POST qabul qiladi'

if __name__ == '__main__':
    app.run(debug=True)
"""

L3_TEXT = """\
<h2>Jinja2 Templates</h2>

<pre class="mermaid">
flowchart LR
    R["route handler"] --> CTX["context dict name=Aziz"]
    CTX --> T["render_template"]
    T -->|reads| F["templates/index.html"]
    T --> J["Jinja2 engine"]
    J -->|expands| V["double curly variables"]
    J -->|runs| L["for if blocks"]
    J -->|applies| FL["upper length safe filters"]
    V --> H["rendered HTML"]
    L --> H
    FL --> H
    H -->|escaped XSS safe| B["Brauzer"]
</pre>

<p>Hozirgacha biz HTML'ni Python qator ichida yozdik — bu shoxni juda tez qiyinlashtiradi. To'g'ri yo'l: HTML'ni alohida faylga ajratish va Python'dan unga ma'lumot yuborish. Buni <strong>shablon (template)</strong> deyiladi.</p>
<h3>templates/ papkasi</h3>
<p>Flask odatda shablonlarni <code>templates/</code> papkasidan qidiradi:</p>
<pre><code>flask_app/
├── app.py
└── templates/
    ├── index.html
    └── about.html</code></pre>
<h3>render_template</h3>
<pre><code>from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', name='Aziz')</code></pre>
<p><code>name='Aziz'</code> — shablonga uzatiladigan ma'lumot. Endi <code>index.html</code> ichida uni ishlatish mumkin:</p>
<pre><code>&lt;h1&gt;Salom, {{ name }}!&lt;/h1&gt;</code></pre>
<h3>O'zgaruvchilar — {{ ... }}</h3>
<p>Ikki figurali qavs ichida har qanday Python qiymatini chiqarish mumkin: o'zgaruvchi, list elementi, obyekt atributi, hattoki ifoda.</p>
<pre><code>&lt;p&gt;Yoshi: {{ user.age }}&lt;/p&gt;
&lt;p&gt;Jami: {{ price * quantity }}&lt;/p&gt;</code></pre>
<h3>Sikl — {% for %}</h3>
<p>List bo'ylab aylanish uchun:</p>
<pre><code>&lt;ul&gt;
  {% for item in items %}
    &lt;li&gt;{{ item }}&lt;/li&gt;
  {% endfor %}
&lt;/ul&gt;</code></pre>
<h3>Shart — {% if %}</h3>
<pre><code>{% if user %}
  &lt;p&gt;Xush kelibsiz, {{ user.name }}!&lt;/p&gt;
{% else %}
  &lt;a href="/login"&gt;Kirish&lt;/a&gt;
{% endif %}</code></pre>
<h3>Filtrlar — | bilan</h3>
<p>Qiymatni chiqarishdan oldin uni o'zgartirish mumkin:</p>
<ul>
<li><code>{{ name | upper }}</code> — KATTA HARFLAR</li>
<li><code>{{ name | lower }}</code> — kichik harflar</li>
<li><code>{{ items | length }}</code> — list uzunligi</li>
<li><code>{{ text | safe }}</code> — HTML'ni escape qilmaslik (ehtiyot bo'ling, XSS xavfi!)</li>
<li><code>{{ price | round(2) }}</code> — 2 raqamga yaxlitlash</li>
</ul>
<h3>Shablonlar avtomatik xavfsiz</h3>
<p>Jinja2 har qanday HTML belgisini avtomatik escape qiladi. Ya'ni agar <code>name = "&lt;script&gt;alert(1)&lt;/script&gt;"</code> bo'lsa, brauzer uni JavaScript sifatida ishga tushirmaydi — bu XSS hujumlardan himoyalanadi.</p>
"""

L3_CODE = """\
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    users = ['Aziz', 'Begzod', 'Madina', 'Sevara']
    return render_template('index.html', users=users, total=len(users))

@app.route('/user/<name>')
def profile(name):
    return render_template('profile.html', name=name, is_admin=(name == 'admin'))

# templates/index.html
# <h1>Foydalanuvchilar ({{ total }} ta)</h1>
# <ul>
#   {% for u in users %}
#     <li>{{ u | upper }}</li>
#   {% endfor %}
# </ul>
"""

L4_TEXT = """\
<h2>Statik fayllar va GET form</h2>

<pre class="mermaid">
flowchart TB
    B["Brauzer"] -->|GET /static/style.css| S["static papka"]
    S -->|file response| B
    B -->|GET /static/logo.png| S
    U["foydalanuvchi forma to'ldiradi"] -->|GET /search?q=flask| H["search handler"]
    H --> Q["request.args.get q"]
    Q --> FT["filter items by q"]
    FT --> RT["render_template results"]
    RT --> B
    H -.->|q yo'q| EMPTY["bo'sh natija"]
</pre>

<h3>static/ papkasi</h3>
<p>CSS, JavaScript, rasm — bularning hammasi <code>static/</code> papkasiga joylanadi. Flask ularni avtomatik xizmat qiladi.</p>
<pre><code>flask_app/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── logo.png</code></pre>
<h3>Shablon ichida statik faylga havola</h3>
<p>URL'ni qo'lda yozmang — <code>url_for</code> ishlating:</p>
<pre><code>&lt;link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"&gt;
&lt;img src="{{ url_for('static', filename='logo.png') }}" alt="Logo"&gt;</code></pre>
<p>Bu shuning uchun yaxshiroq: agar Flask deploymentda <code>/static/</code> ni <code>/assets/</code> ga ko'chirsa — kodingiz ishlashda davom etadi.</p>
<h3>GET form — query string</h3>
<p>Eng oddiy forma — GET method bilan ma'lumotni URL ga qo'shadi:</p>
<pre><code>&lt;form action="/search" method="get"&gt;
  &lt;input name="q" placeholder="Qidirish..."&gt;
  &lt;button&gt;Qidirish&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p>Foydalanuvchi "flask" ni qidirsa — brauzer <code>/search?q=flask</code> manziliga o'tadi.</p>
<h3>request.args.get</h3>
<p>URL parametrlarini olish uchun:</p>
<pre><code>from flask import request

@app.route('/search')
def search():
    query = request.args.get('q', '')   # default '' agar bo'lmasa
    return f'Siz qidirgansiz: {query}'</code></pre>
<p><strong>Muhim</strong>: <code>request.args.get</code> ishlating, <code>request.args['q']</code> emas — birinchisi yo'q bo'lsa <code>None</code> qaytaradi, ikkinchisi 400 xato beradi.</p>
<h3>Bir nechta parametr</h3>
<pre><code># /filter?category=books&min_price=10
category = request.args.get('category')
min_price = request.args.get('min_price', type=int)  # avtomatik int'ga aylanadi</code></pre>
<p><code>type=int</code> ishlating — aks holda <code>min_price</code> string bo'lib qoladi va siz <code>"10" &lt; 20</code> kabi xatolarga uchraysiz.</p>
"""

L4_CODE = """\
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return render_template('search.html', error='Qidiruv so\\'zi kerak')
    # Demo: hardcoded "ma'lumotlar bazasi"
    items = ['Flask kitobi', 'Python qo\\'llanma', 'Django darslari', 'CSS asoslari']
    results = [i for i in items if q.lower() in i.lower()]
    return render_template('search.html', q=q, results=results)
"""

L5_TEXT = """\
<h2>POST formani qabul qilish</h2>

<pre class="mermaid">
flowchart LR
    A["GET /contact"] -->|render| F["form HTML"]
    F -->|user submits| C["POST /contact"]
    C --> RF["request.form"]
    RF --> V["validate fields"]
    V -->|ok| SAVE["save data"]
    SAVE --> FS["flash success"]
    FS --> RDR["redirect 302"]
    V -->|fail| FE["flash error"]
    FE --> RDR
    RDR -->|GET again| A
</pre>

<p>GET form URL ichida ma'lumot yuboradi (qisqa, ko'rinadigan). POST esa request body ichida yuboradi — uzun yoki maxfiy ma'lumotlar (parol, izoh, fayl) uchun.</p>
<h3>methods=['GET', 'POST']</h3>
<p>Bitta route ham forma ko'rsatadi (GET), ham qabul qiladi (POST):</p>
<pre><code>from flask import Flask, render_template, request, redirect, url_for, flash

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # ... ma'lumotni saqlash
        flash('Xabaringiz yuborildi!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')</code></pre>
<h3>request.form vs request.args</h3>
<ul>
<li><code>request.args.get('q')</code> — URL'dan (<code>?q=...</code>)</li>
<li><code>request.form.get('name')</code> — POST body'dan</li>
<li><code>request.values.get('x')</code> — ikkalasidan ham (kamdan-kam ishlatiladi)</li>
</ul>
<h3>redirect + url_for — POST/Redirect/GET pattern</h3>
<p>POST'dan keyin foydalanuvchi sahifani yangilasa — brauzer "Formani qayta yubormoqchimisiz?" deb so'raydi va forma ikki marta yuboriladi. Buning oldini olish:</p>
<pre><code>return redirect(url_for('contact'))  # 302 redirect → GET</code></pre>
<p>Bu naqsh nomi <strong>PRG (Post/Redirect/Get)</strong>.</p>
<h3>flash — vaqtinchalik xabar</h3>
<p>Redirect'dan keyin foydalanuvchiga "Xabar yuborildi" deb ko'rsatish kerak. <code>flash()</code> session orqali bir martalik xabar yuboradi:</p>
<pre><code>app.secret_key = 'sirli-kalit-uzgartiring'  # flash session uchun shart

flash('Tabriklaymiz!', 'success')
flash('Xato yuz berdi', 'error')</code></pre>
<p>Shablonda:</p>
<pre><code>{% for category, msg in get_flashed_messages(with_categories=true) %}
  &lt;div class="alert alert-{{ category }}"&gt;{{ msg }}&lt;/div&gt;
{% endfor %}</code></pre>
<h3>Validatsiya — minimal misol</h3>
<pre><code>if not name or len(name) &lt; 2:
    flash("Ism kamida 2 harfdan iborat bo'lishi kerak", 'error')
    return redirect(url_for('contact'))
if '@' not in (email or ''):
    flash('Email noto\\'g\\'ri', 'error')
    return redirect(url_for('contact'))</code></pre>
<p>Jiddiyroq validatsiya uchun <strong>Flask-WTF</strong> kutubxonasi mavjud — kelajakdagi darslarda ko'ramiz.</p>
"""

L5_CODE = """\
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'demo-secret-change-in-production'

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip()
        msg = (request.form.get('message') or '').strip()

        if len(name) < 2:
            flash('Ism kamida 2 harf', 'error')
        elif '@' not in email:
            flash('Email noto\\'g\\'ri', 'error')
        elif len(msg) < 10:
            flash('Xabar kamida 10 harf', 'error')
        else:
            # TODO: bazaga saqlash
            flash(f'Rahmat, {name}! Xabaringiz yuborildi.', 'success')
            return redirect(url_for('contact'))

    return render_template('contact.html')
"""

L6_TEXT = """\
<h2>Session va cookies</h2>

<pre class="mermaid">
flowchart LR
    A["POST /login user pass"] --> B["check credentials"]
    B -->|ok| S["session user_id=42"]
    S -->|signed by SECRET_KEY| CK["Set-Cookie session"]
    CK --> U["Brauzer saves"]
    U -->|next request sends cookie| D["GET /dashboard"]
    D --> RD["read session user_id"]
    RD --> PG["render private page"]
    L["GET /logout"] --> CL["session.clear"]
    CL --> RM["expire cookie"]
</pre>

<p>HTTP — bu <em>stateless</em> protokol. Har bir so'rov o'z-o'zicha mustaqil, server siz kimligingizni eslab qolmaydi. Lekin login qilishingiz uchun server kim siz ekanligingizni bilishi kerak. Yechim — <strong>session</strong> va <strong>cookies</strong>.</p>
<h3>Cookies — brauzer xotirasi</h3>
<p>Server brauzerga "bu qiymatni yodda saqla va keyingi so'rovda menga qaytar" deydi. Brauzer buni avtomatik bajaradi.</p>
<pre><code>from flask import make_response, request

@app.route('/set')
def set_cookie():
    resp = make_response('Cookie o\\'rnatildi')
    resp.set_cookie('tema', 'qora', max_age=60*60*24*30)  # 30 kun
    return resp

@app.route('/get')
def get_cookie():
    return f'Sizning temangiz: {request.cookies.get("tema", "yoq")}'</code></pre>
<h3>Session — xavfsiz cookie</h3>
<p>Session — bu maxsus cookie. Flask uni imzolaydi (signed) — ya'ni foydalanuvchi qiymatni o'zgartira olmaydi. Session'da odatda foydalanuvchi ID'si saqlanadi.</p>
<pre><code>from flask import session

app.secret_key = 'shu-kalit-juda-maxfiy-bolishi-kerak'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    # ... parolni tekshirish ...
    session['user_id'] = 42
    session['username'] = username
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return f'Salom, {session["username"]}!'</code></pre>
<h3>secret_key — eng muhim sozlama</h3>
<p>Session imzosi <code>secret_key</code> orqali yaratiladi. Agar kimdir buni bilsa — sizning ilovangizdagi har qanday foydalanuvchini "o'g'irlay" oladi.</p>
<ul>
<li>Hech qachon kodga yozmang — environment variable ishlating</li>
<li>Tasodifiy uzun string bo'lsin: <code>python -c "import secrets; print(secrets.token_hex(32))"</code></li>
<li>Production'da o'zgartiring va boshqalar bilan bo'lishmang</li>
</ul>
<h3>Session vs Cookie</h3>
<table>
<tr><th></th><th>Cookie</th><th>Session</th></tr>
<tr><td>Saqlash</td><td>Brauzer</td><td>Brauzer (imzolangan)</td></tr>
<tr><td>O'qish</td><td>request.cookies</td><td>session[...]</td></tr>
<tr><td>O'zgartirish</td><td>Foydalanuvchi qila oladi</td><td>Imzo bilan himoyalangan</td></tr>
<tr><td>Ishlatish</td><td>Tema, til</td><td>Login, user_id</td></tr>
</table>
"""

L6_CODE = """\
from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'production-da-environ-orqali-bering'

USERS = {'aziz': '12345', 'admin': 'secret'}

@app.route('/')
def home():
    if 'username' in session:
        return f'Salom, {session["username"]}! <a href="/logout">Chiqish</a>'
    return '<a href="/login">Kirish</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if USERS.get(u) == p:
            session['username'] = u
            return redirect(url_for('home'))
        return 'Login xato', 401
    return '''<form method="post">
        <input name="username" placeholder="login">
        <input name="password" type="password">
        <button>Kirish</button>
    </form>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
"""

L7_TEXT = """\
<h2>Database — Flask-SQLAlchemy</h2>

<pre class="mermaid">
flowchart LR
    P["Python kod"] --> M["User Model class"]
    M --> ORM["SQLAlchemy ORM"]
    P -->|User.query.all| Q["query builder"]
    Q --> ORM
    P -->|db.session.add| S["unit of work"]
    S -->|db.session.commit| ORM
    ORM -->|SQL statement| D["SQLite or Postgres"]
    D -->|rows| ORM
    ORM -->|User objects| P
    P -.->|rollback on error| S
</pre>

<p>Real ilovalarda ma'lumot xotirada emas, balki <strong>ma'lumotlar bazasida</strong> saqlanadi. Flask'da eng keng tarqalgan vosita — <code>Flask-SQLAlchemy</code>, bu Python obyektlari orqali SQL bilan ishlash imkonini beradi (ORM).</p>
<h3>O'rnatish</h3>
<pre><code>pip install flask-sqlalchemy</code></pre>
<h3>Sozlash</h3>
<pre><code>from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)</code></pre>
<p><code>sqlite:///app.db</code> — eng oddiy variant, fayl-asosida ishlaydi, sozlash kerak emas. Production'da PostgreSQL ishlatamiz:</p>
<pre><code>SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dbname'</code></pre>
<h3>Model — bu Python sinfi</h3>
<pre><code>class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'&lt;User {self.username}&gt;'</code></pre>
<p>Har bir <code>db.Column</code> — bu jadval ustuni. <code>primary_key=True</code> avtomatik o'sib boruvchi ID. <code>unique=True</code> — takror qiymat ruxsat etilmaydi.</p>
<h3>Jadvallarni yaratish</h3>
<pre><code>with app.app_context():
    db.create_all()</code></pre>
<p>Bu komanda bazada barcha modellar uchun jadval yaratadi (agar yo'q bo'lsa). <strong>Eslatma</strong>: bu mavjud jadvallarni o'zgartirmaydi. Production'da schema o'zgartirish uchun <strong>Flask-Migrate</strong> (Alembic) ishlatiladi.</p>
<h3>Birinchi so'rov</h3>
<pre><code># Yangi yozuv qo'shish
user = User(username='aziz', email='aziz@example.com')
db.session.add(user)
db.session.commit()

# Hamma foydalanuvchilarni olish
users = User.query.all()

# ID bo'yicha
user = User.query.get(1)

# Filtr
admin = User.query.filter_by(username='admin').first()

# Tartiblash + limit
recent = User.query.order_by(User.created_at.desc()).limit(10).all()</code></pre>
<h3>Muhim qoidalar</h3>
<ul>
<li><code>db.session.add()</code> — yangi yozuvni "sessiyaga" qo'shadi (hali bazaga yozilmadi)</li>
<li><code>db.session.commit()</code> — bazaga haqiqatan yozadi</li>
<li><code>db.session.rollback()</code> — xato bo'lsa, o'zgarishlarni bekor qiladi</li>
<li>Har bir route oxirida session avtomatik yopiladi</li>
</ul>
"""

L7_CODE = """\
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

@app.route('/users')
def list_users():
    return jsonify([u.to_dict() for u in User.query.all()])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Demo: agar bo'sh bo'lsa, bitta foydalanuvchi qo'shamiz
        if not User.query.first():
            db.session.add(User(username='aziz', email='aziz@example.com'))
            db.session.commit()
    app.run(debug=True)
"""

L8_TEXT = """\
<h2>CRUD operatsiyalar</h2>

<pre class="mermaid">
flowchart TB
    subgraph CR["CREATE"]
        C1["POST /notes"] --> C2["Note title body"]
        C2 --> C3["add then commit"]
    end
    subgraph RD["READ"]
        R1["GET /notes"] --> R2["query.order_by all"]
        R3["GET /notes/id"] --> R4["get_or_404"]
    end
    subgraph UP["UPDATE"]
        U1["POST /notes/id/edit"] --> U2["note.title equals new"]
        U2 --> U3["commit only"]
    end
    subgraph DL["DELETE"]
        D1["POST /notes/id/delete"] --> D2["session.delete"]
        D2 --> D3["commit"]
    end
</pre>

<p>CRUD — bu Create, Read, Update, Delete. Har qanday ma'lumot bilan ishlovchi ilovaning asosiy 4 amali.</p>
<h3>CREATE — yangi yozuv</h3>
<pre><code>@app.route('/notes', methods=['POST'])
def create_note():
    title = request.form['title']
    body = request.form['body']

    note = Note(title=title, body=body)
    db.session.add(note)
    db.session.commit()  # endi note.id mavjud
    return redirect(url_for('show_note', id=note.id))</code></pre>
<h3>READ — bitta yoki ko'p</h3>
<pre><code># Hammasi (eng yangidan eski tomon)
@app.route('/notes')
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=notes)

# Bitta
@app.route('/notes/&lt;int:id&gt;')
def show_note(id):
    note = Note.query.get_or_404(id)  # yo'q bo'lsa avtomatik 404
    return render_template('note.html', note=note)</code></pre>
<p><code>get_or_404</code> juda foydali — <code>None</code> ni tekshirish va xato qaytarish kerak emas.</p>
<h3>UPDATE — mavjud yozuvni o'zgartirish</h3>
<pre><code>@app.route('/notes/&lt;int:id&gt;/edit', methods=['GET', 'POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    if request.method == 'POST':
        note.title = request.form['title']
        note.body = request.form['body']
        db.session.commit()  # add() kerak emas — yozuv allaqachon sessiyada
        return redirect(url_for('show_note', id=note.id))
    return render_template('edit_note.html', note=note)</code></pre>
<h3>DELETE — yozuvni o'chirish</h3>
<pre><code>@app.route('/notes/&lt;int:id&gt;/delete', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('Yozuv o\\'chirildi', 'success')
    return redirect(url_for('list_notes'))</code></pre>
<p><strong>Muhim</strong>: DELETE va shunga o'xshash xavfli amallarni faqat POST orqali qiling, GET emas. Aks holda Google bot yoki link preview sizning yozuvlaringizni o'chirib yuborishi mumkin.</p>
<h3>Xato bilan ishlash</h3>
<pre><code>from sqlalchemy.exc import IntegrityError

try:
    db.session.add(user)
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    flash('Bu username allaqachon mavjud', 'error')
    return redirect(url_for('register'))</code></pre>
<p><code>commit()</code> xato bersa — <strong>rollback()</strong> qilish shart, aks holda sessiya buzilib qoladi.</p>
<h3>Bulk operatsiyalar — tezroq</h3>
<pre><code># 1000 yozuvni bittada o'chirish (har birini sessiyaga yuklamasdan)
Note.query.filter(Note.created_at &lt; cutoff).delete()
db.session.commit()</code></pre>
"""

L8_CODE = """\
from flask import Flask, request, redirect, url_for, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=db.func.now())

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        n = Note(title=request.form['title'], body=request.form.get('body', ''))
        try:
            db.session.add(n)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 'Xato', 400
        return redirect(url_for('notes'))
    return render_template('notes.html', notes=Note.query.order_by(Note.id.desc()).all())

@app.route('/notes/<int:id>/delete', methods=['POST'])
def delete(id):
    n = Note.query.get_or_404(id)
    db.session.delete(n)
    db.session.commit()
    return redirect(url_for('notes'))
"""

L9_TEXT = """\
<h2>Blueprint va app factory</h2>

<pre class="mermaid">
flowchart TB
    F["create_app config"] --> A["Flask instance"]
    A --> CFG["config.from_object"]
    A --> DB["db.init_app app"]
    A --> AB["auth_bp at /auth"]
    A --> NB["notes_bp at /notes"]
    AB --> AR["login logout routes"]
    NB --> NR["list show edit routes"]
    A --> RET["return app"]
    RET --> RUN["run.py or wsgi.py"]
</pre>

<p>11 ta route va 5 ta modeli bor ilova bitta <code>app.py</code> faylida turishi mumkin. Lekin 50 route va 20 model uchun — bu jahannamga aylanadi. Yechim: <strong>Blueprint</strong> va <strong>app factory</strong> pattern.</p>
<h3>App factory pattern</h3>
<p>Ilovani global o'zgaruvchi sifatida emas, balki <strong>funksiyadan qaytariladigan obyekt</strong> sifatida yaratamiz:</p>
<pre><code># app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    db.init_app(app)

    from app.auth import auth_bp
    from app.notes import notes_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(notes_bp, url_prefix='/notes')

    return app</code></pre>
<p>Bunga afzalliklar:</p>
<ul>
<li><strong>Test qulay</strong>: har bir testda yangi app yaratish mumkin (har xil konfiguratsiya bilan)</li>
<li><strong>Circular import yo'q</strong>: <code>db</code>, <code>app</code> birgalikda ishlatilganda muammo bo'lmaydi</li>
<li><strong>Bir nechta deploy konfiguratsiyasi</strong>: dev/test/prod</li>
</ul>
<h3>Blueprint — modulli marshrutlar</h3>
<p>Blueprint — bu Flask ilovasining bir qismi: bir guruh route, template, static fayllar. Ularni alohida faylga ajratish mumkin:</p>
<pre><code># app/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from app.auth import routes  # noqa: route'larni ro'yxatga olish uchun

# app/auth/routes.py
from app.auth import auth_bp
from flask import render_template, request

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    return 'Chiqdingiz'</code></pre>
<p>Endi <code>/auth/login</code> ishlaydi (chunki <code>url_prefix='/auth'</code> bilan ro'yxatga oldik).</p>
<h3>url_for blueprint bilan</h3>
<p>Blueprint ichidagi route'ga havola berish uchun blueprint nomini qo'shamiz:</p>
<pre><code>url_for('auth.login')   # → '/auth/login'
url_for('notes.show', id=42)  # → '/notes/42'</code></pre>
<h3>Tavsiya etilgan loyiha tuzilmasi</h3>
<pre><code>flask_app/
├── app/
│   ├── __init__.py          # create_app
│   ├── models.py            # SQLAlchemy modellari
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── templates/auth/login.html
│   └── notes/
│       ├── __init__.py
│       ├── routes.py
│       └── templates/notes/list.html
├── config.py
├── run.py                   # from app import create_app; create_app().run()
└── requirements.txt</code></pre>
<p>Bu shakl Flask jamoasi tomonidan rasmiy ravishda tavsiya etilgan va katta loyihalar uchun standart.</p>
"""

L9_CODE = """\
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = 'dev-key-change-me'

    db.init_app(app)

    from app.main import main_bp
    from app.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

# app/auth/__init__.py
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

from app.auth import routes

# app/auth/routes.py
from flask import render_template
from app.auth import auth_bp

@auth_bp.route('/login')
def login():
    return 'Login sahifasi'

# run.py
from app import create_app
if __name__ == '__main__':
    create_app().run(debug=True)
"""

L10_TEXT = """\
<h2>JSON API yaratish</h2>

<pre class="mermaid">
flowchart LR
    C["Client React or curl"] -->|GET /api/notes| LH["list_notes"]
    LH -->|jsonify list 200| C
    C -->|POST /api/notes JSON| PH["create_note"]
    PH -->|jsonify dict 201| C
    C -->|GET /api/notes/id| GH["get_note"]
    GH -->|jsonify 200 or 404| C
    C -->|PUT /api/notes/id| UH["update_note"]
    UH -->|jsonify 200| C
    C -->|DELETE /api/notes/id| DH["delete_note"]
    DH -->|empty 204| C
</pre>

<p>Hozirgacha Flask HTML qaytardi. Lekin mobil ilova yoki React frontend bilan ishlash uchun bizga <strong>JSON API</strong> kerak — server JSON qaytaradi, klient uni o'zicha ko'rsatadi.</p>
<h3>jsonify — JSON javob qaytarish</h3>
<pre><code>from flask import jsonify

@app.route('/api/users')
def api_users():
    users = User.query.all()
    return jsonify([
        {'id': u.id, 'username': u.username}
        for u in users
    ])</code></pre>
<p><code>jsonify</code>:</p>
<ul>
<li>Python dict/list ni JSON ga aylantiradi</li>
<li><code>Content-Type: application/json</code> header qo'shadi</li>
<li>UTF-8 belgilarini to'g'ri saqlaydi</li>
</ul>
<h3>request.get_json — JSON qabul qilish</h3>
<pre><code>@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'title shart'}), 400

    note = Note(title=data['title'], body=data.get('body', ''))
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id, 'title': note.title}), 201</code></pre>
<h3>HTTP status codes</h3>
<table>
<tr><th>Kod</th><th>Ma'no</th><th>Qachon</th></tr>
<tr><td>200</td><td>OK</td><td>Muvaffaqiyatli GET</td></tr>
<tr><td>201</td><td>Created</td><td>POST orqali yangi resurs yaratildi</td></tr>
<tr><td>204</td><td>No Content</td><td>DELETE muvaffaqiyatli, javob bo'sh</td></tr>
<tr><td>400</td><td>Bad Request</td><td>Klient noto'g'ri so'rov yubordi</td></tr>
<tr><td>401</td><td>Unauthorized</td><td>Avtorizatsiya kerak</td></tr>
<tr><td>403</td><td>Forbidden</td><td>Kirish ta'qiqlangan</td></tr>
<tr><td>404</td><td>Not Found</td><td>Resurs topilmadi</td></tr>
<tr><td>500</td><td>Server Error</td><td>Backendda xato</td></tr>
</table>
<p>Flask'da statusni javob bilan qaytarish:</p>
<pre><code>return jsonify({'error': 'topilmadi'}), 404</code></pre>
<h3>REST konventsiya</h3>
<pre><code>GET    /api/notes        — hammasi
GET    /api/notes/&lt;id&gt;   — bittasi
POST   /api/notes        — yangi yaratish
PUT    /api/notes/&lt;id&gt;   — to'liq yangilash
PATCH  /api/notes/&lt;id&gt;   — qisman yangilash
DELETE /api/notes/&lt;id&gt;   — o'chirish</code></pre>
<h3>CORS — boshqa domaindagi frontend uchun</h3>
<p>Agar frontend (React, Vue) <code>localhost:3000</code> da, backend <code>localhost:5000</code> da bo'lsa — brauzer "Cross-Origin" deb so'rovlarni bloklaydi. Yechim:</p>
<pre><code>pip install flask-cors

from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})</code></pre>
<p>Production'da <code>"origins": "*"</code> o'rniga aniq domen kiriting: <code>"https://myapp.com"</code>.</p>
<h3>Error handlers — global xato boshqaruvi</h3>
<pre><code>@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Topilmadi'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server xatosi'}), 500</code></pre>
"""

L10_CODE = """\
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, default='')

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'body': self.body}

@app.route('/api/notes', methods=['GET'])
def list_notes():
    return jsonify([n.to_dict() for n in Note.query.all()])

@app.route('/api/notes/<int:id>', methods=['GET'])
def get_note(id):
    n = Note.query.get_or_404(id)
    return jsonify(n.to_dict())

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'title shart'}), 400
    n = Note(title=data['title'], body=data.get('body', ''))
    db.session.add(n)
    db.session.commit()
    return jsonify(n.to_dict()), 201

@app.route('/api/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    n = Note.query.get_or_404(id)
    db.session.delete(n)
    db.session.commit()
    return '', 204

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Topilmadi'}), 404
"""

L11_TEXT = """\
<h2>Deployga tayyorlash</h2>

<pre class="mermaid">
flowchart LR
    I["Internet"] -->|HTTPS 443| N["nginx"]
    N -->|proxy_pass 8000| G["gunicorn 4 workers"]
    G --> F["Flask app"]
    F --> D["PostgreSQL"]
    E[".env file"] -->|load_dotenv| F
    E -.->|SECRET_KEY DATABASE_URL| F
    N -.->|serves static| S["static folder"]
    F -.->|debug=False| PROD["production safe"]
</pre>

<p>Ilovangiz lokalda ishlayapti. Endi uni publik serverga chiqarish vaqti. Lekin <code>python app.py</code> bilan production'da ishlatish — xavfli va sekin. To'g'ri yo'l: <strong>WSGI server + environment vars + xavfsiz sozlamalar</strong>.</p>
<h3>1. python-dotenv — .env fayl</h3>
<p>Maxfiy ma'lumotlarni (SECRET_KEY, DATABASE_URL) kodga yozmang. <code>.env</code> faylga chiqaring:</p>
<pre><code># .env
SECRET_KEY=tasodifiy-uzun-string
DATABASE_URL=postgresql://user:pass@host/db
FLASK_ENV=production</code></pre>
<pre><code>pip install python-dotenv

# app.py boshida
from dotenv import load_dotenv
import os
load_dotenv()

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']</code></pre>
<p><code>.env</code> ni <strong>git ga commit qilmang</strong> — <code>.gitignore</code> ga qo'shing. Repo'da <code>.env.example</code> ni saqlang (haqiqiy qiymatlarsiz).</p>
<h3>2. gunicorn — production WSGI server</h3>
<p>Flask'ning ichki serveri (<code>app.run()</code>) faqat developmenta uchun. U bir vaqtda bitta so'rovni boshqaradi, xavfsizlik tekshiruvlari yo'q. Production uchun <strong>gunicorn</strong>:</p>
<pre><code>pip install gunicorn

# Ishga tushirish
gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'</code></pre>
<ul>
<li><code>-w 4</code> — 4 ta worker process (taxminan CPU core × 2)</li>
<li><code>-b 0.0.0.0:8000</code> — barcha interfeyslarga bog'lanish, 8000-portda</li>
<li><code>'app:create_app()'</code> — modulning nomi + factory chaqirig'i</li>
</ul>
<h3>3. debug=False</h3>
<p>Production'da hech qachon <code>debug=True</code> bo'lmasin. Bu — eng katta xavfsizlik xatosi. Gunicorn bilan ishlaganda buni unutmaslik oson, lekin:</p>
<pre><code>if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_ENV') == 'development')</code></pre>
<h3>4. Nginx — gunicorn oldida proxy</h3>
<p>Odatda quyidagi tuzilma:</p>
<pre><code>Internet → nginx (:80, :443) → gunicorn (:8000) → Flask</code></pre>
<p>Nginx HTTPS, statik fayllar, rate limiting va keshlashni boshqaradi. Gunicorn Python kodini ishga tushiradi.</p>
<h3>5. ProxyFix — to'g'ri IP olish</h3>
<p>Nginx orqali kelganda <code>request.remote_addr</code> har doim <code>127.0.0.1</code> ko'rinadi. To'g'ri client IP olish uchun:</p>
<pre><code>from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)</code></pre>
<h3>6. requirements.txt — qatiy versiyalar</h3>
<pre><code>pip freeze &gt; requirements.txt</code></pre>
<p>Bu faylda har bir paket aniq versiyasi bilan. Production serverda <code>pip install -r requirements.txt</code> — xuddi shu versiyalar o'rnatiladi.</p>
<h3>7. Tekshiruv ro'yxati</h3>
<ul>
<li>☐ <code>debug=False</code></li>
<li>☐ <code>SECRET_KEY</code> environment'dan</li>
<li>☐ <code>DATABASE_URL</code> environment'dan</li>
<li>☐ <code>.env</code> gitignore'da</li>
<li>☐ <code>requirements.txt</code> yangilangan</li>
<li>☐ gunicorn (yoki uwsgi) ishlatilmoqda</li>
<li>☐ Nginx oldida turibdi</li>
<li>☐ HTTPS yoqilgan</li>
</ul>
<h3>Tabriklaymiz!</h3>
<p>Siz endi to'liq Flask ilovani noldan production'gacha olib chiqishni bilasiz. Keyingi qadamlar: <strong>Flask-Login</strong> (autentifikatsiya), <strong>Flask-Migrate</strong> (DB migration), <strong>Celery</strong> (background tasks), <strong>pytest</strong> (testing).</p>
"""

L11_CODE = """\
# run.py — production entrypoint
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app

application = create_app()  # gunicorn shu nomni qidiradi

if __name__ == '__main__':
    # Faqat local dev uchun
    application.run(debug=os.environ.get('FLASK_ENV') == 'development', port=5000)

# Production'da:
#   gunicorn -w 4 -b 0.0.0.0:8000 run:application
#
# nginx config (qisqartirilgan):
#   server {
#       listen 443 ssl;
#       server_name myapp.com;
#       location / { proxy_pass http://127.0.0.1:8000; }
#       location /static { alias /var/www/myapp/static; }
#   }
"""


# ═════════════════════════════════════════════════════════════════════════════
# REVISION LESSONS — module checkpoints with mini-projects
# Each consolidates the preceding module and unlocks via a project ≥ 90/100.
# ═════════════════════════════════════════════════════════════════════════════

R1_TEXT = """\
<h2>Takrorlash: Modul 1 + 2 — Routes, Templates, Forms, Session</h2>

<pre class="mermaid">
flowchart TB
    L1["GET /login form"] -->|user submits| L2["POST /login"]
    L2 -->|session username set| I["GET / index"]
    I -->|render_template entries user| H["index HTML"]
    H -->|user types text| S["POST /post"]
    S --> AUTH["session check"]
    AUTH -->|ok| APP["append entry"]
    APP -->|redirect 302| I
    AUTH -->|no session| L1
    I -->|click chiqish| O["GET /logout"]
    O -->|session.clear| L1
</pre>

<p>Tabriklaymiz! Siz allaqachon 6 ta darsni o'tdingiz. Bu — Flask asoslarining yarmi. Endi to'xtab, hammasini birlashtirib mustahkamlash vaqti keldi. Bu dars yangi mavzu emas — bu sizning egallagan bilimlaringizni <strong>birgalikda</strong> ishlatishni o'rgatadi.</p>

<h3>📋 Modul 1+2 da nimalarni o'rgangansiz</h3>
<table style="border-collapse:collapse;width:100%;margin:1em 0">
  <thead>
    <tr style="background:#f3f4f6">
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Dars</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Asosiy konsept</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Kalit kod</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">1</td><td style="padding:8px;border:1px solid #e5e7eb">Flask ilovasini ishga tushirish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>app = Flask(__name__)</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">2</td><td style="padding:8px;border:1px solid #e5e7eb">Routing va URL parametrlari</td><td style="padding:8px;border:1px solid #e5e7eb"><code>@app.route('/u/&lt;name&gt;')</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">3</td><td style="padding:8px;border:1px solid #e5e7eb">Jinja2 templatelar</td><td style="padding:8px;border:1px solid #e5e7eb"><code>render_template('x.html', user=u)</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">4</td><td style="padding:8px;border:1px solid #e5e7eb">Static fayllar + GET forma</td><td style="padding:8px;border:1px solid #e5e7eb"><code>request.args.get('q')</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">5</td><td style="padding:8px;border:1px solid #e5e7eb">POST forma va PRG pattern</td><td style="padding:8px;border:1px solid #e5e7eb"><code>request.form['x']</code> → <code>redirect(url_for(...))</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">6</td><td style="padding:8px;border:1px solid #e5e7eb">Session va cookies</td><td style="padding:8px;border:1px solid #e5e7eb"><code>session['user_id'] = id</code></td></tr>
  </tbody>
</table>

<h3>🧩 Hammasini birlashtirish — odatiy ilova oqimi</h3>
<p>Real veb-ilovada bu 6 ta konsept har doim birga ishlaydi. Foydalanuvchining bitta oddiy harakatini (login qilib, biror narsa yuborish) kuzatib chiqamiz:</p>
<ol>
  <li><strong>GET /login</strong> → <code>@app.route('/login', methods=['GET'])</code> → <code>render_template('login.html')</code> orqali forma chiqaradi</li>
  <li><strong>POST /login</strong> → <code>request.form['username']</code> → tekshirib <code>session['username'] = ...</code> → <code>redirect(url_for('home'))</code></li>
  <li><strong>GET /</strong> → <code>session.get('username')</code> bor-yo'qligini tekshiradi → <code>render_template('home.html', user=session['username'])</code></li>
  <li><strong>POST /post</strong> → forma ma'lumotlari + <code>session['username']</code> birgalikda saqlanadi → redirect</li>
  <li><strong>GET /logout</strong> → <code>session.clear()</code> → <code>redirect(url_for('login'))</code></li>
</ol>

<h3>⚠️ Modul 1+2 da eng ko'p uchraydigan xatolar</h3>
<ul>
  <li><strong>methods'ni unutish</strong>: <code>@app.route('/login')</code> faqat GET ni qabul qiladi. POST uchun <code>methods=['GET', 'POST']</code> kerak.</li>
  <li><strong>POST'dan keyin redirect qilmaslik</strong>: foydalanuvchi sahifani refresh qilsa, forma qayta yuboriladi. Doim PRG pattern (POST → Redirect → GET).</li>
  <li><strong>session'ni SECRET_KEY'siz ishlatish</strong>: <code>app.secret_key = '...'</code> bo'lmasa, session umuman ishlamaydi.</li>
  <li><strong>session.get vs session[]</strong>: <code>session['username']</code> agar yo'q bo'lsa KeyError beradi. Xavfsiz tekshirish: <code>session.get('username')</code>.</li>
  <li><strong>Jinja2 da Python ishlamaydi</strong>: <code>{{ items.length }}</code> emas, balki <code>{{ items|length }}</code> (filter) yoki <code>{{ items|count }}</code>.</li>
  <li><strong>url_for() ni hardcode bilan almashtirish</strong>: HTML da <code>&lt;a href="/login"&gt;</code> emas, <code>&lt;a href="{{ url_for('login') }}"&gt;</code> — keyin route nomi o'zgarsa, linklar buzilmaydi.</li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq ishlaydigan <strong>Mehmonlar kitobi</strong> ilovasi. U bu modulning 4 ta asosiy konseptini birga ishlatadi: routing, templates, forms, session. Birinchi navbatda kodni o'qib chiqing, keyin uni o'zingiz qaytadan yozing (copy-paste qilmang!). Keyin loyihani bajaring.</p>
"""

R1_CODE = """\
# app.py — to'liq ishlaydigan Mehmonlar kitobi (guest book)
# 6 darsdan oldin o'rganganlaringiz birga ishlaydi.
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maxfiy-kalit-prod-uchun-environment-dan-o\\'qing'  # 6-dars: session uchun

# Oddiy xotira (database emas — keyingi darsda o'rganamiz)
ENTRIES = []  # [{'author': str, 'text': str, 'time': datetime}]


# ─── 2-dars: Routing ─────────────────────────────────────────────
@app.route('/')
def index():
    # 6-dars: session'dan kim kirganini bilamiz
    user = session.get('username')
    # 3-dars: Jinja2 bilan render qilish, 5-dars: flash xabarlar
    return render_template_string(INDEX_HTML, entries=ENTRIES, user=user)


# ─── 5-dars: GET + POST forma ────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        # 5-dars: server-side validation
        if len(username) < 2:
            flash('Ism kamida 2 ta belgidan iborat bo\\'lishi kerak', 'error')
            return redirect(url_for('login'))  # PRG pattern
        session['username'] = username  # 6-dars: session'ga yozish
        flash(f'Xush kelibsiz, {username}!', 'success')
        return redirect(url_for('index'))
    return render_template_string(LOGIN_HTML)


# ─── 5-dars: POST-only endpoint + 6-dars: session tekshiruv ────
@app.route('/post', methods=['POST'])
def post():
    user = session.get('username')
    if not user:
        flash('Avval ro\\'yxatdan o\\'ting', 'error')
        return redirect(url_for('login'))
    text = request.form.get('text', '').strip()
    if not text:
        flash('Xabar bo\\'sh bo\\'lishi mumkin emas', 'error')
        return redirect(url_for('index'))
    ENTRIES.insert(0, {  # yangi xabarlar yuqorida
        'author': user,
        'text': text,
        'time': datetime.now().strftime('%H:%M %d-%b'),
    })
    return redirect(url_for('index'))  # PRG pattern


# ─── 6-dars: session'ni tozalash ─────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('Xayr! Yana keling.', 'success')
    return redirect(url_for('index'))


# ─── 3-dars: Jinja2 templatelar (oddiylik uchun string ichida) ──
INDEX_HTML = '''
<!DOCTYPE html>
<html><head><title>Mehmonlar kitobi</title></head><body>
  <h1>📖 Mehmonlar kitobi</h1>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, msg in messages %}
      <div style="color: {{ 'red' if category == 'error' else 'green' }}">{{ msg }}</div>
    {% endfor %}
  {% endwith %}
  {% if user %}
    <p>Salom, <strong>{{ user }}</strong>! (<a href="{{ url_for('logout') }}">Chiqish</a>)</p>
    <form method="post" action="{{ url_for('post') }}">
      <input name="text" placeholder="Sizning xabaringiz..." required>
      <button type="submit">Yuborish</button>
    </form>
  {% else %}
    <p><a href="{{ url_for('login') }}">Xabar yozish uchun ro'yxatdan o'ting</a></p>
  {% endif %}
  <hr>
  {% if entries %}
    {% for e in entries %}
      <div style="margin: 1em 0; padding: 0.5em; background: #f0f0f0">
        <strong>{{ e.author }}</strong> <small>· {{ e.time }}</small><br>
        {{ e.text }}
      </div>
    {% endfor %}
  {% else %}
    <p style="color: gray">Hali xabarlar yo'q. Birinchi bo'lib yozing!</p>
  {% endif %}
</body></html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html><head><title>Login</title></head><body>
  <h1>Ro'yxatdan o'tish</h1>
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, msg in messages %}
      <div style="color: red">{{ msg }}</div>
    {% endfor %}
  {% endwith %}
  <form method="post">
    <input name="username" placeholder="Ismingiz" required minlength="2">
    <button type="submit">Kirish</button>
  </form>
  <p><a href="{{ url_for('index') }}">← Ortga</a></p>
</body></html>
'''


if __name__ == '__main__':
    app.run(debug=True)
"""


R2_TEXT = """\
<h2>Takrorlash: Modul 3 — Database va CRUD</h2>

<pre class="mermaid">
flowchart LR
    subgraph DB["Database"]
        U["User id username"] -->|one to many| N1["Note id title body user_id"]
        U -->|one to many| N2["Note id title body user_id"]
    end
    R["GET /notes"] --> SE["session.get user_id"]
    SE --> FT["filter_by user_id"]
    FT --> DB
    DB --> LST["only my notes"]
    E["GET /notes/55/edit"] --> CHK["note.user_id check"]
    CHK -->|mismatch| F403["403 Forbidden"]
    CHK -->|match| FORM["edit form"]
</pre>

<p>Modul 3 da siz Flask-SQLAlchemy bilan ishlash, ma'lumotlarni saqlash va o'qish (Read), yangilash (Update), o'chirish (Delete) — ya'ni to'liq <strong>CRUD</strong> ni o'rgandingiz. Endi vaqt keldi — hammasini birlashtirib, har bir foydalanuvchining o'z shaxsiy yozuvlari bo'lgan to'liq ilovasini quramiz.</p>

<h3>📋 Modul 3 da nimalarni o'rgangansiz</h3>
<table style="border-collapse:collapse;width:100%;margin:1em 0">
  <thead>
    <tr style="background:#f3f4f6">
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Konsept</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">SQLAlchemy kod</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Model yaratish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>class Note(db.Model): ...</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Yangi yozuv</td><td style="padding:8px;border:1px solid #e5e7eb"><code>db.session.add(n); db.session.commit()</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Hammasini olish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>Note.query.all()</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Bittasini ID bo'yicha</td><td style="padding:8px;border:1px solid #e5e7eb"><code>Note.query.get_or_404(id)</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Filtrlash</td><td style="padding:8px;border:1px solid #e5e7eb"><code>Note.query.filter_by(user_id=u).all()</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Tartiblash</td><td style="padding:8px;border:1px solid #e5e7eb"><code>Note.query.order_by(Note.created_at.desc())</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Yangilash</td><td style="padding:8px;border:1px solid #e5e7eb"><code>n.title = 'yangi'; db.session.commit()</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">O'chirish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>db.session.delete(n); db.session.commit()</code></td></tr>
  </tbody>
</table>

<h3>🧩 Modul 2 + 3 = real ilova</h3>
<p>Modul 2 da o'rgangan <strong>session</strong>'ni Modul 3 dagi <strong>database</strong> bilan birlashtirsak — har bir foydalanuvchining o'z ma'lumotlari bo'ladi. Bu zamonaviy veb-ilovaning eng asosiy nuqtasi.</p>

<h3>👥 User + Note: ikkita jadval orasidagi bog'lanish</h3>
<p>Real ilovalarda bitta foydalanuvchining ko'p notalari bo'ladi. Buni <strong>one-to-many</strong> munosabat deyiladi va SQLAlchemy'da <code>ForeignKey</code> bilan yoziladi:</p>
<pre><code>class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    notes = db.relationship('Note', backref='owner', lazy=True)  # bu foydalanuvchining barcha notalari

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # qaysi foydalanuvchiniki
    created_at = db.Column(db.DateTime, default=datetime.utcnow)</code></pre>
<p>Endi siz <code>user.notes</code> bilan foydalanuvchining barcha notalarini olishingiz mumkin, yoki <code>note.owner</code> bilan notaning egasini bilib olishingiz mumkin.</p>

<h3>🔐 Login + filtrlash = xavfsizlik</h3>
<p>Eng muhim qoida: <strong>foydalanuvchi faqat o'z notalarini ko'rishi va o'zgartirishi kerak</strong>. Buni quyidagi pattern bilan ta'minlaymiz:</p>
<pre><code>@app.route('/notes')
def list_notes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    # FAQAT shu foydalanuvchining notalarini olamiz
    notes = Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=notes)

@app.route('/notes/&lt;int:note_id&gt;/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    user_id = session.get('user_id')
    note = Note.query.get_or_404(note_id)
    # MUHIM: notaning egasi shu foydalanuvchi ekanligini tekshiramiz
    if note.user_id != user_id:
        return 'Ruxsat yo\\'q', 403
    # ... edit logic ...
</code></pre>

<h3>⚠️ Modul 3 da eng xavfli xatolar</h3>
<ul>
  <li><strong>commit() ni unutish</strong>: <code>db.session.add(n)</code> dan keyin <code>db.session.commit()</code> chaqirilmasa, hech narsa saqlanmaydi.</li>
  <li><strong>Foydalanuvchini tekshirmaslik</strong>: <code>Note.query.get(id)</code> har qanday notani qaytaradi — boshqa foydalanuvchiniki ham. Doim <code>note.user_id != session['user_id']</code> ni tekshiring.</li>
  <li><strong>get() vs get_or_404()</strong>: <code>get(id)</code> mavjud bo'lmasa <code>None</code> qaytaradi, keyin AttributeError beradi. Yaxshisi <code>get_or_404(id)</code> — avtomatik 404 chiqaradi.</li>
  <li><strong>created_at ga default qo'ymaslik</strong>: <code>default=datetime.utcnow</code> — qavslarsiz! Aks holda barcha notalar bir xil vaqt bilan saqlanadi.</li>
  <li><strong>Parolni ochiq saqlash</strong>: bu darsda biz parolni hash qilmayapmiz (Medium kursida o'rgansiz), lekin haqiqiy ilovada hech qachon ochiq parol saqlamang.</li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq ishlaydigan shaxsiy notlar ilovasi. U Modul 2 + Modul 3 ning barcha konseptlarini birga ishlatadi. Birinchi navbatda kodni o'qib chiqing, har bir qatorning vazifasini tushuning. Keyin o'z loyihangizni qurishga o'ting.</p>
"""

R2_CODE = """\
# app.py — Shaxsiy yozuvlar ilovasi (User + Note + Session-based auth)
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'maxfiy-kalit-prod-uchun-environment-dan-o\\'qing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ─── Modul 3: Models bilan one-to-many bog'lanish ──────────────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # Asosiy! lazy=True — kerakli vaqtda olinadi (performance uchun yaxshi)
    notes = db.relationship('Note', backref='owner', lazy=True, cascade='all, delete-orphan')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # MUHIM: default=datetime.utcnow (qavslarsiz!) — har not uchun yangi vaqt
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Yordamchi: joriy foydalanuvchini olish ────────────────────
def current_user():
    user_id = session.get('user_id')
    return User.query.get(user_id) if user_id else None


def login_required(view):
    \"\"\"Oddiy decorator: login bo'lmagan foydalanuvchini /login ga yuboradi\"\"\"
    from functools import wraps
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash('Avval kirish kerak', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


# ─── Login: yangi foydalanuvchi yaratamiz yoki mavjudini topamiz ─
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if len(username) < 2:
            flash('Ism kamida 2 ta belgidan iborat bo\\'lishi kerak', 'error')
            return redirect(url_for('login'))
        # Mavjud foydalanuvchini topish yoki yangi yaratish
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        flash(f'Xush kelibsiz, {username}!', 'success')
        return redirect(url_for('list_notes'))
    return render_template_string(LOGIN_HTML)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ─── R (Read): faqat O'Z notalarimni ko'rish ──────────────────
@app.route('/')
@app.route('/notes')
@login_required
def list_notes():
    user = current_user()
    # MUHIM: filter_by(user_id=user.id) — boshqalarning notalari ko'rinmaydi
    notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    return render_template_string(NOTES_HTML, notes=notes, user=user)


# ─── C (Create): yangi nota qo'shish ─────────────────────────
@app.route('/notes/new', methods=['GET', 'POST'])
@login_required
def new_note():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        if not title or not body:
            flash('Sarlavha va matn to\\'ldirilishi kerak', 'error')
            return redirect(url_for('new_note'))
        note = Note(title=title, body=body, user_id=current_user().id)
        db.session.add(note)
        db.session.commit()
        flash('Nota qo\\'shildi', 'success')
        return redirect(url_for('list_notes'))  # PRG pattern
    return render_template_string(NEW_NOTE_HTML)


# ─── U (Update): tahrirlash + xavfsizlik tekshiruvi ──────────
@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    # MUHIM: faqat o'z notangizni tahrirlashingiz mumkin
    if note.user_id != current_user().id:
        abort(403)
    if request.method == 'POST':
        note.title = request.form.get('title', '').strip()
        note.body = request.form.get('body', '').strip()
        db.session.commit()  # add() chaqirish shart emas — obyekt allaqachon session'da
        flash('Nota yangilandi', 'success')
        return redirect(url_for('list_notes'))
    return render_template_string(EDIT_NOTE_HTML, note=note)


# ─── D (Delete): o'chirish (POST orqali — GET xavfsiz emas) ───
@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user().id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Nota o\\'chirildi', 'success')
    return redirect(url_for('list_notes'))


# ─── Templatelar (oddiylik uchun string ichida) ───────────────
LOGIN_HTML = '''<!doctype html><h1>Login</h1>
{% with msgs = get_flashed_messages() %}{% for m in msgs %}<p style="color:red">{{ m }}</p>{% endfor %}{% endwith %}
<form method="post"><input name="username" required minlength="2"><button>Kirish</button></form>'''

NOTES_HTML = '''<!doctype html><h1>{{ user.username }} ning notalari</h1>
<p><a href="{{ url_for('new_note') }}">+ Yangi nota</a> | <a href="{{ url_for('logout') }}">Chiqish</a></p>
{% with msgs = get_flashed_messages() %}{% for m in msgs %}<p style="color:green">{{ m }}</p>{% endfor %}{% endwith %}
{% for n in notes %}
  <div style="border:1px solid #ccc;padding:1em;margin:0.5em 0">
    <h3>{{ n.title }}</h3><p>{{ n.body }}</p>
    <small>{{ n.created_at.strftime('%d-%b %H:%M') }}</small>
    <a href="{{ url_for('edit_note', note_id=n.id) }}">✎ Tahrirlash</a>
    <form method="post" action="{{ url_for('delete_note', note_id=n.id) }}" style="display:inline">
      <button onclick="return confirm('O\\'chirishni xohlaysizmi?')">🗑</button>
    </form>
  </div>
{% else %}
  <p>Hali notalar yo'q.</p>
{% endfor %}'''

NEW_NOTE_HTML = '''<!doctype html><h1>Yangi nota</h1>
<form method="post">
  <input name="title" placeholder="Sarlavha" required><br>
  <textarea name="body" placeholder="Matn" required></textarea><br>
  <button>Saqlash</button>
</form>'''

EDIT_NOTE_HTML = '''<!doctype html><h1>Tahrirlash</h1>
<form method="post">
  <input name="title" value="{{ note.title }}" required><br>
  <textarea name="body" required>{{ note.body }}</textarea><br>
  <button>Yangilash</button>
</form>'''


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
"""


R3_TEXT = """\
<h2>Takrorlash: Modul 4 — Blueprint va JSON API</h2>

<pre class="mermaid">
flowchart TB
    F["create_app"] --> A["Flask"]
    A --> AB["auth_bp at /api/auth"]
    A --> NB["notes_bp at /api/notes"]
    AB --> LOGIN["POST login"]
    AB --> LOGOUT["POST logout"]
    NB --> G["GET list"]
    NB --> P["POST create"]
    NB --> PUT["PUT update"]
    NB --> DEL["DELETE remove"]
    G -->|jsonify 200| C["Client React Vue mobile"]
    P -->|jsonify 201| C
    PUT -->|jsonify 200| C
    DEL -->|empty 204| C
    LOGIN -.->|session set| C
</pre>

<p>Modul 4 da siz katta loyihalarni <strong>Blueprint</strong>'lar orqali qismlarga bo'lish va JSON <strong>REST API</strong> yaratishni o'rgandingiz. Endi vaqt keldi — Modul 3 da yaratgan notlar ilovasini professional struktura va REST API ga aylantirishimiz mumkin.</p>

<h3>📋 Modul 4 da nimalarni o'rgangansiz</h3>
<table style="border-collapse:collapse;width:100%;margin:1em 0">
  <thead>
    <tr style="background:#f3f4f6">
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Konsept</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Kod</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Blueprint yaratish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>notes_bp = Blueprint('notes', __name__)</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Blueprint'ni ulash</td><td style="padding:8px;border:1px solid #e5e7eb"><code>app.register_blueprint(notes_bp, url_prefix='/api/notes')</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">app factory</td><td style="padding:8px;border:1px solid #e5e7eb"><code>def create_app(): app = Flask(__name__); ...; return app</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">JSON qaytarish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>return jsonify({'id': n.id, 'title': n.title})</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">JSON qabul qilish</td><td style="padding:8px;border:1px solid #e5e7eb"><code>data = request.get_json()</code></td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb">Status kodlari</td><td style="padding:8px;border:1px solid #e5e7eb"><code>return jsonify(...), 201</code></td></tr>
  </tbody>
</table>

<h3>📊 HTTP status kodlari — eslab qoling</h3>
<table style="border-collapse:collapse;width:100%;margin:1em 0">
  <thead>
    <tr style="background:#f3f4f6">
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Kod</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Ma'no</th>
      <th style="padding:8px;border:1px solid #e5e7eb;text-align:left">Qachon ishlatiladi</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>200</strong></td><td style="padding:8px;border:1px solid #e5e7eb">OK</td><td style="padding:8px;border:1px solid #e5e7eb">GET muvaffaqiyatli (default)</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>201</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Created</td><td style="padding:8px;border:1px solid #e5e7eb">POST — yangi resurs yaratildi</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>204</strong></td><td style="padding:8px;border:1px solid #e5e7eb">No Content</td><td style="padding:8px;border:1px solid #e5e7eb">DELETE muvaffaqiyatli (jisman hech narsa qaytarmaydi)</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>400</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Bad Request</td><td style="padding:8px;border:1px solid #e5e7eb">Mijoz xatosi (JSON noto'g'ri, maydon yo'q)</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>401</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Unauthorized</td><td style="padding:8px;border:1px solid #e5e7eb">Login qilinmagan</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>403</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Forbidden</td><td style="padding:8px;border:1px solid #e5e7eb">Login qilingan lekin ruxsat yo'q</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>404</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Not Found</td><td style="padding:8px;border:1px solid #e5e7eb">Resurs topilmadi</td></tr>
    <tr><td style="padding:8px;border:1px solid #e5e7eb"><strong>500</strong></td><td style="padding:8px;border:1px solid #e5e7eb">Server Error</td><td style="padding:8px;border:1px solid #e5e7eb">Bizning xatomiz (exception)</td></tr>
  </tbody>
</table>

<h3>🏗 Loyiha tuzilishi — yaxshi va yomon</h3>
<p><strong>Yomon (hammasi bitta faylda):</strong></p>
<pre><code>app.py    # 500 qator, hammasi shu yerda
notes.db</code></pre>
<p><strong>Yaxshi (Blueprint + app factory):</strong></p>
<pre><code>app/
  __init__.py        # create_app() factory
  models.py          # User, Note modellari
  auth/
    __init__.py
    routes.py        # /api/auth/login, /api/auth/logout
  notes/
    __init__.py
    routes.py        # /api/notes (CRUD)
run.py               # entry point: from app import create_app; create_app().run()
config.py            # ConfigBase, DevConfig, ProdConfig</code></pre>

<h3>🧪 API ni qanday tekshirish — curl</h3>
<pre><code># Barcha notalarni olish
curl http://localhost:5000/api/notes

# Yangi nota yaratish
curl -X POST http://localhost:5000/api/notes \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Test", "body": "Salom"}'

# Bittasini olish
curl http://localhost:5000/api/notes/1

# Yangilash
curl -X PUT http://localhost:5000/api/notes/1 \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Yangilangan"}'

# O'chirish
curl -X DELETE http://localhost:5000/api/notes/1</code></pre>

<h3>⚠️ Modul 4 da eng ko'p uchraydigan xatolar</h3>
<ul>
  <li><strong>url_prefix ni unutish</strong>: <code>app.register_blueprint(notes_bp)</code> da prefix bermasangiz, route'lar to'qnashishi mumkin.</li>
  <li><strong>request.json vs request.get_json()</strong>: get_json() tavsiya etiladi — <code>force=True</code>, <code>silent=True</code> kabi opsiyalar bor.</li>
  <li><strong>Status kod 200 ni har joyga qo'yish</strong>: POST → 201, DELETE → 204, xato → 400/404. To'g'ri kodlar mijozga aniq ma'lumot beradi.</li>
  <li><strong>Xato javobni JSON sifatida qaytarmaslik</strong>: API foydalanuvchilar HTML xato sahifasini parse qila olmaydi. Doim <code>jsonify({'error': '...'}), 400</code> qaytaring.</li>
  <li><strong>Foydalanuvchi tekshiruvini API'da unutish</strong>: web routes'larda <code>if not current_user()</code> bor, lekin API endpoint'larda buni qayta yozing — yangi developer e'tibordan chetda qoldirishi mumkin.</li>
</ul>

<h3>🎯 Endi navbat sizda</h3>
<p>Pastdagi kod — to'liq REST API. Bu R2 dagi notlar ilovasining API versiyasi. Endi siz har qanday frontend (React, Vue, mobile app) bilan ishlay olasiz. Birinchi navbatda kodni o'qib chiqing va curl bilan har endpoint'ni tekshirib ko'ring. Keyin o'z loyihangizga o'ting.</p>
"""

R3_CODE = """\
# notes_api.py — to'liq Notes REST API (Blueprint + app factory + JSON)
# R2 dagi notlar ilovasini API ga o'tkazamiz.
from flask import Flask, Blueprint, request, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ─── Modellar (R2 dagi bilan bir xil) ──────────────────────────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    notes = db.relationship('Note', backref='owner', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {'id': self.id, 'username': self.username}


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        \"\"\"Serializatsiya — JSON ga aylantirish uchun\"\"\"
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
        }


# ─── Auth Blueprint: /api/auth/login, /api/auth/logout ─────────
auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if len(username) < 2:
        return jsonify({'error': 'username kamida 2 ta belgi'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return jsonify({'user': user.to_dict(), 'message': 'Login muvaffaqiyatli'}), 200


@auth_bp.post('/logout')
def logout():
    session.clear()
    return '', 204  # No Content


@auth_bp.get('/me')
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Login qilinmagan'}), 401
    user = User.query.get(user_id)
    return jsonify({'user': user.to_dict()}), 200


# ─── Notes Blueprint: /api/notes (CRUD) ────────────────────────
notes_bp = Blueprint('notes', __name__)


def require_login():
    \"\"\"Yordamchi: 401 qaytaradi yoki current user'ni qaytaradi\"\"\"
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@notes_bp.get('')
def list_notes():
    user = require_login()
    if not user:
        return jsonify({'error': 'Avval kirish kerak'}), 401
    notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    return jsonify({'notes': [n.to_dict() for n in notes]}), 200


@notes_bp.post('')
def create_note():
    user = require_login()
    if not user:
        return jsonify({'error': 'Avval kirish kerak'}), 401
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    if not title or not body:
        return jsonify({'error': 'title va body to\\'ldirilishi kerak'}), 400
    note = Note(title=title, body=body, user_id=user.id)
    db.session.add(note)
    db.session.commit()
    return jsonify({'note': note.to_dict()}), 201  # Created


@notes_bp.get('/<int:note_id>')
def get_note(note_id):
    user = require_login()
    if not user:
        return jsonify({'error': 'Avval kirish kerak'}), 401
    note = Note.query.get_or_404(note_id)
    if note.user_id != user.id:
        return jsonify({'error': 'Ruxsat yo\\'q'}), 403
    return jsonify({'note': note.to_dict()}), 200


@notes_bp.put('/<int:note_id>')
def update_note(note_id):
    user = require_login()
    if not user:
        return jsonify({'error': 'Avval kirish kerak'}), 401
    note = Note.query.get_or_404(note_id)
    if note.user_id != user.id:
        return jsonify({'error': 'Ruxsat yo\\'q'}), 403
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        note.title = (data['title'] or '').strip()
    if 'body' in data:
        note.body = (data['body'] or '').strip()
    db.session.commit()
    return jsonify({'note': note.to_dict()}), 200


@notes_bp.delete('/<int:note_id>')
def delete_note(note_id):
    user = require_login()
    if not user:
        return jsonify({'error': 'Avval kirish kerak'}), 401
    note = Note.query.get_or_404(note_id)
    if note.user_id != user.id:
        return jsonify({'error': 'Ruxsat yo\\'q'}), 403
    db.session.delete(note)
    db.session.commit()
    return '', 204  # No Content


# ─── App factory pattern ───────────────────────────────────────
def create_app():
    app = Flask(__name__)
    app.secret_key = 'maxfiy-kalit-prod-da-environment-dan-o\\'qing'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_api.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    # Blueprint'larni ulash, har biriga URL prefiks beriladi
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    create_app().run(debug=True)
"""


# Each lesson has 5 mixed-type, auto-gradable exercises:
#   - 2× multiple_choice (single answer)
#   - 1× multiple_choice (is_multiple_select=True)
#   - 1× drag_and_drop  (correct_order = JSON list of strings, IN ORDER)
#   - 1× text_input     (AI-graded via expected_answer)
#
# Grading contract (verified in app/services/exercise_service.py):
#   multiple_choice  correct_answers = "B" or "A,C"  (letters, set-compared)
#   drag_and_drop    correct_order   = JSON list of strings (exact order)
#   text_input       expected_answer = model answer (passed to AI grader)
#
# options/drag_items/correct_order are stored as Text columns; we json.dumps
# them before insert. parseListField on the frontend handles both JSON and CSV.
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
# Per-lesson assignments (mapped by lesson `order`). Wired into Lesson.task_*
# fields by the seed loop. Lessons 7–11 build one progressive "Notlar" app.
#
#   title         → Lesson.task_title         (shown as project label)
#   description   → Lesson.task_description   (what to build)
#   requirements  → Lesson.task_requirements  (acceptance criteria)
#   technologies  → Lesson.task_technologies  (allowed stack)
#   deadline_days → Lesson.task_deadline_days (1..365)
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {  # 1-Flaskga kirish
        "title": "Salomlashish ilovasi",
        "description": (
            "Flask'da bitta sahifali \"Salom, men <ism>!\" ilovasini yarating. "
            "/ route bosh sahifa, /time route hozirgi vaqtni ko'rsatsin."
        ),
        "requirements": (
            "• 2 ta route: / va /time\n"
            "• requirements.txt faylida flask kutubxonasi ko'rsatilgan\n"
            "• app.run(debug=True) bilan ishga tushadi\n"
            "• GitHub repo va README.md (qanday ishga tushirish)"
        ),
        "technologies": "Python 3.10+, Flask",
        "deadline_days": 3,
    },
    1: {  # 2-Routing va URL
        "title": "Mening profilim sayti",
        "description": (
            "3 ta route'li mini-sayt: / (bosh sahifa), /about (siz haqingizda), "
            "/hello/<name> (dinamik URL parametr orqali salomlashish)."
        ),
        "requirements": (
            "• Kamida 3 ta route, jumladan dinamik <name> parametri\n"
            "• Sahifalar orasida url_for() bilan link'lar\n"
            "• README'da har bir route uchun misol URL ko'rsatilgan"
        ),
        "technologies": "Python, Flask, url_for, dynamic URL parameters",
        "deadline_days": 4,
    },
    2: {  # 3-Jinja2 templates
        "title": "Retsept sayti (Jinja2)",
        "description": (
            "Bosh sahifada 5+ retsept ro'yxati, har biriga bosish — detali sahifa. "
            "Jinja2 for/if va template inheritance (base.html) qo'llang."
        ),
        "requirements": (
            "• base.html (template inheritance) mavjud\n"
            "• Kamida 5 ta retsept (Python list yoki dict)\n"
            "• Ro'yxat {% for %} orqali generatsiya qilingan\n"
            "• Narxi 0 bo'lganda \"Bepul\" deb {% if %} bilan chiqsin\n"
            "• Har retseptga detali sahifa (/recipes/<id>)"
        ),
        "technologies": "Python, Flask, Jinja2, HTML, CSS",
        "deadline_days": 5,
    },
    3: {  # 4-Static fayllar va GET form
        "title": "Mahsulot qidiruv (GET form)",
        "description": (
            "CSS bilan stillangan sahifa, qidiruv GET formasi (?q=...). "
            "Kamida 8 ta mahsulot Python list ichida, kirit so'zga ko'ra "
            "filtrlash, natijalar pastda ro'yxat shaklida."
        ),
        "requirements": (
            "• static/style.css mavjud va url_for orqali ulangan\n"
            "• GET form ishlaydi, request.args.get('q') orqali olinadi\n"
            "• Bo'sh natija holati: \"Hech narsa topilmadi\" xabari\n"
            "• Filtr katta/kichik harf farqlamasin (case-insensitive)"
        ),
        "technologies": "Python, Flask, HTML, CSS, GET form, static files",
        "deadline_days": 5,
    },
    4: {  # 5-POST formani qabul qilish
        "title": "Fikr-mulohaza formasi",
        "description": (
            "Ism, email va xabar maydonlarini qabul qiluvchi POST forma. "
            "Yuborilganidan keyin \"Rahmat\" sahifasi yuborilgan ma'lumotlarni "
            "ko'rsatadi. Server tomonida validatsiya bo'lishi shart."
        ),
        "requirements": (
            "• POST forma ishlaydi (method=\"POST\")\n"
            "• Server-side validation: bo'sh maydonlar uchun xato xabari\n"
            "• Email tarkibida @ borligi tekshiriladi\n"
            "• Success sahifasi yuborilgan ism va xabarni ko'rsatadi\n"
            "• POST'dan keyin sahifa qaytarib yuklanmaslik uchun redirect (PRG)"
        ),
        "technologies": "Python, Flask, HTML, POST form, request.form, redirect",
        "deadline_days": 5,
    },
    5: {  # 6-Session va cookies
        "title": "Oddiy login (session)",
        "description": (
            "Hardcoded user (admin/1234) bilan login sistemasi. Muvaffaqiyatli "
            "login session'ga yoziladi. /dashboard sahifasi faqat login bo'lgan "
            "foydalanuvchi uchun. /logout session'ni tozalaydi."
        ),
        "requirements": (
            "• secret_key o'rnatilgan (lekin GitHub'ga commit qilinmagan)\n"
            "• /login (GET+POST), /dashboard (faqat login bo'lganlar), /logout\n"
            "• Login'siz /dashboard ga kirsa — /login ga redirect\n"
            "• Session orqali username saqlanadi va dashboardda ko'rinadi\n"
            "• Logout dan keyin /dashboard yana yopiq bo'lib qoladi"
        ),
        "technologies": "Python, Flask, session, secret_key, redirect, url_for",
        "deadline_days": 6,
    },
    6: {  # R1-Mehmonlar kitobi (REVISION of Modules 1+2)
        "title": "🔁 R1: Mehmonlar kitobi (Guest Book)",
        "description": (
            "Modul 1+2 takrori: routes + templates + forms + session ni birga ishlatib "
            "to'liq Mehmonlar kitobi ilovasini quring. Foydalanuvchilar ro'yxatdan o'tib, "
            "xabar qoldira oladigan oddiy lekin to'liq sayt."
        ),
        "requirements": (
            "• 4 ta route: / (bosh sahifa), /login (GET+POST), /post (POST), /logout (GET)\n"
            "• Login session orqali ishlaydi (app.secret_key o'rnatilgan)\n"
            "• Login bo'lmagan foydalanuvchi /post ga POST qila olmasin (redirect + flash)\n"
            "• Bosh sahifa Jinja2 template orqali render qilinadi (oxirgi 20 ta xabar yuqorida)\n"
            "• Har xabar yonida: author + matn + vaqt\n"
            "• Logout dan keyin session tozalanadi va siz endi xabar yoza olmaysiz\n"
            "• Bonus: bir xil matnli xabarni ketma-ket ikki marta yuborish bloklansin"
        ),
        "technologies": "Python, Flask, Jinja2, session, flash, POST form, redirect (PRG)",
        "deadline_days": 5,
    },
    7: {  # 7-Database (SQLAlchemy)
        "title": "Notlar ilovasi v1 — Model",
        "description": (
            "Flask-SQLAlchemy bilan Note modelini yarating (id, title, body, "
            "created_at). Bosh sahifa bazadagi barcha notlarni ro'yxat "
            "shaklida ko'rsatsin. Boshlang'ich uchun kamida 3 ta nota seed qiling. "
            "Bu loyiha 8-11 darslarda kengaytiriladi — yaxshi asos qo'ying!"
        ),
        "requirements": (
            "• Note modeli: id (PK), title (String 200), body (Text), created_at (DateTime)\n"
            "• SQLite bazasi (app.db) ishlaydi, db.create_all() chaqirilgan\n"
            "• Bosh sahifada notlar ro'yxati (yangi notlar yuqorida)\n"
            "• Kamida 3 ta seed nota (skript yoki Flask shell orqali)\n"
            "• README'da loyihani ishga tushirish bo'yicha aniq qadamlar"
        ),
        "technologies": "Python, Flask, Flask-SQLAlchemy, SQLite",
        "deadline_days": 7,
    },
    8: {  # 8-CRUD operatsiyalar
        "title": "Notlar ilovasi v2 — CRUD",
        "description": (
            "7-darsdagi Notlar ilovasini kengaytiring: yangi not qo'shish, "
            "tahrirlash, o'chirish. Har bir amaldan keyin flash xabar va "
            "PRG pattern bilan redirect."
        ),
        "requirements": (
            "• Create: /notes/new (GET forma + POST yaratish)\n"
            "• Read: bosh sahifada ro'yxat + /notes/<id> detali\n"
            "• Update: /notes/<id>/edit (GET forma + POST yangilash)\n"
            "• Delete: /notes/<id>/delete (POST orqali)\n"
            "• Har amaldan keyin flash() xabar va redirect (PRG pattern)\n"
            "• Mavjud bo'lmagan id uchun 404"
        ),
        "technologies": "Python, Flask, SQLAlchemy, flash, redirect, url_for",
        "deadline_days": 7,
    },
    9: {  # R2-Shaxsiy yozuvlar (REVISION of Module 3)
        "title": "🔁 R2: Shaxsiy yozuvlar (Personal Notes)",
        "description": (
            "Modul 3 takrori: Modul 2 dagi session + Modul 3 dagi SQLAlchemy CRUD ni birlashtirib "
            "ko'p-foydalanuvchili Notlar ilovasini quring. Har bir foydalanuvchi faqat o'z notalarini "
            "ko'radi va tahrirlay oladi."
        ),
        "requirements": (
            "• Ikkita model: User (id, username) va Note (id, title, body, user_id, created_at)\n"
            "• db.relationship + ForeignKey orqali bog'lanish, cascade delete-orphan\n"
            "• /login — username yuboradi, mavjud bo'lmasa yangi User yaratiladi, session['user_id'] o'rnatiladi\n"
            "• /notes — faqat shu foydalanuvchining notalari (filter_by(user_id=...))\n"
            "• Full CRUD: /notes/new, /notes/<id>/edit, /notes/<id>/delete\n"
            "• MUHIM: edit va delete'da note.user_id != session['user_id'] bo'lsa abort(403)\n"
            "• PRG pattern + flash xabarlar\n"
            "• /logout session ni tozalaydi"
        ),
        "technologies": "Python, Flask, SQLAlchemy, session, ForeignKey, relationship, login pattern",
        "deadline_days": 7,
    },
    10: {  # 9-Blueprint va app factory
        "title": "Notlar ilovasi v3 — Blueprint",
        "description": (
            "8-darsdagi ilovani Blueprint'larga ajrating: main_bp (bosh sahifa, "
            "about) va notes_bp (CRUD). create_app() factory pattern qo'llang. "
            "app.py faqat factory'ni chaqirsin."
        ),
        "requirements": (
            "• Kamida 2 ta Blueprint: main_bp va notes_bp\n"
            "• create_app() funksiyasi mavjud va Flask app'ni qaytaradi\n"
            "• app.py faqat factory chaqiruvi (3-5 qator)\n"
            "• Ilova 8-darsdagi versiyasi kabi to'liq ishlashi shart\n"
            "• Loyiha tuzilishi: app/__init__.py, app/main/, app/notes/"
        ),
        "technologies": "Python, Flask, Blueprint, app factory pattern",
        "deadline_days": 7,
    },
    11: {  # 10-JSON API
        "title": "Notlar ilovasi v4 — REST API",
        "description": (
            "9-darsdagi ilovaga JSON API endpoint'lari qo'shing. To'g'ri HTTP "
            "status kodlari (200, 201, 404). curl yoki Postman bilan tekshirib "
            "ko'ring."
        ),
        "requirements": (
            "• GET /api/notes — barcha notlar JSON (200)\n"
            "• GET /api/notes/<id> — bitta nota (200 yoki 404)\n"
            "• POST /api/notes — yangi not yaratish (201, JSON tanada title+body)\n"
            "• DELETE /api/notes/<id> — o'chirish (204 yoki 404)\n"
            "• Web UI (CRUD) ham ishlashda davom etadi\n"
            "• README'da har bir endpoint uchun curl misoli"
        ),
        "technologies": "Python, Flask, jsonify, request.json, REST, HTTP status codes",
        "deadline_days": 7,
    },
    12: {  # R3-Notes REST API (REVISION of Module 4)
        "title": "🔁 R3: Notes REST API (to'liq)",
        "description": (
            "Modul 4 takrori: R2 dagi Shaxsiy notlar ilovasini Blueprint struktura va to'liq "
            "JSON REST API ga o'tkazing. Endi sizning bekendingiz har qanday frontend (React, mobil) "
            "bilan ishlay oladi."
        ),
        "requirements": (
            "• 2 ta Blueprint: auth_bp (/api/auth/...) va notes_bp (/api/notes/...)\n"
            "• create_app() factory pattern\n"
            "• POST /api/auth/login — {username} qabul qiladi, session o'rnatadi, 200 + user JSON\n"
            "• POST /api/auth/logout — 204 No Content\n"
            "• GET /api/auth/me — login bo'lgan foydalanuvchi haqida ma'lumot (401 agar yo'q)\n"
            "• GET /api/notes — login bo'lgan foydalanuvchining notalari (200)\n"
            "• POST /api/notes — yangi nota yaratish (201)\n"
            "• GET/PUT/DELETE /api/notes/<id> — to'g'ri status kodlar (200/204/403/404)\n"
            "• Barcha xato javoblari JSON formatida: {'error': '...'}\n"
            "• README'da curl misollari har bir endpoint uchun"
        ),
        "technologies": "Python, Flask, Blueprint, jsonify, request.get_json, REST, HTTP status codes, session-based auth",
        "deadline_days": 10,
    },
    13: {  # 11-Deployga tayyorlash (CAPSTONE)
        "title": "🚀 CAPSTONE: Notlar ilovasini internetga chiqarish",
        "description": (
            "7–10 darslarda yaratgan to'liq Notlar ilovasini bepul hosting'ga "
            "(Render, PythonAnywhere yoki Railway) deploy qiling. Bu kursning "
            "yakuniy ishi — diqqat bilan, README ni mukammal yozing va tirik "
            "ishlaydigan demo URL'ni topshiring."
        ),
        "requirements": (
            "• Tirik demo URL ochiladi va ishlaydi (Render/PythonAnywhere/Railway)\n"
            "• secret_key .env dan o'qiladi (hardcode qilinmagan, .env .gitignore'da)\n"
            "• .gitignore, requirements.txt, Procfile (yoki ekvivalent) mavjud\n"
            "• Production'da DEBUG=False\n"
            "• gunicorn orqali ishga tushadi\n"
            "• README to'liq: lokal o'rnatish + deploy qadamlari + demo URL\n"
            "• Web UI + REST API ham prod'da ishlaydi"
        ),
        "technologies": "Python, Flask, gunicorn, .env (python-dotenv), Render/PythonAnywhere/Railway, git",
        "deadline_days": 14,
    },
}


LESSONS = [
    {
        "order": 0, "title": "1-Flaskga kirish",
        "text": L1_TEXT, "code": L1_CODE, "lang": "python",
        "video": "https://youtu.be/Z1RJmh_OqeA",
        "exercises": [
            mc("Flask nima?",
               ["Python uchun ma'lumotlar bazasi boshqaruv tizimi",
                "Python'da web ilovalar yozish uchun mikro framework",
                "Faqat frontend uchun JavaScript kutubxonasi",
                "Linux operatsion tizimi distributivi"],
               "B", hint="U server tomonda ishlaydi va 'mikro' deyiladi.",
               explanation="Flask — Python'da web ilovalar yozish uchun yengil (mikro) framework.",
               diff="Easy", pts=2),
            mc("virtualenv nima uchun kerak?",
               ["Kodni avtomatik tezlashtirish uchun",
                "Har bir loyihaning kutubxonalarini alohida, izolyatsiyalangan saqlash uchun",
                "Internetga ulanish uchun",
                "HTML shablonlarni yozish uchun"],
               "B", hint="Ikki loyiha bir xil kutubxonaning turli versiyalarini talab qilsa-chi?",
               diff="Easy", pts=2),
            mc("Flask ilovasini ishga tushirishning to'g'ri usullarini tanlang",
               ["python app.py   (faylda if __name__ == '__main__' bloki bo'lsa)",
                "flask run   (FLASK_APP belgilangan bo'lsa)",
                "run app.py",
                "python -m flask start"],
               "A,B", multi=True,
               hint="Ikki haqiqiy variant bor; qolgan ikkitasi mavjud komanda emas.",
               diff="Medium", pts=3),
            dd("Minimal Flask ilovasini yaratish bosqichlarini to'g'ri tartibda joylang",
               ["from flask import Flask",
                "app = Flask(__name__)",
                "@app.route('/') dekoratori bilan funksiya yozish",
                "app.run(debug=True)"],
               hint="Avval import, keyin ilova obyekti, keyin route, oxirida ishga tushirish.",
               diff="Medium", pts=3),
            ti("__name__ ni Flask konstruktoriga nima uchun beramiz?",
               "__name__ Flask'ga ilova qaysi modul/papkada joylashganini bildiradi. "
               "Flask shu ma'lumot orqali templates/ va static/ papkalarini qayerdan qidirishni aniqlaydi.",
               hint="Flask templates va static fayllarini qayerdan qidirishini qanday biladi?",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 1, "title": "2-Routing va URL",
        "text": L2_TEXT, "code": L2_CODE, "lang": "python",
        "video": "https://youtu.be/H4qPV6OS5LM",
        "exercises": [
            mc("@app.route('/') dekoratori asosan nima qiladi?",
               ["HTML faylni o'qiydi",
                "URL ni Python funksiyaga bog'laydi",
                "Ma'lumotlar bazasini sozlaydi",
                "JavaScript faylga havola yaratadi"],
               "B", diff="Easy", pts=2),
            mc("<int:id> URL converter'i nima qiladi?",
               ["Faqat butun son qabul qiladi va id parametriga uzatadi",
                "Faqat satr qabul qiladi",
                "Sessiyaga ID saqlaydi",
                "Bazadan id ni avtomatik oladi"],
               "A", hint="/post/42 ishlaydi, /post/abc esa 404 qaytaradi — nima uchun?",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari to'g'ri url_for chaqirig'i?",
               ["url_for('home')",
                "url_for('user_page', username='aziz')",
                "url_for('/about')",
                "url_for(home)  # tirnoqsiz"],
               "A,B", multi=True,
               hint="url_for endpoint NOMINI string sifatida qabul qiladi.",
               diff="Medium", pts=3),
            dd("HTTP so'rovi qabul qilingandan keyingi bosqichlarni to'g'ri tartibda joylang",
               ["Brauzer URL ga so'rov yuboradi",
                "Flask URL ni route bilan solishtiradi",
                "Mos kelgan funksiya chaqiriladi",
                "Funksiya javob qaytaradi",
                "Brauzer javobni ko'rsatadi"],
               diff="Medium", pts=3),
            ti("methods=['GET', 'POST'] parametri qachon kerak bo'ladi?",
               "Odatda @app.route faqat GET so'rovlarini qabul qiladi. Forma yuborish (POST), "
               "PUT, DELETE yoki boshqa methodlarni ham qabul qilish uchun methods parametrida ularni "
               "aniq ko'rsatish kerak.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 2, "title": "3-Jinja2 templates",
        "text": L3_TEXT, "code": L3_CODE, "lang": "python",
        "video": "https://youtu.be/QnDWIZuWYW0",
        "exercises": [
            mc("render_template fayllarni qaysi papkadan qidiradi?",
               ["src/", "views/", "templates/", "html/"],
               "C", diff="Easy", pts=2),
            mc("{{ name }} va {% if %} orasidagi farq nima?",
               ["Birinchisi sikl, ikkinchisi shart",
                "{{ }} qiymatni chiqaradi, {% %} esa boshqaruv konstruksiyasi (if/for/...)",
                "{{ }} faqat HTML uchun, {% %} CSS uchun",
                "Hech qanday farq yo'q"],
               "B", diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari haqiqiy Jinja2 filtrlari?",
               ["| upper", "| length", "| sort", "| encrypt"],
               "A,B,C", multi=True,
               hint="Bittasi Jinja2 da mavjud emas — qaysi biri shifrlash bilan bog'liq?",
               diff="Medium", pts=3),
            dd("Jinja2 if/else blokini to'g'ri tartibda joylang",
               ["{% if condition %}",
                "Agar shart bajarilsa, bu HTML chiqadi",
                "{% else %}",
                "Aks holda, bu HTML chiqadi",
                "{% endif %}"],
               diff="Medium", pts=3),
            ti("Jinja2 nega avtomatik HTML escape qiladi?",
               "XSS (Cross-Site Scripting) hujumlardan himoyalanish uchun. Foydalanuvchi kiritgan "
               "ma'lumotda HTML yoki JavaScript bo'lsa, Jinja2 uni avtomatik escape qiladi va "
               "brauzer uni matn sifatida ko'rsatadi, kod sifatida ishga tushirmaydi.",
               diff="Hard", pts=4),
            mc("{{ items | length }} filtri nima qaytaradi?",
               ["items ro'yxatini sortlaydi",
                "items ro'yxatining uzunligini (elementlar sonini) qaytaradi",
                "items ichidagi har bir elementni chiqaradi",
                "items ro'yxatini bo'shatadi"],
               "B", hint="length so'zining ingliz tilidagi ma'nosini eslang.",
               diff="Easy", pts=2),
            ti("{% for item in items %}...{% endfor %} qanday ishlaydi va qaysi vaziyatlarda ishlatiladi?",
               "Bu Jinja2 sikl. Python list yoki har qanday iterable obyekt elementlari bo'ylab "
               "aylanadi va har bir element uchun ichidagi HTML bloki takrorlanadi. Foydalanuvchilar "
               "ro'yxati, mahsulotlar jadvali, blog postlari kabi takrorlanuvchi ma'lumotlarni "
               "shablonda ko'rsatish uchun ishlatiladi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 3, "title": "4-Static fayllar va GET form",
        "text": L4_TEXT, "code": L4_CODE, "lang": "python",
        "video": "https://youtu.be/3mwFC4SHY-Y",
        "exercises": [
            mc("static/ papkasi nimaga ishlatiladi?",
               ["HTML shablonlar",
                "CSS, JavaScript, rasm — o'zgarmaydigan resurslar",
                "Ma'lumotlar bazasi fayllari",
                "Python modullari"],
               "B", diff="Easy", pts=2),
            mc("CSS faylga shablonda eng to'g'ri havola qaysi biri?",
               ["<link href=\"style.css\">",
                "<link href=\"{{ url_for('static', filename='style.css') }}\">",
                "<link href=\"/css/style.css\">",
                "{% load static %}{% static 'style.css' %}"],
               "B", hint="url_for static papkasi yo'lini o'zgartirsa ham ishlashda davom etadi.",
               diff="Easy", pts=2),
            mc("GET form haqida qaysi gaplar to'g'ri?",
               ["Ma'lumot URL query string ga qo'shiladi (?q=...)",
                "Server ma'lumotni request.args.get orqali oladi",
                "Faqat oz miqdordagi ma'lumot uchun mos",
                "Parol yuborish uchun ideal"],
               "A,B,C", multi=True,
               hint="Parol URL'da ko'rinib qolsa — yaxshi g'oya bo'lmaydi.",
               diff="Medium", pts=3),
            dd("GET form ishlash bosqichlarini tartiblang",
               ["Foydalanuvchi formani to'ldiradi",
                "Submit tugmasini bosadi",
                "Brauzer URL'ga ?q=qiymat qo'shadi",
                "Server request.args.get('q') orqali qiymatni oladi",
                "Server javob qaytaradi"],
               diff="Medium", pts=3),
            ti("Nega request.args.get('q') request.args['q']'dan yaxshiroq?",
               "request.args.get('q') parametr yo'q bo'lsa None (yoki default qiymat) qaytaradi. "
               "request.args['q'] esa KeyError chiqaradi va Flask 400 xato bilan javob beradi. "
               "get() xavfsizroq va qulayroq.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 4, "title": "5-POST formani qabul qilish",
        "text": L5_TEXT, "code": L5_CODE, "lang": "python",
        "video": "https://youtu.be/UIJKdCIEXUQ",
        "exercises": [
            mc("POST so'rov GET dan nima bilan farqlanadi?",
               ["Tezroq ishlaydi",
                "Ma'lumotni URL emas, request body orqali yuboradi",
                "Faqat JSON qabul qiladi",
                "Faqat ma'lumotlar bazasi uchun ishlatiladi"],
               "B", diff="Easy", pts=2),
            mc("flash xabarini ko'rsatish uchun qanday sozlama shart?",
               ["flask-flash paketini o'rnatish",
                "app.secret_key ni belgilash",
                "jQuery ulash",
                "Ma'lumotlar bazasi ulash"],
               "B", hint="flash session orqali ishlaydi, session esa imzo uchun kalit kerak.",
               diff="Easy", pts=2),
            mc("PRG (Post/Redirect/Get) pattern nima uchun foydali?",
               ["Sahifa yangilanganda forma qayta yuborilmaydi",
                "URL POST javobi emas, GET URL ko'rsatiladi (toza qoladi)",
                "Brauzer 'Formani qayta yubormoqchimisiz?' so'ramaydi",
                "Forma ma'lumoti shifrlanadi"],
               "A,B,C", multi=True, diff="Medium", pts=3),
            dd("POST formani qayta ishlash tartibini tuzing",
               ["Foydalanuvchi formani to'ldirib yuboradi",
                "Server request.form orqali ma'lumotni oladi",
                "Validatsiya: maydonlar to'g'ri to'ldirilganmi tekshirish",
                "Ma'lumot bazaga saqlanadi",
                "redirect(url_for(...)) bilan javob qaytariladi"],
               diff="Medium", pts=3),
            ti("Validatsiya nima uchun har doim server tomonda ham qilinishi kerak?",
               "Frontend validatsiyasi (HTML required, JavaScript) faqat foydalanuvchi tajribasini "
               "yaxshilaydi, lekin uni chetlab o'tish oson — masalan, DevTools orqali yoki to'g'ridan-"
               "to'g'ri server URL ga curl bilan so'rov yuborish. Server doim mustaqil ravishda "
               "tekshirishi kerak.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 5, "title": "6-Session va cookies",
        "text": L6_TEXT, "code": L6_CODE, "lang": "python",
        "video": "https://youtu.be/CSHx6eCkmv0",
        "exercises": [
            mc("HTTP nima uchun 'stateless' deyiladi?",
               ["Server doim o'chirilgan",
                "Har bir so'rov mustaqil — server kim siz ekanligingizni o'z-o'zidan eslab qolmaydi",
                "Yangi versiyasi yo'q",
                "Faqat statik fayllar uchun ishlatiladi"],
               "B", diff="Easy", pts=2),
            mc("secret_key nima uchun maxfiy bo'lishi kerak?",
               ["Faqat chiroyli ko'rinish uchun",
                "Session imzosini yaratadi — bilsa, har qanday foydalanuvchini 'soxtalashtirish' mumkin",
                "Faqat HTTPS uchun",
                "Foydalanuvchi parolini saqlash uchun"],
               "B", hint="Imzo nima va kim uni yarata oladi?",
               diff="Easy", pts=2),
            mc("session va oddiy cookie orasidagi to'g'ri farqlarni tanlang",
               ["session Flask tomonidan imzolanadi (foydalanuvchi qiymatni o'zgartira olmaydi)",
                "session ham, cookie ham brauzerda saqlanadi",
                "Cookie odatda foydalanuvchi sozlamalari uchun, session esa login uchun ishlatiladi",
                "Cookie session'dan tezroq"],
               "A,B,C", multi=True, diff="Medium", pts=3),
            dd("Login jarayoni bosqichlarini to'g'ri tartibda joylang",
               ["Foydalanuvchi login va parolni yuboradi",
                "Server parolni bazada tekshiradi",
                "session['user_id'] = user.id",
                "Foydalanuvchi dashboard sahifasiga yo'naltiriladi",
                "Keyingi so'rovlarda session orqali kim ekanligi aniqlanadi"],
               diff="Medium", pts=3),
            ti("session.clear() qachon ishlatiladi va nima qiladi?",
               "Logout amalida — foydalanuvchining sessiyadagi barcha ma'lumotlarini (user_id, "
               "username va boshqalar) o'chiradi. Shunda u sahifaga endi anonymous sifatida kiradi. "
               "Parol o'zgartirgandan keyin xavfsizlik uchun ham ishlatiladi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 6, "title": "R1-Mehmonlar kitobi (takrorlash)",
        "text": R1_TEXT, "code": R1_CODE, "lang": "python",
        "video": "",
        "exercises": [
            mc("Quyidagi route Flask'da nimaga mos keladi: @app.route('/post', methods=['POST'])?",
               ["Faqat GET so'rovlarni qabul qiladi",
                "Faqat POST so'rovlarni qabul qiladi",
                "GET va POST ikkalasini qabul qiladi",
                "Hech qaysi so'rovni qabul qilmaydi"],
               "B", hint="methods ro'yxatida nima yozilgan?",
               diff="Easy", pts=2),
            mc("session ishlatish uchun nima eng birinchi sozlanishi kerak?",
               ["app.run(debug=True) qo'shish",
                "app.secret_key o'rnatish",
                "session.init() chaqirish",
                "Hech narsa — session avtomatik ishlaydi"],
               "B", hint="Session imzolanadi — kalit yo'q bo'lsa qanday imzolanadi?",
               diff="Easy", pts=2),
            mc("Jinja2 da foydalanuvchi login bo'lganligini tekshirish uchun qaysi to'g'ri?",
               ["{{ if session.username }} ... {{ endif }}",
                "{% if user %} ... {% endif %}",
                "<? if (user) ?> ... <? endif ?>",
                "@if(user) ... @endif"],
               "B", hint="Jinja2 da boshqarish bloklari {% ... %} ichida.",
               diff="Easy", pts=2),
            mc("Foydalanuvchi /post ga POST so'rov yubordi lekin sessiyada username yo'q. "
               "Eng to'g'ri xatti-harakat qaysi?",
               ["Bo'sh username bilan entry saqlash",
                "302 redirect /login ga, flash('Avval login qiling') bilan",
                "500 xato qaytarish",
                "Sessiyaga 'guest' username yozish va davom etish"],
               "B", hint="Foydalanuvchini boshqa joyga qanday yo'naltirish kerak?",
               diff="Medium", pts=3),
            mc("PRG (POST-Redirect-GET) pattern qaysi muammolarni hal qiladi?",
               ["Sahifa refresh qilinganda formani qayta yuborish",
                "URL bar'da forma ma'lumotlari ko'rinishi",
                "Brauzer 'Back' tugmasi xatosi (POST resubmit warning)",
                "JavaScript yo'q sahifalarda ishlash"],
               "A,C", multi=True,
               hint="POST javobi sifatida HTML qaytarish nimaga olib keladi?",
               diff="Medium", pts=3),
            dd("Foydalanuvchi 'Mehmonlar kitobi'da xabar yozish jarayoni bosqichlarini tartiblang",
               ["Foydalanuvchi /login ga kiradi va ismni yuboradi",
                "Server session['username'] = ism ni o'rnatadi",
                "/ sahifaga redirect bo'ladi",
                "Foydalanuvchi xabarini yozadi va /post ga yuboradi",
                "Server session['username'] borligini tekshiradi",
                "Yangi entry ENTRIES listga qo'shiladi",
                "/ sahifaga redirect bo'ladi va yangi xabar ko'rinadi"],
               diff="Medium", pts=3),
            ti("session.clear() va session.pop('username', None) o'rtasidagi farq nima?",
               "session.clear() — barcha session ma'lumotlarini o'chiradi (username, user_id va boshqalar — hammasi). "
               "session.pop('username', None) — faqat 'username' kalitini o'chiradi, qolgan ma'lumotlar joyida qoladi. "
               "Logout uchun clear() ko'p ishlatiladi (xavfsizroq). Pop esa ma'lum bir narsani olib tashlash uchun — masalan, "
               "flash xabar o'qib bo'lingach uni o'chirish. Yana muhimi: pop() ikkinchi argumenti default — kalit yo'q bo'lsa xatolik chiqmaydi.",
               diff="Hard", pts=4),
            ti("Nima uchun Mehmonlar kitobi misolida xabarlar `ENTRIES.insert(0, entry)` orqali qo'shiladi, append(entry) emas?",
               "insert(0, entry) yangi xabarni list'ning boshiga qo'shadi — shunda eng so'nggi xabar ro'yxatda birinchi (yuqorida) ko'rinadi. "
               "append(entry) esa oxiriga qo'shadi va eski xabarlar yuqorida, yangilar pastda bo'lib qoladi. UX nuqtai nazaridan "
               "foydalanuvchilar odatda eng yangi narsalarni birinchi ko'rishni xohlaydi (Twitter, Telegram, hamma joyda shunday). "
               "Eslatma: real ilovada bu mantiqni database darajasida hal qilamiz — order_by(created_at.desc()).",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 7, "title": "7-Database (SQLAlchemy)",
        "text": L7_TEXT, "code": L7_CODE, "lang": "python",
        "video": "https://youtu.be/cYWiDiIUxQc",
        "exercises": [
            mc("ORM nima?",
               ["Yangi Python kutubxonasi nomi",
                "Bazaga yozuvlarni Python obyektlari sifatida ishlatish imkonini beruvchi tizim",
                "SQL serverlarining yangi standarti",
                "Faqat MySQL uchun ishlaydi"],
               "B", diff="Easy", pts=2),
            mc("primary_key=True nima uchun kerak?",
               ["Yozuvni shifrlaydi",
                "Ustun avtomatik o'sib boruvchi yagona identifikator (id) bo'lishini ta'minlaydi",
                "Ustunga faqat raqam yozilishini ta'minlaydi",
                "Kerakli ustun ekanligini bildiradi"],
               "B", diff="Easy", pts=2),
            mc("db.session.add() haqida qaysi gaplar to'g'ri?",
               ["Yangi yozuvni sessiyaga qo'shadi",
                "Bazaga yozish uchun keyin commit() ham chaqirish kerak",
                "Darhol bazaga yozadi",
                "Mavjud yozuvni o'zgartirish uchun ham har safar chaqirish kerak"],
               "A,B", multi=True,
               hint="add() va commit() ikki alohida bosqich.",
               diff="Medium", pts=3),
            dd("Yangi yozuv qo'shish bosqichlarini tartiblang",
               ["user = User(name='Aziz', email='aziz@example.com')",
                "db.session.add(user)",
                "db.session.commit()",
                "Endi user.id qiymatga ega",
                "Boshqa joyda user obyektidan foydalanish"],
               diff="Medium", pts=3),
            ti("Nima uchun db.create_all() faqat yangi jadvallarni yaratadi, mavjudini o'zgartirmaydi?",
               "create_all() mavjud jadvallarni o'zgartirsa, undagi ma'lumotlar yo'qolishi yoki "
               "buzilishi mumkin. Schema o'zgartirish uchun Flask-Migrate (Alembic) kabi migration "
               "vositalari ishlatiladi — ular o'zgarishlarni xavfsiz, qadama-qadam qo'llaydi.",
               diff="Hard", pts=4),
            mc("User.query.filter_by(username='aziz').first() nima qaytaradi?",
               ["Birinchi foydalanuvchini (har qanday)",
                "username='aziz' bo'lgan birinchi foydalanuvchini, topilmasa None",
                "Aziz nomli barcha foydalanuvchilarni",
                "SQL so'rovni matn ko'rinishida"],
               "B", diff="Easy", pts=2),
            ti("nullable=False va unique=True ustun cheklovlari nima uchun kerak?",
               "nullable=False — ustun NULL (bo'sh) bo'lishi mumkin emas; yozuv yaratilganda u "
               "qiymatga ega bo'lishi shart. unique=True — bu ustunning qiymati bazada "
               "takrorlanmasligi kerak; takror urinish IntegrityError xato beradi. Birgalikda ular "
               "ma'lumotlar yaxlitligini ta'minlaydi (masalan, email uchun nullable=False + "
               "unique=True har bir user'ning aniq, takrorlanmas email'i bo'lishini kafolatlaydi).",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 8, "title": "8-CRUD operatsiyalar",
        "text": L8_TEXT, "code": L8_CODE, "lang": "python",
        "video": "https://youtu.be/m_jzo2zE5LM",
        "exercises": [
            mc("CRUD harflari nimani anglatadi?",
               ["Create, Read, Update, Delete",
                "Code, Run, Update, Deploy",
                "Common, Routine, User, Data",
                "Connect, Read, Update, Detach"],
               "A", diff="Easy", pts=2),
            mc("get_or_404(id) nima qiladi?",
               ["404 sahifani ko'rsatadi",
                "Yozuv topilsa qaytaradi, topilmasa avtomatik 404 xato javobi beradi",
                "404 ta yozuv olib keladi",
                "Eski yozuvlarni o'chiradi"],
               "B", diff="Easy", pts=2),
            mc("Nega DELETE amalini POST orqali qilamiz, GET orqali emas?",
               ["Brauzer link preview yozuvlarni tasodifan o'chirib qo'ymasligi uchun",
                "Google bot o'chirish URL'lariga kirib yozuvlarni o'chirmasligi uchun",
                "HTTP standartiga ko'ra GET o'zgartiruvchi (mutating) amallar uchun mos emas",
                "DELETE faqat POST orqali ishlaydi"],
               "A,B,C", multi=True,
               hint="GET 'xavfsiz' (safe) deyiladi.",
               diff="Medium", pts=3),
            dd("Yozuvni yangilash (UPDATE) bosqichlarini tartiblang",
               ["note = Note.query.get_or_404(id)",
                "note.title = request.form['title']",
                "db.session.commit()",
                "return redirect(url_for('show_note', id=note.id))"],
               hint="add() chaqirilmaydi — yozuv allaqachon sessiyada.",
               diff="Medium", pts=3),
            ti("IntegrityError yuz berganda nima qilish kerak va nima uchun?",
               "db.session.rollback() chaqirish kerak — aks holda sessiya 'buzilgan' holatda qoladi "
               "va keyingi commit'lar ham xato beradi. Rollback'dan keyin foydalanuvchiga tushunarli "
               "xato xabari (masalan, 'Bu email allaqachon mavjud') ko'rsatish kerak.",
               diff="Hard", pts=4),
            mc("Note.query.order_by(Note.created_at.desc()).limit(10).all() nima qaytaradi?",
               ["Eng eski 10 ta yozuvni",
                "Eng yangi 10 ta yozuvni (sana bo'yicha kamayish tartibida)",
                "Tasodifiy 10 ta yozuvni",
                "Barcha yozuvlarni, lekin faqat 10 tasini ko'rsatish uchun"],
               "B", hint="desc() so'zining ma'nosini eslang — kamayuvchi tartib.",
               diff="Easy", pts=2),
            ti("db.session.commit() qachon va nima uchun chaqiriladi? Agar uni chaqirmasdan route tugab ketsa nima bo'ladi?",
               "commit() o'zgartirishlarni (add/update/delete) bazaga haqiqiy yozadi. Agar "
               "chaqirilmasa, sessiya yopilganda o'zgarishlar avtomatik rollback bo'ladi — ya'ni "
               "yo'qoladi. Bir nechta amalni birlashtirib bitta tranzaksiyada saqlash uchun har bir "
               "add'dan keyin emas, balki barcha o'zgarishlardan keyin bir marta commit qilish "
               "maqsadga muvofiq.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 9, "title": "R2-Shaxsiy yozuvlar (takrorlash)",
        "text": R2_TEXT, "code": R2_CODE, "lang": "python",
        "video": "",
        "exercises": [
            mc("User va Note modellari orasidagi munosabat qaysi?",
               ["One-to-one (bir foydalanuvchining bitta notasi)",
                "One-to-many (bir foydalanuvchining ko'p notalari)",
                "Many-to-many (bir notada ko'p foydalanuvchi)",
                "Hech qanday munosabat — ular mustaqil"],
               "B", hint="db.relationship('Note', backref='owner', lazy=True) nima anglatadi?",
               diff="Easy", pts=2),
            mc("Note.query.get_or_404(id) nima qiladi?",
               ["Notani topadi, agar yo'q bo'lsa None qaytaradi",
                "Notani topadi, agar yo'q bo'lsa avtomatik 404 xato chiqaradi",
                "Notani topadi va o'chiradi",
                "Notani topadi va 404 statusda qaytaradi"],
               "B", hint="Method nomi: get + or_404. 404 nima?",
               diff="Easy", pts=2),
            mc("Foydalanuvchi /notes/5/edit ga kirdi. Note id=5 boshqa foydalanuvchiniki. Eng to'g'ri xatti-harakat?",
               ["Notani tahrirlashga ruxsat berish",
                "404 qaytarish (bizning foydalanuvchi uchun u 'mavjud emas')",
                "abort(403) — Ruxsat yo'q",
                "Notani avtomatik o'chirib tashlash"],
               "C", hint="403 Forbidden — autentifikatsiya qilingan lekin ruxsat yo'q.",
               diff="Medium", pts=3),
            mc("Quyidagi qaysi kod TO'G'RI yangi notani saqlaydi?",
               ["note = Note(title='X', body='Y'); db.session.commit()",
                "note = Note(title='X', body='Y'); db.session.add(note); db.session.commit()",
                "Note.insert(title='X', body='Y')",
                "db.add(Note(title='X', body='Y')); db.save()"],
               "B", hint="Yangi yozuv: add() + commit() — ikkalasi ham kerak.",
               diff="Easy", pts=2),
            mc("created_at uchun qaysi kod TO'G'RI?",
               ["db.Column(db.DateTime, default=datetime.utcnow)",
                "db.Column(db.DateTime, default=datetime.utcnow())",
                "db.Column(db.DateTime, server_default=db.func.now())",
                "db.Column(db.DateTime, default=lambda: datetime.utcnow())"],
               "A,C,D", multi=True,
               hint="Qaysi variantda datetime.utcnow() FUNKSIYA emas, NATIJASI uzatiladi? Bu qaysi muammoga olib keladi?",
               diff="Medium", pts=3),
            dd("Foydalanuvchi 'Shaxsiy yozuvlar'da yangi nota yaratish jarayoni bosqichlarini tartiblang",
               ["Foydalanuvchi /login ga kiradi va ismni yuboradi",
                "Server User.query.filter_by(username=...).first() bilan tekshiradi",
                "Foydalanuvchi yo'q bo'lsa — yangi User yaratiladi va commit qilinadi",
                "session['user_id'] = user.id o'rnatiladi",
                "Foydalanuvchi /notes/new ga o'tadi va formani to'ldiradi",
                "Server Note(title, body, user_id=session['user_id']) yaratadi",
                "db.session.add(note) va db.session.commit() chaqiriladi",
                "/notes ga redirect qilinadi (PRG pattern)"],
               diff="Medium", pts=3),
            ti("Nima uchun cascade='all, delete-orphan' User.notes relationship'ida muhim?",
               "Bu opsiya bo'lmasa, foydalanuvchini o'chirishga uringanimizda SQLAlchemy xato chiqaradi — chunki foydalanuvchining "
               "notalari Note.user_id = user.id ga bog'langan (foreign key constraint). cascade='all, delete-orphan' shuni anglatadi: "
               "foydalanuvchi o'chirilsa, uning barcha notalari ham avtomatik o'chiriladi (cascade). 'delete-orphan' qismi esa shuni "
               "anglatadi: agar notani user.notes ro'yxatidan olib tashlasak (lekin Note obyekti hali jonli), uning 'egasi' qolmagan — "
               "demak u 'orphan' (yetim) va u ham o'chiriladi. Bu — modellaringizning ma'lumot butunligini saqlaydi.",
               diff="Hard", pts=4),
            ti("Foydalanuvchi /notes/5/delete ga GET so'rov yubordi. Bizning kodimiz POST kutmoqda. Bu qanday xavfdan saqlaydi?",
               "GET so'rovlar HAVOLALAR orqali tasodifan ishga tushishi mumkin — masalan, brauzer sahifani prefetch qiladi, "
               "yoki Slack/Telegram-da bot link'ni preview qilish uchun ochadi, yoki Google bot indekslayotganda. Agar /notes/5/delete "
               "GET ga ishlasa, kimdir sizga zararli HTML jo'natsa (masalan, <img src='https://app.com/notes/5/delete'>), brauzeringiz "
               "avtomatik so'rov yuboradi va siz xabaringiz o'chib ketadi. POST esa odatda forma orqali boshlanadi va CSRF himoyasi bilan "
               "to'liq xavfsiz qilish mumkin. Asosiy qoida: o'zgartirish bajaradigan amallar (delete, update, create) GET orqali bo'lmasin.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 10, "title": "9-Blueprint va app factory",
        "text": L9_TEXT, "code": L9_CODE, "lang": "python",
        "video": "https://youtu.be/WteIH6J9v64",
        "exercises": [
            mc("app factory pattern nimani anglatadi?",
               ["Ilovani global o'zgaruvchi emas, funksiyadan qaytariladigan obyekt sifatida yaratish",
                "Loyihada ko'p modul ishlatish",
                "Production'da gunicorn ishlatish",
                "HTML shablonlarni avtomatik yaratish"],
               "A", diff="Easy", pts=2),
            mc("Blueprint nima uchun foydali?",
               ["Faqat HTML dizayn uchun",
                "Bir guruh route va template'larni alohida modulga ajratish — kod tartibga solinishi uchun",
                "Bazaga ulanish uchun",
                "AI integratsiyasi uchun"],
               "B", diff="Easy", pts=2),
            mc("create_app() factory'ning afzalliklari qaysilar?",
               ["Testlar uchun har xil konfiguratsiya bilan yangi ilova yaratish oson",
                "Circular import muammolari kamayadi",
                "Bir nechta deploy konfiguratsiyasi (dev, test, prod) bo'lishi mumkin",
                "Avtomatik HTTPS yoqadi"],
               "A,B,C", multi=True, diff="Medium", pts=3),
            dd("Yangi Blueprint qo'shish bosqichlarini tartiblang",
               ["auth/__init__.py: auth_bp = Blueprint('auth', __name__)",
                "auth/routes.py: @auth_bp.route('/login') def login(): ...",
                "app/__init__.py: from app.auth import auth_bp",
                "app.register_blueprint(auth_bp, url_prefix='/auth')",
                "Endi /auth/login URL ishlaydi"],
               diff="Medium", pts=3),
            ti("url_for da blueprint endpointiga qanday murojaat qilamiz va nima uchun?",
               "url_for('auth.login') — blueprint nomi va endpoint nomi nuqta bilan ajratiladi. "
               "Bir nechta blueprint'da bir xil nomli funksiya (masalan, 'home') bo'lishi mumkin; "
               "prefix bo'lmasa Flask qaysi birini chaqirayotganini ajrata olmaydi.",
               diff="Hard", pts=4),
            mc("Blueprint('auth', __name__, template_folder='templates') chaqirig'ida "
               "template_folder parametri nima uchun kerak?",
               ["Statik fayllar joyini belgilaydi",
                "Bu blueprint o'zining template'larini qaysi papkadan qidirishini bildiradi",
                "Eski template'larni avtomatik o'chiradi",
                "Faqat dekorativ — hech qanday ta'sir qilmaydi"],
               "B", hint="Har bir blueprint o'z template'larini mustaqil saqlashi mumkin.",
               diff="Easy", pts=2),
            ti("app.register_blueprint(auth_bp, url_prefix='/auth') chaqirig'ida url_prefix "
               "qanday ta'sir qiladi? Misol bilan tushuntiring.",
               "url_prefix blueprint'dagi har bir route'ning oldiga belgilangan yo'lni qo'shadi. "
               "Misol: agar blueprint ichida @auth_bp.route('/login') deb yozilgan bo'lsa, "
               "register_blueprint chaqirilgandan keyin haqiqiy URL /auth/login bo'ladi, nafaqat "
               "/login. Bu blueprint'ni o'z 'namespace'iga ajratish va URL'lar to'qnashuvi oldini "
               "olish uchun foydali.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 11, "title": "10-JSON API",
        "text": L10_TEXT, "code": L10_CODE, "lang": "python",
        "video": "https://youtu.be/PTZiDnuC86g",
        "exercises": [
            mc("jsonify oddiy return dan nima bilan farq qiladi?",
               ["Faqat string qabul qiladi",
                "Python dict/list ni JSON ga aylantiradi va Content-Type: application/json qo'yadi",
                "Tezroq ishlaydi",
                "Faqat GET so'rovlar uchun ishlaydi"],
               "B", diff="Easy", pts=2),
            mc("201 status kodi qachon qaytariladi?",
               ["Sahifa topilmadi",
                "Server xatosi",
                "POST orqali yangi resurs muvaffaqiyatli yaratildi",
                "Avtorizatsiya kerak"],
               "C", diff="Easy", pts=2),
            mc("REST konventsiyaga ko'ra qaysilari to'g'ri yozilgan endpointlar?",
               ["GET /api/users — barcha foydalanuvchilarni olish",
                "POST /api/users — yangi foydalanuvchi yaratish",
                "DELETE /api/users/42 — foydalanuvchini o'chirish",
                "GET /api/users/delete/42 — foydalanuvchini o'chirish"],
               "A,B,C", multi=True,
               hint="REST'da amal HTTP method'da bo'ladi, URL'da emas.",
               diff="Medium", pts=3),
            dd("Bitta resurs (notes) uchun REST endpointlarni tartiblang (Create→Delete)",
               ["POST   /api/notes          — Create",
                "GET    /api/notes          — Read (list)",
                "GET    /api/notes/<id>     — Read (one)",
                "PUT    /api/notes/<id>     — Update",
                "DELETE /api/notes/<id>     — Delete"],
               diff="Medium", pts=3),
            ti("CORS nima va qachon kerak bo'ladi?",
               "CORS (Cross-Origin Resource Sharing) — brauzer xavfsizlik mexanizmi. Frontend "
               "(masalan, React localhost:3000) backend (Flask localhost:5000) ga so'rov yuborganda, "
               "bu turli origin (port farqi ham origin farqi). Brauzer bunday so'rovlarni avtomatik "
               "bloklaydi; CORS sozlash orqali backend ruxsat berilgan domainlarni e'lon qiladi.",
               diff="Hard", pts=4),
            mc("PUT va PATCH orasidagi farq nima?",
               ["PUT yangi yaratadi, PATCH yangilaydi",
                "PUT butun resursni almashtiradi (to'liq yangilash), "
                "PATCH faqat berilgan maydonlarni o'zgartiradi",
                "PUT GET ning aksi, PATCH POST ning aksi",
                "Hech qanday farq yo'q — ikkalasi ham bir xil"],
               "B", hint="Bittasi 'to'liq almashtirish', ikkinchisi 'qisman yangilash'.",
               diff="Easy", pts=2),
            ti("@app.errorhandler(404) JSON API uchun nima uchun ayniqsa muhim?",
               "JSON API klienti (React, mobil ilova) HTML xato sahifasini ko'rmaydi — u JSON "
               "kutadi. Agar errorhandler(404) belgilanmasa, Flask odatda HTML 404 sahifasini "
               "qaytaradi va klient JSON.parse() qila olmay xato beradi. Custom 404 handler "
               "{'error': 'Topilmadi'} ko'rinishidagi JSON qaytaradi, shunda klient xatoni to'g'ri "
               "boshqarib foydalanuvchiga tushunarli xabar ko'rsata oladi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 12, "title": "R3-Notes REST API (takrorlash)",
        "text": R3_TEXT, "code": R3_CODE, "lang": "python",
        "video": "",
        "exercises": [
            mc("POST /api/notes muvaffaqiyatli yangi nota yaratdi. Qaysi status kod TO'G'RI?",
               ["200 OK",
                "201 Created",
                "204 No Content",
                "302 Found"],
               "B", hint="POST + yangi resurs yaratildi — qaysi 2xx kod maxsus shu uchun?",
               diff="Easy", pts=2),
            mc("DELETE /api/notes/5 muvaffaqiyatli o'chirdi. Eng to'g'ri javob qaysi?",
               ["200 OK, {'deleted': true}",
                "201 Created, {}",
                "204 No Content, javob tanasi bo'sh",
                "404 Not Found"],
               "C", hint="DELETE muvaffaqiyatli bo'lganda nima qaytariladi? 'No Content' nimani anglatadi?",
               diff="Easy", pts=2),
            mc("request.get_json(silent=True) ning request.get_json() ga nisbatan afzalligi nima?",
               ["Tezroq ishlaydi",
                "Mijoz noto'g'ri JSON yuborgan bo'lsa, xato chiqarmasdan None qaytaradi",
                "Faqat Python 3.11+ da ishlaydi",
                "Hech qanday farq yo'q"],
               "B", hint="silent=True nomidan ham — 'jim'.",
               diff="Easy", pts=2),
            mc("Auth Blueprint'ni '/api/auth' prefiks bilan ulash uchun qaysi to'g'ri?",
               ["app.register_blueprint(auth_bp, url_prefix='/api/auth')",
                "auth_bp.url_prefix = '/api/auth'",
                "app.add_blueprint(auth_bp, '/api/auth')",
                "auth_bp.register(app, '/api/auth')"],
               "A", hint="register_blueprint ning argumentlari nima?",
               diff="Easy", pts=2),
            mc("REST API'da xato javoblar uchun qaysi yondashuvlar TO'G'RI?",
               ["HTML xato sahifasi qaytarish",
                "{'error': 'Topilmadi'} ko'rinishidagi JSON qaytarish",
                "To'g'ri HTTP status kod (404, 400, 403) qo'shish",
                "Faqat 200 OK qaytarib, javob tanasida xato matni"],
               "B,C", multi=True,
               hint="API mijozi HTML'ni parse qila olmaydi. Va 200 status — 'hammasi yaxshi' degan ma'noni anglatadi.",
               diff="Medium", pts=3),
            dd("REST API orqali yangi nota yaratish jarayonini tartiblang",
               ["Mijoz POST /api/auth/login ga {username: 'X'} yuboradi",
                "Server User'ni topadi yoki yaratadi va session['user_id'] o'rnatadi",
                "Mijoz POST /api/notes ga {title, body} yuboradi (cookie bilan)",
                "Server session['user_id'] borligini tekshiradi (401 agar yo'q)",
                "Server JSON validatsiya qiladi (400 agar title/body yo'q)",
                "Server Note yaratadi va db.session.commit() chaqiradi",
                "Server 201 status va yangi note JSON qaytaradi"],
               diff="Medium", pts=3),
            ti("Nima uchun Note modelida to_dict() metodi yozish JSON API uchun yaxshi pattern?",
               "to_dict() — model obyektini JSON'ga aylantirish mantiqini bitta joyda saqlaydi. Agar har endpoint'da qo'lda "
               "{'id': n.id, 'title': n.title, ...} yozsangiz: (1) takrorlash ko'p — DRY printsipiga zid; (2) yangi maydon qo'shilsa, "
               "har endpoint'da yangilash kerak — eslab qolmasangiz, ba'zi endpointlardan u tushib qoladi; (3) sezgir ma'lumotlar "
               "(masalan, password_hash) tasodifan ochilib qolishi mumkin. to_dict() metodida esa — model qaysi maydonlarini API "
               "ochishini aniq belgilaysiz. Yana yaxshi tomoni: kelajakda Marshmallow yoki Pydantic kabi serializer'larga osongina o'tasiz.",
               diff="Hard", pts=4),
            ti("CRUD operatsiyalari uchun qaysi HTTP method qaysi vazifaga to'g'ri keladi va nima uchun?",
               "GET — Read (o'qish): xavfsiz va idempotent (bir xil natija). URL'da parametr orqali, body yo'q. Misol: GET /api/notes/5. "
               "POST — Create (yaratish): yangi resurs yaratiladi, server unga id beradi. Idempotent emas — har bir POST yangi entry yaratadi. "
               "Misol: POST /api/notes + JSON body. PUT — Update (to'liq yangilash): mavjud resursni yangi ma'lumot bilan to'liq almashtirish. "
               "Idempotent — bir xil PUT necha marta yuborilsa ham natija bir xil. PATCH — Update (qisman yangilash): faqat o'zgargan maydonlar. "
               "DELETE — Delete (o'chirish): resursni o'chiradi. Idempotent — ikkinchi DELETE 404 qaytaradi (oldingisi allaqachon ishlab bo'lgan). "
               "RESTful API'ning go'zalligi shunda — har URL bitta resursni anglatadi va method nima qilishingizni belgilaydi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 13, "title": "11-Deployga tayyorlash",
        "text": L11_TEXT, "code": L11_CODE, "lang": "python",
        "video": "https://youtu.be/goToXTC96Co",
        "exercises": [
            mc("python-dotenv nima uchun kerak?",
               ["Python'ni avtomatik o'rnatadi",
                ".env faylidan environment o'zgaruvchilarini os.environ ga yuklab oladi",
                "Faqat Linux serverlarda ishlaydi",
                "Faqat Django uchun"],
               "B", diff="Easy", pts=2),
            mc("Nima uchun gunicorn ishlatamiz, app.run() yetmaydimi?",
               ["gunicorn tezroq ishga tushadi",
                "app.run() faqat development uchun: bir vaqtda bitta so'rovni boshqaradi va xavfsizligi cheklangan",
                "gunicorn bepul, app.run() pulli",
                "gunicorn HTML chiqaradi"],
               "B", diff="Easy", pts=2),
            mc("Production checklist'idan qaysi bandlar SHART?",
               ["debug=False bo'lishi shart",
                "SECRET_KEY environment variable orqali kelishi kerak",
                ".env fayl gitignore'da bo'lishi shart",
                "Hech qanday log yozmaslik kerak"],
               "A,B,C", multi=True,
               hint="Loglar production'da albatta kerak — qaysi band noto'g'ri?",
               diff="Medium", pts=3),
            dd("Yangi versiyani production'ga deploy qilish bosqichlarini tartiblang",
               ["Kodni Git'ga commit qilish va push",
                "Serverga ssh orqali ulanish",
                "git pull va pip install -r requirements.txt",
                "Yangi environment o'zgaruvchilarini .env ga yozish (kerak bo'lsa)",
                "gunicorn / systemd service'ni qayta ishga tushirish",
                "Brauzerda yoki curl bilan tekshirish"],
               diff="Medium", pts=3),
            ti("ProxyFix nima uchun ishlatiladi?",
               "Nginx orqali so'rov kelganda, Flask uchun request.remote_addr har doim 127.0.0.1 "
               "(nginx) bo'lib ko'rinadi — haqiqiy mijoz IP'si emas. ProxyFix Flask'ga nginx "
               "tomonidan qo'shilgan X-Forwarded-For va X-Forwarded-Proto header'larini o'qishni "
               "o'rgatadi, shunda haqiqiy mijoz IP va HTTP/HTTPS sxema to'g'ri aniqlanadi.",
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
    """Mirror the HTML CSS course shape: text → code → video → exercise.

    Embedded exercise mirror copies every field the frontend reads from the
    inline section (options, drag_items, etc.) so renderer doesn't have to
    fetch them separately.
    """
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
        # 1) Course — skip if exists
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

        # 2) Lessons + exercises
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
                sections_json=None,            # filled in after exercise ids exist
                task_title=task.get("title"),
                task_description=task.get("description"),
                task_requirements=task.get("requirements"),
                task_technologies=task.get("technologies"),
                task_deadline_days=task.get("deadline_days"),
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()  # need lesson.id for exercises

            # Insert exercises. Field rules (verified against
            # exercise_service.check_answer_locally):
            #   multiple_choice → correct_answers="B" or "A,C" (letters)
            #   drag_and_drop   → correct_order = JSON list of strings IN ORDER
            #   text_input      → expected_answer = model answer (AI-graded)
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
            await db.flush()  # need exercise ids for sections_json

            # Now build sections_json with real exercise ids embedded
            lesson.sections_json = build_sections_json(ldata, ex_rows)
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<32}  exercises={len(ex_rows)}")

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
