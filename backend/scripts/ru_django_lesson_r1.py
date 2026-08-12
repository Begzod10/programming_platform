"""Russian translation for Python: Django Asoslari, lesson order=4 (R1)."""
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

LESSON_ID = 694

TITLE_RU = "R1-Мини-блог (повторение)"

TEXT_RU = """\
<h2>R1 — Повторение уроков 1-4: Мини-блог</h2>

<p>Объединив всё из уроков 1-4, построим полностью рабочий мини-блог: модель Post, миграция, routing и наследование шаблонов — всё вместе.</p>

<h3>Цель проекта</h3>
<ul>
<li>Модель <code>Post</code> — с полями <code>sarlavha</code>, <code>matn</code>, <code>yaratilgan_vaqt</code> (урок 4)</li>
<li><code>blog/urls.py</code> — routing для страницы списка (<code>/blog/</code>) и детальной страницы (<code>/blog/&lt;int:post_id&gt;/</code>) (урок 2)</li>
<li>Шаблоны <code>post_list.html</code> и <code>post_detail.html</code>, унаследованные от <code>base.html</code> (урок 3)</li>
<li>Приложение должно быть правильно добавлено в <code>INSTALLED_APPS</code> и мигрировано (урок 1)</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — модель Post</h4>
<p>Создайте модель <code>Post</code> с полями <code>sarlavha</code> (CharField), <code>matn</code> (TextField), <code>yaratilgan_vaqt</code> (DateTimeField, <code>auto_now_add=True</code>), затем выполните <code>makemigrations</code> + <code>migrate</code> (как в уроке 4).</p>

<h4>Задание 2 — routing</h4>
<p>В <code>blog/urls.py</code> напишите два <code>path()</code>: для страницы списка (<code>''</code>) и детальной страницы (<code>'&lt;int:post_id&gt;/'</code>), подключите их к главному <code>urls.py</code> через <code>include()</code> (как в уроке 2).</p>

<h4>Задание 3 — views и templates</h4>
<p>View <code>postlar_royxati</code> получает <code>Post.objects.all()</code> и рендерит <code>post_list.html</code>; view <code>post_detail</code> получает <code>Post.objects.get(id=post_id)</code> и рендерит <code>post_detail.html</code>. Оба шаблона должны наследоваться от <code>base.html</code> через <code>extends</code> (как в уроке 3).</p>

<h4>Задание 4 — объединение</h4>
<p>Проверьте всё вместе: <code>/blog/</code> должен показывать список всех постов, <code>/blog/1/</code> — полный текст одного поста.</p>

<h3>🐛 Намеренная сложность: проверка view без миграции</h3>
<p>Если вы напишете модель <code>Post</code>, но НЕ ВЫПОЛНИТЕ <code>makemigrations</code>/<code>migrate</code>, а затем откроете view <code>postlar_royxati</code>, при вызове <code>Post.objects.all()</code> вы столкнётесь с ошибкой <strong>OperationalError: no such table: blog_post</strong> &mdash; это точно та же проблема, что и в уроке 4, но теперь в полноценном проекте. Правильный порядок: <strong>сначала</strong> напишите модель, <strong>сразу же</strong> выполните миграцию, и <strong>только затем</strong> проверяйте view/шаблон.</p>

<h3>Начальный код</h3>
<pre><code># blog/models.py
from django.db import models

class Post(models.Model):
    # Задание 1: добавьте поля sarlavha, matn, yaratilgan_vaqt
    pass

# blog/views.py
from django.shortcuts import render
from .models import Post

def postlar_royxati(request):
    # Задание 3: получите Post.objects.all() и отрендерите post_list.html
    pass

def post_detail(request, post_id):
    # Задание 3: получите Post.objects.get(id=post_id) и отрендерите post_detail.html
    pass

# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Задание 2: напишите два path()
]</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code># ─── blog/models.py ───
from django.db import models

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# В терминале: python manage.py makemigrations blog && python manage.py migrate

# ─── blog/views.py ───
from django.shortcuts import render
from .models import Post

def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})

def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# ─── blog/urls.py ───
from django.urls import path
from . import views

urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),
]

# ─── mysite/urls.py ───
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]

# ─── templates/blog/post_list.html ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li><a href="{% url 'post-detail' post.id %}">{{ post.sarlavha }}</a></li>
#   {% endfor %}
#   </ul>
# {% endblock %}

# ─── templates/blog/post_detail.html ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>{{ post.sarlavha }}</h1>
#   <p>{{ post.matn }}</p>
# {% endblock %}</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Всё из уроков 1-4 вместе: регистрация app, модель, миграция, routing, templates</li>
<li>✅ Правильный порядок: написать модель → выполнить миграцию → проверить view/шаблон</li>
<li>✅ <code>{% url 'post-detail' post.id %}</code> — создание динамической ссылки через name=</li>
<li>✅ Проверка view без миграции даёт ошибку "no such table"</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 1: Мини-блог (уроки 1-4)
# ════════════════════════════════════════════════════════════════════

# ─── blog/models.py ───
from django.db import models


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# В терминале: python manage.py makemigrations blog && python manage.py migrate

# ─── blog/views.py ───
from django.shortcuts import render


def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# ─── blog/urls.py ───
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.postlar_royxati, name='post-list'),
#     path('<int:post_id>/', views.post_detail, name='post-detail'),
# ]

# ─── templates/blog/post_list.html (в комментарии) ───
# {% extends 'base.html' %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li><a href="{% url 'post-detail' post.id %}">{{ post.sarlavha }}</a></li>
#   {% endfor %}
#   </ul>
# {% endblock %}
"""

EX = {
    4079: {
        "title": "Правильный порядок действий",
        "description": "Что нужно сделать после написания модели Post, прежде чем проверять view?",
        "hint": "Вспомните урок 4: Python-класс и реальная таблица — разные вещи.",
        "explanation": "После написания модели обязательно нужно выполнить makemigrations и migrate для создания реальной таблицы базы данных, иначе возникнет ошибка \"no such table\".",
    },
    4080: {
        "title": "Создание динамической ссылки в шаблоне",
        "description": "Какая запись используется в post_list.html для создания ссылки на детальную страницу каждого поста?",
        "hint": "Вспомните параметр name=, изученный в уроке 2.",
        "explanation": "{% url 'post-detail' post.id %} создаёт динамическую ссылку через name=, указанный в path() — код продолжает работать, даже если изменится адрес URL.",
    },
    4081: {
        "title": "Расположите процесс запроса мини-блога в правильном порядке",
        "description": "Расположите процесс, происходящий на сервере при открытии /blog/1/ в браузере.",
        "hint": "Вспомните все шаги, изученные в уроках 1-4, по порядку.",
        "explanation": "",
    },
    4082: {
        "title": "Почему регистрация app, миграция, routing и templates используются вместе?",
        "description": (
            "В проекте мини-блога почему важно применять вместе "
            "регистрацию app (урок 1), миграцию (урок 4), routing "
            "(урок 2) и наследование шаблонов (урок 3)? Какую проблему "
            "предотвращает каждый из них? Объясните своими словами."
        ),
        "hint": "Подумайте о каждом отдельно: что сломается, если его не будет?",
        "expected_answer": "Регистрация app (INSTALLED_APPS) \"представляет\" Django приложение blog — без неё Django вообще не увидит ни его модели, ни его миграции. Миграция превращает Python-класс модели Post в реальную таблицу базы данных — без неё возникает ошибка \"no such table\". Routing (urls.py + include()) направляет запрос от браузера в правильную view-функцию — без него выдаётся ошибка 404. Наследование шаблонов (extends/block) же предотвращает повторное написание одинакового HTML-скелета на каждой странице. Если каждый из них не работает на своём этапе, не работает и следующий этап — поэтому все они нужны вместе, в правильном порядке.",
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
