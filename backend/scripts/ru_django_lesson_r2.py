"""Russian translation for Python: Django Asoslari, lesson order=8 (R2)."""
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

LESSON_ID = 702

TITLE_RU = "R2-Мини-проект Forms + Relationships (повторение)"

TEXT_RU = """\
<h2>R2 — Повторение уроков 5-7: мини-проект Forms + Relationships</h2>

<p>Объединив уроки 5-7, добавим возможность управлять постами, связанными с <code>Tag</code>, через админ-панель и форму: настройка admin, ModelForm и связь ManyToMany — всё вместе.</p>

<h3>Цель проекта</h3>
<ul>
<li>Модель <code>Tag</code> и её связь с <code>Post</code> через <code>ManyToManyField</code> (урок 7)</li>
<li>В <code>PostAdmin</code> должны быть настроены <code>list_display</code>, <code>search_fields</code> (урок 5)</li>
<li>Создание поста через <code>PostForm</code> (ModelForm), в форме должно быть и поле <code>teglar</code> (урок 6)</li>
<li>При создании нового поста <strong>правильно</strong> сохранять теги (особое правило ManyToMany)</li>
</ul>

<h3>Задания</h3>

<h4>Задание 1 — модель Tag и связь</h4>
<p>Создайте модель <code>Tag</code> (с полем <code>nomi</code>), добавьте в <code>Post</code> поле <code>teglar = models.ManyToManyField(Tag)</code>, выполните миграцию (как в уроке 7).</p>

<h4>Задание 2 — настройка admin</h4>
<p>В <code>PostAdmin</code> добавьте <code>list_display = ('sarlavha', 'muallif')</code> и <code>search_fields = ('sarlavha',)</code>; зарегистрируйте <code>Tag</code> простым <code>admin.site.register(Tag)</code> (как в уроке 5).</p>

<h4>Задание 3 — PostForm (ModelForm)</h4>
<p>Создайте <code>PostForm</code> с <code>fields = ['sarlavha', 'matn', 'teglar']</code> &mdash; <code>ModelForm</code> автоматически превращает и <code>ManyToManyField</code> в поле формы (как в уроке 6).</p>

<h4>Задание 4 — правильное сохранение во view</h4>
<p>Во view <code>post_yaratish</code> вызовите <code>form.save()</code> и убедитесь, что он правильно сохраняет и <code>ManyToManyField</code> (метод <code>ModelForm.save()</code> Django справляется с этим автоматически).</p>

<h3>🐛 Намеренная сложность: установка ManyToMany перед сохранением</h3>
<p>Если вы захотите создать пост <strong>вручную</strong>, не используя <code>ModelForm.save()</code>, вы можете попасть в следующую ловушку:</p>
<pre><code>post = Post(sarlavha="Test", matn="...", muallif=muallif)
post.teglar.set([tag1, tag2])  # ❌ Ошибка: post ещё не сохранён (нет id)!
post.save()

# ❌ ValueError: "&lt;Post: Test&gt;" needs to have a value for field "id"
#    before this many-to-many relationship can be used.</code></pre>
<p><strong>Результат:</strong> <code>ManyToManyField</code> сохраняется за кулисами в отдельной "промежуточной таблице", и для записи в эту таблицу <strong>у обеих сторон</strong> (в данном случае у <code>Post</code>) <code>id</code> должен <strong>уже</strong> существовать. Поэтому правильный порядок: <strong>сначала</strong> <code>post.save()</code> (присваивается id), <strong>только затем</strong> <code>post.teglar.set(...)</code>. Метод <code>ModelForm.save()</code> Django же делает это <strong>внутри в правильном порядке</strong> автоматически — поэтому использование ModelForm безопаснее ручного написания.</p>

<h3>Начальный код</h3>
<pre><code># blog/models.py
class Tag(models.Model):
    # Задание 1: добавьте поле nomi
    pass

class Post(models.Model):
    # ... существующие поля ...
    # Задание 1: добавьте teglar = models.ManyToManyField(Tag)
    pass

# blog/forms.py
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Задание 3: добавьте 'teglar' в список fields
        fields = ['sarlavha', 'matn']</code></pre>

<h3>Решение</h3>
<details>
<summary>Полное решение — сначала попробуйте сами!</summary>
<pre><code># ─── blog/models.py ───
class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─── blog/admin.py ───
from django.contrib import admin
from .models import Post, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')
    search_fields = ('sarlavha',)

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)

# ─── blog/forms.py ───
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['sarlavha', 'matn', 'teglar']

# ─── blog/views.py ───
def post_yaratish(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()   # ❗ ModelForm сначала сохраняет Post, затем правильно связывает теги
            return redirect('post-list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})</code></pre>
</details>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Всё из уроков 5-7 вместе: настройка admin, ModelForm, связь ManyToMany</li>
<li>✅ ModelForm автоматически превращает и ManyToManyField в поле формы</li>
<li>✅ Перед установкой ManyToMany объект должен быть сохранён (иметь id)</li>
<li>✅ form.save() автоматически обеспечивает правильный порядок (сначала save, затем ManyToMany)</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 2: Forms + Relationships (уроки 5-7)
# ════════════════════════════════════════════════════════════════════

# ─── blog/models.py ───
from django.db import models


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

# class Post(models.Model):
#     sarlavha = models.CharField(max_length=200)
#     matn = models.TextField()
#     muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
#     teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─── blog/admin.py ───
from django.contrib import admin


class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')
    search_fields = ('sarlavha',)

# admin.site.register(Post, PostAdmin)
# admin.site.register(Tag)

# ─── blog/forms.py ───
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        # model = Post
        fields = ['sarlavha', 'matn', 'teglar']

# ─── blog/views.py ───
# def post_yaratish(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('post-list')
#     else:
#         form = PostForm()
#     return render(request, 'blog/post_form.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# Намеренная сложность - установка ManyToMany перед сохранением (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# post = Post(sarlavha="Test", matn="...", muallif=muallif)
# post.teglar.set([tag1, tag2])  # ❌ post ещё не сохранён!
# post.save()
# ❌ ValueError: needs to have a value for field "id" before this
#    many-to-many relationship can be used.
"""

EX = {
    4117: {
        "title": "ModelForm и ManyToManyField",
        "description": "Если в списке PostForm.Meta.fields есть 'teglar' (ManyToManyField), что делает с этим полем ModelForm?",
        "hint": "ModelForm умеет работать с разными типами полей модели.",
        "explanation": "ModelForm автоматически превращает и ManyToManyField в поле формы (обычно как список множественного выбора), а form.save() сохраняет его в правильном порядке.",
    },
    4118: {
        "title": "Почему ручная установка ManyToMany даёт ошибку?",
        "description": "Почему последовательность post = Post(...); post.teglar.set([tag1, tag2]); post.save() даёт ошибку?",
        "hint": "ManyToMany сохраняется за кулисами в отдельной таблице.",
        "explanation": "post ещё не сохранён (нет id), а ManyToMany требует id у обеих сторон — поэтому сначала нужно вызвать save(), а затем teglar.set().",
    },
    4119: {
        "title": "Расположите внутренний порядок работы form.save()",
        "description": "Расположите внутренний процесс правильного сохранения тегов при вызове form.save() в PostForm(ModelForm).",
        "hint": "",
        "explanation": "",
    },
    4120: {
        "title": "Почему ModelForm безопаснее ручного написания?",
        "description": (
            "При работе с ManyToManyField (teglar) при создании поста, "
            "почему form.save() (ModelForm) безопаснее, чем ручной "
            "вызов post.teglar.set()? Объясните своими словами."
        ),
        "hint": "Что уже должно существовать у объекта для установки ManyToMany?",
        "expected_answer": "Для установки ManyToManyField у объекта (Post) уже должен существовать id, так как эта связь сохраняется за кулисами в отдельной промежуточной таблице, а для записи в эту таблицу нужен id обеих сторон. Если разработчик пишет это вручную, есть риск вызвать save() и teglar.set() в неправильном порядке (например, сначала set(), потом save()), что приводит к ошибке ValueError. Метод ModelForm.save() Django же автоматически и правильно выполняет этот порядок (сначала сохранить объект, затем установить связи ManyToMany) внутри себя, поэтому разработчик избавлен от риска допустить эту ошибку порядка.",
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
