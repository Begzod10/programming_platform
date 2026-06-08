"""Seed the "SQL va PostgreSQL Asoslari" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_sql_postgres_basics.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: Programming beginners / Python Asoslari graduates who need
real SQL skills before touching ORM. Builds from SELECT to JOIN to schema
design to indexes to window functions. Language: Uzbek content with Russian
section labels. Each lesson uses the WIN-FIRST shape: BLOKA 1/2/3 hands-on
hook -> deliberate-error -> theory -> "Bu darsdan keyin siz bilasizki" wrap.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import engine, AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "SQL va PostgreSQL Asoslari",
    "description": (
        "Ma'lumotlar bazasi bilan ishlashni boshlovchilar uchun: PostgreSQL'da "
        "SELECT, WHERE, JOIN, GROUP BY, indekslar, sxema dizayni va oyna "
        "funksiyalari. ORM oldida real SQL. Har bir modul oxirida loyiha. "
        "Yakuniy capstone — E-commerce tahlil tizimi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 5,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson content placeholders — filled in by subsequent edits.
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>Birinchi SELECT — ma'lumotni o'qishni boshlaymiz</h2>

<pre class="mermaid">
flowchart LR
    DB[("PostgreSQL DB")] --> T1["jadval: talabalar"]
    DB --> T2["jadval: fanlar"]
    DB --> T3["jadval: baholar"]
    T1 -->|SELECT * FROM talabalar| OUT["qatorlar"]
</pre>

<p><strong>SQL</strong> — bu ma'lumotlar bazasi bilan gaplashish tili. Sizning Python kodingiz "men buni qil" deydi (imperative). SQL esa "menga shu ma'lumotni ber" deydi (declarative). Ichkarisida nima sodir bo'lishi — bu PostgreSQL'ning ishi.</p>

<p>Ma'lumotlar bazasi (DB) ichida <strong>jadvallar</strong> bor. Har bir jadval — Excel varag'iga o'xshaydi: <strong>ustunlar</strong> (column) va <strong>qatorlar</strong> (row).</p>

<h3>🏆 5 daqiqada g'alaba</h3>
<p>pgAdmin yoki <code>psql</code> ochib quyidagi misollarni sinab ko'ring. Birinchi galda <code>talabalar</code> jadvali allaqachon to'ldirilgan deb tasavvur qiling.</p>

<h4>BLOKA 1 — eng oddiy so'rov</h4>
<pre><code>-- Jami qancha qator bor?
SELECT COUNT(*) FROM talabalar;
-- count: 6

-- Barcha ustun, barcha qator
SELECT * FROM talabalar;
-- id | ism   | familiya  | yosh | ball | sinf
-- 1  | Olim  | Karimov   |  17  |  87  | 11-A
-- 2  | Vali  | Toshev    |  16  |  72  | 10-B
-- ...</code></pre>

<h4>BLOKA 2 — faqat kerakli ustunlar</h4>
<pre><code>-- Faqat ism va ball
SELECT ism, ball FROM talabalar;

-- Tartibni almashtirish ham mumkin
SELECT ball, ism FROM talabalar;</code></pre>

<p>💡 <code>*</code> — "barcha ustun" degani. Production'da uni juda <em>kam</em> ishlatamiz: kerakli ustunlarni aniq sanab berish tezroq va xavfsizroq.</p>

<h4>BLOKA 3 — ustunga yangi nom berish (AS)</h4>
<pre><code>SELECT
    ism AS talaba_ismi,
    ball AS jami_ball
FROM talabalar;

-- talaba_ismi | jami_ball
-- Olim        |    87
-- Vali        |    72</code></pre>

<p><code>AS</code> — ustunga vaqtinchalik nom (alias). Bu hisobotlarda chiroyli ko'rinish uchun ham, keyinroq murakkab so'rovlarda esa zaruriy. <code>AS</code> so'zini tushirib qoldirsangiz ham ishlaydi (<code>ism talaba_ismi</code>), lekin yozish — yaxshi odat.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>SELECT ism, fmilya FROM talabalar;</code></pre>
<p><strong>Natija:</strong> <code>ERROR: column "fmilya" does not exist</code>. PostgreSQL ustun nomini bilmagan vaqtda darhol xato qaytaradi. Bu — yaxshi xato: kompilyatsiya vaqtidagi xato production'da uzilishdan ko'ra million marta yaxshiroq.</p>

<p>SQL kalit so'zlari (<code>SELECT</code>, <code>FROM</code>) katta-kichik harfga sezgir emas, lekin <strong>ustun va jadval nomlari</strong> sezgir bo'lishi mumkin (yaratilganda qanday yozilgan bo'lsa, shunday).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. SQL so'rovining anatomiyasi</h4>
<pre><code>SELECT &lt;ustunlar&gt;
FROM   &lt;jadval&gt;
WHERE  &lt;shart&gt;;       -- 2-darsda
</code></pre>
<ul>
<li><strong>SELECT</strong> — qaysi ustunlarni ko'rsataylik</li>
<li><strong>FROM</strong> — qaysi jadvaldan</li>
<li><strong>;</strong> (nuqta-vergul) — so'rov tugadi. Bir nechta so'rovni ketma-ket yozsangiz, har birini ; bilan ajrating</li>
</ul>

<h4>2. Database, schema, table — qaysi qaysi?</h4>
<table>
<tr><th>Tushuncha</th><th>Misol</th><th>Tushuntirish</th></tr>
<tr><td>Cluster</td><td>localhost:5432</td><td>PostgreSQL server</td></tr>
<tr><td>Database</td><td>maktab_db</td><td>Bir server ichida ko'p DB bo'lishi mumkin</td></tr>
<tr><td>Schema</td><td>public</td><td>DB ichida jadvallar guruhi (default: public)</td></tr>
<tr><td>Table</td><td>talabalar</td><td>Asl ma'lumot — qatorlar va ustunlar</td></tr>
</table>

<h4>3. Ma'lumot turlari (asoslari)</h4>
<table>
<tr><th>Tur</th><th>Misol</th><th>Qachon</th></tr>
<tr><td><code>INTEGER</code></td><td>17, -42</td><td>butun sonlar</td></tr>
<tr><td><code>NUMERIC(10,2)</code></td><td>1500.50</td><td>aniq kasr (pul!)</td></tr>
<tr><td><code>VARCHAR(50)</code></td><td>'Olim'</td><td>belgilangan uzunlikdagi matn</td></tr>
<tr><td><code>TEXT</code></td><td>'uzun matn...'</td><td>chegarasiz matn</td></tr>
<tr><td><code>BOOLEAN</code></td><td>TRUE, FALSE</td><td>ha/yo'q</td></tr>
<tr><td><code>DATE</code></td><td>'2026-06-08'</td><td>sana</td></tr>
<tr><td><code>TIMESTAMP</code></td><td>'2026-06-08 14:30:00'</td><td>sana + vaqt</td></tr>
</table>

<h4>4. Matn (string) literallari</h4>
<p>SQL'da matnni <strong>bitta tirnoq</strong> ichida yozasiz (Python'dagi <code>"..."</code> emas):</p>
<pre><code>SELECT * FROM talabalar WHERE ism = 'Olim';
-- 'Olim' — bu string

-- Tirnoqni ichida ishlatish — ikkita tirnoq
SELECT 'O''zbekiston' AS davlat;
-- O'zbekiston</code></pre>

<h4>5. Komment</h4>
<pre><code>-- Bir qatorli komment
/* Ko'p qatorli
   komment */
SELECT * FROM talabalar;  -- qator oxiri ham bo'lishi mumkin</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>SELECT &lt;ustunlar&gt; FROM &lt;jadval&gt;;</code> — har SQL so'rovning asosiy shakli</li>
<li>✅ <code>*</code> — barcha ustun, lekin production'da kam ishlatiladi</li>
<li>✅ <code>AS</code> — ustunga alias berish</li>
<li>✅ Matn literali — bitta tirnoq <code>'matn'</code></li>
<li>✅ Komment — <code>--</code> bir qator, <code>/* */</code> ko'p qator</li>
<li>✅ Asosiy ma'lumot turlari: INTEGER, VARCHAR, TEXT, NUMERIC, BOOLEAN, DATE</li>
</ul>
"""

L1_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 1: Birinchi SELECT
-- Maqsad: bog'lanish, jadval ko'rish, ustun tanlash
-- ═══════════════════════════════════════════════════════════════════════

-- Bizning misol jadval: talabalar
-- Quyidagi 2 ta blokni psql / pgAdmin'ga ko'chiring va ishga tushiring
-- ─────────────────────────────────────────────────────────────────────

-- 1) Jadvalni yaratamiz (faqat birinchi marta)
CREATE TABLE IF NOT EXISTS talabalar (
    id       SERIAL PRIMARY KEY,
    ism      VARCHAR(50) NOT NULL,
    familiya VARCHAR(50) NOT NULL,
    yosh     INTEGER,
    ball     INTEGER,
    sinf     VARCHAR(10)
);

-- 2) Ma'lumot to'ldiramiz (faqat birinchi marta)
INSERT INTO talabalar (ism, familiya, yosh, ball, sinf) VALUES
    ('Olim',   'Karimov',   17, 87, '11-A'),
    ('Vali',   'Toshev',    16, 72, '10-B'),
    ('Karim',  'Yusupov',   17, 91, '11-A'),
    ('Dilshod','Saidov',    15, 64, '9-B'),
    ('Nigora', 'Rahimova',  16, 95, '10-A'),
    ('Salim',  'Norqulov',  17, 58, '11-B');

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — eng oddiy so'rovlar
-- ─────────────────────────────────────────────────────────────────────

-- Jami qancha qator?
SELECT COUNT(*) FROM talabalar;

-- Barcha ustun, barcha qator
SELECT * FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — kerakli ustunlar
-- ─────────────────────────────────────────────────────────────────────

SELECT ism, ball FROM talabalar;

SELECT ball, ism FROM talabalar;  -- tartib o'zgarganini ko'ring

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — alias (AS)
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ism      AS talaba_ismi,
    ball     AS jami_ball,
    sinf     AS guruh
FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — hisoblangan ustun
-- ─────────────────────────────────────────────────────────────────────

-- Hisoblash bevosita SELECT ichida
SELECT
    ism,
    ball,
    ball + 5 AS bonusli_ball,
    yosh * 12 AS yoshi_oyda
FROM talabalar;

-- Matnlarni birlashtirish — || operatori
SELECT ism || ' ' || familiya AS toliq_ism FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — turli ma'lumot bilan tanishish
-- ─────────────────────────────────────────────────────────────────────

SELECT 42 AS son,
       'salom' AS matn,
       TRUE AS bayroq,
       CURRENT_DATE AS bugun;

-- O'zbekcha matnda apostrofni ikkilab yozamiz
SELECT 'O''zbekiston' AS davlat;
"""
L2_TEXT = """\
<h2>WHERE — kerakli qatorlarni topish</h2>

<pre class="mermaid">
flowchart LR
    ALL["barcha qatorlar"] -->|WHERE shart| FILT["shartga to'g'ri kelganlar"]
    FILT --> OUT["natija"]
</pre>

<p>1-darsda biz <em>ustun</em> tanlashni o'rgandik. Endi <strong>qator</strong> tanlash navbati. <code>WHERE</code> — SQL'ning eng ko'p ishlatiladigan kalit so'zi. Sizning har bir sahifa "mahsulotlar narxi 1000 dan ortiq" yoki "buyurtmalar oxirgi 7 kun ichidagi" — barchasi WHERE bilan ishlaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>
<p>1-darsdagi <code>talabalar</code> jadvali davom etadi.</p>

<h4>BLOKA 1 — taqqoslash operatorlari</h4>
<pre><code>-- Ball 80 dan katta yoki teng
SELECT ism, ball FROM talabalar WHERE ball &gt;= 80;
-- Olim   87
-- Karim  91
-- Nigora 95

-- Yosh aniq 17
SELECT * FROM talabalar WHERE yosh = 17;

-- Teng emas
SELECT * FROM talabalar WHERE sinf &lt;&gt; '11-A';   -- yoki  != '11-A'</code></pre>

<h4>BLOKA 2 — AND, OR, NOT</h4>
<pre><code>-- Ham 17 yosh, ham 80+ ball
SELECT ism, ball FROM talabalar
WHERE yosh = 17 AND ball &gt;= 80;

-- Yoki 9-B sinfda, yoki ball 90+
SELECT ism, sinf, ball FROM talabalar
WHERE sinf = '9-B' OR ball &gt;= 90;

-- 11-A da BO'LMAGAN talabalar
SELECT ism FROM talabalar WHERE NOT sinf = '11-A';
-- yoki sodda:  WHERE sinf &lt;&gt; '11-A';</code></pre>

<h4>BLOKA 3 — BETWEEN, IN, LIKE</h4>
<pre><code>-- Ball 70 dan 90 gacha (chetlari kiradi)
SELECT * FROM talabalar WHERE ball BETWEEN 70 AND 90;

-- Sinf — ro'yxatdan biri
SELECT * FROM talabalar WHERE sinf IN ('11-A', '10-A');

-- Ism 'K' bilan boshlanadi
SELECT * FROM talabalar WHERE ism LIKE 'K%';
-- Karim, ...

-- Ism ichida 'li' bor
SELECT * FROM talabalar WHERE ism LIKE '%li%';
-- Olim, Vali, Salim</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>SELECT * FROM talabalar WHERE familiya = NULL;</code></pre>
<p><strong>Natija:</strong> hech narsa qaytmaydi. <code>NULL</code> — bu "noma'lum qiymat", va u <em>hech narsaga teng emas</em> — hatto o'ziga ham. To'g'ri yo'l: <code>IS NULL</code> yoki <code>IS NOT NULL</code>.</p>
<pre><code>-- TO'G'RI
SELECT * FROM talabalar WHERE familiya IS NULL;
SELECT * FROM talabalar WHERE familiya IS NOT NULL;</code></pre>

<p>Bu — SQL'da eng ko'p uchraydigan "tinch xato": kod xato chiqarmaydi, lekin natija noto'g'ri.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Taqqoslash operatorlari</h4>
<table>
<tr><th>Operator</th><th>Ma'no</th><th>Misol</th></tr>
<tr><td><code>=</code></td><td>teng</td><td><code>ball = 87</code></td></tr>
<tr><td><code>&lt;&gt;</code> yoki <code>!=</code></td><td>teng emas</td><td><code>sinf &lt;&gt; '11-A'</code></td></tr>
<tr><td><code>&lt;</code> <code>&gt;</code></td><td>kichik, katta</td><td><code>yosh &lt; 18</code></td></tr>
<tr><td><code>&lt;=</code> <code>&gt;=</code></td><td>kichik/katta yoki teng</td><td><code>ball &gt;= 80</code></td></tr>
</table>

<h4>2. Mantiqiy birikmalar</h4>
<table>
<tr><th>Operator</th><th>Qachon TRUE</th><th>Prioritet</th></tr>
<tr><td><code>AND</code></td><td>Ikkala shart TRUE</td><td>yuqori</td></tr>
<tr><td><code>OR</code></td><td>Kamida bittasi TRUE</td><td>past</td></tr>
<tr><td><code>NOT</code></td><td>Shart FALSE</td><td>eng yuqori</td></tr>
</table>

<p>⚠️ AND/OR aralashganda <strong>qavslar</strong> qo'ying — xato qilish oson:</p>
<pre><code>-- Yomon (yashirin xato)
WHERE sinf = '11-A' OR sinf = '11-B' AND ball &gt;= 80
-- Bu aslida: 11-A IS THIS, OR (11-B AND ball&gt;=80) — siz xohlagan emas

-- Yaxshi
WHERE (sinf = '11-A' OR sinf = '11-B') AND ball &gt;= 80</code></pre>

<h4>3. BETWEEN, IN, LIKE — qulay qisqartmalar</h4>
<table>
<tr><th>So'rov</th><th>Teng (long form)</th></tr>
<tr><td><code>ball BETWEEN 70 AND 90</code></td><td><code>ball &gt;= 70 AND ball &lt;= 90</code></td></tr>
<tr><td><code>sinf IN ('11-A','11-B')</code></td><td><code>sinf='11-A' OR sinf='11-B'</code></td></tr>
<tr><td><code>ism LIKE 'K%'</code></td><td>K bilan boshlangan</td></tr>
<tr><td><code>ism LIKE '%a'</code></td><td>a bilan tugagan</td></tr>
<tr><td><code>ism LIKE '_a%'</code></td><td>2-harfi a (bitta belgi)</td></tr>
</table>

<h4>4. NULL — alohida olamda</h4>
<p><code>NULL</code> "noma'lum" degani. Ushbu qoidalarni yodlang:</p>
<ul>
<li><code>NULL = NULL</code> → NULL (TRUE emas!)</li>
<li><code>NULL = 5</code> → NULL</li>
<li><code>NULL AND TRUE</code> → NULL</li>
<li><code>NULL OR TRUE</code> → TRUE</li>
</ul>
<p>Tekshirish faqat <code>IS NULL</code> / <code>IS NOT NULL</code> orqali.</p>

<h4>5. Katta-kichik harf va LIKE</h4>
<p><code>LIKE</code> — katta-kichik harfga <strong>sezgir</strong>. Sezmaslik uchun <code>ILIKE</code>:</p>
<pre><code>SELECT * FROM talabalar WHERE ism LIKE 'o%';   -- bo'sh (Olim kapital)
SELECT * FROM talabalar WHERE ism ILIKE 'o%';  -- Olim chiqadi</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>WHERE</code> + taqqoslash (<code>= &lt;&gt; &lt; &gt; &lt;= &gt;=</code>)</li>
<li>✅ <code>AND OR NOT</code> bilan murakkab shartlar (qavs qo'ying!)</li>
<li>✅ <code>BETWEEN ... AND ...</code>, <code>IN (...)</code>, <code>LIKE '%...%'</code></li>
<li>✅ NULL bilan ishlash: <code>IS NULL</code> / <code>IS NOT NULL</code></li>
<li>✅ <code>ILIKE</code> — katta-kichik harfga befarq qidirish</li>
</ul>
"""

L2_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 2: WHERE — filterlash
-- Maqsad: kerakli qatorlarni topish
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — taqqoslash operatorlari
-- ─────────────────────────────────────────────────────────────────────

-- 80 dan yuqori ball
SELECT ism, ball FROM talabalar WHERE ball >= 80;

-- Aniq yosh
SELECT * FROM talabalar WHERE yosh = 17;

-- Teng emas
SELECT * FROM talabalar WHERE sinf <> '11-A';
-- yoki:
SELECT * FROM talabalar WHERE sinf != '11-A';

-- Hisoblangan shart
SELECT ism, ball * 1.1 AS bonusli FROM talabalar
WHERE ball * 1.1 > 90;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — AND, OR, NOT
-- ─────────────────────────────────────────────────────────────────────

-- Ham yoshi 17, ham bali 80+
SELECT ism, ball FROM talabalar
WHERE yosh = 17 AND ball >= 80;

-- Yoki ... yoki
SELECT ism, sinf FROM talabalar
WHERE sinf = '9-B' OR ball >= 90;

-- NOT bilan inkor
SELECT ism FROM talabalar WHERE NOT sinf = '11-A';

-- Qavslar muhim
SELECT ism, sinf, ball FROM talabalar
WHERE (sinf = '11-A' OR sinf = '11-B') AND ball >= 80;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — BETWEEN, IN, LIKE
-- ─────────────────────────────────────────────────────────────────────

-- Diapazon
SELECT * FROM talabalar WHERE ball BETWEEN 70 AND 90;
SELECT * FROM talabalar WHERE yosh BETWEEN 15 AND 17;

-- Ro'yxatdan biri
SELECT * FROM talabalar WHERE sinf IN ('11-A', '10-A', '9-B');
SELECT * FROM talabalar WHERE id IN (1, 3, 5);

-- LIKE — pattern qidirish
SELECT * FROM talabalar WHERE ism LIKE 'K%';   -- K bilan boshlangan
SELECT * FROM talabalar WHERE ism LIKE '%im';  -- im bilan tugagan
SELECT * FROM talabalar WHERE ism LIKE '%a%';  -- ichida a bor
SELECT * FROM talabalar WHERE ism LIKE '_a%';  -- 2-harfi a

-- ILIKE — katta-kichik harfga befarq
SELECT * FROM talabalar WHERE ism ILIKE 'o%';

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — NULL bilan ishlash
-- ─────────────────────────────────────────────────────────────────────

-- = NULL ishlamaydi
SELECT * FROM talabalar WHERE familiya = NULL;    -- BO'SH

-- To'g'ri yo'l
SELECT * FROM talabalar WHERE familiya IS NULL;
SELECT * FROM talabalar WHERE familiya IS NOT NULL;

-- COALESCE — agar NULL bo'lsa, default qiymat
SELECT ism, COALESCE(familiya, '(noma''lum)') AS familiya FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — birga ishlatish
-- ─────────────────────────────────────────────────────────────────────

-- Murakkab real misol: 11-sinfdagi a'lochilar (90+ ball)
SELECT
    ism || ' ' || familiya AS toliq_ism,
    sinf,
    ball
FROM talabalar
WHERE sinf LIKE '11-%' AND ball >= 90;
"""
L3_TEXT = """\
<h2>ORDER BY, LIMIT va DISTINCT — tartiblash, sahifalash, takrorsiz</h2>

<pre class="mermaid">
flowchart LR
    F["filterlangan qatorlar"] -->|ORDER BY ball DESC| S["tartiblangan"]
    S -->|LIMIT 5 OFFSET 0| P["sahifa 1"]
    S -->|LIMIT 5 OFFSET 5| P2["sahifa 2"]
</pre>

<p>WHERE ma'lumotni <em>filterladi</em>. Endi kerak: <strong>tartiblash</strong> (top-N), <strong>cheklash</strong> (sahifalash), va <strong>takrorsiz</strong> qiymatlar. Bularsiz hech qaysi ro'yxat sahifasi ishlamaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — ORDER BY</h4>
<pre><code>-- Ball bo'yicha pasayuvchi tartibda (kattalardan kichiklarga)
SELECT ism, ball FROM talabalar
ORDER BY ball DESC;
-- Nigora 95, Karim 91, Olim 87, ...

-- O'suvchi (default — ASC ham yozsa bo'ladi)
SELECT ism, yosh FROM talabalar
ORDER BY yosh ASC;

-- Bir nechta ustun bo'yicha
SELECT ism, sinf, ball FROM talabalar
ORDER BY sinf ASC, ball DESC;
-- Sinf alifbo bo'yicha, har sinf ichida — ball kamayuvchi</code></pre>

<h4>BLOKA 2 — LIMIT va OFFSET</h4>
<pre><code>-- TOP-3 talabalar
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 3;

-- Sahifalash: sahifa 2, har sahifada 2 ta
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 2 OFFSET 2;
-- 3 va 4-o'rindagilar</code></pre>

<p>Diqqat: <strong>LIMIT'siz natija tartibi kafolatlanmaydi</strong>. Doim <code>ORDER BY</code> bilan birga ishlating.</p>

<h4>BLOKA 3 — DISTINCT</h4>
<pre><code>-- Qaysi sinflar bor (takrorsiz)
SELECT DISTINCT sinf FROM talabalar;
-- 11-A, 10-B, 11-B, 10-A, 9-B

-- Bir nechta ustun bo'yicha takrorsiz juftliklar
SELECT DISTINCT sinf, yosh FROM talabalar;
-- (11-A, 17), (10-B, 16), ...

-- COUNT bilan birga
SELECT COUNT(DISTINCT sinf) FROM talabalar;
-- 5</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>-- Bu so'rov xato yoki tasodifiy natija beradi?
SELECT * FROM talabalar LIMIT 3;</code></pre>
<p><strong>Natija:</strong> Xato chiqarmaydi, lekin <em>qaysi 3 ta qator</em> qaytishi — kafolatsiz. PostgreSQL har gal bir xil natija qaytarmasligi mumkin (jadval o'sgan sayin). Bu — eng ko'p uchraydigan production xato.</p>

<p>Qoidasi: <strong>LIMIT bo'lsa, ORDER BY ham bo'lsin</strong>. Aks holda siz "tasodifiy 3 ta" so'rab olganingizdek bo'ladi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. ORDER BY — tartiblash sxemasi</h4>
<table>
<tr><th>Kalit</th><th>Ma'no</th></tr>
<tr><td><code>ASC</code></td><td>o'suvchi (default — yozish shart emas)</td></tr>
<tr><td><code>DESC</code></td><td>pasayuvchi</td></tr>
<tr><td><code>NULLS FIRST</code></td><td>NULL'lar boshida</td></tr>
<tr><td><code>NULLS LAST</code></td><td>NULL'lar oxirida</td></tr>
</table>
<pre><code>-- NULL'larni oxiriga itarish
SELECT * FROM talabalar
ORDER BY familiya ASC NULLS LAST;</code></pre>

<h4>2. SQL ijro tartibi (asoslari)</h4>
<p>Yozish tartibi: <code>SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT ...</code><br/>
Bajarilish tartibi esa boshqacha:</p>
<ol>
<li><strong>FROM</strong> — qaysi jadval</li>
<li><strong>WHERE</strong> — qatorlarni filterlash</li>
<li><strong>SELECT</strong> — kerakli ustunlarni tanlash</li>
<li><strong>ORDER BY</strong> — tartiblash</li>
<li><strong>LIMIT/OFFSET</strong> — kesish</li>
</ol>

<p>Shu sababli: <code>ORDER BY</code> ichida <code>SELECT</code> ichidagi alias'larga murojaat qilish mumkin (chunki SELECT oldin bajariladi):</p>
<pre><code>SELECT ism, ball * 1.1 AS bonusli_ball
FROM talabalar
ORDER BY bonusli_ball DESC;   -- alias ishlaydi</code></pre>

<h4>3. LIMIT + OFFSET — sahifalash matematikasi</h4>
<p>Frontend page=N, per_page=M bo'lsa:</p>
<pre><code>LIMIT &lt;per_page&gt;
OFFSET &lt;per_page&gt; * (&lt;page&gt; - 1)</code></pre>
<table>
<tr><th>Sahifa</th><th>LIMIT</th><th>OFFSET</th></tr>
<tr><td>1</td><td>10</td><td>0</td></tr>
<tr><td>2</td><td>10</td><td>10</td></tr>
<tr><td>3</td><td>10</td><td>20</td></tr>
</table>

<p>⚠️ Katta jadvallarda yuqori OFFSET sekin: DB har safar avvalgi qatorlarni o'qib chiqishi kerak. 9-darsda alternativni (keyset pagination) ko'rib chiqamiz.</p>

<h4>4. DISTINCT — takrorsiz, lekin tejamkor emas</h4>
<p>DISTINCT to'liq natijani saralab takrorlarni olib tashlaydi — bu qimmat operatsiya. Agar siz "har sinfdan bittadan misol" izlasangiz, keyinroq (5-darsda) <code>GROUP BY</code> yoki window <code>DISTINCT ON</code> aniqroq bo'ladi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>ORDER BY ustun ASC/DESC</code></li>
<li>✅ Bir nechta ustun bilan tartiblash: <code>ORDER BY a ASC, b DESC</code></li>
<li>✅ <code>LIMIT N OFFSET M</code> sahifalash uchun</li>
<li>✅ <strong>LIMIT bo'lsa, ORDER BY ham bo'lsin</strong></li>
<li>✅ <code>DISTINCT</code> takrorsiz qatorlar</li>
<li>✅ SQL ijro tartibi: FROM → WHERE → SELECT → ORDER BY → LIMIT</li>
</ul>
"""

L3_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 3: ORDER BY, LIMIT, DISTINCT
-- Maqsad: tartiblash, top-N, sahifalash, takrorsiz qiymatlar
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — ORDER BY
-- ─────────────────────────────────────────────────────────────────────

-- Ball bo'yicha kamayuvchi (top -> bottom)
SELECT ism, ball FROM talabalar
ORDER BY ball DESC;

-- O'suvchi (default)
SELECT ism, yosh FROM talabalar
ORDER BY yosh;

-- Bir nechta ustun
SELECT ism, sinf, ball FROM talabalar
ORDER BY sinf ASC, ball DESC;

-- Alias bo'yicha tartiblash
SELECT ism, ball * 1.1 AS bonusli FROM talabalar
ORDER BY bonusli DESC;

-- Ustun raqami bo'yicha (kichik so'rovlarda qulay, lekin tavsiya emas)
SELECT ism, ball FROM talabalar
ORDER BY 2 DESC;   -- 2-ustun = ball

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — LIMIT va OFFSET
-- ─────────────────────────────────────────────────────────────────────

-- TOP-3 a'lochi
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 3;

-- Eng yosh 2 ta talaba
SELECT ism, yosh FROM talabalar
ORDER BY yosh ASC
LIMIT 2;

-- Sahifa 2 (2 ta yozuv har sahifada)
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 2 OFFSET 2;

-- Sahifa 3
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 2 OFFSET 4;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — DISTINCT
-- ─────────────────────────────────────────────────────────────────────

-- Qaysi sinflar bor
SELECT DISTINCT sinf FROM talabalar;

-- Sinf + yosh juftliklari (takrorsiz)
SELECT DISTINCT sinf, yosh FROM talabalar
ORDER BY sinf, yosh;

-- Qancha har xil sinf bor?
SELECT COUNT(DISTINCT sinf) AS sinflar_soni FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — NULL bilan tartiblash
-- ─────────────────────────────────────────────────────────────────────

-- Standart: ASC'da NULL oxirida, DESC'da NULL boshida
SELECT ism, familiya FROM talabalar
ORDER BY familiya ASC NULLS LAST;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — birga ishlatish (real misol)
-- ─────────────────────────────────────────────────────────────────────

-- 11-sinf top-5 ball
SELECT ism, sinf, ball FROM talabalar
WHERE sinf LIKE '11-%'
ORDER BY ball DESC
LIMIT 5;

-- Faqat unikal yoshlar, pasayuvchi
SELECT DISTINCT yosh FROM talabalar
ORDER BY yosh DESC;
"""
R1_TEXT = """\
<h2>R1 — Modul 1 takrorlash: Talabalar ro'yxati</h2>

<p>Birinchi 3 ta darsda o'rgangan har bir narsamizni — <code>SELECT</code>, <code>WHERE</code>, <code>ORDER BY</code>, <code>LIMIT</code>, <code>DISTINCT</code> — bitta amaliy senariy ichida birlashtiramiz.</p>

<p>Tasavvur qiling: sizdan maktab ma'muriyati so'radi — "Birinchi semestr yakuni bo'yicha turli kesimda hisobotlar tuzib bering". Vaqt — 30 daqiqa.</p>

<h3>Kirish ma'lumoti</h3>
<p>1-darsda yaratgan <code>talabalar</code> jadvali. Bunda ma'lumotni boyitamiz — yangi ustun (<code>maktab_kunlari</code>) qo'shamiz. Quyidagi kodni ishga tushiring (faqat birinchi marta).</p>

<pre><code>ALTER TABLE talabalar ADD COLUMN IF NOT EXISTS maktab_kunlari INTEGER DEFAULT 180;
UPDATE talabalar SET maktab_kunlari = 175 WHERE id = 2;
UPDATE talabalar SET maktab_kunlari = 160 WHERE id = 4;
UPDATE talabalar SET maktab_kunlari = 178 WHERE id = 6;</code></pre>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Top a'lochilar</h4>
<p>Ball bo'yicha eng yuqori 3 ta talabani toping. Faqat <code>toliq_ism</code> (ism + familiya) va <code>ball</code> ko'rinsin.</p>

<h4>Vazifa 2 — Filterlangan ro'yxat</h4>
<p>11-sinflarning (11-A va 11-B) 80+ balli talabalarini ball bo'yicha pasayuvchi tartibda ko'rsating.</p>

<h4>Vazifa 3 — Sinflar ro'yxati</h4>
<p>Maktabda qaysi sinflar borligini takrorsiz ro'yxat ko'rinishida ko'rsating.</p>

<h4>Vazifa 4 — Yo'qotgan kunlar</h4>
<p>180 dan kam maktab kuni borgan talabalarni toping. Eng kam kelganlardan tartiblang.</p>

<h4>Vazifa 5 — Eng yosh va eng katta yoshli</h4>
<p>Bitta so'rovda — eng yosh va eng katta yoshli talabaning ismini topib bering (TIP: <code>UNION ALL</code> yoki <code>ORDER BY ... LIMIT 1</code> ni 2 marta).</p>

<h4>Vazifa 6 — Sahifalash</h4>
<p>Talabalarni ball bo'yicha pasayuvchi tartibda 2-sahifani (har sahifada 2 ta yozuv) qaytaring.</p>

<h3>🐛 Ataylab qiyin</h3>
<p>Quyidagi xato so'rov nima uchun ishlamaydi va qanday tuzatish kerak?</p>
<pre><code>SELECT ism, ball + 5 AS yangi_ball
FROM talabalar
WHERE yangi_ball &gt; 80;</code></pre>

<h3>Yechimlar (avval o'zingiz urinib ko'ring!)</h3>

<details>
<summary>Vazifa 1 — yechim</summary>
<pre><code>SELECT ism || ' ' || familiya AS toliq_ism, ball
FROM talabalar
ORDER BY ball DESC
LIMIT 3;</code></pre>
</details>

<details>
<summary>Vazifa 2 — yechim</summary>
<pre><code>SELECT ism, sinf, ball
FROM talabalar
WHERE sinf IN ('11-A', '11-B') AND ball &gt;= 80
ORDER BY ball DESC;
-- yoki LIKE bilan:
WHERE sinf LIKE '11-%' AND ball &gt;= 80</code></pre>
</details>

<details>
<summary>Vazifa 3 — yechim</summary>
<pre><code>SELECT DISTINCT sinf FROM talabalar ORDER BY sinf;</code></pre>
</details>

<details>
<summary>Vazifa 4 — yechim</summary>
<pre><code>SELECT ism, maktab_kunlari
FROM talabalar
WHERE maktab_kunlari &lt; 180
ORDER BY maktab_kunlari ASC;</code></pre>
</details>

<details>
<summary>Vazifa 5 — yechim</summary>
<pre><code>(SELECT ism, yosh, 'eng_yosh' AS toifa FROM talabalar ORDER BY yosh ASC LIMIT 1)
UNION ALL
(SELECT ism, yosh, 'eng_katta' FROM talabalar ORDER BY yosh DESC LIMIT 1);</code></pre>
</details>

<details>
<summary>Vazifa 6 — yechim</summary>
<pre><code>SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 2 OFFSET 2;</code></pre>
</details>

<details>
<summary>Ataylab qiyin — javob</summary>
<p><code>WHERE</code> da alias (<code>yangi_ball</code>) <strong>ishlamaydi</strong>, chunki <code>WHERE</code> <code>SELECT</code> dan oldin ijro etiladi — alias hali yo'q. Tuzatish:</p>
<pre><code>-- A: ifoda takrorlash
SELECT ism, ball + 5 AS yangi_ball FROM talabalar
WHERE ball + 5 &gt; 80;

-- B: subquery
SELECT * FROM (
    SELECT ism, ball + 5 AS yangi_ball FROM talabalar
) sq
WHERE yangi_ball &gt; 80;

-- ORDER BY da esa alias ishlaydi (chunki u SELECT'dan keyin)</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 1 ning barcha tushunchalarini bitta amaliy senariyda birlashtirish</li>
<li>✅ Real hisobotlar qanday yoziladi</li>
<li>✅ WHERE'da alias ishlamasligining sababi (ijro tartibi)</li>
</ul>
"""

R1_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- REVISION 1: Talabalar ro'yxati
-- Modul 1 hammasi birga: SELECT, WHERE, ORDER BY, LIMIT, DISTINCT
-- ═══════════════════════════════════════════════════════════════════════

-- Tayyorgarlik (faqat birinchi marta)
ALTER TABLE talabalar
    ADD COLUMN IF NOT EXISTS maktab_kunlari INTEGER DEFAULT 180;

UPDATE talabalar SET maktab_kunlari = 175 WHERE id = 2;
UPDATE talabalar SET maktab_kunlari = 160 WHERE id = 4;
UPDATE talabalar SET maktab_kunlari = 178 WHERE id = 6;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 1: TOP-3 a'lochi
-- ─────────────────────────────────────────────────────────────────────
SELECT
    ism || ' ' || familiya AS toliq_ism,
    ball
FROM talabalar
ORDER BY ball DESC
LIMIT 3;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 2: 11-sinf a'lochilari (80+)
-- ─────────────────────────────────────────────────────────────────────
SELECT ism, sinf, ball
FROM talabalar
WHERE sinf LIKE '11-%' AND ball >= 80
ORDER BY ball DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 3: takrorsiz sinflar
-- ─────────────────────────────────────────────────────────────────────
SELECT DISTINCT sinf FROM talabalar ORDER BY sinf;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 4: yo'qotgan kunlar
-- ─────────────────────────────────────────────────────────────────────
SELECT ism, familiya, maktab_kunlari
FROM talabalar
WHERE maktab_kunlari < 180
ORDER BY maktab_kunlari ASC;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 5: eng yosh + eng katta yoshli
-- ─────────────────────────────────────────────────────────────────────
(SELECT ism, yosh, 'eng_yosh' AS toifa FROM talabalar ORDER BY yosh ASC LIMIT 1)
UNION ALL
(SELECT ism, yosh, 'eng_katta' AS toifa FROM talabalar ORDER BY yosh DESC LIMIT 1);

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 6: sahifa 2 (per_page=2)
-- ─────────────────────────────────────────────────────────────────────
SELECT ism, ball FROM talabalar
ORDER BY ball DESC
LIMIT 2 OFFSET 2;

-- ─────────────────────────────────────────────────────────────────────
-- BONUS: bitta murakkab so'rov
-- ─────────────────────────────────────────────────────────────────────
-- 10 va 11-sinfning birinchi 5 ta TOP a'lochisi, alfavit bo'yicha
SELECT
    ism || ' ' || COALESCE(familiya, '') AS toliq,
    sinf,
    ball,
    maktab_kunlari
FROM talabalar
WHERE sinf LIKE '10-%' OR sinf LIKE '11-%'
ORDER BY ball DESC, ism ASC
LIMIT 5;
"""
L4_TEXT = """\
<h2>Agregat funksiyalar — COUNT, SUM, AVG, MIN, MAX</h2>

<pre class="mermaid">
flowchart LR
    R["qatorlar"] -->|COUNT| C["jami soni"]
    R -->|SUM ustun| S["yig'indi"]
    R -->|AVG ustun| A["o'rtacha"]
    R -->|MIN/MAX| MM["chegara"]
</pre>

<p>Endi siz "har talaba" o'rniga "barcha talabalar haqida bitta gap" so'roviga o'tasiz: "Qancha?", "Yig'indisi?", "O'rtachasi?", "Eng kattasi?". Bularni <strong>agregat funksiyalar</strong> qiladi — N ta qatordan 1 ta natija chiqaradi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — sanash</h4>
<pre><code>-- Jami nechta talaba
SELECT COUNT(*) FROM talabalar;
-- 6

-- Familiyasi bor talabalar (NULL hisobga kirmaydi)
SELECT COUNT(familiya) FROM talabalar;
-- 6

-- Filterlangan sanash
SELECT COUNT(*) FROM talabalar WHERE ball &gt;= 80;
-- 3</code></pre>

<h4>BLOKA 2 — SUM, AVG, MIN, MAX</h4>
<pre><code>SELECT
    SUM(ball)   AS jami_ball,
    AVG(ball)   AS ortacha_ball,
    MIN(ball)   AS eng_kam,
    MAX(ball)   AS eng_yuqori
FROM talabalar;
-- jami_ball | ortacha_ball       | eng_kam | eng_yuqori
-- 467       | 77.8333333333333333|   58    |    95</code></pre>

<p>AVG kasr qaytaradi (juda ko'p o'nlik!). Yumaloqlash kerak:</p>
<pre><code>SELECT ROUND(AVG(ball), 2) AS ortacha FROM talabalar;
-- 77.83</code></pre>

<h4>BLOKA 3 — string va sana funksiyalar</h4>
<pre><code>-- String
SELECT
    LENGTH(ism)        AS uzunlik,
    UPPER(ism)         AS katta,
    LOWER(familiya)    AS kichik,
    SUBSTRING(ism, 1, 2) AS qisqa,
    CONCAT(ism, ' ', familiya) AS toliq
FROM talabalar
LIMIT 2;

-- Sana
SELECT
    CURRENT_DATE                 AS bugun,
    NOW()                        AS hozir,
    EXTRACT(YEAR FROM NOW())     AS yil,
    AGE(DATE '2010-01-15')       AS yoshi,
    DATE_TRUNC('month', NOW())   AS shu_oy_boshi;</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>-- "Jami balli 87 dan katta" — qaysi qatorlar?
SELECT ism FROM talabalar
WHERE SUM(ball) &gt; 87;</code></pre>

<p><strong>Natija:</strong> <code>ERROR: aggregate functions are not allowed in WHERE</code>. Bu juda muhim tushuncha: <strong>agregat funksiya WHERE'da ishlatib bo'lmaydi</strong>, chunki WHERE har bir qator uchun bajariladi — guruh hali yig'ilmagan.</p>

<p>Agregat shartlari uchun keyingi darsda <code>HAVING</code> bor.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Agregat funksiyalar to'liq ro'yxati</h4>
<table>
<tr><th>Funksiya</th><th>Vazifa</th><th>NULL bilan</th></tr>
<tr><td><code>COUNT(*)</code></td><td>barcha qatorlar</td><td>NULL'larni ham sanaydi</td></tr>
<tr><td><code>COUNT(ustun)</code></td><td>NOT NULL qatorlar</td><td>NULL'ni o'tkazib yuboradi</td></tr>
<tr><td><code>COUNT(DISTINCT ustun)</code></td><td>takrorsiz qiymatlar</td><td>NULL'ni o'tkazadi</td></tr>
<tr><td><code>SUM(ustun)</code></td><td>yig'indi</td><td>NULL'ni 0 deb hisoblaydi</td></tr>
<tr><td><code>AVG(ustun)</code></td><td>o'rtacha</td><td>NULL hisobga kirmaydi</td></tr>
<tr><td><code>MIN(ustun)</code></td><td>eng kichik</td><td>NULL e'tibordan tashqari</td></tr>
<tr><td><code>MAX(ustun)</code></td><td>eng katta</td><td>NULL e'tibordan tashqari</td></tr>
</table>

<h4>2. Foydali matematik funksiyalar</h4>
<table>
<tr><th>Funksiya</th><th>Misol</th><th>Natija</th></tr>
<tr><td><code>ROUND(x, n)</code></td><td><code>ROUND(77.835, 2)</code></td><td>77.84</td></tr>
<tr><td><code>CEIL(x)</code></td><td><code>CEIL(77.1)</code></td><td>78</td></tr>
<tr><td><code>FLOOR(x)</code></td><td><code>FLOOR(77.9)</code></td><td>77</td></tr>
<tr><td><code>ABS(x)</code></td><td><code>ABS(-5)</code></td><td>5</td></tr>
<tr><td><code>POWER(x, n)</code></td><td><code>POWER(2, 10)</code></td><td>1024</td></tr>
</table>

<h4>3. String funksiyalar</h4>
<table>
<tr><th>Funksiya</th><th>Vazifa</th></tr>
<tr><td><code>LENGTH(s)</code></td><td>belgilar soni</td></tr>
<tr><td><code>UPPER(s)</code> / <code>LOWER(s)</code></td><td>katta/kichik harf</td></tr>
<tr><td><code>TRIM(s)</code></td><td>chetidagi bo'shliqlar olib tashlash</td></tr>
<tr><td><code>SUBSTRING(s FROM 1 FOR 3)</code></td><td>qism</td></tr>
<tr><td><code>REPLACE(s, 'a', 'b')</code></td><td>almashtirish</td></tr>
<tr><td><code>s1 || s2</code></td><td>birlashtirish (CONCAT alternativi)</td></tr>
<tr><td><code>POSITION('lo' IN 'salom')</code></td><td>4 — qaerda</td></tr>
</table>

<h4>4. Sana funksiyalar</h4>
<table>
<tr><th>Funksiya</th><th>Vazifa</th></tr>
<tr><td><code>CURRENT_DATE</code></td><td>bugungi sana</td></tr>
<tr><td><code>NOW()</code></td><td>hozirgi vaqt (timestamp)</td></tr>
<tr><td><code>AGE(d)</code></td><td>o'tgan vaqt</td></tr>
<tr><td><code>EXTRACT(YEAR FROM ts)</code></td><td>yil / OY / DAY / HOUR ajratib olish</td></tr>
<tr><td><code>DATE_TRUNC('month', ts)</code></td><td>oyning birinchi kuniga "tushirish"</td></tr>
<tr><td><code>NOW() + INTERVAL '7 days'</code></td><td>7 kun keyin</td></tr>
</table>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>COUNT/SUM/AVG/MIN/MAX</code> — N qatordan 1 natija</li>
<li>✅ <code>COUNT(*)</code> vs <code>COUNT(ustun)</code> — NULL'lar farqi</li>
<li>✅ <code>ROUND(AVG(...), 2)</code> — chiroyli o'rtacha</li>
<li>✅ String va sana funksiyalari — kunlik hisobotlar uchun</li>
<li>✅ Agregat <strong>WHERE</strong>'da ishlatilmaydi (keyingi darsda <code>HAVING</code>)</li>
</ul>
"""

L4_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 4: Agregat funksiyalar
-- Maqsad: N qatordan 1 raqam — COUNT/SUM/AVG/MIN/MAX
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — sanash
-- ─────────────────────────────────────────────────────────────────────

SELECT COUNT(*) AS jami_talabalar FROM talabalar;

SELECT COUNT(*) AS uchinchi_sinflilar
FROM talabalar
WHERE sinf LIKE '11-%';

-- NULL'larni hisobga olmaslik (ustun bo'yicha)
SELECT
    COUNT(*)          AS jami,
    COUNT(familiya)   AS familiyasi_borlar
FROM talabalar;

-- Takrorsizlik
SELECT COUNT(DISTINCT sinf) AS sinflar_soni FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — SUM, AVG, MIN, MAX
-- ─────────────────────────────────────────────────────────────────────

SELECT
    SUM(ball)              AS jami_ball,
    ROUND(AVG(ball), 2)    AS ortacha,
    MIN(ball)              AS eng_kam,
    MAX(ball)              AS eng_yuqori,
    MAX(ball) - MIN(ball)  AS oraliq
FROM talabalar;

-- Filter bilan
SELECT
    ROUND(AVG(ball), 1) AS ortacha_11_sinf
FROM talabalar
WHERE sinf LIKE '11-%';

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — string funksiyalar
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ism,
    LENGTH(ism)              AS belgilar_soni,
    UPPER(ism)               AS katta,
    LOWER(ism)               AS kichik,
    SUBSTRING(ism FROM 1 FOR 2) AS birinchi_ikki,
    ism || ' ' || COALESCE(familiya, '?') AS toliq
FROM talabalar
LIMIT 3;

-- Almashtirish
SELECT REPLACE(sinf, '-', '/') FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — sana/vaqt
-- ─────────────────────────────────────────────────────────────────────

SELECT
    CURRENT_DATE                    AS bugun,
    NOW()                           AS hozir,
    NOW() + INTERVAL '7 days'       AS keyingi_hafta,
    EXTRACT(YEAR FROM NOW())        AS yil,
    EXTRACT(DOW FROM NOW())         AS hafta_kuni,
    DATE_TRUNC('month', NOW())      AS oy_boshi,
    DATE_TRUNC('year', NOW())       AS yil_boshi;

-- Yosh hisoblash
SELECT
    ism,
    yosh,
    EXTRACT(YEAR FROM AGE(DATE '2010-01-15')) AS yashagan_yil
FROM talabalar
LIMIT 1;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — matematik
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ROUND(123.456, 2)   AS yumalok,
    CEIL(77.1)          AS yuqori,
    FLOOR(77.9)         AS pastki,
    ABS(-42)            AS modul,
    POWER(2, 10)        AS ikki_un_uchunchi,
    MOD(10, 3)          AS qoldiq;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — Ataylab xato: WHERE'da agregat
-- ─────────────────────────────────────────────────────────────────────

-- Bu xato qaytaradi
-- SELECT ism FROM talabalar WHERE SUM(ball) > 87;
--   ERROR: aggregate functions are not allowed in WHERE
"""
L5_TEXT = """\
<h2>GROUP BY va HAVING — guruhlab agregatsiya</h2>

<pre class="mermaid">
flowchart LR
    R["qatorlar"] -->|WHERE| F["filterlangan"]
    F -->|GROUP BY sinf| G["guruhlar"]
    G -->|HAVING shart| GF["filterlangan guruhlar"]
    GF --> OUT["natija"]
</pre>

<p>4-darsda <code>AVG(ball)</code> butun jadval bo'yicha bitta o'rtacha qaytardi. Lekin haqiqiy hisobotlar uchun siz <strong>har sinf bo'yicha</strong>, <strong>har kategoriyaga ko'ra</strong>, <strong>har yil bo'yicha</strong> kerakli ko'rsatkichni hisoblaysiz. Bu — <code>GROUP BY</code>.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi GROUP BY</h4>
<pre><code>-- Har sinfda nechtadan talaba?
SELECT sinf, COUNT(*) AS soni
FROM talabalar
GROUP BY sinf;
-- sinf  | soni
-- 10-A  |  1
-- 10-B  |  1
-- 11-A  |  2
-- 11-B  |  1
-- 9-B   |  1</code></pre>

<p>Endi har <em>sinf</em> uchun bitta qator. <code>GROUP BY sinf</code> — "qatorlarni <code>sinf</code> qiymati bo'yicha guruhla". Keyin agregatlar <em>har guruh ichida</em> hisoblanadi.</p>

<h4>BLOKA 2 — bir nechta agregat birga</h4>
<pre><code>SELECT
    sinf,
    COUNT(*)             AS talabalar_soni,
    ROUND(AVG(ball), 1)  AS ortacha,
    MAX(ball)            AS eng_yuqori,
    MIN(ball)            AS eng_past
FROM talabalar
GROUP BY sinf
ORDER BY ortacha DESC;</code></pre>

<h4>BLOKA 3 — HAVING bilan guruhlarni filterlash</h4>
<pre><code>-- Faqat o'rtacha bali 80 dan yuqori sinflar
SELECT
    sinf,
    ROUND(AVG(ball), 1) AS ortacha
FROM talabalar
GROUP BY sinf
HAVING AVG(ball) &gt; 80;
-- 10-A  95.0
-- 11-A  89.0</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>SELECT sinf, ism, AVG(ball)
FROM talabalar
GROUP BY sinf;</code></pre>
<p><strong>Natija:</strong> <code>ERROR: column "talabalar.ism" must appear in the GROUP BY clause</code>. SELECT ichidagi har bir <em>oddiy ustun</em> ham <code>GROUP BY</code> da bo'lishi yoki agregat ichida bo'lishi kerak. Aks holda — bir guruhda 5 ta ism bor — qaysisini qaytarsin?</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. WHERE vs HAVING — eng katta chigallik</h4>
<table>
<tr><th></th><th>WHERE</th><th>HAVING</th></tr>
<tr><td>Qachon</td><td>Guruhlashdan oldin</td><td>Guruhlashdan keyin</td></tr>
<tr><td>Nimani filterlaydi</td><td>Yakka qatorlarni</td><td>Guruhlarni</td></tr>
<tr><td>Agregat ishlatish</td><td>❌ ishlatib bo'lmaydi</td><td>✅ ishlatish kerak</td></tr>
</table>

<pre><code>-- 11-sinflarning o'rtacha bali 80+ bo'lganlari
SELECT sinf, AVG(ball)
FROM talabalar
WHERE sinf LIKE '11-%'    -- avval qatorlarni 11-sinflarga cheklaymiz
GROUP BY sinf
HAVING AVG(ball) &gt; 80;    -- keyin guruhlardan tanlaymiz</code></pre>

<h4>2. GROUP BY qoidasi</h4>
<p>SELECT ichidagi har bir ustun (NOT agregat):</p>
<ul>
<li>YOKI GROUP BY ichida bo'lishi kerak</li>
<li>YOKI agregat funksiya ichida bo'lishi kerak (<code>MAX(ism)</code> kabi)</li>
</ul>

<p>Aks holda PostgreSQL "qaysi qiymatni tanlash?" deb hayron qoladi.</p>

<h4>3. SQL ijro tartibi (yangilangan)</h4>
<ol>
<li><strong>FROM</strong></li>
<li><strong>WHERE</strong> (qatorlar filteri)</li>
<li><strong>GROUP BY</strong> (guruhlash)</li>
<li><strong>HAVING</strong> (guruhlar filteri)</li>
<li><strong>SELECT</strong></li>
<li><strong>ORDER BY</strong></li>
<li><strong>LIMIT</strong></li>
</ol>

<p>Shu sababli HAVING ichida SELECT'dagi alias <em>ishlamasligi</em> mumkin (PostgreSQL'ning ba'zi versiyalarida ishlaydi, lekin standart emas):</p>

<pre><code>-- Standart yondashuv — to'liq ifoda
GROUP BY sinf
HAVING AVG(ball) &gt; 80;

-- PostgreSQL'da alias ham ishlaydi, lekin yaxshi odat — yo'q
GROUP BY sinf
HAVING ortacha &gt; 80;   -- "ortacha" alias bo'lsa</code></pre>

<h4>4. Multi-column GROUP BY</h4>
<pre><code>-- Har (sinf, yosh) juftligi uchun
SELECT sinf, yosh, COUNT(*)
FROM talabalar
GROUP BY sinf, yosh;</code></pre>

<h4>5. Foydali agregatlar — STRING_AGG</h4>
<pre><code>-- Har sinfdagi talabalar ismlari bitta qatorda
SELECT
    sinf,
    STRING_AGG(ism, ', ' ORDER BY ism) AS talabalar
FROM talabalar
GROUP BY sinf;
-- 10-A | Nigora
-- 11-A | Karim, Olim</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>GROUP BY ustun</code> — qatorlarni guruhlarga ajratadi</li>
<li>✅ Agregatlar har guruh ichida ishlaydi</li>
<li>✅ <code>HAVING</code> — guruhlarni filterlash (WHERE ham bo'lishi mumkin, ikkisi har xil)</li>
<li>✅ SELECT'dagi har oddiy ustun GROUP BY ichida bo'lishi kerak</li>
<li>✅ <code>STRING_AGG</code> — guruhdagi qiymatlarni matn qilib birlashtirish</li>
</ul>
"""

L5_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 5: GROUP BY va HAVING
-- Maqsad: guruhlab agregatsiya, guruhlarni filterlash
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — birinchi GROUP BY
-- ─────────────────────────────────────────────────────────────────────

-- Sinf bo'yicha talabalar soni
SELECT sinf, COUNT(*) AS soni
FROM talabalar
GROUP BY sinf
ORDER BY soni DESC;

-- Yosh bo'yicha
SELECT yosh, COUNT(*) AS soni
FROM talabalar
GROUP BY yosh
ORDER BY yosh;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — to'liq hisobot
-- ─────────────────────────────────────────────────────────────────────

SELECT
    sinf,
    COUNT(*)             AS soni,
    ROUND(AVG(ball), 1)  AS ortacha,
    MAX(ball)            AS top,
    MIN(ball)            AS pastki,
    SUM(ball)            AS jami
FROM talabalar
GROUP BY sinf
ORDER BY ortacha DESC;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — WHERE + GROUP BY birga
-- ─────────────────────────────────────────────────────────────────────

-- 11-sinflarning sinf bo'yicha o'rtacha bali
SELECT
    sinf,
    ROUND(AVG(ball), 1) AS ortacha
FROM talabalar
WHERE sinf LIKE '11-%'
GROUP BY sinf;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — HAVING
-- ─────────────────────────────────────────────────────────────────────

-- Faqat 80+ o'rtacha balli sinflar
SELECT
    sinf,
    ROUND(AVG(ball), 1) AS ortacha
FROM talabalar
GROUP BY sinf
HAVING AVG(ball) > 80
ORDER BY ortacha DESC;

-- 2 yoki undan ko'p talaba bor sinflar
SELECT sinf, COUNT(*) AS soni
FROM talabalar
GROUP BY sinf
HAVING COUNT(*) >= 2;

-- HAVING + WHERE birga
SELECT sinf, ROUND(AVG(ball), 1) AS ortacha
FROM talabalar
WHERE yosh >= 16
GROUP BY sinf
HAVING AVG(ball) > 75;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — Multi-column GROUP BY
-- ─────────────────────────────────────────────────────────────────────

SELECT sinf, yosh, COUNT(*) AS soni
FROM talabalar
GROUP BY sinf, yosh
ORDER BY sinf, yosh;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — STRING_AGG
-- ─────────────────────────────────────────────────────────────────────

-- Sinfdagi barcha ismlar — vergul bilan
SELECT
    sinf,
    STRING_AGG(ism, ', ' ORDER BY ism) AS talabalar,
    COUNT(*) AS soni
FROM talabalar
GROUP BY sinf
ORDER BY sinf;
"""
L6_TEXT = """\
<h2>JOIN'lar — jadvallarni birlashtirish</h2>

<pre class="mermaid">
flowchart LR
    A["talabalar"] --> J{"JOIN\nON id"}
    B["baholar"] --> J
    J --> R["birlashgan natija"]
</pre>

<p>Bu — SQL'ning eng muhim darslaridan biri. Real DB hech qachon faqat bitta jadvaldan iborat emas: <strong>talabalar</strong> bitta jadvalda, <strong>baholari</strong> ikkinchisida, <strong>fanlar</strong> uchinchisida. <code>JOIN</code> — ularni bog'lash.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<p>Yangi 2 ta jadval qo'shamiz: <code>fanlar</code> va <code>baholar</code>.</p>

<pre><code>CREATE TABLE IF NOT EXISTS fanlar (
    id   SERIAL PRIMARY KEY,
    nomi VARCHAR(50) NOT NULL
);

INSERT INTO fanlar (nomi) VALUES
    ('Matematika'), ('Fizika'), ('Tarix'), ('Ona tili');

CREATE TABLE IF NOT EXISTS baholar (
    id          SERIAL PRIMARY KEY,
    talaba_id   INTEGER REFERENCES talabalar(id),
    fan_id      INTEGER REFERENCES fanlar(id),
    baho        INTEGER CHECK (baho BETWEEN 1 AND 100),
    sana        DATE DEFAULT CURRENT_DATE
);

INSERT INTO baholar (talaba_id, fan_id, baho) VALUES
    (1, 1, 90), (1, 2, 85),   -- Olim: matem, fizika
    (2, 1, 70), (2, 3, 75),   -- Vali
    (3, 1, 95), (3, 2, 88), (3, 4, 92),  -- Karim
    (5, 1, 98), (5, 4, 94);   -- Nigora</code></pre>

<h4>BLOKA 1 — INNER JOIN</h4>
<pre><code>SELECT
    t.ism,
    f.nomi    AS fan,
    b.baho
FROM baholar b
JOIN talabalar t ON t.id = b.talaba_id
JOIN fanlar    f ON f.id = b.fan_id
ORDER BY t.ism, f.nomi;
-- Karim | Fizika     | 88
-- Karim | Matematika | 95
-- Karim | Ona tili   | 92
-- ...</code></pre>

<p>Endi ko'rasiz: 3 ta jadvaldagi ma'lumotni bitta tableda. <code>t</code>, <code>f</code>, <code>b</code> — <strong>jadval aliaslari</strong> (tezroq yozish).</p>

<h4>BLOKA 2 — LEFT JOIN</h4>
<pre><code>-- Hamma talabalar (hatto baho yo'qlari ham)
SELECT
    t.ism,
    COUNT(b.id) AS bahosi_soni
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism
ORDER BY bahosi_soni DESC;
-- Karim    | 3
-- Olim     | 2
-- Salim    | 0   &lt;-- bahosi yo'q, lekin ko'rinadi</code></pre>

<h4>BLOKA 3 — RIGHT, FULL, CROSS</h4>
<pre><code>-- RIGHT JOIN (kam ishlatiladi — LEFT JOIN bilan almashtirish mumkin)
SELECT t.ism, b.baho
FROM baholar b
RIGHT JOIN talabalar t ON t.id = b.talaba_id;

-- FULL OUTER JOIN — ikkala tomonni hammasini
SELECT t.ism, b.baho
FROM talabalar t
FULL OUTER JOIN baholar b ON t.id = b.talaba_id;

-- CROSS JOIN — kartezian (har talaba × har fan)
SELECT t.ism, f.nomi
FROM talabalar t
CROSS JOIN fanlar f;
-- 6 talaba × 4 fan = 24 qator</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>SELECT t.ism, f.nomi, b.baho
FROM talabalar t, fanlar f, baholar b
WHERE b.talaba_id = t.id;</code></pre>

<p><strong>Natija:</strong> Juda ko'p qator! <code>fanlar</code> bilan bog'lanish unutilgan, demak har baho × har fan kartezian ko'paytma chiqadi (9 baho × 4 fan = 36). Bu — eski "implicit join" sintaksisining xavfli tarafi. <strong>Doim aniq <code>JOIN ... ON ...</code> ishlating.</strong></p>

<h3>Endi tushuntiramiz</h3>

<h4>1. JOIN turlari — vizual</h4>
<pre><code>     A (chap)    B (o'ng)
       ┌──┐     ┌──┐
       │  │     │  │
       │ ●○○○○● │  │     ●  — A da bor, B da yo'q
       │  │     │  │     ○  — kesishish (umumiy)
       └──┘     └──┘     ●  — B da bor, A da yo'q

INNER JOIN       — faqat ○○○○ (kesishish)
LEFT JOIN        — ●○○○○ (A ning hammasi + kesishish)
RIGHT JOIN       — ○○○○● (B ning hammasi + kesishish)
FULL OUTER JOIN  — ●○○○○● (hammasi)</code></pre>

<h4>2. JOIN sintaksisi</h4>
<pre><code>SELECT &lt;ustunlar&gt;
FROM   &lt;chap_jadval&gt; alias1
[INNER | LEFT | RIGHT | FULL] JOIN &lt;ong_jadval&gt; alias2
    ON  &lt;bog'lanish_sharti&gt;
WHERE  &lt;qator_sharti&gt;</code></pre>

<p>⚠️ Eng katta tuzoq: <code>ON</code> vs <code>WHERE</code>. Bog'lanish — <code>ON</code> da. Filterlash — <code>WHERE</code> da. LEFT JOIN'da <code>WHERE</code> ga shart qo'ysangiz, u INNER JOIN'ga aylanib qolishi mumkin:</p>

<pre><code>-- XATO: LEFT JOIN'ni buzadi
SELECT t.ism, b.baho
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
WHERE b.baho &gt; 80;       -- NULL bahodagilarni o'chiradi -> INNER bo'ladi

-- TO'G'RI: shartni ON ichiga
SELECT t.ism, b.baho
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id AND b.baho &gt; 80;</code></pre>

<h4>3. Ko'p jadval JOIN</h4>
<p>Tartib: birinchi jadvalga ikkinchini, keyin uchinchini, va h.k.</p>
<pre><code>FROM    talabalar  t
JOIN    baholar    b ON b.talaba_id = t.id
JOIN    fanlar     f ON f.id = b.fan_id</code></pre>

<h4>4. Self JOIN</h4>
<p>Jadvalni o'ziga ulash — masalan, xodimlar -&gt; menejer:</p>
<pre><code>SELECT
    e.ism      AS xodim,
    m.ism      AS menejer
FROM xodimlar e
LEFT JOIN xodimlar m ON m.id = e.menejer_id;</code></pre>

<h4>5. JOIN + agregat — eng kuchli birikma</h4>
<pre><code>-- Har talabaning o'rtacha bahosi
SELECT
    t.ism,
    ROUND(AVG(b.baho), 1) AS ortacha_baho,
    COUNT(b.id)            AS fanlar_soni
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism
ORDER BY ortacha_baho DESC NULLS LAST;</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ INNER / LEFT / RIGHT / FULL JOIN — qachon qaysi birini</li>
<li>✅ <code>ON</code> bog'lanish shartlari, <code>WHERE</code> qator filterlari</li>
<li>✅ LEFT JOIN'da WHERE qo'shsa — INNER'ga aylanish xavfi</li>
<li>✅ Jadval aliaslari (<code>t</code>, <code>b</code>, <code>f</code>) — tezroq yozish</li>
<li>✅ Self JOIN — jadvalni o'ziga ulash</li>
<li>✅ JOIN + GROUP BY — real hisobotlarning asosi</li>
</ul>
"""

L6_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 6: JOIN'lar
-- Maqsad: jadvallarni birlashtirib hisobotlar yasash
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- Tayyorgarlik — fanlar va baholar jadvallari
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fanlar (
    id   SERIAL PRIMARY KEY,
    nomi VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS baholar (
    id        SERIAL PRIMARY KEY,
    talaba_id INTEGER REFERENCES talabalar(id),
    fan_id    INTEGER REFERENCES fanlar(id),
    baho      INTEGER CHECK (baho BETWEEN 1 AND 100),
    sana      DATE DEFAULT CURRENT_DATE
);

-- Faqat birinchi marta
INSERT INTO fanlar (nomi) VALUES
    ('Matematika'), ('Fizika'), ('Tarix'), ('Ona tili')
ON CONFLICT DO NOTHING;

INSERT INTO baholar (talaba_id, fan_id, baho) VALUES
    (1, 1, 90), (1, 2, 85),
    (2, 1, 70), (2, 3, 75),
    (3, 1, 95), (3, 2, 88), (3, 4, 92),
    (5, 1, 98), (5, 4, 94);
-- e'tibor: talaba id=4 (Dilshod) va id=6 (Salim) — baho yo'q

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — INNER JOIN
-- ─────────────────────────────────────────────────────────────────────

SELECT
    t.ism,
    f.nomi   AS fan,
    b.baho
FROM baholar b
JOIN talabalar t ON t.id = b.talaba_id
JOIN fanlar    f ON f.id = b.fan_id
ORDER BY t.ism, f.nomi;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — LEFT JOIN (hamma talabalar)
-- ─────────────────────────────────────────────────────────────────────

SELECT
    t.ism,
    COUNT(b.id) AS bahosi_soni,
    ROUND(AVG(b.baho), 1) AS ortacha_baho
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism
ORDER BY bahosi_soni DESC;

-- Bahosi yo'qlarini ko'rish
SELECT t.ism
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
WHERE b.id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — RIGHT, FULL OUTER
-- ─────────────────────────────────────────────────────────────────────

-- RIGHT JOIN — odatda LEFT bilan tartibni almashtirish kifoya
SELECT t.ism, b.baho
FROM baholar b
RIGHT JOIN talabalar t ON t.id = b.talaba_id;

-- FULL OUTER — har ikkala tomon
SELECT t.ism, f.nomi
FROM talabalar t
FULL OUTER JOIN baholar b ON b.talaba_id = t.id
FULL OUTER JOIN fanlar    f ON f.id = b.fan_id;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — Filter qaerda turishi (ON vs WHERE)
-- ─────────────────────────────────────────────────────────────────────

-- 1) WHERE bilan — LEFT JOIN buziladi (INNER ga aylanadi)
SELECT t.ism, b.baho
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
WHERE b.baho > 80;     -- NULL'larni o'chiradi

-- 2) ON ichida — to'g'ri
SELECT t.ism, b.baho
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id AND b.baho > 80;
-- Bahosi yo'q talabalar ham qaytadi, b.baho ustuni NULL

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — kuchli hisobot
-- ─────────────────────────────────────────────────────────────────────

-- Har fan bo'yicha eng yuqori ball olgan talaba
SELECT
    f.nomi              AS fan,
    t.ism               AS eng_yaxshi,
    b.baho              AS bahosi
FROM baholar b
JOIN fanlar    f ON f.id = b.fan_id
JOIN talabalar t ON t.id = b.talaba_id
WHERE b.baho = (
    SELECT MAX(b2.baho) FROM baholar b2 WHERE b2.fan_id = b.fan_id
)
ORDER BY f.nomi;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — Self JOIN namunasi (xodim → menejer simulatsiyasi)
-- ─────────────────────────────────────────────────────────────────────

-- Bu yerda demonstratsiya uchun talabalar ichida "yondosh" parlikni topamiz
SELECT
    a.ism AS birinchi,
    b.ism AS ikkinchi,
    a.sinf
FROM talabalar a
JOIN talabalar b ON a.sinf = b.sinf AND a.id < b.id
ORDER BY a.sinf;
"""
R2_TEXT = """\
<h2>R2 — Modul 2 takrorlash: Maktab tahlili dashboard</h2>

<p>Endi sizda ikkita yangi qurol bor: <strong>GROUP BY + HAVING</strong> va <strong>JOIN</strong>. Bularni birga qo'shish — har bir analitik dashboard ortidagi haqiqiy SQL. Bu modulda biz <em>"O'qituvchi maktab haqida o'rganishi kerak narsalarning hammasi"</em> dashboardini tuzamiz.</p>

<h3>Kirish ma'lumoti</h3>
<p>5 va 6-darslarda yaratgan <code>talabalar</code>, <code>fanlar</code>, <code>baholar</code> jadvallari. Hech narsa qo'shmaymiz.</p>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Sinf reytingi</h4>
<p>Har sinf bo'yicha: talabalar soni, o'rtacha ball, eng yuqori ball. O'rtacha bo'yicha tartiblang.</p>

<h4>Vazifa 2 — Fan bo'yicha statistika</h4>
<p>Har fan uchun: nechta talaba ushbu fandan baho olgan, o'rtacha baho, eng yuqori va eng past. Faqat 2 yoki undan ko'p baho borlari.</p>

<h4>Vazifa 3 — Eng kuchli talaba har fan bo'yicha</h4>
<p>Har fan bo'yicha eng yuqori baho olgan talabaning ismini ko'rsating.</p>

<h4>Vazifa 4 — Bahosiz talabalar</h4>
<p>Hech bo'lmaganda bitta fandan baho olmagan talabalarni toping. Ularning ismi va sinflari.</p>

<h4>Vazifa 5 — "Universal a'lochi"</h4>
<p>Barcha fanlardan 85+ baho olgan talabalarni toping. Bu — eng murakkabi.</p>

<h4>Vazifa 6 — O'qituvchi yordamchisi</h4>
<p>Har talaba uchun: ism, sinfi, nechta fandan baho olgani, va o'rtacha bahosi. Bahosi yo'qlar ham ko'rinsin (ortacha NULL bo'ladi).</p>

<h3>🐛 Ataylab qiyin</h3>
<p>Quyidagi so'rovni "9 ta baho" emas, balki "3 ta baho" qaytarganiga ahamiyat bering — nima uchun?</p>
<pre><code>SELECT COUNT(*)
FROM baholar
WHERE baho IN (SELECT MIN(baho) FROM baholar GROUP BY fan_id);</code></pre>

<h3>Yechimlar</h3>

<details>
<summary>Vazifa 1</summary>
<pre><code>SELECT
    sinf,
    COUNT(*) AS talabalar,
    ROUND(AVG(ball), 1) AS ortacha,
    MAX(ball) AS top
FROM talabalar
GROUP BY sinf
ORDER BY ortacha DESC;</code></pre>
</details>

<details>
<summary>Vazifa 2</summary>
<pre><code>SELECT
    f.nomi AS fan,
    COUNT(*) AS baholar_soni,
    ROUND(AVG(b.baho), 1) AS ortacha,
    MIN(b.baho) AS past,
    MAX(b.baho) AS yuqori
FROM baholar b
JOIN fanlar f ON f.id = b.fan_id
GROUP BY f.id, f.nomi
HAVING COUNT(*) &gt;= 2
ORDER BY ortacha DESC;</code></pre>
</details>

<details>
<summary>Vazifa 3</summary>
<pre><code>SELECT
    f.nomi AS fan,
    t.ism AS eng_kuchli,
    b.baho
FROM baholar b
JOIN fanlar f ON f.id = b.fan_id
JOIN talabalar t ON t.id = b.talaba_id
WHERE b.baho = (
    SELECT MAX(b2.baho) FROM baholar b2 WHERE b2.fan_id = b.fan_id
)
ORDER BY f.nomi;</code></pre>
</details>

<details>
<summary>Vazifa 4</summary>
<pre><code>SELECT t.ism, t.sinf
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
WHERE b.id IS NULL;</code></pre>
</details>

<details>
<summary>Vazifa 5 — universal a'lochi</summary>
<pre><code>-- Yondashuv: har talaba uchun MIN(baho) &gt;= 85
SELECT
    t.ism,
    MIN(b.baho) AS eng_past_baho,
    COUNT(b.id) AS fanlar_soni
FROM talabalar t
JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism
HAVING MIN(b.baho) &gt;= 85;</code></pre>
<p>💡 Tushuncha: agar eng past baho ham 85+ bo'lsa — demak barcha baholari 85+.</p>
</details>

<details>
<summary>Vazifa 6</summary>
<pre><code>SELECT
    t.ism,
    t.sinf,
    COUNT(b.id) AS fanlar,
    ROUND(AVG(b.baho), 1) AS ortacha
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism, t.sinf
ORDER BY ortacha DESC NULLS LAST;</code></pre>
</details>

<details>
<summary>Ataylab qiyin — javob</summary>
<p>Subquery <code>(SELECT MIN(baho) FROM baholar GROUP BY fan_id)</code> har fan uchun alohida MIN qaytaradi (4 ta qator). Lekin <code>IN</code> "shu 4 ta sondan biri" deydi — ya'ni har fanning MIN'ini boshqa fanning baholari bilan ham mos kelishi mumkin. Bu — talab qilinganidan ko'pi natija beradi. To'g'risi: <code>EXISTS</code> bilan korelatsiya yoki <code>JOIN</code> bilan fan bo'yicha solishtirish.</p>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ JOIN + GROUP BY birga — har analitikaning asosi</li>
<li>✅ "Universal a'lochi" kabi tipik shartlar — MIN/MAX hiylasi</li>
<li>✅ LEFT JOIN + GROUP BY — bahosizlarni saqlash</li>
<li>✅ Subquery'larda korelatsiya muhim (10-darsda chuqurroq)</li>
</ul>
"""

R2_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- REVISION 2: Maktab tahlili dashboard
-- Modul 2: GROUP BY + HAVING + JOIN
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 1: Sinf reytingi
-- ─────────────────────────────────────────────────────────────────────
SELECT
    sinf,
    COUNT(*)             AS talabalar,
    ROUND(AVG(ball), 1)  AS ortacha,
    MAX(ball)            AS top,
    MIN(ball)            AS pastki
FROM talabalar
GROUP BY sinf
ORDER BY ortacha DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 2: Fan bo'yicha statistika
-- ─────────────────────────────────────────────────────────────────────
SELECT
    f.nomi               AS fan,
    COUNT(*)             AS baholar_soni,
    ROUND(AVG(b.baho), 1) AS ortacha,
    MIN(b.baho)          AS past,
    MAX(b.baho)          AS yuqori
FROM baholar b
JOIN fanlar f ON f.id = b.fan_id
GROUP BY f.id, f.nomi
HAVING COUNT(*) >= 2
ORDER BY ortacha DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 3: Har fanda eng kuchli
-- ─────────────────────────────────────────────────────────────────────
SELECT
    f.nomi    AS fan,
    t.ism     AS eng_kuchli,
    b.baho
FROM baholar b
JOIN fanlar    f ON f.id = b.fan_id
JOIN talabalar t ON t.id = b.talaba_id
WHERE b.baho = (
    SELECT MAX(b2.baho)
    FROM baholar b2
    WHERE b2.fan_id = b.fan_id
)
ORDER BY f.nomi;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 4: Bahosizlar
-- ─────────────────────────────────────────────────────────────────────
SELECT t.ism, t.sinf
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
WHERE b.id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 5: Universal a'lochi (har fandan 85+)
-- ─────────────────────────────────────────────────────────────────────
SELECT
    t.ism,
    MIN(b.baho) AS eng_past_baho,
    COUNT(b.id) AS fanlar_soni
FROM talabalar t
JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism
HAVING MIN(b.baho) >= 85
ORDER BY MIN(b.baho) DESC;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 6: O'qituvchi yordamchisi (LEFT JOIN bilan)
-- ─────────────────────────────────────────────────────────────────────
SELECT
    t.ism,
    t.sinf,
    COUNT(b.id)           AS fanlar,
    ROUND(AVG(b.baho), 1) AS ortacha
FROM talabalar t
LEFT JOIN baholar b ON b.talaba_id = t.id
GROUP BY t.id, t.ism, t.sinf
ORDER BY ortacha DESC NULLS LAST;

-- ─────────────────────────────────────────────────────────────────────
-- BONUS: dashboardni bitta so'rov bilan ko'rsatish
-- ─────────────────────────────────────────────────────────────────────
SELECT
    'Jami talabalar'    AS metric,
    COUNT(*)::TEXT      AS qiymat
FROM talabalar
UNION ALL
SELECT 'Jami baholar', COUNT(*)::TEXT FROM baholar
UNION ALL
SELECT 'O''rtacha baho', ROUND(AVG(baho), 1)::TEXT FROM baholar
UNION ALL
SELECT 'Sinflar soni', COUNT(DISTINCT sinf)::TEXT FROM talabalar;
"""
L7_TEXT = """\
<h2>INSERT, UPDATE, DELETE va tranzaksiyalar</h2>

<pre class="mermaid">
flowchart LR
    B["BEGIN"] --> O1["INSERT"]
    O1 --> O2["UPDATE"]
    O2 --> CK{"hammasi\nyaxshimi?"}
    CK -->|HA| C["COMMIT (saqlash)"]
    CK -->|YO'Q| R["ROLLBACK (bekor qilish)"]
</pre>

<p>Hozirgacha biz faqat <strong>o'qiganmiz</strong> (SELECT). Endi <strong>yozish</strong> navbati: INSERT (qo'shish), UPDATE (o'zgartirish), DELETE (o'chirish). Va eng muhimi — <strong>tranzaksiyalar</strong>: agar nimadir noto'g'ri ketsa, butun o'zgartirishni bekor qilish.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — INSERT</h4>
<pre><code>-- Bitta qator
INSERT INTO talabalar (ism, familiya, yosh, ball, sinf)
VALUES ('Aziza', 'Komilova', 16, 89, '10-A');

-- Bir nechta qator
INSERT INTO talabalar (ism, familiya, yosh, ball, sinf) VALUES
    ('Sherzod', 'Tursunov', 17, 76, '11-B'),
    ('Madina',  'Rasulova', 15, 92, '9-A');

-- RETURNING — qo'shilgan qatorning ma'lumotini qaytarish
INSERT INTO talabalar (ism, ball, sinf)
VALUES ('Test', 50, '8-A')
RETURNING id, ism;
-- id | ism
-- 9  | Test</code></pre>

<h4>BLOKA 2 — UPDATE</h4>
<pre><code>-- Bitta talabaning balini o'zgartirish
UPDATE talabalar
SET    ball = 99
WHERE  id = 1;

-- Bir nechta ustun birga
UPDATE talabalar
SET    ball = ball + 5, sinf = '12-A'
WHERE  sinf = '11-A';

-- Murakkab — boshqa jadvaldan
UPDATE talabalar t
SET    ball = ball + 10
WHERE  EXISTS (
    SELECT 1 FROM baholar b
    WHERE b.talaba_id = t.id AND b.baho &gt;= 95
);</code></pre>

<h4>BLOKA 3 — DELETE</h4>
<pre><code>-- Bitta yozuvni o'chirish
DELETE FROM talabalar WHERE id = 9;

-- Shart bilan
DELETE FROM baholar WHERE baho &lt; 50;

-- RETURNING bilan
DELETE FROM talabalar WHERE sinf = '8-A'
RETURNING id, ism;</code></pre>

<h3>🐛 Ataylab xato (juda xavfli)</h3>
<pre><code>UPDATE talabalar SET ball = 0;</code></pre>
<p><strong>Natija:</strong> Hamma talabaning bali 0 ga aylanadi! <code>WHERE</code> ni unutish — eng kuchli bug shu yerda yashaydi. Production DB'da bunday so'rov yuborib qo'ysangiz, oqibatlari katta. <strong>Doim UPDATE/DELETE oldin SELECT bilan tekshiring.</strong></p>

<pre><code>-- 1) Avval ko'ramiz:
SELECT id, ism, ball FROM talabalar WHERE sinf = '11-A';

-- 2) Ishonchimiz komil — endi UPDATE
UPDATE talabalar SET ball = ball + 5 WHERE sinf = '11-A';</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Tranzaksiyalar — "hammasi yoki hech narsa"</h4>
<p>Bank o'tkazmasini tasavvur qiling: A hisobdan -100, B hisobga +100. Agar 2-bosqich uzilsa, A pul yo'qotadi, B esa olmaydi. Bu — <strong>tranzaksiya</strong> kerakligining sababi.</p>

<pre><code>BEGIN;
    UPDATE hisoblar SET balans = balans - 100 WHERE id = 1;
    UPDATE hisoblar SET balans = balans + 100 WHERE id = 2;
    -- Agar bu yerda nimadir noto'g'ri:
    -- ROLLBACK;
COMMIT;</code></pre>

<p><strong>ACID</strong> — tranzaksiyaning 4 ta xususiyati:</p>
<table>
<tr><th>Harf</th><th>So'z</th><th>Ma'no</th></tr>
<tr><td>A</td><td>Atomicity</td><td>Hammasi yoki hech narsa</td></tr>
<tr><td>C</td><td>Consistency</td><td>Ma'lumot doim qoidaga mos</td></tr>
<tr><td>I</td><td>Isolation</td><td>Parallel tranzaksiyalar bir-biriga to'sqinlik qilmaydi</td></tr>
<tr><td>D</td><td>Durability</td><td>COMMIT qilingach — saqlandi</td></tr>
</table>

<h4>2. BEGIN / COMMIT / ROLLBACK</h4>
<pre><code>BEGIN;            -- yoki: START TRANSACTION;
    INSERT INTO ...
    UPDATE ...
    -- bo'lib qoldi yoki xatoga uchradi
ROLLBACK;          -- hammasini orqaga qaytarish

BEGIN;
    INSERT INTO ...
COMMIT;           -- yozish yakunlandi</code></pre>

<h4>3. SAVEPOINT — qisman ROLLBACK</h4>
<pre><code>BEGIN;
    INSERT INTO talabalar (...) VALUES (...);
    SAVEPOINT s1;
    INSERT INTO baholar (...) VALUES (...);
    -- baho yomon
    ROLLBACK TO SAVEPOINT s1;
    -- talaba qoladi, faqat baho bekor qilindi
COMMIT;</code></pre>

<h4>4. INSERT ... ON CONFLICT (upsert)</h4>
<pre><code>-- Bor bo'lsa — yangilash, yo'q bo'lsa — qo'shish
INSERT INTO talabalar (id, ism, ball)
VALUES (1, 'Olim', 100)
ON CONFLICT (id) DO UPDATE
SET ball = EXCLUDED.ball;
-- EXCLUDED — yangi qiymatlar</code></pre>

<h4>5. RETURNING — yozish + o'qish bitta so'rovda</h4>
<pre><code>INSERT INTO baholar (talaba_id, fan_id, baho)
VALUES (1, 3, 88)
RETURNING id, sana;

UPDATE talabalar SET ball = ball + 5 WHERE sinf = '11-A'
RETURNING ism, ball;

DELETE FROM baholar WHERE baho &lt; 50
RETURNING *;</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>INSERT INTO ... VALUES (...)</code> — qo'shish</li>
<li>✅ <code>UPDATE ... SET ... WHERE ...</code> — <strong>WHERE'siz qilmang!</strong></li>
<li>✅ <code>DELETE FROM ... WHERE ...</code> — xuddi shu xavf</li>
<li>✅ <code>BEGIN / COMMIT / ROLLBACK</code> — "hammasi yoki hech narsa"</li>
<li>✅ ACID — tranzaksiyaning 4 ta kafolati</li>
<li>✅ <code>ON CONFLICT DO UPDATE</code> — upsert</li>
<li>✅ <code>RETURNING</code> — yozish + o'qish bitta so'rovda</li>
</ul>
"""

L7_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 7: INSERT, UPDATE, DELETE va tranzaksiyalar
-- Maqsad: ma'lumotni o'zgartirish va xavfsiz saqlash
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — INSERT
-- ─────────────────────────────────────────────────────────────────────

-- Bitta qator
INSERT INTO talabalar (ism, familiya, yosh, ball, sinf)
VALUES ('Aziza', 'Komilova', 16, 89, '10-A');

-- Bir nechta qator
INSERT INTO talabalar (ism, familiya, yosh, ball, sinf) VALUES
    ('Sherzod', 'Tursunov', 17, 76, '11-B'),
    ('Madina',  'Rasulova', 15, 92, '9-A');

-- RETURNING
INSERT INTO talabalar (ism, ball, sinf)
VALUES ('Test', 50, '8-A')
RETURNING id, ism, ball;

-- Boshqa jadvaldan
-- INSERT INTO arxiv_talabalar (ism, ball)
-- SELECT ism, ball FROM talabalar WHERE ball < 60;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — UPDATE
-- ─────────────────────────────────────────────────────────────────────

-- Avval SELECT bilan tekshiramiz
SELECT id, ism, ball FROM talabalar WHERE sinf = '11-A';

-- Endi UPDATE
UPDATE talabalar
SET ball = ball + 5
WHERE sinf = '11-A'
RETURNING id, ism, ball;

-- Bir nechta ustun
UPDATE talabalar
SET ball = 95, sinf = '12-A'
WHERE id = 1
RETURNING *;

-- Korelatsion UPDATE
UPDATE talabalar t
SET ball = ball + 10
WHERE EXISTS (
    SELECT 1 FROM baholar b
    WHERE b.talaba_id = t.id AND b.baho >= 95
);

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — DELETE
-- ─────────────────────────────────────────────────────────────────────

-- Bitta yozuv
DELETE FROM talabalar WHERE ism = 'Test'
RETURNING id;

-- Shart bilan
-- DELETE FROM baholar WHERE baho < 50;

-- E'TIBOR! WHERE'siz DELETE — barcha qatorlar yo'qoladi
-- DELETE FROM talabalar;  -- ASLO bunday qilmang

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — Tranzaksiya (ROLLBACK)
-- ─────────────────────────────────────────────────────────────────────

BEGIN;
    UPDATE talabalar SET ball = 0 WHERE sinf = '11-A';
    SELECT ism, ball FROM talabalar WHERE sinf = '11-A';
    -- Voy! Bu xato edi
ROLLBACK;

-- Tekshirib ko'ring — ballar tiklandi
SELECT ism, ball FROM talabalar WHERE sinf = '11-A';

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — Tranzaksiya (COMMIT)
-- ─────────────────────────────────────────────────────────────────────

BEGIN;
    INSERT INTO talabalar (ism, ball, sinf)
    VALUES ('Yangi', 70, '10-A');

    UPDATE talabalar SET ball = ball + 2 WHERE sinf = '10-A';
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — SAVEPOINT
-- ─────────────────────────────────────────────────────────────────────

BEGIN;
    INSERT INTO talabalar (ism, ball, sinf) VALUES ('Saqlash1', 80, '9-A');
    SAVEPOINT s1;

    INSERT INTO talabalar (ism, ball, sinf) VALUES ('Saqlash2', 'XATO', '9-A');
    -- bu so'rov xato — type mismatch
    ROLLBACK TO SAVEPOINT s1;

    -- Saqlash1 saqlanadi, Saqlash2 bekor qilingan
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 7 — UPSERT (INSERT ... ON CONFLICT)
-- ─────────────────────────────────────────────────────────────────────

INSERT INTO talabalar (id, ism, ball, sinf)
VALUES (1, 'Olim', 100, '12-A')
ON CONFLICT (id) DO UPDATE
SET ball = EXCLUDED.ball,
    sinf = EXCLUDED.sinf
RETURNING id, ism, ball, sinf;
"""
L8_TEXT = """\
<h2>CREATE TABLE — sxema dizayni va cheklovlar</h2>

<pre class="mermaid">
flowchart TB
    DB[("Database")] --> T1["mijozlar\n(id PK, ism, email UNIQUE)"]
    DB --> T2["buyurtmalar\n(id PK, mijoz_id FK, sana, summa)"]
    T1 -.->|1 ↔ N| T2
</pre>

<p>Hozirgacha siz tayyor jadvallarni o'qiy oldingiz. Endi o'zingiz <strong>sxema</strong> yaratish navbati — bu DB dizaynerligining boshlanishi. Yaxshi sxema ma'lumotni xavfsiz, tushunarli, va kelajakda o'zgartirish oson holatda saqlaydi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi jadval</h4>
<pre><code>CREATE TABLE mijozlar (
    id          SERIAL PRIMARY KEY,
    ism         VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    yosh        INTEGER      CHECK (yosh &gt;= 0 AND yosh &lt;= 150),
    yaratilgan  TIMESTAMPTZ  DEFAULT NOW()
);</code></pre>

<p>Har ustun: <strong>nom</strong>, <strong>tur</strong>, <strong>cheklovlar</strong>.</p>

<h4>BLOKA 2 — FOREIGN KEY (bog'lanish)</h4>
<pre><code>CREATE TABLE buyurtmalar (
    id          SERIAL PRIMARY KEY,
    mijoz_id    INTEGER      NOT NULL REFERENCES mijozlar(id),
    summa       NUMERIC(10,2) NOT NULL CHECK (summa &gt; 0),
    holat       VARCHAR(20)  NOT NULL DEFAULT 'kutmoqda',
    sana        DATE         NOT NULL DEFAULT CURRENT_DATE
);</code></pre>

<p><code>REFERENCES mijozlar(id)</code> — <em>foreign key</em>. Bu cheklov mavjud bo'lmagan <code>mijoz_id</code> ga buyurtma yaratishga ruxsat bermaydi va <code>mijozlar</code> jadvalidan ulangan qatorni o'chirishni bloklaydi.</p>

<h4>BLOKA 3 — jadvalni o'zgartirish (ALTER)</h4>
<pre><code>-- Yangi ustun qo'shish
ALTER TABLE mijozlar ADD COLUMN telefon VARCHAR(20);

-- Ustun nomini o'zgartirish
ALTER TABLE mijozlar RENAME COLUMN ism TO toliq_ism;

-- Ustun turini o'zgartirish
ALTER TABLE mijozlar ALTER COLUMN telefon TYPE VARCHAR(30);

-- Cheklov qo'shish
ALTER TABLE mijozlar ADD CONSTRAINT unik_telefon UNIQUE (telefon);

-- Jadvalni o'chirish (juda ehtiyot bo'ling!)
-- DROP TABLE buyurtmalar;</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>-- Mijoz bo'lmagan ID bilan buyurtma yarating
INSERT INTO buyurtmalar (mijoz_id, summa) VALUES (9999, 100);</code></pre>

<p><strong>Natija:</strong> <code>ERROR: insert or update on table "buyurtmalar" violates foreign key constraint</code>. <code>REFERENCES</code> sizni ma'nosiz ma'lumotdan saqladi. Bu — FOREIGN KEY ning eng katta yutug'i: "yo'q narsalarga" havola qila olmaysiz.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Asosiy ma'lumot turlari</h4>
<table>
<tr><th>Tur</th><th>Misol</th><th>Foydalanish</th></tr>
<tr><td><code>SERIAL</code></td><td>1, 2, 3, ...</td><td>auto-inkrement ID</td></tr>
<tr><td><code>BIGSERIAL</code></td><td>katta sonlar</td><td>milliard+ qatorli jadvallar uchun</td></tr>
<tr><td><code>INTEGER</code></td><td>42</td><td>oddiy butun son (±2.1 mlrd)</td></tr>
<tr><td><code>BIGINT</code></td><td>katta son</td><td>±9 kvint</td></tr>
<tr><td><code>NUMERIC(p,s)</code></td><td>NUMERIC(10,2)</td><td>aniq kasr — <strong>pul!</strong></td></tr>
<tr><td><code>REAL/DOUBLE</code></td><td>3.14</td><td>fan/grafika — pulda KAM</td></tr>
<tr><td><code>VARCHAR(n)</code></td><td>'Olim'</td><td>maxsus uzunlikdagi matn</td></tr>
<tr><td><code>TEXT</code></td><td>'uzun matn...'</td><td>chegarasiz matn (zamonaviy default)</td></tr>
<tr><td><code>BOOLEAN</code></td><td>TRUE / FALSE</td><td>ha/yo'q</td></tr>
<tr><td><code>DATE</code></td><td>'2026-06-08'</td><td>sana</td></tr>
<tr><td><code>TIMESTAMP</code></td><td>'2026-06-08 14:30'</td><td>sana + vaqt</td></tr>
<tr><td><code>TIMESTAMPTZ</code></td><td>UTC bilan</td><td>multi-zone app uchun afzal</td></tr>
<tr><td><code>JSONB</code></td><td>'{"a": 1}'</td><td>strukturali ma'lumot</td></tr>
<tr><td><code>UUID</code></td><td>'a1b2-...'</td><td>tarqalgan ID</td></tr>
</table>

<h4>2. Cheklovlar (Constraints)</h4>
<table>
<tr><th>Cheklov</th><th>Vazifa</th></tr>
<tr><td><code>PRIMARY KEY</code></td><td>Yagona, NOT NULL — qatorning shaxsiy ID'si</td></tr>
<tr><td><code>FOREIGN KEY (...) REFERENCES T(id)</code></td><td>boshqa jadvalga ishonchli havola</td></tr>
<tr><td><code>NOT NULL</code></td><td>Ustun bo'sh bo'lmasin</td></tr>
<tr><td><code>UNIQUE</code></td><td>Qiymat takrorlanmasin</td></tr>
<tr><td><code>DEFAULT &lt;ifoda&gt;</code></td><td>Yozilmasa — bu qiymat</td></tr>
<tr><td><code>CHECK (shart)</code></td><td>Qatorga doimiy qoida</td></tr>
</table>

<h4>3. FOREIGN KEY tushuntirilgan</h4>
<pre><code>FOREIGN KEY (mijoz_id) REFERENCES mijozlar(id)
    ON DELETE CASCADE       -- mijoz o'chirilsa, buyurtmalari ham o'chsin
    ON DELETE RESTRICT      -- mijozni o'chirishga ruxsat berma (default)
    ON DELETE SET NULL      -- mijoz_id ni NULL qil</code></pre>

<p>To'g'ri tanlovni vaziyatga qarab qiling: log/zaxira yozuvlari uchun <code>CASCADE</code>, muhim hisobotlar uchun <code>RESTRICT</code> yaxshi.</p>

<h4>4. Ko'p ustunli PRIMARY KEY va UNIQUE</h4>
<pre><code>-- Talaba + fan juftligi takrorlanmasin
CREATE TABLE baholar (
    talaba_id INTEGER REFERENCES talabalar(id),
    fan_id    INTEGER REFERENCES fanlar(id),
    baho      INTEGER,
    PRIMARY KEY (talaba_id, fan_id)
);</code></pre>

<h4>5. Sxema dizayni — yaxshi odatlar</h4>
<ul>
<li>✅ Har jadvalda <code>id SERIAL PRIMARY KEY</code></li>
<li>✅ <code>created_at TIMESTAMPTZ DEFAULT NOW()</code></li>
<li>✅ Pul — har doim <code>NUMERIC(p,s)</code>, hech qachon REAL/DOUBLE</li>
<li>✅ Sana/vaqt — <code>TIMESTAMPTZ</code> default tavsiya</li>
<li>✅ Foreign key — <strong>doim</strong> qo'ying (faqat performance yutuqlar bilan istisno)</li>
<li>✅ <code>NOT NULL</code> ni ko'pi bilan ishlating — NULL — chigallikning manbai</li>
<li>✅ <code>VARCHAR(n)</code> emas, <code>TEXT</code> — zamonaviy default (PostgreSQL'da farq yo'q)</li>
</ul>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>CREATE TABLE</code> — ustunlar + turlar + cheklovlar</li>
<li>✅ PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, DEFAULT, CHECK</li>
<li>✅ Ma'lumot turlari: SERIAL, INTEGER, NUMERIC, TEXT, BOOLEAN, DATE, TIMESTAMPTZ, JSONB, UUID</li>
<li>✅ FOREIGN KEY xato ma'lumotdan saqlaydi</li>
<li>✅ <code>ALTER TABLE</code> — jadval o'zgartirish</li>
<li>✅ ON DELETE CASCADE/RESTRICT/SET NULL — bog'liqlik strategiyalari</li>
</ul>
"""

L8_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 8: CREATE TABLE, ma'lumot turlari va cheklovlar
-- Maqsad: sxema dizayni — jadvallarni o'zingiz yaratasiz
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — oddiy jadval
-- ─────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS buyurtmalar CASCADE;
DROP TABLE IF EXISTS mijozlar CASCADE;

CREATE TABLE mijozlar (
    id          SERIAL PRIMARY KEY,
    ism         VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    yosh        INTEGER      CHECK (yosh >= 0 AND yosh <= 150),
    telefon     VARCHAR(20),
    yaratilgan  TIMESTAMPTZ  DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — FOREIGN KEY bilan jadval
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE buyurtmalar (
    id          SERIAL PRIMARY KEY,
    mijoz_id    INTEGER       NOT NULL
                REFERENCES mijozlar(id) ON DELETE CASCADE,
    summa       NUMERIC(10,2) NOT NULL CHECK (summa > 0),
    holat       VARCHAR(20)   NOT NULL DEFAULT 'kutmoqda'
                CHECK (holat IN ('kutmoqda','tasdiqlangan','bekor')),
    sana        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — sinash uchun ma'lumot
-- ─────────────────────────────────────────────────────────────────────

INSERT INTO mijozlar (ism, email, yosh) VALUES
    ('Aziz',    'aziz@example.uz',   28),
    ('Dilnoza', 'dilya@example.uz',  34),
    ('Sardor',  'sardor@example.uz', 25);

INSERT INTO buyurtmalar (mijoz_id, summa, holat) VALUES
    (1, 150000.00, 'tasdiqlangan'),
    (1,  45000.00, 'kutmoqda'),
    (2, 230000.00, 'tasdiqlangan');

-- Tekshirish
SELECT m.ism, b.summa, b.holat
FROM buyurtmalar b
JOIN mijozlar m ON m.id = b.mijoz_id;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — cheklovlar ishini ko'rsatish
-- ─────────────────────────────────────────────────────────────────────

-- Mavjud bo'lmagan mijoz id bilan
-- INSERT INTO buyurtmalar (mijoz_id, summa) VALUES (9999, 100);
-- ERROR: violates foreign key

-- UNIQUE email
-- INSERT INTO mijozlar (ism, email) VALUES ('Boshqa', 'aziz@example.uz');
-- ERROR: duplicate key value

-- CHECK yosh
-- INSERT INTO mijozlar (ism, email, yosh) VALUES ('Bot', 'b@b.uz', -5);
-- ERROR: violates check constraint

-- CHECK holat
-- INSERT INTO buyurtmalar (mijoz_id, summa, holat) VALUES (1, 100, 'xato_status');
-- ERROR: violates check constraint

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — ALTER TABLE
-- ─────────────────────────────────────────────────────────────────────

-- Yangi ustun
ALTER TABLE mijozlar
    ADD COLUMN viplik BOOLEAN NOT NULL DEFAULT FALSE;

-- Ustun nomini o'zgartirish
ALTER TABLE mijozlar RENAME COLUMN viplik TO vip;

-- Ustun turini o'zgartirish (NULL'siz qiymat majburiy bo'lsa kerak)
ALTER TABLE buyurtmalar ALTER COLUMN summa TYPE NUMERIC(12,2);

-- Cheklov qo'shish
ALTER TABLE mijozlar
    ADD CONSTRAINT unik_telefon UNIQUE (telefon);

-- Cheklovni o'chirish
ALTER TABLE mijozlar DROP CONSTRAINT IF EXISTS unik_telefon;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — Multi-column UNIQUE
-- ─────────────────────────────────────────────────────────────────────

-- Bir kunda bir xil summa bilan ikkita bir xil mijoz buyurtmasi bo'lmasin
ALTER TABLE buyurtmalar
    ADD CONSTRAINT bir_kun_takror UNIQUE (mijoz_id, summa, sana);

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 7 — Jadvalni o'chirish
-- ─────────────────────────────────────────────────────────────────────

-- Ehtiyot — qaytarib bo'lmaydi!
-- DROP TABLE buyurtmalar;
-- DROP TABLE mijozlar CASCADE;  -- bog'liq jadvallarni ham o'chiradi
"""
L9_TEXT = """\
<h2>Indekslar va EXPLAIN — tezlikning kaliti</h2>

<pre class="mermaid">
flowchart LR
    Q["SELECT ... WHERE email='x'"] --> P["Planner"]
    P -->|index bor| IX["Index Scan: ~1ms"]
    P -->|index yo'q| SQ["Seq Scan: 5000ms"]
</pre>

<p>1M qator bor jadvalda <code>WHERE email = 'olim@uz'</code> so'rovi kerak. Indeks bo'lmasa — PostgreSQL har qatorni ko'rib chiqadi (5 soniya). Indeks bo'lsa — to'g'ri kelgan qatorga 0.001 soniyada o'tadi. Bu — DB tezligining asosi.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi indeks</h4>
<pre><code>-- Email bo'yicha tez qidiruv
CREATE INDEX idx_mijozlar_email ON mijozlar(email);

-- Telefon ham
CREATE INDEX idx_mijozlar_telefon ON mijozlar(telefon);

-- Multi-column — tartib MUHIM
CREATE INDEX idx_buyurtma_mijoz_sana ON buyurtmalar(mijoz_id, sana);</code></pre>

<h4>BLOKA 2 — EXPLAIN bilan tekshirish</h4>
<pre><code>EXPLAIN SELECT * FROM mijozlar WHERE email = 'aziz@example.uz';
-- Index Scan using idx_mijozlar_email on mijozlar  (cost=0.15..8.17 rows=1 width=...)
--   Index Cond: ((email)::text = 'aziz@example.uz'::text)

EXPLAIN SELECT * FROM mijozlar WHERE ism = 'Aziz';
-- Seq Scan on mijozlar  (cost=0.00..15.00 rows=1)
--   Filter: ((ism)::text = 'Aziz'::text)
-- (ism uchun indeks yo'q — sekvensial skan)</code></pre>

<h4>BLOKA 3 — EXPLAIN ANALYZE (real ijro)</h4>
<pre><code>EXPLAIN ANALYZE
SELECT m.ism, COUNT(b.id) AS buyurtmalar
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
GROUP BY m.id;
-- haqiqiy vaqtni ko'rsatadi (Execution Time: 0.234 ms)</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>-- Indeks bor — lekin ishlatilmaydi
CREATE INDEX idx_email ON mijozlar(email);

EXPLAIN SELECT * FROM mijozlar WHERE LOWER(email) = 'aziz@example.uz';
-- Seq Scan (!!!)  — chunki LOWER() — funksiya, "email" emas</code></pre>

<p><strong>Sabab:</strong> Indeks <code>email</code> ustini bilad — lekin <code>LOWER(email)</code> — boshqa ifoda. Yechim: <strong>functional index</strong>:</p>

<pre><code>CREATE INDEX idx_email_lower ON mijozlar(LOWER(email));

-- Endi:
EXPLAIN SELECT * FROM mijozlar WHERE LOWER(email) = 'aziz@example.uz';
-- Index Scan using idx_email_lower</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Indeks nima va qanday ishlaydi</h4>
<p>Indeks — bu kitobning <em>indeksiga</em> o'xshaydi: har sahifani o'qish o'rniga, sizga kerakli sahifani topish. PostgreSQL'da default — B-tree (saralangan daraxt):</p>

<pre><code>           [50]
          /    \\
       [25]    [75]
       / \\     / \\
     [10][40] [60][90]</code></pre>

<p>Qidiruv: <code>WHERE id = 60</code> — 50&gt;60? yo'q → 75? 60 dan katta? yo'q → 60 topildi. 3 ta solishtirish (log N).</p>

<h4>2. Indeks turlari</h4>
<table>
<tr><th>Tur</th><th>Qachon</th></tr>
<tr><td><strong>B-tree</strong> (default)</td><td>= &lt; &gt; BETWEEN — universal</td></tr>
<tr><td><strong>Hash</strong></td><td>faqat <code>=</code> uchun (kam tavsiya)</td></tr>
<tr><td><strong>GIN</strong></td><td>JSONB, text search, arrays</td></tr>
<tr><td><strong>GiST</strong></td><td>geometriya, range</td></tr>
<tr><td><strong>BRIN</strong></td><td>juda katta, vaqt bo'yicha tartibli (loglar)</td></tr>
</table>

<h4>3. Multi-column index — tartibga e'tibor</h4>
<pre><code>CREATE INDEX idx_a_b ON jadval(A, B);

-- ISHLAYDI:
WHERE A = ?
WHERE A = ? AND B = ?
WHERE A = ? ORDER BY B

-- ISHLAMAYDI (yoki yarim):
WHERE B = ?           -- A yo'q
WHERE B = ? AND A = ? -- bu ham ishlaydi, planner aniqlaydi</code></pre>

<p>Qoidasi: <strong>tez-tez ishlatiladigan</strong> ustun birinchi, <strong>kam tanlanadiganlar</strong> oxirida.</p>

<h4>4. Qachon indeks ishlatib bo'lmaydi</h4>
<ul>
<li><strong>Ustunga funksiya qo'llanganda</strong> — <code>WHERE LOWER(email) = ...</code> (functional index kerak)</li>
<li><strong>Hisoblash qilinganda</strong> — <code>WHERE ball + 5 &gt; 80</code></li>
<li><strong>LIKE '%lo%'</strong> — boshida % bo'lsa indeks samarasiz (oxirida % bo'lsa ishlaydi)</li>
<li><strong>Kichik jadvallarda</strong> — DB Seq Scan tezroq deb hisoblaydi</li>
<li><strong>OR bilan ko'p ustun aralash</strong> — har biriga alohida indeks kerak</li>
</ul>

<h4>5. Partial Index — kerakli qismi uchun</h4>
<pre><code>-- Faqat faol buyurtmalar uchun indeks (kichkina va tez)
CREATE INDEX idx_faol_buyurtmalar
ON buyurtmalar(sana)
WHERE holat = 'kutmoqda';</code></pre>

<h4>6. EXPLAIN o'qish</h4>
<table>
<tr><th>Belgi</th><th>Yaxshi/Yomon</th></tr>
<tr><td>Index Scan</td><td>✅ yaxshi</td></tr>
<tr><td>Index Only Scan</td><td>✅✅ a'lo</td></tr>
<tr><td>Bitmap Index Scan</td><td>✅ ko'p qator + indeks</td></tr>
<tr><td>Seq Scan</td><td>⚠️ katta jadvalda muammo</td></tr>
<tr><td>Nested Loop</td><td>kichik tomon uchun ok</td></tr>
<tr><td>Hash Join / Merge Join</td><td>katta natija uchun yaxshi</td></tr>
</table>

<h4>7. Indeks narxi — bepul emas</h4>
<p>Indeks SELECT ni tezlashtiradi, lekin INSERT/UPDATE/DELETE ni <em>sekinlashtiradi</em> (har yangi qator har indeksga qo'shilishi kerak). Diskni ham yeydi. Shuning uchun "har ustunga indeks" — emas, balki <strong>tez-tez WHERE/JOIN/ORDER BY da ishlatiladigan</strong> ustunlarga.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>CREATE INDEX idx_... ON jadval(ustun)</code></li>
<li>✅ <code>EXPLAIN</code> — plan ko'rish, <code>EXPLAIN ANALYZE</code> — real vaqt</li>
<li>✅ B-tree default; GIN — JSONB/array uchun</li>
<li>✅ Multi-column indeks va ustun tartibi</li>
<li>✅ Ustun ustida funksiya — indeksni "ko'r" qiladi (functional index kerak)</li>
<li>✅ Indeks bepul emas — yozish narxini oshiradi</li>
<li>✅ Partial index — kichikroq, tezroq</li>
</ul>
"""

L9_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 9: Indekslar va EXPLAIN
-- Maqsad: tezroq so'rovlar va ularni o'lchash
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- Tayyorgarlik — katta jadval (10000 qator)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS log (
    id      SERIAL PRIMARY KEY,
    foydalanuvchi_id INTEGER NOT NULL,
    daraja  VARCHAR(10) NOT NULL,
    matn    TEXT,
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10000 qator generate
INSERT INTO log (foydalanuvchi_id, daraja, matn)
SELECT
    (random() * 100)::INTEGER,
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'INFO'
        WHEN 1 THEN 'WARN'
        ELSE 'ERROR'
    END,
    'log yozuvi #' || generate_series
FROM generate_series(1, 10000);

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — indekssiz EXPLAIN
-- ─────────────────────────────────────────────────────────────────────

-- Seq Scan ko'ramiz
EXPLAIN ANALYZE
SELECT * FROM log WHERE foydalanuvchi_id = 42;
-- Seq Scan ...  10000 qator skan, masalan 2 ms

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — indeks qo'shamiz
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_log_user ON log(foydalanuvchi_id);

-- Endi qaytadan EXPLAIN
EXPLAIN ANALYZE
SELECT * FROM log WHERE foydalanuvchi_id = 42;
-- Index Scan / Bitmap Index Scan ... 0.05 ms

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — multi-column indeks
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_log_user_level ON log(foydalanuvchi_id, daraja);

-- Foydalanuvchi + daraja birga
EXPLAIN ANALYZE
SELECT COUNT(*) FROM log
WHERE foydalanuvchi_id = 42 AND daraja = 'ERROR';
-- Index Only Scan!

-- Faqat daraja — yarim ishlaydi (B-tree multi'da birinchi ustun shart)
EXPLAIN ANALYZE
SELECT * FROM log WHERE daraja = 'ERROR';
-- Hammasi: Seq Scan yoki Bitmap

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — funksiya bilan indeks (xato)
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_log_matn ON log(matn);

-- LOWER bilan — indeks ishlamaydi
EXPLAIN ANALYZE
SELECT * FROM log WHERE LOWER(matn) = 'log yozuvi #100';
-- Seq Scan

-- Functional indeks
CREATE INDEX idx_log_matn_lower ON log(LOWER(matn));

-- Endi indeks ishlaydi
EXPLAIN ANALYZE
SELECT * FROM log WHERE LOWER(matn) = 'log yozuvi #100';
-- Index Scan

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — Partial index
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_faqat_errorlar
ON log(yaratilgan)
WHERE daraja = 'ERROR';

-- Bu indeks faqat ERRORlar uchun — kichik va tez
EXPLAIN ANALYZE
SELECT * FROM log
WHERE daraja = 'ERROR'
  AND yaratilgan > NOW() - INTERVAL '1 hour';

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — indeks ro'yxati va o'chirish
-- ─────────────────────────────────────────────────────────────────────

-- Jadvaldagi barcha indekslar
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS hajm
FROM pg_indexes
WHERE tablename = 'log';

-- Indeksni o'chirish
DROP INDEX IF EXISTS idx_log_matn;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 7 — JOIN qachon indeksdan foyda ko'radi
-- ─────────────────────────────────────────────────────────────────────

-- FK ustunlariga doim indeks qo'ying!
-- PostgreSQL avtomatik ravishda FOREIGN KEY uchun indeks YARATMAYDI.

EXPLAIN ANALYZE
SELECT m.ism, COUNT(b.id)
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
GROUP BY m.id, m.ism;

-- Agar buyurtmalar.mijoz_id da indeks bo'lmasa — har JOIN Seq Scan
-- bo'ladi. Indeks qo'shing:
-- CREATE INDEX idx_buyurtma_mijoz ON buyurtmalar(mijoz_id);
"""
R3_TEXT = """\
<h2>R3 — Modul 3 takrorlash: Blog DB sxemasi</h2>

<p>3-modulning butun mazmunini bitta amaliy loyihada birlashtiramiz: <strong>blog DB sxemasini noldan yaratish</strong>. Bu — Flask/FastAPI bilan ishlay boshlaganingizda har kuni qiladigan ish.</p>

<h3>Loyihaning talablari</h3>
<ul>
<li>Foydalanuvchilar postlar yozadi</li>
<li>Postlar teglarga ega (M:N munosabat)</li>
<li>Foydalanuvchilar postlarga izoh yozadi</li>
<li>Postlar va izohlar ehtiyot tartibida o'chiriladi (audit muhim — RESTRICT)</li>
</ul>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Sxema</h4>
<p>4 ta jadval yarating: <code>foydalanuvchilar</code>, <code>postlar</code>, <code>izohlar</code>, <code>teglar</code> va bog'lovchi <code>post_teglar</code>.</p>

<h4>Vazifa 2 — Test ma'lumoti</h4>
<p>3 ta foydalanuvchi, 5 ta post, 4 ta teg, 8 ta izohga ega bo'ladigan INSERT'lar yozing. Tranzaksiya ichida.</p>

<h4>Vazifa 3 — Indekslar</h4>
<p>Tez-tez qidirish bo'ladigan ustunlarga indeks qo'shing: foydalanuvchi email, post yaratilgan sanasi, izoh post_id.</p>

<h4>Vazifa 4 — Hisobotlar</h4>
<ul>
<li>Eng faol foydalanuvchi (post + izoh soni)</li>
<li>Eng mashhur teg (postlar soni)</li>
<li>Har postning izohlar soni va oxirgi izoh sanasi</li>
<li>0 izohli postlar (LEFT JOIN)</li>
</ul>

<h4>Vazifa 5 — Performance</h4>
<p>Bitta hisobotni <code>EXPLAIN ANALYZE</code> bilan tekshiring, indekslar ishlayotganini ko'ring.</p>

<h3>🐛 Ataylab qiyin: M:N munosabat</h3>
<p>Postlar va teglar — har post ko'p tegga, har teg ko'p postga ega bo'lishi mumkin. Bunday holatda <em>uchinchi jadval</em> kerak: <code>post_teglar (post_id, teg_id)</code>. Bu — relyatsion modellashda eng asosiy nayrang.</p>

<h3>Yechimlar</h3>

<details>
<summary>Vazifa 1 — Sxema</summary>
<pre><code>CREATE TABLE foydalanuvchilar (
    id           SERIAL PRIMARY KEY,
    ism          VARCHAR(50)  NOT NULL,
    email        VARCHAR(100) UNIQUE NOT NULL,
    yaratilgan   TIMESTAMPTZ  DEFAULT NOW()
);

CREATE TABLE postlar (
    id           SERIAL PRIMARY KEY,
    muallif_id   INTEGER NOT NULL REFERENCES foydalanuvchilar(id) ON DELETE RESTRICT,
    sarlavha     VARCHAR(200) NOT NULL,
    matn         TEXT NOT NULL,
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE izohlar (
    id           SERIAL PRIMARY KEY,
    post_id      INTEGER NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif_id   INTEGER NOT NULL REFERENCES foydalanuvchilar(id),
    matn         TEXT NOT NULL,
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE teglar (
    id   SERIAL PRIMARY KEY,
    nomi VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE post_teglar (
    post_id INTEGER REFERENCES postlar(id) ON DELETE CASCADE,
    teg_id  INTEGER REFERENCES teglar(id)  ON DELETE CASCADE,
    PRIMARY KEY (post_id, teg_id)
);</code></pre>
</details>

<details>
<summary>Vazifa 4 — Eng faol foydalanuvchi</summary>
<pre><code>SELECT
    f.ism,
    COUNT(DISTINCT p.id) AS postlar,
    COUNT(DISTINCT i.id) AS izohlar,
    COUNT(DISTINCT p.id) + COUNT(DISTINCT i.id) AS jami
FROM foydalanuvchilar f
LEFT JOIN postlar  p ON p.muallif_id = f.id
LEFT JOIN izohlar  i ON i.muallif_id = f.id
GROUP BY f.id, f.ism
ORDER BY jami DESC;</code></pre>
</details>

<details>
<summary>Vazifa 4 — Har postning izohlar statistikasi</summary>
<pre><code>SELECT
    p.sarlavha,
    COUNT(i.id)      AS izohlar_soni,
    MAX(i.yaratilgan) AS oxirgi_izoh
FROM postlar p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY izohlar_soni DESC;</code></pre>
</details>

<details>
<summary>Vazifa 4 — 0 izohli postlar</summary>
<pre><code>SELECT p.sarlavha
FROM postlar p
LEFT JOIN izohlar i ON i.post_id = p.id
WHERE i.id IS NULL;</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Sxemani noldan yaratish (4-5 jadval)</li>
<li>✅ M:N munosabat — bog'lovchi jadval bilan</li>
<li>✅ ON DELETE CASCADE vs RESTRICT — har joyga mos</li>
<li>✅ FK ustuniga indeks qo'shish — JOIN performance</li>
<li>✅ Real hisobotlar — LEFT JOIN + GROUP BY birga</li>
</ul>
"""

R3_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- REVISION 3: Blog DB sxemasi
-- Modul 3: CREATE TABLE + INSERT/UPDATE/DELETE + indekslar
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- TOZALASH (idempotent)
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS post_teglar CASCADE;
DROP TABLE IF EXISTS izohlar CASCADE;
DROP TABLE IF EXISTS postlar CASCADE;
DROP TABLE IF EXISTS teglar CASCADE;
DROP TABLE IF EXISTS foydalanuvchilar CASCADE;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 1: Sxema
-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE foydalanuvchilar (
    id          SERIAL PRIMARY KEY,
    ism         VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    yaratilgan  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE postlar (
    id          SERIAL PRIMARY KEY,
    muallif_id  INTEGER NOT NULL REFERENCES foydalanuvchilar(id) ON DELETE RESTRICT,
    sarlavha    VARCHAR(200) NOT NULL,
    matn        TEXT NOT NULL,
    yaratilgan  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE izohlar (
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif_id  INTEGER NOT NULL REFERENCES foydalanuvchilar(id),
    matn        TEXT NOT NULL,
    yaratilgan  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE teglar (
    id   SERIAL PRIMARY KEY,
    nomi VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE post_teglar (
    post_id INTEGER NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    teg_id  INTEGER NOT NULL REFERENCES teglar(id)  ON DELETE CASCADE,
    PRIMARY KEY (post_id, teg_id)
);

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 2: Tranzaksiya ichida test ma'lumoti
-- ─────────────────────────────────────────────────────────────────────

BEGIN;

INSERT INTO foydalanuvchilar (ism, email) VALUES
    ('Aziz',    'aziz@blog.uz'),
    ('Dilnoza', 'dilnoza@blog.uz'),
    ('Sardor',  'sardor@blog.uz');

INSERT INTO teglar (nomi) VALUES
    ('python'), ('sql'), ('django'), ('react');

INSERT INTO postlar (muallif_id, sarlavha, matn) VALUES
    (1, 'Python boshlovchilarga',  'Asoslari haqida...'),
    (1, 'SQL ham oddiy',           'SELECT * FROM ...'),
    (2, 'Djangoda autentifikatsiya','Foydalanuvchi tizimi...'),
    (2, 'React komponentlari',     'JSX va props...'),
    (3, 'PostgreSQL JOIN turlari', 'INNER, LEFT, RIGHT...');

INSERT INTO post_teglar (post_id, teg_id) VALUES
    (1, 1),         -- python
    (2, 2),         -- sql
    (3, 3), (3, 1), -- django + python
    (4, 4),         -- react
    (5, 2);         -- sql

INSERT INTO izohlar (post_id, muallif_id, matn) VALUES
    (1, 2, 'Juda foydali!'),
    (1, 3, 'Yaxshi yozilgan'),
    (2, 1, 'Davom eting'),
    (2, 3, 'SQL maqolasi kerak edi'),
    (3, 1, 'Faqat django emas, FastAPI ham keting'),
    (3, 3, 'Authentication qiyin mavzu'),
    (5, 1, 'PostgreSQL ajoyib'),
    (5, 2, 'JOIN larni qayta o''rgandim');

COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 3: Indekslar
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_foyd_email     ON foydalanuvchilar(email);
CREATE INDEX idx_post_muallif   ON postlar(muallif_id);
CREATE INDEX idx_post_yaratil   ON postlar(yaratilgan DESC);
CREATE INDEX idx_izoh_post      ON izohlar(post_id);
CREATE INDEX idx_izoh_muallif   ON izohlar(muallif_id);

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 4: Hisobotlar
-- ─────────────────────────────────────────────────────────────────────

-- 4a) Eng faol foydalanuvchi
SELECT
    f.ism,
    COUNT(DISTINCT p.id) AS postlar,
    COUNT(DISTINCT i.id) AS izohlar,
    COUNT(DISTINCT p.id) + COUNT(DISTINCT i.id) AS jami
FROM foydalanuvchilar f
LEFT JOIN postlar p ON p.muallif_id = f.id
LEFT JOIN izohlar i ON i.muallif_id = f.id
GROUP BY f.id, f.ism
ORDER BY jami DESC;

-- 4b) Eng mashhur teg
SELECT t.nomi, COUNT(*) AS postlar_soni
FROM teglar t
JOIN post_teglar pt ON pt.teg_id = t.id
GROUP BY t.id, t.nomi
ORDER BY postlar_soni DESC;

-- 4c) Har postning izohlar statistikasi
SELECT
    p.sarlavha,
    COUNT(i.id)       AS izohlar_soni,
    MAX(i.yaratilgan) AS oxirgi_izoh
FROM postlar p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY izohlar_soni DESC;

-- 4d) 0 izohli postlar
SELECT p.sarlavha
FROM postlar p
LEFT JOIN izohlar i ON i.post_id = p.id
WHERE i.id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- Vazifa 5: EXPLAIN ANALYZE
-- ─────────────────────────────────────────────────────────────────────

EXPLAIN ANALYZE
SELECT p.sarlavha, COUNT(i.id) AS izohlar
FROM postlar p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY izohlar DESC;
-- Index Scan / Bitmap Scan ko'rinishi kerak (idx_izoh_post indeks ishlaydi)
"""
L10_TEXT = """\
<h2>Subqueries, CTE va Window funksiyalar</h2>

<pre class="mermaid">
flowchart LR
    SQ["Subquery\nso'rov ichida so'rov"] --> R["natija"]
    CTE["WITH ... AS\no'qish oson"] --> R
    WIN["Window funcs\nqator ustida hisob"] --> R
</pre>

<p>Bu — kursning eng kuchli darslaridan biri. Endi siz "har sinfning top-3 talabasi" yoki "har oydagi o'sish foizi" kabi so'rovlarni yoza olasiz. Bularsiz dashboard'lar mavjud emas.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Subquery</h4>
<pre><code>-- Maktab o'rtachasidan yuqori balli talabalar
SELECT ism, ball
FROM talabalar
WHERE ball &gt; (SELECT AVG(ball) FROM talabalar);

-- IN bilan
SELECT * FROM talabalar
WHERE id IN (
    SELECT talaba_id FROM baholar WHERE baho &gt;= 95
);

-- EXISTS bilan (tezroq IN'dan)
SELECT * FROM talabalar t
WHERE EXISTS (
    SELECT 1 FROM baholar b
    WHERE b.talaba_id = t.id AND b.baho &gt;= 95
);</code></pre>

<h4>BLOKA 2 — CTE (Common Table Expression)</h4>
<pre><code>WITH sinf_stats AS (
    SELECT sinf, AVG(ball) AS ortacha
    FROM talabalar
    GROUP BY sinf
)
SELECT t.ism, t.sinf, t.ball, s.ortacha
FROM talabalar t
JOIN sinf_stats s ON s.sinf = t.sinf
WHERE t.ball &gt; s.ortacha;
-- Har sinfdagi o'rtachadan yuqori talabalar</code></pre>

<p>CTE — subquery'ning chiroyli ko'rinishi. <em>O'qish</em> osonroq, va bir necha marta ishlatish mumkin.</p>

<h4>BLOKA 3 — Window funksiyalar</h4>
<pre><code>-- Har sinfdagi reyting
SELECT
    ism,
    sinf,
    ball,
    ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC) AS o_rin
FROM talabalar;
-- Olim   | 11-A | 87 | 2
-- Karim  | 11-A | 91 | 1
-- Salim  | 11-B | 58 | 1
-- ...</code></pre>

<p><code>OVER (PARTITION BY sinf ORDER BY ball DESC)</code> — "har sinf ichida ballarni saralab, raqamla". Bu — window funksiyalarning sehri.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>-- Har sinfdan top-1 talaba
SELECT ism, sinf, MAX(ball) FROM talabalar GROUP BY sinf;
-- 11-A | 91   (lekin Karim'mi yoki Olim'mi?)</code></pre>

<p><strong>Natija:</strong> Xato chiqarmaydi (PostgreSQL'da chiqaradi), lekin <em>ism</em> kim ekanligi noaniq. To'g'risi — window funksiya bilan:</p>

<pre><code>WITH rangs AS (
    SELECT ism, sinf, ball,
           ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC) AS r
    FROM talabalar
)
SELECT ism, sinf, ball FROM rangs WHERE r = 1;</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Subquery turlari</h4>
<table>
<tr><th>Tur</th><th>Misol</th></tr>
<tr><td>Scalar (1 ta qiymat)</td><td><code>WHERE ball &gt; (SELECT AVG(ball) FROM talabalar)</code></td></tr>
<tr><td>Column (1 ta ustun)</td><td><code>WHERE id IN (SELECT talaba_id ...)</code></td></tr>
<tr><td>Row (1 ta qator)</td><td><code>WHERE (a, b) = (SELECT a, b FROM ...)</code></td></tr>
<tr><td>Table (jadval)</td><td><code>FROM (SELECT ...) sq</code></td></tr>
<tr><td>EXISTS</td><td><code>WHERE EXISTS (SELECT 1 ...)</code> — tezroq</td></tr>
</table>

<h4>2. CTE — WITH ... AS</h4>
<pre><code>WITH
    a AS (SELECT ...),
    b AS (SELECT ... FROM a WHERE ...)
SELECT ... FROM b;</code></pre>

<p>Bir nechta CTE'ni ketma-ket yozish mumkin. Har biri keyingisida ishlatiladi.</p>

<h4>3. Recursive CTE</h4>
<pre><code>-- 1 dan 10 gacha
WITH RECURSIVE sonlar AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM sonlar WHERE n &lt; 10
)
SELECT * FROM sonlar;
-- 1, 2, 3, ..., 10</code></pre>

<p>Recursive CTE — daraxt strukturasi (kategoriya iyerarxiyasi, org chart) uchun.</p>

<h4>4. Window funksiyalar to'liq</h4>
<table>
<tr><th>Funksiya</th><th>Vazifa</th></tr>
<tr><td><code>ROW_NUMBER()</code></td><td>1, 2, 3, ...</td></tr>
<tr><td><code>RANK()</code></td><td>1, 2, 2, 4, ... (tenglarga bir xil)</td></tr>
<tr><td><code>DENSE_RANK()</code></td><td>1, 2, 2, 3, ... (oraliq kalit yo'q)</td></tr>
<tr><td><code>LAG(x, 1)</code></td><td>oldingi qatordan x</td></tr>
<tr><td><code>LEAD(x, 1)</code></td><td>keyingi qatordan x</td></tr>
<tr><td><code>FIRST_VALUE(x)</code></td><td>oynaning birinchi qiymati</td></tr>
<tr><td><code>SUM(x) OVER (...)</code></td><td>kumulyativ yig'indi</td></tr>
<tr><td><code>AVG(x) OVER (...)</code></td><td>moving average</td></tr>
</table>

<h4>5. OVER (PARTITION BY ... ORDER BY ...)</h4>
<pre><code>-- Faqat tartib (jami top)
ROW_NUMBER() OVER (ORDER BY ball DESC)

-- Har sinfda alohida tartib
ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC)

-- Kumulyativ ball
SUM(ball) OVER (ORDER BY id)</code></pre>

<h4>6. LAG/LEAD — oldingi va keyingi</h4>
<pre><code>-- Har talaba va undan oldingi balli farqi
SELECT
    ism,
    ball,
    LAG(ball, 1) OVER (ORDER BY ball DESC) AS oldingi,
    ball - LAG(ball, 1) OVER (ORDER BY ball DESC) AS farq
FROM talabalar;</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Subquery (Scalar/Column/Table/EXISTS) — so'rov ichida so'rov</li>
<li>✅ <code>WITH ... AS</code> — CTE bilan o'qishni osonlashtirish</li>
<li>✅ <code>WITH RECURSIVE</code> — iyerarxiya uchun</li>
<li>✅ <code>ROW_NUMBER/RANK/DENSE_RANK</code> — reyting</li>
<li>✅ <code>LAG/LEAD</code> — oldingi/keyingi qator</li>
<li>✅ <code>SUM/AVG OVER (...)</code> — kumulyativ/moving</li>
<li>✅ <code>PARTITION BY</code> — guruh ichida tartib</li>
</ul>
"""

L10_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- DARS 10: Subqueries, CTE va Window funksiyalar
-- Maqsad: chuqurroq tahliliy so'rovlar
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 1 — Subquery turlari
-- ─────────────────────────────────────────────────────────────────────

-- 1a) Scalar — bitta qiymat
SELECT ism, ball
FROM talabalar
WHERE ball > (SELECT AVG(ball) FROM talabalar);

-- 1b) IN — ro'yxat
SELECT ism FROM talabalar
WHERE id IN (
    SELECT talaba_id FROM baholar WHERE baho >= 95
);

-- 1c) EXISTS — odatda tezroq
SELECT ism FROM talabalar t
WHERE EXISTS (
    SELECT 1 FROM baholar b
    WHERE b.talaba_id = t.id AND b.baho >= 95
);

-- 1d) Korelatsion — har qator uchun ichki so'rov
SELECT
    ism,
    ball,
    (SELECT AVG(ball) FROM talabalar) AS umumiy_ortacha,
    ball - (SELECT AVG(ball) FROM talabalar) AS farq
FROM talabalar;

-- 1e) FROM ichida — jadval kabi
SELECT sq.sinf, sq.ortacha
FROM (
    SELECT sinf, AVG(ball) AS ortacha
    FROM talabalar
    GROUP BY sinf
) sq
WHERE sq.ortacha > 80;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 2 — CTE (WITH ... AS)
-- ─────────────────────────────────────────────────────────────────────

WITH sinf_stats AS (
    SELECT sinf, AVG(ball) AS ortacha, COUNT(*) AS soni
    FROM talabalar
    GROUP BY sinf
)
SELECT t.ism, t.sinf, t.ball, s.ortacha
FROM talabalar t
JOIN sinf_stats s ON s.sinf = t.sinf
WHERE t.ball > s.ortacha
ORDER BY t.sinf, t.ball DESC;

-- Bir nechta CTE
WITH
yuqori AS (
    SELECT * FROM talabalar WHERE ball >= 80
),
pastki AS (
    SELECT * FROM talabalar WHERE ball < 80
)
SELECT
    (SELECT COUNT(*) FROM yuqori) AS a_lochilar,
    (SELECT COUNT(*) FROM pastki) AS qolganlar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 3 — Recursive CTE
-- ─────────────────────────────────────────────────────────────────────

-- 1 dan 10 gacha sonlar
WITH RECURSIVE sonlar AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM sonlar WHERE n < 10
)
SELECT * FROM sonlar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 4 — Window: ROW_NUMBER, RANK, DENSE_RANK
-- ─────────────────────────────────────────────────────────────────────

-- Umumiy reyting (1 dan to N gacha)
SELECT
    ism,
    ball,
    ROW_NUMBER() OVER (ORDER BY ball DESC) AS o_rin,
    RANK()       OVER (ORDER BY ball DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY ball DESC) AS dense
FROM talabalar;

-- Har sinfda alohida reyting
SELECT
    ism,
    sinf,
    ball,
    ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC) AS sinf_o_rin
FROM talabalar;

-- Har sinfdan TOP-1
WITH r AS (
    SELECT ism, sinf, ball,
           ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC) AS rn
    FROM talabalar
)
SELECT ism, sinf, ball
FROM r WHERE rn = 1;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 5 — LAG, LEAD
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ism,
    ball,
    LAG(ball, 1)  OVER (ORDER BY ball DESC) AS oldingi,
    LEAD(ball, 1) OVER (ORDER BY ball DESC) AS keyingi,
    ball - LAG(ball, 1) OVER (ORDER BY ball DESC) AS farq
FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 6 — Kumulyativ va Moving Average
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ism,
    ball,
    SUM(ball) OVER (ORDER BY id) AS kumulyativ,
    ROUND(AVG(ball) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1)
        AS moving_avg_3
FROM talabalar;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 7 — Foiz hisoblash
-- ─────────────────────────────────────────────────────────────────────

SELECT
    ism,
    ball,
    ROUND(ball * 100.0 / SUM(ball) OVER (), 1) AS foiz
FROM talabalar
ORDER BY foiz DESC;

-- ─────────────────────────────────────────────────────────────────────
-- BLOKA 8 — Har fan bo'yicha top-1 (real misol)
-- ─────────────────────────────────────────────────────────────────────

WITH rangs AS (
    SELECT
        f.nomi AS fan,
        t.ism,
        b.baho,
        ROW_NUMBER() OVER (PARTITION BY f.id ORDER BY b.baho DESC) AS r
    FROM baholar b
    JOIN fanlar f    ON f.id = b.fan_id
    JOIN talabalar t ON t.id = b.talaba_id
)
SELECT fan, ism, baho FROM rangs WHERE r = 1;
"""
L11_TEXT = """\
<h2>🚀 CAPSTONE: E-commerce tahlil tizimi</h2>

<pre class="mermaid">
flowchart TB
    M["mijozlar"] --> B["buyurtmalar"]
    B --> BE["buyurtma_elementlari"]
    BE --> MH["mahsulotlar"]
    MH --> K["kategoriyalar"]
</pre>

<p>Endi siz to'liq SQL ishchisisiz. Yakuniy loyiha — <strong>real e-commerce shirkati</strong> uchun tahlil tizimi: sxema, ma'lumot, indekslar va 15+ ta murakkab hisobot. Bu — siz Flask/FastAPI bilan ishlay boshlaganingizda har kuni qiladigan vazifa.</p>

<h3>Sxema</h3>

<table>
<tr><th>Jadval</th><th>Maqsad</th></tr>
<tr><td><code>kategoriyalar</code></td><td>Mahsulot turkumi (Telefon, Kiyim, ...)</td></tr>
<tr><td><code>mahsulotlar</code></td><td>Sotuvga qo'yilgan tovar</td></tr>
<tr><td><code>mijozlar</code></td><td>Xaridorlar</td></tr>
<tr><td><code>buyurtmalar</code></td><td>Har xaridning sarlavhasi</td></tr>
<tr><td><code>buyurtma_elementlari</code></td><td>Bitta buyurtmaning har bir mahsuloti</td></tr>
</table>

<h3>Talab qilinadigan hisobotlar</h3>

<h4>Sotuv tahlili (5 ta)</h4>
<ol>
<li>Jami daromad, jami buyurtmalar soni, o'rtacha chek</li>
<li>Eng ko'p sotilgan TOP-5 mahsulot</li>
<li>Har kategoriya bo'yicha daromad va mahsulotlar soni</li>
<li>Eng faol TOP-5 mijoz (jami xarid summasi)</li>
<li>Daromadning oylik trendi (oxirgi 6 oy)</li>
</ol>

<h4>Murakkab so'rovlar (5 ta)</h4>
<ol start="6">
<li>Har kategoriyaning eng qimmat mahsuloti (window funksiya)</li>
<li>Bir marta xarid qilgan vs takror mijoz (segmentatsiya)</li>
<li>"Birga sotib olinadi" — bir buyurtmada keluvchi mahsulotlar (self JOIN)</li>
<li>Har oyning daromad o'sish foizi (LAG)</li>
<li>Hech qachon sotilmagan mahsulotlar (LEFT JOIN + IS NULL)</li>
</ol>

<h4>Performance (3 ta)</h4>
<ol start="11">
<li>FK ustunlariga indeks qo'yish</li>
<li>2 ta hisobotni EXPLAIN ANALYZE bilan o'lchash</li>
<li>1 ta qimmat so'rovni CTE bilan optimallashtirish</li>
</ol>

<h3>Texnologik talablar</h3>
<ul>
<li>✅ Hamma <code>CREATE TABLE</code> da PRIMARY KEY, FOREIGN KEY, NOT NULL, CHECK</li>
<li>✅ Pul — <code>NUMERIC(10,2)</code></li>
<li>✅ Sana/vaqt — <code>TIMESTAMPTZ</code></li>
<li>✅ Tranzaksiya ichida test ma'lumot</li>
<li>✅ FK ustunlariga indeks</li>
<li>✅ Hisobotlarning kamida 5 tasi window/CTE bilan</li>
<li>✅ Hech bo'lmaganda 1 ta recursive CTE yoki self JOIN</li>
</ul>

<h3>Bonus (ixtiyoriy)</h3>
<ul>
<li>📊 RFM segmentatsiya (Recency, Frequency, Monetary)</li>
<li>📈 Cohort tahlil (mijoz birinchi xarid qilgan oy bo'yicha)</li>
<li>🎯 Mahsulotni tavsiya qilish: "Buni olganlar, buni ham olishadi"</li>
<li>🔍 Materialized View — kun bo'yicha dashboard</li>
<li>⚡ EXPLAIN ANALYZE bilan slow query topish va tuzatish</li>
</ul>

<h3>Yakuniy yo'l xaritasi</h3>
<ol>
<li><strong>Bosqich 1</strong> — sxema yarating (5 jadval)</li>
<li><strong>Bosqich 2</strong> — tranzaksiya bilan test ma'lumot to'ldiring (5 kategoriya, 20 mahsulot, 10 mijoz, 50 buyurtma, 100 element)</li>
<li><strong>Bosqich 3</strong> — indekslar qo'shing</li>
<li><strong>Bosqich 4</strong> — 13 ta hisobot</li>
<li><strong>Bosqich 5</strong> — EXPLAIN ANALYZE bilan tekshirish</li>
<li><strong>Bosqich 6</strong> — bonus</li>
</ol>

<h3>📌 Yakuniy g'olib bayonoti</h3>
<p>Bu loyihani tugatgan dasturchi <strong>Flask/FastAPI/Django</strong> da hech qanday qiyinchiliksiz ORM bilan ishlashga tayyor. ORM faqat SQL ustidan ko'rinish — siz endi har generatsiya qilingan SQL'ni o'qiy olasiz va "nima uchun sekin?" degan savolga javob bera olasiz.</p>

<p>Bu kurs sizga DB <em>foydalanish</em>ni emas, balki <em>tushunish</em>ni o'rgatdi. Keyingi qadam — production'da real biznes muammolarini hal qilish. Omad!</p>
"""

L11_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- 🚀 CAPSTONE: E-commerce tahlil tizimi
-- Yakuniy loyiha — 13 ta hisobot, 5 ta jadval, indekslar, optimizatsiya
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BOSQICH 1: Sxema
-- ─────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS buyurtma_elementlari CASCADE;
DROP TABLE IF EXISTS buyurtmalar CASCADE;
DROP TABLE IF EXISTS mahsulotlar CASCADE;
DROP TABLE IF EXISTS kategoriyalar CASCADE;
DROP TABLE IF EXISTS ec_mijozlar CASCADE;

CREATE TABLE kategoriyalar (
    id   SERIAL PRIMARY KEY,
    nomi VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE mahsulotlar (
    id            SERIAL PRIMARY KEY,
    kategoriya_id INTEGER NOT NULL REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi          VARCHAR(100) NOT NULL,
    narx          NUMERIC(10,2) NOT NULL CHECK (narx > 0),
    zaxira        INTEGER NOT NULL DEFAULT 0 CHECK (zaxira >= 0),
    yaratilgan    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ec_mijozlar (
    id          SERIAL PRIMARY KEY,
    ism         VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    shahar      VARCHAR(50),
    royxatdan   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE buyurtmalar (
    id          SERIAL PRIMARY KEY,
    mijoz_id    INTEGER NOT NULL REFERENCES ec_mijozlar(id) ON DELETE RESTRICT,
    holat       VARCHAR(20) NOT NULL DEFAULT 'tasdiqlangan'
                CHECK (holat IN ('kutmoqda','tasdiqlangan','yetkazildi','bekor')),
    yaratilgan  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE buyurtma_elementlari (
    id            SERIAL PRIMARY KEY,
    buyurtma_id   INTEGER NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id   INTEGER NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor        INTEGER NOT NULL CHECK (miqdor > 0),
    narx_birlik   NUMERIC(10,2) NOT NULL CHECK (narx_birlik > 0)
);

-- ─────────────────────────────────────────────────────────────────────
-- BOSQICH 2: Test ma'lumot (tranzaksiya ichida)
-- ─────────────────────────────────────────────────────────────────────

BEGIN;

INSERT INTO kategoriyalar (nomi) VALUES
    ('Telefonlar'), ('Kompyuter'), ('Kiyim'), ('Kitob'), ('Oziq-ovqat');

INSERT INTO mahsulotlar (kategoriya_id, nomi, narx, zaxira) VALUES
    (1, 'iPhone 15',          15000000, 5),
    (1, 'Samsung S24',        12000000, 8),
    (1, 'Xiaomi 14',           7000000, 15),
    (2, 'MacBook Pro 14',     22000000, 3),
    (2, 'ThinkPad X1',        18000000, 4),
    (2, 'Dell XPS',           14000000, 6),
    (3, 'Adidas krossovka',     800000, 30),
    (3, 'Nike futbolka',        250000, 50),
    (3, 'Levis jeans',          550000, 25),
    (4, 'Atomic Habits',         85000, 100),
    (4, 'Sapiens',              120000, 80),
    (4, 'Clean Code',           180000, 40),
    (5, 'Choy paket',            45000, 200),
    (5, 'Asal 1kg',             120000, 60),
    (5, 'Yong''oq 500g',         95000, 80);

INSERT INTO ec_mijozlar (ism, email, shahar, royxatdan) VALUES
    ('Aziz K',     'aziz@mail.uz',     'Toshkent',  NOW() - INTERVAL '300 days'),
    ('Dilnoza R',  'dilya@mail.uz',    'Samarqand', NOW() - INTERVAL '250 days'),
    ('Sardor T',   'sardor@mail.uz',   'Buxoro',    NOW() - INTERVAL '200 days'),
    ('Madina K',   'madina@mail.uz',   'Toshkent',  NOW() - INTERVAL '150 days'),
    ('Jamol O',    'jamol@mail.uz',    'Andijon',   NOW() - INTERVAL '120 days'),
    ('Nigora B',   'nigora@mail.uz',   'Toshkent',  NOW() - INTERVAL '100 days'),
    ('Akmal X',    'akmal@mail.uz',    'Farg''ona', NOW() - INTERVAL '80 days'),
    ('Lola P',     'lola@mail.uz',     'Toshkent',  NOW() - INTERVAL '60 days');

-- Buyurtmalar — turli oylarda
INSERT INTO buyurtmalar (mijoz_id, yaratilgan, holat) VALUES
    (1, NOW() - INTERVAL '180 days', 'yetkazildi'),
    (1, NOW() - INTERVAL '150 days', 'yetkazildi'),
    (1, NOW() - INTERVAL '20 days',  'yetkazildi'),
    (2, NOW() - INTERVAL '170 days', 'yetkazildi'),
    (2, NOW() - INTERVAL '90 days',  'yetkazildi'),
    (3, NOW() - INTERVAL '100 days', 'yetkazildi'),
    (4, NOW() - INTERVAL '60 days',  'yetkazildi'),
    (4, NOW() - INTERVAL '30 days',  'yetkazildi'),
    (4, NOW() - INTERVAL '10 days',  'tasdiqlangan'),
    (5, NOW() - INTERVAL '40 days',  'yetkazildi'),
    (6, NOW() - INTERVAL '50 days',  'yetkazildi'),
    (6, NOW() - INTERVAL '15 days',  'yetkazildi'),
    (7, NOW() - INTERVAL '20 days',  'tasdiqlangan'),
    (8, NOW() - INTERVAL '5 days',   'kutmoqda');

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik) VALUES
    (1, 1,  1, 15000000),
    (1, 8,  2,   250000),
    (2, 4,  1, 22000000),
    (3, 10, 3,    85000),
    (3, 11, 1,   120000),
    (4, 2,  1, 12000000),
    (4, 9,  1,   550000),
    (5, 13, 5,    45000),
    (6, 3,  1,  7000000),
    (6, 7,  2,   800000),
    (7, 5,  1, 18000000),
    (7, 12, 1,   180000),
    (8, 14, 2,   120000),
    (8, 15, 1,    95000),
    (9, 1,  1, 15000000),
    (10, 6, 1, 14000000),
    (10, 9, 1,  550000),
    (11, 7, 1,  800000),
    (11, 13, 4,  45000),
    (12, 11, 2, 120000),
    (12, 10, 1,  85000),
    (13, 2,  1, 12000000),
    (14, 8,  3,  250000);

COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- BOSQICH 3: Indekslar
-- ─────────────────────────────────────────────────────────────────────

CREATE INDEX idx_mahs_kategoriya ON mahsulotlar(kategoriya_id);
CREATE INDEX idx_buyu_mijoz       ON buyurtmalar(mijoz_id);
CREATE INDEX idx_buyu_yaratilgan  ON buyurtmalar(yaratilgan DESC);
CREATE INDEX idx_buyu_holat       ON buyurtmalar(holat);
CREATE INDEX idx_el_buyurtma      ON buyurtma_elementlari(buyurtma_id);
CREATE INDEX idx_el_mahsulot      ON buyurtma_elementlari(mahsulot_id);
CREATE INDEX idx_mij_email        ON ec_mijozlar(email);

-- ─────────────────────────────────────────────────────────────────────
-- BOSQICH 4: 13 ta hisobot
-- ─────────────────────────────────────────────────────────────────────

-- 1) Jami daromad, buyurtmalar, o'rtacha chek
WITH chek_summasi AS (
    SELECT b.id, SUM(e.miqdor * e.narx_birlik) AS summa
    FROM buyurtmalar b
    JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
    WHERE b.holat IN ('tasdiqlangan','yetkazildi')
    GROUP BY b.id
)
SELECT
    COUNT(*)            AS buyurtmalar_soni,
    SUM(summa)          AS jami_daromad,
    ROUND(AVG(summa), 0) AS ortacha_chek
FROM chek_summasi;

-- 2) TOP-5 sotilgan mahsulot (miqdor bo'yicha)
SELECT
    m.nomi,
    SUM(e.miqdor)               AS jami_miqdor,
    SUM(e.miqdor * e.narx_birlik) AS daromad
FROM buyurtma_elementlari e
JOIN mahsulotlar m ON m.id = e.mahsulot_id
JOIN buyurtmalar b ON b.id = e.buyurtma_id
WHERE b.holat IN ('tasdiqlangan','yetkazildi')
GROUP BY m.id, m.nomi
ORDER BY jami_miqdor DESC
LIMIT 5;

-- 3) Kategoriya bo'yicha daromad
SELECT
    k.nomi AS kategoriya,
    COUNT(DISTINCT m.id) AS mahsulot_turi,
    SUM(e.miqdor)        AS jami_dona,
    SUM(e.miqdor * e.narx_birlik) AS daromad
FROM kategoriyalar k
LEFT JOIN mahsulotlar m ON m.kategoriya_id = k.id
LEFT JOIN buyurtma_elementlari e ON e.mahsulot_id = m.id
LEFT JOIN buyurtmalar b ON b.id = e.buyurtma_id
    AND b.holat IN ('tasdiqlangan','yetkazildi')
GROUP BY k.id, k.nomi
ORDER BY daromad DESC NULLS LAST;

-- 4) TOP-5 mijoz
SELECT
    mz.ism,
    mz.shahar,
    COUNT(DISTINCT b.id)         AS buyurtmalar,
    SUM(e.miqdor * e.narx_birlik) AS jami_xarid
FROM ec_mijozlar mz
JOIN buyurtmalar b ON b.mijoz_id = mz.id
JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
WHERE b.holat IN ('tasdiqlangan','yetkazildi')
GROUP BY mz.id, mz.ism, mz.shahar
ORDER BY jami_xarid DESC
LIMIT 5;

-- 5) Oylik trend
SELECT
    DATE_TRUNC('month', b.yaratilgan)::DATE AS oy,
    COUNT(DISTINCT b.id)                   AS buyurtmalar,
    SUM(e.miqdor * e.narx_birlik)          AS daromad
FROM buyurtmalar b
JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
WHERE b.holat IN ('tasdiqlangan','yetkazildi')
  AND b.yaratilgan >= NOW() - INTERVAL '6 months'
GROUP BY oy
ORDER BY oy;

-- 6) Har kategoriyaning eng qimmat mahsuloti (window)
WITH r AS (
    SELECT
        k.nomi AS kategoriya,
        m.nomi,
        m.narx,
        ROW_NUMBER() OVER (PARTITION BY k.id ORDER BY m.narx DESC) AS rn
    FROM mahsulotlar m
    JOIN kategoriyalar k ON k.id = m.kategoriya_id
)
SELECT kategoriya, nomi, narx
FROM r WHERE rn = 1;

-- 7) Bir martalik vs takror mijoz
WITH mc AS (
    SELECT mijoz_id, COUNT(*) AS soni
    FROM buyurtmalar
    WHERE holat IN ('tasdiqlangan','yetkazildi')
    GROUP BY mijoz_id
)
SELECT
    CASE WHEN soni = 1 THEN 'bir martalik' ELSE 'takror' END AS toifa,
    COUNT(*) AS mijozlar
FROM mc
GROUP BY toifa;

-- 8) Birga sotib olinadi (self JOIN ko'rinishi)
SELECT
    m1.nomi AS mahsulot_1,
    m2.nomi AS mahsulot_2,
    COUNT(*) AS qancha_marta
FROM buyurtma_elementlari e1
JOIN buyurtma_elementlari e2 ON e1.buyurtma_id = e2.buyurtma_id
    AND e1.mahsulot_id < e2.mahsulot_id
JOIN mahsulotlar m1 ON m1.id = e1.mahsulot_id
JOIN mahsulotlar m2 ON m2.id = e2.mahsulot_id
GROUP BY m1.nomi, m2.nomi
ORDER BY qancha_marta DESC
LIMIT 10;

-- 9) Oylik o'sish foizi (LAG)
WITH oylik AS (
    SELECT
        DATE_TRUNC('month', b.yaratilgan)::DATE AS oy,
        SUM(e.miqdor * e.narx_birlik) AS daromad
    FROM buyurtmalar b
    JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
    WHERE b.holat IN ('tasdiqlangan','yetkazildi')
    GROUP BY oy
)
SELECT
    oy,
    daromad,
    LAG(daromad, 1) OVER (ORDER BY oy) AS oldingi_oy,
    ROUND(
        (daromad - LAG(daromad, 1) OVER (ORDER BY oy)) * 100.0
        / NULLIF(LAG(daromad, 1) OVER (ORDER BY oy), 0),
        1
    ) AS oysish_foiz
FROM oylik
ORDER BY oy;

-- 10) Hech qachon sotilmagan mahsulotlar
SELECT m.nomi, k.nomi AS kategoriya, m.narx
FROM mahsulotlar m
JOIN kategoriyalar k ON k.id = m.kategoriya_id
LEFT JOIN buyurtma_elementlari e ON e.mahsulot_id = m.id
WHERE e.id IS NULL;

-- 11) EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT m.nomi, SUM(e.miqdor) AS jami
FROM buyurtma_elementlari e
JOIN mahsulotlar m ON m.id = e.mahsulot_id
GROUP BY m.id, m.nomi
ORDER BY jami DESC
LIMIT 5;

-- 12) Optimize qilingan versiya
EXPLAIN ANALYZE
WITH agreg AS (
    SELECT mahsulot_id, SUM(miqdor) AS jami
    FROM buyurtma_elementlari
    GROUP BY mahsulot_id
)
SELECT m.nomi, a.jami
FROM agreg a
JOIN mahsulotlar m ON m.id = a.mahsulot_id
ORDER BY a.jami DESC
LIMIT 5;

-- 13) BONUS: RFM segmentatsiya
WITH mijoz_rfm AS (
    SELECT
        mz.id,
        mz.ism,
        EXTRACT(DAY FROM NOW() - MAX(b.yaratilgan)) AS recency_kun,
        COUNT(b.id)                                  AS frequency,
        SUM(e.miqdor * e.narx_birlik)               AS monetary
    FROM ec_mijozlar mz
    JOIN buyurtmalar b ON b.mijoz_id = mz.id
    JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
    WHERE b.holat IN ('tasdiqlangan','yetkazildi')
    GROUP BY mz.id, mz.ism
)
SELECT
    ism,
    recency_kun::INTEGER AS recency,
    frequency,
    monetary,
    CASE
        WHEN recency_kun <= 30 AND frequency >= 2 AND monetary > 5000000 THEN 'VIP'
        WHEN recency_kun <= 60 THEN 'faol'
        WHEN recency_kun <= 120 THEN 'kutmoqda'
        ELSE 'yo''qotilgan'
    END AS segment
FROM mijoz_rfm
ORDER BY monetary DESC;
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


# Per-lesson exercise placeholders — filled in below
L1_EX: list = [
    mc("Quyidagi so'rov nima qaytaradi?\n`SELECT * FROM talabalar;`",
       ["Jadvalning barcha ustunlari va barcha qatorlari",
        "Faqat birinchi qator",
        "Faqat ustun nomlari",
        "Xato — `*` SQL'da ishlatilmaydi"],
       "A", hint="`*` — barcha ustun degani.",
       diff="Easy", pts=2),
    mc("SQL'da matn (string) literali qanday yoziladi?",
       ["\"Olim\" — qo'sh tirnoqda",
        "'Olim' — bitta tirnoqda",
        "`Olim` — backtick'da",
        "Olim — tirnoqsiz"],
       "B", hint="Qo'sh tirnoq — bu identifikator (ustun/jadval nomi) uchun.",
       explanation="SQL'da string — bitta tirnoq. Qo'sh tirnoq esa kerak bo'lganda identifikatorni o'rab oladi.",
       diff="Easy", pts=2),
    mc("`SELECT ism AS talaba FROM talabalar;` so'rovida `AS` nima qiladi?",
       ["Ustunga vaqtinchalik nom (alias) beradi",
        "Ustunni o'chiradi",
        "Ustunni filterlaydi",
        "Yangi ustun yaratadi"],
       "A", hint="AS so'zi natijaning ustun nomini o'zgartiradi (jadvalda emas).",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari TO'G'RI SQL sintaksisi?",
       ["SELECT * FROM talabalar;",
        "SELECT ism, ball FROM talabalar;",
        "SELECT ism FROM talabalar",
        "from talabalar select *;",
        "SELECT ism || ' ' || familiya FROM talabalar;"],
       "A,B,C,E", multi=True,
       hint="Nuqta-vergul majburiy emas (psql'da har bayonot oxirida tavsiya), lekin tartibni almashtirib bo'lmaydi.",
       explanation="To'rttasi sintaktik to'g'ri. `from talabalar select *;` — noto'g'ri tartib, SELECT FROM ketma-ketligi shart.",
       diff="Medium", pts=3),
    dd("To'liq ismni hisoblab chiqaruvchi so'rov bosqichlari",
       ["SELECT",
        "    ism || ' ' || familiya AS toliq_ism",
        "FROM",
        "    talabalar;"],
       diff="Medium", pts=3),
    ti("`SELECT 'O''zbekiston' AS davlat;` — natija nima va nima uchun ikkita tirnoq yozildi?",
       "Natija: O'zbekiston. SQL'da string bitta tirnoq ichida. "
       "Agar matn ichida o'zi tirnoq bo'lsa, uni \"ekran\" qilish uchun ikki marta yoziladi. "
       "Ya'ni 'O''zbekiston' — bu 'O' + ''' (bitta tirnoq) + 'zbekiston'. "
       "Bu Python'ning \\' kabi. Aks holda parser stringni shu yerda tugadi deb o'ylaydi.",
       hint="Bitta tirnoqni stringga qanday qo'shamiz?",
       diff="Hard", pts=4),
    mc("Production kodida nima uchun `SELECT *` ni kam ishlatamiz?",
       ["Ishlamaydi",
        "Kerakli ustunlar aniq ko'rinmaydi, sxema o'zgarsa kod sinadi va ko'pincha keraksiz ma'lumot uzatadi",
        "PostgreSQL `*` ni qabul qilmaydi",
        "Tezroq ishlaydi"],
       "B", explanation="Aniq ustunlar = aniq shartnoma. Sxema o'zgarsa, kod oldindan ko'rinadigan tarzda ishdan chiqadi (yashirin bug emas).",
       diff="Medium", pts=3),
]
L2_EX: list = [
    mc("`SELECT * FROM talabalar WHERE ball >= 80;` — bu so'rov qaytaradi:",
       ["Ballari 80 ga teng yoki katta bo'lgan barcha talabalar",
        "Faqat 80 balli talabalar",
        "Birinchi 80 ta qator",
        "80 ta ustun"],
       "A", hint="`>=` — katta yoki teng.",
       diff="Easy", pts=2),
    mc("Quyidagi so'rov — `WHERE familiya = NULL` — natija qanday bo'ladi?",
       ["familiya'si NULL bo'lgan qatorlar",
        "Hech narsa qaytmaydi (bo'sh natija)",
        "Barcha qatorlar",
        "Xato — sintaksis noto'g'ri"],
       "B", explanation="NULL hech narsaga teng emas, hatto NULL ham. To'g'ri: `IS NULL`.",
       diff="Medium", pts=3),
    mc("`ball BETWEEN 70 AND 90` qaysi so'rovga teng?",
       ["ball > 70 AND ball < 90",
        "ball >= 70 AND ball <= 90",
        "ball >= 70 OR ball <= 90",
        "ball IN (70, 90)"],
       "B", hint="BETWEEN — inkluziv, chetlari kiradi.",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari TO'G'RI ishlaydi va ma'noli natija beradi?",
       ["WHERE sinf = '11-A'",
        "WHERE yosh BETWEEN 14 AND 18",
        "WHERE ism LIKE 'A%'",
        "WHERE familiya == 'Karimov'",
        "WHERE id IN (1, 2, 3)",
        "WHERE familiya IS NULL"],
       "A,B,C,E,F", multi=True,
       hint="SQL'da tenglik bitta `=` belgisi.",
       explanation="`==` — Python sintaksisi. SQL'da faqat bitta `=`.",
       diff="Medium", pts=3),
    dd("'A' harfidan boshlanadigan ismli 80+ ballilarni topish bosqichlari",
       ["SELECT",
        "    ism, ball",
        "FROM",
        "    talabalar",
        "WHERE",
        "    ism LIKE 'A%'",
        "    AND ball >= 80;"],
       diff="Medium", pts=3),
    ti("Nima uchun `WHERE sinf = '11-A' OR sinf = '11-B' AND ball >= 80` xavfli? Tuzating.",
       "AND ning prioriteti OR dan yuqori. Demak so'rov: "
       "sinf = '11-A' OR (sinf = '11-B' AND ball >= 80) deb o'qiladi. "
       "Bu '11-A bo'lsa, ballidan qat'i nazar oladi' degani — bu odatda kerakli emas. "
       "Tuzatish: qavslar bilan aniqlash — (sinf = '11-A' OR sinf = '11-B') AND ball >= 80. "
       "Endi ikkala sinf uchun ham 80+ ball sharti qo'llaniladi.",
       hint="Qaysi operator avval bajariladi: AND yoki OR?",
       diff="Hard", pts=4),
    mc("`ILIKE` `LIKE` dan qanday farq qiladi?",
       ["Tezroq ishlaydi",
        "Faqat son ustida ishlaydi",
        "Katta-kichik harfga sezgir emas",
        "Faqat birinchi natijani qaytaradi"],
       "C", explanation="`LIKE 'o%'` — 'Olim' ni topmaydi (kapital O). `ILIKE 'o%'` — topadi.",
       diff="Medium", pts=3),
]
L3_EX: list = [
    mc("`ORDER BY ball DESC` nima qiladi?",
       ["Ball bo'yicha o'suvchi tartibda",
        "Ball bo'yicha pasayuvchi tartibda (kattalardan kichiklarga)",
        "Ballarni o'chiradi",
        "Ballarni filterlaydi"],
       "B", hint="DESC — descending (pasayuvchi).",
       diff="Easy", pts=2),
    mc("Default tartib yo'nalishi qanday?",
       ["ASC (o'suvchi)",
        "DESC (pasayuvchi)",
        "RANDOM",
        "Yo'nalish — majburiy, default yo'q"],
       "A", hint="ASC — yozish shart emas.",
       diff="Easy", pts=2),
    mc("`LIMIT 10 OFFSET 20` nima qaytaradi?",
       ["10-dan 20-gacha bo'lgan qatorlar",
        "20 ta qatorni o'tkazib, keyingi 10 tasini qaytaradi",
        "Eng katta 10 ta",
        "10 ta qator, ma'lumotsiz"],
       "B", hint="OFFSET — o'tkazib yuborish.",
       diff="Medium", pts=3),
    mc("Nima uchun `LIMIT` ni `ORDER BY` siz ishlatish xavfli?",
       ["LIMIT ishlamaydi",
        "Qaysi qatorlar qaytishi kafolatlanmaydi — tartib aniqlanmagan",
        "PostgreSQL xato beradi",
        "Sekin ishlaydi"],
       "B", explanation="LIMIT — N ta qatorni kessadi. Lekin qaysi N tasi ekanligi ORDER BY siz aniq emas.",
       diff="Medium", pts=3),
    mc("`SELECT DISTINCT sinf FROM talabalar;` so'rovi qaytaradi:",
       ["Barcha qatorlar",
        "Faqat takrorlanmas sinf qiymatlari",
        "Sinflar soni",
        "Birinchi sinf"],
       "B", diff="Easy", pts=2),
    dd("'11-A' sinfning top-3 a'lochi talabasini topish bosqichlari",
       ["SELECT",
        "    ism, ball",
        "FROM",
        "    talabalar",
        "WHERE",
        "    sinf = '11-A'",
        "ORDER BY",
        "    ball DESC",
        "LIMIT 3;"],
       diff="Medium", pts=3),
    ti("Frontend'da sahifa=3, har sahifada 10 ta yozuv. Qanday LIMIT/OFFSET kerak? Va nima uchun katta OFFSET sekin?",
       "LIMIT 10 OFFSET 20. Formula: OFFSET = per_page * (page - 1) = 10 * (3-1) = 20. "
       "Katta OFFSET sekin chunki DB har safar o'tkazib yuboriladigan barcha qatorlarni "
       "o'qib chiqishi va atlab tashlashi kerak. Masalan OFFSET 1,000,000 — million qator "
       "skanerlanadi va tashlab yuboriladi. Yechim: keyset pagination (oxirgi ko'rilgan "
       "id'dan keyingilar: WHERE id > $last_id LIMIT 10).",
       hint="OFFSET = per_page * (page - 1).",
       diff="Hard", pts=4),
    mc("SQL ijro tartibi to'g'ri ko'rsatilgan variant qaysi?",
       ["SELECT → FROM → WHERE → ORDER BY",
        "FROM → WHERE → SELECT → ORDER BY → LIMIT",
        "ORDER BY → SELECT → WHERE → FROM",
        "FROM → SELECT → WHERE → LIMIT → ORDER BY"],
       "B", explanation="Yozish tartibi va bajarish tartibi farq qiladi. Bajarish: FROM → WHERE → (GROUP BY) → SELECT → ORDER BY → LIMIT.",
       diff="Hard", pts=4),
]
R1_EX: list = [
    mc("'A' bilan boshlangan ismli barcha talabalar, ball bo'yicha pasayuvchi tartibda. Qaysi so'rov?",
       ["SELECT * FROM talabalar WHERE ism = 'A%' ORDER BY ball DESC;",
        "SELECT * FROM talabalar WHERE ism LIKE 'A%' ORDER BY ball DESC;",
        "SELECT * FROM talabalar ORDER BY ball DESC WHERE ism LIKE 'A%';",
        "SELECT * FROM talabalar WHERE ism STARTS 'A' ORDER BY ball DESC;"],
       "B", hint="Pattern qidirish — LIKE. WHERE doim ORDER BY dan oldin.",
       diff="Medium", pts=3),
    mc("Qaysi so'rovlar 11-A va 11-B sinflarini birga qaytaradi?",
       ["WHERE sinf = '11-A' OR sinf = '11-B'",
        "WHERE sinf IN ('11-A', '11-B')",
        "WHERE sinf LIKE '11-%'",
        "WHERE sinf = '11-A' AND sinf = '11-B'"],
       "A,B,C", multi=True,
       hint="AND bilan ikkala teng bo'lishi kerak — bu mumkin emas.",
       diff="Medium", pts=3),
    mc("Sahifa 3, har sahifada 5 ta yozuv. To'g'ri LIMIT/OFFSET:",
       ["LIMIT 5 OFFSET 3",
        "LIMIT 5 OFFSET 10",
        "LIMIT 15 OFFSET 5",
        "LIMIT 5 OFFSET 15"],
       "B", explanation="OFFSET = per_page × (page - 1) = 5 × 2 = 10.",
       diff="Medium", pts=3),
    dd("Eng yosh talaba ismini topish bosqichlari",
       ["SELECT",
        "    ism, yosh",
        "FROM",
        "    talabalar",
        "ORDER BY",
        "    yosh ASC",
        "LIMIT 1;"],
       diff="Medium", pts=3),
    ti("Maktabda nechta TURLI sinf borligini qanday so'rov bilan aniqlaysiz? Yozing.",
       "SELECT COUNT(DISTINCT sinf) FROM talabalar;",
       hint="DISTINCT + COUNT.",
       diff="Hard", pts=4),
    mc("Nima uchun `WHERE bonusli > 80` (`bonusli` — SELECT'dagi alias) ishlamaydi?",
       ["WHERE faqat NOT NULL ustun bilan ishlaydi",
        "Ijro tartibi: WHERE — SELECT'dan oldin, demak alias hali yo'q",
        "SQL alias'larni unutadi",
        "Bu sintaktik xato, lekin ishlaydi"],
       "B", explanation="WHERE bajariladi → keyin SELECT. WHERE'da alias o'rniga to'liq ifoda yozish kerak.",
       diff="Hard", pts=4),
    mc("Sahifaning eng yuqori 10 yozuvni, lekin tartib aniq bo'lishi uchun nima qo'shasiz?",
       ["FROM",
        "ORDER BY",
        "DISTINCT",
        "WHERE"],
       "B", explanation="LIMIT siz ORDER BY tasodifiy qatorlar beradi.",
       diff="Easy", pts=2),
]
L4_EX: list = [
    mc("`SELECT COUNT(*) FROM talabalar;` 6 qaytardi. Bu nimani anglatadi?",
       ["Eng yuqori ball — 6",
        "Jadvalda 6 ta qator bor",
        "6 ta ustun bor",
        "6-talabani ko'rsatadi"],
       "A", hint="COUNT — sanash funksiyasi.", diff="Easy", pts=2),
    mc("`COUNT(*)` va `COUNT(familiya)` qachon HAR XIL natija beradi?",
       ["Hech qachon",
        "Familiya ustunida NULL qiymatlar bor bo'lsa",
        "Familiya ustuni mavjud bo'lmasa",
        "WHERE ishlatilganda"],
       "B", explanation="`COUNT(*)` barcha qatorni sanaydi, `COUNT(ustun)` esa NULL'larni o'tkazib yuboradi.",
       diff="Medium", pts=3),
    mc("Quyidagi so'rov nima xato beradi?\n`SELECT ism FROM talabalar WHERE AVG(ball) > 80;`",
       ["Sintaktik xato — vergul yo'q",
        "Agregat funksiya WHERE'da ishlatilmaydi",
        "AVG — noma'lum funksiya",
        "Hech narsa, ishlaydi"],
       "B", explanation="AVG butun guruh ustida ishlaydi, WHERE esa har qatorni alohida tekshiradi. Bu maqsad mos kelmaydi.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari TO'G'RI agregat ishlatish?",
       ["SELECT MAX(ball) FROM talabalar;",
        "SELECT COUNT(DISTINCT sinf) FROM talabalar;",
        "SELECT SUM(ism) FROM talabalar;",
        "SELECT ROUND(AVG(ball), 1) FROM talabalar;",
        "SELECT ism, AVG(ball) FROM talabalar;"],
       "A,B,D", multi=True,
       hint="SUM matn ustida ishlamaydi. Agregat va oddiy ustun aralashtirilsa GROUP BY shart (keyingi dars).",
       diff="Medium", pts=3),
    dd("11-sinfda nechta talaba va ularning o'rtacha bali — hisoblang",
       ["SELECT",
        "    COUNT(*) AS soni,",
        "    ROUND(AVG(ball), 1) AS ortacha",
        "FROM",
        "    talabalar",
        "WHERE",
        "    sinf LIKE '11-%';"],
       diff="Medium", pts=3),
    ti("`SUM(NULL)` natijasi va `SUM(ustun)` ichida NULL qiymatlar bo'lsa nima bo'ladi?",
       "SUM(NULL) — NULL. Lekin SUM(ustun) ichidagi NULL qiymatlar — e'tibordan tashqari. "
       "Ya'ni SUM faqat NOT NULL qiymatlarni qo'shadi. Agar hamma qiymatlar NULL bo'lsa — natija NULL "
       "(0 emas!). Buni hisobga olish kerak: agar ish 0 kerak bo'lsa COALESCE(SUM(x), 0) yozing.",
       hint="NULL qachon e'tiborga olinadi?",
       diff="Hard", pts=4),
    mc("`ROUND(AVG(ball), 2)` nima qiladi?",
       ["O'rtacha balni 2 ta o'nlikgacha yumaloqlaydi",
        "Faqat 2 qatorga qo'llaydi",
        "AVG'ni 2 marta hisoblaydi",
        "Yumaloqlamaydi"],
       "A", diff="Easy", pts=2),
]
L5_EX: list = [
    mc("`GROUP BY sinf` qatorlar ustida nima qiladi?",
       ["Sinf bo'yicha tartiblaydi",
        "Qatorlarni sinf qiymati bo'yicha guruhlarga ajratadi",
        "Sinf ustunini olib tashlaydi",
        "Sinfni almashtiradi"],
       "B", hint="GROUP BY = guruhlash.", diff="Easy", pts=2),
    mc("WHERE va HAVING orasidagi asosiy farq nima?",
       ["Faqat sintaktik farq",
        "WHERE qatorlarni, HAVING guruhlarni filterlaydi",
        "HAVING tezroq",
        "WHERE faqat birinchi ishlatiladi"],
       "B", explanation="WHERE — GROUP BY dan oldin. HAVING — GROUP BY dan keyin agregat shartlari uchun.",
       diff="Medium", pts=3),
    mc("Quyidagi so'rov nima xato beradi?\n`SELECT sinf, ism FROM talabalar GROUP BY sinf;`",
       ["Sintaktik xato",
        "`ism` GROUP BY da bo'lishi yoki agregat ichida bo'lishi kerak",
        "GROUP BY ikkita ustun bilan ishlamaydi",
        "Hech narsa — ishlaydi"],
       "B", explanation="GROUP BY qaytarganda har guruh uchun 1 ta ism kerak. Qaysi birini? — kompyuter bilmaydi.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari to'g'ri HAVING ishlatishi?",
       ["GROUP BY sinf HAVING COUNT(*) > 2",
        "GROUP BY sinf HAVING AVG(ball) > 80",
        "WHERE COUNT(*) > 2",
        "HAVING sinf = '11-A' (GROUP BY siz)",
        "GROUP BY sinf HAVING MAX(ball) BETWEEN 80 AND 100"],
       "A,B,E", multi=True,
       hint="WHERE'da agregat ishlatilmaydi. HAVING odatda GROUP BY bilan birga.",
       diff="Medium", pts=3),
    dd("Sinf bo'yicha o'rtacha bali 80+ bo'lgan sinflar — ball pasayuvchi",
       ["SELECT",
        "    sinf,",
        "    ROUND(AVG(ball), 1) AS ortacha",
        "FROM",
        "    talabalar",
        "GROUP BY",
        "    sinf",
        "HAVING",
        "    AVG(ball) > 80",
        "ORDER BY",
        "    ortacha DESC;"],
       diff="Medium", pts=3),
    ti("HAVING'siz, 11-A sinfining o'rtacha balini topish so'rovini yozing.",
       "SELECT AVG(ball) FROM talabalar WHERE sinf = '11-A';",
       hint="WHERE bilan filterlaydi, GROUP BY shart emas — chunki bitta guruh.",
       diff="Hard", pts=4),
    mc("Standart SQL ijro tartibi qaysi?",
       ["FROM → WHERE → SELECT → GROUP BY → HAVING",
        "FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY",
        "GROUP BY → FROM → WHERE → SELECT",
        "SELECT → FROM → WHERE → GROUP BY"],
       "B", explanation="Bu tartib SQL'da fundamental. Yodda saqlang.",
       diff="Hard", pts=4),
]
L6_EX: list = [
    mc("`INNER JOIN` qachon qatorni qaytaradi?",
       ["Faqat ON sharti TRUE bo'lgan, har ikki jadvalda mos bor qator",
        "Chap jadvaldagi hamma qator",
        "O'ng jadvaldagi hamma qator",
        "Doim — barcha qatorlar"],
       "A", hint="INNER = kesishish.", diff="Easy", pts=2),
    mc("`LEFT JOIN` ning xususiyati nima?",
       ["Tezroq ishlaydi",
        "Chap jadvaldagi BARCHA qator qaytadi, mos kelmaganlarda o'ng ustunlar NULL",
        "O'ng jadvalni e'tibordan tashqari qoldiradi",
        "Faqat NULL qatorlarni qaytaradi"],
       "B", explanation="LEFT = chap tomonni saqlash. O'ng — agar mos bo'lsa qo'shadi.",
       diff="Easy", pts=2),
    mc("Quyidagi so'rov nima xato qiladi?\n`SELECT * FROM A LEFT JOIN B ON A.id = B.a_id WHERE B.x = 5;`",
       ["Hech nima",
        "LEFT JOIN INNER JOIN'ga aylanadi (WHERE B.x NULL bo'lsa false bo'lganligi uchun)",
        "Sintaksis xato",
        "B.x ustuni topilmaydi"],
       "B", explanation="WHERE B.x = 5 — B.x NULL bo'lgan qatorlarni filterlab tashlaydi. To'g'risi: ON sharti ichiga qo'shing.",
       diff="Hard", pts=4),
    mc("Quyidagi JOIN turlaridan qaysilari MAVJUD SQL'da?",
       ["INNER JOIN",
        "LEFT JOIN",
        "FRIEND JOIN",
        "RIGHT JOIN",
        "FULL OUTER JOIN",
        "CROSS JOIN"],
       "A,B,D,E,F", multi=True,
       hint="\"FRIEND JOIN\" — bunaqasi yo'q.", diff="Easy", pts=2),
    dd("Har talabaning o'rtacha bahosini, hatto bahosi yo'qlarini ham — qanday yoziladi?",
       ["SELECT",
        "    t.ism,",
        "    ROUND(AVG(b.baho), 1) AS ortacha",
        "FROM",
        "    talabalar t",
        "LEFT JOIN",
        "    baholar b ON b.talaba_id = t.id",
        "GROUP BY",
        "    t.id, t.ism",
        "ORDER BY",
        "    ortacha DESC NULLS LAST;"],
       diff="Hard", pts=4),
    ti("Nima uchun `FROM A, B WHERE A.id = B.a_id` (implicit join) zamonaviy kodda tavsiya etilmaydi?",
       "Sabablari: 1) ON sharti unutilsa CARTEZIAN ko'paytma — milliard qator natija; "
       "2) LEFT/RIGHT/FULL JOIN bilan ishlamaydi; "
       "3) Bog'lanish sharti va filter (WHERE) bir joyda — o'qish qiyin; "
       "4) Standart ANSI JOIN sintaksisi (1992) — barcha DB'da yagona. "
       "Doim aniq JOIN ... ON ... yozish kerak.",
       hint="Kartezian xavfi va o'qish qulayligi.", diff="Hard", pts=4),
    mc("Quyidagi 4 ta jadvalni bog'lash uchun nechta JOIN kerak?",
       ["3 ta",
        "4 ta",
        "2 ta",
        "Aniq emas — bog'lanishlarga bog'liq"],
       "A", explanation="N ta jadvalni zanjir bilan ulash uchun N-1 ta JOIN kerak.",
       diff="Medium", pts=3),
]
R2_EX: list = [
    mc("Sinf bo'yicha o'rtacha balli 80+ sinflarni topishda — qaysi to'g'ri?",
       ["WHERE AVG(ball) > 80",
        "GROUP BY sinf HAVING AVG(ball) > 80",
        "WHERE sinf > 80",
        "HAVING sinf > 80"],
       "B", diff="Easy", pts=2),
    mc("LEFT JOIN bilan birga GROUP BY ishlatilgan so'rovda bahosizlarni qanday ko'rasiz?",
       ["WHERE b.id IS NULL",
        "WHERE COUNT(*) = 0",
        "HAVING COUNT(b.id) = 0",
        "Mumkin emas — LEFT JOIN bahosizlarni qaytarmaydi"],
       "C", explanation="WHERE b.id IS NULL — bu yondashuv ham ishlaydi, lekin GROUP BY bilan birga HAVING COUNT(b.id) = 0 standartroq.",
       diff="Hard", pts=4),
    mc("\"Universal a'lochi\" (har fandan 85+) — qaysi shart to'g'ri?",
       ["AVG(baho) >= 85",
        "MIN(baho) >= 85",
        "MAX(baho) >= 85",
        "SUM(baho) >= 85"],
       "B", explanation="Agar eng past baho ham 85+ bo'lsa — barchasi 85+ degani.",
       diff="Hard", pts=4),
    dd("Fan bo'yicha eng yuqori baho olgan talaba — so'rov bosqichlari",
       ["SELECT",
        "    f.nomi AS fan,",
        "    t.ism AS eng_kuchli,",
        "    b.baho",
        "FROM",
        "    baholar b",
        "JOIN fanlar f ON f.id = b.fan_id",
        "JOIN talabalar t ON t.id = b.talaba_id",
        "WHERE",
        "    b.baho = (SELECT MAX(b2.baho) FROM baholar b2 WHERE b2.fan_id = b.fan_id)"],
       diff="Hard", pts=4),
    mc("3 ta jadval (talabalar, baholar, fanlar) ni bog'lash uchun nechta JOIN kerak?",
       ["1", "2", "3", "4"],
       "B", explanation="3 jadval — 2 JOIN (zanjir: A-B-C).",
       diff="Easy", pts=2),
    ti("Bahosi bo'lmagan talabalarni topish so'rovini yozing.",
       "SELECT t.ism FROM talabalar t LEFT JOIN baholar b ON b.talaba_id = t.id WHERE b.id IS NULL;",
       hint="LEFT JOIN + IS NULL.",
       diff="Medium", pts=3),
    mc("`HAVING COUNT(*) >= 2` shartini qaysi ma'noda tushuniladi?",
       ["Jadvalda 2+ qator bo'lsa",
        "Har guruhda 2+ qator bo'lsa",
        "WHERE bilan birga ishlatilmaydi",
        "Bu shart noto'g'ri"],
       "B", diff="Medium", pts=3),
]
L7_EX: list = [
    mc("`UPDATE talabalar SET ball = 0;` nima qiladi?",
       ["Bitta talaba balini 0 ga aylantiradi",
        "Hech narsa — WHERE shart",
        "BARCHA talabalar balini 0 ga aylantiradi (xavfli!)",
        "Sintaktik xato"],
       "C", explanation="WHERE'siz UPDATE — barcha qatorlarga qo'llaniladi. Eng xavfli xato.",
       diff="Medium", pts=3),
    mc("Tranzaksiyani bekor qilish uchun qaysi buyruq?",
       ["UNDO",
        "ROLLBACK",
        "CANCEL",
        "REVERT"],
       "B", diff="Easy", pts=2),
    mc("`INSERT INTO ... RETURNING id` qachon foydali?",
       ["Hech qachon",
        "Yangi yaratilgan qatorning ID'sini bilish kerak bo'lganda",
        "Faqat UPDATE bilan ishlaydi",
        "Tezroq INSERT qilish uchun"],
       "B", explanation="Backend application — INSERT keyin bevosita ID kerak. RETURNING — buni bitta so'rovda beradi.",
       diff="Medium", pts=3),
    mc("ACID ning A harfi nimani anglatadi?",
       ["Authentication",
        "Atomicity — hammasi yoki hech narsa",
        "Async",
        "Auto-commit"],
       "B", diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari `ON CONFLICT` (UPSERT) ning ma'noli ishlatilishi?",
       ["Qator bor bo'lsa — yangilash, yo'q bo'lsa — qo'shish",
        "Konflikt bo'lsa hech narsa qilmaslik (`DO NOTHING`)",
        "Konfliktni xato qilib ko'tarish",
        "Faqat tezroq INSERT"],
       "A,B", multi=True,
       hint="ON CONFLICT DO UPDATE — upsert. ON CONFLICT DO NOTHING — sukut.",
       diff="Medium", pts=3),
    dd("Tranzaksiya bilan 2 ta yangilashni xavfsiz qilish",
       ["BEGIN;",
        "    UPDATE hisoblar SET balans = balans - 100 WHERE id = 1;",
        "    UPDATE hisoblar SET balans = balans + 100 WHERE id = 2;",
        "COMMIT;"],
       diff="Medium", pts=3),
    ti("UPDATE/DELETE qilishdan oldin qanday xavfsizlik tartibi tavsiya etiladi?",
       "1) Avval shu WHERE bilan SELECT qilib natijani ko'rish. "
       "2) BEGIN tranzaksiya boshlash. "
       "3) UPDATE/DELETE bajarish va RETURNING bilan natijani tekshirish. "
       "4) Agar yaxshi — COMMIT, agar xato — ROLLBACK. "
       "5) Production'da har doim WHERE'siz UPDATE/DELETE ni alohida tekshirish. "
       "Bu — eng katta bug'larning oldini oluvchi tartib.",
       hint="SELECT → BEGIN → UPDATE → COMMIT/ROLLBACK.",
       diff="Hard", pts=4),
]
L8_EX: list = [
    mc("`SERIAL PRIMARY KEY` nima qiladi?",
       ["Faqat unik ID",
        "Auto-inkrement, unik, NOT NULL — har qatorga avtomatik raqam",
        "Faqat NOT NULL",
        "PostgreSQL'da bunday turi yo'q"],
       "B", explanation="SERIAL = INTEGER + sequence + DEFAULT nextval. Plyus PRIMARY KEY — UNIQUE + NOT NULL.",
       diff="Easy", pts=2),
    mc("Pul saqlash uchun qaysi turi to'g'ri?",
       ["REAL",
        "DOUBLE PRECISION",
        "NUMERIC(p, s)",
        "VARCHAR"],
       "C", explanation="REAL/DOUBLE — yumaloqlash xatosi. Pul har doim NUMERIC(p,s).",
       diff="Medium", pts=3),
    mc("`FOREIGN KEY (mijoz_id) REFERENCES mijozlar(id)` nimadan saqlaydi?",
       ["Mijoz ID'sini takrorlashdan",
        "Mavjud bo'lmagan mijoz ID'siga buyurtma yaratishdan",
        "INSERT sekinlashishidan",
        "Hech narsadan — bu shunchaki hujjat"],
       "B", explanation="FK bog'lanish kafolati. Yo'q narsalarga havola qila olmaysiz.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari haqiqiy SQL cheklovi?",
       ["PRIMARY KEY",
        "FOREIGN KEY",
        "NOT NULL",
        "UNIQUE",
        "CHECK",
        "MUST_HAVE"],
       "A,B,C,D,E", multi=True,
       hint="MUST_HAVE — yo'q.",
       diff="Easy", pts=2),
    dd("Email maydoni majburiy va takrorsiz bo'lgan mijozlar jadvalini yarating",
       ["CREATE TABLE mijozlar (",
        "    id    SERIAL PRIMARY KEY,",
        "    ism   VARCHAR(50) NOT NULL,",
        "    email VARCHAR(100) UNIQUE NOT NULL",
        ");"],
       diff="Medium", pts=3),
    ti("`ON DELETE CASCADE` va `ON DELETE RESTRICT` orasidagi farq nima va qachon qaysini tanlaysiz?",
       "CASCADE: parent o'chirilsa, bog'liq child qatorlar avtomatik o'chiriladi. "
       "RESTRICT: parent o'chirishga ruxsat bermaydi, agar child qator hali bog'lanib turgan bo'lsa. "
       "CASCADE — log, comment, session kabi bog'liq vaqtinchalik ma'lumotlar uchun. "
       "RESTRICT — buyurtma, to'lov kabi muhim hisobotlar uchun (mijozni o'chirsa, buyurtma yo'qolmasin). "
       "SET NULL — child saqlanadi, FK ustuni NULL ga aylanadi.",
       hint="Vaqtinchalik vs muhim ma'lumot.",
       diff="Hard", pts=4),
    mc("`CHECK (yosh >= 0 AND yosh <= 150)` qaysi vaziyatda xato beradi?",
       ["yosh = -5 yoki yosh = 200 kiritilganda",
        "yosh NULL bo'lganda",
        "yosh ustuni o'chirilganda",
        "Hech qachon"],
       "A", explanation="CHECK qator-darajasidagi qoida. NULL — CHECK uchun TRUE deb hisoblanadi (NULL semantikasi).",
       diff="Medium", pts=3),
]
L9_EX: list = [
    mc("Indeks nima uchun kerak?",
       ["Ma'lumotni saqlash uchun",
        "WHERE/JOIN/ORDER BY ni tezlashtirish uchun",
        "Foydalanuvchi nomini saqlash uchun",
        "Hech narsa uchun"],
       "B", diff="Easy", pts=2),
    mc("`WHERE LOWER(email) = 'x'` so'rovida email ustiga oddiy indeks bormi va ishlaydi?",
       ["Ha, ishlaydi",
        "Yo'q, ishlamaydi — functional indeks kerak: `(LOWER(email))`",
        "Indeks shart emas",
        "Bu xato so'rov"],
       "B", explanation="Indeks ustunga emas, ifodaga bog'liq. LOWER(email) — boshqa ifoda.",
       diff="Hard", pts=4),
    mc("Multi-column indeks `(A, B)` qachon ishlaydi?",
       ["WHERE A = ?",
        "WHERE B = ?",
        "WHERE A = ? AND B = ?",
        "WHERE A = ? ORDER BY B"],
       "A,C,D", multi=True,
       hint="Birinchi ustun (A) bo'lmasa, indeks samarasiz.",
       diff="Hard", pts=4),
    mc("`EXPLAIN` va `EXPLAIN ANALYZE` orasidagi farq nima?",
       ["EXPLAIN faqat plan ko'rsatadi, ANALYZE — real ijro qiladi va aniq vaqtni ko'rsatadi",
        "EXPLAIN tezroq",
        "ANALYZE faqat raqamlarni hisoblaydi",
        "Hech qanday farq"],
       "A", explanation="ANALYZE so'rovni HAQIQATAN bajaradi. SELECT bilan xavfsiz, lekin UPDATE/DELETE/INSERT bilan — ehtiyot bo'ling.",
       diff="Medium", pts=3),
    dd("Email ustiga indeks qo'shish so'rovi",
       ["CREATE INDEX",
        "    idx_mijozlar_email",
        "ON",
        "    mijozlar(email);"],
       diff="Easy", pts=2),
    ti("Foreign key ustuni uchun nima uchun indeks qo'shish kerak (PostgreSQL avtomatik qilmaydi)?",
       "PostgreSQL FK CONSTRAINT yaratganda indeks avtomatik yaratmaydi. "
       "Ammo har JOIN da FK ustuni bilan qidirish bo'lib qoladi. Indeks bo'lmasa — "
       "Seq Scan, katta jadvallarda sekin. Plyus parent qatorni o'chirsangiz (CASCADE/RESTRICT) "
       "DB FK qiymatini topish kerak — indeks juda foydali. Demak: har FK ustuni uchun "
       "alohida CREATE INDEX qo'shing.",
       hint="JOIN va parent o'chirish.",
       diff="Hard", pts=4),
    mc("Indeks barcha so'rovlarni tezlashtiradimi?",
       ["Ha, har doim",
        "Yo'q — SELECT'larni tezlashtiradi, INSERT/UPDATE/DELETE'larni sekinlashtiradi",
        "Faqat UPDATE'larni tezlashtiradi",
        "Hech qachon"],
       "B", explanation="Indeks — narxli. SELECT tez, lekin yozish — sekin (har indeksga qo'shilishi kerak). Mos joyda ishlatish kerak.",
       diff="Medium", pts=3),
]
R3_EX: list = [
    mc("Postlar va teglar — M:N munosabat. Bu uchun nimadan foydalanasiz?",
       ["Faqat 2 ta jadval",
        "Bog'lovchi (junction) jadval — post_teglar(post_id, teg_id)",
        "FOREIGN KEY har ikkala tomondan",
        "Hech narsa — ikki jadval kifoya"],
       "B", explanation="M:N — har doim 3-jadval kerak: bog'lovchi.",
       diff="Medium", pts=3),
    mc("Foydalanuvchi o'chirilganda postlari ham o'chsinmi?",
       ["Ha doim — CASCADE qo'ying",
        "Aniq emas — biznes qoidasiga bog'liq. Ko'p hollarda postlar muhim, RESTRICT yaxshi",
        "Mumkin emas SQL'da",
        "ON DELETE SET NULL — eng yaxshi"],
       "B", explanation="Audit muhim bo'lsa RESTRICT (foydalanuvchini o'chirib bo'lmaydi); arxiv kerak bo'lsa SET NULL; vaqtinchalik bo'lsa CASCADE.",
       diff="Hard", pts=4),
    mc("`post_teglar(post_id, teg_id)` jadvalida PRIMARY KEY (post_id, teg_id) — bu nima beradi?",
       ["Faqat tezroq qidiruv",
        "Har juftlikni takrorsiz qiladi (bitta teg postga 2 marta qo'shilmaydi)",
        "Auto-inkrement",
        "FK avtomatik"],
       "B", diff="Medium", pts=3),
    dd("Eng faol foydalanuvchi so'rovi bosqichlari",
       ["SELECT",
        "    f.ism,",
        "    COUNT(DISTINCT p.id) + COUNT(DISTINCT i.id) AS jami",
        "FROM",
        "    foydalanuvchilar f",
        "LEFT JOIN postlar p ON p.muallif_id = f.id",
        "LEFT JOIN izohlar i ON i.muallif_id = f.id",
        "GROUP BY f.id, f.ism",
        "ORDER BY jami DESC;"],
       diff="Hard", pts=4),
    ti("Nima uchun har 2 ta jadvalga JOIN qilganda COUNT(DISTINCT) ishlatish kerak?",
       "Ko'p tomonli JOIN da Cartesian effekt paydo bo'ladi. Masalan foydalanuvchining "
       "3 ta posti va 2 ta izohi bo'lsa — JOIN natijasida 3×2=6 qator chiqadi. "
       "COUNT(p.id) — 6 qaytaradi, lekin postlar — 3 ta. "
       "COUNT(DISTINCT p.id) — to'g'ri (3). Yoki alternativ: subquery'lar bilan alohida "
       "hisoblash. DISTINCT — eng oddiy yechim.",
       hint="JOIN ning Cartesian effekti.", diff="Hard", pts=4),
    mc("Foreign key ustuniga indeks kerakmi?",
       ["Yo'q, PostgreSQL avtomatik qiladi",
        "Ha — JOIN va parent o'chirish uchun manfaatli",
        "Faqat agar UNIQUE bo'lsa",
        "Bunday savol kerak emas"],
       "B", explanation="PostgreSQL FK constraint yaratganda indeks YARATMAYDI. Qo'l bilan qo'shish kerak.",
       diff="Medium", pts=3),
    mc("0 izohli postlarni topish uchun qaysi yondashuv to'g'ri?",
       ["INNER JOIN izohlar WHERE COUNT = 0",
        "LEFT JOIN izohlar ON ... WHERE i.id IS NULL",
        "WHERE NOT EXISTS (SELECT 1 FROM izohlar)",
        "SELECT DISTINCT"],
       "B,C", multi=True,
       hint="LEFT JOIN + IS NULL — klassik. NOT EXISTS — to'g'ri lekin alohida tushuncha.",
       diff="Medium", pts=3),
]
L10_EX: list = [
    mc("`WHERE ball > (SELECT AVG(ball) FROM talabalar)` nimani qaytaradi?",
       ["Maktab o'rtachasidan yuqori balli talabalar",
        "Eng yuqori balli",
        "Faqat o'rtacha balli",
        "Xato — subquery WHERE'da yo'q"],
       "A", diff="Easy", pts=2),
    mc("CTE (WITH ... AS) ning afzalligi nima?",
       ["Faqat sintaktik chiroy",
        "Kodni o'qish oson, qayta ishlatish, recursive yozish mumkin",
        "Hech qanday afzalligi yo'q",
        "Faqat optimizatsiya"],
       "B", diff="Medium", pts=3),
    mc("`ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC)` nima qiladi?",
       ["Har qatorga 1 dan boshlab raqam beradi (umumiy)",
        "Har sinf ichida ballarni saralab raqamlaydi (har sinfda 1 dan)",
        "Faqat tartiblaydi",
        "GROUP BY ga teng"],
       "B", explanation="PARTITION BY — guruh chegarasi. Har guruh ichida ORDER BY bilan tartib.",
       diff="Hard", pts=4),
    mc("`RANK()` va `DENSE_RANK()` orasidagi farq nima?",
       ["Hech qanday",
        "RANK teng qiymatlardan keyin 'sakraydi' (1,2,2,4), DENSE_RANK esa ketma-ket (1,2,2,3)",
        "DENSE_RANK tezroq",
        "RANK faqat sonlar uchun"],
       "B", diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari MAVJUD window funksiya?",
       ["ROW_NUMBER()",
        "LAG()",
        "FIRST_VALUE()",
        "PARTITION()",
        "SUM() ... OVER (...)"],
       "A,B,C,E", multi=True,
       hint="PARTITION — kalit so'z, funksiya emas.",
       diff="Medium", pts=3),
    dd("Har sinfdan TOP-1 talabani topish bosqichlari",
       ["WITH rangs AS (",
        "    SELECT ism, sinf, ball,",
        "           ROW_NUMBER() OVER (PARTITION BY sinf ORDER BY ball DESC) AS rn",
        "    FROM talabalar",
        ")",
        "SELECT ism, sinf, ball",
        "FROM rangs",
        "WHERE rn = 1;"],
       diff="Hard", pts=4),
    ti("`SUM(ball) OVER (ORDER BY id)` va oddiy `SUM(ball)` orasidagi farq nima?",
       "Oddiy SUM(ball) — butun jadval bo'yicha bitta yig'indi qaytaradi (bitta qator). "
       "SUM(ball) OVER (ORDER BY id) — har qator uchun KUMULYATIV yig'indi qaytaradi: "
       "1-qator uchun 1-ball, 2-qator uchun 1+2, 3-qator uchun 1+2+3, va h.k. "
       "Bu window funksiya — qatorlar sonini saqlaydi, lekin har qator uchun hisob qiladi. "
       "Foydali: progress, salary increase trend, cumulative revenue.",
       hint="OVER bilan funksiya — qatorni saqlaydi.",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("Yakuniy loyihada nechta jadval kerak?",
       ["3",
        "5: kategoriyalar, mahsulotlar, mijozlar, buyurtmalar, buyurtma_elementlari",
        "10+",
        "Faqat bittasi"],
       "B", diff="Easy", pts=2),
    mc("Buyurtma va mahsulotlar M:N munosabati — qaysi sxema to'g'ri?",
       ["buyurtma.mahsulot_id (bitta buyurtma — bitta mahsulot)",
        "buyurtma_elementlari(buyurtma_id, mahsulot_id, miqdor)",
        "mahsulotlar.buyurtma_id",
        "Faqat buyurtmalar jadvali kifoya"],
       "B", explanation="Bitta buyurtmada ko'p mahsulot bo'lishi mumkin. Bog'lovchi jadval — buyurtma_elementlari.",
       diff="Medium", pts=3),
    mc("Pul ustun uchun qaysi turi to'g'ri?",
       ["REAL", "FLOAT", "NUMERIC(10,2)", "INTEGER"],
       "C", explanation="Pulda yumaloqlash xatosi qabul qilinmaydi.",
       diff="Easy", pts=2),
    mc("Quyidagi xususiyatlardan qaysilari yakuniy loyihada SHART?",
       ["Hamma FOREIGN KEY ustunlariga indeks",
        "Pul — NUMERIC",
        "Tranzaksiya ichida test ma'lumot",
        "Hamma jadvalda PRIMARY KEY",
        "Hammasi REAL turi bilan",
        "Vaqt — TIMESTAMPTZ"],
       "A,B,C,D,F", multi=True,
       hint="REAL — pul uchun yaroqsiz.", diff="Medium", pts=3),
    dd("Eng faol mijozni topish bosqichlari",
       ["SELECT",
        "    mz.ism,",
        "    COUNT(DISTINCT b.id) AS buyurtmalar,",
        "    SUM(e.miqdor * e.narx_birlik) AS jami_xarid",
        "FROM",
        "    ec_mijozlar mz",
        "JOIN buyurtmalar b ON b.mijoz_id = mz.id",
        "JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id",
        "WHERE",
        "    b.holat IN ('tasdiqlangan','yetkazildi')",
        "GROUP BY mz.id, mz.ism",
        "ORDER BY jami_xarid DESC",
        "LIMIT 5;"],
       diff="Hard", pts=4),
    ti("Oylik o'sish foizini hisoblash uchun qaysi window funksiyani ishlatasiz va nima uchun?",
       "LAG(daromad, 1) OVER (ORDER BY oy). Sabab: har oy uchun OLDINGI oyning "
       "daromad qiymati kerak. LAG — oldingi qatorni qaytaradi. "
       "Foiz formulasi: (joriy - oldingi) * 100 / oldingi. "
       "Diqqat: NULLIF(oldingi, 0) ishlatish kerak — birinchi oyda oldingi NULL bo'ladi "
       "va nolga bo'lish xato. ORDER BY oy — vaqtga ko'ra ketma-ketlik.",
       hint="Oldingi qator qiymati kerak.", diff="Hard", pts=4),
    mc("Yakuniy loyihada SQL ko'rsatdiki, siz endi nimaga tayyorsiz?",
       ["Hech narsaga",
        "Flask/Django/FastAPI ORM bilan ishlay olasiz, har SQL'ni o'qiy olasiz, performance muammolarni topa olasiz",
        "Faqat oddiy CRUD'ga",
        "ORM ham bilmaysiz"],
       "B", explanation="To'g'ri — ORM faqat SQL ustidan ko'rinish. Endi nima ish qilayotgani aniq.",
       diff="Easy", pts=2),
]


# ─────────────────────────────────────────────────────────────────────────────
# Lesson tasks (project briefs) — filled in below
# ─────────────────────────────────────────────────────────────────────────────
LESSON_TASKS: dict = {
    0: {
        "title": "Birinchi jadval va SELECT amaliyot",
        "description": (
            "PostgreSQL'da ulanib, talabalar jadvalini yaratish va birinchi "
            "SELECT so'rovlarini bajarish."
        ),
        "requirements": (
            "• pgAdmin yoki psql orqali bog'lanish (screenshot)\n"
            "• talabalar jadvalini yaratish (5+ ustun)\n"
            "• 10+ qator ma'lumot kiritish\n"
            "• 5 ta turli SELECT so'rovi (*, ustun tanlash, AS, ||)\n"
            "• Hisoblangan ustun bilan so'rov (`ball * 1.1`)\n"
            "• Hisobotni .sql fayl sifatida saqlash"
        ),
        "technologies": "PostgreSQL, SELECT, AS, ||",
        "deadline_days": 2,
    },
    1: {
        "title": "WHERE filterlar amaliyot",
        "description": "Talabalar jadvalida har xil WHERE shartlari bilan qidiruv.",
        "requirements": (
            "• 5 ta turli WHERE shartlari (=, >, BETWEEN, IN, LIKE, IS NULL)\n"
            "• AND/OR/NOT bilan murakkab shart (qavslar bilan)\n"
            "• `LIKE` va `ILIKE` farqi misol bilan\n"
            "• `IS NULL` va `= NULL` farqi misol bilan\n"
            "• Hisoblangan shart bilan WHERE (`ball + 5 > 80`)\n"
            "• 8+ ta turli so'rov natijasi bilan"
        ),
        "technologies": "PostgreSQL, WHERE, LIKE, BETWEEN, IN, NULL",
        "deadline_days": 2,
    },
    2: {
        "title": "Sahifalash va tartiblash",
        "description": "ORDER BY, LIMIT, OFFSET va DISTINCT bilan amaliyot.",
        "requirements": (
            "• ASC/DESC bilan tartiblash\n"
            "• Multi-column tartiblash\n"
            "• 3 ta sahifa LIMIT/OFFSET bilan\n"
            "• DISTINCT bilan unikal qiymatlar\n"
            "• COUNT(DISTINCT) ishlatish\n"
            "• Sahifalash formula tushuntirish\n"
            "• `NULLS LAST` bilan tartiblash misoli"
        ),
        "technologies": "PostgreSQL, ORDER BY, LIMIT, OFFSET, DISTINCT",
        "deadline_days": 2,
    },
    3: {  # R1
        "title": "🔁 R1: Talabalar ro'yxati hisoboti",
        "description": (
            "Maktab ma'muriyatiga hisobot — Modul 1 ning barcha tushunchalarini "
            "birga ishlatib, talabalar haqida 6 ta hisobotni bitta .sql faylga yozish."
        ),
        "requirements": (
            "• Top-3 a'lochi (ism + ball)\n"
            "• Filterlangan + tartiblangan ro'yxat\n"
            "• Takrorsiz sinflar ro'yxati\n"
            "• Yo'qotgan kunlar bo'yicha hisobot\n"
            "• Eng yosh va eng katta yoshli — UNION ALL\n"
            "• Sahifa 2 (LIMIT/OFFSET)\n"
            "• Bonus: 11-sinf top-5 a'lochilari\n"
            "• Har so'rov uchun -- komment"
        ),
        "technologies": "PostgreSQL, SELECT, WHERE, ORDER BY, LIMIT, UNION ALL",
        "deadline_days": 4,
    },
    4: {
        "title": "Statistika hisoboti (agregatlar)",
        "description": "Talabalar ma'lumoti ustida agregat funksiyalar amaliyoti.",
        "requirements": (
            "• COUNT(*), COUNT(DISTINCT) bilan misol\n"
            "• SUM/AVG/MIN/MAX bilan to'liq statistika\n"
            "• ROUND bilan o'rtacha yumaloqlash\n"
            "• String funksiyalar misoli (UPPER, LENGTH, ||)\n"
            "• Sana funksiyalari (NOW, CURRENT_DATE, EXTRACT)\n"
            "• Matematik funksiyalar (CEIL, FLOOR, MOD)\n"
            "• Ataylab WHERE'da agregat — xato ko'rsatish va sabab"
        ),
        "technologies": "PostgreSQL, COUNT, SUM, AVG, ROUND, string/date functions",
        "deadline_days": 3,
    },
    5: {
        "title": "Sinf statistikasi (GROUP BY)",
        "description": "Talabalar va baholar ustida guruhlab tahlil qilish.",
        "requirements": (
            "• Sinf bo'yicha GROUP BY + COUNT + AVG\n"
            "• HAVING bilan filterlash (80+ o'rtacha)\n"
            "• Multi-column GROUP BY (sinf + yosh)\n"
            "• STRING_AGG bilan ismlar ro'yxati\n"
            "• WHERE + GROUP BY + HAVING — uchalasini birga\n"
            "• Ataylab xato — GROUP BY siz oddiy ustun (sabab tushuntirish)"
        ),
        "technologies": "PostgreSQL, GROUP BY, HAVING, STRING_AGG",
        "deadline_days": 3,
    },
    6: {
        "title": "Jadvallarni bog'lash (JOIN)",
        "description": (
            "Talabalar, fanlar va baholar jadvallarini bog'lab "
            "haqiqiy hisobotlar tuzish."
        ),
        "requirements": (
            "• INNER JOIN bilan 3 ta jadvalni bog'lash\n"
            "• LEFT JOIN bilan bahosizlarni saqlash\n"
            "• Bahosizlarni topish (`WHERE b.id IS NULL`)\n"
            "• Har talabaning o'rtacha bahosi (LEFT JOIN + GROUP BY)\n"
            "• Har fan bo'yicha eng yuqori ball olgan talaba\n"
            "• Self JOIN misoli (xuddi sinfdoshlar)\n"
            "• Ataylab xato — implicit join (`FROM A, B WHERE ...`) — Cartesian ko'rsatish"
        ),
        "technologies": "PostgreSQL, INNER JOIN, LEFT JOIN, ON vs WHERE, self JOIN",
        "deadline_days": 4,
    },
    7: {  # R2
        "title": "🔁 R2: Maktab tahlili dashboard",
        "description": (
            "Modul 2 ning hammasi birga — JOIN + GROUP BY + HAVING bilan "
            "real maktab tahlili dashboardini yaratish."
        ),
        "requirements": (
            "• Sinf reytingi (count, avg, max, min)\n"
            "• Fan bo'yicha statistika (HAVING bilan)\n"
            "• Har fan bo'yicha eng yaxshi talaba\n"
            "• Bahosiz talabalar (LEFT JOIN + IS NULL)\n"
            "• \"Universal a'lochi\" (MIN(baho) >= 85)\n"
            "• Hamma talabalar uchun ortacha (LEFT JOIN)\n"
            "• Bonus — UNION ALL bilan dashboard metrikalari\n"
            "• Har so'rov uchun -- izoh"
        ),
        "technologies": "PostgreSQL, JOIN, GROUP BY, HAVING, subquery",
        "deadline_days": 5,
    },
    8: {
        "title": "Ma'lumotni o'zgartirish va tranzaksiya",
        "description": (
            "INSERT/UPDATE/DELETE amaliyoti, tranzaksiya bilan xavfsizlik."
        ),
        "requirements": (
            "• 5 ta INSERT (turli usul — vergulli, RETURNING bilan)\n"
            "• 3 ta UPDATE (oddiy, expression, korelatsion)\n"
            "• 2 ta DELETE (RETURNING bilan)\n"
            "• BEGIN ... ROLLBACK misol (bekor qilish)\n"
            "• BEGIN ... COMMIT misol (saqlash)\n"
            "• SAVEPOINT bilan qisman bekor qilish\n"
            "• ON CONFLICT DO UPDATE (upsert) misol\n"
            "• WHERE'siz UPDATE/DELETE — xavf tushuntirish"
        ),
        "technologies": "PostgreSQL, INSERT, UPDATE, DELETE, BEGIN/COMMIT/ROLLBACK, ON CONFLICT",
        "deadline_days": 3,
    },
    9: {
        "title": "Kichik e-shop sxemasi",
        "description": (
            "0 dan e-shop sxemasini loyihalashtirish: mahsulot, mijoz, buyurtma."
        ),
        "requirements": (
            "• 3-4 jadval CREATE TABLE\n"
            "• Har jadvalda PRIMARY KEY\n"
            "• FOREIGN KEY har bog'lanish uchun\n"
            "• NOT NULL, UNIQUE, DEFAULT, CHECK ishlatish\n"
            "• Multi-column UNIQUE misoli\n"
            "• Pul — NUMERIC(p, s), vaqt — TIMESTAMPTZ\n"
            "• ON DELETE CASCADE va RESTRICT misollari\n"
            "• ALTER TABLE bilan ustun qo'shish/o'zgartirish\n"
            "• Sxemada xato ma'lumot kiritishga urinish va xatoni ko'rsatish"
        ),
        "technologies": "PostgreSQL, CREATE TABLE, constraints, ALTER TABLE",
        "deadline_days": 5,
    },
    10: {
        "title": "Performance va EXPLAIN amaliyoti",
        "description": (
            "Katta jadvalga indeks qo'shish va EXPLAIN bilan tezlikni o'lchash."
        ),
        "requirements": (
            "• `generate_series` bilan 10000+ qator generatsiya\n"
            "• Indekssiz EXPLAIN — Seq Scan ko'rsatish\n"
            "• B-tree indeks qo'shish\n"
            "• Indeksli EXPLAIN ANALYZE — vaqt taqqoslash\n"
            "• Multi-column indeks misoli\n"
            "• Functional indeks (`LOWER(...)`) misoli\n"
            "• Partial index misoli\n"
            "• FK ustuniga indeks qo'shish (PostgreSQL avtomatik qilmaydi)\n"
            "• Indekslar narxi haqida qisqacha hisobot"
        ),
        "technologies": "PostgreSQL, CREATE INDEX, EXPLAIN ANALYZE, B-tree",
        "deadline_days": 5,
    },
    11: {  # R3
        "title": "🔁 R3: Blog DB sxemasi va hisobotlari",
        "description": (
            "Modul 3 takrorlash — to'liq blog sxemasi yaratish, ma'lumot to'ldirish, "
            "indeks va hisobotlar."
        ),
        "requirements": (
            "• 5 ta jadval (foydalanuvchilar, postlar, izohlar, teglar, post_teglar)\n"
            "• M:N munosabat — bog'lovchi jadval bilan\n"
            "• Tranzaksiya ichida test ma'lumot\n"
            "• FK ustunlariga indeks (5+ indeks)\n"
            "• 4 ta hisobot: eng faol foydalanuvchi, eng mashhur teg, "
            "har postning izohlari, 0 izohli postlar\n"
            "• Hech bo'lmaganda bittasini EXPLAIN ANALYZE bilan tekshirish\n"
            "• ON DELETE RESTRICT (postlar) va CASCADE (izohlar) farqini izohlash"
        ),
        "technologies": "PostgreSQL, schema, FK, indekslar, JOIN, GROUP BY",
        "deadline_days": 6,
    },
    12: {
        "title": "Maktab tahlili: window funksiyalar bilan",
        "description": (
            "Window funksiyalar va CTE bilan murakkab tahliliy so'rovlar."
        ),
        "requirements": (
            "• Subquery 3 turi (scalar, IN, EXISTS) — misollar\n"
            "• CTE bilan o'qish oson hisobot\n"
            "• Bir nechta CTE birgalikda (`WITH a AS ..., b AS ...`)\n"
            "• Recursive CTE misoli (1 dan 10 ga yoki kategoriya iyerarxiya)\n"
            "• ROW_NUMBER bilan har sinfdan TOP-1\n"
            "• RANK vs DENSE_RANK — farq misoli\n"
            "• LAG bilan oldingi qiymatga taqqoslash\n"
            "• Kumulyativ SUM yoki moving AVG\n"
            "• Foiz hisoblash (`x * 100 / SUM(x) OVER ()`)"
        ),
        "technologies": "PostgreSQL, CTE, WITH RECURSIVE, ROW_NUMBER, RANK, LAG, LEAD",
        "deadline_days": 5,
    },
    13: {  # L11 — CAPSTONE
        "title": "🚀 CAPSTONE: E-commerce tahlil tizimi",
        "description": (
            "Kursning yakuniy loyihasi: real e-commerce shirkati uchun "
            "to'liq tahlil tizimi — sxema, ma'lumot, indekslar va 13 ta hisobot."
        ),
        "requirements": (
            "• 5 ta jadval: kategoriyalar, mahsulotlar, mijozlar, buyurtmalar, buyurtma_elementlari\n"
            "• Hamma FK, PRIMARY KEY, NOT NULL, CHECK cheklovlari\n"
            "• Pul — NUMERIC, vaqt — TIMESTAMPTZ\n"
            "• Tranzaksiya ichida test ma'lumot (5+ kategoriya, 15+ mahsulot, 8+ mijoz, 14+ buyurtma)\n"
            "• FK va tez-tez qidiriladigan ustunlarga indekslar\n"
            "• Sotuv tahlili: jami daromad, TOP-5 mahsulot, kategoriya bo'yicha, TOP mijoz, oylik trend\n"
            "• Murakkab so'rovlar: har kategoriyaning eng qimmati (window), bir/takror mijoz, "
            "self JOIN (birga sotiladi), LAG bilan o'sish foizi, sotilmagan mahsulotlar\n"
            "• Kamida 2 ta hisobotni EXPLAIN ANALYZE bilan tekshirish\n"
            "• 1 ta qimmat so'rovni CTE bilan optimallashtirish\n"
            "• Bonus: RFM segmentatsiya (recency + frequency + monetary)\n"
            "• Hisobot — .sql fayl va natija screenshotlari"
        ),
        "technologies": (
            "PostgreSQL, full schema design, FK, indekslar, JOIN, GROUP BY, "
            "HAVING, CTE, window functions, EXPLAIN ANALYZE, transactions"
        ),
        "deadline_days": 14,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Lessons list — order, title, refs to content globals above.
# ─────────────────────────────────────────────────────────────────────────────
LESSONS = [
    {"order": 0,  "title": "1-Birinchi SELECT (database, jadval, ustun)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/HXV3zeQKqGY", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-WHERE: ma'lumotlarni filterlash",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/SpfIwlAYaKk", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-ORDER BY, LIMIT, DISTINCT",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/9Pzj7Aj25lw", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Talabalar ro'yxati (takrorlash)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/p3qvj9hO_Bo", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-Agregat funksiyalar (COUNT, SUM, AVG)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/cE6BqB1u_R0", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-GROUP BY va HAVING",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/g14OglS5_4o", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-JOIN'lar (INNER, LEFT, RIGHT, FULL)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/9yeOJ0ZMUYw", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-Maktab tahlili (takrorlash)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/3JxhSe9Xq38", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-INSERT, UPDATE, DELETE va tranzaksiyalar",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/Cz3WcZLRaWc", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-CREATE TABLE, ma'lumot turlari va cheklovlar",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/qw--VYLpxG4", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-Indekslar va EXPLAIN",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/IqAKxAcvAGE", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Blog DB sxemasi (takrorlash)",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/QlnwUkkqaUk", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Subqueries, CTE va Window funksiyalar",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/eb4ETXSwT6c", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: E-commerce tahlil tizimi",
     "text": None, "code": None, "lang": "sql",
     "video": "https://youtu.be/Cz3WcZLRaWc", "exercises": L11_EX, "_ref": "L11"},
]


def _resolve_lessons() -> None:
    """Wire text/code globals into LESSONS rows by their _ref slug."""
    g = globals()
    for row in LESSONS:
        ref = row["_ref"]
        row["text"] = g[f"{ref}_TEXT"]
        row["code"] = g[f"{ref}_CODE"]


# ─────────────────────────────────────────────────────────────────────────────
# Seed / persistence
# ─────────────────────────────────────────────────────────────────────────────
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
