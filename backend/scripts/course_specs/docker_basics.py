"""Course spec: Docker asoslari — 6 lessons, UZ + RU.

A small FastAPI Notes API is packaged in stages: docker run basics -> Dockerfile ->
ports/env/volumes -> Compose with PostgreSQL -> hardened image + CI -> project. Every file and
command below was run on a real Docker engine (Docker 29, Compose v5) by the verification script
before a lesson text may use it. Host ports in the lessons are the usual ones (8000, 5432); the
verification used other host ports (18080, 15432) so it could not collide with other containers.
API messages are English so the code is identical in UZ and RU.
"""
from __future__ import annotations

# ── Stage files (single source of truth for lessons 1-6) ─────────────────────

REQUIREMENTS_L2 = '''fastapi==0.136.0
uvicorn==0.44.0
'''

REQUIREMENTS_L4 = '''fastapi==0.136.0
uvicorn==0.44.0
psycopg[binary]==3.2.9
'''

MAIN_SIMPLE = '''import os
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="Notes API")

DATA_FILE = Path(os.environ.get("DATA_DIR", "/data")) / "visits.txt"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": os.environ.get("GREETING", "Hello from Docker")}


@app.get("/visits")
def visits():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    count = int(DATA_FILE.read_text()) + 1 if DATA_FILE.exists() else 1
    DATA_FILE.write_text(str(count))
    return {"visits": count}
'''

MAIN_DB = '''import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel, Field

DATABASE_URL = os.environ["DATABASE_URL"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, text TEXT NOT NULL)")
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


class NoteIn(BaseModel):
    text: str = Field(min_length=3, max_length=200)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes")
def list_notes():
    with psycopg.connect(DATABASE_URL) as conn:
        rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
    return [{"id": row[0], "text": row[1]} for row in rows]


@app.post("/notes", status_code=201)
def create_note(data: NoteIn):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute("INSERT INTO notes (text) VALUES (%s) RETURNING id", (data.text,)).fetchone()
    return {"id": row[0], "text": data.text}
'''

DOCKERFILE_L2 = '''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

DOCKERIGNORE = '''__pycache__/
*.pyc
.venv/
.git/
.env
.github/
compose.yaml
Dockerfile
.dockerignore
'''

COMPOSE_L4 = '''services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: notes
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-notes-dev-password}
      POSTGRES_DB: notes
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notes -d notes"]
      interval: 3s
      timeout: 3s
      retries: 10

  api:
    build: .
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql://notes:${POSTGRES_PASSWORD:-notes-dev-password}@db:5432/notes
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 3s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
'''

DOCKERFILE_L5 = '''FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \\
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

COMPOSE_L5 = '''services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: notes
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
      POSTGRES_DB: notes
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notes -d notes"]
      interval: 3s
      timeout: 3s
      retries: 10
    restart: unless-stopped

  api:
    build: .
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql://notes:${POSTGRES_PASSWORD}@db:5432/notes
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

volumes:
  pgdata:
'''

ENV_EXAMPLE = '''POSTGRES_PASSWORD=change-me-to-a-long-random-value
API_PORT=8000
'''

WORKFLOW_YML = '''name: docker

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create .env
        run: echo "POSTGRES_PASSWORD=ci-only-password" > .env
      - name: Build and start the stack
        run: docker compose up -d --build --wait
      - name: Smoke test
        run: |
          curl --fail http://127.0.0.1:8000/health
          curl --fail -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" -d '{"text": "from CI"}'
          curl --fail http://127.0.0.1:8000/notes
      - name: Logs on failure
        if: failure()
        run: docker compose logs
      - name: Stop
        if: always()
        run: docker compose down -v
'''

CMD_L1_RUN = '''docker run --rm python:3.12-slim python -c "print('salom, Docker')"
docker run -d --name my-postgres -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:16-alpine
docker ps
docker logs my-postgres
docker exec -it my-postgres psql -U postgres -c "SELECT version();"
docker stop my-postgres
docker rm my-postgres
'''

CMD_L1_LIST = '''docker images
docker ps -a
docker rm -f my-postgres
'''

CMD_L2_BUILD = '''docker build -t notes-api:1.0 .
docker run -d --name notes-api -p 8000:8000 notes-api:1.0
curl http://127.0.0.1:8000/health
docker logs notes-api
'''

CMD_L3_RUN = '''docker run -d --name notes-api -p 8000:8000 -e GREETING="Salom, Docker" notes-api:1.0
curl http://127.0.0.1:8000/
docker rm -f notes-api

docker run -d --name notes-api -p 8000:8000 -v visits:/data notes-api:1.0
curl http://127.0.0.1:8000/visits
curl http://127.0.0.1:8000/visits
docker rm -f notes-api
docker run -d --name notes-api -p 8000:8000 -v visits:/data notes-api:1.0
curl http://127.0.0.1:8000/visits
'''

CMD_L3_VOLUME = '''docker volume ls
docker volume inspect visits
docker volume rm visits
'''

CMD_L3_ENVFILE = '''docker run -d --name notes-api -p 8000:8000 --env-file .env notes-api:1.0
'''

CMD_L4_UP = '''docker compose up -d --build --wait
docker compose ps
curl -X POST http://127.0.0.1:8000/notes -H "Content-Type: application/json" -d '{"text": "buy bread"}'
curl http://127.0.0.1:8000/notes
docker compose logs api
docker compose exec db psql -U notes -d notes -c "SELECT * FROM notes;"
docker compose down
docker compose up -d --wait
curl http://127.0.0.1:8000/notes
docker compose down -v
'''

CMD_L5_BUILD = '''docker build -t notes-api:slim .
docker images notes-api
docker compose up -d --build --wait
docker compose exec api id
docker compose ps
'''


COURSE = {
    "title": "Docker asoslari",
    "title_ru": "Основы Docker",
    "description": (
        "Docker bilan ilovani konteynerga o'rashni o'rganasiz: image va konteyner, Dockerfile, port, muhit o'zgaruvchilari va "
        "volume, Docker Compose bilan API + PostgreSQL, xavfsiz image va GitHub Actions. "
        "Kurs oxirida o'z API'ngizni Dockerfile va compose.yaml bilan bir buyruqda ishga tushadigan qilasiz."
    ),
    "description_ru": (
        "Вы научитесь упаковывать приложение в контейнер с помощью Docker: образ и контейнер, Dockerfile, порты, переменные "
        "окружения и тома, Docker Compose для API + PostgreSQL, безопасный образ и GitHub Actions. "
        "В конце курса вы сделаете так, чтобы ваш API запускался одной командой через Dockerfile и compose.yaml."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 11,
    "prerequisite_course_id": 45,
    "display_order": 603,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


# ── 1-dars: Docker nima ──────────────────────────────────────────────────────

_L1_TEXT_UZ = """<h3>Muammo: «menda ishlayapti»</h3>
<p>Siz yozgan API sizning kompyuteringizda ishlaydi: Python versiyasi, kutubxonalar, PostgreSQL, sozlamalar sizda to'g'ri. Jamoadoshingiz yoki server esa boshqa versiya, boshqa operatsion tizim va boshqa sozlamalarga ega, natijada «menda ishlayapti» degan gap paydo bo'ladi. <strong>Docker</strong> ilovani <em>kerakli hamma narsasi bilan</em> (Python, kutubxonalar, fayllar, buyruq) bitta paketga o'raydi va uni istalgan joyda bir xil ishga tushiradi.</p>

<h3>Image va konteyner</h3>
<ul>
  <li><strong>Image</strong> — ilovaning o'zgarmas «qolipi»: fayllar va ishga tushirish buyrug'i. U faqat o'qiladi.</li>
  <li><strong>Konteyner</strong> — image'dan ishga tushirilgan <em>jarayon</em>. Bitta image'dan bir nechta konteyner yaratish mumkin, ular bir-biriga xalaqit bermaydi.</li>
  <li><strong>Registry</strong> (masalan, Docker Hub) — image'lar ombori. <code>docker run</code> image lokalda bo'lmasa, uni shu yerdan o'zi yuklab oladi.</li>
</ul>
<p>Konteyner virtual mashina emas: u kompyuteringizning yadrosini (kernel) ulashadi, shuning uchun soniyalarda ishga tushadi va kam xotira oladi. Lekin ichidagi fayllar tizimi, tarmoq va jarayonlar boshqalardan ajratilgan.</p>
<pre class="mermaid">
flowchart LR
  A["Image (qolip)"] -->|"docker run"| B["Konteyner: ishlayapti"]
  B -->|"docker stop"| C["Konteyner: to'xtagan"]
  C -->|"docker rm"| D["Konteyner o'chirildi"]
  A -.->|"image saqlanib qoladi"| A
</pre>

<h3>O'rnatish</h3>
<p>Windows va macOS'da <strong>Docker Desktop</strong>, Linux'da Docker Engine o'rnatiladi. Tekshirish: <code>docker --version</code> va <code>docker compose version</code>.</p>

<h3>Birinchi buyruqlar</h3>
<pre><code>__RUN__</code></pre>
<ul>
  <li><code>docker run --rm python:3.12-slim python -c "..."</code> — image'dan konteyner ishga tushiradi, buyruqni bajaradi va <code>--rm</code> tufayli tugagach konteynerni o'zi o'chiradi. Image nomi <code>nom:teg</code> ko'rinishida (<code>python:3.12-slim</code> — Python 3.12'ning yengil varianti).</li>
  <li><code>-d</code> (detached) — konteynerni orqa fonda ishga tushiradi. <code>--name</code> unga o'zingiz nom beradi, <code>-e</code> muhit o'zgaruvchisini beradi (PostgreSQL image'i <code>POSTGRES_PASSWORD</code> siz ishlamaydi), <code>-p 5432:5432</code> kompyuteringizning portini konteyner portiga ulaydi (3-darsda batafsil).</li>
  <li><code>docker ps</code> — ishlayotgan konteynerlar; <code>docker logs</code> — konteyner chiqargan matn; <code>docker exec</code> — ishlayotgan konteyner ichida buyruq bajaradi (yuqoridagi misolda <code>psql</code> orqali bazaga so'rov); <code>-it</code> interaktiv terminal uchun.</li>
  <li><code>docker stop</code> konteynerni to'xtatadi, <code>docker rm</code> o'chiradi.</li>
</ul>
<p>Agar sizning kompyuteringizda 5432-port allaqachon band bo'lsa (lokal PostgreSQL), <code>-p 15432:5432</code> kabi boshqa port bering.</p>

<h3>Ro'yxat va tozalash</h3>
<pre><code>__LIST__</code></pre>
<p><code>docker images</code> lokal image'lar ro'yxati, <code>docker ps -a</code> to'xtaganlarini ham ko'rsatadi, <code>docker rm -f</code> ishlayotgan konteynerni majburan to'xtatib o'chiradi. Konteyner o'chirilsa, uning ichidagi <em>o'zgarishlar ham yo'qoladi</em>: ma'lumotni saqlash uchun volume kerak (3-dars).</p>"""

_L1_TEXT_RU = """<h3>Проблема: «у меня работает»</h3>
<p>Написанный вами API работает на вашем компьютере: версия Python, библиотеки, PostgreSQL и настройки у вас правильные. У коллеги или на сервере другая версия, другая операционная система и другие настройки, и появляется фраза «у меня работает». <strong>Docker</strong> упаковывает приложение <em>со всем необходимым</em> (Python, библиотеки, файлы, команда запуска) в один пакет и запускает его одинаково где угодно.</p>

<h3>Образ и контейнер</h3>
<ul>
  <li><strong>Образ (image)</strong> — неизменяемый «шаблон» приложения: файлы и команда запуска. Он только для чтения.</li>
  <li><strong>Контейнер</strong> — <em>процесс</em>, запущенный из образа. Из одного образа можно создать несколько контейнеров, они не мешают друг другу.</li>
  <li><strong>Registry</strong> (например, Docker Hub) — хранилище образов. Если образа нет локально, <code>docker run</code> сам скачает его оттуда.</li>
</ul>
<p>Контейнер — не виртуальная машина: он использует ядро (kernel) вашего компьютера, поэтому запускается за секунды и занимает мало памяти. При этом его файловая система, сеть и процессы изолированы от остальных.</p>
<pre class="mermaid">
flowchart LR
  A["Образ (шаблон)"] -->|"docker run"| B["Контейнер: работает"]
  B -->|"docker stop"| C["Контейнер: остановлен"]
  C -->|"docker rm"| D["Контейнер удалён"]
  A -.->|"образ остаётся"| A
</pre>

<h3>Установка</h3>
<p>В Windows и macOS ставится <strong>Docker Desktop</strong>, в Linux — Docker Engine. Проверка: <code>docker --version</code> и <code>docker compose version</code>.</p>

<h3>Первые команды</h3>
<pre><code>__RUN__</code></pre>
<ul>
  <li><code>docker run --rm python:3.12-slim python -c "..."</code> запускает контейнер из образа, выполняет команду и благодаря <code>--rm</code> сам удаляет контейнер после завершения. Имя образа записывается как <code>имя:тег</code> (<code>python:3.12-slim</code> — лёгкий вариант Python 3.12).</li>
  <li><code>-d</code> (detached) запускает контейнер в фоне. <code>--name</code> задаёт ему имя, <code>-e</code> передаёт переменную окружения (образ PostgreSQL не работает без <code>POSTGRES_PASSWORD</code>), <code>-p 5432:5432</code> соединяет порт вашего компьютера с портом контейнера (подробно в уроке 3).</li>
  <li><code>docker ps</code> — работающие контейнеры; <code>docker logs</code> — вывод контейнера; <code>docker exec</code> — выполняет команду внутри работающего контейнера (в примере выше запрос к базе через <code>psql</code>); <code>-it</code> нужен для интерактивного терминала.</li>
  <li><code>docker stop</code> останавливает контейнер, <code>docker rm</code> удаляет его.</li>
</ul>
<p>Если порт 5432 на вашем компьютере уже занят (локальный PostgreSQL), укажите другой порт, например <code>-p 15432:5432</code>.</p>

<h3>Список и очистка</h3>
<pre><code>__LIST__</code></pre>
<p><code>docker images</code> показывает локальные образы, <code>docker ps -a</code> — в том числе остановленные контейнеры, <code>docker rm -f</code> принудительно останавливает и удаляет работающий контейнер. Если контейнер удалён, <em>изменения внутри него тоже пропадают</em>: для сохранения данных нужен volume (том), о нём в уроке 3.</p>"""

_L1_BLOCKS = dict(RUN=CMD_L1_RUN, LIST=CMD_L1_LIST)

LESSON_1 = {
    "order": 0,
    "title": "1-Docker nima: image va konteyner",
    "title_ru": "1-Что такое Docker: образ и контейнер",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": CMD_L1_RUN,
    "code_content_ru": CMD_L1_RUN,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: docker run, ps, logs, exec",
        "title_ru": "Пример: docker run, ps, logs, exec",
        "description": "Python va PostgreSQL konteynerlarini ishga tushirish, loglarni ko'rish, ichida buyruq bajarish va o'chirish.",
        "description_ru": "Запуск контейнеров Python и PostgreSQL, просмотр логов, выполнение команды внутри и удаление.",
        "sample_type": "code",
        "code_files": [{"filename": "commands.sh", "language": "bash", "code": CMD_L1_RUN + "\n" + CMD_L1_LIST}],
    },
    "exercises": [
        {
            "title": "Image va konteyner", "title_ru": "Образ и контейнер",
            "description": "Image va konteyner o'rtasidagi farq qaysi variantda to'g'ri?",
            "description_ru": "В каком варианте верно описана разница между образом и контейнером?",
            "exercise_type": "multiple_choice",
            "options": [
                "Image — o'zgarmas qolip, konteyner — undan ishga tushirilgan jarayon",
                "Image — ishlayotgan jarayon, konteyner — fayl",
                "Ikkalasi bir xil narsa",
                "Image faqat Windows'da, konteyner faqat Linux'da bo'ladi",
            ],
            "options_ru": [
                "Образ — неизменяемый шаблон, контейнер — запущенный из него процесс",
                "Образ — работающий процесс, контейнер — файл",
                "Это одно и то же",
                "Образ бывает только в Windows, а контейнер только в Linux",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Bitta image'dan bir nechta konteyner yaratish mumkin.",
            "hint_ru": "Из одного образа можно создать несколько контейнеров.",
            "explanation": "Image faqat o'qiladigan qolip, konteyner esa shu image'dan ishga tushirilgan jarayon. Shuning uchun bitta image'dan ko'p konteyner yaratiladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Konteyner ro'yxati", "title_ru": "Список контейнеров",
            "description": "To'xtagan konteynerlarni ham ko'rsatadigan buyruq: docker ps ___",
            "description_ru": "Команда, показывающая и остановленные контейнеры: docker ps ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "-a",
            "hint": "«all» so'zining birinchi harfi.",
            "hint_ru": "Первая буква слова «all».",
            "explanation": "docker ps faqat ishlayotganlarini, docker ps -a esa to'xtaganlarini ham ko'rsatadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Konteyner hayoti", "title_ru": "Жизнь контейнера",
            "description": "Konteyner bilan ishlash tartibini joylashtiring.",
            "description_ru": "Расположите порядок работы с контейнером.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["docker run -d --name my-postgres ... bilan ishga tushirish", "docker ps bilan ishlayotganini tekshirish", "docker stop my-postgres bilan to'xtatish", "docker rm my-postgres bilan o'chirish"],
            "drag_items_ru": ["Запустить через docker run -d --name my-postgres ...", "Проверить через docker ps, что он работает", "Остановить через docker stop my-postgres", "Удалить через docker rm my-postgres"],
            "correct_order": ["docker run -d --name my-postgres ... bilan ishga tushirish", "docker ps bilan ishlayotganini tekshirish", "docker stop my-postgres bilan to'xtatish", "docker rm my-postgres bilan o'chirish"],
            "hint": "Konteyner avval ishga tushadi, keyin to'xtatiladi, oxirida o'chiriladi.",
            "hint_ru": "Контейнер сначала запускают, затем останавливают, в конце удаляют.",
            "explanation": "run konteyner yaratadi va ishga tushiradi, ps holatni ko'rsatadi, stop to'xtatadi, rm esa konteynerni butunlay o'chiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Flaglar", "title_ru": "Флаги",
            "description": "docker run flaglari haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о флагах docker run верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "-d konteynerni orqa fonda ishga tushiradi",
                "--rm konteyner tugagach uni o'zi o'chiradi",
                "-e muhit o'zgaruvchisini beradi",
                "--name konteyner image'ining nomini o'zgartiradi",
            ],
            "options_ru": [
                "-d запускает контейнер в фоне",
                "--rm сам удаляет контейнер после завершения",
                "-e передаёт переменную окружения",
                "--name меняет имя образа контейнера",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "--name image'ga emas, konteynerga nom beradi.",
            "hint_ru": "--name задаёт имя контейнеру, а не образу.",
            "explanation": "-d, --rm va -e to'g'ri ishlaydi. --name konteynerga nom beradi, image nomi esa nom:teg ko'rinishida alohida yoziladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Konteyner va virtual mashina", "title_ru": "Контейнер и виртуальная машина",
            "description": "Konteyner virtual mashinadan nimasi bilan farq qiladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Чем контейнер отличается от виртуальной машины? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Konteyner kompyuterning yadrosini (kernel) ulashadi, to'liq operatsion tizimni ishga tushirmaydi, shuning uchun soniyalarda ishga tushadi va kam xotira oladi. Virtual mashina esa o'zining to'liq operatsion tizimini ishga tushiradi.",
            "hint": "Kim yadroni (kernel) ulashadi, kim o'zining operatsion tizimini olib keladi?",
            "hint_ru": "Кто делит ядро (kernel), а кто несёт собственную операционную систему?",
            "explanation": "Konteyner host yadrosini ishlatadi va faqat ilova hamda kutubxonalarni ajratadi, shuning uchun yengil va tez. Virtual mashina esa to'liq OT ni ishga tushiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 2-dars: Dockerfile ───────────────────────────────────────────────────────

_L2_TEXT_UZ = """<h3>Dockerfile: image'ni o'zingiz yasaysiz</h3>
<p>Tayyor image'lar (<code>postgres</code>, <code>python</code>) bilan ishlashni ko'rdingiz. O'z ilovangizni konteynerga o'rash uchun <strong>Dockerfile</strong> yoziladi: image qanday yig'ilishini bosqichma-bosqich tavsiflaydigan matn fayli. Namuna: kichik FastAPI ilovasi (3 ta endpoint: <code>/health</code>, <code>/</code> va 3-darsda kerak bo'ladigan <code>/visits</code>).</p>
<pre><code>__MAIN__</code></pre>
<pre><code>__REQ__</code></pre>
<pre><code>__DOCKERFILE__</code></pre>
<ul>
  <li><code>FROM</code> — qaysi image asosida yig'iladi (<code>python:3.12-slim</code>).</li>
  <li><code>WORKDIR</code> — image ichidagi ish papkasi; keyingi buyruqlar shu yerda bajariladi.</li>
  <li><code>COPY</code> — fayllarni kompyuteringizdan image'ga ko'chiradi.</li>
  <li><code>RUN</code> — image yig'ilayotganda buyruq bajaradi (kutubxonalarni o'rnatish).</li>
  <li><code>EXPOSE</code> — ilova qaysi portda ishlashini <em>hujjatlashtiradi</em>. U portni tashqariga ochmaydi: buning uchun <code>docker run -p</code> kerak.</li>
  <li><code>CMD</code> — konteyner ishga tushganda bajariladigan asosiy buyruq. Massiv shaklida (<code>["uvicorn", ...]</code>) yoziladi.</li>
</ul>
<p><strong>Muhim:</strong> <code>--host 0.0.0.0</code>. Agar uvicorn standart <code>127.0.0.1</code> da tinglasa, ilova faqat konteynerning <em>ichidan</em> ko'rinadi va <code>-p</code> bilan ulangan port ishlamaydi. <code>0.0.0.0</code> «hamma tarmoq interfeysida tingla» degani.</p>

<h3>Layer'lar va kesh</h3>
<p>Dockerfile'ning har qatori image'ning bitta <strong>layer</strong>'ini (qatlamini) yaratadi. Docker o'zgarmagan layer'larni keshdan oladi. Shuning uchun <code>requirements.txt</code> ni <em>kodni nusxalashdan oldin</em> alohida ko'chirib, <code>pip install</code> ni shundan keyin yozdik. <code>main.py</code> o'zgarsa, faqat <code>COPY . .</code> qayta bajariladi, <code>pip install</code> esa keshdan olinadi va qayta build soniyalarda tugaydi.</p>
<pre class="mermaid">
flowchart TD
  A["COPY requirements.txt"] --> B["RUN pip install"]
  B --> C["COPY . ."]
  D["main.py o'zgardi"] --> C
  A -.->|"o'zgarmadi: CACHED"| B
  B -.->|"CACHED"| C
</pre>
<p>Agar <code>COPY . .</code> ni <code>pip install</code> dan oldin yozsangiz, har bir kod o'zgarishida kutubxonalar qayta o'rnatiladi.</p>

<h3>.dockerignore</h3>
<p><code>COPY . .</code> papkadagi <em>hamma</em> narsani ko'chiradi. <code>.dockerignore</code> fayli ba'zi fayllarni image'ga tushirmaydi (<code>.git</code>, <code>.venv</code>, <code>__pycache__</code> va ayniqsa parollar bor <code>.env</code>). Bu image'ni kichik va xavfsiz qiladi.</p>
<pre><code>__IGNORE__</code></pre>

<h3>Build va ishga tushirish</h3>
<pre><code>__BUILD__</code></pre>
<p><code>docker build -t notes-api:1.0 .</code> — nuqta (<code>.</code>) build konteksti, ya'ni Dockerfile turgan papka; <code>-t</code> image'ga nom va teg beradi. Bu misoldagi image taxminan 240 MB. Ishga tushgan konteyner <code>/health</code> da <code>{"status":"ok"}</code> qaytaradi. Tegni (<code>1.0</code>) har versiyada o'zgartiring: <code>latest</code> qaysi versiya ekanini yashiradi.</p>"""

_L2_TEXT_RU = """<h3>Dockerfile: вы сами создаёте образ</h3>
<p>Вы уже работали с готовыми образами (<code>postgres</code>, <code>python</code>). Чтобы упаковать собственное приложение в контейнер, пишется <strong>Dockerfile</strong> — текстовый файл, пошагово описывающий, как собирается образ. Пример: небольшое приложение FastAPI (3 эндпоинта: <code>/health</code>, <code>/</code> и <code>/visits</code>, который понадобится в уроке 3).</p>
<pre><code>__MAIN__</code></pre>
<pre><code>__REQ__</code></pre>
<pre><code>__DOCKERFILE__</code></pre>
<ul>
  <li><code>FROM</code> — на основе какого образа строится новый (<code>python:3.12-slim</code>).</li>
  <li><code>WORKDIR</code> — рабочая папка внутри образа; следующие команды выполняются в ней.</li>
  <li><code>COPY</code> — копирует файлы с вашего компьютера в образ.</li>
  <li><code>RUN</code> — выполняет команду во время сборки образа (установка библиотек).</li>
  <li><code>EXPOSE</code> — <em>документирует</em>, на каком порту работает приложение. Он не открывает порт наружу: для этого нужен <code>docker run -p</code>.</li>
  <li><code>CMD</code> — основная команда, выполняемая при запуске контейнера. Записывается в виде массива (<code>["uvicorn", ...]</code>).</li>
</ul>
<p><strong>Важно:</strong> <code>--host 0.0.0.0</code>. Если uvicorn слушает стандартный <code>127.0.0.1</code>, приложение видно только <em>изнутри</em> контейнера, и порт, соединённый через <code>-p</code>, не заработает. <code>0.0.0.0</code> означает «слушай на всех сетевых интерфейсах».</p>

<h3>Слои и кеш</h3>
<p>Каждая строка Dockerfile создаёт один <strong>слой (layer)</strong> образа. Docker берёт неизменившиеся слои из кеша. Поэтому <code>requirements.txt</code> мы копируем отдельно <em>до копирования кода</em>, а <code>pip install</code> пишем после. Если изменится <code>main.py</code>, заново выполнится только <code>COPY . .</code>, а <code>pip install</code> возьмётся из кеша, и повторная сборка займёт секунды.</p>
<pre class="mermaid">
flowchart TD
  A["COPY requirements.txt"] --> B["RUN pip install"]
  B --> C["COPY . ."]
  D["main.py изменился"] --> C
  A -.->|"не менялся: CACHED"| B
  B -.->|"CACHED"| C
</pre>
<p>Если поставить <code>COPY . .</code> перед <code>pip install</code>, библиотеки будут переустанавливаться при каждом изменении кода.</p>

<h3>.dockerignore</h3>
<p><code>COPY . .</code> копирует <em>всё</em> из папки. Файл <code>.dockerignore</code> не пускает часть файлов в образ (<code>.git</code>, <code>.venv</code>, <code>__pycache__</code> и особенно <code>.env</code> с паролями). Это делает образ меньше и безопаснее.</p>
<pre><code>__IGNORE__</code></pre>

<h3>Сборка и запуск</h3>
<pre><code>__BUILD__</code></pre>
<p><code>docker build -t notes-api:1.0 .</code> — точка (<code>.</code>) обозначает контекст сборки, то есть папку с Dockerfile; <code>-t</code> задаёт образу имя и тег. В этом примере образ весит около 240 МБ. Запущенный контейнер на <code>/health</code> возвращает <code>{"status":"ok"}</code>. Меняйте тег (<code>1.0</code>) с каждой версией: <code>latest</code> скрывает, какая это версия.</p>"""

_L2_BLOCKS = dict(MAIN=MAIN_SIMPLE, REQ=REQUIREMENTS_L2, DOCKERFILE=DOCKERFILE_L2, IGNORE=DOCKERIGNORE, BUILD=CMD_L2_BUILD)

LESSON_2 = {
    "order": 1,
    "title": "2-Dockerfile: o'z image'ingizni yig'ish",
    "title_ru": "2-Dockerfile: сборка собственного образа",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": DOCKERFILE_L2,
    "code_content_ru": DOCKERFILE_L2,
    "code_language": "dockerfile",
    "sample": {
        "title": "Namuna: FastAPI ilovasi uchun Dockerfile",
        "title_ru": "Пример: Dockerfile для приложения FastAPI",
        "description": "Dockerfile, requirements.txt, .dockerignore va oddiy FastAPI ilovasi: build va run buyruqlari bilan.",
        "description_ru": "Dockerfile, requirements.txt, .dockerignore и простое приложение FastAPI: команды build и run.",
        "sample_type": "code",
        "code_files": [
            {"filename": "Dockerfile", "language": "dockerfile", "code": DOCKERFILE_L2},
            {"filename": "main.py", "language": "python", "code": MAIN_SIMPLE},
            {"filename": "requirements.txt", "language": "text", "code": REQUIREMENTS_L2},
            {"filename": ".dockerignore", "language": "text", "code": DOCKERIGNORE},
            {"filename": "commands.sh", "language": "bash", "code": CMD_L2_BUILD},
        ],
    },
    "exercises": [
        {
            "title": "Layer tartibi", "title_ru": "Порядок слоёв",
            "description": "Nega requirements.txt kodni nusxalashdan oldin alohida ko'chiriladi?",
            "description_ru": "Почему requirements.txt копируют отдельно до копирования кода?",
            "exercise_type": "multiple_choice",
            "options": [
                "Kod o'zgarganda pip install layer'i keshdan olinadi va build tez bo'ladi",
                "Docker faqat requirements.txt ni o'qiy oladi",
                "Aks holda ilova ishga tushmaydi",
                "Image kichikroq bo'lishi uchun requirements.txt o'chiriladi",
            ],
            "options_ru": [
                "При изменении кода слой pip install берётся из кеша, и сборка идёт быстро",
                "Docker умеет читать только requirements.txt",
                "Иначе приложение не запустится",
                "Чтобы образ был меньше, requirements.txt удаляется",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Docker o'zgarmagan layer'larni qayta bajarmaydi.",
            "hint_ru": "Docker не выполняет заново неизменившиеся слои.",
            "explanation": "Kutubxonalar kamdan-kam o'zgaradi, kod esa tez-tez. Shuning uchun pip install layer'i kod nusxalanishidan oldin turadi va keshdan olinadi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Asosiy buyruq", "title_ru": "Основная команда",
            "description": "Konteyner ishga tushganda bajariladigan asosiy buyruq Dockerfile'da qaysi kalit so'z bilan yoziladi? ___",
            "description_ru": "Каким ключевым словом в Dockerfile записывается основная команда запуска контейнера? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "CMD",
            "hint": "Uch harfli, inglizcha «command» ning qisqartmasi.",
            "hint_ru": "Три буквы, сокращение от «command».",
            "explanation": "CMD konteyner ishga tushganda bajariladi, RUN esa image yig'ilayotganda.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Dockerfile tartibi", "title_ru": "Порядок Dockerfile",
            "description": "Dockerfile qatorlarini to'g'ri tartibga soling (keshdan eng yaxshi foydalanish uchun).",
            "description_ru": "Расположите строки Dockerfile в правильном порядке (для лучшего использования кеша).",
            "exercise_type": "drag_and_drop",
            "drag_items": ["FROM python:3.12-slim", "COPY requirements.txt .", "RUN pip install --no-cache-dir -r requirements.txt", "COPY . ."],
            "drag_items_ru": ["FROM python:3.12-slim", "COPY requirements.txt .", "RUN pip install --no-cache-dir -r requirements.txt", "COPY . ."],
            "correct_order": ["FROM python:3.12-slim", "COPY requirements.txt .", "RUN pip install --no-cache-dir -r requirements.txt", "COPY . ."],
            "hint": "Kam o'zgaradigan narsa tepada, tez-tez o'zgaradigan (kod) pastda.",
            "hint_ru": "Редко меняющееся — выше, часто меняющееся (код) — ниже.",
            "explanation": "Asos image, keyin kutubxona ro'yxati, kutubxonalarni o'rnatish va eng oxirida kod. Shunda kod o'zgarganda faqat oxirgi layer qayta yig'iladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Host va port", "title_ru": "Хост и порт",
            "description": "Konteyner ichida uvicorn --host 0.0.0.0 bilan ishga tushirilishining sabablari qaysilar? (Bir nechta javob)",
            "description_ru": "Почему внутри контейнера uvicorn запускают с --host 0.0.0.0? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "127.0.0.1 da ilova faqat konteyner ichidan ko'rinadi",
                "0.0.0.0 barcha tarmoq interfeyslarida tinglashni bildiradi",
                "-p bilan ulangan port faqat shunda ishlaydi",
                "0.0.0.0 ilovani tezlashtiradi",
            ],
            "options_ru": [
                "На 127.0.0.1 приложение видно только изнутри контейнера",
                "0.0.0.0 означает прослушивание на всех сетевых интерфейсах",
                "Порт, соединённый через -p, работает только так",
                "0.0.0.0 ускоряет приложение",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Tezlik bilan bog'liq emas, tarmoq ko'rinishi haqida.",
            "hint_ru": "Не про скорость, а про сетевую доступность.",
            "explanation": "127.0.0.1 faqat konteyner ichida ko'rinadi. 0.0.0.0 hamma interfeysda tinglaydi, shuning uchun -p orqali tashqaridan ulanish mumkin bo'ladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": ".dockerignore vazifasi", "title_ru": "Назначение .dockerignore",
            "description": ".dockerignore nima uchun kerak va unga nimalar yoziladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем нужен .dockerignore и что в него пишут? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "COPY . . papkadagi hamma narsani image'ga ko'chiradi. .dockerignore keraksiz va maxfiy fayllarni (.git, .venv, __pycache__, parollar bor .env) ko'chirishdan saqlaydi: image kichikroq va xavfsizroq bo'ladi.",
            "hint": "COPY . . nimalarni ko'chirishini o'ylang.",
            "hint_ru": "Подумайте, что копирует COPY . .",
            "explanation": ".dockerignore build kontekstidan fayllarni chiqarib tashlaydi. Bu image hajmini kamaytiradi va .env kabi maxfiy fayllar image'ga tushib qolmasligini ta'minlaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: port, env, volume ────────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>Konteyner izolyatsiyalangan</h3>
<p>Konteyner o'z tarmog'i va o'z fayllar tizimiga ega. Ichkaridagi ilovaga tashqaridan kirish, sozlamani berish va ma'lumotni saqlash uchun uch narsa kerak: <strong>port</strong>, <strong>muhit o'zgaruvchisi</strong> va <strong>volume</strong>. 2-darsdagi <code>notes-api:1.0</code> image'i bilan ishlaymiz.</p>

<h3>Portlar: -p tashqi:ichki</h3>
<p><code>-p 8000:8000</code> — «kompyuterimning 8000-portiga kelgan so'rovni konteynerning 8000-portiga yubor». Birinchi raqam <strong>sizning kompyuteringiz</strong>, ikkinchisi <strong>konteyner ichidagi</strong> port. Kompyuteringizda 8000 band bo'lsa, <code>-p 8080:8000</code> deb tashqi portni o'zgartirasiz, konteyner ichidagi 8000 o'zgarmaydi.</p>

<h3>Muhit o'zgaruvchilari</h3>
<p>Sozlama (<code>GREETING</code>, baza manzili, kalit) image'ga yozilmaydi: image bir marta yig'iladi, sozlamani esa har muhit uchun alohida beramiz. <code>-e NOM=qiymat</code> bitta o'zgaruvchi beradi, <code>--env-file</code> esa faylni (<code>NOM=qiymat</code> qatorlari) o'qiydi. Ilova ularni <code>os.environ.get("GREETING", ...)</code> bilan oladi (2-darsdagi <code>main.py</code>). Parol va kalitlarni <strong>hech qachon</strong> Dockerfile'ga yozmang: image'ni ko'rgan har kim ularni o'qiy oladi.</p>

<h3>Volume: ma'lumot konteynerdan uzoq yashashi uchun</h3>
<p>Konteyner o'chirilsa, uning ichidagi barcha o'zgarishlar yo'qoladi. Ma'lumotni saqlash uchun <strong>volume</strong> ishlatiladi: Docker boshqaradigan va konteynerdan mustaqil yashaydigan papka. <code>-v visits:/data</code> — «<code>visits</code> nomli volume'ni konteynerning <code>/data</code> papkasiga ulagin». Ilovamizdagi <code>/visits</code> endpoint'i hisoblagichni <code>/data/visits.txt</code> faylida saqlaydi.</p>
<pre class="mermaid">
flowchart LR
  A["Konteyner 1 (/data)"] --> V[("volume: visits")]
  V --> B["Konteyner 2 (/data)"]
  A -.->|"docker rm: konteyner o'chdi"| X["fayllar volume'da qoladi"]
</pre>
<pre><code>__RUN__</code></pre>
<p>Natija: birinchi bo'lim <code>{"message":"Salom, Docker"}</code> qaytaradi. Ikkinchi bo'limda hisoblagich 1, 2 bo'ladi. Konteynerni o'chirib, <strong>shu volume</strong> bilan qayta ishga tushirsangiz, hisoblagich <strong>3</strong> dan davom etadi. Volume'siz yangi konteynerda esa <strong>1</strong> dan boshlanadi: ma'lumot yo'qolgan.</p>

<h3>Volume bilan ishlash</h3>
<pre><code>__VOLUME__</code></pre>
<p><code>docker volume rm</code> volume'ni va undagi ma'lumotni butunlay o'chiradi: ehtiyot bo'ling. Uni faqat hech bir konteyner ishlatmayotgan bo'lsagina o'chirish mumkin.</p>

<h3>.env fayli bilan</h3>
<pre><code>__ENVFILE__</code></pre>
<p><code>.env</code> faylida <code>GREETING=Salom</code> kabi qatorlar bo'ladi. Bu fayl <strong>git'ga qo'shilmaydi</strong> (<code>.gitignore</code>) va <code>.dockerignore</code> orqali image'ga ham tushmaydi.</p>

<h3>Bind mount haqida</h3>
<p>Volume'dan tashqari kompyuteringizdagi <em>aniq papkani</em> konteynerga ulash ham mumkin (bind mount). U odatda ishlab chiqishda kodni qayta build qilmasdan ko'rish uchun ishlatiladi. Production'da ma'lumot uchun nomli volume ishonchliroq.</p>"""

_L3_TEXT_RU = """<h3>Контейнер изолирован</h3>
<p>У контейнера своя сеть и своя файловая система. Чтобы достучаться до приложения внутри, передать ему настройку и сохранить данные, нужны три вещи: <strong>порт</strong>, <strong>переменная окружения</strong> и <strong>volume (том)</strong>. Работаем с образом <code>notes-api:1.0</code> из урока 2.</p>

<h3>Порты: -p внешний:внутренний</h3>
<p><code>-p 8000:8000</code> означает «запрос на порт 8000 моего компьютера отправь на порт 8000 контейнера». Первое число — порт <strong>вашего компьютера</strong>, второе — порт <strong>внутри контейнера</strong>. Если у вас занят 8000, укажите <code>-p 8080:8000</code>: внешний порт меняется, а порт 8000 внутри контейнера остаётся прежним.</p>

<h3>Переменные окружения</h3>
<p>Настройки (<code>GREETING</code>, адрес базы, ключ) не записывают в образ: образ собирается один раз, а настройки задаются отдельно для каждой среды. <code>-e ИМЯ=значение</code> передаёт одну переменную, а <code>--env-file</code> читает файл (строки <code>ИМЯ=значение</code>). Приложение получает их через <code>os.environ.get("GREETING", ...)</code> (<code>main.py</code> из урока 2). <strong>Никогда</strong> не записывайте пароли и ключи в Dockerfile: любой, кто получит образ, сможет их прочитать.</p>

<h3>Volume: чтобы данные жили дольше контейнера</h3>
<p>Если контейнер удалён, все изменения внутри него пропадают. Для сохранения данных используется <strong>volume</strong> — папка, которой управляет Docker и которая живёт независимо от контейнера. <code>-v visits:/data</code> означает «подключи volume с именем <code>visits</code> к папке <code>/data</code> контейнера». Эндпоинт <code>/visits</code> нашего приложения хранит счётчик в файле <code>/data/visits.txt</code>.</p>
<pre class="mermaid">
flowchart LR
  A["Контейнер 1 (/data)"] --> V[("volume: visits")]
  V --> B["Контейнер 2 (/data)"]
  A -.->|"docker rm: контейнер удалён"| X["файлы остаются в volume"]
</pre>
<pre><code>__RUN__</code></pre>
<p>Результат: первый блок вернёт <code>{"message":"Salom, Docker"}</code>. Во втором блоке счётчик станет 1, затем 2. Если удалить контейнер и запустить новый с <strong>тем же volume</strong>, счётчик продолжится с <strong>3</strong>. А в новом контейнере без volume он начнётся с <strong>1</strong>: данные потеряны.</p>

<h3>Работа с volume</h3>
<pre><code>__VOLUME__</code></pre>
<p><code>docker volume rm</code> полностью удаляет volume вместе с данными: будьте осторожны. Удалить его можно, только если им не пользуется ни один контейнер.</p>

<h3>Через файл .env</h3>
<pre><code>__ENVFILE__</code></pre>
<p>В файле <code>.env</code> лежат строки вида <code>GREETING=Salom</code>. Этот файл <strong>не добавляется в git</strong> (<code>.gitignore</code>) и через <code>.dockerignore</code> не попадает в образ.</p>

<h3>О bind mount</h3>
<p>Кроме volume можно подключить к контейнеру <em>конкретную папку</em> вашего компьютера (bind mount). Обычно её используют при разработке, чтобы видеть изменения кода без пересборки. Для данных в production надёжнее именованный volume.</p>"""

_L3_BLOCKS = dict(RUN=CMD_L3_RUN, VOLUME=CMD_L3_VOLUME, ENVFILE=CMD_L3_ENVFILE)

LESSON_3 = {
    "order": 2,
    "title": "3-Port, muhit o'zgaruvchilari va volume",
    "title_ru": "3-Порты, переменные окружения и volume",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": CMD_L3_RUN,
    "code_content_ru": CMD_L3_RUN,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: -p, -e va -v bilan konteyner",
        "title_ru": "Пример: контейнер с -p, -e и -v",
        "description": "Port, muhit o'zgaruvchisi va volume: hisoblagich konteyner o'chirilgandan keyin ham saqlanadi.",
        "description_ru": "Порт, переменная окружения и volume: счётчик сохраняется даже после удаления контейнера.",
        "sample_type": "code",
        "code_files": [
            {"filename": "commands.sh", "language": "bash", "code": CMD_L3_RUN + "\n" + CMD_L3_VOLUME + "\n" + CMD_L3_ENVFILE},
            {"filename": "main.py", "language": "python", "code": MAIN_SIMPLE},
        ],
    },
    "exercises": [
        {
            "title": "Port ulash", "title_ru": "Проброс порта",
            "description": "docker run -p 8080:8000 ... buyrug'ida 8080 nimani bildiradi?",
            "description_ru": "Что означает 8080 в команде docker run -p 8080:8000 ...?",
            "exercise_type": "multiple_choice",
            "options": [
                "Kompyuteringiz (host) porti",
                "Konteyner ichidagi port",
                "Ma'lumotlar bazasi porti",
                "Image versiyasi",
            ],
            "options_ru": [
                "Порт вашего компьютера (host)",
                "Порт внутри контейнера",
                "Порт базы данных",
                "Версия образа",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Format: tashqi:ichki.",
            "hint_ru": "Формат: внешний:внутренний.",
            "explanation": "-p host:konteyner. 8080 — kompyuteringizdagi port, 8000 esa konteyner ichidagi port.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Volume flagi", "title_ru": "Флаг volume",
            "description": "Volume'ni konteynerga ulaydigan flag: docker run ___ visits:/data ...",
            "description_ru": "Флаг, подключающий volume к контейнеру: docker run ___ visits:/data ...",
            "exercise_type": "fill_in_blank",
            "correct_answers": "-v",
            "hint": "«volume» so'zining birinchi harfi.",
            "hint_ru": "Первая буква слова «volume».",
            "explanation": "-v nom:yo'l nomli volume'ni konteynerdagi papkaga ulaydi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Ma'lumot saqlanishi", "title_ru": "Сохранение данных",
            "description": "Volume bilan ma'lumotning saqlanishini ko'rsatadigan tartibni joylashtiring.",
            "description_ru": "Расположите порядок, показывающий сохранение данных с volume.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Konteyner -v visits:/data bilan ishga tushadi", "/visits ikki marta chaqiriladi (hisoblagich 2)", "Konteyner docker rm -f bilan o'chiriladi", "Yangi konteyner shu volume bilan ishga tushadi va hisoblagich 3 bo'ladi"],
            "drag_items_ru": ["Контейнер запускается с -v visits:/data", "/visits вызывается дважды (счётчик 2)", "Контейнер удаляется через docker rm -f", "Новый контейнер запускается с тем же volume, счётчик становится 3"],
            "correct_order": ["Konteyner -v visits:/data bilan ishga tushadi", "/visits ikki marta chaqiriladi (hisoblagich 2)", "Konteyner docker rm -f bilan o'chiriladi", "Yangi konteyner shu volume bilan ishga tushadi va hisoblagich 3 bo'ladi"],
            "hint": "Ma'lumot volume'da qoladi, konteyner o'chsa ham.",
            "hint_ru": "Данные остаются в volume, даже если контейнер удалён.",
            "explanation": "Volume konteynerdan mustaqil, shuning uchun konteyner o'chirilganda ham fayl qoladi va yangi konteyner hisoblagichni davom ettiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Sozlamalar xavfsizligi", "title_ru": "Безопасность настроек",
            "description": "Parol va sozlamalarni berish haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о передаче паролей и настроек верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "-e yoki --env-file bilan ishga tushganda beriladi",
                ".env fayli git'ga qo'shilmaydi",
                "Parolni Dockerfile ichiga yozish xavfsiz",
                "Image'ni ko'rgan har kim ichidagi parolni o'qiy oladi",
            ],
            "options_ru": [
                "Передаются при запуске через -e или --env-file",
                "Файл .env не добавляют в git",
                "Писать пароль в Dockerfile безопасно",
                "Любой, кто получил образ, может прочитать пароль внутри",
            ],
            "correct_answers": "A,B,D", "is_multiple_select": True,
            "hint": "Image ko'p odamga tarqalishi mumkin.",
            "hint_ru": "Образ может попасть ко многим людям.",
            "explanation": "Sozlama image'ga emas, ishga tushirishda beriladi; .env git'ga qo'shilmaydi. Dockerfile'ga yozilgan parol image'da qoladi va uni hamma o'qiy oladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Volume kerakligi", "title_ru": "Зачем нужен volume",
            "description": "Nega ma'lumotlar bazasi konteynerida volume ishlatish shart? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему для контейнера с базой данных обязательно использовать volume? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Konteyner o'chirilsa yoki qayta yaratilsa, uning ichidagi fayllar yo'qoladi. Volume Docker boshqaradigan va konteynerdan mustaqil papka, shuning uchun baza ma'lumotlari konteyner o'chsa ham saqlanib qoladi.",
            "hint": "Konteyner o'chirilganda ichidagi fayllarga nima bo'ladi?",
            "hint_ru": "Что происходит с файлами внутри контейнера при его удалении?",
            "explanation": "Konteynerning fayllar tizimi vaqtinchalik. Volume ma'lumotni konteynerdan alohida saqlaydi, shuning uchun baza qayta yaratilganda ma'lumotlar yo'qolmaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: Docker Compose ───────────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>Nega Compose</h3>
<p>Haqiqiy ilova bitta konteynerdan iborat emas: API, ma'lumotlar bazasi, ba'zan keshlash. Ularni alohida <code>docker run</code> bilan, har biriga portlar, o'zgaruvchilar va tarmoqni qo'lda yozib ishga tushirish noqulay. <strong>Docker Compose</strong> butun to'plamni bitta <code>compose.yaml</code> faylida tasvirlaydi va bitta buyruq bilan ishga tushiradi. Bu darsda API (FastAPI) va PostgreSQL'ni birga ishga tushiramiz.</p>

<h3>Ilova: PostgreSQL bilan</h3>
<p>Endi yozuvlar bazada saqlanadi. Ilova baza manzilini <code>DATABASE_URL</code> o'zgaruvchisidan oladi (sozlama image'da emas). <code>requirements.txt</code> ga <code>psycopg</code> qo'shildi, Dockerfile esa 2-darsdagi bilan bir xil.</p>
<pre><code>__MAIN__</code></pre>
<pre><code>__REQ__</code></pre>

<h3>compose.yaml</h3>
<pre><code>__COMPOSE__</code></pre>
<ul>
  <li><code>services</code> — har bir konteyner (xizmat) shu yerda. Xizmat nomi (<code>db</code>, <code>api</code>) Compose tarmog'ida <strong>host nomi</strong> bo'ladi: API bazaga <code>localhost</code> emas, <code>db:5432</code> orqali ulanadi. Konteyner ichida <code>localhost</code> — konteynerning o'zi.</li>
  <li><code>image</code> tayyor image oladi, <code>build: .</code> esa joriy papkadagi Dockerfile'dan image yig'adi.</li>
  <li><code>environment</code> — o'zgaruvchilar. <code>${POSTGRES_PASSWORD:-notes-dev-password}</code> — «shell yoki <code>.env</code> dagi <code>POSTGRES_PASSWORD</code>ni ol, yo'q bo'lsa <code>notes-dev-password</code>». <code>${API_PORT:-8000}</code> ham shunday: portni tashqaridan o'zgartirish mumkin.</li>
  <li><code>volumes</code> — baza ma'lumoti uchun <code>pgdata</code> volume'i (3-dars), pastdagi <code>volumes:</code> bo'limida e'lon qilinadi.</li>
  <li><code>healthcheck</code> — Docker xizmat haqiqatan tayyorligini qanday tekshirishini aytadi: <code>pg_isready</code> bazani, API uchun esa <code>/health</code> ni.</li>
  <li><code>depends_on</code> + <code>condition: service_healthy</code> — API faqat baza <em>sog'lom</em> bo'lgandan keyin ishga tushadi. Oddiy <code>depends_on</code> faqat konteyner boshlanishini kutadi, baza qabul qilishga tayyor bo'lishini emas.</li>
</ul>
<pre class="mermaid">
flowchart LR
  U["Siz: curl :8000"] --> A["api konteyneri (8000)"]
  A -->|"db:5432 (Compose tarmog'i)"| D["db konteyneri (PostgreSQL)"]
  D --> V[("volume: pgdata")]
</pre>

<h3>Asosiy buyruqlar</h3>
<pre><code>__UP__</code></pre>
<ul>
  <li><code>up -d --build --wait</code> — kerak bo'lsa image'ni yig'adi, hammasini orqa fonda ishga tushiradi va <em>healthcheck</em>lar yashil bo'lguncha kutadi. <code>--wait</code> bo'lmasa, <code>curl</code> API tayyor bo'lishidan oldin ishga tushib, bo'sh javob olishi mumkin.</li>
  <li><code>ps</code> xizmatlar holatini, <code>logs api</code> bitta xizmat logini ko'rsatadi. <code>exec db psql ...</code> ishlayotgan bazada buyruq bajaradi.</li>
  <li><code>down</code> konteynerlar va tarmoqni o'chiradi, <strong>volume saqlanadi</strong>: keyingi <code>up</code> da yozuv joyida turadi. <code>down -v</code> volume'ni ham o'chiradi: baza ma'lumoti yo'qoladi.</li>
</ul>
<p>Natija: <code>POST</code> yozuv yaratadi (<code>201</code>), 2 ta harfli matn <code>422</code> qaytaradi, <code>down</code> dan keyingi <code>up</code> yozuvni saqlab qoladi.</p>"""

_L4_TEXT_RU = """<h3>Зачем нужен Compose</h3>
<p>Настоящее приложение состоит не из одного контейнера: API, база данных, иногда кеш. Запускать их по отдельности через <code>docker run</code>, вручную прописывая порты, переменные и сеть, неудобно. <strong>Docker Compose</strong> описывает весь набор в одном файле <code>compose.yaml</code> и запускает его одной командой. В этом уроке мы запустим вместе API (FastAPI) и PostgreSQL.</p>

<h3>Приложение: с PostgreSQL</h3>
<p>Теперь записи хранятся в базе. Приложение получает адрес базы из переменной <code>DATABASE_URL</code> (настройка не в образе). В <code>requirements.txt</code> добавлен <code>psycopg</code>, а Dockerfile такой же, как в уроке 2.</p>
<pre><code>__MAIN__</code></pre>
<pre><code>__REQ__</code></pre>

<h3>compose.yaml</h3>
<pre><code>__COMPOSE__</code></pre>
<ul>
  <li><code>services</code> — здесь описан каждый контейнер (сервис). Имя сервиса (<code>db</code>, <code>api</code>) становится <strong>именем хоста</strong> в сети Compose: API подключается к базе не через <code>localhost</code>, а через <code>db:5432</code>. Внутри контейнера <code>localhost</code> — это сам контейнер.</li>
  <li><code>image</code> берёт готовый образ, а <code>build: .</code> собирает образ из Dockerfile в текущей папке.</li>
  <li><code>environment</code> — переменные. <code>${POSTGRES_PASSWORD:-notes-dev-password}</code> означает «возьми <code>POSTGRES_PASSWORD</code> из shell или <code>.env</code>, а если его нет — <code>notes-dev-password</code>». <code>${API_PORT:-8000}</code> работает так же: порт можно менять снаружи.</li>
  <li><code>volumes</code> — volume <code>pgdata</code> для данных базы (урок 3), объявляется в разделе <code>volumes:</code> внизу.</li>
  <li><code>healthcheck</code> — говорит Docker, как проверить, что сервис действительно готов: <code>pg_isready</code> для базы и <code>/health</code> для API.</li>
  <li><code>depends_on</code> + <code>condition: service_healthy</code> — API стартует только когда база <em>здорова</em>. Обычный <code>depends_on</code> ждёт лишь запуска контейнера, а не готовности базы принимать запросы.</li>
</ul>
<pre class="mermaid">
flowchart LR
  U["Вы: curl :8000"] --> A["контейнер api (8000)"]
  A -->|"db:5432 (сеть Compose)"| D["контейнер db (PostgreSQL)"]
  D --> V[("volume: pgdata")]
</pre>

<h3>Основные команды</h3>
<pre><code>__UP__</code></pre>
<ul>
  <li><code>up -d --build --wait</code> при необходимости собирает образ, запускает всё в фоне и <em>ждёт</em>, пока <em>healthcheck</em> станут зелёными. Без <code>--wait</code> команда <code>curl</code> может выполниться раньше, чем API будет готов, и вернуть пустой ответ.</li>
  <li><code>ps</code> показывает состояние сервисов, <code>logs api</code> — лог одного сервиса. <code>exec db psql ...</code> выполняет команду в работающей базе.</li>
  <li><code>down</code> удаляет контейнеры и сеть, но <strong>volume сохраняется</strong>: при следующем <code>up</code> запись останется на месте. <code>down -v</code> удаляет и volume: данные базы пропадают.</li>
</ul>
<p>Результат: <code>POST</code> создаёт запись (<code>201</code>), текст из 2 букв вернёт <code>422</code>, а <code>up</code> после <code>down</code> сохраняет запись.</p>"""

_L4_BLOCKS = dict(MAIN=MAIN_DB, REQ=REQUIREMENTS_L4, COMPOSE=COMPOSE_L4, UP=CMD_L4_UP)

LESSON_4 = {
    "order": 3,
    "title": "4-Docker Compose: API + PostgreSQL",
    "title_ru": "4-Docker Compose: API и PostgreSQL",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": COMPOSE_L4,
    "code_content_ru": COMPOSE_L4,
    "code_language": "yaml",
    "sample": {
        "title": "Namuna: compose.yaml bilan API va PostgreSQL",
        "title_ru": "Пример: API и PostgreSQL через compose.yaml",
        "description": "compose.yaml (healthcheck, depends_on, volume), PostgreSQL bilan ishlaydigan FastAPI ilovasi va buyruqlar.",
        "description_ru": "compose.yaml (healthcheck, depends_on, volume), приложение FastAPI с PostgreSQL и команды.",
        "sample_type": "code",
        "code_files": [
            {"filename": "compose.yaml", "language": "yaml", "code": COMPOSE_L4},
            {"filename": "main.py", "language": "python", "code": MAIN_DB},
            {"filename": "requirements.txt", "language": "text", "code": REQUIREMENTS_L4},
            {"filename": "Dockerfile", "language": "dockerfile", "code": DOCKERFILE_L2},
            {"filename": "commands.sh", "language": "bash", "code": CMD_L4_UP},
        ],
    },
    "exercises": [
        {
            "title": "Compose'da baza manzili", "title_ru": "Адрес базы в Compose",
            "description": "API konteyneri Compose'dagi baza xizmatiga (db) qanday ulanadi?",
            "description_ru": "Как контейнер API подключается к сервису базы (db) в Compose?",
            "exercise_type": "multiple_choice",
            "options": [
                "db:5432 (xizmat nomi host sifatida)",
                "localhost:5432",
                "127.0.0.1:5432",
                "Faqat kompyuterning IP manzili orqali",
            ],
            "options_ru": [
                "db:5432 (имя сервиса как хост)",
                "localhost:5432",
                "127.0.0.1:5432",
                "Только через IP-адрес компьютера",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Konteyner ichida localhost — konteynerning o'zi.",
            "hint_ru": "Внутри контейнера localhost — это сам контейнер.",
            "explanation": "Compose xizmat nomini tarmoqda host nomi qiladi, shuning uchun API bazaga db:5432 orqali ulanadi. localhost API konteynerining o'zi bo'lardi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Compose buyrug'i", "title_ru": "Команда Compose",
            "description": "Barcha xizmatlarni orqa fonda ishga tushiradigan buyruq: docker compose ___ -d",
            "description_ru": "Команда, запускающая все сервисы в фоне: docker compose ___ -d",
            "exercise_type": "fill_in_blank",
            "correct_answers": "up",
            "hint": "«Ko'tarish» inglizcha qanday?",
            "hint_ru": "Как по-английски «поднять»?",
            "explanation": "docker compose up -d xizmatlarni orqa fonda ishga tushiradi, docker compose down esa to'xtatib o'chiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Ishga tushish tartibi", "title_ru": "Порядок запуска",
            "description": "docker compose up -d --build --wait paytidagi tartibni joylashtiring.",
            "description_ru": "Расположите порядок событий при docker compose up -d --build --wait.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["API image'i yig'iladi (build)", "db konteyneri ishga tushadi", "db healthcheck (pg_isready) yashil bo'ladi", "api konteyneri ishga tushadi va /health yashil bo'ladi"],
            "drag_items_ru": ["Собирается образ API (build)", "Запускается контейнер db", "Healthcheck db (pg_isready) становится зелёным", "Запускается контейнер api, и /health становится зелёным"],
            "correct_order": ["API image'i yig'iladi (build)", "db konteyneri ishga tushadi", "db healthcheck (pg_isready) yashil bo'ladi", "api konteyneri ishga tushadi va /health yashil bo'ladi"],
            "hint": "API faqat baza sog'lom bo'lgach boshlanadi.",
            "hint_ru": "API стартует только после того, как база здорова.",
            "explanation": "Avval image yig'iladi, baza ishga tushadi va sog'lom bo'ladi (service_healthy), shundan keyin api boshlanadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "down va down -v", "title_ru": "down и down -v",
            "description": "docker compose down va down -v haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о docker compose down и down -v верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "down konteynerlarni o'chiradi, nomli volume saqlanadi",
                "down -v volume'ni ham o'chiradi",
                "down -v dan keyin baza ma'lumoti saqlanib qoladi",
                "down volume'ni har doim o'chiradi",
            ],
            "options_ru": [
                "down удаляет контейнеры, именованный volume сохраняется",
                "down -v удаляет и volume",
                "После down -v данные базы сохраняются",
                "down всегда удаляет volume",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "-v — volume so'zining birinchi harfi.",
            "hint_ru": "-v — первая буква слова volume.",
            "explanation": "Oddiy down volume'ni saqlaydi, shuning uchun ma'lumot qoladi. down -v volume'ni ham o'chiradi va ma'lumot yo'qoladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "healthcheck va depends_on", "title_ru": "healthcheck и depends_on",
            "description": "Nega depends_on bilan birga healthcheck va condition: service_healthy ishlatiladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем вместе с depends_on используют healthcheck и condition: service_healthy? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Oddiy depends_on faqat baza konteyneri boshlanishini kutadi, baza so'rov qabul qilishga tayyor bo'lishini emas. healthcheck bazaning haqiqatan tayyorligini tekshiradi va service_healthy shartida API faqat shundan keyin ishga tushadi, shuning uchun u ulana olmay yiqilmaydi.",
            "hint": "Konteyner ishga tushishi bilan baza tayyor bo'ladimi?",
            "hint_ru": "Готова ли база сразу после запуска контейнера?",
            "explanation": "Konteyner boshlanishi bilan ichidagi baza hali qabul qilishga tayyor bo'lmasligi mumkin. healthcheck haqiqiy tayyorlikni tekshiradi, service_healthy esa API'ni shu vaqtgacha kutdiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: xavfsiz image va CI ──────────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Production uchun image</h3>
<p>Ishlaydigan image hali yaxshi image emas. Bu darsda to'rtta yaxshilanish qilamiz: <strong>multi-stage build</strong>, <strong>root bo'lmagan foydalanuvchi</strong>, <strong>HEALTHCHECK</strong> va <strong>sirlarni .env da saqlash</strong>. Keyin hammasini GitHub Actions'da avtomatik tekshiramiz.</p>
<pre><code>__DOCKERFILE__</code></pre>
<ul>
  <li><strong>Multi-stage build.</strong> Birinchi bosqich (<code>AS builder</code>) kutubxonalarni <code>/install</code> ga o'rnatadi, ikkinchisi faqat tayyor natijani (<code>COPY --from=builder</code>) oladi. Build vositalari va keshlar yakuniy image'ga tushmaydi. Bizning kichik ilovada farq oz: bitta bosqichli image taxminan 259 MB, multi-stage esa taxminan 246 MB (kompilyatsiya kerak bo'lmagani uchun). Haqiqiy foyda kutubxonalarni <em>kompilyatsiya</em> qilish kerak bo'lganda (<code>gcc</code> va boshqa vositalar) seziladi: ular birinchi bosqichda qoladi.</li>
  <li><strong>Root bo'lmagan foydalanuvchi.</strong> Standart holatda konteynerdagi jarayon <code>root</code> bilan ishlaydi. Ilovaga xavfsizlik teshigi topilsa, hujumchi konteyner ichida to'liq huquq oladi. <code>useradd</code> va <code>USER appuser</code> jarayonni cheklangan foydalanuvchiga o'tkazadi. Tekshiruv natijasi: <code>docker compose exec api id</code> → <code>uid=10001(appuser)</code>.</li>
  <li><strong>HEALTHCHECK.</strong> Docker har 10 soniyada <code>/health</code> ni tekshiradi va konteyner holatiga <code>healthy</code> yoki <code>unhealthy</code> deb yozadi. Endi <code>docker compose ps</code> va <code>--wait</code> shunga tayanadi.</li>
  <li><strong>.dockerignore.</strong> <code>.env</code> image'ga tushmaydi (konteyner ichida <code>.env.example</code> bor, <code>.env</code> yo'q).</li>
</ul>

<h3>Sirlar: .env va compose.yaml</h3>
<p>Parolni <code>compose.yaml</code> ga yozmaymiz: u <code>.env</code> dan olinadi. <code>${POSTGRES_PASSWORD:?...}</code> belgisi o'zgaruvchi yo'q bo'lsa <strong>darhol xato beradi</strong>, standart parolni jimgina qo'ymaydi. Haqiqatan: <code>.env</code> yo'q bo'lganda <code>docker compose config</code> «required variable POSTGRES_PASSWORD is missing a value» xatosini beradi.</p>
<pre><code>__COMPOSE__</code></pre>
<p><code>.env.example</code> (git'da turadi) o'zgaruvchilar ro'yxatini ko'rsatadi, haqiqiy <code>.env</code> (git'ga <strong>qo'shilmaydi</strong>) esa parollarni saqlaydi. <code>restart: unless-stopped</code> server qayta yuklanganda yoki konteyner yiqilganda uni qayta ishga tushiradi.</p>
<pre><code>__ENV__</code></pre>
<pre><code>__BUILD__</code></pre>

<h3>GitHub Actions bilan tekshirish</h3>
<p>Har push'da butun to'plam ishga tushib, ishlashi tekshirilsa, «menda ishlayapti» yo'qoladi. <code>.github/workflows/docker.yml</code>:</p>
<pre class="mermaid">
flowchart LR
  A["git push / pull request"] --> B["checkout"]
  B --> C[".env yaratish (faqat CI uchun parol)"]
  C --> D["docker compose up -d --build --wait"]
  D --> E["curl: /health, POST /notes, GET /notes"]
  E --> F{"Hammasi o'tdimi?"}
  F -- "ha" --> G["yashil belgi"]
  F -- "yo'q" --> H["docker compose logs"]
  G --> I["docker compose down -v"]
  H --> I
</pre>
<pre><code>__WORKFLOW__</code></pre>
<ul>
  <li><code>curl --fail</code> HTTP xatosi (400 va undan yuqori) bo'lsa, buyruqni muvaffaqiyatsiz qiladi: shunda CI qizil bo'ladi.</li>
  <li><code>if: failure()</code> faqat xato bo'lganda loglarni chiqaradi, <code>if: always()</code> esa oxirida hamma narsani tozalaydi.</li>
  <li>Bu yerda CI uchun alohida parol (<code>ci-only-password</code>) ishlatiladi: haqiqiy sirlar kodda bo'lmaydi.</li>
</ul>"""

_L5_TEXT_RU = """<h3>Образ для production</h3>
<p>Работающий образ — ещё не хороший образ. В этом уроке мы сделаем четыре улучшения: <strong>multi-stage build</strong>, <strong>пользователь без root</strong>, <strong>HEALTHCHECK</strong> и <strong>хранение секретов в .env</strong>. Затем проверим всё автоматически в GitHub Actions.</p>
<pre><code>__DOCKERFILE__</code></pre>
<ul>
  <li><strong>Multi-stage build.</strong> Первый этап (<code>AS builder</code>) устанавливает библиотеки в <code>/install</code>, а второй берёт только готовый результат (<code>COPY --from=builder</code>). Инструменты сборки и кеши не попадают в итоговый образ. В нашем небольшом приложении разница невелика: образ с одним этапом около 259 МБ, multi-stage около 246 МБ (компиляция не требуется). Настоящая польза заметна, когда библиотеки нужно <em>компилировать</em> (<code>gcc</code> и другие инструменты): они остаются на первом этапе.</li>
  <li><strong>Пользователь без root.</strong> По умолчанию процесс в контейнере работает от <code>root</code>. Если в приложении найдут уязвимость, злоумышленник получит полные права внутри контейнера. <code>useradd</code> и <code>USER appuser</code> переводят процесс на ограниченного пользователя. Результат проверки: <code>docker compose exec api id</code> → <code>uid=10001(appuser)</code>.</li>
  <li><strong>HEALTHCHECK.</strong> Docker каждые 10 секунд проверяет <code>/health</code> и записывает в состояние контейнера <code>healthy</code> или <code>unhealthy</code>. На это теперь опираются <code>docker compose ps</code> и <code>--wait</code>.</li>
  <li><strong>.dockerignore.</strong> Файл <code>.env</code> не попадает в образ (в контейнере есть <code>.env.example</code>, но нет <code>.env</code>).</li>
</ul>

<h3>Секреты: .env и compose.yaml</h3>
<p>Пароль мы не пишем в <code>compose.yaml</code>: он берётся из <code>.env</code>. Запись <code>${POSTGRES_PASSWORD:?...}</code> <strong>сразу выдаёт ошибку</strong>, если переменной нет, а не подставляет пароль по умолчанию втихую. Проверено: если файла <code>.env</code> нет, <code>docker compose config</code> сообщает «required variable POSTGRES_PASSWORD is missing a value».</p>
<pre><code>__COMPOSE__</code></pre>
<p><code>.env.example</code> (лежит в git) показывает список переменных, а настоящий <code>.env</code> (в git <strong>не добавляется</strong>) хранит пароли. <code>restart: unless-stopped</code> перезапускает контейнер при перезагрузке сервера или падении.</p>
<pre><code>__ENV__</code></pre>
<pre><code>__BUILD__</code></pre>

<h3>Проверка через GitHub Actions</h3>
<p>Если при каждом push весь набор запускается и проверяется, проблема «у меня работает» исчезает. Файл <code>.github/workflows/docker.yml</code>:</p>
<pre class="mermaid">
flowchart LR
  A["git push / pull request"] --> B["checkout"]
  B --> C["создание .env (пароль только для CI)"]
  C --> D["docker compose up -d --build --wait"]
  D --> E["curl: /health, POST /notes, GET /notes"]
  E --> F{"Всё прошло?"}
  F -- "да" --> G["зелёная отметка"]
  F -- "нет" --> H["docker compose logs"]
  G --> I["docker compose down -v"]
  H --> I
</pre>
<pre><code>__WORKFLOW__</code></pre>
<ul>
  <li><code>curl --fail</code> завершает команду ошибкой при HTTP-ошибке (400 и выше): тогда CI становится красным.</li>
  <li><code>if: failure()</code> выводит логи только при ошибке, а <code>if: always()</code> в конце всё очищает.</li>
  <li>Здесь для CI используется отдельный пароль (<code>ci-only-password</code>): настоящие секреты в коде не хранятся.</li>
</ul>"""

_L5_BLOCKS = dict(DOCKERFILE=DOCKERFILE_L5, COMPOSE=COMPOSE_L5, ENV=ENV_EXAMPLE, BUILD=CMD_L5_BUILD, WORKFLOW=WORKFLOW_YML)

LESSON_5 = {
    "order": 4,
    "title": "5-Xavfsiz image: multi-stage, non-root va CI",
    "title_ru": "5-Безопасный образ: multi-stage, non-root и CI",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": DOCKERFILE_L5,
    "code_content_ru": DOCKERFILE_L5,
    "code_language": "dockerfile",
    "sample": {
        "title": "Namuna: multi-stage Dockerfile va GitHub Actions workflow",
        "title_ru": "Пример: multi-stage Dockerfile и workflow GitHub Actions",
        "description": "Root bo'lmagan foydalanuvchi, HEALTHCHECK, .env bilan compose.yaml va CI'da Compose'ni tekshiruvchi workflow.",
        "description_ru": "Пользователь без root, HEALTHCHECK, compose.yaml с .env и workflow, проверяющий Compose в CI.",
        "sample_type": "code",
        "code_files": [
            {"filename": "Dockerfile", "language": "dockerfile", "code": DOCKERFILE_L5},
            {"filename": "compose.yaml", "language": "yaml", "code": COMPOSE_L5},
            {"filename": ".env.example", "language": "text", "code": ENV_EXAMPLE},
            {"filename": ".github/workflows/docker.yml", "language": "yaml", "code": WORKFLOW_YML},
        ],
    },
    "exercises": [
        {
            "title": "Root'dan voz kechish", "title_ru": "Отказ от root",
            "description": "Nega konteyner ichidagi ilova root bilan emas, cheklangan foydalanuvchi bilan ishlashi kerak?",
            "description_ru": "Почему приложение в контейнере должно работать не от root, а от ограниченного пользователя?",
            "exercise_type": "multiple_choice",
            "options": [
                "Ilovada zaiflik topilsa, hujumchining huquqi cheklangan bo'ladi",
                "Root bilan ilova ishlamaydi",
                "Root bilan image katta bo'lib ketadi",
                "Cheklangan foydalanuvchi portlarni ochadi",
            ],
            "options_ru": [
                "Если в приложении найдут уязвимость, права злоумышленника будут ограничены",
                "От root приложение не работает",
                "От root образ становится больше",
                "Ограниченный пользователь открывает порты",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Gap xavfsizlik haqida, tezlik haqida emas.",
            "hint_ru": "Речь о безопасности, а не о скорости.",
            "explanation": "Root bilan ishlagan jarayon buzilsa, hujumchi konteyner ichida to'liq huquq oladi. Cheklangan foydalanuvchi zararni kamaytiradi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Bosqichlarni nusxalash", "title_ru": "Копирование между этапами",
            "description": "Multi-stage build'da oldingi bosqichdan fayl olish: COPY ___=builder /install /usr/local",
            "description_ru": "Получение файлов из предыдущего этапа в multi-stage build: COPY ___=builder /install /usr/local",
            "exercise_type": "fill_in_blank",
            "correct_answers": "--from",
            "hint": "«...dan» inglizcha «from», ikkita chiziqcha bilan.",
            "hint_ru": "«Из» по-английски «from», с двумя дефисами.",
            "explanation": "COPY --from=builder oldingi bosqichning natijasini keyingi bosqichga ko'chiradi; build vositalari yakuniy image'ga tushmaydi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "CI zanjiri", "title_ru": "Цепочка CI",
            "description": "GitHub Actions workflow'idagi qadamlar tartibini joylashtiring.",
            "description_ru": "Расположите шаги workflow GitHub Actions по порядку.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["actions/checkout bilan kodni olish", ".env faylini yaratish", "docker compose up -d --build --wait", "curl --fail bilan /health va /notes ni tekshirish", "docker compose down -v bilan tozalash"],
            "drag_items_ru": ["Получить код через actions/checkout", "Создать файл .env", "docker compose up -d --build --wait", "Проверить /health и /notes через curl --fail", "Очистить через docker compose down -v"],
            "correct_order": ["actions/checkout bilan kodni olish", ".env faylini yaratish", "docker compose up -d --build --wait", "curl --fail bilan /health va /notes ni tekshirish", "docker compose down -v bilan tozalash"],
            "hint": "Tekshirishdan oldin to'plam ishga tushgan va tayyor bo'lishi kerak.",
            "hint_ru": "Перед проверкой набор должен быть запущен и готов.",
            "explanation": "Kod olinadi, .env yaratiladi, to'plam ishga tushib tayyor bo'lguncha kutiladi, so'ng curl bilan tekshiriladi va oxirida hammasi tozalanadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Sirlar bilan ishlash", "title_ru": "Работа с секретами",
            "description": "Parollar bilan ishlashda qaysi qoidalar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие правила работы с паролями верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                ".env git'ga qo'shilmaydi, .env.example esa qo'shiladi",
                "${VAR:?xabar} o'zgaruvchi yo'q bo'lsa darhol xato beradi",
                ".env .dockerignore orqali image'ga tushmaydi",
                "Haqiqiy parol compose.yaml ga yoziladi va git'ga qo'shiladi",
            ],
            "options_ru": [
                ".env не добавляют в git, а .env.example добавляют",
                "${VAR:?сообщение} сразу выдаёт ошибку, если переменной нет",
                ".env не попадает в образ благодаря .dockerignore",
                "Настоящий пароль пишут в compose.yaml и добавляют в git",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Haqiqiy parol hech qachon git'ga tushmasligi kerak.",
            "hint_ru": "Настоящий пароль никогда не должен попадать в git.",
            "explanation": "Parol .env da turadi (git va image'dan tashqarida), .env.example esa faqat nomlarni ko'rsatadi, ${VAR:?...} esa o'zgaruvchi unutilsa jimgina xatoga yo'l qo'ymaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Multi-stage foydasi", "title_ru": "Польза multi-stage",
            "description": "Multi-stage build qachon haqiqiy foyda beradi va nega bizning misolda farq kichik? O'z so'zingiz bilan yozing.",
            "description_ru": "Когда multi-stage build даёт реальную пользу и почему в нашем примере разница небольшая? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Multi-stage build kutubxonalarni kompilyatsiya qilish uchun build vositalari (gcc va boshqalar) kerak bo'lganda foyda beradi: ular birinchi bosqichda qoladi va yakuniy image'ga tushmaydi. Bizning ilovada kompilyatsiya kerak emas, shuning uchun image taxminan 259 MB dan 246 MB ga tushadi xolos.",
            "hint": "Qaysi vositalar faqat yig'ish paytida kerak bo'ladi?",
            "hint_ru": "Какие инструменты нужны только во время сборки?",
            "explanation": "Multi-stage yakuniy image'dan build vositalarini chiqarib tashlaydi. Kompilyatsiya talab qilinmasa, tejalgan joy ozgina bo'ladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>Asoslar:</strong> image va konteyner, <code>docker run</code>, <code>ps</code>, <code>logs</code>, <code>exec</code>, <code>stop</code>, <code>rm</code>.</li>
  <li><strong>Dockerfile:</strong> <code>FROM</code>, <code>WORKDIR</code>, <code>COPY</code>, <code>RUN</code>, <code>CMD</code>, layer keshi, <code>.dockerignore</code>.</li>
  <li><strong>Ma'lumot va sozlama:</strong> <code>-p</code>, <code>-e</code>, <code>--env-file</code>, volume.</li>
  <li><strong>Compose:</strong> <code>compose.yaml</code>, <code>healthcheck</code>, <code>depends_on</code>, <code>up --wait</code>, <code>down -v</code>.</li>
  <li><strong>Xavfsizlik va CI:</strong> multi-stage, root bo'lmagan foydalanuvchi, <code>HEALTHCHECK</code>, <code>.env</code>, GitHub Actions.</li>
</ul>

<h3>Tez-tez uchraydigan xatolar</h3>
<ul>
  <li>Ilova <code>127.0.0.1</code> da tinglaydi va <code>-p</code> ishlamaydi: <code>--host 0.0.0.0</code> qo'ying.</li>
  <li>API bazaga <code>localhost</code> orqali ulanmoqchi bo'ladi: Compose'da xizmat nomi (<code>db</code>) ishlatiladi.</li>
  <li><code>COPY . .</code> ni <code>pip install</code> dan oldin yozish: har o'zgarishda kutubxonalar qayta o'rnatiladi.</li>
  <li><code>.env</code> ni git'ga qo'shib yuborish yoki parolni Dockerfile'ga yozish.</li>
  <li><code>down -v</code> ni bilmasdan ishlatib, baza ma'lumotini yo'qotish.</li>
  <li>Image'ga <code>latest</code> tegi bilan ishonish: qaysi versiya ekani noma'lum. Versiyani aniq yozing (<code>postgres:16-alpine</code>, <code>python:3.12-slim</code>).</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Quyida butun loyiha tarkibi. Hammasi birga ishlaydi: <code>cp .env.example .env</code>, so'ng <code>docker compose up -d --build --wait</code>, <code>curl http://127.0.0.1:8000/health</code>. Loyihada ilova (<code>main.py</code>, <code>requirements.txt</code>), <code>Dockerfile</code>, <code>.dockerignore</code>, <code>compose.yaml</code>, <code>.env.example</code> va <code>.github/workflows/docker.yml</code> bor. Loyihaning <code>README</code> faylida ishga tushirish buyruqlari yozilgan bo'lishi kerak: boshqa odam faqat shu fayl bo'yicha uni ishga tushira olishi shart.</p>
<pre><code>__DOCKERFILE__</code></pre>
<pre><code>__COMPOSE__</code></pre>
<p>Keyingi bosqich — vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, <strong>o'z API'ngizni</strong> (FastAPI, Flask yoki Express) shu usulda konteynerga o'rang.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>Основы:</strong> образ и контейнер, <code>docker run</code>, <code>ps</code>, <code>logs</code>, <code>exec</code>, <code>stop</code>, <code>rm</code>.</li>
  <li><strong>Dockerfile:</strong> <code>FROM</code>, <code>WORKDIR</code>, <code>COPY</code>, <code>RUN</code>, <code>CMD</code>, кеш слоёв, <code>.dockerignore</code>.</li>
  <li><strong>Данные и настройки:</strong> <code>-p</code>, <code>-e</code>, <code>--env-file</code>, volume.</li>
  <li><strong>Compose:</strong> <code>compose.yaml</code>, <code>healthcheck</code>, <code>depends_on</code>, <code>up --wait</code>, <code>down -v</code>.</li>
  <li><strong>Безопасность и CI:</strong> multi-stage, пользователь без root, <code>HEALTHCHECK</code>, <code>.env</code>, GitHub Actions.</li>
</ul>

<h3>Частые ошибки</h3>
<ul>
  <li>Приложение слушает на <code>127.0.0.1</code>, и <code>-p</code> не работает: укажите <code>--host 0.0.0.0</code>.</li>
  <li>API пытается подключиться к базе через <code>localhost</code>: в Compose используется имя сервиса (<code>db</code>).</li>
  <li><code>COPY . .</code> перед <code>pip install</code>: при каждом изменении библиотеки переустанавливаются.</li>
  <li>Добавить <code>.env</code> в git или записать пароль в Dockerfile.</li>
  <li>Выполнить <code>down -v</code> не зная последствий и потерять данные базы.</li>
  <li>Полагаться на тег <code>latest</code>: неизвестно, какая это версия. Указывайте версию явно (<code>postgres:16-alpine</code>, <code>python:3.12-slim</code>).</li>
</ul>

<h3>Готовое решение</h3>
<p>Ниже состав всего проекта. Всё работает вместе: <code>cp .env.example .env</code>, затем <code>docker compose up -d --build --wait</code>, <code>curl http://127.0.0.1:8000/health</code>. В проекте есть приложение (<code>main.py</code>, <code>requirements.txt</code>), <code>Dockerfile</code>, <code>.dockerignore</code>, <code>compose.yaml</code>, <code>.env.example</code> и <code>.github/workflows/docker.yml</code>. В файле <code>README</code> проекта должны быть записаны команды запуска: другой человек обязан суметь запустить проект только по нему.</p>
<pre><code>__DOCKERFILE__</code></pre>
<pre><code>__COMPOSE__</code></pre>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, упакуйте в контейнер <strong>собственный API</strong> (FastAPI, Flask или Express) тем же способом.</p>"""

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: o'z API'ngizni konteynerga o'rang",
    "title_ru": "6-Повторение: упакуйте собственный API в контейнер",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, DOCKERFILE=DOCKERFILE_L5, COMPOSE=COMPOSE_L5),
    "text_content_ru": _fill(_L6_TEXT_RU, DOCKERFILE=DOCKERFILE_L5, COMPOSE=COMPOSE_L5),
    "code_content": COMPOSE_L5,
    "code_content_ru": COMPOSE_L5,
    "code_language": "yaml",
    "sample": {
        "title": "Namuna: to'liq konteynerlangan Notes API",
        "title_ru": "Пример: полностью упакованный в контейнеры Notes API",
        "description": "Ilova, Dockerfile, .dockerignore, compose.yaml, .env.example va GitHub Actions workflow'i: bir buyruqda ishga tushadi.",
        "description_ru": "Приложение, Dockerfile, .dockerignore, compose.yaml, .env.example и workflow GitHub Actions: запускается одной командой.",
        "sample_type": "code",
        "code_files": [
            {"filename": "main.py", "language": "python", "code": MAIN_DB},
            {"filename": "requirements.txt", "language": "text", "code": REQUIREMENTS_L4},
            {"filename": "Dockerfile", "language": "dockerfile", "code": DOCKERFILE_L5},
            {"filename": ".dockerignore", "language": "text", "code": DOCKERIGNORE},
            {"filename": "compose.yaml", "language": "yaml", "code": COMPOSE_L5},
            {"filename": ".env.example", "language": "text", "code": ENV_EXAMPLE},
            {"filename": ".github/workflows/docker.yml", "language": "yaml", "code": WORKFLOW_YML},
        ],
    },
    "task": {
        "task_title": "Loyiha: o'z API'ngizni Docker va Compose bilan ishga tushiring",
        "task_title_ru": "Проект: запустите собственный API через Docker и Compose",
        "task_description": "O'zingizning API'ngizni (FastAPI, Flask yoki Express) va unga kerak bo'lgan PostgreSQL'ni Docker Compose bilan bir buyruqda ishga tushadigan qiling: Dockerfile, .dockerignore, compose.yaml, .env.example va README yozing, GitHub Actions bilan tekshiring.",
        "task_description_ru": "Сделайте так, чтобы ваш API (FastAPI, Flask или Express) и нужная ему PostgreSQL запускались одной командой через Docker Compose: напишите Dockerfile, .dockerignore, compose.yaml, .env.example и README, проверьте через GitHub Actions.",
        "task_requirements": (
            "1) Dockerfile: kutubxonalar kodni nusxalashdan oldin o'rnatiladi (layer keshi), ilova 0.0.0.0 da tinglaydi, root bo'lmagan foydalanuvchi (USER) va HEALTHCHECK bor. "
            "2) .dockerignore: .env, .git va keraksiz fayllar image'ga tushmaydi. "
            "3) compose.yaml: API va PostgreSQL, baza uchun volume va healthcheck, API uchun depends_on (condition: service_healthy). "
            "4) Parollar .env da, .env.example repozitoriyda, .env esa git'da yo'q; baza manzili DATABASE_URL o'zgaruvchisidan olinadi. "
            "5) docker compose up -d --build --wait bilan ishga tushadi, ma'lumot docker compose down dan keyin saqlanadi. "
            "6) README da ishga tushirish buyruqlari yozilgan. "
            "7) .github/workflows/docker.yml: compose'ni ishga tushirib, curl --fail bilan kamida ikki endpoint'ni tekshiradi."
        ),
        "task_requirements_ru": (
            "1) Dockerfile: библиотеки устанавливаются до копирования кода (кеш слоёв), приложение слушает 0.0.0.0, есть пользователь без root (USER) и HEALTHCHECK. "
            "2) .dockerignore: .env, .git и лишние файлы не попадают в образ. "
            "3) compose.yaml: API и PostgreSQL, для базы volume и healthcheck, для API depends_on (condition: service_healthy). "
            "4) Пароли в .env, в репозитории .env.example, а .env в git отсутствует; адрес базы берётся из переменной DATABASE_URL. "
            "5) Запускается через docker compose up -d --build --wait, данные сохраняются после docker compose down. "
            "6) В README записаны команды запуска. "
            "7) .github/workflows/docker.yml: запускает compose и проверяет через curl --fail как минимум два эндпоинта."
        ),
        "task_technologies": "Docker, Docker Compose, PostgreSQL, GitHub Actions",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Hammasini bog'lang", "title_ru": "Соедините всё вместе",
            "description": "Qaysi variant to'liq konteynerlangan loyihaning ishga tushirish tartibini to'g'ri ko'rsatadi?",
            "description_ru": "Какой вариант верно показывает порядок запуска полностью упакованного проекта?",
            "exercise_type": "multiple_choice",
            "options": [
                ".env.example dan .env yaratish → docker compose up -d --build --wait → curl bilan tekshirish",
                "docker compose down -v → .env ni git'ga qo'shish → up",
                "Parolni Dockerfile'ga yozish → docker run → down",
                "curl bilan tekshirish → .env yaratish → build",
            ],
            "options_ru": [
                "создать .env из .env.example → docker compose up -d --build --wait → проверить через curl",
                "docker compose down -v → добавить .env в git → up",
                "записать пароль в Dockerfile → docker run → down",
                "проверить через curl → создать .env → build",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Avval sozlama, keyin ishga tushirish, oxirida tekshirish.",
            "hint_ru": "Сначала настройка, затем запуск, в конце проверка.",
            "explanation": "Sozlama .env.example asosida tayyorlanadi, to'plam up --wait bilan ishga tushib tayyor bo'lguncha kutiladi, keyin curl bilan tekshiriladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Compose'ni to'xtatish", "title_ru": "Остановка Compose",
            "description": "Konteynerlarni o'chirib, volume'ni (ma'lumot bilan) saqlab qoladigan buyruq: docker compose ___",
            "description_ru": "Команда, удаляющая контейнеры, но сохраняющая volume (вместе с данными): docker compose ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "down",
            "hint": "-v siz ishlatiladigan variant.",
            "hint_ru": "Вариант без флага -v.",
            "explanation": "docker compose down konteynerlar va tarmoqni o'chiradi, nomli volume saqlanadi. Volume'ni ham o'chirish uchun down -v ishlatiladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Loyihani tekshirish", "title_ru": "Проверка проекта",
            "description": "Konteynerlangan loyihangiz to'g'ri ekanini qaysi tekshiruvlar bilan isbotlaysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Какими проверками вы докажете, что ваш упакованный проект работает правильно? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Toza muhitda faqat .env.example dan .env yaratib docker compose up -d --build --wait ni ishga tushiraman, curl --fail bilan /health va asosiy endpoint'larni tekshiraman, docker compose down dan keyin ma'lumot saqlanishini ko'raman va docker compose exec orqali jarayon root emasligini (id) tekshiraman. Xuddi shu ni GitHub Actions workflow'i har push'da bajaradi.",
            "hint": "Ishga tushish, endpoint'lar, ma'lumot saqlanishi va xavfsizlikni o'ylab ko'ring.",
            "hint_ru": "Подумайте о запуске, эндпоинтах, сохранении данных и безопасности.",
            "explanation": "Yaxshi tekshiruv butun yo'lni qamraydi: toza ishga tushish, ishlayotgan endpoint'lar, volume'dagi ma'lumot va root bo'lmagan foydalanuvchi. CI buni avtomatlashtiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
