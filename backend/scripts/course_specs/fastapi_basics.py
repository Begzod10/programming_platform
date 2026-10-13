"""Course spec: FastAPI Asoslari — 6 lessons, UZ + RU.

A Notes API is built in stages: first endpoint (path/query params, /docs) -> Pydantic
request bodies -> SQLAlchemy + Depends -> JWT auth (OAuth2 password flow) -> CORS + pytest
with dependency_overrides -> project. Every code constant below is materialised into a real
FastAPI project and run by the verification script before a lesson text may use it.
API messages are English so the code is identical in UZ and RU.
"""
from __future__ import annotations

# ── Stage code (single source of truth for lessons 1-6) ──────────────────────

CODE_MAIN_L1 = '''from fastapi import FastAPI, HTTPException

app = FastAPI(title="Notes API")

NOTES = [
    {"id": 1, "text": "buy bread"},
    {"id": 2, "text": "learn FastAPI"},
]


@app.get("/")
def root():
    return {"message": "Notes API is running"}


@app.get("/notes")
def list_notes(limit: int = 10, search: str | None = None):
    notes = NOTES
    if search:
        notes = [n for n in notes if search.lower() in n["text"].lower()]
    return notes[:limit]


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    for note in NOTES:
        if note["id"] == note_id:
            return note
    raise HTTPException(status_code=404, detail="note not found")
'''

CODE_MAIN_L2 = '''from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, StringConstraints

app = FastAPI(title="Notes API")

NoteText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]


class NoteCreate(BaseModel):
    text: NoteText


class NoteOut(BaseModel):
    id: int
    text: str


NOTES: list[dict] = []
next_id = 1


@app.get("/notes", response_model=list[NoteOut])
def list_notes():
    return NOTES


@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate):
    global next_id
    note = {"id": next_id, "text": data.text}
    next_id += 1
    NOTES.append(note)
    return note


@app.patch("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteCreate):
    for note in NOTES:
        if note["id"] == note_id:
            note["text"] = data.text
            return note
    raise HTTPException(status_code=404, detail="note not found")


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    for note in NOTES:
        if note["id"] == note_id:
            NOTES.remove(note)
            return
    raise HTTPException(status_code=404, detail="note not found")
'''

CODE_DATABASE = '''from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

CODE_MODELS_L3 = '''from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
'''

CODE_SCHEMAS_L3 = '''from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

NoteText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]


class NoteCreate(BaseModel):
    text: NoteText


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
'''

CODE_MAIN_L3 = '''from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   # runs once at startup
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(db: Session = Depends(get_db)):
    return db.scalars(select(models.Note).order_by(models.Note.id)).all()


@app.post("/notes", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: schemas.NoteCreate, db: Session = Depends(get_db)):
    note = models.Note(text=data.text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.get("/notes/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(models.Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(models.Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    db.delete(note)
    db.commit()
'''

CODE_MODELS_L4 = '''from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(default=False)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(200))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
'''

CODE_SCHEMAS_L4 = '''from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

NoteText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]


class NoteCreate(BaseModel):
    text: NoteText


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    owner_id: int
    created_at: datetime


class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]
    password: Annotated[str, StringConstraints(min_length=6, max_length=72)]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
'''

CODE_SECURITY = '''import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from database import get_db

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-use-a-long-random-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user: models.User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": str(user.id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(models.User, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error
    if user is None:
        raise error
    return user


def require_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin only")
    return user
'''

CODE_MAIN_L4 = '''from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
from security import create_access_token, get_current_user, hash_password, require_admin, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.User).where(models.User.username == data.username)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username is taken")
    user = models.User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.username == form.username))
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(models.Note).order_by(models.Note.id)
    if not user.is_admin:
        query = query.where(models.Note.owner_id == user.id)
    return db.scalars(query).all()


@app.post("/notes", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: schemas.NoteCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = models.Note(text=data.text, owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.get(models.Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    if note.owner_id != user.id and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not your note")
    db.delete(note)
    db.commit()


@app.get("/admin/users", response_model=list[schemas.UserOut])
def list_users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(models.User).order_by(models.User.id)).all()
'''

CODE_CORS_L5 = '''from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
'''

# 5-dars va 6-dars uchun to'liq main.py: CORS qo'shilgan
CODE_MAIN_L5 = CODE_MAIN_L4.replace(
    'app = FastAPI(title="Notes API", lifespan=lifespan)\n',
    'app = FastAPI(title="Notes API", lifespan=lifespan)\n\n'
    + CODE_CORS_L5.replace("from fastapi.middleware.cors import CORSMiddleware\n\n", ""),
).replace(
    "from fastapi.security import OAuth2PasswordRequestForm\n",
    "from fastapi.middleware.cors import CORSMiddleware\nfrom fastapi.security import OAuth2PasswordRequestForm\n",
)

PYTEST_INI = '''[pytest]
pythonpath = .
'''

CODE_TESTS_L5 = '''from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base, get_db
from main import app
from security import ALGORITHM, SECRET_KEY, hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client, username):
    body = {"username": username, "password": "secret12"}
    assert client.post("/register", json=body).status_code == 201
    token = client.post("/token", data=body).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_validates_and_rejects_duplicates(client):
    assert client.post("/register", json={"username": "ab", "password": "secret12"}).status_code == 422
    assert client.post("/register", json={"username": "ali", "password": "secret12"}).status_code == 201
    assert client.post("/register", json={"username": "ali", "password": "secret12"}).status_code == 409


def test_wrong_password_gets_no_token(client):
    client.post("/register", json={"username": "ali", "password": "secret12"})
    res = client.post("/token", data={"username": "ali", "password": "wrong"})
    assert res.status_code == 401


def test_notes_need_a_valid_token(client):
    assert client.get("/notes").status_code == 401
    res = client.get("/notes", headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 401
    assert res.json()["detail"] == "could not validate credentials"


def test_an_expired_token_is_rejected(client):
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}, SECRET_KEY, algorithm=ALGORITHM
    )
    res = client.get("/notes", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401


def test_users_only_see_and_delete_their_own_notes(client):
    ali = register_and_login(client, "ali")
    vali = register_and_login(client, "vali")
    created = client.post("/notes", json={"text": "ali note"}, headers=ali)
    assert created.status_code == 201
    note_id = created.json()["id"]
    assert len(client.get("/notes", headers=ali).json()) == 1
    assert client.get("/notes", headers=vali).json() == []
    assert client.delete(f"/notes/{note_id}", headers=vali).status_code == 403
    assert client.delete(f"/notes/{note_id}", headers=ali).status_code == 204
    assert client.delete(f"/notes/{note_id}", headers=ali).status_code == 404


def test_admin_sees_everything_and_only_admin_lists_users(client):
    ali = register_and_login(client, "ali")
    with TestingSession() as db:
        db.add(models.User(username="boss", password_hash=hash_password("secret12"), is_admin=True))
        db.commit()
    token = client.post("/token", data={"username": "boss", "password": "secret12"}).json()["access_token"]
    boss = {"Authorization": f"Bearer {token}"}
    client.post("/notes", json={"text": "ali note"}, headers=ali)
    assert len(client.get("/notes", headers=boss).json()) == 1
    assert client.get("/admin/users", headers=boss).status_code == 200
    assert client.get("/admin/users", headers=ali).status_code == 403


def test_cors_allows_the_frontend_origin_and_the_authorization_header(client):
    pre = client.options(
        "/notes",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert pre.headers["access-control-allow-origin"] == "http://localhost:8080"
    assert "authorization" in pre.headers["access-control-allow-headers"].lower()
    other = client.options(
        "/notes", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"}
    )
    assert "access-control-allow-origin" not in other.headers
'''

API_JS = '''const API = "http://127.0.0.1:8000";

async function login(username, password) {
  const res = await fetch(`${API}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail);
  localStorage.setItem("auth_token", data.access_token);
  return data;
}

async function loadNotes() {
  const res = await fetch(`${API}/notes`, {
    headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
  });
  if (res.status === 401) {
    localStorage.removeItem("auth_token");
    throw new Error("login required");
  }
  return res.json();
}
'''

CMD_INSTALL = '''pip install fastapi "uvicorn[standard]"
'''

CMD_RUN = '''uvicorn main:app --reload
'''

CMD_PIP_DB = '''pip install sqlalchemy
'''

CMD_PIP_AUTH = '''pip install pyjwt bcrypt python-multipart
'''

CMD_PIP_TEST = '''pip install pytest httpx
pytest
'''

CURL_L1 = '''curl http://127.0.0.1:8000/notes
curl "http://127.0.0.1:8000/notes?search=bread&limit=1"
curl http://127.0.0.1:8000/notes/2
curl http://127.0.0.1:8000/notes/abc
'''

CURL_L2 = '''curl -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" -d '{"text": "buy bread"}'
curl -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" -d '{"text": "ab"}'
curl -X DELETE http://127.0.0.1:8000/notes/1
'''

CURL_L4 = '''curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl -X POST http://127.0.0.1:8000/token -d "username=ali&password=secret12"
curl http://127.0.0.1:8000/notes -H "Authorization: Bearer eyJ..."
'''

CURL_PREFLIGHT = '''curl -i -X OPTIONS http://127.0.0.1:8000/notes -H "Origin: http://localhost:8080" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: authorization"
'''

POSTMAN_SCRIPT = '''const data = pm.response.json();
pm.collectionVariables.set("token", data.access_token);
'''

INDEX_HTML = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Notes</title>
</head>
<body>
  <h1>Notes</h1>
  <form id="login-form">
    <input id="username" placeholder="username" required>
    <input id="password" type="password" placeholder="password" required>
    <button>Login</button>
  </form>
  <p id="message"></p>
  <ul id="notes"></ul>
  <script src="api.js"></script>
  <script>
    const message = document.getElementById("message");
    const list = document.getElementById("notes");

    async function showNotes() {
      list.innerHTML = "";
      try {
        for (const note of await loadNotes()) {
          const li = document.createElement("li");
          li.textContent = note.text;
          list.appendChild(li);
        }
      } catch (err) {
        message.textContent = err.message;
      }
    }

    document.getElementById("login-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await login(event.target.username.value, event.target.password.value);
        message.textContent = "";
        showNotes();
      } catch (err) {
        message.textContent = err.message;
      }
    });

    if (localStorage.getItem("auth_token")) showNotes();
  </script>
</body>
</html>
'''


COURSE = {
    "title": "FastAPI Asoslari",
    "title_ru": "Основы FastAPI",
    "description": (
        "FastAPI bilan zamonaviy API yasashni o'rganasiz: birinchi endpoint va avtomatik /docs, Pydantic bilan so'rov tanasi "
        "va validatsiya, SQLAlchemy bilan baza va Depends, JWT autentifikatsiya, CORS va pytest testlari. "
        "Kurs oxirida tokenli Notes API va unga ulangan oddiy frontend yasaysiz."
    ),
    "description_ru": (
        "Вы научитесь делать современный API на FastAPI: первый эндпоинт и автоматический /docs, тело запроса и валидация "
        "через Pydantic, база данных на SQLAlchemy и Depends, JWT-аутентификация, CORS и тесты на pytest. "
        "В конце курса вы сделаете Notes API с токеном и подключите к нему простой фронтенд."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 8,
    "prerequisite_course_id": 37,
    "display_order": 310,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


# ── 1-dars: birinchi endpoint ────────────────────────────────────────────────

_L1_TEXT_UZ = """<h3>FastAPI nima</h3>
<p><strong>FastAPI</strong> — Python uchun zamonaviy API framework. Uning uchta kuchli tomoni bor: Python <em>type hint</em>lari (<code>int</code>, <code>str</code>) orqali kiruvchi ma'lumotni avtomatik tekshiradi, <strong>avtomatik hujjat</strong> (<code>/docs</code>) yaratadi va juda tez ishlaydi. Flask'da tekshiruvni qo'lda yozgan bo'lsangiz, bu yerda uni funksiya imzosi (parametrlari) o'zi bajaradi.</p>

<h3>O'rnatish va ishga tushirish</h3>
<pre><code>__INSTALL__</code></pre>
<p><strong>uvicorn</strong> — FastAPI ilovasini ishga tushiradigan server (ASGI server). Ilovani <code>main.py</code> fayliga yozing va ishga tushiring:</p>
<pre><code>__RUN__</code></pre>
<p><code>main:app</code> — «<code>main.py</code> faylidagi <code>app</code> obyekti». <code>--reload</code> kodni o'zgartirganingizda serverni o'zi qayta ishga tushiradi (faqat ishlab chiqish uchun).</p>

<h3>Birinchi endpoint'lar</h3>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>@app.get("/notes")</code> — GET so'rovi shu yo'lga kelganda funksiya chaqiriladi. Qaytarilgan <code>dict</code> yoki ro'yxat avtomatik JSON bo'ladi.</li>
  <li><strong>Path parametri:</strong> <code>/notes/{note_id}</code> dagi <code>note_id: int</code>. FastAPI qiymatni <code>int</code> ga aylantiradi. <code>/notes/abc</code> yuborilsa, funksiya umuman chaqirilmaydi va <code>422</code> qaytadi.</li>
  <li><strong>Query parametri:</strong> yo'lda yo'q, funksiyada bor parametr (<code>limit</code>, <code>search</code>) so'rovda <code>?limit=1&amp;search=bread</code> bo'lib keladi. Standart qiymati bo'lsa, ixtiyoriy; <code>str | None = None</code> — ixtiyoriy matn.</li>
  <li><strong><code>HTTPException</code></strong> berilgan status kodi bilan JSON xato qaytaradi: <code>{"detail": "note not found"}</code>.</li>
</ul>
<pre class="mermaid">
flowchart LR
  A["So'rov: GET /notes/abc"] --> B["Yo'l topiladi"]
  B --> C{"note_id: int ga aylandimi?"}
  C -- "yo'q" --> D["422 + xato tavsifi (funksiya chaqirilmaydi)"]
  C -- "ha" --> E["Funksiya bajariladi"]
  E --> F["Natija JSON ga aylanadi"]
</pre>

<h3>Avtomatik hujjat</h3>
<p>Brauzerda <code>http://127.0.0.1:8000/docs</code> ni oching: <strong>Swagger UI</strong> barcha endpoint'larni ko'rsatadi va ularni shu yerning o'zida sinab ko'rishga imkon beradi (<em>Try it out</em>). <code>/redoc</code> — shu hujjatning boshqa ko'rinishi, <code>/openapi.json</code> — mashina o'qiydigan tavsif. Hujjatni qo'lda yozmaysiz: u kodingizdan yasaladi, shuning uchun kod bilan bir vaqtda yangilanadi.</p>

<h3>def yoki async def</h3>
<p>FastAPI ikkalasini ham qo'llaydi. <code>async def</code> ichida <code>await</code> bilan kutiladigan kutubxonalar (asinxron baza, <code>httpx</code>) ishlatiladi. Oddiy <code>def</code> esa bloklovchi kod uchun (bizning sinxron SQLAlchemy kabi): FastAPI uni alohida oqimda bajaradi va server boshqa so'rovlarga javob berishda davom etadi. Shubha bo'lsa, oddiy <code>def</code> yozing.</p>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Oxirgi so'rov <code>422</code> va <code>{"detail": [{"type": "int_parsing", "loc": ["path", "note_id"], ...}]}</code> qaytaradi: <code>loc</code> xato qayerda ekanini ko'rsatadi.</p>"""

_L1_TEXT_RU = """<h3>Что такое FastAPI</h3>
<p><strong>FastAPI</strong> — современный фреймворк для API на Python. У него три сильные стороны: он автоматически проверяет входные данные по <em>type hint</em>-ам Python (<code>int</code>, <code>str</code>), создаёт <strong>автоматическую документацию</strong> (<code>/docs</code>) и работает очень быстро. Если во Flask вы писали проверку вручную, то здесь её выполняет сама сигнатура функции (её параметры).</p>

<h3>Установка и запуск</h3>
<pre><code>__INSTALL__</code></pre>
<p><strong>uvicorn</strong> — сервер (ASGI-сервер), который запускает приложение FastAPI. Напишите приложение в файле <code>main.py</code> и запустите:</p>
<pre><code>__RUN__</code></pre>
<p><code>main:app</code> означает «объект <code>app</code> из файла <code>main.py</code>». Флаг <code>--reload</code> сам перезапускает сервер при изменении кода (только для разработки).</p>

<h3>Первые эндпоинты</h3>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>@app.get("/notes")</code> — функция вызывается, когда по этому пути приходит GET-запрос. Возвращённый <code>dict</code> или список автоматически становится JSON.</li>
  <li><strong>Path-параметр:</strong> <code>note_id: int</code> в <code>/notes/{note_id}</code>. FastAPI преобразует значение в <code>int</code>. Если отправить <code>/notes/abc</code>, функция вообще не вызывается, а возвращается <code>422</code>.</li>
  <li><strong>Query-параметр:</strong> параметр, которого нет в пути, но есть в функции (<code>limit</code>, <code>search</code>), приходит в запросе как <code>?limit=1&amp;search=bread</code>. Если есть значение по умолчанию, он необязательный; <code>str | None = None</code> — необязательная строка.</li>
  <li><strong><code>HTTPException</code></strong> возвращает JSON-ошибку с указанным кодом статуса: <code>{"detail": "note not found"}</code>.</li>
</ul>
<pre class="mermaid">
flowchart LR
  A["Запрос: GET /notes/abc"] --> B["Находится маршрут"]
  B --> C{"note_id преобразован в int?"}
  C -- "нет" --> D["422 + описание ошибки (функция не вызывается)"]
  C -- "да" --> E["Функция выполняется"]
  E --> F["Результат превращается в JSON"]
</pre>

<h3>Автоматическая документация</h3>
<p>Откройте в браузере <code>http://127.0.0.1:8000/docs</code>: <strong>Swagger UI</strong> показывает все эндпоинты и позволяет пробовать их прямо на странице (<em>Try it out</em>). <code>/redoc</code> — другой вид той же документации, <code>/openapi.json</code> — машиночитаемое описание. Документацию вы не пишете вручную: она строится по коду, поэтому обновляется вместе с ним.</p>

<h3>def или async def</h3>
<p>FastAPI поддерживает оба варианта. <code>async def</code> используют с библиотеками, которые ждут через <code>await</code> (асинхронная база, <code>httpx</code>). Обычный <code>def</code> — для блокирующего кода (как наш синхронный SQLAlchemy): FastAPI выполняет его в отдельном потоке, и сервер продолжает отвечать на другие запросы. Если сомневаетесь, пишите обычный <code>def</code>.</p>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Последний запрос вернёт <code>422</code> и <code>{"detail": [{"type": "int_parsing", "loc": ["path", "note_id"], ...}]}</code>: поле <code>loc</code> показывает, где ошибка.</p>"""

_L1_BLOCKS = dict(INSTALL=CMD_INSTALL, RUN=CMD_RUN, CODE=CODE_MAIN_L1, CURL=CURL_L1)

LESSON_1 = {
    "order": 0,
    "title": "1-FastAPI va birinchi endpoint",
    "title_ru": "1-FastAPI и первый эндпоинт",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": CODE_MAIN_L1,
    "code_content_ru": CODE_MAIN_L1,
    "code_language": "python",
    "sample": {
        "title": "Namuna: birinchi FastAPI endpoint'lari",
        "title_ru": "Пример: первые эндпоинты FastAPI",
        "description": "Path va query parametrlari, HTTPException, avtomatik /docs.",
        "description_ru": "Path- и query-параметры, HTTPException, автоматический /docs.",
        "sample_type": "code",
        "code_files": [{"filename": "main.py", "language": "python", "code": CODE_MAIN_L1}],
    },
    "exercises": [
        {
            "title": "Hujjat manzili", "title_ru": "Адрес документации",
            "description": "FastAPI avtomatik yaratadigan Swagger UI hujjati qaysi manzilda?",
            "description_ru": "По какому адресу находится автоматическая документация Swagger UI?",
            "exercise_type": "multiple_choice",
            "options": ["/docs", "/swagger.json", "/help", "/api-docs.html"],
            "options_ru": ["/docs", "/swagger.json", "/help", "/api-docs.html"],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Nomi inglizcha «documents» ning qisqartmasi.",
            "hint_ru": "Название — сокращение от «documents».",
            "explanation": "Swagger UI /docs da, ReDoc /redoc da, mashina o'qiydigan tavsif esa /openapi.json da turadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Serverni ishga tushirish", "title_ru": "Запуск сервера",
            "description": "main.py ichidagi app ni ishga tushiradigan buyruq: ___ main:app --reload",
            "description_ru": "Команда запуска app из main.py: ___ main:app --reload",
            "exercise_type": "fill_in_blank",
            "correct_answers": "uvicorn",
            "hint": "ASGI serveri nomi «uvi...» bilan boshlanadi.",
            "hint_ru": "Название ASGI-сервера начинается с «uvi...».",
            "explanation": "uvicorn FastAPI ilovasini ishga tushiradigan ASGI serveri; main:app — fayl va undagi obyekt nomi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Path parametri xatosi", "title_ru": "Ошибка path-параметра",
            "description": "get_note(note_id: int) uchun /notes/abc so'rovi yuborilsa nima bo'ladi?",
            "description_ru": "Что произойдёт при запросе /notes/abc к get_note(note_id: int)?",
            "exercise_type": "multiple_choice",
            "options": [
                "422: funksiya chaqirilmaydi, javobda xato tavsifi bo'ladi",
                "500: server qulaydi",
                "404 va bo'sh javob",
                "200 va note_id = \"abc\"",
            ],
            "options_ru": [
                "422: функция не вызывается, в ответе описание ошибки",
                "500: сервер падает",
                "404 и пустой ответ",
                "200 и note_id = \"abc\"",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "FastAPI turni funksiyadan oldin tekshiradi.",
            "hint_ru": "FastAPI проверяет тип до вызова функции.",
            "explanation": "int ga aylantirib bo'lmasa, FastAPI 422 Unprocessable Entity qaytaradi va xato qayerda ekanini loc maydonida ko'rsatadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi gaplar to'g'ri", "title_ru": "Какие утверждения верны",
            "description": "FastAPI haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о FastAPI верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Parametrlarning type hint'lari ma'lumotni avtomatik tekshiradi",
                "Hujjat kod asosida avtomatik yaratiladi",
                "Hujjatni qo'lda alohida yozish shart",
                "Funksiya ichida har bir parametrni qo'lda int() ga aylantirish shart",
            ],
            "options_ru": [
                "Type hint параметров автоматически проверяют данные",
                "Документация автоматически строится по коду",
                "Документацию обязательно писать вручную отдельно",
                "Каждый параметр внутри функции нужно вручную приводить через int()",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "FastAPI qo'lda bajariladigan ishlarni kamaytiradi.",
            "hint_ru": "FastAPI уменьшает объём ручной работы.",
            "explanation": "Type hint tekshiruvni, kod esa hujjatni o'zi beradi: qo'lda parse qilish ham, alohida hujjat yozish ham shart emas.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Query va path", "title_ru": "Query и path",
            "description": "Path parametri bilan query parametrining farqini o'z so'zingiz bilan yozing.",
            "description_ru": "Объясните своими словами разницу между path-параметром и query-параметром.",
            "exercise_type": "text_input",
            "expected_answer": "Path parametri URL yo'lining ichida bo'ladi (/notes/{note_id}) va resursni aniqlaydi. Query parametri yo'lda yo'q, funksiyada bor parametr bo'lib, so'rovda ?limit=1 ko'rinishida keladi va odatda filtr yoki sozlama uchun ixtiyoriy bo'ladi.",
            "hint": "Qaysi biri URL yo'lida, qaysi biri «?» dan keyin?",
            "hint_ru": "Какой из них в пути URL, а какой после «?»?",
            "explanation": "Path parametri resursni aniqlaydi va yo'lda yoziladi; query parametri filtr, tartib kabi qo'shimcha sozlama bo'lib, ? dan keyin keladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 2-dars: Pydantic ─────────────────────────────────────────────────────────

_L2_TEXT_UZ = """<h3>So'rov tanasi: Pydantic modeli</h3>
<p>POST va PATCH'da ma'lumot so'rov <em>tanasi</em>da (JSON) keladi. FastAPI uni <strong>Pydantic</strong> modeli bilan tekshiradi: <code>BaseModel</code> dan meros olgan klassda maydonlarning turi va cheklovlari yoziladi. Funksiya parametri shu modelga tegishli bo'lsa, FastAPI uni JSON tanasi deb tushunadi, tekshiradi va tayyor obyekt sifatida beradi.</p>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>NoteCreate</code> — <em>kiruvchi</em> ma'lumot (mijoz nima yubora oladi). <code>StringConstraints</code> avval bo'sh joylarni qirqadi (<code>strip_whitespace</code>), keyin uzunlikni tekshiradi (3–200).</li>
  <li><code>NoteOut</code> — <em>chiquvchi</em> ma'lumot. <code>response_model=NoteOut</code> javobni shu shaklga keltiradi: ortiqcha maydonlar tushib qoladi va hujjatda javob tuzilmasi ko'rinadi.</li>
  <li><code>status_code=201</code> yaratish uchun, <code>204</code> (javob tanasiz) o'chirish uchun.</li>
  <li>Kiruvchi va chiquvchi modelni ajratish xavfsizlik uchun muhim: mijoz <code>id</code> kabi serverga tegishli maydonlarni yubora olmaydi.</li>
</ul>
<p>Misolda yozuvlar oddiylik uchun ro'yxatda (xotirada) saqlanadi: server qayta ishga tushsa, ular yo'qoladi. Keyingi darsda ularni bazaga o'tkazamiz.</p>

<h3>Validatsiya xatosi</h3>
<p>Mijoz noto'g'ri ma'lumot yuborsa, FastAPI funksiyani chaqirmasdan <code>422</code> qaytaradi. Javobdagi <code>detail</code> — ro'yxat, har elementda <code>loc</code> (xato qayerda: <code>["body", "text"]</code>), <code>msg</code> (matn) va <code>type</code> (xato turi). Frontend shu <code>loc</code> bo'yicha xatoni kerakli maydon yonida ko'rsata oladi.</p>

<h3>PATCH va DELETE</h3>
<p>Yozuv topilmasa <code>HTTPException(404)</code>. O'chirishda <code>204</code> qaytariladi va hech narsa qaytarilmaydi (<code>return</code>). Bu amallar 1-darsdagi path parametri bilan birga ishlaydi: <code>/notes/{note_id}</code>.</p>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Ikkinchi so'rov <code>422</code> va <code>"String should have at least 3 characters"</code> xabarini qaytaradi. Shuningdek <code>/docs</code> da <em>Try it out</em> tugmasi bilan JSON tanasini yuborib ko'ring: u modelga qarab tayyor namuna yaratadi.</p>"""

_L2_TEXT_RU = """<h3>Тело запроса: модель Pydantic</h3>
<p>В POST и PATCH данные приходят в <em>теле</em> запроса (JSON). FastAPI проверяет их моделью <strong>Pydantic</strong>: в классе, наследующем <code>BaseModel</code>, записываются типы полей и ограничения. Если параметр функции относится к такой модели, FastAPI понимает, что это тело JSON, проверяет его и передаёт готовый объект.</p>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>NoteCreate</code> — <em>входные</em> данные (что может отправить клиент). <code>StringConstraints</code> сначала обрезает пробелы (<code>strip_whitespace</code>), затем проверяет длину (3–200).</li>
  <li><code>NoteOut</code> — <em>выходные</em> данные. <code>response_model=NoteOut</code> приводит ответ к этой форме: лишние поля отбрасываются, а в документации видна структура ответа.</li>
  <li><code>status_code=201</code> — для создания, <code>204</code> (ответ без тела) — для удаления.</li>
  <li>Разделение входной и выходной модели важно для безопасности: клиент не может прислать служебные поля вроде <code>id</code>.</li>
</ul>
<p>В примере записи для простоты хранятся в списке (в памяти): после перезапуска сервера они пропадут. В следующем уроке мы перенесём их в базу.</p>

<h3>Ошибка валидации</h3>
<p>Если клиент прислал неверные данные, FastAPI возвращает <code>422</code>, не вызывая функцию. <code>detail</code> в ответе — это список, где у каждого элемента есть <code>loc</code> (где ошибка: <code>["body", "text"]</code>), <code>msg</code> (текст) и <code>type</code> (вид ошибки). По <code>loc</code> фронтенд может показать ошибку рядом с нужным полем.</p>

<h3>PATCH и DELETE</h3>
<p>Если запись не найдена, выбрасываем <code>HTTPException(404)</code>. При удалении возвращается <code>204</code> без тела (<code>return</code>). Эти операции работают вместе с path-параметром из урока 1: <code>/notes/{note_id}</code>.</p>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Второй запрос вернёт <code>422</code> и сообщение <code>"String should have at least 3 characters"</code>. Также попробуйте в <code>/docs</code> кнопку <em>Try it out</em> и отправку JSON-тела: она подставляет готовый пример по модели.</p>"""

_L2_BLOCKS = dict(CODE=CODE_MAIN_L2, CURL=CURL_L2)

LESSON_2 = {
    "order": 1,
    "title": "2-Pydantic: so'rov tanasi va validatsiya",
    "title_ru": "2-Pydantic: тело запроса и валидация",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": CODE_MAIN_L2,
    "code_content_ru": CODE_MAIN_L2,
    "code_language": "python",
    "sample": {
        "title": "Namuna: Pydantic modellari va CRUD",
        "title_ru": "Пример: модели Pydantic и CRUD",
        "description": "NoteCreate va NoteOut modellari, response_model, 201/204/404 holatlari.",
        "description_ru": "Модели NoteCreate и NoteOut, response_model, случаи 201/204/404.",
        "sample_type": "code",
        "code_files": [{"filename": "main.py", "language": "python", "code": CODE_MAIN_L2}],
    },
    "exercises": [
        {
            "title": "Model klassi", "title_ru": "Класс модели",
            "description": "Pydantic modeli qaysi klassdan meros oladi? class NoteCreate(___)",
            "description_ru": "От какого класса наследуется модель Pydantic? class NoteCreate(___)",
            "exercise_type": "fill_in_blank",
            "correct_answers": "BaseModel",
            "hint": "Nomida «Base» va «Model» bor.",
            "hint_ru": "В названии есть «Base» и «Model».",
            "explanation": "Pydantic modellari pydantic.BaseModel dan meros oladi; FastAPI shu klass orqali tanani tekshiradi va hujjatlashtiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Yaratish kodi", "title_ru": "Код при создании",
            "description": "Yangi yozuv yaratadigan POST endpoint odatda qaysi status kodini qaytaradi?",
            "description_ru": "Какой код статуса обычно возвращает POST-эндпоинт, создающий запись?",
            "exercise_type": "multiple_choice",
            "options": ["200", "201", "204", "302"],
            "options_ru": ["200", "201", "204", "302"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "«Created» — yaratildi.",
            "hint_ru": "«Created» — создано.",
            "explanation": "201 Created resurs yaratilganini bildiradi. 204 tanasiz javob (o'chirish) uchun.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "So'rov yo'li", "title_ru": "Путь запроса",
            "description": "Noto'g'ri tanali POST so'rovining FastAPI'dagi yo'lini joylashtiring.",
            "description_ru": "Расположите путь POST-запроса с неверным телом в FastAPI.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Mijoz JSON tanasini yuboradi", "FastAPI NoteCreate bilan tekshiradi", "Tekshiruv muvaffaqiyatsiz: funksiya chaqirilmaydi", "422 va xato tavsifi qaytadi"],
            "drag_items_ru": ["Клиент отправляет тело JSON", "FastAPI проверяет его через NoteCreate", "Проверка не пройдена: функция не вызывается", "Возвращается 422 и описание ошибки"],
            "correct_order": ["Mijoz JSON tanasini yuboradi", "FastAPI NoteCreate bilan tekshiradi", "Tekshiruv muvaffaqiyatsiz: funksiya chaqirilmaydi", "422 va xato tavsifi qaytadi"],
            "hint": "Funksiya faqat to'g'ri ma'lumotdan keyin ishga tushadi.",
            "hint_ru": "Функция запускается только после корректной проверки.",
            "explanation": "FastAPI tanani funksiyadan oldin tekshiradi; noto'g'ri bo'lsa funksiya chaqirilmaydi va 422 qaytadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "response_model foydasi", "title_ru": "Польза response_model",
            "description": "response_model=NoteOut nima beradi? (Bir nechta javob)",
            "description_ru": "Что даёт response_model=NoteOut? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Javobni NoteOut shakliga keltiradi, ortiqcha maydonlar tushib qoladi",
                "Hujjatda javob tuzilmasini ko'rsatadi",
                "Kiruvchi ma'lumotni tekshiradi",
                "Bazani yaratadi",
            ],
            "options_ru": [
                "Приводит ответ к форме NoteOut, лишние поля отбрасываются",
                "Показывает структуру ответа в документации",
                "Проверяет входные данные",
                "Создаёт базу данных",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "U chiquvchi ma'lumot haqida, kiruvchi haqida emas.",
            "hint_ru": "Он про выходные данные, а не про входные.",
            "explanation": "response_model chiquvchi ma'lumotni filtrlaydi va hujjatlashtiradi; kiruvchi tekshiruvni NoteCreate bajaradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega ikkita model", "title_ru": "Зачем две модели",
            "description": "Nega kiruvchi (NoteCreate) va chiquvchi (NoteOut) uchun alohida model yoziladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем для входных (NoteCreate) и выходных (NoteOut) данных пишут отдельные модели? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Kiruvchi modelda faqat mijoz yubora oladigan maydonlar bor, chiquvchida esa serverga tegishli maydonlar (id, yaratilgan vaqt) ham bor. Alohida bo'lsa mijoz id kabi maydonlarni o'zgartira olmaydi va javobga ortiqcha ma'lumot tushmaydi.",
            "hint": "id ni kim belgilashi kerak: mijozmi yoki server?",
            "hint_ru": "Кто должен задавать id: клиент или сервер?",
            "explanation": "Kiruvchi va chiquvchi shakl farq qiladi: id va yaratilgan vaqtni server belgilaydi. Alohida modellar mijozning ortiqcha maydon yuborishini oldini oladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: baza va Depends ──────────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>Reja</h3>
<p>Xotiradagi ro'yxat server qayta ishga tushganda yo'qoladi. Endi yozuvlarni SQLite bazasiga yozamiz (keyin shu kod PostgreSQL bilan ham ishlaydi: faqat manzil o'zgaradi). Buning uchun <strong>SQLAlchemy</strong> ORM'idan va FastAPI'ning asosiy imkoniyati <strong>Depends</strong> (dependency injection) dan foydalanamiz.</p>
<pre><code>__PIP__</code></pre>

<h3>Loyiha tuzilmasi</h3>
<ul>
  <li><code>database.py</code> — ulanish va sessiya;</li>
  <li><code>models.py</code> — jadvallar (SQLAlchemy);</li>
  <li><code>schemas.py</code> — Pydantic modellari (API shakli);</li>
  <li><code>main.py</code> — endpoint'lar.</li>
</ul>
<p>Model (jadval) va schema (API shakli) alohida: jadvalda parol xeshi bo'lishi mumkin, lekin javobda u bo'lmasligi kerak.</p>

<h3>database.py: ulanish va get_db</h3>
<pre><code>__DATABASE__</code></pre>
<ul>
  <li><code>engine</code> — bazaga ulanish, <code>SessionLocal</code> — sessiya yaratuvchi. SQLite uchun <code>check_same_thread=False</code> kerak, chunki FastAPI so'rovlarni turli oqimlarda bajaradi.</li>
  <li><code>get_db</code> — <strong>dependency</strong>: so'rov boshida sessiya ochadi, <code>yield</code> bilan funksiyaga beradi, so'rov tugagach (xato bo'lsa ham) <code>finally</code> da yopadi.</li>
</ul>

<h3>models.py va schemas.py</h3>
<pre><code>__MODELS__</code></pre>
<pre><code>__SCHEMAS__</code></pre>
<p><code>Mapped[int]</code> va <code>mapped_column</code> — SQLAlchemy 2.0 uslubi: Python turi ustun turini belgilaydi. <code>from_attributes=True</code> Pydantic'ga SQLAlchemy obyektidan (atributlardan) o'qishni o'rgatadi, shuning uchun endpoint bazadan olingan obyektni to'g'ridan-to'g'ri qaytara oladi.</p>

<h3>main.py: Depends</h3>
<pre class="mermaid">
flowchart TD
  A["So'rov: GET /notes"] --> B["FastAPI: Depends(get_db) ni chaqiradi"]
  B --> C["Sessiya ochiladi (yield)"]
  C --> D["list_notes(db=sessiya)"]
  D --> E["Javob qaytadi"]
  E --> F["finally: sessiya yopiladi"]
</pre>
<pre><code>__MAIN__</code></pre>
<ul>
  <li><code>db: Session = Depends(get_db)</code> — «menga sessiya ber»: FastAPI <code>get_db</code> ni o'zi chaqiradi va natijani parametrga qo'yadi. Sessiyani qo'lda ochib-yopish shart emas.</li>
  <li><code>lifespan</code> server ishga tushganda bir marta <code>create_all</code> bilan jadvallarni yaratadi.</li>
  <li><code>select(...)</code> so'rov quradi; <code>db.scalars(...).all()</code> ro'yxat, <code>db.get(Model, id)</code> id bo'yicha bitta yozuv (yo'q bo'lsa <code>None</code>) beradi.</li>
  <li>Yozish: <code>db.add(obj)</code>, <code>db.commit()</code> bilan saqlash, <code>db.refresh(obj)</code> bilan bazadagi qiymatlarni (<code>id</code>, <code>created_at</code>) olish.</li>
</ul>
<p>Eslatma: <code>create_all</code> mavjud jadvalni <em>o'zgartirmaydi</em>. Jadval tuzilmasi o'zgarsa, haqiqiy loyihada migratsiya vositasi (Alembic) ishlatiladi; o'quv loyihasida <code>notes.db</code> faylini o'chirib tashlash kifoya.</p>

<h3>Dependency nega qulay</h3>
<p>Dependency bir joyda yoziladi va istalgan endpoint'ga <code>Depends</code> bilan ulanadi. Keyingi darslarda shu usul bilan «joriy foydalanuvchi» ni ham beramiz, testlarda esa bazani osongina almashtiramiz.</p>"""

_L3_TEXT_RU = """<h3>План</h3>
<p>Список в памяти пропадает при перезапуске сервера. Теперь запишем данные в базу SQLite (потом тот же код заработает и с PostgreSQL: изменится только адрес). Для этого используем ORM <strong>SQLAlchemy</strong> и главную возможность FastAPI — <strong>Depends</strong> (внедрение зависимостей, dependency injection).</p>
<pre><code>__PIP__</code></pre>

<h3>Структура проекта</h3>
<ul>
  <li><code>database.py</code> — подключение и сессия;</li>
  <li><code>models.py</code> — таблицы (SQLAlchemy);</li>
  <li><code>schemas.py</code> — модели Pydantic (форма API);</li>
  <li><code>main.py</code> — эндпоинты.</li>
</ul>
<p>Модель (таблица) и схема (форма API) разделены: в таблице может лежать хеш пароля, но в ответе его быть не должно.</p>

<h3>database.py: подключение и get_db</h3>
<pre><code>__DATABASE__</code></pre>
<ul>
  <li><code>engine</code> — подключение к базе, <code>SessionLocal</code> — создатель сессий. Для SQLite нужен <code>check_same_thread=False</code>, потому что FastAPI выполняет запросы в разных потоках.</li>
  <li><code>get_db</code> — <strong>зависимость</strong> (dependency): в начале запроса открывает сессию, передаёт её функции через <code>yield</code> и после завершения запроса (даже при ошибке) закрывает в <code>finally</code>.</li>
</ul>

<h3>models.py и schemas.py</h3>
<pre><code>__MODELS__</code></pre>
<pre><code>__SCHEMAS__</code></pre>
<p><code>Mapped[int]</code> и <code>mapped_column</code> — стиль SQLAlchemy 2.0: тип Python задаёт тип столбца. <code>from_attributes=True</code> учит Pydantic читать данные из объекта SQLAlchemy (из атрибутов), поэтому эндпоинт может сразу вернуть объект, полученный из базы.</p>

<h3>main.py: Depends</h3>
<pre class="mermaid">
flowchart TD
  A["Запрос: GET /notes"] --> B["FastAPI вызывает Depends(get_db)"]
  B --> C["Сессия открывается (yield)"]
  C --> D["list_notes(db=сессия)"]
  D --> E["Ответ возвращается"]
  E --> F["finally: сессия закрывается"]
</pre>
<pre><code>__MAIN__</code></pre>
<ul>
  <li><code>db: Session = Depends(get_db)</code> — «дай мне сессию»: FastAPI сам вызывает <code>get_db</code> и подставляет результат в параметр. Открывать и закрывать сессию вручную не нужно.</li>
  <li><code>lifespan</code> один раз при запуске сервера создаёт таблицы через <code>create_all</code>.</li>
  <li><code>select(...)</code> строит запрос; <code>db.scalars(...).all()</code> возвращает список, <code>db.get(Model, id)</code> — одну запись по id (или <code>None</code>, если её нет).</li>
  <li>Запись: <code>db.add(obj)</code>, сохранение через <code>db.commit()</code>, получение значений из базы (<code>id</code>, <code>created_at</code>) через <code>db.refresh(obj)</code>.</li>
</ul>
<p>Заметьте: <code>create_all</code> <em>не изменяет</em> уже существующую таблицу. Если структура таблицы меняется, в настоящем проекте используют инструмент миграций (Alembic); в учебном проекте достаточно удалить файл <code>notes.db</code>.</p>

<h3>Чем удобна зависимость</h3>
<p>Зависимость пишется в одном месте и подключается к любому эндпоинту через <code>Depends</code>. В следующих уроках так же мы получим «текущего пользователя», а в тестах легко подменим базу.</p>"""

_L3_BLOCKS = dict(PIP=CMD_PIP_DB, DATABASE=CODE_DATABASE, MODELS=CODE_MODELS_L3, SCHEMAS=CODE_SCHEMAS_L3, MAIN=CODE_MAIN_L3)

LESSON_3 = {
    "order": 2,
    "title": "3-SQLAlchemy va Depends",
    "title_ru": "3-SQLAlchemy и Depends",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": CODE_MAIN_L3,
    "code_content_ru": CODE_MAIN_L3,
    "code_language": "python",
    "sample": {
        "title": "Namuna: SQLAlchemy bazasi va Depends(get_db)",
        "title_ru": "Пример: база SQLAlchemy и Depends(get_db)",
        "description": "database.py, models.py, schemas.py va get_db dependency'si bilan ishlaydigan Notes API.",
        "description_ru": "Notes API с database.py, models.py, schemas.py и зависимостью get_db.",
        "sample_type": "code",
        "code_files": [
            {"filename": "database.py", "language": "python", "code": CODE_DATABASE},
            {"filename": "models.py", "language": "python", "code": CODE_MODELS_L3},
            {"filename": "schemas.py", "language": "python", "code": CODE_SCHEMAS_L3},
            {"filename": "main.py", "language": "python", "code": CODE_MAIN_L3},
        ],
    },
    "exercises": [
        {
            "title": "Dependency nima", "title_ru": "Что такое зависимость",
            "description": "db: Session = Depends(get_db) nimani bildiradi?",
            "description_ru": "Что означает db: Session = Depends(get_db)?",
            "exercise_type": "multiple_choice",
            "options": [
                "FastAPI get_db ni o'zi chaqirib, natijani db parametriga beradi",
                "db o'zgaruvchisiga funksiyaning o'zi yoziladi, chaqirilmaydi",
                "Bu faqat izoh, hech narsa qilmaydi",
                "Bazani o'chiradi",
            ],
            "options_ru": [
                "FastAPI сам вызывает get_db и передаёт результат в параметр db",
                "В db записывается сама функция, она не вызывается",
                "Это просто комментарий, ничего не делает",
                "Удаляет базу данных",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Depends — «menga buni tayyorlab ber» degani.",
            "hint_ru": "Depends означает «подготовь мне это».",
            "explanation": "Depends dependency injection: FastAPI get_db ni so'rov boshida chaqiradi va qaytargan (yield qilgan) sessiyani parametrga uzatadi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Saqlash buyrug'i", "title_ru": "Команда сохранения",
            "description": "O'zgarishlarni bazaga yozadigan sessiya metodi: db.___()",
            "description_ru": "Метод сессии, записывающий изменения в базу: db.___()",
            "exercise_type": "fill_in_blank",
            "correct_answers": "commit",
            "hint": "Git'dagi buyruq bilan bir xil nom.",
            "hint_ru": "То же название, что и команда в Git.",
            "explanation": "db.add() obyektni sessiyaga qo'shadi, db.commit() esa o'zgarishlarni bazaga yozadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Sessiya hayoti", "title_ru": "Жизнь сессии",
            "description": "get_db dependency'sining so'rov davomidagi tartibini joylashtiring.",
            "description_ru": "Расположите порядок работы зависимости get_db в течение запроса.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Sessiya ochiladi", "yield bilan endpoint'ga beriladi", "Endpoint ishlaydi va javob qaytadi", "finally da sessiya yopiladi"],
            "drag_items_ru": ["Сессия открывается", "Через yield передаётся эндпоинту", "Эндпоинт выполняется, ответ возвращается", "В finally сессия закрывается"],
            "correct_order": ["Sessiya ochiladi", "yield bilan endpoint'ga beriladi", "Endpoint ishlaydi va javob qaytadi", "finally da sessiya yopiladi"],
            "hint": "Yopish eng oxirida, finally da bo'ladi.",
            "hint_ru": "Закрытие происходит в самом конце, в finally.",
            "explanation": "Sessiya so'rov boshida ochiladi, yield bilan beriladi va so'rov tugagach finally da (xato bo'lsa ham) yopiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Model va schema", "title_ru": "Модель и схема",
            "description": "Model (models.py) va schema (schemas.py) haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о модели (models.py) и схеме (schemas.py) верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Model bazadagi jadvalni tavsiflaydi",
                "Schema API'ning kirish va chiqish shaklini tavsiflaydi",
                "Ikkalasi bir xil narsa, ajratish kerak emas",
                "Schema parol xeshini avtomatik javobga qo'shadi",
            ],
            "options_ru": [
                "Модель описывает таблицу в базе",
                "Схема описывает форму входа и выхода API",
                "Это одно и то же, разделять не нужно",
                "Схема автоматически добавляет хеш пароля в ответ",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Biri baza uchun, biri API uchun.",
            "hint_ru": "Одна для базы, другая для API.",
            "explanation": "Model jadvalni, schema API shaklini tavsiflaydi. Ularni ajratish jadvaldagi maxfiy maydonlar (masalan, parol xeshi) javobga tushmasligini ta'minlaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega from_attributes", "title_ru": "Зачем from_attributes",
            "description": "ConfigDict(from_attributes=True) nima uchun kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем нужен ConfigDict(from_attributes=True)? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "U Pydantic modeliga SQLAlchemy obyektidan (atributlardan) ma'lumot o'qishni o'rgatadi. Shuning uchun endpoint bazadan olingan obyektni lug'atga aylantirmasdan to'g'ridan-to'g'ri qaytara oladi va response_model uni JSON'ga o'tkazadi.",
            "hint": "SQLAlchemy obyekti lug'at emas, atributlari bor obyekt.",
            "hint_ru": "Объект SQLAlchemy — не словарь, а объект с атрибутами.",
            "explanation": "Pydantic odatda lug'at kutadi. from_attributes=True uni oddiy obyektning atributlaridan o'qishga o'rgatadi, shuning uchun ORM obyektini qo'lda lug'atga aylantirish shart emas.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: JWT autentifikatsiya ─────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>Reja</h3>
<p>Endi API'ni <strong>JWT token</strong> bilan himoyalaymiz: foydalanuvchi ro'yxatdan o'tadi, login qilib token oladi, har so'rovda uni <code>Authorization: Bearer</code> sarlavhasida yuboradi va faqat o'z yozuvlarini ko'radi. (JWT — imzolangan, muddatli matn; server uni imzosi bo'yicha tekshiradi va sessiya saqlamaydi.)</p>
<pre><code>__PIP__</code></pre>
<p><code>pyjwt</code> token yaratadi va tekshiradi, <code>bcrypt</code> parolni xeshlaydi, <code>python-multipart</code> esa login formasini (<code>form-data</code>) o'qish uchun kerak.</p>

<h3>Model va schema'lar</h3>
<p>Foydalanuvchi jadvali qo'shiladi, yozuvga <code>owner_id</code> bog'lanadi. Parolni <strong>hech qachon ochiq saqlamang</strong>: faqat xesh (<code>password_hash</code>). Agar eski <code>notes.db</code> bor bo'lsa, uni o'chiring: <code>create_all</code> mavjud jadvalga yangi ustun qo'shmaydi.</p>
<pre><code>__MODELS__</code></pre>
<pre><code>__SCHEMAS__</code></pre>
<p><code>UserOut</code> da parol yo'q: shu sababli javobga tushmaydi. Parolga <code>max_length=72</code> qo'yildi, chunki bcrypt faqat birinchi 72 baytni ishlatadi.</p>

<h3>security.py: token va joriy foydalanuvchi</h3>
<pre><code>__SECURITY__</code></pre>
<ul>
  <li><code>OAuth2PasswordBearer(tokenUrl="token")</code> so'rovdan <code>Bearer</code> tokenni oladi va <code>/docs</code> da <em>Authorize</em> tugmasini paydo qiladi.</li>
  <li><code>get_current_user</code> — dependency: tokenni tekshiradi (imzo va muddat), undagi <code>sub</code> bo'yicha foydalanuvchini <strong>bazadan</strong> oladi. Token buzilgan, eskirgan yoki foydalanuvchi o'chirilgan bo'lsa — <code>401</code>.</li>
  <li><code>require_admin</code> — <code>get_current_user</code> ustiga qurilgan dependency: admin bo'lmasa <code>403</code>. Dependency'lar zanjir bo'lib ulanadi.</li>
  <li>Rol tokenga emas, bazadan olinadi: shu bilan foydalanuvchi admin huquqini olsa yoki yo'qotsa, o'zgarish darhol kuchga kiradi.</li>
  <li><code>SECRET_KEY</code> ni kodga yozmang, muhit o'zgaruvchisidan oling.</li>
</ul>

<h3>main.py: register, login va himoyalangan route'lar</h3>
<pre class="mermaid">
flowchart TD
  A["So'rov + Authorization: Bearer"] --> B{"get_current_user: token to'g'rimi?"}
  B -- "yo'q" --> C["401 Unauthorized"]
  B -- "ha" --> D{"Ruxsat bormi? (require_admin, egalik)"}
  D -- "yo'q" --> E["403 Forbidden"]
  D -- "ha" --> F["Endpoint ishlaydi: faqat o'z yozuvlari"]
</pre>
<pre><code>__MAIN__</code></pre>
<ul>
  <li><code>/token</code> <code>OAuth2PasswordRequestForm</code> ishlatadi: login <strong>JSON emas, form-data</strong> (<code>username</code> va <code>password</code>) bilan yuboriladi. Shu sababli <code>/docs</code> dagi <em>Authorize</em> ham ishlaydi. Javobdagi <code>access_token</code> keyingi so'rovlarda ishlatiladi.</li>
  <li>Noto'g'ri login va noto'g'ri parol uchun <strong>bir xil xabar</strong> qaytaring: hujumchi qaysi loginlar borligini bilib olmasin.</li>
  <li><code>user: models.User = Depends(get_current_user)</code> endpoint'ni himoyalaydi. <code>create_note</code> egasini (<code>owner_id</code>) tokendan olingan foydalanuvchidan qo'yadi.</li>
  <li><code>401</code> — «kimligingiz noma'lum», <code>403</code> — «kimligingiz ma'lum, lekin ruxsat yo'q». Aralashtirmang.</li>
</ul>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Tokensiz <code>/notes</code> <code>401</code> qaytaradi. <code>/docs</code> da <em>Authorize</em> tugmasi orqali login qilib, endpoint'larni tokenli sinab ko'rishingiz ham mumkin.</p>"""

_L4_TEXT_RU = """<h3>План</h3>
<p>Теперь защитим API с помощью <strong>JWT-токена</strong>: пользователь регистрируется, входит и получает токен, отправляет его в каждом запросе в заголовке <code>Authorization: Bearer</code> и видит только свои записи. (JWT — подписанная строка с ограниченным сроком; сервер проверяет её по подписи и не хранит сессию.)</p>
<pre><code>__PIP__</code></pre>
<p><code>pyjwt</code> создаёт и проверяет токены, <code>bcrypt</code> хеширует пароль, а <code>python-multipart</code> нужен для чтения формы входа (<code>form-data</code>).</p>

<h3>Модель и схемы</h3>
<p>Добавляется таблица пользователей, а к записи привязывается <code>owner_id</code>. <strong>Никогда не храните пароль в открытом виде</strong>: только хеш (<code>password_hash</code>). Если у вас остался старый <code>notes.db</code>, удалите его: <code>create_all</code> не добавляет новый столбец в существующую таблицу.</p>
<pre><code>__MODELS__</code></pre>
<pre><code>__SCHEMAS__</code></pre>
<p>В <code>UserOut</code> пароля нет, поэтому он не попадает в ответ. Для пароля стоит <code>max_length=72</code>, потому что bcrypt использует только первые 72 байта.</p>

<h3>security.py: токен и текущий пользователь</h3>
<pre><code>__SECURITY__</code></pre>
<ul>
  <li><code>OAuth2PasswordBearer(tokenUrl="token")</code> берёт <code>Bearer</code>-токен из запроса и добавляет в <code>/docs</code> кнопку <em>Authorize</em>.</li>
  <li><code>get_current_user</code> — зависимость: проверяет токен (подпись и срок) и загружает пользователя <strong>из базы</strong> по <code>sub</code>. Если токен испорчен, просрочен или пользователь удалён — <code>401</code>.</li>
  <li><code>require_admin</code> — зависимость, построенная поверх <code>get_current_user</code>: если пользователь не админ, возвращается <code>403</code>. Зависимости соединяются в цепочку.</li>
  <li>Роль берётся не из токена, а из базы: поэтому, если пользователь получил или потерял права админа, изменение действует сразу.</li>
  <li>Не пишите <code>SECRET_KEY</code> в коде, берите из переменной окружения.</li>
</ul>

<h3>main.py: регистрация, вход и защищённые маршруты</h3>
<pre class="mermaid">
flowchart TD
  A["Запрос + Authorization: Bearer"] --> B{"get_current_user: токен верный?"}
  B -- "нет" --> C["401 Unauthorized"]
  B -- "да" --> D{"Права есть? (require_admin, владелец)"}
  D -- "нет" --> E["403 Forbidden"]
  D -- "да" --> F["Эндпоинт выполняется: только свои записи"]
</pre>
<pre><code>__MAIN__</code></pre>
<ul>
  <li><code>/token</code> использует <code>OAuth2PasswordRequestForm</code>: вход отправляется <strong>не JSON, а form-data</strong> (<code>username</code> и <code>password</code>). Поэтому работает и <em>Authorize</em> в <code>/docs</code>. Полученный <code>access_token</code> используется в следующих запросах.</li>
  <li>Для неверного логина и неверного пароля возвращайте <strong>одинаковое сообщение</strong>: чтобы злоумышленник не узнал, какие логины существуют.</li>
  <li><code>user: models.User = Depends(get_current_user)</code> защищает эндпоинт. <code>create_note</code> записывает владельца (<code>owner_id</code>) из пользователя, полученного по токену.</li>
  <li><code>401</code> — «вы неизвестны», <code>403</code> — «вы известны, но прав нет». Не путайте их.</li>
</ul>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Запрос к <code>/notes</code> без токена вернёт <code>401</code>. Также можно войти через кнопку <em>Authorize</em> в <code>/docs</code> и пробовать эндпоинты уже с токеном.</p>"""

_L4_BLOCKS = dict(PIP=CMD_PIP_AUTH, MODELS=CODE_MODELS_L4, SCHEMAS=CODE_SCHEMAS_L4, SECURITY=CODE_SECURITY,
                  MAIN=CODE_MAIN_L4, CURL=CURL_L4)

LESSON_4 = {
    "order": 3,
    "title": "4-JWT autentifikatsiya va faqat o'z yozuvlari",
    "title_ru": "4-JWT-аутентификация и доступ только к своим записям",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": CODE_SECURITY,
    "code_content_ru": CODE_SECURITY,
    "code_language": "python",
    "sample": {
        "title": "Namuna: JWT va OAuth2PasswordBearer bilan himoyalangan API",
        "title_ru": "Пример: API под защитой JWT и OAuth2PasswordBearer",
        "description": "Register, /token, get_current_user, require_admin va faqat o'z yozuvlariga ruxsat.",
        "description_ru": "Регистрация, /token, get_current_user, require_admin и доступ только к своим записям.",
        "sample_type": "code",
        "code_files": [
            {"filename": "models.py", "language": "python", "code": CODE_MODELS_L4},
            {"filename": "schemas.py", "language": "python", "code": CODE_SCHEMAS_L4},
            {"filename": "security.py", "language": "python", "code": CODE_SECURITY},
            {"filename": "main.py", "language": "python", "code": CODE_MAIN_L4},
        ],
    },
    "exercises": [
        {
            "title": "Tokensiz so'rov", "title_ru": "Запрос без токена",
            "description": "get_current_user bilan himoyalangan endpoint'ga tokensiz so'rov yuborilsa qaysi kod qaytadi?",
            "description_ru": "Какой код вернётся при запросе без токена к эндпоинту с get_current_user?",
            "exercise_type": "multiple_choice",
            "options": ["200", "401", "403", "404"],
            "options_ru": ["200", "401", "403", "404"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Foydalanuvchi kimligi noma'lum.",
            "hint_ru": "Личность пользователя неизвестна.",
            "explanation": "Token yo'q bo'lsa foydalanuvchi autentifikatsiyadan o'tmagan: 401. 403 esa kimligi ma'lum, lekin ruxsati yo'q holat uchun.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Parolni xeshlash", "title_ru": "Хеширование пароля",
            "description": "Bu darsda parolni xeshlash uchun ishlatilgan kutubxona: ___",
            "description_ru": "Библиотека, использованная в этом уроке для хеширования пароля: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "bcrypt",
            "hint": "Nomida «crypt» bor.",
            "hint_ru": "В названии есть «crypt».",
            "explanation": "bcrypt parolni qaytarib bo'lmaydigan xeshga aylantiradi (bcrypt.hashpw) va tekshiradi (bcrypt.checkpw).",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Login tartibi", "title_ru": "Порядок входа",
            "description": "POST /token ishlash tartibini joylashtiring.",
            "description_ru": "Расположите порядок работы POST /token.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Form-data'dan username va password olinadi", "Foydalanuvchi bazadan topiladi", "Parol xeshi tekshiriladi", "access_token yaratilib qaytariladi"],
            "drag_items_ru": ["Из form-data берутся username и password", "Пользователь ищется в базе", "Проверяется хеш пароля", "Создаётся и возвращается access_token"],
            "correct_order": ["Form-data'dan username va password olinadi", "Foydalanuvchi bazadan topiladi", "Parol xeshi tekshiriladi", "access_token yaratilib qaytariladi"],
            "hint": "Token faqat parol tasdiqlangandan keyin beriladi.",
            "hint_ru": "Токен выдаётся только после подтверждения пароля.",
            "explanation": "Avval ma'lumot olinadi, foydalanuvchi va parol tekshiriladi; faqat shundan keyin token yaratiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Dependency zanjiri", "title_ru": "Цепочка зависимостей",
            "description": "get_current_user va require_admin haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о get_current_user и require_admin верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "require_admin get_current_user ga tayanadi",
                "Admin bo'lmagan foydalanuvchi require_admin da 403 oladi",
                "Rol har so'rovda bazadan olinadi",
                "Rol har doim tokenning ichiga yoziladi va bazaga qaralmaydi",
            ],
            "options_ru": [
                "require_admin опирается на get_current_user",
                "Не-админ получает 403 в require_admin",
                "Роль берётся из базы при каждом запросе",
                "Роль всегда записана в токене, и в базу не обращаются",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Bu darsda rol tokendan emas, bazadan olinadi.",
            "hint_ru": "В этом уроке роль берётся не из токена, а из базы.",
            "explanation": "require_admin get_current_user natijasidan foydalanadi; admin bo'lmasa 403. Rol bazadan olingani uchun admin huquqining o'zgarishi darhol kuchga kiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega bir xil xabar", "title_ru": "Зачем одинаковое сообщение",
            "description": "Nega noto'g'ri login va noto'g'ri parol uchun bir xil xabar qaytariladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем для неверного логина и неверного пароля возвращают одинаковое сообщение? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Agar xabarlar farq qilsa, hujumchi qaysi loginlar mavjudligini bilib oladi va faqat paroli taxmin qiladi. Bir xil xabar bu ma'lumotni yashiradi.",
            "hint": "Hujumchi javobdan nimani bilib olishi mumkin?",
            "hint_ru": "Что злоумышленник может узнать из ответа?",
            "explanation": "Turli xabarlar login mavjudligini oshkor qiladi (user enumeration). Bir xil javob hujumchiga hech qanday ma'lumot bermaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: CORS, testlar, Postman ───────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Muammo: brauzer so'rovni to'sib qo'yadi</h3>
<p>Frontend <code>http://localhost:8080</code> da, API esa <code>http://127.0.0.1:8000</code> da ishlayotgan bo'lsin. Origin (manba) — protokol, domen va portning birikmasi; bular farq qilsa, manbalar <strong>turli</strong> hisoblanadi. Brauzer xavfsizlik uchun (same-origin siyosati) boshqa manbaga yuborilgan so'rovning <em>javobini</em> JavaScript'ga bermaydi, agar server buni aniq ruxsat etmasa. Konsolda <code>blocked by CORS policy</code> xatosini ko'rasiz. Bu server buzilganini bildirmaydi: so'rov yetib boradi, lekin brauzer javobni yashiradi, shuning uchun uni <strong>serverda</strong> to'g'rilaymiz.</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Brauzer (8080)
  participant S as FastAPI (8000)
  B->>S: OPTIONS /notes (Origin, Request-Headers)
  S-->>B: 200 + access-control-allow-origin va allow-headers
  B->>S: GET /notes (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p><code>Authorization</code> sarlavhasi yoki JSON <code>Content-Type</code> bilan so'rovdan oldin brauzer o'zi <code>OPTIONS</code> (preflight) so'rovi yuboradi. Server ruxsat bermasa, asl so'rov yuborilmaydi.</p>

<h3>CORSMiddleware</h3>
<p>FastAPI'da CORS tayyor middleware bilan yoqiladi:</p>
<pre><code>__CORS__</code></pre>
<ul>
  <li><code>allow_origins</code> — ruxsat etilgan manbalar. Aniq manzillarni yozing; <code>["*"]</code> (hamma) tokenli API uchun xavfli.</li>
  <li><code>allow_headers</code> — <code>Authorization</code> ni qo'shmasangiz, tokenli so'rov preflight'dan o'tmaydi.</li>
  <li><code>allow_methods</code> — ruxsat etilgan metodlar.</li>
</ul>
<p>Preflight'ni qo'lda sinang:</p>
<pre><code>__PRE__</code></pre>
<p>Javobda <code>access-control-allow-origin: http://localhost:8080</code> bo'lishi kerak; <code>http://evil.example</code> uchun bu sarlavha qaytmaydi.</p>

<h3>Frontend: fetch va token</h3>
<p>Frontend login javobidagi <code>access_token</code> ni <code>localStorage</code> da saqlaydi va har <code>fetch</code> so'roviga <code>Authorization: Bearer</code> sarlavhasi bilan qo'shadi. Server <code>401</code> qaytarsa, eski token o'chiriladi va foydalanuvchi qayta kiradi. Login <code>form-data</code> bilan yuboriladi (<code>URLSearchParams</code>). Ogohlantirish: <code>localStorage</code> dagi token sahifadagi har qanday skriptga ko'rinadi (XSS xavfi); o'quv loyihasi uchun yetarli. To'liq frontend kodi 6-darsda.</p>

<h3>Testlar: TestClient va dependency_overrides</h3>
<p><code>TestClient</code> serverni ishga tushirmasdan ilovaga so'rov yuboradi. Testlar <em>haqiqiy</em> <code>notes.db</code> ga tegmasligi kerak, shuning uchun <code>get_db</code> dependency'sini <code>app.dependency_overrides</code> bilan vaqtinchalik bazaga almashtiramiz (xotiradagi SQLite). <code>StaticPool</code> barcha ulanishlar bitta xotiradagi bazani ko'rishini ta'minlaydi. Har test oldidan jadvallar qayta yaratiladi: testlar bir-biriga bog'liq bo'lmaydi.</p>
<pre><code>__TESTS__</code></pre>
<ul>
  <li>Login testda <code>data=</code> (form-data), ro'yxatdan o'tish esa <code>json=</code> bilan yuboriladi.</li>
  <li>Eskirgan tokenni <code>jwt.encode</code> bilan o'tgan <code>exp</code> qo'yib yasaymiz: kutish shart emas.</li>
  <li>Admin foydalanuvchini to'g'ridan-to'g'ri test bazasiga yozamiz.</li>
</ul>
<pre><code>__PIPTEST__</code></pre>
<p><code>pytest.ini</code> dagi <code>pythonpath = .</code> testlarga <code>main</code> va <code>security</code> modullarini import qilishga imkon beradi.</p>

<h3>Postman</h3>
<ol>
  <li><strong>POST</strong> <code>/token</code>: Body → <em>x-www-form-urlencoded</em> (<code>username</code>, <code>password</code>). Bu yerda JSON emas, form-data ishlatiladi.</li>
  <li>Tokenni avtomatik saqlash uchun so'rovning <em>Tests</em> yorlig'iga yozing:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>Himoyalangan so'rovda <em>Authorization</em> yorlig'i → Type: <em>Bearer Token</em> → qiymat: <code>{{token}}</code>.</li>
</ol>"""

_L5_TEXT_RU = """<h3>Проблема: браузер блокирует запрос</h3>
<p>Пусть фронтенд работает на <code>http://localhost:8080</code>, а API — на <code>http://127.0.0.1:8000</code>. Origin (источник) — это сочетание протокола, домена и порта; если они отличаются, источники <strong>разные</strong>. В целях безопасности (политика same-origin) браузер не отдаёт JavaScript <em>ответ</em> на запрос к другому источнику, пока сервер явно этого не разрешит. В консоли вы увидите ошибку <code>blocked by CORS policy</code>. Это не значит, что сервер сломан: запрос доходит, но браузер скрывает ответ, поэтому исправляем её <strong>на сервере</strong>.</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Браузер (8080)
  participant S as FastAPI (8000)
  B->>S: OPTIONS /notes (Origin, Request-Headers)
  S-->>B: 200 + access-control-allow-origin и allow-headers
  B->>S: GET /notes (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p>Перед запросом с заголовком <code>Authorization</code> или JSON в <code>Content-Type</code> браузер сам отправляет <code>OPTIONS</code> (preflight). Если сервер не разрешил, основной запрос не отправляется.</p>

<h3>CORSMiddleware</h3>
<p>В FastAPI CORS включается готовым middleware:</p>
<pre><code>__CORS__</code></pre>
<ul>
  <li><code>allow_origins</code> — разрешённые источники. Указывайте конкретные адреса; <code>["*"]</code> (все) опасно для API с токенами.</li>
  <li><code>allow_headers</code> — не забудьте добавить <code>Authorization</code>, иначе запрос с токеном не пройдёт preflight.</li>
  <li><code>allow_methods</code> — разрешённые методы.</li>
</ul>
<p>Проверьте preflight вручную:</p>
<pre><code>__PRE__</code></pre>
<p>В ответе должен быть <code>access-control-allow-origin: http://localhost:8080</code>; для <code>http://evil.example</code> этот заголовок не вернётся.</p>

<h3>Фронтенд: fetch и токен</h3>
<p>Фронтенд сохраняет <code>access_token</code> из ответа на вход в <code>localStorage</code> и добавляет его в каждый запрос <code>fetch</code> через заголовок <code>Authorization: Bearer</code>. Если сервер вернул <code>401</code>, старый токен удаляется и пользователь входит заново. Вход отправляется как <code>form-data</code> (<code>URLSearchParams</code>). Предупреждение: токен в <code>localStorage</code> виден любому скрипту на странице (риск XSS); для учебного проекта этого достаточно. Полный код фронтенда — в уроке 6.</p>

<h3>Тесты: TestClient и dependency_overrides</h3>
<p><code>TestClient</code> отправляет запросы приложению без запуска сервера. Тесты не должны трогать <em>настоящий</em> <code>notes.db</code>, поэтому мы временно подменяем зависимость <code>get_db</code> через <code>app.dependency_overrides</code> на временную базу (SQLite в памяти). <code>StaticPool</code> гарантирует, что все подключения видят одну и ту же базу в памяти. Перед каждым тестом таблицы создаются заново: тесты не зависят друг от друга.</p>
<pre><code>__TESTS__</code></pre>
<ul>
  <li>Вход в тесте отправляется через <code>data=</code> (form-data), а регистрация — через <code>json=</code>.</li>
  <li>Просроченный токен создаём через <code>jwt.encode</code> с уже прошедшим <code>exp</code>: ждать не нужно.</li>
  <li>Админа записываем прямо в тестовую базу.</li>
</ul>
<pre><code>__PIPTEST__</code></pre>
<p><code>pythonpath = .</code> в <code>pytest.ini</code> позволяет тестам импортировать модули <code>main</code> и <code>security</code>.</p>

<h3>Postman</h3>
<ol>
  <li><strong>POST</strong> <code>/token</code>: Body → <em>x-www-form-urlencoded</em> (<code>username</code>, <code>password</code>). Здесь используется form-data, а не JSON.</li>
  <li>Чтобы сохранять токен автоматически, на вкладке <em>Tests</em> запроса напишите:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>В защищённом запросе откройте вкладку <em>Authorization</em> → Type: <em>Bearer Token</em> → значение: <code>{{token}}</code>.</li>
</ol>"""

_L5_BLOCKS = dict(CORS=CODE_CORS_L5, PRE=CURL_PREFLIGHT, TESTS=CODE_TESTS_L5, PIPTEST=CMD_PIP_TEST, POSTMAN=POSTMAN_SCRIPT)

LESSON_5 = {
    "order": 4,
    "title": "5-CORS, pytest testlari va Postman",
    "title_ru": "5-CORS, тесты pytest и Postman",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": CODE_CORS_L5,
    "code_content_ru": CODE_CORS_L5,
    "code_language": "python",
    "sample": {
        "title": "Namuna: CORSMiddleware va 7 ta pytest testi",
        "title_ru": "Пример: CORSMiddleware и 7 тестов pytest",
        "description": "CORS sozlamasi, TestClient va dependency_overrides bilan yozilgan testlar.",
        "description_ru": "Настройка CORS и тесты на TestClient и dependency_overrides.",
        "sample_type": "code",
        "code_files": [
            {"filename": "main.py", "language": "python", "code": CODE_MAIN_L5},
            {"filename": "tests/test_api.py", "language": "python", "code": CODE_TESTS_L5},
            {"filename": "pytest.ini", "language": "ini", "code": PYTEST_INI},
            {"filename": "api.js", "language": "javascript", "code": API_JS},
        ],
    },
    "exercises": [
        {
            "title": "Preflight metodi", "title_ru": "Метод preflight",
            "description": "Brauzer preflight uchun qaysi HTTP metodini yuboradi? ___",
            "description_ru": "Какой HTTP-метод браузер отправляет для preflight? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "OPTIONS",
            "hint": "U serverdan «nimalarga ruxsat bor?» deb so'raydi.",
            "hint_ru": "Он спрашивает сервер: «что разрешено?».",
            "explanation": "Preflight — OPTIONS so'rovi. Server access-control-allow-* sarlavhalari bilan javob beradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Origin nima", "title_ru": "Что такое origin",
            "description": "Qaysi ikki manzil bir xil origin (manba) hisoblanadi?",
            "description_ru": "Какие два адреса считаются одним origin (источником)?",
            "exercise_type": "multiple_choice",
            "options": [
                "http://localhost:8080 va http://localhost:8000",
                "http://localhost:8080 va https://localhost:8080",
                "http://localhost:8080/a va http://localhost:8080/b",
                "http://localhost:8080 va http://127.0.0.1:8080",
            ],
            "options_ru": [
                "http://localhost:8080 и http://localhost:8000",
                "http://localhost:8080 и https://localhost:8080",
                "http://localhost:8080/a и http://localhost:8080/b",
                "http://localhost:8080 и http://127.0.0.1:8080",
            ],
            "correct_answers": "C", "is_multiple_select": False,
            "hint": "Origin = protokol + domen + port; yo'l (path) hisobga olinmaydi.",
            "hint_ru": "Origin = протокол + домен + порт; путь (path) не учитывается.",
            "explanation": "Faqat yo'l farq qilsa origin bir xil. Port, protokol yoki domen (hatto localhost va 127.0.0.1) farq qilsa, origin turli.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Test sozlash tartibi", "title_ru": "Порядок настройки теста",
            "description": "Har test uchun toza muhit tayyorlash tartibini joylashtiring.",
            "description_ru": "Расположите порядок подготовки чистой среды для каждого теста.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Jadvallarni o'chirib qayta yaratish", "get_db ni dependency_overrides bilan almashtirish", "TestClient(app) bilan so'rov yuborish", "Testdan keyin overrides ni tozalash"],
            "drag_items_ru": ["Удалить и заново создать таблицы", "Подменить get_db через dependency_overrides", "Отправить запрос через TestClient(app)", "После теста очистить overrides"],
            "correct_order": ["Jadvallarni o'chirib qayta yaratish", "get_db ni dependency_overrides bilan almashtirish", "TestClient(app) bilan so'rov yuborish", "Testdan keyin overrides ni tozalash"],
            "hint": "Avval tayyorgarlik, keyin so'rov, oxirida tozalash.",
            "hint_ru": "Сначала подготовка, потом запрос, в конце очистка.",
            "explanation": "Fixture avval toza baza va override ni tayyorlaydi, test so'rov yuboradi, keyin override tozalanadi: testlar bir-biriga ta'sir qilmaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi sozlamalar kerak", "title_ru": "Какие настройки нужны",
            "description": "Frontend Authorization sarlavhasi bilan so'rov yuborishi uchun CORSMiddleware'da nima bo'lishi kerak? (Bir nechta javob)",
            "description_ru": "Что должно быть в CORSMiddleware, чтобы фронтенд мог отправлять запрос с заголовком Authorization? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "allow_origins ichida frontend manzili",
                "allow_headers ichida Authorization",
                "Frontend kodida CORS xatosini try/catch bilan o'rash",
                "Tokenni URL'ga qo'shish",
            ],
            "options_ru": [
                "Адрес фронтенда в allow_origins",
                "Authorization в allow_headers",
                "Обернуть ошибку CORS во фронтенде в try/catch",
                "Добавить токен в URL",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Ikkala sozlama ham serverda qilinadi.",
            "hint_ru": "Обе настройки делаются на сервере.",
            "explanation": "Server frontend origin'ini ham, Authorization sarlavhasini ham aniq ruxsat etishi kerak. try/catch CORS blokini olib tashlamaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega dependency_overrides", "title_ru": "Зачем dependency_overrides",
            "description": "Testlarda nega get_db ni dependency_overrides bilan almashtiramiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем в тестах мы подменяем get_db через dependency_overrides? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Testlar haqiqiy bazaga tegmasligi va bir-biriga bog'liq bo'lmasligi kerak. get_db ni vaqtinchalik xotiradagi bazaga almashtirsak, har test toza bazada ishlaydi, haqiqiy ma'lumot buzilmaydi va test tez ishlaydi.",
            "hint": "Test haqiqiy foydalanuvchi ma'lumotlarini o'zgartirib yuborsa nima bo'ladi?",
            "hint_ru": "Что будет, если тест изменит данные настоящих пользователей?",
            "explanation": "dependency_overrides endpoint kodini o'zgartirmasdan bazani almashtirishga imkon beradi: testlar izolyatsiyalangan va xavfsiz bo'ladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>Endpoint'lar:</strong> path va query parametrlari, <code>HTTPException</code>, avtomatik <code>/docs</code>.</li>
  <li><strong>Pydantic:</strong> <code>BaseModel</code>, kiruvchi va chiquvchi model, <code>response_model</code>, <code>422</code> xatolari.</li>
  <li><strong>Baza:</strong> <code>SQLAlchemy</code>, <code>Depends(get_db)</code>, <code>from_attributes</code>.</li>
  <li><strong>JWT:</strong> <code>OAuth2PasswordBearer</code>, <code>get_current_user</code>, parol xeshi, 401 va 403, faqat o'z yozuvlari.</li>
  <li><strong>CORS va testlar:</strong> <code>CORSMiddleware</code>, <code>TestClient</code>, <code>dependency_overrides</code>, Postman.</li>
</ul>

<h3>Production'ga chiqarishdan oldin</h3>
<ul>
  <li><code>JWT_SECRET_KEY</code> ni kodga yozmang, muhit o'zgaruvchisidan oling.</li>
  <li>Serverni <code>--reload</code> siz ishga tushiring: <code>uvicorn main:app --host 0.0.0.0 --port 8000</code>.</li>
  <li><code>allow_origins</code> ichida faqat haqiqiy frontend manzili (HTTPS).</li>
  <li>SQLite o'rniga PostgreSQL ishlating: bazaga ulanish manzili (<code>DATABASE_URL</code>) muhit o'zgaruvchisida bo'lsin, jadval o'zgarishlari uchun Alembic ishlating.</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Pastda frontend: <code>index.html</code> va <code>api.js</code>. Serverni <code>uvicorn main:app --reload</code> bilan, frontendni esa uning papkasida <code>python -m http.server 8080</code> bilan ishga tushiring: shunda manzil CORS'da ruxsat etilgan <code>http://localhost:8080</code> bilan mos keladi. Server kodi (database, models, schemas, security, main va tests) 3–5-darslardagi bilan bir xil.</p>
<pre><code>__JS__</code></pre>
<pre><code>__HTML__</code></pre>
<p>Keyingi bosqich — vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, o'z mavzuingizdagi yozuvlar (masalan, vazifalar yoki xarajatlar) uchun shu usulda tokenli API yozing.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>Эндпоинты:</strong> path- и query-параметры, <code>HTTPException</code>, автоматический <code>/docs</code>.</li>
  <li><strong>Pydantic:</strong> <code>BaseModel</code>, входная и выходная модель, <code>response_model</code>, ошибки <code>422</code>.</li>
  <li><strong>База:</strong> <code>SQLAlchemy</code>, <code>Depends(get_db)</code>, <code>from_attributes</code>.</li>
  <li><strong>JWT:</strong> <code>OAuth2PasswordBearer</code>, <code>get_current_user</code>, хеш пароля, 401 и 403, доступ только к своим записям.</li>
  <li><strong>CORS и тесты:</strong> <code>CORSMiddleware</code>, <code>TestClient</code>, <code>dependency_overrides</code>, Postman.</li>
</ul>

<h3>Перед выходом в production</h3>
<ul>
  <li>Не храните <code>JWT_SECRET_KEY</code> в коде, берите из переменной окружения.</li>
  <li>Запускайте сервер без <code>--reload</code>: <code>uvicorn main:app --host 0.0.0.0 --port 8000</code>.</li>
  <li>В <code>allow_origins</code> только настоящий адрес фронтенда (HTTPS).</li>
  <li>Вместо SQLite используйте PostgreSQL: адрес подключения (<code>DATABASE_URL</code>) держите в переменной окружения, а для изменений таблиц применяйте Alembic.</li>
</ul>

<h3>Готовое решение</h3>
<p>Ниже фронтенд: <code>index.html</code> и <code>api.js</code>. Запустите сервер командой <code>uvicorn main:app --reload</code>, а фронтенд — командой <code>python -m http.server 8080</code> в его папке: тогда адрес совпадёт с разрешённым в CORS <code>http://localhost:8080</code>. Код сервера (database, models, schemas, security, main и tests) такой же, как в уроках 3–5.</p>
<pre><code>__JS__</code></pre>
<pre><code>__HTML__</code></pre>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, напишите API с токеном для записей на свою тему (например, задачи или расходы) тем же способом.</p>"""

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: tokenli Notes API + oddiy frontend",
    "title_ru": "6-Повторение: Notes API с токеном + простой фронтенд",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, JS=API_JS, HTML=INDEX_HTML),
    "text_content_ru": _fill(_L6_TEXT_RU, JS=API_JS, HTML=INDEX_HTML),
    "code_content": API_JS,
    "code_content_ru": API_JS,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: tokenli Notes API (to'liq loyiha)",
        "title_ru": "Пример: Notes API с токеном (полный проект)",
        "description": "Server kodi, testlar va fetch bilan ishlaydigan oddiy frontend.",
        "description_ru": "Код сервера, тесты и простой фронтенд на fetch.",
        "sample_type": "code",
        "code_files": [
            {"filename": "database.py", "language": "python", "code": CODE_DATABASE},
            {"filename": "models.py", "language": "python", "code": CODE_MODELS_L4},
            {"filename": "schemas.py", "language": "python", "code": CODE_SCHEMAS_L4},
            {"filename": "security.py", "language": "python", "code": CODE_SECURITY},
            {"filename": "main.py", "language": "python", "code": CODE_MAIN_L5},
            {"filename": "tests/test_api.py", "language": "python", "code": CODE_TESTS_L5},
            {"filename": "pytest.ini", "language": "ini", "code": PYTEST_INI},
            {"filename": "api.js", "language": "javascript", "code": API_JS},
            {"filename": "index.html", "language": "html", "code": INDEX_HTML},
        ],
    },
    "task": {
        "task_title": "Loyiha: tokenli yozuvlar API'si (FastAPI) + oddiy frontend",
        "task_title_ru": "Проект: API записей с токеном (FastAPI) + простой фронтенд",
        "task_description": "O'zingiz tanlagan mavzu (vazifalar, xarajatlar, kitoblar...) uchun FastAPI API yozing: foydalanuvchi ro'yxatdan o'tadi, kiradi va faqat o'z yozuvlarini boshqaradi. Admin hammasini ko'radi. Oddiy HTML/JavaScript frontend login qiladi va yozuvlar ro'yxatini ko'rsatadi.",
        "task_description_ru": "Напишите API на FastAPI для выбранной вами темы (задачи, расходы, книги...): пользователь регистрируется, входит и управляет только своими записями. Админ видит всё. Простой HTML/JavaScript-фронтенд выполняет вход и показывает список записей.",
        "task_requirements": (
            "1) Pydantic modellari (BaseModel): kiruvchi va chiquvchi model, response_model va kamida bitta cheklov (StringConstraints). "
            "2) SQLAlchemy bazasi va Depends(get_db) bilan yozuv yaratish, ro'yxat va o'chirish endpoint'lari. "
            "3) POST /register va POST /token (JWT, OAuth2PasswordBearer): parol bcrypt xeshi bilan saqlanadi. "
            "4) get_current_user bilan himoya, faqat o'z yozuvlari (403) va require_admin bilan faqat admin uchun endpoint. "
            "5) CORSMiddleware: faqat frontend manzili ruxsat etilgan, Authorization sarlavhasi bilan. "
            "6) fetch bilan oddiy frontend: login va yozuvlar ro'yxati, token localStorage'da. "
            "7) TestClient va dependency_overrides bilan pytest'da kamida 3 ta test."
        ),
        "task_requirements_ru": (
            "1) Модели Pydantic (BaseModel): входная и выходная модель, response_model и хотя бы одно ограничение (StringConstraints). "
            "2) Эндпоинты создания, списка и удаления записей на базе SQLAlchemy и Depends(get_db). "
            "3) POST /register и POST /token (JWT, OAuth2PasswordBearer): пароль хранится как хеш bcrypt. "
            "4) Защита через get_current_user, доступ только к своим записям (403) и эндпоинт только для админа через require_admin. "
            "5) CORSMiddleware: разрешён только адрес фронтенда, с заголовком Authorization. "
            "6) Простой фронтенд на fetch: вход и список записей, токен в localStorage. "
            "7) Не менее 3 тестов в pytest с TestClient и dependency_overrides."
        ),
        "task_technologies": "Python, FastAPI, Pydantic, SQLAlchemy, JavaScript",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Hammasini bog'lang", "title_ru": "Соедините всё вместе",
            "description": "Qaysi variant «token bilan ishlovchi to'liq API»ning to'g'ri tartibini ko'rsatadi?",
            "description_ru": "Какой вариант показывает верный порядок работы API с токеном?",
            "exercise_type": "multiple_choice",
            "options": [
                "login → access_token → Authorization: Bearer bilan himoyalangan so'rov",
                "himoyalangan so'rov → login → token",
                "token → login → parol",
                "parolni har so'rovda URL ichida yuborish",
            ],
            "options_ru": [
                "вход → access_token → защищённый запрос с Authorization: Bearer",
                "защищённый запрос → вход → токен",
                "токен → вход → пароль",
                "отправлять пароль в URL при каждом запросе",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Token faqat login'dan keyin paydo bo'ladi.",
            "hint_ru": "Токен появляется только после входа.",
            "explanation": "Parol faqat login paytida yuboriladi, keyin barcha so'rovlar access token bilan ketadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Testlarni ishga tushirish", "title_ru": "Запуск тестов",
            "description": "Loyiha papkasida testlarni ishga tushiradigan buyruq: ___",
            "description_ru": "Команда запуска тестов в папке проекта: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "pytest",
            "hint": "Kutubxona nomi bilan bir xil.",
            "hint_ru": "Совпадает с названием библиотеки.",
            "explanation": "pytest pytest.ini dagi sozlamalar bo'yicha tests/ papkasidagi barcha test fayllarini topadi va ishga tushiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Loyihani tekshirish", "title_ru": "Проверка проекта",
            "description": "Loyihangiz xavfsiz ekanini qaysi tekshiruvlar bilan isbotlaysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Какими проверками вы докажете, что ваш проект безопасен? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Tokensiz so'rov 401 qaytarishini, boshqa foydalanuvchining yozuvi uchun 403 kelishini, oddiy foydalanuvchi admin endpoint'iga kira olmasligini (403) va CORS faqat frontend manziliga ruxsat berishini TestClient bilan tekshiraman.",
            "hint": "401, 403 va CORS holatlarini o'ylab ko'ring.",
            "hint_ru": "Подумайте о случаях 401, 403 и CORS.",
            "explanation": "Testlar himoyaning har qatlamini tekshiradi: token, egalik, rol va CORS. Shu holatlar bo'lsa, loyiha asosiy xavfsizlik talablarini qoplaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
