"""Seed "SQL: Ma'lumotlar Bazasi Dizayni" (13 lessons): the first follow-on
course in the SQL category after "SQL va PostgreSQL Asoslari" (course 41).

Where course 41 taught students to *query* a schema someone else designed,
this course teaches them to *design* it: 1NF/2NF/3NF/BCNF, 1:1 / 1:N / N:N
relationships, key strategies and referential actions, declarative
constraints, ER diagrams, deliberate denormalization, and finally a
critique-and-redesign of the exact e-commerce schema they built in course
41's capstone (lesson 368).

Usage:
    cd backend
    python scripts/seed_sql_database_design.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists,
and skips already-seeded lessons by order.
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
from app.models.lesson_sample import LessonSample  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Course-level metadata
# ─────────────────────────────────────────────────────────────────────────────
COURSE = {
    "title": "SQL: Ma'lumotlar Bazasi Dizayni",
    "description": (
        "Sxemani nima uchun aynan shunday qurish kerakligini o'rgatadigan kurs: "
        "normalizatsiya (1NF, 2NF, 3NF, BCNF), 1:1 / 1:N / N:N munosabatlar va "
        "junction jadvallar, natural va surrogate kalitlar, ON DELETE CASCADE / "
        "SET NULL, CHECK va UNIQUE cheklovlar, ER diagrammalar hamda ongli "
        "denormalizatsiya. Yakunda — kutubxona, ijtimoiy tarmoq va booking "
        "tizimlari sxemasini noldan loyihalash."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 4,
    "max_points": 181,
    "category_id": 10,  # SQL
    "prerequisite_course_id": 41,  # SQL va PostgreSQL Asoslari
    "display_order": 501,  # right after course 41 (display_order=500)
    "is_active": True,
    "is_published": False,  # human review before it goes live
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson plan
# ═════════════════════════════════════════════════════════════════════════════
LESSON_PLAN = [
    {"order": 0, "ref": "L1", "status": "done", "points": 12,
     "title": "1-Normalizatsiya nima va nega kerak (1NF)",
     "scope": "Anomaliyalar, takrorlanuvchi guruhlar, atomik qiymatlar, 1NF."},
    {"order": 1, "ref": "L2", "status": "done", "points": 13,
     "title": "2-2NF va 3NF — takrorlanuvchi ma'lumotlarni yo'qotish",
     "scope": "Qisman bog'liqlik (2NF), tranzitiv bog'liqlik (3NF)."},
    {"order": 2, "ref": "L3", "status": "done", "points": 14,
     "title": "3-BCNF va normalizatsiyaning chegaralari",
     "scope": "Boyce-Codd normal forma, 3NF yetmagan holat, ortiqcha normalizatsiya."},
    {"order": 3, "ref": "L4", "status": "done", "points": 12,
     "title": "4-Munosabatlar: 1:1 va 1:N",
     "scope": "users/user_profiles (1:1), mualliflar/kitoblar (1:N), FK joylashuvi."},
    {"order": 4, "ref": "L5", "status": "done", "points": 13,
     "title": "5-Munosabatlar: N:N va junction jadvallar",
     "scope": "talabalar/kurslar via enrollments, kompozit kalit, qo'shimcha atributlar."},
    {"order": 5, "ref": "R1", "status": "done", "points": 15,
     "title": "R1-Kutubxona tizimi sxemasini loyihalash (takrorlash)",
     "scope": "1NF-3NF + 1:1/1:N/N:N — kutubxona sxemasi mini-loyiha."},
    {"order": 6, "ref": "L6", "status": "done", "points": 13,
     "title": "6-Primary/Foreign key strategiyalari, ON DELETE CASCADE/SET NULL",
     "scope": "Natural vs surrogate kalit, referensial yaxlitlik, CASCADE/SET NULL/RESTRICT."},
    {"order": 7, "ref": "L7", "status": "done", "points": 12,
     "title": "7-Check constraints, unique constraints, default qiymatlar",
     "scope": "CHECK, UNIQUE, NOT NULL, DEFAULT — biznes qoidalarini DB darajasida majburlash."},
    {"order": 8, "ref": "L8", "status": "done", "points": 13,
     "title": "8-ER diagrammalar — loyihadan kodgacha",
     "scope": "Crow's foot notatsiyasi, mermaid erDiagram, diagrammadan CREATE TABLE'ga."},
    {"order": 9, "ref": "L9", "status": "done", "points": 14,
     "title": "9-Denormalizatsiya — qachon va nega buzish kerak",
     "scope": "O'qish tezligi uchun ongli denormalizatsiya, hisoblangan ustunlar, trigger, MATERIALIZED VIEW."},
    {"order": 10, "ref": "R2", "status": "done", "points": 15,
     "title": "R2-Ijtimoiy tarmoq DB sxemasi (takrorlash)",
     "scope": "users/posts/comments/likes/follows — self-referential N:N mini-loyiha."},
    {"order": 11, "ref": "L10", "status": "done", "points": 15,
     "title": "10-Real-world case: E-commerce sxemasini noldan qayta loyihalash",
     "scope": "Course 41 capstone sxemasini tanqid qilish va qayta loyihalash."},
    {"order": 12, "ref": "C1", "status": "done", "points": 20,
     "title": "11-CAPSTONE: Ko'p jadvalli booking/reservation tizimi",
     "scope": "Mehmonxona/tadbir booking tizimi: users, listings, bookings, payments, reviews."},
]


# ═════════════════════════════════════════════════════════════════════════════
# L1 — Normalizatsiya nima va nega kerak (1NF)
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h3>Normalizatsiya nima?</h3>
<p><strong>Normalizatsiya</strong> &mdash; jadvallarni shunday qayta tashkil qilish jarayoniki, har bir fakt bazada <em>aniq bitta joyda</em> saqlansin. Bu shunchaki "chiroyli sxema" masalasi emas. Agar bitta fakt (masalan, mijozning telefon raqami) o'nta qatorda takrorlansa, ertami-kechmi ulardan to'qqiztasi yangilanadi-yu, bittasi eski qolib ketadi &mdash; va sizning bazangiz endi o'zi bilan o'zi ziddiyatda bo'ladi.</p>
<p>Oldingi kursda siz tayyor sxemadan <code>SELECT</code> qilishni o'rgandingiz. Bu kurs esa boshqa savolga javob beradi: <strong>nima uchun</strong> o'sha sxema aynan shunday tuzilgan edi?</p>

<h3>Uchta anomaliya &mdash; muammoning asl nomi</h3>
<p>Yomon loyihalangan jadval quyidagi uchta muammoni keltirib chiqaradi. Ular kitoblarda "anomaliya" deb ataladi:</p>
<ul>
<li><strong>INSERT anomaliyasi</strong> &mdash; yangi faktni kiritish uchun sizda hali mavjud bo'lmagan boshqa fakt talab qilinadi. Masalan, hali birorta buyurtma bermagan yangi mijozni saqlab bo'lmaydi, chunki mijoz ma'lumoti faqat buyurtmalar jadvalida yashaydi.</li>
<li><strong>UPDATE anomaliyasi</strong> &mdash; bitta faktni o'zgartirish uchun bir nechta qatorni yangilash kerak. Bittasini unutsangiz &mdash; ma'lumot ziddiyatli bo'ladi.</li>
<li><strong>DELETE anomaliyasi</strong> &mdash; bir qatorni o'chirish siz o'chirmoqchi bo'lmagan faktni ham yo'q qiladi. Mijozning oxirgi buyurtmasini o'chirsangiz, mijozning o'zi ham bazadan yo'qoladi.</li>
</ul>
<p>Normalizatsiya &mdash; aynan shu uchta anomaliyaga qarshi qurol. Boshqa hech narsaga emas.</p>

<h3>Birinchi normal forma (1NF)</h3>
<p>Jadval 1NF da hisoblanadi, agar:</p>
<ul>
<li>Har bir katakdagi qiymat <strong>atomik</strong> (bo'linmas) bo'lsa &mdash; ichida vergul bilan ajratilgan ro'yxat yoki JSON massiv yashirinmasa.</li>
<li>Jadvalda <strong>takrorlanuvchi guruhlar</strong> bo'lmasa &mdash; ya'ni <code>mahsulot_1</code>, <code>mahsulot_2</code>, <code>mahsulot_3</code> kabi raqamlangan ustunlar bo'lmasa.</li>
<li>Har bir qator noyob bo'lsa &mdash; ya'ni jadvalda birlamchi kalit (PRIMARY KEY) bo'lsa.</li>
</ul>

<h3>Oldin va keyin</h3>
<table>
<tr><th>Xususiyat</th><th>Normalizatsiyadan oldin</th><th>1NF dan keyin</th></tr>
<tr><td>Mahsulotlar</td><td>bitta TEXT ustunda: 'iPhone 15, Chexol'</td><td>har biri alohida qatorda</td></tr>
<tr><td>"Nechta Chexol sotildi?"</td><td><code>LIKE '%Chexol%'</code> &mdash; noto'g'ri natija</td><td><code>SUM(miqdor)</code> &mdash; aniq javob</td></tr>
<tr><td>Miqdorni o'zgartirish</td><td>matnni qo'lda parse qilish</td><td>oddiy <code>UPDATE</code></td></tr>
<tr><td>Cheklov qo'yish</td><td>imkonsiz</td><td><code>CHECK (miqdor &gt; 0)</code></td></tr>
<tr><td>Indeks</td><td>foydasiz (matn ichida qidiruv)</td><td>ustunga to'g'ridan-to'g'ri</td></tr>
</table>

<pre class="mermaid">
flowchart LR
  A["buyurtmalar_xom
mahsulotlar = 'iPhone 15, Chexol, Quloqchin'
miqdorlar = '1, 2, 1'"] -->|"1NF: har qiymat atomik,
har qator noyob"| B["buyurtma_qatorlari
1 qator = 1 mahsulot
PRIMARY KEY (buyurtma_id, mahsulot_nomi)"]
</pre>

<h3>Eng ko'p uchraydigan xato</h3>
<p>Boshlovchilar ko'pincha shunday deydi: "Men mahsulotlarni vergul bilan bitta ustunga yozaman, keyin dasturda <code>split(',')</code> qilaman &mdash; shunday tezroq". Bu &mdash; ma'lumotlar bazasini oddiy fayl sifatida ishlatish. Siz bir zumda quyidagilarni yo'qotasiz: <code>JOIN</code>, <code>SUM</code>, <code>GROUP BY</code>, <code>FOREIGN KEY</code>, <code>CHECK</code>, indeks va tranzaksion yaxlitlik. Ya'ni bazani tanlashning butun ma'nosini.</p>
<p>Eslatma: PostgreSQL da massiv (<code>text[]</code>) va <code>JSONB</code> turlari bor va ular real loyihalarda ishlatiladi &mdash; lekin ular <em>o'zaro bog'lanadigan mohiyatlar</em> (entity) uchun emas, balki tuzilmasi oldindan noma'lum, hech qachon <code>JOIN</code> qilinmaydigan qo'shimcha ma'lumot uchun. Mahsulot &mdash; bu mohiyat, shuning uchun u alohida qatorda yashashi kerak.</p>
"""

L1_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- 1NF: normalizatsiyadan oldin va keyin — real misol
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- 1-QADAM: "yomon" jadval. Mahsulotlar vergul bilan bitta TEXT ustunda.
-- Bu — takrorlanuvchi guruh, ya'ni 1NF buzilgan.
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtmalar_xom;

CREATE TABLE buyurtmalar_xom (
    buyurtma_id   INTEGER PRIMARY KEY,
    mijoz_ism     VARCHAR(60),
    mijoz_telefon VARCHAR(20),
    mahsulotlar   TEXT,   -- 'iPhone 15, Chexol, Quloqchin'  <- atomik EMAS
    miqdorlar     TEXT    -- '1, 2, 1'                       <- atomik EMAS
);

INSERT INTO buyurtmalar_xom VALUES
    (1, 'Aziz Karimov',     '+998901112233', 'iPhone 15, Chexol, Quloqchin', '1, 2, 1'),
    (2, 'Dilnoza Rasulova', '+998907778899', 'MacBook Pro',                  '1'),
    (3, 'Aziz Karimov',     '+998901112233', 'Chexol, Quloqchin',           '3, 2');

-- Savol: jami nechta "Chexol" sotildi? Bu jadvalda aniq javob YO'Q.
-- LIKE faqat QATORLARNI sanaydi, miqdorni emas:
SELECT COUNT(*) AS chexol_bor_buyurtmalar
FROM buyurtmalar_xom
WHERE mahsulotlar LIKE '%Chexol%';
-- Natija: 2. Lekin haqiqiy sotilgan miqdor 2 + 3 = 5.
-- Yana yomoni: 'Chexol Pro' degan mahsulot bo'lsa, LIKE uni ham qo'shib
-- yuboradi. Ya'ni javob nafaqat noto'g'ri, balki jimgina noto'g'ri.

-- UPDATE anomaliyasi: Azizning telefoni o'zgarsa, uni IKKI qatorda
-- yangilash kerak. Bittasi unutilsa — bazada ikkita turli telefon qoladi.
UPDATE buyurtmalar_xom
SET mijoz_telefon = '+998901110000'
WHERE buyurtma_id = 1;   -- 3-buyurtma eski raqam bilan qoldi!

SELECT DISTINCT mijoz_ism, mijoz_telefon FROM buyurtmalar_xom;
-- Aziz Karimov ikki xil telefon bilan chiqadi — ma'lumot buzildi.

-- ─────────────────────────────────────────────────────────────────────
-- 2-QADAM: 1NF ga o'tkazamiz. Har bir mahsulot — alohida qator.
-- Endi har katakda bitta bo'linmas (atomik) qiymat turadi.
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtma_qatorlari;

CREATE TABLE buyurtma_qatorlari (
    buyurtma_id   INTEGER      NOT NULL,
    mahsulot_nomi VARCHAR(60)  NOT NULL,
    miqdor        INTEGER      NOT NULL CHECK (miqdor > 0),
    mijoz_ism     VARCHAR(60)  NOT NULL,
    mijoz_telefon VARCHAR(20)  NOT NULL,
    -- Kompozit birlamchi kalit: bitta buyurtmada bir mahsulot bir marta
    PRIMARY KEY (buyurtma_id, mahsulot_nomi)
);

INSERT INTO buyurtma_qatorlari VALUES
    (1, 'iPhone 15',  1, 'Aziz Karimov',     '+998901112233'),
    (1, 'Chexol',     2, 'Aziz Karimov',     '+998901112233'),
    (1, 'Quloqchin',  1, 'Aziz Karimov',     '+998901112233'),
    (2, 'MacBook Pro',1, 'Dilnoza Rasulova', '+998907778899'),
    (3, 'Chexol',     3, 'Aziz Karimov',     '+998901112233'),
    (3, 'Quloqchin',  2, 'Aziz Karimov',     '+998901112233');

-- Endi savolga ANIQ javob bor — oddiy agregat yetarli:
SELECT mahsulot_nomi, SUM(miqdor) AS jami_sotilgan
FROM buyurtma_qatorlari
GROUP BY mahsulot_nomi
ORDER BY jami_sotilgan DESC;
-- Chexol -> 5. To'g'ri javob.

-- Bonus: endi cheklov ham ishlaydi. Manfiy miqdorni baza o'zi rad etadi:
-- INSERT INTO buyurtma_qatorlari VALUES (4, 'Chexol', -1, 'X', '+998900000000');
-- ERROR:  new row violates check constraint "buyurtma_qatorlari_miqdor_check"

-- ─────────────────────────────────────────────────────────────────────
-- MUHIM: bu jadval 1NF da, LEKIN hali ham mukammal emas.
-- mijoz_ism va mijoz_telefon har qatorda takrorlanmoqda — UPDATE
-- anomaliyasi hamon bor. Uni 2NF va 3NF hal qiladi (keyingi dars).
-- ─────────────────────────────────────────────────────────────────────
SELECT buyurtma_id, mijoz_ism, COUNT(*) AS takrorlanish
FROM buyurtma_qatorlari
GROUP BY buyurtma_id, mijoz_ism
ORDER BY buyurtma_id;
"""

L1_EX = [
    {
        "title": "1NF ning asosiy talabi",
        "description": "Jadval Birinchi Normal Formada (1NF) bo'lishi uchun ustundagi qiymatlar qanday bo'lishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir katakda bitta bo'linmas (atomik) qiymat bo'lishi kerak",
            "Har bir ustun matn (TEXT) turida bo'lishi kerak",
            "Barcha ustunlarda UNIQUE cheklov bo'lishi kerak",
            "Jadvalda kamida uchta ustun bo'lishi kerak",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bitta katakda vergul bilan ajratilgan ro'yxat turgan bo'lsa, bu shart buzilgan.",
        "explanation": "1NF ning asosiy talabi — atomiklik: har bir katakda faqat bitta bo'linmas qiymat turishi kerak. 'iPhone, Chexol, Quloqchin' kabi ro'yxat bu talabni buzadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Anomaliyaning nomi",
        "description": "Mijozning telefon raqami 10 ta qatorda takrorlangan. Raqamni o'zgartirganda 9 tasi yangilandi, bittasi eski qoldi — natijada bazada ziddiyat paydo bo'ldi. Bu qanday anomaliya? Bo'sh joyni bitta so'z bilan to'ldiring: ___ anomaliyasi.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "UPDATE",
        "hint": "Ma'lumotni o'zgartirish paytida yuz beradigan muammo.",
        "explanation": "Bir faktni o'zgartirish uchun bir nechta qatorni yangilash kerak bo'lsa va ulardan biri unutilsa — bu UPDATE anomaliyasi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1NF ga o'tkazish qadamlari",
        "description": "Vergul bilan ajratilgan ro'yxat saqlaydigan jadvalni 1NF ga o'tkazish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Atomik bo'lmagan (ro'yxat saqlaydigan) ustunlarni aniqlash",
            "Ro'yxatdagi har bir element uchun alohida qator ajratish",
            "Qatorni noyob qiladigan birlamchi kalitni belgilash",
            "Endi mumkin bo'lgan cheklovlarni qo'shish (CHECK, NOT NULL)",
        ],
        "correct_order": [
            "Atomik bo'lmagan (ro'yxat saqlaydigan) ustunlarni aniqlash",
            "Ro'yxatdagi har bir element uchun alohida qator ajratish",
            "Qatorni noyob qiladigan birlamchi kalitni belgilash",
            "Endi mumkin bo'lgan cheklovlarni qo'shish (CHECK, NOT NULL)",
        ],
        "hint": "Avval muammoni topamiz, keyin qatorlarga yoyamiz, keyin kalit va cheklov.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L2 — 2NF va 3NF
# ═════════════════════════════════════════════════════════════════════════════
L2_TEXT = """\
<h3>1NF yetarli emas edi</h3>
<p>Oldingi darsda biz jadvalni 1NF ga keltirdik, lekin muammo tugamadi: <code>mijoz_ism</code> va <code>mijoz_telefon</code> har bir qatorda takrorlanaverdi. 2NF va 3NF aynan shu takrorlanishni yo'q qiladi.</p>
<p>Ikkalasi ham bitta g'oyaning ikki bosqichi: <strong>har bir noqalit ustun butun birlamchi kalitga, faqat unga va boshqa hech narsaga bog'liq bo'lishi kerak</strong>.</p>

<h3>Funksional bog'liqlik &mdash; asosiy tushuncha</h3>
<p>Agar <code>A</code> ustunining qiymati <code>B</code> ustunining qiymatini bir qiymatli aniqlab bersa, buni <code>A &rarr; B</code> deb yozamiz va "B funksional ravishda A ga bog'liq" deymiz. Masalan <code>mijoz_id &rarr; mijoz_telefon</code>: mijoz nomerini bilsak, telefonini ham bilamiz.</p>

<h3>Ikkinchi normal forma (2NF): qisman bog'liqlikni yo'qotish</h3>
<p>2NF faqat <strong>kompozit</strong> (bir nechta ustundan iborat) birlamchi kalitli jadvallar uchun ma'noga ega. Qoida: hech bir noqalit ustun kalitning <em>bir qismiga</em> bog'liq bo'lmasligi kerak.</p>
<p>Misol: <code>PRIMARY KEY (buyurtma_id, mahsulot_nomi)</code> bo'lgan jadvalda <code>mahsulot_narxi</code> ustuni bor. Narx faqat <code>mahsulot_nomi</code> ga bog'liq, <code>buyurtma_id</code> ga umuman aloqasi yo'q &mdash; bu <strong>qisman bog'liqlik</strong> (partial dependency). Natijada bitta mahsulotning narxi o'nlab qatorda takrorlanadi.</p>

<h3>Uchinchi normal forma (3NF): tranzitiv bog'liqlikni yo'qotish</h3>
<p>3NF qoidasi: hech bir noqalit ustun boshqa noqalit ustun orqali kalitga bog'lanmasligi kerak.</p>
<p>Misol: <code>buyurtmalar(buyurtma_id PK, mijoz_id, mijoz_shahri, shahar_viloyati)</code>. Bu yerda <code>buyurtma_id &rarr; mijoz_shahri &rarr; shahar_viloyati</code> zanjiri bor. Viloyat aslida buyurtmaga emas, shaharga bog'liq &mdash; bu <strong>tranzitiv bog'liqlik</strong> (transitive dependency).</p>

<h3>Qisqacha eslab qolish uchun</h3>
<table>
<tr><th>Forma</th><th>Nimani talab qiladi</th><th>Nimani yo'qotadi</th></tr>
<tr><td>1NF</td><td>Atomik qiymatlar, takrorlanuvchi guruh yo'q</td><td>Ro'yxat saqlaydigan ustunlar</td></tr>
<tr><td>2NF</td><td>1NF + kalitning qismiga bog'liqlik yo'q</td><td>Qisman bog'liqlik</td></tr>
<tr><td>3NF</td><td>2NF + noqalit &rarr; noqalit bog'liqlik yo'q</td><td>Tranzitiv bog'liqlik</td></tr>
</table>
<p>Klassik mnemonika: <em>"har bir noqalit ustun kalitga, butun kalitga va faqat kalitga bog'liq bo'lsin"</em>. "Kalitga" &mdash; 1NF, "butun kalitga" &mdash; 2NF, "faqat kalitga" &mdash; 3NF.</p>

<pre class="mermaid">
flowchart TB
  A["buyurtma_qatorlari (1NF)
buyurtma_id, mahsulot_nomi, miqdor,
mahsulot_narxi, mijoz_ism, mijoz_telefon, mijoz_shahri, shahar_viloyati"]
  A -->|"2NF: mahsulot_narxi faqat
mahsulot_nomi ga bog'liq"| B["mahsulotlar
id PK, nomi, narx"]
  A -->|"3NF: viloyat shaharga,
shahar mijozga bog'liq"| C["mijozlar
id PK, ism, telefon, shahar_id"]
  C --> D["shaharlar
id PK, nomi, viloyat"]
  A -->|"qolgani"| E["buyurtma_elementlari
buyurtma_id, mahsulot_id, miqdor"]
</pre>

<h3>Amaliy foyda</h3>
<p>Normalizatsiyadan keyin mahsulot narxini o'zgartirish &mdash; bitta <code>UPDATE mahsulotlar SET narx = ... WHERE id = ...</code>. Normalizatsiyagacha esa yuzlab qatorni yangilash kerak edi va ulardan bittasi doim unutilardi. Bu &mdash; nazariya emas, bu haqiqiy loyihalarda eng ko'p uchraydigan ma'lumot buzilishining sababi.</p>
"""

L2_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- 2NF va 3NF: yassi jadvalni bosqichma-bosqich normallashtirish
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- BOSHLANG'ICH HOLAT: 1NF da, lekin 2NF va 3NF buzilgan
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtmalar_yassi;

CREATE TABLE buyurtmalar_yassi (
    buyurtma_id     INTEGER      NOT NULL,
    mahsulot_nomi   VARCHAR(60)  NOT NULL,
    miqdor          INTEGER      NOT NULL CHECK (miqdor > 0),
    -- 2NF buzilishi: narx kalitning FAQAT bir qismiga (mahsulot_nomi) bog'liq
    mahsulot_narxi  NUMERIC(12,2) NOT NULL,
    -- 3NF buzilishi: shahar mijozga, viloyat esa shaharga bog'liq
    mijoz_ism       VARCHAR(60)  NOT NULL,
    mijoz_shahri    VARCHAR(40)  NOT NULL,
    shahar_viloyati VARCHAR(40)  NOT NULL,
    PRIMARY KEY (buyurtma_id, mahsulot_nomi)
);

INSERT INTO buyurtmalar_yassi VALUES
    (1, 'iPhone 15', 1, 15000000, 'Aziz Karimov',     'Toshkent',  'Toshkent shahri'),
    (1, 'Chexol',    2,    85000, 'Aziz Karimov',     'Toshkent',  'Toshkent shahri'),
    (2, 'iPhone 15', 1, 15000000, 'Dilnoza Rasulova', 'Samarqand', 'Samarqand viloyati'),
    (3, 'Chexol',    3,    85000, 'Aziz Karimov',     'Toshkent',  'Toshkent shahri');

-- Muammoni ko'rsatamiz: iPhone narxi 2 qatorda, Chexol narxi 2 qatorda
-- takrorlangan. Narxni oshirish uchun BARCHA qatorni yangilash kerak.
SELECT mahsulot_nomi, COUNT(*) AS narx_necha_marta_takrorlangan
FROM buyurtmalar_yassi
GROUP BY mahsulot_nomi;

-- ─────────────────────────────────────────────────────────────────────
-- 2NF: qisman bog'liqlikni ajratamiz -> mahsulotlar alohida jadval
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtma_elementlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;
DROP TABLE IF EXISTS shaharlar;
DROP TABLE IF EXISTS mahsulotlar;

CREATE TABLE mahsulotlar (
    id   SERIAL        PRIMARY KEY,
    nomi VARCHAR(60)   NOT NULL UNIQUE,
    narx NUMERIC(12,2) NOT NULL CHECK (narx > 0)
);

-- ─────────────────────────────────────────────────────────────────────
-- 3NF: tranzitiv bog'liqlikni ajratamiz.
-- shahar_viloyati -> shaharlar jadvaliga, shahar -> mijozlar jadvaliga.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE shaharlar (
    id       SERIAL      PRIMARY KEY,
    nomi     VARCHAR(40) NOT NULL UNIQUE,
    viloyati VARCHAR(40) NOT NULL
);

CREATE TABLE mijozlar (
    id        SERIAL      PRIMARY KEY,
    ism       VARCHAR(60) NOT NULL,
    shahar_id INTEGER     NOT NULL REFERENCES shaharlar(id)
);

CREATE TABLE buyurtmalar (
    id         SERIAL      PRIMARY KEY,
    mijoz_id   INTEGER     NOT NULL REFERENCES mijozlar(id),
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Bog'lovchi jadval: faqat kompozit kalitga TO'LIQ bog'liq ustunlar qoldi
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER NOT NULL REFERENCES mahsulotlar(id),
    miqdor      INTEGER NOT NULL CHECK (miqdor > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)
);

-- ── Ma'lumotni ko'chiramiz ────────────────────────────────────────────
INSERT INTO mahsulotlar (nomi, narx)
SELECT DISTINCT mahsulot_nomi, mahsulot_narxi FROM buyurtmalar_yassi;

INSERT INTO shaharlar (nomi, viloyati)
SELECT DISTINCT mijoz_shahri, shahar_viloyati FROM buyurtmalar_yassi;

INSERT INTO mijozlar (ism, shahar_id)
SELECT DISTINCT y.mijoz_ism, s.id
FROM buyurtmalar_yassi y
JOIN shaharlar s ON s.nomi = y.mijoz_shahri;

INSERT INTO buyurtmalar (id, mijoz_id)
SELECT DISTINCT y.buyurtma_id, m.id
FROM buyurtmalar_yassi y
JOIN mijozlar m ON m.ism = y.mijoz_ism;

-- SERIAL hisoblagichini qo'lda kiritilgan id lardan keyinga suramiz
SELECT setval('buyurtmalar_id_seq', (SELECT MAX(id) FROM buyurtmalar));

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor)
SELECT y.buyurtma_id, p.id, y.miqdor
FROM buyurtmalar_yassi y
JOIN mahsulotlar p ON p.nomi = y.mahsulot_nomi;

-- ─────────────────────────────────────────────────────────────────────
-- NATIJA: endi narx BITTA joyda. Bitta UPDATE — hamma joyda o'zgardi.
-- ─────────────────────────────────────────────────────────────────────
UPDATE mahsulotlar SET narx = 16000000 WHERE nomi = 'iPhone 15';

-- Eski yassi ko'rinishni JOIN bilan qayta yig'ib olamiz —
-- ma'lumot yo'qolmadi, faqat to'g'ri joyga taqsimlandi.
SELECT b.id            AS buyurtma_id,
       m.ism           AS mijoz,
       s.nomi          AS shahar,
       s.viloyati      AS viloyat,
       p.nomi          AS mahsulot,
       e.miqdor,
       p.narx,
       e.miqdor * p.narx AS qator_summasi
FROM buyurtma_elementlari e
JOIN buyurtmalar b ON b.id = e.buyurtma_id
JOIN mijozlar    m ON m.id = b.mijoz_id
JOIN shaharlar   s ON s.id = m.shahar_id
JOIN mahsulotlar p ON p.id = e.mahsulot_id
ORDER BY b.id, p.nomi;
"""

L2_EX = [
    {
        "title": "Qisman bog'liqlik qaysi normal formani buzadi?",
        "description": "PRIMARY KEY (buyurtma_id, mahsulot_id) bo'lgan jadvalda mahsulot_narxi ustuni bor va u faqat mahsulot_id ga bog'liq. Bu qaysi normal formaning talabini buzadi?",
        "exercise_type": "multiple_choice",
        "options": ["1NF", "2NF", "3NF", "BCNF"],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Kalitning bir qismiga bog'liqlik — bu qanday bog'liqlik deb ataladi?",
        "explanation": "Noqalit ustun kompozit kalitning faqat bir qismiga bog'liq bo'lsa — bu qisman bog'liqlik (partial dependency) va u aynan 2NF talabini buzadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Tranzitiv bog'liqlik nomi",
        "description": "buyurtmalar(buyurtma_id PK, mijoz_shahri, shahar_viloyati) jadvalida buyurtma_id -> mijoz_shahri -> shahar_viloyati zanjiri bor. Bunday bog'liqlik nima deb ataladi? (ikki so'z bilan yozing)",
        "exercise_type": "text_input",
        "expected_answer": "tranzitiv bog'liqlik",
        "hint": "Noqalit ustun boshqa noqalit ustun orqali kalitga bog'langan.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "3NF haqida to'g'ri fikrlar",
        "description": "Quyidagilardan qaysilari 3NF haqida to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": [
            "3NF bo'lishi uchun jadval avval 2NF da bo'lishi shart",
            "3NF noqalit ustunlar orasidagi bog'liqlikni taqiqlaydi",
            "3NF jadvaldagi barcha ustunlarni UNIQUE qilishni talab qiladi",
            "3NF UPDATE anomaliyasini kamaytiradi",
        ],
        "correct_answers": "A,B,D",
        "is_multiple_select": True,
        "hint": "Bittasi UNIQUE cheklovi haqida — bu normalizatsiyaga umuman aloqador emas.",
        "explanation": "Normal formalar bosqichma-bosqich: 3NF avvalo 2NF ni talab qiladi, noqalit ustunlar orasidagi (tranzitiv) bog'liqlikni taqiqlaydi va shu orqali UPDATE anomaliyasini kamaytiradi. Barcha ustunlarni UNIQUE qilish talabi hech qaysi normal formada yo'q.",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L3 — BCNF va normalizatsiyaning chegaralari
# ═════════════════════════════════════════════════════════════════════════════
L3_TEXT = """\
<h3>3NF yetmagan holat</h3>
<p>3NF juda kuchli, lekin u bitta teshik qoldiradi. 3NF qoidasi noqalit ustunlarni tekshiradi &mdash; ammo agar bog'liqlikning <em>chap tomonida</em> noqalit ustun, o'ng tomonida esa kalitning bir qismi tursa, 3NF buni sezmaydi.</p>
<p><strong>Boyce-Codd normal forma (BCNF)</strong> qoidasi ancha sodda va qat'iy: <em>har qanday <code>X &rarr; Y</code> funksional bog'liqlikda <code>X</code> nomzod kalit (candidate key) bo'lishi shart</em>. Bo'lmasa &mdash; jadval BCNF da emas.</p>

<h3>Klassik misol: o'qituvchi &rarr; fan</h3>
<p>Universitet jadvalini ko'ramiz: <code>darslar(talaba_id, fan, oqituvchi)</code>.</p>
<p>Biznes qoidalari:</p>
<ul>
<li>Bitta talaba bitta fanni faqat bitta o'qituvchidan o'qiydi &rarr; <code>(talaba_id, fan) &rarr; oqituvchi</code></li>
<li>Har bir o'qituvchi faqat bitta fanni o'qitadi &rarr; <code>oqituvchi &rarr; fan</code></li>
</ul>
<p>Nomzod kalitlar: <code>(talaba_id, fan)</code> va <code>(talaba_id, oqituvchi)</code>. Jadvalda noqalit ustun umuman yo'q &mdash; demak, 3NF <strong>buzilmagan</strong>. Lekin <code>oqituvchi &rarr; fan</code> bog'liqligining chap tomoni (<code>oqituvchi</code>) kalit emas. Ya'ni BCNF buzilgan.</p>
<p>Oqibati aniq: "Karimov &mdash; Fizika o'qituvchisi" fakti unga yozilgan har bir talaba uchun takrorlanadi. Karimov Kimyoga o'tsa, o'nlab qator yangilanishi kerak. Va eng yomoni: hali birorta talabasi yo'q yangi o'qituvchini bazaga umuman kirita olmaymiz (INSERT anomaliyasi).</p>

<h3>Yechim</h3>
<p>Jadvalni ikkiga bo'lamiz: <code>oqituvchilar(oqituvchi PK, fan)</code> va <code>royxat(talaba_id, oqituvchi)</code>. Endi har ikkala jadval ham BCNF da.</p>
<p>Halol bo'lish kerak: bu bo'linish bir narsani <em>yo'qotadi</em>. Endi "bitta talaba bitta fanni ikki xil o'qituvchidan o'qimasin" qoidasini faqat jadval strukturasi bilan ta'minlab bo'lmaydi &mdash; unga alohida <code>UNIQUE</code> yoki trigger kerak. Bu BCNF ning ma'lum narxi: u har doim ham bog'liqliklarni saqlab qolmaydi (dependency preservation).</p>

<table>
<tr><th>Forma</th><th>Qoida</th><th>Amalda qanchalik kerak</th></tr>
<tr><td>1NF</td><td>Atomik qiymatlar</td><td>Har doim majburiy</td></tr>
<tr><td>2NF</td><td>Qisman bog'liqlik yo'q</td><td>Har doim majburiy</td></tr>
<tr><td>3NF</td><td>Tranzitiv bog'liqlik yo'q</td><td>Amaliy standart &mdash; 95% loyihalar shu yerda to'xtaydi</td></tr>
<tr><td>BCNF</td><td>Har bir determinant &mdash; nomzod kalit</td><td>Bir nechta ustma-ust nomzod kalit bo'lganda</td></tr>
<tr><td>4NF / 5NF</td><td>Ko'p qiymatli bog'liqliklar</td><td>Kamdan-kam, asosan nazariy</td></tr>
</table>

<h3>Ortiqcha normalizatsiya &mdash; halol gaplashamiz</h3>
<p>Normalizatsiya bepul emas. Har bir yangi jadval &mdash; bu har bir so'rovda yana bitta <code>JOIN</code>. Quyidagi holatlarda to'xtash oqilona:</p>
<ul>
<li><strong>Manzil ustunlarini haddan tashqari maydalash.</strong> <code>shaharlar</code>, <code>tumanlar</code>, <code>ko'chalar</code>, <code>uylar</code> jadvallari &mdash; agar siz statistikani viloyat bo'yicha hisoblamasangiz, bu 4 ta ortiqcha <code>JOIN</code>dan boshqa hech narsa bermaydi.</li>
<li><strong>Tarixiy qiymatlar.</strong> Buyurtma qatorida <code>narx_birlik</code> ni saqlash &mdash; bu takrorlanish emas, balki <em>boshqa fakt</em>: "sotuv paytidagi narx". Mahsulot narxi keyin o'zgarsa, eski chekdagi summa o'zgarmasligi kerak. Buni "denormalizatsiya" deb atash xato.</li>
<li><strong>1&ndash;2 qiymatli lug'atlar.</strong> <code>jins</code> yoki <code>holat</code> uchun alohida jadval o'rniga <code>CHECK (holat IN (...))</code> yoki <code>ENUM</code> ko'pincha yetarli va o'qishga ancha qulay.</li>
</ul>
<p><strong>Amaliy tavsiya:</strong> 3NF gacha normallashtiring &mdash; bu deyarli har doim to'g'ri javob. BCNF ni faqat bir nechta ustma-ust nomzod kalit bo'lgan holatda qo'llang. Undan yuqorisi (4NF, 5NF) real loyihalarda deyarli hech qachon kerak bo'lmaydi. Va faqat o'lchangan performance muammosi bo'lgandagina denormalizatsiya haqida o'ylang &mdash; bu haqda 9-darsda gaplashamiz.</p>
"""

L3_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- BCNF: 3NF da bo'lgan, lekin BCNF ni buzadigan jadval
-- ═══════════════════════════════════════════════════════════════════════

-- Biznes qoidalari:
--   1) (talaba_id, fan) -> oqituvchi   [talaba bir fanni bir o'qituvchidan]
--   2) oqituvchi -> fan                [har o'qituvchi bitta fan o'qitadi]
-- Nomzod kalitlar: (talaba_id, fan) VA (talaba_id, oqituvchi)
-- Noqalit ustun YO'Q -> 3NF buzilmagan. Lekin "oqituvchi" kalit emas,
-- shuning uchun "oqituvchi -> fan" bog'liqligi BCNF ni buzadi.

DROP TABLE IF EXISTS darslar;

CREATE TABLE darslar (
    talaba_id INTEGER     NOT NULL,
    fan       VARCHAR(40) NOT NULL,
    oqituvchi VARCHAR(40) NOT NULL,
    PRIMARY KEY (talaba_id, fan),
    -- ikkinchi nomzod kalit ham majburlanadi
    UNIQUE (talaba_id, oqituvchi)
);

INSERT INTO darslar VALUES
    (1, 'Fizika', 'Karimov'),
    (2, 'Fizika', 'Karimov'),
    (3, 'Fizika', 'Karimov'),
    (1, 'Kimyo',  'Rasulova'),
    (2, 'Kimyo',  'Rasulova');

-- MUAMMO 1 — takrorlanish: "Karimov Fizika o'qitadi" fakti 3 marta yozilgan
SELECT oqituvchi, fan, COUNT(*) AS necha_marta_takrorlangan
FROM darslar
GROUP BY oqituvchi, fan
ORDER BY oqituvchi;

-- MUAMMO 2 — UPDATE anomaliyasi: Karimov Kimyoga o'tsa, 3 qator o'zgaradi
-- va bittasi unutilsa, Karimov bir vaqtning o'zida ikki fan o'qitib qoladi.

-- MUAMMO 3 — INSERT anomaliyasi: hali talabasi yo'q yangi o'qituvchini
-- bazaga kiritib bo'lmaydi, chunki talaba_id NOT NULL va kalitning qismi.

-- ─────────────────────────────────────────────────────────────────────
-- BCNF YECHIMI: har bir determinantni o'z jadvalining kalitiga aylantiramiz
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS royxat;
DROP TABLE IF EXISTS oqituvchilar;

-- "oqituvchi -> fan" bog'liqligi: endi oqituvchi — BIRLAMCHI KALIT
CREATE TABLE oqituvchilar (
    oqituvchi VARCHAR(40) PRIMARY KEY,
    fan       VARCHAR(40) NOT NULL
);

-- talaba qaysi o'qituvchiga yozilgan
CREATE TABLE royxat (
    talaba_id INTEGER     NOT NULL,
    oqituvchi VARCHAR(40) NOT NULL REFERENCES oqituvchilar(oqituvchi),
    PRIMARY KEY (talaba_id, oqituvchi)
);

INSERT INTO oqituvchilar VALUES
    ('Karimov',  'Fizika'),
    ('Rasulova', 'Kimyo');

INSERT INTO royxat VALUES
    (1, 'Karimov'), (2, 'Karimov'), (3, 'Karimov'),
    (1, 'Rasulova'), (2, 'Rasulova');

-- Endi "Karimov Kimyoga o'tdi" — BITTA qator o'zgaradi:
UPDATE oqituvchilar SET fan = 'Kimyo' WHERE oqituvchi = 'Karimov';
UPDATE oqituvchilar SET fan = 'Fizika' WHERE oqituvchi = 'Karimov';  -- qaytardik

-- Va talabasi yo'q yangi o'qituvchini bemalol qo'shamiz (INSERT anomaliyasi yo'q):
INSERT INTO oqituvchilar VALUES ('Toshmatov', 'Matematika');

-- Eski ko'rinishni JOIN bilan tiklaymiz
SELECT r.talaba_id, o.fan, r.oqituvchi
FROM royxat r
JOIN oqituvchilar o ON o.oqituvchi = r.oqituvchi
ORDER BY r.talaba_id, o.fan;

-- ─────────────────────────────────────────────────────────────────────
-- BCNF NING NARXI: "bitta talaba bitta fanni ikki o'qituvchidan
-- o'qimasin" qoidasi endi struktura bilan AVTOMATIK ta'minlanmaydi.
-- Ikki jadvalga bo'lgach, bu qoida ikkalasining ham ichida qolmadi —
-- kitoblarda buni "dependency preservation yo'qoldi" deyishadi.
--
-- Yechim: fan ustunini royxat jadvaliga ko'chirib, uni kompozit FK
-- bilan oqituvchilar jadvaliga qulflab qo'yamiz — shunda fan qiymati
-- hech qachon o'qituvchining haqiqiy faniga zid bo'lolmaydi.
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE royxat ADD COLUMN fan VARCHAR(40);
UPDATE royxat r SET fan = o.fan FROM oqituvchilar o WHERE o.oqituvchi = r.oqituvchi;
ALTER TABLE royxat ALTER COLUMN fan SET NOT NULL;

ALTER TABLE oqituvchilar ADD CONSTRAINT oqituvchilar_oqituvchi_fan_uq
    UNIQUE (oqituvchi, fan);

ALTER TABLE royxat DROP CONSTRAINT royxat_oqituvchi_fkey;
ALTER TABLE royxat ADD CONSTRAINT royxat_oqituvchi_fan_fkey
    FOREIGN KEY (oqituvchi, fan) REFERENCES oqituvchilar (oqituvchi, fan);

-- Endi bu UNIQUE qoidani majburlaydi va fan ustuni FK bilan himoyalangan:
CREATE UNIQUE INDEX royxat_talaba_fan_uq ON royxat (talaba_id, fan);

-- XULOSA: BCNF har doim ham bepul emas. 3NF — amaliy standart,
-- BCNF esa faqat ustma-ust nomzod kalitlar bo'lganda kerak bo'ladi.
"""

L3_EX = [
    {
        "title": "BCNF ning asosiy qoidasi",
        "description": "Jadval BCNF da bo'lishi uchun har qanday X -> Y funksional bog'liqlikda X qanday bo'lishi shart?",
        "exercise_type": "multiple_choice",
        "options": [
            "X nomzod kalit (candidate key) bo'lishi shart",
            "X noqalit ustun bo'lishi shart",
            "X butun son turida bo'lishi shart",
            "X NULL qabul qilmasligi shart",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "BCNF determinantlar haqida: bog'liqlikning chap tomoni nima bo'lishi kerak?",
        "explanation": "BCNF qoidasi: har bir determinant (bog'liqlikning chap tomoni) nomzod kalit bo'lishi shart. Aks holda jadval BCNF da emas.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Amaliy standart normal forma",
        "description": "Real loyihalarning aksariyati qaysi normal formada to'xtaydi va uni amaliy standart deb hisoblaydi? Bo'sh joyni to'ldiring: ___ (masalan: 1NF).",
        "exercise_type": "fill_in_blank",
        "correct_answers": "3NF",
        "hint": "Tranzitiv bog'liqlikni yo'qotadigan forma.",
        "explanation": "3NF — amaliy standart. BCNF faqat bir nechta ustma-ust nomzod kalit bo'lgan maxsus holatlarda kerak bo'ladi, 4NF va 5NF esa real loyihalarda deyarli qo'llanilmaydi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Buyurtmadagi narx takrorlanishmi?",
        "description": "buyurtma_elementlari jadvalida narx_birlik ustuni saqlanadi, garchi narx mahsulotlar jadvalida ham bor. Nima uchun bu denormalizatsiya emas, balki to'g'ri dizayn? Qisqacha (1-2 jumla) tushuntiring.",
        "exercise_type": "text_input",
        "expected_answer": "Chunki narx_birlik — bu boshqa fakt: sotuv paytidagi tarixiy narx. Mahsulot narxi keyin o'zgarsa ham, eski buyurtmadagi summa o'zgarmasligi kerak, shuning uchun uni chek bilan birga saqlash zarur.",
        "hint": "Mahsulot narxi ertaga oshsa, kechagi chekdagi summa o'zgarishi kerakmi?",
        "difficulty_level": "Hard",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L4 — Munosabatlar: 1:1 va 1:N
# ═════════════════════════════════════════════════════════════════════════════
L4_TEXT = """\
<h3>Munosabat (relationship) nima?</h3>
<p>Normalizatsiya jadvallarni <em>ajratdi</em>. Endi ularni qayta <em>bog'lash</em> kerak. Bog'lanish vositasi bitta &mdash; <strong>FOREIGN KEY</strong>. Butun savol shundaki: FK qaysi jadvalga qo'yiladi va unda <code>UNIQUE</code> bo'ladimi yoki yo'qmi. Aynan shu ikki qaror munosabat turini belgilaydi.</p>

<h3>1:N (bir-ko'p) &mdash; eng ko'p uchraydigan tur</h3>
<p>Bitta muallif ko'p kitob yozadi, lekin har bir kitobning bitta muallifi bor. Bitta mijozning ko'p buyurtmasi bor, lekin har buyurtma bitta mijozniki.</p>
<p><strong>Qoida:</strong> FK har doim <em>"ko'p" tomonda</em> turadi. Ya'ni <code>kitoblar</code> jadvalida <code>muallif_id</code> bo'ladi, <code>mualliflar</code> jadvalida esa <code>kitob_id</code> emas. Sababi oddiy: bitta katakka bir nechta kitob ID sini sig'dirib bo'lmaydi &mdash; bu bizni to'g'ridan-to'g'ri 1NF buzilishiga olib borardi.</p>

<h3>1:1 (bir-bir) &mdash; kamroq, lekin kerak</h3>
<p>1:1 &mdash; bu texnik jihatdan <code>UNIQUE</code> qo'shilgan 1:N. FK ustuniga <code>UNIQUE</code> qo'ysangiz, "ko'p" avtomatik "bir" ga aylanadi.</p>
<p>Mantiqiy savol tug'iladi: agar munosabat 1:1 bo'lsa, nega ikkala jadvalni birlashtirib yubormaymiz? Asosli sabablar bor:</p>
<ul>
<li><strong>Ixtiyoriy ma'lumot.</strong> Har bir foydalanuvchida profil (bio, avatar, tug'ilgan sana) bo'lishi shart emas. Ularni <code>users</code> ga qo'shsak, ko'p qatorda <code>NULL</code> to'planadi.</li>
<li><strong>Turli xavfsizlik darajasi.</strong> Pasport ma'lumoti yoki bank kartasi &mdash; alohida jadvalda, alohida ruxsatlar bilan bo'lgani xavfsizroq.</li>
<li><strong>Kam o'qiladigan og'ir ustunlar.</strong> Har so'rovda kerak bo'lmaydigan katta <code>TEXT</code> yoki <code>BYTEA</code> ustunlarni ajratsak, asosiy jadval qatori ixchamroq bo'ladi va tezroq o'qiladi.</li>
</ul>

<h3>Solishtirish jadvali</h3>
<table>
<tr><th>Xususiyat</th><th>1:1</th><th>1:N</th></tr>
<tr><td>Misol</td><td>users &harr; user_profiles</td><td>mualliflar &rarr; kitoblar</td></tr>
<tr><td>FK qayerda</td><td>bog'liq (ixtiyoriy) tomonda</td><td>"ko'p" tomonda</td></tr>
<tr><td>FK ustunida UNIQUE</td><td>Ha (yoki FK = PK)</td><td>Yo'q</td></tr>
<tr><td>Qo'shimcha jadval kerakmi</td><td>Yo'q</td><td>Yo'q</td></tr>
<tr><td>Odatiy ON DELETE</td><td>CASCADE</td><td>RESTRICT yoki SET NULL</td></tr>
</table>

<pre class="mermaid">
flowchart LR
  U["users
id PK"] ---|"1 : 1"| P["user_profiles
user_id PK va FK
(UNIQUE avtomatik)"]
  A["mualliflar
id PK"] ---|"1 : N"| B["kitoblar
id PK
muallif_id FK (UNIQUE emas)"]
</pre>

<h3>1:1 ni amalga oshirishning ikki usuli</h3>
<ul>
<li><strong>Umumiy birlamchi kalit (shared PK).</strong> <code>user_profiles.user_id</code> bir vaqtning o'zida ham PRIMARY KEY, ham FOREIGN KEY. Eng toza usul: UNIQUE avtomatik ta'minlanadi, ortiqcha <code>id</code> ustuni yo'q.</li>
<li><strong>Alohida id + UNIQUE FK.</strong> <code>user_profiles(id PK, user_id FK UNIQUE)</code>. ORM lar (Django, SQLAlchemy) ko'pincha shuni afzal ko'radi, chunki ularning ba'zi qismlari har jadvalda alohida <code>id</code> bo'lishini kutadi.</li>
</ul>
<p><strong>Eng ko'p uchraydigan xato:</strong> 1:1 munosabatda FK ustuniga <code>UNIQUE</code> qo'yishni unutish. Bunda baza jimgina bitta foydalanuvchiga ikkita profil yozilishiga ruxsat beradi &mdash; va bu xato faqat oylar o'tib, ilova <code>get_profile()</code> dan ikkita qator qaytganda ma'lum bo'ladi.</p>
"""

L4_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- 1:1 va 1:N munosabatlar — FK qayerda turishi va UNIQUE ning roli
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS kitoblar;
DROP TABLE IF EXISTS mualliflar;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;

-- ─────────────────────────────────────────────────────────────────────
-- 1:1 — foydalanuvchi va uning profili
-- Usul: umumiy birlamchi kalit (shared primary key).
-- user_id bir vaqtda PK ham, FK ham -> UNIQUE avtomatik kafolatlanadi.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE users (
    id         SERIAL       PRIMARY KEY,
    email      VARCHAR(120) NOT NULL UNIQUE,
    parol_hash VARCHAR(255) NOT NULL,
    yaratilgan TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
    -- PK va FK bitta ustunda: bitta userda ko'pi bilan bitta profil
    user_id       INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tolik_ism     VARCHAR(80),
    bio           TEXT,
    avatar_url    VARCHAR(255),
    tugilgan_sana DATE
);

INSERT INTO users (email, parol_hash) VALUES
    ('aziz@mail.uz',  'hash_1'),
    ('dilya@mail.uz', 'hash_2'),
    ('sardor@mail.uz','hash_3');

-- Uchinchi foydalanuvchi hali profil to'ldirmagan — bu normal holat.
-- Aynan shuning uchun profil alohida jadvalda: users da NULL to'planmaydi.
INSERT INTO user_profiles (user_id, tolik_ism, bio) VALUES
    (1, 'Aziz Karimov',     'Backend dasturchi'),
    (2, 'Dilnoza Rasulova', 'Data analitik');

-- Baza ikkinchi profilni YOZDIRMAYDI — PK buni bloklaydi:
-- INSERT INTO user_profiles (user_id, tolik_ism) VALUES (1, 'Ikkinchi profil');
-- ERROR:  duplicate key value violates unique constraint "user_profiles_pkey"

-- Profili bo'lmaganlarni ham ko'rish uchun LEFT JOIN kerak:
SELECT u.id, u.email, p.tolik_ism, p.bio
FROM users u
LEFT JOIN user_profiles p ON p.user_id = u.id
ORDER BY u.id;

-- ─────────────────────────────────────────────────────────────────────
-- 1:N — bitta muallif, ko'p kitob. FK "ko'p" tomonda: kitoblar.muallif_id
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE mualliflar (
    id           SERIAL      PRIMARY KEY,
    ism          VARCHAR(80) NOT NULL,
    tugilgan_yil INTEGER     CHECK (tugilgan_yil BETWEEN 1000 AND 2100)
);

CREATE TABLE kitoblar (
    id          SERIAL      PRIMARY KEY,
    -- UNIQUE YO'Q — shuning uchun bitta muallifda ko'p kitob bo'la oladi
    muallif_id  INTEGER     NOT NULL REFERENCES mualliflar(id) ON DELETE RESTRICT,
    sarlavha    VARCHAR(150) NOT NULL,
    nashr_yili  INTEGER     CHECK (nashr_yili BETWEEN 1000 AND 2100),
    isbn        CHAR(13)    UNIQUE
);

INSERT INTO mualliflar (ism, tugilgan_yil) VALUES
    ('Abdulla Qodiriy', 1894),
    ('Cho''lpon',       1897),
    ('Robert Martin',   1952);

INSERT INTO kitoblar (muallif_id, sarlavha, nashr_yili, isbn) VALUES
    (1, 'O''tkan kunlar',      1926, '9789943010101'),
    (1, 'Mehrobdan chayon',    1929, '9789943010102'),
    (2, 'Kecha va kunduz',     1936, '9789943010103'),
    (3, 'Clean Code',          2008, '9780132350884'),
    (3, 'Clean Architecture',  2017, '9780134494166');

-- 1:N ni tekshiramiz — har muallifda nechta kitob bor
SELECT a.ism, COUNT(k.id) AS kitoblar_soni
FROM mualliflar a
LEFT JOIN kitoblar k ON k.muallif_id = a.id
GROUP BY a.id, a.ism
ORDER BY kitoblar_soni DESC;

-- FK himoyasi ishlayotganini ko'ramiz: mavjud bo'lmagan muallif
-- INSERT INTO kitoblar (muallif_id, sarlavha) VALUES (999, 'Sehrli kitob');
-- ERROR:  insert or update on table "kitoblar" violates foreign key constraint

-- ON DELETE RESTRICT: kitoblari bor muallifni o'chirib bo'lmaydi
-- DELETE FROM mualliflar WHERE id = 1;
-- ERROR:  update or delete on table "mualliflar" violates foreign key constraint

-- ON DELETE CASCADE ishlayotganini 1:1 tomonda tekshiramiz:
DELETE FROM users WHERE id = 2;
SELECT COUNT(*) AS qolgan_profillar FROM user_profiles;  -- 1 ta qoldi

-- ─────────────────────────────────────────────────────────────────────
-- MUHIM: 1:1 ni UNIQUE siz qursangiz, u jimgina 1:N bo'lib qoladi.
-- Quyidagi ikkita ustun ta'rifi orasidagi farq — butun munosabat turi:
--   muallif_id INTEGER REFERENCES mualliflar(id)          -> 1:N
--   muallif_id INTEGER UNIQUE REFERENCES mualliflar(id)   -> 1:1
-- ─────────────────────────────────────────────────────────────────────
"""

L4_EX = [
    {
        "title": "FK qaysi jadvalda turadi?",
        "description": "1:N munosabatda (bitta muallif — ko'p kitob) FOREIGN KEY ustuni qaysi jadvalga qo'yiladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "kitoblar jadvaliga (muallif_id)",
            "mualliflar jadvaliga (kitob_id)",
            "Ikkalasiga ham",
            "Alohida uchinchi jadvalga",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bitta katakka bir nechta ID sig'maydi — bu 1NF ni buzardi.",
        "explanation": "FK har doim \"ko'p\" tomonda turadi, ya'ni kitoblar.muallif_id. Aks holda bitta katakka bir nechta kitob ID sini yozish kerak bo'lardi va bu 1NF ni buzardi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1:N ni 1:1 ga aylantirish",
        "description": "1:N munosabatni 1:1 ga aylantirish uchun FK ustuniga qanday cheklov qo'shish kerak? Bo'sh joyni to'ldiring (bitta so'z, katta harflar bilan): ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "UNIQUE",
        "hint": "Bu cheklov ustunda bir xil qiymat ikki marta uchramasligini ta'minlaydi.",
        "explanation": "FK ustuniga UNIQUE qo'yilsa, bitta \"ota\" qatorga ko'pi bilan bitta \"bola\" qator to'g'ri kela oladi — ya'ni 1:N avtomatik 1:1 ga aylanadi. Muqobil variant: FK ustunini bir vaqtning o'zida PRIMARY KEY qilish.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1:1 ni alohida jadvalga ajratish sabablari",
        "description": "Quyidagilardan qaysilari 1:1 munosabatni alohida jadvalga ajratish uchun asosli sabab hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Ma'lumot ixtiyoriy — ko'p qatorda NULL to'planib qolmasligi uchun",
            "Ma'lumot maxfiy va unga alohida ruxsat kerak",
            "Har so'rovda kerak bo'lmaydigan katta TEXT/BYTEA ustunlarni ajratish",
            "Jadvaldagi ustunlar soni 5 tadan oshib ketgani uchun",
        ],
        "correct_answers": "A,B,C",
        "is_multiple_select": True,
        "hint": "Ustunlar sonining o'zi hech qachon jadvalni bo'lish sababi emas.",
        "explanation": "1:1 ni ajratishning uchta asosli sababi: ixtiyoriy ma'lumot (NULL to'planishi), turli xavfsizlik darajasi va kam o'qiladigan og'ir ustunlar. Ustunlar sonining o'zi — sabab emas, chunki 3NF da bo'lgan keng jadval ham mutlaqo normal.",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L5 — Munosabatlar: N:N va junction jadvallar
# ═════════════════════════════════════════════════════════════════════════════
L5_TEXT = """\
<h3>N:N &mdash; nima uchun uni to'g'ridan-to'g'ri qurib bo'lmaydi</h3>
<p>Bitta talaba ko'p kursga yozila oladi, va bitta kursda ko'p talaba bor. Bu &mdash; <strong>ko'p-ko'p</strong> (N:N) munosabat.</p>
<p>Uni ikkita jadval bilan qurishga urinib ko'ring va darhol devorga urilasiz:</p>
<ul>
<li><code>talabalar.kurs_id</code> qo'ysak &mdash; talaba faqat bitta kursga yozila oladi.</li>
<li><code>kurslar.talaba_id</code> qo'ysak &mdash; kursda faqat bitta talaba bo'ladi.</li>
<li><code>talabalar.kurs_idlar = '1,3,7'</code> yozsak &mdash; bu 1NF ning ochiq buzilishi va biz 1-darsda ko'rgan barcha muammolar qaytadi.</li>
</ul>
<p>Yagona to'g'ri yechim &mdash; <strong>junction jadval</strong> (bog'lovchi, bridge yoki associative table deb ham ataladi). U ikkita 1:N munosabatni birlashtiradi va shu tariqa N:N ni hosil qiladi.</p>

<h3>Junction jadvalning tuzilishi</h3>
<p>Eng kamida u ikkita FK dan iborat bo'ladi va ular birgalikda kompozit birlamchi kalit hosil qiladi:</p>
<ul>
<li><code>talaba_id</code> &rarr; <code>talabalar(id)</code></li>
<li><code>kurs_id</code> &rarr; <code>kurslar(id)</code></li>
<li><code>PRIMARY KEY (talaba_id, kurs_id)</code> &mdash; bitta talaba bitta kursga ikki marta yozila olmaydi.</li>
</ul>

<h3>Junction jadval &mdash; bu shunchaki "texnik" jadval emas</h3>
<p>Bu darsdagi eng muhim fikr. Boshlovchilar junction jadvalni "shunchaki ikkita ID ni bog'lash uchun" deb o'ylashadi. Amalda esa u deyarli har doim <em>o'z atributlariga ega mustaqil mohiyat</em> bo'lib chiqadi:</p>
<table>
<tr><th>N:N munosabat</th><th>Junction jadval</th><th>Uning o'z atributlari</th></tr>
<tr><td>talabalar &harr; kurslar</td><td>royxatlar (enrollments)</td><td>yozilgan_sana, baho, holat</td></tr>
<tr><td>buyurtmalar &harr; mahsulotlar</td><td>buyurtma_elementlari</td><td>miqdor, narx_birlik, chegirma</td></tr>
<tr><td>foydalanuvchilar &harr; rollar</td><td>user_roles</td><td>berilgan_sana, kim_bergan</td></tr>
<tr><td>postlar &harr; teglar</td><td>post_tags</td><td>(ko'pincha bo'sh &mdash; sof bog'lanish)</td></tr>
</table>
<p>Shuning uchun junction jadvalga o'ylab nom bering. <code>talaba_kurs</code> emas &mdash; <code>royxatlar</code>. <code>buyurtma_mahsulot</code> emas &mdash; <code>buyurtma_elementlari</code>. Nom mohiyatni ochsa, keyinchalik unga ustun qo'shish tabiiy tuyuladi.</p>

<pre class="mermaid">
flowchart LR
  T["talabalar
id PK"] -->|"1 : N"| R["royxatlar
talaba_id FK
kurs_id FK
PK (talaba_id, kurs_id)
+ yozilgan_sana, baho"]
  K["kurslar
id PK"] -->|"1 : N"| R
</pre>

<h3>Kompozit kalit yoki surrogate id?</h3>
<p>Junction jadvalga <code>id SERIAL PRIMARY KEY</code> qo'shib, <code>(talaba_id, kurs_id)</code> ga esa <code>UNIQUE</code> berish ham mumkin. Ikkalasi ham to'g'ri, tanlov kontekstga bog'liq:</p>
<ul>
<li><strong>Kompozit kalit</strong> &mdash; sof SQL loyihalarida afzal: ortiqcha ustun yo'q va kalitning o'zi biznes qoidasini ifodalaydi.</li>
<li><strong>Surrogate id + UNIQUE</strong> &mdash; agar bu qatorlarga boshqa jadval murojaat qilsa (masalan, <code>baholar.royxat_id</code>) yoki ORM talab qilsa. Muhim: bunda ham <code>UNIQUE (talaba_id, kurs_id)</code> ni qo'shishni <em>unutmang</em> &mdash; aks holda dublikat yozuvlar paydo bo'ladi.</li>
</ul>
"""

L5_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- N:N munosabat va junction jadval — talabalar / kurslar / royxatlar
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS royxatlar;
DROP TABLE IF EXISTS kurslar;
DROP TABLE IF EXISTS talabalar;

CREATE TABLE talabalar (
    id     SERIAL       PRIMARY KEY,
    ism    VARCHAR(80)  NOT NULL,
    email  VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE kurslar (
    id       SERIAL       PRIMARY KEY,
    nomi     VARCHAR(120) NOT NULL UNIQUE,
    kreditlar INTEGER     NOT NULL CHECK (kreditlar BETWEEN 1 AND 10)
);

-- ─────────────────────────────────────────────────────────────────────
-- JUNCTION JADVAL. Diqqat: bu shunchaki "bog'lovchi" emas —
-- unda yozilish sanasi, baho va holat kabi O'Z atributlari bor.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE royxatlar (
    talaba_id      INTEGER NOT NULL REFERENCES talabalar(id) ON DELETE CASCADE,
    kurs_id        INTEGER NOT NULL REFERENCES kurslar(id)   ON DELETE RESTRICT,
    yozilgan_sana  DATE    NOT NULL DEFAULT CURRENT_DATE,
    baho           INTEGER CHECK (baho BETWEEN 0 AND 100),
    holat          VARCHAR(16) NOT NULL DEFAULT 'faol'
                   CHECK (holat IN ('faol', 'tugatgan', 'tashlab_ketgan')),
    -- Kompozit birlamchi kalit: bir talaba bir kursga BIR marta yoziladi
    PRIMARY KEY (talaba_id, kurs_id)
);

INSERT INTO talabalar (ism, email) VALUES
    ('Aziz Karimov',     'aziz@edu.uz'),
    ('Dilnoza Rasulova', 'dilya@edu.uz'),
    ('Sardor Tursunov',  'sardor@edu.uz');

INSERT INTO kurslar (nomi, kreditlar) VALUES
    ('SQL Asoslari',        4),
    ('Python Asoslari',     5),
    ('Ma''lumotlar Bazasi Dizayni', 4);

INSERT INTO royxatlar (talaba_id, kurs_id, baho, holat) VALUES
    (1, 1, 92, 'tugatgan'),
    (1, 2, 85, 'tugatgan'),
    (1, 3, NULL, 'faol'),
    (2, 1, 78, 'tugatgan'),
    (2, 3, NULL, 'faol'),
    (3, 2, NULL, 'tashlab_ketgan');

-- Kompozit kalit dublikatni bloklaydi:
-- INSERT INTO royxatlar (talaba_id, kurs_id) VALUES (1, 1);
-- ERROR:  duplicate key value violates unique constraint "royxatlar_pkey"

-- ─────────────────────────────────────────────────────────────────────
-- N:N ni ikki tomonlama o'qish
-- ─────────────────────────────────────────────────────────────────────

-- 1) Bir talaba qaysi kurslarda?
SELECT t.ism, k.nomi AS kurs, r.holat, r.baho
FROM royxatlar r
JOIN talabalar t ON t.id = r.talaba_id
JOIN kurslar   k ON k.id = r.kurs_id
WHERE t.email = 'aziz@edu.uz'
ORDER BY k.nomi;

-- 2) Bir kursda qaysi talabalar?
SELECT k.nomi AS kurs, t.ism, r.yozilgan_sana
FROM royxatlar r
JOIN kurslar   k ON k.id = r.kurs_id
JOIN talabalar t ON t.id = r.talaba_id
WHERE k.nomi = 'SQL Asoslari'
ORDER BY t.ism;

-- 3) Junction jadvaldagi atributlar tufayli mumkin bo'lgan hisobot:
--    har kursning o'rtacha bahosi va tugatganlar ulushi
SELECT k.nomi                                        AS kurs,
       COUNT(*)                                      AS jami_yozilgan,
       COUNT(*) FILTER (WHERE r.holat = 'tugatgan')  AS tugatgan,
       ROUND(AVG(r.baho), 1)                         AS ortacha_baho
FROM kurslar k
JOIN royxatlar r ON r.kurs_id = k.id
GROUP BY k.id, k.nomi
ORDER BY kurs;

-- 4) Hech kim yozilmagan kurslar (LEFT JOIN + IS NULL)
SELECT k.nomi
FROM kurslar k
LEFT JOIN royxatlar r ON r.kurs_id = k.id
WHERE r.kurs_id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- MUQOBIL VARIANT: surrogate id + UNIQUE.
-- Boshqa jadval ayni royxat qatoriga murojaat qilishi kerak bo'lganda
-- (masalan, har topshiriq bahosi alohida saqlansa) shu qulayroq.
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS royxatlar_v2;

CREATE TABLE royxatlar_v2 (
    id            SERIAL  PRIMARY KEY,
    talaba_id     INTEGER NOT NULL REFERENCES talabalar(id) ON DELETE CASCADE,
    kurs_id       INTEGER NOT NULL REFERENCES kurslar(id)   ON DELETE RESTRICT,
    yozilgan_sana DATE    NOT NULL DEFAULT CURRENT_DATE,
    -- UNIQUE ni UNUTMANG — busiz dublikatlar bemalol kiradi!
    UNIQUE (talaba_id, kurs_id)
);

INSERT INTO royxatlar_v2 (talaba_id, kurs_id) VALUES (1, 1), (2, 1);

-- FK ustunlariga indeks: PK birinchi ustunni qoplaydi, lekin
-- "bu kursda kim bor?" so'rovi uchun kurs_id ga alohida indeks kerak.
CREATE INDEX royxatlar_kurs_id_idx ON royxatlar (kurs_id);
"""

L5_EX = [
    {
        "title": "N:N ni qanday amalga oshiriladi?",
        "description": "Talabalar va kurslar orasidagi ko'p-ko'p (N:N) munosabat PostgreSQL da qanday amalga oshiriladi?",
        "exercise_type": "multiple_choice",
        "options": [
            "talabalar jadvaliga kurs_idlar ustunini qo'shib, ID larni vergul bilan yozib",
            "Ikkita FK dan iborat alohida junction (bog'lovchi) jadval yaratib",
            "kurslar jadvaliga talaba_id ustunini qo'shib",
            "Ikkala jadvalga ham bir-biriga FK qo'yib",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "N:N — bu aslida ikkita 1:N munosabatning birlashmasi.",
        "explanation": "N:N faqat junction jadval orqali quriladi: u ikkita FK saqlaydi va shu tariqa ikkita 1:N munosabatni birlashtirib N:N hosil qiladi. Qolgan variantlar yo 1NF ni buzadi, yo munosabatni 1:N ga cheklab qo'yadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Junction jadvalning kaliti",
        "description": "royxatlar(talaba_id, kurs_id) junction jadvalida bitta talaba bitta kursga ikki marta yozilmasligi uchun ikkala ustundan qanday kalit tuziladi? Bo'sh joyni to'ldiring: ___ birlamchi kalit (bir so'z).",
        "exercise_type": "fill_in_blank",
        "correct_answers": "kompozit",
        "hint": "Bir nechta ustundan tashkil topgan kalit shunday ataladi.",
        "explanation": "PRIMARY KEY (talaba_id, kurs_id) — kompozit (composite) birlamchi kalit. U dublikat yozuvlarni baza darajasida bloklaydi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Junction jadvalga surrogate id qo'shilganda",
        "description": "Junction jadvalga id SERIAL PRIMARY KEY qo'shildi va ikkita FK ustuni oddiy ustun bo'lib qoldi. Dublikat yozuvlar paydo bo'lmasligi uchun yana qanday cheklov qo'shish shart? SQL ko'rinishida yozing (masalan: UNIQUE (a, b)).",
        "exercise_type": "text_input",
        "expected_answer": "UNIQUE (talaba_id, kurs_id)",
        "hint": "Kompozit PK olib tashlangach, uning kafolatini boshqa cheklov bilan qaytarish kerak.",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# R1 — Kutubxona tizimi sxemasini loyihalash (takrorlash)
# ═════════════════════════════════════════════════════════════════════════════
R1_TEXT = """\
<h2>R1 &mdash; Modul 1 takrorlash: kutubxona tizimi sxemasi</h2>
<p>Birinchi 5 ta darsda o'rgangan hamma narsani &mdash; 1NF, 2NF, 3NF, 1:1, 1:N va N:N &mdash; bitta real sxemada birlashtiramiz.</p>
<p>Tasavvur qiling: shahar kutubxonasi sizdan tizim so'radi. Ular hozir hamma narsani Excel jadvalida yuritadi va u quyidagi ko'rinishda:</p>

<table>
<tr><th>kitob</th><th>muallif</th><th>muallif_tugilgan</th><th>oquvchi</th><th>oquvchi_tel</th><th>olingan</th><th>qaytarilgan</th></tr>
<tr><td>O'tkan kunlar</td><td>Abdulla Qodiriy</td><td>1894</td><td>Aziz K</td><td>+998901112233</td><td>2026-01-10</td><td>2026-01-24</td></tr>
<tr><td>O'tkan kunlar</td><td>Abdulla Qodiriy</td><td>1894</td><td>Dilnoza R</td><td>+998907778899</td><td>2026-02-01</td><td></td></tr>
<tr><td>Clean Code</td><td>Robert Martin</td><td>1952</td><td>Aziz K</td><td>+998901112233</td><td>2026-01-15</td><td>2026-02-15</td></tr>
</table>

<h3>Bu jadvaldagi muammolarni sanang</h3>
<ul>
<li>Muallifning tug'ilgan yili har kitob-o'quvchi juftligida takrorlanmoqda &mdash; <strong>tranzitiv bog'liqlik</strong> (3NF buzilgan).</li>
<li>O'quvchining telefoni har qarzda takrorlanmoqda &mdash; UPDATE anomaliyasi.</li>
<li>Hali birorta kitob olmagan o'quvchini yoki hech kim olmagan kitobni saqlab bo'lmaydi &mdash; INSERT anomaliyasi.</li>
<li>Bir kitobning bir nechta nusxasi bo'lsa, ularni farqlash imkoni yo'q.</li>
<li>Bir kitobda bir nechta muallif bo'lsa &mdash; bu sxema umuman ishlamaydi.</li>
</ul>

<h3>Sizdan kutilayotgan sxema</h3>
<p>Kamida quyidagi mohiyatlar bo'lishi kerak. Har biri uchun munosabat turini o'zingiz aniqlang:</p>
<table>
<tr><th>Jadval</th><th>Maqsad</th><th>Munosabat</th></tr>
<tr><td><code>mualliflar</code></td><td>Muallif haqidagi fakt bir joyda</td><td>kitoblar bilan N:N</td></tr>
<tr><td><code>kitoblar</code></td><td>Asar (nom, ISBN, nashr yili)</td><td>&mdash;</td></tr>
<tr><td><code>kitob_mualliflari</code></td><td>Junction: bir kitobda bir nechta muallif</td><td>N:N ni ochadi</td></tr>
<tr><td><code>nusxalar</code></td><td>Javondagi jismoniy nusxa (inventar raqami)</td><td>kitoblar bilan 1:N</td></tr>
<tr><td><code>azolar</code></td><td>Kutubxona a'zosi</td><td>&mdash;</td></tr>
<tr><td><code>azo_profillari</code></td><td>Manzil, pasport &mdash; ixtiyoriy maxfiy ma'lumot</td><td>azolar bilan 1:1</td></tr>
<tr><td><code>qarzlar</code></td><td>Kim, qaysi nusxani, qachon oldi/qaytardi</td><td>nusxalar va azolar bilan N:N</td></tr>
</table>

<h3>Diqqat qaratiladigan qiyin qaror</h3>
<p>Nima uchun <code>kitoblar</code> va <code>nusxalar</code> alohida? Chunki "O'tkan kunlar" &mdash; bu <em>asar</em>, javondagi 5 ta jild esa <em>5 ta alohida jismoniy obyekt</em>. Qarz bitta jismoniy nusxaga beriladi, asarga emas. Bu farqni ko'rmaslik &mdash; kutubxona sxemasidagi eng ko'p uchraydigan xato: usiz "bu kitobning nechta nusxasi bo'sh?" degan savolga javob bera olmaysiz.</p>

<pre class="mermaid">
flowchart TB
  M["mualliflar"] --> KM["kitob_mualliflari
(junction, N:N)"]
  K["kitoblar"] --> KM
  K -->|"1 : N"| N["nusxalar
(inventar_raqami)"]
  A["azolar"] -->|"1 : 1"| AP["azo_profillari"]
  N --> Q["qarzlar
(olingan_sana, qaytarilgan_sana)"]
  A --> Q
</pre>

<h3>Tekshirish savollari</h3>
<ol>
<li>Har bir jadvalning birlamchi kaliti nima? Qaysilari kompozit?</li>
<li><code>qarzlar</code> jadvalida <code>PRIMARY KEY (nusxa_id, azo_id)</code> qo'yish to'g'ri bo'ladimi? (Ipucha: bir a'zo bir kitobni ikki marta olishi mumkinmi?)</li>
<li>A'zo o'chirilsa, uning qarzlari bilan nima bo'lishi kerak &mdash; <code>CASCADE</code> mi, <code>RESTRICT</code> mi?</li>
<li>"Hozir kimdadir bo'lgan nusxalar" so'rovini qanday yozasiz?</li>
</ol>
"""

R1_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- R1 — Kutubxona sxemasi: START KIT
-- Quyida sxemaning bir qismi berilgan. Qolganini o'zingiz yozasiz.
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS qarzlar;
DROP TABLE IF EXISTS nusxalar;
DROP TABLE IF EXISTS kitob_mualliflari;
DROP TABLE IF EXISTS kitoblar;
DROP TABLE IF EXISTS mualliflar;
DROP TABLE IF EXISTS azo_profillari;
DROP TABLE IF EXISTS azolar;

-- ── Mualliflar (3NF: muallif fakti bitta joyda) ───────────────────────
CREATE TABLE mualliflar (
    id           SERIAL      PRIMARY KEY,
    ism          VARCHAR(80) NOT NULL,
    tugilgan_yil INTEGER     CHECK (tugilgan_yil BETWEEN 1000 AND 2100)
);

-- ── Kitoblar = ASAR (jismoniy nusxa emas!) ────────────────────────────
CREATE TABLE kitoblar (
    id         SERIAL       PRIMARY KEY,
    sarlavha   VARCHAR(200) NOT NULL,
    isbn       CHAR(13)     UNIQUE,
    nashr_yili INTEGER      CHECK (nashr_yili BETWEEN 1000 AND 2100)
);

-- ── N:N junction: bir kitobda bir nechta muallif bo'lishi mumkin ──────
CREATE TABLE kitob_mualliflari (
    kitob_id   INTEGER NOT NULL REFERENCES kitoblar(id)   ON DELETE CASCADE,
    muallif_id INTEGER NOT NULL REFERENCES mualliflar(id) ON DELETE RESTRICT,
    -- mualliflar tartibi muhim: birinchi muallif muqovada birinchi turadi
    tartib     SMALLINT NOT NULL DEFAULT 1 CHECK (tartib > 0),
    PRIMARY KEY (kitob_id, muallif_id)
);

-- ── 1:N — asarning javondagi jismoniy nusxalari ───────────────────────
CREATE TABLE nusxalar (
    id              SERIAL      PRIMARY KEY,
    kitob_id        INTEGER     NOT NULL REFERENCES kitoblar(id) ON DELETE RESTRICT,
    inventar_raqami VARCHAR(20) NOT NULL UNIQUE,
    holati          VARCHAR(12) NOT NULL DEFAULT 'yaxshi'
                    CHECK (holati IN ('yaxshi', 'eskirgan', 'yaroqsiz'))
);

-- ── A'zolar ───────────────────────────────────────────────────────────
CREATE TABLE azolar (
    id            SERIAL       PRIMARY KEY,
    ism           VARCHAR(80)  NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    azolik_sanasi DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- ── 1:1 — ixtiyoriy va maxfiyroq ma'lumot alohida jadvalda ────────────
CREATE TABLE azo_profillari (
    azo_id         INTEGER PRIMARY KEY REFERENCES azolar(id) ON DELETE CASCADE,
    telefon        VARCHAR(20),
    manzil         TEXT,
    pasport_raqami VARCHAR(20) UNIQUE
);

-- ─────────────────────────────────────────────────────────────────────
-- TOPSHIRIQ: qarzlar jadvalini O'ZINGIZ yozing.
--
-- O'ylab ko'ring:
--   * PRIMARY KEY (nusxa_id, azo_id) TO'G'RI EMAS — nega?
--     Chunki bir a'zo bir kitobni yil davomida bir necha marta olishi
--     mumkin. Kalitga olingan_sana ni qo'shish yoki surrogate id
--     ishlatish kerak.
--   * qaytarilgan_sana NULL bo'lishi kerak — "hali qaytarilmagan".
--   * Qaytarish sanasi olish sanasidan oldin bo'lolmaydi -> CHECK.
--   * A'zo o'chirilsa qarz tarixi nima bo'ladi? CASCADE mi, RESTRICT mi?
--
-- Namuna yechim (o'zingiznikini yozib bo'lgach solishtiring):
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE qarzlar (
    id                SERIAL  PRIMARY KEY,
    nusxa_id          INTEGER NOT NULL REFERENCES nusxalar(id) ON DELETE RESTRICT,
    azo_id            INTEGER NOT NULL REFERENCES azolar(id)   ON DELETE RESTRICT,
    olingan_sana      DATE    NOT NULL DEFAULT CURRENT_DATE,
    qaytarish_muddati DATE    NOT NULL,
    qaytarilgan_sana  DATE,
    CHECK (qaytarish_muddati > olingan_sana),
    CHECK (qaytarilgan_sana IS NULL OR qaytarilgan_sana >= olingan_sana)
);

-- Bitta jismoniy nusxa bir vaqtda faqat BITTA odamda bo'lishi kerak.
-- Buni qisman (partial) unique indeks bilan majburlaymiz:
CREATE UNIQUE INDEX qarzlar_faol_nusxa_uq
    ON qarzlar (nusxa_id)
    WHERE qaytarilgan_sana IS NULL;

-- ── Test ma'lumot ─────────────────────────────────────────────────────
INSERT INTO mualliflar (ism, tugilgan_yil) VALUES
    ('Abdulla Qodiriy', 1894),
    ('Robert Martin',   1952),
    ('James Grimmelmann', 1976);

INSERT INTO kitoblar (sarlavha, isbn, nashr_yili) VALUES
    ('O''tkan kunlar', '9789943010101', 1926),
    ('Clean Code',     '9780132350884', 2008);

INSERT INTO kitob_mualliflari (kitob_id, muallif_id, tartib) VALUES
    (1, 1, 1),
    (2, 2, 1),
    (2, 3, 2);   -- ikkinchi muallif — N:N tufayli mumkin

INSERT INTO nusxalar (kitob_id, inventar_raqami) VALUES
    (1, 'INV-0001'), (1, 'INV-0002'), (1, 'INV-0003'),
    (2, 'INV-0100'), (2, 'INV-0101');

INSERT INTO azolar (ism, email) VALUES
    ('Aziz Karimov',     'aziz@lib.uz'),
    ('Dilnoza Rasulova', 'dilya@lib.uz');

INSERT INTO azo_profillari (azo_id, telefon) VALUES
    (1, '+998901112233');

INSERT INTO qarzlar (nusxa_id, azo_id, olingan_sana, qaytarish_muddati, qaytarilgan_sana) VALUES
    (1, 1, DATE '2026-01-10', DATE '2026-01-24', DATE '2026-01-24'),
    (2, 2, DATE '2026-02-01', DATE '2026-02-15', NULL),
    (4, 1, DATE '2026-01-15', DATE '2026-02-15', NULL);

-- Bir nusxa ikki odamda bo'lolmaydi — qisman indeks bloklaydi:
-- INSERT INTO qarzlar (nusxa_id, azo_id, qaytarish_muddati)
-- VALUES (2, 1, CURRENT_DATE + 14);
-- ERROR:  duplicate key value violates unique constraint "qarzlar_faol_nusxa_uq"

-- ── Sxema ishlayotganini tasdiqlovchi hisobotlar ──────────────────────

-- 1) Hozir kimdadir bo'lgan nusxalar
SELECT k.sarlavha, n.inventar_raqami, a.ism, q.qaytarish_muddati
FROM qarzlar q
JOIN nusxalar n ON n.id = q.nusxa_id
JOIN kitoblar k ON k.id = n.kitob_id
JOIN azolar   a ON a.id = q.azo_id
WHERE q.qaytarilgan_sana IS NULL
ORDER BY q.qaytarish_muddati;

-- 2) Har asarning nechta nusxasi bo'sh
SELECT k.sarlavha,
       COUNT(n.id)                                          AS jami_nusxa,
       COUNT(n.id) - COUNT(q.id)                            AS bosh_nusxa
FROM kitoblar k
LEFT JOIN nusxalar n ON n.kitob_id = k.id
LEFT JOIN qarzlar  q ON q.nusxa_id = n.id AND q.qaytarilgan_sana IS NULL
GROUP BY k.id, k.sarlavha
ORDER BY k.sarlavha;

-- 3) Ko'p muallifli kitoblar — N:N to'g'ri ishlayotganini isbotlaydi
SELECT k.sarlavha, STRING_AGG(m.ism, ', ' ORDER BY km.tartib) AS mualliflar
FROM kitoblar k
JOIN kitob_mualliflari km ON km.kitob_id = k.id
JOIN mualliflar m ON m.id = km.muallif_id
GROUP BY k.id, k.sarlavha
HAVING COUNT(*) > 1;
"""

R1_EX = [
    {
        "title": "Kutubxona sxemasidagi to'g'ri qarorlar",
        "description": "Kutubxona sxemasi haqida quyidagilardan qaysilari to'g'ri?",
        "exercise_type": "multiple_choice",
        "options": [
            "kitoblar (asar) va nusxalar (jismoniy jild) alohida jadval bo'lishi kerak",
            "Bir kitobda bir nechta muallif bo'lishi mumkinligi uchun N:N junction kerak",
            "qarzlar jadvalida PRIMARY KEY (nusxa_id, azo_id) yetarli",
            "azo_profillari azolar bilan 1:1 munosabatda bo'ladi",
        ],
        "correct_answers": "A,B,D",
        "is_multiple_select": True,
        "hint": "Bir a'zo bir kitobni yil davomida necha marta olishi mumkin?",
        "explanation": "Asar va jismoniy nusxa — turli mohiyatlar; bir kitobda bir nechta muallif bo'lgani uchun N:N junction zarur; profil esa 1:1. PRIMARY KEY (nusxa_id, azo_id) esa XATO, chunki bir a'zo bir nusxani bir necha marta qarzga olishi mumkin — kalitga sana qo'shish yoki surrogate id ishlatish kerak.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Sxema loyihalash tartibi",
        "description": "Excel jadvalidan normallashtirilgan sxemaga o'tish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Mohiyatlarni (entity) ajratib olish: kitob, muallif, nusxa, a'zo, qarz",
            "Har bir mohiyat uchun birlamchi kalitni tanlash",
            "Mohiyatlar orasidagi munosabat turini aniqlash (1:1, 1:N, N:N)",
            "N:N munosabatlar uchun junction jadvallarni yaratish",
            "Cheklovlarni qo'shish: NOT NULL, CHECK, UNIQUE, FOREIGN KEY",
        ],
        "correct_order": [
            "Mohiyatlarni (entity) ajratib olish: kitob, muallif, nusxa, a'zo, qarz",
            "Har bir mohiyat uchun birlamchi kalitni tanlash",
            "Mohiyatlar orasidagi munosabat turini aniqlash (1:1, 1:N, N:N)",
            "N:N munosabatlar uchun junction jadvallarni yaratish",
            "Cheklovlarni qo'shish: NOT NULL, CHECK, UNIQUE, FOREIGN KEY",
        ],
        "hint": "Avval nimalar borligini, keyin ular qanday bog'lanishini, oxirida qoidalarni aniqlaymiz.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 12,
    },
]

R1_TASK = {
    "task_title": "🔁 R1: Kutubxona tizimi sxemasi",
    "task_description": (
        "Shahar kutubxonasi uchun to'liq normallashtirilgan sxemani noldan "
        "loyihalang: 1NF-3NF, 1:1, 1:N va N:N munosabatlarning barchasi bitta "
        "loyihada ishlatilishi kerak. Natija — ishga tushiriladigan bitta .sql fayl."
    ),
    "task_requirements": (
        "• Kamida 7 ta jadval: mualliflar, kitoblar, kitob_mualliflari, nusxalar, azolar, azo_profillari, qarzlar\n"
        "• Har bir jadvalda PRIMARY KEY; junction jadvalda kompozit kalit\n"
        "• N:N: bir kitobda bir nechta muallif bo'la olishi kerak\n"
        "• 1:1: azo_profillari (pasport, manzil) — UNIQUE yoki PK=FK bilan\n"
        "• 1:N: bir asarning bir nechta jismoniy nusxasi\n"
        "• qarzlar: bir a'zo bir nusxani turli sanalarda qayta olishi mumkin bo'lsin\n"
        "• Bir jismoniy nusxa bir vaqtda faqat bitta odamda — buni indeks yoki cheklov bilan majburlang\n"
        "• CHECK: qaytarish_muddati > olingan_sana, qaytarilgan_sana >= olingan_sana\n"
        "• Har bir FK uchun ON DELETE strategiyasini tanlang va -- komment bilan IZOHLANG\n"
        "• Test ma'lumot: 5+ muallif, 5+ kitob, 10+ nusxa, 5+ a'zo, 8+ qarz\n"
        "• 5 ta hisobot: hozir qo'lda bo'lgan nusxalar; muddati o'tgan qarzlar; "
        "har asar bo'yicha bo'sh nusxalar soni; eng faol 3 a'zo; hech qachon olinmagan asarlar\n"
        "• Bonus: qaysi normal formani qayerda qo'llaganingizni sxema boshida "
        "kommentda yozing (masalan: \"muallif_tugilgan_yil -> mualliflar: 3NF, tranzitiv bog'liqlik\")"
    ),
    "task_technologies": (
        "PostgreSQL, normalizatsiya (1NF/2NF/3NF), CREATE TABLE, PRIMARY KEY, "
        "FOREIGN KEY, kompozit kalit, junction jadval, CHECK, UNIQUE, partial index, JOIN"
    ),
    "task_deadline_days": 5,
}


# ═════════════════════════════════════════════════════════════════════════════
# L6 — Primary/Foreign key strategiyalari, ON DELETE
# ═════════════════════════════════════════════════════════════════════════════
L6_TEXT = """\
<h3>Birlamchi kalitni tanlash: natural yoki surrogate?</h3>
<p><strong>Natural kalit</strong> &mdash; ma'lumotning o'zida allaqachon mavjud bo'lgan, tabiatan noyob qiymat: ISBN, pasport raqami, email, mamlakat kodi.</p>
<p><strong>Surrogate kalit</strong> &mdash; faqat identifikatsiya uchun sun'iy yaratilgan qiymat: <code>SERIAL</code>, <code>IDENTITY</code>, <code>UUID</code>. Uning biznes ma'nosi yo'q.</p>

<table>
<tr><th>Mezon</th><th>Natural kalit</th><th>Surrogate kalit</th></tr>
<tr><td>O'qishga qulaylik</td><td>Yaxshi: <code>WHERE isbn = '978...'</code></td><td>Yomonroq: <code>WHERE id = 4821</code></td></tr>
<tr><td>O'zgarish xavfi</td><td>Yuqori &mdash; email, telefon o'zgaradi</td><td>Nol &mdash; hech qachon o'zgarmaydi</td></tr>
<tr><td>Hajmi</td><td>Katta bo'lishi mumkin (CHAR(13))</td><td>4&ndash;8 bayt</td></tr>
<tr><td>FK ustunlari</td><td>Butun kalitni takrorlaydi</td><td>Bitta ixcham son</td></tr>
<tr><td>JOIN tezligi</td><td>Sekinroq (uzun kalit)</td><td>Tezroq</td></tr>
<tr><td>Ma'lumot sizishi</td><td>PK URL da ko'rinsa &mdash; xavf</td><td>SERIAL ham sanoqni oshkor qiladi; UUID qilmaydi</td></tr>
</table>

<p><strong>Amaliy tavsiya:</strong> birlamchi kalit sifatida surrogate (<code>SERIAL</code>/<code>IDENTITY</code>) ishlating, natural kalitni esa <code>UNIQUE</code> cheklov sifatida saqlang. Shunda ikkala afzallikni ham olasiz: barqaror ichki identifikator va baza darajasida majburlangan biznes noyobligi.</p>
<p>Nima uchun email ni PK qilish yomon fikr? Foydalanuvchi emailini o'zgartirganda, unga FK bilan bog'langan barcha jadvallardagi barcha qatorlarni yangilash kerak bo'ladi (yoki <code>ON UPDATE CASCADE</code> ga umid qilish kerak). Surrogate id da esa hech narsa o'zgarmaydi &mdash; faqat <code>users.email</code> ustuni yangilanadi.</p>

<h3>SERIAL, IDENTITY yoki UUID?</h3>
<ul>
<li><code>SERIAL</code> &mdash; PostgreSQL ning eski, tanish usuli. Ichida sequence yaratadi.</li>
<li><code>GENERATED ALWAYS AS IDENTITY</code> &mdash; SQL standarti, PostgreSQL 10+ da tavsiya etiladi. Tasodifan qo'lda <code>id</code> yozib qo'yishdan himoyalaydi.</li>
<li><code>UUID</code> &mdash; taqsimlangan tizimlarda, yoki ID URL da ko'rinadigan bo'lsa (raqobatchi sizning nechta buyurtmangiz borligini bilib qolmasligi uchun). Narxi: 16 bayt va tasodifiy tartib tufayli indeks fragmentatsiyasi (buni <code>uuid_generate_v7</code> yoki <code>ULID</code> hal qiladi).</li>
</ul>

<h3>Referensial yaxlitlik va ON DELETE</h3>
<p><code>FOREIGN KEY</code> &mdash; bu shunchaki hujjat emas, bu <em>baza darajasidagi kafolat</em>: mavjud bo'lmagan mijozga buyurtma yozib bo'lmaydi. Ilova kodidagi tekshiruvdan farqi shundaki, uni chetlab o'tib bo'lmaydi &mdash; na boshqa mikroservis, na migratsiya skripti, na qo'lda yozilgan <code>psql</code> so'rovi.</p>
<p>Asosiy savol: ota qator o'chirilsa, bolalar bilan nima bo'ladi? Buni <code>ON DELETE</code> hal qiladi.</p>

<table>
<tr><th>Strategiya</th><th>Nima qiladi</th><th>Qachon ishlatiladi</th></tr>
<tr><td><code>RESTRICT</code> / <code>NO ACTION</code></td><td>Bolasi bor bo'lsa, o'chirishni bloklaydi</td><td>Standart himoya. Buyurtmalari bor mijozni o'chirmaslik</td></tr>
<tr><td><code>CASCADE</code></td><td>Bolalarni ham o'chiradi</td><td>Bola otasisiz ma'nosiz bo'lganda: buyurtma_elementlari, profil</td></tr>
<tr><td><code>SET NULL</code></td><td>FK ni NULL ga o'zgartiradi</td><td>Bog'lanish ixtiyoriy bo'lganda: xodim ketdi, vazifa qoldi</td></tr>
<tr><td><code>SET DEFAULT</code></td><td>FK ni DEFAULT qiymatga o'tkazadi</td><td>Kamdan-kam: "Arxiv" kategoriyasiga o'tkazish</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  D["DELETE FROM mijozlar WHERE id = 5"] --> Q{"buyurtmalar.mijoz_id
FK strategiyasi?"}
  Q -->|"RESTRICT"| R["XATO: o'chirish bloklandi.
Mijoz va uning tarixi saqlanadi."]
  Q -->|"CASCADE"| C["Mijoz + barcha buyurtmalari
+ barcha buyurtma_elementlari o'chdi.
Moliyaviy tarix yo'qoldi!"]
  Q -->|"SET NULL"| S["Buyurtmalar qoldi,
lekin mijoz_id = NULL.
'Kimniki?' — endi noma'lum."]
</pre>

<h3>Real oqibat: mijozni o'chirish</h3>
<p>Bu &mdash; eng ko'p uchraydigan va eng qimmatga tushadigan xato. Aytaylik <code>buyurtmalar.mijoz_id</code> ga <code>ON DELETE CASCADE</code> qo'yilgan. Support xodimi mijozning "hisobini o'chirish" so'roviga javoban bitta <code>DELETE</code> yozadi &mdash; va shu bilan uch yillik sotuv tarixi, buxgalteriya hisoboti va oylik daromad statistikasi bir zumda yo'qoladi. Hech qanday ogohlantirishsiz.</p>
<p><strong>To'g'ri yondashuv:</strong> moliyaviy ma'noga ega ma'lumot uchun <code>ON DELETE RESTRICT</code> qo'ying va o'chirish o'rniga <em>soft delete</em> ishlating &mdash; <code>ochirilgan_sana TIMESTAMPTZ</code> ustuni. Mijoz ilova uchun "yo'q", lekin buyurtmalar tarixi va hisobotlar joyida qoladi.</p>
<p><code>CASCADE</code> ni faqat bola qator otasisiz haqiqatan ma'nosiz bo'lganda ishlating: <code>buyurtma_elementlari</code> o'chirilgan buyurtmasiz, <code>user_profiles</code> o'chirilgan usersiz, <code>post_tags</code> o'chirilgan postsiz &mdash; bularning hech biri mustaqil qiymatga ega emas.</p>
"""

L6_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- Kalit strategiyalari va ON DELETE — har birining oqibatini ko'ramiz
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS vazifalar;
DROP TABLE IF EXISTS xodimlar;
DROP TABLE IF EXISTS buyurtma_elementlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mahsulotlar;
DROP TABLE IF EXISTS mijozlar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) Surrogate PK + natural kalit UNIQUE sifatida — tavsiya etilgan usul
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE mijozlar (
    -- IDENTITY: SQL standarti, SERIAL dan xavfsizroq (qo'lda id yozib
    -- bo'lmaydi, shuning uchun sequence hech qachon "adashib" qolmaydi)
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- natural kalit: PK emas, lekin baza darajasida noyob
    email           VARCHAR(120) NOT NULL UNIQUE,
    ism             VARCHAR(80)  NOT NULL,
    -- soft delete: o'chirish o'rniga sana qo'yamiz
    ochirilgan_sana TIMESTAMPTZ
);

CREATE TABLE mahsulotlar (
    id   INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi VARCHAR(80)   NOT NULL,
    narx NUMERIC(12,2) NOT NULL CHECK (narx > 0)
);

-- ─────────────────────────────────────────────────────────────────────
-- 2) ON DELETE RESTRICT — moliyaviy tarixni himoya qiladi
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE buyurtmalar (
    id         INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- RESTRICT: buyurtmasi bor mijozni o'chirib BO'LMAYDI
    mijoz_id   INTEGER     NOT NULL REFERENCES mijozlar(id) ON DELETE RESTRICT,
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────
-- 3) ON DELETE CASCADE — bola otasisiz ma'nosiz bo'lganda
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    -- mahsulotga esa RESTRICT: sotilgan mahsulotni katalogdan
    -- o'chirish tarixni buzadi
    mahsulot_id INTEGER NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor      INTEGER NOT NULL CHECK (miqdor > 0),
    -- TARIXIY narx: mahsulot narxi keyin o'zgarsa ham chek o'zgarmaydi
    narx_birlik NUMERIC(12,2) NOT NULL CHECK (narx_birlik > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)
);

-- ─────────────────────────────────────────────────────────────────────
-- 4) ON DELETE SET NULL — bog'lanish ixtiyoriy bo'lganda
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE xodimlar (
    id  INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ism VARCHAR(80) NOT NULL
);

CREATE TABLE vazifalar (
    id        INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sarlavha  VARCHAR(150) NOT NULL,
    -- SET NULL ishlashi uchun ustun NULL qabul QILISHI SHART
    xodim_id  INTEGER      REFERENCES xodimlar(id) ON DELETE SET NULL,
    muddat    DATE
);

-- ── Test ma'lumot ─────────────────────────────────────────────────────
INSERT INTO mijozlar (email, ism) VALUES
    ('aziz@mail.uz', 'Aziz Karimov'),
    ('dilya@mail.uz','Dilnoza Rasulova');

INSERT INTO mahsulotlar (nomi, narx) VALUES
    ('iPhone 15', 15000000),
    ('Chexol',       85000);

INSERT INTO buyurtmalar (mijoz_id) VALUES (1), (1), (2);

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik) VALUES
    (1, 1, 1, 15000000),
    (1, 2, 2,    85000),
    (2, 2, 3,    85000),
    (3, 1, 1, 15000000);

INSERT INTO xodimlar (ism) VALUES ('Sardor'), ('Nigora');
INSERT INTO vazifalar (sarlavha, xodim_id, muddat) VALUES
    ('Hisobot tayyorlash', 1, DATE '2026-08-01'),
    ('Sxemani ko''rib chiqish', 1, DATE '2026-08-10'),
    ('Backup sozlash', 2, DATE '2026-08-05');

-- ─────────────────────────────────────────────────────────────────────
-- TAJRIBA 1: RESTRICT haqiqatan himoya qilayotganini ko'ramiz
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    DELETE FROM mijozlar WHERE id = 1;
    RAISE NOTICE 'Mijoz o''chirildi — bu KUTILMAGAN natija!';
EXCEPTION WHEN foreign_key_violation THEN
    RAISE NOTICE 'RESTRICT ishladi: buyurtmasi bor mijoz o''chirilmadi.';
END $$;

-- To'g'ri yondashuv — soft delete. Tarix saqlanadi, mijoz "yo'q" bo'ladi:
UPDATE mijozlar SET ochirilgan_sana = NOW() WHERE id = 1;

SELECT id, ism, ochirilgan_sana IS NOT NULL AS ochirilganmi FROM mijozlar ORDER BY id;

-- Ilova endi faqat faol mijozlarni oladi:
SELECT id, ism FROM mijozlar WHERE ochirilgan_sana IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- TAJRIBA 2: CASCADE — buyurtmani o'chirsak, elementlari ham o'chadi
-- ─────────────────────────────────────────────────────────────────────
SELECT COUNT(*) AS elementlar_ochirishdan_oldin FROM buyurtma_elementlari;

DELETE FROM buyurtmalar WHERE id = 2;

SELECT COUNT(*) AS elementlar_ochirishdan_keyin FROM buyurtma_elementlari;
-- 4 -> 3. CASCADE avtomatik ishladi, "yetim" qator qolmadi.

-- ─────────────────────────────────────────────────────────────────────
-- TAJRIBA 3: SET NULL — xodim ketdi, vazifalar qoldi
-- ─────────────────────────────────────────────────────────────────────
DELETE FROM xodimlar WHERE id = 1;

SELECT sarlavha, xodim_id, muddat FROM vazifalar ORDER BY id;
-- Ikkita vazifada xodim_id = NULL. Ish yo'qolmadi, faqat egasiz qoldi —
-- menejer ularni qayta taqsimlashi mumkin.

-- ─────────────────────────────────────────────────────────────────────
-- MUHIM ESLATMA: FK ustuniga PostgreSQL AVTOMATIK indeks YARATMAYDI.
-- Faqat PRIMARY KEY va UNIQUE indeks oladi. FK ga indeks bo'lmasa,
-- ota qatorni o'chirish har safar bola jadvalni to'liq skanerlaydi.
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX buyurtmalar_mijoz_id_idx  ON buyurtmalar (mijoz_id);
CREATE INDEX vazifalar_xodim_id_idx    ON vazifalar (xodim_id);
CREATE INDEX bel_mahsulot_id_idx       ON buyurtma_elementlari (mahsulot_id);
"""

L6_EX = [
    {
        "title": "Email ni PRIMARY KEY qilish",
        "description": "Nima uchun foydalanuvchi emailini birlamchi kalit qilish yomon g'oya hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Email o'zgarishi mumkin, va u o'zgarganda unga bog'langan barcha FK qiymatlarini yangilash kerak bo'ladi",
            "PostgreSQL matn turini birlamchi kalit sifatida qabul qilmaydi",
            "Email ustuniga UNIQUE cheklov qo'yib bo'lmaydi",
            "Email har doim NULL bo'lishi mumkin",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Birlamchi kalitning eng muhim xususiyati — barqarorlik.",
        "explanation": "Natural kalitning asosiy muammosi — o'zgaruvchanlik. Email o'zgarganda unga FK bilan bog'langan barcha jadvallardagi qiymatlarni ham yangilash kerak. Surrogate id esa hech qachon o'zgarmaydi, shuning uchun email ni UNIQUE cheklov sifatida saqlash to'g'riroq.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "Mijozni o'chirishda to'g'ri strategiya",
        "description": "buyurtmalar.mijoz_id uchun qaysi ON DELETE strategiyasi moliyaviy tarixni himoya qiladi va soft delete bilan birga ishlatilishi tavsiya etiladi?",
        "exercise_type": "multiple_choice",
        "options": ["CASCADE", "SET NULL", "RESTRICT", "SET DEFAULT"],
        "correct_answers": "C",
        "is_multiple_select": False,
        "hint": "Buyurtmalari bor mijozni umuman o'chirib bo'lmasligi kerak.",
        "explanation": "RESTRICT buyurtmasi bor mijozni o'chirishni bloklaydi va shu orqali sotuv tarixini saqlab qoladi. CASCADE bu holatda butun moliyaviy tarixni yo'q qilib yuborardi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "FK ustuni va indeks",
        "description": "PostgreSQL FOREIGN KEY ustuni uchun indeksni avtomatik yaratadimi? Javobni bitta so'z bilan yozing (ha / yo'q).",
        "exercise_type": "fill_in_blank",
        "correct_answers": "yo'q",
        "hint": "Avtomatik indeks faqat PRIMARY KEY va UNIQUE cheklovlarida paydo bo'ladi.",
        "explanation": "PostgreSQL FK ustuniga indeks yaratmaydi — buni qo'lda qilish kerak. Aks holda ota qatorni har o'chirish yoki yangilashda bola jadval to'liq skanerlanadi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L7 — CHECK, UNIQUE, NOT NULL, DEFAULT
# ═════════════════════════════════════════════════════════════════════════════
L7_TEXT = """\
<h3>Biznes qoidasi qayerda yashashi kerak?</h3>
<p>"Narx musbat bo'lishi kerak" &mdash; bu qoidani qayerga yozamiz? Ko'pchilik javob beradi: ilova kodida, validatsiya funksiyasida. Bu javob yetarli emas.</p>
<p>Baza bitta ilova bilan gaplashmaydi. Uning bilan ishlaydiganlar: web-backend, mobil API, cron-skript, ma'lumot import qiluvchi ETL, migratsiya fayli, analitikning qo'lda yozgan <code>UPDATE</code> i va yarim tunda ishga tushirilgan tuzatish skripti. Ilovadagi validatsiya bulardan faqat bittasini qamrab oladi.</p>
<p><strong>Baza darajasidagi cheklov &mdash; oxirgi va yagona ishonchli himoya chizig'i.</strong> Uni chetlab o'tish uchun cheklovni ataylab o'chirish kerak bo'ladi.</p>

<h3>To'rt asosiy cheklov</h3>
<table>
<tr><th>Cheklov</th><th>Nimani kafolatlaydi</th><th>Misol</th></tr>
<tr><td><code>NOT NULL</code></td><td>Qiymat majburiy</td><td><code>email VARCHAR(120) NOT NULL</code></td></tr>
<tr><td><code>DEFAULT</code></td><td>Ko'rsatilmasa qanday qiymat qo'yiladi</td><td><code>holat VARCHAR(12) DEFAULT 'yangi'</code></td></tr>
<tr><td><code>UNIQUE</code></td><td>Qiymat takrorlanmaydi</td><td><code>UNIQUE (email)</code></td></tr>
<tr><td><code>CHECK</code></td><td>Ixtiyoriy mantiqiy shart</td><td><code>CHECK (narx &gt; 0)</code></td></tr>
</table>

<h3>NULL &mdash; UNIQUE va CHECK bilan ishlashda tuzoq</h3>
<p>Bu &mdash; boshlovchilarni eng ko'p adashtiradigan joy, shuning uchun aniq eslab qoling:</p>
<ul>
<li><strong><code>UNIQUE</code> va NULL:</strong> SQL da <code>NULL = NULL</code> emas, balki <code>NULL</code>. Shuning uchun <code>UNIQUE</code> ustunga <strong>bir nechta <code>NULL</code> kirishi mumkin</strong>. Agar bu sizga to'g'ri kelmasa &mdash; <code>NOT NULL</code> qo'shing yoki PostgreSQL 15+ da <code>UNIQUE NULLS NOT DISTINCT</code> ishlating.</li>
<li><strong><code>CHECK</code> va NULL:</strong> <code>CHECK</code> shart <code>NULL</code> (noma'lum) qaytarsa, cheklov <strong>buzilmagan</strong> hisoblanadi. Ya'ni <code>CHECK (yosh &gt;= 18)</code> bo'lgan ustunga <code>NULL</code> bemalol kiradi. Faqat <code>FALSE</code> qatorni rad etadi.</li>
</ul>

<h3>DEFAULT qachon qo'llaniladi</h3>
<p>DEFAULT faqat ustun <code>INSERT</code> da <em>umuman ko'rsatilmaganda</em> ishlaydi. Agar siz aniq <code>NULL</code> yozsangiz &mdash; DEFAULT qo'llanilmaydi va ustunga <code>NULL</code> tushadi. Bu farq ma'lumot import qilishda tez-tez muammo tug'diradi.</p>

<pre class="mermaid">
flowchart TB
  I["INSERT so'rovi keldi"] --> N{"Ustun ko'rsatilganmi?"}
  N -->|"Yo'q"| D["DEFAULT qiymat qo'yiladi"]
  N -->|"Ha, NULL yozilgan"| NL["NULL qo'yiladi — DEFAULT ISHLAMAYDI"]
  N -->|"Ha, qiymat bor"| V["Qiymat olinadi"]
  D --> C{"NOT NULL / CHECK / UNIQUE
tekshiruvi"}
  NL --> C
  V --> C
  C -->|"Hammasi TRUE yoki NULL"| OK["Qator yoziladi"]
  C -->|"Biror shart FALSE"| ERR["ERROR — qator rad etildi"]
</pre>

<h3>Amaliyotdan tavsiyalar</h3>
<ul>
<li><strong>Cheklovga nom bering.</strong> <code>CONSTRAINT mahsulotlar_narx_musbat CHECK (narx &gt; 0)</code>. Avtomatik nom (<code>mahsulotlar_narx_check</code>) xato xabarida foydalanuvchiga hech narsa aytmaydi va migratsiyada uni topish qiyin bo'ladi.</li>
<li><strong>Holat ustunlari uchun <code>CHECK (holat IN (...))</code> yozing.</strong> U <code>ENUM</code> dan ko'ra moslashuvchan: yangi qiymat qo'shish uchun <code>ALTER TABLE ... DROP CONSTRAINT / ADD CONSTRAINT</code> yetarli, <code>ENUM</code> da esa tur o'zgartirish kerak.</li>
<li><strong>Bir nechta ustunni bog'laydigan <code>CHECK</code> yozishdan qo'rqmang:</strong> <code>CHECK (tugash_sanasi &gt; boshlanish_sanasi)</code>. Bu &mdash; jadval darajasidagi cheklov va u ilovadagi eng ko'p uchraydigan sana xatolarini butunlay yo'q qiladi.</li>
<li><strong>Shartli noyoblik uchun partial unique indeks:</strong> <code>CREATE UNIQUE INDEX ... WHERE ochirilgan_sana IS NULL</code>. Shunda o'chirilgan yozuvlar noyoblikni band qilib turmaydi.</li>
</ul>
"""

L7_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- Cheklovlar: biznes qoidalarini ilova emas, BAZA majburlaydi
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS bronlar;
DROP TABLE IF EXISTS xonalar;

CREATE TABLE xonalar (
    id      INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raqami  VARCHAR(10)  NOT NULL,
    qavat   SMALLINT     NOT NULL,
    sigim   SMALLINT     NOT NULL,
    narx    NUMERIC(10,2) NOT NULL,
    holat   VARCHAR(12)  NOT NULL DEFAULT 'bosh',

    -- Cheklovga NOM beramiz: xato xabari tushunarli bo'ladi
    CONSTRAINT xonalar_raqami_uq       UNIQUE (raqami),
    CONSTRAINT xonalar_qavat_diapazon  CHECK (qavat BETWEEN 1 AND 30),
    CONSTRAINT xonalar_sigim_musbat    CHECK (sigim BETWEEN 1 AND 8),
    CONSTRAINT xonalar_narx_musbat     CHECK (narx > 0),
    CONSTRAINT xonalar_holat_qiymatlar CHECK (holat IN ('bosh', 'band', 'tamirda'))
);

INSERT INTO xonalar (raqami, qavat, sigim, narx) VALUES
    ('101', 1, 2,  450000),
    ('102', 1, 2,  450000),
    ('205', 2, 4,  850000),
    ('301', 3, 1,  300000);
-- holat ko'rsatilmadi -> DEFAULT 'bosh' qo'yildi

SELECT raqami, qavat, sigim, narx, holat FROM xonalar ORDER BY raqami;

-- ─────────────────────────────────────────────────────────────────────
-- Har bir cheklov haqiqatan ishlayotganini tekshiramiz.
-- DO blok ichida xatoni ushlab, NOTICE chiqaramiz.
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx) VALUES ('999', 45, 2, 500000);
    RAISE NOTICE 'XATO: 45-qavat qabul qilindi!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK ishladi: 45-qavat rad etildi (qavat 1..30).';
END $$;

DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx) VALUES ('102', 1, 2, 450000);
    RAISE NOTICE 'XATO: takroriy xona raqami qabul qilindi!';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'UNIQUE ishladi: 102-xona ikki marta yaratilmadi.';
END $$;

DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx, holat)
    VALUES ('401', 4, 2, 500000, 'tozalanmoqda');
    RAISE NOTICE 'XATO: noma''lum holat qabul qilindi!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK IN ishladi: "tozalanmoqda" ruxsat etilmagan holat.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- Ko'p ustunli CHECK: sana mantiqini baza darajasida majburlash
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE bronlar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    xona_id         INTEGER      NOT NULL REFERENCES xonalar(id) ON DELETE RESTRICT,
    mehmon_email    VARCHAR(120) NOT NULL,
    kirish_sanasi   DATE         NOT NULL,
    chiqish_sanasi  DATE         NOT NULL,
    mehmonlar_soni  SMALLINT     NOT NULL DEFAULT 1,
    bekor_qilingan  BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT bronlar_sana_tartibi   CHECK (chiqish_sanasi > kirish_sanasi),
    CONSTRAINT bronlar_mehmon_soni    CHECK (mehmonlar_soni BETWEEN 1 AND 8),
    CONSTRAINT bronlar_email_formati  CHECK (mehmon_email LIKE '%_@_%._%')
);

INSERT INTO bronlar (xona_id, mehmon_email, kirish_sanasi, chiqish_sanasi, mehmonlar_soni) VALUES
    (1, 'aziz@mail.uz',  DATE '2026-08-01', DATE '2026-08-05', 2),
    (3, 'dilya@mail.uz', DATE '2026-08-03', DATE '2026-08-07', 4);

DO $$
BEGIN
    INSERT INTO bronlar (xona_id, mehmon_email, kirish_sanasi, chiqish_sanasi)
    VALUES (1, 'test@mail.uz', DATE '2026-09-10', DATE '2026-09-05');
    RAISE NOTICE 'XATO: chiqish kirishdan oldin bo''lgan bron qabul qilindi!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK ishladi: chiqish sanasi kirishdan oldin bo''lolmaydi.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- NULL TUZOQLARI — buni albatta o'zingiz sinab ko'ring
-- ─────────────────────────────────────────────────────────────────────

-- 1) UNIQUE ustunga bir nechta NULL KIRADI, chunki NULL != NULL
ALTER TABLE xonalar ADD COLUMN qayd_raqami VARCHAR(20);
ALTER TABLE xonalar ADD CONSTRAINT xonalar_qayd_uq UNIQUE (qayd_raqami);

UPDATE xonalar SET qayd_raqami = NULL;   -- hammasi NULL
SELECT COUNT(*) AS null_qatorlar FROM xonalar WHERE qayd_raqami IS NULL;
-- 4 ta qator, hammasi NULL — va UNIQUE hech qanday e'tiroz bildirmadi!

-- 2) CHECK sharti NULL qaytarsa, cheklov BUZILMAGAN hisoblanadi
ALTER TABLE xonalar ADD COLUMN yosh_chegarasi SMALLINT;
ALTER TABLE xonalar ADD CONSTRAINT xonalar_yosh_check
    CHECK (yosh_chegarasi >= 18);

INSERT INTO xonalar (raqami, qavat, sigim, narx, yosh_chegarasi)
VALUES ('501', 5, 2, 600000, NULL);   -- NULL bemalol kiradi!

SELECT raqami, yosh_chegarasi FROM xonalar WHERE raqami = '501';
-- Agar qiymat majburiy bo'lsa, CHECK yetarli emas — NOT NULL ham kerak.

-- ─────────────────────────────────────────────────────────────────────
-- DEFAULT tuzog'i: aniq NULL yozilsa, DEFAULT ISHLAMAYDI
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx, holat)
    VALUES ('502', 5, 2, 600000, NULL);
    RAISE NOTICE 'XATO: NULL holat qabul qilindi!';
EXCEPTION WHEN not_null_violation THEN
    RAISE NOTICE 'NOT NULL ishladi: aniq NULL yozilganda DEFAULT qo''llanilmaydi.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- PARTIAL UNIQUE INDEX: shartli noyoblik
-- Bekor qilingan bronlar noyoblikni band qilib turmasligi kerak
-- ─────────────────────────────────────────────────────────────────────
CREATE UNIQUE INDEX bronlar_faol_xona_sana_uq
    ON bronlar (xona_id, kirish_sanasi)
    WHERE bekor_qilingan = FALSE;

-- Bekor qilingan bron bilan bir xil sanaga yangisini yozish MUMKIN:
UPDATE bronlar SET bekor_qilingan = TRUE WHERE id = 1;
INSERT INTO bronlar (xona_id, mehmon_email, kirish_sanasi, chiqish_sanasi)
VALUES (1, 'yangi@mail.uz', DATE '2026-08-01', DATE '2026-08-04');

SELECT id, xona_id, mehmon_email, kirish_sanasi, bekor_qilingan
FROM bronlar ORDER BY id;
"""

L7_EX = [
    {
        "title": "UNIQUE va NULL",
        "description": "UNIQUE cheklovga ega ustunga nechta NULL qiymat kirita olasiz (PostgreSQL da, standart sozlamada)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir nechta — chunki SQL da NULL boshqa NULL ga teng hisoblanmaydi",
            "Faqat bitta — NULL ham oddiy qiymat sifatida qaraladi",
            "Bittasi ham — UNIQUE ustun NULL qabul qilmaydi",
            "Faqat jadval bo'sh bo'lganda",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "SQL da NULL = NULL ifodasi TRUE emas, balki NULL qaytaradi.",
        "explanation": "SQL da NULL = NULL taqqoslashi NULL (noma'lum) qaytaradi, shuning uchun UNIQUE cheklov bir nechta NULL ga ruxsat beradi. Agar bu kerak bo'lmasa — NOT NULL qo'shing yoki PostgreSQL 15+ da UNIQUE NULLS NOT DISTINCT ishlating.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "CHECK sharti NULL qaytarganda",
        "description": "CHECK (yosh >= 18) cheklovi bor ustunga NULL qiymat yozilsa nima bo'ladi? Bo'sh joyni to'ldiring: qator ___ (qabul qilinadi / rad etiladi).",
        "exercise_type": "fill_in_blank",
        "correct_answers": "qabul qilinadi",
        "hint": "CHECK faqat FALSE natijada qatorni rad etadi.",
        "explanation": "CHECK sharti NULL (noma'lum) qaytarsa, cheklov buzilmagan hisoblanadi va qator qabul qilinadi. Qiymat majburiy bo'lsa, CHECK yetarli emas — NOT NULL ham qo'shish kerak.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Cheklov qatlamlarini tartibga solish",
        "description": "INSERT so'rovi kelganda PostgreSQL qanday tartibda ish ko'radi? Qadamlarni to'g'ri joylashtiring.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Ko'rsatilmagan ustunlarga DEFAULT qiymat qo'yiladi",
            "NOT NULL cheklovlari tekshiriladi",
            "CHECK shartlari hisoblanadi (faqat FALSE rad etadi)",
            "UNIQUE va PRIMARY KEY indekslari tekshiriladi",
            "FOREIGN KEY mavjudligi tekshiriladi",
        ],
        "correct_order": [
            "Ko'rsatilmagan ustunlarga DEFAULT qiymat qo'yiladi",
            "NOT NULL cheklovlari tekshiriladi",
            "CHECK shartlari hisoblanadi (faqat FALSE rad etadi)",
            "UNIQUE va PRIMARY KEY indekslari tekshiriladi",
            "FOREIGN KEY mavjudligi tekshiriladi",
        ],
        "hint": "Avval qiymat shakllanadi, keyin ustun darajasidagi, oxirida jadvallararo tekshiruvlar.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L8 — ER diagrammalar
# ═════════════════════════════════════════════════════════════════════════════
L8_TEXT = """\
<h3>Nima uchun avval diagramma chiziladi</h3>
<p><code>CREATE TABLE</code> yozishdan oldin sxemani chizish &mdash; bu vaqtni tejash emas, balki <em>xatoni arzon bosqichda topish</em>. Diagrammada munosabatni o'zgartirish 10 soniya oladi. Ishlab turgan bazada esa bu &mdash; migratsiya, ma'lumotni ko'chirish, ilova kodini o'zgartirish va deploy.</p>
<p><strong>ER diagramma</strong> (Entity-Relationship) uch narsani ko'rsatadi: qanday mohiyatlar bor, ularda qanday atributlar bor va ular bir-biri bilan qanday bog'langan.</p>

<h3>Crow's foot notatsiyasi</h3>
<p>Eng keng tarqalgan belgilash usuli. Chiziqning har uchi ikkita belgidan iborat: birinchisi &mdash; <em>minimum</em> (0 yoki 1), ikkinchisi &mdash; <em>maksimum</em> (1 yoki ko'p).</p>
<table>
<tr><th>Belgi</th><th>Mermaid yozuvi</th><th>Ma'nosi</th></tr>
<tr><td>Bir (aniq)</td><td><code>||</code></td><td>Aynan bitta</td></tr>
<tr><td>Nol yoki bir</td><td><code>o|</code></td><td>Ixtiyoriy, ko'pi bilan bitta</td></tr>
<tr><td>Bir yoki ko'p</td><td><code>}|</code></td><td>Kamida bitta</td></tr>
<tr><td>Nol yoki ko'p</td><td><code>}o</code></td><td>Ixtiyoriy, cheklanmagan</td></tr>
</table>
<p>Eng ko'p ishlatiladigan kombinatsiyalar:</p>
<ul>
<li><code>MIJOZLAR ||--o{ BUYURTMALAR</code> &mdash; bir mijozda nol yoki ko'p buyurtma; har buyurtmada aynan bitta mijoz.</li>
<li><code>USERS ||--o| PROFILLAR</code> &mdash; 1:1, profil ixtiyoriy.</li>
<li><code>BUYURTMALAR ||--|{ ELEMENTLAR</code> &mdash; buyurtmada kamida bitta element bo'lishi shart.</li>
</ul>

<h3>To'liq misol: kichik e-commerce</h3>
<pre class="mermaid">
erDiagram
    MIJOZLAR ||--o{ BUYURTMALAR : "beradi"
    MIJOZLAR ||--o| MIJOZ_PROFILLARI : "ega"
    BUYURTMALAR ||--|{ BUYURTMA_ELEMENTLARI : "tarkibi"
    MAHSULOTLAR ||--o{ BUYURTMA_ELEMENTLARI : "sotiladi"
    KATEGORIYALAR ||--o{ MAHSULOTLAR : "guruhlaydi"

    MIJOZLAR {
        int id PK
        varchar email UK
        varchar ism
        timestamptz ochirilgan_sana
    }
    MIJOZ_PROFILLARI {
        int mijoz_id PK "FK ham"
        varchar telefon
        text manzil
    }
    KATEGORIYALAR {
        int id PK
        varchar nomi UK
    }
    MAHSULOTLAR {
        int id PK
        int kategoriya_id FK
        varchar nomi
        numeric narx
    }
    BUYURTMALAR {
        int id PK
        int mijoz_id FK
        varchar holat
        timestamptz yaratilgan
    }
    BUYURTMA_ELEMENTLARI {
        int buyurtma_id PK "FK ham"
        int mahsulot_id PK "FK ham"
        int miqdor
        numeric narx_birlik
    }
</pre>

<h3>Diagrammadan kodga: mexanik tarjima</h3>
<p>ER diagramma to'g'ri chizilgan bo'lsa, <code>CREATE TABLE</code> yozish ijodiy ish emas &mdash; bu mexanik tarjima. Qoidalar:</p>
<table>
<tr><th>Diagrammada</th><th>Kodda</th></tr>
<tr><td>Mohiyat (to'rtburchak)</td><td><code>CREATE TABLE</code></td></tr>
<tr><td><code>PK</code> belgisi</td><td><code>PRIMARY KEY</code></td></tr>
<tr><td><code>UK</code> belgisi</td><td><code>UNIQUE</code> cheklov</td></tr>
<tr><td><code>FK</code> belgisi</td><td><code>REFERENCES boshqa_jadval(id)</code></td></tr>
<tr><td><code>||--o{</code> (1:N)</td><td>FK "ko'p" tomondagi jadvalda</td></tr>
<tr><td><code>||--o|</code> (1:1)</td><td>FK + <code>UNIQUE</code> (yoki FK = PK)</td></tr>
<tr><td>N:N munosabat</td><td>Junction jadval, kompozit PK</td></tr>
<tr><td><code>||</code> chap tomonda (majburiy)</td><td>FK ustunida <code>NOT NULL</code></td></tr>
<tr><td><code>o|</code> chap tomonda (ixtiyoriy)</td><td>FK ustuni <code>NULL</code> qabul qiladi</td></tr>
</table>
<p>Diqqat qiling: mermaid <code>erDiagram</code> da N:N ni <code>}o--o{</code> ko'rinishida chizish <em>mumkin</em>, lekin kodda u hech qachon to'g'ridan-to'g'ri amalga oshirilmaydi. Shuning uchun diagrammani ham darhol junction jadval bilan chizing &mdash; shunda diagramma haqiqiy sxemani aks ettiradi, uning soddalashtirilgan xayoliy versiyasini emas.</p>
"""

L8_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- ER diagrammadan CREATE TABLE ga — mexanik tarjima
-- Yuqoridagi diagrammadagi har bir belgining kodda qanday
-- ko'rinishini bosqichma-bosqich kuzating.
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS buyurtma_elementlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mahsulotlar;
DROP TABLE IF EXISTS kategoriyalar;
DROP TABLE IF EXISTS mijoz_profillari;
DROP TABLE IF EXISTS mijozlar;

-- ── MIJOZLAR: id PK, email UK ─────────────────────────────────────────
CREATE TABLE mijozlar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR(120) NOT NULL UNIQUE,   -- diagrammadagi UK
    ism             VARCHAR(80)  NOT NULL,
    ochirilgan_sana TIMESTAMPTZ
);

-- ── MIJOZLAR ||--o| MIJOZ_PROFILLARI ──────────────────────────────────
-- "o|" = nol yoki bitta -> 1:1, profil ixtiyoriy.
-- PK = FK usuli: UNIQUE avtomatik ta'minlanadi.
CREATE TABLE mijoz_profillari (
    mijoz_id INTEGER PRIMARY KEY REFERENCES mijozlar(id) ON DELETE CASCADE,
    telefon  VARCHAR(20),
    manzil   TEXT
);

-- ── KATEGORIYALAR ||--o{ MAHSULOTLAR ──────────────────────────────────
-- "||" chapda = har mahsulotda AYNAN BITTA kategoriya -> FK NOT NULL
-- "o{" o'ngda = kategoriyada nol yoki ko'p mahsulot -> FK da UNIQUE yo'q
CREATE TABLE kategoriyalar (
    id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE mahsulotlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kategoriya_id INTEGER       NOT NULL REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi          VARCHAR(100)  NOT NULL,
    narx          NUMERIC(12,2) NOT NULL CHECK (narx > 0)
);

-- ── MIJOZLAR ||--o{ BUYURTMALAR ───────────────────────────────────────
CREATE TABLE buyurtmalar (
    id         INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijoz_id   INTEGER     NOT NULL REFERENCES mijozlar(id) ON DELETE RESTRICT,
    holat      VARCHAR(20) NOT NULL DEFAULT 'yangi'
               CHECK (holat IN ('yangi','tasdiqlangan','yetkazildi','bekor')),
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── BUYURTMALAR ||--|{ BUYURTMA_ELEMENTLARI ───────────────────────────
-- "|{" = kamida BITTA element bo'lishi shart.
-- Diqqat: bu qoidani CREATE TABLE ning o'zi majburlay OLMAYDI —
-- u faqat ilova mantig'i yoki DEFERRABLE tekshiruv orqali ta'minlanadi.
-- Bu — ER diagramma kod bilan 100% mos kelmaydigan kam sonli joylardan biri.
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor      INTEGER       NOT NULL CHECK (miqdor > 0),
    narx_birlik NUMERIC(12,2) NOT NULL CHECK (narx_birlik > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)   -- kompozit PK, N:N junction
);

-- FK ustunlariga indeks (PK birinchi ustunni qoplaydi, ikkinchisini yo'q)
CREATE INDEX mahsulotlar_kategoriya_idx ON mahsulotlar (kategoriya_id);
CREATE INDEX buyurtmalar_mijoz_idx      ON buyurtmalar (mijoz_id);
CREATE INDEX bel_mahsulot_idx           ON buyurtma_elementlari (mahsulot_id);

-- ── Test ma'lumot ─────────────────────────────────────────────────────
INSERT INTO mijozlar (email, ism) VALUES
    ('aziz@shop.uz',  'Aziz Karimov'),
    ('dilya@shop.uz', 'Dilnoza Rasulova');

INSERT INTO mijoz_profillari (mijoz_id, telefon) VALUES (1, '+998901112233');

INSERT INTO kategoriyalar (nomi) VALUES ('Telefonlar'), ('Aksessuarlar');

INSERT INTO mahsulotlar (kategoriya_id, nomi, narx) VALUES
    (1, 'iPhone 15', 15000000),
    (1, 'Samsung S24', 12000000),
    (2, 'Chexol', 85000);

INSERT INTO buyurtmalar (mijoz_id, holat) VALUES (1, 'yetkazildi'), (2, 'yangi');

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik) VALUES
    (1, 1, 1, 15000000),
    (1, 3, 2,    85000),
    (2, 2, 1, 12000000);

-- ─────────────────────────────────────────────────────────────────────
-- TESKARI YO'NALISH: mavjud bazadan diagramma tiklash.
-- Quyidagi so'rov barcha FK munosabatlarini crow's foot ko'rinishida
-- chiqaradi — begona loyihaga kirganda birinchi ishlatiladigan so'rov.
-- ─────────────────────────────────────────────────────────────────────
SELECT
    src.relname  || ' }o--|| ' || tgt.relname AS munosabat,
    a.attname                                 AS fk_ustun,
    CASE WHEN a.attnotnull THEN 'majburiy' ELSE 'ixtiyoriy' END AS majburiylik
FROM pg_constraint c
JOIN pg_class src ON src.oid = c.conrelid
JOIN pg_class tgt ON tgt.oid = c.confrelid
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND src.relnamespace = current_schema()::regnamespace
ORDER BY munosabat;

-- Har jadvaldagi cheklovlar ro'yxati — dizaynni tekshirish uchun
SELECT conrelid::regclass AS jadval,
       conname            AS cheklov_nomi,
       CASE contype WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'c' THEN 'CHECK' END AS turi
FROM pg_constraint
WHERE connamespace = current_schema()::regnamespace
ORDER BY jadval, turi;
"""

L8_EX = [
    {
        "title": "Crow's foot: ||--o{ nimani anglatadi?",
        "description": "Mermaid erDiagram da MIJOZLAR ||--o{ BUYURTMALAR yozuvi qanday munosabatni bildiradi?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir mijozda nol yoki ko'p buyurtma; har buyurtmada aynan bitta mijoz",
            "Bir mijozda aynan bitta buyurtma; bir buyurtmada ko'p mijoz",
            "Ko'p-ko'p munosabat, junction jadval kerak",
            "Bir mijozda kamida bitta buyurtma bo'lishi shart",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "'o' — nol (ixtiyoriy), '{' — ko'p, '||' — aynan bitta.",
        "explanation": "|| chap tomonda 'aynan bitta' degani, o{ o'ng tomonda 'nol yoki ko'p'. Ya'ni klassik 1:N: har buyurtmaning bitta mijozi bor, mijozda esa buyurtma umuman bo'lmasligi ham mumkin.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "1:1 ni kodga o'girish",
        "description": "ER diagrammada USERS ||--o| PROFILLAR munosabati ko'rsatilgan. PROFILLAR jadvalidagi user_id ustunini SQL da qanday e'lon qilasiz? Bitta qatorda yozing (ustun ta'rifi ko'rinishida).",
        "exercise_type": "text_input",
        "expected_answer": "user_id INTEGER PRIMARY KEY REFERENCES users(id)",
        "hint": "1:1 uchun FK ustunini bir vaqtda PRIMARY KEY qilish yoki unga UNIQUE qo'shish kerak.",
        "difficulty_level": "Medium",
        "points": 12,
    },
    {
        "title": "Diagrammadan kodga o'tish tartibi",
        "description": "ER diagrammani ishlaydigan sxemaga aylantirish qadamlarini to'g'ri tartibga soling.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Mustaqil (FK siz) mohiyat jadvallarini yaratish",
            "1:N va 1:1 munosabatlar uchun FK ustunlarini qo'shish",
            "N:N munosabatlar uchun junction jadvallarni yaratish",
            "CHECK, UNIQUE va NOT NULL cheklovlarini qo'shish",
            "FK ustunlariga indeks yaratish",
        ],
        "correct_order": [
            "Mustaqil (FK siz) mohiyat jadvallarini yaratish",
            "1:N va 1:1 munosabatlar uchun FK ustunlarini qo'shish",
            "N:N munosabatlar uchun junction jadvallarni yaratish",
            "CHECK, UNIQUE va NOT NULL cheklovlarini qo'shish",
            "FK ustunlariga indeks yaratish",
        ],
        "hint": "FK ishlashi uchun ota jadval oldin mavjud bo'lishi kerak.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# L9 — Denormalizatsiya
# ═════════════════════════════════════════════════════════════════════════════
L9_TEXT = """\
<h3>Sakkiz dars normallashtirdik. Endi qachon buzish kerakligini gaplashamiz</h3>
<p>Halol boshlaylik: <strong>denormalizatsiya &mdash; bu optimizatsiya, dizayn emas.</strong> Uni normal sxemadan boshlab, o'lchangan muammoni ko'rgandan keyingina qo'llash kerak. "Menimcha bu tez ishlamaydi" &mdash; bu sabab emas. <code>EXPLAIN ANALYZE</code> natijasi &mdash; sabab.</p>
<p>Va ikkinchi halol gap: denormalizatsiya <em>bepul emas</em>. Siz <strong>o'qish tezligini</strong> sotib olib, evaziga <strong>ma'lumot yaxlitligi riskini</strong> to'laysiz. Takrorlangan qiymat &mdash; bu ertami-kechmi asl qiymat bilan mos kelmay qoladigan qiymat. Savol faqat shundaki: bu savdo sizga foydalimi?</p>

<h3>Qachon denormalizatsiya oqlanadi</h3>
<ul>
<li><strong>O'qish yozishdan 100 barobar ko'p.</strong> Postdagi like soni har sahifada ko'rsatiladi, lekin kuniga bir necha marta o'zgaradi.</li>
<li><strong>Agregat har safar butun jadvalni skanerlaydi.</strong> "Bu foydalanuvchining 40 000 ta postidagi jami like" &mdash; buni har so'rovda <code>COUNT</code> qilish ahmoqona.</li>
<li><strong>Hisobot real vaqtda bo'lishi shart emas.</strong> Kunlik dashboard 15 daqiqa eskirgan bo'lsa &mdash; hech kim sezmaydi. Bu <code>MATERIALIZED VIEW</code> uchun ideal holat.</li>
<li><strong>JOIN chuqurligi 5&ndash;6 jadvaldan oshgan</strong> va so'rov eng issiq yo'lda turibdi.</li>
</ul>

<h3>Qachon denormalizatsiya QILMASLIK kerak</h3>
<ul>
<li><strong>Loyihaning boshida.</strong> Sizda hali na ma'lumot, na o'lchov bor. Bu &mdash; sof taxmin.</li>
<li><strong>Oddiy indeks yetarli bo'lganda.</strong> Denormalizatsiyaga o'tishdan oldin har doim indeks, so'rovni qayta yozish va <code>EXPLAIN ANALYZE</code> ni sinab ko'ring. Amaliyotda "sekin so'rov" muammosining aksariyati yetishmayotgan indeksdan chiqadi.</li>
<li><strong>Ma'lumot moliyaviy yoki huquqiy ahamiyatga ega bo'lganda</strong> va uni sinxron ushlab turishga ishonchingiz bo'lmasa.</li>
</ul>

<h3>Uchta amaliy usul</h3>
<table>
<tr><th>Usul</th><th>Yangilanish</th><th>Ma'lumot yangiligi</th><th>Risk</th></tr>
<tr><td>Hisoblangan ustun + <code>TRIGGER</code></td><td>Avtomatik, o'sha tranzaksiyada</td><td>Doim aniq</td><td>Past &mdash; lekin har yozishga qo'shimcha yuk</td></tr>
<tr><td>Hisoblangan ustun + ilova kodi</td><td>Qo'lda, ilovada</td><td>Kodga bog'liq</td><td><strong>Yuqori</strong> &mdash; bitta unutilgan joy yetarli</td></tr>
<tr><td><code>MATERIALIZED VIEW</code></td><td><code>REFRESH</code> bilan</td><td>Eskirgan</td><td>Past &mdash; asl ma'lumot buzilmaydi</td></tr>
<tr><td>Tarixiy nusxa (narx_birlik)</td><td>Bir marta yoziladi</td><td>Ataylab "eski"</td><td>Nol &mdash; bu denormalizatsiya emas</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  S["So'rov sekin ishlayapti"] --> E["EXPLAIN ANALYZE bilan o'lchang"]
  E --> I{"Indeks yetishmayaptimi?"}
  I -->|"Ha"| IX["Indeks qo'shing. TUGADI —
denormalizatsiya kerak emas."]
  I -->|"Yo'q"| Q{"So'rovni qayta yozish
yordam beradimi?"}
  Q -->|"Ha"| QR["CTE / JOIN tartibi / window.
TUGADI."]
  Q -->|"Yo'q"| F{"Ma'lumot real vaqtda
bo'lishi shartmi?"}
  F -->|"Yo'q"| MV["MATERIALIZED VIEW +
jadval bo'yicha REFRESH"]
  F -->|"Ha"| TR["Hisoblangan ustun + TRIGGER
(ilova kodiga ISHONMANG)"]
</pre>

<h3>Eng muhim qoida</h3>
<p>Agar hisoblangan ustunni qo'shdingiz, u <strong>hech qachon</strong> ilova kodi tomonidan yangilanmasin. Ilovada o'nlab joy bor: web API, admin panel, import skripti, migratsiya, qo'lda tuzatish. Ulardan bittasi <code>UPDATE</code> ni unutadi &mdash; va sizda "like soni 47, aslida 52" degan xato paydo bo'ladi, uni esa hech kim yillar davomida sezmaydi.</p>
<p>Yechim: <code>TRIGGER</code>. U bir joyda yozilgan, tranzaksiya ichida ishlaydi va uni chetlab o'tib bo'lmaydi. Va albatta: hisoblangan qiymatni asl ma'lumot bilan solishtiruvchi <em>tekshiruv so'rovi</em> yozib qo'ying va uni vaqti-vaqti bilan ishga tushiring.</p>
"""

L9_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- Denormalizatsiya: hisoblangan ustun, TRIGGER va MATERIALIZED VIEW
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS layklar;
DROP TABLE IF EXISTS postlar;
DROP TABLE IF EXISTS foydalanuvchilar;

CREATE TABLE foydalanuvchilar (
    id       INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE postlar (
    id         INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    muallif_id INTEGER     NOT NULL REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    matn       TEXT        NOT NULL,
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- ── DENORMALIZATSIYA: hisoblangan ustun ──────────────────────────
    -- Asl manba — layklar jadvali. Bu ustun uning KESHI.
    -- Faqat trigger yangilaydi; ilova kodi bunga TEGMAYDI.
    layklar_soni INTEGER NOT NULL DEFAULT 0 CHECK (layklar_soni >= 0)
);

CREATE TABLE layklar (
    post_id       INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    foydalanuvchi_id INTEGER  NOT NULL REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bosilgan      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- bir odam bir postni bir marta layk qiladi
    PRIMARY KEY (post_id, foydalanuvchi_id)
);

CREATE INDEX layklar_foydalanuvchi_idx ON layklar (foydalanuvchi_id);

-- ─────────────────────────────────────────────────────────────────────
-- TRIGGER: hisoblangan ustunni AVTOMATIK va o'sha tranzaksiyada yangilaydi
-- ─────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION layklar_sonini_yangilash() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE postlar SET layklar_soni = layklar_soni + 1 WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE postlar SET layklar_soni = layklar_soni - 1 WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;   -- AFTER trigger uchun qaytariladigan qiymat ahamiyatsiz
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER layklar_soni_trigger
    AFTER INSERT OR DELETE ON layklar
    FOR EACH ROW EXECUTE FUNCTION layklar_sonini_yangilash();

-- ── Test ma'lumot ─────────────────────────────────────────────────────
INSERT INTO foydalanuvchilar (username) VALUES
    ('aziz'), ('dilnoza'), ('sardor'), ('madina');

INSERT INTO postlar (muallif_id, matn) VALUES
    (1, 'Bugun normalizatsiyani tugatdim!'),
    (1, 'BCNF haqiqatan ham qiyin ekan.'),
    (2, 'Junction jadval — eng foydali tushuncha.');

INSERT INTO layklar (post_id, foydalanuvchi_id) VALUES
    (1, 2), (1, 3), (1, 4),
    (2, 3),
    (3, 1), (3, 4);

-- Trigger avtomatik ishladi — hech kim qo'lda UPDATE yozmadi:
SELECT id, LEFT(matn, 40) AS post, layklar_soni FROM postlar ORDER BY id;

-- Layk olib tashlansa ham hisob to'g'ri qoladi:
DELETE FROM layklar WHERE post_id = 1 AND foydalanuvchi_id = 4;
SELECT id, layklar_soni FROM postlar WHERE id = 1;   -- 3 -> 2

-- ─────────────────────────────────────────────────────────────────────
-- TEKSHIRUV SO'ROVI: keshni asl manba bilan solishtirish.
-- Buni cron bilan haftada bir marta ishga tushiring. Natija bo'sh
-- bo'lishi kerak; bo'sh bo'lmasa — trigger yoki migratsiyada muammo bor.
-- ─────────────────────────────────────────────────────────────────────
SELECT p.id,
       p.layklar_soni       AS keshdagi_qiymat,
       COUNT(l.post_id)     AS haqiqiy_qiymat
FROM postlar p
LEFT JOIN layklar l ON l.post_id = p.id
GROUP BY p.id, p.layklar_soni
HAVING p.layklar_soni <> COUNT(l.post_id);
-- Bo'sh natija = kesh to'g'ri.

-- ─────────────────────────────────────────────────────────────────────
-- NIMA UCHUN ILOVA KODIGA ISHONMASLIK KERAK — jonli namoyish.
-- Tasavvur qiling, admin panel "spam layklarni tozalash" skriptini
-- ishga tushirdi va layklar_soni ni yangilashni UNUTDI:
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE layklar DISABLE TRIGGER layklar_soni_trigger;
DELETE FROM layklar WHERE post_id = 3;           -- trigger o'chirilgan!
ALTER TABLE layklar ENABLE TRIGGER layklar_soni_trigger;

-- Endi tekshiruv so'rovi muammoni TOPADI:
SELECT p.id, p.layklar_soni AS keshdagi, COUNT(l.post_id) AS haqiqiy
FROM postlar p
LEFT JOIN layklar l ON l.post_id = p.id
GROUP BY p.id, p.layklar_soni
HAVING p.layklar_soni <> COUNT(l.post_id);
-- post 3: keshda 2, haqiqatda 0. Aynan shu — denormalizatsiyaning narxi.

-- Tuzatish:
UPDATE postlar p
SET layklar_soni = sub.haqiqiy
FROM (SELECT p2.id, COUNT(l.post_id) AS haqiqiy
      FROM postlar p2 LEFT JOIN layklar l ON l.post_id = p2.id
      GROUP BY p2.id) sub
WHERE p.id = sub.id AND p.layklar_soni <> sub.haqiqiy;

-- ─────────────────────────────────────────────────────────────────────
-- MATERIALIZED VIEW: og'ir hisobot uchun eng xavfsiz denormalizatsiya.
-- Asl jadvallar toza qoladi, kesh esa alohida obyektda yashaydi.
-- ─────────────────────────────────────────────────────────────────────
DROP MATERIALIZED VIEW IF EXISTS muallif_statistikasi;

CREATE MATERIALIZED VIEW muallif_statistikasi AS
SELECT f.id                        AS muallif_id,
       f.username,
       COUNT(DISTINCT p.id)        AS postlar_soni,
       COALESCE(SUM(p.layklar_soni), 0) AS jami_layklar,
       MAX(p.yaratilgan)           AS oxirgi_post
FROM foydalanuvchilar f
LEFT JOIN postlar p ON p.muallif_id = f.id
GROUP BY f.id, f.username;

-- REFRESH uchun UNIQUE indeks kerak (CONCURRENTLY ishlashi uchun)
CREATE UNIQUE INDEX muallif_statistikasi_pk ON muallif_statistikasi (muallif_id);

SELECT * FROM muallif_statistikasi ORDER BY jami_layklar DESC;

-- Yangi ma'lumot qo'shamiz — VIEW hali ESKI holatda qoladi:
INSERT INTO postlar (muallif_id, matn) VALUES (3, 'Denormalizatsiya — ehtiyotkorlik bilan.');
SELECT username, postlar_soni FROM muallif_statistikasi WHERE username = 'sardor';  -- 0

REFRESH MATERIALIZED VIEW muallif_statistikasi;
SELECT username, postlar_soni FROM muallif_statistikasi WHERE username = 'sardor';  -- 1

-- XULOSA: avval indeks, keyin so'rovni qayta yozish, keyin
-- MATERIALIZED VIEW, va faqat oxirida trigger bilan hisoblangan ustun.
"""

L9_EX = [
    {
        "title": "Denormalizatsiyadan oldin nima qilinadi?",
        "description": "So'rov sekin ishlayapti. Denormalizatsiyaga o'tishdan OLDIN qaysi qadamlarni sinab ko'rish kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "EXPLAIN ANALYZE bilan sekinlik sababini o'lchash",
            "Yetishmayotgan indekslarni qo'shish",
            "So'rovni qayta yozish (JOIN tartibi, CTE, window funksiya)",
            "Darhol hisoblangan ustun qo'shib, uni ilova kodidan yangilash",
        ],
        "correct_answers": "A,B,C",
        "is_multiple_select": True,
        "hint": "Bittasi — aynan oxirgi chora, birinchi emas.",
        "explanation": "Avval o'lchash, keyin indeks, keyin so'rovni qayta yozish. Amaliyotda sekin so'rovlarning aksariyati yetishmayotgan indeksdan kelib chiqadi. Hisoblangan ustun — oxirgi chora, va uni ilova kodi emas, trigger yangilashi kerak.",
        "difficulty_level": "Medium",
        "points": 12,
    },
    {
        "title": "Hisoblangan ustunni kim yangilaydi?",
        "description": "postlar.layklar_soni kabi hisoblangan ustunni yangilash uchun eng ishonchli mexanizm nima? Bitta so'z bilan yozing.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "trigger",
        "hint": "U bitta joyda yoziladi, tranzaksiya ichida ishlaydi va uni chetlab o'tib bo'lmaydi.",
        "explanation": "TRIGGER — eng ishonchli variant, chunki u bazaning o'zida yashaydi va bazaga yozadigan HAR QANDAY mijoz (web API, skript, qo'lda so'rov) uchun bir xil ishlaydi. Ilova kodiga tayanish esa ertami-kechmi keshning asl ma'lumotdan farq qilishiga olib keladi.",
        "difficulty_level": "Medium",
        "points": 10,
    },
    {
        "title": "narx_birlik denormalizatsiyami?",
        "description": "buyurtma_elementlari.narx_birlik ustuni denormalizatsiya hisoblanadimi? Javobingizni 1-2 jumla bilan asoslang.",
        "exercise_type": "text_input",
        "expected_answer": "Yo'q. narx_birlik — mahsulot narxining keshi emas, balki alohida tarixiy fakt: sotuv paytidagi narx. Mahsulot narxi keyin o'zgarsa ham u o'zgarmasligi kerak, shuning uchun bu takrorlanish emas, to'g'ri dizayn.",
        "hint": "Kesh asl qiymat o'zgarganda yangilanishi kerak. narx_birlik yangilanishi kerakmi?",
        "difficulty_level": "Hard",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# R2 — Ijtimoiy tarmoq DB sxemasi (takrorlash)
# ═════════════════════════════════════════════════════════════════════════════
R2_TEXT = """\
<h2>R2 &mdash; Modul 2 takrorlash: ijtimoiy tarmoq sxemasi</h2>
<p>6&ndash;9-darslarda o'rgangan hamma narsani &mdash; kalit strategiyalari, <code>ON DELETE</code>, cheklovlar, ER diagramma va denormalizatsiya &mdash; bitta murakkab sxemada birlashtiramiz.</p>
<p>Vazifa: Instagram/Twitter tipidagi ijtimoiy tarmoq uchun ma'lumotlar bazasi. Bu sxemada oldingi loyihalarda uchramagan bitta yangi qiyinchilik bor.</p>

<h3>Yangi qiyinchilik: self-referential N:N</h3>
<p>Obuna (follow) munosabatini ko'ring: <strong>foydalanuvchi foydalanuvchiga</strong> obuna bo'ladi. Ya'ni N:N munosabatning ikkala tomoni ham bitta jadval &mdash; <code>foydalanuvchilar</code>.</p>
<p>Junction jadval bunday ko'rinadi:</p>
<ul>
<li><code>obunachi_id</code> &rarr; <code>foydalanuvchilar(id)</code> &mdash; kim obuna bo'lyapti</li>
<li><code>obuna_bolingan_id</code> &rarr; <code>foydalanuvchilar(id)</code> &mdash; kimga obuna bo'lyapti</li>
<li><code>PRIMARY KEY (obunachi_id, obuna_bolingan_id)</code></li>
<li><code>CHECK (obunachi_id &lt;&gt; obuna_bolingan_id)</code> &mdash; <strong>o'zingizga obuna bo'lolmaysiz</strong></li>
</ul>
<p>Ikkala FK ham bitta jadvalga ishora qilgani uchun ustun nomlari <em>rolni</em> ifodalashi shart. <code>user_id_1</code> va <code>user_id_2</code> deb nomlash &mdash; olti oydan keyin qaysi biri kim ekanligini hech kim eslay olmasligini kafolatlaydi.</p>
<p>Yana bir muhim nuqta: obuna &mdash; <strong>yo'naltirilgan</strong> (directed) munosabat. Aziz Dilnozaga obuna bo'lishi mumkin, Dilnoza esa Azizga yo'q. Bu do'stlik emas &mdash; do'stlikda ikkala yo'nalish ham kerak bo'lardi.</p>

<h3>Kutilayotgan sxema</h3>
<table>
<tr><th>Jadval</th><th>Maqsad</th><th>Diqqat qiladigan joy</th></tr>
<tr><td><code>foydalanuvchilar</code></td><td>Akkaunt</td><td>username UNIQUE, soft delete</td></tr>
<tr><td><code>profillar</code></td><td>Bio, avatar &mdash; 1:1</td><td>PK = FK</td></tr>
<tr><td><code>postlar</code></td><td>Nashr</td><td>muallif_id 1:N, layklar_soni keshi</td></tr>
<tr><td><code>izohlar</code></td><td>Post ostidagi izoh</td><td>ota_izoh_id &mdash; o'ziga havola (threaded)</td></tr>
<tr><td><code>layklar</code></td><td>Kim nimani layk qildi</td><td>kompozit PK, N:N</td></tr>
<tr><td><code>obunalar</code></td><td>Kim kimga obuna</td><td>self-referential N:N + CHECK</td></tr>
</table>

<pre class="mermaid">
erDiagram
    FOYDALANUVCHILAR ||--o| PROFILLAR : "ega"
    FOYDALANUVCHILAR ||--o{ POSTLAR : "yozadi"
    FOYDALANUVCHILAR ||--o{ IZOHLAR : "izohlaydi"
    FOYDALANUVCHILAR ||--o{ LAYKLAR : "bosadi"
    FOYDALANUVCHILAR ||--o{ OBUNALAR : "obunachi"
    FOYDALANUVCHILAR ||--o{ OBUNALAR : "obuna_bolingan"
    POSTLAR ||--o{ IZOHLAR : "ostida"
    POSTLAR ||--o{ LAYKLAR : "oladi"
    IZOHLAR ||--o{ IZOHLAR : "javob"
</pre>

<h3>Sizdan javob kutiladigan qiyin savollar</h3>
<ol>
<li>Foydalanuvchi akkauntini o'chirsa, uning postlari, izohlari va layklari bilan nima bo'lishi kerak? Har biri uchun <code>CASCADE</code> / <code>RESTRICT</code> / <code>SET NULL</code> dan qaysi birini tanlaysiz va nega?</li>
<li><code>izohlar.ota_izoh_id</code> o'zi turgan jadvalga ishora qiladi. Ota izoh o'chirilsa, javoblar bilan nima bo'ladi &mdash; <code>CASCADE</code> (butun tarmoq o'chadi) mi, <code>SET NULL</code> (javoblar yuqoriga ko'tariladi) mi?</li>
<li>"Aziz obuna bo'lganlarning postlari" (lenta) so'rovini qanday yozasiz?</li>
<li>Obunachilar sonini <code>COUNT</code> bilan hisoblaysizmi yoki hisoblangan ustunga keshlaysizmi? Qaysi hollarda birinchisi yetarli?</li>
</ol>
"""

R2_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- R2 — Ijtimoiy tarmoq sxemasi: START KIT
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS obunalar;
DROP TABLE IF EXISTS layklar;
DROP TABLE IF EXISTS izohlar;
DROP TABLE IF EXISTS postlar;
DROP TABLE IF EXISTS profillar;
DROP TABLE IF EXISTS foydalanuvchilar;

CREATE TABLE foydalanuvchilar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username        VARCHAR(30)  NOT NULL,
    email           VARCHAR(120) NOT NULL,
    parol_hash      VARCHAR(255) NOT NULL,
    royxatdan       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    ochirilgan_sana TIMESTAMPTZ,
    CONSTRAINT foydalanuvchilar_username_uq UNIQUE (username),
    CONSTRAINT foydalanuvchilar_email_uq    UNIQUE (email),
    CONSTRAINT foydalanuvchilar_username_fmt
        CHECK (username ~ '^[a-z0-9_]{3,30}$')
);

-- 1:1 — profil ixtiyoriy, PK = FK
CREATE TABLE profillar (
    foydalanuvchi_id INTEGER PRIMARY KEY
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    tolik_ism        VARCHAR(80),
    bio              VARCHAR(300),
    avatar_url       VARCHAR(255),
    sayt             VARCHAR(255)
);

-- 1:N — postlar
CREATE TABLE postlar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    muallif_id   INTEGER     NOT NULL
                 REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    matn         VARCHAR(2200) NOT NULL,
    rasm_url     VARCHAR(255),
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- denormalizatsiya: trigger yangilaydi (9-darsga qarang)
    layklar_soni INTEGER     NOT NULL DEFAULT 0 CHECK (layklar_soni >= 0),
    CONSTRAINT postlar_matn_bosh_emas CHECK (LENGTH(TRIM(matn)) > 0)
);

-- SELF-REFERENTIAL 1:N — izohga javob (threaded comments)
CREATE TABLE izohlar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id      INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif_id   INTEGER     NOT NULL
                 REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    -- o'z jadvaliga havola. NULL = bu yuqori darajadagi izoh.
    -- CASCADE: ota izoh o'chsa, butun javoblar tarmog'i ham o'chadi.
    ota_izoh_id  INTEGER     REFERENCES izohlar(id) ON DELETE CASCADE,
    matn         VARCHAR(1000) NOT NULL,
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- N:N — layklar
CREATE TABLE layklar (
    post_id          INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    foydalanuvchi_id INTEGER     NOT NULL
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bosilgan         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (post_id, foydalanuvchi_id)
);

-- ─────────────────────────────────────────────────────────────────────
-- SELF-REFERENTIAL N:N — obunalar. Bu darsning asosiy yangiligi.
-- Ikkala FK ham bitta jadvalga ishora qiladi, shuning uchun ustun
-- nomlari ROLNI ifodalaydi: kim obuna bo'ldi va kimga.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE obunalar (
    obunachi_id        INTEGER NOT NULL
                       REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    obuna_bolingan_id  INTEGER NOT NULL
                       REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    boshlangan         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (obunachi_id, obuna_bolingan_id),
    -- O'ZINGIZGA OBUNA BO'LOLMAYSIZ — busiz sxema jimgina buziladi
    CONSTRAINT obunalar_ozi_emas CHECK (obunachi_id <> obuna_bolingan_id)
);

-- Teskari yo'nalish uchun indeks: "menga kim obuna?" so'rovi uchun
CREATE INDEX obunalar_obuna_bolingan_idx ON obunalar (obuna_bolingan_id);
CREATE INDEX izohlar_post_idx            ON izohlar (post_id);
CREATE INDEX izohlar_ota_idx             ON izohlar (ota_izoh_id);
CREATE INDEX layklar_foydalanuvchi_idx   ON layklar (foydalanuvchi_id);
CREATE INDEX postlar_muallif_vaqt_idx    ON postlar (muallif_id, yaratilgan DESC);

-- ── Test ma'lumot ─────────────────────────────────────────────────────
INSERT INTO foydalanuvchilar (username, email, parol_hash) VALUES
    ('aziz',    'aziz@soc.uz',    'hash1'),
    ('dilnoza', 'dilnoza@soc.uz', 'hash2'),
    ('sardor',  'sardor@soc.uz',  'hash3'),
    ('madina',  'madina@soc.uz',  'hash4');

INSERT INTO profillar (foydalanuvchi_id, tolik_ism, bio) VALUES
    (1, 'Aziz Karimov', 'Backend dasturchi'),
    (2, 'Dilnoza Rasulova', 'Data analitik');

INSERT INTO postlar (muallif_id, matn) VALUES
    (1, 'Birinchi post!'),
    (2, 'SQL o''rganyapman'),
    (2, 'Junction jadval — kashfiyot'),
    (3, 'Salom hammaga');

INSERT INTO izohlar (post_id, muallif_id, ota_izoh_id, matn) VALUES
    (1, 2, NULL, 'Tabriklaymiz!'),
    (1, 3, 1,    'Qo''shilaman'),      -- 1-izohga javob
    (2, 1, NULL, 'Zo''r mavzu');

INSERT INTO layklar (post_id, foydalanuvchi_id) VALUES
    (1, 2), (1, 3), (2, 1), (3, 1), (3, 4);

INSERT INTO obunalar (obunachi_id, obuna_bolingan_id) VALUES
    (1, 2),   -- aziz -> dilnoza
    (1, 3),   -- aziz -> sardor
    (2, 1),   -- dilnoza -> aziz (o'zaro obuna)
    (4, 2),   -- madina -> dilnoza
    (3, 2);   -- sardor -> dilnoza

-- O'ziga obuna bo'lish bloklanadi:
-- INSERT INTO obunalar (obunachi_id, obuna_bolingan_id) VALUES (1, 1);
-- ERROR:  new row violates check constraint "obunalar_ozi_emas"

-- ── Sxemani tasdiqlovchi hisobotlar ───────────────────────────────────

-- 1) LENTA: aziz obuna bo'lganlarning postlari
SELECT p.id, f.username AS muallif, p.matn, p.yaratilgan
FROM obunalar o
JOIN postlar p ON p.muallif_id = o.obuna_bolingan_id
JOIN foydalanuvchilar f ON f.id = p.muallif_id
WHERE o.obunachi_id = (SELECT id FROM foydalanuvchilar WHERE username = 'aziz')
ORDER BY p.yaratilgan DESC;

-- 2) Har foydalanuvchining obunachilari va obunalari soni
SELECT f.username,
       (SELECT COUNT(*) FROM obunalar WHERE obuna_bolingan_id = f.id) AS obunachilar,
       (SELECT COUNT(*) FROM obunalar WHERE obunachi_id = f.id)       AS obunalari
FROM foydalanuvchilar f
ORDER BY obunachilar DESC;

-- 3) O'ZARO obuna (do'stlar) — self JOIN
SELECT a.username AS birinchi, b.username AS ikkinchi
FROM obunalar o1
JOIN obunalar o2
  ON o1.obunachi_id = o2.obuna_bolingan_id
 AND o1.obuna_bolingan_id = o2.obunachi_id
JOIN foydalanuvchilar a ON a.id = o1.obunachi_id
JOIN foydalanuvchilar b ON b.id = o1.obuna_bolingan_id
WHERE o1.obunachi_id < o1.obuna_bolingan_id;   -- juftlik ikki marta chiqmasin

-- 4) Threaded izohlar — recursive CTE bilan
WITH RECURSIVE izoh_daraxti AS (
    SELECT id, post_id, muallif_id, ota_izoh_id, matn, 0 AS daraja
    FROM izohlar WHERE post_id = 1 AND ota_izoh_id IS NULL
    UNION ALL
    SELECT i.id, i.post_id, i.muallif_id, i.ota_izoh_id, i.matn, d.daraja + 1
    FROM izohlar i
    JOIN izoh_daraxti d ON i.ota_izoh_id = d.id
)
SELECT REPEAT('  ', daraja) || matn AS izoh, daraja
FROM izoh_daraxti
ORDER BY daraja, id;
"""

R2_EX = [
    {
        "title": "Self-referential N:N da majburiy cheklov",
        "description": "obunalar(obunachi_id, obuna_bolingan_id) jadvalida ikkala FK ham foydalanuvchilar jadvaliga ishora qiladi. Qaysi cheklov bu sxemada MAJBURIY va uni ko'pincha unutib qo'yishadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "CHECK (obunachi_id <> obuna_bolingan_id) — o'zingizga obuna bo'lish taqiqlanadi",
            "UNIQUE (obunachi_id) — bir odam faqat bitta obunaga ega bo'lsin",
            "NOT NULL boshlangan ustuniga",
            "FOREIGN KEY ni olib tashlash, chunki jadval o'ziga ishora qilyapti",
        ],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Ikkala ustun ham bitta jadvalga ishora qilganda, ular teng bo'lib qolishi mumkin.",
        "explanation": "Self-referential munosabatda ikkala FK bir xil qatorga ishora qilishi mumkin. CHECK (obunachi_id <> obuna_bolingan_id) busiz foydalanuvchi o'ziga obuna bo'lib, obunachilar sonini soxtalashtira oladi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "Ijtimoiy tarmoq sxemasini qurish tartibi",
        "description": "Ijtimoiy tarmoq sxemasini yaratish qadamlarini to'g'ri tartibga soling (FK bog'liqliklarini hisobga oling).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "foydalanuvchilar jadvali (hech kimga bog'liq emas)",
            "profillar — foydalanuvchilar bilan 1:1 (PK = FK)",
            "postlar — foydalanuvchilar bilan 1:N",
            "izohlar va layklar — postlarga bog'liq",
            "obunalar — self-referential N:N + CHECK",
            "Indekslar: teskari yo'nalish va lenta so'rovlari uchun",
        ],
        "correct_order": [
            "foydalanuvchilar jadvali (hech kimga bog'liq emas)",
            "profillar — foydalanuvchilar bilan 1:1 (PK = FK)",
            "postlar — foydalanuvchilar bilan 1:N",
            "izohlar va layklar — postlarga bog'liq",
            "obunalar — self-referential N:N + CHECK",
            "Indekslar: teskari yo'nalish va lenta so'rovlari uchun",
        ],
        "hint": "FK ishlashi uchun ota jadval avval yaratilgan bo'lishi kerak; indekslar oxirida.",
        "explanation": "",
        "difficulty_level": "Medium",
        "points": 12,
    },
]

R2_TASK = {
    "task_title": "🔁 R2: Ijtimoiy tarmoq DB sxemasi",
    "task_description": (
        "Instagram/Twitter tipidagi ijtimoiy tarmoq uchun to'liq sxema loyihalang. "
        "Asosiy qiyinchilik — self-referential N:N (obunalar) va self-referential "
        "1:N (izohga javob). Natija — ishga tushiriladigan .sql fayl va ER diagramma."
    ),
    "task_requirements": (
        "• 6 ta jadval: foydalanuvchilar, profillar, postlar, izohlar, layklar, obunalar\n"
        "• profillar — foydalanuvchilar bilan 1:1 (PK = FK yoki UNIQUE FK)\n"
        "• obunalar — self-referential N:N; ustun nomlari ROLNI ifodalasin "
        "(obunachi_id / obuna_bolingan_id, user_id_1 / user_id_2 EMAS)\n"
        "• CHECK (obunachi_id <> obuna_bolingan_id) — o'ziga obuna bo'lish taqiqlansin\n"
        "• izohlar.ota_izoh_id — o'z jadvaliga havola (threaded izohlar)\n"
        "• layklar — kompozit PK, bir odam bir postni bir marta layk qiladi\n"
        "• username uchun UNIQUE va format CHECK (regex)\n"
        "• Har bir FK uchun ON DELETE strategiyasini tanlang va -- komment bilan IZOHLANG\n"
        "• postlar.layklar_soni — trigger bilan yangilanadigan hisoblangan ustun\n"
        "• Keshni asl ma'lumot bilan solishtiruvchi tekshiruv so'rovi yozing\n"
        "• Barcha FK ustunlariga va lenta so'rovi uchun indekslar\n"
        "• Test ma'lumot: 6+ foydalanuvchi, 15+ post, 20+ izoh (kamida 2 daraja "
        "chuqurlikda), 30+ layk, 15+ obuna\n"
        "• 6 ta hisobot: foydalanuvchi lentasi; o'zaro obunalar (self JOIN); "
        "TOP-5 mashhur post; obunachilari eng ko'p 3 foydalanuvchi; threaded izohlar "
        "(recursive CTE); hech kim obuna bo'lmagan foydalanuvchilar\n"
        "• Sxemani mermaid erDiagram ko'rinishida chizib, .md faylga qo'shing"
    ),
    "task_technologies": (
        "PostgreSQL, self-referential FK, junction jadval, kompozit kalit, CHECK, "
        "UNIQUE, partial/composite index, TRIGGER, recursive CTE, self JOIN, mermaid erDiagram"
    ),
    "task_deadline_days": 7,
}


# ═════════════════════════════════════════════════════════════════════════════
# L10 — E-commerce sxemasini qayta loyihalash (course 41 capstone tanqidi)
# ═════════════════════════════════════════════════════════════════════════════
L10_TEXT = """\
<h3>O'z kodingizni tanqid qilish vaqti</h3>
<p>"SQL va PostgreSQL Asoslari" kursining yakuniy loyihasida siz e-commerce tahlil tizimini qurgan edingiz. O'sha sxema shunday ko'rinardi:</p>

<pre class="mermaid">
erDiagram
    KATEGORIYALAR ||--o{ MAHSULOTLAR : "guruhlaydi"
    EC_MIJOZLAR ||--o{ BUYURTMALAR : "beradi"
    BUYURTMALAR ||--o{ BUYURTMA_ELEMENTLARI : "tarkibi"
    MAHSULOTLAR ||--o{ BUYURTMA_ELEMENTLARI : "sotiladi"

    KATEGORIYALAR {
        serial id PK
        varchar nomi UK
    }
    MAHSULOTLAR {
        serial id PK
        int kategoriya_id FK
        varchar nomi
        numeric narx
        int zaxira
        timestamptz yaratilgan
    }
    EC_MIJOZLAR {
        serial id PK
        varchar ism
        varchar email UK
        varchar shahar
        timestamptz royxatdan
    }
    BUYURTMALAR {
        serial id PK
        int mijoz_id FK
        varchar holat
        timestamptz yaratilgan
    }
    BUYURTMA_ELEMENTLARI {
        serial id PK
        int buyurtma_id FK
        int mahsulot_id FK
        int miqdor
        numeric narx_birlik
    }
</pre>

<p>Bu sxema o'sha kurs uchun <em>to'liq yetarli</em> edi: uning maqsadi <code>JOIN</code>, <code>GROUP BY</code> va window funksiyalarni o'rgatish edi, sxema dizayni emas. Endi esa sizda dizaynerning ko'zi bor. Xuddi shu sxemaga qaytib qaraymiz.</p>

<h3>Avval &mdash; nima to'g'ri qilingan</h3>
<ul>
<li><strong><code>buyurtma_elementlari.narx_birlik</code></strong> &mdash; eng muhim to'g'ri qaror. Bu mahsulot narxining nusxasi emas, balki <em>sotuv paytidagi tarixiy narx</em>. Mahsulot narxi ertaga oshsa, kechagi chek o'zgarmaydi. 3-darsda ko'rganimizdek, bu denormalizatsiya emas &mdash; bu boshqa fakt.</li>
<li><strong><code>ON DELETE RESTRICT</code> mahsulot va mijozga</strong> &mdash; sotuv tarixini himoya qiladi.</li>
<li><strong><code>ON DELETE CASCADE</code> buyurtma elementlariga</strong> &mdash; to'g'ri: element buyurtmasiz ma'nosiz.</li>
<li><strong><code>CHECK (holat IN (...))</code></strong> &mdash; holat ustuni matn tuzog'iga aylanmagan.</li>
<li><strong>Pul <code>NUMERIC</code> da, vaqt <code>TIMESTAMPTZ</code> da</strong> &mdash; <code>FLOAT</code> va <code>TIMESTAMP</code> emas. To'g'ri.</li>
</ul>

<h3>Endi &mdash; oltita jiddiy muammo</h3>

<h4>1. <code>buyurtma_elementlari</code> da dublikatga yo'l ochiq</h4>
<p>Jadvalda <code>id SERIAL PRIMARY KEY</code> bor, lekin <code>UNIQUE (buyurtma_id, mahsulot_id)</code> yo'q. Ya'ni bitta buyurtmada bitta mahsulot <strong>ikki marta alohida qator bo'lib</strong> tura oladi &mdash; ehtimol turli narx bilan. Bu haqiqiy xato: hisobotlaringiz jimgina noto'g'ri natija bera boshlaydi. 5-darsda ko'rganimizdek, surrogate <code>id</code> qo'shilganda <code>UNIQUE</code> ni <em>albatta</em> qaytarish kerak.</p>

<h4>2. <code>ec_mijozlar.shahar VARCHAR(50)</code> &mdash; erkin matn</h4>
<p>"Toshkent", "toshkent", "Tashkent", "Toshkent sh." &mdash; bular baza uchun to'rtta har xil shahar. Viloyat bo'yicha hisobot esa umuman imkonsiz, chunki viloyat haqida ma'lumot yo'q. 2-darsda ko'rganimizdek, bu tranzitiv bog'liqlik: <code>shahar &rarr; viloyat</code>. Yechim &mdash; <code>shaharlar</code> lug'at jadvali.</p>

<h4>3. Yetkazib berish manzili umuman yo'q</h4>
<p>Real e-commerce da buyurtma qayergadir yetkaziladi. Va bu &mdash; nozik joy: manzilni <code>mijozlar</code> jadvalidan <code>JOIN</code> qilib olish <strong>xato</strong>. Mijoz keyingi yil ko'chib ketsa, sizning uch yillik yetkazib berish tarixingiz bir zumda soxtalashadi. Manzil buyurtma qatoriga <em>nusxa</em> sifatida yozilishi kerak &mdash; xuddi <code>narx_birlik</code> kabi.</p>

<h4>4. <code>NUMERIC(10,2)</code> &mdash; so'm uchun kichik</h4>
<p><code>NUMERIC(10,2)</code> maksimal 99 999 999.99 ni saqlaydi &mdash; ya'ni 100 million so'mdan kam. Bitta noutbuk sig'adi, lekin qimmat texnika, mebel to'plami yoki yirik ulgurji buyurtma <em>sig'maydi</em> va baza <code>numeric field overflow</code> xatosi bilan yiqiladi. So'mda ishlaydigan tizim uchun kamida <code>NUMERIC(14,2)</code> kerak.</p>

<h4>5. <code>holat</code> ikkita turli tushunchani aralashtiradi</h4>
<p><code>'kutmoqda'</code>, <code>'tasdiqlangan'</code>, <code>'yetkazildi'</code>, <code>'bekor'</code> &mdash; bularda buyurtmaning <em>bajarilish</em> holati ham, <em>to'lov</em> holati ham yashiringan. "Yetkazildi, lekin hali to'lanmagan" holatini bu sxemada ifodalab bo'lmaydi. To'lov &mdash; alohida mohiyat: uning summasi, usuli, vaqti va tranzaksiya ID si bor.</p>

<h4>6. <code>mahsulotlar.zaxira</code> &mdash; yashirin denormalizatsiya</h4>
<p>Zaxira &mdash; bu aslida <em>hisoblangan qiymat</em>: kirim minus chiqim. Uni bitta ustunda saqlash o'zi xato emas (9-darsda ko'rganimizdek, bu maqbul optimizatsiya), lekin uni shunchaki <code>UPDATE</code> bilan o'zgartirish tarixni yo'q qiladi: "zaxira nega 3 ta kam?" degan savolga hech qachon javob bera olmaysiz. To'g'ri yechim &mdash; <code>zaxira_harakatlari</code> jadvali va uning ustidagi kesh.</p>

<h3>Qo'shimcha kichik kamchiliklar</h3>
<table>
<tr><th>Muammo</th><th>Oqibati</th><th>Yechim</th></tr>
<tr><td>Kategoriya tekis (parent yo'q)</td><td>"Telefonlar &rarr; Smartfonlar" ierarxiyasi qurib bo'lmaydi</td><td><code>ota_id</code> &mdash; self-referential 1:N</td></tr>
<tr><td>Mahsulotni o'chirib bo'lmaydi (RESTRICT)</td><td>Katalogda eskirgan tovar abadiy qoladi</td><td><code>faol BOOLEAN</code> yoki <code>ochirilgan_sana</code></td></tr>
<tr><td><code>yangilangan</code> ustuni yo'q</td><td>Nima qachon o'zgargani noma'lum</td><td><code>yangilangan TIMESTAMPTZ</code> + trigger</td></tr>
<tr><td>FK larga indeks yo'q</td><td>Har <code>JOIN</code> va <code>DELETE</code> to'liq skanerlash</td><td><code>CREATE INDEX</code> har FK ga</td></tr>
<tr><td><code>VARCHAR(50)</code> ism uchun</td><td>Uzun ism kesiladi yoki xato beradi</td><td><code>VARCHAR(120)</code> yoki <code>TEXT</code></td></tr>
</table>

<h3>v2 sxemasi</h3>
<pre class="mermaid">
erDiagram
    SHAHARLAR ||--o{ MIJOZLAR : "joylashgan"
    KATEGORIYALAR ||--o{ KATEGORIYALAR : "ota"
    KATEGORIYALAR ||--o{ MAHSULOTLAR : "guruhlaydi"
    MIJOZLAR ||--o{ MANZILLAR : "saqlaydi"
    MIJOZLAR ||--o{ BUYURTMALAR : "beradi"
    BUYURTMALAR ||--|{ BUYURTMA_ELEMENTLARI : "tarkibi"
    MAHSULOTLAR ||--o{ BUYURTMA_ELEMENTLARI : "sotiladi"
    BUYURTMALAR ||--o{ TOLOVLAR : "to_lanadi"
    MAHSULOTLAR ||--o{ ZAXIRA_HARAKATLARI : "harakat"
</pre>
<p>Diqqat qiling: <code>manzillar</code> jadvali <em>bor</em>, lekin <code>buyurtmalar</code> unga FK bilan bog'lanmaydi &mdash; buyurtma manzil <strong>matnini nusxa</strong> qilib saqlaydi. Bu ataylab qilingan: manzil keyin o'zgarsa ham, yetkazib berilgan joy tarixi o'zgarmasligi kerak.</p>
"""

L10_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- E-commerce sxemasi v2 — Asoslari kursidagi capstone sxemasini
-- ushbu kursdagi hamma narsani qo'llab qayta loyihalash
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS zaxira_harakatlari;
DROP TABLE IF EXISTS tolovlar;
DROP TABLE IF EXISTS buyurtma_elementlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS manzillar;
DROP TABLE IF EXISTS mahsulotlar;
DROP TABLE IF EXISTS kategoriyalar;
DROP TABLE IF EXISTS mijozlar;
DROP TABLE IF EXISTS shaharlar;

-- ── TUZATISH 2: shahar erkin matn emas, lug'at jadval (3NF) ───────────
CREATE TABLE shaharlar (
    id       INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi     VARCHAR(60) NOT NULL,
    viloyati VARCHAR(60) NOT NULL,
    CONSTRAINT shaharlar_nomi_viloyat_uq UNIQUE (nomi, viloyati)
);

CREATE TABLE mijozlar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- TUZATISH: ism uchun yetarli uzunlik
    ism             VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL,
    shahar_id       INTEGER      REFERENCES shaharlar(id) ON DELETE SET NULL,
    royxatdan       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- TUZATISH: soft delete — mijozni o'chirmasdan "yo'q" qilish
    ochirilgan_sana TIMESTAMPTZ,
    CONSTRAINT mijozlar_email_uq  UNIQUE (email),
    CONSTRAINT mijozlar_email_fmt CHECK (email LIKE '%_@_%._%')
);

-- ── TUZATISH: kategoriya ierarxiyasi (self-referential 1:N) ───────────
CREATE TABLE kategoriyalar (
    id     INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ota_id INTEGER     REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi   VARCHAR(60) NOT NULL,
    CONSTRAINT kategoriyalar_nomi_uq UNIQUE (nomi),
    -- o'zi o'zining otasi bo'lolmaydi
    CONSTRAINT kategoriyalar_ota_ozi_emas CHECK (ota_id IS NULL OR ota_id <> id)
);

CREATE TABLE mahsulotlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kategoriya_id INTEGER       NOT NULL REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi          VARCHAR(150)  NOT NULL,
    -- TUZATISH 4: NUMERIC(10,2) so'm uchun kichik -> NUMERIC(14,2)
    narx          NUMERIC(14,2) NOT NULL CHECK (narx > 0),
    -- TUZATISH 6: zaxira — zaxira_harakatlari ustidagi KESH.
    -- Uni faqat trigger yangilaydi, ilova kodi emas.
    zaxira        INTEGER       NOT NULL DEFAULT 0 CHECK (zaxira >= 0),
    -- TUZATISH: katalogdan olib tashlash uchun soft delete
    faol          BOOLEAN       NOT NULL DEFAULT TRUE,
    yaratilgan    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    yangilangan   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ── TUZATISH 3: mijozning saqlangan manzillari (1:N) ──────────────────
CREATE TABLE manzillar (
    id          INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijoz_id    INTEGER      NOT NULL REFERENCES mijozlar(id) ON DELETE CASCADE,
    shahar_id   INTEGER      NOT NULL REFERENCES shaharlar(id) ON DELETE RESTRICT,
    kocha_uy    VARCHAR(200) NOT NULL,
    telefon     VARCHAR(20)  NOT NULL,
    asosiy      BOOLEAN      NOT NULL DEFAULT FALSE
);

-- Bir mijozda faqat BITTA asosiy manzil — partial unique index
CREATE UNIQUE INDEX manzillar_bitta_asosiy
    ON manzillar (mijoz_id) WHERE asosiy;

CREATE TABLE buyurtmalar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijoz_id     INTEGER     NOT NULL REFERENCES mijozlar(id) ON DELETE RESTRICT,
    -- TUZATISH 5: bajarilish holati va to'lov holati AJRATILDI
    holat        VARCHAR(20) NOT NULL DEFAULT 'yangi'
                 CHECK (holat IN ('yangi','yigilmoqda','jonatildi','yetkazildi','bekor')),
    -- TUZATISH 3: manzil FK EMAS, balki NUSXA. Mijoz ko'chib ketsa ham
    -- bu buyurtma qayerga yetkazilgani o'zgarmaydi.
    yetkazish_manzili TEXT     NOT NULL,
    yetkazish_telefoni VARCHAR(20) NOT NULL,
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE buyurtma_elementlari (
    id          INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buyurtma_id INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor      INTEGER       NOT NULL CHECK (miqdor > 0),
    narx_birlik NUMERIC(14,2) NOT NULL CHECK (narx_birlik > 0),
    -- TUZATISH 1: eng muhim tuzatish. Busiz bitta mahsulot bitta
    -- buyurtmada ikki marta paydo bo'lib, hisobotlarni buzardi.
    CONSTRAINT bel_buyurtma_mahsulot_uq UNIQUE (buyurtma_id, mahsulot_id)
);

-- ── TUZATISH 5: to'lov — mustaqil mohiyat ─────────────────────────────
CREATE TABLE tolovlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buyurtma_id   INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE RESTRICT,
    summa         NUMERIC(14,2) NOT NULL CHECK (summa > 0),
    usul          VARCHAR(20)   NOT NULL
                  CHECK (usul IN ('naqd','karta','click','payme','bank')),
    holat         VARCHAR(20)   NOT NULL DEFAULT 'kutmoqda'
                  CHECK (holat IN ('kutmoqda','tasdiqlandi','rad_etildi','qaytarildi')),
    tranzaksiya_id VARCHAR(64),
    vaqti         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    -- tashqi to'lov tizimidagi ID takrorlanmasin
    CONSTRAINT tolovlar_tranzaksiya_uq UNIQUE (tranzaksiya_id)
);

-- ── TUZATISH 6: zaxira harakati — kirim/chiqim tarixi ─────────────────
CREATE TABLE zaxira_harakatlari (
    id          INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mahsulot_id INTEGER     NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    -- musbat = kirim (yetkazib berildi), manfiy = chiqim (sotildi)
    ozgarish    INTEGER     NOT NULL CHECK (ozgarish <> 0),
    sabab       VARCHAR(20) NOT NULL
                CHECK (sabab IN ('kirim','sotuv','qaytarish','inventarizatsiya','yaroqsiz')),
    buyurtma_id INTEGER     REFERENCES buyurtmalar(id) ON DELETE SET NULL,
    vaqti       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Kesh ustunini harakatlar bilan sinxron ushlab turuvchi trigger
CREATE OR REPLACE FUNCTION zaxirani_yangilash() RETURNS TRIGGER AS $$
BEGIN
    UPDATE mahsulotlar
    SET zaxira = zaxira + NEW.ozgarish,
        yangilangan = NOW()
    WHERE id = NEW.mahsulot_id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER zaxira_harakat_trigger
    AFTER INSERT ON zaxira_harakatlari
    FOR EACH ROW EXECUTE FUNCTION zaxirani_yangilash();

-- ── Indekslar: har FK ga + tez-tez ishlatiladigan filtrlarga ──────────
CREATE INDEX mijozlar_shahar_idx        ON mijozlar (shahar_id);
CREATE INDEX kategoriyalar_ota_idx      ON kategoriyalar (ota_id);
CREATE INDEX mahsulotlar_kategoriya_idx ON mahsulotlar (kategoriya_id);
CREATE INDEX manzillar_mijoz_idx        ON manzillar (mijoz_id);
CREATE INDEX buyurtmalar_mijoz_vaqt_idx ON buyurtmalar (mijoz_id, yaratilgan DESC);
CREATE INDEX bel_mahsulot_idx           ON buyurtma_elementlari (mahsulot_id);
CREATE INDEX tolovlar_buyurtma_idx      ON tolovlar (buyurtma_id);
CREATE INDEX zaxira_mahsulot_vaqt_idx   ON zaxira_harakatlari (mahsulot_id, vaqti DESC);

-- ═══════════════════════════════════════════════════════════════════════
-- Test ma'lumot
-- ═══════════════════════════════════════════════════════════════════════
INSERT INTO shaharlar (nomi, viloyati) VALUES
    ('Toshkent',  'Toshkent shahri'),
    ('Samarqand', 'Samarqand viloyati'),
    ('Buxoro',    'Buxoro viloyati');

INSERT INTO mijozlar (ism, email, shahar_id) VALUES
    ('Aziz Karimov',     'aziz@shop.uz',   1),
    ('Dilnoza Rasulova', 'dilya@shop.uz',  2),
    ('Sardor Tursunov',  'sardor@shop.uz', 1);

-- Ierarxik kategoriyalar
INSERT INTO kategoriyalar (ota_id, nomi) VALUES (NULL, 'Elektronika');
INSERT INTO kategoriyalar (ota_id, nomi) VALUES (1, 'Telefonlar'), (1, 'Noutbuklar');

INSERT INTO mahsulotlar (kategoriya_id, nomi, narx) VALUES
    (2, 'iPhone 15',      15000000),
    (2, 'Samsung S24',    12000000),
    (3, 'MacBook Pro 14', 22000000);

-- Zaxira faqat harakat orqali o'zgaradi — trigger keshni yangilaydi
INSERT INTO zaxira_harakatlari (mahsulot_id, ozgarish, sabab) VALUES
    (1, 10, 'kirim'), (2, 8, 'kirim'), (3, 5, 'kirim');

SELECT nomi, zaxira FROM mahsulotlar ORDER BY id;   -- 10, 8, 5

INSERT INTO manzillar (mijoz_id, shahar_id, kocha_uy, telefon, asosiy) VALUES
    (1, 1, 'Amir Temur ko''chasi, 15-uy', '+998901112233', TRUE),
    (1, 1, 'Yunusobod 4-kvartal, 22-uy',  '+998901112233', FALSE),
    (2, 2, 'Registon ko''chasi, 7-uy',    '+998907778899', TRUE);

-- Ikkinchi "asosiy" manzil bloklanadi:
-- UPDATE manzillar SET asosiy = TRUE WHERE id = 2;
-- ERROR:  duplicate key value violates unique constraint "manzillar_bitta_asosiy"

-- Buyurtma: manzil NUSXA sifatida yoziladi, FK sifatida emas
INSERT INTO buyurtmalar (mijoz_id, holat, yetkazish_manzili, yetkazish_telefoni) VALUES
    (1, 'yetkazildi', 'Toshkent, Amir Temur ko''chasi, 15-uy', '+998901112233'),
    (2, 'yigilmoqda', 'Samarqand, Registon ko''chasi, 7-uy',   '+998907778899');

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik) VALUES
    (1, 1, 1, 15000000),
    (1, 3, 1, 22000000),
    (2, 2, 2, 12000000);

-- Dublikat endi BLOKLANADI (v1 da bu bemalol o'tib ketardi):
-- INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik)
-- VALUES (1, 1, 5, 14000000);
-- ERROR:  duplicate key value violates unique constraint "bel_buyurtma_mahsulot_uq"

-- Sotuv zaxiradan chiqim yaratadi
INSERT INTO zaxira_harakatlari (mahsulot_id, ozgarish, sabab, buyurtma_id) VALUES
    (1, -1, 'sotuv', 1), (3, -1, 'sotuv', 1), (2, -2, 'sotuv', 2);

SELECT nomi, zaxira FROM mahsulotlar ORDER BY id;   -- 9, 6, 4

INSERT INTO tolovlar (buyurtma_id, summa, usul, holat, tranzaksiya_id) VALUES
    (1, 37000000, 'click', 'tasdiqlandi', 'CLK-2026-0001'),
    (2, 12000000, 'karta', 'tasdiqlandi', 'CRD-2026-0002');
-- Diqqat: 2-buyurtma qisman to'langan (24 mln dan 12 mln).
-- v1 sxemasida buni ifodalash IMKONSIZ edi.

-- ═══════════════════════════════════════════════════════════════════════
-- v2 sxema ochgan yangi imkoniyatlar
-- ═══════════════════════════════════════════════════════════════════════

-- 1) Viloyat bo'yicha daromad — v1 da IMKONSIZ edi (viloyat saqlanmagan)
SELECT s.viloyati,
       COUNT(DISTINCT b.id)              AS buyurtmalar,
       SUM(e.miqdor * e.narx_birlik)     AS daromad
FROM buyurtmalar b
JOIN mijozlar m  ON m.id = b.mijoz_id
JOIN shaharlar s ON s.id = m.shahar_id
JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
GROUP BY s.viloyati
ORDER BY daromad DESC;

-- 2) To'liq to'lanmagan buyurtmalar — v1 da IMKONSIZ edi
SELECT b.id,
       SUM(e.miqdor * e.narx_birlik) AS buyurtma_summasi,
       COALESCE(t.tolangan, 0)       AS tolangan,
       SUM(e.miqdor * e.narx_birlik) - COALESCE(t.tolangan, 0) AS qarz
FROM buyurtmalar b
JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
LEFT JOIN (
    SELECT buyurtma_id, SUM(summa) AS tolangan
    FROM tolovlar WHERE holat = 'tasdiqlandi'
    GROUP BY buyurtma_id
) t ON t.buyurtma_id = b.id
GROUP BY b.id, t.tolangan
HAVING SUM(e.miqdor * e.narx_birlik) > COALESCE(t.tolangan, 0);

-- 3) Zaxira tarixi — "nega 3 ta kam?" savoliga javob. v1 da IMKONSIZ.
SELECT p.nomi, z.vaqti, z.ozgarish, z.sabab, z.buyurtma_id
FROM zaxira_harakatlari z
JOIN mahsulotlar p ON p.id = z.mahsulot_id
ORDER BY p.nomi, z.vaqti;

-- 4) Kategoriya ierarxiyasi — recursive CTE. v1 da IMKONSIZ.
WITH RECURSIVE kat_yol AS (
    SELECT id, nomi, nomi::TEXT AS yol FROM kategoriyalar WHERE ota_id IS NULL
    UNION ALL
    SELECT k.id, k.nomi, y.yol || ' > ' || k.nomi
    FROM kategoriyalar k JOIN kat_yol y ON k.ota_id = y.id
)
SELECT y.yol AS kategoriya_yoli, COUNT(p.id) AS mahsulotlar
FROM kat_yol y
LEFT JOIN mahsulotlar p ON p.kategoriya_id = y.id
GROUP BY y.yol
ORDER BY y.yol;

-- 5) Kesh tekshiruvi: mahsulotlar.zaxira harakatlar bilan mos keladimi?
SELECT p.id, p.nomi, p.zaxira AS keshdagi,
       COALESCE(SUM(z.ozgarish), 0) AS haqiqiy
FROM mahsulotlar p
LEFT JOIN zaxira_harakatlari z ON z.mahsulot_id = p.id
GROUP BY p.id, p.nomi, p.zaxira
HAVING p.zaxira <> COALESCE(SUM(z.ozgarish), 0);
-- Bo'sh natija = kesh to'g'ri.
"""

L10_EX = [
    {
        "title": "v1 sxemasidagi haqiqiy xatolar",
        "description": "Asoslari kursidagi e-commerce sxemasi (v1) haqida quyidagilardan qaysilari haqiqiy dizayn xatosi hisoblanadi?",
        "exercise_type": "multiple_choice",
        "options": [
            "buyurtma_elementlari da UNIQUE (buyurtma_id, mahsulot_id) yo'q — bir mahsulot bitta buyurtmada ikki marta tura oladi",
            "ec_mijozlar.shahar erkin matn — viloyat bo'yicha hisobot imkonsiz",
            "buyurtma_elementlari.narx_birlik saqlanishi — bu ortiqcha takrorlanish",
            "Yetkazib berish manzili umuman saqlanmaydi",
        ],
        "correct_answers": "A,B,D",
        "is_multiple_select": True,
        "hint": "Bittasi aslida to'g'ri qilingan qaror — tarixiy faktni saqlash.",
        "explanation": "UNIQUE yo'qligi, shaharning erkin matn bo'lishi va manzilning umuman saqlanmasligi — haqiqiy xatolar. narx_birlik esa aksincha, to'g'ri qaror: u mahsulot narxining keshi emas, balki sotuv paytidagi tarixiy narx.",
        "difficulty_level": "Hard",
        "points": 12,
    },
    {
        "title": "NUMERIC(10,2) chegarasi",
        "description": "NUMERIC(10,2) turi saqlay oladigan eng katta qiymatni yozing (masalan: 999.99 ko'rinishida).",
        "exercise_type": "text_input",
        "expected_answer": "99999999.99",
        "hint": "Jami 10 ta raqam, ulardan 2 tasi kasr qismida.",
        "difficulty_level": "Medium",
        "points": 12,
    },
    {
        "title": "Yetkazish manzili: FK yoki nusxa?",
        "description": "Buyurtmadagi yetkazib berish manzili qanday saqlanishi kerak?",
        "exercise_type": "multiple_choice",
        "options": [
            "manzillar jadvaliga FK bilan — takrorlanish bo'lmasligi uchun",
            "Buyurtma qatorida matn nusxasi sifatida — mijoz ko'chib ketsa ham tarix o'zgarmasin",
            "Umuman saqlanmasligi kerak, mijozdan JOIN bilan olinadi",
            "Har safar yetkazib berish paytida qayta so'ralishi kerak",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "narx_birlik bilan bir xil mantiq: bu tarixiy fakt.",
        "explanation": "Yetkazib berish manzili — buyurtma vaqtidagi tarixiy fakt, xuddi narx_birlik kabi. FK bilan bog'lansa, mijoz manzilini o'zgartirganda butun yetkazib berish tarixi soxtalashadi. Shuning uchun u buyurtma qatoriga nusxa sifatida yoziladi.",
        "difficulty_level": "Hard",
        "points": 12,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# C1 — CAPSTONE: booking/reservation tizimi
# ═════════════════════════════════════════════════════════════════════════════
C1_TEXT = """\
<h2>🚀 CAPSTONE: Ko'p jadvalli booking/reservation tizimi</h2>

<p>Bu kursning yakuniy loyihasi. Vazifa &mdash; Booking.com yoki Airbnb tipidagi bron qilish tizimi uchun to'liq ma'lumotlar bazasi sxemasini <strong>noldan</strong> loyihalash. Bu yerda sizga tayyor sxema berilmaydi: siz uni o'zingiz quryapsiz, har bir qarorni esa yozma ravishda asoslashingiz kerak.</p>

<h3>Qamrab olinishi kerak bo'lgan mohiyatlar</h3>
<table>
<tr><th>Mohiyat</th><th>Nima uchun kerak</th><th>Qanday munosabatlar</th></tr>
<tr><td><code>foydalanuvchilar</code></td><td>Mehmon ham, uy egasi ham</td><td>1:1 profil bilan</td></tr>
<tr><td><code>obyektlar</code> (listings)</td><td>Ijaraga beriladigan joy</td><td>egasi bilan 1:N</td></tr>
<tr><td><code>obyekt_qulayliklari</code></td><td>Wi-Fi, avtoturargoh, basseyn</td><td>obyektlar bilan N:N</td></tr>
<tr><td><code>bronlar</code></td><td>Kim, qaysi obyektni, qaysi sanalarga</td><td>ikkala tomon bilan N:N</td></tr>
<tr><td><code>tolovlar</code></td><td>Qisman to'lov, qaytarish</td><td>bronlar bilan 1:N</td></tr>
<tr><td><code>sharhlar</code></td><td>Baho va izoh</td><td>bron bilan 1:1</td></tr>
</table>

<h3>⚠️ Ataylab qiyin qilingan dizayn qarorlari</h3>
<p>Quyidagi to'rtta savolga <strong>yozma javob</strong> berishingiz kerak. Har biri uchun tanlagan variantingizni va nima uchun boshqasini tanlamaganingizni asoslang. To'g'ri javob bittadan ko'p bo'lishi mumkin &mdash; baholanadigan narsa <em>asoslash sifati</em>.</p>

<h4>1. Sanalar kesishishini qanday bloklaysiz?</h4>
<p>Bitta obyekt bir vaqtning o'zida ikki kishiga bron qilinmasligi kerak. Oddiy <code>UNIQUE</code> bu yerda ishlamaydi, chunki muammo aniq tenglikda emas, balki <em>oraliqlarning kesishishida</em>: 1&ndash;5 avgust va 3&ndash;8 avgust bronlari kesishadi, lekin ularning ustun qiymatlari bir xil emas. Variantlar:</p>
<ul>
<li><code>EXCLUDE USING gist</code> cheklovi va <code>daterange</code> turi (<code>btree_gist</code> kengaytmasi bilan) &mdash; baza darajasida to'liq kafolat;</li>
<li>ilova kodida tranzaksiya + <code>SELECT ... FOR UPDATE</code> bilan tekshirish;</li>
<li>trigger ichida kesishishni tekshirish.</li>
</ul>
<p>Qaysi birini tanlaysiz va nega? Ilova darajasidagi tekshiruv qaysi holatda ishlamay qoladi?</p>

<h4>2. Narx qayerda saqlanadi?</h4>
<p>Obyektning kunlik narxi vaqt o'tishi bilan o'zgaradi (mavsum, chegirma). Bron qilingandan keyin narx o'zgarsa, eski bron summasi o'zgarmasligi kerak. Bundan tashqari, "kelasi yozgi narxlar" ni oldindan kiritish imkoni ham kerak. Bitta <code>obyektlar.narx</code> ustuni yetadimi? <code>narx_kalendari</code> jadvali kerakmi? Bron qatoriga narx nusxasini yozish kifoyami?</p>

<h4>3. Sharh yozish huquqini qanday cheklaysiz?</h4>
<p>Faqat <em>haqiqatan yashab chiqqan</em> mehmon sharh yoza olishi kerak &mdash; ya'ni bron mavjud va u tugagan bo'lishi shart. Buni sxema darajasida qanday majburlaysiz? <code>sharhlar.bron_id</code> ni <code>UNIQUE</code> qilish yetarlimi? "Bron tugagan" shartini <code>CHECK</code> bilan ifodalash mumkinmi (eslatma: <code>CHECK</code> boshqa jadvalga murojaat qila olmaydi)?</p>

<h4>4. Bekor qilish tarixi qayerda yashaydi?</h4>
<p>Bron bekor qilinganda <code>DELETE</code> qilasizmi yoki <code>holat = 'bekor'</code> qo'yasizmi? To'lov allaqachon o'tgan bo'lsa nima bo'ladi? Bekor qilingan bron sanalari darhol bo'shashi kerak &mdash; bu 1-savoldagi kesishish cheklovi bilan qanday kelishadi?</p>

<h3>Texnik talablar</h3>
<ul>
<li>✅ Kamida 8 ta jadval; barchasi 3NF da (istisnolarni izohlang)</li>
<li>✅ 1:1, 1:N va N:N &mdash; uchalasi ham ishlatilgan bo'lsin</li>
<li>✅ Kamida bitta self-referential munosabat</li>
<li>✅ Har bir FK uchun <code>ON DELETE</code> tanlangan va <code>--</code> komment bilan izohlangan</li>
<li>✅ Pul &mdash; <code>NUMERIC(14,2)</code>, vaqt &mdash; <code>TIMESTAMPTZ</code>, sana oralig'i &mdash; <code>DATE</code> yoki <code>daterange</code></li>
<li>✅ Kamida 6 ta nomlangan <code>CHECK</code> cheklovi</li>
<li>✅ Kamida bitta partial yoki kompozit unique indeks</li>
<li>✅ Barcha FK ustunlariga indeks</li>
<li>✅ Sanalar kesishishini bloklovchi mexanizm (qaysi birini tanlaganingizni asoslang)</li>
<li>✅ Test ma'lumot: 10+ foydalanuvchi, 8+ obyekt, 25+ bron (kamida 3 tasi bekor qilingan), 20+ to'lov, 10+ sharh</li>
<li>✅ Kamida 8 ta hisobot (quyida ro'yxat)</li>
<li>✅ mermaid <code>erDiagram</code> ko'rinishidagi sxema</li>
<li>✅ <code>DIZAYN.md</code> fayli: yuqoridagi 4 ta qiyin savolga yozma javob</li>
</ul>

<h3>Talab qilinadigan hisobotlar</h3>
<ol>
<li>Berilgan sana oralig'ida bo'sh obyektlar</li>
<li>Har obyektning bandlik foizi (oxirgi 90 kun)</li>
<li>Uy egalari bo'yicha daromad reytingi</li>
<li>O'rtacha bahosi eng yuqori TOP-5 obyekt (kamida 3 ta sharh bo'lganlar)</li>
<li>Qisman to'langan yoki umuman to'lanmagan bronlar</li>
<li>Bekor qilish darajasi (cancellation rate) &mdash; mehmonlar bo'yicha</li>
<li>Qaysi qulayliklar yuqori bahoga hamroh bo'ladi (N:N + agregat)</li>
<li>Oylik daromad trendi va o'sish foizi (window funksiya, <code>LAG</code>)</li>
</ol>

<h3>Bonus (ixtiyoriy)</h3>
<ul>
<li>🎯 <code>EXCLUDE USING gist</code> bilan sanalar kesishishini baza darajasida bloklash</li>
<li>📈 Bandlik dashboardi uchun <code>MATERIALIZED VIEW</code></li>
<li>🔁 Sharh yozish huquqini tekshiruvchi trigger</li>
<li>💸 Bekor qilish siyosati: qancha qaytariladi (sana farqiga qarab)</li>
<li>🔍 Ikkita eng og'ir hisobotni <code>EXPLAIN ANALYZE</code> bilan o'lchash va indeks bilan tezlashtirish</li>
</ul>

<h3>📌 Yakuniy so'z</h3>
<p>Bu kurs boshida siz sxemani "qanday qilib ishlaydi" deb ko'rar edingiz. Endi siz uni "nima uchun aynan shunday" deb ko'ryapsiz &mdash; va bu ikkalasi orasidagi farq dasturchi bilan ma'lumotlar bazasi dizayneri o'rtasidagi farqdir.</p>
<p>Yodda tuting: yaxshi sxema noto'g'ri ma'lumotni <em>saqlashning imkonini bermaydi</em>. Har safar "buni ilovada tekshiramiz" degan fikr kelganda, o'zingizdan so'rang: agar ertaga boshqa xizmat, boshqa skript yoki men o'zim yarim tunda <code>psql</code> dan yozsam &mdash; bu tekshiruv ishlaydimi? Javob "yo'q" bo'lsa, u tekshiruv bazada bo'lishi kerak.</p>
"""

C1_CODE = """\
-- ═══════════════════════════════════════════════════════════════════════
-- 🚀 CAPSTONE: booking tizimi — START KIT
--
-- Quyida sxemaning FAQAT poydevori berilgan. Qolganini o'zingiz
-- quryapsiz. Har bir qaror uchun -- komment bilan asos yozing.
-- ═══════════════════════════════════════════════════════════════════════

-- Sana oralig'i cheklovi uchun kerak (bonus vazifa)
CREATE EXTENSION IF NOT EXISTS btree_gist;

DROP TABLE IF EXISTS sharhlar;
DROP TABLE IF EXISTS tolovlar;
DROP TABLE IF EXISTS bronlar;
DROP TABLE IF EXISTS obyekt_qulayliklari;
DROP TABLE IF EXISTS qulayliklar;
DROP TABLE IF EXISTS obyektlar;
DROP TABLE IF EXISTS profillar;
DROP TABLE IF EXISTS foydalanuvchilar;

-- ── Foydalanuvchi: ham mehmon, ham uy egasi bo'la oladi ───────────────
CREATE TABLE foydalanuvchilar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR(160) NOT NULL,
    ism             VARCHAR(120) NOT NULL,
    telefon         VARCHAR(20),
    royxatdan       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    ochirilgan_sana TIMESTAMPTZ,
    CONSTRAINT foydalanuvchilar_email_uq  UNIQUE (email),
    CONSTRAINT foydalanuvchilar_email_fmt CHECK (email LIKE '%_@_%._%')
);

-- ── 1:1 — ixtiyoriy profil ────────────────────────────────────────────
CREATE TABLE profillar (
    foydalanuvchi_id INTEGER PRIMARY KEY
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bio              VARCHAR(500),
    avatar_url       VARCHAR(255),
    tasdiqlangan     BOOLEAN NOT NULL DEFAULT FALSE
);

-- ── 1:N — obyekt va uning egasi ───────────────────────────────────────
CREATE TABLE obyektlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- RESTRICT: obyektlari bor foydalanuvchini o'chirib bo'lmaydi,
    -- chunki bu bronlar va to'lovlar tarixini yo'q qilardi
    egasi_id      INTEGER       NOT NULL
                  REFERENCES foydalanuvchilar(id) ON DELETE RESTRICT,
    sarlavha      VARCHAR(200)  NOT NULL,
    shahar        VARCHAR(60)   NOT NULL,
    turi          VARCHAR(20)   NOT NULL
                  CHECK (turi IN ('kvartira','uy','xona','hostel')),
    sigim         SMALLINT      NOT NULL CHECK (sigim BETWEEN 1 AND 20),
    kunlik_narx   NUMERIC(14,2) NOT NULL CHECK (kunlik_narx > 0),
    faol          BOOLEAN       NOT NULL DEFAULT TRUE,
    yaratilgan    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ── N:N — obyekt va qulayliklar ───────────────────────────────────────
CREATE TABLE qulayliklar (
    id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE obyekt_qulayliklari (
    obyekt_id   INTEGER NOT NULL REFERENCES obyektlar(id)   ON DELETE CASCADE,
    qulaylik_id INTEGER NOT NULL REFERENCES qulayliklar(id) ON DELETE RESTRICT,
    PRIMARY KEY (obyekt_id, qulaylik_id)
);

-- ── Bronlar: kursning barcha tushunchalari shu jadvalda uchrashadi ────
CREATE TABLE bronlar (
    id             INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    obyekt_id      INTEGER       NOT NULL REFERENCES obyektlar(id) ON DELETE RESTRICT,
    mehmon_id      INTEGER       NOT NULL
                   REFERENCES foydalanuvchilar(id) ON DELETE RESTRICT,
    kirish_sanasi  DATE          NOT NULL,
    chiqish_sanasi DATE          NOT NULL,
    mehmonlar_soni SMALLINT      NOT NULL DEFAULT 1 CHECK (mehmonlar_soni > 0),
    -- TARIXIY narx: bron paytidagi kunlik narx nusxasi.
    -- Obyekt narxi keyin o'zgarsa ham bu bron summasi o'zgarmaydi.
    kunlik_narx    NUMERIC(14,2) NOT NULL CHECK (kunlik_narx > 0),
    holat          VARCHAR(15)   NOT NULL DEFAULT 'kutmoqda'
                   CHECK (holat IN ('kutmoqda','tasdiqlangan','yashab_chiqdi','bekor')),
    yaratilgan     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT bronlar_sana_tartibi CHECK (chiqish_sanasi > kirish_sanasi),
    -- ⚠️ ASOSIY QIYIN QAROR: sanalar kesishishini bloklash.
    -- Oddiy UNIQUE bu yerda ishlamaydi — muammo tenglikda emas,
    -- oraliqlarning KESISHISHIDA. EXCLUDE USING gist buni hal qiladi.
    -- WHERE sharti: bekor qilingan bronlar sanani band qilmaydi.
    CONSTRAINT bronlar_kesishmasin EXCLUDE USING gist (
        obyekt_id WITH =,
        daterange(kirish_sanasi, chiqish_sanasi, '[)') WITH &&
    ) WHERE (holat <> 'bekor')
);

-- ── 1:N — to'lovlar (qisman to'lov va qaytarish mumkin) ───────────────
CREATE TABLE tolovlar (
    id          INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bron_id     INTEGER       NOT NULL REFERENCES bronlar(id) ON DELETE RESTRICT,
    summa       NUMERIC(14,2) NOT NULL CHECK (summa <> 0),  -- manfiy = qaytarish
    usul        VARCHAR(20)   NOT NULL CHECK (usul IN ('karta','click','payme','naqd')),
    vaqti       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ── 1:1 — har bronga ko'pi bilan bitta sharh ──────────────────────────
CREATE TABLE sharhlar (
    -- bron_id ni PK qilish = 1:1 va "sharh faqat bron bo'lsa" kafolati
    bron_id    INTEGER  PRIMARY KEY REFERENCES bronlar(id) ON DELETE CASCADE,
    baho       SMALLINT NOT NULL CHECK (baho BETWEEN 1 AND 5),
    matn       VARCHAR(1000),
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indekslar ─────────────────────────────────────────────────────────
CREATE INDEX obyektlar_egasi_idx      ON obyektlar (egasi_id);
CREATE INDEX obyektlar_shahar_idx     ON obyektlar (shahar) WHERE faol;
CREATE INDEX bronlar_obyekt_sana_idx  ON bronlar (obyekt_id, kirish_sanasi);
CREATE INDEX bronlar_mehmon_idx       ON bronlar (mehmon_id);
CREATE INDEX tolovlar_bron_idx        ON tolovlar (bron_id);
CREATE INDEX oq_qulaylik_idx          ON obyekt_qulayliklari (qulaylik_id);

-- ── Minimal test ma'lumot (siz buni kengaytirasiz) ────────────────────
INSERT INTO foydalanuvchilar (email, ism) VALUES
    ('aziz@bk.uz',   'Aziz Karimov'),
    ('dilya@bk.uz',  'Dilnoza Rasulova'),
    ('sardor@bk.uz', 'Sardor Tursunov');

INSERT INTO profillar (foydalanuvchi_id, bio, tasdiqlangan) VALUES
    (1, 'Toshkentda 3 ta kvartira ijaraga beraman', TRUE);

INSERT INTO qulayliklar (nomi) VALUES
    ('Wi-Fi'), ('Avtoturargoh'), ('Konditsioner'), ('Kir yuvish mashinasi');

INSERT INTO obyektlar (egasi_id, sarlavha, shahar, turi, sigim, kunlik_narx) VALUES
    (1, 'Markazda zamonaviy kvartira', 'Toshkent',  'kvartira', 4, 450000),
    (1, 'Yunusobodda studiya',         'Toshkent',  'kvartira', 2, 300000),
    (2, 'Registon yonida uy',          'Samarqand', 'uy',       6, 800000);

INSERT INTO obyekt_qulayliklari (obyekt_id, qulaylik_id) VALUES
    (1, 1), (1, 2), (1, 3),
    (2, 1), (2, 3),
    (3, 1), (3, 2), (3, 4);

INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
                     mehmonlar_soni, kunlik_narx, holat) VALUES
    (1, 2, DATE '2026-08-01', DATE '2026-08-05', 2, 450000, 'yashab_chiqdi'),
    (1, 3, DATE '2026-08-10', DATE '2026-08-14', 3, 450000, 'tasdiqlangan'),
    (3, 1, DATE '2026-08-03', DATE '2026-08-08', 4, 800000, 'tasdiqlangan');

-- Kesishuvchi bron BLOKLANADI — EXCLUDE cheklovi ishlaydi:
-- INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
--                      kunlik_narx) VALUES (1, 3, '2026-08-03', '2026-08-07', 450000);
-- ERROR:  conflicting key value violates exclusion constraint "bronlar_kesishmasin"

-- Bekor qilingan bron sanani BAND QILMAYDI (WHERE sharti tufayli):
INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
                     kunlik_narx, holat)
VALUES (1, 3, DATE '2026-09-01', DATE '2026-09-05', 450000, 'bekor');
INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
                     kunlik_narx, holat)
VALUES (1, 2, DATE '2026-09-01', DATE '2026-09-05', 450000, 'tasdiqlangan');

INSERT INTO tolovlar (bron_id, summa, usul) VALUES
    (1, 1800000, 'click'),
    (2,  900000, 'karta'),   -- qisman to'lov (jami 1 800 000 dan)
    (3, 4000000, 'payme');

INSERT INTO sharhlar (bron_id, baho, matn) VALUES
    (1, 5, 'Ajoyib joy, hamma narsa tasvirdagidek edi.');

-- ── Namuna hisobot: bandlik va daromad ────────────────────────────────
SELECT o.sarlavha,
       COUNT(b.id) FILTER (WHERE b.holat <> 'bekor')          AS bronlar,
       SUM((b.chiqish_sanasi - b.kirish_sanasi) * b.kunlik_narx)
           FILTER (WHERE b.holat <> 'bekor')                  AS daromad,
       ROUND(AVG(s.baho), 2)                                  AS ortacha_baho
FROM obyektlar o
LEFT JOIN bronlar  b ON b.obyekt_id = o.id
LEFT JOIN sharhlar s ON s.bron_id  = b.id
GROUP BY o.id, o.sarlavha
ORDER BY daromad DESC NULLS LAST;

-- ── Namuna hisobot: to'liq to'lanmagan bronlar ────────────────────────
SELECT b.id,
       (b.chiqish_sanasi - b.kirish_sanasi) * b.kunlik_narx AS jami,
       COALESCE(SUM(t.summa), 0)                            AS tolangan,
       (b.chiqish_sanasi - b.kirish_sanasi) * b.kunlik_narx
           - COALESCE(SUM(t.summa), 0)                      AS qarz
FROM bronlar b
LEFT JOIN tolovlar t ON t.bron_id = b.id
WHERE b.holat <> 'bekor'
GROUP BY b.id, b.chiqish_sanasi, b.kirish_sanasi, b.kunlik_narx
HAVING (b.chiqish_sanasi - b.kirish_sanasi) * b.kunlik_narx
       > COALESCE(SUM(t.summa), 0);

-- ── SIZ DAVOM ETTIRASIZ ───────────────────────────────────────────────
-- 1. narx_kalendari jadvali (mavsumiy narxlar) — kerakmi? Asoslang.
-- 2. Sharh yozish huquqini tekshiruvchi trigger (bron 'yashab_chiqdi'
--    holatida bo'lsagina sharh yozilsin).
-- 3. Bekor qilish siyosati: qancha qaytariladi?
-- 4. Qolgan 6 ta hisobot.
-- 5. mermaid erDiagram va DIZAYN.md — 4 ta qiyin savolga javob.
"""

C1_EX = [
    {
        "title": "Sanalar kesishishini bloklash",
        "description": "Bitta obyekt bir vaqtda ikki kishiga bron qilinmasligi uchun PostgreSQL da eng ishonchli baza darajasidagi mexanizm qaysi?",
        "exercise_type": "multiple_choice",
        "options": [
            "UNIQUE (obyekt_id, kirish_sanasi, chiqish_sanasi)",
            "EXCLUDE USING gist (obyekt_id WITH =, daterange(...) WITH &&)",
            "Ilova kodida SELECT bilan tekshirish",
            "CHECK (kirish_sanasi < chiqish_sanasi)",
        ],
        "correct_answers": "B",
        "is_multiple_select": False,
        "hint": "Muammo aniq tenglikda emas, oraliqlarning kesishishida.",
        "explanation": "UNIQUE faqat bir xil qiymatlarni bloklaydi, kesishuvchi oraliqlarni emas (1-5 va 3-8 avgust kesishadi, lekin qiymatlari har xil). CHECK esa faqat bitta qator ichida ishlaydi. EXCLUDE USING gist + daterange && operatori — aynan shu muammoni hal qilish uchun mavjud va u parallel tranzaksiyalarda ham ishonchli.",
        "difficulty_level": "Hard",
        "points": 15,
    },
    {
        "title": "Bron narxi qanday saqlanadi?",
        "description": "Obyektning kunlik narxi vaqt o'tishi bilan o'zgaradi. Bron qilingandan keyin narx oshsa, eski bron summasi o'zgarmasligi kerak. Buni ta'minlash uchun bronlar jadvalida nima bo'lishi kerak va nima uchun? 2-3 jumla bilan javob bering.",
        "exercise_type": "text_input",
        "expected_answer": "bronlar jadvalida kunlik_narx ustuni bo'lishi kerak — bron qilingan paytdagi narxning nusxasi. Bu obyektlar.narx ga FK yoki JOIN bilan bog'lanmaydi, chunki u tarixiy fakt: narx keyin o'zgarsa ham bron summasi o'zgarmasligi kerak. Bu xuddi buyurtma_elementlari.narx_birlik bilan bir xil mantiq.",
        "hint": "narx_birlik va yetkazish manzili bilan bir xil tamoyil.",
        "difficulty_level": "Hard",
        "points": 15,
    },
]

C1_TASK = {
    "task_title": "🚀 CAPSTONE: Booking/reservation tizimi sxemasi",
    "task_description": (
        "Kursning yakuniy loyihasi: Booking.com / Airbnb tipidagi bron qilish "
        "tizimi uchun to'liq ma'lumotlar bazasi sxemasini noldan loyihalang. "
        "Sizga tayyor sxema berilmaydi — siz uni o'zingiz quryapsiz va har bir "
        "dizayn qarorini yozma ravishda asoslaysiz. Natija: ishga tushiriladigan "
        ".sql fayl, mermaid erDiagram va DIZAYN.md hujjati."
    ),
    "task_requirements": (
        "• Kamida 8 ta jadval: foydalanuvchilar, profillar, obyektlar, qulayliklar, "
        "obyekt_qulayliklari, bronlar, tolovlar, sharhlar\n"
        "• 1:1, 1:N va N:N — uchala munosabat turi ham ishlatilsin\n"
        "• Kamida bitta self-referential munosabat (masalan: sharhga javob yoki "
        "obyekt ierarxiyasi)\n"
        "• Barcha jadvallar 3NF da; istisno qilsangiz — sababini kommentda yozing\n"
        "• Pul — NUMERIC(14,2), vaqt — TIMESTAMPTZ, sanalar — DATE/daterange\n"
        "• Kamida 6 ta NOMLANGAN CHECK cheklovi\n"
        "• Kamida bitta partial yoki kompozit unique indeks\n"
        "• Har bir FK uchun ON DELETE strategiyasi tanlangan va -- komment bilan IZOHLANGAN\n"
        "• Barcha FK ustunlariga indeks\n"
        "• Bir obyekt bir vaqtda ikki kishiga bron qilinmasligini ta'minlovchi "
        "mexanizm (EXCLUDE USING gist tavsiya etiladi) va tanlovingizning asosi\n"
        "• Bron narxi tarixiy nusxa sifatida saqlansin (narx keyin o'zgarsa ham "
        "eski bron summasi o'zgarmasin)\n"
        "• Test ma'lumot: 10+ foydalanuvchi, 8+ obyekt, 25+ bron (kamida 3 tasi bekor), "
        "20+ to'lov, 10+ sharh\n"
        "• 8 ta hisobot: sana oralig'ida bo'sh obyektlar; bandlik foizi (90 kun); "
        "uy egalari daromad reytingi; o'rtacha bahosi TOP-5 obyekt (3+ sharh bilan); "
        "qisman/to'lanmagan bronlar; mehmonlar bo'yicha bekor qilish darajasi; "
        "qulayliklar va baho bog'liqligi (N:N + agregat); oylik daromad trendi (LAG)\n"
        "• DIZAYN.md da 4 ta qiyin savolga yozma javob:\n"
        "   1) Sanalar kesishishini qanday bloklaysiz va nega aynan shu usulni tanladingiz?\n"
        "   2) Narx qayerda saqlanadi — obyektda, narx kalendarida yoki bronda? Nega?\n"
        "   3) Sharh yozish huquqini (faqat yashab chiqqan mehmon) qanday cheklaysiz?\n"
        "   4) Bekor qilingan bron DELETE qilinadimi yoki holat bilan belgilanadimi? "
        "To'lov o'tgan bo'lsa nima bo'ladi?\n"
        "• Bonus: MATERIALIZED VIEW bilan bandlik dashboardi; sharh huquqini "
        "tekshiruvchi trigger; 2 ta og'ir hisobotni EXPLAIN ANALYZE bilan optimallashtirish"
    ),
    "task_technologies": (
        "PostgreSQL, to'liq sxema dizayni, normalizatsiya (1NF/2NF/3NF/BCNF), "
        "1:1 / 1:N / N:N, junction jadval, self-referential FK, kompozit va partial "
        "unique index, CHECK, EXCLUDE USING gist, daterange, btree_gist, TRIGGER, "
        "MATERIALIZED VIEW, recursive CTE, window functions, EXPLAIN ANALYZE, mermaid erDiagram"
    ),
    "task_deadline_days": 14,
}


def _jdump(value):
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(order: int, text: str, code: str, video: str | None,
                         exercise_rows: list[Exercise], lang: str = "sql",
                         project_task: dict | None = None) -> str:
    sections = [
        {"id": f"t{order}", "type": "text", "label": "Текст",
         "html": text, "order": 0},
        {"id": f"c{order}", "type": "code", "label": "Код",
         "code": code, "lang": lang, "order": 1},
    ]
    if video:
        sections.append({"id": f"v{order}", "type": "video", "label": "Видео",
                          "videoUrl": video, "order": 2})
    if exercise_rows:
        sections.append({
            "id": f"e{order}", "type": "exercise", "label": "Упражнения",
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
            "order": 3,
        })
    if project_task:
        sections.append({
            "id": f"p{order}", "type": "project", "label": project_task["task_title"],
            "description": project_task["task_description"],
            "requirements": project_task["task_requirements"],
            "techStack": project_task["task_technologies"],
            "deadline": project_task["task_deadline_days"],
            "order": 4,
        })
    return json.dumps(sections, ensure_ascii=False)


async def seed(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()

        if existing:
            course = existing
            print(f"Course '{COURSE['title']}' already exists (id={course.id}). "
                  f"Adding/updating lessons only.")
        else:
            course = Course(**COURSE)
            db.add(course)
            await db.flush()
            print(f"Created course: id={course.id}  title='{course.title}'")

        existing_orders = {
            row[0] for row in (
                await db.execute(select(Lesson.order).where(Lesson.course_id == course.id))
            ).all()
        }

        done_lessons = [l for l in LESSON_PLAN if l["status"] == "done"]
        print(f"\nSeeding {len(done_lessons)}/{len(LESSON_PLAN)} lessons "
              f"(rest are still 'todo' in LESSON_PLAN):\n")

        total_ex = 0
        for ldata in done_lessons:
            if ldata["order"] in existing_orders:
                print(f"  ⏭️  order={ldata['order']:>2}  {ldata['title']:<55}  "
                      f"already seeded, skipped")
                continue

            text = globals()[f"{ldata['ref']}_TEXT"]
            code = globals()[f"{ldata['ref']}_CODE"]
            ex_list = globals().get(f"{ldata['ref']}_EX", [])
            task = globals().get(f"{ldata['ref']}_TASK")
            lang = ldata.get("lang", "sql")

            lesson = Lesson(
                course_id=course.id,
                title=ldata["title"],
                order=ldata["order"],
                points_reward=ldata.get("points", 13),
                text_content=text,
                code_content=code,
                code_language=lang,
                video_url=None,  # TODO: add a real video link before publishing
                sections_json=None,
                task_title=task.get("task_title") if task else None,
                task_description=task.get("task_description") if task else None,
                task_requirements=task.get("task_requirements") if task else None,
                task_technologies=task.get("task_technologies") if task else None,
                task_deadline_days=task.get("task_deadline_days") if task else None,
                is_active=True,
                is_published=True,
            )
            db.add(lesson)
            await db.flush()

            ex_rows: list[Exercise] = []
            for ex_order, ex in enumerate(ex_list):
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
            total_ex += len(ex_rows)

            lesson.sections_json = build_sections_json(
                ldata["order"], text, code, None, ex_rows, lang=lang,
                project_task=task,
            )

            sample = LessonSample(
                lesson_id=lesson.id,
                title=f"Namuna: {ldata['title']}",
                description=ldata["scope"],
                sample_type="code",
                code_files_json=json.dumps(
                    [{"filename": f"dizayn.{lang}", "language": lang, "code": code}],
                    ensure_ascii=False,
                ),
            )
            db.add(sample)

            print(f"  lesson order={lesson.order:>2} id={lesson.id:>4}  "
                  f"{lesson.title:<58}  exercises={len(ex_rows)}  "
                  f"points={lesson.points_reward}  task={'yes' if task else 'no'}")

        print(f"\nTotal exercises: {total_ex}")
        print(f"Total lesson points: {sum(l.get('points', 13) for l in done_lessons)}")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nSeeded {len(done_lessons)} lesson(s).")

    await engine.dispose()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry))
