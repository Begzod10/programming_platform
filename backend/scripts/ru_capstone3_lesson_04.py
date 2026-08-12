"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=3 (L4)."""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

LESSON_ID = 764

TITLE_RU = "4-Аутентификация"

TEXT_RU = """\
<h2>Этап 4: Аутентификация — пароль через werkzeug.security, API через токен</h2>

<pre class="mermaid">
flowchart LR
    REGISTER["POST /api/register"] --> HASH["generate_password_hash() - пароль хешируется"]
    HASH --> LOGIN["POST /api/login"]
    LOGIN --> CHECK["check_password_hash() - сравнивается"]
    CHECK --> TOKEN["создаётся и возвращается токен"]
    TOKEN --> JS["Vanilla JS сохраняет токен и добавляет к каждому запросу"]
</pre>

<p>На курсе Flask О'rta daraja вы видели хеширование пароля через <code>werkzeug.security</code>. На этом этапе применим это в системе регистрации/входа MoneyLog, и построим hand-rolled token-аутентификацию для vanilla JS frontend (как во 2-м capstone-курсе).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — регистрация: ПРАВИЛЬНОЕ хеширование пароля</h4>
<pre><code># app/routes.py
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

@api.route('/register', methods=['POST'])
def register():
    ma_lumot = request.get_json()
    parol_hash = generate_password_hash(ma_lumot["parol"])   # ❗ пароль НИКОГДА не хранится в открытом виде!

    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"], parol_hash=parol_hash,
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201</code></pre>

<h4>БЛОК 2 — вход: проверка пароля и создание токена</h4>
<pre><code>@api.route('/login', methods=['POST'])
def login():
    ma_lumot = request.get_json()
    user = User.query.filter_by(email=ma_lumot["email"]).first()

    if user is None or not check_password_hash(user.parol_hash, ma_lumot["parol"]):
        return jsonify({"xato": "Email yoki parol noto'g'ri"}), 401

    user.token = secrets.token_hex(20)   # ❗ предполагаем, что в модели User есть столбец 'token'
    db.session.commit()
    return jsonify({"token": user.token, "ism": user.ism})</code></pre>

<h4>БЛОК 3 — декоратор для защищённого эндпоинта</h4>
<pre><code># app/auth_utils.py
from functools import wraps
from flask import request, jsonify
from app.models import User

def token_talab_qilish(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return jsonify({"xato": "Token yo'q"}), 401

        token = auth_header.split(' ')[1]
        user = User.query.filter_by(token=token).first()
        if user is None:
            return jsonify({"xato": "Token yaroqsiz"}), 401

        request.joriy_user = user   # ❗ передаёт пользователя следующему route
        return f(*args, **kwargs)
    return wrapper

# app/routes.py
@api.route('/expenses', methods=['GET'])
@token_talab_qilish
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=request.joriy_user.id).all()
    return jsonify([x.to_dict() for x in xarajatlar])</code></pre>

<h3>🐛 Намеренная ошибка — забыли хешировать пароль</h3>
<pre><code>@api.route('/register', methods=['POST'])
def register_xato():
    ma_lumot = request.get_json()
    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"],
        parol_hash=ma_lumot["parol"],   # ❌ generate_password_hash() НЕ ИСПОЛЬЗОВАН - открытый пароль!
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201

# В базе данных:
# столбец parol_hash хранит "mening_parolim123" как ОТКРЫТЫЙ ТЕКСТ!
# ❌ Если база станет доступной, реальные пароли ВСЕХ пользователей
#    сразу же будут видны</code></pre>

<p><strong>Результат:</strong> если пароль хранится <strong>без хеширования</strong> напрямую, и база данных (или её резервная копия) станет доступной <strong>по любой причине</strong> &mdash; взлом, неверно настроенные права доступа, или даже через сотрудника изнутри &mdash; реальные пароли <strong>всех</strong> пользователей будут <strong>немедленно</strong> раскрыты. Кроме того, многие пользователи используют <strong>один и тот же</strong> пароль на других сайтах &mdash; это создаёт риск и для других сервисов. <code>generate_password_hash()</code> преобразует пароль в <strong>необратимую</strong> форму, поэтому даже если база станет доступной, восстановить реальный пароль невозможно.</p>

<h3>Теперь объясним</h3>

<h4>1. Как работают <code>generate_password_hash()</code> и <code>check_password_hash()</code>?</h4>
<p><code>generate_password_hash(parol)</code> превращает пароль в <strong>одностороннюю</strong> (необратимую) хеш-функцию. При входе <code>check_password_hash(saqlangan_hash, kiritilgan_parol)</code> заново хеширует введённый пароль <strong>тем же алгоритмом</strong> и сравнивает с сохранённым хешем &mdash; это позволяет проверить правильность, не "восстанавливая" исходный пароль.</p>

<h4>2. Почему токен хранится в самой модели <code>User</code> (не в отдельной таблице Token)?</h4>
<p>Это &mdash; упрощённый подход: предполагается, что у каждого пользователя <strong>один</strong> активный токен (при новом входе старый заменяется). В курсе Django capstone использовалась отдельная таблица <code>Token</code> &mdash; это тоже правильно, здесь же показан более простой вариант.</p>

<h4>3. Как работает декоратор (<code>token_talab_qilish</code>)?</h4>
<p>Это &mdash; версия для Flask декоратора <code>@token_talab_qilish</code> из курса Django capstone: проверяет заголовок <code>Authorization</code>, находит пользователя по токену, и присоединив его к <code>request.joriy_user</code>, передаёт управление исходной route-функции.</p>

<h4>4. Почему отсутствие хеширования пароля <strong>особенно</strong> опасно?</h4>
<p>Пароль &mdash; секретные данные, выбранные <strong>самим</strong> пользователем, часто используемые и на других сервисах. В отличие от данных вроде email или имени, раскрытие пароля создаёт риск и для <strong>других</strong> аккаунтов пользователя (если он повторно использовал тот же пароль).</p>

<h4>5. Почему эта ошибка не проявляется сразу?</h4>
<p>Регистрация и вход <strong>функционально</strong> работают правильно &mdash; пользователь регистрируется, затем может войти, всё выглядит "рабочим". Проблема становится известна только <strong>позже</strong>, когда база данных станет доступной (или во время аудита безопасности) &mdash; это делает её особенно опасной, так как никто не замечает её сразу.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>generate_password_hash()</code>/<code>check_password_hash()</code> — безопасное хранение и проверка пароля</li>
<li>✅ Пароль <strong>никогда</strong> не должен храниться в открытом виде</li>
<li>✅ Hand-rolled token-аутентификация — подходящее решение для vanilla JS frontend</li>
<li>✅ Декоратор позволяет писать защищённые routes организованно и переиспользуемо</li>
<li>✅ Ошибка отсутствия хеширования пароля проявляется не сразу, а только когда база станет доступной — это делает её серьёзно опасной</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 4: Аутентификация - werkzeug.security и токен
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/routes.py - регистрация (с хешированием пароля)
# ─────────────────────────────────────────────────────────────────────

from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask import request, jsonify
from app import db
from app.models import User


@api.route('/register', methods=['POST'])
def register():
    ma_lumot = request.get_json()
    parol_hash = generate_password_hash(ma_lumot["parol"])

    yangi_user = User(
        ism=ma_lumot["ism"], email=ma_lumot["email"], parol_hash=parol_hash,
    )
    db.session.add(yangi_user)
    db.session.commit()
    return jsonify({"xabar": "Ro'yxatdan o'tish muvaffaqiyatli"}), 201

# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - вход (проверка пароля, создание токена)
# ─────────────────────────────────────────────────────────────────────


@api.route('/login', methods=['POST'])
def login():
    ma_lumot = request.get_json()
    user = User.query.filter_by(email=ma_lumot["email"]).first()

    if user is None or not check_password_hash(user.parol_hash, ma_lumot["parol"]):
        return jsonify({"xato": "Email yoki parol noto'g'ri"}), 401

    user.token = secrets.token_hex(20)
    db.session.commit()
    return jsonify({"token": user.token, "ism": user.ism})

# ─────────────────────────────────────────────────────────────────────
# 3) app/auth_utils.py - декоратор защищённого эндпоинта
# ─────────────────────────────────────────────────────────────────────

from functools import wraps


def token_talab_qilish(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return jsonify({"xato": "Token yo'q"}), 401

        token = auth_header.split(' ')[1]
        user = User.query.filter_by(token=token).first()
        if user is None:
            return jsonify({"xato": "Token yaroqsiz"}), 401

        request.joriy_user = user
        return f(*args, **kwargs)
    return wrapper

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли хешировать пароль (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @api.route('/register', methods=['POST'])
# def register_xato():
#     ma_lumot = request.get_json()
#     yangi_user = User(
#         ism=ma_lumot["ism"], email=ma_lumot["email"],
#         parol_hash=ma_lumot["parol"],   # generate_password_hash() НЕ ИСПОЛЬЗОВАН!
#     )
#     db.session.add(yangi_user)
#     db.session.commit()
# ❌ Если база доступна, все пароли видны в ОТКРЫТОМ виде!
"""

EX = {
    4424: {
        "title": "Как работают generate_password_hash() и check_password_hash()?",
        "description": "Что делает check_password_hash() в процессе входа?",
        "hint": "Хеш нельзя \"развернуть обратно\" - как тогда происходит сравнение?",
        "explanation": "check_password_hash() заново хеширует введённый пароль тем же алгоритмом и сравнивает с сохранённым хешем — это позволяет проверить правильность, не \"восстанавливая\" исходный пароль.",
    },
    4425: {
        "title": "Почему отсутствие хеширования пароля особенно опасно?",
        "description": "Почему хранение пароля без хеширования считается более опасным, чем раскрытие других данных (например имени или email)?",
        "hint": "Люди часто повторно используют один и тот же пароль.",
        "explanation": "Так как пароль — секретные данные, которые пользователь использует и на других сервисах, его раскрытие создаёт риск не только для этой системы, но и для других аккаунтов пользователя.",
    },
    4426: {
        "title": "Расположите процесс регистрации и входа",
        "description": "Расположите полный процесс, происходящий при регистрации пользователя, а затем входе.",
        "hint": "",
        "explanation": "",
    },
    4427: {
        "title": "Функция для хеширования пароля",
        "description": "Напишите название функции в модуле werkzeug.security, используемой для хеширования пароля.",
        "hint": "",
        "expected_answer": "generate_password_hash",
    },
    4428: {
        "title": "Почему отсутствие хеширования пароля не проявляется сразу?",
        "description": (
            "Если в register_xato() пароль сохраняется напрямую без "
            "хеширования, регистрация и вход всё равно \"работают "
            "правильно\". Почему эта ошибка не проявляется сразу, и "
            "когда она на самом деле приводит к серьёзным последствиям? "
            "Объясните своими словами."
        ),
        "hint": "",
        "expected_answer": "Даже если пароль сохраняется без хеширования, регистрация и вход функционально работают правильно, так как код просто напрямую сравнивает введённый пароль с сохранённым (открытым) паролем — внешне это выглядит безошибочно. Проблема появляется только тогда, когда сама база данных (или её резервная копия) по какой-то причине (взлом, неверно настроенные права доступа) станет доступной — в этот момент реальные, открытые пароли всех пользователей сразу же становятся видны. Этот риск никогда не проявляется при обычном использовании, а реализуется только при нарушении безопасности — поэтому крайне важно устранить его заранее, в качестве меры предосторожности.",
    },
}


async def _run():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        ex_rows = (
            await db.execute(select(Exercise).where(Exercise.id.in_(EX.keys())))
        ).scalars().all()

        section_map = {"Текст": "Текст", "Код": "Код", "Упражнения": "Упражнения"}
        section_map[lesson.text_content] = TEXT_RU
        section_map[lesson.code_content] = CODE_RU
        TASK_TITLE_RU = "MoneyLog — аутентификация (хеш пароля + токен)"
        TASK_DESCRIPTION_RU = (
            "Создайте эндпоинты POST /api/register и POST /api/login. "
            "Хешируйте и проверяйте пароль через werkzeug.security. Напишите "
            "декоратор token_talab_qilish и примените его к эндпоинтам "
            "expenses. Реализуйте формы входа/регистрации на frontend."
        )
        TASK_REQUIREMENTS_RU = (
            "• POST /api/register — сохраняет пароль через generate_password_hash() (НЕ открытым текстом)\n"
            "• POST /api/login — проверяет через check_password_hash(), возвращает токен\n"
            "• Декоратор token_talab_qilish — проверяет заголовок Authorization\n"
            "• GET/POST /api/expenses — возвращает/создаёт только данные, относящиеся к request.joriy_user\n"
            "• Frontend: формы входа/регистрации, токен сохраняется в localStorage и добавляется к каждому запросу\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Flask, werkzeug.security, модуль secrets, Vanilla JS"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
