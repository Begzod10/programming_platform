"""Intermediate Git course: internals + advanced workflow, past course 45.

Course 45 ("Git va GitHub", category_id=11, Beginner, 14 lessons) already
covers init/add/commit, .gitignore/log/diff, branch/switch/merge, GitHub/
SSH/remote/push, PR lifecycle, merge conflicts, stash/cherry-pick/amend,
rebase vs merge, reset/revert/reflog, tags/GitHub Actions intro, and a
team-workflow capstone. This course goes DEEPER and LATER: how Git actually
stores data (objects, refs, packfiles), advanced rebase/bisect, worktree,
submodules/subtrees, hooks (grounded in this repo's real
.github/workflows/*.yml), advanced conflict strategies (rerere, merge
drivers), and monorepo techniques (sparse-checkout, partial clone) grounded
in this repo's own backend/+frontend/+docs/+alembic layout.

Built with the course_builder scaffold — see course_builder/__init__.py for
the spec contract. Every lesson gets both task + sample from the start,
full UZ+RU authored here (not machine-translated), Mermaid diagrams where
pedagogically justified. is_published stays False — human review first.
"""

COURSE = {
    "title": "Git: Ichki Tuzilishi va Ilg'or Workflow",
    "description": (
        "Git va GitHub (45-kurs) asosiy amaliyotni — commit, branch, PR, "
        "konflikt, rebase — allaqachon o'rgatgan. Bu kurs xuddi shu "
        "vositaning parda ortida qanday ishlashini ochadi: obyektlar bazasi "
        "(blob/tree/commit), SHA-1 content-addressing, .git/ papkasining "
        "tuzilishi, refs va HEAD nima uchun shunchaki fayl, packfile va "
        "git gc orqali tarix qanday siqiladi. Shundan so'ng ilg'or "
        "workflow: interaktiv rebase (squash/fixup/reorder/edit/drop), "
        "git bisect orqali xatoni ikkilik qidiruv bilan topish, "
        "git worktree, submodule va subtree, real pre-commit/pre-push "
        "hook'lar (ushbu repozitoriyaning haqiqiy GitHub Actions "
        "workflow'lari bilan solishtirilgan holda), rerere va merge "
        "drayverlari, hamda katta monorepo'larda sparse-checkout va "
        "partial clone — aynan shu platformaning backend/frontend/docs/"
        "alembic tuzilishi misolida. Kurs amaliy capstone loyihasi bilan "
        "yakunlanadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 5,
    "max_points": 215,
    "category_id": 11,
    "prerequisite_course_id": 45,
    "display_order": 601,
    "is_active": True,
    "is_published": False,
}

# ---------------------------------------------------------------------------
# Lesson 0 — Git obyektlari: blob, tree, commit va SHA-1
# ---------------------------------------------------------------------------

L0_TEXT = """
<h3>Git nimani saqlaydi: o'zgarishlarni emas, holatlarni</h3>
<p>45-kursda siz <code>git commit</code> qilishni o'rgandingiz, lekin savol
qoldi: commit qilinganda Git aniq nimani saqlaydi? Ko'pchilik "Git har bir
commit uchun diff (farqni) saqlaydi" deb o'ylaydi — bu <strong>noto'g'ri</strong>.
Git har bir commit uchun butun loyihaning to'liq <em>snapshot</em>'ini
(fayllar to'plamining holatini) saqlaydi, xuddi rasmga olingandek. Diff'lar
faqat ko'rsatish uchun (<code>git diff</code>, <code>git log -p</code>) keyinroq
ikkita snapshot orasida hisoblab chiqariladi — saqlashda ular mavjud emas.
Bu dizayn qarori Git'ning tezligi va ishonchliligining sababi: har bir
snapshot mustaqil, oldingi commit'larga bog'liq emas.</p>

<h3>To'rtta obyekt turi</h3>
<p>Git ichida hamma narsa faqat to'rtta obyekt turidan iborat:</p>
<ul>
<li><strong>blob</strong> (binary large object) — bitta faylning xom kontenti.
Fayl nomi, ruxsatlar, joylashuvi blob'da SAQLANMAYDI — faqat baytlar.</li>
<li><strong>tree</strong> — bitta papkaning ro'yxati: har bir qatorda ruxsat
(mode), turi (blob yoki tree), SHA-1 va nom bor. Ichma-ich papkalar —
ichma-ich tree obyektlari.</li>
<li><strong>commit</strong> — bitta tree'ga ishora, ota commit(lar)ning
SHA-1'i, muallif, committer va xabar. E'tibor bering: commit to'g'ridan-
to'g'ri fayllarni emas, faqat BITTA tree'ni ko'rsatadi — o'sha tree esa
butun loyihaning o'sha paytdagi holatini ifodalaydi.</li>
<li><strong>tag</strong> (annotated) — bitta obyektga (odatda commit'ga)
ishora, muallif va xabar bilan; yengil (lightweight) teglar esa umuman
alohida obyekt emas, shunchaki ref.</li>
</ul>

<h3>SHA-1 va content-addressing</h3>
<p>Har bir obyektning ID'si — uning kontentidan (turi + o'lchami + mazmuni)
hisoblangan 40 belgili SHA-1 xesh. Bu <strong>content-addressable storage</strong>
deb ataladi: obyektni ID orqali emas, mazmuni orqali topasiz. Bundan ikkita
muhim natija kelib chiqadi: (1) bir xil kontentga ega ikkita fayl — hatto
turli papkalarda, turli commit'larda bo'lsa ham — bitta blob sifatida
saqlanadi (avtomatik deduplikatsiya); (2) obyekt bir bayt o'zgarsa, uning
SHA-1'i butunlay boshqa bo'ladi — shuning uchun commit tarixini "orqaga
qaytarib" o'zgartirish deyarli imkonsiz sezilmasdan: bitta eski commit
o'zgarsa, undan keyingi HAMMA commit'larning SHA-1'i ham o'zgaradi.</p>

<h3>.git/ papkasining anatomiyasi</h3>
<p>Loyihangizdagi <code>.git/</code> papkasi — butun tarix shu yerda:</p>
<ul>
<li><code>.git/objects/</code> — barcha blob/tree/commit/tag obyektlari,
SHA-1'ning birinchi 2 belgisi papka nomi, qolgan 38 belgisi fayl nomi
sifatida (masalan <code>a3/f291...</code>).</li>
<li><code>.git/refs/heads/</code> — har bir mahalliy branch uchun bitta
oddiy matn fayli, ichida commit SHA-1'i.</li>
<li><code>.git/HEAD</code> — hozir qaysi branch/commit'da turganingizni
ko'rsatuvchi bitta qator.</li>
<li><code>.git/index</code> — staging area (binary format).</li>
<li><code>.git/config</code>, <code>.git/hooks/</code>, <code>.git/logs/</code> —
loyiha sozlamalari, hook skriptlari, reflog.</li>
</ul>

<h3>Obyektlar orasidagi bog'lanish</h3>
<pre class="mermaid">
flowchart TB
  C["commit abc123
author, message, parent"] -->|"tree"| T["tree def456
(root papka)"]
  T -->|"blob"| B1["blob 9a8b7c
main.py mazmuni"]
  T -->|"tree"| T2["tree 55ee11
app/ papkasi"]
  T2 -->|"blob"| B2["blob 22cc33
models/course.py mazmuni"]
  style C fill:#d6e9ff,stroke:#2266aa
  style T fill:#ffe9b3,stroke:#d09000
  style T2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma shu platformaning haqiqiy tuzilishiga asoslangan: bitta commit
ildiz tree'ga, u esa <code>main.py</code> kabi fayllar (blob) va
<code>app/</code> kabi ichki papkalarga (o'z tree'lari bilan) ishora qiladi.
Har bir keyingi commit odatda ko'p tree/blob'ni QAYTA ISHLATADI — faqat
o'zgargan fayllar uchun yangi blob, va o'zgargan yo'l bo'ylab yangi tree
yaratiladi, qolgani eski obyektlarga ishora qilib qoladi. Shuning uchun
minglab commit bo'lsa ham, deyarli o'zgarmagan fayllar uchun obyektlar bazasi
shishib ketmaydi.</p>

<h3>Amalda: git cat-file bilan qazish</h3>
<p><code>git cat-file -t &lt;sha&gt;</code> obyekt turini, <code>git cat-file -p
&lt;sha&gt;</code> esa uning mazmunini ko'rsatadi. <code>git hash-object</code>
faylni Git obyektiga aylantirmasdan turib uning SHA-1'ini hisoblab beradi —
bu Git'ning butun modelini qo'lda takrorlash imkonini beradi va aynan shu
narsa quyidagi kod namunasida ko'rsatilgan.</p>
""".strip()

L0_TEXT_RU = """
<h3>Что хранит Git: не изменения, а состояния</h3>
<p>В курсе 45 вы научились делать <code>git commit</code>, но остался
вопрос: что именно Git сохраняет при коммите? Многие думают "Git хранит
diff (разницу) для каждого коммита" — это <strong>неверно</strong>. Git
хранит для каждого коммита полный <em>snapshot</em> (состояние всего набора
файлов проекта), как фотографию. Diff'ы вычисляются только для показа
(<code>git diff</code>, <code>git log -p</code>) между двумя снимками позже —
при хранении их не существует. Это архитектурное решение — причина
скорости и надёжности Git: каждый снимок независим и не зависит от
предыдущих коммитов.</p>

<h3>Четыре типа объектов</h3>
<p>Внутри Git всё состоит только из четырёх типов объектов:</p>
<ul>
<li><strong>blob</strong> (binary large object) — сырое содержимое одного
файла. Имя файла, права доступа, расположение в blob НЕ хранятся — только
байты.</li>
<li><strong>tree</strong> — список одной папки: в каждой строке права
(mode), тип (blob или tree), SHA-1 и имя. Вложенные папки — вложенные
объекты tree.</li>
<li><strong>commit</strong> — указывает на один tree, SHA-1 родительского
коммита(-ов), автора, коммиттера и сообщение. Обратите внимание: коммит
указывает не напрямую на файлы, а только на ОДИН tree — а этот tree
представляет состояние всего проекта на тот момент.</li>
<li><strong>tag</strong> (annotated) — указывает на один объект (обычно
commit) с автором и сообщением; лёгкие (lightweight) теги вообще не
отдельный объект, а просто ref.</li>
</ul>

<h3>SHA-1 и content-addressing</h3>
<p>ID каждого объекта — это 40-символьный SHA-1 хеш, вычисленный из его
содержимого (тип + размер + содержимое). Это называется
<strong>content-addressable storage</strong>: объект находится не по ID, а
по своему содержимому. Отсюда два важных следствия: (1) два файла с
одинаковым содержимым — даже в разных папках, разных коммитах — хранятся
как один blob (автоматическая дедупликация); (2) если в объекте меняется
хотя бы один байт, его SHA-1 становится полностью другим — поэтому
незаметно изменить историю коммитов "задним числом" практически
невозможно: если меняется один старый коммит, меняются SHA-1 ВСЕХ
последующих коммитов.</p>

<h3>Анатомия папки .git/</h3>
<p>Папка <code>.git/</code> вашего проекта — вся история здесь:</p>
<ul>
<li><code>.git/objects/</code> — все объекты blob/tree/commit/tag, первые 2
символа SHA-1 — имя папки, оставшиеся 38 — имя файла (например
<code>a3/f291...</code>).</li>
<li><code>.git/refs/heads/</code> — для каждой локальной ветки один обычный
текстовый файл, внутри — SHA-1 коммита.</li>
<li><code>.git/HEAD</code> — одна строка, показывающая, на какой ветке/
коммите вы сейчас находитесь.</li>
<li><code>.git/index</code> — staging area (бинарный формат).</li>
<li><code>.git/config</code>, <code>.git/hooks/</code>, <code>.git/logs/</code> —
настройки проекта, скрипты hook, reflog.</li>
</ul>

<h3>Связь между объектами</h3>
<pre class="mermaid">
flowchart TB
  C["commit abc123
author, message, parent"] -->|"tree"| T["tree def456
(корневая папка)"]
  T -->|"blob"| B1["blob 9a8b7c
содержимое main.py"]
  T -->|"tree"| T2["tree 55ee11
папка app/"]
  T2 -->|"blob"| B2["blob 22cc33
содержимое models/course.py"]
  style C fill:#d6e9ff,stroke:#2266aa
  style T fill:#ffe9b3,stroke:#d09000
  style T2 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма основана на реальной структуре этой платформы: один коммит
указывает на корневой tree, тот — на файлы (blob), такие как
<code>main.py</code>, и на внутренние папки (со своими tree), такие как
<code>app/</code>. Каждый следующий коммит обычно ПЕРЕИСПОЛЬЗУЕТ множество
tree/blob — новый blob создаётся только для изменённых файлов, новый tree —
только вдоль изменённого пути, остальное ссылается на старые объекты.
Поэтому даже при тысячах коммитов база объектов не раздувается для файлов,
которые почти не меняются.</p>

<h3>На практике: раскопки через git cat-file</h3>
<p><code>git cat-file -t &lt;sha&gt;</code> показывает тип объекта,
<code>git cat-file -p &lt;sha&gt;</code> — его содержимое.
<code>git hash-object</code> вычисляет SHA-1 файла, не превращая его в
объект Git — это позволяет вручную повторить всю модель Git, что и
показано в примере кода ниже.</p>
""".strip()

L0_CODE = """
# ============================================================
# 1) .git/ papkasini birinchi marta ko'rish
# ============================================================
$ git init sandbox && cd sandbox
$ echo "salom dunyo" > hello.txt
$ ls -la .git/
# HEAD  config  description  hooks/  info/  objects/  refs/
$ cat .git/HEAD
ref: refs/heads/main
# HEAD hali hech qanday branch fayliga ishora qilmaydi, chunki
# refs/heads/main hali yaratilmagan — birinchi commit'gacha.

# ============================================================
# 2) Blob'ni qo'lda yaratish — git add'siz
# ============================================================
$ git hash-object -w hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
# -w kaliti obyektni HAQIQATDA .git/objects/ ichiga yozadi.
# Bu SHA-1 faqat "blob 12\\0salom dunyo\\n" kontentidan hisoblangan —
# fayl nomi "hello.txt" bu hisoblashda umuman ishtirok etmaydi!

$ git cat-file -t 5a3d0b3
blob
$ git cat-file -p 5a3d0b3
salom dunyo

# ============================================================
# 3) Ikkita bir xil fayl — bitta blob (deduplikatsiya)
# ============================================================
$ mkdir -p a b
$ echo "salom dunyo" > a/hello.txt
$ echo "salom dunyo" > b/hello.txt
$ git hash-object a/hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
$ git hash-object b/hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
# Ikkalasi AYNAN bir xil SHA-1 — Git ikkalasi uchun BITTA blob saqlaydi,
# ikki marta emas. Kontent bir xil bo'lsa, joylashuv muhim emas.

# ============================================================
# 4) Tree'ni qo'lda qurish
# ============================================================
$ git update-index --add --cacheinfo 100644 5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f hello.txt
$ git write-tree
def4567890abcdef1234567890abcdef12345678
$ git cat-file -p def4567
100644 blob 5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f    hello.txt
# Tree — mode + turi + SHA-1 + nom ro'yxati. Nom AYNAN shu yerda saqlanadi,
# blob'da emas — shuning uchun bir xil blob turli nomlar bilan turli
# tree'larda ishlatilishi mumkin.

# ============================================================
# 5) Commit'ni qo'lda qurish
# ============================================================
$ echo "Birinchi commit" | git commit-tree def4567890abcdef1234567890abcdef12345678
abc123def4567890abcdef1234567890abcdef12
$ git cat-file -p abc123d
tree def4567890abcdef1234567890abcdef12345678
author Ism Familiya <email@example.com> 1700000000 +0500
committer Ism Familiya <email@example.com> 1700000000 +0500

Birinchi commit
# E'tibor bering: bu yerda "parent" qatori YO'Q — bu ILDIZ commit.
# Ikkinchi commit qo'shilsa, u "parent abc123d..." qatoriga ega bo'ladi.

# ============================================================
# 6) Bitta bayt o'zgarsa — butunlay boshqa SHA-1
# ============================================================
$ echo "salom dunyo!" > hello.txt   # oxiriga "!" qo'shildi
$ git hash-object hello.txt
f19e02c4a8b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3
# Butunlay boshqa xesh — birgina belgi ham butun SHA-1'ni o'zgartiradi.
# Shu sababli tarixni "orqaga qaytarib tuzatish" darhol sezilib qoladi:
# o'sha commit'dan keyingi HAR BIR commit'ning SHA-1'i ham o'zgaradi.

# ============================================================
# 7) refs/heads/ — branch shunchaki fayl ekanini isbotlash
# ============================================================
$ mkdir -p .git/refs/heads
$ echo "abc123def4567890abcdef1234567890abcdef12" > .git/refs/heads/main
$ cat .git/refs/heads/main
abc123def4567890abcdef1234567890abcdef12
$ git log --oneline
abc123d Birinchi commit
# Endi "main" branch mavjud — biz uni git branch orqali EMAS, oddiy
# `echo` bilan fayl yozib yaratdik. Keyingi darsda buni chuqurroq ko'ramiz.

# ============================================================
# 8) Real loyihada obyektlarni ko'rish
# ============================================================
$ cd /home/user/student_platform
$ git cat-file -p HEAD
tree 7c9e6b4a3d2f1e0c9b8a7d6e5f4a3b2c1d0e9f8a
parent 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
author Dev <dev@example.com> 1706000000 +0500
committer Dev <dev@example.com> 1706000000 +0500

fix: backend/app/models/course.py validatsiya xatosi

$ git cat-file -p 7c9e6b4 | grep app
040000 tree 55ee1122334455667788990011223344556677  backend
$ git cat-file -p 55ee112 | grep app
040000 tree 99aa88bb77cc66dd55ee44ff33gg22hh11ii00jj  app

# ============================================================
# 9) Annotated tag obyekti — to'rtinchi obyekt turi
# ============================================================
$ git tag -a v1.0.0 -m "Birinchi barqaror reliz"
$ git cat-file -t v1.0.0
tag
$ git cat-file -p v1.0.0
object abc123def4567890abcdef1234567890abcdef12
type commit
tag v1.0.0
tagger Ism Familiya <email@example.com> 1706000000 +0500

Birinchi barqaror reliz
# E'tibor bering: tag OBYEKTI commit'ga emas, balki O'ZI alohida obyekt —
# "object" qatori orqali commit'ga ishora qiladi. Yengil (lightweight) teg
# esa umuman bunday obyekt yaratmaydi, faqat oddiy ref (0-darsdagi
# refs/heads/ kabi, lekin refs/tags/ ostida).

$ ls .git/refs/tags/
v1.0.0
$ cat .git/refs/tags/v1.0.0
9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d6
# Bu — annotated tag OBYEKTINING SHA-1'i, commit'ning o'zi EMAS.

# ============================================================
# 10) git fsck — butun obyektlar bazasining yaxlitligini tekshirish
# ============================================================
$ git fsck --full
Checking object directories: 100% (256/256), done.
Checking objects: 100% (52/52), done.
# Muammo bo'lmasa hech qanday xato chiqmaydi. Agar disk buzilib, bitta
# obyekt korruptsiyaga uchrasa:
$ git fsck --full
error: hash mismatch for .git/objects/9f/8e7d6c... (expected 9f8e7d6c...)
# Bu SHA-1'ning content-addressing xususiyati tufayli mumkin bo'lgan
# tekshiruv — agar bayt korruptsiyaga uchrasa, xesh mos kelmay qoladi,
# demak muammo DARHOL aniqlanadi (0-darsdagi "bir bayt o'zgarsa, butun
# SHA-1 o'zgaradi" qoidasi shu yerda amaliy foyda beradi).
""".strip()

L0_CODE_RU = """
# ============================================================
# 1) Первый взгляд на папку .git/
# ============================================================
$ git init sandbox && cd sandbox
$ echo "hello world" > hello.txt
$ ls -la .git/
# HEAD  config  description  hooks/  info/  objects/  refs/
$ cat .git/HEAD
ref: refs/heads/main
# HEAD ещё не указывает ни на какой файл ветки, потому что
# refs/heads/main ещё не создан — до первого коммита.

# ============================================================
# 2) Создание blob вручную — без git add
# ============================================================
$ git hash-object -w hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
# Ключ -w РЕАЛЬНО записывает объект внутрь .git/objects/.
# Этот SHA-1 вычислен только из содержимого "blob 12\\0hello world\\n" —
# имя файла "hello.txt" вообще НЕ участвует в этом вычислении!

$ git cat-file -t 5a3d0b3
blob
$ git cat-file -p 5a3d0b3
hello world

# ============================================================
# 3) Два одинаковых файла — один blob (дедупликация)
# ============================================================
$ mkdir -p a b
$ echo "hello world" > a/hello.txt
$ echo "hello world" > b/hello.txt
$ git hash-object a/hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
$ git hash-object b/hello.txt
5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f
# У обоих АБСОЛЮТНО одинаковый SHA-1 — Git хранит ОДИН blob для обоих,
# а не два раза. При одинаковом содержимом расположение не важно.

# ============================================================
# 4) Ручное построение tree
# ============================================================
$ git update-index --add --cacheinfo 100644 5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f hello.txt
$ git write-tree
def4567890abcdef1234567890abcdef12345678
$ git cat-file -p def4567
100644 blob 5a3d0b3e6e6b0b3f5e9c8a1d2e4f6a7b8c9d0e1f    hello.txt
# Tree — это список mode + тип + SHA-1 + имя. Имя хранится ИМЕННО здесь,
# а не в blob — поэтому один и тот же blob может использоваться под
# разными именами в разных tree.

# ============================================================
# 5) Ручное построение commit
# ============================================================
$ echo "Первый коммит" | git commit-tree def4567890abcdef1234567890abcdef12345678
abc123def4567890abcdef1234567890abcdef12
$ git cat-file -p abc123d
tree def4567890abcdef1234567890abcdef12345678
author Имя Фамилия <email@example.com> 1700000000 +0500
committer Имя Фамилия <email@example.com> 1700000000 +0500

Первый коммит
# Обратите внимание: здесь НЕТ строки "parent" — это КОРНЕВОЙ коммит.
# Когда добавится второй коммит, у него появится строка "parent abc123d...".

# ============================================================
# 6) Один изменённый байт — совсем другой SHA-1
# ============================================================
$ echo "hello world!" > hello.txt   # добавлен "!" в конце
$ git hash-object hello.txt
f19e02c4a8b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3
# Совершенно другой хеш — даже один символ меняет весь SHA-1.
# Поэтому "исправить" историю задним числом сразу заметно:
# у КАЖДОГО коммита после этого меняется SHA-1.

# ============================================================
# 7) refs/heads/ — доказательство, что ветка это просто файл
# ============================================================
$ mkdir -p .git/refs/heads
$ echo "abc123def4567890abcdef1234567890abcdef12" > .git/refs/heads/main
$ cat .git/refs/heads/main
abc123def4567890abcdef1234567890abcdef12
$ git log --oneline
abc123d Первый коммит
# Теперь ветка "main" существует — мы создали её НЕ через git branch,
# а обычной командой `echo`, записав файл. Подробнее в следующем уроке.

# ============================================================
# 8) Просмотр объектов в реальном проекте
# ============================================================
$ cd /home/user/student_platform
$ git cat-file -p HEAD
tree 7c9e6b4a3d2f1e0c9b8a7d6e5f4a3b2c1d0e9f8a
parent 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
author Dev <dev@example.com> 1706000000 +0500
committer Dev <dev@example.com> 1706000000 +0500

fix: ошибка валидации в backend/app/models/course.py

$ git cat-file -p 7c9e6b4 | grep app
040000 tree 55ee1122334455667788990011223344556677  backend
$ git cat-file -p 55ee112 | grep app
040000 tree 99aa88bb77cc66dd55ee44ff33gg22hh11ii00jj  app

# ============================================================
# 9) Объект annotated tag — четвёртый тип объекта
# ============================================================
$ git tag -a v1.0.0 -m "Первый стабильный релиз"
$ git cat-file -t v1.0.0
tag
$ git cat-file -p v1.0.0
object abc123def4567890abcdef1234567890abcdef12
type commit
tag v1.0.0
tagger Имя Фамилия <email@example.com> 1706000000 +0500

Первый стабильный релиз
# Обратите внимание: объект тега указывает не на дерево, а на COMMIT —
# через строку "object". Лёгкий (lightweight) тег вообще не создаёт
# такого объекта, это просто ref (как refs/heads/ из урока 0, но под
# refs/tags/).

$ ls .git/refs/tags/
v1.0.0
$ cat .git/refs/tags/v1.0.0
9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d6
# Это SHA-1 ОБЪЕКТА annotated tag, а не самого коммита.

# ============================================================
# 10) git fsck — проверка целостности всей базы объектов
# ============================================================
$ git fsck --full
Checking object directories: 100% (256/256), done.
Checking objects: 100% (52/52), done.
# Если проблем нет, ошибок не будет. Если диск повреждён и один объект
# подвергся коррупции:
$ git fsck --full
error: hash mismatch for .git/objects/9f/8e7d6c... (expected 9f8e7d6c...)
# Это проверка, возможная благодаря свойству content-addressing SHA-1 —
# если байт повреждён, хеш не совпадёт, значит проблема обнаруживается
# СРАЗУ (правило из урока 0 "один изменённый байт — другой SHA-1" здесь
# приносит практическую пользу).
""".strip()

L0_TASK = {
    "task_title": "O'zingizning obyektlar bazangizni qo'lda quring",
    "task_title_ru": "Постройте свою базу объектов вручную",
    "task_description": (
        "Bo'sh papkada `git init` bilan yangi repo yarating. `git "
        "hash-object -w`, `git update-index --add --cacheinfo`, `git "
        "write-tree` va `git commit-tree` buyruqlaridan FOYDALANIB, "
        "`git add`/`git commit` ishlatmasdan, kamida 2 ta faylli va 2 ta "
        "commit'li tarixni qo'lda yarating (ikkinchi commit birinchisini "
        "`parent` sifatida ko'rsatishi kerak). Har bir qadamda "
        "`git cat-file -p` chiqishini hisobotga kiriting."
    ),
    "task_description_ru": (
        "Создайте новый репозиторий через `git init` в пустой папке. "
        "Используя команды `git hash-object -w`, `git update-index "
        "--add --cacheinfo`, `git write-tree` и `git commit-tree` — БЕЗ "
        "`git add`/`git commit` — вручную создайте историю минимум с 2 "
        "файлами и 2 коммитами (второй коммит должен указывать на первый "
        "как на `parent`). Включите в отчёт вывод `git cat-file -p` для "
        "каждого шага."
    ),
    "task_requirements": (
        "1) `.git/objects/` ichida kamida 2 ta blob, 2 ta tree, 2 ta "
        "commit obyekti mavjudligini `find .git/objects -type f` bilan "
        "isbotlang. 2) Ikkinchi commit'ning `git cat-file -p` chiqishida "
        "`parent` qatori bo'lishi shart. 3) `.git/refs/heads/main` "
        "faylini qo'lda yozib, `git log --oneline` ishlashini ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Докажите через `find .git/objects -type f`, что в "
        "`.git/objects/` есть минимум 2 blob, 2 tree, 2 commit. 2) Вывод "
        "`git cat-file -p` для второго коммита должен содержать строку "
        "`parent`. 3) Вручную запишите файл `.git/refs/heads/main` и "
        "покажите, что `git log --oneline` работает."
    ),
    "task_technologies": "Git plumbing commands (hash-object, write-tree, commit-tree)",
    "task_deadline_days": 3,
}

L0_SAMPLE = {
    "title": "Namuna: qo'lda 2-commitli tarix qurish skripti",
    "description": (
        "Bash skripti — `git add`/`git commit` ishlatmasdan, faqat "
        "plumbing buyruqlar bilan ikkita fayl va ikkita bog'langan "
        "commit'dan iborat tarix quradi, so'ngra har bir obyektni "
        "`cat-file` orqali tekshiradi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "build_history.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf sandbox && mkdir sandbox && cd sandbox\n"
                "git init -q\n\n"
                "echo \"birinchi qator\" > readme.txt\n"
                "BLOB1=$(git hash-object -w readme.txt)\n"
                "git update-index --add --cacheinfo 100644 \"$BLOB1\" readme.txt\n"
                "TREE1=$(git write-tree)\n"
                "COMMIT1=$(echo \"boshlang'ich commit\" | git commit-tree \"$TREE1\")\n"
                "echo \"1-commit: $COMMIT1 (tree $TREE1, blob $BLOB1)\"\n\n"
                "echo \"ikkinchi qator qo'shildi\" >> readme.txt\n"
                "BLOB2=$(git hash-object -w readme.txt)\n"
                "git update-index --add --cacheinfo 100644 \"$BLOB2\" readme.txt\n"
                "TREE2=$(git write-tree)\n"
                "COMMIT2=$(echo \"ikkinchi qator qo'shildi\" | git commit-tree \"$TREE2\" -p \"$COMMIT1\")\n"
                "echo \"2-commit: $COMMIT2 (tree $TREE2, blob $BLOB2, parent $COMMIT1)\"\n\n"
                "mkdir -p .git/refs/heads\n"
                "echo \"$COMMIT2\" > .git/refs/heads/main\n\n"
                "echo \"--- git log natijasi ---\"\n"
                "git log --oneline\n\n"
                "echo \"--- obyektlar soni ---\"\n"
                "find .git/objects -type f | wc -l\n"
            ),
        },
        {
            "filename": "inspect.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "# Har bir obyekt turini va mazmunini ko'rsatadi.\n"
                "set -euo pipefail\n"
                "for sha in $(git rev-list --objects --all | awk '{print $1}'); do\n"
                "    type=$(git cat-file -t \"$sha\")\n"
                "    echo \"$sha [$type]\"\n"
                "    git cat-file -p \"$sha\" | sed 's/^/    /'\n"
                "    echo \"---\"\n"
                "done\n"
            ),
        },
    ],
}

L0_EXERCISES = [
    {
        "title": "Git nimani saqlaydi?",
        "title_ru": "Что хранит Git?",
        "description": "Har bir commit uchun Git aslida nimani saqlaydi?",
        "description_ru": "Что на самом деле хранит Git для каждого коммита?",
        "exercise_type": "multiple_choice",
        "options": [
            "Loyihaning to'liq snapshot'ini (tree orqali)",
            "Oldingi commit'ga nisbatan diff'ni",
            "Faqat o'zgargan fayllar ro'yxatini, kontentsiz",
            "Faylning binary patch'ini",
        ],
        "options_ru": [
            "Полный snapshot проекта (через tree)",
            "Diff относительно предыдущего коммита",
            "Только список изменённых файлов, без содержимого",
            "Бинарный patch файла",
        ],
        "correct_answers": "A",
        "hint": "Commit bitta tree'ga ishora qiladi, tree esa butun holatni ifodalaydi.",
        "hint_ru": "Коммит указывает на один tree, а tree представляет всё состояние.",
        "explanation": "Git diff'larni faqat ko'rsatish uchun hisoblaydi; saqlashda har commit to'liq snapshot.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Obyektlarni qo'lda yaratish tartibi",
        "title_ru": "Порядок ручного создания объектов",
        "description": "Plumbing buyruqlar bilan yangi commit yaratishning to'g'ri tartibini joylashtiring.",
        "description_ru": "Расположите правильный порядок создания нового коммита через plumbing-команды.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git hash-object -w bilan blob yaratish",
            "git update-index --add --cacheinfo bilan indeksga qo'shish",
            "git write-tree bilan tree yaratish",
            "git commit-tree bilan commit yaratish",
        ],
        "drag_items_ru": [
            "Создать blob через git hash-object -w",
            "Добавить в индекс через git update-index --add --cacheinfo",
            "Создать tree через git write-tree",
            "Создать commit через git commit-tree",
        ],
        "correct_order": [
            "git hash-object -w bilan blob yaratish",
            "git update-index --add --cacheinfo bilan indeksga qo'shish",
            "git write-tree bilan tree yaratish",
            "git commit-tree bilan commit yaratish",
        ],
        "hint": "Avval kontent (blob), keyin ro'yxat (tree), oxirida ishora (commit).",
        "hint_ru": "Сначала содержимое (blob), затем список (tree), в конце указатель (commit).",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Content-addressing atamasi",
        "title_ru": "Термин content-addressing",
        "description": "Git obyektining ID'si uning joylashuvi emas, balki uning ___ orqali hisoblanadi.",
        "description_ru": "ID объекта Git вычисляется не по его расположению, а по его ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "kontenti",
        "correct_answers_ru": "содержимому",
        "hint": "SHA-1 nimadan hisoblanadi — fayl nomidanmi yoki ichidagi baytlardanmi?",
        "hint_ru": "Из чего вычисляется SHA-1 — из имени файла или из байтов внутри?",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 1 — Refs, HEAD, branch'lar — yengil ko'rsatkichlar
# ---------------------------------------------------------------------------

L1_TEXT = """
<h3>Branch — bu ma'lumot tuzilmasi emas, bitta fayl</h3>
<p>0-darsda siz commit'larni qo'lda yaratib, <code>.git/refs/heads/main</code>
faylini o'zingiz yozdingiz. Bu tasodifiy misol emas edi — aynan shu Git'da
branch'ning HAQIQIY ta'rifi: <strong>branch — 40 baytlik commit SHA-1'ini
o'zida saqlagan oddiy matn fayli</strong>, boshqa hech narsa emas. Bu bilan
taqqoslang: ba'zi eski versiya-nazorat tizimlarida (masalan Subversion)
branch yaratish butun loyiha nusxasini boshqa papkaga ko'chirishni anglatadi
— bu operatsiya sekin va qimmat. Git'da <code>git branch feature-x</code>
buyrug'i shunchaki 41 baytlik (40 belgi + yangi qator) bitta faylni yozadi.</p>

<h3>Nega branch yaratish O(1) — hajmdan qat'iy nazar</h3>
<p>Loyihada 10 ta commit bo'ladimi, 10 000 tami — farqi yo'q: yangi branch
yaratish har doim bitta fayl yozish, ya'ni doimiy vaqt <strong>O(1)</strong>.
Buning sababi — branch commit tarixining nusxasini emas, faqat BITTA
ko'rsatkichni saqlaydi. Tarixning o'zi allaqachon obyektlar bazasida mavjud
(0-darsda ko'rganingizdek) va u branch'lar orasida ULASHILADI — ikkita
branch bir xil eski commit'larga ishora qilsa, ular bitta obyekt nusxasini
baham ko'radi, ikkitasini emas.</p>

<h3>HEAD — "men hozir qayerdaman"</h3>
<p><code>.git/HEAD</code> fayli odatda commit SHA-1'ini emas, balki BOSHQA
ref'ga ishorani saqlaydi: <code>ref: refs/heads/main</code>. Bu bilvosita
darajasi muhim: <code>git commit</code> qilganingizda Git (1) yangi commit
obyektini yaratadi, (2) HEAD qaysi ref'ga ishora qilsa, o'sha ref faylini
yangi commit SHA-1'i bilan yangilaydi. Agar HEAD to'g'ridan-to'g'ri commit
SHA-1'iga ishora qilsa (ref'ga emas), bu <strong>detached HEAD</strong> holati
— branch yo'q, shuning uchun keyingi commit hech qanday branch'ni
yangilamaydi va oson yo'qolib qolishi mumkin (reflog orqali qutqarish
mumkin bo'lsa ham).</p>

<h3>git switch/checkout aslida nima qiladi</h3>
<p><code>git switch feature-x</code> uchta narsani bajaradi: (1) HEAD
faylini <code>ref: refs/heads/feature-x</code> ga yangilaydi, (2) index'ni
o'sha branch commit'ining tree'siga mos qiladi, (3) working directory
fayllarini shu tree'dagi blob'lar bilan almashtiradi. Bu — nusxalash emas,
FAQAT ko'rsatkichni almashtirib, keyin fayllarni sinxronlash. Shu sababli
katta loyihada ham branch almashtirish soniyalar ichida bo'ladi (agar ikki
branch orasida farq katta bo'lmasa).</p>

<h3>packed-refs — ko'p branch/tag bo'lganda optimallashtirish</h3>
<p>Yuzlab branch/tag bo'lgan repo'da har biri uchun alohida fayl o'qish
sekinlashishi mumkin, shuning uchun Git ba'zan <code>.git/packed-refs</code>
degan bitta faylga ko'p ref'ni siqadi (odatda <code>git gc</code> paytida).
Muhim nuqta: agar bir xil ref ham <code>refs/heads/</code> papkasida, ham
<code>packed-refs</code> ichida bo'lsa, "loose" (alohida fayl) versiyasi
DOIM ustunlik qiladi — bu yangi commit qilinganda birinchi yangilanadigan
joy.</p>

<h3>Branch'lar va commit grafigi</h3>
<pre class="mermaid">
flowchart LR
  subgraph refs [".git/refs/heads/"]
    M["main -> c3"]
    F["feature-x -> c2"]
  end
  H["HEAD -> refs/heads/feature-x"] -.-> F
  c1["c1"] --> c2["c2"] --> c3["c3"]
  F -.->|"ishora"| c2
  M -.->|"ishora"| c3
  style H fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma shuni ko'rsatadi: <code>main</code> va <code>feature-x</code> —
bir xil commit grafigidagi ikki xil nuqtaga ishora qiluvchi ikkita alohida
fayl, HEAD esa hozir qaysi ref'ga (demak, qaysi branch'ga) ishora
qilinayotganini bildiradi. Commit grafigining o'zi branch'lardan mustaqil
mavjud — branch'lar shunchaki unga "yorliqlar".</p>

<h3>git symbolic-ref — HEAD bilan bevosita ishlash</h3>
<p><code>git switch</code> ichki jarayonini qo'lda takrorlash uchun
<code>git symbolic-ref HEAD refs/heads/feature-x</code> buyrug'i bor —
bu aynan <code>.git/HEAD</code> fayliga <code>ref: refs/heads/feature-x</code>
matnini yozadi, xuddi siz buni <code>echo</code> bilan qilganingizdek.
Farqi shundaki, <code>symbolic-ref</code> ref'ning haqiqatda mavjudligini
va to'g'ri formatda ekanligini tekshiradi — xavfsizroq usul.</p>

<h3>Reflog — refs o'zgarishlari tarixi</h3>
<p>Har safar biror ref (masalan <code>HEAD</code> yoki <code>refs/heads/
main</code>) yangilanganda, Git bu voqeani <code>.git/logs/</code> ichidagi
mos faylga (masalan <code>.git/logs/HEAD</code>) bitta qator sifatida
qo'shib boradi: eski SHA-1, yangi SHA-1, sabab (commit, checkout, rebase,
va h.k.). <code>git reflog</code> buyrug'i aynan shu faylni o'qib
ko'rsatadi. Bu 0-darsda ko'rgan "obyektlar abadiy saqlanadi" tamoyilidan
FARQ qiladi — reflog vaqt o'tishi bilan (odatda 90 kun) eskirgan
yozuvlarni tozalaydi, va faqat MAHALLIY repo'da mavjud, hech qachon
push/clone qilinmaydi.</p>
""".strip()

L1_TEXT_RU = """
<h3>Ветка — не структура данных, а один файл</h3>
<p>В уроке 0 вы вручную создавали коммиты и сами записывали файл
<code>.git/refs/heads/main</code>. Это был не случайный пример — именно
таково НАСТОЯЩЕЕ определение ветки в Git: <strong>ветка — это обычный
текстовый файл, хранящий 40-байтный SHA-1 коммита</strong>, и больше
ничего. Сравните: в некоторых старых системах контроля версий (например
Subversion) создание ветки означает копирование всего проекта в другую
папку — эта операция медленная и дорогая. В Git команда <code>git branch
feature-x</code> просто записывает один файл размером 41 байт (40 символов
+ перевод строки).</p>

<h3>Почему создание ветки — O(1), независимо от размера</h3>
<p>Неважно, 10 коммитов в проекте или 10 000 — создание новой ветки всегда
запись одного файла, то есть постоянное время <strong>O(1)</strong>.
Причина — ветка хранит не копию истории коммитов, а только ОДИН
указатель. Сама история уже существует в базе объектов (как вы видели в
уроке 0) и она РАЗДЕЛЯЕТСЯ между ветками — если две ветки указывают на
одни и те же старые коммиты, они используют одну копию объекта, а не
две.</p>

<h3>HEAD — "где я сейчас нахожусь"</h3>
<p>Файл <code>.git/HEAD</code> обычно хранит не SHA-1 коммита, а указатель
на ДРУГОЙ ref: <code>ref: refs/heads/main</code>. Этот уровень косвенности
важен: при <code>git commit</code> Git (1) создаёт новый объект коммита,
(2) обновляет файл ref, на который указывает HEAD, новым SHA-1 коммита.
Если HEAD указывает напрямую на SHA-1 коммита (а не на ref) — это
состояние <strong>detached HEAD</strong> — ветки нет, поэтому следующий
коммит не обновит никакую ветку и легко может "потеряться" (хотя его
можно спасти через reflog).</p>

<h3>Что на самом деле делает git switch/checkout</h3>
<p><code>git switch feature-x</code> выполняет три действия: (1) обновляет
файл HEAD на <code>ref: refs/heads/feature-x</code>, (2) приводит index в
соответствие с tree коммита этой ветки, (3) заменяет файлы рабочей
директории на blob'ы из этого tree. Это не копирование, а ТОЛЬКО замена
указателя с последующей синхронизацией файлов. Поэтому даже в большом
проекте переключение веток занимает секунды (если разница между двумя
ветками не огромна).</p>

<h3>packed-refs — оптимизация при множестве веток/тегов</h3>
<p>При сотнях веток/тегов чтение отдельного файла для каждой может
замедлиться, поэтому Git иногда сжимает много ref в один файл
<code>.git/packed-refs</code> (обычно во время <code>git gc</code>). Важный
момент: если один и тот же ref есть и в <code>refs/heads/</code>, и в
<code>packed-refs</code>, версия "loose" (отдельный файл) ВСЕГДА имеет
приоритет — это первое место, которое обновляется при новом коммите.</p>

<h3>Ветки и граф коммитов</h3>
<pre class="mermaid">
flowchart LR
  subgraph refs [".git/refs/heads/"]
    M["main -> c3"]
    F["feature-x -> c2"]
  end
  H["HEAD -> refs/heads/feature-x"] -.-> F
  c1["c1"] --> c2["c2"] --> c3["c3"]
  F -.->|"указывает"| c2
  M -.->|"указывает"| c3
  style H fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает: <code>main</code> и <code>feature-x</code> — два
отдельных файла, указывающих на разные точки одного графа коммитов, а
HEAD показывает, на какой ref (значит, на какую ветку) указывает сейчас.
Сам граф коммитов существует независимо от веток — ветки лишь "ярлыки" к
нему.</p>

<h3>git symbolic-ref — прямая работа с HEAD</h3>
<p>Чтобы вручную повторить внутренний процесс <code>git switch</code>,
есть команда <code>git symbolic-ref HEAD refs/heads/feature-x</code> —
она записывает в файл <code>.git/HEAD</code> именно текст <code>ref:
refs/heads/feature-x</code>, как если бы вы сделали это через
<code>echo</code>. Разница в том, что <code>symbolic-ref</code> проверяет
реальное существование ref и правильность формата — более безопасный
способ.</p>

<h3>Reflog — история изменений refs</h3>
<p>Каждый раз, когда какой-либо ref (например <code>HEAD</code> или
<code>refs/heads/main</code>) обновляется, Git добавляет это событие
строкой в соответствующий файл внутри <code>.git/logs/</code> (например
<code>.git/logs/HEAD</code>): старый SHA-1, новый SHA-1, причина
(commit, checkout, rebase и т.д.). Команда <code>git reflog</code> просто
читает и показывает этот файл. Это ОТЛИЧАЕТСЯ от принципа "объекты
хранятся вечно" из урока 0 — reflog со временем (обычно 90 дней) очищает
устаревшие записи, и существует только в ЛОКАЛЬНОМ репозитории, никогда
не push/clone'ится.</p>
""".strip()

L1_CODE = """
# ============================================================
# 1) Branch yaratishning "haqiqiy" narxi
# ============================================================
$ time git branch big-history-branch
real    0m0.003s   # 10 000 commit bo'lsa ham natija shu — O(1)

$ cat .git/refs/heads/big-history-branch
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
$ wc -c .git/refs/heads/big-history-branch
41 .git/refs/heads/big-history-branch
# Aynan 41 bayt: 40 belgili SHA-1 + yangi qator (\\n).

# ============================================================
# 2) HEAD nima ekanligini isbotlash
# ============================================================
$ cat .git/HEAD
ref: refs/heads/main

$ git switch feature-x
$ cat .git/HEAD
ref: refs/heads/feature-x
# switch shunchaki HEAD faylining matnini o'zgartirdi.

# ============================================================
# 3) Detached HEAD holatini qo'lda hosil qilish
# ============================================================
$ git checkout c3a1f9e
Note: switching to 'c3a1f9e'.
You are in 'detached HEAD' state...
$ cat .git/HEAD
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
# Endi HEAD ref'ga EMAS, to'g'ridan-to'g'ri commit SHA-1'iga ishora qiladi.

$ git commit --allow-empty -m "detached holatda commit"
[detached HEAD f00dbabe] detached holatda commit
$ git branch --contains f00dbabe
# (bo'sh natija) — bu commit hech qanday branch'ga tegishli emas!
$ git reflog | head -3
f00dbabe HEAD@{0}: commit: detached holatda commit
c3a1f9e HEAD@{1}: checkout: moving from feature-x to c3a1f9e
# reflog orqali topib, uni yangi branch'ga biriktirish mumkin:
$ git branch qutqarilgan-branch f00dbabe

# ============================================================
# 4) git switch/checkout uchta amalni bajarishini kuzatish
# ============================================================
$ git switch main
$ cat .git/HEAD                       # 1) HEAD yangilandi
ref: refs/heads/main
$ git status --short                   # 2) index tree bilan mos
# (toza — farq yo'q)
$ ls                                    # 3) working dir yangilandi
README.md  backend/  frontend/

# ============================================================
# 5) packed-refs bilan loose ref orasidagi ustunlik
# ============================================================
$ git pack-refs --all
$ cat .git/packed-refs | grep feature-x
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e refs/heads/feature-x
$ ls .git/refs/heads/
main
# feature-x endi loose fayl sifatida yo'q, faqat packed-refs ichida.

$ git commit --allow-empty -m "yangi commit feature-x'da"
$ ls .git/refs/heads/
feature-x  main
# Yangi commit qilinganda Git AVTOMATIK ravishda loose faylni qayta
# yaratdi — packed-refs endi eskirgan, lekin loose versiya ustunlik qiladi.

# ============================================================
# 6) Ikkita branch bir xil eski commit'larni ULASHISHI
# ============================================================
$ git log --oneline main
c3a1f9e uchinchi commit
7b2e8d1 ikkinchi commit
4a1c7f0 birinchi commit
$ git log --oneline feature-x
9d4e2a3 feature ustida ish
7b2e8d1 ikkinchi commit      # <- main bilan BIR XIL obyekt
4a1c7f0 birinchi commit      # <- main bilan BIR XIL obyekt
# 7b2e8d1 va 4a1c7f0 ikkalasida ham bitta marta saqlangan, ikki marta emas.

# ============================================================
# 7) symbolic-ref — HEAD'ni to'g'ridan-to'g'ri boshqarish
# ============================================================
$ git symbolic-ref HEAD
refs/heads/main
$ git symbolic-ref HEAD refs/heads/feature-x
$ cat .git/HEAD
ref: refs/heads/feature-x
# Xuddi git switch qilingandek natija, lekin buyruq darajasida, oshkora.

$ git symbolic-ref HEAD refs/heads/notavjud
$ git status
fatal: not a valid ref: HEAD refers to a nonexistent ref
# symbolic-ref formatni tekshiradi, lekin ref'ning mavjudligini emas —
# shuning uchun ehtiyotkorlik bilan ishlatish kerak.

# ============================================================
# 8) Reflog — .git/logs/ ichida nima bor
# ============================================================
$ cat .git/logs/HEAD | tail -3
7b2e8d1... 9d4e2a3... Dev <dev@example.com> 1706000100 +0500	commit: feature ustida ish
9d4e2a3... c3a1f9e... Dev <dev@example.com> 1706000200 +0500	checkout: moving from feature-x to main
c3a1f9e... 7b2e8d1... Dev <dev@example.com> 1706000300 +0500	commit: uchinchi commit

$ git reflog
7b2e8d1 (HEAD -> main) HEAD@{0}: commit: uchinchi commit
9d4e2a3 HEAD@{1}: checkout: moving from feature-x to main
c3a1f9e HEAD@{2}: commit: feature ustida ish
# git reflog aynan shu faylni o'qib, o'qish uchun qulay formatga o'giradi.

# ============================================================
# 9) Remote-tracking ref — uchinchi ref turi
# ============================================================
$ git fetch origin
$ ls .git/refs/remotes/origin/
main  feature-x
$ cat .git/refs/remotes/origin/main
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
# refs/remotes/origin/main — bu SIZNING main branch'ingiz EMAS, balki
# oxirgi fetch paytida serverda main qayerda turgani haqidagi "xotira".
# git pull = git fetch (bu ref'ni yangilaydi) + git merge (mahalliy
# branch'ga qo'shadi).
""".strip()

L1_CODE_RU = """
# ============================================================
# 1) "Настоящая" цена создания ветки
# ============================================================
$ time git branch big-history-branch
real    0m0.003s   # даже при 10 000 коммитов результат тот же — O(1)

$ cat .git/refs/heads/big-history-branch
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
$ wc -c .git/refs/heads/big-history-branch
41 .git/refs/heads/big-history-branch
# Ровно 41 байт: 40-символьный SHA-1 + перевод строки (\\n).

# ============================================================
# 2) Доказательство, что такое HEAD
# ============================================================
$ cat .git/HEAD
ref: refs/heads/main

$ git switch feature-x
$ cat .git/HEAD
ref: refs/heads/feature-x
# switch просто изменил текст файла HEAD.

# ============================================================
# 3) Искусственное создание detached HEAD
# ============================================================
$ git checkout c3a1f9e
Note: switching to 'c3a1f9e'.
You are in 'detached HEAD' state...
$ cat .git/HEAD
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
# Теперь HEAD указывает НЕ на ref, а напрямую на SHA-1 коммита.

$ git commit --allow-empty -m "коммит в detached состоянии"
[detached HEAD f00dbabe] коммит в detached состоянии
$ git branch --contains f00dbabe
# (пустой результат) — этот коммит не принадлежит ни одной ветке!
$ git reflog | head -3
f00dbabe HEAD@{0}: commit: коммит в detached состоянии
c3a1f9e HEAD@{1}: checkout: moving from feature-x to c3a1f9e
# Через reflog можно найти и привязать его к новой ветке:
$ git branch spasennaya-branch f00dbabe

# ============================================================
# 4) Наблюдение за тремя действиями git switch/checkout
# ============================================================
$ git switch main
$ cat .git/HEAD                       # 1) HEAD обновлён
ref: refs/heads/main
$ git status --short                   # 2) index соответствует tree
# (чисто — разницы нет)
$ ls                                    # 3) рабочая директория обновлена
README.md  backend/  frontend/

# ============================================================
# 5) Приоритет loose ref над packed-refs
# ============================================================
$ git pack-refs --all
$ cat .git/packed-refs | grep feature-x
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e refs/heads/feature-x
$ ls .git/refs/heads/
main
# feature-x теперь не существует как loose файл, только в packed-refs.

$ git commit --allow-empty -m "новый коммит в feature-x"
$ ls .git/refs/heads/
feature-x  main
# При новом коммите Git АВТОМАТИЧЕСКИ пересоздал loose файл —
# packed-refs теперь устарел, но loose версия имеет приоритет.

# ============================================================
# 6) Как две ветки РАЗДЕЛЯЮТ одни и те же старые коммиты
# ============================================================
$ git log --oneline main
c3a1f9e третий коммит
7b2e8d1 второй коммит
4a1c7f0 первый коммит
$ git log --oneline feature-x
9d4e2a3 работа над feature
7b2e8d1 второй коммит      # <- ТОТ ЖЕ объект, что и в main
4a1c7f0 первый коммит      # <- ТОТ ЖЕ объект, что и в main
# 7b2e8d1 и 4a1c7f0 хранятся один раз для обоих, а не дважды.

# ============================================================
# 7) symbolic-ref — прямое управление HEAD
# ============================================================
$ git symbolic-ref HEAD
refs/heads/main
$ git symbolic-ref HEAD refs/heads/feature-x
$ cat .git/HEAD
ref: refs/heads/feature-x
# Тот же результат, что и при git switch, но на уровне команды, явно.

$ git symbolic-ref HEAD refs/heads/notexist
$ git status
fatal: not a valid ref: HEAD refers to a nonexistent ref
# symbolic-ref проверяет формат, но не существование ref — поэтому
# нужно использовать осторожно.

# ============================================================
# 8) Reflog — что внутри .git/logs/
# ============================================================
$ cat .git/logs/HEAD | tail -3
7b2e8d1... 9d4e2a3... Dev <dev@example.com> 1706000100 +0500	commit: работа над feature
9d4e2a3... c3a1f9e... Dev <dev@example.com> 1706000200 +0500	checkout: moving from feature-x to main
c3a1f9e... 7b2e8d1... Dev <dev@example.com> 1706000300 +0500	commit: третий коммит

$ git reflog
7b2e8d1 (HEAD -> main) HEAD@{0}: commit: третий коммит
9d4e2a3 HEAD@{1}: checkout: moving from feature-x to main
c3a1f9e HEAD@{2}: commit: работа над feature
# git reflog просто читает этот файл и превращает в удобный для чтения формат.

# ============================================================
# 9) Remote-tracking ref — третий тип ref
# ============================================================
$ git fetch origin
$ ls .git/refs/remotes/origin/
main  feature-x
$ cat .git/refs/remotes/origin/main
c3a1f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e
# refs/remotes/origin/main — это НЕ ваша ветка main, а "память" о том,
# где находился main на сервере во время последнего fetch.
# git pull = git fetch (обновляет этот ref) + git merge (добавляет в
# локальную ветку).
""".strip()

L1_TASK = {
    "task_title": "Detached HEAD'dan reflog orqali qutqarish",
    "task_title_ru": "Спасение из detached HEAD через reflog",
    "task_description": (
        "Kamida 3 commit'li repo yarating. `git checkout <eski-commit>` "
        "bilan ataylab detached HEAD holatiga o'ting, o'sha yerda yangi "
        "commit qiling. Keyin boshqa branch'ga o'ting (bu commit "
        "'yo'qolgandek' tuyulishi kerak). So'ngra FAQAT `git reflog` va "
        "`git branch <nom> <sha>` yordamida o'sha commit'ni qutqarib, "
        "unga yangi branch nomi bering. Har bir qadamda `.git/HEAD` "
        "faylining mazmunini hisobotga kiriting."
    ),
    "task_description_ru": (
        "Создайте репозиторий минимум с 3 коммитами. Через `git checkout "
        "<старый-коммит>` намеренно перейдите в состояние detached HEAD и "
        "сделайте там новый коммит. Затем переключитесь на другую ветку "
        "(этот коммит должен казаться 'потерянным'). После этого, "
        "используя ТОЛЬКО `git reflog` и `git branch <имя> <sha>`, "
        "спасите этот коммит, дав ему имя новой ветки. Включите в отчёт "
        "содержимое файла `.git/HEAD` на каждом шаге."
    ),
    "task_requirements": (
        "1) `cat .git/HEAD` chiqishi commit qilishdan oldin va detached "
        "holatda farqli ekanligini ko'rsating. 2) `git branch --contains "
        "<sha>` yo'qolgan commit uchun BO'SH natija berishini isbotlang. "
        "3) reflog orqali topib, yangi branch yaratib, endi "
        "`--contains` natija berishini ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Покажите, что вывод `cat .git/HEAD` отличается до коммита и "
        "в detached состоянии. 2) Докажите, что `git branch --contains "
        "<sha>` для потерянного коммита даёт ПУСТОЙ результат. 3) Найдя "
        "через reflog и создав новую ветку, покажите, что теперь "
        "`--contains` даёт результат."
    ),
    "task_technologies": "Git (checkout, reflog, branch)",
    "task_deadline_days": 3,
}

L1_SAMPLE = {
    "title": "Namuna: detached HEAD qutqaruv skripti",
    "description": (
        "Bash skripti detached HEAD holatini ataylab hosil qiladi, "
        "yo'qolgan commit'ni reflog orqali topadi va uni yangi branch'ga "
        "biriktiradi, har bir bosqichda HEAD holatini chop etadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "rescue_detached.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf demo && mkdir demo && cd demo && git init -q\n"
                "git commit --allow-empty -q -m \"c1\"\n"
                "git commit --allow-empty -q -m \"c2\"\n"
                "OLD=$(git rev-parse HEAD)\n\n"
                "echo \"== HEAD branch'da ==\"; cat .git/HEAD\n\n"
                "git checkout -q \"$OLD\"\n"
                "echo \"== HEAD detached holatda ==\"; cat .git/HEAD\n\n"
                "git commit --allow-empty -q -m \"yo'qolishi mumkin bo'lgan commit\"\n"
                "LOST=$(git rev-parse HEAD)\n"
                "echo \"Yo'qolgan commit: $LOST\"\n\n"
                "git switch -q main\n"
                "echo \"== main'ga qaytdik, LOST hali ko'rinmaydi ==\"\n"
                "git branch --contains \"$LOST\" || echo \"(bo'sh — kutilganidek)\"\n\n"
                "echo \"== reflog orqali qidirish ==\"\n"
                "git reflog | grep \"$LOST\" | head -1\n\n"
                "git branch qutqarilgan \"$LOST\"\n"
                "echo \"== endi ko'rinadi ==\"\n"
                "git branch --contains \"$LOST\"\n"
            ),
        },
    ],
}

L1_EXERCISES = [
    {
        "title": "Branch nima?",
        "title_ru": "Что такое ветка?",
        "description": "Git'da 'branch' aslida texnik jihatdan nima?",
        "description_ru": "Что технически представляет собой 'ветка' в Git?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bitta commit SHA-1'ini saqlovchi oddiy matn fayli",
            "Butun loyihaning alohida nusxasi",
            "Obyektlar bazasining alohida bo'limi",
            "Faqat xotirada mavjud bo'lgan vaqtinchalik ko'rsatkich",
        ],
        "options_ru": [
            "Обычный текстовый файл, хранящий SHA-1 одного коммита",
            "Отдельная копия всего проекта",
            "Отдельный раздел базы объектов",
            "Временный указатель, существующий только в памяти",
        ],
        "correct_answers": "A",
        "hint": ".git/refs/heads/ ichidagi faylni cat bilan ochib ko'ring.",
        "hint_ru": "Откройте файл внутри .git/refs/heads/ командой cat.",
        "explanation": "Branch — 40 baytlik SHA-1'ni saqlovchi fayl, shuning uchun yaratish O(1).",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Detached HEAD xavfi",
        "title_ru": "Опасность detached HEAD",
        "description": "Detached HEAD holatida yangi commit qilinsa, nima uchun bu commit 'yo'qolib qolishi mumkin'?",
        "description_ru": "Почему коммит, сделанный в состоянии detached HEAD, может 'потеряться'?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki hech qanday branch fayli o'sha commit'ga ishora qilmaydi",
            "Chunki commit obyektlar bazasiga umuman yozilmaydi",
            "Chunki SHA-1 hisoblanmaydi",
            "Chunki .git/index avtomatik o'chib ketadi",
        ],
        "options_ru": [
            "Потому что ни один файл ветки не указывает на этот коммит",
            "Потому что коммит вообще не записывается в базу объектов",
            "Потому что SHA-1 не вычисляется",
            "Потому что .git/index автоматически удаляется",
        ],
        "correct_answers": "A",
        "hint": "git branch --contains natijasini eslang.",
        "hint_ru": "Вспомните результат git branch --contains.",
        "explanation": "Commit obyekti mavjud, lekin unga hech qaysi ref ishora qilmasa, u faqat reflog orqali topiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "HEAD faylining ikki turi",
        "title_ru": "Два состояния файла HEAD",
        "description": "Branch'da turganda .git/HEAD odatda 'ref: refs/heads/...' saqlaydi; detached holatda esa to'g'ridan-to'g'ri ___ saqlaydi.",
        "description_ru": "Когда вы на ветке, .git/HEAD обычно хранит 'ref: refs/heads/...'; в detached состоянии он хранит напрямую ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "commit SHA-1",
        "correct_answers_ru": "SHA-1 коммита",
        "hint": "40 belgili narsa — 0-darsda ko'rgan obyekt ID'si.",
        "hint_ru": "40-символьная вещь — ID объекта из урока 0.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 2 — Packfile va git gc: tarix qanday siqiladi
# ---------------------------------------------------------------------------

L2_TEXT = """
<h3>Loose obyektlar — samarasiz, lekin sodda</h3>
<p>0-darsda ko'rgan har bir obyekt (<code>git hash-object -w</code> orqali
yaratilgan) — alohida, zlib bilan siqilgan fayl sifatida
<code>.git/objects/xx/yyyy...</code> ichida saqlanadi. Bunga <strong>loose
object</strong> deyiladi. Bu format sodda va tez yoziladi, lekin ikkita
muammosi bor: (1) minglab kichik fayl — fayl tizimi uchun ortiqcha yuk
(har bir fayl metama'lumoti, inode), (2) har bir obyekt ALOHIDA siqiladi —
agar ikkita commit orasida bitta faylning faqat bitta qatori o'zgargan
bo'lsa ham, ikkala to'liq versiya alohida-alohida saqlanadi, garchi ular
juda o'xshash bo'lsa ham.</p>

<h3>Packfile — bir nechta obyektni bitta faylga siqish</h3>
<p><code>git gc</code> (yoki avtomatik <code>git gc --auto</code>, ma'lum
miqdordagi loose obyekt to'planganda) loose obyektlarni bitta
<strong>packfile</strong>ga (<code>.pack</code> fayli) yig'adi. Bu jarayonda
Git faqat siqish (zlib) bilan cheklanmaydi — u <strong>delta
compression</strong> qo'llaydi: o'xshash obyektlarni (masalan, bir xil
faylning ketma-ket versiyalari) topib, ulardan birini to'liq saqlaydi,
qolganlarini esa faqat "asosiy nusxadan farqi" sifatida saqlaydi. Bu xuddi
video kodlashdagi key-frame + farq-freym mantig'iga o'xshaydi.</p>

<h3>.idx fayli — packfile ichida tez qidiruv</h3>
<p>Packfile o'zi ketma-ket siqilgan baytlar oqimi — ichidan bitta SHA-1'ni
tez topish uchun Git har bir <code>.pack</code> uchun mos <code>.idx</code>
(index) faylini ham yaratadi: SHA-1 dan pack faylidagi bayt-ofset (offset)
ga xarita. Shu ikkita fayl (<code>pack-XXXX.pack</code> + <code>pack-XXXX.idx</code>)
birgalikda <code>.git/objects/pack/</code> papkasida yashaydi.</p>

<h3>Loose obyektlar vs packfile</h3>
<pre class="mermaid">
flowchart LR
  subgraph before ["git gc DAN OLDIN"]
    L1["loose: a3/f291.."]
    L2["loose: 9c/7b1a.."]
    L3["loose: 55/ee11.."]
    L4["loose: ...ko'plab kichik fayl"]
  end
  subgraph after ["git gc DAN KEYIN"]
    P["pack-1a2b3c.pack
(delta-siqilgan, bitta fayl)"]
    I["pack-1a2b3c.idx
(SHA-1 -> offset xaritasi)"]
  end
  before -->|"git gc"| after
  style P fill:#d6e9ff,stroke:#2266aa
  style I fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma shu narsani ko'rsatadi: ko'plab mayda loose fayllar bitta
ixcham pack faylga aylanadi, unga mos idx fayl esa qidiruvni tez
saqlaydi. <code>git gc</code>dan keyin ham repo to'liq ishlaydi — Git
avtomatik ravishda kerak bo'lganda ham loose, ham pack obyektlarni
tekshiradi, foydalanuvchi uchun farqi sezilmaydi.</p>

<h3>git gc nima qiladi (to'liq ro'yxat)</h3>
<p><code>git gc</code> bir nechta ishni birgalikda bajaradi: loose
obyektlarni pack'ga yig'ish, keraksiz (hech qanday ref'dan yetib
bo'lmaydigan) obyektlarni <code>gc.pruneExpire</code> muddatidan keyin
o'chirish, <code>packed-refs</code>ni yangilash, eskirgan reflog
yozuvlarini tozalash. <strong>Diqqat</strong>: <code>git gc --prune=now</code>
darhol o'chiradi — agar hali reflog orqali kerak bo'lishi mumkin bo'lgan
commit bo'lsa (masalan endigina reset qilingan), buni avval tekshiring.</p>

<h3>Nega bu amaliyotda muhim</h3>
<p>Katta repo'da (minglab commit, ko'p binary fayl) <code>.git/</code>
hajmi tez o'sib ketishi mumkin. <code>git count-objects -v</code> orqali
loose obyektlar sonini va umumiy hajmni ko'rish mumkin — agar
<code>loose-objects</code> soni juda katta bo'lsa, bu <code>git gc</code>
hali ishlamaganini yoki avtomatik chegaraga yetmaganini bildiradi.
Ko'pchilik CI/CD tizimi va Git server (GitHub) fon rejimida muntazam
<code>git gc</code> ishga tushiradi, shuning uchun oddiy foydalanuvchi buni
qo'lda chaqirishga kamdan-kam muhtoj bo'ladi — lekin nima uchun repo
klonlash ba'zan tezlashishini tushunish uchun bu muhim.</p>

<h3>Bitmap index — klonlash va fetch'ni tezlashtirish</h3>
<p>Juda katta repo'larda (GitHub kabi serverlarda) <code>git repack
-b</code> yoki <code>git gc</code> paytida qo'shimcha
<code>.bitmap</code> fayli yaratilishi mumkin — bu har bir commit uchun
"undan yetib bo'ladigan barcha obyektlar" ro'yxatini oldindan hisoblab,
bit-massiv shaklida saqlaydi. Natijada <code>git clone</code> yoki
<code>git fetch</code> paytida kerakli obyektlar to'plamini hisoblash
(odatda sekin graf-aylanish talab qiladigan amal) juda tezlashadi —
bitmap orqali bu deyarli darhol bajariladi.</p>

<h3>git repack vs git gc — farqi</h3>
<p><code>git gc</code> — bu "avtomatik, xavfsiz sukut" vazifa: u
pruning, reflog tozalash va repack'ni birgalikda, konservativ
sozlamalar bilan bajaradi. <code>git repack</code> esa faqat
QAYTA PAKETLASH vazifasini bajaradigan, ko'proq nazoratga ega
quyi-darajadagi buyruq — masalan <code>git repack -a -d
--depth=250 --window=250</code> orqali maksimal siqishni majburlash
mumkin (bu sekinroq, lekin eng ixcham natija beradi — odatda serverlar
CI/release paytida shunday ishlatadi).</p>
""".strip()

L2_TEXT_RU = """
<h3>Loose-объекты — просто, но неэффективно</h3>
<p>Каждый объект, который вы видели в уроке 0 (созданный через <code>git
hash-object -w</code>), хранится как отдельный, сжатый через zlib файл в
<code>.git/objects/xx/yyyy...</code>. Это называется <strong>loose
object</strong>. Формат простой и быстро записывается, но имеет две
проблемы: (1) тысячи мелких файлов — лишняя нагрузка на файловую систему
(метаданные, inode для каждого), (2) каждый объект сжимается ОТДЕЛЬНО —
даже если между двумя коммитами в одном файле изменилась только одна
строка, обе полные версии хранятся отдельно, хотя они очень похожи.</p>

<h3>Packfile — сжатие нескольких объектов в один файл</h3>
<p><code>git gc</code> (или автоматический <code>git gc --auto</code>,
когда накопится определённое число loose-объектов) собирает
loose-объекты в один <strong>packfile</strong> (файл <code>.pack</code>).
При этом Git не ограничивается просто сжатием (zlib) — он применяет
<strong>delta compression</strong>: находит похожие объекты (например,
последовательные версии одного файла), сохраняет один из них полностью, а
остальные — только как "разницу от базовой версии". Это похоже на логику
key-frame + разностных кадров в видеокодировании.</p>

<h3>Файл .idx — быстрый поиск внутри packfile</h3>
<p>Сам packfile — это последовательный поток сжатых байт, поэтому для
быстрого поиска одного SHA-1 внутри Git создаёт для каждого
<code>.pack</code> соответствующий файл <code>.idx</code> (индекс):
карту от SHA-1 к байтовому смещению (offset) внутри pack-файла. Эти два
файла (<code>pack-XXXX.pack</code> + <code>pack-XXXX.idx</code>) вместе
живут в папке <code>.git/objects/pack/</code>.</p>

<h3>Loose-объекты против packfile</h3>
<pre class="mermaid">
flowchart LR
  subgraph before ["ДО git gc"]
    L1["loose: a3/f291.."]
    L2["loose: 9c/7b1a.."]
    L3["loose: 55/ee11.."]
    L4["loose: ...много мелких файлов"]
  end
  subgraph after ["ПОСЛЕ git gc"]
    P["pack-1a2b3c.pack
(delta-сжатый, один файл)"]
    I["pack-1a2b3c.idx
(карта SHA-1 -> offset)"]
  end
  before -->|"git gc"| after
  style P fill:#d6e9ff,stroke:#2266aa
  style I fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает: множество мелких loose-файлов превращаются в
один компактный pack-файл, а соответствующий idx-файл сохраняет быстрый
поиск. После <code>git gc</code> репозиторий продолжает полностью
работать — Git автоматически проверяет и loose, и pack объекты по мере
необходимости, разницы для пользователя не заметно.</p>

<h3>Что делает git gc (полный список)</h3>
<p><code>git gc</code> выполняет несколько задач одновременно: собирает
loose-объекты в pack, удаляет ненужные (недостижимые ни из одного ref)
объекты после истечения срока <code>gc.pruneExpire</code>, обновляет
<code>packed-refs</code>, очищает устаревшие записи reflog.
<strong>Внимание</strong>: <code>git gc --prune=now</code> удаляет
немедленно — если ещё есть коммит, который может понадобиться через
reflog (например, только что после reset), сначала проверьте это.</p>

<h3>Почему это важно на практике</h3>
<p>В большом репозитории (тысячи коммитов, много бинарных файлов) размер
<code>.git/</code> может быстро расти. Через <code>git count-objects
-v</code> можно увидеть число loose-объектов и общий размер — если число
<code>loose-objects</code> очень большое, это значит, что <code>git
gc</code> ещё не запускался или не достиг автоматического порога.
Большинство CI/CD систем и Git-серверов (GitHub) регулярно запускают
<code>git gc</code> в фоне, поэтому обычному пользователю редко нужно
вызывать его вручную — но понимание этого важно, чтобы понять, почему
клонирование репозитория иногда ускоряется.</p>

<h3>Bitmap index — ускорение clone и fetch</h3>
<p>В очень крупных репозиториях (на серверах вроде GitHub) во время
<code>git repack -b</code> или <code>git gc</code> может создаваться
дополнительный файл <code>.bitmap</code> — он заранее вычисляет и
хранит в виде битового массива список "всех объектов, достижимых из"
каждого коммита. В результате вычисление нужного набора объектов при
<code>git clone</code> или <code>git fetch</code> (обычно требующее
медленного обхода графа) сильно ускоряется — через bitmap это
происходит почти мгновенно.</p>

<h3>git repack против git gc — разница</h3>
<p><code>git gc</code> — это задача "автоматическая, безопасная по
умолчанию": она выполняет pruning, очистку reflog и repack вместе, с
консервативными настройками. <code>git repack</code> же — низкоуровневая
команда, выполняющая ТОЛЬКО задачу ПЕРЕУПАКОВКИ, с большим контролем —
например, через <code>git repack -a -d --depth=250 --window=250</code>
можно принудить максимальное сжатие (медленнее, но даёт самый компактный
результат — обычно так делают серверы во время CI/релиза).</p>
""".strip()

L2_CODE = """
# ============================================================
# 1) Loose obyektlar sonini kuzatish
# ============================================================
$ git count-objects -v
count: 47
size: 188
in-pack: 0
packs: 0
size-pack: 0
prune-packable: 0
garbage: 0
size-garbage: 0
# "count: 47" — 47 ta loose obyekt, hali hech qanday pack yo'q.

$ find .git/objects -type f | grep -v pack | wc -l
47
# Aynan shu son — har bir loose obyekt alohida fayl.

# ============================================================
# 2) git gc ishga tushirish va natijani solishtirish
# ============================================================
$ git gc
Enumerating objects: 47, done.
Counting objects: 100% (47/47), done.
Delta compression using up to 8 threads
Compressing objects: 100% (40/40), done.
Writing objects: 100% (47/47), done.
Total 47 (delta 12), reused 0 (delta 0), pack-reused 0

$ git count-objects -v
count: 0
size: 0
in-pack: 47
packs: 1
size-pack: 62
prune-packable: 0
garbage: 0
size-garbage: 0
# "count: 0" — endi loose obyekt yo'q, hammasi "in-pack: 47" ichida.
# "size-pack: 62" (KB) — 188 KB'dan 62 KB'ga qisqardi (delta+zlib tufayli).

$ ls .git/objects/pack/
pack-3f8a91c2b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2.idx
pack-3f8a91c2b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2.pack

# ============================================================
# 3) Pack ichidan bitta obyektni topish (git kabi)
# ============================================================
$ git verify-pack -v .git/objects/pack/pack-3f8a91c2*.idx | head -8
9a8b7c1d... blob   1240 512 12
7b2e8d1f... commit 245  180 524
5a3d0b3e... blob   4    32   704 1 4a1c7f0e...
# Oxirgi qatorda "1 4a1c7f0e..." — bu obyekt DELTA sifatida saqlangan,
# ya'ni 4a1c7f0e obyektidan farq sifatida, to'liq nusxa emas.

$ git cat-file -p 5a3d0b3e
# Natija hali ham to'liq, tushunarli kontent — Git delta'ni "shaffof"
# ravishda ORQAGA yig'ib beradi, foydalanuvchi buni sezmaydi.

# ============================================================
# 4) Delta compression samarasini ko'rish (katta fayl misolida)
# ============================================================
$ for i in $(seq 1 20); do
    echo "qator $i: $(date)" >> big_log.txt
    git add big_log.txt
    git commit -q -m "big_log.txt: $i-o'zgarish"
  done
$ du -sh .git/objects   # gc'dan oldin
1.2M    .git/objects
$ git gc
$ du -sh .git/objects   # gc'dan keyin
84K     .git/objects
# 20 ta deyarli bir xil versiya endi bitta bazaviy nusxa + 19 ta kichik
# delta sifatida saqlanadi — sezilarli farq.

# ============================================================
# 5) Nomukammal narsa: dangling (ref'siz) obyektlar
# ============================================================
$ git commit --allow-empty -m "vaqtinchalik"
$ git reset --hard HEAD~1
$ git fsck --unreachable
unreachable commit a1b2c3d4e5f6...
# Bu commit endi hech qanday branch'dan yetib bo'lmaydi, lekin hali
# o'chirilmagan — chunki gc.pruneExpire (odatda 2 hafta) hali o'tmagan.

$ git gc --prune=now
$ git fsck --unreachable
# (bo'sh) — endi butunlay o'chirildi. DIQQAT: bu QAYTARIB BO'LMAYDIGAN amal.

# ============================================================
# 6) git repack — qo'lda maksimal siqish
# ============================================================
$ git repack -a -d --depth=250 --window=250
Enumerating objects: 512, done.
Counting objects: 100% (512/512), done.
Delta compression using up to 8 threads
Compressing objects: 100% (498/498), done.
Writing objects: 100% (512/512), done.
# -a: barcha obyektlarni bitta pack'ga; -d: eski pack fayllarni o'chirish;
# --depth/--window: delta qidiruvni chuqurroq va kengroq qilish (sekinroq,
# lekin yaxshiroq siqish) — odatda faqat release/CI serverida ishlatiladi.

$ du -sh .git/objects/pack/
38K     .git/objects/pack/
# Odatiy git gc'ga nisbatan biroz kichikroq, lekin ancha sekinroq ishladi.

# ============================================================
# 7) Bitmap index bilan pack yaratish
# ============================================================
$ git repack -a -d -b
$ ls .git/objects/pack/
pack-xxxx.bitmap  pack-xxxx.idx  pack-xxxx.pack
# .bitmap fayli — har bir commit uchun "undan yetib bo'ladigan obyektlar"
# ro'yxatini oldindan hisoblab qo'yadi, clone/fetch'ni tezlashtiradi.

# ============================================================
# 8) git prune — faqat yetib bo'lmaydigan loose obyektlarni tozalash
# ============================================================
$ git prune --expire=now
# git gc --prune=now'dan farqi: prune FAQAT tozalaydi, pack yaratmaydi;
# odatda git gc o'z ichida avtomatik chaqiradi, alohida kamdan-kam
# ishlatiladi (masalan disk joyi darhol kerak bo'lganda).
""".strip()

L2_CODE_RU = """
# ============================================================
# 1) Отслеживание количества loose-объектов
# ============================================================
$ git count-objects -v
count: 47
size: 188
in-pack: 0
packs: 0
size-pack: 0
prune-packable: 0
garbage: 0
size-garbage: 0
# "count: 47" — 47 loose-объектов, packfile ещё нет.

$ find .git/objects -type f | grep -v pack | wc -l
47
# Именно это число — каждый loose-объект отдельный файл.

# ============================================================
# 2) Запуск git gc и сравнение результата
# ============================================================
$ git gc
Enumerating objects: 47, done.
Counting objects: 100% (47/47), done.
Delta compression using up to 8 threads
Compressing objects: 100% (40/40), done.
Writing objects: 100% (47/47), done.
Total 47 (delta 12), reused 0 (delta 0), pack-reused 0

$ git count-objects -v
count: 0
size: 0
in-pack: 47
packs: 1
size-pack: 62
prune-packable: 0
garbage: 0
size-garbage: 0
# "count: 0" — теперь loose-объектов нет, все в "in-pack: 47".
# "size-pack: 62" (КБ) — сократилось со 188 КБ до 62 КБ (delta+zlib).

$ ls .git/objects/pack/
pack-3f8a91c2b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2.idx
pack-3f8a91c2b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2.pack

# ============================================================
# 3) Поиск одного объекта внутри pack (как это делает Git)
# ============================================================
$ git verify-pack -v .git/objects/pack/pack-3f8a91c2*.idx | head -8
9a8b7c1d... blob   1240 512 12
7b2e8d1f... commit 245  180 524
5a3d0b3e... blob   4    32   704 1 4a1c7f0e...
# В последней строке "1 4a1c7f0e..." — этот объект сохранён как DELTA,
# то есть разница от объекта 4a1c7f0e, а не полная копия.

$ git cat-file -p 5a3d0b3e
# Результат всё равно полное, понятное содержимое — Git "прозрачно"
# восстанавливает дельту обратно, пользователь этого не замечает.

# ============================================================
# 4) Эффект delta compression на примере большого файла
# ============================================================
$ for i in $(seq 1 20); do
    echo "строка $i: $(date)" >> big_log.txt
    git add big_log.txt
    git commit -q -m "big_log.txt: изменение $i"
  done
$ du -sh .git/objects   # до gc
1.2M    .git/objects
$ git gc
$ du -sh .git/objects   # после gc
84K     .git/objects
# 20 почти одинаковых версий теперь хранятся как одна базовая копия +
# 19 маленьких дельт — заметная разница.

# ============================================================
# 5) Несовершенство: dangling (без ref) объекты
# ============================================================
$ git commit --allow-empty -m "временный"
$ git reset --hard HEAD~1
$ git fsck --unreachable
unreachable commit a1b2c3d4e5f6...
# Этот коммит теперь недостижим ни из одной ветки, но ещё не удалён —
# потому что gc.pruneExpire (обычно 2 недели) ещё не истёк.

$ git gc --prune=now
$ git fsck --unreachable
# (пусто) — теперь удалён полностью. ВНИМАНИЕ: это НЕОБРАТИМАЯ операция.

# ============================================================
# 6) git repack — ручное максимальное сжатие
# ============================================================
$ git repack -a -d --depth=250 --window=250
Enumerating objects: 512, done.
Counting objects: 100% (512/512), done.
Delta compression using up to 8 threads
Compressing objects: 100% (498/498), done.
Writing objects: 100% (512/512), done.
# -a: все объекты в один pack; -d: удалить старые pack-файлы;
# --depth/--window: сделать поиск delta глубже и шире (медленнее, но
# лучшее сжатие) — обычно используется только на сервере релиза/CI.

$ du -sh .git/objects/pack/
38K     .git/objects/pack/
# Немного меньше, чем при обычном git gc, но работало значительно медленнее.

# ============================================================
# 7) Создание pack с bitmap index
# ============================================================
$ git repack -a -d -b
$ ls .git/objects/pack/
pack-xxxx.bitmap  pack-xxxx.idx  pack-xxxx.pack
# Файл .bitmap заранее вычисляет список "достижимых объектов" для
# каждого коммита, ускоряя clone/fetch.

# ============================================================
# 8) git prune — очистка только недостижимых loose-объектов
# ============================================================
$ git prune --expire=now
# Отличие от git gc --prune=now: prune ТОЛЬКО очищает, не создаёт pack;
# обычно git gc вызывает его автоматически внутри себя, отдельно
# используется редко (например, когда срочно нужно место на диске).
""".strip()

L2_TASK = {
    "task_title": "gc oldin va keyin: o'lchamlarni o'lchang",
    "task_title_ru": "До и после gc: измерьте размеры",
    "task_description": (
        "Yangi repo yarating, kamida 20 ta commit qiling (bitta faylni "
        "kichik-kichik o'zgartirib). `git count-objects -v` va `du -sh "
        ".git/objects` natijalarini `git gc`dan OLDIN yozib oling. So'ngra "
        "`git gc` ishga tushiring va xuddi shu ikkita buyruqni QAYTA "
        "ishga tushiring. Ikkalasini solishtiruvchi jadval tuzing va "
        "farqning sababini (delta compression) tushuntiring."
    ),
    "task_description_ru": (
        "Создайте новый репозиторий, сделайте минимум 20 коммитов "
        "(меняя один файл небольшими порциями). Запишите результаты "
        "`git count-objects -v` и `du -sh .git/objects` ДО `git gc`. "
        "Затем запустите `git gc` и выполните те же две команды СНОВА. "
        "Составьте сравнительную таблицу и объясните причину разницы "
        "(delta compression)."
    ),
    "task_requirements": (
        "1) gc'dan oldingi va keyingi `count-objects -v` to'liq "
        "chiqishini keltiring. 2) `du -sh` orqali hajm farqini foizda "
        "hisoblang. 3) `git verify-pack -v` chiqishida kamida bitta "
        "delta-saqlangan obyektni topib ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Приведите полный вывод `count-objects -v` до и после gc. "
        "2) Через `du -sh` посчитайте разницу в размере в процентах. "
        "3) Найдите и покажите минимум один объект, сохранённый как "
        "delta, в выводе `git verify-pack -v`."
    ),
    "task_technologies": "Git (gc, count-objects, verify-pack, fsck)",
    "task_deadline_days": 4,
}

L2_SAMPLE = {
    "title": "Namuna: gc oldin/keyin o'lchov skripti",
    "description": (
        "Bash skripti 20 ta kichik commit yaratadi, gc'dan oldin va "
        "keyin obyekt sonini hamda hajmni o'lchab, taqqoslovchi jadval "
        "chop etadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "gc_before_after.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf gcdemo && mkdir gcdemo && cd gcdemo && git init -q\n\n"
                "for i in $(seq 1 20); do\n"
                "    echo \"qator $i: $(date +%s)\" >> big_log.txt\n"
                "    git add big_log.txt\n"
                "    git commit -q -m \"o'zgarish $i\"\n"
                "done\n\n"
                "echo \"=== gc'DAN OLDIN ===\"\n"
                "git count-objects -v\n"
                "du -sh .git/objects\n\n"
                "git gc --quiet\n\n"
                "echo \"=== gc'DAN KEYIN ===\"\n"
                "git count-objects -v\n"
                "du -sh .git/objects\n\n"
                "echo \"=== delta obyektlar namunasi ===\"\n"
                "PACKIDX=$(ls .git/objects/pack/*.idx | head -1)\n"
                "git verify-pack -v \"$PACKIDX\" | grep -E ' [0-9]+ [0-9a-f]+$' | head -5\n"
            ),
        },
    ],
}

L2_EXERCISES = [
    {
        "title": "Packfile maqsadi",
        "title_ru": "Назначение packfile",
        "description": "git gc'ning loose obyektlarni packfile'ga yig'ishdan asosiy maqsadi nima?",
        "description_ru": "Какова основная цель сборки loose-объектов в packfile при git gc?",
        "exercise_type": "multiple_choice",
        "options": [
            "Fayl sonini kamaytirish va delta compression orqali hajmni qisqartirish",
            "Obyektlarning SHA-1'ini o'zgartirish",
            "Commit tarixini o'chirib, faqat oxirgi holatni qoldirish",
            "Branch'larni bitta branch'ga birlashtirish",
        ],
        "options_ru": [
            "Сократить число файлов и уменьшить размер через delta compression",
            "Изменить SHA-1 объектов",
            "Удалить историю коммитов, оставив только последнее состояние",
            "Объединить все ветки в одну",
        ],
        "correct_answers": "A",
        "hint": "count-objects -v natijasidagi size-pack'ni size bilan solishtiring.",
        "hint_ru": "Сравните size-pack с size в выводе count-objects -v.",
        "explanation": "Packfile ko'plab kichik loose faylni bitta ixcham, delta-siqilgan faylga aylantiradi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "git gc bosqichlarini tartiblang",
        "title_ru": "Расположите этапы git gc",
        "description": "git gc'ning ichki bosqichlarini mantiqiy tartibda joylashtiring.",
        "description_ru": "Расположите внутренние этапы git gc в логическом порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Loose obyektlarni aniqlash",
            "O'xshash obyektlar orasida delta hisoblash",
            "Natijani pack va idx fayllariga yozish",
            "Yetib bo'lmaydigan obyektlarni muddat o'tgach o'chirish",
        ],
        "drag_items_ru": [
            "Определение loose-объектов",
            "Вычисление delta между похожими объектами",
            "Запись результата в файлы pack и idx",
            "Удаление недостижимых объектов после истечения срока",
        ],
        "correct_order": [
            "Loose obyektlarni aniqlash",
            "O'xshash obyektlar orasida delta hisoblash",
            "Natijani pack va idx fayllariga yozish",
            "Yetib bo'lmaydigan obyektlarni muddat o'tgach o'chirish",
        ],
        "hint": "Avval nima borligini aniqlaydi, keyin siqadi, oxirida tozalaydi.",
        "hint_ru": "Сначала выясняет, что есть, потом сжимает, в конце очищает.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Delta compression atamasi",
        "title_ru": "Термин delta compression",
        "description": "Packfile ichida o'xshash obyektning to'liq nusxasi o'rniga faqat 'asosiy nusxadan ___' saqlanadi.",
        "description_ru": "Внутри packfile вместо полной копии похожего объекта сохраняется только '___ от базовой версии'.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "farqi",
        "correct_answers_ru": "разница",
        "hint": "git verify-pack -v natijasidagi oxirgi ustunni eslang.",
        "hint_ru": "Вспомните последнюю колонку в выводе git verify-pack -v.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 3 — Interaktiv rebase: squash, fixup, reorder, edit, drop
# ---------------------------------------------------------------------------

L3_TEXT = """
<h3>45-kursdagi rebase'dan farqi</h3>
<p>45-kursda siz "rebase vs merge" farqini — commit'larni yangi asosga
qayta joylashtirish — o'rgandingiz. Bu darsda esa <code>git rebase -i</code>
(interactive) ning to'liq imkoniyatlarini ko'ramiz: bu shunchaki commit'larni
ko'chirish emas, balki commit TARIXINI TAHRIRLASH vositasi — birlashtirish,
qayta tartiblash, matnini o'zgartirish, hatto butunlay olib tashlash.</p>

<h3>Rebase todo ro'yxati — bu oddiy matn fayli</h3>
<p><code>git rebase -i HEAD~4</code> buyrug'i tahrirlovchingizda (odatda
<code>$EDITOR</code>) oddiy matn faylini ochadi — har bir qatorda bitta
buyruq va commit. Bu fayl — <code>.git/rebase-merge/git-rebase-todo</code>
(yoki <code>rebase-apply</code>). Muhim tushuncha: siz bu faylni QO'LDA
tahrirlaysiz, Git esa uni yuqoridan pastga qarab bajaradi.</p>

<h3>Buyruqlar va ular aslida nima qiladi</h3>
<ul>
<li><strong>pick</strong> — commit'ni o'zgarishsiz qo'llash.</li>
<li><strong>reword</strong> — commit'ni qo'llaydi, lekin xabarni
tahrirlash uchun to'xtaydi (kontent o'zgarmaydi, faqat matn).</li>
<li><strong>edit</strong> — commit'ni qo'llaydi, so'ng REBASE'ni
TO'XTATADI — siz o'sha nuqtada fayllarni o'zgartirib,
<code>git commit --amend</code>, keyin <code>git rebase --continue</code>
qilishingiz mumkin.</li>
<li><strong>squash</strong> — bu commit'ni OLDINGI qatordagi commit bilan
birlashtiradi, ikkalasining xabarini birlashtirib tahrirlash uchun
to'xtaydi.</li>
<li><strong>fixup</strong> — xuddi squash kabi birlashtiradi, lekin bu
commit'ning xabarini BUTUNLAY TASHLAYDI — oldingi commit xabari saqlanadi.
Odatda "kichik tuzatish"larni asosiy commit'ga jimgina qo'shish uchun
ishlatiladi.</li>
<li><strong>drop</strong> — commit'ni BUTUNLAY OLIB TASHLAYDI, xuddi u
hech qachon bo'lmagandek (uning o'zgarishlari yo'qoladi).</li>
</ul>

<h3>Qatorlarni qayta tartiblash = commit'lar tartibini o'zgartirish</h3>
<p>Todo ro'yxatidagi qatorlar tartibi — commit'larning YANGI tarixdagi
tartibi. Qatorlarni qo'lda ko'chirib, commit'larni qayta tartiblash mumkin
— lekin AGOHLIK: agar ikkita commit bir xil qatorlarni o'zgartirsa,
tartibni o'zgartirish konfliktga olib kelishi mumkin, chunki Git har bir
commit'ni YANGI ketma-ketlikda, YANGI asosdan boshlab qayta qo'llaydi.</p>

<h3>Rebase qayta tartiblashdan oldin va keyin</h3>
<pre class="mermaid">
flowchart TB
  subgraph oldin ["REBASE TODO'DAN OLDIN"]
    direction TB
    A1["pick c1: 'login forma'"]
    A2["pick c2: 'typo tuzatish'"]
    A3["pick c3: 'login validatsiya'"]
    A4["pick c4: 'yana typo'"]
  end
  subgraph keyin ["QAYTA TARTIBLANGAN TODO"]
    direction TB
    B1["pick c1: 'login forma'"]
    B2["fixup c2: 'typo tuzatish'"]
    B3["pick c3: 'login validatsiya'"]
    B4["fixup c4: 'yana typo'"]
  end
  oldin -->|"qayta tartiblash + fixup"| keyin
  style B2 fill:#ffe9b3,stroke:#d09000
  style B4 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma tipik vaziyatni ko'rsatadi: ishlash jarayonida yozilgan
"typo tuzatish" kabi kichik commit'lar <code>fixup</code> orqali tegishli
asosiy commit'ga (c1, c3) jimgina "yutiladi" — natijada toza, mantiqiy
tarix qoladi: faqat "login forma" va "login validatsiya", ikkita aniq
commit, GitHub'da PR ko'rib chiqishda tushunarli.</p>

<h3>--autosquash — odatiy ishni avtomatlashtirish</h3>
<p><code>git commit --fixup=&lt;sha&gt;</code> maxsus formatdagi commit
yaratadi (<code>fixup! &lt;original xabar&gt;</code>). Keyin
<code>git rebase -i --autosquash</code> bunday commit'larni AVTOMATIK
ravishda todo ro'yxatida to'g'ri joyga (asosiy commit'dan keyin,
<code>fixup</code> buyrug'i bilan) joylashtiradi — qo'lda qatorlarni
ko'chirish shart emas.</p>

<h3>Xavfsizlik: --force-with-lease</h3>
<p>Rebase'dan keyin tarix o'zgargani uchun (yangi SHA-1lar) remote'ga
push qilish uchun <code>--force</code> kerak bo'ladi. Lekin oddiy
<code>--force</code> xavfli: agar boshqa dasturchi shu orada push qilgan
bo'lsa, uning ishi yo'qoladi. <code>--force-with-lease</code> esa avval
remote'dagi holat siz oxirgi marta ko'rgan holat bilan bir xilligini
TEKSHIRADI, aks holda rad etadi — bu jamoaviy ishda ustuvor tanlov.</p>

<h3>rebase --onto — commit'lar oralig'ini boshqa asosga ko'chirish</h3>
<p>Ba'zan butun branch'ni emas, faqat UNING BIR QISMINI boshqa asosga
ko'chirish kerak bo'ladi — masalan, <code>feature-x</code> noto'g'ri
branch'dan (<code>old-base</code>) boshlangan bo'lsa. <code>git rebase
--onto new-base old-base feature-x</code> aynan shuni qiladi: faqat
<code>old-base</code>dan <code>feature-x</code>gacha bo'lgan commit'larni
oladi va ularni <code>new-base</code> ustiga qo'yadi — <code>old-base</code>
va undan oldingi hech narsa ta'sirlanmaydi. Bu oddiy <code>rebase -i</code>
bilan qo'lda qilinadigan ishni bitta buyruqqa siqadi.</p>
""".strip()

L3_TEXT_RU = """
<h3>Отличие от rebase из курса 45</h3>
<p>В курсе 45 вы изучили разницу "rebase vs merge" — перенос коммитов на
новую базу. В этом уроке рассмотрим полные возможности <code>git rebase
-i</code> (interactive): это не просто перемещение коммитов, а инструмент
РЕДАКТИРОВАНИЯ ИСТОРИИ коммитов — объединение, перестановка, изменение
текста и даже полное удаление.</p>

<h3>Список todo для rebase — это обычный текстовый файл</h3>
<p>Команда <code>git rebase -i HEAD~4</code> открывает в вашем редакторе
(обычно <code>$EDITOR</code>) обычный текстовый файл — в каждой строке
одна команда и коммит. Этот файл —
<code>.git/rebase-merge/git-rebase-todo</code> (или
<code>rebase-apply</code>). Важное понимание: вы редактируете этот файл
ВРУЧНУЮ, а Git выполняет его сверху вниз.</p>

<h3>Команды и что они на самом деле делают</h3>
<ul>
<li><strong>pick</strong> — применить коммит без изменений.</li>
<li><strong>reword</strong> — применяет коммит, но останавливается для
редактирования сообщения (содержимое не меняется, только текст).</li>
<li><strong>edit</strong> — применяет коммит, затем ОСТАНАВЛИВАЕТ rebase
— в этой точке можно изменить файлы, сделать <code>git commit
--amend</code>, затем <code>git rebase --continue</code>.</li>
<li><strong>squash</strong> — объединяет этот коммит с ПРЕДЫДУЩЕЙ строкой,
останавливается для редактирования объединённого сообщения обоих.</li>
<li><strong>fixup</strong> — объединяет как squash, но ПОЛНОСТЬЮ
ОТБРАСЫВАЕТ сообщение этого коммита — сохраняется сообщение предыдущего.
Обычно используется, чтобы тихо добавить "мелкие правки" в основной
коммит.</li>
<li><strong>drop</strong> — ПОЛНОСТЬЮ УДАЛЯЕТ коммит, как будто его никогда
не было (его изменения теряются).</li>
</ul>

<h3>Перестановка строк = изменение порядка коммитов</h3>
<p>Порядок строк в списке todo — это НОВЫЙ порядок коммитов в истории.
Строки можно вручную переместить, чтобы переставить коммиты — но
ОСТОРОЖНО: если два коммита меняют одни и те же строки, изменение порядка
может привести к конфликту, потому что Git заново применяет каждый коммит
в НОВОЙ последовательности, начиная с НОВОЙ базы.</p>

<h3>Rebase до и после перестановки</h3>
<pre class="mermaid">
flowchart TB
  subgraph oldin ["ДО REBASE TODO"]
    direction TB
    A1["pick c1: 'форма входа'"]
    A2["pick c2: 'исправление опечатки'"]
    A3["pick c3: 'валидация входа'"]
    A4["pick c4: 'ещё опечатка'"]
  end
  subgraph keyin ["ПЕРЕСТАВЛЕННЫЙ TODO"]
    direction TB
    B1["pick c1: 'форма входа'"]
    B2["fixup c2: 'исправление опечатки'"]
    B3["pick c3: 'валидация входа'"]
    B4["fixup c4: 'ещё опечатка'"]
  end
  oldin -->|"перестановка + fixup"| keyin
  style B2 fill:#ffe9b3,stroke:#d09000
  style B4 fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает типичную ситуацию: мелкие коммиты вроде
"исправление опечатки", сделанные в процессе работы, через
<code>fixup</code> тихо "поглощаются" соответствующим основным коммитом
(c1, c3) — в результате остаётся чистая, логичная история: только "форма
входа" и "валидация входа", два понятных коммита, легко читаемых при
ревью PR на GitHub.</p>

<h3>--autosquash — автоматизация типичной работы</h3>
<p><code>git commit --fixup=&lt;sha&gt;</code> создаёт коммит специального
формата (<code>fixup! &lt;оригинальное сообщение&gt;</code>). Затем
<code>git rebase -i --autosquash</code> АВТОМАТИЧЕСКИ размещает такие
коммиты в списке todo в нужном месте (сразу после основного коммита, с
командой <code>fixup</code>) — вручную перемещать строки не нужно.</p>

<h3>Безопасность: --force-with-lease</h3>
<p>После rebase история изменилась (новые SHA-1), поэтому для push в
remote нужен <code>--force</code>. Но обычный <code>--force</code>
опасен: если другой разработчик уже успел запушить в это время, его
работа потеряется. <code>--force-with-lease</code> сначала ПРОВЕРЯЕТ, что
состояние remote совпадает с тем, что вы видели последний раз, иначе
отклоняет push — это предпочтительный выбор в командной работе.</p>

<h3>rebase --onto — перенос диапазона коммитов на другую базу</h3>
<p>Иногда нужно перенести не всю ветку, а только ЕЁ ЧАСТЬ на другую базу
— например, если <code>feature-x</code> ошибочно началась от
<code>old-base</code>. <code>git rebase --onto new-base old-base
feature-x</code> делает именно это: берёт только коммиты от
<code>old-base</code> до <code>feature-x</code> и переносит их на
<code>new-base</code> — сам <code>old-base</code> и всё, что до него, не
затрагивается. Это сжимает в одну команду работу, которую иначе пришлось
бы делать вручную через <code>rebase -i</code>.</p>
""".strip()

L3_CODE = """
# ============================================================
# 1) Interaktiv rebase'ni boshlash
# ============================================================
$ git log --oneline -4
d4e5f6a yana typo
c3b4a5d login validatsiya
b2a3c4e typo tuzatish
a1b2c3d login forma

$ git rebase -i HEAD~4
# Tahrirlovchida ochiladi:
pick a1b2c3d login forma
pick b2a3c4e typo tuzatish
pick c3b4a5d login validatsiya
pick d4e5f6a yana typo

# Rebase 4 commit'ni to'xtatadi (edit, drop, squash, fixup, break, ...)
# Yuqoridagi qatorlar TARTIBI - bu keyingi tarix tartibi.

# ============================================================
# 2) Qo'lda tahrirlash: fixup + qayta tartiblash
# ============================================================
pick a1b2c3d login forma
fixup b2a3c4e typo tuzatish
pick c3b4a5d login validatsiya
fixup d4e5f6a yana typo
# Faylni saqlab yopamiz. Git avtomatik ravishda:
$ git rebase -i HEAD~4
Successfully rebased and updated refs/heads/feature-login.

$ git log --oneline -2
9f8e7d6 login validatsiya
1a2b3c4 login forma
# 4 ta commit endi 2 taga aylandi — typo'lar jimgina yutildi.

# ============================================================
# 3) edit bilan o'rtadagi commit'ni tahrirlash
# ============================================================
$ git rebase -i HEAD~2
pick 1a2b3c4 login forma
edit 9f8e7d6 login validatsiya
# saqlaymiz -> Git birinchi commit'ni qo'llaydi, ikkinchisida to'xtaydi:
Stopped at 9f8e7d6...  login validatsiya
You can amend the commit now, with

  git commit --amend

$ echo "qo'shimcha validatsiya qatori" >> validators.py
$ git add validators.py
$ git commit --amend --no-edit
$ git rebase --continue
Successfully rebased and updated refs/heads/feature-login.
# 9f8e7d6 endi YANGI SHA-1'ga ega — chunki kontenti o'zgardi.

# ============================================================
# 4) --autosquash bilan avtomatlashtirish
# ============================================================
$ git commit --fixup=1a2b3c4 -m "kichik tuzatish"
[feature-login e5f6a7b] fixup! login forma

$ git log --oneline -3
e5f6a7b fixup! login forma
9f8e7d6 login validatsiya
1a2b3c4 login forma

$ git rebase -i --autosquash HEAD~3
# Todo ro'yxati Git tomonidan AVTOMATIK shunday tuziladi:
pick 1a2b3c4 login forma
fixup e5f6a7b fixup! login forma
pick 9f8e7d6 login validatsiya
# Qo'lda ko'chirish shart bo'lmadi — Git "fixup!" prefiksini tanib,
# to'g'ri joyga qo'ydi.

# ============================================================
# 5) drop bilan commit'ni butunlay olib tashlash
# ============================================================
$ git rebase -i HEAD~3
pick 1a2b3c4 login forma
drop 9f8e7d6 login validatsiya   # <- bu qatorni butunlay o'chiramiz
pick e5f6a7b fixup! login forma
# saqlab yopamiz -> login validatsiya commit'i BUTUNLAY yo'qoladi,
# uning kod o'zgarishlari HAM yo'qoladi (drop != revert).

# ============================================================
# 6) Xavfsiz force-push
# ============================================================
$ git push --force-with-lease origin feature-login
# Agar boshqa dasturchi orada push qilgan bo'lsa:
To github.com:team/repo.git
 ! [rejected]  feature-login -> feature-login (stale info)
error: failed to push some refs
# --force-with-lease buni oldini oladi; oddiy --force esa bosib o'tib
# hamkasbning ishini yo'qotib qo'yardi.

# ============================================================
# 7) Rebase to'xtab qolsa — abort bilan orqaga qaytish
# ============================================================
$ git rebase -i HEAD~3
# konflikt yuzaga keldi, chalkashib ketdik:
$ git rebase --abort
# Repo REBASE BOSHLANISHDAN OLDINGI holatga to'liq qaytadi — hech qanday
# o'zgarish saqlanmaydi, xavfsiz "orqaga" tugmasi.

# ============================================================
# 8) rebase --onto — faqat oraliqni ko'chirish
# ============================================================
$ git log --oneline --all --graph
* d4e5f6a (feature-x) feature commit 2
* c3b4a5d feature commit 1
* b2a3c4e (old-base) eski, kerak bo'lmagan asos
* a1b2c3d (new-base) yangi, to'g'ri asos
* 9f8e7d6 umumiy ajdod

$ git rebase --onto new-base old-base feature-x
Successfully rebased and updated refs/heads/feature-x.

$ git log --oneline --all --graph
* f1e2d3c (feature-x) feature commit 2
* e0d1c2b feature commit 1
| * b2a3c4e (old-base) eski, kerak bo'lmagan asos
|/
* a1b2c3d (new-base) yangi, to'g'ri asos
* 9f8e7d6 umumiy ajdod
# feature-x'ning IKKALA commit'i ham endi new-base ustida, old-base
# butunlay chetlab o'tildi — uning tarixiga hech qanday ta'sir bo'lmadi.

# ============================================================
# 9) Rebase paytida konflikt — continue/skip/abort uchligi
# ============================================================
$ git rebase main
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
error: could not apply 7c3a1e9... login validatsiya

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> 7c3a1e9 (login validatsiya)
$ vim config.py && git add config.py
$ git rebase --continue
# YOKI, agar bu commit umuman kerak bo'lmasa:
$ git rebase --skip
# YOKI, agar butunlay chalkashib ketgan bo'lsangiz:
$ git rebase --abort   # boshlanishdan oldingi holatga to'liq qaytadi
""".strip()

L3_CODE_RU = """
# ============================================================
# 1) Запуск интерактивного rebase
# ============================================================
$ git log --oneline -4
d4e5f6a ещё опечатка
c3b4a5d валидация входа
b2a3c4e исправление опечатки
a1b2c3d форма входа

$ git rebase -i HEAD~4
# Открывается в редакторе:
pick a1b2c3d форма входа
pick b2a3c4e исправление опечатки
pick c3b4a5d валидация входа
pick d4e5f6a ещё опечатка

# Rebase останавливает 4 коммита (edit, drop, squash, fixup, break, ...)
# ПОРЯДОК строк выше — это порядок будущей истории.

# ============================================================
# 2) Ручное редактирование: fixup + перестановка
# ============================================================
pick a1b2c3d форма входа
fixup b2a3c4e исправление опечатки
pick c3b4a5d валидация входа
fixup d4e5f6a ещё опечатка
# Сохраняем и закрываем файл. Git автоматически:
$ git rebase -i HEAD~4
Successfully rebased and updated refs/heads/feature-login.

$ git log --oneline -2
9f8e7d6 валидация входа
1a2b3c4 форма входа
# 4 коммита теперь превратились в 2 — опечатки тихо поглощены.

# ============================================================
# 3) Редактирование среднего коммита через edit
# ============================================================
$ git rebase -i HEAD~2
pick 1a2b3c4 форма входа
edit 9f8e7d6 валидация входа
# сохраняем -> Git применяет первый коммит, останавливается на втором:
Stopped at 9f8e7d6...  валидация входа
You can amend the commit now, with

  git commit --amend

$ echo "дополнительная строка валидации" >> validators.py
$ git add validators.py
$ git commit --amend --no-edit
$ git rebase --continue
Successfully rebased and updated refs/heads/feature-login.
# 9f8e7d6 теперь имеет НОВЫЙ SHA-1 — потому что содержимое изменилось.

# ============================================================
# 4) Автоматизация через --autosquash
# ============================================================
$ git commit --fixup=1a2b3c4 -m "мелкая правка"
[feature-login e5f6a7b] fixup! форма входа

$ git log --oneline -3
e5f6a7b fixup! форма входа
9f8e7d6 валидация входа
1a2b3c4 форма входа

$ git rebase -i --autosquash HEAD~3
# Список todo Git строит АВТОМАТИЧЕСКИ так:
pick 1a2b3c4 форма входа
fixup e5f6a7b fixup! форма входа
pick 9f8e7d6 валидация входа
# Вручную перемещать не пришлось — Git распознал префикс "fixup!" и
# поставил в нужное место.

# ============================================================
# 5) Полное удаление коммита через drop
# ============================================================
$ git rebase -i HEAD~3
pick 1a2b3c4 форма входа
drop 9f8e7d6 валидация входа   # <- эту строку полностью убираем
pick e5f6a7b fixup! форма входа
# сохраняем и закрываем -> коммит "валидация входа" ПОЛНОСТЬЮ исчезает,
# его изменения кода ТОЖЕ исчезают (drop != revert).

# ============================================================
# 6) Безопасный force-push
# ============================================================
$ git push --force-with-lease origin feature-login
# Если другой разработчик уже успел запушить в это время:
To github.com:team/repo.git
 ! [rejected]  feature-login -> feature-login (stale info)
error: failed to push some refs
# --force-with-lease предотвращает это; обычный --force прошёл бы и
# потерял работу коллеги.

# ============================================================
# 7) Rebase застрял — возврат через abort
# ============================================================
$ git rebase -i HEAD~3
# возник конфликт, всё запуталось:
$ git rebase --abort
# Репозиторий ПОЛНОСТЬЮ возвращается к состоянию ДО начала rebase —
# ничего не сохраняется, безопасная кнопка "назад".

# ============================================================
# 8) rebase --onto — перенос только диапазона
# ============================================================
$ git log --oneline --all --graph
* d4e5f6a (feature-x) коммит feature 2
* c3b4a5d коммит feature 1
* b2a3c4e (old-base) старая, ненужная база
* a1b2c3d (new-base) новая, правильная база
* 9f8e7d6 общий предок

$ git rebase --onto new-base old-base feature-x
Successfully rebased and updated refs/heads/feature-x.

$ git log --oneline --all --graph
* f1e2d3c (feature-x) коммит feature 2
* e0d1c2b коммит feature 1
| * b2a3c4e (old-base) старая, ненужная база
|/
* a1b2c3d (new-base) новая, правильная база
* 9f8e7d6 общий предок
# ОБА коммита feature-x теперь на new-base, old-base полностью обойдён —
# на его историю это никак не повлияло.

# ============================================================
# 9) Конфликт во время rebase — тройка continue/skip/abort
# ============================================================
$ git rebase main
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
error: could not apply 7c3a1e9... валидация входа

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> 7c3a1e9 (валидация входа)
$ vim config.py && git add config.py
$ git rebase --continue
# ИЛИ, если этот коммит вообще не нужен:
$ git rebase --skip
# ИЛИ, если всё совсем запуталось:
$ git rebase --abort   # полный возврат к состоянию до начала
""".strip()

L3_TASK = {
    "task_title": "5 commit'ni interaktiv rebase bilan tozalang",
    "task_title_ru": "Очистите 5 коммитов через интерактивный rebase",
    "task_description": (
        "Kamida 5 ta commit'li branch yarating: ikkitasi 'typo tuzatish' "
        "kabi kichik tuzatish, bittasi xabari noto'g'ri yozilgan, "
        "qolganlari mantiqiy. `git rebase -i` yordamida: (1) kichik "
        "tuzatishlarni tegishli commit'larga `fixup` qiling, (2) noto'g'ri "
        "xabarni `reword` bilan tuzating, (3) natijada 2-3 ta toza, "
        "mantiqiy commit qoldiring."
    ),
    "task_description_ru": (
        "Создайте ветку минимум с 5 коммитами: два — мелкие исправления "
        "вроде 'исправление опечатки', один — с неправильно "
        "сформулированным сообщением, остальные — логичные. Через `git "
        "rebase -i`: (1) сделайте `fixup` мелких исправлений в "
        "соответствующие коммиты, (2) исправьте неверное сообщение через "
        "`reword`, (3) в результате оставьте 2-3 чистых, логичных "
        "коммита."
    ),
    "task_requirements": (
        "1) `git log --oneline` natijasida oldingi va keyingi holatni "
        "solishtiring (skrinshot yoki matn). 2) Kamida bitta `fixup` va "
        "bitta `reword` ishlatilgan bo'lishi shart. 3) Yakuniy tarixda "
        "'typo' so'zi umuman uchramasligi kerak."
    ),
    "task_requirements_ru": (
        "1) Сравните состояние `git log --oneline` до и после (скриншот "
        "или текст). 2) Должен быть использован минимум один `fixup` и "
        "один `reword`. 3) В финальной истории слово 'опечатка' вообще "
        "не должно встречаться."
    ),
    "task_technologies": "Git (rebase -i, fixup, reword, force-with-lease)",
    "task_deadline_days": 4,
}

L3_SAMPLE = {
    "title": "Namuna: fixup + autosquash oqimi",
    "description": (
        "Bash skripti 4 ta commit yaratadi (asosiy + 2 ta typo tuzatish "
        "+ yana bitta asosiy), so'ngra --fixup va --autosquash bilan "
        "ularni avtomatik ravishda 2 ta toza commit'ga aylantiradi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "autosquash_demo.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "export GIT_EDITOR=true   # avtomatik saqlash uchun editor'ni chetlab o'tish\n\n"
                "rm -rf rebasedemo && mkdir rebasedemo && cd rebasedemo && git init -q\n\n"
                "echo \"forma\" > login.py && git add . && git commit -q -m \"login forma\"\n"
                "BASE1=$(git rev-parse HEAD)\n\n"
                "echo \"typo1\" >> login.py && git add . && git commit -q --fixup=\"$BASE1\"\n\n"
                "echo \"validatsiya\" > validators.py && git add . && git commit -q -m \"login validatsiya\"\n"
                "BASE2=$(git rev-parse HEAD)\n\n"
                "echo \"typo2\" >> validators.py && git add . && git commit -q --fixup=\"$BASE2\"\n\n"
                "echo \"=== AVTOSQUASH'DAN OLDIN ===\"\n"
                "git log --oneline\n\n"
                "GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash --root\n\n"
                "echo \"=== AVTOSQUASH'DAN KEYIN ===\"\n"
                "git log --oneline\n"
            ),
        },
    ],
}

L3_EXERCISES = [
    {
        "title": "fixup vs squash",
        "title_ru": "fixup против squash",
        "description": "fixup buyrug'i squash'dan asosan nimasi bilan farq qiladi?",
        "description_ru": "Чем команда fixup принципиально отличается от squash?",
        "exercise_type": "multiple_choice",
        "options": [
            "fixup birlashtirilgan commit'ning xabarini tashlab yuboradi, squash tahrirlash uchun to'xtaydi",
            "fixup commit'ni butunlay o'chiradi",
            "squash faqat oxirgi commit bilan ishlaydi, fixup istalgan commit bilan ishlamaydi",
            "Ular bir xil, faqat nomi farq qiladi",
        ],
        "options_ru": [
            "fixup отбрасывает сообщение объединяемого коммита, squash останавливается для редактирования",
            "fixup полностью удаляет коммит",
            "squash работает только с последним коммитом, fixup вообще не работает",
            "Они одинаковы, отличается только название",
        ],
        "correct_answers": "A",
        "hint": "Ikkalasi ham birlashtiradi, lekin xabar bilan ishlash farq qiladi.",
        "hint_ru": "Оба объединяют, но по-разному работают с сообщением.",
        "explanation": "fixup xabarni jimgina tashlaydi, squash esa ikkala xabarni birlashtirib tahrirlashga imkon beradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Rebase todo bosqichlarini tartiblang",
        "title_ru": "Расположите этапы rebase todo",
        "description": "'edit' buyrug'i bilan commit'ni tahrirlashning to'g'ri ish oqimini joylashtiring.",
        "description_ru": "Расположите правильный процесс редактирования коммита командой 'edit'.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git rebase -i HEAD~N, edit belgilash",
            "Git commit'ni qo'llab, to'xtaydi",
            "Fayllarni o'zgartirib git commit --amend qilish",
            "git rebase --continue bilan davom ettirish",
        ],
        "drag_items_ru": [
            "git rebase -i HEAD~N, отметить edit",
            "Git применяет коммит и останавливается",
            "Изменить файлы и сделать git commit --amend",
            "Продолжить через git rebase --continue",
        ],
        "correct_order": [
            "git rebase -i HEAD~N, edit belgilash",
            "Git commit'ni qo'llab, to'xtaydi",
            "Fayllarni o'zgartirib git commit --amend qilish",
            "git rebase --continue bilan davom ettirish",
        ],
        "hint": "Rebase avval to'xtaydi, keyin siz o'zgartirasiz, keyin davom etadi.",
        "hint_ru": "Rebase сначала останавливается, потом вы меняете, потом продолжаете.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Nega force-with-lease xavfsizroq",
        "title_ru": "Почему force-with-lease безопаснее",
        "description": "Rebase'dan keyin `--force-with-lease` odatiy `--force`'dan nega xavfsizroq ekanini tushuntiring (2-3 gap).",
        "description_ru": "Объясните (2-3 предложения), почему после rebase `--force-with-lease` безопаснее обычного `--force`.",
        "exercise_type": "text_input",
        "expected_answer": "force-with-lease remote holatini tekshiradi va boshqa birov push qilgan bo'lsa rad etadi, oddiy force esa hech narsani tekshirmasdan bosib o'tadi.",
        "hint": "Kim orada push qilib qo'ygan bo'lsa nima bo'ladi, ikkala holatda ham o'ylab ko'ring.",
        "hint_ru": "Подумайте, что будет в обоих случаях, если кто-то уже успел запушить.",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 4 — git bisect: xatoni ikkilik qidiruv bilan topish
# ---------------------------------------------------------------------------

L4_TEXT = """
<h3>Muammo: qaysi commit'da xato paydo bo'lgan?</h3>
<p>Tasavvur qiling: 200 ta commit'dan iborat tarixda hozir bitta test
muvaffaqiyatsiz. Siz bilasiz — 3 oy oldin (commit #10da) hammasi ishlagan.
Har bir commit'ni qo'lda tekshirish 200 ta urinish talab qilishi mumkin.
<code>git bisect</code> aynan shu muammoni <strong>ikkilik qidiruv (binary
search)</strong> algoritmi bilan yechadi — 200 ta emas, atigi ~8 ta
(<code>log2(200) ≈ 7.6</code>) tekshiruv bilan.</p>

<h3>Ikkilik qidiruv nima uchun ishlaydi</h3>
<p>Shart — <strong>monotonlik</strong>: bitta "yaxshi" commit'dan bitta
"yomon" commit'gacha bo'lgan chiziqli tarixda xato faqat BIR marta paydo
bo'lgan deb faraz qilinadi (avval yo'q, keyin doim bor). Shu shartda har
bir tekshiruv qolgan intervalni <strong>ikki barobar</strong> qisqartiradi
— aynan shuning uchun <code>N</code> commit uchun <code>log2(N)</code>
tekshiruv yetarli.</p>

<h3>Amaliy ish oqimi</h3>
<ol>
<li><code>git bisect start</code> — rejimni boshlash.</li>
<li><code>git bisect bad</code> — hozirgi (yomon) commit'ni belgilash.</li>
<li><code>git bisect good &lt;eski-sha&gt;</code> — ma'lum yaxshi
commit'ni belgilash.</li>
<li>Git AVTOMATIK ravishda oraliqdagi commit'ga o'tkazadi (checkout
qiladi) — siz sinab ko'rasiz (test ishga tushirasiz yoki qo'lda
tekshirasiz).</li>
<li>Natijaga qarab <code>git bisect good</code> yoki <code>git bisect
bad</code> deysiz — Git qidiruv oralig'ini yarmiga qisqartirib, keyingi
commit'ga o'tkazadi.</li>
<li>Faqat bitta "gumon qilinuvchi" commit qolguncha takrorlanadi — Git
uni aniq ko'rsatadi: "commit X is the first bad commit".</li>
<li><code>git bisect reset</code> — asl branch'ga qaytish.</li>
</ol>

<h3>Ikkilik qidiruv bosqichlari</h3>
<pre class="mermaid">
flowchart TB
  R["200 ta commit oralig'i
(good ... bad)"] --> S1["1-tekshiruv:
o'rtadagi commit"]
  S1 -->|"good"| S2a["Faqat YUQORI yarim qoladi
(~100 ta)"]
  S1 -->|"bad"| S2b["Faqat PASTKI yarim qoladi
(~100 ta)"]
  S2a --> S3["2-tekshiruv:
yana o'rtasi (~50 ta)"]
  S2b --> S3
  S3 --> S4["... taxminan 8-tekshiruvdan keyin"]
  S4 --> F["Bitta commit qoldi:
'first bad commit'"]
  style F fill:#ffd6d6,stroke:#c00000
</pre>
<p>Diagramma shuni ko'rsatadi: har bir tekshiruv qolgan nomzodlar sonini
YARMIGA qisqartiradi — chiziqli qidiruv (har bir commit'ni birma-bir
tekshirish) 200 ta urinish talab qilsa, ikkilik qidiruv atigi 7-8 ta
urinish bilan aynan shu natijaga keladi.</p>

<h3>git bisect run — butun jarayonni avtomatlashtirish</h3>
<p>Agar "yaxshi/yomon"ni aniqlaydigan skript (masalan bitta pytest testi)
bo'lsa, <code>git bisect run &lt;skript&gt;</code> BUTUN jarayonni
avtomatlashtiradi: Git har bir commit'da skriptni ishga tushiradi, uning
chiqish kodi (0 = good, boshqa = bad, 125 = "bu commit'ni o'tkazib
yuborish, sinab bo'lmaydi") asosida o'zi qaror qabul qiladi va oxirida
javobni chop etadi — inson aralashuvisiz.</p>

<h3>skip — sinab bo'lmaydigan commit'lar uchun</h3>
<p>Ba'zan oraliqdagi commit umuman build bo'lmaydi yoki testni ishga
tushirish imkonsiz (masalan, o'sha nuqtada boshqa, bog'liqsiz xato bor).
Bunday holda <code>good</code>/<code>bad</code> o'rniga <code>git bisect
skip</code> ishlatiladi — Git o'sha commit'ni chetlab o'tib, qidiruvni
davom ettiradi, natijani "bir nechta nomzod" sifatida taqdim qilishi
mumkin.</p>

<h3>Maxsus atamalar: --term-old / --term-new</h3>
<p>"good"/"bad" so'zlari har doim mos kelavermaydi — masalan, performance
regressiyasini qidirsangiz, "yaxshi" va "yomon" o'rniga "fast"/"slow"
tabiiyroq bo'ladi. <code>git bisect start --term-old=fast
--term-new=slow</code> orqali bu atamalarni almashtirish mumkin, keyin
<code>git bisect fast</code> / <code>git bisect slow</code> ishlatiladi
— algoritmning o'zi butunlay bir xil qoladi, faqat so'zlar
tushunarliroq bo'ladi.</p>

<h3>bisect log va replay — sessiyani saqlash va tiklash</h3>
<p><code>git bisect log</code> hozirgi bisect sessiyasining BARCHA
qadamlarini (start, good, bad belgilangan commit'lar) matn shaklida
chiqaradi. Bu matnni faylga saqlab, keyinroq (hatto boshqa
kompyuterda) <code>git bisect replay &lt;fayl&gt;</code> orqali xuddi
shu sessiyani QAYTA TIKLASH mumkin — masalan, murakkab bisect'ni
hamkasbingizga "davom ettirish uchun" yuborishda foydali.</p>

<h3>bisect va worktree — asosiy ishni to'xtatmasdan qidirish</h3>
<p>6-darsda ko'rasiz: <code>git bisect</code> checkout qilish orqali
ishlaydi, bu esa joriy ishchi katalogingizni o'zgartiradi. Agar
tugallanmagan ishingiz bo'lsa, <code>git worktree add ../bisect-wt</code>
bilan ALOHIDA papkada bisect o'tkazish mumkin — asosiy ishingizga
umuman tegilmaydi.</p>
""".strip()

L4_TEXT_RU = """
<h3>Проблема: в каком коммите появился баг?</h3>
<p>Представьте: в истории из 200 коммитов сейчас один тест падает. Вы
знаете — 3 месяца назад (коммит #10da) всё работало. Проверка каждого
коммита вручную может потребовать 200 попыток. <code>git bisect</code>
решает именно эту проблему алгоритмом <strong>двоичного поиска (binary
search)</strong> — не за 200, а всего за ~8 (<code>log2(200) ≈ 7.6</code>)
проверок.</p>

<h3>Почему работает двоичный поиск</h3>
<p>Условие — <strong>монотонность</strong>: в линейной истории от одного
"хорошего" коммита до одного "плохого" предполагается, что баг появился
только ОДИН раз (сначала его не было, потом он есть всегда). При этом
условии каждая проверка сокращает оставшийся интервал <strong>в два
раза</strong> — именно поэтому для <code>N</code> коммитов достаточно
<code>log2(N)</code> проверок.</p>

<h3>Практический рабочий процесс</h3>
<ol>
<li><code>git bisect start</code> — начать режим.</li>
<li><code>git bisect bad</code> — отметить текущий (плохой) коммит.</li>
<li><code>git bisect good &lt;старый-sha&gt;</code> — отметить известный
хороший коммит.</li>
<li>Git АВТОМАТИЧЕСКИ переключает (checkout) на коммит посередине —
вы проверяете (запускаете тест или проверяете вручную).</li>
<li>В зависимости от результата говорите <code>git bisect good</code> или
<code>git bisect bad</code> — Git сокращает интервал поиска вдвое и
переключает на следующий коммит.</li>
<li>Повторяется, пока не останется один "подозреваемый" коммит — Git
точно укажет его: "commit X is the first bad commit".</li>
<li><code>git bisect reset</code> — вернуться на исходную ветку.</li>
</ol>

<h3>Этапы двоичного поиска</h3>
<pre class="mermaid">
flowchart TB
  R["интервал из 200 коммитов
(good ... bad)"] --> S1["1-я проверка:
средний коммит"]
  S1 -->|"good"| S2a["Остаётся ТОЛЬКО верхняя половина
(~100)"]
  S1 -->|"bad"| S2b["Остаётся ТОЛЬКО нижняя половина
(~100)"]
  S2a --> S3["2-я проверка:
снова середина (~50)"]
  S2b --> S3
  S3 --> S4["... примерно после 8-й проверки"]
  S4 --> F["Остался один коммит:
'first bad commit'"]
  style F fill:#ffd6d6,stroke:#c00000
</pre>
<p>Диаграмма показывает: каждая проверка сокращает число оставшихся
кандидатов ВДВОЕ — линейный поиск (проверка каждого коммита по очереди)
потребовал бы 200 попыток, двоичный поиск даёт тот же результат всего за
7-8 попыток.</p>

<h3>git bisect run — автоматизация всего процесса</h3>
<p>Если есть скрипт, определяющий "хорошо/плохо" (например, один pytest
тест), <code>git bisect run &lt;скрипт&gt;</code> автоматизирует ВЕСЬ
процесс: Git запускает скрипт на каждом коммите, по его коду выхода (0 =
good, другое = bad, 125 = "пропустить этот коммит, проверить нельзя")
сам принимает решение и в конце выводит ответ — без участия человека.</p>

<h3>skip — для коммитов, которые нельзя проверить</h3>
<p>Иногда промежуточный коммит вообще не собирается или тест невозможно
запустить (например, в этой точке есть другой, не связанный баг). В этом
случае вместо <code>good</code>/<code>bad</code> используется <code>git
bisect skip</code> — Git пропускает этот коммит и продолжает поиск, может
представить результат как "несколько кандидатов".</p>

<h3>Специальные термины: --term-old / --term-new</h3>
<p>Слова "good"/"bad" не всегда подходят — например, при поиске
регрессии производительности вместо "хорошо"/"плохо" естественнее
"fast"/"slow". Через <code>git bisect start --term-old=fast
--term-new=slow</code> можно заменить эти термины, затем использовать
<code>git bisect fast</code> / <code>git bisect slow</code> — сам
алгоритм остаётся полностью тем же, меняются только слова, становясь
понятнее.</p>

<h3>bisect log и replay — сохранение и восстановление сессии</h3>
<p><code>git bisect log</code> выводит в текстовом виде ВСЕ шаги текущей
сессии bisect (start, отмеченные good и bad коммиты). Этот текст можно
сохранить в файл и позже (даже на другом компьютере) через <code>git
bisect replay &lt;файл&gt;</code> ВОССТАНОВИТЬ ту же самую сессию —
полезно, например, при передаче сложного bisect коллеге "для
продолжения".</p>

<h3>bisect и worktree — поиск без остановки основной работы</h3>
<p>Как вы увидите в уроке 6, <code>git bisect</code> работает через
checkout, что меняет текущий рабочий каталог. Если есть незавершённая
работа, можно провести bisect в ОТДЕЛЬНОЙ папке через <code>git
worktree add ../bisect-wt</code> — основная работа вообще не
затрагивается.</p>
""".strip()

L4_CODE = """
# ============================================================
# 1) bisect'ni boshlash
# ============================================================
$ git bisect start
$ git bisect bad                    # HEAD — hozirgi, buzilgan holat
$ git bisect good v1.4.0            # 1.4.0 tegida hammasi ishlagan edi
Bisecting: 99 revisions left to test after this (roughly 7 steps)
[7c3a1e9...] refactor: payment modulini qayta yozish

# ============================================================
# 2) Har bir qadamda sinab ko'rish
# ============================================================
$ pytest tests/test_payment.py -q
# FAILED tests/test_payment.py::test_discount_applies
$ git bisect bad
Bisecting: 49 revisions left to test after this (roughly 6 steps)
[a8b7c6d...] feat: chegirma hisoblash logikasi

$ pytest tests/test_payment.py -q
# 3 passed
$ git bisect good
Bisecting: 24 revisions left to test after this (roughly 5 steps)
[...]

# ... yana bir necha qadamdan keyin:
$ git bisect bad
Bisecting: 0 revisions left to test after this (roughly 0 steps)

# ============================================================
# 3) Yakuniy natija
# ============================================================
$ git bisect bad
f4e5d6c7 is the first bad commit
commit f4e5d6c7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
Author: Dev <dev@example.com>
Date:   Mon Jul 20 14:00:00 2026 +0500

    fix: chegirma foizini validatsiya qilish

 app/services/payment_service.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)

$ git bisect reset
Previous HEAD position was f4e5d6c... fix: chegirma foizini validatsiya
Switched to branch 'main'
# Asl branch'ga qaytdik, bisect rejimi tugadi.

# ============================================================
# 4) git bisect run — to'liq avtomatlashtirish
# ============================================================
$ cat check_bug.sh
#!/bin/bash
pytest tests/test_payment.py -q -k test_discount_applies
exit $?

$ git bisect start HEAD v1.4.0
$ git bisect run ./check_bug.sh
running ./check_bug.sh
Bisecting: 99 revisions left to test after this (roughly 7 steps)
running ./check_bug.sh
...
f4e5d6c7 is the first bad commit
bisect run success
# Inson aralashuvisiz — Git skriptni har bir commit'da ishga tushirib,
# chiqish kodiga qarab o'zi good/bad deb belgiladi.

# ============================================================
# 5) skip — sinab bo'lmaydigan commit
# ============================================================
$ git bisect good
Bisecting: 12 revisions left to test after this (roughly 4 steps)
[abc1234] chore: dependency yangilanishi (build buzilgan, sinab bo'lmaydi)

$ npm install
# ERROR: package-lock.json mos kelmayapti, build ishlamaydi
$ git bisect skip
Bisecting: 12 revisions left to test after this (roughly 4 steps)
[def5678] boshqa commit — bu build bo'ladi

$ pytest tests/test_payment.py -q
# 3 passed
$ git bisect good
# ... davom etadi, skip qilingan commit hisobga kiritilmaydi.

# ============================================================
# 6) log2(N) hisob-kitobi — nega bu tez
# ============================================================
$ python3 -c "import math; print(math.log2(200))"
7.643856189774724
# 200 ta commit uchun атиги ~8 ta tekshiruv — chiziqli qidiruv (200 ta
# urinish) bilan solishtiring: 25 barobar kamroq ish.

# ============================================================
# 7) Maxsus atamalar bilan performance regressiyasini qidirish
# ============================================================
$ git bisect start --term-old=fast --term-new=slow
$ git bisect slow HEAD
$ git bisect fast v2.0.0
Bisecting: 49 revisions left to test after this (roughly 6 steps)
$ ./benchmark.sh
# natija: 340ms (chegara 200ms)
$ git bisect slow
$ ./benchmark.sh
# natija: 120ms
$ git bisect fast
# ... davom etadi, "good"/"bad" o'rniga "fast"/"slow" ishlatiladi.

# ============================================================
# 8) bisect log va replay — sessiyani saqlash
# ============================================================
$ git bisect log > bisect_session.log
$ cat bisect_session.log
git bisect start
# status: waiting for both good and bad commits
git bisect bad HEAD
git bisect good v2.0.0
git bisect bad a8b7c6d
# ...

$ git bisect reset
# Boshqa kunda yoki boshqa kompyuterda:
$ git bisect replay bisect_session.log
# Git avtomatik ravishda barcha qadamlarni qayta bajaradi va xuddi
# shu nuqtada davom etish uchun tayyor bo'ladi.

# ============================================================
# 9) bisect'ni worktree bilan birlashtirish
# ============================================================
$ git worktree add ../bisect-wt main
$ cd ../bisect-wt
$ git bisect start
$ git bisect bad HEAD
$ git bisect good v1.4.0
$ git bisect run ./check_bug.sh
f4e5d6c7 is the first bad commit
$ git bisect reset
$ cd ../repo
$ git worktree remove ../bisect-wt
# Asosiy papkadagi tugallanmagan ishga umuman tegilmadi.
""".strip()

L4_CODE_RU = """
# ============================================================
# 1) Запуск bisect
# ============================================================
$ git bisect start
$ git bisect bad                    # HEAD — текущее, сломанное состояние
$ git bisect good v1.4.0            # в теге 1.4.0 всё работало
Bisecting: 99 revisions left to test after this (roughly 7 steps)
[7c3a1e9...] refactor: переписан модуль оплаты

# ============================================================
# 2) Проверка на каждом шаге
# ============================================================
$ pytest tests/test_payment.py -q
# FAILED tests/test_payment.py::test_discount_applies
$ git bisect bad
Bisecting: 49 revisions left to test after this (roughly 6 steps)
[a8b7c6d...] feat: логика расчёта скидки

$ pytest tests/test_payment.py -q
# 3 passed
$ git bisect good
Bisecting: 24 revisions left to test after this (roughly 5 steps)
[...]

# ... через ещё несколько шагов:
$ git bisect bad
Bisecting: 0 revisions left to test after this (roughly 0 steps)

# ============================================================
# 3) Итоговый результат
# ============================================================
$ git bisect bad
f4e5d6c7 is the first bad commit
commit f4e5d6c7a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
Author: Dev <dev@example.com>
Date:   Mon Jul 20 14:00:00 2026 +0500

    fix: валидация процента скидки

 app/services/payment_service.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)

$ git bisect reset
Previous HEAD position was f4e5d6c... fix: валидация процента скидки
Switched to branch 'main'
# Вернулись на исходную ветку, режим bisect завершён.

# ============================================================
# 4) git bisect run — полная автоматизация
# ============================================================
$ cat check_bug.sh
#!/bin/bash
pytest tests/test_payment.py -q -k test_discount_applies
exit $?

$ git bisect start HEAD v1.4.0
$ git bisect run ./check_bug.sh
running ./check_bug.sh
Bisecting: 99 revisions left to test after this (roughly 7 steps)
running ./check_bug.sh
...
f4e5d6c7 is the first bad commit
bisect run success
# Без участия человека — Git запускает скрипт на каждом коммите, по коду
# выхода сам решает good/bad.

# ============================================================
# 5) skip — для коммитов, которые нельзя проверить
# ============================================================
$ git bisect good
Bisecting: 12 revisions left to test after this (roughly 4 steps)
[abc1234] chore: обновление зависимостей (сборка сломана, проверить нельзя)

$ npm install
# ERROR: package-lock.json не совпадает, сборка не работает
$ git bisect skip
Bisecting: 12 revisions left to test after this (roughly 4 steps)
[def5678] другой коммит — этот соберётся

$ pytest tests/test_payment.py -q
# 3 passed
$ git bisect good
# ... продолжается, пропущенный коммит не учитывается.

# ============================================================
# 6) Расчёт log2(N) — почему это быстро
# ============================================================
$ python3 -c "import math; print(math.log2(200))"
7.643856189774724
# Для 200 коммитов достаточно ~8 проверок — сравните с линейным поиском
# (200 попыток): в 25 раз меньше работы.

# ============================================================
# 7) Поиск регрессии производительности со спец-терминами
# ============================================================
$ git bisect start --term-old=fast --term-new=slow
$ git bisect slow HEAD
$ git bisect fast v2.0.0
Bisecting: 49 revisions left to test after this (roughly 6 steps)
$ ./benchmark.sh
# результат: 340ms (порог 200ms)
$ git bisect slow
$ ./benchmark.sh
# результат: 120ms
$ git bisect fast
# ... продолжается, вместо "good"/"bad" используются "fast"/"slow".

# ============================================================
# 8) bisect log и replay — сохранение сессии
# ============================================================
$ git bisect log > bisect_session.log
$ cat bisect_session.log
git bisect start
# status: waiting for both good and bad commits
git bisect bad HEAD
git bisect good v2.0.0
git bisect bad a8b7c6d
# ...

$ git bisect reset
# В другой день или на другом компьютере:
$ git bisect replay bisect_session.log
# Git автоматически повторяет все шаги и готов продолжить с той же точки.

# ============================================================
# 9) Совмещение bisect с worktree
# ============================================================
$ git worktree add ../bisect-wt main
$ cd ../bisect-wt
$ git bisect start
$ git bisect bad HEAD
$ git bisect good v1.4.0
$ git bisect run ./check_bug.sh
f4e5d6c7 is the first bad commit
$ git bisect reset
$ cd ../repo
$ git worktree remove ../bisect-wt
# Незавершённая работа в основной папке вообще не была затронута.
""".strip()

L4_TASK = {
    "task_title": "bisect run bilan xato commit'ini avtomatik toping",
    "task_title_ru": "Найдите баг-коммит автоматически через bisect run",
    "task_description": (
        "Kamida 15 ta commit'li repo yarating, ularning biri (o'rtada) "
        "ataylab bitta funksiyani buzsin (masalan noto'g'ri natija "
        "qaytarsin). Sodda pytest testi yozing, u shu funksiyani "
        "tekshiradi. `git bisect start`, `git bisect bad/good` bilan "
        "QO'LDA kamida 3 marta qadam bosing, so'ngra `git bisect run "
        "<skript>` bilan JARAYONNI QAYTA, endi AVTOMATIK bajaring va "
        "ikkalasining natijasi bir xil ekanini tekshiring."
    ),
    "task_description_ru": (
        "Создайте репозиторий минимум с 15 коммитами, один из них (в "
        "середине) намеренно ломает одну функцию (например, возвращает "
        "неверный результат). Напишите простой pytest-тест, проверяющий "
        "эту функцию. Через `git bisect start`, `git bisect bad/good` "
        "ВРУЧНУЮ сделайте минимум 3 шага, затем ПОВТОРИТЕ процесс через "
        "`git bisect run <скрипт>`, теперь АВТОМАТИЧЕСКИ, и убедитесь, "
        "что результат обоих совпадает."
    ),
    "task_requirements": (
        "1) Qo'lda bisect'ning har bir qadamidagi `git bisect` chiqishini "
        "hisobotga kiriting. 2) `git bisect log` natijasini keltiring. "
        "3) `git bisect run` orqali topilgan commit qo'lda topilgan "
        "commit bilan BIR XIL ekanini isbotlang."
    ),
    "task_requirements_ru": (
        "1) Включите в отчёт вывод `git bisect` на каждом ручном шаге. "
        "2) Приведите результат `git bisect log`. 3) Докажите, что "
        "коммит, найденный через `git bisect run`, СОВПАДАЕТ с найденным "
        "вручную."
    ),
    "task_technologies": "Git (bisect, bisect run), pytest",
    "task_deadline_days": 4,
}

L4_SAMPLE = {
    "title": "Namuna: avtomatik bisect skripti",
    "description": (
        "15 commitli sun'iy repo yaratadi, 10-commit'da xato kiritadi, "
        "so'ngra git bisect run orqali xato commit'ini avtomatik topadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "setup_bisect_demo.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf bisectdemo && mkdir bisectdemo && cd bisectdemo && git init -q\n\n"
                "cat > calc.py << 'EOF'\n"
                "def discount(price, percent):\n"
                "    return price - (price * percent / 100)\n"
                "EOF\n"
                "git add . && git commit -q -m \"c0: boshlang'ich calc.py\"\n\n"
                "for i in $(seq 1 9); do\n"
                "    echo \"# no-op $i\" >> calc.py\n"
                "    git add . && git commit -q -m \"c$i: kichik o'zgarish\"\n"
                "done\n\n"
                "# 10-commit — ATAYLAB XATO kiritamiz\n"
                "cat > calc.py << 'EOF'\n"
                "def discount(price, percent):\n"
                "    return price - percent  # BUG: foiz emas, to'g'ridan-to'g'ri ayirilmoqda\n"
                "EOF\n"
                "git add . && git commit -q -m \"c10: chegirma logikasini refaktoring qilish (BUG)\"\n\n"
                "for i in $(seq 11 14); do\n"
                "    echo \"# no-op $i\" >> calc.py\n"
                "    git add . && git commit -q -m \"c$i: kichik o'zgarish\"\n"
                "done\n\n"
                "cat > check_bug.sh << 'EOF'\n"
                "#!/bin/bash\n"
                "python3 -c \"from calc import discount; assert discount(100, 10) == 90\"\n"
                "exit $?\n"
                "EOF\n"
                "chmod +x check_bug.sh\n\n"
                "echo \"=== AVTOMATIK BISECT ===\"\n"
                "git bisect start HEAD $(git rev-list --max-parents=0 HEAD)\n"
                "git bisect run ./check_bug.sh\n"
                "git bisect reset\n"
            ),
        },
    ],
}

L4_EXERCISES = [
    {
        "title": "bisect algoritmi",
        "title_ru": "Алгоритм bisect",
        "description": "git bisect qaysi algoritmga asoslangan?",
        "description_ru": "На каком алгоритме основан git bisect?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ikkilik qidiruv (binary search)",
            "Chiziqli qidiruv (har bir commit'ni birma-bir)",
            "Tasodifiy tanlov",
            "Chuqurlikni birinchi aylanish (DFS)",
        ],
        "options_ru": [
            "Двоичный поиск (binary search)",
            "Линейный поиск (проверка каждого коммита по очереди)",
            "Случайный выбор",
            "Обход в глубину (DFS)",
        ],
        "correct_answers": "A",
        "hint": "Har bir qadam qolgan oraliqni yarmiga qisqartiradi.",
        "hint_ru": "Каждый шаг сокращает оставшийся интервал вдвое.",
        "explanation": "Shuning uchun 200 commit uchun ~8 tekshiruv yetarli — log2(200).",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "bisect qadamlarini tartiblang",
        "title_ru": "Расположите шаги bisect",
        "description": "git bisect'ning to'g'ri ish oqimini tartibga joylashtiring.",
        "description_ru": "Расположите правильный рабочий процесс git bisect.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git bisect start",
            "git bisect bad (hozirgi holatni belgilash)",
            "git bisect good <eski-sha>",
            "Har bir taklif qilingan commit'da sinash va good/bad deyish",
            "git bisect reset",
        ],
        "drag_items_ru": [
            "git bisect start",
            "git bisect bad (отметить текущее состояние)",
            "git bisect good <старый-sha>",
            "Проверка каждого предложенного коммита и good/bad",
            "git bisect reset",
        ],
        "correct_order": [
            "git bisect start",
            "git bisect bad (hozirgi holatni belgilash)",
            "git bisect good <eski-sha>",
            "Har bir taklif qilingan commit'da sinash va good/bad deyish",
            "git bisect reset",
        ],
        "hint": "Avval ikkala chegara belgilanadi, keyin takroriy tekshiruv, oxirida reset.",
        "hint_ru": "Сначала отмечаются обе границы, потом повторная проверка, в конце reset.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Nega bisect log2(N) tekshiruv talab qiladi",
        "title_ru": "Почему bisect требует log2(N) проверок",
        "description": "200 ta commit bo'lsa, git bisect nega taxminan 200 emas, atigi 8 ta tekshiruv talab qilishini tushuntiring.",
        "description_ru": "Объясните, почему при 200 коммитах git bisect требует не примерно 200, а всего около 8 проверок.",
        "exercise_type": "text_input",
        "expected_answer": "Har bir tekshiruv oraliqni ikki barobar qisqartiradi (ikkilik qidiruv), shuning uchun kerakli tekshiruvlar soni N emas, log2(N) ga teng.",
        "hint": "Har bir good/bad javobi qolgan nomzodlar sonini qanday o'zgartiradi?",
        "hint_ru": "Как каждый ответ good/bad меняет число оставшихся кандидатов?",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 5 — R1: Takrorlash (objects/refs/packfile/rebase/bisect)
# ---------------------------------------------------------------------------

L5_TEXT = """
<h3>Bu checkpoint nima uchun kerak</h3>
<p>0-4-darslarda siz Git'ning "parda ortidagi" mexanikasini ko'rdingiz:
obyektlar bazasi (blob/tree/commit), branch va HEAD'ning shunchaki fayl
ekanligi, packfile orqali siqish, interaktiv rebase orqali tarixni
tahrirlash, va bisect orqali xatoni ikkilik qidiruv bilan topish. Bu
qism yangi mavzu emas — bu 5 darsni BIR AMALIY LOYIHADA birlashtirib,
bilim uzuklarini tekshirish uchun.</p>

<h3>Qismlarning bir-biriga bog'liqligi</h3>
<p>Bu besh mavzu tasodifan ketma-ket kelmagan — ular bir-birini
to'ldiradi: obyektlar bazasi (0-dars) — Git nimani saqlashini tushuntiradi;
refs (1-dars) — o'sha obyektlarga qanday "nom" berilishini; packfile
(2-dars) — vaqt o'tishi bilan bu saqlash qanday optimallashishini;
interaktiv rebase (3-dars) — obyektlar darajasida tarix qanday QAYTA
yaratilishini (eski commit'lar YANGI SHA-1 bilan almashtiriladi — chunki
0-darsda ko'rganingizdek, kontent o'zgarsa xesh ham o'zgaradi); bisect
(4-dars) — shu grafikni samarali qidirish uchun ishlatishni.</p>

<h3>Eng ko'p uchraydigan tushunmovchiliklar — qayta ko'rib chiqamiz</h3>
<ul>
<li>"Git diff saqlaydi" — YO'Q, har bir commit to'liq snapshot (tree)
saqlaydi; diff faqat ko'rsatish uchun keyin hisoblanadi.</li>
<li>"Branch yaratish qimmat operatsiya" — YO'Q, bu bitta 41-baytli fayl
yozish, O(1), tarix hajmidan mustaqil.</li>
<li>"rebase -i faqat commit'larni ko'chiradi" — YO'Q, u pick/reword/edit/
squash/fixup/drop orqali TARIXNI TAHRIRLAYDI, shunchaki ko'chirish emas.</li>
<li>"bisect har bir commit'ni birma-bir tekshiradi" — YO'Q, u ikkilik
qidiruv bilan har safar oraliqni yarmiga qisqartiradi.</li>
</ul>

<h3>Amaliy stsenariy: hammasini birlashtirish</h3>
<p>Real vaziyatda ish oqimi shunday bo'ladi: siz xatoni <code>git
bisect run</code> bilan topasiz (4-dars) → topilgan commit'ni <code>git
cat-file -p</code> bilan tekshirasiz, u qaysi tree/blob'ga ishora
qilishini ko'rasiz (0-dars) → tuzatishni alohida branch'da qilasiz, bu
branch shunchaki yangi ref (1-dars) → tuzatish commit'larini <code>git
rebase -i --autosquash</code> bilan toza tarixga aylantirasiz (3-dars) →
oxir-oqibat bu barcha obyektlar <code>git gc</code> orqali packfile'ga
siqiladi (2-dars). Bitta uzun ish oqimi — besh dars, bitta izchil
tushuncha.</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Agar ikkita fayl bir xil kontentga ega bo'lsa, ular nechta blob
sifatida saqlanadi va nega?</li>
<li>Detached HEAD holatida commit qilingan ishni yo'qotmaslik uchun qaysi
buyruq yordam beradi?</li>
<li><code>git verify-pack -v</code> chiqishida bitta obyekt boshqasidan
"delta" sifatida ko'rsatilsa, bu nimani anglatadi?</li>
<li><code>fixup</code> va <code>drop</code> orasidagi asosiy farq nima —
ikkalasi ham commit'ni "yo'qotadi"mi?</li>
<li>Nega <code>git bisect</code> N ta commit uchun N emas, balki
<code>log2(N)</code> tekshiruv talab qiladi?</li>
</ul>

<h3>Qo'shimcha stsenariy: nega bu besh dars birga o'qitiladi</h3>
<p>Ko'p talabalar "obyektlar bazasi" va "bisect" orasida bevosita bog'liq
yo'qdek tuyuladi, deb o'ylashadi — aslida ular bir grafning ikki
tomoni: obyektlar bazasi (0-dars) GRAFNI (commit'lar zanjirini) hosil
qiladi, bisect (4-dars) esa aynan shu GRAF ustida ikkilik qidiruv
o'tkazadi. Xuddi shunday, refs (1-dars) grafning qaysi nuqtalari "muhim"
(branch, tag) ekanligini belgilaydi, rebase (3-dars) esa grafni QAYTA
QURADI — yangi commit'lar, yangi SHA-1lar bilan. Packfile (2-dars) esa
bu grafning FIZIK saqlanishini optimallashtiradi. Beshtasi ham — bitta
model ustida ishlaydigan besh xil operatsiya.</p>

<h3>Yana bir amaliy misol: eski xatoni topib, tarixni tozalash</h3>
<p>Aytaylik, 6 oy oldin yozilgan funksiyada nozik xato bor va u faqat
hozir sezildi. Ish oqimi: <code>git bisect start</code> bilan qidiruvni
boshlaysiz, <code>git bisect good</code>/<code>bad</code> bilan
oralig'ingizni toraytirasiz (har safar Git avtomatik commit'ni checkout
qiladi — bu checkout paytida u sizning HEAD faylingizni, demak
<code>.git/HEAD</code>ni, YANGILAYDI, aynan 1-darsda ko'rgan mexanizm
orqali). Topilgan commit'ning tree'sini <code>cat-file</code> bilan
ochib, xato QAYERDA ekanligini aniq ko'rasiz. Tuzatishni bir necha kichik
commit bilan yozasiz, so'ng ularni <code>rebase -i</code> bilan bitta
mantiqiy commit'ga aylantirasiz — bu YANGI commit YANGI SHA-1 oladi
(0-darsdagi "kontent o'zgarsa, xesh o'zgaradi" qoidasi). Push qilishdan
oldin <code>--force-with-lease</code> ishlatasiz. Va nihoyat, oylar
o'tib, bu va boshqa minglab commit <code>git gc</code> orqali
packfile'ga siqiladi.</p>
""".strip()

L5_TEXT_RU = """
<h3>Зачем нужен этот checkpoint</h3>
<p>В уроках 0-4 вы увидели "закулисную" механику Git: базу объектов
(blob/tree/commit), что ветка и HEAD — это просто файлы, сжатие через
packfile, редактирование истории через интерактивный rebase, и поиск
бага через двоичный поиск с bisect. Этот раздел — не новая тема, а
объединение этих 5 уроков в ОДНОМ практическом проекте для проверки
пробелов в знаниях.</p>

<h3>Как части связаны друг с другом</h3>
<p>Эти пять тем идут подряд не случайно — они дополняют друг друга: база
объектов (урок 0) объясняет, ЧТО хранит Git; refs (урок 1) — как этим
объектам даётся "имя"; packfile (урок 2) — как это хранение оптимизируется
со временем; интерактивный rebase (урок 3) — как история ПЕРЕСОЗДАЁТСЯ на
уровне объектов (старые коммиты заменяются НОВЫМ SHA-1 — потому что, как
вы видели в уроке 0, при изменении содержимого меняется и хеш); bisect
(урок 4) — как эффективно искать по этому графу.</p>

<h3>Самые частые заблуждения — пересмотрим</h3>
<ul>
<li>"Git хранит diff" — НЕТ, каждый коммит хранит полный snapshot (tree);
diff вычисляется только для показа, позже.</li>
<li>"Создание ветки — дорогая операция" — НЕТ, это запись одного файла в
41 байт, O(1), независимо от размера истории.</li>
<li>"rebase -i только перемещает коммиты" — НЕТ, он РЕДАКТИРУЕТ ИСТОРИЮ
через pick/reword/edit/squash/fixup/drop, а не просто перемещает.</li>
<li>"bisect проверяет каждый коммит по очереди" — НЕТ, он использует
двоичный поиск, каждый раз сокращая интервал вдвое.</li>
</ul>

<h3>Практический сценарий: объединяем всё</h3>
<p>В реальной ситуации рабочий процесс выглядит так: вы находите баг
через <code>git bisect run</code> (урок 4) → проверяете найденный коммит
через <code>git cat-file -p</code>, видите, на какой tree/blob он
указывает (урок 0) → делаете исправление в отдельной ветке, которая
просто новый ref (урок 1) → превращаете коммиты исправления в чистую
историю через <code>git rebase -i --autosquash</code> (урок 3) → в итоге
все эти объекты сжимаются в packfile через <code>git gc</code> (урок 2).
Один длинный рабочий процесс — пять уроков, одно связное понимание.</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Если два файла имеют одинаковое содержимое, сколько blob'ов они
образуют и почему?</li>
<li>Какая команда помогает не потерять работу, закоммиченную в состоянии
detached HEAD?</li>
<li>Что означает, если в выводе <code>git verify-pack -v</code> один
объект показан как "delta" от другого?</li>
<li>В чём главное отличие между <code>fixup</code> и <code>drop</code> —
разве оба не "теряют" коммит?</li>
<li>Почему <code>git bisect</code> требует не N, а <code>log2(N)</code>
проверок для N коммитов?</li>
</ul>

<h3>Дополнительный сценарий: почему эти пять уроков изучаются вместе</h3>
<p>Многие студенты думают, что "база объектов" и "bisect" не связаны
напрямую — на самом деле это две стороны одного графа: база объектов
(урок 0) СОЗДАЁТ граф (цепочку коммитов), bisect (урок 4) же проводит
именно по этому ГРАФУ двоичный поиск. Аналогично, refs (урок 1)
определяют, какие точки графа "важны" (ветка, тег), rebase (урок 3)
ПЕРЕСТРАИВАЕТ граф — с новыми коммитами, новыми SHA-1. Packfile (урок 2)
оптимизирует ФИЗИЧЕСКОЕ хранение этого графа. Все пять — пять разных
операций над одной моделью.</p>

<h3>Ещё один практический пример: находим старый баг и чистим историю</h3>
<p>Предположим, в функции, написанной 6 месяцев назад, есть тонкий баг,
и он замечен только сейчас. Рабочий процесс: начинаете поиск через
<code>git bisect start</code>, сужаете интервал через <code>git bisect
good</code>/<code>bad</code> (каждый раз Git автоматически делает
checkout коммита — при этом checkout ОБНОВЛЯЕТ ваш файл HEAD, то есть
<code>.git/HEAD</code>, именно через механизм из урока 1). Открыв tree
найденного коммита через <code>cat-file</code>, вы точно видите, ГДЕ
баг. Пишете исправление несколькими мелкими коммитами, затем превращаете
их в один логичный коммит через <code>rebase -i</code> — этот НОВЫЙ
коммит получает НОВЫЙ SHA-1 (правило из урока 0 "меняется содержимое —
меняется хеш"). Перед push используете <code>--force-with-lease</code>.
И наконец, спустя месяцы, этот и тысячи других коммитов сжимаются в
packfile через <code>git gc</code>.</p>
""".strip()

L5_CODE = """
# ============================================================
# Yakuniy amaliyot: besh mavzuni bitta stsenariyda ishlatish
# ============================================================

# 1) Xato bor deb faraz qilamiz, uni bisect bilan topamiz (4-dars)
$ git bisect start
$ git bisect bad HEAD
$ git bisect good v2.0.0
$ git bisect run ./check_bug.sh
a1b2c3d4 is the first bad commit
$ git bisect reset

# 2) Topilgan commit'ni obyekt darajasida tekshiramiz (0-dars)
$ git cat-file -p a1b2c3d4
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d
parent 0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
author Dev <dev@example.com> 1706000000 +0500

fix: chegirma hisoblashda xato

$ git cat-file -p 9f8e7d6c | grep payment
100644 blob 5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b    payment_service.py

# 3) Tuzatish uchun yangi branch — bu shunchaki yangi ref (1-dars)
$ git switch -c fix/discount-bug a1b2c3d4^   # xato commit'dan OLDINGI holatdan
$ cat .git/refs/heads/fix/discount-bug
0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b

# 4) Tuzatishni bir necha kichik commit bilan yozamiz
$ vim payment_service.py && git commit -am "urinish 1"
$ vim payment_service.py && git commit -am "yana tuzatish"
$ vim payment_service.py && git commit -am "test qo'shildi"

# 5) Interaktiv rebase bilan toza commit'ga aylantiramiz (3-dars)
$ git rebase -i HEAD~3
# pick + squash + squash -> bitta commit:
$ git log --oneline -1
e5f6a7b8 fix: chegirma hisoblash formulasi tuzatildi (test bilan)

# 6) Force-push xavfsiz usulda
$ git push --force-with-lease origin fix/discount-bug

# 7) Vaqt o'tib, bu tarix boshqa ko'plab commit bilan birga
#    packfile'ga siqiladi (2-dars) — buni qo'lda ham tekshirish mumkin:
$ git gc
$ git count-objects -v
count: 0
in-pack: 512
packs: 1

# ============================================================
# O'z-o'zini tekshirish: interaktiv jadval
# ============================================================
# | Savol                                    | Javob qayerda?    |
# |-------------------------------------------|-------------------|
# | Bir xil kontent -> nechta blob?           | 0-dars, 3-bo'lim  |
# | Branch nima o'zi, texnik jihatdan?        | 1-dars, 1-bo'lim  |
# | verify-pack'da "delta" nima anglatadi?    | 2-dars, 3-bo'lim  |
# | fixup vs drop farqi?                      | 3-dars, buyruqlar |
# | Nega bisect log2(N)?                      | 4-dars, 2-bo'lim  |

# ============================================================
# Qo'shimcha tekshiruv: har bir bosqichni alohida tasdiqlash
# ============================================================
$ git cat-file -t a1b2c3d4
commit
$ git cat-file -p a1b2c3d4 | head -1
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d

$ cat .git/refs/heads/fix/discount-bug
0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
$ wc -c .git/refs/heads/fix/discount-bug
41 .git/refs/heads/fix/discount-bug

$ git rebase -i HEAD~3
$ git log --oneline -1 --format='%H'
e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
# Diqqat: bu SHA-1 hech qachon oldin ko'rilmagan — chunki kontent
# (xabar + tree + parent) o'zgargani uchun butunlay yangi obyekt.

$ git verify-pack -v .git/objects/pack/*.idx 2>/dev/null | wc -l
512
# gc'dan keyin barcha obyektlar (eski VA yangi) bitta pack ichida.

$ git count-objects -v
count: 0
in-pack: 512
packs: 1
size-pack: 148
# "count: 0" — loose obyekt qolmadi, hammasi "in-pack"da. Bu 0-4-darslarda
# ko'rgan har bir amal (blob yaratish, tree qurish, commit yozish, ref
# yangilash, bisect orqali qidirish, rebase orqali qayta yozish) oxir-oqibat
# aynan shu bitta obyektlar bazasida iz qoldiradi — packfile esa bu izlarni
# vaqt o'tishi bilan ixcham saqlash usuli, xolos.
""".strip()

L5_CODE_RU = """
# ============================================================
# Итоговая практика: применяем пять тем в одном сценарии
# ============================================================

# 1) Предполагаем баг, находим его через bisect (урок 4)
$ git bisect start
$ git bisect bad HEAD
$ git bisect good v2.0.0
$ git bisect run ./check_bug.sh
a1b2c3d4 is the first bad commit
$ git bisect reset

# 2) Проверяем найденный коммит на уровне объектов (урок 0)
$ git cat-file -p a1b2c3d4
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d
parent 0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
author Dev <dev@example.com> 1706000000 +0500

fix: ошибка в расчёте скидки

$ git cat-file -p 9f8e7d6c | grep payment
100644 blob 5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b    payment_service.py

# 3) Новая ветка для исправления — это просто новый ref (урок 1)
$ git switch -c fix/discount-bug a1b2c3d4^   # с состояния ДО бага
$ cat .git/refs/heads/fix/discount-bug
0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b

# 4) Пишем исправление несколькими мелкими коммитами
$ vim payment_service.py && git commit -am "попытка 1"
$ vim payment_service.py && git commit -am "ещё исправление"
$ vim payment_service.py && git commit -am "добавлен тест"

# 5) Через интерактивный rebase превращаем в чистый коммит (урок 3)
$ git rebase -i HEAD~3
# pick + squash + squash -> один коммит:
$ git log --oneline -1
e5f6a7b8 fix: исправлена формула расчёта скидки (с тестом)

# 6) Безопасный force-push
$ git push --force-with-lease origin fix/discount-bug

# 7) Со временем эта история вместе со многими другими коммитами
#    сжимается в packfile (урок 2) — можно проверить вручную:
$ git gc
$ git count-objects -v
count: 0
in-pack: 512
packs: 1

# ============================================================
# Самопроверка: интерактивная таблица
# ============================================================
# | Вопрос                                     | Где ответ?        |
# |---------------------------------------------|--------------------|
# | Одинаковое содержимое -> сколько blob?       | Урок 0, раздел 3   |
# | Что такое ветка технически?                  | Урок 1, раздел 1   |
# | Что значит "delta" в verify-pack?            | Урок 2, раздел 3   |
# | Разница fixup и drop?                        | Урок 3, команды    |
# | Почему bisect даёт log2(N)?                  | Урок 4, раздел 2   |

# ============================================================
# Дополнительная проверка: подтверждение каждого шага отдельно
# ============================================================
$ git cat-file -t a1b2c3d4
commit
$ git cat-file -p a1b2c3d4 | head -1
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d

$ cat .git/refs/heads/fix/discount-bug
0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
$ wc -c .git/refs/heads/fix/discount-bug
41 .git/refs/heads/fix/discount-bug

$ git rebase -i HEAD~3
$ git log --oneline -1 --format='%H'
e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
# Внимание: этот SHA-1 никогда раньше не встречался — потому что
# содержимое (сообщение + tree + parent) изменилось, значит это
# совершенно новый объект.

$ git verify-pack -v .git/objects/pack/*.idx 2>/dev/null | wc -l
512
# После gc все объекты (старые И новые) в одном pack.

$ git count-objects -v
count: 0
in-pack: 512
packs: 1
size-pack: 148
# "count: 0" — loose-объектов не осталось, все в "in-pack". Каждое
# действие из уроков 0-4 (создание blob, построение tree, запись commit,
# обновление ref, поиск через bisect, переписывание через rebase) в
# итоге оставляет след именно в этой единой базе объектов — packfile же
# лишь способ компактно хранить эти следы со временем.
""".strip()

L5_TASK = {
    "task_title": "R1 capstone-mini: bisect -> obyekt -> rebase -> gc",
    "task_title_ru": "R1 мини-капстоун: bisect -> объект -> rebase -> gc",
    "task_description": (
        "Sun'iy repo yarating (kamida 20 commit, birida ataylab xato). "
        "Quyidagi to'liq zanjirni bajaring: (1) `git bisect run` bilan "
        "xato commit'ini toping, (2) `git cat-file -p` bilan uning "
        "tree/blob'larini tekshiring, (3) tuzatish uchun yangi branch "
        "oching va kamida 3 ta kichik commit qiling, (4) `git rebase -i` "
        "bilan ularni bitta toza commit'ga aylantiring, (5) `git gc` "
        "ishga tushirib, natijada obyektlar sonini `count-objects -v` "
        "bilan ko'rsating."
    ),
    "task_description_ru": (
        "Создайте искусственный репозиторий (минимум 20 коммитов, в "
        "одном намеренная ошибка). Выполните полную цепочку: (1) "
        "найдите баг-коммит через `git bisect run`, (2) проверьте его "
        "tree/blob через `git cat-file -p`, (3) откройте новую ветку для "
        "исправления и сделайте минимум 3 мелких коммита, (4) через `git "
        "rebase -i` превратите их в один чистый коммит, (5) запустите "
        "`git gc` и покажите итоговое число объектов через "
        "`count-objects -v`."
    ),
    "task_requirements": (
        "1) Har bir bosqichning buyruq + natija juftligi hisobotda "
        "bo'lishi shart (5 bosqich). 2) Yakuniy `git log --oneline` "
        "toza, mantiqiy tarixni ko'rsatishi kerak. 3) gc'dan oldin va "
        "keyingi `count-objects -v` solishtirilgan bo'lishi kerak."
    ),
    "task_requirements_ru": (
        "1) В отчёте должна быть пара команда+результат для каждого из "
        "5 шагов. 2) Финальный `git log --oneline` должен показывать "
        "чистую, логичную историю. 3) Должно быть сравнение "
        "`count-objects -v` до и после gc."
    ),
    "task_technologies": "Git (bisect, cat-file, rebase -i, gc)",
    "task_deadline_days": 5,
}

L5_SAMPLE = {
    "title": "Namuna: R1 to'liq zanjir skripti",
    "description": (
        "Bitta bash skripti besh darsning barcha g'oyalarini ketma-ket "
        "bajaradi: xato bilan repo yaratish, bisect orqali topish, "
        "obyektni tekshirish, tuzatish branch'ini rebase bilan tozalash, "
        "va gc bilan yakunlash."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "r1_full_chain.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "export GIT_EDITOR=true\n\n"
                "rm -rf r1demo && mkdir r1demo && cd r1demo && git init -q\n\n"
                "echo 'def add(a, b): return a + b' > mathlib.py\n"
                "git add . && git commit -q -m \"c0\"\n"
                "for i in $(seq 1 8); do echo \"# no-op $i\" >> mathlib.py; git add .; git commit -q -m \"c$i\"; done\n\n"
                "echo 'def add(a, b): return a - b  # BUG' > mathlib.py\n"
                "git add . && git commit -q -m \"c9: BUG kiritildi\"\n"
                "for i in $(seq 10 18); do echo \"# no-op $i\" >> mathlib.py; git add .; git commit -q -m \"c$i\"; done\n\n"
                "cat > check.sh << 'EOF'\n"
                "#!/bin/bash\n"
                "python3 -c \"from mathlib import add; assert add(2,2)==4\"\n"
                "EOF\n"
                "chmod +x check.sh\n\n"
                "echo \"== 1) BISECT ==\"\n"
                "git bisect start HEAD $(git rev-list --max-parents=0 HEAD)\n"
                "git bisect run ./check.sh | tail -3\n"
                "BUGSHA=$(git bisect view --format='%H' 2>/dev/null || git rev-parse refs/bisect/bad)\n"
                "git bisect reset\n\n"
                "echo \"== 2) OBYEKTNI TEKSHIRISH ==\"\n"
                "git cat-file -p \"$BUGSHA\" | head -3\n\n"
                "echo \"== 3-4) TUZATISH + REBASE ==\"\n"
                "git switch -q -c fix/mathlib \"$BUGSHA~1\"\n"
                "echo 'def add(a, b): return a + b' > mathlib.py\n"
                "git commit -qam \"urinish\"\n"
                "echo '# test qo\\047shildi' >> mathlib.py\n"
                "git commit -qam \"test\"\n"
                "GIT_SEQUENCE_EDITOR='sed -i \"2s/pick/squash/\"' git rebase -i HEAD~2\n"
                "git log --oneline -1\n\n"
                "echo \"== 5) GC ==\"\n"
                "git checkout -q main 2>/dev/null || git checkout -q master\n"
                "git count-objects -v\n"
                "git gc --quiet\n"
                "git count-objects -v\n"
            ),
        },
    ],
}

L5_EXERCISES = [
    {
        "title": "R1: obyekt saqlash mantig'i",
        "title_ru": "R1: логика хранения объектов",
        "description": "Ikkita commit bir xil faylning ikki xil versiyasini o'z ichiga olsa, Git ularni qanday saqlaydi?",
        "description_ru": "Если два коммита содержат две разные версии одного файла, как Git их хранит?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har biri uchun alohida blob, keyin gc paytida delta sifatida siqiladi",
            "Ikkalasi bitta blob sifatida majburan birlashtiriladi",
            "Faqat oxirgi versiya saqlanadi, eskisi o'chiriladi",
            "Ikkalasi ham tashqi faylga eksport qilinadi",
        ],
        "options_ru": [
            "Каждая как отдельный blob, позже сжимается как delta при gc",
            "Обе принудительно объединяются в один blob",
            "Сохраняется только последняя версия, старая удаляется",
            "Обе экспортируются во внешний файл",
        ],
        "correct_answers": "A",
        "hint": "0 va 2-darslarni birlashtiring: har bir kontent alohida blob, keyin siqiladi.",
        "hint_ru": "Объедините уроки 0 и 2: каждое содержимое — отдельный blob, потом сжимается.",
        "explanation": "Har bir versiya alohida blob sifatida yoziladi; gc keyinroq ularni delta orqali siqadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "R1: to'liq ish oqimini tartiblang",
        "title_ru": "R1: расположите полный рабочий процесс",
        "description": "Xatoni topishdan tozalashgacha bo'lgan to'g'ri ketma-ketlikni joylashtiring.",
        "description_ru": "Расположите правильную последовательность от обнаружения бага до очистки.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git bisect run bilan xato commit'ini topish",
            "git cat-file -p bilan obyektni tekshirish",
            "Tuzatish uchun yangi branch (ref) ochish",
            "git rebase -i bilan commit'larni tozalash",
            "git gc bilan obyektlarni siqish",
        ],
        "drag_items_ru": [
            "Найти баг-коммит через git bisect run",
            "Проверить объект через git cat-file -p",
            "Открыть новую ветку (ref) для исправления",
            "Очистить коммиты через git rebase -i",
            "Сжать объекты через git gc",
        ],
        "correct_order": [
            "git bisect run bilan xato commit'ini topish",
            "git cat-file -p bilan obyektni tekshirish",
            "Tuzatish uchun yangi branch (ref) ochish",
            "git rebase -i bilan commit'larni tozalash",
            "git gc bilan obyektlarni siqish",
        ],
        "hint": "0-4-darslar tartibi aynan shu ish oqimiga mos keladi.",
        "hint_ru": "Порядок уроков 0-4 точно соответствует этому рабочему процессу.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "R1: force-with-lease nega tanlanadi",
        "title_ru": "R1: почему выбирают force-with-lease",
        "description": "rebase -i'dan keyin jamoaviy branch'ga push qilishda oddiy --force o'rniga --force-with-lease ishlatishning sababini yozing.",
        "description_ru": "Опишите, почему после rebase -i при push в общую ветку используют --force-with-lease вместо обычного --force.",
        "exercise_type": "text_input",
        "expected_answer": "force-with-lease remote holatini tekshirib, boshqa birov orada push qilgan bo'lsa, xavfsiz rad etadi; oddiy force esa tekshirmasdan hamkasb ishini yo'qotib qo'yishi mumkin.",
        "hint": "3-darsdagi xavfsizlik bo'limini eslang.",
        "hint_ru": "Вспомните раздел про безопасность из урока 3.",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 6 — git worktree: bir vaqtda bir nechta branch ustida ishlash
# ---------------------------------------------------------------------------

L6_TEXT = """
<h3>Muammo: stash qilmasdan branch almashtirish mumkinmi?</h3>
<p>45-kursda <code>git stash</code>ni "tugallanmagan ishni vaqtincha
yashirish" vositasi sifatida o'rgangansiz — chunki bitta ishchi papkada
(working directory) faqat BITTA branch faylini bir vaqtning o'zida ko'ra
olasiz. Tasavvur qiling: <code>feature-payment</code> ustida ishlayapsiz,
birdan production'da o'ta muhim xato (hotfix) chiqadi. Stash qilib,
branch almashtirib, tuzatib, qaytib, stash pop qilish — bir necha qadam,
va agar stash konflikt qilsa, yanada murakkab. <code>git worktree</code> bu
muammoni butunlay boshqacha yechadi: stash umuman kerak emas.</p>

<h3>Worktree nima: bitta repo, bir nechta ishchi papka</h3>
<p><code>git worktree add</code> — bitta <code>.git/</code> obyektlar
bazasiga ULANGAN, lekin ALOHIDA ishchi papka va ALOHIDA index yaratadi.
Har bir worktree o'zining branch'ida turadi (bitta branch bir vaqtda
faqat BITTA worktree'da checkout qilingan bo'lishi mumkin — Git buni
qat'iy ta'qiqlaydi, ikki joyda bir xil branch'ni checkout qilib bo'lmaydi).
Obyektlar bazasi, refs, config — HAMMASI ulashiladi; faqat ishchi fayllar
va index'gina har bir worktree uchun alohida.</p>

<h3>Nima uchun bu stash'dan tubdan farq qiladi</h3>
<p>Stash — vaqtinchalik, "yashirin" holat; worktree — HAQIQIY, alohida
papka, istalgan vaqt ochiq turishi mumkin. Amaliy natija: endi
<code>feature-payment</code> papkasida hech narsaga tegmasdan, alohida
<code>../hotfix</code> papkasida <code>hotfix</code> branch'ini ochib,
tuzatib, commit qilib, push qilish mumkin — birinchi papkadagi
tugallanmagan o'zgarishlar hech qachon stash'ga tushmaydi.</p>

<h3>.git/worktrees/ — ichki mexanizm</h3>
<p>Asosiy worktree'dagi <code>.git/</code> odatdagidek to'liq papka.
Qo'shimcha worktree'lar esa o'zining <code>.git</code> FAYLINI (papka
emas!) oladi — u faqat asosiy repo'ga ishora qiladi:
<code>gitdir: /path/to/main/.git/worktrees/hotfix</code>. Asosiy
<code>.git/worktrees/hotfix/</code> ichida esa o'sha worktree'ning
alohida <code>HEAD</code>, <code>index</code> va <code>logs/</code> fayllari
saqlanadi — obyektlar bazasi esa asosiy joydan ulashiladi.</p>

<h3>Bitta repo, bir nechta ishchi papka — vizual</h3>
<pre class="mermaid">
flowchart TB
  subgraph shared ["ULASHILGAN"]
    OBJ[".git/objects/
(barcha commit/tree/blob)"]
    REFS[".git/refs/
(barcha branch)"]
  end
  subgraph wt1 ["Asosiy worktree: ~/repo"]
    B1["branch: feature-payment"]
    F1["ishchi fayllar + index"]
  end
  subgraph wt2 ["Qo'shimcha worktree: ~/repo-hotfix"]
    B2["branch: hotfix"]
    F2["ishchi fayllar + index"]
  end
  wt1 -.->|"o'qish/yozish"| shared
  wt2 -.->|"o'qish/yozish"| shared
  style shared fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Diagramma shuni ko'rsatadi: ikkala jismoniy papka ham BITTA obyektlar
bazasi va ref to'plamiga ulanadi, lekin har birining o'z branch'i, o'z
ishchi fayllari va o'z index'i bor — bir-biriga umuman xalaqit
bermaydi.</p>

<h3>Amaliy foydalanish holatlari</h3>
<ul>
<li><strong>Shoshilinch hotfix</strong> — asosiy ishni to'xtatmasdan
alohida papkada tuzatish.</li>
<li><strong>Uzoq test/build</strong> — bitta worktree'da testlar
ishlayotganda, boshqasida kod yozishni davom ettirish.</li>
<li><strong>PR ko'rib chiqish</strong> — kimningdir branch'ini alohida
worktree'da ochib, o'z ishingizga tegmasdan sinab ko'rish.</li>
</ul>
<p><code>git worktree remove</code> tugagach worktree'ni tozalab
o'chiradi (ishchi fayllar bilan birga); <code>git worktree list</code>
barcha faol worktree'larni ko'rsatadi; <code>git worktree prune</code> esa
qo'lda o'chirilgan (papka <code>rm -rf</code> qilingan, lekin Git hali
bilmagan) worktree yozuvlarini tozalaydi.</p>

<h3>Worktree'ni qulflash — tashqi disk yoki uzoq muddatli worktree uchun</h3>
<p>Agar worktree tashqi diskda yoki tarmoq orqali ulangan papkada bo'lsa,
uni tasodifan <code>git worktree prune</code> orqali "yo'qolgan" deb
hisoblab tozalab yubormaslik uchun <code>git worktree lock
&lt;path&gt; --reason "tashqi disk, uzoq muddat kerak"</code> ishlatiladi.
Qulflangan worktree <code>prune</code> tomonidan HECH QACHON avtomatik
o'chirilmaydi, faqat <code>git worktree unlock</code> orqali qo'lda
ochiladi.</p>

<h3>Skript uchun --porcelain formati</h3>
<p><code>git worktree list --porcelain</code> odatiy formatdan farqli,
avtomatlashtirilgan skriptlar uchun barqaror, mashina o'qiy oladigan
formatda chiqadi (har bir maydon alohida qatorda, bo'sh qator bilan
ajratilgan) — CI skriptlari yoki IDE integratsiyalari odatda shu
formatdan foydalanadi, chunki odatiy formatning ustun kengligi Git
versiyasiga qarab o'zgarishi mumkin.</p>
""".strip()

L6_TEXT_RU = """
<h3>Проблема: можно ли переключить ветку без stash?</h3>
<p>В курсе 45 вы изучили <code>git stash</code> как способ "временно
спрятать" незавершённую работу — потому что в одной рабочей директории
(working directory) можно видеть только ОДНУ ветку одновременно.
Представьте: вы работаете над <code>feature-payment</code>, внезапно в
production появляется критический баг (hotfix). Сделать stash,
переключить ветку, исправить, вернуться, stash pop — несколько шагов, а
если stash конфликтует, ещё сложнее. <code>git worktree</code> решает эту
проблему совершенно иначе: stash вообще не нужен.</p>

<h3>Что такое worktree: один репозиторий, несколько рабочих папок</h3>
<p><code>git worktree add</code> создаёт ОТДЕЛЬНУЮ рабочую папку и
ОТДЕЛЬНЫЙ index, СВЯЗАННЫЕ с одной базой объектов <code>.git/</code>.
Каждый worktree находится на своей ветке (одна ветка может быть
checkout'нута только в ОДНОМ worktree одновременно — Git это строго
запрещает, нельзя checkout'нуть одну и ту же ветку в двух местах). База
объектов, refs, config — ВСЁ разделяется; только рабочие файлы и index
отдельные для каждого worktree.</p>

<h3>Почему это принципиально отличается от stash</h3>
<p>Stash — временное, "скрытое" состояние; worktree — НАСТОЯЩАЯ, отдельная
папка, может оставаться открытой сколько угодно. Практический результат:
теперь в папке <code>../hotfix</code> можно, не трогая
<code>feature-payment</code>, открыть ветку <code>hotfix</code>,
исправить, закоммитить, запушить — незавершённые изменения в первой
папке никогда не попадают в stash.</p>

<h3>.git/worktrees/ — внутренний механизм</h3>
<p><code>.git/</code> в основном worktree — обычная полная папка.
Дополнительные worktree получают собственный ФАЙЛ <code>.git</code> (не
папку!) — он лишь указывает на основной репозиторий:
<code>gitdir: /path/to/main/.git/worktrees/hotfix</code>. А внутри
основной <code>.git/worktrees/hotfix/</code> хранятся собственные
<code>HEAD</code>, <code>index</code> и <code>logs/</code> этого
worktree — база объектов же разделяется из основного места.</p>

<h3>Один репозиторий, несколько рабочих папок — визуально</h3>
<pre class="mermaid">
flowchart TB
  subgraph shared ["ОБЩЕЕ"]
    OBJ[".git/objects/
(все commit/tree/blob)"]
    REFS[".git/refs/
(все ветки)"]
  end
  subgraph wt1 ["Основной worktree: ~/repo"]
    B1["ветка: feature-payment"]
    F1["рабочие файлы + index"]
  end
  subgraph wt2 ["Доп. worktree: ~/repo-hotfix"]
    B2["ветка: hotfix"]
    F2["рабочие файлы + index"]
  end
  wt1 -.->|"чтение/запись"| shared
  wt2 -.->|"чтение/запись"| shared
  style shared fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Диаграмма показывает: обе физические папки подключены к ОДНОЙ базе
объектов и набору refs, но у каждой своя ветка, свои рабочие файлы и
свой index — они совершенно не мешают друг другу.</p>

<h3>Практические случаи использования</h3>
<ul>
<li><strong>Срочный hotfix</strong> — исправление в отдельной папке, не
останавливая основную работу.</li>
<li><strong>Долгий тест/сборка</strong> — пока в одном worktree работают
тесты, в другом можно продолжать писать код.</li>
<li><strong>Ревью PR</strong> — открыть чью-то ветку в отдельном
worktree и проверить, не трогая свою работу.</li>
</ul>
<p><code>git worktree remove</code> после завершения аккуратно удаляет
worktree (вместе с рабочими файлами); <code>git worktree list</code>
показывает все активные worktree; <code>git worktree prune</code>
очищает записи о worktree, удалённых вручную (папка удалена через <code>rm
-rf</code>, но Git ещё не знает об этом).</p>

<h3>Блокировка worktree — для внешнего диска или долгоживущего worktree</h3>
<p>Если worktree находится на внешнем диске или в папке, подключённой
по сети, чтобы случайно не "потерять" его через <code>git worktree
prune</code>, используется <code>git worktree lock &lt;path&gt;
--reason "внешний диск, нужен надолго"</code>. Заблокированный worktree
НИКОГДА не удаляется <code>prune</code> автоматически, разблокируется
только вручную через <code>git worktree unlock</code>.</p>

<h3>Формат --porcelain для скриптов</h3>
<p><code>git worktree list --porcelain</code> в отличие от обычного
формата, выводит в стабильном, машиночитаемом формате для
автоматизированных скриптов (каждое поле на отдельной строке, разделено
пустой строкой) — CI-скрипты или интеграции IDE обычно используют
именно этот формат, поскольку ширина колонок обычного формата может
меняться в зависимости от версии Git.</p>
""".strip()

L6_CODE = """
# ============================================================
# 1) Muammoni ko'rish: stash'siz branch almashtirib bo'lmaydi
# ============================================================
$ git status --short
 M app/services/payment_service.py
 M app/api/v1/endpoints/payments.py
# feature-payment ustida tugallanmagan ish bor, birdan hotfix kerak:
$ git switch main
error: Your local changes to the following files would be overwritten by checkout:
	app/services/payment_service.py
Please commit your changes or stash them before you switch branches.

# ============================================================
# 2) Worktree bilan yechim — stash umuman kerak emas
# ============================================================
$ git worktree add ../repo-hotfix main
Preparing worktree (checking out 'main')
HEAD is now at 3f2e1d0 fix: oldingi hotfix

$ ls ..
repo/  repo-hotfix/
$ cd ../repo-hotfix
$ git branch --show-current
main
$ git switch -c hotfix/urgent-bug
$ vim app/services/critical.py
$ git commit -am "hotfix: production'dagi kritik xato tuzatildi"
$ git push origin hotfix/urgent-bug

# Bu paytda birinchi papkada HECH NARSA o'zgarmagan:
$ cd ../repo
$ git status --short
 M app/services/payment_service.py
 M app/api/v1/endpoints/payments.py
# Xuddi shu, tegilmagan holatda — hotfix uchun stash/pop kerak bo'lmadi.

# ============================================================
# 3) Ichki mexanizmni tekshirish
# ============================================================
$ cat ../repo-hotfix/.git
gitdir: /home/user/repo/.git/worktrees/repo-hotfix
# Bu FAYL, papka emas — faqat asosiy repo'ga ishora.

$ ls .git/worktrees/
repo-hotfix
$ ls .git/worktrees/repo-hotfix/
HEAD  index  logs/  ORIG_HEAD  commondir  gitdir
$ cat .git/worktrees/repo-hotfix/HEAD
ref: refs/heads/hotfix/urgent-bug
# Har bir worktree o'z HEAD'iga ega, lekin refs/heads/ ULASHILGAN:
$ ls .git/refs/heads/
feature-payment  hotfix/  main

# ============================================================
# 4) Bir xil branch'ni ikki joyda checkout qilib bo'lmasligi
# ============================================================
$ git worktree add ../repo-main2 main
fatal: 'main' is already used by worktree at '/home/user/repo-hotfix'
# Git buni ATAYLAB taqiqlaydi — bitta branch ikki xil ishchi papkada
# bir vaqtda bo'lsa, index'lar mos kelmay qolishi mumkin edi.

# ============================================================
# 5) Faol worktree'larni ko'rish va tozalash
# ============================================================
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
/home/user/repo-hotfix   a1b2c3d [hotfix/urgent-bug]

$ rm -rf ../repo-hotfix          # qo'lda o'chirib yubordik
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
/home/user/repo-hotfix   a1b2c3d [hotfix/urgent-bug]  (o'chirilgan, lekin hali ro'yxatda)

$ git worktree prune
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
# Endi Git bu haqda bilib, yozuvni tozaladi.

# To'g'ri usul (prune shart emas):
$ git worktree add ../repo-review pr-123-branch
$ git worktree remove ../repo-review

# ============================================================
# 6) Worktree'ni qulflash (tashqi disk uchun)
# ============================================================
$ git worktree add /mnt/external-disk/long-task feature-y
$ git worktree lock /mnt/external-disk/long-task --reason "tashqi disk, uzoq muddat"
$ git worktree list
/home/user/repo               3f2e1d0 [main]
/mnt/external-disk/long-task   a8b7c6d [feature-y] locked

$ git worktree prune   # tashqi disk vaqtincha ulanmagan bo'lsa ham xavfsiz
# Locked worktree HECH QACHON prune tomonidan o'chirilmaydi.

$ git worktree unlock /mnt/external-disk/long-task
$ git worktree remove /mnt/external-disk/long-task

# ============================================================
# 7) --porcelain — skript uchun barqaror format
# ============================================================
$ git worktree list --porcelain
worktree /home/user/repo
HEAD 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
branch refs/heads/main

worktree /home/user/repo-hotfix
HEAD a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9
branch refs/heads/hotfix/urgent-bug

# Har bir worktree haqida uchta qator: worktree (yo'l), HEAD (SHA-1),
# branch (to'liq ref nomi) — bo'sh qator bilan ajratilgan, skript uchun
# qulay, versiyalar orasida barqaror.

# ============================================================
# 8) Worktree'ni boshqa joyga ko'chirish
# ============================================================
$ git worktree move ../repo-hotfix ../renamed-hotfix
$ git worktree list
/home/user/repo             3f2e1d0 [main]
/home/user/renamed-hotfix   a8b7c6d [hotfix/urgent-bug]
# .git/worktrees/ ichidagi ichki yozuvlar ham avtomatik yangilanadi.
""".strip()

L6_CODE_RU = """
# ============================================================
# 1) Видим проблему: без stash ветку не переключить
# ============================================================
$ git status --short
 M app/services/payment_service.py
 M app/api/v1/endpoints/payments.py
# на feature-payment есть незавершённая работа, вдруг нужен hotfix:
$ git switch main
error: Your local changes to the following files would be overwritten by checkout:
	app/services/payment_service.py
Please commit your changes or stash them before you switch branches.

# ============================================================
# 2) Решение через worktree — stash вообще не нужен
# ============================================================
$ git worktree add ../repo-hotfix main
Preparing worktree (checking out 'main')
HEAD is now at 3f2e1d0 fix: предыдущий hotfix

$ ls ..
repo/  repo-hotfix/
$ cd ../repo-hotfix
$ git branch --show-current
main
$ git switch -c hotfix/urgent-bug
$ vim app/services/critical.py
$ git commit -am "hotfix: исправлен критический баг в production"
$ git push origin hotfix/urgent-bug

# В это время в первой папке НИЧЕГО не изменилось:
$ cd ../repo
$ git status --short
 M app/services/payment_service.py
 M app/api/v1/endpoints/payments.py
# Точно так же, нетронуто — stash/pop для hotfix не понадобился.

# ============================================================
# 3) Проверка внутреннего механизма
# ============================================================
$ cat ../repo-hotfix/.git
gitdir: /home/user/repo/.git/worktrees/repo-hotfix
# Это ФАЙЛ, а не папка — просто указывает на основной репозиторий.

$ ls .git/worktrees/
repo-hotfix
$ ls .git/worktrees/repo-hotfix/
HEAD  index  logs/  ORIG_HEAD  commondir  gitdir
$ cat .git/worktrees/repo-hotfix/HEAD
ref: refs/heads/hotfix/urgent-bug
# У каждого worktree свой HEAD, но refs/heads/ ОБЩИЙ:
$ ls .git/refs/heads/
feature-payment  hotfix/  main

# ============================================================
# 4) Нельзя checkout'нуть одну ветку в двух местах
# ============================================================
$ git worktree add ../repo-main2 main
fatal: 'main' is already used by worktree at '/home/user/repo-hotfix'
# Git НАМЕРЕННО это запрещает — если одна ветка будет одновременно в двух
# рабочих папках, их index могли бы разойтись.

# ============================================================
# 5) Просмотр активных worktree и очистка
# ============================================================
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
/home/user/repo-hotfix   a1b2c3d [hotfix/urgent-bug]

$ rm -rf ../repo-hotfix          # удалили вручную
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
/home/user/repo-hotfix   a1b2c3d [hotfix/urgent-bug]  (удалён, но ещё в списке)

$ git worktree prune
$ git worktree list
/home/user/repo          3f2e1d0 [feature-payment]
# Теперь Git узнал об этом и очистил запись.

# Правильный способ (prune не нужен):
$ git worktree add ../repo-review pr-123-branch
$ git worktree remove ../repo-review

# ============================================================
# 6) Блокировка worktree (для внешнего диска)
# ============================================================
$ git worktree add /mnt/external-disk/long-task feature-y
$ git worktree lock /mnt/external-disk/long-task --reason "внешний диск, надолго"
$ git worktree list
/home/user/repo               3f2e1d0 [main]
/mnt/external-disk/long-task   a8b7c6d [feature-y] locked

$ git worktree prune   # безопасно, даже если внешний диск временно не подключён
# Заблокированный worktree НИКОГДА не удаляется через prune.

$ git worktree unlock /mnt/external-disk/long-task
$ git worktree remove /mnt/external-disk/long-task

# ============================================================
# 7) --porcelain — стабильный формат для скриптов
# ============================================================
$ git worktree list --porcelain
worktree /home/user/repo
HEAD 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
branch refs/heads/main

worktree /home/user/repo-hotfix
HEAD a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9
branch refs/heads/hotfix/urgent-bug

# Три строки для каждого worktree: worktree (путь), HEAD (SHA-1),
# branch (полное имя ref) — разделены пустой строкой, удобно для
# скриптов, стабильно между версиями.

# ============================================================
# 8) Перемещение worktree в другое место
# ============================================================
$ git worktree move ../repo-hotfix ../renamed-hotfix
$ git worktree list
/home/user/repo             3f2e1d0 [main]
/home/user/renamed-hotfix   a8b7c6d [hotfix/urgent-bug]
# Внутренние записи в .git/worktrees/ тоже обновляются автоматически.
""".strip()

L6_TASK = {
    "task_title": "Stash'siz shoshilinch hotfix: worktree amaliyoti",
    "task_title_ru": "Срочный hotfix без stash: практика с worktree",
    "task_description": (
        "Repo yarating, `feature-x` branch'ida FAYLNI TAHRIRLAB, hali "
        "commit qilmasdan qoldiring (tugallanmagan ish holatini "
        "simulyatsiya qiling). `git worktree add` yordamida alohida "
        "papkada `main`dan `hotfix/urgent` branch'ini oching, u yerda "
        "tuzatish qilib commit qiling. So'ngra asosiy papkaga qaytib, "
        "`feature-x`dagi tugallanmagan o'zgarishlar TEGILMAGAN "
        "qolganini isbotlang."
    ),
    "task_description_ru": (
        "Создайте репозиторий, на ветке `feature-x` ОТРЕДАКТИРУЙТЕ файл, "
        "не коммитя (симулируйте незавершённую работу). Через `git "
        "worktree add` откройте в отдельной папке ветку `hotfix/urgent` "
        "от `main`, там сделайте исправление и коммит. Затем вернитесь в "
        "основную папку и докажите, что незавершённые изменения в "
        "`feature-x` остались НЕТРОНУТЫМИ."
    ),
    "task_requirements": (
        "1) `git worktree list` ikkala worktree'ni ko'rsatishi kerak. "
        "2) Asosiy papkada `git status --short` hotfix'dan OLDIN va "
        "KEYIN bir xil ekanini ko'rsating. 3) `.git/worktrees/` ichidagi "
        "tuzilishni (`cat .git/worktrees/<nom>/HEAD`) hisobotga "
        "kiriting. 4) Oxirida `git worktree remove` bilan tozalang."
    ),
    "task_requirements_ru": (
        "1) `git worktree list` должен показывать оба worktree. 2) "
        "Покажите, что `git status --short` в основной папке одинаков "
        "ДО и ПОСЛЕ hotfix. 3) Включите в отчёт структуру внутри "
        "`.git/worktrees/` (`cat .git/worktrees/<имя>/HEAD`). 4) В конце "
        "очистите через `git worktree remove`."
    ),
    "task_technologies": "Git (worktree add/list/remove/prune)",
    "task_deadline_days": 3,
}

L6_SAMPLE = {
    "title": "Namuna: worktree hotfix skripti",
    "description": (
        "Bash skripti tugallanmagan o'zgarishni simulyatsiya qiladi, "
        "keyin git worktree orqali stash ishlatmasdan alohida hotfix "
        "branch ochib, tuzatish qiladi va asosiy papka tegilmaganini "
        "tekshiradi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "worktree_hotfix.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf wtdemo wtdemo-hotfix && mkdir wtdemo && cd wtdemo && git init -q\n"
                "echo 'v1' > app.py && git add . && git commit -q -m \"c0\"\n"
                "git switch -q -c feature-x\n"
                "echo 'tugallanmagan feature kodi' >> app.py   # commit QILINMAYDI\n\n"
                "echo \"=== hotfix'dan OLDIN status ===\"\n"
                "git status --short\n\n"
                "git worktree add -q ../wtdemo-hotfix main\n"
                "( cd ../wtdemo-hotfix\n"
                "  git switch -q -c hotfix/urgent\n"
                "  echo 'hotfix tuzatildi' > hotfix.txt\n"
                "  git add . && git commit -q -m \"hotfix: shoshilinch tuzatish\" )\n\n"
                "echo \"=== hotfix'dan KEYIN status (o'zgarmagan bo'lishi kerak) ===\"\n"
                "git status --short\n\n"
                "echo \"=== worktree ro'yxati ===\"\n"
                "git worktree list\n\n"
                "cat ../wtdemo-hotfix/.git\n"
                "git worktree remove ../wtdemo-hotfix\n"
            ),
        },
    ],
}

L6_EXERCISES = [
    {
        "title": "worktree vs stash",
        "title_ru": "worktree против stash",
        "description": "git worktree'ning stash'dan asosiy afzalligi nima?",
        "description_ru": "В чём главное преимущество git worktree перед stash?",
        "exercise_type": "multiple_choice",
        "options": [
            "Tugallanmagan ishga tegmasdan, alohida papkada boshqa branch'ni ochish mumkin",
            "worktree o'zgarishlarni avtomatik commit qiladi",
            "worktree obyektlar bazasining alohida nusxasini yaratadi",
            "worktree faqat remote repo'lar bilan ishlaydi",
        ],
        "options_ru": [
            "Можно открыть другую ветку в отдельной папке, не трогая незавершённую работу",
            "worktree автоматически коммитит изменения",
            "worktree создаёт отдельную копию базы объектов",
            "worktree работает только с удалёнными репозиториями",
        ],
        "correct_answers": "A",
        "hint": "Stash ishni yashiradi, worktree esa umuman unga tegmaydi.",
        "hint_ru": "Stash прячет работу, а worktree вообще её не трогает.",
        "explanation": "Har bir worktree o'z ishchi fayllari va index'iga ega, shuning uchun stash shart emas.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Worktree qo'shish ish oqimi",
        "title_ru": "Рабочий процесс добавления worktree",
        "description": "Shoshilinch hotfix uchun worktree ishlatishning to'g'ri tartibini joylashtiring.",
        "description_ru": "Расположите правильный порядок использования worktree для срочного hotfix.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git worktree add ../hotfix main",
            "Yangi papkaga o'tib, hotfix branch ochish",
            "Tuzatish qilib commit va push qilish",
            "git worktree remove ../hotfix",
        ],
        "drag_items_ru": [
            "git worktree add ../hotfix main",
            "Перейти в новую папку и открыть ветку hotfix",
            "Сделать исправление, commit и push",
            "git worktree remove ../hotfix",
        ],
        "correct_order": [
            "git worktree add ../hotfix main",
            "Yangi papkaga o'tib, hotfix branch ochish",
            "Tuzatish qilib commit va push qilish",
            "git worktree remove ../hotfix",
        ],
        "hint": "Avval papka yaratiladi, keyin ishlanadi, oxirida tozalanadi.",
        "hint_ru": "Сначала создаётся папка, потом работа, в конце очистка.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Bir branch, ikki worktree",
        "title_ru": "Одна ветка, два worktree",
        "description": "Git bitta branch'ni ikkita worktree'da bir vaqtda checkout qilishga ___ (ruxsat beradi / ruxsat bermaydi).",
        "description_ru": "Git ___ (разрешает / не разрешает) checkout одной ветки одновременно в двух worktree.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "ruxsat bermaydi",
        "correct_answers_ru": "не разрешает",
        "hint": "'already used by worktree' xato xabarini eslang.",
        "hint_ru": "Вспомните сообщение об ошибке 'already used by worktree'.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 7 — Submodule vs Subtree: tashqi repo'larni boshqarish
# ---------------------------------------------------------------------------

L7_TEXT = """
<h3>Muammo: bitta repo boshqa repo'ga muhtoj bo'lsa</h3>
<p>Ba'zan loyihangiz boshqa Git repo'sini o'z ichiga olishi kerak —
masalan umumiy UI komponent kutubxonasi, yoki uchinchi tomon SDK'si,
alohida repo sifatida saqlanadi, lekin sizning asosiy loyihangiz ichida
kerak. Buning uchun ikkita asosiy yechim bor: <strong>submodule</strong>
va <strong>subtree</strong>. Ikkalasi ham muammoni yechadi, lekin
butunlay boshqacha mexanizm bilan — va noto'g'ri tanlov jamoada
chalkashlikka olib kelishi mumkin.</p>

<h3>Submodule: "ishorat" saqlash usuli</h3>
<p><code>git submodule add &lt;url&gt; path/</code> asosiy repo'da
<code>.gitmodules</code> faylini yaratadi (URL va yo'lni saqlaydi) va
<code>path/</code> ostida maxsus "gitlink" yozuvi qo'shadi — bu ODDIY
papka EMAS, balki "boshqa repo'ning ANIQ commit SHA-1'iga ishora"
yozuvi. Asosiy repo submodule'ning FAYLLARINI saqlamaydi, faqat "qaysi
commit'da bo'lishi kerak"ligini saqlaydi. Klonlashda
<code>git clone --recurse-submodules</code> yoki keyinroq <code>git
submodule update --init</code> kerak — aks holda submodule papkasi BO'SH
qoladi.</p>

<h3>Subtree: "haqiqiy nusxalash" usuli</h3>
<p><code>git subtree add --prefix=path/ &lt;url&gt; &lt;branch&gt;</code>
esa boshqa repo'ning BARCHA fayllarini asosiy repo'ning O'Z tarixiga
MERGE qiladi — natijada tashqi kod xuddi har doim shu yerda yozilgandek
ko'rinadi. Alohida <code>.gitmodules</code> yo'q, alohida "init" qadami
kerak emas — <code>git clone</code> qilgan HAR KIM darhol to'liq kodni
oladi, chunki u sizning repo'ingizning oddiy tarixiy qismi.</p>

<h3>Ikkalasining tub farqi — vizual</h3>
<pre class="mermaid">
flowchart LR
  subgraph sub ["SUBMODULE"]
    A1["asosiy repo"] -->|".gitmodules + gitlink"| A2["ISHORAT: commit abc123
(fayllar YO'Q, faqat SHA-1)"]
    A2 -.->|"alohida clone/update kerak"| A3["tashqi repo (alohida .git)"]
  end
  subgraph sub2 ["SUBTREE"]
    B1["asosiy repo"] -->|"merge --squash"| B2["HAQIQIY fayllar
(asosiy tarixning qismi)"]
  end
  style A2 fill:#ffe9b3,stroke:#d09000
  style B2 fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Diagramma asosiy farqni ko'rsatadi: submodule — ISHORAT (tashqi
repo'ga ko'rsatkich, fayllarsiz), subtree — HAQIQIY NUSXA (fayllar
to'liq asosiy tarixga birlashtirilgan).</p>

<h3>Qachon qaysi birini tanlash</h3>
<table>
<tr><th>Mezon</th><th>Submodule</th><th>Subtree</th></tr>
<tr><td>Tashqi repo'ga o'zgarish qaytarish</td><td>Oson (o'z repo'sida)</td><td>Qiyinroq (subtree push)</td></tr>
<tr><td>Klonlash sodda-ligi</td><td>Qo'shimcha qadam kerak</td><td>Oddiy git clone yetarli</td></tr>
<tr><td>Repo hajmi</td><td>Kichik (faqat ishorat)</td><td>Katta (fayllar nusxasi)</td></tr>
<tr><td>Tarixni ko'rish</td><td>Alohida (tashqi repo'da)</td><td>Aralashgan (bitta log'da)</td></tr>
</table>
<p>Umumiy qoida: agar tashqi kodni FAOL ravishda o'zgartirib, orqaga
qaytarib turishingiz kerak bo'lsa — submodule. Agar tashqi kod
"o'rnatib-unutiladigan" bo'lsa va yangi jamoa a'zosi qo'shimcha
qadamlarsiz darhol to'liq kod olishi kerak bo'lsa — subtree.</p>

<h3>Eng ko'p uchraydigan submodule xatosi</h3>
<p><code>git clone</code> (oddiy, <code>--recurse-submodules</code>siz)
qilingandan so'ng submodule papkalari BO'SH bo'ladi — bu yangi
dasturchilar orasida eng ko'p uchraydigan chalkashlik. Yechim:
<code>git submodule update --init --recursive</code> yoki
<code>git config --global submodule.recurseCheckout true</code> kabi
global sozlash.</p>

<h3>submodule foreach — bir nechta submodule bilan bir vaqtda ishlash</h3>
<p>Katta loyihada o'nlab submodule bo'lishi mumkin. <code>git submodule
foreach '&lt;buyruq&gt;'</code> BARCHA submodule'lar ichida ketma-ket
bitta buyruqni ishga tushiradi — masalan, <code>git submodule foreach
'git checkout main && git pull'</code> orqali barcha submodule'larni bir
zumda yangilash mumkin, har birini qo'lda kirib chiqmasdan.</p>

<h3>Submodule'ni butunlay olib tashlash — deinit</h3>
<p>Submodule'ni oddiy <code>rm -rf path/</code> bilan o'chirish YETARLI
EMAS — <code>.gitmodules</code>, <code>.git/config</code> va
<code>.git/modules/</code> ichida hali ham yozuvlar qoladi. To'g'ri
yo'l: <code>git submodule deinit path/</code> (ishchi papkani tozalaydi,
lekin ro'yxatdan chiqarmaydi), so'ng <code>git rm path/</code> (butunlay
ro'yxatdan chiqaradi va <code>.gitmodules</code>ni yangilaydi).</p>
""".strip()

L7_TEXT_RU = """
<h3>Проблема: когда один репозиторий нуждается в другом</h3>
<p>Иногда ваш проект должен включать другой Git-репозиторий — например,
общую библиотеку UI-компонентов или SDK третьей стороны, который
хранится как отдельный репозиторий, но нужен внутри вашего основного
проекта. Для этого есть два основных решения: <strong>submodule</strong>
и <strong>subtree</strong>. Оба решают проблему, но совершенно разным
механизмом — и неверный выбор может привести к путанице в команде.</p>

<h3>Submodule: способ хранения "указателя"</h3>
<p><code>git submodule add &lt;url&gt; path/</code> создаёт в основном
репозитории файл <code>.gitmodules</code> (хранит URL и путь) и
добавляет под <code>path/</code> специальную запись "gitlink" — это НЕ
обычная папка, а запись "указатель на ТОЧНЫЙ SHA-1 коммита другого
репозитория". Основной репозиторий не хранит ФАЙЛЫ submodule, только то,
"на каком коммите он должен быть". При клонировании нужен <code>git
clone --recurse-submodules</code> или позже <code>git submodule update
--init</code> — иначе папка submodule останется ПУСТОЙ.</p>

<h3>Subtree: способ "настоящего копирования"</h3>
<p><code>git subtree add --prefix=path/ &lt;url&gt; &lt;branch&gt;</code>
же ОБЪЕДИНЯЕТ ВСЕ файлы другого репозитория в СОБСТВЕННУЮ историю
основного репозитория — в результате внешний код выглядит так, будто
всегда писался здесь. Отдельного <code>.gitmodules</code> нет, отдельный
шаг "init" не нужен — ЛЮБОЙ, кто сделает <code>git clone</code>, сразу
получит полный код, потому что он просто обычная историческая часть
вашего репозитория.</p>

<h3>Принципиальная разница — визуально</h3>
<pre class="mermaid">
flowchart LR
  subgraph sub ["SUBMODULE"]
    A1["основной репозиторий"] -->|".gitmodules + gitlink"| A2["УКАЗАТЕЛЬ: commit abc123
(файлов НЕТ, только SHA-1)"]
    A2 -.->|"нужен отдельный clone/update"| A3["внешний репозиторий (свой .git)"]
  end
  subgraph sub2 ["SUBTREE"]
    B1["основной репозиторий"] -->|"merge --squash"| B2["НАСТОЯЩИЕ файлы
(часть основной истории)"]
  end
  style A2 fill:#ffe9b3,stroke:#d09000
  style B2 fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Диаграмма показывает принципиальную разницу: submodule — УКАЗАТЕЛЬ
(ссылка на внешний репозиторий, без файлов), subtree — НАСТОЯЩАЯ КОПИЯ
(файлы полностью объединены в основную историю).</p>

<h3>Когда что выбирать</h3>
<table>
<tr><th>Критерий</th><th>Submodule</th><th>Subtree</th></tr>
<tr><td>Возврат изменений во внешний репозиторий</td><td>Легко (в своём репозитории)</td><td>Сложнее (subtree push)</td></tr>
<tr><td>Простота клонирования</td><td>Нужен доп. шаг</td><td>Достаточно обычного git clone</td></tr>
<tr><td>Размер репозитория</td><td>Маленький (только указатель)</td><td>Большой (копия файлов)</td></tr>
<tr><td>Просмотр истории</td><td>Отдельно (во внешнем репозитории)</td><td>Смешано (в одном log)</td></tr>
</table>
<p>Общее правило: если внешний код нужно АКТИВНО изменять и возвращать
обратно — submodule. Если внешний код "установил и забыл", а новый член
команды должен сразу получить полный код без дополнительных шагов —
subtree.</p>

<h3>Самая частая ошибка с submodule</h3>
<p>После обычного <code>git clone</code> (без
<code>--recurse-submodules</code>) папки submodule будут ПУСТЫМИ — это
самая частая путаница среди новых разработчиков. Решение: <code>git
submodule update --init --recursive</code> или глобальная настройка
вроде <code>git config --global submodule.recurseCheckout true</code>.</p>

<h3>submodule foreach — работа с несколькими submodule одновременно</h3>
<p>В крупном проекте может быть десятки submodule. <code>git submodule
foreach '&lt;команда&gt;'</code> запускает одну команду последовательно
внутри ВСЕХ submodule — например, через <code>git submodule foreach
'git checkout main && git pull'</code> можно мгновенно обновить все
submodule, не заходя в каждый вручную.</p>

<h3>Полное удаление submodule — deinit</h3>
<p>Удалить submodule обычным <code>rm -rf path/</code> НЕДОСТАТОЧНО —
записи всё ещё остаются в <code>.gitmodules</code>, <code>.git/
config</code> и <code>.git/modules/</code>. Правильный путь: <code>git
submodule deinit path/</code> (очищает рабочую папку, но не убирает из
реестра), затем <code>git rm path/</code> (полностью убирает из
реестра и обновляет <code>.gitmodules</code>).</p>
""".strip()

L7_CODE = """
# ============================================================
# 1) Submodule qo'shish
# ============================================================
$ git submodule add https://github.com/example/ui-kit.git vendor/ui-kit
Cloning into '/home/user/repo/vendor/ui-kit'...
$ cat .gitmodules
[submodule "vendor/ui-kit"]
	path = vendor/ui-kit
	url = https://github.com/example/ui-kit.git

$ git status --short
A  .gitmodules
A  vendor/ui-kit          # <- 160000 mode, gitlink, oddiy papka EMAS
$ git ls-tree HEAD vendor/
160000 commit 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e	vendor/ui-kit
# "160000" — bu maxsus mode, submodule ekanini bildiradi.

$ git commit -am "vendor/ui-kit submodule qo'shildi"

# ============================================================
# 2) Klonlashda submodule'ni unutish xatosi
# ============================================================
$ git clone https://github.com/team/repo.git fresh-clone
$ ls fresh-clone/vendor/ui-kit
# (BO'SH papka!)

$ cd fresh-clone
$ git submodule update --init --recursive
Submodule 'vendor/ui-kit' registered for path 'vendor/ui-kit'
Cloning into 'vendor/ui-kit'...
$ ls vendor/ui-kit
README.md  src/  package.json    # endi to'liq

# Yaxshiroq usul — bir qadamda:
$ git clone --recurse-submodules https://github.com/team/repo.git

# ============================================================
# 3) Submodule'ni yangi commit'ga ko'chirish
# ============================================================
$ cd vendor/ui-kit
$ git log --oneline -1
3f2e1d0 v2.1.0 relizi
$ git pull origin main
$ git log --oneline -1
9a8b7c1 v2.2.0 relizi
$ cd ../..
$ git status --short
 M vendor/ui-kit           # ishorat commit o'zgardi
$ git add vendor/ui-kit
$ git commit -m "vendor/ui-kit ni v2.2.0 ga yangilash"
# Asosiy repo faqat "endi 9a8b7c1'ga ishora qil" deb saqlaydi.

# ============================================================
# 4) Subtree qo'shish — HAQIQIY nusxa
# ============================================================
$ git subtree add --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git main --squash
Squash commit -- not updating HEAD
Merge commit -- not updating HEAD

$ git log --oneline -1
a1b2c3d Merge commit 'xxxx' as 'vendor/ui-kit-subtree'
$ ls vendor/ui-kit-subtree/
README.md  src/  package.json    # DARHOL to'liq — clone/init shart emas

$ git clone https://github.com/team/repo.git fresh2
$ ls fresh2/vendor/ui-kit-subtree/
README.md  src/  package.json    # darhol to'liq, hech qanday qo'shimcha buyruqsiz!

# ============================================================
# 5) Subtree'ni yangilash va o'zgarishni qaytarish
# ============================================================
$ git subtree pull --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git main --squash

$ vim vendor/ui-kit-subtree/src/button.js   # mahalliy tuzatish
$ git commit -am "ui-kit tugmasini tuzatish"
$ git subtree push --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git my-fix-branch
# Endi my-fix-branch orqali original repo'ga PR ochish mumkin.

# ============================================================
# 6) Qaysi mode ekanini tekshirish (submodule vs oddiy papka)
# ============================================================
$ git ls-tree HEAD vendor/
160000 commit 9a8b7c1...  vendor/ui-kit           # <- submodule (gitlink)
040000 tree   b2c3d4e...  vendor/ui-kit-subtree   # <- subtree (oddiy tree)

# ============================================================
# 7) submodule foreach — bir nechta submodule'ni bir vaqtda yangilash
# ============================================================
$ cat .gitmodules
[submodule "vendor/ui-kit"]
	path = vendor/ui-kit
	url = https://github.com/example/ui-kit.git
[submodule "vendor/charts"]
	path = vendor/charts
	url = https://github.com/example/charts.git

$ git submodule foreach 'git checkout main && git pull origin main'
Entering 'vendor/charts'
Already on 'main'
Entering 'vendor/ui-kit'
Already on 'main'
# Ikkala submodule ham BITTA buyruq bilan yangilandi.

$ git submodule foreach 'echo "$name da $(git rev-parse --short HEAD)"'
Entering 'vendor/charts'
vendor/charts da 7c3a1e9
Entering 'vendor/ui-kit'
vendor/ui-kit da 9a8b7c1

# ============================================================
# 8) Submodule'ni to'g'ri olib tashlash
# ============================================================
$ git submodule deinit vendor/ui-kit
Cleared directory 'vendor/ui-kit'
$ ls vendor/ui-kit
# (bo'sh — fayllar o'chirildi, lekin .gitmodules'da yozuv qoladi)

$ git rm vendor/ui-kit
rm 'vendor/ui-kit'
$ git status --short
D  .gitmodules
D  vendor/ui-kit
$ git commit -m "vendor/ui-kit submodule butunlay olib tashlandi"
# Endi .gitmodules, .git/config va .git/modules/ ichidagi barcha
# izlar tozalandi — oddiy rm -rf bilan bu HECH QACHON to'liq bo'lmasdi.
""".strip()

L7_CODE_RU = """
# ============================================================
# 1) Добавление submodule
# ============================================================
$ git submodule add https://github.com/example/ui-kit.git vendor/ui-kit
Cloning into '/home/user/repo/vendor/ui-kit'...
$ cat .gitmodules
[submodule "vendor/ui-kit"]
	path = vendor/ui-kit
	url = https://github.com/example/ui-kit.git

$ git status --short
A  .gitmodules
A  vendor/ui-kit          # <- режим 160000, gitlink, НЕ обычная папка
$ git ls-tree HEAD vendor/
160000 commit 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e	vendor/ui-kit
# "160000" — специальный режим, означающий submodule.

$ git commit -am "добавлен submodule vendor/ui-kit"

# ============================================================
# 2) Ошибка забытого submodule при клонировании
# ============================================================
$ git clone https://github.com/team/repo.git fresh-clone
$ ls fresh-clone/vendor/ui-kit
# (ПУСТАЯ папка!)

$ cd fresh-clone
$ git submodule update --init --recursive
Submodule 'vendor/ui-kit' registered for path 'vendor/ui-kit'
Cloning into 'vendor/ui-kit'...
$ ls vendor/ui-kit
README.md  src/  package.json    # теперь полностью

# Лучший способ — одним шагом:
$ git clone --recurse-submodules https://github.com/team/repo.git

# ============================================================
# 3) Перемещение submodule на новый коммит
# ============================================================
$ cd vendor/ui-kit
$ git log --oneline -1
3f2e1d0 релиз v2.1.0
$ git pull origin main
$ git log --oneline -1
9a8b7c1 релиз v2.2.0
$ cd ../..
$ git status --short
 M vendor/ui-kit           # указатель-коммит изменился
$ git add vendor/ui-kit
$ git commit -m "обновление vendor/ui-kit до v2.2.0"
# Основной репозиторий хранит только "теперь указывай на 9a8b7c1".

# ============================================================
# 4) Добавление subtree — НАСТОЯЩАЯ копия
# ============================================================
$ git subtree add --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git main --squash
Squash commit -- not updating HEAD
Merge commit -- not updating HEAD

$ git log --oneline -1
a1b2c3d Merge commit 'xxxx' as 'vendor/ui-kit-subtree'
$ ls vendor/ui-kit-subtree/
README.md  src/  package.json    # СРАЗУ полностью — clone/init не нужен

$ git clone https://github.com/team/repo.git fresh2
$ ls fresh2/vendor/ui-kit-subtree/
README.md  src/  package.json    # сразу полностью, без дополнительных команд!

# ============================================================
# 5) Обновление subtree и возврат изменений
# ============================================================
$ git subtree pull --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git main --squash

$ vim vendor/ui-kit-subtree/src/button.js   # локальное исправление
$ git commit -am "исправление кнопки в ui-kit"
$ git subtree push --prefix=vendor/ui-kit-subtree \\
    https://github.com/example/ui-kit.git my-fix-branch
# Теперь через my-fix-branch можно открыть PR в оригинальный репозиторий.

# ============================================================
# 6) Проверка режима (submodule против обычной папки)
# ============================================================
$ git ls-tree HEAD vendor/
160000 commit 9a8b7c1...  vendor/ui-kit           # <- submodule (gitlink)
040000 tree   b2c3d4e...  vendor/ui-kit-subtree   # <- subtree (обычный tree)

# ============================================================
# 7) submodule foreach — одновременное обновление нескольких submodule
# ============================================================
$ cat .gitmodules
[submodule "vendor/ui-kit"]
	path = vendor/ui-kit
	url = https://github.com/example/ui-kit.git
[submodule "vendor/charts"]
	path = vendor/charts
	url = https://github.com/example/charts.git

$ git submodule foreach 'git checkout main && git pull origin main'
Entering 'vendor/charts'
Already on 'main'
Entering 'vendor/ui-kit'
Already on 'main'
# Оба submodule обновлены ОДНОЙ командой.

$ git submodule foreach 'echo "$name: $(git rev-parse --short HEAD)"'
Entering 'vendor/charts'
vendor/charts: 7c3a1e9
Entering 'vendor/ui-kit'
vendor/ui-kit: 9a8b7c1

# ============================================================
# 8) Правильное удаление submodule
# ============================================================
$ git submodule deinit vendor/ui-kit
Cleared directory 'vendor/ui-kit'
$ ls vendor/ui-kit
# (пусто — файлы удалены, но запись в .gitmodules остаётся)

$ git rm vendor/ui-kit
rm 'vendor/ui-kit'
$ git status --short
D  .gitmodules
D  vendor/ui-kit
$ git commit -m "submodule vendor/ui-kit полностью удалён"
# Теперь все следы в .gitmodules, .git/config и .git/modules/ очищены —
# обычным rm -rf это НИКОГДА не было бы полным.
""".strip()

L7_TASK = {
    "task_title": "Bitta tashqi kutubxonani ikkala usulda ham qo'shing",
    "task_title_ru": "Добавьте одну внешнюю библиотеку двумя способами",
    "task_description": (
        "Kichik GitHub repo (yoki mahalliy 'tashqi' repo) tanlang. Uni "
        "asosiy loyihangizga (1) `git submodule add` orqali "
        "`vendor/lib-sub` yo'liga, (2) `git subtree add --squash` orqali "
        "`vendor/lib-subtree` yo'liga qo'shing. Ikkalasini ham fresh "
        "`git clone` bilan qayta klonlab, qaysi biri darhol to'liq "
        "fayllarga ega, qaysi biri qo'shimcha qadam talab qilishini "
        "ko'rsating."
    ),
    "task_description_ru": (
        "Выберите небольшой GitHub-репозиторий (или локальный 'внешний' "
        "репозиторий). Добавьте его в основной проект (1) через `git "
        "submodule add` в путь `vendor/lib-sub`, (2) через `git subtree "
        "add --squash` в путь `vendor/lib-subtree`. Клонируйте оба "
        "заново через свежий `git clone` и покажите, какой сразу "
        "содержит полные файлы, а какой требует дополнительного шага."
    ),
    "task_requirements": (
        "1) `.gitmodules` faylining mazmunini keltiring. 2) `git ls-tree "
        "HEAD vendor/` chiqishida ikkala yo'lning mode'i (160000 vs "
        "040000) farqlanishini ko'rsating. 3) Fresh clone'dan keyin "
        "submodule papkasi bo'sh, subtree papkasi to'liq ekanini "
        "isbotlang."
    ),
    "task_requirements_ru": (
        "1) Приведите содержимое файла `.gitmodules`. 2) Покажите "
        "разницу режимов (160000 против 040000) для обоих путей в "
        "выводе `git ls-tree HEAD vendor/`. 3) Докажите, что после "
        "свежего клонирования папка submodule пуста, а subtree "
        "полная."
    ),
    "task_technologies": "Git (submodule, subtree)",
    "task_deadline_days": 4,
}

L7_SAMPLE = {
    "title": "Namuna: submodule va subtree taqqoslash skripti",
    "description": (
        "Bash skripti sun'iy 'tashqi' repo yaratadi, uni submodule va "
        "subtree sifatida ikkita alohida yo'lga qo'shadi, so'ngra fresh "
        "clone qilib farqni ko'rsatadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "compare_submodule_subtree.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf extlib main-repo fresh-check\n"
                "mkdir extlib && cd extlib && git init -q\n"
                "echo 'tashqi kutubxona kodi' > lib.py\n"
                "git add . && git commit -q -m \"v1.0\"\n"
                "EXTLIB=$(pwd)\n"
                "cd ..\n\n"
                "mkdir main-repo && cd main-repo && git init -q\n"
                "echo 'asosiy loyiha' > app.py && git add . && git commit -q -m \"c0\"\n\n"
                "git submodule add -q \"$EXTLIB\" vendor/lib-sub\n"
                "git commit -q -m \"submodule qo'shildi\"\n\n"
                "git subtree add --prefix=vendor/lib-subtree \"$EXTLIB\" master --squash -q\n\n"
                "echo \"=== mode farqi ===\"\n"
                "git ls-tree HEAD vendor/\n\n"
                "cd ..\n"
                "git clone -q main-repo fresh-check\n\n"
                "echo \"=== fresh clone'da submodule (bo'sh bo'lishi kerak) ===\"\n"
                "ls fresh-check/vendor/lib-sub/ 2>/dev/null || echo \"(bo'sh)\"\n\n"
                "echo \"=== fresh clone'da subtree (to'liq bo'lishi kerak) ===\"\n"
                "ls fresh-check/vendor/lib-subtree/\n"
            ),
        },
    ],
}

L7_EXERCISES = [
    {
        "title": "Submodule nima saqlaydi",
        "title_ru": "Что хранит submodule",
        "description": "Asosiy repo submodule uchun texnik jihatdan nimani saqlaydi?",
        "description_ru": "Что технически хранит основной репозиторий для submodule?",
        "exercise_type": "multiple_choice",
        "options": [
            "Faqat tashqi repo'ning ANIQ commit SHA-1'iga ishorani",
            "Tashqi repo'ning barcha fayllarining to'liq nusxasini",
            "Tashqi repo'ning faqat oxirgi versiyasi haqida metama'lumot",
            "Hech narsani, faqat URL'ni ko'rsatadi",
        ],
        "options_ru": [
            "Только указатель на ТОЧНЫЙ SHA-1 коммита внешнего репозитория",
            "Полную копию всех файлов внешнего репозитория",
            "Только метаданные о последней версии внешнего репозитория",
            "Ничего, только показывает URL",
        ],
        "correct_answers": "A",
        "hint": "git ls-tree'dagi 160000 mode'ni eslang — bu gitlink.",
        "hint_ru": "Вспомните режим 160000 в git ls-tree — это gitlink.",
        "explanation": "Submodule — bu ishorat (gitlink), fayllar tashqi repo'ning o'zida saqlanadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Qaysi holatda subtree yaxshiroq",
        "title_ru": "Когда subtree предпочтительнее",
        "description": "Yangi jamoa a'zosi hech qanday qo'shimcha buyruqsiz DARHOL to'liq tashqi kodni olishi kerak bo'lsa, submodule va subtree'dan qaysi biri ma'qulroq: ___",
        "description_ru": "Если новый член команды должен СРАЗУ получить полный внешний код без дополнительных команд, что предпочтительнее — submodule или subtree: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "subtree",
        "correct_answers_ru": "subtree",
        "hint": "Qaysi biri git clone'dan keyin darhol to'liq fayllarga ega bo'ladi?",
        "hint_ru": "Какой из них сразу после git clone имеет полные файлы?",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 8 — Git hooks: mahalliy pre-commit/commit-msg/pre-push avtomatlashtirish
# ---------------------------------------------------------------------------

L8_TEXT = """
<h3>Hook nima: Git o'zi ishga tushiradigan skriptlar</h3>
<p>Har bir Git repo'sida <code>.git/hooks/</code> papkasi bor — u yerda
Git MA'LUM voqealar (commit qilishdan oldin, commit xabari yozilganda,
push qilishdan oldin va h.k.) sodir bo'lganda AVTOMATIK ishga tushiradigan
skriptlar joylashadi. Yangi repo'da bu papka faqat <code>.sample</code>
kengaytmali NAMUNA fayllarni o'z ichiga oladi (masalan
<code>pre-commit.sample</code>) — ular ISHLAMAYDI, chunki Git faqat
kengaytmasiz, ishga tushirish huquqiga ega (<code>chmod +x</code>) faylni
qidiradi.</p>

<h3>Eng muhim mahalliy hook'lar</h3>
<ul>
<li><strong>pre-commit</strong> — <code>git commit</code> BOSHLANISHIDAN
oldin, hatto commit xabari so'ralishidan ham oldin ishga tushadi.
Chiqish kodi 0 bo'lmasa, commit BUTUNLAY to'xtaydi. Odatda: linter, kod
formatlash tekshiruvi, maxfiy kalitlarni tekshirish.</li>
<li><strong>commit-msg</strong> — commit xabari YOZILGANDAN keyin, lekin
commit YAKUNLANISHIDAN oldin ishga tushadi; xabar matni argument sifatida
uzatiladi. Odatda: Conventional Commits formatini (<code>feat:</code>,
<code>fix:</code>) tekshirish.</li>
<li><strong>pre-push</strong> — <code>git push</code> serverga
ULANISHDAN oldin ishga tushadi. Chiqish kodi 0 bo'lmasa, push BUTUNLAY
bekor qilinadi. Odatda: testlarni ishga tushirish, `master`ga to'g'ridan-
to'g'ri push'ni taqiqlash.</li>
</ul>

<h3>Muhim cheklov: hook'lar VERSIYALANMAYDI</h3>
<p><code>.git/hooks/</code> — <code>.git/</code> ICHIDA, demak
<strong>u repo'ning commit tarixining qismi emas</strong>. Siz
<code>pre-commit</code> skriptini yozib, uni jamoangizga "push" qila
olmaysiz — chunki <code>.git/</code> hech qachon push/pull qilinmaydi!
Har bir dasturchi o'zining mahalliy nusxasida hook'ni qo'lda o'rnatishi
kerak, yoki <code>husky</code>/<code>pre-commit</code> (Python) kabi
vositalar orqali <code>package.json</code>/<code>.pre-commit-config.yaml</code>
fayli (bular repo'da versiyalanadi) orqali avtomatik o'rnatiladi.</p>

<h3>Mahalliy hook vs CI: bir xil tekshiruv, ikki xil kafolat</h3>
<p>Bu farq amaliyotda juda muhim. Ushbu platformaning o'zida
<code>.github/workflows/test.yml</code> fayli bor — u HAR BIR push'da
(<code>branches: ["**"]</code>) GitHub serverida pytest va Jest testlarini
ishga tushiradi. Bu — <strong>CI hook</strong>: serverda ishlaydi, HECH
KIM uni chetlab o'ta olmaydi (hatto <code>--no-verify</code> bilan ham).
Mahalliy <code>pre-push</code> hook esa xuddi shu testni push'dan OLDIN,
dasturchining KOMPYUTERIDA ishga tushiradi — tezroq fikr-mulohaza beradi,
lekin <code>git push --no-verify</code> bilan OSON chetlab o'tiladi.
Shuning uchun ikkalasi ham kerak: mahalliy hook — tezkor, ixtiyoriy
signal; CI — sekinroq, lekin MAJBURIY darvoza.</p>

<h3>Hook turlari va ularning kafolat darajasi</h3>
<pre class="mermaid">
flowchart LR
  A["Dasturchi kod yozadi"] --> B["pre-commit
(mahalliy, --no-verify bilan o'tkazib yuborsa bo'ladi)"]
  B --> C["commit-msg
(mahalliy, ixtiyoriy)"]
  C --> D["git push"]
  D --> E["pre-push
(mahalliy, --no-verify bilan o'tkazib yuborsa bo'ladi)"]
  E --> F["GitHub serveri:
.github/workflows/test.yml
(CI, HECH QANDAY --no-verify yordam bermaydi)"]
  style F fill:#ffd6d6,stroke:#c00000
  style B fill:#ffe9b3,stroke:#d09000
  style E fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma ushbu platformaning haqiqiy oqimini ko'rsatadi: mahalliy
hook'lar (sariq) tezkor, lekin chetlab o'tish mumkin bo'lgan tekshiruvlar;
GitHub Actions CI (qizil) esa serverda ishlaydi va uni hech kim chetlab
o'ta olmaydi — shuning uchun "haqiqiy" sifat darvozasi hamisha CI'da
bo'lishi kerak, mahalliy hook faqat qo'shimcha qulaylik.</p>

<h3>Amaliy misol: real workflow'ga mos pre-push</h3>
<p>Ushbu platformaning <code>test.yml</code>'i backend uchun
<code>python -m pytest tests/ -v --tb=short</code> ishga tushiradi.
Mahalliy <code>pre-push</code> hook'ni aynan shu buyruqni CI'dan OLDIN
ishga tushiradigan qilib yozish mumkin — shunda dasturchi xato haqida
serverga kutilmasdan, o'z kompyuterida darhol bilib oladi.</p>

<h3>Server tomonidagi hook'lar — yana bir qatlam</h3>
<p>Mahalliy hook'lardan tashqari, Git serverning o'zida ham ishlaydigan
hook'lar bor: <strong>pre-receive</strong> (push qabul qilinishidan oldin,
BUTUN push'ni rad etish imkoniyati bilan) va <strong>update</strong> (har
bir ref uchun alohida). Bular <code>--no-verify</code> bilan CHETLAB
O'TILMAYDI, chunki ular mijoz kompyuterida emas, SERVERDA ishlaydi — bu
GitHub Actions CI bilan bir xil kafolat darajasiga ega, faqat boshqa
mexanizm orqali (GitHub o'zining ichki pre-receive hook'larini branch
protection qoidalari sifatida taqdim qiladi).</p>
""".strip()

L8_TEXT_RU = """
<h3>Что такое hook: скрипты, которые запускает сам Git</h3>
<p>В каждом Git-репозитории есть папка <code>.git/hooks/</code> — там
находятся скрипты, которые Git АВТОМАТИЧЕСКИ запускает при наступлении
ОПРЕДЕЛЁННЫХ событий (перед коммитом, при написании сообщения коммита,
перед push и т.д.). В новом репозитории эта папка содержит только
ПРИМЕРЫ файлов с расширением <code>.sample</code> (например
<code>pre-commit.sample</code>) — они НЕ РАБОТАЮТ, потому что Git ищет
файл без расширения, с правом на выполнение (<code>chmod +x</code>).</p>

<h3>Самые важные локальные hook</h3>
<ul>
<li><strong>pre-commit</strong> — запускается ДО начала <code>git
commit</code>, ещё до запроса сообщения коммита. Если код выхода не 0,
коммит ПОЛНОСТЬЮ останавливается. Обычно: линтер, проверка форматирования
кода, проверка секретов.</li>
<li><strong>commit-msg</strong> — запускается ПОСЛЕ написания сообщения
коммита, но ДО завершения коммита; текст сообщения передаётся как
аргумент. Обычно: проверка формата Conventional Commits
(<code>feat:</code>, <code>fix:</code>).</li>
<li><strong>pre-push</strong> — запускается ДО подключения <code>git
push</code> к серверу. Если код выхода не 0, push ПОЛНОСТЬЮ отменяется.
Обычно: запуск тестов, запрет прямого push в `master`.</li>
</ul>

<h3>Важное ограничение: hook НЕ ВЕРСИОНИРУЮТСЯ</h3>
<p><code>.git/hooks/</code> находится ВНУТРИ <code>.git/</code>, значит
<strong>это не часть истории коммитов репозитория</strong>. Вы не можете
написать скрипт <code>pre-commit</code> и "запушить" его команде — потому
что <code>.git/</code> никогда не push/pull'ится! Каждый разработчик
должен установить hook вручную в своей локальной копии, либо через
инструменты вроде <code>husky</code> или <code>pre-commit</code> (Python),
которые устанавливают их автоматически через файл
<code>package.json</code>/<code>.pre-commit-config.yaml</code> (эти файлы
уже версионируются в репозитории).</p>

<h3>Локальный hook против CI: одна проверка, две разные гарантии</h3>
<p>Эта разница очень важна на практике. В самой этой платформе есть файл
<code>.github/workflows/test.yml</code> — он запускает pytest и Jest
тесты на сервере GitHub при КАЖДОМ push (<code>branches: ["**"]</code>).
Это — <strong>CI hook</strong>: работает на сервере, НИКТО не может его
обойти (даже через <code>--no-verify</code>). Локальный же hook
<code>pre-push</code> запускает тот же тест ДО push, на КОМПЬЮТЕРЕ
разработчика — даёт более быструю обратную связь, но ЛЕГКО обходится
через <code>git push --no-verify</code>. Поэтому нужны оба: локальный
hook — быстрый, необязательный сигнал; CI — медленнее, но
ОБЯЗАТЕЛЬНЫЕ ворота.</p>

<h3>Типы hook и уровень их гарантии</h3>
<pre class="mermaid">
flowchart LR
  A["Разработчик пишет код"] --> B["pre-commit
(локально, можно пропустить через --no-verify)"]
  B --> C["commit-msg
(локально, необязательно)"]
  C --> D["git push"]
  D --> E["pre-push
(локально, можно пропустить через --no-verify)"]
  E --> F["Сервер GitHub:
.github/workflows/test.yml
(CI, НИКАКОЙ --no-verify не поможет)"]
  style F fill:#ffd6d6,stroke:#c00000
  style B fill:#ffe9b3,stroke:#d09000
  style E fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает реальный процесс этой платформы: локальные hook
(жёлтые) — быстрые, но обходимые проверки; GitHub Actions CI (красный) —
работает на сервере, и никто не может его обойти — поэтому "настоящие"
ворота качества всегда должны быть в CI, локальный hook лишь
дополнительное удобство.</p>

<h3>Практический пример: pre-push, соответствующий реальному workflow</h3>
<p><code>test.yml</code> этой платформы запускает для backend <code>python
-m pytest tests/ -v --tb=short</code>. Можно написать локальный
<code>pre-push</code> hook, запускающий именно эту команду ДО CI —
тогда разработчик узнает об ошибке сразу на своём компьютере, не
дожидаясь сервера.</p>

<h3>Серверные hook — ещё один уровень</h3>
<p>Помимо локальных hook, есть hook, работающие на самом сервере Git:
<strong>pre-receive</strong> (перед принятием push, с возможностью
отклонить ВЕСЬ push) и <strong>update</strong> (для каждого ref
отдельно). Их НЕЛЬЗЯ обойти через <code>--no-verify</code>, потому что
они работают не на компьютере клиента, а на СЕРВЕРЕ — это тот же уровень
гарантии, что и GitHub Actions CI, только через другой механизм (GitHub
предоставляет свои внутренние pre-receive hook в виде правил branch
protection).</p>
""".strip()

L8_CODE = """
# ============================================================
# 1) .sample fayllar — nega ISHLAMAYDI
# ============================================================
$ ls .git/hooks/
applypatch-msg.sample  post-update.sample  pre-commit.sample
commit-msg.sample      pre-applypatch.sample  pre-push.sample
...
$ git commit -m "test"
[main abc123] test
# .sample kengaytmasi bo'lgani uchun Git ularni umuman ko'rmaydi.

# ============================================================
# 2) pre-commit hook — maxfiy kalitni tekshirish
# ============================================================
$ cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached | grep -qE "(SECRET_KEY|API_KEY)\\s*=\\s*['\\"][a-zA-Z0-9]"; then
    echo "XATO: staged o'zgarishlarda maxfiy kalit topildi!"
    echo "  .env faylidan foydalaning, kodga yozmang."
    exit 1
fi
exit 0
EOF
$ chmod +x .git/hooks/pre-commit

$ echo 'SECRET_KEY = "abc123supersecret"' >> config.py
$ git add config.py
$ git commit -m "config yangilandi"
XATO: staged o'zgarishlarda maxfiy kalit topildi!
  .env faylidan foydalaning, kodga yozmang.
# Commit BUTUNLAY to'xtatildi — chiqish kodi 1 bo'lgani uchun.

$ git commit -m "config yangilandi" --no-verify
[main def456] config yangilandi
# --no-verify BARCHA mahalliy hook'larni chetlab o'tadi — bu XAVFLI,
# lekin ba'zan qasddan (masalan WIP commit) ishlatiladi.

# ============================================================
# 3) commit-msg hook — Conventional Commits formatini majburlash
# ============================================================
$ cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
MSG_FILE=$1
PATTERN="^(feat|fix|refactor|docs|test|chore|perf|ci)(\\(.+\\))?: .+"
if ! grep -qE "$PATTERN" "$MSG_FILE"; then
    echo "XATO: commit xabari 'feat: ...' yoki 'fix: ...' formatida bo'lishi kerak"
    exit 1
fi
EOF
$ chmod +x .git/hooks/commit-msg

$ git commit -m "narsalarni tuzatdim"
XATO: commit xabari 'feat: ...' yoki 'fix: ...' formatida bo'lishi kerak
$ git commit -m "fix: chegirma hisoblash xatosi tuzatildi"
[main 7c3a1e9] fix: chegirma hisoblash xatosi tuzatildi

# ============================================================
# 4) pre-push hook — shu platformaning test.yml'iga mos avtomatik test
# ============================================================
$ cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "pre-push: backend testlari ishga tushirilmoqda (test.yml kabi)..."
cd backend && python -m pytest tests/ -q --tb=short
if [ $? -ne 0 ]; then
    echo "XATO: testlar muvaffaqiyatsiz, push bekor qilindi."
    echo "(Bu xuddi GitHub Actions serverda qiladigan tekshiruv — farqi:"
    echo " bu yerda push'dan OLDIN, mahalliy kompyuterda bajarilyapti.)"
    exit 1
fi
EOF
$ chmod +x .git/hooks/pre-push

$ git push origin feature-x
pre-push: backend testlari ishga tushirilmoqda (test.yml kabi)...
FAILED tests/test_payment.py::test_discount_applies
XATO: testlar muvaffaqiyatsiz, push bekor qilindi.
error: failed to push some refs

# ============================================================
# 5) Nega hook'lar versiyalanmaydi — isbot
# ============================================================
$ git status --short
# (bo'sh) — .git/hooks/pre-commit HECH QACHON "git status" da ko'rinmaydi,
# chunki u .gitignore'da emas, u .git/ ICHIDA, umuman kuzatilmaydi.

$ git ls-files | grep hooks
# (bo'sh natija) — hook'lar repo tarixining qismi EMAS.

# ============================================================
# 6) Versiyalanadigan yechim: repo ichidagi skript + o'rnatuvchi
# ============================================================
$ mkdir -p scripts/git-hooks
$ cp .git/hooks/pre-push scripts/git-hooks/pre-push
$ git add scripts/git-hooks/pre-push
$ git commit -m "chore: pre-push hook skripti repo'ga qo'shildi"
# Endi har bir dasturchi buni o'rnatishi mumkin:
$ ln -sf ../../scripts/git-hooks/pre-push .git/hooks/pre-push
# Yoki README'da: "git config core.hooksPath scripts/git-hooks"
$ git config core.hooksPath scripts/git-hooks
# Bu Git'ga hook'larni .git/hooks/ o'rniga scripts/git-hooks/ dan
# o'qishni buyuradi — endi versiyalanadigan papka ISHLAYDI.

# ============================================================
# 7) Server tomonidagi pre-receive hook (illyustrativ misol)
# ============================================================
# Bu skript SERVERDA (masalan GitHub Enterprise yoki o'z Git serveringizda)
# joylashadi, mijoz kompyuterida EMAS — shuning uchun --no-verify unga
# ta'sir qilmaydi.
$ cat /path/to/server-repo.git/hooks/pre-receive
#!/bin/bash
while read oldrev newrev refname; do
    if [[ "$refname" == "refs/heads/main" ]]; then
        echo "XATO: main branch'ga to'g'ridan-to'g'ri push taqiqlangan."
        echo "Iltimos, Pull Request oching."
        exit 1
    fi
done

$ git push origin main
remote: XATO: main branch'ga to'g'ridan-to'g'ri push taqiqlangan.
remote: Iltimos, Pull Request oching.
To github.com:team/repo.git
 ! [remote rejected] main -> main (pre-receive hook declined)
# --no-verify bu yerda HECH QANDAY farq qilmaydi, chunki tekshiruv
# mijoz tomonida emas, SERVER tomonida ishlayapti.

# ============================================================
# 8) commit-msg hook'ni kengaytirish — uzunlik tekshiruvi qo'shish
# ============================================================
$ cat scripts/git-hooks/commit-msg
#!/bin/bash
MSG_FILE=$1
FIRST_LINE=$(head -1 "$MSG_FILE")
if [ ${#FIRST_LINE} -gt 72 ]; then
    echo "XATO: birinchi qator 72 belgidan uzun (${#FIRST_LINE} belgi)"
    exit 1
fi
PATTERN="^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+"
if ! grep -qE "$PATTERN" "$MSG_FILE"; then
    echo "XATO: 'feat: ...' yoki 'fix: ...' formatida yozing"
    exit 1
fi
""".strip()

L8_CODE_RU = """
# ============================================================
# 1) Файлы .sample — почему НЕ РАБОТАЮТ
# ============================================================
$ ls .git/hooks/
applypatch-msg.sample  post-update.sample  pre-commit.sample
commit-msg.sample      pre-applypatch.sample  pre-push.sample
...
$ git commit -m "test"
[main abc123] test
# Из-за расширения .sample Git их вообще не видит.

# ============================================================
# 2) pre-commit hook — проверка секретного ключа
# ============================================================
$ cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached | grep -qE "(SECRET_KEY|API_KEY)\\s*=\\s*['\\"][a-zA-Z0-9]"; then
    echo "ОШИБКА: в staged-изменениях найден секретный ключ!"
    echo "  Используйте файл .env, не пишите в код."
    exit 1
fi
exit 0
EOF
$ chmod +x .git/hooks/pre-commit

$ echo 'SECRET_KEY = "abc123supersecret"' >> config.py
$ git add config.py
$ git commit -m "обновление config"
ОШИБКА: в staged-изменениях найден секретный ключ!
  Используйте файл .env, не пишите в код.
# Коммит ПОЛНОСТЬЮ остановлен — из-за кода выхода 1.

$ git commit -m "обновление config" --no-verify
[main def456] обновление config
# --no-verify обходит ВСЕ локальные hook — это ОПАСНО, но иногда
# используется намеренно (например, WIP-коммит).

# ============================================================
# 3) commit-msg hook — принуждение к формату Conventional Commits
# ============================================================
$ cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
MSG_FILE=$1
PATTERN="^(feat|fix|refactor|docs|test|chore|perf|ci)(\\(.+\\))?: .+"
if ! grep -qE "$PATTERN" "$MSG_FILE"; then
    echo "ОШИБКА: сообщение коммита должно быть в формате 'feat: ...' или 'fix: ...'"
    exit 1
fi
EOF
$ chmod +x .git/hooks/commit-msg

$ git commit -m "исправил кое-что"
ОШИБКА: сообщение коммита должно быть в формате 'feat: ...' или 'fix: ...'
$ git commit -m "fix: исправлена ошибка расчёта скидки"
[main 7c3a1e9] fix: исправлена ошибка расчёта скидки

# ============================================================
# 4) pre-push hook — автоматический тест по образцу test.yml этой платформы
# ============================================================
$ cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "pre-push: запускаются тесты backend (как в test.yml)..."
cd backend && python -m pytest tests/ -q --tb=short
if [ $? -ne 0 ]; then
    echo "ОШИБКА: тесты не прошли, push отменён."
    echo "(Это та же проверка, что делает GitHub Actions на сервере —"
    echo " разница в том, что здесь она выполняется ДО push, локально.)"
    exit 1
fi
EOF
$ chmod +x .git/hooks/pre-push

$ git push origin feature-x
pre-push: запускаются тесты backend (как в test.yml)...
FAILED tests/test_payment.py::test_discount_applies
ОШИБКА: тесты не прошли, push отменён.
error: failed to push some refs

# ============================================================
# 5) Почему hook не версионируются — доказательство
# ============================================================
$ git status --short
# (пусто) — .git/hooks/pre-commit НИКОГДА не виден в "git status",
# потому что он не в .gitignore, он ВНУТРИ .git/, вообще не отслеживается.

$ git ls-files | grep hooks
# (пустой результат) — hook НЕ являются частью истории репозитория.

# ============================================================
# 6) Версионируемое решение: скрипт в репозитории + установщик
# ============================================================
$ mkdir -p scripts/git-hooks
$ cp .git/hooks/pre-push scripts/git-hooks/pre-push
$ git add scripts/git-hooks/pre-push
$ git commit -m "chore: скрипт pre-push hook добавлен в репозиторий"
# Теперь каждый разработчик может его установить:
$ ln -sf ../../scripts/git-hooks/pre-push .git/hooks/pre-push
# Или в README: "git config core.hooksPath scripts/git-hooks"
$ git config core.hooksPath scripts/git-hooks
# Это говорит Git читать hook из scripts/git-hooks/ вместо .git/hooks/ —
# теперь версионируемая папка РАБОТАЕТ.

# ============================================================
# 7) Серверный pre-receive hook (иллюстративный пример)
# ============================================================
# Этот скрипт находится НА СЕРВЕРЕ (например GitHub Enterprise или
# собственном Git-сервере), не на компьютере клиента — поэтому
# --no-verify на него не влияет.
$ cat /path/to/server-repo.git/hooks/pre-receive
#!/bin/bash
while read oldrev newrev refname; do
    if [[ "$refname" == "refs/heads/main" ]]; then
        echo "ОШИБКА: прямой push в main запрещён."
        echo "Пожалуйста, откройте Pull Request."
        exit 1
    fi
done

$ git push origin main
remote: ОШИБКА: прямой push в main запрещён.
remote: Пожалуйста, откройте Pull Request.
To github.com:team/repo.git
 ! [remote rejected] main -> main (pre-receive hook declined)
# --no-verify здесь НИКАК не поможет, потому что проверка работает не
# на стороне клиента, а на стороне СЕРВЕРА.

# ============================================================
# 8) Расширение commit-msg hook — добавление проверки длины
# ============================================================
$ cat scripts/git-hooks/commit-msg
#!/bin/bash
MSG_FILE=$1
FIRST_LINE=$(head -1 "$MSG_FILE")
if [ ${#FIRST_LINE} -gt 72 ]; then
    echo "ОШИБКА: первая строка длиннее 72 символов (${#FIRST_LINE})"
    exit 1
fi
PATTERN="^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+"
if ! grep -qE "$PATTERN" "$MSG_FILE"; then
    echo "ОШИБКА: пишите в формате 'feat: ...' или 'fix: ...'"
    exit 1
fi
""".strip()

L8_TASK = {
    "task_title": "test.yml'ga mos pre-push hook yarating",
    "task_title_ru": "Создайте pre-push hook по образцу test.yml",
    "task_description": (
        "Ushbu platformaning `.github/workflows/test.yml` faylini o'qib "
        "chiqing. Xuddi shu backend test buyrug'ini (`python -m pytest "
        "tests/ -v --tb=short`) push'dan OLDIN mahalliy ravishda ishga "
        "tushiradigan `pre-push` hook yozing. So'ngra buni "
        "`scripts/git-hooks/` papkasiga ko'chirib, `core.hooksPath` "
        "orqali versiyalanadigan qilib qo'ying — shunda u jamoa bilan "
        "baham ko'rilishi mumkin."
    ),
    "task_description_ru": (
        "Прочитайте файл `.github/workflows/test.yml` этой платформы. "
        "Напишите `pre-push` hook, который локально запускает ту же "
        "команду теста backend (`python -m pytest tests/ -v "
        "--tb=short`) ДО push. Затем перенесите его в папку "
        "`scripts/git-hooks/` и сделайте версионируемым через "
        "`core.hooksPath` — чтобы им можно было поделиться с командой."
    ),
    "task_requirements": (
        "1) Testlar muvaffaqiyatsiz bo'lganda push BEKOR qilinishini "
        "ko'rsating (chiqish kodi orqali). 2) `--no-verify` bilan hook "
        "chetlab o'tilishini isbotlang. 3) `core.hooksPath` "
        "sozlangandan keyin `git ls-files` orqali hook skripti ENDI "
        "repo tarixida ekanini ko'rsating (oddiy `.git/hooks/`dan "
        "farqli)."
    ),
    "task_requirements_ru": (
        "1) Покажите, что при неуспешных тестах push ОТМЕНЯЕТСЯ (через "
        "код выхода). 2) Докажите, что hook можно обойти через "
        "`--no-verify`. 3) После настройки `core.hooksPath` покажите "
        "через `git ls-files`, что скрипт hook ТЕПЕРЬ в истории "
        "репозитория (в отличие от обычного `.git/hooks/`)."
    ),
    "task_technologies": "Git hooks (pre-push, commit-msg), pytest, GitHub Actions (grounding)",
    "task_deadline_days": 4,
}

L8_SAMPLE = {
    "title": "Namuna: versiyalanadigan hook to'plami",
    "description": (
        "core.hooksPath orqali ishlaydigan uchta hook (pre-commit, "
        "commit-msg, pre-push) — bularning barchasi repo ichida "
        "versiyalanadi, shu platformaning test.yml uslubiga mos."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "scripts/git-hooks/pre-commit",
            "language": "bash",
            "code": (
                "#!/bin/bash\n"
                "# Maxfiy kalitlarni staged o'zgarishlarda tekshiradi.\n"
                "if git diff --cached | grep -qE \"(SECRET_KEY|API_KEY|PASSWORD)\\s*=\\s*['\\\"][a-zA-Z0-9]\"; then\n"
                "    echo \"XATO: staged o'zgarishlarda maxfiy kalit topildi!\"\n"
                "    exit 1\n"
                "fi\n"
                "exit 0\n"
            ),
        },
        {
            "filename": "scripts/git-hooks/commit-msg",
            "language": "bash",
            "code": (
                "#!/bin/bash\n"
                "# Conventional Commits formatini majburlaydi.\n"
                "MSG_FILE=$1\n"
                "PATTERN=\"^(feat|fix|refactor|docs|test|chore|perf|ci)(\\(.+\\))?: .+\"\n"
                "if ! grep -qE \"$PATTERN\" \"$MSG_FILE\"; then\n"
                "    echo \"XATO: 'feat: ...' yoki 'fix: ...' formatida yozing\"\n"
                "    exit 1\n"
                "fi\n"
            ),
        },
        {
            "filename": "scripts/git-hooks/pre-push",
            "language": "bash",
            "code": (
                "#!/bin/bash\n"
                "# .github/workflows/test.yml'dagi backend bosqichi bilan bir xil buyruq.\n"
                "echo \"pre-push: backend testlari (test.yml kabi)...\"\n"
                "( cd backend && python -m pytest tests/ -q --tb=short )\n"
                "STATUS=$?\n"
                "if [ $STATUS -ne 0 ]; then\n"
                "    echo \"XATO: testlar o'tmadi, push bekor qilindi.\"\n"
                "    exit 1\n"
                "fi\n"
                "exit 0\n"
            ),
        },
        {
            "filename": "scripts/git-hooks/README.md",
            "language": "markdown",
            "code": (
                "# Versiyalanadigan Git hooks\n\n"
                "O'rnatish:\n\n"
                "```bash\n"
                "git config core.hooksPath scripts/git-hooks\n"
                "chmod +x scripts/git-hooks/*\n"
                "```\n\n"
                "Bu buyruq Git'ga hook'larni `.git/hooks/` (versiyalanmaydigan) "
                "o'rniga `scripts/git-hooks/` (repo bilan versiyalanadigan) "
                "papkadan o'qishni buyuradi.\n"
            ),
        },
    ],
}

L8_EXERCISES = [
    {
        "title": "pre-commit vs pre-push",
        "title_ru": "pre-commit против pre-push",
        "description": "pre-commit va pre-push hook'lari orasidagi asosiy farq nima?",
        "description_ru": "В чём главная разница между hook pre-commit и pre-push?",
        "exercise_type": "multiple_choice",
        "options": [
            "pre-commit har bir commit'dan oldin, pre-push serverga yuborishdan oldin ishlaydi",
            "pre-commit serverda, pre-push mahalliy kompyuterda ishlaydi",
            "Ular bir xil, faqat nomi farq qiladi",
            "pre-push faqat GitHub Actions ichida ishlaydi",
        ],
        "options_ru": [
            "pre-commit срабатывает перед каждым коммитом, pre-push — перед отправкой на сервер",
            "pre-commit работает на сервере, pre-push — на локальном компьютере",
            "Они одинаковы, отличается только название",
            "pre-push работает только внутри GitHub Actions",
        ],
        "correct_answers": "A",
        "hint": "Nomlarining o'zi qachon ishga tushishini ko'rsatadi.",
        "hint_ru": "Сами названия указывают, когда они срабатывают.",
        "explanation": "pre-commit commit yaratilishidan oldin, pre-push esa push serverga ulanishidan oldin ishga tushadi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Hook ishga tushish ketma-ketligi",
        "title_ru": "Порядок срабатывания hook",
        "description": "Oddiy commit va push jarayonida hook'larning ishga tushish tartibini joylashtiring.",
        "description_ru": "Расположите порядок срабатывания hook в обычном процессе commit и push.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "pre-commit (commit boshlanishidan oldin)",
            "commit-msg (xabar yozilgandan keyin)",
            "pre-push (push serverga ulanishidan oldin)",
            "GitHub Actions CI (serverda, push qabul qilingandan keyin)",
        ],
        "drag_items_ru": [
            "pre-commit (перед началом коммита)",
            "commit-msg (после написания сообщения)",
            "pre-push (перед подключением push к серверу)",
            "GitHub Actions CI (на сервере, после получения push)",
        ],
        "correct_order": [
            "pre-commit (commit boshlanishidan oldin)",
            "commit-msg (xabar yozilgandan keyin)",
            "pre-push (push serverga ulanishidan oldin)",
            "GitHub Actions CI (serverda, push qabul qilingandan keyin)",
        ],
        "hint": "Avval commit hodisalari, keyin push, oxirida server.",
        "hint_ru": "Сначала события коммита, потом push, в конце сервер.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Nega mahalliy hook yetarli emas",
        "title_ru": "Почему локального hook недостаточно",
        "description": "Nega faqat mahalliy pre-push hook'ga tayanib, GitHub Actions CI'siz qolib bo'lmaydi? (2-3 gap bilan tushuntiring, --no-verify'ni eslatib o'ting.)",
        "description_ru": "Почему нельзя полагаться только на локальный hook pre-push без GitHub Actions CI? (Объясните 2-3 предложениями, упомянув --no-verify.)",
        "exercise_type": "text_input",
        "expected_answer": "Mahalliy hook --no-verify bilan oson chetlab o'tiladi va faqat bitta dasturchining kompyuterida ishlaydi, CI esa serverda ishlaydi va uni hech kim chetlab o'ta olmaydi, shuning uchun haqiqiy majburiy tekshiruv faqat CI'da bo'lishi kerak.",
        "hint": "8-darsdagi diagrammani va --no-verify bo'limini eslang.",
        "hint_ru": "Вспомните диаграмму из урока 8 и раздел про --no-verify.",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 9 — Ilg'or merge-konflikt strategiyalari: rerere, merge drayverlari
# ---------------------------------------------------------------------------

L9_TEXT = """
<h3>45-kursdagi konfliktdan farqi</h3>
<p>45-kursda siz konfliktni QO'LDA — <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>
belgilarini ko'rib, kerakli qismni tanlab — yechishni o'rgandingiz. Bu
dars bitta savolga javob beradi: agar BIR XIL konflikt QAYTA-QAYTA
chiqsa-chi (masalan, uzoq muddatli feature branch'ni har hafta
<code>main</code>dan rebase qilsangiz)? Yoki ba'zi fayl turlari uchun
konflikt yechimi HAR DOIM bitta tomonni tanlash bo'lsa-chi (masalan,
avtomatik generatsiya qilingan fayl)?</p>

<h3>git rerere — "reuse recorded resolution"</h3>
<p><code>git config rerere.enabled true</code> yoqilgandan so'ng, Git HAR
BIR konflikt yechimingizni <code>.git/rr-cache/</code>ga ESLAB QOLADI:
konflikt qanday ko'rinishda edi va siz uni qanday yechdingiz. Xuddi shu
konflikt (bir xil ikki tomon) KEYINGI safar chiqsa, Git uni AVTOMATIK
qo'llaydi — sizdan qayta so'ramaydi. Bu ayniqsa uzoq muddatli branch'ni
qayta-qayta rebase qilishda juda foydali: birinchi safar qo'lda
yechilgan konflikt qolgan barcha keyingi rebase urinishlarida AVTOMATIK
takrorlanadi.</p>

<h3>Custom merge drivers — fayl turiga qarab maxsus mantiq</h3>
<p><code>.gitattributes</code> faylida ma'lum fayl naqshi uchun maxsus
merge strategiyasini belgilash mumkin: <code>*.generated.json
merge=ours</code>. Bu Git'ga "bu fayllarda konflikt chiqsa,
<strong>doim mening tomonimni</strong> (HOZIRGI branch'nikini) tanla,
boshqa tomonni butunlay e'tiborsiz qoldir" deb aytadi. Bu ayniqsa
avtomatik generatsiya qilinadigan (masalan, lock fayllar, kompilyatsiya
natijalari) fayllar uchun foydali — ularni QO'LDA birlashtirish
mantiqsiz, chunki ular baribir qayta generatsiya qilinadi.</p>

<h3>-X ours / -X theirs — bitta merge uchun</h3>
<p><code>git merge -X ours</code> — <code>merge=ours</code> drayveridan
FARQLI: bu FAQAT konflikt qatorlarida joriy branch versiyasini tanlaydi,
BOSHQA (konflikt bo'lmagan) o'zgarishlar hali ham birlashtiriladi.
<code>-X theirs</code> — teskarisi, boshqa branch versiyasini tanlaydi.
Diqqat: <code>merge=ours</code> drayveri BUTUN faylni e'tiborsiz
qoldiradi, <code>-X ours</code> esa faqat KONFLIKT QATORLARIDA joriy
tomonni tanlaydi — bu ikkisi ko'pincha chalkashtiriladi!</p>

<h3>Konflikt yechish oqimi — vizual</h3>
<pre class="mermaid">
flowchart TB
  A["Merge/rebase boshlanadi"] --> B{"Konflikt bormi?"}
  B -->|"yo'q"| Z["Avtomatik yakunlanadi"]
  B -->|"ha"| C{"rerere avval shu konfliktni ko'rganmi?"}
  C -->|"ha"| D["Avtomatik qo'llaniladi
(rerere.enabled=true)"]
  C -->|"yo'q"| E{".gitattributes'da
merge drayveri bormi?"}
  E -->|"ha (masalan merge=ours)"| F["Belgilangan strategiya
avtomatik qo'llaniladi"]
  E -->|"yo'q"| G["Qo'lda yechish:
markerlarni tahrirlash + git add"]
  G --> H["rerere yechimni ESLAB QOLADI
(keyingi safar uchun)"]
  style D fill:#d6e9ff,stroke:#2266aa
  style F fill:#d6e9ff,stroke:#2266aa
  style G fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma shu narsani ko'rsatadi: konflikt yuzaga kelganda Git avval
oldindan belgilangan avtomatik yechimlarni (rerere xotirasi, merge
drayverlari) tekshiradi, faqat ular bo'lmasa qo'lda aralashuv talab
qilinadi — va o'sha qo'lda yechim KEYINGI safarlar uchun rerere orqali
ESLAB QOLINADI.</p>

<h3>Qachon qaysi vositani ishlatish</h3>
<table>
<tr><th>Vosita</th><th>Qachon foydali</th></tr>
<tr><td><code>rerere</code></td><td>Uzoq muddatli branch'ni qayta-qayta rebase qilishda, bir xil konflikt qayta chiqsa</td></tr>
<tr><td><code>merge=ours</code> drayveri</td><td>Avtomatik generatsiya qilinadigan fayllar, lock fayllar uchun doimiy qoida</td></tr>
<tr><td><code>-X ours/theirs</code></td><td>Bitta aniq merge uchun, faqat konflikt qatorlarida bitta tomonni afzal ko'rish</td></tr>
</table>

<h3>diff3 konflikt uslubi — umumiy ajdodni ham ko'rsatish</h3>
<p>Odatiy konflikt belgilari faqat IKKI tomonni (HEAD va boshqa branch)
ko'rsatadi — lekin ba'zan "aslida asl holat qanday edi" bilishni talab
qiladi. <code>git config merge.conflictStyle diff3</code> yoqilgandan
so'ng konflikt belgilarida UCHINCHI qism —
<code>|||||||</code> — paydo bo'ladi, u umumiy ajdod (ikkala branch
ajralib chiqqan nuqtadagi) versiyasini ko'rsatadi. Bu ayniqsa ikkala
tomon ham ASL qatorni turlicha o'zgartirganda, qaysi o'zgarish
"to'g'ri niyat" ekanligini tushunishga yordam beradi.</p>

<h3>git mergetool — vizual konflikt yechish</h3>
<p>Matn ko'rinishidagi konflikt belgilarini qo'lda o'qish o'rniga,
<code>git mergetool</code> buyrug'i sozlangan grafik vositani (masalan
<code>vimdiff</code>, <code>meld</code>, <code>kdiff3</code>) ochadi — u
uch panelli ko'rinishda (local/base/remote) konfliktni vizual
taqqoslashga imkon beradi. Bu <code>rerere</code> bilan birga ishlaydi:
<code>mergetool</code> orqali yechilgan konflikt HAM keyingi safar
avtomatik eslab qolinadi.</p>
""".strip()

L9_TEXT_RU = """
<h3>Отличие от конфликтов из курса 45</h3>
<p>В курсе 45 вы научились разрешать конфликт ВРУЧНУЮ — видя маркеры
<code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> и выбирая нужную часть. Этот
урок отвечает на один вопрос: что если ОДИН И ТОТ ЖЕ конфликт возникает
СНОВА И СНОВА (например, вы каждую неделю делаете rebase долгоживущей
feature-ветки от <code>main</code>)? Или если для некоторых типов файлов
решение конфликта ВСЕГДА — выбрать одну сторону (например, автоматически
сгенерированный файл)?</p>

<h3>git rerere — "reuse recorded resolution"</h3>
<p>После включения <code>git config rerere.enabled true</code> Git
ЗАПОМИНАЕТ КАЖДОЕ ваше решение конфликта в <code>.git/rr-cache/</code>:
как выглядел конфликт и как вы его разрешили. Если ТОТ ЖЕ конфликт (те
же две стороны) возникнет СЛЕДУЮЩИЙ раз, Git применит его АВТОМАТИЧЕСКИ
— не спросит снова. Это особенно полезно при повторяющемся rebase
долгоживущей ветки: конфликт, разрешённый вручную в первый раз,
АВТОМАТИЧЕСКИ повторяется во всех последующих попытках rebase.</p>

<h3>Custom merge drivers — специальная логика по типу файла</h3>
<p>В файле <code>.gitattributes</code> можно задать специальную
стратегию merge для определённого шаблона файлов: <code>*.generated.json
merge=ours</code>. Это говорит Git: "если в этих файлах возникнет
конфликт, всегда выбирай <strong>мою сторону</strong> (текущей ветки),
полностью игнорируя другую сторону". Это особенно полезно для
автоматически генерируемых файлов (например, lock-файлы, результаты
компиляции) — их объединение ВРУЧНУЮ бессмысленно, поскольку они всё
равно будут перегенерированы.</p>

<h3>-X ours / -X theirs — для одного merge</h3>
<p><code>git merge -X ours</code> — ОТЛИЧАЕТСЯ от драйвера
<code>merge=ours</code>: он выбирает версию текущей ветки ТОЛЬКО в
конфликтующих строках, ОСТАЛЬНЫЕ (неконфликтующие) изменения всё равно
объединяются. <code>-X theirs</code> — наоборот, выбирает версию другой
ветки. Внимание: драйвер <code>merge=ours</code> игнорирует ВЕСЬ файл, а
<code>-X ours</code> выбирает текущую сторону ТОЛЬКО В КОНФЛИКТУЮЩИХ
СТРОКАХ — это часто путают!</p>

<h3>Процесс разрешения конфликта — визуально</h3>
<pre class="mermaid">
flowchart TB
  A["Начинается merge/rebase"] --> B{"Есть конфликт?"}
  B -->|"нет"| Z["Автоматически завершается"]
  B -->|"да"| C{"rerere уже видел этот конфликт?"}
  C -->|"да"| D["Применяется автоматически
(rerere.enabled=true)"]
  C -->|"нет"| E{"Есть ли merge driver
в .gitattributes?"}
  E -->|"да (например merge=ours)"| F["Заданная стратегия
применяется автоматически"]
  E -->|"нет"| G["Ручное разрешение:
редактирование маркеров + git add"]
  G --> H["rerere ЗАПОМИНАЕТ решение
(для следующего раза)"]
  style D fill:#d6e9ff,stroke:#2266aa
  style F fill:#d6e9ff,stroke:#2266aa
  style G fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает: при возникновении конфликта Git сначала
проверяет заранее заданные автоматические решения (память rerere, merge
drivers), и только если их нет, требуется ручное вмешательство — а это
ручное решение ЗАПОМИНАЕТСЯ через rerere для следующих раз.</p>

<h3>Когда какой инструмент использовать</h3>
<table>
<tr><th>Инструмент</th><th>Когда полезен</th></tr>
<tr><td><code>rerere</code></td><td>При повторяющемся rebase долгоживущей ветки, когда возникает один и тот же конфликт</td></tr>
<tr><td>драйвер <code>merge=ours</code></td><td>Для автоматически генерируемых, lock-файлов — постоянное правило</td></tr>
<tr><td><code>-X ours/theirs</code></td><td>Для одного конкретного merge, предпочесть одну сторону только в конфликтующих строках</td></tr>
</table>

<h3>Стиль конфликта diff3 — показ общего предка тоже</h3>
<p>Обычные маркеры конфликта показывают только ДВЕ стороны (HEAD и
другую ветку) — но иногда нужно знать, "как было изначально". После
включения <code>git config merge.conflictStyle diff3</code> в маркерах
конфликта появляется ТРЕТЬЯ часть — <code>|||||||</code>, показывающая
версию общего предка (в точке, где разошлись обе ветки). Это особенно
помогает, когда ОБЕ стороны по-разному изменили ИСХОДНУЮ строку —
понять, какое изменение было "правильным намерением".</p>

<h3>git mergetool — визуальное разрешение конфликтов</h3>
<p>Вместо ручного чтения текстовых маркеров конфликта, команда <code>git
mergetool</code> открывает настроенный графический инструмент (например
<code>vimdiff</code>, <code>meld</code>, <code>kdiff3</code>) — он даёт
визуальное трёхпанельное сравнение (local/base/remote). Это работает
вместе с <code>rerere</code>: конфликт, разрешённый через
<code>mergetool</code>, ТАКЖЕ запоминается автоматически для следующего
раза.</p>
""".strip()

L9_CODE = """
# ============================================================
# 1) rerere'ni yoqish va birinchi konfliktni yechish
# ============================================================
$ git config rerere.enabled true
$ git rerere status
# hali hech narsa yo'q

$ git merge feature-a
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Recorded preimage for 'config.py'
# "Recorded preimage" — rerere konfliktning KO'RINISHINI eslab qolayapti.

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> feature-a
$ vim config.py    # qo'lda TIMEOUT = 45 deb yechamiz
$ git add config.py
$ git commit
Recorded resolution for 'config.py'.
# "Recorded resolution" — bu safar YECHIMNI ham eslab qoldi.

# ============================================================
# 2) Xuddi shu konflikt qayta chiqsa — AVTOMATIK yechiladi
# ============================================================
$ git rebase main   # feature-a ni main ustiga qayta joylashtiramiz
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Resolved 'config.py' using previous resolution.
# rerere DARHOL avvalgi yechimni qo'lladi — qayta qo'lda tuzatish shart emas!
$ git status --short
# (config.py allaqachon avtomatik yechilgan holda staged)
$ git rebase --continue

# ============================================================
# 3) rerere keshini ko'rish
# ============================================================
$ ls .git/rr-cache/
a3f291e8d7c6b5a4938271605f4e3d2c1b0a9f8/
$ ls .git/rr-cache/a3f291e8d7c6b5a4938271605f4e3d2c1b0a9f8/
postimage  preimage

# ============================================================
# 4) .gitattributes orqali custom merge driver
# ============================================================
$ cat .gitattributes
package-lock.json merge=ours
*.generated.json merge=ours

$ git config merge.ours.driver true
# "true" buyrug'i har doim 0 (muvaffaqiyat) qaytaradi -> HECH QANDAY
# birlashtirish qilinmaydi, joriy branch versiyasi saqlanadi.

$ git merge feature-b
Auto-merging package-lock.json
Merge made by the 'ort' strategy.
# package-lock.json'da konflikt BO'LSA HAM, u ko'rsatilmaydi —
# HAR DOIM bizning (HEAD) versiyamiz saqlanadi, boshqa tomon e'tiborsiz.

# ============================================================
# 5) -X ours vs merge=ours — MUHIM farq
# ============================================================
$ git merge -X ours feature-c
# config.py'da konflikt bo'lsa — FAQAT konflikt qatorlarida bizning
# versiyamiz tanlanadi, LEKIN feature-c'dagi BOSHQA (konfliktsiz)
# o'zgarishlar hali ham qo'shiladi:
$ git diff HEAD~1 --stat
config.py       | 2 +-
new_feature.py  | 15 +++++++++++++++    # <- bu hali ham qo'shildi!

# merge=ours drayveri esa BUTUN faylni e'tiborsiz qoldiradi:
$ git merge feature-d   # package-lock.json uchun merge=ours ishlaydi
$ git diff HEAD~1 -- package-lock.json
# (bo'sh — fayl UMUMAN o'zgarmadi, feature-d'dagi o'zgarishlar yo'qoldi)

# ============================================================
# 6) rerere'ni tozalash (eskirgan yechimlar to'planganda)
# ============================================================
$ git rerere gc
# gc.rerereResolved (odatda 60 kun) va gc.rerereUnresolved (15 kun)
# muddatidan o'tgan yozuvlarni tozalaydi.

# ============================================================
# 7) diff3 konflikt uslubi — umumiy ajdodni ko'rish
# ============================================================
$ git config merge.conflictStyle diff3
$ git merge feature-a
CONFLICT (content): Merge conflict in config.py

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 45
||||||| a1b2c3d (umumiy ajdod)
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> feature-a
# Endi UCHTA versiya ko'rinadi: HEAD (45), asl ajdod (30), feature-a (60).
# Buni ko'rib, "ikkalasi ham asl 30'dan boshqacha yo'nalishda o'zgartirgan"
# ekanini tushunish osonlashadi — oddiy ikki tomonlama diff bunday
# kontekstni bermas edi.

# ============================================================
# 8) git mergetool — vizual yechim
# ============================================================
$ git config merge.tool vimdiff
$ git mergetool
Merging:
config.py

Normal merge conflict for 'config.py':
  {local}: modified file
  {base}: modified file
  {remote}: modified file
Hit return to start merge resolution tool (vimdiff):
# vimdiff to'rt panelli ko'rinishda ochiladi: LOCAL | BASE | MERGED | REMOTE
# Qo'lda kerakli qatorlarni tanlab, :wqa bilan saqlab chiqiladi.

$ git status --short
M  config.py    # mergetool orqali yechilgan, endi staged
$ git commit --no-edit
Recorded resolution for 'config.py'.
# rerere BU YERDA ham ishlaydi — mergetool orqali yechilgan konflikt ham
# keyingi safar avtomatik eslab qolinadi.
""".strip()

L9_CODE_RU = """
# ============================================================
# 1) Включение rerere и разрешение первого конфликта
# ============================================================
$ git config rerere.enabled true
$ git rerere status
# пока ничего нет

$ git merge feature-a
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Recorded preimage for 'config.py'
# "Recorded preimage" — rerere запоминает КАК ВЫГЛЯДИТ конфликт.

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> feature-a
$ vim config.py    # вручную решаем TIMEOUT = 45
$ git add config.py
$ git commit
Recorded resolution for 'config.py'.
# "Recorded resolution" — на этот раз запомнил и РЕШЕНИЕ.

# ============================================================
# 2) Тот же конфликт возникает снова — разрешается АВТОМАТИЧЕСКИ
# ============================================================
$ git rebase main   # переносим feature-a на main
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Resolved 'config.py' using previous resolution.
# rerere СРАЗУ применил прошлое решение — заново вручную исправлять не нужно!
$ git status --short
# (config.py уже автоматически разрешён и в staged)
$ git rebase --continue

# ============================================================
# 3) Просмотр кэша rerere
# ============================================================
$ ls .git/rr-cache/
a3f291e8d7c6b5a4938271605f4e3d2c1b0a9f8/
$ ls .git/rr-cache/a3f291e8d7c6b5a4938271605f4e3d2c1b0a9f8/
postimage  preimage

# ============================================================
# 4) Кастомный merge driver через .gitattributes
# ============================================================
$ cat .gitattributes
package-lock.json merge=ours
*.generated.json merge=ours

$ git config merge.ours.driver true
# Команда "true" всегда возвращает 0 (успех) -> НИКАКОГО объединения не
# происходит, сохраняется версия текущей ветки.

$ git merge feature-b
Auto-merging package-lock.json
Merge made by the 'ort' strategy.
# ДАЖЕ ЕСЛИ в package-lock.json есть конфликт, он не показывается —
# ВСЕГДА сохраняется наша (HEAD) версия, другая сторона игнорируется.

# ============================================================
# 5) -X ours против merge=ours — ВАЖНАЯ разница
# ============================================================
$ git merge -X ours feature-c
# если в config.py конфликт — выбирается наша версия ТОЛЬКО в
# конфликтующих строках, НО другие (неконфликтующие) изменения из
# feature-c всё равно добавляются:
$ git diff HEAD~1 --stat
config.py       | 2 +-
new_feature.py  | 15 +++++++++++++++    # <- это всё равно добавилось!

# Драйвер merge=ours же игнорирует ВЕСЬ файл:
$ git merge feature-d   # для package-lock.json работает merge=ours
$ git diff HEAD~1 -- package-lock.json
# (пусто — файл ВООБЩЕ не изменился, изменения из feature-d потерялись)

# ============================================================
# 6) Очистка rerere (когда накапливаются устаревшие решения)
# ============================================================
$ git rerere gc
# Очищает записи старше gc.rerereResolved (обычно 60 дней) и
# gc.rerereUnresolved (15 дней).

# ============================================================
# 7) Стиль конфликта diff3 — просмотр общего предка
# ============================================================
$ git config merge.conflictStyle diff3
$ git merge feature-a
CONFLICT (content): Merge conflict in config.py

$ cat config.py
<<<<<<< HEAD
TIMEOUT = 45
||||||| a1b2c3d (общий предок)
TIMEOUT = 30
=======
TIMEOUT = 60
>>>>>>> feature-a
# Теперь видны ТРИ версии: HEAD (45), исходный предок (30), feature-a (60).
# Видя это, легче понять, что "обе стороны изменили исходные 30 в разных
# направлениях" — обычный двусторонний diff такого контекста не давал.

# ============================================================
# 8) git mergetool — визуальное решение
# ============================================================
$ git config merge.tool vimdiff
$ git mergetool
Merging:
config.py

Normal merge conflict for 'config.py':
  {local}: modified file
  {base}: modified file
  {remote}: modified file
Hit return to start merge resolution tool (vimdiff):
# vimdiff открывается в четырёхпанельном виде: LOCAL | BASE | MERGED | REMOTE
# Вручную выбираются нужные строки, сохраняются через :wqa.

$ git status --short
M  config.py    # разрешено через mergetool, теперь staged
$ git commit --no-edit
Recorded resolution for 'config.py'.
# rerere РАБОТАЕТ и ЗДЕСЬ — конфликт, разрешённый через mergetool, тоже
# запоминается автоматически для следующего раза.
""".strip()

L9_TASK = {
    "task_title": "rerere bilan takroriy konfliktni avtomatlashtiring",
    "task_title_ru": "Автоматизируйте повторяющийся конфликт через rerere",
    "task_description": (
        "Ikkita branch yarating (`main` va `feature-x`), ular BIR XIL "
        "faylning bir xil qatorini turlicha o'zgartirsin (konflikt "
        "hosil qiling). `git config rerere.enabled true` yoqing, "
        "konfliktni QO'LDA yeching va commit qiling. So'ngra "
        "`feature-x`ni RESET qilib, xuddi shu merge/rebase'ni QAYTA "
        "ishga tushiring — bu safar rerere avtomatik yechishini "
        "ko'rsating."
    ),
    "task_description_ru": (
        "Создайте две ветки (`main` и `feature-x`), которые по-разному "
        "меняют ОДНУ И ТУ ЖЕ строку одного файла (создайте конфликт). "
        "Включите `git config rerere.enabled true`, разрешите конфликт "
        "ВРУЧНУЮ и закоммитьте. Затем СБРОСЬТЕ `feature-x` и ЗАНОВО "
        "запустите тот же merge/rebase — покажите, что на этот раз "
        "rerere разрешает автоматически."
    ),
    "task_requirements": (
        "1) Birinchi marta 'Recorded resolution' xabarini ko'rsating. "
        "2) Ikkinchi marta 'Resolved ... using previous resolution' "
        "xabarini ko'rsating. 3) `.git/rr-cache/` ichidagi fayllarni "
        "`ls` bilan ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Покажите сообщение 'Recorded resolution' в первый раз. 2) "
        "Покажите сообщение 'Resolved ... using previous resolution' во "
        "второй раз. 3) Покажите файлы внутри `.git/rr-cache/` через "
        "`ls`."
    ),
    "task_technologies": "Git (rerere, merge, rebase)",
    "task_deadline_days": 4,
}

L9_SAMPLE = {
    "title": "Namuna: rerere avtomatlashtirish skripti",
    "description": (
        "Bash skripti bir xil konfliktni ikki marta hosil qiladi — "
        "birinchi marta qo'lda, ikkinchi marta rerere orqali avtomatik "
        "yechilishini ko'rsatadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "rerere_demo.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf rerere_demo && mkdir rerere_demo && cd rerere_demo && git init -q\n"
                "git config rerere.enabled true\n\n"
                "echo 'TIMEOUT = 30' > config.py\n"
                "git add . && git commit -q -m \"c0\"\n\n"
                "git switch -q -c feature-x\n"
                "echo 'TIMEOUT = 60' > config.py\n"
                "git commit -qam \"feature-x: timeout oshirildi\"\n\n"
                "git switch -q main 2>/dev/null || git switch -q master\n"
                "echo 'TIMEOUT = 45' > config.py\n"
                "git commit -qam \"main: timeout boshqacha o'zgartirildi\"\n\n"
                "echo \"=== BIRINCHI MARTA: qo'lda yechamiz ===\"\n"
                "git merge feature-x --no-edit 2>&1 | tail -3 || true\n"
                "echo 'TIMEOUT = 50  # qo\\047lda kelishilgan qiymat' > config.py\n"
                "git add config.py\n"
                "git commit --no-edit\n\n"
                "echo \"=== branch'ni asl konfliktli holatga qaytaramiz ===\"\n"
                "git reset --hard HEAD~1\n\n"
                "echo \"=== IKKINCHI MARTA: rerere avtomatik yechishi kerak ===\"\n"
                "git merge feature-x --no-edit 2>&1 | tail -5 || true\n"
                "cat config.py\n"
            ),
        },
    ],
}

L9_EXERCISES = [
    {
        "title": "rerere nima qiladi",
        "title_ru": "Что делает rerere",
        "description": "git rerere'ning asosiy vazifasi nima?",
        "description_ru": "Какова основная задача git rerere?",
        "exercise_type": "multiple_choice",
        "options": [
            "Oldingi konflikt yechimlarini eslab qolib, xuddi shu konflikt qayta chiqsa avtomatik qo'llash",
            "Barcha konfliktlarni avtomatik 'ours' bilan yechish",
            "Konfliktlarni butunlay oldini olish",
            "Faqat binary fayllardagi konfliktlarni yechish",
        ],
        "options_ru": [
            "Запоминать прошлые решения конфликтов и применять их автоматически при повторении того же конфликта",
            "Автоматически разрешать все конфликты через 'ours'",
            "Полностью предотвращать конфликты",
            "Разрешать конфликты только в бинарных файлах",
        ],
        "correct_answers": "A",
        "hint": "'reuse recorded resolution' — nomining o'zi javobni beradi.",
        "hint_ru": "'reuse recorded resolution' — само название даёт ответ.",
        "explanation": "rerere birinchi qo'lda yechimni eslab qoladi, keyingi bir xil konfliktlarda uni avtomatik qo'llaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Konflikt yechish ustuvorligini tartiblang",
        "title_ru": "Расположите приоритет разрешения конфликта",
        "description": "Git konflikt yuzaga kelganda avtomatik yechimlarni qanday tartibda tekshirishini joylashtiring.",
        "description_ru": "Расположите порядок, в котором Git проверяет автоматические решения при конфликте.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "rerere xotirasida shu konflikt bormi tekshirish",
            ".gitattributes'da mos merge drayveri bormi tekshirish",
            "Qo'lda yechishni talab qilish",
            "Yechimni keyingi safar uchun rerere orqali eslab qolish",
        ],
        "drag_items_ru": [
            "Проверить, есть ли этот конфликт в памяти rerere",
            "Проверить, есть ли подходящий merge driver в .gitattributes",
            "Потребовать ручное разрешение",
            "Запомнить решение через rerere для следующего раза",
        ],
        "correct_order": [
            "rerere xotirasida shu konflikt bormi tekshirish",
            ".gitattributes'da mos merge drayveri bormi tekshirish",
            "Qo'lda yechishni talab qilish",
            "Yechimni keyingi safar uchun rerere orqali eslab qolish",
        ],
        "hint": "9-dars diagrammasidagi qaror daraxtini eslang.",
        "hint_ru": "Вспомните дерево решений из диаграммы урока 9.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "-X ours va merge=ours farqi",
        "title_ru": "Разница между -X ours и merge=ours",
        "description": "`git merge -X ours` faqat ___ qatorlarida joriy tomonni tanlaydi, `merge=ours` drayveri esa BUTUN faylni o'zgarishsiz qoldiradi.",
        "description_ru": "`git merge -X ours` выбирает текущую сторону только в ___ строках, а драйвер `merge=ours` оставляет ВЕСЬ файл без изменений.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "konflikt",
        "correct_answers_ru": "конфликтующих",
        "hint": "Faqat muammoli joylarda ishlaydimi yoki butun faylda?",
        "hint_ru": "Работает только в проблемных местах или во всём файле?",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 10 — R2: Takrorlash (worktree/submodule-subtree/hooks/rerere)
# ---------------------------------------------------------------------------

L10_TEXT = """
<h3>Bu checkpoint nima uchun kerak</h3>
<p>6-9-darslarda siz kundalik ishni sezilarli yengillashtiruvchi to'rtta
vositani ko'rdingiz: <code>git worktree</code> (stash'siz parallel ish),
submodule/subtree (tashqi kodni boshqarish), git hooks (mahalliy
avtomatlashtirish vs CI kafolati), va rerere/merge drayverlari (takroriy
konfliktlarni avtomatlashtirish). Bu qism ularni BITTA jamoaviy
stsenariyda birlashtiradi.</p>

<h3>To'rtta vosita — bitta umumiy mavzu</h3>
<p>Diqqat bilan qaralsa, bu to'rt mavzuning barchasi bitta umumiy g'oyani
turli kontekstda takrorlaydi: <strong>"takroriy qo'lda ishni
avtomatlashtirish yoki mutlaqo yo'q qilish"</strong>. worktree — stash/pop
takrorini yo'q qiladi. Submodule/subtree — tashqi kodni qo'lda nusxalash
o'rniga strukturaviy yechim beradi. Hooks — sifat tekshiruvini qo'lda
eslab, qo'lda ishga tushirish o'rniga avtomatlashtiradi. rerere — bir xil
konfliktni qayta-qayta qo'lda yechish o'rniga eslab qoladi.</p>

<h3>Eng ko'p uchraydigan tushunmovchiliklar — qayta ko'rib chiqamiz</h3>
<ul>
<li>"worktree — bu branch'ning nusxasi" — YO'Q, u faqat alohida ishchi
papka va index; obyektlar bazasi to'liq ULASHILADI.</li>
<li>"submodule va subtree bir xil narsa, faqat sintaksisi farq qiladi" —
YO'Q, submodule ISHORAT saqlaydi (fayllarsiz), subtree fayllarni
HAQIQATDA asosiy tarixga birlashtiradi.</li>
<li>"pre-push hook o'rnatilgan bo'lsa, testsiz kod serverga bora
olmaydi" — YO'Q, <code>--no-verify</code> mahalliy hook'larni OSON
chetlab o'tadi; faqat CI (server tomonda) haqiqiy majburiy darvoza.</li>
<li>"merge=ours va -X ours bir xil ishlaydi" — YO'Q, birinchisi BUTUN
faylni e'tiborsiz qoldiradi, ikkinchisi faqat konflikt qatorlarida
ishlaydi.</li>
</ul>

<h3>Amaliy stsenariy: hammasini birlashtirish</h3>
<p>Real jamoada ish oqimi shunday bo'lishi mumkin: siz shoshilinch
hotfix uchun <code>git worktree add</code> bilan alohida papka ochasiz
(6-dars) → o'sha yerda loyihaning `vendor/` submodule'ini yangilaysiz
(7-dars) → commit qilishdan oldin mahalliy <code>pre-commit</code> hook
maxfiy kalitlarni tekshiradi (8-dars) → `main`ga qaytarib
birlashtirishda avval ham xuddi shu joyda konflikt chiqqan edi, lekin
<code>rerere</code> uni avtomatik yechadi (9-dars) → oxirida
<code>git push</code>dan oldin mahalliy <code>pre-push</code> testlarni
ishga tushiradi, so'ngra GitHub Actions serverda YANA tekshiradi.</p>

<h3>O'z-o'zini tekshirish savollari</h3>
<ul>
<li>Nega bitta branch bir vaqtning o'zida ikkita worktree'da checkout
qilib bo'lmaydi?</li>
<li>Yangi jamoa a'zosi <code>git clone</code> qilganda submodule papkasi
nega bo'sh chiqadi?</li>
<li>Nega faqat mahalliy hook'larga tayanib, CI'siz qolib bo'lmaydi?</li>
<li><code>git rerere</code> ikkinchi safar konfliktni ko'rganda nima
deb xabar beradi (birinchi safardagidan farqli)?</li>
</ul>

<h3>Qo'shimcha stsenariy: nega bu to'rt dars birga o'qitiladi</h3>
<p>worktree, submodule/subtree, hooks va rerere — bir qarashda mutlaqo
bog'liq bo'lmagan mavzular. Lekin ularning barchasi bitta amaliy
muammoni yechadi: <strong>takroriy, xavfli yoki chalg'ituvchi qo'lda
ishni yo'q qilish</strong>. Ular ko'pincha BITTA ish kunida birgalikda
ishlatiladi — masalan, siz worktree'da tashqi kutubxona (submodule)
ustida ishlaysiz, hook sizni xato qilishdan (maxfiy kalit commit qilish)
saqlaydi, va rerere avvalgi konfliktlarni avtomatik yechadi, shunda
diqqatingiz haqiqiy muammoga qaratiladi, takroriy ishga emas.</p>

<h3>Yana bir amaliy misol: ko'p bosqichli jamoaviy ish kuni</h3>
<p>Ertalab: <code>git worktree add ../review pr-42</code> bilan
hamkasbning PR'ini alohida papkada ko'rib chiqasiz, o'z ishingizga
tegmasdan. Tushdan keyin: asosiy papkada <code>vendor/</code>
submodule'ini yangi versiyaga ko'chirasiz, <code>git submodule
foreach</code> orqali barcha submodule'larni bir vaqtda tekshirasiz.
Commit qilishdan oldin: mahalliy <code>pre-commit</code> hook maxfiy
kalitni tutib, sizni ogohlantiradi — muammoni <code>--no-verify</code>
bilan chetlab o'tish o'rniga, uni to'g'ri hal qilasiz. Kechqurun:
<code>main</code>ga birlashtirishda ertalabki xuddi shu konflikt qayta
chiqadi, lekin <code>rerere</code> uni darhol, avtomatik yechadi — chunki
siz uni birinchi marta ertalab qo'lda yechgan edingiz.</p>
""".strip()

L10_TEXT_RU = """
<h3>Зачем нужен этот checkpoint</h3>
<p>В уроках 6-9 вы увидели четыре инструмента, заметно облегчающих
повседневную работу: <code>git worktree</code> (параллельная работа без
stash), submodule/subtree (управление внешним кодом), git hooks
(локальная автоматизация против гарантии CI), и rerere/merge drivers
(автоматизация повторяющихся конфликтов). Этот раздел объединяет их в
ОДНОМ командном сценарии.</p>

<h3>Четыре инструмента — одна общая тема</h3>
<p>При внимательном рассмотрении все эти четыре темы повторяют одну общую
идею в разном контексте: <strong>"автоматизировать или полностью убрать
повторяющуюся ручную работу"</strong>. worktree убирает повтор stash/pop.
Submodule/subtree дают структурное решение вместо ручного копирования
внешнего кода. Hooks автоматизируют проверку качества вместо запоминания
и ручного запуска. rerere запоминает решение вместо повторного ручного
разрешения одного и того же конфликта.</p>

<h3>Самые частые заблуждения — пересмотрим</h3>
<ul>
<li>"worktree — это копия ветки" — НЕТ, это только отдельная рабочая
папка и index; база объектов полностью ОБЩАЯ.</li>
<li>"submodule и subtree — одно и то же, отличается только синтаксис" —
НЕТ, submodule хранит УКАЗАТЕЛЬ (без файлов), subtree реально объединяет
файлы в основную историю.</li>
<li>"если настроен pre-push hook, код без тестов не попадёт на сервер" —
НЕТ, <code>--no-verify</code> ЛЕГКО обходит локальные hook; только CI (на
сервере) — настоящие обязательные ворота.</li>
<li>"merge=ours и -X ours работают одинаково" — НЕТ, первый игнорирует
ВЕСЬ файл, второй работает только в конфликтующих строках.</li>
</ul>

<h3>Практический сценарий: объединяем всё</h3>
<p>В реальной команде рабочий процесс может выглядеть так: вы открываете
отдельную папку через <code>git worktree add</code> для срочного hotfix
(урок 6) → там обновляете submodule `vendor/` проекта (урок 7) → перед
коммитом локальный hook <code>pre-commit</code> проверяет секретные
ключи (урок 8) → при объединении обратно в `main` раньше в этом же месте
уже был конфликт, но <code>rerere</code> разрешает его автоматически
(урок 9) → в конце перед <code>git push</code> локальный
<code>pre-push</code> запускает тесты, затем GitHub Actions ЕЩЁ РАЗ
проверяет на сервере.</p>

<h3>Вопросы для самопроверки</h3>
<ul>
<li>Почему одну ветку нельзя checkout'нуть одновременно в двух
worktree?</li>
<li>Почему папка submodule пуста, когда новый член команды делает
<code>git clone</code>?</li>
<li>Почему нельзя полагаться только на локальные hook без CI?</li>
<li>Что сообщает <code>git rerere</code>, увидев конфликт второй раз (в
отличие от первого)?</li>
</ul>

<h3>Дополнительный сценарий: почему эти четыре урока изучаются вместе</h3>
<p>worktree, submodule/subtree, hooks и rerere — на первый взгляд
совершенно не связанные темы. Но все они решают одну практическую
проблему: <strong>устранение повторяющейся, опасной или отвлекающей
ручной работы</strong>. Часто они используются ВМЕСТЕ в течение ОДНОГО
рабочего дня — например, вы работаете над внешней библиотекой
(submodule) в worktree, hook защищает вас от ошибки (коммит секретного
ключа), а rerere автоматически разрешает прежние конфликты, позволяя
сосредоточиться на реальной проблеме, а не на повторяющейся работе.</p>

<h3>Ещё один практический пример: многоэтапный командный рабочий день</h3>
<p>Утром: через <code>git worktree add ../review pr-42</code> вы
просматриваете PR коллеги в отдельной папке, не трогая свою работу.
После обеда: в основной папке обновляете submodule <code>vendor/</code>
до новой версии, проверяете все submodule одновременно через <code>git
submodule foreach</code>. Перед коммитом: локальный <code>pre-commit</code>
hook ловит секретный ключ и предупреждает вас — вместо обхода через
<code>--no-verify</code>, вы правильно решаете проблему. Вечером: при
merge в <code>main</code> утренний конфликт возникает снова, но
<code>rerere</code> разрешает его сразу, автоматически — потому что вы
уже разрешили его вручную утром в первый раз.</p>

<h3>Итог: от повторяющейся работы к системе</h3>
<p>Четыре инструмента этого блока превращают то, что раньше было ручной,
подверженной ошибкам рутиной, в предсказуемую, воспроизводимую систему:
worktree убирает риск потери незакоммиченной работы, submodule/subtree
делают версию внешнего кода явной и отслеживаемой, hooks переносят
проверку качества на самый ранний возможный момент, а rerere превращает
"я уже это решал" в автоматическое действие, а не повторный ручной труд.</p>
""".strip()

L10_CODE = """
# ============================================================
# Yakuniy amaliyot: to'rt mavzuni bitta jamoaviy stsenariyda
# ============================================================

# 1) Shoshilinch hotfix uchun worktree (6-dars)
$ git worktree add ../hotfix main
$ cd ../hotfix
$ git switch -c hotfix/vendor-update

# 2) vendor/ submodule'ini yangilash (7-dars)
$ cd vendor/ui-kit
$ git pull origin main
$ cd ../..
$ git add vendor/ui-kit
$ git commit -m "vendor/ui-kit yangilandi"

# 3) pre-commit hook maxfiy kalitni tekshiradi (8-dars)
$ git commit -am "config.py yangilandi"
XATO: staged o'zgarishlarda maxfiy kalit topildi!
$ vim config.py   # kalitni .env'ga ko'chiramiz
$ git commit -am "config.py yangilandi (kalit .env'ga ko'chirildi)"
[hotfix/vendor-update abc123] config.py yangilandi

# 4) main'ga birlashtirishda avvalgi konflikt qayta chiqadi, rerere yechadi (9-dars)
$ git switch main
$ git merge hotfix/vendor-update
Auto-merging config.py
Resolved 'config.py' using previous resolution.
Auto-merging vendor/ui-kit
Merge made by the 'ort' strategy.

# 5) Push'dan oldin mahalliy test, keyin server tekshiruvi
$ git push origin main
pre-push: backend testlari (test.yml kabi)...
3 passed
# ... push davom etadi, GitHub serverida .github/workflows/test.yml
# QAYTA, mustaqil ravishda ishga tushadi — bu ikkinchi, majburiy qatlam.

# 6) Tozalash
$ git worktree remove ../hotfix

# ============================================================
# O'z-o'zini tekshirish: interaktiv jadval
# ============================================================
# | Savol                                      | Javob qayerda?     |
# |----------------------------------------------|---------------------|
# | worktree nima saqlaydi, nima ulashadi?       | 6-dars              |
# | submodule vs subtree fayl saqlash farqi?     | 7-dars              |
# | --no-verify nima uchun xavfli?               | 8-dars              |
# | rerere ikkinchi safar nima deydi?            | 9-dars              |

# ============================================================
# Qo'shimcha tekshiruv: worktree + submodule + hook birgalikda
# ============================================================
$ git worktree list --porcelain | head -6
worktree /home/user/repo
HEAD 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
branch refs/heads/main

worktree /home/user/hotfix
HEAD a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9

$ cd ../hotfix
$ git submodule foreach 'git log -1 --oneline'
Entering 'vendor/ui-kit'
9a8b7c1 v2.2.0 relizi

$ git config core.hooksPath scripts/git-hooks
$ git commit -am "config.py yangilandi"
# pre-commit hook ishga tushadi, tekshiradi, muammo bo'lmasa o'tkazadi

$ cd ../repo
$ git merge hotfix/vendor-update
Resolved 'config.py' using previous resolution.
$ git rerere status
# (bo'sh — barcha konfliktlar allaqachon yechilgan)

$ git submodule foreach 'git status --short'
Entering 'vendor/ui-kit'
Entering 'vendor/charts'
# (bo'sh ikkalasida ham — ikkala submodule ham toza, saqlanmagan
# o'zgarishlarsiz)

$ git worktree list
/home/user/repo      3f2e1d0 [main]
/home/user/hotfix     a8b7c6d [hotfix/vendor-update]
$ git worktree remove ../hotfix
# Ish kuni tugadi: worktree yopildi, submodule yangilandi, hook ishladi,
# rerere konfliktni avtomatik yechdi — to'rtta vosita, bitta izchil ish
# oqimida.
""".strip()

L10_CODE_RU = """
# ============================================================
# Итоговая практика: четыре темы в одном командном сценарии
# ============================================================

# 1) worktree для срочного hotfix (урок 6)
$ git worktree add ../hotfix main
$ cd ../hotfix
$ git switch -c hotfix/vendor-update

# 2) Обновление submodule vendor/ (урок 7)
$ cd vendor/ui-kit
$ git pull origin main
$ cd ../..
$ git add vendor/ui-kit
$ git commit -m "обновлён vendor/ui-kit"

# 3) pre-commit hook проверяет секретный ключ (урок 8)
$ git commit -am "обновлён config.py"
ОШИБКА: в staged-изменениях найден секретный ключ!
$ vim config.py   # переносим ключ в .env
$ git commit -am "обновлён config.py (ключ перенесён в .env)"
[hotfix/vendor-update abc123] обновлён config.py

# 4) При merge в main прежний конфликт возникает снова, rerere разрешает (урок 9)
$ git switch main
$ git merge hotfix/vendor-update
Auto-merging config.py
Resolved 'config.py' using previous resolution.
Auto-merging vendor/ui-kit
Merge made by the 'ort' strategy.

# 5) Локальный тест перед push, затем проверка на сервере
$ git push origin main
pre-push: backend testlari (test.yml kabi)...
3 passed
# ... push продолжается, на сервере GitHub .github/workflows/test.yml
# ЗАПУСКАЕТСЯ СНОВА, независимо — это второй, обязательный уровень.

# 6) Очистка
$ git worktree remove ../hotfix

# ============================================================
# Самопроверка: интерактивная таблица
# ============================================================
# | Вопрос                                        | Где ответ?         |
# |--------------------------------------------------|----------------------|
# | Что хранит worktree, что общее?                  | Урок 6               |
# | Разница submodule и subtree в хранении файлов?   | Урок 7               |
# | Почему --no-verify опасен?                       | Урок 8               |
# | Что говорит rerere во второй раз?                | Урок 9               |

# ============================================================
# Дополнительная проверка: worktree + submodule + hook вместе
# ============================================================
$ git worktree list --porcelain | head -6
worktree /home/user/repo
HEAD 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
branch refs/heads/main

worktree /home/user/hotfix
HEAD a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9

$ cd ../hotfix
$ git submodule foreach 'git log -1 --oneline'
Entering 'vendor/ui-kit'
9a8b7c1 релиз v2.2.0

$ git config core.hooksPath scripts/git-hooks
$ git commit -am "обновлён config.py"
# pre-commit hook срабатывает, проверяет, если проблем нет — пропускает

$ cd ../repo
$ git merge hotfix/vendor-update
Resolved 'config.py' using previous resolution.
$ git rerere status
# (пусто — все конфликты уже разрешены)

# ============================================================
# Дополнительная проверка: worktree + submodule + hook вместе
# ============================================================
$ git worktree list --porcelain | head -6
worktree /home/user/repo
HEAD 3f2e1d0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e
branch refs/heads/main

worktree /home/user/hotfix
HEAD a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9

$ cd ../hotfix
$ git submodule foreach 'git log -1 --oneline'
Entering 'vendor/ui-kit'
9a8b7c1 релиз v2.2.0

$ git config core.hooksPath scripts/git-hooks
$ git commit -am "обновлён config.py"
# pre-commit hook срабатывает, проверяет, если проблем нет — пропускает

$ cd ../repo
$ git merge hotfix/vendor-update
Resolved 'config.py' using previous resolution.
$ git rerere status
# (пусто — все конфликты уже разрешены)

# ============================================================
# Дополнительная сверка: submodule foreach на нескольких модулях
# ============================================================
$ git submodule foreach 'git status --short'
Entering 'vendor/ui-kit'
Entering 'vendor/charts'
# (пусто у обоих — оба submodule чистые, без несохранённых изменений)

$ git worktree list
/home/user/repo      3f2e1d0 [main]
/home/user/hotfix     a8b7c6d [hotfix/vendor-update]
$ git worktree remove ../hotfix
# Рабочий день завершён: worktree закрыт, submodule обновлён, hook
# отработал, rerere разрешил конфликт автоматически.
""".strip()

L10_TASK = {
    "task_title": "R2 capstone-mini: worktree -> submodule -> hook -> rerere",
    "task_title_ru": "R2 мини-капстоун: worktree -> submodule -> hook -> rerere",
    "task_description": (
        "To'liq jamoaviy stsenariyni takrorlang: (1) `git worktree add` "
        "bilan alohida hotfix papkasi oching, (2) unda submodule'ni "
        "yangilang (yoki simulyatsiya qiling), (3) mahalliy pre-commit "
        "hook orqali maxfiy kalitni tutib, tuzating, (4) `main`ga "
        "birlashtirishda avvaldan yozib qo'yilgan rerere yechimi "
        "avtomatik ishlashini ko'rsating."
    ),
    "task_description_ru": (
        "Повторите полный командный сценарий: (1) откройте отдельную "
        "папку hotfix через `git worktree add`, (2) обновите в ней "
        "submodule (или симулируйте), (3) через локальный pre-commit "
        "hook поймайте и исправьте секретный ключ, (4) при merge в "
        "`main` покажите, что заранее записанное решение rerere "
        "срабатывает автоматически."
    ),
    "task_requirements": (
        "1) Har bir bosqichning buyruq+natija juftligi hisobotda "
        "bo'lishi shart (4 bosqich). 2) pre-commit hook maxfiy kalitni "
        "TUTGANINI ko'rsatuvchi xato xabari bo'lishi kerak. 3) rerere'ning "
        "'Resolved ... using previous resolution' xabari bo'lishi "
        "kerak."
    ),
    "task_requirements_ru": (
        "1) В отчёте должна быть пара команда+результат для каждого из "
        "4 шагов. 2) Должно быть сообщение об ошибке, показывающее, что "
        "pre-commit hook ПОЙМАЛ секретный ключ. 3) Должно быть сообщение "
        "rerere 'Resolved ... using previous resolution'."
    ),
    "task_technologies": "Git (worktree, submodule, hooks, rerere)",
    "task_deadline_days": 5,
}

L10_SAMPLE = {
    "title": "Namuna: R2 to'liq jamoaviy zanjir skripti",
    "description": (
        "Bitta bash skripti to'rt darsning g'oyalarini ketma-ket "
        "bajaradi: worktree ochish, submodule yangilash, pre-commit "
        "hook orqali maxfiy kalitni tutish, va rerere orqali takroriy "
        "konfliktni avtomatik yechish."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "r2_full_chain.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf r2demo r2demo-hotfix && mkdir r2demo && cd r2demo && git init -q\n"
                "git config rerere.enabled true\n\n"
                "cat > .git/hooks/pre-commit << 'EOF'\n"
                "#!/bin/bash\n"
                "if git diff --cached | grep -qE \"SECRET_KEY\\s*=\\s*['\\\"]\"; then\n"
                "    echo \"XATO: maxfiy kalit topildi!\"\n"
                "    exit 1\n"
                "fi\n"
                "EOF\n"
                "chmod +x .git/hooks/pre-commit\n\n"
                "echo 'TIMEOUT = 30' > config.py\n"
                "git add . && git commit -q -m \"c0\"\n\n"
                "echo \"== 1) WORKTREE ==\"\n"
                "git worktree add -q ../r2demo-hotfix -b hotfix/vendor-update\n"
                "cd ../r2demo-hotfix\n\n"
                "echo \"== 3) PRE-COMMIT HOOK MAXFIY KALITNI TUTADI ==\"\n"
                "echo 'SECRET_KEY = \"oops\"' >> config.py\n"
                "git add . && (git commit -m \"config yangilandi\" || echo \"(kutilganidek to'xtatildi)\")\n"
                "git checkout -- config.py\n"
                "echo 'TIMEOUT = 60' > config.py\n"
                "git commit -qam \"timeout oshirildi\"\n\n"
                "cd ../r2demo\n"
                "echo 'TIMEOUT = 45' > config.py\n"
                "git commit -qam \"main: timeout boshqacha\"\n\n"
                "echo \"== BIRINCHI merge (qo'lda yechamiz) ==\"\n"
                "git merge hotfix/vendor-update --no-edit 2>&1 | tail -3 || true\n"
                "echo 'TIMEOUT = 50' > config.py && git add config.py && git commit --no-edit\n\n"
                "git reset --hard HEAD~1\n"
                "echo \"== IKKINCHI marta: rerere avtomatik yechadi ==\"\n"
                "git merge hotfix/vendor-update --no-edit 2>&1 | tail -5 || true\n\n"
                "git worktree remove ../r2demo-hotfix --force\n"
            ),
        },
    ],
}

L10_EXERCISES = [
    {
        "title": "R2: worktree va obyektlar bazasi",
        "title_ru": "R2: worktree и база объектов",
        "description": "Ikkita worktree orasida NIMA ulashiladi, NIMA alohida?",
        "description_ru": "Что ОБЩЕЕ между двумя worktree, а что ОТДЕЛЬНОЕ?",
        "exercise_type": "multiple_choice",
        "options": [
            "Obyektlar bazasi va refs ulashiladi; ishchi fayllar va index alohida",
            "Hammasi to'liq ulashiladi, hech qanday farq yo'q",
            "Hammasi alohida, hech narsa ulashilmaydi",
            "Faqat .gitignore ulashiladi",
        ],
        "options_ru": [
            "База объектов и refs общие; рабочие файлы и index отдельные",
            "Всё полностью общее, разницы нет",
            "Всё отдельное, ничего не разделяется",
            "Общий только .gitignore",
        ],
        "correct_answers": "A",
        "hint": "6-darsdagi diagrammani eslang.",
        "hint_ru": "Вспомните диаграмму из урока 6.",
        "explanation": "Obyektlar bazasi va refs ulashiladi, faqat ishchi papka va index har bir worktree uchun alohida.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "R2: jamoaviy stsenariyni tartiblang",
        "title_ru": "R2: расположите командный сценарий",
        "description": "Hotfix'dan main'ga qadar bo'lgan to'g'ri ketma-ketlikni joylashtiring.",
        "description_ru": "Расположите правильную последовательность от hotfix до main.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git worktree add bilan alohida papka ochish",
            "Submodule'ni yangilash",
            "pre-commit hook maxfiy kalitni tekshirishi",
            "main'ga merge qilishda rerere avtomatik yechishi",
        ],
        "drag_items_ru": [
            "Открыть отдельную папку через git worktree add",
            "Обновить submodule",
            "pre-commit hook проверяет секретный ключ",
            "rerere автоматически разрешает при merge в main",
        ],
        "correct_order": [
            "git worktree add bilan alohida papka ochish",
            "Submodule'ni yangilash",
            "pre-commit hook maxfiy kalitni tekshirishi",
            "main'ga merge qilishda rerere avtomatik yechishi",
        ],
        "hint": "6-7-8-9-darslar tartibi aynan shu ish oqimiga mos keladi.",
        "hint_ru": "Порядок уроков 6-7-8-9 точно соответствует этому процессу.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "R2: nega ikkala qatlam ham kerak",
        "title_ru": "R2: почему нужны оба уровня",
        "description": "Mahalliy pre-push hook va GitHub Actions CI'ning ikkalasi ham nega kerak, faqat bittasi yetarli emas?",
        "description_ru": "Почему нужны и локальный pre-push hook, и GitHub Actions CI — почему одного недостаточно?",
        "exercise_type": "text_input",
        "expected_answer": "Mahalliy hook tezkor fikr-mulohaza beradi, lekin --no-verify bilan chetlab o'tiladi; CI esa serverda ishlaydi va uni hech kim chetlab o'ta olmaydi, shuning uchun haqiqiy majburiy tekshiruv faqat CI'da.",
        "hint": "8-darsdagi diagrammani eslang.",
        "hint_ru": "Вспомните диаграмму из урока 8.",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 11 — Monorepo asoslari: sparse-checkout va partial clone
# ---------------------------------------------------------------------------

L11_TEXT = """
<h3>Muammo: katta monorepo bilan ishlash</h3>
<p>Ushbu platformaning o'zi — <strong>monorepo</strong>: bitta Git
repo'sida <code>backend/</code>, <code>frontend/</code>, <code>docs/</code>
va ildiz darajasidagi <code>alembic/</code> birga yashaydi. Frontend
dasturchisiga odatda <code>backend/venv/</code>, <code>node_modules/</code>
tarixi yoki <code>alembic/versions/</code>dagi yuzlab eski migratsiya
fayli kerak emas — lekin oddiy <code>git clone</code> BARCHA fayllarning
BARCHA tarixini yuklaydi. Katta monorepo'larda (ayniqsa yuzlab
megabayt/gigabayt binary fayllar bilan) bu daqiqalab davom etishi
mumkin.</p>

<h3>sparse-checkout: faqat kerakli papkalarni ishchi katalogda ko'rish</h3>
<p><code>git sparse-checkout</code> obyektlar bazasini QISQARTIRMAYDI —
u faqat ISHCHI KATALOGDA qaysi papkalar CHIQARILISHINI (checkout)
boshqaradi. <code>--cone</code> rejimi (tavsiya etiladi) papka darajasida
ishlaydi: <code>git sparse-checkout set backend frontend</code> desangiz,
<code>docs/</code> va ildizdagi <code>alembic/</code> DISKKA yozilmaydi,
lekin ular hali ham obyektlar bazasida (<code>.git/objects/</code>) mavjud
— xohlagan vaqtda <code>git sparse-checkout add docs</code> bilan qaytarib
qo'shish mumkin, qayta yuklab olishga hojat yo'q.</p>

<h3>partial clone: obyektlar bazasining o'zini ham qisqartirish</h3>
<p>sparse-checkout ISHCHI katalogni qisqartirsa, <code>--filter</code>
bilan <code>partial clone</code> OBYEKTLAR BAZASINI qisqartiradi:
<code>git clone --filter=blob:none &lt;url&gt;</code> — bu BARCHA
commit va tree obyektlarini yuklaydi (tarix to'liq ko'rinadi), lekin
BLOB'larni (fayl kontenti) FAQAT ular haqiqatda kerak bo'lganda (masalan
<code>git checkout</code> yoki <code>git show</code> paytida) serverdan
"lazy" ravishda yuklaydi. Bu ikkalasi (sparse-checkout + partial clone)
BIRGA ishlatilganda eng katta samarani beradi: faqat kerakli papkalar
checkout qilinadi VA faqat o'sha papkalar uchun blob'lar yuklanadi.</p>

<h3>Ushbu repo tuzilishida amaliy misol</h3>
<pre class="mermaid">
flowchart TB
  R["Repo ildizi (monorepo)"] --> BE["backend/
(Python, FastAPI)"]
  R --> FE["frontend/
(React)"]
  R --> DOCS["docs/
(hujjatlar)"]
  R --> ALEMBIC["alembic/
(ildiz darajasidagi migratsiyalar)"]
  BE -.->|"sparse-checkout: KIRITILADI"| CO1["Frontend dasturchisi uchun
checkout'da YO'Q"]
  FE -.->|"sparse-checkout: KIRITILADI"| CO2["Frontend dasturchisi uchun
checkout'da BOR"]
  DOCS -.->|"sparse-checkout: chiqarib tashlanadi"| CO3["Diskka yozilmaydi,
lekin .git/objects'da mavjud"]
  style FE fill:#d6e9ff,stroke:#2266aa
  style DOCS fill:#ffe9b3,stroke:#d09000
</pre>
<p>Diagramma shu repo'ning haqiqiy tuzilishini ko'rsatadi: frontend
dasturchisi <code>git sparse-checkout set frontend</code> bilan faqat
<code>frontend/</code>ni ishchi katalogda ko'radi, <code>backend/</code>
va <code>docs/</code> diskda YO'Q — lekin ular hali ham obyektlar
bazasida, kerak bo'lsa qaytarib qo'shiladi.</p>

<h3>Cone mode vs non-cone mode</h3>
<p><code>--cone</code> rejimi (Git 2.25+ tavsiyasi) faqat to'liq papka
yo'llarini qabul qiladi va ICHKI ravishda ancha tezroq ishlaydi
(katalog darajasida filtrlaydi). Eski, cone bo'lmagan rejim
<code>.gitignore</code>ga o'xshash naqshlarni (<code>*.py</code>,
<code>!important.py</code>) qo'llab-quvvatlaydi, lekin sekinroq va
xatoga moyilroq. Yangi loyihalarda deyarli har doim
<code>--cone</code> tanlanadi.</p>

<h3>Amaliy foyda: klonlash vaqti</h3>
<p>Katta monorepo'da (masalan minglab commit, ko'p binary asset)
<code>git clone --filter=blob:none --sparse</code> keyin <code>git
sparse-checkout set backend</code> — to'liq clone'ga nisbatan sezilarli
tezroq va kamroq disk joyi ishlatadi, chunki faqat kerakli qism uchun
blob so'raladi.</p>

<h3>Shallow clone vs partial clone — muhim farq</h3>
<p>Ikkalasi ham "kichikroq clone" bergani uchun ko'pincha chalkashtiriladi,
lekin ular MUTLAQO boshqa o'lchamda cheklaydi: <strong>shallow clone</strong>
(<code>git clone --depth=1</code>) TARIX CHUQURLIGINI cheklaydi — faqat
oxirgi N commit yuklanadi, ESKI commit'lar UMUMAN mavjud emas (hatto
so'ralganda ham serverdan olib bo'lmaydi, agar server buni qo'llab-
quvvatlamasa). <strong>partial clone</strong> (<code>--filter</code>)
esa TARIXNI TO'LIQ saqlaydi (barcha commit/tree), faqat BLOB kontentini
kechiktiradi. Boshqacha aytganda: shallow — "tarixni qisqartirish",
partial — "kontentni kechiktirish". Ba'zi ishlar (masalan <code>git
blame</code>, <code>git log</code> to'liq tarix) shallow clone'da
ishlamasligi mumkin, lekin partial clone'da to'liq ishlaydi.</p>
""".strip()

L11_TEXT_RU = """
<h3>Проблема: работа с большим monorepo</h3>
<p>Сама эта платформа — <strong>monorepo</strong>: в одном
Git-репозитории живут вместе <code>backend/</code>, <code>frontend/</code>,
<code>docs/</code> и <code>alembic/</code> корневого уровня. Frontend-
разработчику обычно не нужны <code>backend/venv/</code>, история
<code>node_modules/</code> или сотни старых файлов миграций в
<code>alembic/versions/</code> — но обычный <code>git clone</code>
загружает ВСЮ историю ВСЕХ файлов. В больших monorepo (особенно с
сотнями мегабайт/гигабайтами бинарных файлов) это может занимать
минуты.</p>

<h3>sparse-checkout: видеть в рабочем каталоге только нужные папки</h3>
<p><code>git sparse-checkout</code> НЕ УМЕНЬШАЕТ базу объектов — он
только управляет тем, какие папки ВЫВОДЯТСЯ (checkout) в РАБОЧИЙ
КАТАЛОГ. Режим <code>--cone</code> (рекомендуется) работает на уровне
папок: если сказать <code>git sparse-checkout set backend
frontend</code>, <code>docs/</code> и корневой <code>alembic/</code> НЕ
БУДУТ записаны на диск, но они всё ещё есть в базе объектов
(<code>.git/objects/</code>) — в любой момент можно вернуть их через
<code>git sparse-checkout add docs</code>, без повторной загрузки.</p>

<h3>partial clone: уменьшение самой базы объектов</h3>
<p>Если sparse-checkout уменьшает РАБОЧИЙ каталог, то <code>partial
clone</code> с <code>--filter</code> уменьшает САМУ БАЗУ ОБЪЕКТОВ:
<code>git clone --filter=blob:none &lt;url&gt;</code> — загружает ВСЕ
объекты commit и tree (история видна полностью), но BLOB (содержимое
файлов) загружает с сервера "лениво" ТОЛЬКО когда они реально нужны
(например, при <code>git checkout</code> или <code>git show</code>).
Наибольший эффект даёт СОВМЕСТНОЕ использование (sparse-checkout +
partial clone): checkout только нужных папок И загрузка blob только для
этих папок.</p>

<h3>Практический пример на структуре этого репозитория</h3>
<pre class="mermaid">
flowchart TB
  R["Корень репозитория (monorepo)"] --> BE["backend/
(Python, FastAPI)"]
  R --> FE["frontend/
(React)"]
  R --> DOCS["docs/
(документация)"]
  R --> ALEMBIC["alembic/
(миграции корневого уровня)"]
  BE -.->|"sparse-checkout: ВКЛЮЧЕНО"| CO1["У frontend-разработчика
НЕТ в checkout"]
  FE -.->|"sparse-checkout: ВКЛЮЧЕНО"| CO2["У frontend-разработчика
ЕСТЬ в checkout"]
  DOCS -.->|"sparse-checkout: исключено"| CO3["Не записано на диск,
но есть в .git/objects"]
  style FE fill:#d6e9ff,stroke:#2266aa
  style DOCS fill:#ffe9b3,stroke:#d09000
</pre>
<p>Диаграмма показывает реальную структуру этого репозитория: через
<code>git sparse-checkout set frontend</code> frontend-разработчик видит
в рабочем каталоге только <code>frontend/</code>, <code>backend/</code>
и <code>docs/</code> НЕТ на диске — но они всё ещё в базе объектов, при
необходимости легко добавляются обратно.</p>

<h3>Cone mode против non-cone mode</h3>
<p>Режим <code>--cone</code> (рекомендация Git 2.25+) принимает только
полные пути к папкам и работает значительно быстрее ВНУТРЕННЕ (фильтрует
на уровне каталогов). Старый, не-cone режим поддерживает шаблоны, похожие
на <code>.gitignore</code> (<code>*.py</code>, <code>!important.py</code>),
но медленнее и более подвержен ошибкам. В новых проектах почти всегда
выбирают <code>--cone</code>.</p>

<h3>Практическая польза: время клонирования</h3>
<p>В большом monorepo (например, тысячи коммитов, много бинарных assets)
<code>git clone --filter=blob:none --sparse</code>, затем <code>git
sparse-checkout set backend</code> — заметно быстрее полного clone и
использует меньше места на диске, поскольку blob запрашиваются только
для нужной части.</p>

<h3>Shallow clone против partial clone — важная разница</h3>
<p>Оба дают "клон поменьше", поэтому их часто путают, но они ограничивают
СОВЕРШЕННО разные измерения: <strong>shallow clone</strong> (<code>git
clone --depth=1</code>) ограничивает ГЛУБИНУ ИСТОРИИ — загружаются
только последние N коммитов, СТАРЫЕ коммиты ВООБЩЕ не существуют (даже
при запросе их нельзя получить с сервера, если сервер это не
поддерживает). <strong>partial clone</strong> (<code>--filter</code>)
же СОХРАНЯЕТ ИСТОРИЮ ПОЛНОСТЬЮ (все commit/tree), только откладывает
содержимое BLOB. Другими словами: shallow — "сокращение истории",
partial — "отложенное содержимое". Некоторые операции (например
<code>git blame</code>, полный <code>git log</code>) могут не работать
в shallow clone, но полностью работают в partial clone.</p>
""".strip()

L11_CODE = """
# ============================================================
# 1) Bu platformaning haqiqiy monorepo tuzilishi
# ============================================================
$ ls
alembic/  alembic.ini  backend/  docs/  frontend/  .github/
$ du -sh */
340M    backend/
180M    frontend/
2.1M    docs/
8.4M    alembic/

# ============================================================
# 2) Partial clone — faqat commit/tree, blob'lar keyinroq
# ============================================================
$ git clone --filter=blob:none --sparse \\
    https://github.com/team/student_platform.git thin-clone
Cloning into 'thin-clone'...
remote: Enumerating objects: 15234, done.
remote: Total 15234 (delta 8821), reused 15100 (delta 8750)
Receiving objects: 100% (15234/15234), 12.4 MiB | ...
# Diqqat: 12.4 MiB — TO'LIQ clone bo'lsa 500+ MiB bo'lardi.
# Commit/tree tarixi TO'LIQ, lekin fayl kontenti (blob) hali yuklanmagan.

$ cd thin-clone
$ ls
# (bo'sh yoki minimal — sparse hali sozlanmagan)

# ============================================================
# 3) sparse-checkout: faqat kerakli papkalarni tanlash
# ============================================================
$ git sparse-checkout init --cone
$ git sparse-checkout set backend frontend
$ ls
backend/  frontend/
# docs/ va alembic/ diskda YO'Q, lekin hali obyektlar bazasida mavjud.

$ du -sh .git
45M .git
# To'liq clone'dagi bir necha yuz MB'ga solishtiring.

# ============================================================
# 4) Blob'lar "lazy" ravishda yuklanishi
# ============================================================
$ cat backend/app/models/course.py
remote: Enumerating objects: 3, done.
Receiving objects: 100% (3/3), 2.1 KiB | 850 KiB/s, done.
class Course(Base):
    __tablename__ = "courses"
    ...
# Fayl birinchi marta o'qilganda Git uni serverdan "on-demand" yuklab
# oldi — bu paytgacha faqat SHA-1 ma'lum edi, kontent yo'q edi.

# ============================================================
# 5) Kerak bo'lganda docs/ ni qaytarib qo'shish
# ============================================================
$ git sparse-checkout add docs
$ ls
backend/  docs/  frontend/
# Qayta klonlash SHART EMAS — docs/ obyektlari allaqachon .git/objects
# ichida bor edi (chunki partial clone faqat BLOB'larni kechiktirgan
# edi, tree'larni emas).

# ============================================================
# 6) Cone mode qanday sozlanganini tekshirish
# ============================================================
$ cat .git/info/sparse-checkout
/*
!/*/
/backend/
/docs/
/frontend/
$ git config core.sparseCheckoutCone
true

# ============================================================
# 7) To'liq clone bilan solishtirish jadvali
# ============================================================
# | Usul                                          | Vaqt | Hajm  |
# |------------------------------------------------|------|-------|
# | git clone (to'liq)                             | 45s  | 520MB |
# | --filter=blob:none --sparse + backend/frontend | 6s   | 45MB  |

# ============================================================
# 8) Shallow clone — tarix chuqurligini cheklash
# ============================================================
$ git clone --depth=1 https://github.com/team/student_platform.git shallow-clone
Cloning into 'shallow-clone'...
remote: Total 234 (delta 12)
Receiving objects: 100% (234/234), 8.2 MiB | ...

$ cd shallow-clone
$ git log --oneline
a1b2c3d (HEAD -> main) oxirgi commit
# ATIGI BITTA commit — qolgan tarix UMUMAN yuklanmagan.

$ git log --oneline HEAD~5
fatal: ambiguous argument 'HEAD~5': unknown revision
# Eski commit'larga umuman kira olmaymiz — bu partial clone'dan farq
# qiladi, u yerda tarix TO'LIQ, faqat blob kechiktiriladi.

# ============================================================
# 9) Shallow'ni keyinroq to'liq tarixga aylantirish
# ============================================================
$ git fetch --unshallow
remote: Enumerating objects: 15234, done.
Receiving objects: 100% (15000/15000), 480 MiB | ...
$ git log --oneline | wc -l
15234
# Endi to'liq tarix mavjud — lekin bu katta, sekin operatsiya (butun
# tarixni bir zumda yuklaydi).

# ============================================================
# 10) Qaysi birini tanlash — jadval
# ============================================================
# | Ehtiyoj                                    | Yechim          |
# |-----------------------------------------------|-------------------|
# | CI'da faqat oxirgi kodni build qilish          | shallow clone     |
# | Faqat backend/ bilan ishlash, TO'LIQ tarix     | partial+sparse    |
# | git blame/log to'liq tarix kerak               | partial clone     |
# | Disk joyi eng muhim, tarix umuman kerak emas   | shallow clone     |
""".strip()

L11_CODE_RU = """
# ============================================================
# 1) Реальная структура monorepo этой платформы
# ============================================================
$ ls
alembic/  alembic.ini  backend/  docs/  frontend/  .github/
$ du -sh */
340M    backend/
180M    frontend/
2.1M    docs/
8.4M    alembic/

# ============================================================
# 2) Partial clone — только commit/tree, blob позже
# ============================================================
$ git clone --filter=blob:none --sparse \\
    https://github.com/team/student_platform.git thin-clone
Cloning into 'thin-clone'...
remote: Enumerating objects: 15234, done.
remote: Total 15234 (delta 8821), reused 15100 (delta 8750)
Receiving objects: 100% (15234/15234), 12.4 MiB | ...
# Внимание: 12.4 МиБ — при ПОЛНОМ clone было бы 500+ МиБ.
# История commit/tree ПОЛНАЯ, но содержимое файлов (blob) ещё не загружено.

$ cd thin-clone
$ ls
# (пусто или минимально — sparse ещё не настроен)

# ============================================================
# 3) sparse-checkout: выбор только нужных папок
# ============================================================
$ git sparse-checkout init --cone
$ git sparse-checkout set backend frontend
$ ls
backend/  frontend/
# docs/ и alembic/ НЕТ на диске, но они всё ещё есть в базе объектов.

$ du -sh .git
45M .git
# Сравните с несколькими сотнями МБ при полном clone.

# ============================================================
# 4) "Ленивая" загрузка blob
# ============================================================
$ cat backend/app/models/course.py
remote: Enumerating objects: 3, done.
Receiving objects: 100% (3/3), 2.1 KiB | 850 KiB/s, done.
class Course(Base):
    __tablename__ = "courses"
    ...
# При первом чтении файла Git загрузил его с сервера "по требованию" —
# до этого был известен только SHA-1, содержимого не было.

# ============================================================
# 5) Возврат docs/ обратно при необходимости
# ============================================================
$ git sparse-checkout add docs
$ ls
backend/  docs/  frontend/
# Повторное клонирование НЕ НУЖНО — объекты docs/ уже были в
# .git/objects (потому что partial clone откладывал только BLOB, а не tree).

# ============================================================
# 6) Проверка настройки cone mode
# ============================================================
$ cat .git/info/sparse-checkout
/*
!/*/
/backend/
/docs/
/frontend/
$ git config core.sparseCheckoutCone
true

# ============================================================
# 7) Таблица сравнения с полным clone
# ============================================================
# | Способ                                          | Время | Размер |
# |----------------------------------------------------|-------|--------|
# | git clone (полный)                                 | 45с   | 520МБ  |
# | --filter=blob:none --sparse + backend/frontend     | 6с    | 45МБ   |

# ============================================================
# 8) Shallow clone — ограничение глубины истории
# ============================================================
$ git clone --depth=1 https://github.com/team/student_platform.git shallow-clone
Cloning into 'shallow-clone'...
remote: Total 234 (delta 12)
Receiving objects: 100% (234/234), 8.2 MiB | ...

$ cd shallow-clone
$ git log --oneline
a1b2c3d (HEAD -> main) последний коммит
# ТОЛЬКО ОДИН коммит — остальная история ВООБЩЕ не загружена.

$ git log --oneline HEAD~5
fatal: ambiguous argument 'HEAD~5': unknown revision
# К старым коммитам вообще нет доступа — это отличается от partial
# clone, где история ПОЛНАЯ, откладываются только blob.

# ============================================================
# 9) Превращение shallow в полную историю позже
# ============================================================
$ git fetch --unshallow
remote: Enumerating objects: 15234, done.
Receiving objects: 100% (15000/15000), 480 MiB | ...
$ git log --oneline | wc -l
15234
# Теперь полная история доступна — но это большая, медленная операция
# (загружает всю историю разом).

# ============================================================
# 10) Что выбрать — таблица
# ============================================================
# | Потребность                                   | Решение           |
# |----------------------------------------------------|----------------------|
# | Сборка в CI только последнего кода                  | shallow clone        |
# | Работа только с backend/, но ПОЛНАЯ история        | partial+sparse       |
# | Нужна полная история для git blame/log             | partial clone        |
# | Важнее всего место на диске, история не нужна       | shallow clone        |
""".strip()

L11_TASK = {
    "task_title": "Ushbu platformani sparse-checkout bilan klonlang",
    "task_title_ru": "Клонируйте эту платформу через sparse-checkout",
    "task_description": (
        "Ushbu platformaning repo'sini (yoki uning nusxasini) "
        "`git clone --filter=blob:none --sparse` bilan klonlang. "
        "`--cone` rejimida faqat `backend/` va `docs/` papkalarini "
        "tanlang. `du -sh .git` orqali hajmni to'liq klonlash bilan "
        "solishtiring. So'ngra `frontend/`ni ham qo'shib, qayta "
        "klonlashga hojat yo'qligini isbotlang."
    ),
    "task_description_ru": (
        "Клонируйте репозиторий этой платформы (или его копию) через "
        "`git clone --filter=blob:none --sparse`. В режиме `--cone` "
        "выберите только папки `backend/` и `docs/`. Через `du -sh "
        ".git` сравните размер с полным клонированием. Затем добавьте "
        "`frontend/` и докажите, что повторное клонирование не "
        "нужно."
    ),
    "task_requirements": (
        "1) `git sparse-checkout list` chiqishini keltiring. 2) `du "
        "-sh .git` natijasini to'liq clone bilan solishtiring (jadval "
        "shaklida). 3) `git sparse-checkout add frontend`dan keyin "
        "qayta tarmoq so'rovi (fetch) BO'LMASLIGINI ko'rsating (agar "
        "tree obyektlari allaqachon mavjud bo'lsa)."
    ),
    "task_requirements_ru": (
        "1) Приведите вывод `git sparse-checkout list`. 2) Сравните "
        "результат `du -sh .git` с полным clone (в виде таблицы). 3) "
        "Покажите, что после `git sparse-checkout add frontend` "
        "повторного сетевого запроса (fetch) НЕ происходит (если tree "
        "объекты уже есть)."
    ),
    "task_technologies": "Git (sparse-checkout --cone, clone --filter)",
    "task_deadline_days": 4,
}

L11_SAMPLE = {
    "title": "Namuna: sparse-checkout sozlash skripti",
    "description": (
        "Bash skripti mahalliy 'monorepo' simulyatsiyasini (backend/, "
        "frontend/, docs/, alembic/ papkalari bilan) yaratadi, so'ngra "
        "sparse-checkout orqali faqat kerakli papkalarni tanlaydi va "
        "hajm farqini ko'rsatadi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "setup_sparse_demo.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n\n"
                "rm -rf monorepo-src sparse-clone\n"
                "mkdir -p monorepo-src/{backend,frontend,docs,alembic}\n"
                "cd monorepo-src && git init -q\n\n"
                "echo 'FastAPI kodi' > backend/main.py\n"
                "echo 'React kodi' > frontend/App.js\n"
                "echo 'Hujjatlar' > docs/README.md\n"
                "for i in $(seq 1 30); do echo \"migratsiya $i\" > alembic/m$i.py; done\n"
                "git add . && git commit -q -m \"monorepo boshlang'ich holati\"\n"
                "SRC=$(pwd)\n"
                "cd ..\n\n"
                "git clone -q --no-local --filter=blob:none --sparse \"file://$SRC\" sparse-clone\n"
                "cd sparse-clone\n"
                "git sparse-checkout init --cone\n"
                "git sparse-checkout set backend docs\n\n"
                "echo \"=== checkout'dagi papkalar ===\"\n"
                "ls\n\n"
                "echo \"=== sparse-checkout ro'yxati ===\"\n"
                "git sparse-checkout list\n\n"
                "echo \"=== frontend'ni qaytarib qo'shish ===\"\n"
                "git sparse-checkout add frontend\n"
                "ls\n"
            ),
        },
    ],
}

L11_EXERCISES = [
    {
        "title": "sparse-checkout nimani qisqartiradi",
        "title_ru": "Что сокращает sparse-checkout",
        "description": "git sparse-checkout aslida nimani qisqartiradi?",
        "description_ru": "Что на самом деле сокращает git sparse-checkout?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ishchi katalogda checkout qilinadigan papkalarni (obyektlar bazasi to'liq qoladi)",
            "Obyektlar bazasining o'zini (commit/tree/blob sonini)",
            "Faqat .git/refs papkasini",
            "Remote serverdagi repo hajmini",
        ],
        "options_ru": [
            "Папки, выводимые (checkout) в рабочий каталог (база объектов остаётся полной)",
            "Саму базу объектов (число commit/tree/blob)",
            "Только папку .git/refs",
            "Размер репозитория на удалённом сервере",
        ],
        "correct_answers": "A",
        "hint": "Bazani qisqartiradigan narsa boshqa mavzu — partial clone.",
        "hint_ru": "То, что сокращает базу — другая тема, partial clone.",
        "explanation": "sparse-checkout faqat ishchi katalogni boshqaradi; obyektlar bazasini qisqartirish uchun partial clone kerak.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Ingichka klon qadamlarini tartiblang",
        "title_ru": "Расположите шаги тонкого клона",
        "description": "Katta monorepo'dan faqat kerakli papkalarni olishning to'g'ri tartibini joylashtiring.",
        "description_ru": "Расположите правильный порядок получения только нужных папок из большого monorepo.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git clone --filter=blob:none --sparse <url>",
            "git sparse-checkout init --cone",
            "git sparse-checkout set backend frontend",
            "Kerak bo'lganda git sparse-checkout add docs",
        ],
        "drag_items_ru": [
            "git clone --filter=blob:none --sparse <url>",
            "git sparse-checkout init --cone",
            "git sparse-checkout set backend frontend",
            "При необходимости git sparse-checkout add docs",
        ],
        "correct_order": [
            "git clone --filter=blob:none --sparse <url>",
            "git sparse-checkout init --cone",
            "git sparse-checkout set backend frontend",
            "Kerak bo'lganda git sparse-checkout add docs",
        ],
        "hint": "Avval yupqa clone, keyin rejim, keyin tanlov, oxirida kengaytirish.",
        "hint_ru": "Сначала тонкий clone, потом режим, потом выбор, в конце расширение.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "cone mode atamasi",
        "title_ru": "Термин cone mode",
        "description": "Git 2.25+ da tavsiya etiladigan, papka darajasida ishlaydigan tezroq sparse-checkout rejimi ___ deb ataladi.",
        "description_ru": "Рекомендуемый в Git 2.25+ более быстрый режим sparse-checkout, работающий на уровне папок, называется ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "cone",
        "correct_answers_ru": "cone",
        "hint": "--cone bayrog'ini eslang.",
        "hint_ru": "Вспомните флаг --cone.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 12 — Capstone: ilg'or Git workflow'ni real loyihada qo'llash
# ---------------------------------------------------------------------------

L12_TEXT = """
<h3>Capstone stsenariysi</h3>
<p>Siz jamoaviy loyihada (masalan, ushbu platformaning o'ziga o'xshash
monorepo'da) o'rta darajadagi funksiyani ishlab chiqasiz va bir vaqtning
o'zida ikkinchi, shoshilinch xatoni ham tuzatishingiz kerak. Bu capstone
0-11-darslardagi BARCHA vositalarni bitta izchil, real hayotdagi ish
oqimida qo'llashni talab qiladi — alohida mashq sifatida emas, balki
bir-biriga bog'liq qadamlar zanjiri sifatida.</p>

<h3>To'liq stsenariy — bosqichma-bosqich</h3>
<ol>
<li><strong>Bug topish (4-dars)</strong>: production'da funksiya
noto'g'ri ishlayapti. <code>git bisect run</code> bilan xato commit'ini
toping.</li>
<li><strong>Parallel ish (6-dars)</strong>: asosiy feature branch'ingizga
tegmasdan, <code>git worktree add</code> bilan alohida papkada hotfix
branch oching.</li>
<li><strong>Obyekt darajasida tekshiruv (0-dars)</strong>: topilgan
commit'ni <code>git cat-file -p</code> bilan tekshirib, aynan qaysi
fayl (tree/blob) o'zgarganini aniqlang.</li>
<li><strong>Toza tarix (3-dars)</strong>: tuzatishni bir necha kichik
commit bilan yozib, <code>git rebase -i --autosquash</code> bilan bitta
toza commit'ga aylantiring.</li>
<li><strong>Sifat darvozasi (8-dars)</strong>: mahalliy
<code>pre-commit</code>/<code>pre-push</code> hook'lar orqali maxfiy
kalit va testlarni tekshiring, so'ngra GitHub Actions CI'ga tayanib
YAKUNIY tasdiqni oling.</li>
<li><strong>Konflikt (9-dars)</strong>: hotfix'ni <code>main</code>ga
qaytarishda avvalgi shunga o'xshash konflikt <code>rerere</code> orqali
avtomatik yechilishini kuzating.</li>
<li><strong>Tashqi kutubxona (7-dars)</strong>: shu orada asosiy feature
branch'ingizda <code>vendor/</code> submodule'ini yangi versiyaga
ko'chirasiz.</li>
<li><strong>Yakuniy tozalash (2-dars)</strong>: barcha ish tugagach,
<code>git gc</code> orqali obyektlar bazasini optimallashtiring va
natijani <code>count-objects -v</code> bilan tasdiqlang.</li>
<li><strong>Katta repo bilan samarali ishlash (11-dars)</strong>: yangi
jamoa a'zosi uchun faqat kerakli papkalarni o'z ichiga olgan
sparse-checkout ko'rsatmasini yozing.</li>
</ol>

<h3>Nega bu tartib muhim</h3>
<p>Bu zanjir tasodifiy emas — u haqiqiy dasturchi ish kunining tipik
tuzilishi: avval MUAMMONI TOPISH (bisect), keyin uni ASOSIY ISHGA
XALAQIT BERMASDAN hal qilish (worktree), keyin YECHIMNI TUSHUNISH
(cat-file), keyin uni TOZA TARZDA taqdim qilish (rebase), keyin uni
IKKI QATLAMLI TEKSHIRUVDAN o'tkazish (hooks + CI), va nihoyat, VAQT
O'TISHI BILAN butun tizimni SAMARALI saqlash (gc, sparse-checkout).</p>

<h3>Yakuniy ish oqimi — umumlashtirilgan ko'rinish</h3>
<pre class="mermaid">
flowchart TB
  A["1. bisect: xato commit'ini topish"] --> B["2. worktree: alohida hotfix papka"]
  B --> C["3. cat-file: obyektni tushunish"]
  C --> D["4. rebase -i: toza commit"]
  D --> E["5. hooks: mahalliy tekshiruv"]
  E --> F["6. CI: server tomonidagi majburiy tasdiq"]
  F --> G["7. rerere: main'ga birlashtirishda avtomatik konflikt yechish"]
  G --> H["8. gc: obyektlarni siqish"]
  H --> I["9. sparse-checkout: yangi a'zo uchun yengil klon"]
  style A fill:#ffd6d6,stroke:#c00000
  style F fill:#d6e9ff,stroke:#2266aa
  style I fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Diagramma butun kursning yakuniy xaritasi: har bir qadam avvalgi
darsda alohida o'rganilgan mavzu, endi esa ular BITTA uzluksiz, real
loyihadagi ish oqimida birlashtirilgan.</p>

<h3>Baholash mezonlari</h3>
<p>Capstone loyihasi quyidagilar bo'yicha baholanadi: (1) har bir
bosqichning buyruq+natija dalili mavjudligi, (2) yakuniy commit
tarixining tozaligi (ortiqcha "wip"/"typo" commit'lar yo'qligi), (3)
xavfsizlik amaliyoti (maxfiy kalitlar hech qachon commit qilinmagan), (4)
git holatini tushunish chuqurligi — nafaqat "qaysi buyruq" balki "nega
aynan shu buyruq" savoliga javob berish qobiliyati.</p>

<h3>Bu capstone'ning haqiqiy jamoalarga aloqasi</h3>
<p>Bu stsenariy o'ylab topilgan mashq emas — bu haqiqiy o'rta va katta
dasturiy jamoalarning kundalik ishi. GitHub, GitLab kabi platformalarda
ishlaydigan muhandislar aynan shu vositalarni har kuni ishlatadi:
bisect — production incident'larni tergash uchun, worktree — bir vaqtda
bir nechta vazifa ustida ishlash uchun, rebase -i — PR'ni ko'rib chiquvchi
uchun o'qilishi oson qilish uchun, hooks+CI — sifat darvozasi sifatida,
rerere — uzoq muddatli branch'larni boshqarish uchun, va
sparse-checkout — ulkan monorepo'larda samarali ishlash uchun. Ushbu
platformaning o'zi ham xuddi shunday monorepo, xuddi shunday CI
(.github/workflows/) va xuddi shunday ko'p papkali tuzilishga ega — bu
kursda o'rgangan HAR BIR vosita shu yerda, haqiqatda, ishlatilishi
mumkin.</p>

<h3>Onboarding hujjatlarini yozish — docs/ papkasiga hissa</h3>
<p>Yaxshi muhandis nafaqat vositalarni bilishi, balki ularni jamoa
uchun HUJJATLASHTIRISHI kerak. Ushbu platformaning <code>docs/</code>
papkasida <code>BACKEND_BUGS.md</code> va <code>FRONTEND_BUGS.md</code>
kabi fayllar bor — xuddi shunday, capstone loyihangizning
<code>ONBOARDING.md</code> fayli yangi jamoa a'zosi uchun "birinchi kun"
qo'llanmasi bo'lib xizmat qiladi: qaysi papkalar kerak, qaysi hook'larni
o'rnatish kerak, qanday qilib tezkor klonlash mumkin.</p>
""".strip()

L12_TEXT_RU = """
<h3>Сценарий капстоуна</h3>
<p>Вы разрабатываете функцию средней сложности в командном проекте
(например, в monorepo, похожем на эту платформу), и одновременно нужно
исправить второй, срочный баг. Этот капстоун требует применить ВСЕ
инструменты уроков 0-11 в одном связном, реалистичном рабочем процессе —
не как отдельные упражнения, а как цепочку взаимосвязанных шагов.</p>

<h3>Полный сценарий — по шагам</h3>
<ol>
<li><strong>Поиск бага (урок 4)</strong>: функция неправильно работает в
production. Найдите баг-коммит через <code>git bisect run</code>.</li>
<li><strong>Параллельная работа (урок 6)</strong>: не трогая основную
feature-ветку, откройте hotfix-ветку в отдельной папке через <code>git
worktree add</code>.</li>
<li><strong>Проверка на уровне объектов (урок 0)</strong>: проверьте
найденный коммит через <code>git cat-file -p</code>, определите, какой
именно файл (tree/blob) изменился.</li>
<li><strong>Чистая история (урок 3)</strong>: запишите исправление
несколькими мелкими коммитами, превратите их в один чистый коммит через
<code>git rebase -i --autosquash</code>.</li>
<li><strong>Ворота качества (урок 8)</strong>: проверьте секретные ключи
и тесты через локальные hook <code>pre-commit</code>/<code>pre-push</code>,
затем получите ФИНАЛЬНОЕ подтверждение от GitHub Actions CI.</li>
<li><strong>Конфликт (урок 9)</strong>: при возврате hotfix в
<code>main</code> понаблюдайте, как похожий прошлый конфликт разрешается
автоматически через <code>rerere</code>.</li>
<li><strong>Внешняя библиотека (урок 7)</strong>: тем временем в
основной feature-ветке обновите submodule <code>vendor/</code> до новой
версии.</li>
<li><strong>Финальная очистка (урок 2)</strong>: после завершения всей
работы оптимизируйте базу объектов через <code>git gc</code> и
подтвердите результат через <code>count-objects -v</code>.</li>
<li><strong>Эффективная работа с большим репозиторием (урок 11)</strong>:
напишите инструкцию sparse-checkout для нового члена команды, включающую
только нужные папки.</li>
</ol>

<h3>Почему важен именно такой порядок</h3>
<p>Эта цепочка не случайна — это типичная структура рабочего дня
настоящего разработчика: сначала НАЙТИ ПРОБЛЕМУ (bisect), затем решить
её, НЕ МЕШАЯ основной работе (worktree), затем ПОНЯТЬ решение
(cat-file), затем представить его в ЧИСТОМ виде (rebase), затем провести
через ДВУХУРОВНЕВУЮ проверку (hooks + CI), и наконец СО ВРЕМЕНЕМ
эффективно поддерживать всю систему (gc, sparse-checkout).</p>

<h3>Итоговый рабочий процесс — обобщённый вид</h3>
<pre class="mermaid">
flowchart TB
  A["1. bisect: найти баг-коммит"] --> B["2. worktree: отдельная папка hotfix"]
  B --> C["3. cat-file: понять объект"]
  C --> D["4. rebase -i: чистый коммит"]
  D --> E["5. hooks: локальная проверка"]
  E --> F["6. CI: обязательное подтверждение на сервере"]
  F --> G["7. rerere: автоматическое разрешение конфликта при merge в main"]
  G --> H["8. gc: сжатие объектов"]
  H --> I["9. sparse-checkout: лёгкий клон для нового участника"]
  style A fill:#ffd6d6,stroke:#c00000
  style F fill:#d6e9ff,stroke:#2266aa
  style I fill:#d6e9ff,stroke:#2266aa
</pre>
<p>Диаграмма — итоговая карта всего курса: каждый шаг — тема, изученная
отдельно в предыдущем уроке, теперь же они объединены в ОДИН непрерывный
рабочий процесс реального проекта.</p>

<h3>Критерии оценки</h3>
<p>Капстоун-проект оценивается по: (1) наличию доказательства
команда+результат для каждого шага, (2) чистоте финальной истории
коммитов (отсутствие лишних коммитов "wip"/"опечатка"), (3) практике
безопасности (секретные ключи никогда не закоммичены), (4) глубине
понимания состояния git — не только "какая команда", но и способности
ответить на вопрос "почему именно эта команда".</p>

<h3>Связь этого капстоуна с реальными командами</h3>
<p>Этот сценарий не выдуманное упражнение — это ежедневная работа
реальных средних и крупных команд разработки. Инженеры, работающие на
платформах вроде GitHub, GitLab, используют именно эти инструменты
каждый день: bisect — для расследования production-инцидентов,
worktree — для работы над несколькими задачами одновременно, rebase -i —
чтобы сделать PR удобным для чтения ревьюером, hooks+CI — как ворота
качества, rerere — для управления долгоживущими ветками, и
sparse-checkout — для эффективной работы в огромных monorepo. Сама эта
платформа — такой же monorepo, с таким же CI (.github/workflows/) и
такой же многопапочной структурой — КАЖДЫЙ инструмент, изученный в этом
курсе, может быть реально использован именно здесь.</p>

<h3>Написание onboarding-документации — вклад в папку docs/</h3>
<p>Хороший инженер должен не только знать инструменты, но и
ДОКУМЕНТИРОВАТЬ их для команды. В папке <code>docs/</code> этой
платформы есть файлы вроде <code>BACKEND_BUGS.md</code> и
<code>FRONTEND_BUGS.md</code> — аналогично, файл <code>ONBOARDING.md</code>
вашего капстоун-проекта служит руководством "первого дня" для нового
члена команды: какие папки нужны, какие hook установить, как быстро
клонировать.</p>
""".strip()

L12_CODE = """
# ============================================================
# CAPSTONE: to'liq ish oqimi, boshidan oxirigacha
# ============================================================

# --- 1. bisect: xatoni topish ---
$ git bisect start HEAD v3.0.0
$ git bisect run ./check_bug.sh
a1b2c3d is the first bad commit

# --- 2. worktree: alohida hotfix papka ---
$ git worktree add ../hotfix a1b2c3d^
$ cd ../hotfix
$ git switch -c hotfix/hisoblash-xatosi

# --- 3. cat-file: obyektni tushunish ---
$ git cat-file -p a1b2c3d | head -3
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d
parent 0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
$ git cat-file -p 9f8e7d6c | grep payment
100644 blob 5a4b3c2d... payment_service.py

# --- 4. Tuzatish + rebase -i --autosquash bilan toza commit ---
$ vim payment_service.py && git commit -am "urinish"
$ vim payment_service.py && git commit -am "test qo'shildi"
$ git rebase -i HEAD~2   # squash qilib bittaga aylantiramiz
$ git log --oneline -1
e5f6a7b fix: chegirma hisoblash formulasi tuzatildi (test bilan)

# --- 5. Mahalliy hook + CI ikki qatlamli tekshiruv ---
$ git push origin hotfix/hisoblash-xatosi
pre-push: backend testlari (test.yml kabi)...
3 passed
# ... push davom etadi, GitHub Actions serverda MUSTAQIL qayta tekshiradi

# --- 6. main'ga birlashtirish, rerere avvalgi konfliktni eslaydi ---
$ git switch main
$ git merge hotfix/hisoblash-xatosi
Auto-merging payment_service.py
Resolved 'payment_service.py' using previous resolution.
Merge made by the 'ort' strategy.

# --- 7. Shu orada feature branch'da submodule yangilanadi ---
$ git switch feature/yangi-funksiya
$ cd vendor/ui-kit && git pull origin main && cd ../..
$ git add vendor/ui-kit
$ git commit -m "vendor/ui-kit v2.2.0 ga yangilandi"

# --- 8. Yakuniy tozalash ---
$ git worktree remove ../hotfix
$ git count-objects -v
count: 34
in-pack: 512
$ git gc
$ git count-objects -v
count: 0
in-pack: 546

# --- 9. Yangi a'zo uchun yengil klon ko'rsatmasi ---
$ cat ONBOARDING.md
## Faqat backend bilan ishlaydigan dasturchilar uchun:
git clone --filter=blob:none --sparse <url>
cd student_platform
git sparse-checkout init --cone
git sparse-checkout set backend alembic
# frontend/ va docs/ kerak bo'lsa:
# git sparse-checkout add frontend docs

# ============================================================
# Yakuniy tarix — toza va tushunarli
# ============================================================
$ git log --oneline --graph -8
*   f9e8d7c Merge branch 'hotfix/hisoblash-xatosi'
|\\
| * e5f6a7b fix: chegirma hisoblash formulasi tuzatildi (test bilan)
* | 7c3a1e9 vendor/ui-kit v2.2.0 ga yangilandi
* | 3f2e1d0 feat: yangi funksiya asosiy qismi
|/
* 0c9b8a7 boshlang'ich holat

# ============================================================
# YAKUNIY CHEAT-SHEET: kurs davomida o'rganilgan barcha buyruqlar
# ============================================================
# | Mavzu                | Asosiy buyruq                                    |
# |------------------------|-----------------------------------------------------|
# | Obyektlar (0-dars)     | git cat-file -p/-t, git hash-object -w              |
# | Refs/HEAD (1-dars)     | git symbolic-ref, cat .git/HEAD, git reflog         |
# | Packfile (2-dars)      | git gc, git count-objects -v, git repack -a -d      |
# | Rebase (3-dars)        | git rebase -i, --autosquash, --onto                 |
# | Bisect (4-dars)        | git bisect start/good/bad/run, --term-old/new       |
# | Worktree (6-dars)      | git worktree add/list/remove/lock                   |
# | Submodule/Subtree (7)  | git submodule add/foreach, git subtree add/pull     |
# | Hooks (8-dars)         | .git/hooks/, core.hooksPath, pre-commit/pre-push    |
# | Konflikt (9-dars)      | git rerere, merge=ours, -X ours/theirs, mergetool   |
# | Monorepo (11-dars)     | sparse-checkout --cone, clone --filter=blob:none    |

$ echo "Capstone yakunlandi — 12 mavzu, bitta ish oqimida."
Capstone yakunlandi — 12 mavzu, bitta ish oqimida.
""".strip()

L12_CODE_RU = """
# ============================================================
# CAPSTONE: полный рабочий процесс, от начала до конца
# ============================================================

# --- 1. bisect: поиск бага ---
$ git bisect start HEAD v3.0.0
$ git bisect run ./check_bug.sh
a1b2c3d is the first bad commit

# --- 2. worktree: отдельная папка hotfix ---
$ git worktree add ../hotfix a1b2c3d^
$ cd ../hotfix
$ git switch -c hotfix/oshibka-rascheta

# --- 3. cat-file: понимание объекта ---
$ git cat-file -p a1b2c3d | head -3
tree 9f8e7d6c5b4a3928170615f4e3d2c1b0a9f8e7d
parent 0c9b8a7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b
$ git cat-file -p 9f8e7d6c | grep payment
100644 blob 5a4b3c2d... payment_service.py

# --- 4. Исправление + чистый коммит через rebase -i --autosquash ---
$ vim payment_service.py && git commit -am "попытка"
$ vim payment_service.py && git commit -am "добавлен тест"
$ git rebase -i HEAD~2   # squash в один коммит
$ git log --oneline -1
e5f6a7b fix: исправлена формула расчёта скидки (с тестом)

# --- 5. Двухуровневая проверка: локальный hook + CI ---
$ git push origin hotfix/oshibka-rascheta
pre-push: запускаются тесты backend (как в test.yml)...
3 passed
# ... push продолжается, GitHub Actions на сервере проверяет НЕЗАВИСИМО

# --- 6. Merge в main, rerere запоминает прошлый конфликт ---
$ git switch main
$ git merge hotfix/oshibka-rascheta
Auto-merging payment_service.py
Resolved 'payment_service.py' using previous resolution.
Merge made by the 'ort' strategy.

# --- 7. Тем временем в feature-ветке обновляется submodule ---
$ git switch feature/novaya-funkciya
$ cd vendor/ui-kit && git pull origin main && cd ../..
$ git add vendor/ui-kit
$ git commit -m "обновлён vendor/ui-kit до v2.2.0"

# --- 8. Финальная очистка ---
$ git worktree remove ../hotfix
$ git count-objects -v
count: 34
in-pack: 512
$ git gc
$ git count-objects -v
count: 0
in-pack: 546

# --- 9. Инструкция лёгкого клона для нового участника ---
$ cat ONBOARDING.md
## Для разработчиков, работающих только с backend:
git clone --filter=blob:none --sparse <url>
cd student_platform
git sparse-checkout init --cone
git sparse-checkout set backend alembic
# если нужны frontend/ и docs/:
# git sparse-checkout add frontend docs

# ============================================================
# Финальная история — чистая и понятная
# ============================================================
$ git log --oneline --graph -8
*   f9e8d7c Merge branch 'hotfix/oshibka-rascheta'
|\\
| * e5f6a7b fix: исправлена формула расчёта скидки (с тестом)
* | 7c3a1e9 обновлён vendor/ui-kit до v2.2.0
* | 3f2e1d0 feat: основная часть новой функции
|/
* 0c9b8a7 начальное состояние

# ============================================================
# ИТОГОВЫЙ CHEAT-SHEET: все команды, изученные в курсе
# ============================================================
# | Тема                    | Основная команда                                 |
# |----------------------------|-------------------------------------------------------|
# | Объекты (урок 0)          | git cat-file -p/-t, git hash-object -w              |
# | Refs/HEAD (урок 1)        | git symbolic-ref, cat .git/HEAD, git reflog         |
# | Packfile (урок 2)         | git gc, git count-objects -v, git repack -a -d      |
# | Rebase (урок 3)           | git rebase -i, --autosquash, --onto                 |
# | Bisect (урок 4)           | git bisect start/good/bad/run, --term-old/new       |
# | Worktree (урок 6)         | git worktree add/list/remove/lock                   |
# | Submodule/Subtree (7)     | git submodule add/foreach, git subtree add/pull     |
# | Hooks (урок 8)            | .git/hooks/, core.hooksPath, pre-commit/pre-push    |
# | Конфликты (урок 9)        | git rerere, merge=ours, -X ours/theirs, mergetool   |
# | Monorepo (урок 11)        | sparse-checkout --cone, clone --filter=blob:none    |

$ echo "Капстоун завершён — 12 тем, один рабочий процесс."
Капстоун завершён — 12 тем, один рабочий процесс.
""".strip()

L12_TASK = {
    "task_title": "Capstone: to'liq ilg'or Git workflow'ni bajaring",
    "task_title_ru": "Капстоун: выполните полный продвинутый Git workflow",
    "task_description": (
        "Sun'iy 'monorepo' loyiha yarating (kamida 2 papka: backend/, "
        "frontend/). Quyidagi TO'LIQ zanjirni bajaring va har bir "
        "qadamni hisobotga kiriting: (1) `git bisect run` bilan xato "
        "commit'ini toping, (2) `git worktree add` bilan alohida hotfix "
        "ochib tuzating, (3) `git cat-file -p` bilan obyektni tushuning, "
        "(4) `git rebase -i --autosquash` bilan toza commit yarating, "
        "(5) mahalliy pre-commit/pre-push hook bilan tekshiring, (6) "
        "`main`ga birlashtirishda oldindan yozilgan `rerere` yechimi "
        "avtomatik ishlashini ko'rsating, (7) `git gc` bilan yakunlang, "
        "(8) yangi a'zo uchun sparse-checkout ko'rsatmasini yozing."
    ),
    "task_description_ru": (
        "Создайте искусственный 'monorepo' проект (минимум 2 папки: "
        "backend/, frontend/). Выполните ПОЛНУЮ цепочку и включите в "
        "отчёт каждый шаг: (1) найдите баг-коммит через `git bisect "
        "run`, (2) откройте отдельный hotfix через `git worktree add` и "
        "исправьте, (3) поймите объект через `git cat-file -p`, (4) "
        "создайте чистый коммит через `git rebase -i --autosquash`, (5) "
        "проверьте через локальный pre-commit/pre-push hook, (6) "
        "покажите, что заранее записанное решение `rerere` срабатывает "
        "автоматически при merge в `main`, (7) завершите через `git "
        "gc`, (8) напишите инструкцию sparse-checkout для нового "
        "участника."
    ),
    "task_requirements": (
        "1) Barcha 8 bosqichning buyruq+natija dalili hisobotda "
        "bo'lishi shart. 2) Yakuniy `git log --oneline --graph` toza, "
        "mantiqiy tarixni ko'rsatishi kerak (ortiqcha 'wip'/'typo' "
        "commit'siz). 3) `git count-objects -v` gc'dan oldin va "
        "keyingi solishtirilgan holda keltirilishi kerak. 4) "
        "ONBOARDING ko'rsatmasi kamida 2 ta aniq papkani ko'rsatishi "
        "kerak."
    ),
    "task_requirements_ru": (
        "1) В отчёте должно быть доказательство команда+результат для "
        "всех 8 шагов. 2) Финальный `git log --oneline --graph` должен "
        "показывать чистую, логичную историю (без лишних "
        "'wip'/'опечатка' коммитов). 3) `git count-objects -v` должен "
        "быть приведён в сравнении до и после gc. 4) Инструкция "
        "ONBOARDING должна указывать минимум 2 конкретные папки."
    ),
    "task_technologies": "Git (bisect, worktree, cat-file, rebase -i, hooks, rerere, gc, sparse-checkout)",
    "task_deadline_days": 7,
}

L12_SAMPLE = {
    "title": "Namuna: capstone to'liq avtomatlashtirilgan skript",
    "description": (
        "Kursning barcha 12 mavzusini bitta uzluksiz bash skriptida "
        "birlashtiruvchi to'liq namuna: bisect, worktree, cat-file, "
        "rebase, hooks, rerere, gc, sparse-checkout."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "capstone_full_workflow.sh",
            "language": "bash",
            "code": (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "export GIT_EDITOR=true\n\n"
                "rm -rf capstone capstone-hotfix\n"
                "mkdir -p capstone/{backend,frontend} && cd capstone && git init -q\n"
                "git config rerere.enabled true\n\n"
                "cat > .git/hooks/pre-commit << 'EOF'\n"
                "#!/bin/bash\n"
                "git diff --cached | grep -qE \"SECRET_KEY\\s*=\" && { echo \"XATO: maxfiy kalit!\"; exit 1; }\n"
                "exit 0\n"
                "EOF\n"
                "chmod +x .git/hooks/pre-commit\n\n"
                "echo 'def discount(p, pct): return p - pct  # BUG' > backend/pay.py\n"
                "echo 'App' > frontend/App.js\n"
                "git add . && git commit -q -m \"c0: BUG bilan boshlang'ich holat\"\n"
                "for i in $(seq 1 5); do echo \"# no-op $i\" >> backend/pay.py; git add .; git commit -q -m \"c$i\"; done\n\n"
                "cat > check.sh << 'EOF'\n"
                "#!/bin/bash\n"
                "python3 -c \"import sys; sys.path.insert(0,'backend'); from pay import discount; assert discount(100,10)==90\"\n"
                "EOF\n"
                "chmod +x check.sh\n\n"
                "echo \"== 1) BISECT ==\"\n"
                "ROOT=$(git rev-list --max-parents=0 HEAD)\n"
                "git bisect start HEAD \"$ROOT\" > /dev/null\n"
                "git bisect run ./check.sh | tail -2\n"
                "git bisect reset\n\n"
                "echo \"== 2) WORKTREE ==\"\n"
                "git worktree add -q ../capstone-hotfix -b hotfix/fix-discount main 2>/dev/null || \\\n"
                "  git worktree add -q ../capstone-hotfix -b hotfix/fix-discount master\n"
                "cd ../capstone-hotfix\n\n"
                "echo \"== 4) TUZATISH + REBASE ==\"\n"
                "echo 'def discount(p, pct): return p - (p*pct/100)' > backend/pay.py\n"
                "git commit -qam \"tuzatish\"\n"
                "echo '# test' >> backend/pay.py\n"
                "git commit -qam \"test qo'shildi\"\n"
                "GIT_SEQUENCE_EDITOR='sed -i \"2s/pick/squash/\"' git rebase -i HEAD~2\n"
                "git log --oneline -1\n\n"
                "echo \"== 6) MAIN'GA BIRLASHTIRISH ==\"\n"
                "cd ../capstone\n"
                "git merge hotfix/fix-discount --no-edit | tail -3\n\n"
                "echo \"== 8) GC ==\"\n"
                "git count-objects -v\n"
                "git gc --quiet\n"
                "git count-objects -v\n\n"
                "git worktree remove ../capstone-hotfix --force\n"
            ),
        },
        {
            "filename": "ONBOARDING.md",
            "language": "markdown",
            "code": (
                "# Yangi jamoa a'zosi uchun yengil klon\n\n"
                "Faqat backend bilan ishlaysizmi? To'liq tarixni yuklamang:\n\n"
                "```bash\n"
                "git clone --filter=blob:none --sparse <repo-url>\n"
                "cd <repo>\n"
                "git sparse-checkout init --cone\n"
                "git sparse-checkout set backend alembic\n"
                "```\n\n"
                "Keyinroq frontend kerak bo'lsa:\n\n"
                "```bash\n"
                "git sparse-checkout add frontend\n"
                "```\n"
            ),
        },
    ],
}

L12_EXERCISES = [
    {
        "title": "Capstone: ish oqimidagi vositalar",
        "title_ru": "Капстоун: инструменты в рабочем процессе",
        "description": "Capstone stsenariysida xatoni ANIQLASH bosqichida qaysi vosita ishlatiladi?",
        "description_ru": "Какой инструмент используется на этапе ОБНАРУЖЕНИЯ бага в сценарии капстоуна?",
        "exercise_type": "multiple_choice",
        "options": [
            "git bisect run",
            "git worktree add",
            "git rerere",
            "git sparse-checkout",
        ],
        "options_ru": [
            "git bisect run",
            "git worktree add",
            "git rerere",
            "git sparse-checkout",
        ],
        "correct_answers": "A",
        "hint": "4-darsni eslang — ikkilik qidiruv bilan xato commit'ini topish.",
        "hint_ru": "Вспомните урок 4 — поиск бага через двоичный поиск.",
        "explanation": "bisect run xato commit'ini avtomatik topadi, bu esa keyingi barcha qadamlarning boshlang'ich nuqtasi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Capstone: to'liq ish oqimini tartiblang",
        "title_ru": "Капстоун: расположите полный рабочий процесс",
        "description": "Xatoni topishdan yangi a'zoni onboarding qilishgacha bo'lgan to'g'ri ketma-ketlikni joylashtiring.",
        "description_ru": "Расположите правильную последовательность от обнаружения бага до onboarding нового участника.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "git bisect run bilan xato commit'ini topish",
            "git worktree add bilan alohida hotfix ochish",
            "git rebase -i --autosquash bilan toza commit yaratish",
            "main'ga birlashtirish (rerere avtomatik yechadi)",
            "git gc bilan yakunlash",
            "Yangi a'zo uchun sparse-checkout ko'rsatmasi yozish",
        ],
        "drag_items_ru": [
            "Найти баг-коммит через git bisect run",
            "Открыть отдельный hotfix через git worktree add",
            "Создать чистый коммит через git rebase -i --autosquash",
            "Merge в main (rerere разрешает автоматически)",
            "Завершить через git gc",
            "Написать инструкцию sparse-checkout для нового участника",
        ],
        "correct_order": [
            "git bisect run bilan xato commit'ini topish",
            "git worktree add bilan alohida hotfix ochish",
            "git rebase -i --autosquash bilan toza commit yaratish",
            "main'ga birlashtirish (rerere avtomatik yechadi)",
            "git gc bilan yakunlash",
            "Yangi a'zo uchun sparse-checkout ko'rsatmasi yozish",
        ],
        "hint": "Kurs davomida o'rgangan 0-11-darslar tartibiga mos keladi.",
        "hint_ru": "Соответствует порядку уроков 0-11, изученных в курсе.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Capstone: yakuniy mulohaza",
        "title_ru": "Капстоун: итоговое рассуждение",
        "description": "Nega mahalliy pre-push hook testlarni o'tkazgan bo'lsa ham, GitHub Actions CI YANA testlarni ishga tushiradi — bu ortiqcha ish emasmi? Fikringizni asoslang.",
        "description_ru": "Почему GitHub Actions CI ЕЩЁ РАЗ запускает тесты, даже если локальный pre-push hook уже их пропустил — не лишняя ли это работа? Обоснуйте свою позицию.",
        "exercise_type": "text_input",
        "expected_answer": "Ortiqcha emas, chunki mahalliy hook --no-verify bilan chetlab o'tilishi mumkin va faqat bitta dasturchining muhitida ishlaydi; CI esa har doim bir xil, boshqariladigan serverda ishlab, hech kim chetlab o'ta olmaydigan yagona ishonchli tekshiruvni ta'minlaydi.",
        "hint": "8-darsdagi mahalliy hook vs CI kafolat darajasi bo'limini eslang.",
        "hint_ru": "Вспомните раздел урока 8 про уровень гарантии локального hook против CI.",
        "difficulty_level": "Hard",
        "points": 12,
    },
]

# ---------------------------------------------------------------------------
# LESSONS assembly
# ---------------------------------------------------------------------------

LESSONS = [
    {
        "order": 0,
        "title": "Git obyektlari: blob, tree, commit va SHA-1 bilan tanishuv",
        "title_ru": "Объекты Git: blob, tree, commit и знакомство с SHA-1",
        "points_reward": 15,
        "text_content": L0_TEXT,
        "text_content_ru": L0_TEXT_RU,
        "code_content": L0_CODE,
        "code_content_ru": L0_CODE_RU,
        "code_language": "bash",
        "task": L0_TASK,
        "sample": L0_SAMPLE,
        "exercises": L0_EXERCISES,
    },
    {
        "order": 1,
        "title": "Refs, HEAD, branch'lar — yengil ko'rsatkichlar",
        "title_ru": "Refs, HEAD, ветки — лёгкие указатели",
        "points_reward": 15,
        "text_content": L1_TEXT,
        "text_content_ru": L1_TEXT_RU,
        "code_content": L1_CODE,
        "code_content_ru": L1_CODE_RU,
        "code_language": "bash",
        "task": L1_TASK,
        "sample": L1_SAMPLE,
        "exercises": L1_EXERCISES,
    },
    {
        "order": 2,
        "title": "Packfile va git gc: tarix qanday siqiladi",
        "title_ru": "Packfile и git gc: как сжимается история",
        "points_reward": 15,
        "text_content": L2_TEXT,
        "text_content_ru": L2_TEXT_RU,
        "code_content": L2_CODE,
        "code_content_ru": L2_CODE_RU,
        "code_language": "bash",
        "task": L2_TASK,
        "sample": L2_SAMPLE,
        "exercises": L2_EXERCISES,
    },
    {
        "order": 3,
        "title": "Interaktiv rebase: squash, fixup, reorder, edit, drop",
        "title_ru": "Интерактивный rebase: squash, fixup, reorder, edit, drop",
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
        "title": "git bisect: xatoni ikkilik qidiruv bilan topish",
        "title_ru": "git bisect: поиск бага через двоичный поиск",
        "points_reward": 15,
        "text_content": L4_TEXT,
        "text_content_ru": L4_TEXT_RU,
        "code_content": L4_CODE,
        "code_content_ru": L4_CODE_RU,
        "code_language": "bash",
        "task": L4_TASK,
        "sample": L4_SAMPLE,
        "exercises": L4_EXERCISES,
    },
    {
        "order": 5,
        "title": "R1 — Takrorlash: obyektlar, refs, packfile, rebase, bisect",
        "title_ru": "R1 — Повторение: объекты, refs, packfile, rebase, bisect",
        "points_reward": 20,
        "text_content": L5_TEXT,
        "text_content_ru": L5_TEXT_RU,
        "code_content": L5_CODE,
        "code_content_ru": L5_CODE_RU,
        "code_language": "bash",
        "task": L5_TASK,
        "sample": L5_SAMPLE,
        "exercises": L5_EXERCISES,
    },
    {
        "order": 6,
        "title": "git worktree: bir vaqtda bir nechta branch ustida ishlash",
        "title_ru": "git worktree: работа с несколькими ветками одновременно",
        "points_reward": 15,
        "text_content": L6_TEXT,
        "text_content_ru": L6_TEXT_RU,
        "code_content": L6_CODE,
        "code_content_ru": L6_CODE_RU,
        "code_language": "bash",
        "task": L6_TASK,
        "sample": L6_SAMPLE,
        "exercises": L6_EXERCISES,
    },
    {
        "order": 7,
        "title": "Submodule vs Subtree: tashqi repo'larni boshqarish",
        "title_ru": "Submodule против Subtree: управление внешними репозиториями",
        "points_reward": 15,
        "text_content": L7_TEXT,
        "text_content_ru": L7_TEXT_RU,
        "code_content": L7_CODE,
        "code_content_ru": L7_CODE_RU,
        "code_language": "bash",
        "task": L7_TASK,
        "sample": L7_SAMPLE,
        "exercises": L7_EXERCISES,
    },
    {
        "order": 8,
        "title": "Git hooks: mahalliy pre-commit/pre-push avtomatlashtirish",
        "title_ru": "Git hooks: локальная автоматизация pre-commit/pre-push",
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
        "title": "Ilg'or merge-konflikt strategiyalari: rerere, merge drayverlari",
        "title_ru": "Продвинутые стратегии merge-конфликтов: rerere, merge drivers",
        "points_reward": 15,
        "text_content": L9_TEXT,
        "text_content_ru": L9_TEXT_RU,
        "code_content": L9_CODE,
        "code_content_ru": L9_CODE_RU,
        "code_language": "bash",
        "task": L9_TASK,
        "sample": L9_SAMPLE,
        "exercises": L9_EXERCISES,
    },
    {
        "order": 10,
        "title": "R2 — Takrorlash: worktree, submodule/subtree, hooks, rerere",
        "title_ru": "R2 — Повторение: worktree, submodule/subtree, hooks, rerere",
        "points_reward": 20,
        "text_content": L10_TEXT,
        "text_content_ru": L10_TEXT_RU,
        "code_content": L10_CODE,
        "code_content_ru": L10_CODE_RU,
        "code_language": "bash",
        "task": L10_TASK,
        "sample": L10_SAMPLE,
        "exercises": L10_EXERCISES,
    },
    {
        "order": 11,
        "title": "Monorepo asoslari: sparse-checkout va partial clone",
        "title_ru": "Основы monorepo: sparse-checkout и partial clone",
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
        "title": "Capstone: ilg'or Git workflow'ni real loyihada qo'llash",
        "title_ru": "Капстоун: применение продвинутого Git workflow в реальном проекте",
        "points_reward": 25,
        "text_content": L12_TEXT,
        "text_content_ru": L12_TEXT_RU,
        "code_content": L12_CODE,
        "code_content_ru": L12_CODE_RU,
        "code_language": "bash",
        "task": L12_TASK,
        "sample": L12_SAMPLE,
        "exercises": L12_EXERCISES,
    },
]
