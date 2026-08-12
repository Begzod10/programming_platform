"""Russian translation for Python: Django Asoslari, lesson order=0 (L1)."""
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

LESSON_ID = 686

TITLE_RU = "1-Введение в Django и архитектура MTV"

TEXT_RU = """\
<h2>Введение в Django — первая страница за 5 минут</h2>

<pre class="mermaid">
flowchart LR
    REQ["Запрос браузера"] --> URL["urls.py — какой View?"]
    URL --> VIEW["views.py — логика, получение данных из Model"]
    VIEW --> MODEL["models.py — база данных"]
    VIEW --> TEMPLATE["template.html — HTML результат"]
    TEMPLATE --> RESP["Ответ браузеру"]
</pre>

<p>Вы умеете строить веб-приложения на Flask &mdash; routing, view-функции, шаблоны. <strong>Django</strong> тоже веб-фреймворк на Python, но в отличие от Flask, он "batteries-included" &mdash; то есть ORM, админ-панель, аутентификация, валидация форм и многое другое поставляются <strong>уже готовыми</strong>. Для крупных, серьёзных проектов именно Django считается отраслевым стандартом.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание проекта и приложения</h4>
<pre><code># В терминале:
django-admin startproject mysite    # ❗ создаётся проект (весь сайт)
cd mysite
python manage.py startapp blog      # ❗ создаётся app (одна функциональная часть)

# В результате получается такая структура:
# mysite/
#   manage.py          <- через него запускаются все команды
#   mysite/settings.py <- настройки проекта (здесь INSTALLED_APPS)
#   mysite/urls.py      <- главные маршруты URL
#   blog/
#     models.py         <- таблицы базы данных
#     views.py          <- логика (что нужно показать)
#     admin.py          <- регистрация в админ-панели

python manage.py runserver           # ❗ запускает локальный сервер (127.0.0.1:8000)</code></pre>

<h4>БЛОК 2 — регистрация приложения (INSTALLED_APPS)</h4>
<pre><code># mysite/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # ❗ созданное приложение обязательно нужно "представить" Django, иначе оно не заработает
]</code></pre>

<h4>БЛОК 3 — архитектура MTV (Model-Template-View)</h4>
<pre><code># Django называет свою версию MVC (Model-View-Controller) термином MTV:
#
# Model    -> работает с базой данных (models.py)
# Template -> HTML, видимый пользователю (templates/)
# View     -> получает данные из Model, передаёт в Template - выполняет роль "controller"

# blog/views.py
from django.http import HttpResponse

def salomlash(request):          # ❗ каждый view принимает HttpRequest, возвращает HttpResponse
    return HttpResponse("Salom, Django!")</code></pre>

<h3>🐛 Намеренная ошибка — забыли добавить приложение в INSTALLED_APPS</h3>
<pre><code># В blog/models.py создана модель, но в settings.py:
INSTALLED_APPS = [
    'django.contrib.admin',
    # строки 'blog' нет!
]

# Если запустить команду python manage.py makemigrations blog:
# ❌ Ошибка: App 'blog' could not be found. Is it in INSTALLED_APPS?</code></pre>

<p><strong>Результат:</strong> Django не "чувствует" автоматически папки в проекте &mdash; каждое приложение обязательно должно быть добавлено в список <code>INSTALLED_APPS</code>, иначе Django <strong>вообще не увидит</strong> его models, admin или другие части. Это отличается от логики Flask "создал папку — работает" &mdash; в Django каждая часть должна быть <strong>явно зарегистрирована</strong>.</p>

<h3>Теперь объясним</h3>

<h4>1. Основное различие между Django и Flask</h4>
<p>Flask &mdash; "микро-фреймворк": минимальный, нужные вещи (ORM, forms, auth) вы добавляете сами. Django &mdash; "batteries-included": ORM, админ-панель, система аутентификации, валидация форм &mdash; многое уже <strong>готово</strong>. В крупных проектах это ускоряет работу, но нужно соблюдать собственные правила (конвенции) Django.</p>

<h4>2. Разница между проектом (project) и приложением (app)</h4>
<p><strong>Проект</strong> &mdash; весь сайт (настройки, главные URL). <strong>App</strong> &mdash; одна самостоятельная функциональная часть внутри проекта (например <code>blog</code>, <code>users</code>, <code>shop</code>). В одном проекте может быть несколько app, и app могут переиспользоваться и в других проектах.</p>

<h4>3. Архитектура MTV</h4>
<p>MTV в Django очень похожа на классический MVC, только называется иначе: <strong>Model</strong> (база данных) — то же самое, что Model в MVC. <strong>Template</strong> (HTML) — соответствует View в MVC. <strong>View</strong> (в Django) — выполняет роль Controller в MVC, то есть получает данные из Model и передаёт их в Template.</p>

<h4>4. Почему каждое приложение нужно добавлять в INSTALLED_APPS?</h4>
<p>Так как Django — крупный, сложный фреймворк, он должен <strong>точно</strong> знать, какие app "активны" — это нужно для отслеживания миграций этих app, регистрации в admin и множества других внутренних процессов. Приложение, не добавленное в список, для Django считается "несуществующим".</p>

<h4>5. Зачем нужен manage.py?</h4>
<p><code>manage.py</code> &mdash; "центр управления" проектом: запуск сервера (<code>runserver</code>), создание/применение миграций (<code>makemigrations</code>/<code>migrate</code>), создание суперпользователя и все остальные команды Django запускаются через этот файл.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>django-admin startproject</code> создаёт проект, <code>python manage.py startapp</code> — приложение</li>
<li>✅ Каждое приложение <strong>обязательно</strong> нужно добавить в <code>INSTALLED_APPS</code>, иначе Django его "не увидит"</li>
<li>✅ MTV: Model (БД) — Template (HTML) — View (логика, Controller в MVC)</li>
<li>✅ Django "batteries-included" — в отличие от Flask многое поставляется готовым</li>
<li>✅ <code>manage.py runserver</code> — запускает локальный сервер</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 1: Введение в Django и архитектура MTV
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Создание проекта и приложения (команды терминала, в комментарии)
# ─────────────────────────────────────────────────────────────────────

# django-admin startproject mysite
# cd mysite
# python manage.py startapp blog
# python manage.py runserver

# ─────────────────────────────────────────────────────────────────────
# 2) mysite/settings.py - регистрация приложения
# ─────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
]

# ─────────────────────────────────────────────────────────────────────
# 3) blog/views.py - первый view (часть View в MTV)
# ─────────────────────────────────────────────────────────────────────

from django.http import HttpResponse


def salomlash(request):
    return HttpResponse("Salom, Django!")

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли добавить в INSTALLED_APPS (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     # строки 'blog' нет!
# ]
# python manage.py makemigrations blog
# ❌ App 'blog' could not be found. Is it in INSTALLED_APPS?
"""

EX = {
    4040: {
        "title": "Основное различие между Django и Flask",
        "description": "В чём основное различие между Django и Flask?",
        "hint": "В одном многое готово, в другом добавляете сами.",
        "explanation": "Django \"batteries-included\" — ORM, админ-панель, аутентификация уже готовы. Flask же минимальный micro-framework, нужные вещи вы добавляете сами.",
    },
    4041: {
        "title": "Как регистрируется приложение?",
        "description": "Что нужно сделать, чтобы \"представить\" новое созданное Django-приложение проекту?",
        "hint": "Это список в файле настроек.",
        "explanation": "Каждое приложение обязательно нужно добавить в список INSTALLED_APPS файла settings.py, иначе Django его \"не увидит\".",
    },
    4042: {
        "title": "Расположите процесс запроса в MTV",
        "description": "Расположите по порядку процесс, происходящий при поступлении запроса от браузера в архитектуре MTV.",
        "hint": "",
        "explanation": "",
    },
    4043: {
        "title": "Команда для запуска локального сервера",
        "description": "Какая команда используется для запуска локального сервера в проекте Django? (напишите именно эту команду)",
        "hint": "Запускается через файл manage.py.",
        "expected_answer": "python manage.py runserver",
    },
    4044: {
        "title": "Почему не добавленное в INSTALLED_APPS приложение даёт ошибку?",
        "description": (
            "В blog/models.py создана модель, но 'blog' не добавлен в "
            "список INSTALLED_APPS. Если запустить команду "
            "makemigrations, почему Django выдаёт ошибку \"App 'blog' "
            "could not be found\"? Объясните своими словами."
        ),
        "hint": "Как Django \"узнаёт\" о приложениях — видя папку или через какой-то список?",
        "expected_answer": "Django не \"чувствует\" автоматически структуру папок — он узнаёт, какие приложения \"активны\" в проекте, только через список INSTALLED_APPS. Если 'blog' не добавлен в этот список, для Django оно считается \"несуществующим\" — поэтому он не может найти ни его файл models.py, ни его миграции, и выдаёт ошибку. Это правило Django о том, что каждая часть должна быть явно зарегистрирована.",
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
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={"title": TITLE_RU, "text_content": TEXT_RU},
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
