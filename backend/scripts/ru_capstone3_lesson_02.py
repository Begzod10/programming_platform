"""Russian translation for Capstone 3: Flask + JavaScript + Telegram Bot, lesson order=1 (L2)."""
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

LESSON_ID = 760

TITLE_RU = "2-Flask backend API"

TEXT_RU = """\
<h2>Этап 2: Flask backend API — CRUD для Category и Expense</h2>

<pre class="mermaid">
flowchart LR
    MODEL["Модель Flask-SQLAlchemy"] --> DICT["to_dict() - JSON-совместимый dict"]
    DICT --> JSONIFY["jsonify(dict) - работает правильно"]
    MODEL -->|напрямую jsonify()| ERROR["TypeError: Object of type Expense is not JSON serializable"]
</pre>

<p>На курсе Flask О'rta daraja вы уже видели Flask-SQLAlchemy и REST API. На этом этапе построим их как JSON API, организованный через <strong>Blueprint</strong>, который будут использовать и vanilla JS frontend (урок 3), и Telegram-бот (урок 5).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — модели Flask-SQLAlchemy (по схеме из урока 1)</h4>
<pre><code># app/models.py
from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summa = db.Column(db.Numeric(10, 2), nullable=False)   # ❗ как в уроке 1 - NUMERIC
    tavsif = db.Column(db.String(200))
    sana = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):                          # ❗ превращает модель в JSON-совместимый dict
        return {
            "id": self.id,
            "summa": float(self.summa),           # ❗ Decimal тоже не стандартный тип JSON!
            "tavsif": self.tavsif,
            "sana": self.sana.isoformat(),         # ❗ date тоже превращается в текст
            "category_nomi": self.category.nomi,
        }</code></pre>

<h4>БЛОК 2 — JSON API через Blueprint</h4>
<pre><code># app/routes.py
from flask import Blueprint, jsonify, request
from app import db
from app.models import Expense, Category

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/expenses', methods=['GET'])
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=1).all()   # ❗ в уроке 4 заменим на request.user
    return jsonify([x.to_dict() for x in xarajatlar])         # ❗ через to_dict() - ПРАВИЛЬНО

@api.route('/expenses', methods=['POST'])
def expense_yaratish():
    ma_lumot = request.get_json()
    yangi = Expense(
        summa=ma_lumot["summa"], tavsif=ma_lumot.get("tavsif", ""),
        sana=ma_lumot["sana"], category_id=ma_lumot["category_id"], user_id=1,
    )
    db.session.add(yangi)
    db.session.commit()
    return jsonify(yangi.to_dict()), 201</code></pre>

<h4>БЛОК 3 — app/__init__.py: регистрация Blueprint</h4>
<pre><code># app/__init__.py (Application Factory pattern - знакомо по уроку 1 курса Flask О'rta daraja)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = '...'
    db.init_app(app)

    from app.routes import api
    app.register_blueprint(api)

    return app</code></pre>

<h3>🐛 Намеренная ошибка — прямая передача объекта модели в jsonify()</h3>
<pre><code>@api.route('/expenses/<int:id>')
def expense_korish(id):
    xarajat = Expense.query.get_or_404(id)
    return jsonify(xarajat)   # ❌ to_dict() НЕ ИСПОЛЬЗОВАН!

# При отправке запроса:
# ❌ TypeError: Object of type Expense is not JSON serializable
# (jsonify() Flask не "понимает" объект Expense - он ожидает только
#  простые типы Python: dict, list, string, число)</code></pre>

<p><strong>Результат:</strong> <code>jsonify()</code> может преобразовать в JSON только <strong>стандартные</strong> типы Python (dict, list, str, int, float, bool, None). <code>Expense</code> &mdash; это <strong>особый</strong> класс Python (модель SQLAlchemy), и <code>jsonify()</code> "не знает", как превратить его в JSON &mdash; поэтому возникает <code>TypeError</code>. Решение: <strong>сначала</strong> превратить модель в обычный <code>dict</code> через <code>to_dict()</code>, <strong>затем</strong> передать этот dict в <code>jsonify()</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему метод <code>to_dict()</code> пишется в самом классе модели?</h4>
<p>Это &mdash; хорошая практика для <strong>организованного</strong> кода: каждая модель сама знает, как "переводится" в JSON. Это позволяет не переписывать эту логику в каждой route-функции.</p>

<h4>2. Почему используется <code>float(self.summa)</code>?</h4>
<p>Столбец <code>summa</code> имеет тип <code>Numeric</code>, и в Python он возвращается как объект <code>Decimal</code>. <code>Decimal</code> тоже <strong>не</strong> является стандартно поддерживаемым типом <code>jsonify()</code> &mdash; поэтому перед выводом в JSON его нужно преобразовать в <code>float()</code> (важность "точности при хранении", подчёркнутая в уроке 1, относится к хранению и вычислениям в базе, а не к отображению <strong>одного</strong> значения через JSON).</p>

<h4>3. Зачем используется Application Factory pattern (<code>create_app()</code>)?</h4>
<p>Это &mdash; паттерн, изученный в уроке 1 курса Flask О'rta daraja: создание приложения <code>Flask</code> внутри функции позволяет гибко использовать разные конфигурации (тест, production).</p>

<h4>4. Зачем используется Blueprint?</h4>
<p><code>Blueprint</code> &mdash; паттерн из урока 2 курса Flask О'rta daraja: позволяет выделить маршруты в <strong>отдельный, организованный</strong> модуль. Когда проект растёт (например добавляются дополнительные маршруты для бота), эта структура сохраняется.</p>

<h4>5. Почему прямая передача объекта модели в <code>jsonify()</code> даёт ошибку?</h4>
<p><code>jsonify()</code> внутренне использует стандартный модуль Python <code>json</code>, который умеет "сериализовать" только <strong>простые</strong> типы (dict, list и т.д.). Так как класс <code>Expense</code> — особый объект Python, модуль <code>json</code> "не знает", как превратить его в текст (JSON), и выдаёт ошибку.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Добавление метода <code>to_dict()</code> в класс модели — организованная практика для JSON API</li>
<li>✅ <code>Decimal</code> (столбцы Numeric) нужно преобразовать в <code>float()</code> перед выводом в JSON</li>
<li>✅ Application Factory и Blueprint — знакомые паттерны из курса Flask О'rta daraja, применяются и здесь</li>
<li>✅ <code>jsonify()</code> поддерживает только простые типы Python (dict, list, str, число)</li>
<li>✅ Прямая передача объекта модели в <code>jsonify()</code> даёт <code>TypeError</code> — сначала нужен <code>to_dict()</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 2: Flask backend API - CRUD для Category и Expense
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/models.py
# ─────────────────────────────────────────────────────────────────────

from app import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summa = db.Column(db.Numeric(10, 2), nullable=False)
    tavsif = db.Column(db.String(200))
    sana = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.relationship('Category')

    def to_dict(self):
        return {
            "id": self.id,
            "summa": float(self.summa),
            "tavsif": self.tavsif,
            "sana": self.sana.isoformat(),
            "category_nomi": self.category.nomi,
        }

# ─────────────────────────────────────────────────────────────────────
# 2) app/routes.py - JSON API через Blueprint
# ─────────────────────────────────────────────────────────────────────

from flask import Blueprint, jsonify, request

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/expenses', methods=['GET'])
def expenses_royxati():
    xarajatlar = Expense.query.filter_by(user_id=1).all()
    return jsonify([x.to_dict() for x in xarajatlar])


@api.route('/expenses', methods=['POST'])
def expense_yaratish():
    ma_lumot = request.get_json()
    yangi = Expense(
        summa=ma_lumot["summa"], tavsif=ma_lumot.get("tavsif", ""),
        sana=ma_lumot["sana"], category_id=ma_lumot["category_id"], user_id=1,
    )
    db.session.add(yangi)
    db.session.commit()
    return jsonify(yangi.to_dict()), 201

# ─────────────────────────────────────────────────────────────────────
# 3) app/__init__.py (в комментарии - Application Factory)
# ─────────────────────────────────────────────────────────────────────

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy()
#
# def create_app():
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = '...'
#     db.init_app(app)
#     from app.routes import api
#     app.register_blueprint(api)
#     return app

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - прямая передача модели в jsonify() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @api.route('/expenses/<int:id>')
# def expense_korish_xato(id):
#     xarajat = Expense.query.get_or_404(id)
#     return jsonify(xarajat)   # to_dict() НЕ ИСПОЛЬЗОВАН!
# ❌ TypeError: Object of type Expense is not JSON serializable
"""

EX = {
    4404: {
        "title": "Зачем нужен метод to_dict()?",
        "description": "Почему в модель Expense добавляется метод to_dict(), а не передаётся напрямую сам объект модели в jsonify()?",
        "hint": "Какие типы \"понимает\" jsonify()?",
        "explanation": "jsonify() может преобразовать в JSON только стандартные типы Python (dict, list, str, число) — объект модели является особым классом, поэтому его сначала нужно превратить в обычный dict через to_dict().",
    },
    4405: {
        "title": "Почему используется float(self.summa)?",
        "description": "Почему в методе to_dict() поле summa возвращается не напрямую, а через float(self.summa)?",
        "hint": "В какой тип превращается столбец db.Numeric в Python?",
        "explanation": "Столбец Numeric в Python возвращается как объект Decimal, который тоже не является стандартным типом jsonify() — поэтому перед выводом в JSON он преобразуется в float().",
    },
    4406: {
        "title": "Расположите процесс запроса GET /api/expenses",
        "description": "Расположите процесс, происходящий внутри expenses_royxati() при получении GET-запроса от vanilla JS.",
        "hint": "",
        "explanation": "",
    },
    4407: {
        "title": "Инструмент Flask для выделения маршрутов в отдельный модуль",
        "description": "Напишите инструмент Flask, используемый для выделения маршрутов в отдельный, организованный модуль (знакомый по курсу Flask О'rta daraja).",
        "hint": "",
        "expected_answer": "Blueprint",
    },
    4408: {
        "title": "Почему прямая передача объекта модели в jsonify() даёт TypeError?",
        "description": (
            "Если в функции expense_korish_xato() вызвать jsonify(xarajat) "
            "без to_dict() (xarajat — объект Expense), почему Flask "
            "выдаёт ошибку \"TypeError: Object of type Expense is not "
            "JSON serializable\"? Объясните своими словами."
        ),
        "hint": "Какие типы \"знает\" jsonify() (или используемый им модуль json), и относится ли к ним класс Expense?",
        "expected_answer": "jsonify() внутренне использует стандартный модуль Python json, который умеет преобразовывать в текст JSON только простые, \"знакомые\" типы Python вроде dict, list, str, число. Класс Expense же — особый объект Python, созданный SQLAlchemy — модуль json заранее не знает, как \"перевести\" этот особый класс в вид JSON, поэтому считает его \"несериализуемым\" (not JSON serializable) и выдаёт ошибку TypeError. Именно метод to_dict() вручную выполняет этот \"перевод\", после чего результат становится знакомым для jsonify() обычным dict.",
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
        TASK_TITLE_RU = "MoneyLog — Flask backend API (Category + Expense)"
        TASK_DESCRIPTION_RU = (
            "На основе схемы из этапа 1 создайте модели Flask-SQLAlchemy "
            "Category и Expense, выполните миграцию. Добавьте обеим метод "
            "to_dict(). Постройте через Blueprint JSON API, поддерживающий "
            "GET и POST запросы."
        )
        TASK_REQUIREMENTS_RU = (
            "• Модели Category и Expense созданы с правильными foreign key\n"
            "• Столбец summa имеет тип Numeric(10,2) (не FLOAT)\n"
            "• В обеих моделях есть метод to_dict(), Decimal/date правильно приведены к JSON-совместимому виду\n"
            "• GET /api/expenses — возвращает все расходы вместе с category_nomi как JSON-список\n"
            "• POST /api/expenses — создаёт новый расход, возвращает 201\n"
            "• Маршруты организованы через Blueprint\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Flask, Flask-SQLAlchemy, PostgreSQL"
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
