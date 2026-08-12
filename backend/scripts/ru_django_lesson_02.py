"""Russian translation for Python: Django Asoslari, lesson order=1 (L2)."""
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

LESSON_ID = 688

TITLE_RU = "2-URL routing и views"

TEXT_RU = """\
<h2>URL routing и views — направление запроса в нужную функцию</h2>

<pre class="mermaid">
flowchart LR
    A["/blog/"] --> V1["views.postlar_royxati"]
    B["/blog/5/"] --> V2["views.post_detail(post_id=5)"]
    C["mysite/urls.py"] -->|include| D["blog/urls.py"]
</pre>

<p>На Flask вы бы написали <code>@app.route("/blog/&lt;int:post_id&gt;")</code>. В Django routing хранится в отдельном файле <code>urls.py</code>, <strong>отдельно от views</strong> &mdash; это позволяет в крупных проектах видеть все маршруты в одном месте.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — простой path() и view</h4>
<pre><code># blog/views.py
from django.http import HttpResponse

def postlar_royxati(request):
    return HttpResponse("Barcha postlar ro'yxati")

def salomlash(request):
    return HttpResponse("Salom, Django!")

# blog/urls.py (новый файл - создаётся отдельно)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),      # ❗ '' - это сам blog/
    path('salom/', views.salomlash, name='salomlash'),        # ❗ blog/salom/
]</code></pre>

<h4>БЛОК 2 — include() в главном urls.py</h4>
<pre><code># mysite/urls.py (главный файл маршрутизации проекта)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # ❗ все URL, начинающиеся с blog/, направляются в blog/urls.py
]
# Результат: mysite.com/blog/salom/  ->  'salom/' в blog/urls.py -> views.salomlash</code></pre>

<h4>БЛОК 3 — динамические параметры URL</h4>
<pre><code># blog/urls.py
urlpatterns = [
    path('', views.postlar_royxati, name='post-list'),
    path('<int:post_id>/', views.post_detail, name='post-detail'),  # ❗ <int:post_id> - принимает целое число
]

# blog/views.py
def post_detail(request, post_id):          # ❗ параметр из URL приходит в view как аргумент
    return HttpResponse(f"Post ID: {post_id}")

# blog/5/  ->  post_detail(request, post_id=5)  ->  "Post ID: 5"
# blog/abc/ -> ❌ не подходит, потому что <int:...> принимает только целое число</code></pre>

<h3>🐛 Намеренная ошибка — забыли сделать include() в mysite/urls.py</h3>
<pre><code># blog/urls.py написан правильно, но в mysite/urls.py:
urlpatterns = [
    path('admin/', admin.site.urls),
    # строки path('blog/', include('blog.urls')) нет!
]

# При открытии mysite.com/blog/ в браузере:
# ❌ Ошибка: Page not found (404) - Django вообще не знает о blog/urls.py</code></pre>

<p><strong>Результат:</strong> файл <code>urls.py</code> каждого приложения <strong>не работает сам по себе</strong> &mdash; его обязательно нужно подключить к главному <code>urls.py</code> проекта через <code>include()</code>. Иначе, даже если весь routing в приложении blog написан правильно, Django их вообще "не увидит", так как главный файл маршрутизации не указывает на них никакого пути.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему routing хранится в отдельном файле urls.py?</h4>
<p>На Flask routing и view обычно пишутся в одном месте (декоратор <code>@app.route</code>). В Django routing хранится <strong>отдельно</strong> &mdash; это позволяет в крупных проектах видеть, упорядочивать все URL в одном месте и переиспользовать между приложениями.</p>

<h4>2. Зачем нужен include()?</h4>
<p><code>include('blog.urls')</code> говорит главному файлу <code>urls.py</code> проекта: "если URL начинается с <code>blog/</code>, ищи оставшуюся часть в файле <code>blog/urls.py</code>". Это позволяет хранить routing каждого приложения самостоятельно, в отдельном файле.</p>

<h4>3. Как работают динамические параметры URL?</h4>
<p>Запись вроде <code>&lt;int:post_id&gt;</code> "захватывает" часть URL и передаёт её в view-функцию <strong>как аргумент</strong>. Часть <code>int:</code> &mdash; конвертер, обеспечивающий соответствие только целым числам (есть и другие конвертеры, например <code>str:</code>, <code>slug:</code>).</p>

<h4>4. Зачем нужен параметр name=?</h4>
<p>Указание <code>name=</code> для каждого <code>path()</code> позволяет позже обращаться к этому URL в шаблоне или коде view по имени, через <code>{% url 'post-detail' post_id=5 %}</code>, вместо <strong>жёстко прописанного текста</strong> (например <code>"/blog/5/"</code>) &mdash; даже если адрес URL изменится, код менять не придётся.</p>

<h4>5. Почему без include() выдаётся ошибка 404?</h4>
<p>Django ищет запрос от браузера <strong>только</strong> через главный файл <code>urls.py</code> проекта. Если главный файл не направлен через <code>include()</code> на <code>urls.py</code> какого-либо приложения, все маршруты внутри этого приложения для Django "не существуют" &mdash; в результате выдаётся ошибка 404 (Page not found).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Routing хранится в файле <code>urls.py</code>, отдельно от views</li>
<li>✅ <code>include('app.urls')</code> — подключает routing приложения к главному <code>urls.py</code></li>
<li>✅ <code>&lt;int:param&gt;</code> — передаёт динамическую часть URL в view как аргумент</li>
<li>✅ <code>name=</code> — даёт URL имя, позволяя обращаться к нему по имени вместо жёсткого текста в коде</li>
<li>✅ Без <code>include()</code> routing приложения полностью "невидим", и выдаётся ошибка 404</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 2: URL routing и views
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - простые view
# ─────────────────────────────────────────────────────────────────────

from django.http import HttpResponse


def postlar_royxati(request):
    return HttpResponse("Barcha postlar ro'yxati")


def salomlash(request):
    return HttpResponse("Salom, Django!")


def post_detail(request, post_id):
    return HttpResponse(f"Post ID: {post_id}")

# ─────────────────────────────────────────────────────────────────────
# 2) blog/urls.py - файл маршрутизации приложения
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.postlar_royxati, name='post-list'),
#     path('salom/', views.salomlash, name='salomlash'),
#     path('<int:post_id>/', views.post_detail, name='post-detail'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 3) mysite/urls.py - главный файл маршрутизации
# ─────────────────────────────────────────────────────────────────────

# from django.contrib import admin
# from django.urls import path, include
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('blog/', include('blog.urls')),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли include() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # строки path('blog/', include('blog.urls')) нет!
# ]
# mysite.com/blog/ -> ❌ Page not found (404)
"""

EX = {
    4050: {
        "title": "Где хранится routing в Django?",
        "description": "В отличие от Flask, где обычно хранится URL routing в Django?",
        "hint": "На Flask @app.route в одном месте, а в Django...",
        "explanation": "В Django routing хранится отдельно от views, в специальном файле urls.py — это позволяет видеть все маршруты в одном месте.",
    },
    4051: {
        "title": "Для чего используется include()?",
        "description": "Что делает строка path('blog/', include('blog.urls')) в mysite/urls.py?",
        "hint": "Это соединяет два файла urls.py друг с другом.",
        "explanation": "include('blog.urls') указывает главному urls.py искать оставшуюся часть URL, начинающихся с blog/, в файле blog/urls.py.",
    },
    4052: {
        "title": "Расположите процесс динамического запроса URL",
        "description": "Расположите процесс работы при открытии blog/5/ через path('<int:post_id>/', views.post_detail).",
        "hint": "",
        "explanation": "",
    },
    4053: {
        "title": "Причина указания name= в path()",
        "description": "Чем полезно указание параметра name= в path()? (одним словом: через что можно обращаться в шаблоне или коде?)",
        "hint": "То, что используется в теге {% url '...' %}.",
        "expected_answer": "имя",
    },
    4054: {
        "title": "Почему без include() выдаётся ошибка 404?",
        "description": (
            "blog/urls.py написан правильно, но в mysite/urls.py нет "
            "строки path('blog/', include('blog.urls')). Почему при "
            "открытии blog/ в браузере выдаётся ошибка 404 (Page not "
            "found), хотя в blog/urls.py есть соответствующий routing? "
            "Объясните своими словами."
        ),
        "hint": "Откуда Django начинает искать запрос — из всех файлов urls.py или только из главного?",
        "expected_answer": "Django ищет и проверяет любой запрос от браузера ТОЛЬКО через главный файл urls.py проекта — он не ищет самостоятельно файлы urls.py других приложений. Если в главном urls.py нет строки include('blog.urls'), Django вообще не знает о routing внутри приложения blog — для него эти маршруты \"не существуют\". Поэтому, даже если в blog/urls.py всё написано правильно, так как к нему не указан никакой путь, Django возвращает ошибку 404.",
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
