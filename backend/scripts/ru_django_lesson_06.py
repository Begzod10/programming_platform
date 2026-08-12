"""Russian translation for Python: Django Asoslari, lesson order=6 (L6)."""
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

LESSON_ID = 698

TITLE_RU = "6-Формы и валидация"

TEXT_RU = """\
<h2>Формы и валидация — безопасное получение данных пользователя</h2>

<pre class="mermaid">
flowchart LR
    GET["GET-запрос"] --> BOSH["Показывается пустая форма"]
    POST["POST-запрос"] --> VALID{"form.is_valid()?"}
    VALID -->|True| SAVE["form.cleaned_data / form.save()"]
    VALID -->|False| ERR["Повторно показывается с form.errors"]
</pre>

<p>На Flask вы бы вручную получали данные формы через <code>request.form</code> и сами их проверяли (или использовали Flask-WTF). У Django есть <strong>собственная система Forms</strong> &mdash; валидация, сообщения об ошибках и даже вывод самой HTML-формы происходят автоматически.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — простая forms.Form</h4>
<pre><code># blog/forms.py
from django import forms

class KontaktForm(forms.Form):
    ism = forms.CharField(max_length=100)               # ❗ не может быть пустым (по умолчанию: required=True)
    email = forms.EmailField()                          # ❗ автоматически проверяет формат email
    xabar = forms.CharField(widget=forms.Textarea)       # ❗ отображается как &lt;textarea&gt;

# blog/views.py
from django.shortcuts import render
from .forms import KontaktForm

def kontakt(request):
    if request.method == 'POST':
        form = KontaktForm(request.POST)                # ❗ форма, заполненная данными POST
        if form.is_valid():                              # ❗ проверяет ВСЕ правила валидации разом
            ism = form.cleaned_data['ism']                # ❗ очищенные, безопасные данные
            # ... отправка email или сохранение ...
            return render(request, 'blog/rahmat.html')
    else:
        form = KontaktForm()                              # ❗ пустая форма (при GET-запросе)
    return render(request, 'blog/kontakt.html', {'form': form})</code></pre>

<h4>БЛОК 2 — форма в шаблоне и CSRF-токен</h4>
<pre><code>{# blog/kontakt.html #}
&lt;form method="post"&gt;
  {% csrf_token %}          {# ❗ ОБЯЗАТЕЛЬНО — защищает от CSRF-атаки #}
  {{ form.as_p }}           {# ❗ выводит все поля формы, обёрнутые в теги &lt;p&gt; #}
  &lt;button type="submit"&gt;Yuborish&lt;/button&gt;
&lt;/form&gt;</code></pre>

<h4>БЛОК 3 — ModelForm: автоматическая форма из модели</h4>
<pre><code># blog/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):     # ❗ ModelForm - создаёт форму автоматически из модели
    class Meta:
        model = Post
        fields = ['sarlavha', 'matn']  # ❗ в форме будут только эти поля

# blog/views.py
def post_yaratish(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()                # ❗ у ModelForm можно сохранять напрямую!
            return redirect('post-list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})</code></pre>

<h3>🐛 Намеренная ошибка — забыли {% csrf_token %}</h3>
<pre><code>&lt;form method="post"&gt;
  {# {% csrf_token %} отсутствует! #}
  {{ form.as_p }}
  &lt;button type="submit"&gt;Yuborish&lt;/button&gt;
&lt;/form&gt;

# При отправке формы:
# ❌ Ошибка: 403 Forbidden - CSRF verification failed. Request aborted.</code></pre>

<p><strong>Результат:</strong> Django <strong>по умолчанию</strong> защищает все POST-запросы от атаки CSRF (Cross-Site Request Forgery). Каждая HTML-форма <strong>обязательно</strong> должна выводить скрытый токен через <code>{% csrf_token %}</code> &mdash; сервер проверяет именно этот токен. Если токена нет, Django считает запрос <strong>недоверенным</strong> и отклоняет его с ошибкой 403 &mdash; это намеренно строгое требование ради безопасности.</p>

<h3>Теперь объясним</h3>

<h4>1. Что делает is_valid()?</h4>
<p><code>form.is_valid()</code> проверяет правила валидации <strong>всех</strong> полей формы разом (например, формат email для <code>EmailField</code>, пустоту полей с <code>required=True</code>) и возвращает <code>True</code>/<code>False</code>. Если <code>False</code>, ошибки собираются в <code>form.errors</code>.</p>

<h4>2. Зачем нужен cleaned_data?</h4>
<p><code>form.cleaned_data</code> &mdash; данные, <strong>успешно прошедшие</strong> валидацию, приведённые к правильному типу (например строка для <code>EmailField</code>, int для <code>IntegerField</code>) и <strong>безопасные</strong>. В отличие от сырого <code>request.POST</code>, этим данным можно доверять.</p>

<h4>3. Разница между forms.Form и ModelForm</h4>
<p><code>forms.Form</code> &mdash; для любой формы (например, контактной формы, не связанной с моделью). <code>ModelForm</code> &mdash; <strong>автоматически</strong> создаёт поля формы из существующей модели (например <code>Post</code>) и позволяет сохранять напрямую в базу данных через <code>form.save()</code>.</p>

<h4>4. Зачем нужен CSRF-токен?</h4>
<p>При CSRF-атаке злонамеренный сайт пытается отправить запрос на ваш сайт от имени пользователя (без его ведома). <code>{% csrf_token %}</code> выводит уникальный, непредсказуемый токен для каждой сессии пользователя &mdash; сервер проверяет этот токен, подтверждая, что запрос <strong>действительно</strong> пришёл из формы на вашем сайте.</p>

<h4>5. Почему форма без csrf_token даёт ошибку 403?</h4>
<p>С точки зрения безопасности Django применяет подход <strong>"default deny"</strong> (запрет по умолчанию): если в POST-запросе нет правильного CSRF-токена, этот запрос считается <strong>недоверенным</strong> (возможно, атакой) и отклоняется, <strong>не доходя</strong> до сервера. Это вынуждает разработчика обязательно применять меры безопасности.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>form.is_valid()</code> — проверяет все правила валидации разом</li>
<li>✅ <code>form.cleaned_data</code> — прошедшие валидацию, безопасные данные</li>
<li>✅ <code>forms.Form</code> — любая форма, <code>ModelForm</code> — автоматическая форма из модели + <code>save()</code></li>
<li>✅ <code>{% csrf_token %}</code> — ОБЯЗАТЕЛЕН в каждой POST-форме, защищает от CSRF-атаки</li>
<li>✅ Без токена Django отклоняет запрос с ошибкой 403</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 6: Формы и валидация
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) blog/forms.py - простая forms.Form
# ─────────────────────────────────────────────────────────────────────

from django import forms


class KontaktForm(forms.Form):
    ism = forms.CharField(max_length=100)
    email = forms.EmailField()
    xabar = forms.CharField(widget=forms.Textarea)

# ─────────────────────────────────────────────────────────────────────
# 2) blog/views.py - работа с формой
# ─────────────────────────────────────────────────────────────────────

from django.shortcuts import render


def kontakt(request):
    if request.method == 'POST':
        form = KontaktForm(request.POST)
        if form.is_valid():
            ism = form.cleaned_data['ism']
            return render(request, 'blog/rahmat.html')
    else:
        form = KontaktForm()
    return render(request, 'blog/kontakt.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# 3) blog/kontakt.html (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# <form method="post">
#   {% csrf_token %}
#   {{ form.as_p }}
#   <button type="submit">Yuborish</button>
# </form>

# ─────────────────────────────────────────────────────────────────────
# 4) ModelForm - автоматическая форма из модели
# ─────────────────────────────────────────────────────────────────────

# from .models import Post
#
# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['sarlavha', 'matn']
#
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
# 5) Намеренная ошибка - забыли {% csrf_token %} (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# <form method="post">
#   {# {% csrf_token %} отсутствует! #}
#   {{ form.as_p }}
# </form>
# ❌ 403 Forbidden - CSRF verification failed. Request aborted.
"""

EX = {
    4098: {
        "title": "Что делает is_valid()?",
        "description": "Что делает метод form.is_valid()?",
        "hint": "Он возвращает результат проверки как булево значение.",
        "explanation": "form.is_valid() проверяет правила валидации всех полей (required, формат EmailField и т.д.) разом и возвращает True/False.",
    },
    4099: {
        "title": "Разница между forms.Form и ModelForm",
        "description": "В чём основная разница между forms.Form и ModelForm?",
        "hint": "Одна связана с моделью, другая самостоятельна.",
        "explanation": "ModelForm автоматически создаёт поля формы из существующей модели (например Post) и позволяет сохранять напрямую через form.save(). forms.Form же независима от модели, используется для любой формы.",
    },
    4100: {
        "title": "Расположите процесс отправки формы",
        "description": "Расположите процесс, происходящий при заполнении и отправке (POST) пользователем формы KontaktForm.",
        "hint": "",
        "explanation": "",
    },
    4101: {
        "title": "Обязательный тег для защиты CSRF",
        "description": "Какой тег обязательно нужно написать в каждой POST HTML-форме для защиты CSRF? (напишите именно этот тег)",
        "hint": "Пишется внутри формы, перед кнопкой отправки.",
        "expected_answer": "{% csrf_token %}",
    },
    4102: {
        "title": "Почему форма без csrf_token даёт ошибку 403?",
        "description": (
            "Если в HTML-форме не написан {% csrf_token %}, почему при "
            "отправке формы Django выдаёт ошибку \"403 Forbidden - CSRF "
            "verification failed\"? От какой атаки это защищает? "
            "Объясните своими словами."
        ),
        "hint": "Что означает CSRF и от какой атаки она защищает?",
        "expected_answer": "Django ради безопасности применяет подход \"default deny\" (запрет по умолчанию): в каждом POST-запросе обязательно должен быть настоящий, привязанный к сессии CSRF-токен. Этот токен защищает от атаки Cross-Site Request Forgery (CSRF) — когда злонамеренный сторонний сайт пытается отправить запрос на ваш сайт от имени пользователя, без его ведома. Если {% csrf_token %} не написан, форма не отправляет правильный токен, и Django считает этот запрос недоверенным (потенциальной атакой), отклоняя его с ошибкой 403, не доводя до сервера.",
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
