"""Seed the "Git va GitHub" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_git_github.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: dasturlash boshlovchilari — har kim. Hech qanday old talab
yo'q (CLI bilan tanish bo'lish foydali, lekin shart emas). Git/GitHub —
har dasturchining birinchi qurolidan biri. Bu kurs barcha boshqa kurslar
uchun prerequisite. Til: Uzbek + Russian section labels. WIN-FIRST shape.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "Git va GitHub",
    "description": (
        "Har dasturchining birinchi quroli — versiyalarni boshqarish. Lokal "
        "Git'dan tortib GitHub'da jamoaviy ish, Pull Request, merge conflict, "
        "rebase, GitHub Actions va to'liq team workflow capstone'ga qadar. "
        "Bu kurs barcha boshqa kurslar uchun zarur asos."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 3,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson content placeholders
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Git nima va birinchi repo</h2>

<pre class="mermaid">
flowchart LR
    WD["Working Directory\n(siz tahrirlovchi fayllar)"] -->|git add| ST["Staging Area\n(commit'ga tayyor)"]
    ST -->|git commit| RP["Repository\n(.git papka, tarix)"]
    RP -->|git checkout| WD
</pre>

<p><strong>Git</strong> — bu sizning kodingiz uchun "Ctrl+Z bilan vaqt mashinasi". Har o'zgartirish saqlanadi, qaytarish, eski versiyaga qaytish, yondosh versiyalar (branch) bilan ishlash — hammasi mumkin. Versiyalarni boshqarish tizimi (VCS — Version Control System).</p>

<p>Nima uchun kerakmi? Quyidagi muammolarni tasavvur qiling:</p>
<ul>
<li>📁 <code>loyiha_yangi.py</code>, <code>loyiha_yangi_final.py</code>, <code>loyiha_yangi_final_v2.py</code>... Git'siz hayot.</li>
<li>🐛 Kecha ishlatgan kod bugun ishlamayapti. Nima o'zgardi?</li>
<li>👥 Sherigingiz bilan birga ishlamoqdasiz. Kim qaysi qatorni o'zgartirdi?</li>
<li>🔥 Tasodifan muhim faylni o'chirib qo'ydingiz.</li>
</ul>

<p>Git — barcha bu muammolarni hal qiladi. <strong>GitHub</strong> — Git'ni internetda saqlash va jamoaviy ishlash uchun veb-sayt (oxirgi 4 darsda).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Git o'rnatish va sozlash</h4>
<pre><code># Tekshirish — git bormi?
git --version
# git version 2.43.0

# Birinchi ishlatganda — ism va email
git config --global user.name "Olim Karimov"
git config --global user.email "olim@example.uz"

# Default branch — main (master emas, zamonaviy)
git config --global init.defaultBranch main</code></pre>

<p>Bu konfiguratsiya bir marta — kompyuteringizda butun umrga. Endi Git sizning har commitingizga "Olim Karimov" deb yozadi.</p>

<h4>BLOKA 2 — birinchi repo</h4>
<pre><code># Yangi papka
mkdir mening-loyiham
cd mening-loyiham

# Git'ni shu yerda ishga tushirish
git init
# Initialized empty Git repository in .../mening-loyiham/.git/

# Yashirin .git papka paydo bo'ldi — Git'ning hammasi shu yerda
ls -la</code></pre>

<p><strong>.git</strong> papka — bu butun tarix, branchlar, sozlamalar. Uni qo'l bilan tahrirlash mumkin emas, faqat <code>git</code> komandalari orqali.</p>

<h4>BLOKA 3 — birinchi commit</h4>
<pre><code># Fayl yaratamiz
echo "# Mening loyiham" &gt; README.md
echo "print('Salom, Git!')" &gt; main.py

# Holat — Git nima ko'rdi?
git status
# Untracked files: README.md, main.py

# Staging area'ga qo'shamiz
git add README.md main.py
# yoki barchasi:
git add .

# Yana status — endi yashil rangda
git status
# Changes to be committed: README.md, main.py

# Commit — fotoglavlash
git commit -m "Birinchi commit: README va main.py"
# [main (root-commit) abc1234] Birinchi commit: README va main.py
#  2 files changed, 2 insertions(+)

# Tarix
git log
# commit abc1234... (HEAD -&gt; main)
# Author: Olim Karimov &lt;olim@example.uz&gt;
# Date: ...
#
#     Birinchi commit: README va main.py</code></pre>

<p>Tabriklayman! Sizning kodingiz endi <strong>versiyalanmoqda</strong>. Har qachon bu fotoga (commit) qaytish mumkin.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>git commit -m "yaxshilash"
# nothing to commit, working tree clean</code></pre>

<p><strong>Sabab:</strong> <code>git add</code> qilmagansiz. Git 3 ta "joy" bor — <strong>Working Directory</strong> (siz tahrirlovchi fayllar), <strong>Staging Area</strong> (commit'ga tayyor), <strong>Repository</strong> (commit qilingan tarix). Fayllar avtomatik commit qilinmaydi — siz aniq aytishingiz kerak: "shu fayllarni commit'ga qo'shing" (<code>git add</code>), keyin "endi commit qiling" (<code>git commit</code>).</p>

<p>Bu — yangi boshlovchining eng katta savoli: "Nima uchun ikki bosqich?" Sabab: siz <em>aniq tanlay olasiz</em> — qaysi o'zgarishlarni shu commit'ga, qaysilarini keyingisiga.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. 3 ta hudud (areas) — vizual</h4>

<pre><code>+--------------+        +--------------+        +-------------+
| Working Dir  | -- add | Staging Area | commit | Repository  |
| (sizning     |  ----&gt; | (tayyor      | -----&gt; | (.git tarix)|
|  fayllaringiz)|        |  o'zgarishlar)|        |             |
+--------------+        +--------------+        +-------------+
       ^                                                |
       |________________________________________________|
                  git checkout / git reset</code></pre>

<h4>2. Asosiy buyruqlar</h4>
<table>
<tr><th>Buyruq</th><th>Vazifa</th></tr>
<tr><td><code>git init</code></td><td>Joriy papkani Git repo'ga aylantirish</td></tr>
<tr><td><code>git status</code></td><td>Hozirgi holat — qaysi fayl o'zgargan</td></tr>
<tr><td><code>git add &lt;fayl&gt;</code></td><td>Faylni staging'ga qo'shish</td></tr>
<tr><td><code>git add .</code></td><td>Barcha o'zgarishlarni staging'ga</td></tr>
<tr><td><code>git commit -m "xabar"</code></td><td>Staging'dagilarni saqlash (snapshot)</td></tr>
<tr><td><code>git log</code></td><td>Commit tarixini ko'rish</td></tr>
<tr><td><code>git diff</code></td><td>Hali staging'da bo'lmagan o'zgarishlar</td></tr>
</table>

<h4>3. Commit xabarining qoidalari</h4>

<p>Yaxshi commit xabari — kelajakda siz va sherigingizning hayotini saqlaydi.</p>

<table>
<tr><th>❌ Yomon</th><th>✅ Yaxshi</th></tr>
<tr><td><code>"fix"</code></td><td><code>"Login formada email validatsiyasi to'g'rilandi"</code></td></tr>
<tr><td><code>"update"</code></td><td><code>"User schema'ga 'phone' maydoni qo'shildi"</code></td></tr>
<tr><td><code>"asdf"</code></td><td><code>"Header navigatsiyasi mobile'da to'g'rilandi"</code></td></tr>
</table>

<p>Pro qoidasi — <strong>Conventional Commits</strong> formati:</p>

<pre><code>&lt;tur&gt;: &lt;qisqa tavsif&gt;

[ixtiyoriy batafsil tavsif]</code></pre>

<p>Turlar: <code>feat</code>, <code>fix</code>, <code>refactor</code>, <code>docs</code>, <code>test</code>, <code>chore</code>, <code>perf</code>, <code>ci</code>.</p>

<pre><code>feat: foydalanuvchi profil sahifasi qo'shildi
fix: login xato xabar 2 marta chiqishi to'g'rilandi
refactor: API client alohida modulga ko'chirildi
docs: README ga setup qadamlari qo'shildi</code></pre>

<h4>4. Multi-line commit</h4>
<pre><code># -m'siz — vim/nano ochiladi (siz xohlagan)
git commit

# Yoki ikkita -m
git commit -m "feat: yangi profil sahifasi" \\
           -m "Bu commit foydalanuvchi profilini ko'rsatish va tahrirlashni qo'shadi"</code></pre>

<h4>5. Commit'ni tekshirish</h4>
<pre><code># Oxirgi commit'ning batafsil
git show

# Tarix to'liq (q bilan chiqing)
git log

# Bir qatorli — chiroyli
git log --oneline
# abc1234 (HEAD -&gt; main) feat: yangi profil sahifasi
# def5678 fix: login xato to'g'rilandi
# 9012abc Birinchi commit</code></pre>

<h4>6. .git papka — qora qutidan ichkari</h4>
<p>Qiziq bo'lsa, <code>ls .git/</code> qiling. U yerda: <code>HEAD</code> (joriy branch), <code>config</code> (sozlamalar), <code>objects/</code> (har commit, fayl SHA-1 hash bilan), <code>refs/</code> (branch'lar). Lekin <strong>hech qachon qo'l bilan tahrirlash kerak emas</strong> — buyruqlar orqali.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Git nima va nima uchun kerak</li>
<li>✅ <code>git config</code> bilan birinchi sozlash</li>
<li>✅ <code>git init</code> — repo yaratish</li>
<li>✅ 3 ta hudud: Working / Staging / Repository</li>
<li>✅ <code>git status</code>, <code>git add</code>, <code>git commit -m</code></li>
<li>✅ <code>git log</code> bilan tarix</li>
<li>✅ Conventional Commits formati: <code>feat:</code>, <code>fix:</code>, va h.k.</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 1: Git nima va birinchi repo
# Maqsad: init → add → commit → log
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 0) Tekshirish va sozlash
# ─────────────────────────────────────────────────────────────────────

git --version
# git version 2.43.0 (siznikida boshqacha bo'lishi mumkin)

# Birinchi marta — ism va email
git config --global user.name "Olim Karimov"
git config --global user.email "olim@example.uz"

# Default branch — main
git config --global init.defaultBranch main

# Tekshirish
git config --list
git config user.name
git config user.email

# ─────────────────────────────────────────────────────────────────────
# 1) Yangi repo
# ─────────────────────────────────────────────────────────────────────

mkdir mening-loyiham
cd mening-loyiham

git init
# Initialized empty Git repository in .../mening-loyiham/.git/

# .git papka paydo bo'ldi
ls -la

# ─────────────────────────────────────────────────────────────────────
# 2) Birinchi fayl va commit
# ─────────────────────────────────────────────────────────────────────

# Fayl yaratamiz
echo "# Mening loyiham" > README.md
echo "Bu mening birinchi Git loyihalarim" >> README.md

# Status — Git nima ko'rdi?
git status
# On branch main
# No commits yet
# Untracked files:
#   README.md
# nothing added to commit but untracked files present

# Staging'ga qo'shamiz
git add README.md

# Yana status
git status
# Changes to be committed:
#   new file: README.md

# Commit
git commit -m "docs: birinchi README qo'shildi"
# [main (root-commit) abc1234] docs: birinchi README qo'shildi
#  1 file changed, 2 insertions(+)
#  create mode 100644 README.md

# Tarix
git log
# commit abc1234... (HEAD -> main)
# Author: Olim Karimov <olim@example.uz>
# Date: ...
#
#     docs: birinchi README qo'shildi

# Bir qatorli
git log --oneline

# ─────────────────────────────────────────────────────────────────────
# 3) Ko'p fayl, ko'p commit
# ─────────────────────────────────────────────────────────────────────

echo "print('Salom, Git!')" > main.py
echo "Hello from JS" > script.js

git status
# Untracked: main.py, script.js

# Hammasini birga
git add .

# Yoki alohida
# git add main.py
# git add script.js

git commit -m "feat: main.py va script.js qo'shildi"

# Tarix
git log --oneline
# def5678 (HEAD -> main) feat: main.py va script.js qo'shildi
# abc1234 docs: birinchi README qo'shildi

# ─────────────────────────────────────────────────────────────────────
# 4) Faylni o'zgartirish — modify
# ─────────────────────────────────────────────────────────────────────

# main.py ni o'zgartirib qo'yamiz
echo "print('Yangilangan salom!')" > main.py

git status
# modified: main.py

# Nimani aniq o'zgartirdik?
git diff
# - print('Salom, Git!')
# + print('Yangilangan salom!')

# Stage va commit
git add main.py
git commit -m "fix: main.py salom matni yangilandi"

# ─────────────────────────────────────────────────────────────────────
# 5) Multi-line commit (batafsil)
# ─────────────────────────────────────────────────────────────────────

echo "# Sozlamalar" > config.md

git add config.md
git commit -m "docs: sozlamalar fayli qo'shildi" \\
           -m "Bu commit foydalanuvchi sozlamalari uchun config.md faylini qo'shadi. Hozircha bo'sh — keyingi commitda ma'lumot to'ldiriladi."

# ─────────────────────────────────────────────────────────────────────
# 6) Tarix turli ko'rinishlarda
# ─────────────────────────────────────────────────────────────────────

git log                    # to'liq
git log --oneline          # qisqa
git log -n 3               # oxirgi 3
git log --author="Olim"    # faqat Olim'ning commitlari
git log --since="1 week ago"
git log --grep="fix"       # xabarda "fix" so'zi borlari

# Oxirgi commit'ning to'liq
git show

# Belgilangan commit
git show abc1234

# ─────────────────────────────────────────────────────────────────────
# 7) Ataylab xato — add'siz commit
# ─────────────────────────────────────────────────────────────────────

echo "yangi qator" >> README.md
git commit -m "test"
# nothing to commit, working tree clean
# (chunki staging area bo'sh — add qilmagansiz)

# To'g'risi:
git add README.md
git commit -m "docs: README ga yangi qator qo'shildi"
"""
L2_TEXT = """\
<h2>.gitignore, log, diff — tarix bilan ishlash</h2>

<pre class="mermaid">
flowchart LR
    F1[".env, node_modules,\nvenv, .pyc"] -->|.gitignore| IG["Git e'tibordan tashqari"]
    F2["main.py, README"] -->|kuzatiladi| TR["Git tarix"]
</pre>

<p>Birinchi darsda siz commit qila olasiz. Lekin <strong>nima'ni</strong> commit qilish kerak? <code>.env</code> ichida sirli kalitlar bor — uni commit qilsangiz, hammaga ko'rinadi. <code>node_modules/</code> — yuz minglab fayllar, hech kerak emas. Bu darsda 2 ta hayotiy ko'nikma: <strong>ignoring</strong> (.gitignore) va <strong>tarix bilan ishlash</strong> (log, diff, show).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — .gitignore</h4>
<pre><code># .gitignore fayl yarating (loyiha ildizida)
cat &gt; .gitignore &lt;&lt;EOF
# Secret files
.env
.env.local
*.key

# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
*.log
EOF

git add .gitignore
git commit -m "chore: .gitignore qo'shildi"</code></pre>

<p>Endi bu fayl/papkalar Git tomonidan <em>e'tibordan tashqari</em>. <code>git status</code> ularni ko'rmaydi.</p>

<h4>BLOKA 2 — log: ko'p qiziqarli</h4>
<pre><code># Standart
git log

# Bir qatorli, chiroyli
git log --oneline --graph --decorate --all

# Filtr
git log --author="Olim"
git log --since="2 weeks ago" --until="yesterday"
git log --grep="fix"           # commit xabarda "fix" so'zi
git log -p                     # har commit'ning to'liq diff'i
git log --stat                 # qaysi fayl o'zgargani
git log -n 5                   # oxirgi 5</code></pre>

<h4>BLOKA 3 — diff: nima o'zgargan?</h4>
<pre><code># Working Directory vs Staging Area (hali add qilmaganlar)
git diff

# Staging vs oxirgi commit (add qilingan, lekin commit emas)
git diff --staged
# yoki:
git diff --cached

# Working vs oxirgi commit (hammasi)
git diff HEAD

# Bitta faylga
git diff main.py
git diff --staged main.py

# 2 ta commit orasidagi farq
git diff abc1234 def5678</code></pre>

<h3>🐛 Ataylab xato (juda xavfli)</h3>
<pre><code>git add .
git commit -m "feat: API integration"
git push
# ... 5 daqiqadan keyin:
# 😱 .env fayl push bo'lib ketdi, ichida AWS access key!</code></pre>

<p><strong>Sabab:</strong> <code>.gitignore</code> yaratishni unutgansiz. Git secret fayllarni bilmaydi — siz aytishingiz kerak.</p>

<p><strong>Yechim (oldindan oldini olish):</strong> Birinchi commit'dan oldin <code>.gitignore</code> yarating. <strong>Yechim (allaqachon push qilingan bo'lsa):</strong> Kalitni darhol rotation qiling (AWS console'da bekor qiling), keyin tarix tozalash (qiyin va xavfli — <code>git filter-repo</code> yoki BFG). <strong>Eng yaxshisi — oldindan oldini olish.</strong></p>

<h3>Endi tushuntiramiz</h3>

<h4>1. .gitignore qoidalari</h4>

<table>
<tr><th>Pattern</th><th>Ma'no</th></tr>
<tr><td><code>fayl.txt</code></td><td>Aynan shu fayl</td></tr>
<tr><td><code>*.log</code></td><td>.log bilan tugaganlar</td></tr>
<tr><td><code>logs/</code></td><td>logs nomli papka (har joyda)</td></tr>
<tr><td><code>/build</code></td><td>Faqat ildizdagi build (papka/fayl)</td></tr>
<tr><td><code>**/tmp</code></td><td>Har joyda tmp</td></tr>
<tr><td><code>!important.log</code></td><td>Bu faylni ignore qilma (istisno)</td></tr>
<tr><td><code># komment</code></td><td>komment</td></tr>
</table>

<h4>2. Tipik .gitignore namuna</h4>

<pre><code># OS
.DS_Store
Thumbs.db

# Editors
.vscode/
.idea/
*.swp
*.swo

# Secrets
.env
.env.*
!.env.example
*.pem
*.key

# Python
__pycache__/
*.py[cod]
venv/
.venv/
*.egg-info/
.pytest_cache/

# Node.js
node_modules/
npm-debug.log
yarn-error.log
.next/
dist/

# Logs
*.log
logs/

# Build
build/
out/</code></pre>

<h4>3. Allaqachon kuzatilgan faylni ignore qilish</h4>
<pre><code># Avval u kuzatilgan, endi ignore xohlaymiz
echo "config.json" &gt;&gt; .gitignore

# Tarixdan olib tashlash (lekin diskdan emas)
git rm --cached config.json

git commit -m "chore: config.json endi gitignore'da"</code></pre>

<h4>4. .gitignore'ni qaysi joyga?</h4>
<ul>
<li><strong>Loyiha .gitignore</strong> — loyiha ildizida, jamoaga umumiy</li>
<li><strong>Global .gitignore</strong> — har repo uchun (siz uchun: <code>.DS_Store</code>, <code>.vscode/</code>)</li>
</ul>

<pre><code># Global gitignore o'rnatish
git config --global core.excludesfile ~/.gitignore_global

# Va shu faylga yozing
echo ".DS_Store" &gt;&gt; ~/.gitignore_global
echo ".vscode/" &gt;&gt; ~/.gitignore_global</code></pre>

<h4>5. log batafsil — eng foydali bayroqlar</h4>

<table>
<tr><th>Flag</th><th>Vazifa</th></tr>
<tr><td><code>--oneline</code></td><td>Har commit — 1 qator</td></tr>
<tr><td><code>--graph</code></td><td>ASCII grafik (branchlar)</td></tr>
<tr><td><code>--all</code></td><td>Barcha branchlar</td></tr>
<tr><td><code>--decorate</code></td><td>Tag, branch nomlari</td></tr>
<tr><td><code>--stat</code></td><td>Fayllar va satrlar soni</td></tr>
<tr><td><code>-p</code></td><td>To'liq diff</td></tr>
<tr><td><code>--reverse</code></td><td>Eskidan yangiga (default — aksincha)</td></tr>
</table>

<p>Eng foydali alias:</p>
<pre><code>git config --global alias.lg "log --oneline --graph --decorate --all"

# Endi:
git lg</code></pre>

<h4>6. show — bir commit batafsil</h4>
<pre><code>git show HEAD            # oxirgi commit
git show HEAD~1          # oxirgi'dan oldingi
git show HEAD~3          # 3 ta oldingi
git show abc1234         # belgilangan
git show abc1234:main.py # o'sha commit'dagi main.py mazmuni</code></pre>

<h4>7. blame — qaysi qator kim tomonidan</h4>
<pre><code>git blame main.py
# abc1234 (Olim 2026-01-01) print("Salom")
# def5678 (Vali 2026-02-15) print("Yangilangan")</code></pre>

<p>Bu — debug uchun zarur: "shu bug qaysi commit'dan kelgan?" Javob — blame.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>.gitignore</code> — secret va keraksiz fayllarni Git'dan yashirish</li>
<li>✅ Tipik patterns: <code>*.log</code>, <code>node_modules/</code>, <code>.env</code></li>
<li>✅ Global gitignore — har repo uchun shaxsiy</li>
<li>✅ <code>git log --oneline --graph --all</code> — go'zal tarix</li>
<li>✅ <code>git diff</code> 3 xil (working/staged/HEAD)</li>
<li>✅ <code>git show</code> — bir commit batafsil</li>
<li>✅ <code>git blame</code> — har qator kim tomonidan</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 2: .gitignore, log, diff
# Maqsad: keraksiz fayllarni yashirish + tarix bilan ishlash
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) .gitignore yaratish
# ─────────────────────────────────────────────────────────────────────

cd mening-loyiham

# .gitignore — pattern'lar
cat > .gitignore <<EOF
# Secrets
.env
.env.*
!.env.example
*.key
*.pem

# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs and builds
*.log
dist/
build/
EOF

git add .gitignore
git commit -m "chore: .gitignore qo'shildi"

# ─────────────────────────────────────────────────────────────────────
# 2) Sinash — secret fayl
# ─────────────────────────────────────────────────────────────────────

echo "SECRET_KEY=abc123-very-secret" > .env

git status
# (.env ko'rinmaydi! gitignore ishladi)

# Tasodifan add qilishga urinsangiz:
git add .env
# Bu xato chiqarmaydi, lekin status'da ko'rinmaydi
# (gitignore'dagi fayllar add qilinmaydi)

# Tekshirish — Git nima ko'radi
git check-ignore -v .env
# .gitignore:2:.env  .env

# ─────────────────────────────────────────────────────────────────────
# 3) Tarix uchun ko'p commit yaratamiz
# ─────────────────────────────────────────────────────────────────────

# Commit 1
echo "def salom(ism): return f'Salom, {ism}!'" > main.py
git add main.py
git commit -m "feat: salom() funksiyasi qo'shildi"

# Commit 2
echo "def xayr(ism): return f'Xayr, {ism}!'" >> main.py
git add main.py
git commit -m "feat: xayr() funksiyasi qo'shildi"

# Commit 3
echo "if __name__ == '__main__': print(salom('Dunyo'))" >> main.py
git add main.py
git commit -m "feat: main blok qo'shildi"

# Commit 4
sed -i.bak "s/Salom/Assalomu alaykum/g" main.py
rm main.py.bak
git add main.py
git commit -m "refactor: rasmiyroq salomlashish"

# ─────────────────────────────────────────────────────────────────────
# 4) Log — turli ko'rinishlarda
# ─────────────────────────────────────────────────────────────────────

# Oddiy
git log

# Bir qatorli
git log --oneline

# Grafik bilan
git log --oneline --graph --all

# Filtr
git log --author="Olim"
git log --since="1 hour ago"
git log --grep="feat"
git log -n 3                  # oxirgi 3

# To'liq diff bilan
git log -p

# Faqat fayl statistika
git log --stat

# Alias yaratamiz — keyingilar uchun qulay
git config --global alias.lg "log --oneline --graph --decorate --all"

git lg

# ─────────────────────────────────────────────────────────────────────
# 5) Diff — nima o'zgargan?
# ─────────────────────────────────────────────────────────────────────

# Yangi o'zgarish (hali add'siz)
echo "# Yangi komment" >> main.py

git diff
# - if __name__ == '__main__': print(salom('Dunyo'))
# + if __name__ == '__main__': print(salom('Dunyo'))
# + # Yangi komment

# Add qilamiz
git add main.py

git diff             # bo'sh — working = staging
git diff --staged    # endi farq ko'rinadi
git diff HEAD        # working vs oxirgi commit (hammasi)

# Commit qilamiz
git commit -m "docs: komment qo'shildi"

# ─────────────────────────────────────────────────────────────────────
# 6) Show — bir commit batafsil
# ─────────────────────────────────────────────────────────────────────

# Oxirgi
git show

# 2 oldingi
git show HEAD~2

# Belgilangan SHA bilan
git show abc1234

# Aniq commit'dagi fayl mazmuni
git show HEAD:main.py

# ─────────────────────────────────────────────────────────────────────
# 7) Blame — qaysi qator kim tomonidan
# ─────────────────────────────────────────────────────────────────────

git blame main.py
# abc1234 (Olim 2026-06-08) def salom(ism):
# def5678 (Olim 2026-06-08) def xayr(ism):
# ...

# Aniq qatorlar (10-20)
git blame -L 10,20 main.py

# ─────────────────────────────────────────────────────────────────────
# 8) Tarix qidirish — log bilan
# ─────────────────────────────────────────────────────────────────────

# "salom" so'zi qaysi commit'da paydo bo'lgan?
git log -S "salom" --oneline

# Funksiya tarixini ko'rsatish
git log -L :salom:main.py

# ─────────────────────────────────────────────────────────────────────
# 9) Allaqachon kuzatilgan faylni ignore qilish
# ─────────────────────────────────────────────────────────────────────

# Faraz: config.json allaqachon commit qilingan
echo "config.json" >> .gitignore

# Tarixdan emas, hozirgi kuzatuvdan olib tashlash
# git rm --cached config.json

# Endi commit qilsangiz, Git uni unutadi
# git commit -m "chore: config.json endi gitignore'da"

# ─────────────────────────────────────────────────────────────────────
# 10) Global .gitignore (kompyuteringizdagi har repo uchun)
# ─────────────────────────────────────────────────────────────────────

git config --global core.excludesfile ~/.gitignore_global

cat >> ~/.gitignore_global <<EOF
.DS_Store
.vscode/
.idea/
Thumbs.db
EOF
"""
L3_TEXT = """\
<h2>Branching — branch, switch, merge</h2>

<pre class="mermaid">
gitGraph
    commit id: "A"
    commit id: "B"
    branch feature
    checkout feature
    commit id: "C"
    commit id: "D"
    checkout main
    merge feature
</pre>

<p>Branch (shox) — bu Git'ning eng kuchli imkoniyatlaridan biri. Bitta loyihaning <strong>yondosh versiyalari</strong>. Asosiy versiyaga tegmasdan yangi feature qo'shasiz, bug tuzatasiz, eksperiment qilasiz. Tayyor bo'lganda — asosiyga qo'shasiz (<strong>merge</strong>).</p>

<p>Bu — har dasturchining kunlik ishi. <code>main</code>'da hech qachon to'g'ridan-to'g'ri ishlamaysiz. Har vazifa uchun yangi branch.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — branch yaratish va o'tish</h4>
<pre><code># Hozirgi branchni ko'ring
git branch
# * main

# Yangi branch yaratamiz
git branch feature/login

# Branchlar ro'yxati
git branch
#   feature/login
# * main

# Branch'ga o'tish
git switch feature/login
# Switched to branch 'feature/login'

# Yoki bitta buyruq bilan yaratib o'tish:
git switch -c feature/profile</code></pre>

<h4>BLOKA 2 — branch'da ishlash</h4>
<pre><code># Hozir feature/profile branchidamiz
git branch
#   feature/login
# * feature/profile
#   main

# Yangi commit qilamiz
echo "def profil(): pass" &gt;&gt; main.py
git add main.py
git commit -m "feat: profil() funksiya skelet"

echo "def profil(id): return {'id': id, 'ism': 'X'}" &gt; profil.py
git add profil.py
git commit -m "feat: profil() implementatsiyasi"

# Tarix faqat shu branchda
git log --oneline
# def5678 (HEAD -&gt; feature/profile) feat: profil() implementatsiyasi
# abc1234 feat: profil() funksiya skelet
# 9012345 (main) ... (oldin)

# main'ga qaytamiz — profil.py YOQ
git switch main
ls
# (profil.py yo'q — chunki u feature/profile branchda)</code></pre>

<h4>BLOKA 3 — merge</h4>
<pre><code># main'da turibmiz
git switch main

# feature/profile ni main'ga qo'shamiz
git merge feature/profile
# Fast-forward
#  profil.py | 1 +
#  main.py   | 1 +

# Endi profil.py main'da
ls
# main.py  profil.py

# Tarix
git log --oneline
# def5678 (HEAD -&gt; main, feature/profile) feat: profil() implementatsiyasi
# abc1234 feat: profil() funksiya skelet
# 9012345 ...

# Branch endi kerak emas — o'chirish
git branch -d feature/profile
# Deleted branch feature/profile (was def5678).</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Branch'da o'zgartirish qildingiz, lekin commit qilmagansiz
git switch main
# error: Your local changes to the following files would be overwritten by checkout:
#   main.py
# Please commit your changes or stash them before you switch branches.</code></pre>

<p><strong>Sabab:</strong> Hozirgi branch'da commit qilinmagan o'zgarishlar bor. Boshqa branch'ga o'tish — ularni yo'qotishi mumkin. Git buni oldini oladi.</p>

<p><strong>2 yechim:</strong></p>
<ol>
<li><strong>Commit qiling</strong> (yarim ishlangan bo'lsa ham — keyin amend bilan to'g'rilash mumkin)</li>
<li><strong>Stash qiling</strong> (vaqtinchalik saqlash, 7-darsda)</li>
</ol>

<h3>Endi tushuntiramiz</h3>

<h4>1. Branch — bu nima aslida?</h4>

<p>Branch — bu shunchaki <strong>commit'ga ishora qiluvchi pointer</strong>. Yangi commit qilsangiz, pointer keyingiga ko'chadi. Branch'lar bepul va tez (<code>git branch</code> — 1 ms).</p>

<pre><code>main:     A --- B --- C
                       \\
feature:                D --- E
                              ^
                              HEAD</code></pre>

<h4>2. Asosiy buyruqlar</h4>
<table>
<tr><th>Buyruq</th><th>Vazifa</th></tr>
<tr><td><code>git branch</code></td><td>Branchlar ro'yxati</td></tr>
<tr><td><code>git branch &lt;nom&gt;</code></td><td>Yangi branch (lekin o'tmaydi)</td></tr>
<tr><td><code>git switch &lt;nom&gt;</code></td><td>Branch'ga o'tish</td></tr>
<tr><td><code>git switch -c &lt;nom&gt;</code></td><td>Yaratib darhol o'tish</td></tr>
<tr><td><code>git merge &lt;nom&gt;</code></td><td>Boshqa branchni hozirgiga qo'shish</td></tr>
<tr><td><code>git branch -d &lt;nom&gt;</code></td><td>Branchni o'chirish (xavfsiz)</td></tr>
<tr><td><code>git branch -D &lt;nom&gt;</code></td><td>Branchni majburiy o'chirish</td></tr>
</table>

<h4>3. Branch nomlash konventsiyasi</h4>

<table>
<tr><th>Pattern</th><th>Misol</th></tr>
<tr><td><code>feature/&lt;nom&gt;</code></td><td><code>feature/login</code>, <code>feature/dark-mode</code></td></tr>
<tr><td><code>fix/&lt;nom&gt;</code></td><td><code>fix/login-bug</code></td></tr>
<tr><td><code>refactor/&lt;nom&gt;</code></td><td><code>refactor/api-client</code></td></tr>
<tr><td><code>chore/&lt;nom&gt;</code></td><td><code>chore/update-deps</code></td></tr>
<tr><td><code>hotfix/&lt;nom&gt;</code></td><td><code>hotfix/payment-crash</code></td></tr>
</table>

<h4>4. checkout vs switch</h4>
<p>Eski buyruq: <code>git checkout</code> (ko'p ish qilardi — branch ham, fayl ham). Zamonaviy:</p>

<table>
<tr><th>Eski</th><th>Yangi</th></tr>
<tr><td><code>git checkout &lt;branch&gt;</code></td><td><code>git switch &lt;branch&gt;</code></td></tr>
<tr><td><code>git checkout -b &lt;branch&gt;</code></td><td><code>git switch -c &lt;branch&gt;</code></td></tr>
<tr><td><code>git checkout -- &lt;fayl&gt;</code></td><td><code>git restore &lt;fayl&gt;</code></td></tr>
</table>

<p>Yangilarini ishlating — aniqroq va xavfsizroq.</p>

<h4>5. Merge turlari</h4>

<p><strong>Fast-forward</strong> — main hech o'zgarmagan paytda feature qilingan:</p>
<pre><code>Avval:           main: A --- B
                              \\
                  feature:     C --- D

Merge keyin:     main:    A --- B --- C --- D   (faqat pointer surildi)</code></pre>

<p><strong>Merge commit (3-way merge)</strong> — main va feature parallel rivojlangan:</p>
<pre><code>Avval:           main:    A --- B --- E
                                \\
                  feature:       C --- D

Merge keyin:     main:    A --- B --- E ----- M
                                \\           /
                                 C --- D ---
                                 (M — merge commit)</code></pre>

<p>Merge commit avtomatik yaratiladi. Xabari: <code>Merge branch 'feature/profile'</code>. Ba'zilar buni xohlamaydi (linear tarix) — 8-darsda <code>rebase</code>'ni o'rganamiz.</p>

<h4>6. Tipik kunlik workflow</h4>

<pre><code># 1. main'dan yangi branch
git switch main
git pull               # so'nggi versiya (4-darsda)
git switch -c feature/yangi-narsa

# 2. Ishlang, commit qiling
# ... kod yozasiz ...
git add .
git commit -m "feat: yangi narsa qo'shildi"

# 3. main'ga merge
git switch main
git merge feature/yangi-narsa

# 4. Branchni o'chiring
git branch -d feature/yangi-narsa</code></pre>

<h4>7. Hozir qaysi branchdaman?</h4>
<pre><code>git branch                # ro'yxat, * bilan
git status                # boshida ko'rsatadi
git rev-parse --abbrev-ref HEAD   # faqat nom

# Terminalga branchni doim ko'rsatish — git-prompt yoki oh-my-zsh</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Branch — yondosh versiya, pointer commit'ga</li>
<li>✅ <code>git branch</code>, <code>git switch</code>, <code>git switch -c</code></li>
<li>✅ <code>git merge</code> — branchni qo'shish (fast-forward yoki merge commit)</li>
<li>✅ Branch nomlash: <code>feature/...</code>, <code>fix/...</code>, <code>refactor/...</code></li>
<li>✅ <code>git switch</code> tavsiya (eski <code>checkout</code> emas)</li>
<li>✅ Commit qilmagan o'zgarishlarda branch o'zgartirib bo'lmaydi</li>
<li>✅ Kunlik workflow: yangi branch → commit → merge → delete</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 3: Branching — branch, switch, merge
# ════════════════════════════════════════════════════════════════════

cd mening-loyiham

# ─────────────────────────────────────────────────────────────────────
# 1) Hozirgi branchni ko'rish
# ─────────────────────────────────────────────────────────────────────

git branch
# * main

git status
# On branch main

# ─────────────────────────────────────────────────────────────────────
# 2) Yangi branch yaratish va o'tish
# ─────────────────────────────────────────────────────────────────────

# Variant A: 2 ta buyruq
git branch feature/login
git switch feature/login

# Variant B: 1 buyruq (tavsiya)
git switch -c feature/profile

# Tekshirish
git branch
#   feature/login
# * feature/profile
#   main

# ─────────────────────────────────────────────────────────────────────
# 3) Branch'da ishlash
# ─────────────────────────────────────────────────────────────────────

# Hozir feature/profile branchidamiz
echo "def profil(id):" > profil.py
echo "    return {'id': id, 'ism': 'Olim'}" >> profil.py

git add profil.py
git commit -m "feat: profil() funksiyasi qo'shildi"

echo "def yangilash(id, ism):" >> profil.py
echo "    return {'id': id, 'ism': ism}" >> profil.py

git add profil.py
git commit -m "feat: yangilash() funksiyasi"

# Tarix faqat shu branchda
git log --oneline
# def5678 (HEAD -> feature/profile) feat: yangilash()
# abc1234 feat: profil()
# 9012345 ... (main'dan keyin)

# ─────────────────────────────────────────────────────────────────────
# 4) main'ga qaytish — profil.py YO'Q
# ─────────────────────────────────────────────────────────────────────

git switch main

ls
# main.py  README.md
# (profil.py yo'q — feature/profile branchda)

git log --oneline
# 9012345 ... (oldingi commit'lar)
# (feature/profile commitlari ko'rinmaydi)

# ─────────────────────────────────────────────────────────────────────
# 5) Merge — fast-forward
# ─────────────────────────────────────────────────────────────────────

# main hech o'zgarmagan, feature ilgariga ketgan → fast-forward
git merge feature/profile
# Fast-forward
#  profil.py | 3 +++
#  1 file changed, 3 insertions(+)

# Endi profil.py main'da
ls
# main.py  profil.py  README.md

git log --oneline
# def5678 (HEAD -> main, feature/profile) feat: yangilash()
# abc1234 feat: profil()
# 9012345 ...

# ─────────────────────────────────────────────────────────────────────
# 6) Branchni o'chirish
# ─────────────────────────────────────────────────────────────────────

git branch -d feature/profile
# Deleted branch feature/profile

git branch
# * main
# feature/login (hali bor)

# ─────────────────────────────────────────────────────────────────────
# 7) Merge commit (3-way merge) — main ham o'zgargan
# ─────────────────────────────────────────────────────────────────────

# Yana yangi branch
git switch -c feature/api

echo "def get_api(): return 'API data'" > api.py
git add api.py
git commit -m "feat: API client"

# main'ga qaytib boshqa o'zgarish
git switch main
echo "# Loyiha yangiliklar" > CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: CHANGELOG qo'shildi"

# Endi ikkalasi ham ilgariga ketgan
git log --oneline --graph --all
# * abc111 (HEAD -> main) docs: CHANGELOG
# | * def222 (feature/api) feat: API client
# |/
# * 9012345 ...

# Merge — endi merge commit yaratiladi
git merge feature/api
# Merge made by the 'ort' strategy.

git log --oneline --graph --all
# *   M (HEAD -> main) Merge branch 'feature/api'
# |\\
# | * def222 (feature/api) feat: API client
# * | abc111 docs: CHANGELOG
# |/
# * 9012345 ...

# ─────────────────────────────────────────────────────────────────────
# 8) Branch'da o'zgarishlar bor — switch bloklanadi
# ─────────────────────────────────────────────────────────────────────

echo "test" >> main.py
git switch feature/login
# error: Your local changes... would be overwritten

# Yechim 1: commit
git add main.py
git commit -m "WIP: hali tugamadi"

# Yechim 2: stash (7-darsda)
# git stash
# git switch feature/login

# ─────────────────────────────────────────────────────────────────────
# 9) Branch nomlarini renomlash
# ─────────────────────────────────────────────────────────────────────

git switch feature/login

# Joriy branchni rename
git branch -m feature/auth

# Boshqa branchni rename
git branch -m feature/login feature/login-form
"""
R1_TEXT = """\
<h2>R1 — Modul 1 takrorlash: Kunlik commit jurnal</h2>

<p>Modul 1 ning hammasi birga: <strong>init, add, commit, gitignore, log, diff, branch, merge</strong>. Bu safar — sizning shaxsiy loyihangiz. Har kun nima qilganingizni Git bilan saqlaydigan jurnal.</p>

<p>Bu loyiha 2 maqsadli: Git'ni mustahkamlash + haqiqiy foydali narsa qurish (kun davomida o'ylangan g'oyalar, qilingan ishlar).</p>

<h3>Loyihaning maqsadi</h3>

<p>3 ta papkali jurnal:</p>
<pre><code>kundalik/
├── README.md
├── .gitignore
├── 2026/
│   ├── 06/
│   │   ├── 08.md
│   │   ├── 09.md
│   │   └── 10.md
└── shablonlar/
    └── kun-shabloni.md</code></pre>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Loyihani boshlash</h4>
<ul>
<li><code>kundalik</code> papkasi yarating</li>
<li><code>git init</code></li>
<li>README.md (loyiha haqida)</li>
<li>.gitignore (.DS_Store, .vscode/, *.tmp)</li>
<li>Birinchi commit: <code>chore: loyiha boshlash</code></li>
</ul>

<h4>Vazifa 2 — Shablon yaratish</h4>
<p><code>shablonlar/kun-shabloni.md</code>:</p>
<pre><code># &lt;Sana&gt;

## 🎯 Bugun nima qildim
- ...

## 🐛 Qiyinchiliklar
- ...

## 💡 Yangi o'rganganlar
- ...

## 📋 Ertaga
- ...</code></pre>

<p>Commit: <code>feat: kun shabloni yaratildi</code></p>

<h4>Vazifa 3 — Branch'da yangi feature</h4>
<ul>
<li>Yangi branch: <code>feature/teglar</code></li>
<li>README.md ga "Teglar" bo'limini qo'shing: <code>#kod</code>, <code>#kitob</code>, <code>#ish</code>...</li>
<li>Shablonga "## 🏷️ Teglar" qatorini qo'shing</li>
<li>Commit, main'ga merge, branchni o'chiring</li>
</ul>

<h4>Vazifa 4 — 5 kunlik yozuv</h4>
<p>Har kun uchun fayl: <code>2026/06/08.md</code>, <code>09.md</code>, ... 12.md.</p>
<p>Har kun alohida commit: <code>docs(daily): 08-iyun yozuv</code>, va h.k.</p>

<h4>Vazifa 5 — Tahrirlash va diff</h4>
<ul>
<li>08.md ni tahrirlang (qo'shimcha qator)</li>
<li><code>git diff</code> bilan o'zgarishni ko'ring</li>
<li>Commit: <code>docs(daily): 08-iyun yangilandi</code></li>
</ul>

<h4>Vazifa 6 — Tarix tahlili</h4>
<p>Quyidagi savollarga javob bering (faylda, masalan, <code>tarix-tahlili.md</code>):</p>
<ul>
<li><code>git log --oneline</code> — jami nechta commit?</li>
<li><code>git log --stat</code> — eng katta o'zgarish qaysi kun edi?</li>
<li><code>git log --grep="feat"</code> — nechta feature commit?</li>
<li><code>git blame README.md</code> — qaysi qator qaysi commit'dan?</li>
</ul>

<h4>Vazifa 7 — .gitignore sinash</h4>
<p>Tasodifan <code>shablon.tmp</code> faylini yarating. <code>git status</code> uni ko'rmasligi kerak (gitignore'da <code>*.tmp</code> bor).</p>

<h3>🐛 Ataylab qiyin: branch'da unutilgan o'zgarish</h3>

<p>Senariy: <code>feature/teglar</code> branch'da turibsiz. Yangi qator yozdingiz, lekin commit qilishni unutdingiz. <code>git switch main</code> qilmoqchisiz...</p>

<p>Nima bo'ladi? Qanday yechasiz? (2 ta variant — javobni hisobotda yozing)</p>

<h3>Yechim sketch</h3>

<details>
<summary>Yo'l xaritasi — avval o'zingiz urinib ko'ring!</summary>
<pre><code># Vazifa 1
mkdir kundalik && cd kundalik
git init
echo "# Kundalik" &gt; README.md
echo "Bu mening kundalik commit jurnali" &gt;&gt; README.md
cat &gt; .gitignore &lt;&lt;EOF
.DS_Store
.vscode/
*.tmp
EOF
git add .
git commit -m "chore: loyiha boshlash"

# Vazifa 2
mkdir shablonlar
cat &gt; shablonlar/kun-shabloni.md &lt;&lt;EOF
# &lt;Sana&gt;
## 🎯 Bugun
## 🐛 Qiyinchiliklar
## 💡 O'rgandim
## 📋 Ertaga
EOF
git add .
git commit -m "feat: kun shabloni"

# Vazifa 3 — branch
git switch -c feature/teglar
echo "" &gt;&gt; shablonlar/kun-shabloni.md
echo "## 🏷️ Teglar" &gt;&gt; shablonlar/kun-shabloni.md
echo "" &gt;&gt; README.md
echo "## Teglar" &gt;&gt; README.md
echo "- #kod  #kitob  #ish" &gt;&gt; README.md
git add .
git commit -m "feat(teglar): teglar tizimi qo'shildi"
git switch main
git merge feature/teglar
git branch -d feature/teglar

# Vazifa 4
mkdir -p 2026/06
for kun in 08 09 10 11 12; do
  cp shablonlar/kun-shabloni.md 2026/06/$kun.md
  sed -i.bak "s/&lt;Sana&gt;/2026-06-$kun/" 2026/06/$kun.md
  rm 2026/06/$kun.md.bak
  git add 2026/06/$kun.md
  git commit -m "docs(daily): $kun-iyun yozuv"
done</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 1 ning hammasi birga: init, gitignore, commit, log, branch, merge</li>
<li>✅ Real loyihada Git ishlatish — kun davomida</li>
<li>✅ Conventional commits formati amaliyot</li>
<li>✅ Branch workflow — kichik feature'larni alohida ishlash</li>
<li>✅ Tarix tahlili — log, blame, stat</li>
</ul>
"""

R1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 1: Kunlik commit jurnal
# Modul 1: init + gitignore + add + commit + branch + merge
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# Vazifa 1: loyihani boshlash
# ─────────────────────────────────────────────────────────────────────

mkdir kundalik && cd kundalik

git init

cat > README.md <<EOF
# Kundalik

Mening kundalik commit jurnali. Git bilan o'rganaman.

## Struktura

- 2026/MM/DD.md — har kun yozuv
- shablonlar/ — kun shabloni
EOF

cat > .gitignore <<EOF
# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp

# Vaqtinchalik
*.tmp
*.bak
EOF

git add .
git commit -m "chore: loyiha boshlash"

# ─────────────────────────────────────────────────────────────────────
# Vazifa 2: shablon
# ─────────────────────────────────────────────────────────────────────

mkdir shablonlar

cat > shablonlar/kun-shabloni.md <<'EOF'
# <Sana>

## 🎯 Bugun nima qildim
-

## 🐛 Qiyinchiliklar
-

## 💡 Yangi o'rganganlar
-

## 📋 Ertaga
-
EOF

git add shablonlar/
git commit -m "feat: kun shabloni yaratildi"

# ─────────────────────────────────────────────────────────────────────
# Vazifa 3: feature/teglar branch
# ─────────────────────────────────────────────────────────────────────

git switch -c feature/teglar

# Shablonga teglar bo'limi
cat >> shablonlar/kun-shabloni.md <<'EOF'

## 🏷️ Teglar
-
EOF

# README ga teglar
cat >> README.md <<'EOF'

## Teglar

Har yozuvda foydalanish mumkin:
- `#kod` — dasturlash bilan bog'liq
- `#kitob` — o'qigan
- `#ish` — ish vazifalari
- `#sport` — jismoniy tarbiya
EOF

git add .
git commit -m "feat(teglar): teglar tizimi qo'shildi"

# main'ga qaytib merge
git switch main
git merge feature/teglar
git branch -d feature/teglar

# Tekshirish
git log --oneline --graph --all

# ─────────────────────────────────────────────────────────────────────
# Vazifa 4: 5 kunlik yozuv
# ─────────────────────────────────────────────────────────────────────

mkdir -p 2026/06

for kun in 08 09 10 11 12; do
  cp shablonlar/kun-shabloni.md 2026/06/$kun.md
  # macOS sed
  sed -i.bak "s/<Sana>/2026-06-$kun/" 2026/06/$kun.md
  rm 2026/06/$kun.md.bak
  git add 2026/06/$kun.md
  git commit -m "docs(daily): $kun-iyun yozuv"
done

# Linux sed (agar -i.bak ishlamasa):
# sed -i "s/<Sana>/2026-06-$kun/" 2026/06/$kun.md

# ─────────────────────────────────────────────────────────────────────
# Vazifa 5: tahrir + diff
# ─────────────────────────────────────────────────────────────────────

# 08.md ga to'liq mazmun yozamiz
cat > 2026/06/08.md <<'EOF'
# 2026-06-08

## 🎯 Bugun nima qildim
- Git va GitHub kursini boshlashdim
- Birinchi commit qildim — juda zo'r tuyildi!
- 3 ta branch yaratdim va merge qildim

## 🐛 Qiyinchiliklar
- `git add` ni unutib `commit` qilishga urinardim
- Branch o'zgartirishda "uncommitted changes" xato chiqdi

## 💡 Yangi o'rganganlar
- Conventional Commits formati: `feat:`, `fix:`, `chore:`
- `git log --oneline --graph` — chiroyli tarix
- .gitignore qoidalari

## 📋 Ertaga
- GitHub account ochish
- SSH key sozlash

## 🏷️ Teglar
- #kod #git #boshlanish
EOF

# Diff'ni ko'rish
git diff 2026/06/08.md

# Commit
git add 2026/06/08.md
git commit -m "docs(daily): 08-iyun yozuv to'ldirildi"

# ─────────────────────────────────────────────────────────────────────
# Vazifa 6: tarix tahlili
# ─────────────────────────────────────────────────────────────────────

cat > tarix-tahlili.md <<'EOF'
# Tarix tahlili

## Jami commit'lar
EOF

echo '```' >> tarix-tahlili.md
git log --oneline | wc -l >> tarix-tahlili.md
echo '```' >> tarix-tahlili.md

cat >> tarix-tahlili.md <<'EOF'

## Statistika
EOF

echo '```' >> tarix-tahlili.md
git log --stat | tail -50 >> tarix-tahlili.md
echo '```' >> tarix-tahlili.md

git add tarix-tahlili.md
git commit -m "docs: tarix tahlili"

# ─────────────────────────────────────────────────────────────────────
# Vazifa 7: .gitignore sinash
# ─────────────────────────────────────────────────────────────────────

echo "test" > test.tmp

git status
# (test.tmp YO'Q — gitignore ishladi)

git check-ignore -v test.tmp
# .gitignore:10:*.tmp  test.tmp

rm test.tmp

# ─────────────────────────────────────────────────────────────────────
# Yakuniy holat
# ─────────────────────────────────────────────────────────────────────

git log --oneline --graph --all

# Tipik natija:
# * abc123 (HEAD -> main) docs: tarix tahlili
# * def456 docs(daily): 08-iyun yozuv to'ldirildi
# * ...
# * ghi789 docs(daily): 12-iyun yozuv
# ...
# * jkl012 feat(teglar): teglar tizimi qo'shildi
# * mno345 feat: kun shabloni
# * pqr678 chore: loyiha boshlash
"""
L4_TEXT = """\
<h2>GitHub, SSH, remote — birinchi push</h2>

<pre class="mermaid">
flowchart LR
    L["Local repo\n(sizning kompyuter)"] -->|git push| R["Remote: origin\n(GitHub.com)"]
    R -->|git pull| L
    R -->|git clone| NEW["Yangi kompyuter"]
</pre>

<p>Hozirgacha hammasi <em>lokal</em> edi — faqat sizning kompyuteringizda. Endi GitHub'ga bog'lanamiz. <strong>GitHub</strong> — bu Git repolarini internetda saqlovchi platforma. Sherigingiz bilan birga ishlash, backup, portfolio — hammasi shu yerda.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — GitHub account va SSH key</h4>

<p>1. <a href="https://github.com">github.com</a> ga ro'yxatdan o'ting (bepul).</p>

<p>2. SSH key yarating (kompyuteringizdan password'siz GitHub'ga bog'lanish uchun):</p>

<pre><code># SSH key yaratish
ssh-keygen -t ed25519 -C "olim@example.uz"
# Enter file in which to save the key (~/.ssh/id_ed25519): [Enter]
# Enter passphrase: [Enter yoki kuchli parol]

# Public key'ni nusxalash
cat ~/.ssh/id_ed25519.pub
# ssh-ed25519 AAAA... olim@example.uz</code></pre>

<p>3. GitHub'da: <strong>Settings → SSH and GPG keys → New SSH key</strong>. Public key'ni paste qiling.</p>

<p>4. Sinash:</p>
<pre><code>ssh -T git@github.com
# Hi olim! You've successfully authenticated...</code></pre>

<h4>BLOKA 2 — GitHub'da repo yaratish va ulash</h4>

<p>1. GitHub'da: <strong>New repository</strong> → nom yozing (masalan, <code>mening-loyiham</code>) → <strong>Create</strong>. README qo'shmang (sizda allaqachon bor).</p>

<p>2. Lokal repo'ni GitHub'ga bog'lang:</p>

<pre><code>cd mening-loyiham

# Remote qo'shamiz — "origin" — standart nom
git remote add origin git@github.com:olim/mening-loyiham.git

# Tekshirish
git remote -v
# origin  git@github.com:olim/mening-loyiham.git (fetch)
# origin  git@github.com:olim/mening-loyiham.git (push)

# Birinchi push — -u bilan upstream sozlaymiz
git push -u origin main
# Total 6 (delta 0), reused 0 (delta 0)
# To github.com:olim/mening-loyiham.git
#  * [new branch]      main -&gt; main
# branch 'main' set up to track 'origin/main'.</code></pre>

<p>Endi GitHub'da yangilang sahifani — kodingiz ko'rinadi!</p>

<h4>BLOKA 3 — pull va clone</h4>

<pre><code># Boshqa kompyuter / hamkasbingiz uchun
git clone git@github.com:olim/mening-loyiham.git
cd mening-loyiham
# Hammasi to'liq — fayllar, tarix, branchlar

# Yangiliklar olish (boshqa joydan kelgan o'zgarishlar)
git pull
# Already up to date.

# Yoki agar yangilik bor:
# Updating abc123..def456
# Fast-forward
#  ...</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>git push
# To github.com:olim/mening-loyiham.git
#  ! [rejected]        main -&gt; main (fetch first)
# error: failed to push some refs to 'github.com:olim/mening-loyiham.git'
# hint: Updates were rejected because the remote contains work that you do
# hint: not have locally.</code></pre>

<p><strong>Sabab:</strong> GitHub'da yangiliklar bor (boshqa joydan, masalan, GitHub UI orqali commit qilingan), siz pull qilmagansiz. Push qilsangiz — boshqa odam ishini bekor qilasiz. Git buni bloklaydi.</p>

<p><strong>Yechim:</strong></p>
<pre><code>git pull          # avval olib keling
# (agar conflict bo'lsa, 6-darsda)
git push          # endi push</code></pre>

<p><strong>NIMA ASLO QILMASLIK kerak:</strong> <code>git push --force</code> (boshqalarning ishini o'chiradi). Faqat shaxsiy branch'da, ehtiyot bilan.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. SSH vs HTTPS</h4>

<table>
<tr><th></th><th>SSH</th><th>HTTPS</th></tr>
<tr><td>URL</td><td><code>git@github.com:user/repo.git</code></td><td><code>https://github.com/user/repo.git</code></td></tr>
<tr><td>Auth</td><td>SSH key (bir marta sozlaysiz)</td><td>Personal Access Token (har push uchun)</td></tr>
<tr><td>Tavsiya</td><td>✅ kunlik ishlash uchun</td><td>Faqat birinchi marta clone uchun</td></tr>
</table>

<p>SSH key sozlangach — har push/pull'da password yo'q.</p>

<h4>2. Remote — pultni boshqarish</h4>

<table>
<tr><th>Buyruq</th><th>Vazifa</th></tr>
<tr><td><code>git remote -v</code></td><td>Remote'lar ro'yxati</td></tr>
<tr><td><code>git remote add &lt;nom&gt; &lt;url&gt;</code></td><td>Yangi remote</td></tr>
<tr><td><code>git remote remove &lt;nom&gt;</code></td><td>O'chirish</td></tr>
<tr><td><code>git remote set-url &lt;nom&gt; &lt;url&gt;</code></td><td>URL o'zgartirish</td></tr>
<tr><td><code>git remote rename &lt;eski&gt; &lt;yangi&gt;</code></td><td>Rename</td></tr>
</table>

<p><strong>origin</strong> — Git'ning konvensional nomi. Ko'p remote bo'lishi mumkin (origin + upstream — 5-darsda fork bilan).</p>

<h4>3. push qoidalari</h4>

<pre><code># Birinchi marta — -u bilan upstream sozlash
git push -u origin main

# Keyingi safarlari — qisqa
git push

# Boshqa branchni
git push origin feature/login

# Hammasini
git push --all

# Force push (XAVFLI — boshqa work'ni o'chirishi mumkin)
git push --force-with-lease    # xavfsizroq variant</code></pre>

<h4>4. pull = fetch + merge</h4>

<pre><code># Bu ikkita bilan teng:
git pull origin main

# 1. Olib kelish (local'ga merge qilmasdan)
git fetch origin

# 2. Merge qilish
git merge origin/main</code></pre>

<p><code>fetch</code> avval ko'rib chiqish uchun yaxshi (nima yangiliklar bor?), keyin merge.</p>

<h4>5. clone — to'liq nusxa</h4>

<pre><code># Yangi joyga clone
git clone git@github.com:user/repo.git

# Boshqa nom bilan
git clone git@github.com:user/repo.git mening-papka

# Faqat oxirgi commit (tezroq, kichikroq)
git clone --depth 1 git@github.com:user/repo.git

# Belgilangan branch
git clone -b develop git@github.com:user/repo.git</code></pre>

<h4>6. README.md — birinchi taassurot</h4>

<p>Har GitHub repo'da <code>README.md</code> birinchi ko'rinadi. Yaxshi README:</p>

<pre><code># Loyiha nomi

Bir satrli tavsif — bu nima qiladi?

## Tezda boshlash

```bash
git clone ...
cd loyiha
npm install
npm run dev
```

## Xususiyatlar
- ...

## Texnologiyalar
- React, Node.js, PostgreSQL

## Litsenziya
MIT</code></pre>

<h4>7. GitHub'ga professional profil</h4>

<ul>
<li>📸 Avatar (chiroyli foto)</li>
<li>📝 README profile (sizning <code>username/username</code> repo'si)</li>
<li>📌 Pinned repos (yaxshi loyihalar)</li>
<li>🏆 Contribution graph (yashil kvadratchalar)</li>
<li>⭐ Star berish — boshqa loyihalarni saqlash</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ GitHub account + SSH key sozlash</li>
<li>✅ <code>git remote add origin ...</code></li>
<li>✅ <code>git push -u origin main</code> (birinchi marta)</li>
<li>✅ <code>git pull</code> = fetch + merge</li>
<li>✅ <code>git clone</code> — boshqa joyga yoki yangi kompyuterga</li>
<li>✅ Push'da reject — pull qilish kerak (force emas)</li>
<li>✅ Yaxshi README — loyihaning yuzi</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 4: GitHub, SSH, remote
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) SSH key yaratish va GitHub'ga qo'shish
# ─────────────────────────────────────────────────────────────────────

# Avval — bormi?
ls ~/.ssh/
# id_ed25519, id_ed25519.pub (bor bo'lsa)

# Yo'q bo'lsa — yaratish
ssh-keygen -t ed25519 -C "olim@example.uz"
# Enter file in which to save the key: [Enter — default]
# Enter passphrase: [Enter yoki kuchli parol]

# Public key'ni ko'rsatish
cat ~/.ssh/id_ed25519.pub
# ssh-ed25519 AAAAC3NzaC1lZDI1... olim@example.uz

# Buni nusxalang va GitHub'ga qo'shing:
# GitHub → Settings → SSH and GPG keys → New SSH key

# Tekshirish
ssh -T git@github.com
# Hi olim! You've successfully authenticated...

# ─────────────────────────────────────────────────────────────────────
# 2) Lokal repo'ni GitHub'ga bog'lash
# ─────────────────────────────────────────────────────────────────────

# Avval GitHub'da repo yarating (web UI):
# github.com → New repository → nom: "mening-loyiham"
# README qo'shmang!

cd mening-loyiham

# Remote qo'shish
git remote add origin git@github.com:olim/mening-loyiham.git

# Tekshirish
git remote -v
# origin  git@github.com:olim/mening-loyiham.git (fetch)
# origin  git@github.com:olim/mening-loyiham.git (push)

# Birinchi push — -u bilan upstream
git push -u origin main
# Enumerating objects: 12, done.
# To github.com:olim/mening-loyiham.git
#  * [new branch]      main -> main

# Endi GitHub sahifasini yangilang — kodingiz ko'rinadi!

# ─────────────────────────────────────────────────────────────────────
# 3) Yangi commit + push
# ─────────────────────────────────────────────────────────────────────

echo "Yangi qator" >> README.md
git add README.md
git commit -m "docs: README yangilandi"

git push
# Endi -u kerak emas — birinchi marta sozlangan
# To github.com:olim/mening-loyiham.git
#    abc1234..def5678  main -> main

# ─────────────────────────────────────────────────────────────────────
# 4) clone — boshqa joydan olish
# ─────────────────────────────────────────────────────────────────────

cd ~/Desktop

# To'liq clone
git clone git@github.com:olim/mening-loyiham.git
cd mening-loyiham

# Tarix, branchlar — hammasi keldi
git log --oneline

# Boshqa nom bilan
# git clone git@github.com:olim/mening-loyiham.git mening-loyiham-2

# Faqat oxirgi commit (tezroq)
# git clone --depth 1 git@github.com:olim/mening-loyiham.git

# Belgilangan branch
# git clone -b develop git@github.com:olim/mening-loyiham.git

# ─────────────────────────────────────────────────────────────────────
# 5) pull — yangiliklar olish
# ─────────────────────────────────────────────────────────────────────

# Faraz: GitHub'da yoki boshqa kompyuterda commit bo'ldi
# Lokal'da ko'ramiz:
git pull
# Already up to date.
# yoki:
# Updating abc1234..def5678
# Fast-forward
#  README.md | 1 +
#  1 file changed, 1 insertion(+)

# pull = fetch + merge
git fetch origin
git merge origin/main
# (yuqorisi bilan teng)

# Faqat ko'rib chiqish (merge qilmasdan)
git fetch origin
git log --oneline HEAD..origin/main
# (yangi commit'lar ko'rinadi)

# ─────────────────────────────────────────────────────────────────────
# 6) Push xato — reject
# ─────────────────────────────────────────────────────────────────────

# Sinariy: boshqa joyda commit bo'ldi, siz lokal'da ham commit qildingiz
# Push qilmoqchisiz...

# git push
# ! [rejected]        main -> main (fetch first)
# error: failed to push some refs
# hint: Updates were rejected because the remote contains work...

# Yechim:
git pull --rebase     # yoki: git pull
git push

# (rebase — 8-darsda batafsil)

# ─────────────────────────────────────────────────────────────────────
# 7) Boshqa branchni push
# ─────────────────────────────────────────────────────────────────────

git switch -c feature/footer

echo "<footer>© 2026</footer>" > footer.html
git add footer.html
git commit -m "feat: footer komponenti"

# Birinchi marta — upstream sozlash
git push -u origin feature/footer
# To github.com:olim/mening-loyiham.git
#  * [new branch]      feature/footer -> feature/footer
# branch 'feature/footer' set up to track 'origin/feature/footer'.

# Keyingi safar — git push yetadi

# ─────────────────────────────────────────────────────────────────────
# 8) Remote boshqarish
# ─────────────────────────────────────────────────────────────────────

# Ro'yxat
git remote -v

# URL o'zgartirish (HTTPS → SSH ga)
git remote set-url origin git@github.com:olim/mening-loyiham.git

# O'chirish
# git remote remove origin

# Rename
# git remote rename origin upstream

# ─────────────────────────────────────────────────────────────────────
# 9) Branch o'chirish (lokal va remote)
# ─────────────────────────────────────────────────────────────────────

# Lokal
git branch -d feature/footer

# Remote
git push origin --delete feature/footer

# Ikkalasi birga
# (qisqa skript yo'q — alohida buyruq)

# ─────────────────────────────────────────────────────────────────────
# 10) Force push — XAVFLI
# ─────────────────────────────────────────────────────────────────────

# Faqat shaxsiy branch'da, jamoadosh bilan kelishilgan paytda
# git push --force                  # ESKI — eng xavfli
# git push --force-with-lease       # YAXSHI — eski versiyaga override qilmaydi
"""
L5_TEXT = """\
<h2>Pull Request lifecycle — fork, branch, PR, review</h2>

<pre class="mermaid">
flowchart LR
    UP["upstream:\nmain repo"] -->|fork| F["origin:\nsizning fork"]
    F -->|clone| L["lokal"]
    L -->|push| F
    F -->|PR| UP
    UP -->|review + merge| UP2["upstream main\n+ sizning kod"]
</pre>

<p>Pull Request (PR) — GitHub'ning butun yuzi. Bu shunday tartib: "Men shu o'zgarishni qildim. Iltimos ko'rib chiqing va qabul qiling". Open source loyihalar, jamoaviy ish, hatto sizning shaxsiy loyihangiz — hammasi PR orqali.</p>

<p>2 ta senariy:</p>
<ol>
<li><strong>O'z repo'ngiz</strong> — branch yarating, push qiling, PR ochib o'zingiz merge qiling</li>
<li><strong>Boshqa repo (open source)</strong> — fork qiling, o'zgartiring, PR yuboring</li>
</ol>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — O'z repo'da PR (basic)</h4>

<pre><code># 1. Yangi feature branch
git switch -c feature/login-form

# 2. Kod yozing va commit
echo "&lt;form id='login'&gt;...&lt;/form&gt;" &gt; login.html
git add login.html
git commit -m "feat: login formasi qo'shildi"

# 3. Branchni push
git push -u origin feature/login-form
# remote: Create a pull request for 'feature/login-form' on GitHub by visiting:
# remote: https://github.com/olim/mening-loyiham/pull/new/feature/login-form</code></pre>

<p>4. URL'ga o'ting — GitHub PR yaratish formasini ochadi:</p>
<ul>
<li>📝 <strong>Title</strong> — qisqa, aniq</li>
<li>📋 <strong>Description</strong> — nima va nima uchun</li>
<li>✅ <strong>Create pull request</strong></li>
</ul>

<p>5. Endi review (o'zingiz yoki sherigingiz). Comment'lar, suggestion'lar. Hammasi yaxshi bo'lsa — <strong>Merge pull request</strong> bosing.</p>

<p>6. Lokal'da yangilang:</p>
<pre><code>git switch main
git pull
git branch -d feature/login-form    # local clean
git push origin --delete feature/login-form   # remote clean</code></pre>

<h4>BLOKA 2 — Fork bilan open source PR</h4>

<p>Faraz: <code>github.com/anthropic/cool-project</code> repo'siga o'z hissangizni qo'shmoqchisiz.</p>

<p><strong>1. Fork</strong> — GitHub'da repo sahifasida <code>Fork</code> tugmasi. Bu sizning hisobingizga nusxa yaratadi: <code>github.com/olim/cool-project</code>.</p>

<p><strong>2. Clone (sizning fork)</strong>:</p>
<pre><code>git clone git@github.com:olim/cool-project.git
cd cool-project

# upstream — asl repo
git remote add upstream git@github.com:anthropic/cool-project.git

git remote -v
# origin    git@github.com:olim/cool-project.git (sizning fork)
# upstream  git@github.com:anthropic/cool-project.git (asl)</code></pre>

<p><strong>3. Branch + o'zgarish + push</strong>:</p>
<pre><code>git switch -c fix/typo-readme

# README'da typo to'g'rilang
# ...
git add README.md
git commit -m "fix: README typo to'g'rilandi"

git push -u origin fix/typo-readme</code></pre>

<p><strong>4. GitHub'da</strong>: fork sahifasi → <code>Compare &amp; pull request</code> tugma. Asl repo'ga PR ochiladi.</p>

<p><strong>5. Reviewer'lar javob beradi</strong>. O'zgarishlar so'rasalar — yana commit qiling va push. PR avtomatik yangilanadi.</p>

<p><strong>6. Merge bo'lgach</strong>:</p>
<pre><code># Upstream'dan yangiliklar olish (sizning PR ham shu yerda)
git switch main
git pull upstream main
git push origin main    # sizning fork yangilash

# Branchni o'chirish
git branch -d fix/typo-readme
git push origin --delete fix/typo-readme</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Fork'ni 6 oy oldin qildingiz. Asl repo ilgariga ketgan.
# Sizning fork eskirgan.
git clone git@github.com:olim/cool-project.git
# (eski versiya keladi)</code></pre>

<p><strong>Sabab:</strong> Fork — bir martalik nusxa. GitHub avtomatik sync qilmaydi. <strong>Yechim:</strong> upstream'dan pull qilib, fork'ni yangilang:</p>

<pre><code>git remote add upstream git@github.com:anthropic/cool-project.git
git pull upstream main
git push origin main</code></pre>

<p>Yoki GitHub UI'da: fork sahifasida <strong>Sync fork</strong> tugmasi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. PR'ning to'liq hayot tsikli</h4>

<ol>
<li><strong>Branch</strong> — main'da hech qachon ishlamaysiz</li>
<li><strong>Commit'lar</strong> — kichik, aniq</li>
<li><strong>Push</strong> — origin'ga</li>
<li><strong>PR ochish</strong> — title + description</li>
<li><strong>CI tests</strong> — avtomatik (10-darsda)</li>
<li><strong>Review</strong> — kod o'qish, comment'lar</li>
<li><strong>O'zgarishlar</strong> — yana commit + push (PR avtomatik yangilanadi)</li>
<li><strong>Approve</strong> — reviewer "Approve" beradi</li>
<li><strong>Merge</strong> — 3 ta variant (pastda)</li>
<li><strong>Delete branch</strong> — toza</li>
</ol>

<h4>2. PR yaxshi yozish — checklist</h4>

<table>
<tr><th>Bo'lim</th><th>Mazmun</th></tr>
<tr><td>Title</td><td>Qisqa, conventional commit format: <code>feat: yangi profil sahifasi</code></td></tr>
<tr><td>Description</td><td>Nima o'zgardi va NIMA UCHUN. Screenshot/video agar UI.</td></tr>
<tr><td>Testing</td><td>Qanday test qildingiz?</td></tr>
<tr><td>Linked issue</td><td>Closes #42</td></tr>
<tr><td>Reviewers</td><td>Kim ko'rishi kerak</td></tr>
<tr><td>Labels</td><td>bug, feature, documentation</td></tr>
</table>

<h4>3. PR description template</h4>

<pre><code>## Nima o'zgardi
- Profil sahifasi yaratildi
- Avatar yuklash ishlaydi

## Nima uchun
Foydalanuvchilar profilini boshqarishni so'rashdi (issue #42).

## Test
- [x] Manual test bajarildi
- [x] Birlik testlari yozildi
- [ ] E2E test (keyingi PR'da)

## Screenshot
[rasm bu yerga]

Closes #42</code></pre>

<h4>4. Review qilish — sherikingiz PR'iga</h4>

<p>GitHub'da PR sahifasi → <strong>Files changed</strong> tab:</p>

<ul>
<li>🟢 <strong>Approve</strong> — hammasi yaxshi</li>
<li>💬 <strong>Comment</strong> — savol/taklif (block qilmaydi)</li>
<li>🔴 <strong>Request changes</strong> — bu yo'q, tuzating</li>
</ul>

<p>Qator ustiga bosing → comment qoldiring. Yoki <strong>Suggest changes</strong> — to'g'ridan-to'g'ri tuzatma kod taklif qiling.</p>

<h4>5. 3 ta merge strategiyasi</h4>

<table>
<tr><th>Strategiya</th><th>Natija</th><th>Qachon</th></tr>
<tr><td><strong>Merge commit</strong></td><td>Hammasi + merge commit</td><td>Tarix to'liq saqlash</td></tr>
<tr><td><strong>Squash</strong></td><td>Hammasi 1 ta commit'ga birlashtiriladi</td><td>Toza tarix (mashhur)</td></tr>
<tr><td><strong>Rebase</strong></td><td>Commit'lar main'ga ketma-ket qo'shiladi</td><td>Linear tarix</td></tr>
</table>

<p>Ko'p loyihalar — <strong>Squash</strong> tanlaydi.</p>

<h4>6. Draft PR</h4>

<p>Hali tugamagan ish — <strong>Draft PR</strong> qilib oching. Reviewer'lar early feedback berishi mumkin, lekin merge bloklanadi. Tayyor bo'lganda <strong>Ready for review</strong>.</p>

<h4>7. gh CLI — terminalda PR</h4>

<pre><code># GitHub CLI o'rnatish
brew install gh        # macOS
# sudo apt install gh  # Linux

gh auth login

# PR yaratish (branchni push qilgandan keyin)
gh pr create --title "feat: login form" --body "Login UI"

# PR ro'yxati
gh pr list

# PR ochish browser'da
gh pr view --web

# Merge qilish
gh pr merge --squash</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ PR — GitHub'ning markaziy ish jarayoni</li>
<li>✅ Fork → clone → branch → commit → push → PR</li>
<li>✅ Fork — bir martalik nusxa, sync kerak</li>
<li>✅ <code>upstream</code> + <code>origin</code> — 2 ta remote</li>
<li>✅ PR description — nima + nima uchun + test</li>
<li>✅ 3 ta merge: merge commit / squash / rebase</li>
<li>✅ Draft PR — hali tugamagan ish uchun</li>
<li>✅ <code>gh</code> CLI — terminalda PR boshqarish</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 5: Pull Request lifecycle
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) O'z repo'da PR
# ─────────────────────────────────────────────────────────────────────

cd mening-loyiham

# Yangi feature
git switch -c feature/dark-mode

cat > theme.css <<'EOF'
:root {
    --bg: #fff;
    --text: #000;
}

[data-theme="dark"] {
    --bg: #222;
    --text: #fff;
}
EOF

git add theme.css
git commit -m "feat: dark mode CSS variables"

# UI tugmasi
echo '<button id="theme-toggle">🌙</button>' >> index.html

git add index.html
git commit -m "feat: theme toggle button"

# Push
git push -u origin feature/dark-mode
# remote: Create a pull request for 'feature/dark-mode'...
# remote: https://github.com/olim/mening-loyiham/pull/new/feature/dark-mode

# URL'ga o'tib PR yarating
# yoki gh CLI bilan:
gh pr create \\
    --title "feat: dark mode qo'shildi" \\
    --body "$(cat <<'PR'
## Nima o'zgardi
- CSS variables bilan dark mode
- Theme toggle button

## Nima uchun
Foydalanuvchilar so'rovi (issue #15).

## Test
- [x] Chrome'da sinangan
- [x] Firefox'da sinangan
- [ ] Safari (TODO)

## Screenshot
(rasmni qo'shing)
PR
)"

# PR'ni ko'rish
gh pr view --web

# ─────────────────────────────────────────────────────────────────────
# 2) Reviewer feedback: o'zgartirish so'raldi
# ─────────────────────────────────────────────────────────────────────

# Reviewer dedi: "localStorage'da saqlash kerak"

cat >> theme.js <<'EOF'
const toggle = document.getElementById('theme-toggle');
toggle.onclick = () => {
    const yangi = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    document.body.dataset.theme = yangi;
    localStorage.setItem('theme', yangi);
};

// Saqlangan tema
document.body.dataset.theme = localStorage.getItem('theme') || 'light';
EOF

git add theme.js
git commit -m "feat: tema localStorage'da saqlanadi"

# Push — PR avtomatik yangilanadi!
git push

# ─────────────────────────────────────────────────────────────────────
# 3) Merge — 3 ta variant
# ─────────────────────────────────────────────────────────────────────

# GitHub UI'da Merge dropdown:
# - Create a merge commit
# - Squash and merge       (mashhur)
# - Rebase and merge

# Yoki gh CLI:
gh pr merge --squash --delete-branch
# yoki:
# gh pr merge --merge --delete-branch
# gh pr merge --rebase --delete-branch

# ─────────────────────────────────────────────────────────────────────
# 4) Lokal toza
# ─────────────────────────────────────────────────────────────────────

git switch main
git pull              # main yangiliklar (squash commit shu yerda)
git branch -d feature/dark-mode

# Remote'da ham o'chirish (agar gh --delete-branch ishlatmagansiz)
# git push origin --delete feature/dark-mode

# Eskirgan local branchlarni tozalash
git fetch --prune
git branch --merged main | grep -v "main" | xargs -n 1 git branch -d

# ─────────────────────────────────────────────────────────────────────
# 5) Fork workflow (open source)
# ─────────────────────────────────────────────────────────────────────

# 1. GitHub'da Fork tugmasini bosing
#    github.com/anthropic/cool-project → Fork → github.com/olim/cool-project

# 2. Clone (SIZNING fork)
git clone git@github.com:olim/cool-project.git
cd cool-project

# 3. upstream — asl repo'ni qo'shing
git remote add upstream git@github.com:anthropic/cool-project.git

git remote -v
# origin    git@github.com:olim/cool-project.git
# upstream  git@github.com:anthropic/cool-project.git

# 4. Asosiy ish
git switch -c fix/readme-typo

# Tahrir...
sed -i.bak 's/recieve/receive/g' README.md
rm README.md.bak

git add README.md
git commit -m "fix: typo 'recieve' -> 'receive'"

git push -u origin fix/readme-typo

# 5. PR yarating — upstream/main ga
gh pr create \\
    --title "fix: README typo" \\
    --body "Recieve -> receive" \\
    --base main \\
    --head olim:fix/readme-typo

# 6. Reviewer'lar javob, siz tuzatish — qaytadan push
# 7. Merge bo'lgach, fork'ni yangilang:

git switch main
git pull upstream main
git push origin main      # sizning fork'da main yangilanadi

git branch -d fix/readme-typo
git push origin --delete fix/readme-typo

# ─────────────────────────────────────────────────────────────────────
# 6) gh CLI — kunlik buyruqlar
# ─────────────────────────────────────────────────────────────────────

# Auth
gh auth login

# PR ro'yxat (joriy repo)
gh pr list

# PR sizning (har repo'da)
gh pr list --author "@me"

# Bitta PR'ni ko'rish
gh pr view 42
gh pr view 42 --web

# PR checkout (sherikingiz PR'iga o'tish)
gh pr checkout 42

# Comment qo'shish
gh pr comment 42 --body "LGTM 🎉"

# Approve
gh pr review 42 --approve

# Request changes
gh pr review 42 --request-changes --body "Test yo'q"

# Draft PR
gh pr create --draft

# Ready for review
gh pr ready

# ─────────────────────────────────────────────────────────────────────
# 7) Fork'ni yangilash — qisqa
# ─────────────────────────────────────────────────────────────────────

# Variant A: terminal
git fetch upstream
git switch main
git merge upstream/main
git push origin main

# Variant B: gh CLI (zamonaviy)
gh repo sync olim/cool-project --branch main

# Variant C: GitHub UI
# Fork sahifasida "Sync fork" tugmasi
"""
L6_TEXT = """\
<h2>Merge conflict — qanday yechish</h2>

<pre class="mermaid">
flowchart LR
    A["main: 'red'"] --> M["MERGE"]
    B["feature: 'blue'"] --> M
    M -->|qaror qiling| C{"qaysisi?"}
    C -->|red| R["red qoldi"]
    C -->|blue| BL["blue qoldi"]
    C -->|ikkalasi| BT["ikkalasi birga"]
</pre>

<p>2 ta odam <strong>bir xil faylning bir xil qatori</strong>ni o'zgartirsa — Git qaysi versiyani saqlashni bilmaydi. Bu — <strong>merge conflict</strong>. Birinchi marta uchratganda qo'rqitadi, lekin aslida — oddiy: Git sizdan "qaysi versiya?" deb so'raydi, siz tanlaysiz.</p>

<p>Merge conflict — Git'ning xatosi emas, sizning ishingiz. Har dasturchi har kuni 1-2 marta uchraydi. Tinch yeching va davom eting.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — conflict yaratamiz</h4>

<pre><code># main'da
git switch main
echo "Bu — main versiyasi" &gt; matn.txt
git add matn.txt
git commit -m "feat: matn.txt qo'shildi"

# feature branchda boshqa versiya
git switch -c feature/yangi-matn
echo "Bu — feature versiyasi" &gt; matn.txt
git add matn.txt
git commit -m "feat: matn yangilandi"

# main'ga qaytib boshqacha o'zgarish
git switch main
echo "Bu — main'ning yangilangan versiyasi" &gt; matn.txt
git add matn.txt
git commit -m "feat: main matn yangilandi"

# Endi merge — conflict!
git merge feature/yangi-matn
# CONFLICT (content): Merge conflict in matn.txt
# Automatic merge failed; fix conflicts and then commit the result.</code></pre>

<h4>BLOKA 2 — conflict'ni ko'rish</h4>
<pre><code>cat matn.txt
# &lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD
# Bu — main'ning yangilangan versiyasi
# =======
# Bu — feature versiyasi
# &gt;&gt;&gt;&gt;&gt;&gt;&gt; feature/yangi-matn</code></pre>

<p>Git fayl ichiga marker qo'ydi:</p>
<ul>
<li><code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</code> — hozirgi branch (main)</li>
<li><code>=======</code> — chegara</li>
<li><code>&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature/...</code> — boshqa branch</li>
</ul>

<h4>BLOKA 3 — conflict'ni yechish</h4>

<p>Editor'da faylni oching va <strong>kerakli mazmunni saqlang, marker'larni o'chiring</strong>. 3 ta variant:</p>

<pre><code># Variant 1: faqat main'ni saqlash
Bu — main'ning yangilangan versiyasi

# Variant 2: faqat feature'ni
Bu — feature versiyasi

# Variant 3: ikkalasini birlashtirish
Bu — main'ning yangilangan versiyasi
Bu — feature versiyasi

# Variant 4: yangi ma'no
Bu — ikkala versiyaning eng yaxshi qismi</code></pre>

<p>Marker'larni butunlay olib tashlang. Saqlang.</p>

<pre><code># Conflict yechilgani aytamiz
git add matn.txt

# Merge'ni yakunlash
git commit
# (avtomatik xabar: "Merge branch 'feature/yangi-matn'")</code></pre>

<h3>🐛 Ataylab xato (yangi boshlovchining klassik tuzog'i)</h3>
<pre><code>git add matn.txt
git commit -m "fix conflict"
# (lekin marker'larni o'chirmagan!)</code></pre>

<p><strong>Natija:</strong> Commit muvaffaqiyatli, lekin faylda hali <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> bor. Kod sintaktik xato beradi, hech qaysi til kompilyator buni qabul qilmaydi.</p>

<p><strong>Qoidasi:</strong> conflict yechish = marker'larni olib tashlash + mantiqiy mazmun. Doim faylni o'qib chiqing!</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Conflict qachon bo'ladi?</h4>

<p>2 ta branch <strong>bir xil faylning bir xil joyini</strong> o'zgartirganda. Agar har xil joyni o'zgartirsangiz — Git avtomatik birlashtiradi (conflict yo'q).</p>

<h4>2. Conflict yechish jarayonida foydali buyruqlar</h4>

<table>
<tr><th>Buyruq</th><th>Vazifa</th></tr>
<tr><td><code>git status</code></td><td>Qaysi fayllarda conflict</td></tr>
<tr><td><code>git diff</code></td><td>Conflict markerlarini ko'rish</td></tr>
<tr><td><code>git merge --abort</code></td><td>Merge'ni bekor qilish (eski holatga)</td></tr>
<tr><td><code>git checkout --ours fayl</code></td><td>Faqat hozirgi (main) versiyani saqlash</td></tr>
<tr><td><code>git checkout --theirs fayl</code></td><td>Faqat boshqa (feature) versiyani</td></tr>
<tr><td><code>git mergetool</code></td><td>GUI mergetool ochish</td></tr>
</table>

<h4>3. Ours vs Theirs — yodlash hiyla</h4>

<pre><code># merge'da:
git checkout --ours fayl    # = hozirgi (main) saqlanadi
git checkout --theirs fayl  # = qo'shilayotgan (feature) saqlanadi

# rebase'da (8-darsda) — aksincha! Mantiq teskari.</code></pre>

<h4>4. Visual merge tools</h4>

<p>Murakkab conflict'lar uchun — VS Code, Meld, Beyond Compare:</p>

<pre><code># VS Code'da
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Conflict paytida
git mergetool</code></pre>

<p>VS Code'da har conflict joyida tugmalar: <strong>Accept Current Change</strong>, <strong>Accept Incoming Change</strong>, <strong>Accept Both Changes</strong>.</p>

<h4>5. Conflict'ning oldini olish</h4>

<ul>
<li><strong>Tez-tez pull qiling</strong> — kichik conflict'lar oson, katta — qiyin</li>
<li><strong>Kichik PR'lar</strong> — bir nechta dars'dan keyin emas, bir nechta soat</li>
<li><strong>Aloqada bo'ling</strong> — "men avtorlash kodida ishlayapman" deb ayting</li>
<li><strong>Aniq fayl tuzilmasi</strong> — har modul alohida faylda</li>
</ul>

<h4>6. Ko'p faylda conflict</h4>

<pre><code>git merge feature/big-change
# CONFLICT in: a.py, b.py, c.py

# Har birini alohida yeching
git status
# Unmerged paths:
#   both modified: a.py
#   both modified: b.py
#   both modified: c.py

# Yeching, add qiling, status tekshiring
vim a.py
git add a.py

vim b.py
git add b.py

vim c.py
git add c.py

git status
# All conflicts fixed but you are still merging.

git commit</code></pre>

<h4>7. Bekor qilish — agar adashib ketgan bo'lsangiz</h4>

<pre><code># Merge'ni butunlay bekor qilish
git merge --abort

# Eski holatga — hech narsa bo'lmagandek
git status
# On branch main
# nothing to commit, working tree clean</code></pre>

<h4>8. PR'da conflict</h4>

<p>GitHub PR sahifasi pastida:</p>
<pre><code>This branch has conflicts that must be resolved</code></pre>

<p>2 yo'l:</p>
<ol>
<li>GitHub UI'da (kichik conflict uchun) — "Resolve conflicts" tugmasi</li>
<li>Lokal'da yechish — pull qiling, conflict yeching, push qiling</li>
</ol>

<pre><code># Lokal'da
git switch feature/login
git pull origin main          # main'dagi yangiliklar bilan merge
# (conflict yeching)
git push                       # PR avtomatik yangilanadi</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Merge conflict — Git'ning sizdan "qaysi versiya?" deb so'rashi</li>
<li>✅ <code>&lt;&lt;&lt;</code>, <code>===</code>, <code>&gt;&gt;&gt;</code> marker'lari</li>
<li>✅ Conflict yechish: tahrir + marker'larni o'chirish + add + commit</li>
<li>✅ <code>git merge --abort</code> — bekor qilish</li>
<li>✅ <code>--ours</code> / <code>--theirs</code> — bir tomonni avtomatik saqlash</li>
<li>✅ Visual mergetool (VS Code) — murakkablar uchun</li>
<li>✅ Oldini olish: tez-tez pull, kichik PR</li>
<li>✅ PR'da conflict — lokal'da yechish va qaytadan push</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 6: Merge conflict — yechish
# ════════════════════════════════════════════════════════════════════

cd mening-loyiham

# ─────────────────────────────────────────────────────────────────────
# 1) Toza holatdan boshlash
# ─────────────────────────────────────────────────────────────────────

git switch main
git pull

# Test fayl
echo "matn versiya 1" > test.txt
git add test.txt
git commit -m "test: boshlang'ich fayl"
git push

# ─────────────────────────────────────────────────────────────────────
# 2) Conflict yaratamiz
# ─────────────────────────────────────────────────────────────────────

# Feature branch
git switch -c feature/o-zgartirish
echo "matn — feature versiyasi" > test.txt
git add test.txt
git commit -m "feat: matn feature uslubida"

# Main'ga qaytib boshqa o'zgarish
git switch main
echo "matn — main versiyasi" > test.txt
git add test.txt
git commit -m "feat: matn main uslubida"

# Merge — CONFLICT!
git merge feature/o-zgartirish
# Auto-merging test.txt
# CONFLICT (content): Merge conflict in test.txt
# Automatic merge failed; fix conflicts and then commit the result.

# ─────────────────────────────────────────────────────────────────────
# 3) Conflict'ni ko'rish
# ─────────────────────────────────────────────────────────────────────

git status
# Unmerged paths:
#   both modified: test.txt

cat test.txt
# <<<<<<< HEAD
# matn — main versiyasi
# =======
# matn — feature versiyasi
# >>>>>>> feature/o-zgartirish

# ─────────────────────────────────────────────────────────────────────
# 4) Yechish — 4 ta variant
# ─────────────────────────────────────────────────────────────────────

# Variant 1: faqat main
cat > test.txt <<'EOF'
matn — main versiyasi
EOF

# yoki avtomatik:
git checkout --ours test.txt

# Variant 2: faqat feature
git checkout --theirs test.txt

# Variant 3: ikkalasi birga
cat > test.txt <<'EOF'
matn — main versiyasi
matn — feature versiyasi
EOF

# Variant 4: yangi mazmun
cat > test.txt <<'EOF'
matn — main va feature versiyalari birlashtirildi
EOF

# Hozir variant 4 ni tanlaymiz
cat > test.txt <<'EOF'
matn — birlashtirildi
EOF

# ─────────────────────────────────────────────────────────────────────
# 5) Yechilganini Git'ga aytish
# ─────────────────────────────────────────────────────────────────────

git add test.txt

git status
# All conflicts fixed but you are still merging.

git commit
# Editor ochiladi (yoki avtomatik xabar bilan)
# Default xabar: "Merge branch 'feature/o-zgartirish'"

# ─────────────────────────────────────────────────────────────────────
# 6) Tarix
# ─────────────────────────────────────────────────────────────────────

git log --oneline --graph --all
# *   merge_sha Merge branch 'feature/o-zgartirish'
# |\\
# | * feat_sha feat: matn feature uslubida
# * | main_sha feat: matn main uslubida
# |/
# * old_sha test: boshlang'ich fayl

# ─────────────────────────────────────────────────────────────────────
# 7) Merge'ni bekor qilish
# ─────────────────────────────────────────────────────────────────────

# Conflict paytida — eski holatga qaytish
# git merge --abort

# Bu — eski main'ga qaytish. Hech narsa o'zgarmagan.

# ─────────────────────────────────────────────────────────────────────
# 8) Ko'p faylda conflict
# ─────────────────────────────────────────────────────────────────────

# Faraz — 3 ta faylda
git switch main
echo "main a" > a.txt && echo "main b" > b.txt && echo "main c" > c.txt
git add . && git commit -m "main: a,b,c"

git switch -c feature/multi
echo "feat a" > a.txt && echo "feat b" > b.txt && echo "feat c" > c.txt
git add . && git commit -m "feat: a,b,c"

git switch main
echo "yana main" > a.txt && echo "yana main b" > b.txt
git add . && git commit -m "main: a,b yangilandi"

git merge feature/multi
# CONFLICT in: a.txt, b.txt (c.txt avtomatik mergeli)

# Har birini alohida
echo "yakuniy a" > a.txt && git add a.txt
echo "yakuniy b" > b.txt && git add b.txt

git status
# all conflicts fixed

git commit

# ─────────────────────────────────────────────────────────────────────
# 9) VS Code'ni mergetool sifatida
# ─────────────────────────────────────────────────────────────────────

# git config --global merge.tool vscode
# git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Conflict paytida
# git mergetool

# VS Code ochiladi, har conflict joyida tugmalar:
# - Accept Current Change (ours)
# - Accept Incoming Change (theirs)
# - Accept Both Changes
# - Compare Changes

# ─────────────────────────────────────────────────────────────────────
# 10) PR'da conflict — lokal yechish
# ─────────────────────────────────────────────────────────────────────

# GitHub: "This branch has conflicts that must be resolved"

# Lokal:
git switch feature/login
git fetch origin
git merge origin/main         # main'ni feature'ga
# CONFLICT...

# Yechib commit qiling
# git add . && git commit

# Push — PR yangilanadi
git push
"""
R2_TEXT = """\
<h2>R2 — Modul 2 takrorlash: Open source repo'ga real PR</h2>

<p>Modul 2 ning eng katta amaliyoti — siz hayotingizdagi <strong>birinchi haqiqiy PR</strong> ni open source loyihaga yuborasiz. Bu yangi boshlovchilar uchun katta qadam: GitHub portfoliongizda "Contributor" belgisi, CV uchun mavzu.</p>

<p>Modul 2 ning hamma narsasi birga: <strong>SSH, fork, clone, branch, commit, push, PR, conflict (agar bo'lsa).</strong></p>

<h3>Loyihaning maqsadi</h3>

<p>Real open source loyihaga foydali (lekin oddiy) hissa qo'shish. <strong>Documentation</strong> yoki <strong>typo fix</strong> — yangi boshlovchilar uchun ideal birinchi PR.</p>

<h3>Yaxshi birinchi PR uchun repo qidirish</h3>

<p>GitHub'da qidirish: <strong>"good first issue"</strong> label'i.</p>

<ul>
<li>🔗 <a href="https://goodfirstissue.dev/">goodfirstissue.dev</a></li>
<li>🔗 <a href="https://github.com/topics/good-first-issue">github.com/topics/good-first-issue</a></li>
<li>🔗 <a href="https://up-for-grabs.net/">up-for-grabs.net</a></li>
</ul>

<p>Yaxshi tanlovlar:</p>

<table>
<tr><th>Tur</th><th>Misol</th></tr>
<tr><td>Typo fix</td><td>README'da "recieve" → "receive"</td></tr>
<tr><td>Translation</td><td>Documentation o'zbek tiliga</td></tr>
<tr><td>Example qo'shish</td><td>Docs'da kichik kod misoli</td></tr>
<tr><td>Broken link fix</td><td>README'dagi eski link</td></tr>
<tr><td>Documentation</td><td>"Get started" sahifasini yaxshilash</td></tr>
</table>

<p>Boshlash uchun yaxshi joylar:</p>
<ul>
<li><strong>freeCodeCamp</strong> — har xil tilda content</li>
<li><strong>MDN web docs</strong> — web tutorials</li>
<li><strong>Awesome lists</strong> — har sohada</li>
<li><strong>Hacktoberfest</strong> — har oktyabrda kampaniya</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Repo tanlash</h4>
<ul>
<li>"good first issue" label'i bilan kamida 3 ta repo'ni tekshiring</li>
<li>Bittasini tanlang (README/docs/translation muammoli)</li>
<li>Repo: kamida 100 star, oxirgi commit 30 kun ichida (faol)</li>
<li>CONTRIBUTING.md o'qing (har repo'ning o'z qoidalari)</li>
</ul>

<h4>Vazifa 2 — Issue ochish (agar yo'q bo'lsa)</h4>
<ul>
<li>Repo'da hali sizning fix uchun issue yo'qmi?</li>
<li>Yangi issue oching: muammo + taklif yechim</li>
<li>Maintainer'lardan ko'k chiroq olib (agar kerak bo'lsa)</li>
</ul>

<h4>Vazifa 3 — Fork → Clone → Branch</h4>
<ul>
<li>Fork qiling (GitHub UI)</li>
<li>Clone qiling lokal'ga</li>
<li>upstream remote qo'shing</li>
<li>Yangi branch: <code>fix/&lt;qisqa-tavsif&gt;</code></li>
</ul>

<h4>Vazifa 4 — O'zgarish va commit</h4>
<ul>
<li>Faqat MOSLI faylni o'zgartiring (begona narsa qo'shmang)</li>
<li>Conventional commit: <code>docs: typo "recieve" → "receive"</code></li>
<li>Push: <code>git push -u origin fix/...</code></li>
</ul>

<h4>Vazifa 5 — PR yuborish</h4>
<ul>
<li>GitHub'da fork sahifasiga → Compare &amp; pull request</li>
<li>Title: aniq, conventional commit format</li>
<li>Description: nima, nima uchun, qanday test qildim</li>
<li>Closes #&lt;issue-num&gt; (agar issue bor bo'lsa)</li>
<li>Maintainer'larni mention qiling (juda kerak bo'lsa)</li>
</ul>

<h4>Vazifa 6 — Review va follow up</h4>
<ul>
<li>Maintainer comment'lariga sabr bilan javob bering (kunlar/haftalar)</li>
<li>O'zgartirish kerak bo'lsa — yana commit + push (PR avtomatik yangilanadi)</li>
<li>Tushunmasangiz — savol bering, qo'rqmang</li>
</ul>

<h4>Vazifa 7 — Merge bo'lgach</h4>
<ul>
<li>🎉 Sizning PR merge bo'ldi — birinchi hissa!</li>
<li>Fork'ni sync qiling (upstream'dan)</li>
<li>Branchni o'chiring (lokal va remote)</li>
<li>GitHub profilingizda "Contributor" belgisi paydo bo'ladi</li>
</ul>

<h3>🐛 Ataylab qiyin: rejection</h3>

<p>Maintainer "Sorry, this doesn't fit our roadmap" deb yopib qo'yishi mumkin. Bu — normal. Sabablari:</p>
<ul>
<li>Loyiha endi qo'llab-quvvatlanmayapti</li>
<li>Boshqa odam allaqachon shu narsa ustida ishlamoqda</li>
<li>Maintainer boshqa ko'rinish istaydi</li>
<li>Sizning kod CONTRIBUTING qoidalariga mos kelmaydi</li>
</ul>

<p>Yo'q deb qabul qiling, boshqa repo'ga o'tib qaytadan urinib ko'ring. Bu — open source hayoti.</p>

<h3>PR yozish — yaxshi misol</h3>

<pre><code>Title: docs: README'da typo "recieve" -&gt; "receive"

Description:
## Nima o'zgardi
README.md ning 42-qatorida "recieve" o'rniga "receive" yozildi.

## Nima uchun
Imlo xatosi — eslatma uchun.

## Tekshirish
- [x] grep "recieve" bilan tekshirildi — boshqa o'rinda yo'q
- [x] Lokal'da render qilindi

Closes #123</code></pre>

<h3>Yo'l xaritasi — to'liq jarayon</h3>

<details>
<summary>Birinchi PR uchun bosqichma-bosqich</summary>
<pre><code># 1. Repo tanlash
# Faraz: github.com/awesome-org/cool-docs
# README'da "recieve" topdingiz

# 2. Fork (GitHub UI: Fork tugmasi)
# Endi: github.com/olim/cool-docs

# 3. Clone
git clone git@github.com:olim/cool-docs.git
cd cool-docs

# 4. upstream
git remote add upstream git@github.com:awesome-org/cool-docs.git

# 5. CONTRIBUTING.md o'qish
cat CONTRIBUTING.md

# 6. Branch
git switch -c fix/readme-typo

# 7. Tahrirlash
sed -i.bak 's/recieve/receive/g' README.md
rm README.md.bak

# Tekshirish
git diff
grep -c "recieve" README.md   # 0 chiqishi kerak

# 8. Commit
git add README.md
git commit -m "docs: typo 'recieve' -&gt; 'receive'"

# 9. Push
git push -u origin fix/readme-typo

# 10. PR (gh CLI bilan)
gh pr create \\
    --title "docs: typo 'recieve' -&gt; 'receive'" \\
    --body "Simple typo fix in README line 42. Closes #123."

# 11. Sabr — review kelishini kuting (kunlar/haftalar)

# 12. Merge bo'lgach
git switch main
git pull upstream main
git push origin main
git branch -d fix/readme-typo
git push origin --delete fix/readme-typo

# 🎉 Birinchi PR!</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Birinchi haqiqiy open source PR yuborish</li>
<li>✅ "Good first issue" repo'larni topish</li>
<li>✅ CONTRIBUTING.md o'qish — har loyihaning qoidalari</li>
<li>✅ Sabr — maintainer'lar tezda javob bermasligi mumkin</li>
<li>✅ Rejection — normal, boshqa repo bilan urinish</li>
<li>✅ GitHub portfolio'da "Contributor" belgisi</li>
</ul>
"""

R2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 2: Open source PR (real)
# Modul 2: SSH + fork + branch + push + PR
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# Vazifa 1: repo qidirish
# ─────────────────────────────────────────────────────────────────────

# Sayt'larda qidiruv:
# - https://goodfirstissue.dev/
# - github.com/topics/good-first-issue
# - up-for-grabs.net

# Yoki gh CLI bilan
gh search issues --label "good first issue" --state open --limit 20

# Faraz: tanlangan repo
# REPO=awesome-org/cool-docs
# ISSUE=#123 (README'da typo)

# CONTRIBUTING.md o'qish
# (har repo'ning o'z qoidalari)

# ─────────────────────────────────────────────────────────────────────
# Vazifa 2: fork va clone
# ─────────────────────────────────────────────────────────────────────

# GitHub UI'da Fork tugmasini bosing
# (yoki: gh CLI)
gh repo fork awesome-org/cool-docs --clone

cd cool-docs

# upstream'ni tekshirish
git remote -v
# origin    git@github.com:olim/cool-docs.git
# upstream  https://github.com/awesome-org/cool-docs.git
# (gh repo fork avtomatik qo'shadi)

# ─────────────────────────────────────────────────────────────────────
# Vazifa 3: branch
# ─────────────────────────────────────────────────────────────────────

# main'ni eng so'nggi versiyaga keltirish (fork eski bo'lishi mumkin)
git switch main
git pull upstream main
git push origin main

# Yangi branch
git switch -c fix/readme-typo

# ─────────────────────────────────────────────────────────────────────
# Vazifa 4: o'zgarish va test
# ─────────────────────────────────────────────────────────────────────

# Mantiqiy tahrir
sed -i.bak 's/recieve/receive/g' README.md
rm README.md.bak

# Tekshirish
git diff
# -## How to recieve notifications
# +## How to receive notifications

grep -c "recieve" README.md
# 0 (hammasi tuzatildi)

# ─────────────────────────────────────────────────────────────────────
# Vazifa 5: commit va push
# ─────────────────────────────────────────────────────────────────────

git add README.md

git commit -m "docs: typo 'recieve' -> 'receive'"

git push -u origin fix/readme-typo

# ─────────────────────────────────────────────────────────────────────
# Vazifa 6: PR yuborish
# ─────────────────────────────────────────────────────────────────────

gh pr create \\
    --title "docs: typo 'recieve' -> 'receive'" \\
    --body "$(cat <<'PR'
## Nima o'zgardi
README.md'da "recieve" -> "receive" tuzatildi (3 ta o'rin).

## Nima uchun
Imlo xatosi.

## Tekshirildi
- [x] `grep -c "recieve" README.md` -> 0
- [x] Lokal'da preview qildim

Closes #123
PR
)" \\
    --base main

# Tarmoq bilan tekshirish
gh pr view --web

# ─────────────────────────────────────────────────────────────────────
# Vazifa 7: maintainer feedback
# ─────────────────────────────────────────────────────────────────────

# Faraz: "Mansion 'receive' bo'lishi kerak edi, lekin docs ichida ham bor"
# Tuzatish:
sed -i.bak 's/recieve/receive/g' docs/*.md
rm docs/*.md.bak

git add docs/
git commit -m "docs: typo docs/ ichida ham tuzatildi"
git push

# PR avtomatik yangilanadi!

# ─────────────────────────────────────────────────────────────────────
# Vazifa 8: merge bo'lgach toza
# ─────────────────────────────────────────────────────────────────────

# (Maintainer Squash and merge qildi)

git switch main
git pull upstream main          # asl'dan yangiliklar (sizning PR shu yerda)
git push origin main             # fork yangilanish

git branch -d fix/readme-typo
git push origin --delete fix/readme-typo

# Eskirgan branchlarni tozalash
git fetch --prune

# ─────────────────────────────────────────────────────────────────────
# Vazifa 9: GitHub profilida tekshirish
# ─────────────────────────────────────────────────────────────────────

# github.com/olim
# Yashil kvadrat (contribution) paydo bo'ladi
# "Pull requests" tab: 1 ta merge bo'lgan PR
# "Contributions" tab: kelajakda 5+ contribution — open source contributor!

# ─────────────────────────────────────────────────────────────────────
# Vazifa 10: agar reject bo'lsa
# ─────────────────────────────────────────────────────────────────────

# Maintainer: "Sorry, we changed direction"
# Tarmoq:
# 1) Yo'q deb qabul qiling
# 2) Issue'da rahmat ayting
# 3) Boshqa repo'ga o'ting
# 4) Yana urinib ko'ring

# Bu — normal. Hatto experiyensli dasturchilarning PR'lari ham rad etiladi.

# ─────────────────────────────────────────────────────────────────────
# Hacktoberfest — har oktyabrda
# ─────────────────────────────────────────────────────────────────────

# hacktoberfest.com
# Oktyabrda 4 ta merge bo'lgan PR — tshirt yutib olish
# Eng yaxshi vaqt birinchi PR uchun
"""
L7_TEXT = """\
<h2>Stash, cherry-pick, amend — kunlik qurollar</h2>

<pre class="mermaid">
flowchart LR
    W["Working: yarim ish"] -->|git stash| S["Stash: vaqtinchalik"]
    S -->|git stash pop| W
    F1["feature: commit X"] -->|cherry-pick X| F2["main: shu commit"]
    OLD["oxirgi commit: xato xabar"] -->|amend| NEW["yangilangan commit"]
</pre>

<p>Hozirgacha — asosiy buyruqlar. Endi — kunlik <strong>productivity</strong> qurollar:</p>
<ul>
<li><strong>stash</strong> — yarim ishni vaqtinchalik yashirib qo'yish</li>
<li><strong>cherry-pick</strong> — boshqa branch'dan faqat 1 commit'ni olish</li>
<li><strong>amend</strong> — oxirgi commit'ni tahrirlash (xabar yoki mazmun)</li>
</ul>

<p>Bularsiz ham ishlaysiz, lekin bular bilan — ish 2-3 marta tezroq.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — stash</h4>

<p>Senariy: <code>feature/login</code>'da ishlayapsiz, yarim kod yozdingiz. Direktor "shoshilinch <code>main</code>'da bug fix kerak!" deydi. Hozirgi ishni yo'qotmasdan bug fix qilish.</p>

<pre><code># Yarim ishni stash'ga
git stash
# Saved working directory and index state WIP on feature/login: ...

# Endi working directory toza
git status
# nothing to commit, working tree clean

# main'ga o'tib bug fix
git switch main
# ... fix qiling ...
git add . && git commit -m "fix: critical bug"
git push

# Yarim ishga qaytish
git switch feature/login
git stash pop
# o'zgartirishlar qaytdi, davom etish mumkin</code></pre>

<h4>BLOKA 2 — cherry-pick</h4>

<p>Senariy: <code>feature/big</code>'da 5 ta commit qildingiz. Lekin <code>main</code>'ga faqat <em>bittasi</em> kerak (boshqalari tugamagan).</p>

<pre><code># feature/big'da commit'lar
git log --oneline
# def5678 (HEAD -&gt; feature/big) feat: refactor (tugamagan)
# abc1234 fix: critical security bug   &lt;-- shu main'ga kerak
# 9012345 wip: experiment
# ... va h.k.

# main'ga o'tamiz
git switch main

# Faqat shu commit'ni olamiz
git cherry-pick abc1234
# [main yangi_sha] fix: critical security bug

git log --oneline
# yangi_sha (HEAD -&gt; main) fix: critical security bug
# ... (oldingi main commit'lari)</code></pre>

<h4>BLOKA 3 — amend</h4>

<p>Senariy: hozirgina commit qildingiz, lekin xabar xato yoki bir fayl unutilgan.</p>

<pre><code># Faqat xabarni tuzatish
git commit --amend -m "fix: login formada email validatsiyasi"

# Yangi fayl qo'shish (oxirgi commit'ga)
echo "test" &gt;&gt; main.py
git add main.py
git commit --amend --no-edit       # xabar o'zgarmaydi

# Ikkalasi
git add yangi-fayl.py
git commit --amend -m "feat: yangi fayl va to'liq feature"</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># PUSH QILGAN commit'ni amend qilish
git push                       # commit GitHub'da
git commit --amend             # tahrirlandi
git push                       # ❌ REJECTED!</code></pre>

<p><strong>Sabab:</strong> <code>amend</code> aslida YANGI commit yaratadi (boshqa SHA bilan). Push qilingan commit allaqachon GitHub'da — yangi'sini push qilish — tarix qayta yozish. Bu jamoadosh uchun katastrofa.</p>

<p><strong>Qoidasi:</strong> <code>amend</code> faqat <strong>hali push qilinmagan</strong> commit'lar uchun. Yoki o'zingiznikiga (jamoadosh hech kim hali pull qilmagan).</p>

<p><strong>Force push</strong> bilan majburiy ham mumkin, lekin <code>--force-with-lease</code> ishlatib, jamoadoshga ogohlantiring.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Stash batafsil</h4>

<table>
<tr><th>Buyruq</th><th>Vazifa</th></tr>
<tr><td><code>git stash</code></td><td>O'zgarishlarni vaqtinchalik saqlash</td></tr>
<tr><td><code>git stash push -m "nom"</code></td><td>Nom bilan saqlash</td></tr>
<tr><td><code>git stash list</code></td><td>Stash'lar ro'yxati</td></tr>
<tr><td><code>git stash show</code></td><td>Oxirgi stash mazmunini ko'rish</td></tr>
<tr><td><code>git stash pop</code></td><td>Oxirgi'ni qaytarish va o'chirish</td></tr>
<tr><td><code>git stash apply</code></td><td>Qaytarish, lekin stash'da qoladi</td></tr>
<tr><td><code>git stash drop</code></td><td>Oxirgi stash'ni o'chirish</td></tr>
<tr><td><code>git stash clear</code></td><td>Hammasini o'chirish</td></tr>
<tr><td><code>git stash apply stash@{2}</code></td><td>2-stash (indeks bo'yicha)</td></tr>
</table>

<h4>2. Stash use cases</h4>

<ol>
<li>Yarim ishni vaqtinchalik saqlash (branch o'zgartirish uchun)</li>
<li><code>git pull</code> oldidan local o'zgartirishlarni saqlash</li>
<li>Tezda eksperiment qilish — keyin qaytarish</li>
<li>"Bu fayl tahrirlandi, lekin commit'ga kirmasin"</li>
</ol>

<h4>3. Cherry-pick batafsil</h4>

<pre><code># Bitta commit
git cherry-pick abc1234

# Bir nechta commit (ketma-ket)
git cherry-pick abc1234 def5678 9012345

# Commit oraliq
git cherry-pick abc1234..def5678   # abc'dan keyin def'gacha

# Commit qilmasdan (faqat staging'ga)
git cherry-pick -n abc1234

# Conflict bo'lsa
git cherry-pick abc1234
# CONFLICT...
# Yeching, keyin:
git add .
git cherry-pick --continue
# Yoki bekor qilish:
git cherry-pick --abort</code></pre>

<h4>4. Amend qoidalari</h4>

<table>
<tr><th>Vaziyat</th><th>Yo'l</th></tr>
<tr><td>Push qilmagan, xabar xato</td><td>✅ <code>git commit --amend -m "yangi"</code></td></tr>
<tr><td>Push qilmagan, fayl unutilgan</td><td>✅ <code>git add fayl && git commit --amend</code></td></tr>
<tr><td>Push qilingan, shaxsiy branch</td><td>⚠️ <code>amend + push --force-with-lease</code></td></tr>
<tr><td>Push qilingan, main / shared branch</td><td>❌ <strong>amend qilmang</strong>. Yangi commit yarating</td></tr>
</table>

<h4>5. Alias'lar — kunlik tezlik</h4>

<pre><code>git config --global alias.s "status -s"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.cm "commit -m"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.unstage "reset HEAD --"

# Endi:
git s
git lg
git amend
git unstage main.py</code></pre>

<h4>6. Stash pro tips</h4>

<pre><code># Faqat tracked fayllarni stash
git stash

# Untracked fayllarni ham
git stash -u

# Hammasini (gitignore'dagilarni ham — xavfli!)
git stash -a

# Aniq fayllarni
git stash push -m "WIP" main.py utils.py

# Stash'dan branch yaratish
git stash branch yangi-feature stash@{0}</code></pre>

<h4>7. Reset --soft bilan amend alternativi</h4>

<pre><code># Oxirgi commit'ni "ochib" — staging'ga qaytarish
git reset --soft HEAD~1

# Endi yangi commit'lar yarating yoki yana add qiling
git commit -m "yangi xabar"</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>git stash</code> — yarim ishni vaqtinchalik saqlash</li>
<li>✅ <code>git stash pop</code> — qaytarish</li>
<li>✅ <code>git cherry-pick</code> — boshqa branch'dan faqat 1 commit</li>
<li>✅ <code>git commit --amend</code> — oxirgi commit'ni tahrirlash</li>
<li>✅ Push qilingan commit'ni amend qilmang!</li>
<li>✅ Foydali alias'lar (lg, amend, s)</li>
<li>✅ <code>git stash -u</code> — untracked ham</li>
</ul>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 7: Stash, cherry-pick, amend
# ════════════════════════════════════════════════════════════════════

cd mening-loyiham

# ─────────────────────────────────────────────────────────────────────
# 1) STASH — eng oddiy
# ─────────────────────────────────────────────────────────────────────

# Senariy: yarim ish, boshqa branchga o'tish kerak
echo "# Yarim ish" >> README.md

git status
# modified: README.md

# Vaqtinchalik saqlash
git stash
# Saved working directory: WIP on main

git status
# nothing to commit, working tree clean

# Boshqa branchga o'tib ish qilish
git switch -c hotfix/critical
echo "BUG FIX" >> main.py
git add main.py
git commit -m "fix: critical"

# Yarim ishga qaytish
git switch main
git stash pop
# o'zgarish qaytdi:
git status
# modified: README.md

# ─────────────────────────────────────────────────────────────────────
# 2) STASH list, show, named
# ─────────────────────────────────────────────────────────────────────

# Bir nechta stash
echo "ish 1" >> a.txt
git stash push -m "WIP: yangi feature"

echo "ish 2" >> b.txt
git stash push -m "WIP: bug fix"

# Ro'yxat
git stash list
# stash@{0}: On main: WIP: bug fix
# stash@{1}: On main: WIP: yangi feature

# Mazmunni ko'rish
git stash show
git stash show -p stash@{1}    # to'liq diff

# Belgilangan stash'ni qaytarish
git stash apply stash@{1}
# (faqat apply — stash'da qoladi)

# pop — qaytarish + o'chirish
git stash pop stash@{0}

# Hammasini o'chirish
git stash clear

# ─────────────────────────────────────────────────────────────────────
# 3) STASH untracked fayllar
# ─────────────────────────────────────────────────────────────────────

# Yangi fayl yaratamiz
echo "yangi" > yangi.txt

git stash
# yangi.txt stash'ga TUSHMAYDI (untracked)

# -u flag bilan
git stash -u
# yangi.txt ham stash'ga tushdi

# Hammasini (gitignore'dagilarni ham)
# git stash -a    # xavfli, ehtiyot bo'ling

# ─────────────────────────────────────────────────────────────────────
# 4) STASH'dan branch
# ─────────────────────────────────────────────────────────────────────

# Stash'dagi ish endi to'liq feature bo'lib qoldi
echo "katta ish" >> README.md
git stash push -m "yangi katta feature"

git stash list
# stash@{0}: WIP yangi katta feature

# Bevosita branch yaratish
git stash branch feature/katta-ish stash@{0}
# yangi branchda turibsiz, stash o'chgan, o'zgartirishlar tiklangan

# ─────────────────────────────────────────────────────────────────────
# 5) CHERRY-PICK
# ─────────────────────────────────────────────────────────────────────

# Boshqa branchda commit'lar
git switch -c feature/many
echo "ish 1" > f1.py && git add . && git commit -m "feat: 1"
echo "ish 2" > f2.py && git add . && git commit -m "feat: 2"
echo "BUG FIX" > f3.py && git add . && git commit -m "fix: critical bug"
echo "ish 4" > f4.py && git add . && git commit -m "feat: 4"

git log --oneline
# d4 (HEAD -> feature/many) feat: 4
# c3 fix: critical bug
# b2 feat: 2
# a1 feat: 1

# main'ga qaytamiz va faqat fix'ni olamiz
git switch main

# c3 SHA'sini eslab qoling
git cherry-pick c3
# [main yangi_sha] fix: critical bug

git log --oneline
# yangi_sha (HEAD -> main) fix: critical bug
# ... (oldingi)

# ─────────────────────────────────────────────────────────────────────
# 6) CHERRY-PICK ko'pchilik
# ─────────────────────────────────────────────────────────────────────

# Bir nechta
git cherry-pick a1 b2 d4

# Oraliq (a'dan d'gacha — d ham kiradi)
git cherry-pick a1^..d4

# Commit qilmasdan (faqat staging'ga)
git cherry-pick -n c3

# Conflict bo'lsa
git cherry-pick c3
# CONFLICT...
# (yeching)
git add .
git cherry-pick --continue

# Yoki bekor qilish
# git cherry-pick --abort

# ─────────────────────────────────────────────────────────────────────
# 7) AMEND — xabar tuzatish
# ─────────────────────────────────────────────────────────────────────

git commit -m "fix something"

# Xabar yomon — tuzatamiz
git commit --amend -m "fix: login formada email validatsiyasi"

# Editor ochilishi (xabar batafsil yozish)
# git commit --amend

# ─────────────────────────────────────────────────────────────────────
# 8) AMEND — fayl qo'shish
# ─────────────────────────────────────────────────────────────────────

echo "yangi qator" >> main.py
git add main.py

# --no-edit — xabar o'zgarmaydi
git commit --amend --no-edit

# Yoki yangi xabar
# git commit --amend -m "feat: to'liq versiya"

git log --oneline
# (oxirgi commit yangi SHA bilan — amend yangi commit yaratdi)

# ─────────────────────────────────────────────────────────────────────
# 9) PUSH qilingan commit'ni amend (XAVFLI)
# ─────────────────────────────────────────────────────────────────────

# git commit -m "feat: X"
# git push                        # GitHub'da
# git commit --amend -m "feat: yangi xabar"
# git push                        # REJECTED — yangi SHA

# Yagona yo'l (xavfli):
# git push --force-with-lease    # boshqa eski commit'ga ustidan emas

# Faqat shaxsiy branch'da va jamoadosh bilan kelishilgan.
# Main yoki shared branch'da — ASLO.

# ─────────────────────────────────────────────────────────────────────
# 10) FOYDALI ALIAS'LAR
# ─────────────────────────────────────────────────────────────────────

git config --global alias.s "status -s"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.cm "commit -m"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.unstage "reset HEAD --"
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.pf "push --force-with-lease"

# Tekshirish
git config --get-regexp alias

# Endi:
git s         # status
git lg        # tarix grafigi
git amend     # oxirgi'ga add qilish
git unstage main.py
"""
L8_TEXT = """\
<h2>Rebase vs Merge — qachon qaysini</h2>

<pre class="mermaid">
flowchart TB
    M["MERGE\nmerge commit yaratiladi\ntarix oson tushuniladi\nashardumshani saqlaydi"]
    R["REBASE\ncommit'lar yangidan yoziladi\nlinear tarix\ntoza, lekin tarix qayta yoziladi"]
</pre>

<p>Bu — Git'ning eng debatable mavzularidan biri. Ham <strong>merge</strong>, ham <strong>rebase</strong> bir maqsad — branch'ni yangilash. Lekin yo'l boshqacha. Har birining tarafdorlari va dushmanlari bor.</p>

<p>Asosiy farq: <strong>merge</strong> tarixni saqlaydi (haqiqiy "qanday bo'lganini"), <strong>rebase</strong> tarixni qayta yozadi (chiroyli, linear).</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — merge</h4>

<pre><code>main:     A --- B --- C
                       \\
feature:                D --- E

# Senariy: main ham yangilangan
main:     A --- B --- C --- F
                       \\
feature:                D --- E

# git merge main (feature'da)
main:     A --- B --- C --- F
                       \\     \\
feature:                D --- E --- M  (merge commit)</code></pre>

<h4>BLOKA 2 — rebase</h4>

<pre><code>main:     A --- B --- C --- F
                       \\
feature:                D --- E

# git rebase main (feature'da)
main:     A --- B --- C --- F
                              \\
feature:                       D' --- E'   (yangi commit'lar)</code></pre>

<p>Diqqat: <strong>D' va E'</strong> — bu yangi commit'lar (yangi SHA bilan). Mazmuni o'sha — lekin Git nuqtai nazaridan butunlay yangi. Tarix toza: F → D' → E' (linear, merge commit yo'q).</p>

<h4>BLOKA 3 — amaliyot</h4>

<pre><code># Feature branch'da turibsiz
git switch feature/login

# main yangiliklari bilan rebase
git rebase main
# Successfully rebased and updated refs/heads/feature/login.

# Endi feature main'ning eng yangi versiyasi ustida</code></pre>

<h3>🐛 Ataylab xato (jamoadagi katastrofa)</h3>
<pre><code># Push qilingan branch'da rebase
git switch feature/login
# (sherigingiz ham shu branch'da ishlamoqda)
git rebase main
git push --force        # ❌
# Sherigingizning ish yo'qoladi!</code></pre>

<p><strong>Sabab:</strong> Rebase commit'lar SHA'sini o'zgartiradi. Sherigingizning lokal'ida eski SHA'lar bor. Pull qilganda — ikkita tarix to'qnashadi, conflict yoki ma'lumot yo'qoladi.</p>

<p><strong>Oltin qoidasi:</strong> <strong>Push qilingan commit'larni rebase qilmang</strong> (faqat o'z shaxsiy branch'da, hech kim ishlatmasa).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Qachon merge, qachon rebase?</h4>

<table>
<tr><th>Vaziyat</th><th>Tavsiya</th></tr>
<tr><td>main'ni feature'ga olib kelish</td><td><strong>Rebase</strong> (tarix toza)</td></tr>
<tr><td>feature'ni main'ga qo'shish</td><td><strong>Merge</strong> (squash ham mumkin)</td></tr>
<tr><td>Jamoa ishlaydigan branch</td><td><strong>Merge</strong> (rebase xavfli)</td></tr>
<tr><td>Shaxsiy branch tarixini tozalash</td><td><strong>Rebase</strong> (interactive)</td></tr>
<tr><td>Push qilingan commit'lar</td><td><strong>Merge</strong> (rebase qilmang)</td></tr>
</table>

<h4>2. Interactive rebase — eng kuchli</h4>

<p>3 ta commit qildingiz, lekin 1 ta katta commit'ga birlashtirmoqchimisiz? Yoki birinchi commit xabari xato? Interactive rebase.</p>

<pre><code># Oxirgi 3 commit
git rebase -i HEAD~3

# Editor ochiladi:
# pick abc1234 feat: A
# pick def5678 feat: B
# pick 9012345 feat: C

# Buyruqlar:
# pick   = saqlash (default)
# reword = saqlash + xabar tuzatish
# edit   = to'xtatish + tahrirlash
# squash = oldingiga birlashtirish + xabar tuzatish
# fixup  = oldingiga birlashtirish (xabar tashlash)
# drop   = o'chirish
# reorder = qatorlarni o'rin almashtirish</code></pre>

<h4>3. Squash misol — 3 ni 1 ga</h4>

<pre><code># Avval
git log --oneline
# c3 feat: C
# b2 feat: B
# a1 feat: A
# main

# git rebase -i HEAD~3
# pick a1 feat: A
# squash b2 feat: B
# squash c3 feat: C

# Editor — yangi xabar:
# feat: A, B, C — to'liq feature

# Natija
git log --oneline
# yangi feat: A, B, C — to'liq feature
# main</code></pre>

<h4>4. Conflict rebase'da</h4>

<pre><code>git rebase main
# CONFLICT (content): Merge conflict in main.py

# Yeching
vim main.py
git add main.py

# DIQQAT: rebase'da `git commit` YO'Q
# Buni qiling:
git rebase --continue

# Yoki bekor qilish (eski holatga):
git rebase --abort</code></pre>

<h4>5. Pull strategiyalari</h4>

<pre><code># Default — merge
git pull
# = git fetch + git merge

# Rebase bilan
git pull --rebase
# = git fetch + git rebase
# Tarix toza qoladi (merge commit yo'q)

# Default sozlash
git config --global pull.rebase true</code></pre>

<h4>6. Force push xavfsiz versiyasi</h4>

<p>Rebase keyin push'ga ehtiyoj bor — chunki SHA o'zgargan. Lekin <code>--force</code> emas:</p>

<pre><code>git push --force-with-lease
# Agar remote'da boshqa eski commit'dan keyin yangi bo'lsa, push to'xtaydi
# (kim bo'lsa boshqa ish qilgan — siz overwrite qilmaysiz)</code></pre>

<h4>7. Squash and merge (GitHub) — rebase alternativi</h4>

<p>GitHub PR'da <strong>Squash and merge</strong> tugmasi — bu rebase'ning oddiy versiyasi. PR'dagi 10 ta commit → 1 ta clean commit main'da. Ko'p loyihalar shu yondashuvni ishlatadi — siz rebase haqida o'ylamasangiz ham bo'ladi.</p>

<h4>8. Tartib — eng yaxshi amaliyot</h4>

<pre><code># Har kuni boshlaganda
git switch main
git pull --rebase    # main'ni yangilash

git switch feature/men
git rebase main      # men'ning branchni main'ga moslash
# (conflict bo'lsa yeching)

# Ish davom
# ...

# Push (rebase keyin)
git push --force-with-lease</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Merge — tarix saqlanadi, merge commit yaratiladi</li>
<li>✅ Rebase — commit'lar qayta yoziladi, linear tarix</li>
<li>✅ Rebase qoidasi: <strong>push qilingan commit'larda QILMANG</strong></li>
<li>✅ Interactive rebase (squash, reword, drop, reorder)</li>
<li>✅ <code>git pull --rebase</code> default sifatida</li>
<li>✅ <code>git push --force-with-lease</code> (force emas)</li>
<li>✅ GitHub "Squash and merge" — rebase'siz toza tarix</li>
</ul>
"""

L8_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 8: Rebase vs Merge
# ════════════════════════════════════════════════════════════════════

cd mening-loyiham

# ─────────────────────────────────────────────────────────────────────
# 1) Test scenariy yaratamiz
# ─────────────────────────────────────────────────────────────────────

git switch main

# Boshlang'ich
echo "A" > x.txt
git add . && git commit -m "feat: A"

echo "B" >> x.txt
git add . && git commit -m "feat: B"

# Feature branch
git switch -c feature/test
echo "C" >> x.txt
git add . && git commit -m "feat: C"

echo "D" >> x.txt
git add . && git commit -m "feat: D"

# main'ga qaytib boshqa ish
git switch main
echo "E (main)" >> y.txt
git add . && git commit -m "feat: E"

# Tarix
git log --oneline --graph --all
# * E (main)
# | * D (feature/test)
# | * C
# |/
# * B
# * A

# ─────────────────────────────────────────────────────────────────────
# 2) MERGE yondashuvi
# ─────────────────────────────────────────────────────────────────────

git switch feature/test

# main'ni feature'ga merge
git merge main
# Auto-merging or merge commit

# Tarix
git log --oneline --graph
# *   merge_commit Merge branch 'main' into feature/test
# |\\
# | * E (main)
# * | D
# * | C
# |/
# * B
# * A

# ─────────────────────────────────────────────────────────────────────
# 3) Yangi scenariy — REBASE
# ─────────────────────────────────────────────────────────────────────

# Toza boshlash
git switch main
git branch -D feature/test 2>/dev/null

git switch -c feature/test2
echo "C2" >> x.txt && git add . && git commit -m "feat: C2"
echo "D2" >> x.txt && git add . && git commit -m "feat: D2"

git switch main
echo "F (main)" >> z.txt && git add . && git commit -m "feat: F"

git switch feature/test2

# Avval tarix
git log --oneline --graph --all

# REBASE — feature'ni main ustiga ko'chirish
git rebase main
# Successfully rebased and updated refs/heads/feature/test2.

# Endi tarix LINEAR
git log --oneline --graph --all
# * D2' (feature/test2) feat: D2
# * C2' feat: C2
# * F (main) feat: F
# * E feat: E
# * B feat: B
# * A feat: A

# D2 va C2 ning SHA'si BOSHQA endi (rebase yangi commit yaratdi)

# ─────────────────────────────────────────────────────────────────────
# 4) Rebase conflict
# ─────────────────────────────────────────────────────────────────────

git switch main
echo "main version" > shared.txt
git add . && git commit -m "feat: shared from main"

git switch -c feature/conflict
echo "feature version" > shared.txt
git add . && git commit -m "feat: shared from feature"

git switch main
echo "main yana" > shared.txt
git add . && git commit -m "feat: shared yangilandi"

git switch feature/conflict
git rebase main
# CONFLICT (content): Merge conflict in shared.txt

# Yeching
echo "yakuniy" > shared.txt
git add shared.txt

# DIQQAT: rebase'da `git commit` YO'Q
git rebase --continue

# Yoki bekor qilish
# git rebase --abort

# ─────────────────────────────────────────────────────────────────────
# 5) INTERACTIVE REBASE — squash
# ─────────────────────────────────────────────────────────────────────

git switch main
git switch -c feature/wip

echo "1" > a.py && git add . && git commit -m "WIP 1"
echo "2" >> a.py && git add . && git commit -m "WIP 2"
echo "3" >> a.py && git add . && git commit -m "WIP 3"
echo "yakuniy" > a.py && git add . && git commit -m "feat: clean version"

git log --oneline
# d4 feat: clean version
# c3 WIP 3
# b2 WIP 2
# a1 WIP 1

# 4 ta commit'ni 1 ga birlashtirish
git rebase -i HEAD~4
# Editor ochiladi:
# pick a1 WIP 1
# pick b2 WIP 2
# pick c3 WIP 3
# pick d4 feat: clean version

# O'zgartiring:
# pick a1 WIP 1
# squash b2 WIP 2
# squash c3 WIP 3
# squash d4 feat: clean version

# Saqlash → yangi editor (xabar uchun)
# # Editor:
# feat: yangi feature to'liq versiya

# Natija
git log --oneline
# yangi_sha feat: yangi feature to'liq versiya
# main

# ─────────────────────────────────────────────────────────────────────
# 6) INTERACTIVE — reword, reorder, drop
# ─────────────────────────────────────────────────────────────────────

# Oxirgi 5 commit
git rebase -i HEAD~5

# Editor:
# pick a1 feat: A
# pick b2 feat B (chastota)        ← typo
# pick c3 fix: yana bir bug
# pick d4 WIP                       ← o'chirish kerak
# pick e5 feat: E

# O'zgartirish:
# pick a1 feat: A
# reword b2 feat B                  ← reword
# pick e5 feat: E                   ← order
# pick c3 fix: yana bir bug
# drop d4 WIP                       ← drop

# Saqlash → reword uchun editor → e'tibor: order o'zgargan

# ─────────────────────────────────────────────────────────────────────
# 7) PULL --rebase
# ─────────────────────────────────────────────────────────────────────

git switch main
git pull --rebase
# = git fetch + git rebase origin/main

# Default sifatida sozlash
git config --global pull.rebase true

# Endi git pull avtomatik rebase ishlatadi

# ─────────────────────────────────────────────────────────────────────
# 8) FORCE PUSH — xavfsiz versiya
# ─────────────────────────────────────────────────────────────────────

git switch feature/wip
git rebase main      # commit SHA'lar o'zgardi

# Push — eski SHA'lar overwrite qilish kerak
git push --force-with-lease
# Agar remote'da YANGI commit bo'lsa (boshqa kim bo'lsa) — push to'xtaydi

# Eski xavfli:
# git push --force      # o'qotmang!

# ─────────────────────────────────────────────────────────────────────
# 9) Kunlik workflow — eng yaxshi amaliyot
# ─────────────────────────────────────────────────────────────────────

# Kun boshida
git switch main
git pull --rebase

# Yangi feature
git switch -c feature/yangi

# ... ish ...
git add . && git commit -m "feat: X"
git add . && git commit -m "feat: Y"

# main'da yangilik bo'lsa — feature'ni moslash
git switch main
git pull --rebase
git switch feature/yangi
git rebase main
# Conflict bo'lsa yeching, --continue

# Push
git push -u origin feature/yangi
# Yoki rebase keyin:
# git push --force-with-lease

# PR yarating
gh pr create

# Merge bo'lgach
git switch main
git pull --rebase
git branch -d feature/yangi
"""
L9_TEXT = """\
<h2>Reset, revert, reflog — qutqarish texnikalari</h2>

<pre class="mermaid">
flowchart LR
    RESET["RESET\ntarixdan o'chiradi\n(xavfli, push qilingan emas uchun)"]
    REVERT["REVERT\nyangi commit qaytarish bilan\n(xavfsiz, push qilingan uchun)"]
    REFLOG["REFLOG\nhar harakatni eslab qoladi\n(yo'qotgan commit'ni topish)"]
</pre>

<p>Adashtirib commit qildingiz? Master branchni o'chirib yubordingiz? Force push bilan barcha tarixni yo'qotgansiz? <strong>Tinchlaning</strong>. Git'da deyarli hech narsa abadiy yo'qolmaydi. Bu darsda 3 ta hayot saqlovchi qurol:</p>

<ul>
<li><strong>reset</strong> — tarixdan commit'larni olib tashlash</li>
<li><strong>revert</strong> — commit'ni bekor qilish (yangi commit bilan)</li>
<li><strong>reflog</strong> — har bir harakatning jurnali — "qaerga ketdim?"</li>
</ul>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — reset (3 ta darajada)</h4>

<pre><code># Holat: oxirgi commit yomon
git log --oneline
# def5678 (HEAD -&gt; main) "WIP yarim ish"
# abc1234 yaxshi commit

# RESET --soft — commit o'chadi, lekin fayllar staging'da qoladi
git reset --soft HEAD~1
# Endi commit'ni qaytadan qilish mumkin (xabarni o'zgartirish)

# RESET --mixed (default) — commit + staging tozalanadi, fayllar saqlanadi
git reset HEAD~1
# Fayllar working dir'da, lekin add qilinmagan

# RESET --hard — COMMIT + STAGING + FAYLLAR yo'qoladi
git reset --hard HEAD~1
# ⚠️ XAVFLI — fayllaringizni yo'qotasiz</code></pre>

<h4>BLOKA 2 — revert (xavfsiz)</h4>

<pre><code># Push qilingan commit — reset xavfli (tarix o'zgaradi)
# Revert — yangi commit yaratadi, eski'ni bekor qiluvchi

git log --oneline
# def5678 (HEAD -&gt; main) "BUG: hammasini o'chirdi"  ← yomon
# abc1234 yaxshi

# Revert
git revert def5678
# [main yangi_sha] Revert "BUG: hammasini o'chirdi"

git log --oneline
# yangi_sha Revert "BUG..."
# def5678 BUG: hammasini o'chirdi
# abc1234 yaxshi

# Push xavfsiz — yangi commit, tarix saqlanadi
git push</code></pre>

<h4>BLOKA 3 — reflog (eng kuchli)</h4>

<pre><code># Faraz: tasodifan reset --hard qildingiz, ish yo'qoldi
# PANIKA emas — reflog hammasini eslab qoladi

git reflog
# def5678 HEAD@{0}: reset: moving to HEAD~1
# abc1234 HEAD@{1}: commit: yaxshi commit
# 9012345 HEAD@{2}: commit: oldingi
# ...

# Yo'qolgan ishga qaytish
git reset --hard abc1234

# Yoki branch yaratish o'sha SHA dan
git branch saved-work abc1234</code></pre>

<h3>🐛 Ataylab xato (eng katta)</h3>
<pre><code># Push qilingan commit'da reset
git reset --hard HEAD~5     # 5 commit oldinga
git push --force            # ❌ Jamoadosh tarixi yo'qoladi!</code></pre>

<p><strong>Sabab:</strong> Reset tarixni qayta yozadi. Push qilingan commit'lar GitHub'da. Force push — jamoadoshlarning ishlarini o'chiradi. Birgan ishlaydigan jamoa uchun katastrofa.</p>

<p><strong>Yechim:</strong> Push qilingan commit uchun <code>revert</code> ishlatish. U yangi commit yaratadi — tarix saqlanadi.</p>

<table>
<tr><th>Vaziyat</th><th>Yo'l</th></tr>
<tr><td>Push qilmagan, lokal</td><td>Reset (har xil)</td></tr>
<tr><td>Push qilingan</td><td>Revert</td></tr>
<tr><td>Yo'qolgan ishni topish</td><td>Reflog</td></tr>
</table>

<h3>Endi tushuntiramiz</h3>

<h4>1. Reset 3 ta darajada — to'liq jadval</h4>

<table>
<tr><th>Flag</th><th>Commit</th><th>Staging</th><th>Working dir</th></tr>
<tr><td><code>--soft</code></td><td>O'chiriladi</td><td>Saqlanadi</td><td>Saqlanadi</td></tr>
<tr><td><code>--mixed</code> (default)</td><td>O'chiriladi</td><td>Tozalanadi</td><td>Saqlanadi</td></tr>
<tr><td><code>--hard</code></td><td>O'chiriladi</td><td>Tozalanadi</td><td>Yo'qoladi (xavfli)</td></tr>
</table>

<h4>2. Reset misollari</h4>

<pre><code># Oxirgi 3 commit'ni "ochish" (xabarni qaytadan)
git reset --soft HEAD~3

# Oxirgi commit'ni undo qilish (fayllarni saqlab)
git reset HEAD~1

# Hammasini eski holatga (xavfli)
git reset --hard origin/main

# Staging'dan olib tashlash (faylni)
git reset HEAD main.py
# yoki zamonaviy:
git restore --staged main.py</code></pre>

<h4>3. Revert</h4>

<pre><code># Bitta commit'ni bekor qilish
git revert abc1234

# Bir nechta
git revert abc1234 def5678

# Oraliq
git revert abc1234..def5678

# Commit qilmasdan (faqat o'zgartirish staging'da)
git revert -n abc1234

# Merge commit'ni revert (-m bilan parent ko'rsatish)
git revert -m 1 merge_sha</code></pre>

<h4>4. Reflog — hayot saqlovchi</h4>

<pre><code># Reflog — har lokal harakat (commit, reset, checkout, merge)
git reflog
# def5678 HEAD@{0}: commit: yangi
# abc1234 HEAD@{1}: checkout: moving from feature to main
# 9012345 HEAD@{2}: commit: x
# ...

# Filter
git reflog --since="2 days ago"

# Branch'ning reflog'i
git reflog feature/login

# Reflog HEAD'dan branch yaratish
git branch saved HEAD@{5}</code></pre>

<p>Reflog faqat <strong>lokal</strong>. Push qilinganidan keyin yo'qolgan ish — GitHub'da bo'lishi mumkin (orphan branch, GC oldida).</p>

<h4>5. Foydali qutqarish senariylari</h4>

<p><strong>Senariy 1:</strong> Branch'ni tasodifan o'chirdingiz.</p>
<pre><code>git reflog                  # branch oxirgi SHA'sini topish
git branch yangi-branch &lt;SHA&gt;</code></pre>

<p><strong>Senariy 2:</strong> Force push bilan boshqa odam tarix overwrite qildi.</p>
<pre><code>git reflog                  # eski commit'lar lokal'da bor
git reset --hard HEAD@{1}   # eski holatga</code></pre>

<p><strong>Senariy 3:</strong> Yarim ishni tasodifan reset --hard qildingiz.</p>
<pre><code>git reflog                  # commit qilmagan o'zgarishlar topish qiyin
# Agar add qilgan bo'lsangiz — git fsck --lost-found
# Kommit qilmagan + add qilmagan — afsus, yo'qoldi</code></pre>

<h4>6. Detached HEAD — sayyora</h4>

<pre><code># Belgilangan commit'ga checkout
git checkout abc1234
# Note: switching to 'abc1234'.
# You are in 'detached HEAD' state. ...

# Endi siz branch'da emas — sayyora commit'da
# Yangi commit qilsangiz, branch'siz qoladi → yo'qoladi

# Yechim — branch yaratish
git switch -c yangi-branch
# yoki main'ga qaytish
git switch main</code></pre>

<h4>7. clean — kuzatilmayotgan fayllarni o'chirish</h4>

<pre><code># Avval ko'rib chiqish (dry run)
git clean -n
# Would remove: tmp.log, build/, ...

# O'chirish (fayllarni)
git clean -f

# Papkalarni ham
git clean -fd

# .gitignore'dagilarni ham
git clean -fX     # faqat .gitignore'dagilar
git clean -fx     # hammasi</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>git reset</code> 3 daraja: --soft, --mixed (default), --hard</li>
<li>✅ <code>git revert</code> — yangi commit bilan bekor qilish (xavfsiz)</li>
<li>✅ Push qilingan commit — revert, reset emas</li>
<li>✅ <code>git reflog</code> — har harakatning jurnali, hayot saqlovchi</li>
<li>✅ Yo'qolgan branch/commit'ni reflog orqali topish</li>
<li>✅ Detached HEAD — branch yaratib chiqib ketish</li>
<li>✅ <code>git clean</code> — kuzatilmayotgan fayllarni o'chirish</li>
</ul>
"""

L9_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 9: Reset, revert, reflog
# ════════════════════════════════════════════════════════════════════

cd mening-loyiham

# ─────────────────────────────────────────────────────────────────────
# 1) RESET --soft (commit ochish, fayllar saqlanadi)
# ─────────────────────────────────────────────────────────────────────

# Test commit
echo "test" > soft.txt
git add . && git commit -m "WIP yarim ish"

git log --oneline
# abc1234 WIP yarim ish
# ... (oldingi)

# Soft reset — commit ochiladi, fayllar staging'da
git reset --soft HEAD~1

git status
# Changes to be committed:
#   new file: soft.txt

# Endi yangi xabar bilan qaytadan commit
git commit -m "feat: soft.txt qo'shildi"

# ─────────────────────────────────────────────────────────────────────
# 2) RESET --mixed (default) — fayllar saqlanadi, lekin unstaged
# ─────────────────────────────────────────────────────────────────────

echo "ish 1" > a.py
git add . && git commit -m "commit 1"

echo "ish 2" > b.py
git add . && git commit -m "commit 2"

git log --oneline
# def commit 2
# abc commit 1
# ...

# Mixed reset
git reset HEAD~2          # default --mixed

git status
# Untracked: a.py, b.py
# (yoki: not staged: modified — a.py, b.py)

# Tanlab add qilish mumkin
git add a.py
git commit -m "feat: a"

git add b.py
git commit -m "feat: b"

# ─────────────────────────────────────────────────────────────────────
# 3) RESET --hard (XAVFLI — fayllarni yo'qotasiz)
# ─────────────────────────────────────────────────────────────────────

echo "muhim" > muhim.txt
git add . && git commit -m "feat: muhim"

git log --oneline | head -3

# HAMMASINI yo'qotish (oxirgi commit)
# git reset --hard HEAD~1
# (kommit + staging + working — hammasi yo'qoladi)
# muhim.txt YO'Q

# Yoki origin/main'ga moslashtirish
# git reset --hard origin/main

# Bu — eng kuchli reset. Faqat aniq xohlaganingizda ishlatish.

# ─────────────────────────────────────────────────────────────────────
# 4) REVERT — push qilingan uchun xavfsiz
# ─────────────────────────────────────────────────────────────────────

# Bad commit
echo "yomon kod" > yomon.py
git add . && git commit -m "BUG: yomon"

git log --oneline
# bad_sha BUG: yomon
# good_sha feat: ...

# Revert — yangi commit yaratadi
git revert HEAD
# Editor ochiladi, default xabar: Revert "BUG: yomon"
# Yoki:
# git revert --no-edit HEAD     # default xabar bilan

git log --oneline
# revert_sha Revert "BUG: yomon"
# bad_sha BUG: yomon
# good_sha feat: ...

# Fayl yo'q (revert bekor qildi)
ls yomon.py
# No such file

# Push xavfsiz
# git push

# ─────────────────────────────────────────────────────────────────────
# 5) REVERT bir nechta commit
# ─────────────────────────────────────────────────────────────────────

# Faraz oxirgi 3 ta yomon
git log --oneline
# c3 (HEAD) feat 3
# b2 feat 2
# a1 feat 1

# Hammasini revert (reverse order)
git revert HEAD~2..HEAD
# 3 ta yangi revert commit yaratiladi

# Yoki bir commit'ga birlashtirish
git revert --no-commit HEAD~2..HEAD
git commit -m "revert: oxirgi 3 ta yomon ish bekor qilindi"

# ─────────────────────────────────────────────────────────────────────
# 6) REFLOG — hayot saqlovchi
# ─────────────────────────────────────────────────────────────────────

# Reflog ko'rish
git reflog
# abc1234 HEAD@{0}: commit: oxirgi ish
# def5678 HEAD@{1}: reset: moving to HEAD~1
# 9012345 HEAD@{2}: commit: muhim ish    ← YO'QOLGAN
# ...

# Yo'qolgan commit'ga qaytish
git reset --hard 9012345

# Yoki yangi branch yaratish
git branch saved-work 9012345

# Filter
git reflog --since="1 hour ago"
git reflog feature/login

# ─────────────────────────────────────────────────────────────────────
# 7) Senariy: branch tasodifan o'chirildi
# ─────────────────────────────────────────────────────────────────────

git switch -c feature/important
echo "muhim ish" > muhim.py
git add . && git commit -m "feat: muhim ish"

git switch main

# Tasodifan
git branch -D feature/important
# Deleted branch feature/important (was abc1234).

# PANIKA YO'Q
git reflog
# abc1234 HEAD@{...} commit: feat: muhim ish

# Branchni qaytarish
git branch feature/important abc1234

git switch feature/important
ls muhim.py
# muhim.py — qaytdi 🎉

# ─────────────────────────────────────────────────────────────────────
# 8) Senariy: tasodifan reset --hard
# ─────────────────────────────────────────────────────────────────────

git switch main

echo "yana muhim" > yana.txt
git add . && git commit -m "feat: yana muhim"

# Tasodifan
git reset --hard HEAD~3
# 3 ta commit yo'qoldi (ko'rinishda)

ls yana.txt
# No such file

# REFLOG
git reflog
# def5678 HEAD@{0}: reset: moving to HEAD~3
# abc1234 HEAD@{1}: commit: feat: yana muhim    ← oxirgi yaxshi holat

git reset --hard HEAD@{1}
# Eski holatga
ls yana.txt
# yana.txt — qaytdi

# ─────────────────────────────────────────────────────────────────────
# 9) DETACHED HEAD
# ─────────────────────────────────────────────────────────────────────

# Belgilangan commit'ga
git checkout abc1234
# You are in 'detached HEAD' state...

# Yangi branch yaratish
git switch -c yangi-eksperiment
# Endi haqiqiy branch'da

# Yoki main'ga qaytish
git switch main

# ─────────────────────────────────────────────────────────────────────
# 10) CLEAN — kuzatilmayotgan fayllarni o'chirish
# ─────────────────────────────────────────────────────────────────────

# Yangi fayl
touch tmp1.log tmp2.tmp
mkdir bekor && touch bekor/x.txt

git status
# Untracked: tmp1.log, tmp2.tmp, bekor/

# Dry run — nimani o'chiradi
git clean -n
# Would remove tmp1.log
# Would remove tmp2.tmp
# Would remove bekor/  (faqat -d bilan)

# Papkalarni ham
git clean -nd

# Bajarish
git clean -fd
# Removed tmp1.log, tmp2.tmp, bekor/
"""
R3_TEXT = """\
<h2>R3 — Modul 3 takrorlash: Yo'qotilgan kodni qutqarish</h2>

<p>Modul 3 ning hammasi birga — <strong>recovery laboratoriyasi</strong>. Atayin xato qilamiz: branch o'chiramiz, reset --hard qilamiz, force push'ni simulyatsiya qilamiz. Va keyin <strong>reflog + reset + revert</strong> bilan hammasini qutqaramiz.</p>

<p>Bu — Git'da yashash uchun zarur ko'nikma. Birinchi marta xato qilganingizda — panika emas, balki uskunalar bor.</p>

<h3>Loyihaning maqsadi</h3>

<p>5 ta "katastrofa" senariyni simulyatsiya qiling va har birini qutqaring. Yakuniy hisobot: nima qildim → nima bo'ldi → qanday qutqardim.</p>

<h3>Topshiriqlar</h3>

<h4>Senariy 1 — Muhim branchni tasodifan o'chirish</h4>

<ul>
<li><code>feature/payment</code> branchda 5 ta commit qiling (har biri ma'noli mazmun)</li>
<li>main'ga o'tib, tasodifan <code>git branch -D feature/payment</code></li>
<li><strong>Qutqarish:</strong> reflog → branch'ni qaytadan yaratish</li>
</ul>

<h4>Senariy 2 — reset --hard bilan ish yo'qotish</h4>

<ul>
<li>main'da 3 ta yangi commit qiling</li>
<li>Tasodifan <code>git reset --hard HEAD~3</code></li>
<li><strong>Qutqarish:</strong> reflog → eski holatga reset</li>
</ul>

<h4>Senariy 3 — Push qilingan yomon commit</h4>

<ul>
<li>main'da push qilingan kerakli commit'lar bor</li>
<li>Yomon commit qiling (masalan, "DELETE ALL")</li>
<li>Push qiling (sizning shaxsiy test repo'da xavfsiz)</li>
<li><strong>Qutqarish:</strong> revert (reset emas — chunki push qilingan)</li>
</ul>

<h4>Senariy 4 — Wrong branch'da commit</h4>

<ul>
<li>main'da turibsiz</li>
<li>Yangi feature uchun 3 ta commit qildingiz</li>
<li>Eslab oldingiz: "voy, bu feature/profile branchda bo'lishi kerak edi!"</li>
<li><strong>Qutqarish:</strong> branch yaratish + reset main'da</li>
</ul>

<h4>Senariy 5 — Detached HEAD'da ish</h4>

<ul>
<li><code>git checkout HEAD~3</code> — detached HEAD holatida</li>
<li>2 ta commit qildingiz</li>
<li>Boshqa branch'ga o'tdingiz</li>
<li>Endi commit'lar yo'q (branch'siz qoldi)</li>
<li><strong>Qutqarish:</strong> reflog → branch yaratish o'sha SHA dan</li>
</ul>

<h4>Bonus senariy 6 — Conflict bo'lganda rebase'ni bekor qilish</h4>

<ul>
<li>Rebase bilan conflict</li>
<li>Yarim yechgansiz, lekin xato qilgansiz</li>
<li><code>git rebase --abort</code> — boshlanish holatga qaytish</li>
</ul>

<h3>🐛 Ataylab eng qiyin: 2 daraja recovery</h3>

<p>1) Branch'ni o'chirib qo'ydingiz. 2) Reflog'dan SHA topib, lekin yangi branch yaratishdan oldin <code>git gc</code> ishlatdingiz (garbage collector).</p>

<p>Endi reflog SHA'si ham ko'rinmasligi mumkin. Yo'l: <code>git fsck --lost-found</code>. Bu — "yo'qolgan ob'ektlar" papkasiga qaraydi.</p>

<h3>Hisobot template</h3>

<pre><code># Recovery hisoboti

## Senariy 1: Branch o'chirildi

### Nima qildim
git branch -D feature/payment

### Nima bo'ldi
5 ta commit "ko'rinishidan" yo'qoldi

### Qanday qutqardim
git reflog | grep payment    # SHA topish
git branch feature/payment &lt;SHA&gt;

### Natija
Branch va commit'lar tiklandi ✅

---

## Senariy 2: ...
...</code></pre>

<h3>Yechim sketch</h3>

<details>
<summary>Hamma senariy uchun bosqichma-bosqich</summary>
<pre><code>cd qutqarish-lab && git init

# Boshlang'ich commit
echo "boshlanish" &gt; README.md
git add . && git commit -m "init"

# ─── SENARIY 1: branch o'chirish ───
git switch -c feature/payment
for i in 1 2 3 4 5; do
    echo "payment $i" &gt;&gt; payment.py
    git add . && git commit -m "feat: payment step $i"
done

git switch main
git branch -D feature/payment   # ❌

# Qutqarish
git reflog
# SHA topish: oxirgi feature commit
SHA=$(git reflog | grep "payment step 5" | head -1 | awk '{print $1}')
git branch feature/payment $SHA
git switch feature/payment
git log --oneline   # ✅ qaytdi

# ─── SENARIY 2: reset --hard ───
git switch main
for i in 1 2 3; do
    echo "ish $i" &gt;&gt; ish.py
    git add . && git commit -m "feat: ish $i"
done

git reset --hard HEAD~3   # ❌

# Qutqarish
git reflog
# HEAD@{1} — reset oldidan
git reset --hard HEAD@{1}   # ✅

# ─── SENARIY 3: push qilingan yomon commit ───
# (lokal simulyatsiya — push'siz)
echo "DELETE ALL" &gt; bad.py
git add . && git commit -m "BUG: delete everything"

# Revert
git revert HEAD --no-edit   # ✅ yangi commit bekor qiluvchi

# ─── SENARIY 4: wrong branch ───
git switch main
echo "feature 1" &gt; new1.py && git add . && git commit -m "feat: f1"
echo "feature 2" &gt; new2.py && git add . && git commit -m "feat: f2"
echo "feature 3" &gt; new3.py && git add . && git commit -m "feat: f3"

# Voy — bu main'da emas, profile branchda bo'lishi kerak edi
# Qutqarish
git branch feature/profile        # main'dan branch yaratish (joriy SHA)
git reset --hard HEAD~3            # main'ni 3 commit oldinga qaytarish
git switch feature/profile         # endi 3 ta commit shu yerda ✅

# ─── SENARIY 5: detached HEAD ───
git switch main
git checkout HEAD~2       # ⚠️ detached HEAD
echo "ekspriment 1" &gt; exp.py
git add . && git commit -m "exp: 1"
echo "ekspriment 2" &gt;&gt; exp.py
git add . && git commit -m "exp: 2"

git switch main           # ❌ commit'lar branch'siz qoldi

# Qutqarish
git reflog | grep "exp"
SHA=$(git reflog | grep "exp: 2" | head -1 | awk '{print $1}')
git branch experiment $SHA   # ✅
git switch experiment</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 3 ning hammasi: reset, revert, reflog birga</li>
<li>✅ Real recovery senariylari — har dasturchi uchratadi</li>
<li>✅ Panika emas — Git'da deyarli hech narsa abadiy yo'qolmaydi</li>
<li>✅ Reflog — lokal hayot saqlovchi</li>
<li>✅ Qachon reset, qachon revert tanlash</li>
</ul>
"""

R3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 3: Yo'qotilgan kodni qutqarish — laboratoriyasi
# Modul 3: reset + revert + reflog
# ════════════════════════════════════════════════════════════════════

# Toza laboratoriya
mkdir qutqarish-lab && cd qutqarish-lab
git init
echo "boshlang'ich" > README.md
git add . && git commit -m "init"

# ─────────────────────────────────────────────────────────────────────
# SENARIY 1: Muhim branchni tasodifan o'chirish
# ─────────────────────────────────────────────────────────────────────

# Sozlash
git switch -c feature/payment
for i in 1 2 3 4 5; do
    echo "payment kod step $i" >> payment.py
    git add . && git commit -m "feat: payment step $i"
done

git log --oneline
# 5 ta commit + init

git switch main

# ❌ KATASTROFA
git branch -D feature/payment
# Deleted branch feature/payment (was abc1234).

# 🚨 QUTQARISH
git reflog
# Eng yuqori — oxirgi harakatlar
# abc1234 HEAD@{0}: checkout: moving from feature/payment to main
# def5678 HEAD@{1}: commit: feat: payment step 5

# SHA topish — oxirgi feature/payment HEAD
SHA=$(git reflog | grep "payment step 5" | head -1 | awk '{print $1}')
echo "Topildi: $SHA"

# Branchni qaytarish
git branch feature/payment $SHA

# Tekshirish
git switch feature/payment
git log --oneline
# ✅ 5 ta commit qaytdi

# ─────────────────────────────────────────────────────────────────────
# SENARIY 2: reset --hard bilan ish yo'qotish
# ─────────────────────────────────────────────────────────────────────

git switch main

for i in 1 2 3; do
    echo "ish $i" >> ish.py
    git add . && git commit -m "feat: ish $i"
done

git log --oneline | head -5

# ❌ KATASTROFA — 3 commit yo'qotish
git reset --hard HEAD~3

ls ish.py
# ❌ ish.py YO'Q!

# 🚨 QUTQARISH
git reflog
# HEAD@{0}: reset: moving to HEAD~3
# HEAD@{1}: commit: feat: ish 3   ← bu eski holat

# Eski holatga
git reset --hard HEAD@{1}

ls ish.py
# ✅ ish.py qaytdi
git log --oneline | head -5
# 3 ta commit ham qaytdi

# ─────────────────────────────────────────────────────────────────────
# SENARIY 3: Push qilingan yomon commit (revert)
# ─────────────────────────────────────────────────────────────────────

# Push'siz simulyatsiya — yomon commit qilingan
echo "DELETE EVERYTHING" > bad.py
git add . && git commit -m "BUG: delete everything"

git log --oneline | head -3

# ❌ Yomon commit allaqachon push qilingan (faraz)
# Reset xavfli — chunki push qilingan
# Yechim — REVERT

git revert HEAD --no-edit
# Yangi commit yaratiladi:
# Revert "BUG: delete everything"

ls bad.py
# ❌ bad.py YO'Q (revert bekor qildi)

git log --oneline | head -3
# revert_sha Revert "BUG..."
# bad_sha BUG: delete everything
# ✅ Tarix saqlanadi, lekin bad effect bekor

# ─────────────────────────────────────────────────────────────────────
# SENARIY 4: Wrong branch'da commit
# ─────────────────────────────────────────────────────────────────────

git switch main

# Tasodifan main'da 3 commit
echo "profile UI 1" > profile1.py && git add . && git commit -m "feat: profile 1"
echo "profile UI 2" > profile2.py && git add . && git commit -m "feat: profile 2"
echo "profile UI 3" > profile3.py && git add . && git commit -m "feat: profile 3"

# Voy — bu feature/profile branchda bo'lishi kerak edi
# 🚨 QUTQARISH (push qilmagan deb faraz):

# 1) Joriy holat'dan branch yaratish
git branch feature/profile

# 2) main'ni 3 commit oldinga qaytarish
git reset --hard HEAD~3

# 3) Yangi branchga o'tish
git switch feature/profile

git log --oneline | head -5
# ✅ 3 ta commit shu yerda
# main toza

# ─────────────────────────────────────────────────────────────────────
# SENARIY 5: Detached HEAD'da ish
# ─────────────────────────────────────────────────────────────────────

git switch main

# 3 commit orqaga
git checkout HEAD~3
# Note: switching to 'abc1234'.
# You are in 'detached HEAD' state.

# Eksperiment
echo "ekspriment 1" > exp.py
git add . && git commit -m "exp: 1"

echo "ekspriment 2" >> exp.py
git add . && git commit -m "exp: 2"

# Voy — branch'ga qaytmoqchi
git switch main
# ❌ exp commit'lar ko'rinmaydi (branch'siz qoldi)

ls exp.py
# ❌ YO'Q

# 🚨 QUTQARISH
git reflog | grep "exp"
# abc HEAD@{N}: commit: exp: 2

SHA=$(git reflog | grep "exp: 2" | head -1 | awk '{print $1}')

# Branch yaratish o'sha SHA dan
git branch experiment $SHA

git switch experiment
ls exp.py
# ✅ exp.py qaytdi
git log --oneline | head -3

# ─────────────────────────────────────────────────────────────────────
# BONUS SENARIY 6: Rebase --abort
# ─────────────────────────────────────────────────────────────────────

git switch main
echo "shared" > shared.txt && git add . && git commit -m "main: shared"

git switch -c feature/conflict
echo "feature shared" > shared.txt && git add . && git commit -m "feat: shared"

git switch main
echo "yana main" > shared.txt && git add . && git commit -m "main: yana"

git switch feature/conflict

# Rebase
git rebase main
# CONFLICT...

# Yarim yechdim, lekin xato qildim
echo "wrong" > shared.txt
git add shared.txt

# 🚨 QUTQARISH — bekor qilish
git rebase --abort
# Eski holatga qaytadi

git status
# clean — hech narsa o'zgarmagan

# ─────────────────────────────────────────────────────────────────────
# Yakuniy hisobot
# ─────────────────────────────────────────────────────────────────────

cat > hisobot.md <<'EOF'
# Recovery laboratoriyasi — hisobot

## Senariy 1: Branch o'chirish
- ❌ git branch -D feature/payment
- 🚨 git reflog + git branch feature/payment <SHA>
- ✅ Tiklandi

## Senariy 2: reset --hard
- ❌ git reset --hard HEAD~3
- 🚨 git reflog + git reset --hard HEAD@{1}
- ✅ Tiklandi

## Senariy 3: Push qilingan yomon commit
- ❌ Bad commit + push
- 🚨 git revert HEAD (reset emas, chunki push qilingan)
- ✅ Yangi commit bilan bekor

## Senariy 4: Wrong branch
- ❌ main'da feature commit'lar
- 🚨 git branch <yangi> + git reset --hard HEAD~N main'da
- ✅ Tiklandi

## Senariy 5: Detached HEAD
- ❌ checkout SHA + commit'lar
- 🚨 git reflog + git branch <yangi> <SHA>
- ✅ Tiklandi

## Senariy 6: Rebase abort
- ❌ Yarim conflict yechish — adashish
- 🚨 git rebase --abort
- ✅ Eski holatga
EOF

git add hisobot.md
git commit -m "docs: recovery lab hisoboti"
"""
L10_TEXT = """\
<h2>Tag, release va GitHub Actions (CI/CD)</h2>

<pre class="mermaid">
flowchart LR
    PUSH["git push"] --> GH["GitHub"]
    GH --> ACT["GitHub Actions"]
    ACT --> T["Test"]
    ACT --> B["Build"]
    ACT --> D["Deploy"]
    GH --> TAG["v1.0.0 tag"]
    TAG --> REL["GitHub Release"]
</pre>

<p>Professional darajaga o'tish vaqti. Bu darsda:</p>
<ul>
<li><strong>Tag</strong> — version belgisi (<code>v1.0.0</code>)</li>
<li><strong>Release</strong> — GitHub'da rasmiy versiya e'loni</li>
<li><strong>GitHub Actions</strong> — har push'da avtomatik test/build/deploy</li>
<li><strong>SemVer</strong> — version qoidalari (1.2.3 — major.minor.patch)</li>
</ul>

<p>Bularsiz ham yashash mumkin, lekin bular bilan — sizning loyihangiz <em>professional ko'rinadi</em> va xatolar oldindan to'xtatiladi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Tag yaratish</h4>

<pre><code># Hozirgi commit'ga tag
git tag v1.0.0

# Annotated tag (yaxshiroq — xabar va metadata bilan)
git tag -a v1.0.0 -m "Birinchi rasmiy versiya"

# Belgilangan commit'ga
git tag -a v0.9.0 abc1234 -m "Beta versiyasi"

# Ro'yxat
git tag
# v0.9.0
# v1.0.0

# Tag'larni remote'ga push
git push origin v1.0.0
# yoki hammasi:
git push --tags

# Tag o'chirish
git tag -d v1.0.0           # lokal
git push origin --delete v1.0.0   # remote</code></pre>

<h4>BLOKA 2 — GitHub Release</h4>

<p>Tag yaratganingizdan keyin GitHub'da: <strong>Releases → Draft a new release</strong>.</p>

<ul>
<li>📌 Choose tag: <code>v1.0.0</code></li>
<li>📝 Release title: "v1.0.0 — Birinchi versiya"</li>
<li>📋 Description: changelog</li>
<li>📦 Binaries upload (agar bo'lsa)</li>
<li>✅ <strong>Publish release</strong></li>
</ul>

<p>Yoki gh CLI bilan:</p>
<pre><code>gh release create v1.0.0 \\
    --title "v1.0.0 — Birinchi versiya" \\
    --notes "Birinchi rasmiy versiya. ..."</code></pre>

<h4>BLOKA 3 — GitHub Actions birinchi workflow</h4>

<p>Repo ildizida: <code>.github/workflows/test.yml</code></p>

<pre><code>name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest</code></pre>

<p>Push qiling. GitHub'da: <strong>Actions</strong> tab → workflow ishga tushadi. Yashil ✅ — testlar o'tdi. Qizil ❌ — failed (loglarni ko'ring).</p>

<h3>🐛 Ataylab xato</h3>
<pre><code># Yamlda indentatsiya — 4 bo'shliq
jobs:
    test:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4</code></pre>

<p><strong>Sabab:</strong> YAML <strong>2 bo'shliq</strong> indentatsiya ishlatadi. 4 bo'shliq — sintaktik xato. Plus: tab'lar emas, faqat bo'shliq. Bu — YAML'ning eng katta tuzog'i.</p>

<p>To'g'risi:</p>
<pre><code>jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Semantic Versioning (SemVer)</h4>

<p>Format: <code>MAJOR.MINOR.PATCH</code> (masalan, <code>2.5.13</code>)</p>

<table>
<tr><th>Qism</th><th>Qachon oshirish</th></tr>
<tr><td><strong>MAJOR</strong> (2.x.x)</td><td>Breaking change — eski kod sinadi</td></tr>
<tr><td><strong>MINOR</strong> (x.5.x)</td><td>Yangi feature (backward compatible)</td></tr>
<tr><td><strong>PATCH</strong> (x.x.13)</td><td>Bug fix</td></tr>
</table>

<p>Pre-release: <code>1.0.0-alpha</code>, <code>1.0.0-beta.2</code>, <code>1.0.0-rc.1</code>.</p>

<h4>2. Lightweight vs Annotated tag</h4>

<pre><code># Lightweight (pointer faqat)
git tag v1.0.0

# Annotated (recommended — full metadata)
git tag -a v1.0.0 -m "Version 1.0.0 — initial release"
# - tag SHA o'zi bor (commit'dan boshqa)
# - tagger ism, email, sana
# - xabar
# - GPG sign mumkin</code></pre>

<p>Release'lar uchun — annotated tavsiya.</p>

<h4>3. GitHub Actions — asoslar</h4>

<table>
<tr><th>Qism</th><th>Vazifa</th></tr>
<tr><td><code>name</code></td><td>Workflow nomi (Actions tabda ko'rinadi)</td></tr>
<tr><td><code>on</code></td><td>Qachon ishga tushsin (push, PR, schedule, ...)</td></tr>
<tr><td><code>jobs</code></td><td>Bajariladigan vazifalar</td></tr>
<tr><td><code>runs-on</code></td><td>OS (ubuntu, macos, windows)</td></tr>
<tr><td><code>steps</code></td><td>Har bir qadam</td></tr>
<tr><td><code>uses</code></td><td>Tayyor action ishlatish</td></tr>
<tr><td><code>run</code></td><td>Shell buyrug'i</td></tr>
</table>

<h4>4. Triggerlar — qachon ishga tushadi</h4>

<pre><code>on:
  push:
    branches: [main, develop]
    tags: ['v*']

  pull_request:
    branches: [main]

  schedule:
    - cron: '0 0 * * *'   # har kun yarim tunda

  workflow_dispatch:       # qo'l bilan

  release:
    types: [created]</code></pre>

<h4>5. Tipik workflow misollari</h4>

<p><strong>Python test:</strong></p>
<pre><code>name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -r requirements.txt
      - run: pytest --cov</code></pre>

<p><strong>Node.js build + deploy:</strong></p>
<pre><code>name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - run: npm test
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}</code></pre>

<h4>6. Secrets — sirli ma'lumotlar</h4>

<p>API kalit, deploy token — kodda yozmang. GitHub: <strong>Settings → Secrets and variables → Actions → New secret</strong>.</p>

<pre><code>steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: ./deploy.sh</code></pre>

<h4>7. Badge — README'da yashil belgi</h4>

<pre><code>![Tests](https://github.com/olim/repo/workflows/Tests/badge.svg)</code></pre>

<p>README'da yashil "passing" — sizning loyihangiz testlar bilan himoyalangan ko'rsatadi.</p>

<h4>8. Marketplace — tayyor action'lar</h4>

<p><a href="https://github.com/marketplace?type=actions">github.com/marketplace</a> — 20,000+ tayyor action'lar:</p>

<ul>
<li><code>actions/checkout</code> — repo'ni clone</li>
<li><code>actions/setup-python</code></li>
<li><code>actions/setup-node</code></li>
<li><code>docker/build-push-action</code></li>
<li><code>peter-evans/create-pull-request</code></li>
<li><code>codecov/codecov-action</code></li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Tag (lightweight va annotated) yaratish</li>
<li>✅ SemVer — major.minor.patch qoidalari</li>
<li>✅ GitHub Release — rasmiy versiya e'loni</li>
<li>✅ GitHub Actions — YAML workflow</li>
<li>✅ Triggerlar: push, pull_request, schedule, dispatch</li>
<li>✅ Matrix builds (bir nechta versiya parallel)</li>
<li>✅ Secrets — sirli ma'lumotlarni saqlash</li>
<li>✅ Status badge README'da</li>
</ul>
"""

L10_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 10: Tag, release, GitHub Actions
# ════════════════════════════════════════════════════════════════════
# Bu fayl 2 qism: bash buyruqlar + YAML workflow misollari

# ─────────────────────────────────────────────────────────────────────
# QISM A: BASH — tag va release
# ─────────────────────────────────────────────────────────────────────

cd mening-loyiham

# Tag — lightweight
git tag v0.1.0

# Annotated tag (tavsiya)
git tag -a v1.0.0 -m "Birinchi rasmiy versiya"

# Belgilangan commit'ga
git tag -a v0.9.0 abc1234 -m "Beta versiyasi"

# Ro'yxat
git tag
git tag -l "v1.*"     # patternga mos

# Tag'ni ko'rish
git show v1.0.0

# Tag'ni remote'ga push
git push origin v1.0.0
git push origin --tags     # hammasi

# Lokal tag o'chirish
git tag -d v0.1.0

# Remote tag o'chirish
git push origin --delete v0.1.0

# ─────────────────────────────────────────────────────────────────────
# Release yaratish — gh CLI bilan
# ─────────────────────────────────────────────────────────────────────

gh release create v1.0.0 \\
    --title "v1.0.0 — Birinchi versiya" \\
    --notes "$(cat <<'EOF'
## 🚀 Yangi xususiyatlar
- Login va register
- Profile sahifa
- Dark mode

## 🐛 Bug fixes
- Email validatsiyasi to'g'rilandi

## 📦 Dependencies
- React 19
- Vite 7
EOF
)"

# Fayl yuklash
gh release upload v1.0.0 dist/app.zip

# Release ro'yxati
gh release list

# Bitta'ni ko'rish
gh release view v1.0.0

# ─────────────────────────────────────────────────────────────────────
# QISM B: YAML workflow misollari
# ─────────────────────────────────────────────────────────────────────

# Repo ildizida:
# mkdir -p .github/workflows
# .github/workflows/test.yml fayl yarating

# ════════════════════════════════════════════════════════════════════
# Misol 1: Python test
# ════════════════════════════════════════════════════════════════════

cat > .github/workflows/test-python.yml << 'YAML'
name: Python Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint with ruff
        run: |
          pip install ruff
          ruff check .

      - name: Test with pytest
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
YAML

# ════════════════════════════════════════════════════════════════════
# Misol 2: Node.js build va deploy
# ════════════════════════════════════════════════════════════════════

cat > .github/workflows/deploy-node.yml << 'YAML'
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test

      - name: Build
        run: npm run build

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
YAML

# ════════════════════════════════════════════════════════════════════
# Misol 3: Release tag'ga binary build
# ════════════════════════════════════════════════════════════════════

cat > .github/workflows/release.yml << 'YAML'
name: Release Binary

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Build
        run: go build -o myapp${{ matrix.os == 'windows-latest' && '.exe' || '' }}

      - name: Upload to release
        uses: softprops/action-gh-release@v2
        with:
          files: myapp*
YAML

# ════════════════════════════════════════════════════════════════════
# Misol 4: Scheduled (har kun)
# ════════════════════════════════════════════════════════════════════

cat > .github/workflows/daily-report.yml << 'YAML'
name: Daily Report

on:
  schedule:
    - cron: '0 8 * * *'   # har kun ertalab 8:00 UTC
  workflow_dispatch:       # qo'l bilan ham ishlatish

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate stats
        run: |
          echo "## Daily report" > report.md
          git log --oneline --since="yesterday" >> report.md

      - name: Send to Slack
        env:
          WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        run: |
          curl -X POST "$WEBHOOK" \\
            -H "Content-Type: application/json" \\
            -d "{\\"text\\": \\"Daily report:\\n$(cat report.md)\\"}"
YAML

# ─────────────────────────────────────────────────────────────────────
# Hammasini commit va push
# ─────────────────────────────────────────────────────────────────────

git add .github/
git commit -m "ci: GitHub Actions workflows qo'shildi"
git push

# GitHub'da Actions tab — workflow'lar ishga tushadi
# Yashil ✅ — passing
# Qizil ❌ — log'larni ko'ring

# ─────────────────────────────────────────────────────────────────────
# README ga badge qo'shish
# ─────────────────────────────────────────────────────────────────────

cat >> README.md << 'EOF'

## Status

![Tests](https://github.com/olim/mening-loyiham/workflows/Python%20Tests/badge.svg)
![Deploy](https://github.com/olim/mening-loyiham/workflows/Build%20and%20Deploy/badge.svg)
EOF
"""
L11_TEXT = """\
<h2>🚀 CAPSTONE: Jamoaviy loyiha workflow</h2>

<pre class="mermaid">
flowchart TB
    I["Issue: yangi feature"] --> A["Asign: jamoadosh"]
    A --> B["Branch: feature/X"]
    B --> COM["Commit'lar"]
    COM --> P["Push"]
    P --> PR["PR + reviewer"]
    PR --> REV["Review + diskussiya"]
    REV --> CI["CI tests"]
    CI --> M["Merge to main"]
    M --> DEP["Deploy"]
    DEP --> REL["Tag + Release"]
</pre>

<p>Kursning yakuniy loyihasi — <strong>haqiqiy jamoaviy ish</strong>. Siz 2-4 odamlik jamoa bilan kichik loyiha qurasiz. Hamma narsa: <strong>issues, branches, PRs, review, conflict yechish, CI/CD, release</strong>.</p>

<p>Bu — ish o'rnida har kuni qiladigan ish. Bu loyihani tugatgan siz <em>"komandada Git bilan ishlay olaman"</em> deyish huquqiga ega bo'lasiz — bu CV uchun katta.</p>

<h3>Loyiha tanlovi</h3>

<p>Mavzu — istalgan kichik real foydali narsa. Misollar:</p>

<table>
<tr><th>Loyiha</th><th>Texnologiya</th></tr>
<tr><td>Quiz app</td><td>HTML + JS yoki React</td></tr>
<tr><td>Recipe collection</td><td>Frontend + backend</td></tr>
<tr><td>Task tracker (Trello clone)</td><td>React + Flask</td></tr>
<tr><td>Markdown editor</td><td>HTML + JS</td></tr>
<tr><td>Weather dashboard</td><td>React + API</td></tr>
<tr><td>Movie database</td><td>React + TMDB API</td></tr>
<tr><td>O'zbek-rus tarjimon</td><td>HTML + JS + LLM API</td></tr>
</table>

<p>Asosiy — <strong>kichik loyiha</strong> (1-2 hafta), lekin <strong>professional workflow</strong>.</p>

<h3>Texnik talablar</h3>

<h4>1. Repo va README</h4>
<ul>
<li>✅ GitHub'da public repo</li>
<li>✅ Chiroyli README.md (description, tezda boshlash, texnologiyalar, screenshot)</li>
<li>✅ .gitignore (loyiha turi uchun moslangan)</li>
<li>✅ LICENSE (MIT yoki Apache 2.0)</li>
<li>✅ CONTRIBUTING.md (yangi contributor'lar uchun)</li>
</ul>

<h4>2. Issues va Project board</h4>
<ul>
<li>✅ Kamida 10 ta issue yaratilgan</li>
<li>✅ Label'lar: <code>feature</code>, <code>bug</code>, <code>documentation</code>, <code>good first issue</code></li>
<li>✅ Milestone (masalan, "v1.0.0")</li>
<li>✅ Project board (Kanban): Todo / In Progress / Done</li>
<li>✅ Issue'lar jamoadoshlarga assign qilingan</li>
</ul>

<h4>3. Branch strategy</h4>
<ul>
<li>✅ <code>main</code> — production, doim ishlovchi</li>
<li>✅ <code>develop</code> — keyingi release uchun (ixtiyoriy)</li>
<li>✅ <code>feature/&lt;nom&gt;</code> — har issue uchun</li>
<li>✅ <code>fix/&lt;nom&gt;</code> — bug fix'lar</li>
<li>✅ Branch protection rules (Settings → Branches): main'ga PR'siz push yo'q</li>
</ul>

<h4>4. Commit va PR qoidalari</h4>
<ul>
<li>✅ Conventional Commits (<code>feat:</code>, <code>fix:</code>, <code>docs:</code>)</li>
<li>✅ Har PR — bitta issue'ga bog'langan (<code>Closes #N</code>)</li>
<li>✅ PR description — nima, nima uchun, qanday test qildim</li>
<li>✅ Kamida 1 ta reviewer approve qilgan</li>
<li>✅ CI yashil (testlar o'tgan)</li>
</ul>

<h4>5. CI/CD (GitHub Actions)</h4>
<ul>
<li>✅ Har push/PR'da test workflow</li>
<li>✅ Lint check</li>
<li>✅ Build check</li>
<li>✅ (Bonus) Auto-deploy main'ga merge keyin</li>
<li>✅ Status badge README'da</li>
</ul>

<h4>6. Release</h4>
<ul>
<li>✅ Tag (SemVer): <code>v0.1.0</code>, <code>v1.0.0</code></li>
<li>✅ GitHub Release sahifa — changelog bilan</li>
<li>✅ Deploy live URL (Vercel/Netlify/Railway)</li>
</ul>

<h4>7. Jamoaviy ish</h4>
<ul>
<li>✅ 2-4 jamoadosh</li>
<li>✅ Har biridan kamida 5 ta commit</li>
<li>✅ Kamida 1 ta merge conflict (yechilgan)</li>
<li>✅ Kamida 1 ta code review siklasi (siz boshqalarning kodini review qildingiz)</li>
<li>✅ Issue diskussiya (kamida 3 ta comment exchange)</li>
</ul>

<h3>Bosqichlar (2 hafta)</h3>

<h4>Hafta 1 — Sozlash va boshlash</h4>
<ol>
<li><strong>Kun 1</strong>: Jamoa to'plang, mavzu kelishuv</li>
<li><strong>Kun 2</strong>: GitHub org/repo yaratish, README, LICENSE</li>
<li><strong>Kun 3</strong>: Issue'lar yarating va assign</li>
<li><strong>Kun 4</strong>: GitHub Actions workflow</li>
<li><strong>Kun 5-7</strong>: Har feature uchun PR (kichik)</li>
</ol>

<h4>Hafta 2 — Tugatish va release</h4>
<ol>
<li><strong>Kun 1-3</strong>: Qolgan feature'lar + review</li>
<li><strong>Kun 4</strong>: Bug fix'lar (issue'lar yaratib)</li>
<li><strong>Kun 5</strong>: Deploy + dokumentatsiya</li>
<li><strong>Kun 6</strong>: <code>v1.0.0</code> tag + Release</li>
<li><strong>Kun 7</strong>: Retrospective — nima yaxshi, nima yaxshilanishi mumkin</li>
</ol>

<h3>Yakuniy yetkazib berish</h3>

<ul>
<li>📦 <strong>GitHub repo URL</strong></li>
<li>🌐 <strong>Live demo URL</strong></li>
<li>📋 <strong>README</strong> — to'liq</li>
<li>🏆 <strong>Release v1.0.0</strong> — changelog bilan</li>
<li>📊 <strong>Insights → Contributors</strong> — har jamoadosh contribution</li>
<li>🎥 <strong>5 daqiqalik demo video</strong> (ixtiyoriy)</li>
</ul>

<h3>Baholash mezonlari</h3>

<table>
<tr><th>Mezon</th><th>Ball</th></tr>
<tr><td>Repo struktura va README</td><td>10</td></tr>
<tr><td>Issues va project management</td><td>15</td></tr>
<tr><td>Conventional commits</td><td>10</td></tr>
<tr><td>PR'lar va review jarayoni</td><td>20</td></tr>
<tr><td>Conflict yechish</td><td>10</td></tr>
<tr><td>GitHub Actions (CI passing)</td><td>15</td></tr>
<tr><td>Release va deploy</td><td>10</td></tr>
<tr><td>Jamoa hissasi (balanslangan)</td><td>10</td></tr>
</table>

<h3>Bonus (ixtiyoriy)</h3>

<ul>
<li>🎨 GitHub Pages bilan landing page</li>
<li>📊 README'da chiroyli badge'lar (shields.io)</li>
<li>🐛 Dependabot — avtomatik dep update PR'lar</li>
<li>📝 GitHub Discussions yoqilgan</li>
<li>🎭 PR template (.github/pull_request_template.md)</li>
<li>📋 Issue template (.github/ISSUE_TEMPLATE/)</li>
<li>🤖 GitHub Actions: bot tomonidan auto-label PR'lar</li>
<li>🌟 5+ star (do'stlardan)</li>
</ul>

<h3>🎯 Yakuniy g'olib bayonoti</h3>

<p>Bu kursni va capstone'ni tugatgan siz <strong>tayyor</strong>:</p>
<ul>
<li>✅ Real ishda jamoa Git workflow'ini boshqarish</li>
<li>✅ Open source loyihalarga hissa qo'shish</li>
<li>✅ O'zingizning loyihalaringizni professional darajada saqlash</li>
<li>✅ CV uchun haqiqiy loyiha (live URL + GitHub)</li>
<li>✅ Interview uchun Git mavzulari (rebase, conflict, recovery)</li>
<li>✅ CI/CD asoslari (har boshlovchi dasturchi'dan boshqacha)</li>
</ul>

<p>Git va GitHub — siz endi har boshqa kursdan oson o'tasiz (har birida CSV uchun kerak), va eng muhimi — <strong>haqiqiy ish bilan tanish</strong>.</p>

<p>Keyingi qadamlar:</p>
<ul>
<li>📦 <strong>Docker</strong> — containerization</li>
<li>☁️ <strong>AWS/GCP</strong> — deploy va cloud</li>
<li>🧪 <strong>Pytest/Jest</strong> — testlar (avtomatik CI uchun zarur)</li>
<li>🎯 <strong>Real loyiha</strong> — bo'sh vaqtingizda o'zingiz uchun</li>
</ul>

<p>Tabriklayman! Siz endi <strong>dasturchi</strong>siz. Omad!</p>
"""

L11_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 🚀 CAPSTONE: Jamoaviy loyiha workflow — qadamlar
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 1: Repo sozlash
# ─────────────────────────────────────────────────────────────────────

# GitHub'da yangi org (yoki shaxsiy account) ostida public repo
# Misol: github.com/our-team/quiz-app

# Lokal'da
git clone git@github.com:our-team/quiz-app.git
cd quiz-app

# README
cat > README.md <<'EOF'
# Quiz App 🎯

Real-time quiz application with multiplayer support.

![Tests](https://github.com/our-team/quiz-app/workflows/Tests/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Tezda boshlash

\`\`\`bash
git clone https://github.com/our-team/quiz-app.git
cd quiz-app
npm install
npm run dev
\`\`\`

## 📦 Texnologiyalar

- **Frontend:** React 19, Vite, TailwindCSS
- **Backend:** Flask, SQLAlchemy, PostgreSQL
- **Tests:** Vitest, Pytest
- **CI/CD:** GitHub Actions
- **Deploy:** Vercel (FE) + Railway (BE)

## 🌐 Live demo

https://quiz-app.vercel.app

## 📋 Xususiyatlar

- [x] Foydalanuvchi register/login
- [x] Quiz yaratish
- [x] Multiplayer rejim
- [ ] Leaderboard (in progress)

## 🤝 Hissa qo'shish

[CONTRIBUTING.md](./CONTRIBUTING.md) ni o'qing.

## 📄 Litsenziya

MIT
EOF

# .gitignore
cat > .gitignore <<'EOF'
node_modules/
dist/
.env
__pycache__/
venv/
.DS_Store
*.log
EOF

# LICENSE
curl -o LICENSE https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt
sed -i.bak "s/\\[year\\]/2026/g; s/\\[fullname\\]/Our Team/g" LICENSE
rm LICENSE.bak

# CONTRIBUTING
cat > CONTRIBUTING.md <<'EOF'
# Contributing

## Workflow

1. Fork or branch from main
2. Create feature branch: `git switch -c feature/your-feature`
3. Commit using Conventional Commits: `feat:`, `fix:`, `docs:`
4. Push and open PR
5. Link PR to issue: `Closes #N`
6. Wait for review (at least 1 approval)

## Branch naming

- `feature/login`
- `fix/login-bug`
- `refactor/api-client`
- `docs/readme-update`

## Commit format

\`\`\`
<type>: <description>

[optional body]
\`\`\`

## Code style

- TypeScript strict mode
- Prettier + ESLint
- Tests for new features
EOF

git add .
git commit -m "chore: initial project setup"
git push origin main

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 2: Branch protection (GitHub UI)
# ─────────────────────────────────────────────────────────────────────

# Settings → Branches → Add rule
# Branch name pattern: main
# - [x] Require pull request before merging
# - [x] Require approvals: 1
# - [x] Require status checks (after first CI run)
# - [x] Require branches to be up to date
# - [x] Include administrators

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 3: Issues
# ─────────────────────────────────────────────────────────────────────

# gh CLI bilan 10 ta issue
gh issue create --title "feat: User registration" \\
    --body "Email + password registration with validation" \\
    --label "feature,frontend,backend"

gh issue create --title "feat: User login" \\
    --body "JWT-based authentication" \\
    --label "feature,backend"

gh issue create --title "feat: Quiz creation form" \\
    --body "Form to create quiz with multiple questions" \\
    --label "feature,frontend"

gh issue create --title "feat: Real-time multiplayer" \\
    --body "WebSocket-based multiplayer rooms" \\
    --label "feature,backend"

gh issue create --title "feat: Leaderboard" \\
    --body "Top players ranking" \\
    --label "feature,frontend"

gh issue create --title "fix: Login form validation" \\
    --body "Email validation not working on Firefox" \\
    --label "bug,frontend"

gh issue create --title "docs: API documentation" \\
    --body "OpenAPI spec for backend" \\
    --label "documentation"

gh issue create --title "chore: Setup ESLint" \\
    --body "Add ESLint + Prettier config" \\
    --label "good first issue,tooling"

gh issue create --title "test: Unit tests for auth" \\
    --body "Cover login/register edge cases" \\
    --label "tests,backend"

gh issue create --title "feat: Dark mode" \\
    --body "Toggle for dark/light theme" \\
    --label "good first issue,frontend"

# Assign issues
# gh issue edit 1 --add-assignee olim
# gh issue edit 2 --add-assignee vali

# Milestone
gh api repos/our-team/quiz-app/milestones -f title="v1.0.0" -f description="MVP"

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 4: GitHub Actions workflow
# ─────────────────────────────────────────────────────────────────────

mkdir -p .github/workflows

cat > .github/workflows/ci.yml <<'YAML'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build

  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest --cov
YAML

git add .github/
git commit -m "ci: setup CI workflows for FE and BE"
git push

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 5: PR template
# ─────────────────────────────────────────────────────────────────────

mkdir -p .github

cat > .github/pull_request_template.md <<'EOF'
## Nima o'zgardi

-

## Nima uchun

Closes #

## Test

- [ ] Manual test
- [ ] Unit tests
- [ ] Lint passing

## Screenshot (UI bo'lsa)

EOF

git add .github/pull_request_template.md
git commit -m "chore: PR template"
git push

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 6: Birinchi feature PR
# ─────────────────────────────────────────────────────────────────────

# Issue #1 — User registration
gh issue view 1
gh issue edit 1 --add-assignee "@me"

git switch -c feature/user-registration

mkdir -p backend/app
cat > backend/app/auth.py <<'EOF'
from flask import Blueprint, request, jsonify
# ... auth code ...

bp = Blueprint('auth', __name__)

@bp.post('/register')
def register():
    # TODO
    return jsonify({'ok': True})
EOF

git add backend/
git commit -m "feat(auth): scaffold registration endpoint"

# Davom
cat > backend/tests/test_auth.py <<'EOF'
def test_register():
    # TODO
    pass
EOF

git add backend/tests/
git commit -m "test(auth): registration test scaffold"

# Push
git push -u origin feature/user-registration

# PR
gh pr create \\
    --title "feat: User registration endpoint" \\
    --body "$(cat <<'PR'
## Nima o'zgardi
- /auth/register POST endpoint
- Test scaffold

## Nima uchun
Closes #1

## Test
- [x] Lint passing
- [ ] Full tests (TODO in next PR)
PR
)" \\
    --assignee "@me" \\
    --label "feature,backend"

# Review kelishini kuting...
# Review bo'lgach (approve), squash and merge

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 7: Reviewer sifatida boshqa PR
# ─────────────────────────────────────────────────────────────────────

# Sherigingiz PR yubordi (#15)
gh pr list

# Checkout
gh pr checkout 15

# Tekshirish — manual test, kod o'qish
# ... ish ...

# Comment
gh pr comment 15 --body "Looks great! One suggestion: extract validation to utils."

# Yoki approve
gh pr review 15 --approve

# Yoki request changes
# gh pr review 15 --request-changes --body "Please add tests"

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 8: Conflict yechish (real)
# ─────────────────────────────────────────────────────────────────────

git switch feature/user-registration
git fetch origin
git rebase origin/main
# CONFLICT in backend/app/__init__.py

# Yeching, marker'larni o'chiring
# vim backend/app/__init__.py

git add backend/app/__init__.py
git rebase --continue
git push --force-with-lease

# ─────────────────────────────────────────────────────────────────────
# BOSQICH 9: Release v1.0.0
# ─────────────────────────────────────────────────────────────────────

# Hammasi tugadi, main toza
git switch main
git pull

# Tag
git tag -a v1.0.0 -m "v1.0.0 — MVP release"
git push origin v1.0.0

# Release
gh release create v1.0.0 \\
    --title "v1.0.0 — MVP" \\
    --notes "$(cat <<'EOF'
## 🚀 Yangi xususiyatlar

- Foydalanuvchi register/login (JWT)
- Quiz yaratish formasi
- Quiz o'ynash (single player)
- Dark mode

## 🐛 Bug fixes

- Login form Firefox'da to'g'rilandi

## 📦 Dependencies

- React 19
- Flask 3.0
- PostgreSQL 16

## 🙏 Contributors

- @olim
- @vali
- @karim

## 🔗 Links

- [Live demo](https://quiz-app.vercel.app)
- [API docs](https://quiz-app-api.railway.app/docs)
EOF
)"

# ─────────────────────────────────────────────────────────────────────
# 🎉 BAJARILDI
# ─────────────────────────────────────────────────────────────────────

# GitHub Insights → Contributors — har jamoadosh hissasi
# Release sahifa — v1.0.0 download link
# Live demo — hammasi ishlayapti
# README'da yashil CI badge

# CV uchun:
# "Quiz App — fullstack jamoaviy loyiha (4 odam)"
# "GitHub: github.com/our-team/quiz-app"
# "Live: quiz-app.vercel.app"

# 🏆 Siz endi haqiqiy dasturchisiz!
"""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise builders
# ─────────────────────────────────────────────────────────────────────────────
def mc(title, options, correct, *, multi=False, hint="", explanation="", diff="Easy", pts=2):
    return {"title": title, "description": title, "exercise_type": "multiple_choice",
            "options": options, "correct_answers": correct, "is_multiple_select": multi,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def dd(title, items_in_order, *, hint="", explanation="", diff="Medium", pts=3):
    return {"title": title, "description": title, "exercise_type": "drag_and_drop",
            "drag_items": list(items_in_order), "correct_order": list(items_in_order),
            "is_multiple_select": False, "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


def ti(title, expected, *, hint="", explanation="", diff="Hard", pts=4):
    return {"title": title, "description": title, "exercise_type": "text_input",
            "expected_answer": expected, "is_multiple_select": False,
            "hint": hint, "explanation": explanation,
            "difficulty_level": diff, "points": pts}


L1_EX: list = [
    mc("Git nima?",
       ["Programming tili",
        "Versiyalarni boshqarish tizimi — kod tarixini saqlaydi",
        "Database",
        "Operatsion tizim"],
       "B", diff="Easy", pts=2),
    mc("Yangi papkani Git repo'ga aylantirish uchun qaysi buyruq?",
       ["git start",
        "git init",
        "git create",
        "git new"],
       "B", diff="Easy", pts=2),
    mc("Git'ning 3 ta hududi qaysi?",
       ["Working / Staging / Repository",
        "Local / Remote / Cloud",
        "Edit / Save / Send",
        "Yangi / Eski / Tarix"],
       "A", explanation="Working = sizning fayllar. Staging = `git add` keyin. Repository = `git commit` keyin (.git ichida).",
       diff="Medium", pts=3),
    mc("`git commit -m \"xabar\"` ishlatishdan oldin nima qilish kerak?",
       ["Hech narsa",
        "`git add` bilan o'zgarishlarni staging'ga qo'shish",
        "`git init` qaytadan",
        "`git push`"],
       "B", explanation="Avval add (staging), keyin commit (repository).",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari YAXSHI commit xabari?",
       ["fix",
        "feat: login formada email validatsiyasi qo'shildi",
        "asdf",
        "docs: README ga setup qadamlari yozildi",
        "update"],
       "B,D", multi=True,
       hint="Aniq, conventional commits formati.",
       diff="Medium", pts=3),
    dd("Birinchi commit qilish bosqichlari",
       ["mkdir mening-loyiham && cd mening-loyiham",
        "git init",
        "echo '# README' > README.md",
        "git add README.md",
        "git commit -m 'docs: birinchi commit'",
        "git log"],
       diff="Medium", pts=3),
    ti("`git config --global user.email \"x@y.uz\"` — `--global` flag nima qiladi?",
       "--global belgilashi bu sozlama BU KOMPYUTERDAGI HAR REPO uchun amal qiladi (~/.gitconfig faylida saqlanadi). "
       "Agar --global bo'lmasa — faqat joriy repo uchun (.git/config). "
       "--global afzal: har yangi repo'da qayta sozlash kerak emas. "
       "Lekin maxsus loyiha uchun boshqa email kerak bo'lsa — local config bilan override qilish mumkin.",
       hint="Global vs local config.",
       diff="Hard", pts=4),
]
L2_EX: list = [
    mc(".gitignore nima qiladi?",
       ["Faylni o'chiradi",
        "Git'ga ko'rsatilgan fayl/papkalarni e'tibordan tashqari qoldirishni aytadi",
        "Faqat backup",
        "Loyihani tezlashtiradi"],
       "B", diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari .gitignore'ga TIPIK kiritiladi?",
       [".env",
        "node_modules/",
        "main.py",
        "__pycache__/",
        "README.md",
        ".DS_Store"],
       "A,B,D,F", multi=True,
       hint="Secret, build artifact, OS fayllar — ha. Source kod — yo'q.",
       diff="Medium", pts=3),
    mc("`git diff` va `git diff --staged` orasidagi farq?",
       ["Hech qanday",
        "git diff — staging'da bo'lmaganlar. --staged — staging vs oxirgi commit",
        "--staged tezroq",
        "Faqat sintaktik"],
       "B", diff="Hard", pts=4),
    mc("Loyihada `git status` `node_modules/` ni ko'rsatmoqda. Nima qilishni kerak?",
       ["O'chirib tashlash",
        "Commit qilish",
        ".gitignore'ga `node_modules/` qatorini qo'shish",
        "Hech narsa"],
       "C", explanation="node_modules — npm install bilan qayta yaratiladi. Hech qachon commit qilmang.",
       diff="Easy", pts=2),
    mc("`git blame fayl.py` nima qiladi?",
       ["Faylni o'chiradi",
        "Har qator kim va qaysi commit'da yozilganini ko'rsatadi",
        "Faylni reset qiladi",
        "Tarixni bekor qiladi"],
       "B", explanation="Debug uchun zarur: 'shu bug qachondan paydo bo'lgan?' — blame'dan ko'rinadi.",
       diff="Easy", pts=2),
    dd("Tarixni go'zal grafik bilan ko'rsatuvchi alias yaratish",
       ["git config --global alias.lg \\",
        "    \"log --oneline --graph --decorate --all\"",
        "# Endi:",
        "git lg"],
       diff="Medium", pts=3),
    ti("Tasodifan .env fayl push qildingiz, ichida API kalit. Birinchi nima qilish kerak?",
       "1) BIRINCHI: kalitni darhol rotation qiling (AWS/Stripe/GitHub'da bekor qilib yangisini yarating). "
       "Bu eng muhim, chunki kalit allaqachon GitHub'da ko'rinadi va botlar uni topishlari mumkin. "
       "2) .gitignore ga .env qo'shing va commit qiling. "
       "3) Faylni tarixdan tozalash — git filter-repo yoki BFG (qiyin, force-push kerak — jamoadosh bilan kelishing). "
       "4) GitHub'da repo'ni private qilish (vaqtinchalik). "
       "Asosiy daraja: PREVENTION — birinchi commit'dan oldin .gitignore yarating.",
       hint="Kalit rotation BIRINCHI bo'lishi kerak.",
       diff="Hard", pts=4),
]
L3_EX: list = [
    mc("Git'da branch nima?",
       ["Loyihaning butun nusxasi",
        "Commit'ga ishora qiluvchi pointer — yondosh versiya",
        "Backup",
        "Faqat eski versiya"],
       "B", explanation="Branch — pointer. Yangi commit qilsangiz, pointer ko'chadi.",
       diff="Medium", pts=3),
    mc("Yangi branch yaratib darhol o'tish uchun zamonaviy buyruq:",
       ["git branch X && git switch X",
        "git switch -c X",
        "git checkout X",
        "git create X"],
       "B", explanation="-c = create. Bitta buyruqda yaratib, o'tadi.",
       diff="Easy", pts=2),
    mc("`git merge feature/login` qaysi branchni qaysiga qo'shadi?",
       ["main'ni feature'ga",
        "Hozirgi branchga feature/login'ni",
        "Doim main'ga",
        "Hech qaysisi"],
       "B", explanation="Merge buyrug'i — hozirgi branchga (HEAD) belgilangan branchni qo'shadi.",
       diff="Medium", pts=3),
    mc("'Fast-forward merge' qachon bo'ladi?",
       ["main yangi commit'lar olgan paytda",
        "main hech o'zgarmagan, feature ilgariga ketganida — main pointer feature'ga sirpanadi",
        "Har doim",
        "Hech qachon"],
       "B", explanation="Linear history — eng yaxshi. Yangi merge commit yaratilmaydi.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari YAXSHI branch nomlari?",
       ["feature/login-form",
        "fix/payment-crash",
        "asdf",
        "my-branch",
        "refactor/api-client",
        "hotfix/db-migration"],
       "A,B,E,F", multi=True,
       hint="Tur prefiks + tavsif. Aniq, qisqa.",
       diff="Medium", pts=3),
    dd("main'dan yangi feature branch yaratish va merge qilish",
       ["git switch main",
        "git switch -c feature/yangi-narsa",
        "# ... kod yozish ...",
        "git add .",
        "git commit -m 'feat: yangi narsa'",
        "git switch main",
        "git merge feature/yangi-narsa",
        "git branch -d feature/yangi-narsa"],
       diff="Hard", pts=4),
    ti("Commit qilmagan o'zgarishlar bor paytda `git switch boshqa-branch` xato beradi. Nima uchun va 2 ta yechim qaysi?",
       "Sabab: o'zgartirilgan fayllar hali commit qilinmagan. Boshqa branchga o'tish — ularni "
       "yo'qotishi mumkin (yangi branchda boshqa mazmun bo'lishi mumkin). "
       "Yechim 1: COMMIT — yarim ish bo'lsa ham (keyin amend bilan to'g'rilash mumkin, 7-darsda). "
       "Yechim 2: STASH — `git stash` bilan vaqtinchalik saqlash, branchga o'tish, ish tugagach "
       "`git stash pop` bilan tiklash (8-darsda). "
       "Stash — qachon ishingiz hali commit'ga arzimagani uchun.",
       hint="Commit yoki stash.",
       diff="Hard", pts=4),
]
R1_EX: list = [
    mc("Yangi loyiha boshlash uchun birinchi nima qilamiz?",
       ["git push",
        "Papka yaratish + git init + .gitignore + birinchi commit",
        "GitHub'da repo ochish",
        "Hech narsa"],
       "B", diff="Easy", pts=2),
    mc("Conventional commit'da yangi fayl qo'shish — qaysi prefix?",
       ["fix",
        "feat",
        "chore",
        "docs"],
       "B", explanation="feat: yangi funksionallik. chore: ish bilan bog'liq emas (deps, config).",
       diff="Easy", pts=2),
    mc("`shablonlar/kun-shabloni.md` faylida o'zgarishlar bor. Faqat shu faylni commit qilish:",
       ["git add . && git commit",
        "git add shablonlar/kun-shabloni.md && git commit -m 'docs: shablon'",
        "git commit shablonlar/kun-shabloni.md",
        "git push shablon"],
       "B", diff="Medium", pts=3),
    dd("Yangi feature uchun branch yaratib, merge qilish",
       ["git switch main",
        "git switch -c feature/teglar",
        "# ... o'zgarishlar ...",
        "git add .",
        "git commit -m 'feat(teglar): qo'shildi'",
        "git switch main",
        "git merge feature/teglar",
        "git branch -d feature/teglar"],
       diff="Medium", pts=3),
    mc(".gitignore ga `*.tmp` qatorini qo'shdingiz. Lekin `test.tmp` allaqachon commit qilingan. Nima bo'ladi?",
       ["Avtomatik o'chiriladi",
        "Hech narsa — gitignore faqat YANGI fayllarga ta'sir qiladi. Bor faylni `git rm --cached` bilan kuzatuvdan olish kerak",
        "Xato chiqaradi",
        "Shu fayl ham endi ignored bo'ladi"],
       "B", explanation="Gitignore — kuzatilmayotgan fayllar uchun. Bor fayl — git rm --cached.",
       diff="Hard", pts=4),
    ti("Branch'da commit qilinmagan o'zgarishlar bor paytda boshqa branchga o'tishga urindingiz va xato oldingiz. Eng yaxshi yo'l qaysi va nima uchun?",
       "Eng yaxshi: agar ish hali yarim — `git stash` (vaqtinchalik saqlash, 7-darsda). "
       "Branchga o'tib, ish qilish, qaytish, `git stash pop` bilan tiklash. "
       "Agar ish tugagan/yaxshi holatda — commit qilish (keyin amend bilan tahrirlash mumkin). "
       "Hech qachon: o'zgartirishlarni yo'qotish (git checkout . yoki force switch). "
       "Stash — Git'ning hayot saqlovchi xususiyati: kichik ish uzilganda himoyalanasiz.",
       hint="Stash yoki commit — qachon qaysi?",
       diff="Hard", pts=4),
    mc("Tarix tahlilida `git log --grep='feat'` qachon foydali?",
       ["Hech qachon",
        "Faqat yangi funksionalliklar (feature) qo'shilgan commit'larni filterlash uchun",
        "Bug'larni topish uchun",
        "Performance uchun"],
       "B", explanation="Release notes yozishda yoki feature progress'ni hisobotlash uchun zarur.",
       diff="Easy", pts=2),
]
L4_EX: list = [
    mc("SSH key nima uchun kerak?",
       ["Repo tezligini oshirish",
        "Har push/pull'da parol so'ramasdan GitHub'ga avtomatik bog'lanish",
        "Faqat backup",
        "Branch yaratish uchun"],
       "B", diff="Easy", pts=2),
    mc("Lokal repo'ni GitHub'ga ulash uchun:",
       ["git push",
        "git remote add origin <url>",
        "git init github",
        "git connect"],
       "B", explanation="origin — remote'ning konvensional nomi.",
       diff="Easy", pts=2),
    mc("Birinchi push'da `-u` flag nima qiladi?",
       ["Tezroq push qiladi",
        "Upstream sozlaydi — keyingi git push/pull qisqartirilgan bo'ladi",
        "Force push",
        "User'ni o'rnatadi"],
       "B", diff="Medium", pts=3),
    mc("`git push` xato berdi: 'rejected — fetch first'. Sabab va yechim?",
       ["Network xato — qaytadan urinish",
        "Remote'da yangiliklar bor, avval pull qilish kerak. Yechim: git pull, keyin git push",
        "Force push qilish",
        "Repo'ni delete qilish"],
       "B", explanation="Force push — boshqalarning ishini o'chiradi. Pull avval — to'g'ri.",
       diff="Medium", pts=3),
    mc("`git pull` va `git fetch` orasidagi farq?",
       ["Hech qanday",
        "pull = fetch + merge. fetch faqat olib keladi, merge qilmaydi",
        "fetch tezroq",
        "pull faqat birinchi marta"],
       "B", explanation="fetch — xavfsizroq (ko'rib chiqasiz, keyin merge). pull — bir buyruqda.",
       diff="Hard", pts=4),
    dd("Yangi loyihani GitHub'ga ulash bosqichlari",
       ["# 1) GitHub'da yangi repo (README'siz)",
        "# 2) Lokal'da:",
        "git remote add origin git@github.com:user/repo.git",
        "git remote -v",
        "git push -u origin main"],
       diff="Medium", pts=3),
    ti("`git push --force` qachon qabul qilinarli va qachon ASLO QILMASLIK kerak?",
       "QABUL QILINARLI: 1) Faqat O'ZINGIZNING shaxsiy branch'da (jamoadosh ishlatmaganida); "
       "2) Rebase yoki amend keyin — feature branch'ni tozalash uchun; "
       "3) Force-with-lease ishlating (xavfsizroq variant — agar boshqa eski'dan keyin commit bo'lsa, push to'xtaydi). "
       "ASLO QILMASLIK: 1) main yoki develop kabi umumiy branch'da; "
       "2) Jamoadosh ishlaydigan branch'da; "
       "3) Open source repo'da. "
       "Force push — boshqalarning commit'larini o'chirib tashlashi mumkin (ma'lumot yo'qoladi). "
       "Doim: git pull --rebase qilib, conflict'larni yeching, keyin oddiy push.",
       hint="Shaxsiy vs umumiy branch.",
       diff="Hard", pts=4),
]
L5_EX: list = [
    mc("Pull Request (PR) nima?",
       ["Repo'ni download qilish",
        "Branch'dagi o'zgarishlarni asosiy branchga qo'shish uchun rasmiy so'rov + review",
        "Fork'ning ikkinchi nomi",
        "Faqat private repo'larda"],
       "B", diff="Easy", pts=2),
    mc("'Fork' nima?",
       ["Branch yaratish",
        "Boshqa odamning repo'sini o'z hisobingizga to'liq nusxalash (alohida copy)",
        "Repo'ni delete qilish",
        "Faqat clone'ning sinonimi"],
       "B", explanation="Fork — bir martalik nusxa. Asl bilan avtomatik sync emas.",
       diff="Easy", pts=2),
    mc("Open source loyihada PR yuborish ketma-ketligi:",
       ["clone → branch → push → PR",
        "fork → clone → branch → commit → push → PR",
        "push directly → PR",
        "git request-pull"],
       "B", diff="Medium", pts=3),
    mc("PR ochildi va reviewer 'localStorage'da saqlang' dedi. Nima qilamiz?",
       ["Yangi PR ochamiz",
        "Shu branch'da yana commit + push qilamiz — PR avtomatik yangilanadi",
        "Force push",
        "PR'ni close qilib qaytadan"],
       "B", explanation="PR — branch'ga bog'langan. Yangi commit avtomatik PR'ga qo'shiladi.",
       diff="Medium", pts=3),
    mc("3 ta merge strategiyasi qaysi?",
       ["Create merge commit",
        "Squash and merge",
        "Force merge",
        "Rebase and merge",
        "Delete branch"],
       "A,B,D", multi=True,
       hint="Force merge — yo'q. Delete branch — merge'dan keyin.",
       diff="Medium", pts=3),
    dd("Open source PR yuborish bosqichlari",
       ["# 1. Fork (GitHub UI)",
        "git clone git@github.com:olim/cool-project.git",
        "cd cool-project",
        "git remote add upstream git@github.com:anthropic/cool-project.git",
        "git switch -c fix/typo",
        "# ... tahrirlar ...",
        "git add . && git commit -m 'fix: typo'",
        "git push -u origin fix/typo",
        "gh pr create --base main"],
       diff="Hard", pts=4),
    ti("Sizning fork 6 oy oldin qilingan, asl repo'da 200 ta yangi commit. Fork'ni qanday yangilaysiz?",
       "3 ta variant: "
       "1) Terminal — `git remote add upstream <asl-url>`, `git fetch upstream`, "
       "`git switch main`, `git merge upstream/main`, `git push origin main`. "
       "2) gh CLI — `gh repo sync olim/cool-project --branch main` (eng oson). "
       "3) GitHub UI — fork sahifasida 'Sync fork' tugmasi. "
       "Hammasi bir vazifani qiladi: upstream/main → sizning origin/main. "
       "PR yuborishdan oldin doim shu jarayonni o'tkazing — eskirgan fork'dan PR conflict beradi.",
       hint="upstream remote va sync.",
       diff="Hard", pts=4),
]
L6_EX: list = [
    mc("Merge conflict qachon paydo bo'ladi?",
       ["Doim merge'da",
        "2 ta branch bir xil faylning bir xil joyini har xil o'zgartirganida",
        "Faqat asosiy branch'da",
        "Faqat ko'p odamli loyihalarda"],
       "B", explanation="Har xil fayllar yoki har xil joylar — Git avtomatik birlashtiradi.",
       diff="Medium", pts=3),
    mc("Conflict markerlari qaysi?",
       ["<<<<<<<, =======, >>>>>>>",
        "// CONFLICT, // END",
        "[CONFLICT]...[/CONFLICT]",
        "#start, #end"],
       "A", diff="Easy", pts=2),
    mc("Conflict yechishning to'g'ri ketma-ketligi:",
       ["git commit, keyin faylni tahrirlash",
        "Faylni tahrirlash + markerlarni o'chirish, keyin git add, keyin git commit",
        "Faqat git add",
        "Branch'ni o'chirish"],
       "B", diff="Medium", pts=3),
    mc("Conflict paytida `git merge --abort` nima qiladi?",
       ["Conflict'ni avtomatik yechadi",
        "Merge'ni bekor qiladi — eski (merge'dan oldingi) holatga qaytaradi",
        "Faylni o'chiradi",
        "Push qiladi"],
       "B", explanation="Yangi boshlovchining hayotni saqlovchi buyruq — adashganda eski holatga qaytadi.",
       diff="Easy", pts=2),
    mc("`git checkout --ours fayl.txt` merge paytida nima qiladi?",
       ["Branchni o'zgartiradi",
        "Hozirgi (HEAD/main) versiyasini saqlaydi, boshqa versiyani tashlaydi",
        "Yangi fayl yaratadi",
        "Conflict'ni saqlaydi"],
       "B", explanation="--ours = bizniki (joriy). --theirs = ularniki (qo'shilayotgan).",
       diff="Hard", pts=4),
    dd("Conflict yechish bosqichlari",
       ["git merge feature/login",
        "# CONFLICT — git status bilan ko'rdik",
        "# Faylni tahrirlash — markerlarni o'chirish",
        "git add <yechilgan-fayl>",
        "git status   # tekshirish",
        "git commit   # merge'ni yakunlash"],
       diff="Medium", pts=3),
    ti("Conflict'ni 'yechib' commit qildingiz, lekin keyinroq faylda hali `<<<<<<<` markerlari qolganini ko'rdingiz. Nima bo'lgan va qanday tuzatish?",
       "Sabab: markerlarni butunlay olib tashlamagansiz. git add + git commit — yechilgan deb qabul qiladi (Git ichidagi mazmunni tekshirmaydi). "
       "Kompilyator/parser endi xato beradi: <<<<<<< — kod sintaksisi emas. "
       "Tuzatish: 1) Yangi commit yarating — faylni tahrirlang, markerlarni o'chiring, `git commit -m 'fix: conflict marker tozalandi'`. "
       "2) Yoki amend bilan oxirgi commit'ni tuzating (7-darsda). "
       "Oldini olish: doim conflict commit'dan keyin `grep -r '<<<<<<<' .` qiling yoki pre-commit hook o'rnating.",
       hint="Sintaksis xato va keyingi commit.",
       diff="Hard", pts=4),
]
R2_EX: list = [
    mc("Yangi boshlovchilar uchun eng yaxshi birinchi PR turi?",
       ["Asosiy feature qo'shish",
        "Typo fix yoki documentation",
        "Refactoring",
        "Security fix"],
       "B", explanation="Kichik, xavfsiz, qabul qilinishi oson.",
       diff="Easy", pts=2),
    mc("'good first issue' label nima?",
       ["Faqat hisobni belgilash",
        "Maintainer'lar tomonidan yangi boshlovchilar uchun belgilangan oson issue'lar",
        "Eng yaxshi issue",
        "Faqat closed issue'lar"],
       "B", explanation="Bu label'ni qidiring — yangi contributor'lar uchun kirish nuqtasi.",
       diff="Easy", pts=2),
    mc("PR yuborishdan oldin nima'ni o'qish KERAK?",
       ["Faqat README",
        "CONTRIBUTING.md — har loyihaning o'z qoidalari",
        "Hech narsa",
        "Faqat issue'lar"],
       "B", explanation="Code style, commit format, branch naming — hammasi CONTRIBUTING'da.",
       diff="Medium", pts=3),
    mc("Sizning PR 2 hafta ichida hech qanday javob olmagan. Nima qilamiz?",
       ["Yana 10 ta PR ochish",
        "Sabr bilan kutish — open source maintainer'lar volunter, vaqt ko'p kerak. Comment yozsangiz bo'ladi, lekin nazokat bilan",
        "Issue ochish",
        "Yopib qaytadan"],
       "B", diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari YAXSHI birinchi PR amaliyot?",
       ["Faqat MOSLI faylni o'zgartirish (begona narsa qo'shmaslik)",
        "Conventional commit format",
        "Closes #N bilan issue'ni bog'lash",
        "Force push qilish",
        "Maintainer'larni @ tag qilib spam qilish",
        "Tahrirgacha CONTRIBUTING.md ni o'qish"],
       "A,B,C,F", multi=True,
       hint="Force push va spam — ASLO.",
       diff="Medium", pts=3),
    dd("Open source PR yuborishning to'liq jarayoni",
       ["# 1. Repo tanlash + CONTRIBUTING.md o'qish",
        "# 2. Fork (GitHub UI)",
        "git clone git@github.com:olim/repo.git",
        "git remote add upstream git@github.com:asl-org/repo.git",
        "git switch -c fix/typo",
        "# ... tahrirlar ...",
        "git add . && git commit -m 'fix: typo'",
        "git push -u origin fix/typo",
        "gh pr create --base main",
        "# ... review kutib ...",
        "# Merge bo'lgach:",
        "git switch main && git pull upstream main && git push origin main",
        "git branch -d fix/typo"],
       diff="Hard", pts=4),
    ti("PR yuborgach maintainer 'Sorry, this doesn't fit our roadmap' deb rad etdi. Nima qilamiz?",
       "1) Sabr bilan qabul qiling — bu open source hayoti, hatto experiment dasturchilarda ham bo'ladi. "
       "2) Issue'da maintainer'ga rahmat ayting — vaqt ajratgani uchun. "
       "3) Sababini tushunishga harakat qiling (kelajak loyihalar uchun). "
       "4) Boshqa repo'ga o'ting — 'good first issue' label bilan yana qidiring. "
       "5) Boshqa muammo bilan shu repo'ga qaytib kelishingiz mumkin (boshqa narsa qo'shing). "
       "Reject — bekorlik emas, ko'pincha loyihaning yo'nalishi yoki vaqt cheklovi. "
       "Hatto rad etilgan PR ham CV uchun yaxshi — siz harakat qildingiz, jamoa bilan ishladingiz.",
       hint="Sabr, rahmat, boshqa repo.",
       diff="Hard", pts=4),
]
L7_EX: list = [
    mc("`git stash` nima qiladi?",
       ["Faylni o'chiradi",
        "Hozirgi (commit qilinmagan) o'zgarishlarni vaqtinchalik saqlaydi va working directory'ni tozalaydi",
        "Branch o'chiradi",
        "Push qiladi"],
       "B", diff="Easy", pts=2),
    mc("`git stash pop` va `git stash apply` farqi?",
       ["Hech qanday",
        "pop — qaytarish + stash'ni o'chirish. apply — qaytarish, stash'da qoladi",
        "pop tezroq",
        "apply faqat root user uchun"],
       "B", diff="Medium", pts=3),
    mc("`git cherry-pick abc1234` nima qiladi?",
       ["Branch'ni o'chiradi",
        "Boshqa branch'dagi `abc1234` commit'ni hozirgi branchga nusxalaydi",
        "Yangi commit yaratadi",
        "Faylni qaytaradi"],
       "B", explanation="Faqat 1 commit (yoki bir necha) — boshqalari emas. Selektiv qo'shish.",
       diff="Medium", pts=3),
    mc("`git commit --amend` nima qiladi?",
       ["Yangi commit qo'shadi",
        "Oxirgi commit'ni tahrirlash — yangi xabar yoki yangi fayl qo'shish",
        "Branch'ni rename",
        "Push qiladi"],
       "B", explanation="Diqqat: yangi SHA yaratiladi. Push qilingan commit uchun xavfli.",
       diff="Medium", pts=3),
    mc("Quyidagi vaziyatlardan qaysilarida `git commit --amend` XAVFLI?",
       ["Push qilmagan commit, faqat lokal",
        "Push qilingan, shared main branch",
        "Hech kim hali pull qilmagan shaxsiy branch",
        "Push qilingan, jamoadosh pull qilgan",
        "Faqat xabar tuzatish, push qilmagan"],
       "B,D", multi=True,
       hint="Push + jamoadosh ishlatgan — xavf.",
       diff="Hard", pts=4),
    dd("Yarim ishni saqlab, boshqa branchda fix qilib, qaytib davom etish",
       ["git stash push -m 'WIP: profil ishi'",
        "git switch main",
        "git switch -c hotfix/critical",
        "# ... fix qilish ...",
        "git add . && git commit -m 'fix: critical'",
        "git switch profil-branch",
        "git stash pop"],
       diff="Medium", pts=3),
    ti("Sherigingiz feature/big branch'da 10 ta commit qildi, biri muhim hotfix. Boshqalari hali tugamagan. Faqat hotfix'ni main'ga qanday olamiz?",
       "git cherry-pick <hotfix-SHA>. Bosqichlar: "
       "1) git log feature/big --oneline — hotfix commit SHA topish; "
       "2) git switch main; "
       "3) git cherry-pick <SHA>; "
       "4) Agar conflict bo'lsa — yeching, git add ., git cherry-pick --continue. "
       "5) git push. "
       "Cherry-pick — selektiv: faqat shu commit, boshqa 9 ta o'zgarish main'ga kirmaydi. "
       "Merge bilan — hammasi kelar edi (siz xohlamagan). Cherry-pick — keng tarqalgan hotfix pattern.",
       hint="cherry-pick + SHA.",
       diff="Hard", pts=4),
]
L8_EX: list = [
    mc("Merge va Rebase orasidagi asosiy farq?",
       ["Hech qanday",
        "Merge: tarix saqlanadi, merge commit yaratiladi. Rebase: commit'lar qayta yoziladi (yangi SHA), linear tarix",
        "Rebase tezroq",
        "Merge faqat main'da"],
       "B", diff="Medium", pts=3),
    mc("Rebase'ning ASOSIY xavfi qaysi?",
       ["Sekin",
        "Commit'lar SHA o'zgaradi — push qilinganida jamoadosh tarixi bilan to'qnashadi",
        "Faqat sintaksis",
        "Hech qanday"],
       "B", diff="Hard", pts=4),
    mc("Interactive rebase'da 3 ta commit'ni 1 ga birlashtirish — qaysi keyword?",
       ["merge",
        "squash (yoki fixup)",
        "drop",
        "combine"],
       "B", explanation="squash — xabar tahrir bilan. fixup — eski xabarni saqlaydi.",
       diff="Medium", pts=3),
    mc("`git pull --rebase` nima qiladi?",
       ["pull va keyin rebase alohida",
        "Bir buyruqda: fetch + rebase (merge o'rniga) — tarix toza qoladi",
        "Faqat fetch",
        "Push qiladi"],
       "B", explanation="Default sozlash: git config --global pull.rebase true.",
       diff="Medium", pts=3),
    mc("Quyidagi vaziyatlarda QAYSI yondashuv yaxshiroq?",
       ["main'ni feature'ga olib kelish — rebase",
        "Feature'ni main'ga qo'shish — merge yoki squash",
        "Shaxsiy branch tarixini tozalash — interactive rebase",
        "Push qilingan main'da rebase",
        "Jamoa ishlaydigan branch'da rebase",
        "Pull qilishda toza tarix — pull --rebase"],
       "A,B,C,F", multi=True,
       hint="Push qilingan + shared — merge.",
       diff="Hard", pts=4),
    dd("Rebase paytida conflict bo'lganida nima qilamiz",
       ["git rebase main",
        "# CONFLICT in: shared.txt",
        "# Faylni tahrir, marker'larni o'chirish",
        "git add shared.txt",
        "# DIQQAT: git commit YO'Q (rebase)",
        "git rebase --continue",
        "# Yoki bekor qilish: git rebase --abort"],
       diff="Hard", pts=4),
    ti("`git push --force-with-lease` va `git push --force` orasidagi farq nima va nima uchun --with-lease afzal?",
       "--force: lokal'dagi tarixni REMOTE'ga majburiy yozadi, eski qiymatlarni e'tibordan tashqari. Boshqa odamning ishi o'chishi mumkin. "
       "--force-with-lease: TEKSHIRADI — remote sizning oxirgi pull qilgan paytdagi versiyada turgan bo'lsa, push o'tadi. Agar boshqa yangi commit bo'lsa (kimdir push qilgan) — push to'xtaydi. "
       "Bu — \"ma'lumot yo'qotmaslik\" kafolati. Rebase yoki amend keyin doim --force-with-lease. "
       "--force — faqat eski Git habit, hech qachon ishlatmang. Yaxshi default: git config --global push.default current.",
       hint="Yo'qotish xavfi.",
       diff="Hard", pts=4),
]
L9_EX: list = [
    mc("`git reset --hard HEAD~1` nima qiladi?",
       ["Faqat commit'ni ochadi",
        "Commit + staging + working directory — HAMMASINI o'chiradi (commit qilinmagan ishlar yo'qoladi)",
        "Yangi commit qiladi",
        "Push qiladi"],
       "B", explanation="Eng xavfli reset. Faqat aniq xohlaganingizda. Push qilingan'da ASLO.",
       diff="Hard", pts=4),
    mc("Push qilingan commit'ni qaytarish uchun qaysi xavfsiz?",
       ["git reset --hard",
        "git revert (yangi commit yaratadi, tarix saqlanadi)",
        "git push --force",
        "git delete"],
       "B", diff="Medium", pts=3),
    mc("`git reflog` nima qiladi?",
       ["Branch'larni ko'rsatadi",
        "Lokal'dagi har HEAD harakatini (commit, checkout, reset, merge) saqlaydi — yo'qolgan commit'ni topishga yordam",
        "Faqat log",
        "Push tarixi"],
       "B", explanation="Git'ning eng katta hayot saqlovchi xususiyati.",
       diff="Medium", pts=3),
    mc("Tasodifan `git branch -D important` qildingiz. Qaytarish:",
       ["Mumkin emas",
        "git reflog bilan oxirgi commit SHA topib, git branch important <SHA>",
        "git restore",
        "git revert"],
       "B", explanation="Branch — pointer. SHA o'sha yerda. Pointer'ni qaytadan yaratish.",
       diff="Hard", pts=4),
    mc("`git reset --soft`, `--mixed` (default), `--hard` orasidagi farq?",
       ["soft: commit + staging + working — hammasi yo'q",
        "soft: commit ochiladi, staging saqlanadi, working saqlanadi",
        "mixed: commit + staging tozalanadi, working saqlanadi",
        "hard: hammasi yo'q (xavfli)",
        "soft tezroq",
        "hammasi bir xil"],
       "B,C,D", multi=True,
       hint="soft saqlaydi ko'p, hard saqlamaydi hech narsa.",
       diff="Hard", pts=4),
    dd("Yo'qolgan commit'ni reflog orqali qaytarish",
       ["git reflog",
        "# Yo'qolgan SHA topish — masalan 9012345",
        "git reset --hard 9012345",
        "# Yoki yangi branch yaratish:",
        "# git branch saved-work 9012345"],
       diff="Medium", pts=3),
    ti("Force push bilan jamoadosh tarixingizni overwrite qildi. Sizning ishingiz lokal'da bormi va qanday qaytaramiz?",
       "Ha — lokal'da bor (Git har harakatni saqlaydi). Yo'l: "
       "1) git reflog — eski tarix oxirgi SHA topish (force push'dan oldingisi); "
       "2) git reset --hard HEAD@{N} — o'sha holatga qaytish; "
       "3) Yoki yangi branch: git branch backup HEAD@{N}; "
       "4) Push qaytarish — boshqa jamoadoshlar bilan kelishish (force push qaytarish — tarix to'qnashuvi); "
       "5) Eng yaxshisi — jamoa orasida 'force push kerakmi?' deb avval kelishish. "
       "Reflog faqat lokal va vaqt cheklangan (default 30 kun) — har harakat keyin yangilanadi.",
       hint="Reflog lokal saqlaydi.",
       diff="Hard", pts=4),
]
R3_EX: list = [
    mc("Tasodifan `git branch -D feature/important` qildingiz. Birinchi qadam?",
       ["Panika qilish",
        "git reflog — yo'qolgan commit SHA topish",
        "Yangi commit qilish",
        "git push"],
       "B", explanation="Reflog — lokal'da har harakatni saqlaydi.",
       diff="Easy", pts=2),
    mc("Push qilingan commit yomon. Qaysi xavfsiz?",
       ["git reset --hard",
        "git revert (yangi commit bekor qiluvchi, tarix saqlanadi)",
        "git push --force",
        "git delete"],
       "B", diff="Medium", pts=3),
    mc("Wrong branch'da 3 commit qilingan. main'dan profile'ga qanday ko'chiramiz?",
       ["git move",
        "git branch profile  (main'da SHA saqlash) + git reset --hard HEAD~3 main'da",
        "git cherry-pick uchun yangi branch",
        "Yangi loyiha"],
       "B", explanation="Branch — pointer. Yangi pointer + main'ni orqa siljitish.",
       diff="Hard", pts=4),
    mc("Detached HEAD'da commit qildingiz, keyin main'ga o'tdingiz. Commit'lar ko'rinmaydi. Sabab?",
       ["Yo'qoldi",
        "Commit'lar bor (Git ob'ektlarda), lekin branch'siz qoldi — git reflog + git branch <yangi> <SHA>",
        "Faqat reset bilan",
        "Bekor bo'lib ketgan"],
       "B", explanation="Branch yo'q = ko'rinmaydi. SHA topib pointer yarating.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari hayot saqlovchi recovery vositalar?",
       ["git reflog",
        "git fsck --lost-found",
        "git stash list",
        "git push --force",
        "git rebase --abort",
        "git merge --abort"],
       "A,B,C,E,F", multi=True,
       hint="push --force yo'qotadi, saqlamaydi.",
       diff="Medium", pts=3),
    dd("Reset --hard yo'qotgan ishni qaytarish bosqichlari",
       ["git reflog",
        "# Yo'qolgan oxirgi commit SHA topish",
        "git reset --hard HEAD@{1}",
        "# Yoki:",
        "# git branch saved <SHA>"],
       diff="Medium", pts=3),
    ti("Eng katta recovery saboq — Git'da panika qilmaslik. Nima uchun?",
       "Sabab: Git deyarli hech narsa abadiy o'chirmaydi. Har commit, branch, "
       "hatto reset --hard keyin ham — ob'ekt .git/objects ichida qoladi (default 30 kun, "
       "git gc bekor qilguncha). Reflog 90 kun saqlaydi. "
       "Birinchi qoidasi — panika qilmang. 2-qoidasi — git reflog tekshiring. "
       "3-qoidasi — kerakli SHA ni topgach, git branch <yangi> <SHA> bilan saqlang. "
       "ASLO QILMASLIK: panika holatida force push, hard reset, branch delete. "
       "Bularning hammasi vaziyatni og'irlashtirishi mumkin. "
       "Eng yaxshisi — har xato keyin git reflog'ga qarash.",
       hint="Reflog va sabr.",
       diff="Hard", pts=4),
]
L10_EX: list = [
    mc("`v1.2.3` SemVer'da `3` raqami nima?",
       ["Major version",
        "Minor version",
        "Patch version (bug fix)",
        "Pre-release"],
       "C", explanation="major.minor.patch. Patch — bug fix. Minor — yangi feature. Major — breaking.",
       diff="Easy", pts=2),
    mc("`git tag v1.0.0` va `git tag -a v1.0.0 -m 'msg'` farqi?",
       ["Hech qanday",
        "Birinchi lightweight (pointer faqat). Ikkinchi annotated (xabar, vaqt, tagger bilan)",
        "Birinchi tezroq",
        "Faqat -a versiya"],
       "B", explanation="Production release'lar uchun annotated tavsiya.",
       diff="Medium", pts=3),
    mc("GitHub Actions YAML faylida indentatsiya:",
       ["1 bo'shliq",
        "2 bo'shliq (faqat space, tab emas)",
        "4 bo'shliq",
        "Tab"],
       "B", explanation="YAML — strict syntax. 2 spaces, hech qachon tab.",
       diff="Hard", pts=4),
    mc("Tag'larni remote'ga push qilish — qaysi buyruq?",
       ["git push",
        "git push --tags (yoki git push origin v1.0.0)",
        "git tag push",
        "git upload tags"],
       "B", explanation="Oddiy git push tag'larni push qilmaydi — alohida flag.",
       diff="Easy", pts=2),
    mc("GitHub Actions'da sirli ma'lumotlar (API key) qaerga saqlanadi?",
       ["Kodda bevosita",
        "Settings → Secrets and variables → Actions",
        ".env faylda commit qilingan",
        "README'da"],
       "B", explanation="Secrets — kodda ko'rinmaydi, workflow'da ${{ secrets.X }} bilan ishlatiladi.",
       diff="Medium", pts=3),
    dd("Python tests uchun GitHub Action workflow yozish",
       ["name: Tests",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "    branches: [main]",
        "jobs:",
        "  test:",
        "    runs-on: ubuntu-latest",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: actions/setup-python@v5",
        "        with:",
        "          python-version: '3.12'",
        "      - run: pip install -r requirements.txt",
        "      - run: pytest"],
       diff="Hard", pts=4),
    ti("Matrix builds (matrix strategy) nima va qachon foydali?",
       "Matrix builds — bir workflow'ni bir nechta versiya/OS/parametr bilan PARALLEL ishga tushirish. "
       "Misol: Python 3.10, 3.11, 3.12 da hamma testlarni alohida ishlatish, "
       "yoki Linux+macOS+Windows da. Strategy: matrix: { python: [...] }. "
       "Foydasi: 1) library multi-version compatibility; 2) cross-platform release; "
       "3) tezroq feedback (parallel). "
       "Diqqat: GitHub bepul minutes cheklangan — matrix ko'p resurs sarflaydi. "
       "Lekin open source uchun bepul cheksiz public repo'larda.",
       hint="Parallel test bir nechta version.",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("Yakuniy capstone'da jamoa nechta odam tavsiya etiladi?",
       ["1 (yolg'iz)",
        "2-4 (haqiqiy jamoaviy ish uchun)",
        "10+",
        "Aniq emas"],
       "B", explanation="2-4 — har odam o'z hissasini ko'rsata oladi, conflict yechish bilan tanishish mumkin.",
       diff="Easy", pts=2),
    mc("Branch protection rules main uchun nima qiladi?",
       ["Branch'ni delete qiladi",
        "main'ga to'g'ridan-to'g'ri push'ni bloklaydi — faqat PR + approve orqali",
        "Hech narsa",
        "Faqat performance"],
       "B", diff="Medium", pts=3),
    mc("Issue va PR orasidagi bog'lanish:",
       ["Hech qanday",
        "PR description'da 'Closes #N' — merge bo'lganda issue avtomatik yopiladi",
        "Faqat manual",
        "Faqat tashkilot uchun"],
       "B", explanation="Closes, Fixes, Resolves — GitHub'da ishlaydi. Manual close shart emas.",
       diff="Medium", pts=3),
    mc("Capstone uchun MAJBURIY qaysilari?",
       ["Conventional Commits",
        "GitHub Actions CI",
        "Tag + Release",
        "10000 ta commit",
        "Branch protection",
        "PR review"],
       "A,B,C,E,F", multi=True,
       hint="Commit soni — sifat emas, miqdor.",
       diff="Medium", pts=3),
    mc("Reviewer sifatida PR'ga 3 ta variant javob:",
       ["Approve / Comment / Request changes",
        "Yes / No / Maybe",
        "Like / Dislike",
        "Faqat Approve"],
       "A", explanation="Approve — yashil chiroq. Comment — savol/taklif (block emas). Request changes — qizil chiroq.",
       diff="Easy", pts=2),
    dd("Capstone'da birinchi feature PR yuborish qadamlari",
       ["# 1. Issue tanlash va assign",
        "gh issue edit 1 --add-assignee '@me'",
        "git switch -c feature/X",
        "# ... kod yozish ...",
        "git add . && git commit -m 'feat: X'",
        "git push -u origin feature/X",
        "gh pr create --title 'feat: X' --body 'Closes #1'",
        "# Review kelishini kuting",
        "# Approve + CI yashil bo'lgach: gh pr merge --squash"],
       diff="Hard", pts=4),
    ti("Bu kursni va capstone'ni tugatgandan keyin siz CV'da nimani yozasiz?",
       "1) 'Jamoaviy Git workflow ekspertizasi' — branch protection, PR review, conflict yechish, CI/CD. "
       "2) 'Open source contributor' — sizning birinchi (R2'dan) va keyingi PR'lar. "
       "3) Real loyiha — link bilan (GitHub repo + live deploy). "
       "4) GitHub profil — yashil contribution graph, pinned loyihalar. "
       "5) Texnik mavzular interview uchun: rebase, merge strategiyasi, recovery (reflog), CI/CD asoslari. "
       "6) Jamoaviy ish ko'nikmasi — code review, issue management, kelishish. "
       "Asosiy: siz endi har boshqa kursdan oson o'tasiz (Git har joyda kerak) va real loyihalarga tayyor.",
       hint="CV uchun nima muhim.",
       diff="Easy", pts=2),
]


LESSON_TASKS: dict = {
    0: {
        "title": "Birinchi Git repo (init, add, commit, log)",
        "description": "Lokal repo yarating, fayllar bilan ishlang, conventional commit'lar yozing.",
        "requirements": (
            "• `git config` bilan ism va email sozlash\n"
            "• Yangi papka + `git init`\n"
            "• 5+ commit (har xil tipda: feat, fix, docs, chore)\n"
            "• Conventional Commits formati\n"
            "• `git log --oneline` natijasi (screenshot)\n"
            "• `git show` bilan bitta commit batafsil\n"
            "• Multi-line commit yozish (`-m` ikki marta)\n"
            "• Ataylab xato: `add` siz `commit` urinish va sabab tushuntirish"
        ),
        "technologies": "Git, init, add, commit, log, conventional commits",
        "deadline_days": 2,
    },
    1: {
        "title": ".gitignore va tarix tahlili",
        "description": "Loyiha uchun .gitignore yarating va Git tarixini chuqur tahlil qiling.",
        "requirements": (
            "• Loyiha turi uchun moslangan .gitignore (Python yoki Node)\n"
            "• `.env` faylni yaratib `git status` da ko'rinmasligini tasdiqlash\n"
            "• Global `.gitignore_global` sozlash\n"
            "• `git diff` 3 ta variantda misol: working/staged/HEAD\n"
            "• `git log --oneline --graph --all` aliasi yaratish\n"
            "• `git blame` bilan har qator tarixi\n"
            "• `git log -S 'soz'` bilan qidirish\n"
            "• Allaqachon kuzatilgan faylni `git rm --cached` bilan ignore'ga"
        ),
        "technologies": "Git, .gitignore, log, diff, blame, alias",
        "deadline_days": 2,
    },
    2: {
        "title": "Branch va merge amaliyot",
        "description": "Bir nechta branch yaratib, ishlang va merge qiling.",
        "requirements": (
            "• 3-4 ta feature branch yaratish (`feature/X` format)\n"
            "• Har birida 2-3 ta commit\n"
            "• Fast-forward merge misoli\n"
            "• 3-way merge (merge commit) misoli\n"
            "• Branch o'chirish (`-d` xavfsiz va `-D` majburiy)\n"
            "• Branch rename (`-m`)\n"
            "• Ataylab xato: commit qilinmagan o'zgarishlar bilan branch o'zgartirish urinish\n"
            "• `git log --graph --all` bilan branchlar grafigi"
        ),
        "technologies": "Git, branch, switch, merge, fast-forward, 3-way merge",
        "deadline_days": 3,
    },
    3: {  # R1
        "title": "🔁 R1: Shaxsiy kunlik commit jurnal",
        "description": (
            "Modul 1 takrorlash: real loyiha — kunlik jurnal, har kun commit. "
            "JSX + Props + useState + branch + merge birga."
        ),
        "requirements": (
            "• `kundalik/` papkasi + git init + README + .gitignore\n"
            "• `shablonlar/kun-shabloni.md` (## 🎯, ## 🐛, ## 💡, ## 📋)\n"
            "• `feature/teglar` branch — README ga teglar bo'limi qo'shish\n"
            "• Branch'ni main'ga merge va branchni o'chirish\n"
            "• 5 ta kunlik yozuv (2026/06/08.md ... 12.md)\n"
            "• Har kun alohida commit (`docs(daily): X-iyun yozuv`)\n"
            "• Hech bo'lmaganda bir yozuvni tahrirlab `git diff` bilan ko'rsatish\n"
            "• Tarix tahlili faylida: jami commit, eng katta o'zgarish, blame natijasi\n"
            "• `*.tmp` ignore'da ishlashini tasdiqlash"
        ),
        "technologies": "Git, init, gitignore, commit, branch, merge, log",
        "deadline_days": 4,
    },
    4: {
        "title": "GitHub'ga birinchi push",
        "description": "GitHub account ochish, SSH sozlash, lokal repo'ni GitHub'ga ulash.",
        "requirements": (
            "• GitHub account (bepul)\n"
            "• SSH key yaratish (`ssh-keygen -t ed25519`)\n"
            "• Public key'ni GitHub'ga qo'shish\n"
            "• `ssh -T git@github.com` bilan tasdiqlash\n"
            "• GitHub'da yangi repo (README'siz)\n"
            "• Lokal repo'ga `git remote add origin`\n"
            "• `git push -u origin main`\n"
            "• Yangi commit + `git push` (qisqartirilgan)\n"
            "• Repo'ni boshqa joyga `git clone`\n"
            "• `git pull` bilan yangiliklar olish\n"
            "• Feature branch yaratib `git push -u origin feature/X`"
        ),
        "technologies": "Git, GitHub, SSH, remote, push, pull, clone",
        "deadline_days": 3,
    },
    5: {
        "title": "Pull Request lifecycle amaliyot",
        "description": "O'z repo'da PR yaratish, review va merge.",
        "requirements": (
            "• Feature branch yaratish + 2-3 ta commit\n"
            "• `git push -u origin feature/X`\n"
            "• GitHub UI'da PR yaratish (title + description + screenshot)\n"
            "• Conventional commit format title\n"
            "• PR description'da Closes #N\n"
            "• `gh pr create` CLI bilan ham urinish\n"
            "• O'zingiz approve (yoki sherikingiz bilan)\n"
            "• 3 ta merge strategiyani sinab ko'rish (squash tavsiya)\n"
            "• Branch o'chirish (lokal va remote)\n"
            "• Draft PR misoli\n"
            "• `gh pr list`, `gh pr view --web` ishlatish"
        ),
        "technologies": "GitHub, PR, gh CLI, review, merge strategies",
        "deadline_days": 4,
    },
    6: {
        "title": "Merge conflict yechish laboratoriyasi",
        "description": "Conflict'lar yaratib (har xil holatlarda) qanday yechishni amaliyot qilish.",
        "requirements": (
            "• Senariy 1: oddiy 2 branch conflict — yechish va commit\n"
            "• Senariy 2: 3 ta faylda conflict — har birini alohida yechish\n"
            "• `git merge --abort` bilan bekor qilish\n"
            "• `git checkout --ours` va `--theirs` ishlatish\n"
            "• PR'da conflict — lokal'da yechish va qaytadan push\n"
            "• Visual mergetool sozlash (VS Code)\n"
            "• Ataylab xato: markerlarni o'chirmasdan commit (sabab tushuntirish)\n"
            "• Conflict'ni oldini olish strategiyalari hisoboti"
        ),
        "technologies": "Git, merge, conflict, mergetool, abort, ours/theirs",
        "deadline_days": 4,
    },
    7: {  # R2
        "title": "🔁 R2: Open source repo'ga real PR",
        "description": (
            "Modul 2 takrorlash: HAQIQIY open source loyihaga PR yuborish. "
            "Fork → clone → branch → push → PR → review jarayoni."
        ),
        "requirements": (
            "• 'good first issue' label bilan kamida 3 ta repo tahlili\n"
            "• Repo tanlash (100+ star, faol)\n"
            "• CONTRIBUTING.md o'qish va qoidalarga rioya\n"
            "• Fork qilish (GitHub UI yoki `gh repo fork`)\n"
            "• `upstream` remote qo'shish\n"
            "• Yangi branch (`fix/...` yoki `docs/...`)\n"
            "• Tahrir (typo, docs, kichik fix)\n"
            "• Conventional commit + push\n"
            "• PR yuborish (title + description + Closes #N)\n"
            "• Maintainer feedback'ga javob (sabr bilan)\n"
            "• Merge bo'lgach: fork'ni sync qilish, branchni o'chirish\n"
            "• Reject bo'lsa — boshqa repo bilan qaytadan urinish\n"
            "• Hisobot: tanlangan repo URL, PR URL, jarayon haqida"
        ),
        "technologies": "GitHub, fork, PR, open source, gh CLI",
        "deadline_days": 7,
    },
    8: {
        "title": "Stash, cherry-pick, amend amaliyot",
        "description": "Kunlik productivity qurollarini amaliyot.",
        "requirements": (
            "• `git stash` 3 ta vaziyatda: yarim ish, pull conflict oldini olish, eksperiment\n"
            "• `git stash list`, `apply`, `pop`, `drop`\n"
            "• `git stash -u` untracked fayllar bilan\n"
            "• `git stash branch` — stash'dan yangi branch\n"
            "• `git cherry-pick` bitta commit\n"
            "• `git cherry-pick` bir nechta\n"
            "• Cherry-pick conflict yechish (--continue)\n"
            "• `git commit --amend` xabar tahrirlash\n"
            "• `git commit --amend` yangi fayl qo'shish (--no-edit)\n"
            "• Push qilingan commit'da amend xavfi — tushuntirish\n"
            "• Kamida 6 ta foydali alias yaratish"
        ),
        "technologies": "Git, stash, cherry-pick, amend, aliases",
        "deadline_days": 4,
    },
    9: {
        "title": "Rebase va interactive rebase laboratoriyasi",
        "description": "Merge vs Rebase'ni amaliy taqqoslash va interactive rebase bilan tarix tozalash.",
        "requirements": (
            "• Bir xil senariyni avval merge bilan, keyin rebase bilan hal qilish\n"
            "• Tarix grafiklarini taqqoslash (`--graph --all`)\n"
            "• Rebase conflict yechish (`--continue`, `--abort`)\n"
            "• Interactive rebase: 3 ta commit'ni squash bilan 1 ga\n"
            "• Interactive rebase: reword (xabar tuzatish)\n"
            "• Interactive rebase: drop (commit o'chirish)\n"
            "• Interactive rebase: reorder (qatorlar)\n"
            "• `git pull --rebase` ishlatish\n"
            "• `git push --force-with-lease` xavfsiz versiya\n"
            "• Push qilingan commit'da rebase xavfi — hisobot\n"
            "• Kunlik workflow yozilgan dokument"
        ),
        "technologies": "Git, rebase, interactive rebase, squash, force-with-lease",
        "deadline_days": 5,
    },
    10: {
        "title": "Reset, revert, reflog amaliyot",
        "description": "3 ta recovery vositasini har xil senariylarda sinash.",
        "requirements": (
            "• `git reset --soft` misoli (commit ochish)\n"
            "• `git reset --mixed` misoli (default)\n"
            "• `git reset --hard` xavfli misol + reflog bilan qutqarish\n"
            "• `git revert` bitta commit\n"
            "• `git revert` bir nechta commit\n"
            "• `git reflog` bilan tarix kuzatish\n"
            "• Reflog SHA dan branch yaratish\n"
            "• Detached HEAD'dan chiqish\n"
            "• `git clean -fd` kuzatilmayotgan fayllarni o'chirish\n"
            "• Hisobot: qachon reset, qachon revert"
        ),
        "technologies": "Git, reset, revert, reflog, clean, recovery",
        "deadline_days": 4,
    },
    11: {  # R3
        "title": "🔁 R3: Yo'qotilgan kodni qutqarish laboratoriyasi",
        "description": (
            "Modul 3 takrorlash: 5+ ta katastrofa senariyni simulyatsiya va qutqarish."
        ),
        "requirements": (
            "• Senariy 1: branch o'chirish + reflog bilan qaytarish\n"
            "• Senariy 2: reset --hard + reflog bilan qaytarish\n"
            "• Senariy 3: push qilingan yomon commit + revert bilan bekor\n"
            "• Senariy 4: wrong branch'da commit + reset main'da + branch yaratish\n"
            "• Senariy 5: detached HEAD'da ish + branch yaratish reflog'dan\n"
            "• Bonus senariy 6: rebase --abort bilan bekor qilish\n"
            "• Bonus senariy 7: git fsck --lost-found ishlatish\n"
            "• Yakuniy hisobot: har senariy uchun (Nima qildim → Nima bo'ldi → Qanday qutqardim → Olganlar)\n"
            "• Eng katta saboq: panika qilmaslik tushuntirish"
        ),
        "technologies": "Git, reset, revert, reflog, recovery scenarios",
        "deadline_days": 5,
    },
    12: {
        "title": "Tag, Release, GitHub Actions sozlash",
        "description": "Loyihada professional CI/CD va release jarayoni.",
        "requirements": (
            "• 2 ta tag (lightweight va annotated)\n"
            "• Tag'larni push qilish (--tags)\n"
            "• GitHub Release sahifa changelog bilan\n"
            "• `gh release create` CLI bilan\n"
            "• `.github/workflows/test.yml` — push/PR'da test\n"
            "• Matrix builds (kamida 2 ta Python yoki Node versiya)\n"
            "• `.github/workflows/deploy.yml` — main'ga merge'da deploy (yoki simulyatsiya)\n"
            "• Secrets sozlash (kamida 1 ta)\n"
            "• README'da status badge\n"
            "• Scheduled workflow misoli (cron)\n"
            "• YAML indentatsiya xato tahlili (2 vs 4)"
        ),
        "technologies": "Git, tags, semver, GitHub Releases, GitHub Actions, YAML, CI/CD",
        "deadline_days": 6,
    },
    13: {  # L11 — CAPSTONE
        "title": "🚀 CAPSTONE: Jamoaviy loyiha workflow",
        "description": (
            "Kursning yakuniy loyihasi: 2-4 odamlik jamoa bilan kichik real loyihani "
            "professional GitHub workflow bilan amalga oshirish. 2 hafta."
        ),
        "requirements": (
            "Repo va dokumentatsiya:\n"
            "• Public GitHub repo + chiroyli README\n"
            "• Mos .gitignore + LICENSE (MIT)\n"
            "• CONTRIBUTING.md\n"
            "• PR va Issue template'lari\n"
            "\n"
            "Issue va project management:\n"
            "• 10+ ta issue (label'lar bilan)\n"
            "• Milestone (v1.0.0)\n"
            "• Project board (Kanban)\n"
            "• Issue'lar jamoadoshlarga assign\n"
            "\n"
            "Branch va PR:\n"
            "• Branch protection rules main'da\n"
            "• `feature/...`, `fix/...` branchlar\n"
            "• Conventional Commits\n"
            "• Har PR bitta issue'ga bog'langan (Closes #N)\n"
            "• Kamida 1 ta merge conflict yechilgan\n"
            "• Kamida 1 ta code review siklasi (siz boshqalarning kodini)\n"
            "\n"
            "CI/CD:\n"
            "• GitHub Actions: test workflow\n"
            "• Lint check, build check\n"
            "• Status badge README'da\n"
            "• (Bonus) Auto-deploy\n"
            "\n"
            "Release:\n"
            "• Tag v1.0.0 (annotated)\n"
            "• GitHub Release sahifa changelog bilan\n"
            "• Live demo URL (Vercel/Netlify/Railway)\n"
            "\n"
            "Jamoa:\n"
            "• 2-4 jamoadosh\n"
            "• Har biridan kamida 5 ta commit\n"
            "• Balanced contributions (GitHub Insights ko'rsatadi)\n"
            "• Issue diskussiyalari (kamida 3 ta comment exchange)\n"
            "\n"
            "Yakuniy yetkazib berish:\n"
            "• GitHub repo URL\n"
            "• Live demo URL\n"
            "• Release v1.0.0 link\n"
            "• 5 daqiqalik demo video (ixtiyoriy)\n"
            "• Retrospective hisobot"
        ),
        "technologies": (
            "Git, GitHub, branches, PR, review, conflict resolution, CI/CD, "
            "GitHub Actions, releases, project management, team collaboration"
        ),
        "deadline_days": 14,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {"order": 0,  "title": "1-Git nima va birinchi repo (init, add, commit)",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/RGOj5yH7evk", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-.gitignore, log, diff — tarix bilan ishlash",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/HVsySz-h9r4", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-Branching: branch, switch, merge",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/QV0kVNvkMxc", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Shaxsiy kunlik commit jurnal (takrorlash)",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/8JJ101D3knE", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-GitHub, SSH, remote — birinchi push",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/nhNq2kIvi9s", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-Pull Request lifecycle (fork, branch, PR)",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/8lGpZkjnkt4", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-Merge conflict — qanday yechish",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/Sqsz1-o7nXk", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-Open source repo'ga real PR (takrorlash)",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/dSl_qnWO104", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-Stash, cherry-pick, amend — kunlik qurollar",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/KLEDKgMmbBI", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-Rebase vs Merge — qachon qaysini",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/0chZFIZLR_0", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-Reset, revert, reflog — qutqarish texnikalari",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/Y-EQf7OkPP8", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Yo'qotilgan kodni qutqarish (takrorlash)",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/iLOl3Y_BACA", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Tag, release, GitHub Actions (CI/CD intro)",
     "text": None, "code": None, "lang": "yaml",
     "video": "https://youtu.be/R8_veQiYBjI", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: Jamoaviy loyiha workflow",
     "text": None, "code": None, "lang": "bash",
     "video": "https://youtu.be/3a8KsB5wJDE", "exercises": L11_EX, "_ref": "L11"},
]


def _resolve_lessons() -> None:
    g = globals()
    for row in LESSONS:
        ref = row["_ref"]
        row["text"] = g[f"{ref}_TEXT"]
        row["code"] = g[f"{ref}_CODE"]


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(lesson: dict, exercise_rows: list[Exercise]) -> str:
    sections = [
        {"id": f"t{lesson['order']}", "type": "text", "label": "Текст",
         "html": lesson["text"], "order": 0},
        {"id": f"c{lesson['order']}", "type": "code", "label": "Код",
         "code": lesson["code"], "lang": lesson["lang"], "order": 1},
        {"id": f"v{lesson['order']}", "type": "video", "label": "Видео",
         "videoUrl": lesson["video"], "order": 2},
        {"id": f"e{lesson['order']}", "type": "exercise", "label": "Упражнения",
         "exercises": [
             {
                 "_localId": e.id, "id": e.id,
                 "title": e.title, "description": e.description,
                 "exercise_type": e.exercise_type,
                 "options": e.options or "",
                 "correct_answers": e.correct_answers or "",
                 "drag_items": e.drag_items or "",
                 "correct_order": e.correct_order or "",
                 "is_multiple_select": bool(e.is_multiple_select),
                 "expected_answer": e.expected_answer or "",
                 "hint": e.hint or "",
                 "explanation": e.explanation or "",
                 "difficulty_level": e.difficulty_level,
                 "points": e.points, "order": e.order,
             }
             for e in exercise_rows
         ],
         "order": 3},
    ]
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    _resolve_lessons()

    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if existing:
            print(f"Course '{COURSE['title']}' already exists (id={existing.id}). "
                  f"Delete it first if you want to re-seed.")
            return

        course = Course(**COURSE)
        db.add(course)
        await db.flush()
        print(f"Created course: id={course.id}  title='{course.title}'")

        for ldata in LESSONS:
            task = LESSON_TASKS.get(ldata["order"], {})
            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=10,
                text_content=ldata["text"],
                code_content=ldata["code"],
                code_language=ldata["lang"],
                video_url=ldata["video"],
                sections_json=None,
                task_title=task.get("title"),
                task_description=task.get("description"),
                task_requirements=task.get("requirements"),
                task_technologies=task.get("technologies"),
                task_deadline_days=task.get("deadline_days"),
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ldata["exercises"]):
                row = Exercise(
                    lesson_id=lesson.id,
                    title=ex["title"],
                    description=ex.get("description", ex["title"]),
                    exercise_type=ex["exercise_type"],
                    options=_jdump(ex.get("options")),
                    correct_answers=_jdump(ex.get("correct_answers")),
                    drag_items=_jdump(ex.get("drag_items")),
                    correct_order=_jdump(ex.get("correct_order")),
                    is_multiple_select=bool(ex.get("is_multiple_select", False)),
                    expected_answer=ex.get("expected_answer", ""),
                    hint=ex.get("hint", ""),
                    explanation=ex.get("explanation", ""),
                    difficulty_level=ex["difficulty_level"],
                    points=ex["points"],
                    order=ex_order,
                    is_active=True,
                )
                db.add(row)
                ex_rows.append(row)
            await db.flush()

            lesson.sections_json = build_sections_json(ldata, ex_rows)
            print(f"  lesson order={lesson.order:>2} id={lesson.id:>3}  "
                  f"{lesson.title:<55}  exercises={len(ex_rows)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded course '{COURSE['title']}' with "
                  f"{len(LESSONS)} lessons and "
                  f"{sum(len(l['exercises']) for l in LESSONS)} exercises.")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
