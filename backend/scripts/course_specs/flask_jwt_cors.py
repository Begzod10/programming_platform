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
    "max_points": 110,
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

LESSONS = [LESSON_1]
