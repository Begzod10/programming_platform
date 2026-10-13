"""Course spec: Linux va terminal asoslari — 6 lessons, UZ + RU.

Every command in the lessons was run in a real Linux shell: a Debian 13 container (Docker) as an ordinary
user "student" (root would ignore file permissions), against the practice folder ~/lab that LAB_SETUP creates.
The TRANSCRIPT_* constants are the captured terminal sessions ("$ command" followed by its output) of those
runs. Two things differ on a real machine and the lessons say so: the sort order of `ls` / `find` depends on
the locale and the file system, and dates such as the backup file name change from day to day.
What could NOT be run here and is written without output: `sudo`, `systemctl`/`journalctl` (the container has
no systemd; the same two read-only forms were run on a real Ubuntu server), `ssh`/`scp` to a remote host,
and `crontab`. API messages are English so the code is identical in UZ and RU.
"""
from __future__ import annotations

# ── Verified artefacts (single source of truth for lessons 1-6) ──────────────

LAB_SETUP = r'''#!/usr/bin/env bash
# Creates the practice folder ~/lab used by every lesson of the course.
set -euo pipefail

mkdir -p ~/lab/projects/shop/{src,tests,docs} ~/lab/logs
cd ~/lab

printf 'milk\nbread\neggs\nbread\ntea\n' > shopping.txt
printf 'print("hello from shop")\n' > projects/shop/src/main.py
printf 'def test_ok():\n    assert True\n' > projects/shop/tests/test_main.py
printf '# Shop\nA tiny practice project.\n' > projects/shop/README.md
printf 'DEBUG=true\nPORT=8000\n' > projects/shop/.env
printf 'Deploy notes\n============\nrestart the service after every release\n' > projects/shop/docs/deploy.txt

# 70 access-log lines in the nginx style; the numbers are computed, so everybody gets the same file
paths=(/api/notes /api/login /api/notes /api/register /health /api/notes /missing)
codes=(200 200 200 201 200 200 404)
for i in $(seq 0 69); do
  path=${paths[$((i % 7))]}
  code=${codes[$((i % 7))]}
  if (( i % 2 == 0 )) && [[ $path == /api/login ]]; then code=500; fi
  printf '10.0.0.%d - - [13/Oct/2026:10:%02d:%02d +0000] "GET %s HTTP/1.1" %s %d\n' \
    $((i % 5 + 1)) $((i / 60)) $((i % 60)) "$path" "$code" $((100 + i * 7))
done > logs/access.log

# one fixed timestamp for everything, so `ls -l` looks the same for every student
find ~/lab -exec touch -d "2026-10-01 10:00" {} +
echo "lab is ready: $(find ~/lab -type f | wc -l) files"
'''

LOGREPORT_SH = r'''#!/usr/bin/env bash
# Usage: ./logreport.sh <access.log>
# Prints a short report. Exit codes: 0 all good, 1 file missing, 2 wrong usage, 3 the log contains 5xx errors.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <access.log>" >&2
  exit 2
fi

log=$1
if [[ ! -f $log ]]; then
  echo "error: $log not found" >&2
  exit 1
fi

total=$(wc -l < "$log")
errors=$(grep -c ' 5[0-9][0-9] ' "$log" || true)

echo "requests: $total"
echo "server errors (5xx): $errors"
echo "by status:"
awk '{print $9}' "$log" | sort | uniq -c | sort -rn | sed 's/^/  /'
echo "top paths:"
awk '{print $7}' "$log" | sort | uniq -c | sort -rn | head -3 | sed 's/^/  /'

if (( errors > 0 )); then
  exit 3
fi
'''

BACKUP_SH = r'''#!/usr/bin/env bash
# Usage: ./backup.sh <folder> <destination-folder>
set -euo pipefail

source_dir=${1:?usage: $0 <folder> <destination-folder>}
dest_dir=${2:?usage: $0 <folder> <destination-folder>}

mkdir -p "$dest_dir"
archive="$dest_dir/$(basename "$source_dir")-$(date +%F).tar.gz"

tar -czf "$archive" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
echo "created $archive ($(du -h "$archive" | cut -f1))"
tar -tzf "$archive" | head -5
'''

TRANSCRIPT_L1 = r'''$ pwd
/home/student
$ whoami
student
$ ls
lab
$ ls -l
total 4
drwxr-xr-x 4 student student 4096 Oct  1 10:00 lab
$ ls -a
.
..
.bash_logout
.bashrc
.profile
lab
$ cd lab
$ pwd
/home/student/lab
$ ls
logs
projects
shopping.txt
$ ls projects/shop
README.md
docs
src
tests
$ cd projects/shop/src
$ pwd
/home/student/lab/projects/shop/src
$ cd ..
$ pwd
/home/student/lab/projects/shop
$ cd ../..
$ pwd
/home/student/lab
$ cd ~
$ pwd
/home/student
$ cd /tmp
$ pwd
/tmp
$ cd -
/home/student
$ echo $HOME
/home/student
$ ls ~/lab/projects/shop
README.md
docs
src
tests
$ ls -a ~/lab/projects/shop
.
..
.env
README.md
docs
src
tests
'''

TRANSCRIPT_L2 = r'''$ cd ~/lab
$ cat shopping.txt
milk
bread
eggs
bread
tea
$ head -n 2 shopping.txt
milk
bread
$ tail -n 2 shopping.txt
bread
tea
$ wc -l shopping.txt
5 shopping.txt
$ mkdir -p backup/2026
$ cp shopping.txt backup/shopping.bak
$ cp -r projects/shop backup/shop-copy
$ ls backup
2026
shop-copy
shopping.bak
$ mv shopping.txt groceries.txt
$ ls
backup
groceries.txt
logs
projects
$ rm groceries.txt
$ rm -r backup/shop-copy
$ ls backup
2026
shopping.bak
$ ls projects/shop/*.md
projects/shop/README.md
$ ls projects/shop/src/*.p?
projects/shop/src/main.py
$ ls --help | head -3
Usage: ls [OPTION]... [FILE]...
List information about the FILEs (the current directory by default).
Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.
$ rm nothing.txt
rm: cannot remove 'nothing.txt': No such file or directory
$ rm -r backup
$ ls
logs
projects
'''

TRANSCRIPT_L3 = r'''$ cd ~/lab/logs
$ wc -l access.log
70 access.log
$ head -n 2 access.log
10.0.0.1 - - [13/Oct/2026:10:00:00 +0000] "GET /api/notes HTTP/1.1" 200 100
10.0.0.2 - - [13/Oct/2026:10:00:01 +0000] "GET /api/login HTTP/1.1" 200 107
$ grep -c ' 404 ' access.log
10
$ grep ' 500 ' access.log | head -n 2
10.0.0.4 - - [13/Oct/2026:10:00:08 +0000] "GET /api/login HTTP/1.1" 500 156
10.0.0.3 - - [13/Oct/2026:10:00:22 +0000] "GET /api/login HTTP/1.1" 500 254
$ grep -n 'register' access.log | head -n 2
4:10.0.0.4 - - [13/Oct/2026:10:00:03 +0000] "GET /api/register HTTP/1.1" 201 121
11:10.0.0.1 - - [13/Oct/2026:10:00:10 +0000] "GET /api/register HTTP/1.1" 201 170
$ grep -v ' 200 ' access.log | wc -l
25
$ grep -i 'NOTES' access.log | wc -l
30
$ awk '{print $9}' access.log | sort | uniq -c | sort -rn
     45 200
     10 404
     10 201
      5 500
$ awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -n 3
     30 /api/notes
     10 /missing
     10 /health
$ awk '$9 == 500 {print $1}' access.log | sort -u
10.0.0.1
10.0.0.2
10.0.0.3
10.0.0.4
10.0.0.5
$ cut -d' ' -f1 access.log | sort | uniq -c
     14 10.0.0.1
     14 10.0.0.2
     14 10.0.0.3
     14 10.0.0.4
     14 10.0.0.5
$ echo "report" > /tmp/report.txt
$ echo "line two" >> /tmp/report.txt
$ cat /tmp/report.txt
report
line two
$ ls /nonexistent 2> errors.txt
$ cat errors.txt
ls: cannot access '/nonexistent': No such file or directory
$ find ~/lab -name '*.py'
/home/student/lab/projects/shop/src/main.py
/home/student/lab/projects/shop/tests/test_main.py
$ find ~/lab -type d
/home/student/lab
/home/student/lab/projects
/home/student/lab/projects/shop
/home/student/lab/projects/shop/docs
/home/student/lab/projects/shop/src
/home/student/lab/projects/shop/tests
/home/student/lab/logs
$ find ~/lab -name '*.txt' -type f
/home/student/lab/projects/shop/docs/deploy.txt
/home/student/lab/logs/errors.txt
/home/student/lab/shopping.txt
$ grep -rn 'hello' ~/lab/projects
/home/student/lab/projects/shop/src/main.py:1:print("hello from shop")
$ find ~/lab -name '*.py' | xargs wc -l
 1 /home/student/lab/projects/shop/src/main.py
 2 /home/student/lab/projects/shop/tests/test_main.py
 3 total
$ tr 'a-z' 'A-Z' < ~/lab/shopping.txt | head -n 2
MILK
BREAD
$ sort ~/lab/shopping.txt | uniq -d
bread
'''

TRANSCRIPT_L4 = r'''$ cd ~/lab
$ ls -l projects/shop
total 16
-rw-r--r-- 1 student student   32 Oct  1 10:00 README.md
drwxr-xr-x 2 student student 4096 Oct  1 10:00 docs
drwxr-xr-x 2 student student 4096 Oct  1 10:00 src
drwxr-xr-x 2 student student 4096 Oct  1 10:00 tests
$ ls -l shopping.txt
-rw-r--r-- 1 student student 26 Oct  1 10:00 shopping.txt
$ printf '#!/usr/bin/env bash\necho "hello from a script"\n' > hello.sh
$ ls -l hello.sh
-rw-r--r-- 1 student student 47 Oct 13 15:29 hello.sh
$ ./hello.sh
bash: ./hello.sh: Permission denied
$ chmod +x hello.sh
$ ls -l hello.sh
-rwxr-xr-x 1 student student 47 Oct 13 15:29 hello.sh
$ ./hello.sh
hello from a script
$ chmod 600 projects/shop/.env
$ ls -l projects/shop/.env
-rw------- 1 student student 21 Oct  1 10:00 projects/shop/.env
$ chmod u+rwx,g+rx,o-rwx hello.sh
$ stat -c '%A %a %U:%G %n' hello.sh projects/shop/.env
-rwxr-x--- 750 student:student hello.sh
-rw------- 600 student:student projects/shop/.env
$ chmod 644 hello.sh
$ ./hello.sh
bash: ./hello.sh: Permission denied
$ chmod 755 hello.sh
$ id
uid=1000(student) gid=1000(student) groups=1000(student)
$ umask
0022
$ touch newfile.txt
$ stat -c '%A %a' newfile.txt
-rw-r--r-- 644
$ chown root hello.sh
chown: changing ownership of 'hello.sh': Operation not permitted
$ echo "$PATH"
/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
$ mkdir -p ~/bin
$ cp hello.sh ~/bin/hello
$ export PATH="$HOME/bin:$PATH"
$ hello
hello from a script
$ which hello
/home/student/bin/hello
$ type cd
cd is a shell builtin
'''

TRANSCRIPT_L5 = r'''$ sleep 300 &
$ pid=$!
$ ps -p "$pid" -o pid,stat,comm
    PID STAT COMMAND
     15 S    sleep
$ kill "$pid"
$ wait "$pid" 2>/dev/null; echo "exit code: $?"
exit code: 143
$ ps -p "$pid" -o pid,comm || echo "process $pid is gone"
    PID COMMAND
process 15 is gone
$ python3 -m http.server 8000 --directory ~/lab >/dev/null 2>&1 &
$ server=$!
$ sleep 1
$ curl -s localhost:8000/shopping.txt
milk
bread
eggs
bread
tea
$ curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/nothing
404
$ ss -ltn | grep 8000 | awk '{print $1, $4}'
LISTEN 0.0.0.0:8000
$ kill "$server"
$ wait "$server" 2>/dev/null; true
$ du -sh ~/lab
60K	/home/student/lab
$ du -sh ~/lab/* | sort -h
4.0K	/home/student/lab/shopping.txt
12K	/home/student/lab/logs
40K	/home/student/lab/projects
$ export APP_ENV=production
$ echo "$APP_ENV"
production
$ env | grep APP_ENV
APP_ENV=production
$ bash -c 'echo "child sees: $APP_ENV"'
child sees: production
$ APP_ENV=test bash -c 'echo "one-off: $APP_ENV"'
one-off: test
$ echo "$APP_ENV"
production
$ mkdir -p ~/.ssh
$ ssh-keygen -t ed25519 -C "student@example.com" -f ~/.ssh/id_ed25519 -N "" -q
$ ls -l ~/.ssh
total 8
-rw------- 1 student student 411 Oct 13 15:29 id_ed25519
-rw-r--r-- 1 student student 101 Oct 13 15:29 id_ed25519.pub
$ cut -d' ' -f1 ~/.ssh/id_ed25519.pub
ssh-ed25519
$ cut -d' ' -f3 ~/.ssh/id_ed25519.pub
student@example.com
$ free -h | head -n 1
               total        used        free      shared  buff/cache   available
$ df -h / | head -n 1
Filesystem      Size  Used Avail Use% Mounted on
$ uptime >/dev/null && echo "uptime works"
uptime works
'''

TRANSCRIPT_L6 = r'''$ cd ~/lab
$ cp ~/scripts/logreport.sh ~/scripts/backup.sh .
$ chmod +x logreport.sh backup.sh
$ ./logreport.sh logs/access.log
requests: 70
server errors (5xx): 5
by status:
       45 200
       10 404
       10 201
        5 500
top paths:
       30 /api/notes
       10 /missing
       10 /health
$ echo "exit code: $?"
exit code: 3
$ ./logreport.sh
usage: ./logreport.sh <access.log>
$ echo "exit code: $?"
exit code: 2
$ ./logreport.sh missing.log
error: missing.log not found
$ echo "exit code: $?"
exit code: 1
$ grep -v ' 500 ' logs/access.log > logs/clean.log
$ ./logreport.sh logs/clean.log > /dev/null
$ echo "exit code: $?"
exit code: 0
$ ./backup.sh projects/shop /tmp/backups
created /tmp/backups/shop-2026-10-13.tar.gz (4.0K)
shop/
shop/.env
shop/docs/
shop/docs/deploy.txt
shop/README.md
$ ./backup.sh projects/shop
./backup.sh: line 6: 2: usage: ./backup.sh <folder> <destination-folder>
$ echo "exit code: $?"
exit code: 1
$ ls /tmp/backups
shop-2026-10-13.tar.gz
$ name="Aziz"; echo "Hello, $name! You have $(wc -l < shopping.txt) items."
Hello, Aziz! You have 5 items.
$ for f in projects/shop/src/*.py projects/shop/tests/*.py; do echo "checking $f"; done
checking projects/shop/src/main.py
checking projects/shop/tests/test_main.py
$ count=3; if (( count > 2 )); then echo "more than two"; else echo "two or fewer"; fi
more than two
$ greet() { echo "hi, $1"; }; greet Ali
hi, Ali
$ false && echo "not printed"; true || echo "not printed"
$ false || echo "printed after failure"
printed after failure
$ bash -c 'set -e; echo before; false; echo after'
before
$ bash -c 'set -u; echo "$UNDEFINED_VAR"'
bash: line 1: UNDEFINED_VAR: unbound variable
$ bash -c 'set -o pipefail; false | cat; echo "pipe status: $?"'
pipe status: 1
'''

COURSE = {
    "title": "Linux va terminal asoslari",
    "title_ru": "Основы Linux и терминала",
    "description": (
        "Server va dasturchi ishining asosi bo'lgan terminalni o'rganasiz: fayl tizimi, fayl va papkalar, qidirish va quvurlar, "
        "ruxsatlar, jarayonlar, SSH va bash skriptlar. Barcha buyruqlar haqiqiy Linux'da sinalgan. "
        "Kurs oxirida loglarni tahlil qiladigan va zaxira nusxa yaratadigan o'z skriptingizni yozasiz."
    ),
    "description_ru": (
        "Вы изучите терминал — основу работы сервера и разработчика: файловую систему, файлы и папки, поиск и конвейеры, "
        "права доступа, процессы, SSH и bash-скрипты. Все команды проверены в настоящем Linux. "
        "В конце курса вы напишете собственный скрипт, который анализирует логи и делает резервную копию."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 2,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 11,
    "prerequisite_course_id": 45,
    "display_order": 604,
    "is_active": True,
    "is_published": False,
}


def _esc(code: str) -> str:
    return code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fill(text: str, **blocks: str) -> str:
    for key, code in blocks.items():
        text = text.replace(f"__{key}__", _esc(code))
    return text


CMD_RUN_SETUP = '''bash lab_setup.sh
cd ~
'''

CMD_SYSTEMD = '''systemctl is-active nginx
systemctl status nginx
sudo systemctl restart nginx
journalctl -u nginx -n 20 --no-pager
'''

CMD_SSH = '''ssh student@203.0.113.10
ssh-copy-id student@203.0.113.10
scp report.txt student@203.0.113.10:/tmp/
ssh student@203.0.113.10 'uptime'
'''

SSH_CONFIG = '''Host myserver
    HostName 203.0.113.10
    User student
    IdentityFile ~/.ssh/id_ed25519
'''

CRON_LINE = '''# minute hour day-of-month month day-of-week  command
0 3 * * * /home/student/lab/backup.sh /home/student/lab/projects/shop /home/student/backups
'''

CMD_CRON = '''crontab -e
crontab -l
'''


# ── 1-dars: terminal va fayl tizimi ──────────────────────────────────────────

_L1_TEXT_UZ = """<h3>Nega terminal</h3>
<p>Dasturlashda va serverda ishlaganda siz ko'pincha tugmalar emas, <strong>buyruqlar</strong> yozasiz. Serverlarning aksariyatida grafik interfeys umuman yo'q, faqat terminal bor. Buyruqlar tez, takrorlanadigan ishni <em>skript</em>ga yig'ish mumkin va ular deyarli har bir Linux serverida bir xil ishlaydi. Server production'da ishlayotgan Linux (Ubuntu yoki Debian) bo'lgani uchun bu kursdagi barcha buyruqlar <strong>haqiqiy Linux'da sinalgan</strong>.</p>
<ul>
  <li><strong>Linux</strong>: to'g'ridan-to'g'ri ishlaydi (Ubuntu, Debian va boshqalar).</li>
  <li><strong>macOS</strong>: terminal bor, buyruqlarning ko'pi bir xil, lekin ba'zilarining flaglari farq qiladi (masalan, <code>sed -i</code>, <code>stat</code>, <code>date</code>), chunki macOS BSD oilasidan.</li>
  <li><strong>Windows</strong>: WSL (Windows Subsystem for Linux) orqali Ubuntu o'rnating va u yerda ishlang.</li>
</ul>
<p><strong>Terminal</strong> — buyruq yoziladigan oyna. <strong>Shell</strong> (bizda <code>bash</code>) — yozgan buyrug'ingizni tushunib bajaradigan dastur. Buyruq qatoridagi <code>student@host:~$</code> belgisi (<em>prompt</em>) «kim@qaysi-kompyuter:qaysi-papka$» degani: <code>~</code> — uy papkangiz, <code>$</code> — oddiy foydalanuvchi (administrator uchun <code>#</code> bo'ladi).</p>

<h3>Mashq papkasini tayyorlash</h3>
<p>Butun kurs davomida bitta mashq papkasi — <code>~/lab</code> bilan ishlaymiz. Uni quyidagi skript yaratadi (6-darsda uning o'zini ham tushunib olasiz). Fayl sifatida <code>lab_setup.sh</code> nomi bilan saqlang va ishga tushiring:</p>
<pre><code>__SETUP__</code></pre>
<pre><code>__RUNSETUP__</code></pre>
<p>Skript <code>~/lab</code> ichida kichik loyiha (<code>projects/shop</code>), xarid ro'yxati (<code>shopping.txt</code>) va veb-server logi (<code>logs/access.log</code>, 70 qator) yaratadi.</p>

<h3>Fayl tizimi daraxti</h3>
<p>Linux'da <code>C:</code> yoki <code>D:</code> disklari yo'q: hamma narsa bitta daraxt, uning ildizi <code>/</code>. Qurilmalar ham daraxtning biror papkasiga «ulanadi».</p>
<pre class="mermaid">
flowchart TD
  R["/ (ildiz)"] --> H["/home: foydalanuvchi papkalari"]
  R --> E["/etc: sozlama fayllari"]
  R --> V["/var: o'zgaruvchan ma'lumot (/var/log: loglar)"]
  R --> U["/usr/bin: dasturlar"]
  R --> T["/tmp: vaqtinchalik fayllar"]
  H --> S["/home/student (~): sizning papkangiz"]
  S --> L["~/lab: mashq papkasi"]
</pre>
<p>Dasturchi uchun eng muhimlari: <code>/home/&lt;ism&gt;</code> (sizning fayllaringiz), <code>/etc</code> (sozlamalar, masalan, nginx), <code>/var/log</code> (loglar), <code>/tmp</code> (vaqtincha, tizim qayta yuklanganda tozalanishi mumkin).</p>

<h3>Yo'l: absolyut va nisbiy</h3>
<ul>
  <li><strong>Absolyut yo'l</strong> <code>/</code> dan boshlanadi va qayerda turishingizdan qat'i nazar bir xil joyni ko'rsatadi: <code>/home/student/lab/shopping.txt</code>.</li>
  <li><strong>Nisbiy yo'l</strong> joriy papkadan hisoblanadi: <code>projects/shop</code>.</li>
  <li>Maxsus belgilar: <code>.</code> — joriy papka, <code>..</code> — bitta yuqori papka, <code>~</code> — uy papkangiz, <code>-</code> (<code>cd -</code> da) — oldingi papka.</li>
</ul>

<h3>Birinchi buyruqlar</h3>
<p>Quyida haqiqiy sessiya: <code>$</code> dan keyin yozilgan buyruq, uning tagida natija.</p>
<pre><code>__TRANSCRIPT__</code></pre>
<ul>
  <li><code>pwd</code> — qayerdaman (print working directory), <code>whoami</code> — kim sifatida kirganman.</li>
  <li><code>ls</code> — papka ichidagilar. <code>ls -l</code> — batafsil ro'yxat (ruxsatlar, egasi, hajmi, sanasi), <code>ls -a</code> — <em>yashirin</em> fayllar bilan. Nuqta bilan boshlanadigan fayl yashirin: <code>.env</code>, <code>.bashrc</code>.</li>
  <li><code>cd papka</code> — papkaga o'tish. <code>cd</code> yolg'iz o'zi yoki <code>cd ~</code> uyga qaytaradi; <code>cd ..</code> — bitta yuqoriga; <code>cd -</code> — oldingi joyga qaytaradi va uni yozib qo'yadi.</li>
</ul>
<p>Eslatmalar: natija chiqishi fayl tizimi va tilingizga qarab biroz farq qilishi mumkin: <code>ls</code> tartibi (bosh harflar oldin yoki aralash) va sanalar sizda boshqacha bo'ladi. Terminalda <code>ls</code> nomlarni ustunlarga joylaydi, bu yerda esa har nom alohida qatorda ko'rsatilgan.</p>

<h3>Terminalni tez ishlatish</h3>
<ul>
  <li><strong>Tab</strong> — nomni avtomatik to'ldiradi (<code>cd pro</code> + Tab → <code>cd projects/</code>). Eng foydali odat.</li>
  <li><strong>↑ / ↓</strong> — oldingi buyruqlar tarixi; <strong>Ctrl+R</strong> — tarixdan qidirish.</li>
  <li><strong>Ctrl+C</strong> — ishlayotgan buyruqni to'xtatish; <strong>Ctrl+L</strong> (yoki <code>clear</code>) — ekranni tozalash.</li>
</ul>"""

_L1_TEXT_RU = """<h3>Зачем нужен терминал</h3>
<p>В программировании и при работе с сервером вы часто не нажимаете кнопки, а вводите <strong>команды</strong>. На большинстве серверов графического интерфейса вообще нет, только терминал. Команды быстрые, повторяющуюся работу можно собрать в <em>скрипт</em>, и они почти одинаково работают на любом Linux-сервере. Поскольку сервер в production — это Linux (Ubuntu или Debian), все команды этого курса <strong>проверены в настоящем Linux</strong>.</p>
<ul>
  <li><strong>Linux</strong>: работает напрямую (Ubuntu, Debian и другие).</li>
  <li><strong>macOS</strong>: терминал есть, большинство команд такие же, но у некоторых отличаются флаги (например, <code>sed -i</code>, <code>stat</code>, <code>date</code>), потому что macOS принадлежит семейству BSD.</li>
  <li><strong>Windows</strong>: установите Ubuntu через WSL (Windows Subsystem for Linux) и работайте в нём.</li>
</ul>
<p><strong>Терминал</strong> — окно, в которое вводятся команды. <strong>Shell</strong> (у нас <code>bash</code>) — программа, которая понимает и выполняет введённую команду. Значок <code>student@host:~$</code> в начале строки (<em>prompt</em>) означает «кто@на-каком-компьютере:в-какой-папке$»: <code>~</code> — ваша домашняя папка, <code>$</code> — обычный пользователь (у администратора будет <code>#</code>).</p>

<h3>Готовим папку для практики</h3>
<p>Весь курс мы работаем с одной учебной папкой — <code>~/lab</code>. Её создаёт скрипт ниже (в уроке 6 вы поймёте и сам скрипт). Сохраните его в файл <code>lab_setup.sh</code> и запустите:</p>
<pre><code>__SETUP__</code></pre>
<pre><code>__RUNSETUP__</code></pre>
<p>Скрипт создаёт в <code>~/lab</code> небольшой проект (<code>projects/shop</code>), список покупок (<code>shopping.txt</code>) и лог веб-сервера (<code>logs/access.log</code>, 70 строк).</p>

<h3>Дерево файловой системы</h3>
<p>В Linux нет дисков <code>C:</code> или <code>D:</code>: всё находится в одном дереве с корнем <code>/</code>. Устройства тоже «подключаются» к какой-нибудь папке этого дерева.</p>
<pre class="mermaid">
flowchart TD
  R["/ (корень)"] --> H["/home: папки пользователей"]
  R --> E["/etc: файлы настроек"]
  R --> V["/var: изменяемые данные (/var/log: логи)"]
  R --> U["/usr/bin: программы"]
  R --> T["/tmp: временные файлы"]
  H --> S["/home/student (~): ваша папка"]
  S --> L["~/lab: учебная папка"]
</pre>
<p>Самое важное для разработчика: <code>/home/&lt;имя&gt;</code> (ваши файлы), <code>/etc</code> (настройки, например nginx), <code>/var/log</code> (логи), <code>/tmp</code> (временное, может очищаться при перезагрузке).</p>

<h3>Путь: абсолютный и относительный</h3>
<ul>
  <li><strong>Абсолютный путь</strong> начинается с <code>/</code> и всегда указывает на одно и то же место, где бы вы ни находились: <code>/home/student/lab/shopping.txt</code>.</li>
  <li><strong>Относительный путь</strong> отсчитывается от текущей папки: <code>projects/shop</code>.</li>
  <li>Специальные обозначения: <code>.</code> — текущая папка, <code>..</code> — папка на уровень выше, <code>~</code> — ваша домашняя папка, <code>-</code> (в <code>cd -</code>) — предыдущая папка.</li>
</ul>

<h3>Первые команды</h3>
<p>Ниже настоящая сессия: после <code>$</code> записана команда, а под ней — результат.</p>
<pre><code>__TRANSCRIPT__</code></pre>
<ul>
  <li><code>pwd</code> — где я (print working directory), <code>whoami</code> — под кем я вошёл.</li>
  <li><code>ls</code> — содержимое папки. <code>ls -l</code> — подробный список (права, владелец, размер, дата), <code>ls -a</code> — вместе со <em>скрытыми</em> файлами. Файл, имя которого начинается с точки, скрытый: <code>.env</code>, <code>.bashrc</code>.</li>
  <li><code>cd папка</code> — перейти в папку. <code>cd</code> без аргументов или <code>cd ~</code> возвращает домой; <code>cd ..</code> — на уровень выше; <code>cd -</code> — возвращает на прежнее место и показывает его.</li>
</ul>
<p>Примечания: вывод может немного отличаться в зависимости от файловой системы и языка: порядок в <code>ls</code> (заглавные буквы сначала или вперемешку) и даты у вас будут другими. В терминале <code>ls</code> раскладывает имена по столбцам, а здесь каждое имя показано на отдельной строке.</p>

<h3>Как работать в терминале быстрее</h3>
<ul>
  <li><strong>Tab</strong> — автодополнение имени (<code>cd pro</code> + Tab → <code>cd projects/</code>). Самая полезная привычка.</li>
  <li><strong>↑ / ↓</strong> — история команд; <strong>Ctrl+R</strong> — поиск по истории.</li>
  <li><strong>Ctrl+C</strong> — остановить выполняющуюся команду; <strong>Ctrl+L</strong> (или <code>clear</code>) — очистить экран.</li>
</ul>"""

_L1_BLOCKS = dict(SETUP=LAB_SETUP, RUNSETUP=CMD_RUN_SETUP, TRANSCRIPT=TRANSCRIPT_L1)

LESSON_1 = {
    "order": 0,
    "title": "1-Terminal va fayl tizimi",
    "title_ru": "1-Терминал и файловая система",
    "points_reward": 10,
    "text_content": _fill(_L1_TEXT_UZ, **_L1_BLOCKS),
    "text_content_ru": _fill(_L1_TEXT_RU, **_L1_BLOCKS),
    "code_content": TRANSCRIPT_L1,
    "code_content_ru": TRANSCRIPT_L1,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: mashq papkasi va birinchi buyruqlar",
        "title_ru": "Пример: учебная папка и первые команды",
        "description": "lab_setup.sh mashq papkasini yaratadi; pwd, ls, cd sessiyasi haqiqiy Linux'da olingan.",
        "description_ru": "lab_setup.sh создаёт учебную папку; сессия pwd, ls, cd снята в настоящем Linux.",
        "sample_type": "code",
        "code_files": [
            {"filename": "lab_setup.sh", "language": "bash", "code": LAB_SETUP},
            {"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L1},
        ],
    },
    "exercises": [
        {
            "title": "Joriy papka", "title_ru": "Текущая папка",
            "description": "Hozir qaysi papkadaman? degan savolga javob beradigan buyruq: ___",
            "description_ru": "Команда, отвечающая на вопрос «в какой папке я сейчас?»: ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "pwd",
            "hint": "«print working directory» qisqartmasi.",
            "hint_ru": "Сокращение от «print working directory».",
            "explanation": "pwd joriy ish papkasining to'liq (absolyut) yo'lini chiqaradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Uy papkasi", "title_ru": "Домашняя папка",
            "description": "Qaysi buyruq sizni istalgan joydan uy papkangizga qaytaradi?",
            "description_ru": "Какая команда возвращает вас домой из любого места?",
            "exercise_type": "multiple_choice",
            "options": ["cd ~", "cd ..", "cd /", "ls ~ -l"],
            "options_ru": ["cd ~", "cd ..", "cd /", "ls ~ -l"],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Tilda belgisi uy papkasini bildiradi.",
            "hint_ru": "Символ тильды обозначает домашнюю папку.",
            "explanation": "cd ~ (yoki yolg'iz cd) uy papkasiga qaytaradi. cd .. bitta yuqoriga, cd / esa tizim ildiziga olib boradi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Yo'l bo'ylab", "title_ru": "Путь по папкам",
            "description": "~/lab papkasidan boshlab: avval projects/shop/src ga kiring, keyin uy papkasiga qaytib, joyni tekshiring. Buyruqlarni to'g'ri tartibga soling.",
            "description_ru": "Начав в ~/lab: сначала войдите в projects/shop/src, затем вернитесь в домашнюю папку и проверьте место. Расположите команды в правильном порядке.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["cd projects/shop/src", "cd ../..", "cd ~", "pwd"],
            "drag_items_ru": ["cd projects/shop/src", "cd ../..", "cd ~", "pwd"],
            "correct_order": ["cd projects/shop/src", "cd ../..", "cd ~", "pwd"],
            "hint": "Avval chuqurga kiring, keyin yuqoriga chiqing, oxirida joyni tekshiring.",
            "hint_ru": "Сначала войдите вглубь, затем поднимитесь, в конце проверьте место.",
            "explanation": "cd projects/shop/src chuqurga kiradi, cd ../.. src dan ikki pog'ona yuqoriga, ya'ni projects papkasiga chiqaradi, cd ~ uyga qaytaradi, pwd esa natijani ko'rsatadi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Yo'llar haqida", "title_ru": "О путях",
            "description": "Yo'llar haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о путях верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Absolyut yo'l / dan boshlanadi",
                "Nuqta bilan boshlanadigan fayl yashirin hisoblanadi (masalan, .env)",
                ".. joriy papkaning o'zini bildiradi",
                "Nisbiy yo'l joriy papkaga nisbatan hisoblanadi",
            ],
            "options_ru": [
                "Абсолютный путь начинается с /",
                "Файл, имя которого начинается с точки, считается скрытым (например, .env)",
                ".. обозначает саму текущую папку",
                "Относительный путь отсчитывается от текущей папки",
            ],
            "correct_answers": "A,B,D", "is_multiple_select": True,
            "hint": "Joriy papka bitta nuqta, ikkita nuqta — undan yuqorisi.",
            "hint_ru": "Текущая папка — одна точка, две точки — папка выше.",
            "explanation": ".. bitta yuqori papkani bildiradi, joriy papka esa bitta nuqta (.). Qolgan uch gap to'g'ri.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Tab nima uchun", "title_ru": "Зачем Tab",
            "description": "Terminalda Tab tugmasi nima qiladi va nega foydali? O'z so'zingiz bilan yozing.",
            "description_ru": "Что делает клавиша Tab в терминале и почему она полезна? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Tab fayl yoki papka nomini avtomatik to'ldiradi. Bu yozishni tezlashtiradi, imlo xatolarini kamaytiradi va nom mavjudligini darhol ko'rsatadi.",
            "hint": "Uzun nomni to'liq yozmasdan nima qilasiz?",
            "hint_ru": "Что делать, чтобы не набирать длинное имя целиком?",
            "explanation": "Tab bilan avtomatik to'ldirish vaqtni tejaydi va xatolarni kamaytiradi: nom mavjud bo'lsa to'ldiriladi, bo'lmasa hech narsa o'zgarmaydi.",
            "difficulty_level": "Easy", "points": 4,
        },
    ],
}


# ── 2-dars: fayl va papkalar bilan ishlash ───────────────────────────────────

_L2_TEXT_UZ = """<h3>Faylni o'qish</h3>
<ul>
  <li><code>cat fayl</code> — butun faylni chiqaradi (kichik fayllar uchun).</li>
  <li><code>head -n 2 fayl</code> — birinchi 2 qator, <code>tail -n 2 fayl</code> — oxirgi 2 qator. Loglar uchun <code>tail -f fayl</code> faylning oxirini <em>kuzatib</em> turadi (Ctrl+C bilan to'xtatiladi).</li>
  <li><code>wc -l fayl</code> — qatorlar soni (<code>wc</code> — word count).</li>
  <li>Katta fayl uchun <code>less fayl</code>: ↑/↓ yoki bo'sh joy bilan ko'rasiz, <code>/so'z</code> bilan qidirasiz, <code>q</code> bilan chiqasiz.</li>
</ul>

<h3>Yaratish, nusxalash, ko'chirish, o'chirish</h3>
<ul>
  <li><code>mkdir papka</code> — papka yaratadi; <code>mkdir -p a/b/c</code> — oradagi papkalarni ham yaratadi va papka allaqachon bo'lsa xato bermaydi.</li>
  <li><code>touch fayl</code> — bo'sh fayl yaratadi (bor bo'lsa, sanasini yangilaydi).</li>
  <li><code>cp manba nishon</code> — nusxa. Papkani nusxalash uchun <code>-r</code> (recursive: ichidagilari bilan).</li>
  <li><code>mv manba nishon</code> — ko'chiradi <em>yoki</em> nomini o'zgartiradi: <code>mv shopping.txt groceries.txt</code> shu papkaning ichida nomini almashtiradi.</li>
  <li><code>rm fayl</code> — o'chiradi; papka uchun <code>rm -r papka</code>.</li>
</ul>
<p><strong>Ehtiyot bo'ling:</strong> Linux terminalida «axlat qutisi» yo'q. <code>rm</code> bilan o'chirilgan narsa qaytmaydi. Buyruqni Enter bilan yuborishdan oldin yo'lni yana o'qing. Ayniqsa <code>rm -rf</code> (so'ramasdan, ichkarisi bilan) xavfli: noto'g'ri yo'l butun ishingizni o'chirib yuborishi mumkin. Shubhangiz bo'lsa avval o'sha yo'l bilan <code>ls</code> qilib, nima o'chishini ko'ring.</p>

<h3>Shablon belgilar (wildcards)</h3>
<p>Shell fayl nomlarini <em>shablon</em> bo'yicha o'zi ochib beradi: <code>*</code> — istalgan belgilar (hech narsa bo'lishi ham mumkin), <code>?</code> — aynan bitta belgi. Masalan, <code>projects/shop/*.md</code> — shu papkadagi hamma <code>.md</code> fayllar, <code>src/*.p?</code> — <code>.py</code>, <code>.pl</code> kabi ikki belgili kengaytmalar.</p>

<h3>Yordam olish</h3>
<p>Buyruq flaglarini eslab qolish shart emas: <code>buyruq --help</code> qisqa yordam beradi, <code>man buyruq</code> to'liq qo'llanmani ochadi (<code>q</code> bilan chiqiladi). Xato xabarini o'qing: ular odatda sababni aniq aytadi, masalan mavjud bo'lmagan faylni o'chirishga urinish (pastdagi sessiyaga qarang).</p>

<h3>Sessiya</h3>
<p>Avval 1-darsdagi <code>lab_setup.sh</code> bilan mashq papkasini tayyorlab oling, so'ng buyruqlarni o'zingiz yozib ko'ring:</p>
<pre><code>__TRANSCRIPT__</code></pre>
<ul>
  <li><code>mkdir -p backup/2026</code> papka ichida papka yaratdi; <code>cp -r projects/shop backup/shop-copy</code> butun loyihani nusxaladi.</li>
  <li><code>mv shopping.txt groceries.txt</code> nomni o'zgartirdi; <code>ls</code> da eski nom yo'qolib, yangisi paydo bo'ldi.</li>
  <li>Oxirgi <code>rm nothing.txt</code> «No such file or directory» xabarini berdi: xato fayl nomi yoki yo'lda.</li>
  <li>Eslatma: <code>ls</code> da <code>.env</code> ko'rinmaydi (yashirin), shuning uchun <code>projects/shop/*.md</code> faqat <code>README.md</code> ni topdi.</li>
</ul>"""

_L2_TEXT_RU = """<h3>Чтение файла</h3>
<ul>
  <li><code>cat файл</code> — выводит весь файл (для небольших файлов).</li>
  <li><code>head -n 2 файл</code> — первые 2 строки, <code>tail -n 2 файл</code> — последние 2 строки. Для логов <code>tail -f файл</code> <em>следит</em> за концом файла (останавливается через Ctrl+C).</li>
  <li><code>wc -l файл</code> — количество строк (<code>wc</code> — word count).</li>
  <li>Для большого файла <code>less файл</code>: листаете стрелками ↑/↓ или пробелом, ищете через <code>/слово</code>, выходите клавишей <code>q</code>.</li>
</ul>

<h3>Создание, копирование, перемещение, удаление</h3>
<ul>
  <li><code>mkdir папка</code> — создаёт папку; <code>mkdir -p a/b/c</code> — создаёт и промежуточные папки и не выдаёт ошибку, если папка уже есть.</li>
  <li><code>touch файл</code> — создаёт пустой файл (если он есть, обновляет дату).</li>
  <li><code>cp источник назначение</code> — копия. Чтобы копировать папку, нужен <code>-r</code> (recursive: вместе с содержимым).</li>
  <li><code>mv источник назначение</code> — перемещает <em>или</em> переименовывает: <code>mv shopping.txt groceries.txt</code> переименовывает файл в той же папке.</li>
  <li><code>rm файл</code> — удаляет; для папки <code>rm -r папка</code>.</li>
</ul>
<p><strong>Осторожно:</strong> в терминале Linux нет «корзины». Удалённое через <code>rm</code> не возвращается. Перед нажатием Enter ещё раз прочитайте путь. Особенно опасен <code>rm -rf</code> (без вопросов и вместе с содержимым): неверный путь может стереть всю вашу работу. Если сомневаетесь, сначала выполните <code>ls</code> с тем же путём и посмотрите, что будет удалено.</p>

<h3>Шаблоны (wildcards)</h3>
<p>Shell сам раскрывает имена файлов по <em>шаблону</em>: <code>*</code> — любые символы (в том числе их отсутствие), <code>?</code> — ровно один символ. Например, <code>projects/shop/*.md</code> — все файлы <code>.md</code> в этой папке, <code>src/*.p?</code> — расширения из двух символов вроде <code>.py</code>, <code>.pl</code>.</p>

<h3>Как получить помощь</h3>
<p>Флаги команд запоминать не обязательно: <code>команда --help</code> выдаёт краткую справку, <code>man команда</code> открывает полное руководство (выход клавишей <code>q</code>). Читайте сообщения об ошибках: обычно они прямо называют причину, например при попытке удалить несуществующий файл (см. сессию ниже).</p>

<h3>Сессия</h3>
<p>Сначала подготовьте учебную папку скриптом <code>lab_setup.sh</code> из урока 1, затем вводите команды сами:</p>
<pre><code>__TRANSCRIPT__</code></pre>
<ul>
  <li><code>mkdir -p backup/2026</code> создал папку внутри папки; <code>cp -r projects/shop backup/shop-copy</code> скопировал весь проект.</li>
  <li><code>mv shopping.txt groceries.txt</code> переименовал файл; в <code>ls</code> старое имя исчезло, появилось новое.</li>
  <li>Последний <code>rm nothing.txt</code> выдал «No such file or directory»: ошибка в имени файла или пути.</li>
  <li>Заметьте: в <code>ls</code> не виден <code>.env</code> (скрытый), поэтому <code>projects/shop/*.md</code> нашёл только <code>README.md</code>.</li>
</ul>"""

_L2_BLOCKS = dict(TRANSCRIPT=TRANSCRIPT_L2)

LESSON_2 = {
    "order": 1,
    "title": "2-Fayl va papkalar bilan ishlash",
    "title_ru": "2-Работа с файлами и папками",
    "points_reward": 10,
    "text_content": _fill(_L2_TEXT_UZ, **_L2_BLOCKS),
    "text_content_ru": _fill(_L2_TEXT_RU, **_L2_BLOCKS),
    "code_content": TRANSCRIPT_L2,
    "code_content_ru": TRANSCRIPT_L2,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: cat, cp, mv, rm va shablonlar",
        "title_ru": "Пример: cat, cp, mv, rm и шаблоны",
        "description": "Fayl o'qish, nusxalash, nomini o'zgartirish, o'chirish va * ? shablonlari: haqiqiy Linux sessiyasi.",
        "description_ru": "Чтение, копирование, переименование, удаление файлов и шаблоны * ?: сессия в настоящем Linux.",
        "sample_type": "code",
        "code_files": [{"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L2}],
    },
    "exercises": [
        {
            "title": "Papka yaratish", "title_ru": "Создание папки",
            "description": "Oradagi papkalar mavjud bo'lmasa ham a/b/c papkasini yaratadigan buyruq: mkdir ___ a/b/c",
            "description_ru": "Команда, создающая папку a/b/c, даже если промежуточных папок нет: mkdir ___ a/b/c",
            "exercise_type": "fill_in_blank",
            "correct_answers": "-p", "correct_answers_ru": "-p",
            "hint": "«parents» so'zining birinchi harfi.",
            "hint_ru": "Первая буква слова «parents».",
            "explanation": "mkdir -p oradagi barcha papkalarni ham yaratadi va papka mavjud bo'lsa xato bermaydi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Nom o'zgartirish", "title_ru": "Переименование",
            "description": "Faylning nomini shu papkaning o'zida o'zgartirish uchun qaysi buyruq ishlatiladi?",
            "description_ru": "Какая команда используется, чтобы переименовать файл в той же папке?",
            "exercise_type": "multiple_choice",
            "options": ["mv eski yangi", "cp eski yangi", "rm eski yangi", "touch eski yangi"],
            "options_ru": ["mv старое новое", "cp старое новое", "rm старое новое", "touch старое новое"],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Nom o'zgartirish — «ko'chirish»ning bir ko'rinishi.",
            "hint_ru": "Переименование — это разновидность «перемещения».",
            "explanation": "mv faylni yangi joyga ko'chiradi yoki shu papkada yangi nom beradi. cp nusxa yaratadi va eski fayl qoladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Nusxa va o'chirish", "title_ru": "Копирование и удаление",
            "description": "Loyihani zaxiralab, so'ng nusxani o'chirish bosqichlarini tartibga soling.",
            "description_ru": "Расположите этапы: сделать копию проекта, проверить её и затем удалить.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["mkdir -p backup", "cp -r projects/shop backup/shop-copy", "ls backup", "rm -r backup/shop-copy"],
            "drag_items_ru": ["mkdir -p backup", "cp -r projects/shop backup/shop-copy", "ls backup", "rm -r backup/shop-copy"],
            "correct_order": ["mkdir -p backup", "cp -r projects/shop backup/shop-copy", "ls backup", "rm -r backup/shop-copy"],
            "hint": "Nusxa ko'rinib turgandan keyingina o'chirish mumkin.",
            "hint_ru": "Удалять можно только после того, как копия появилась.",
            "explanation": "Avval nishon papka yaratiladi, keyin nusxa olinadi, ls bilan tekshiriladi va faqat shundan keyin o'chiriladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Ehtiyotkorlik", "title_ru": "Осторожность",
            "description": "rm bilan ishlash haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о работе с rm верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Linux terminalida rm bilan o'chirilgan fayl axlat qutisiga tushmaydi",
                "Papkani ichidagilari bilan o'chirish uchun -r flagi kerak",
                "rm -rf so'ramasdan o'chiradi, shuning uchun yo'lni ikki marta tekshirish kerak",
                "rm xato yo'l kiritilsa baribir hammasini qaytarib beradi",
            ],
            "options_ru": [
                "В терминале Linux файл, удалённый через rm, не попадает в корзину",
                "Чтобы удалить папку вместе с содержимым, нужен флаг -r",
                "rm -rf удаляет без вопросов, поэтому путь нужно проверять дважды",
                "Если ввести неверный путь, rm всё равно вернёт всё обратно",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Terminalda «bekor qilish» tugmasi yo'q.",
            "hint_ru": "В терминале нет кнопки «отменить».",
            "explanation": "rm qaytarib bo'lmaydigan o'chirish; papka uchun -r, so'ramaslik uchun -f. Yo'lni avval ls bilan tekshirish xavfsiz odat.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Shablon belgilar", "title_ru": "Шаблоны",
            "description": "Nima uchun ls projects/shop/*.md faqat README.md ni topdi, .env ni ko'rsatmadi? Va * hamda ? belgilari nimani bildiradi? O'z so'zingiz bilan yozing.",
            "description_ru": "Почему ls projects/shop/*.md нашёл только README.md? И что означают символы * и ?? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Shablon faqat .md bilan tugaydigan nomlarni tanlaydi, .env esa boshqa kengaytmali yashirin fayl. * istalgan sondagi belgilarni (hech narsani ham), ? esa aynan bitta belgini bildiradi; shell nomlarni o'zi ochib beradi.",
            "hint": "Shablon qaysi nomlarga mos kelishini o'ylang.",
            "hint_ru": "Подумайте, каким именам соответствует шаблон.",
            "explanation": "*.md faqat .md bilan tugaydigan nomlarga mos. * — nol yoki ko'p belgi, ? — aynan bitta belgi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 3-dars: qidirish va quvurlar ─────────────────────────────────────────────

_L3_TEXT_UZ = """<h3>Muammo: logdan javob topish</h3>
<p>Veb-server har so'rovni <code>access.log</code> fayliga bir qator qilib yozadi. 70 qatorni ko'z bilan o'qish mumkin, 7 millionini esa yo'q. «Nechta 404 bo'ldi? Qaysi yo'l eng ko'p so'raldi? Qaysi IP xato oldi?» kabi savollarga terminal bir necha soniyada javob beradi. Qator tuzilishi (maydonlar bo'sh joy bilan ajratilgan): <code>IP - - [vaqt +0000] "METOD /yo'l HTTP/1.1" status hajm</code>. Bo'sh joy bo'yicha 1-maydon — IP, 7-maydon — yo'l, 9-maydon — status.</p>

<h3>grep: matn qidirish</h3>
<ul>
  <li><code>grep so'z fayl</code> — so'z bor qatorlarni chiqaradi. <code>-n</code> qator raqami bilan, <code>-i</code> harf registrini farqlamaydi, <code>-v</code> so'z <em>bo'lmagan</em> qatorlar, <code>-c</code> faqat sonini, <code>-r</code> papka ichida rekursiv.</li>
  <li>Izoh: <code>grep ' 404 '</code> da bo'sh joylar ataylab qo'yilgan: shunda «1404» kabi tasodifiy mos kelishlar chiqmaydi.</li>
</ul>

<h3>Quvur (pipe) va qayta yo'naltirish</h3>
<p><strong>Quvur</strong> <code>|</code> bir buyruqning natijasini keyingisiga kirish sifatida beradi. Kichik, bitta ishni qiladigan buyruqlarni zanjirga ulab murakkab ish bajarasiz: bu Unix falsafasi.</p>
<pre class="mermaid">
flowchart LR
  A["access.log"] --> B["awk '{print $9}': status ustuni"]
  B --> C["sort: guruhlash uchun tartiblash"]
  C --> D["uniq -c: qaytarilishlarni sanash"]
  D --> E["sort -rn: ko'pdan kamga"]
</pre>
<ul>
  <li><code>&gt;</code> natijani faylga <em>yozadi</em> (borini o'chirib), <code>&gt;&gt;</code> faylning <em>oxiriga qo'shadi</em>, <code>&lt;</code> faylni kirish sifatida beradi.</li>
  <li><code>2&gt;</code> faqat <em>xato</em> oqimini yo'naltiradi. Har buyruqda ikki chiqish bor: oddiy natija (stdout) va xatolar (stderr).</li>
</ul>

<h3>Matnni qayta ishlovchi buyruqlar</h3>
<ul>
  <li><code>sort</code> — tartiblaydi (<code>-r</code> teskari, <code>-n</code> raqam sifatida, <code>-u</code> takrorlarni olib tashlaydi), <code>uniq</code> — <em>ketma-ket</em> takrorlarni birlashtiradi (shuning uchun avval <code>sort</code>); <code>uniq -c</code> sonini yozadi, <code>uniq -d</code> faqat takrorlanganlarni ko'rsatadi.</li>
  <li><code>cut -d' ' -f1</code> — ajratuvchi (bo'sh joy) bo'yicha 1-maydonni oladi. <code>awk '{print $9}'</code> ham maydon oladi, lekin shart ham qo'ya oladi: <code>awk '$9 == 500 {print $1}'</code> — status 500 bo'lgan qatorlarning IP'si.</li>
  <li><code>tr 'a-z' 'A-Z'</code> — belgilarni almashtiradi, <code>wc -l</code> — qatorlarni sanaydi, <code>xargs</code> — oldingi natijani keyingi buyruqqa <em>argument</em> qilib beradi.</li>
</ul>

<h3>find: fayl qidirish</h3>
<p><code>find qayerda shart</code>: <code>-name '*.py'</code> nom bo'yicha (shablonni tirnoqqa oling, aks holda shell uni o'zi ochib yuboradi), <code>-type d</code> faqat papkalar, <code>-type f</code> faqat fayllar. Boshqa foydali shartlar: <code>-size +1M</code> (1 MB dan katta), <code>-mtime -1</code> (oxirgi kunda o'zgargan).</p>

<h3>Sessiya</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Xulosa: 70 ta so'rovdan 45 tasi <code>200</code>, 10 tasi <code>201</code>, 10 tasi <code>404</code> va <strong>5 tasi <code>500</code></strong>. <code>grep ' 500 '</code> ko'rsatganidek, hammasi <code>/api/login</code> yo'lida, ular <code>awk</code> bilan olingan IP'lar (10.0.0.1–10.0.0.5) hammasidan kelgan: muammo bitta foydalanuvchida emas, yo'lning o'zida. Shu tarzda log tahlilidan aniq xulosa chiqadi. Eslatma: <code>find</code> natijalarining tartibi fayl tizimiga bog'liq va sizda boshqacha bo'lishi mumkin.</p>"""

_L3_TEXT_RU = """<h3>Задача: найти ответ в логе</h3>
<p>Веб-сервер записывает каждый запрос одной строкой в файл <code>access.log</code>. 70 строк можно прочитать глазами, а 7 миллионов — нет. На вопросы «сколько было 404? какой путь запрашивали чаще всего? какой IP получил ошибку?» терминал отвечает за секунды. Структура строки (поля разделены пробелами): <code>IP - - [время +0000] "МЕТОД /путь HTTP/1.1" статус размер</code>. Если считать по пробелам, 1-е поле — IP, 7-е — путь, 9-е — статус.</p>

<h3>grep: поиск текста</h3>
<ul>
  <li><code>grep слово файл</code> — выводит строки, где есть слово. <code>-n</code> — с номером строки, <code>-i</code> — без учёта регистра, <code>-v</code> — строки, где слова <em>нет</em>, <code>-c</code> — только количество, <code>-r</code> — рекурсивно по папке.</li>
  <li>Пояснение: в <code>grep ' 404 '</code> пробелы поставлены намеренно: так не находятся случайные совпадения вроде «1404».</li>
</ul>

<h3>Конвейер (pipe) и перенаправление</h3>
<p><strong>Конвейер</strong> <code>|</code> передаёт результат одной команды на вход следующей. Соединяя маленькие команды, каждая из которых делает одно дело, вы решаете сложные задачи: в этом философия Unix.</p>
<pre class="mermaid">
flowchart LR
  A["access.log"] --> B["awk '{print $9}': столбец статуса"]
  B --> C["sort: сортировка для группировки"]
  C --> D["uniq -c: подсчёт повторов"]
  D --> E["sort -rn: от большего к меньшему"]
</pre>
<ul>
  <li><code>&gt;</code> <em>записывает</em> результат в файл (затирая прежнее), <code>&gt;&gt;</code> <em>дописывает в конец</em> файла, <code>&lt;</code> подаёт файл на вход.</li>
  <li><code>2&gt;</code> перенаправляет только поток <em>ошибок</em>. У каждой команды два вывода: обычный результат (stdout) и ошибки (stderr).</li>
</ul>

<h3>Команды для обработки текста</h3>
<ul>
  <li><code>sort</code> — сортирует (<code>-r</code> в обратном порядке, <code>-n</code> как числа, <code>-u</code> убирает повторы), <code>uniq</code> — объединяет <em>идущие подряд</em> повторы (поэтому сначала <code>sort</code>); <code>uniq -c</code> пишет количество, <code>uniq -d</code> показывает только повторяющиеся.</li>
  <li><code>cut -d' ' -f1</code> — берёт 1-е поле по разделителю (пробелу). <code>awk '{print $9}'</code> тоже берёт поле, но умеет и условия: <code>awk '$9 == 500 {print $1}'</code> — IP тех строк, где статус 500.</li>
  <li><code>tr 'a-z' 'A-Z'</code> — заменяет символы, <code>wc -l</code> — считает строки, <code>xargs</code> — передаёт результат предыдущей команды следующей как <em>аргументы</em>.</li>
</ul>

<h3>find: поиск файлов</h3>
<p><code>find где условие</code>: <code>-name '*.py'</code> по имени (шаблон берите в кавычки, иначе shell раскроет его сам), <code>-type d</code> только папки, <code>-type f</code> только файлы. Другие полезные условия: <code>-size +1M</code> (больше 1 МБ), <code>-mtime -1</code> (изменён за последние сутки).</p>

<h3>Сессия</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Вывод: из 70 запросов 45 дали <code>200</code>, 10 — <code>201</code>, 10 — <code>404</code> и <strong>5 — <code>500</code></strong>. Как показал <code>grep ' 500 '</code>, все они на пути <code>/api/login</code>, а IP, полученные через <code>awk</code> (10.0.0.1–10.0.0.5), — это все пять клиентов: проблема не у одного пользователя, а в самом пути. Так анализ лога даёт конкретный вывод. Примечание: порядок результатов <code>find</code> зависит от файловой системы и у вас может быть другим.</p>"""

_L3_BLOCKS = dict(TRANSCRIPT=TRANSCRIPT_L3)

LESSON_3 = {
    "order": 2,
    "title": "3-Qidirish, filtrlash va quvurlar (pipe)",
    "title_ru": "3-Поиск, фильтрация и конвейеры (pipe)",
    "points_reward": 10,
    "text_content": _fill(_L3_TEXT_UZ, **_L3_BLOCKS),
    "text_content_ru": _fill(_L3_TEXT_RU, **_L3_BLOCKS),
    "code_content": TRANSCRIPT_L3,
    "code_content_ru": TRANSCRIPT_L3,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: access.log tahlili grep, awk, sort va uniq bilan",
        "title_ru": "Пример: анализ access.log через grep, awk, sort и uniq",
        "description": "grep, find, quvurlar, awk, qayta yo'naltirish: 70 qatorli logdan statuslar, yo'llar va IP'lar bo'yicha xulosa.",
        "description_ru": "grep, find, конвейеры, awk, перенаправление: выводы по статусам, путям и IP из лога в 70 строк.",
        "sample_type": "code",
        "code_files": [{"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L3}],
    },
    "exercises": [
        {
            "title": "Qator sanash", "title_ru": "Подсчёт строк",
            "description": "Fayldagi qatorlar sonini sanaydigan buyruq: ___ -l access.log",
            "description_ru": "Команда, считающая количество строк в файле: ___ -l access.log",
            "exercise_type": "fill_in_blank",
            "correct_answers": "wc",
            "hint": "«word count» qisqartmasi.",
            "hint_ru": "Сокращение от «word count».",
            "explanation": "wc -l fayldagi qatorlar sonini chiqaradi (wc — word count).",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "grep -v", "title_ru": "grep -v",
            "description": "grep -v ' 200 ' access.log nimani chiqaradi?",
            "description_ru": "Что выведет grep -v ' 200 ' access.log?",
            "exercise_type": "multiple_choice",
            "options": [
                "Statusi 200 bo'lmagan qatorlarni",
                "Faqat statusi 200 bo'lgan qatorlarni",
                "Fayldagi qatorlar sonini",
                "Hamma qatorlarni teskari tartibda",
            ],
            "options_ru": [
                "Строки, где статус не 200",
                "Только строки со статусом 200",
                "Количество строк в файле",
                "Все строки в обратном порядке",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "-v — «invert» (teskari).",
            "hint_ru": "-v — «invert» (инвертировать).",
            "explanation": "-v tanlovni teskari qiladi: so'z bor qatorlar tashlanadi, yo'q qatorlar chiqariladi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "Statuslarni sanash", "title_ru": "Подсчёт статусов",
            "description": "Logdagi statuslarni sanab, ko'pdan kamga tartiblaydigan zanjirni to'g'ri tartibga soling.",
            "description_ru": "Расположите звенья конвейера, считающего статусы в логе от частых к редким.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["awk '{print $9}' access.log", "sort", "uniq -c", "sort -rn"],
            "drag_items_ru": ["awk '{print $9}' access.log", "sort", "uniq -c", "sort -rn"],
            "correct_order": ["awk '{print $9}' access.log", "sort", "uniq -c", "sort -rn"],
            "hint": "uniq faqat ketma-ket takrorlarni birlashtiradi, shuning uchun u oldidan tartiblash kerak.",
            "hint_ru": "uniq объединяет только идущие подряд повторы, поэтому перед ним нужна сортировка.",
            "explanation": "Avval status ustuni ajratiladi, sort bir xillarni yonma-yon qo'yadi, uniq -c ularni sanaydi va sort -rn eng ko'pini tepaga chiqaradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Yo'naltirish belgilari", "title_ru": "Символы перенаправления",
            "description": "Qayta yo'naltirish haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о перенаправлении верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "> natijani faylga yozadi va fayldagi eskisini o'chiradi",
                ">> natijani faylning oxiriga qo'shadi",
                "2> faqat xato xabarlarini yo'naltiradi",
                "| natijani faylga yozadi",
            ],
            "options_ru": [
                "> записывает результат в файл, затирая прежнее содержимое",
                ">> дописывает результат в конец файла",
                "2> перенаправляет только сообщения об ошибках",
                "| записывает результат в файл",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Quvur (|) natijani keyingi buyruqqa uzatadi, faylga emas.",
            "hint_ru": "Конвейер (|) передаёт результат следующей команде, а не в файл.",
            "explanation": ">, >> va 2> to'g'ri. | natijani faylga emas, keyingi buyruqning kirishiga beradi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Logdan xulosa", "title_ru": "Вывод из лога",
            "description": "Log tahlilidan nima bilib oldik va qaysi buyruqlar bunga yordam berdi? 500 xatolari haqida o'z so'zingiz bilan yozing.",
            "description_ru": "Что мы узнали из анализа лога и какие команды помогли? Напишите своими словами про ошибки 500.",
            "exercise_type": "text_input",
            "expected_answer": "70 ta so'rovdan 5 tasi 500 xato bergan. grep ' 500 ' ularning hammasi /api/login yo'lida ekanini, awk va sort -u esa xato hamma 5 ta IP'dan kelganini ko'rsatdi: muammo bitta foydalanuvchida emas, shu yo'lning o'zida.",
            "hint": "Xatolar qaysi yo'lda va qaysi IP'larda uchragan?",
            "hint_ru": "На каком пути и у каких IP встретились ошибки?",
            "explanation": "grep xato qatorlarini ajratadi, awk kerakli maydonni (IP yoki yo'l) oladi, sort | uniq -c esa sanaydi. Natijada xato bitta yo'lga bog'liqligi ma'lum bo'ladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 4-dars: ruxsatlar, foydalanuvchilar, PATH ────────────────────────────────

_L4_TEXT_UZ = """<h3>Nega ruxsatlar</h3>
<p>Linux ko'p foydalanuvchili tizim: serverda siz, boshqa dasturchi va dasturlarning o'z hisoblari bor. Har faylning <strong>egasi</strong>, <strong>guruhi</strong> va <strong>ruxsatlari</strong> bor: kim o'qiy oladi, o'zgartira oladi, ishga tushira oladi. Bu parollar bor <code>.env</code> yoki shaxsiy SSH kaliti kabi fayllarni begonalardan himoya qiladi. «Permission denied» xatosi aksar hollarda ruxsat yetishmasligini bildiradi.</p>

<h3>ls -l ni o'qish</h3>
<pre class="mermaid">
flowchart LR
  A["-rwxr-xr-x"] --> B["- : oddiy fayl (d = papka)"]
  A --> C["rwx : egasi (user): o'qish, yozish, ishga tushirish"]
  A --> D["r-x : guruh (group): o'qish va ishga tushirish"]
  A --> E["r-x : boshqalar (others): o'qish va ishga tushirish"]
</pre>
<ul>
  <li><code>r</code> (read, 4) — o'qish, <code>w</code> (write, 2) — o'zgartirish, <code>x</code> (execute, 1) — fayl uchun ishga tushirish, <em>papka</em> uchun ichiga kirish.</li>
  <li>Raqamli yozuv uch raqam: <code>755</code> = egasi <code>7</code> (4+2+1 = rwx), guruh <code>5</code> (4+1 = r-x), boshqalar <code>5</code> (r-x). <code>644</code> = rw-r--r--, <code>600</code> = rw-------.</li>
  <li><code>ls -l</code> da keyingi ustunlar: bog'lanishlar soni, egasi, guruhi, hajmi (bayt), o'zgargan sana va nom.</li>
</ul>

<h3>chmod: ruxsatni o'zgartirish</h3>
<ul>
  <li>Raqam bilan: <code>chmod 600 .env</code>, <code>chmod 755 skript.sh</code>.</li>
  <li>Harf bilan: <code>chmod +x skript.sh</code> (hamma uchun ishga tushirish), <code>chmod u+rwx,g+rx,o-rwx fayl</code> (<code>u</code> — egasi, <code>g</code> — guruh, <code>o</code> — boshqalar, <code>+</code> qo'shish, <code>-</code> olib tashlash).</li>
  <li>Hech qachon <code>chmod 777</code> (hamma hamma narsa qila oladi) qilmang: bu odatda xato yechim va xavfsizlik teshigi.</li>
</ul>

<h3>Skriptni ishga tushirish</h3>
<p>Matn fayl o'z-o'zidan dastur emas: unga <code>x</code> ruxsati kerak. Skriptning birinchi qatori <strong>shebang</strong> (<code>#!/usr/bin/env bash</code>) tizimga uni qaysi dastur bilan ishga tushirishni aytadi. Yuqoridagi sessiyada ko'rasiz: <code>./hello.sh</code> <code>chmod +x</code> dan oldin «Permission denied» beradi, keyin ishlaydi. <code>./</code> «joriy papkadagi shu fayl» degani: shell joriy papkani o'zi qidirmaydi.</p>

<h3>Foydalanuvchi va administrator</h3>
<ul>
  <li><code>id</code> — sizning foydalanuvchi va guruh raqamlaringiz, <code>whoami</code> — nomingiz. <code>umask</code> — yangi fayllar qanday ruxsat bilan yaratilishini belgilaydi: <code>0022</code> da fayl <code>644</code>, papka <code>755</code> bo'ladi.</li>
  <li><code>root</code> — administrator, hamma narsaga ruxsati bor. Oddiy foydalanuvchi egasini o'zgartira olmaydi: <code>chown root hello.sh</code> «Operation not permitted» beradi. Administrator huquqi kerak bo'lsa, buyruq oldiga <code>sudo</code> qo'yiladi (masalan, <code>sudo chown root fayl</code>), u parol so'raydi. <code>sudo</code> faqat kerak bo'lgandagina ishlating.</li>
</ul>

<h3>PATH: buyruqlar qayerdan topiladi</h3>
<p>Siz <code>ls</code> yozganda shell uni <code>PATH</code> o'zgaruvchisidagi papkalar ro'yxatidan (<code>:</code> bilan ajratilgan) birma-bir qidiradi. O'z skriptingizni istalgan joydan chaqirish uchun uni shu ro'yxatdagi papkaga qo'ying. Odatda <code>~/bin</code> yaratib, <code>PATH</code> ga qo'shishadi. <code>which nom</code> buyruq qayerdan topilganini, <code>type nom</code> esa u nima ekanini (fayl, shell ichki buyrug'i, alias) ko'rsatadi. Eslatma: <code>export PATH=...</code> faqat joriy terminal oynasi uchun; doimiy qilish uchun uni <code>~/.bashrc</code> fayliga yozing.</p>

<h3>Sessiya</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Natijani ko'ring: <code>.env</code> <code>600</code> bo'ldi (<code>-rw-------</code>: faqat egasi), skript <code>755</code> da <code>./hello.sh</code> ishlaydi, <code>644</code> da esa yana «Permission denied». <code>hello</code> nomi <code>~/bin</code> dagi nusxadan topilgan va istalgan papkadan ishlaydi.</p>"""

_L4_TEXT_RU = """<h3>Зачем нужны права доступа</h3>
<p>Linux — многопользовательская система: на сервере есть учётные записи ваша, других разработчиков и программ. У каждого файла есть <strong>владелец</strong>, <strong>группа</strong> и <strong>права</strong>: кто может читать, изменять, запускать. Это защищает от посторонних такие файлы, как <code>.env</code> с паролями или личный SSH-ключ. Ошибка «Permission denied» чаще всего означает нехватку прав.</p>

<h3>Читаем ls -l</h3>
<pre class="mermaid">
flowchart LR
  A["-rwxr-xr-x"] --> B["- : обычный файл (d = папка)"]
  A --> C["rwx : владелец (user): чтение, запись, запуск"]
  A --> D["r-x : группа (group): чтение и запуск"]
  A --> E["r-x : остальные (others): чтение и запуск"]
</pre>
<ul>
  <li><code>r</code> (read, 4) — чтение, <code>w</code> (write, 2) — изменение, <code>x</code> (execute, 1) — для файла запуск, для <em>папки</em> вход внутрь.</li>
  <li>Числовая запись — три цифры: <code>755</code> = владелец <code>7</code> (4+2+1 = rwx), группа <code>5</code> (4+1 = r-x), остальные <code>5</code> (r-x). <code>644</code> = rw-r--r--, <code>600</code> = rw-------.</li>
  <li>Следующие столбцы <code>ls -l</code>: число ссылок, владелец, группа, размер (в байтах), дата изменения и имя.</li>
</ul>

<h3>chmod: меняем права</h3>
<ul>
  <li>Числами: <code>chmod 600 .env</code>, <code>chmod 755 скрипт.sh</code>.</li>
  <li>Буквами: <code>chmod +x скрипт.sh</code> (запуск для всех), <code>chmod u+rwx,g+rx,o-rwx файл</code> (<code>u</code> — владелец, <code>g</code> — группа, <code>o</code> — остальные, <code>+</code> добавить, <code>-</code> убрать).</li>
  <li>Никогда не делайте <code>chmod 777</code> (все могут всё): это обычно неверное решение и дыра в безопасности.</li>
</ul>

<h3>Запуск скрипта</h3>
<p>Текстовый файл сам по себе не программа: ему нужно право <code>x</code>. Первая строка скрипта — <strong>shebang</strong> (<code>#!/usr/bin/env bash</code>) — сообщает системе, какой программой его запускать. В сессии выше вы увидите: <code>./hello.sh</code> до <code>chmod +x</code> выдаёт «Permission denied», а после — работает. <code>./</code> означает «этот файл в текущей папке»: shell сам текущую папку не ищет.</p>

<h3>Пользователь и администратор</h3>
<ul>
  <li><code>id</code> — ваши номера пользователя и групп, <code>whoami</code> — ваше имя. <code>umask</code> — определяет, с какими правами создаются новые файлы: при <code>0022</code> файл получает <code>644</code>, а папка <code>755</code>.</li>
  <li><code>root</code> — администратор, у него есть доступ ко всему. Обычный пользователь не может сменить владельца: <code>chown root hello.sh</code> выдаёт «Operation not permitted». Если нужны права администратора, перед командой ставят <code>sudo</code> (например, <code>sudo chown root файл</code>), он запросит пароль. Используйте <code>sudo</code> только когда это действительно нужно.</li>
</ul>

<h3>PATH: откуда берутся команды</h3>
<p>Когда вы вводите <code>ls</code>, shell ищет эту команду по очереди в папках из переменной <code>PATH</code> (разделитель <code>:</code>). Чтобы запускать свой скрипт из любого места, поместите его в одну из этих папок. Обычно создают <code>~/bin</code> и добавляют её в <code>PATH</code>. <code>which имя</code> показывает, откуда найдена команда, а <code>type имя</code> — чем она является (файл, встроенная команда shell, alias). Примечание: <code>export PATH=...</code> действует только в текущем окне терминала; чтобы сделать это постоянным, запишите строку в файл <code>~/.bashrc</code>.</p>

<h3>Сессия</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Посмотрите на результат: <code>.env</code> стал <code>600</code> (<code>-rw-------</code>: только владелец), скрипт с <code>755</code> запускается через <code>./hello.sh</code>, а с <code>644</code> снова «Permission denied». Имя <code>hello</code> найдено по копии в <code>~/bin</code> и работает из любой папки.</p>"""

_L4_BLOCKS = dict(TRANSCRIPT=TRANSCRIPT_L4)

LESSON_4 = {
    "order": 3,
    "title": "4-Ruxsatlar, foydalanuvchilar va PATH",
    "title_ru": "4-Права доступа, пользователи и PATH",
    "points_reward": 10,
    "text_content": _fill(_L4_TEXT_UZ, **_L4_BLOCKS),
    "text_content_ru": _fill(_L4_TEXT_RU, **_L4_BLOCKS),
    "code_content": TRANSCRIPT_L4,
    "code_content_ru": TRANSCRIPT_L4,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: chmod, ruxsatlar va PATH",
        "title_ru": "Пример: chmod, права и PATH",
        "description": "Permission denied, chmod +x, 755/644/600, stat, chown va ~/bin orqali PATH: haqiqiy Linux sessiyasi.",
        "description_ru": "Permission denied, chmod +x, 755/644/600, stat, chown и PATH через ~/bin: сессия в настоящем Linux.",
        "sample_type": "code",
        "code_files": [{"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L4}],
    },
    "exercises": [
        {
            "title": "Raqamli ruxsat", "title_ru": "Числовые права",
            "description": "Faqat egasi o'qiy va yoza oladigan (rw-------) ruxsatning raqamli ko'rinishi: chmod ___ .env",
            "description_ru": "Числовая запись прав, при которых читать и писать может только владелец (rw-------): chmod ___ .env",
            "exercise_type": "fill_in_blank",
            "correct_answers": "600",
            "hint": "rw- = 4+2 = 6, qolganlari 0.",
            "hint_ru": "rw- = 4+2 = 6, остальные 0.",
            "explanation": "Egasi uchun r+w = 4+2 = 6, guruh va boshqalar uchun hech narsa: 600. Parollar bor .env uchun mos ruxsat.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "755 nimani bildiradi", "title_ru": "Что значит 755",
            "description": "chmod 755 hello.sh qanday ruxsat beradi?",
            "description_ru": "Какие права задаёт chmod 755 hello.sh?",
            "exercise_type": "multiple_choice",
            "options": [
                "Egasi: o'qish, yozish, ishga tushirish; guruh va boshqalar: o'qish va ishga tushirish",
                "Hamma hammasini qila oladi",
                "Faqat egasi o'qiy oladi",
                "Hech kim ishga tushira olmaydi",
            ],
            "options_ru": [
                "Владелец: чтение, запись, запуск; группа и остальные: чтение и запуск",
                "Все могут всё",
                "Только владелец может читать",
                "Никто не может запускать",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "7 = 4+2+1, 5 = 4+1.",
            "hint_ru": "7 = 4+2+1, 5 = 4+1.",
            "explanation": "7 (rwx) egasiga, 5 (r-x) guruh va boshqalarga: o'qish va ishga tushirish bor, yozish yo'q. Hamma narsa uchun 777 kerak bo'lardi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Skriptni ishga tushirish", "title_ru": "Запуск скрипта",
            "description": "Yangi yozilgan hello.sh ni ishlaydigan qilish bosqichlarini joylashtiring.",
            "description_ru": "Расположите этапы, чтобы заработал только что написанный hello.sh.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["Birinchi qatorga #!/usr/bin/env bash yozish", "./hello.sh: Permission denied xatosini ko'rish", "chmod +x hello.sh", "./hello.sh: skript ishlaydi"],
            "drag_items_ru": ["Написать в первой строке #!/usr/bin/env bash", "Увидеть ошибку ./hello.sh: Permission denied", "chmod +x hello.sh", "./hello.sh: скрипт работает"],
            "correct_order": ["Birinchi qatorga #!/usr/bin/env bash yozish", "./hello.sh: Permission denied xatosini ko'rish", "chmod +x hello.sh", "./hello.sh: skript ishlaydi"],
            "hint": "x ruxsati berilmaguncha skript ishlamaydi.",
            "hint_ru": "Пока не выдано право x, скрипт не запустится.",
            "explanation": "Fayl yaratiladi, ishga tushirishga urinilsa ruxsat yo'qligi chiqadi, chmod +x ruxsat beradi va shundan keyin skript ishlaydi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "Xavfsiz odatlar", "title_ru": "Безопасные привычки",
            "description": "Ruxsatlar va sudo haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о правах и sudo верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Parollar bor .env va shaxsiy SSH kalitiga 600 beriladi",
                "chmod 777 odatda xavfsizlik teshigi",
                "Oddiy foydalanuvchi chown bilan egasini o'zgartira olmaydi, buning uchun sudo kerak",
                "sudo ni har buyruq oldiga qo'yish yaxshi odat",
            ],
            "options_ru": [
                ".env с паролями и личному SSH-ключу выдают 600",
                "chmod 777 — обычно дыра в безопасности",
                "Обычный пользователь не может сменить владельца через chown, для этого нужен sudo",
                "Ставить sudo перед каждой командой — хорошая привычка",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "sudo faqat kerak bo'lganda ishlatiladi.",
            "hint_ru": "sudo используют только когда он действительно нужен.",
            "explanation": "600 maxfiy fayllar uchun, 777 xavfli, chown egasini o'zgartirish administrator huquqini talab qiladi. sudo esa faqat zarur bo'lganda ishlatiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "PATH vazifasi", "title_ru": "Назначение PATH",
            "description": "PATH o'zgaruvchisi nima uchun kerak va o'z skriptingizni istalgan joydan chaqirish uchun nima qilasiz? O'z so'zingiz bilan yozing.",
            "description_ru": "Для чего нужна переменная PATH и что вы сделаете, чтобы вызывать свой скрипт из любого места? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "PATH — shell buyruqlarni qidiradigan papkalar ro'yxati. Skriptni istalgan joydan chaqirish uchun uni (ishga tushirish ruxsati bilan) shu ro'yxatdagi papkaga qo'yaman, masalan ~/bin yaratib, uni export PATH=\"$HOME/bin:$PATH\" bilan qo'shaman. Doimiy qilish uchun buni ~/.bashrc ga yozaman.",
            "hint": "Shell buyruq nomini qayerdan qidiradi?",
            "hint_ru": "Где shell ищет имя команды?",
            "explanation": "PATH dagi papkalardan shell buyruq nomini qidiradi. Skript shu papkalardan birida (masalan, ~/bin) va x ruxsati bilan bo'lsa, uni ./ siz chaqirish mumkin.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 5-dars: jarayonlar, tarmoq, SSH ──────────────────────────────────────────

_L5_TEXT_UZ = """<h3>Jarayonlar</h3>
<p>Ishlayotgan har dastur — <strong>jarayon</strong> (process), unda noyob raqam <strong>PID</strong> bor. Server bilan ishlaganda «nima ishlayapti, nima qotib qoldi, uni qanday to'xtataman» savollari doim chiqadi.</p>
<ul>
  <li><code>ps</code> — jarayonlar ro'yxati (<code>ps aux</code> — hamma jarayonlar, <code>ps -p PID -o pid,stat,comm</code> — bittasi). <code>top</code> — jonli ko'rinish (<code>q</code> bilan chiqiladi).</li>
  <li><code>&amp;</code> buyruq oxirida uni <em>orqa fonda</em> ishga tushiradi, terminal band bo'lmaydi. <code>$!</code> — oxirgi orqa fon jarayonning PID'i, <code>$?</code> — oxirgi buyruqning chiqish kodi.</li>
  <li><code>kill PID</code> jarayonga to'xtash <em>signali</em> (SIGTERM) yuboradi, u tartibli yopilishi mumkin. <code>wait PID</code> uning tugashini kutadi. Sessiyada ko'rasiz: <code>kill</code> dan keyin chiqish kodi <code>143</code> = 128 + 15 (15 — SIGTERM raqami): «signal bilan to'xtatilgan». Jarayon <code>kill</code> ga javob bermasa, <code>kill -9 PID</code> (SIGKILL) majburan o'ldiradi, lekin u tozalash imkonini bermaydi, shuning uchun oxirgi chora.</li>
</ul>

<h3>Tarmoq va portlar</h3>
<p>Server dasturi biror <strong>port</strong>da tinglaydi. Sessiyada bitta qatorda kichik veb-server ishga tushiramiz: <code>python3 -m http.server 8000</code> (papkani <code>http://localhost:8000</code> orqali beradi). <code>curl</code> — terminaldan HTTP so'rov yuboradigan dastur (<code>-s</code> — jim rejim, <code>-o /dev/null -w '%{http_code}'</code> — faqat status kodi). <code>ss -ltn</code> tinglayotgan TCP portlarni ko'rsatadi (<code>-l</code> listening, <code>-t</code> TCP, <code>-n</code> raqam bilan). «Address already in use» xatosi chiqsa, port boshqa jarayonda band: <code>ss -ltn | grep 8000</code> bilan toping.</p>

<h3>Diskni va xotirani tekshirish</h3>
<ul>
  <li><code>df -h</code> — disklarning hajmi va bo'sh joyi (<code>-h</code> — odam o'qiydigan: K, M, G). «Use%» 100% ga yaqin bo'lsa, server to'xtab qolishi mumkin.</li>
  <li><code>du -sh papka</code> — papka hajmi (<code>-s</code> faqat jami, <code>-h</code> odam o'qiydigan). <code>du -sh * | sort -h</code> eng katta papkani oxirida ko'rsatadi: disk to'lganda «nima joy egallayapti» savoliga javob.</li>
  <li><code>free -h</code> — xotira (RAM), <code>uptime</code> — tizim qancha vaqtdan beri ishlayotgani va yuklama.</li>
</ul>

<h3>Muhit o'zgaruvchilari</h3>
<p><code>NOM=qiymat</code> o'zgaruvchi yaratadi, <code>export</code> uni ishga tushirilgan <em>bolalar jarayonlariga</em> ham ko'rinadigan qiladi. Dasturlar sozlamani (<code>APP_ENV</code>, <code>DATABASE_URL</code>, kalit) shundan oladi: sirni kodga yozmasdan berishning oddiy yo'li. <code>NOM=qiymat buyruq</code> qiymatni faqat shu bitta buyruq uchun beradi (sessiyada <code>APP_ENV=test</code> bir marta ishlab, keyin <code>production</code> qoldi). <code>env</code> hamma o'zgaruvchilarni ko'rsatadi.</p>

<h3>Servislar: systemd</h3>
<p>Production serverlarda ilovalar odatda <strong>systemd</strong> servisi sifatida ishlaydi: avtomatik yuklanadi, yiqilsa qayta ishga tushadi, loglari bitta joyda. Asosiy buyruqlar (servis nomi sifatida <code>nginx</code> olindi, o'zingiznikini qo'ying; buni systemd bor server yoki WSL'da sinang):</p>
<pre><code>__SYSTEMD__</code></pre>
<ul>
  <li><code>systemctl is-active nom</code> — servis ishlayaptimi (<code>active</code> yoki <code>inactive</code>), <code>status</code> — batafsil holat va oxirgi loglar.</li>
  <li><code>sudo systemctl restart nom</code> — qayta ishga tushirish: sozlamani o'zgartirgach yoki yangi versiyani qo'ygach.</li>
  <li><code>journalctl -u nom -n 20 --no-pager</code> — servisning oxirgi 20 qator logi. Xato bo'lganda birinchi qaraydigan joy.</li>
</ul>

<h3>SSH: serverga xavfsiz kirish</h3>
<p><strong>SSH</strong> boshqa kompyuterning terminaliga shifrlangan kanal orqali kirishga imkon beradi. Paroldan xavfsizroq usul — <strong>kalit juftligi</strong>: <em>shaxsiy</em> kalit (<code>id_ed25519</code>) sizning kompyuteringizda qoladi va hech kimga berilmaydi, <em>ochiq</em> kalit (<code>id_ed25519.pub</code>) serverga qo'yiladi. Server «bu ochiq kalitga mos shaxsiy kalit egasi» ekanligingizni tekshirib, kiritadi.</p>
<pre class="mermaid">
sequenceDiagram
  participant C as Sizning kompyuteringiz (shaxsiy kalit)
  participant S as Server (~/.ssh/authorized_keys: ochiq kalit)
  C->>S: Ulanish: men student, mana mening ochiq kalitim
  S-->>C: Sinov: shaxsiy kalit egasi ekanini isbotlang
  C->>S: Shaxsiy kalit bilan imzolangan javob
  S-->>C: Kirishga ruxsat
</pre>
<p>Kalit juftligini yaratish sessiyada ko'rsatilgan: <code>ssh-keygen -t ed25519</code>. <code>ls -l ~/.ssh</code> da shaxsiy kalit <code>-rw-------</code> (600): ssh boshqalar o'qiy oladigan shaxsiy kalitni rad etadi. <code>.pub</code> faylning birinchi so'zi kalit turi (<code>ssh-ed25519</code>), oxirgisi izoh (siz <code>-C</code> bilan bergan nom). Serverga ulanish buyruqlari (o'z serveringizning manzili va nomini qo'ying; <code>203.0.113.10</code> — hujjatlar uchun ajratilgan namuna manzil):</p>
<pre><code>__SSH__</code></pre>
<ul>
  <li><code>ssh-copy-id</code> ochiq kalitingizni serverning <code>~/.ssh/authorized_keys</code> fayliga qo'shadi (bir marta paroldan foydalaniladi).</li>
  <li><code>scp fayl foydalanuvchi@server:/papka/</code> faylni serverga ko'chiradi; buyruq oxiridagi qo'shtirnoq ichidagi matn serverda bajariladi.</li>
</ul>
<p>Har safar uzun buyruq yozmaslik uchun <code>~/.ssh/config</code> faylida qisqa nom beriladi, keyin <code>ssh myserver</code> yetarli:</p>
<pre><code>__SSHCONFIG__</code></pre>

<h3>Sessiya</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Eslatma: PID raqamlari va <code>free</code>, <code>df</code> natijalari har kompyuterda boshqacha, shu sababli sessiyada ular faqat sarlavha qatorlari bilan ko'rsatilgan.</p>"""

_L5_TEXT_RU = """<h3>Процессы</h3>
<p>Каждая запущенная программа — это <strong>процесс</strong> (process) с уникальным номером <strong>PID</strong>. При работе с сервером постоянно возникают вопросы «что запущено, что зависло, как это остановить».</p>
<ul>
  <li><code>ps</code> — список процессов (<code>ps aux</code> — все процессы, <code>ps -p PID -o pid,stat,comm</code> — один). <code>top</code> — живой вид (выход клавишей <code>q</code>).</li>
  <li><code>&amp;</code> в конце команды запускает её <em>в фоне</em>, и терминал остаётся свободным. <code>$!</code> — PID последнего фонового процесса, <code>$?</code> — код завершения последней команды.</li>
  <li><code>kill PID</code> посылает процессу <em>сигнал</em> остановки (SIGTERM), и он может завершиться корректно. <code>wait PID</code> ждёт его окончания. В сессии вы увидите: после <code>kill</code> код завершения равен <code>143</code> = 128 + 15 (15 — номер SIGTERM): «остановлен сигналом». Если процесс не реагирует на <code>kill</code>, <code>kill -9 PID</code> (SIGKILL) завершает его принудительно, но не даёт ему прибраться, поэтому это крайняя мера.</li>
</ul>

<h3>Сеть и порты</h3>
<p>Серверная программа слушает какой-нибудь <strong>порт</strong>. В сессии мы одной строкой запускаем небольшой веб-сервер: <code>python3 -m http.server 8000</code> (отдаёт папку по адресу <code>http://localhost:8000</code>). <code>curl</code> — программа, отправляющая HTTP-запрос из терминала (<code>-s</code> — тихий режим, <code>-o /dev/null -w '%{http_code}'</code> — только код статуса). <code>ss -ltn</code> показывает слушающие TCP-порты (<code>-l</code> listening, <code>-t</code> TCP, <code>-n</code> числами). Если появилась ошибка «Address already in use», порт занят другим процессом: найдите его через <code>ss -ltn | grep 8000</code>.</p>

<h3>Проверка диска и памяти</h3>
<ul>
  <li><code>df -h</code> — размер дисков и свободное место (<code>-h</code> — читаемо для человека: K, M, G). Если «Use%» близко к 100%, сервер может остановиться.</li>
  <li><code>du -sh папка</code> — размер папки (<code>-s</code> только итог, <code>-h</code> читаемо). <code>du -sh * | sort -h</code> показывает самую большую папку последней: ответ на вопрос «что занимает место», когда диск заполнен.</li>
  <li><code>free -h</code> — память (RAM), <code>uptime</code> — сколько времени работает система и какая нагрузка.</li>
</ul>

<h3>Переменные окружения</h3>
<p><code>ИМЯ=значение</code> создаёт переменную, а <code>export</code> делает её видимой и для запущенных <em>дочерних процессов</em>. Программы получают настройки (<code>APP_ENV</code>, <code>DATABASE_URL</code>, ключ) именно так: это простой способ передать секрет, не записывая его в код. <code>ИМЯ=значение команда</code> задаёт значение только для этой одной команды (в сессии <code>APP_ENV=test</code> сработал один раз, а потом снова остался <code>production</code>). <code>env</code> показывает все переменные.</p>

<h3>Сервисы: systemd</h3>
<p>На production-серверах приложения обычно работают как сервисы <strong>systemd</strong>: запускаются автоматически, перезапускаются при падении, а логи собраны в одном месте. Основные команды (в качестве имени сервиса взят <code>nginx</code>, подставьте свой; пробуйте на сервере с systemd или в WSL):</p>
<pre><code>__SYSTEMD__</code></pre>
<ul>
  <li><code>systemctl is-active имя</code> — работает ли сервис (<code>active</code> или <code>inactive</code>), <code>status</code> — подробное состояние и последние логи.</li>
  <li><code>sudo systemctl restart имя</code> — перезапуск: после изменения настроек или выкладки новой версии.</li>
  <li><code>journalctl -u имя -n 20 --no-pager</code> — последние 20 строк лога сервиса. Первое место, куда смотрят при ошибке.</li>
</ul>

<h3>SSH: безопасный вход на сервер</h3>
<p><strong>SSH</strong> позволяет войти в терминал другого компьютера по зашифрованному каналу. Безопаснее пароля — <strong>пара ключей</strong>: <em>закрытый</em> ключ (<code>id_ed25519</code>) остаётся на вашем компьютере и никому не передаётся, <em>открытый</em> ключ (<code>id_ed25519.pub</code>) кладётся на сервер. Сервер проверяет, что вы владеете закрытым ключом, соответствующим этому открытому, и пускает вас.</p>
<pre class="mermaid">
sequenceDiagram
  participant C as Ваш компьютер (закрытый ключ)
  participant S as Сервер (~/.ssh/authorized_keys: открытый ключ)
  C->>S: Подключение: я student, вот мой открытый ключ
  S-->>C: Проверка: докажите, что у вас закрытый ключ
  C->>S: Ответ, подписанный закрытым ключом
  S-->>C: Вход разрешён
</pre>
<p>Создание пары ключей показано в сессии: <code>ssh-keygen -t ed25519</code>. В <code>ls -l ~/.ssh</code> закрытый ключ имеет <code>-rw-------</code> (600): ssh отвергает закрытый ключ, доступный для чтения другим. Первое слово файла <code>.pub</code> — тип ключа (<code>ssh-ed25519</code>), последнее — комментарий (имя, которое вы задали через <code>-C</code>). Команды подключения к серверу (подставьте адрес и имя своего сервера; <code>203.0.113.10</code> — адрес-пример, зарезервированный для документации):</p>
<pre><code>__SSH__</code></pre>
<ul>
  <li><code>ssh-copy-id</code> добавляет ваш открытый ключ в файл <code>~/.ssh/authorized_keys</code> на сервере (один раз используется пароль).</li>
  <li><code>scp файл пользователь@сервер:/папка/</code> копирует файл на сервер; текст в кавычках в конце команды <code>ssh</code> выполняется на сервере.</li>
</ul>
<p>Чтобы не набирать длинные команды, в файле <code>~/.ssh/config</code> задают короткое имя, и тогда достаточно <code>ssh myserver</code>:</p>
<pre><code>__SSHCONFIG__</code></pre>

<h3>Сессия</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Примечание: номера PID и результаты <code>free</code>, <code>df</code> на каждом компьютере разные, поэтому в сессии для них оставлены только строки заголовков.</p>"""

_L5_BLOCKS = dict(SYSTEMD=CMD_SYSTEMD, SSH=CMD_SSH, SSHCONFIG=SSH_CONFIG, TRANSCRIPT=TRANSCRIPT_L5)

LESSON_5 = {
    "order": 4,
    "title": "5-Jarayonlar, tarmoq va SSH",
    "title_ru": "5-Процессы, сеть и SSH",
    "points_reward": 10,
    "text_content": _fill(_L5_TEXT_UZ, **_L5_BLOCKS),
    "text_content_ru": _fill(_L5_TEXT_RU, **_L5_BLOCKS),
    "code_content": TRANSCRIPT_L5,
    "code_content_ru": TRANSCRIPT_L5,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: jarayon, port, o'zgaruvchi va SSH kaliti",
        "title_ru": "Пример: процесс, порт, переменная и SSH-ключ",
        "description": "kill va chiqish kodi 143, orqa fonda veb-server, curl va ss, export, ssh-keygen: haqiqiy Linux sessiyasi. systemd va ssh buyruqlari alohida.",
        "description_ru": "kill и код завершения 143, веб-сервер в фоне, curl и ss, export, ssh-keygen: сессия в настоящем Linux. Команды systemd и ssh отдельно.",
        "sample_type": "code",
        "code_files": [
            {"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L5},
            {"filename": "systemd.sh", "language": "bash", "code": CMD_SYSTEMD},
            {"filename": "ssh.sh", "language": "bash", "code": CMD_SSH},
            {"filename": "ssh_config", "language": "text", "code": SSH_CONFIG},
        ],
    },
    "exercises": [
        {
            "title": "Orqa fonda ishga tushirish", "title_ru": "Запуск в фоне",
            "description": "Buyruqni orqa fonda ishga tushirish uchun uning oxiriga qo'yiladigan belgi: sleep 300 ___",
            "description_ru": "Символ, который ставят в конце команды, чтобы запустить её в фоне: sleep 300 ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "&",
            "hint": "«Va» (and) belgisi.",
            "hint_ru": "Знак «и» (ampersand).",
            "explanation": "Buyruq oxiridagi & uni orqa fonda ishga tushiradi, terminal band bo'lmaydi. Jarayonning PID'i $! da turadi.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "143 chiqish kodi", "title_ru": "Код завершения 143",
            "description": "kill dan keyin wait chiqish kodi sifatida 143 ni qaytardi. Bu nimani bildiradi?",
            "description_ru": "После kill команда wait вернула код завершения 143. Что это значит?",
            "exercise_type": "multiple_choice",
            "options": [
                "Jarayon SIGTERM signali bilan to'xtatilgan (128 + 15)",
                "Jarayon muvaffaqiyatli tugagan",
                "Server 143-portda ishlayapti",
                "Fayl topilmagan",
            ],
            "options_ru": [
                "Процесс остановлен сигналом SIGTERM (128 + 15)",
                "Процесс успешно завершился",
                "Сервер работает на порту 143",
                "Файл не найден",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "128 ga signal raqami qo'shilgan.",
            "hint_ru": "К 128 прибавлен номер сигнала.",
            "explanation": "Signal bilan to'xtatilgan jarayonning kodi 128 + signal raqami. SIGTERM — 15, demak 143. Muvaffaqiyat kodi esa 0.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Veb-serverni tekshirish", "title_ru": "Проверка веб-сервера",
            "description": "Kichik veb-serverni ishga tushirib, tekshirib va to'xtatish bosqichlarini joylashtiring.",
            "description_ru": "Расположите этапы: запустить небольшой веб-сервер, проверить его и остановить.",
            "exercise_type": "drag_and_drop",
            "drag_items": ["python3 -m http.server 8000 &", "ss -ltn | grep 8000", "curl -s localhost:8000/shopping.txt", "kill $!"],
            "drag_items_ru": ["python3 -m http.server 8000 &", "ss -ltn | grep 8000", "curl -s localhost:8000/shopping.txt", "kill $!"],
            "correct_order": ["python3 -m http.server 8000 &", "ss -ltn | grep 8000", "curl -s localhost:8000/shopping.txt", "kill $!"],
            "hint": "To'xtatish eng oxirida.",
            "hint_ru": "Остановка в самом конце.",
            "explanation": "Server orqa fonda ishga tushadi, port tinglayotgani ss bilan, javob esa curl bilan tekshiriladi va oxirida kill $! bilan to'xtatiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "SSH kalitlari", "title_ru": "Ключи SSH",
            "description": "SSH kalit juftligi haqida qaysi gaplar to'g'ri? (Bir nechta javob)",
            "description_ru": "Какие утверждения о паре ключей SSH верны? (Несколько ответов)",
            "exercise_type": "multiple_choice",
            "options": [
                "Shaxsiy kalit kompyuteringizda qoladi va hech kimga berilmaydi",
                "Ochiq kalit (.pub) serverning authorized_keys fayliga qo'yiladi",
                "Shaxsiy kalit fayli 600 ruxsatiga ega bo'lishi kerak",
                "Shaxsiy kalitni jamoadoshga yuborish xavfsiz",
            ],
            "options_ru": [
                "Закрытый ключ остаётся на вашем компьютере и никому не передаётся",
                "Открытый ключ (.pub) кладётся в файл authorized_keys на сервере",
                "Файл закрытого ключа должен иметь права 600",
                "Отправлять закрытый ключ коллеге безопасно",
            ],
            "correct_answers": "A,B,C", "is_multiple_select": True,
            "hint": "Shaxsiy kalit — sizning «parolingiz».",
            "hint_ru": "Закрытый ключ — это ваш «пароль».",
            "explanation": "Shaxsiy kalit sir, ochiq kalit esa serverda turadi. ssh boshqalar o'qiy oladigan shaxsiy kalitni rad etadi, shuning uchun 600.",
            "difficulty_level": "Medium", "points": 4,
        },
        {
            "title": "export nima qiladi", "title_ru": "Что делает export",
            "description": "export bilan oddiy o'zgaruvchi yaratish o'rtasidagi farqni o'z so'zingiz bilan yozing. Sessiyadagi child sees misolini eslang.",
            "description_ru": "Объясните своими словами разницу между export и обычным созданием переменной. Вспомните пример child sees из сессии.",
            "exercise_type": "text_input",
            "expected_answer": "Oddiy NOM=qiymat faqat joriy shell'da ko'rinadi. export uni shu shell'dan ishga tushirilgan bolalar jarayonlariga (masalan, bash -c ...) ham ko'rinadigan qiladi, shuning uchun dasturlar sozlamani muhit o'zgaruvchisidan oladi. NOM=qiymat buyruq esa qiymatni faqat shu bitta buyruq uchun beradi.",
            "hint": "Bolalar jarayoni nimani ko'radi?",
            "hint_ru": "Что видит дочерний процесс?",
            "explanation": "export o'zgaruvchini muhitga qo'shadi, shu sabab ishga tushirilgan dasturlar uni o'qiy oladi. Oldiga qo'yilgan NOM=qiymat esa faqat bitta buyruqqa ta'sir qiladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}


# ── 6-dars: bash skriptlar va loyiha ─────────────────────────────────────────

_L6_TEXT_UZ = """<h3>Nega skript</h3>
<p>Bir xil buyruqlar ketma-ketligini har safar qo'lda yozish xatoga olib keladi. Ularni <strong>bash skript</strong>ga yig'ib, bitta buyruq bilan ishga tushirasiz: tahlil, zaxira nusxa, deploy. Bu darsda ikkita haqiqiy skript yozamiz: log hisoboti va zaxira nusxa. Birinchi dars <code>lab_setup.sh</code> ham aynan shunday skript edi.</p>

<h3>Skript tuzilishi</h3>
<pre><code>__LOGREPORT__</code></pre>
<ul>
  <li><strong>Shebang</strong> <code>#!/usr/bin/env bash</code> — birinchi qator: skript qaysi dastur bilan ishlaydi. Fayl <code>chmod +x</code> bilan ishga tushiriladigan qilinadi (4-dars).</li>
  <li><strong>Argumentlar</strong>: <code>$1</code> — birinchi argument, <code>$#</code> — argumentlar soni, <code>$0</code> — skriptning nomi. <code>log=$1</code> o'zgaruvchi yaratadi (tenglik atrofida <em>bo'sh joy bo'lmaydi</em>).</li>
  <li><strong>Qiymatni olish</strong> <code>$(buyruq)</code>: buyruq natijasi o'zgaruvchiga tushadi (<code>total=$(wc -l &lt; "$log")</code>).</li>
  <li><strong>Shartlar</strong>: <code>[[ $# -ne 1 ]]</code> (<code>-ne</code> teng emas, <code>-f</code> fayl bormi, <code>-z</code> bo'shmi), sonlar uchun <code>(( errors &gt; 0 ))</code>. <code>if ...; then ...; fi</code>.</li>
  <li><strong>Chiqish kodi</strong>: <code>exit 2</code> skriptni berilgan kod bilan tugatadi, <code>0</code> — muvaffaqiyat, noldan farqli — xato. Kodni <code>$?</code> bilan ko'rasiz. Biz kelishdik: 1 — fayl yo'q, 2 — noto'g'ri foydalanish, 3 — logda 5xx xato bor. Boshqa dasturlar (CI, monitoring) shu kod bo'yicha qaror qiladi.</li>
  <li><strong>Xato oqimi</strong>: <code>echo "..." &gt;&amp;2</code> xabarni stderr'ga yuboradi, oddiy natija bilan aralashmaydi.</li>
</ul>

<h3>set -euo pipefail</h3>
<p>Standart holatda bash xatodan keyin ham keyingi qatorni bajaraveradi: bu xavfli. Skript boshiga qo'yiladigan <code>set -euo pipefail</code> uch himoya beradi:</p>
<ul>
  <li><code>-e</code> — biror buyruq xato bilan tugasa, skript darhol to'xtaydi (sessiyadagi <code>set -e</code> misolida faqat <code>before</code> chiqdi, <code>after</code> chiqmadi).</li>
  <li><code>-u</code> — e'lon qilinmagan o'zgaruvchiga murojaat xato bo'ladi (<code>unbound variable</code>). Bu <code>rm -rf "$DIR/"</code> da <code>DIR</code> bo'sh qolsa butun tizimni o'chirib yuborish kabi falokatlarning oldini oladi.</li>
  <li><code>-o pipefail</code> — quvurdagi <em>istalgan</em> buyruq xato bersa, quvur xato hisoblanadi (aks holda faqat oxirgisi hisobga olinadi).</li>
</ul>
<p>Bu rejimda <code>grep</code> hech narsa topmasa ham kod <code>1</code> qaytaradi va skript to'xtab qoladi. Shuning uchun skriptda <code>grep -c ... || true</code> yozilgan: «topilmasa ham davom et».</p>

<h3>Buyruqlarni zanjirlash va qiymat bilan ishlash</h3>
<ul>
  <li><code>a &amp;&amp; b</code> — <code>b</code> faqat <code>a</code> muvaffaqiyatli bo'lsa; <code>a || b</code> — <code>b</code> faqat <code>a</code> xato bersa; <code>;</code> — ketma-ket, natijadan qat'i nazar.</li>
  <li><strong>Doim o'zgaruvchini qo'shtirnoqqa oling</strong>: <code>"$log"</code>. Aks holda bo'sh joy bor nomlar bir nechta argumentga bo'linib ketadi. <code>"..."</code> ichida o'zgaruvchi ochiladi, <code>'...'</code> ichida esa matn o'zgarishsiz qoladi.</li>
  <li>Takrorlash: <code>for f in *.py; do ...; done</code>. Funksiya: <code>greet() { echo "hi, $1"; }</code>. <code>${1:?xabar}</code> argument bo'lmasa xabar bilan to'xtatadi.</li>
</ul>

<h3>Zaxira nusxa skripti</h3>
<pre><code>__BACKUP__</code></pre>
<p><code>tar -czf arxiv.tar.gz papka</code> papkani siqilgan arxivga o'raydi (<code>c</code> — create, <code>z</code> — gzip, <code>f</code> — fayl nomi), <code>tar -tzf</code> arxiv ichini ko'rsatadi (ochmasdan tekshirish), <code>tar -xzf</code> ochadi. <code>date +%F</code> sanani <code>2026-10-13</code> ko'rinishida beradi: arxiv nomiga sana qo'yish tartibli zaxira beradi. <code>basename</code> va <code>dirname</code> yo'lni nom va papkaga ajratadi.</p>

<h3>Sessiya</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Natijani o'qing: hisobot <code>5xx = 5</code> topgani uchun chiqish kodi <code>3</code>, argumentsiz chaqirilganda <code>2</code>, mavjud bo'lmagan faylda <code>1</code> bo'ldi; 500 qatorlari olib tashlangan <code>clean.log</code> da esa <code>0</code>. Zaxira skripti ikkinchi argument bo'lmaganda <code>2: usage: ...</code> xabari bilan to'xtadi (<code>${2:?...}</code>), arxiv ichi <code>tar -tzf</code> bilan ko'rsatildi. Sana (<code>2026-10-13</code>) sizda bugungi sana bo'ladi.</p>

<h3>Rejalashtirish: cron</h3>
<p>Skriptni har kecha o'zi ishga tushirish uchun <strong>cron</strong> ishlatiladi. <code>crontab -e</code> jadvalni ochadi, <code>crontab -l</code> uni ko'rsatadi. Qatorda besh maydon: daqiqa, soat, oyning kuni, oy, haftaning kuni, so'ng buyruq. Quyidagi qator har kuni 03:00 da zaxira oladi (<code>*</code> — «har qanday»; cronda yo'lni <em>to'liq</em> yozing):</p>
<pre><code>__CRON__</code></pre>
<pre><code>__CMDCRON__</code></pre>
<p>Cron buyruq natijasini ko'rsatmaydi, shuning uchun skriptda muhim xabarlarni logga yozing yoki <code>&gt;&gt; fayl 2&gt;&amp;1</code> qo'shing. Skriptni qanday ishga tushirish va cron qatorini loyihaning <code>README</code> fayliga yozib qo'ying: boshqa odam (yoki yarim yildan keyingi o'zingiz) uni shu fayl bo'yicha tushuna olishi kerak.</p>"""

_L6_TEXT_RU = """<h3>Зачем скрипты</h3>
<p>Каждый раз вводить одну и ту же последовательность команд вручную — это путь к ошибкам. Вы собираете их в <strong>bash-скрипт</strong> и запускаете одной командой: анализ, резервная копия, деплой. В этом уроке мы напишем два настоящих скрипта: отчёт по логу и резервную копию. Первый файл курса <code>lab_setup.sh</code> был именно таким скриптом.</p>

<h3>Устройство скрипта</h3>
<pre><code>__LOGREPORT__</code></pre>
<ul>
  <li><strong>Shebang</strong> <code>#!/usr/bin/env bash</code> — первая строка: какой программой выполняется скрипт. Файл делается запускаемым через <code>chmod +x</code> (урок 4).</li>
  <li><strong>Аргументы</strong>: <code>$1</code> — первый аргумент, <code>$#</code> — их количество, <code>$0</code> — имя скрипта. <code>log=$1</code> создаёт переменную (вокруг знака равенства <em>нет пробелов</em>).</li>
  <li><strong>Получение значения</strong> <code>$(команда)</code>: результат команды попадает в переменную (<code>total=$(wc -l &lt; "$log")</code>).</li>
  <li><strong>Условия</strong>: <code>[[ $# -ne 1 ]]</code> (<code>-ne</code> не равно, <code>-f</code> файл существует, <code>-z</code> пусто), для чисел <code>(( errors &gt; 0 ))</code>. <code>if ...; then ...; fi</code>.</li>
  <li><strong>Код завершения</strong>: <code>exit 2</code> завершает скрипт с заданным кодом, <code>0</code> — успех, не ноль — ошибка. Код смотрят через <code>$?</code>. Мы договорились: 1 — файла нет, 2 — неверное использование, 3 — в логе есть ошибки 5xx. По этому коду другие программы (CI, мониторинг) принимают решение.</li>
  <li><strong>Поток ошибок</strong>: <code>echo "..." &gt;&amp;2</code> отправляет сообщение в stderr, не смешивая его с обычным результатом.</li>
</ul>

<h3>set -euo pipefail</h3>
<p>По умолчанию bash продолжает выполнять следующую строку даже после ошибки: это опасно. Строка <code>set -euo pipefail</code> в начале скрипта даёт три защиты:</p>
<ul>
  <li><code>-e</code> — если какая-то команда завершилась с ошибкой, скрипт сразу останавливается (в примере с <code>set -e</code> из сессии вывелось только <code>before</code>, а <code>after</code> нет).</li>
  <li><code>-u</code> — обращение к необъявленной переменной считается ошибкой (<code>unbound variable</code>). Это предотвращает катастрофы вроде <code>rm -rf "$DIR/"</code>, когда пустая <code>DIR</code> удаляла бы всю систему.</li>
  <li><code>-o pipefail</code> — если <em>любая</em> команда конвейера завершилась с ошибкой, ошибкой считается и весь конвейер (иначе учитывается только последняя).</li>
</ul>
<p>В этом режиме даже <code>grep</code> без совпадений возвращает код <code>1</code> и останавливает скрипт. Поэтому в скрипте написано <code>grep -c ... || true</code>: «если ничего не найдено, продолжай».</p>

<h3>Цепочки команд и работа со значениями</h3>
<ul>
  <li><code>a &amp;&amp; b</code> — <code>b</code> выполняется только если <code>a</code> успешна; <code>a || b</code> — <code>b</code> только если <code>a</code> завершилась ошибкой; <code>;</code> — подряд, независимо от результата.</li>
  <li><strong>Всегда берите переменную в кавычки</strong>: <code>"$log"</code>. Иначе имена с пробелами разобьются на несколько аргументов. Внутри <code>"..."</code> переменная раскрывается, а внутри <code>'...'</code> текст остаётся как есть.</li>
  <li>Цикл: <code>for f in *.py; do ...; done</code>. Функция: <code>greet() { echo "hi, $1"; }</code>. <code>${1:?сообщение}</code> останавливает скрипт с сообщением, если аргумента нет.</li>
</ul>

<h3>Скрипт резервной копии</h3>
<pre><code>__BACKUP__</code></pre>
<p><code>tar -czf архив.tar.gz папка</code> упаковывает папку в сжатый архив (<code>c</code> — create, <code>z</code> — gzip, <code>f</code> — имя файла), <code>tar -tzf</code> показывает содержимое архива (проверка без распаковки), <code>tar -xzf</code> распаковывает. <code>date +%F</code> выдаёт дату в виде <code>2026-10-13</code>: дата в имени архива упорядочивает резервные копии. <code>basename</code> и <code>dirname</code> разбивают путь на имя и папку.</p>

<h3>Сессия</h3>
<pre><code>__TRANSCRIPT__</code></pre>
<p>Прочитайте результат: отчёт нашёл <code>5xx = 5</code>, поэтому код завершения <code>3</code>, при вызове без аргументов — <code>2</code>, для несуществующего файла — <code>1</code>; а для <code>clean.log</code> без строк 500 — <code>0</code>. Скрипт резервной копии без второго аргумента остановился с сообщением <code>2: usage: ...</code> (<code>${2:?...}</code>), содержимое архива показано через <code>tar -tzf</code>. Дата (<code>2026-10-13</code>) у вас будет сегодняшняя.</p>

<h3>Расписание: cron</h3>
<p>Чтобы скрипт запускался сам каждую ночь, используется <strong>cron</strong>. <code>crontab -e</code> открывает расписание, <code>crontab -l</code> показывает его. В строке пять полей: минута, час, день месяца, месяц, день недели, затем команда. Строка ниже делает резервную копию каждый день в 03:00 (<code>*</code> — «любое»; в cron пишите путь <em>полностью</em>):</p>
<pre><code>__CRON__</code></pre>
<pre><code>__CMDCRON__</code></pre>
<p>Cron не показывает вывод команды, поэтому важные сообщения скрипта пишите в лог или добавьте <code>&gt;&gt; файл 2&gt;&amp;1</code>. Как запускать скрипт и строку cron запишите в файл <code>README</code> проекта: другой человек (или вы сами через полгода) должен суметь разобраться по нему.</p>"""

_L6_BLOCKS = dict(LOGREPORT=LOGREPORT_SH, BACKUP=BACKUP_SH, TRANSCRIPT=TRANSCRIPT_L6, CRON=CRON_LINE, CMDCRON=CMD_CRON)

LESSON_6 = {
    "order": 5,
    "title": "6-Bash skriptlar va avtomatlashtirish",
    "title_ru": "6-Bash-скрипты и автоматизация",
    "points_reward": 30,
    "text_content": _fill(_L6_TEXT_UZ, **_L6_BLOCKS),
    "text_content_ru": _fill(_L6_TEXT_RU, **_L6_BLOCKS),
    "code_content": LOGREPORT_SH,
    "code_content_ru": LOGREPORT_SH,
    "code_language": "bash",
    "sample": {
        "title": "Namuna: log hisoboti va zaxira nusxa skriptlari",
        "title_ru": "Пример: скрипты отчёта по логу и резервной копии",
        "description": "logreport.sh (chiqish kodlari 0/1/2/3), backup.sh (tar.gz), set -euo pipefail, cron qatori: haqiqiy Linux sessiyasi bilan.",
        "description_ru": "logreport.sh (коды завершения 0/1/2/3), backup.sh (tar.gz), set -euo pipefail, строка cron: вместе с сессией в настоящем Linux.",
        "sample_type": "code",
        "code_files": [
            {"filename": "logreport.sh", "language": "bash", "code": LOGREPORT_SH},
            {"filename": "backup.sh", "language": "bash", "code": BACKUP_SH},
            {"filename": "lab_setup.sh", "language": "bash", "code": LAB_SETUP},
            {"filename": "session.txt", "language": "text", "code": TRANSCRIPT_L6},
            {"filename": "crontab.txt", "language": "text", "code": CRON_LINE},
        ],
    },
    "task": {
        "task_title": "Loyiha: server holati va zaxira skripti",
        "task_title_ru": "Проект: скрипт состояния сервера и резервной копии",
        "task_description": "O'z loyihangiz uchun bitta bash skript yozing: u veb-server logini tahlil qilib qisqa hisobot beradi, loyiha papkasining zaxira nusxasini sana bilan arxivlaydi va xato bo'lsa tushunarli chiqish kodi bilan tugaydi. Skriptni cron orqali har kuni ishlaydigan qilib sozlang.",
        "task_description_ru": "Напишите для своего проекта один bash-скрипт: он анализирует лог веб-сервера и выдаёт краткий отчёт, архивирует папку проекта с датой в имени и завершается с понятным кодом при ошибке. Настройте запуск скрипта по расписанию через cron.",
        "task_requirements": (
            "1) Birinchi qatorda shebang #!/usr/bin/env bash, undan keyin set -euo pipefail; skript chmod +x bilan ishga tushiriladi. "
            "2) Argumentlar ($1 va $2): log fayl va loyiha papkasi. Argument yo'q bo'lsa foydalanish matni stderr'ga chiqadi va kod 2, fayl yoki papka mavjud bo'lmasa kod 1. "
            "3) Hisobot: so'rovlar soni (wc), statuslar bo'yicha jadval (awk, sort, uniq -c), eng ko'p so'ralgan 3 ta yo'l. "
            "4) Zaxira: tar -czf bilan sana (date +%F) qo'yilgan arxiv va tar -tzf bilan tekshirish. "
            "5) Logda 5xx xato bo'lsa skript hisobot va zaxiradan keyin kod 3 bilan tugaydi; xato bo'lmasa 0. "
            "6) cron qatori (crontab -e) va skriptni ishga tushirish buyrug'i README faylida yozilgan. "
            "7) Skript 1-darsdagi lab_setup.sh yaratgan logs/access.log va projects/shop da sinalgan: chiqish kodlari 0, 1, 2 va 3 ko'rsatilgan."
        ),
        "task_requirements_ru": (
            "1) В первой строке shebang #!/usr/bin/env bash, дальше set -euo pipefail; скрипт запускается после chmod +x. "
            "2) Аргументы ($1 и $2): файл лога и папка проекта. Если аргументов нет, текст использования идёт в stderr и код 2; если файла или папки нет, код 1. "
            "3) Отчёт: число запросов (wc), таблица по статусам (awk, sort, uniq -c), три самых частых пути. "
            "4) Резервная копия: tar -czf с датой (date +%F) в имени архива и проверка через tar -tzf. "
            "5) Если в логе есть ошибки 5xx, скрипт после отчёта и резервной копии завершается с кодом 3, иначе 0. "
            "6) Строка cron (crontab -e) и команда запуска скрипта записаны в файле README. "
            "7) Скрипт проверен на logs/access.log и projects/shop, созданных lab_setup.sh из урока 1: показаны коды завершения 0, 1, 2 и 3."
        ),
        "task_technologies": "Linux, Bash, cron",
        "task_deadline_days": 3,
    },
    "exercises": [
        {
            "title": "Skript boshidagi himoya", "title_ru": "Защита в начале скрипта",
            "description": "set -euo pipefail skriptni qanday himoya qiladi?",
            "description_ru": "Как set -euo pipefail защищает скрипт?",
            "exercise_type": "multiple_choice",
            "options": [
                "Xatodan keyin to'xtaydi, e'lon qilinmagan o'zgaruvchini xato deb hisoblaydi va quvurdagi xatoni ham ko'radi",
                "Skriptni tezroq ishlatadi",
                "Skriptga administrator huquqini beradi",
                "Skript natijasini faylga yozadi",
            ],
            "options_ru": [
                "Останавливается после ошибки, считает ошибкой необъявленную переменную и учитывает ошибку внутри конвейера",
                "Ускоряет выполнение скрипта",
                "Даёт скрипту права администратора",
                "Записывает результат скрипта в файл",
            ],
            "correct_answers": "A", "is_multiple_select": False,
            "hint": "Uch bayroq: e, u va pipefail: har biri o'z xatosini tutadi.",
            "hint_ru": "Три флага: e, u и pipefail: каждый ловит свой вид ошибок.",
            "explanation": "-e xatoda to'xtatadi, -u e'lon qilinmagan o'zgaruvchini xato qiladi, -o pipefail quvurdagi har qanday xatoni hisobga oladi.",
            "difficulty_level": "Medium", "points": 3,
        },
        {
            "title": "Oxirgi chiqish kodi", "title_ru": "Последний код завершения",
            "description": "Oxirgi bajarilgan buyruqning chiqish kodini beradigan maxsus o'zgaruvchi: echo ___",
            "description_ru": "Специальная переменная, содержащая код завершения последней команды: echo ___",
            "exercise_type": "fill_in_blank",
            "correct_answers": "$?",
            "hint": "Dollar va savol belgisi.",
            "hint_ru": "Знак доллара и вопросительный знак.",
            "explanation": "$? oxirgi buyruqning chiqish kodini saqlaydi: 0 muvaffaqiyat, noldan farqli xato.",
            "difficulty_level": "Easy", "points": 3,
        },
        {
            "title": "O'z skriptingizni rejalashtirish", "title_ru": "План вашего скрипта",
            "description": "Loyiha skriptingizni qaysi tartibda yozasiz va nimalarni tekshirasiz? O'z so'zingiz bilan yozing.",
            "description_ru": "В каком порядке вы напишете скрипт проекта и что проверите? Объясните своими словами.",
            "exercise_type": "text_input",
            "expected_answer": "Avval shebang va set -euo pipefail, so'ng argumentlarni tekshirish (kod 2 va 1). Keyin awk, sort va uniq bilan hisobot, tar -czf bilan sanali zaxira va tar -tzf bilan tekshirish, oxirida 5xx bo'lsa kod 3. Skriptni chmod +x bilan ishga tushirib, kodlarni 0, 1, 2 va 3 uchun echo $? bilan tekshiraman, cron qatorini README ga yozaman.",
            "hint": "Himoya, kirish tekshiruvi, asosiy ish, chiqish kodi, sinash.",
            "hint_ru": "Защита, проверка входных данных, основная работа, код завершения, проверка.",
            "explanation": "Yaxshi skript himoyadan (set -euo pipefail) va kirish tekshiruvidan boshlanadi, keyin ish bajariladi, oxirida aniq chiqish kodi qaytaradi; hammasi echo $? bilan sinaladi.",
            "difficulty_level": "Medium", "points": 4,
        },
    ],
}

LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]

# max_points = lesson points_reward + all exercise points (same rule as the other specs)
COURSE["max_points"] = sum(lesson["points_reward"] + sum(e["points"] for e in lesson["exercises"]) for lesson in LESSONS)
