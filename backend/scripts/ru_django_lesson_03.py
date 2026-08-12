"""Russian translation for Python: Django Asoslari, lesson order=2 (L3)."""
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

LESSON_ID = 690

TITLE_RU = "3-Шаблоны и язык шаблонов"

TEXT_RU = """\
<h2>Templates и язык шаблонов — от Model до HTML</h2>

<pre class="mermaid">
flowchart LR
    VIEW["render(request, 'post_list.html', context)"] --> TPL["templates/post_list.html"]
    BASE["base.html"] -->|extends| TPL
    TPL -->|block content| BASE
</pre>

<p>Чтобы вывести данные, полученные во view, в виде <strong>видимого пользователю HTML</strong>, Django использует собственный <strong>Django Template Language (DTL)</strong> &mdash; он очень похож на Jinja2 (используемый во Flask), но с некоторыми отличиями.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — render() и простой шаблон</h4>
<pre><code># blog/views.py
from django.shortcuts import render

def postlar_royxati(request):
    postlar = ["Birinchi post", "Ikkinchi post", "Uchinchi post"]
    return render(request, 'blog/post_list.html', {'postlar': postlar})  # ❗ context - dict

# templates/blog/post_list.html
&lt;h1&gt;Postlar&lt;/h1&gt;
&lt;ul&gt;
{% for post in postlar %}                 {# ❗ {% %} - для логики (tag) #}
  &lt;li&gt;{{ post }}&lt;/li&gt;                     {# ❗ {{ }} - для вывода значения #}
{% empty %}
  &lt;li&gt;Postlar yo'q&lt;/li&gt;
{% endfor %}
&lt;/ul&gt;</code></pre>

<h4>БЛОК 2 — наследование шаблонов (extends/block)</h4>
<pre><code>{# templates/base.html - общий "скелет" для всех страниц #}
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;&lt;title&gt;{% block title %}Mening Blogim{% endblock %}&lt;/title&gt;&lt;/head&gt;
&lt;body&gt;
  &lt;nav&gt;Bosh sahifa | Blog&lt;/nav&gt;
  {% block content %}
  {% endblock %}
&lt;/body&gt;
&lt;/html&gt;

{# templates/blog/post_list.html #}
{% extends 'base.html' %}                  {# ❗ наследуется от base.html #}

{% block title %}Postlar ro'yxati{% endblock %}

{% block content %}                        {# ❗ ЗАПОЛНЯЕТ пустое место из base.html #}
  &lt;h1&gt;Postlar&lt;/h1&gt;
  &lt;ul&gt;
  {% for post in postlar %}
    &lt;li&gt;{{ post }}&lt;/li&gt;
  {% endfor %}
  &lt;/ul&gt;
{% endblock %}</code></pre>

<h4>БЛОК 3 — фильтры и статические файлы</h4>
<pre><code>{# Фильтры - изменяют значение через "|" #}
&lt;p&gt;{{ post.sarlavha|upper }}&lt;/p&gt;         {# переводит в верхний регистр #}
&lt;p&gt;{{ post.matn|truncatewords:10 }}&lt;/p&gt; {# показывает только 10 слов #}
&lt;p&gt;{{ postlar|length }}&lt;/p&gt;              {# длина списка #}

{# Для статических файлов (CSS, JS, изображения) #}
{% load static %}                          {# ❗ всегда обязательно пишется в начале файла #}
&lt;link rel="stylesheet" href="{% static 'blog/style.css' %}"&gt;</code></pre>

<h3>🐛 Намеренная ошибка — забыли {% load static %}</h3>
<pre><code>{# Без {% load static %}: #}
&lt;link rel="stylesheet" href="{% static 'blog/style.css' %}"&gt;
{# ❌ Ошибка: Invalid block tag on line N: 'static'. Did you forget to
   register or load this tag? #}</code></pre>

<p><strong>Результат:</strong> некоторые теги в Django Template Language (например <code>{% static %}</code>) не являются <strong>встроенными по умолчанию</strong> &mdash; они поставляются как отдельная "библиотека" и должны быть <strong>явно загружены</strong> через <code>{% load static %}</code>. Если эта строка не написана, Django <strong>вообще не распознаёт</strong> тег <code>{% static %}</code> и выдаёт ошибку &mdash; это похоже на Python-код, в котором забыли сделать <code>import</code>.</p>

<h3>Теперь объясним</h3>

<h4>1. Разница между {{ }} и {% %}</h4>
<p><code>{{ переменная }}</code> &mdash; для <strong>вывода</strong> значения внутрь HTML (например <code>{{ post.sarlavha }}</code>). <code>{% tag %}</code> &mdash; для логики и управляющих конструкций (<code>for</code>, <code>if</code>, <code>block</code>, <code>extends</code> и т.д.).</p>

<h4>2. Как работает наследование шаблонов?</h4>
<p><code>base.html</code> задаёт общий "скелет", в котором оставлены "пустые места" вроде <code>{% block content %}</code>. Другой шаблон, объявив <code>{% extends 'base.html' %}</code>, <strong>заполняет</strong> эти пустые места через <code>{% block content %}...{% endblock %}</code>. Это предотвращает повторное написание повторяющихся частей вроде навбара, футера на каждой странице.</p>

<h4>3. Зачем нужны фильтры (<code>|</code>)?</h4>
<p>Фильтры позволяют <strong>изменять</strong> значение внутри шаблона &mdash; например, перевести текст в верхний регистр, сократить длинный текст, получить длину списка. Они предназначены для выполнения небольших трансформаций без написания Python-кода внутри шаблона.</p>

<h4>4. Зачем нужен {% load static %}?</h4>
<p>Django не считает некоторые теги (например <code>{% static %}</code>) <strong>встроенными</strong> &mdash; они поставляются как отдельный модуль и перед использованием должны быть <strong>явно загружены</strong> через <code>{% load static %}</code>. Это похоже на попытку использовать функцию модуля в Python без предварительного <code>import</code>.</p>

<h4>5. Что делает функция render()?</h4>
<p><code>render(request, имя_шаблона, context)</code> объединяет заданный файл шаблона с <code>context</code> (dict) и возвращает готовый <code>HttpResponse</code> в виде HTML-текста. Это намного удобнее, чем создавать <code>HttpResponse</code> вручную, и является самым распространённым способом в Django.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>{{ }}</code> — вывод значения, <code>{% %}</code> — для логики/тегов</li>
<li>✅ <code>{% extends %}</code> + <code>{% block %}</code> — наследование между шаблонами (DRY)</li>
<li>✅ Фильтры (<code>|upper</code>, <code>|truncatewords</code>, <code>|length</code>) изменяют значение внутри шаблона</li>
<li>✅ <code>{% load static %}</code> — обязателен для загрузки тега статических файлов</li>
<li>✅ <code>render()</code> — объединяет шаблон + context и возвращает HTML в HttpResponse</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 3: Шаблоны и язык шаблонов
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/views.py - с render()
# ─────────────────────────────────────────────────────────────────────

from django.shortcuts import render


def postlar_royxati(request):
    postlar = ["Birinchi post", "Ikkinchi post", "Uchinchi post"]
    return render(request, 'blog/post_list.html', {'postlar': postlar})

# ─────────────────────────────────────────────────────────────────────
# 2) templates/base.html (в комментарии - HTML файл, не Python)
# ─────────────────────────────────────────────────────────────────────

# <!DOCTYPE html>
# <html>
# <head><title>{% block title %}Mening Blogim{% endblock %}</title></head>
# <body>
#   <nav>Bosh sahifa | Blog</nav>
#   {% block content %}
#   {% endblock %}
# </body>
# </html>

# ─────────────────────────────────────────────────────────────────────
# 3) templates/blog/post_list.html (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# {% extends 'base.html' %}
# {% block title %}Postlar ro'yxati{% endblock %}
# {% block content %}
#   <h1>Postlar</h1>
#   <ul>
#   {% for post in postlar %}
#     <li>{{ post }}</li>
#   {% empty %}
#     <li>Postlar yo'q</li>
#   {% endfor %}
#   </ul>
# {% endblock %}

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли {% load static %} (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# <link rel="stylesheet" href="{% static 'blog/style.css' %}">
# ❌ Invalid block tag: 'static'. Did you forget to load this tag?
# (правильно: в начале файла обязательно написать {% load static %})
"""

EX = {
    4060: {
        "title": "Разница между {{ }} и {% %}",
        "description": "В чём основная разница между {{ post.sarlavha }} и {% for post in postlar %} в шаблоне Django?",
        "hint": "Один выводит значение, другой отдаёт команду.",
        "explanation": "{{ переменная }} выводит значение внутрь HTML, {% tag %} используется для логики и управляющих конструкций (for, if, block).",
    },
    4061: {
        "title": "Как работает наследование шаблонов?",
        "description": "Что вместе обеспечивают {% extends 'base.html' %} и {% block content %}?",
        "hint": "Это предотвращает повторное написание повторяющихся частей вроде навбара/футера.",
        "explanation": "Через extends дочерний шаблон наследует общую структуру base.html, а block позволяет заполнить только нужную часть (например content).",
    },
    4062: {
        "title": "Расположите процесс работы render()",
        "description": "Расположите процесс при вызове return render(request, 'blog/post_list.html', {'postlar': postlar}).",
        "hint": "",
        "explanation": "",
    },
    4063: {
        "title": "Загрузка тега статических файлов",
        "description": "Какую строку нужно написать в начале файла перед использованием тега {% static %}? (напишите именно эту строку)",
        "hint": "Это похоже на import в Python.",
        "expected_answer": "{% load static %}",
    },
    4064: {
        "title": "Почему забыть {% load static %} даёт ошибку?",
        "description": (
            "Если использовать {% static 'blog/style.css' %} без "
            "написанного в начале шаблона {% load static %}, почему "
            "Django выдаёт ошибку \"Invalid block tag: 'static'\"? "
            "Объясните своими словами."
        ),
        "hint": "{% static %} — встроенный тег или требующий отдельной загрузки?",
        "expected_answer": "Не все теги Django Template Language являются встроенными (built-in) — некоторые теги, такие как {% static %}, поставляются как отдельная библиотека (модуль) и перед использованием должны быть явно загружены через {% load static %}. Если эта строка не написана, Django вообще не распознаёт тег {% static %} и считает его \"неверным/несуществующим тегом\", выдавая ошибку — это похоже на попытку использовать функцию модуля в Python без предварительного import.",
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
