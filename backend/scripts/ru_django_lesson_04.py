"""Russian translation for Python: Django Asoslari, lesson order=3 (L4)."""
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

LESSON_ID = 692

TITLE_RU = "4-Основы Models и ORM"

TEXT_RU = """\
<h2>Models и основы ORM — работа с базой данных без написания SQL</h2>

<pre class="mermaid">
flowchart LR
    MODEL["class Post(models.Model)"] --> MAKEM["makemigrations — записывает изменение в файл"]
    MAKEM --> MIGRATE["migrate — создаёт/обновляет реальную таблицу"]
    MODEL --> QS["Post.objects.all() / .filter() / .get()"]
</pre>

<p>На Flask вы обычно использовали SQLAlchemy. У Django есть <strong>собственный ORM</strong> &mdash; он тоже позволяет описывать таблицу базы данных через Python-класс и отправлять запросы без написания SQL, но синтаксис немного отличается.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — первая модель</h4>
<pre><code># blog/models.py
from django.db import models

class Post(models.Model):                        # ❗ каждая модель - таблица
    sarlavha = models.CharField(max_length=200)   # ❗ VARCHAR(200)
    matn = models.TextField()                     # ❗ TEXT
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)  # ❗ заполняется автоматически при создании
    nashr_qilingan = models.BooleanField(default=False)

    def __str__(self):
        return self.sarlavha                      # ❗ для красивого отображения в админке и shell</code></pre>

<h4>БЛОК 2 — миграции</h4>
<pre><code># В терминале:
python manage.py makemigrations blog   # ❗ создаёт "план" (файл миграции), соответствующий модели Post
python manage.py migrate                # ❗ выполняет этот план в реальной базе данных (создаёт таблицу)

# Каждый раз, когда меняется models.py (даже добавление нового поля),
# нужно СНОВА выполнить makemigrations + migrate!</code></pre>

<h4>БЛОК 3 — QuerySet: получение данных</h4>
<pre><code># В Django shell (python manage.py shell) или внутри view:
from blog.models import Post

barcha_postlar = Post.objects.all()                     # ❗ все
nashr_qilingan = Post.objects.filter(nashr_qilingan=True)  # ❗ МНОЖЕСТВО результатов, соответствующих условию
bitta_post = Post.objects.get(id=1)                      # ❗ РОВНО ОДИН результат (ошибка, если не найдено/найдено 2)

yangi_post = Post.objects.create(                        # ❗ создание и сохранение в одну строку
    sarlavha="Birinchi post",
    matn="Bu mening birinchi Django postim",
)</code></pre>

<h3>🐛 Намеренная ошибка — забыли выполнить миграцию после изменения models.py</h3>
<pre><code># В models.py добавлено новое поле:
class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif_ismi = models.CharField(max_length=100)  # ❗ НОВОЕ поле

# Но makemigrations/migrate НЕ ВЫПОЛНЕНЫ, и во view:
Post.objects.create(sarlavha="Test", matn="...", muallif_ismi="Olim")
# ❌ Ошибка: OperationalError: no such column: blog_post.muallif_ismi
# (или другое сообщение в зависимости от базы данных)</code></pre>

<p><strong>Результат:</strong> модель Django (Python-класс) и реальная таблица в базе данных &mdash; <strong>две отдельные</strong> вещи. Изменение <code>models.py</code> <strong>никогда</strong> не изменяет реальную таблицу автоматически &mdash; для этого <strong>обязательно</strong> нужна последовательность <code>makemigrations</code> (записать изменение как "план") и <code>migrate</code> (выполнить план). Если пропустить этот шаг, код и реальная база данных расходятся, и возникает ошибка.</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое модель?</h4>
<p>Каждый Python-класс, унаследованный от <code>models.Model</code>, представляет одну таблицу в базе данных. Каждое свойство класса (<code>CharField</code>, <code>TextField</code> и т.д.) соответствует одному столбцу таблицы.</p>

<h4>2. Разница между makemigrations и migrate</h4>
<p><code>makemigrations</code> записывает изменения в <code>models.py</code> в виде <strong>файла</strong> (миграции), но ещё не трогает базу данных. <code>migrate</code> выполняет уже записанные файлы миграций в <strong>реальной</strong> базе данных (создаёт/изменяет таблицу). Обе команды должны выполняться последовательно каждый раз при изменении модели.</p>

<h4>3. Разница между filter() и get()</h4>
<p><code>filter()</code> возвращает <strong>несколько</strong> (или ноль) результатов, соответствующих условию, в виде QuerySet, никогда не выдавая ошибку. <code>get()</code> ожидает <strong>ровно один</strong> результат: если ничего не найдено — ошибка <code>DoesNotExist</code>, если найдено несколько — ошибка <code>MultipleObjectsReturned</code>.</p>

<h4>4. Что такое objects?</h4>
<p><code>Post.objects</code> &mdash; "менеджер", автоматически добавляемый Django к каждой модели &mdash; через него доступны методы вроде <code>all()</code>, <code>filter()</code>, <code>get()</code>, <code>create()</code>. Это "точка входа" в ORM.</p>

<h4>5. Почему без миграции возникает ошибка?</h4>
<p>Реальная структура таблицы в базе данных изменяется <strong>только</strong> через применённые миграции. Добавление нового поля в <code>models.py</code> &mdash; это лишь изменение Python-кода, которое ещё "не дошло" до базы данных. Поэтому при попытке записи в новое поле база данных ещё <strong>не знает</strong> о таком столбце и выдаёт ошибку.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Класс, унаследованный от <code>models.Model</code> — таблица базы данных</li>
<li>✅ <code>makemigrations</code> превращает изменение в файл, <code>migrate</code> выполняет его в базе</li>
<li>✅ <code>filter()</code> — много результатов (без ошибки), <code>get()</code> — ровно один результат (может выдать ошибку)</li>
<li>✅ <code>Model.objects</code> — точка входа в ORM (менеджер)</li>
<li>✅ Изменение models.py без миграции не влияет на реальную базу данных</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 4: Models и основы ORM
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/models.py - первая модель
# ─────────────────────────────────────────────────────────────────────

from django.db import models


class Post(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    nashr_qilingan = models.BooleanField(default=False)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) Миграции (команды терминала, в комментарии)
# ─────────────────────────────────────────────────────────────────────

# python manage.py makemigrations blog
# python manage.py migrate

# ─────────────────────────────────────────────────────────────────────
# 3) QuerySet - получение данных
# ─────────────────────────────────────────────────────────────────────

# from blog.models import Post
#
# barcha_postlar = Post.objects.all()
# nashr_qilingan = Post.objects.filter(nashr_qilingan=True)
# bitta_post = Post.objects.get(id=1)
#
# yangi_post = Post.objects.create(
#     sarlavha="Birinchi post",
#     matn="Bu mening birinchi Django postim",
# )

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли миграцию (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class Post(models.Model):
#     ...
#     muallif_ismi = models.CharField(max_length=100)  # новое поле
#
# # makemigrations/migrate НЕ ВЫПОЛНЕНЫ, затем:
# Post.objects.create(sarlavha="Test", matn="...", muallif_ismi="Olim")
# ❌ OperationalError: no such column: blog_post.muallif_ismi
"""

EX = {
    4070: {
        "title": "Что представляет модель?",
        "description": "Что представляет Python-класс, унаследованный от models.Model в Django?",
        "hint": "Каждое свойство (CharField, TextField) соответствует столбцу.",
        "explanation": "Каждый класс, унаследованный от models.Model, представляет одну таблицу базы данных, а его свойства соответствуют столбцам таблицы.",
    },
    4071: {
        "title": "Разница между makemigrations и migrate",
        "description": "В чём разница между командами makemigrations и migrate?",
        "hint": "Одна \"записывает план\", другая \"выполняет план\".",
        "explanation": "makemigrations записывает изменения из models.py в файл миграции, migrate выполняет этот файл в реальной базе данных.",
    },
    4072: {
        "title": "Расположите процесс создания нового поста",
        "description": "Расположите процесс при вызове Post.objects.create(sarlavha=\"...\", matn=\"...\").",
        "hint": "",
        "explanation": "",
    },
    4073: {
        "title": "Метод, ожидающий ровно один результат",
        "description": "Какой метод QuerySet ожидает ровно один результат и выдаёт ошибку, если не найдено или найдено несколько? (напишите название)",
        "hint": "В отличие от filter(), этот метод предназначен только для одного.",
        "expected_answer": "get",
    },
    4074: {
        "title": "Почему без миграции возникает OperationalError?",
        "description": (
            "В модель Post добавлено новое поле muallif_ismi, но "
            "makemigrations/migrate не были выполнены. Почему при "
            "последующем вызове Post.objects.create(..., "
            "muallif_ismi=\"Olim\") выдаётся ошибка \"no such column\"? "
            "Объясните своими словами."
        ),
        "hint": "Изменение в Python-классе автоматически влияет на реальную базу данных?",
        "expected_answer": "Python-класс (models.py) и реальная таблица в базе данных — две отдельные вещи. Добавление нового поля в models.py просто изменяет Python-код, но это изменение ещё не \"дошло\" до реальной таблицы базы данных — для этого обязательно нужно выполнить makemigrations (записать изменение как план) и migrate (выполнить план в базе). Так как этот шаг не выполнен, в реальной таблице столбца muallif_ismi ещё не существует, поэтому база данных не может найти такой столбец и выдаёт ошибку.",
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
