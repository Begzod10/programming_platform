"""Course spec: Express: API testlash (Jest va supertest) — 6 lessons, UZ + RU.

A Notes API (Express + JWT + a repository layer) is tested in stages: Jest basics ->
supertest route tests -> authenticated route tests -> mocking the data layer ->
coverage + CI -> project. Every code constant below is materialised into a real Node
project and run with Jest by the verification script before a lesson text may use it.
API messages are English so the code is identical in UZ and RU.
"""
from __future__ import annotations

# ── Stage code (single source of truth for lessons 1-6) ──────────────────────

PACKAGE_L1 = '''{
  "name": "notes-api",
  "version": "1.0.0",
  "scripts": {
    "start": "node src/server.js",
    "test": "jest"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^7.0.0"
  }
}
'''

CODE_VALIDATE = '''function validateNoteText(text) {
  if (typeof text !== "string") return "text is required";
  const trimmed = text.trim();
  if (trimmed.length < 3) return "text must be at least 3 characters";
  if (trimmed.length > 200) return "text must be at most 200 characters";
  return null;
}

module.exports = { validateNoteText };
'''

TEST_VALIDATE = '''const { validateNoteText } = require("../src/validate");

describe("validateNoteText", () => {
  test("accepts a normal text", () => {
    expect(validateNoteText("buy bread")).toBeNull();
  });

  test("trims spaces before counting", () => {
    expect(validateNoteText("  ab  ")).toBe("text must be at least 3 characters");
  });

  test.each([
    [undefined, "text is required"],
    [42, "text is required"],
    ["", "text must be at least 3 characters"],
    ["x".repeat(201), "text must be at most 200 characters"],
  ])("rejects %p", (input, message) => {
    expect(validateNoteText(input)).toBe(message);
  });
});
'''

CODE_REPO = '''const users = [];
const notes = [];
let nextUserId = 1;
let nextNoteId = 1;

module.exports = {
  async findUserByName(username) {
    return users.find((u) => u.username === username) || null;
  },
  async createUser({ username, passwordHash, role }) {
    const user = { id: nextUserId++, username, passwordHash, role };
    users.push(user);
    return user;
  },
  async listUsers() {
    return users.map(({ id, username, role }) => ({ id, username, role }));
  },
  async listNotes(ownerId) {
    return ownerId === null ? [...notes] : notes.filter((n) => n.ownerId === ownerId);
  },
  async createNote({ text, ownerId }) {
    const note = { id: nextNoteId++, text, ownerId };
    notes.push(note);
    return note;
  },
  async findNote(id) {
    return notes.find((n) => n.id === id) || null;
  },
  async deleteNote(id) {
    const index = notes.findIndex((n) => n.id === id);
    if (index !== -1) notes.splice(index, 1);
  },
  async reset() {
    users.length = 0;
    notes.length = 0;
    nextUserId = 1;
    nextNoteId = 1;
  },
};
'''

CODE_APP = '''const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const repo = require("./repo");
const { validateNoteText } = require("./validate");

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || "dev-only-change-me-use-a-long-random-key";
const BCRYPT_ROUNDS = process.env.NODE_ENV === "test" ? 4 : 10;

const handle = (fn) => (req, res, next) => fn(req, res, next).catch(next);

function auth(req, res, next) {
  const [scheme, token] = (req.headers.authorization || "").split(" ");
  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({ error: "authorization token is required" });
  }
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch (err) {
    const message = err.name === "TokenExpiredError" ? "token has expired" : "token is invalid";
    res.status(401).json({ error: message });
  }
}

function adminOnly(req, res, next) {
  if (req.user.role !== "admin") return res.status(403).json({ error: "admin only" });
  next();
}

app.post("/api/register", handle(async (req, res) => {
  const { username, password } = req.body || {};
  if (typeof username !== "string" || username.trim().length < 3 || typeof password !== "string" || password.length < 6) {
    return res.status(400).json({ error: "username needs 3+ and password 6+ characters" });
  }
  if (await repo.findUserByName(username.trim())) {
    return res.status(409).json({ error: "username is taken" });
  }
  const role = username.trim() === process.env.ADMIN_USERNAME ? "admin" : "user";
  const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
  await repo.createUser({ username: username.trim(), passwordHash, role });
  res.status(201).json({ message: "registered" });
}));

app.post("/api/login", handle(async (req, res) => {
  const { username, password } = req.body || {};
  const user = await repo.findUserByName(typeof username === "string" ? username.trim() : "");
  if (!user || !(await bcrypt.compare(String(password || ""), user.passwordHash))) {
    return res.status(401).json({ error: "invalid username or password" });
  }
  const token = jwt.sign({ sub: String(user.id), role: user.role }, JWT_SECRET, { expiresIn: "30m" });
  res.json({ token, username: user.username });
}));

app.get("/api/notes", auth, handle(async (req, res) => {
  const ownerId = req.user.role === "admin" ? null : Number(req.user.sub);
  res.json(await repo.listNotes(ownerId));
}));

app.post("/api/notes", auth, handle(async (req, res) => {
  const problem = validateNoteText((req.body || {}).text);
  if (problem) return res.status(400).json({ error: problem });
  const note = await repo.createNote({ text: req.body.text.trim(), ownerId: Number(req.user.sub) });
  res.status(201).json(note);
}));

app.delete("/api/notes/:id", auth, handle(async (req, res) => {
  const note = await repo.findNote(Number(req.params.id));
  if (!note) return res.status(404).json({ error: "note not found" });
  if (note.ownerId !== Number(req.user.sub) && req.user.role !== "admin") {
    return res.status(403).json({ error: "not your note" });
  }
  await repo.deleteNote(note.id);
  res.json({ message: "deleted" });
}));

app.get("/api/admin/users", auth, adminOnly, handle(async (req, res) => {
  res.json(await repo.listUsers());
}));

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  res.status(500).json({ error: "internal server error" });
});

module.exports = app;
'''

CODE_SERVER = '''const app = require("./app");

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Notes API listening on http://127.0.0.1:${port}`));
'''

TEST_AUTH = '''const request = require("supertest");

const app = require("../src/app");
const repo = require("../src/repo");

beforeEach(() => repo.reset());

describe("POST /api/register", () => {
  test("creates a user", async () => {
    const res = await request(app).post("/api/register").send({ username: "ali", password: "secret12" });
    expect(res.status).toBe(201);
    expect(res.body).toEqual({ message: "registered" });
  });

  test("rejects a short password", async () => {
    const res = await request(app).post("/api/register").send({ username: "ali", password: "123" });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/password/);
  });

  test("rejects a duplicate username", async () => {
    const body = { username: "ali", password: "secret12" };
    await request(app).post("/api/register").send(body);
    const res = await request(app).post("/api/register").send(body);
    expect(res.status).toBe(409);
  });
});

describe("POST /api/login", () => {
  beforeEach(() => request(app).post("/api/register").send({ username: "ali", password: "secret12" }));

  test("returns a token for the right password", async () => {
    const res = await request(app).post("/api/login").send({ username: "ali", password: "secret12" });
    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toMatch(/json/);
    expect(res.body.token.split(".")).toHaveLength(3);
    expect(res.body.username).toBe("ali");
  });

  test("returns 401 for a wrong password", async () => {
    const res = await request(app).post("/api/login").send({ username: "ali", password: "wrong" });
    expect(res.status).toBe(401);
    expect(res.body.token).toBeUndefined();
  });
});
'''

TEST_NOTES = '''const request = require("supertest");
const jwt = require("jsonwebtoken");

const app = require("../src/app");
const repo = require("../src/repo");

const SECRET = "dev-only-change-me-use-a-long-random-key";

async function loginAs(username) {
  await request(app).post("/api/register").send({ username, password: "secret12" });
  const res = await request(app).post("/api/login").send({ username, password: "secret12" });
  return { Authorization: `Bearer ${res.body.token}` };
}

beforeEach(() => repo.reset());
afterEach(() => delete process.env.ADMIN_USERNAME);

describe("authentication", () => {
  test("a request without a token gets 401", async () => {
    const res = await request(app).get("/api/notes");
    expect(res.status).toBe(401);
  });

  test("a broken token gets 401", async () => {
    const res = await request(app).get("/api/notes").set("Authorization", "Bearer garbage");
    expect(res.status).toBe(401);
    expect(res.body.error).toBe("token is invalid");
  });

  test("an expired token gets its own message", async () => {
    const expired = jwt.sign({ sub: "1", role: "user" }, SECRET, { expiresIn: -1 });
    const res = await request(app).get("/api/notes").set("Authorization", `Bearer ${expired}`);
    expect(res.status).toBe(401);
    expect(res.body.error).toBe("token has expired");
  });
});

describe("notes", () => {
  test("a user creates and lists their own notes", async () => {
    const ali = await loginAs("ali");
    const created = await request(app).post("/api/notes").set(ali).send({ text: "buy bread" });
    expect(created.status).toBe(201);
    expect(created.body).toMatchObject({ text: "buy bread", ownerId: 1 });
    const list = await request(app).get("/api/notes").set(ali);
    expect(list.body).toHaveLength(1);
  });

  test("a note with a bad text is rejected", async () => {
    const ali = await loginAs("ali");
    const res = await request(app).post("/api/notes").set(ali).send({ text: "x" });
    expect(res.status).toBe(400);
  });

  test("users cannot see or delete each other's notes", async () => {
    const ali = await loginAs("ali");
    const vali = await loginAs("vali");
    await request(app).post("/api/notes").set(ali).send({ text: "ali note" });
    expect((await request(app).get("/api/notes").set(vali)).body).toEqual([]);
    expect((await request(app).delete("/api/notes/1").set(vali)).status).toBe(403);
    expect((await request(app).delete("/api/notes/1").set(ali)).status).toBe(200);
    expect((await request(app).delete("/api/notes/1").set(ali)).status).toBe(404);
  });

  test("an admin sees every note and may list users", async () => {
    process.env.ADMIN_USERNAME = "boss";
    const boss = await loginAs("boss");
    const ali = await loginAs("ali");
    await request(app).post("/api/notes").set(ali).send({ text: "ali note" });
    expect((await request(app).get("/api/notes").set(boss)).body).toHaveLength(1);
    expect((await request(app).get("/api/admin/users").set(boss)).status).toBe(200);
    expect((await request(app).get("/api/admin/users").set(ali)).status).toBe(403);
  });
});
'''

TEST_ERRORS = '''const request = require("supertest");
const jwt = require("jsonwebtoken");

jest.mock("../src/repo");

const app = require("../src/app");
const repo = require("../src/repo");

const token = jwt.sign({ sub: "7", role: "user" }, "dev-only-change-me-use-a-long-random-key");
const authHeader = { Authorization: `Bearer ${token}` };

beforeEach(() => jest.resetAllMocks());

test("the route passes the right arguments to the data layer", async () => {
  repo.createNote.mockResolvedValue({ id: 1, text: "buy bread", ownerId: 7 });
  const res = await request(app).post("/api/notes").set(authHeader).send({ text: "  buy bread  " });
  expect(res.status).toBe(201);
  expect(repo.createNote).toHaveBeenCalledTimes(1);
  expect(repo.createNote).toHaveBeenCalledWith({ text: "buy bread", ownerId: 7 });
});

test("a regular user only asks for their own notes", async () => {
  repo.listNotes.mockResolvedValue([]);
  await request(app).get("/api/notes").set(authHeader);
  expect(repo.listNotes).toHaveBeenCalledWith(7);
});

test("a database failure becomes a clean 500 response", async () => {
  repo.listNotes.mockRejectedValue(new Error("db is down"));
  const res = await request(app).get("/api/notes").set(authHeader);
  expect(res.status).toBe(500);
  expect(res.body).toEqual({ error: "internal server error" });
});

test("invalid input never reaches the data layer", async () => {
  const res = await request(app).post("/api/notes").set(authHeader).send({ text: "x" });
  expect(res.status).toBe(400);
  expect(repo.createNote).not.toHaveBeenCalled();
});
'''

PACKAGE_L5 = '''{
  "name": "notes-api",
  "version": "1.0.0",
  "scripts": {
    "start": "node src/server.js",
    "test": "jest",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^7.0.0"
  },
  "jest": {
    "testEnvironment": "node",
    "collectCoverageFrom": ["src/**/*.js", "!src/server.js"],
    "coverageThreshold": {
      "global": { "lines": 90, "branches": 80 }
    }
  }
}
'''

WORKFLOW_YML = '''name: tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run test:coverage
'''

CMD_INSTALL = '''npm install express bcryptjs jsonwebtoken
npm install --save-dev jest supertest
npm test
'''

CMD_RUN = '''npm test
npm test -- tests/auth.test.js
npm test -- -t "login"
npm run test:coverage
'''


COURSE = {
    "title": "Express: API testlash (Jest va supertest)",
    "title_ru": "Express: тестирование API (Jest и supertest)",
    "description": (
        "Express API'ni avtomatik testlashni o'rganasiz: Jest bilan birinchi testlar, supertest bilan route'lar, "
        "token bilan himoyalangan route'lar, bazani mock qilish, coverage va GitHub Actions. "
        "Kurs oxirida o'z API'ngiz uchun to'liq test to'plami va CI yozasiz."
    ),
    "description_ru": (
        "Вы научитесь автоматически тестировать Express API: первые тесты на Jest, маршруты через supertest, "
        "маршруты под защитой токена, мок базы данных, coverage и GitHub Actions. "
        "В конце курса вы напишете полный набор тестов и CI для собственного API."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 7,
    "prerequisite_course_id": 74,
    "display_order": 207,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


# ── 1-dars: Jest bilan birinchi test ─────────────────────────────────────────

_L1_TEXT_UZ = """<h3>Nega testlash kerak</h3>
<p>API'ni qo'lda Postman bilan tekshirish dastlab yetarli ko'rinadi. Lekin route'lar ko'paygach, har o'zgarishdan keyin hammasini qayta bosib chiqish mumkin emas, kimdir bitta qatorni o'zgartirib boshqa joyni buzib qo'yishi esa tabiiy. <strong>Avtomatik test</strong> — bu kodni kodga tekshirtirish: bir buyruq bilan yuzlab holat sekundlarda tekshiriladi. Test uch ish qiladi: xatoni tez topadi, kodni xavfsiz o'zgartirishga imkon beradi (refaktoring) va API qanday ishlashi haqida tirik hujjat bo'ladi.</p>

<h3>Test turlari</h3>
<pre class="mermaid">
flowchart TD
  A["Unit test: bitta funksiya (tez, ko'p)"] --> B["Integration test: route + middleware + ma'lumotlar qatlami"]
  B --> C["End-to-end test: haqiqiy brauzer va server (sekin, kam)"]
</pre>
<ul>
  <li><strong>Unit</strong> — bitta funksiya, masalan <code>validateNoteText</code>. Juda tez va aniq.</li>
  <li><strong>Integration</strong> — so'rov route'dan middleware orqali o'tishi. Bu kursning asosiy qismi (2–4-darslar).</li>
  <li><strong>End-to-end</strong> — butun tizim, tashqaridan. Sekin, shuning uchun kam yoziladi.</li>
</ul>

<h3>Jest o'rnatish</h3>
<p><strong>Jest</strong> — JavaScript uchun eng ommabop test kutubxonasi: test topadi, ishga tushiradi va natijani chiroyli ko'rsatadi. Mavjud Notes API loyihangizda (<code>package.json</code> bor papkada):</p>
<pre><code>__INSTALL__</code></pre>
<p><code>--save-dev</code> test kutubxonalari faqat ishlab chiqish uchun ekanini bildiradi. <code>package.json</code> da <code>"test": "jest"</code> skripti bo'lishi kerak:</p>
<pre><code>__PACKAGE__</code></pre>

<h3>Birinchi unit test</h3>
<p>Tekshiriladigan funksiya: yozuv matnini tekshiradi va xato xabari yoki <code>null</code> qaytaradi.</p>
<pre><code>__VALIDATE__</code></pre>
<p>Test fayli <code>tests/</code> papkasida, nomi <code>*.test.js</code> bilan tugaydi: Jest shu nomdagi fayllarni o'zi topadi.</p>
<pre><code>__TEST__</code></pre>
<ul>
  <li><code>describe</code> — testlarni guruhlaydi, <code>test</code> (yoki <code>it</code>) — bitta tekshiruv.</li>
  <li><code>expect(qiymat)</code> keyin <em>matcher</em>: <code>toBe</code> (qat'iy tenglik), <code>toEqual</code> (obyektni chuqur solishtirish), <code>toBeNull</code>, <code>toMatch</code> (regex), <code>toHaveLength</code>, <code>toMatchObject</code> (obyektning bir qismi).</li>
  <li><code>test.each</code> bitta testni bir necha kirish bilan takrorlaydi; <code>%p</code> qiymatni test nomiga qo'yadi.</li>
</ul>

<h3>Ishga tushirish</h3>
<pre><code>__RUN__</code></pre>
<p>Birinchi buyruq hamma testni yurgizadi, ikkinchisi bitta faylni, uchinchisi nomi bo'yicha filtrlaydi (<code>-t</code>), to'rtinchisi esa 5-darsda o'rganiladigan coverage hisobotini beradi. Test muvaffaqiyatsiz bo'lsa, Jest qaysi qiymat kutilgani va nima kelganini ko'rsatadi: avval shu xabarni o'qing.</p>"""

_L1_TEXT_RU = """<h3>Зачем нужны тесты</h3>
<p>Проверять API вручную через Postman сначала кажется достаточным. Но когда маршрутов становится много, перепроверять всё после каждого изменения невозможно, а сломать одним изменением другое место очень легко. <strong>Автоматический тест</strong> — это код, который проверяет код: одной командой за секунды проверяются сотни случаев. Тест делает три вещи: быстро находит ошибку, позволяет безопасно менять код (рефакторинг) и служит живой документацией того, как работает API.</p>

<h3>Виды тестов</h3>
<pre class="mermaid">
flowchart TD
  A["Unit-тест: одна функция (быстро, много)"] --> B["Integration-тест: маршрут + middleware + слой данных"]
  B --> C["End-to-end тест: настоящий браузер и сервер (медленно, мало)"]
</pre>
<ul>
  <li><strong>Unit</strong> — одна функция, например <code>validateNoteText</code>. Очень быстро и точно.</li>
  <li><strong>Integration</strong> — путь запроса через маршрут и middleware. Это основная часть курса (уроки 2–4).</li>
  <li><strong>End-to-end</strong> — вся система снаружи. Медленно, поэтому таких тестов пишут мало.</li>
</ul>

<h3>Установка Jest</h3>
<p><strong>Jest</strong> — самая популярная библиотека тестирования для JavaScript: находит тесты, запускает их и красиво показывает результат. В существующем проекте Notes API (в папке с <code>package.json</code>):</p>
<pre><code>__INSTALL__</code></pre>
<p><code>--save-dev</code> означает, что библиотеки нужны только для разработки. В <code>package.json</code> должен быть скрипт <code>"test": "jest"</code>:</p>
<pre><code>__PACKAGE__</code></pre>

<h3>Первый unit-тест</h3>
<p>Тестируемая функция проверяет текст записи и возвращает сообщение об ошибке или <code>null</code>.</p>
<pre><code>__VALIDATE__</code></pre>
<p>Файл теста лежит в папке <code>tests/</code> и заканчивается на <code>*.test.js</code>: Jest сам находит файлы с таким именем.</p>
<pre><code>__TEST__</code></pre>
<ul>
  <li><code>describe</code> группирует тесты, <code>test</code> (или <code>it</code>) — одна проверка.</li>
  <li><code>expect(значение)</code>, затем <em>matcher</em>: <code>toBe</code> (строгое равенство), <code>toEqual</code> (глубокое сравнение объектов), <code>toBeNull</code>, <code>toMatch</code> (регулярное выражение), <code>toHaveLength</code>, <code>toMatchObject</code> (часть объекта).</li>
  <li><code>test.each</code> повторяет один тест с разными входными данными; <code>%p</code> подставляет значение в название теста.</li>
</ul>

<h3>Запуск</h3>
<pre><code>__RUN__</code></pre>
<p>Первая команда запускает все тесты, вторая — один файл, третья фильтрует по названию (<code>-t</code>), а четвёртая выдаёт отчёт coverage, о котором мы поговорим в уроке 5. Если тест упал, Jest показывает, какое значение ожидалось и что пришло: сначала читайте это сообщение.</p>"""

_L1_BLOCKS = dict(INSTALL=CMD_INSTALL, PACKAGE=PACKAGE_L1, VALIDATE=CODE_VALIDATE, TEST=TEST_VALIDATE, RUN=CMD_RUN)

LESSON_1 = {
    "order": 0,
    "title": "1-Nega testlash kerak: Jest bilan birinchi test",
    "title_ru": "1-Зачем тестировать: первый тест на Jest",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": TEST_VALIDATE,
    "code_content_ru": TEST_VALIDATE,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: Jest bilan unit test",
        "title_ru": "Пример: unit-тест на Jest",
        "description": "validateNoteText funksiyasi va uning describe, test, test.each bilan yozilgan testlari.",
        "description_ru": "Функция validateNoteText и её тесты на describe, test и test.each.",
        "sample_type": "code",
        "code_files": [
            {"filename": "package.json", "language": "json", "code": PACKAGE_L1},
            {"filename": "src/validate.js", "language": "javascript", "code": CODE_VALIDATE},
            {"filename": "tests/validate.test.js", "language": "javascript", "code": TEST_VALIDATE},
        ],
    },
    "exercises": [
        {
            "title": "Test fayli nomi", "title_ru": "Имя файла теста",
            "description": "Jest qaysi nomdagi fayllarni test deb topadi?",
            "description_ru": "Какие файлы Jest считает тестами?",
            "exercise_type": "multiple_choice",
            "options": ["Faqat test.js nomli fayl", "*.test.js (va *.spec.js) bilan tugaydigan fayllar", "Barcha .js fayllar", "Faqat src/ ichidagi fayllar"],
            "options_ru": ["Только файл с именем test.js", "Файлы, заканчивающиеся на *.test.js (и *.spec.js)", "Все .js файлы", "Только файлы внутри src/"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Nomi «.test.js» bilan tugaydi.",
            "hint_ru": "Название заканчивается на «.test.js».",
            "explanation": "Jest standart bo'yicha *.test.js va *.spec.js fayllarini (hamda __tests__ papkasidagilarini) topadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Obyektni solishtirish", "title_ru": "Сравнение объектов",
            "description": "Ikki obyektni chuqur (qiymati bo'yicha) solishtiradigan matcher: expect(a).___(b)",
            "description_ru": "Matcher, глубоко (по значению) сравнивающий два объекта: expect(a).___(b)",
            "exercise_type": "fill_in_blank",
            "correct_answers": "toEqual",
            "hint": "toBe emas: u faqat bir xil havolani qabul qiladi.",
            "hint_ru": "Не toBe: он принимает только ту же самую ссылку.",
            "explanation": "toEqual obyekt va massivlarni qiymati bo'yicha solishtiradi. toBe esa === bilan, ya'ni havola bo'yicha tekshiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Test tuzilishi", "title_ru": "Структура теста",
            "description": "Yaxshi testning qadamlarini tartibga soling.",
            "description_ru": "Расположите шаги хорошего теста по порядку.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Kerakli holatni tayyorlash (arrange)", "Tekshiriladigan kodni chaqirish (act)", "expect bilan natijani tekshirish (assert)"],
            "drag_items_ru": ["Подготовить нужное состояние (arrange)", "Вызвать проверяемый код (act)", "Проверить результат через expect (assert)"],
            "correct_order": ["Kerakli holatni tayyorlash (arrange)", "Tekshiriladigan kodni chaqirish (act)", "expect bilan natijani tekshirish (assert)"],
            "hint": "Avval tayyorgarlik, keyin harakat, oxirida tekshiruv.",
            "hint_ru": "Сначала подготовка, затем действие, в конце проверка.",
            "explanation": "Arrange-Act-Assert: holatni tayyorla, kodni chaqir, natijani tekshir. Shu tartib testni o'qishga oson qiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Testning foydasi", "title_ru": "Польза тестов",
            "description": "Avtomatik testlarning qaysi foydalari to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие преимущества автоматических тестов верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Kodni o'zgartirganda eski xatolar qaytganini tez bildiradi",
                "Refaktoringni xavfsiz qiladi",
                "Kodda xato bo'lishining oldini 100% kafolatlaydi",
                "Dasturchi kodni umuman o'qimasa ham bo'ladi",
            ],
            "options_ru": [
                "Быстро сообщают, что после изменения вернулись старые ошибки",
                "Делают рефакторинг безопасным",
                "На 100% гарантируют отсутствие ошибок в коде",
                "Разработчику вообще не нужно читать код",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Test xatolarni topadi, lekin ularning yo'qligini isbotlamaydi.",
            "hint_ru": "Тест находит ошибки, но не доказывает их отсутствие.",
            "explanation": "Testlar regressiyani tez topadi va refaktoringga ishonch beradi. Lekin ular faqat tekshirilgan holatlarni qamraydi, 100% kafolat bermaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Unit va integration", "title_ru": "Unit и integration",
            "description": "Unit va integration testlarning farqini o'z so'zingiz bilan yozing.",
            "description_ru": "Объясните своими словами разницу между unit- и integration-тестами.",
            "exercise_type": "text_input",
            "expected_answer": "Unit test bitta funksiyani alohida tekshiradi (tez, aniq). Integration test bir nechta qismni birga tekshiradi, masalan so'rovning route, middleware va ma'lumotlar qatlami orqali o'tishini.",
            "hint": "Bitta qism yoki bir nechta qism birgalikda?",
            "hint_ru": "Одна часть или несколько частей вместе?",
            "explanation": "Unit — alohida funksiya, integration — qismlarning birgalikdagi ishi. Ikkalasi kerak: unit tez xatoni topadi, integration qismlar o'zaro to'g'ri ulanganini ko'rsatadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 2-dars: supertest ────────────────────────────────────────────────────────

_L2_TEXT_UZ = """<h3>Route'ni qanday test qilamiz</h3>
<p>Route'ni tekshirish uchun serverni ishga tushirib, Postman bilan so'rov yuborish shart emas. <strong>supertest</strong> Express ilovasini o'zi vaqtinchalik portda ishga tushiradi, so'rov yuboradi va javobni qaytaradi. Faqat bitta shart: ilova va serverni ajratish.</p>
<pre class="mermaid">
flowchart LR
  T["test: request(app).post(...)"] --> S["supertest: vaqtinchalik server"]
  S --> A["app.js: route va middleware"]
  A --> R["javob: status, headers, body"]
  R --> T
</pre>
<ul>
  <li><code>app.js</code> ilovani yaratadi va <code>module.exports = app</code> qiladi, lekin <code>listen</code> chaqirmaydi.</li>
  <li><code>server.js</code> faqat <code>app.listen</code> ni chaqiradi. Ishga tushirish: <code>npm start</code>.</li>
</ul>
<p>Shunda testlar portni band qilmaydi va bir vaqtda parallel ishlay oladi. Quyida test qilinadigan Notes API (ma'lumotlar <code>repo.js</code> da, bu 4-darsda mock qilinadigan qatlam):</p>
<pre><code>__REPO__</code></pre>
<pre><code>__APP__</code></pre>
<pre><code>__SERVER__</code></pre>
<p>E'tibor bering: <code>BCRYPT_ROUNDS</code> test rejimida kichik. Jest <code>NODE_ENV</code> ni o'zi <code>test</code> qiladi, shuning uchun parol xeshlash testlarda tez ishlaydi.</p>

<h3>register va login testlari</h3>
<pre><code>__TEST__</code></pre>
<ul>
  <li><code>request(app).post(url).send(obyekt)</code> JSON yuboradi va <code>await</code> bilan javobni kutadi.</li>
  <li><code>res.status</code>, <code>res.body</code> (tayyor JS obyekti) va <code>res.headers</code> tekshiriladi.</li>
  <li><code>beforeEach(() =&gt; repo.reset())</code> har testdan oldin ma'lumotni tozalaydi: <strong>testlar bir-biriga bog'liq bo'lmasligi</strong> kerak, aks holda ularning tartibi natijaga ta'sir qiladi.</li>
  <li>Ichki <code>describe</code> dagi <code>beforeEach</code> tashqaridagidan keyin ishlaydi: shuning uchun login testlarida foydalanuvchi allaqachon ro'yxatdan o'tgan.</li>
</ul>

<h3>Nimani test qilish kerak</h3>
<p>Har bir route uchun kamida: muvaffaqiyatli holat (happy path), noto'g'ri kirish (400), mavjud emas (404) va ruxsat (401, 403) holatlari. Xatoni tekshiruvchi test ko'pincha muvaffaqiyatni tekshiruvchidan foydaliroq: aynan shu yerda xatolar yashirinadi.</p>"""

_L2_TEXT_RU = """<h3>Как тестировать маршрут</h3>
<p>Чтобы проверить маршрут, не нужно запускать сервер и слать запрос через Postman. <strong>supertest</strong> сам запускает приложение Express на временном порту, отправляет запрос и возвращает ответ. Есть одно условие: приложение и сервер должны быть разделены.</p>
<pre class="mermaid">
flowchart LR
  T["тест: request(app).post(...)"] --> S["supertest: временный сервер"]
  S --> A["app.js: маршруты и middleware"]
  A --> R["ответ: status, headers, body"]
  R --> T
</pre>
<ul>
  <li><code>app.js</code> создаёт приложение и делает <code>module.exports = app</code>, но не вызывает <code>listen</code>.</li>
  <li><code>server.js</code> только вызывает <code>app.listen</code>. Запуск: <code>npm start</code>.</li>
</ul>
<p>Так тесты не занимают порт и могут работать параллельно. Ниже тестируемое Notes API (данные хранятся в <code>repo.js</code> — этот слой мы заменим моком в уроке 4):</p>
<pre><code>__REPO__</code></pre>
<pre><code>__APP__</code></pre>
<pre><code>__SERVER__</code></pre>
<p>Обратите внимание: <code>BCRYPT_ROUNDS</code> в тестовом режиме маленький. Jest сам задаёт <code>NODE_ENV</code> равным <code>test</code>, поэтому хеширование пароля в тестах работает быстро.</p>

<h3>Тесты регистрации и входа</h3>
<pre><code>__TEST__</code></pre>
<ul>
  <li><code>request(app).post(url).send(объект)</code> отправляет JSON, а <code>await</code> ждёт ответ.</li>
  <li>Проверяются <code>res.status</code>, <code>res.body</code> (готовый JS-объект) и <code>res.headers</code>.</li>
  <li><code>beforeEach(() =&gt; repo.reset())</code> очищает данные перед каждым тестом: <strong>тесты не должны зависеть друг от друга</strong>, иначе их порядок влияет на результат.</li>
  <li><code>beforeEach</code> во вложенном <code>describe</code> срабатывает после внешнего: поэтому в тестах входа пользователь уже зарегистрирован.</li>
</ul>

<h3>Что нужно тестировать</h3>
<p>Для каждого маршрута как минимум: успешный случай (happy path), неверный ввод (400), отсутствие ресурса (404) и права доступа (401, 403). Тест на ошибку часто полезнее теста на успех: именно там прячутся баги.</p>"""

_L2_BLOCKS = dict(REPO=CODE_REPO, APP=CODE_APP, SERVER=CODE_SERVER, TEST=TEST_AUTH)

LESSON_2 = {
    "order": 1,
    "title": "2-supertest bilan route'larni testlash",
    "title_ru": "2-Тестирование маршрутов через supertest",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": TEST_AUTH,
    "code_content_ru": TEST_AUTH,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: supertest bilan register/login testlari",
        "title_ru": "Пример: тесты регистрации и входа на supertest",
        "description": "app.js va server.js ajratilgan Notes API hamda uning supertest testlari.",
        "description_ru": "Notes API с разделёнными app.js и server.js и его тесты на supertest.",
        "sample_type": "code",
        "code_files": [
            {"filename": "src/repo.js", "language": "javascript", "code": CODE_REPO},
            {"filename": "src/app.js", "language": "javascript", "code": CODE_APP},
            {"filename": "src/server.js", "language": "javascript", "code": CODE_SERVER},
            {"filename": "tests/auth.test.js", "language": "javascript", "code": TEST_AUTH},
        ],
    },
    "exercises": [
        {
            "title": "App va server", "title_ru": "App и server",
            "description": "Nega app.js da app.listen chaqirilmaydi va app eksport qilinadi?",
            "description_ru": "Почему в app.js не вызывают app.listen, а экспортируют app?",
            "exercise_type": "multiple_choice",
            "options": [
                "Chunki supertest ilovani o'zi vaqtinchalik portda ishga tushiradi, testlar portni band qilmaydi",
                "Chunki Express listen'ni qo'llab-quvvatlamaydi",
                "Chunki Jest listen'ni taqiqlaydi",
                "Hech qanday sababi yo'q",
            ],
            "options_ru": [
                "Потому что supertest сам запускает приложение на временном порту, и тесты не занимают порт",
                "Потому что Express не поддерживает listen",
                "Потому что Jest запрещает listen",
                "Никакой причины нет",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Ikkita test bir xil portni olishga urinsa nima bo'ladi?",
            "hint_ru": "Что будет, если два теста попытаются занять один порт?",
            "explanation": "Ilovani serverdan ajratish testlarda port bandligi xatosini yo'qotadi va supertest har so'rov uchun o'zi server ochishga imkon beradi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "supertest chaqiruvi", "title_ru": "Вызов supertest",
            "description": "supertest bilan ilovaga so'rov yuborishni boshlaydigan funksiya: ___(app).get(\"/api/notes\")",
            "description_ru": "Функция, с которой начинается запрос к приложению через supertest: ___(app).get(\"/api/notes\")",
            "exercise_type": "fill_in_blank",
            "correct_answers": "request",
            "hint": "require(\"supertest\") odatda shu nom bilan olinadi.",
            "hint_ru": "require(\"supertest\") обычно присваивают этому имени.",
            "explanation": "const request = require(\"supertest\"); keyin request(app).get(url) so'rovni yuboradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Login testi tartibi", "title_ru": "Порядок теста входа",
            "description": "Muvaffaqiyatli login testining qadamlarini joylashtiring.",
            "description_ru": "Расположите шаги теста успешного входа.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["repo.reset() bilan ma'lumotni tozalash", "Foydalanuvchini ro'yxatdan o'tkazish", "POST /api/login yuborish", "Status 200 va token borligini tekshirish"],
            "drag_items_ru": ["Очистить данные через repo.reset()", "Зарегистрировать пользователя", "Отправить POST /api/login", "Проверить статус 200 и наличие токена"],
            "correct_order": ["repo.reset() bilan ma'lumotni tozalash", "Foydalanuvchini ro'yxatdan o'tkazish", "POST /api/login yuborish", "Status 200 va token borligini tekshirish"],
            "hint": "Login qilishdan oldin foydalanuvchi mavjud bo'lishi kerak.",
            "hint_ru": "Перед входом пользователь должен существовать.",
            "explanation": "Avval holat tozalanadi, keyin foydalanuvchi yaratiladi, so'ng login so'rovi yuboriladi va natija tekshiriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi holatlar kerak", "title_ru": "Какие случаи нужны",
            "description": "POST /api/register uchun qaysi testlar foydali? (Bir nechta javob)",
            "description_ru": "Какие тесты полезны для POST /api/register? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "To'g'ri ma'lumot bilan 201",
                "Qisqa parol bilan 400",
                "Takroriy username bilan 409",
                "Faqat to'g'ri ma'lumot testi yetarli",
            ],
            "options_ru": [
                "201 при корректных данных",
                "400 при коротком пароле",
                "409 при повторяющемся username",
                "Достаточно только теста с корректными данными",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Faqat muvaffaqiyatli holatni tekshirish yetarli emas.",
            "hint_ru": "Проверки только успешного случая недостаточно.",
            "explanation": "Yaxshi to'plam muvaffaqiyat va xato holatlarini ham qamraydi: 201, 400 va 409.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Testlar bog'liqmasligi", "title_ru": "Независимость тестов",
            "description": "Nega har testdan oldin ma'lumotlar tozalanadi (beforeEach)? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем перед каждым тестом очищают данные (beforeEach)? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Testlar bir-biriga bog'liq bo'lmasligi kerak: oldingi test qoldirgan ma'lumot keyingisining natijasiga ta'sir qilmasin va test tartibi o'zgarsa ham natija bir xil bo'lsin.",
            "hint": "Birinchi test yaratgan foydalanuvchi ikkinchisiga xalaqit bersa nima bo'ladi?",
            "hint_ru": "Что будет, если пользователь из первого теста помешает второму?",
            "explanation": "Izolyatsiya testni ishonchli qiladi: har test bir xil boshlang'ich holatdan boshlanadi, shuning uchun natija tartibga bog'liq emas.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: himoyalangan route'larni testlash ────────────────────────────────

_L3_TEXT_UZ = """<h3>Tokenli route'ni qanday test qilamiz</h3>
<p>Himoyalangan route'ga so'rov yuborish uchun test avval haqiqiy tokenni olishi kerak. Yo'li oddiy: testning o'zida ro'yxatdan o'tamiz, login qilamiz va tokenni <code>Authorization</code> sarlavhasiga qo'yamiz. Shuni yordamchi funksiyaga chiqaramiz va har testda qayta ishlatamiz. Sarlavhani <code>.set({...})</code> bilan beramiz.</p>
<pre class="mermaid">
flowchart TD
  A["GET /api/notes"] --> B{"Token bormi?"}
  B -- "yo'q" --> C["401: token is required"]
  B -- "buzilgan" --> D["401: token is invalid"]
  B -- "muddati o'tgan" --> E["401: token has expired"]
  B -- "to'g'ri" --> F["200: faqat o'z yozuvlari"]
</pre>
<pre><code>__TEST__</code></pre>

<h3>Nimalarga e'tibor berish kerak</h3>
<ul>
  <li><strong>Yordamchi funksiya</strong> <code>loginAs(username)</code> takrorni yo'qotadi va testni qisqa, o'qilishi oson qiladi.</li>
  <li><strong>Muddati o'tgan token</strong>ni <code>jwt.sign(..., { expiresIn: -1 })</code> bilan to'g'ridan-to'g'ri yasaymiz: 30 daqiqa kutish shart emas. Buning uchun test ham ilova ishlatgan maxfiy kalitni bilishi kerak.</li>
  <li><strong>401 va 403</strong>: 401 — token yo'q yoki yaroqsiz, 403 — token to'g'ri, lekin ruxsat yo'q. Ikkalasini alohida testlang.</li>
  <li><strong>Egalik tekshiruvi</strong>: bir foydalanuvchi boshqasining yozuvini ko'rmasligi va o'chira olmasligini isbotlang. Bu eng muhim xavfsizlik testlaridan biri.</li>
  <li><strong>Muhit o'zgaruvchisi</strong> (<code>ADMIN_USERNAME</code>) testda qo'yiladi va <code>afterEach</code> bilan olib tashlanadi, aks holda u boshqa testlarga ta'sir qiladi.</li>
  <li><code>toMatchObject</code> obyektning faqat kerakli maydonlarini tekshiradi: yangi maydon qo'shilsa test sinmaydi.</li>
</ul>

<h3>Test nomlari</h3>
<p>Test nomi muvaffaqiyatsiz bo'lganda o'qiladigan birinchi narsa. «test1» emas, nima kutilishini yozing: <code>"an expired token gets its own message"</code>. Nomga qarab xato qayerda ekanini tushunish kerak.</p>"""

_L3_TEXT_RU = """<h3>Как тестировать маршрут с токеном</h3>
<p>Чтобы отправить запрос к защищённому маршруту, тест сначала должен получить настоящий токен. Способ простой: прямо в тесте регистрируемся, входим и кладём токен в заголовок <code>Authorization</code>. Выносим это во вспомогательную функцию и используем в каждом тесте. Заголовок передаётся через <code>.set({...})</code>.</p>
<pre class="mermaid">
flowchart TD
  A["GET /api/notes"] --> B{"Токен есть?"}
  B -- "нет" --> C["401: token is required"]
  B -- "испорчен" --> D["401: token is invalid"]
  B -- "срок истёк" --> E["401: token has expired"]
  B -- "верный" --> F["200: только свои записи"]
</pre>
<pre><code>__TEST__</code></pre>

<h3>На что обратить внимание</h3>
<ul>
  <li><strong>Вспомогательная функция</strong> <code>loginAs(username)</code> убирает повторение и делает тест короче и понятнее.</li>
  <li><strong>Просроченный токен</strong> мы создаём напрямую через <code>jwt.sign(..., { expiresIn: -1 })</code>: ждать 30 минут не нужно. Для этого тест должен знать тот же секретный ключ, что и приложение.</li>
  <li><strong>401 и 403</strong>: 401 — токена нет или он недействителен, 403 — токен верный, но прав нет. Тестируйте оба случая отдельно.</li>
  <li><strong>Проверка владельца</strong>: докажите, что один пользователь не видит и не удаляет чужие записи. Это один из самых важных тестов безопасности.</li>
  <li><strong>Переменная окружения</strong> (<code>ADMIN_USERNAME</code>) задаётся в тесте и убирается в <code>afterEach</code>, иначе она повлияет на другие тесты.</li>
  <li><code>toMatchObject</code> проверяет только нужные поля объекта: если добавится новое поле, тест не сломается.</li>
</ul>

<h3>Названия тестов</h3>
<p>Название теста — первое, что вы прочитаете при падении. Пишите не «test1», а что ожидается: <code>"an expired token gets its own message"</code>. По названию должно быть понятно, где ошибка.</p>"""

_L3_BLOCKS = dict(TEST=TEST_NOTES)

LESSON_3 = {
    "order": 2,
    "title": "3-Himoyalangan route'larni testlash",
    "title_ru": "3-Тестирование защищённых маршрутов",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": TEST_NOTES,
    "code_content_ru": TEST_NOTES,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: token, egalik va admin testlari",
        "title_ru": "Пример: тесты токена, владельца и админа",
        "description": "loginAs yordamchisi, 401/403/404 holatlari, muddati o'tgan token va admin testlari.",
        "description_ru": "Помощник loginAs, случаи 401/403/404, просроченный токен и тесты админа.",
        "sample_type": "code",
        "code_files": [
            {"filename": "tests/notes.test.js", "language": "javascript", "code": TEST_NOTES},
        ],
    },
    "exercises": [
        {
            "title": "Tokensiz so'rov testi", "title_ru": "Тест запроса без токена",
            "description": "Tokensiz GET /api/notes testida qaysi status kutiladi?",
            "description_ru": "Какой статус ожидается в тесте GET /api/notes без токена?",
            "exercise_type": "multiple_choice",
            "options": ["200", "401", "403", "500"],
            "options_ru": ["200", "401", "403", "500"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Foydalanuvchi kimligi noma'lum.",
            "hint_ru": "Личность пользователя неизвестна.",
            "explanation": "Token yo'q bo'lsa auth middleware 401 qaytaradi. 403 — kim ekani ma'lum, lekin ruxsat yo'q holat uchun.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Sarlavha o'rnatish", "title_ru": "Установка заголовка",
            "description": "supertest'da so'rovga sarlavha qo'shadigan metod: request(app).get(url).___({ Authorization: token })",
            "description_ru": "Метод supertest, добавляющий заголовок к запросу: request(app).get(url).___({ Authorization: token })",
            "exercise_type": "fill_in_blank",
            "correct_answers": "set",
            "hint": "Qisqa, uch harfli metod nomi.",
            "hint_ru": "Короткое название метода из трёх букв.",
            "explanation": ".set(nom, qiymat) yoki .set({ ...sarlavhalar }) so'rovga HTTP sarlavhalarini qo'shadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Eskirgan token testi", "title_ru": "Тест просроченного токена",
            "description": "Muddati o'tgan tokenni testda qanday olish to'g'ri?",
            "description_ru": "Как правильно получить просроченный токен в тесте?",
            "exercise_type": "multiple_choice",
            "options": [
                "30 daqiqa kutib turish",
                "jwt.sign ga manfiy expiresIn berish",
                "Tokenning oxirgi belgisini o'chirish",
                "Serverni qayta ishga tushirish",
            ],
            "options_ru": [
                "Ждать 30 минут",
                "Передать в jwt.sign отрицательный expiresIn",
                "Удалить последний символ токена",
                "Перезапустить сервер",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Test tez ishlashi kerak.",
            "hint_ru": "Тест должен быть быстрым.",
            "explanation": "Manfiy expiresIn token yaratilishi bilan eskirgan bo'lishini ta'minlaydi. Belgini o'chirsangiz, «invalid» holati chiqadi, «expired» emas.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Egalik testlari", "title_ru": "Тесты владельца",
            "description": "Ali va Vali foydalanuvchilari uchun qaysi tekshiruvlar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие проверки верны для пользователей Али и Вали? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Vali Ali'ning yozuvini ro'yxatda ko'rmaydi",
                "Vali Ali'ning yozuvini o'chirsa 403 oladi",
                "Ali o'z yozuvini o'chirsa 200 oladi",
                "Vali Ali'ning yozuvini o'chira oladi",
            ],
            "options_ru": [
                "Вали не видит запись Али в списке",
                "Если Вали удаляет запись Али, он получает 403",
                "Если Али удаляет свою запись, он получает 200",
                "Вали может удалить запись Али",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Faqat bitta variant noto'g'ri.",
            "hint_ru": "Неверен только один вариант.",
            "explanation": "Egalik qoidasi: foydalanuvchi faqat o'z yozuvini ko'radi va o'chiradi. Boshqasiniki uchun 403 qaytadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega yordamchi funksiya", "title_ru": "Зачем вспомогательная функция",
            "description": "Nega testlarda loginAs kabi yordamchi funksiya yoziladi? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем в тестах пишут вспомогательную функцию вроде loginAs? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Ro'yxatdan o'tish va login har himoyalangan testda kerak bo'ladi. Yordamchi funksiya takrorlashni yo'qotadi, testni qisqa va o'qilishi oson qiladi, login qoidasi o'zgarsa bitta joyda tuzatiladi.",
            "hint": "Bir xil qadamlar nechta testda takrorlanadi?",
            "hint_ru": "В скольких тестах повторяются одни и те же шаги?",
            "explanation": "Takrorlanuvchi tayyorgarlikni bitta funksiyaga chiqarish testni qisqartiradi va o'zgarish bitta joyda qilinadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: bazani mock qilish ───────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>Mock nima va nega kerak</h3>
<p>Hozircha testlar haqiqiy <code>repo.js</code> bilan ishlaydi. Haqiqiy loyihada bu qatlam PostgreSQL bilan gaplashadi va test uchun bazani ishga tushirish sekin va murakkab. Ba'zi holatlarni (masalan, «baza ishlamayapti») haqiqiy bazada umuman yaratib bo'lmaydi. <strong>Mock</strong> — haqiqiy qismning o'rniga qo'yiladigan soxta nusxa: siz uning nima qaytarishini belgilaysiz va qanday chaqirilganini tekshirasiz.</p>
<pre class="mermaid">
flowchart LR
  A["route"] --> B{"Qaysi repo?"}
  B -- "oddiy test" --> C["haqiqiy repo (xotirada)"]
  B -- "jest.mock" --> D["soxta repo: javobni siz belgilaysiz"]
  D --> E["chaqiruv argumentlarini tekshirish"]
</pre>
<p>Shuning uchun biz ma'lumotlar bilan ishlashni alohida <code>repo.js</code> qatlamiga ajratgandik: route'lar bazani to'g'ridan-to'g'ri emas, shu qatlam orqali chaqiradi va uni almashtirish oson.</p>

<h3>jest.mock va mock funksiyalar</h3>
<ul>
  <li><code>jest.mock("../src/repo")</code> modulning barcha funksiyalarini avtomatik <em>mock funksiyaga</em> aylantiradi. Bu fayl boshida, <code>require</code> dan oldin yoziladi (Jest uni o'zi yuqoriga ko'taradi).</li>
  <li><code>mockResolvedValue(x)</code> — mock async funksiya <code>x</code> bilan bajariladi, <code>mockRejectedValue(err)</code> — xato bilan rad etiladi.</li>
  <li><code>toHaveBeenCalledWith(...)</code> — funksiya aynan shu argumentlar bilan chaqirilganini, <code>toHaveBeenCalledTimes(n)</code> — necha marta chaqirilganini, <code>not.toHaveBeenCalled()</code> — umuman chaqirilmaganini tekshiradi.</li>
  <li><code>jest.resetAllMocks()</code> har testdan oldin mocklarni boshlang'ich holatga qaytaradi: oldingi test sozlagan qiymatlar keyingisiga o'tmaydi.</li>
</ul>
<pre><code>__TEST__</code></pre>

<h3>Bu testlar nimani isbotlaydi</h3>
<ul>
  <li><strong>Argumentlar:</strong> route yozuv matnini tozalab (<code>trim</code>) va egasini tokendan olib (<code>ownerId: 7</code>) ma'lumotlar qatlamiga uzatadi.</li>
  <li><strong>Xatoni simulyatsiya:</strong> baza ishlamasa, foydalanuvchi serverning ichki xabarini emas, toza <code>500</code> JSON javobini oladi.</li>
  <li><strong>Chaqirilmaslik:</strong> noto'g'ri ma'lumot bazaga umuman yetib bormaydi.</li>
</ul>

<h3>Mockni haddan oshirmang</h3>
<p>Har narsani mock qilsangiz, test faqat o'z mocklarini tekshirib qoladi va haqiqiy xatoni topmaydi. Qoida: <strong>o'zingizning kodingizni</strong> emas, <strong>tashqi qaramliklarni</strong> (baza, tarmoq, pochta) mock qiling. Muhim oqimlar uchun (2–3-darslardagidek) mocksiz testlar ham qolsin.</p>"""

_L4_TEXT_RU = """<h3>Что такое мок и зачем он нужен</h3>
<p>Пока наши тесты работают с настоящим <code>repo.js</code>. В реальном проекте этот слой общается с PostgreSQL, а поднимать базу для тестов медленно и сложно. Некоторые ситуации (например, «база не работает») на настоящей базе вообще не создать. <strong>Мок</strong> — это подставная копия вместо настоящей части: вы сами задаёте, что она вернёт, и проверяете, как её вызвали.</p>
<pre class="mermaid">
flowchart LR
  A["маршрут"] --> B{"Какой repo?"}
  B -- "обычный тест" --> C["настоящий repo (в памяти)"]
  B -- "jest.mock" --> D["подставной repo: ответ задаёте вы"]
  D --> E["проверка аргументов вызова"]
</pre>
<p>Поэтому мы вынесли работу с данными в отдельный слой <code>repo.js</code>: маршруты обращаются к базе не напрямую, а через этот слой, и его легко заменить.</p>

<h3>jest.mock и мок-функции</h3>
<ul>
  <li><code>jest.mock("../src/repo")</code> автоматически превращает все функции модуля в <em>мок-функции</em>. Пишется в начале файла, до <code>require</code> (Jest сам поднимает эту строку наверх).</li>
  <li><code>mockResolvedValue(x)</code> — мок асинхронной функции завершается значением <code>x</code>, <code>mockRejectedValue(err)</code> — завершается ошибкой.</li>
  <li><code>toHaveBeenCalledWith(...)</code> проверяет, что функцию вызвали именно с этими аргументами, <code>toHaveBeenCalledTimes(n)</code> — сколько раз вызвали, <code>not.toHaveBeenCalled()</code> — что не вызывали вообще.</li>
  <li><code>jest.resetAllMocks()</code> перед каждым тестом возвращает моки в исходное состояние: значения из предыдущего теста не переходят в следующий.</li>
</ul>
<pre><code>__TEST__</code></pre>

<h3>Что доказывают эти тесты</h3>
<ul>
  <li><strong>Аргументы:</strong> маршрут очищает текст записи (<code>trim</code>) и берёт владельца из токена (<code>ownerId: 7</code>), передавая их в слой данных.</li>
  <li><strong>Имитация ошибки:</strong> если база не работает, пользователь получает аккуратный JSON с кодом <code>500</code>, а не внутреннее сообщение сервера.</li>
  <li><strong>Отсутствие вызова:</strong> неверные данные вообще не доходят до базы.</li>
</ul>

<h3>Не злоупотребляйте моками</h3>
<p>Если замокать всё, тест начнёт проверять только собственные моки и не найдёт настоящую ошибку. Правило: мокайте <strong>внешние зависимости</strong> (база, сеть, почта), а не <strong>собственный код</strong>. Для важных сценариев (как в уроках 2–3) оставляйте и тесты без моков.</p>"""

_L4_BLOCKS = dict(TEST=TEST_ERRORS)

LESSON_4 = {
    "order": 3,
    "title": "4-Bazani mock qilish (jest.mock)",
    "title_ru": "4-Мок базы данных (jest.mock)",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": TEST_ERRORS,
    "code_content_ru": TEST_ERRORS,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: jest.mock bilan ma'lumotlar qatlamini almashtirish",
        "title_ru": "Пример: подмена слоя данных через jest.mock",
        "description": "mockResolvedValue, mockRejectedValue, toHaveBeenCalledWith va 500 xatoni sinash.",
        "description_ru": "mockResolvedValue, mockRejectedValue, toHaveBeenCalledWith и проверка ошибки 500.",
        "sample_type": "code",
        "code_files": [
            {"filename": "tests/errors.test.js", "language": "javascript", "code": TEST_ERRORS},
        ],
    },
    "exercises": [
        {
            "title": "Mock nima", "title_ru": "Что такое мок",
            "description": "Mock nima?",
            "description_ru": "Что такое мок?",
            "exercise_type": "multiple_choice",
            "options": [
                "Haqiqiy qismning o'rniga qo'yiladigan soxta nusxa, uning javobini siz belgilaysiz",
                "Testlarni tezlashtiradigan Jest plagini",
                "Bazani tozalaydigan buyruq",
                "HTTP sarlavhasi",
            ],
            "options_ru": [
                "Подставная копия вместо настоящей части, ответ которой задаёте вы",
                "Плагин Jest, ускоряющий тесты",
                "Команда очистки базы",
                "HTTP-заголовок",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "«Mock» inglizcha «taqlid» degani.",
            "hint_ru": "«Mock» по-английски означает «имитация».",
            "explanation": "Mock tashqi qaramlikni soxta nusxa bilan almashtiradi, shunda test tez, aniq va xatolarni ham simulyatsiya qila oladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Mock'ni o'rnatish", "title_ru": "Установка мока",
            "description": "Modulni mock qiladigan chaqiruv: jest.___(\"../src/repo\")",
            "description_ru": "Вызов, подменяющий модуль моком: jest.___(\"../src/repo\")",
            "exercise_type": "fill_in_blank",
            "correct_answers": "mock",
            "hint": "Metod nomi mavzu nomi bilan bir xil.",
            "hint_ru": "Название метода совпадает с названием темы.",
            "explanation": "jest.mock(yo'l) modulning funksiyalarini mock funksiyalarga aylantiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Xato testi tartibi", "title_ru": "Порядок теста ошибки",
            "description": "«Baza ishlamaydi» testining qadamlarini joylashtiring.",
            "description_ru": "Расположите шаги теста «база не работает».",
            "exercise_type": "drag_and_drop",
            "drag_items": ["repo.listNotes.mockRejectedValue(new Error(...))", "GET /api/notes so'rovini yuborish", "Status 500 ni tekshirish", "Javob tanasi {error: \"internal server error\"} ekanini tekshirish"],
            "drag_items_ru": ["repo.listNotes.mockRejectedValue(new Error(...))", "Отправить запрос GET /api/notes", "Проверить статус 500", "Проверить, что тело ответа {error: \"internal server error\"}"],
            "correct_order": ["repo.listNotes.mockRejectedValue(new Error(...))", "GET /api/notes so'rovini yuborish", "Status 500 ni tekshirish", "Javob tanasi {error: \"internal server error\"} ekanini tekshirish"],
            "hint": "Avval mockni sozlang, keyin so'rov yuboring.",
            "hint_ru": "Сначала настройте мок, потом отправьте запрос.",
            "explanation": "Mock avval xato qaytaradigan qilib sozlanadi, so'ng so'rov yuboriladi va status bilan javob tanasi tekshiriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi gaplar to'g'ri", "title_ru": "Какие утверждения верны",
            "description": "Mock bilan nimalarni tekshirish mumkin? (Bir nechta javob)",
            "description_ru": "Что можно проверить с помощью мока? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Funksiya qanday argumentlar bilan chaqirilganini",
                "Baza ishlamagan holatdagi javobni",
                "Funksiya umuman chaqirilmaganini",
                "Haqiqiy PostgreSQL so'rovi to'g'ri ishlashini",
            ],
            "options_ru": [
                "С какими аргументами вызвали функцию",
                "Ответ в ситуации, когда база не работает",
                "Что функцию вообще не вызывали",
                "Что настоящий запрос к PostgreSQL работает верно",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Mock haqiqiy bazani almashtiradi, shuning uchun uning ishlashini isbotlay olmaydi.",
            "hint_ru": "Мок заменяет настоящую базу, поэтому не может доказать её работу.",
            "explanation": "Mock chaqiruvlarni va xatolarni tekshirishga yaraydi, lekin haqiqiy bazaning to'g'riligini isbotlamaydi: buning uchun alohida integratsion test kerak.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Mockni haddan oshirish", "title_ru": "Избыточные моки",
            "description": "Nima uchun hamma narsani mock qilish yomon? Nimani mock qilish kerak, nimani yo'q? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему плохо мокать всё подряд? Что нужно мокать, а что нет? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Hamma narsa mock qilinsa, test faqat o'z mocklarini tekshiradi va haqiqiy xatoni topmaydi. Tashqi qaramliklarni (baza, tarmoq, pochta) mock qilish kerak, o'zingizning kodingizni emas.",
            "hint": "Test nimani tekshirib qoladi, agar hamma narsa soxta bo'lsa?",
            "hint_ru": "Что будет проверять тест, если всё в нём подставное?",
            "explanation": "Mock tashqi, sekin yoki nazorat qilib bo'lmaydigan qismlar uchun. O'z kodingizni mock qilsangiz, test hech narsani isbotlamaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: coverage va CI ───────────────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Coverage: kodning qancha qismi tekshirilgan</h3>
<p><strong>Coverage</strong> (qamrov) testlar ishlaganda kodingizning qancha qismi bajarilganini ko'rsatadi. Buyruq: <code>npm run test:coverage</code> (ya'ni <code>jest --coverage</code>). Hisobotda to'rt ustun bor: <code>Stmts</code> (operatorlar), <code>Branch</code> (<code>if</code> va boshqa tarmoqlar), <code>Funcs</code> (funksiyalar) va <code>Lines</code> (qatorlar). Oxirgi ustunda bajarilmagan qator raqamlari ko'rsatiladi: aynan shu yerda test yetishmaydi.</p>
<p>Muhim ogohlantirish: coverage faqat <em>kod bajarilganini</em> ko'rsatadi, <em>to'g'ri tekshirilganini</em> emas. <code>expect</code> siz test ham qatorni «qamrab oladi». 100% maqsad emas; xatar bor joylarni (xatolar, ruxsatlar, tarmoqlar) tekshirilgan deb bilish muhim.</p>

<h3>Chegara (threshold) qo'yish</h3>
<p>Coverage kamayib ketmasligi uchun <code>package.json</code> ga chegara qo'yamiz. Chegaradan past bo'lsa, Jest nolga teng bo'lmagan kod bilan tugaydi va CI qizil bo'ladi:</p>
<pre><code>__PACKAGE__</code></pre>
<ul>
  <li><code>collectCoverageFrom</code> — qaysi fayllar hisobga olinadi. <code>server.js</code> ni chiqarib tashlaymiz: u faqat <code>listen</code> ni chaqiradi.</li>
  <li><code>coverageThreshold</code> — minimal foiz. Haqiqatga yaqin, lekin erishsa bo'ladigan raqamni tanlang (bizda 90% qator va 80% tarmoq).</li>
  <li>Bitta fayl testlarini ishga tushirsangiz, umumiy coverage tushib ketadi va chegara ogohlantiradi: bu normal, chegara butun to'plam uchun.</li>
</ul>

<h3>CI: har push'da testlar o'zi ishlaydi</h3>
<p><strong>CI</strong> (Continuous Integration) — kodni GitHub'ga yuborganingizda testlarni avtomatik, toza muhitda ishga tushirish. Shunda «menda ishlayapti» muammosi yo'qoladi va buzilgan kod asosiy tarmoqqa tushmaydi. GitHub Actions uchun loyihada <code>.github/workflows/test.yml</code> fayli yaratiladi:</p>
<pre class="mermaid">
flowchart LR
  A["git push / pull request"] --> B["GitHub: toza server"]
  B --> C["checkout: kodni olish"]
  C --> D["npm ci: paketlarni o'rnatish"]
  D --> E["npm run test:coverage"]
  E --> F{"Hammasi o'tdimi?"}
  F -- "ha" --> G["yashil belgi"]
  F -- "yo'q" --> H["qizil belgi: birlashtirib bo'lmaydi"]
</pre>
<pre><code>__WORKFLOW__</code></pre>
<ul>
  <li><code>on</code> — qachon ishga tushadi: asosiy tarmoqqa push va har pull request'da.</li>
  <li><code>actions/checkout</code> kodni oladi, <code>actions/setup-node</code> Node versiyasini o'rnatadi va <code>npm</code> keshini yoqadi.</li>
  <li><code>npm ci</code> <code>package-lock.json</code> bo'yicha aniq shu versiyalarni o'rnatadi: <code>npm install</code> dan tezroq va takrorlanuvchi. Shuning uchun <code>package-lock.json</code> repozitoriyga qo'shilgan bo'lishi kerak.</li>
  <li>Oxirgi qadam testlarni coverage bilan yurgizadi: chegaradan past bo'lsa, qadam muvaffaqiyatsiz tugaydi.</li>
</ul>
<p>Push qilgach, GitHub'da repozitoriyning <em>Actions</em> yorlig'ida natijani ko'rasiz. Pull request'da yashil belgi testlar o'tganini bildiradi.</p>"""

_L5_TEXT_RU = """<h3>Coverage: какая часть кода проверена</h3>
<p><strong>Coverage</strong> (покрытие) показывает, какая часть вашего кода выполнялась во время тестов. Команда: <code>npm run test:coverage</code> (то есть <code>jest --coverage</code>). В отчёте четыре столбца: <code>Stmts</code> (операторы), <code>Branch</code> (ветки <code>if</code> и другие), <code>Funcs</code> (функции) и <code>Lines</code> (строки). В последнем столбце указаны номера невыполненных строк: именно там не хватает тестов.</p>
<p>Важное предупреждение: coverage показывает лишь то, что код <em>выполнялся</em>, а не то, что он <em>проверен правильно</em>. Тест без <code>expect</code> тоже «покрывает» строку. 100% — не цель; важно, чтобы рискованные места (ошибки, права доступа, ветки) были проверены.</p>

<h3>Задаём порог (threshold)</h3>
<p>Чтобы покрытие не снижалось, добавим порог в <code>package.json</code>. Если покрытие ниже порога, Jest завершится с ненулевым кодом, а CI станет красным:</p>
<pre><code>__PACKAGE__</code></pre>
<ul>
  <li><code>collectCoverageFrom</code> — какие файлы учитываются. <code>server.js</code> исключаем: он только вызывает <code>listen</code>.</li>
  <li><code>coverageThreshold</code> — минимальный процент. Выбирайте реалистичное, но достижимое число (у нас 90% строк и 80% веток).</li>
  <li>Если запустить тесты одного файла, общее покрытие упадёт и порог выдаст предупреждение: это нормально, порог рассчитан на весь набор.</li>
</ul>

<h3>CI: тесты запускаются сами при каждом push</h3>
<p><strong>CI</strong> (Continuous Integration) — автоматический запуск тестов в чистой среде, когда вы отправляете код на GitHub. Так исчезает проблема «у меня работает», а сломанный код не попадает в основную ветку. Для GitHub Actions в проекте создаётся файл <code>.github/workflows/test.yml</code>:</p>
<pre class="mermaid">
flowchart LR
  A["git push / pull request"] --> B["GitHub: чистый сервер"]
  B --> C["checkout: получение кода"]
  C --> D["npm ci: установка пакетов"]
  D --> E["npm run test:coverage"]
  E --> F{"Всё прошло?"}
  F -- "да" --> G["зелёная отметка"]
  F -- "нет" --> H["красная отметка: слить нельзя"]
</pre>
<pre><code>__WORKFLOW__</code></pre>
<ul>
  <li><code>on</code> — когда запускается: при push в основную ветку и при каждом pull request.</li>
  <li><code>actions/checkout</code> получает код, <code>actions/setup-node</code> устанавливает версию Node и включает кеш <code>npm</code>.</li>
  <li><code>npm ci</code> устанавливает точные версии из <code>package-lock.json</code>: быстрее и воспроизводимее, чем <code>npm install</code>. Поэтому <code>package-lock.json</code> должен быть добавлен в репозиторий.</li>
  <li>Последний шаг запускает тесты с coverage: если покрытие ниже порога, шаг завершится ошибкой.</li>
</ul>
<p>После push результат виден на вкладке <em>Actions</em> репозитория на GitHub. В pull request зелёная отметка означает, что тесты прошли.</p>"""

_L5_BLOCKS = dict(PACKAGE=PACKAGE_L5, WORKFLOW=WORKFLOW_YML)

LESSON_5 = {
    "order": 4,
    "title": "5-Coverage va CI (GitHub Actions)",
    "title_ru": "5-Coverage и CI (GitHub Actions)",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": WORKFLOW_YML,
    "code_content_ru": WORKFLOW_YML,
    "code_language": "yaml",
    "sample": {
        "title": "Namuna: coverage chegarasi va GitHub Actions",
        "title_ru": "Пример: порог coverage и GitHub Actions",
        "description": "package.json dagi coverageThreshold va testlarni har push'da yurgizadigan workflow.",
        "description_ru": "coverageThreshold в package.json и workflow, запускающий тесты при каждом push.",
        "sample_type": "code",
        "code_files": [
            {"filename": "package.json", "language": "json", "code": PACKAGE_L5},
            {"filename": ".github/workflows/test.yml", "language": "yaml", "code": WORKFLOW_YML},
        ],
    },
    "exercises": [
        {
            "title": "Coverage buyrug'i", "title_ru": "Команда coverage",
            "description": "Jest'da coverage hisobotini beradigan flag: jest --___",
            "description_ru": "Флаг Jest, выдающий отчёт о покрытии: jest --___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "coverage",
            "hint": "Flag nomi mavzu nomi bilan bir xil.",
            "hint_ru": "Название флага совпадает с названием темы.",
            "explanation": "jest --coverage bajarilgan qatorlar, tarmoqlar va funksiyalar foizini ko'rsatadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Coverage nimani bildiradi", "title_ru": "Что означает coverage",
            "description": "90% coverage nimani bildiradi?",
            "description_ru": "Что означает покрытие 90%?",
            "exercise_type": "multiple_choice",
            "options": [
                "Kodning 90% i testlar paytida bajarilgan",
                "Dasturda 10% xato bor",
                "Kodning 90% i to'g'ri ekani isbotlangan",
                "Testlarning 90% i o'tgan",
            ],
            "options_ru": [
                "90% кода выполнялось во время тестов",
                "В программе 10% ошибок",
                "Доказано, что 90% кода верно",
                "90% тестов прошло",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Coverage bajarilishni o'lchaydi, to'g'rilikni emas.",
            "hint_ru": "Coverage измеряет выполнение, а не правильность.",
            "explanation": "Coverage faqat kod bajarilganini ko'rsatadi. expect siz test ham qatorni qamraydi, shuning uchun u sifatning kafolati emas.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "CI zanjiri", "title_ru": "Цепочка CI",
            "description": "GitHub Actions workflow'idagi qadamlar tartibini joylashtiring.",
            "description_ru": "Расположите шаги workflow GitHub Actions по порядку.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["actions/checkout bilan kodni olish", "actions/setup-node bilan Node o'rnatish", "npm ci bilan paketlarni o'rnatish", "npm run test:coverage bilan testlarni yurgizish"],
            "drag_items_ru": ["Получить код через actions/checkout", "Установить Node через actions/setup-node", "Установить пакеты через npm ci", "Запустить тесты через npm run test:coverage"],
            "correct_order": ["actions/checkout bilan kodni olish", "actions/setup-node bilan Node o'rnatish", "npm ci bilan paketlarni o'rnatish", "npm run test:coverage bilan testlarni yurgizish"],
            "hint": "Testdan oldin kod va paketlar kerak.",
            "hint_ru": "Перед тестами нужны код и пакеты.",
            "explanation": "Avval kod olinadi, Node o'rnatiladi, paketlar o'rnatiladi, so'ng testlar ishga tushadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "npm ci afzalligi", "title_ru": "Преимущества npm ci",
            "description": "CI'da npm install o'rniga npm ci ishlatishning qaysi sabablari to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие причины использовать в CI npm ci вместо npm install верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "package-lock.json dagi aniq versiyalarni o'rnatadi",
                "Odatda tezroq ishlaydi",
                "package-lock.json ni avtomatik o'zgartiradi",
                "Versiyalar har safar farq qilishi uchun",
            ],
            "options_ru": [
                "Устанавливает точные версии из package-lock.json",
                "Обычно работает быстрее",
                "Автоматически изменяет package-lock.json",
                "Чтобы версии каждый раз отличались",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "CI'da natija takrorlanuvchi bo'lishi kerak.",
            "hint_ru": "В CI результат должен быть воспроизводимым.",
            "explanation": "npm ci lock-fayl bo'yicha aniq versiyalarni o'rnatadi va tezroq: CI'da natija har safar bir xil bo'ladi. U lock-faylni o'zgartirmaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "CI nima beradi", "title_ru": "Что даёт CI",
            "description": "CI loyihaga qanday foyda keltiradi? O'z so'zingiz bilan yozing.",
            "description_ru": "Какую пользу CI приносит проекту? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Har push va pull request'da testlar toza muhitda avtomatik ishga tushadi. Shunda «menda ishlayapti» muammosi yo'qoladi, buzilgan kod asosiy tarmoqqa tushishidan oldin bilinadi.",
            "hint": "Testlarni kim va qachon ishga tushiradi?",
            "hint_ru": "Кто и когда запускает тесты?",
            "explanation": "CI testlarni inson xotirasiga bog'lamasdan, har o'zgarishda toza muhitda tekshiradi va buzilgan kodni oldindan to'xtatadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>Jest:</strong> <code>describe</code>, <code>test</code>, <code>expect</code>, <code>test.each</code>, unit test.</li>
  <li><strong>supertest:</strong> <code>app</code> va <code>server</code> ajratish, <code>request(app)</code> bilan route testlari.</li>
  <li><strong>Himoyalangan route'lar:</strong> token olish yordamchisi, 401 / 403 / 404, muddati o'tgan token, egalik testi.</li>
  <li><strong>Mock:</strong> <code>jest.mock</code>, <code>mockResolvedValue</code>, <code>mockRejectedValue</code>, <code>toHaveBeenCalledWith</code>.</li>
  <li><strong>Coverage va CI:</strong> <code>coverageThreshold</code>, <code>npm ci</code>, GitHub Actions.</li>
</ul>

<h3>Test yozishda tez-tez uchraydigan xatolar</h3>
<ul>
  <li><code>await</code> ni unutish: test tugab bo'lgach javob keladi va <code>expect</code> hech narsani tekshirmaydi.</li>
  <li>Testlarning bir-biriga bog'liqligi: bittasi yaratgan ma'lumotni boshqasi kutadi.</li>
  <li>Faqat muvaffaqiyatli holatni test qilish va 400 / 401 / 403 / 404 ni unutish.</li>
  <li>Hamma narsani mock qilish: test faqat o'z mocklarini tekshiradi.</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Quyida butun test to'plami: testlar va ularni ishga tushirish sozlamalari. Ilovaning o'zi (<code>app.js</code>, <code>repo.js</code>, <code>server.js</code>) 2-darsdagi bilan bir xil. Tekshiring: <code>npm test</code> 22 ta testni o'tkazadi, <code>npm run test:coverage</code> chegarani buzmaydi.</p>
<pre><code>__PACKAGE__</code></pre>
<pre><code>__WORKFLOW__</code></pre>
<p>Keyingi bosqich — vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, <strong>o'z Express API'ngiz</strong> (masalan, Node.js/Express kursining yakuniy loyihasi) uchun test to'plami va CI yozing.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>Jest:</strong> <code>describe</code>, <code>test</code>, <code>expect</code>, <code>test.each</code>, unit-тесты.</li>
  <li><strong>supertest:</strong> разделение <code>app</code> и <code>server</code>, тесты маршрутов через <code>request(app)</code>.</li>
  <li><strong>Защищённые маршруты:</strong> помощник для получения токена, 401 / 403 / 404, просроченный токен, тест владельца.</li>
  <li><strong>Моки:</strong> <code>jest.mock</code>, <code>mockResolvedValue</code>, <code>mockRejectedValue</code>, <code>toHaveBeenCalledWith</code>.</li>
  <li><strong>Coverage и CI:</strong> <code>coverageThreshold</code>, <code>npm ci</code>, GitHub Actions.</li>
</ul>

<h3>Частые ошибки при написании тестов</h3>
<ul>
  <li>Забыть <code>await</code>: тест завершается раньше, чем приходит ответ, и <code>expect</code> ничего не проверяет.</li>
  <li>Зависимость тестов друг от друга: один ждёт данные, созданные другим.</li>
  <li>Тестировать только успешный случай и забыть про 400 / 401 / 403 / 404.</li>
  <li>Мокать всё подряд: тест проверяет только собственные моки.</li>
</ul>

<h3>Готовое решение</h3>
<p>Ниже весь набор тестов: тесты и настройки их запуска. Само приложение (<code>app.js</code>, <code>repo.js</code>, <code>server.js</code>) такое же, как в уроке 2. Проверьте: <code>npm test</code> проходит 22 теста, а <code>npm run test:coverage</code> не нарушает порог.</p>
<pre><code>__PACKAGE__</code></pre>
<pre><code>__WORKFLOW__</code></pre>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, напишите набор тестов и CI для <strong>собственного Express API</strong> (например, итогового проекта курса по Node.js/Express).</p>"""

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: o'z API'ngiz uchun test to'plami va CI",
    "title_ru": "6-Повторение: набор тестов и CI для собственного API",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, PACKAGE=PACKAGE_L5, WORKFLOW=WORKFLOW_YML),
    "text_content_ru": _fill(_L6_TEXT_RU, PACKAGE=PACKAGE_L5, WORKFLOW=WORKFLOW_YML),
    "code_content": PACKAGE_L5,
    "code_content_ru": PACKAGE_L5,
    "code_language": "json",
    "sample": {
        "title": "Namuna: Notes API va to'liq test to'plami (22 test)",
        "title_ru": "Пример: Notes API и полный набор тестов (22 теста)",
        "description": "Ilova, 4 ta test fayli, coverage chegarasi va GitHub Actions workflow'i.",
        "description_ru": "Приложение, 4 файла тестов, порог coverage и workflow GitHub Actions.",
        "sample_type": "code",
        "code_files": [
            {"filename": "package.json", "language": "json", "code": PACKAGE_L5},
            {"filename": "src/validate.js", "language": "javascript", "code": CODE_VALIDATE},
            {"filename": "src/repo.js", "language": "javascript", "code": CODE_REPO},
            {"filename": "src/app.js", "language": "javascript", "code": CODE_APP},
            {"filename": "src/server.js", "language": "javascript", "code": CODE_SERVER},
            {"filename": "tests/validate.test.js", "language": "javascript", "code": TEST_VALIDATE},
            {"filename": "tests/auth.test.js", "language": "javascript", "code": TEST_AUTH},
            {"filename": "tests/notes.test.js", "language": "javascript", "code": TEST_NOTES},
            {"filename": "tests/errors.test.js", "language": "javascript", "code": TEST_ERRORS},
            {"filename": ".github/workflows/test.yml", "language": "yaml", "code": WORKFLOW_YML},
        ],
    },
    "task": {
        "task_title": "Loyiha: Express API uchun Jest + supertest testlari va CI",
        "task_title_ru": "Проект: тесты Jest + supertest и CI для Express API",
        "task_description": "O'z Express API'ngiz (masalan, Node.js/Express kursidagi yakuniy loyiha) uchun avtomatik test to'plamini yozing: supertest bilan route testlari, himoyalangan route'lar, mock bilan xatolarni tekshirish, coverage chegarasi va GitHub Actions workflow'i.",
        "task_description_ru": "Напишите набор автоматических тестов для собственного Express API (например, итогового проекта курса Node.js/Express): тесты маршрутов на supertest, защищённые маршруты, проверка ошибок через мок, порог coverage и workflow GitHub Actions.",
        "task_requirements": (
            "1) Ilova va serverni ajrating: app.js eksport qiladi, server.js faqat listen chaqiradi. "
            "2) supertest bilan kamida 6 ta route testi: muvaffaqiyat, 400 va 404 holatlari. "
            "3) Himoyalangan route uchun: tokensiz (401) va boshqa foydalanuvchining yozuvi (403 yoki 404) testlari. "
            "4) jest.mock bilan ma'lumotlar qatlamini almashtirib, kamida bitta 500 xato testi. "
            "5) test.each bilan kamida bitta unit test. "
            "6) coverageThreshold (qatorlar kamida 80%) va npm run test:coverage skripti. "
            "7) .github/workflows/test.yml: npm ci va testlarni yurgizish."
        ),
        "task_requirements_ru": (
            "1) Разделите приложение и сервер: app.js экспортирует приложение, server.js только вызывает listen. "
            "2) Не менее 6 тестов маршрутов на supertest: успех, случаи 400 и 404. "
            "3) Для защищённого маршрута: тесты без токена (401) и с чужой записью (403 или 404). "
            "4) Хотя бы один тест ошибки 500 с подменой слоя данных через jest.mock. "
            "5) Хотя бы один unit-тест на test.each. "
            "6) coverageThreshold (строки не менее 80%) и скрипт npm run test:coverage. "
            "7) .github/workflows/test.yml: npm ci и запуск тестов."
        ),
        "task_technologies": "Node.js, Express, Jest, supertest, GitHub Actions",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Yo'qolgan await", "title_ru": "Потерянный await",
            "description": "Testda so'rovdan oldin await yozish unutilsa nima bo'ladi?",
            "description_ru": "Что произойдёт, если в тесте забыть await перед запросом?",
            "exercise_type": "multiple_choice",
            "options": [
                "Test javob kelmasdan tugaydi va expect hech narsani tekshirmay qolishi mumkin",
                "Test avtomatik ravishda kutadi",
                "Jest xato bermaydi va hammasi to'g'ri",
                "Server o'chib qoladi",
            ],
            "options_ru": [
                "Тест завершится до прихода ответа, и expect может ничего не проверить",
                "Тест автоматически подождёт",
                "Jest не сообщит об ошибке, и всё в порядке",
                "Сервер выключится",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Request asinxron: u Promise qaytaradi.",
            "hint_ru": "Запрос асинхронный: он возвращает Promise.",
            "explanation": "Asinxron testda await bo'lmasa, test javobni kutmasdan tugaydi. Natijada noto'g'ri kod ham «o'tgan» test beradi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Testlarni ishga tushirish", "title_ru": "Запуск тестов",
            "description": "package.json dagi skriptni ishga tushiradigan buyruq: npm ___",
            "description_ru": "Команда, запускающая скрипт из package.json: npm ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "test",
            "hint": "Skript nomi bitta so'z: «test».",
            "hint_ru": "Название скрипта — одно слово: «test».",
            "explanation": "npm test package.json dagi \"test\" skriptini (bizda jest) ishga tushiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "O'z loyihangizni rejalashtirish", "title_ru": "План для вашего проекта",
            "description": "Loyihangiz uchun test to'plamini qaysi tartibda yozasiz va nimalarni qamraysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "В каком порядке вы напишете набор тестов для проекта и что покроете? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Avval ilova va serverni ajrataman, keyin supertest bilan route testlarini yozaman (muvaffaqiyat, 400, 404), so'ng himoyalangan route uchun 401 va egalik testlarini, jest.mock bilan bazadagi xato (500) testini va validatsiya uchun test.each unit testini qo'shaman. Oxirida coverage chegarasini va GitHub Actions workflow'ini sozlayman.",
            "hint": "Oddiydan murakkabga: ajratish, route'lar, himoya, mock, coverage, CI.",
            "hint_ru": "От простого к сложному: разделение, маршруты, защита, мок, coverage, CI.",
            "explanation": "Yaxshi reja ilovani test qilinadigan qiladi, keyin muvaffaqiyat va xato holatlarini, himoyani, mockni, coverage va CI'ni ketma-ket qo'shadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
