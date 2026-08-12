"""Russian translation for Python: Django Asoslari, lesson order=10 (L9)."""
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

LESSON_ID = 706

TITLE_RU = "9-Class-Based Views (CBV)"

TEXT_RU = """\
<h2>Class-Based Views (CBV) — сокращение повторяющихся view через классы</h2>

<pre class="mermaid">
flowchart LR
    FBV["Function-based view (много повторяющегося кода)"] -->|refactor| CBV["ListView/DetailView/CreateView"]
    CBV --> URLS["path(..., PostListView.as_view())"]
</pre>

<p>В уроках 1-8 мы писали все view как <strong>function-based</strong> (обычные функции). Но задачи вроде "показать список", "показать один объект", "создать/изменить/удалить" почти <strong>всегда имеют одинаковую</strong> структуру. Django предоставляет для этого готовые <strong>Class-Based Views (CBV)</strong> — они сокращают много повторяющегося кода.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — ListView и DetailView</h4>
<pre><code># blog/views.py
from django.views.generic import ListView, DetailView
from .models import Post

class PostListView(ListView):          # ❗ автоматически получает Post.objects.all() и рендерит
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'postlar'    # ❗ имя переменной, используемой в шаблоне

class PostDetailView(DetailView):      # ❗ автоматически получает Post.objects.get(pk=...)
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

# blog/urls.py
from django.urls import path
from .views import PostListView, PostDetailView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),          # ❗ .as_view() ОБЯЗАТЕЛЕН!
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]</code></pre>

<h4>БЛОК 2 — CreateView, UpdateView, DeleteView</h4>
<pre><code># blog/views.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class PostCreateView(LoginRequiredMixin, CreateView):   # ❗ Mixin - защита, похожая на login_required
    model = Post
    fields = ['sarlavha', 'matn']       # ❗ ModelForm создаётся автоматически (как в уроке 6)
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')  # ❗ куда перенаправить после успеха

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')</code></pre>

<h4>БЛОК 3 — сравнение CBV и function-based view</h4>
<pre><code># Function-based (как в уроке 4) - 5 строк:
def postlar_royxati(request):
    postlar = Post.objects.all()
    return render(request, 'blog/post_list.html', {'postlar': postlar})

# Тот же результат с CBV - меньше повторяющегося кода:
class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
# CBV сам автоматически: Post.objects.all() + render() + template_name (выводится из имени модели)</code></pre>

<h3>🐛 Намеренная ошибка — забыли .as_view() в urls.py</h3>
<pre><code># blog/urls.py
urlpatterns = [
    path('', PostListView, name='post-list'),   # ❌ НЕТ .as_view()!
]

# При запуске сервера или открытии страницы:
# ❌ Ошибка: View function did not return an HttpResponse object. It
#    returned None instead. (или ошибка типа TypeError)</code></pre>

<p><strong>Результат:</strong> система маршрутизации Django (<code>urls.py</code>) может вызывать только <strong>функции</strong> (так как каждый view — это вызываемая сущность, принимающая HTTP-запрос и возвращающая ответ). CBV же — <strong>класс</strong>, а не функция. Метод <code>.as_view()</code> <strong>превращает класс в вызываемую функцию</strong> — если пропустить этот шаг, Django попытается вызвать сам класс напрямую, и это не даст ожидаемого результата.</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем нужны CBV?</h4>
<p>Задачи вроде "показать список", "показать один объект", "создать/изменить/удалить" почти <strong>одинаково</strong> повторяются для каждой модели. CBV предоставляет этот общий паттерн в виде готовых классов <code>ListView</code>, <code>DetailView</code>, <code>CreateView</code> — разработчик указывает лишь небольшие настройки вроде <code>model</code>, <code>fields</code>.</p>

<h4>2. Почему .as_view() обязателен?</h4>
<p>Система маршрутизации Django ожидает в качестве view <strong>вызываемую функцию</strong>. <code>PostListView.as_view()</code> возвращает <strong>функцию</strong>, которая создаёт новый объект класса для каждого запроса и направляет запрос в нужный метод (например <code>get()</code>).</p>

<h4>3. Зачем нужен context_object_name?</h4>
<p>По умолчанию CBV даёт контексту общее имя вроде <code>object_list</code> (для ListView) или <code>object</code> (для DetailView). <code>context_object_name</code> позволяет <strong>изменить</strong> это имя (например на <code>postlar</code>), делая код шаблона более читаемым.</p>

<h4>4. Что такое LoginRequiredMixin?</h4>
<p>Это <strong>классовая версия</strong> <code>@login_required</code> для CBV: если написать <code>class PostCreateView(LoginRequiredMixin, CreateView)</code>, доступ к этому view получат только прошедшие аутентификацию пользователи, иначе они будут перенаправлены на страницу входа.</p>

<h4>5. Почему без .as_view() возникает ошибка?</h4>
<p>Сам класс (например <code>PostListView</code>) &mdash; обычный Python-класс, <strong>не знающий</strong>, как обрабатывать HTTP-запрос. <code>.as_view()</code> превращает его в <strong>настоящую функцию</strong>, создающую новый объект при каждом запросе и направляющую запрос в подходящий метод. Без этого шага <code>urls.py</code> попытается вызвать сам класс, что не даст ожидаемый <code>HttpResponse</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>ListView</code>/<code>DetailView</code> — готовые CBV для показа списка/одного объекта</li>
<li>✅ <code>CreateView</code>/<code>UpdateView</code>/<code>DeleteView</code> — готовые CBV для операций CRUD</li>
<li>✅ Каждый CBV в <code>urls.py</code> <strong>обязательно</strong> должен быть превращён в функцию через <code>.as_view()</code></li>
<li>✅ <code>LoginRequiredMixin</code> — классовый эквивалент <code>@login_required</code> для CBV</li>
<li>✅ CBV сокращает повторяющийся код, но для сложной, специфичной логики function-based view гибче</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 9: Class-Based Views (CBV)
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) ListView и DetailView
# ─────────────────────────────────────────────────────────────────────

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class PostListView(ListView):
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'


class PostDetailView(DetailView):
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

# ─────────────────────────────────────────────────────────────────────
# 2) CreateView, UpdateView, DeleteView
# ─────────────────────────────────────────────────────────────────────


class PostCreateView(LoginRequiredMixin, CreateView):
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')


class PostUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['sarlavha', 'matn']
    template_name = 'blog/post_form.html'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')

# ─────────────────────────────────────────────────────────────────────
# 3) blog/urls.py (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from .views import PostListView, PostDetailView
#
# urlpatterns = [
#     path('', PostListView.as_view(), name='post-list'),
#     path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли .as_view() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# urlpatterns = [
#     path('', PostListView, name='post-list'),   # ❌ НЕТ .as_view()!
# ]
# ❌ View function did not return an HttpResponse object. It returned
#    None instead.
"""

EX = {
    4136: {
        "title": "Для чего используются CBV?",
        "description": "Для чего в основном используются Class-Based Views (CBV)?",
        "hint": "Многие view имеют одинаковую структуру.",
        "explanation": "CBV сокращает повторяющийся код, предоставляя готовые классы для почти всегда одинаковых паттернов — показ списка, показ одного объекта, создание/изменение/удаление.",
    },
    4137: {
        "title": "Почему .as_view() обязателен?",
        "description": "В чём причина написания PostListView.as_view() в urls.py?",
        "hint": "Сам класс не знает, как обрабатывать HTTP-запрос.",
        "explanation": "Маршрутизация Django ожидает в качестве view вызываемую функцию. .as_view() создаёт из класса функцию, направляющую запрос в нужный метод.",
    },
    4138: {
        "title": "Расположите процесс работы PostCreateView",
        "description": "Расположите процесс, происходящий при создании пользователем нового поста через PostCreateView.",
        "hint": "",
        "explanation": "",
    },
    4139: {
        "title": "Классовый эквивалент @login_required",
        "description": "Напишите название класса-миксина, обеспечивающего для CBV защиту, похожую на @login_required.",
        "hint": "Импортируется из django.contrib.auth.mixins.",
        "expected_answer": "LoginRequiredMixin",
    },
    4140: {
        "title": "Почему без .as_view() возникает ошибка?",
        "description": (
            "Если в urls.py написать path('', PostListView, "
            "name='post-list') (то есть без .as_view()), почему Django "
            "выдаёт ошибку? Объясните своими словами."
        ),
        "hint": "Сам класс и результат .as_view() — оба ли являются \"вызываемыми\"?",
        "expected_answer": "Сам PostListView — обычный Python-класс, не знающий, как обрабатывать HTTP-запрос. Система маршрутизации Django ожидает в качестве view только вызываемую (callable) функцию, потому что при каждом запросе именно эта функция вызывается и должна вернуть HttpResponse. Метод .as_view() превращает класс в соответствующую этому требованию настоящую вызываемую функцию — она создаёт новый объект класса для каждого запроса и направляет запрос в подходящий метод (например get() для GET). Если этот шаг пропущен, Django пытается вызвать сам класс, что не даёт ожидаемый HttpResponse и приводит к ошибке.",
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
