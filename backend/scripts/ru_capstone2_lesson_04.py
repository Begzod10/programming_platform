"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=3 (L4)."""
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

LESSON_ID = 750

TITLE_RU = "4-Аутентификация"

TEXT_RU = """\
<h2>Этап 4: Аутентификация — токен на Django, использование в React</h2>

<pre class="mermaid">
flowchart LR
    LOGIN["POST /api/login/"] --> TOKEN["создаётся запись в модели Token"]
    TOKEN --> REACT["React сохраняет токен"]
    REACT --> REQ["К каждому запросу добавляется Authorization: Token xxx"]
    REQ --> CHECK{"Token.objects.get(key=...) успешен?"}
    CHECK -->|DoesNotExist не перехвачен| CRASH["500 Internal Server Error"]
    CHECK -->|правильно перехвачен| OK["401 или пользователь определён"]
</pre>

<p>Так как в StudyMate React — отдельный frontend, обычная session-аутентификация Django (<code>login()</code> из курса Django Asoslari) не работает напрямую — React нужна <strong>token-based</strong> аутентификация. В этом уроке построим её <strong>сами</strong> (без DRF, на чистом Django).</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — модель Token и эндпоинт входа</h4>
<pre><code># studymate/models.py
import secrets
from django.db import models
from django.contrib.auth.models import User

class Token(models.Model):
    key = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def yaratish(user):
        key = secrets.token_hex(20)                  # ❗ 40-символьный случайный, безопасный токен
        return Token.objects.create(key=key, user=user)

# studymate/views.py
from django.contrib.auth import authenticate
from django.http import JsonResponse
import json

@csrf_exempt
def login_view(request):
    ma_lumot = json.loads(request.body)
    user = authenticate(username=ma_lumot["email"], password=ma_lumot["parol"])
    if user is None:
        return JsonResponse({"xato": "Email yoki parol noto'g'ri"}, status=401)

    token, _ = Token.objects.get_or_create(user=user, defaults={"key": secrets.token_hex(20)})
    return JsonResponse({"token": token.key, "ism": user.first_name})</code></pre>

<h4>БЛОК 2 — декоратор для защищённого view</h4>
<pre><code># studymate/auth_utils.py
from functools import wraps
from django.http import JsonResponse
from .models import Token

def token_talab_qilish(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Token "):
            return JsonResponse({"xato": "Token yo'q"}, status=401)

        key = auth_header.split(" ")[1]
        try:
            token = Token.objects.get(key=key)         # ❗ МОЖЕТ возникнуть DoesNotExist
        except Token.DoesNotExist:
            return JsonResponse({"xato": "Token yaroqsiz"}, status=401)

        request.user = token.user                        # ❗ передаёт user следующему view
        return view_func(request, *args, **kwargs)
    return wrapper

# studymate/views.py
@token_talab_qilish
def topshiriqlar_view(request):
    topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
    # ...</code></pre>

<h4>БЛОК 3 — React: сохранение и отправка токена</h4>
<pre><code>// frontend/src/api/auth.js
export async function kirish(email, parol) {
  const javob = await fetch(`${API_URL}/api/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, parol }),
  });
  const data = await javob.json();
  localStorage.setItem('token', data.token);
  return data;
}

// frontend/src/api/topshiriqlar.js - защищённый запрос
export async function topshiriqlarniOlish() {
  const token = localStorage.getItem('token');
  const javob = await fetch(`${API_URL}/api/topshiriqlar/`, {
    headers: { Authorization: `Token ${token}` },      // ❗ не "Bearer", а префикс "Token"
  });
  return await javob.json();
}</code></pre>

<h3>🐛 Намеренная ошибка — не перехватили Token.DoesNotExist</h3>
<pre><code>def token_talab_qilish_xato(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        key = auth_header.split(" ")[1]
        token = Token.objects.get(key=key)   # ❌ НЕТ try/except!
        request.user = token.user
        return view_func(request, *args, **kwargs)
    return wrapper

# Если отправлен неверный или устаревший токен:
# ❌ Django выбрасывает Token.DoesNotExist, и так как он не перехвачен,
#    возвращается 500 Internal Server Error (вместо 401)!</code></pre>

<p><strong>Результат:</strong> метод <code>.get()</code> в Django ORM, если соответствующая запись <strong>не найдена</strong>, <strong>выбрасывает</strong> исключение <code>Model.DoesNotExist</code> (вспомните урок 4 курса Django Asoslari). Если это исключение <strong>не перехвачено вручную</strong> через <code>try/except</code>, оно "поднимается" до верхнего уровня программы, и Django возвращает это как <strong>500 Internal Server Error</strong> &mdash; это показывает пользователю (или React-коду) непонятную ошибку сервера вместо ожидаемого "токен неверен" (401).</p>

<h3>Теперь объясним</h3>

<h4>1. Почему обычная session-аутентификация Django здесь не используется?</h4>
<p>Session-аутентификация полагается на cookie браузера и обычно предназначена для рендерящихся на сервере страниц <strong>одного домена</strong>. Так как React — <strong>отдельный</strong> frontend, работающий на другом порту/домене, token-based аутентификация (явная отправка заголовка <code>Authorization</code> при каждом запросе) подходит гораздо лучше.</p>

<h4>2. Зачем используется <code>secrets.token_hex(20)</code>?</h4>
<p>Модуль <code>secrets</code> создаёт криптографически безопасные случайные значения (в отличие от обычного модуля <code>random</code>). Так как токен используется для "узнавания" пользователя, он обязан быть <strong>непредсказуемым</strong>.</p>

<h4>3. Что делает декоратор (<code>token_talab_qilish</code>)?</h4>
<p>Это &mdash; практическое применение паттерна декоратора из урока 1 (курс Ilg'or Mavzular): "оборачивает" view-функцию, проверяет заголовок <code>Authorization</code>, ищет токен в базе, и если он верен, устанавливает <code>request.user</code> и передаёт управление исходному view.</p>

<h4>4. Почему обязательно нужно перехватывать <code>Token.DoesNotExist</code>?</h4>
<p>Пользователь (или злоумышленник) может отправить <strong>любой</strong> неверный токен &mdash; это <strong>нормальная, ожидаемая</strong> ситуация, а не ошибка. <code>try/except Token.DoesNotExist</code> позволяет обработать эту ситуацию <strong>контролируемо</strong> (с ответом 401), иначе Django посчитает это неожиданной серверной ошибкой (500).</p>

<h4>5. В чём разница между "Token xxx" и "Bearer xxx"?</h4>
<p>Это просто <strong>соглашение</strong> &mdash; формат заголовка <code>Authorization</code> имеет вид <code>&lt;схема&gt; &lt;значение&gt;</code>. Для JWT обычно используется <code>Bearer</code>, а в собственных (hand-rolled) системах токенов часто используется префикс <code>Token</code> (сам Django REST Framework тоже использует это соглашение). Важно, чтобы backend и frontend ожидали и отправляли <strong>одну и ту же</strong> схему.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Token-based аутентификация подходит лучше session для отдельного frontend (React)</li>
<li>✅ <code>secrets.token_hex()</code> создаёт криптографически безопасный, непредсказуемый токен</li>
<li>✅ Написание защищённых view через декоратор — практическое применение паттерна из урока 1 (Ilg'or Mavzular)</li>
<li>✅ Метод <code>.get()</code> Django ORM выбрасывает <code>DoesNotExist</code>, если запись не найдена — это <strong>обязательно нужно перехватывать</strong></li>
<li>✅ Формат заголовка <code>Authorization</code>: <code>&lt;схема&gt; &lt;значение&gt;</code>, backend/frontend должны ожидать одну и ту же схему</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 4: Аутентификация - токен на Django, использование в React
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/models.py - модель Token
# ─────────────────────────────────────────────────────────────────────

import secrets
from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    key = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def yaratish(user):
        key = secrets.token_hex(20)
        return Token.objects.create(key=key, user=user)

# ─────────────────────────────────────────────────────────────────────
# 2) studymate/views.py - вход
# ─────────────────────────────────────────────────────────────────────

import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login_view(request):
    ma_lumot = json.loads(request.body)
    user = authenticate(username=ma_lumot["email"], password=ma_lumot["parol"])
    if user is None:
        return JsonResponse({"xato": "Email yoki parol noto'g'ri"}, status=401)

    token, _ = Token.objects.get_or_create(user=user, defaults={"key": secrets.token_hex(20)})
    return JsonResponse({"token": token.key, "ism": user.first_name})

# ─────────────────────────────────────────────────────────────────────
# 3) studymate/auth_utils.py - декоратор защищённого view
# ─────────────────────────────────────────────────────────────────────

from functools import wraps


def token_talab_qilish(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Token "):
            return JsonResponse({"xato": "Token yo'q"}, status=401)

        key = auth_header.split(" ")[1]
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            return JsonResponse({"xato": "Token yaroqsiz"}, status=401)

        request.user = token.user
        return view_func(request, *args, **kwargs)
    return wrapper

# ─────────────────────────────────────────────────────────────────────
# 4) frontend/src/api/auth.js (в комментарии - JS)
# ─────────────────────────────────────────────────────────────────────

# export async function kirish(email, parol) {
#   const javob = await fetch(`${API_URL}/api/login/`, {
#     method: 'POST',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify({ email, parol }),
#   });
#   const data = await javob.json();
#   localStorage.setItem('token', data.token);
#   return data;
# }
#
# export async function topshiriqlarniOlish() {
#   const token = localStorage.getItem('token');
#   const javob = await fetch(`${API_URL}/api/topshiriqlar/`, {
#     headers: { Authorization: `Token ${token}` },
#   });
#   return await javob.json();
# }

# ─────────────────────────────────────────────────────────────────────
# 5) Намеренная ошибка - не перехвачен Token.DoesNotExist (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def token_talab_qilish_xato(view_func):
#     def wrapper(request, *args, **kwargs):
#         auth_header = request.headers.get("Authorization", "")
#         key = auth_header.split(" ")[1]
#         token = Token.objects.get(key=key)   # НЕТ try/except!
#         request.user = token.user
#         return view_func(request, *args, **kwargs)
#     return wrapper
# ❌ Неверный токен -> Token.DoesNotExist -> 500 Internal Server Error
"""

EX = {
    4354: {
        "title": "Почему используется token-based аутентификация?",
        "description": "Почему в StudyMate вместо обычной session-аутентификации Django используется token-based аутентификация?",
        "hint": "Session полагается на cookie, токен же — на каждый запрос.",
        "explanation": "Так как React — отдельный frontend (на другом порту/домене), вместо session-аутентификации, полагающейся на cookie браузера, лучше подходит token-based аутентификация с явной отправкой при каждом запросе.",
    },
    4355: {
        "title": "Зачем используется модуль secrets?",
        "description": "Почему при создании токена вместо обычного модуля random используется secrets?",
        "hint": "Токен используется для \"узнавания\" пользователя — предсказать его опасно.",
        "explanation": "Модуль secrets создаёт криптографически безопасные, непредсказуемые случайные значения, что необходимо для токенов аутентификации.",
    },
    4356: {
        "title": "Расположите процесс защищённого запроса",
        "description": "Расположите процесс внутри декоратора token_talab_qilish при поступлении запроса с заголовком Authorization от React.",
        "hint": "",
        "explanation": "",
    },
    4357: {
        "title": "Какое исключение выбрасывает Model.objects.get(), если запись не найдена?",
        "description": "Какое исключение выбрасывает метод .get() в Django ORM, если соответствующая запись не найдена? (например: DoesNotExist)",
        "hint": "",
        "expected_answer": "DoesNotExist",
    },
    4358: {
        "title": "Почему не перехваченный Token.DoesNotExist даёт ошибку 500?",
        "description": (
            "Если в декораторе token_talab_qilish_xato() вызвать "
            "Token.objects.get(key=key) без try/except, и отправить "
            "неверный токен, почему это заканчивается ошибкой 500 "
            "Internal Server Error вместо 401? Объясните своими словами."
        ),
        "hint": "Что делает метод .get() Django ORM, если запись не найдена, и что происходит, если эта \"ошибка\" не перехвачена вручную?",
        "expected_answer": "Метод .get() в Django ORM, если запись, соответствующая заданному условию, вообще не найдена, выбрасывает исключение Model.DoesNotExist (такое поведение уже встречалось в курсе Django Asoslari). Если это исключение не перехвачено вручную через try/except, оно \"выходит\" из view-функции и поднимается до общего механизма обработки ошибок Django, который считает это неожиданной, необработанной ошибкой и возвращает 500 Internal Server Error. Отправка неверного токена же на самом деле обычная, ожидаемая ситуация (должна была быть 401) — но так как исключение не перехвачено, она выглядит как серверная ошибка.",
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
        TASK_TITLE_RU = "StudyMate — token-based аутентификация"
        TASK_DESCRIPTION_RU = (
            "Создайте на Django модель Token и эндпоинт входа. Напишите "
            "декоратор token_talab_qilish и примените его к topshiriqlar_view. "
            "Правильно перехватите Token.DoesNotExist. На frontend реализуйте "
            "форму входа и добавление токена к каждому защищённому запросу."
        )
        TASK_REQUIREMENTS_RU = (
            "• Модель Token (key, user) создана и мигрирована\n"
            "• POST /api/login/ — проверяет через authenticate(), возвращает токен\n"
            "• Декоратор token_talab_qilish — проверяет заголовок Authorization\n"
            "• Token.DoesNotExist правильно перехвачен через try/except (возвращает 401, не 500)\n"
            "• GET /api/topshiriqlar/ — возвращает только задания request.user\n"
            "• Frontend: форма входа, токен сохраняется в localStorage и добавляется к каждому запросу\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Django, модуль secrets, React"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
