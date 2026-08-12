"""Course 3 of 3 in the "Git & collaboration workflows" track: the human/
team-process layer that sits on top of Git internals (course 112) and
CI/CD (course 117).

Course 112 ("Git: Ichki Tuzilishi va Ilg'or Workflow") taught how Git
actually stores and manipulates history: objects/SHA-1, refs, packfiles,
interactive rebase, bisect, worktree, submodule/subtree, hooks, rerere,
monorepo sparse-checkout. Course 117 ("GitHub Actions va CI/CD Chuqur")
taught how to build the automated pipeline around that history: workflow
anatomy, triggers, secrets, matrix builds, caching, artifacts, real
deploy (grounded in this repo's own .github/workflows/*.yml), branch
protection, reusable workflows, runners, CI debugging. Neither course
touches the HUMAN side of shipping code as a team: how a change actually
gets from "I wrote it" to "it's in production and everyone trusts it" —
writing a description another human can review, committing in a way that
tells a story, reviewing someone else's work well, giving and receiving
feedback without friction, choosing a merge strategy, and versioning +
releasing what ships. That gap is this course.

Grounded throughout in this repo's OWN real artifacts rather than
invented examples:
  - `git log --oneline` — this repo's actual Conventional Commits history
    (feat/fix/refactor/chore/docs/test/perf/ci, real scopes, real bodies)
    is used directly as teaching material for commit-message-quality and
    PR-description-quality lessons. Confirmed via `git log --merges`: this
    repo has ZERO merge commits (a single-maintainer linear history) and
    zero tags and no CHANGELOG/CONTRIBUTING/CODEOWNERS/PR-template files —
    lessons say so explicitly rather than pretending those exist, and use
    that as the honest starting point for "here's how you'd introduce
    this practice into a repo like this one."
  - `.github/workflows/test.yml` / `deploy-backend.yml` / `deploy-frontend.yml`
    (already used in course 117) are referenced again where the human
    process intersects with CI (e.g. required checks vs human review;
    tag-triggered release deploys).

Built with the course_builder scaffold — see course_builder/__init__.py
for the spec contract. Every lesson gets both task + sample from the
start (same convention course 117 established: the spec docstring says
task/sample are "only for review/capstone lessons" but every course built
so far gives every lesson both), full UZ+RU authored here directly (not
machine-translated), Mermaid diagrams where pedagogically justified.
is_published stays False — human review first.
"""

COURSE = {
    "title": "Jamoaviy Ish Madaniyati: Code Review va Versiyalash",
    "description": (
        "112-kurs Git'ning ICHKI qismini, 117-kurs esa GitHub Actions "
        "orqali CI/CD QURISHNI o'rgatdi. Ikkalasi ham muhim, lekin ikkalasi "
        "ham kod QANDAY qilib bir kishidan butun jamoaga, ishonchli holatda "
        "yetib borishini tushuntirmaydi. Ushbu kurs aynan shu inson "
        "qatlamini yopadi: boshqa dasturchi tushunadigan pull request "
        "tavsifini yozish, tarixni o'qish mumkin bo'lgan commit xabarlarini "
        "yozish (ushbu platformaning real git tarixi asosida), boshqa "
        "odamning kodini samarali va xolisona ko'rib chiqish, "
        "fikr-mulohazani aniq va samimiy berish hamda uni ego'siz qabul "
        "qilish, jamoa uchun to'g'ri merge strategiyasini tanlash, "
        "semantik versiyalash va o'zgarishlar jurnali (changelog) yuritish, "
        "va nihoyat — reliz teglash orqali buni CI/CD trigger'iga "
        "bog'lash. Kurs 112 va 117-kurslarning bilimlarini birlashtirgan "
        "yakuniy capstone loyiha bilan tugaydi: bitta xususiyatni to'liq "
        "jamoaviy workflow orqali — atomik commit'lardan tortib, reliz "
        "teglashgacha — \"yetkazish\"."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 5,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 11,
    "prerequisite_course_id": 117,
    "display_order": 603,
    "image_url": "https://raw.githubusercontent.com/primer/octicons/main/icons/code-review-24.svg",
    "thumbnail_url": "https://raw.githubusercontent.com/primer/octicons/main/icons/git-pull-request-24.svg",
    "is_active": True,
    "is_published": False,
}

# ---------------------------------------------------------------------------
# Lesson 0 — Code review nima va nima uchun kerak
# ---------------------------------------------------------------------------

L0_TEXT = """
<h3>Nima uchun Git va CI/CD'dan keyin yana bir kurs kerak</h3>
<p>112-kursda siz Git'ning ichki tuzilishini, 117-kursda esa GitHub Actions
orqali avtomatik test va deploy qurishni o'rgandingiz. Ikkalasi ham
"mashina" tomonini yopadi: kod qanday saqlanadi, qanday avtomatik
tekshiriladi. Lekin real jamoada bitta savol ochiq qoladi — <code>git
push</code> qilingandan keyin, CI yashil bo'lgandan keyin, kod hali ham
darhol <code>main</code>'ga qo'shilmaydi. Avval boshqa INSON uni ko'rib
chiqadi. Bu jarayon — <strong>code review</strong> (kodni ko'rib
chiqish) — texnik emas, <em>jamoaviy</em> amaliyot, va aynan shu narsa
ushbu kursning mavzusi.</p>

<h3>Code review nima uchun kerak — uchta haqiqiy sabab</h3>
<p>Ko'p yangi dasturchilar code review'ni "boshqa birov mening kodimni
tekshiradi, xato qilsam meni ushlaydi" deb, ya'ni faqat nazorat
(gatekeeping) sifatida tushunadi. Bu — eng kichik va eng kam foydali
sabab. Haqiqiy sabablar uchta:</p>
<ul>
<li><strong>Xatolarni ishlab chiqarishdan OLDIN ushlash.</strong> CI
(117-kurs) faqat SIZ yozgan testlar tekshirgan narsani topadi. Inson
review'i esa testda yo'q narsani ko'radi: "bu funksiya <code>None</code>
kelsa nima bo'ladi?", "bu so'rov N+1 muammosiga olib kelmaydimi?" —
mantiqiy, testda hali qamrab olinmagan xatolar.</li>
<li><strong>Bilim almashish.</strong> Review — kodni faqat tekshirish
emas, balki jamoa a'zolari bir-birining kodini O'QISH orqali loyihaning
turli qismlarini o'rganishi. Yangi qo'shilgan dasturchi review orqali
kodni yozmasdan turib kod bazasi konventsiyalarini o'rganadi; tajribali
dasturchi review orqali yangi qismlarda nima o'zgarganini kuzatib boradi
— bu "bus factor"ni (bitta odam ketib qolsa loyiha to'xtab qolish xavfi)
kamaytiradi.</li>
<li><strong>Standart va izchillikni saqlash.</strong> Har bir dasturchi
o'zicha nom qo'ysa, o'zicha struktura tanlasa, kod bazasi vaqt o'tishi
bilan parchalanib ketadi. Review — jamoa qaror qilgan konventsiyalarni
(masalan shu kursning 2-darsida ko'radigan commit format) amalda
saqlashning asosiy mexanizmi.</li>
</ul>
<p>Muhim: <strong>uslub</strong> (formatlash, qavs joylashuvi) review
vaqtini band qilmasligi kerak — bu avtomatlashtiriladigan narsa (linter,
formatter), inson e'tibori esa <em>mantiq, xavfsizlik, o'qilishi</em>
kabi avtomatlashtirib bo'lmaydigan narsalarga sarflanishi kerak. Buni
4-darsda batafsil ko'ramiz.</p>

<h3>Real misol: review nimani ushlab qolishi mumkin edi</h3>
<p>Ushbu platformaning o'z tarixida <code>e6c19f2 fix: correct
multiple_choice grading and project points display</code> commit'i bor.
Commit tavsifidan: <code>exercise_service.py</code>da bitta xato bor edi —
bitta variantli (single-select) savollarda <code>correct_answers</code>
har doim vergul bo'yicha bo'linar edi, hatto to'g'ri javob matnining
o'zi ichida vergul bo'lsa ham. Natijada A-D orasidagi HAR QANDAY javob
"noto'g'ri" deb baholangan — bu xato "bir nechta kurs va talabaning real
javoblari orqali tasdiqlangan", ya'ni ISHLAB CHIQARISHGA yetib borgan.
Agar shu o'zgarish merge qilinishidan oldin kimdir "vergul bo'yicha
bo'lish nafaqat ko'p tanlovli, balki BARCHA holatlarda ishlaydimi?" deb
so'ragan bo'lsa, bu xato talabalarga yetib borishidan OLDIN tutilgan
bo'lardi. Bu — code review'ning eng aniq foydasi: sinov (test) qamrab
olmagan chekka holatni, ikkinchi juftlik ko'z orqali topish.</p>

<h3>Code review — darvozabon emas, xavfsizlik to'ri</h3>
<p>"Gatekeeping" fikri review'ni "meniki tasdiqlanmasa, ishim yomon"
degan ziddiyatli munosabatga aylantiradi. To'g'ri fikrlash: review —
CI kabi xavfsizlik qatlami, lekin AVTOMATLASHTIRIB bo'lmaydigan narsalar
uchun. CI "test.yml o'tdimi?" degan savolga javob beradi; review "bu
YECHIM to'g'rimi, o'qilishi osonmi, xavfsizmi?" degan savolga javob
beradi. Ikkalasi ham bir xil maqsadga xizmat qiladi — MUVAFFAQIYATSIZ
kodni production'ga yetkazmaslik — lekin turli vositalar bilan.</p>

<h3>Bitta PR/MR'ning hayot yo'li</h3>
<pre class="mermaid">
flowchart LR
  D["Draft
(hali tayyor emas)"] --> RR["Review so'ralgan
(Ready for review)"]
  RR --> CR{"Reviewer
ko'rib chiqadi"}
  CR -->|"o'zgarish kerak"| CH["Changes requested"]
  CH -->|"muallif tuzatadi"| RR
  CR -->|"hammasi joyida"| AP["Approved"]
  AP --> M["Merged"]
  style D fill:#eeeeee,stroke:#888888
  style CH fill:#ffd6d6,stroke:#cc3333
  style AP fill:#d6f5d6,stroke:#2a8a2a
  style M fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Diagramma har bir PR/MR (pull request/merge request) o'tadigan besh
holatni ko'rsatadi. E'tibor bering: <code>Changes requested</code> —
DEADLOCK emas, balki oddiy tsikl — muallif tuzatadi, qayta so'raydi, va
reviewer yana ko'radi. Bu tsikl bir necha marta takrorlanishi mumkin va
bu NORMAL holat, muvaffaqiyatsizlik emas. Ushbu kurs davomida siz shu
diagrammaning HAR BIR bosqichini chuqur o'rganasiz: qanday PR tavsifi
"Ready for review"ni haqiqatan tayyor qiladi (1-dars), qanday commit
tarixi review'ni osonlashtiradi (2-3-dars), reviewer sifatida nimaga
e'tibor berish kerak (4-dars), qanday fikr-mulohaza berish va qabul
qilish (6-7-dars), va nihoyat — <code>Merged</code>dan keyin nima
bo'ladi: qaysi merge strategiyasi, qanday versiyalash va reliz (8-11-dars).</p>

<h3>Bu kurs 112 va 117-kurslardan nimasi bilan farq qiladi</h3>
<p>112-kurs savoli: "Git ICHKARIDA qanday ishlaydi?" 117-kurs savoli:
"Kod qanday AVTOMATIK tekshiriladi va joylanadi?" Bu kursning savoli:
"Odamlar bir-birining kodi ustida qanday ISHONCHLI hamkorlik qiladi?"
Uchalasi ham bir xil pipeline'ning turli qatlamlari — capstone loyihada
(13-dars) barcha uchalasi bitta real ssenariyoda birlashadi.</p>
""".strip()

L0_TEXT_RU = """
<h3>Зачем ещё один курс после Git и CI/CD</h3>
<p>В курсе 112 вы изучили внутреннее устройство Git, а в курсе 117 —
построение автоматических тестов и деплоя через GitHub Actions. Оба курса
закрывают "машинную" сторону: как хранится код, как он автоматически
проверяется. Но в реальной команде остаётся один открытый вопрос — после
<code>git push</code>, даже когда CI зелёный, код не сразу попадает в
<code>main</code>. Сначала его смотрит другой ЧЕЛОВЕК. Этот процесс —
<strong>code review</strong> (ревью кода) — это не техническая, а
<em>командная</em> практика, и именно она — тема этого курса.</p>

<h3>Зачем нужно код-ревью — три реальные причины</h3>
<p>Многие новые разработчики понимают code review как "кто-то проверяет
мой код, поймает меня на ошибке", то есть только как контроль
(gatekeeping). Это — наименее полезная причина. Настоящих причин три:</p>
<ul>
<li><strong>Поймать ошибки ДО продакшена.</strong> CI (курс 117) находит
только то, что покрыто вашими собственными тестами. Ревью человека видит
то, чего нет в тесте: "что будет, если сюда придёт <code>None</code>?",
"этот запрос не приведёт к проблеме N+1?" — логические ошибки, ещё не
покрытые тестами.</li>
<li><strong>Обмен знаниями.</strong> Ревью — это не только проверка кода,
но и способ, которым члены команды изучают части проекта, ЧИТАЯ код друг
друга. Новый разработчик через ревью изучает конвенции кодовой базы, не
написав ни строчки; опытный разработчик через ревью следит за тем, что
меняется в незнакомых частях — это снижает "bus factor" (риск остановки
проекта, если один человек уйдёт).</li>
<li><strong>Поддержание стандарта и согласованности.</strong> Если каждый
разработчик называет и структурирует код по-своему, кодовая база со
временем распадается. Ревью — основной механизм, которым команда реально
поддерживает согласованные конвенции (например, формат коммитов, который
мы увидим в уроке 2).</li>
</ul>
<p>Важно: <strong>стиль</strong> (форматирование, расположение скобок) не
должен занимать время ревью — это автоматизируется (linter, formatter),
а внимание человека должно тратиться на то, что автоматизировать нельзя:
<em>логику, безопасность, читаемость</em>. Подробно рассмотрим это в
уроке 4.</p>

<h3>Реальный пример: что могло бы поймать ревью</h3>
<p>В собственной истории этой платформы есть коммит <code>e6c19f2 fix:
correct multiple_choice grading and project points display</code>. Из
описания коммита: в <code>exercise_service.py</code> была ошибка — для
вопросов с одним правильным ответом (single-select) <code>correct_answers</code>
всегда разбивался по запятой, даже если сам текст правильного ответа
содержал запятую. В результате ЛЮБОЙ ответ между A-D оценивался как
"неверный" — эта ошибка была "подтверждена через реальные ответы
нескольких курсов и студентов", то есть дошла до ПРОДАКШЕНА. Если бы
перед merge кто-то спросил "разбиение по запятой работает не только для
множественного выбора, но и во ВСЕХ случаях?", эта ошибка была бы
поймана ДО того, как дошла до студентов. Это — самая наглядная польза
code review: находить граничный случай, не покрытый тестом, вторым
взглядом.</p>

<h3>Code review — не привратник, а сеть безопасности</h3>
<p>Идея "gatekeeping" превращает ревью в противоречивое отношение "если
моё не одобрили, значит моя работа плоха". Правильный взгляд: ревью —
такой же слой безопасности, как CI, но для того, что НЕЛЬЗЯ
автоматизировать. CI отвечает на вопрос "прошёл ли test.yml?"; ревью
отвечает на вопрос "это РЕШЕНИЕ правильное, легко ли читается,
безопасно ли?". Оба служат одной цели — не пропустить неудачный код в
продакшен — но разными инструментами.</p>

<h3>Жизненный путь одного PR/MR</h3>
<pre class="mermaid">
flowchart LR
  D["Draft
(ещё не готово)"] --> RR["Запрошено ревью
(Ready for review)"]
  RR --> CR{"Reviewer
проверяет"}
  CR -->|"нужны изменения"| CH["Changes requested"]
  CH -->|"автор исправляет"| RR
  CR -->|"всё в порядке"| AP["Approved"]
  AP --> M["Merged"]
  style D fill:#eeeeee,stroke:#888888
  style CH fill:#ffd6d6,stroke:#cc3333
  style AP fill:#d6f5d6,stroke:#2a8a2a
  style M fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Диаграмма показывает пять состояний, через которые проходит каждый
PR/MR (pull request/merge request). Обратите внимание: <code>Changes
requested</code> — это не тупик, а обычный цикл — автор исправляет,
запрашивает снова, и reviewer проверяет ещё раз. Этот цикл может
повториться несколько раз, и это НОРМАЛЬНОЕ состояние, а не неудача. В
этом курсе вы глубоко изучите КАЖДЫЙ этап этой диаграммы: какое описание
PR реально делает его "Ready for review" (урок 1), какая история
коммитов облегчает ревью (уроки 2-3), на что обращать внимание в роли
reviewer (урок 4), как давать и принимать обратную связь (уроки 6-7), и,
наконец, что происходит после <code>Merged</code>: какая стратегия
merge, версионирование и релиз (уроки 8-11).</p>

<h3>Чем этот курс отличается от курсов 112 и 117</h3>
<p>Вопрос курса 112: "Как Git устроен ВНУТРИ?" Вопрос курса 117: "Как код
автоматически проверяется и деплоится?" Вопрос этого курса: "Как люди
НАДЁЖНО сотрудничают над кодом друг друга?" Все три — разные слои одного
и того же pipeline — в капстоуне (урок 13) все три объединятся в одном
реальном сценарии.</p>
""".strip()

L0_CODE = """
# ============================================================
# Real misol: e6c19f2 commit tavsifidan (bu platformaning o'z
# git tarixi) - review nimani ushlab qolishi mumkin edi
# ============================================================

# --- MUAMMOLI KOD (merge qilingunga qadar hech kim savol bermagan) ---
def check_multiple_choice(exercise, student_answer):
    correct = exercise.correct_answers          # masalan: "Konsolga chiqaradi, aniq"
    correct_list = correct.split(",")           # <- HAR DOIM vergul bo'yicha boladi
    student_list = student_answer.split(",")
    return set(correct_list) == set(student_list)

# Agar to'g'ri javob matnining o'zida vergul bo'lsa (yuqoridagi misolda
# "Konsolga chiqaradi, aniq"), u ikkita bo'lakka bo'linadi:
#   ["Konsolga chiqaradi", " aniq"]
# Talaba xuddi shu variantni TO'LIQ tanlagan bo'lsa ham (bitta string
# sifatida), taqqoslash hech qachon mos kelmaydi - javob DOIM "noto'g'ri"
# deb belgilanadi, talaba nima tanlashidan qat'i nazar.

# --- TUZATILGAN KOD (commit e6c19f2'dan keyin) ---
def check_multiple_choice_fixed(exercise, student_answer):
    if exercise.is_multiple_select:
        correct_list = exercise.correct_answers.split(",")
        student_list = student_answer.split(",")
        return set(correct_list) == set(student_list)
    # Bitta tanlovli savolda MATNNI BUTUNLIGICHA solishtiramiz,
    # ichidagi vergulga qaramasdan
    return exercise.correct_answers.strip() == student_answer.strip()

# ============================================================
# Review paytida so'ralishi kerak bo'lgan savol (agar berilganida,
# bu xato ishlab chiqarishga yetib bormagan bo'lardi):
#
#   "correct_answers'ni vergul bo'yicha bo'lish nafaqat ko'p
#    tanlovli (is_multiple_select=True), balki BARCHA holatlar
#    uchun to'g'rimi? Bitta tanlovli javob matnida vergul bo'lsa
#    nima bo'ladi?"
#
# Bu savol CI (test.yml) tomonidan AVTOMATIK berilmaydi - faqat
# mavjud testlar tekshirgan holatlarni tasdiqlaydi. Yangi chekka
# holatni o'ylab topish - aynan inson review'ining vazifasi.
# ============================================================
""".strip()

L0_CODE_RU = """
# ============================================================
# Реальный пример: из описания коммита e6c19f2 (собственная
# git-история этой платформы) - что могло бы поймать ревью
# ============================================================

# --- ПРОБЛЕМНЫЙ КОД (никто не задал вопрос до merge) ---
def check_multiple_choice(exercise, student_answer):
    correct = exercise.correct_answers          # например: "Выводит в консоль, точно"
    correct_list = correct.split(",")           # <- ВСЕГДА разбивается по запятой
    student_list = student_answer.split(",")
    return set(correct_list) == set(student_list)

# Если сам текст правильного ответа содержит запятую (как в примере
# выше "Выводит в консоль, точно"), он разбивается на два куска:
#   ["Выводит в консоль", " точно"]
# Даже если студент выбрал ИМЕННО этот вариант целиком (как одну
# строку), сравнение никогда не совпадёт - ответ ВСЕГДА помечается
# как "неверный", независимо от выбора студента.

# --- ИСПРАВЛЕННЫЙ КОД (после коммита e6c19f2) ---
def check_multiple_choice_fixed(exercise, student_answer):
    if exercise.is_multiple_select:
        correct_list = exercise.correct_answers.split(",")
        student_list = student_answer.split(",")
        return set(correct_list) == set(student_list)
    # Для вопроса с одним выбором сравниваем ВЕСЬ текст целиком,
    # не обращая внимания на запятую внутри
    return exercise.correct_answers.strip() == student_answer.strip()

# ============================================================
# Вопрос, который должен был быть задан на ревью (если бы его
# задали, эта ошибка не дошла бы до продакшена):
#
#   "Разбиение correct_answers по запятой верно не только для
#    множественного выбора (is_multiple_select=True), но и для
#    ВСЕХ случаев? Что если в тексте ответа с одним выбором есть
#    запятая?"
#
# Этот вопрос НЕ задаётся CI (test.yml) автоматически - он лишь
# подтверждает случаи, уже покрытые существующими тестами. Придумать
# новый граничный случай - именно задача ревью человеком.
# ============================================================
""".strip()

L0_TASK = {
    "task_title": "GitHub'dagi ochiq PR'ning hayot yo'lini tahlil qiling",
    "task_title_ru": "Проанализируйте жизненный путь открытого PR на GitHub",
    "task_description": (
        "Har qanday mashhur ochiq-manba (open source) loyihadan (masalan "
        "GitHub'da qidiruv orqali topilgan, kamida 10 ta izohli PR) YOPILGAN "
        "(closed/merged) bitta pull request tanlang. Uning \"Conversation\" "
        "va \"Commits\" bo'limlarini o'qib, quyidagilarni yozma ravishda "
        "hujjatlashtiring: (1) PR qachon \"Ready for review\" belgilangan "
        "(agar Draft bo'lgan bo'lsa), (2) nechta \"changes requested\" tsikli "
        "bo'lgan va har birida nima so'ralgan, (3) nima uchun oxir-oqibat "
        "\"Approved\" bo'lgan, (4) sizningcha shu review qanday xatoni yoki "
        "muammoni ushlab qolgan (agar ushlagan bo'lsa)."
    ),
    "task_description_ru": (
        "Выберите один ЗАКРЫТЫЙ (closed/merged) pull request из любого "
        "популярного open source проекта (например, найденного через поиск "
        "на GitHub, минимум с 10 комментариями). Прочитайте его разделы "
        "\"Conversation\" и \"Commits\" и письменно задокументируйте: (1) "
        "когда PR был помечен \"Ready for review\" (если был Draft), (2) "
        "сколько было циклов \"changes requested\" и что запрашивалось в "
        "каждом, (3) почему в итоге он был \"Approved\", (4) какую ошибку "
        "или проблему, по вашему мнению, поймало это ревью (если поймало)."
    ),
    "task_requirements": (
        "1) Havola (link) tanlangan PR'ga ilova qilinishi shart. 2) Har bir "
        "4 ta savolga kamida 2-3 gapdan iborat javob. 3) Diagrammadagi "
        "besh holatning kamida uchtasi (Draft/Review requested/Changes "
        "requested/Approved/Merged) shu PR misolida aniq ko'rsatilgan "
        "bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Обязательно приложить ссылку на выбранный PR. 2) На каждый из 4 "
        "вопросов - ответ минимум из 2-3 предложений. 3) Минимум три из пяти "
        "состояний диаграммы (Draft/Review requested/Changes "
        "requested/Approved/Merged) должны быть чётко показаны на примере "
        "этого PR."
    ),
    "task_technologies": "GitHub (Pull Requests), yozma tahlil",
    "task_deadline_days": 3,
}

L0_SAMPLE = {
    "title": "Namuna: bitta xato, ikki holat - review bilan va reviewsiz",
    "description": (
        "Ushbu darsning kod namunasi asosida, e6c19f2 commit tavsifidagi "
        "haqiqiy xatoni ikkita holatda ko'rsatadi: review qilinmagan (xato "
        "production'ga yetib borgan) va agar review qilingan bo'lsa (xato "
        "merge'dan oldin ushlangan) qanday ko'rinishda bo'lishi. Ikkalasi "
        "ham to'liq ishlaydigan Python fayllari sifatida."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "before_review.py",
            "language": "python",
            "code": (
                "\"\"\"Review'dan o'tmagan holat - haqiqiy production bug.\"\"\"\n\n"
                "def check_multiple_choice(exercise, student_answer):\n"
                "    correct = exercise.correct_answers\n"
                "    correct_list = correct.split(\",\")\n"
                "    student_list = student_answer.split(\",\")\n"
                "    return set(correct_list) == set(student_list)\n\n"
                "# Sinov: to'g'ri javob matnida vergul bo'lsa\n"
                "class FakeExercise:\n"
                "    correct_answers = \"Konsolga chiqaradi, aniq\"\n\n"
                "result = check_multiple_choice(FakeExercise(), \"Konsolga chiqaradi, aniq\")\n"
                "print(f\"Talaba to'liq to'g'ri javobni tanladi, natija: {result}\")\n"
                "# Natija: False - talaba TO'G'RI javobni tanlagan bo'lsa ham!\n"
            ),
        },
        {
            "filename": "after_review.py",
            "language": "python",
            "code": (
                "\"\"\"Agar review paytida savol berilganida - to'g'ri yechim.\"\"\"\n\n"
                "def check_multiple_choice(exercise, student_answer):\n"
                "    if exercise.is_multiple_select:\n"
                "        correct_list = exercise.correct_answers.split(\",\")\n"
                "        student_list = student_answer.split(\",\")\n"
                "        return set(correct_list) == set(student_list)\n"
                "    return exercise.correct_answers.strip() == student_answer.strip()\n\n"
                "class FakeExercise:\n"
                "    correct_answers = \"Konsolga chiqaradi, aniq\"\n"
                "    is_multiple_select = False\n\n"
                "result = check_multiple_choice(FakeExercise(), \"Konsolga chiqaradi, aniq\")\n"
                "print(f\"Talaba to'liq to'g'ri javobni tanladi, natija: {result}\")\n"
                "# Natija: True - review paytida so'ralgan BITTA savol bu xatoni oldini oldi\n"
            ),
        },
    ],
}

L0_EXERCISES = [
    {
        "title": "Code review'ning asosiy maqsadi",
        "title_ru": "Основная цель code review",
        "description": "Code review'ning ENG KAM foydali va noto'g'ri tushunilgan sababi qaysi?",
        "description_ru": "Какая причина code review НАИМЕНЕЕ полезна и чаще всего понимается неправильно?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat xatoni topib, muallifni \"ushlash\" (gatekeeping)",
            "Xatolarni production'dan oldin ushlash",
            "Jamoa a'zolari orasida bilim almashish",
            "Kod bazasida standart va izchillikni saqlash",
        ],
        "options_ru": [
            "Только поймать ошибку и \"поймать\" автора (gatekeeping)",
            "Поймать ошибки до продакшена",
            "Обмен знаниями между членами команды",
            "Поддержание стандарта и согласованности в кодовой базе",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Darsda aytilgan: bu fikr review'ni ziddiyatli munosabatga aylantiradi.",
        "hint_ru": "Сказано в уроке: этот взгляд превращает ревью в противоречивое отношение.",
        "explanation": (
            "\"Gatekeeping\" review'ni faqat nazorat vositasi deb tushunish - eng kam foydali "
            "va ko'pincha ziddiyatga olib keladigan qarash. Haqiqiy uchta sabab: xatolarni "
            "erta ushlash, bilim almashish, va standartni saqlash."
        ),
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "e6c19f2 xatosi",
        "title_ru": "Ошибка e6c19f2",
        "description": (
            "e6c19f2 commit'idagi bug'da, agar review paytida qanday savol berilganida, "
            "xato production'ga yetib borishdan oldin ushlangan bo'lardi?"
        ),
        "description_ru": (
            "В баге коммита e6c19f2, какой вопрос на ревью поймал бы ошибку до того, как "
            "она дошла до продакшена?"
        ),
        "exercise_type": "multiple_choice",
        "options": [
            "Bu funksiya qanday nomlanishi kerak?",
            "Vergul bo'yicha bo'lish faqat multi-select uchunmi, hamma holat uchunmi?",
            "Kod qatorlari soni 50 dan oshmayaptimi?",
            "Fayl nomi to'g'ri tanlanganmi?",
        ],
        "options_ru": [
            "Как должна называться эта функция?",
            "Разбиение по запятой - только для multi-select или для всех случаев?",
            "Не превышает ли количество строк кода 50?",
            "Правильно ли выбрано имя файла?",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsdagi kod namunasidagi izohni eslang - chekka holat haqida.",
        "hint_ru": "Вспомните комментарий в примере кода урока - о граничном случае.",
        "explanation": (
            "Xato aynan shu taxminda edi: split(\",\") HAR DOIM ishlatilgan, lekin bitta "
            "tanlovli javob matnida vergul bo'lsa, bu taxmin noto'g'ri edi. Bu - testlar "
            "qamrab olmagan, faqat inson savol berish orqali topadigan chekka holat."
        ),
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "PR hayot yo'lini tartiblang",
        "title_ru": "Расположите жизненный путь PR по порядку",
        "description": "Bitta PR/MR odatda o'tadigan besh holatni to'g'ri tartibda joylashtiring.",
        "description_ru": "Расположите пять состояний, через которые обычно проходит PR/MR, в правильном порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["Draft", "Review so'ralgan", "Changes requested", "Approved", "Merged"],
        "drag_items_ru": ["Draft", "Запрошено ревью", "Changes requested", "Approved", "Merged"],
        "correct_order": ["Draft", "Review so'ralgan", "Changes requested", "Approved", "Merged"],
        "hint": "Diagrammadagi flowchart'ni chapdan o'ngga o'qing (Changes requested tsikl ekanini eslang).",
        "hint_ru": "Прочитайте flowchart диаграммы слева направо (помните, что Changes requested - это цикл).",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "CI vs inson review",
        "title_ru": "CI против ревью человека",
        "description": "___ faqat mavjud testlar tekshirgan holatlarni tasdiqlaydi, yangi chekka holatni o'ylab topmaydi.",
        "description_ru": "___ подтверждает только случаи, покрытые существующими тестами, но не придумывает новый граничный случай.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "CI",  # technical/code-like token, no RU translation needed
        "hint": "117-kursda o'rgangan avtomatik tekshiruv tizimi nomi (qisqartma).",
        "hint_ru": "Название автоматической системы проверки из курса 117 (аббревиатура).",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 1 — Yaxshi PR/MR tavsifi yozish
# ---------------------------------------------------------------------------

L1_TEXT = """
<h3>Nima uchun tavsif kod'ning o'zi kabi muhim</h3>
<p>Ko'p yangi dasturchilar PR (pull request) yaratganda tavsif maydonini
bo'sh qoldiradi yoki "fix bug" kabi bir og'iz gap yozadi — "kod o'zi
tushuntiradi" deb o'ylashadi. Bu noto'g'ri: reviewer kodni SIZning fikringiz
bilan emas, birinchi marta ko'rmoqda. Yaxshi tavsif reviewer'ning ish
vaqtini realda tejaydi — nima uchun bu o'zgarish kerakligini, nima
o'zgarganini va uni qanday tekshirish mumkinligini oldindan tushuntiradi.
Yomon tavsif reviewer'ni kodni o'qib, izohlarsiz o'zi taxmin qilishga
majbur qiladi — bu ko'proq vaqt oladi va ko'proq savol-javob turini keltirib
chiqaradi.</p>

<p><strong>Muhim eslatma:</strong> ushbu platformaning repozitoriyasida
CODEOWNERS fayli ham, PR shabloni (PULL_REQUEST_TEMPLATE) ham yo'q —
GitHub tavsifni majburiy formatga solmaydi. Bu odatiy holat ko'p kichik
va o'rta jamoalarda. Shablon yo'qligi tavsifni yozish shart emas degani
emas — aksincha, jamoa o'zi qaror qilgan tuzilishga rioya qilishi
kerakligini bildiradi, chunki hech narsa buni majburlamaydi.</p>

<h3>To'rtta savol — har qanday yaxshi tavsifning skeleti</h3>
<ul>
<li><strong>Kontekst (Context)</strong> — bu o'zgarish NIMA UCHUN kerak
bo'lib qoldi? Qaysi bug hisobot qilingan, qaysi funksiya so'ralgan, yoki
qaysi muammo kuzatilgan? Reviewer buni bilmasa, "nega bu o'zgarish
umuman kerak" degan savoldan boshlaydi.</li>
<li><strong>Nima o'zgardi (What changed)</strong> — fayllar darajasida
emas (buni <code>git diff</code> ko'rsatadi), balki kontseptual darajada:
"X funksiyasi endi Y holatni ham to'g'ri boshqaradi", "Z endpoint'iga
yangi validatsiya qo'shildi".</li>
<li><strong>Nima uchun aynan shu yechim (Why this approach)</strong> —
agar muqobil yechim bo'lgan bo'lsa (masalan bazada indeks qo'shish o'rniga
so'rovni qayta yozish), buni tushuntirish reviewer'ni "nega boshqacha
qilmadingiz" degan savoldan qutqaradi.</li>
<li><strong>Qanday tekshirish mumkin (How to test)</strong> — reviewer
o'zi qanday tasdiqlashi mumkin: qaysi buyruqni ishga tushirish kerak,
qaysi sahifani ochish kerak, qaysi holatni qo'lda sinab ko'rish kerak.</li>
</ul>

<h3>Bu platformaning o'z tarixi — allaqachon yaxshi namuna</h3>
<p><code>git log</code> orqali ko'rish mumkinki, bu repozitoriyaning
commit tavsiflari (ular alohida PR emas, lekin xuddi shu tuzilishga
amal qiladi, chunki bitta maintainer bevosita <code>server</code>
branch'iga push qiladi) aslida yuqoridagi to'rtta savolga allaqachon
javob beradi. Masalan <code>2096b0e feat(scripts): add reusable
course_builder library + generic scripts</code> commit'ining to'liq
tavsifi: muammoni tasvirlaydi ("har bir yangi kurs uchun 2000+ qatorli
skript nusxalash"), yechimni tavsiflaydi (qaysi kichik skriptlar
qo'shilgani, ro'yxat bilan), NEGA aynan shunday qilinganini tushuntiradi
(<code>sections_json</code>da to'liq nusxa emas, <code>{"id": N}</code>
stub saqlashning sababi), va oxirida qanday tasdiqlanganini yozadi
("verified end-to-end via build_course.py against production"). Bu —
aynan Kontekst + Nima o'zgardi + Nega + Qanday tekshirilgan tuzilishi,
faqat "PR tavsifi" emas "commit tavsifi" nomi bilan.</p>

<h3>Bir xil o'zgarish, ikki xil tavsif — solishtiring</h3>
<p>Quyidagi kod namunasida xuddi shu <code>2096b0e</code> o'zgarishi
uchun ikkita tavsif berilgan: birinchisi — bu darsdagi haqiqiy commit
tavsifi (yuqorida tasvirlangan), ikkinchisi — SIZ ko'p ko'radigan, lekin
hech qanday foydali ma'lumot bermaydigan zaif tavsif (bu haqiqiy emas,
faqat solishtirish uchun qasddan zaiflashtirilgan). Farqga e'tibor
bering: ikkinchisi ham "to'g'ri" — u yolg'on gapirmaydi — lekin reviewer
uni o'qib hech narsa tushunmaydi va kodni boshidan o'zi tahlil qilishga
majbur bo'ladi.</p>

<h3>Tavsif bo'limlari qanday savollarni oldindan yopadi</h3>
<pre class="mermaid">
flowchart LR
  C["Kontekst
nega kerak bo'ldi"] --> Q1{{"reviewer:
'nega bu umuman kerak?'"}}
  W["Nima o'zgardi
kontseptual daraja"] --> Q2{{"reviewer:
'diff qamrovi qanday?'"}}
  Y["Nega aynan shu yechim"] --> Q3{{"reviewer:
'nega boshqacha emas?'"}}
  T["Qanday tekshirish"] --> Q4{{"reviewer:
'o'zim qanday tasdiqlayman?'"}}
  Q1 & Q2 & Q3 & Q4 --> F["Tezroq approve,
kamroq savol-javob turi"]
  style F fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma har bir tavsif bo'limining o'z vazifasi borligini
ko'rsatadi: u reviewer boshqa holatda SO'RASHI kerak bo'lgan savolga
oldindan javob beradi. To'rtta savol oldindan yopilsa, review tsikli
(0-darsdagi diagrammani eslang) kamroq "changes requested" bosqichidan
o'tadi — chunki reviewer aniqlik izlab vaqt sarflamaydi.</p>

<h3>Draft PR — tayyor bo'lmagan ishni ko'rsatish vositasi</h3>
<p>0-darsdagi diagrammada <code>Draft</code> holati bor edi. GitHub'da
buni PR yaratishda "Create draft pull request" tugmasi orqali belgilash
mumkin: bu "men hali tugatmaganman, lekin erta fikr-mulohaza xohlayman"
degani, va odatda CI baribir ishga tushadi (117-kurs), lekin reviewer'lar
odatda formal review so'ralmaguncha kutishadi. Tavsifni Draft bosqichida
ham yozish foydali — "Ready for review" belgilanganda uni to'ldirish
kifoya, boshidan yozish shart emas.</p>
""".strip()

L1_TEXT_RU = """
<h3>Почему описание так же важно, как сам код</h3>
<p>Многие начинающие разработчики оставляют поле описания PR (pull
request) пустым или пишут одну фразу вроде "fix bug" — думая, что "код
сам всё объяснит". Это неверно: reviewer видит код впервые, а не с вашим
ходом мыслей. Хорошее описание реально экономит время reviewer'а —
заранее объясняет, зачем нужно это изменение, что изменилось и как это
проверить. Плохое описание заставляет reviewer читать код и
догадываться без подсказок — это занимает больше времени и порождает
больше вопросов-ответов.</p>

<p><strong>Важное замечание:</strong> в репозитории этой платформы нет ни
файла CODEOWNERS, ни шаблона PR (PULL_REQUEST_TEMPLATE) — GitHub не
навязывает обязательный формат описания. Это обычная ситуация во многих
малых и средних командах. Отсутствие шаблона не означает, что описание
писать не нужно — наоборот, значит, что команда должна сама следовать
согласованной структуре, потому что ничто её не принуждает.</p>

<h3>Четыре вопроса — скелет любого хорошего описания</h3>
<ul>
<li><strong>Контекст (Context)</strong> — ПОЧЕМУ это изменение стало
нужным? Какой баг был зарегистрирован, какая функция была запрошена, или
какая проблема была замечена? Если reviewer этого не знает, он начинает
с вопроса "зачем это изменение вообще нужно".</li>
<li><strong>Что изменилось (What changed)</strong> — не на уровне файлов
(это покажет <code>git diff</code>), а на концептуальном уровне: "функция
X теперь корректно обрабатывает и случай Y", "в endpoint Z добавлена
новая валидация".</li>
<li><strong>Почему именно это решение (Why this approach)</strong> —
если была альтернатива (например, вместо переписывания запроса —
добавление индекса в базу), объяснение этого избавляет reviewer'а от
вопроса "почему не сделали иначе".</li>
<li><strong>Как проверить (How to test)</strong> — как reviewer может
сам подтвердить: какую команду запустить, какую страницу открыть, какой
случай проверить вручную.</li>
</ul>

<h3>Собственная история платформы — уже хороший образец</h3>
<p>Через <code>git log</code> видно, что описания коммитов этого
репозитория (это не отдельные PR, но следуют той же структуре, так как
один maintainer пушит напрямую в ветку <code>server</code>) уже отвечают
на все четыре вопроса выше. Например, полное описание коммита
<code>2096b0e feat(scripts): add reusable course_builder library +
generic scripts</code>: описывает проблему ("копирование скрипта на
2000+ строк для каждого нового курса"), описывает решение (список
добавленных мелких скриптов), объясняет ПОЧЕМУ сделано именно так
(причина хранения <code>{"id": N}</code> stub, а не полной копии в
<code>sections_json</code>), и в конце пишет, как это было подтверждено
("verified end-to-end via build_course.py against production"). Это —
именно структура Контекст + Что изменилось + Почему + Как проверено,
только под названием "описание коммита", а не "описание PR".</p>

<h3>Одно и то же изменение, два разных описания — сравните</h3>
<p>В примере кода ниже для того же изменения <code>2096b0e</code> дано
два описания: первое — реальное описание коммита из этого урока (описано
выше), второе — слабое описание, которое вы часто видите, но которое не
даёт полезной информации (оно НЕ реальное, а намеренно ослаблено для
сравнения). Обратите внимание на разницу: второе тоже "правильное" — оно
не лжёт — но reviewer, прочитав его, ничего не поймёт и будет вынужден
анализировать код с нуля сам.</p>

<h3>Какие вопросы заранее закрывают разделы описания</h3>
<pre class="mermaid">
flowchart LR
  C["Контекст
почему понадобилось"] --> Q1{{"reviewer:
'зачем это вообще нужно?'"}}
  W["Что изменилось
концептуальный уровень"] --> Q2{{"reviewer:
'каков охват diff?'"}}
  Y["Почему именно это решение"] --> Q3{{"reviewer:
'почему не иначе?'"}}
  T["Как проверить"] --> Q4{{"reviewer:
'как мне самому подтвердить?'"}}
  Q1 & Q2 & Q3 & Q4 --> F["Быстрее approve,
меньше циклов вопрос-ответ"]
  style F fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает, что у каждого раздела описания своя роль: он
заранее отвечает на вопрос, который reviewer иначе был бы вынужден
ЗАДАТЬ. Если все четыре вопроса закрыты заранее, цикл ревью (вспомните
диаграмму урока 0) проходит через меньше этапов "changes requested" —
потому что reviewer не тратит время на поиск ясности.</p>

<h3>Draft PR — инструмент показать незавершённую работу</h3>
<p>На диаграмме урока 0 было состояние <code>Draft</code>. На GitHub это
можно отметить при создании PR кнопкой "Create draft pull request": это
значит "я ещё не закончил, но хочу раннюю обратную связь", и обычно CI
всё равно запускается (курс 117), но reviewer'ы обычно ждут, пока не
будет запрошено формальное ревью. Писать описание уже на этапе Draft
полезно — при пометке "Ready for review" достаточно его дополнить, не
нужно начинать с нуля.</p>
""".strip()

L1_CODE = """
# ============================================================
# Bitta o'zgarish (2096b0e), ikki tavsif - solishtiring
# ============================================================

# --- HAQIQIY TAVSIF (bu repozitoriyaning o'z commit tarixidan) ---
REAL_DESCRIPTION = \"\"\"
feat(scripts): add reusable course_builder library + generic scripts

Replaces the "copy a 2,000+ line seed script per course" pattern with a
shared library plus small, generic, per-concern scripts driven by a
course spec module (pure data - no DB code):

  create_course.py       - Course row (idempotent by title)
  create_lessons.py      - Lesson rows (idempotent by course_id+order)
  create_exercises.py    - Exercise rows + sections_json exercise stubs
  create_samples.py      - LessonSample rows (namuna)
  set_submission_tasks.py - UPDATE task_* columns (not a separate table)
  translate_lessons_ru.py / translate_exercises_ru.py - RU content
  build_course.py         - runs all of the above in the correct order,
                            then check_exercise_integrity + check_ru_coverage

Exercises are stored in sections_json as bare {"id": N} stubs rather than
full snapshots: a full embed is a frozen copy that silently goes stale,
a stub is always hydrated fresh at request time.

Verified end-to-end via build_course.py against production (committed,
checked, then cleaned up).
\"\"\"

# --- ZAIFLASHTIRILGAN TAVSIF (HAQIQIY EMAS - faqat solishtirish uchun,
#     xuddi shu o'zgarish uchun ko'p ko'riladigan zaif variant) ---
WEAK_DESCRIPTION = \"\"\"
refactor: update course scripts

Cleaned up the scripts folder a bit. Added some new files for building
courses. Should work now.
\"\"\"

# ============================================================
# Reviewer nuqtai nazaridan farq:
#
# REAL_DESCRIPTION o'qigandan keyin reviewer BILADI: (1) qanday muammo
# hal qilinmoqda (2000+ qatorli nusxalash), (2) qaysi fayllar qo'shilgan
# va har biri nima qiladi, (3) NEGA stub yondashuvi tanlangan (frozen
# copy emas, har doim yangi hydrate), (4) qanday tasdiqlangan (production
# build orqali).
#
# WEAK_DESCRIPTION o'qigandan keyin reviewer HECH NARSA bilmaydi: "bir
# oz" tozalangan - qancha? "ba'zi" fayllar - qaysi va nima uchun? "ishlashi
# kerak" - qanday tekshirilgan, umuman tekshirilganmi? Reviewer endi BUTUN
# diff'ni o'zi, hech qanday yo'l-yo'riqsiz o'qib chiqishga majbur.
# ============================================================
""".strip()

L1_CODE_RU = """
# ============================================================
# Одно изменение (2096b0e), два описания - сравните
# ============================================================

# --- РЕАЛЬНОЕ ОПИСАНИЕ (из собственной истории коммитов этого репозитория) ---
REAL_DESCRIPTION = \"\"\"
feat(scripts): add reusable course_builder library + generic scripts

Заменяет паттерн "копировать скрипт на 2000+ строк для каждого курса"
общей библиотекой плюс маленькими, специализированными скриптами,
управляемыми модулем-спецификацией курса (чистые данные - без кода БД):

  create_course.py       - строка Course (идемпотентно по title)
  create_lessons.py      - строки Lesson (идемпотентно по course_id+order)
  create_exercises.py    - строки Exercise + заглушки в sections_json
  create_samples.py      - строки LessonSample (namuna)
  set_submission_tasks.py - UPDATE колонок task_* (не отдельная таблица)
  translate_lessons_ru.py / translate_exercises_ru.py - RU-контент
  build_course.py         - запускает всё вышеперечисленное по порядку,
                            затем check_exercise_integrity + check_ru_coverage

Упражнения хранятся в sections_json как голые заглушки {"id": N}, а не
полные снимки: полное встраивание - это замороженная копия, которая
незаметно устаревает, заглушка же всегда гидратируется свежей при запросе.

Проверено сквозным образом через build_course.py на продакшене
(закоммичено, проверено, затем очищено).
\"\"\"

# --- ОСЛАБЛЕННОЕ ОПИСАНИЕ (НЕ РЕАЛЬНОЕ - только для сравнения,
#     часто встречающийся слабый вариант для того же изменения) ---
WEAK_DESCRIPTION = \"\"\"
refactor: update course scripts

Немного почистил папку скриптов. Добавил несколько новых файлов для
построения курсов. Должно работать.
\"\"\"

# ============================================================
# Разница с точки зрения reviewer:
#
# После REAL_DESCRIPTION reviewer ЗНАЕТ: (1) какая проблема решается
# (копирование 2000+ строк), (2) какие файлы добавлены и что каждый
# делает, (3) ПОЧЕМУ выбран подход с заглушкой (не замороженная копия, а
# всегда свежая гидратация), (4) как это подтверждено (через продакшн-сборку).
#
# После WEAK_DESCRIPTION reviewer НЕ ЗНАЕТ НИЧЕГО: "немного" почищено -
# сколько? "несколько" файлов - какие и зачем? "должно работать" - как
# проверено, проверено ли вообще? Reviewer теперь вынужден сам, без
# каких-либо ориентиров, прочитать ВЕСЬ diff.
# ============================================================
""".strip()

L1_TASK = {
    "task_title": "O'z o'zgarishingiz uchun to'liq PR tavsifi yozing",
    "task_title_ru": "Напишите полное описание PR для своего изменения",
    "task_description": (
        "Shaxsiy loyihangizda (yoki shu platformaning fork'ida) kichik "
        "amaliy o'zgarish qiling (bitta bug tuzatish yoki kichik funksiya). "
        "Uni branch'ga qo'ying va GitHub'da PR oching (Draft sifatida ham "
        "bo'lishi mumkin). Tavsifni to'rtta bo'lim bilan yozing: Kontekst, "
        "Nima o'zgardi, Nega aynan shu yechim, Qanday tekshirish mumkin."
    ),
    "task_description_ru": (
        "В своём проекте (или форке этой платформы) внесите небольшое "
        "практическое изменение (одно исправление бага или небольшую "
        "функцию). Поместите его в ветку и откройте PR на GitHub (можно и "
        "как Draft). Напишите описание с четырьмя разделами: Контекст, Что "
        "изменилось, Почему именно это решение, Как проверить."
    ),
    "task_requirements": (
        "1) PR havolasi ilova qilinishi shart. 2) Barcha to'rtta bo'lim "
        "aniq sarlavhalar bilan ajratilgan bo'lishi kerak. 3) \"Qanday "
        "tekshirish\" bo'limida kamida bitta aniq, bajarilishi mumkin "
        "buyruq yoki qadam bo'lishi kerak (masalan \"pytest tests/test_x.py "
        "ishga tushiring\")."
    ),
    "task_requirements_ru": (
        "1) Обязательно приложить ссылку на PR. 2) Все четыре раздела "
        "должны быть отделены чёткими заголовками. 3) В разделе \"Как "
        "проверить\" должна быть минимум одна конкретная, выполнимая "
        "команда или шаг (например \"запустите pytest tests/test_x.py\")."
    ),
    "task_technologies": "GitHub (Pull Requests), Markdown",
    "task_deadline_days": 3,
}

L1_SAMPLE = {
    "title": "Namuna: real vs zaif PR tavsifi",
    "description": (
        "Ushbu darsning kod namunasi asosida, bitta real o'zgarish uchun "
        "ikki xil tavsifni to'liq matn sifatida ko'rsatadi - reviewer "
        "nuqtai nazaridan farqni tushunish uchun."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "pr_description_good.md",
            "language": "markdown",
            "code": (
                "## Kontekst\n"
                "Har bir yangi kurs uchun 2000+ qatorli seed skript nusxalanardi - "
                "bu RU tarjima bosqichini tasodifan tashlab ketishni osonlashtirardi "
                "(1,371 mashq shu sababli tarjimasiz qolgan edi).\n\n"
                "## Nima o'zgardi\n"
                "Umumiy `course_builder/` kutubxonasi va spec-modul asosida ishlaydigan "
                "kichik, alohida vazifali skriptlar qo'shildi: `create_course.py`, "
                "`create_lessons.py`, `create_exercises.py`, `create_samples.py`, "
                "`build_course.py` (hammasini to'g'ri tartibda ishga tushiradi).\n\n"
                "## Nega aynan shu yechim\n"
                "Mashqlar `sections_json`da to'liq nusxa emas, `{\"id\": N}` stub "
                "sifatida saqlanadi - stub so'rov vaqtida har doim yangi ma'lumot bilan "
                "to'ldiriladi, to'liq nusxa esa muzlab qolib, eskirib ketishi mumkin edi.\n\n"
                "## Qanday tekshirish mumkin\n"
                "`python scripts/build_course.py course_specs/_example.py --dry-run` "
                "ishga tushiring - hech narsa yozilmasdan spec formatini tasdiqlaydi."
            ),
        },
        {
            "filename": "pr_description_weak.md",
            "language": "markdown",
            "code": (
                "## Tavsif\n"
                "Skriptlarni bir oz tozaladim. Kurs qurish uchun ba'zi yangi fayllar "
                "qo'shdim. Ishlashi kerak."
            ),
        },
    ],
}

L1_EXERCISES = [
    {
        "title": "Tavsifning to'rtta bo'limi",
        "title_ru": "Четыре раздела описания",
        "description": "Quyidagilardan qaysi biri yaxshi PR tavsifining TO'RT asosiy bo'limiga KIRMAYDI?",
        "description_ru": "Какой из перечисленных пунктов НЕ входит в четыре основных раздела хорошего описания PR?",
        "exercise_type": "multiple_choice",
        "options": [
            "Kontekst (nega kerak bo'ldi)",
            "Nima o'zgardi",
            "Muallifning boshqa loyihalardagi tajribasi",
            "Qanday tekshirish mumkin",
        ],
        "options_ru": [
            "Контекст (почему понадобилось)",
            "Что изменилось",
            "Опыт автора в других проектах",
            "Как проверить",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Darsda sanalgan to'rtta bo'limni eslang - ular reviewer'ga aloqador savollarga javob beradi.",
        "hint_ru": "Вспомните четыре раздела из урока - они отвечают на вопросы, важные для reviewer'а.",
        "explanation": (
            "To'rt bo'lim: Kontekst, Nima o'zgardi, Nega aynan shu yechim, Qanday "
            "tekshirish mumkin. Muallifning boshqa loyihalardagi tajribasi bu "
            "o'zgarishni baholashga aloqasi yo'q."
        ),
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "2096b0e tavsifi qanday savolga javob beradi",
        "title_ru": "На какой вопрос отвечает описание 2096b0e",
        "description": (
            "2096b0e commit tavsifidagi \"Exercises are stored in sections_json as "
            "bare {\"id\": N} stubs...\" jumlasi tavsifning qaysi bo'limiga tegishli?"
        ),
        "description_ru": (
            "К какому разделу описания относится фраза \"Exercises are stored in "
            "sections_json as bare {\"id\": N} stubs...\" из описания коммита 2096b0e?"
        ),
        "exercise_type": "multiple_choice",
        "options": ["Kontekst", "Nima o'zgardi", "Nega aynan shu yechim", "Qanday tekshirish mumkin"],
        "options_ru": ["Контекст", "Что изменилось", "Почему именно это решение", "Как проверить"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Bu jumla NEGA stub (frozen copy emas) tanlanganini tushuntiradi.",
        "hint_ru": "Эта фраза объясняет, ПОЧЕМУ выбрана заглушка (а не замороженная копия).",
        "explanation": (
            "Bu jumla dizayn qarorining sababini tushuntiradi (stub har doim yangi "
            "hydrate qilinadi, frozen copy esa eskiradi) - bu aynan \"Nega aynan shu "
            "yechim\" bo'limining vazifasi."
        ),
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "PR tavsifi bo'limlarini tartiblang",
        "title_ru": "Расположите разделы описания PR по порядку",
        "description": "Yaxshi PR tavsifining bo'limlarini odatiy mantiqiy tartibda joylashtiring.",
        "description_ru": "Расположите разделы хорошего описания PR в обычном логическом порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["Kontekst", "Nima o'zgardi", "Nega aynan shu yechim", "Qanday tekshirish mumkin"],
        "drag_items_ru": ["Контекст", "Что изменилось", "Почему именно это решение", "Как проверить"],
        "correct_order": ["Kontekst", "Nima o'zgardi", "Nega aynan shu yechim", "Qanday tekshirish mumkin"],
        "hint": "Avval NEGA kerakligini, keyin NIMA qilinganini, keyin NEGA shu yo'l, oxirida TEKSHIRISHNI tushuntiring.",
        "hint_ru": "Сначала объясните, ЗАЧЕМ нужно, потом ЧТО сделано, потом ПОЧЕМУ так, и в конце — КАК проверить.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Draft PR maqsadi",
        "title_ru": "Назначение Draft PR",
        "description": "GitHub'da PR'ni ___ deb belgilash \"hali tugallanmagan, lekin erta fikr-mulohaza kerak\" degani.",
        "description_ru": "Пометка PR как ___ на GitHub означает \"ещё не завершено, но нужна ранняя обратная связь\".",
        "exercise_type": "fill_in_blank",
        "correct_answers": "Draft",  # literal UI state name, no natural-language RU equivalent needed
        "hint": "0-darsdagi diagrammaning birinchi holati.",
        "hint_ru": "Первое состояние на диаграмме урока 0.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 2 — Commit xabarlari konventsiyasi: Conventional Commits
# ---------------------------------------------------------------------------

L2_TEXT = """
<h3>Nima uchun commit xabari ham kod kabi "yoziladi"</h3>
<p>3-darsda commit'larning o'zi (atomik yoki aralash) haqida gaplashamiz;
bu darsda esa ularning XABARI qanday YOZILISHI haqida — chunki
<code>git log --oneline</code> orqali o'qiladigan tarix o'zi hujjat
vazifasini bajaradi. Bir yil o'tib "bu funksiya nega shunday yozilgan?"
degan savolga <code>git blame</code> orqali javob qidirganda, sizni
<code>fix bug</code> emas, <code>fix(scoring): guard against
self-contradictory project grading</code> kabi xabar qutqaradi.</p>

<h3>Conventional Commits formati</h3>
<p><strong>Conventional Commits</strong> — keng tarqalgan konventsiya:
<code>tur(qamrov): tavsif</code>. Uch qism:</p>
<ul>
<li><strong>tur (type)</strong> — o'zgarish TABIATINI bildiradi:
<code>feat</code> (yangi funksiya), <code>fix</code> (xato tuzatish),
<code>refactor</code> (xatti-harakat o'zgarmasdan kod tuzilishi
o'zgarishi), <code>docs</code> (hujjat), <code>test</code> (faqat test),
<code>chore</code> (infratuzilma/skript/konfiguratsiya), <code>perf</code>
(tezlik optimizatsiyasi), <code>ci</code> (CI/CD konfiguratsiyasi).</li>
<li><strong>qamrov (scope)</strong> — qavs ichida, QAYSI qism
o'zgarganini bildiradi (masalan <code>scripts</code>, <code>lessons</code>,
<code>points</code>). Ixtiyoriy, lekin katta kod bazasida juda foydali —
<code>git log --oneline -- backend/app/services/exercise_service.py</code>
qidirishdan ko'ra, <code>git log --grep="(scoring)"</code> tezroq.</li>
<li><strong>tavsif</strong> — BUYRUQ MAYLIDA (imperative mood): "add",
"fix", "make" — "added", "fixed", "makes" EMAS. Sabab: Git o'zining
avtomatik xabarlarida ham shu uslubni ishlatadi ("Merge branch..."), va
bu "agar shu commit qo'llansa, u NIMA QILADI" deb o'qiladi.</li>
</ul>

<h3>Ushbu platformaning o'z tarixidan — real, ixtiyoriy misollar emas</h3>
<p><code>git log --oneline -40</code> buyrug'i shu repozitoriyaning har
bir commit'ini ko'rsatadi, va ular DEYARLI HAMMASI yuqoridagi formatga
qat'iy amal qiladi:</p>
<ul>
<li><code>feat(scripts): add reusable course_builder library</code> —
tur=feat (yangi kutubxona), qamrov=scripts, tavsif buyruq maylida "add".</li>
<li><code>fix(lessons): make in-lesson exercise hydration
language-aware</code> — tur=fix (xato: til hisobga olinmagan edi),
qamrov=lessons, aniq NIMA tuzatilgani ko'rinib turibdi.</li>
<li><code>chore(scripts): add exercise-integrity and course-image
checkers</code> — tur=chore (yangi funksiya emas, infratuzilma:
tekshiruv skriptlari), qamrov=scripts.</li>
<li><code>fix(points): stop permanently inflating lifetime_points/
leaderboard on reversal</code> — tur=fix, qamrov=points, "stop ... on
reversal" — MUAMMO nima ekanini xabarning o'zida ko'rsatadi.</li>
</ul>
<p>To'rttasini solishtiring: qamrovlar turlicha (<code>scripts</code>,
<code>lessons</code>, <code>points</code>), lekin STRUKTURA bir xil.
Aynan shu izchillik <code>git log --grep="^fix"</code> yoki
<code>--grep="(points)"</code> orqali qidirishni ishonchli qiladi — agar
ba'zi commit'lar formatga rioya qilmasa, qidiruv ularni o'tkazib
yuboradi.</p>

<h3>Nomukammallik ham real tarixda bor — buni yashirmaymiz</h3>
<p>Bir xil tarixda <code>debug: log openai url and error body in ai
chain</code> degan commit ham bor. <code>debug</code> — Conventional
Commits'ning STANDART turlari ro'yxatida YO'Q (standart: feat, fix,
docs, style, refactor, perf, test, chore, ci, build, revert). Bu holatda
<code>chore(ai): add debug logging for openai url and error body</code>
kabi yozilgan bo'lsa, izchillik saqlanardi. Bu — hatto juda intizomli
tarixda ham kichik chetga chiqish bo'lishi mumkinligini ko'rsatadi;
review paytida buni ko'rgan hamkasb "bu yangi tur nima uchun kerak,
standart to'plamdan foydalanish mumkinmi?" deb so'rashi mumkin edi.</p>

<h3>Commit xabari anatomiyasi va uning keyingi hayoti</h3>
<pre class="mermaid">
flowchart LR
  T["tur: fix"] --> MSG["fix(points): stop permanently
inflating lifetime_points on reversal"]
  S["qamrov: points"] --> MSG
  D["tavsif: buyruq maylida"] --> MSG
  MSG --> G["git log --grep
qidiruv uchun"]
  MSG --> B["git blame
kontekst uchun"]
  MSG --> CL["Changelog
avtomatik guruhlash uchun
(10-darsda ko'ramiz)"]
  style MSG fill:#d6e9ff,stroke:#2266aa
  style CL fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma commit xabarining uchta qismi (tur, qamrov, tavsif) qanday
birlashib bitta izlanadigan, o'qiladigan yozuvni hosil qilishini, va bu
yozuv keyinchalik uch xil maqsadda (qidiruv, blame konteksti, va
10-darsda ko'radigan avtomatik changelog guruhlash) qayta ishlatilishini
ko'rsatadi. Format buzilsa, uchala foydalanish ham qiyinlashadi.</p>

<h3>Nega bu shunchaki "uslub afzalligi" emas</h3>
<p>0-darsda aytilganidek, uslub review vaqtini band qilmasligi kerak —
lekin commit format BOSHQACHA: u faqat "chiroyli ko'rinish" emas, balki
KEYINGI FOYDALANUVCHI (o'zingiz, olti oydan keyin, yoki jamoadosh) uchun
qidiriladigan indeks yaratadi. <code>git log --grep="^fix(points)"</code>
kabi buyruq faqat format izchil bo'lgandagina ishlaydi.</p>
""".strip()

L2_TEXT_RU = """
<h3>Почему сообщение коммита тоже "пишется" как код</h3>
<p>В уроке 3 мы поговорим о самих коммитах (атомарных или смешанных); в
этом уроке — о том, КАК ПИШЕТСЯ их сообщение, потому что читаемая через
<code>git log --oneline</code> история сама выполняет роль документации.
Через год, когда вы ищете ответ на вопрос "почему эта функция написана
именно так" через <code>git blame</code>, вас спасёт не <code>fix
bug</code>, а сообщение вроде <code>fix(scoring): guard against
self-contradictory project grading</code>.</p>

<h3>Формат Conventional Commits</h3>
<p><strong>Conventional Commits</strong> — широко распространённая
конвенция: <code>тип(область): описание</code>. Три части:</p>
<ul>
<li><strong>тип (type)</strong> — обозначает ПРИРОДУ изменения:
<code>feat</code> (новая функция), <code>fix</code> (исправление
ошибки), <code>refactor</code> (изменение структуры кода без изменения
поведения), <code>docs</code> (документация), <code>test</code> (только
тесты), <code>chore</code> (инфраструктура/скрипты/конфигурация),
<code>perf</code> (оптимизация скорости), <code>ci</code> (конфигурация
CI/CD).</li>
<li><strong>область (scope)</strong> — в скобках, обозначает, КАКАЯ
часть изменилась (например <code>scripts</code>, <code>lessons</code>,
<code>points</code>). Необязательна, но очень полезна в большой кодовой
базе — <code>git log --grep="(scoring)"</code> быстрее, чем поиск через
<code>git log --oneline -- backend/app/services/exercise_service.py</code>.</li>
<li><strong>описание</strong> — в ПОВЕЛИТЕЛЬНОМ наклонении (imperative
mood): "add", "fix", "make" — а НЕ "added", "fixed", "makes". Причина: сам
Git использует такой же стиль в своих автоматических сообщениях ("Merge
branch..."), и это читается как "если применить этот коммит, он СДЕЛАЕТ
это".</li>
</ul>

<h3>Из собственной истории платформы — реальные, не выдуманные примеры</h3>
<p>Команда <code>git log --oneline -40</code> показывает каждый коммит
этого репозитория, и они ПОЧТИ ВСЕ строго следуют формату выше:</p>
<ul>
<li><code>feat(scripts): add reusable course_builder library</code> —
тип=feat (новая библиотека), область=scripts, описание в повелительном
наклонении "add".</li>
<li><code>fix(lessons): make in-lesson exercise hydration
language-aware</code> — тип=fix (ошибка: язык не учитывался),
область=lessons, чётко видно, ЧТО исправлено.</li>
<li><code>chore(scripts): add exercise-integrity and course-image
checkers</code> — тип=chore (не новая функция, а инфраструктура:
скрипты проверки), область=scripts.</li>
<li><code>fix(points): stop permanently inflating lifetime_points/
leaderboard on reversal</code> — тип=fix, область=points, "stop ... on
reversal" — сама формулировка показывает, В ЧЁМ была ПРОБЛЕМА.</li>
</ul>
<p>Сравните все четыре: области разные (<code>scripts</code>,
<code>lessons</code>, <code>points</code>), но СТРУКТУРА одна и та же.
Именно эта согласованность делает поиск через <code>git log
--grep="^fix"</code> или <code>--grep="(points)"</code> надёжным — если
часть коммитов не следует формату, поиск их пропустит.</p>

<h3>Несовершенство тоже есть в реальной истории — не скрываем его</h3>
<p>В той же истории есть коммит <code>debug: log openai url and error
body in ai chain</code>. <code>debug</code> НЕ входит в стандартный
список типов Conventional Commits (стандарт: feat, fix, docs, style,
refactor, perf, test, chore, ci, build, revert). Если бы это было
написано как <code>chore(ai): add debug logging for openai url and error
body</code>, согласованность бы сохранилась. Это показывает, что даже в
очень дисциплинированной истории возможно небольшое отклонение; коллега,
увидевший это на ревью, мог бы спросить "зачем нужен новый тип, можно ли
использовать стандартный набор?"</p>

<h3>Анатомия сообщения коммита и его дальнейшая жизнь</h3>
<pre class="mermaid">
flowchart LR
  T["тип: fix"] --> MSG["fix(points): stop permanently
inflating lifetime_points on reversal"]
  S["область: points"] --> MSG
  D["описание: повелительное наклонение"] --> MSG
  MSG --> G["git log --grep
для поиска"]
  MSG --> B["git blame
для контекста"]
  MSG --> CL["Changelog
для автогруппировки
(увидим в уроке 10)"]
  style MSG fill:#d6e9ff,stroke:#2266aa
  style CL fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает, как три части сообщения коммита (тип, область,
описание) объединяются в одну доступную для поиска, читаемую запись, и
эта запись затем используется трижды с разной целью (поиск, контекст
blame, и автоматическая группировка в changelog в уроке 10). Если формат
нарушен, все три использования усложняются.</p>

<h3>Почему это не просто "стилистическое преимущество"</h3>
<p>Как говорилось в уроке 0, стиль не должен занимать время ревью — но
формат коммита ДРУГОЕ: это не просто "красивый вид", а создание
индекса, доступного для поиска СЛЕДУЮЩИМ пользователем (вами самими
через полгода, или коллегой). Команда вроде <code>git log
--grep="^fix(points)"</code> работает только при согласованном формате.</p>
""".strip()

L2_CODE = """
# ============================================================
# git log --oneline -40'dan haqiqiy misollar (bu repozitoriyaning
# o'z tarixi) - Conventional Commits formatini tahlil qilamiz
# ============================================================

REAL_COMMITS = [
    "feat(scripts): add reusable course_builder library + generic scripts",
    "fix(lessons): make in-lesson exercise hydration language-aware",
    "chore(scripts): add exercise-integrity and course-image checkers",
    "fix(points): stop permanently inflating lifetime_points/leaderboard on reversal",
    "feat(team-game): notify parent bot on session complete + public snapshot endpoints",
    "fix(dictionary): stop leaking the answer word and fix RU definition gen",
    "refactor(fonts): normalize CSS to --font-ui / --font-mono tokens",
    "debug: log openai url and error body in ai chain",   # <- standart TUR emas!
]

import re

# type(scope): description  yoki  type: description
CONVENTIONAL_PATTERN = re.compile(
    r"^(feat|fix|refactor|docs|test|chore|perf|ci|style|build|revert)"
    r"(\\([a-z0-9_-]+\\))?: .+"
)

STANDARD_TYPES = {
    "feat", "fix", "refactor", "docs", "test",
    "chore", "perf", "ci", "style", "build", "revert",
}

for msg in REAL_COMMITS:
    match = CONVENTIONAL_PATTERN.match(msg)
    type_part = msg.split(":")[0].split("(")[0]
    is_standard = type_part in STANDARD_TYPES
    print(f"{'OK ' if match and is_standard else 'DIQQAT'}  {msg}")

# Natija:
# OK      feat(scripts): add reusable course_builder library ...
# OK      fix(lessons): make in-lesson exercise hydration ...
# OK      chore(scripts): add exercise-integrity ...
# OK      fix(points): stop permanently inflating ...
# OK      feat(team-game): notify parent bot ...
# OK      fix(dictionary): stop leaking ...
# OK      refactor(fonts): normalize CSS ...
# DIQQAT  debug: log openai url and error body in ai chain
#         ^ "debug" standart tur emas - review'da savol tug'dirishi mumkin edi


# ============================================================
# Bu repozitoriyaning so'nggi 300 commit'ini turi bo'yicha
# guruhlash (git log --oneline -300'dan olingan real taqsimot)
# ============================================================
from collections import Counter

# git log --oneline -300 | grep -oE '^[a-z]+' natijasining qisqartirilgan
# ko'rinishi - bu son real repozitoriyadan olingan (taxminiy taqsimot)
REAL_TYPE_COUNTS = Counter({
    "fix": 34,       # scope'siz "fix:" + scope'li "fix(...)"
    "feat": 17,
    "refactor": 3,
    "chore": 3,
    "test": 2,
    "ci": 1,
    "debug": 1,      # <- standart emas
})


def summarize_history(counts: Counter) -> None:
    total = sum(counts.values())
    for commit_type, count in counts.most_common():
        flag = "" if commit_type in STANDARD_TYPES else "  <- standart emas!"
        pct = count / total * 100
        print(f"{commit_type:>10}: {count:>3} ta ({pct:4.1f}%){flag}")


summarize_history(REAL_TYPE_COUNTS)
# fix eng ko'p uchraydigan tur ekani - bu odatiy holat: aksariyat
# kunlik ish bug tuzatishlardan iborat, feat kamroq (yangi funksiya
# kamroq tez-tez qo'shiladi), va debug kabi standart bo'lmagan tur
# JUDA kam (1 ta, 300 tadan) - bu izchillik odatda YAXSHI saqlanganini
# ko'rsatadi, lekin nol emasligini ham.
""".strip()

L2_CODE_RU = """
# ============================================================
# Реальные примеры из git log --oneline -40 (собственная история
# этого репозитория) - анализируем формат Conventional Commits
# ============================================================

REAL_COMMITS = [
    "feat(scripts): add reusable course_builder library + generic scripts",
    "fix(lessons): make in-lesson exercise hydration language-aware",
    "chore(scripts): add exercise-integrity and course-image checkers",
    "fix(points): stop permanently inflating lifetime_points/leaderboard on reversal",
    "feat(team-game): notify parent bot on session complete + public snapshot endpoints",
    "fix(dictionary): stop leaking the answer word and fix RU definition gen",
    "refactor(fonts): normalize CSS to --font-ui / --font-mono tokens",
    "debug: log openai url and error body in ai chain",   # <- НЕ стандартный ТИП!
]

import re

# type(scope): description  или  type: description
CONVENTIONAL_PATTERN = re.compile(
    r"^(feat|fix|refactor|docs|test|chore|perf|ci|style|build|revert)"
    r"(\\([a-z0-9_-]+\\))?: .+"
)

STANDARD_TYPES = {
    "feat", "fix", "refactor", "docs", "test",
    "chore", "perf", "ci", "style", "build", "revert",
}

for msg in REAL_COMMITS:
    match = CONVENTIONAL_PATTERN.match(msg)
    type_part = msg.split(":")[0].split("(")[0]
    is_standard = type_part in STANDARD_TYPES
    print(f"{'OK ' if match and is_standard else 'ВНИМАНИЕ'}  {msg}")

# Результат:
# OK        feat(scripts): add reusable course_builder library ...
# OK        fix(lessons): make in-lesson exercise hydration ...
# OK        chore(scripts): add exercise-integrity ...
# OK        fix(points): stop permanently inflating ...
# OK        feat(team-game): notify parent bot ...
# OK        fix(dictionary): stop leaking ...
# OK        refactor(fonts): normalize CSS ...
# ВНИМАНИЕ  debug: log openai url and error body in ai chain
#           ^ "debug" - не стандартный тип, мог бы вызвать вопрос на ревью


# ============================================================
# Группировка последних 300 коммитов этого репозитория по типу
# (реальное распределение из git log --oneline -300)
# ============================================================
from collections import Counter

# Сокращённое представление результата git log --oneline -300 |
# grep -oE '^[a-z]+' - эти числа взяты из реального репозитория
# (приблизительное распределение)
REAL_TYPE_COUNTS = Counter({
    "fix": 34,       # "fix:" без scope + "fix(...)" со scope
    "feat": 17,
    "refactor": 3,
    "chore": 3,
    "test": 2,
    "ci": 1,
    "debug": 1,      # <- не стандартный
})


def summarize_history(counts: Counter) -> None:
    total = sum(counts.values())
    for commit_type, count in counts.most_common():
        flag = "" if commit_type in STANDARD_TYPES else "  <- не стандартный!"
        pct = count / total * 100
        print(f"{commit_type:>10}: {count:>3} шт. ({pct:4.1f}%){flag}")


summarize_history(REAL_TYPE_COUNTS)
# fix - самый частый тип - это обычное явление: большинство повседневной
# работы состоит из исправлений багов, feat встречается реже (новая
# функция добавляется не так часто), а нестандартный тип вроде debug -
# ОЧЕНЬ редок (1 из 300) - это показывает, что согласованность обычно
# ХОРОШО сохраняется, но не равна нулю отклонений.
""".strip()

L2_TASK = {
    "task_title": "O'zingizning 5 ta commit'ingizni Conventional Commits'ga moslang",
    "task_title_ru": "Приведите свои 5 коммитов к формату Conventional Commits",
    "task_description": (
        "Shaxsiy loyihangizdan (yoki avvalgi vazifalaringizdan) so'nggi 5 ta "
        "commit xabarini oling (agar formatga mos kelmasa, xayoliy misollar "
        "yozing). Har birini Conventional Commits formatiga (tur(qamrov): "
        "buyruq maylidagi tavsif) qayta yozing va nima uchun aynan shu tur "
        "va qamrovni tanlaganingizni bir gapda tushuntiring."
    ),
    "task_description_ru": (
        "Возьмите последние 5 сообщений коммитов из своего проекта (или "
        "прошлых заданий) (если формат не подходит, напишите условные "
        "примеры). Перепишите каждое в формате Conventional Commits "
        "(тип(область): описание в повелительном наклонении) и одним "
        "предложением объясните, почему выбрали именно такой тип и область."
    ),
    "task_requirements": (
        "1) Aynan 5 ta commit xabari bo'lishi kerak. 2) Har biri "
        "tur(qamrov): tavsif formatida, standart turlardan (feat/fix/"
        "refactor/docs/test/chore/perf/ci) foydalanilgan bo'lishi shart. "
        "3) Har birida tavsif buyruq maylida yozilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Должно быть ровно 5 сообщений коммитов. 2) Каждое в формате "
        "тип(область): описание, с использованием стандартных типов "
        "(feat/fix/refactor/docs/test/chore/perf/ci). 3) В каждом описание "
        "должно быть в повелительном наклонении."
    ),
    "task_technologies": "Git, Conventional Commits",
    "task_deadline_days": 3,
}

L2_SAMPLE = {
    "title": "Namuna: real commit tarixini formatga tekshirish skripti",
    "description": (
        "Ushbu darsning kod namunasi asosida, bu platformaning o'z "
        "commit'larini Conventional Commits formatiga qarshi tekshiradigan, "
        "va standart bo'lmagan turlarni (masalan 'debug') aniqlaydigan "
        "to'liq ishlaydigan skript."
    ),
    "sample_type": "python",
    "html_code": None,
    "css_code": None,
    "js_code": None,
    "code_files": [
        {
            "filename": "check_commit_format.py",
            "language": "python",
            "code": (
                "import re\n\n"
                "STANDARD_TYPES = {\n"
                "    \"feat\", \"fix\", \"refactor\", \"docs\", \"test\",\n"
                "    \"chore\", \"perf\", \"ci\", \"style\", \"build\", \"revert\",\n"
                "}\n"
                "PATTERN = re.compile(r\"^([a-zA-Z]+)(\\([a-z0-9_-]+\\))?: .+\")\n\n\n"
                "def check(message: str) -> list[str]:\n"
                "    \"\"\"Bitta commit xabaridagi muammolarni qaytaradi (bo'sh = OK).\"\"\"\n"
                "    problems = []\n"
                "    match = PATTERN.match(message)\n"
                "    if not match:\n"
                "        problems.append(\"format 'type(scope): description'ga mos kelmadi\")\n"
                "        return problems\n"
                "    commit_type = match.group(1)\n"
                "    if commit_type not in STANDARD_TYPES:\n"
                "        problems.append(f\"'{commit_type}' standart tur emas\")\n"
                "    description = message.split(': ', 1)[1] if ': ' in message else ''\n"
                "    if description and description[0].isupper():\n"
                "        problems.append(\"tavsif kichik harf bilan boshlanishi tavsiya etiladi\")\n"
                "    if description.endswith('.'):\n"
                "        problems.append(\"tavsif oxirida nuqta shart emas\")\n"
                "    return problems\n\n\n"
                "if __name__ == \"__main__\":\n"
                "    examples = [\n"
                "        \"fix(points): stop permanently inflating lifetime_points on reversal\",\n"
                "        \"debug: log openai url and error body in ai chain\",\n"
                "        \"Fixed the bug.\",\n"
                "    ]\n"
                "    for msg in examples:\n"
                "        result = check(msg)\n"
                "        status = \"OK\" if not result else f\"MUAMMO: {result}\"\n"
                "        print(f\"{msg!r} -> {status}\")\n"
            ),
        }
    ],
}

L2_EXERCISES = [
    {
        "title": "Conventional Commits qismlari",
        "title_ru": "Части Conventional Commits",
        "description": "\"fix(points): stop permanently inflating lifetime_points on reversal\" xabarida qamrov (scope) qaysi so'z?",
        "description_ru": "В сообщении \"fix(points): stop permanently inflating lifetime_points on reversal\" какое слово является областью (scope)?",
        "exercise_type": "multiple_choice",
        "options": ["fix", "points", "stop", "lifetime_points"],
        "options_ru": ["fix", "points", "stop", "lifetime_points"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Qamrov qavs ICHIDA joylashadi: tur(qamrov): tavsif.",
        "hint_ru": "Область находится ВНУТРИ скобок: тип(область): описание.",
        "explanation": "Format tur(qamrov): tavsif. Bu xabarda tur=fix, qamrov=points, tavsif esa qolgan qism.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Standart bo'lmagan tur",
        "title_ru": "Нестандартный тип",
        "description": "Ushbu repozitoriyaning real tarixidagi qaysi commit turi Conventional Commits STANDART ro'yxatida yo'q?",
        "description_ru": "Какой тип коммита из реальной истории этого репозитория ОТСУТСТВУЕТ в стандартном списке Conventional Commits?",
        "exercise_type": "multiple_choice",
        "options": ["feat", "chore", "debug", "refactor"],
        "options_ru": ["feat", "chore", "debug", "refactor"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Darsda \"debug: log openai url...\" commit'i alohida muhokama qilingan.",
        "hint_ru": "В уроке отдельно разобран коммит \"debug: log openai url...\".",
        "explanation": (
            "\"debug\" standart turlar ro'yxatida (feat, fix, docs, style, refactor, perf, "
            "test, chore, ci, build, revert) yo'q - u chore yoki fix sifatida yozilishi "
            "mumkin edi."
        ),
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Tur va ta'rifni moslashtiring",
        "title_ru": "Сопоставьте тип и определение",
        "description": "Har bir Conventional Commits turini uning ta'rifiga mos ravishda tartiblang (kartochkalarni ta'riflar tartibida joylang).",
        "description_ru": "Расположите карточки типов Conventional Commits в порядке, соответствующем их определениям.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["feat", "fix", "refactor", "chore"],
        "drag_items_ru": ["feat", "fix", "refactor", "chore"],
        "correct_order": ["feat", "fix", "refactor", "chore"],
        "hint": "Ta'riflar tartibi: yangi funksiya -> xato tuzatish -> xatti-harakat o'zgarmasdan tuzilish -> infratuzilma/skript.",
        "hint_ru": "Порядок определений: новая функция -> исправление ошибки -> изменение структуры без поведения -> инфраструктура/скрипты.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Tavsif maylini yozing",
        "title_ru": "Напишите наклонение описания",
        "description": "Conventional Commits'da tavsif qismi ___ maylida yoziladi (masalan \"add\", \"fix\", \"make\" - \"added\" emas).",
        "description_ru": "В Conventional Commits описание пишется в ___ наклонении (например \"add\", \"fix\", \"make\", а не \"added\").",
        "exercise_type": "fill_in_blank",
        "correct_answers": "buyruq",
        "correct_answers_ru": "повелительном",
        "hint": "Bu Git'ning o'z avtomatik xabarlarida ham ishlatiladigan uslub.",
        "hint_ru": "Этот стиль используется и в собственных автоматических сообщениях Git.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 3 — Atomik commit'lar vs "fix stuff" commit'lari
# ---------------------------------------------------------------------------

L3_TEXT = """
<h3>Atomik commit nima</h3>
<p><strong>Atomik commit</strong> — BITTA mantiqiy o'zgarishni o'z ichiga
olgan commit: bitta bug tuzatish, bitta kichik funksiya, bitta
refaktoring qadami. "Atomik" — bo'linmas degani: agar commit'ni ikkiga
bo'lish mumkin bo'lsa va ikkala bo'lak alohida mustaqil ma'noga ega
bo'lsa, u ehtimol ikkita commit bo'lishi kerak edi. Bunga qarama-qarshi —
"fix stuff", "wip", "more changes" kabi xabar bilan kelgan, o'zida
bir-biriga bog'liq bo'lmagan bir nechta o'zgarishni jamlagan commit.</p>

<h3>Nima uchun bu ahamiyatli — uchta aniq foyda</h3>
<ul>
<li><strong>git bisect uchun (112-kurs).</strong> 112-kursda
<code>git bisect</code>ni ikkilik qidiruv orqali xatoni topish uchun
o'rgangansiz. Agar bitta commit ikkita bog'liq bo'lmagan o'zgarishni
o'z ichiga olsa, bisect "shu commit yomon" deb topganda, QAYSI
o'zgarish aslida xatoga sabab bo'lganini bilib bo'lmaydi — ikkalasini
ham qo'lda tekshirish kerak bo'ladi.</li>
<li><strong>git revert uchun.</strong> Agar keyinchalik bitta o'zgarishni
bekor qilish kerak bo'lsa (masalan yangi funksiya muammoli chiqdi), lekin
u boshqa, muhim tuzatish bilan bitta commit'da bo'lsa, ikkalasini ham
birga bekor qilishga majbur bo'lasiz yoki qo'lda ajratib olishingiz
kerak bo'ladi.</li>
<li><strong>Review uchun (0-4-darslar).</strong> Kichik, bitta maqsadli
commit'ni ko'rib chiqish tezroq va aniqroq — reviewer "bu commit NIMA
qiladi" degan savolga bitta javob topadi. Katta, aralash commit reviewer'ni
"bu qism nima uchun shu yerda?" degan savolga majbur qiladi.</li>
</ul>

<h3><code>git add -p</code> — staging'ni nazorat qilish vositasi</h3>
<p>Amalda ko'pincha siz bir vaqtning o'zida ikki xil narsa ustida
ishlaysiz (masalan bug tuzatish + kichik refaktoring bir xil faylda), va
ularni ALOHIDA commit qilishni xohlaysiz. <code>git add -p</code>
(patch rejimi) faylni "hunk" (bo'lak)larga bo'lib, har birini alohida
staging'ga qo'shish yoki qo'shmaslikni so'raydi — butun faylni emas.
Shu tarzda bitta fayldagi ikki xil o'zgarishni ikkita alohida, atomik
commit'ga ajratish mumkin, hattoki ular bitta ish sessiyasida yozilgan
bo'lsa ham.</p>

<h3>Real misol: hatto intizomli tarixda ham chetga chiqish bo'ladi</h3>
<p>Bu platformaning o'z tarixidagi <code>e6c19f2 fix: correct
multiple_choice grading and project points display</code> commit'ini
diqqat bilan o'qib chiqamiz. Uning tavsifi ikkita ALOHIDA, bir-biriga
bog'liq bo'lmagan tuzatishni tasvirlaydi: (1)
<code>exercise_service.py</code>da grading (baholash) xatosi va (2)
<code>students.py</code>da profil sahifasidagi ball ko'rsatish xatosi.
Ikkalasi ham "fix" turida, lekin ular MUSTAQIL fayllarda, MUSTAQIL
sabablarga ko'ra tuzatilgan — biri talabaning javobi qanday baholanishi,
ikkinchisi profil sahifasida qancha ball ko'rsatilishi haqida. Agar
kelajakda ikkinchi tuzatish muammo keltirib chiqarsa (masalan noto'g'ri
filtr), uni birinchisidan ajratib revert qilish endi bitta commit'ni
qo'lda kesish talab qiladi. Bu — hatto juda intizomli, Conventional
Commits formatiga rioya qiladigan tarixda ham ikkita mustaqil tuzatishni
ikkita alohida commit'ga bo'lish mumkin (va ehtimol kerak) bo'lgan real
misol.</p>
<p>Solishtirish uchun, <code>refactor+test: split team_game.py,
achievement_service.py; add 27 new tests</code> commit'i xabarning
o'zida IKKITA tur (<code>refactor+test</code>) borligini ko'rsatadi —
lekin bu holatda ikkalasi bog'liq: kodni bo'lish va shu bo'linishni
tasdiqlovchi testlarni qo'shish odatda BIR ish birligi sifatida
qaraladi (refaktoring test bilan birga kelishi kerak). Farq shunda: bir
xil MAQSADGA xizmat qiladigan ikki turdagi o'zgarish (refactor+test)
bitta commit'da qolishi mumkin, lekin ikkita MUSTAQIL MAQSADGA xizmat
qiladigan ikki tuzatish (grading bug + ball ko'rsatish bug'i) alohida
bo'lishi kerak edi.</p>

<h3>Atomik tarix vs aralash "katta blob" — solishtiring</h3>
<pre class="mermaid">
flowchart TB
  subgraph A["Atomik tarix - har biri BITTA maqsad"]
    direction TB
    A1["fix(scoring): guard against
self-contradictory grading"]
    A2["fix(students): filter project
points by approved status"]
    A1 --> A2
  end
  subgraph B["Aralash 'katta blob' - ikki maqsad birga"]
    direction TB
    B1["fix: correct multiple_choice
grading AND points display"]
  end
  A --> R1["git revert A2 -> faqat
ball ko'rsatishni bekor qiladi"]
  B --> R2["git revert B1 -> IKKALASINI
ham bekor qiladi, xohlasa ham"]
  style A fill:#d6f5d6,stroke:#2a8a2a
  style B fill:#ffe9b3,stroke:#d09000
  style R2 fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Diagramma bir xil ikkita tuzatishni ikki xil tarzda commit qilish
oqibatini ko'rsatadi: atomik tarixda har birini alohida <code>git
revert</code> qilish mumkin; aralash "blob"da esa ikkalasi bir-biriga
"yopishib qolgan" — birini bekor qilish ikkinchisini ham majburan
bekor qiladi.</p>

<h3>Bu shuni anglatmaydiki, har doim mayda-mayda commit qiling</h3>
<p>Atomiklik "har bir qatorga alohida commit" degani emas — "har bir
commit BITTA tugallangan, mustaqil ma'noga ega o'zgarish" degani. Bitta
funksiya + uni tekshiruvchi test — odatda BITTA atomik commit (funksiya
testsiz "tugallangan" hisoblanmaydi). Ikki xil, bir-biriga aloqasi
yo'q bug tuzatish esa — ikkita alohida commit.</p>
""".strip()

L3_TEXT_RU = """
<h3>Что такое атомарный коммит</h3>
<p><strong>Атомарный коммит</strong> — коммит, содержащий ОДНО логическое
изменение: одно исправление бага, одну небольшую функцию, один шаг
рефакторинга. "Атомарный" значит неделимый: если коммит можно разделить
на два, и каждая часть имеет отдельный самостоятельный смысл, значит, он,
вероятно, должен был быть двумя коммитами. Противоположность —
коммит с сообщением вроде "fix stuff", "wip", "more changes",
объединяющий несколько несвязанных изменений.</p>

<h3>Почему это важно — три конкретные выгоды</h3>
<ul>
<li><strong>Для git bisect (курс 112).</strong> В курсе 112 вы изучили
<code>git bisect</code> для поиска ошибки бинарным поиском. Если один
коммит содержит два несвязанных изменения, и bisect определяет "этот
коммит плохой", невозможно узнать, КАКОЕ именно изменение вызвало
ошибку — оба придётся проверять вручную.</li>
<li><strong>Для git revert.</strong> Если позже нужно отменить одно
изменение (например, новая функция оказалась проблемной), но оно в одном
коммите с другим, важным исправлением, вы вынуждены отменить оба сразу
или вручную их разделять.</li>
<li><strong>Для ревью (уроки 0-4).</strong> Небольшой, целенаправленный
коммит проверяется быстрее и точнее — reviewer находит один ответ на
вопрос "что делает этот коммит". Большой смешанный коммит заставляет
reviewer задавать вопрос "почему эта часть здесь?".</li>
</ul>

<h3><code>git add -p</code> — инструмент контроля staging</h3>
<p>На практике вы часто работаете одновременно над двумя разными вещами
(например, исправление бага + небольшой рефакторинг в одном файле), и
хотите закоммитить их ОТДЕЛЬНО. <code>git add -p</code> (режим patch)
разбивает файл на "hunk" (куски) и спрашивает про каждый отдельно,
добавлять его в staging или нет — а не весь файл целиком. Так можно
разделить два разных изменения в одном файле на два отдельных атомарных
коммита, даже если они написаны в одной рабочей сессии.</p>

<h3>Реальный пример: отклонение бывает даже в дисциплинированной истории</h3>
<p>Внимательно прочитаем коммит <code>e6c19f2 fix: correct
multiple_choice grading and project points display</code> из собственной
истории этой платформы. Его описание описывает ДВА ОТДЕЛЬНЫХ, не
связанных друг с другом исправления: (1) ошибка баллинга (grading) в
<code>exercise_service.py</code> и (2) ошибка отображения баллов на
странице профиля в <code>students.py</code>. Оба типа "fix", но они в
НЕЗАВИСИМЫХ файлах, по НЕЗАВИСИМЫМ причинам — одно про то, как
оценивается ответ студента, второе — сколько баллов показывается на
странице профиля. Если в будущем второе исправление создаст проблему
(например, неверный фильтр), отделить его от первого при revert теперь
потребует ручного разрезания одного коммита. Это — реальный пример
того, что даже в очень дисциплинированной истории, следующей формату
Conventional Commits, два независимых исправления МОГЛИ (и, возможно,
должны были) быть двумя отдельными коммитами.</p>
<p>Для сравнения, коммит <code>refactor+test: split team_game.py,
achievement_service.py; add 27 new tests</code> показывает ДВА типа в
самом сообщении (<code>refactor+test</code>) — но в этом случае они
связаны: разделение кода и добавление тестов, подтверждающих это
разделение, обычно рассматриваются как ОДНА единица работы
(рефакторинг должен сопровождаться тестами). Разница в том, что два типа
изменения, служащие одной ЦЕЛИ (refactor+test), могут оставаться в одном
коммите, а два исправления, служащие двум НЕЗАВИСИМЫМ целям (баг
баллинга + отображение баллов), должны были быть раздельными.</p>

<h3>Атомарная история vs смешанный "большой блок" — сравните</h3>
<pre class="mermaid">
flowchart TB
  subgraph A["Атомарная история - каждый с ОДНОЙ целью"]
    direction TB
    A1["fix(scoring): guard against
self-contradictory grading"]
    A2["fix(students): filter project
points by approved status"]
    A1 --> A2
  end
  subgraph B["Смешанный 'большой блок' - две цели вместе"]
    direction TB
    B1["fix: correct multiple_choice
grading AND points display"]
  end
  A --> R1["git revert A2 -> отменяет
только отображение баллов"]
  B --> R2["git revert B1 -> отменяет
ОБА, даже если нужно только одно"]
  style A fill:#d6f5d6,stroke:#2a8a2a
  style B fill:#ffe9b3,stroke:#d09000
  style R2 fill:#ffd6d6,stroke:#cc3333
</pre>
<p>Диаграмма показывает последствие коммита одних и тех же двух
исправлений двумя разными способами: в атомарной истории каждое можно
<code>git revert</code> отдельно; в смешанном "блоке" оба "слиплись"
друг с другом — отмена одного принудительно отменяет и второе.</p>

<h3>Это не значит, что нужно коммитить каждую мелочь отдельно</h3>
<p>Атомарность не значит "отдельный коммит на каждую строку" — значит
"каждый коммит — ОДНО завершённое, самостоятельное изменение". Одна
функция + тест, проверяющий её — обычно ОДИН атомарный коммит (функция
без теста не считается "завершённой"). А два разных, не связанных друг с
другом исправления бага — два отдельных коммита.</p>
""".strip()

L3_CODE = """
# ============================================================
# git add -p orqali bitta fayldagi ikki xil o'zgarishni
# ikkita alohida, atomik commit'ga bo'lish
# ============================================================

# Faraz qilaylik, exercise_service.py'da BIR VAQTNING o'zida ikki xil
# ish qilingan: (1) grading bug tuzatildi, (2) keraksiz print() olib
# tashlandi (kichik tozalash). Bularni ALOHIDA commit qilamiz:

# 1-qadam: patch rejimida staging
# $ git add -p backend/app/services/exercise_service.py
#
# Git har bir hunk (o'zgargan bo'lak) uchun so'raydi:
#   Stage this hunk [y,n,q,a,d,s,e,?]?
#
# Faqat grading tuzatishga tegishli hunk'ni 'y' bilan tanlaymiz,
# print() olib tashlashga tegishli hunkni 's' (split) yoki 'n' bilan
# o'tkazib yuboramiz.

# 2-qadam: faqat tanlangan o'zgarish bilan atomik commit
# $ git commit -m "fix(scoring): guard multiple_choice grading against \\
#   comma-containing single-select answers"

# 3-qadam: qolgan o'zgarishni (print() olib tashlash) ALOHIDA staging'ga
# $ git add -p backend/app/services/exercise_service.py
# (bu safar qolgan hunk'ni 'y' bilan tanlaymiz)

# 4-qadam: ikkinchi, mustaqil atomik commit
# $ git commit -m "chore(scoring): remove leftover debug print statement"

# ============================================================
# Natija: bitta ish sessiyasida yozilgan ikki xil o'zgarish endi
# IKKITA mustaqil commit - har birini alohida revert qilish,
# alohida bisect orqali topish, alohida review qilish mumkin.
# ============================================================

# ------------------------------------------------------------
# Solishtirish uchun: agar ALOHIDA commit qilinmaganida
# ------------------------------------------------------------
# $ git add backend/app/services/exercise_service.py   # BUTUN faylni
# $ git commit -m "fix: correct grading and clean up code"
#
# Endi ikkala o'zgarish BITTA commit'da - agar print() olib tashlash
# kutilmagan yon ta'sir keltirib chiqarsa (masalan log monitoring shu
# print()ga bog'liq bo'lib qolgan bo'lsa), uni grading tuzatishidan
# ajratib revert qilish endi qo'lda diff kesishni talab qiladi.
""".strip()

L3_CODE_RU = """
# ============================================================
# Разделение двух разных изменений в одном файле на два
# отдельных атомарных коммита через git add -p
# ============================================================

# Предположим, в exercise_service.py ОДНОВРЕМЕННО сделаны два разных
# дела: (1) исправлен баг grading, (2) убран ненужный print() (мелкая
# чистка). Коммитим их ОТДЕЛЬНО:

# Шаг 1: staging в режиме patch
# $ git add -p backend/app/services/exercise_service.py
#
# Git спрашивает про каждый hunk (изменённый кусок):
#   Stage this hunk [y,n,q,a,d,s,e,?]?
#
# Выбираем 'y' только для hunk'а, относящегося к исправлению grading,
# hunk с удалением print() пропускаем через 's' (split) или 'n'.

# Шаг 2: атомарный коммит только с выбранным изменением
# $ git commit -m "fix(scoring): guard multiple_choice grading against \\
#   comma-containing single-select answers"

# Шаг 3: оставшееся изменение (удаление print()) ОТДЕЛЬНО в staging
# $ git add -p backend/app/services/exercise_service.py
# (на этот раз выбираем оставшийся hunk через 'y')

# Шаг 4: второй, независимый атомарный коммит
# $ git commit -m "chore(scoring): remove leftover debug print statement"

# ============================================================
# Результат: два разных изменения, написанных за одну рабочую сессию,
# теперь ДВА независимых коммита - каждый можно отдельно откатить,
# отдельно найти через bisect, отдельно проверить на ревью.
# ============================================================

# ------------------------------------------------------------
# Для сравнения: если бы НЕ были закоммичены отдельно
# ------------------------------------------------------------
# $ git add backend/app/services/exercise_service.py   # ВЕСЬ файл
# $ git commit -m "fix: correct grading and clean up code"
#
# Теперь оба изменения в ОДНОМ коммите - если удаление print() вызовет
# неожиданный побочный эффект (например, мониторинг логов зависел от
# этого print()), отделить его от исправления grading при откате теперь
# потребует ручного разрезания diff.
""".strip()

L3_TASK = {
    "task_title": "Bitta faylda ikki xil o'zgarishni ikkita atomik commit'ga bo'ling",
    "task_title_ru": "Разделите два изменения в одном файле на два атомарных коммита",
    "task_description": (
        "Shaxsiy repozitoriyangizda bitta faylga IKKITA bir-biriga bog'liq "
        "bo'lmagan o'zgarish kiriting (masalan bitta bug tuzatish + bitta "
        "keraksiz kodni olib tashlash). git add -p (yoki IDE'ning "
        "\"stage hunk\" funksiyasi) yordamida ularni IKKITA alohida, "
        "Conventional Commits formatidagi atomik commit'ga ajrating."
    ),
    "task_description_ru": (
        "В своём репозитории внесите ДВА не связанных друг с другом "
        "изменения в один файл (например, одно исправление бага + удаление "
        "одного ненужного кода). С помощью git add -p (или функции "
        "\"stage hunk\" в IDE) разделите их на ДВА отдельных атомарных "
        "коммита в формате Conventional Commits."
    ),
    "task_requirements": (
        "1) Ikkala commit ham bitta faylga tegishli, lekin turli hunk'lardan "
        "iborat bo'lishi kerak. 2) Har biri alohida, mustaqil ma'noli "
        "Conventional Commits xabariga ega bo'lishi shart. 3) "
        "`git log -p` chiqishi ilova qilinishi kerak - ikkala commit ham "
        "aniq ko'rinadigan bo'lishi uchun."
    ),
    "task_requirements_ru": (
        "1) Оба коммита должны относиться к одному файлу, но к разным "
        "hunk'ам. 2) Каждый должен иметь отдельное, самостоятельное "
        "сообщение в формате Conventional Commits. 3) Приложить вывод "
        "`git log -p`, чтобы оба коммита были ясно видны."
    ),
    "task_technologies": "Git (add -p, commit)",
    "task_deadline_days": 3,
}

L3_SAMPLE = {
    "title": "Namuna: atomik vs aralash commit tarixini taqqoslash skripti",
    "description": (
        "Ushbu darsning kod namunasi asosida, ikkita xayoliy commit "
        "tarixini (atomik va aralash) taqqoslab, git revert qanday "
        "natija berishini simulyatsiya qiladigan skript."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "compare_commit_history.py",
            "language": "python",
            "code": (
                "\"\"\"Ikkita commit tarixi strategiyasini taqqoslash: har biri\n"
                "revert qilinganda nima bekor bo'lishini ko'rsatadi.\"\"\"\n\n"
                "atomic_history = [\n"
                "    {\"hash\": \"a1\", \"msg\": \"fix(scoring): guard self-contradictory grading\", \"touches\": {\"grading\"}},\n"
                "    {\"hash\": \"a2\", \"msg\": \"fix(students): filter project points by approved status\", \"touches\": {\"points_display\"}},\n"
                "]\n\n"
                "mixed_history = [\n"
                "    {\"hash\": \"b1\", \"msg\": \"fix: correct multiple_choice grading AND points display\", \"touches\": {\"grading\", \"points_display\"}},\n"
                "]\n\n\n"
                "def revert(history, target_touches):\n"
                "    \"\"\"target_touches bilan bog'liq commit'larni topib, ular\n"
                "    NIMANI qamrab olishini (touches) qaytaradi.\"\"\"\n"
                "    affected = set()\n"
                "    for commit in history:\n"
                "        if commit[\"touches\"] & target_touches:\n"
                "            affected |= commit[\"touches\"]\n"
                "    return affected\n\n\n"
                "print(\"Faqat 'points_display'ni bekor qilmoqchimiz:\")\n"
                "print(\"  Atomik tarixda:\", revert(atomic_history, {\"points_display\"}))\n"
                "print(\"  Aralash tarixda:\", revert(mixed_history, {\"points_display\"}))\n"
                "# Atomik: {'points_display'} - faqat kerakli qism\n"
                "# Aralash: {'grading', 'points_display'} - grading HAM majburan qo'shiladi!\n"
            ),
        }
    ],
}

L3_EXERCISES = [
    {
        "title": "Atomik commit ta'rifi",
        "title_ru": "Определение атомарного коммита",
        "description": "Atomik commit'ning eng to'g'ri ta'rifi qaysi?",
        "description_ru": "Какое определение атомарного коммита наиболее точное?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir o'zgargan qatorga alohida commit",
            "Kuniga bittadan ko'p bo'lmagan commit",
            "Bitta mantiqiy, mustaqil ma'noga ega o'zgarishni o'z ichiga olgan commit",
            "Faqat bitta faylga tegishli commit",
        ],
        "options_ru": [
            "Отдельный коммит на каждую изменённую строку",
            "Не более одного коммита в день",
            "Коммит, содержащий одно логическое, самостоятельное изменение",
            "Коммит, относящийся только к одному файлу",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Darsning oxirida aytilgan: \"har bir qatorga alohida commit\" degani EMAS.",
        "hint_ru": "В конце урока сказано: НЕ значит \"отдельный коммит на каждую строку\".",
        "explanation": (
            "Atomiklik mustaqil MANTIQIY birlik haqida, fayl soni yoki qator soni haqida "
            "emas. Bitta funksiya + uni testi odatda bitta atomik commit bo'lishi mumkin."
        ),
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "e6c19f2 nega ikkiga bo'linishi kerak edi",
        "title_ru": "Почему e6c19f2 стоило разделить на два",
        "description": (
            "e6c19f2 commit'i nima uchun ikkita atomik commit'ga bo'linishi mumkin (va "
            "ehtimol kerak) edi?"
        ),
        "description_ru": (
            "Почему коммит e6c19f2 мог (и, вероятно, должен был) быть разделён на два "
            "атомарных коммита?"
        ),
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki u \"fix\" turida yozilgan",
            "Chunki u ikkita mustaqil faylda, ikkita mustaqil sababga ko'ra tuzatish kiritgan",
            "Chunki u juda uzun tavsifga ega edi",
            "Chunki unda hech qanday qamrov (scope) ko'rsatilmagan",
        ],
        "options_ru": [
            "Потому что он был написан с типом \"fix\"",
            "Потому что он вносил исправления в два независимых файла по двум независимым причинам",
            "Потому что у него было слишком длинное описание",
            "Потому что в нём не была указана область (scope)",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Grading bug va ball ko'rsatish bug'i bir-biriga bog'liq emas edi.",
        "hint_ru": "Баг grading и баг отображения баллов не были связаны друг с другом.",
        "explanation": (
            "Ikkala tuzatish MUSTAQIL fayllarda (exercise_service.py va students.py) va "
            "MUSTAQIL sabablarga ko'ra qilingan - bu ularni ikkita alohida, revert "
            "qilinishi mumkin bo'lgan commit qilish uchun asosiy mezon."
        ),
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "git add -p qadamlarini tartiblang",
        "title_ru": "Расположите шаги git add -p по порядку",
        "description": "Bitta fayldagi ikki xil o'zgarishni ikkita atomik commit'ga ajratish qadamlarini tartiblang.",
        "description_ru": "Расположите шаги разделения двух изменений в одном файле на два атомарных коммита.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git add -p bilan birinchi hunk'ni tanlash",
            "Birinchi atomik commit qilish",
            "git add -p bilan qolgan hunk'ni tanlash",
            "Ikkinchi atomik commit qilish",
        ],
        "drag_items_ru": [
            "Выбрать первый hunk через git add -p",
            "Сделать первый атомарный коммит",
            "Выбрать оставшийся hunk через git add -p",
            "Сделать второй атомарный коммит",
        ],
        "correct_order": [
            "git add -p bilan birinchi hunk'ni tanlash",
            "Birinchi atomik commit qilish",
            "git add -p bilan qolgan hunk'ni tanlash",
            "Ikkinchi atomik commit qilish",
        ],
        "hint": "Har safar: avval tanlash (add -p), keyin commit - va bu juftlik ikki marta takrorlanadi.",
        "hint_ru": "Каждый раз: сначала выбор (add -p), потом коммит - и эта пара повторяется дважды.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Fayl bo'laklarini tanlash buyrug'i",
        "title_ru": "Команда выбора частей файла",
        "description": "Butun faylni emas, balki uning alohida bo'laklarini (hunk) staging'ga qo'shish uchun: git add ___",
        "description_ru": "Чтобы добавить в staging не весь файл, а его отдельные части (hunk): git add ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "-p",
        "correct_answers_ru": "-p",  # CLI flag, identical literal in both languages — the
        # heuristic flags any short alphabetic string as "natural language" even
        # though "-p" is a literal git flag with no translation; set explicitly
        # identical rather than leaving it to be reported as a gap.
        "hint": "\"Patch\" rejimini yoqadigan bitta harfli flag.",
        "hint_ru": "Однобуквенный флаг, включающий режим \"patch\".",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 4 — Samarali review qilish: nimalarga e'tibor berish kerak
# ---------------------------------------------------------------------------

L4_TEXT = """
<h3>Reviewer sifatida vaqtingizni qayerga sarflash kerak</h3>
<p>0-darsda aytilganidek, code review'ning eng katta xatosi — uni uslub
(formatlash, qavs joylashuvi) muhokamasiga aylantirish. Bu — vaqtni
noto'g'ri joyga sarflash: uslubni linter/formatter avtomatik tekshiradi
(masalan bu platformaning <code>test.yml</code>'ida sinovlar avtomatik
ishga tushadi), inson e'tibori esa MASHINA topa OLMAYDIGAN narsalarga
qaratilishi kerak. To'rt ustuvor yo'nalish bor, va ular AYNAN shu
tartibda muhim.</p>

<h3>1. To'g'rilik (Correctness) — birinchi va eng muhim</h3>
<p>"Bu kod REJALASHTIRILGANDEK ishlaydimi?" Bu — chekka holatlarni
(edge case) qidirish: bo'sh ro'yxat, <code>None</code> qiymat, noldan
bo'lish, bir vaqtning o'zida ikki so'rov (race condition). 0-darsdagi
misolni eslang: <code>correct_answers.split(",")</code> HAR DOIM
ishlatilgani, holbuki bitta tanlovli javob matnida vergul bo'lishi
mumkinligi hisobga olinmagan edi — bu aynan to'g'rilik muammosi, uslub
emas.</p>

<h3>2. Xavfsizlik (Security)</h3>
<p>Foydalanuvchi kiritgan ma'lumot to'g'ridan-to'g'ri SQL so'roviga
qo'shilmayaptimi (SQL injection)? Maxfiy kalitlar (API key, parol) kodda
qattiq yozilmaganmi (hardcoded secret)? Foydalanuvchi HTML'i tozalanmasdan
sahifaga chiqarilmayaptimi (XSS)? Bu savollar har bir PR'da so'ralishi
shart emas — faqat foydalanuvchi kirishini, autentifikatsiyani yoki
maxfiy ma'lumotni qayta ishlaydigan kod uchun — lekin ular UNUTILMASLIGI
kerak bo'lgan tekshiruv.</p>

<h3>3. Testlar (Tests)</h3>
<p>Yangi funksiya yoki tuzatish uchun test yozilganmi? Test faqat
"muvaffaqiyatli" holatni emas, balki chekka holatni ham tekshiradimi?
Diqqat: "test bor" — "test YETARLI" degani emas. Reviewer o'zidan
so'rashi kerak: "agar men bu funksiyani BUZSAM, test buni ushlab
qoladimi?"</p>

<h3>4. O'qilishi (Readability) — muhim, lekin oxirgi</h3>
<p>Kod boshqa dasturchi (yoki olti oydan keyingi O'ZINGIZ) uchun
tushunarlimi? O'zgaruvchi nomlari mazmunga mos keladimi? Bu muhim, lekin
TO'G'RILIK va XAVFSIZLIKDAN keyin keladi — mukammal o'qiladigan, lekin
noto'g'ri ishlaydigan kod baribir noto'g'ri.</p>

<h3>Uslub nima uchun ustuvorlik RO'YXATIDA yo'q</h3>
<p>Qavs qayerda turishi, bo'sh joy soni, satr uzunligi — булар reviewer
vaqtini band qilmasligi kerak, chunki ular AVTOMATLASHTIRILADI. Agar
loyihada linter sozlanmagan bo'lsa, bu ALOHIDA muammo (uni sozlash kerak,
review paytida qo'lda muhokama qilish emas). Agar reviewer uslub haqida
izoh qoldirmoqchi bo'lsa, buni <code>nit:</code> prefiksi bilan (6-darsda
ko'ramiz) ixtiyoriy, bloklamaydigan izoh sifatida belgilashi kerak.</p>

<h3>To'rt ustuvorlik va ularning oqibati</h3>
<pre class="mermaid">
flowchart TB
  PR["Kiruvchi PR"] --> C{"1. To'g'rilik:
chekka holatlar to'g'ri?"}
  C -->|"yo'q"| BLOCK1["Changes requested
(bloklaydi)"]
  C -->|"ha"| S{"2. Xavfsizlik:
secret/injection/XSS yo'qmi?"}
  S -->|"yo'q"| BLOCK2["Changes requested
(bloklaydi)"]
  S -->|"ha"| T{"3. Testlar:
chekka holat qamrab olinganmi?"}
  T -->|"yo'q"| BLOCK3["Changes requested
(bloklaydi)"]
  T -->|"ha"| R{"4. O'qilishi:
tushunarlimi?"}
  R -->|"yo'q"| NIT["nit: izoh
(BLOKLAMAYDI)"]
  R -->|"ha"| APP["Approved"]
  NIT --> APP
  style BLOCK1 fill:#ffd6d6,stroke:#cc3333
  style BLOCK2 fill:#ffd6d6,stroke:#cc3333
  style BLOCK3 fill:#ffd6d6,stroke:#cc3333
  style NIT fill:#fff3cd,stroke:#d0a000
  style APP fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma to'rtta ustuvorlikning MUHIM farqini ko'rsatadi: birinchi
uchtasi (to'g'rilik, xavfsizlik, testlar) YETISHMASA, bu PR'ni
BLOKLAYDI — "changes requested" holatiga qaytaradi. To'rtinchisi
(o'qilish) esa odatda faqat <code>nit:</code> (ixtiyoriy) izoh sifatida
qoldiriladi va PR'ni bloklamaydi. Bu tartibni chalkashtirish (masalan
o'zgaruvchi nomi haqida bahslashib, N+1 so'rovni payqamaslik) review
sifatini pasaytiradi.</p>

<h3>CI bilan bo'linish: nimani INSON, nimani MASHINA tekshiradi</h3>
<p>117-kursda ko'rgan <code>test.yml</code> — pytest va Jest testlarini
avtomatik ishga tushiradi. Bu degani: reviewer "testlar o'tdimi?" deb
qo'lda tekshirmaydi — CI status belgisi (yashil/qizil) buni allaqachon
ko'rsatib turibdi. Reviewer'ning vazifasi — "YETARLI test bormi, TO'G'RI
holatni tekshirayaptimi" kabi CI AVTOMATIK ANIQLAY OLMAYDIGAN savollarga
javob berish.</p>
""".strip()

L4_TEXT_RU = """
<h3>Куда reviewer'у стоит тратить своё время</h3>
<p>Как говорилось в уроке 0, самая большая ошибка code review — превратить
его в обсуждение стиля (форматирование, расположение скобок). Это —
неправильное расходование времени: стиль автоматически проверяется
линтером/форматтером (например, в <code>test.yml</code> этой платформы
тесты запускаются автоматически), а внимание человека должно быть
направлено на то, что МАШИНА НЕ МОЖЕТ найти. Есть четыре приоритетных
направления, и они важны ИМЕННО в этом порядке.</p>

<h3>1. Правильность (Correctness) — первое и самое важное</h3>
<p>"Работает ли этот код так, как ЗАДУМАНО?" Это — поиск граничных
случаев (edge case): пустой список, значение <code>None</code>, деление
на ноль, одновременный запрос (race condition). Вспомните пример из
урока 0: <code>correct_answers.split(",")</code> использовался ВСЕГДА,
хотя не было учтено, что текст ответа с одним выбором может содержать
запятую — это именно проблема правильности, а не стиля.</p>

<h3>2. Безопасность (Security)</h3>
<p>Не добавляются ли введённые пользователем данные напрямую в SQL-запрос
(SQL injection)? Не захардкожены ли секретные ключи (API key, пароль) в
коде? Не выводится ли HTML пользователя на страницу без очистки (XSS)?
Эти вопросы не нужно задавать в каждом PR — только для кода,
обрабатывающего пользовательский ввод, аутентификацию или секретные
данные — но их НЕЛЬЗЯ ЗАБЫВАТЬ проверять.</p>

<h3>3. Тесты (Tests)</h3>
<p>Написан ли тест для новой функции или исправления? Проверяет ли тест
не только "успешный" случай, но и граничный? Внимание: "тест есть" не
значит "тест ДОСТАТОЧЕН". Reviewer должен спросить себя: "если я СЛОМАЮ
эту функцию, поймает ли это тест?"</p>

<h3>4. Читаемость (Readability) — важно, но в конце</h3>
<p>Понятен ли код другому разработчику (или ВАМ САМИМ через полгода)?
Соответствуют ли имена переменных смыслу? Это важно, но идёт ПОСЛЕ
правильности и безопасности — идеально читаемый, но неправильно
работающий код всё равно неправильный.</p>

<h3>Почему стиля нет в списке приоритетов</h3>
<p>Расположение скобок, количество пробелов, длина строки — это НЕ
должно занимать время reviewer'а, потому что это АВТОМАТИЗИРУЕТСЯ. Если
в проекте не настроен линтер, это ОТДЕЛЬНАЯ проблема (её нужно настроить,
а не обсуждать вручную на ревью). Если reviewer всё же хочет оставить
комментарий о стиле, он должен пометить его префиксом <code>nit:</code>
(увидим в уроке 6) как необязательный, неблокирующий комментарий.</p>

<h3>Четыре приоритета и их последствие</h3>
<pre class="mermaid">
flowchart TB
  PR["Входящий PR"] --> C{"1. Правильность:
граничные случаи верны?"}
  C -->|"нет"| BLOCK1["Changes requested
(блокирует)"]
  C -->|"да"| S{"2. Безопасность:
нет secret/injection/XSS?"}
  S -->|"нет"| BLOCK2["Changes requested
(блокирует)"]
  S -->|"да"| T{"3. Тесты:
граничный случай покрыт?"}
  T -->|"нет"| BLOCK3["Changes requested
(блокирует)"]
  T -->|"да"| R{"4. Читаемость:
понятно?"}
  R -->|"нет"| NIT["nit: комментарий
(НЕ БЛОКИРУЕТ)"]
  R -->|"да"| APP["Approved"]
  NIT --> APP
  style BLOCK1 fill:#ffd6d6,stroke:#cc3333
  style BLOCK2 fill:#ffd6d6,stroke:#cc3333
  style BLOCK3 fill:#ffd6d6,stroke:#cc3333
  style NIT fill:#fff3cd,stroke:#d0a000
  style APP fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает важное различие между четырьмя приоритетами:
первые три (правильность, безопасность, тесты), если не выполнены,
БЛОКИРУЮТ PR — возвращают его в состояние "changes requested". Четвёртый
(читаемость) обычно оставляется только как <code>nit:</code>
(необязательный) комментарий и не блокирует PR. Путаница в этом порядке
(например, спор об имени переменной при пропуске запроса N+1) снижает
качество ревью.</p>

<h3>Разделение с CI: что проверяет ЧЕЛОВЕК, что МАШИНА</h3>
<p><code>test.yml</code> из курса 117 автоматически запускает тесты
pytest и Jest. Это значит: reviewer НЕ проверяет вручную "прошли ли
тесты?" — статус CI (зелёный/красный) уже это показывает. Задача
reviewer'а — отвечать на вопросы, которые CI АВТОМАТИЧЕСКИ определить НЕ
МОЖЕТ, например "ДОСТАТОЧНО ли тестов, ПРАВИЛЬНЫЙ ли случай проверяется".</p>
""".strip()

L4_CODE = """
# ============================================================
# Review checklist - real PR uchun to'rt ustuvorlik bo'yicha
# tekshiruv (bu platformaning e6c19f2 xatosi misolida)
# ============================================================

REVIEW_CHECKLIST = {
    "1_correctness": [
        "Chekka holatlar (bo'sh, None, 0, juda katta qiymat) ko'rib chiqilganmi?",
        "Taxmin (masalan 'har doim vergul bo'yicha bo'linadi') HAR DOIM to'g'rimi,"
        " yoki faqat ba'zi holatlarda?",
        "Race condition (bir vaqtda ikki so'rov) bo'lishi mumkinmi?",
    ],
    "2_security": [
        "Foydalanuvchi kiritgan ma'lumot to'g'ridan-to'g'ri SQL/shell buyrug'iga qo'shilmayaptimi?",
        "Maxfiy kalit (API key, parol) kodda qattiq yozilmaganmi?",
        "Foydalanuvchi HTML'i tozalanmasdan chiqarilmayaptimi (XSS)?",
    ],
    "3_tests": [
        "Yangi xatti-harakat uchun test bormi?",
        "Test faqat 'muvaffaqiyatli' holatni emas, chekka holatni ham tekshiradimi?",
        "Agar bu funksiya buzilsa, test buni ushlab qoladimi?",
    ],
    "4_readability": [
        "O'zgaruvchi va funksiya nomlari mazmunga mos keladimi?",
        "Funksiya bir vaqtning o'zida bir nechta ishni qilmayaptimi?",
        "(BU band uslub emas - agar faqat qavs/bo'sh joy bo'lsa, nit: bilan belgilang)",
    ],
}


def review_pr(diff_summary: dict) -> str:
    \"\"\"Sodda simulyatsiya: birinchi uchta band bo'yicha muammo topilsa,
    PR bloklanadi; to'rtinchisi faqat nit: sifatida qoldiriladi.\"\"\"
    for priority in ("1_correctness", "2_security", "3_tests"):
        if diff_summary.get(priority) is False:
            return f"Changes requested - {priority} bo'yicha muammo bor"
    if diff_summary.get("4_readability") is False:
        return "Approved (nit: readability bo'yicha ixtiyoriy izoh qoldirildi)"
    return "Approved"


# e6c19f2'dagi grading bug'i review qilinganda TO'G'RILIK bandida
# aniqlanishi kerak edi:
example_diff = {"1_correctness": False, "2_security": True, "3_tests": True, "4_readability": True}
print(review_pr(example_diff))
# Natija: "Changes requested - 1_correctness bo'yicha muammo bor"
""".strip()

L4_CODE_RU = """
# ============================================================
# Чек-лист ревью - проверка по четырём приоритетам для
# реального PR (на примере ошибки e6c19f2 этой платформы)
# ============================================================

REVIEW_CHECKLIST = {
    "1_correctness": [
        "Рассмотрены ли граничные случаи (пусто, None, 0, слишком большое значение)?",
        "Предположение (например 'всегда разбивается по запятой') верно ВСЕГДА,"
        " или только в некоторых случаях?",
        "Возможен ли race condition (два запроса одновременно)?",
    ],
    "2_security": [
        "Не добавляются ли введённые пользователем данные напрямую в SQL/shell-команду?",
        "Не захардкожен ли секретный ключ (API key, пароль) в коде?",
        "Не выводится ли HTML пользователя без очистки (XSS)?",
    ],
    "3_tests": [
        "Есть ли тест для нового поведения?",
        "Проверяет ли тест не только 'успешный' случай, но и граничный?",
        "Если эта функция сломается, поймает ли это тест?",
    ],
    "4_readability": [
        "Соответствуют ли имена переменных и функций смыслу?",
        "Не делает ли функция сразу несколько дел одновременно?",
        "(ЭТО не про стиль - если только скобки/пробелы, помечайте через nit:)",
    ],
}


def review_pr(diff_summary: dict) -> str:
    \"\"\"Простая симуляция: если найдена проблема по первым трём пунктам,
    PR блокируется; четвёртый оставляется только как nit:.\"\"\"
    for priority in ("1_correctness", "2_security", "3_tests"):
        if diff_summary.get(priority) is False:
            return f"Changes requested - проблема по {priority}"
    if diff_summary.get("4_readability") is False:
        return "Approved (nit: необязательный комментарий по читаемости оставлен)"
    return "Approved"


# Баг grading в e6c19f2 при ревью должен был быть найден в пункте
# ПРАВИЛЬНОСТЬ:
example_diff = {"1_correctness": False, "2_security": True, "3_tests": True, "4_readability": True}
print(review_pr(example_diff))
# Результат: "Changes requested - проблема по 1_correctness"
""".strip()

L4_TASK = {
    "task_title": "To'rt ustuvorlik bo'yicha real PR'ni tahlil qiling",
    "task_title_ru": "Проанализируйте реальный PR по четырём приоритетам",
    "task_description": (
        "0-darsda tanlagan (yoki yangi) ochiq-manba PR'ni to'rt ustuvorlik "
        "(to'g'rilik, xavfsizlik, testlar, o'qilishi) bo'yicha alohida-alohida "
        "tahlil qiling. Har bir band uchun: shu PR'da ushbu band bo'yicha "
        "izoh qoldirilganmi (agar reviewer izohlarini o'qish mumkin bo'lsa) "
        "yoki sizning fikringizcha nima e'tiborga olinishi kerak edi."
    ),
    "task_description_ru": (
        "Проанализируйте PR из open source (выбранный в уроке 0, или новый) "
        "отдельно по каждому из четырёх приоритетов (правильность, "
        "безопасность, тесты, читаемость). Для каждого пункта: был ли "
        "оставлен комментарий по этому пункту в этом PR (если можно прочитать "
        "комментарии reviewer'а), или что, по-вашему, следовало учесть."
    ),
    "task_requirements": (
        "1) Har bir 4 ustuvorlik uchun alohida bo'lim bo'lishi kerak. "
        "2) Kamida bitta bandda reviewer real izoh qoldirganini toping va "
        "iqtibos keltiring. 3) Agar biror band bo'yicha hech qanday izoh "
        "topilmasa, buning sababini taxmin qiling (masalan kod juda oddiy edi)."
    ),
    "task_requirements_ru": (
        "1) Для каждого из 4 приоритетов - отдельный раздел. 2) Найдите и "
        "процитируйте минимум один реальный комментарий reviewer'а по одному "
        "из пунктов. 3) Если по какому-то пункту комментариев не найдено, "
        "предположите причину (например, код был слишком простым)."
    ),
    "task_technologies": "GitHub (Pull Requests), yozma tahlil",
    "task_deadline_days": 4,
}

L4_SAMPLE = {
    "title": "Namuna: to'rt ustuvorlikni tekshiruvchi review checklist skripti",
    "description": (
        "Ushbu darsning kod namunasi asosida, to'rtta ustuvorlik bo'yicha "
        "diff'ni baholaydigan va Approved/Changes requested qaytaradigan "
        "to'liq ishlaydigan Python skripti."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "review_checklist.py",
            "language": "python",
            "code": (
                "\"\"\"Sodda review-checklist simulyatori - haqiqiy PR baholash\n"
                "jarayonini soddalashtirib ko'rsatadi.\"\"\"\n\n"
                "PRIORITY_ORDER = [\"correctness\", \"security\", \"tests\", \"readability\"]\n"
                "BLOCKING = {\"correctness\", \"security\", \"tests\"}\n\n\n"
                "def review(findings: dict[str, bool]) -> dict:\n"
                "    \"\"\"findings: {\"correctness\": True/False, ...} - True = muammo yo'q.\n"
                "    Qaytaradi: {\"decision\": ..., \"blocking_issues\": [...], \"nits\": [...]}\n"
                "    \"\"\"\n"
                "    blocking_issues = [p for p in PRIORITY_ORDER if p in BLOCKING and not findings.get(p, True)]\n"
                "    nits = [p for p in PRIORITY_ORDER if p not in BLOCKING and not findings.get(p, True)]\n"
                "    decision = \"Changes requested\" if blocking_issues else \"Approved\"\n"
                "    return {\"decision\": decision, \"blocking_issues\": blocking_issues, \"nits\": nits}\n\n\n"
                "if __name__ == \"__main__\":\n"
                "    # e6c19f2 uslubidagi xato: to'g'rilik bandida muammo\n"
                "    result = review({\"correctness\": False, \"security\": True, \"tests\": True, \"readability\": True})\n"
                "    print(result)\n"
                "    # {'decision': 'Changes requested', 'blocking_issues': ['correctness'], 'nits': []}\n\n"
                "    # Faqat o'qilishda kichik izoh - bloklamaydi\n"
                "    result2 = review({\"correctness\": True, \"security\": True, \"tests\": True, \"readability\": False})\n"
                "    print(result2)\n"
                "    # {'decision': 'Approved', 'blocking_issues': [], 'nits': ['readability']}\n"
            ),
        }
    ],
}

L4_EXERCISES = [
    {
        "title": "To'rt ustuvorlikning tartibi",
        "title_ru": "Порядок четырёх приоритетов",
        "description": "Review paytida e'tibor berish kerak bo'lgan to'rtta narsaning TO'G'RI ustuvorlik tartibi qaysi?",
        "description_ru": "Какой порядок приоритетов правильный для четырёх вещей, на которые нужно обращать внимание на ревью?",
        "exercise_type": "multiple_choice",
        "options": [
            "O'qilishi -> Testlar -> Xavfsizlik -> To'g'rilik",
            "To'g'rilik -> Xavfsizlik -> Testlar -> O'qilishi",
            "Uslub -> To'g'rilik -> Xavfsizlik -> Testlar",
            "Testlar -> O'qilishi -> To'g'rilik -> Xavfsizlik",
        ],
        "options_ru": [
            "Читаемость -> Тесты -> Безопасность -> Правильность",
            "Правильность -> Безопасность -> Тесты -> Читаемость",
            "Стиль -> Правильность -> Безопасность -> Тесты",
            "Тесты -> Читаемость -> Правильность -> Безопасность",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Uslub ro'yxatda umuman yo'q - u avtomatlashtiriladi.",
        "hint_ru": "Стиля вообще нет в списке - он автоматизируется.",
        "explanation": "To'g'ri tartib: to'g'rilik, xavfsizlik, testlar, o'qilishi - uslub ro'yxatda yo'q, chunki u avtomatlashtiriladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Bloklovchi vs bloklamaydigan izoh",
        "title_ru": "Блокирующий против неблокирующего комментария",
        "description": "Quyidagi to'rtta bandning qaysi biri odatda PR'ni BLOKLAMAYDI, faqat nit: sifatida qoldiriladi?",
        "description_ru": "Какой из четырёх пунктов обычно НЕ блокирует PR и оставляется только как nit:?",
        "exercise_type": "multiple_choice",
        "options": ["To'g'rilik", "Xavfsizlik", "Testlar", "O'qilishi"],
        "options_ru": ["Правильность", "Безопасность", "Тесты", "Читаемость"],
        "correct_answers": "D",
        "is_multiple_select": False,
        "hint": "Diagrammadagi rangli bloklarni eslang - faqat bittasi sariq (nit) rangda edi.",
        "hint_ru": "Вспомните цветные блоки диаграммы - только один был жёлтым (nit).",
        "explanation": "O'qilishi muhim, lekin odatda bloklamaydigan, ixtiyoriy nit: izoh sifatida qoldiriladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Review bandlarini ustuvorlik tartibida joylang",
        "title_ru": "Расположите пункты ревью по приоритету",
        "description": "To'rt review bandini ustuvorlik tartibida (birinchi tekshiriladigandan oxirgigacha) joylashtiring.",
        "description_ru": "Расположите четыре пункта ревью по приоритету (от проверяемого первым до последнего).",
        "exercise_type": "drag_and_drop",
        "drag_items": ["To'g'rilik", "Xavfsizlik", "Testlar", "O'qilishi"],
        "drag_items_ru": ["Правильность", "Безопасность", "Тесты", "Читаемость"],
        "correct_order": ["To'g'rilik", "Xavfsizlik", "Testlar", "O'qilishi"],
        "hint": "Diagrammaning yuqoridan pastga oqimini eslang.",
        "hint_ru": "Вспомните направление диаграммы сверху вниз.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "CI va reviewer vazifasi",
        "title_ru": "CI и задача reviewer'а",
        "description": "test.yml testlar o'tgan-o'tmaganini avtomatik tekshiradi; reviewer esa testlar ___ ekanini tekshiradi.",
        "description_ru": "test.yml автоматически проверяет, прошли ли тесты; а reviewer проверяет, ___ ли тесты.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "yetarli",
        "correct_answers_ru": "достаточны",
        "hint": "Darsda aytilgan: \"test bor\" bilan \"test YETARLI\" bir xil emas.",
        "hint_ru": "В уроке сказано: \"тест есть\" не то же самое, что \"тест ДОСТАТОЧЕН\".",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 5 — R1: Takrorlash (mini-capstone) — review nima uchun, PR
# tavsifi, commit konventsiyasi, atomik commit, samarali review
# ---------------------------------------------------------------------------

L5_TEXT = """
<h3>Bu darsda yangi mavzu yo'q — sintez</h3>
<p>Bu — birinchi takrorlash darsi. 0-4-darslarda o'rgangan HAMMA narsani
BITTA real ssenariyoda birlashtiramiz: code review'ning maqsadi (0-dars),
yaxshi PR tavsifi (1-dars), commit konventsiyasi (2-dars), atomik
commit'lar (3-dars), va samarali review qilish (4-dars). Yangi tushuncha
yo'q — faqat mavjud bilimni bitta izchil ish jarayoniga yig'ish.</p>

<h3>Besh mavzuni bitta ssenariyoda ko'rish</h3>
<p>Quyidagi kod namunasida siz "talaba profilida ballarni noto'g'ri
ko'rsatish" degan xayoliy bug uchun TO'LIQ, boshidan oxirigacha bo'lgan
ish jarayonini ko'rasiz: avval nima uchun bu muammo umuman review talab
qilishini (0-dars), keyin uni ikkita atomik commit'ga qanday bo'lishni
(3-dars) va har biriga Conventional Commits formatida xabar yozishni
(2-dars), so'ng PR tavsifini to'rt bo'lim bilan yozishni (1-dars), va
nihoyat reviewer sifatida to'rt ustuvorlik bo'yicha uni qanday tekshirishni
(4-dars).</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Agar bitta commit ikkita mustaqil bug tuzatishini o'z ichiga olsa,
keyinchalik <code>git bisect</code> (112-kurs) bilan xato qidirishda
qanday muammo yuzaga keladi?</li>
<li>PR tavsifida "Qanday tekshirish mumkin" bo'limi bo'lmasa, reviewer
odatda birinchi navbatda nima qiladi?</li>
<li>Reviewer o'zgaruvchi nomi haqida izoh qoldirmoqchi, lekin kod
mantiqiy jihatdan to'g'ri va testlangan. Bu izoh PR'ni bloklashi
kerakmi?</li>
<li><code>fix(points)</code> va <code>chore(scripts)</code> commit
xabarlaridagi qamrov (scope) nima uchun foydali — <code>git log
--grep</code> nuqtai nazaridan?</li>
</ul>

<h3>Besh mavzuning bitta ish jarayonidagi joylashuvi</h3>
<pre class="mermaid">
flowchart TB
  P["Muammo aniqlandi
(0-dars: review nega kerak)"] --> AC["Ikkita atomik commit
git add -p bilan
(3-dars)"]
  AC --> CC["Har biriga Conventional
Commits xabari
(2-dars)"]
  CC --> PRD["PR ochiladi:
Kontekst+Nima+Nega+Test
(1-dars)"]
  PRD --> REV["Reviewer: to'g'rilik->
xavfsizlik->testlar->o'qilishi
(4-dars)"]
  REV --> M["Approved -> Merged"]
  style P fill:#d6e9ff,stroke:#2266aa
  style AC fill:#ffe9b3,stroke:#d09000
  style REV fill:#ffd6d6,stroke:#cc3333
  style M fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma 0-4-darslarning har biri BITTA real PR jarayonida qanday
qatlam bo'lib joylashishini ko'rsatadi — bu keyingi darslarda (fikr-
mulohaza berish/qabul qilish, merge strategiyasi, versiyalash)
davom etadigan asosiy "skelet".</p>

<h3>Nega bu dars qisqaroq</h3>
<p>Bu takrorlash darsi qasddan yangi tushunchalar bilan "shishirilmagan"
— uning vazifasi 0-4-darslarni BOG'LASH, yangi material qo'shish emas.
Kod namunasi to'liq bir ish jarayonini ko'rsatadi, lekin har bir qadami
allaqachon tanish. Keyingi, 6-darsdan boshlab yana yangi mavzular
(fikr-mulohaza berish va qabul qilish) davom etadi.</p>
""".strip()

L5_TEXT_RU = """
<h3>В этом уроке нет новой темы — синтез</h3>
<p>Это — первый урок повторения. Собираем ВСЁ изученное в уроках 0-4 в
ОДИН реальный сценарий: цель code review (урок 0), хорошее описание PR
(урок 1), конвенция коммитов (урок 2), атомарные коммиты (урок 3), и
эффективное ревью (урок 4). Новых понятий нет — только сборка
существующих знаний в один цельный рабочий процесс.</p>

<h3>Пять тем в одном сценарии</h3>
<p>В примере кода ниже вы увидите ПОЛНЫЙ, от начала до конца, рабочий
процесс для условного бага "неправильное отображение баллов в профиле
студента": сначала почему эта проблема вообще требует ревью (урок 0),
затем как разделить её на два атомарных коммита (урок 3) и написать
сообщение в формате Conventional Commits для каждого (урок 2), затем
написать описание PR с четырьмя разделами (урок 1), и, наконец, как
reviewer проверяет его по четырём приоритетам (урок 4).</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Если один коммит содержит два независимых исправления бага, какая
проблема возникнет позже при поиске ошибки через <code>git bisect</code>
(курс 112)?</li>
<li>Если в описании PR нет раздела "Как проверить", что обычно делает
reviewer в первую очередь?</li>
<li>Reviewer хочет оставить комментарий об имени переменной, но код
логически правильный и протестирован. Должен ли этот комментарий
блокировать PR?</li>
<li>Почему область (scope) в сообщениях коммитов <code>fix(points)</code>
и <code>chore(scripts)</code> полезна с точки зрения <code>git log
--grep</code>?</li>
</ul>

<h3>Расположение пяти тем в одном рабочем процессе</h3>
<pre class="mermaid">
flowchart TB
  P["Проблема обнаружена
(урок 0: зачем ревью)"] --> AC["Два атомарных коммита
через git add -p
(урок 3)"]
  AC --> CC["Сообщение Conventional
Commits для каждого
(урок 2)"]
  CC --> PRD["Открывается PR:
Контекст+Что+Почему+Тест
(урок 1)"]
  PRD --> REV["Reviewer: правильность->
безопасность->тесты->читаемость
(урок 4)"]
  REV --> M["Approved -> Merged"]
  style P fill:#d6e9ff,stroke:#2266aa
  style AC fill:#ffe9b3,stroke:#d09000
  style REV fill:#ffd6d6,stroke:#cc3333
  style M fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает, как каждый из уроков 0-4 располагается слоем
внутри ОДНОГО реального процесса PR — это базовый "скелет", на который
мы будем наращивать в следующих уроках (обратная связь, стратегия
merge, версионирование).</p>

<h3>Почему этот урок короче</h3>
<p>Этот урок повторения намеренно не "раздут" новыми понятиями — его
задача СВЯЗАТЬ уроки 0-4, а не добавить новый материал. Пример кода
показывает полный рабочий процесс, но каждый его шаг уже знаком. Начиная
со следующего, 6-го урока, снова пойдут новые темы (обратная связь).</p>
""".strip()

L5_CODE = """
# ============================================================
# Sintez: xayoliy "profilda ballar noto'g'ri ko'rsatilmoqda" bug'i
# uchun TO'LIQ ish jarayoni - 0-4-darslarning barchasi
# ============================================================

# --- 0-dars: muammo nega review talab qiladi ---
# CI (test.yml) mavjud testlarni tekshiradi, lekin "Rejected holatidagi
# loyihalar ball hisoblanishi kerakmi" degan yangi savolni CI o'zi
# o'ylab topmaydi - buni inson ko'rib chiqishi kerak.

# --- 3-dars: ikkita atomik commit (git add -p orqali ajratilgan) ---
# $ git add -p backend/app/api/v1/endpoints/students.py
# $ git commit -m "fix(students): filter project points by approved status"
#
# $ git add -p backend/app/services/exercise_service.py
# $ git commit -m "fix(scoring): guard multiple_choice grading against \\
#   comma-containing single-select answers"

# --- 2-dars: xabarlar Conventional Commits formatiga mos ---
COMMITS = [
    "fix(students): filter project points by approved status",
    "fix(scoring): guard multiple_choice grading against comma-containing single-select answers",
]
for msg in COMMITS:
    assert ": " in msg and msg.split("(")[0] in {"fix", "feat", "chore", "refactor"}
print("Ikkala commit ham Conventional Commits formatiga mos:", COMMITS)

# --- 1-dars: PR tavsifi to'rt bo'lim bilan ---
PR_DESCRIPTION = \"\"\"
## Kontekst
Talabalar profilida ko'rsatilgan ball haqiqiy hisoblangan balldan farq
qilishi haqida shikoyat tushdi.

## Nima o'zgardi
students.py'dagi profil statistikasi endi faqat Approved/Reviewed
holatidagi loyihalar ballarini hisoblaydi.

## Nega aynan shu yechim
Rejected loyihaning ball_earned qiymati hech qachon hamyonga
qo'shilmaydi - shu sababli ko'rsatilgan raqam ham shunga mos bo'lishi
kerak.

## Qanday tekshirish mumkin
pytest tests/test_students.py ishga tushiring - yangi test Rejected
loyiha ball hisobiga kirmasligini tasdiqlaydi.
\"\"\"

# --- 4-dars: reviewer to'rt ustuvorlik bo'yicha tekshiradi ---
REVIEW_RESULT = {
    "1_correctness": True,   # filtr to'g'ri holatlarni qamrab oladi
    "2_security": True,      # foydalanuvchi kiritishi ishtirok etmaydi
    "3_tests": True,         # yangi test qo'shilgan
    "4_readability": True,   # nomlar aniq
}
print("Review natijasi: Approved" if all(REVIEW_RESULT.values()) else "Changes requested")
""".strip()

L5_CODE_RU = """
# ============================================================
# Синтез: полный рабочий процесс для условного бага "неверное
# отображение баллов в профиле" - всё из уроков 0-4
# ============================================================

# --- Урок 0: почему проблема требует ревью ---
# CI (test.yml) проверяет существующие тесты, но новый вопрос "должны
# ли учитываться баллы проектов в статусе Rejected" CI сам не придумает
# - это должен рассмотреть человек.

# --- Урок 3: два атомарных коммита (разделены через git add -p) ---
# $ git add -p backend/app/api/v1/endpoints/students.py
# $ git commit -m "fix(students): filter project points by approved status"
#
# $ git add -p backend/app/services/exercise_service.py
# $ git commit -m "fix(scoring): guard multiple_choice grading against \\
#   comma-containing single-select answers"

# --- Урок 2: сообщения соответствуют формату Conventional Commits ---
COMMITS = [
    "fix(students): filter project points by approved status",
    "fix(scoring): guard multiple_choice grading against comma-containing single-select answers",
]
for msg in COMMITS:
    assert ": " in msg and msg.split("(")[0] in {"fix", "feat", "chore", "refactor"}
print("Оба коммита соответствуют формату Conventional Commits:", COMMITS)

# --- Урок 1: описание PR с четырьмя разделами ---
PR_DESCRIPTION = \"\"\"
## Контекст
Поступила жалоба, что балл, показанный в профиле студента, отличается
от фактически начисленного.

## Что изменилось
Статистика профиля в students.py теперь считает баллы только по
проектам в статусе Approved/Reviewed.

## Почему именно это решение
points_earned отклонённого (Rejected) проекта никогда не зачисляется в
кошелёк - поэтому показанное число должно соответствовать этому.

## Как проверить
Запустите pytest tests/test_students.py - новый тест подтверждает, что
Rejected проект не учитывается в подсчёте баллов.
\"\"\"

# --- Урок 4: reviewer проверяет по четырём приоритетам ---
REVIEW_RESULT = {
    "1_correctness": True,   # фильтр охватывает нужные статусы
    "2_security": True,      # пользовательский ввод не участвует
    "3_tests": True,         # новый тест добавлен
    "4_readability": True,   # имена понятны
}
print("Результат ревью: Approved" if all(REVIEW_RESULT.values()) else "Changes requested")
""".strip()

L5_TASK = {
    "task_title": "To'liq ish jarayonini o'zingizning o'zgarishingiz uchun qo'llang",
    "task_title_ru": "Примените полный рабочий процесс к своему изменению",
    "task_description": (
        "Shaxsiy repozitoriyangizda kichik, ikki qismli o'zgarish toping "
        "(yoki qasddan yarating) va 0-4-darslarning BARCHASINI qo'llang: "
        "(1) nega review kerakligini bir gapda yozing, (2) ikkita atomik "
        "commit qiling, (3) har biriga Conventional Commits xabari yozing, "
        "(4) to'rt bo'limli PR tavsifi yozing, (5) o'zingizni reviewer "
        "o'rniga qo'yib, to'rt ustuvorlik bo'yicha o'z PR'ingizni baholang."
    ),
    "task_description_ru": (
        "В своём репозитории найдите (или намеренно создайте) небольшое "
        "изменение из двух частей и примените ВСЁ из уроков 0-4: (1) одним "
        "предложением напишите, зачем нужно ревью, (2) сделайте два "
        "атомарных коммита, (3) напишите для каждого сообщение Conventional "
        "Commits, (4) напишите описание PR из четырёх разделов, (5) поставив "
        "себя на место reviewer'а, оцените свой PR по четырём приоритетам."
    ),
    "task_requirements": (
        "1) Ikkala commit hash'i va xabari ilova qilinishi kerak. 2) PR "
        "tavsifi to'rt bo'lim bilan to'liq yozilgan bo'lishi shart. 3) "
        "O'z-o'zini baholash to'rtta ustuvorlikning har biri bo'yicha "
        "alohida jumla bilan yozilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Приложить хеши и сообщения обоих коммитов. 2) Описание PR "
        "должно быть полностью написано с четырьмя разделами. 3) "
        "Самооценка должна быть написана отдельным предложением по каждому "
        "из четырёх приоритетов."
    ),
    "task_technologies": "Git, GitHub (Pull Requests)",
    "task_deadline_days": 4,
}

L5_SAMPLE = {
    "title": "Namuna: 0-4-darslarning barchasini birlashtirgan to'liq ish jarayoni",
    "description": (
        "Ushbu darsning kod namunasi asosida, xayoliy \"profilda ballar "
        "noto'g'ri\" bug'i uchun review-dan-nega-kerakligidan tortib "
        "reviewer baholashigacha bo'lgan to'liq, izohli ish jarayoni."
    ),
    "sample_type": "code",
    "code_files": [
        {"filename": "full_workflow_demo.py", "language": "python", "code": "# Qarang: L5_CODE ushbu darsning to'liq matnida"},
    ],
}

L5_EXERCISES = [
    {
        "title": "Bo'lingan commit va bisect",
        "title_ru": "Разделённый коммит и bisect",
        "description": (
            "Agar ikkita mustaqil tuzatish BITTA commit'da bo'lsa, keyinchalik "
            "git bisect (112-kurs) bilan qanday muammo yuzaga keladi?"
        ),
        "description_ru": (
            "Если два независимых исправления окажутся в ОДНОМ коммите, какая "
            "проблема возникнет позже при использовании git bisect (курс 112)?"
        ),
        "exercise_type": "multiple_choice",
        "options": [
            "bisect umuman ishlamay qoladi",
            "bisect commit'ni topadi, lekin QAYSI o'zgarish xatoga sabab bo'lganini bilib bo'lmaydi",
            "bisect ikkala o'zgarishni alohida-alohida ko'rsatadi",
            "Hech qanday muammo bo'lmaydi",
        ],
        "options_ru": [
            "bisect вообще перестаёт работать",
            "bisect находит коммит, но невозможно узнать, КАКОЕ изменение вызвало ошибку",
            "bisect показывает оба изменения отдельно",
            "Никакой проблемы не возникнет",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "3-darsdagi diagrammani eslang - bisect faqat commit darajasida ishlaydi.",
        "hint_ru": "Вспомните диаграмму урока 3 - bisect работает только на уровне коммита.",
        "explanation": "bisect faqat \"qaysi COMMIT yomon\" deb topadi - ichidagi qaysi o'zgarish sabab ekanini bilib bo'lmaydi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "To'liq ish jarayonini tartiblang",
        "title_ru": "Расположите полный рабочий процесс по порядку",
        "description": "0-4-darslarning bir PR ichidagi to'g'ri ketma-ketligini joylashtiring.",
        "description_ru": "Расположите правильную последовательность уроков 0-4 внутри одного PR.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Muammoni aniqlash (nega review kerak)",
            "Atomik commit'lar qilish",
            "PR tavsifini yozish",
            "Reviewer to'rt ustuvorlik bo'yicha tekshiradi",
        ],
        "drag_items_ru": [
            "Обнаружение проблемы (зачем ревью)",
            "Сделать атомарные коммиты",
            "Написать описание PR",
            "Reviewer проверяет по четырём приоритетам",
        ],
        "correct_order": [
            "Muammoni aniqlash (nega review kerak)",
            "Atomik commit'lar qilish",
            "PR tavsifini yozish",
            "Reviewer to'rt ustuvorlik bo'yicha tekshiradi",
        ],
        "hint": "Diagrammadagi flowchart'ni yuqoridan pastga o'qing.",
        "hint_ru": "Прочитайте flowchart диаграммы сверху вниз.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Qamrov (scope) foydasi",
        "title_ru": "Польза области (scope)",
        "description": "git log --grep=\"(points)\" buyrug'i faqat commit xabarida ___ to'g'ri ko'rsatilgan bo'lsagina ishonchli ishlaydi.",
        "description_ru": "Команда git log --grep=\"(points)\" работает надёжно, только если в сообщении коммита правильно указана ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "qamrov",
        "correct_answers_ru": "область",
        "hint": "2-darsda Conventional Commits'ning qavs ichidagi qismi.",
        "hint_ru": "Часть Conventional Commits в скобках из урока 2.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 6 — Amaliy va samimiy fikr-mulohaza berish
# ---------------------------------------------------------------------------

L6_TEXT = """
<h3>Nima uchun "bu noto'g'ri" yetarli emas</h3>
<p>4-darsda reviewer NIMAGA e'tibor berishi kerakligini o'rgandik.
Bu darsda — topilgan muammoni QANDAY yozib bildirish haqida. Ikkita
reviewer bir xil xatoni topishi mumkin, lekin biri "bu noto'g'ri" deb
yozadi, ikkinchisi esa "bu funksiya <code>student_answer</code>
bo'sh string bo'lsa <code>IndexError</code> beradi, chunki 43-qatorda
<code>[0]</code> indeksga to'g'ridan-to'g'ri murojaat qilinmoqda —
oldin uzunlikni tekshirish kerak" deb yozadi. Ikkalasi ham "muammo
bor" deydi, lekin faqat ikkinchisi muallifga NIMA qilish kerakligini
ko'rsatadi.</p>

<h3>Aniq (actionable) izohning uch qismi</h3>
<ul>
<li><strong>NIMA muammo</strong> — aniq qator/funksiya/holat
ko'rsatilgan bo'lishi kerak, "bu yerda muammo bor" emas.</li>
<li><strong>NEGA muammo</strong> — qaysi holatda bu xato ishga
tushishini tushuntirish (masalan "agar X bo'lsa, Y sodir bo'ladi").</li>
<li><strong>NIMA qilish kerak (ixtiyoriy, lekin foydali)</strong> —
aniq taklif yoki yo'nalish, ayniqsa GitHub'ning "suggestion" bloki
orqali to'g'ridan-to'g'ri kod taklif qilish mumkin.</li>
</ul>

<h3>Vague (noaniq) izohlar — nima uchun zararli</h3>
<p>"Bu yomon", "menga yoqmadi", "buni qayta yozing" kabi izohlar
muallifga IKKI marta ish qildiradi: avval "nima yomon ekanini" taxmin
qilish, keyin tuzatish. Bundan tashqari, bunday izohlar SHAXSGA
qarshi qaratilgandek tuyulishi mumkin ("sen yomon yozibsan" degandek),
holbuki maqsad KOD haqida, MUALLIF haqida emas. Bu — 0-darsda aytilgan
"gatekeeping" hissi paydo bo'lishining asosiy sababi: aniq bo'lmagan
izoh haqiqatan ham hukm kabi tuyuladi.</p>

<h3>"nit:" prefiksi — bloklamaydigan izohni ajratish</h3>
<p>4-darsda aytilganidek, o'qilish/uslub bo'yicha izohlar odatda PR'ni
bloklamasligi kerak. Buni yozma ravishda ko'rsatish uchun ko'p jamoalar
<code>nit:</code> (nitpick — mayda-chuyda) prefiksidan foydalanadi:
"nit: bu o'zgaruvchini <code>result</code> emas <code>filtered_result</code>
deb nomlash o'qilishni yaxshilaydi" — bu "MEN buni tavsiya qilaman,
lekin bu APPROVE'ni to'xtatmaydi" degan aniq signal.</p>

<h3>Yaxshi narsani ham ayting</h3>
<p>Review faqat muammo topish emas — agar kimdir aqlli yechim yozgan
bo'lsa (masalan chekka holatni chiroyli boshqargan), buni aytish
foydali: bu ijobiy naqshni MUSTAHKAMLAYDI va review'ni faqat tanqid
maydoniga aylanishidan saqlaydi. Masalan: "Bu yerda <code>is_multiple_select</code>
tekshiruvi chiroyli — chekka holatni to'g'ri ajratdi."</p>

<h3>Vague va actionable izohning oqibati</h3>
<pre class="mermaid">
flowchart LR
  V["Vague izoh:
'bu noto'g'ri'"] --> V1["Muallif taxmin qiladi"]
  V1 --> V2["Noto'g'ri taxmin qilsa:
yana bir 'changes requested'"]
  A["Actionable izoh:
qator+sabab+taklif"] --> A1["Muallif darhol tuzatadi"]
  A1 --> A2["Bir marta 'changes requested'
bilan yakunlanadi"]
  style V2 fill:#ffd6d6,stroke:#cc3333
  style A2 fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma shuni ko'rsatadiki, vague izoh ko'pincha 0-darsdagi
"Changes requested" tsiklini KO'PROQ marta aylantiradi — muallif
noto'g'ri taxmin qilib, yana tekshirtirishga majbur bo'ladi. Actionable
izoh esa odatda bitta tsiklda hal bo'ladi.</p>

<h3>Bu 117-kurs bilan qanday bog'liq</h3>
<p>117-kursdagi <code>test.yml</code> xato bersa, CI logida ANIQ qator
va xato xabari ko'rsatiladi ("bu qator, bu sabab"). Inson izohi ham
xuddi shunday aniq bo'lishi kerak — CI'ning o'zi bergan aniqlik darajasi
inson fikr-mulohazasi uchun ham standart bo'lishi kerak.</p>

<h3>GitHub'ning o'zida buni yozish mexanizmi</h3>
<p>GitHub PR'da ikki xil izoh mavjud: <strong>umumiy izoh</strong>
("Conversation" bo'limida, butun PR haqida) va <strong>qatorga
bog'langan izoh</strong> (aynan bitta faylning aynan bitta qatoriga
"biriktirilgan"). Actionable izoh deyarli har doim QATORGA bog'langan
bo'lishi kerak — "bu funksiya yomon" degan umumiy izoh muallifni QAYSI
funksiyani qidirishga majbur qiladi, qatorga bog'langan izoh esa buni
darhol ko'rsatadi. Bundan tashqari, GitHub'ning "Add a suggestion"
tugmasi orqali reviewer to'g'ridan-to'g'ri KOD TAKLIFINI yozishi mumkin
— muallif buni bitta bosishda ("Commit suggestion") qabul qilishi mumkin,
bu esa 3-darsdagi atomiklikni buzmasdan tezkor tuzatish imkonini
beradi.</p>

<h3>"Request changes" va "Comment" — ikki xil review turi</h3>
<p>GitHub'da review yakunlanganda uchta variant bor: <strong>Comment</strong>
(izoh qoldirish, hech narsani bloklamaydi), <strong>Approve</strong>
(tasdiqlash), va <strong>Request changes</strong> (o'zgarish talab
qilish — bu holat PR'ni RASMAN blokka oladi, 0-darsdagi "Changes
requested" holatiga mos keladi). Muhim farq: agar reviewer faqat
<code>nit:</code> izohlari qoldirsa, u "Comment" yoki "Approve" tanlashi
kerak — "Request changes"ni faqat 4-darsdagi UCHTA bloklovchi ustuvorlik
(to'g'rilik, xavfsizlik, testlar) bo'yicha haqiqiy muammo bo'lganda
ishlatish kerak.</p>
""".strip()

L6_TEXT_RU = """
<h3>Почему "это неправильно" недостаточно</h3>
<p>В уроке 4 мы изучили, на что reviewer'у обращать внимание. В этом
уроке — КАК записать найденную проблему. Два reviewer'а могут найти одну
и ту же ошибку, но один напишет "это неправильно", а другой — "эта
функция выдаст <code>IndexError</code>, если <code>student_answer</code>
— пустая строка, потому что в строке 43 напрямую обращаются к индексу
<code>[0]</code> — сначала нужно проверить длину". Оба говорят "проблема
есть", но только второй показывает автору, ЧТО нужно сделать.</p>

<h3>Три части actionable (действенного) комментария</h3>
<ul>
<li><strong>В ЧЁМ проблема</strong> — должна быть указана конкретная
строка/функция/случай, а не "здесь проблема".</li>
<li><strong>ПОЧЕМУ это проблема</strong> — объяснение, в каком случае
эта ошибка сработает (например "если X, то произойдёт Y").</li>
<li><strong>ЧТО делать (необязательно, но полезно)</strong> — конкретное
предложение или направление, особенно можно предложить код напрямую
через блок "suggestion" GitHub.</li>
</ul>

<h3>Vague (расплывчатые) комментарии — почему они вредны</h3>
<p>Комментарии вроде "это плохо", "мне не нравится", "перепишите это"
заставляют автора работать ДВАЖДЫ: сначала догадаться, "что плохо",
затем исправить. Кроме того, такие комментарии могут восприниматься как
направленные ПРОТИВ человека ("ты плохо написал"), хотя цель — КОД, а не
АВТОР. Это — основная причина возникновения ощущения "gatekeeping" из
урока 0: расплывчатый комментарий действительно ощущается как приговор.</p>

<h3>Префикс "nit:" — выделение неблокирующего комментария</h3>
<p>Как говорилось в уроке 4, комментарии о читаемости/стиле обычно не
должны блокировать PR. Чтобы показать это письменно, многие команды
используют префикс <code>nit:</code> (nitpick — мелочь): "nit: назвать
эту переменную <code>filtered_result</code>, а не <code>result</code>,
улучшило бы читаемость" — это чёткий сигнал "Я это рекомендую, но это
НЕ останавливает APPROVE".</p>

<h3>Говорите и о хорошем</h3>
<p>Ревью — это не только поиск проблем: если кто-то написал умное
решение (например, красиво обработал граничный случай), полезно об
этом сказать: это ЗАКРЕПЛЯЕТ положительный паттерн и не даёт ревью
превратиться только в поле для критики. Например: "Здесь проверка
<code>is_multiple_select</code> красивая — правильно разделила
граничный случай."</p>

<h3>Последствие vague и actionable комментария</h3>
<pre class="mermaid">
flowchart LR
  V["Vague комментарий:
'это неправильно'"] --> V1["Автор догадывается"]
  V1 --> V2["Если догадка неверна:
ещё одно 'changes requested'"]
  A["Actionable комментарий:
строка+причина+предложение"] --> A1["Автор сразу исправляет"]
  A1 --> A2["Завершается за один цикл
'changes requested'"]
  style V2 fill:#ffd6d6,stroke:#cc3333
  style A2 fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает, что vague комментарий часто ЗАПУСКАЕТ цикл
"Changes requested" из урока 0 БОЛЬШЕЕ число раз — автор неверно
догадывается и снова просит проверить. Actionable комментарий обычно
решается за один цикл.</p>

<h3>Как это связано с курсом 117</h3>
<p>Если <code>test.yml</code> из курса 117 выдаёт ошибку, в логе CI
показывается ТОЧНАЯ строка и сообщение об ошибке ("эта строка, эта
причина"). Комментарий человека должен быть таким же точным — уровень
точности, который даёт сам CI, должен стать стандартом и для обратной
связи человека.</p>

<h3>Механизм записи этого на самом GitHub</h3>
<p>В PR на GitHub есть два вида комментариев: <strong>общий
комментарий</strong> (в разделе "Conversation", о всём PR) и
<strong>комментарий, привязанный к строке</strong> (буквально
"прикреплённый" к одной строке одного файла). Actionable комментарий
почти всегда должен быть привязан к СТРОКЕ — общий комментарий "эта
функция плохая" заставляет автора искать, КАКУЮ функцию имели в виду, а
комментарий, привязанный к строке, показывает это сразу. Кроме того,
через кнопку "Add a suggestion" reviewer может написать предложение КОДА
напрямую — автор может принять его одним нажатием ("Commit suggestion"),
что даёт быстрое исправление, не нарушая атомарность из урока 3.</p>

<h3>"Request changes" и "Comment" — два типа ревью</h3>
<p>При завершении ревью на GitHub есть три варианта: <strong>Comment</strong>
(оставить комментарий, ничего не блокирует), <strong>Approve</strong>
(одобрить), и <strong>Request changes</strong> (запросить изменения —
это состояние ОФИЦИАЛЬНО блокирует PR, соответствует состоянию "Changes
requested" из урока 0). Важное различие: если reviewer оставляет только
комментарии <code>nit:</code>, он должен выбрать "Comment" или
"Approve" — "Request changes" следует использовать только при реальной
проблеме по ТРЁМ блокирующим приоритетам из урока 4 (правильность,
безопасность, тесты).</p>
""".strip()

L6_CODE = """
# ============================================================
# Vague vs actionable izoh - bir xil xato uchun ikki xil yozuv
# ============================================================

CODE_UNDER_REVIEW = \"\"\"
def get_first_answer(student_answer):
    return student_answer.split(",")[0]
\"\"\"

# --- VAGUE (noaniq) izoh ---
VAGUE_COMMENT = "Bu funksiya yaxshi emas."

# --- ACTIONABLE (aniq) izoh: NIMA + NEGA + NIMA QILISH ---
ACTIONABLE_COMMENT = \"\"\"
get_first_answer bo'sh string (student_answer = "") kelsa
IndexError beradi, chunki split(",") natijasi [""] bo'ladi, lekin
[0] baribir ishlaydi - aslida muammo student_answer=None kelganda:
None.split() AttributeError beradi.

Taklif:
    def get_first_answer(student_answer):
        if not student_answer:
            return ""
        return student_answer.split(",")[0]
\"\"\"

# --- nit: prefiksi bilan bloklamaydigan izoh ---
NIT_COMMENT = "nit: `get_first_answer` o'rniga `get_first_selected_option` " \\
              "nomi maqsadni aniqroq ifodalaydi (bloklamaydi, ixtiyoriy)."

# --- Ijobiy izoh (mustahkamlash) ---
POSITIVE_COMMENT = "Bu yerda `is_multiple_select` tekshiruvi chiroyli - " \\
                    "chekka holatni aniq ajratgan."

print("=== Vague ===")
print(VAGUE_COMMENT)
print("\\n=== Actionable ===")
print(ACTIONABLE_COMMENT)
print("\\n=== Nit (bloklamaydi) ===")
print(NIT_COMMENT)
print("\\n=== Ijobiy ===")
print(POSITIVE_COMMENT)


# ============================================================
# Izohni avtomatik "sifat darajasi"ga baholovchi sodda tekshiruv -
# uch mezon: aniq qator/holat, sabab, va ohang
# ============================================================
import re


def score_comment_quality(comment: str) -> dict:
    \"\"\"Juda sodda evristika - real jamoada bu inson qarori, lekin
    asosiy signal turlarini ko'rsatish uchun foydali.\"\"\"
    has_specific_reference = bool(re.search(r"\\d+-qator|`\\w+`", comment))
    has_reasoning = any(word in comment.lower() for word in ["chunki", "sabab", "agar"])
    is_harsh = any(word in comment.lower() for word in ["yomon", "yoqmadi"])
    return {
        "aniq_qatorga_ishora": has_specific_reference,
        "sabab_tushuntirilgan": has_reasoning,
        "keskin_ohang": is_harsh,
        "actionable_hisoblanadimi": has_specific_reference and has_reasoning and not is_harsh,
    }


for label, comment in [("Vague", VAGUE_COMMENT), ("Actionable", ACTIONABLE_COMMENT)]:
    print(f"\\n{label}: {score_comment_quality(comment)}")
""".strip()

L6_CODE_RU = """
# ============================================================
# Vague vs actionable комментарий - две записи для одной ошибки
# ============================================================

CODE_UNDER_REVIEW = \"\"\"
def get_first_answer(student_answer):
    return student_answer.split(",")[0]
\"\"\"

# --- VAGUE (расплывчатый) комментарий ---
VAGUE_COMMENT = "Эта функция плохая."

# --- ACTIONABLE (действенный) комментарий: ЧТО + ПОЧЕМУ + ЧТО ДЕЛАТЬ ---
ACTIONABLE_COMMENT = \"\"\"
get_first_answer выдаст IndexError, если придёт пустая строка
(student_answer = ""), потому что результат split(",") будет [""], но
[0] всё равно сработает - на самом деле проблема, если придёт
student_answer=None: None.split() выдаст AttributeError.

Предложение:
    def get_first_answer(student_answer):
        if not student_answer:
            return ""
        return student_answer.split(",")[0]
\"\"\"

# --- Неблокирующий комментарий с префиксом nit: ---
NIT_COMMENT = "nit: имя `get_first_selected_option` вместо " \\
              "`get_first_answer` точнее выражает назначение (не блокирует, необязательно)."

# --- Позитивный комментарий (закрепление) ---
POSITIVE_COMMENT = "Здесь проверка `is_multiple_select` красивая - " \\
                    "чётко выделила граничный случай."

print("=== Vague ===")
print(VAGUE_COMMENT)
print("\\n=== Actionable ===")
print(ACTIONABLE_COMMENT)
print("\\n=== Nit (не блокирует) ===")
print(NIT_COMMENT)
print("\\n=== Позитивный ===")
print(POSITIVE_COMMENT)


# ============================================================
# Простая проверка, автоматически оценивающая "уровень качества"
# комментария - три критерия: точная ссылка, причина, тон
# ============================================================
import re


def score_comment_quality(comment: str) -> dict:
    \"\"\"Очень простая эвристика - в реальной команде это решение
    человека, но полезно для демонстрации основных типов сигналов.\"\"\"
    has_specific_reference = bool(re.search(r"строке? \\d+|`\\w+`", comment))
    has_reasoning = any(word in comment.lower() for word in ["потому что", "причина", "если"])
    is_harsh = any(word in comment.lower() for word in ["плохая", "не нравится"])
    return {
        "точная_ссылка": has_specific_reference,
        "причина_объяснена": has_reasoning,
        "резкий_тон": is_harsh,
        "считается_actionable": has_specific_reference and has_reasoning and not is_harsh,
    }


for label, comment in [("Vague", VAGUE_COMMENT), ("Actionable", ACTIONABLE_COMMENT)]:
    print(f"\\n{label}: {score_comment_quality(comment)}")
""".strip()

L6_TASK = {
    "task_title": "Vague izohni actionable izohga qayta yozing",
    "task_title_ru": "Перепишите vague комментарий в actionable",
    "task_description": (
        "Berilgan uchta vague izohni ('bu chalkash', 'buni qayta yozing', "
        "'menga yoqmadi') aniq kod parchasi uchun actionable izohga qayta "
        "yozing: har birida NIMA muammo, NEGA muammo, va NIMA qilish kerak "
        "bo'lishi kerak. Bittasini nit: prefiksi bilan (bloklamaydigan) "
        "yozing."
    ),
    "task_description_ru": (
        "Перепишите три данных vague комментария ('это запутанно', "
        "'перепишите это', 'мне не нравится') в actionable комментарии для "
        "конкретного фрагмента кода: в каждом должно быть ЧТО не так, "
        "ПОЧЕМУ не так, и ЧТО делать. Один напишите с префиксом nit: "
        "(неблокирующий)."
    ),
    "task_requirements": (
        "1) Uchta izohning har biri kamida 2-3 gapdan iborat bo'lishi "
        "kerak. 2) Har birida aniq kod qatoriga yoki funksiyaga ishora "
        "bo'lishi shart. 3) Kamida bittasida GitHub'ning \"suggestion\" "
        "formatidagi kod taklifi bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Каждый из трёх комментариев должен состоять минимум из 2-3 "
        "предложений. 2) В каждом должна быть ссылка на конкретную строку "
        "или функцию кода. 3) Минимум в одном должно быть предложение кода "
        "в формате \"suggestion\" GitHub."
    ),
    "task_technologies": "GitHub (Pull Request Review), yozma fikr-mulohaza",
    "task_deadline_days": 3,
}

L6_SAMPLE = {
    "title": "Namuna: vague, actionable, nit va ijobiy izohlar to'plami",
    "description": (
        "Ushbu darsning kod namunasi asosida, bitta kod parchasiga "
        "yozilgan to'rt xil izoh turi (vague, actionable, nit, ijobiy) "
        "to'liq matn sifatida."
    ),
    "sample_type": "code",
    "code_files": [
        {"filename": "review_comments_demo.py", "language": "python", "code": "# Qarang: L6_CODE ushbu darsning to'liq matnida"},
    ],
}

L6_EXERCISES = [
    {
        "title": "Actionable izohning uch qismi",
        "title_ru": "Три части actionable комментария",
        "description": "Aniq (actionable) izohda BO'LISHI shart bo'lgan ikkita element qaysi?",
        "description_ru": "Какие два элемента ОБЯЗАТЕЛЬНО должны быть в actionable комментарии?",
        "exercise_type": "multiple_choice",
        "options": [
            "Muallifning ismi va vaqti",
            "NIMA muammo va NEGA muammo ekanligi",
            "Faqat \"bu yomon\" degan baho",
            "Kodning umumiy qatorlar soni",
        ],
        "options_ru": [
            "Имя автора и время",
            "В ЧЁМ проблема и ПОЧЕМУ это проблема",
            "Только оценка \"это плохо\"",
            "Общее количество строк кода",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsdagi uchta qismni eslang: NIMA, NEGA, (ixtiyoriy) NIMA QILISH.",
        "hint_ru": "Вспомните три части из урока: ЧТО, ПОЧЕМУ, (необязательно) ЧТО ДЕЛАТЬ.",
        "explanation": "Actionable izoh kamida NIMA muammo va NEGA ekanini ko'rsatishi kerak - \"NIMA QILISH\" ixtiyoriy, lekin foydali.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "nit: prefiksining vazifasi",
        "title_ru": "Назначение префикса nit:",
        "description": "\"nit:\" prefiksi bilan boshlangan izoh nimani anglatadi?",
        "description_ru": "Что означает комментарий, начинающийся с префикса \"nit:\"?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bu - PR'ni albatta bloklaydigan jiddiy muammo",
            "Bu - xavfsizlik bo'yicha kritik izoh",
            "Bu - ixtiyoriy tavsiya, PR'ni bloklamaydi",
            "Bu - reviewer PR'ni rad etganini bildiradi",
        ],
        "options_ru": [
            "Это серьёзная проблема, обязательно блокирующая PR",
            "Это критический комментарий по безопасности",
            "Это необязательная рекомендация, не блокирующая PR",
            "Это означает, что reviewer отклонил PR",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "\"Nitpick\" so'zining ma'nosini eslang - mayda-chuyda.",
        "hint_ru": "Вспомните значение слова \"nitpick\" - мелочь.",
        "explanation": "nit: - ixtiyoriy, bloklamaydigan tavsiya ekanini aniq bildiradigan konventsional prefiks.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Izohlarni noaniqlikdan aniqlikka tartiblang",
        "title_ru": "Расположите комментарии от расплывчатого к точному",
        "description": "Quyidagi to'rtta izohni ENG NOANIQdan ENG ANIQqa tartiblang.",
        "description_ru": "Расположите четыре комментария от САМОГО РАСПЛЫВЧАТОГО к САМОМУ ТОЧНОМУ.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Bu yomon.",
            "Bu funksiya yaxshi emas, boshqacha yozing.",
            "Bu funksiya None kelsa xato beradi.",
            "42-qatorda student_answer=None bo'lsa AttributeError chiqadi - avval bo'sh tekshiruv qo'shing.",
        ],
        "drag_items_ru": [
            "Это плохо.",
            "Эта функция нехорошая, напишите иначе.",
            "Эта функция выдаёт ошибку, если приходит None.",
            "В строке 42, если student_answer=None, будет AttributeError - сначала добавьте проверку на пустоту.",
        ],
        "correct_order": [
            "Bu yomon.",
            "Bu funksiya yaxshi emas, boshqacha yozing.",
            "Bu funksiya None kelsa xato beradi.",
            "42-qatorda student_answer=None bo'lsa AttributeError chiqadi - avval bo'sh tekshiruv qo'shing.",
        ],
        "hint": "Har bir keyingi izohda qator raqami, aniq xato turi va yechim qo'shilib boradi.",
        "hint_ru": "В каждом следующем комментарии добавляется номер строки, тип ошибки и решение.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 7 — Fikr-mulohazani ego'siz qabul qilish va javob berish
# ---------------------------------------------------------------------------

L7_TEXT = """
<h3>Fikr-mulohaza SIZGA emas, KODGA qaratilgan</h3>
<p>6-darsda yaxshi izoh qanday yozilishini ko'rdik. Endi tanga teskari
tomondan qaraymiz: SIZ muallif bo'lganingizda, boshqa birov sizning
kodingizga izoh qoldirsa, buni qanday qabul qilish kerak? Eng katta
xato — izohni SHAXSIY hujum sifatida qabul qilish ("meni yomon dasturchi
deb o'ylayapti"). Hatto eng aniq va samimiy yozilgan izoh ham (6-dars)
agar muallif uni himoya sifatida qabul qilsa, foydasiz bo'lib qoladi.
Yodda tuting: reviewer KOD haqida gapiryapti, SIZNING qadr-qimmatingiz
haqida emas.</p>

<h3>To'g'ri javob berish qadamlari</h3>
<ul>
<li><strong>Avval tushunishga harakat qiling.</strong> Agar izoh
tushunarsiz bo'lsa, darhol himoyalanmang — aniqlashtiruvchi savol
bering: "Sen shu holatni nazarda tutyapsanmi: agar X bo'lsa?" Bu
himoyalanish emas, aniqlik izlash.</li>
<li><strong>Rozi bo'lsangiz — TUZATING, faqat "OK" demang.</strong> Kod
o'zgarganda buni ko'rsating (masalan yangi commit qo'shib, "Tuzatildi:
abc123" deb javob yozing) — reviewer o'zgarish haqiqatan sodir bo'lganini
ko'rishi kerak.</li>
<li><strong>Rozi bo'lmasangiz — HURMAT bilan, DALIL bilan qarshi
chiqing.</strong> "Yo'q, bu noto'g'ri" emas, balki "Men bu yerda X
sababli boshqacha yondashuvni tanladim, chunki Y — lekin agar Z holatni
nazarda tutayotgan bo'lsang, unda haq bo'lasan, ko'rib chiqaman."
Fikr-mulohazani rad etish — normal, agar u DALIL bilan qilinsa.</li>
<li><strong>Har bir izohni "Resolved" deb belgilang faqat haqiqatan hal
bo'lgandan keyin.</strong> Suhbatni yopish ("resolve") kod o'zgarmasdan
turib qilinsa, reviewer keyingi safar sizning "Resolved" belgingizga
ishonmay qoladi.</li>
</ul>

<h3>Qayta so'rash (re-request review) — oxirgi qadam</h3>
<p>Barcha izohlarga javob berilgandan so'ng, PR yana <code>Review
so'ralgan</code> holatiga qaytariladi (0-darsdagi diagrammani eslang) —
GitHub'da bu "Re-request review" tugmasi orqali qilinadi. Buni
UNUTMASLIK kerak: agar siz shunchaki kod o'zgartirib, reviewer'ga
xabar bermasangiz, u PR'ning tayyor ekanini bilmasligi mumkin.</p>

<h3>Nima uchun bahslashish yaxshi, agar u dalilga asoslansa</h3>
<p>"Ego'siz" qabul qilish — hamma narsaga "xo'p" deyish degani emas.
Agar reviewer noto'g'ri taxmin qilsa (masalan sizning yondashuvingiz
allaqachon shu holatni to'g'ri boshqarayotganini bilmasa), buni ANIQ
tushuntirish — bu sog'lom muhokama, ego emas. Farq — HISSIYOTGA emas,
DALILGA asoslanishda: "chunki men SHUNDAY his qilaman" emas, "chunki
42-qatordagi tekshiruv aynan shu holatni allaqachon qamrab oladi"
sifatida.</p>

<h3>Bitta izoh mavzusining hayot yo'li</h3>
<pre class="mermaid">
sequenceDiagram
    participant R as Reviewer
    participant M as Muallif
    R->>M: Izoh qoldiradi (6-dars: aniq, actionable)
    M->>M: Tushunishga harakat qiladi
    alt Tushunarsiz
        M->>R: Aniqlashtiruvchi savol beradi
        R->>M: Javob beradi
    end
    alt Rozi
        M->>M: Kodni tuzatadi, yangi commit
        M->>R: "Tuzatildi: abc123" deb javob yozadi
    else Rozi emas, dalil bor
        M->>R: Hurmat bilan, dalil bilan tushuntiradi
        R->>M: Ko'rib chiqadi, rozi bo'ladi yoki yo'q
    end
    M->>R: Re-request review
</pre>
<p>Diagramma bitta izoh atrofidagi to'liq suhbatni ko'rsatadi — bu
0-darsdagi katta PR holatlar diagrammasining "Changes requested"
qutisi ICHIDA aslida nima sodir bo'lishini kattalashtirib ko'rsatadi.</p>

<h3>Bir necha tsikl bo'lishi normal — charchash emas, jarayon</h3>
<p>Ba'zan bitta PR 3-4 marta "changes requested" -> tuzatish -> qayta
so'rash tsiklidan o'tadi. Bu ayniqsa katta yoki murakkab o'zgarishlarda
kutilgan holat, MUVAFFAQIYATSIZLIK emas. Agar siz ko'p tsikldan charchab,
"xo'p, hammasiga rozi" deb qolsangiz — bu ham ego muammosi, teskari
tomondan: endi siz o'z fikringizni dalilsiz taslim qilyapsiz. To'g'ri
yondashuv — har bir tsiklda xuddi birinchisidek diqqat bilan javob
berish, safar soni ko'p bo'lgani uchun emas.</p>

<h3>"Resolve conversation" tugmasi — kim bosishi kerak</h3>
<p>GitHub'da har bir izoh mavzusini "Resolve conversation" tugmasi
yopadi. Ko'p jamoada konventsiya shunday: buni REVIEWER bosadi, muallif
emas — chunki aynan reviewer o'z izohi HAQIQATAN hal qilinganini
tasdiqlaydi. Agar muallif o'zi yopsa (7-darsning boshida aytilgan
"resolve without fixing" xatosining yumshoq shakli), reviewer keyingi
safar bu belgiga ishonmay, HAR BIR "Resolved" mavzuni qayta o'qishga
majbur bo'ladi — bu esa butun jarayonni SEKINLASHTIRADI.</p>

<h3>Bu 4 va 6-darslar bilan qanday bog'liq</h3>
<p>4-darsda reviewer nimaga e'tibor berishini, 6-darsda buni QANDAY
yozishni ko'rdik. Bu dars — xuddi shu jarayonning IKKINCHI yarmi:
muallif tomonidan. Ikkala tomon ham bir xil maqsadga xizmat qiladi —
0-darsda aytilgan uchta sabab (xato ushlash, bilim almashish, standart
saqlash) — va bu faqat REVIEWER emas, MUALLIFNING ham javobgarligi
ekanini ko'rsatadi.</p>
""".strip()

L7_TEXT_RU = """
<h3>Обратная связь направлена на КОД, а не на ВАС</h3>
<p>В уроке 6 мы увидели, как пишется хороший комментарий. Теперь
посмотрим с другой стороны: когда ВЫ — автор, и кто-то оставляет
комментарий к вашему коду, как это правильно принять? Самая большая
ошибка — воспринять комментарий как ЛИЧНОЕ нападение ("он думает, что я
плохой разработчик"). Даже самый точный и доброжелательно написанный
комментарий (урок 6) становится бесполезным, если автор воспринимает его
как защиту. Помните: reviewer говорит о КОДЕ, а не о ВАШЕЙ ценности как
человека.</p>

<h3>Шаги правильного ответа</h3>
<ul>
<li><strong>Сначала постарайтесь понять.</strong> Если комментарий
непонятен, не защищайтесь сразу — задайте уточняющий вопрос: "Ты имеешь
в виду случай, когда X?" Это не защита, а поиск ясности.</li>
<li><strong>Если согласны — ИСПРАВЬТЕ, а не просто напишите "OK".</strong>
Когда код изменён, покажите это (например, добавив новый коммит и
ответив "Исправлено: abc123") — reviewer должен видеть, что изменение
реально произошло.</li>
<li><strong>Если не согласны — возразите С УВАЖЕНИЕМ и С ДОКАЗАТЕЛЬСТВОМ.</strong>
Не "нет, это неправильно", а "Я выбрал другой подход здесь по причине X,
потому что Y — но если ты имел в виду случай Z, тогда ты прав, я
пересмотрю". Отклонение обратной связи — нормально, если оно
подкреплено ДОКАЗАТЕЛЬСТВОМ.</li>
<li><strong>Отмечайте каждый комментарий как "Resolved" только после
реального решения.</strong> Если закрыть обсуждение ("resolve") без
изменения кода, reviewer в следующий раз перестанет доверять вашей
пометке "Resolved".</li>
</ul>

<h3>Повторный запрос ревью (re-request review) — последний шаг</h3>
<p>После ответа на все комментарии PR снова возвращается в состояние
<code>Запрошено ревью</code> (вспомните диаграмму урока 0) — на GitHub
это делается кнопкой "Re-request review". Это НЕЛЬЗЯ забывать: если вы
просто измените код, не уведомив reviewer'а, он может не узнать, что PR
готов.</p>

<h3>Почему спорить хорошо, если это подкреплено доказательствами</h3>
<p>Принятие "без эго" не значит соглашаться со всем. Если reviewer
ошибочно предположил (например, не знал, что ваш подход уже правильно
обрабатывает этот случай), ЧЁТКО объяснить это — здоровая дискуссия, а
не эго. Разница — в опоре не на ЭМОЦИИ, а на ДОКАЗАТЕЛЬСТВА: не "потому
что я ТАК чувствую", а "потому что проверка в строке 42 уже покрывает
именно этот случай".</p>

<h3>Жизненный путь одной ветки комментария</h3>
<pre class="mermaid">
sequenceDiagram
    participant R as Reviewer
    participant M as Автор
    R->>M: Оставляет комментарий (урок 6: точный, actionable)
    M->>M: Пытается понять
    alt Непонятно
        M->>R: Задаёт уточняющий вопрос
        R->>M: Отвечает
    end
    alt Согласен
        M->>M: Исправляет код, новый коммит
        M->>R: Отвечает "Исправлено: abc123"
    else Не согласен, есть доказательство
        M->>R: Объясняет с уважением и доказательством
        R->>M: Рассматривает, соглашается или нет
    end
    M->>R: Re-request review
</pre>
<p>Диаграмма показывает полный разговор вокруг одного комментария — это
увеличенный вид того, что происходит ВНУТРИ блока "Changes requested" на
большой диаграмме состояний PR из урока 0.</p>

<h3>Несколько циклов — это нормально, а не усталость</h3>
<p>Иногда один PR проходит 3-4 цикла "changes requested" ->
исправление -> повторный запрос. Это ожидаемо, особенно для больших или
сложных изменений, а НЕ неудача. Если вы устали от множества циклов и
говорите "ладно, со всем согласен" — это тоже проблема эго, только с
обратной стороны: теперь вы сдаёте своё мнение без доказательств.
Правильный подход — отвечать на каждый цикл так же внимательно, как на
первый, независимо от их количества.</p>

<h3>Кнопка "Resolve conversation" — кто должен нажимать</h3>
<p>На GitHub каждую ветку комментариев закрывает кнопка "Resolve
conversation". Во многих командах конвенция такая: её нажимает
REVIEWER, а не автор — потому что именно reviewer подтверждает, что его
комментарий РЕАЛЬНО решён. Если автор закрывает сам (мягкая форма
ошибки "resolve without fixing" из начала урока 7), reviewer в следующий
раз перестанет доверять этой пометке и будет вынужден перечитывать
КАЖДУЮ "Resolved" ветку — это ЗАМЕДЛЯЕТ весь процесс.</p>

<h3>Как это связано с уроками 4 и 6</h3>
<p>В уроке 4 мы увидели, на что reviewer обращает внимание, в уроке 6 —
КАК это записать. Этот урок — вторая половина того же процесса: со
стороны автора. Обе стороны служат одной цели — три причины из урока 0
(поймать ошибку, обмен знаниями, поддержание стандарта) — и это
показывает, что это ответственность не только REVIEWER'А, но и АВТОРА.</p>
""".strip()

L7_CODE = """
# ============================================================
# Fikr-mulohazaga javob berish - to'rt xil ssenariy
# ============================================================

class ReviewThread:
    def __init__(self, comment: str):
        self.comment = comment
        self.status = "open"
        self.replies = []

    def clarify(self, question: str):
        \"\"\"Tushunarsiz bo'lsa - aniqlashtiruvchi savol.\"\"\"
        self.replies.append(f"SAVOL: {question}")
        return self

    def agree_and_fix(self, commit_hash: str):
        \"\"\"Rozi bo'lsa - tuzatish, keyin javob.\"\"\"
        self.replies.append(f"Tuzatildi: {commit_hash}")
        self.status = "resolved"
        return self

    def respectfully_disagree(self, reasoning: str):
        \"\"\"Rozi bo'lmasa - dalil bilan, hurmat bilan.\"\"\"
        self.replies.append(f"Boshqacha fikr, sababi: {reasoning}")
        # E'tibor bering: status HALI "resolved" emas - reviewer ko'rib
        # chiqishi kerak, muallif bir tomonlama yopmaydi
        return self

    def resolve_without_fixing(self):
        \"\"\"YOMON namuna - kod o'zgarmasdan yopish.\"\"\"
        self.status = "resolved"
        return self  # <- reviewer keyingi safar ishonmay qoladi


# --- Yaxshi ssenariy: rozi bo'lib, tuzatib, javob berish ---
thread1 = ReviewThread("student_answer None bo'lsa AttributeError beradi")
thread1.agree_and_fix("a1b2c3d")
print(thread1.status, thread1.replies)
# resolved ['Tuzatildi: a1b2c3d']

# --- Yaxshi ssenariy: dalil bilan qarshi chiqish ---
thread2 = ReviewThread("Bu yerda indeks tekshiruvi yetishmayapti")
thread2.respectfully_disagree(
    "42-qatordagi if not student_answer: tekshiruvi aynan shu holatni allaqachon qamrab oladi"
)
print(thread2.status, thread2.replies)
# open ['Boshqacha fikr, sababi: ...']  <- reviewer hali ko'rib chiqmagan

# --- YOMON ssenariy: kod o'zgarmasdan "Resolved" ---
thread3 = ReviewThread("Bu funksiya juda uzun, bo'ling")
thread3.resolve_without_fixing()
print(thread3.status, thread3.replies)
# resolved []  <- HECH NARSA o'zgarmadi, faqat yopildi - ishonchni yo'qotadi
""".strip()

L7_CODE_RU = """
# ============================================================
# Ответ на обратную связь - четыре разных сценария
# ============================================================

class ReviewThread:
    def __init__(self, comment: str):
        self.comment = comment
        self.status = "open"
        self.replies = []

    def clarify(self, question: str):
        \"\"\"Если непонятно - уточняющий вопрос.\"\"\"
        self.replies.append(f"ВОПРОС: {question}")
        return self

    def agree_and_fix(self, commit_hash: str):
        \"\"\"Если согласны - исправление, затем ответ.\"\"\"
        self.replies.append(f"Исправлено: {commit_hash}")
        self.status = "resolved"
        return self

    def respectfully_disagree(self, reasoning: str):
        \"\"\"Если не согласны - с доказательством, с уважением.\"\"\"
        self.replies.append(f"Другое мнение, причина: {reasoning}")
        # Обратите внимание: статус ЕЩЁ не "resolved" - reviewer должен
        # рассмотреть, автор не закрывает односторонне
        return self

    def resolve_without_fixing(self):
        \"\"\"ПЛОХОЙ пример - закрытие без изменения кода.\"\"\"
        self.status = "resolved"
        return self  # <- reviewer в следующий раз перестанет доверять


# --- Хороший сценарий: согласиться, исправить, ответить ---
thread1 = ReviewThread("Если student_answer None, будет AttributeError")
thread1.agree_and_fix("a1b2c3d")
print(thread1.status, thread1.replies)
# resolved ['Исправлено: a1b2c3d']

# --- Хороший сценарий: возразить с доказательством ---
thread2 = ReviewThread("Здесь не хватает проверки индекса")
thread2.respectfully_disagree(
    "Проверка if not student_answer: в строке 42 уже покрывает именно этот случай"
)
print(thread2.status, thread2.replies)
# open ['Другое мнение, причина: ...']  <- reviewer ещё не рассмотрел

# --- ПЛОХОЙ сценарий: "Resolved" без изменения кода ---
thread3 = ReviewThread("Эта функция слишком длинная, разделите её")
thread3.resolve_without_fixing()
print(thread3.status, thread3.replies)
# resolved []  <- НИЧЕГО не изменилось, просто закрыто - теряет доверие
""".strip()

L7_TASK = {
    "task_title": "Real yoki xayoliy izohga to'rt ssenariy bo'yicha javob yozing",
    "task_title_ru": "Ответьте на реальный или условный комментарий по четырём сценариям",
    "task_description": (
        "0-darsda tanlagan PR'dagi (yoki xayoliy) uchta review izohini "
        "oling. Har biriga: (1) agar tushunarsiz bo'lsa qanday "
        "aniqlashtiruvchi savol berган bo'lardingiz, (2) agar rozi "
        "bo'lsangiz qanday javob yozgan bo'lardingiz (kod o'zgarishi "
        "bilan birga), (3) agar rozi bo'lmasangiz, qanday dalil bilan "
        "hurmat saqlagan holda qarshi chiqqan bo'lardingiz."
    ),
    "task_description_ru": (
        "Возьмите три комментария ревью из PR, выбранного в уроке 0 (или "
        "условных). Для каждого напишите: (1) какой уточняющий вопрос вы "
        "задали бы, если непонятно, (2) какой ответ написали бы, если "
        "согласны (вместе с изменением кода), (3) как бы вы уважительно "
        "возразили с доказательством, если не согласны."
    ),
    "task_requirements": (
        "1) Uchta izohning har biri uchun barcha uch ssenariy yozilishi "
        "kerak (9 ta javob jami). 2) \"Rozi emas\" ssenariysida kamida "
        "bitta kod qatoriga yoki testga ishora qilingan dalil bo'lishi "
        "shart. 3) Hech qanday javob \"chunki men shunday his qilaman\" "
        "kabi hissiy asosga qurilmagan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) Для каждого из трёх комментариев должны быть написаны все три "
        "сценария (итого 9 ответов). 2) В сценарии \"не согласен\" должно "
        "быть минимум одно доказательство со ссылкой на строку кода или "
        "тест. 3) Ни один ответ не должен опираться на эмоциональное "
        "основание вроде \"потому что я так чувствую\"."
    ),
    "task_technologies": "GitHub (Pull Request Review), yozma javob",
    "task_deadline_days": 3,
}

L7_SAMPLE = {
    "title": "Namuna: fikr-mulohazaga javob berishning to'rt ssenariysi",
    "description": (
        "Ushbu darsning kod namunasi asosida, ReviewThread klassi orqali "
        "to'rtta javob ssenariysini (aniqlashtirish, rozi+tuzatish, "
        "hurmat bilan qarshi chiqish, yomon namuna) modellashtirish."
    ),
    "sample_type": "python",
    "code_files": [
        {"filename": "review_thread_demo.py", "language": "python", "code": "# Qarang: L7_CODE ushbu darsning to'liq matnida"},
    ],
}

L7_EXERCISES = [
    {
        "title": "Fikr-mulohaza kimga qaratilgan",
        "title_ru": "На кого направлена обратная связь",
        "description": "Review izohi asosan NIMAGA qaratilgan bo'lishi kerak?",
        "description_ru": "На что должен быть в первую очередь направлен комментарий ревью?",
        "exercise_type": "multiple_choice",
        "options": ["Muallifning shaxsiga", "Kodga", "Muallifning tajribasiga", "Boshqa dasturchilar bilan solishtirishga"],
        "options_ru": ["На личность автора", "На код", "На опыт автора", "На сравнение с другими разработчиками"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsning boshida aytilgan asosiy tamoyilni eslang.",
        "hint_ru": "Вспомните главный принцип, сказанный в начале урока.",
        "explanation": "Fikr-mulohaza doim KOD haqida bo'lishi kerak - muallifning shaxsi yoki qadr-qimmati haqida emas.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "\"Resolved\" belgisi qachon qo'yiladi",
        "title_ru": "Когда ставится пометка \"Resolved\"",
        "description": "Review izohini \"Resolved\" deb belgilash qachon TO'G'RI?",
        "description_ru": "Когда правильно помечать комментарий ревью как \"Resolved\"?",
        "exercise_type": "multiple_choice",
        "options": [
            "Izoh qoldirilgan zahoti",
            "Faqat kod haqiqatan o'zgargandan yoki masala haqiqatan hal bo'lgandan keyin",
            "Reviewer band bo'lsa",
            "PR ochilgan kuni",
        ],
        "options_ru": [
            "Сразу после того, как оставлен комментарий",
            "Только после того, как код реально изменился или вопрос реально решён",
            "Когда reviewer занят",
            "В день открытия PR",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsda aytilgan: kod o'zgarmasdan yopish ishonchni yo'qotadi.",
        "hint_ru": "В уроке сказано: закрытие без изменения кода теряет доверие.",
        "explanation": "Kod o'zgarmasdan \"Resolved\" belgilash reviewer'ning kelajakdagi ishonchini pasaytiradi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Bir izoh mavzusining qadamlarini tartiblang",
        "title_ru": "Расположите шаги одной ветки комментария по порядку",
        "description": "Muallif tomonidan bitta review izohiga javob berish qadamlarini tartibga soling.",
        "description_ru": "Расположите шаги ответа автора на один комментарий ревью по порядку.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Izohni diqqat bilan o'qib tushunishga harakat qilish",
            "Kerak bo'lsa aniqlashtiruvchi savol berish",
            "Rozi bo'lsa kodni tuzatib, javob yozish",
            "Barcha izohlardan keyin qayta review so'rash",
        ],
        "drag_items_ru": [
            "Внимательно прочитать и постараться понять комментарий",
            "При необходимости задать уточняющий вопрос",
            "Если согласен, исправить код и ответить",
            "После всех комментариев запросить повторное ревью",
        ],
        "correct_order": [
            "Izohni diqqat bilan o'qib tushunishga harakat qilish",
            "Kerak bo'lsa aniqlashtiruvchi savol berish",
            "Rozi bo'lsa kodni tuzatib, javob yozish",
            "Barcha izohlardan keyin qayta review so'rash",
        ],
        "hint": "Sequence diagrammadagi Muallif qatoridagi harakatlar tartibini eslang.",
        "hint_ru": "Вспомните порядок действий автора на sequence-диаграмме.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 8 — Merge strategiyalari: merge commit, squash, rebase-merge
# ---------------------------------------------------------------------------

L8_TEXT = """
<h3>PR "Approved" bo'lgandan keyin ham hali bir qaror qoladi</h3>
<p>0-darsdagi diagrammada <code>Approved</code>dan keyin darhol
<code>Merged</code> keladi — lekin GitHub'da bu bitta tugma emas, uchta
variant: <strong>"Create a merge commit"</strong>, <strong>"Squash and
merge"</strong>, <strong>"Rebase and merge"</strong>. Bu — jamoa
darajasida OLDINDAN qaror qilinishi kerak bo'lgan tanlov, chunki u
loyihaning BUTUN kelajakdagi tarixi qanday ko'rinishiga ta'sir qiladi.
112-kursda <code>git rebase</code>ning ICHKI ishlash mexanizmini
o'rgangansiz — bu darsda esa uni jamoaviy MERGE STRATEGIYASI sifatida,
tarix o'qilishi nuqtai nazaridan ko'rib chiqamiz.</p>

<h3>Uchta strategiya — nima qiladi</h3>
<ul>
<li><strong>Merge commit</strong> — feature branch'ning BARCHA
commit'lari saqlanadi, ustiga ikkita ota-commit'ga ega bitta
"merge commit" qo'shiladi. Natija: <code>git log --graph</code>da
tarmoqlanish ko'rinadi (haqiqiy branch tuzilishi saqlanadi).</li>
<li><strong>Squash and merge</strong> — feature branch'dagi BARCHA
commit'lar BITTA yangi commit'ga "siqiladi" va <code>main</code>ga
chiziqli qo'shiladi. Feature branch'dagi individual commit'lar (masalan
"wip", "fix typo", "address review comments") <code>main</code>
tarixida UMUMAN ko'rinmaydi — faqat yakuniy natija.</li>
<li><strong>Rebase and merge</strong> — feature branch'ning HAR BIR
commit'i (o'zgarishsiz yoki tozalangan holda) <code>main</code>ning
oxiriga ketma-ket qo'shiladi, merge commit'siz. Natija: chiziqli tarix,
lekin (squash'dan farqli) individual commit'lar saqlanadi.</li>
</ul>

<h3>Jamoa tarixi o'qilishi nuqtai nazaridan trade-off</h3>
<p><strong>Merge commit</strong>ning afzalligi — HECH narsa yo'qolmaydi,
har bir "wip" commit ham tarixda qoladi; kamchiligi — katta jamoada
<code>git log --graph</code> chalkash "spagetti" ko'rinishga aylanishi
mumkin. <strong>Squash</strong>ning afzalligi — <code>main</code> tarixi
har doim TOZA: bitta PR = bitta commit, <code>git log --oneline</code>
o'qish oson (aynan shu kursning 2-darsida ko'rgan formatga mos); kamchiligi
— agar feature branch'da qimmatli, alohida ko'rib chiqilishi kerak
bo'lgan oraliq qadamlar bo'lsa, ular yo'qoladi. <strong>Rebase and
merge</strong> — ikkalasining o'rtasi: chiziqli VA batafsil, lekin
feature branch'dagi HAR bir commit (hatto "fix typo" kabi kichiklari
ham) alohida saqlanadi — bu 3-darsda o'rgangan ATOMIKLIK talabini
oshiradi, chunki endi HAR bir commit <code>main</code>da abadiy qoladi.</p>

<h3>Bu platforma qaysi yondashuvni tanlagan (kuzatilgan holat)</h3>
<p><code>git log --merges --oneline</code> buyrug'i bu repozitoriyada
BIRORTA HAM merge commit yo'qligini ko'rsatadi — bu bitta maintainer
to'g'ridan-to'g'ri <code>server</code> branch'iga push qilgani (PR
jarayonisiz) yoki har doim squash/rebase uslubida ishlagani sababli.
Tarix o'zi CHIZIQLI: <code>git log --oneline</code>da har bir yozuv
alohida, tarmoqlanishsiz commit. Bu — kichik jamoa yoki yakka
loyihalarda keng tarqalgan, sodda yondashuv, lekin ko'p muallifli
jamoada odatda GitHub darajasida ANIQ tanlov (repozitoriya
sozlamalarida qaysi merge tugmalari yoqilgan) qilinishi kerak.</p>

<h3>Uchta strategiya — vizual taqqoslash</h3>
<pre class="mermaid">
flowchart TB
  subgraph MC["Merge commit"]
    direction LR
    m1["main"] --> m2["main"] --> mc["Merge commit
(2 ota-commit)"]
    f1["feature: c1"] --> f2["feature: c2"] --> f3["feature: c3"] --> mc
  end
  subgraph SQ["Squash and merge"]
    direction LR
    s1["main"] --> s2["main"] --> sq["1 ta yangi commit
(c1+c2+c3 siqilgan)"]
  end
  subgraph RB["Rebase and merge"]
    direction LR
    r1["main"] --> rc1["c1"] --> rc2["c2"] --> rc3["c3"]
  end
  style MC fill:#d6e9ff,stroke:#2266aa
  style SQ fill:#d6f5d6,stroke:#2a8a2a
  style RB fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma uchta strategiyaning natija tarixini ko'rsatadi: Merge
commit'da tarmoqlanish saqlanadi va alohida merge-commit qo'shiladi;
Squash'da uchta commit BITTA commit'ga aylanadi; Rebase'da uchta commit
ALOHIDA holicha, lekin chiziqli tartibda <code>main</code>ga qo'shiladi.</p>

<h3>Qaysi holatda qaysi strategiya tavsiya etiladi</h3>
<p>Kichik, tez-tez PR ochiladigan jamoalar odatda <strong>Squash</strong>ni
tanlaydi — <code>main</code> tarixi toza va 2-darsdagi Conventional
Commits formatini saqlash oson (chunki faqat BITTA yakuniy xabar
yoziladi). Katta, kompleks feature'lar ustida ishlaydigan jamoalar,
ayniqsa oraliq qadamlar muhim bo'lsa, <strong>Merge commit</strong>ni
afzal ko'rishi mumkin. <strong>Rebase and merge</strong> — atomik
commit madaniyati (3-dars) allaqachon kuchli bo'lgan, har bir individual
commit yaxshi yozilgan jamoalarda eng ma'noli.</p>
""".strip()

L8_TEXT_RU = """
<h3>После "Approved" остаётся ещё одно решение</h3>
<p>На диаграмме урока 0 сразу после <code>Approved</code> идёт
<code>Merged</code> — но на GitHub это не одна кнопка, а три варианта:
<strong>"Create a merge commit"</strong>, <strong>"Squash and
merge"</strong>, <strong>"Rebase and merge"</strong>. Это выбор,
который должен быть решён ЗАРАНЕЕ на уровне команды, потому что он
влияет на то, как будет выглядеть ВСЯ будущая история проекта. В курсе
112 вы изучили ВНУТРЕННИЙ механизм работы <code>git rebase</code> — в
этом уроке рассмотрим его как КОМАНДНУЮ СТРАТЕГИЮ слияния, с точки
зрения читаемости истории.</p>

<h3>Три стратегии — что они делают</h3>
<ul>
<li><strong>Merge commit</strong> — ВСЕ коммиты feature-ветки
сохраняются, поверх добавляется один "merge commit" с двумя
родительскими коммитами. Результат: в <code>git log --graph</code>
видно ветвление (сохраняется реальная структура веток).</li>
<li><strong>Squash and merge</strong> — ВСЕ коммиты feature-ветки
"сжимаются" в ОДИН новый коммит и добавляются в <code>main</code>
линейно. Отдельные коммиты feature-ветки (например "wip", "fix typo",
"address review comments") в истории <code>main</code> ВООБЩЕ не видны
— только конечный результат.</li>
<li><strong>Rebase and merge</strong> — КАЖДЫЙ коммит feature-ветки (без
изменений или очищенный) добавляется в конец <code>main</code>
последовательно, без merge commit. Результат: линейная история, но (в
отличие от squash) отдельные коммиты сохраняются.</li>
</ul>

<h3>Компромисс с точки зрения читаемости командной истории</h3>
<p>Преимущество <strong>merge commit</strong> — НИЧЕГО не теряется,
каждый коммит "wip" остаётся в истории; недостаток — в большой команде
<code>git log --graph</code> может превратиться в запутанное
"спагетти". Преимущество <strong>squash</strong> — история
<code>main</code> всегда ЧИСТАЯ: один PR = один коммит, легко читать
<code>git log --oneline</code> (соответствует формату из урока 2);
недостаток — если в feature-ветке были ценные, отдельно важные
промежуточные шаги, они теряются. <strong>Rebase and merge</strong> —
среднее между двумя: линейная И подробная, но КАЖДЫЙ коммит
feature-ветки (даже мелкие вроде "fix typo") сохраняется отдельно — это
повышает требование к АТОМАРНОСТИ из урока 3, потому что теперь КАЖДЫЙ
коммит остаётся в <code>main</code> навсегда.</p>

<h3>Какой подход выбрала эта платформа (наблюдаемое состояние)</h3>
<p>Команда <code>git log --merges --oneline</code> показывает, что в
этом репозитории НЕТ НИ ОДНОГО merge commit — потому что один
maintainer пушит напрямую в ветку <code>server</code> (без процесса PR)
или всегда работал в стиле squash/rebase. История сама ЛИНЕЙНА: в
<code>git log --oneline</code> каждая запись — отдельный коммит без
ветвления. Это — распространённый, простой подход в маленьких командах
или сольных проектах, но в команде с несколькими авторами обычно нужен
ЧЁТКИЙ выбор на уровне GitHub (какие кнопки merge включены в настройках
репозитория).</p>

<h3>Три стратегии — визуальное сравнение</h3>
<pre class="mermaid">
flowchart TB
  subgraph MC["Merge commit"]
    direction LR
    m1["main"] --> m2["main"] --> mc["Merge commit
(2 родителя)"]
    f1["feature: c1"] --> f2["feature: c2"] --> f3["feature: c3"] --> mc
  end
  subgraph SQ["Squash and merge"]
    direction LR
    s1["main"] --> s2["main"] --> sq["1 новый коммит
(c1+c2+c3 сжаты)"]
  end
  subgraph RB["Rebase and merge"]
    direction LR
    r1["main"] --> rc1["c1"] --> rc2["c2"] --> rc3["c3"]
  end
  style MC fill:#d6e9ff,stroke:#2266aa
  style SQ fill:#d6f5d6,stroke:#2a8a2a
  style RB fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает итоговую историю трёх стратегий: в Merge commit
сохраняется ветвление и добавляется отдельный merge-коммит; в Squash три
коммита превращаются в ОДИН; в Rebase три коммита остаются ОТДЕЛЬНЫМИ,
но добавляются в <code>main</code> линейно.</p>

<h3>Какая стратегия рекомендуется в каком случае</h3>
<p>Маленькие команды с частыми PR обычно выбирают <strong>Squash</strong>
— история <code>main</code> чистая, и легко сохранить формат Conventional
Commits из урока 2 (потому что пишется только ОДНО итоговое сообщение).
Команды, работающие над большими сложными фичами, особенно если важны
промежуточные шаги, могут предпочесть <strong>Merge commit</strong>.
<strong>Rebase and merge</strong> наиболее осмыслен в командах, где уже
сильна культура атомарных коммитов (урок 3), и каждый отдельный коммит
хорошо написан.</p>
""".strip()

L8_CODE = """
# ============================================================
# Uchta merge strategiyasi natijasini git buyruqlari orqali
# simulyatsiya qilish (kontseptual - real branch ustida sinab
# ko'rish mumkin)
# ============================================================

# --- Boshlang'ich holat: main'da 2 commit, feature'da 3 commit ---
# main:    M1 -- M2
# feature:         \\-- F1 -- F2 -- F3

# --- 1) Merge commit ---
# $ git checkout main
# $ git merge --no-ff feature
# Natija:  M1 -- M2 --------- MC (2 ota: M2 va F3)
#                \\-- F1-F2-F3 /
# git log --graph BUTUN tarmoqlanishni ko'rsatadi

# --- 2) Squash and merge ---
# $ git checkout main
# $ git merge --squash feature
# $ git commit -m "feat(x): add complete feature (from F1+F2+F3)"
# Natija:  M1 -- M2 -- S (F1,F2,F3 BITTA commit'ga siqilgan)
# F1/F2/F3 alohida holda main tarixida UMUMAN yo'q

# --- 3) Rebase and merge ---
# $ git checkout feature
# $ git rebase main
# $ git checkout main
# $ git merge --ff-only feature
# Natija:  M1 -- M2 -- F1' -- F2' -- F3'  (chiziqli, HAR biri alohida)

# ============================================================
# Bu platformaning o'z holati: git log --merges --oneline BO'SH -
# demak birorta ham "Merge commit" (2 ota-commitli) yo'q. Butun
# tarix chiziqli - yakka maintainer bevosita push qilgani yoki
# squash/rebase uslubidan foydalanilgani sababli.
# ============================================================

# ============================================================
# Har bir strategiyaning natija tarixini tekshiruvchi kichik
# yordamchi - qaysi strategiya nechta YANGI commit qo'shishini
# hisoblaydi
# ============================================================


def count_new_commits_on_main(strategy: str, feature_commit_count: int) -> int:
    \"\"\"8-darsdagi uchta strategiyaning har biri main'ga NECHTA yangi
    commit qo'shishini qaytaradi.\"\"\"
    if strategy == "merge_commit":
        return feature_commit_count + 1   # barcha commit'lar + 1 ta merge commit
    if strategy == "squash":
        return 1                          # barchasi BITTA commit'ga siqiladi
    if strategy == "rebase":
        return feature_commit_count       # har biri alohida, lekin merge commit'siz
    raise ValueError(f"noma'lum strategiya: {strategy!r}")


for strategy in ("merge_commit", "squash", "rebase"):
    n = count_new_commits_on_main(strategy, feature_commit_count=3)
    print(f"{strategy:>12}: main'ga {n} ta yangi commit qo'shiladi")

# merge_commit: main'ga 4 ta yangi commit qo'shiladi   (3 + 1 merge)
# squash:       main'ga 1 ta yangi commit qo'shiladi
# rebase:       main'ga 3 ta yangi commit qo'shiladi   (har biri alohida)
""".strip()

L8_CODE_RU = """
# ============================================================
# Симуляция результата трёх стратегий merge через команды git
# (концептуально - можно опробовать на реальной ветке)
# ============================================================

# --- Начальное состояние: 2 коммита в main, 3 в feature ---
# main:    M1 -- M2
# feature:         \\-- F1 -- F2 -- F3

# --- 1) Merge commit ---
# $ git checkout main
# $ git merge --no-ff feature
# Результат:  M1 -- M2 --------- MC (2 родителя: M2 и F3)
#                   \\-- F1-F2-F3 /
# git log --graph показывает ВСЁ ветвление

# --- 2) Squash and merge ---
# $ git checkout main
# $ git merge --squash feature
# $ git commit -m "feat(x): add complete feature (from F1+F2+F3)"
# Результат:  M1 -- M2 -- S (F1,F2,F3 сжаты в ОДИН коммит)
# F1/F2/F3 отдельно в истории main ВООБЩЕ отсутствуют

# --- 3) Rebase and merge ---
# $ git checkout feature
# $ git rebase main
# $ git checkout main
# $ git merge --ff-only feature
# Результат:  M1 -- M2 -- F1' -- F2' -- F3'  (линейно, КАЖДЫЙ отдельно)

# ============================================================
# Собственное состояние этой платформы: git log --merges --oneline
# ПУСТ - значит, нет ни одного "Merge commit" (с 2 родителями). Вся
# история линейна - единственный maintainer пушил напрямую или
# использовал стиль squash/rebase.
# ============================================================

# ============================================================
# Небольшой помощник, проверяющий итоговую историю каждой стратегии -
# считает, сколько НОВЫХ коммитов добавит каждая стратегия
# ============================================================


def count_new_commits_on_main(strategy: str, feature_commit_count: int) -> int:
    \"\"\"Возвращает, сколько НОВЫХ коммитов добавит в main каждая из
    трёх стратегий урока 8.\"\"\"
    if strategy == "merge_commit":
        return feature_commit_count + 1   # все коммиты + 1 merge commit
    if strategy == "squash":
        return 1                          # всё сжимается в ОДИН коммит
    if strategy == "rebase":
        return feature_commit_count       # каждый отдельно, но без merge commit
    raise ValueError(f"неизвестная стратегия: {strategy!r}")


for strategy in ("merge_commit", "squash", "rebase"):
    n = count_new_commits_on_main(strategy, feature_commit_count=3)
    print(f"{strategy:>12}: в main добавится {n} новых коммитов")

# merge_commit: в main добавится 4 новых коммитов   (3 + 1 merge)
# squash:       в main добавится 1 новых коммитов
# rebase:       в main добавится 3 новых коммитов   (каждый отдельно)
""".strip()

L8_TASK = {
    "task_title": "Bitta feature uchun uch xil merge strategiyasini sinab ko'ring",
    "task_title_ru": "Опробуйте три разные стратегии merge для одной фичи",
    "task_description": (
        "Shaxsiy test repozitoriyasida (yoki shu platformaning fork'ida) "
        "bitta feature branch yarating, unga 3 ta atomik commit qiling. "
        "Branch'ni UCH MARTA (alohida nusxalarda) main'ga qo'shing: birinchi "
        "safar 'merge commit', ikkinchi safar 'squash', uchinchi safar "
        "'rebase' orqali. Har safar `git log --graph --oneline` natijasini "
        "saqlab, uch natijani solishtiring."
    ),
    "task_description_ru": (
        "В тестовом репозитории (или форке этой платформы) создайте одну "
        "feature-ветку с 3 атомарными коммитами. Слейте ветку с main ТРИ "
        "РАЗА (в отдельных копиях): первый раз через 'merge commit', "
        "второй - через 'squash', третий - через 'rebase'. Каждый раз "
        "сохраните вывод `git log --graph --oneline` и сравните три "
        "результата."
    ),
    "task_requirements": (
        "1) Uchala `git log --graph --oneline` natijasi ilova qilinishi "
        "kerak. 2) Har bir strategiya uchun main'da nechta yangi commit "
        "paydo bo'lganini (1 ta squash uchun, 3 ta rebase uchun, 4 ta "
        "merge commit uchun - 3 original + 1 merge) yozing. 3) Qaysi "
        "strategiyani QAYSI jamoa uchun tavsiya qilishingizni asoslang."
    ),
    "task_requirements_ru": (
        "1) Приложить все три вывода `git log --graph --oneline`. 2) "
        "Написать, сколько новых коммитов появилось в main для каждой "
        "стратегии (1 для squash, 3 для rebase, 4 для merge commit - 3 "
        "оригинала + 1 merge). 3) Обосновать, какую стратегию для какой "
        "команды вы бы рекомендовали."
    ),
    "task_technologies": "Git (merge, squash, rebase)",
    "task_deadline_days": 4,
}

L8_SAMPLE = {
    "title": "Namuna: uch merge strategiyasini bosqichma-bosqich ko'rsatuvchi skript",
    "description": (
        "Ushbu darsning kod namunasi asosida, uchta merge strategiyasi "
        "uchun kerakli git buyruqlarini bosqichma-bosqich, izohlar bilan "
        "ko'rsatuvchi bash skripti."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "compare_merge_strategies.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "# Bitta feature branch'ni uchta strategiyada, uchta alohida\n"
                "# nusxada sinab ko'radigan demo skript.\n"
                "set -e\n\n"
                "setup_demo_repo() {\n"
                "    rm -rf /tmp/merge-demo && mkdir /tmp/merge-demo && cd /tmp/merge-demo\n"
                "    git init -q\n"
                "    echo 'main v1' > file.txt && git add . && git commit -qm 'chore: init'\n"
                "    git checkout -qb feature\n"
                "    echo 'f1' >> file.txt && git commit -aqm 'feat(x): step one'\n"
                "    echo 'f2' >> file.txt && git commit -aqm 'feat(x): step two'\n"
                "    echo 'f3' >> file.txt && git commit -aqm 'feat(x): step three'\n"
                "    git checkout -q main\n"
                "}\n\n"
                "echo '=== 1) Merge commit ==='\n"
                "setup_demo_repo && git merge --no-ff -q feature -m 'merge feature'\n"
                "git log --graph --oneline\n\n"
                "echo '=== 2) Squash and merge ==='\n"
                "setup_demo_repo && git merge --squash -q feature && git commit -qm 'feat(x): add complete feature'\n"
                "git log --graph --oneline\n\n"
                "echo '=== 3) Rebase and merge ==='\n"
                "setup_demo_repo && git checkout -q feature && git rebase -q main && git checkout -q main && git merge -q --ff-only feature\n"
                "git log --graph --oneline\n"
            ),
        }
    ],
}

L8_EXERCISES = [
    {
        "title": "Squash natijasi",
        "title_ru": "Результат Squash",
        "description": "Squash and merge orqali qo'shilgan 3 ta feature commit main'da nechta yangi commit sifatida ko'rinadi?",
        "description_ru": "Сколько новых коммитов появится в main для 3 коммитов feature-ветки при Squash and merge?",
        "exercise_type": "multiple_choice",
        "options": ["3 ta", "1 ta", "4 ta", "0 ta"],
        "options_ru": ["3", "1", "4", "0"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "\"Squash\" so'zi \"siqish\" ma'nosini bildiradi.",
        "hint_ru": "Слово \"Squash\" означает \"сжатие\".",
        "explanation": "Squash BARCHA commit'larni BITTA yangi commit'ga siqadi - individual commit'lar main tarixida ko'rinmaydi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Bu platformaning kuzatilgan holati",
        "title_ru": "Наблюдаемое состояние этой платформы",
        "description": "git log --merges --oneline ushbu repozitoriyada nima ko'rsatadi?",
        "description_ru": "Что покажет git log --merges --oneline в этом репозитории?",
        "exercise_type": "multiple_choice",
        "options": [
            "O'nlab merge commit",
            "Bo'sh natija - birorta ham merge commit yo'q",
            "Faqat bitta eng katta merge commit",
            "Xato xabari",
        ],
        "options_ru": [
            "Десятки merge commit",
            "Пустой результат - нет ни одного merge commit",
            "Только один самый большой merge commit",
            "Сообщение об ошибке",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsda bu repozitoriyaning haqiqiy holati alohida aytilgan.",
        "hint_ru": "В уроке отдельно указано реальное состояние этого репозитория.",
        "explanation": "Bu repozitoriyaning tarixi butunlay chiziqli - hech qanday 2-ota-commitli merge commit yo'q.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Strategiya va uning xususiyatini moslashtiring",
        "title_ru": "Сопоставьте стратегию и её особенность",
        "description": "Uchta merge strategiyasini, ularning asosiy xususiyati tartibida joylashtiring (merge commit -> squash -> rebase).",
        "description_ru": "Расположите три стратегии merge в порядке их основной особенности (merge commit -> squash -> rebase).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Merge commit (tarmoqlanish saqlanadi)",
            "Squash and merge (bitta commit'ga siqiladi)",
            "Rebase and merge (chiziqli, lekin har biri alohida)",
        ],
        "drag_items_ru": [
            "Merge commit (ветвление сохраняется)",
            "Squash and merge (сжимается в один коммит)",
            "Rebase and merge (линейно, но каждый отдельно)",
        ],
        "correct_order": [
            "Merge commit (tarmoqlanish saqlanadi)",
            "Squash and merge (bitta commit'ga siqiladi)",
            "Rebase and merge (chiziqli, lekin har biri alohida)",
        ],
        "hint": "Darsdagi \"Uchta strategiya - nima qiladi\" bo'limidagi tartibni eslang.",
        "hint_ru": "Вспомните порядок из раздела \"Три стратегии - что они делают\" в уроке.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Qaysi strategiya 2-darsning formatini saqlash oson",
        "title_ru": "Какая стратегия легче сохраняет формат урока 2",
        "description": "___ strategiyasi main tarixini eng TOZA saqlaydi, chunki har bir PR uchun faqat bitta yakuniy Conventional Commits xabari yoziladi.",
        "description_ru": "Стратегия ___ сохраняет историю main самой ЧИСТОЙ, так как для каждого PR пишется только одно итоговое сообщение Conventional Commits.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "Squash",  # literal strategy/UI name, no natural-language RU translation needed
        "hint": "Bir necha kichik commit'ni bitta yakuniy commit'ga aylantiradigan strategiya.",
        "hint_ru": "Стратегия, превращающая несколько мелких коммитов в один итоговый.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 9 — Semantik versiyalash (SemVer): MAJOR.MINOR.PATCH
# ---------------------------------------------------------------------------

L9_TEXT = """
<h3>Merge qilingandan keyin — bu "reliz"mi?</h3>
<p>8-darsda kod qanday <code>main</code>ga qo'shilishini ko'rdik. Lekin
"main'ga qo'shildi" va "reliz qilindi" — ikki xil narsa. Ko'p jamoalar
qachon "1.2.0" yoki "2.0.0" deb e'lon qilishni QANDAY hal qilishni
bilmaydi — bu tasodifiy raqam emas, <strong>Semantic Versioning
(SemVer)</strong> deb ataladigan qat'iy qoidalar to'plami orqali
hal qilinadi.</p>

<h3>MAJOR.MINOR.PATCH — uchta raqam, uchta ma'no</h3>
<p>Versiya <code>MAJOR.MINOR.PATCH</code> shaklida yoziladi (masalan
<code>1.2.3</code>), va har bir qism ANIQ narsani anglatadi:</p>
<ul>
<li><strong>MAJOR</strong> (birinchi raqam) — <strong>breaking
change</strong> (moslik buzuvchi o'zgarish): mavjud API/interfeys endi
oldingidek ishlamaydi. Masalan, endpoint javobining maydon nomi
o'zgartirilsa, eski nomga tayangan har qanday mijoz kodi buziladi.</li>
<li><strong>MINOR</strong> (ikkinchi raqam) — yangi FUNKSIYA qo'shildi,
lekin mavjud narsa BUZILMAYDI (backward-compatible). Masalan, yangi,
ixtiyoriy endpoint qo'shilishi.</li>
<li><strong>PATCH</strong> (uchinchi raqam) — bug tuzatish, hech qanday
yangi funksiya yo'q, hech narsa buzilmaydi. Masalan, e6c19f2'dagi
grading tuzatishi — bu xatti-harakatni "to'g'rilaydi", lekin API
shaklini o'zgartirmaydi.</li>
</ul>
<p>Qoida: agar <code>1.4.2</code>dan <code>1.5.0</code>ga o'tsangiz,
mijoz (boshqa dasturchi, boshqa xizmat) hech narsa buzilmasligiga
ISHONISHI mumkin. Agar <code>1.4.2</code>dan <code>2.0.0</code>ga
o'tsa, u o'z kodini tekshirib chiqishi SHART.</p>

<h3>Bu platformaning o'z holati — nomuvofiqlik ham real</h3>
<p>Ushbu repozitoriyaning <code>backend/.env</code> faylida
<code>APP_VERSION=1.0.0</code>, <code>frontend/package.json</code>da esa
<code>"version": "0.1.0"</code> yozilgan. Ikkalasi HAR XIL: backend
"1.0.0" — birinchi barqaror, jamoat uchun tayyor reliz deb e'lon qilingan
(MAJOR>=1); frontend "0.1.0" — SemVer qoidasiga ko'ra <code>0.y.z</code>
hali "boshlang'ich rivojlanish" bosqichini bildiradi, ya'ni API
(bu holda UI/komponent tuzilishi) HALI istalgan vaqtda tubdan
o'zgarishi mumkin, hatto MINOR versiyada ham. Bu — real loyihalarda
alohida komponentlar (backend/frontend) MUSTAQIL versiyalanishi
mumkinligini ko'rsatadi, lekin jamoa buni ANIQ bilishi kerak — aks
holda "frontend 0.1.0 versiyada" degan signal e'tiborsiz qoldiriladi.</p>

<h3>Har bir commit turi qaysi versiya bo'lagiga mos keladi</h3>
<p>2-darsda ko'rgan Conventional Commits turlari SemVer bilan
to'g'ridan-to'g'ri bog'lanadi: <code>fix</code> tipidagi commit'lar —
PATCH, <code>feat</code> tipidagi commit'lar — MINOR, va agar commit
tavsifida <code>BREAKING CHANGE:</code> footer'i bo'lsa (yoki
<code>feat!</code>/<code>fix!</code> kabi undov belgisi bilan) — MAJOR.
Bu bog'liqlik 10-darsda changelog'ni AVTOMATIK yaratish uchun asos
bo'ladi.</p>

<h3>Versiya qanday oshirilishini hal qiluvchi qaror daraxti</h3>
<pre class="mermaid">
flowchart TD
  Q1{"Mavjud API/interfeys
BUZILADIMI?"} -->|"ha"| MAJ["MAJOR++
(masalan 1.4.2 -> 2.0.0)"]
  Q1 -->|"yo'q"| Q2{"Yangi FUNKSIYA
qo'shildimi?"}
  Q2 -->|"ha"| MIN["MINOR++
(masalan 1.4.2 -> 1.5.0)"]
  Q2 -->|"yo'q"| Q3{"Faqat bug
tuzatildimi?"}
  Q3 -->|"ha"| PAT["PATCH++
(masalan 1.4.2 -> 1.4.3)"]
  style MAJ fill:#ffd6d6,stroke:#cc3333
  style MIN fill:#fff3cd,stroke:#d0a000
  style PAT fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma har bir versiya oshirilishi ORQASIDA aslida bitta savolga
javob borligini ko'rsatadi: "bu o'zgarish mijozni BUZADIMI?" Agar
javob "ha" bo'lsa — qolgan ikkita savol MUHIM emas, MAJOR baribir
oshadi.</p>

<h3>Pre-release va build metama'lumoti — to'liq SemVer spetsifikatsiyasi</h3>
<p>To'liq SemVer spetsifikatsiyasi yana ikkita ixtiyoriy qismni ham
belgilaydi: <strong>pre-release</strong> teg (masalan
<code>1.1.0-beta.1</code> — "1.1.0 hali TO'LIQ barqaror emas, sinov
bosqichida") va <strong>build metadata</strong> (masalan
<code>1.1.0+20260115</code> — qurilish haqida qo'shimcha ma'lumot,
versiya taqqoslashda E'TIBORGA OLINMAYDI). Amalda pre-release teglar
ayniqsa foydali: jamoa <code>1.1.0-beta.1</code>ni cheklangan
foydalanuvchilarga chiqarib, muammo bo'lmasa GINA <code>1.1.0</code>
sifatida to'liq reliz qiladi — bu 11-darsda ko'radigan reliz strategiyasi
bilan bevosita bog'liq.</p>

<h3>Nega bu commit konventsiyasi (2-dars) bilan bevosita bog'liq</h3>
<p>Agar commit xabarlari izchil <code>fix</code>/<code>feat</code>
turlaridan foydalansa, versiya raqamini QO'LDA o'ylab topish shart
emas — u avtomatik HISOBLANISHI mumkin (10-11-darslarda ko'ramiz). Bu —
2-darsda aytilgan "izchillik faqat chiroyli ko'rinish emas" degan
fikrning yana bir amaliy dalili.</p>
""".strip()

L9_TEXT_RU = """
<h3>После merge — это уже "релиз"?</h3>
<p>В уроке 8 мы увидели, как код попадает в <code>main</code>. Но
"добавлено в main" и "выпущен релиз" — разные вещи. Многие команды не
знают, КАК решить, когда объявлять "1.2.0" или "2.0.0" — это не
случайное число, а решается через строгий набор правил под названием
<strong>Semantic Versioning (SemVer)</strong>.</p>

<h3>MAJOR.MINOR.PATCH — три числа, три значения</h3>
<p>Версия пишется в формате <code>MAJOR.MINOR.PATCH</code> (например
<code>1.2.3</code>), и каждая часть означает ТОЧНО определённое:</p>
<ul>
<li><strong>MAJOR</strong> (первое число) — <strong>breaking
change</strong> (изменение, ломающее совместимость): существующий
API/интерфейс больше не работает как раньше. Например, если изменить
имя поля в ответе endpoint, любой клиентский код, зависящий от старого
имени, сломается.</li>
<li><strong>MINOR</strong> (второе число) — добавлена новая ФУНКЦИЯ, но
существующее НЕ ЛОМАЕТСЯ (обратно совместимо). Например, добавление
нового, необязательного endpoint.</li>
<li><strong>PATCH</strong> (третье число) — исправление бага, никакой
новой функции, ничего не ломается. Например, исправление grading в
e6c19f2 — оно "исправляет" поведение, но не меняет форму API.</li>
</ul>
<p>Правило: если вы переходите с <code>1.4.2</code> на
<code>1.5.0</code>, клиент (другой разработчик, другой сервис) может
БЫТЬ УВЕРЕН, что ничего не сломается. Если переход с <code>1.4.2</code>
на <code>2.0.0</code>, он ОБЯЗАН проверить свой код.</p>

<h3>Собственное состояние этой платформы — несоответствие тоже реально</h3>
<p>В файле <code>backend/.env</code> этого репозитория записано
<code>APP_VERSION=1.0.0</code>, а в <code>frontend/package.json</code> —
<code>"version": "0.1.0"</code>. Оба РАЗНЫЕ: backend "1.0.0" — объявлен
как первый стабильный, готовый к публичному использованию релиз
(MAJOR>=1); frontend "0.1.0" — по правилу SemVer <code>0.y.z</code>
означает стадию "начальной разработки", то есть API (в данном случае
структура UI/компонентов) ЕЩЁ может кардинально измениться в любой
момент, даже в MINOR-версии. Это показывает, что в реальных проектах
отдельные компоненты (backend/frontend) МОГУТ версионироваться
НЕЗАВИСИМО, но команда должна ЧЁТКО это понимать — иначе сигнал
"frontend на версии 0.1.0" остаётся незамеченным.</p>

<h3>Какой тип коммита соответствует какой части версии</h3>
<p>Типы Conventional Commits из урока 2 напрямую связаны с SemVer:
коммиты типа <code>fix</code> — это PATCH, коммиты типа <code>feat</code>
— это MINOR, а если в описании коммита есть footer <code>BREAKING
CHANGE:</code> (или восклицательный знак вроде <code>feat!</code>/
<code>fix!</code>) — это MAJOR. Эта связь станет основой для
АВТОМАТИЧЕСКОГО создания changelog в уроке 10.</p>

<h3>Дерево решений для повышения версии</h3>
<pre class="mermaid">
flowchart TD
  Q1{"Ломается ли существующий
API/интерфейс?"} -->|"да"| MAJ["MAJOR++
(например 1.4.2 -> 2.0.0)"]
  Q1 -->|"нет"| Q2{"Добавлена ли новая
ФУНКЦИЯ?"}
  Q2 -->|"да"| MIN["MINOR++
(например 1.4.2 -> 1.5.0)"]
  Q2 -->|"нет"| Q3{"Исправлен только
баг?"}
  Q3 -->|"да"| PAT["PATCH++
(например 1.4.2 -> 1.4.3)"]
  style MAJ fill:#ffd6d6,stroke:#cc3333
  style MIN fill:#fff3cd,stroke:#d0a000
  style PAT fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает, что за каждым повышением версии стоит один
вопрос: "ломает ли это изменение клиента?" Если ответ "да" — остальные
два вопроса НЕ ВАЖНЫ, MAJOR повышается в любом случае.</p>

<h3>Pre-release и метаданные сборки — полная спецификация SemVer</h3>
<p>Полная спецификация SemVer определяет ещё две необязательные части:
<strong>pre-release</strong> метку (например <code>1.1.0-beta.1</code>
— "1.1.0 ещё НЕ полностью стабилен, на стадии тестирования") и
<strong>метаданные сборки</strong> (например <code>1.1.0+20260115</code>
— дополнительная информация о сборке, НЕ учитывается при сравнении
версий). На практике pre-release метки особенно полезны: команда
выпускает <code>1.1.0-beta.1</code> для ограниченного круга
пользователей, и ТОЛЬКО если проблем нет, выпускает полный релиз
<code>1.1.0</code> — это напрямую связано со стратегией релиза, которую
увидим в уроке 11.</p>

<h3>Почему это напрямую связано с конвенцией коммитов (урок 2)</h3>
<p>Если сообщения коммитов последовательно используют типы
<code>fix</code>/<code>feat</code>, номер версии не нужно придумывать
ВРУЧНУЮ — он может быть вычислен АВТОМАТИЧЕСКИ (увидим в уроках 10-11).
Это — ещё одно практическое доказательство мысли из урока 2, что
"согласованность — не просто красивый вид".</p>
""".strip()

L9_CODE = """
# ============================================================
# SemVer qaror daraxtini kod sifatida - real o'zgarishlarga
# qo'llash
# ============================================================

from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, change_type: str) -> "Version":
        \"\"\"change_type: 'major' | 'minor' | 'patch'. Immutable - yangi
        Version qaytaradi, o'zini o'zgartirmaydi.\"\"\"
        if change_type == "major":
            return Version(self.major + 1, 0, 0)
        if change_type == "minor":
            return Version(self.major, self.minor + 1, 0)
        if change_type == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"noma'lum change_type: {change_type!r}")


def classify_change(breaks_api: bool, adds_feature: bool) -> str:
    \"\"\"9-darsdagi qaror daraxtining kod ko'rinishi.\"\"\"
    if breaks_api:
        return "major"
    if adds_feature:
        return "minor"
    return "patch"


# --- Bu platformaning haqiqiy holati (real fayllardan) ---
backend_version = Version(1, 0, 0)   # backend/.env: APP_VERSION=1.0.0
frontend_version = Version(0, 1, 0)  # frontend/package.json: "version": "0.1.0"
print(f"Backend: {backend_version} (barqaror reliz, MAJOR>=1)")
print(f"Frontend: {frontend_version} (0.y.z - hali boshlang'ich rivojlanish)")

# --- e6c19f2 kabi bug tuzatish qanday versiyaga ta'sir qiladi ---
change_type = classify_change(breaks_api=False, adds_feature=False)
new_version = backend_version.bump(change_type)
print(f"e6c19f2 (fix, API buzilmaydi) -> {change_type} -> {backend_version} -> {new_version}")
# e6c19f2 (fix, API buzilmaydi) -> patch -> 1.0.0 -> 1.0.1

# --- Agar endpoint javobi maydon nomi o'zgartirilsa (breaking) ---
change_type2 = classify_change(breaks_api=True, adds_feature=False)
new_version2 = backend_version.bump(change_type2)
print(f"Endpoint maydon nomi o'zgardi -> {change_type2} -> {backend_version} -> {new_version2}")
# Endpoint maydon nomi o'zgardi -> major -> 1.0.0 -> 2.0.0
""".strip()

L9_CODE_RU = """
# ============================================================
# Дерево решений SemVer как код - применение к реальным
# изменениям
# ============================================================

from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, change_type: str) -> "Version":
        \"\"\"change_type: 'major' | 'minor' | 'patch'. Иммутабельно -
        возвращает новый Version, себя не изменяет.\"\"\"
        if change_type == "major":
            return Version(self.major + 1, 0, 0)
        if change_type == "minor":
            return Version(self.major, self.minor + 1, 0)
        if change_type == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"неизвестный change_type: {change_type!r}")


def classify_change(breaks_api: bool, adds_feature: bool) -> str:
    \"\"\"Кодовое представление дерева решений из урока 9.\"\"\"
    if breaks_api:
        return "major"
    if adds_feature:
        return "minor"
    return "patch"


# --- Реальное состояние этой платформы (из настоящих файлов) ---
backend_version = Version(1, 0, 0)   # backend/.env: APP_VERSION=1.0.0
frontend_version = Version(0, 1, 0)  # frontend/package.json: "version": "0.1.0"
print(f"Backend: {backend_version} (стабильный релиз, MAJOR>=1)")
print(f"Frontend: {frontend_version} (0.y.z - ещё начальная разработка)")

# --- Как исправление бага вроде e6c19f2 влияет на версию ---
change_type = classify_change(breaks_api=False, adds_feature=False)
new_version = backend_version.bump(change_type)
print(f"e6c19f2 (fix, API не ломается) -> {change_type} -> {backend_version} -> {new_version}")
# e6c19f2 (fix, API не ломается) -> patch -> 1.0.0 -> 1.0.1

# --- Если изменится имя поля в ответе endpoint (breaking) ---
change_type2 = classify_change(breaks_api=True, adds_feature=False)
new_version2 = backend_version.bump(change_type2)
print(f"Имя поля endpoint изменилось -> {change_type2} -> {backend_version} -> {new_version2}")
# Имя поля endpoint изменилось -> major -> 1.0.0 -> 2.0.0
""".strip()

L9_TASK = {
    "task_title": "10 ta xayoliy o'zgarishni SemVer bo'yicha tasniflang",
    "task_title_ru": "Классифицируйте 10 условных изменений по SemVer",
    "task_description": (
        "10 ta turli xil o'zgarish tavsifi beriladi (masalan \"yangi "
        "/api/v1/reports endpoint qo'shildi\", \"login javobidagi 'token' "
        "maydoni 'access_token' deb o'zgartirildi\", \"xato xabaridagi "
        "yozuv xatosi tuzatildi\"). Har birini MAJOR/MINOR/PATCH sifatida "
        "tasniflang va 9-darsdagi qaror daraxtiga asoslanib sababini "
        "yozing."
    ),
    "task_description_ru": (
        "Дано 10 описаний разных изменений (например \"добавлен новый "
        "endpoint /api/v1/reports\", \"поле 'token' в ответе login "
        "переименовано в 'access_token'\", \"исправлена опечатка в "
        "сообщении об ошибке\"). Классифицируйте каждое как MAJOR/MINOR/"
        "PATCH и обоснуйте, опираясь на дерево решений из урока 9."
    ),
    "task_requirements": (
        "1) Barcha 10 ta o'zgarish uchun aniq MAJOR/MINOR/PATCH belgisi "
        "qo'yilgan bo'lishi shart. 2) Har bir belgilash uchun kamida bitta "
        "gap asos ko'rsatilishi kerak. 3) Kamida bittasi MAJOR, bittasi "
        "MINOR va bittasi PATCH bo'lishi kerak (aralash misollar)."
    ),
    "task_requirements_ru": (
        "1) Для всех 10 изменений должна быть чётко указана метка MAJOR/"
        "MINOR/PATCH. 2) Для каждой метки - минимум одно предложение "
        "обоснования. 3) Минимум одно должно быть MAJOR, одно MINOR и "
        "одно PATCH (смешанные примеры)."
    ),
    "task_technologies": "Semantic Versioning",
    "task_deadline_days": 3,
}

L9_SAMPLE = {
    "title": "Namuna: SemVer qaror daraxtini avtomatlashtiruvchi skript",
    "description": (
        "Ushbu darsning kod namunasi asosida, o'zgarish tavsifidan "
        "MAJOR/MINOR/PATCH'ni avtomatik hisoblab, yangi versiya raqamini "
        "chiqaruvchi to'liq ishlaydigan Python skripti."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "semver_bump.py",
            "language": "python",
            "code": (
                "from dataclasses import dataclass\n\n\n"
                "@dataclass(frozen=True)\n"
                "class Version:\n"
                "    major: int\n"
                "    minor: int\n"
                "    patch: int\n\n"
                "    def __str__(self):\n"
                "        return f\"{self.major}.{self.minor}.{self.patch}\"\n\n"
                "    @classmethod\n"
                "    def parse(cls, text: str) -> \"Version\":\n"
                "        major, minor, patch = (int(x) for x in text.split(\".\"))\n"
                "        return cls(major, minor, patch)\n\n"
                "    def bump(self, change_type: str) -> \"Version\":\n"
                "        if change_type == \"major\":\n"
                "            return Version(self.major + 1, 0, 0)\n"
                "        if change_type == \"minor\":\n"
                "            return Version(self.major, self.minor + 1, 0)\n"
                "        if change_type == \"patch\":\n"
                "            return Version(self.major, self.minor, self.patch + 1)\n"
                "        raise ValueError(change_type)\n\n\n"
                "def change_type_from_commit_type(commit_type: str, is_breaking: bool) -> str:\n"
                "    \"\"\"9-dars: fix->patch, feat->minor, BREAKING CHANGE->major.\"\"\"\n"
                "    if is_breaking:\n"
                "        return \"major\"\n"
                "    return {\"fix\": \"patch\", \"feat\": \"minor\"}.get(commit_type, \"patch\")\n\n\n"
                "if __name__ == \"__main__\":\n"
                "    current = Version.parse(\"1.0.0\")   # backend/.env APP_VERSION\n"
                "    for commit_type, is_breaking in [(\"fix\", False), (\"feat\", False), (\"feat\", True)]:\n"
                "        ct = change_type_from_commit_type(commit_type, is_breaking)\n"
                "        new_v = current.bump(ct)\n"
                "        print(f\"{commit_type}(breaking={is_breaking}) -> {ct} -> {current} => {new_v}\")\n"
            ),
        }
    ],
}

L9_EXERCISES = [
    {
        "title": "MAJOR versiya nimani anglatadi",
        "title_ru": "Что означает MAJOR-версия",
        "description": "SemVer'da MAJOR raqamining oshishi nimani anglatadi?",
        "description_ru": "Что означает повышение числа MAJOR в SemVer?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat kichik bug tuzatildi",
            "Yangi, backward-compatible funksiya qo'shildi",
            "Mavjud API/interfeys buziladigan (breaking) o'zgarish kiritildi",
            "Kod tozalandi, hech narsa o'zgarmadi",
        ],
        "options_ru": [
            "Исправлен только мелкий баг",
            "Добавлена новая, обратно совместимая функция",
            "Внесено ломающее совместимость (breaking) изменение существующего API",
            "Код почищен, ничего не изменилось",
        ],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Qaror daraxtidagi birinchi savolni eslang.",
        "hint_ru": "Вспомните первый вопрос дерева решений.",
        "explanation": "MAJOR faqat mavjud narsa BUZILGANDA oshadi - qolgan ikki savol (yangi funksiya, bug) bunda ahamiyatsiz.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Backend va frontend versiyasi",
        "title_ru": "Версии backend и frontend",
        "description": "Bu platformaning backend'i (.env) va frontend'i (package.json) haqiqiy versiyalari haqida qaysi gap TO'G'RI?",
        "description_ru": "Какое утверждение о РЕАЛЬНЫХ версиях backend'а (.env) и frontend'а (package.json) этой платформы ВЕРНО?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkalasi ham bir xil 1.0.0",
            "Backend 1.0.0 (barqaror), frontend 0.1.0 (boshlang'ich rivojlanish)",
            "Ikkalasi ham 0.1.0",
            "Bunday ma'lumot repozitoriyada mavjud emas",
        ],
        "options_ru": [
            "Оба одинаковые 1.0.0",
            "Backend 1.0.0 (стабильный), frontend 0.1.0 (начальная разработка)",
            "Оба 0.1.0",
            "Такой информации в репозитории нет",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsda aynan shu ikki real fayl (.env va package.json) keltirilgan.",
        "hint_ru": "В уроке приведены именно эти два реальных файла (.env и package.json).",
        "explanation": "backend/.env: APP_VERSION=1.0.0; frontend/package.json: \"version\": \"0.1.0\" - real, mos kelmaydigan holat.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Commit turini SemVer bo'lagiga moslashtiring",
        "title_ru": "Сопоставьте тип коммита с частью SemVer",
        "description": "Commit turlarini mos SemVer bo'lagi bilan mos tartibda joylang: fix -> feat -> BREAKING CHANGE.",
        "description_ru": "Расположите типы коммитов в порядке соответствия части SemVer: fix -> feat -> BREAKING CHANGE.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["fix (PATCH)", "feat (MINOR)", "BREAKING CHANGE (MAJOR)"],
        "drag_items_ru": ["fix (PATCH)", "feat (MINOR)", "BREAKING CHANGE (MAJOR)"],
        "correct_order": ["fix (PATCH)", "feat (MINOR)", "BREAKING CHANGE (MAJOR)"],
        "hint": "Eng kichik ta'sirdan eng kattasigacha tartiblang.",
        "hint_ru": "Расположите от наименьшего воздействия к наибольшему.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Frontend versiyasining ma'nosi",
        "title_ru": "Значение версии frontend",
        "description": "SemVer qoidasiga ko'ra, 0.y.z shaklidagi versiya (masalan frontend'ning 0.1.0) hali ___ bosqichida ekanini bildiradi.",
        "description_ru": "По правилу SemVer, версия вида 0.y.z (например 0.1.0 у frontend) означает, что проект ещё на стадии ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "boshlang'ich rivojlanish",
        "correct_answers_ru": "начальной разработки",
        "hint": "Darsda \"MAJOR=0\" holati alohida tushuntirilgan.",
        "hint_ru": "В уроке отдельно объяснено состояние \"MAJOR=0\".",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 10 — Changelog yuritish: qo'lda va Conventional Commits'dan
# avtomatik
# ---------------------------------------------------------------------------

L10_TEXT = """
<h3>Versiya raqami yetarli emas — "nima o'zgardi" qayerda yozilgan</h3>
<p>9-darsda <code>1.0.0</code>dan <code>1.1.0</code>ga o'tish nimani
anglatishini (yangi funksiya) o'rgandik. Lekin foydalanuvchi yoki
jamoadosh "aniq NIMA qo'shildi" deb bilishni xohlasa, versiya raqamining
o'zi javob bermaydi — <strong>CHANGELOG</strong> (o'zgarishlar jurnali)
kerak: har bir versiya uchun NIMA o'zgarganini ro'yxatlaydigan alohida
fayl (odatda <code>CHANGELOG.md</code>).</p>

<h3>Muhim eslatma: bu repozitoriyada hali CHANGELOG.md yo'q</h3>
<p>Boshqa darslarda aytilganidek, bu repozitoriyada CODEOWNERS va PR
shabloni yo'q edi; xuddi shunday — CHANGELOG.md fayli ham, reliz
teglari ham hozircha yo'q (11-darsda buni ko'ramiz). Bu dars shu
sababli "mavjud CHANGELOG'ni o'qish" emas, balki "shu repozitoriyaga
O'XSHASH loyihaga CHANGELOG QANDAY QILIB kiritilishi mumkin"ni
o'rgatadi — real, hali qo'llanilmagan amaliyot sifatida.</p>

<h3>"Keep a Changelog" formati</h3>
<p>Eng ko'p qo'llaniladigan konventsiya — har bir versiya uchun
o'zgarishlarni toifalarga ajratish: <strong>Added</strong> (qo'shildi),
<strong>Changed</strong> (o'zgartirildi), <strong>Fixed</strong>
(tuzatildi), <strong>Removed</strong> (olib tashlandi),
<strong>Security</strong> (xavfsizlik). Har bir versiya sarlavhasi
sana va versiya raqami bilan boshlanadi.</p>

<h3>Qo'lda yozishning muammosi — va avtomatlashtirish yechimi</h3>
<p>Agar changelog QO'LDA yozilsa, u ko'pincha UNUTILADI — dasturchi
kodni yozadi, commit qiladi, lekin "buni changelog'ga ham yozish
kerak edi" degan qo'shimcha qadamni tez-tez o'tkazib yuboradi. Yechim:
agar commit xabarlari 2-darsdagi Conventional Commits formatiga QAT'IY
rioya qilsa, changelog'ni <code>git log</code>dan AVTOMATIK generatsiya
qilish mumkin — <code>fix</code> turidagi commit'lar "Fixed" bo'limiga,
<code>feat</code> turidagilar "Added" bo'limiga avtomatik joylashadi.
Bu — <code>conventional-changelog</code>, <code>git-cliff</code> kabi
vositalar qiladigan aynan shu ish.</p>

<h3>Bu platformaning real commit'laridan changelog qurish</h3>
<p>Quyidagi kod namunasida 2-darsda ko'rgan haqiqiy commit'lar
(<code>feat(scripts): add reusable course_builder library</code>,
<code>fix(lessons): make in-lesson exercise hydration
language-aware</code>, <code>chore(scripts): add exercise-integrity and
course-image checkers</code>, <code>fix(points): stop permanently
inflating lifetime_points/leaderboard on reversal</code>) AVTOMATIK
ravishda "Added"/"Fixed" bo'limlariga guruhlangan holda ko'rasiz —
qo'lda hech narsa qayta yozilmagan, faqat commit TURI o'qilgan.</p>

<h3>Commit turidan changelog bo'limigacha</h3>
<pre class="mermaid">
flowchart LR
  F1["feat(scripts): add
course_builder library"] --> ADD["## Added"]
  F2["fix(lessons): make hydration
language-aware"] --> FIX["## Fixed"]
  F3["fix(points): stop inflating
lifetime_points"] --> FIX
  C1["chore(scripts): add
integrity checkers"] --> SKIP["Changelog'ga
odatda kiritilmaydi
(foydalanuvchiga ko'rinmaydi)"]
  ADD --> CL["CHANGELOG.md
## v1.1.0 - 2026-01-15"]
  FIX --> CL
  style ADD fill:#d6f5d6,stroke:#2a8a2a
  style FIX fill:#ffe9b3,stroke:#d09000
  style SKIP fill:#eeeeee,stroke:#888888
</pre>
<p>Diagramma shuni ko'rsatadiki, HAR bir commit turi changelog'ga
kiritilavermaydi — <code>chore</code> kabi ICHKI, foydalanuvchiga
ko'rinmaydigan o'zgarishlar (masalan tekshiruv skriptlari qo'shish)
odatda changelog'dan chiqarib tashlanadi, chunki changelog FOYDALANUVCHI
uchun yozilgan, dasturchi uchun emas (bu farq <code>git log</code> bilan
<code>CHANGELOG.md</code> orasidagi asosiy farq).</p>

<h3>"Unreleased" bo'limi — hali reliz qilinmagan o'zgarishlar uchun</h3>
<p>"Keep a Changelog" konventsiyasining yana bir muhim qismi —
<code>## [Unreleased]</code> sarlavhasi: fayl eng yuqorisida turadi va
hali RELIZ qilinmagan (11-darsda ko'radigan tag hali qo'yilmagan), lekin
<code>main</code>ga allaqachon merge qilingan o'zgarishlarni to'playdi.
Yangi reliz chiqarilganda, <code>Unreleased</code> ostidagi barcha
yozuvlar yangi versiya sarlavhasi (masalan <code>## [1.1.0] -
2026-01-15</code>) ostiga "ko'chiriladi", va <code>Unreleased</code>
bo'limi bo'shab, keyingi reliz uchun tayyor holatda qoladi. Bu — 8-darsda
ko'rgan "merge qilingan, lekin hali reliz qilinmagan" holatni changelog
darajasida aks ettiruvchi mexanizm.</p>

<h3>Nega bu 2 va 9-darslar bilan bevosita bog'liq</h3>
<p>Changelog avtomatlashtirish FAQAT commit xabarlari izchil bo'lgandagina
ishlaydi (2-dars) — agar bitta commit "fix stuff" deb yozilgan bo'lsa,
avtomatik vosita uni HECH QAYSI bo'limga qo'yolmaydi. Xuddi shu tarzda,
changelog versiyalari 9-darsdagi SemVer raqamlariga to'g'ridan-to'g'ri
mos keladi — <code>## [1.1.0]</code> sarlavhasi FAQAT shu versiyaga
MINOR sifatida kelgan o'zgarishlarni o'z ichiga oladi.</p>
""".strip()

L10_TEXT_RU = """
<h3>Номера версии недостаточно — где написано "что изменилось"</h3>
<p>В уроке 9 мы узнали, что значит переход с <code>1.0.0</code> на
<code>1.1.0</code> (новая функция). Но если пользователь или коллега
хочет знать, ЧТО именно добавлено, сам номер версии не отвечает — нужен
<strong>CHANGELOG</strong> (журнал изменений): отдельный файл (обычно
<code>CHANGELOG.md</code>), перечисляющий, ЧТО изменилось для каждой
версии.</p>

<h3>Важное замечание: в этом репозитории пока нет CHANGELOG.md</h3>
<p>Как говорилось в других уроках, в этом репозитории нет CODEOWNERS и
шаблона PR; так же — нет и файла CHANGELOG.md, ни тегов релизов (увидим
в уроке 11). Поэтому этот урок учит не "чтению существующего
CHANGELOG", а тому, КАК можно ВНЕДРИТЬ changelog в проект, похожий на
этот — как реальную, ещё не применённую практику.</p>

<h3>Формат "Keep a Changelog"</h3>
<p>Самая распространённая конвенция — делить изменения каждой версии по
категориям: <strong>Added</strong> (добавлено), <strong>Changed</strong>
(изменено), <strong>Fixed</strong> (исправлено), <strong>Removed</strong>
(удалено), <strong>Security</strong> (безопасность). Заголовок каждой
версии начинается с даты и номера версии.</p>

<h3>Проблема ручного ведения — и решение через автоматизацию</h3>
<p>Если changelog пишется ВРУЧНУЮ, его часто ЗАБЫВАЮТ — разработчик
пишет код, коммитит, но часто пропускает дополнительный шаг "это нужно
было записать и в changelog". Решение: если сообщения коммитов СТРОГО
следуют формату Conventional Commits из урока 2, changelog можно
АВТОМАТИЧЕСКИ сгенерировать из <code>git log</code> — коммиты типа
<code>fix</code> автоматически попадают в раздел "Fixed", типа
<code>feat</code> — в раздел "Added". Именно это делают инструменты
вроде <code>conventional-changelog</code>, <code>git-cliff</code>.</p>

<h3>Построение changelog из реальных коммитов этой платформы</h3>
<p>В примере кода ниже вы увидите реальные коммиты из урока 2
(<code>feat(scripts): add reusable course_builder library</code>,
<code>fix(lessons): make in-lesson exercise hydration
language-aware</code>, <code>chore(scripts): add exercise-integrity and
course-image checkers</code>, <code>fix(points): stop permanently
inflating lifetime_points/leaderboard on reversal</code>), АВТОМАТИЧЕСКИ
сгруппированные по разделам "Added"/"Fixed" — вручную ничего не
переписано, прочитан только ТИП коммита.</p>

<h3>От типа коммита до раздела changelog</h3>
<pre class="mermaid">
flowchart LR
  F1["feat(scripts): add
course_builder library"] --> ADD["## Added"]
  F2["fix(lessons): make hydration
language-aware"] --> FIX["## Fixed"]
  F3["fix(points): stop inflating
lifetime_points"] --> FIX
  C1["chore(scripts): add
integrity checkers"] --> SKIP["Обычно не входит
в changelog
(не видно пользователю)"]
  ADD --> CL["CHANGELOG.md
## v1.1.0 - 2026-01-15"]
  FIX --> CL
  style ADD fill:#d6f5d6,stroke:#2a8a2a
  style FIX fill:#ffe9b3,stroke:#d09000
  style SKIP fill:#eeeeee,stroke:#888888
</pre>
<p>Диаграмма показывает, что НЕ каждый тип коммита попадает в changelog
— внутренние, невидимые пользователю изменения вроде <code>chore</code>
(например добавление скриптов проверки) обычно исключаются из
changelog, потому что changelog пишется для ПОЛЬЗОВАТЕЛЯ, а не для
разработчика (это ключевое отличие <code>git log</code> от
<code>CHANGELOG.md</code>).</p>

<h3>Раздел "Unreleased" — для ещё не выпущенных изменений</h3>
<p>Ещё одна важная часть конвенции "Keep a Changelog" — заголовок
<code>## [Unreleased]</code>: он находится в самом верху файла и
собирает изменения, которые уже смёржены в <code>main</code>, но ещё НЕ
выпущены релизом (тег из урока 11 ещё не поставлен). Когда выходит новый
релиз, все записи под <code>Unreleased</code> "переносятся" под новый
заголовок версии (например <code>## [1.1.0] - 2026-01-15</code>), а
раздел <code>Unreleased</code> становится пустым и готовым для
следующего релиза. Это — механизм, отражающий на уровне changelog
состояние "смёржено, но ещё не выпущено", которое мы видели в уроке 8.</p>

<h3>Почему это напрямую связано с уроками 2 и 9</h3>
<p>Автоматизация changelog работает ТОЛЬКО если сообщения коммитов
согласованы (урок 2) — если один коммит написан как "fix stuff",
автоматический инструмент не сможет отнести его НИ К ОДНОМУ разделу.
Точно так же версии changelog напрямую соответствуют номерам SemVer из
урока 9 — заголовок <code>## [1.1.0]</code> включает ТОЛЬКО изменения,
пришедшие как MINOR для этой версии.</p>
""".strip()

L10_CODE = """
# ============================================================
# Bu platformaning REAL commit'laridan changelog'ni avtomatik
# generatsiya qilish
# ============================================================

REAL_COMMITS = [
    "feat(scripts): add reusable course_builder library + generic scripts",
    "fix(lessons): make in-lesson exercise hydration language-aware",
    "chore(scripts): add exercise-integrity and course-image checkers",
    "fix(points): stop permanently inflating lifetime_points/leaderboard on reversal",
    "docs(readme): clarify local setup steps",  # ta'lim uchun qo'shilgan misol
]

SECTION_BY_TYPE = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": None,   # foydalanuvchiga ko'rinmaydigan hisoblanadi - o'chirib tashlanadi
    "chore": None,  # ichki infratuzilma - changelog'ga kirmaydi
    "refactor": None,
}


def parse_commit(msg: str) -> tuple[str, str, str]:
    \"\"\"'type(scope): description' -> (type, scope, description).\"\"\"
    head, _, description = msg.partition(": ")
    if "(" in head:
        commit_type, scope = head.split("(", 1)
        scope = scope.rstrip(")")
    else:
        commit_type, scope = head, ""
    return commit_type, scope, description


def build_changelog(commits: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    for msg in commits:
        commit_type, scope, description = parse_commit(msg)
        section = SECTION_BY_TYPE.get(commit_type)
        if section is None:
            continue  # foydalanuvchiga ko'rinmaydigan turdagi o'zgarish
        sections.setdefault(section, []).append(f"{description} ({scope})" if scope else description)
    return sections


changelog = build_changelog(REAL_COMMITS)
print("## [1.1.0] - 2026-01-15\\n")
for section in ("Added", "Changed", "Fixed", "Removed", "Security"):
    if section in changelog:
        print(f"### {section}")
        for item in changelog[section]:
            print(f"- {item}")
        print()

# Natija:
# ## [1.1.0] - 2026-01-15
#
# ### Added
# - add reusable course_builder library + generic scripts (scripts)
#
# ### Fixed
# - make in-lesson exercise hydration language-aware (lessons)
# - stop permanently inflating lifetime_points/leaderboard on reversal (points)
#
# (chore va docs commit'lari - foydalanuvchi uchun ahamiyatsiz - kiritilmadi)
""".strip()

L10_CODE_RU = """
# ============================================================
# Автоматическая генерация changelog из РЕАЛЬНЫХ коммитов этой
# платформы
# ============================================================

REAL_COMMITS = [
    "feat(scripts): add reusable course_builder library + generic scripts",
    "fix(lessons): make in-lesson exercise hydration language-aware",
    "chore(scripts): add exercise-integrity and course-image checkers",
    "fix(points): stop permanently inflating lifetime_points/leaderboard on reversal",
    "docs(readme): clarify local setup steps",  # добавлен учебный пример
]

SECTION_BY_TYPE = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": None,   # считается невидимым пользователю - убирается
    "chore": None,  # внутренняя инфраструктура - не входит в changelog
    "refactor": None,
}


def parse_commit(msg: str) -> tuple[str, str, str]:
    \"\"\"'type(scope): description' -> (type, scope, description).\"\"\"
    head, _, description = msg.partition(": ")
    if "(" in head:
        commit_type, scope = head.split("(", 1)
        scope = scope.rstrip(")")
    else:
        commit_type, scope = head, ""
    return commit_type, scope, description


def build_changelog(commits: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    for msg in commits:
        commit_type, scope, description = parse_commit(msg)
        section = SECTION_BY_TYPE.get(commit_type)
        if section is None:
            continue  # изменение типа, невидимого пользователю
        sections.setdefault(section, []).append(f"{description} ({scope})" if scope else description)
    return sections


changelog = build_changelog(REAL_COMMITS)
print("## [1.1.0] - 2026-01-15\\n")
for section in ("Added", "Changed", "Fixed", "Removed", "Security"):
    if section in changelog:
        print(f"### {section}")
        for item in changelog[section]:
            print(f"- {item}")
        print()

# Результат:
# ## [1.1.0] - 2026-01-15
#
# ### Added
# - add reusable course_builder library + generic scripts (scripts)
#
# ### Fixed
# - make in-lesson exercise hydration language-aware (lessons)
# - stop permanently inflating lifetime_points/leaderboard on reversal (points)
#
# (коммиты chore и docs - не важны для пользователя - не включены)
""".strip()

L10_TASK = {
    "task_title": "O'z loyihangiz uchun CHANGELOG.md yarating",
    "task_title_ru": "Создайте CHANGELOG.md для своего проекта",
    "task_description": (
        "Shaxsiy loyihangizning (yoki shu platforma fork'ining) so'nggi "
        "10-15 ta commit xabarini oling. Ularni ushbu darsdagi skript "
        "mantig'iga o'xshab qo'lda tahlil qiling: fix->Fixed, feat->Added, "
        "boshqalar (chore/docs/refactor)->o'tkazib yuborilsin. Natijada "
        "\"Keep a Changelog\" formatidagi bitta CHANGELOG.md bo'limi "
        "yozing."
    ),
    "task_description_ru": (
        "Возьмите последние 10-15 сообщений коммитов своего проекта (или "
        "форка этой платформы). Проанализируйте их вручную по логике "
        "скрипта из этого урока: fix->Fixed, feat->Added, остальные "
        "(chore/docs/refactor)->пропустить. В результате напишите один "
        "раздел CHANGELOG.md в формате \"Keep a Changelog\"."
    ),
    "task_requirements": (
        "1) CHANGELOG bo'limi versiya raqami va sana bilan boshlanishi "
        "kerak. 2) Kamida ikkita bo'lim (masalan Added va Fixed) bo'lishi "
        "shart. 3) chore/docs turidagi commit'lar CHANGELOG'ga "
        "KIRITILMAGANLIGI aniq ko'rsatilishi kerak (masalan izoh sifatida)."
    ),
    "task_requirements_ru": (
        "1) Раздел CHANGELOG должен начинаться с номера версии и даты. "
        "2) Должно быть минимум два раздела (например Added и Fixed). 3) "
        "Должно быть чётко показано (например комментарием), что коммиты "
        "типа chore/docs НЕ включены в CHANGELOG."
    ),
    "task_technologies": "Markdown, Conventional Commits",
    "task_deadline_days": 4,
}

L10_SAMPLE = {
    "title": "Namuna: real commit'lardan CHANGELOG.md generatsiya qilish skripti",
    "description": (
        "Ushbu darsning kod namunasi asosida, bu platformaning haqiqiy "
        "commit xabarlaridan to'liq \"Keep a Changelog\" formatidagi "
        "bo'lim yaratuvchi ishlaydigan Python skripti."
    ),
    "sample_type": "python",
    "code_files": [
        {"filename": "generate_changelog.py", "language": "python", "code": "# Qarang: L10_CODE ushbu darsning to'liq matnida"},
    ],
}

L10_EXERCISES = [
    {
        "title": "Changelog kimga mo'ljallangan",
        "title_ru": "Для кого предназначен changelog",
        "description": "CHANGELOG.md asosan KIM uchun yoziladi?",
        "description_ru": "Для КОГО в первую очередь пишется CHANGELOG.md?",
        "exercise_type": "multiple_choice",
        "options": ["Faqat dasturchilar uchun", "Foydalanuvchi/mijoz uchun", "Faqat CI tizimi uchun", "Faqat huquqiy hujjatlar uchun"],
        "options_ru": ["Только для разработчиков", "Для пользователя/клиента", "Только для системы CI", "Только для юридических документов"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsdagi diagrammada chore commit'i nima uchun o'tkazib yuborilganini eslang.",
        "hint_ru": "Вспомните из диаграммы урока, почему коммит chore пропускается.",
        "explanation": "Changelog FOYDALANUVCHI uchun yoziladi - shu sababli ichki (chore) o'zgarishlar odatda kiritilmaydi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Qaysi commit turi changelog'dan chiqarib tashlanadi",
        "title_ru": "Какой тип коммита исключается из changelog",
        "description": "Darsdagi misolga ko'ra, qaysi commit turi odatda CHANGELOG.md'ga KIRITILMAYDI?",
        "description_ru": "Согласно примеру урока, какой тип коммита обычно НЕ ВКЛЮЧАЕТСЯ в CHANGELOG.md?",
        "exercise_type": "multiple_choice",
        "options": ["feat", "fix", "chore", "Hammasi kiritiladi"],
        "options_ru": ["feat", "fix", "chore", "Всё включается"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Diagrammadagi kulrang \"SKIP\" qutisini eslang.",
        "hint_ru": "Вспомните серый блок \"SKIP\" на диаграмме.",
        "explanation": "chore - ichki infratuzilma o'zgarishi, foydalanuvchiga ko'rinmaydi, shu sababli changelog'dan chiqarib tashlanadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Commit turini changelog bo'limiga moslashtiring",
        "title_ru": "Сопоставьте тип коммита с разделом changelog",
        "description": "Commit turlarini mos changelog bo'limi bilan mos tartibda joylang: feat -> fix.",
        "description_ru": "Расположите типы коммитов в порядке соответствия разделу changelog: feat -> fix.",
        "exercise_type": "drag_and_drop",
        "drag_items": ["feat -> Added", "fix -> Fixed"],
        "drag_items_ru": ["feat -> Added", "fix -> Fixed"],
        "correct_order": ["feat -> Added", "fix -> Fixed"],
        "hint": "Darsdagi SECTION_BY_TYPE lug'atini eslang.",
        "hint_ru": "Вспомните словарь SECTION_BY_TYPE из урока.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Changelog formatining nomi",
        "title_ru": "Название формата changelog",
        "description": "Darsda ko'rilgan, Added/Changed/Fixed/Removed/Security bo'limlaridan foydalanadigan keng tarqalgan konventsiya \"Keep a ___\" deb ataladi.",
        "description_ru": "Широко распространённая конвенция с разделами Added/Changed/Fixed/Removed/Security, рассмотренная в уроке, называется \"Keep a ___\".",
        "exercise_type": "fill_in_blank",
        "correct_answers": "Changelog",  # literal format/convention name, no natural-language RU translation needed
        "hint": "Darsning nomidagi asosiy atama.",
        "hint_ru": "Основной термин из названия урока.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 11 — Reliz teglash strategiyasi: semver teglar + CI/CD trigger
# ---------------------------------------------------------------------------

L11_TEXT = """
<h3>Versiya raqami + changelog + hali bitta bo'g'in yetishmaydi</h3>
<p>9-darsda versiya raqamini, 10-darsda changelog'ni ko'rdik. Lekin
"biz 1.1.0'ni chiqardik" degan gap qanday ANIQ, tekshiriladigan
voqeaga aylanadi? Javob — <strong>Git tag</strong>: tarixdagi ANIQ bitta
commit'ga doimiy, o'zgarmas nom beriladigan belgi. 112-kursda tag
obyektining ICHKI tuzilishini (annotated tag — o'ziga xos SHA-1'ga ega
to'liq obyekt) o'rgangansiz; bu darsda uni RELIZ STRATEGIYASI sifatida
ko'ramiz.</p>

<h3>Annotated vs lightweight tag — qaysi biri reliz uchun</h3>
<p>112-kursni eslatib o'tamiz: <strong>lightweight tag</strong> — shunchaki
commit'ga ishora qiluvchi belgi (metama'lumotsiz), <strong>annotated
tag</strong> esa — muallif, sana, xabar va (ixtiyoriy) GPG imzoga ega
TO'LIQ Git obyekti. Reliz uchun DOIM annotated tag ishlatilishi kerak —
u kim, qachon va NEGA shu versiyani chiqarganini saqlaydi, bu esa
audit va ishonch uchun muhim.</p>

<h3>v-prefiksli SemVer teglar — konventsiya</h3>
<p>Amaliyotda reliz teglari deyarli har doim <code>v</code> prefiksi
bilan yoziladi: <code>v1.2.0</code>, <code>v2.0.0</code> — bu SemVer
raqamini (9-dars) boshqa teglardan (masalan xususiyat belgilari) vizual
ajratib turadi. Buyruq:</p>
<pre><code>git tag -a v1.1.0 -m "Release 1.1.0: course_builder library + RU coverage fixes"
git push origin v1.1.0</code></pre>

<h3>Bu repozitoriyaning haqiqiy holati: hali teglar yo'q</h3>
<p><code>git tag</code> buyrug'i bu repozitoriyada BO'SH natija
qaytaradi — hozircha birorta ham reliz teglanmagan. Bu — 10-darsda
CHANGELOG.md yo'qligi kabi, real, kutilgan holat: kichik/yakka
loyihalarda ko'pincha versiyalash amaliyoti hali joriy qilinmaydi. Bu
dars aynan shu loyihaga qanday QILIB teglash strategiyasini kiritish
mumkinligini ko'rsatadi.</p>

<h3>Tegni deploy trigger'iga bog'lash — 117-kursning davomi</h3>
<p>117-kurs capstone darsida (13-dars) siz <code>on: push: tags:
['v*.*.*']</code> konsepsiyasini ko'rgansiz — bu HAR bir push'da emas,
FAQAT semver tegi push qilinganda ishga tushadigan deploy workflow'i.
Bu platformaning haqiqiy <code>deploy-backend.yml</code>/
<code>deploy-frontend.yml</code> fayllari hozircha <code>server</code>
branch'iga HAR push'da ishga tushadi — bu "har bir commit deploy
qilinadi" strategiyasi. Muqobil, tegga asoslangan strategiya:
"faqat ANIQ belgilangan reliz nuqtalarida deploy qilish" — bu jamoaga
KO'PROQ nazorat beradi (masalan bir nechta PR'ni birlashtirib, BITTA
tekshirilgan tegda deploy qilish), lekin tezlikni kamaytiradi (har bir
kichik tuzatish darhol production'ga tushmaydi).</p>

<h3>Toʻliq reliz pipeline'i — commit'dan deploygacha</h3>
<pre class="mermaid">
flowchart TB
  M["PR merge qilindi
(8-dars: merge strategiyasi)"] --> V["Versiya turi aniqlanadi
(9-dars: fix/feat/breaking)"]
  V --> CL["CHANGELOG.md yangilanadi
(10-dars: Added/Fixed)"]
  CL --> TAG["git tag -a v1.1.0
(annotated, imzolangan)"]
  TAG --> PUSH["git push origin v1.1.0"]
  PUSH --> CI["CI: on push tags v*.*.*
(117-kurs workflow'i)"]
  CI --> DEPLOY["Production'ga deploy"]
  style TAG fill:#d6e9ff,stroke:#2266aa
  style CI fill:#ffe9b3,stroke:#d09000
  style DEPLOY fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma BUTUN reliz zanjirini ko'rsatadi: merge (8-dars) ->
versiya turi (9-dars) -> changelog (10-dars) -> annotated tag -> push
-> CI trigger (117-kurs) -> deploy. Har bir bosqich oldingi darsning
bevosita davomi.</p>

<h3>GitHub Releases — tegni ko'rinadigan sahifaga aylantirish</h3>
<p>Tag push qilingandan keyin, GitHub'ning "Releases" bo'limida shu tag
asosida RASMIY reliz sahifasi yaratish mumkin (qo'lda yoki
<code>gh release create v1.1.0</code> orqali). GitHub'ning "Generate
release notes" tugmasi esa aynan 10-darsda ko'rgan g'oyani avtomatlashtiradi
— oxirgi tegdan beri qo'shilgan PR'larni o'qib, ularning sarlavhalaridan
(ko'pincha Conventional Commits formatidagi) tayyor reliz eslatmasini
yaratadi. Bu — CHANGELOG.md'ning muqobili emas, balki uni TO'LDIRUVCHI,
GitHub UI'sida ko'rinadigan qatlam.</p>

<h3>Nega bu zanjirning HAR bir bo'g'ini muhim</h3>
<p>Agar commit'lar izchil bo'lmasa (2-dars) — versiya turini avtomatik
aniqlab bo'lmaydi. Agar versiya noto'g'ri hisoblansa (9-dars) —
changelog noto'g'ri bo'limga yoziladi. Agar tag lightweight bo'lsa —
kim, qachon, NEGA relizni chiqarganini keyinchalik bilib bo'lmaydi.
Agar CI faqat push'ga, tegga emas, bog'langan bo'lsa — "reliz" tushunchasi
umuman yo'qoladi, chunki har bir commit "reliz" hisoblanadi.</p>
""".strip()

L11_TEXT_RU = """
<h3>Номер версии + changelog + ещё одно недостающее звено</h3>
<p>В уроке 9 мы увидели номер версии, в уроке 10 — changelog. Но как
фраза "мы выпустили 1.1.0" становится КОНКРЕТНЫМ, проверяемым событием?
Ответ — <strong>Git tag</strong>: постоянная, неизменная метка,
присваиваемая ОДНОМУ конкретному коммиту в истории. В курсе 112 вы
изучили ВНУТРЕННЕЕ устройство объекта тега (annotated tag — полноценный
объект с собственным SHA-1); в этом уроке рассмотрим его как СТРАТЕГИЮ
РЕЛИЗА.</p>

<h3>Annotated vs lightweight tag — какой для релиза</h3>
<p>Напомним из курса 112: <strong>lightweight tag</strong> — просто
метка, указывающая на коммит (без метаданных), <strong>annotated
tag</strong> — ПОЛНОЦЕННЫЙ объект Git с автором, датой, сообщением и
(опционально) GPG-подписью. Для релиза ВСЕГДА следует использовать
annotated tag — он сохраняет, кто, когда и ПОЧЕМУ выпустил именно эту
версию, что важно для аудита и доверия.</p>

<h3>Теги SemVer с префиксом v — конвенция</h3>
<p>На практике теги релизов почти всегда пишутся с префиксом
<code>v</code>: <code>v1.2.0</code>, <code>v2.0.0</code> — это визуально
отличает номер SemVer (урок 9) от других тегов (например меток
функций). Команда:</p>
<pre><code>git tag -a v1.1.0 -m "Release 1.1.0: course_builder library + RU coverage fixes"
git push origin v1.1.0</code></pre>

<h3>Реальное состояние этого репозитория: тегов пока нет</h3>
<p>Команда <code>git tag</code> в этом репозитории возвращает ПУСТОЙ
результат — пока не помечен ни один релиз. Это — как отсутствие
CHANGELOG.md в уроке 10, реальное, ожидаемое состояние: в маленьких/
сольных проектах практика версионирования часто ещё не внедрена. Этот
урок показывает, КАК можно ВНЕДРИТЬ стратегию тегирования именно в
такой проект.</p>

<h3>Привязка тега к триггеру деплоя — продолжение курса 117</h3>
<p>В капстоуне курса 117 (урок 13) вы видели концепцию <code>on: push:
tags: ['v*.*.*']</code> — это workflow деплоя, который запускается НЕ
при каждом push, а ТОЛЬКО при push semver-тега. Реальные
<code>deploy-backend.yml</code>/<code>deploy-frontend.yml</code> этой
платформы сейчас запускаются при КАЖДОМ push в ветку <code>server</code>
— это стратегия "деплоится каждый коммит". Альтернативная,
основанная на тегах стратегия: "деплоить только в чётко обозначенных
точках релиза" — это даёт команде БОЛЬШЕ контроля (например, объединить
несколько PR и деплоить ОДНИМ проверенным тегом), но снижает скорость
(мелкое исправление не попадает в продакшен сразу).</p>

<h3>Полный pipeline релиза — от коммита до деплоя</h3>
<pre class="mermaid">
flowchart TB
  M["PR смёржен
(урок 8: стратегия merge)"] --> V["Определяется тип версии
(урок 9: fix/feat/breaking)"]
  V --> CL["Обновляется CHANGELOG.md
(урок 10: Added/Fixed)"]
  CL --> TAG["git tag -a v1.1.0
(annotated, подписанный)"]
  TAG --> PUSH["git push origin v1.1.0"]
  PUSH --> CI["CI: on push tags v*.*.*
(workflow курса 117)"]
  CI --> DEPLOY["Деплой в продакшен"]
  style TAG fill:#d6e9ff,stroke:#2266aa
  style CI fill:#ffe9b3,stroke:#d09000
  style DEPLOY fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает ВЕСЬ цепочку релиза: merge (урок 8) -> тип
версии (урок 9) -> changelog (урок 10) -> annotated tag -> push -> CI
триггер (курс 117) -> деплой. Каждый этап — прямое продолжение
предыдущего урока.</p>

<h3>GitHub Releases — превращение тега в видимую страницу</h3>
<p>После push тега в разделе "Releases" GitHub можно создать
ОФИЦИАЛЬНУЮ страницу релиза на основе этого тега (вручную или через
<code>gh release create v1.1.0</code>). Кнопка "Generate release notes"
автоматизирует именно ту идею, что мы видели в уроке 10 — читает PR,
добавленные с прошлого тега, и создаёт готовые заметки о релизе из их
заголовков (часто в формате Conventional Commits). Это не замена
CHANGELOG.md, а ДОПОЛНЯЮЩИЙ его слой, видимый в интерфейсе GitHub.</p>

<h3>Почему важно КАЖДОЕ звено этой цепочки</h3>
<p>Если коммиты не согласованы (урок 2) — тип версии нельзя определить
автоматически. Если версия вычислена неверно (урок 9) — changelog
запишется в неверный раздел. Если тег lightweight — впоследствии
невозможно узнать, кто, когда и ПОЧЕМУ выпустил релиз. Если CI привязан
только к push, а не к тегу — понятие "релиз" вообще исчезает, потому
что каждый коммит считается "релизом".</p>
""".strip()

L11_CODE = """
# ============================================================
# Reliz teglash - annotated tag va tegga bog'langan CI trigger
# ============================================================

# --- 1) Annotated tag yaratish (112-kursda ko'rgan -a flag) ---
# $ git tag -a v1.1.0 -m "Release 1.1.0: course_builder library + RU coverage fixes"
#
# Solishtirish uchun - lightweight tag (reliz uchun TAVSIYA ETILMAYDI):
# $ git tag v1.1.0-lite     # -a yo'q, -m yo'q - metama'lumotsiz

# --- 2) Tag'ni tekshirish - annotated tag O'ZINING obyektiga ega ---
# $ git cat-file -p v1.1.0
# tag v1.1.0
# tagger Ism Familiya <email> 1700000000 +0500
#
# Release 1.1.0: course_builder library + RU coverage fixes
#
# (lightweight tag uchun git cat-file -p commit'ning O'ZINI ko'rsatadi -
#  alohida tag obyekti YO'Q)

# --- 3) Tag'ni remote'ga push qilish ---
# $ git push origin v1.1.0

# ============================================================
# --- 4) Tegga bog'langan CI trigger (117-kurs capstone'idan) ---
# ============================================================
RELEASE_WORKFLOW_YAML = \"\"\"
name: Release Deploy

on:
  push:
    tags:
      - 'v*.*.*'          # <- FAQAT semver tegi push qilinganda

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Extract version from tag
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> "$GITHUB_ENV"
      - name: Deploy release ${{ env.VERSION }}
        run: echo "Deploying version $VERSION to production"
\"\"\"

# ============================================================
# Solishtirish: bu platformaning HAQIQIY deploy-backend.yml'i
# ============================================================
CURRENT_REAL_TRIGGER = \"\"\"
on:
  push:
    branches: [server]      # <- HAR push'da, tegsiz
    paths:
      - 'backend/**'
  workflow_dispatch:
\"\"\"

print("Reliz strategiyasi: FAQAT teg push qilinganda deploy")
print(RELEASE_WORKFLOW_YAML)
print("Bu platformaning haqiqiy strategiyasi: HAR push'da deploy")
print(CURRENT_REAL_TRIGGER)
""".strip()

L11_CODE_RU = """
# ============================================================
# Тегирование релиза - annotated tag и CI триггер, привязанный
# к тегу
# ============================================================

# --- 1) Создание annotated tag (флаг -a из курса 112) ---
# $ git tag -a v1.1.0 -m "Release 1.1.0: course_builder library + RU coverage fixes"
#
# Для сравнения - lightweight tag (НЕ РЕКОМЕНДУЕТСЯ для релиза):
# $ git tag v1.1.0-lite     # без -a, без -m - без метаданных

# --- 2) Проверка тега - annotated tag имеет СОБСТВЕННЫЙ объект ---
# $ git cat-file -p v1.1.0
# tag v1.1.0
# tagger Имя Фамилия <email> 1700000000 +0500
#
# Release 1.1.0: course_builder library + RU coverage fixes
#
# (для lightweight tag git cat-file -p покажет САМ коммит -
#  отдельного объекта тега НЕТ)

# --- 3) Push тега в remote ---
# $ git push origin v1.1.0

# ============================================================
# --- 4) CI триггер, привязанный к тегу (из капстоуна курса 117) ---
# ============================================================
RELEASE_WORKFLOW_YAML = \"\"\"
name: Release Deploy

on:
  push:
    tags:
      - 'v*.*.*'          # <- ТОЛЬКО при push semver-тега

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Extract version from tag
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> "$GITHUB_ENV"
      - name: Deploy release ${{ env.VERSION }}
        run: echo "Deploying version $VERSION to production"
\"\"\"

# ============================================================
# Для сравнения: РЕАЛЬНЫЙ deploy-backend.yml этой платформы
# ============================================================
CURRENT_REAL_TRIGGER = \"\"\"
on:
  push:
    branches: [server]      # <- при КАЖДОМ push, без тега
    paths:
      - 'backend/**'
  workflow_dispatch:
\"\"\"

print("Стратегия релиза: деплой ТОЛЬКО при push тега")
print(RELEASE_WORKFLOW_YAML)
print("Реальная стратегия этой платформы: деплой при КАЖДОМ push")
print(CURRENT_REAL_TRIGGER)
""".strip()

L11_TASK = {
    "task_title": "O'z loyihangiz uchun tegga asoslangan reliz workflow'ini loyihalang",
    "task_title_ru": "Спроектируйте релизный workflow на основе тегов для своего проекта",
    "task_description": (
        "Shaxsiy repozitoriyangizda (yoki test repozitoriyada) annotated "
        "reliz tegi yarating (git tag -a v1.0.0 -m \"...\"). So'ngra shu "
        "darsdagi RELEASE_WORKFLOW_YAML namunasiga asoslanib, "
        "'on: push: tags' trigger'idan foydalanadigan (haqiqiy deploy "
        "qilish shart emas, faqat YAML tuzilishi to'g'ri bo'lishi kerak) "
        "o'z GitHub Actions workflow faylingizni yozing."
    ),
    "task_description_ru": (
        "В своём репозитории (или тестовом) создайте annotated тег релиза "
        "(git tag -a v1.0.0 -m \"...\"). Затем, опираясь на пример "
        "RELEASE_WORKFLOW_YAML из этого урока, напишите свой файл GitHub "
        "Actions workflow, использующий триггер 'on: push: tags' (реальный "
        "деплой не обязателен, важна правильная структура YAML)."
    ),
    "task_requirements": (
        "1) git tag -v (yoki git cat-file -p) chiqishi ilova qilinishi "
        "kerak - annotated ekanini isbotlash uchun. 2) Workflow YAML fayli "
        "'v*.*.*' pattern'idan foydalanishi shart. 3) Nima uchun "
        "lightweight emas, aynan annotated tag tanlanganini bir gapda "
        "tushuntiring."
    ),
    "task_requirements_ru": (
        "1) Приложить вывод git tag -v (или git cat-file -p) - для "
        "подтверждения, что тег annotated. 2) Файл workflow YAML должен "
        "использовать паттерн 'v*.*.*'. 3) Одним предложением объяснить, "
        "почему выбран именно annotated, а не lightweight тег."
    ),
    "task_technologies": "Git (tag), GitHub Actions",
    "task_deadline_days": 4,
}

L11_SAMPLE = {
    "title": "Namuna: reliz teglash va tegga bog'langan deploy workflow'i",
    "description": (
        "Ushbu darsning kod namunasi asosida, annotated tag yaratish "
        "buyruqlari va 'on: push: tags' trigger'idan foydalanadigan "
        "to'liq GitHub Actions workflow fayli."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "release-deploy.yml",
            "language": "yaml",
            "code": (
                "name: Release Deploy\n\n"
                "# Faqat semver formatidagi teg (v1.2.3 kabi) push qilinganda\n"
                "# ishga tushadi - har bir oddiy commit'da EMAS.\n\n"
                "on:\n"
                "  push:\n"
                "    tags:\n"
                "      - 'v*.*.*'\n\n"
                "jobs:\n"
                "  deploy:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 15\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n\n"
                "      - name: Extract version from tag\n"
                "        run: echo \"VERSION=${GITHUB_REF#refs/tags/v}\" >> \"$GITHUB_ENV\"\n\n"
                "      - name: Verify tag is annotated\n"
                "        run: |\n"
                "          git fetch --tags --force\n"
                "          git cat-file -t \"$GITHUB_REF_NAME\" | grep -q '^tag$' || \\\n"
                "            (echo \"XATO: bu lightweight tag, annotated emas!\" && exit 1)\n\n"
                "      - name: Deploy release\n"
                "        run: echo \"Deploying version $VERSION to production\"\n"
            ),
        },
        {
            "filename": "create_release_tag.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -e\n\n"
                "VERSION=\"$1\"   # masalan: v1.1.0\n"
                "MESSAGE=\"$2\"   # masalan: \"Release 1.1.0: course_builder library\"\n\n"
                "if [ -z \"$VERSION\" ] || [ -z \"$MESSAGE\" ]; then\n"
                "    echo \"Usage: $0 <version> <message>\"\n"
                "    exit 1\n"
                "fi\n\n"
                "git tag -a \"$VERSION\" -m \"$MESSAGE\"\n"
                "git push origin \"$VERSION\"\n"
                "echo \"Annotated tag $VERSION yaratildi va push qilindi.\"\n"
            ),
        },
    ],
}

L11_EXERCISES = [
    {
        "title": "Reliz uchun tag turi",
        "title_ru": "Тип тега для релиза",
        "description": "Reliz uchun nega DOIM annotated tag (lightweight emas) ishlatilishi tavsiya etiladi?",
        "description_ru": "Почему для релиза ВСЕГДА рекомендуется использовать annotated tag (не lightweight)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki annotated tag tezroq push qilinadi",
            "Chunki annotated tag muallif, sana, xabar va imzoni saqlaydigan to'liq obyekt",
            "Chunki lightweight tag umuman ishlamaydi",
            "Chunki annotated tag avtomatik CHANGELOG yaratadi",
        ],
        "options_ru": [
            "Потому что annotated tag быстрее пушится",
            "Потому что annotated tag - полноценный объект с автором, датой, сообщением и подписью",
            "Потому что lightweight tag вообще не работает",
            "Потому что annotated tag автоматически создаёт CHANGELOG",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "112-kursda o'rgangan annotated tag'ning ICHKI tuzilishini eslang.",
        "hint_ru": "Вспомните внутреннюю структуру annotated tag из курса 112.",
        "explanation": "Annotated tag audit va ishonch uchun kerakli metama'lumotni (kim, qachon, nega) saqlaydi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Bu platformaning haqiqiy deploy trigger'i",
        "title_ru": "Реальный триггер деплоя этой платформы",
        "description": "Bu platformaning HAQIQIY deploy-backend.yml'i hozirda qanday strategiyada ishlaydi?",
        "description_ru": "По какой стратегии сейчас работает РЕАЛЬНЫЙ deploy-backend.yml этой платформы?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat v*.*.* tegi push qilinganda",
            "server branch'iga har push qilinganda",
            "Faqat qo'lda workflow_dispatch orqali",
            "Har oy bir marta jadval bo'yicha",
        ],
        "options_ru": [
            "Только при push тега v*.*.*",
            "При каждом push в ветку server",
            "Только вручную через workflow_dispatch",
            "Раз в месяц по расписанию",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsda bu ikki strategiya (haqiqiy vs tegga asoslangan) alohida solishtirilgan.",
        "hint_ru": "В уроке отдельно сравнены эти две стратегии (реальная vs основанная на тегах).",
        "explanation": "Hozirgi haqiqiy workflow \"har push -> deploy\" strategiyasida - bu darsda muqobil, tegga asoslangan strategiya taklif qilingan.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "To'liq reliz zanjirini tartiblang",
        "title_ru": "Расположите полную цепочку релиза по порядку",
        "description": "Merge'dan deploygacha bo'lgan to'liq reliz zanjirini to'g'ri tartibda joylashtiring.",
        "description_ru": "Расположите полную цепочку релиза от merge до деплоя в правильном порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "PR merge qilinadi",
            "Versiya turi aniqlanadi (SemVer)",
            "CHANGELOG.md yangilanadi",
            "Annotated tag yaratiladi va push qilinadi",
            "CI teg trigger'i orqali deploy qiladi",
        ],
        "drag_items_ru": [
            "PR смёржен",
            "Определяется тип версии (SemVer)",
            "Обновляется CHANGELOG.md",
            "Создаётся и пушится annotated tag",
            "CI деплоит через триггер тега",
        ],
        "correct_order": [
            "PR merge qilinadi",
            "Versiya turi aniqlanadi (SemVer)",
            "CHANGELOG.md yangilanadi",
            "Annotated tag yaratiladi va push qilinadi",
            "CI teg trigger'i orqali deploy qiladi",
        ],
        "hint": "Diagrammadagi flowchart'ni yuqoridan pastga o'qing.",
        "hint_ru": "Прочитайте flowchart диаграммы сверху вниз.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Reliz teg prefiksi",
        "title_ru": "Префикс релизного тега",
        "description": "SemVer reliz teglari deyarli har doim ___ prefiksi bilan yoziladi (masalan v1.2.0).",
        "description_ru": "Теги релизов SemVer почти всегда пишутся с префиксом ___ (например v1.2.0).",
        "exercise_type": "fill_in_blank",
        "correct_answers": "v",  # literal prefix character, no natural-language RU translation needed
        "hint": "Darsda ikkita marta ko'rilgan bitta harfli prefiks.",
        "hint_ru": "Однобуквенный префикс, дважды встреченный в уроке.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 12 — R2: Takrorlash — fikr-mulohaza, merge strategiyasi,
# semver, changelog, reliz teglash
# ---------------------------------------------------------------------------

L12_TEXT = """
<h3>Bu darsda yangi mavzu yo'q — ikkinchi sintez</h3>
<p>Bu — kursning ikkinchi va oxirgi (capstone'dan oldingi) takrorlash
darsi. 6-11-darslarda o'rgangan HAMMA narsani BITTA reliz jarayonida
birlashtiramiz: aniq fikr-mulohaza berish (6-dars), uni ego'siz qabul
qilish (7-dars), merge strategiyasini tanlash (8-dars), semantik
versiyalash (9-dars), changelog yuritish (10-dars), va reliz teglash
(11-dars). Yangi tushuncha yo'q — faqat mavjud bilimni bitta izchil
reliz jarayoniga yig'ish.</p>

<h3>Olti mavzuni bitta reliz jarayonida ko'rish</h3>
<p>Quyidagi kod namunasida siz xayoliy "profil ballari" bug'i PR
ochilgandan RELIZ chiqarilgunigacha bo'lgan davrni ko'rasiz: reviewer
aniq izoh qoldiradi (6-dars), muallif rozi bo'lib tuzatadi (7-dars),
jamoa Squash strategiyasini tanlaydi (8-dars), o'zgarish PATCH sifatida
tasniflanadi (9-dars), CHANGELOG.md'ga "Fixed" bo'limiga qo'shiladi
(10-dars), va nihoyat annotated tag orqali reliz qilinadi (11-dars).</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Agar reviewer "bu funksiya yomon" deb yozsa (vague), muallif buni
qanday actionable izohga aylantirib so'rashi mumkin?</li>
<li>Nima uchun bitta bug tuzatish (breaking change bo'lmagan) MAJOR
emas, PATCH sifatida versiyalanadi?</li>
<li>Agar jamoa Squash and merge tanlagan bo'lsa, CHANGELOG.md'ga necha
qatorlik yozuv qo'shiladi — feature branch'dagi 5 ta commit uchunmi,
yoki bitta yakuniy commit uchunmi?</li>
<li>Nega annotated tag push qilinishi CI'ni ishga tushirishi uchun
YETARLI, lekin lightweight tag reliz jarayoni uchun TAVSIYA
ETILMAYDI?</li>
</ul>

<h3>Olti mavzuning bitta reliz jarayonidagi joylashuvi</h3>
<pre class="mermaid">
flowchart TB
  FB["Reviewer aniq izoh qoldiradi
(6-dars)"] --> RESP["Muallif ego'siz javob beradi,
tuzatadi
(7-dars)"]
  RESP --> MRG["Jamoa Squash strategiyasini
tanlaydi
(8-dars)"]
  MRG --> VER["O'zgarish PATCH sifatida
tasniflanadi
(9-dars)"]
  VER --> CHL["CHANGELOG.md 'Fixed'
bo'limiga qo'shiladi
(10-dars)"]
  CHL --> TAG["Annotated tag + CI deploy
(11-dars)"]
  style FB fill:#d6e9ff,stroke:#2266aa
  style MRG fill:#ffe9b3,stroke:#d09000
  style TAG fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma 6-11-darslarning har biri BITTA reliz jarayonida qanday
qatlam bo'lib joylashishini ko'rsatadi — bu keyingi, yakuniy capstone
darsida (13-dars) 112 va 117-kurslar bilan birlashadigan asosiy
"skelet".</p>

<h3>Nega bu dars qisqaroq</h3>
<p>Bu takrorlash darsi ham, R1 (5-dars) kabi, qasddan yangi
tushunchalar bilan "shishirilmagan" — uning vazifasi 6-11-darslarni
BOG'LASH. Kod namunasi to'liq bir reliz jarayonini ko'rsatadi, lekin
har bir qadami allaqachon tanish. Keyingi, yakuniy 13-darsda barcha
14 dars VA ikkala oldingi kurs (112, 117) bitta capstone loyihada
birlashadi.</p>
""".strip()

L12_TEXT_RU = """
<h3>В этом уроке нет новой темы — второй синтез</h3>
<p>Это — второй и последний (перед капстоуном) урок повторения.
Собираем ВСЁ изученное в уроках 6-11 в ОДИН процесс релиза: точная
обратная связь (урок 6), принятие её без эго (урок 7), выбор стратегии
merge (урок 8), семантическое версионирование (урок 9), ведение
changelog (урок 10), и тегирование релиза (урок 11). Новых понятий нет
— только сборка существующих знаний в один цельный процесс релиза.</p>

<h3>Шесть тем в одном процессе релиза</h3>
<p>В примере кода ниже вы увидите период от открытия PR до выпуска
РЕЛИЗА для условного бага "баллы профиля": reviewer оставляет точный
комментарий (урок 6), автор соглашается и исправляет (урок 7), команда
выбирает стратегию Squash (урок 8), изменение классифицируется как
PATCH (урок 9), добавляется в раздел "Fixed" CHANGELOG.md (урок 10), и,
наконец, выпускается релиз через annotated tag (урок 11).</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Если reviewer напишет "эта функция плохая" (vague), как автор может
попросить превратить это в actionable комментарий?</li>
<li>Почему исправление одного бага (не breaking change) версионируется
как PATCH, а не MAJOR?</li>
<li>Если команда выбрала Squash and merge, сколько строк добавится в
CHANGELOG.md — для 5 коммитов feature-ветки, или для одного итогового
коммита?</li>
<li>Почему push annotated tag ДОСТАТОЧЕН для запуска CI, но lightweight
tag НЕ РЕКОМЕНДУЕТСЯ для процесса релиза?</li>
</ul>

<h3>Расположение шести тем в одном процессе релиза</h3>
<pre class="mermaid">
flowchart TB
  FB["Reviewer оставляет точный
комментарий
(урок 6)"] --> RESP["Автор отвечает без эго,
исправляет
(урок 7)"]
  RESP --> MRG["Команда выбирает
стратегию Squash
(урок 8)"]
  MRG --> VER["Изменение классифицируется
как PATCH
(урок 9)"]
  VER --> CHL["Добавляется в раздел 'Fixed'
CHANGELOG.md
(урок 10)"]
  CHL --> TAG["Annotated tag + CI деплой
(урок 11)"]
  style FB fill:#d6e9ff,stroke:#2266aa
  style MRG fill:#ffe9b3,stroke:#d09000
  style TAG fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает, как каждый из уроков 6-11 располагается слоем
внутри ОДНОГО процесса релиза — это базовый "скелет", который в
следующем, финальном уроке капстоуна (урок 13) объединится с курсами
112 и 117.</p>

<h3>Почему этот урок короче</h3>
<p>Этот урок повторения, как и R1 (урок 5), намеренно не "раздут"
новыми понятиями — его задача СВЯЗАТЬ уроки 6-11. Пример кода
показывает полный процесс релиза, но каждый его шаг уже знаком. В
следующем, финальном уроке 13 все 14 уроков И оба предыдущих курса
(112, 117) объединятся в одном капстоун-проекте.</p>
""".strip()

L12_CODE = """
# ============================================================
# Sintez: xayoliy "profil ballari" bug'i - PR'dan RELIZgacha
# to'liq jarayon (6-11-darslarning barchasi)
# ============================================================

# --- 6-dars: reviewer aniq (actionable) izoh qoldiradi ---
REVIEW_COMMENT = (
    "students.py'da 88-qatorda project.status tekshirilmayapti - "
    "Rejected loyihalar ham ball hisobiga qo'shilib qolyapti. "
    "Taklif: filter(lambda p: p.status in ('approved', 'reviewed'), projects)"
)

# --- 7-dars: muallif rozi bo'lib, tuzatib javob beradi ---
AUTHOR_REPLY = "Rozi, tuzatildi: a1b2c3d. Testni ham qo'shdim."

# --- 8-dars: jamoa Squash and merge tanlaydi ---
MERGE_STRATEGY = "squash"
FINAL_COMMIT = "fix(students): filter project points by approved status"

# --- 9-dars: o'zgarish PATCH sifatida tasniflanadi ---
CHANGE_TYPE = "patch"  # breaks_api=False, adds_feature=False
CURRENT_VERSION = "1.0.0"
NEW_VERSION = "1.0.1"

# --- 10-dars: CHANGELOG.md'ga qo'shiladi ---
CHANGELOG_ENTRY = f\"\"\"
## [{NEW_VERSION}] - 2026-02-01

### Fixed
- filter project points by approved status (students)
\"\"\"

# --- 11-dars: annotated tag + CI deploy ---
RELEASE_COMMANDS = [
    f'git tag -a v{NEW_VERSION} -m "Release {NEW_VERSION}: fix project points filtering"',
    f"git push origin v{NEW_VERSION}",
]

print("1) Review izohi (6-dars):", REVIEW_COMMENT)
print("2) Muallif javobi (7-dars):", AUTHOR_REPLY)
print("3) Merge strategiyasi (8-dars):", MERGE_STRATEGY, "->", FINAL_COMMIT)
print("4) Versiya turi (9-dars):", CHANGE_TYPE, CURRENT_VERSION, "->", NEW_VERSION)
print("5) Changelog (10-dars):", CHANGELOG_ENTRY)
print("6) Reliz buyruqlari (11-dars):", RELEASE_COMMANDS)
""".strip()

L12_CODE_RU = """
# ============================================================
# Синтез: условный баг "баллы профиля" - полный процесс от PR
# до РЕЛИЗА (всё из уроков 6-11)
# ============================================================

# --- Урок 6: reviewer оставляет точный (actionable) комментарий ---
REVIEW_COMMENT = (
    "В строке 88 students.py не проверяется project.status - "
    "отклонённые (Rejected) проекты тоже учитываются в баллах. "
    "Предложение: filter(lambda p: p.status in ('approved', 'reviewed'), projects)"
)

# --- Урок 7: автор соглашается, исправляет и отвечает ---
AUTHOR_REPLY = "Согласен, исправлено: a1b2c3d. Добавил и тест."

# --- Урок 8: команда выбирает Squash and merge ---
MERGE_STRATEGY = "squash"
FINAL_COMMIT = "fix(students): filter project points by approved status"

# --- Урок 9: изменение классифицируется как PATCH ---
CHANGE_TYPE = "patch"  # breaks_api=False, adds_feature=False
CURRENT_VERSION = "1.0.0"
NEW_VERSION = "1.0.1"

# --- Урок 10: добавляется в CHANGELOG.md ---
CHANGELOG_ENTRY = f\"\"\"
## [{NEW_VERSION}] - 2026-02-01

### Fixed
- filter project points by approved status (students)
\"\"\"

# --- Урок 11: annotated tag + CI деплой ---
RELEASE_COMMANDS = [
    f'git tag -a v{NEW_VERSION} -m "Release {NEW_VERSION}: fix project points filtering"',
    f"git push origin v{NEW_VERSION}",
]

print("1) Комментарий ревью (урок 6):", REVIEW_COMMENT)
print("2) Ответ автора (урок 7):", AUTHOR_REPLY)
print("3) Стратегия merge (урок 8):", MERGE_STRATEGY, "->", FINAL_COMMIT)
print("4) Тип версии (урок 9):", CHANGE_TYPE, CURRENT_VERSION, "->", NEW_VERSION)
print("5) Changelog (урок 10):", CHANGELOG_ENTRY)
print("6) Команды релиза (урок 11):", RELEASE_COMMANDS)
""".strip()

L12_TASK = {
    "task_title": "To'liq reliz jarayonini o'zingizning o'zgarishingiz uchun qo'llang",
    "task_title_ru": "Примените полный процесс релиза к своему изменению",
    "task_description": (
        "5-darsdagi PR'ingizni (yoki yangi kichik o'zgarishni) davom "
        "ettiring: (1) o'zingizga (yoki hamkasbingizga) kamida bitta "
        "actionable izoh yozdiring/yozing, (2) unga ego'siz javob "
        "bering/bering, (3) qaysi merge strategiyasini tanlaganingizni "
        "asoslang, (4) o'zgarishni MAJOR/MINOR/PATCH sifatida tasniflang, "
        "(5) CHANGELOG.md yozuvi yarating, (6) annotated tag bilan "
        "\"reliz qiling\"."
    ),
    "task_description_ru": (
        "Продолжите свой PR из урока 5 (или новое небольшое изменение): "
        "(1) напишите себе (или коллеге) минимум один actionable "
        "комментарий, (2) ответьте на него без эго, (3) обоснуйте выбор "
        "стратегии merge, (4) классифицируйте изменение как MAJOR/MINOR/"
        "PATCH, (5) создайте запись CHANGELOG.md, (6) \"выпустите релиз\" "
        "с annotated tag."
    ),
    "task_requirements": (
        "1) Har bir 6 qadam uchun alohida bo'lim bo'lishi kerak. 2) "
        "Annotated tag'ning git cat-file -p natijasi ilova qilinishi "
        "shart. 3) CHANGELOG.md yozuvi versiya raqami va sana bilan "
        "boshlanishi kerak."
    ),
    "task_requirements_ru": (
        "1) Для каждого из 6 шагов - отдельный раздел. 2) Обязательно "
        "приложить вывод git cat-file -p для annotated tag. 3) Запись "
        "CHANGELOG.md должна начинаться с номера версии и даты."
    ),
    "task_technologies": "Git, GitHub (Pull Requests), Markdown",
    "task_deadline_days": 4,
}

L12_SAMPLE = {
    "title": "Namuna: 6-11-darslarning barchasini birlashtirgan reliz jarayoni",
    "description": (
        "Ushbu darsning kod namunasi asosida, xayoliy \"profil ballari\" "
        "bug'i uchun izohdan tortib relizgacha bo'lgan to'liq, izohli "
        "jarayon."
    ),
    "sample_type": "code",
    "code_files": [
        {"filename": "full_release_demo.py", "language": "python", "code": "# Qarang: L12_CODE ushbu darsning to'liq matnida"},
    ],
}

L12_EXERCISES = [
    {
        "title": "Vague izohni actionable qilish",
        "title_ru": "Превращение vague комментария в actionable",
        "description": "\"Bu funksiya yomon\" degan izohni actionable qilish uchun ENG MUHIM qo'shimcha nima?",
        "description_ru": "Какое дополнение НАИБОЛЕЕ важно, чтобы сделать комментарий \"эта функция плохая\" actionable?",
        "exercise_type": "multiple_choice",
        "options": [
            "Emoji qo'shish",
            "Aniq qator/holat va NEGA muammo ekanini ko'rsatish",
            "Izohni uzunroq qilish",
            "Boshqa dasturchi bilan solishtirish",
        ],
        "options_ru": [
            "Добавить эмодзи",
            "Указать конкретную строку/случай и ПОЧЕМУ это проблема",
            "Сделать комментарий длиннее",
            "Сравнить с другим разработчиком",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "6-darsdagi uch qismni eslang.",
        "hint_ru": "Вспомните три части из урока 6.",
        "explanation": "Aniq qator/holat + sabab - vague izohni actionable'ga aylantiruvchi asosiy element.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "PATCH versiya sababi",
        "title_ru": "Причина версии PATCH",
        "description": "Bug tuzatish (breaking change bo'lmagan) nega MAJOR emas, aynan PATCH sifatida versiyalanadi?",
        "description_ru": "Почему исправление бага (не breaking change) версионируется именно как PATCH, а не MAJOR?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki PATCH har doim standart tanlov",
            "Chunki mavjud API/interfeys buzilmaydi, faqat xatti-harakat to'g'rilanadi",
            "Chunki bug tuzatish hech qachon versiyalanmaydi",
            "Chunki changelog PATCH'ni talab qiladi",
        ],
        "options_ru": [
            "Потому что PATCH - всегда выбор по умолчанию",
            "Потому что существующий API/интерфейс не ломается, только исправляется поведение",
            "Потому что исправление бага никогда не версионируется",
            "Потому что changelog требует PATCH",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "9-darsdagi qaror daraxtini eslang.",
        "hint_ru": "Вспомните дерево решений из урока 9.",
        "explanation": "SemVer qoidasi: agar mavjud narsa buzilmasa va yangi funksiya qo'shilmasa - bu PATCH.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "To'liq reliz jarayonini tartiblang",
        "title_ru": "Расположите полный процесс релиза по порядку",
        "description": "6-11-darslarning bitta reliz jarayoni ichidagi to'g'ri ketma-ketligini joylashtiring.",
        "description_ru": "Расположите правильную последовательность уроков 6-11 внутри одного процесса релиза.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Aniq izoh + ego'siz javob",
            "Merge strategiyasini tanlash",
            "SemVer bo'yicha tasniflash",
            "Changelog yozish",
            "Annotated tag va CI deploy",
        ],
        "drag_items_ru": [
            "Точный комментарий + ответ без эго",
            "Выбор стратегии merge",
            "Классификация по SemVer",
            "Запись в changelog",
            "Annotated tag и CI деплой",
        ],
        "correct_order": [
            "Aniq izoh + ego'siz javob",
            "Merge strategiyasini tanlash",
            "SemVer bo'yicha tasniflash",
            "Changelog yozish",
            "Annotated tag va CI deploy",
        ],
        "hint": "Diagrammadagi flowchart'ni yuqoridan pastga o'qing.",
        "hint_ru": "Прочитайте flowchart диаграммы сверху вниз.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 13 — Capstone: bitta xususiyatni to'liq jamoaviy workflow
# orqali yetkazish (112 + 117 + bu kursning birlashuvi)
# ---------------------------------------------------------------------------

L13_TEXT = """
<h3>Uchta kursni birlashtiruvchi yakuniy loyiha</h3>
<p>112-kursda siz Git'ning ICHKI qismini (obyektlar, bisect, hook'lar,
teglar) o'rgandingiz. 117-kursda GitHub Actions orqali CI/CD QURISHNI
o'rgandingiz. Ushbu kursda esa INSON qatlamini — code review, commit
madaniyati, fikr-mulohaza, merge strategiyasi, versiyalash, reliz — 
o'rgandingiz. Capstone loyihasi UCHALASINI BIRLASHTIRADI: bitta
xususiyatni chinakam jamoa qanday qilib "ishlab chiqarishga yetkazishi"
mumkinligini to'liq, boshidan oxirigacha ko'rsatadi.</p>

<h3>Vazifa 1: to'liq zanjir — atomik commit'dan reliz teggacha</h3>
<p>Shaxsiy repozitoriyangizda (yoki shu platforma fork'ida) kichik,
haqiqiy xususiyat tanlang. Uni AYNAN quyidagi zanjir bo'yicha
yetkazing: (a) 3-darsdagi kabi ikkita-uchta ATOMIK, Conventional
Commits formatidagi commit yozing; (b) 1-darsdagi to'rt bo'limli PR
tavsifini yozing; (c) 4-darsdagi to'rt ustuvorlik bo'yicha o'z-o'zingizni
reviewer sifatida tekshiring; (d) 8-darsdagi uchta strategiyadan birini
tanlab, nima uchun tanlaganingizni asoslang; (e) 9-darsdagi qaror
daraxti bo'yicha o'zgarishni MAJOR/MINOR/PATCH sifatida tasniflang; (f)
10-darsdagi formatda CHANGELOG.md yozuvi yarating; (g) 11-darsdagi kabi
annotated tag yarating va push qiling.</p>

<h3>Vazifa 2: git bisect'ni atomik commit madaniyati bilan bog'lash (112-kurs)</h3>
<p>112-kursning bisect darsida siz <code>git bisect</code>ni QO'LDA
ishlatishni o'rgangansiz. Bu kursning 3-darsida esa nega ATOMIK
commit'lar bisect'ni FOYDALI qilishini ko'rdingiz (aralash commit
QAYSI o'zgarish sabab ekanini yashiradi). Capstone'da buni AMALDA
bog'lang: 5 ta ATOMIK commit yarating (har biri bitta kichik o'zgarish),
ularning BIRIGA ataylab kichik bug kiritib qo'ying, so'ng
<code>git bisect start</code> / <code>git bisect good/bad</code> orqali
xatoni toping. Natijada bisect ANIQ QAYSI commit sabab ekanini
ko'rsatishi kerak — bu 3-darsda aytilgan nazariy foydaning amaliy
isboti.</p>

<h3>Vazifa 3: uch qatlamli himoya — hook, review, CI required check</h3>
<p>112-kursning hook darsida mahalliy <code>pre-commit</code> hook
maxsus bayroq bilan chetlab o'tilishi mumkinligini o'rgandingiz (repo
hook'ni majburiy qilib bo'lmaydi — u faqat mahalliy qulaylik). 117-kursning
branch himoyasi darsida esa CI'ning required status check sifatida
bunday chetlab o'tishni oldini olishini ko'rdingiz. Ushbu kursning
4-darsida esa inson review'i CI TOPA OLMAYDIGAN narsalarni (masalan
yaxshi arxitektura qarori) qo'shishini o'rgandingiz. Capstone'da UCHALA
qatlamni birlashtiring: (1) mahalliy <code>pre-commit</code> hook orqali
tez tekshiruv (masalan lint), (2) xuddi shu tekshiruvni
<code>test.yml</code>ga alohida job sifatida qo'shib, CI'ni yagona
chetlab bo'lmaydigan qatlam qiling, (3) PR'ga ushbu kursning 4-darsidagi
to'rt ustuvorlik checklist'i bo'yicha o'z-o'zingizni baholovchi izoh
yozing.</p>

<h3>Vazifa 4: reliz tegini haqiqiy CI trigger'iga ulash (117-kurs)</h3>
<p>117-kursning capstone darsida <code>on: push: tags: ['v*.*.*']</code>
KONSEPSIYASINI ko'rgansiz. Ushbu kursning 11-darsida esa buni ANNOTATED
TAG bilan qanday BOG'LASHNI ko'rdingiz. Capstone'da bularni birlashtiring:
1-vazifadagi annotated tegingizni haqiqiy (yoki test) GitHub repozitoriyaga
push qiling va <code>on: push: tags</code> trigger'iga ega workflow
FAOL ishga tushganini (Actions bo'limida yashil belgi bilan) skrinshot
orqali isbotlang.</p>

<h3>Capstone arxitekturasi: uch kursning kesishuvi</h3>
<pre class="mermaid">
flowchart TB
  subgraph K112["112-kurs: Git ichki tuzilishi"]
    G1["git bisect"]
    G2["pre-commit hook"]
    G3["annotated tag obyekti"]
  end
  subgraph K3["Bu kurs: jamoaviy jarayon"]
    T1["Atomik commit + PR tavsifi"]
    T2["To'rt ustuvorlikli review"]
    T3["Merge strategiyasi + SemVer + changelog"]
    T4["Reliz teglash strategiyasi"]
  end
  subgraph K117["117-kurs: CI/CD"]
    A1["Required status check"]
    A2["on: push: tags trigger"]
  end
  G1 -->|"ATOMIK commit'lar bilan
FOYDALI bo'ladi"| T1
  G2 -->|"CI bilan ikki qatlamli
himoyaga aylanadi"| A1
  T2 -->|"CI TOPA OLMAYDIGAN
narsani qo'shadi"| A1
  T3 -->|"reliz uchun tag
yaratiladi"| G3
  G3 -->|"tag push qilinadi"| T4
  T4 -->|"CI trigger'ini
ishga tushiradi"| A2
  style K112 fill:#d6e9ff,stroke:#2266aa
  style K3 fill:#ffe9b3,stroke:#d09000
  style K117 fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Diagramma capstone'ning markaziy g'oyasini ko'rsatadi: 112-kursning
ICHKI mexanizmlari (chapda) bu kursning JAMOAVIY jarayoni (o'rtada)
orqali 117-kursning AVTOMATIK pipeline'iga (o'ngda) oqib boradi. Uchala
kurs alohida emas — BITTA yaxlit "zamonaviy jamoaviy ishlab chiqarish"
bilimining uch qismi.</p>

<h3>Nega bu to'rtta vazifa tasodifiy tanlanmagan</h3>
<p>Har bir vazifa ANIQ ikkita darsni (bitta boshqa kursdan, bitta shu
kursdan) bog'laydi va ular BIR-BIRISIZ "yarim tugallangan" qolishini
ko'rsatadi: bisect o'zi ishlaydi, lekin aralash commit'larda foydasi
cheklangan; pre-commit hook o'zi yetarli emas — CI bo'lmasa "ixtiyoriy"
bo'lib qoladi; annotated tag o'zi shunchaki ma'lumot — deploy trigger'iga
aylanmaguncha amaliy qiymati cheklangan; CI'ning tag trigger'i o'zi
ham FOYDASIZ, agar teglash strategiyasi (qachon, nima uchun teglash)
bo'lmasa. Capstone — uchta kursni "birlashtirish" emas, balki HAR BIR
bilim NIMA UCHUN qolganlarisiz to'liq emasligini ko'rsatish.</p>
""".strip()

L13_TEXT_RU = """
<h3>Финальный проект, объединяющий три курса</h3>
<p>В курсе 112 вы изучили ВНУТРЕННЮЮ часть Git (объекты, bisect, hooks,
теги). В курсе 117 вы научились СТРОИТЬ CI/CD через GitHub Actions. В
этом курсе вы изучили ЧЕЛОВЕЧЕСКИЙ слой — code review, культуру
коммитов, обратную связь, стратегию merge, версионирование, релиз.
Капстоун-проект ОБЪЕДИНЯЕТ ВСЕ ТРИ: показывает полностью, от начала до
конца, как реальная команда может "довести" одну фичу до продакшена.</p>

<h3>Задача 1: полная цепочка — от атомарного коммита до тега релиза</h3>
<p>В своём репозитории (или форке этой платформы) выберите небольшую,
реальную фичу. Проведите её ТОЧНО по следующей цепочке: (a) как в уроке
3, напишите два-три АТОМАРНЫХ коммита в формате Conventional Commits;
(b) напишите описание PR из четырёх разделов, как в уроке 1; (c)
проверьте себя как reviewer по четырём приоритетам из урока 4; (d)
выберите одну из трёх стратегий из урока 8 и обоснуйте выбор; (e)
классифицируйте изменение как MAJOR/MINOR/PATCH по дереву решений из
урока 9; (f) создайте запись CHANGELOG.md в формате урока 10; (g)
создайте и запушьте annotated tag, как в уроке 11.</p>

<h3>Задача 2: связь git bisect с культурой атомарных коммитов (курс 112)</h3>
<p>В уроке bisect курса 112 вы научились использовать <code>git
bisect</code> ВРУЧНУЮ. В уроке 3 этого курса вы увидели, почему АТОМАРНЫЕ
коммиты делают bisect ПОЛЕЗНЫМ (смешанный коммит скрывает, КАКОЕ
изменение стало причиной). Свяжите это НА ПРАКТИКЕ в капстоуне: создайте
5 АТОМАРНЫХ коммитов (каждый - одно небольшое изменение), намеренно
внесите небольшой баг в ОДИН из них, затем найдите ошибку через
<code>git bisect start</code> / <code>git bisect good/bad</code>. В
результате bisect должен точно указать, КАКОЙ коммит стал причиной —
это практическое доказательство теоретической пользы из урока 3.</p>

<h3>Задача 3: трёхслойная защита — hook, ревью, required check CI</h3>
<p>В уроке hooks курса 112 вы изучили, что локальный
<code>pre-commit</code> hook можно обойти специальным флагом (репозиторий
не может сделать hook обязательным — он лишь локальное удобство). В уроке
защиты веток курса 117 вы увидели, что CI как required status check
предотвращает такой обход. В уроке 4 этого курса вы изучили, что ревью
человека добавляет то, что CI НЕ МОЖЕТ найти (например, хорошее
архитектурное решение). В капстоуне объедините ВСЕ ТРИ слоя: (1)
быструю проверку (например lint) через локальный <code>pre-commit</code>
hook, (2) ту же проверку как отдельный job в <code>test.yml</code>,
делающий CI единственным необходимым слоем, (3) комментарий к PR,
оценивающий себя по чек-листу из четырёх приоритетов урока 4.</p>

<h3>Задача 4: привязка тега релиза к реальному триггеру CI (курс 117)</h3>
<p>В капстоуне курса 117 вы увидели КОНЦЕПЦИЮ <code>on: push: tags:
['v*.*.*']</code>. В уроке 11 этого курса вы увидели, как СВЯЗАТЬ это с
ANNOTATED TAG. В капстоуне объедините их: запушьте annotated tag из
Задачи 1 в реальный (или тестовый) репозиторий GitHub, и докажите
скриншотом, что workflow с триггером <code>on: push: tags</code> АКТИВНО
запустился (зелёная отметка в разделе Actions).</p>

<h3>Архитектура капстоуна: пересечение трёх курсов</h3>
<pre class="mermaid">
flowchart TB
  subgraph K112["Курс 112: внутреннее устройство Git"]
    G1["git bisect"]
    G2["pre-commit hook"]
    G3["объект annotated tag"]
  end
  subgraph K3["Этот курс: командный процесс"]
    T1["Атомарный коммит + описание PR"]
    T2["Ревью по четырём приоритетам"]
    T3["Стратегия merge + SemVer + changelog"]
    T4["Стратегия тегирования релиза"]
  end
  subgraph K117["Курс 117: CI/CD"]
    A1["Required status check"]
    A2["Триггер on: push: tags"]
  end
  G1 -->|"становится ПОЛЕЗНЫМ
с АТОМАРНЫМИ коммитами"| T1
  G2 -->|"становится двухслойной
защитой с CI"| A1
  T2 -->|"добавляет то, что CI
НЕ МОЖЕТ найти"| A1
  T3 -->|"создаётся тег
для релиза"| G3
  G3 -->|"тег пушится"| T4
  T4 -->|"запускает
триггер CI"| A2
  style K112 fill:#d6e9ff,stroke:#2266aa
  style K3 fill:#ffe9b3,stroke:#d09000
  style K117 fill:#d6f5d6,stroke:#2a8a2a
</pre>
<p>Диаграмма показывает центральную идею капстоуна: ВНУТРЕННИЕ механизмы
курса 112 (слева) через КОМАНДНЫЙ процесс этого курса (в центре) втекают
в АВТОМАТИЧЕСКИЙ pipeline курса 117 (справа). Все три курса — не
отдельные, а три части ОДНОГО целостного знания "современной командной
разработки".</p>

<h3>Почему эти четыре задачи выбраны не случайно</h3>
<p>Каждая задача связывает ТОЧНО два урока (один из другого курса, один
из этого) и показывает, что они остаются "наполовину завершёнными" ДРУГ
БЕЗ ДРУГА: bisect работает сам по себе, но его польза ограничена при
смешанных коммитах; pre-commit hook сам по себе недостаточен — без CI
остаётся "необязательным"; annotated tag сам по себе — просто данные —
пока не станет триггером деплоя, его практическая ценность ограничена;
триггер тега CI сам по себе БЕСПОЛЕЗЕН, если нет стратегии тегирования
(когда, почему тегировать). Капстоун — не "объединение трёх тем", а
демонстрация того, ПОЧЕМУ каждое знание неполно без остальных.</p>
""".strip()

L13_CODE = """
# ============================================================
# Capstone: 112 + bu kurs + 117 - to'liq zanjirni ko'rsatuvchi
# skript (kontseptual - real repo'da qo'llash uchun)
# ============================================================

# --- Vazifa 1: to'liq zanjir (bu kursning o'z darslari) ---
ATOMIC_COMMITS = [
    "fix(scoring): guard multiple_choice grading against comma-containing answers",
    "test(scoring): add regression test for comma-in-answer edge case",
]
PR_DESCRIPTION_SECTIONS = ["Kontekst", "Nima o'zgardi", "Nega aynan shu yechim", "Qanday tekshirish mumkin"]
MERGE_STRATEGY = "squash"          # 8-dars
VERSION_BUMP = ("1.0.0", "patch", "1.0.1")   # 9-dars
CHANGELOG_SECTION = "Fixed"        # 10-dars
RELEASE_TAG = "v1.0.1"             # 11-dars (annotated)

# --- Vazifa 2: bisect + atomik commit madaniyati (112-kurs) ---
# $ git bisect start
# $ git bisect bad HEAD
# $ git bisect good v1.0.0
# Git avtomatik oraliq commit'larni taklif qiladi; har birida:
# $ pytest tests/test_scoring.py -k comma_edge_case
# $ git bisect good   # yoki bad
# Natijada: "abc1234 is the first bad commit" - ANIQ bitta atomik
# commit ko'rsatiladi, aralash commit bo'lganida bu ANIQLIK yo'qolardi.

# --- Vazifa 3: uch qatlamli himoya ---
LOCAL_PRE_COMMIT_HOOK = "black --check backend/ && ruff check backend/"
CI_JOB_SAME_CHECK = \"\"\"
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install black ruff
      - run: black --check backend/ && ruff check backend/
\"\"\"
BRANCH_PROTECTION_REQUIRED_CHECK = "lint"   # 117-kurs: required status check nomi

# --- Vazifa 4: reliz tegini CI trigger'iga ulash (117-kurs) ---
RELEASE_TRIGGER_YAML = \"\"\"
on:
  push:
    tags:
      - 'v*.*.*'
\"\"\"

print("=== Capstone zanjiri ===")
print("1) Atomik commit'lar:", ATOMIC_COMMITS)
print("2) PR bo'limlari:", PR_DESCRIPTION_SECTIONS)
print("3) Merge strategiyasi:", MERGE_STRATEGY)
print("4) Versiya:", VERSION_BUMP)
print("5) Changelog bo'limi:", CHANGELOG_SECTION)
print("6) Reliz tegi:", RELEASE_TAG)
print("7) Required CI check (117-kurs):", BRANCH_PROTECTION_REQUIRED_CHECK)
print("8) Reliz trigger (117-kurs):", RELEASE_TRIGGER_YAML)
""".strip()

L13_CODE_RU = """
# ============================================================
# Капстоун: 112 + этот курс + 117 - скрипт, показывающий полную
# цепочку (концептуально - для применения в реальном репо)
# ============================================================

# --- Задача 1: полная цепочка (собственные уроки этого курса) ---
ATOMIC_COMMITS = [
    "fix(scoring): guard multiple_choice grading against comma-containing answers",
    "test(scoring): add regression test for comma-in-answer edge case",
]
PR_DESCRIPTION_SECTIONS = ["Контекст", "Что изменилось", "Почему именно это решение", "Как проверить"]
MERGE_STRATEGY = "squash"          # урок 8
VERSION_BUMP = ("1.0.0", "patch", "1.0.1")   # урок 9
CHANGELOG_SECTION = "Fixed"        # урок 10
RELEASE_TAG = "v1.0.1"             # урок 11 (annotated)

# --- Задача 2: bisect + культура атомарных коммитов (курс 112) ---
# $ git bisect start
# $ git bisect bad HEAD
# $ git bisect good v1.0.0
# Git автоматически предлагает промежуточные коммиты; на каждом:
# $ pytest tests/test_scoring.py -k comma_edge_case
# $ git bisect good   # или bad
# Результат: "abc1234 is the first bad commit" - указан ТОЧНО один
# атомарный коммит, при смешанном коммите эта ТОЧНОСТЬ была бы потеряна.

# --- Задача 3: трёхслойная защита ---
LOCAL_PRE_COMMIT_HOOK = "black --check backend/ && ruff check backend/"
CI_JOB_SAME_CHECK = \"\"\"
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install black ruff
      - run: black --check backend/ && ruff check backend/
\"\"\"
BRANCH_PROTECTION_REQUIRED_CHECK = "lint"   # курс 117: имя required status check

# --- Задача 4: привязка тега релиза к триггеру CI (курс 117) ---
RELEASE_TRIGGER_YAML = \"\"\"
on:
  push:
    tags:
      - 'v*.*.*'
\"\"\"

print("=== Цепочка капстоуна ===")
print("1) Атомарные коммиты:", ATOMIC_COMMITS)
print("2) Разделы PR:", PR_DESCRIPTION_SECTIONS)
print("3) Стратегия merge:", MERGE_STRATEGY)
print("4) Версия:", VERSION_BUMP)
print("5) Раздел changelog:", CHANGELOG_SECTION)
print("6) Тег релиза:", RELEASE_TAG)
print("7) Required CI check (курс 117):", BRANCH_PROTECTION_REQUIRED_CHECK)
print("8) Триггер релиза (курс 117):", RELEASE_TRIGGER_YAML)
""".strip()

L13_TASK = {
    "task_title": "Capstone: bitta xususiyatni to'liq jamoaviy workflow orqali yetkazing",
    "task_title_ru": "Капстоун: проведите одну фичу через полный командный workflow",
    "task_description": (
        "Shaxsiy repozitoriyangizda (yoki shu platforma fork'ida) to'rtta "
        "vazifani BAJARING: (1) kichik xususiyatni to'liq zanjir bo'yicha "
        "(atomik commit -> PR tavsifi -> o'z-o'zini review -> merge "
        "strategiyasi -> SemVer -> changelog -> annotated tag) yetkazing; "
        "(2) 5 ta atomik commit yaratib, biriga bug kiritib, git bisect "
        "orqali toping; (3) pre-commit hook + CI job orqali bir xil "
        "tekshiruvni ikki qatlamda joylashtiring; (4) annotated tegingizni "
        "push qilib, on:push:tags trigger'i ishga tushganini isbotlang."
    ),
    "task_description_ru": (
        "В своём репозитории (или форке этой платформы) ВЫПОЛНИТЕ четыре "
        "задачи: (1) проведите небольшую фичу по полной цепочке (атомарный "
        "коммит -> описание PR -> саморевью -> стратегия merge -> SemVer "
        "-> changelog -> annotated tag); (2) создайте 5 атомарных коммитов, "
        "внесите баг в один из них, найдите его через git bisect; (3) "
        "разместите одну и ту же проверку в двух слоях через pre-commit "
        "hook + CI job; (4) запушьте свой annotated tag и докажите, что "
        "триггер on:push:tags сработал."
    ),
    "task_requirements": (
        "1) Har bir 4 vazifa uchun alohida, isbotlovchi material (commit "
        "hash'lari, git bisect chiqishi, workflow fayli, Actions "
        "skrinshoti) ilova qilinishi shart. 2) Har bir vazifada ANIQ "
        "qaysi 112/117-kurs darsi va ANIQ qaysi shu kurs darsi "
        "qo'llanilganini yozing. 3) Yakuniy xulosada uchala kursning "
        "bilimlari QANDAY bir-birini TO'LDIRGANINI 3-4 gapda yozing."
    ),
    "task_requirements_ru": (
        "1) Для каждой из 4 задач приложите отдельный подтверждающий "
        "материал (хеши коммитов, вывод git bisect, файл workflow, "
        "скриншот Actions). 2) Для каждой задачи укажите, ТОЧНО какой "
        "урок курса 112/117 и ТОЧНО какой урок этого курса применён. 3) "
        "В итоговом выводе в 3-4 предложениях напишите, КАК знания всех "
        "трёх курсов ДОПОЛНИЛИ друг друга."
    ),
    "task_technologies": "Git, GitHub Actions, GitHub (Pull Requests)",
    "task_deadline_days": 7,
}

L13_SAMPLE = {
    "title": "Namuna: uch kursni birlashtiruvchi to'liq capstone zanjiri",
    "description": (
        "Ushbu darsning kod namunasi asosida, atomik commit'dan reliz "
        "tegigacha, bisect'dan uch qatlamli himoyagacha bo'lgan barcha "
        "vazifalarni birlashtirgan, izohli ko'rinish."
    ),
    "sample_type": "code",
    "code_files": [
        {"filename": "capstone_full_chain.py", "language": "python", "code": "# Qarang: L13_CODE ushbu darsning to'liq matnida"},
        {
            "filename": "release-with-lint-gate.yml",
            "language": "yaml",
            "code": (
                "name: Release Deploy (with two-layer lint gate)\n\n"
                "on:\n"
                "  push:\n"
                "    branches: [\"**\"]      # <- lint job har push'da (2-qatlam)\n"
                "  pull_request:\n"
                "    branches: [master]\n"
                "  tags:\n"
                "    - 'v*.*.*'             # <- deploy job faqat tegda\n\n"
                "jobs:\n"
                "  lint:                     # <- 112-kurs pre-commit hook'i bilan BIR XIL tekshiruv\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - run: pip install black ruff\n"
                "      - run: black --check backend/ && ruff check backend/\n\n"
                "  deploy:\n"
                "    if: startsWith(github.ref, 'refs/tags/v')\n"
                "    needs: lint\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - name: Deploy release\n"
                "        run: echo \"Deploying $GITHUB_REF_NAME\"\n"
            ),
        },
    ],
}

L13_EXERCISES = [
    {
        "title": "Bisect va atomik commit bog'liqligi",
        "title_ru": "Связь bisect и атомарного коммита",
        "description": "Capstone Vazifa 2'da bisect ANIQ bitta commit'ni ko'rsatishi uchun asosiy shart nima?",
        "description_ru": "Какое главное условие в Задаче 2 капстоуна нужно, чтобы bisect указал ТОЧНО один коммит?",
        "exercise_type": "multiple_choice",
        "options": [
            "Commit xabarlari ingliz tilida bo'lishi",
            "Har bir commit ATOMIK (bitta mustaqil o'zgarish) bo'lishi",
            "Commit'lar soni juda ko'p bo'lishi",
            "Reviewer PR'ni tez approve qilishi",
        ],
        "options_ru": [
            "Сообщения коммитов должны быть на английском",
            "Каждый коммит должен быть АТОМАРНЫМ (одно независимое изменение)",
            "Коммитов должно быть очень много",
            "Reviewer должен быстро одобрить PR",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "3-darsdagi asosiy tamoyilni eslang.",
        "hint_ru": "Вспомните главный принцип из урока 3.",
        "explanation": "Faqat atomik commit'larda bisect QAYSI o'zgarish sabab ekanini ANIQ ko'rsata oladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Uch qatlamli himoyaning tartibi",
        "title_ru": "Порядок трёхслойной защиты",
        "description": "Capstone Vazifa 3'dagi uch himoya qatlamini ODATIY ishlash tartibida joylashtiring (birinchi tekshiriladigandan oxirgigacha).",
        "description_ru": "Расположите три слоя защиты из Задачи 3 капстоуна в обычном порядке срабатывания (от первого до последнего).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Mahalliy pre-commit hook (112-kurs)",
            "CI'dagi bir xil tekshiruv (117-kurs)",
            "Inson review'i to'rt ustuvorlik bo'yicha (bu kurs)",
        ],
        "drag_items_ru": [
            "Локальный pre-commit hook (курс 112)",
            "Та же проверка в CI (курс 117)",
            "Ревью человека по четырём приоритетам (этот курс)",
        ],
        "correct_order": [
            "Mahalliy pre-commit hook (112-kurs)",
            "CI'dagi bir xil tekshiruv (117-kurs)",
            "Inson review'i to'rt ustuvorlik bo'yicha (bu kurs)",
        ],
        "hint": "Commit qilishdan oldin -> push qilingandan keyin -> PR ochilgandan keyin.",
        "hint_ru": "Перед коммитом -> после push -> после открытия PR.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Capstone'ning markaziy g'oyasi",
        "title_ru": "Центральная идея капстоуна",
        "description": "Capstone diagrammasi asosan NIMANI ko'rsatadi?",
        "description_ru": "Что в первую очередь показывает диаграмма капстоуна?",
        "exercise_type": "multiple_choice",
        "options": [
            "112, 117 va bu kurs bir-biriga bog'liq emasligini",
            "Har bir kursning bilimi qolgan ikkitasisiz to'liq emasligini",
            "Faqat 117-kurs muhimligini",
            "GitHub Actions Git'dan ustunligini",
        ],
        "options_ru": [
            "Что 112, 117 и этот курс не связаны друг с другом",
            "Что знание каждого курса неполно без двух остальных",
            "Что важен только курс 117",
            "Что GitHub Actions превосходит Git",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Darsning oxirgi bo'limidagi xulosani eslang.",
        "hint_ru": "Вспомните вывод из последнего раздела урока.",
        "explanation": "Capstone uchta bilimning bir-birini TO'LDIRISHINI, alohida emasligini ko'rsatadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Reliz trigger'ining formati",
        "title_ru": "Формат триггера релиза",
        "description": "117-kurs va 11-darsni bog'lovchi CI trigger patterni: on: push: tags: ['___'].",
        "description_ru": "Паттерн CI-триггера, связывающий курс 117 и урок 11: on: push: tags: ['___'].",
        "exercise_type": "fill_in_blank",
        "correct_answers": "v*.*.*",
        "correct_answers_ru": "v*.*.*",  # literal YAML glob pattern, identical in both
        # languages — the heuristic flags it (contains letters, no code punctuation
        # it recognizes) even though it's not natural language; set explicitly.
        "hint": "SemVer formatidagi HAR qanday v-prefiksli tegga mos keladigan glob pattern.",
        "hint_ru": "Glob-паттерн, соответствующий ЛЮБОМУ тегу с префиксом v в формате SemVer.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# LESSONS assembly
# ---------------------------------------------------------------------------

LESSONS = [
    {
        "order": 0,
        "title": "Code review nima va nima uchun kerak",
        "title_ru": "Что такое code review и зачем оно нужно",
        "points_reward": 15,
        "text_content": L0_TEXT,
        "text_content_ru": L0_TEXT_RU,
        "code_content": L0_CODE,
        "code_content_ru": L0_CODE_RU,
        "code_language": "python",
        "task": L0_TASK,
        "sample": L0_SAMPLE,
        "exercises": L0_EXERCISES,
    },
    {
        "order": 1,
        "title": "Yaxshi PR/MR tavsifi yozish",
        "title_ru": "Написание хорошего описания PR/MR",
        "points_reward": 15,
        "text_content": L1_TEXT,
        "text_content_ru": L1_TEXT_RU,
        "code_content": L1_CODE,
        "code_content_ru": L1_CODE_RU,
        "code_language": "markdown",
        "task": L1_TASK,
        "sample": L1_SAMPLE,
        "exercises": L1_EXERCISES,
    },
    {
        "order": 2,
        "title": "Commit xabarlari konventsiyasi: Conventional Commits",
        "title_ru": "Конвенция сообщений коммитов: Conventional Commits",
        "points_reward": 15,
        "text_content": L2_TEXT,
        "text_content_ru": L2_TEXT_RU,
        "code_content": L2_CODE,
        "code_content_ru": L2_CODE_RU,
        "code_language": "python",
        "task": L2_TASK,
        "sample": L2_SAMPLE,
        "exercises": L2_EXERCISES,
    },
    {
        "order": 3,
        "title": "Atomik commit'lar vs \"fix stuff\" commit'lari",
        "title_ru": "Атомарные коммиты против коммитов \"fix stuff\"",
        "points_reward": 15,
        "text_content": L3_TEXT,
        "text_content_ru": L3_TEXT_RU,
        "code_content": L3_CODE,
        "code_content_ru": L3_CODE_RU,
        "code_language": "bash",
        "task": L3_TASK,
        "sample": L3_SAMPLE,
        "exercises": L3_EXERCISES,
    },
    {
        "order": 4,
        "title": "Samarali review qilish: nimalarga e'tibor berish kerak",
        "title_ru": "Как эффективно проводить ревью: на что обращать внимание",
        "points_reward": 15,
        "text_content": L4_TEXT,
        "text_content_ru": L4_TEXT_RU,
        "code_content": L4_CODE,
        "code_content_ru": L4_CODE_RU,
        "code_language": "python",
        "task": L4_TASK,
        "sample": L4_SAMPLE,
        "exercises": L4_EXERCISES,
    },
    {
        "order": 5,
        "title": "R1 — Takrorlash: review, PR tavsifi, commit konventsiyasi, atomiklik",
        "title_ru": "R1 — Повторение: ревью, описание PR, конвенция коммитов, атомарность",
        "points_reward": 20,
        "text_content": L5_TEXT,
        "text_content_ru": L5_TEXT_RU,
        "code_content": L5_CODE,
        "code_content_ru": L5_CODE_RU,
        "code_language": "python",
        "task": L5_TASK,
        "sample": L5_SAMPLE,
        "exercises": L5_EXERCISES,
    },
    {
        "order": 6,
        "title": "Amaliy va samimiy fikr-mulohaza berish",
        "title_ru": "Как давать действенную и доброжелательную обратную связь",
        "points_reward": 15,
        "text_content": L6_TEXT,
        "text_content_ru": L6_TEXT_RU,
        "code_content": L6_CODE,
        "code_content_ru": L6_CODE_RU,
        "code_language": "python",
        "task": L6_TASK,
        "sample": L6_SAMPLE,
        "exercises": L6_EXERCISES,
    },
    {
        "order": 7,
        "title": "Fikr-mulohazani ego'siz qabul qilish va javob berish",
        "title_ru": "Принятие обратной связи и ответ на неё без эго",
        "points_reward": 15,
        "text_content": L7_TEXT,
        "text_content_ru": L7_TEXT_RU,
        "code_content": L7_CODE,
        "code_content_ru": L7_CODE_RU,
        "code_language": "python",
        "task": L7_TASK,
        "sample": L7_SAMPLE,
        "exercises": L7_EXERCISES,
    },
    {
        "order": 8,
        "title": "Merge strategiyalari: merge commit, squash, rebase-merge",
        "title_ru": "Стратегии merge: merge commit, squash, rebase-merge",
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
        "title": "Semantik versiyalash (SemVer): MAJOR.MINOR.PATCH",
        "title_ru": "Семантическое версионирование (SemVer): MAJOR.MINOR.PATCH",
        "points_reward": 15,
        "text_content": L9_TEXT,
        "text_content_ru": L9_TEXT_RU,
        "code_content": L9_CODE,
        "code_content_ru": L9_CODE_RU,
        "code_language": "python",
        "task": L9_TASK,
        "sample": L9_SAMPLE,
        "exercises": L9_EXERCISES,
    },
    {
        "order": 10,
        "title": "Changelog yuritish: qo'lda va Conventional Commits'dan avtomatik",
        "title_ru": "Ведение changelog: вручную и автоматически из Conventional Commits",
        "points_reward": 15,
        "text_content": L10_TEXT,
        "text_content_ru": L10_TEXT_RU,
        "code_content": L10_CODE,
        "code_content_ru": L10_CODE_RU,
        "code_language": "python",
        "task": L10_TASK,
        "sample": L10_SAMPLE,
        "exercises": L10_EXERCISES,
    },
    {
        "order": 11,
        "title": "Reliz teglash strategiyasi: semver teglar + CI/CD trigger",
        "title_ru": "Стратегия тегирования релиза: semver-теги + триггер CI/CD",
        "points_reward": 20,
        "text_content": L11_TEXT,
        "text_content_ru": L11_TEXT_RU,
        "code_content": L11_CODE,
        "code_content_ru": L11_CODE_RU,
        "code_language": "python",
        "task": L11_TASK,
        "sample": L11_SAMPLE,
        "exercises": L11_EXERCISES,
    },
    {
        "order": 12,
        "title": "R2 — Takrorlash: fikr-mulohaza, merge, semver, changelog, reliz",
        "title_ru": "R2 — Повторение: обратная связь, merge, semver, changelog, релиз",
        "points_reward": 20,
        "text_content": L12_TEXT,
        "text_content_ru": L12_TEXT_RU,
        "code_content": L12_CODE,
        "code_content_ru": L12_CODE_RU,
        "code_language": "python",
        "task": L12_TASK,
        "sample": L12_SAMPLE,
        "exercises": L12_EXERCISES,
    },
    {
        "order": 13,
        "title": "Capstone: xususiyatni to'liq jamoaviy workflow orqali yetkazish",
        "title_ru": "Капстоун: доведение фичи через полный командный workflow",
        "points_reward": 30,
        "text_content": L13_TEXT,
        "text_content_ru": L13_TEXT_RU,
        "code_content": L13_CODE,
        "code_content_ru": L13_CODE_RU,
        "code_language": "python",
        "task": L13_TASK,
        "sample": L13_SAMPLE,
        "exercises": L13_EXERCISES,
    },
]

# max_points = sum of lesson points_reward + all exercise points (same
# convention as courses 112/117 - no separate task scoring beyond the
# lesson's points_reward).
_lesson_points = sum(l.get("points_reward", 10) for l in LESSONS)
_exercise_points = sum(
    ex.get("points", 10) for l in LESSONS for ex in (l.get("exercises") or [])
)
COURSE["max_points"] = _lesson_points + _exercise_points
