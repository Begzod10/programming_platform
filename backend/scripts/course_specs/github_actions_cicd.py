"""Intermediate/Advanced CI/CD course: GitHub Actions built around Git,
course 2 of 3 in the "Git & collaboration workflows" track, past course 112.

Course 45 ("Git va GitHub", Beginner) taught basic commit/branch/PR/conflict
workflow and briefly introduced GitHub Actions as a topic name. Course 112
("Git: Ichki Tuzilishi va Ilg'or Workflow", Intermediate, prerequisite 45)
went deep on Git internals (objects/SHA-1, refs/HEAD, packfile/gc),
interactive rebase, bisect, worktree, submodule/subtree, git hooks
(pre-commit/pre-push), rerere/merge strategies, and monorepo sparse-
checkout/partial clone — grounded in this repo's own structure and its real
.github/workflows/*.yml files (referenced there only as an example of what
a hook cannot replace).

THIS course goes the other direction: the student already understands how
Git stores and moves data. Now teach them how a team builds an automated
pipeline ON TOP of Git events — GitHub Actions. Every concrete example is
grounded in this repository's actual three workflows:
  - .github/workflows/test.yml            (backend pytest + frontend Jest)
  - .github/workflows/deploy-backend.yml   (SSH + systemctl restart on push)
  - .github/workflows/deploy-frontend.yml  (build in CI, rsync to prod)

Built with the course_builder scaffold — see course_builder/__init__.py for
the spec contract. Every lesson gets both task + sample from the start,
full UZ+RU authored here (not machine-translated), Mermaid diagrams where
pedagogically justified. is_published stays False — human review first.
"""

COURSE = {
    "title": "GitHub Actions va CI/CD Chuqur",
    "description": (
        "Git: Ichki Tuzilishi va Ilg'or Workflow (112-kurs) Git'ning o'zini "
        "chuqur o'rgatgan — obyektlar, refs, rebase, hook'lar. Bu kurs xuddi "
        "shu bilim ustiga CI/CD'ni quradi: GitHub Actions workflow'i qanday "
        "yoziladi (YAML anatomiyasi — on/jobs/steps/runs-on), qaysi event'lar "
        "uni ishga tushiradi (push, pull_request, schedule, workflow_dispatch), "
        "sirlar va environment o'zgaruvchilari qanday xavfsiz uzatiladi "
        "(GITHUB_TOKEN, repo secrets, environments), matrix build orqali bir "
        "nechta versiyada parallel test, actions/cache orqali bog'liqliklarni "
        "keshlash, artifact'lar orqali build natijalarini saqlash va "
        "uzatish, branch himoya qoidalari va required status check'lar, "
        "qayta ishlatiladigan workflow'lar (workflow_call) va composite "
        "action'lar, self-hosted vs GitHub-hosted runner'lar, va nihoyat "
        "muvaffaqiyatsiz CI'ni disk qilish (log'larni o'qish, job'ni qayta "
        "ishga tushirish, keng tarqalgan xato turlari). Har bir mavzu ushbu "
        "platformaning haqiqiy uchta workflow fayli — test.yml, "
        "deploy-backend.yml, deploy-frontend.yml — misolida o'rgatiladi, "
        "o'ylab topilgan generik YAML emas. Kurs capstone loyihasi bilan "
        "yakunlanadi: CI/CD'ni 112-kursdagi Git ichki tuzilishi bilimlari "
        "bilan bog'lab, real avtomatlashtirilgan pipeline qurish."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 5,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 11,
    "prerequisite_course_id": 112,
    "display_order": 602,
    "image_url": "https://github.githubassets.com/images/modules/site/features/actions-icon-actions.svg",
    "thumbnail_url": "https://icon.icepanel.io/Technology/svg/GitHub-Actions.svg",
    "is_active": True,
    "is_published": False,
}

# ---------------------------------------------------------------------------
# Lesson 0 — GitHub Actions asoslari: workflow YAML anatomiyasi
# ---------------------------------------------------------------------------

L0_TEXT = """
<h3>Nima uchun Git bilimidan keyin CI/CD?</h3>
<p>112-kursda siz Git'ning ichki tuzilishini — obyektlar, refs, packfile,
hook'lar — chuqur o'rgandingiz. Ammo real jamoada kod <code>git push</code>
qilingandan keyin nima bo'ladi? Kimdir qo'lda testlarni ishga tushirib,
qo'lda serverga joylashtirmaydi — bu sekin va xatoga moyil. <strong>GitHub
Actions</strong> — GitHub'ning o'ziga xos CI/CD (Continuous
Integration/Continuous Deployment) platformasi: Git repozitoriyasidagi
voqealarga (push, pull request va h.k.) javoban avtomatik ravishda kod
ishga tushiriladigan muhit. Bu platformaning o'zi aynan shu texnologiyadan
foydalanadi — <code>.github/workflows/</code> papkasida uchta real workflow
fayli bor, va shu kurs davomida ularning HAR BIRINI qatma-qat o'rganamiz.</p>

<h3>Workflow fayli qayerda yashaydi</h3>
<p>Har qanday GitHub Actions workflow'i repozitoriyaning ildizidagi
<code>.github/workflows/</code> papkasida, <code>.yml</code> yoki
<code>.yaml</code> kengaytmali fayl sifatida yashaydi. GitHub bu papkani
avtomatik skanerlaydi — alohida ro'yxatdan o'tkazish shart emas. Ushbu
platformada uchta fayl bor: <code>test.yml</code>, <code>deploy-backend.yml</code>,
<code>deploy-frontend.yml</code> — har biri mustaqil workflow, bir-biridan
xabarsiz ishlaydi (agar maxsus bog'lanmagan bo'lsa).</p>

<h3>Uch asosiy daraja: workflow, job, step</h3>
<p>Har bir workflow YAML fayli uchta ierarxik darajadan iborat:</p>
<ul>
<li><strong>workflow</strong> — butun fayl; <code>name:</code> kaliti unga
inson o'qiy oladigan nom beradi (GitHub UI'da "Actions" bo'limida shu nom
ko'rinadi) va <code>on:</code> kaliti qaysi event'lar uni ishga tushirishini
belgilaydi.</li>
<li><strong>job</strong> — <code>jobs:</code> kaliti ostida bitta yoki bir
nechta job aniqlanadi; har bir job <code>runs-on:</code> orqali qaysi
virtual mashinada (masalan <code>ubuntu-latest</code>) ishlashini
belgilaydi. Standart holatda barcha job'lar <strong>parallel</strong>
ishga tushadi — bir-birini kutmaydi, agar <code>needs:</code> orqali
maxsus bog'liqlik ko'rsatilmagan bo'lsa.</li>
<li><strong>step</strong> — job ichidagi <code>steps:</code> ro'yxati; har
bir step yoki tayyor action'ni ishlatadi (<code>uses:</code>), yoki oddiy
shell buyrug'ini bajaradi (<code>run:</code>). Step'lar job ICHIDA doim
KETMA-KET bajariladi, yuqoridan pastga.</li>
</ul>

<h3>uses vs run — ikki xil step turi</h3>
<p><code>uses:</code> — GitHub Marketplace'dagi yoki boshqa repozitoriyadagi
tayyor, qayta ishlatiladigan action'ni chaqiradi (masalan
<code>actions/checkout@v4</code> — repozitoriyani runner'ga klonlaydi).
Versiya <code>@v4</code> kabi tag orqali qat'iy belgilanishi kerak — versiya
ko'rsatilmasa, action muallifi uni istalgan vaqtda o'zgartirib, workflow'ni
kutilmaganda buzishi mumkin. <code>run:</code> — runner'ning shell'ida
(odatda bash) to'g'ridan-to'g'ri buyruq bajaradi, xuddi terminalga
yozgandek. Ikkalasi ham bitta step ichida BIRGA bo'la olmaydi — har bir
step yo <code>uses</code>, yo <code>run</code> ishlatadi, ikkalasi emas.</p>

<h3>Workflow, job'lar va step'lar orasidagi munosabat</h3>
<pre class="mermaid">
flowchart TB
  W["test.yml workflow
name: Tests"] --> J1["job: backend
runs-on: ubuntu-latest"]
  W --> J2["job: frontend
runs-on: ubuntu-latest"]
  J1 --> S1["step: actions/checkout@v4"]
  S1 --> S2["step: actions/setup-python@v5"]
  S2 --> S3["step: run pip install -r requirements.txt"]
  S3 --> S4["step: run pytest tests/ -v"]
  J2 --> S5["step: actions/checkout@v4"]
  S5 --> S6["step: actions/setup-node@v4"]
  S6 --> S7["step: run npm ci"]
  S7 --> S8["step: run react-scripts test"]
  style J1 fill:#d6e9ff,stroke:#2266aa
  style J2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma ushbu platformaning haqiqiy <code>test.yml</code> faylidan olingan:
bitta workflow ichida ikkita mustaqil job (<code>backend</code> va
<code>frontend</code>) parallel ishga tushadi, har biri o'z step'lar
zanjiriga ega. Ikkala job ham checkout bilan boshlanadi (kod runner'ga
kerak), so'ng til muhitini o'rnatadi, bog'liqliklarni o'rnatadi, va
oxirida testlarni ishga tushiradi — bu odatiy CI job tuzilishi.</p>

<h3>runs-on — qaysi mashinada ishlaydi</h3>
<p><code>runs-on: ubuntu-latest</code> — GitHub'ning o'zi taqdim etadigan,
vaqtinchalik (ephemeral) virtual mashina: har bir job yangi, toza muhitda
boshlanadi, tugagandan keyin butunlay o'chiriladi. Shu sababli har safar
bog'liqliklarni qaytadan o'rnatish kerak (keyingi darslarda buni
<code>actions/cache</code> bilan tezlashtirishni o'rganamiz). Muqobil
qiymatlar: <code>windows-latest</code>, <code>macos-latest</code>, yoki
<code>self-hosted</code> (10-darsda ko'ramiz).</p>
""".strip()

L0_TEXT_RU = """
<h3>Зачем CI/CD после знаний о Git?</h3>
<p>В курсе 112 вы глубоко изучили внутреннее устройство Git — объекты,
refs, packfile, hooks. Но что происходит в реальной команде после
<code>git push</code>? Никто не запускает тесты вручную и не разворачивает
код на сервере руками — это медленно и подвержено ошибкам.
<strong>GitHub Actions</strong> — собственная CI/CD (Continuous
Integration/Continuous Deployment) платформа GitHub: среда, где код
автоматически запускается в ответ на события в Git-репозитории (push,
pull request и т.д.). Сама эта платформа использует именно эту технологию —
в папке <code>.github/workflows/</code> лежат три реальных файла workflow,
и на протяжении этого курса мы изучим КАЖДЫЙ из них по порядку.</p>

<h3>Где живёт файл workflow</h3>
<p>Любой workflow GitHub Actions живёт в папке <code>.github/workflows/</code>
в корне репозитория, в виде файла с расширением <code>.yml</code> или
<code>.yaml</code>. GitHub автоматически сканирует эту папку — отдельная
регистрация не нужна. В этой платформе три файла:
<code>test.yml</code>, <code>deploy-backend.yml</code>,
<code>deploy-frontend.yml</code> — каждый независимый workflow, работает,
не зная о другом (если не связан специально).</p>

<h3>Три основных уровня: workflow, job, step</h3>
<p>Каждый YAML-файл workflow состоит из трёх иерархических уровней:</p>
<ul>
<li><strong>workflow</strong> — весь файл; ключ <code>name:</code> даёт ему
человекочитаемое имя (это имя видно в разделе "Actions" GitHub UI), а ключ
<code>on:</code> определяет, какие события его запускают.</li>
<li><strong>job</strong> — под ключом <code>jobs:</code> определяется один
или несколько job'ов; каждый job через <code>runs-on:</code> задаёт, на
какой виртуальной машине он работает (например <code>ubuntu-latest</code>).
По умолчанию все job'ы запускаются <strong>параллельно</strong> — не ждут
друг друга, если не указана специальная зависимость через
<code>needs:</code>.</li>
<li><strong>step</strong> — список <code>steps:</code> внутри job; каждый
step либо использует готовый action (<code>uses:</code>), либо выполняет
обычную shell-команду (<code>run:</code>). Внутри job'а step'ы ВСЕГДА
выполняются ПОСЛЕДОВАТЕЛЬНО, сверху вниз.</li>
</ul>

<h3>uses против run — два типа step</h3>
<p><code>uses:</code> — вызывает готовый, переиспользуемый action из
GitHub Marketplace или другого репозитория (например
<code>actions/checkout@v4</code> — клонирует репозиторий на runner).
Версия вроде <code>@v4</code> должна быть строго зафиксирована тегом —
если версия не указана, автор action может изменить его в любой момент и
неожиданно сломать workflow. <code>run:</code> — выполняет команду
напрямую в shell раннера (обычно bash), как будто вы напечатали её в
терминале. Оба вместе в одном step быть не могут — каждый step использует
либо <code>uses</code>, либо <code>run</code>, но не оба сразу.</p>

<h3>Связь между workflow, job'ами и step'ами</h3>
<pre class="mermaid">
flowchart TB
  W["workflow test.yml
name: Tests"] --> J1["job: backend
runs-on: ubuntu-latest"]
  W --> J2["job: frontend
runs-on: ubuntu-latest"]
  J1 --> S1["step: actions/checkout@v4"]
  S1 --> S2["step: actions/setup-python@v5"]
  S2 --> S3["step: run pip install -r requirements.txt"]
  S3 --> S4["step: run pytest tests/ -v"]
  J2 --> S5["step: actions/checkout@v4"]
  S5 --> S6["step: actions/setup-node@v4"]
  S6 --> S7["step: run npm ci"]
  S7 --> S8["step: run react-scripts test"]
  style J1 fill:#d6e9ff,stroke:#2266aa
  style J2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма взята из реального файла <code>test.yml</code> этой платформы:
внутри одного workflow два независимых job'а (<code>backend</code> и
<code>frontend</code>) запускаются параллельно, у каждого своя цепочка
step'ов. Оба job'а начинаются с checkout (код нужен на runner'е), затем
настраивают языковую среду, устанавливают зависимости и в конце запускают
тесты — это типичная структура CI job'а.</p>

<h3>runs-on — на какой машине выполняется</h3>
<p><code>runs-on: ubuntu-latest</code> — виртуальная машина, которую
предоставляет сам GitHub, временная (эфемерная): каждый job начинается в
новой, чистой среде и полностью удаляется после завершения. Поэтому
зависимости приходится устанавливать заново каждый раз (в следующих уроках
мы ускорим это через <code>actions/cache</code>). Альтернативные значения:
<code>windows-latest</code>, <code>macos-latest</code>, или
<code>self-hosted</code> (увидим в уроке 10).</p>
""".strip()

L0_CODE = """
# ============================================================
# 1) test.yml — ushbu platformaning haqiqiy workflow fayli
#    (.github/workflows/test.yml, to'liq holicha)
# ============================================================
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    name: Backend (pytest)
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci --no-audit --no-fund

      - name: Run tests
        working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests

# ============================================================
# 2) Anatomiyani qatma-qat o'qish
# ============================================================
# name: Tests                    <- workflow darajasi: GitHub UI'da shu
#                                    nom "Actions" bo'limida ko'rinadi
#
# on: push / pull_request        <- workflow darajasi: qachon ishga tushadi
#                                    (keyingi darsda batafsil)
#
# jobs:                          <- ikkita mustaqil job: backend, frontend
#   backend:                     <- job darajasi
#     runs-on: ubuntu-latest     <- qaysi virtual mashinada
#     timeout-minutes: 10        <- job 10 daqiqadan ko'p ketsa, majburan
#                                    to'xtatiladi (osilib qolgan testni
#                                    abadiy kutmaslik uchun)
#     steps:                     <- step darajasi, KETMA-KET bajariladi
#       - uses: actions/checkout@v4          <- 1-step: tayyor action
#       - name: Set up Python                <- "name" ixtiyoriy — UI'da
#         uses: actions/setup-python@v5           chiroyli ko'rsatish uchun
#       - name: Install dependencies          <- 3-step: run bilan
#         run: pip install -r requirements.txt

# ============================================================
# 3) working-directory — nega backend/frontend prefiksi bor
# ============================================================
# actions/checkout@v4 BUTUN repozitoriyani (backend/ va frontend/ ikkalasini
# ham) runner'ga klonlaydi. Lekin backend job'ining "Install dependencies"
# step'i faqat backend/requirements.txt bilan ishlashi kerak — shuning uchun
# har bir run: qatoriga alohida "working-directory: backend" yozilgan.
# Buni yozmasangiz, `pip install -r requirements.txt` ildiz papkada
# requirements.txt qidiradi va topolmay, xato beradi.

$ ls .github/workflows/
deploy-backend.yml  deploy-frontend.yml  test.yml

# ============================================================
# 4) Workflow'ni GitHub UI'dan kuzatish
# ============================================================
# Reponing "Actions" tabiga o'ting -> "Tests" workflow'ini tanlang ->
# har bir push/PR uchun alohida "run" ro'yxatga olinadi. Har bir run ichida
# backend va frontend job'lari alohida ustunlarda, parallel progress bilan
# ko'rinadi. Muvaffaqiyatsiz step qizil X bilan, muvaffaqiyatli esa yashil
# tik bilan belgilanadi — 11-darsda buni disk qilishni chuqur o'rganamiz.

# ============================================================
# 5) Minimal, o'zingiz sinab ko'rish uchun workflow
# ============================================================
# .github/workflows/hello.yml sifatida saqlab, push qiling:
name: Hello CI

on: [push]

jobs:
  say-hello:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Salom, $GITHUB_ACTOR! Bu commit $GITHUB_SHA."
      - run: ls -la
""".strip()

L0_CODE_RU = """
# ============================================================
# 1) test.yml — реальный файл workflow этой платформы
#    (.github/workflows/test.yml, полностью)
# ============================================================
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    name: Backend (pytest)
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci --no-audit --no-fund

      - name: Run tests
        working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests

# ============================================================
# 2) Построчный разбор анатомии
# ============================================================
# name: Tests                    <- уровень workflow: это имя видно в
#                                    разделе "Actions" GitHub UI
#
# on: push / pull_request        <- уровень workflow: когда запускается
#                                    (подробно в следующем уроке)
#
# jobs:                          <- два независимых job'а: backend, frontend
#   backend:                     <- уровень job
#     runs-on: ubuntu-latest     <- на какой виртуальной машине
#     timeout-minutes: 10        <- если job идёт дольше 10 минут, он
#                                    принудительно останавливается (чтобы
#                                    не ждать вечно зависший тест)
#     steps:                     <- уровень step, выполняются ПОСЛЕДОВАТЕЛЬНО
#       - uses: actions/checkout@v4          <- 1-й step: готовый action
#       - name: Set up Python                <- "name" необязателен — для
#         uses: actions/setup-python@v5           красивого отображения в UI
#       - name: Install dependencies          <- 3-й step: через run
#         run: pip install -r requirements.txt

# ============================================================
# 3) working-directory — зачем префикс backend/frontend
# ============================================================
# actions/checkout@v4 клонирует на runner ВЕСЬ репозиторий (и backend/, и
# frontend/). Но step "Install dependencies" job'а backend должен работать
# только с backend/requirements.txt — поэтому в каждой строке run: отдельно
# прописан "working-directory: backend". Без этого `pip install -r
# requirements.txt` будет искать requirements.txt в корневой папке и, не
# найдя, выдаст ошибку.

$ ls .github/workflows/
deploy-backend.yml  deploy-frontend.yml  test.yml

# ============================================================
# 4) Наблюдение за workflow из GitHub UI
# ============================================================
# Перейдите на вкладку "Actions" репозитория -> выберите workflow "Tests" ->
# для каждого push/PR регистрируется отдельный "run". Внутри каждого run
# job'ы backend и frontend показываются в отдельных колонках с параллельным
# прогрессом. Неудачный step отмечен красным крестиком, успешный — зелёной
# галочкой — в уроке 11 подробно изучим отладку этого.

# ============================================================
# 5) Минимальный workflow для собственной проверки
# ============================================================
# Сохраните как .github/workflows/hello.yml и запушьте:
name: Hello CI

on: [push]

jobs:
  say-hello:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Привет, $GITHUB_ACTOR! Это коммит $GITHUB_SHA."
      - run: ls -la
""".strip()

L0_TASK = {
    "task_title": "test.yml'ni qo'lda takrorlang va kengaytiring",
    "task_title_ru": "Воспроизведите и расширьте test.yml вручную",
    "task_description": (
        "Ushbu repozitoriyaning `.github/workflows/test.yml` faylini "
        "o'qing. So'ngra o'zingizning shaxsiy (yoki fork qilingan) "
        "repozitoriyangizda shunga o'xshash, lekin uchinchi job qo'shilgan "
        "workflow yozing: `lint` nomli job, `runs-on: ubuntu-latest`, ikkita "
        "step bilan — `actions/checkout@v4` va keyin `backend/` papkasida "
        "`python -m py_compile app/main.py` buyrug'ini bajaruvchi `run` "
        "step'i (working-directory bilan)."
    ),
    "task_description_ru": (
        "Прочитайте файл `.github/workflows/test.yml` этого репозитория. "
        "Затем в своём собственном (или форкнутом) репозитории напишите "
        "похожий workflow, но с добавленным третьим job'ом: job с именем "
        "`lint`, `runs-on: ubuntu-latest`, с двумя step'ами — "
        "`actions/checkout@v4` и затем `run`-step, выполняющий "
        "`python -m py_compile app/main.py` в папке `backend/` (с "
        "working-directory)."
    ),
    "task_requirements": (
        "1) YAML fayl to'g'ri sintaksisga ega bo'lishi va GitHub Actions "
        "tomonidan qabul qilinishi kerak (push qilib, Actions tabida "
        "ko'ring). 2) `lint` job'i alohida, mustaqil job sifatida "
        "ko'rinishi kerak (backend/frontend job'lariga bog'liq emas). "
        "3) `working-directory` to'g'ri ko'rsatilgan bo'lishi shart."
    ),
    "task_requirements_ru": (
        "1) YAML-файл должен иметь корректный синтаксис и приниматься "
        "GitHub Actions (запушьте и проверьте во вкладке Actions). 2) Job "
        "`lint` должен отображаться как отдельный, независимый job (не "
        "зависящий от job'ов backend/frontend). 3) `working-directory` "
        "должен быть указан правильно."
    ),
    "task_technologies": "GitHub Actions, YAML",
    "task_deadline_days": 3,
}

L0_SAMPLE = {
    "title": "Namuna: uch job'li kengaytirilgan test workflow",
    "description": (
        "test.yml asosidagi, lekin uchinchi 'lint' job'i qo'shilgan "
        "namuna workflow fayli — har bir qismi izohlangan."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/test-extended.yml",
            "language": "yaml",
            "code": (
                "name: Tests Extended\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [\"**\"]\n"
                "  pull_request:\n"
                "    branches: [master]\n\n"
                "jobs:\n"
                "  backend:\n"
                "    name: Backend (pytest)\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: \"3.11\"\n"
                "          cache: pip\n"
                "          cache-dependency-path: backend/requirements.txt\n"
                "      - working-directory: backend\n"
                "        run: pip install -r requirements.txt\n"
                "      - working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --tb=short\n\n"
                "  frontend:\n"
                "    name: Frontend (Jest)\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-node@v4\n"
                "        with:\n"
                "          node-version: \"20\"\n"
                "          cache: npm\n"
                "          cache-dependency-path: frontend/package-lock.json\n"
                "      - working-directory: frontend\n"
                "        run: npm ci --no-audit --no-fund\n"
                "      - working-directory: frontend\n"
                "        env:\n"
                "          CI: \"true\"\n"
                "        run: npx react-scripts test --watchAll=false --passWithNoTests\n\n"
                "  # Yangi, mustaqil uchinchi job — backend/frontend'ga bog'liq\n"
                "  # EMAS, shuning uchun ular bilan parallel ishga tushadi.\n"
                "  lint:\n"
                "    name: Backend syntax check\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 5\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: \"3.11\"\n"
                "      - name: Compile-check main.py\n"
                "        working-directory: backend\n"
                "        run: python -m py_compile app/main.py\n"
            ),
        },
    ],
}

L0_EXERCISES = [
    {
        "title": "Workflow fayli qayerda saqlanadi?",
        "title_ru": "Где хранится файл workflow?",
        "description": "GitHub Actions workflow fayllari qaysi papkada bo'lishi kerak?",
        "description_ru": "В какой папке должны находиться файлы workflow GitHub Actions?",
        "exercise_type": "multiple_choice",
        "options": [".github/workflows/", ".github/actions/", "ci/", ".actions/"],
        "options_ru": [".github/workflows/", ".github/actions/", "ci/", ".actions/"],
        "correct_answers": "A",
        "hint": "test.yml, deploy-backend.yml va deploy-frontend.yml qaysi papkada joylashgan edi?",
        "hint_ru": "В какой папке находились test.yml, deploy-backend.yml и deploy-frontend.yml?",
        "explanation": "GitHub faqat .github/workflows/ ichidagi .yml/.yaml fayllarni avtomatik skanerlaydi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "uses vs run",
        "title_ru": "uses против run",
        "description": "Bitta step ichida `uses:` va `run:` kalitlari qanday ishlatiladi?",
        "description_ru": "Как используются ключи `uses:` и `run:` внутри одного step?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir step faqat bittasini ishlatadi, ikkalasi birga bo'lmaydi",
            "Har doim ikkalasi birga yozilishi shart",
            "uses faqat job darajasida, run faqat step darajasida ishlaydi",
            "Ular sinonim, farqi yo'q",
        ],
        "options_ru": [
            "Каждый step использует только одно из двух, оба вместе не бывают",
            "Оба всегда должны быть написаны вместе",
            "uses работает только на уровне job, run — только на уровне step",
            "Это синонимы, разницы нет",
        ],
        "correct_answers": "A",
        "hint": "test.yml'dagi har bir step'ni diqqat bilan qarang — ikkalasi birga ko'ringanmi?",
        "hint_ru": "Внимательно посмотрите на каждый step в test.yml — встречались ли оба ключа вместе?",
        "explanation": "uses tayyor action'ni, run esa shell buyrug'ini chaqiradi — bitta stepda faqat biri bo'ladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Job'lar orasidagi ijro tartibi",
        "title_ru": "Порядок выполнения между job'ами",
        "description": "test.yml'da backend va frontend job'lari, agar `needs:` ko'rsatilmagan bo'lsa, qanday ishga tushadi?",
        "description_ru": "Как запускаются job'ы backend и frontend в test.yml, если `needs:` не указан?",
        "exercise_type": "multiple_choice",
        "options": ["Parallel, bir-birini kutmasdan", "Ketma-ket, alfavit tartibida", "Ketma-ket, yozilish tartibida", "Tasodifiy tartibda"],
        "options_ru": ["Параллельно, не дожидаясь друг друга", "Последовательно, в алфавитном порядке", "Последовательно, в порядке написания", "В случайном порядке"],
        "correct_answers": "A",
        "hint": "needs: kaliti bo'lmasa, job'lar orasida qanday bog'liqlik bor?",
        "hint_ru": "Какая зависимость есть между job'ами, если нет ключа needs:?",
        "explanation": "needs: ko'rsatilmasa, barcha job'lar mustaqil va parallel ishga tushadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Workflow anatomiyasi atamasi",
        "title_ru": "Термин анатомии workflow",
        "description": "Job ichida step'larni belgilaydigan kalit so'z: ___",
        "description_ru": "Ключевое слово, определяющее step'ы внутри job: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "steps",
        "hint": "YAML faylida jobs: dan keyin, har bir job ichida qaysi kalit bor?",
        "hint_ru": "Какой ключ есть внутри каждого job в YAML-файле, после jobs:?",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 1 — Trigger'lar va event'lar: push, pull_request, schedule, workflow_dispatch
# ---------------------------------------------------------------------------

L1_TEXT = """
<h3>on: — workflow'ni nima ishga tushiradi</h3>
<p>0-darsda <code>on:</code> kalitini ko'rdik, lekin uni yuzaki qoldirdik.
Bu — workflow'ning eng muhim qismlaridan biri: qaysi Git voqeasi (event)
sodir bo'lganda avtomatik ishga tushishini belgilaydi. Ushbu platformaning
uchta workflow fayli uchta har xil trigger strategiyasini ko'rsatadi —
ularni solishtirish orqali eng ko'p ishlatiladigan naqshlarni o'rganamiz.</p>

<h3>push — eng oddiy trigger</h3>
<p><code>test.yml</code>da: <code>push: branches: ["**"]</code> — BARCHA
branch'larga push qilinganda ishga tushadi (<code>**</code> — har qanday
branch nomiga mos keluvchi glob naqsh). Bu qasddan shunday: har bir
dasturchi o'z feature branch'iga push qilganida ham darhol test natijasini
ko'rsin, master'ga PR ochishdan oldin muammoni aniqlasin.</p>

<h3>pull_request — faqat maqsad branch muhim</h3>
<p>Xuddi shu faylda: <code>pull_request: branches: [master]</code> — bu
faqat maqsad (target) branch <code>master</code> bo'lgan PR'lar uchun
ishga tushadi, manba branch qaysi bo'lishidan qat'iy nazar. Diqqat: bitta
push bir vaqtning o'zida HAM <code>push</code>, HAM <code>pull_request</code>
event'ini keltirib chiqarishi mumkin (agar branch'ga push qilingan bo'lsa va
o'sha branch'dan PR ochilgan bo'lsa) — shuning uchun ba'zan bitta o'zgarish
uchun ikkita alohida workflow run ko'rasiz, bu xato emas, ikki xil event.</p>

<h3>paths — faqat tegishli fayllar o'zgarganda</h3>
<p><code>deploy-backend.yml</code>da: <code>paths: ['backend/**',
'.github/workflows/deploy-backend.yml']</code> — workflow FAQAT shu
yo'llardagi fayllar o'zgarganda ishga tushadi. Bu muhim optimallashtirish:
agar faqat <code>frontend/</code> ichida o'zgarish bo'lsa, backend'ni qayta
deploy qilishning hojati yo'q — <code>paths</code> filtri buni oldini
oladi, runner vaqtini va CI/CD daqiqalarini tejaydi.</p>

<h3>workflow_dispatch — qo'lda ishga tushirish</h3>
<p>Ikkala deploy faylida ham: <code>workflow_dispatch:</code> — bu GitHub
UI'dagi Actions tabida "Run workflow" tugmasini yoqadi. Bu foydali: kod
o'zgarishi bo'lmasa ham (masalan, kalitni almashtirgandan keyin) qayta
deploy qilish, yoki xatolikni tuzatib push qilmasdan qayta urinish uchun.
<code>schedule:</code> (cron sintaksisi bilan, masalan
<code>cron: '0 3 * * *'</code> — har kuni soat 3:00da) ushbu repoda
ishlatilmagan, lekin muntazam vazifalar — masalan, har haftalik hisobot
yoki eskirgan ma'lumotlarni tozalash — uchun keng tarqalgan.</p>

<h3>concurrency — bir vaqtda ikkita run to'qnashmasligi</h3>
<p>Ikkala deploy faylida: <code>concurrency: {group: deploy-backend,
cancel-in-progress: false}</code>. Bu deploy'larni SERIYALASHTIRADI: agar
ikkita push tez ketma-ket kelsa, ikkinchi run birinchisi tugaguncha
KUTADI (o'chirilmaydi, chunki <code>cancel-in-progress: false</code>).
Buning sababi kommentariyada aniq yozilgan: ikkita deploy runi bir vaqtda
bitta prod serverga rsync/systemctl restart qilsa, poyga holati (race
condition) yuzaga kelishi mumkin.</p>

<h3>Uchta workflow'ning trigger strategiyasi taqqoslash</h3>
<pre class="mermaid">
flowchart LR
  E1["push: har qanday branch"] --> W1["test.yml
backend + frontend testlari"]
  E2["pull_request: -> master"] --> W1
  E3["push: faqat backend/**"] --> W2["deploy-backend.yml
SSH + systemctl restart"]
  E4["workflow_dispatch"] --> W2
  E5["push: faqat frontend/**"] --> W3["deploy-frontend.yml
build + rsync"]
  E6["workflow_dispatch"] --> W3
  style W1 fill:#d6e9ff,stroke:#2266aa
  style W2 fill:#ffe9b3,stroke:#d09000
  style W3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Diagramma shuni ko'rsatadi: <code>test.yml</code> KENG (har qanday
branch va PR uchun) ishga tushadi, chunki maqsad — imkon qadar tezroq
xatoni ushlash. Ikkala deploy fayli esa TOR (faqat tegishli papka
o'zgarganda, faqat <code>server</code> branch'ida) ishga tushadi, chunki
maqsad — faqat kerak bo'lganda haqiqiy prod serverni qayta ishga
tushirish, ortiqcha deploy qilmaslik.</p>

<h3>github.event_name — workflow ichida qaysi trigger ekanini bilish</h3>
<p>Bitta workflow bir nechta event turiga javob bersa (masalan, ham
<code>push</code>, ham <code>pull_request</code>), uning ICHIDA
<code>${{ github.event_name }}</code> orqali aynan qaysi event sabab
bo'lganini bilib olish mumkin. Bu foydali: masalan, faqat
<code>pull_request</code> bo'lganda qo'shimcha statik tahlil qo'shish,
lekin oddiy <code>push</code>da uni o'tkazib yuborish mumkin — hozircha
ushbu platformaning workflow'lari bunday shartli mantiqni ishlatmaydi,
lekin buni bilish keyingi darslarda (matrix, reusable workflow) muhim
bo'ladi, chunki ko'p real loyihalarda job'lar event turiga qarab
shartli ishga tushadi (<code>if: github.event_name == 'pull_request'</code>).</p>
""".strip()

L1_TEXT_RU = """
<h3>on: — что запускает workflow</h3>
<p>В уроке 0 мы видели ключ <code>on:</code>, но поверхностно. Это — одна
из важнейших частей workflow: определяет, какое Git-событие (event)
запускает автоматический запуск. Три файла workflow этой платформы
показывают три разные стратегии триггеров — сравнивая их, изучим самые
распространённые паттерны.</p>

<h3>push — самый простой триггер</h3>
<p>В <code>test.yml</code>: <code>push: branches: ["**"]</code> —
запускается при push в ЛЮБУЮ ветку (<code>**</code> — glob-паттерн,
соответствующий любому имени ветки). Это сделано намеренно: каждый
разработчик должен сразу видеть результат тестов при push в свою feature
ветку, обнаруживая проблему ещё до открытия PR в master.</p>

<h3>pull_request — важна только целевая ветка</h3>
<p>В том же файле: <code>pull_request: branches: [master]</code> — это
запускается только для PR, чья целевая (target) ветка —
<code>master</code>, независимо от того, какая ветка-источник. Обратите
внимание: один push может вызвать ОДНОВРЕМЕННО и событие
<code>push</code>, и <code>pull_request</code> (если push сделан в ветку,
из которой уже открыт PR) — поэтому иногда вы видите два отдельных run
workflow для одного изменения, это не ошибка, а два разных события.</p>

<h3>paths — только когда меняются нужные файлы</h3>
<p>В <code>deploy-backend.yml</code>: <code>paths: ['backend/**',
'.github/workflows/deploy-backend.yml']</code> — workflow запускается
ТОЛЬКО когда меняются файлы по этим путям. Это важная оптимизация: если
изменения только в <code>frontend/</code>, нет смысла заново
разворачивать backend — фильтр <code>paths</code> предотвращает это,
экономя время runner'а и минуты CI/CD.</p>

<h3>workflow_dispatch — запуск вручную</h3>
<p>В обоих файлах деплоя: <code>workflow_dispatch:</code> — это включает
кнопку "Run workflow" во вкладке Actions GitHub UI. Это полезно: даже без
изменения кода (например, после смены ключа) можно повторно развернуть,
или повторить попытку после исправления ошибки, не делая push.
<code>schedule:</code> (с cron-синтаксисом, например <code>cron: '0 3 * *
*'</code> — каждый день в 3:00) в этом репозитории не используется, но
широко распространён для регулярных задач — например, еженедельного
отчёта или очистки устаревших данных.</p>

<h3>concurrency — чтобы два run не сталкивались</h3>
<p>В обоих файлах деплоя: <code>concurrency: {group: deploy-backend,
cancel-in-progress: false}</code>. Это СЕРИАЛИЗУЕТ деплои: если два push
приходят подряд быстро, второй run ЖДЁТ завершения первого (не
отменяется, т.к. <code>cancel-in-progress: false</code>). Причина чётко
написана в комментарии: если два run деплоя одновременно делают
rsync/systemctl restart на один prod-сервер, может возникнуть состояние
гонки (race condition).</p>

<h3>Сравнение стратегий триггеров трёх workflow</h3>
<pre class="mermaid">
flowchart LR
  E1["push: любая ветка"] --> W1["test.yml
тесты backend + frontend"]
  E2["pull_request: -> master"] --> W1
  E3["push: только backend/**"] --> W2["deploy-backend.yml
SSH + systemctl restart"]
  E4["workflow_dispatch"] --> W2
  E5["push: только frontend/**"] --> W3["deploy-frontend.yml
build + rsync"]
  E6["workflow_dispatch"] --> W3
  style W1 fill:#d6e9ff,stroke:#2266aa
  style W2 fill:#ffe9b3,stroke:#d09000
  style W3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Диаграмма показывает: <code>test.yml</code> запускается ШИРОКО (для
любой ветки и PR), потому что цель — поймать ошибку как можно быстрее.
Оба файла деплоя запускаются УЗКО (только когда меняется нужная папка,
только в ветке <code>server</code>), потому что цель — перезапускать
реальный prod-сервер только когда это действительно нужно, не делая
лишних деплоев.</p>

<h3>github.event_name — как узнать триггер внутри workflow</h3>
<p>Если один workflow реагирует на несколько типов событий (например, и
<code>push</code>, и <code>pull_request</code>), внутри него можно узнать,
какое именно событие стало причиной, через <code>${{ github.event_name
}}</code>. Это полезно: например, добавлять дополнительный статический
анализ только для <code>pull_request</code>, но пропускать его при
обычном <code>push</code> — пока workflow этой платформы не используют
такую условную логику, но это важно знать для следующих уроков (matrix,
reusable workflow), поскольку во многих реальных проектах job'ы условно
запускаются в зависимости от типа события
(<code>if: github.event_name == 'pull_request'</code>).</p>
""".strip()

L1_CODE = """
# ============================================================
# 1) test.yml trigger qismi — keng, HAR QANDAY branch
# ============================================================
on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]
# "**" glob naqshi — feature/xyz, bugfix/abc, hattoki ismsiz branch'lar
# ham mos keladi. pull_request faqat master'ga yo'naltirilgan PR'lar uchun.

# ============================================================
# 2) deploy-backend.yml trigger qismi — tor, faqat backend/** + server branch
# ============================================================
on:
  push:
    branches: [server]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-backend
  cancel-in-progress: false

# ============================================================
# 3) deploy-frontend.yml trigger qismi — o'ziga xos izoh bilan
# ============================================================
on:
  push:
    branches: [server]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:
    # Lets you click "Run workflow" in the Actions tab — handy for forcing
    # a rebuild without pushing a code change (e.g. after rotating a key).

concurrency:
  group: deploy-frontend
  cancel-in-progress: false

# ============================================================
# 4) Amaliy stsenariy: nechta workflow ishga tushadi?
# ============================================================
# Stsenariy A: `feature/login` branch'iga faqat frontend/src/App.js
# o'zgartirilib push qilinsa:
#   - test.yml    -> ISHGA TUSHADI (push: branches ["**"])
#   - deploy-backend.yml -> ISHGA TUSHMAYDI (branch server emas)
#   - deploy-frontend.yml -> ISHGA TUSHMAYDI (branch server emas)
#
# Stsenariy B: `server` branch'iga faqat backend/app/main.py o'zgartirilib
# push qilinsa:
#   - test.yml    -> ISHGA TUSHADI (har qanday branch)
#   - deploy-backend.yml -> ISHGA TUSHADI (branch=server, paths=backend/**)
#   - deploy-frontend.yml -> ISHGA TUSHMAYDI (paths mos kelmadi)
#
# Stsenariy C: `server` branch'iga backend/ VA frontend/ ikkalasi ham
# bitta commit'da o'zgartirilib push qilinsa:
#   - test.yml    -> ISHGA TUSHADI
#   - deploy-backend.yml  -> ISHGA TUSHADI
#   - deploy-frontend.yml -> ISHGA TUSHADI (ikkalasi HAM parallel, lekin
#     ularning ICHIDAGI concurrency group'lari alohida — bir-birini
#     to'sib qo'ymaydi, faqat OʻZ turidagi ikkinchi runni to'sadi)

# ============================================================
# 5) workflow_dispatch'ga kirish parametri qo'shish (kengaytma)
# ============================================================
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Qaysi muhitga deploy qilish'
        required: true
        default: 'production'
        type: choice
        options: [production, staging]
# Ishga tushirilganda GitHub UI kirish maydonini so'raydi;
# ${{ github.event.inputs.environment }} orqali workflow ichida o'qiladi.

# ============================================================
# 6) schedule bilan kunlik vazifa (hozircha bu repoda ishlatilmagan)
# ============================================================
on:
  schedule:
    - cron: '0 3 * * *'   # har kuni soat 03:00 UTC da
# Cron formati: daqiqa soat kun-oy oy hafta-kuni.
# GitHub'ning o'z jadvali biroz kechikishi mumkin (yuklama past bo'lganda
# yaqinroq, yuqori bo'lganda 10-15 daqiqagacha kechikishi mumkin) —
# aniq vaqtga tayanadigan muhim vazifalar uchun bu cheklovni bilib qo'ying.
""".strip()

L1_CODE_RU = """
# ============================================================
# 1) Секция триггера test.yml — широкая, ЛЮБАЯ ветка
# ============================================================
on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]
# Glob-паттерн "**" — feature/xyz, bugfix/abc, даже безымянные ветки тоже
# подходят. pull_request — только для PR, направленных в master.

# ============================================================
# 2) Секция триггера deploy-backend.yml — узкая, только backend/** + ветка server
# ============================================================
on:
  push:
    branches: [server]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-backend
  cancel-in-progress: false

# ============================================================
# 3) Секция триггера deploy-frontend.yml — с характерным комментарием
# ============================================================
on:
  push:
    branches: [server]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:
    # Позволяет нажать "Run workflow" во вкладке Actions — удобно, чтобы
    # принудительно пересобрать без изменения кода (например, после смены ключа).

concurrency:
  group: deploy-frontend
  cancel-in-progress: false

# ============================================================
# 4) Практический сценарий: сколько workflow запустится?
# ============================================================
# Сценарий A: в ветку `feature/login` пушится только изменение
# frontend/src/App.js:
#   - test.yml    -> ЗАПУСКАЕТСЯ (push: branches ["**"])
#   - deploy-backend.yml -> НЕ ЗАПУСКАЕТСЯ (ветка не server)
#   - deploy-frontend.yml -> НЕ ЗАПУСКАЕТСЯ (ветка не server)
#
# Сценарий B: в ветку `server` пушится только изменение
# backend/app/main.py:
#   - test.yml    -> ЗАПУСКАЕТСЯ (любая ветка)
#   - deploy-backend.yml -> ЗАПУСКАЕТСЯ (branch=server, paths=backend/**)
#   - deploy-frontend.yml -> НЕ ЗАПУСКАЕТСЯ (paths не совпали)
#
# Сценарий C: в ветку `server` в одном коммите пушатся изменения И
# backend/, И frontend/:
#   - test.yml    -> ЗАПУСКАЕТСЯ
#   - deploy-backend.yml  -> ЗАПУСКАЕТСЯ
#   - deploy-frontend.yml -> ЗАПУСКАЕТСЯ (оба ПАРАЛЛЕЛЬНО, но их
#     concurrency-группы разные — не блокируют друг друга, каждая
#     блокирует только ВТОРОЙ run СВОЕГО же типа)

# ============================================================
# 5) Добавление входного параметра к workflow_dispatch (расширение)
# ============================================================
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'В какое окружение развернуть'
        required: true
        default: 'production'
        type: choice
        options: [production, staging]
# При запуске GitHub UI запросит поле ввода;
# читается внутри workflow через ${{ github.event.inputs.environment }}.

# ============================================================
# 6) Ежедневная задача через schedule (пока не используется в этом репо)
# ============================================================
on:
  schedule:
    - cron: '0 3 * * *'   # каждый день в 03:00 UTC
# Формат cron: минута час день-месяца месяц день-недели.
# Собственное расписание GitHub может немного запаздывать (ближе к
# точному времени при низкой нагрузке, до 10-15 минут при высокой) —
# учитывайте это ограничение для задач, критичных к точному времени.
""".strip()

L1_TASK = {
    "task_title": "Uchta workflow'ning trigger jadvalini tuzing",
    "task_title_ru": "Составьте таблицу триггеров трёх workflow",
    "task_description": (
        "Ushbu repozitoriyaning uchta workflow faylini (`test.yml`, "
        "`deploy-backend.yml`, `deploy-frontend.yml`) qayta o'qing. Har "
        "biri uchun jadval tuzing: qaysi event(lar) (`push`/`pull_request`/"
        "`workflow_dispatch`/`schedule`), qaysi branch(lar), qaysi "
        "`paths` filtri (agar bo'lsa), va concurrency group nomi. So'ngra "
        "3 ta aniq stsenariy yozing (masalan, 'faqat docs/ o'zgardi', "
        "'faqat backend/ o'zgardi server branch'ida') va har biri uchun "
        "qaysi workflow(lar) ishga tushishini bashorat qiling."
    ),
    "task_description_ru": (
        "Перечитайте три файла workflow этого репозитория (`test.yml`, "
        "`deploy-backend.yml`, `deploy-frontend.yml`). Составьте таблицу "
        "для каждого: какое событие/события (`push`/`pull_request`/"
        "`workflow_dispatch`/`schedule`), какие ветки, какой фильтр "
        "`paths` (если есть), и имя группы concurrency. Затем напишите 3 "
        "конкретных сценария (например, 'изменился только docs/', "
        "'изменился только backend/ в ветке server') и предскажите для "
        "каждого, какие workflow запустятся."
    ),
    "task_requirements": (
        "1) Jadval barcha uchta faylni to'liq qamrab olishi kerak. 2) Har "
        "bir stsenariy uchun bashorat REAL push qilib tekshirilgan "
        "(yoki kamida GitHub Actions hujjatlariga asoslanib to'g'ri "
        "asoslangan) bo'lishi kerak. 3) Concurrency group'larining nima "
        "uchun kerakligi tushuntirilgan bo'lishi shart."
    ),
    "task_requirements_ru": (
        "1) Таблица должна полностью охватывать все три файла. 2) "
        "Предсказание для каждого сценария должно быть проверено "
        "реальным push (или как минимум корректно обосновано на "
        "документации GitHub Actions). 3) Должно быть объяснено, зачем "
        "нужны группы concurrency."
    ),
    "task_technologies": "GitHub Actions, YAML, Git branches",
    "task_deadline_days": 3,
}

L1_SAMPLE = {
    "title": "Namuna: workflow_dispatch kirish parametri bilan qo'lda deploy",
    "description": (
        "deploy-backend.yml asosida, workflow_dispatch'ga muhit tanlash "
        "kirish parametri qo'shilgan va shu parametrga qarab turlicha "
        "xabar chiqaruvchi kengaytirilgan namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/manual-deploy-demo.yml",
            "language": "yaml",
            "code": (
                "name: Manual Deploy Demo\n\n"
                "on:\n"
                "  workflow_dispatch:\n"
                "    inputs:\n"
                "      environment:\n"
                "        description: \"Qaysi muhitga deploy qilish\"\n"
                "        required: true\n"
                "        default: \"production\"\n"
                "        type: choice\n"
                "        options: [production, staging]\n\n"
                "concurrency:\n"
                "  group: manual-deploy-demo\n"
                "  cancel-in-progress: false\n\n"
                "jobs:\n"
                "  announce:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 5\n"
                "    steps:\n"
                "      - name: Show chosen environment\n"
                "        run: |\n"
                "          echo \"Tanlangan muhit: ${{ github.event.inputs.environment }}\"\n"
                "          if [ \"${{ github.event.inputs.environment }}\" = \"production\" ]; then\n"
                "            echo \"::warning::Bu PROD muhitga qo'lda deploy - ehtiyot bo'ling!\"\n"
                "          else\n"
                "            echo \"Staging muhitga xavfsiz deploy qilinmoqda.\"\n"
                "          fi\n"
            ),
        },
    ],
}

L1_EXERCISES = [
    {
        "title": "Bir necha branch uchun trigger",
        "title_ru": "Триггер для нескольких веток",
        "description": "test.yml'da push trigger'i qaysi branch'lar uchun ishga tushadi?",
        "description_ru": "Для каких веток срабатывает триггер push в test.yml?",
        "exercise_type": "multiple_choice",
        "options": ["Faqat master", "Faqat server", "Har qanday branch (\"**\")", "Hech qaysi, faqat PR uchun"],
        "options_ru": ["Только master", "Только server", "Любая ветка (\"**\")", "Ни одна, только для PR"],
        "correct_answers": "C",
        "hint": "test.yml'dagi on.push.branches qiymatini eslang.",
        "hint_ru": "Вспомните значение on.push.branches в test.yml.",
        "explanation": "branches: [\"**\"] glob naqshi barcha branch'larga mos keladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "paths filtri nima uchun kerak",
        "title_ru": "Зачем нужен фильтр paths",
        "description": "deploy-backend.yml'da `paths: ['backend/**', ...]` filtri asosiy maqsadi nima?",
        "description_ru": "Какова основная цель фильтра `paths: ['backend/**', ...]` в deploy-backend.yml?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat backend o'zgarganda ishga tushib, keraksiz deploy'larni oldini olish",
            "Backend kodini xavfsizlik uchun shifrlash",
            "Faqat backend testlarini o'chirish",
            "Runner tanlashni tezlashtirish",
        ],
        "options_ru": [
            "Запускаться только при изменении backend, избегая ненужных деплоев",
            "Шифровать код backend для безопасности",
            "Отключать только тесты backend",
            "Ускорять выбор runner'а",
        ],
        "correct_answers": "A",
        "hint": "Agar faqat frontend/ o'zgargan bo'lsa, backend'ni qayta deploy qilish kerakmi?",
        "hint_ru": "Если изменился только frontend/, нужно ли заново разворачивать backend?",
        "explanation": "paths filtri workflow'ni faqat tegishli fayllar o'zgarganda ishga tushiradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "concurrency vazifasi",
        "title_ru": "Задача concurrency",
        "description": "`cancel-in-progress: false` bo'lgan concurrency group'da ikkinchi run nima qiladi?",
        "description_ru": "Что делает второй run в группе concurrency с `cancel-in-progress: false`?",
        "exercise_type": "multiple_choice",
        "options": ["Birinchisi tugaguncha kutadi", "Darhol bekor qilinadi", "Birinchisini bekor qiladi", "Parallel ishga tushadi"],
        "options_ru": ["Ждёт завершения первого", "Немедленно отменяется", "Отменяет первый", "Запускается параллельно"],
        "correct_answers": "A",
        "hint": "cancel-in-progress false bo'lsa, hech narsa bekor qilinmaydi — unda navbat qanday ishlaydi?",
        "hint_ru": "Если cancel-in-progress false, ничего не отменяется — как тогда работает очередь?",
        "explanation": "false qiymati bilan ikkinchi run navbatga turadi va birinchisi tugagach boshlanadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Qo'lda ishga tushirish trigger'i",
        "title_ru": "Триггер ручного запуска",
        "description": "GitHub UI'da \"Run workflow\" tugmasini yoqadigan kalit so'z: ___",
        "description_ru": "Ключевое слово, включающее кнопку \"Run workflow\" в GitHub UI: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "workflow_dispatch",
        "hint": "Ikkala deploy faylida ham on: ostida bor edi.",
        "hint_ru": "В обоих deploy-файлах это было под on:.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 2 — Secrets va environment o'zgaruvchilari
# ---------------------------------------------------------------------------

L2_TEXT = """
<h3>Nega maxfiy ma'lumotni YAML fayliga yozib bo'lmaydi</h3>
<p><code>deploy-backend.yml</code> ssh orqali prod serverga ulanadi — buning
uchun xususiy kalit (private key), server manzili, foydalanuvchi nomi
kerak. Bularni to'g'ridan-to'g'ri YAML faylga yozish OGʻIR xavfsizlik
xatosi bo'lardi: repozitoriy ochiq (yoki hatto yopiq bo'lsa ham, kimdir
kirish huquqiga ega bo'lsa) — kalit darhol oshkor bo'ladi. GitHub Actions
buning uchun <strong>repository secrets</strong> mexanizmini taqdim etadi:
Settings → Secrets and variables → Actions bo'limida saqlanadigan,
shifrlangan, workflow logida hech qachon ochiq ko'rinmaydigan qiymatlar.</p>

<h3>Ushbu repo qanday secret'lardan foydalanadi</h3>
<p><code>deploy-backend.yml</code>ning boshidagi kommentariyada aniq
ro'yxat bor: <code>SSH_HOST</code>, <code>SSH_USER</code>,
<code>SSH_PRIVATE_KEY</code>, ixtiyoriy <code>SSH_PORT</code>,
<code>BACKEND_DIR</code>, <code>SERVICE_NAME</code>.
<code>deploy-frontend.yml</code>da esa <code>SSH_HOST</code>,
<code>SSH_USER</code>, <code>SSH_PRIVATE_KEY</code>, ixtiyoriy
<code>SSH_PORT</code>. Workflow ichida ular
<code>${{ secrets.SSH_HOST }}</code> sintaksisi orqali o'qiladi — bu
qiymat step ichida <code>env:</code> orqali oddiy environment
o'zgaruvchisiga aylantiriladi, so'ngra shell buyrug'ida
<code>"$SSH_HOST"</code> sifatida ishlatiladi.</p>

<h3>GITHUB_TOKEN — avtomatik, alohida sozlanmaydigan secret</h3>
<p>Har bir workflow run uchun GitHub o'zi avtomatik ravishda
<code>GITHUB_TOKEN</code> nomli vaqtinchalik secret yaratadi — uni qo'lda
qo'shish shart emas, u <code>${{ secrets.GITHUB_TOKEN }}</code> orqali
darhol mavjud. U repo'ning o'zi bilan ishlash uchun (masalan, PR'ga
kommentariya qoldirish, release yaratish, boshqa workflow'ni trigger
qilish) ishlatiladi va run tugagach avtomatik bekor qilinadi (revoke).
Ushbu platformaning workflow'lari uni hozircha ishlatmaydi (chunki ular
faqat SSH orqali tashqi serverga ulanadi, GitHub API bilan ishlamaydi),
lekin har qanday workflow'da <em>doim</em> mavjud bo'lgani uchun bilish
muhim.</p>

<h3>Oddiy environment o'zgaruvchilari — secret emas</h3>
<p><code>deploy-frontend.yml</code>ning "Build production bundle" step'ida:
<code>REACT_APP_API_URL: https://tech.gennis.uz/</code>,
<code>CI: 'false'</code>, <code>NODE_OPTIONS: --max-old-space-size=4096</code>,
<code>GENERATE_SOURCEMAP: 'false'</code>. Bular <strong>secret EMAS</strong>
— ular maxfiy emas, YAML faylida ochiq ko'rinadi, chunki bu qiymatlar
oshkor bo'lsa ham hech qanday xavf yo'q (API manzili, build sozlamalari).
Farqni tushunish muhim: <code>secrets.X</code> — shifrlangan, log'da
avtomatik <code>***</code> bilan almashtiriladi; oddiy <code>env:</code>
qiymati — ochiq matn, log'da to'liq ko'rinadi.</p>

<h3>Environments — qo'shimcha himoya qatlami</h3>
<p>GitHub "Environments" (masalan <code>production</code>,
<code>staging</code>) — har biriga alohida secret to'plami va ixtiyoriy
"required reviewers" qo'yish mumkin: deploy job shu environment'ga
ishora qilsa, u avval belgilangan odam(lar) tasdiqlashini kutadi. Ushbu
repo hozircha alohida environment ishlatmaydi (barcha secret'lar
repo darajasida), lekin katta jamoada bu — ayniqsa production'ga
deploy qilishdan oldin qo'shimcha inson nazorati kerak bo'lganda — juda
foydali naqsh.</p>

<h3>Secret oqimi: qayerdan qayergacha</h3>
<pre class="mermaid">
flowchart LR
  S["GitHub Settings
Secrets and variables"] -->|"${{ secrets.SSH_PRIVATE_KEY }}"| ST["step env:
SSH_PRIVATE_KEY"]
  ST -->|"printf ... > ~/.ssh/deploy_key"| F["vaqtinchalik fayl
runner diskida"]
  F -->|"ssh -i ~/.ssh/deploy_key"| PROD["prod server"]
  ST -.->|"log'da avtomatik ***"| LOG["Actions log"]
  style S fill:#ffe9b3,stroke:#d09000
  style LOG fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Diagramma <code>deploy-backend.yml</code>ning "Configure SSH" step'idan
olingan real oqim: secret GitHub'ning shifrlangan xotirasidan step'ning
environment o'zgaruvchisiga, undan vaqtinchalik faylga yoziladi, va faqat
shu fayl SSH ulanish uchun ishlatiladi. Agar kimdir <code>echo
$SSH_PRIVATE_KEY</code> qilishga urinsa, GitHub buni log'da avtomatik
<code>***</code> bilan almashtiradi — lekin bu HAM qat'iy kafolat emas:
qiymatni boshqa o'zgaruvchiga qo'shib (masalan
<code>base64 encode</code> qilib) chiqarsa, maskировка ishlamaydi, shuning
uchun "Cleanup SSH key" step'i <code>if: always()</code> bilan faylni
darhol o'chiradi.</p>
""".strip()

L2_TEXT_RU = """
<h3>Почему секретные данные нельзя писать в YAML-файл</h3>
<p><code>deploy-backend.yml</code> подключается к prod-серверу по SSH — для
этого нужны приватный ключ, адрес сервера, имя пользователя. Записать их
прямо в YAML-файл было бы СЕРЬЁЗНОЙ ошибкой безопасности: репозиторий
открыт (или даже если закрыт, кто-то имеет доступ) — ключ будет сразу
раскрыт. GitHub Actions предоставляет для этого механизм
<strong>repository secrets</strong>: значения, хранящиеся в разделе
Settings → Secrets and variables → Actions, зашифрованные, никогда не
отображаемые открыто в логе workflow.</p>

<h3>Какие secrets использует этот репозиторий</h3>
<p>В комментарии в начале <code>deploy-backend.yml</code> есть чёткий
список: <code>SSH_HOST</code>, <code>SSH_USER</code>,
<code>SSH_PRIVATE_KEY</code>, опциональный <code>SSH_PORT</code>,
<code>BACKEND_DIR</code>, <code>SERVICE_NAME</code>. В
<code>deploy-frontend.yml</code>: <code>SSH_HOST</code>,
<code>SSH_USER</code>, <code>SSH_PRIVATE_KEY</code>, опциональный
<code>SSH_PORT</code>. Внутри workflow они читаются через синтаксис
<code>${{ secrets.SSH_HOST }}</code> — это значение внутри step
превращается в обычную переменную окружения через <code>env:</code>, а
затем используется в shell-команде как <code>"$SSH_HOST"</code>.</p>

<h3>GITHUB_TOKEN — автоматический, отдельно не настраиваемый secret</h3>
<p>Для каждого run workflow GitHub сам автоматически создаёт временный
secret с именем <code>GITHUB_TOKEN</code> — добавлять его вручную не
нужно, он сразу доступен через <code>${{ secrets.GITHUB_TOKEN }}</code>.
Используется для работы с самим репозиторием (например, оставить
комментарий к PR, создать release, вызвать другой workflow) и
автоматически аннулируется (revoke) после завершения run. Workflow этой
платформы пока не используют его (т.к. они только подключаются по SSH к
внешнему серверу, не работают с GitHub API), но важно знать, что он
<em>всегда</em> присутствует в любом workflow.</p>

<h3>Обычные переменные окружения — не secret</h3>
<p>В step "Build production bundle" файла <code>deploy-frontend.yml</code>:
<code>REACT_APP_API_URL: https://tech.gennis.uz/</code>,
<code>CI: 'false'</code>, <code>NODE_OPTIONS: --max-old-space-size=4096</code>,
<code>GENERATE_SOURCEMAP: 'false'</code>. Это <strong>НЕ secret</strong> —
они не секретны, видны открыто в YAML-файле, потому что даже при их
раскрытии нет никакого риска (адрес API, настройки сборки). Важно понять
разницу: <code>secrets.X</code> — зашифровано, автоматически заменяется
на <code>***</code> в логе; обычное значение <code>env:</code> — открытый
текст, полностью видно в логе.</p>

<h3>Environments — дополнительный слой защиты</h3>
<p>GitHub "Environments" (например <code>production</code>,
<code>staging</code>) — у каждого свой набор secrets и опциональные
"required reviewers": если деплой-job указывает на такое environment, он
ждёт подтверждения от заранее назначенного человека (людей). Этот
репозиторий пока не использует отдельные environments (все secrets на
уровне репо), но в большой команде это — особенно когда перед деплоем в
production нужен дополнительный человеческий контроль — очень полезный
паттерн.</p>

<h3>Поток секрета: откуда куда</h3>
<pre class="mermaid">
flowchart LR
  S["GitHub Settings
Secrets and variables"] -->|"${{ secrets.SSH_PRIVATE_KEY }}"| ST["step env:
SSH_PRIVATE_KEY"]
  ST -->|"printf ... > ~/.ssh/deploy_key"| F["временный файл
на диске runner'а"]
  F -->|"ssh -i ~/.ssh/deploy_key"| PROD["prod-сервер"]
  ST -.->|"в логе автоматически ***"| LOG["лог Actions"]
  style S fill:#ffe9b3,stroke:#d09000
  style LOG fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Диаграмма взята из реального потока step "Configure SSH" файла
<code>deploy-backend.yml</code>: secret из зашифрованного хранилища
GitHub попадает в переменную окружения step'а, оттуда — во временный
файл, и только этот файл используется для SSH-подключения. Если кто-то
попробует сделать <code>echo $SSH_PRIVATE_KEY</code>, GitHub автоматически
заменит это в логе на <code>***</code> — но это ТОЖЕ не строгая гарантия:
если значение вывести через другую переменную (например, закодировав в
<code>base64</code>), маскировка не сработает, поэтому step "Cleanup SSH
key" с <code>if: always()</code> немедленно удаляет файл.</p>
""".strip()

L2_CODE = """
# ============================================================
# 1) deploy-backend.yml — secret'lardan foydalanish (to'liq oqim)
# ============================================================
jobs:
  deploy:
    name: Pull & restart backend
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Pull latest code and restart service
        env:
          SSH_HOST:     ${{ secrets.SSH_HOST }}
          SSH_USER:     ${{ secrets.SSH_USER }}
          SSH_PORT:     ${{ secrets.SSH_PORT }}
          BACKEND_DIR:  ${{ secrets.BACKEND_DIR }}
          SERVICE_NAME: ${{ secrets.SERVICE_NAME }}
        run: |
          PORT="${SSH_PORT:-22}"
          ssh -i ~/.ssh/deploy_key -p "$PORT" -o StrictHostKeyChecking=yes \\
              "$SSH_USER@$SSH_HOST" \\
              "set -e
               git -C \\"$BACKEND_DIR\\" pull origin server
               cd \\"$BACKEND_DIR\\"
               source venv/bin/activate
               pip install -r requirements.txt --quiet
               systemctl restart \\"$SERVICE_NAME\\""

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key
# "if: always()" — bu step HAR DOIM bajariladi, hattoki oldingi step'lar
# muvaffaqiyatsiz bo'lsa ham. Kalit fayli runner o'chganda baribir yo'qoladi
# (runner ephemeral), lekin aniq o'chirish - "belt-and-suspenders" ehtiyot
# chorasi, izohda aytilganidek.

# ============================================================
# 2) deploy-frontend.yml — oddiy (secret bo'lmagan) env o'zgaruvchilari
# ============================================================
- name: Build production bundle
  working-directory: frontend
  env:
    REACT_APP_API_URL: https://tech.gennis.uz/
    # CRA treats warnings as errors when CI=true. Runners set CI=true by
    # default, so we override.
    CI: 'false'
    NODE_OPTIONS: --max-old-space-size=4096
    GENERATE_SOURCEMAP: 'false'
  run: npm run build
# Bu qiymatlar YAML faylida OCHIQ - GitHub log'ida to'liq ko'rinadi,
# hech narsa maskировка qilinmaydi, chunki bular maxfiy emas.

# ============================================================
# 3) Secret qiymatini GitHub CLI orqali qo'shish
# ============================================================
$ gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_deploy
$ gh secret set SSH_HOST --body "5.129.242.151"
$ gh secret list
NAME               UPDATED
BACKEND_DIR        2 days ago
SERVICE_NAME       2 days ago
SSH_HOST           2 days ago
SSH_PRIVATE_KEY    2 days ago
SSH_PORT           2 days ago
SSH_USER           2 days ago
# gh secret list qiymatlarni HECH QACHON ko'rsatmaydi - faqat nom va
# oxirgi yangilanish sanasi, bu qasddan shunday (secret write-only).

# ============================================================
# 4) GITHUB_TOKEN'ning avtomatik namunasi (bu repoda ishlatilmagan,
#    lekin har qanday workflow'da mavjud)
# ============================================================
jobs:
  comment-on-pr:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write   # GITHUB_TOKEN'ning ruxsatlarini cheklash/kengaytirish
    steps:
      - uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'CI testlari muvaffaqiyatli o\\'tdi!'
            })
# permissions: bloki bilan GITHUB_TOKEN'ning nima qila olishini
# minimal qilib cheklash - xavfsizlik amaliyoti (least privilege).

# ============================================================
# 5) Environment (production) bilan required reviewer namunasi
# ============================================================
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production   # <- Settings > Environments'da sozlangan
                               #    "production" muhitiga bog'laydi
    steps:
      - run: echo "Bu step faqat tasdiqlangandan keyin ishga tushadi"
""".strip()

L2_CODE_RU = """
# ============================================================
# 1) deploy-backend.yml — использование secrets (полный поток)
# ============================================================
jobs:
  deploy:
    name: Pull & restart backend
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Pull latest code and restart service
        env:
          SSH_HOST:     ${{ secrets.SSH_HOST }}
          SSH_USER:     ${{ secrets.SSH_USER }}
          SSH_PORT:     ${{ secrets.SSH_PORT }}
          BACKEND_DIR:  ${{ secrets.BACKEND_DIR }}
          SERVICE_NAME: ${{ secrets.SERVICE_NAME }}
        run: |
          PORT="${SSH_PORT:-22}"
          ssh -i ~/.ssh/deploy_key -p "$PORT" -o StrictHostKeyChecking=yes \\
              "$SSH_USER@$SSH_HOST" \\
              "set -e
               git -C \\"$BACKEND_DIR\\" pull origin server
               cd \\"$BACKEND_DIR\\"
               source venv/bin/activate
               pip install -r requirements.txt --quiet
               systemctl restart \\"$SERVICE_NAME\\""

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key
# "if: always()" — этот step выполняется ВСЕГДА, даже если предыдущие
# step'ы завершились неудачно. Файл ключа всё равно исчезнет при
# уничтожении runner'а (runner эфемерный), но явное удаление — мера
# предосторожности "belt-and-suspenders", как сказано в комментарии.

# ============================================================
# 2) deploy-frontend.yml — обычные (не secret) переменные окружения
# ============================================================
- name: Build production bundle
  working-directory: frontend
  env:
    REACT_APP_API_URL: https://tech.gennis.uz/
    # CRA treats warnings as errors when CI=true. Runners set CI=true by
    # default, so we override.
    CI: 'false'
    NODE_OPTIONS: --max-old-space-size=4096
    GENERATE_SOURCEMAP: 'false'
  run: npm run build
# Эти значения ОТКРЫТЫ в YAML-файле — полностью видны в логе GitHub,
# ничего не маскируется, потому что они не секретны.

# ============================================================
# 3) Добавление secret через GitHub CLI
# ============================================================
$ gh secret set SSH_PRIVATE_KEY < ~/.ssh/id_deploy
$ gh secret set SSH_HOST --body "5.129.242.151"
$ gh secret list
NAME               UPDATED
BACKEND_DIR        2 days ago
SERVICE_NAME       2 days ago
SSH_HOST           2 days ago
SSH_PRIVATE_KEY    2 days ago
SSH_PORT           2 days ago
SSH_USER           2 days ago
# gh secret list НИКОГДА не показывает значения — только имя и дату
# последнего обновления, это сделано намеренно (secret write-only).

# ============================================================
# 4) Автоматический пример GITHUB_TOKEN (не используется в этом репо,
#    но присутствует в любом workflow)
# ============================================================
jobs:
  comment-on-pr:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write   # ограничение/расширение прав GITHUB_TOKEN
    steps:
      - uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Тесты CI прошли успешно!'
            })
# Блок permissions: минимизирует, что может делать GITHUB_TOKEN —
# практика безопасности (least privilege).

# ============================================================
# 5) Пример environment (production) с required reviewer
# ============================================================
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production   # <- привязывает к environment "production",
                               #    настроенному в Settings > Environments
    steps:
      - run: echo "Этот step запустится только после подтверждения"
""".strip()

L2_TASK = {
    "task_title": "Xavfsiz deploy workflow: secret vs oddiy env",
    "task_title_ru": "Безопасный deploy workflow: secret против обычного env",
    "task_description": (
        "`deploy-backend.yml` va `deploy-frontend.yml` fayllarini qayta "
        "o'qing va ikkita ustunli jadval tuzing: 'Secret sifatida "
        "saqlanishi kerak' va 'Oddiy env sifatida yetarli' — har bir "
        "ishlatilgan qiymatni (SSH_HOST, REACT_APP_API_URL, "
        "SERVICE_NAME, NODE_OPTIONS va h.k.) to'g'ri ustunga joylashtiring "
        "va HAR BIRI uchun 1 gapda nima uchun shu tanlov to'g'ri ekanini "
        "yozing."
    ),
    "task_description_ru": (
        "Перечитайте файлы `deploy-backend.yml` и `deploy-frontend.yml` и "
        "составьте таблицу из двух колонок: 'Должно храниться как secret' "
        "и 'Достаточно обычного env' — распределите каждое используемое "
        "значение (SSH_HOST, REACT_APP_API_URL, SERVICE_NAME, "
        "NODE_OPTIONS и т.д.) в правильную колонку и для КАЖДОГО напишите "
        "одно предложение, почему выбор верный."
    ),
    "task_requirements": (
        "1) Kamida 8 ta qiymat tahlil qilingan bo'lishi kerak. 2) Har bir "
        "qator uchun asoslash yozilgan bo'lishi shart (nafaqat 'to'g'ri' "
        "deb belgilash). 3) GITHUB_TOKEN'ning nima uchun repo secret'lari "
        "ro'yxatida ko'rinmasligi tushuntirilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Должно быть проанализировано минимум 8 значений. 2) Для "
        "каждой строки должно быть написано обоснование (не просто "
        "пометка 'верно'). 3) Должно быть объяснено, почему GITHUB_TOKEN "
        "не появляется в списке repo secrets."
    ),
    "task_technologies": "GitHub Actions secrets, environment variables",
    "task_deadline_days": 3,
}

L2_SAMPLE = {
    "title": "Namuna: secret bilan xavfsiz curl deploy-hook workflow",
    "description": (
        "Repo secret'idan foydalanib tashqi deploy-hook URL'iga so'rov "
        "yuboruvchi, log'da hech qanday maxfiy qiymat oshkor bo'lmaydigan "
        "namuna workflow."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/notify-deploy-hook.yml",
            "language": "yaml",
            "code": (
                "name: Notify Deploy Hook\n\n"
                "on:\n"
                "  workflow_dispatch:\n\n"
                "jobs:\n"
                "  notify:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 5\n"
                "    steps:\n"
                "      - name: Ping deploy hook (secret URL, secret token)\n"
                "        env:\n"
                "          HOOK_URL: ${{ secrets.DEPLOY_HOOK_URL }}\n"
                "          HOOK_TOKEN: ${{ secrets.DEPLOY_HOOK_TOKEN }}\n"
                "        run: |\n"
                "          set -euo pipefail\n"
                "          if [ -z \"${HOOK_URL:-}\" ]; then\n"
                "            echo \"::error::DEPLOY_HOOK_URL sozlanmagan\"\n"
                "            exit 1\n"
                "          fi\n"
                "          curl -sf -X POST \"$HOOK_URL\" \\\n"
                "            -H \"Authorization: Bearer $HOOK_TOKEN\" \\\n"
                "            -H \"Content-Type: application/json\" \\\n"
                "            -d '{\"status\": \"deployed\", \"ref\": \"'\"$GITHUB_SHA\"'\"}'\n"
                "          echo \"Hook chaqirildi (token log'da hech qachon ko'rinmaydi)\"\n"
            ),
        },
    ],
}

L2_EXERCISES = [
    {
        "title": "Secret qayerda saqlanadi",
        "title_ru": "Где хранится secret",
        "description": "GitHub repository secret'lari qaysi bo'limda sozlanadi?",
        "description_ru": "В каком разделе настраиваются repository secrets GitHub?",
        "exercise_type": "multiple_choice",
        "options": ["Settings -> Secrets and variables -> Actions", ".github/secrets.yml faylida", "README.md ichida", "package.json ichida"],
        "options_ru": ["Settings -> Secrets and variables -> Actions", "В файле .github/secrets.yml", "Внутри README.md", "Внутри package.json"],
        "correct_answers": "A",
        "hint": "Bu YAML fayl ichida emas, GitHub'ning veb interfeysida sozlanadi.",
        "hint_ru": "Это настраивается не внутри YAML-файла, а в веб-интерфейсе GitHub.",
        "explanation": "Secret'lar faqat GitHub UI/API orqali, Settings bo'limida qo'shiladi, hech qachon kodda emas.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "secrets vs oddiy env",
        "title_ru": "secrets против обычного env",
        "description": "deploy-frontend.yml'dagi REACT_APP_API_URL nega secrets.X sifatida emas, oddiy qiymat sifatida yozilgan?",
        "description_ru": "Почему REACT_APP_API_URL в deploy-frontend.yml записан обычным значением, а не через secrets.X?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki u maxfiy emas, oshkor bo'lsa ham xavf yo'q",
            "Chunki secrets faqat SSH uchun ishlatiladi",
            "Chunki u juda uzun matn",
            "Chunki REACT_APP prefiksli o'zgaruvchilar secret bo'la olmaydi",
        ],
        "options_ru": [
            "Потому что оно не секретно, раскрытие не несёт риска",
            "Потому что secrets используются только для SSH",
            "Потому что это слишком длинный текст",
            "Потому что переменные с префиксом REACT_APP не могут быть secret",
        ],
        "correct_answers": "A",
        "hint": "API manzilining o'zi maxfiy ma'lumotmi?",
        "hint_ru": "Является ли сам адрес API секретной информацией?",
        "explanation": "secret faqat haqiqiy maxfiy qiymatlar (kalitlar, parollar, tokenlar) uchun ishlatiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "GITHUB_TOKEN xususiyati",
        "title_ru": "Свойство GITHUB_TOKEN",
        "description": "GITHUB_TOKEN qo'lda repo secret sifatida qo'shilishi kerakmi?",
        "description_ru": "Нужно ли добавлять GITHUB_TOKEN вручную как repo secret?",
        "exercise_type": "multiple_choice",
        "options": ["Yo'q, GitHub uni har bir run uchun avtomatik yaratadi", "Ha, har safar qo'lda yaratish kerak", "Faqat production'da kerak", "Faqat pull_request'da mavjud"],
        "options_ru": ["Нет, GitHub создаёт его автоматически для каждого run", "Да, нужно создавать вручную каждый раз", "Нужен только в production", "Существует только для pull_request"],
        "correct_answers": "A",
        "hint": "Bu maxsus, GitHub'ning o'zi boshqaradigan secret turi.",
        "hint_ru": "Это особый тип secret, которым управляет сам GitHub.",
        "explanation": "GITHUB_TOKEN avtomatik yaratiladi va run tugagach avtomatik bekor qilinadi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Maxfiy qiymatni o'qish sintaksisi",
        "title_ru": "Синтаксис чтения секретного значения",
        "description": "Workflow ichida repo secret'ini o'qish uchun ishlatiladigan sintaksis: ${{ ___.SSH_HOST }}",
        "description_ru": "Синтаксис для чтения repo secret внутри workflow: ${{ ___.SSH_HOST }}",
        "exercise_type": "fill_in_blank",
        "correct_answers": "secrets",
        "hint": "deploy-backend.yml'dagi env: blokini eslang.",
        "hint_ru": "Вспомните блок env: в deploy-backend.yml.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 3 — Matrix build'lar: bir nechta versiyada parallel test
# ---------------------------------------------------------------------------

L3_TEXT = """
<h3>Muammo: bitta versiyada test o'tdi, boshqasida sinmasligiga kafolat yo'q</h3>
<p>Ushbu platformaning <code>test.yml</code>i backend uchun faqat BITTA
Python versiyasida (<code>"3.11"</code>) va frontend uchun faqat BITTA
Node versiyasida (<code>"20"</code>) test qiladi. Bu kichik jamoa uchun
yetarli, chunki prod server ham xuddi shu versiyalarni ishlatadi. Lekin
kutubxona yozayotgan, yoki turli mijozlar turli versiyada ishlatishi
mumkin bo'lgan loyihada — bitta versiyada test o'tishi boshqa versiyada
ham ishlashiga KAFOLAT bermaydi. <strong>Matrix strategy</strong> — bir
xil job'ni bir nechta parametr kombinatsiyasida AVTOMATIK ravishda
parallel ishga tushirish mexanizmi.</p>

<h3>strategy.matrix — asosiy sintaksis</h3>
<p><code>jobs.&lt;job_id&gt;.strategy.matrix</code> ostida ro'yxat(lar)
beriladi — GitHub Actions ularning DEKART ko'paytmasini (barcha
kombinatsiyalarni) hisoblab, har biri uchun alohida job nusxasini yaratadi.
Masalan <code>python-version: ["3.10", "3.11", "3.12"]</code> berilsa, uch
xil versiyada bir xil step'lar uch marta, PARALLEL ishga tushadi — har
biri o'z alohida runner'ida, bir-biridan mustaqil.</p>

<h3>matrix qiymatiga step ichida murojaat qilish</h3>
<p>Matrix o'zgaruvchisi <code>${{ matrix.python-version }}</code> orqali
o'qiladi — bu qiymat har bir parallel nusxada boshqacha bo'ladi. Buni
<code>actions/setup-python@v5</code>ning <code>with: python-version:</code>
parametriga to'g'ridan-to'g'ri berish mumkin, shunda bitta step yozib,
GitHub avtomatik uni har bir versiya uchun takrorlaydi.</p>

<h3>Ikki o'lchamli matrix — versiya x operatsion tizim</h3>
<p>Matrix'ga bir nechta kalit qo'shish mumkin: masalan
<code>python-version: ["3.10", "3.11"]</code> VA <code>os: [ubuntu-latest,
windows-latest]</code> berilsa — 2×2=4 ta kombinatsiya, ya'ni 4 ta
parallel job yaratiladi (Ubuntu+3.10, Ubuntu+3.11, Windows+3.10,
Windows+3.11). Bu kutubxona turli platformalarda ham ishlashini
tekshirish uchun standart naqsh.</p>

<h3>fail-fast va exclude — matrix'ni boshqarish</h3>
<p><code>strategy.fail-fast: false</code> qo'yilsa, bitta kombinatsiya
muvaffaqiyatsiz bo'lganda QOLGAN kombinatsiyalar BEKOR QILINMAYDI — har
biri to'liq natija berguncha davom etadi (standart holatda
<code>fail-fast: true</code>, ya'ni birinchi xato hammasini to'xtatadi).
<code>exclude:</code> orqali muayyan kombinatsiyalarni chiqarib tashlash
mumkin (masalan, eskirgan Python versiyasi Windows'da qo'llab-
quvvatlanmasa). Bular real loyihalarda vaqt va CI daqiqalarini tejash
uchun muhim.</p>

<h3>test.yml'ni matrix bilan kengaytirish diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  M["strategy.matrix
python-version: [3.10, 3.11, 3.12]"] --> J1["backend (3.10)
runs-on: ubuntu-latest"]
  M --> J2["backend (3.11)
runs-on: ubuntu-latest"]
  M --> J3["backend (3.12)
runs-on: ubuntu-latest"]
  J1 --> R1["pytest tests/ - natija"]
  J2 --> R2["pytest tests/ - natija"]
  J3 --> R3["pytest tests/ - natija"]
  style J1 fill:#d6e9ff,stroke:#2266aa
  style J2 fill:#d6e9ff,stroke:#2266aa
  style J3 fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Diagramma shuni ko'rsatadi: bitta <code>backend</code> job ta'rifi
YAML'da FAQAT BIR MARTA yoziladi, lekin matrix orqali 3 xil Python
versiyasida 3 marta, parallel ishga tushadi. Agar barcha 3 kombinatsiya
muvaffaqiyatli o'tsa, kod 3.10, 3.11 va 3.12'da ham ishlashi
KAFOLATLANADI — hozirgi test.yml esa faqat 3.11'da tekshirilganini
bildiradi, boshqa versiyalarda ishlashi haqida hech narsa aytmaydi.</p>

<h3>Matrix narxi: har bir kombinatsiya alohida daqiqa sarflaydi</h3>
<p>Matrix "bepul" emas — har bir kombinatsiya alohida runner, alohida
bog'liqliklarni o'rnatish, demak alohida CI daqiqasini sarflaydi. Xususiy
(private) repozitoriyalarda GitHub Actions daqiqalari cheklangan
kvota bo'yicha hisoblanadi (jamoat/ochiq repozitoriyalar uchun odatda
bepul). Shuning uchun matrix'ni "iloji boricha ko'p versiya" emas,
"real qo'llab-quvvatlanadigan versiyalar" bilan cheklash kerak — masalan,
ushbu platformaning frontend job'i uchun faqat Node 20'ni tekshirish
yetarli, chunki prod server ham aynan shu versiyani ishlatadi; agar
kutubxona sifatida tarqatilsa, Node 18/20/22 uchtasini tekshirish
oqilona bo'lardi. Bir so'z bilan: matrix — kengroq qamrov va CI xarajati
orasidagi ongli murosa, har doim eng katta ro'yxatni yozish emas.</p>
""".strip()

L3_TEXT_RU = """
<h3>Проблема: тест прошёл на одной версии — не гарантия для другой</h3>
<p><code>test.yml</code> этой платформы тестирует backend только на ОДНОЙ
версии Python (<code>"3.11"</code>) и frontend только на ОДНОЙ версии Node
(<code>"20"</code>). Для небольшой команды этого достаточно, ведь
prod-сервер использует те же версии. Но в библиотеке, или в проекте, где
разные клиенты могут использовать разные версии — прохождение теста на
одной версии НЕ ГАРАНТИРУЕТ работу на другой. <strong>Matrix
strategy</strong> — механизм АВТОМАТИЧЕСКОГО параллельного запуска
одного и того же job'а с несколькими комбинациями параметров.</p>

<h3>strategy.matrix — основной синтаксис</h3>
<p>Под <code>jobs.&lt;job_id&gt;.strategy.matrix</code> задаются
список(ки) — GitHub Actions вычисляет их ДЕКАРТОВО произведение (все
комбинации) и создаёт отдельный экземпляр job'а для каждой. Например, при
<code>python-version: ["3.10", "3.11", "3.12"]</code> одни и те же step'ы
запускаются три раза на трёх версиях, ПАРАЛЛЕЛЬНО — каждый на своём
отдельном runner'е, независимо друг от друга.</p>

<h3>Обращение к значению matrix внутри step</h3>
<p>Переменная matrix читается через <code>${{ matrix.python-version
}}</code> — это значение разное в каждом параллельном экземпляре. Его
можно передать напрямую в параметр <code>with: python-version:</code>
action'а <code>actions/setup-python@v5</code>, тогда достаточно написать
один step, а GitHub автоматически повторит его для каждой версии.</p>

<h3>Двумерная matrix — версия x операционная система</h3>
<p>В matrix можно добавить несколько ключей: например, при
<code>python-version: ["3.10", "3.11"]</code> И <code>os: [ubuntu-latest,
windows-latest]</code> — получается 2×2=4 комбинации, то есть создаётся 4
параллельных job'а (Ubuntu+3.10, Ubuntu+3.11, Windows+3.10,
Windows+3.11). Это стандартный паттерн для проверки работы библиотеки на
разных платформах.</p>

<h3>fail-fast и exclude — управление matrix</h3>
<p>При <code>strategy.fail-fast: false</code>, если одна комбинация
падает, ОСТАЛЬНЫЕ комбинации НЕ ОТМЕНЯЮТСЯ — каждая продолжается до
полного результата (по умолчанию <code>fail-fast: true</code>, т.е.
первая же ошибка останавливает всё). Через <code>exclude:</code> можно
исключить определённые комбинации (например, если устаревшая версия
Python не поддерживается на Windows). Это важно в реальных проектах для
экономии времени и минут CI.</p>

<h3>Диаграмма расширения test.yml через matrix</h3>
<pre class="mermaid">
flowchart TB
  M["strategy.matrix
python-version: [3.10, 3.11, 3.12]"] --> J1["backend (3.10)
runs-on: ubuntu-latest"]
  M --> J2["backend (3.11)
runs-on: ubuntu-latest"]
  M --> J3["backend (3.12)
runs-on: ubuntu-latest"]
  J1 --> R1["pytest tests/ - результат"]
  J2 --> R2["pytest tests/ - результат"]
  J3 --> R3["pytest tests/ - результат"]
  style J1 fill:#d6e9ff,stroke:#2266aa
  style J2 fill:#d6e9ff,stroke:#2266aa
  style J3 fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Диаграмма показывает: одно определение job'а <code>backend</code>
пишется в YAML ТОЛЬКО ОДИН РАЗ, но через matrix запускается 3 раза,
параллельно, на 3 разных версиях Python. Если все 3 комбинации проходят
успешно, ГАРАНТИРУЕТСЯ работа кода и на 3.10, и на 3.11, и на 3.12 —
текущий же test.yml означает лишь то, что код проверен на 3.11, и ничего
не говорит о работе на других версиях.</p>

<h3>Цена matrix: каждая комбинация тратит отдельную минуту</h3>
<p>Matrix не «бесплатна» — каждая комбинация это отдельный runner,
отдельная установка зависимостей, то есть отдельная минута CI. В частных
(private) репозиториях минуты GitHub Actions считаются по ограниченной
квоте (для публичных репозиториев обычно бесплатно). Поэтому matrix
нужно ограничивать не «как можно больше версий», а «реально
поддерживаемыми версиями» — например, для job frontend этой платформы
достаточно проверять только Node 20, потому что prod-сервер использует
именно эту версию; а если бы это распространялось как библиотека, было
бы разумно проверять Node 18/20/22 все три. Одним словом: matrix — это
осознанный компромисс между широтой охвата и стоимостью CI, а не повод
всегда писать самый длинный список. Хорошее практическое правило —
матрица должна отражать реально поддерживаемые версии продакшена, а не
теоретически возможные.</p>
""".strip()

L3_CODE = """
# ============================================================
# 1) test.yml'ni matrix bilan kengaytirish (backend job)
# ============================================================
jobs:
  backend:
    name: Backend (pytest)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short
# Natijada Actions tabida "backend (3.10)", "backend (3.11)", "backend
# (3.12)" nomli UCHTA alohida job ko'rinadi - barchasi parallel.

# ============================================================
# 2) Ikki o'lchamli matrix: versiya x OS
# ============================================================
jobs:
  cross-platform-test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11"]
        exclude:
          # macOS runner'lari qimmatroq va sekinroq - faqat eng yangi
          # versiyani tekshiramiz, vaqt tejash uchun.
          - os: macos-latest
            python-version: "3.10"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r backend/requirements.txt
      - run: python -m pytest backend/tests/ -v
# Jami kombinatsiya: 3 OS x 2 versiya = 6, minus 1 exclude = 5 ta parallel job.

# ============================================================
# 3) include - matrix'ga qo'shimcha, boshqacha maydon qo'shish
# ============================================================
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        include:
          # Faqat 3.12 uchun qo'shimcha "experimental: true" belgisi
          - python-version: "3.12"
            experimental: true
    continue-on-error: ${{ matrix.experimental == true }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r backend/requirements.txt
      - run: python -m pytest backend/tests/ -v
# continue-on-error: true bo'lsa, o'sha kombinatsiya muvaffaqiyatsiz
# bo'lsa ham butun workflow "muvaffaqiyatli" deb belgilanadi - eksperimental
# versiyalar uchun foydali (hali barqaror emas, lekin CI'ni to'xtatmasin).

# ============================================================
# 4) Natijaviy job nomlari GitHub UI'da qanday ko'rinadi
# ============================================================
# Actions tab -> "Tests" workflow run ->
#   backend (3.10)
#   backend (3.11)
#   backend (3.12)
#   frontend
# Har biri alohida progress-bar, alohida log, alohida muvaffaqiyat/
# muvaffaqiyatsizlik belgisi bilan.
""".strip()

L3_CODE_RU = """
# ============================================================
# 1) Расширение test.yml через matrix (job backend)
# ============================================================
jobs:
  backend:
    name: Backend (pytest)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short
# В итоге во вкладке Actions видны ТРИ отдельных job'а: "backend (3.10)",
# "backend (3.11)", "backend (3.12)" — все параллельно.

# ============================================================
# 2) Двумерная matrix: версия x ОС
# ============================================================
jobs:
  cross-platform-test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11"]
        exclude:
          # Раннеры macOS дороже и медленнее — проверяем только самую
          # новую версию, для экономии времени.
          - os: macos-latest
            python-version: "3.10"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r backend/requirements.txt
      - run: python -m pytest backend/tests/ -v
# Всего комбинаций: 3 ОС x 2 версии = 6, минус 1 exclude = 5 параллельных job'ов.

# ============================================================
# 3) include — добавление дополнительного поля в matrix
# ============================================================
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        include:
          # Только для 3.12 добавляем дополнительный флаг "experimental: true"
          - python-version: "3.12"
            experimental: true
    continue-on-error: ${{ matrix.experimental == true }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r backend/requirements.txt
      - run: python -m pytest backend/tests/ -v
# При continue-on-error: true, даже если эта комбинация упадёт, весь
# workflow помечается "успешным" — полезно для экспериментальных версий
# (ещё не стабильны, но не должны останавливать CI).

# ============================================================
# 4) Как имена итоговых job'ов выглядят в GitHub UI
# ============================================================
# Вкладка Actions -> run workflow "Tests" ->
#   backend (3.10)
#   backend (3.11)
#   backend (3.12)
#   frontend
# У каждого отдельный прогресс-бар, отдельный лог, отдельная отметка
# успеха/неудачи.
""".strip()

L3_TASK = {
    "task_title": "test.yml'ni matrix strategiyasi bilan kengaytiring",
    "task_title_ru": "Расширьте test.yml стратегией matrix",
    "task_description": (
        "Ushbu repozitoriyaning `backend` job'ini (`test.yml`dan) nusxa "
        "oling va uni `strategy.matrix.python-version: [\"3.10\", \"3.11\", "
        "\"3.12\"]` bilan kengaytiring. `fail-fast: false` qo'ying. "
        "So'ngra shaxsiy repozitoriyangizga push qilib, Actions tabida "
        "uchta alohida `backend (3.10)`, `backend (3.11)`, `backend "
        "(3.12)` job'ining PARALLEL ishga tushganini skrinshot bilan "
        "hisobotga kiriting."
    ),
    "task_description_ru": (
        "Скопируйте job `backend` (из `test.yml`) этого репозитория и "
        "расширьте его через `strategy.matrix.python-version: [\"3.10\", "
        "\"3.11\", \"3.12\"]`. Поставьте `fail-fast: false`. Затем "
        "запушьте в свой репозиторий и приложите к отчёту скриншот того, "
        "как во вкладке Actions ПАРАЛЛЕЛЬНО запустились три отдельных "
        "job'а: `backend (3.10)`, `backend (3.11)`, `backend (3.12)`."
    ),
    "task_requirements": (
        "1) Barcha uchta versiya UCHUN ham workflow muvaffaqiyatli "
        "o'tishi kerak (yoki agar biri muvaffaqiyatsiz bo'lsa, sababi "
        "tushuntirilgan bo'lishi kerak). 2) fail-fast: false qo'yilgani "
        "aniq ko'rsatilgan bo'lishi shart. 3) Matrix qiymatiga step "
        "ichida qanday murojaat qilinganini (${{ matrix.python-version "
        "}}) kodda ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Workflow должен успешно пройти для ВСЕХ трёх версий (или, "
        "если одна упала, должна быть объяснена причина). 2) Должно быть "
        "чётко показано, что установлен fail-fast: false. 3) Покажите в "
        "коде, как внутри step идёт обращение к значению matrix "
        "(${{ matrix.python-version }})."
    ),
    "task_technologies": "GitHub Actions matrix strategy, Python",
    "task_deadline_days": 4,
}

L3_SAMPLE = {
    "title": "Namuna: ikki o'lchamli matrix bilan cross-platform test",
    "description": (
        "test.yml'ning backend job'i asosida, uch OS va ikki Python "
        "versiyasida (bitta exclude bilan) ishlaydigan to'liq matrix "
        "namunasi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/matrix-demo.yml",
            "language": "yaml",
            "code": (
                "name: Matrix Demo\n\n"
                "on:\n"
                "  workflow_dispatch:\n"
                "  push:\n"
                "    branches: [\"**\"]\n\n"
                "jobs:\n"
                "  backend-matrix:\n"
                "    name: Backend (${{ matrix.os }}, py${{ matrix.python-version }})\n"
                "    runs-on: ${{ matrix.os }}\n"
                "    timeout-minutes: 10\n"
                "    strategy:\n"
                "      fail-fast: false\n"
                "      matrix:\n"
                "        os: [ubuntu-latest, windows-latest]\n"
                "        python-version: [\"3.10\", \"3.11\", \"3.12\"]\n"
                "        exclude:\n"
                "          - os: windows-latest\n"
                "            python-version: \"3.10\"\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: ${{ matrix.python-version }}\n"
                "          cache: pip\n"
                "          cache-dependency-path: backend/requirements.txt\n"
                "      - name: Install dependencies\n"
                "        working-directory: backend\n"
                "        run: pip install -r requirements.txt\n"
                "      - name: Run tests\n"
                "        working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --tb=short\n"
            ),
        },
    ],
}

L3_EXERCISES = [
    {
        "title": "Matrix'ning asosiy vazifasi",
        "title_ru": "Основная задача matrix",
        "description": "strategy.matrix ning asosiy vazifasi nima?",
        "description_ru": "Какова основная задача strategy.matrix?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir xil job'ni bir nechta parametr kombinatsiyasida parallel ishga tushirish",
            "Job'larni ketma-ket navbatga qo'yish",
            "Secret'larni shifrlash",
            "Runner tezligini oshirish",
        ],
        "options_ru": [
            "Параллельно запускать один и тот же job с несколькими комбинациями параметров",
            "Ставить job'ы в последовательную очередь",
            "Шифровать secrets",
            "Ускорять runner",
        ],
        "correct_answers": "A",
        "hint": "python-version: [\"3.10\", \"3.11\", \"3.12\"] berilsa, nechta job yaratiladi?",
        "hint_ru": "Если задано python-version: [\"3.10\", \"3.11\", \"3.12\"], сколько job'ов создаётся?",
        "explanation": "Matrix GitHub Actions'ga bir xil job ta'rifini turli parametrlar bilan avtomatik takrorlashga imkon beradi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Ikki o'lchamli matrix hisobi",
        "title_ru": "Расчёт двумерной matrix",
        "description": "os: [ubuntu-latest, windows-latest] va python-version: [\"3.10\", \"3.11\", \"3.12\"] berilsa, nechta parallel job yaratiladi (exclude'siz)?",
        "description_ru": "Если заданы os: [ubuntu-latest, windows-latest] и python-version: [\"3.10\", \"3.11\", \"3.12\"], сколько параллельных job'ов создаётся (без exclude)?",
        "exercise_type": "multiple_choice",
        "options": ["6", "2", "3", "5"],
        "options_ru": ["6", "2", "3", "5"],
        "correct_answers": "A",
        "hint": "Dekart ko'paytmasi: 2 x 3 = ?",
        "hint_ru": "Декартово произведение: 2 x 3 = ?",
        "explanation": "Matrix o'lchamlari ko'paytiriladi: 2 OS x 3 versiya = 6 kombinatsiya.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "fail-fast: false vazifasi",
        "title_ru": "Задача fail-fast: false",
        "description": "fail-fast: false qo'yilganda, bitta kombinatsiya muvaffaqiyatsiz bo'lsa, boshqalari nima bo'ladi?",
        "description_ru": "Если задано fail-fast: false, что происходит с остальными комбинациями, если одна упала?",
        "exercise_type": "multiple_choice",
        "options": ["Davom etadi, natijasini alohida ko'rsatadi", "Barchasi darhol bekor qilinadi", "Faqat ikkinchisi bekor qilinadi", "Workflow butunlay to'xtaydi"],
        "options_ru": ["Продолжают выполняться, показывая результат отдельно", "Все немедленно отменяются", "Отменяется только вторая", "Workflow полностью останавливается"],
        "correct_answers": "A",
        "hint": "Standart (true) holatda birinchi xato hammasini to'xtatadi - false esa buni o'zgartiradi.",
        "hint_ru": "По умолчанию (true) первая ошибка останавливает всё — false меняет это поведение.",
        "explanation": "fail-fast: false har bir kombinatsiyaga mustaqil yakunlanish imkonini beradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Matrix qiymatiga murojaat",
        "title_ru": "Обращение к значению matrix",
        "description": "Step ichida matrix'ning python-version qiymatiga murojaat qilish sintaksisi: ${{ ___.python-version }}",
        "description_ru": "Синтаксис обращения к значению python-version matrix внутри step: ${{ ___.python-version }}",
        "exercise_type": "fill_in_blank",
        "correct_answers": "matrix",
        "hint": "strategy.matrix ostidagi kalitga qanday murojaat qilinadi?",
        "hint_ru": "Как обращаются к ключу под strategy.matrix?",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 4 — Cache'lash: actions/cache, pip/npm keshlash
# ---------------------------------------------------------------------------

L4_TEXT = """
<h3>Muammo: har bir run bog'liqliklarni noldan o'rnatadi</h3>
<p>0-darsda o'rgangandek, <code>runs-on: ubuntu-latest</code> har safar
YANGI, toza virtual mashina beradi — demak <code>pip install</code> yoki
<code>npm ci</code> HAR BIR run'da noldan boshlanadi, hatto
<code>requirements.txt</code> yoki <code>package-lock.json</code> bir
hafta o'zgarmagan bo'lsa ham. Bu ham vaqt (har bir run bir necha daqiqa
qo'shimcha kutadi), ham tarmoq trafigini behuda sarflaydi. Yechim —
<strong>keshlash</strong>: bog'liqliklar papkasini (masalan
<code>~/.cache/pip</code> yoki <code>node_modules</code>) run'lar orasida
saqlab qolish.</p>

<h3>setup-python/setup-node'ning o'rnatilgan cache parametri</h3>
<p>Ushbu platformaning <code>test.yml</code>i eng oddiy, tavsiya
etiladigan usulni ishlatadi: <code>actions/setup-python@v5</code>ning
<code>with: cache: pip</code> va <code>actions/setup-node@v4</code>ning
<code>with: cache: npm</code> parametrlari. Bular ICHIDA
<code>actions/cache</code>ni avtomatik chaqiradi — alohida
<code>actions/cache</code> step yozish shart emas. Muhim qism —
<code>cache-dependency-path</code>: <code>test.yml</code>da
<code>backend/requirements.txt</code> va
<code>frontend/package-lock.json</code> ko'rsatilgan — bu fayl KESH
KALITINI hisoblash uchun ishlatiladi.</p>

<h3>Kesh kaliti qanday ishlaydi</h3>
<p>Kesh kaliti odatda faylning HASH'idan hosil qilinadi (masalan
<code>requirements.txt</code>ning SHA-256'i). Agar fayl o'zgarmasa, HASH
bir xil qoladi — demak eski kesh TOPILADI va qayta ishlatiladi (tez).
Agar fayl birgina qatorda o'zgarsa (yangi kutubxona qo'shilsa), HASH
BUTUNLAY boshqa bo'ladi — demak eski kesh mos KELMAYDI, yangi kesh
noldan yaratiladi (sekin, lekin TO'G'RI: eskirgan bog'liqlik hech qachon
ishlatilmaydi). Bu — <code>git</code>ning content-addressing
(112-kursning 0-darsi) bilan bir xil mantiq: kontent o'zgarsa, identifikator
ham o'zgaradi.</p>

<h3>actions/cache'ni to'g'ridan-to'g'ri ishlatish</h3>
<p>Agar <code>setup-python</code>/<code>setup-node</code>ning ichki
keshlashi yetarli bo'lmasa (masalan, boshqa bir tool — Playwright
brauzerlari, yoki Docker layer'lari — uchun), <code>actions/cache@v4</code>ni
alohida ishlatish mumkin: <code>path:</code> (nima saqlanadi),
<code>key:</code> (aniq kesh identifikatori, odatda hash bilan),
<code>restore-keys:</code> (aniq mos kelmasa, QISMAN mos keladigan eski
kesh'ni tiklash uchun zaxira ro'yxati).</p>

<h3>Kesh yagona haqiqat manbai emas — faqat tezlashtiruvchi</h3>
<p>Muhim: kesh HECH QACHON to'g'ri natijani KAFOLATLAMAYDI, faqat
TEZLASHTIRADI. Agar kesh yaroqsiz yoki eskirgan bo'lib qolsa (masalan
GitHub'ning infratuzilmasida muammo bo'lsa), <code>pip
install</code>/<code>npm ci</code> baribir haqiqiy tarmoqdan
o'rnatishga qaytadi — build hech qachon "kesh yo'q" sababli SINMAYDI,
faqat sekinlashadi. Shuning uchun kesh xatosi CI'ni to'xtatishi kerak
emas, bu — 11-darsda o'rganadigan "keng tarqalgan, lekin xavfsiz"
muammolardan biri.</p>

<h3>Keshlash oqimi diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  R["requirements.txt hash hisoblanadi"] --> D{"Kesh mavjudmi
shu hash uchun?"}
  D -->|"Ha - HIT"| RESTORE["~/.cache/pip tiklanadi
pip install TEZ ishlaydi"]
  D -->|"Yo'q - MISS"| FRESH["noldan yuklanadi
pip install SEKIN ishlaydi"]
  FRESH --> SAVE["run oxirida yangi kesh
saqlanadi (shu hash bilan)"]
  RESTORE --> RUN["pytest tests/"]
  SAVE --> RUN
  style RESTORE fill:#c8f7c5,stroke:#2a9d34
  style FRESH fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma <code>test.yml</code>dagi <code>cache: pip,
cache-dependency-path: backend/requirements.txt</code> orqali ishlaydigan
real mexanizmni ko'rsatadi: birinchi run'da kesh yo'q (MISS), lekin oxirida
saqlanadi; keyingi run'larda, agar <code>requirements.txt</code>
o'zgarmagan bo'lsa, kesh topiladi (HIT) va o'rnatish sezilarli tezlashadi.</p>

<h3>Kesh chegaralari: hajm, muddat va branch qamrovi</h3>
<p>GitHub Actions cache'i cheksiz emas: bitta repozitoriy uchun umumiy
kesh hajmi 10 GB atrofida cheklangan (limitdan oshsa, eng eski
ishlatilmagan kesh'lar avtomatik o'chiriladi), va 7 kun ichida
ishlatilmagan kesh ham avtomatik o'chiriladi. Kesh qamrovi ham muhim: bir
branch'da yaratilgan kesh, standart holatda, faqat o'sha branch va uning
asosidagi (base) branch'lar uchun ko'rinadi — butunlay boshqa, aloqasiz
branch bu keshni ko'rmaydi. Shuning uchun har bir feature branch birinchi
marta o'z alohida keshini yaratadi (asosiy branch'nikidan meros
olganidan keyin), bu — 112-kursda o'rgangan branch izolyatsiyasi
tamoyiliga o'xshash mantiq.</p>
""".strip()

L4_TEXT_RU = """
<h3>Проблема: каждый run устанавливает зависимости с нуля</h3>
<p>Как мы узнали в уроке 0, <code>runs-on: ubuntu-latest</code> каждый раз
даёт НОВУЮ, чистую виртуальную машину — значит <code>pip install</code>
или <code>npm ci</code> в КАЖДОМ run начинается с нуля, даже если
<code>requirements.txt</code> или <code>package-lock.json</code> не
менялись неделю. Это тратит и время (каждый run ждёт лишние несколько
минут), и сетевой трафик впустую. Решение — <strong>кеширование</strong>:
сохранять папку зависимостей (например <code>~/.cache/pip</code> или
<code>node_modules</code>) между run'ами.</p>

<h3>Встроенный параметр cache в setup-python/setup-node</h3>
<p><code>test.yml</code> этой платформы использует самый простой,
рекомендуемый способ: параметр <code>with: cache: pip</code> у
<code>actions/setup-python@v5</code> и <code>with: cache: npm</code> у
<code>actions/setup-node@v4</code>. Они ВНУТРИ себя автоматически
вызывают <code>actions/cache</code> — отдельный step с
<code>actions/cache</code> писать не нужно. Важная часть —
<code>cache-dependency-path</code>: в <code>test.yml</code> указаны
<code>backend/requirements.txt</code> и
<code>frontend/package-lock.json</code> — этот файл используется для
вычисления КЛЮЧА КЕША.</p>

<h3>Как работает ключ кеша</h3>
<p>Ключ кеша обычно получается из ХЕША файла (например SHA-256 файла
<code>requirements.txt</code>). Если файл не менялся, ХЕШ остаётся тем
же — значит старый кеш НАХОДИТСЯ и переиспользуется (быстро). Если файл
изменился хотя бы на одну строку (добавлена новая библиотека), ХЕШ
становится СОВСЕМ другим — значит старый кеш НЕ ПОДХОДИТ, новый кеш
создаётся с нуля (медленно, но ПРАВИЛЬНО: устаревшая зависимость никогда
не используется). Это та же логика, что и content-addressing Git (урок 0
курса 112): меняется контент — меняется идентификатор.</p>

<h3>Прямое использование actions/cache</h3>
<p>Если встроенного кеширования <code>setup-python</code>/
<code>setup-node</code> недостаточно (например, для другого инструмента —
браузеров Playwright, или слоёв Docker), можно использовать
<code>actions/cache@v4</code> отдельно: <code>path:</code> (что
сохраняется), <code>key:</code> (точный идентификатор кеша, обычно с
хешем), <code>restore-keys:</code> (резервный список для восстановления
ЧАСТИЧНО подходящего старого кеша, если точного совпадения нет).</p>

<h3>Кеш — не источник истины, а лишь ускоритель</h3>
<p>Важно: кеш НИКОГДА не гарантирует правильный результат, только
УСКОРЯЕТ. Если кеш оказался невалидным или устаревшим (например, из-за
проблемы в инфраструктуре GitHub), <code>pip install</code>/<code>npm
ci</code> всё равно вернётся к реальной установке из сети — сборка
НИКОГДА не ломается из-за "отсутствия кеша", только замедляется. Поэтому
ошибка кеша не должна останавливать CI — это одна из "распространённых,
но безопасных" проблем, которые мы изучим в уроке 11.</p>

<h3>Диаграмма потока кеширования</h3>
<pre class="mermaid">
flowchart TB
  R["вычисляется хеш requirements.txt"] --> D{"Есть ли кеш
для этого хеша?"}
  D -->|"Да - HIT"| RESTORE["~/.cache/pip восстановлен
pip install работает БЫСТРО"]
  D -->|"Нет - MISS"| FRESH["загружается с нуля
pip install работает МЕДЛЕННО"]
  FRESH --> SAVE["в конце run сохраняется
новый кеш (с этим хешем)"]
  RESTORE --> RUN["pytest tests/"]
  SAVE --> RUN
  style RESTORE fill:#c8f7c5,stroke:#2a9d34
  style FRESH fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает реальный механизм, работающий через <code>cache:
pip, cache-dependency-path: backend/requirements.txt</code> в
<code>test.yml</code>: в первом run кеша нет (MISS), но в конце он
сохраняется; в следующих run'ах, если <code>requirements.txt</code> не
менялся, кеш находится (HIT), и установка заметно ускоряется.</p>

<h3>Ограничения кеша: объём, срок и охват веток</h3>
<p>Кеш GitHub Actions не безграничен: общий объём кеша для одного
репозитория ограничен примерно 10 ГБ (при превышении лимита старые
неиспользуемые кеши удаляются автоматически), а неиспользуемый в течение
7 дней кеш тоже удаляется автоматически. Охват кеша тоже важен: кеш,
созданный в одной ветке, по умолчанию виден только для этой ветки и её
базовых (base) веток — совершенно другая, не связанная ветка этот кеш не
видит. Поэтому каждая feature-ветка при первом запуске создаёт свой
отдельный кеш (унаследовав от базовой ветки), это похоже на принцип
изоляции веток, изученный в курсе 112.</p>
""".strip()

L4_CODE = """
# ============================================================
# 1) test.yml'dagi o'rnatilgan keshlash (real, ikkala job)
# ============================================================
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: pip
    cache-dependency-path: backend/requirements.txt

- name: Set up Node
  uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: npm
    cache-dependency-path: frontend/package-lock.json
# Ikkalasi ham "cache: <manager>" - GitHub qaysi papkani keshlashni
# (~/.cache/pip yoki node_modules manba kesh papkasini) o'zi biladi,
# faqat cache-dependency-path orqali qaysi fayl KESH KALITINI
# aniqlashini ko'rsatish kifoya.

# ============================================================
# 2) deploy-frontend.yml'dagi xuddi shu naqsh
# ============================================================
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: npm
    cache-dependency-path: frontend/package-lock.json
# deploy-frontend.yml HAM xuddi shu keshlash strategiyasidan foydalanadi -
# har bir deploy'da npm ci'ni tezlashtirish uchun.

# ============================================================
# 3) actions/cache'ni to'g'ridan-to'g'ri ishlatish (qo'lda)
# ============================================================
- name: Cache pip packages manually
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
# key: aniq mos kelish uchun - hashFiles() requirements.txt kontentidan
# hash hisoblaydi (git obyektlarining SHA-1 kontent-addressing
# tamoyiliga o'xshash - 112-kurs 0-darsini eslang).
# restore-keys: aniq mos kelmasa (masalan requirements.txt biroz
# o'zgargan bo'lsa), eng yaqin mos keluvchi ESKI kesh'ni tiklaydi -
# to'liq bo'sh boshlashdan ko'ra tezroq.

# ============================================================
# 4) Playwright brauzerlarini keshlash namunasi (frontend E2E uchun)
# ============================================================
- name: Cache Playwright browsers
  uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('frontend/package-lock.json') }}

- name: Install Playwright browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'
  working-directory: frontend
  run: npx playwright install --with-deps
# id: bilan step natijasiga keyingi step'dan murojaat qilinadi.
# cache-hit != 'true' - agar kesh TOPILGAN bo'lsa, brauzerlarni QAYTA
# yuklab olishning hojati yo'q (yuklab olish o'zi bir necha daqiqa ketadi).

# ============================================================
# 5) Keshning haqiqiy tezlik farqi (namunaviy o'lchov)
# ============================================================
# Kesh YO'Q (MISS):    npm ci -> ~55 soniya (tarmoqdan yuklash)
# Kesh BOR (HIT):      npm ci -> ~8 soniya  (mahalliy nusxadan)
# Kesh YO'Q (MISS):    pip install -r requirements.txt -> ~30 soniya
# Kesh BOR (HIT):      pip install -r requirements.txt -> ~4 soniya
# Sonlar taxminiy - real vaqt tarmoq holati va paket sonига bog'liq,
# lekin nisbat (5-8x tezlashish) odatiy CI loyihalarida barqaror kuzatiladi.

# ============================================================
# 6) gh CLI orqali repozitoriy kesh'larini ko'rish va o'chirish
# ============================================================
$ gh cache list
ID      KEY                                              SIZE     CREATED
123456  Linux-pip-3a7f9e2b1c...                          45 MB    2 hours ago
123457  Linux-npm-9d8c7b6a5f...                          120 MB   1 day ago
123458  playwright-Linux-2e1d0c9b...                     310 MB   3 days ago

$ gh cache delete 123458
# Eskirgan yoki noto'g'ri kesh'ni qo'lda o'chirish - masalan, kesh
# buzilgan (corrupt) bo'lib qolsa yoki 10 GB limitiga yaqinlashilsa.

$ gh cache delete --all
# BARCHA repozitoriy kesh'larini tozalash - keyingi run to'liq MISS
# bo'ladi, lekin bu xavfsiz: build hech qachon shu sababdan sinmaydi.

# ============================================================
# 7) Docker layer keshlash - boshqa turdagi kesh, xuddi shu tamoyil
# ============================================================
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build with layer cache
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    push: false
    cache-from: type=gha
    cache-to: type=gha,mode=max
# type=gha - GitHub Actions'ning o'z kesh backend'idan foydalanish,
# xuddi actions/cache kabi, lekin Docker qatlamlari (layer) uchun
# maxsuslashtirilgan. Har bir o'zgarmagan Dockerfile qatlami qayta
# qurilmaydi - faqat o'zgargan qatlamdan boshlab qayta quriladi.

# ============================================================
# 8) Kesh o'lchamini kuzatish - GitHub UI orqali
# ============================================================
# Repo -> Settings -> Actions -> Caches bo'limida:
#   - Har bir kesh yozuvi: kalit, hajm, oxirgi ishlatilgan vaqt
#   - Umumiy sig'im chizig'i (10 GB'ga nisbatan foiz)
#   - "Delete" tugmasi - qo'lda tozalash uchun
# Bu bo'lim ayniqsa ko'p matrix kombinatsiyasi ishlatilganda foydali -
# har bir kombinatsiya o'z alohida kesh yozuvini yaratishi mumkin, va
# ular jamlanib tez orada 10 GB limitiga yaqinlashishi mumkin.
""".strip()

L4_CODE_RU = """
# ============================================================
# 1) Встроенное кеширование в test.yml (реальное, оба job'а)
# ============================================================
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: pip
    cache-dependency-path: backend/requirements.txt

- name: Set up Node
  uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: npm
    cache-dependency-path: frontend/package-lock.json
# Оба варианта "cache: <manager>" - GitHub сам знает, какую папку
# кешировать (исходную кеш-папку ~/.cache/pip или node_modules),
# достаточно только через cache-dependency-path указать, какой файл
# определяет КЛЮЧ КЕША.

# ============================================================
# 2) Тот же паттерн в deploy-frontend.yml
# ============================================================
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: npm
    cache-dependency-path: frontend/package-lock.json
# deploy-frontend.yml ТОЖЕ использует ту же стратегию кеширования - для
# ускорения npm ci при каждом деплое.

# ============================================================
# 3) Прямое использование actions/cache (вручную)
# ============================================================
- name: Cache pip packages manually
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
# key: для точного совпадения - hashFiles() вычисляет хеш из содержимого
# requirements.txt (похоже на принцип content-addressing SHA-1 объектов
# Git - вспомните урок 0 курса 112).
# restore-keys: если точного совпадения нет (например, requirements.txt
# немного изменился), восстанавливает ближайший подходящий СТАРЫЙ кеш -
# быстрее, чем начинать полностью с нуля.

# ============================================================
# 4) Пример кеширования браузеров Playwright (для frontend E2E)
# ============================================================
- name: Cache Playwright browsers
  uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('frontend/package-lock.json') }}

- name: Install Playwright browsers
  if: steps.playwright-cache.outputs.cache-hit != 'true'
  working-directory: frontend
  run: npx playwright install --with-deps
# id: используется для обращения к результату step из следующего step.
# cache-hit != 'true' - если кеш НАЙДЕН, нет смысла ЗАНОВО скачивать
# браузеры (само скачивание занимает несколько минут).

# ============================================================
# 5) Реальная разница в скорости при кешировании (примерное измерение)
# ============================================================
# Кеша НЕТ (MISS):    npm ci -> ~55 секунд (загрузка из сети)
# Кеш ЕСТЬ (HIT):      npm ci -> ~8 секунд  (из локальной копии)
# Кеша НЕТ (MISS):    pip install -r requirements.txt -> ~30 секунд
# Кеш ЕСТЬ (HIT):      pip install -r requirements.txt -> ~4 секунды
# Цифры примерные - реальное время зависит от состояния сети и числа
# пакетов, но соотношение (ускорение в 5-8 раз) стабильно наблюдается в
# типичных CI-проектах.

# ============================================================
# 6) Просмотр и удаление кешей репозитория через gh CLI
# ============================================================
$ gh cache list
ID      KEY                                              SIZE     CREATED
123456  Linux-pip-3a7f9e2b1c...                          45 MB    2 hours ago
123457  Linux-npm-9d8c7b6a5f...                          120 MB   1 day ago
123458  playwright-Linux-2e1d0c9b...                     310 MB   3 days ago

$ gh cache delete 123458
# Ручное удаление устаревшего или неверного кеша - например, если кеш
# оказался повреждён (corrupt) или приближается лимит в 10 ГБ.

$ gh cache delete --all
# Очистка ВСЕХ кешей репозитория - следующий run будет полным MISS,
# но это безопасно: сборка никогда не ломается по этой причине.

# ============================================================
# 7) Кеширование слоёв Docker - другой тип кеша, тот же принцип
# ============================================================
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build with layer cache
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    push: false
    cache-from: type=gha
    cache-to: type=gha,mode=max
# type=gha - использование собственного кеш-бэкенда GitHub Actions,
# как и actions/cache, но специализированного для слоёв (layer) Docker.
# Каждый неизменившийся слой Dockerfile не пересобирается - пересборка
# начинается только с изменившегося слоя.

# ============================================================
# 8) Отслеживание размера кеша через GitHub UI
# ============================================================
# Репо -> Settings -> Actions -> Caches:
#   - Каждая запись кеша: ключ, размер, время последнего использования
#   - Общая шкала ёмкости (в процентах от 10 ГБ)
#   - Кнопка "Delete" - для ручной очистки
# Этот раздел особенно полезен при большом числе комбинаций matrix -
# каждая комбинация может создавать свою отдельную запись кеша, и они
# в сумме могут быстро приблизиться к лимиту в 10 ГБ.
""".strip()

L4_TASK = {
    "task_title": "Keshlashning oldi va keyingi tezligini o'lchang",
    "task_title_ru": "Измерьте скорость до и после кеширования",
    "task_description": (
        "Shaxsiy (yoki fork qilingan) repozitoriyangizda `test.yml`ning "
        "backend job'ini ikki marta ishga tushiring: birinchi marta "
        "keshni butunlay o'chirib (cache-dependency-path'ni olib "
        "tashlab, yoki Settings -> Actions -> Caches orqali eski keshni "
        "o'chirib), ikkinchi marta kesh yoqilgan holda. Ikkala 'Install "
        "dependencies' step'ining vaqtini solishtiring va farqni "
        "hisobotga yozing."
    ),
    "task_description_ru": (
        "В своём (или форкнутом) репозитории запустите job backend из "
        "`test.yml` дважды: первый раз полностью отключив кеш (убрав "
        "cache-dependency-path, или удалив старый кеш через Settings -> "
        "Actions -> Caches), второй раз с включённым кешем. Сравните "
        "время обоих step'ов 'Install dependencies' и запишите разницу в "
        "отчёт."
    ),
    "task_requirements": (
        "1) Ikkala run'ning 'Install dependencies' step vaqti aniq "
        "(soniyalarda) ko'rsatilgan bo'lishi kerak. 2) Kesh HIT/MISS "
        "holatini GitHub Actions log'idan (\"Cache restored from key\" "
        "yoki \"Cache not found\") tasdiqlang. 3) Nima uchun kesh hech "
        "qachon build'ni SINDIRMASLIGINI (faqat sekinlashtirishini) bir "
        "gapda tushuntiring."
    ),
    "task_requirements_ru": (
        "1) Должно быть точно указано время step'а 'Install "
        "dependencies' (в секундах) для обоих run'ов. 2) Подтвердите "
        "статус кеша HIT/MISS из лога GitHub Actions (\"Cache restored "
        "from key\" или \"Cache not found\"). 3) Объясните одним "
        "предложением, почему кеш никогда не ЛОМАЕТ сборку (только "
        "замедляет)."
    ),
    "task_technologies": "GitHub Actions cache, actions/cache",
    "task_deadline_days": 3,
}

L4_SAMPLE = {
    "title": "Namuna: qo'lda actions/cache + Playwright keshi",
    "description": (
        "pip keshini qo'lda (restore-keys bilan) va Playwright "
        "brauzerlarini cache-hit tekshiruvi bilan keshlaydigan to'liq "
        "namuna workflow."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/cache-demo.yml",
            "language": "yaml",
            "code": (
                "name: Cache Demo\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [\"**\"]\n\n"
                "jobs:\n"
                "  backend-with-manual-cache:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: \"3.11\"\n\n"
                "      - name: Cache pip packages\n"
                "        uses: actions/cache@v4\n"
                "        id: pip-cache\n"
                "        with:\n"
                "          path: ~/.cache/pip\n"
                "          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}\n"
                "          restore-keys: |\n"
                "            ${{ runner.os }}-pip-\n\n"
                "      - name: Report cache status\n"
                "        run: echo \"Kesh holati: ${{ steps.pip-cache.outputs.cache-hit }}\"\n\n"
                "      - name: Install dependencies\n"
                "        working-directory: backend\n"
                "        run: pip install -r requirements.txt\n\n"
                "      - name: Run tests\n"
                "        working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --tb=short\n"
            ),
        },
    ],
}

L4_EXERCISES = [
    {
        "title": "Kesh nima uchun kerak",
        "title_ru": "Зачем нужен кеш",
        "description": "actions/cache'ning asosiy maqsadi nima?",
        "description_ru": "Какова основная цель actions/cache?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bog'liqliklarni run'lar orasida saqlab, o'rnatishni tezlashtirish",
            "Kodni shifrlash",
            "Testlarni parallel ishga tushirish",
            "Secret'larni saqlash",
        ],
        "options_ru": [
            "Сохранять зависимости между run'ами, ускоряя установку",
            "Шифровать код",
            "Запускать тесты параллельно",
            "Хранить secrets",
        ],
        "correct_answers": "A",
        "hint": "Har bir run yangi virtual mashinada boshlanadi - bu nimani anglatadi?",
        "hint_ru": "Каждый run начинается на новой виртуальной машине - что это значит?",
        "explanation": "Kesh bog'liqliklar papkasini saqlab, tarmoqdan qayta yuklashning oldini oladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Kesh kaliti qanday hisoblanadi",
        "title_ru": "Как вычисляется ключ кеша",
        "description": "test.yml'da backend uchun kesh kaliti qaysi faylga bog'liq?",
        "description_ru": "От какого файла зависит ключ кеша для backend в test.yml?",
        "exercise_type": "multiple_choice",
        "options": ["backend/requirements.txt", "backend/app/main.py", "README.md", ".github/workflows/test.yml"],
        "options_ru": ["backend/requirements.txt", "backend/app/main.py", "README.md", ".github/workflows/test.yml"],
        "correct_answers": "A",
        "hint": "cache-dependency-path parametrining qiymatini eslang.",
        "hint_ru": "Вспомните значение параметра cache-dependency-path.",
        "explanation": "cache-dependency-path: backend/requirements.txt shu faylning hash'idan kesh kalitini hosil qiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Kesh MISS bo'lganda nima bo'ladi",
        "title_ru": "Что происходит при кеш MISS",
        "description": "Agar kesh topilmasa (MISS), build sinadimi?",
        "description_ru": "Если кеш не найден (MISS), сборка ломается?",
        "exercise_type": "multiple_choice",
        "options": ["Yo'q, faqat sekinroq bajariladi, tarmoqdan o'rnatadi", "Ha, build darhol to'xtaydi", "Ha, lekin faqat Windows'da", "Yo'q, lekin testlar o'tkazib yuboriladi"],
        "options_ru": ["Нет, просто выполняется медленнее, устанавливая из сети", "Да, сборка немедленно останавливается", "Да, но только на Windows", "Нет, но тесты пропускаются"],
        "correct_answers": "A",
        "hint": "Kesh faqat tezlashtiruvchi, u yagona ma'lumot manbai emas.",
        "hint_ru": "Кеш — только ускоритель, а не единственный источник данных.",
        "explanation": "Kesh yo'qligi hech qachon build'ni sindirmaydi, chunki paketlar baribir tarmoqdan o'rnatiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "setup-python cache parametri",
        "title_ru": "Параметр cache в setup-python",
        "description": "actions/setup-python@v5'da pip keshlashni yoqadigan parametr: cache: ___",
        "description_ru": "Параметр в actions/setup-python@v5, включающий кеширование pip: cache: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "pip",
        "hint": "test.yml'dagi Set up Python step'ini eslang.",
        "hint_ru": "Вспомните шаг Set up Python в test.yml.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 5 — R1: Takrorlash (mini-capstone) — asoslar, trigger, secrets, matrix, cache
# ---------------------------------------------------------------------------

L5_TEXT = """
<h3>Bu darsda yangi mavzu yo'q — sintez</h3>
<p>Bu — birinchi takrorlash darsi. 0-4-darslarda o'rgangan HAMMA narsani
BITTA workflow faylida birlashtiramiz: workflow anatomiyasi (0-dars),
trigger strategiyasi (1-dars), secret/env farqi (2-dars), matrix
build (3-dars) va keshlash (4-dars). Yangi tushuncha yo'q — faqat
mavjud bilimni bitta izchil, real ishlaydigan faylga yig'ish.</p>

<h3>Besh mavzuni bitta workflow'da ko'rish</h3>
<p>Quyidagi kod namunasida har bir qism qaysi darsdan kelganini
izohlarda ko'rasiz: <code>on:</code> bloki (1-dars: push+paths+
workflow_dispatch), <code>concurrency:</code> (1-dars), matrix
strategiyasi (3-dars: uch Python versiyasi), <code>cache: pip</code>
(4-dars), va <code>secrets.</code> orqali SSH ulanish (2-dars). Bu —
real jamoada yozilishi mumkin bo'lgan, ishlab chiqarishga tayyor CI/CD
faylining ko'rinishi.</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Agar <code>frontend/src/App.js</code> fayli <code>server</code>
branch'iga push qilinsa, quyidagi uchta workflow'dan qaysilari ishga
tushadi: <code>test.yml</code>, <code>deploy-backend.yml</code>,
<code>deploy-frontend.yml</code>?</li>
<li>Nima uchun <code>SSH_PRIVATE_KEY</code> secret sifatida, lekin
<code>NODE_OPTIONS</code> oddiy env sifatida saqlanadi?</li>
<li>3 ta Python versiyasida matrix ishlatilsa va <code>fail-fast:
true</code> (standart) bo'lsa, 3.10'da xato chiqsa, 3.11 va 3.12 ham
darhol bekor qilinadimi?</li>
<li><code>requirements.txt</code>ga bitta yangi kutubxona qo'shilsa,
keshning HIT/MISS holati o'zgaradimi? Nega?</li>
</ul>

<h3>Besh mavzuning bitta workflow'dagi joylashuvi</h3>
<pre class="mermaid">
flowchart TB
  T["on: push+paths, workflow_dispatch
(1-dars)"] --> C["concurrency group
(1-dars)"]
  C --> J["job: deploy
strategy.matrix python-version
(3-dars)"]
  J --> CA["setup-python
cache: pip
(4-dars)"]
  CA --> SEC["env: secrets.SSH_PRIVATE_KEY
(2-dars)"]
  SEC --> RUN["ssh orqali deploy
(0-dars: uses/run anatomiyasi)"]
  style T fill:#d6e9ff,stroke:#2266aa
  style CA fill:#ffe9b3,stroke:#d09000
  style SEC fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Diagramma 0-4-darslarning har biri BITTA real workflow ichida qanday
qatlam bo'lib joylashishini ko'rsatadi — bu keyingi darslarda (deploy,
branch himoyasi, reusable workflow) ustiga qurib boradigan asosiy
"skelet".</p>

<h3>Nega bu dars qisqaroq</h3>
<p>Bu takrorlash darsi qasddan yangi tushunchalar bilan "shishirilmagan" —
uning vazifasi 0-4-darslarni BOG'LASH, yangi material qo'shish emas. Kod
namunasi to'liq ishlaydigan workflow, lekin har bir qatori allaqachon
tanish. Keyingi, 6-darsdan boshlab yana yangi mavzular (artifact'lar,
real deploy, branch himoyasi) davom etadi.</p>
""".strip()

L5_TEXT_RU = """
<h3>В этом уроке нет новой темы — синтез</h3>
<p>Это — первый урок повторения. Собираем ВСЁ изученное в уроках 0-4 в
ОДИН файл workflow: анатомия workflow (урок 0), стратегия триггеров
(урок 1), разница secret/env (урок 2), matrix build (урок 3) и
кеширование (урок 4). Новых понятий нет — только сборка существующих
знаний в один цельный, реально работающий файл.</p>

<h3>Пять тем в одном workflow</h3>
<p>В примере кода ниже вы увидите в комментариях, из какого урока пришла
каждая часть: блок <code>on:</code> (урок 1: push+paths+
workflow_dispatch), <code>concurrency:</code> (урок 1), стратегия matrix
(урок 3: три версии Python), <code>cache: pip</code> (урок 4), и
подключение по SSH через <code>secrets.</code> (урок 2). Это — вид
готового к продакшену файла CI/CD, который может быть написан в реальной
команде.</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Если файл <code>frontend/src/App.js</code> запушен в ветку
<code>server</code>, какие из трёх workflow запустятся:
<code>test.yml</code>, <code>deploy-backend.yml</code>,
<code>deploy-frontend.yml</code>?</li>
<li>Почему <code>SSH_PRIVATE_KEY</code> хранится как secret, а
<code>NODE_OPTIONS</code> — как обычный env?</li>
<li>Если используется matrix с 3 версиями Python и стоит
<code>fail-fast: true</code> (по умолчанию), и на 3.10 произошла ошибка —
отменятся ли немедленно 3.11 и 3.12?</li>
<li>Если в <code>requirements.txt</code> добавлена одна новая
библиотека, изменится ли статус кеша HIT/MISS? Почему?</li>
</ul>

<h3>Расположение пяти тем в одном workflow</h3>
<pre class="mermaid">
flowchart TB
  T["on: push+paths, workflow_dispatch
(урок 1)"] --> C["группа concurrency
(урок 1)"]
  C --> J["job: deploy
strategy.matrix python-version
(урок 3)"]
  J --> CA["setup-python
cache: pip
(урок 4)"]
  CA --> SEC["env: secrets.SSH_PRIVATE_KEY
(урок 2)"]
  SEC --> RUN["деплой через ssh
(урок 0: анатомия uses/run)"]
  style T fill:#d6e9ff,stroke:#2266aa
  style CA fill:#ffe9b3,stroke:#d09000
  style SEC fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Диаграмма показывает, как каждый из уроков 0-4 располагается слоем
внутри ОДНОГО реального workflow — это базовый "скелет", на который мы
будем наращивать в следующих уроках (деплой, защита веток, reusable
workflow).</p>

<h3>Почему этот урок короче</h3>
<p>Этот урок повторения намеренно не "раздут" новыми понятиями — его
задача СВЯЗАТЬ уроки 0-4, а не добавить новый материал. Пример кода —
полностью рабочий workflow, но каждая его строка уже знакома. Начиная со
следующего, 6-го урока, снова пойдут новые темы (артефакты, реальный
деплой, защита веток).</p>
""".strip()

L5_CODE = """
# ============================================================
# Sintez workflow: 0-4-darslarning HAMMASI bitta faylda
# ============================================================
name: Full CI/CD Recap Demo
# ^ 0-dars: workflow darajasidagi name

on:                                    # <- 1-dars: trigger strategiyasi
  push:
    branches: [server]
    paths:
      - 'backend/**'
  workflow_dispatch:

concurrency:                           # <- 1-dars: bir vaqtda ikkita
  group: recap-deploy                  #    deploy to'qnashmasligi
  cancel-in-progress: false

jobs:
  test-and-deploy:
    name: Test (${{ matrix.python-version }}) then deploy
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:                          # <- 3-dars: matrix build
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4      # <- 0-dars: uses bilan tayyor action

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip                   # <- 4-dars: keshlash
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies      # <- 0-dars: run bilan shell buyrug'i
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

      - name: Configure SSH             # <- 2-dars: secret vs oddiy env
        if: matrix.python-version == '3.11'   # faqat bitta versiyada deploy
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# Har bir savolga qisqa javob (o'z-o'zini tekshirish uchun)
# ============================================================
# 1) frontend/src/App.js -> server branch:
#    test.yml -> ISHGA TUSHADI (har qanday branch)
#    deploy-backend.yml -> ISHGA TUSHMAYDI (paths mos kelmadi)
#    deploy-frontend.yml -> ISHGA TUSHADI (paths=frontend/** mos keldi)
#
# 2) SSH_PRIVATE_KEY maxfiy (server kirish huquqi), NODE_OPTIONS oshkor
#    bo'lsa ham xavf yo'q (faqat build sozlamasi).
#
# 3) Ha, fail-fast: true (standart) bo'lsa, 3.10 xato bersa, 3.11/3.12
#    HAM darhol bekor qilinadi - shuning uchun ko'p loyihalar
#    fail-fast: false qo'yadi (3-darsni eslang).
#
# 4) Ha, o'zgaradi - kesh kaliti requirements.txt HASH'idan hisoblanadi,
#    fayl o'zgarsa hash ham o'zgaradi, demak eski kesh endi mos kelmaydi
#    (MISS), yangi kesh yaratiladi.
""".strip()

L5_CODE_RU = """
# ============================================================
# Синтез-workflow: ВСЁ из уроков 0-4 в одном файле
# ============================================================
name: Full CI/CD Recap Demo
# ^ урок 0: name на уровне workflow

on:                                    # <- урок 1: стратегия триггеров
  push:
    branches: [server]
    paths:
      - 'backend/**'
  workflow_dispatch:

concurrency:                           # <- урок 1: чтобы два деплоя
  group: recap-deploy                  #    не сталкивались одновременно
  cancel-in-progress: false

jobs:
  test-and-deploy:
    name: Test (${{ matrix.python-version }}) then deploy
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:                          # <- урок 3: matrix build
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4      # <- урок 0: uses с готовым action

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip                   # <- урок 4: кеширование
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies      # <- урок 0: run с shell-командой
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

      - name: Configure SSH             # <- урок 2: secret против обычного env
        if: matrix.python-version == '3.11'   # деплой только на одной версии
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# Краткие ответы на каждый вопрос (для самопроверки)
# ============================================================
# 1) frontend/src/App.js -> ветка server:
#    test.yml -> ЗАПУСКАЕТСЯ (любая ветка)
#    deploy-backend.yml -> НЕ ЗАПУСКАЕТСЯ (paths не совпал)
#    deploy-frontend.yml -> ЗАПУСКАЕТСЯ (paths=frontend/** совпал)
#
# 2) SSH_PRIVATE_KEY секретен (доступ к серверу), NODE_OPTIONS не несёт
#    риска даже при раскрытии (только настройка сборки).
#
# 3) Да, при fail-fast: true (по умолчанию), если 3.10 упадёт, 3.11/3.12
#    ТОЖЕ немедленно отменятся - поэтому многие проекты ставят
#    fail-fast: false (вспомните урок 3).
#
# 4) Да, изменится - ключ кеша вычисляется из ХЕША requirements.txt,
#    если файл изменился, хеш тоже меняется, значит старый кеш больше не
#    подходит (MISS), создаётся новый кеш.
""".strip()

L5_TASK = {
    "task_title": "Sintez workflow'ni yozing va ishga tushiring",
    "task_title_ru": "Напишите и запустите синтез-workflow",
    "task_description": (
        "Shaxsiy repozitoriyangizda 0-4-darslarning HAMMA elementlarini "
        "(trigger+paths, concurrency, matrix, cache, secrets orqali SSH) "
        "birlashtirgan bitta workflow yozing (ushbu darsdagi namunaga "
        "asoslanib, lekin o'zingizning loyihangizga moslab). Uni push "
        "qilib, muvaffaqiyatli ishga tushirganini isbotlang."
    ),
    "task_description_ru": (
        "В своём репозитории напишите один workflow, объединяющий ВСЕ "
        "элементы уроков 0-4 (триггер+paths, concurrency, matrix, cache, "
        "SSH через secrets) — на основе примера этого урока, но "
        "адаптированный под ваш проект. Запушьте и докажите успешный "
        "запуск."
    ),
    "task_requirements": (
        "1) Workflow kamida 3 xil matrix kombinatsiyasida ishga tushishi "
        "kerak. 2) Kamida bitta secret va bitta oddiy env o'zgaruvchisi "
        "ishlatilgan bo'lishi shart. 3) cache: pip yoki cache: npm "
        "qo'llanilgan va uning HIT/MISS holati log'da ko'rsatilgan "
        "bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Workflow должен запускаться минимум с 3 разными "
        "комбинациями matrix. 2) Должны использоваться минимум один "
        "secret и одна обычная переменная env. 3) Должен применяться "
        "cache: pip или cache: npm, а его статус HIT/MISS должен быть "
        "показан в логе."
    ),
    "task_technologies": "GitHub Actions (workflow, matrix, cache, secrets)",
    "task_deadline_days": 4,
}

L5_SAMPLE = {
    "title": "Namuna: 0-4-darslarning barchasini birlashtirgan workflow",
    "description": (
        "Ushbu darsning kod namunasi asosida, izohlar bilan to'liq "
        "ishlaydigan sintez workflow fayli."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/recap-r1-demo.yml",
            "language": "yaml",
            "code": (
                "name: Recap R1 Demo\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [server]\n"
                "    paths:\n"
                "      - 'backend/**'\n"
                "  workflow_dispatch:\n\n"
                "concurrency:\n"
                "  group: recap-r1-demo\n"
                "  cancel-in-progress: false\n\n"
                "jobs:\n"
                "  test-matrix:\n"
                "    name: Test (${{ matrix.python-version }})\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    strategy:\n"
                "      fail-fast: false\n"
                "      matrix:\n"
                "        python-version: [\"3.10\", \"3.11\", \"3.12\"]\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: ${{ matrix.python-version }}\n"
                "          cache: pip\n"
                "          cache-dependency-path: backend/requirements.txt\n"
                "      - working-directory: backend\n"
                "        run: pip install -r requirements.txt\n"
                "      - working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --tb=short\n"
            ),
        },
    ],
}

L5_EXERCISES = [
    {
        "title": "Trigger + paths sintezi",
        "title_ru": "Синтез trigger + paths",
        "description": "Faqat `server` branch'ida va faqat `backend/` papkasi o'zgarganda ishga tushuvchi trigger qanday yoziladi?",
        "description_ru": "Как записать триггер, который срабатывает только в ветке `server` и только при изменении папки `backend/`?",
        "exercise_type": "multiple_choice",
        "options": [
            "on: push: branches: [server], paths: ['backend/**']",
            "on: push: branches: ['**']",
            "on: pull_request: branches: [backend]",
            "on: schedule: cron: '0 3 * * *'",
        ],
        "options_ru": [
            "on: push: branches: [server], paths: ['backend/**']",
            "on: push: branches: ['**']",
            "on: pull_request: branches: [backend]",
            "on: schedule: cron: '0 3 * * *'",
        ],
        "correct_answers": "A",
        "hint": "deploy-backend.yml'dagi on: blokini eslang.",
        "hint_ru": "Вспомните блок on: в deploy-backend.yml.",
        "explanation": "branches ANIQ branch nomini, paths ANIQ papkani cheklaydi - ikkalasi birga eng tor filtrni beradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Matrix + fail-fast sintezi",
        "title_ru": "Синтез matrix + fail-fast",
        "description": "3 ta Python versiyasida matrix ishlatilib, `fail-fast: false` qo'yilgan. 3.10 muvaffaqiyatsiz bo'lsa, 3.11 va 3.12 nima bo'ladi?",
        "description_ru": "Используется matrix с 3 версиями Python, задан `fail-fast: false`. Если 3.10 упадёт, что произойдёт с 3.11 и 3.12?",
        "exercise_type": "multiple_choice",
        "options": ["Ular davom etadi va o'z natijasini beradi", "Ular ham darhol bekor qilinadi", "Faqat 3.11 bekor qilinadi", "Butun workflow qayta boshlanadi"],
        "options_ru": ["Продолжатся и дадут свой результат", "Они тоже немедленно отменятся", "Отменится только 3.11", "Весь workflow перезапустится"],
        "correct_answers": "A",
        "hint": "3-darsdagi fail-fast: false ta'rifini eslang.",
        "hint_ru": "Вспомните определение fail-fast: false из урока 3.",
        "explanation": "fail-fast: false har bir kombinatsiyani mustaqil yakunlaydi, boshqalarning holatidan qat'iy nazar.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Secret vs env sintezi",
        "title_ru": "Синтез secret против env",
        "description": "SSH ulanish uchun kalit qanday saqlanishi kerak?",
        "description_ru": "Как должен храниться ключ для SSH-подключения?",
        "exercise_type": "multiple_choice",
        "options": ["secrets.SSH_PRIVATE_KEY sifatida", "env: SSH_PRIVATE_KEY: \"oshkor matn\" sifatida", "README.md ichida", "package.json ichida"],
        "options_ru": ["Как secrets.SSH_PRIVATE_KEY", "Как env: SSH_PRIVATE_KEY: \"открытый текст\"", "Внутри README.md", "Внутри package.json"],
        "correct_answers": "A",
        "hint": "2-darsdagi maxfiy vs oddiy qiymat farqini eslang.",
        "hint_ru": "Вспомните разницу секретного и обычного значения из урока 2.",
        "explanation": "Har qanday server kirish huquqini beruvchi qiymat secrets orqali saqlanishi shart.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Kesh kaliti sintezi",
        "title_ru": "Синтез ключа кеша",
        "description": "Kesh kaliti odatda qaysi funksiya orqali fayl kontentidan hisoblanadi: ___Files('requirements.txt')",
        "description_ru": "Через какую функцию обычно вычисляется ключ кеша из содержимого файла: ___Files('requirements.txt')",
        "exercise_type": "fill_in_blank",
        "correct_answers": "hash",
        "hint": "4-darsdagi actions/cache namunasini eslang - hashFiles(...) shaklida edi.",
        "hint_ru": "Вспомните пример actions/cache из 4-го урока — он был в форме hashFiles(...).",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 6 — Artifact'lar va build natijalari
# ---------------------------------------------------------------------------

L6_TEXT = """
<h3>Muammo: job tugagach, uning fayllari yo'qoladi</h3>
<p>0-darsda o'rgangandek, har bir job o'z alohida, vaqtinchalik runner'ida
ishlaydi va tugagach BUTUNLAY o'chiriladi — u yaratgan fayllar (masalan
build natijasi, test hisoboti, log) HAM birga yo'qoladi. Agar boshqa job
o'sha fayllarga muhtoj bo'lsa (masalan, "build" job'i yasagan
<code>frontend/build/</code> papkasini "deploy" job'i serverga
yuborishi kerak bo'lsa), ularni job'lar orasida uzatish uchun maxsus
mexanizm kerak — bu <strong>artifact</strong>.</p>

<h3>deploy-frontend.yml qanday qiladi — hozircha artifact'siz</h3>
<p>Qiziq holat: <code>deploy-frontend.yml</code> BITTA job ichida ham
build qiladi (<code>npm run build</code>), ham natijani serverga
yuboradi (<code>rsync</code>) — shuning uchun bu workflow'da artifact
kerak EMAS, chunki build va deploy bitta job'ning ICHIDA, bir xil
runner faylizmida ketma-ket bajariladi. Artifact faqat build va deploy
turli JOB'larga (yoki turli WORKFLOW'larga) bo'linganda kerak bo'ladi —
masalan, agar build'ni bir necha OS/versiyada matrix orqali (3-dars)
tekshirib, faqat ENG mos natijani deploy qilish kerak bo'lsa.</p>

<h3>actions/upload-artifact va actions/download-artifact</h3>
<p><code>actions/upload-artifact@v4</code> — joriy job'ning fayl(lar)ini
GitHub'ning vaqtinchalik saqlash joyiga yuklaydi (<code>name:</code> —
identifikator, <code>path:</code> — qaysi fayl/papka, <code>retention-
days:</code> — necha kun saqlanishi, standart 90 kun). Boshqa job (yoki
hatto boshqa workflow, agar <code>workflow_run</code> orqali bog'langan
bo'lsa) <code>actions/download-artifact@v4</code> bilan aynan shu nom
orqali uni tiklab oladi. Bu — kesh (4-dars)dan farqli: kesh IXTIYORIY
tezlashtiruvchi (yo'q bo'lsa qayta hisoblanadi), artifact esa aniq NATIJA
— agar u yo'qolsa, keyingi job ishlay OLMAYDI (chunki fayl haqiqatan ham
yo'q, qayta "hisoblab" bo'lmaydi, faqat qaytadan build qilib chiqarish
kerak).</p>

<h3>Build verifikatsiyasi — artifact yuklashdan oldingi muhim qadam</h3>
<p><code>deploy-frontend.yml</code>ning "Verify build artefact" step'i
diqqatga sazovor: <code>test -f frontend/build/index.html || { echo
"::error::build/index.html missing"; exit 1; }</code>. Bu — "eng yomon
sokin xato holatini" ushlash: build 0 kod bilan tugashi mumkin, lekin
haqiqatda HECH NARSA yaratmasligi mumkin (masalan disk to'lib qolsa).
Bu tekshiruv bo'lmasa, keyingi qadam (rsync) BO'SH papkani prod serverga
yuborib, saytni butunlay buzishi mumkin edi. Artifact yuklashdan oldin
ham xuddi shunday tekshiruv qo'shish yaxshi amaliyot — bo'sh yoki
yaroqsiz artifact'ni yuklashning o'zi hech qanday foyda bermaydi.</p>

<h3>Artifact orqali job'lar o'rtasida fayl uzatish oqimi</h3>
<pre class="mermaid">
flowchart LR
  B["job: build
npm run build"] -->|"actions/upload-artifact
name: frontend-build"| A["GitHub artifact
saqlash joyi"]
  A -->|"actions/download-artifact
name: frontend-build"| D["job: deploy
rsync serverga"]
  B -.->|"job tugagach runner
o'chiriladi, fayllar yo'qoladi"| X["yo'qolgan fayllar
(artifact bo'lmasa)"]
  style A fill:#ffe9b3,stroke:#d09000
  style X fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Diagramma shuni ko'rsatadi: agar build va deploy IKKI alohida job'ga
bo'linsa (hozirgi <code>deploy-frontend.yml</code>dagidek BITTA job emas),
build natijasi artifact orqali "ko'prik" vazifasini bajaradi — aks holda
"deploy" job'i boshlanganda "build" job'ining fayllari allaqachon
yo'qolgan bo'lardi, chunki ular boshqa, allaqachon o'chirilgan runner'da
yaratilgan edi.</p>

<h3>Artifact chegaralari va Actions tabidan yuklab olish</h3>
<p>Artifact ham cheksiz emas: standart saqlash muddati 90 kun (
<code>retention-days</code> orqali qisqartirish mumkin — masalan, vaqtinchalik
build natijalari uchun 1 kun kifoya, xarajatni tejash uchun). Har bir
artifact GitHub'ning umumiy repozitoriy saqlash kvotasiga qo'shiladi.
Foydali amaliy jihat: har qanday workflow run tugagach, GitHub UI'dagi
o'sha run sahifasida "Artifacts" bo'limi paydo bo'ladi — inson u yerdan
qo'lda ZIP fayl sifatida yuklab olishi mumkin, bu ayniqsa CI muvaffaqiyatsiz
bo'lgan build natijasini (yoki test-report.xml'ni) tekshirish uchun qulay,
hech qanday qo'shimcha buyruqsiz. Bu — hech qanday boshqa job dasturiy
ravishda artifact so'ramagan taqdirda ham, inson uchun qulay kirish
nuqtasi.</p>
""".strip()

L6_TEXT_RU = """
<h3>Проблема: после завершения job его файлы исчезают</h3>
<p>Как мы узнали в уроке 0, каждый job работает на своём отдельном,
временном runner'е и после завершения ПОЛНОСТЬЮ уничтожается — созданные
им файлы (например результат сборки, отчёт теста, лог) ИСЧЕЗАЮТ вместе с
ним. Если другому job'у нужны эти файлы (например, job "build" создал
папку <code>frontend/build/</code>, а job "deploy" должен отправить её
на сервер), нужен специальный механизм передачи между job'ами — это
<strong>artifact</strong>.</p>

<h3>Как это делает deploy-frontend.yml — пока без artifact</h3>
<p>Интересный случай: <code>deploy-frontend.yml</code> И собирает
(<code>npm run build</code>), И отправляет результат на сервер
(<code>rsync</code>) ВНУТРИ ОДНОГО job'а — поэтому в этом workflow
artifact НЕ НУЖЕН, ведь сборка и деплой выполняются последовательно
внутри одного job'а, в одной и той же файловой системе runner'а. Artifact
нужен только когда build и deploy разделены на разные JOB'ы (или разные
WORKFLOW), например, если сборка тестируется в нескольких ОС/версиях
через matrix (урок 3), а деплоится только ЛУЧШИЙ подходящий результат.</p>

<h3>actions/upload-artifact и actions/download-artifact</h3>
<p><code>actions/upload-artifact@v4</code> — загружает файл(ы) текущего
job'а во временное хранилище GitHub (<code>name:</code> — идентификатор,
<code>path:</code> — какой файл/папка, <code>retention-days:</code> —
сколько дней хранить, по умолчанию 90 дней). Другой job (или даже другой
workflow, если связан через <code>workflow_run</code>) через
<code>actions/download-artifact@v4</code> восстанавливает его по этому же
имени. Это отличается от кеша (урок 4): кеш — НЕОБЯЗАТЕЛЬНЫЙ ускоритель
(если его нет, всё пересчитывается), artifact — точный РЕЗУЛЬТАТ — если
он потерян, следующий job работать НЕ СМОЖЕТ (потому что файла реально
нет, его нельзя "пересчитать", можно только заново собрать).</p>

<h3>Верификация сборки — важный шаг перед загрузкой artifact</h3>
<p>Step "Verify build artefact" в <code>deploy-frontend.yml</code>
примечателен: <code>test -f frontend/build/index.html || { echo
"::error::build/index.html missing"; exit 1; }</code>. Это — отлов
"худшего тихого режима отказа": сборка может завершиться с кодом 0, но
реально НИЧЕГО не создать (например, если диск заполнился). Без этой
проверки следующий шаг (rsync) отправил бы ПУСТУЮ папку на prod-сервер,
полностью сломав сайт. Добавлять такую же проверку перед загрузкой
artifact — хорошая практика: загрузка пустого или невалидного artifact
сама по себе не приносит никакой пользы.</p>

<h3>Поток передачи файлов между job'ами через artifact</h3>
<pre class="mermaid">
flowchart LR
  B["job: build
npm run build"] -->|"actions/upload-artifact
name: frontend-build"| A["хранилище GitHub
artifact"]
  A -->|"actions/download-artifact
name: frontend-build"| D["job: deploy
rsync на сервер"]
  B -.->|"после job runner
уничтожается, файлы исчезают"| X["утерянные файлы
(без artifact)"]
  style A fill:#ffe9b3,stroke:#d09000
  style X fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Диаграмма показывает: если build и deploy разделены на ДВА разных
job'а (не как сейчас в <code>deploy-frontend.yml</code>, где это ОДИН
job), результат сборки играет роль "моста" через artifact — иначе к
моменту начала job "deploy" файлы job "build" уже исчезли бы, так как
были созданы на другом, уже уничтоженном runner'е.</p>

<h3>Ограничения artifact и скачивание из вкладки Actions</h3>
<p>Artifact тоже не безграничен: стандартный срок хранения — 90 дней (
можно сократить через <code>retention-days</code> — например, для
временных результатов сборки достаточно 1 дня, экономя место). Каждый
artifact учитывается в общей квоте хранения репозитория GitHub. Полезная
практическая деталь: после завершения любого run workflow на странице
этого run в GitHub UI появляется раздел "Artifacts" — человек может
вручную скачать его оттуда как ZIP-файл, что особенно удобно для
проверки результата сборки при неудачном CI (или test-report.xml), без
каких-либо дополнительных команд. Это удобная точка входа для человека,
даже когда никакой другой job внутри workflow не запрашивал artifact
программно. Полезно держать в голове это разграничение: кеш экономит
время внутри одного и того же вида job'а между запусками, а artifact
переносит конкретный результат конкретного запуска дальше по конвейеру
или человеку.</p>
""".strip()

L6_CODE = """
# ============================================================
# 1) deploy-frontend.yml'ning haqiqiy verifikatsiya step'i
#    (artifact ISHLATILMAYDI, chunki bitta job ichida ketma-ket)
# ============================================================
- name: Build production bundle
  working-directory: frontend
  env:
    REACT_APP_API_URL: https://tech.gennis.uz/
    CI: 'false'
    NODE_OPTIONS: --max-old-space-size=4096
    GENERATE_SOURCEMAP: 'false'
  run: npm run build

- name: Verify build artefact
  run: |
    test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }
    echo "Build size:"
    du -sh frontend/build
    ls -la frontend/build

- name: Rsync build to prod
  env:
    SSH_HOST: ${{ secrets.SSH_HOST }}
    SSH_USER: ${{ secrets.SSH_USER }}
    SSH_PORT: ${{ secrets.SSH_PORT }}
  run: |
    PORT="${SSH_PORT:-22}"
    rsync -avz --delete \\
      -e "ssh -i ~/.ssh/deploy_key -p $PORT -o StrictHostKeyChecking=yes" \\
      frontend/build/ \\
      "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"
# Bitta job ichida: build -> verify -> rsync. Artifact YO'Q, chunki
# hammasi bitta runner faylizmida, ketma-ket.

# ============================================================
# 2) Agar build va deploy IKKI job'ga bo'linsa - artifact KERAK bo'ladi
# ============================================================
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          REACT_APP_API_URL: https://tech.gennis.uz/
          CI: 'false'
          GENERATE_SOURCEMAP: 'false'
        run: npm run build
      - name: Verify build artefact
        run: test -f frontend/build/index.html || { echo "::error::missing"; exit 1; }

      # <- YANGI qadam: build natijasini artifact sifatida yuklash
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: frontend-build
          path: frontend/build/
          retention-days: 1

  deploy:
    needs: build          # <- deploy job build job tugashini kutadi
    runs-on: ubuntu-latest
    steps:
      # <- YANGI qadam: build job'ining artifact'ini shu job'ga tiklash
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: frontend-build
          path: frontend/build/

      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST: ${{ secrets.SSH_HOST }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null

      - name: Rsync build to prod
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
        run: |
          rsync -avz --delete \\
            -e "ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes" \\
            frontend/build/ "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"
# needs: build - artifact tayyor bo'lguncha deploy BOSHLANMAYDI.
# Bu ikki job'li bo'linish foydali: masalan, "build" job'ini alohida
# saqlab, bir necha marta "deploy"ni QAYTA ishga tushirish mumkin (11-dars
# - re-run) - build'ni har safar QAYTA yig'ish shart emas.

# ============================================================
# 3) Test hisobotini artifact sifatida saqlash (pytest bilan)
# ============================================================
- name: Run tests with report
  working-directory: backend
  run: python -m pytest tests/ -v --tb=short --junitxml=test-report.xml

- name: Upload test report
  if: always()          # <- testlar MUVAFFAQIYATSIZ bo'lsa ham hisobot saqlansin
  uses: actions/upload-artifact@v4
  with:
    name: pytest-report
    path: backend/test-report.xml
    retention-days: 14
# if: always() - test.yml'dagi "Cleanup SSH key" step'idagi bilan bir xil
# naqsh (2-dars): hisobot HAR DOIM saqlanishi kerak, test o'tdimi
# yoki yo'qmi - ayniqsa muvaffaqiyatsizlikni keyinroq tahlil qilish uchun.
""".strip()

L6_CODE_RU = """
# ============================================================
# 1) Реальный шаг верификации из deploy-frontend.yml
#    (artifact НЕ ИСПОЛЬЗУЕТСЯ, т.к. всё внутри одного job'а)
# ============================================================
- name: Build production bundle
  working-directory: frontend
  env:
    REACT_APP_API_URL: https://tech.gennis.uz/
    CI: 'false'
    NODE_OPTIONS: --max-old-space-size=4096
    GENERATE_SOURCEMAP: 'false'
  run: npm run build

- name: Verify build artefact
  run: |
    test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }
    echo "Build size:"
    du -sh frontend/build
    ls -la frontend/build

- name: Rsync build to prod
  env:
    SSH_HOST: ${{ secrets.SSH_HOST }}
    SSH_USER: ${{ secrets.SSH_USER }}
    SSH_PORT: ${{ secrets.SSH_PORT }}
  run: |
    PORT="${SSH_PORT:-22}"
    rsync -avz --delete \\
      -e "ssh -i ~/.ssh/deploy_key -p $PORT -o StrictHostKeyChecking=yes" \\
      frontend/build/ \\
      "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"
# Внутри одного job'а: build -> verify -> rsync. Artifact НЕТ, т.к. всё
# происходит в одной файловой системе runner'а, последовательно.

# ============================================================
# 2) Если build и deploy разделены на ДВА job'а - artifact НУЖЕН
# ============================================================
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          REACT_APP_API_URL: https://tech.gennis.uz/
          CI: 'false'
          GENERATE_SOURCEMAP: 'false'
        run: npm run build
      - name: Verify build artefact
        run: test -f frontend/build/index.html || { echo "::error::missing"; exit 1; }

      # <- НОВЫЙ шаг: загрузка результата сборки как artifact
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: frontend-build
          path: frontend/build/
          retention-days: 1

  deploy:
    needs: build          # <- job deploy ждёт завершения job build
    runs-on: ubuntu-latest
    steps:
      # <- НОВЫЙ шаг: восстановление artifact job'а build в этот job
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: frontend-build
          path: frontend/build/

      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST: ${{ secrets.SSH_HOST }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null

      - name: Rsync build to prod
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
        run: |
          rsync -avz --delete \\
            -e "ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes" \\
            frontend/build/ "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"
# needs: build - деплой НЕ НАЧНЁТСЯ, пока artifact не готов.
# Такое разделение на два job'а полезно: например, можно хранить job
# "build" отдельно и несколько раз ПОВТОРЯТЬ запуск "deploy" (урок 11 —
# re-run) - пересобирать build заново каждый раз не нужно.

# ============================================================
# 3) Сохранение отчёта тестов как artifact (с pytest)
# ============================================================
- name: Run tests with report
  working-directory: backend
  run: python -m pytest tests/ -v --tb=short --junitxml=test-report.xml

- name: Upload test report
  if: always()          # <- отчёт сохраняется, даже если тесты УПАЛИ
  uses: actions/upload-artifact@v4
  with:
    name: pytest-report
    path: backend/test-report.xml
    retention-days: 14
# if: always() - тот же паттерн, что и в step "Cleanup SSH key" из
# test.yml (урок 2): отчёт ДОЛЖЕН сохраняться всегда, прошли тесты или
# нет - особенно для последующего анализа неудачи.
""".strip()

L6_TASK = {
    "task_title": "Build va deploy'ni ikki job'ga ajratib, artifact bilan bog'lang",
    "task_title_ru": "Разделите build и deploy на два job'а, свяжите через artifact",
    "task_description": (
        "`deploy-frontend.yml`ni asos qilib oling va uni IKKI alohida "
        "job'ga bo'ling: `build` (checkout, setup-node, npm ci, npm run "
        "build, verify, keyin `actions/upload-artifact`) va `deploy` "
        "(`needs: build`, `actions/download-artifact`, keyin SSH+rsync). "
        "Shaxsiy repozitoriyangizda push qilib, ikkala job'ning "
        "ketma-ketligini (deploy build tugashini kutishini) Actions "
        "tabida ko'rsating."
    ),
    "task_description_ru": (
        "Возьмите за основу `deploy-frontend.yml` и разделите его на ДВА "
        "отдельных job'а: `build` (checkout, setup-node, npm ci, npm run "
        "build, verify, затем `actions/upload-artifact`) и `deploy` "
        "(`needs: build`, `actions/download-artifact`, затем SSH+rsync). "
        "Запушьте в свой репозиторий и покажите во вкладке Actions "
        "последовательность (deploy ждёт завершения build)."
    ),
    "task_requirements": (
        "1) `build` job artifact'ni to'g'ri yuklashi va `deploy` job uni "
        "to'g'ri tiklashi kerak (bir xil `name:`). 2) `needs: build` "
        "aniq ko'rsatilgan bo'lishi shart. 3) Verify qadami build "
        "natijasi bo'sh bo'lmasligini tekshirishi kerak."
    ),
    "task_requirements_ru": (
        "1) Job `build` должен корректно загружать artifact, а job "
        "`deploy` — корректно его восстанавливать (одинаковое `name:`). "
        "2) Должно быть чётко указано `needs: build`. 3) Шаг verify "
        "должен проверять, что результат сборки не пуст."
    ),
    "task_technologies": "GitHub Actions artifacts, upload-artifact, download-artifact",
    "task_deadline_days": 4,
}

L6_SAMPLE = {
    "title": "Namuna: build+test-report artifact bilan ikki job'li workflow",
    "description": (
        "Backend testini ishga tushirib, hisobotni artifact sifatida "
        "saqlaydigan va frontend build'ini alohida job'da yig'ib, "
        "artifact orqali deploy job'iga uzatuvchi to'liq namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/artifact-demo.yml",
            "language": "yaml",
            "code": (
                "name: Artifact Demo\n\n"
                "on:\n"
                "  workflow_dispatch:\n\n"
                "jobs:\n"
                "  test-backend:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: \"3.11\"\n"
                "          cache: pip\n"
                "          cache-dependency-path: backend/requirements.txt\n"
                "      - working-directory: backend\n"
                "        run: pip install -r requirements.txt\n"
                "      - working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --junitxml=test-report.xml\n"
                "      - name: Upload test report\n"
                "        if: always()\n"
                "        uses: actions/upload-artifact@v4\n"
                "        with:\n"
                "          name: pytest-report\n"
                "          path: backend/test-report.xml\n"
                "          retention-days: 14\n\n"
                "  build-frontend:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 15\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-node@v4\n"
                "        with:\n"
                "          node-version: '20'\n"
                "          cache: npm\n"
                "          cache-dependency-path: frontend/package-lock.json\n"
                "      - working-directory: frontend\n"
                "        run: npm ci --no-audit --no-fund\n"
                "      - working-directory: frontend\n"
                "        env:\n"
                "          CI: 'false'\n"
                "          GENERATE_SOURCEMAP: 'false'\n"
                "        run: npm run build\n"
                "      - name: Verify build artefact\n"
                "        run: test -f frontend/build/index.html || { echo \"::error::missing\"; exit 1; }\n"
                "      - name: Upload build artifact\n"
                "        uses: actions/upload-artifact@v4\n"
                "        with:\n"
                "          name: frontend-build\n"
                "          path: frontend/build/\n"
                "          retention-days: 1\n"
            ),
        },
    ],
}

L6_EXERCISES = [
    {
        "title": "Artifact nima uchun kerak",
        "title_ru": "Зачем нужен artifact",
        "description": "Artifact'ning asosiy vazifasi nima?",
        "description_ru": "Какова основная задача artifact?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir job'ning faylini boshqa job'ga (yoki keyinroq foydalanish uchun) saqlab uzatish",
            "Secret'larni shifrlash",
            "Bog'liqliklarni tezroq o'rnatish",
            "Testlarni parallel ishga tushirish",
        ],
        "options_ru": [
            "Сохранять и передавать файл одного job'а другому (или для использования позже)",
            "Шифровать secrets",
            "Быстрее устанавливать зависимости",
            "Запускать тесты параллельно",
        ],
        "correct_answers": "A",
        "hint": "Job tugagach uning fayllari nima bo'ladi?",
        "hint_ru": "Что происходит с файлами job'а после его завершения?",
        "explanation": "Artifact job tugagandan keyin ham fayllarni saqlab, boshqa job yoki keyingi foydalanish uchun beradi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Artifact vs cache",
        "title_ru": "Artifact против cache",
        "description": "Artifact bilan cache orasidagi asosiy farq nima?",
        "description_ru": "В чём основное отличие artifact от cache?",
        "exercise_type": "multiple_choice",
        "options": [
            "Cache ixtiyoriy tezlashtiruvchi, artifact esa aniq kerakli natija",
            "Ular butunlay bir xil",
            "Cache faqat Python uchun, artifact faqat Node uchun",
            "Artifact hech qachon saqlanmaydi",
        ],
        "options_ru": [
            "Cache — необязательный ускоритель, artifact — точно нужный результат",
            "Они полностью одинаковы",
            "Cache только для Python, artifact только для Node",
            "Artifact никогда не сохраняется",
        ],
        "correct_answers": "A",
        "hint": "Agar kesh yo'qolsa, build sinadimi? Agar artifact yo'qolsa-chi?",
        "hint_ru": "Если кеш потеряется, сломается ли сборка? А если потеряется artifact?",
        "explanation": "Kesh yo'qligi faqat sekinlashtiradi, artifact yo'qligi esa keyingi job'ni ISHLAY OLMAYDIGAN qiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "deploy-frontend.yml'da artifact nega yo'q",
        "title_ru": "Почему в deploy-frontend.yml нет artifact",
        "description": "deploy-frontend.yml build va rsync'ni bitta job ichida qiladi. Nega bunda artifact kerak emas?",
        "description_ru": "deploy-frontend.yml делает build и rsync внутри одного job'а. Почему artifact здесь не нужен?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bitta job ichida fayllar bir xil runner faylizmida qoladi",
            "Chunki artifact faqat matrix bilan ishlaydi",
            "Chunki rsync artifact talab qilmaydi",
            "Chunki frontend build artifact bo'la olmaydi",
        ],
        "options_ru": [
            "Потому что внутри одного job'а файлы остаются в одной файловой системе runner'а",
            "Потому что artifact работает только с matrix",
            "Потому что rsync не требует artifact",
            "Потому что frontend build не может быть artifact",
        ],
        "correct_answers": "A",
        "hint": "Artifact faqat job'lar ORASIDA kerak - bitta job ichida kerakmi?",
        "hint_ru": "Artifact нужен только МЕЖДУ job'ами — нужен ли он внутри одного job'а?",
        "explanation": "Bitta job ichidagi step'lar bir xil runner diskini ishlatadi, fayllar allaqachon bir joyda.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Artifact yuklash action'i",
        "title_ru": "Action для загрузки artifact",
        "description": "Joriy job natijasini artifact sifatida yuklaydigan tayyor action nomi: actions/___-artifact",
        "description_ru": "Имя готового action, загружающего результат текущего job'а как artifact: actions/___-artifact",
        "exercise_type": "fill_in_blank",
        "correct_answers": "upload",
        "hint": "Yuklash - inglizcha \"upload\".",
        "hint_ru": "Загрузка — по-английски \"upload\".",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 7 — Real deploy target'ga joylashtirish: deploy-backend.yml va deploy-frontend.yml
# ---------------------------------------------------------------------------

L7_TEXT = """
<h3>Ikkita haqiqiy deploy strategiyasi — nega ular boshqacha</h3>
<p>Ushbu platforma backend va frontend uchun IKKI XIL deploy strategiyasi
ishlatadi, va sabab chuqur: backend — Python kodi, serverning o'zida
ishlaydi (systemd service sifatida), shuning uchun uni deploy qilish
"kodni yangilab, xizmatni qayta ishga tushirish". Frontend esa — statik
fayllar (HTML/JS/CSS), brauzerda ishlaydi, shuning uchun uni deploy
qilish "build qilib, natijani serverga nusxalash". Ikkalasi ham
<code>server</code> branch'iga push orqali ishga tushadi, lekin
ICHKI mexanizmi butunlay boshqacha.</p>

<h3>deploy-backend.yml: SSH orqali pull + restart</h3>
<p>Bu workflow'ning mantig'i sodda: (1) SSH kalitini vaqtinchalik faylga
yozish, (2) <code>ssh-keyscan</code> orqali server "host key"ini oldindan
bilib olish (MITM hujumidan himoya — 112-kursdagi content-addressing
tamoyiliga o'xshab, kutilmagan o'zgarishni oldindan aniqlash), (3) SSH
orqali serverga ulanib, BITTA uzun buyruq zanjirini bajarish:
<code>git pull</code>, <code>pip install</code>, <code>systemctl
restart</code>. Muhim qism — oxirgi tekshiruv: <code>systemctl
is-active --quiet "$SERVICE_NAME" && echo 'Service is running' || {
systemctl status ...; exit 1; }</code>. Bu — xizmat HAQIQATAN ishga
tushganini tasdiqlaydi; agar xizmat sinib qolsa (masalan yangi kodda
sintaksis xatosi bo'lsa), workflow QIZIL bo'lib, jamoaga darhol
xabar beradi — aks holda "deploy muvaffaqiyatli" degan yolg'on signal
bilan server aslida ishlamay qolgan bo'lardi.</p>

<h3>deploy-frontend.yml: CI'da build, keyin rsync</h3>
<p>Bu workflow'ning boshidagi kommentariyada MUHIM tarixiy sabab bor:
"Earlier deploys ran npm run build directly on the production server and
OOM-killed mid-build" — ya'ni ilgari build TO'G'RIDAN-TO'G'RI prod
serverda bajarilgan va xotira yetishmay (OOM — Out Of Memory) o'rtada
o'chib qolib, YARIM yozilgan <code>build/</code> papkasi bilan sayt
buzilgan. Yechim: build'ni GitHub Actions runner'ida (7 GB RAM, 4 core —
prod serverdan ko'ra ko'proq resurs) bajarish, va faqat TAYYOR natijani
<code>rsync</code> orqali serverga ko'chirish. Bu — "build joyi bilan
ishlash joyini ajratish" tamoyilining aniq amaliy namunasi.</p>

<h3>rsync --delete va oxiridagi slash — ikkita nozik, lekin muhim detal</h3>
<p><code>rsync -avz --delete ... frontend/build/
"$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"</code>.
<code>--delete</code> — manba papkada YO'Q bo'lgan faylni maqsad
papkadan HAM o'chiradi (aks holda eskirgan, endi kerak bo'lmagan JS
fayllari serverda abadiy qolib ketardi). Manba yo'lidagi OXIRIDAGI SLASH
esa — izohda aniq ta'kidlanganidek — "load-bearing": slash bo'lmasa,
rsync <code>build/</code> papkaning O'ZINI (papka sifatida) maqsad ichiga
nusxalaydi, natijada <code>.../frontend/build/build/index.html</code>
kabi ICHMA-ICH, noto'g'ri yo'l hosil bo'ladi.</p>

<h3>concurrency va systemctl tekshiruvi ikkala faylda ham takrorlanadi</h3>
<p>1-darsda ko'rgan <code>concurrency: {group: ..., cancel-in-progress:
false}</code> ikkala deploy faylida ham bor — ikkita tez ketma-ket push
bitta prod serverga bir vaqtda ikkita rsync/restart yubormasligi uchun.
Bu ikkala fayl mustaqil yozilgan bo'lsa-da, bir xil xavfsizlik naqshini
takrorlaydi — bu tasodif emas, katta jamoalarda "deploy pipeline
checklist" sifatida hujjatlashtiriladigan umumiy amaliyot.</p>

<h3>Ikki deploy strategiyasining taqqoslash diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  subgraph BE["deploy-backend.yml"]
    B1["SSH bilan ulanish"] --> B2["git pull origin server
(serverning o'zida)"]
    B2 --> B3["pip install
(serverning o'zida)"]
    B3 --> B4["systemctl restart
+ is-active tekshiruvi"]
  end
  subgraph FE["deploy-frontend.yml"]
    F1["npm ci + npm run build
(GitHub runner'ida, 7GB RAM)"] --> F2["Verify build artefact
index.html bormi?"]
    F2 --> F3["rsync --delete
runner -> prod serverga"]
  end
  style B4 fill:#c8f7c5,stroke:#2a9d34
  style F3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Diagramma ikkala workflow'ning TUBDAN farqli falsafasini ko'rsatadi:
backend deploy — "serverning o'zida yangilash" (chunki backend serverda
ISHLAYDI), frontend deploy — "boshqa joyda tayyorlab, faqat natijani
ko'chirish" (chunki frontend faqat STATIK fayl, uni har qanday joyda
qurish mumkin, prod serverning o'zida emas).</p>
""".strip()

L7_TEXT_RU = """
<h3>Две реальные стратегии деплоя — почему они разные</h3>
<p>Эта платформа использует ДВЕ РАЗНЫЕ стратегии деплоя для backend и
frontend, и причина глубокая: backend — код на Python, работает на самом
сервере (как systemd-сервис), поэтому его деплой — это "обновить код и
перезапустить сервис". Frontend же — статические файлы (HTML/JS/CSS),
работает в браузере, поэтому его деплой — "собрать и скопировать
результат на сервер". Оба запускаются через push в ветку
<code>server</code>, но ВНУТРЕННИЙ механизм совершенно разный.</p>

<h3>deploy-backend.yml: pull + restart через SSH</h3>
<p>Логика этого workflow проста: (1) записать SSH-ключ во временный
файл, (2) через <code>ssh-keyscan</code> заранее узнать "host key"
сервера (защита от MITM-атаки — похоже на принцип content-addressing из
курса 112: заранее обнаружить неожиданное изменение), (3) подключиться
по SSH к серверу и выполнить ОДНУ длинную цепочку команд:
<code>git pull</code>, <code>pip install</code>, <code>systemctl
restart</code>. Важная часть — финальная проверка: <code>systemctl
is-active --quiet "$SERVICE_NAME" && echo 'Service is running' || {
systemctl status ...; exit 1; }</code>. Она подтверждает, что сервис
ДЕЙСТВИТЕЛЬНО запустился; если сервис упал (например, в новом коде
синтаксическая ошибка), workflow становится КРАСНЫМ и сразу сигнализирует
команде — иначе был бы ложный сигнал "деплой успешен", хотя сервер на
самом деле не работает.</p>

<h3>deploy-frontend.yml: сборка в CI, затем rsync</h3>
<p>В комментарии в начале этого workflow есть ВАЖНАЯ историческая
причина: "Earlier deploys ran npm run build directly on the production
server and OOM-killed mid-build" — то есть раньше сборка выполнялась
НАПРЯМУЮ на prod-сервере, и из-за нехватки памяти (OOM — Out Of Memory)
процесс обрывался посередине, оставляя ПОЛОВИНУ записанной папки
<code>build/</code>, что ломало сайт. Решение: выполнять сборку на
runner'е GitHub Actions (7 ГБ RAM, 4 ядра — больше ресурсов, чем на
prod-сервере), и переносить на сервер через <code>rsync</code> только
ГОТОВЫЙ результат. Это — конкретный практический пример принципа
"разделить место сборки и место работы".</p>

<h3>rsync --delete и завершающий слэш — две тонкие, но важные детали</h3>
<p><code>rsync -avz --delete ... frontend/build/
"$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"</code>.
<code>--delete</code> — удаляет из целевой папки и файл, которого НЕТ в
исходной (иначе устаревшие, больше не нужные JS-файлы навсегда
оставались бы на сервере). ЗАВЕРШАЮЩИЙ СЛЭШ в исходном пути — как чётко
подмечено в комментарии — "load-bearing" (несущий): без слэша rsync
скопирует САМУ папку <code>build/</code> (как папку) внутрь целевой,
получив ВЛОЖЕННЫЙ, неверный путь вроде
<code>.../frontend/build/build/index.html</code>.</p>

<h3>concurrency и проверка systemctl повторяются в обоих файлах</h3>
<p><code>concurrency: {group: ..., cancel-in-progress: false}</code> из
урока 1 есть в ОБОИХ файлах деплоя — чтобы два быстро следующих push не
отправили одновременно два rsync/restart на один prod-сервер. Хотя эти
два файла написаны независимо, они повторяют один и тот же паттерн
безопасности — это не совпадение, а общая практика, которую в больших
командах документируют как "чеклист pipeline деплоя".</p>

<h3>Диаграмма сравнения двух стратегий деплоя</h3>
<pre class="mermaid">
flowchart TB
  subgraph BE["deploy-backend.yml"]
    B1["Подключение по SSH"] --> B2["git pull origin server
(на самом сервере)"]
    B2 --> B3["pip install
(на самом сервере)"]
    B3 --> B4["systemctl restart
+ проверка is-active"]
  end
  subgraph FE["deploy-frontend.yml"]
    F1["npm ci + npm run build
(на runner'е GitHub, 7ГБ RAM)"] --> F2["Verify build artefact
есть ли index.html?"]
    F2 --> F3["rsync --delete
runner -> на prod-сервер"]
  end
  style B4 fill:#c8f7c5,stroke:#2a9d34
  style F3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Диаграмма показывает КОРЕННОЕ различие философии двух workflow: деплой
backend — "обновление на самом сервере" (т.к. backend РАБОТАЕТ на
сервере), деплой frontend — "подготовка в другом месте, перенос только
результата" (т.к. frontend — просто СТАТИЧЕСКИЕ файлы, их можно собрать
где угодно, не обязательно на самом prod-сервере).</p>
""".strip()

L7_CODE = """
# ============================================================
# 1) deploy-backend.yml - to'liq, real fayl
# ============================================================
name: Deploy Backend

on:
  push:
    branches: [server]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-backend
  cancel-in-progress: false

jobs:
  deploy:
    name: Pull & restart backend
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Pull latest code and restart service
        env:
          SSH_HOST:     ${{ secrets.SSH_HOST }}
          SSH_USER:     ${{ secrets.SSH_USER }}
          SSH_PORT:     ${{ secrets.SSH_PORT }}
          BACKEND_DIR:  ${{ secrets.BACKEND_DIR }}
          SERVICE_NAME: ${{ secrets.SERVICE_NAME }}
        run: |
          PORT="${SSH_PORT:-22}"
          ssh -i ~/.ssh/deploy_key -p "$PORT" -o StrictHostKeyChecking=yes \\
              "$SSH_USER@$SSH_HOST" \\
              "set -e
               git -C \\"$BACKEND_DIR\\" pull origin server
               cd \\"$BACKEND_DIR\\"
               source venv/bin/activate
               pip install -r requirements.txt --quiet
               systemctl restart \\"$SERVICE_NAME\\"
               systemctl is-active --quiet \\"$SERVICE_NAME\\" && echo 'Service is running' || { echo 'Service failed to start'; systemctl status \\"$SERVICE_NAME\\" --no-pager; exit 1; }"

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# 2) deploy-frontend.yml - to'liq, real fayl
# ============================================================
name: Deploy Frontend

on:
  push:
    branches: [server]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-frontend
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 25

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci --no-audit --no-fund

      - name: Build production bundle
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://tech.gennis.uz/
          CI: 'false'
          NODE_OPTIONS: --max-old-space-size=4096
          GENERATE_SOURCEMAP: 'false'
        run: npm run build

      - name: Verify build artefact
        run: |
          test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }
          echo "Build size:"
          du -sh frontend/build
          ls -la frontend/build

      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh
          chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Rsync build to prod
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
        run: |
          PORT="${SSH_PORT:-22}"
          rsync -avz --delete \\
            -e "ssh -i ~/.ssh/deploy_key -p $PORT -o StrictHostKeyChecking=yes" \\
            frontend/build/ \\
            "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# 3) Nima uchun rsync'dagi oxirgi slash MUHIM (amaliy tajriba)
# ============================================================
# TO'G'RI (slash BILAN manba yo'lida):
#   rsync frontend/build/ user@host:/var/www/site/build/
#   -> /var/www/site/build/index.html  (TO'G'RI)
#
# NOTO'G'RI (slashSIZ):
#   rsync frontend/build user@host:/var/www/site/build/
#   -> /var/www/site/build/build/index.html  (ICHMA-ICH, NOTO'G'RI!)
#   Sayt "404 Not Found" beradi, chunki server index.html'ni
#   /var/www/site/build/ ichida emas, build/build/ ichida qidiradi.

# ============================================================
# 4) systemctl tekshiruvining ahamiyati - deploy "muvaffaqiyatli"
#    signalini yolg'ondan bermaslik
# ============================================================
$ systemctl restart student-platform-backend
$ systemctl is-active --quiet student-platform-backend && echo OK || echo FAIL
# Agar restart buyrug'i "muvaffaqiyatli" qaytsa-yu, lekin xizmat DARHOL
# yiqilib qolsa (masalan .env faylida SECRET_KEY yo'q bo'lsa), shu
# tekshiruvsiz workflow baribir "yashil" bo'lib qolardi - eng xavfli
# yolg'on signal turi.
""".strip()

L7_CODE_RU = """
# ============================================================
# 1) deploy-backend.yml - полный, реальный файл
# ============================================================
name: Deploy Backend

on:
  push:
    branches: [server]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-backend
  cancel-in-progress: false

jobs:
  deploy:
    name: Pull & restart backend
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh && chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Pull latest code and restart service
        env:
          SSH_HOST:     ${{ secrets.SSH_HOST }}
          SSH_USER:     ${{ secrets.SSH_USER }}
          SSH_PORT:     ${{ secrets.SSH_PORT }}
          BACKEND_DIR:  ${{ secrets.BACKEND_DIR }}
          SERVICE_NAME: ${{ secrets.SERVICE_NAME }}
        run: |
          PORT="${SSH_PORT:-22}"
          ssh -i ~/.ssh/deploy_key -p "$PORT" -o StrictHostKeyChecking=yes \\
              "$SSH_USER@$SSH_HOST" \\
              "set -e
               git -C \\"$BACKEND_DIR\\" pull origin server
               cd \\"$BACKEND_DIR\\"
               source venv/bin/activate
               pip install -r requirements.txt --quiet
               systemctl restart \\"$SERVICE_NAME\\"
               systemctl is-active --quiet \\"$SERVICE_NAME\\" && echo 'Service is running' || { echo 'Service failed to start'; systemctl status \\"$SERVICE_NAME\\" --no-pager; exit 1; }"

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# 2) deploy-frontend.yml - полный, реальный файл
# ============================================================
name: Deploy Frontend

on:
  push:
    branches: [server]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  workflow_dispatch:

concurrency:
  group: deploy-frontend
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 25

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci --no-audit --no-fund

      - name: Build production bundle
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://tech.gennis.uz/
          CI: 'false'
          NODE_OPTIONS: --max-old-space-size=4096
          GENERATE_SOURCEMAP: 'false'
        run: npm run build

      - name: Verify build artefact
        run: |
          test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }
          echo "Build size:"
          du -sh frontend/build
          ls -la frontend/build

      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SSH_HOST:        ${{ secrets.SSH_HOST }}
          SSH_PORT:        ${{ secrets.SSH_PORT }}
        run: |
          mkdir -p ~/.ssh
          chmod 700 ~/.ssh
          printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          PORT="${SSH_PORT:-22}"
          ssh-keyscan -p "$PORT" -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
          chmod 644 ~/.ssh/known_hosts

      - name: Rsync build to prod
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
        run: |
          PORT="${SSH_PORT:-22}"
          rsync -avz --delete \\
            -e "ssh -i ~/.ssh/deploy_key -p $PORT -o StrictHostKeyChecking=yes" \\
            frontend/build/ \\
            "$SSH_USER@$SSH_HOST:/var/www/tech_gennis/frontend/build/"

      - name: Cleanup SSH key
        if: always()
        run: rm -f ~/.ssh/deploy_key

# ============================================================
# 3) Почему завершающий слэш в rsync ВАЖЕН (практический опыт)
# ============================================================
# ПРАВИЛЬНО (слэш В исходном пути):
#   rsync frontend/build/ user@host:/var/www/site/build/
#   -> /var/www/site/build/index.html  (ПРАВИЛЬНО)
#
# НЕПРАВИЛЬНО (без слэша):
#   rsync frontend/build user@host:/var/www/site/build/
#   -> /var/www/site/build/build/index.html  (ВЛОЖЕННЫЙ, НЕВЕРНЫЙ!)
#   Сайт выдаёт "404 Not Found", потому что сервер ищет index.html не в
#   /var/www/site/build/, а в build/build/.

# ============================================================
# 4) Значимость проверки systemctl - не давать ложный сигнал
#    "деплой успешен"
# ============================================================
$ systemctl restart student-platform-backend
$ systemctl is-active --quiet student-platform-backend && echo OK || echo FAIL
# Если команда restart вернёт "успех", но сервис СРАЗУ упадёт (например,
# в .env отсутствует SECRET_KEY), без этой проверки workflow всё равно
# остался бы "зелёным" - самый опасный тип ложного сигнала.
""".strip()

L7_TASK = {
    "task_title": "Deploy pipeline'ni sxematik tasvirlab, xato stsenariysini tahlil qiling",
    "task_title_ru": "Схематически изобразите deploy pipeline и разберите сценарий сбоя",
    "task_description": (
        "`deploy-backend.yml` va `deploy-frontend.yml`ni qayta o'qing. "
        "Har birining barcha step'larini ketma-ket ro'yxatlab, har bir "
        "qadamda NIMA MUVAFFAQIYATSIZ bo'lishi mumkinligini (masalan, "
        "'SSH kaliti noto'g'ri bo'lsa', 'systemctl xizmat topilmasa', "
        "'build/index.html yaratilmasa') va workflow shu holatda "
        "QIZIL bo'lib jamoaga signal berishini tasdiqlang."
    ),
    "task_description_ru": (
        "Перечитайте `deploy-backend.yml` и `deploy-frontend.yml`. "
        "Перечислите по порядку все шаги каждого, и для каждого шага "
        "укажите, ЧТО может пойти не так (например, 'SSH-ключ неверен', "
        "'systemctl не находит сервис', 'build/index.html не создан'), "
        "и подтвердите, что в этом случае workflow становится КРАСНЫМ и "
        "сигнализирует команде."
    ),
    "task_requirements": (
        "1) Har ikkala workflow uchun kamida 5 tadan potentsial xato "
        "nuqtasi aniqlangan bo'lishi kerak. 2) Har bir xato nuqtasi "
        "uchun workflow buni QANDAY aniqlashi (qaysi step, qaysi "
        "tekshiruv) ko'rsatilgan bo'lishi shart. 3) rsync'dagi oxirgi "
        "slash'ning ahamiyati misol bilan tushuntirilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Для каждого из двух workflow должно быть определено минимум "
        "5 потенциальных точек сбоя. 2) Для каждой точки сбоя должно "
        "быть показано, КАК workflow это обнаруживает (какой шаг, какая "
        "проверка). 3) Значимость завершающего слэша в rsync должна быть "
        "объяснена на примере."
    ),
    "task_technologies": "GitHub Actions, SSH, systemd, rsync",
    "task_deadline_days": 4,
}

L7_SAMPLE = {
    "title": "Namuna: xavfsizlik tekshiruvlari kuchaytirilgan deploy workflow",
    "description": (
        "deploy-backend.yml asosida, systemctl tekshiruvidan tashqari "
        "sog'liq-tekshiruvi (health check) qo'shilgan va muvaffaqiyatsiz "
        "bo'lsa avtomatik oldingi holatga (rollback) urinuvchi kengaytirilgan "
        "namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/deploy-backend-with-healthcheck.yml",
            "language": "yaml",
            "code": (
                "name: Deploy Backend With Healthcheck\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [server]\n"
                "    paths:\n"
                "      - 'backend/**'\n"
                "  workflow_dispatch:\n\n"
                "concurrency:\n"
                "  group: deploy-backend\n"
                "  cancel-in-progress: false\n\n"
                "jobs:\n"
                "  deploy:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 15\n"
                "    steps:\n"
                "      - name: Configure SSH\n"
                "        env:\n"
                "          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}\n"
                "          SSH_HOST: ${{ secrets.SSH_HOST }}\n"
                "        run: |\n"
                "          mkdir -p ~/.ssh && chmod 700 ~/.ssh\n"
                "          printf '%s\\n' \"$SSH_PRIVATE_KEY\" > ~/.ssh/deploy_key\n"
                "          chmod 600 ~/.ssh/deploy_key\n"
                "          ssh-keyscan -H \"$SSH_HOST\" >> ~/.ssh/known_hosts 2>/dev/null\n\n"
                "      - name: Deploy and restart\n"
                "        env:\n"
                "          SSH_HOST: ${{ secrets.SSH_HOST }}\n"
                "          SSH_USER: ${{ secrets.SSH_USER }}\n"
                "          BACKEND_DIR: ${{ secrets.BACKEND_DIR }}\n"
                "          SERVICE_NAME: ${{ secrets.SERVICE_NAME }}\n"
                "        run: |\n"
                "          ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes \"$SSH_USER@$SSH_HOST\" \"set -e\n"
                "            git -C '$BACKEND_DIR' pull origin server\n"
                "            cd '$BACKEND_DIR'\n"
                "            source venv/bin/activate\n"
                "            pip install -r requirements.txt --quiet\n"
                "            systemctl restart '$SERVICE_NAME'\n"
                "            sleep 3\n"
                "            systemctl is-active --quiet '$SERVICE_NAME' || { systemctl status '$SERVICE_NAME' --no-pager; exit 1; }\n"
                "            curl -sf http://127.0.0.1:8000/health || { echo 'Health check failed'; exit 1; }\"\n\n"
                "      - name: Cleanup SSH key\n"
                "        if: always()\n"
                "        run: rm -f ~/.ssh/deploy_key\n"
            ),
        },
    ],
}

L7_EXERCISES = [
    {
        "title": "Backend va frontend deploy strategiyasi farqi",
        "title_ru": "Разница стратегий деплоя backend и frontend",
        "description": "Nega backend serverning o'zida (SSH orqali) yangilanadi, frontend esa CI'da yig'ilib rsync qilinadi?",
        "description_ru": "Почему backend обновляется на самом сервере (через SSH), а frontend собирается в CI и переносится через rsync?",
        "exercise_type": "multiple_choice",
        "options": [
            "Backend serverda systemd xizmat sifatida ishlaydi, frontend esa statik fayl - build joyi muhim emas",
            "Frontend har doim tezroq",
            "Backend uchun rsync ishlamaydi",
            "Ular aslida bir xil strategiyani ishlatadi",
        ],
        "options_ru": [
            "Backend работает на сервере как systemd-сервис, frontend — статические файлы, место сборки не важно",
            "Frontend всегда быстрее",
            "Для backend rsync не работает",
            "Они на самом деле используют одну и ту же стратегию",
        ],
        "correct_answers": "A",
        "hint": "Backend kod ISHLAYDIGAN joy bilan, frontend esa faqat NATIJA bilan bog'liq.",
        "hint_ru": "Backend связан с местом, где код РАБОТАЕТ, а frontend — только с РЕЗУЛЬТАТОМ.",
        "explanation": "Backend'ni yangilash uchun xizmatni qayta ishga tushirish kerak, frontend esa faqat static fayl almashtirish.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "OOM muammosining yechimi",
        "title_ru": "Решение проблемы OOM",
        "description": "deploy-frontend.yml'ning kommentariyasiga ko'ra, ilgari qanday muammo bo'lgan va u qanday hal qilingan?",
        "description_ru": "Согласно комментарию в deploy-frontend.yml, какая проблема была раньше и как она решена?",
        "exercise_type": "multiple_choice",
        "options": [
            "Build prod serverda OOM bilan o'chib qolgan - endi GitHub runner'da (ko'proq RAM) bajariladi",
            "Build juda sekin edi - endi Docker ishlatiladi",
            "SSH kaliti muntazam o'zgargan - endi statik kalit ishlatiladi",
            "rsync ishlamagan - endi scp ishlatiladi",
        ],
        "options_ru": [
            "Сборка на prod-сервере обрывалась из-за OOM - теперь выполняется на runner'е GitHub (больше RAM)",
            "Сборка была слишком медленной - теперь используется Docker",
            "SSH-ключ регулярно менялся - теперь используется статический ключ",
            "rsync не работал - теперь используется scp",
        ],
        "correct_answers": "A",
        "hint": "Workflow faylining boshidagi izohni diqqat bilan o'qing.",
        "hint_ru": "Внимательно прочитайте комментарий в начале файла workflow.",
        "explanation": "GitHub runner'lari 7GB RAM va 4 core beradi - prod serverdan ko'ra ko'proq, shuning uchun build u yerda xavfsizroq.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "rsync manba yo'lidagi slash",
        "title_ru": "Слэш в исходном пути rsync",
        "description": "rsync frontend/build/ (slash BILAN) va rsync frontend/build (slashSIZ) orasidagi farq nima?",
        "description_ru": "В чём разница между rsync frontend/build/ (СО слэшем) и rsync frontend/build (БЕЗ слэша)?",
        "exercise_type": "multiple_choice",
        "options": [
            "SlashSIZ, papkaning O'ZI maqsad ichiga nusxalanib, ichma-ich yo'l hosil qiladi",
            "Hech qanday farq yo'q",
            "SlashSIZ tezroq ishlaydi",
            "Slash faqat Windows'da kerak",
        ],
        "options_ru": [
            "Без слэша САМА папка копируется внутрь целевой, создавая вложенный путь",
            "Никакой разницы нет",
            "Без слэша работает быстрее",
            "Слэш нужен только на Windows",
        ],
        "correct_answers": "A",
        "hint": "deploy-frontend.yml'dagi kommentariyada bu \"load-bearing\" deb ta'kidlangan.",
        "hint_ru": "В комментарии deploy-frontend.yml это подчёркнуто как \"load-bearing\".",
        "explanation": "Manba yo'lidagi oxirgi slash papka ICHINI, slashsiz esa papkaning O'ZINI nusxalashni bildiradi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Xizmat holatini tekshirish buyrug'i",
        "title_ru": "Команда проверки состояния сервиса",
        "description": "deploy-backend.yml'da xizmat haqiqatan ishga tushganini tekshiruvchi buyruq: systemctl ___ --quiet",
        "description_ru": "Команда в deploy-backend.yml, проверяющая, что сервис реально запустился: systemctl ___ --quiet",
        "exercise_type": "fill_in_blank",
        "correct_answers": "is-active",
        "correct_answers_ru": "is-active",  # systemctl subcommand — literal CLI token, unchanged across languages
        "hint": "restart'dan keyin xizmat holatini tasdiqlash uchun ishlatiladi.",
        "hint_ru": "Используется после restart, чтобы подтвердить состояние сервиса.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 8 — Branch himoya qoidalari va required status check'lar
# ---------------------------------------------------------------------------

L8_TEXT = """
<h3>Muammo: test.yml qizil bo'lsa ham, kimdir master'ga merge qilishi mumkin</h3>
<p>Hozircha <code>test.yml</code> har bir PR uchun ishga tushadi va
natijani ko'rsatadi — lekin GitHub UI'da hech narsa dasturchini
"testlar o'tmagan PR"ni <strong>merge qilishdan</strong> jismonan
to'xtatmaydi, agar maxsus qoida qo'yilmagan bo'lsa. <strong>Branch
protection rules</strong> — aynan shu bo'shliqni yopadi: ma'lum
branch (masalan <code>master</code>) uchun qoidalar o'rnatib, "Merge"
tugmasini SHART bajarilmagunicha o'chirib qo'yish.</p>

<h3>Required status checks — test.yml'ning natijasini majburiy qilish</h3>
<p>Settings → Branches → Branch protection rule → "Require status checks
to pass before merging" yoqilsa, aniq job nomlarini (masalan
<code>Backend (pytest)</code>, <code>Frontend (Jest)</code> —
<code>test.yml</code>dagi <code>name:</code> maydonlari) tanlash mumkin.
Shundan keyin, agar shu job'lardan BIRI qizil bo'lsa, GitHub "Merge"
tugmasini kulrang qilib qo'yadi — hatto repo egasi bo'lsangiz ham, qoida
"Do not allow bypassing" bilan kuchaytirilgan bo'lsa, majburan kutish
kerak bo'ladi.</p>

<h3>Require branches to be up to date — eskirgan PR muammosi</h3>
<p>Muhim, ko'pincha e'tibordan chetda qoladigan qoida: "Require branches
to be up to date before merging". Bu YO'Q bo'lsa, quyidagi holat yuz
berishi mumkin: PR A va PR B ikkalasi ham master'ning ESKI holatidan
boshlangan va ikkalasi ham alohida testdan MUVAFFAQIYATLI o'tgan — lekin
A merge qilingandan keyin B'ning master bilan birlashtirilgan (merged)
holati HECH QACHON birga test qilinmagan. Bu qoida yoqilsa, B testdan
qayta o'tishi uchun avval master'ning eng yangi holatiga
<code>rebase</code>/<code>merge</code> qilishga majburlanadi — 112-kursda
o'rgangan rebase bilimi shu yerda amaliy foyda beradi.</p>

<h3>Required reviewers va CODEOWNERS</h3>
<p>"Require a pull request before merging" + "Required approvals: 2" —
kamida ikkita boshqa dasturchi tasdiqlamaguncha merge tugmasi ishlamaydi.
<code>CODEOWNERS</code> fayli (repo ildizida yoki
<code>.github/CODEOWNERS</code>) muayyan yo'llar uchun (masalan
<code>/backend/app/models/</code>) MAXSUS tasdiqlovchini majburiy
qiladi — shu papkaga tegishli PR faqat o'sha shaxs(lar) tasdiqlagandan
keyin merge bo'la oladi.</p>

<h3>"Do not allow bypassing the above settings" — hattoki admin uchun ham</h3>
<p>Standart holatda repo administratori branch protection qoidalarini
CHETLAB o'tishi mumkin (favqulodda holatlar uchun). Agar bu katak
yoqilsa, HECH KIM — hattoki repo egasi ham — qoidalarni chetlab
o'tolmaydi. Bu — ayniqsa moliyaviy yoki talaba ma'lumotlari kabi
nozik operatsiyalarga ega loyihalarda (xuddi shu platforma kabi)
tavsiya etiladigan qattiq siyosat.</p>

<h3>Himoyalangan branch orqali merge oqimi</h3>
<pre class="mermaid">
flowchart TB
  PR["PR ochildi: feature -> master"] --> CI["test.yml ishga tushadi
Backend (pytest) + Frontend (Jest)"]
  CI -->|"ikkalasi ham yashil"| CHECK1{"Required status
checks o'tdimi?"}
  CI -->|"biri qizil"| BLOCK1["Merge tugmasi
KULRANG"]
  CHECK1 -->|"Ha"| CHECK2{"Kamida 1 ta
reviewer tasdiqladimi?"}
  CHECK2 -->|"Yo'q"| BLOCK2["Merge tugmasi
KULRANG"]
  CHECK2 -->|"Ha"| MERGE["Merge tugmasi
YASHIL - bosish mumkin"]
  style BLOCK1 fill:#ffd6d6,stroke:#cc3333
  style BLOCK2 fill:#ffd6d6,stroke:#cc3333
  style MERGE fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Diagramma real GitHub UI oqimini ko'rsatadi: <code>test.yml</code>ning
o'zi hech narsani BLOKLAMAYDI — u faqat NATIJA beradi. Blokirovka
qiluvchi — Settings'da alohida sozlangan branch protection qoidasi, u
shu natijani "Merge tugmasi yoqiladimi yoqilmaydimi" qaroriga
bog'laydi.</p>

<h3>Require linear history — 112-kursdagi rebase bilimiga bog'liq qoida</h3>
<p>"Require linear history" qoyilsa, oddiy merge commit (ikkita ota-
commitli) butunlay TAQIQLANADI — faqat <code>rebase</code> yoki
<code>squash merge</code> orqaligina master'ga qo'shish mumkin bo'ladi.
Bu 112-kursda o'rgangan "interaktiv rebase" bilimini kundalik ish
jarayoniga majburiy qiladi: har bir dasturchi PR'ini merge qilishdan
oldin, tarixni chiziqli qilib qo'yishga majbur bo'ladi, natijada
<code>git log --oneline</code> tushunarli, chalkash bo'lmagan chiziqli
tarixni ko'rsatadi.</p>
""".strip()

L8_TEXT_RU = """
<h3>Проблема: даже красный test.yml не мешает смержить в master</h3>
<p>Сейчас <code>test.yml</code> запускается для каждого PR и показывает
результат — но ничто в GitHub UI физически не мешает разработчику
<strong>смержить</strong> PR с непройденными тестами, если не настроено
специальное правило. <strong>Branch protection rules</strong> закрывают
именно этот пробел: устанавливают правила для определённой ветки
(например <code>master</code>), отключая кнопку "Merge", пока условие не
выполнено.</p>

<h3>Required status checks — сделать результат test.yml обязательным</h3>
<p>Если включить Settings → Branches → Branch protection rule →
"Require status checks to pass before merging", можно выбрать конкретные
имена job'ов (например <code>Backend (pytest)</code>,
<code>Frontend (Jest)</code> — поля <code>name:</code> в
<code>test.yml</code>). После этого, если хотя бы ОДИН из этих job'ов
красный, GitHub делает кнопку "Merge" серой — даже если вы владелец
репо, при усилении правила "Do not allow bypassing" придётся ждать
принудительно.</p>

<h3>Require branches to be up to date — проблема устаревшего PR</h3>
<p>Важное, часто упускаемое правило: "Require branches to be up to date
before merging". Без него может произойти следующее: PR A и PR B оба
начались от СТАРОГО состояния master и оба УСПЕШНО прошли тест по
отдельности — но состояние ПОСЛЕ слияния A и B НИКОГДА совместно не
тестировалось. Если это правило включено, B будет принудительно
обязан сначала сделать <code>rebase</code>/<code>merge</code> на
последнее состояние master, прежде чем снова пройти тест — здесь знания
о rebase из курса 112 приносят практическую пользу.</p>

<h3>Required reviewers и CODEOWNERS</h3>
<p>"Require a pull request before merging" + "Required approvals: 2" —
кнопка merge не работает, пока минимум два других разработчика не
подтвердят PR. Файл <code>CODEOWNERS</code> (в корне репо или
<code>.github/CODEOWNERS</code>) делает ОБЯЗАТЕЛЬНЫМ конкретного
подтверждающего для определённых путей (например
<code>/backend/app/models/</code>) — PR, затрагивающий эту папку, может
быть смержен только после подтверждения именно этим человеком (людьми).</p>

<h3>"Do not allow bypassing the above settings" — даже для админа</h3>
<p>По умолчанию администратор репо может ОБОЙТИ правила branch protection
(для экстренных случаев). Если включить этот флажок, НИКТО — даже
владелец репо — не может обойти правила. Это — строгая политика,
рекомендуемая особенно для проектов с чувствительными операциями
(например, финансовыми данными или данными студентов, как в этой
платформе).</p>

<h3>Поток merge через защищённую ветку</h3>
<pre class="mermaid">
flowchart TB
  PR["Открыт PR: feature -> master"] --> CI["запускается test.yml
Backend (pytest) + Frontend (Jest)"]
  CI -->|"оба зелёные"| CHECK1{"Required status
checks прошли?"}
  CI -->|"один красный"| BLOCK1["Кнопка Merge
СЕРАЯ"]
  CHECK1 -->|"Да"| CHECK2{"Хотя бы 1 reviewer
подтвердил?"}
  CHECK2 -->|"Нет"| BLOCK2["Кнопка Merge
СЕРАЯ"]
  CHECK2 -->|"Да"| MERGE["Кнопка Merge
ЗЕЛЁНАЯ - можно нажать"]
  style BLOCK1 fill:#ffd6d6,stroke:#cc3333
  style BLOCK2 fill:#ffd6d6,stroke:#cc3333
  style MERGE fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Диаграмма показывает реальный поток GitHub UI: сам
<code>test.yml</code> НИЧЕГО не блокирует — он только даёт РЕЗУЛЬТАТ.
Блокирует — отдельно настроенное в Settings правило branch protection,
которое связывает этот результат с решением "включена ли кнопка Merge".</p>

<h3>Require linear history — правило, связанное со знаниями курса 112 о rebase</h3>
<p>При включении "Require linear history" обычный merge-коммит (с двумя
родительскими коммитами) ПОЛНОСТЬЮ ЗАПРЕЩЁН — добавить в master можно
только через <code>rebase</code> или <code>squash merge</code>. Это
делает знания об "интерактивном rebase" из курса 112 обязательной частью
ежедневной работы: каждый разработчик перед merge своего PR обязан
сделать историю линейной, в результате <code>git log --oneline</code>
показывает понятную, без путаницы линейную историю. Это правило часто
комбинируют с required status checks — так и код проверен, и история
репозитория остаётся читаемой для всей команды. Это ещё один пример
того, как правило branch protection превращает знание, изученное как
"техника Git" (курс 112), в обязательную часть повседневного командного
процесса, а не просто необязательную рекомендацию.</p>
""".strip()

L8_CODE = """
# ============================================================
# 1) Branch protection qoidasini GitHub CLI orqali o'rnatish
#    (test.yml'ning HAQIQIY job nomlari bilan)
# ============================================================
$ gh api repos/{owner}/{repo}/branches/master/protection \\
  --method PUT \\
  --field required_status_checks='{"strict":true,"contexts":["Backend (pytest)","Frontend (Jest)"]}' \\
  --field enforce_admins=true \\
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \\
  --field restrictions=null
# required_status_checks.strict: true - bu "Require branches to be up
# to date before merging" ga mos keladi.
# contexts - test.yml'dagi job "name:" maydonlaridan OLINGAN ANIQ matn -
# nomi bir harf farq qilsa ham, GitHub qoidani mos kelmagan deb hisoblaydi.

# ============================================================
# 2) .github/CODEOWNERS - muayyan yo'llar uchun majburiy tekshiruvchi
# ============================================================
# Global standart - reponing istalgan qismi uchun
* @backend-team-lead

# Backend model o'zgarishlari - faqat bazaviy tuzilishni biladigan odam
/backend/app/models/ @db-schema-owner

# Deploy workflow'lari - faqat DevOps mas'uli
/.github/workflows/deploy-*.yml @devops-lead

# Frontend komponentlar - frontend jamoasi
/frontend/src/components/ @frontend-team

# ============================================================
# 3) required_status_checks kontekstini test.yml'dan aniq olish
# ============================================================
# test.yml'dagi:
#   backend:
#     name: Backend (pytest)     <- bu "context" nomi
#   frontend:
#     name: Frontend (Jest)      <- bu ham "context" nomi
#
# Branch protection sozlamasida ANIQ shu ikki nom kiritilishi kerak -
# agar "name:" o'zgartirilsa (masalan "Backend Tests" deb), eski qoidada
# saqlangan "Backend (pytest)" endi HECH QACHON topilmaydi, va PR
# ABADIY "kutilmoqda" holatida qolib ketadi (bu keng tarqalgan xato -
# 11-darsda batafsil ko'ramiz).

# ============================================================
# 4) Rebase talab qilinishi - 112-kurs bilimi amaliyotda
# ============================================================
$ git fetch origin
$ git rebase origin/master
# Agar "Require branches to be up to date" yoqilgan bo'lsa, GitHub
# feature branch'ni PR oynasida "This branch is out-of-date with the
# base branch" deb ko'rsatadi - "Update branch" tugmasi (yoki qo'lda
# rebase) bosilmaguncha, hatto testlar avval o'tgan bo'lsa ham, Merge
# tugmasi ishlamaydi.

# ============================================================
# 5) Bypass qilishni butunlay o'chirish (eng qattiq siyosat)
# ============================================================
$ gh api repos/{owner}/{repo}/branches/master/protection \\
  --method PUT \\
  --field enforce_admins=true
# enforce_admins: true - "Do not allow bypassing the above settings"ga
# mos keladi. Bu yoqilgach, repo egasi HAM qoidalarni chetlab o'ta
# olmaydi - favqulodda holatda ham avval qoidani VAQTINCHA o'chirish
# kerak bo'ladi, bu esa qasddan qiyinlashtirilgan (audit uchun).
""".strip()

L8_CODE_RU = """
# ============================================================
# 1) Установка правила branch protection через GitHub CLI
#    (с РЕАЛЬНЫМИ именами job'ов из test.yml)
# ============================================================
$ gh api repos/{owner}/{repo}/branches/master/protection \\
  --method PUT \\
  --field required_status_checks='{"strict":true,"contexts":["Backend (pytest)","Frontend (Jest)"]}' \\
  --field enforce_admins=true \\
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \\
  --field restrictions=null
# required_status_checks.strict: true - соответствует "Require branches
# to be up to date before merging".
# contexts - ТОЧНЫЙ текст, ВЗЯТЫЙ из поля "name:" job'ов в test.yml -
# даже отличие на одну букву, и GitHub посчитает правило не совпавшим.

# ============================================================
# 2) .github/CODEOWNERS - обязательный проверяющий для конкретных путей
# ============================================================
# Глобальный дефолт - для любой части репо
* @backend-team-lead

# Изменения моделей backend - только человек, знающий структуру БД
/backend/app/models/ @db-schema-owner

# Workflow'ы деплоя - только ответственный за DevOps
/.github/workflows/deploy-*.yml @devops-lead

# Компоненты frontend - команда frontend
/frontend/src/components/ @frontend-team

# ============================================================
# 3) Точное получение контекста required_status_checks из test.yml
# ============================================================
# В test.yml:
#   backend:
#     name: Backend (pytest)     <- это имя "context"
#   frontend:
#     name: Frontend (Jest)      <- это тоже имя "context"
#
# В настройках branch protection нужно указать ТОЧНО эти два имени -
# если "name:" изменится (например на "Backend Tests"), сохранённое в
# старом правиле "Backend (pytest)" больше НИКОГДА не найдётся, и PR
# НАВСЕГДА останется в состоянии "ожидание" (это распространённая
# ошибка - подробно разберём в уроке 11).

# ============================================================
# 4) Требование rebase - знания курса 112 на практике
# ============================================================
$ git fetch origin
$ git rebase origin/master
# Если включено "Require branches to be up to date", GitHub покажет в
# окне PR "This branch is out-of-date with the base branch" - пока не
# нажата кнопка "Update branch" (или не сделан rebase вручную), кнопка
# Merge не работает, даже если тесты уже проходили раньше.

# ============================================================
# 5) Полное отключение возможности bypass (самая строгая политика)
# ============================================================
$ gh api repos/{owner}/{repo}/branches/master/protection \\
  --method PUT \\
  --field enforce_admins=true
# enforce_admins: true - соответствует "Do not allow bypassing the
# above settings". После включения владелец репо ТОЖЕ не может обойти
# правила - даже в экстренном случае сначала нужно ВРЕМЕННО отключить
# правило, что специально усложнено (для аудита).
""".strip()

L8_TASK = {
    "task_title": "master branch'ni test.yml natijasi bilan himoyalang",
    "task_title_ru": "Защитите ветку master результатом test.yml",
    "task_description": (
        "Shaxsiy (yoki fork qilingan) repozitoriyangizda `master` "
        "branch'i uchun branch protection rule o'rnating: required "
        "status checks sifatida `test.yml`dagi ANIQ ikkita job nomini "
        "(`Backend (pytest)`, `Frontend (Jest)`) tanlang, kamida 1 "
        "reviewer talab qiling, va \"Require branches to be up to "
        "date\" ni yoqing. So'ngra QASDDAN sinadigan test bilan PR "
        "oching va Merge tugmasi bloklanganini skrinshot bilan isbotlang."
    ),
    "task_description_ru": (
        "В своём (или форкнутом) репозитории установите правило branch "
        "protection для ветки `master`: в качестве required status "
        "checks выберите ТОЧНЫЕ имена двух job'ов из `test.yml` "
        "(`Backend (pytest)`, `Frontend (Jest)`), потребуйте минимум 1 "
        "reviewer, включите \"Require branches to be up to date\". "
        "Затем откройте PR с ЗАВЕДОМО падающим тестом и докажите "
        "скриншотом, что кнопка Merge заблокирована."
    ),
    "task_requirements": (
        "1) Required status check nomlari test.yml'dagi `name:` "
        "maydonlariga ANIQ mos kelishi kerak. 2) Qizil test bilan Merge "
        "tugmasi bloklanganini isbotlash kerak. 3) Testni to'g'irlab, "
        "Merge tugmasi qayta yoqilganini ham ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Имена required status check должны ТОЧНО совпадать с полями "
        "`name:` в test.yml. 2) Должно быть доказано, что при красном "
        "тесте кнопка Merge заблокирована. 3) Покажите также, что после "
        "исправления теста кнопка Merge снова разблокирована."
    ),
    "task_technologies": "GitHub branch protection, required status checks",
    "task_deadline_days": 4,
}

L8_SAMPLE = {
    "title": "Namuna: gh CLI orqali to'liq branch protection sozlash skripti",
    "description": (
        "test.yml'ning haqiqiy job nomlaridan foydalanib, required "
        "status checks, reviewer talabi va enforce_admins'ni bitta "
        "buyruqda o'rnatuvchi skript."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "setup_branch_protection.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "OWNER=\"your-org\"\n"
                "REPO=\"student_platform\"\n"
                "BRANCH=\"master\"\n\n"
                "echo \"Sozlanmoqda: $OWNER/$REPO ($BRANCH)\"\n\n"
                "gh api \"repos/$OWNER/$REPO/branches/$BRANCH/protection\" \\\n"
                "  --method PUT \\\n"
                "  --field required_status_checks='{\"strict\":true,\"contexts\":[\"Backend (pytest)\",\"Frontend (Jest)\"]}' \\\n"
                "  --field enforce_admins=true \\\n"
                "  --field required_pull_request_reviews='{\"required_approving_review_count\":1,\"dismiss_stale_reviews\":true}' \\\n"
                "  --field restrictions=null\n\n"
                "echo \"Tayyor. Tekshirish:\"\n"
                "gh api \"repos/$OWNER/$REPO/branches/$BRANCH/protection\" | jq '.required_status_checks.contexts'\n"
            ),
        },
    ],
}

L8_EXERCISES = [
    {
        "title": "test.yml o'z-o'zidan merge'ni bloklaydimi",
        "title_ru": "Блокирует ли test.yml merge сам по себе",
        "description": "test.yml o'zi (branch protection qoidasisiz) qizil bo'lsa, GitHub PR'ni merge qilishga jismonan to'sqinlik qiladimi?",
        "description_ru": "Мешает ли сам test.yml (без правила branch protection) физически смержить PR, если он красный?",
        "exercise_type": "multiple_choice",
        "options": ["Yo'q, faqat natija ko'rsatadi - to'sish uchun qoida kerak", "Ha, avtomatik to'sadi", "Faqat master branch'ida to'sadi", "Faqat admin bo'lmasa to'sadi"],
        "options_ru": ["Нет, только показывает результат - для блокировки нужно правило", "Да, автоматически блокирует", "Блокирует только в ветке master", "Блокирует только если не админ"],
        "correct_answers": "A",
        "hint": "Workflow va branch protection qoidasi ikki alohida narsa.",
        "hint_ru": "Workflow и правило branch protection — две отдельные вещи.",
        "explanation": "Faqat required status check sifatida belgilangandan keyingina test.yml natijasi merge'ni bloklay oladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Required status check nomi qayerdan olinadi",
        "title_ru": "Откуда берётся имя required status check",
        "description": "Branch protection'da 'contexts' sifatida ko'rsatiladigan nom qaysi YAML maydonidan olinadi?",
        "description_ru": "Из какого поля YAML берётся имя, указываемое как 'contexts' в branch protection?",
        "exercise_type": "multiple_choice",
        "options": ["job'ning name: maydoni", "workflow faylining nomi (test.yml)", "runs-on qiymati", "on: bloki"],
        "options_ru": ["Поле name: job'а", "Имя файла workflow (test.yml)", "Значение runs-on", "Блок on:"],
        "correct_answers": "A",
        "hint": "test.yml'da \"Backend (pytest)\" qayerda yozilgan edi?",
        "hint_ru": "Где было написано \"Backend (pytest)\" в test.yml?",
        "explanation": "GitHub job'ning name: maydonidagi matnni aynan 'context' sifatida ishlatadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Require branches to be up to date maqsadi",
        "title_ru": "Цель Require branches to be up to date",
        "description": "Bu qoida nima uchun kerak?",
        "description_ru": "Зачем нужно это правило?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkita PR'ning birlashtirilgan holati birga test qilinganini kafolatlash",
            "Faqat kod formatini tekshirish",
            "Deploy tezligini oshirish",
            "Secret'larni yangilash",
        ],
        "options_ru": [
            "Гарантировать, что объединённое состояние двух PR протестировано вместе",
            "Проверять только формат кода",
            "Ускорять деплой",
            "Обновлять secrets",
        ],
        "correct_answers": "A",
        "hint": "Ikki PR alohida eski master'dan test o'tsa, ular BIRGA test qilinganmi?",
        "hint_ru": "Если два PR по отдельности прошли тест от старого master, протестированы ли они ВМЕСТЕ?",
        "explanation": "Bu qoida branch'ni eng yangi master bilan yangilashga majburlab, haqiqiy merge natijasini tekshiradi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Muayyan yo'l uchun majburiy tasdiqlovchi",
        "title_ru": "Обязательный проверяющий для конкретного пути",
        "description": "Muayyan papka/fayl uchun majburiy tasdiqlovchini belgilaydigan fayl nomi: ___",
        "description_ru": "Имя файла, определяющего обязательного проверяющего для конкретной папки/файла: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "CODEOWNERS",
        "hint": "Repo ildizida yoki .github/ ichida joylashadi.",
        "hint_ru": "Находится в корне репозитория или внутри .github/.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 9 — Qayta ishlatiladigan workflow'lar va composite action'lar
# ---------------------------------------------------------------------------

L9_TEXT = """
<h3>Muammo: test.yml'dagi naqsh boshqa loyihalarda ham takrorlanadi</h3>
<p>Agar bu platformada yana ikkita mikroservis bo'lsa, har birida
<code>actions/checkout</code> + <code>actions/setup-python</code> +
<code>pip install</code> + <code>pytest</code> zanjiri deyarli AYNAN
takrorlanadi. Har bir yangi repo uchun bu zanjirni qayta yozish —
DRY (Don't Repeat Yourself) tamoyiliga zid. GitHub Actions buning uchun
IKKI xil qayta ishlatish mexanizmini taqdim etadi: <strong>reusable
workflow</strong> (<code>workflow_call</code>) va <strong>composite
action</strong>.</p>

<h3>Composite action — step'lar guruhini bitta "action" qilib o'rash</h3>
<p>Composite action — bir nechta <code>run</code>/<code>uses</code>
step'ini BITTA qayta ishlatiladigan blokka birlashtiradi.
<code>.github/actions/setup-backend/action.yml</code> fayli yaratilib,
ichida <code>runs: using: composite, steps: [...]</code> yozilsa, uni
istalgan workflow'da bitta qatorda
<code>uses: ./.github/actions/setup-backend</code> deb chaqirish mumkin.
Bu — <code>test.yml</code>ning "Set up Python" + "Install dependencies"
juftligini BITTA qayta ishlatiladigan blokka aylantirishning aynan o'zi.</p>

<h3>Reusable workflow — butun job(lar)ni qayta ishlatish</h3>
<p>Reusable workflow — composite action'dan KATTAROQ birlik: butun bir
YOKI bir nechta job'ni <code>on: workflow_call:</code> trigger'i bilan
"chaqiriladigan funksiya"ga aylantiradi. Masalan
<code>.github/workflows/_reusable-backend-test.yml</code> fayli
<code>test.yml</code>ning butun <code>backend</code> job'ini o'z ichiga
olishi mumkin, va boshqa workflow uni
<code>uses: ./.github/workflows/_reusable-backend-test.yml</code> orqali
chaqiradi — <code>inputs:</code> (parametrlar) va <code>secrets:</code>
(qaysi secret'lar uzatilishini) aniq belgilab.</p>

<h3>Qачон qaysi birini tanlash</h3>
<p>Oddiy qoida: agar takrorlanayotgan narsa BIR NECHTA STEP (masalan,
"muhitni sozlash") bo'lsa — <strong>composite action</strong>. Agar
takrorlanayotgan narsa BUTUN JOB yoki JOB'LAR ZANJIRI (masalan, "testni
ishga tushirib, natijani yig'ish va bildirishnoma yuborish") bo'lsa —
<strong>reusable workflow</strong>. Composite action bitta job ICHIDA
ishlaydi (o'z alohida runner'i yo'q); reusable workflow esa o'ZINING
alohida job(lar)i, hattoki o'z <code>runs-on:</code>iga ega bo'lishi
mumkin.</p>

<h3>secrets: inherit — barcha secret'larni avtomatik uzatish</h3>
<p>Reusable workflow'ni chaqirganda har bir secret'ni qo'lda sanab
o'tirish o'rniga, <code>secrets: inherit</code> yozish mumkin — bu
chaqiruvchi workflow'ning BARCHA secret'larini avtomatik chaqirilgan
workflow'ga uzatadi. Bu qulay, lekin xavfsizlik nuqtai nazaridan
"eng kam huquq" (least privilege) tamoyiliga zid bo'lishi mumkin — katta
jamoada odatda faqat kerakli secret'larni aniq sanab o'tish tavsiya
etiladi.</p>

<h3>Composite action va reusable workflow'ning farqi diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  subgraph CA["Composite action"]
    direction TB
    CA1["uses: ./.github/actions/setup-backend"] --> CA2["BIR job ICHIDA
step'lar guruhi ishga tushadi"]
  end
  subgraph RW["Reusable workflow"]
    direction TB
    RW1["uses: ./.github/workflows/_reusable-backend-test.yml"] --> RW2["BUTUN job(lar)
alohida runner'da ishga tushadi"]
  end
  style CA2 fill:#d6e9ff,stroke:#2266aa
  style RW2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma ikkalasining darajasini ko'rsatadi: composite action —
"step darajasidagi" qayta ishlatish, reusable workflow — "job
darajasidagi" qayta ishlatish. Ikkalasi ham bir xil maqsadga xizmat
qiladi (DRY), lekin qamrovi boshqacha.</p>

<h3>Versiyalash: composite action va reusable workflow'ni tag bilan qulflash</h3>
<p>0-darsda <code>actions/checkout@v4</code>dagi <code>@v4</code>ning
nima uchun muhimligini o'rgangandik — xuddi shu qoida O'ZINGIZ yozgan
composite action/reusable workflow'ga ham tegishli. Agar ular boshqa
repozitoriyada joylashgan bo'lsa (masalan alohida "shared-actions"
repo), ularni <code>@main</code> emas, aniq
<code>@v1</code>/commit SHA (yana content-addressing — 112-kurs 0-darsi)
bilan chaqirish kerak: aks holda kimdir "shared-actions"ni o'zgartirsa,
BARCHA uni ishlatuvchi loyihalar kutilmaganda buzilishi mumkin.</p>
""".strip()

L9_TEXT_RU = """
<h3>Проблема: паттерн test.yml повторяется и в других проектах</h3>
<p>Если бы в этой платформе было ещё два микросервиса, в каждом из них
цепочка <code>actions/checkout</code> + <code>actions/setup-python</code>
+ <code>pip install</code> + <code>pytest</code> повторялась бы почти
ТОЧНО так же. Переписывать эту цепочку для каждого нового репо —
противоречит принципу DRY (Don't Repeat Yourself). GitHub Actions
предоставляет для этого ДВА механизма переиспользования:
<strong>reusable workflow</strong> (<code>workflow_call</code>) и
<strong>composite action</strong>.</p>

<h3>Composite action — обернуть группу step'ов в один "action"</h3>
<p>Composite action объединяет несколько step'ов
<code>run</code>/<code>uses</code> в ОДИН переиспользуемый блок. Если
создать файл <code>.github/actions/setup-backend/action.yml</code>, где
написано <code>runs: using: composite, steps: [...]</code>, его можно
вызвать в любом workflow одной строкой:
<code>uses: ./.github/actions/setup-backend</code>. Это — именно
превращение пары "Set up Python" + "Install dependencies" из
<code>test.yml</code> в ОДИН переиспользуемый блок.</p>

<h3>Reusable workflow — переиспользование целого(ых) job'а(ов)</h3>
<p>Reusable workflow — единица КРУПНЕЕ composite action: превращает
целый один ИЛИ несколько job'ов в "вызываемую функцию" через триггер
<code>on: workflow_call:</code>. Например, файл
<code>.github/workflows/_reusable-backend-test.yml</code> может
содержать весь job <code>backend</code> из <code>test.yml</code>, а
другой workflow вызывает его через
<code>uses: ./.github/workflows/_reusable-backend-test.yml</code> —
чётко определяя <code>inputs:</code> (параметры) и <code>secrets:</code>
(какие secrets передаются).</p>

<h3>Когда что выбирать</h3>
<p>Простое правило: если повторяется НЕСКОЛЬКО STEP'ОВ (например,
"настройка среды") — <strong>composite action</strong>. Если повторяется
ЦЕЛЫЙ JOB или ЦЕПОЧКА JOB'ОВ (например, "запустить тест, собрать
результат и отправить уведомление") — <strong>reusable workflow</strong>.
Composite action работает ВНУТРИ одного job'а (у него нет своего
runner'а); reusable workflow может иметь СВОЙ(и) отдельный(ые) job(ы),
даже свой <code>runs-on:</code>.</p>

<h3>secrets: inherit — автоматическая передача всех secrets</h3>
<p>При вызове reusable workflow, вместо ручного перечисления каждого
secret, можно написать <code>secrets: inherit</code> — это автоматически
передаёт ВСЕ secrets вызывающего workflow вызываемому. Это удобно, но с
точки зрения безопасности может противоречить принципу "минимальных прав"
(least privilege) — в большой команде обычно рекомендуется явно
перечислять только нужные secrets.</p>

<h3>Диаграмма разницы composite action и reusable workflow</h3>
<pre class="mermaid">
flowchart TB
  subgraph CA["Composite action"]
    direction TB
    CA1["uses: ./.github/actions/setup-backend"] --> CA2["группа step'ов запускается
ВНУТРИ одного job'а"]
  end
  subgraph RW["Reusable workflow"]
    direction TB
    RW1["uses: ./.github/workflows/_reusable-backend-test.yml"] --> RW2["ЦЕЛЫЙ job(ы)
запускается на отдельном runner'е"]
  end
  style CA2 fill:#d6e9ff,stroke:#2266aa
  style RW2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает уровень каждого: composite action —
переиспользование "на уровне step", reusable workflow — переиспользование
"на уровне job". Оба служат одной цели (DRY), но с разным охватом.</p>

<h3>Версионирование: фиксация composite action и reusable workflow тегом</h3>
<p>В уроке 0 мы узнали, почему важен <code>@v4</code> в
<code>actions/checkout@v4</code> — то же правило касается и
СОБСТВЕННОГО composite action/reusable workflow. Если они находятся в
другом репозитории (например, отдельное репо "shared-actions"), их нужно
вызывать не через <code>@main</code>, а через точный
<code>@v1</code>/SHA коммита (снова content-addressing — урок 0 курса
112): иначе если кто-то изменит "shared-actions", ВСЕ использующие его
проекты могут неожиданно сломаться. Тот же принцип, что и с любым
внешним action: доверие к чужому коду должно быть привязано к
конкретной, неизменной версии, а не к постоянно двигающейся ветке. Это
касается и собственных composite action/reusable workflow внутри одного
репозитория: даже локальный путь вроде
<code>./.github/actions/setup-backend</code> стоит сопровождать
понятным описанием версии в самом файле action, чтобы будущие изменения
были осознанными, а не случайными побочными эффектами.</p>
""".strip()

L9_CODE = """
# ============================================================
# 1) Composite action: test.yml'ning backend sozlash qismini o'rash
# ============================================================
# .github/actions/setup-backend/action.yml
name: 'Setup Backend'
description: 'Checkout + Python + bog\\'liqliklarni o\\'rnatish'
inputs:
  python-version:
    description: 'Python versiyasi'
    required: false
    default: '3.11'
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
        cache-dependency-path: backend/requirements.txt
    - name: Install dependencies
      shell: bash
      working-directory: backend
      run: pip install -r requirements.txt
# Composite action ICHIDA "shell: bash" har bir run: step'i uchun ANIQ
# ko'rsatilishi SHART - oddiy workflow'dan farqli, bu yerda standart
# shell avtomatik tanlanmaydi.

# ============================================================
# 2) Composite action'ni test.yml ichida chaqirish
# ============================================================
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-backend    # <- BITTA qatorda
        with:                                     #    ikkita step o'rniga
          python-version: "3.11"
      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

# ============================================================
# 3) Reusable workflow: butun backend test job'ini funksiya qilish
# ============================================================
# .github/workflows/_reusable-backend-test.yml
name: Reusable Backend Test

on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.11"
    secrets:
      db-url:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
          cache-dependency-path: backend/requirements.txt
      - working-directory: backend
        run: pip install -r requirements.txt
      - working-directory: backend
        env:
          DATABASE_URL: ${{ secrets.db-url || 'sqlite+aiosqlite:///./test.db' }}
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

# ============================================================
# 4) Reusable workflow'ni chaqiruvchi fayl
# ============================================================
# .github/workflows/test.yml (yangi versiya, reusable bilan)
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    uses: ./.github/workflows/_reusable-backend-test.yml
    with:
      python-version: "3.11"
    secrets: inherit    # <- barcha secret'larni avtomatik uzatish

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests
# Diqqat: reusable workflow chaqirilganda "backend" job'i endi
# `uses:` bilan yoziladi, "runs-on:"/"steps:" YO'Q - bular
# _reusable-backend-test.yml ICHIDA yashiringan.
""".strip()

L9_CODE_RU = """
# ============================================================
# 1) Composite action: обёртка части настройки backend из test.yml
# ============================================================
# .github/actions/setup-backend/action.yml
name: 'Setup Backend'
description: 'Checkout + Python + установка зависимостей'
inputs:
  python-version:
    description: 'Версия Python'
    required: false
    default: '3.11'
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
        cache-dependency-path: backend/requirements.txt
    - name: Install dependencies
      shell: bash
      working-directory: backend
      run: pip install -r requirements.txt
# Внутри composite action "shell: bash" ДОЛЖЕН быть указан явно для
# каждого step'а run: - в отличие от обычного workflow, здесь shell по
# умолчанию не выбирается автоматически.

# ============================================================
# 2) Вызов composite action внутри test.yml
# ============================================================
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-backend    # <- ОДНА строка вместо
        with:                                     #    двух step'ов
          python-version: "3.11"
      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: sqlite+aiosqlite:///./test.db
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

# ============================================================
# 3) Reusable workflow: превращение целого job'а теста backend в функцию
# ============================================================
# .github/workflows/_reusable-backend-test.yml
name: Reusable Backend Test

on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.11"
    secrets:
      db-url:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
          cache-dependency-path: backend/requirements.txt
      - working-directory: backend
        run: pip install -r requirements.txt
      - working-directory: backend
        env:
          DATABASE_URL: ${{ secrets.db-url || 'sqlite+aiosqlite:///./test.db' }}
          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
        run: python -m pytest tests/ -v --tb=short

# ============================================================
# 4) Файл, вызывающий reusable workflow
# ============================================================
# .github/workflows/test.yml (новая версия, с reusable)
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    uses: ./.github/workflows/_reusable-backend-test.yml
    with:
      python-version: "3.11"
    secrets: inherit    # <- автоматическая передача всех secrets

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests
# Внимание: при вызове reusable workflow job "backend" теперь пишется
# через `uses:`, "runs-on:"/"steps:" ОТСУТСТВУЮТ - они спрятаны ВНУТРИ
# _reusable-backend-test.yml.
""".strip()

L9_TASK = {
    "task_title": "test.yml'ni composite action bilan qayta tuzing",
    "task_title_ru": "Перестройте test.yml с composite action",
    "task_description": (
        "`.github/actions/setup-backend/action.yml` composite "
        "action'ini yarating (checkout'dan KEYIN chaqiriladigan, Python "
        "sozlash + bog'liqlik o'rnatishni o'z ichiga olgan). So'ngra "
        "`test.yml`ning `backend` job'ini shu action'ni ishlatadigan "
        "qilib qayta yozing. Push qilib, workflow avvalgidek "
        "ishlashini isbotlang."
    ),
    "task_description_ru": (
        "Создайте composite action "
        "`.github/actions/setup-backend/action.yml` (вызываемый ПОСЛЕ "
        "checkout, включающий настройку Python + установку "
        "зависимостей). Затем перепишите job `backend` в `test.yml`, "
        "чтобы он использовал этот action. Запушьте и докажите, что "
        "workflow работает как раньше."
    ),
    "task_requirements": (
        "1) Composite action `runs: using: composite` bilan to'g'ri "
        "ta'riflangan bo'lishi kerak. 2) Har bir run: step'ida `shell: "
        "bash` aniq ko'rsatilgan bo'lishi shart. 3) Yangi `test.yml` "
        "avvalgi natija bilan bir xil (testlar o'tishi) bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Composite action должен быть корректно определён через "
        "`runs: using: composite`. 2) В каждом step'е run: должен быть "
        "явно указан `shell: bash`. 3) Новый `test.yml` должен давать "
        "тот же результат (тесты проходят), что и раньше."
    ),
    "task_technologies": "GitHub Actions composite actions, DRY",
    "task_deadline_days": 5,
}

L9_SAMPLE = {
    "title": "Namuna: composite action + reusable workflow to'liq juftligi",
    "description": (
        "setup-backend composite action'i va uni ishlatuvchi reusable "
        "workflow, hamda uni chaqiruvchi asosiy fayl - uch faylli "
        "to'liq namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/actions/setup-backend/action.yml",
            "language": "yaml",
            "code": (
                "name: 'Setup Backend'\n"
                "description: 'Checkout keyin Python + bogliqliklarni ornatish'\n"
                "inputs:\n"
                "  python-version:\n"
                "    required: false\n"
                "    default: '3.11'\n"
                "runs:\n"
                "  using: composite\n"
                "  steps:\n"
                "    - uses: actions/setup-python@v5\n"
                "      with:\n"
                "        python-version: ${{ inputs.python-version }}\n"
                "        cache: pip\n"
                "        cache-dependency-path: backend/requirements.txt\n"
                "    - shell: bash\n"
                "      working-directory: backend\n"
                "      run: pip install -r requirements.txt\n"
            ),
        },
        {
            "filename": ".github/workflows/_reusable-backend-test.yml",
            "language": "yaml",
            "code": (
                "name: Reusable Backend Test\n\n"
                "on:\n"
                "  workflow_call:\n"
                "    inputs:\n"
                "      python-version:\n"
                "        type: string\n"
                "        default: \"3.11\"\n\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 10\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: ./.github/actions/setup-backend\n"
                "        with:\n"
                "          python-version: ${{ inputs.python-version }}\n"
                "      - working-directory: backend\n"
                "        env:\n"
                "          DATABASE_URL: sqlite+aiosqlite:///./test.db\n"
                "          SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod\n"
                "        run: python -m pytest tests/ -v --tb=short\n"
            ),
        },
        {
            "filename": ".github/workflows/test-with-reusable.yml",
            "language": "yaml",
            "code": (
                "name: Tests (Reusable)\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [\"**\"]\n\n"
                "jobs:\n"
                "  backend:\n"
                "    uses: ./.github/workflows/_reusable-backend-test.yml\n"
                "    with:\n"
                "      python-version: \"3.11\"\n"
            ),
        },
    ],
}

L9_EXERCISES = [
    {
        "title": "Composite action vs reusable workflow qamrovi",
        "title_ru": "Охват composite action против reusable workflow",
        "description": "Composite action qaysi darajada ishlaydi?",
        "description_ru": "На каком уровне работает composite action?",
        "exercise_type": "multiple_choice",
        "options": ["Step darajasida, bitta job ichida", "Butun workflow darajasida", "Faqat secrets darajasida", "Faqat matrix darajasida"],
        "options_ru": ["На уровне step, внутри одного job'а", "На уровне целого workflow", "Только на уровне secrets", "Только на уровне matrix"],
        "correct_answers": "A",
        "hint": "Composite action o'z alohida runner'ga egami?",
        "hint_ru": "Есть ли у composite action свой отдельный runner?",
        "explanation": "Composite action bitta job ICHIDA, o'sha job'ning runner'ida ishlaydi, alohida runner'i yo'q.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Reusable workflow trigger'i",
        "title_ru": "Триггер reusable workflow",
        "description": "Boshqa workflow'lar tomonidan chaqirilishi mumkin bo'lgan workflow qanday trigger'ga ega bo'lishi kerak?",
        "description_ru": "Какой триггер должен быть у workflow, который могут вызывать другие workflow?",
        "exercise_type": "multiple_choice",
        "options": ["on: workflow_call", "on: workflow_dispatch", "on: push", "on: schedule"],
        "options_ru": ["on: workflow_call", "on: workflow_dispatch", "on: push", "on: schedule"],
        "correct_answers": "A",
        "hint": "workflow_dispatch - qo'lda, workflow_call esa boshqa workflow'dan chaqirish uchun.",
        "hint_ru": "workflow_dispatch — вручную, workflow_call — для вызова из другого workflow.",
        "explanation": "on: workflow_call: workflow'ni \"chaqiriladigan funksiya\"ga aylantiradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "secrets: inherit xavfi",
        "title_ru": "Риск secrets: inherit",
        "description": "secrets: inherit ishlatishning potentsial xavfsizlik kamchiligi nima?",
        "description_ru": "Какой потенциальный недостаток безопасности у использования secrets: inherit?",
        "exercise_type": "multiple_choice",
        "options": [
            "Barcha secret'larni uzatib, 'eng kam huquq' tamoyilini buzishi mumkin",
            "Hech qanday xavf yo'q",
            "Faqat matrix bilan ishlamaydi",
            "Secret'larni logда ochiq ko'rsatadi",
        ],
        "options_ru": [
            "Может нарушить принцип 'минимальных прав', передавая все secrets",
            "Никакого риска нет",
            "Не работает только с matrix",
            "Показывает secrets открыто в логе",
        ],
        "correct_answers": "A",
        "hint": "Chaqirilgan workflow'ga KERAKSIZ secret'lar ham uzatilsa nima bo'ladi?",
        "hint_ru": "Что если вызванному workflow передаются и НЕНУЖНЫЕ secrets?",
        "explanation": "Aniq sanab o'tish (faqat kerakli secret'larni) xavfsizroq, lekin ko'proq yozish talab qiladi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Composite action shell talabi",
        "title_ru": "Требование shell в composite action",
        "description": "Composite action ichidagi har bir run: step'ida aniq ko'rsatilishi shart bo'lgan kalit: ___: bash",
        "description_ru": "Ключ, который обязательно нужно указать явно в каждом step'е run: внутри composite action: ___: bash",
        "exercise_type": "fill_in_blank",
        "correct_answers": "shell",
        "hint": "Oddiy workflow'da avtomatik tanlanadigan, lekin composite action'da aniq yozilishi kerak bo'lgan narsa.",
        "hint_ru": "То, что в обычном workflow выбирается автоматически, но в composite action должно быть указано явно.",
        "difficulty_level": "Hard",
        "points": 12,
    },
]

# ---------------------------------------------------------------------------
# Lesson 10 — Self-hosted vs GitHub-hosted runner'lar
# ---------------------------------------------------------------------------

L10_TEXT = """
<h3>Ushbu platforma qaysi runner turini ishlatadi va nega</h3>
<p>Uchala workflow ham <code>runs-on: ubuntu-latest</code> ishlatadi —
bu <strong>GitHub-hosted runner</strong>: GitHub'ning o'zi taqdim
etadigan, har bir run uchun yangidan yaratiladigan, tugagach butunlay
o'chiriladigan virtual mashina. Muqobili — <strong>self-hosted
runner</strong>: siz o'zingiz boshqaradigan, doimiy ishlaydigan mashina
(jismoniy server, VM, hattoki xuddi shu prod server) bo'lib, unga
<code>runs-on: self-hosted</code> orqali murojaat qilinadi.</p>

<h3>GitHub-hosted afzalliklari — nega bu repo ularni tanlagan</h3>
<p><code>deploy-frontend.yml</code>ning kommentariyasi buni to'g'ridan-
to'g'ri tushuntiradi: "GH Actions runners have 7 GB RAM and 4 cores —
comfortable margin". GitHub-hosted runner'lar (1) HECH QANDAY sozlashni
talab qilmaydi (darhol tayyor), (2) har safar TOZA muhitda ishlaydi (bir
run'dagi holat ikkinchisiga umuman ta'sir qilmaydi — xavfsizlik uchun
ideal), (3) GitHub tomonidan avtomatik yangilanib turiladi. Kamchiligi —
(1) resurs cheklangan (standart 7GB RAM/2-4 core), (2) uzoq/og'ir
vazifalar (masalan katta Docker image qurish) uchun sekinroq bo'lishi
mumkin, (3) xususiy repo'larda daqiqalar bo'yicha to'lanadi.</p>

<h3>Self-hosted qachon kerak bo'ladi</h3>
<p>Agar ushbu platforma <strong>self-hosted</strong> runner ishlatganda
edi (masalan, prod serverning o'zida), <code>deploy-backend.yml</code>
SSH orqali ulanish o'rniga TO'G'RIDAN-TO'G'RI o'sha serverda ishlagan
bo'lardi — SSH kaliti, <code>ssh-keyscan</code>, hattoki butun "Configure
SSH" step'i UMUMAN kerak bo'lmasdi. Bu — ba'zan jozibali ko'rinadi, lekin
o'ziga xos yangi muammolarni keltirib chiqaradi: runner doimiy ishlaydigan
bo'lgani uchun, ikkita run orasida ESKI holat (fayllar, kesh, hatto zararli
kod) QOLIB KETISHI mumkin — bu GitHub-hosted'ning "har safar toza muhit"
kafolatini yo'qotadi.</p>

<h3>Self-hosted'ning haqiqiy sabablari</h3>
<ul>
<li><strong>Maxsus apparat</strong> — GPU kerak bo'lgan ML pipeline,
yoki juda katta RAM/disk talab qiladigan build.</li>
<li><strong>Tarmoq izolyatsiyasi</strong> — CI ichki tarmoqdagi
resurslarga (masalan, faqat VPN ichida ko'rinadigan baza) kirishi kerak
bo'lganda.</li>
<li><strong>Xarajat</strong> — juda ko'p sonli, doimiy CI run'lari
bo'lgan katta jamoada, o'z serveringiz GitHub'ning daqiqa narxidan
arzonroq bo'lishi mumkin.</li>
</ul>

<h3>Self-hosted'ning xavfsizlik xavfi — nega ehtiyot bo'lish kerak</h3>
<p>GitHub'ning o'zi ochiq-manba (public) repozitoriyalarda self-hosted
runner ishlatishni QATTIQ tavsiya ETMAYDI: har qanday tashqi
kontributor ochgan pull request avtomatik ravishda self-hosted runner
kodini bajarishi mumkin — bu runner joylashgan tarmoqqa kirish huquqini
berishi mumkin (masalan, prod serverning o'zi bo'lsa). Xususiy repo'da,
ishonchli jamoa a'zolari bilan, bu xavf sezilarli darajada kamayadi, lekin
baribir "kim PR ocha oladi" nazoratini talab qiladi.</p>

<h3>GitHub-hosted vs self-hosted taqqoslash</h3>
<pre class="mermaid">
flowchart LR
  subgraph GH["GitHub-hosted (ushbu repo)"]
    G1["runs-on: ubuntu-latest"] --> G2["Har run - yangi, toza VM
7GB RAM, 4 core"]
    G2 --> G3["Tugagach butunlay
o'chiriladi"]
  end
  subgraph SH["Self-hosted (muqobil)"]
    S1["runs-on: self-hosted"] --> S2["Doimiy ishlaydigan
o'z mashinangiz"]
    S2 --> S3["Run'lar orasida
holat SAQLANIB QOLADI"]
  end
  style G3 fill:#c8f7c5,stroke:#2a9d34
  style S3 fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Diagramma asosiy amaliy farqni ko'rsatadi: GitHub-hosted'da har bir run
mutlaqo mustaqil (xavfsiz, lekin resurs cheklangan); self-hosted'da
tezlik/moslashuvchanlik bor, lekin run'lar orasidagi holat izolyatsiyasi
sizning o'z mas'uliyatingiz.</p>

<h3>Runner group'lar — tashkilot darajasida boshqarish</h3>
<p>Ko'plab repozitoriyaga ega tashkilotlarda self-hosted runner'lar
alohida <strong>runner group</strong>larga birlashtiriladi (masalan
"production-deploy-runners", "gpu-runners") — har bir guruh uchun qaysi
repozitoriyalar unga murojaat qila olishini cheklash mumkin. Bu — ushbu
kursning 8-darsida ko'rgan CODEOWNERS'ga o'xshash cheklov tamoyili:
har bir resurs faqat unga ruxsat berilgan aniq doiraga ochiq bo'ladi,
hamma narsaga hamma kirmaydi.</p>
""".strip()

L10_TEXT_RU = """
<h3>Какой тип runner использует эта платформа и почему</h3>
<p>Все три workflow используют <code>runs-on: ubuntu-latest</code> — это
<strong>GitHub-hosted runner</strong>: виртуальная машина,
предоставляемая самим GitHub, создаваемая заново для каждого run и
полностью уничтожаемая после завершения. Альтернатива —
<strong>self-hosted runner</strong>: машина, которой управляете вы сами
(физический сервер, VM, даже тот же самый prod-сервер), постоянно
работающая, к которой обращаются через <code>runs-on: self-hosted</code>.</p>

<h3>Преимущества GitHub-hosted — почему этот репо выбрал их</h3>
<p>Комментарий в <code>deploy-frontend.yml</code> объясняет это напрямую:
"GH Actions runners have 7 GB RAM and 4 cores — comfortable margin".
GitHub-hosted runner'ы (1) НЕ требуют НИКАКОЙ настройки (сразу готовы),
(2) каждый раз работают в ЧИСТОЙ среде (состояние одного run вообще не
влияет на другой — идеально для безопасности), (3) автоматически
обновляются самим GitHub. Недостатки — (1) ограниченные ресурсы (по
умолчанию 7ГБ RAM/2-4 ядра), (2) могут быть медленнее для
долгих/тяжёлых задач (например, сборка большого Docker image), (3) в
частных репозиториях оплачиваются по минутам.</p>

<h3>Когда нужен self-hosted</h3>
<p>Если бы эта платформа использовала <strong>self-hosted</strong>
runner (например, на самом prod-сервере), <code>deploy-backend.yml</code>
работал бы НАПРЯМУЮ на этом сервере вместо подключения по SSH — ключ
SSH, <code>ssh-keyscan</code>, даже весь step "Configure SSH" были бы
ВООБЩЕ не нужны. Это иногда кажется привлекательным, но порождает свои
новые проблемы: поскольку runner работает постоянно, между двумя run
может СОХРАНЯТЬСЯ СТАРОЕ состояние (файлы, кеш, даже вредоносный код) —
это теряет гарантию "каждый раз чистая среда" у GitHub-hosted.</p>

<h3>Реальные причины для self-hosted</h3>
<ul>
<li><strong>Специальное железо</strong> — ML pipeline, требующий GPU,
или сборка, требующая очень много RAM/диска.</li>
<li><strong>Сетевая изоляция</strong> — когда CI нужен доступ к
ресурсам внутренней сети (например, БД, видимая только внутри VPN).</li>
<li><strong>Стоимость</strong> — в большой команде с очень частыми,
постоянными CI run'ами, собственный сервер может быть дешевле, чем
поминутная цена GitHub.</li>
</ul>

<h3>Риск безопасности self-hosted — почему нужна осторожность</h3>
<p>Сам GitHub НАСТОЯТЕЛЬНО НЕ РЕКОМЕНДУЕТ использовать self-hosted runner
в публичных (public) репозиториях: любой pull request, открытый внешним
контрибьютором, может автоматически выполнить код на self-hosted runner'е
— это может дать доступ к сети, где находится runner (например, если это
сам prod-сервер). В частном репо, с доверенными членами команды, этот
риск значительно снижается, но всё равно требует контроля "кто может
открывать PR".</p>

<h3>Сравнение GitHub-hosted и self-hosted</h3>
<pre class="mermaid">
flowchart LR
  subgraph GH["GitHub-hosted (этот репо)"]
    G1["runs-on: ubuntu-latest"] --> G2["Каждый run - новая, чистая VM
7ГБ RAM, 4 ядра"]
    G2 --> G3["После завершения полностью
уничтожается"]
  end
  subgraph SH["Self-hosted (альтернатива)"]
    S1["runs-on: self-hosted"] --> S2["Постоянно работающая
собственная машина"]
    S2 --> S3["Состояние МЕЖДУ run'ами
СОХРАНЯЕТСЯ"]
  end
  style G3 fill:#c8f7c5,stroke:#2a9d34
  style S3 fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Диаграмма показывает главную практическую разницу: в GitHub-hosted
каждый run абсолютно независим (безопасно, но ограничены ресурсы); в
self-hosted есть скорость/гибкость, но изоляция состояния между run'ами
— ваша собственная ответственность.</p>

<h3>Группы runner'ов — управление на уровне организации</h3>
<p>В организациях с множеством репозиториев self-hosted runner'ы
объединяются в отдельные <strong>runner group</strong> (например
"production-deploy-runners", "gpu-runners") — для каждой группы можно
ограничить, какие репозитории могут к ней обращаться. Это — принцип
ограничения, похожий на CODEOWNERS из урока 8 этого курса: каждый ресурс
открыт только для конкретного разрешённого круга, а не для всех.
Итоговое практическое правило для любой новой платформы вроде этой:
начинать с GitHub-hosted по умолчанию и переходить на self-hosted только
тогда, когда для этого есть конкретная, измеримая причина — а не просто
потому, что "свой сервер кажется быстрее".</p>
""".strip()

L10_CODE = """
# ============================================================
# 1) Ushbu repo'ning haqiqiy tanlovi - GitHub-hosted, uchala faylda ham
# ============================================================
# test.yml:
jobs:
  backend:
    runs-on: ubuntu-latest    # <- GitHub-hosted
  frontend:
    runs-on: ubuntu-latest    # <- GitHub-hosted

# deploy-backend.yml:
jobs:
  deploy:
    runs-on: ubuntu-latest    # <- GitHub-hosted (SSH orqali PROD serverga ulanadi)

# deploy-frontend.yml:
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest    # <- GitHub-hosted (build shu yerda, keyin rsync)

# ============================================================
# 2) Agar self-hosted ishlatilganda - deploy-backend.yml QANDAY o'zgarardi
# ============================================================
# HOZIRGI (GitHub-hosted + SSH):
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          mkdir -p ~/.ssh && printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
      - name: Pull and restart (orqali SSH)
        run: ssh -i ~/.ssh/deploy_key user@host "cd /app && git pull && systemctl restart app"

# MUQOBIL (self-hosted, prod serverning o'zida ishlaydi):
jobs:
  deploy:
    runs-on: self-hosted       # <- prod serverning o'zi runner sifatida ro'yxatdan o'tgan
    steps:
      # SSH kaliti, ssh-keyscan, Configure SSH step'i - UMUMAN KERAK EMAS,
      # chunki runner ALLAQACHON prod serverning o'zi.
      - run: cd /app && git pull origin server
      - run: source venv/bin/activate && pip install -r requirements.txt --quiet
      - run: sudo systemctl restart student-platform-backend

# ============================================================
# 3) Self-hosted runner'ni repo'ga ro'yxatdan o'tkazish (bir martalik)
# ============================================================
$ mkdir actions-runner && cd actions-runner
$ curl -o actions-runner-linux-x64.tar.gz -L \\
    https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-linux-x64-2.319.1.tar.gz
$ tar xzf actions-runner-linux-x64.tar.gz
$ ./config.sh --url https://github.com/OWNER/REPO --token <RUNNER_TOKEN>
$ ./run.sh
# Runner endi Settings -> Actions -> Runners bo'limida "Idle" (bo'sh)
# holatida ko'rinadi va runs-on: self-hosted bo'lgan har qanday job'ni
# kutib turadi.

# ============================================================
# 4) Label orqali muayyan self-hosted runner'ni tanlash
# ============================================================
jobs:
  gpu-training:
    runs-on: [self-hosted, gpu, linux]   # <- faqat shu 3 ta labelga ega
                                          #    runner'da ishga tushadi
    steps:
      - run: nvidia-smi
      - run: python train_model.py

# ============================================================
# 5) Xavfsizlik: public repo'da self-hosted runner ishlatishning xavfi
# ============================================================
# Agar OWNER/REPO PUBLIC bo'lsa va self-hosted runner ulangan bo'lsa:
#   1. Tashqi odam fork qilib, zararli kod bilan PR ochadi
#   2. Agar workflow pull_request_target yoki noto'g'ri sozlangan
#      pull_request trigger bilan ishlasa, bu kod SIZNING self-hosted
#      runner'ingizda BAJARILISHI mumkin
#   3. Runner joylashgan tarmoqqa (masalan ichki baza, boshqa serverlar)
#      kirish xavfi tug'iladi
# Shu sababli GitHub PUBLIC repo'lar uchun self-hosted'ni faqat qattiq
# nazorat (masalan required approval for first-time contributors) bilan
# ishlatishni tavsiya qiladi.
""".strip()

L10_CODE_RU = """
# ============================================================
# 1) Реальный выбор этого репо - GitHub-hosted, во всех трёх файлах
# ============================================================
# test.yml:
jobs:
  backend:
    runs-on: ubuntu-latest    # <- GitHub-hosted
  frontend:
    runs-on: ubuntu-latest    # <- GitHub-hosted

# deploy-backend.yml:
jobs:
  deploy:
    runs-on: ubuntu-latest    # <- GitHub-hosted (подключается по SSH к PROD-серверу)

# deploy-frontend.yml:
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest    # <- GitHub-hosted (сборка здесь, затем rsync)

# ============================================================
# 2) Как изменился бы deploy-backend.yml при использовании self-hosted
# ============================================================
# ТЕКУЩИЙ (GitHub-hosted + SSH):
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          mkdir -p ~/.ssh && printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
      - name: Pull and restart (через SSH)
        run: ssh -i ~/.ssh/deploy_key user@host "cd /app && git pull && systemctl restart app"

# АЛЬТЕРНАТИВА (self-hosted, работает на самом prod-сервере):
jobs:
  deploy:
    runs-on: self-hosted       # <- сам prod-сервер зарегистрирован как runner
    steps:
      # Ключ SSH, ssh-keyscan, step Configure SSH - ВООБЩЕ НЕ НУЖНЫ,
      # т.к. runner УЖЕ И ЕСТЬ сам prod-сервер.
      - run: cd /app && git pull origin server
      - run: source venv/bin/activate && pip install -r requirements.txt --quiet
      - run: sudo systemctl restart student-platform-backend

# ============================================================
# 3) Регистрация self-hosted runner в репо (одноразово)
# ============================================================
$ mkdir actions-runner && cd actions-runner
$ curl -o actions-runner-linux-x64.tar.gz -L \\
    https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-linux-x64-2.319.1.tar.gz
$ tar xzf actions-runner-linux-x64.tar.gz
$ ./config.sh --url https://github.com/OWNER/REPO --token <RUNNER_TOKEN>
$ ./run.sh
# Теперь runner виден в разделе Settings -> Actions -> Runners в
# состоянии "Idle" (свободен) и ожидает любой job с runs-on: self-hosted.

# ============================================================
# 4) Выбор конкретного self-hosted runner через label
# ============================================================
jobs:
  gpu-training:
    runs-on: [self-hosted, gpu, linux]   # <- запустится только на runner'е
                                          #    с этими 3 label
    steps:
      - run: nvidia-smi
      - run: python train_model.py

# ============================================================
# 5) Безопасность: риск использования self-hosted runner в public репо
# ============================================================
# Если OWNER/REPO ПУБЛИЧНЫЙ и подключён self-hosted runner:
#   1. Внешний человек форкает и открывает PR со злонамеренным кодом
#   2. Если workflow использует pull_request_target или неверно
#      настроенный триггер pull_request, этот код может ВЫПОЛНИТЬСЯ
#      на ВАШЕМ self-hosted runner'е
#   3. Возникает риск доступа к сети, где находится runner (например,
#      внутренняя БД, другие серверы)
# Поэтому GitHub рекомендует использовать self-hosted для ПУБЛИЧНЫХ репо
# только со строгим контролем (например, required approval for
# first-time contributors).
""".strip()

L10_TASK = {
    "task_title": "GitHub-hosted vs self-hosted qaror hujjatini yozing",
    "task_title_ru": "Напишите документ решения GitHub-hosted против self-hosted",
    "task_description": (
        "Ushbu platformaning uchta workflow faylini tahlil qilib, "
        "quyidagi savolga texnik hujjat (ADR — Architecture Decision "
        "Record uslubida) yozing: 'Agar prod server resurslari juda "
        "cheklangan bo'lib, GitHub-hosted runner minutlari uchun oylik "
        "byudjet tugab qolsa, biz self-hosted runner'ga o'tishimiz "
        "kerakmi?' Ijobiy va salbiy tomonlarni ANIQ shu repo konteksida "
        "(SSH, secrets, deploy strategiyasi) muhokama qiling."
    ),
    "task_description_ru": (
        "Проанализировав три файла workflow этой платформы, напишите "
        "технический документ (в стиле ADR — Architecture Decision "
        "Record) на вопрос: 'Если ресурсы prod-сервера сильно "
        "ограничены и заканчивается месячный бюджет минут GitHub-hosted "
        "runner, должны ли мы перейти на self-hosted runner?' Обсудите "
        "плюсы и минусы ИМЕННО в контексте этого репо (SSH, secrets, "
        "стратегия деплоя)."
    ),
    "task_requirements": (
        "1) Kamida 3 ta ijobiy va 3 ta salbiy jihat sanab o'tilgan "
        "bo'lishi kerak. 2) Xavfsizlik xavfi (public repo, ishonchsiz "
        "PR) alohida muhokama qilinishi shart. 3) Yakuniy tavsiya aniq "
        "asoslangan bo'lishi kerak (ha/yo'q, va nima uchun)."
    ),
    "task_requirements_ru": (
        "1) Должно быть перечислено минимум 3 плюса и 3 минуса. 2) Риск "
        "безопасности (публичный репо, недоверенные PR) должен быть "
        "обсуждён отдельно. 3) Итоговая рекомендация должна быть чётко "
        "обоснована (да/нет и почему)."
    ),
    "task_technologies": "GitHub Actions runners, ADR",
    "task_deadline_days": 4,
}

L10_SAMPLE = {
    "title": "Namuna: label bilan ikkita runner turini shartli tanlash",
    "description": (
        "Bitta workflow ichida input parametriga qarab GitHub-hosted "
        "yoki self-hosted runner'ni tanlaydigan namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/runner-choice-demo.yml",
            "language": "yaml",
            "code": (
                "name: Runner Choice Demo\n\n"
                "on:\n"
                "  workflow_dispatch:\n"
                "    inputs:\n"
                "      use_self_hosted:\n"
                "        description: \"self-hosted runner ishlatilsinmi\"\n"
                "        type: boolean\n"
                "        default: false\n\n"
                "jobs:\n"
                "  build:\n"
                "    runs-on: ${{ inputs.use_self_hosted && 'self-hosted' || 'ubuntu-latest' }}\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - name: Show runner info\n"
                "        run: |\n"
                "          echo \"Runner OS: $RUNNER_OS\"\n"
                "          echo \"Runner name: $RUNNER_NAME\"\n"
                "          echo \"Self-hosted tanlandimi: ${{ inputs.use_self_hosted }}\"\n"
            ),
        },
    ],
}

L10_EXERCISES = [
    {
        "title": "Ushbu repo qaysi runner turini ishlatadi",
        "title_ru": "Какой тип runner использует этот репо",
        "description": "Uchala workflow faylida ham runs-on qaysi qiymatga ega?",
        "description_ru": "Какое значение имеет runs-on во всех трёх файлах workflow?",
        "exercise_type": "multiple_choice",
        "options": ["ubuntu-latest (GitHub-hosted)", "self-hosted", "windows-latest", "macos-latest"],
        "options_ru": ["ubuntu-latest (GitHub-hosted)", "self-hosted", "windows-latest", "macos-latest"],
        "correct_answers": "A",
        "hint": "0-darsda ko'rgan runs-on qiymatini eslang.",
        "hint_ru": "Вспомните значение runs-on из урока 0.",
        "explanation": "test.yml, deploy-backend.yml va deploy-frontend.yml barchasi ubuntu-latest'dan foydalanadi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "GitHub-hosted'ning asosiy afzalligi",
        "title_ru": "Основное преимущество GitHub-hosted",
        "description": "GitHub-hosted runner'ning eng muhim xavfsizlik afzalligi nima?",
        "description_ru": "Каково важнейшее преимущество безопасности GitHub-hosted runner?",
        "exercise_type": "multiple_choice",
        "options": ["Har bir run toza, yangi muhitda boshlanadi", "U bepul va cheksiz", "U tezroq internet tezligiga ega", "U hech qachon o'chirilmaydi"],
        "options_ru": ["Каждый run начинается в чистой, новой среде", "Он бесплатный и безграничный", "У него быстрее интернет", "Он никогда не выключается"],
        "correct_answers": "A",
        "hint": "Run tugagach nima bo'ladi?",
        "hint_ru": "Что происходит после завершения run?",
        "explanation": "Har bir run mustaqil, yangi VM'da ishlaydi - eski run'ning holati keyingisiga ta'sir qilmaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Self-hosted xavfsizlik xavfi",
        "title_ru": "Риск безопасности self-hosted",
        "description": "Public repo'da self-hosted runner ishlatishning asosiy xavfi nima?",
        "description_ru": "Каков основной риск использования self-hosted runner в публичном репо?",
        "exercise_type": "multiple_choice",
        "options": [
            "Tashqi PR orqali zararli kod runner tarmog'ida bajarilishi mumkin",
            "U hech qachon ishlamaydi",
            "U faqat Windows'da ishlaydi",
            "Secret'lar avtomatik oshkor bo'ladi",
        ],
        "options_ru": [
            "Через внешний PR вредоносный код может выполниться в сети runner'а",
            "Он вообще не работает",
            "Работает только на Windows",
            "Secrets автоматически раскрываются",
        ],
        "correct_answers": "A",
        "hint": "Kim PR ochsa, uning kodi qaysi runner'da ishga tushadi?",
        "hint_ru": "На каком runner'е выполняется код того, кто открыл PR?",
        "explanation": "Ishonchsiz tashqi kontributor'ning kodi self-hosted runner tarmog'iga kirish huquqini olishi mumkin.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Runner turini belgilaydigan kalit",
        "title_ru": "Ключ, определяющий тип runner",
        "description": "Job qaysi mashinada ishlashini belgilaydigan kalit so'z: ___: ubuntu-latest",
        "description_ru": "Ключевое слово, определяющее, на какой машине работает job: ___: ubuntu-latest",
        "exercise_type": "fill_in_blank",
        "correct_answers": "runs-on",
        "correct_answers_ru": "runs-on",  # YAML key — literal token, unchanged across languages
        "hint": "0-darsdan boshlab har bir job ta'rifida bor edi.",
        "hint_ru": "Начиная с 0-го урока, это было в определении каждого job.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 11 — Muvaffaqiyatsiz CI'ni disk qilish: log'lar, qayta ishga tushirish, keng tarqalgan xatolar
# ---------------------------------------------------------------------------

L11_TEXT = """
<h3>Qizil X ko'rgach birinchi qadam: log'ni o'qish</h3>
<p>Actions tabida muvaffaqiyatsiz run ustiga bosilsa, har bir step
kengaytiriladigan (expandable) bo'lib, ANIQ qaysi buyruq, qaysi qatorda
xato berganini ko'rsatadi. Muhim odat: eng OXIRIDAGI qizil step'dan
BOSHLANG, undan OLDINGI (yashil) step'larni emas — muammo deyarli har
doim birinchi muvaffaqiyatsiz step'da, undan oldingilar allaqachon
o'tgan. <code>::error::</code> prefiksi bilan yozilgan qatorlar
(<code>deploy-frontend.yml</code>dagi "Verify build artefact" kabi) UI'da
maxsus qizil belgi bilan ажratilib, tezda topiladi.</p>

<h3>Keng tarqalgan xato turi 1: working-directory unutilishi</h3>
<p>0-darsda ko'rganimizdek, <code>test.yml</code>ning har bir step'ida
<code>working-directory: backend</code> yoki <code>frontend</code> aniq
yozilgan. Agar buni QO'SHILGAN yangi step'da unutib qo'ysangiz, xato
odatda shunday ko'rinadi: <code>ERROR: Could not open requirements
file: [Errno 2] No such file or directory: 'requirements.txt'</code> —
bu Python ildiz papkada qidirayotganini, lekin fayl
<code>backend/</code> ichida ekanini bildiradi.</p>

<h3>Keng tarqalgan xato turi 2: mahalliyda ishlaydi, CI'da ishlamaydi</h3>
<p>Bu — eng ko'p uchraydigan, eng chalkashtiruvchi holat. Sabablar
odatda: (1) atrof-muhit o'zgaruvchisi CI'da yo'q (masalan
<code>DATABASE_URL</code> mahalliyda <code>.env</code> orqali, CI'da esa
<code>env:</code> orqali berilishi kerak — <code>test.yml</code>da aynan
shu <code>DATABASE_URL: sqlite+aiosqlite:///./test.db</code> qatoriga
e'tibor bering), (2) kesh eskirgan (4-dars — lekin bu HECH QACHON
build'ni sindirmaydi, faqat sekinlashtiradi, shuning uchun bu ehtimol
past), (3) fayl tizimi katta-kichik harflarga sezgirligi farqi
(mahalliy macOS/Windows katta-kichikni farqlamasligi mumkin, Linux
runner esa farqlaydi — <code>Import.js</code> va <code>import.js</code>
Linux'da IKKI XIL fayl).</p>

<h3>Keng tarqalgan xato turi 3: secret noto'g'ri yoki eskirgan</h3>
<p>2-darsda ko'rganimizdek, agar <code>SSH_PRIVATE_KEY</code> noto'g'ri
formatda saqlangan bo'lsa (masalan oxirgi yangi qator belgisi
kesilgan bo'lsa), xato odatda <code>Permission denied
(publickey)</code> ko'rinishida chiqadi. Bu — deploy-backend.yml/
deploy-frontend.yml'da eng ko'p uchraydigan muvaffaqiyatsizlik sababi:
secret QIYMATI o'zgarmagan, lekin SERVERDAGI <code>authorized_keys</code>
fayli yangilanmagan (yoki aksincha) — ikkala tomon SINXRON emas.</p>

<h3>Job'ni qayta ishga tushirish — qachon foydali, qachon xavfli</h3>
<p>GitHub UI'dagi "Re-run failed jobs" tugmasi — agar xato VAQTINCHA
(masalan tarmoq uzilishi, GitHub'ning o'zida vaqtinchalik nosozlik)
bo'lsa foydali. Lekin agar xato KOD MUAMMOSI bo'lsa (masalan haqiqiy test
buzilgan), qayta ishga tushirish HECH NARSANI o'zgartirmaydi — xuddi
o'sha xato qayta chiqadi, faqat CI daqiqasi behuda sarflanadi. Muhim
qoida: birinchi navbatda log'ni o'qib, xato TABIATINI aniqlang, keyingina
qayta ishga tushirish kerakmi yoki kodni tuzatish kerakmi qaror qiling.</p>

<h3>Diagnostika oqimi diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  X["Qizil X ko'rindi"] --> L["Eng oxirgi qizil
step logini oching"]
  L --> Q{"Xato tabiati?"}
  Q -->|"Tarmoq/GitHub
vaqtinchalik nosozligi"| RERUN["Re-run failed jobs"]
  Q -->|"working-directory
yoki yo'l xatosi"| FIX1["YAML'ni tuzatib
qayta push"]
  Q -->|"Secret/kirish
huquqi xatosi"| FIX2["Secret'ni qayta
tekshirib yangilash"]
  Q -->|"Haqiqiy kod/test
xatosi"| FIX3["Kodni tuzatib
qayta push"]
  style RERUN fill:#d6e9ff,stroke:#2266aa
  style FIX1 fill:#ffe9b3,stroke:#d09000
  style FIX2 fill:#ffd6d6,stroke:#cc3333
  style FIX3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Diagramma har bir xato turi uchun TO'G'RI reaktsiyani ko'rsatadi — bu
kursning eng amaliy qismi: log'ni o'qish orqali xato TURINI aniqlash,
so'ngra mos yechim tanlash, tasodifiy "qayta urinib ko'raman" emas.</p>

<h3>Keng tarqalgan xato turi 4: YAML joylashuvi (indentation) xatosi</h3>
<p>YAML bo'shliqlarga (whitespace) juda sezgir — <code>steps:</code>
ro'yxatidagi bitta qatorning noto'g'ri chekinishi butun workflow'ni
GitHub tomonidan "Invalid workflow file" deb rad etilishiga olib kelishi
mumkin. Bunday xato hattoki run BOSHLANMASDAN OLDIN, Actions tabida
qizil ogohlantirish sifatida ko'rinadi ("This run likely failed because
of a workflow file issue"). Eng tez tekshirish usuli — YAML'ni
mahalliyda <code>yamllint</code> yoki onlayn YAML validator orqali push
qilishdan OLDIN tekshirish, 112-kursda o'rgangan "muammoni ishlab
chiqarishga yetkazmasdan ushlash" tamoyiliga mos.</p>
""".strip()

L11_TEXT_RU = """
<h3>Первый шаг при виде красного X: чтение лога</h3>
<p>Если нажать на неудачный run во вкладке Actions, каждый step
раскрывается (expandable) и показывает ТОЧНО, какая команда, в какой
строке дала ошибку. Важная привычка: начинайте с ПОСЛЕДНЕГО красного
step'а, а не с предыдущих (зелёных) — проблема почти всегда в первом
неудачном step'е, предыдущие уже прошли. Строки с префиксом
<code>::error::</code> (как в "Verify build artefact" из
<code>deploy-frontend.yml</code>) в UI выделяются специальным красным
значком и быстро находятся.</p>

<h3>Распространённый тип ошибки 1: забытый working-directory</h3>
<p>Как мы видели в уроке 0, в каждом step'е <code>test.yml</code> точно
указан <code>working-directory: backend</code> или <code>frontend</code>.
Если забыть это в НОВОМ добавленном step'е, ошибка обычно выглядит так:
<code>ERROR: Could not open requirements file: [Errno 2] No such file or
directory: 'requirements.txt'</code> — это значит, что Python ищет в
корневой папке, а файл находится внутри <code>backend/</code>.</p>

<h3>Распространённый тип ошибки 2: работает локально, не работает в CI</h3>
<p>Это — самый частый, самый запутывающий случай. Причины обычно: (1)
переменная окружения отсутствует в CI (например
<code>DATABASE_URL</code> локально задаётся через <code>.env</code>, а в
CI должна передаваться через <code>env:</code> — обратите внимание
именно на строку <code>DATABASE_URL: sqlite+aiosqlite:///./test.db</code>
в <code>test.yml</code>), (2) устаревший кеш (урок 4 — но это НИКОГДА не
ломает сборку, только замедляет, поэтому вероятность этой причины
низкая), (3) разница в чувствительности файловой системы к регистру
(локальный macOS/Windows может не различать регистр, а Linux runner
различает — <code>Import.js</code> и <code>import.js</code> на Linux —
ДВА РАЗНЫХ файла).</p>

<h3>Распространённый тип ошибки 3: неверный или устаревший secret</h3>
<p>Как мы видели в уроке 2, если <code>SSH_PRIVATE_KEY</code> сохранён в
неверном формате (например, обрезан последний символ новой строки),
ошибка обычно выглядит как <code>Permission denied
(publickey)</code>. Это — самая частая причина сбоя в
deploy-backend.yml/deploy-frontend.yml: ЗНАЧЕНИЕ secret не менялось, но
файл <code>authorized_keys</code> НА СЕРВЕРЕ не обновился (или наоборот)
— обе стороны НЕ СИНХРОНИЗИРОВАНЫ.</p>

<h3>Повторный запуск job'а — когда полезен, когда опасен</h3>
<p>Кнопка "Re-run failed jobs" в GitHub UI полезна, если ошибка
ВРЕМЕННАЯ (например, обрыв сети, временный сбой самого GitHub). Но если
ошибка — это ПРОБЛЕМА В КОДЕ (например, реально сломанный тест),
повторный запуск НИЧЕГО не изменит — та же ошибка появится снова, только
впустую потратится минута CI. Важное правило: сначала прочитайте лог,
определите ПРИРОДУ ошибки, и только потом решайте, нужен ли повторный
запуск или исправление кода.</p>

<h3>Диаграмма потока диагностики</h3>
<pre class="mermaid">
flowchart TB
  X["Увиден красный X"] --> L["Открыть лог последнего
красного step'а"]
  L --> Q{"Природа ошибки?"}
  Q -->|"Временный сбой сети
или GitHub"| RERUN["Re-run failed jobs"]
  Q -->|"Ошибка working-directory
или пути"| FIX1["Исправить YAML
и запушить снова"]
  Q -->|"Ошибка secret/
доступа"| FIX2["Перепроверить и
обновить secret"]
  Q -->|"Реальная ошибка
кода/теста"| FIX3["Исправить код
и запушить снова"]
  style RERUN fill:#d6e9ff,stroke:#2266aa
  style FIX1 fill:#ffe9b3,stroke:#d09000
  style FIX2 fill:#ffd6d6,stroke:#cc3333
  style FIX3 fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Диаграмма показывает ПРАВИЛЬНУЮ реакцию для каждого типа ошибки — это
самая практическая часть курса: определить ТИП ошибки через чтение лога,
затем выбрать подходящее решение, а не случайное "попробую ещё раз".</p>

<h3>Распространённый тип ошибки 4: ошибка отступов (indentation) YAML</h3>
<p>YAML очень чувствителен к пробелам (whitespace) — неверный отступ
одной строки в списке <code>steps:</code> может привести к тому, что
GitHub отклонит весь workflow как "Invalid workflow file". Такая ошибка
видна во вкладке Actions ещё ДО НАЧАЛА run, как красное предупреждение
("This run likely failed because of a workflow file issue"). Самый
быстрый способ проверки — проверить YAML локально через
<code>yamllint</code> или онлайн-валидатор YAML ДО push, что
соответствует принципу курса 112 "ловить проблему до продакшена".</p>
""".strip()

L11_CODE = """
# ============================================================
# 1) Log'dagi ::error:: annotatsiyasini o'qish
# ============================================================
# deploy-frontend.yml'dagi haqiqiy misol:
- name: Verify build artefact
  run: |
    test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }

# Agar bu step muvaffaqiyatsiz bo'lsa, Actions UI'da:
#   [ERROR] build/index.html missing — aborting deploy
# qatori QIZIL rangda, alohida "Annotations" bo'limida ko'rinadi -
# butun log ichida qidirishning hojati yo'q.

# ============================================================
# 2) working-directory unutilgan xato (keng tarqalgan #1)
# ============================================================
# XATO (working-directory yo'q):
jobs:
  backend:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt   # <- YO'Q: working-directory!
# Xato xabari:
#   ERROR: Could not open requirements file: [Errno 2] No such file or
#   directory: 'requirements.txt'

# TO'G'RI:
      - working-directory: backend
        run: pip install -r requirements.txt

# ============================================================
# 3) env o'zgaruvchisi CI'da yo'qligi (keng tarqalgan #2)
# ============================================================
# Mahalliyda ishlaydi (.env fayli orqali DATABASE_URL bor), lekin CI'da
# .env fayli YO'Q (odatda .gitignore'da) - shuning uchun test.yml buni
# ANIQ env: orqali beradi:
- name: Run tests
  working-directory: backend
  env:
    DATABASE_URL: sqlite+aiosqlite:///./test.db
    SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
  run: python -m pytest tests/ -v --tb=short
# Agar bu env: bloki YO'QOLSA, xato odatda:
#   KeyError: 'DATABASE_URL'  yoki  sqlalchemy.exc.ArgumentError

# ============================================================
# 4) SSH secret xatosi (keng tarqalgan #3)
# ============================================================
$ ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes user@host "..."
# Muvaffaqiyatsiz bo'lsa:
Permission denied (publickey).
# Eng ko'p uchraydigan sabablar:
#  a) SSH_PRIVATE_KEY secret'i noto'liq nusxalangan (masalan oxirgi
#     bo'sh qator yo'qolgan) - printf '%s\\n' ishlatilishi aynan shu
#     muammoni oldini olish uchun (deploy-backend.yml'da ko'rgandek)
#  b) Serverdagi ~/.ssh/authorized_keys hali yangi PUBLIC kalitni
#     o'z ichiga OLMAGAN
#  c) Xato foydalanuvchi nomi (SSH_USER) yoki xato host (SSH_HOST)

# ============================================================
# 5) gh CLI orqali muvaffaqiyatsiz run'ni tekshirish va qayta ishga tushirish
# ============================================================
$ gh run list --workflow=test.yml --limit 5
STATUS  TITLE                    WORKFLOW   BRANCH   EVENT  ID
X       fix: auth bug            Tests      server   push   123456789

$ gh run view 123456789 --log-failed
# Faqat MUVAFFAQIYATSIZ step'larning to'liq logini ko'rsatadi -
# muvaffaqiyatli step'larni skroll qilishga hojat yo'q.

$ gh run rerun 123456789 --failed
# Faqat muvaffaqiyatsiz job'larni qayta ishga tushiradi (muvaffaqiyatli
# job'larni qayta bajarmaydi - vaqt tejaydi).

# ============================================================
# 6) YAML'ni push qilishdan OLDIN mahalliyda tekshirish
# ============================================================
$ pip install yamllint
$ yamllint .github/workflows/test.yml
.github/workflows/test.yml
  12:9      error    wrong indentation: expected 10 but found 8  (indentation)

# Yoki tezroq, o'rnatishsiz:
$ python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
# Xato bo'lsa, aniq qator raqami bilan yaml.scanner.ScannerError chiqadi -
# bu push qilishdan oldin, hattoki GitHub'ga yuborishdan oldin xatoni
# ushlaydi.

$ gh workflow view test.yml
# Workflow GitHub tomonidan qabul qilinganini (sintaksis to'g'ri
# ekanini) tasdiqlaydi - agar fayl noto'g'ri bo'lsa, bu buyruq workflow
# ro'yxatda "disabled" yoki umuman ko'rinmasligi mumkinligini bildiradi.
""".strip()

L11_CODE_RU = """
# ============================================================
# 1) Чтение аннотации ::error:: в логе
# ============================================================
# Реальный пример из deploy-frontend.yml:
- name: Verify build artefact
  run: |
    test -f frontend/build/index.html || { echo "::error::build/index.html missing — aborting deploy"; exit 1; }

# Если этот step упадёт, в Actions UI:
#   [ERROR] build/index.html missing — aborting deploy
# строка отображается КРАСНЫМ, в отдельном разделе "Annotations" -
# не нужно искать по всему логу.

# ============================================================
# 2) Ошибка забытого working-directory (распространённая #1)
# ============================================================
# ОШИБКА (нет working-directory):
jobs:
  backend:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt   # <- НЕТ working-directory!
# Сообщение об ошибке:
#   ERROR: Could not open requirements file: [Errno 2] No such file or
#   directory: 'requirements.txt'

# ПРАВИЛЬНО:
      - working-directory: backend
        run: pip install -r requirements.txt

# ============================================================
# 3) Отсутствие переменной env в CI (распространённая #2)
# ============================================================
# Локально работает (через файл .env есть DATABASE_URL), но в CI файла
# .env НЕТ (обычно в .gitignore) - поэтому test.yml даёт это ЯВНО через
# env:
- name: Run tests
  working-directory: backend
  env:
    DATABASE_URL: sqlite+aiosqlite:///./test.db
    SECRET_KEY: test-secret-key-for-ci-only-not-used-in-prod
  run: python -m pytest tests/ -v --tb=short
# Если этот блок env: ИСЧЕЗНЕТ, ошибка обычно:
#   KeyError: 'DATABASE_URL'  или  sqlalchemy.exc.ArgumentError

# ============================================================
# 4) Ошибка SSH secret (распространённая #3)
# ============================================================
$ ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes user@host "..."
# При неудаче:
Permission denied (publickey).
# Самые частые причины:
#  a) Secret SSH_PRIVATE_KEY скопирован неполностью (например, потерян
#     последний перевод строки) - printf '%s\\n' используется именно
#     чтобы избежать этой проблемы (как видели в deploy-backend.yml)
#  b) Файл ~/.ssh/authorized_keys на сервере ещё НЕ СОДЕРЖИТ новый
#     PUBLIC-ключ
#  c) Неверное имя пользователя (SSH_USER) или неверный хост (SSH_HOST)

# ============================================================
# 5) Проверка и повторный запуск неудачного run через gh CLI
# ============================================================
$ gh run list --workflow=test.yml --limit 5
STATUS  TITLE                    WORKFLOW   BRANCH   EVENT  ID
X       fix: auth bug            Tests      server   push   123456789

$ gh run view 123456789 --log-failed
# Показывает полный лог ТОЛЬКО неудачных step'ов - не нужно
# прокручивать успешные step'ы.

$ gh run rerun 123456789 --failed
# Перезапускает только неудачные job'ы (не выполняет заново успешные -
# экономит время).

# ============================================================
# 6) Проверка YAML локально ДО push
# ============================================================
$ pip install yamllint
$ yamllint .github/workflows/test.yml
.github/workflows/test.yml
  12:9      error    wrong indentation: expected 10 but found 8  (indentation)

# Или быстрее, без установки:
$ python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
# При ошибке появится yaml.scanner.ScannerError с точным номером строки -
# это ловит ошибку ДО push, ещё до отправки в GitHub.

$ gh workflow view test.yml
# Подтверждает, что workflow принят GitHub'ом (синтаксис верен) - если
# файл неверен, эта команда покажет, что workflow отображается как
# "disabled" или вообще не виден в списке.
""".strip()

L11_TASK = {
    "task_title": "Qasddan uchta xato yarating va disk qiling",
    "task_title_ru": "Намеренно создайте три ошибки и разберите их",
    "task_description": (
        "Shaxsiy repozitoriyangizda `test.yml`ning nusxasiga QASDDAN 3 "
        "xil xato kiriting: (1) bitta step'dan `working-directory`ni "
        "olib tashlang, (2) `DATABASE_URL` env o'zgaruvchisini olib "
        "tashlang, (3) noto'g'ri (mavjud bo'lmagan) secret nomiga "
        "murojaat qiling. Har birini alohida push qiling, log'ni "
        "o'qib, xato xabarini va uning SABABINI hisobotga yozing, "
        "so'ngra tuzating."
    ),
    "task_description_ru": (
        "В своём репозитории НАМЕРЕННО внесите 3 разные ошибки в копию "
        "`test.yml`: (1) уберите `working-directory` из одного step'а, "
        "(2) уберите переменную env `DATABASE_URL`, (3) сошлитесь на "
        "неверное (несуществующее) имя secret. Запушьте каждую отдельно, "
        "прочитайте лог, запишите в отчёт сообщение об ошибке и её "
        "ПРИЧИНУ, затем исправьте."
    ),
    "task_requirements": (
        "1) Har bir xato uchun ANIQ log xabari (nusxa ko'chirilgan) "
        "hisobotda bo'lishi kerak. 2) Har bir xatoning ILDIZ sababi "
        "tushuntirilgan bo'lishi shart (nafaqat 'ishlamadi'). 3) Har "
        "birini tuzatib, workflow qayta yashil bo'lganini isbotlang."
    ),
    "task_requirements_ru": (
        "1) Для каждой ошибки в отчёте должно быть ТОЧНОЕ сообщение "
        "лога (скопированное). 2) Для каждой ошибки должна быть "
        "объяснена КОРНЕВАЯ причина (не просто 'не сработало'). 3) "
        "Исправьте каждую и докажите, что workflow снова зелёный."
    ),
    "task_technologies": "GitHub Actions debugging, gh CLI",
    "task_deadline_days": 4,
}

L11_SAMPLE = {
    "title": "Namuna: gh CLI orqali CI diagnostika skripti",
    "description": (
        "Oxirgi muvaffaqiyatsiz run'ni topib, uning log'ini ko'rsatuvchi "
        "va foydalanuvchidan qayta ishga tushirishni so'ruvchi bash "
        "skripti."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "diagnose_ci.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "WORKFLOW=\"${1:-test.yml}\"\n\n"
                "echo \"Eng oxirgi muvaffaqiyatsiz '$WORKFLOW' run'i qidirilmoqda...\"\n"
                "RUN_ID=$(gh run list --workflow=\"$WORKFLOW\" --status=failure --limit 1 --json databaseId --jq '.[0].databaseId')\n\n"
                "if [ -z \"$RUN_ID\" ]; then\n"
                "  echo \"Muvaffaqiyatsiz run topilmadi - hammasi yashil.\"\n"
                "  exit 0\n"
                "fi\n\n"
                "echo \"Topildi: run $RUN_ID. Faqat muvaffaqiyatsiz qismlar logi:\"\n"
                "gh run view \"$RUN_ID\" --log-failed\n\n"
                "read -p \"Qayta ishga tushirilsinmi? (y/n) \" answer\n"
                "if [ \"$answer\" = \"y\" ]; then\n"
                "  gh run rerun \"$RUN_ID\" --failed\n"
                "  echo \"Qayta ishga tushirildi.\"\n"
                "else\n"
                "  echo \"Bekor qilindi - avval kodni tuzating.\"\n"
                "fi\n"
            ),
        },
    ],
}

L11_EXERCISES = [
    {
        "title": "Birinchi diagnostika qadami",
        "title_ru": "Первый шаг диагностики",
        "description": "Muvaffaqiyatsiz run'ni ko'rganda birinchi navbatda nima qilish kerak?",
        "description_ru": "Что нужно сделать в первую очередь, увидев неудачный run?",
        "exercise_type": "multiple_choice",
        "options": ["Eng oxirgi qizil step'ning log'ini o'qish", "Darhol re-run bosish", "Butun workflow faylini o'chirish", "Repozitoriyani qayta klonlash"],
        "options_ru": ["Прочитать лог последнего красного step'а", "Сразу нажать re-run", "Удалить весь файл workflow", "Заново клонировать репозиторий"],
        "correct_answers": "A",
        "hint": "Xato TABIATINI bilmasdan qayta urinish foydalimi?",
        "hint_ru": "Полезно ли повторять попытку, не зная ПРИРОДЫ ошибки?",
        "explanation": "Log har doim ANIQ qaysi buyruq va nima uchun xato berganini ko'rsatadi - bu birinchi manba.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "working-directory xatosi belgisi",
        "title_ru": "Признак ошибки working-directory",
        "description": "\"Could not open requirements file: No such file or directory\" xatosi ko'pincha nimani anglatadi?",
        "description_ru": "Что чаще всего означает ошибка \"Could not open requirements file: No such file or directory\"?",
        "exercise_type": "multiple_choice",
        "options": [
            "working-directory noto'g'ri yoki yo'q, buyruq boshqa papkada qidirmoqda",
            "Internet aloqasi yo'q",
            "Python o'rnatilmagan",
            "Secret noto'g'ri",
        ],
        "options_ru": [
            "working-directory неверен или отсутствует, команда ищет не в той папке",
            "Нет интернет-соединения",
            "Python не установлен",
            "Secret неверен",
        ],
        "correct_answers": "A",
        "hint": "requirements.txt qayerda joylashgan edi - ildiz papkadami yoki backend/ ichidami?",
        "hint_ru": "Где находится requirements.txt — в корневой папке или внутри backend/?",
        "explanation": "Bu xato deyarli har doim working-directory noto'g'ri (yoki umuman yo'q) ekanini bildiradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Re-run qачон foydasiz",
        "title_ru": "Когда re-run бесполезен",
        "description": "Qaysi holatda \"Re-run failed jobs\" tugmasi HECH NARSANI o'zgartirmaydi?",
        "description_ru": "В каком случае кнопка \"Re-run failed jobs\" НИЧЕГО не изменит?",
        "exercise_type": "multiple_choice",
        "options": [
            "Xato haqiqiy kod/test muammosi bo'lsa",
            "Xato vaqtinchalik tarmoq uzilishi bo'lsa",
            "Xato GitHub'ning o'zida vaqtinchalik nosozlik bo'lsa",
            "Har doim foydali",
        ],
        "options_ru": [
            "Если ошибка — реальная проблема в коде/тесте",
            "Если ошибка — временный обрыв сети",
            "Если ошибка — временный сбой самого GitHub",
            "Всегда полезно",
        ],
        "correct_answers": "A",
        "hint": "Kod o'zgarmasa, xuddi shu kod qayta ishga tushirilsa, natija o'zgaradimi?",
        "hint_ru": "Если код не изменился и запустить его снова, изменится ли результат?",
        "explanation": "Doimiy (kod) xatolar qayta ishga tushirishda AYNAN o'sha xatoni beradi - avval kodni tuzatish kerak.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "SSH xatosining odatiy xabari",
        "title_ru": "Типичное сообщение ошибки SSH",
        "description": "SSH kaliti noto'g'ri yoki mos kelmasa, odatda qanday xabar chiqadi: Permission denied (___)",
        "description_ru": "Если SSH-ключ неверен или не совпадает, обычно появляется сообщение: Permission denied (___)",
        "exercise_type": "fill_in_blank",
        "correct_answers": "publickey",
        "hint": "SSH kalit turi - ochiq kalit, inglizcha \"public key\".",
        "hint_ru": "Тип SSH-ключа — открытый ключ, по-английски \"public key\".",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 12 — R2: Takrorlash — artifact'lar, real deploy, branch himoyasi, reusable, runner, disk qilish
# ---------------------------------------------------------------------------

L12_TEXT = """
<h3>Ikkinchi takrorlash — 6-11-darslarning sintezi</h3>
<p>Bu — kursning ikkinchi va oxirgi (capstone'dan oldingi) takrorlash
darsi. 6-11-darslarda o'rgangan HAMMA narsani BITTA katta rasm sifatida
birlashtiramiz: artifact'lar (6-dars), ikkita real deploy strategiyasi
(7-dars), branch himoyasi (8-dars), reusable workflow/composite action
(9-dars), runner tanlovi (10-dars), va disk qilish (11-dars). Xuddi
5-darsdek, yangi tushuncha YO'Q — faqat mavjud bilimni "to'liq CI/CD
pipeline" ko'rinishida ko'rish.</p>

<h3>To'liq pipeline: PR'dan prod'gacha</h3>
<p>Quyidagi kod namunasida real jamoada bo'lishi mumkin bo'lgan TO'LIQ
oqim ko'rsatilgan: dasturchi feature branch ochadi -> PR yaratadi ->
<code>test.yml</code> (endi reusable workflow orqali qurilgan) ishga
tushadi -> branch protection qoidasi testlar o'tishini VA kamida bitta
reviewer tasdig'ini talab qiladi -> merge qilingach,
<code>deploy-backend.yml</code>/<code>deploy-frontend.yml</code>
avtomatik ishga tushadi -> agar biror qadam muvaffaqiyatsiz bo'lsa,
11-darsda o'rgangan diagnostika usuli qo'llaniladi.</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Agar <code>build</code> va <code>deploy</code> ikki alohida job'ga
bo'lingan bo'lsa, ular orasida fayl qanday uzatiladi?</li>
<li>Nima uchun <code>deploy-backend.yml</code> va
<code>deploy-frontend.yml</code> ikki xil deploy strategiyasidan
foydalanadi?</li>
<li>Branch protection qoidasidagi "context" nomi qayerdan olinadi, va u
o'zgarsa nima bo'ladi?</li>
<li>Composite action va reusable workflow orasidagi asosiy farq
nima?</li>
<li>Public repo'da self-hosted runner ishlatishning asosiy xavfi
nima?</li>
<li>"Permission denied (publickey)" xatosi ko'pincha nimani
anglatadi?</li>
</ul>

<h3>To'liq pipeline diagrammasi — PR'dan prod'gacha</h3>
<pre class="mermaid">
flowchart TB
  DEV["Dasturchi: feature branch
+ PR ochadi"] --> CI["test.yml
(6-dars: artifact bilan)"]
  CI --> BP{"Branch protection:
testlar + reviewer?"}
  BP -->|"Yo'q"| BLOCK["Merge bloklangan
(8-dars)"]
  BP -->|"Ha"| MERGE["Merge qilinadi
server branch'iga"]
  MERGE --> DB["deploy-backend.yml
SSH + systemctl (7-dars)"]
  MERGE --> DF["deploy-frontend.yml
build + rsync (7-dars)"]
  DB -->|"muvaffaqiyatsiz"| DEBUG["Disk qilish
(11-dars)"]
  DF -->|"muvaffaqiyatsiz"| DEBUG
  style BLOCK fill:#ffd6d6,stroke:#cc3333
  style DEBUG fill:#ffe9b3,stroke:#d09000
  style MERGE fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Diagramma 6-11-darslarning har biri qayerda ishlatilishini butun
pipeline kontekstida ko'rsatadi — bu keyingi, oxirgi capstone darsi
uchun to'liq zamin bo'lib xizmat qiladi.</p>
""".strip()

L12_TEXT_RU = """
<h3>Второе повторение — синтез уроков 6-11</h3>
<p>Это — второй и последний (перед капстоуном) урок повторения. Собираем
ВСЁ изученное в уроках 6-11 в ОДНУ большую картину: artifact'ы (урок 6),
две реальные стратегии деплоя (урок 7), защита веток (урок 8), reusable
workflow/composite action (урок 9), выбор runner'а (урок 10), и отладка
(урок 11). Как и в уроке 5, новых понятий НЕТ — только рассмотрение
существующих знаний в виде "полного CI/CD pipeline".</p>

<h3>Полный pipeline: от PR до prod</h3>
<p>В примере кода ниже показан ПОЛНЫЙ поток, возможный в реальной
команде: разработчик открывает feature-ветку -> создаёт PR ->
запускается <code>test.yml</code> (теперь построенный через reusable
workflow) -> правило branch protection требует прохождения тестов И
подтверждения минимум одного reviewer -> после merge автоматически
запускаются <code>deploy-backend.yml</code>/<code>deploy-frontend.yml</code>
-> если какой-то шаг падает, применяется метод диагностики из урока 11.</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Если <code>build</code> и <code>deploy</code> разделены на два
отдельных job'а, как между ними передаётся файл?</li>
<li>Почему <code>deploy-backend.yml</code> и
<code>deploy-frontend.yml</code> используют две разные стратегии
деплоя?</li>
<li>Откуда берётся имя "context" в правиле branch protection, и что
будет, если оно изменится?</li>
<li>В чём основная разница между composite action и reusable
workflow?</li>
<li>Каков основной риск использования self-hosted runner в публичном
репо?</li>
<li>Что чаще всего означает ошибка "Permission denied (publickey)"?</li>
</ul>

<h3>Диаграмма полного pipeline — от PR до prod</h3>
<pre class="mermaid">
flowchart TB
  DEV["Разработчик: feature-ветка
+ открывает PR"] --> CI["test.yml
(урок 6: с artifact)"]
  CI --> BP{"Branch protection:
тесты + reviewer?"}
  BP -->|"Нет"| BLOCK["Merge заблокирован
(урок 8)"]
  BP -->|"Да"| MERGE["Merge выполняется
в ветку server"]
  MERGE --> DB["deploy-backend.yml
SSH + systemctl (урок 7)"]
  MERGE --> DF["deploy-frontend.yml
build + rsync (урок 7)"]
  DB -->|"неудача"| DEBUG["Отладка
(урок 11)"]
  DF -->|"неудача"| DEBUG
  style BLOCK fill:#ffd6d6,stroke:#cc3333
  style DEBUG fill:#ffe9b3,stroke:#d09000
  style MERGE fill:#c8f7c5,stroke:#2a9d34
</pre>
<p>Диаграмма показывает, где применяется каждый из уроков 6-11 в
контексте всего pipeline — это служит полным фундаментом для
следующего, финального урока-капстоуна.</p>
""".strip()

L12_CODE = """
# ============================================================
# To'liq pipeline: har bir qismi qaysi darsdan (6-11) kelganini
# izohlarda ko'rsatadi
# ============================================================

# --- test.yml (6-dars: artifact + 9-dars: reusable workflow) ---
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    uses: ./.github/workflows/_reusable-backend-test.yml   # <- 9-dars
    with:
      python-version: "3.11"
    secrets: inherit

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest                                   # <- 10-dars: GitHub-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests
      - name: Upload test artifacts on failure                # <- 6-dars
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: frontend-test-logs
          path: frontend/coverage/

# --- Branch protection (8-dars, gh CLI orqali sozlangan) ---
# required_status_checks.contexts: ["Backend (pytest)", "Frontend (Jest)"]
# required_pull_request_reviews.required_approving_review_count: 1
# required_status_checks.strict: true (branch up-to-date bo'lishi shart)

# --- deploy-backend.yml (7-dars) ---
name: Deploy Backend
on:
  push:
    branches: [server]
    paths: ['backend/**']
concurrency:
  group: deploy-backend
  cancel-in-progress: false
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          mkdir -p ~/.ssh && printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
      - name: Deploy and verify
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
        run: |
          ssh -i ~/.ssh/deploy_key "$SSH_HOST" "systemctl restart backend && systemctl is-active --quiet backend"
          # Muvaffaqiyatsizlik holatida - 11-dars: log'ni o'qib,
          # "Permission denied" (secret muammosi) yoki "inactive"
          # (kod muammosi) ekanini aniqlash.

# ============================================================
# O'z-o'zini tekshirish savollariga qisqa javoblar
# ============================================================
# 1) actions/upload-artifact (build job'ida) + actions/download-artifact
#    (deploy job'ida), bir xil name: orqali bog'lanadi.
# 2) Backend serverda ISHLAYDI (systemd) - SSH orqali yangilanadi;
#    frontend STATIK fayl - CI'da qurilib, rsync qilinadi.
# 3) job'ning name: maydonidan; o'zgartirilsa, eski qoida hech qachon
#    mos kelmay, PR abadiy "kutilmoqda" holatida qoladi.
# 4) Composite action - step darajasida (bitta job ichida); reusable
#    workflow - butun job(lar) darajasida, o'z runner'i bilan.
# 5) Ishonchsiz tashqi PR kodi runner tarmog'ida bajarilishi mumkin.
# 6) SSH kaliti noto'g'ri/eskirgan yoki authorized_keys yangilanmagan.
""".strip()

L12_CODE_RU = """
# ============================================================
# Полный pipeline: в комментариях показано, из какого урока (6-11)
# пришла каждая часть
# ============================================================

# --- test.yml (урок 6: artifact + урок 9: reusable workflow) ---
name: Tests

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [master]

jobs:
  backend:
    uses: ./.github/workflows/_reusable-backend-test.yml   # <- урок 9
    with:
      python-version: "3.11"
    secrets: inherit

  frontend:
    name: Frontend (Jest)
    runs-on: ubuntu-latest                                   # <- урок 10: GitHub-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: npm ci --no-audit --no-fund
      - working-directory: frontend
        env:
          CI: "true"
        run: npx react-scripts test --watchAll=false --passWithNoTests
      - name: Upload test artifacts on failure                # <- урок 6
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: frontend-test-logs
          path: frontend/coverage/

# --- Branch protection (урок 8, настроено через gh CLI) ---
# required_status_checks.contexts: ["Backend (pytest)", "Frontend (Jest)"]
# required_pull_request_reviews.required_approving_review_count: 1
# required_status_checks.strict: true (ветка должна быть актуальной)

# --- deploy-backend.yml (урок 7) ---
name: Deploy Backend
on:
  push:
    branches: [server]
    paths: ['backend/**']
concurrency:
  group: deploy-backend
  cancel-in-progress: false
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure SSH
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          mkdir -p ~/.ssh && printf '%s\\n' "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
      - name: Deploy and verify
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
        run: |
          ssh -i ~/.ssh/deploy_key "$SSH_HOST" "systemctl restart backend && systemctl is-active --quiet backend"
          # При неудаче - урок 11: прочитать лог и определить, это
          # "Permission denied" (проблема secret) или "inactive"
          # (проблема в коде).

# ============================================================
# Краткие ответы на вопросы для самопроверки
# ============================================================
# 1) actions/upload-artifact (в job build) + actions/download-artifact
#    (в job deploy), связаны одинаковым name:.
# 2) Backend РАБОТАЕТ на сервере (systemd) - обновляется через SSH;
#    frontend - СТАТИЧЕСКИЕ файлы - собираются в CI, переносятся rsync.
# 3) Из поля name: job'а; если изменится, старое правило больше никогда
#    не совпадёт, и PR навсегда останется в состоянии "ожидание".
# 4) Composite action - на уровне step (внутри одного job'а); reusable
#    workflow - на уровне целого job(ов), со своим runner'ом.
# 5) Код из недоверенного внешнего PR может выполниться в сети runner'а.
# 6) SSH-ключ неверен/устарел, или authorized_keys не обновлён.
""".strip()

L12_TASK = {
    "task_title": "To'liq CI/CD pipeline sxemasini chizib, har bir bosqichni tushuntiring",
    "task_title_ru": "Нарисуйте схему полного CI/CD pipeline и объясните каждый этап",
    "task_description": (
        "Ushbu platformaning uchta workflow fayli va 6-11-darslarda "
        "o'rgangan mavzular asosida, PR ochilishidan prod serverga "
        "deploy bo'lishigacha bo'lgan TO'LIQ pipeline sxemasini chizing "
        "(qog'ozda, Mermaid'da yoki istalgan diagramma vositasida). Har "
        "bir bosqich uchun qaysi darsdan qaysi bilim ishlatilganini "
        "yozing."
    ),
    "task_description_ru": (
        "На основе трёх файлов workflow этой платформы и тем, изученных "
        "в уроках 6-11, нарисуйте ПОЛНУЮ схему pipeline от открытия PR "
        "до деплоя на prod-сервер (на бумаге, в Mermaid или любом "
        "инструменте для диаграмм). Для каждого этапа укажите, какое "
        "знание из какого урока используется."
    ),
    "task_requirements": (
        "1) Sxema kamida 6 ta bosqichni o'z ichiga olishi kerak (PR, "
        "test, branch protection, merge, ikkita deploy, xato holati). "
        "2) Har bir bosqich uchun mos dars raqami ko'rsatilgan bo'lishi "
        "shart. 3) Kamida bitta muvaffaqiyatsizlik stsenariysi va uning "
        "diagnostika yo'li ko'rsatilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Схема должна включать минимум 6 этапов (PR, тест, branch "
        "protection, merge, два деплоя, случай ошибки). 2) Для каждого "
        "этапа должен быть указан соответствующий номер урока. 3) "
        "Должен быть показан минимум один сценарий сбоя и путь его "
        "диагностики."
    ),
    "task_technologies": "GitHub Actions (full pipeline), Mermaid",
    "task_deadline_days": 5,
}

L12_SAMPLE = {
    "title": "Namuna: 6-11-darslarning barchasini birlashtirgan to'liq pipeline",
    "description": (
        "test.yml (reusable + artifact), branch protection sozlamasi "
        "va deploy-backend.yml'ni bitta hujjatda ko'rsatuvchi, "
        "izohlangan to'liq namuna."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/full-pipeline-demo.yml",
            "language": "yaml",
            "code": (
                "name: Full Pipeline Demo\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [\"**\"]\n"
                "  pull_request:\n"
                "    branches: [master]\n\n"
                "jobs:\n"
                "  backend:\n"
                "    uses: ./.github/workflows/_reusable-backend-test.yml\n"
                "    with:\n"
                "      python-version: \"3.11\"\n"
                "    secrets: inherit\n\n"
                "  frontend:\n"
                "    name: Frontend (Jest)\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-node@v4\n"
                "        with:\n"
                "          node-version: \"20\"\n"
                "          cache: npm\n"
                "          cache-dependency-path: frontend/package-lock.json\n"
                "      - working-directory: frontend\n"
                "        run: npm ci --no-audit --no-fund\n"
                "      - working-directory: frontend\n"
                "        env:\n"
                "          CI: \"true\"\n"
                "        run: npx react-scripts test --watchAll=false --passWithNoTests\n"
                "      - name: Upload test artifacts on failure\n"
                "        if: failure()\n"
                "        uses: actions/upload-artifact@v4\n"
                "        with:\n"
                "          name: frontend-test-logs\n"
                "          path: frontend/coverage/\n"
            ),
        },
    ],
}

L12_EXERCISES = [
    {
        "title": "Artifact bog'lash kaliti",
        "title_ru": "Ключ связывания artifact",
        "description": "upload-artifact va download-artifact bir-birini qanday nom orqali topadi?",
        "description_ru": "По какому имени upload-artifact и download-artifact находят друг друга?",
        "exercise_type": "multiple_choice",
        "options": ["Bir xil name: qiymati orqali", "job ID orqali", "run raqami orqali", "branch nomi orqali"],
        "options_ru": ["Через одинаковое значение name:", "Через ID job'а", "Через номер run", "Через имя ветки"],
        "correct_answers": "A",
        "hint": "6-darsda ikkala action'da ham bir xil parametr bor edi.",
        "hint_ru": "В уроке 6 у обоих action был одинаковый параметр.",
        "explanation": "name: qiymati mos kelmasa, download-artifact tegishli artifact'ni topa olmaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Ikki deploy strategiyasini eslash",
        "title_ru": "Вспомнить две стратегии деплоя",
        "description": "deploy-backend.yml serverning o'zida ishlaydi, deploy-frontend.yml esa CI'da build qiladi. Sabab nima edi?",
        "description_ru": "deploy-backend.yml работает на самом сервере, а deploy-frontend.yml собирается в CI. В чём была причина?",
        "exercise_type": "multiple_choice",
        "options": [
            "Backend - ishlaydigan xizmat, frontend - statik fayl",
            "Backend sekinroq",
            "Frontend har doim kichikroq",
            "Ular aslida bir xil",
        ],
        "options_ru": [
            "Backend — работающий сервис, frontend — статический файл",
            "Backend работает медленнее",
            "Frontend всегда меньше",
            "Они на самом деле одинаковы",
        ],
        "correct_answers": "A",
        "hint": "7-darsdagi ikki falsafani eslang.",
        "hint_ru": "Вспомните две философии из урока 7.",
        "explanation": "Ishlaydigan xizmatni serverning o'zida yangilash kerak, statik faylni esa istalgan joyda qurish mumkin.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Branch protection + reusable workflow sintezi",
        "title_ru": "Синтез branch protection + reusable workflow",
        "description": "Agar reusable workflow'dagi job nomi o'zgartirilsa, branch protection qoidasiga nima bo'ladi?",
        "description_ru": "Если имя job'а в reusable workflow изменится, что произойдёт с правилом branch protection?",
        "exercise_type": "multiple_choice",
        "options": [
            "Eski required status check nomi endi hech qachon mos kelmaydi",
            "Hech narsa o'zgarmaydi",
            "Qoida avtomatik yangilanadi",
            "Reusable workflow ishlamay qoladi",
        ],
        "options_ru": [
            "Старое имя required status check больше никогда не совпадёт",
            "Ничего не изменится",
            "Правило автоматически обновится",
            "Reusable workflow перестанет работать",
        ],
        "correct_answers": "A",
        "hint": "8-darsdagi \"context\" nomi qayerdan olinishini eslang.",
        "hint_ru": "Вспомните, откуда берётся имя \"context\" из урока 8.",
        "explanation": "Bu - 8 va 9-darslarning kesishgan nozik nuqtasi: nom o'zgarishi qoidani \"ko'rinmas\" qilib qo'yadi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Diagnostika birinchi qadami (yakuniy takror)",
        "title_ru": "Первый шаг диагностики (финальное повторение)",
        "description": "Muvaffaqiyatsiz run'ni ko'rganda birinchi navbatda nima o'qiladi: eng oxirgi qizil step'ning ___",
        "description_ru": "Что читается в первую очередь при виде неудачного run: ___ последнего красного step'а",
        "exercise_type": "fill_in_blank",
        "correct_answers": "log",
        "hint": "11-darsni eslang.",
        "hint_ru": "Вспомните 11-й урок.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 13 — Capstone: CI/CD'ni Git ichki tuzilishi bilan bog'lash
# ---------------------------------------------------------------------------

L13_TEXT = """
<h3>Ikki kursni birlashtiruvchi yakuniy loyiha</h3>
<p>112-kursda siz Git'ning ICHKI qismini (obyektlar, refs, packfile,
bisect, hook'lar) o'rgandingiz. Ushbu kursda esa GitHub Actions orqali
CI/CD QURISHNI o'rgandingiz. Capstone loyihasi ikkalasini BIRLASHTIRADI:
CI/CD pipeline'i endi shunchaki "test ishga tushirish" emas, balki Git
tarixining O'ZINI faol ravishda ishlatadigan, undan foydalanadigan
tizimga aylanadi.</p>

<h3>Vazifa 1: git bisect'ni CI'da avtomatlashtirish</h3>
<p>112-kursning 4-darsida <code>git bisect</code>ni QO'LDA ishlatishni
o'rgandingiz. Endi uni workflow ichida <code>workflow_dispatch</code>
input parametri (masalan "known_bad_sha") orqali ishga tushiring:
workflow <code>git bisect start</code>, <code>git bisect bad</code>,
<code>git bisect good &lt;oxirgi yaxshi tag&gt;</code> buyruqlarini
bajarib, har bir bisect qadamida testni ishga tushiradi va
<code>git bisect run pytest ...</code> orqali BUTUN jarayonni avtomatik
qiladi — inson qo'lda hech qanday commit'ni tekshirmaydi.</p>

<h3>Vazifa 2: pre-commit hook + CI'ning "ikki qatlamli himoya"si</h3>
<p>112-kursning 8-darsida mahalliy <code>pre-commit</code> hook va CI
orasidagi farqni o'rgandingiz: mahalliy hook <code>--no-verify</code>
bilan chetlab o'tilishi mumkin, CI esa har doim bir xil serverda
ishlaydi. Capstone'da buni AMALDA qo'llang: <code>.git/hooks/pre-commit</code>
(yoki <code>pre-commit</code> framework) orqali mahalliy tez tekshiruv
(masalan <code>black --check</code>) qo'ying, VA xuddi shu tekshiruvni
<code>test.yml</code>ga alohida job sifatida qo'shing — ikkala qatlam
BIR XIL buyruqni ishlatadi, lekin CI - yagona chetlab bo'lmaydigan
haqiqiy manba.</p>

<h3>Vazifa 3: tag/release event'iga bog'langan deploy</h3>
<p>Hozirgi <code>deploy-backend.yml</code>/<code>deploy-frontend.yml</code>
har bir <code>push</code>da ishga tushadi. 112-kursning tag bilimini
qo'llab, muqobil strategiya yarating: <code>on: push: tags:
['v*.*.*']</code> — faqat SEMVER teg (masalan <code>v1.2.0</code>)
push qilinganda deploy qiladigan workflow. Bu — "har bir commit emas,
faqat ANIQ belgilangan reliz nuqtalarida deploy qilish" (release-based
deployment) degan real amaliyot, va teglar 112-kursda o'rgangan
"annotated tag obyekti"ning to'g'ridan-to'g'ri qo'llanilishi.</p>

<h3>Vazifa 4: monorepo bilimi + matrix + paths birlashuvi</h3>
<p>112-kursning 11-darsida sparse-checkout/partial clone orqali katta
monorepo'da faqat kerakli qismni klonlashni o'rgandingiz. Ushbu kursning
1 va 3-darslaridagi <code>paths</code> filtri va <code>matrix</code>
strategiyasini birlashtirib, katta monorepo uchun "faqat o'zgargan
QISM uchun, faqat tegishli versiyada" test qiluvchi workflow loyihalang
(kontseptual — amalga oshirish shart emas, lekin YAML tuzilishi to'liq
yozilishi kerak).</p>

<h3>Capstone arxitekturasi: ikki kursning kesishuvi</h3>
<pre class="mermaid">
flowchart TB
  subgraph K112["112-kurs: Git ichki tuzilishi"]
    G1["git bisect"]
    G2["pre-commit/pre-push hook"]
    G3["annotated tag"]
    G4["sparse-checkout"]
  end
  subgraph K2["Bu kurs: GitHub Actions"]
    A1["workflow_dispatch + input"]
    A2["CI job sifatida bir xil tekshiruv"]
    A3["on: push: tags"]
    A4["matrix + paths"]
  end
  G1 -->|"avtomatlashtiriladi"| A1
  G2 -->|"ikkinchi, chetlanmas qatlam"| A2
  G3 -->|"trigger sifatida"| A3
  G4 -->|"CI strategiyasiga ko'chadi"| A4
  style K112 fill:#d6e9ff,stroke:#2266aa
  style K2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma capstone'ning markaziy g'oyasini ko'rsatadi: har bir Git
ichki tuzilish tushunchasi (chapda) CI/CD'da o'zining amaliy
qo'llanilishini (o'ngda) topadi — bu ikki kurs alohida emas, BIR yaxlit
"zamonaviy jamoaviy ishlab chiqarish" bilimining ikki yarmi ekanini
tasdiqlaydi.</p>

<h3>Nega bu to'rtta vazifa tasodifiy tanlanmagan</h3>
<p>Har bir vazifa 112-kursning ANIQ bitta darsiga to'g'ridan-to'g'ri
bog'lanadi va shu bilim CI/CD kontekstisiz "yarim tugallangan" bo'lib
qolishini ko'rsatadi: qo'lda bisect qilish ishlaydi, lekin ONLARCHA
commit bo'lsa charchatadi — avtomatlashtirish uni haqiqatan foydali
qiladi. Pre-commit hook o'zi yetarli emas — CI bo'lmasa, "ixtiyoriy"
bo'lib qoladi. Annotated tag obyekti o'zi shunchaki ma'lumot — deploy
trigger'iga aylanmaguncha, amaliy qiymati cheklangan. Sparse-checkout
o'zi disk joyini tejaydi, lekin CI strategiyasiga integratsiya qilinmasa,
uning tezlik foydasi CI vaqtida yo'qoladi. Shuning uchun capstone —
shunchaki "ikkita mavzuni birlashtirish" emas, balki HAR BIR bilim
NIMA UCHUN ikkinchisisiz to'liq emasligini ko'rsatish.</p>
""".strip()

L13_TEXT_RU = """
<h3>Финальный проект, объединяющий два курса</h3>
<p>В курсе 112 вы изучили ВНУТРЕННЕЕ устройство Git (объекты, refs,
packfile, bisect, hooks). В этом курсе вы научились СТРОИТЬ CI/CD через
GitHub Actions. Капстоун-проект ОБЪЕДИНЯЕТ оба: pipeline CI/CD теперь не
просто "запускает тесты", а становится системой, которая активно
ИСПОЛЬЗУЕТ саму историю Git.</p>

<h3>Задача 1: автоматизация git bisect в CI</h3>
<p>В уроке 4 курса 112 вы научились использовать <code>git bisect</code>
ВРУЧНУЮ. Теперь запустите его внутри workflow через входной параметр
<code>workflow_dispatch</code> (например "known_bad_sha"): workflow
выполняет команды <code>git bisect start</code>, <code>git bisect
bad</code>, <code>git bisect good &lt;последний хороший тег&gt;</code>,
запуская тест на каждом шаге bisect, и через <code>git bisect run pytest
...</code> автоматизирует ВЕСЬ процесс — человек вручную не проверяет ни
один коммит.</p>

<h3>Задача 2: "двухслойная защита" pre-commit hook + CI</h3>
<p>В уроке 8 курса 112 вы изучили разницу между локальным
<code>pre-commit</code> hook и CI: локальный hook можно обойти через
<code>--no-verify</code>, а CI всегда работает на одном и том же
сервере. Примените это НА ПРАКТИКЕ в капстоуне: через
<code>.git/hooks/pre-commit</code> (или фреймворк <code>pre-commit</code>)
добавьте локальную быструю проверку (например <code>black
--check</code>), И добавьте ТУ ЖЕ проверку как отдельный job в
<code>test.yml</code> — оба слоя используют ОДНУ И ТУ ЖЕ команду, но CI —
единственный источник истины, который нельзя обойти.</p>

<h3>Задача 3: деплой, привязанный к событию tag/release</h3>
<p>Сейчас <code>deploy-backend.yml</code>/<code>deploy-frontend.yml</code>
запускаются при каждом <code>push</code>. Применив знания о тегах из
курса 112, создайте альтернативную стратегию: <code>on: push: tags:
['v*.*.*']</code> — workflow, который деплоит только при push SEMVER-тега
(например <code>v1.2.0</code>). Это — реальная практика "деплоить не
каждый коммит, а только в чётко обозначенных точках релиза"
(release-based deployment), а теги — прямое применение "объекта
annotated tag", изученного в курсе 112.</p>

<h3>Задача 4: объединение знаний о monorepo + matrix + paths</h3>
<p>В уроке 11 курса 112 вы изучили клонирование только нужной части
большого monorepo через sparse-checkout/partial clone. Объединив фильтр
<code>paths</code> из урока 1 и стратегию <code>matrix</code> из урока 3
этого курса, спроектируйте workflow, тестирующий большой monorepo "только
изменённую ЧАСТЬ, только в нужной версии" (концептуально — реализация не
обязательна, но структура YAML должна быть полностью написана).</p>

<h3>Архитектура капстоуна: пересечение двух курсов</h3>
<pre class="mermaid">
flowchart TB
  subgraph K112["Курс 112: внутреннее устройство Git"]
    G1["git bisect"]
    G2["pre-commit/pre-push hook"]
    G3["annotated tag"]
    G4["sparse-checkout"]
  end
  subgraph K2["Этот курс: GitHub Actions"]
    A1["workflow_dispatch + input"]
    A2["одна и та же проверка как CI job"]
    A3["on: push: tags"]
    A4["matrix + paths"]
  end
  G1 -->|"автоматизируется"| A1
  G2 -->|"второй, необходимый слой"| A2
  G3 -->|"как триггер"| A3
  G4 -->|"переносится в стратегию CI"| A4
  style K112 fill:#d6e9ff,stroke:#2266aa
  style K2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает центральную идею капстоуна: каждое понятие
внутреннего устройства Git (слева) находит своё практическое применение
в CI/CD (справа) — это подтверждает, что два курса — не отдельные, а две
половины ОДНОГО целостного знания "современной командной разработки".</p>

<h3>Почему эти четыре задачи выбраны не случайно</h3>
<p>Каждая задача напрямую связана с ТОЧНО одним уроком курса 112 и
показывает, что это знание без контекста CI/CD остаётся "наполовину
завершённым": ручной bisect работает, но утомителен при ДЕСЯТКАХ
коммитов — автоматизация делает его по-настоящему полезным. Pre-commit
hook сам по себе недостаточен — без CI он остаётся "необязательным".
Объект annotated tag сам по себе — просто данные — пока не станет
триггером деплоя, его практическая ценность ограничена. Sparse-checkout
сам по себе экономит место на диске, но без интеграции в стратегию CI
его преимущество в скорости теряется во времени CI. Поэтому капстоун —
не просто "объединение двух тем", а демонстрация того, ПОЧЕМУ каждое
знание неполно без другого.</p>
""".strip()

L13_CODE = """
# ============================================================
# 1) git bisect'ni workflow_dispatch orqali avtomatlashtirish
# ============================================================
name: Automated Bisect

on:
  workflow_dispatch:
    inputs:
      good_ref:
        description: "Oxirgi ma'lum YAXSHI commit/tag (masalan v1.2.0)"
        required: true
      bad_ref:
        description: "Ma'lum YOMON commit (masalan HEAD)"
        required: true
        default: HEAD

jobs:
  bisect:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0     # <- BUTUN tarix kerak, bisect uchun shart
                              #    (112-kurs 2-darsi: packfile/gc'ni eslang)

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run automated bisect
        run: |
          git bisect start
          git bisect bad ${{ inputs.bad_ref }}
          git bisect good ${{ inputs.good_ref }}
          # git bisect run - har bir qadamda BUYRUQNI avtomatik bajaradi;
          # buyruq 0 qaytarsa "good", boshqa kod qaytarsa "bad" deb belgilaydi.
          git bisect run bash -c "cd backend && python -m pytest tests/test_regression.py -x -q"
          echo "Bisect natijasi:"
          git bisect log
          git bisect reset

# ============================================================
# 2) pre-commit hook + CI'dagi bir xil tekshiruv (112-kurs 8-darsi amaliyoti)
# ============================================================
# .pre-commit-config.yaml (mahalliy, --no-verify bilan chetlab o'tilishi mumkin)
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.11

# test.yml'ga QO'SHILGAN yangi job (chetlab bo'lmaydigan ikkinchi qatlam):
jobs:
  format-check:
    name: Black formatting (chetlab bo'lmaydigan)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install black==24.4.2
      - working-directory: backend
        run: black --check .
# Mahalliy hook TEZ, lekin --no-verify bilan o'tkazib yuborilishi mumkin.
# CI job xuddi shu buyruqni ishlatadi, lekin HECH KIM uni chetlab o'ta
# olmaydi (8-darsdagi required status check bilan birlashtirilsa).

# ============================================================
# 3) Faqat SEMVER tag push qilinganda deploy (annotated tag amaliyoti)
# ============================================================
name: Deploy Backend On Release Tag

on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'   # <- faqat v1.2.0 kabi ANIQ SEMVER teglar

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Confirm this is an annotated tag
        run: |
          git cat-file -t "$GITHUB_REF_NAME" || echo "Lightweight tag (obyekt emas)"
          # 112-kurs 0-darsi: annotated tag ALOHIDA obyekt, lightweight
          # tag esa shunchaki ref - shu farq shu yerda amaliy tekshiriladi.
      - name: Deploy (namuna)
        run: echo "Deploying release $GITHUB_REF_NAME to production"

# ============================================================
# 4) Monorepo: paths + matrix birlashuvi (kontseptual loyiha)
# ============================================================
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend_changed: ${{ steps.filter.outputs.backend }}
      frontend_changed: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend_changed == 'true'
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Faqat backend/ o'zgarganda, faqat shu versiyada test"
# Bu - 1-darsdagi paths (faqat o'zgargan qismni aniqlash) va 3-darsdagi
# matrix (bir nechta versiyada test)ning MONOREPO SHAROITIDA birlashuvi -
# 112-kurs 11-darsidagi sparse-checkout g'oyasining CI strategiyasidagi
# ekvivalenti: "faqat kerakli qismga e'tibor qaratish".
""".strip()

L13_CODE_RU = """
# ============================================================
# 1) Автоматизация git bisect через workflow_dispatch
# ============================================================
name: Automated Bisect

on:
  workflow_dispatch:
    inputs:
      good_ref:
        description: "Последний известный ХОРОШИЙ commit/tag (например v1.2.0)"
        required: true
      bad_ref:
        description: "Известный ПЛОХОЙ commit (например HEAD)"
        required: true
        default: HEAD

jobs:
  bisect:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0     # <- нужна ВСЯ история, обязательно для bisect
                              #    (вспомните урок 2 курса 112: packfile/gc)

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt

      - name: Run automated bisect
        run: |
          git bisect start
          git bisect bad ${{ inputs.bad_ref }}
          git bisect good ${{ inputs.good_ref }}
          # git bisect run - автоматически выполняет КОМАНДУ на каждом шаге;
          # если команда вернёт 0 - "good", иначе - "bad".
          git bisect run bash -c "cd backend && python -m pytest tests/test_regression.py -x -q"
          echo "Результат bisect:"
          git bisect log
          git bisect reset

# ============================================================
# 2) pre-commit hook + та же проверка в CI (практика урока 8 курса 112)
# ============================================================
# .pre-commit-config.yaml (локально, можно обойти через --no-verify)
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3.11

# НОВЫЙ job, ДОБАВЛЕННЫЙ в test.yml (второй, необходимый слой):
jobs:
  format-check:
    name: Black formatting (нельзя обойти)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install black==24.4.2
      - working-directory: backend
        run: black --check .
# Локальный hook БЫСТРЫЙ, но может быть пропущен через --no-verify.
# CI job использует ТУ ЖЕ команду, но НИКТО не может его обойти (если
# объединить с required status check из урока 8).

# ============================================================
# 3) Деплой только при push SEMVER-тега (практика annotated tag)
# ============================================================
name: Deploy Backend On Release Tag

on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'   # <- только ТОЧНЫЕ SEMVER-теги вроде v1.2.0

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Confirm this is an annotated tag
        run: |
          git cat-file -t "$GITHUB_REF_NAME" || echo "Lightweight tag (не объект)"
          # Урок 0 курса 112: annotated tag - ОТДЕЛЬНЫЙ объект, а
          # lightweight tag - просто ref - эта разница здесь проверяется
          # на практике.
      - name: Deploy (пример)
        run: echo "Deploying release $GITHUB_REF_NAME to production"

# ============================================================
# 4) Monorepo: объединение paths + matrix (концептуальный проект)
# ============================================================
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend_changed: ${{ steps.filter.outputs.backend }}
      frontend_changed: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend_changed == 'true'
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Только при изменении backend/, только на этой версии"
# Это - объединение paths (обнаружение изменённой части, урок 1) и matrix
# (тест на нескольких версиях, урок 3) В УСЛОВИЯХ MONOREPO - эквивалент
# идеи sparse-checkout из урока 11 курса 112 в стратегии CI: "уделять
# внимание только нужной части".
""".strip()

L13_TASK = {
    "task_title": "Capstone: ikki kurs bilimini birlashtirgan CI/CD loyihasi",
    "task_title_ru": "Капстоун: проект CI/CD, объединяющий знания двух курсов",
    "task_description": (
        "Shaxsiy (yoki fork qilingan) repozitoriyangizda quyidagi TO'RTTA "
        "vazifadan KAMIDA IKKITASINI to'liq amalga oshiring: (1) "
        "workflow_dispatch orqali avtomatlashtirilgan git bisect, (2) "
        "pre-commit hook + CI'da bir xil tekshiruvni ikki qatlamli qilib "
        "joriy etish, (3) faqat SEMVER tag push qilinganda ishga "
        "tushadigan deploy workflow, (4) paths+matrix birlashgan "
        "monorepo test strategiyasi (kamida YAML tuzilishi bilan). Har "
        "biri uchun 112-kursdagi qaysi bilim ishlatilganini aniq "
        "yozing."
    ),
    "task_description_ru": (
        "В своём (или форкнутом) репозитории полностью реализуйте "
        "МИНИМУМ ДВЕ из четырёх задач: (1) автоматизированный git bisect "
        "через workflow_dispatch, (2) внедрение pre-commit hook + той же "
        "проверки в CI как двухслойной защиты, (3) workflow деплоя, "
        "запускающийся только при push SEMVER-тега, (4) объединённая "
        "стратегия тестирования monorepo paths+matrix (минимум со "
        "структурой YAML). Для каждой чётко укажите, какое знание из "
        "курса 112 использовано."
    ),
    "task_requirements": (
        "1) Kamida ikkita vazifa TO'LIQ ishlaydigan (push qilib "
        "sinalgan) workflow bilan amalga oshirilgan bo'lishi kerak. 2) "
        "Har bir amalga oshirilgan vazifa uchun 112-kursdagi ANIQ dars "
        "va tushunchaga ishora qilingan bo'lishi shart. 3) Kamida bitta "
        "vazifa uchun 'nima uchun bu ikki kursni birlashtiradi' "
        "degan savolga yozma javob berilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Минимум две задачи должны быть реализованы с ПОЛНОСТЬЮ "
        "рабочим (проверенным push'ем) workflow. 2) Для каждой "
        "реализованной задачи должна быть ссылка на ТОЧНЫЙ урок и "
        "понятие из курса 112. 3) Минимум для одной задачи должен быть "
        "письменный ответ на вопрос 'почему это объединяет два курса'."
    ),
    "task_technologies": "GitHub Actions, git bisect, git tag, pre-commit, monorepo",
    "task_deadline_days": 7,
}

L13_SAMPLE = {
    "title": "Namuna: capstone'ning to'rtta vazifasini birlashtirgan repo tuzilishi",
    "description": (
        "Barcha to'rtta capstone vazifasini (bisect, ikki qatlamli "
        "tekshiruv, tag-based deploy, monorepo strategiyasi) o'z ichiga "
        "olgan fayl tuzilishi va asosiy workflow'lar namunasi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": ".github/workflows/automated-bisect.yml",
            "language": "yaml",
            "code": (
                "name: Automated Bisect\n\n"
                "on:\n"
                "  workflow_dispatch:\n"
                "    inputs:\n"
                "      good_ref:\n"
                "        required: true\n"
                "      bad_ref:\n"
                "        required: true\n"
                "        default: HEAD\n\n"
                "jobs:\n"
                "  bisect:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 30\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "        with:\n"
                "          fetch-depth: 0\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: \"3.11\"\n"
                "      - working-directory: backend\n"
                "        run: pip install -r requirements.txt\n"
                "      - name: Run bisect\n"
                "        run: |\n"
                "          git bisect start\n"
                "          git bisect bad ${{ inputs.bad_ref }}\n"
                "          git bisect good ${{ inputs.good_ref }}\n"
                "          git bisect run bash -c \"cd backend && python -m pytest tests/ -x -q\"\n"
                "          git bisect log\n"
                "          git bisect reset\n"
            ),
        },
        {
            "filename": ".github/workflows/deploy-on-release-tag.yml",
            "language": "yaml",
            "code": (
                "name: Deploy On Release Tag\n\n"
                "on:\n"
                "  push:\n"
                "    tags:\n"
                "      - 'v[0-9]+.[0-9]+.[0-9]+'\n\n"
                "jobs:\n"
                "  deploy:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - name: Verify annotated tag\n"
                "        run: git cat-file -p \"$GITHUB_REF_NAME\" | head -5\n"
                "      - name: Deploy\n"
                "        run: echo \"Deploying $GITHUB_REF_NAME\"\n"
            ),
        },
        {
            "filename": ".pre-commit-config.yaml",
            "language": "yaml",
            "code": (
                "repos:\n"
                "  - repo: https://github.com/psf/black\n"
                "    rev: 24.4.2\n"
                "    hooks:\n"
                "      - id: black\n"
                "        language_version: python3.11\n"
            ),
        },
    ],
}

L13_EXERCISES = [
    {
        "title": "git bisect'ni CI'da avtomatlashtirish uchun kerakli checkout parametri",
        "title_ru": "Параметр checkout, нужный для автоматизации git bisect в CI",
        "description": "git bisect ishlashi uchun actions/checkout'da qaysi parametr BUTUN tarixni olib kelishi kerak?",
        "description_ru": "Какой параметр в actions/checkout должен получить ВСЮ историю, чтобы работал git bisect?",
        "exercise_type": "multiple_choice",
        "options": ["fetch-depth: 0", "fetch-depth: 1", "sparse-checkout: true", "ref: bisect"],
        "options_ru": ["fetch-depth: 0", "fetch-depth: 1", "sparse-checkout: true", "ref: bisect"],
        "correct_answers": "A",
        "hint": "Standart checkout faqat oxirgi commit'ni oladi (shallow) - bisect esa butun tarixni talab qiladi.",
        "hint_ru": "Стандартный checkout берёт только последний коммит (shallow) — bisect требует всю историю.",
        "explanation": "fetch-depth: 0 to'liq (shallow bo'lmagan) tarixni olib keladi, bisect uchun zarur.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Ikki qatlamli himoyaning maqsadi",
        "title_ru": "Цель двухслойной защиты",
        "description": "Pre-commit hook VA CI'da bir xil tekshiruvni qo'shishning asosiy sababi nima?",
        "description_ru": "Какова основная причина добавления одной и той же проверки И в pre-commit hook, И в CI?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hook tezkor, lekin chetlab o'tilishi mumkin; CI esa chetlanmas yakuniy manba",
            "Ular butunlay boshqa narsalarni tekshiradi",
            "CI hookdan sekinroq, shuning uchun hook kerak emas",
            "Faqat bittasi kifoya, ikkinchisi ortiqcha",
        ],
        "options_ru": [
            "Hook быстрый, но можно обойти; CI — необходимый источник истины",
            "Они проверяют совершенно разные вещи",
            "CI медленнее hook'а, поэтому hook не нужен",
            "Достаточно одного, второй лишний",
        ],
        "correct_answers": "A",
        "hint": "112-kurs 8-darsidagi --no-verify muammosini eslang.",
        "hint_ru": "Вспомните проблему --no-verify из урока 8 курса 112.",
        "explanation": "Hook tezkor fikr-mulohaza beradi, lekin CI - hech kim chetlab o'ta olmaydigan yakuniy tekshiruv.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Annotated tag'ga asoslangan deploy",
        "title_ru": "Деплой на основе annotated tag",
        "description": "Faqat SEMVER teg push qilinganda ishga tushadigan trigger qanday yoziladi?",
        "description_ru": "Как записать триггер, запускающийся только при push SEMVER-тега?",
        "exercise_type": "multiple_choice",
        "options": [
            "on: push: tags: ['v[0-9]+.[0-9]+.[0-9]+']",
            "on: push: branches: [v*]",
            "on: release: types: [created]",
            "on: schedule: cron: 'v*'",
        ],
        "options_ru": [
            "on: push: tags: ['v[0-9]+.[0-9]+.[0-9]+']",
            "on: push: branches: [v*]",
            "on: release: types: [created]",
            "on: schedule: cron: 'v*'",
        ],
        "correct_answers": "A",
        "hint": "Teglar branch emas - alohida on: push: tags: kaliti bor.",
        "hint_ru": "Теги — не ветки, есть отдельный ключ on: push: tags:.",
        "explanation": "tags: kaliti push event'ini muayyan teg naqshiga (masalan SEMVER) cheklaydi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Ikki kursni bog'lovchi asosiy tushuncha",
        "title_ru": "Основное понятие, связывающее два курса",
        "description": "112-kursdagi git ___ buyrug'i, avtomatlashtirilganda, xatoni topish uchun CI'da ikkilik qidiruvni amalga oshiradi",
        "description_ru": "Команда git ___ из курса 112, будучи автоматизированной, выполняет двоичный поиск ошибки в CI",
        "exercise_type": "fill_in_blank",
        "correct_answers": "bisect",
        "hint": "112-kurs 4-darsining asosiy mavzusi.",
        "hint_ru": "Главная тема 4-го урока курса 112.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# LESSONS assembly
# ---------------------------------------------------------------------------

LESSONS = [
    {
        "order": 0,
        "title": "GitHub Actions asoslari: workflow YAML anatomiyasi",
        "title_ru": "Основы GitHub Actions: анатомия YAML workflow",
        "points_reward": 15,
        "text_content": L0_TEXT,
        "text_content_ru": L0_TEXT_RU,
        "code_content": L0_CODE,
        "code_content_ru": L0_CODE_RU,
        "code_language": "yaml",
        "task": L0_TASK,
        "sample": L0_SAMPLE,
        "exercises": L0_EXERCISES,
    },
    {
        "order": 1,
        "title": "Trigger'lar va event'lar: push, pull_request, schedule, workflow_dispatch",
        "title_ru": "Триггеры и события: push, pull_request, schedule, workflow_dispatch",
        "points_reward": 15,
        "text_content": L1_TEXT,
        "text_content_ru": L1_TEXT_RU,
        "code_content": L1_CODE,
        "code_content_ru": L1_CODE_RU,
        "code_language": "yaml",
        "task": L1_TASK,
        "sample": L1_SAMPLE,
        "exercises": L1_EXERCISES,
    },
    {
        "order": 2,
        "title": "Secrets va environment o'zgaruvchilari",
        "title_ru": "Secrets и переменные окружения",
        "points_reward": 15,
        "text_content": L2_TEXT,
        "text_content_ru": L2_TEXT_RU,
        "code_content": L2_CODE,
        "code_content_ru": L2_CODE_RU,
        "code_language": "yaml",
        "task": L2_TASK,
        "sample": L2_SAMPLE,
        "exercises": L2_EXERCISES,
    },
    {
        "order": 3,
        "title": "Matrix build'lar: bir nechta versiyada parallel test",
        "title_ru": "Matrix build: параллельное тестирование на нескольких версиях",
        "points_reward": 15,
        "text_content": L3_TEXT,
        "text_content_ru": L3_TEXT_RU,
        "code_content": L3_CODE,
        "code_content_ru": L3_CODE_RU,
        "code_language": "yaml",
        "task": L3_TASK,
        "sample": L3_SAMPLE,
        "exercises": L3_EXERCISES,
    },
    {
        "order": 4,
        "title": "Cache'lash: actions/cache, pip/npm keshlash",
        "title_ru": "Кеширование: actions/cache, кеширование pip/npm",
        "points_reward": 15,
        "text_content": L4_TEXT,
        "text_content_ru": L4_TEXT_RU,
        "code_content": L4_CODE,
        "code_content_ru": L4_CODE_RU,
        "code_language": "yaml",
        "task": L4_TASK,
        "sample": L4_SAMPLE,
        "exercises": L4_EXERCISES,
    },
    {
        "order": 5,
        "title": "R1 — Takrorlash: asoslar, trigger, secrets, matrix, cache",
        "title_ru": "R1 — Повторение: основы, триггеры, secrets, matrix, cache",
        "points_reward": 20,
        "text_content": L5_TEXT,
        "text_content_ru": L5_TEXT_RU,
        "code_content": L5_CODE,
        "code_content_ru": L5_CODE_RU,
        "code_language": "yaml",
        "task": L5_TASK,
        "sample": L5_SAMPLE,
        "exercises": L5_EXERCISES,
    },
    {
        "order": 6,
        "title": "Artifact'lar va build natijalari",
        "title_ru": "Артефакты и результаты сборки",
        "points_reward": 15,
        "text_content": L6_TEXT,
        "text_content_ru": L6_TEXT_RU,
        "code_content": L6_CODE,
        "code_content_ru": L6_CODE_RU,
        "code_language": "yaml",
        "task": L6_TASK,
        "sample": L6_SAMPLE,
        "exercises": L6_EXERCISES,
    },
    {
        "order": 7,
        "title": "Real deploy: deploy-backend.yml va deploy-frontend.yml",
        "title_ru": "Реальный деплой: deploy-backend.yml и deploy-frontend.yml",
        "points_reward": 20,
        "text_content": L7_TEXT,
        "text_content_ru": L7_TEXT_RU,
        "code_content": L7_CODE,
        "code_content_ru": L7_CODE_RU,
        "code_language": "yaml",
        "task": L7_TASK,
        "sample": L7_SAMPLE,
        "exercises": L7_EXERCISES,
    },
    {
        "order": 8,
        "title": "Branch himoya qoidalari va required status check'lar",
        "title_ru": "Правила защиты веток и required status checks",
        "points_reward": 15,
        "text_content": L8_TEXT,
        "text_content_ru": L8_TEXT_RU,
        "code_content": L8_CODE,
        "code_content_ru": L8_CODE_RU,
        "code_language": "bash",
        "task": L8_TASK,
        "sample": L8_SAMPLE,
        "exercises": L8_EXERCISES,
    },
    {
        "order": 9,
        "title": "Qayta ishlatiladigan workflow'lar va composite action'lar",
        "title_ru": "Reusable workflows и composite actions",
        "points_reward": 15,
        "text_content": L9_TEXT,
        "text_content_ru": L9_TEXT_RU,
        "code_content": L9_CODE,
        "code_content_ru": L9_CODE_RU,
        "code_language": "yaml",
        "task": L9_TASK,
        "sample": L9_SAMPLE,
        "exercises": L9_EXERCISES,
    },
    {
        "order": 10,
        "title": "Self-hosted vs GitHub-hosted runner'lar",
        "title_ru": "Self-hosted против GitHub-hosted runner",
        "points_reward": 15,
        "text_content": L10_TEXT,
        "text_content_ru": L10_TEXT_RU,
        "code_content": L10_CODE,
        "code_content_ru": L10_CODE_RU,
        "code_language": "yaml",
        "task": L10_TASK,
        "sample": L10_SAMPLE,
        "exercises": L10_EXERCISES,
    },
    {
        "order": 11,
        "title": "Muvaffaqiyatsiz CI'ni disk qilish: log'lar, qayta ishga tushirish, keng tarqalgan xatolar",
        "title_ru": "Отладка неудачного CI: логи, повторный запуск, распространённые ошибки",
        "points_reward": 15,
        "text_content": L11_TEXT,
        "text_content_ru": L11_TEXT_RU,
        "code_content": L11_CODE,
        "code_content_ru": L11_CODE_RU,
        "code_language": "bash",
        "task": L11_TASK,
        "sample": L11_SAMPLE,
        "exercises": L11_EXERCISES,
    },
    {
        "order": 12,
        "title": "R2 — Takrorlash: artifact'lar, deploy, branch himoyasi, reusable, runner, disk qilish",
        "title_ru": "R2 — Повторение: артефакты, деплой, защита веток, reusable, runner, отладка",
        "points_reward": 20,
        "text_content": L12_TEXT,
        "text_content_ru": L12_TEXT_RU,
        "code_content": L12_CODE,
        "code_content_ru": L12_CODE_RU,
        "code_language": "yaml",
        "task": L12_TASK,
        "sample": L12_SAMPLE,
        "exercises": L12_EXERCISES,
    },
    {
        "order": 13,
        "title": "Capstone: CI/CD'ni Git ichki tuzilishi bilan bog'lash",
        "title_ru": "Капстоун: связь CI/CD с внутренним устройством Git",
        "points_reward": 30,
        "text_content": L13_TEXT,
        "text_content_ru": L13_TEXT_RU,
        "code_content": L13_CODE,
        "code_content_ru": L13_CODE_RU,
        "code_language": "yaml",
        "task": L13_TASK,
        "sample": L13_SAMPLE,
        "exercises": L13_EXERCISES,
    },
]

# max_points = sum of lesson points_reward + all exercise points + all task
# "completion" points. This course's submission tasks aren't separately
# points-scored beyond the lesson's points_reward (same convention as
# course 112) — so max_points = lessons points_reward + exercise points.
_lesson_points = sum(l.get("points_reward", 10) for l in LESSONS)
_exercise_points = sum(
    ex.get("points", 10) for l in LESSONS for ex in (l.get("exercises") or [])
)
COURSE["max_points"] = _lesson_points + _exercise_points
