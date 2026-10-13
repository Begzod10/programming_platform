"""Flask: Token autentifikatsiya va CORS (API) — course spec (UZ + RU).

Authoring rules: docs/course-content-style.md. Run:
    python scripts/build_course.py course_specs/flask_jwt_cors.py --dry-run
Content changes go through THIS file only (UZ and RU are updated together). The course stays unpublished
(is_published=False) until a teacher has reviewed both languages.

Running example for the whole course: a Notes API (same domain as the Flask "R3-Notes REST API" lesson).
Endpoint and storage names match the team-project blueprints: POST /api/register, POST /api/login -> {token, username},
token kept by the frontend under the key `auth_token`.
Verified with: Flask 3.1, Flask-JWT-Extended 4.7, Flask-CORS 6.0, PyJWT 2.x.
"""

COURSE = {
    "title": "Flask: Token autentifikatsiya va CORS (API)",
    "title_ru": "Flask: токен-аутентификация и CORS (API)",
    "description": (
        "Flask API'ni token (JWT) bilan himoyalashni o'rganasiz: token nima va qanday ishlaydi, register va login, "
        "himoyalangan route'lar va rollar, CORS bilan frontendni ulash, API xatolari va testlash. "
        "Kurs oxirida tokenli Notes API va unga ulangan oddiy frontend yasaysiz."
    ),
    "description_ru": (
        "Вы научитесь защищать Flask API токеном (JWT): что такое токен и как он работает, регистрация и вход, "
        "защищённые маршруты и роли, подключение фронтенда через CORS, ошибки API и тестирование. "
        "В конце курса вы создадите Notes API с токенами и подключите к нему простой фронтенд."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 8,
    "prerequisite_course_id": 28,   # Python Flask — O'rta daraja
    "display_order": 303,
    "is_active": True,
    "is_published": False,
}

# ── 1-dars ──────────────────────────────────────────────────────────────────

_JWT_DEMO_UZ = '''import base64
import datetime as dt
import json

import jwt  # pip install PyJWT

SECRET = "change-me-use-a-long-random-secret-key-32chars"

# Payload: token ichidagi ma'lumot. exp — amal qilish muddati
payload = {
    "sub": "42",          # kim: foydalanuvchi id'si
    "role": "user",
    "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15),
}
token = jwt.encode(payload, SECRET, algorithm="HS256")
print(len(token.split(".")), "parts")

# Tekshirish: imzo va muddat tekshiriladi
data = jwt.decode(token, SECRET, algorithms=["HS256"])
print(data["sub"], data["role"])

# Payload shifrlanmagan: uni hamma o'qiy oladi
payload_part = token.split(".")[1]
padded = payload_part + "=" * (-len(payload_part) % 4)
print(json.loads(base64.urlsafe_b64decode(padded)))

# Boshqa kalit bilan imzo mos kelmaydi
try:
    jwt.decode(token, "another-secret-key-with-at-least-32-chars", algorithms=["HS256"])
except jwt.InvalidTokenError:
    print("invalid: signature mismatch")

# Muddati o'tgan token rad etiladi
old = jwt.encode({"sub": "42", "exp": dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)}, SECRET, algorithm="HS256")
try:
    jwt.decode(old, SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("invalid: token expired")
'''

_JWT_DEMO_RU = '''import base64
import datetime as dt
import json

import jwt  # pip install PyJWT

SECRET = "change-me-use-a-long-random-secret-key-32chars"

# Payload: данные внутри токена. exp — срок действия
payload = {
    "sub": "42",          # кто: id пользователя
    "role": "user",
    "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15),
}
token = jwt.encode(payload, SECRET, algorithm="HS256")
print(len(token.split(".")), "parts")

# Проверка: проверяются подпись и срок действия
data = jwt.decode(token, SECRET, algorithms=["HS256"])
print(data["sub"], data["role"])

# Payload не зашифрован: его может прочитать любой
payload_part = token.split(".")[1]
padded = payload_part + "=" * (-len(payload_part) % 4)
print(json.loads(base64.urlsafe_b64decode(padded)))

# С другим ключом подпись не совпадёт
try:
    jwt.decode(token, "another-secret-key-with-at-least-32-chars", algorithms=["HS256"])
except jwt.InvalidTokenError:
    print("invalid: signature mismatch")

# Токен с истёкшим сроком отклоняется
old = jwt.encode({"sub": "42", "exp": dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)}, SECRET, algorithm="HS256")
try:
    jwt.decode(old, SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("invalid: token expired")
'''

_L1_TEXT_UZ = """<h3>Muammo: server sizni qanday taniydi?</h3>
<p>HTTP <strong>xotirasiz</strong> (stateless) protokol: server har bir so'rovni yangi deb qabul qiladi va oldingi so'rovda kim bo'lganingizni eslamaydi. Login qilganingizdan keyin ham keyingi so'rovda server «bu o'sha foydalanuvchi» ekanini bilishi uchun biror <em>belgi</em> kerak. Bu belgi — <strong>token</strong>.</p>

<h3>Ikki yondashuv: sessiya va token</h3>
<ul>
  <li><strong>Sessiya:</strong> server foydalanuvchi haqidagi ma'lumotni o'z xotirasida (yoki bazada) saqlaydi, brauzerga faqat sessiya id'sini cookie qilib beradi. Flask-Login shunday ishlaydi. Server har safar saqlangan sessiyani qidiradi.</li>
  <li><strong>Token:</strong> kerakli ma'lumot tokenning ichida, server esa uni <em>imzolaydi</em>. Mijoz tokenni o'zi saqlaydi va har so'rovda yuboradi. Server hech narsa saqlamasdan faqat imzoni tekshiradi.</li>
</ul>
<p>Token yondashuvi <strong>API</strong>lar uchun qulay: mobil ilova, alohida frontend (React, oddiy JavaScript) va boshqa servislar cookie'siz ham bir xil usulda ishlaydi.</p>

<h3>Token qanday ishlaydi</h3>
<pre class="mermaid">
flowchart LR
  A["Mijoz: login + parol"] --> B["Server: parolni tekshiradi"]
  B --> C["Server: token yaratadi va imzolaydi"]
  C --> D["Mijoz tokenni saqlaydi"]
  D --> E["Har so'rovda: Authorization: Bearer eyJ..."]
  E --> F{"Imzo va muddat to'g'rimi?"}
  F -->|"ha"| G["So'rov bajariladi"]
  F -->|"yo'q"| H["401 Unauthorized"]
</pre>
<p>Diagrammada ko'rinadiki, parol faqat bir marta — loginda yuboriladi. Keyingi so'rovlarda faqat token yuboriladi.</p>

<h3>JWT tuzilishi</h3>
<p><strong>JWT</strong> (JSON Web Token) nuqta bilan ajratilgan <strong>uch qismdan</strong> iborat: <code>header.payload.signature</code>.</p>
<ul>
  <li><strong>header</strong> — algoritm va tur: <code>{"alg": "HS256", "typ": "JWT"}</code>;</li>
  <li><strong>payload</strong> — ma'lumotlar (<em>claim</em>lar): <code>sub</code> (kim), <code>exp</code> (muddat), o'zimiz qo'shgan <code>role</code> kabi;</li>
  <li><strong>signature</strong> — header va payload'dan maxfiy kalit bilan hisoblangan imzo (HS256 = HMAC-SHA256). Birorta belgi o'zgarsa, imzo mos kelmaydi.</li>
</ul>
<p>Birinchi ikki qism oddiy <em>base64url</em> bilan kodlangan, ya'ni <strong>shifrlanmagan</strong>. Imzo ma'lumotni yashirmaydi, faqat uning o'zgartirilmaganini kafolatlaydi.</p>

<h3>PyJWT bilan amaliyot</h3>
<p>Quyidagi dastur token yaratadi, tekshiradi, payload'ni o'qiydi va ikki xil yaroqsiz tokenni rad etadi. Uni o'zingiz ishga tushirib ko'ring (<code>pip install PyJWT</code>).</p>
<pre><code>__CODE__</code></pre>
<p>Natija: <code>3 parts</code>, keyin <code>42 user</code>, payload lug'ati (<code>sub</code>, <code>role</code>, <code>exp</code>) va ikkala <code>invalid: ...</code> xabari.</p>

<h3>Xavfsizlik qoidalari</h3>
<ul>
  <li><strong>Payload'ga parol, karta raqami kabi maxfiy ma'lumot yozmang</strong>: uni tokenni ushlagan har kim o'qiydi.</li>
  <li><strong>Maxfiy kalit</strong> (<code>SECRET</code>) kodga yozilmaydi, muhit o'zgaruvchisidan olinadi. Kalitni bilgan odam o'zi uchun token yasay oladi.</li>
  <li><strong>Muddatni qisqa qiling</strong> (<code>exp</code>, masalan 15–60 daqiqa): token o'g'irlansa, zarar chegaralangan bo'ladi. Berilgan tokenni muddatidan oldin «bekor qilib» bo'lmaydi.</li>
  <li>Tokenni faqat <strong>HTTPS</strong> orqali yuboring.</li>
</ul>
<p>Keyingi darsda shu g'oyani Flask'da <strong>Flask-JWT-Extended</strong> bilan amalga oshirib, <code>/api/register</code> va <code>/api/login</code> yozamiz.</p>"""

_L1_TEXT_RU = """<h3>Проблема: как сервер узнаёт вас?</h3>
<p>HTTP — протокол <strong>без состояния</strong> (stateless): сервер воспринимает каждый запрос как новый и не помнит, кем вы были в предыдущем. Чтобы после входа сервер понимал в следующем запросе, что это тот же пользователь, нужна какая-то <em>метка</em>. Эта метка — <strong>токен</strong>.</p>

<h3>Два подхода: сессия и токен</h3>
<ul>
  <li><strong>Сессия:</strong> сервер хранит данные о пользователе у себя (в памяти или в базе данных), а браузеру отдаёт только id сессии в cookie. Так работает Flask-Login. Каждый раз сервер ищет сохранённую сессию.</li>
  <li><strong>Токен:</strong> нужные данные лежат внутри токена, а сервер его <em>подписывает</em>. Клиент сам хранит токен и отправляет его в каждом запросе. Сервер ничего не хранит и только проверяет подпись.</li>
</ul>
<p>Подход с токеном удобен для <strong>API</strong>: мобильное приложение, отдельный фронтенд (React, обычный JavaScript) и другие сервисы работают одинаково и без cookie.</p>

<h3>Как работает токен</h3>
<pre class="mermaid">
flowchart LR
  A["Клиент: логин + пароль"] --> B["Сервер: проверяет пароль"]
  B --> C["Сервер: создаёт токен и подписывает"]
  C --> D["Клиент сохраняет токен"]
  D --> E["В каждом запросе: Authorization: Bearer eyJ..."]
  E --> F{"Подпись и срок верны?"}
  F -->|"да"| G["Запрос выполняется"]
  F -->|"нет"| H["401 Unauthorized"]
</pre>
<p>На диаграмме видно, что пароль отправляется только один раз — при входе. В следующих запросах отправляется только токен.</p>

<h3>Устройство JWT</h3>
<p><strong>JWT</strong> (JSON Web Token) состоит из <strong>трёх частей</strong>, разделённых точками: <code>header.payload.signature</code>.</p>
<ul>
  <li><strong>header</strong> — алгоритм и тип: <code>{"alg": "HS256", "typ": "JWT"}</code>;</li>
  <li><strong>payload</strong> — данные (<em>claim</em>-ы): <code>sub</code> (кто), <code>exp</code> (срок), а также свои, например <code>role</code>;</li>
  <li><strong>signature</strong> — подпись, вычисленная от header и payload секретным ключом (HS256 = HMAC-SHA256). Если изменить хоть один символ, подпись перестанет совпадать.</li>
</ul>
<p>Первые две части просто закодированы в <em>base64url</em>, то есть <strong>не зашифрованы</strong>. Подпись не скрывает данные, а лишь гарантирует, что их не изменили.</p>

<h3>Практика с PyJWT</h3>
<p>Программа ниже создаёт токен, проверяет его, читает payload и отклоняет два вида недействительных токенов. Запустите её сами (<code>pip install PyJWT</code>).</p>
<pre><code>__CODE__</code></pre>
<p>Результат: <code>3 parts</code>, затем <code>42 user</code>, словарь payload (<code>sub</code>, <code>role</code>, <code>exp</code>) и оба сообщения <code>invalid: ...</code>.</p>

<h3>Правила безопасности</h3>
<ul>
  <li><strong>Не записывайте в payload пароль, номер карты и другие секреты</strong>: их прочитает любой, у кого есть токен.</li>
  <li><strong>Секретный ключ</strong> (<code>SECRET</code>) не пишут в коде, а берут из переменной окружения. Кто знает ключ, может сам создавать токены.</li>
  <li><strong>Делайте срок короче</strong> (<code>exp</code>, например 15–60 минут): если токен украдут, ущерб ограничен. Выданный токен нельзя «отозвать» раньше срока.</li>
  <li>Передавайте токен только по <strong>HTTPS</strong>.</li>
</ul>
<p>В следующем уроке мы реализуем эту идею во Flask с помощью <strong>Flask-JWT-Extended</strong> и напишем <code>/api/register</code> и <code>/api/login</code>.</p>"""


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


LESSON_1 = {
    "order": 0,
    "title": "1-Token nima va nega kerak",
    "title_ru": "1-Что такое токен и зачем он нужен",
    "points_reward": 10,
    "text_content": _L1_TEXT_UZ.replace("__CODE__", _esc(_JWT_DEMO_UZ)),
    "text_content_ru": _L1_TEXT_RU.replace("__CODE__", _esc(_JWT_DEMO_RU)),
    "code_content": _JWT_DEMO_UZ,
    "code_content_ru": _JWT_DEMO_RU,
    "code_language": "python",
    "sample": {
        "title": "Namuna: JWT yaratish va tekshirish",
        "title_ru": "Пример: создание и проверка JWT",
        "description": "PyJWT bilan token yaratish, tekshirish, payload'ni o'qish va yaroqsiz tokenlarni rad etish.",
        "description_ru": "Создание и проверка токена с PyJWT, чтение payload и отклонение недействительных токенов.",
        "sample_type": "code",
        "code_files": [{"filename": "jwt_demo.py", "language": "python", "code": _JWT_DEMO_UZ}],
    },
    "exercises": [
        {
            "title": "JWT qismlari", "title_ru": "Части JWT",
            "description": "JWT nechta qismdan iborat va ular qanday ajratiladi?",
            "description_ru": "Из скольких частей состоит JWT и как они разделяются?",
            "exercise_type": "multiple_choice",
            "options": [
                "Ikki qism: header va payload, nuqta bilan",
                "Uch qism: header, payload va signature, nuqta bilan",
                "To'rt qism, vergul bilan ajratilgan",
                "Bitta qism: faqat signature",
            ],
            "options_ru": [
                "Две части: header и payload, через точку",
                "Три части: header, payload и signature, через точку",
                "Четыре части, разделённые запятой",
                "Одна часть: только signature",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Token ko'rinishini eslang: header.payload.signature.",
            "hint_ru": "Вспомните вид токена: header.payload.signature.",
            "explanation": "JWT uch qismdan iborat: header, payload va signature. Ular nuqta bilan ajratiladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Token oqimi", "title_ru": "Поток токена",
            "description": "Token bilan ishlash qadamlarini to'g'ri tartibga joylashtiring.",
            "description_ru": "Расположите шаги работы с токеном в правильном порядке.",
            "exercise_type": "drag_and_drop",
            "drag_items": [
                "Mijoz login va parolni yuboradi",
                "Server parolni tekshirib, token yaratadi",
                "Mijoz tokenni saqlaydi",
                "Mijoz har so'rovda tokenni yuboradi",
                "Server imzoni tekshirib, javob beradi",
            ],
            "drag_items_ru": [
                "Клиент отправляет логин и пароль",
                "Сервер проверяет пароль и создаёт токен",
                "Клиент сохраняет токен",
                "Клиент отправляет токен в каждом запросе",
                "Сервер проверяет подпись и отвечает",
            ],
            "correct_order": [
                "Mijoz login va parolni yuboradi",
                "Server parolni tekshirib, token yaratadi",
                "Mijoz tokenni saqlaydi",
                "Mijoz har so'rovda tokenni yuboradi",
                "Server imzoni tekshirib, javob beradi",
            ],
            "hint": "Token avval yaratiladi, keyin ishlatiladi.",
            "hint_ru": "Токен сначала создаётся, потом используется.",
            "explanation": "Parol faqat loginda yuboriladi. Undan keyin mijoz faqat tokenni yuboradi, server esa imzoni tekshiradi.",
            "difficulty_level": "Easy", "points": 4,
        },
        {
            "title": "Authorization sarlavhasi", "title_ru": "Заголовок Authorization",
            "description": "Token so'rovda shunday yuboriladi: Authorization: ___ eyJhbGciOiJIUzI1NiJ9...",
            "description_ru": "Токен отправляется в запросе так: Authorization: ___ eyJhbGciOiJIUzI1NiJ9...",
            "exercise_type": "fill_in_blank",
            "correct_answers": "Bearer",
            "hint": "Sarlavhadagi tokendan oldingi so'z — tur nomi.",
            "hint_ru": "Слово перед токеном в заголовке — название схемы.",
            "explanation": "Standart sxema «Bearer»: Authorization sarlavhasida «Bearer» va bo'sh joydan keyin token yoziladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Payload'da nima xavfsiz", "title_ru": "Что безопасно хранить в payload",
            "description": "JWT payload'iga qaysilarni yozish xavfsiz? To'g'ri javoblarni tanlang.",
            "description_ru": "Что безопасно записывать в payload JWT? Выберите правильные ответы.",
            "exercise_type": "multiple_choice",
            "options": [
                "Foydalanuvchi id'si (sub)",
                "Foydalanuvchi roli (masalan, user yoki admin)",
                "Foydalanuvchining paroli",
                "Bank kartasi raqami",
            ],
            "options_ru": [
                "id пользователя (sub)",
                "Роль пользователя (например, user или admin)",
                "Пароль пользователя",
                "Номер банковской карты",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Payload'ni tokenni ushlagan har kim o'qiy oladi.",
            "hint_ru": "Payload может прочитать любой, у кого есть токен.",
            "explanation": "Payload shifrlanmagan, faqat base64url bilan kodlangan. Shuning uchun u yerga faqat maxfiy bo'lmagan ma'lumot (id, rol) yoziladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega imzo kerak", "title_ru": "Зачем нужна подпись",
            "description": "Agar payload shifrlanmagan bo'lsa, JWT'dagi imzo (signature) nima uchun kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Если payload не зашифрован, зачем в JWT нужна подпись (signature)? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Imzo ma'lumotni yashirmaydi, lekin token o'zgartirilmaganini yoki soxtalashtirilmaganini tekshirishga imkon beradi: maxfiy kalitsiz to'g'ri imzo yasab bo'lmaydi.",
            "hint": "Imzo ma'lumotni yashirish uchun emas, boshqa narsa uchun.",
            "hint_ru": "Подпись нужна не для того, чтобы скрывать данные, а для другого.",
            "explanation": "Imzo yaxlitlikni (integrity) kafolatlaydi: kimdir payload'ni o'zgartirsa yoki soxta token yasasa, maxfiy kalitsiz to'g'ri imzo hosil qila olmaydi va server uni rad etadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

# ── 2-dars: register va login ────────────────────────────────────────────────

_L2_CODE = '''import datetime as dt
import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-use-a-long-random-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.timedelta(minutes=30)
jwt = JWTManager(app)

users = {}   # username -> {"id", "password_hash"}


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if len(username) < 3 or len(password) < 6:
        return jsonify(error="username needs 3+ and password 6+ characters"), 400
    if username in users:
        return jsonify(error="username is taken"), 409
    users[username] = {"id": len(users) + 1, "password_hash": generate_password_hash(password)}
    return jsonify(message="registered"), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    user = users.get(username)
    if user is None or not check_password_hash(user["password_hash"], data.get("password") or ""):
        return jsonify(error="invalid username or password"), 401
    token = create_access_token(identity=str(user["id"]))
    return jsonify(token=token, username=username)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
'''

_L2_CURL = '''curl -X POST http://127.0.0.1:5000/api/register -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl -X POST http://127.0.0.1:5000/api/login -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
'''

_L2_TEXT_UZ = """<h3>Reja</h3>
<p>Bu darsda Notes API'ning kirish qismini yozamiz: <code>POST /api/register</code> (ro'yxatdan o'tish) va <code>POST /api/login</code> (kirish va token olish). Login muvaffaqiyatli bo'lsa, server <code>{"token": "...", "username": "..."}</code> qaytaradi. Aynan shu shakl keyingi darslardagi frontend va jamoaviy loyihalarda ham ishlatiladi.</p>

<h3>O'rnatish va sozlash</h3>
<pre><code>pip install Flask Flask-JWT-Extended</code></pre>
<p><strong>Flask-JWT-Extended</strong> token yaratish va tekshirishni Flask'ga ulaydi. Ikkita muhim sozlama:</p>
<ul>
  <li><code>JWT_SECRET_KEY</code> — token imzolanadigan maxfiy kalit. Uni <strong>kodga yozmang</strong>, muhit o'zgaruvchisidan oling (<code>os.environ</code>). Quyidagi misoldagi zaxira qiymat faqat o'qish va sinash uchun.</li>
  <li><code>JWT_ACCESS_TOKEN_EXPIRES</code> — tokenning amal qilish muddati. Standart qiymat 15 daqiqa; biz 30 daqiqa qo'ydik.</li>
</ul>

<h3>Parolni xeshlash</h3>
<p>Parol bazada <strong>hech qachon ochiq matnda</strong> saqlanmaydi. Werkzeug'ning <code>generate_password_hash</code> funksiyasi parolni qaytarib bo'lmaydigan xeshga aylantiradi, <code>check_password_hash</code> esa kiritilgan parolni saqlangan xesh bilan solishtiradi. Bu funksiyalar Flask bilan birga o'rnatilgan.</p>

<h3>Register va login</h3>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>identity</code> — token ichiga yoziladigan «kim». Flask-JWT-Extended uni <strong>satr</strong> sifatida kutadi, shuning uchun <code>str(user["id"])</code>.</li>
  <li>Status kodlar: <code>201</code> — yaratildi, <code>400</code> — noto'g'ri ma'lumot, <code>409</code> — login band, <code>401</code> — kirish rad etildi.</li>
  <li>Noto'g'ri login va noto'g'ri parol uchun <strong>bir xil xabar</strong> qaytaring: aks holda hujumchi qaysi loginlar mavjudligini bilib oladi.</li>
</ul>
<p>Misolda foydalanuvchilar oddiylik uchun xotirada (<code>users</code> lug'ati) saqlanadi: server qayta ishga tushsa, ular yo'qoladi. Haqiqiy loyihada bu ma'lumotlar bazaga (masalan, SQLAlchemy) yoziladi, token qismi esa aynan shunday qoladi.</p>

<h3>Sinab ko'ring</h3>
<p>Serverni <code>python app.py</code> bilan ishga tushiring va boshqa terminalda:</p>
<pre><code>__CURL__</code></pre>
<p>Ikkinchi so'rov <code>{"token": "eyJ...", "username": "ali"}</code> qaytaradi. Tokenni nusxalab, 1-darsdagi <code>jwt.decode</code> bilan ochib, ichidagi <code>sub</code> va <code>exp</code> ni ko'ring.</p>"""

_L2_TEXT_RU = """<h3>План</h3>
<p>В этом уроке мы напишем «входную» часть Notes API: <code>POST /api/register</code> (регистрация) и <code>POST /api/login</code> (вход и получение токена). При успешном входе сервер возвращает <code>{"token": "...", "username": "..."}</code>. Именно такой формат используется дальше во фронтенде и в командных проектах.</p>

<h3>Установка и настройка</h3>
<pre><code>pip install Flask Flask-JWT-Extended</code></pre>
<p><strong>Flask-JWT-Extended</strong> подключает создание и проверку токенов к Flask. Две важные настройки:</p>
<ul>
  <li><code>JWT_SECRET_KEY</code> — секретный ключ, которым подписываются токены. <strong>Не пишите его в коде</strong>, берите из переменной окружения (<code>os.environ</code>). Запасное значение в примере ниже — только для чтения и проб.</li>
  <li><code>JWT_ACCESS_TOKEN_EXPIRES</code> — срок действия токена. По умолчанию 15 минут; мы поставили 30 минут.</li>
</ul>

<h3>Хеширование пароля</h3>
<p>Пароль <strong>никогда не хранится в открытом виде</strong>. Функция <code>generate_password_hash</code> из Werkzeug превращает пароль в необратимый хеш, а <code>check_password_hash</code> сравнивает введённый пароль с сохранённым хешем. Эти функции устанавливаются вместе с Flask.</p>

<h3>Регистрация и вход</h3>
<pre><code>__CODE__</code></pre>
<ul>
  <li><code>identity</code> — «кто» записывается в токен. Flask-JWT-Extended ожидает <strong>строку</strong>, поэтому <code>str(user["id"])</code>.</li>
  <li>Коды статуса: <code>201</code> — создано, <code>400</code> — неверные данные, <code>409</code> — логин занят, <code>401</code> — вход отклонён.</li>
  <li>Для неверного логина и неверного пароля возвращайте <strong>одинаковое сообщение</strong>: иначе злоумышленник узнает, какие логины существуют.</li>
</ul>
<p>Для простоты в примере пользователи хранятся в памяти (словарь <code>users</code>): после перезапуска сервера они пропадут. В реальном проекте эти данные записываются в базу данных (например, через SQLAlchemy), а часть с токеном остаётся такой же.</p>

<h3>Проверьте сами</h3>
<p>Запустите сервер командой <code>python app.py</code> и в другом терминале выполните:</p>
<pre><code>__CURL__</code></pre>
<p>Второй запрос вернёт <code>{"token": "eyJ...", "username": "ali"}</code>. Скопируйте токен, откройте его через <code>jwt.decode</code> из первого урока и посмотрите на <code>sub</code> и <code>exp</code> внутри.</p>"""

LESSON_2 = {
    "order": 1,
    "title": "2-Flask-JWT-Extended: register va login",
    "title_ru": "2-Flask-JWT-Extended: регистрация и вход",
    "points_reward": 10,
    "text_content": _L2_TEXT_UZ.replace("__CODE__", _esc(_L2_CODE)).replace("__CURL__", _esc(_L2_CURL)),
    "text_content_ru": _L2_TEXT_RU.replace("__CODE__", _esc(_L2_CODE)).replace("__CURL__", _esc(_L2_CURL)),
    "code_content": _L2_CODE,
    "code_content_ru": _L2_CODE,
    "code_language": "python",
    "sample": {
        "title": "Namuna: register va login",
        "title_ru": "Пример: регистрация и вход",
        "description": "Flask-JWT-Extended bilan /api/register va /api/login: parol xeshi, token yaratish, bir xil xato xabari.",
        "description_ru": "/api/register и /api/login на Flask-JWT-Extended: хеш пароля, создание токена, одинаковое сообщение об ошибке.",
        "sample_type": "code",
        "code_files": [{"filename": "app.py", "language": "python", "code": _L2_CODE}],
    },
    "exercises": [
        {
            "title": "Parolni saqlash", "title_ru": "Хранение пароля",
            "description": "Foydalanuvchi parolini bazada qanday saqlash to'g'ri?",
            "description_ru": "Как правильно хранить пароль пользователя в базе данных?",
            "exercise_type": "multiple_choice",
            "options": [
                "Ochiq matnda, qidirish oson bo'lishi uchun",
                "generate_password_hash bilan olingan xesh ko'rinishida",
                "Base64 bilan kodlab",
                "Parol o'rniga tokenni saqlab",
            ],
            "options_ru": [
                "В открытом виде, чтобы проще искать",
                "В виде хеша, полученного через generate_password_hash",
                "Закодировав в Base64",
                "Хранить токен вместо пароля",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Saqlangan qiymatdan asl parolni tiklab bo'lmasligi kerak.",
            "hint_ru": "По сохранённому значению нельзя восстановить исходный пароль.",
            "explanation": "Xesh qaytarilmaydi: baza o'g'irlansa ham parollar ochiq bo'lmaydi. Base64 esa shifrlash emas, uni osongina qaytarish mumkin.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Login qadamlari", "title_ru": "Шаги входа",
            "description": "Login endpoint'ining ishlash tartibini joylashtiring.",
            "description_ru": "Расположите шаги работы эндпоинта входа в правильном порядке.",
            "exercise_type": "drag_and_drop",
            "drag_items": [
                "So'rovdan JSON'ni o'qish",
                "Foydalanuvchini login bo'yicha topish",
                "Parol xeshini tekshirish",
                "Token yaratish",
                "Token va username'ni qaytarish",
            ],
            "drag_items_ru": [
                "Прочитать JSON из запроса",
                "Найти пользователя по логину",
                "Проверить хеш пароля",
                "Создать токен",
                "Вернуть токен и username",
            ],
            "correct_order": [
                "So'rovdan JSON'ni o'qish",
                "Foydalanuvchini login bo'yicha topish",
                "Parol xeshini tekshirish",
                "Token yaratish",
                "Token va username'ni qaytarish",
            ],
            "hint": "Token faqat parol tasdiqlangandan keyin beriladi.",
            "hint_ru": "Токен выдаётся только после подтверждения пароля.",
            "explanation": "Avval ma'lumot o'qiladi, foydalanuvchi va parol tekshiriladi; faqat shundan keyin token yaratilib, mijozga qaytariladi.",
            "difficulty_level": "Easy", "points": 4,
        },
        {
            "title": "Token yaratish funksiyasi", "title_ru": "Функция создания токена",
            "description": "Flask-JWT-Extended'da token yaratadigan funksiya: ___(identity=str(user_id))",
            "description_ru": "Функция Flask-JWT-Extended, создающая токен: ___(identity=str(user_id))",
            "exercise_type": "fill_in_blank",
            "correct_answers": "create_access_token",
            "hint": "Nomida «create», «access» va «token» so'zlari bor.",
            "hint_ru": "В названии есть слова «create», «access» и «token».",
            "explanation": "create_access_token(identity=...) token yaratadi va imzolaydi. Identity satr bo'lishi kerak.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Status kodlar", "title_ru": "Коды статуса",
            "description": "Qaysi juftlik to'g'ri: «login band» va «parol noto'g'ri» holatlari uchun status kodlar?",
            "description_ru": "Какая пара верна: коды статуса для случаев «логин занят» и «неверный пароль»?",
            "exercise_type": "multiple_choice",
            "options": [
                "Login band — 401, noto'g'ri parol — 409",
                "Login band — 409, noto'g'ri parol — 401",
                "Ikkalasi ham — 200",
                "Ikkalasi ham — 500",
            ],
            "options_ru": [
                "Логин занят — 401, неверный пароль — 409",
                "Логин занят — 409, неверный пароль — 401",
                "Оба — 200",
                "Оба — 500",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "409 — «ziddiyat» (resurs allaqachon bor), 401 — «kirish rad etildi».",
            "hint_ru": "409 — «конфликт» (ресурс уже существует), 401 — «вход отклонён».",
            "explanation": "Band login — ziddiyat (409 Conflict). Noto'g'ri parol — autentifikatsiya muvaffaqiyatsiz (401 Unauthorized).",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Maxfiy kalit", "title_ru": "Секретный ключ",
            "description": "JWT_SECRET_KEY nima uchun kodga yozilmaydi va uni qayerdan olish kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему JWT_SECRET_KEY не пишут в коде и откуда его нужно брать? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Kalitni bilgan kishi o'zi uchun to'g'ri imzolangan token yasay oladi; kod GitHub'ga tushsa kalit ham ochiladi. Shuning uchun uni muhit o'zgaruvchisidan (os.environ) olish kerak.",
            "hint": "Kodga kim kirish huquqiga ega bo'lishini o'ylang (masalan, repozitoriy).",
            "hint_ru": "Подумайте, кто может получить доступ к коду (например, к репозиторию).",
            "explanation": "Maxfiy kalit bo'yicha token imzolanadi. Kalit sizib chiqsa, hujumchi istalgan foydalanuvchi uchun token yaratadi. Shu sababli kalit kodda emas, muhit o'zgaruvchisida saqlanadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3–6-darslar uchun umumiy Notes API (kod bitta manbadan olinadi) ──────────

_APP_FULL = '''import datetime as dt
import os
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-use-a-long-random-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.timedelta(minutes=30)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080"]}}, allow_headers=["Content-Type", "Authorization"])

users = {}   # username -> {"id", "password_hash", "role"}
notes = []   # {"id", "text", "owner_id"}


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if len(username) < 3 or len(password) < 6:
        return jsonify(error="username needs 3+ and password 6+ characters"), 400
    if username in users:
        return jsonify(error="username is taken"), 409
    role = "admin" if username == os.environ.get("ADMIN_USERNAME") else "user"
    users[username] = {"id": len(users) + 1, "password_hash": generate_password_hash(password), "role": role}
    return jsonify(message="registered"), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    user = users.get(username)
    if user is None or not check_password_hash(user["password_hash"], data.get("password") or ""):
        return jsonify(error="invalid username or password"), 401
    token = create_access_token(identity=str(user["id"]), additional_claims={"role": user["role"]})
    return jsonify(token=token, username=username)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return jsonify(error="admin only"), 403
        return fn(*args, **kwargs)
    return wrapper


@app.get("/api/notes")
@jwt_required()
def list_notes():
    if get_jwt().get("role") == "admin":
        return jsonify(notes)
    owner_id = int(get_jwt_identity())
    return jsonify([n for n in notes if n["owner_id"] == owner_id])


@app.post("/api/notes")
@jwt_required()
def create_note():
    text = ((request.get_json(silent=True) or {}).get("text") or "").strip()
    if not text:
        return jsonify(error="text is required"), 400
    note = {"id": len(notes) + 1, "text": text, "owner_id": int(get_jwt_identity())}
    notes.append(note)
    return jsonify(note), 201


@app.delete("/api/notes/<int:note_id>")
@jwt_required()
def delete_note(note_id):
    note = next((n for n in notes if n["id"] == note_id), None)
    if note is None:
        return jsonify(error="note not found"), 404
    if note["owner_id"] != int(get_jwt_identity()) and get_jwt().get("role") != "admin":
        return jsonify(error="not your note"), 403
    notes.remove(note)
    return jsonify(message="deleted")


@app.get("/api/admin/users")
@admin_required
def list_users():
    return jsonify([{"id": u["id"], "username": name, "role": u["role"]} for name, u in users.items()])


@jwt.unauthorized_loader
def missing_token(reason):
    return jsonify(error="authorization token is required", code="token_missing"), 401


@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify(error="token is invalid", code="token_invalid"), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify(error="token has expired", code="token_expired"), 401


if __name__ == "__main__":
    app.run(port=5000, debug=True)
'''

_LOADERS_START = "\n\n@jwt.unauthorized_loader"
_MAIN_START = '\n\nif __name__ == "__main__":'
_CORS_LINE = 'CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080"]}}, allow_headers=["Content-Type", "Authorization"])\n'

# 4-dars: 5-darsdagi xato ishlovchilarsiz; 3-dars: CORS ham yo'q
_APP_NO_LOADERS = _APP_FULL.split(_LOADERS_START)[0] + _APP_FULL[_APP_FULL.index(_MAIN_START):]
_APP_NO_CORS = _APP_NO_LOADERS.replace("from flask_cors import CORS\n", "").replace(_CORS_LINE, "")

_API_JS = '''const API = "http://127.0.0.1:5000";

async function login(username, password) {
  const res = await fetch(`${API}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  localStorage.setItem("auth_token", data.token);
  return data;
}

async function loadNotes() {
  const res = await fetch(`${API}/api/notes`, {
    headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
  });
  if (res.status === 401) {
    localStorage.removeItem("auth_token");
    throw new Error("login required");
  }
  return res.json();
}
'''

_TEST_APP = '''import datetime as dt

import pytest
from flask_jwt_extended import create_access_token

import app as notes_app


@pytest.fixture
def client():
    notes_app.users.clear()
    notes_app.notes.clear()
    notes_app.app.config["TESTING"] = True
    return notes_app.app.test_client()


def register_and_login(client, username="ali", password="secret12"):
    assert client.post("/api/register", json={"username": username, "password": password}).status_code == 201
    token = client.post("/api/login", json={"username": username, "password": password}).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_validates_and_rejects_duplicates(client):
    assert client.post("/api/register", json={"username": "a", "password": "secret12"}).status_code == 400
    assert client.post("/api/register", json={"username": "ali", "password": "secret12"}).status_code == 201
    assert client.post("/api/register", json={"username": "ali", "password": "secret12"}).status_code == 409


def test_login_returns_a_token_only_for_the_right_password(client):
    client.post("/api/register", json={"username": "ali", "password": "secret12"})
    assert client.post("/api/login", json={"username": "ali", "password": "wrong"}).status_code == 401
    ok = client.post("/api/login", json={"username": "ali", "password": "secret12"})
    assert ok.status_code == 200 and ok.get_json()["token"].count(".") == 2


def test_notes_need_a_token(client):
    res = client.get("/api/notes")
    assert res.status_code == 401 and res.get_json()["code"] == "token_missing"
    bad = client.get("/api/notes", headers={"Authorization": "Bearer garbage"})
    assert bad.status_code == 401 and bad.get_json()["code"] == "token_invalid"


def test_an_expired_token_is_rejected_with_its_own_code(client):
    with notes_app.app.app_context():
        old = create_access_token(identity="1", expires_delta=dt.timedelta(seconds=-1))
    res = client.get("/api/notes", headers={"Authorization": f"Bearer {old}"})
    assert res.status_code == 401 and res.get_json()["code"] == "token_expired"


def test_users_only_see_and_delete_their_own_notes(client):
    ali, vali = register_and_login(client, "ali"), register_and_login(client, "vali")
    client.post("/api/notes", json={"text": "ali note"}, headers=ali)
    assert [n["text"] for n in client.get("/api/notes", headers=ali).get_json()] == ["ali note"]
    assert client.get("/api/notes", headers=vali).get_json() == []
    assert client.delete("/api/notes/1", headers=vali).status_code == 403
    assert client.delete("/api/notes/1", headers=ali).status_code == 200
    assert client.delete("/api/notes/1", headers=ali).status_code == 404


def test_admin_sees_everything_and_only_admin_lists_users(client, monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "boss")
    boss, ali = register_and_login(client, "boss"), register_and_login(client, "ali")
    client.post("/api/notes", json={"text": "ali note"}, headers=ali)
    assert len(client.get("/api/notes", headers=boss).get_json()) == 1
    assert client.get("/api/admin/users", headers=boss).status_code == 200
    assert client.get("/api/admin/users", headers=ali).status_code == 403


def test_cors_allows_the_frontend_origin_and_the_authorization_header(client):
    pre = client.options("/api/notes", headers={"Origin": "http://localhost:8080", "Access-Control-Request-Method": "GET",
                                               "Access-Control-Request-Headers": "authorization"})
    assert pre.headers["Access-Control-Allow-Origin"] == "http://localhost:8080"
    assert "authorization" in pre.headers["Access-Control-Allow-Headers"].lower()
    other = client.options("/api/notes", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"})
    assert "Access-Control-Allow-Origin" not in other.headers
'''

_INDEX_HTML = '''<!doctype html>
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

_CURL_AUTH = '''curl http://127.0.0.1:5000/api/notes
curl -X POST http://127.0.0.1:5000/api/notes -H "Authorization: Bearer eyJ..." -H "Content-Type: application/json" -d '{"text": "buy bread"}'
curl http://127.0.0.1:5000/api/admin/users -H "Authorization: Bearer eyJ..."
'''

_PREFLIGHT_CURL = '''curl -i -X OPTIONS http://127.0.0.1:5000/api/notes -H "Origin: http://localhost:8080" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: authorization"
'''

_POSTMAN_SCRIPT = '''const data = pm.response.json();
pm.collectionVariables.set("token", data.token);
'''

_L3_SNIPPET = '''@app.get("/api/notes")
@jwt_required()
def list_notes():
    if get_jwt().get("role") == "admin":
        return jsonify(notes)
    owner_id = int(get_jwt_identity())
    return jsonify([n for n in notes if n["owner_id"] == owner_id])
'''

_L5_SNIPPET = '''@jwt.unauthorized_loader
def missing_token(reason):
    return jsonify(error="authorization token is required", code="token_missing"), 401


@jwt.invalid_token_loader
def invalid_token(reason):
    return jsonify(error="token is invalid", code="token_invalid"), 401


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return jsonify(error="token has expired", code="token_expired"), 401
'''

_L5_TEST_SNIPPET = '''def test_notes_need_a_token(client):
    res = client.get("/api/notes")
    assert res.status_code == 401 and res.get_json()["code"] == "token_missing"
'''


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


# ── 3-dars ───────────────────────────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>Himoyalangan route</h3>
<p>Route'ni himoyalash uchun unga <code>@jwt_required()</code> dekoratorini qo'yamiz. Dekorator <code>Authorization: Bearer &lt;token&gt;</code> sarlavhasini tekshiradi: token yo'q, buzilgan yoki muddati o'tgan bo'lsa, funksiya umuman ishga tushmaydi va server <code>401</code> qaytaradi. Funksiya ichida esa «so'rovni kim yubordi» degan savolga <code>get_jwt_identity()</code> javob beradi.</p>
<pre><code>__SNIPPET__</code></pre>

<h3>Rol: tokenga qo'shimcha ma'lumot</h3>
<p>Login paytida <code>additional_claims={"role": "admin"}</code> bilan tokenga rolni yozamiz. Keyin istalgan route'da <code>get_jwt()</code> butun payload'ni lug'at sifatida beradi. Shu sababli har so'rovda bazaga murojaat qilmasdan rolni bilamiz. Eslatma: payload ochiq o'qiladi, shuning uchun unga parol kabi sir yozmang.</p>

<h3>Adminga xos route</h3>
<p>Rolni tekshirishni har joyda takrorlamaslik uchun o'zimizning dekoratorimizni yozamiz. <code>@wraps</code> asl funksiyaning nomini saqlaydi (Flask uchun muhim), ichkarida esa <code>@jwt_required()</code> ishlaydi:</p>
<pre class="mermaid">
flowchart TD
  A["So'rov + Authorization sarlavhasi"] --> B{"Token to'g'rimi?"}
  B -- "yo'q" --> C["401 Unauthorized"]
  B -- "ha" --> D{"Rol yetarlimi?"}
  D -- "yo'q" --> E["403 Forbidden"]
  D -- "ha" --> F["Route ishlaydi"]
</pre>
<p><strong>401</strong> — «siz kimligingiz noma'lum» (token yo'q yoki yaroqsiz). <strong>403</strong> — «kimligingiz ma'lum, lekin ruxsatingiz yo'q» (masalan, oddiy foydalanuvchi admin route'iga kirdi). Bu ikki kodni aralashtirmang.</p>

<h3>Faqat o'zining yozuvlari</h3>
<p>Autentifikatsiya yetarli emas: foydalanuvchi boshqa birovning yozuvini ko'rmasligi yoki o'chirmasligi kerak. Shuning uchun har yozuvda <code>owner_id</code> saqlanadi va <code>get_jwt_identity()</code> bilan solishtiriladi. Egasi boshqa bo'lsa — <code>403</code>, yozuv topilmasa — <code>404</code>.</p>

<h3>To'liq fayl</h3>
<pre><code>__CODE__</code></pre>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Birinchi so'rov tokensiz ketadi va <code>401</code> qaytaradi. Ikkinchisida login'dan olingan token bor, yozuv yaratiladi. Uchinchisi oddiy foydalanuvchi tokeni bilan <code>403</code> beradi.</p>"""

_L3_TEXT_RU = """<h3>Защищённый маршрут</h3>
<p>Чтобы защитить маршрут, добавьте к нему декоратор <code>@jwt_required()</code>. Он проверяет заголовок <code>Authorization: Bearer &lt;token&gt;</code>: если токена нет, он повреждён или просрочен, функция вообще не запускается, а сервер возвращает <code>401</code>. Внутри функции на вопрос «кто отправил запрос» отвечает <code>get_jwt_identity()</code>.</p>
<pre><code>__SNIPPET__</code></pre>

<h3>Роль: дополнительные данные в токене</h3>
<p>При входе мы записываем роль в токен через <code>additional_claims={"role": "admin"}</code>. Затем в любом маршруте <code>get_jwt()</code> возвращает весь payload в виде словаря. Поэтому роль известна без обращения к базе на каждый запрос. Помните: payload читается открыто, не записывайте в него секреты вроде пароля.</p>

<h3>Маршрут только для админа</h3>
<p>Чтобы не повторять проверку роли везде, напишем собственный декоратор. <code>@wraps</code> сохраняет имя исходной функции (это важно для Flask), а внутри работает <code>@jwt_required()</code>:</p>
<pre class="mermaid">
flowchart TD
  A["Запрос + заголовок Authorization"] --> B{"Токен верный?"}
  B -- "нет" --> C["401 Unauthorized"]
  B -- "да" --> D{"Роли достаточно?"}
  D -- "нет" --> E["403 Forbidden"]
  D -- "да" --> F["Маршрут выполняется"]
</pre>
<p><strong>401</strong> — «вы неизвестны» (токена нет или он недействителен). <strong>403</strong> — «вы известны, но прав нет» (например, обычный пользователь зашёл в админский маршрут). Не путайте эти два кода.</p>

<h3>Только свои записи</h3>
<p>Одной аутентификации мало: пользователь не должен видеть или удалять чужие записи. Поэтому у каждой записи хранится <code>owner_id</code>, и он сравнивается с <code>get_jwt_identity()</code>. Если владелец другой — <code>403</code>, если записи нет — <code>404</code>.</p>

<h3>Полный файл</h3>
<pre><code>__CODE__</code></pre>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Первый запрос уходит без токена и возвращает <code>401</code>. Во втором есть токен из входа, запись создаётся. Третий с токеном обычного пользователя вернёт <code>403</code>.</p>"""

LESSON_3 = {
    "order": 2,
    "title": "3-Himoyalangan route'lar va rollar",
    "title_ru": "3-Защищённые маршруты и роли",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, SNIPPET=_L3_SNIPPET, CODE=_APP_NO_CORS, CURL=_CURL_AUTH),
    "text_content_ru": _fill(_L3_TEXT_RU, SNIPPET=_L3_SNIPPET, CODE=_APP_NO_CORS, CURL=_CURL_AUTH),
    "code_content": _APP_NO_CORS,
    "code_content_ru": _APP_NO_CORS,
    "code_language": "python",
    "sample": {
        "title": "Namuna: himoyalangan Notes API",
        "title_ru": "Пример: защищённое Notes API",
        "description": "@jwt_required, rol claim'i, admin_required dekoratori va faqat o'z yozuvlariga ruxsat.",
        "description_ru": "@jwt_required, роль в claim, декоратор admin_required и доступ только к своим записям.",
        "sample_type": "code",
        "code_files": [{"filename": "app.py", "language": "python", "code": _APP_NO_CORS}],
    },
    "exercises": [
        {
            "title": "401 yoki 403", "title_ru": "401 или 403",
            "description": "Oddiy foydalanuvchi (to'g'ri tokenli) admin route'iga kirdi. Server qaysi kodni qaytarishi kerak?",
            "description_ru": "Обычный пользователь (с верным токеном) зашёл в админский маршрут. Какой код должен вернуть сервер?",
            "exercise_type": "multiple_choice",
            "options": ["401 Unauthorized", "403 Forbidden", "404 Not Found", "200 OK"],
            "options_ru": ["401 Unauthorized", "403 Forbidden", "404 Not Found", "200 OK"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Foydalanuvchi kimligi ma'lum, ammo ruxsati yo'q.",
            "hint_ru": "Личность пользователя известна, но прав у него нет.",
            "explanation": "401 — autentifikatsiya yo'q yoki xato. Token to'g'ri, lekin rol yetarli emas bo'lsa 403 Forbidden qaytariladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Dekorator nomi", "title_ru": "Название декоратора",
            "description": "Route'ni faqat tokeni bor foydalanuvchilarga ochadigan dekorator: @___()",
            "description_ru": "Декоратор, открывающий маршрут только пользователям с токеном: @___()",
            "exercise_type": "fill_in_blank",
            "correct_answers": "jwt_required",
            "hint": "Nomida «jwt» va «required» bor.",
            "hint_ru": "В названии есть «jwt» и «required».",
            "explanation": "@jwt_required() tokenni tekshiradi; token yo'q yoki yaroqsiz bo'lsa funksiya chaqirilmaydi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "So'rov tartibi", "title_ru": "Порядок проверки запроса",
            "description": "Himoyalangan admin route'iga so'rov kelganda tekshiruv tartibini joylashtiring.",
            "description_ru": "Расположите порядок проверки при запросе к защищённому админскому маршруту.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Authorization sarlavhasini o'qish", "Token imzosi va muddatini tekshirish", "Roldan admin ekanini tekshirish", "Route funksiyasini bajarish"],
            "drag_items_ru": ["Прочитать заголовок Authorization", "Проверить подпись и срок токена", "Проверить по роли, что это админ", "Выполнить функцию маршрута"],
            "correct_order": ["Authorization sarlavhasini o'qish", "Token imzosi va muddatini tekshirish", "Roldan admin ekanini tekshirish", "Route funksiyasini bajarish"],
            "hint": "Avval token to'g'riligi, keyin ruxsat.",
            "hint_ru": "Сначала корректность токена, потом права.",
            "explanation": "Token tekshirilmaguncha rolga ishonib bo'lmaydi. Rol tokenning ichida, shuning uchun avval imzo tekshiriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Tokenga nima yozish mumkin", "title_ru": "Что можно писать в токен",
            "description": "Qaysilarini tokenning additional_claims qismiga xavfsiz yozish mumkin? (Bir nechta javob)",
            "description_ru": "Что безопасно записывать в additional_claims токена? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": ["Foydalanuvchi roli", "Foydalanuvchi paroli", "Foydalanuvchi id'si", "Bank kartasi raqami"],
            "options_ru": ["Роль пользователя", "Пароль пользователя", "Идентификатор пользователя", "Номер банковской карты"],
            "correct_answers": "A,C", "is_multiple_select": True,
            "hint": "Payload'ni istalgan kishi o'qiy oladi.",
            "hint_ru": "Payload может прочитать кто угодно.",
            "explanation": "JWT imzolanadi, lekin shifrlanmaydi. Rol va id kabi maxfiy bo'lmagan ma'lumotlar mumkin, parol va karta raqami mutlaqo mumkin emas.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Boshqa birovning yozuvi", "title_ru": "Чужая запись",
            "description": "Nega faqat @jwt_required() yetarli emas va yozuvni o'chirishda yana nimani tekshirish kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему одного @jwt_required() недостаточно и что ещё нужно проверить при удалении записи? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Token faqat foydalanuvchi kimligini tasdiqlaydi. Yozuvning egasi (owner_id) token identity'siga teng ekanini ham tekshirish kerak, aks holda bir foydalanuvchi boshqasining yozuvini o'chira oladi; egasi boshqa bo'lsa 403 qaytariladi.",
            "hint": "Yozuvdagi owner_id ni get_jwt_identity() bilan solishtiring.",
            "hint_ru": "Сравните owner_id записи с get_jwt_identity().",
            "explanation": "Autentifikatsiya «kim?» savoliga, avtorizatsiya «unga ruxsat bormi?» savoliga javob beradi. Egalikni tekshirmasdan har bir kirgan foydalanuvchi har qanday yozuvni o'chira oladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars ───────────────────────────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>Muammo: brauzer so'rovni to'sib qo'yadi</h3>
<p>Frontend <code>http://localhost:8080</code> da, API esa <code>http://127.0.0.1:5000</code> da ishlayotgan bo'lsin. Origin (manba) — protokol, domen va portning birikmasi; bular farq qilsa, manbalar <strong>turli</strong> hisoblanadi. Brauzer xavfsizlik uchun (same-origin siyosati) boshqa manbaga yuborilgan so'rovning <em>javobini</em> JavaScript'ga bermaydi, agar server buni aniq ruxsat etmasa. Konsolda <code>blocked by CORS policy</code> xatosini ko'rasiz.</p>
<p>CORS xatosi server buzilganini bildirmaydi: so'rov serverga yetib boradi, lekin brauzer javobni yashiradi. Shuning uchun uni <strong>serverda</strong> to'g'rilaymiz, frontendda emas.</p>

<h3>Preflight (OPTIONS) so'rovi</h3>
<p>Oddiy bo'lmagan so'rovlar (masalan, <code>Authorization</code> sarlavhasi yoki JSON <code>Content-Type</code> bilan) oldidan brauzer o'zi <code>OPTIONS</code> so'rovini yuborib so'raydi: «bu manbadan, bu metod va sarlavhalar bilan kelsam bo'ladimi?»</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Brauzer (8080)
  participant S as Flask API (5000)
  B->>S: OPTIONS /api/notes (Origin, Request-Headers)
  S-->>B: 200 + Access-Control-Allow-Origin va Allow-Headers
  B->>S: GET /api/notes (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p>Server ruxsat bermasa, ikkinchi (asl) so'rov umuman yuborilmaydi.</p>

<h3>Flask-CORS</h3>
<pre><code>pip install Flask-CORS</code></pre>
<pre><code>__SNIPPET__</code></pre>
<ul>
  <li><code>origins</code> — ruxsat etilgan manbalar ro'yxati. Aniq manzillarni yozing; <code>"*"</code> (hamma) faqat ochiq, tokensiz API'lar uchun.</li>
  <li><code>allow_headers</code> — <code>Authorization</code> ni qo'shishni unutmang, aks holda tokenli so'rov preflight'dan o'tmaydi.</li>
  <li><code>resources</code> — faqat <code>/api/*</code> yo'llariga qo'llanadi.</li>
</ul>
<p>Tekshirish uchun preflight'ni qo'lda yuboring:</p>
<pre><code>__PRE__</code></pre>
<p>Javobda <code>Access-Control-Allow-Origin: http://localhost:8080</code> bo'lishi kerak. Boshqa manbadan (masalan, <code>http://evil.example</code>) bu sarlavha qaytmaydi.</p>

<h3>Frontend: fetch va token</h3>
<p>Frontend login'dan olingan tokenni <code>localStorage</code> da saqlaydi va har so'rovga <code>Authorization</code> sarlavhasi bilan qo'shadi. Agar server <code>401</code> qaytarsa, eski tokenni o'chirib, qayta kirishni so'raymiz.</p>
<pre><code>__JS__</code></pre>
<p>Ogohlantirish: <code>localStorage</code> dagi token sahifadagi har qanday skriptga ko'rinadi (XSS xavfi). O'quv loyihasi uchun yetarli, jiddiy loyihada cookie'ning <code>HttpOnly</code> rejimi ham ko'rib chiqiladi.</p>

<h3>To'liq server fayli</h3>
<pre><code>__CODE__</code></pre>"""

_L4_TEXT_RU = """<h3>Проблема: браузер блокирует запрос</h3>
<p>Пусть фронтенд работает на <code>http://localhost:8080</code>, а API — на <code>http://127.0.0.1:5000</code>. Origin (источник) — это сочетание протокола, домена и порта; если они отличаются, источники <strong>разные</strong>. В целях безопасности (политика same-origin) браузер не отдаёт JavaScript <em>ответ</em> на запрос к другому источнику, пока сервер явно этого не разрешит. В консоли вы увидите ошибку <code>blocked by CORS policy</code>.</p>
<p>Ошибка CORS не значит, что сервер сломан: запрос доходит до сервера, но браузер скрывает ответ. Поэтому исправляем её <strong>на сервере</strong>, а не во фронтенде.</p>

<h3>Preflight-запрос (OPTIONS)</h3>
<p>Перед «непростыми» запросами (например, с заголовком <code>Authorization</code> или JSON в <code>Content-Type</code>) браузер сам отправляет <code>OPTIONS</code>-запрос и спрашивает: «можно ли мне с этого источника, с этим методом и заголовками?»</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Браузер (8080)
  participant S as Flask API (5000)
  B->>S: OPTIONS /api/notes (Origin, Request-Headers)
  S-->>B: 200 + Access-Control-Allow-Origin и Allow-Headers
  B->>S: GET /api/notes (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p>Если сервер не разрешил, основной (второй) запрос вообще не отправляется.</p>

<h3>Flask-CORS</h3>
<pre><code>pip install Flask-CORS</code></pre>
<pre><code>__SNIPPET__</code></pre>
<ul>
  <li><code>origins</code> — список разрешённых источников. Указывайте конкретные адреса; <code>"*"</code> (все) подходит только для открытых API без токенов.</li>
  <li><code>allow_headers</code> — не забудьте добавить <code>Authorization</code>, иначе запрос с токеном не пройдёт preflight.</li>
  <li><code>resources</code> — действует только на пути <code>/api/*</code>.</li>
</ul>
<p>Чтобы проверить, отправьте preflight вручную:</p>
<pre><code>__PRE__</code></pre>
<p>В ответе должен быть <code>Access-Control-Allow-Origin: http://localhost:8080</code>. С другого источника (например, <code>http://evil.example</code>) этот заголовок не вернётся.</p>

<h3>Фронтенд: fetch и токен</h3>
<p>Фронтенд сохраняет токен из ответа на вход в <code>localStorage</code> и добавляет его в каждый запрос через заголовок <code>Authorization</code>. Если сервер вернул <code>401</code>, старый токен удаляем и просим войти заново.</p>
<pre><code>__JS__</code></pre>
<p>Предупреждение: токен в <code>localStorage</code> виден любому скрипту на странице (риск XSS). Для учебного проекта этого достаточно, в серьёзном проекте стоит рассмотреть и cookie с режимом <code>HttpOnly</code>.</p>

<h3>Полный файл сервера</h3>
<pre><code>__CODE__</code></pre>"""

_CORS_SNIPPET = (
    "from flask_cors import CORS\n\n"
    + _CORS_LINE
)

LESSON_4 = {
    "order": 3,
    "title": "4-CORS: frontend bilan ulash",
    "title_ru": "4-CORS: подключение фронтенда",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, SNIPPET=_CORS_SNIPPET, PRE=_PREFLIGHT_CURL, JS=_API_JS, CODE=_APP_NO_LOADERS),
    "text_content_ru": _fill(_L4_TEXT_RU, SNIPPET=_CORS_SNIPPET, PRE=_PREFLIGHT_CURL, JS=_API_JS, CODE=_APP_NO_LOADERS),
    "code_content": _APP_NO_LOADERS,
    "code_content_ru": _APP_NO_LOADERS,
    "code_language": "python",
    "sample": {
        "title": "Namuna: CORS va fetch bilan tokenli so'rov",
        "title_ru": "Пример: CORS и запрос с токеном через fetch",
        "description": "Flask-CORS sozlamasi va frontend tomonidagi login/loadNotes funksiyalari.",
        "description_ru": "Настройка Flask-CORS и функции login/loadNotes на стороне фронтенда.",
        "sample_type": "code",
        "code_files": [
            {"filename": "app.py", "language": "python", "code": _APP_NO_LOADERS},
            {"filename": "api.js", "language": "javascript", "code": _API_JS},
        ],
    },
    "exercises": [
        {
            "title": "Origin nima", "title_ru": "Что такое origin",
            "description": "Qaysi ikki manzil bir xil origin (manba) hisoblanadi?",
            "description_ru": "Какие два адреса считаются одним origin (источником)?",
            "exercise_type": "multiple_choice",
            "options": [
                "http://localhost:8080 va http://localhost:5000",
                "http://localhost:8080 va https://localhost:8080",
                "http://localhost:8080/a va http://localhost:8080/b",
                "http://localhost:8080 va http://127.0.0.1:8080",
            ],
            "options_ru": [
                "http://localhost:8080 и http://localhost:5000",
                "http://localhost:8080 и https://localhost:8080",
                "http://localhost:8080/a и http://localhost:8080/b",
                "http://localhost:8080 и http://127.0.0.1:8080",
            ],
            "correct_answers": "C", "is_multiple_select": False,
            "hint": "Origin = protokol + domen + port; yo'l (path) hisobga olinmaydi.",
            "hint_ru": "Origin = протокол + домен + порт; путь (path) не учитывается.",
            "explanation": "Faqat yo'l farq qilsa origin bir xil. Port, protokol yoki domen (hatto localhost va 127.0.0.1) farq qilsa — turli origin.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Preflight metodi", "title_ru": "Метод preflight",
            "description": "Brauzer preflight uchun qaysi HTTP metodini yuboradi? ___",
            "description_ru": "Какой HTTP-метод браузер отправляет для preflight? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "OPTIONS",
            "hint": "U serverdan «nimalarga ruxsat bor?» deb so'raydi.",
            "hint_ru": "Он спрашивает сервер: «что разрешено?».",
            "explanation": "Preflight — OPTIONS so'rovi. Server Access-Control-Allow-* sarlavhalari bilan javob beradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Preflight tartibi", "title_ru": "Порядок при preflight",
            "description": "Tokenli so'rov yuborilganda brauzer va server o'rtasidagi tartibni joylashtiring.",
            "description_ru": "Расположите порядок обмена браузера и сервера при запросе с токеном.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Brauzer OPTIONS yuboradi", "Server Allow-Origin va Allow-Headers qaytaradi", "Brauzer asl GET so'rovini yuboradi", "JavaScript javobni oladi"],
            "drag_items_ru": ["Браузер отправляет OPTIONS", "Сервер возвращает Allow-Origin и Allow-Headers", "Браузер отправляет основной GET-запрос", "JavaScript получает ответ"],
            "correct_order": ["Brauzer OPTIONS yuboradi", "Server Allow-Origin va Allow-Headers qaytaradi", "Brauzer asl GET so'rovini yuboradi", "JavaScript javobni oladi"],
            "hint": "Asl so'rov faqat ruxsat olingandan keyin ketadi.",
            "hint_ru": "Основной запрос уходит только после получения разрешения.",
            "explanation": "Brauzer avval ruxsat so'raydi (OPTIONS). Ruxsat bo'lsa asl so'rov yuboriladi, aks holda to'xtatiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi sozlamalar kerak", "title_ru": "Какие настройки нужны",
            "description": "Frontend Authorization sarlavhasi bilan so'rov yuborishi uchun Flask-CORS'da nima bo'lishi kerak? (Bir nechta javob)",
            "description_ru": "Что должно быть в Flask-CORS, чтобы фронтенд мог отправлять запрос с заголовком Authorization? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "origins ro'yxatida frontend manzili",
                "allow_headers ichida Authorization",
                "Frontend kodida CORS xatosini try/catch bilan o'rash",
                "Tokenni URL'ga qo'shish",
            ],
            "options_ru": [
                "Адрес фронтенда в списке origins",
                "Authorization в allow_headers",
                "Обернуть ошибку CORS во фронтенде в try/catch",
                "Добавить токен в URL",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Ikkalasi ham serverda sozlanadi.",
            "hint_ru": "Обе настройки делаются на сервере.",
            "explanation": "Server frontend origin'ini ham, Authorization sarlavhasini ham aniq ruxsat etishi kerak. try/catch CORS blokini olib tashlamaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega * xavfli", "title_ru": "Чем опасен *",
            "description": "Nega tokenli API uchun origins ichiga \"*\" yozish tavsiya etilmaydi? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему для API с токенами не рекомендуется указывать \"*\" в origins? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "\"*\" har qanday saytga API'ga brauzerdan murojaat qilishga ruxsat beradi. Tokenli API uchun faqat ishonchli frontend manzillarini aniq ro'yxatda berish kerak, shunda begona saytlar so'rov yubora olmaydi.",
            "hint": "Ruxsat etilgan manbalar ro'yxatini kim nazorat qilishi kerak?",
            "hint_ru": "Кто должен контролировать список разрешённых источников?",
            "explanation": "CORS — ruxsat ro'yxati. \"*\" bilan ro'yxat yo'qoladi va har qanday sayt API javobini o'qiy oladi. Aniq manzillar xavfni kamaytiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars ───────────────────────────────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Nega xatolar ham JSON bo'lishi kerak</h3>
<p>Frontend javobni <code>res.json()</code> bilan o'qiydi. Flask-JWT-Extended standart xatolarni qaytarganda format sizning API'ngizdan farq qilishi mumkin, frontend esa «token yo'q», «token buzilgan» va «token muddati o'tgan» holatlarini ajrata olmaydi. Muddati o'tgan tokenda foydalanuvchini login sahifasiga yo'naltirish kerak, buzilgan tokenda esa ham shunday, lekin boshqa xabar bilan. Buning uchun har holatga o'z <code>code</code> maydonini beramiz.</p>

<h3>Xato ishlovchilar (loader'lar)</h3>
<pre><code>__LOADERS__</code></pre>
<ul>
  <li><code>unauthorized_loader</code> — Authorization sarlavhasi umuman yo'q.</li>
  <li><code>invalid_token_loader</code> — token buzilgan yoki imzosi noto'g'ri.</li>
  <li><code>expired_token_loader</code> — muddati tugagan (bu funksiya ikkita argument oladi).</li>
</ul>
<p>Hammasi bir xil <code>{"error", "code"}</code> shaklida va <code>401</code> bilan qaytadi.</p>

<h3>Flask test client</h3>
<p>Serverni ishga tushirmasdan ham API'ni tekshirish mumkin: <code>app.test_client()</code> so'rovlarni to'g'ridan-to'g'ri ilovaga yuboradi. <code>pytest</code> bilan tekshiruvlarni yozamiz:</p>
<pre><code>__TEST__</code></pre>
<p>Muddati o'tgan tokenni olish uchun <code>app_context()</code> ichida <code>create_access_token(..., expires_delta=timedelta(seconds=-1))</code> chaqiramiz: token yaratilishi bilan eskirgan bo'ladi. To'liq test fayli quyida; ishga tushirish: <code>pip install pytest</code>, so'ng <code>pytest</code>.</p>
<pre><code>__ALL_TESTS__</code></pre>

<h3>Postman</h3>
<ol>
  <li><strong>POST</strong> <code>/api/login</code> so'rovini yuboring (Body → raw → JSON).</li>
  <li>Javobdagi tokenni avtomatik saqlash uchun so'rovning <em>Tests</em> yorlig'iga quyidagini yozing:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>Himoyalangan so'rovda <em>Authorization</em> yorlig'i → Type: <em>Bearer Token</em> → qiymat: <code>{{token}}</code>.</li>
</ol>
<p>Shunda tokenni qo'lda nusxalash shart emas va token yangilanganda barcha so'rovlar o'zi yangilanadi.</p>"""

_L5_TEXT_RU = """<h3>Почему ошибки тоже должны быть JSON</h3>
<p>Фронтенд читает ответ через <code>res.json()</code>. Стандартные ошибки Flask-JWT-Extended могут отличаться по формату от вашего API, и фронтенд не сможет различить «токена нет», «токен испорчен» и «срок токена истёк». При просроченном токене пользователя нужно отправить на страницу входа; при испорченном — тоже, но с другим сообщением. Для этого даём каждому случаю собственное поле <code>code</code>.</p>

<h3>Обработчики ошибок (loader'ы)</h3>
<pre><code>__LOADERS__</code></pre>
<ul>
  <li><code>unauthorized_loader</code> — заголовка Authorization нет вообще.</li>
  <li><code>invalid_token_loader</code> — токен повреждён или подпись неверна.</li>
  <li><code>expired_token_loader</code> — срок действия истёк (эта функция принимает два аргумента).</li>
</ul>
<p>Все возвращаются в одном формате <code>{"error", "code"}</code> с кодом <code>401</code>.</p>

<h3>Flask test client</h3>
<p>API можно проверять и без запуска сервера: <code>app.test_client()</code> отправляет запросы прямо в приложение. Пишем проверки с помощью <code>pytest</code>:</p>
<pre><code>__TEST__</code></pre>
<p>Чтобы получить просроченный токен, вызываем внутри <code>app_context()</code> функцию <code>create_access_token(..., expires_delta=timedelta(seconds=-1))</code>: токен устаревает сразу при создании. Полный файл тестов ниже; запуск: <code>pip install pytest</code>, затем <code>pytest</code>.</p>
<pre><code>__ALL_TESTS__</code></pre>

<h3>Postman</h3>
<ol>
  <li>Отправьте <strong>POST</strong>-запрос на <code>/api/login</code> (Body → raw → JSON).</li>
  <li>Чтобы сохранять токен из ответа автоматически, на вкладке <em>Tests</em> запроса напишите:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>В защищённом запросе откройте вкладку <em>Authorization</em> → Type: <em>Bearer Token</em> → значение: <code>{{token}}</code>.</li>
</ol>
<p>Так токен не нужно копировать вручную, а при его обновлении все запросы подхватят новое значение.</p>"""

LESSON_5 = {
    "order": 4,
    "title": "5-API xatolari, test client va Postman",
    "title_ru": "5-Ошибки API, test client и Postman",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, LOADERS=_L5_SNIPPET, TEST=_L5_TEST_SNIPPET, ALL_TESTS=_TEST_APP, POSTMAN=_POSTMAN_SCRIPT),
    "text_content_ru": _fill(_L5_TEXT_RU, LOADERS=_L5_SNIPPET, TEST=_L5_TEST_SNIPPET, ALL_TESTS=_TEST_APP, POSTMAN=_POSTMAN_SCRIPT),
    "code_content": _L5_SNIPPET,
    "code_content_ru": _L5_SNIPPET,
    "code_language": "python",
    "sample": {
        "title": "Namuna: JSON xatolari va testlar",
        "title_ru": "Пример: JSON-ошибки и тесты",
        "description": "To'liq Notes API va unga yozilgan 7 ta pytest testi (Flask test client).",
        "description_ru": "Полное Notes API и 7 тестов pytest (Flask test client).",
        "sample_type": "code",
        "code_files": [
            {"filename": "app.py", "language": "python", "code": _APP_FULL},
            {"filename": "test_app.py", "language": "python", "code": _TEST_APP},
        ],
    },
    "exercises": [
        {
            "title": "Qaysi loader", "title_ru": "Какой loader",
            "description": "Token muddati tugagan bo'lsa, qaysi dekorator bilan belgilangan funksiya chaqiriladi?",
            "description_ru": "Какой декоратор отмечает функцию, вызываемую при истёкшем сроке токена?",
            "exercise_type": "multiple_choice",
            "options": ["@jwt.unauthorized_loader", "@jwt.invalid_token_loader", "@jwt.expired_token_loader", "@jwt_required()"],
            "options_ru": ["@jwt.unauthorized_loader", "@jwt.invalid_token_loader", "@jwt.expired_token_loader", "@jwt_required()"],
            "correct_answers": "C", "is_multiple_select": False,
            "hint": "Nomida «expired» bor.",
            "hint_ru": "В названии есть «expired».",
            "explanation": "expired_token_loader muddati o'tgan token uchun. unauthorized_loader — sarlavha yo'q, invalid_token_loader — token buzilgan.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Test client", "title_ru": "Тестовый клиент",
            "description": "Flask ilovasini serverni ishga tushirmasdan tekshiradigan obyekt: app.___()",
            "description_ru": "Объект, который проверяет приложение Flask без запуска сервера: app.___()",
            "exercise_type": "fill_in_blank",
            "correct_answers": "test_client",
            "hint": "Nomi «test» va «client» so'zlaridan iborat.",
            "hint_ru": "Название состоит из слов «test» и «client».",
            "explanation": "app.test_client() so'rovlarni to'g'ridan-to'g'ri ilovaga yuboradi, tarmoq va port kerak emas.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Postman tartibi", "title_ru": "Порядок в Postman",
            "description": "Postman'da tokenli so'rov yuborish tartibini joylashtiring.",
            "description_ru": "Расположите шаги отправки запроса с токеном в Postman.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["/api/login so'rovini yuborish", "Tests skripti tokenni o'zgaruvchiga yozadi", "Authorization → Bearer Token: {{token}}", "Himoyalangan so'rovni yuborish"],
            "drag_items_ru": ["Отправить запрос /api/login", "Скрипт Tests записывает токен в переменную", "Authorization → Bearer Token: {{token}}", "Отправить защищённый запрос"],
            "correct_order": ["/api/login so'rovini yuborish", "Tests skripti tokenni o'zgaruvchiga yozadi", "Authorization → Bearer Token: {{token}}", "Himoyalangan so'rovni yuborish"],
            "hint": "Token avval olinadi, keyin ishlatiladi.",
            "hint_ru": "Сначала токен получают, потом используют.",
            "explanation": "Login javobidagi token o'zgaruvchiga saqlanadi va keyingi so'rovlarda {{token}} orqali ishlatiladi.",
            "difficulty_level": "Easy", "points": 4,
        },
        {
            "title": "Eskirgan token testi", "title_ru": "Тест просроченного токена",
            "description": "Testda muddati o'tgan token olish uchun qaysi yo'l to'g'ri?",
            "description_ru": "Как правильно получить просроченный токен в тесте?",
            "exercise_type": "multiple_choice",
            "options": [
                "30 daqiqa kutib turish",
                "create_access_token'ga manfiy expires_delta berish",
                "Tokenning oxirgi harfini o'chirib tashlash",
                "Serverni qayta ishga tushirish",
            ],
            "options_ru": [
                "Ждать 30 минут",
                "Передать в create_access_token отрицательный expires_delta",
                "Удалить последнюю букву токена",
                "Перезапустить сервер",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Test tez ishlashi kerak, kutish yaramaydi.",
            "hint_ru": "Тест должен быть быстрым, ждать нельзя.",
            "explanation": "Manfiy expires_delta token yaratilishi bilan eskirgan bo'lishini ta'minlaydi. Oxirgi harfni o'chirish esa «invalid» holatini beradi, «expired»ni emas.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega code maydoni", "title_ru": "Зачем поле code",
            "description": "Xato javoblarida error bilan birga code maydoni (token_expired, token_invalid) nima uchun kerak? O'z so'zingiz bilan yozing.",
            "description_ru": "Зачем в ответах с ошибкой рядом с error нужно поле code (token_expired, token_invalid)? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Matnli xabar o'zgarishi yoki tarjima qilinishi mumkin, code esa barqaror. Frontend code bo'yicha holatni aniq ajratadi (muddati tugagan, yaroqsiz, token yo'q) va har biriga to'g'ri harakat qiladi, masalan login sahifasiga yo'naltiradi.",
            "hint": "Frontend matnni emas, qanday qiymatni tekshirishi qulayroq?",
            "hint_ru": "Что удобнее проверять во фронтенде: текст или стабильное значение?",
            "explanation": "Mashina o'qiydigan kod xabar matni o'zgarganda ham buzilmaydi. Shuning uchun xatolarda error (odam uchun) va code (dastur uchun) birga beriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>Token</strong> (JWT): sessiyasiz, imzolangan, muddatli; <code>Authorization: Bearer</code> bilan yuboriladi.</li>
  <li><strong>Register / login:</strong> parol xeshi, <code>create_access_token</code>, bir xil xato xabari.</li>
  <li><strong>Himoya:</strong> <code>@jwt_required()</code>, rol <code>additional_claims</code> da, 401 va 403 farqi, faqat o'z yozuvi.</li>
  <li><strong>CORS:</strong> preflight, <code>origins</code>, <code>allow_headers</code>, frontenddan <code>fetch</code>.</li>
  <li><strong>Xatolar va testlar:</strong> JSON xatolar <code>code</code> bilan, <code>test_client</code>, Postman.</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Pastda butun loyiha: server (<code>app.py</code>), testlar (<code>test_app.py</code>) va oddiy frontend (<code>index.html</code> + <code>api.js</code>). Frontendni ishga tushirish uchun <code>python -m http.server 8080</code> buyrug'ini frontend papkasida bajaring: shunda manzil CORS'da ruxsat etilgan <code>http://localhost:8080</code> bilan mos keladi.</p>
<pre><code>__CODE__</code></pre>
<h3>Frontend</h3>
<pre><code>__HTML__</code></pre>
<p>Keyingi bosqich — vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, o'z mavzuingizdagi yozuvlar (masalan, vazifalar yoki xarajatlar) uchun shu usulda token bilan himoyalangan API yozing.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>Токен</strong> (JWT): без сессии, подписан, с ограниченным сроком; передаётся через <code>Authorization: Bearer</code>.</li>
  <li><strong>Регистрация и вход:</strong> хеш пароля, <code>create_access_token</code>, одинаковое сообщение об ошибке.</li>
  <li><strong>Защита:</strong> <code>@jwt_required()</code>, роль в <code>additional_claims</code>, разница 401 и 403, доступ только к своим записям.</li>
  <li><strong>CORS:</strong> preflight, <code>origins</code>, <code>allow_headers</code>, <code>fetch</code> из фронтенда.</li>
  <li><strong>Ошибки и тесты:</strong> JSON-ошибки с <code>code</code>, <code>test_client</code>, Postman.</li>
</ul>

<h3>Готовое решение</h3>
<p>Ниже весь проект: сервер (<code>app.py</code>), тесты (<code>test_app.py</code>) и простой фронтенд (<code>index.html</code> + <code>api.js</code>). Чтобы запустить фронтенд, выполните в его папке <code>python -m http.server 8080</code>: тогда адрес совпадёт с разрешённым в CORS <code>http://localhost:8080</code>.</p>
<pre><code>__CODE__</code></pre>
<h3>Фронтенд</h3>
<pre><code>__HTML__</code></pre>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, напишите защищённый токеном API для записей на свою тему (например, задачи или расходы) тем же способом.</p>"""

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: tokenli Notes API + oddiy frontend",
    "title_ru": "6-Повторение: Notes API с токеном + простой фронтенд",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, CODE=_APP_FULL, HTML=_INDEX_HTML),
    "text_content_ru": _fill(_L6_TEXT_RU, CODE=_APP_FULL, HTML=_INDEX_HTML),
    "code_content": _APP_FULL,
    "code_content_ru": _APP_FULL,
    "code_language": "python",
    "sample": {
        "title": "Namuna: tokenli Notes API (to'liq loyiha)",
        "title_ru": "Пример: Notes API с токеном (полный проект)",
        "description": "Server, 7 ta test va fetch bilan ishlaydigan oddiy frontend.",
        "description_ru": "Сервер, 7 тестов и простой фронтенд на fetch.",
        "sample_type": "code",
        "code_files": [
            {"filename": "app.py", "language": "python", "code": _APP_FULL},
            {"filename": "test_app.py", "language": "python", "code": _TEST_APP},
            {"filename": "api.js", "language": "javascript", "code": _API_JS},
            {"filename": "index.html", "language": "html", "code": _INDEX_HTML},
        ],
    },
    "task": {
        "task_title": "Loyiha: tokenli yozuvlar API'si + oddiy frontend",
        "task_title_ru": "Проект: API записей с токеном + простой фронтенд",
        "task_description": "O'zingiz tanlagan mavzu (vazifalar, xarajatlar, kitoblar...) uchun Flask API yozing: foydalanuvchi ro'yxatdan o'tadi, kiradi va faqat o'z yozuvlarini boshqaradi. Admin hammasini ko'radi. Oddiy HTML/JavaScript frontend login qiladi va yozuvlar ro'yxatini ko'rsatadi.",
        "task_description_ru": "Напишите API на Flask для выбранной вами темы (задачи, расходы, книги...): пользователь регистрируется, входит и управляет только своими записями. Админ видит всё. Простой HTML/JavaScript-фронтенд выполняет вход и показывает список записей.",
        "task_requirements": (
            "1) POST /api/register va POST /api/login: parol xesh ko'rinishida saqlanadi, login token qaytaradi. "
            "2) @jwt_required() bilan himoyalangan route'lar (yozuv yaratish, ro'yxat, o'chirish): foydalanuvchi faqat o'z yozuvlarini ko'radi va o'chiradi (boshqasiniki uchun 403). "
            "3) Rol claim'i va admin_required: faqat admin foydalanuvchilar ro'yxatini ko'radi. "
            "4) CORS: faqat frontend manzili ruxsat etilgan, Authorization sarlavhasi bilan. "
            "5) fetch bilan oddiy frontend: login va yozuvlar ro'yxati, token localStorage'da. "
            "6) Flask test client bilan kamida 3 ta test."
        ),
        "task_requirements_ru": (
            "1) POST /api/register и POST /api/login: пароль хранится в виде хеша, вход возвращает токен. "
            "2) Маршруты под защитой @jwt_required() (создание, список, удаление записей): пользователь видит и удаляет только свои записи (чужие — 403). "
            "3) Роль в claim и admin_required: список пользователей видит только админ. "
            "4) CORS: разрешён только адрес фронтенда, с заголовком Authorization. "
            "5) Простой фронтенд на fetch: вход и список записей, токен в localStorage. "
            "6) Не менее 3 тестов через Flask test client."
        ),
        "task_technologies": "Flask, Flask-JWT-Extended, Flask-CORS, JavaScript",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Hammasini bog'lang", "title_ru": "Соедините всё вместе",
            "description": "Qaysi variant «token bilan ishlovchi to'liq API»ning to'g'ri tartibini ko'rsatadi?",
            "description_ru": "Какой вариант показывает верный порядок работы API с токеном?",
            "exercise_type": "multiple_choice",
            "options": [
                "login → token → Authorization: Bearer bilan himoyalangan so'rov",
                "himoyalangan so'rov → login → token",
                "token → login → parol",
                "parolni har so'rovda URL ichida yuborish",
            ],
            "options_ru": [
                "вход → токен → защищённый запрос с Authorization: Bearer",
                "защищённый запрос → вход → токен",
                "токен → вход → пароль",
                "отправлять пароль в URL при каждом запросе",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Token faqat login'dan keyin paydo bo'ladi.",
            "hint_ru": "Токен появляется только после входа.",
            "explanation": "Parol faqat login paytida yuboriladi, keyin barcha so'rovlar token bilan ketadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "CORS sarlavhasi", "title_ru": "Заголовок CORS",
            "description": "Server preflight javobida qaysi sarlavha frontend manzilini ruxsat etadi? Access-Control-___-Origin",
            "description_ru": "Какой заголовок в ответе на preflight разрешает адрес фронтенда? Access-Control-___-Origin",
            "exercise_type": "fill_in_blank",
            "correct_answers": "Allow",
            "hint": "«Ruxsat berish» inglizcha qanday?",
            "hint_ru": "Как по-английски «разрешить»?",
            "explanation": "Access-Control-Allow-Origin brauzerga javobni shu manbaga berish mumkinligini bildiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Loyihani tekshirish", "title_ru": "Проверка проекта",
            "description": "Loyihangiz xavfsiz ekanini qaysi tekshiruvlar bilan isbotlaysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Какими проверками вы докажете, что ваш проект безопасен? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Tokensiz so'rov 401 qaytarishini, boshqa foydalanuvchining yozuvi uchun 403 kelishini, oddiy foydalanuvchi admin route'iga kira olmasligini va CORS faqat frontend manziliga ruxsat berishini test client bilan tekshiraman.",
            "hint": "401, 403 va CORS holatlarini o'ylab ko'ring.",
            "hint_ru": "Подумайте о случаях 401, 403 и CORS.",
            "explanation": "Testlar himoyaning har qatlamini tekshiradi: token, egalik, rol va CORS. Shu to'rt holat bo'lsa, loyiha asosiy xavfsizlik talablarini qoplaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
