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
<p>Sukut bo'yicha route faqat GET so'rovlarini qabul qiladi. Boshqa methodlarni ruxsat berish uchun:</p>
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
<p>Hozirgacha biz HTML'ni Python qator ichida yozdik — bu shoxni juda tez qiyinlashtiradi. To'g'ri yo'l: HTML'ni alohida faylga ajratish va Python'dan unga ma'lumot yuborish. Buni <strong>shablon (template)</strong> deyiladi.</p>
<h3>templates/ papkasi</h3>
<p>Flask sukut bo'yicha shablonlarni <code>templates/</code> papkasidan qidiradi:</p>
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
               "Sukut bo'yicha @app.route faqat GET so'rovlarini qabul qiladi. Forma yuborish (POST), "
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
        "order": 6, "title": "7-Database (SQLAlchemy)",
        "text": L7_TEXT, "code": L7_CODE, "lang": "python",
        "video": "https://youtu.be/cYWiDiIUxQc",
        "exercises": [
            mc("ORM nima?",
               ["Yangi Python kutubxonasi nomi",
                "Bazaga yozuvlarni Python obyektlari sifatida ishlatish imkonini beruvchi tizim",
                "SQL serverlarining yangi standarti",
                "Faqat MySQL uchun ishlaydi"],
               "B", diff="Easy", pts=2),
            mc("primary_key=True nima vazifa bajaradi?",
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
            ti("nullable=False va unique=True ustun cheklovlari nima vazifa bajaradi?",
               "nullable=False — ustun NULL (bo'sh) bo'lishi mumkin emas; yozuv yaratilganda u "
               "qiymatga ega bo'lishi shart. unique=True — bu ustunning qiymati bazada "
               "takrorlanmasligi kerak; takror urinish IntegrityError xato beradi. Birgalikda ular "
               "ma'lumotlar yaxlitligini ta'minlaydi (masalan, email uchun nullable=False + "
               "unique=True har bir user'ning aniq, takrorlanmas email'i bo'lishini kafolatlaydi).",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 7, "title": "8-CRUD operatsiyalar",
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
               hint="GET 'xavfsiz' (safe) deb hisoblanadi.",
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
        "order": 8, "title": "9-Blueprint va app factory",
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
               "template_folder parametri nima vazifa bajaradi?",
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
        "order": 9, "title": "10-JSON API",
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
               "kutadi. Agar errorhandler(404) belgilanmasa, Flask sukut bo'yicha HTML 404 sahifasini "
               "qaytaradi va klient JSON.parse() qila olmay xato beradi. Custom 404 handler "
               "{'error': 'Topilmadi'} ko'rinishidagi JSON qaytaradi, shunda klient xatoni to'g'ri "
               "boshqarib foydalanuvchiga tushunarli xabar ko'rsata oladi.",
               diff="Hard", pts=4),
        ],
    },
    {
        "order": 10, "title": "11-Deployga tayyorlash",
        "text": L11_TEXT, "code": L11_CODE, "lang": "python",
        "video": "https://youtu.be/goToXTC96Co",
        "exercises": [
            mc("python-dotenv nima vazifa bajaradi?",
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
