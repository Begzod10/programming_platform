"""Course spec: Django: JSON API (DRF asoslari) — 6 lessons, UZ + RU.

Notes API built in stages (JsonResponse -> DRF serializers -> ViewSet/router ->
JWT auth -> CORS + tests -> project). Every code constant below is materialised
into a real Django project and run by the verification script before a lesson
text may use it. API messages are English so the code is identical in UZ and RU.
"""
from __future__ import annotations

# ── Stage code (single source of truth for lessons 1-6) ──────────────────────

CODE_MODELS_L1 = '''from django.db import models


class Note(models.Model):
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
'''

CODE_VIEWS_L1 = '''import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Note


def note_to_dict(note):
    return {"id": note.id, "text": note.text, "created_at": note.created_at.isoformat()}


@csrf_exempt
def notes_list(request):
    if request.method == "GET":
        return JsonResponse([note_to_dict(n) for n in Note.objects.all()], safe=False)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)
        text = str(data.get("text", "")).strip() if isinstance(data, dict) else ""
        if not text:
            return JsonResponse({"error": "text is required"}, status=400)
        note = Note.objects.create(text=text)
        return JsonResponse(note_to_dict(note), status=201)
    return JsonResponse({"error": "method not allowed"}, status=405)
'''

CODE_URLS_APP_L1 = '''from django.urls import path

from . import views

urlpatterns = [
    path("notes/", views.notes_list),
]
'''

CODE_URLS_ROOT = '''from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("notes.urls")),
]
'''

CODE_SERIALIZERS_L2 = '''from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "text", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_text(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("text must be at least 3 characters")
        return value
'''

CODE_VIEWS_L2 = '''from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer


@api_view(["GET", "POST"])
def notes_list(request):
    if request.method == "GET":
        return Response(NoteSerializer(Note.objects.all(), many=True).data)
    serializer = NoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == "DELETE":
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(NoteSerializer(note).data)
'''

CODE_URLS_APP_L2 = '''from django.urls import path

from . import views

urlpatterns = [
    path("notes/", views.notes_list),
    path("notes/<int:pk>/", views.note_detail),
]
'''

CODE_VIEWS_L3 = '''from rest_framework import viewsets

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
'''

CODE_URLS_APP_L3 = '''from rest_framework.routers import DefaultRouter

from .views import NoteViewSet

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="note")

urlpatterns = router.urls
'''

CODE_MODELS_L4 = '''from django.conf import settings
from django.db import models


class Note(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
'''

CODE_SERIALIZERS_L4 = '''from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Note

User = get_user_model()


class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Note
        fields = ["id", "text", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

    def validate_text(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("text must be at least 3 characters")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
'''

CODE_VIEWS_L4 = '''from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer, RegisterSerializer

User = get_user_model()


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Note.objects.all()
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "registered"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def users_list(request):
    return Response([{"id": u.id, "username": u.username, "is_staff": u.is_staff} for u in User.objects.all()])
'''

CODE_URLS_APP_L4 = '''from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("notes", views.NoteViewSet, basename="note")

urlpatterns = [
    path("register/", views.register),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("admin/users/", views.users_list),
] + router.urls
'''

SETTINGS_REST_L2 = '''INSTALLED_APPS += ["rest_framework"]
'''

SETTINGS_JWT_L4 = '''import datetime as dt

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": dt.timedelta(minutes=30),
}
'''

SETTINGS_CORS_L5 = '''INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")   # must come before CommonMiddleware

CORS_ALLOWED_ORIGINS = ["http://localhost:8080"]
CORS_ALLOW_HEADERS = ["authorization", "content-type"]
CORS_URLS_REGEX = r"^/api/.*$"
'''

CODE_TESTS_L5 = '''import datetime as dt

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class NotesApiTests(APITestCase):
    def setUp(self):
        self.ali = User.objects.create_user("ali", password="secret12")
        self.vali = User.objects.create_user("vali", password="secret12")
        self.boss = User.objects.create_user("boss", password="secret12", is_staff=True)

    def login(self, username):
        res = self.client.post("/api/token/", {"username": username, "password": "secret12"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_register_validates_and_rejects_duplicates(self):
        bad = self.client.post("/api/register/", {"username": "new", "password": "123"}, format="json")
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post("/api/register/", {"username": "new", "password": "secret12"}, format="json")
        self.assertEqual(ok.status_code, 201)
        dup = self.client.post("/api/register/", {"username": "new", "password": "secret12"}, format="json")
        self.assertEqual(dup.status_code, 400)

    def test_wrong_password_gets_no_token(self):
        res = self.client.post("/api/token/", {"username": "ali", "password": "wrong"}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_notes_need_a_token(self):
        self.assertEqual(self.client.get("/api/notes/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer garbage")
        res = self.client.get("/api/notes/")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["code"], "token_not_valid")

    def test_an_expired_token_is_rejected(self):
        token = AccessToken.for_user(self.ali)
        token.set_exp(lifetime=-dt.timedelta(seconds=1))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.get("/api/notes/")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["code"], "token_not_valid")

    def test_users_only_see_and_delete_their_own_notes(self):
        self.login("ali")
        created = self.client.post("/api/notes/", {"text": "ali note"}, format="json")
        self.assertEqual(created.status_code, 201)
        note_id = created.data["id"]
        self.assertEqual(len(self.client.get("/api/notes/").data), 1)
        self.login("vali")
        self.assertEqual(self.client.get("/api/notes/").data, [])
        self.assertEqual(self.client.delete(f"/api/notes/{note_id}/").status_code, 404)
        self.login("ali")
        self.assertEqual(self.client.delete(f"/api/notes/{note_id}/").status_code, 204)

    def test_staff_sees_everything_and_only_staff_lists_users(self):
        self.login("ali")
        self.client.post("/api/notes/", {"text": "ali note"}, format="json")
        self.assertEqual(self.client.get("/api/admin/users/").status_code, 403)
        self.login("boss")
        self.assertEqual(len(self.client.get("/api/notes/").data), 1)
        self.assertEqual(self.client.get("/api/admin/users/").status_code, 200)

    def test_cors_allows_the_frontend_origin_and_the_authorization_header(self):
        pre = self.client.options(
            "/api/notes/",
            HTTP_ORIGIN="http://localhost:8080",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization",
        )
        self.assertEqual(pre["Access-Control-Allow-Origin"], "http://localhost:8080")
        self.assertIn("authorization", pre["Access-Control-Allow-Headers"].lower())
        other = self.client.options(
            "/api/notes/", HTTP_ORIGIN="http://evil.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET"
        )
        self.assertNotIn("Access-Control-Allow-Origin", other)
'''

API_JS = '''const API = "http://127.0.0.1:8000";

async function login(username, password) {
  const res = await fetch(`${API}/api/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "login failed");
  localStorage.setItem("auth_token", data.access);
  return data;
}

async function loadNotes() {
  const res = await fetch(`${API}/api/notes/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
  });
  if (res.status === 401) {
    localStorage.removeItem("auth_token");
    throw new Error("login required");
  }
  return res.json();
}
'''


COURSE = {
    "title": "Django: JSON API (DRF asoslari)",
    "title_ru": "Django: JSON API (основы DRF)",
    "description": (
        "Django'da JSON API yasashni o'rganasiz: JsonResponse bilan oddiy API, Django REST Framework serializer'lari, "
        "ViewSet va router, JWT token autentifikatsiya, CORS bilan frontendni ulash va API testlari. "
        "Kurs oxirida tokenli Notes API va unga ulangan oddiy frontend yasaysiz."
    ),
    "description_ru": (
        "Вы научитесь делать JSON API на Django: простой API на JsonResponse, сериализаторы Django REST Framework, "
        "ViewSet и роутер, JWT-аутентификацию, подключение фронтенда через CORS и тесты API. "
        "В конце курса вы сделаете Notes API с токеном и подключите к нему простой фронтенд."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 8,
    "prerequisite_course_id": 82,
    "display_order": 307,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


CURL_L1 = '''curl http://127.0.0.1:8000/api/notes/
curl -X POST http://127.0.0.1:8000/api/notes/ -H "Content-Type: application/json" -d '{"text": "buy bread"}'
'''

CURL_L4 = '''curl -X POST http://127.0.0.1:8000/api/register/ -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{"username": "ali", "password": "secret12"}'
curl http://127.0.0.1:8000/api/notes/ -H "Authorization: Bearer eyJ..."
'''

CURL_PREFLIGHT = '''curl -i -X OPTIONS http://127.0.0.1:8000/api/notes/ -H "Origin: http://localhost:8080" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: authorization"
'''

POSTMAN_SCRIPT = '''const data = pm.response.json();
pm.collectionVariables.set("token", data.access);
'''

SETUP_CMDS = '''python manage.py startapp notes
python manage.py makemigrations notes
python manage.py migrate
python manage.py runserver
'''

PIP_DRF = "pip install djangorestframework"
PIP_JWT = "pip install djangorestframework-simplejwt"
PIP_CORS = "pip install django-cors-headers"

INDEX_HTML = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Notes</title>
</head>
<body>
  <h1>Notes</h1>
  <form id="login-form">
    <input id="username" placeholder="username" required>
    <input id="password" type="password" placeholder="password" required>
    <button>Login</button>
  </form>
  <p id="message"></p>
  <ul id="notes"></ul>
  <script src="api.js"></script>
  <script>
    const message = document.getElementById("message");
    const list = document.getElementById("notes");

    async function showNotes() {
      list.innerHTML = "";
      try {
        for (const note of await loadNotes()) {
          const li = document.createElement("li");
          li.textContent = note.text;
          list.appendChild(li);
        }
      } catch (err) {
        message.textContent = err.message;
      }
    }

    document.getElementById("login-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await login(event.target.username.value, event.target.password.value);
        message.textContent = "";
        showNotes();
      } catch (err) {
        message.textContent = err.message;
      }
    });

    if (localStorage.getItem("auth_token")) showNotes();
  </script>
</body>
</html>
'''


# ── 1-dars: JsonResponse bilan oddiy API ─────────────────────────────────────

_L1_TEXT_UZ = """<h3>JSON API nima</h3>
<p>Siz Django'da HTML sahifalar qaytaradigan view'lar yozgansiz. <strong>JSON API</strong> esa HTML o'rniga <em>ma'lumot</em> (JSON) qaytaradi, uni mobil ilova, React yoki oddiy JavaScript <code>fetch</code> bilan o'qiydi. Shu darsda Django'ning o'zi bilan, hech qanday qo'shimcha kutubxonasiz, <strong>Notes API</strong>ning birinchi variantini yozamiz. Keyingi darslarda uni Django REST Framework (DRF) bilan qisqartiramiz va himoyalaymiz.</p>
<pre class="mermaid">
flowchart LR
  A["Mijoz: GET/POST /api/notes/"] --> B["urls.py: yo'lni topadi"]
  B --> C["view: JSON'ni o'qiydi va tekshiradi"]
  C --> D["Note modeli: bazaga yozadi/o'qiydi"]
  D --> E["JsonResponse + status kodi"]
</pre>

<h3>Loyiha tayyorlash</h3>
<p>Mavjud Django loyihangizda (<code>config</code>) yangi ilova yarating, uni <code>INSTALLED_APPS</code> ga <code>"notes"</code> deb qo'shing, so'ng:</p>
<pre><code>__SETUP__</code></pre>
<p>Model oddiy: matn va yaratilgan vaqt.</p>
<pre><code>__MODELS__</code></pre>

<h3>JsonResponse va view</h3>
<ul>
  <li><code>JsonResponse(dict)</code> lug'atni JSON'ga aylantiradi va <code>Content-Type: application/json</code> qo'yadi. Ro'yxat qaytarsangiz <code>safe=False</code> kerak.</li>
  <li><code>request.body</code> — xom bayt. Uni <code>json.loads</code> bilan o'qiymiz; noto'g'ri JSON bo'lsa <code>JSONDecodeError</code> chiqadi, shuning uchun <code>400</code> qaytaramiz.</li>
  <li>Status kodi: <code>201</code> — yaratildi, <code>400</code> — so'rov noto'g'ri, <code>405</code> — metod qo'llab-quvvatlanmaydi.</li>
  <li><code>@csrf_exempt</code>: Django standart holatda POST'ni CSRF tokenisiz rad etadi. CSRF brauzer formalari uchun; token bilan ishlaydigan API'da u kerak emas. Biz bu darsda uni vaqtincha o'chiramiz, keyingi darslarda DRF buni o'zi hal qiladi.</li>
</ul>
<pre><code>__VIEWS__</code></pre>
<p>URL'larni ulaymiz: ilovada <code>notes/urls.py</code>, loyihada esa <code>/api/</code> prefiksi bilan.</p>
<pre><code>__URLS_APP__</code></pre>
<pre><code>__URLS_ROOT__</code></pre>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Birinchi so'rov bo'sh ro'yxat <code>[]</code> qaytaradi. Ikkinchisi <code>201</code> va yaratilgan yozuvni beradi. Bo'sh <code>text</code> yoki buzilgan JSON yuborib, <code>400</code> ni ham ko'ring.</p>

<h3>Bu yondashuvning kamchiligi</h3>
<p>Har bir view'da JSON'ni qo'lda o'qish, tekshirish, metodni ajratish va xatolarni yozish kerak. Yozuvni o'chirish yoki yangilash qo'shilsa, kod tez ko'payadi. DRF aynan shu takrorlanuvchi ishni o'z zimmasiga oladi.</p>"""

_L1_TEXT_RU = """<h3>Что такое JSON API</h3>
<p>Вы уже писали во view-функциях Django HTML-страницы. <strong>JSON API</strong> возвращает вместо HTML <em>данные</em> (JSON), которые читает мобильное приложение, React или обычный JavaScript через <code>fetch</code>. В этом уроке мы напишем первую версию <strong>Notes API</strong> только средствами Django, без дополнительных библиотек. В следующих уроках мы сократим его с помощью Django REST Framework (DRF) и защитим.</p>
<pre class="mermaid">
flowchart LR
  A["Клиент: GET/POST /api/notes/"] --> B["urls.py: находит маршрут"]
  B --> C["view: читает и проверяет JSON"]
  C --> D["Модель Note: пишет/читает базу"]
  D --> E["JsonResponse + код статуса"]
</pre>

<h3>Подготовка проекта</h3>
<p>В существующем Django-проекте (<code>config</code>) создайте новое приложение, добавьте <code>"notes"</code> в <code>INSTALLED_APPS</code>, затем выполните:</p>
<pre><code>__SETUP__</code></pre>
<p>Модель простая: текст и время создания.</p>
<pre><code>__MODELS__</code></pre>

<h3>JsonResponse и view</h3>
<ul>
  <li><code>JsonResponse(dict)</code> превращает словарь в JSON и ставит <code>Content-Type: application/json</code>. Если возвращаете список, нужен <code>safe=False</code>.</li>
  <li><code>request.body</code> — сырые байты. Читаем их через <code>json.loads</code>; при неверном JSON возникает <code>JSONDecodeError</code>, поэтому возвращаем <code>400</code>.</li>
  <li>Коды статуса: <code>201</code> — создано, <code>400</code> — неверный запрос, <code>405</code> — метод не поддерживается.</li>
  <li><code>@csrf_exempt</code>: по умолчанию Django отклоняет POST без CSRF-токена. CSRF нужен для браузерных форм; в API с токенами он не нужен. В этом уроке мы временно отключаем его, а в следующих DRF решит это сам.</li>
</ul>
<pre><code>__VIEWS__</code></pre>
<p>Подключаем URL: <code>notes/urls.py</code> в приложении и префикс <code>/api/</code> в проекте.</p>
<pre><code>__URLS_APP__</code></pre>
<pre><code>__URLS_ROOT__</code></pre>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Первый запрос вернёт пустой список <code>[]</code>. Второй вернёт <code>201</code> и созданную запись. Отправьте пустой <code>text</code> или сломанный JSON и посмотрите на <code>400</code>.</p>

<h3>Недостаток этого подхода</h3>
<p>В каждом view приходится вручную читать JSON, проверять данные, разделять методы и писать ошибки. Если добавить удаление или обновление записи, кода станет быстро больше. DRF берёт на себя именно эту повторяющуюся работу.</p>"""

_L1_BLOCKS = dict(SETUP=SETUP_CMDS, MODELS=CODE_MODELS_L1, VIEWS=CODE_VIEWS_L1, URLS_APP=CODE_URLS_APP_L1,
                  URLS_ROOT=CODE_URLS_ROOT, CURL=CURL_L1)

LESSON_1 = {
    "order": 0,
    "title": "1-JsonResponse bilan oddiy API",
    "title_ru": "1-Простой API на JsonResponse",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": CODE_VIEWS_L1,
    "code_content_ru": CODE_VIEWS_L1,
    "code_language": "python",
    "sample": {
        "title": "Namuna: JsonResponse bilan Notes API",
        "title_ru": "Пример: Notes API на JsonResponse",
        "description": "Note modeli, JsonResponse qaytaradigan view, URL'lar va 400/201/405 holatlari.",
        "description_ru": "Модель Note, view с JsonResponse, URL и случаи 400/201/405.",
        "sample_type": "code",
        "code_files": [
            {"filename": "notes/models.py", "language": "python", "code": CODE_MODELS_L1},
            {"filename": "notes/views.py", "language": "python", "code": CODE_VIEWS_L1},
            {"filename": "notes/urls.py", "language": "python", "code": CODE_URLS_APP_L1},
            {"filename": "config/urls.py", "language": "python", "code": CODE_URLS_ROOT},
        ],
    },
    "exercises": [
        {
            "title": "Ro'yxat qaytarish", "title_ru": "Возврат списка",
            "description": "JsonResponse ga lug'at emas, ro'yxat berilsa qaysi parametr kerak?",
            "description_ru": "Какой параметр нужен, если в JsonResponse передаётся не словарь, а список?",
            "exercise_type": "multiple_choice",
            "options": ["safe=False", "list=True", "json=True", "strict=False"],
            "options_ru": ["safe=False", "list=True", "json=True", "strict=False"],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Django xavfsizlik uchun faqat lug'atni ruxsat etadi, bu cheklovni olib tashlash kerak.",
            "hint_ru": "Из соображений безопасности Django по умолчанию разрешает только словарь; это ограничение нужно снять.",
            "explanation": "JsonResponse standart holatda faqat dict qabul qiladi. Ro'yxat qaytarish uchun safe=False beriladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Yaratilgan javob kodi", "title_ru": "Код ответа при создании",
            "description": "Yangi yozuv yaratilgandan keyin qaytariladigan status kodi: status=___",
            "description_ru": "Код статуса, который возвращают после создания новой записи: status=___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "201",
            "hint": "200 emas: «yaratildi» uchun alohida kod bor.",
            "hint_ru": "Не 200: для «создано» есть отдельный код.",
            "explanation": "201 Created resurs yaratilganini bildiradi. 200 — oddiy muvaffaqiyat, 400 — mijoz xatosi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "POST so'rovi tartibi", "title_ru": "Порядок обработки POST",
            "description": "view POST so'rovini qanday tartibda qayta ishlashi kerakligini joylashtiring.",
            "description_ru": "Расположите порядок, в котором view должен обработать POST-запрос.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["request.body ni json.loads bilan o'qish", "text maydonini tekshirish", "Note.objects.create bilan saqlash", "201 bilan JsonResponse qaytarish"],
            "drag_items_ru": ["Прочитать request.body через json.loads", "Проверить поле text", "Сохранить через Note.objects.create", "Вернуть JsonResponse с кодом 201"],
            "correct_order": ["request.body ni json.loads bilan o'qish", "text maydonini tekshirish", "Note.objects.create bilan saqlash", "201 bilan JsonResponse qaytarish"],
            "hint": "Avval o'qiladi, keyin tekshiriladi, keyin saqlanadi.",
            "hint_ru": "Сначала читают, затем проверяют, затем сохраняют.",
            "explanation": "Tekshirilmagan ma'lumot bazaga yozilmaydi: o'qish, tekshirish, saqlash, javob berish tartibi shunday.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "To'g'ri javoblar", "title_ru": "Верные утверждения",
            "description": "Qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "JsonResponse Content-Type: application/json qo'yadi",
                "JSON API HTML sahifa qaytaradi",
                "Buzilgan JSON uchun 400 qaytarish to'g'ri",
                "request.body tayyor lug'at bo'lib keladi",
            ],
            "options_ru": [
                "JsonResponse ставит Content-Type: application/json",
                "JSON API возвращает HTML-страницу",
                "Для сломанного JSON правильно вернуть 400",
                "request.body приходит как готовый словарь",
            ],
            "correct_answers": "A,C", "is_multiple_select": True,
            "hint": "request.body — xom bayt, uni o'zingiz o'qiysiz.",
            "hint_ru": "request.body — это сырые байты, их нужно разобрать самому.",
            "explanation": "JsonResponse sarlavhani o'zi qo'yadi; noto'g'ri JSON mijoz xatosi (400). request.body xom bayt, JSON API esa HTML emas, ma'lumot qaytaradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega DRF kerak", "title_ru": "Зачем нужен DRF",
            "description": "JsonResponse bilan yozilgan API'ning qaysi kamchiliklari DRF kerakligini ko'rsatadi? O'z so'zingiz bilan yozing.",
            "description_ru": "Какие недостатки API на JsonResponse показывают, что нужен DRF? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Har bir view'da JSON'ni qo'lda o'qish, ma'lumotni tekshirish, metodlarni ajratish va xatolarni yozish kerak, kod takrorlanadi va endpoint ko'payganda tez o'sadi. DRF serializer va ViewSet bilan buni qisqartiradi.",
            "hint": "Qaysi ishlar har bir endpoint'da qayta-qayta yoziladi?",
            "hint_ru": "Какая работа повторяется в каждом эндпоинте?",
            "explanation": "Qo'lda parse, validatsiya va metod ajratish takrorlanadigan boilerplate. DRF serializer (tekshiruv) va ViewSet (CRUD) bilan buni umumlashtiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 2-dars: serializer va @api_view ──────────────────────────────────────────

_L2_TEXT_UZ = """<h3>Django REST Framework (DRF)</h3>
<p>DRF — Django uchun eng keng tarqalgan API kutubxonasi. O'rnatish va ulash:</p>
<pre><code>__PIP__</code></pre>
<pre><code>__SETTINGS__</code></pre>
<p>(Odatda bu qatorni <code>INSTALLED_APPS</code> ro'yxatining o'ziga qo'shasiz; bu yerda ko'rsatma uchun qisqa yozilgan.)</p>

<h3>Serializer: ma'lumot ↔ JSON</h3>
<p><strong>Serializer</strong> ikki ishni qiladi: modelni JSON'ga aylantiradi (chiqish) va kelgan JSON'ni tekshirib, modelga yozadi (kirish). <code>ModelSerializer</code> modelning maydonlaridan o'zi tuzadi. <code>read_only_fields</code> mijoz yubora olmaydigan maydonlar, <code>validate_&lt;maydon&gt;</code> esa shu maydon uchun o'zingizning tekshiruvingiz.</p>
<pre><code>__SERIALIZERS__</code></pre>

<h3>@api_view va Response</h3>
<p><code>@api_view([...])</code> oddiy funksiyani DRF view'iga aylantiradi: ruxsat etilgan metodlarni cheklaydi, JSON'ni <code>request.data</code> ga o'qiydi, <code>Response</code> esa JSON qaytaradi. <code>is_valid(raise_exception=True)</code> xato bo'lsa o'zi <code>400</code> qaytaradi: tekshiruv xabarlari maydon nomi bilan keladi. <code>get_object_or_404</code> topilmasa, DRF o'zi <code>404</code> JSON bilan javob beradi.</p>
<pre><code>__VIEWS__</code></pre>
<pre><code>__URLS__</code></pre>
<p>1-darsdagi kod bilan solishtiring: qo'lda <code>json.loads</code>, qo'lda tekshiruv va qo'lda status tanlash yo'qoldi.</p>

<h3>Xato javoblari qanday ko'rinadi</h3>
<ul>
  <li>Validatsiya xatosi: <code>400</code> va <code>{"text": ["text must be at least 3 characters"]}</code>.</li>
  <li>Yozuv topilmasa: <code>404</code> va <code>{"detail": "No Note matches the given query."}</code>.</li>
</ul>
<p>Brauzerda <code>http://127.0.0.1:8000/api/notes/</code> ni oching: DRF o'zining <em>Browsable API</em> sahifasini ko'rsatadi, u yerdan POST so'rovini ham yuborish mumkin.</p>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Avval 2 ta harfdan iborat matn yuboring (<code>400</code>), keyin to'g'ri matn yuboring (<code>201</code>).</p>"""

_L2_TEXT_RU = """<h3>Django REST Framework (DRF)</h3>
<p>DRF — самая распространённая библиотека для API на Django. Установка и подключение:</p>
<pre><code>__PIP__</code></pre>
<pre><code>__SETTINGS__</code></pre>
<p>(Обычно эту строку вы добавляете прямо в список <code>INSTALLED_APPS</code>; здесь она записана коротко для примера.)</p>

<h3>Сериализатор: данные ↔ JSON</h3>
<p><strong>Сериализатор</strong> делает две вещи: превращает модель в JSON (на выходе) и проверяет пришедший JSON, записывая его в модель (на входе). <code>ModelSerializer</code> сам строится по полям модели. <code>read_only_fields</code> — поля, которые клиент не может отправить, а <code>validate_&lt;поле&gt;</code> — ваша собственная проверка этого поля.</p>
<pre><code>__SERIALIZERS__</code></pre>

<h3>@api_view и Response</h3>
<p><code>@api_view([...])</code> превращает обычную функцию во view DRF: ограничивает допустимые методы, читает JSON в <code>request.data</code>, а <code>Response</code> возвращает JSON. <code>is_valid(raise_exception=True)</code> при ошибке сам вернёт <code>400</code>: сообщения проверки приходят с именем поля. Если <code>get_object_or_404</code> ничего не нашёл, DRF сам ответит <code>404</code> в формате JSON.</p>
<pre><code>__VIEWS__</code></pre>
<pre><code>__URLS__</code></pre>
<p>Сравните с кодом из урока 1: ручной <code>json.loads</code>, ручная проверка и ручной выбор статуса исчезли.</p>

<h3>Как выглядят ответы с ошибками</h3>
<ul>
  <li>Ошибка проверки: <code>400</code> и <code>{"text": ["text must be at least 3 characters"]}</code>.</li>
  <li>Запись не найдена: <code>404</code> и <code>{"detail": "No Note matches the given query."}</code>.</li>
</ul>
<p>Откройте в браузере <code>http://127.0.0.1:8000/api/notes/</code>: DRF покажет собственную страницу <em>Browsable API</em>, с которой можно отправить и POST-запрос.</p>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Сначала отправьте текст из 2 букв (<code>400</code>), затем корректный текст (<code>201</code>).</p>"""

_L2_BLOCKS = dict(PIP=PIP_DRF, SETTINGS=SETTINGS_REST_L2, SERIALIZERS=CODE_SERIALIZERS_L2, VIEWS=CODE_VIEWS_L2,
                  URLS=CODE_URLS_APP_L2, CURL=CURL_L1)

LESSON_2 = {
    "order": 1,
    "title": "2-DRF: serializer va @api_view",
    "title_ru": "2-DRF: сериализатор и @api_view",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": CODE_SERIALIZERS_L2,
    "code_content_ru": CODE_SERIALIZERS_L2,
    "code_language": "python",
    "sample": {
        "title": "Namuna: ModelSerializer va @api_view",
        "title_ru": "Пример: ModelSerializer и @api_view",
        "description": "NoteSerializer tekshiruv bilan, @api_view funksiyalari va URL'lar.",
        "description_ru": "NoteSerializer с проверкой, функции @api_view и URL.",
        "sample_type": "code",
        "code_files": [
            {"filename": "notes/serializers.py", "language": "python", "code": CODE_SERIALIZERS_L2},
            {"filename": "notes/views.py", "language": "python", "code": CODE_VIEWS_L2},
            {"filename": "notes/urls.py", "language": "python", "code": CODE_URLS_APP_L2},
        ],
    },
    "exercises": [
        {
            "title": "Serializer vazifasi", "title_ru": "Задача сериализатора",
            "description": "Serializer nima qiladi?",
            "description_ru": "Что делает сериализатор?",
            "exercise_type": "multiple_choice",
            "options": [
                "Modelni JSON'ga aylantiradi va kelgan JSON'ni tekshiradi",
                "Faqat URL'larni ro'yxatdan o'tkazadi",
                "Bazani migratsiya qiladi",
                "HTML shablonni chizadi",
            ],
            "options_ru": [
                "Превращает модель в JSON и проверяет пришедший JSON",
                "Только регистрирует URL",
                "Выполняет миграции базы",
                "Рисует HTML-шаблон",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "U ikki tomonga ishlaydi: chiqish va kirish.",
            "hint_ru": "Он работает в обе стороны: на выходе и на входе.",
            "explanation": "Serializer ma'lumotni modeldan JSON'ga va JSON'dan modelga o'tkazadi, shu bilan birga validatsiya qiladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Dekorator", "title_ru": "Декоратор",
            "description": "Oddiy funksiyani DRF view'iga aylantiradigan dekorator: @___([\"GET\", \"POST\"])",
            "description_ru": "Декоратор, превращающий обычную функцию во view DRF: @___([\"GET\", \"POST\"])",
            "exercise_type": "fill_in_blank",
            "correct_answers": "api_view",
            "hint": "Nomida «api» va «view» bor.",
            "hint_ru": "В названии есть «api» и «view».",
            "explanation": "@api_view metodlarni cheklaydi va request.data hamda Response bilan ishlash imkonini beradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Tekshirish tartibi", "title_ru": "Порядок проверки",
            "description": "POST so'rovining DRF'dagi tartibini joylashtiring.",
            "description_ru": "Расположите порядок обработки POST-запроса в DRF.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["NoteSerializer(data=request.data) yaratish", "is_valid(raise_exception=True)", "serializer.save()", "Response(..., status=201)"],
            "drag_items_ru": ["Создать NoteSerializer(data=request.data)", "is_valid(raise_exception=True)", "serializer.save()", "Response(..., status=201)"],
            "correct_order": ["NoteSerializer(data=request.data) yaratish", "is_valid(raise_exception=True)", "serializer.save()", "Response(..., status=201)"],
            "hint": "Saqlashdan oldin tekshirish bo'lishi shart.",
            "hint_ru": "Перед сохранением обязательно должна быть проверка.",
            "explanation": "Avval serializer yaratiladi, keyin tekshiriladi; faqat to'g'ri ma'lumot save() bilan yoziladi va 201 qaytadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Qaysi javoblar to'g'ri", "title_ru": "Какие ответы верны",
            "description": "Matni 2 ta harf bo'lgan so'rov yuborilsa nima bo'ladi? (Bir nechta javob)",
            "description_ru": "Что произойдёт, если отправить запрос с текстом из 2 букв? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Status kodi 400 bo'ladi",
                "Javobda «text» maydoni bo'yicha xabar bo'ladi",
                "Yozuv baribir bazaga yoziladi",
                "Status kodi 201 bo'ladi",
            ],
            "options_ru": [
                "Код статуса будет 400",
                "В ответе будет сообщение по полю «text»",
                "Запись всё равно запишется в базу",
                "Код статуса будет 201",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "validate_text xato ko'tarsa, save() chaqirilmaydi.",
            "hint_ru": "Если validate_text выбросит ошибку, save() не вызывается.",
            "explanation": "validate_text ValidationError ko'taradi, is_valid(raise_exception=True) 400 qaytaradi va maydon nomi bilan xabar beradi; yozuv saqlanmaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Faqat o'qiladigan maydonlar", "title_ru": "Поля только для чтения",
            "description": "Nega id va created_at read_only_fields ichiga qo'yilgan? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему id и created_at указаны в read_only_fields? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Bu maydonlarni server o'zi belgilaydi (id va yaratilgan vaqt), mijoz ularni yuborib o'zgartira olmasligi kerak. read_only bo'lsa ular faqat javobda chiqadi, kirishda e'tiborga olinmaydi.",
            "hint": "Mijozga qaysi qiymatlarni o'zgartirishga ruxsat bermaysiz?",
            "hint_ru": "Какие значения вы не хотите разрешать менять клиенту?",
            "explanation": "id va created_at ni server belgilaydi. read_only_fields ularni faqat chiqishda ko'rsatadi va mijoz yuborgan qiymatni rad etmasdan e'tiborsiz qoldiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: ViewSet va router ────────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>ViewSet: hamma amallar bir joyda</h3>
<p>2-darsda ro'yxat, yaratish, ko'rish va o'chirish uchun ikkita funksiya yozdik; yangilashni qo'shsak, uchinchisi kerak bo'lardi. <strong>ModelViewSet</strong> bu oltita amalni tayyor beradi: <code>list</code>, <code>create</code>, <code>retrieve</code>, <code>update</code>, <code>partial_update</code>, <code>destroy</code>. Siz faqat nimani va qanday serializer bilan ishlashni aytasiz.</p>
<pre><code>__VIEWS__</code></pre>

<h3>Router: URL'larni o'zi yaratadi</h3>
<p><code>DefaultRouter</code> ViewSet'dan URL'lar jadvalini tuzadi. Endi <code>urls.py</code> da har bir yo'lni qo'lda yozish shart emas:</p>
<pre><code>__URLS__</code></pre>
<pre class="mermaid">
flowchart TD
  R["router.register('notes', NoteViewSet)"] --> L["GET /api/notes/ → list"]
  R --> C["POST /api/notes/ → create"]
  R --> G["GET /api/notes/id/ → retrieve"]
  R --> U["PUT, PATCH /api/notes/id/ → update, partial_update"]
  R --> D["DELETE /api/notes/id/ → destroy"]
</pre>
<p>Router yana <code>/api/</code> manzilida <strong>API root</strong> sahifasini yaratadi: u mavjud resurslar ro'yxatini beradi.</p>

<h3>PUT va PATCH</h3>
<ul>
  <li><strong>PUT</strong> — yozuvni <em>to'liq</em> almashtiradi: barcha majburiy maydonlar yuborilishi kerak.</li>
  <li><strong>PATCH</strong> — <em>qisman</em> yangilaydi: faqat o'zgargan maydon yuboriladi.</li>
</ul>

<h3>Qachon ViewSet, qachon @api_view</h3>
<p>Oddiy CRUD resurs (yozuvlar, mahsulotlar, vazifalar) uchun ViewSet qulay: kod kam, URL'lar bir xil. Resursga to'g'ri kelmaydigan bitta alohida amal (masalan, ro'yxatdan o'tish yoki hisobot) uchun esa 2-darsdagidek <code>@api_view</code> yetarli. Ikkalasini bir loyihada aralashtirish mumkin va biz 4-darsda aynan shunday qilamiz.</p>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Natija 2-darsdagi bilan bir xil, lekin kod ancha qisqa. Yangilashni sinash uchun <code>curl -X PATCH http://127.0.0.1:8000/api/notes/1/</code> ga <code>{"text": "new text"}</code> yuboring.</p>"""

_L3_TEXT_RU = """<h3>ViewSet: все действия в одном месте</h3>
<p>В уроке 2 мы написали две функции для списка, создания, просмотра и удаления; с обновлением понадобилась бы третья. <strong>ModelViewSet</strong> даёт эти шесть действий готовыми: <code>list</code>, <code>create</code>, <code>retrieve</code>, <code>update</code>, <code>partial_update</code>, <code>destroy</code>. Вам остаётся только указать, с чем и с каким сериализатором работать.</p>
<pre><code>__VIEWS__</code></pre>

<h3>Роутер: сам создаёт URL</h3>
<p><code>DefaultRouter</code> строит таблицу URL по ViewSet. Теперь не нужно прописывать каждый путь в <code>urls.py</code> вручную:</p>
<pre><code>__URLS__</code></pre>
<pre class="mermaid">
flowchart TD
  R["router.register('notes', NoteViewSet)"] --> L["GET /api/notes/ → list"]
  R --> C["POST /api/notes/ → create"]
  R --> G["GET /api/notes/id/ → retrieve"]
  R --> U["PUT, PATCH /api/notes/id/ → update, partial_update"]
  R --> D["DELETE /api/notes/id/ → destroy"]
</pre>
<p>Роутер также создаёт по адресу <code>/api/</code> страницу <strong>API root</strong> со списком доступных ресурсов.</p>

<h3>PUT и PATCH</h3>
<ul>
  <li><strong>PUT</strong> — <em>полностью</em> заменяет запись: нужно отправить все обязательные поля.</li>
  <li><strong>PATCH</strong> — <em>частично</em> обновляет: отправляется только изменившееся поле.</li>
</ul>

<h3>Когда ViewSet, а когда @api_view</h3>
<p>Для обычного CRUD-ресурса (записи, товары, задачи) удобен ViewSet: кода мало, URL единообразные. Для отдельного действия, которое не вписывается в ресурс (например, регистрация или отчёт), достаточно <code>@api_view</code> из урока 2. Их можно смешивать в одном проекте, и в уроке 4 мы сделаем именно так.</p>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Результат такой же, как в уроке 2, но кода гораздо меньше. Чтобы проверить обновление, отправьте <code>curl -X PATCH http://127.0.0.1:8000/api/notes/1/</code> с телом <code>{"text": "new text"}</code>.</p>"""

_L3_BLOCKS = dict(VIEWS=CODE_VIEWS_L3, URLS=CODE_URLS_APP_L3, CURL=CURL_L1)

LESSON_3 = {
    "order": 2,
    "title": "3-ViewSet va router",
    "title_ru": "3-ViewSet и роутер",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": CODE_VIEWS_L3,
    "code_content_ru": CODE_VIEWS_L3,
    "code_language": "python",
    "sample": {
        "title": "Namuna: ModelViewSet va DefaultRouter",
        "title_ru": "Пример: ModelViewSet и DefaultRouter",
        "description": "Bitta ViewSet va router bilan to'liq CRUD API.",
        "description_ru": "Полный CRUD API на одном ViewSet и роутере.",
        "sample_type": "code",
        "code_files": [
            {"filename": "notes/views.py", "language": "python", "code": CODE_VIEWS_L3},
            {"filename": "notes/urls.py", "language": "python", "code": CODE_URLS_APP_L3},
        ],
    },
    "exercises": [
        {
            "title": "Nechta amal", "title_ru": "Сколько действий",
            "description": "ModelViewSet nechta tayyor amalni beradi?",
            "description_ru": "Сколько готовых действий даёт ModelViewSet?",
            "exercise_type": "multiple_choice",
            "options": ["2 ta", "4 ta", "6 ta", "10 ta"],
            "options_ru": ["2", "4", "6", "10"],
            "correct_answers": "C", "is_multiple_select": False,
            "hint": "Ro'yxat, yaratish, ko'rish, to'liq va qisman yangilash, o'chirish.",
            "hint_ru": "Список, создание, просмотр, полное и частичное обновление, удаление.",
            "explanation": "list, create, retrieve, update, partial_update va destroy: jami oltita amal.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Router klassi", "title_ru": "Класс роутера",
            "description": "ViewSet'dan URL'lar yaratadigan router: router = ___()",
            "description_ru": "Роутер, создающий URL из ViewSet: router = ___()",
            "exercise_type": "fill_in_blank",
            "correct_answers": "DefaultRouter",
            "hint": "Nomi «Default» so'zi bilan boshlanadi.",
            "hint_ru": "Название начинается со слова «Default».",
            "explanation": "DefaultRouter ro'yxat/detal URL'lari va API root sahifasini yaratadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Metod va amal", "title_ru": "Метод и действие",
            "description": "Qaysi juftlik to'g'ri?",
            "description_ru": "Какая пара верна?",
            "exercise_type": "multiple_choice",
            "options": [
                "DELETE /api/notes/1/ → create",
                "GET /api/notes/ → list",
                "POST /api/notes/1/ → retrieve",
                "PATCH /api/notes/ → destroy",
            ],
            "options_ru": [
                "DELETE /api/notes/1/ → create",
                "GET /api/notes/ → list",
                "POST /api/notes/1/ → retrieve",
                "PATCH /api/notes/ → destroy",
            ],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Ro'yxatni olish GET bilan bo'ladi.",
            "hint_ru": "Список получают методом GET.",
            "explanation": "GET /api/notes/ — list. create POST bilan, destroy DELETE bilan, retrieve esa GET /api/notes/<id>/ bilan.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "PUT yoki PATCH", "title_ru": "PUT или PATCH",
            "description": "Faqat text maydonini o'zgartirish uchun qaysi usullar mos? (Bir nechta javob)",
            "description_ru": "Какие способы подходят, чтобы изменить только поле text? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "PATCH bilan faqat text yuborish",
                "PUT bilan barcha majburiy maydonlarni yuborish",
                "POST bilan /api/notes/1/ ga yuborish",
                "GET bilan text'ni query'da yuborish",
            ],
            "options_ru": [
                "PATCH с отправкой только text",
                "PUT с отправкой всех обязательных полей",
                "POST на /api/notes/1/",
                "GET с text в query-параметре",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Yangilash uchun ikki metod bor.",
            "hint_ru": "Для обновления есть два метода.",
            "explanation": "PATCH qisman, PUT to'liq yangilaydi. Detail URL'ga POST yoki GET bilan yozuvni yangilab bo'lmaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "ViewSet yoki @api_view", "title_ru": "ViewSet или @api_view",
            "description": "Qachon ViewSet, qachon @api_view tanlaysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Когда вы выберете ViewSet, а когда @api_view? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Oddiy CRUD resurs uchun ViewSet qulay: kod kam, URL'lar router bilan o'zi yaratiladi. Resursga to'g'ri kelmaydigan alohida amal uchun (masalan, ro'yxatdan o'tish) oddiy @api_view funksiyasi yetarli.",
            "hint": "CRUD va bitta alohida amalni solishtiring.",
            "hint_ru": "Сравните CRUD и отдельное единичное действие.",
            "explanation": "ViewSet standart CRUD'ni umumlashtiradi, @api_view esa bitta maxsus endpoint uchun oddiy va aniq. Ikkalasi bir loyihada ishlaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: JWT autentifikatsiya ─────────────────────────────────────────────

_L4_TEXT_UZ = """<h3>Reja</h3>
<p>Hozir Notes API'ni istalgan kishi ochishi va boshqalarning yozuvlarini o'zgartirishi mumkin. Bu darsda <strong>JWT token</strong> bilan himoya qo'shamiz: foydalanuvchi ro'yxatdan o'tadi, login qilib token oladi, har so'rovda uni <code>Authorization: Bearer</code> sarlavhasida yuboradi va faqat o'z yozuvlarini ko'radi. (JWT token tuzilishi bilan tanish bo'lmasangiz: token — imzolangan, muddatli matn; server uni har so'rovda imzosi bo'yicha tekshiradi, sessiya saqlamaydi.)</p>
<pre><code>__PIP__</code></pre>
<p><strong>SimpleJWT</strong> DRF uchun tayyor token endpoint'larini beradi. Sozlamalar:</p>
<pre><code>__SETTINGS__</code></pre>
<ul>
  <li><code>DEFAULT_AUTHENTICATION_CLASSES</code> — DRF so'rovdagi tokenni shu klass orqali tekshiradi va <code>request.user</code> ni to'ldiradi.</li>
  <li><code>ACCESS_TOKEN_LIFETIME</code> — access tokenning amal qilish muddati.</li>
</ul>

<h3>Yozuv egasi: model o'zgarishi</h3>
<p>Har bir yozuvni foydalanuvchiga bog'laymiz. O'zgartirishdan keyin <code>makemigrations</code> va <code>migrate</code> ni yurgizing. Bazada eski yozuvlar bo'lsa, Django <code>owner</code> uchun standart qiymat so'raydi; o'quv loyihasida <code>db.sqlite3</code> ni o'chirib, qayta migrate qilish osonroq.</p>
<pre><code>__MODELS__</code></pre>

<h3>Register va himoyalangan ViewSet</h3>
<p>Serializer'ga <code>owner</code> (faqat o'qish) va ro'yxatdan o'tish uchun <code>RegisterSerializer</code> qo'shamiz. Parol <code>write_only</code>: javobda hech qachon qaytmaydi, <code>create_user</code> esa uni xeshlab saqlaydi.</p>
<pre><code>__SERIALIZERS__</code></pre>
<p>View'larda uchta yangilik bor:</p>
<ul>
  <li><code>permission_classes = [IsAuthenticated]</code> — tokensiz so'rov <code>401</code> bilan rad etiladi.</li>
  <li><code>get_queryset</code> — oddiy foydalanuvchiga faqat o'z yozuvlari ko'rinadi; <code>is_staff</code> bo'lsa hammasi. Boshqaning yozuviga murojaat qilsangiz, <code>404</code> keladi: ya'ni yozuv mavjudligi ham yashiriladi.</li>
  <li><code>perform_create</code> — saqlashda <code>owner</code> ni tokendan olingan <code>request.user</code> dan qo'yadi, mijoz yuborishi shart emas (va yubora olmaydi).</li>
</ul>
<pre class="mermaid">
flowchart TD
  A["So'rov + Authorization: Bearer"] --> B{"Token to'g'rimi?"}
  B -- "yo'q" --> C["401 Unauthorized"]
  B -- "ha" --> D{"Ruxsat bormi? (IsAuthenticated, IsAdminUser)"}
  D -- "yo'q" --> E["403 Forbidden"]
  D -- "ha" --> F["get_queryset: faqat o'z yozuvlari"]
</pre>
<pre><code>__VIEWS__</code></pre>
<p><code>IsAdminUser</code> faqat <code>is_staff=True</code> foydalanuvchilarga ruxsat beradi. Staff foydalanuvchini <code>python manage.py createsuperuser</code> bilan yaratish mumkin. Oddiy foydalanuvchi <code>/api/admin/users/</code> ga kirsa, <code>403</code> oladi.</p>

<h3>URL'lar va login</h3>
<p>Login uchun yangi view yozmaymiz: <code>TokenObtainPairView</code> loginni, parolni tekshiradi va <code>access</code> hamda <code>refresh</code> tokenlarini qaytaradi. <code>refresh</code> token yangi access olish uchun (<code>token/refresh/</code>), chunki access tokenning muddati qisqa.</p>
<pre><code>__URLS__</code></pre>

<h3>Sinab ko'ring</h3>
<pre><code>__CURL__</code></pre>
<p>Tokensiz so'rov <code>401</code>, noto'g'ri parol bilan login ham <code>401</code> qaytaradi. 401 va 403 ni aralashtirmang: 401 — «siz kimligingiz noma'lum», 403 — «kimligingiz ma'lum, lekin ruxsat yo'q».</p>"""

_L4_TEXT_RU = """<h3>План</h3>
<p>Сейчас Notes API может открыть кто угодно и изменить чужие записи. В этом уроке мы добавим защиту через <strong>JWT-токен</strong>: пользователь регистрируется, входит и получает токен, отправляет его в каждом запросе в заголовке <code>Authorization: Bearer</code> и видит только свои записи. (Если вы не знакомы со структурой JWT: токен — это подписанная строка с ограниченным сроком; сервер проверяет её по подписи при каждом запросе и не хранит сессию.)</p>
<pre><code>__PIP__</code></pre>
<p><strong>SimpleJWT</strong> даёт готовые эндпоинты токенов для DRF. Настройки:</p>
<pre><code>__SETTINGS__</code></pre>
<ul>
  <li><code>DEFAULT_AUTHENTICATION_CLASSES</code> — через этот класс DRF проверяет токен в запросе и заполняет <code>request.user</code>.</li>
  <li><code>ACCESS_TOKEN_LIFETIME</code> — срок действия access-токена.</li>
</ul>

<h3>Владелец записи: изменение модели</h3>
<p>Привяжем каждую запись к пользователю. После изменения выполните <code>makemigrations</code> и <code>migrate</code>. Если в базе уже есть записи, Django спросит значение по умолчанию для <code>owner</code>; в учебном проекте проще удалить <code>db.sqlite3</code> и выполнить migrate заново.</p>
<pre><code>__MODELS__</code></pre>

<h3>Регистрация и защищённый ViewSet</h3>
<p>Добавим в сериализатор поле <code>owner</code> (только чтение) и <code>RegisterSerializer</code> для регистрации. Пароль помечен <code>write_only</code>: в ответе он не возвращается никогда, а <code>create_user</code> сохраняет его в виде хеша.</p>
<pre><code>__SERIALIZERS__</code></pre>
<p>В view три новшества:</p>
<ul>
  <li><code>permission_classes = [IsAuthenticated]</code> — запрос без токена отклоняется с <code>401</code>.</li>
  <li><code>get_queryset</code> — обычный пользователь видит только свои записи; если <code>is_staff</code>, то все. При обращении к чужой записи придёт <code>404</code>: то есть существование записи тоже скрыто.</li>
  <li><code>perform_create</code> — при сохранении подставляет <code>owner</code> из <code>request.user</code>, полученного по токену; клиенту отправлять его не нужно (и нельзя).</li>
</ul>
<pre class="mermaid">
flowchart TD
  A["Запрос + Authorization: Bearer"] --> B{"Токен верный?"}
  B -- "нет" --> C["401 Unauthorized"]
  B -- "да" --> D{"Права есть? (IsAuthenticated, IsAdminUser)"}
  D -- "нет" --> E["403 Forbidden"]
  D -- "да" --> F["get_queryset: только свои записи"]
</pre>
<pre><code>__VIEWS__</code></pre>
<p><code>IsAdminUser</code> пускает только пользователей с <code>is_staff=True</code>. Staff-пользователя можно создать командой <code>python manage.py createsuperuser</code>. Если обычный пользователь зайдёт на <code>/api/admin/users/</code>, он получит <code>403</code>.</p>

<h3>URL и вход</h3>
<p>Для входа отдельный view не нужен: <code>TokenObtainPairView</code> проверяет логин и пароль и возвращает токены <code>access</code> и <code>refresh</code>. Токен <code>refresh</code> нужен, чтобы получить новый access (<code>token/refresh/</code>), потому что срок access-токена короткий.</p>
<pre><code>__URLS__</code></pre>

<h3>Проверьте сами</h3>
<pre><code>__CURL__</code></pre>
<p>Запрос без токена вернёт <code>401</code>, вход с неверным паролем тоже даст <code>401</code>. Не путайте 401 и 403: 401 — «вы неизвестны», 403 — «вы известны, но прав нет».</p>"""

_L4_BLOCKS = dict(PIP=PIP_JWT, SETTINGS=SETTINGS_JWT_L4, MODELS=CODE_MODELS_L4, SERIALIZERS=CODE_SERIALIZERS_L4,
                  VIEWS=CODE_VIEWS_L4, URLS=CODE_URLS_APP_L4, CURL=CURL_L4)

LESSON_4 = {
    "order": 3,
    "title": "4-JWT autentifikatsiya va faqat o'z yozuvlari",
    "title_ru": "4-JWT-аутентификация и доступ только к своим записям",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": CODE_VIEWS_L4,
    "code_content_ru": CODE_VIEWS_L4,
    "code_language": "python",
    "sample": {
        "title": "Namuna: JWT bilan himoyalangan Notes API",
        "title_ru": "Пример: Notes API под защитой JWT",
        "description": "SimpleJWT, register, IsAuthenticated, faqat o'z yozuvlari va IsAdminUser.",
        "description_ru": "SimpleJWT, регистрация, IsAuthenticated, только свои записи и IsAdminUser.",
        "sample_type": "code",
        "code_files": [
            {"filename": "notes/models.py", "language": "python", "code": CODE_MODELS_L4},
            {"filename": "notes/serializers.py", "language": "python", "code": CODE_SERIALIZERS_L4},
            {"filename": "notes/views.py", "language": "python", "code": CODE_VIEWS_L4},
            {"filename": "notes/urls.py", "language": "python", "code": CODE_URLS_APP_L4},
            {"filename": "config/settings_jwt.py", "language": "python", "code": SETTINGS_JWT_L4},
        ],
    },
    "exercises": [
        {
            "title": "Tokensiz so'rov", "title_ru": "Запрос без токена",
            "description": "IsAuthenticated bilan himoyalangan endpoint'ga tokensiz so'rov yuborilsa qaysi kod qaytadi?",
            "description_ru": "Какой код вернётся при запросе без токена к эндпоинту с IsAuthenticated?",
            "exercise_type": "multiple_choice",
            "options": ["200", "401", "403", "404"],
            "options_ru": ["200", "401", "403", "404"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "Foydalanuvchi kimligi umuman noma'lum.",
            "hint_ru": "Личность пользователя вообще неизвестна.",
            "explanation": "Token yo'q bo'lsa foydalanuvchi autentifikatsiyadan o'tmagan: 401 Unauthorized. 403 esa kim ekani ma'lum, lekin ruxsati yo'q holat.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Staff uchun ruxsat", "title_ru": "Права для staff",
            "description": "Faqat is_staff foydalanuvchilarga ruxsat beradigan permission klassi: ___",
            "description_ru": "Класс permission, пускающий только пользователей с is_staff: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "IsAdminUser",
            "hint": "Nomida «Admin» va «User» bor.",
            "hint_ru": "В названии есть «Admin» и «User».",
            "explanation": "IsAdminUser is_staff=True bo'lgan foydalanuvchilarga ruxsat beradi; qolganlar 403 oladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Token olish tartibi", "title_ru": "Порядок получения токена",
            "description": "Yangi foydalanuvchining tokenli ishlash tartibini joylashtiring.",
            "description_ru": "Расположите порядок работы нового пользователя с токеном.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["POST /api/register/", "POST /api/token/ (login, parol)", "access tokenni saqlash", "Authorization: Bearer bilan /api/notes/ ga so'rov"],
            "drag_items_ru": ["POST /api/register/", "POST /api/token/ (логин, пароль)", "Сохранить access-токен", "Запрос к /api/notes/ с Authorization: Bearer"],
            "correct_order": ["POST /api/register/", "POST /api/token/ (login, parol)", "access tokenni saqlash", "Authorization: Bearer bilan /api/notes/ ga so'rov"],
            "hint": "Token faqat login'dan keyin olinadi.",
            "hint_ru": "Токен выдаётся только после входа.",
            "explanation": "Avval ro'yxatdan o'tiladi, keyin token olinadi, saqlanadi va himoyalangan so'rovlarda yuboriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Boshqaning yozuvi", "title_ru": "Чужая запись",
            "description": "Ali vali'ning yozuvi id'si bilan DELETE yuborsa nima bo'ladi? (get_queryset faqat o'z yozuvlarini qaytaradi)",
            "description_ru": "Что произойдёт, если Али отправит DELETE с id записи Вали? (get_queryset возвращает только свои записи)",
            "exercise_type": "multiple_choice",
            "options": [
                "404: yozuv Ali uchun «mavjud emas»",
                "Yozuv o'chiriladi",
                "500: server xatosi",
                "201: yaratildi",
            ],
            "options_ru": [
                "404: для Али записи «не существует»",
                "Запись будет удалена",
                "500: ошибка сервера",
                "201: создано",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "ViewSet yozuvni get_queryset ichidan qidiradi.",
            "hint_ru": "ViewSet ищет запись внутри get_queryset.",
            "explanation": "Yozuv Ali ko'radigan queryset'da yo'q, shuning uchun topilmaydi: 404. Bu yozuv mavjudligini ham yashiradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Nega owner serverda", "title_ru": "Почему owner на сервере",
            "description": "Nega yozuv egasi (owner) mijoz yuborgan ma'lumotdan emas, perform_create ichida request.user dan olinadi? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему владелец записи (owner) берётся не из данных клиента, а из request.user в perform_create? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Agar owner mijozdan kelsa, foydalanuvchi boshqa birovning nomidan yozuv yarata oladi. request.user token orqali tasdiqlangan kimlik, shuning uchun uni serverda qo'yish ishonchli.",
            "hint": "Mijoz yuborgan qiymatga ishonib bo'ladimi?",
            "hint_ru": "Можно ли доверять значению, присланному клиентом?",
            "explanation": "Mijoz ma'lumoti soxtalashtirilishi mumkin. Tokendan olingan request.user esa server tasdiqlagan kimlik, shuning uchun egalik faqat shundan belgilanadi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: CORS, testlar, Postman ───────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Muammo: brauzer so'rovni to'sib qo'yadi</h3>
<p>Frontend <code>http://localhost:8080</code> da, API esa <code>http://127.0.0.1:8000</code> da ishlayotgan bo'lsin. Origin (manba) — protokol, domen va portning birikmasi; bular farq qilsa, manbalar <strong>turli</strong> hisoblanadi. Brauzer xavfsizlik uchun (same-origin siyosati) boshqa manbaga yuborilgan so'rovning <em>javobini</em> JavaScript'ga bermaydi, agar server buni aniq ruxsat etmasa. Konsolda <code>blocked by CORS policy</code> xatosini ko'rasiz. Bu server buzilganini bildirmaydi: so'rov yetib boradi, lekin brauzer javobni yashiradi, shuning uchun uni <strong>serverda</strong> to'g'rilaymiz.</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Brauzer (8080)
  participant S as Django API (8000)
  B->>S: OPTIONS /api/notes/ (Origin, Request-Headers)
  S-->>B: 200 + Access-Control-Allow-Origin va Allow-Headers
  B->>S: GET /api/notes/ (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p><code>Authorization</code> sarlavhasi yoki JSON <code>Content-Type</code> bilan so'rovdan oldin brauzer o'zi <code>OPTIONS</code> (preflight) so'rovi yuboradi. Server ruxsat bermasa, asl so'rov yuborilmaydi.</p>

<h3>django-cors-headers</h3>
<pre><code>__PIP__</code></pre>
<pre><code>__SETTINGS__</code></pre>
<ul>
  <li><code>CorsMiddleware</code> <code>CommonMiddleware</code> dan <strong>oldin</strong> turishi shart, aks holda sarlavhalar qo'shilmaydi.</li>
  <li><code>CORS_ALLOWED_ORIGINS</code> — ruxsat etilgan manbalar. Aniq manzillarni yozing; hamma saytga ruxsat (<code>CORS_ALLOW_ALL_ORIGINS</code>) tokenli API uchun xavfli.</li>
  <li><code>CORS_ALLOW_HEADERS</code> — <code>authorization</code> ni qo'shmasangiz, tokenli so'rov preflight'dan o'tmaydi.</li>
  <li><code>CORS_URLS_REGEX</code> — CORS faqat <code>/api/</code> yo'llariga qo'llanadi.</li>
</ul>
<p>Preflight'ni qo'lda sinang:</p>
<pre><code>__PRE__</code></pre>
<p>Javobda <code>Access-Control-Allow-Origin: http://localhost:8080</code> bo'lishi kerak; <code>http://evil.example</code> uchun bu sarlavha qaytmaydi.</p>

<h3>API testlari</h3>
<p><code>APITestCase</code> har test uchun alohida vaqtinchalik baza yaratadi va <code>self.client</code> (<code>APIClient</code>) beradi. <code>self.client.credentials(...)</code> har so'rovga <code>Authorization</code> sarlavhasini qo'shadi. Tokenning muddati o'tishini tekshirish uchun <code>AccessToken.for_user(user)</code> yaratib, <code>set_exp(lifetime=-timedelta(seconds=1))</code> bilan eskirtiramiz. Noto'g'ri yoki eskirgan token <code>401</code> va <code>"code": "token_not_valid"</code> bilan rad etiladi, frontend shu kod bo'yicha xatoni ajratadi.</p>
<pre><code>__TESTS__</code></pre>
<p>Ishga tushirish: <code>python manage.py test</code>.</p>

<h3>Frontend: fetch va token</h3>
<p>Frontend login javobidagi <code>access</code> tokenni <code>localStorage</code> da saqlaydi va har <code>fetch</code> so'roviga <code>Authorization: Bearer</code> sarlavhasi bilan qo'shadi. Server <code>401</code> qaytarsa, eski token o'chiriladi va foydalanuvchi qayta kiradi. Ogohlantirish: <code>localStorage</code> dagi token sahifadagi har qanday skriptga ko'rinadi (XSS xavfi); o'quv loyihasi uchun yetarli. To'liq frontend kodi 6-darsda.</p>

<h3>Postman</h3>
<ol>
  <li><strong>POST</strong> <code>/api/token/</code> so'rovini yuboring (Body → raw → JSON).</li>
  <li>Tokenni avtomatik saqlash uchun so'rovning <em>Tests</em> yorlig'iga yozing:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>Himoyalangan so'rovda <em>Authorization</em> yorlig'i → Type: <em>Bearer Token</em> → qiymat: <code>{{token}}</code>.</li>
</ol>"""

_L5_TEXT_RU = """<h3>Проблема: браузер блокирует запрос</h3>
<p>Пусть фронтенд работает на <code>http://localhost:8080</code>, а API — на <code>http://127.0.0.1:8000</code>. Origin (источник) — это сочетание протокола, домена и порта; если они отличаются, источники <strong>разные</strong>. В целях безопасности (политика same-origin) браузер не отдаёт JavaScript <em>ответ</em> на запрос к другому источнику, пока сервер явно этого не разрешит. В консоли вы увидите ошибку <code>blocked by CORS policy</code>. Это не значит, что сервер сломан: запрос доходит, но браузер скрывает ответ, поэтому исправляем её <strong>на сервере</strong>.</p>
<pre class="mermaid">
sequenceDiagram
  participant B as Браузер (8080)
  participant S as Django API (8000)
  B->>S: OPTIONS /api/notes/ (Origin, Request-Headers)
  S-->>B: 200 + Access-Control-Allow-Origin и Allow-Headers
  B->>S: GET /api/notes/ (Authorization: Bearer ...)
  S-->>B: 200 + JSON
</pre>
<p>Перед запросом с заголовком <code>Authorization</code> или JSON в <code>Content-Type</code> браузер сам отправляет <code>OPTIONS</code> (preflight). Если сервер не разрешил, основной запрос не отправляется.</p>

<h3>django-cors-headers</h3>
<pre><code>__PIP__</code></pre>
<pre><code>__SETTINGS__</code></pre>
<ul>
  <li><code>CorsMiddleware</code> должен стоять <strong>перед</strong> <code>CommonMiddleware</code>, иначе заголовки не добавятся.</li>
  <li><code>CORS_ALLOWED_ORIGINS</code> — разрешённые источники. Указывайте конкретные адреса; разрешение для всех сайтов (<code>CORS_ALLOW_ALL_ORIGINS</code>) опасно для API с токенами.</li>
  <li><code>CORS_ALLOW_HEADERS</code> — если не добавить <code>authorization</code>, запрос с токеном не пройдёт preflight.</li>
  <li><code>CORS_URLS_REGEX</code> — CORS действует только на пути <code>/api/</code>.</li>
</ul>
<p>Проверьте preflight вручную:</p>
<pre><code>__PRE__</code></pre>
<p>В ответе должен быть <code>Access-Control-Allow-Origin: http://localhost:8080</code>; для <code>http://evil.example</code> этот заголовок не вернётся.</p>

<h3>Тесты API</h3>
<p><code>APITestCase</code> создаёт для каждого теста отдельную временную базу и даёт <code>self.client</code> (<code>APIClient</code>). Вызов <code>self.client.credentials(...)</code> добавляет заголовок <code>Authorization</code> в каждый запрос. Чтобы проверить истечение срока токена, создаём <code>AccessToken.for_user(user)</code> и «старим» его через <code>set_exp(lifetime=-timedelta(seconds=1))</code>. Неверный или просроченный токен отклоняется с <code>401</code> и <code>"code": "token_not_valid"</code>; по этому коду фронтенд отличает ошибку.</p>
<pre><code>__TESTS__</code></pre>
<p>Запуск: <code>python manage.py test</code>.</p>

<h3>Фронтенд: fetch и токен</h3>
<p>Фронтенд сохраняет <code>access</code>-токен из ответа на вход в <code>localStorage</code> и добавляет его в каждый запрос <code>fetch</code> через заголовок <code>Authorization: Bearer</code>. Если сервер вернул <code>401</code>, старый токен удаляется и пользователь входит заново. Предупреждение: токен в <code>localStorage</code> виден любому скрипту на странице (риск XSS); для учебного проекта этого достаточно. Полный код фронтенда — в уроке 6.</p>

<h3>Postman</h3>
<ol>
  <li>Отправьте <strong>POST</strong>-запрос на <code>/api/token/</code> (Body → raw → JSON).</li>
  <li>Чтобы сохранять токен автоматически, на вкладке <em>Tests</em> запроса напишите:</li>
</ol>
<pre><code>__POSTMAN__</code></pre>
<ol start="3">
  <li>В защищённом запросе откройте вкладку <em>Authorization</em> → Type: <em>Bearer Token</em> → значение: <code>{{token}}</code>.</li>
</ol>"""

_L5_BLOCKS = dict(PIP=PIP_CORS, SETTINGS=SETTINGS_CORS_L5, PRE=CURL_PREFLIGHT, TESTS=CODE_TESTS_L5, POSTMAN=POSTMAN_SCRIPT)

LESSON_5 = {
    "order": 4,
    "title": "5-CORS, API testlari va Postman",
    "title_ru": "5-CORS, тесты API и Postman",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": SETTINGS_CORS_L5,
    "code_content_ru": SETTINGS_CORS_L5,
    "code_language": "python",
    "sample": {
        "title": "Namuna: CORS sozlamasi va 7 ta API testi",
        "title_ru": "Пример: настройка CORS и 7 тестов API",
        "description": "django-cors-headers sozlamalari va APITestCase bilan yozilgan testlar.",
        "description_ru": "Настройки django-cors-headers и тесты на APITestCase.",
        "sample_type": "code",
        "code_files": [
            {"filename": "config/settings_cors.py", "language": "python", "code": SETTINGS_CORS_L5},
            {"filename": "notes/tests.py", "language": "python", "code": CODE_TESTS_L5},
            {"filename": "api.js", "language": "javascript", "code": API_JS},
        ],
    },
    "exercises": [
        {
            "title": "Middleware o'rni", "title_ru": "Место middleware",
            "description": "CorsMiddleware MIDDLEWARE ro'yxatida qayerda turishi kerak?",
            "description_ru": "Где в списке MIDDLEWARE должен стоять CorsMiddleware?",
            "exercise_type": "multiple_choice",
            "options": ["Eng oxirida", "CommonMiddleware dan oldin", "SessionMiddleware dan keyin, istalgan joyda", "Ro'yxatga qo'shish shart emas"],
            "options_ru": ["В самом конце", "Перед CommonMiddleware", "После SessionMiddleware, в любом месте", "Добавлять в список не нужно"],
            "correct_answers": "B", "is_multiple_select": False,
            "hint": "U javoblarga sarlavha qo'shadi, shuning uchun erta ishlashi kerak.",
            "hint_ru": "Он добавляет заголовки к ответам, поэтому должен срабатывать рано.",
            "explanation": "CorsMiddleware CommonMiddleware dan oldin turishi kerak, aks holda CORS sarlavhalari qo'shilmasligi mumkin.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Preflight metodi", "title_ru": "Метод preflight",
            "description": "Brauzer preflight uchun qaysi HTTP metodini yuboradi? ___",
            "description_ru": "Какой HTTP-метод браузер отправляет для preflight? ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "OPTIONS",
            "hint": "U serverdan «nimalarga ruxsat bor?» deb so'raydi.",
            "hint_ru": "Он спрашивает сервер: «что разрешено?».",
            "explanation": "Preflight — OPTIONS so'rovi. Server Access-Control-Allow-* sarlavhalari bilan javob beradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Postman tartibi", "title_ru": "Порядок в Postman",
            "description": "Postman'da tokenli so'rov yuborish tartibini joylashtiring.",
            "description_ru": "Расположите шаги отправки запроса с токеном в Postman.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["/api/token/ so'rovini yuborish", "Tests skripti access'ni o'zgaruvchiga yozadi", "Authorization → Bearer Token: {{token}}", "Himoyalangan so'rovni yuborish"],
            "drag_items_ru": ["Отправить запрос /api/token/", "Скрипт Tests записывает access в переменную", "Authorization → Bearer Token: {{token}}", "Отправить защищённый запрос"],
            "correct_order": ["/api/token/ so'rovini yuborish", "Tests skripti access'ni o'zgaruvchiga yozadi", "Authorization → Bearer Token: {{token}}", "Himoyalangan so'rovni yuborish"],
            "hint": "Token avval olinadi, keyin ishlatiladi.",
            "hint_ru": "Сначала токен получают, потом используют.",
            "explanation": "Login javobidagi access token o'zgaruvchiga saqlanadi va keyingi so'rovlarda {{token}} orqali ishlatiladi.",
            "difficulty_level": "Easy", "points": 4,
        },
        {
            "title": "Qaysi sozlamalar kerak", "title_ru": "Какие настройки нужны",
            "description": "Frontend Authorization sarlavhasi bilan so'rov yuborishi uchun django-cors-headers'da nima bo'lishi kerak? (Bir nechta javob)",
            "description_ru": "Что должно быть в django-cors-headers, чтобы фронтенд мог отправлять запрос с заголовком Authorization? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "CORS_ALLOWED_ORIGINS ichida frontend manzili",
                "CORS_ALLOW_HEADERS ichida authorization",
                "Frontend kodida CORS xatosini try/catch bilan o'rash",
                "Tokenni URL'ga qo'shish",
            ],
            "options_ru": [
                "Адрес фронтенда в CORS_ALLOWED_ORIGINS",
                "authorization в CORS_ALLOW_HEADERS",
                "Обернуть ошибку CORS во фронтенде в try/catch",
                "Добавить токен в URL",
            ],
            "correct_answers": "A,B", "is_multiple_select": True,
            "hint": "Ikkala sozlama ham serverda qilinadi.",
            "hint_ru": "Обе настройки делаются на сервере.",
            "explanation": "Server frontend origin'ini ham, authorization sarlavhasini ham aniq ruxsat etishi kerak. try/catch CORS blokini olib tashlamaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Eskirgan token testi", "title_ru": "Тест просроченного токена",
            "description": "Testda muddati o'tgan tokenni qanday olasiz va nima uchun shunday qilasiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Как вы получите просроченный токен в тесте и почему именно так? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "AccessToken.for_user(user) bilan token yaratib, set_exp(lifetime=-timedelta(seconds=1)) bilan eskirtiraman: testda 30 daqiqa kutish shart emas, test tez ishlaydi. Server 401 va token_not_valid kodi bilan rad etishi kerak.",
            "hint": "Test tez ishlashi kerak, kutish yaramaydi.",
            "hint_ru": "Тест должен быть быстрым, ждать нельзя.",
            "explanation": "Salbiy muddat tokenni yaratilishi bilan eskirgan qiladi. Shu bilan kutmasdan 401 holatini tekshirish mumkin.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: takrorlash + loyiha ──────────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nimalarni o'rgandingiz</h3>
<ul>
  <li><strong>JsonResponse:</strong> Django'ning o'zida JSON API, status kodlar, <code>csrf_exempt</code>.</li>
  <li><strong>DRF:</strong> <code>ModelSerializer</code> bilan tekshiruv, <code>@api_view</code>, <code>Response</code>.</li>
  <li><strong>ViewSet:</strong> <code>ModelViewSet</code> va <code>DefaultRouter</code> bilan CRUD.</li>
  <li><strong>JWT:</strong> <code>SimpleJWT</code>, <code>IsAuthenticated</code>, faqat o'z yozuvlari, <code>IsAdminUser</code>.</li>
  <li><strong>CORS va testlar:</strong> <code>django-cors-headers</code>, <code>APITestCase</code>, Postman.</li>
</ul>

<h3>Production'ga chiqarishdan oldin</h3>
<ul>
  <li><code>SECRET_KEY</code> ni kodga yozmang, muhit o'zgaruvchisidan oling.</li>
  <li><code>DEBUG = False</code> va <code>ALLOWED_HOSTS</code> ga haqiqiy domen.</li>
  <li><code>CORS_ALLOWED_ORIGINS</code> ichida faqat haqiqiy frontend manzili (HTTPS).</li>
  <li>Access token muddatini qisqa, <code>refresh</code> ni esa ehtiyotkorlik bilan saqlang.</li>
</ul>

<h3>Tayyor yechim</h3>
<p>Pastda frontend: <code>index.html</code> va <code>api.js</code>. Serverni <code>python manage.py runserver</code> bilan, frontendni esa uning papkasida <code>python -m http.server 8080</code> bilan ishga tushiring: shunda manzil CORS'da ruxsat etilgan <code>http://localhost:8080</code> bilan mos keladi. Server kodi (models, serializers, views, urls va tests) 4- va 5-darslardagi bilan bir xil.</p>
<pre><code>__JS__</code></pre>
<pre><code>__HTML__</code></pre>
<p>Keyingi bosqich — vazifani o'zingiz bajarish: yuqoridagini ko'chirmasdan, o'z mavzuingizdagi yozuvlar (masalan, vazifalar yoki xarajatlar) uchun shu usulda tokenli API yozing.</p>"""

_L6_TEXT_RU = """<h3>Что вы изучили</h3>
<ul>
  <li><strong>JsonResponse:</strong> JSON API средствами самого Django, коды статуса, <code>csrf_exempt</code>.</li>
  <li><strong>DRF:</strong> проверка через <code>ModelSerializer</code>, <code>@api_view</code>, <code>Response</code>.</li>
  <li><strong>ViewSet:</strong> CRUD на <code>ModelViewSet</code> и <code>DefaultRouter</code>.</li>
  <li><strong>JWT:</strong> <code>SimpleJWT</code>, <code>IsAuthenticated</code>, доступ только к своим записям, <code>IsAdminUser</code>.</li>
  <li><strong>CORS и тесты:</strong> <code>django-cors-headers</code>, <code>APITestCase</code>, Postman.</li>
</ul>

<h3>Перед выходом в production</h3>
<ul>
  <li>Не храните <code>SECRET_KEY</code> в коде, берите из переменной окружения.</li>
  <li><code>DEBUG = False</code> и настоящий домен в <code>ALLOWED_HOSTS</code>.</li>
  <li>В <code>CORS_ALLOWED_ORIGINS</code> только настоящий адрес фронтенда (HTTPS).</li>
  <li>Делайте срок access-токена коротким, а <code>refresh</code> храните осторожно.</li>
</ul>

<h3>Готовое решение</h3>
<p>Ниже фронтенд: <code>index.html</code> и <code>api.js</code>. Запустите сервер командой <code>python manage.py runserver</code>, а фронтенд — командой <code>python -m http.server 8080</code> в его папке: тогда адрес совпадёт с разрешённым в CORS <code>http://localhost:8080</code>. Код сервера (models, serializers, views, urls и tests) такой же, как в уроках 4 и 5.</p>
<pre><code>__JS__</code></pre>
<pre><code>__HTML__</code></pre>
<p>Следующий этап — выполнить задание самостоятельно: не копируя код выше, напишите API с токеном для записей на свою тему (например, задачи или расходы) тем же способом.</p>"""

LESSON_6 = {
    "order": 5,
    "title": "6-Takrorlash: tokenli Notes API + oddiy frontend",
    "title_ru": "6-Повторение: Notes API с токеном + простой фронтенд",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, JS=API_JS, HTML=INDEX_HTML),
    "text_content_ru": _fill(_L6_TEXT_RU, JS=API_JS, HTML=INDEX_HTML),
    "code_content": API_JS,
    "code_content_ru": API_JS,
    "code_language": "javascript",
    "sample": {
        "title": "Namuna: tokenli Notes API (to'liq loyiha)",
        "title_ru": "Пример: Notes API с токеном (полный проект)",
        "description": "Server kodi, testlar va fetch bilan ishlaydigan oddiy frontend.",
        "description_ru": "Код сервера, тесты и простой фронтенд на fetch.",
        "sample_type": "code",
        "code_files": [
            {"filename": "notes/models.py", "language": "python", "code": CODE_MODELS_L4},
            {"filename": "notes/serializers.py", "language": "python", "code": CODE_SERIALIZERS_L4},
            {"filename": "notes/views.py", "language": "python", "code": CODE_VIEWS_L4},
            {"filename": "notes/urls.py", "language": "python", "code": CODE_URLS_APP_L4},
            {"filename": "notes/tests.py", "language": "python", "code": CODE_TESTS_L5},
            {"filename": "config/settings_extra.py", "language": "python", "code": SETTINGS_REST_L2 + "\n" + SETTINGS_JWT_L4 + "\n" + SETTINGS_CORS_L5},
            {"filename": "api.js", "language": "javascript", "code": API_JS},
            {"filename": "index.html", "language": "html", "code": INDEX_HTML},
        ],
    },
    "task": {
        "task_title": "Loyiha: tokenli yozuvlar API'si (Django) + oddiy frontend",
        "task_title_ru": "Проект: API записей с токеном (Django) + простой фронтенд",
        "task_description": "O'zingiz tanlagan mavzu (vazifalar, xarajatlar, kitoblar...) uchun Django REST Framework API yozing: foydalanuvchi ro'yxatdan o'tadi, kiradi va faqat o'z yozuvlarini boshqaradi. Staff foydalanuvchi hammasini ko'radi. Oddiy HTML/JavaScript frontend login qiladi va yozuvlar ro'yxatini ko'rsatadi.",
        "task_description_ru": "Напишите API на Django REST Framework для выбранной вами темы (задачи, расходы, книги...): пользователь регистрируется, входит и управляет только своими записями. Staff-пользователь видит всё. Простой HTML/JavaScript-фронтенд выполняет вход и показывает список записей.",
        "task_requirements": (
            "1) ModelSerializer va validate_ usuli bilan kamida bitta tekshiruv. "
            "2) ModelViewSet va DefaultRouter bilan CRUD. "
            "3) POST /api/register/ va /api/token/ (SimpleJWT): login access token qaytaradi. "
            "4) IsAuthenticated, faqat o'z yozuvlari (get_queryset) va IsAdminUser bilan faqat staff uchun endpoint. "
            "5) django-cors-headers: faqat frontend manzili ruxsat etilgan, authorization sarlavhasi bilan. "
            "6) fetch bilan oddiy frontend: login va yozuvlar ro'yxati, token localStorage'da. "
            "7) APITestCase bilan kamida 3 ta test."
        ),
        "task_requirements_ru": (
            "1) ModelSerializer и хотя бы одна проверка через метод validate_. "
            "2) CRUD на ModelViewSet и DefaultRouter. "
            "3) POST /api/register/ и /api/token/ (SimpleJWT): вход возвращает access-токен. "
            "4) IsAuthenticated, доступ только к своим записям (get_queryset) и эндпоинт только для staff через IsAdminUser. "
            "5) django-cors-headers: разрешён только адрес фронтенда, с заголовком authorization. "
            "6) Простой фронтенд на fetch: вход и список записей, токен в localStorage. "
            "7) Не менее 3 тестов на APITestCase."
        ),
        "task_technologies": "Django, Django REST Framework, SimpleJWT, django-cors-headers, JavaScript",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Hammasini bog'lang", "title_ru": "Соедините всё вместе",
            "description": "Qaysi variant «token bilan ishlovchi to'liq API»ning to'g'ri tartibini ko'rsatadi?",
            "description_ru": "Какой вариант показывает верный порядок работы API с токеном?",
            "exercise_type": "multiple_choice",
            "options": [
                "login → access token → Authorization: Bearer bilan himoyalangan so'rov",
                "himoyalangan so'rov → login → token",
                "token → login → parol",
                "parolni har so'rovda URL ichida yuborish",
            ],
            "options_ru": [
                "вход → access-токен → защищённый запрос с Authorization: Bearer",
                "защищённый запрос → вход → токен",
                "токен → вход → пароль",
                "отправлять пароль в URL при каждом запросе",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Token faqat login'dan keyin paydo bo'ladi.",
            "hint_ru": "Токен появляется только после входа.",
            "explanation": "Parol faqat login paytida yuboriladi, keyin barcha so'rovlar access token bilan ketadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Testlar buyrug'i", "title_ru": "Команда запуска тестов",
            "description": "Django testlarini ishga tushiradigan buyruq: python manage.py ___",
            "description_ru": "Команда запуска тестов Django: python manage.py ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "test",
            "hint": "Buyruq nomi bitta so'z: «test».",
            "hint_ru": "Название команды — одно слово: «test».",
            "explanation": "python manage.py test barcha test.py fayllaridagi testlarni ishga tushiradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Loyihani tekshirish", "title_ru": "Проверка проекта",
            "description": "Loyihangiz xavfsiz ekanini qaysi tekshiruvlar bilan isbotlaysiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Какими проверками вы докажете, что ваш проект безопасен? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Tokensiz so'rov 401 qaytarishini, boshqa foydalanuvchining yozuvi 404 bo'lishini, oddiy foydalanuvchi staff endpoint'iga kira olmasligini (403) va CORS faqat frontend manziliga ruxsat berishini APITestCase bilan tekshiraman.",
            "hint": "401, 403, 404 va CORS holatlarini o'ylab ko'ring.",
            "hint_ru": "Подумайте о случаях 401, 403, 404 и CORS.",
            "explanation": "Testlar himoyaning har qatlamini tekshiradi: token, egalik, rol va CORS. Shu holatlar bo'lsa, loyiha asosiy xavfsizlik talablarini qoplaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
