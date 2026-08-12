"""Russian translation for Capstone 2: Django + React + Telegram Bot, lesson order=1 (L2)."""
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

LESSON_ID = 746

TITLE_RU = "2-Django backend API"

TEXT_RU = """\
<h2>Этап 2: Django backend API — CRUD для Fan и Topshiriq</h2>

<pre class="mermaid">
flowchart LR
    MODEL["Модели Django (из схемы урока 1)"] --> VIEW["обычный view + JsonResponse"]
    VIEW --> JSON["React получает JSON"]
    VIEW -->|без safe=False| ERROR["TypeError: список нельзя вернуть напрямую"]
</pre>

<p>На курсе Django Asoslari вы изучили модели и обычные view. На этом этапе построим их как <strong>JSON API</strong> — React frontend (урок 3) и Telegram-бот (урок 5) <strong>оба</strong> будут использовать эти эндпоинты.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — модели Django по схеме из урока 1</h4>
<pre><code># studymate/models.py
from django.db import models
from django.contrib.auth.models import User

class Fan(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fanlar')

    def __str__(self):
        return self.nomi

class Topshiriq(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField(blank=True)
    muddat_vaqti = models.DateTimeField()
    bajarilgan = models.BooleanField(default=False)
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='topshiriqlar')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topshiriqlar')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha</code></pre>

<h4>БЛОК 2 — view, возвращающие JSON</h4>
<pre><code># studymate/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Topshiriq

def topshiriq_to_dict(t):                          # ❗ превращает объект модели в JSON-совместимый dict
    return {
        "id": t.id, "sarlavha": t.sarlavha, "matn": t.matn,
        "muddat_vaqti": t.muddat_vaqti.isoformat(),  # ❗ datetime в JSON должен быть строкой
        "bajarilgan": t.bajarilgan, "fan_nomi": t.fan.nomi,
    }

@require_http_methods(["GET", "POST"])
@csrf_exempt                                         # ❗ для внешних (React) запросов, заменим на token auth (урок 4)
def topshiriqlar_view(request):
    if request.method == "GET":
        topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
        natija = [topshiriq_to_dict(t) for t in topshiriqlar]
        return JsonResponse(natija, safe=False)      # ❗ при возврате списка safe=False ОБЯЗАТЕЛЕН

    ma_lumot = json.loads(request.body)
    yangi = Topshiriq.objects.create(
        sarlavha=ma_lumot["sarlavha"], matn=ma_lumot.get("matn", ""),
        muddat_vaqti=ma_lumot["muddat_vaqti"], fan_id=ma_lumot["fan_id"],
        user=request.user,
    )
    return JsonResponse(topshiriq_to_dict(yangi), status=201)   # ❗ один объект - safe=False не нужен</code></pre>

<h4>БЛОК 3 — urls.py</h4>
<pre><code># studymate/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/topshiriqlar/', views.topshiriqlar_view, name='topshiriqlar'),
]</code></pre>

<h3>🐛 Намеренная ошибка — забыли safe=False при возврате списка</h3>
<pre><code>def topshiriqlar_view_xato(request):
    topshiriqlar = Topshiriq.objects.filter(user=request.user)
    natija = [topshiriq_to_dict(t) for t in topshiriqlar]
    return JsonResponse(natija)   # ❌ НЕТ safe=False!

# При отправке запроса:
# ❌ TypeError: In order to allow non-dict objects to be serialized set the
#    safe parameter to False
# (Django по умолчанию считает "безопасным" ТОЛЬКО объект dict!)</code></pre>

<p><strong>Результат:</strong> <code>JsonResponse</code> в Django по умолчанию считает "безопасным" возврат <strong>только словаря</strong> (dict, единичного объекта) &mdash; это одна из мер безопасности (для предотвращения некоторых старых уязвимостей браузеров). Если вы хотите вернуть <strong>список</strong> (list) (например все задания), Django автоматически это отклоняет и требует <strong>явно</strong> указать <code>safe=False</code> &mdash; это равносильно тому, чтобы сказать Django: "я намеренно и осознанно возвращаю этот список".</p>

<h3>Теперь объясним</h3>

<h4>1. Зачем написана отдельная функция <code>topshiriq_to_dict()</code>?</h4>
<p>Объект модели Django (<code>Topshiriq</code>) нельзя напрямую превратить в JSON &mdash; это Python-объект, а JSON поддерживает только простые типы (строка, число, список, dict). <code>topshiriq_to_dict()</code> "переводит" объект модели в JSON-совместимый <code>dict</code>, и эта функция вынесена отдельно, чтобы не переписывать её в каждом view.</p>

<h4>2. Зачем используется <code>muddat_vaqti.isoformat()</code>?</h4>
<p>Объект <code>datetime</code> в Python не является одним из стандартных типов JSON &mdash; передача его напрямую в <code>JsonResponse</code> вызывает ошибку. <code>.isoformat()</code> преобразует его в <strong>текстовый</strong> вид, поддерживаемый JSON ("2026-08-01T23:59:00").</p>

<h4>3. Зачем используется <code>select_related('fan')</code>?</h4>
<p>Вспомните проблему N+1 из урока 4 курса Django Asoslari &mdash; <code>select_related</code> получает данные <code>Fan</code> вместе с <code>Topshiriq</code> одним запросом, предотвращая отправку отдельного запроса для каждого задания.</p>

<h4>4. Почему <code>safe=False</code> нужен только при возврате списка?</h4>
<p>Django в качестве меры безопасности считает "безопасными" только объекты <code>dict</code>. Один объект (<code>topshiriq_to_dict(yangi)</code>) уже является <code>dict</code>, поэтому <code>safe=False</code> не нужен &mdash; он нужен только когда возвращается <code>list</code>.</p>

<h4>5. Почему <code>@csrf_exempt</code> используется временно?</h4>
<p>Django по умолчанию требует CSRF-токен для всех POST-запросов (это предназначено для страниц, заполняемых через веб-форму). Для API-запросов от отдельного frontend (React) нужен другой подход (аутентификация через токен) &mdash; правильно решим это в уроке 4, а пока временно пропускаем через <code>@csrf_exempt</code>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Схема из урока 1 превращена в модели Django (с ForeignKey)</li>
<li>✅ Написание отдельной функции для превращения объектов модели в JSON-совместимый <code>dict</code> — хорошая практика</li>
<li>✅ Поля <code>datetime</code> перед возвратом в JSON нужно преобразовать в текст через <code>.isoformat()</code></li>
<li>✅ Для возврата списка в <code>JsonResponse</code> <code>safe=False</code> ОБЯЗАТЕЛЕН</li>
<li>✅ <code>select_related</code> позволяет получить связанные данные без проблемы N+1</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 2: Django backend API - CRUD для Fan и Topshiriq
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) studymate/models.py
# ─────────────────────────────────────────────────────────────────────

from django.db import models
from django.contrib.auth.models import User


class Fan(models.Model):
    nomi = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fanlar')

    def __str__(self):
        return self.nomi


class Topshiriq(models.Model):
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField(blank=True)
    muddat_vaqti = models.DateTimeField()
    bajarilgan = models.BooleanField(default=False)
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='topshiriqlar')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topshiriqlar')
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sarlavha

# ─────────────────────────────────────────────────────────────────────
# 2) studymate/views.py
# ─────────────────────────────────────────────────────────────────────

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def topshiriq_to_dict(t):
    return {
        "id": t.id, "sarlavha": t.sarlavha, "matn": t.matn,
        "muddat_vaqti": t.muddat_vaqti.isoformat(),
        "bajarilgan": t.bajarilgan, "fan_nomi": t.fan.nomi,
    }


@require_http_methods(["GET", "POST"])
@csrf_exempt
def topshiriqlar_view(request):
    if request.method == "GET":
        topshiriqlar = Topshiriq.objects.filter(user=request.user).select_related('fan')
        natija = [topshiriq_to_dict(t) for t in topshiriqlar]
        return JsonResponse(natija, safe=False)

    ma_lumot = json.loads(request.body)
    yangi = Topshiriq.objects.create(
        sarlavha=ma_lumot["sarlavha"], matn=ma_lumot.get("matn", ""),
        muddat_vaqti=ma_lumot["muddat_vaqti"], fan_id=ma_lumot["fan_id"],
        user=request.user,
    )
    return JsonResponse(topshiriq_to_dict(yangi), status=201)

# ─────────────────────────────────────────────────────────────────────
# 3) studymate/urls.py (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('api/topshiriqlar/', views.topshiriqlar_view, name='topshiriqlar'),
# ]

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - забыли safe=False (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def topshiriqlar_view_xato(request):
#     topshiriqlar = Topshiriq.objects.filter(user=request.user)
#     natija = [topshiriq_to_dict(t) for t in topshiriqlar]
#     return JsonResponse(natija)   # НЕТ safe=False!
# ❌ TypeError: In order to allow non-dict objects to be serialized set the
#    safe parameter to False
"""

EX = {
    4334: {
        "title": "Зачем нужна функция topshiriq_to_dict()?",
        "description": "Почему объект модели Topshiriq не передаётся напрямую в JsonResponse, а сначала превращается в dict через topshiriq_to_dict()?",
        "hint": "Какие типы поддерживает JSON?",
        "explanation": "Объект модели Django нельзя напрямую превратить в JSON, так как это Python-объект — topshiriq_to_dict() \"переводит\" его в простой dict, поддерживаемый JSON.",
    },
    4335: {
        "title": "Когда нужен safe=False?",
        "description": "В записи JsonResponse(natija, safe=False), когда необходим safe=False?",
        "hint": "Django по умолчанию считает \"безопасным\" только один тип объекта.",
        "explanation": "Django по умолчанию считает безопасными только объекты dict. Если результат — список (list), нужно явно указать safe=False.",
    },
    4336: {
        "title": "Расположите процесс запроса GET /api/topshiriqlar/",
        "description": "Расположите процесс, происходящий внутри topshiriqlar_view при получении GET-запроса от React.",
        "hint": "",
        "explanation": "",
    },
    4337: {
        "title": "Метод преобразования datetime в текст для JSON",
        "description": "Напишите метод, преобразующий объект datetime Python в текстовый вид, поддерживаемый JSON.",
        "hint": "muddat_vaqti.___()",
        "expected_answer": "isoformat",
    },
    4338: {
        "title": "Почему без safe=False возникает TypeError?",
        "description": (
            "Если в функции topshiriqlar_view_xato() вызвать "
            "JsonResponse(natija) без safe=False (natija — список), "
            "почему Django выдаёт ошибку TypeError? Объясните своими "
            "словами."
        ),
        "hint": "Какой тип объекта JsonResponse Django по умолчанию считает \"безопасным\"?",
        "expected_answer": "JsonResponse Django в качестве меры безопасности по умолчанию считает \"безопасным\" только возврат dict (одного объекта) — это решение принято для защиты от некоторых старых уязвимостей браузеров. Если результат является list (списком), Django автоматически это отклоняет и требует от разработчика явного подтверждения через safe=False, что означает \"я намеренно и осознанно возвращаю этот список\". Если это подтверждение не дано (safe=False не написан), Django выбрасывает ошибку TypeError.",
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
        TASK_TITLE_RU = "StudyMate — Django backend API (Fan + Topshiriq)"
        TASK_DESCRIPTION_RU = (
            "На основе схемы из этапа 1 создайте модели Django Fan и "
            "Topshiriq, выполните миграцию. Постройте JSON API через "
            "topshiriqlar_view, поддерживающий GET (список) и POST (добавление). "
            "Через select_related предотвратите проблему N+1."
        )
        TASK_REQUIREMENTS_RU = (
            "• Модели Fan и Topshiriq созданы с правильными foreign key\n"
            "• GET /api/topshiriqlar/ — возвращает задания текущего пользователя "
            "вместе с fan_nomi как JSON-список (safe=False)\n"
            "• POST /api/topshiriqlar/ — создаёт новое задание, возвращает 201\n"
            "• Использован select_related('fan') (без проблемы N+1)\n"
            "• Поля datetime приведены к JSON-совместимому виду через .isoformat()\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Django, PostgreSQL, JsonResponse"
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
