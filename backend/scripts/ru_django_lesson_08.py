"""Russian translation for Python: Django Asoslari, lesson order=9 (L8)."""
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

LESSON_ID = 704

TITLE_RU = "8-Аутентификация"

TEXT_RU = """\
<h2>Аутентификация — готовая система django.contrib.auth</h2>

<pre class="mermaid">
flowchart LR
    REG["Регистрация"] --> LOGIN["Вход (login)"]
    LOGIN --> SESSION["Создаётся session cookie"]
    SESSION --> PROTECTED["Страница, защищённая @login_required"]
    PROTECTED -->|не вошёл| REDIRECT["перенаправление на страницу входа"]
</pre>

<p>На Flask вы бы строили аутентификацию вручную, с дополнительной библиотекой вроде Flask-Login. В Django <code>django.contrib.auth</code> &mdash; <strong>встроенная, готовая</strong> система аутентификации: модель пользователя, login/logout, безопасное хранение паролей (хеширование) и разрешения &mdash; всё <strong>уже есть</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — регистрация и вход</h4>
<pre><code># blog/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

def royxatdan_otish(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)         # ❗ готовая форма регистрации Django
        if form.is_valid():
            user = form.save()                          # ❗ пароль АВТОМАТИЧЕСКИ хешируется при сохранении
            login(request, user)                         # ❗ сразу начинает сессию входа
            return redirect('post-list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/royxat.html', {'form': form})

def kirish(request):
    if request.method == 'POST':
        username = request.POST['username']
        parol = request.POST['password']
        user = authenticate(request, username=username, password=parol)  # ❗ проверяет, но ещё не входит
        if user is not None:
            login(request, user)                          # ❗ только теперь создаётся session
            return redirect('post-list')
    return render(request, 'blog/kirish.html')</code></pre>

<h4>БЛОК 2 — выход и защищённые страницы</h4>
<pre><code># blog/views.py
from django.contrib.auth.decorators import login_required

def chiqish(request):
    logout(request)                    # ❗ завершает сессию
    return redirect('post-list')

@login_required                        # ❗ доступ только для прошедших аутентификацию
def post_yaratish(request):
    # ... работа с формой ...
    pass
# можно написать и login_required(login_url='/kirish/') - чтобы указать куда перенаправлять</code></pre>

<h4>БЛОК 3 — request.user в шаблоне</h4>
<pre><code>{# В любом шаблоне request.user доступен автоматически #}
{% if user.is_authenticated %}
  &lt;p&gt;Salom, {{ user.username }}!&lt;/p&gt;
  &lt;a href="{% url 'chiqish' %}"&gt;Chiqish&lt;/a&gt;
{% else %}
  &lt;a href="{% url 'kirish' %}"&gt;Kirish&lt;/a&gt;
{% endif %}</code></pre>

<h3>🐛 Намеренная ошибка — view, который должен быть защищён, но без login_required</h3>
<pre><code># БЕЗ декоратора @login_required:
def post_yaratish(request):
    # ... логика создания поста ...
    pass

# В результате: даже НЕ вошедший (анонимный) пользователь может напрямую
# зайти на /blog/yaratish/ и создать пост - это ПРОБЛЕМА БЕЗОПАСНОСТИ!</code></pre>

<p><strong>Результат:</strong> установка системы аутентификации Django (модель пользователя, login/logout) <strong>ещё не</strong> защищает страницы <strong>автоматически</strong>. К каждому view, который должен быть защищён, нужно <strong>явно</strong> добавить декоратор <code>@login_required</code>. Если этого не сделать, невошедший пользователь тоже может напрямую (через URL) зайти на этот view и выполнить действия &mdash; это серьёзная уязвимость безопасности.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое UserCreationForm?</h4>
<p><strong>Готовая</strong> форма Django из <code>django.contrib.auth.forms</code> &mdash; содержит поля username, пароля и подтверждения пароля, сохраняет пароль <strong>автоматически хешированным</strong> (в безопасном виде).</p>

<h4>2. Разница между authenticate() и login()</h4>
<p><code>authenticate()</code> проверяет, <strong>верны ли</strong> переданные username/пароль, и если верны, возвращает объект <code>User</code> (не создавая никакой сессии). <code>login()</code> <strong>действительно</strong> начинает session (состояние входа) для переданного <code>User</code>. Обычно они используются последовательно, вместе.</p>

<h4>3. Что делает @login_required?</h4>
<p>Этот декоратор <strong>оборачивает</strong> view-функцию: если пользователь не прошёл аутентификацию, сам view не запускается, а пользователь автоматически перенаправляется на страницу входа. Это избавляет от необходимости писать вручную проверку <code>if not request.user.is_authenticated</code> в каждом view.</p>

<h4>4. Что такое request.user?</h4>
<p>Django <strong>автоматически</strong> добавляет <code>request.user</code> к каждому запросу &mdash; если пользователь вошёл, это реальный объект <code>User</code>, иначе <code>AnonymousUser</code> (специальный объект "невошедшего пользователя"). Поэтому <code>{% if user.is_authenticated %}</code> всегда работает безопасно.</p>

<h4>5. Почему без login_required возникает проблема безопасности?</h4>
<p>Система аутентификации Django работает по принципу <strong>"opt-in"</strong> &mdash; то есть <strong>вы сами</strong> должны <strong>явно</strong> указать, какой view защищать. Если <code>@login_required</code> не добавлен, Django считает этот view "открытым", и невошедший пользователь тоже может напрямую (через URL) обратиться к нему и выполнить действие.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>UserCreationForm</code> — готовая форма регистрации, автоматически хеширует пароль</li>
<li>✅ <code>authenticate()</code> — проверяет, <code>login()</code> — начинает session</li>
<li>✅ <code>@login_required</code> — автоматически перенаправляет невошедшего пользователя на страницу входа</li>
<li>✅ <code>request.user</code> — доступен всегда: реальный User или AnonymousUser</li>
<li>✅ Защита работает по принципу "opt-in" — должна быть явно добавлена к каждому нужному view</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 8: Аутентификация
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - регистрация и вход
# ─────────────────────────────────────────────────────────────────────

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect


def royxatdan_otish(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post-list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/royxat.html', {'form': form})


def kirish(request):
    if request.method == 'POST':
        username = request.POST['username']
        parol = request.POST['password']
        user = authenticate(request, username=username, password=parol)
        if user is not None:
            login(request, user)
            return redirect('post-list')
    return render(request, 'blog/kirish.html')

# ─────────────────────────────────────────────────────────────────────
# 2) Выход и защищённый view
# ─────────────────────────────────────────────────────────────────────

from django.contrib.auth.decorators import login_required


def chiqish(request):
    logout(request)
    return redirect('post-list')


@login_required
def post_yaratish(request):
    pass

# ─────────────────────────────────────────────────────────────────────
# 3) templates/blog/base.html (в комментарии) - request.user
# ─────────────────────────────────────────────────────────────────────

# {% if user.is_authenticated %}
#   <p>Salom, {{ user.username }}!</p>
#   <a href="{% url 'chiqish' %}">Chiqish</a>
# {% else %}
#   <a href="{% url 'kirish' %}">Kirish</a>
# {% endif %}

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - view без login_required (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def post_yaratish_xato(request):
#     # НЕТ @login_required!
#     pass
# # Даже невошедший пользователь может напрямую зайти и создать пост!
"""

EX = {
    4126: {
        "title": "Что делает UserCreationForm?",
        "description": "Для чего используется UserCreationForm из django.contrib.auth.forms?",
        "hint": "Это одна из готовых форм Django.",
        "explanation": "UserCreationForm — готовая форма с полями username, пароля и подтверждения пароля, автоматически сохраняющая пароль в безопасном (хешированном) виде.",
    },
    4127: {
        "title": "Разница между authenticate() и login()",
        "description": "В чём основная разница между функциями authenticate() и login()?",
        "hint": "Одна \"проверяет\", другая \"начинает вход\".",
        "explanation": "authenticate() проверяет верность username/пароля (не создавая session), login() же действительно начинает session (состояние входа).",
    },
    4128: {
        "title": "Расположите процесс входа",
        "description": "Расположите процесс, происходящий при заполнении и отправке пользователем формы входа.",
        "hint": "",
        "explanation": "",
    },
    4129: {
        "title": "Декоратор для защиты view",
        "description": "Какой декоратор ставится над view-функцией, чтобы доступ был только у прошедших аутентификацию пользователей? (напишите именно этот декоратор)",
        "hint": "Импортируется из django.contrib.auth.decorators.",
        "expected_answer": "@login_required",
    },
    4130: {
        "title": "Почему без login_required возникает проблема безопасности?",
        "description": (
            "Если к view post_yaratish не добавлен декоратор "
            "@login_required, почему невошедший (анонимный) "
            "пользователь тоже может напрямую зайти на "
            "/blog/yaratish/ и создать пост? Объясните своими словами."
        ),
        "hint": "Установка системы аутентификации Django автоматически защищает все view?",
        "expected_answer": "Система аутентификации Django работает по принципу \"opt-in\" — то есть установка системы пользователей (login/logout, модель User) ещё не защищает автоматически ни один view. Разработчик должен явно добавить декоратор @login_required к каждому view, который нужно защитить. Если это не сделано, Django считает этот view \"открытым\" — независимо от того, вошёл пользователь или нет, view всё равно запускается, поэтому анонимный пользователь тоже может напрямую через URL обратиться к нему и выполнить такие действия, как создание поста — это серьёзная уязвимость безопасности.",
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
