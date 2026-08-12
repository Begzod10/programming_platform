"""Russian translation for Python: Django Asoslari, lesson order=7 (L7)."""
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

LESSON_ID = 700

TITLE_RU = "7-ORM глубже: querysets и связи"

TEXT_RU = """\
<h2>ORM глубже — связи между таблицами</h2>

<pre class="mermaid">
flowchart LR
    AUTHOR["Author"] -->|ForeignKey - один ко многим| POST["Post"]
    POST -->|ManyToMany - многие ко многим| TAG["Tag"]
    POST -->|post.muallif| AUTHOR
    AUTHOR -->|muallif.post_set / muallif.postlar| POST
</pre>

<p>В реальных проектах таблицы <strong>связаны</strong> друг с другом — у одного автора много постов, у одного поста много тегов. Django ORM выражает эти связи через <code>ForeignKey</code> и <code>ManyToManyField</code>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — ForeignKey (связь один ко многим)</h4>
<pre><code># blog/models.py
from django.db import models

class Author(models.Model):
    ism = models.CharField(max_length=100)

    def __str__(self):
        return self.ism

class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(                    # ❗ у одного автора МОЖЕТ быть много постов
        Author,
        on_delete=models.CASCADE,                    # ❗ при удалении автора его посты ТОЖЕ удаляются
        related_name='postlar',                       # ❗ имя для обращения с обратной стороны
    )

# Использование:
muallif = Author.objects.get(id=1)
muallif.postlar.all()          # ❗ через related_name - все посты этого автора
post = Post.objects.get(id=1)
post.muallif.ism               # ❗ напрямую - автор поста</code></pre>

<h4>БЛОК 2 — ManyToMany (связь многие ко многим)</h4>
<pre><code># blog/models.py
class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi

class Post(models.Model):
    # ... другие поля ...
    teglar = models.ManyToManyField(Tag, related_name='postlar')  # ❗ у одного поста МНОГО тегов, у одного тега МНОГО постов

# Использование:
post = Post.objects.get(id=1)
post.teglar.add(tag1, tag2)     # ❗ добавление тега
post.teglar.all()               # ❗ все теги этого поста

tag = Tag.objects.get(nomi='Django')
tag.postlar.all()               # ❗ через related_name - все посты с этим тегом</code></pre>

<h4>БЛОК 3 — filter chaining и select_related</h4>
<pre><code># Фильтрация цепочкой - поиск по полю связанной таблицы
Post.objects.filter(muallif__ism='Olim')              # ❗ '__' - "переход" к связанной таблице
Post.objects.filter(teglar__nomi='Django')             # ❗ работает и через ManyToMany

# select_related - предотвращает проблему N+1 (делает SQL JOIN)
postlar = Post.objects.select_related('muallif').all()  # ❗ одним запросом получает и автора
for post in postlar:
    print(post.muallif.ism)     # ✅ на каждой итерации НЕТ нового запроса</code></pre>

<h3>🐛 Намеренная ошибка — проблема N+1 без select_related</h3>
<pre><code># Если select_related НЕ ИСПОЛЬЗОВАН:
postlar = Post.objects.all()          # 1 запрос - получает все посты
for post in postlar:
    print(post.muallif.ism)           # ❌ ОТДЕЛЬНЫЙ запрос для КАЖДОГО поста!

# В результате: при 100 постах - 1 (посты) + 100 (автор для каждого) = 101 SQL-запрос!
# Это называется "проблема N+1" и ЗАМЕДЛЯЕТ сайт на большой базе данных</code></pre>

<p><strong>Результат:</strong> при каждом обращении к полю <code>ForeignKey</code> (<code>post.muallif</code>), если заранее не выполнен <code>select_related</code>, Django отправляет <strong>отдельный SQL-запрос</strong>. Для 100 постов в цикле это приводит к 100 дополнительным запросам — это называется "проблема N+1" и <strong>серьёзно</strong> влияет на производительность. <code>select_related</code> же получает всё <strong>одним</strong> запросом через SQL <code>JOIN</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Когда используется ForeignKey?</h4>
<p><code>ForeignKey</code> &mdash; для связи "один ко многим" (one-to-many): у одного <code>Author</code> может быть много <code>Post</code>, но у каждого <code>Post</code> только один <code>Author</code>. <code>on_delete=models.CASCADE</code> означает, что при удалении автора все его посты тоже удаляются автоматически.</p>

<h4>2. Когда используется ManyToManyField?</h4>
<p><code>ManyToManyField</code> &mdash; для связи "многие ко многим" (many-to-many): один <code>Post</code> может относиться к нескольким <code>Tag</code>, и один <code>Tag</code> может относиться к нескольким <code>Post</code>. Django для этого создаёт отдельную "промежуточную таблицу" за кулисами.</p>

<h4>3. Зачем нужен related_name?</h4>
<p><code>related_name</code> даёт имя для обращения с <strong>обратной стороны</strong> связи (например <code>muallif.postlar.all()</code>). Если <code>related_name</code> не указан, Django по умолчанию даёт автоматическое имя вроде <code>post_set</code>, но указание явного имени облегчает чтение кода.</p>

<h4>4. Как работает filter chaining (<code>__</code>)?</h4>
<p>Двойное подчёркивание (<code>__</code>) в <code>filter(muallif__ism='Olim')</code> говорит Django ORM "перейти к связанной таблице и фильтровать по полю там". Это выполняет SQL <code>JOIN</code> без написания его вручную.</p>

<h4>5. Зачем нужен select_related?</h4>
<p>По умолчанию обращение к полю <code>ForeignKey</code> каждый раз отправляет <strong>отдельный</strong> SQL-запрос (ленивая загрузка). <code>select_related('muallif')</code> указывает Django заранее получить связанные данные через SQL <code>JOIN</code> <strong>одним</strong> запросом — это предотвращает проблему N+1 и значительно ускоряет работу.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>ForeignKey</code> — связь "один ко многим", <code>on_delete</code> определяет, что происходит при удалении автора</li>
<li>✅ <code>ManyToManyField</code> — связь "многие ко многим" (например пост-тег)</li>
<li>✅ <code>related_name</code> — имя для обращения с обратной стороны связи</li>
<li>✅ <code>filter(связь__поле=...)</code> — фильтрация по связанной таблице</li>
<li>✅ <code>select_related()</code> — предотвращает проблему N+1, получая данные одним запросом через SQL JOIN</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 7: ORM глубже - querysets и связи
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) ForeignKey (один ко многим)
# ─────────────────────────────────────────────────────────────────────

from django.db import models


class Author(models.Model):
    ism = models.CharField(max_length=100)

    def __str__(self):
        return self.ism


class Tag(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self):
        return self.nomi


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='postlar')
    teglar = models.ManyToManyField(Tag, related_name='postlar')

# ─────────────────────────────────────────────────────────────────────
# 2) Использование (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# muallif = Author.objects.get(id=1)
# muallif.postlar.all()
# post = Post.objects.get(id=1)
# post.muallif.ism
#
# post.teglar.add(tag1, tag2)
# post.teglar.all()

# ─────────────────────────────────────────────────────────────────────
# 3) Filter chaining и select_related
# ─────────────────────────────────────────────────────────────────────

# Post.objects.filter(muallif__ism='Olim')
# Post.objects.filter(teglar__nomi='Django')
#
# postlar = Post.objects.select_related('muallif').all()
# for post in postlar:
#     print(post.muallif.ism)

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - проблема N+1 без select_related (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# postlar = Post.objects.all()          # 1 запрос
# for post in postlar:
#     print(post.muallif.ism)           # ❌ отдельный запрос для каждого поста!
# # 100 постов = 101 SQL-запрос (проблема N+1)
"""

EX = {
    4108: {
        "title": "Когда используется ForeignKey?",
        "description": "Для какого типа связи используется ForeignKey?",
        "hint": "У одного автора может быть много постов, но каждый пост относится к одному автору.",
        "explanation": "ForeignKey используется для связи \"один ко многим\": у одного Author может быть много Post, но у каждого Post только один Author.",
    },
    4109: {
        "title": "Для чего используется select_related?",
        "description": "Для чего используется Post.objects.select_related('muallif').all()?",
        "hint": "Это используется для ускорения работы.",
        "explanation": "select_related() получает связанные данные (например автора) одним запросом через SQL JOIN, предотвращая отправку отдельного запроса для каждого поста (проблема N+1).",
    },
    4110: {
        "title": "Расположите процесс возникновения проблемы N+1",
        "description": "Расположите, как возникает проблема N+1 в цикле Post.objects.all() без использования select_related.",
        "hint": "",
        "explanation": "",
    },
    4111: {
        "title": "Имя для обращения с обратной стороны связи",
        "description": "Напишите название параметра, используемого для обращения с обратной стороны связи ForeignKey или ManyToManyField (например muallif.postlar.all()).",
        "hint": "",
        "expected_answer": "related_name",
    },
    4112: {
        "title": "Почему без select_related возникает проблема N+1?",
        "description": (
            "Если вызвать Post.objects.all(), а затем в цикле для "
            "каждого поста прочитать post.muallif.ism (без "
            "select_related), почему это приводит к 101 SQL-запросу для "
            "100 постов? Объясните своими словами."
        ),
        "hint": "Когда Django отправляет SQL-запрос при обращении к полю ForeignKey — заранее или каждый раз отдельно?",
        "expected_answer": "По умолчанию при каждом обращении к полю ForeignKey (post.muallif) Django работает по принципу \"ленивой загрузки\" (lazy loading) — то есть получает связанные данные не заранее, а отдельным SQL-запросом именно в момент обращения к этому полю. Post.objects.all() получает все посты одним запросом, но когда в цикле для каждого поста вызывается post.muallif.ism, для каждого отправляется ОТДЕЛЬНЫЙ запрос. Для 100 постов это 100 дополнительных запросов, итого 1 (посты) + 100 (автор для каждого) = 101 SQL-запрос — именно поэтому это называется \"проблема N+1\" и заметно замедляет сайт на большой базе данных.",
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
