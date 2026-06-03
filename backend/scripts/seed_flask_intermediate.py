"""Seed the "Python Flask — O'rta daraja" (Intermediate) course.

Prerequisite: students should have finished the basics course
("Python Flask"). This course assumes they already know routes,
templates, basic forms, sessions and raw sqlite3 — and replaces those
hacks with the real libraries (Flask-SQLAlchemy, Flask-Migrate,
Flask-Login, Flask-WTF, Flask-Mail) plus proper structure
(Application Factory, Blueprints).

Usage:
    cd backend
    python scripts/seed_flask_intermediate.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already
exists. To re-seed, delete the existing row manually first.

Language convention (matches basics):
    Uzbek body, Russian section labels (Текст / Код / Видео / Упражнения).
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
    "title": "Python Flask — O'rta daraja",
    "description": (
        "Asoslarni o'rgangan o'quvchilar uchun Flask'ning haqiqiy kutubxonalari: "
        "Application Factory, Blueprint, Flask-SQLAlchemy, Flask-Migrate, "
        "Flask-Login, Flask-WTF, fayl yuklash, REST API va Flask-Mail. "
        "Har modul oxirida takrorlash darsi va mini-loyiha."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 8,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ─────────────────────────────────────────────────────────────────────────────
# Lesson content
# Section convention (matches basics):
#   order 0: text     label=Текст        html
#   order 1: code     label=Код          code + lang
#   order 2: video    label=Видео        videoUrl
#   order 3: exercise label=Упражнения   exercises (mirror of DB rows)
# ─────────────────────────────────────────────────────────────────────────────

# ╔═══════════════════════════════════════════════════════════════════════════
# ║ MODULE 1 — Real project structure
# ╚═══════════════════════════════════════════════════════════════════════════

L1_TEXT = """\
<h2>Application Factory pattern</h2>

<pre class="mermaid">
flowchart LR
    A["wsgi.py"] -->|prod| B["create_app"]
    T["tests.py"] -->|test| B
    D["shell"] -->|dev| B
    B --> C["Flask init"]
    C --> E["config.from_object"]
    E --> F["db.init_app + login.init_app"]
    F --> G["register_blueprint"]
    G --> H(("return app"))
</pre>

<p>Asoslar kursida biz ilovamizni bir qator bilan yaratardik:</p>
<pre><code>app = Flask(__name__)</code></pre>
<p>Bu kichik loyihalarda yaxshi, lekin ilova kattalashganda muammolar boshlanadi: testlarda ikkita alohida ilova kerak bo'ladi, ishlab chiqarish va dev sozlamalari aralashib ketadi, kengaytmalar (SQLAlchemy, Login va boshqalar) global obyektlar bilan bog'lanib qoladi.</p>
<p>Yechim — <strong>Application Factory pattern</strong>. Global <code>app</code> obyektini yaratish o'rniga, biz <code>create_app()</code> nomli funksiya yozamiz va u har chaqirilganda yangi Flask ilovasini qaytaradi.</p>

<h3>Nima uchun bu yaxshi?</h3>
<ul>
<li><strong>Testlar</strong>: har test o'z toza ilovasini oladi — testlar bir-biriga ta'sir qilmaydi.</li>
<li><strong>Ko'p konfiguratsiya</strong>: bitta kod bazasi development, testing va production uchun turli sozlamalar bilan ishlay oladi.</li>
<li><strong>Aylanma import yo'q</strong>: kengaytmalar (db, login_manager) modul darajasida yaratiladi, lekin <code>init_app()</code> orqali keyinroq ilovaga bog'lanadi.</li>
</ul>

<h3>Konfiguratsiya klasslari</h3>
<p>Sozlamalarni alohida <code>config.py</code> fayliga ajratamiz va environment'ga qarab birini tanlaymiz:</p>
<pre><code>class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False</code></pre>
<p>Endi <code>create_app('development')</code> chaqirsak — dev sozlamali ilova, <code>create_app('production')</code> chaqirsak — prod sozlamali ilova oladi.</p>

<h3>Kengaytmalarni qanday bog'lash kerak</h3>
<p>Kengaytmani modul darajasida yaratamiz (ilovaga bog'lamasdan), so'ng <code>create_app</code> ichida <code>init_app(app)</code> chaqiramiz:</p>
<pre><code>from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ilovasiz yaratildi

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)  # endi bog'lanadi
    return app</code></pre>
<p>Bu <strong>juda muhim</strong>: <code>db = SQLAlchemy(app)</code> deb yozsangiz, factory pattern buziladi va testlar ishlamay qoladi.</p>

<pre class="mermaid">
flowchart TB
    subgraph BAD["NOTOGRI - bitta ilovaga mahkamlangan"]
        B1["db = SQLAlchemy with app"] --> B2["Test boshqa app yarata olmaydi"]
        B2 --> B3["Aylanma import xatosi"]
    end
    subgraph GOOD["TOGRI - kechiktirilgan boglanish"]
        G1["db = SQLAlchemy modul darajasida"] --> G2["create_app cfg"]
        G2 --> G3["db.init_app app"]
        G3 --> G4["Har test oz app va db ga ega"]
    end
</pre>

<h3>Eng kichik factory ilovasi</h3>
<p>Quyidagi kodda <code>create_app()</code> chaqirilganda — yangi Flask ilovasi, sozlamasi va bir nechta route bilan qaytadi:</p>
<pre><code>def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    @app.route('/')
    def home():
        return f"Salom! DEBUG={app.config['DEBUG']}"

    return app</code></pre>
<p>Ishga tushirish uchun <code>wsgi.py</code> nomli fayl yaratamiz:</p>
<pre><code>from app import create_app
app = create_app('development')

if __name__ == '__main__':
    app.run()</code></pre>
"""

L1_CODE = """\
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False

CONFIGS = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
}


# app/__init__.py
from flask import Flask
from config import CONFIGS

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    @app.route('/')
    def home():
        return f"Salom! DEBUG={app.config['DEBUG']}"

    return app


# wsgi.py
from app import create_app
app = create_app('development')

if __name__ == '__main__':
    app.run()
"""


L2_TEXT = """\
<h2>Blueprint — ilovani modullarga ajratish</h2>
<p>Asoslar kursida barcha route'lar <code>app.py</code> ichida edi. 5–10 route bilan bu yaxshi, lekin 30+ route bo'lganda fayl o'qib bo'lmas holga keladi. Yechim — <strong>Blueprint</strong>.</p>
<p>Blueprint — bu route'lar va shablonlarni guruhlab, keyinroq <code>create_app</code> ichida ilovaga ulanadigan modul. Har bir Blueprint o'z papkasida yashaydi va o'z prefiksi bilan ishlaydi.</p>

<h3>Tipik tuzilish</h3>
<pre><code>myapp/
├── app/
│   ├── __init__.py          # create_app() shu yerda
│   ├── main/
│   │   ├── __init__.py      # main_bp = Blueprint('main', __name__)
│   │   └── routes.py        # @main_bp.route('/')
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── notes/
│       ├── __init__.py
│       └── routes.py
├── config.py
└── wsgi.py</code></pre>

<h3>Blueprint yaratish</h3>
<pre><code># app/notes/__init__.py
from flask import Blueprint
notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

from . import routes  # routes faylida @notes_bp.route(...) ishlatiladi</code></pre>
<p>Diqqat: <code>from . import routes</code> qatori <code>notes_bp</code>'dan keyin keladi — aylanma import oldini olish uchun.</p>

<h3>Route yozish</h3>
<pre><code># app/notes/routes.py
from . import notes_bp

@notes_bp.route('/')
def list_notes():
    return "Notlar ro'yxati"

@notes_bp.route('/&lt;int:id&gt;')
def show_note(id):
    return f"Nota {id}"</code></pre>
<p>Endi <code>/notes/</code> URL <code>list_notes</code>'ga, <code>/notes/5</code> URL <code>show_note(5)</code>'ga boradi. <code>url_prefix='/notes'</code> avtomatik qo'shiladi — siz har route'ga qayta-qayta yozmaysiz.</p>

<h3>Blueprint'ni ilovaga ulash</h3>
<pre><code># app/__init__.py
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    from app.main import main_bp
    from app.notes import notes_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(notes_bp)
    return app</code></pre>

<h3>url_for Blueprint bilan</h3>
<p>Blueprint route'iga url yozish uchun <code>'blueprint_nomi.funksiya_nomi'</code> formatini ishlatamiz:</p>
<pre><code>{{ url_for('notes.list_notes') }}        # → /notes/
{{ url_for('notes.show_note', id=42) }}  # → /notes/42
{{ url_for('main.home') }}               # → /</code></pre>
<p>Eski <code>url_for('list_notes')</code> ishlamaydi — Blueprint nomini ham yozish kerak.</p>

<h3>Har Blueprint o'z shablonlari</h3>
<p>Blueprint o'z <code>templates/</code> papkasini ham olib yurishi mumkin:</p>
<pre><code>notes_bp = Blueprint('notes', __name__,
                     url_prefix='/notes',
                     template_folder='templates')</code></pre>
<p>Endi <code>render_template('notes/list.html')</code> avval <code>app/notes/templates/notes/list.html</code> qidiradi.</p>
"""

L2_CODE = """\
# app/__init__.py
from flask import Flask
from config import CONFIGS

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    from app.main import main_bp
    from app.notes import notes_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(notes_bp)
    return app


# app/main/__init__.py
from flask import Blueprint
main_bp = Blueprint('main', __name__)
from . import routes


# app/main/routes.py
from flask import render_template
from . import main_bp

@main_bp.route('/')
def home():
    return render_template('main/home.html')

@main_bp.route('/about')
def about():
    return "Biz haqimizda"


# app/notes/__init__.py
from flask import Blueprint
notes_bp = Blueprint('notes', __name__,
                     url_prefix='/notes',
                     template_folder='templates')
from . import routes


# app/notes/routes.py
from flask import render_template, url_for
from . import notes_bp

NOTES = [
    {'id': 1, 'title': 'Birinchi nota', 'body': 'Salom dunyo'},
    {'id': 2, 'title': 'Ikkinchi nota', 'body': 'Flask juda yoqdi'},
]

@notes_bp.route('/')
def list_notes():
    return render_template('notes/list.html', notes=NOTES)

@notes_bp.route('/<int:id>')
def show_note(id):
    note = next((n for n in NOTES if n['id'] == id), None)
    if not note:
        return "Topilmadi", 404
    return render_template('notes/show.html', note=note)
"""


# ╔═══════════════════════════════════════════════════════════════════════════
# ║ MODULE 2 — Database the right way
# ╚═══════════════════════════════════════════════════════════════════════════

L3_TEXT = """\
<h2>Flask-SQLAlchemy — ORM bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    A["Python kod"] -->|ORM| B["SQLAlchemy"]
    B -->|SQL generatsiya| C{"Qaysi baza?"}
    C -->|sqlite| D[("SQLite")]
    C -->|postgresql| E[("PostgreSQL")]
    C -->|mysql| F[("MySQL")]
    style A fill:#e8f5e9
    style B fill:#fff3e0
</pre>

<p>Asoslar kursida biz <code>sqlite3</code> moduli orqali SQL so'rovlarni qo'lda yozdik:</p>
<pre><code>cur.execute("INSERT INTO notes (title, body) VALUES (?, ?)",
            (title, body))</code></pre>
<p>Bu ishlaydi, lekin ko'p kamchiliklari bor: SQL string'larini qo'lda tuzasiz (xato qilish oson), har baza tipi uchun (SQLite/Postgres/MySQL) syntax farq qiladi, JOIN va relationship'lar bilan ishlash murakkab.</p>
<p><strong>ORM</strong> (Object-Relational Mapping) — bu SQL o'rniga Python obyektlari bilan ishlash imkonini beradigan qatlam. <strong>Flask-SQLAlchemy</strong> — Flask uchun eng mashhur ORM.</p>

<h3>O'rnatish va sozlash</h3>
<pre><code>pip install Flask-SQLAlchemy</code></pre>
<p>Application Factory ichida:</p>
<pre><code># app/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # modul darajasida, ilovasiz

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)
    return app</code></pre>
<p>Konfiguratsiyada <code>SQLALCHEMY_DATABASE_URI</code> bo'lishi shart:</p>
<pre><code>SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # ortiqcha ogohlantirishni o'chirish</code></pre>

<h3>Birinchi model</h3>
<p>Model — bu jadvalga mos keluvchi Python klass. <code>db.Model</code>'dan meros oladi.</p>
<pre><code># app/models.py
from datetime import datetime
from app import db

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           index=True)

    def __repr__(self):
        return f'&lt;Note {self.id}: {self.title!r}&gt;'</code></pre>
<p>Ustun turlari: <code>db.Integer</code>, <code>db.String(N)</code>, <code>db.Text</code>, <code>db.DateTime</code>, <code>db.Boolean</code>, <code>db.Float</code>.</p>

<h3>Jadvalni yaratish</h3>
<p>Birinchi marta ishga tushganda jadvalni yaratish kerak. Eng oson — Flask shell ichida:</p>
<pre><code>$ flask shell
&gt;&gt;&gt; from app import db
&gt;&gt;&gt; db.create_all()</code></pre>
<p>Yoki kodda (faqat development'da):</p>
<pre><code>with app.app_context():
    db.create_all()</code></pre>
<p><strong>Diqqat:</strong> <code>create_all()</code> faqat YANGI jadvallarni qo'shadi. Mavjud jadval sxemasini o'zgartirish uchun keyingi darsdagi <em>Flask-Migrate</em> kerak.</p>

<h3>Yozish va o'qish</h3>
<pre><code># Yozish
note = Note(title='Salom', body='Birinchi nota')
db.session.add(note)
db.session.commit()

# Barchasini o'qish
notes = Note.query.all()

# ID bo'yicha
note = Note.query.get(1)         # eski API
note = db.session.get(Note, 1)   # yangi SQLAlchemy 2.x API

# Yangilash — obyektni o'zgartirib commit qilish kifoya
note.title = 'Yangi sarlavha'
db.session.commit()

# O'chirish
db.session.delete(note)
db.session.commit()</code></pre>
<p><strong>Sessiyani unutmang!</strong> <code>db.session.add()</code> faqat o'zgarishni navbatga qo'yadi — <code>commit()</code> chaqirilmaguncha bazaga yozilmaydi.</p>

<h3>Xatolarni boshqarish</h3>
<p>Commit muvaffaqiyatsiz bo'lsa, sessiyani tozalash kerak — aks holda keyingi so'rovlar ham buzilgan holatda bo'ladi:</p>
<pre><code>try:
    db.session.add(note)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise</code></pre>

<pre class="mermaid">
sequenceDiagram
    participant V as View
    participant S as db.session
    participant DB as Baza
    V->>S: add note
    Note over S: navbatda hali yozilmagan
    V->>S: commit
    S->>DB: INSERT INTO notes
    alt Muvaffaqiyatli
        DB-->>S: OK
        S-->>V: True
    else Xato
        DB-->>S: IntegrityError
        S-->>V: Exception
        V->>S: rollback
        Note over S: sessiya toza endi
    end
</pre>
"""

L3_CODE = """\
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import CONFIGS

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)

    from app.notes.routes import notes_bp
    app.register_blueprint(notes_bp)
    return app


# app/models.py
from datetime import datetime
from app import db

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Note {self.id}: {self.title!r}>'


# app/notes/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Note

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')


@notes_bp.route('/')
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes/list.html', notes=notes)


@notes_bp.route('/new', methods=['POST'])
def create_note():
    note = Note(
        title=request.form['title'],
        body=request.form.get('body', ''),
    )
    try:
        db.session.add(note)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for('notes.list_notes'))


# bir martalik: jadvallarni yaratish
# $ flask shell
# >>> from app import db
# >>> db.create_all()
"""


L4_TEXT = """\
<h2>Modellar orasidagi munosabatlar (relationships)</h2>
<p>Hozircha bizning Note modeli yakka holatda. Real ilovada esa har note birovga tegishli — masalan, foydalanuvchiga. Bu munosabat <strong>one-to-many</strong> (bir foydalanuvchining ko'p notalari) deyiladi.</p>

<h3>Foreign Key — bog'lanish ustuni</h3>
<p>One-to-many uchun «ko'p» tomondagi jadvalga <code>ForeignKey</code> ustuni qo'shamiz:</p>
<pre><code>class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    # bu User'ning notlariga tezda kirishni beradi (notes.user_id orqali)
    notes = db.relationship(
        'Note', back_populates='user',
        cascade='all, delete-orphan',
    )


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, default='')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship('User', back_populates='notes')</code></pre>

<h3>back_populates vs backref</h3>
<p>Eski misollar <code>backref='notes'</code> ishlatadi — bu User klassiga avtomatik <code>notes</code> attributi qo'shadi. Yangi (SQLAlchemy 2.x) uslub esa <code>back_populates</code> — har ikkala tomonni qo'lda yozasiz, lekin kod aniq va o'qishga oson.</p>

<h3>cascade='all, delete-orphan' nima qiladi?</h3>
<p>User o'chirilganda uning barcha notalari ham avtomatik o'chiriladi. Bu yo'q bo'lsa, baza darajasida Foreign Key xatosi yuz beradi (yetim notalar qoladi).</p>

<h3>Bog'lanishdan foydalanish</h3>
<pre><code># Foydalanuvchining barcha notalari
user = User.query.get(1)
for note in user.notes:
    print(note.title)

# Notaning egasi
note = Note.query.get(5)
print(note.user.username)

# Yangi nota qo'shish — ikki usul
note = Note(title='Salom', body='...', user=user)  # ORM orqali
# yoki
note = Note(title='Salom', body='...', user_id=user.id)  # ID orqali</code></pre>

<h3>Many-to-many — yorliqlar (tags)</h3>
<p>Bir nota bir nechta yorliq olishi mumkin va bir yorliq ko'p notalarda ishlatilishi mumkin. Bu uchun oraliq jadval kerak:</p>
<pre><code>note_tags = db.Table(
    'note_tags',
    db.Column('note_id', db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id',  db.ForeignKey('tags.id'),  primary_key=True),
)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Note(db.Model):
    # ... (id, title, body, user_id)
    tags = db.relationship('Tag', secondary=note_tags, backref='notes')</code></pre>
<p>Oraliq jadval <code>db.Table</code> bilan yaratiladi (klass emas — chunki o'zining maydonlari yo'q). <code>secondary=note_tags</code> SQLAlchemy ga ikki tomonni qaerdan ulashni aytadi.</p>

<h3>Tag qo'shish va o'chirish</h3>
<pre><code>note = Note.query.get(1)
tag = Tag(name='muhim')
note.tags.append(tag)
db.session.commit()

# Olib tashlash
note.tags.remove(tag)
db.session.commit()</code></pre>
"""

L4_CODE = """\
# app/models.py
from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship(
        'Note', back_populates='user',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<User {self.username!r}>'


note_tags = db.Table(
    'note_tags',
    db.Column('note_id', db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id',  db.ForeignKey('tags.id'),  primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship('User', back_populates='notes')

    tags = db.relationship('Tag', secondary=note_tags, backref='notes')


# Misol — Flask shell ichida:
# >>> u = User(username='aziz')
# >>> n = Note(title='Salom', body='Birinchi nota', user=u)
# >>> t = Tag(name='muhim')
# >>> n.tags.append(t)
# >>> db.session.add_all([u, n, t])
# >>> db.session.commit()
# >>> u.notes
# [<Note 1: 'Salom'>]
# >>> n.tags
# [<Tag muhim>]
"""


L5_TEXT = """\
<h2>So'rovlar, filterlar va paginatsiya</h2>
<p>Endi modellarimiz bor — ulardan kerakli ma'lumotni qanday olamiz? Flask-SQLAlchemy bizga <code>Model.query</code> orqali kuchli so'rov tilini beradi.</p>

<h3>Asosiy so'rov metodlari</h3>
<pre><code># Barcha satrlar
Note.query.all()

# Birinchi mos kelgan
Note.query.first()

# ID bo'yicha (yo'q bo'lsa None)
Note.query.get(5)
db.session.get(Note, 5)   # SQLAlchemy 2.x uslubi

# 404 qaytarish — yo'q bo'lsa
Note.query.get_or_404(5)

# Sanab beradi
Note.query.count()</code></pre>

<h3>Filterlar</h3>
<pre><code># filter_by — sodda holatlar uchun (faqat tenglik)
Note.query.filter_by(user_id=1).all()

# filter — to'liq SQL-bo'sh ifoda
Note.query.filter(Note.created_at &gt; datetime(2025, 1, 1)).all()
Note.query.filter(Note.title.like('%Flask%')).all()
Note.query.filter(Note.title.ilike('%flask%')).all()  # case-insensitive

# Ko'p filterni birlashtirish
Note.query.filter(
    Note.user_id == 1,
    Note.title.ilike('%salom%')
).all()</code></pre>
<p><code>filter_by</code> bilan <code>filter</code>ning farqi: <code>filter_by(user_id=1)</code> faqat tenglik tekshiradi va keyword argument oladi. <code>filter(Note.user_id == 1)</code> — to'liq ifoda, har xil operatorlarni qo'llaydi.</p>

<h3>Tartiblash va chegaralash</h3>
<pre><code>Note.query.order_by(Note.created_at.desc()).all()
Note.query.order_by(Note.title.asc()).all()

# Faqat birinchi 10 ta
Note.query.order_by(Note.created_at.desc()).limit(10).all()

# 20 dan 30 gacha (skip+take)
Note.query.order_by(Note.id).offset(20).limit(10).all()</code></pre>

<h3>JOIN va munosabatlar bo'yicha so'rov</h3>
<pre><code># 'aziz' ismli foydalanuvchining barcha notalari
Note.query.join(User).filter(User.username == 'aziz').all()

# Bog'lanish orqali — N+1 muammosini oldini olish uchun joinedload
from sqlalchemy.orm import joinedload
notes = Note.query.options(joinedload(Note.user)).all()
# endi note.user.username chaqirsangiz — qo'shimcha so'rov bo'lmaydi</code></pre>
<p><strong>N+1 muammo:</strong> 100 ta nota olib, har birining <code>note.user.username</code> chaqirsangiz — bu 1 ta + 100 ta so'rov bo'ladi. <code>joinedload</code> esa hammasini bitta JOIN'ga birlashtiradi.</p>

<h3>Paginatsiya</h3>
<p>Flask-SQLAlchemy <code>paginate()</code> metodi bilan paginatsiya juda oson:</p>
<pre><code>@notes_bp.route('/')
def list_notes():
    page = request.args.get('page', 1, type=int)
    pagination = Note.query.order_by(Note.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False,
    )
    return render_template('notes/list.html', pagination=pagination)</code></pre>
<p>Shablonda:</p>
<pre><code>{% for note in pagination.items %}
  &lt;li&gt;{{ note.title }}&lt;/li&gt;
{% endfor %}

&lt;p&gt;Sahifa {{ pagination.page }} / {{ pagination.pages }}&lt;/p&gt;

{% if pagination.has_prev %}
  &lt;a href="{{ url_for('notes.list_notes', page=pagination.prev_num) }}"&gt;Oldingi&lt;/a&gt;
{% endif %}
{% if pagination.has_next %}
  &lt;a href="{{ url_for('notes.list_notes', page=pagination.next_num) }}"&gt;Keyingi&lt;/a&gt;
{% endif %}</code></pre>

<h3>OR mantiqi</h3>
<pre><code>from sqlalchemy import or_

Note.query.filter(
    or_(Note.title.ilike('%flask%'),
        Note.body.ilike('%flask%'))
).all()</code></pre>
"""

L5_CODE = """\
# app/notes/routes.py
from datetime import datetime
from flask import Blueprint, render_template, request, abort
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app import db
from app.models import Note, User, Tag

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')


@notes_bp.route('/')
def list_notes():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    query = Note.query.options(joinedload(Note.user))

    if q:
        query = query.filter(or_(
            Note.title.ilike(f'%{q}%'),
            Note.body.ilike(f'%{q}%'),
        ))

    pagination = query.order_by(Note.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False,
    )
    return render_template('notes/list.html',
                           pagination=pagination, q=q)


@notes_bp.route('/<int:id>')
def show_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    return render_template('notes/show.html', note=note)


@notes_bp.route('/recent')
def recent_notes():
    notes = (Note.query
             .order_by(Note.created_at.desc())
             .limit(5)
             .all())
    return render_template('notes/recent.html', notes=notes)


@notes_bp.route('/by-tag/<tag_name>')
def notes_by_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template('notes/by_tag.html',
                           tag=tag, notes=tag.notes)
"""


L6_TEXT = """\
<h2>Flask-Migrate — sxemani xavfsiz o'zgartirish</h2>
<p>Asoslar kursida biz <code>db.create_all()</code> chaqirardik — bu YANGI jadvallarni yaratadi, lekin mavjudlarini o'zgartirmaydi. Endi yangi ustun qo'shish kerak bo'lsa-chi? Yoki ustun nomini o'zgartirish? <code>create_all()</code> bunga ojiz.</p>
<p>Yechim — <strong>Migration</strong>. Bu sxemaning har bir o'zgarishi alohida «versiya» fayl sifatida saqlanadi va ketma-ket qo'llab boriladi. <strong>Flask-Migrate</strong> — bu Flask uchun Alembic kutubxonasi ustidan qulay qatlam.</p>

<h3>O'rnatish</h3>
<pre><code>pip install Flask-Migrate</code></pre>
<p>Application Factory ichida:</p>
<pre><code># app/__init__.py
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    # MUHIM: modellar import qilinishi kerak — aks holda Alembic ularni
    # ko'rmaydi va migration bo'sh chiqadi.
    from app import models  # noqa: F401
    return app</code></pre>

<h3>Birinchi marta sozlash</h3>
<pre><code>$ export FLASK_APP=wsgi.py
$ flask db init      # migrations/ papkasini yaratadi (faqat bir marta)
$ flask db migrate -m "initial tables"
$ flask db upgrade   # migration'ni bazaga qo'llaydi</code></pre>
<p>Endi <code>migrations/versions/</code> papkasida birinchi migration fayli paydo bo'ldi — uni git'ga commit qilasiz.</p>

<h3>Sxemani o'zgartirish</h3>
<p>Aytaylik, Note modeliga <code>is_pinned</code> ustun qo'shmoqchimiz:</p>
<pre><code>class Note(db.Model):
    # ... mavjud ustunlar ...
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)</code></pre>
<p>Yangi migration yaratamiz va qo'llaymiz:</p>
<pre><code>$ flask db migrate -m "add is_pinned to notes"
$ flask db upgrade</code></pre>
<p>Alembic modelni ko'radi, bazani ko'radi, farqni topadi va o'zi <code>ALTER TABLE</code> yozadi.</p>

<h3>Migration faylini ko'zdan kechirish</h3>
<p><strong>Avtomatik migration har doim ham to'g'ri bo'lmaydi.</strong> Ayniqsa: ustun nomini o'zgartirish (Alembic uni DROP + ADD deb tushunadi — siz ma'lumot yo'qotasiz), ENUM o'zgartirish, murakkab konstrayntlar.</p>
<p>Shuning uchun har <code>migrate</code>'dan keyin <code>migrations/versions/&lt;hash&gt;_*.py</code> faylini ochib o'qib chiqing, kerak bo'lsa <code>upgrade()</code> va <code>downgrade()</code> funksiyalarini qo'lda tahrirlang.</p>

<h3>Eng foydali komandalar</h3>
<pre><code>flask db current     # hozirgi migration versiyasi
flask db history     # barcha migration ketma-ketligi
flask db downgrade   # bir qadam orqaga
flask db downgrade -1  # bir migration orqaga
flask db stamp head  # bazani migration ostida deb belgilash (ma'lumot o'zgarmaydi)</code></pre>

<h3>Production qoidalari</h3>
<ul>
<li><strong>Migration fayllarini commit qiling</strong> — bu sizning sxema tarixingiz.</li>
<li><strong>Hech qachon mavjud migrationni tahrirlamang</strong> agar u allaqachon production'da qo'llanilgan bo'lsa. Yangi migration yarating.</li>
<li><strong>Deploy oldidan</strong> migrationni avval staging'da sinab ko'ring.</li>
<li><strong>Deploy paytida</strong> <code>flask db upgrade</code> avtomatik chaqirilsin (Procfile yoki release skript ichida).</li>
</ul>
"""

L6_CODE = """\
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import CONFIGS

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    # modellarni import qilish MUHIM:
    # aks holda Alembic ularni ko'rmaydi.
    from app import models  # noqa: F401

    from app.notes.routes import notes_bp
    app.register_blueprint(notes_bp)
    return app


# app/models.py — Note modeliga is_pinned qo'shildi
from datetime import datetime
from app import db


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, default='')
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# CLI ish-jarayoni:
#
#   $ export FLASK_APP=wsgi.py
#   $ flask db init                          # bir martalik
#   $ flask db migrate -m "initial tables"
#   $ flask db upgrade
#
#   # Keyinchalik modelni o'zgartirgach:
#   $ flask db migrate -m "add is_pinned to notes"
#   $ flask db upgrade
#
#   $ flask db current    # hozirgi versiya
#   $ flask db history    # barcha migration tarixi
#   $ flask db downgrade  # bir qadam orqaga (testlar yoki tikash uchun)
"""


R1_TEXT = """\
<h2>R1 — Modul 1 + 2 takrorlash</h2>
<p>Bu darsda yangi kontent yo'q — siz o'rganganlaringizni bitta loyihaga birlashtirib qo'yasiz.</p>

<h3>Nimani takrorlaymiz?</h3>
<ul>
<li><strong>L1 Application Factory</strong> — <code>create_app(config_name)</code>, Config klasslari, <code>wsgi.py</code></li>
<li><strong>L2 Blueprint</strong> — modul-modul tuzilish, <code>url_for('blueprint.func')</code></li>
<li><strong>L3 Flask-SQLAlchemy</strong> — modellar, <code>db.session</code>, CRUD</li>
<li><strong>L4 Relationships</strong> — <code>ForeignKey</code>, <code>relationship</code>, cascade</li>
<li><strong>L5 So'rovlar</strong> — filterlar, tartiblash, paginatsiya, JOIN</li>
<li><strong>L6 Flask-Migrate</strong> — sxemani xavfsiz o'zgartirish</li>
</ul>

<h3>Eslatma jadvali</h3>
<pre><code>┌──────────────────────┬─────────────────────────────────────────┐
│ Aniq holat           │ Qaysi vositadan foydalanasiz?           │
├──────────────────────┼─────────────────────────────────────────┤
│ Yangi ilova boshlash │ create_app() factory pattern            │
│ Route'larni guruhlash│ Blueprint(url_prefix=...)                │
│ Bazaga yozish        │ db.session.add(obj) + db.session.commit()│
│ ID bo'yicha o'qish   │ db.session.get(Model, id)                │
│ Filter + tartib      │ Model.query.filter(...).order_by(...)    │
│ Sahifalash           │ .paginate(page=N, per_page=10)           │
│ Bog'liq obyektlar    │ user.notes / note.user                   │
│ Sxemani o'zgartirish │ flask db migrate + flask db upgrade      │
└──────────────────────┴─────────────────────────────────────────┘</code></pre>

<h3>Loyiha — Yo'qolgan narsalar yorlig'i</h3>
<p>Quyidagi spetsifikatsiya bo'yicha to'liq ilovani quring. Modul 1 va 2 dagi barcha vositalarni qo'llang.</p>
<p>Foydalanuvchi yo'qotgan narsasi haqida e'lon joylaydi (kim, qaerda, nima): kategoriya bilan (telefon, hujjat, kalit va boshqalar). Boshqalar ko'rib, agar topgan bo'lsa — yorliq qo'ya oladi (Many-to-Many bilan).</p>

<h3>Tekshirish ro'yxati</h3>
<ul>
<li>create_app() factory + 3 ta config klass</li>
<li>Kamida 2 ta Blueprint: main_bp va items_bp</li>
<li>Modellar: User, Item, Tag + Many-to-Many (item_tags)</li>
<li>Migration bilan boshlangan (flask db init + 1 ta migration)</li>
<li>Bosh sahifa: paginatsiya bilan e'lonlar ro'yxati (10 ta sahifada)</li>
<li>Qidiruv: ?q=... query param orqali</li>
<li>Tag bo'yicha filtr: /tag/&lt;name&gt;</li>
<li>Yangi e'lon qo'shish formasi (hozircha autentifikatsiyasiz — uni 3-modulda qo'shamiz)</li>
</ul>

<h3>Tavsiya etilgan loyiha tuzilishi</h3>
<pre><code>lost_and_found/
├── config.py
├── wsgi.py
├── requirements.txt
├── migrations/
│   └── versions/
└── app/
    ├── __init__.py
    ├── models.py
    ├── main/
    │   ├── __init__.py
    │   └── routes.py
    ├── items/
    │   ├── __init__.py
    │   └── routes.py
    └── templates/
        ├── base.html
        ├── main/
        │   └── home.html
        └── items/
            ├── list.html
            ├── show.html
            └── new.html</code></pre>
"""

# ╔═══════════════════════════════════════════════════════════════════════════
# ║ MODULE 3 — Real authentication
# ╚═══════════════════════════════════════════════════════════════════════════

L7_TEXT = """\
<h2>Parolni xavfsiz saqlash</h2>
<p>Asoslar kursida biz parolni bevosita tekshirib oddiy login yasagandik:</p>
<pre><code>if username == 'admin' and password == '1234':
    session['user'] = username</code></pre>
<p>Bu mashq uchun yaramaydi — real ilovada parol bazaga saqlanadi, lekin <strong>hech qachon to'g'ridan-to'g'ri</strong> saqlanmaydi. Buning sababi: agar baza buzilsa yoki kimdir <code>SELECT * FROM users</code> qila olsa — barcha foydalanuvchilar paroli ochiq ko'rinadi.</p>

<h3>Hashing nima?</h3>
<p>Hash funksiyasi — bu kirish matnidan qaytmas (one-way) qisqartirilgan satr yaratuvchi algoritm. Bir xil kirish doim bir xil hash beradi, lekin hashdan kirishni qayta tiklab bo'lmaydi.</p>
<pre><code>hash("paroL123") = "$2b$12$KIXc8m..."  # mumkin
hash("$2b$12$KIXc8m...") = "paroL123"  # MUMKIN EMAS</code></pre>

<h3>Werkzeug — Flask bilan kelgan tayyor vosita</h3>
<p>Werkzeug — bu Flask'ning ostida turadigan kutubxona. Parol bilan ishlash uchun ikki tayyor funksiya beradi: <code>generate_password_hash</code> va <code>check_password_hash</code>.</p>
<pre><code>from werkzeug.security import generate_password_hash, check_password_hash

# Yozish (ro'yxatdan o'tish paytida)
hash = generate_password_hash('paroL123')
# Misol: 'pbkdf2:sha256:600000$abc...'

# Tekshirish (login paytida)
check_password_hash(hash, 'paroL123')   # True
check_password_hash(hash, 'yomon')      # False</code></pre>
<p>Werkzeug standart usulda <strong>pbkdf2-sha256 + 600000 iteratsiya + tasodifiy salt</strong> ishlatadi — bu hozircha kuchli. Agar yanada xavfsizlik kerak bo'lsa: <code>pip install bcrypt</code> va <code>generate_password_hash(p, method='bcrypt')</code>.</p>

<h3>Salt nima va nima uchun kerak?</h3>
<p>Salt — bu har parol uchun tasodifiy qo'shimcha. U hashga aralashtirib yuboriladi. Bu nima uchun muhim?</p>
<ul>
<li>Agar saltsiz hash ishlatsangiz, bir xil parolli ikki foydalanuvchining hashlari bir xil bo'ladi — hujumchi buni ko'ra oladi.</li>
<li>Salt har parol uchun unique — <code>hash('paroL123')</code> har safar boshqacha chiqadi.</li>
<li>Werkzeug saltni hashning o'zida saqlaydi (formatdagi <code>$abc...$</code> qismi) — qo'shimcha ustun kerak emas.</li>
</ul>

<h3>User modeliga password_hash qo'shamiz</h3>
<pre><code>class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)</code></pre>
<p>Diqqat: <code>password_hash</code> ustun <strong>255 belgi</strong> bo'lishi kerak — hash uzunligi katta.</p>

<h3>Ro'yxatdan o'tish flow</h3>
<pre><code>@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        # Validatsiya
        if not username or not email or len(password) < 8:
            flash('Barcha maydonlar to\\'ldirilsin, parol kamida 8 belgi')
            return redirect(url_for('auth.register'))

        # Mavjudligini tekshirish
        if User.query.filter_by(username=username).first():
            flash('Bu username band')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Ro\\'yxatdan o\\'tdingiz! Endi login qiling.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')</code></pre>
"""

L7_CODE = """\
# app/models.py
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


# app/auth/routes.py
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return render_template('auth/register.html')

    username = request.form['username'].strip()
    email    = request.form['email'].strip().lower()
    password = request.form['password']

    if not username or not email or len(password) < 8:
        flash("Barcha maydonlar, parol kamida 8 belgi")
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash('Bu username band')
        return redirect(url_for('auth.register'))
    if User.query.filter_by(email=email).first():
        flash('Bu email allaqachon ro\\'yxatdan o\\'tgan')
        return redirect(url_for('auth.register'))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('Tabriklaymiz! Endi login qiling.')
    return redirect(url_for('auth.login'))
"""


L8_TEXT = """\
<h2>Flask-Login — sessiya orqali autentifikatsiya</h2>
<p>Parolimiz bor, lekin login bo'lgan foydalanuvchini har sahifada qanday eslab qolamiz? Asoslar kursida biz <code>session['user_id']</code> ni qo'lda boshqargandik. <strong>Flask-Login</strong> esa buni avtomatlashtiradi va ko'p qulayliklar beradi: <code>current_user</code>, <code>@login_required</code>, «next» URL'iga avtomatik qaytish, va boshqalar.</p>

<h3>O'rnatish va sozlash</h3>
<pre><code>pip install Flask-Login</code></pre>
<pre><code># app/__init__.py
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'   # kim kirmagan bo'lsa qaerga
    login_manager.login_message = 'Avval login qiling'
    return app</code></pre>

<h3>User modelini Flask-Login bilan moslashtirish</h3>
<p>Flask-Login User modelidan 4 ta atribut/metod talab qiladi: <code>is_authenticated</code>, <code>is_active</code>, <code>is_anonymous</code>, <code>get_id()</code>. Ularning hammasini qo'lda yozish o'rniga <code>UserMixin</code>'dan meros olamiz:</p>
<pre><code>from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # ... (username, email, password_hash kabi)</code></pre>

<h3>user_loader callback</h3>
<p>Flask-Login sessiya'dan user_id ni o'qiydi va bizdan User obyektini bazadan olib berishni so'raydi. Buni <code>@login_manager.user_loader</code> bilan ko'rsatamiz:</p>
<pre><code># app/models.py oxiri
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))</code></pre>
<p>Bu callback har so'rovda chaqiriladi (sessiyada user_id bo'lsa) va <code>current_user</code> ga User obyektini joylaydi.</p>

<h3>Login va Logout route'lari</h3>
<pre><code>from flask_login import login_user, logout_user, login_required, current_user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Username yoki parol xato')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        # Avval kirmoqchi bo'lgan sahifaga qaytarish
        next_page = request.args.get('next') or url_for('main.home')
        return redirect(next_page)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))</code></pre>

<h3>@login_required dekoratori</h3>
<p>Bu dekorator — Flask-Login'ning eng foydali qismi. Login bo'lmaganlar avtomatik <code>login_view</code>'ga yuboriladi va ?next=... orqali kelgan sahifani eslab qoladi:</p>
<pre><code>@notes_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_note():
    note = Note(title=request.form['title'],
                user_id=current_user.id)
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('notes.list_notes'))</code></pre>

<h3>current_user — har joyda mavjud</h3>
<p>Login bo'lgan bo'lsa — User obyekt; bo'lmasa — AnonymousUserMixin (is_authenticated=False bilan).</p>
<pre><code>{% if current_user.is_authenticated %}
  &lt;p&gt;Salom, {{ current_user.username }}!&lt;/p&gt;
  &lt;a href="{{ url_for('auth.logout') }}"&gt;Chiqish&lt;/a&gt;
{% else %}
  &lt;a href="{{ url_for('auth.login') }}"&gt;Kirish&lt;/a&gt;
{% endif %}</code></pre>

<h3>«next» URL — UX uchun muhim</h3>
<p>Foydalanuvchi <code>/notes/new</code> ga kirmoqchi, lekin login bo'lmagan. Flask-Login uni <code>/auth/login?next=/notes/new</code>'ga yuboradi. Login muvaffaqiyatli bo'lgach, <code>request.args.get('next')</code> orqali asl URL ni o'qib, foydalanuvchini o'sha yerga qaytaramiz. Bu UX uchun katta farq.</p>
"""

L8_CODE = """\
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import CONFIGS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Avval login qiling'

    from app import models  # noqa: F401

    from app.auth.routes import auth_bp
    from app.notes.routes import notes_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    return app


# app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    notes = db.relationship('Note', back_populates='user',
                            cascade='all, delete-orphan')

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# app/auth/routes.py
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)
from flask_login import login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('auth/login.html')

    user = User.query.filter_by(username=request.form['username']).first()
    if not user or not user.check_password(request.form['password']):
        flash('Username yoki parol xato')
        return redirect(url_for('auth.login'))

    login_user(user, remember=bool(request.form.get('remember')))
    next_page = request.args.get('next') or url_for('main.home')
    return redirect(next_page)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
"""


L9_TEXT = """\
<h2>Roli va kirish nazorati (RBAC)</h2>
<p>Real ilovalarda «login bor / yo'q» yetarli emas — odatda turli rollar mavjud: admin, oddiy foydalanuvchi, moderator. Har birining huquqlari boshqacha. Bu pattern <strong>RBAC</strong> (Role-Based Access Control) deyiladi.</p>

<h3>Eng oddiy yondashuv — string ustun</h3>
<p>Boshlash uchun User modeliga oddiy <code>role</code> ustun qo'shamiz:</p>
<pre><code>class User(UserMixin, db.Model):
    # ... id, username, email, password_hash ...
    role = db.Column(db.String(20), default='user', nullable=False)

    def is_admin(self):
        return self.role == 'admin'</code></pre>
<p>3-4 ta rol bilan bu yetarli. Agar 20+ ta rol va har birining huquqlari murakkab bo'lsa — alohida Role va Permission jadvallari kerak (bu darsdan tashqari).</p>

<h3>@admin_required dekorator</h3>
<p>Flask-Login'ning <code>@login_required</code>'i bor, lekin «faqat admin» kerak bo'lsa o'zimiz dekorator yozamiz:</p>
<pre><code>from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # yoki redirect(url_for('auth.login'))
        if not current_user.is_admin():
            abort(403)  # Forbidden
        return view(*args, **kwargs)
    return wrapped</code></pre>
<p>Ishlatish:</p>
<pre><code>@admin_bp.route('/users')
@admin_required
def list_all_users():
    return render_template('admin/users.html',
                           users=User.query.all())</code></pre>

<h3>HTTP status kodlari muhim</h3>
<p>Diqqat: <code>401</code> va <code>403</code> bir xil emas:</p>
<ul>
<li><strong>401 Unauthorized</strong>: «kim ekanligingiz noma'lum, login qiling».</li>
<li><strong>403 Forbidden</strong>: «kim ekaningizni bilamiz, lekin sizga ruxsat yo'q».</li>
</ul>
<p>Foydalanuvchi login bo'lgan, lekin admin emas — bu 403. Login bo'lmagan — bu 401 (yoki redirect /login'ga).</p>

<h3>«Faqat o'z resursingiz» pattern (object-level)</h3>
<p>RBAC ko'pincha «admin hammasini ko'radi, oddiy foydalanuvchi faqat o'zinikini» degan qoidaga keladi. Bu rol emas — <strong>obyekt egasi</strong>ga tekshiruv:</p>
<pre><code>@notes_bp.route('/<int:id>/edit')
@login_required
def edit_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)

    # Admin ham, ega ham tahrirlay oladi; boshqalar 403
    if not (current_user.is_admin() or note.user_id == current_user.id):
        abort(403)

    return render_template('notes/edit.html', note=note)</code></pre>
<p>Bu logikani yozishni unutmang — aks holda har kim har kimning notalarini o'zgartira oladi (eng keng tarqalgan xavfsizlik xatosi — <strong>broken object level authorization</strong>).</p>

<h3>Shablonda ko'rsatish</h3>
<pre><code>{% if current_user.is_authenticated %}
  {% if current_user.is_admin() %}
    &lt;a href="{{ url_for('admin.list_all_users') }}"&gt;Admin paneli&lt;/a&gt;
  {% endif %}

  {% if note.user_id == current_user.id or current_user.is_admin() %}
    &lt;a href="{{ url_for('notes.edit_note', id=note.id) }}"&gt;Tahrirlash&lt;/a&gt;
  {% endif %}
{% endif %}</code></pre>
<p>Shablonda yashirish — UX uchun. Lekin <strong>server tomonida ham tekshirish majburiy</strong> — chunki foydalanuvchi URL ni qo'lda yozishi mumkin.</p>
"""

L9_CODE = """\
# app/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    \"\"\"Ko'p rollar uchun: @role_required('admin', 'moderator')\"\"\"
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


# app/models.py — User ga role qo'shildi
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)

    def is_admin(self):
        return self.role == 'admin'

    def owns(self, obj):
        return getattr(obj, 'user_id', None) == self.id


# app/notes/routes.py — obyekt darajasidagi tekshiruv
from flask import abort
from flask_login import login_required, current_user
from app.decorators import admin_required

@notes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    if not (current_user.owns(note) or current_user.is_admin()):
        abort(403)
    # ... edit logikasi
    return render_template('notes/edit.html', note=note)


# app/admin/routes.py — adminga maxsus
from flask import Blueprint, render_template
from app.models import User
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@admin_required
def list_users():
    return render_template('admin/users.html', users=User.query.all())


# app/__init__.py da custom error sahifalari (ixtiyoriy)
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401
"""


R2_TEXT = """\
<h2>R2 — Modul 3 takrorlash</h2>
<p>Modul 1+2 dagi sof ilovani endi haqiqiy autentifikatsiya bilan to'ldiramiz: ro'yxatdan o'tish, login, parol hashing, sessiya boshqaruvi va rol-asoslangan kirish.</p>

<h3>Nimani takrorlaymiz?</h3>
<ul>
<li><strong>L7</strong> — werkzeug.security bilan parol hashing</li>
<li><strong>L8</strong> — Flask-Login: login_user, logout_user, current_user, @login_required</li>
<li><strong>L9</strong> — Roli va obyekt darajasidagi tekshiruv (admin / ega)</li>
</ul>

<h3>Eslatma jadvali</h3>
<pre><code>┌─────────────────────────┬──────────────────────────────────────────┐
│ Aniq holat              │ Qaysi vositadan foydalanasiz?            │
├─────────────────────────┼──────────────────────────────────────────┤
│ Yangi user yaratish     │ user.set_password(raw); db.session.add   │
│ Login tekshirish        │ user.check_password(raw)                 │
│ Foydalanuvchini eslash  │ login_user(user, remember=True)          │
│ Sahifani himoyalash     │ @login_required                          │
│ Adminga maxsus          │ @admin_required (o'zimiz yozgan)         │
│ «O'zimniki» tekshirish  │ obj.user_id == current_user.id           │
│ Chiqish                 │ logout_user()                            │
│ Shablonda foydalanuvchi │ current_user.is_authenticated / .username│
└─────────────────────────┴──────────────────────────────────────────┘</code></pre>

<h3>Loyiha — Ko'p foydalanuvchili blog</h3>
<p>Modul 3 ning mukammal mashqi — ko'p foydalanuvchili blog. Har kim post yoza oladi, lekin faqat o'z postini tahrirlay yoki o'chira oladi. Adminlar esa hamma narsani boshqaradi.</p>

<h3>Tekshirish ro'yxati</h3>
<ul>
<li>User (UserMixin, role) + Post (user_id) modellari</li>
<li>password_hash 255 belgi, generate_password_hash bilan</li>
<li>/auth/register — email + username + parol (min 8) bilan</li>
<li>/auth/login — username/email + parol, remember me bilan</li>
<li>?next=... bilan kirilgan sahifaga qaytish</li>
<li>/posts/new — faqat login bo'lganlar uchun</li>
<li>/posts/&lt;id&gt;/edit, /posts/&lt;id&gt;/delete — faqat ega yoki admin</li>
<li>/admin/users — faqat admin (har userning ro'yxati, rolini o'zgartirish)</li>
<li>403 va 404 uchun chiroyli xato sahifalari</li>
<li>Shablonda is_authenticated va is_admin tekshiruvi</li>
</ul>
"""

R2_CODE = """\
# app/auth/routes.py — to'liq ro'yxatdan o'tish va login
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth',
                    template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method != 'POST':
        return render_template('auth/register.html')

    username = request.form['username'].strip()
    email    = request.form['email'].strip().lower()
    password = request.form['password']

    if not username or not email or len(password) < 8:
        flash("Username, email va parol (min 8 belgi) majburiy")
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash("Bu username band")
        return redirect(url_for('auth.register'))
    if User.query.filter_by(email=email).first():
        flash("Bu email allaqachon ishlatilgan")
        return redirect(url_for('auth.register'))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("Tabriklaymiz! Endi login qiling.")
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('auth/login.html')

    identifier = request.form['identifier'].strip().lower()
    user = (User.query
            .filter((User.username == identifier) |
                    (User.email == identifier))
            .first())

    if not user or not user.check_password(request.form['password']):
        flash("Username/email yoki parol xato")
        return redirect(url_for('auth.login'))

    login_user(user, remember=bool(request.form.get('remember')))
    return redirect(request.args.get('next') or url_for('main.home'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# app/posts/routes.py — ega tekshiruvi
from flask import abort
from flask_login import login_required, current_user
from app.models import Post

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')


@posts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = db.session.get(Post, id)
    if not post:
        abort(404)
    if not (current_user.owns(post) or current_user.is_admin()):
        abort(403)

    if request.method == 'POST':
        post.title = request.form['title']
        post.body  = request.form['body']
        db.session.commit()
        flash("Post yangilandi")
        return redirect(url_for('posts.show_post', id=post.id))
    return render_template('posts/edit.html', post=post)


@posts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = db.session.get(Post, id)
    if not post:
        abort(404)
    if not (current_user.owns(post) or current_user.is_admin()):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post o'chirildi")
    return redirect(url_for('posts.list_posts'))


# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

CONFIGS = {'development': DevelopmentConfig}
"""


# ╔═══════════════════════════════════════════════════════════════════════════
# ║ MODULE 4 — Real forms and uploads
# ╚═══════════════════════════════════════════════════════════════════════════

L10_TEXT = """\
<h2>Flask-WTF — formalar va CSRF himoyasi</h2>
<p>Asoslar kursida biz <code>request.form['username']</code> orqali ma'lumotlarni qo'lda olib, validatsiyani har route'da yozardik. Bu ishlaydi, lekin kod tarqalib ketadi: bo'sh maydonni tekshirish, email formatini tekshirish, xato xabarlarni shablonga o'tkazish — har joyda qaytariladi.</p>
<p><strong>Flask-WTF</strong> formani Python klass sifatida tasvirlash imkonini beradi. U validatsiyani, render qilishni va — bu juda muhim — <strong>CSRF himoyasini</strong> avtomatik qo'shadi.</p>

<h3>O'rnatish</h3>
<pre><code>pip install Flask-WTF email-validator</code></pre>
<p><code>email-validator</code> — Email validatorida ishlatiladi, alohida o'rnatish kerak.</p>

<h3>Birinchi forma klassi</h3>
<pre><code># app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80),
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
    ])
    password = PasswordField('Parol', validators=[
        DataRequired(),
        Length(min=8, message='Parol kamida 8 belgi'),
    ])
    confirm = PasswordField('Parolni qayta yozing', validators=[
        DataRequired(),
        EqualTo('password', message='Parollar mos kelmadi'),
    ])
    submit = SubmitField('Ro\\'yxatdan o\\'tish')</code></pre>

<h3>Route'da ishlatish</h3>
<pre><code>from .forms import RegisterForm

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Bu yerga faqat POST + barcha validatorlar o'tgan bo'lsa keladi
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Ro'yxatdan o'tdingiz!")
        return redirect(url_for('auth.login'))

    # GET yoki validatsiya xatosi — formani qayta render qilamiz
    return render_template('auth/register.html', form=form)</code></pre>
<p><code>validate_on_submit()</code> — bitta qator bilan ikki ishni qiladi: «POST so'rovmi» va «barcha validatorlar o'tdimi».</p>

<h3>Shablonda render qilish</h3>
<pre><code>&lt;form method="POST"&gt;
  {{ form.hidden_tag() }}   {# CSRF token shu yerda yashirin #}

  &lt;div&gt;
    {{ form.username.label }}
    {{ form.username(class_="input") }}
    {% for error in form.username.errors %}
      &lt;span class="error"&gt;{{ error }}&lt;/span&gt;
    {% endfor %}
  &lt;/div&gt;

  &lt;div&gt;
    {{ form.email.label }}
    {{ form.email(class_="input") }}
    {% for error in form.email.errors %}
      &lt;span class="error"&gt;{{ error }}&lt;/span&gt;
    {% endfor %}
  &lt;/div&gt;

  {{ form.submit() }}
&lt;/form&gt;</code></pre>

<h3>CSRF nima va nima uchun muhim?</h3>
<p><strong>CSRF</strong> (Cross-Site Request Forgery) — bu hujum turi. Misol: siz bankingiz saytida login bo'lib o'tirgansiz. Boshqa zararli sayt sizga <code>&lt;img src="https://bank.com/transfer?to=hacker&amp;amount=1000"&gt;</code> ko'rsatadi. Brauzer rasmni yuklash uchun avtomatik bank cookie'ngizni jo'natadi — pul o'tib ketadi.</p>
<p><strong>CSRF token</strong> — bu serverning har formaga qo'shadigan tasodifiy maxfiy satr. Faqat sizning brauzeringizdagi sahifa uni biladi. Hujumchining sayti CSRF tokenni bila olmaydi → uning POST so'rovi rad etiladi.</p>
<p>Flask-WTF buni avtomatik qo'shadi — sizga faqat <code>{{ form.hidden_tag() }}</code> chaqirish kifoya. Konfiguratsiyada <code>SECRET_KEY</code> bo'lishi shart (CSRF tokenni imzolash uchun).</p>

<h3>SelectField va TextAreaField</h3>
<pre><code>from wtforms import SelectField, TextAreaField

class PostForm(FlaskForm):
    title = StringField('Sarlavha', validators=[DataRequired(), Length(max=200)])
    body  = TextAreaField('Matn',  validators=[DataRequired()])
    category = SelectField('Kategoriya',
        choices=[('news', 'Yangiliklar'),
                 ('how-to', 'Qo\\'llanma'),
                 ('opinion', 'Fikr')],
        validators=[DataRequired()],
    )</code></pre>

<h3>Maxsus validator</h3>
<pre><code>from wtforms.validators import ValidationError

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Bu username band')</code></pre>
<p>Klass ichidagi <code>validate_&lt;field_name&gt;</code> metodi avtomatik chaqiriladi.</p>

<h3>Forma turi sifatida: GET formalari</h3>
<p>Qidiruv formalari uchun CSRF kerak emas — GET so'rovi state'ni o'zgartirmaydi. <code>FlaskForm</code> o'rniga oddiy <code>Form</code> ishlatamiz:</p>
<pre><code>from flask_wtf import FlaskForm

class SearchForm(FlaskForm):
    class Meta:
        csrf = False   # GET form CSRF kerak emas

    q = StringField('Qidirish', validators=[DataRequired()])</code></pre>
"""

L10_CODE = """\
# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField,
                     SubmitField, TextAreaField, SelectField)
from wtforms.validators import (DataRequired, Email, Length,
                                EqualTo, ValidationError)
from app.models import User


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=80),
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(),
    ])
    password = PasswordField('Parol', validators=[
        DataRequired(),
        Length(min=8, message='Parol kamida 8 belgi'),
    ])
    confirm = PasswordField('Parolni qayta yozing', validators=[
        DataRequired(),
        EqualTo('password', message='Parollar mos kelmadi'),
    ])
    submit = SubmitField("Ro'yxatdan o'tish")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Bu username band')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Bu email allaqachon ishlatilgan")


class LoginForm(FlaskForm):
    identifier = StringField('Username yoki email',
                             validators=[DataRequired()])
    password   = PasswordField('Parol', validators=[DataRequired()])
    remember   = BooleanField('Eslab qol')
    submit     = SubmitField('Kirish')


class PostForm(FlaskForm):
    title = StringField('Sarlavha', validators=[
        DataRequired(), Length(max=200),
    ])
    body = TextAreaField('Matn', validators=[DataRequired()])
    category = SelectField('Kategoriya',
        choices=[('news', 'Yangiliklar'),
                 ('how-to', "Qo'llanma"),
                 ('opinion', 'Fikr')],
        validators=[DataRequired()])
    submit = SubmitField('Saqlash')


# app/auth/routes.py
from .forms import RegisterForm, LoginForm

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Ro'yxatdan o'tdingiz!")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# templates/auth/register.html
# <form method="POST">
#   {{ form.hidden_tag() }}
#   <div>
#     {{ form.username.label }} {{ form.username(class_="input") }}
#     {% for err in form.username.errors %}
#       <span class="error">{{ err }}</span>
#     {% endfor %}
#   </div>
#   ...
#   {{ form.submit() }}
# </form>
"""


L11_TEXT = """\
<h2>Fayl yuklash — xavfsiz va to'g'ri</h2>
<p>Avatarlar, hujjatlar, rasm galereyalari — har real ilovada fayl yuklash mavjud. Lekin bu eng xavfli xususiyatlardan biri: noto'g'ri yozsangiz, hujumchi serveringizga PHP skript yuklab ishga tushirishi mumkin.</p>

<h3>Asosiy qoidalar</h3>
<ol>
<li><strong>Hech qachon foydalanuvchidan kelgan fayl nomiga ishonmang.</strong> Uni har doim <code>secure_filename()</code> bilan tozalang.</li>
<li><strong>Fayl turini kengaytma bilan emas, mazmunini tekshirib aniqlang</strong> — lekin minimum sifatida kengaytma whitelist'ini ham qiling.</li>
<li><strong>Fayl o'lchamini chegaralang</strong> — aks holda kimdir 10 GB fayl yuklab diskni to'ldiradi.</li>
<li><strong>Yuklangan fayllarni hech qachon ishga tushiriladigan joyda saqlamang.</strong> Yuklash papkasi kod katalogidan tashqarida bo'lsin.</li>
<li><strong>Faylga noyob nom bering</strong> (UUID) — aks holda bir xil nomli fayllar bir-birini o'chiradi.</li>
</ol>

<h3>FlaskForm bilan fayl maydoni</h3>
<pre><code>from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

ALLOWED_IMG = ['jpg', 'jpeg', 'png', 'gif', 'webp']

class AvatarForm(FlaskForm):
    avatar = FileField('Rasm', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_IMG, "Faqat rasm fayllari"),
    ])
    submit = SubmitField('Yuklash')</code></pre>
<p><code>FileAllowed</code> kengaytmani tekshiradi. Bu yetarli emas (chunki <code>evil.jpg</code> ichida PHP bo'lishi mumkin), lekin birinchi himoya qatlami.</p>

<h3>Saqlash logikasi</h3>
<pre><code>import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_DIR = '/var/uploads'  # config dan o'qish yaxshi

@user_bp.route('/avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    form = AvatarForm()
    if form.validate_on_submit():
        file = form.avatar.data

        # 1. Xavfsiz nom yaratish
        safe = secure_filename(file.filename)
        ext = safe.rsplit('.', 1)[-1].lower()
        new_name = f"{uuid.uuid4().hex}.{ext}"

        # 2. Saqlash
        path = os.path.join(current_app.config['UPLOAD_DIR'], new_name)
        file.save(path)

        # 3. Bazaga yo'lni yozish
        current_user.avatar = new_name
        db.session.commit()

        flash('Rasm yuklandi')
        return redirect(url_for('user.profile'))

    return render_template('user/avatar.html', form=form)</code></pre>

<h3>Yuklangan faylni xizmat qilish</h3>
<p>Yuklash papkasi <code>static/</code>'dan tashqarida bo'lsa, alohida route kerak:</p>
<pre><code>from flask import send_from_directory

@user_bp.route('/uploads/&lt;filename&gt;')
def serve_upload(filename):
    return send_from_directory(
        current_app.config['UPLOAD_DIR'],
        filename,
    )</code></pre>
<p><code>send_from_directory</code> path traversal hujumlaridan himoyalaydi — <code>../../etc/passwd</code> kabi nomlar rad etiladi.</p>

<h3>Fayl o'lchamini cheklash</h3>
<p>Konfiguratsiyada bitta sozlama:</p>
<pre><code>app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024   # 5 MB</code></pre>
<p>Bundan kattaroq fayl yuborilsa, Flask avtomatik 413 (Request Entity Too Large) qaytaradi. Buni chiroyli xato sahifasi bilan tutib olish mumkin:</p>
<pre><code>@app.errorhandler(413)
def too_large(e):
    return render_template('errors/too_large.html'), 413</code></pre>

<h3>Forma multipart bo'lishi kerak</h3>
<p>HTML formada faylni yuborish uchun maxsus encoding kerak:</p>
<pre><code>&lt;form method="POST" enctype="multipart/form-data"&gt;
  {{ form.hidden_tag() }}
  {{ form.avatar() }}
  {{ form.submit() }}
&lt;/form&gt;</code></pre>
<p><code>enctype="multipart/form-data"</code> yo'q bo'lsa, fayl serverga umuman yetib kelmaydi — <code>form.avatar.data</code> bo'sh bo'ladi.</p>

<h3>Fayl turini ICHKI tekshirish (bonus)</h3>
<p>Kengaytma whitelist kuchli emas — <code>evil.jpg</code> ichida PHP bo'lishi mumkin. Haqiqiy turini aniqlash uchun <code>imghdr</code> (rasmlar uchun) yoki <code>python-magic</code>:</p>
<pre><code>import imghdr

def real_image_type(stream):
    head = stream.read(512)
    stream.seek(0)
    return imghdr.what(None, head)   # 'jpeg', 'png', None va h.k.

# Ishlatish:
if real_image_type(file.stream) not in ('jpeg', 'png', 'gif', 'webp'):
    flash('Bu rasm fayli emas')
    return redirect(...)</code></pre>
"""

L11_CODE = """\
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_DIR = os.environ.get('UPLOAD_DIR') or \\
        os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB


# app/user/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

ALLOWED_IMG = ['jpg', 'jpeg', 'png', 'gif', 'webp']


class AvatarForm(FlaskForm):
    avatar = FileField('Rasm', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_IMG, 'Faqat rasm fayllari ruxsat etiladi'),
    ])
    submit = SubmitField('Yuklash')


# app/user/routes.py
import os, uuid, imghdr
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   current_app, send_from_directory)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from .forms import AvatarForm, ALLOWED_IMG

user_bp = Blueprint('user', __name__, url_prefix='/user',
                    template_folder='templates')


def _real_image_type(stream):
    head = stream.read(512)
    stream.seek(0)
    return imghdr.what(None, head)


@user_bp.route('/avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    form = AvatarForm()
    if form.validate_on_submit():
        file = form.avatar.data

        # Ichki turini tekshirish — kengaytma yetarli emas
        if _real_image_type(file.stream) not in ('jpeg', 'png', 'gif', 'webp'):
            flash('Bu haqiqiy rasm fayli emas')
            return redirect(url_for('user.upload_avatar'))

        # Xavfsiz nom + UUID bilan noyoblik
        safe = secure_filename(file.filename or 'avatar')
        ext = safe.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_IMG:
            ext = 'jpg'
        new_name = f"{uuid.uuid4().hex}.{ext}"

        # Yuklash papkasi mavjud bo'lishi kerak (deploy paytida yaratiladi)
        upload_dir = current_app.config['UPLOAD_DIR']
        os.makedirs(upload_dir, exist_ok=True)

        path = os.path.join(upload_dir, new_name)
        file.save(path)

        current_user.avatar = new_name
        db.session.commit()

        flash('Avatar yangilandi')
        return redirect(url_for('user.profile'))

    return render_template('user/avatar.html', form=form)


@user_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(
        current_app.config['UPLOAD_DIR'],
        filename,
    )


# app/__init__.py — error handler
@app.errorhandler(413)
def too_large(e):
    return render_template('errors/too_large.html'), 413


# templates/user/avatar.html
# <form method="POST" enctype="multipart/form-data">
#   {{ form.hidden_tag() }}
#   {{ form.avatar() }}
#   {% for err in form.avatar.errors %}
#     <p class="error">{{ err }}</p>
#   {% endfor %}
#   {{ form.submit() }}
# </form>
"""


# ╔═══════════════════════════════════════════════════════════════════════════
# ║ MODULE 5 — APIs and email
# ╚═══════════════════════════════════════════════════════════════════════════

L12_TEXT = """\
<h2>REST API'ni to'g'ri qurish</h2>
<p>Asoslar kursida biz oddiy <code>jsonify</code> ishlatdik. Endi haqiqiy REST API ishlab chiqamiz: to'g'ri HTTP status kodlari, izchil JSON formati, xatolar uchun standart javob shakli va alohida API Blueprint.</p>

<h3>REST asoslari</h3>
<p>REST — bu HTTP metodlari va URL'larni resurslarga moslab ishlatish konvensiyasi.</p>
<pre><code>┌────────┬──────────────────┬─────────────────────────────────┐
│ Metod  │ URL              │ Vazifa                          │
├────────┼──────────────────┼─────────────────────────────────┤
│ GET    │ /api/notes       │ Barcha notalarni olish (200)    │
│ GET    │ /api/notes/&lt;id&gt;  │ Bitta nota (200) yoki 404       │
│ POST   │ /api/notes       │ Yangi nota (201)                │
│ PUT    │ /api/notes/&lt;id&gt;  │ To'liq yangilash (200)          │
│ PATCH  │ /api/notes/&lt;id&gt;  │ Qisman yangilash (200)          │
│ DELETE │ /api/notes/&lt;id&gt;  │ O'chirish (204)                 │
└────────┴──────────────────┴─────────────────────────────────┘</code></pre>

<h3>HTTP status kodlar</h3>
<ul>
<li><strong>200 OK</strong> — muvaffaqiyatli GET, PUT, PATCH</li>
<li><strong>201 Created</strong> — POST muvaffaqiyatli, yangi resurs yaratildi</li>
<li><strong>204 No Content</strong> — DELETE muvaffaqiyatli (javob tanasiz)</li>
<li><strong>400 Bad Request</strong> — JSON noto'g'ri yoki maydonlar yetishmaydi</li>
<li><strong>401 Unauthorized</strong> — autentifikatsiya kerak</li>
<li><strong>403 Forbidden</strong> — autentifikatsiya bor, lekin ruxsat yo'q</li>
<li><strong>404 Not Found</strong> — resurs topilmadi</li>
<li><strong>422 Unprocessable Entity</strong> — validatsiya xatosi (alternativ 400 ga)</li>
<li><strong>500 Internal Server Error</strong> — server xatosi</li>
</ul>

<h3>API Blueprint</h3>
<p>API route'larini odatda alohida Blueprint'da saqlaymiz — chunki ular HTML emas, JSON qaytaradi va URL'lari <code>/api/</code> bilan boshlanadi.</p>
<pre><code># app/api/__init__.py
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import notes, errors    # routes va error handlerlar</code></pre>

<h3>Asosiy CRUD route'lari</h3>
<pre><code># app/api/notes.py
from flask import request, jsonify, abort, url_for
from app import db
from app.models import Note
from . import api_bp


def note_to_dict(note):
    return {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': note.user_id,
        'created_at': note.created_at.isoformat(),
    }


@api_bp.route('/notes', methods=['GET'])
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([note_to_dict(n) for n in notes])


@api_bp.route('/notes/&lt;int:id&gt;', methods=['GET'])
def get_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    return jsonify(note_to_dict(note))


@api_bp.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    body  = (data.get('body') or '').strip()

    if not title:
        return jsonify({'error': 'title majburiy'}), 400

    note = Note(title=title, body=body, user_id=1)  # auth keyingi darsda
    db.session.add(note)
    db.session.commit()

    response = jsonify(note_to_dict(note))
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_note', id=note.id)
    return response


@api_bp.route('/notes/&lt;int:id&gt;', methods=['PUT'])
def update_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    data = request.get_json(silent=True) or {}
    note.title = (data.get('title') or note.title).strip()
    note.body  = (data.get('body') or note.body).strip()
    db.session.commit()
    return jsonify(note_to_dict(note))


@api_bp.route('/notes/&lt;int:id&gt;', methods=['DELETE'])
def delete_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    db.session.delete(note)
    db.session.commit()
    return '', 204</code></pre>

<h3>Xato javoblarni standart qilish</h3>
<p>Flask'ning default <code>abort(404)</code> javobi HTML qaytaradi. API uchun esa JSON kerak. Buni Blueprint'ga maxsus errorhandler bilan hal qilamiz:</p>
<pre><code># app/api/errors.py
from flask import jsonify
from . import api_bp

def _err(code, message):
    return jsonify({'error': message, 'status': code}), code

@api_bp.app_errorhandler(404)
def not_found(e):
    return _err(404, 'Resource not found')

@api_bp.app_errorhandler(400)
def bad_request(e):
    return _err(400, str(e.description) or 'Bad request')

@api_bp.app_errorhandler(500)
def server_error(e):
    return _err(500, 'Internal server error')</code></pre>

<h3>request.get_json(silent=True) muhim</h3>
<p><code>silent=True</code> JSON noto'g'ri bo'lganda exception ko'tarmaydi, <code>None</code> qaytaradi. Bu sizga foydali xato xabari ko'rsatish imkonini beradi:</p>
<pre><code>data = request.get_json(silent=True)
if data is None:
    return jsonify({'error': 'JSON tana kutilgan'}), 400</code></pre>

<h3>curl bilan testlash</h3>
<pre><code>$ curl http://localhost:5000/api/notes
$ curl http://localhost:5000/api/notes/1
$ curl -X POST http://localhost:5000/api/notes \\
    -H "Content-Type: application/json" \\
    -d '{"title":"Salom","body":"Birinchi nota"}'
$ curl -X DELETE http://localhost:5000/api/notes/1</code></pre>
"""

L12_CODE = """\
# app/api/__init__.py
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import notes, errors  # noqa: F401, E402


# app/api/notes.py
from flask import request, jsonify, abort, url_for
from app import db
from app.models import Note
from . import api_bp


def note_to_dict(note):
    return {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': note.user_id,
        'created_at': note.created_at.isoformat(),
    }


@api_bp.route('/notes', methods=['GET'])
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([note_to_dict(n) for n in notes])


@api_bp.route('/notes/<int:id>', methods=['GET'])
def get_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    return jsonify(note_to_dict(note))


@api_bp.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'JSON body required'}), 400

    title = (data.get('title') or '').strip()
    body  = (data.get('body') or '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400

    note = Note(title=title, body=body, user_id=1)
    db.session.add(note)
    db.session.commit()

    response = jsonify(note_to_dict(note))
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_note', id=note.id)
    return response


@api_bp.route('/notes/<int:id>', methods=['PUT'])
def update_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        note.title = (data['title'] or '').strip()
    if 'body' in data:
        note.body = (data['body'] or '').strip()
    db.session.commit()
    return jsonify(note_to_dict(note))


@api_bp.route('/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    note = db.session.get(Note, id)
    if not note:
        abort(404)
    db.session.delete(note)
    db.session.commit()
    return '', 204


# app/api/errors.py
from flask import jsonify
from . import api_bp


def _err(code, message):
    return jsonify({'error': message, 'status': code}), code


@api_bp.app_errorhandler(404)
def not_found(e):
    return _err(404, 'Resource not found')


@api_bp.app_errorhandler(400)
def bad_request(e):
    return _err(400, getattr(e, 'description', None) or 'Bad request')


@api_bp.app_errorhandler(500)
def server_error(e):
    return _err(500, 'Internal server error')
"""


L13_TEXT = """\
<h2>API pagination, filtering va sortlash</h2>
<p>API'da <code>GET /api/notes</code> 100 ming yozuvni bir paketda qaytarmaydi — bu ham server, ham mijoz uchun og'ir. Real API'lar har doim paginatsiya beradi, va ko'pincha filter/sort parametrlarini qabul qiladi.</p>

<h3>Query paramlarni o'qish</h3>
<pre><code>page     = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 20, type=int)
q        = request.args.get('q', '', type=str).strip()
sort     = request.args.get('sort', 'created_at')
order    = request.args.get('order', 'desc')</code></pre>
<p><code>type=int</code> avtomatik o'tkazish + default value beradi. <code>?page=abc</code> kelsa — default <code>1</code> ishlatiladi (xato bermaydi).</p>

<h3>Foydalanuvchi kiritmasini cheklash</h3>
<p>Per-page'ni cheksiz qabul qilmang — kimdir <code>?per_page=100000</code> yuborsa server xotirasi tugaydi:</p>
<pre><code>MAX_PER_PAGE = 100

per_page = min(
    request.args.get('per_page', 20, type=int),
    MAX_PER_PAGE,
)</code></pre>
<p>Xuddi shu mantiq <code>sort</code> uchun: foydalanuvchi har qanday ustun nomini emas, faqat sizga ma'lum ro'yxatdagi ustunlarni bera olsin (aks holda — SQL injection):</p>
<pre><code>SORTABLE = {'created_at', 'title', 'id'}

if sort not in SORTABLE:
    sort = 'created_at'</code></pre>

<h3>Filter va sort'ni qurish</h3>
<pre><code>from sqlalchemy import desc, asc

query = Note.query

if q:
    query = query.filter(or_(
        Note.title.ilike(f'%{q}%'),
        Note.body.ilike(f'%{q}%'),
    ))

direction = desc if order == 'desc' else asc
column = getattr(Note, sort)
query = query.order_by(direction(column))</code></pre>

<h3>Paginate + meta</h3>
<p>Yaxshi API javobi nafaqat sahifa elementlarini, balki «meta» ma'lumotini ham qaytaradi: jami nechta, hozir nechinchi sahifa, oldinga/orqaga URL'lar.</p>
<pre><code>@api_bp.route('/notes', methods=['GET'])
def list_notes():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), MAX_PER_PAGE)

    query = Note.query.order_by(Note.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page,
                                error_out=False)

    return jsonify({
        'items': [note_to_dict(n) for n in pagination.items],
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
        'links': {
            'next': url_for('api.list_notes',
                            page=pagination.next_num,
                            per_page=per_page,
                            _external=True) if pagination.has_next else None,
            'prev': url_for('api.list_notes',
                            page=pagination.prev_num,
                            per_page=per_page,
                            _external=True) if pagination.has_prev else None,
        },
    })</code></pre>

<h3>To'liq misol — qidiruv + filter + sort</h3>
<pre><code>GET /api/notes?q=flask&amp;sort=title&amp;order=asc&amp;page=2&amp;per_page=50

# Javob:
{
  "items": [...],
  "meta": {
    "page": 2, "per_page": 50, "total": 137,
    "pages": 3, "has_next": true, "has_prev": true
  },
  "links": {
    "next": "http://localhost:5000/api/notes?page=3&amp;per_page=50",
    "prev": "http://localhost:5000/api/notes?page=1&amp;per_page=50"
  }
}</code></pre>

<h3>Field selection (sparse fieldsets) — bonus</h3>
<p>Ba'zan mijoz faqat <code>id</code> va <code>title</code> kerak (body kerak emas — u katta). API <code>?fields=id,title</code> qabul qilishi mumkin:</p>
<pre><code>fields = request.args.get('fields', '')
allowed = {'id', 'title', 'body', 'created_at'}

if fields:
    requested = {f.strip() for f in fields.split(',') if f.strip()} &amp; allowed
else:
    requested = allowed

def project(d, keys):
    return {k: d[k] for k in keys if k in d}

return jsonify([project(note_to_dict(n), requested) for n in pagination.items])</code></pre>
"""

L13_CODE = """\
# app/api/notes.py
from flask import request, jsonify, url_for
from sqlalchemy import desc, asc, or_

from app import db
from app.models import Note
from . import api_bp


MAX_PER_PAGE = 100
SORTABLE = {'created_at', 'title', 'id'}


def note_to_dict(note):
    return {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': note.user_id,
        'created_at': note.created_at.isoformat(),
    }


@api_bp.route('/notes', methods=['GET'])
def list_notes():
    # Foydalanuvchi kiritmalarini xavfsiz o'qish
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(MAX_PER_PAGE,
                   max(1, request.args.get('per_page', 20, type=int)))
    q = request.args.get('q', '', type=str).strip()
    sort = request.args.get('sort', 'created_at', type=str)
    order = request.args.get('order', 'desc', type=str)

    if sort not in SORTABLE:
        sort = 'created_at'

    # Asosiy so'rov
    query = Note.query

    if q:
        query = query.filter(or_(
            Note.title.ilike(f'%{q}%'),
            Note.body.ilike(f'%{q}%'),
        ))

    column = getattr(Note, sort)
    direction = desc if order == 'desc' else asc
    query = query.order_by(direction(column))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    def link(num):
        return url_for('api.list_notes',
                       page=num, per_page=per_page,
                       q=q or None, sort=sort, order=order,
                       _external=True)

    return jsonify({
        'items': [note_to_dict(n) for n in pagination.items],
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        },
        'links': {
            'next': link(pagination.next_num) if pagination.has_next else None,
            'prev': link(pagination.prev_num) if pagination.has_prev else None,
            'self': link(pagination.page),
        },
    })


# Test:
#   curl 'http://localhost:5000/api/notes?page=1&per_page=10'
#   curl 'http://localhost:5000/api/notes?q=flask&sort=title&order=asc'
"""


L14_TEXT = """\
<h2>Flask-Mail — email yuborish</h2>
<p>Ro'yxatdan o'tishni tasdiqlash, parolni tiklash, bildirishnomalar — email yuborish har bir real ilovaning qismi. <strong>Flask-Mail</strong> Python'ning <code>smtplib</code>'i ustidan qulay qatlam.</p>

<h3>O'rnatish va sozlash</h3>
<pre><code>pip install Flask-Mail</code></pre>
<pre><code># config.py
import os

class Config:
    # ... boshqa sozlamalar ...
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')   # to'liq email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')   # app password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')</code></pre>

<h3>Application Factory ichida</h3>
<pre><code># app/__init__.py
from flask_mail import Mail

mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)
    mail.init_app(app)
    return app</code></pre>

<h3>Oddiy xat yuborish</h3>
<pre><code>from flask_mail import Message
from app import mail

@auth_bp.route('/welcome-test')
def welcome_test():
    msg = Message(
        subject='Xush kelibsiz!',
        recipients=['student@example.com'],
        body='Bizning ilovamizga xush kelibsiz! Bu oddiy matn xat.',
        html='&lt;h1&gt;Xush kelibsiz!&lt;/h1&gt;&lt;p&gt;HTML versiyasi.&lt;/p&gt;',
    )
    mail.send(msg)
    return 'Yuborildi'</code></pre>

<h3>Asosiy muammo — yuborish bloklaydi</h3>
<p>SMTP serveriga ulanish + yuborish 2-5 soniya olishi mumkin. Foydalanuvchi shu vaqt davomida brauzerda kutadi — yomon UX.</p>
<p>Yechim: <strong>orqa fonda yuborish</strong>. Eng oddiy variant — <code>Thread</code>:</p>
<pre><code>from threading import Thread
from flask import current_app

def _send_async(app, msg):
    with app.app_context():
        mail.send(msg)

def send_async_email(msg):
    Thread(target=_send_async,
           args=(current_app._get_current_object(), msg)).start()</code></pre>
<p>Endi yuborishni navbatga qo'yamiz va foydalanuvchini darhol javob beramiz. <strong>Diqqat:</strong> Threadda <code>current_app</code> mavjud bo'lmaydi — shuning uchun haqiqiy app obyektini <code>_get_current_object()</code> bilan olib o'tkazamiz.</p>

<h3>Email shablonlar</h3>
<p>Xat matnini Python string'da yozish noqulay — Jinja2 shablon ishlating:</p>
<pre><code># templates/email/welcome.html
&lt;h1&gt;Salom, {{ user.username }}!&lt;/h1&gt;
&lt;p&gt;Ro'yxatdan o'tganingiz uchun rahmat.&lt;/p&gt;
&lt;p&gt;Hisobingizni tasdiqlash uchun:
  &lt;a href="{{ confirm_url }}"&gt;{{ confirm_url }}&lt;/a&gt;
&lt;/p&gt;</code></pre>
<pre><code># templates/email/welcome.txt
Salom, {{ user.username }}!

Ro'yxatdan o'tganingiz uchun rahmat.
Hisobingizni tasdiqlash uchun:
{{ confirm_url }}</code></pre>
<pre><code>from flask import render_template

def send_welcome_email(user, confirm_url):
    msg = Message(
        subject='Xush kelibsiz!',
        recipients=[user.email],
        body=render_template('email/welcome.txt',
                             user=user, confirm_url=confirm_url),
        html=render_template('email/welcome.html',
                             user=user, confirm_url=confirm_url),
    )
    send_async_email(msg)</code></pre>
<p>Yaxshi pattern: HTML va plain text versiyalarini ikkalasini ham bering. Eski email klientlar yoki spam filterlar plain text'ni afzal ko'radi.</p>

<h3>Parolni tiklash — token bilan</h3>
<p>Parolni tiklash xatida link bo'lishi kerak: <code>https://app.com/reset/&lt;TOKEN&gt;</code>. Token — bu vaqt bilan tugaydigan imzolangan satr. <code>itsdangerous</code> kutubxonasi (Flask bilan keladi) buni qiladi:</p>
<pre><code>from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def make_reset_token(user_id):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_id, salt='password-reset')

def verify_reset_token(token, max_age=3600):  # 1 soat
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt='password-reset', max_age=max_age)
    except Exception:
        return None</code></pre>
<p>Bu token foydalanuvchi ID'sini SECRET_KEY bilan imzolaydi. Hujumchi tokenni soxtalashtirib bo'lmaydi (kalitni bilmaydi), va token 1 soatdan keyin avtomatik bekor bo'ladi.</p>

<h3>Gmail bilan ishlash</h3>
<p>Gmail'dan yuborish uchun: <strong>App Password</strong> kerak (oddiy parolingiz emas). Google Account → Security → 2-Step Verification → App passwords → yarating va <code>MAIL_PASSWORD</code> ga yozing.</p>
<p>Production'da Gmail tavsiya etilmaydi (kuniga ~500 cheklov, spam'ga tushish ehtimoli). Foydalaning: <strong>SendGrid</strong>, <strong>Mailgun</strong>, <strong>AWS SES</strong>, <strong>Postmark</strong> — bularning hammasida bepul tier mavjud.</p>

<h3>Test paytida</h3>
<p>Testlarda haqiqiy email yubormaslik kerak. Flask-Mail <code>MAIL_SUPPRESS_SEND = True</code> beradi — bu bayroq bilan yuborish o'rniga <code>mail.record_messages()</code> bilan tutib olish mumkin:</p>
<pre><code>def test_register_sends_welcome_email(client):
    with mail.record_messages() as outbox:
        client.post('/auth/register', data={...})
        assert len(outbox) == 1
        assert 'Xush kelibsiz' in outbox[0].subject</code></pre>
"""

L14_CODE = """\
# app/__init__.py
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import CONFIGS

db = SQLAlchemy()
mail = Mail()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])
    db.init_app(app)
    mail.init_app(app)
    return app


# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')


# app/email.py
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def _send_async(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.warning("Email failed: %s", e)


def send_async_email(msg):
    Thread(
        target=_send_async,
        args=(current_app._get_current_object(), msg),
        daemon=True,
    ).start()


def send_welcome_email(user, confirm_url):
    msg = Message(
        subject='Xush kelibsiz!',
        recipients=[user.email],
        body=render_template('email/welcome.txt',
                             user=user, confirm_url=confirm_url),
        html=render_template('email/welcome.html',
                             user=user, confirm_url=confirm_url),
    )
    send_async_email(msg)


def send_reset_email(user, reset_url):
    msg = Message(
        subject='Parolni tiklash',
        recipients=[user.email],
        body=render_template('email/reset.txt',
                             user=user, reset_url=reset_url),
        html=render_template('email/reset.html',
                             user=user, reset_url=reset_url),
    )
    send_async_email(msg)


# app/auth/tokens.py
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def make_reset_token(user_id):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_id, salt='password-reset')


def verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt='password-reset', max_age=max_age)
    except Exception:
        return None


# app/auth/routes.py — parolni tiklash flow
from flask import request, url_for, render_template, flash, redirect
from app.email import send_reset_email
from app.auth.tokens import make_reset_token, verify_reset_token
from app.models import User
from app import db


@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = make_reset_token(user.id)
            reset_url = url_for('auth.reset_password',
                                token=token, _external=True)
            send_reset_email(user, reset_url)
        # Email mavjud emasligini ham aytmaymiz — enumeration himoyasi
        flash("Agar email ro'yxatdan o'tgan bo'lsa, tiklash linki yuborildi")
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot.html')


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    if user_id is None:
        flash("Link eskirgan yoki yaroqsiz")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        user = db.session.get(User, user_id)
        user.set_password(request.form['password'])
        db.session.commit()
        flash("Parol yangilandi. Endi login qiling.")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset.html')
"""


R3_TEXT = """\
<h2>R3 — Modul 4+5 takrorlash + kurs yakuni</h2>
<p>Bu kursning yakuniy mashqi. Modul 4 (formalar + fayl yuklash) va Modul 5 (REST API + email) ni bitta haqiqiy ilovada birlashtiramiz. Bu sizning portfolio'ngiz uchun ham yaxshi loyiha bo'ladi.</p>

<h3>Nimani takrorlaymiz?</h3>
<ul>
<li><strong>L10 Flask-WTF</strong> — formalar, CSRF, validatorlar, maxsus validatorlar</li>
<li><strong>L11 File upload</strong> — secure_filename, FileAllowed, MAX_CONTENT_LENGTH, send_from_directory</li>
<li><strong>L12 REST API</strong> — to'g'ri HTTP kodlar, JSON xatolar, API Blueprint</li>
<li><strong>L13 Pagination/filter</strong> — query params, meta + links javob</li>
<li><strong>L14 Flask-Mail</strong> — async yuborish, shablonlar, itsdangerous token</li>
</ul>

<h3>Loyiha — Mini-Blog: to'liq stack</h3>
<p>Avval qurganlaringizning hammasi: Auth + Roles + Posts + Avatar + REST API + Email. Bu ilovani portfolio'ga qo'shsangiz — mukammal.</p>

<h3>Talab qilinadigan xususiyatlar (texnik ro'yxat)</h3>
<ul>
<li>Application Factory + 4+ Blueprint (main, auth, posts, api)</li>
<li>Modellar: User, Post, Tag (many-to-many), Comment (one-to-many)</li>
<li>Flask-Migrate bilan boshqariladi</li>
<li>Flask-Login: register + login + logout + forgot/reset</li>
<li>Parol tiklash xati (email + itsdangerous token, 1 soat amal qilish)</li>
<li>Avatar yuklash (secure, max 2MB, jpg/png/webp)</li>
<li>Postlar Flask-WTF bilan (CSRF, validatorlar)</li>
<li>REST API: /api/posts (GET/POST), /api/posts/&lt;id&gt; (GET/PUT/DELETE)</li>
<li>API pagination: ?page=&amp;per_page= (max 50), meta + links</li>
<li>API qidiruv: ?q= (title + body ichida)</li>
<li>API xatolari JSON formatida (app_errorhandler)</li>
<li>Rollar: admin user'larni boshqaradi (/admin/users)</li>
<li>README'da: ishga tushirish, .env namunasi, curl misollari, deploy qadamlari</li>
</ul>

<h3>Bonus topshiriqlar</h3>
<ul>
<li>Email tasdiqlash (register paytida — link yuboriladi, foydalanuvchi confirmed=False bo'ladi)</li>
<li>Post yorliqlari — many-to-many, /api/posts?tag=python kabi filtr</li>
<li>API rate limit (Flask-Limiter bilan)</li>
<li>Live demo (Render/Railway) — README'da URL</li>
</ul>

<h3>Tabriklaymiz!</h3>
<p>Agar bu loyihani yetkazib bersangiz — siz endi Flask'ning haqiqiy kutubxonalar va patternlarini biladigan o'rta darajadagi backend dasturchisiz. Keyingi qadamlar: Docker, async views, Celery, testing (pytest), production deploy chuqurroq.</p>
"""

R3_CODE = """\
# Loyiha tuzilishi (taklif)
mini_blog/
├── config.py
├── wsgi.py
├── requirements.txt
├── .env.example
├── migrations/
├── uploads/                  # .gitignore'da
└── app/
    ├── __init__.py           # create_app + db/migrate/login/mail init
    ├── models.py             # User, Post, Tag, Comment
    ├── decorators.py         # @admin_required
    ├── email.py              # send_async_email + send_welcome / send_reset
    ├── auth/
    │   ├── __init__.py
    │   ├── routes.py         # register, login, logout, forgot, reset
    │   ├── forms.py          # Flask-WTF: RegisterForm, LoginForm, ...
    │   └── tokens.py         # make_reset_token, verify_reset_token
    ├── posts/
    │   ├── __init__.py
    │   ├── routes.py         # CRUD HTML
    │   └── forms.py          # PostForm
    ├── api/
    │   ├── __init__.py       # api_bp
    │   ├── posts.py          # /api/posts route'lari
    │   └── errors.py         # JSON xato javoblari
    ├── user/
    │   ├── __init__.py
    │   ├── routes.py         # profile, upload_avatar, serve_upload
    │   └── forms.py          # AvatarForm
    └── templates/
        ├── base.html
        ├── auth/
        ├── posts/
        ├── user/
        ├── admin/
        └── email/
            ├── welcome.html
            ├── welcome.txt
            ├── reset.html
            └── reset.txt


# .env.example
SECRET_KEY=change-me-please
DATABASE_URL=sqlite:///app.db
UPLOAD_DIR=./uploads
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=you@gmail.com
MAIL_PASSWORD=app-password-here


# README.md — curl misollari (qisqartirilgan)
#
#   # Ro'yxatdan o'tish
#   curl -X POST localhost:5000/api/auth/register \\\\
#     -H 'Content-Type: application/json' \\\\
#     -d '{"username":"aziz","email":"aziz@x.uz","password":"abc12345"}'
#
#   # Post yaratish (avtorizatsiya cookie bilan)
#   curl -X POST localhost:5000/api/posts \\\\
#     -H 'Content-Type: application/json' \\\\
#     -b cookies.txt \\\\
#     -d '{"title":"Salom","body":"Birinchi post"}'
#
#   # Paginatsiyali ro'yxat
#   curl 'localhost:5000/api/posts?page=1&per_page=20&q=flask&sort=created_at&order=desc'
"""


R1_CODE = """\
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

CONFIGS = {'development': DevelopmentConfig}


# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import CONFIGS

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(CONFIGS[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    from app import models  # noqa: F401

    from app.main.routes  import main_bp
    from app.items.routes import items_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(items_bp)
    return app


# app/models.py
from datetime import datetime
from app import db

item_tags = db.Table(
    'item_tags',
    db.Column('item_id', db.ForeignKey('items.id'), primary_key=True),
    db.Column('tag_id',  db.ForeignKey('tags.id'),  primary_key=True),
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship('Item', back_populates='user',
                            cascade='all, delete-orphan')

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    location = db.Column(db.String(120), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship('User', back_populates='items')

    tags = db.relationship('Tag', secondary=item_tags, backref='items')


# app/items/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import or_
from app import db
from app.models import Item, Tag

items_bp = Blueprint('items', __name__, url_prefix='/items',
                     template_folder='templates')


@items_bp.route('/')
def list_items():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()

    query = Item.query
    if q:
        query = query.filter(or_(
            Item.title.ilike(f'%{q}%'),
            Item.description.ilike(f'%{q}%'),
        ))

    pagination = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False,
    )
    return render_template('items/list.html',
                           pagination=pagination, q=q)


@items_bp.route('/tag/<tag_name>')
def by_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template('items/by_tag.html', tag=tag)
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise factories (identical to basics' helpers)
# ─────────────────────────────────────────────────────────────────────────────

def mc(title, options, correct, *, multi=False, hint="", explanation="",
       diff="Easy", pts=2):
    return {"title": title, "description": title,
            "exercise_type": "multiple_choice",
            "options": options, "correct_answers": correct,
            "is_multiple_select": multi,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def dd(title, items_in_order, *, hint="", explanation="",
       diff="Medium", pts=3):
    return {"title": title, "description": title,
            "exercise_type": "drag_and_drop",
            "drag_items": list(items_in_order),
            "correct_order": list(items_in_order),
            "is_multiple_select": False,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def ti(title, expected, *, hint="", explanation="",
       diff="Hard", pts=4):
    return {"title": title, "description": title,
            "exercise_type": "text_input",
            "expected_answer": expected,
            "is_multiple_select": False,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


# ─────────────────────────────────────────────────────────────────────────────
# Project assignments (mapped by lesson `order`)
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict[int, dict] = {
    0: {  # L1 Application Factory
        "title": "Factory pattern bilan ilova",
        "description": (
            "Asoslar kursidagi har qanday Flask ilovangizni Application Factory "
            "patternga ko'chiring. config.py da 3 ta klass (Dev/Test/Prod), "
            "create_app(config_name) funksiyasi, wsgi.py entry-point bo'lsin."
        ),
        "requirements": (
            "• config.py: DevelopmentConfig, TestingConfig, ProductionConfig\n"
            "• app/__init__.py da create_app(config_name='development')\n"
            "• wsgi.py faqat factory'ni chaqirsin (3-5 qator)\n"
            "• SECRET_KEY environment'dan o'qiladi (hardcode emas)\n"
            "• README'da development va production tarzda ishga tushirish farqi"
        ),
        "technologies": "Python, Flask, app factory, config classes",
        "deadline_days": 4,
    },
    1: {  # L2 Blueprints
        "title": "Blueprint bilan modul tuzilish",
        "description": (
            "1-darsdagi factory ilovaga 2 ta Blueprint qo'shing: main_bp "
            "(bosh sahifa, about) va notes_bp (oddiy notalar ro'yxati — "
            "hozircha xotirada, baza keyingi darsda). Har Blueprint o'z papkasida."
        ),
        "requirements": (
            "• 2 ta Blueprint: main va notes (alohida papkalarda)\n"
            "• notes_bp ga url_prefix='/notes' o'rnatilgan\n"
            "• Kamida 5 ta xotira-ichi nota (Python list)\n"
            "• Shablonlardagi barcha link'lar url_for('blueprint.funksiya') bilan\n"
            "• Loyiha tuzilishi: app/main/, app/notes/, app/templates/"
        ),
        "technologies": "Python, Flask, Blueprint, url_for, app factory",
        "deadline_days": 5,
    },
    2: {  # L3 Flask-SQLAlchemy
        "title": "SQLAlchemy bilan notlar bazasi",
        "description": (
            "2-darsdagi notes_bp dagi xotira-ichi ro'yxat o'rniga "
            "Flask-SQLAlchemy bilan haqiqiy SQLite bazasi ishlatilsin. "
            "Note modeli yarating va eski ro'yxatni bazaga ko'chiring."
        ),
        "requirements": (
            "• Note modeli: id, title (String 200), body (Text), created_at\n"
            "• db = SQLAlchemy() factory pattern bilan to'g'ri ulangan\n"
            "• Bosh sahifa bazadan yangi-eski tartibda ko'rsatadi\n"
            "• Yangi nota qo'shish formasi (POST) ishlaydi\n"
            "• db.session.rollback() bilan xato bo'lganda toza sessiya\n"
            "• Seed: kamida 5 ta boshlang'ich nota Flask shell orqali qo'shilgan"
        ),
        "technologies": "Python, Flask, Flask-SQLAlchemy, SQLite",
        "deadline_days": 6,
    },
    3: {  # L4 Relationships
        "title": "User → Note (one-to-many) + Tag (many-to-many)",
        "description": (
            "3-darsdagi notlar ilovaga User va Tag modellarini qo'shing. "
            "Har nota bir User'ga tegishli (one-to-many). Har nota bir nechta "
            "Tag olishi mumkin (many-to-many)."
        ),
        "requirements": (
            "• User modeli: id, username (unique)\n"
            "• Note ga user_id ForeignKey + relationship('User', back_populates=...)\n"
            "• User.notes da cascade='all, delete-orphan'\n"
            "• Tag modeli + note_tags oraliq jadval\n"
            "• Note.tags = db.relationship('Tag', secondary=note_tags, backref='notes')\n"
            "• Flask shell skript: 3 user, 6 note, 4 tag yarating va bog'lang\n"
            "• Bosh sahifada nota yonida author va tag'lar ko'rsatiladi"
        ),
        "technologies": "Python, Flask, SQLAlchemy, ForeignKey, relationship, "
                        "secondary table",
        "deadline_days": 6,
    },
    4: {  # L5 Queries + pagination
        "title": "Qidiruv, filtr va sahifalash",
        "description": (
            "4-darsdagi ilovaga to'liq qidiruv va paginatsiya qo'shing. "
            "Foydalanuvchilar 100+ nota orasidan kerakli narsani topa olsin."
        ),
        "requirements": (
            "• Bosh sahifada paginate(page=N, per_page=10, error_out=False)\n"
            "• ?q=... query param bilan title VA body bo'yicha qidiruv "
            "(or_ + ilike)\n"
            "• /tag/<name> sahifasi shu tag bilan barcha notalarni ko'rsatadi\n"
            "• /user/<username> sahifasi shu foydalanuvchining notalari\n"
            "• Sahifa pastida «Oldingi / 2 / 5 / Keyingi» linklari (has_prev/has_next)\n"
            "• joinedload(Note.user) bilan N+1 muammoni hal qiling\n"
            "• Seed: 30+ nota generate qiling (testlash uchun)"
        ),
        "technologies": "Python, Flask, SQLAlchemy, query filters, pagination, "
                        "joinedload, ilike",
        "deadline_days": 7,
    },
    5: {  # L6 Flask-Migrate
        "title": "Flask-Migrate bilan sxemani o'zgartirish",
        "description": (
            "5-darsdagi ilovaga Flask-Migrate o'rnating va Note modeliga "
            "yangi ustun (is_pinned: bool) qo'shing — migration orqali."
        ),
        "requirements": (
            "• flask db init bilan migrations/ papkasi yaratilgan\n"
            "• 1-migration: «initial tables» (User, Note, Tag, note_tags)\n"
            "• 2-migration: «add is_pinned to notes»\n"
            "• Ikkala migration fayli ham git'ga commit qilingan\n"
            "• Bosh sahifada is_pinned=True bo'lgan notalar yuqorida\n"
            "• README'da CLI komandalari: flask db init/migrate/upgrade/downgrade\n"
            "• flask db current va flask db history outputi screenshot bilan"
        ),
        "technologies": "Python, Flask, Flask-Migrate, Alembic, schema migrations",
        "deadline_days": 6,
    },
    6: {  # R1 — Lost & Found (Modul 1+2 takrori)
        "title": "🔁 R1: Yo'qolgan narsalar (Lost & Found)",
        "description": (
            "Modul 1+2 takrori: factory + blueprint + SQLAlchemy + "
            "relationships + qidiruv + paginatsiya + migration ni bir "
            "loyihada birlashtirib qo'ying. Foydalanuvchilar yo'qolgan "
            "narsalari haqida e'lon joylaydi va topganlar yorliq qo'ya oladi."
        ),
        "requirements": (
            "• create_app() factory + Dev/Test/Prod Config klasslari\n"
            "• 2+ Blueprint: main_bp va items_bp\n"
            "• Modellar: User, Item, Tag + Many-to-Many (item_tags)\n"
            "• Flask-Migrate bilan boshlangan (kamida 1 migration)\n"
            "• Bosh sahifada paginatsiya (10/sahifa) + ?q=... qidiruv\n"
            "• /tag/<name> sahifasi: shu tag bilan e'lonlar\n"
            "• Yangi e'lon qo'shish formasi (autentifikatsiya keyingi modulda)\n"
            "• cascade='all, delete-orphan' to'g'ri ishlaydi (test qilingan)\n"
            "• README'da loyihani ishga tushirish va migration qadamlari"
        ),
        "technologies": "Python, Flask, app factory, Blueprint, Flask-SQLAlchemy, "
                        "Flask-Migrate, relationships, pagination",
        "deadline_days": 9,
    },
    7: {  # L7 — Password hashing
        "title": "Ro'yxatdan o'tish + parol hashing",
        "description": (
            "R1 dagi Lost & Found ilovaga ro'yxatdan o'tish sahifasi qo'shing. "
            "Parol ochiq saqlanmasin — werkzeug.security bilan hash qiling. "
            "Hozircha login yo'q (keyingi darsda Flask-Login bilan qo'shamiz)."
        ),
        "requirements": (
            "• User modeliga password_hash (String 255) ustun qo'shildi\n"
            "• set_password(raw) va check_password(raw) metodlari\n"
            "• /auth/register GET (forma) + POST (yaratish)\n"
            "• Validatsiya: username/email majburiy, parol kamida 8 belgi\n"
            "• Mavjudligini tekshirish: username va email unique\n"
            "• Flask-Migrate bilan migration (add password_hash to users)\n"
            "• Flask shell orqali test: User.query.first().check_password('...')"
        ),
        "technologies": "Python, Flask, werkzeug.security, Flask-Migrate, "
                        "form validation",
        "deadline_days": 5,
    },
    8: {  # L8 — Flask-Login
        "title": "Flask-Login bilan to'liq autentifikatsiya",
        "description": (
            "7-darsdagi ilovaga Flask-Login o'rnating: login, logout, "
            "current_user, @login_required. Yangi Item qo'shish faqat login "
            "bo'lganlar uchun, va Item.user_id avtomatik current_user dan olinadi."
        ),
        "requirements": (
            "• User modeliga UserMixin meros\n"
            "• @login_manager.user_loader bilan load_user funksiyasi\n"
            "• login_manager.login_view = 'auth.login' o'rnatilgan\n"
            "• /auth/login (username yoki email + parol + remember me)\n"
            "• ?next=... orqali asl sahifaga qaytish\n"
            "• /auth/logout @login_required bilan\n"
            "• /items/new @login_required bilan (Item.user_id = current_user.id)\n"
            "• Bosh menyuda: login bo'lsa username + Chiqish, bo'lmasa Kirish"
        ),
        "technologies": "Python, Flask, Flask-Login, UserMixin, session-based auth",
        "deadline_days": 6,
    },
    9: {  # L9 — Roles + object-level
        "title": "Roli va obyekt darajasidagi tekshiruv",
        "description": (
            "8-darsdagi ilovaga 2 ta rol qo'shing: 'user' va 'admin'. "
            "Item edit/delete faqat ega yoki admin uchun. Admin uchun "
            "alohida /admin/users sahifasi (barcha foydalanuvchilar ro'yxati)."
        ),
        "requirements": (
            "• User.role ustun ('user' default, 'admin' qo'lda)\n"
            "• @admin_required dekorator (app/decorators.py)\n"
            "• Item edit/delete: ega yoki admin → ruxsat, aks holda 403\n"
            "• /admin/users — barcha userlar ro'yxati, rolni o'zgartirish formasi\n"
            "• 403 va 401 uchun chiroyli xato sahifalari (errorhandler)\n"
            "• Shablonda is_admin() tekshiruvi (admin paneli linki ko'rinadi)\n"
            "• Hech bir tekshiruv FAQAT shablonda emas — server ham tekshiradi"
        ),
        "technologies": "Python, Flask, Flask-Login, RBAC, decorators, abort",
        "deadline_days": 6,
    },
    11: {  # L10 — Flask-WTF
        "title": "Flask-WTF bilan formalar va CSRF",
        "description": (
            "R2 dagi blog ilovasidagi qo'lda yozilgan formalarni Flask-WTF "
            "klasslari bilan almashtiring. CSRF himoyasi avtomatik, "
            "validatorlar deklarativ, xato xabarlari shablonda chiroyli."
        ),
        "requirements": (
            "• 4 ta Form klass: RegisterForm, LoginForm, PostForm, SearchForm\n"
            "• validate_username va validate_email maxsus validatorlari\n"
            "• EqualTo bilan password confirm tekshiruvi\n"
            "• Har shablonda {{ form.hidden_tag() }} (CSRF)\n"
            "• Xato xabarlari har maydon ostida ko'rsatiladi\n"
            "• SearchForm uchun csrf = False (GET form)\n"
            "• Old qo'lda yozilgan validatsiya kodi olib tashlangan"
        ),
        "technologies": "Python, Flask, Flask-WTF, WTForms, validators, CSRF",
        "deadline_days": 5,
    },
    12: {  # L11 — File uploads
        "title": "Avatar yuklash (xavfsiz fayl upload)",
        "description": (
            "11-darsdagi blog'ga avatar yuklash imkoniyatini qo'shing. "
            "Xavfsizlik birinchi: kengaytma whitelist, ichki tur tekshiruvi, "
            "UUID-based nom, fayl o'lcham chegarasi, alohida yuklash papkasi."
        ),
        "requirements": (
            "• User modeliga avatar (String 255) ustun + migration\n"
            "• AvatarForm: FileField + FileRequired + FileAllowed validatorlari\n"
            "• MAX_CONTENT_LENGTH = 5MB konfiguratsiyada\n"
            "• secure_filename + uuid.uuid4().hex bilan noyob nom\n"
            "• imghdr bilan ichki tur tekshiruvi (kengaytma yetarli emas)\n"
            "• Yuklash papkasi static dan tashqarida (uploads/)\n"
            "• /user/uploads/<filename> send_from_directory bilan xizmat\n"
            "• <form enctype=\"multipart/form-data\"> shablonda\n"
            "• 413 (Too Large) uchun chiroyli xato sahifasi\n"
            "• .gitignore'da uploads/ papkasi"
        ),
        "technologies": "Python, Flask, Flask-WTF, werkzeug.utils, uuid, imghdr, "
                        "send_from_directory, MAX_CONTENT_LENGTH",
        "deadline_days": 6,
    },
    10: {  # R2 — Multi-user blog
        "title": "🔁 R2: Ko'p foydalanuvchili blog",
        "description": (
            "Modul 3 takrori: ro'yxatdan o'tish + login + parol hashing + "
            "rollar + obyekt darajasidagi tekshiruv ni birlashtiring. "
            "Har kim post yoza oladi; ega yoki admin tahrirlay/o'chira oladi."
        ),
        "requirements": (
            "• User (UserMixin, role default 'user') + Post (user_id) modellari\n"
            "• /auth/register (email + username + parol min 8)\n"
            "• /auth/login (username yoki email + parol + remember)\n"
            "• ?next=... bilan kirilgan sahifaga qaytish\n"
            "• /posts/new — @login_required bilan\n"
            "• /posts/<id>/edit va /posts/<id>/delete — ega yoki admin (server-side)\n"
            "• /admin/users — faqat admin, rol o'zgartirish formasi\n"
            "• 401 va 403 uchun chiroyli xato sahifalari\n"
            "• Shablonda current_user.is_authenticated va is_admin tekshiruvi\n"
            "• README'da admin user yaratish bo'yicha Flask shell komandasi"
        ),
        "technologies": "Python, Flask, Flask-Login, werkzeug.security, RBAC, "
                        "Flask-Migrate, Blueprint, decorators",
        "deadline_days": 10,
    },
    13: {  # L12 — REST API
        "title": "REST API bilan notalar",
        "description": (
            "R2 dagi blog ilovasiga to'liq REST API qo'shing: /api/posts "
            "(GET/POST), /api/posts/<id> (GET/PUT/DELETE). To'g'ri HTTP "
            "kodlar, JSON xato javoblari, alohida API Blueprint."
        ),
        "requirements": (
            "• Alohida api_bp Blueprint (url_prefix='/api')\n"
            "• GET /api/posts — barcha postlar (200)\n"
            "• GET /api/posts/<id> — bitta post (200) yoki 404\n"
            "• POST /api/posts — yangi post (201) + Location header\n"
            "• PUT /api/posts/<id> — yangilash (200)\n"
            "• DELETE /api/posts/<id> — o'chirish (204)\n"
            "• request.get_json(silent=True) bilan xavfsiz parse\n"
            "• title bo'sh bo'lsa 400 + {'error': 'title required'}\n"
            "• @api_bp.app_errorhandler bilan 404/400/500 uchun JSON javob\n"
            "• Web UI (CRUD) ham ishlashda davom etadi\n"
            "• README'da har endpoint uchun curl misoli"
        ),
        "technologies": "Python, Flask, jsonify, request.get_json, REST, "
                        "HTTP status codes, Blueprint",
        "deadline_days": 6,
    },
    14: {  # L13 — API pagination
        "title": "API pagination, qidiruv va sortlash",
        "description": (
            "L12 dagi /api/posts endpointiga professional API standartiga "
            "mos paginatsiya, qidiruv va sortlash qo'shing. Meta + links "
            "bilan to'liq javob."
        ),
        "requirements": (
            "• ?page= va ?per_page= (max 50, default 20)\n"
            "• ?q= title va body bo'yicha qidiruv (or_ + ilike)\n"
            "• ?sort=created_at|title|id — whitelist tekshiruv (SQL injection emas)\n"
            "• ?order=asc|desc (default desc)\n"
            "• Javob: { items, meta: {page, per_page, total, pages, "
            "has_next, has_prev}, links: {next, prev, self} }\n"
            "• link URL'lari _external=True bilan to'liq URL\n"
            "• Bonus: ?fields=id,title bilan field selection\n"
            "• README'da to'liq curl misoli: ?q=&page=&per_page=&sort=&order="
        ),
        "technologies": "Python, Flask, SQLAlchemy, paginate, query params, "
                        "input validation",
        "deadline_days": 6,
    },
    15: {  # L14 — Flask-Mail
        "title": "Email yuborish + parol tiklash",
        "description": (
            "L13 dagi ilovaga Flask-Mail o'rnating. Ro'yxatdan o'tishda "
            "xush kelibsiz xati va parol tiklash flow (token + email link) "
            "qo'shing. Async yuborish bilan UX'ni sekinlashtirmang."
        ),
        "requirements": (
            "• Flask-Mail o'rnatilgan, MAIL_* konfiguratsiya .env dan\n"
            "• Welcome email register paytida yuboriladi (HTML + plain text)\n"
            "• /auth/forgot — email kiritiladi, agar bor bo'lsa link yuboriladi\n"
            "• Email enumeration himoyasi: javob har doim bir xil\n"
            "• itsdangerous bilan reset token (1 soat amal qiladi)\n"
            "• /auth/reset/<token> — token tekshirish + yangi parol\n"
            "• Eskirgan/yaroqsiz token uchun flash xabar\n"
            "• send_async_email bilan orqa fonda yuborish (Thread)\n"
            "• Email shablonlar: templates/email/welcome.{html,txt}, reset.{html,txt}\n"
            "• Test paytida MAIL_SUPPRESS_SEND=True bilan mail.record_messages"
        ),
        "technologies": "Python, Flask, Flask-Mail, itsdangerous, Thread, "
                        "Jinja2 (email templates), SMTP",
        "deadline_days": 7,
    },
    16: {  # R3 — Mini-Blog capstone
        "title": "🔁 R3: Mini-Blog (kurs capstone)",
        "description": (
            "Kursning yakuniy mashqi: butun 14 darsda o'rganganlaringizni "
            "bitta professional mini-blog ilovasiga birlashtiring. "
            "Auth + Roles + Posts + Avatar + REST API + Email — hammasi birga. "
            "Bu portfolio uchun ham yaxshi loyiha bo'ladi."
        ),
        "requirements": (
            "• Application Factory + 4+ Blueprint (main, auth, posts, api)\n"
            "• Modellar: User, Post, Tag (many-to-many), Comment (one-to-many)\n"
            "• Flask-Migrate bilan boshqariladi (kamida 3 migration)\n"
            "• Flask-Login: register + login + logout + forgot/reset\n"
            "• Email tasdiqlash yoki parol tiklash (itsdangerous token, 1 soat)\n"
            "• Avatar yuklash (xavfsiz, max 2MB, jpg/png/webp + imghdr tekshiruvi)\n"
            "• Postlar Flask-WTF bilan (CSRF, EqualTo, maxsus validatorlar)\n"
            "• REST API: /api/posts (GET/POST), /api/posts/<id> (GET/PUT/DELETE)\n"
            "• API paginatsiya: ?page=&per_page= (max 50), meta + links\n"
            "• API qidiruv ?q= va sort ?sort=&order= (whitelist)\n"
            "• API xatolari JSON formatida (app_errorhandler)\n"
            "• @admin_required: /admin/users sahifa\n"
            "• Live demo (Render/Railway) — README'da URL\n"
            "• README to'liq: ishga tushirish, .env.example, curl misollari, "
            "deploy qadamlari"
        ),
        "technologies": "Python, Flask, Flask-SQLAlchemy, Flask-Migrate, "
                        "Flask-Login, Flask-WTF, Flask-Mail, itsdangerous, "
                        "Blueprint, REST, deploy",
        "deadline_days": 21,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list (in `order` sequence)
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {
        "order": 0, "title": "1-Application Factory pattern",
        "text": L1_TEXT, "code": L1_CODE, "lang": "python",
        "video": "https://youtu.be/eBwjUv8e2fA",
        "exercises": [
            mc("Application Factory pattern asosan nima uchun kerak?",
               ["Ilovani tezroq ishga tushirish uchun",
                "Bitta kod bazasi turli sozlama (dev/test/prod) bilan "
                "ishlay olishi uchun",
                "Flask'ning yangi versiyasini majburlash uchun",
                "URL'larni qisqartirish uchun"],
               "B",
               hint="Test paytida bir xil ilovani boshqa konfiguratsiya bilan "
                    "qayta yaratish kerak — bu qanday hal qilinadi?",
               explanation="Factory pattern bitta create_app() funksiyasini "
                           "har xil sozlamalar bilan chaqirib, dev/test/prod "
                           "uchun alohida ilovalar yaratish imkonini beradi.",
               diff="Easy", pts=2),
            mc("Kengaytma (masalan SQLAlchemy) ni factory pattern bilan "
               "qanday to'g'ri ulanadi?",
               ["db = SQLAlchemy(app)  # modul darajasida ilova bilan",
                "Modul darajasida db = SQLAlchemy() yaratamiz, "
                "create_app ichida db.init_app(app) chaqiramiz",
                "Har route ichida yangi SQLAlchemy() yaratamiz",
                "Hech qanday kengaytma ishlatib bo'lmaydi"],
               "B",
               hint="Kengaytma ilova mavjud bo'lishidan oldin yaratiladi, "
                    "lekin ilovaga keyinroq bog'lanadi.",
               explanation="db = SQLAlchemy() ilovasiz yaratiladi, keyin "
                           "create_app ichida db.init_app(app) orqali "
                           "bog'lanadi — shunda aylanma import muammosi "
                           "yo'qoladi.",
               diff="Medium", pts=3),
            mc("Quyidagilardan qaysilari factory pattern uchun to'g'ri "
               "qoidalar?",
               ["create_app() har chaqirilganda yangi Flask ilovasini "
                "qaytaradi",
                "Konfiguratsiya app.config.from_object orqali yuklanadi",
                "Global app = Flask(__name__) ishlatish majburiy",
                "Kengaytmalar har route ichida qayta init qilinadi"],
               "A,B", multi=True,
               hint="Ikki to'g'ri va ikki noto'g'ri javob bor.",
               diff="Medium", pts=3),
            dd("Application Factory ilovasini ishga tushirish bosqichlarini "
               "to'g'ri tartibda joylang",
               ["config.py da Config klasslarini yozish",
                "app/__init__.py da create_app(config_name) yozish",
                "create_app ichida kengaytmalarga init_app(app) chaqirish",
                "wsgi.py da app = create_app('development') yozish",
                "flask run yoki python wsgi.py bilan ishga tushirish"],
               diff="Medium", pts=3),
            ti("Nima uchun db = SQLAlchemy(app) yozish factory pattern bilan "
               "muammo tug'diradi?",
               "Factory pattern'da create_app() har chaqirilganda yangi Flask "
               "ilovasi yaratiladi. Agar SQLAlchemy modul darajasida bitta "
               "aniq ilovaga bog'lansa, testlarda yoki ko'p konfiguratsiyali "
               "muhitda bitta SQLAlchemy obyekti bir nechta ilovaga to'g'ri "
               "ishlay olmaydi. Shuning uchun db = SQLAlchemy() ilovasiz "
               "yaratiladi va init_app(app) orqali keyinroq bog'lanadi.",
               hint="Test paytida ikkita alohida ilova kerak bo'lsa-chi?",
               diff="Hard", pts=4),
            mc("create_app() qaysi muhitda chaqiriladi?",
               ["wsgi.py yoki app.py'da bir marta",
                "Har HTTP so'rovda yangidan",
                "Har 30 daqiqada avtomatik",
                "Faqat ilova yopilganda"],
               "A",
               hint="Bu Flask ilovasini yaratish — bir martalik amal.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 1, "title": "2-Blueprint bilan modul tuzilish",
        "text": L2_TEXT, "code": L2_CODE, "lang": "python",
        "video": "https://youtu.be/3PFQ_w59Eaw",
        "exercises": [
            mc("Blueprint Flask'da nimaga xizmat qiladi?",
               ["Ma'lumotlar bazasi modellarini yaratish uchun",
                "Route'lar va shablonlarni guruhlab modullarga ajratish uchun",
                "Ilovani tezlashtirish uchun",
                "HTML kod yaratish uchun"],
               "B",
               hint="100 ta route ni bitta faylda saqlash o'rniga nima qilish "
                    "kerak?",
               explanation="Blueprint route'lar va shablonlarni mantiqiy "
                           "modullarga ajratish va ularni create_app ichida "
                           "ilovaga ulash imkonini beradi.",
               diff="Easy", pts=2),
            mc("Blueprint yaratishda url_prefix='/notes' nimaga ta'sir "
               "qiladi?",
               ["Shu Blueprint'ning barcha route'lariga /notes prefiksi "
                "avtomatik qo'shiladi",
                "Faqat bosh sahifa URL'ini o'zgartiradi",
                "Ilovaning ma'lumotlar bazasini /notes papkasiga ko'chiradi",
                "Static fayllar yo'lini o'zgartiradi"],
               "A",
               hint="@notes_bp.route('/<id>') qaysi URL ga bog'lanadi?",
               diff="Easy", pts=2),
            mc("url_for ni Blueprint route'i uchun to'g'ri ishlatish "
               "usullarini tanlang",
               ["url_for('notes.list_notes')",
                "url_for('notes.show_note', id=42)",
                "url_for('list_notes')",
                "url_for('/notes')"],
               "A,B", multi=True,
               hint="Blueprint nomi va funksiya nomi nuqta bilan ajratiladi.",
               explanation="Blueprint route uchun url_for "
                           "'<blueprint_nomi>.<funksiya_nomi>' formatini "
                           "talab qiladi.",
               diff="Medium", pts=3),
            dd("Yangi Blueprint qo'shish bosqichlarini to'g'ri tartibda "
               "joylang",
               ["Blueprint uchun papka yaratish: app/notes/",
                "app/notes/__init__.py da notes_bp = Blueprint(...) yozish",
                "app/notes/routes.py da @notes_bp.route(...) bilan funksiyalar",
                "app/notes/__init__.py oxirida from . import routes",
                "app/__init__.py da app.register_blueprint(notes_bp) chaqirish"],
               diff="Medium", pts=3),
            ti("Nima uchun app/notes/__init__.py da 'from . import routes' "
               "qatori notes_bp yaratilgandan KEYIN yoziladi?",
               "Agar from . import routes ni notes_bp yaratilishidan oldin "
               "yozsak, routes.py faylida notes_bp hali aniqlanmagan bo'ladi "
               "va aylanma import xatosi (circular import) yuz beradi. "
               "Blueprint avval yaratiladi, keyin routes import qilinib, "
               "u o'sha notes_bp ga route'larni bog'laydi.",
               hint="routes.py faylida notes_bp ishlatiladi — u qachon "
                    "tayyor bo'lishi kerak?",
               diff="Hard", pts=4),
            mc("Blueprint o'z templates papkasini ham olib yurishi uchun "
               "qanday parametr ishlatiladi?",
               ["template_folder='templates' Blueprint konstruktoriga",
                "@app.template_folder dekoratori",
                "config.py da TEMPLATE_FOLDER",
                "Flask buni avtomatik aniqlaydi"],
               "A",
               hint="Blueprint(...) chaqiruvida qo'shimcha keyword argument bor.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 2, "title": "3-Flask-SQLAlchemy bilan ishlash",
        "text": L3_TEXT, "code": L3_CODE, "lang": "python",
        "video": "https://youtu.be/cYWiDiIUxQc",
        "exercises": [
            mc("Flask-SQLAlchemy nima?",
               ["Flask uchun frontend kutubxonasi",
                "Flask uchun ORM — Python obyektlari orqali baza bilan ishlash",
                "Flask'ning yangi versiyasi",
                "Faqat PostgreSQL bilan ishlaydigan kutubxona"],
               "B",
               hint="ORM nima qiladi?",
               explanation="Flask-SQLAlchemy SQL so'rovlarini Python "
                           "obyektlari ortida yashiradi va har xil bazalar "
                           "(SQLite, Postgres, MySQL) bilan bir xil ishlaydi.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysi biri YANGI obyektni bazaga yozadi?",
               ["db.session.add(obj)  — yetarli",
                "db.session.commit()  — yetarli",
                "db.session.add(obj) + db.session.commit()",
                "Note(title='X')  yaratishning o'zi yetarli"],
               "C",
               hint="add() o'zgarishni navbatga qo'yadi, commit() yozadi.",
               explanation="add() faqat sessiya navbatiga qo'shadi. "
                           "Haqiqiy yozish commit() chaqirilganda bo'ladi.",
               diff="Medium", pts=3),
            mc("ID bo'yicha bitta yozuvni olish uchun qaysilar to'g'ri?",
               ["Note.query.get(5)",
                "db.session.get(Note, 5)",
                "Note.find(5)",
                "Note.query.filter_by(id=5).first()"],
               "A,B,D", multi=True,
               hint="Uch xil to'g'ri usul bor. .find() Flask-SQLAlchemy'da yo'q.",
               diff="Medium", pts=3),
            dd("CRUD operatsiyasini bajarish bosqichlarini to'g'ri tartibda "
               "joylang (yangilash holati)",
               ["Note.query.get(id) bilan obyektni olish",
                "obj.title = 'yangi nom' bilan attributni o'zgartirish",
                "db.session.commit() bilan saqlash",
                "Brauzerda /notes/<id> ni ochib tekshirish"],
               diff="Medium", pts=3),
            ti("Nima uchun commit muvaffaqiyatsiz bo'lganda "
               "db.session.rollback() chaqirish kerak?",
               "SQLAlchemy session — bu bir nechta o'zgarishni birlashtiruvchi "
               "transaksiya. Commit xato bo'lsa, sessiya buzilgan holatda "
               "qoladi va keyingi har qanday so'rov ham xato beradi. "
               "rollback() sessiyani toza holatga qaytaradi, shundan keyin "
               "yangi o'zgarishlarni ishlay olamiz.",
               hint="Sessiya commit xatosidan keyin qanday holatda qoladi?",
               diff="Hard", pts=4),
            mc("SQLALCHEMY_TRACK_MODIFICATIONS = False sozlamasi nima uchun "
               "kerak?",
               ["Bazani tezroq qiladi va ortiqcha ogohlantirishni o'chiradi",
                "Sessiyani butunlay o'chiradi",
                "Baza bilan ulanishni to'xtatadi",
                "Faqat SQLite uchun majburiy"],
               "A",
               hint="Bu Flask-SQLAlchemy'ning eski signal mexanizmi.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 3, "title": "4-Modellar orasidagi munosabatlar",
        "text": L4_TEXT, "code": L4_CODE, "lang": "python",
        "video": "https://youtu.be/juPQ04_twtA",
        "exercises": [
            mc("One-to-many munosabatda ForeignKey qaysi tomonga qo'yiladi?",
               ["«Bir» tomonga (User)",
                "«Ko'p» tomonga (Note)",
                "Ikkala tomonga ham",
                "Hech qaysisiga — relationship() o'zi hal qiladi"],
               "B",
               hint="ForeignKey har doim «kim kimga tegishli» degan tomonda turadi.",
               explanation="Har Note bitta User'ga tegishli, shuning uchun "
                           "user_id ustuni Note jadvalida bo'ladi.",
               diff="Easy", pts=2),
            mc("cascade='all, delete-orphan' nima qiladi?",
               ["Hech narsa — faqat hujjat",
                "Ota obyekt o'chirilganda barcha bola obyektlar ham o'chiriladi",
                "Bola obyektlar avtomatik klonlanadi",
                "Bazaga ulanishni o'chiradi"],
               "B",
               hint="User o'chirilganda uning notalari nima bo'lishi kerak?",
               diff="Medium", pts=3),
            mc("Many-to-many uchun nima kerak?",
               ["Oraliq jadval (db.Table bilan)",
                "secondary=<oraliq_jadval> relationship parametri",
                "Ikkala model uchun ForeignKey ustunlari",
                "Faqat backref — boshqa hech narsa"],
               "A,B", multi=True,
               hint="Ikki haqiqiy talab bor.",
               explanation="Many-to-many uchun: (1) oraliq jadval — odatda "
                           "db.Table bilan, (2) bir tomonda relationship "
                           "secondary=<oraliq_jadval> bilan.",
               diff="Medium", pts=3),
            dd("User va Note bog'lanishini yaratish bosqichlarini to'g'ri "
               "tartibda joylang",
               ["Note ga user_id = db.Column(..., db.ForeignKey('users.id'))",
                "Note ga user = db.relationship('User', back_populates='notes')",
                "User ga notes = db.relationship('Note', back_populates='user')",
                "User ga cascade='all, delete-orphan' qo'shish",
                "flask db migrate + flask db upgrade bilan migration"],
               diff="Medium", pts=3),
            ti("back_populates va backref orasidagi farq nima va qaysi "
               "biri tavsiya etiladi?",
               "backref bir tomonda relationship yozsangiz, ikkinchi tomonga "
               "avtomatik atribut qo'shiladi — qisqa, lekin yashirin. "
               "back_populates esa har ikki tomonda relationship'ni qo'lda "
               "yozasiz va ular bir-biriga back_populates orqali ko'rsatadi — "
               "kod uzunroq, lekin aniq va o'qishga oson. Yangi loyihalar "
               "uchun back_populates tavsiya etiladi (aniqligi tufayli).",
               hint="Qaysi biri kodni o'qishga osonroq?",
               diff="Hard", pts=4),
            mc("user.notes attributi qachon mavjud bo'ladi?",
               ["Faqat db.session.add(user) chaqirilgandan keyin",
                "User klassiga notes = db.relationship('Note', ...) yozilganda",
                "Flask shell ichida qo'lda yaratilganda",
                "Hech qachon — har safar query qilish kerak"],
               "B",
               hint="relationship() bir tomonga qo'yilganda nima sodir bo'ladi?",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 4, "title": "5-So'rovlar, filterlar, sahifalash",
        "text": L5_TEXT, "code": L5_CODE, "lang": "python",
        "video": "https://youtu.be/D8RoeOmIQqQ",
        "exercises": [
            mc("filter_by va filter o'rtasidagi asosiy farq nima?",
               ["Yo'q — bir xil narsa",
                "filter_by faqat tenglikni tekshiradi va keyword argument oladi; "
                "filter to'liq ifoda qabul qiladi",
                "filter_by faqat birinchi natijani qaytaradi",
                "filter SQL string yozishni talab qiladi"],
               "B",
               hint="filter_by(user_id=1) va filter(Note.user_id == 1) — qaysi "
                    "biri kuchliroq?",
               diff="Easy", pts=2),
            mc("Case-insensitive qidiruv uchun qaysi metod ishlatiladi?",
               ["Note.title.like('%flask%')",
                "Note.title.ilike('%flask%')",
                "Note.title.match('%flask%')",
                "Note.title.contains('flask', ignore_case=True)"],
               "B",
               hint="LIKE va ILIKE — birida 'I' bor (insensitive).",
               diff="Easy", pts=2),
            mc("paginate() metodi haqida to'g'ri javoblar",
               ["page va per_page parametrlari oladi",
                "Pagination obyektini qaytaradi (items, has_prev, has_next va "
                "boshqalar bilan)",
                "error_out=False yo'q sahifaga 404 o'rniga bo'sh natija qaytaradi",
                "Faqat SQLite'da ishlaydi"],
               "A,B,C", multi=True,
               hint="3 ta to'g'ri, 1 noto'g'ri.",
               diff="Medium", pts=3),
            dd("N+1 muammosini hal qilish bosqichlarini to'g'ri tartibda "
               "joylang",
               ["Sahifada 100 ta nota ko'rsatildi va har birida note.user.username chaqirildi",
                "Profayl yoki SQL logini ochib 101 ta so'rov ko'rilgani aniqlandi",
                "Query'ga options(joinedload(Note.user)) qo'shildi",
                "Endi bitta SQL JOIN bilan barcha foydalanuvchi ma'lumotlari kelyapti",
                "Sahifa tezligi sezilarli yaxshilandi"],
               diff="Hard", pts=4),
            ti("Nima uchun katta jadvallarda .all() o'rniga .paginate() "
               "yoki .limit() ishlatish kerak?",
               ".all() jadvaldagi barcha satrlarni xotiraga yuklaydi. Agar "
               "jadvalda 100 ming yozuv bo'lsa, server xotirasi tugaydi yoki "
               "sahifa juda sekin yuklanadi. paginate(per_page=20) yoki "
               "limit(20) faqat kerakli qismni oladi va xotirani saqlaydi, "
               "shuningdek SQL darajasida LIMIT/OFFSET bilan tezroq ishlaydi.",
               hint="100 ming yozuvni RAM ga yuklasa nima bo'ladi?",
               diff="Hard", pts=4),
            mc("OR mantiqi bilan filtr yozish uchun qaysi import kerak?",
               ["from sqlalchemy import or_",
                "from flask import or_",
                "OR_ — built-in operator",
                "Hech narsa — | operatori avtomatik ishlaydi"],
               "A",
               hint="OR uchun maxsus funksiya bor — qaysi modulda?",
               explanation="from sqlalchemy import or_ — uni filter() ichida "
                           "or_(cond1, cond2) tarzda ishlatamiz. | operatori "
                           "ham ishlaydi lekin or_ aniqroq.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 5, "title": "6-Flask-Migrate va Alembic",
        "text": L6_TEXT, "code": L6_CODE, "lang": "python",
        "video": "https://youtu.be/wpRrmig7eMc",
        "exercises": [
            mc("Flask-Migrate'ning asosiy maqsadi nima?",
               ["Ma'lumotlar bazasini tezlashtirish",
                "Sxema o'zgarishlarini versiya-versiya saqlash va xavfsiz qo'llash",
                "SQL so'rovlarni avtomatik yozish",
                "Bazani vaqti-vaqti bilan tozalash"],
               "B",
               hint="db.create_all() ni nima bilan almashtirilyapti?",
               diff="Easy", pts=2),
            mc("db.create_all() va flask db migrate o'rtasidagi farq?",
               ["create_all() faqat YANGI jadvallarni qo'shadi, mavjudini "
                "o'zgartirmaydi",
                "db migrate har o'zgarishni alohida versiya fayl sifatida "
                "saqlaydi",
                "create_all() production'da xavfsiz",
                "db migrate avtomatik ravishda har deploy'da chaqiriladi"],
               "A,B", multi=True,
               hint="Asosiy farq — sxema o'zgarishi.",
               diff="Medium", pts=3),
            mc("Avtomatik migration har doim to'g'ri bo'ladimi?",
               ["Ha, har doim",
                "Yo'q — masalan ustun nomini o'zgartirsangiz Alembic uni "
                "DROP+ADD deb tushunadi va ma'lumot yo'qoladi",
                "Faqat PostgreSQL'da to'g'ri",
                "Yo'q — Alembic faqat jadval qo'shishni biladi"],
               "B",
               hint="Rename column → Alembic uni qanday talqin qiladi?",
               diff="Medium", pts=3),
            dd("Birinchi marta Flask-Migrate sozlash bosqichlarini to'g'ri "
               "tartibda joylang",
               ["pip install Flask-Migrate",
                "create_app ichida migrate = Migrate() va migrate.init_app(app, db)",
                "from app import models  # noqa: F401  qatorini qo'shish",
                "$ export FLASK_APP=wsgi.py",
                "$ flask db init",
                "$ flask db migrate -m \"initial tables\"",
                "$ flask db upgrade"],
               diff="Hard", pts=4),
            ti("Nima uchun create_app() ichida 'from app import models' "
               "qatori muhim?",
               "Alembic migrationni yaratishda hozir SQLAlchemy metadata'da "
               "ro'yxatga olingan modellarni baza bilan solishtiradi. Agar "
               "modellar import qilinmagan bo'lsa, SQLAlchemy ularni "
               "ko'rmaydi, metadata bo'sh bo'ladi va migration ham bo'sh "
               "chiqadi (yoki noto'g'ri — mavjud jadvallarni o'chirishga "
               "harakat qiladi). Shuning uchun create_app oxirida modellarni "
               "import qilamiz.",
               hint="Alembic modellarni qaerdan «biladi»?",
               diff="Hard", pts=4),
            mc("Quyidagi komandalardan qaysilari foydali holatlar?",
               ["flask db current — hozirgi migration versiyasini ko'rsatadi",
                "flask db history — barcha migration ketma-ketligi",
                "flask db downgrade — bir qadam orqaga qaytadi",
                "flask db delete — barcha migrationlarni o'chiradi"],
               "A,B,C", multi=True,
               hint="«delete» komandasi yo'q.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 6, "title": "R1-Yo'qolgan narsalar (Lost & Found takrori)",
        "text": R1_TEXT, "code": R1_CODE, "lang": "python",
        "video": "https://youtu.be/eBwjUv8e2fA",
        "exercises": [
            mc("Application Factory + Blueprint + SQLAlchemy birga ishlashda "
               "kengaytmalar (db, migrate) qaerda yaratiladi?",
               ["create_app() ichida har safar yangidan",
                "Modul darajasida (db = SQLAlchemy()), so'ng create_app ichida "
                "init_app(app)",
                "config.py da",
                "wsgi.py da"],
               "B",
               hint="Modul darajasida bir marta — keyin init_app bilan ilovaga "
                    "bog'lanadi.",
               diff="Easy", pts=2),
            mc("Yo'qolgan narsalar ilovasida kategoriya (telefon, kalit va "
               "boshqalar) qaysi munosabatda yaxshiroq?",
               ["One-to-many (Item.category)",
                "Many-to-many (Item.tags) — bir item bir necha tag olishi mumkin",
                "Hech qanday relationship — alohida ustun yetarli",
                "Self-referential (Item.parent)"],
               "B",
               hint="Bir telefon ham «elektron» ham «yangi» tag olishi mumkin?",
               diff="Medium", pts=3),
            mc("Paginatsiya bilan qidiruv birga ishlaganda qaysi xato eng ko'p "
               "uchraydi?",
               ["Qidiruv natijasini paginate qilishni unutib, hammasini "
                "ko'rsatish",
                "?page=N argumentini ?q=... ga qo'shib (yoki teskari) "
                "url_for'da yo'qotib qo'yish",
                "Qidiruv har safar joinedload chaqirib sekinlashishi",
                "Hammasi to'g'ri ishlashidan tashqari hech narsa"],
               "A,B", multi=True,
               hint="UX nuqtai nazaridan — qidiruv natijasi 100 ta bo'lsa "
                    "nima qilamiz?",
               diff="Medium", pts=3),
            dd("Yo'qolgan narsalar loyihasini boshlash bosqichlarini to'g'ri "
               "tartibda joylang",
               ["Project papka tuzilishini yaratish (app/, config.py, wsgi.py)",
                "config.py da Config klasslarni yozish",
                "app/__init__.py da create_app + db + migrate",
                "app/models.py da User, Item, Tag, item_tags",
                "flask db init va birinchi migration",
                "Blueprint'lar va route'larni yozish",
                "Templates yozish va URL'larni url_for bilan bog'lash"],
               diff="Hard", pts=4),
            ti("Nima uchun yangi e'lon qo'shish formasi paginatsiyali "
               "sahifadan alohida route'da bo'lishi yaxshi?",
               "Bosh sahifa GET bilan ro'yxatni ko'rsatadi — bu kesh'lanishi "
               "mumkin, brauzer back tugmasi bilan oson qaytariladi. POST "
               "esa ma'lumot o'zgartiradi va PRG (POST → Redirect → GET) "
               "patternga muhtoj. Ikkalasini alohida route'larda saqlash "
               "har birining vazifasini aniq qiladi va F5 (refresh) bilan "
               "ikki marta yuborishni oldini oladi.",
               hint="POST ni qayta yuborish nima muammo tug'diradi?",
               diff="Hard", pts=4),
            mc("Item modeliga «kategoriya» (telefon/kalit/...) qo'shgandan "
               "keyin Alembic migration to'g'ri ishlashi uchun nima qilish "
               "kerak?",
               ["Hech narsa — Alembic o'zi topadi",
                "create_app() ichida 'from app import models' import qilish + "
                "flask db migrate -m \"add category\" + flask db upgrade",
                "Bazani qo'lda ALTER TABLE bilan o'zgartirish",
                "db.create_all() qayta chaqirish"],
               "B",
               hint="Avval modellar import qilingani kerak.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 7, "title": "7-Parol hashing (werkzeug.security)",
        "text": L7_TEXT, "code": L7_CODE, "lang": "python",
        "video": "https://youtu.be/CSHx6eCkmv0",
        "exercises": [
            mc("Nima uchun parolni bevosita bazaga saqlash xavfli?",
               ["Faqat sekin ishlaydi",
                "Baza buzilsa yoki SELECT * qilinsa, barcha parollar oshkor "
                "bo'ladi",
                "SQL syntax bilan to'qnashadi",
                "Hech qanday xavfli emas"],
               "B",
               hint="Ma'lumotlar bazasi har doim ham xavfsiz emas — "
                    "agar leak bo'lsa nima bo'ladi?",
               diff="Easy", pts=2),
            mc("Hash funksiyasi haqida to'g'ri javoblar",
               ["Bir xil kirish doim bir xil hash beradi",
                "Hashdan asl matnni tiklab bo'lmaydi (one-way)",
                "Salt har parol uchun tasodifiy bo'ladi",
                "Hash MD5 dan farq qilmasdan ishlatilishi kerak"],
               "A,B,C", multi=True,
               hint="3 ta to'g'ri javob — MD5 endi xavfsiz emas.",
               diff="Medium", pts=3),
            mc("Salt nimaga xizmat qiladi?",
               ["Bir xil parolli ikki foydalanuvchining hashlari turlicha "
                "chiqishini ta'minlaydi",
                "Hashni tezroq qiladi",
                "Parolni eslab qolishga yordam beradi",
                "Bazaga ulanishni shifrlash uchun"],
               "A",
               hint="Saltsiz: agar ikki userda parol 'qwerty' bo'lsa "
                    "hashlari qanday bo'ladi?",
               explanation="Salt — har parol uchun tasodifiy qo'shimcha. "
                           "U bilan hash hatto bir xil parol uchun har "
                           "safar boshqacha chiqadi.",
               diff="Medium", pts=3),
            dd("Werkzeug bilan parolni saqlash va tekshirish bosqichlarini "
               "to'g'ri tartibda joylang",
               ["pip install Flask (werkzeug bilan keladi)",
                "from werkzeug.security import generate_password_hash, "
                "check_password_hash",
                "User.password_hash = generate_password_hash(raw) — saqlash",
                "Login paytida check_password_hash(user.password_hash, raw) — "
                "tekshirish",
                "True qaytsa — login muvaffaqiyatli"],
               diff="Medium", pts=3),
            ti("Nima uchun password_hash ustun uzunligi 255 belgi qilib "
               "qo'yiladi (60 yoki 80 emas)?",
               "Werkzeug yoki bcrypt hashlari turli formatlarda chiqadi: "
               "pbkdf2-sha256 ~100 belgi, bcrypt 60 belgi, scrypt yanada "
               "uzun. Algoritm o'zgarsa yoki iteratsiya soni oshirilsa, "
               "hash uzunligi ham o'zgarishi mumkin. 255 — keng zaxira "
               "bilan qulay miqdor (ko'pchilik baza String ustun uchun "
               "indeksiy chegara). 60 ga cheklasangiz, kelajakda algoritm "
               "o'zgarsa migration kerak bo'ladi.",
               hint="Kelajakda algoritm o'zgarsa nima bo'ladi?",
               diff="Hard", pts=4),
            mc("Ro'yxatdan o'tish validatsiyasi uchun minimal qoidalar?",
               ["Parol kamida 8 belgi",
                "Username/email bo'sh emas (strip qilinadi)",
                "Username/email bazada mavjud emasligini tekshirish (unique)",
                "Parol uzunligi har doim 128 belgi"],
               "A,B,C", multi=True,
               hint="3 ta to'g'ri javob, 1 ta noto'g'ri (parol qattiq "
                    "uzunlik talab qilmaydi).",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 8, "title": "8-Flask-Login bilan autentifikatsiya",
        "text": L8_TEXT, "code": L8_CODE, "lang": "python",
        "video": "https://youtu.be/8aTnmsDMldY",
        "exercises": [
            mc("UserMixin nima beradi?",
               ["Flask-Login talab qiladigan 4 ta atributni avtomatik "
                "(is_authenticated, is_active, is_anonymous, get_id)",
                "Ma'lumotlar bazasiga ulanish",
                "JSON serializatsiya",
                "Avtomatik parol hashing"],
               "A",
               hint="Flask-Login User klassidan nimani talab qiladi?",
               diff="Easy", pts=2),
            mc("user_loader callback qachon chaqiriladi?",
               ["Har HTTP so'rovda (sessiyada user_id bo'lsa)",
                "Faqat login paytida",
                "Faqat logout paytida",
                "Hech qachon — manual chaqirish kerak"],
               "A",
               hint="current_user qaerdan keladi?",
               diff="Medium", pts=3),
            mc("Quyidagilardan qaysilari Flask-Login imkoniyatlari?",
               ["login_user(user) — sessiyaga foydalanuvchini yozish",
                "logout_user() — sessiyadan o'chirish",
                "@login_required — sahifani himoyalash",
                "@admin_required — built-in admin himoyasi"],
               "A,B,C", multi=True,
               hint="3 ta built-in, 1 tasi yo'q (uni o'zimiz yozamiz).",
               diff="Medium", pts=3),
            dd("Foydalanuvchi /notes/new ga kirmoqchi (login bo'lmagan) "
               "holatda voqealar tartibini joylang",
               ["Foydalanuvchi /notes/new URL ga kiradi",
                "@login_required dekorator current_user.is_authenticated False "
                "ekanini ko'radi",
                "Flask-Login uni /auth/login?next=/notes/new ga yo'naltiradi",
                "Foydalanuvchi login formani to'ldiradi va POST yuboradi",
                "login_user(user) chaqirilgandan keyin request.args.get('next') "
                "olinadi",
                "Foydalanuvchi asl /notes/new sahifasiga qaytariladi"],
               diff="Hard", pts=4),
            ti("login_view = 'auth.login' sozlamasi nima uchun muhim?",
               "@login_required dekorator kirmagan foydalanuvchini qaerga "
               "yo'naltirishni bilishi kerak. login_view shu manzilni "
               "ko'rsatadi. Aks holda Flask-Login standart 401 javobini "
               "qaytaradi — bu UX uchun yomon. login_view bilan esa "
               "avtomatik chiroyli redirect bo'ladi.",
               hint="kirmagan foydalanuvchi himoyalangan sahifaga kirsa "
                    "qaerga yo'naltiriladi?",
               diff="Hard", pts=4),
            mc("remember=True parametri nima qiladi?",
               ["Brauzer yopilgandan keyin ham foydalanuvchini eslab qoladi "
                "(uzoq muddatli cookie)",
                "Faqat bir kun eslaydi",
                "Parolni eslaydi",
                "Hech narsa qilmaydi"],
               "A",
               hint="«Remember me» checkbox nima uchun?",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 9, "title": "9-Roli va kirish nazorati (RBAC)",
        "text": L9_TEXT, "code": L9_CODE, "lang": "python",
        "video": "https://youtu.be/eN-DXNbVQB8",
        "exercises": [
            mc("401 Unauthorized va 403 Forbidden o'rtasidagi farq nima?",
               ["Yo'q — bir xil narsa",
                "401: kim ekanligingiz noma'lum (login kerak). "
                "403: kim ekanligingizni bilamiz, lekin ruxsat yo'q",
                "401: server xato. 403: client xato",
                "401: redirect uchun. 403: yo'q"],
               "B",
               hint="«Login qiling» va «Sizga ruxsat yo'q» — qaysi qaysi?",
               diff="Easy", pts=2),
            mc("«Faqat ega o'z notasini tahrirlaydi» qoidasini qaerda "
               "tekshirish kerak?",
               ["Faqat shablonda (tugmani yashirish bilan)",
                "Faqat server tomonida (URL qo'lda yozish mumkin)",
                "Server tomonida MAJBURIY + shablonda UX uchun yashirish",
                "Hech qaerda — Flask o'zi tekshiradi"],
               "C",
               hint="Foydalanuvchi /notes/5/edit URL ni qo'lda yozsa nima "
                    "bo'ladi?",
               explanation="Shablonda yashirish faqat UX uchun. Server "
                           "tomonida tekshirish majburiy — aks holda har "
                           "kim har kimning resurslariga o'zgartirish "
                           "kirita oladi (broken object level authorization).",
               diff="Medium", pts=3),
            mc("admin_required dekoratori yozish uchun nimalar kerak?",
               ["functools.wraps — orig funksiya metadata saqlanishi uchun",
                "current_user.is_authenticated tekshiruvi",
                "current_user.is_admin() tekshiruvi",
                "abort(401) yoki abort(403)"],
               "A,B,C,D", multi=True,
               hint="To'rttala kerak.",
               diff="Hard", pts=4),
            dd("Object-level authorization tekshiruvini to'g'ri tartibda "
               "joylang (notani tahrirlash)",
               ["@login_required dekorator (umumiy login tekshiruvi)",
                "Notani db.session.get(Note, id) bilan olish",
                "Topilmagan bo'lsa abort(404)",
                "current_user obyektga ega ekanligini tekshirish "
                "(note.user_id == current_user.id) yoki admin ekanligini",
                "Tekshiruv o'tmasa abort(403)",
                "Edit logikasini bajarish"],
               diff="Hard", pts=4),
            ti("«Broken object level authorization» nima va u qanday yuz "
               "beradi?",
               "Bu eng keng tarqalgan veb xavfsizlik xatolaridan biri "
               "(OWASP Top 10). Foydalanuvchi o'z resurslariga ega — masalan "
               "/notes/5 ni tahrirlay oladi. Lekin u URL ni qo'lda /notes/6 "
               "ga o'zgartiradi va boshqa odamning notasini tahrirlay oladi, "
               "chunki server faqat «login bormi» deb tekshirgan, «bu "
               "nota egasimi» deb tekshirmagan. Yechim: har resurs uchun "
               "obyekt darajasidagi tekshiruv (note.user_id == current_user.id "
               "yoki current_user.is_admin()).",
               hint="Foydalanuvchi URL'ni qo'lda o'zgartirsa nima bo'ladi?",
               diff="Hard", pts=4),
            mc("Shablonda is_admin tekshiruvi qachon foydali?",
               ["Adminga maxsus tugma/link ko'rsatish uchun (UX)",
                "Server tomonidagi tekshiruvni almashtirish uchun",
                "Bazaga yozish uchun",
                "Hech qachon"],
               "A",
               hint="Faqat ko'rsatish — yoki himoyalash?",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 10, "title": "R2-Ko'p foydalanuvchili blog (takrorlash)",
        "text": R2_TEXT, "code": R2_CODE, "lang": "python",
        "video": "https://youtu.be/8aTnmsDMldY",
        "exercises": [
            mc("Modul 3 dagi 3 ta darsdan qaysi biri server tomonida "
               "MAJBURIY tekshirilishi kerak?",
               ["Faqat L7 (hashing)",
                "Faqat L9 (rollar)",
                "Hammasi: hashing bilan login, login_required va "
                "obyekt darajasidagi tekshiruv ham server tomonida",
                "Hech qaysisi"],
               "C",
               hint="Mijoz tomonidagi har qanday tekshiruv buzilishi mumkin.",
               diff="Easy", pts=2),
            mc("Quyidagilardan qaysilari yangi blog loyihasi uchun zarur "
               "sxema?",
               ["users.password_hash (String 255, NOT NULL)",
                "users.role (String 20, default 'user')",
                "posts.user_id ForeignKey('users.id')",
                "posts.plain_password — har post uchun parol"],
               "A,B,C", multi=True,
               hint="3 ta to'g'ri, 1 ta noto'g'ri (har post uchun parol "
                    "nima uchun kerak?)",
               diff="Medium", pts=3),
            mc("Birinchi admin foydalanuvchini qanday yaratasiz?",
               ["/auth/register dan o'tib, keyin Flask shell orqali "
                "u.role = 'admin' qilib commit",
                "Hech qachon — admin yo'q",
                "Bazani qo'lda SQL bilan",
                "Hech kim admin bo'la olmaydi"],
               "A",
               hint="Birinchi admin uchun maxsus UI yo'q — qo'lda shell "
                    "orqali.",
               diff="Easy", pts=2),
            dd("Yangi post yaratish to'liq voqealar tartibini joylang "
               "(ega-tekshiruvli)",
               ["Foydalanuvchi /posts/new sahifasiga GET bilan kiradi",
                "@login_required tekshiradi — login bo'lmasa /auth/login ga",
                "Forma to'ldiriladi va POST yuboriladi",
                "Post(title=..., body=..., user_id=current_user.id) yaratiladi",
                "db.session.add + commit",
                "flash xabar + redirect /posts/<new_id>"],
               diff="Hard", pts=4),
            ti("Nima uchun «remember me» checkbox loginda muhim, lekin "
               "uni standart yoqilgan qilib qo'yish yomon?",
               "remember me brauzer yopilgandan keyin ham foydalanuvchini "
               "eslab qoladi — bu uzoq muddatli cookie orqali ishlaydi. "
               "Bu UX uchun qulay (har safar login qilish kerak emas), "
               "lekin xavfsizlik kompromis: agar foydalanuvchi umumiy "
               "kompyuterda ishlasa va remember me ni yoqib qoldirsa, "
               "kompyuterga boshqa odam o'tirsa uning hisobiga kira oladi. "
               "Shuning uchun checkbox foydalanuvchining aniq tanlovi "
               "bo'lishi kerak — standart o'chirilgan.",
               hint="Umumiy kompyuter foydalanuvchisi uchun bu nima xavf?",
               diff="Hard", pts=4),
            mc("Login formasida username va email ni bir maydonda qabul "
               "qilish uchun qaysi SQL operatori kerak?",
               ["AND",
                "OR (yoki SQLAlchemy'da | operatori, yoki or_)",
                "JOIN",
                "WHERE EXISTS"],
               "B",
               hint="Foydalanuvchi username ham, email ham yozishi mumkin.",
               explanation="User.username == identifier OR User.email == "
                           "identifier — ikki shartdan biri true bo'lsa "
                           "yetadi.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 11, "title": "10-Flask-WTF: formalar va CSRF",
        "text": L10_TEXT, "code": L10_CODE, "lang": "python",
        "video": "https://youtu.be/UIJKdCIEXUQ",
        "exercises": [
            mc("Flask-WTF nima beradi?",
               ["Formani Python klass sifatida tasvirlash, validatorlar va "
                "avtomatik CSRF himoyasi",
                "Faqat HTML render qilish",
                "Faqat ma'lumotlar bazasi",
                "JavaScript validatsiya"],
               "A",
               hint="Klass + validatorlar + CSRF — uchchasi birga.",
               diff="Easy", pts=2),
            mc("CSRF hujum nima va token uni qanday to'xtatadi?",
               ["CSRF: foydalanuvchining sessiyasidan foydalanib uning nomidan "
                "so'rov yuborish. Token: hujumchi bila olmaydigan tasodifiy "
                "satr formaga qo'shiladi va serverda tekshiriladi",
                "CSRF: brute-force parol urinishi",
                "CSRF: SQL injection turi",
                "CSRF: faqat GET so'rovlar uchun muammo"],
               "A",
               hint="Hujumchining sayti sizning bank cookie'ngiz bilan POST "
                    "yubora oladimi?",
               diff="Medium", pts=3),
            mc("validate_on_submit() metodi nima qiladi?",
               ["So'rov POST bo'lsa va barcha validatorlar o'tgan bo'lsa True",
                "Faqat POST bo'lsa True",
                "Faqat validatorlar o'tgan bo'lsa True",
                "Hech narsa qaytarmaydi"],
               "A",
               hint="Ikki shart birga.",
               diff="Easy", pts=2),
            dd("Yangi Flask-WTF formani yaratish bosqichlarini to'g'ri "
               "tartibda joylang",
               ["pip install Flask-WTF email-validator",
                "Form klassini yaratish (FlaskForm meros)",
                "Maydonlar va validatorlarni e'lon qilish",
                "Route ichida form = MyForm() yaratish",
                "if form.validate_on_submit() tekshirish",
                "Shablonda {{ form.hidden_tag() }} (CSRF) va maydonlar"],
               diff="Medium", pts=3),
            ti("Maxsus validator (masalan, validate_username) qachon "
               "chaqiriladi va u boshqa validatorlardan keyin ishlaydimi?",
               "Form klassi ichidagi validate_<field_name> metodlari WTForms "
               "tomonidan avtomatik chaqiriladi — har dala uchun barcha "
               "validators ro'yxati o'tgandan keyin (DataRequired, Length "
               "va boshqalar). Agar field-level validatorlardan birortasi "
               "xato bersa, validate_<field> umuman chaqirilmaydi. "
               "ValidationError ko'tarsa, xato form.<field>.errors ro'yxatiga "
               "qo'shiladi va shablonda ko'rsatiladi.",
               hint="Validators ro'yxati va validate_<field> metodi qaysi "
                    "tartibda ishlaydi?",
               diff="Hard", pts=4),
            mc("GET formasiga (masalan, qidiruv) CSRF kerakmi?",
               ["Ha, har formaga kerak",
                "Yo'q — GET state'ni o'zgartirmaydi. csrf = False bilan o'chiriladi",
                "Hech qachon kerak emas",
                "Faqat Flask-WTF ishlatmaganda kerak"],
               "B",
               hint="GET so'rovi nima qiladi?",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 12, "title": "11-Fayl yuklash (xavfsiz upload)",
        "text": L11_TEXT, "code": L11_CODE, "lang": "python",
        "video": "https://youtu.be/Hu8Q-vTeqxQ",
        "exercises": [
            mc("Nima uchun foydalanuvchi yuborgan fayl nomiga ishonib "
               "bo'lmaydi?",
               ["Nom juda uzun bo'lishi mumkin",
                "Foydalanuvchi maxsus belgilar (../, NUL, control chars) "
                "yuborib disk yo'lini o'zgartirishi mumkin (path traversal)",
                "Faqat ingliz tilida bo'lishi shart",
                "Hech qanday xavf yo'q"],
               "B",
               hint="Foydalanuvchi `../../../etc/passwd` yuborsa nima bo'ladi?",
               diff="Easy", pts=2),
            mc("Fayl yuklash uchun MUHIM xavfsizlik choralari qaysilar?",
               ["secure_filename() bilan nomni tozalash",
                "FileAllowed bilan kengaytma whitelist",
                "MAX_CONTENT_LENGTH bilan o'lcham chegarasi",
                "Fayl mazmunini ham tekshirish (imghdr/magic)"],
               "A,B,C,D", multi=True,
               hint="Hammasi kerak — birorta yetishmasligi xavf.",
               diff="Hard", pts=4),
            mc("HTML formada faylni yuborish uchun enctype qaysi bo'lishi "
               "kerak?",
               ["application/x-www-form-urlencoded (default)",
                "multipart/form-data",
                "text/plain",
                "application/json"],
               "B",
               hint="Default enctype faqat matn yuboradi.",
               explanation="Faylni baytma-bayt yuborish uchun multipart/form-data "
                           "ishlatilishi shart. Bo'lmasa fayl serverga umuman "
                           "yetib kelmaydi.",
               diff="Medium", pts=3),
            dd("Yuklangan rasm faylini xavfsiz saqlash bosqichlarini to'g'ri "
               "tartibda joylang",
               ["form.validate_on_submit() bilan formani tekshirish",
                "imghdr.what bilan ichki tur tekshirish (jpeg/png/...)",
                "secure_filename() bilan nomni tozalash",
                "uuid.uuid4().hex bilan noyob yangi nom yaratish",
                "os.makedirs(UPLOAD_DIR, exist_ok=True)",
                "file.save(path) bilan diskga yozish",
                "Bazaga yangi nomni saqlash (User.avatar = new_name)",
                "redirect + flash bilan profile sahifasiga qaytarish"],
               diff="Hard", pts=4),
            ti("Nima uchun yuklangan fayllarni static/ ichida emas, alohida "
               "uploads/ papkasida saqlash yaxshi?",
               "static/ Flask tomonidan avtomatik xizmat qilinadi va kod "
               "katalogi ichida joylashadi. Yuklangan fayllar foydalanuvchidan "
               "kelgan ishonchsiz mazmun — agar nazoratsiz static ichiga "
               "tushsa, hujumchi nomli HTML/JS fayl yuklab uni sayt domeninda "
               "ishga tushira oladi (XSS). Alohida uploads/ papkasini esa "
               "send_from_directory orqali aniq tekshiruv bilan beramiz. "
               "Bundan tashqari, uploads/ ni .gitignore qilish ham oson — "
               "yuklangan fayllar git tarixiga tushmaydi.",
               hint="Hujumchi nomli evil.html yuklasa nima bo'ladi?",
               diff="Hard", pts=4),
            mc("FileRequired va FileAllowed validatorlari qayerdan import "
               "qilinadi?",
               ["from flask_wtf.file import FileRequired, FileAllowed",
                "from wtforms.validators import FileRequired, FileAllowed",
                "from flask import FileRequired, FileAllowed",
                "Built-in — import kerak emas"],
               "A",
               hint="Fayl-maxsus validatorlar Flask-WTF'ning file modulida.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 13, "title": "12-REST API: to'g'ri HTTP va JSON xatolar",
        "text": L12_TEXT, "code": L12_CODE, "lang": "python",
        "video": "https://youtu.be/dwo46k6gIfM",
        "exercises": [
            mc("POST /api/notes muvaffaqiyatli yaratganida qaysi status "
               "kod qaytariladi?",
               ["200 OK",
                "201 Created",
                "204 No Content",
                "302 Found"],
               "B",
               hint="«Yaratildi» uchun maxsus kod bor.",
               diff="Easy", pts=2),
            mc("DELETE /api/notes/5 muvaffaqiyatli o'chirganda qaysi javob "
               "qaytariladi?",
               ["200 + o'chirilgan obyekt JSON tana bilan",
                "204 + bo'sh tana",
                "200 + {'deleted': true}",
                "404"],
               "B",
               hint="«Hech narsa qaytarmaydi» uchun maxsus kod.",
               explanation="204 No Content — operatsiya muvaffaqiyatli, lekin "
                           "javob tanasi yo'q. DELETE uchun standart.",
               diff="Medium", pts=3),
            mc("API xato javoblarini standartlash uchun qaysi yondashuv "
               "to'g'ri?",
               ["Har route ichida o'zicha jsonify({'error': ...})",
                "@api_bp.app_errorhandler(404), (400), (500) bilan markaziy",
                "abort(404) — Flask o'zi HTML qaytaradi (yaramaydi)",
                "Hech qanday xato javob — faqat status kod"],
               "B",
               hint="Markazlashtirilgan yondashuv qaysi?",
               diff="Medium", pts=3),
            dd("REST endpoint yaratish bosqichlarini to'g'ri tartibda joylang "
               "(POST /api/notes)",
               ["request.get_json(silent=True) bilan tanasini olish",
                "data is None bo'lsa 400 + {'error': 'JSON required'}",
                "Majburiy maydonlar (title) tekshirish, bo'sh bo'lsa 400",
                "Note obyektni yaratish va db.session.add + commit",
                "jsonify(note_to_dict(note)) javob yaratish",
                "response.status_code = 201",
                "response.headers['Location'] = url_for(...)",
                "response qaytarish"],
               diff="Hard", pts=4),
            ti("request.get_json() va request.get_json(silent=True) "
               "o'rtasidagi farq nima va nima uchun silent=True yaxshi?",
               "request.get_json() (silent=False default) JSON noto'g'ri "
               "yoki Content-Type to'g'ri emas bo'lsa BadRequest exception "
               "ko'taradi va Flask avtomatik 400 HTML javobi qaytaradi. "
               "silent=True esa exception ko'tarmasdan None qaytaradi. "
               "Bu sizga foydali xato xabari shakllantirish imkonini beradi "
               "({'error': 'JSON required'}) va API izchil JSON javoblari "
               "berish kafolatini saqlaydi.",
               hint="Default holatda exception ko'tariladi — bu API uchun "
                    "yomonmi?",
               diff="Hard", pts=4),
            mc("Location header POST javobida nima uchun foydali?",
               ["Yangi yaratilgan resursning URL'ini mijozga ko'rsatadi",
                "Brauzerni redirect qiladi",
                "JavaScript uchun majburiy",
                "Hech qanday foyda yo'q"],
               "A",
               hint="REST standartida 201 Created bilan birga keladigan "
                    "narsa.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 14, "title": "13-API pagination, qidiruv, sort",
        "text": L13_TEXT, "code": L13_CODE, "lang": "python",
        "video": "https://youtu.be/zaO9o3FzBmI",
        "exercises": [
            mc("Nima uchun ?per_page=100000 ni cheksiz qabul qilish yomon?",
               ["Server xotirasi tugaydi yoki javob juda sekin",
                "URL juda uzun bo'ladi",
                "Brauzer URL'larni qabul qilmaydi",
                "Hech qanday muammo yo'q"],
               "A",
               hint="100 ming yozuvni xotiraga yuklasa nima bo'ladi?",
               diff="Easy", pts=2),
            mc("?sort=<ustun> parametrini foydalanuvchidan to'g'ridan-to'g'ri "
               "olish nima uchun xavfli?",
               ["Foydalanuvchi har qanday ustun nomini berishi mumkin — "
                "yopiq yoki noma'lum ustunlar (SQL injection xatosi)",
                "Faqat sekin ishlaydi",
                "Brauzer xato beradi",
                "Hech qanday xavf yo'q"],
               "A",
               hint="?sort=password_hash berilsa-chi?",
               explanation="Foydalanuvchi kiritmasini whitelist'ga qarshi "
                           "tekshirish kerak: SORTABLE = {'created_at', "
                           "'title', 'id'}; sort not in SORTABLE → default.",
               diff="Hard", pts=4),
            mc("API javob meta'sida nima ko'rsatilishi yaxshi?",
               ["page va per_page (hozirgi sahifa)",
                "total (jami yozuvlar soni)",
                "pages (jami sahifalar)",
                "has_next va has_prev"],
               "A,B,C,D", multi=True,
               hint="To'rttala foydali — mijozga navigatsiya uchun.",
               diff="Medium", pts=3),
            dd("/api/notes?q=flask&sort=title&order=asc&page=2&per_page=20 "
               "ni qayta ishlash bosqichlarini to'g'ri tartibda joylang",
               ["request.args dan har bir paramni xavfsiz o'qish (type=int, default)",
                "per_page ni MAX_PER_PAGE bilan cheklash",
                "sort ni SORTABLE whitelist bilan tekshirish",
                "Note.query'dan boshlab filter (q bo'lsa or_ ilike)",
                "order_by(direction(getattr(Note, sort))) qo'shish",
                "paginate(page, per_page, error_out=False) chaqirish",
                "{items, meta, links} JSON javob qaytarish"],
               diff="Hard", pts=4),
            ti("API javobida 'links' bo'limi (next, prev, self) nima uchun "
               "foydali? Faqat 'meta' yetarli emas?",
               "links bo'limi HATEOAS (Hypermedia as the Engine of Application "
               "State) tamoyilining bir qismi — mijozga keyingi qadamlarni "
               "URL ko'rinishida beradi. meta'da page/per_page ko'rsatish "
               "yaxshi, lekin mijoz keyingi sahifa URL'ini o'zi qurib "
               "berishi noqulay (qaysi parametrlarni saqlash kerak, "
               "_external'ni qanday qilish). links tayyor URL beradi — "
               "mijoz uni shunchaki chaqiradi va o'zgarmaydigan API logikasini "
               "saqlaydi.",
               hint="Mijoz keyingi sahifa URL'ini o'zi qursa qanday murakkablik?",
               diff="Hard", pts=4),
            mc("?q=flask&page=2 URL'da q parametri bo'sh bo'lsa nima qilish "
               "kerak?",
               ["Filter umuman qo'llanmaydi — query o'zgarmaydi",
                "Har doim filter qo'llaniladi (bo'sh string ham)",
                "404 qaytariladi",
                "URL noto'g'ri deb 400 qaytariladi"],
               "A",
               hint="if q: filter — qisqartirilgan operator.",
               diff="Easy", pts=2),
        ],
    },
    {
        "order": 15, "title": "14-Flask-Mail va parol tiklash",
        "text": L14_TEXT, "code": L14_CODE, "lang": "python",
        "video": "https://youtu.be/3KFNoTLnvgY",
        "exercises": [
            mc("Email yuborish nima uchun orqa fonda (Thread/Celery) "
               "bajarilishi yaxshi?",
               ["SMTP serveriga ulanish 2-5 soniya oladi va foydalanuvchini "
                "kuttirmaslik kerak (UX)",
                "Email yuborish faqat orqa fonda ishlashi mumkin",
                "Flask sinxron email yubora olmaydi",
                "Tezroq jo'natiladi"],
               "A",
               hint="Foydalanuvchi 5 soniya kutishi kerakmi?",
               diff="Easy", pts=2),
            mc("itsdangerous URLSafeTimedSerializer nimaga ishlatiladi?",
               ["Vaqt bilan tugaydigan, imzolangan tokenlar yaratish (parol "
                "tiklash kabi)",
                "Faqat parolni hash qilish",
                "JSON serialization",
                "URL'larni qisqartirish"],
               "A",
               hint="Token vaqt bilan tugashi va soxtalashtirib bo'lmasligi.",
               diff="Medium", pts=3),
            mc("Email enumeration himoyasi nima va u qanday qilinadi?",
               ["Foydalanuvchi /forgot ga email yuborganida, email bor yoki "
                "yo'qligi haqida ma'lumot bermaslik — har doim bir xil javob",
                "Email kiritishni butunlay bloklash",
                "Faqat ma'lum email manzillariga ruxsat berish",
                "Hech narsa qilmaslik"],
               "A",
               hint="Agar javob farq qilsa, hujumchi qaysi email'lar "
                    "ro'yxatda borligini bilib oladi.",
               explanation="«Email yuborildi» yoki «Email topilmadi» o'rniga "
                           "har doim «Agar email ro'yxatdan o'tgan bo'lsa, "
                           "link yuborildi» deb javob beriladi.",
               diff="Hard", pts=4),
            dd("Parolni tiklash flow'ini to'g'ri tartibda joylang",
               ["Foydalanuvchi /auth/forgot sahifasiga email yuboradi",
                "Server email mavjudligini tekshiradi (jim — javob bermaydi)",
                "make_reset_token(user.id) bilan token yaratiladi",
                "Email shablon orqali link bilan jo'natiladi (async)",
                "Foydalanuvchi email'dagi linkni bosadi (/auth/reset/<token>)",
                "verify_reset_token(token) user_id qaytaradi (yoki None)",
                "Yangi parol yuboriladi va user.set_password + commit",
                "Foydalanuvchi /auth/login ga redirect bo'ladi"],
               diff="Hard", pts=4),
            ti("Thread'da yuborish paytida current_app o'rniga "
               "current_app._get_current_object() ishlatish nima uchun zarur?",
               "current_app — bu Flask'ning LocalProxy obyekti, u request "
               "context ichida ishlaydi. Yangi Thread'ga o'tib ketganda, "
               "asl request konteksti yo'q va current_app foydalanuvchi "
               "kerak bo'lganda RuntimeError ko'taradi. "
               "_get_current_object() esa proxy ortidagi haqiqiy Flask app "
               "obyektini qaytaradi — uni Thread'ga to'g'ridan-to'g'ri "
               "o'tkazib, ichida with app.app_context() ochishimiz mumkin.",
               hint="LocalProxy va asl Flask obyekt orasidagi farq.",
               diff="Hard", pts=4),
            mc("Test paytida haqiqiy email yubormaslik uchun qaysi sozlama?",
               ["MAIL_SUPPRESS_SEND = True (yuborilgan xatlar "
                "mail.record_messages() orqali tutilib qoladi)",
                "Hech qanday sozlama — testlar real email yuborishi shart",
                "Email modulini import qilmaslik",
                "Mailbox'ni o'chirish"],
               "A",
               hint="Flask-Mail testlar uchun maxsus bayroq beradi.",
               diff="Medium", pts=3),
        ],
    },
    {
        "order": 16, "title": "R3-Mini-Blog (capstone)",
        "text": R3_TEXT, "code": R3_CODE, "lang": "python",
        "video": "https://youtu.be/3KFNoTLnvgY",
        "exercises": [
            mc("Capstone loyihada zarur bo'lgan Blueprintlar tipik to'plami?",
               ["main, auth, posts, api (4+ Blueprint)",
                "Faqat bitta — app.py'da hammasi",
                "10+ Blueprint — har route uchun alohida",
                "Hech qanday Blueprint kerak emas"],
               "A",
               hint="O'rta hisobda — funksional domenlarga qarab ajratish.",
               diff="Easy", pts=2),
            mc("Production deploy paytida MUHIM xavfsizlik tekshiruvlari?",
               ["SECRET_KEY environment dan o'qiladi (hardcode emas)",
                "DEBUG = False",
                "Yuklangan fayllar uploads/ papkasida (static dan tashqarida)",
                "Email creds, DB URL — .env'da, hech qachon git'da"],
               "A,B,C,D", multi=True,
               hint="To'rttala ham majburiy.",
               diff="Medium", pts=3),
            mc("REST API bilan HTML rendering bir loyihada birga ishlashi "
               "mumkinmi?",
               ["Ha — alohida Blueprintlar (api_bp va posts_bp) bilan, "
                "ikkala interfeys bir baza ustida ishlaydi",
                "Yo'q — faqat birini tanlash kerak",
                "Faqat agar Flask 3.0+ bo'lsa",
                "Hech qachon yo'q"],
               "A",
               hint="Bir kod bazasi, ikki interfeys — bu eng keng tarqalgan "
                    "Flask pattern.",
               diff="Easy", pts=2),
            dd("Capstone loyihasini boshlash bosqichlarini to'g'ri tartibda "
               "joylang",
               ["requirements.txt (Flask + barcha kengaytmalar)",
                "config.py: Dev/Test/Prod Config klasslari + Mail sozlamalari",
                "app/__init__.py: create_app + db/migrate/login/mail init",
                "app/models.py: User, Post, Tag, Comment",
                "flask db init + birinchi migration (initial tables)",
                "Blueprintlar: main, auth, posts, api, user, admin",
                "Templates: base.html va har Blueprint uchun shablon papkasi",
                "Email shablonlar: welcome.{html,txt}, reset.{html,txt}",
                "Manual testing va README yozish",
                "Deploy (Render/Railway) + live URL"],
               diff="Hard", pts=4),
            ti("Nima uchun bir xil loyihada HTML CRUD VA REST API ikkalasini "
               "ham qo'llab-quvvatlash yaxshi g'oya?",
               "HTML CRUD klassik veb foydalanuvchilar uchun (brauzer, "
               "qidiruv mashinalari uchun SEO, server-rendered sahifalar). "
               "REST API esa mobil ilovalar, JavaScript SPA (React/Vue), "
               "boshqa servislar (webhooks, integratsiyalar) uchun. Bir kod "
               "bazasi bir xil ma'lumotlar va biznes logikasi ustida "
               "ikkala interfeysni xizmat qila oladi — bu DRY (Don't "
               "Repeat Yourself) tamoyiliga mos va ko'p mijoz turlari uchun "
               "imkoniyat beradi.",
               hint="HTML va REST har biri qaysi turdagi mijozlarga xizmat "
                    "qiladi?",
               diff="Hard", pts=4),
            mc("Live demo uchun bepul host platformalari qaysilar?",
               ["Render",
                "Railway",
                "PythonAnywhere",
                "Hammasi yuqorida"],
               "D",
               hint="Hammasi bepul tier beradi (qisqartirilgan, lekin "
                    "demo uchun yetadi).",
               diff="Easy", pts=2),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers (identical to basics)
# ─────────────────────────────────────────────────────────────────────────────

def _jdump(value):
    """Serialize lists to JSON for text columns; pass scalars through."""
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson: dict, exercise_rows: list[Exercise]) -> str:
    """Mirror the basics course shape: text → code → video → exercise."""
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
            await db.execute(
                select(Course).where(Course.title == COURSE["title"])
            )
        ).scalar_one_or_none()
        if existing:
            print(f"Course '{COURSE['title']}' already exists "
                  f"(id={existing.id}). Delete it first to re-seed.")
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
                  f"{lesson.title:<46}  exercises={len(ex_rows)}")

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
