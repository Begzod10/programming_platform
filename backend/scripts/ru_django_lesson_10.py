"""Russian translation for Python: Django Asoslari, lesson order=11 (L10, CAPSTONE)."""
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

LESSON_ID = 708

TITLE_RU = "10-CAPSTONE: Полноценный проект Django"

TEXT_RU = """\
<h2>CAPSTONE — полноценный проект блога на Django</h2>

<pre class="mermaid">
flowchart TB
    MODEL["Post: muallif (FK) + teglar (M2M)"] --> ADMIN["PostAdmin - список/поиск"]
    MODEL --> CBV["PostListView / PostDetailView / PostCreateView"]
    AUTH["LoginRequiredMixin"] --> CBV
    CBV -->|form_valid override| SETAUTHOR["muallif = request.user назначается автоматически"]
</pre>

<p>Объединим всё, что изучили в уроках 1-9 &mdash; модели и связи, admin, formы, аутентификацию, CBV &mdash; и построим настоящий небольшой проект: <strong>блог, где вошедший пользователь пишет посты</strong>. Это &mdash; финальное испытание курса.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — модель Post, автор должен назначаться автоматически</h4>
<pre><code># blog/models.py
from django.db import models
from django.contrib.auth.models import User            # ❗ готовая модель User Django

class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postlar')  # ❗ ВАЖНО: обязательное поле
    teglar = models.ManyToManyField(Tag, related_name='postlar', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha</code></pre>

<h4>БЛОК 2 — CBV: список, детали и создание (с аутентификацией)</h4>
<pre><code># blog/views.py
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Post

class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):   # ❗ доступ только у вошедшего пользователя
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']              # ❗ 'muallif' В ФОРМЕ ОТСУТСТВУЕТ - назначается вручную!
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):                          # ❗ ГЛАВНАЯ часть: назначение автора перед сохранением
        form.instance.muallif = self.request.user        # ❗ request.user - из урока 8
        return super().form_valid(form)</code></pre>

<h4>БЛОК 3 — объединение admin и urls.py</h4>
<pre><code># blog/admin.py
from django.contrib import admin
from .models import Post, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif', 'yaratilgan_vaqt')
    search_fields = ('sarlavha', 'matn')

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

# blog/urls.py
from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('yaratish/', PostCreateView.as_view(), name='post-create'),
]</code></pre>

<h3>🐛 Намеренная ошибка — забыли переопределить form_valid()</h3>
<pre><code># МЕТОД form_valid() НЕ НАПИСАН:
class PostCreateViewXato(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']   # 'muallif' нет в форме, и нигде не назначается!
    template_name = 'blog/post_form.html'

# При отправке пользователем заполненной формы:
# ❌ Ошибка: IntegrityError: NOT NULL constraint failed: blog_post.muallif_id
# (так как Post.muallif - обязательный ForeignKey, но значение не передано)</code></pre>

<p><strong>Результат:</strong> мы <strong>намеренно</strong> не оставили <code>muallif</code> в списке <code>fields</code> &mdash; потому что <strong>небезопасно</strong>, чтобы пользователь сам писал "я автор" (он мог бы написать пост от чужого имени). Вместо этого <code>muallif</code> должен <strong>автоматически</strong> браться из текущего вошедшего пользователя (<code>request.user</code>). Если <code>form_valid()</code> не переопределён, Django не находит никакого значения для <code>muallif</code> и выдаёт ошибку при сохранении в базу данных (так как это поле <code>NOT NULL</code>).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему muallif не добавлен в список fields?</h4>
<p>Если бы <code>muallif</code> был в форме, пользователь мог бы отправить через HTML <strong>любой</strong> ID автора &mdash; это позволило бы писать посты от чужого имени (уязвимость безопасности). Поэтому <code>muallif</code> никогда не должен быть полем, вводимым пользователем &mdash; он назначается <strong>на сервере</strong>, из надёжного источника (<code>request.user</code>).</p>

<h4>2. Зачем переопределяется form_valid()?</h4>
<p><code>form_valid()</code> &mdash; метод, вызываемый <strong>после успешной</strong> валидации формы, но <strong>перед сохранением</strong> объекта. Переопределив его и написав <code>form.instance.muallif = self.request.user</code>, можно добавить объекту дополнительное значение (отсутствующее в форме) перед сохранением.</p>

<h4>3. Как работают вместе LoginRequiredMixin и form_valid()?</h4>
<p><code>LoginRequiredMixin</code> блокирует сам доступ к view (перенаправляет на страницу входа), если пользователь <strong>вообще не вошёл</strong>. <code>self.request.user</code> внутри <code>form_valid()</code> же, так как уже подтверждено, что пользователь <strong>вошёл</strong>, всегда даёт реальный объект <code>User</code> &mdash; вместе они дают безопасный и правильный результат.</p>

<h4>4. Зачем добавлен blank=True к полю teglar?</h4>
<p><code>ManyToManyField(..., blank=True)</code> означает, что это поле <strong>не обязательно заполнять</strong> в форме (пост может быть создан и без тегов). Это отличается от <code>null=True</code> &mdash; для <code>ManyToMany</code> <code>null=True</code> обычно бессмысленен, так как связь хранится в отдельной таблице.</p>

<h4>5. Почему этот проект считается финальным испытанием уроков 1-9?</h4>
<p>Здесь модель и связи <code>ForeignKey</code>/<code>ManyToMany</code> (уроки 4, 7), настройка admin (урок 5), форма и её ограничения (урок 6), аутентификация и <code>request.user</code> (урок 8), CBV и его переопределение (урок 9) &mdash; всё объединяется для решения <strong>одного реального требования безопасности</strong> (пользователь не может писать посты от чужого имени).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Важные для безопасности поля (например muallif) не должны добавляться в форму, а назначаться на сервере</li>
<li>✅ Переопределяя <code>form_valid()</code>, можно добавить объекту дополнительное значение перед сохранением</li>
<li>✅ <code>LoginRequiredMixin</code> + <code>form_valid()</code> вместе дают безопасный паттерн "текущий пользователь — автор"</li>
<li>✅ <code>ManyToManyField(blank=True)</code> — необязательная в форме связь</li>
<li>✅ В реальном проекте models, admin, forms, auth, CBV работают в тесной связи друг с другом</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 10 (CAPSTONE): Полноценный проект блога на Django
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/models.py
# ─────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar', blank=True)
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) blog/views.py - CBV + auth + form_valid()
# ─────────────────────────────────────────────────────────────────────

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class PostListView(ListView):
    model = Post
    context_object_name = 'postlar'
    template_name = 'blog/post_list.html'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['sarlavha', 'matn', 'teglar']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.muallif = self.request.user
        return super().form_valid(form)

# ─────────────────────────────────────────────────────────────────────
# 3) blog/admin.py и urls.py (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class PostAdmin(admin.ModelAdmin):
#     list_display = ('sarlavha', 'muallif', 'yaratilgan_vaqt')
#     search_fields = ('sarlavha', 'matn')
#
# urlpatterns = [
#     path('', PostListView.as_view(), name='post-list'),
#     path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
#     path('yaratish/', PostCreateView.as_view(), name='post-create'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - не написан form_valid() (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class PostCreateViewXato(LoginRequiredMixin, CreateView):
#     model = Post
#     fields = ['sarlavha', 'matn', 'teglar']
#     template_name = 'blog/post_form.html'
#     # form_valid() НЕТ - muallif нигде не назначается!
# ❌ IntegrityError: NOT NULL constraint failed: blog_post.muallif_id
"""

EX = {
    4146: {
        "title": "Почему muallif не добавлен в список fields?",
        "description": "Почему в PostCreateView.fields = ['sarlavha', 'matn', 'teglar'] НЕТ 'muallif'?",
        "hint": "Какая опасность возникла бы, если бы пользователь сам отправлял ID автора?",
        "explanation": "Если бы muallif был в форме, пользователь мог бы отправить любой ID автора и написать пост от чужого имени. Поэтому muallif безопасно назначается на сервере через request.user.",
    },
    4147: {
        "title": "Когда вызывается form_valid()?",
        "description": "Когда в CreateView вызывается метод form_valid()?",
        "hint": "Это \"последний этап\" перед сохранением объекта.",
        "explanation": "form_valid() вызывается после успешной валидации формы, но перед сохранением объекта в базу данных — здесь можно назначить дополнительные значения (например автора).",
    },
    4148: {
        "title": "Расположите процесс создания поста",
        "description": "Расположите полный процесс создания нового поста вошедшим пользователем через PostCreateView.",
        "hint": "",
        "explanation": "",
    },
    4149: {
        "title": "Сделать поле ManyToMany необязательным в форме",
        "description": "Напишите параметр, указывающий, что поле ManyToManyField не обязательно заполнять в форме (например: blank=True).",
        "hint": "",
        "expected_answer": "blank=True",
    },
    4150: {
        "title": "Почему без form_valid() возникает IntegrityError?",
        "description": (
            "В PostCreateViewXato метод form_valid() не написан, и в "
            "списке fields нет 'muallif'. Почему при отправке "
            "пользователем заполненной формы выдаётся ошибка \"NOT NULL "
            "constraint failed: blog_post.muallif_id\"? Объясните "
            "своими словами."
        ),
        "hint": "Если никто не передаёт значение muallif, каким оно останется, и какое ограничение есть у этого столбца в базе?",
        "expected_answer": "В модели Post поле muallif объявлено как обязательный (NOT NULL) ForeignKey, но так как его нет в списке fields, форма никогда не передаёт для него значение. Если form_valid() не переопределён, никто (ни форма, ни код) не присваивает полю muallif никакого значения. Когда CreateView пытается сохранить объект Post в базу данных, столбец muallif_id остаётся пустым (None), но так как этот столбец объявлен как NOT NULL, база данных отклоняет эту запись и выдаёт ошибку IntegrityError.",
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
