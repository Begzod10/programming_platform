"""Russian translation for Python: Django Asoslari, lesson order=5 (L5)."""
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

LESSON_ID = 696

TITLE_RU = "5-Админ-панель Django"

TEXT_RU = """\
<h2>Админ-панель Django — готовая панель управления за несколько строк</h2>

<pre class="mermaid">
flowchart LR
    MODEL["class Post(models.Model)"] --> ADMIN["admin.py: admin.site.register(Post)"]
    ADMIN --> PANEL["/admin/ — автоматический CRUD-интерфейс"]
    SUPER["createsuperuser"] --> PANEL
</pre>

<p>На Flask, если требовалась админ-панель, её приходилось писать <strong>самостоятельно</strong> (или с помощью дополнительной библиотеки вроде Flask-Admin). В Django же админ-панель <strong>встроена и готова</strong> &mdash; всего несколькими строками кода вы получаете для модели полноценный CRUD-интерфейс.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — создание суперпользователя и регистрация модели</h4>
<pre><code># В терминале (один раз):
python manage.py createsuperuser   # ❗ создаёт пользователя для входа в админ-панель

# blog/admin.py
from django.contrib import admin
from .models import Post

admin.site.register(Post)   # ❗ вот эта одна строка создаёт для Post полноценный CRUD-интерфейс!

# Теперь на /admin/ можно просматривать, добавлять, изменять, удалять Post'ы</code></pre>

<h4>БЛОК 2 — настройка через ModelAdmin</h4>
<pre><code># blog/admin.py
from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt', 'nashr_qilingan')  # ❗ столбцы, видимые в списке
    search_fields = ('sarlavha', 'matn')                              # ❗ поля, по которым идёт поиск в строке поиска
    list_filter = ('nashr_qilingan',)                                 # ❗ панель фильтров справа

admin.site.register(Post, PostAdmin)   # ❗ теперь регистрируется вместе с ModelAdmin</code></pre>

<h4>БЛОК 3 — синтаксис декоратора (более короткая запись)</h4>
<pre><code># То же самое, но через декоратор
from django.contrib import admin
from .models import Post

@admin.register(Post)              # ❗ тот же результат, что и admin.site.register(Post, PostAdmin)
class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt')
    search_fields = ('sarlavha',)</code></pre>

<h3>🐛 Намеренная ошибка — указание несуществующего поля в list_display</h3>
<pre><code>class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif')  # ❌ в модели Post НЕТ поля 'muallif'

admin.site.register(Post, PostAdmin)

# При открытии /admin/blog/post/:
# ❌ Ошибка: PostAdmin.list_display[1], 'muallif' is not a callable, an
#    attribute of 'PostAdmin', or an attribute or method on 'Post'.</code></pre>

<p><strong>Результат:</strong> каждое имя в <code>list_display</code> <strong>обязательно</strong> должно быть либо реальным полем модели, либо её методом, либо методом <code>PostAdmin</code>. Если указано несуществующее в модели имя, Django выдаёт ошибку <strong>при попытке</strong> открыть админ-панель (не при запуске сервера) &mdash; это похоже на обычную Python-ошибку <code>AttributeError</code>, только в контексте админ-панели.</p>

<h3>Теперь объясним</h3>

<h4>1. Что делает admin.site.register()?</h4>
<p>Эта одна строка кода автоматически создаёт для заданной модели <strong>полноценный CRUD-интерфейс</strong> (просмотр списка, добавление, редактирование, удаление) &mdash; без написания какого-либо HTML, view или формы.</p>

<h4>2. Зачем нужен ModelAdmin?</h4>
<p>Стандартный <code>admin.site.register(Post)</code> даёт очень простое отображение. Через класс <code>ModelAdmin</code> можно <strong>настроить</strong> это отображение: какие столбцы показывать в списке (<code>list_display</code>), по каким полям разрешить поиск (<code>search_fields</code>), какие фильтры показать (<code>list_filter</code>).</p>

<h4>3. Зачем нужен createsuperuser?</h4>
<p>Админ-панель &mdash; защищённое место, доступное только <strong>прошедшим аутентификацию</strong> (и обычно с <code>is_staff=True</code>/<code>is_superuser=True</code>) пользователям. Команда <code>createsuperuser</code> создаёт именно такого полноправного пользователя.</p>

<h4>4. Разница между декоратором (<code>@admin.register</code>) и обычным <code>admin.site.register()</code></h4>
<p>Оба приводят к одному и тому же результату &mdash; разница лишь в <strong>стиле записи</strong>: декоратор регистрирует класс одновременно с его объявлением, это более "Pythonic" стиль, чаще используемый в современных проектах Django.</p>

<h4>5. Почему несуществующее поле в list_display даёт ошибку?</h4>
<p>При построении админ-панели Django <strong>ищет</strong> каждое имя из <code>list_display</code> внутри модели (или методов <code>ModelAdmin</code>). Если такое имя <strong>нигде</strong> не найдено (ни как поле модели, ни как метод), Django считает это ошибкой, так как не знает, <strong>что показывать</strong> в этом столбце списка.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>admin.site.register(Model)</code> — создаёт полноценный CRUD-интерфейс одной строкой</li>
<li>✅ <code>ModelAdmin</code> — настраивает отображение админки через <code>list_display</code>, <code>search_fields</code>, <code>list_filter</code></li>
<li>✅ <code>createsuperuser</code> — создаёт полноправного пользователя для входа в админ-панель</li>
<li>✅ <code>@admin.register(Model)</code> — форма декоратора для <code>admin.site.register()</code></li>
<li>✅ В <code>list_display</code> можно использовать только реально существующие в модели/ModelAdmin имена</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 5: Админ-панель Django
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) Создание суперпользователя (команда терминала, в комментарии)
# ─────────────────────────────────────────────────────────────────────

# python manage.py createsuperuser

# ─────────────────────────────────────────────────────────────────────
# 2) blog/admin.py - простая регистрация
# ─────────────────────────────────────────────────────────────────────

from django.contrib import admin
from .models import Post

# admin.site.register(Post)

# ─────────────────────────────────────────────────────────────────────
# 3) Настройка через ModelAdmin
# ─────────────────────────────────────────────────────────────────────


class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'yaratilgan_vaqt', 'nashr_qilingan')
    search_fields = ('sarlavha', 'matn')
    list_filter = ('nashr_qilingan',)


admin.site.register(Post, PostAdmin)

# ─────────────────────────────────────────────────────────────────────
# 4) Синтаксис декоратора (в комментарии, тот же результат)
# ─────────────────────────────────────────────────────────────────────

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     list_display = ('sarlavha', 'yaratilgan_vaqt')
#     search_fields = ('sarlavha',)

# ─────────────────────────────────────────────────────────────────────
# 5) Намеренная ошибка - несуществующее поле (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class PostAdminXato(admin.ModelAdmin):
#     list_display = ('sarlavha', 'muallif')  # ❌ в Post нет 'muallif'
# ❌ 'muallif' is not a callable, an attribute of 'PostAdminXato', or
#    an attribute or method on 'Post'.
"""

EX = {
    4088: {
        "title": "Что делает admin.site.register()?",
        "description": "Что делает строка admin.site.register(Post)?",
        "hint": "Это одна строка кода — но она делает многое.",
        "explanation": "admin.site.register(Post) автоматически создаёт для указанной модели полноценный CRUD-интерфейс, включающий просмотр списка, добавление, редактирование и удаление.",
    },
    4089: {
        "title": "Для чего используется search_fields?",
        "description": "Что делает search_fields = ('sarlavha', 'matn') в ModelAdmin?",
        "hint": "Это относится к строке поиска в верхней части админ-панели.",
        "explanation": "search_fields добавляет в админ-панель строку поиска и позволяет искать по указанным полям (sarlavha, matn).",
    },
    4090: {
        "title": "Расположите процесс добавления поста через админ-панель",
        "description": "Расположите процесс добавления администратором нового Post через /admin/.",
        "hint": "",
        "explanation": "",
    },
    4091: {
        "title": "Команда для создания пользователя для входа в админ-панель",
        "description": "Напишите команду, создающую полноправного пользователя для входа в админ-панель.",
        "hint": "Запускается через manage.py.",
        "expected_answer": "python manage.py createsuperuser",
    },
    4092: {
        "title": "Почему несуществующее поле в list_display даёт ошибку?",
        "description": (
            "Указано PostAdmin.list_display = ('sarlavha', 'muallif'), "
            "но в модели Post нет поля 'muallif'. Почему при открытии "
            "/admin/blog/post/ Django выдаёт ошибку? Объясните своими "
            "словами."
        ),
        "hint": "Где Django ищет имя из list_display?",
        "expected_answer": "При построении админ-панели Django ищет каждое имя из списка list_display внутри модели (или методов ModelAdmin), потому что для каждого столбца в списке ему нужно точно знать, какое значение показывать. Имя 'muallif' не существует ни как поле модели Post, ни как метод PostAdmin, поэтому Django не может найти для этого имени никакого значения и выдаёт ошибку при попытке открыть страницу админки — это похоже на обычную Python-ошибку AttributeError, только возникающую в контексте админ-панели.",
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
